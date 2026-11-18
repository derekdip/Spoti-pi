"""Per-player personalisation of a VR motion predictor, and when to stop it (docs/netpred.md).

A generic MLP predicts head and hand displacement 100 ms ahead from 267 ms of history (synth.py), trained on
a pooled population. Each new player then gets a LoRA on every layer of it, fitted full-batch on 1, 2 or 5
minutes of their motion, and scored on a fresh 2-minute session of the same player (mean squared error, cm^2).

Stopping, all read off recorded curves except where a fit is named:
- step budgets (100, 300, 1000);
- rule: two half-fits on the first and second half of the player's data in time, each watching the other
  half; g* = the mean of their training-loss drops at the watched minimum; the full fit stops at g*;
- reuse: a relative drop r* = median over calibration players of (knee drop / starting training loss),
  measured once; a new player's fit stops when its training loss has fallen by r* of its start (no extra fits);
- holdout: fit on the first 75% in time, stop at the minimum on the last 25%;
- oracle: the best test error along the full fit.

  python3 -m poc.netpred.personalize pilot OUT_DIR
  python3 -m poc.netpred.personalize run CONFIG.json OUT_DIR
"""
from __future__ import annotations
import json, sys, time
from pathlib import Path
import numpy as np, torch
from . import synth as S

say = lambda s: print(f"[{time.strftime('%H:%M:%S')}] {s}", flush=True)


class LoRALinear(torch.nn.Module):
    def __init__(self, base, rank, seed):
        super().__init__(); self.base = base; g = torch.Generator().manual_seed(seed)
        self.A = torch.nn.Parameter(torch.randn(rank, base.in_features, generator=g) * 0.02); self.B = torch.nn.Parameter(torch.zeros(base.out_features, rank))
    def forward(self, x): return self.base(x) + (x @ self.A.T) @ self.B.T


def mlp(n_in, n_out, width=256):
    return torch.nn.Sequential(torch.nn.Linear(n_in, width), torch.nn.GELU(), torch.nn.Linear(width, width), torch.nn.GELU(), torch.nn.Linear(width, n_out))


class Predictor(torch.nn.Module):
    def __init__(self, n_in=S.K * 9, n_out=9):
        super().__init__(); self.net = mlp(n_in, n_out); self.register_buffer("sx", torch.ones(n_in)); self.register_buffer("sy", torch.ones(n_out))
    def forward(self, x): return self.net(x / self.sx) * self.sy


def with_lora(gen, rank, seed):
    import copy
    m = copy.deepcopy(gen)
    for p in m.parameters(): p.requires_grad_(False)
    layers = [i for i, l in enumerate(m.net) if isinstance(l, torch.nn.Linear)]
    for j, i in enumerate(layers): m.net[i] = LoRALinear(m.net[i], rank, seed + j)
    return m, [p for n, p in m.named_parameters() if n.endswith(".A") or n.endswith(".B")]


def mse(m, x, y):
    with torch.no_grad(): return float(((m(x) - y) ** 2).mean())


def train_generic(n_players, minutes, seed, steps=4000):
    rng = np.random.default_rng(seed); X, Y = [], []
    for p in range(n_players):
        st = S.sample_style(rng); x, y = S.windows(S.session(st, 60 * minutes, seed * 100000 + p), stride=6); X.append(x); Y.append(y)
    X = torch.from_numpy(np.concatenate(X)); Y = torch.from_numpy(np.concatenate(Y)); m = Predictor()
    m.sx.copy_(X.std(0) + 1e-3); m.sy.copy_(Y.std(0) + 1e-3); opt = torch.optim.Adam(m.net.parameters(), lr=1e-3); g = torch.Generator().manual_seed(seed)
    for k in range(steps):
        b = torch.randint(0, len(X), (1024,), generator=g); loss = ((m(X[b]) - Y[b]) ** 2).mean(); opt.zero_grad(); loss.backward(); opt.step()
        if k == steps // 2: opt.param_groups[0]["lr"] = 3e-4
    say(f"generic model: {n_players} players x {minutes} min = {len(X)} windows, train mse {mse(m, X[:20000], Y[:20000]):.3f} cm^2")
    return m


def fit(gen, data, lr, cap, rank, seed, seg=5, watch="te", patience=12, drop=0.25):
    m, ps = with_lora(gen, rank, seed); opt = torch.optim.Adam(ps, lr=lr); x, y = data["tr"]
    ev = lambda: {k: mse(m, *v) for k, v in data.items()}
    out = {k: [v] for k, v in ev().items()}; out["step"] = [0]; peak, kp = -np.inf, 0; out["stopped"] = "cap"
    for k in range(cap // seg):
        for _ in range(seg): loss = ((m(x) - y) ** 2).mean(); opt.zero_grad(); loss.backward(); opt.step()
        cur = ev(); out["step"].append((k + 1) * seg)
        for kk, v in cur.items(): out[kk].append(v)
        g = out[watch][0] - cur[watch]
        if g > peak: peak, kp = g, k
        if k - kp >= patience and g <= drop * peak: out["stopped"] = "turned"; break
    return out


def player_data(style, minutes, seed):
    X = S.session(style, 60 * minutes, seed); T = torch.from_numpy
    x, y = S.windows(X, stride=2); n = len(x); h = n // 2; q = int(0.75 * n)
    return dict(all=(T(x), T(y)), A=(T(x[:h]), T(y[:h])), B=(T(x[h:]), T(y[h:])), fit75=(T(x[:q]), T(y[:q])), last25=(T(x[q:]), T(y[q:])))


def run_player(gen, style, minutes, pseed, cfg):
    d = player_data(style, minutes, pseed); xt, yt = S.windows(S.session(style, 120, pseed + 7), stride=2); te = (torch.from_numpy(xt), torch.from_numpy(yt))
    lr, cap, r = cfg["lr"], cfg["cap"], cfg["rank"]
    sg = cfg.get("seg", 10)
    full = fit(gen, dict(tr=d["all"], te=te), lr, cap, r, pseed, seg=sg)
    halves = [fit(gen, dict(tr=d[a], ho=d[b]), lr, cfg["cap_half"], r, pseed + 1 + i, seg=sg, watch="ho", drop=0.5) for i, (a, b) in enumerate((("A", "B"), ("B", "A")))]
    hold = fit(gen, dict(tr=d["fit75"], ho=d["last25"], te=te), lr, cap, r, pseed + 3, seg=sg, watch="ho", drop=0.5)
    cv = float(((S.const_velocity(xt) - yt) ** 2).mean())
    return dict(full=full, halves=halves, hold=hold, const_vel=cv, minutes=minutes)


def score_player(rec, r_star=None):
    f = rec["full"]; tr = np.array(f["tr"]); te = np.array(f["te"]); st = np.array(f["step"]); base = te[0]; gain = base - te; pk = gain.max()
    at_drop = lambda g: (gain[int(np.argmax(tr[0] - tr >= g))] if (tr[0] - tr >= g).any() else gain[-1])
    knees = [h["tr"][0] - h["tr"][int(np.argmin(h["ho"]))] for h in rec["halves"]]; rel = [k / h["tr"][0] for k, h in zip(knees, rec["halves"])]
    out = dict(minutes=rec["minutes"], base=base, const_vel=rec["const_vel"], oracle=float(te.min()), oracle_step=int(st[int(np.argmax(gain))]), peak_gain=float(pk),
               knee_full=float(tr[0] - tr[int(np.argmax(gain))]), knee_rel_full=float((tr[0] - tr[int(np.argmax(gain))]) / tr[0]), half_knees=knees, half_rel=rel,
               rule=float(base - at_drop(np.mean(knees))), last=float(te[-1]), turned=f["stopped"] == "turned")
    for b in (100, 300, 1000): out[f"steps{b}"] = float(np.interp(b, st, te))
    h = rec["hold"]; out["holdout"] = float(h["te"][int(np.argmin(h["ho"]))]); out["holdout_refit"] = float(np.interp(h["step"][int(np.argmin(h["ho"]))], st, te))
    if r_star is not None: out["reuse"] = float(base - at_drop(r_star * tr[0]))
    return out


def _job(args):
    gen_path, style, minutes, pseed, cfg = args; torch.set_num_threads(1)
    gen = Predictor(); gen.load_state_dict(torch.load(gen_path)); return pseed, minutes, run_player(gen, style, minutes, pseed, cfg)


def run(cfg_path, out_dir):
    """The scored run: calibration and evaluation players drawn fresh from seed `players_seed`, every player at
    every data size, four players at a time. Rows go to rows.json as they finish; score() reads them."""
    cfg = json.load(open(cfg_path)); out = Path(out_dir); out.mkdir(parents=True, exist_ok=True); T0 = time.time()
    if (out / "config.json").resolve() != Path(cfg_path).resolve(): json.dump(cfg, open(out / "config.json", "w"), indent=1)
    gp = out / "generic.pt"
    if not gp.exists(): torch.set_num_threads(4); torch.save(train_generic(cfg["generic_players"], cfg["generic_minutes"], cfg["generic_seed"]).state_dict(), gp)
    rng = np.random.default_rng(cfg["players_seed"]); n = cfg["calib"] + cfg["eval"]; styles = [S.sample_style(rng) for _ in range(n)]
    rows_p = out / "rows.json"; rows = json.load(open(rows_p)) if rows_p.exists() else []; done = {(r["player"], r["minutes"]) for r in rows}
    jobs = [(str(gp), styles[p], m, cfg["players_seed"] * 1000 + 10 * p, cfg["fit"]) for p in range(n) for m in cfg["minutes"] if (p, m) not in done]
    from multiprocessing import Pool
    with Pool(cfg.get("workers", 4)) as pool:
        for pseed, m, rec in pool.imap_unordered(_job, jobs):
            p = (pseed - cfg["players_seed"] * 1000) // 10; rows.append(dict(player=p, role="calib" if p < cfg["calib"] else "eval", minutes=m, rec=rec))
            json.dump(rows, open(rows_p, "w")); sc = score_player(rec)
            say(f"player {p} ({rows[-1]['role']}), {m} min: base {sc['base']:.3f}, best {sc['oracle']:.3f} (step {sc['oracle_step']}), rule {sc['rule']:.3f}, holdout {sc['holdout']:.3f} [{len(rows)} of {n * len(cfg['minutes'])}, {time.time() - T0:.0f}s]")
    say("done")


def score(out_dir):
    out = Path(out_dir); cfg = json.load(open(out / "config.json")); rows = json.load(open(out / "rows.json")); B = cfg["bars"]
    arms = ["rule", "reuse", "holdout", "holdout_refit", "steps100", "steps300", "steps1000", "last"]
    L = ["# Personalising a VR motion predictor: when to stop (frozen scorer)\n", "Share of the possible personalisation gain kept, (generic - arm) / (generic - best along the fit); negative = worse than the generic model.\n"]
    verdicts = {}
    for m in cfg["minutes"]:
        cal = [score_player(r["rec"]) for r in rows if r["role"] == "calib" and r["minutes"] == m]; r_star = float(np.median([c["knee_rel_full"] for c in cal]))
        ev = [score_player(r["rec"], r_star) for r in rows if r["role"] == "eval" and r["minutes"] == m]
        sh = {a: np.array([(e["base"] - e[a]) / max(e["base"] - e["oracle"], 1e-9) for e in ev]) for a in arms}
        L += [f"\n## {m} minute{'s' if m > 1 else ''} of motion ({len(ev)} players; calibrated relative drop r* = {r_star:.3f} from {len(cal)} players)\n",
              f"Error 100 ms ahead, mean over players (cm^2): constant velocity {np.mean([e['const_vel'] for e in ev]):.3f}, generic {np.mean([e['base'] for e in ev]):.3f}, best personalised {np.mean([e['oracle'] for e in ev]):.3f}.\n",
              "| stop | mean share kept | lowest | players worse than generic | mean error (cm^2) |", "|---|---|---|---|---|"]
        for a in arms: L.append(f"| {a} | {sh[a].mean():+.2f} | {sh[a].min():+.2f} | {int((sh[a] < 0).sum())} of {len(ev)} | {np.mean([e[a] for e in ev]):.3f} |")
        best_budget = max(("steps100", "steps300", "steps1000"), key=lambda a: sh[a].mean())
        N1 = sh["rule"].mean() >= B["keep_mean"] and (sh["rule"] > 0).mean() >= B["not_worse_share"]
        N2 = sh["rule"].mean() >= sh[best_budget].mean()
        N3 = sh["reuse"].mean() >= sh["rule"].mean() - B["reuse_margin"]
        verdicts[m] = (N1, N2, N3)
        L += [f"\n- **N1** (the rule keeps at least {B['keep_mean']:.0%} on average and does not end below the generic model for at least {B['not_worse_share']:.0%} of players): {sh['rule'].mean():.2f}, {(sh['rule'] > 0).mean():.0%}: **{'holds' if N1 else 'fails'}**",
              f"- **N2** (the rule keeps at least what the best fixed step budget keeps, chosen with the test data in hand: {best_budget}): {sh['rule'].mean():.2f} against {sh[best_budget].mean():.2f}: **{'holds' if N2 else 'fails'}**",
              f"- **N3** (reuse of one calibrated relative drop is within {B['reuse_margin']} of the rule, with no extra fits): {sh['reuse'].mean():.2f} against {sh['rule'].mean():.2f}: **{'holds' if N3 else 'fails'}**"]
    allok = {k: all(v[i] for v in verdicts.values()) for i, k in enumerate(("N1", "N2", "N3"))}
    L.append(f"\n**Outcome: {'A' if all(allok.values()) else 'B' if allok['N1'] else 'C'}** (A: N1 to N3 hold at every size; B: N1 holds everywhere, N2 or N3 fails somewhere; C: N1 fails somewhere).")
    (out / "report.md").write_text("\n".join(L) + "\n"); print("\n".join(L))


def pilot(out_dir):
    out = Path(out_dir); out.mkdir(parents=True, exist_ok=True); torch.set_num_threads(4); T0 = time.time()
    gen = train_generic(60, 3, seed=1); torch.save(gen.state_dict(), out / "generic.pt")
    rng = np.random.default_rng(999); cfg = dict(lr=1e-3, cap=3000, cap_half=2000, rank=4); res = []
    for p in range(4):
        st = S.sample_style(rng)
        for mins in (1, 5):
            rec = run_player(gen, st, mins, 500000 + 10 * p, cfg); sc = score_player(rec); res.append(dict(rec=rec, score=sc))
            say(f"player {p}, {mins} min: base {sc['base']:.2f}, const-vel {sc['const_vel']:.2f}, best {sc['oracle']:.2f} at step {sc['oracle_step']}, end {sc['last']:.2f} ({rec['full']['stopped']} at {rec['full']['step'][-1]}); "
                f"rule {sc['rule']:.2f}, holdout {sc['holdout']:.2f}, 300 steps {sc['steps300']:.2f}; knee {sc['knee_full']:.3f} (rel {sc['knee_rel_full']:.2f}), half knees {np.round(sc['half_knees'], 3)} [{time.time() - T0:.0f}s]")
            json.dump([r["score"] for r in res], open(out / "pilot_scores.json", "w"), indent=1)
    json.dump(res, open(out / "pilot_rows.json", "w"))


if __name__ == "__main__":
    if sys.argv[1] == "pilot": pilot(sys.argv[2])
    elif sys.argv[1] == "run": run(sys.argv[2], sys.argv[3])
    elif sys.argv[1] == "score": score(sys.argv[2])
