"""Reach-aware menus: learn where a player's hands comfortably go from a few minutes of play, and put menu
buttons there (docs/reach-menus.md). A pilot first; nothing here is preregistered yet.

Synthetic players. Each has a height, a seated or standing posture, an arm length (0.44 x height x a reach
factor, below 1 for limited reach), a right-hand share of reaches, and per hand 2 to 4 habitual reach zones
around the shoulder (direction, distance as a fraction of arm length, weight, spread). The game sees the
hand's position, in the body frame (head-relative, rotated by the smoothed head yaw), while the hand pauses
at the end of a reach: 30 Hz samples during the hold, with hold jitter, tracking noise and a few degrees of
error in the body frame's yaw. That is a simplification of full motion: reach detection is assumed solved.

A player's true comfort zone for a hand is the mixture of their zones (known exactly). Placement puts 3
buttons per hand on the highest-density points of a model of that hand's reach positions, at least 12 cm
apart; a button scores if it lies inside the true 50% (and 80%) highest-density region.

Models: a Gaussian mixture per hand (8 components, full covariance). Generic = one mixture fitted on a
population, positions scaled by height, rescaled to the player's height. Personal = the generic mixture
fine-tuned by Adam on the player's negative log-likelihood (full batch), stopped by the arms of
poc/netpred/personalize.py: the cross-fitted rule, one calibrated relative drop reused, a held-out quarter,
fixed budgets, the best step on a fresh session (oracle).

  python3 -m poc.reach.menus pilot OUT_DIR
"""
from __future__ import annotations
import json, math, sys, time
from pathlib import Path
import numpy as np, torch

say = lambda s: print(f"[{time.strftime('%H:%M:%S')}] {s}", flush=True)
REF_H = 1.75


def sample_style(rng):
    seated = rng.random() < 0.3; h = rng.uniform(1.5, 1.92); eye = h - 0.12 - (0.45 if seated else 0.0)
    arm = 0.44 * h * rng.uniform(0.6, 1.05); rs = rng.uniform(0.25, 0.9); zones = []
    for hand in (0, 1):   # 0 left, 1 right; outward is +y for the left hand
        side = 1 if hand == 0 else -1; k = int(rng.integers(2, 5)); w = rng.dirichlet(np.ones(k) * 2)
        for j in range(k):
            az = np.radians(rng.uniform(-30, 70)); el = np.radians(rng.uniform(-45, 35)); dist = rng.uniform(0.5, 0.95) * arm
            d = np.array([np.cos(el) * np.cos(az), side * np.cos(el) * np.sin(az), np.sin(el)])
            sh = np.array([-0.05, side * 0.18, -0.25 * h / REF_H])
            zones.append(dict(hand=hand, w=float(w[j]), c=(sh + dist * d).tolist(), sd=float(rng.uniform(0.025, 0.07))))
    return dict(height=h, eye=eye, seated=bool(seated), arm=arm, right_share=rs, zones=zones, rate=rng.uniform(15, 50), hold=(0.3, 1.5))


def session(style, minutes, seed):
    """Hold samples per hand: list of two arrays (n, 3), body frame, metres, head at the origin."""
    rng = np.random.default_rng(seed); out = [[], []]; n_ev = rng.poisson(style["rate"] * minutes)
    for _ in range(n_ev):
        hand = int(rng.random() < style["right_share"]); Z = [z for z in style["zones"] if z["hand"] == hand]
        z = Z[rng.choice(len(Z), p=np.array([q["w"] for q in Z]) / sum(q["w"] for q in Z))]
        tgt = np.array(z["c"]) + rng.normal(0, z["sd"], 3); m = max(1, int(rng.uniform(*style["hold"]) * 30))
        a = np.radians(rng.normal(0, 3)); R = np.array([[np.cos(a), -np.sin(a), 0], [np.sin(a), np.cos(a), 0], [0, 0, 1]])
        pts = (R @ tgt) + rng.normal(0, 0.004, (m, 3)) + rng.normal(0, 0.001, (m, 3)); out[hand].append(pts)
    return [np.concatenate(o) if o else np.zeros((0, 3)) for o in out]


def true_logpdf(style, hand, x):
    Z = [z for z in style["zones"] if z["hand"] == hand]; W = np.array([z["w"] for z in Z]); W = W / W.sum(); lp = []
    for z, w in zip(Z, W):
        d2 = ((x - np.array(z["c"])) ** 2).sum(-1) / z["sd"] ** 2; lp.append(np.log(w) - 1.5 * np.log(2 * np.pi * z["sd"] ** 2) - 0.5 * d2)
    return np.logaddexp.reduce(np.stack(lp), 0)


def hpd_thresholds(style, hand, rng, n=20000):
    Z = [z for z in style["zones"] if z["hand"] == hand]; W = np.array([z["w"] for z in Z]); W = W / W.sum()
    idx = rng.choice(len(Z), n, p=W); x = np.array([Z[i]["c"] for i in idx]) + rng.normal(0, 1, (n, 3)) * np.array([Z[i]["sd"] for i in idx])[:, None]
    lp = np.sort(true_logpdf(style, hand, x))[::-1]; return dict(p50=lp[int(0.5 * n)], p80=lp[int(0.8 * n)])


class GMM(torch.nn.Module):
    def __init__(self, K=8, D=3):
        super().__init__(); self.logit = torch.nn.Parameter(torch.zeros(K)); self.mu = torch.nn.Parameter(torch.zeros(K, D))
        self.Lraw = torch.nn.Parameter(torch.zeros(K, D, D)); self.D = D
    def chol(self):
        L = torch.tril(self.Lraw, -1); d = torch.diagonal(self.Lraw, dim1=-2, dim2=-1)
        return L + torch.diag_embed(torch.nn.functional.softplus(d) + 1e-3)
    def logpdf(self, x):
        L = self.chol(); diff = x[:, None, :] - self.mu[None]                   # (n, K, D)
        sol = torch.linalg.solve_triangular(L[None].expand(len(x), -1, -1, -1), diff[..., None], upper=False)[..., 0]
        logdet = torch.log(torch.diagonal(L, dim1=-2, dim2=-1)).sum(-1)
        comp = -0.5 * (sol ** 2).sum(-1) - logdet - 0.5 * self.D * math.log(2 * math.pi) + torch.log_softmax(self.logit, 0)
        return torch.logsumexp(comp, 1)
    def scaled(self, s):   # the same mixture with positions multiplied by s
        g = GMM(len(self.logit), self.D); g.load_state_dict(self.state_dict())
        with torch.no_grad():
            g.mu.mul_(s); L = self.chol() * s; d = torch.diagonal(L, dim1=-2, dim2=-1)
            raw = torch.tril(L, -1) + torch.diag_embed(torch.log(torch.expm1(d - 1e-3)))
            g.Lraw.copy_(raw)
        return g
    def sample(self, n, gen):
        with torch.no_grad():
            k = torch.multinomial(torch.softmax(self.logit, 0), n, replacement=True, generator=gen)
            return self.mu[k] + (self.chol()[k] @ torch.randn(n, self.D, 1, generator=gen))[..., 0]


def fit_gmm(x, init=None, steps=3000, lr=0.01, seed=0):
    torch.manual_seed(seed); g = GMM()
    if init is not None: g.load_state_dict(init.state_dict())
    else:
        with torch.no_grad(): g.mu.copy_(x[torch.randperm(len(x))[:8]]); g.Lraw.copy_(torch.diag_embed(torch.full((8, 3), math.log(math.expm1(0.08)))))
    opt = torch.optim.Adam(g.parameters(), lr=lr)
    for _ in range(steps): loss = -g.logpdf(x).mean(); opt.zero_grad(); loss.backward(); opt.step()
    return g


def place(g, gen, n_btn=3, gap=0.12):
    x = g.sample(6000, gen)
    with torch.no_grad(): lp = g.logpdf(x).numpy()
    x = x.numpy(); order = np.argsort(-lp); picked = []
    for i in order:
        if all(np.linalg.norm(x[i] - p) >= gap for p in picked): picked.append(x[i])
        if len(picked) == n_btn: break
    return np.array(picked)


def button_score(style, hand, pts, thr):
    lp = true_logpdf(style, hand, pts); return dict(in50=float((lp >= thr["p50"]).mean()), in80=float((lp >= thr["p80"]).mean()))


def fixed_panel(style, hand):
    """A common default: buttons 0.45 m ahead of the eyes, 0.3 m below them, 0.12 m apart, on the hand's side."""
    side = 1 if hand == 0 else -1; return np.array([[0.45, side * (0.05 + 0.12 * j), -0.3] for j in range(3)])


def fit_personal(gen_h, x_tr, watches, lr, cap, seg=10, seed=0):
    """Fine-tune from gen_h; record the training loss, each watched set's loss and a parameter snapshot per
    evaluation. Stops at `cap` (no early stop: the arms read the curve)."""
    torch.manual_seed(seed); g = GMM(); g.load_state_dict(gen_h.state_dict()); opt = torch.optim.Adam(g.parameters(), lr=lr)
    def ev():
        with torch.no_grad(): return {k: float(-g.logpdf(v).mean()) for k, v in dict(tr=x_tr, **watches).items()}
    snap = lambda: {k: v.detach().clone() for k, v in g.state_dict().items()}
    out = {k: [v] for k, v in ev().items()}; out["step"] = [0]; snaps = [snap()]
    for k in range(cap // seg):
        for _ in range(seg):
            loss = -g.logpdf(x_tr).mean(); opt.zero_grad(); loss.backward(); opt.step()
        cur = ev(); out["step"].append((k + 1) * seg); snaps.append(snap())
        for kk, v in cur.items(): out[kk].append(v)
    return out, snaps


def gmm_from(sd):
    g = GMM(); g.load_state_dict(sd); return g


def population(n, minutes, seed):
    rng = np.random.default_rng(seed); X = [[], []]
    for p in range(n):
        st = sample_style(rng); hs = session(st, minutes, seed * 1000 + p)
        for h in (0, 1): X[h].append(hs[h] * REF_H / st["height"])
    gens = []
    for h in (0, 1):
        x = torch.from_numpy(np.concatenate(X[h])[::3].astype(np.float32)); gens.append(fit_gmm(x, steps=3000, seed=h)); say(f"population model, hand {h}: {len(x)} samples")
    return gens


def player(gens, style, minutes, seed, cfg, r_star=None):
    """All arms for one player and one data size; per hand, then the hands' scores averaged."""
    rng = np.random.default_rng(seed + 1); tr = session(style, minutes, seed); te = session(style, 5, seed + 2); T = lambda a: torch.from_numpy(a.astype(np.float32))
    gen_t = torch.Generator().manual_seed(seed); res = dict(minutes=minutes, hands=[])
    for h in (0, 1):
        thr = hpd_thresholds(style, h, rng); g0 = gens[h].scaled(style["height"] / REF_H); r = dict(n_tr=len(tr[h]))
        r["fixed"] = button_score(style, h, fixed_panel(style, h), thr); r["generic"] = button_score(style, h, place(g0, gen_t), thr)
        if len(tr[h]) < 20 or len(te[h]) < 20:   # too little reaching with this hand: keep the generic placement everywhere
            for a in ("rule", "reuse", "holdout", "steps100", "steps300", "steps1000", "oracle", "last"): r[a] = r["generic"]
            r["skipped"] = True; res["hands"].append(r); continue
        x = T(tr[h]); n = len(x); half = n // 2; q = int(0.75 * n)
        curve, snaps = fit_personal(g0, x, dict(te=T(te[h])), cfg["lr"], cfg["cap"], seed=seed)
        knees = []
        for a, b in ((x[:half], x[half:]), (x[half:], x[:half])):
            c, _ = fit_personal(g0, a, dict(ho=b), cfg["lr"], cfg["cap"], seed=seed + 5); knees.append(c["tr"][0] - c["tr"][int(np.argmin(c["ho"]))])
        hold, _ = fit_personal(g0, x[:q], dict(ho=x[q:]), cfg["lr"], cfg["cap"], seed=seed + 7)
        tr_c = np.array(curve["tr"]); st = np.array(curve["step"])
        idx_drop = lambda d: int(np.argmax(tr_c[0] - tr_c >= d)) if (tr_c[0] - tr_c >= d).any() else len(tr_c) - 1
        pick = dict(rule=idx_drop(np.mean(knees)), holdout=int(np.argmin(hold["ho"])), oracle=int(np.argmin(curve["te"])), last=len(st) - 1)
        for b in (100, 300, 1000): pick[f"steps{b}"] = int(np.argmin(np.abs(st - b)))
        if r_star is not None: pick["reuse"] = idx_drop(r_star * abs(tr_c[0]))
        r["knee_rel"] = float((tr_c[0] - tr_c[pick["oracle"]]) / abs(tr_c[0])); r["test_nll"] = {a: float(curve["te"][i]) for a, i in pick.items()}; r["test_nll"]["generic"] = float(curve["te"][0])
        for a, i in pick.items(): r[a] = button_score(style, h, place(gmm_from(snaps[i]), gen_t), thr)
        res["hands"].append(r)
    return res


def summarise(rows, arms):
    out = {}
    for a in arms:
        v = [np.mean([hh[a]["in50"] for hh in r["hands"]]) for r in rows if a in r["hands"][0]]; v8 = [np.mean([hh[a]["in80"] for hh in r["hands"]]) for r in rows if a in r["hands"][0]]
        if v: out[a] = (float(np.mean(v)), float(np.mean(v8)))
    return out


def pilot(out_dir):
    out = Path(out_dir); out.mkdir(parents=True, exist_ok=True); torch.set_num_threads(4); T0 = time.time()
    gens = population(60, 5, seed=3); cfg = dict(lr=0.01, cap=1500); rng = np.random.default_rng(4242); rows = []
    styles = [sample_style(rng) for _ in range(8)]
    for p, stl in enumerate(styles):
        for m in (1, 2, 5):
            r = player(gens, stl, m, 900000 + 10 * p, cfg); r["player"] = p; rows.append(r)
            hs = r["hands"]; f = lambda a: np.mean([hh[a]["in50"] for hh in hs])
            say(f"player {p} ({'seated' if stl['seated'] else 'standing'}, reach {stl['arm'] / (0.44 * stl['height']):.2f}, right share {stl['right_share']:.2f}), {m} min: in the true 50% zone, of 6 buttons: fixed {6 * f('fixed'):.1f}, generic {6 * f('generic'):.1f}, rule {6 * f('rule'):.1f}, holdout {6 * f('holdout'):.1f}, best {6 * f('oracle'):.1f}, 300 steps {6 * f('steps300'):.1f}, last {6 * f('last'):.1f} [{time.time() - T0:.0f}s]")
            json.dump(rows, open(out / "pilot_rows.json", "w"), indent=1)
    for m in (1, 2, 5):
        S = summarise([r for r in rows if r["minutes"] == m], ["fixed", "generic", "rule", "holdout", "steps100", "steps300", "steps1000", "oracle", "last"])
        say(f"{m} min, buttons of 6 inside the true 50% / 80% zone: " + ", ".join(f"{a} {6 * v[0]:.1f}/{6 * v[1]:.1f}" for a, v in S.items()))


if __name__ == "__main__":
    if sys.argv[1] == "pilot": pilot(sys.argv[2])
