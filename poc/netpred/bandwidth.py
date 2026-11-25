"""Model-predictive avatar sync: how many bytes a shared motion model saves at a guaranteed error (docs/netpred-bandwidth.md).

Sender and receiver run the same deterministic predictor. After each anchor (the last frame at which anything
was sent, or the end of the predicted horizon) the receiver predicts every tracker's path forward from its own
reconstructed history; the sender simulates exactly the same reconstruction and, at each 90 Hz frame, sends a
tracker's true position (head, left hand, right hand) only when the receiver's estimate of it would be more
than `tol` away (Euclidean, metres). The receiver's error is therefore never above `tol` at any frame. No
network delay here: the guarantee is exact, and delay is a separate question.

Bytes: a packet is a 4-byte header plus 6 bytes per tracker sent (three 16-bit coordinates). Streaming every
tracker every frame costs 90 x (4 + 18) = 1980 B/s per player.

Receivers:
- hold: the last received value;
- deadreck: constant velocity from the last two reconstructed frames;
- generic: an MLP mapping 24 frames of reconstructed history to the displacement 1 to 45 frames ahead,
  trained on a pooled population (synth.py players);
- personal: the generic MLP with a rank-4 LoRA fitted on 2 minutes of the player, stopped by the cross-fitted
  rule (two half-fits in time, each watching the other; stop the full fit at the mean of their training-loss
  drops at the watched minimum).

  python3 -m poc.netpred.bandwidth pilot OUT_DIR
"""
from __future__ import annotations
import json, sys, time
from pathlib import Path
import numpy as np, torch
from . import synth as S
from .personalize import Predictor, with_lora, mlp

say = lambda s: print(f"[{time.strftime('%H:%M:%S')}] {s}", flush=True)
K, HMAX = S.K, 45
HDR, PER = 4, 6


def mh_windows(X, stride=3):
    idx = np.arange(K - 1, len(X) - HMAX, stride)
    past = np.stack([X[i - K + 1:i + 1] - X[i] for i in idx]); fut = np.stack([X[i + 1:i + HMAX + 1] - X[i] for i in idx])
    return (100 * past.reshape(len(idx), -1)).astype(np.float32), (100 * fut.reshape(len(idx), -1)).astype(np.float32)


def train_generic(n_players, minutes, seed, steps=5000, width=256):
    rng = np.random.default_rng(seed); X, Y = [], []
    for p in range(n_players):
        st = S.sample_style(rng); x, y = mh_windows(S.session(st, 60 * minutes, seed * 100000 + p), stride=6); X.append(x); Y.append(y)
    X = torch.from_numpy(np.concatenate(X)); Y = torch.from_numpy(np.concatenate(Y)); m = Predictor(n_in=K * 9, n_out=HMAX * 9)
    if width != 256: m.net = mlp(K * 9, HMAX * 9, width)
    m.sx.copy_(X.std(0) + 1e-3); m.sy.copy_(Y.std(0) + 1e-3); opt = torch.optim.Adam(m.net.parameters(), lr=1e-3); g = torch.Generator().manual_seed(seed)
    for k in range(steps):
        b = torch.randint(0, len(X), (1024,), generator=g); loss = ((m(X[b]) - Y[b]) ** 2).mean(); opt.zero_grad(); loss.backward(); opt.step()
        if k == steps // 2: opt.param_groups[0]["lr"] = 3e-4
    with torch.no_grad(): say(f"generic multi-horizon model: {len(X)} windows, train mse {float(((m(X[:20000]) - Y[:20000]) ** 2).mean()):.3f} cm^2")
    return m


def personalise(gen, X, lr=1e-3, cap=1500, rank=4, seed=0, seg=5):
    """The cross-fitted rule on one player's session X: returns the adapted model and its stopping value."""
    x, y = map(torch.from_numpy, mh_windows(X, stride=2)); n = len(x); h = n // 2
    def run(xt, yt, watch=None, stop_gain=None):
        m, ps = with_lora(gen, rank, seed); opt = torch.optim.Adam(ps, lr=lr)
        with torch.no_grad(): t0 = float(((m(xt) - yt) ** 2).mean()); w0 = float(((m(watch[0]) - watch[1]) ** 2).mean()) if watch else None
        best = (np.inf, 0.0); since = 0
        for k in range(cap // seg):
            for _ in range(seg): loss = ((m(xt) - yt) ** 2).mean(); opt.zero_grad(); loss.backward(); opt.step()
            with torch.no_grad(): tr = float(((m(xt) - yt) ** 2).mean())
            if stop_gain is not None and t0 - tr >= stop_gain: return m, t0 - tr
            if watch:
                with torch.no_grad(): w = float(((m(watch[0]) - watch[1]) ** 2).mean())
                if w < best[0]: best = (w, t0 - tr); since = 0
                else: since += 1
                if since >= 12 and w0 - w <= 0.5 * (w0 - best[0]): break
        return m, (best[1] if watch else t0 - tr)
    knees = [run(x[:h], y[:h], (x[h:], y[h:]))[1], run(x[h:], y[h:], (x[:h], y[:h]))[1]]; g = float(np.mean(knees))
    m, got = run(x, y, stop_gain=g); return m, g


def simulate(X, kind, tol, model=None):
    """Replay a session through the protocol; returns bytes/s, tracker updates/s, packets/s and the max error."""
    T = len(X); R = np.zeros_like(X); R[:K] = X[:K]; packets = K; trackers = 3 * K; t0 = K - 1; traj = None; err_max = 0.0
    def predict(t0):
        if kind == "hold": return np.zeros((HMAX, 9))
        if kind == "deadreck": v = R[t0] - R[t0 - 1]; return np.arange(1, HMAX + 1)[:, None] * v[None]
        if kind == "deadreck_smooth": v = (R[t0] - R[t0 - 6]) / 6; return np.arange(1, HMAX + 1)[:, None] * v[None]
        h = torch.from_numpy((100 * (R[t0 - K + 1:t0 + 1] - R[t0])).reshape(1, -1).astype(np.float32))
        with torch.no_grad(): return model(h)[0].numpy().reshape(HMAX, 9) / 100
    traj = predict(t0)
    for t in range(K, T):
        k = t - t0
        if k > HMAX: t0 = t - 1; traj = predict(t0); k = 1          # past the horizon: re-anchor on the receiver's own track
        est = R[t0] + traj[k - 1]; sent = 0
        for j in range(3):
            sl = slice(3 * j, 3 * j + 3); e = np.linalg.norm(est[sl] - X[t, sl])
            if e > tol: R[t, sl] = X[t, sl]; sent += 1
            else: R[t, sl] = est[sl]; err_max = max(err_max, e)
        if sent: packets += 1; trackers += sent; t0 = t; traj = predict(t0)
    sec = T / S.HZ; return dict(bytes_s=(packets * HDR + trackers * PER) / sec, trackers_s=trackers / sec, packets_s=packets / sec, err_max=err_max)


def pilot(out_dir):
    out = Path(out_dir); out.mkdir(parents=True, exist_ok=True); torch.set_num_threads(4); T0 = time.time()
    gen = train_generic(60, 3, seed=11); torch.save(gen.state_dict(), out / "generic.pt")
    rng = np.random.default_rng(1234); rows = []; tols = (0.005, 0.01, 0.02)
    for p in range(6):
        st = S.sample_style(rng); fitX = S.session(st, 120, 700000 + p); testX = S.session(st, 180, 800000 + p)
        pm, g = personalise(gen, fitX, seed=p)
        for tol in tols:
            r = dict(player=p, tol=tol, gstar=g)
            for kind, m in (("hold", None), ("deadreck", None), ("generic", gen), ("personal", pm)): r[kind] = simulate(testX, kind, tol, m)
            rows.append(r); json.dump(rows, open(out / "pilot_rows.json", "w"), indent=1)
            say(f"player {p}, tolerance {100 * tol:.1f} cm: bytes/s hold {r['hold']['bytes_s']:.0f}, dead reckoning {r['deadreck']['bytes_s']:.0f}, generic {r['generic']['bytes_s']:.0f}, personal {r['personal']['bytes_s']:.0f} (stream 1980); max error {100 * max(r[k]['err_max'] for k in ('hold', 'deadreck', 'generic', 'personal')):.2f} cm [{time.time() - T0:.0f}s]")
    for tol in tols:
        R = [r for r in rows if r["tol"] == tol]; m = {k: np.mean([r[k]["bytes_s"] for r in R]) for k in ("hold", "deadreck", "generic", "personal")}
        say(f"tolerance {100 * tol:.1f} cm, mean bytes/s: " + ", ".join(f"{k} {v:.0f}" for k, v in m.items()) + f"; generic vs dead reckoning {100 * (1 - m['generic'] / m['deadreck']):.0f}% fewer, personal vs generic {100 * (1 - m['personal'] / m['generic']):.0f}% fewer")


KINDS = ("hold", "deadreck", "deadreck_smooth", "generic_small", "generic", "personal")


def run(cfg_path, out_dir):
    cfg = json.load(open(cfg_path)); out = Path(out_dir); out.mkdir(parents=True, exist_ok=True); torch.set_num_threads(4); T0 = time.time()
    if (out / "config.json").resolve() != Path(cfg_path).resolve(): json.dump(cfg, open(out / "config.json", "w"), indent=1)
    gen = train_generic(cfg["generic_players"], cfg["generic_minutes"], cfg["generic_seed"]); small = train_generic(cfg["generic_players"], cfg["generic_minutes"], cfg["generic_seed"], width=cfg["small_width"])
    rng = np.random.default_rng(cfg["players_seed"]); rows = []
    for p in range(cfg["players"]):
        st = S.sample_style(rng); base = cfg["players_seed"] * 1000 + 10 * p
        fitX = S.session(st, 60 * cfg["fit_minutes"], base); testX = S.session(st, 60 * cfg["test_minutes"], base + 1); pm, g = personalise(gen, fitX, seed=base)
        for tol in cfg["tols"]:
            r = dict(player=p, tol=tol, gstar=g, **{k: simulate(testX, k, tol, dict(generic=gen, generic_small=small, personal=pm).get(k)) for k in KINDS}); rows.append(r)
            json.dump(rows, open(out / "rows.json", "w"), indent=1)
        say(f"player {p}: at 1 cm, bytes/s " + ", ".join(f"{k} {[x for x in rows if x['player'] == p and x['tol'] == 0.01][0][k]['bytes_s']:.0f}" for k in KINDS) + f" [{time.time() - T0:.0f}s]")
    say("done")


def score(out_dir):
    out = Path(out_dir); cfg = json.load(open(out / "config.json")); rows = json.load(open(out / "rows.json")); B = cfg["bars"]
    L = ["# Model-predictive avatar sync (frozen scorer)\n", f"Bytes per second per player (streaming every frame: 1980), mean over {cfg['players']} players; the receiver's error never exceeds the tolerance by construction, checked below.\n",
         "| receiver | " + " | ".join(f"{100 * t:.1f} cm" for t in cfg["tols"]) + " |", "|---|" + "---|" * len(cfg["tols"])]
    mean = lambda k, t: float(np.mean([r[k]["bytes_s"] for r in rows if r["tol"] == t]))
    for k in KINDS: L.append(f"| {k} | " + " | ".join(f"{mean(k, t):.0f}" for t in cfg["tols"]) + " |")
    W = {}
    simple = lambda t: min(mean(k, t) for k in ("hold", "deadreck", "deadreck_smooth"))
    W["W1"] = all(mean("generic", t) <= (1 - B["generic_saving"]) * simple(t) for t in cfg["tols"])
    W["W2"] = all(r[k]["err_max"] <= r["tol"] + 1e-12 for r in rows for k in KINDS)
    W["W3"] = mean("personal", 0.01) <= (1 - B["personal_saving"]) * mean("generic", 0.01)
    W["W4"] = all(mean("generic", t) < mean("generic_small", t) for t in cfg["tols"])
    L += ["", f"- **W1** (the learned receiver sends at least {B['generic_saving']:.0%} fewer bytes than the best simple receiver at every tolerance): " + ", ".join(f"{100 * (1 - mean('generic', t) / simple(t)):.0f}%" for t in cfg["tols"]) + f": **{'holds' if W['W1'] else 'fails'}**",
          f"- **W2** (the receiver's error never exceeds the tolerance, any receiver, any player): **{'holds' if W['W2'] else 'fails'}**",
          f"- **W3** (personalising saves at least {B['personal_saving']:.0%} more at 1 cm): {100 * (1 - mean('personal', 0.01) / mean('generic', 0.01)):.1f}%: **{'holds' if W['W3'] else 'fails'}**",
          f"- **W4** (the larger receiver model sends fewer bytes than the small one at every tolerance): " + ", ".join(f"{mean('generic_small', t):.0f} against {mean('generic', t):.0f}" for t in cfg["tols"]) + f": **{'holds' if W['W4'] else 'fails'}**"]
    (out / "report.md").write_text("\n".join(L) + "\n"); print("\n".join(L))


if __name__ == "__main__":
    if sys.argv[1] == "pilot": pilot(sys.argv[2])
    elif sys.argv[1] == "run": run(sys.argv[2], sys.argv[3])
    elif sys.argv[1] == "score": score(sys.argv[2])
