"""A neural walker under full physics, distilled from the predictive-sampling teacher (mpc3d.py).

A feasibility build, not a preregistered experiment (docs/gait3d-distill.md). The teacher plans by sampling
160 one-second rollouts every 20 ms, about 28 times slower than real time on 4 CPU threads. The student is a
small MLP that maps the body's state and the gait clock to the actuator controls in one forward pass, run on
the same MuJoCo body with contacts, gravity and the same actuators: no playback, no kinematic root.

  python3 -m poc.gait3d.distill MORPH OUT_DIR [rounds] [seconds]

Training is DAgger (Ross et al., 2011): round 0 clones the teacher's own rollouts; each later round lets
the student drive (with probability 1 - beta of using its own action at each 20 ms tick, beta halving each
round) while a teacher planner runs alongside on the visited states and labels them, and the student is
refitted on everything gathered. After every round the student alone walks for `seconds` and is scored:
time until it falls (torso below 0.5 of its standing height, or the head below the teacher's head-low line),
distance, mean forward speed, and its wall time per control tick.
"""
from __future__ import annotations
import json, sys, time
from pathlib import Path
import numpy as np, torch, mujoco
from . import biped3d, mpc3d

CTRL_DT = mpc3d.CTRL_DT


def obs(m, d, t):
    """Body state without the world x, y (so the policy does not see where it is), plus the gait clock."""
    ph = 2 * np.pi * mpc3d.REF_FREQ * t
    return np.concatenate([d.qpos[2:], d.qvel, [np.sin(ph), np.cos(ph)]]).astype(np.float32)


class Policy(torch.nn.Module):
    def __init__(self, n_in, n_out, lo, hi, width=256):
        super().__init__()
        self.net = torch.nn.Sequential(torch.nn.Linear(n_in, width), torch.nn.Tanh(), torch.nn.Linear(width, width), torch.nn.Tanh(), torch.nn.Linear(width, n_out))
        self.register_buffer("mu", torch.zeros(n_in)); self.register_buffer("sd", torch.ones(n_in))
        self.register_buffer("lo", torch.tensor(lo, dtype=torch.float32)); self.register_buffer("hi", torch.tensor(hi, dtype=torch.float32))

    def forward(self, x):   # controls in the actuators' ranges, through a tanh
        z = self.net((x - self.mu) / self.sd); return self.lo + (self.hi - self.lo) * (torch.tanh(z) + 1) / 2

    def act(self, o):
        with torch.no_grad(): return self(torch.from_numpy(o)[None])[0].numpy()


def fit(pol, X, Y, epochs=300, lr=1e-3, seed=0):
    torch.manual_seed(seed); X = torch.from_numpy(np.asarray(X)); Y = torch.from_numpy(np.asarray(Y, np.float32))
    pol.mu.copy_(X.mean(0)); pol.sd.copy_(X.std(0) + 1e-3); opt = torch.optim.Adam(pol.net.parameters(), lr=lr); n = len(X)
    span = (pol.hi - pol.lo).clamp(min=1e-6)
    for ep in range(epochs):
        perm = torch.randperm(n)
        for i in range(0, n, 256):
            b = perm[i:i + 256]; loss = (((pol(X[b]) - Y[b]) / span) ** 2).mean(); opt.zero_grad(); loss.backward(); opt.step()
    with torch.no_grad(): return float((((pol(X) - Y) / span) ** 2).mean())


def fallen(m, d, z_stand, head_id):
    return d.qpos[2] < 0.5 * z_stand or d.geom_xpos[head_id][2] < mpc3d.HEAD_LOW


def rollout(m, morph, seconds, policy=None, teacher_seed=None, beta=0.0, rng=None, stop_on_fall=True, noise=0.0, takeover=None):
    """One rollout from the rest pose. policy None: the teacher drives. Otherwise the student drives, taking the
    teacher's action with probability beta; with teacher_seed set, a teacher planner labels every visited state.
    noise: Gaussian noise of this fraction of each actuator's range is added to the executed controls for a
    held 20 ms tick (DART, Laskey et al., 2017); the labels stay the teacher's clean plan. takeover: the teacher
    drives until this time, then the student. Returns observations, teacher labels (or None), and the score."""
    m, d = biped3d.make(morph); ps = mpc3d.PredictiveSampler(m, teacher_seed) if teacher_seed is not None else None
    n_ctrl = int(round(CTRL_DT / m.opt.timestep)); steps = int(round(seconds / CTRL_DT)); z_stand = d.qpos[2]
    head_id = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_GEOM, "head"); X, Y = [], []; t_pol = 0.0; fell = None; x0 = d.qpos[0]
    for k in range(steps):
        t = k * CTRL_DT; o = obs(m, d, t); u_t = None
        if ps is not None:
            u_t, _ = ps.plan(d, t); X.append(o); Y.append(u_t[0].astype(np.float32))
        if policy is None or (takeover is not None and t < takeover): u = u_t
        else:
            t0 = time.perf_counter(); a = policy.act(o); t_pol += time.perf_counter() - t0
            u = u_t if (u_t is not None and rng is not None and rng.random() < beta) else np.repeat(a[None], n_ctrl, 0)
        if noise > 0 and rng is not None:
            u = np.clip(u + rng.normal(0, noise, m.nu) * (m.actuator_ctrlrange[:, 1] - m.actuator_ctrlrange[:, 0]), m.actuator_ctrlrange[:, 0], m.actuator_ctrlrange[:, 1])
        for i in range(n_ctrl): d.ctrl[:] = u[i]; mujoco.mj_step(m, d)
        if ps is not None: ps.shift()
        if fallen(m, d, z_stand, head_id): fell = (k + 1) * CTRL_DT; break
    T = fell if fell is not None else steps * CTRL_DT
    score = dict(survived=T, fell=fell is not None, distance=float(d.qpos[0] - x0), speed=float((d.qpos[0] - x0) / max(T, 1e-9)),
                 drift=float(d.qpos[1]), policy_ms=1000 * t_pol / max(k + 1, 1))
    return X, Y, score


def main(morph="intact", out_dir="poc/results/distill", rounds=6, seconds=10.0, teacher_seconds=5.0, seeds=(0, 1, 2)):
    out = Path(out_dir); out.mkdir(parents=True, exist_ok=True); torch.set_num_threads(2); log = []
    say = lambda s: print(f"[{time.strftime('%H:%M:%S')}] {s}", flush=True)
    m, d = biped3d.make(morph); X, Y = [], []; T0 = time.time()
    for s in seeds:
        x, y, sc = rollout(m, morph, teacher_seconds, None, teacher_seed=s); X += x; Y += y
        say(f"teacher seed {s}: {len(x)} ticks, survived {sc['survived']:.1f}s, speed {sc['speed']:.2f} m/s [{time.time() - T0:.0f}s]"); log.append(dict(kind="teacher", seed=s, **sc))
    pol = Policy(len(X[0]), m.nu, m.actuator_ctrlrange[:, 0], m.actuator_ctrlrange[:, 1]); rng = np.random.default_rng(0)
    for r in range(rounds):
        mse = fit(pol, X, Y, seed=r)
        _, _, sc = rollout(m, morph, seconds, pol)
        say(f"round {r}: {len(X)} labelled ticks, fit {mse:.4f}; student alone survived {sc['survived']:.1f}s of {seconds:.0f}, distance {sc['distance']:.2f} m, speed {sc['speed']:.2f} m/s, drift {sc['drift']:+.2f} m, {sc['policy_ms']:.2f} ms per tick [{time.time() - T0:.0f}s]")
        log.append(dict(kind="student", round=r, n=len(X), mse=mse, **sc)); torch.save(pol.state_dict(), out / f"{morph}_round{r}.pt")
        json.dump(log, open(out / f"{morph}_log.json", "w"), indent=1)
        if r == rounds - 1: break
        beta = 0.5 ** (r + 1)
        for s in seeds[:2]:
            x, y, sc2 = rollout(m, morph, teacher_seconds, pol, teacher_seed=100 * (r + 1) + s, beta=beta, rng=rng); X += x; Y += y
            say(f"  dagger round {r + 1}, seed {s}, beta {beta:.2f}: {len(x)} new labels, mixed rollout survived {sc2['survived']:.1f}s [{time.time() - T0:.0f}s]")
    say("done")


def main2(morph="intact", out_dir="poc/results/distill2", noisy=(0.05, 0.1, 0.15), seeds=(10, 11, 12, 13), rounds=4, seconds=10.0, teacher_seconds=5.0, base=None):
    """Version 2: the clean teacher walks of version 1 (from its log directory, re-run if absent) plus noisy
    teacher walks at each noise level and seed, then DAgger rounds whose student rollouts start after a teacher
    takeover at a random time in the gait cycle, so corrections are gathered across the whole cycle."""
    out = Path(out_dir); out.mkdir(parents=True, exist_ok=True); torch.set_num_threads(2); log = []; T0 = time.time()
    say = lambda s: print(f"[{time.strftime('%H:%M:%S')}] {s}", flush=True)
    m, d = biped3d.make(morph); rng = np.random.default_rng(1); X, Y = [], []
    data = out / f"{morph}_data.npz"
    if data.exists(): z = np.load(data); X, Y = list(z["X"]), list(z["Y"]); say(f"resumed {len(X)} labelled ticks")
    else:
        for s in (0, 1, 2):
            x, y, sc = rollout(m, morph, teacher_seconds, None, teacher_seed=s); X += x; Y += y; say(f"clean teacher seed {s}: survived {sc['survived']:.1f}s [{time.time() - T0:.0f}s]")
        for sig in noisy:
            for s in seeds:
                x, y, sc = rollout(m, morph, teacher_seconds, None, teacher_seed=1000 * int(100 * sig) + s, rng=rng, noise=sig); X += x; Y += y
                say(f"noisy teacher sigma {sig}, seed {s}: {len(x)} ticks, survived {sc['survived']:.1f}s, speed {sc['speed']:.2f} [{time.time() - T0:.0f}s]"); log.append(dict(kind="noisy_teacher", sigma=sig, seed=s, **sc))
                np.savez(data, X=np.array(X), Y=np.array(Y))
    pol = Policy(len(X[0]), m.nu, m.actuator_ctrlrange[:, 0], m.actuator_ctrlrange[:, 1])
    for r in range(rounds):
        mse = fit(pol, X, Y, seed=r); sc = rollout(m, morph, seconds, pol)[2]
        say(f"round {r}: {len(X)} labelled ticks, fit {mse:.4f}; student alone survived {sc['survived']:.1f}s of {seconds:.0f}, distance {sc['distance']:.2f} m, speed {sc['speed']:.2f} m/s, drift {sc['drift']:+.2f} m, {sc['policy_ms']:.2f} ms per tick [{time.time() - T0:.0f}s]")
        log.append(dict(kind="student", round=r, n=len(X), mse=mse, **sc)); torch.save(pol.state_dict(), out / f"{morph}_round{r}.pt"); json.dump(log, open(out / f"{morph}_log.json", "w"), indent=1)
        if r == rounds - 1: break
        for s in range(3):
            tk = float(rng.uniform(0.2, 2.0))
            x, y, sc2 = rollout(m, morph, tk + 2.0, pol, teacher_seed=500 + 10 * r + s, beta=0.0, rng=rng, takeover=tk); X += x; Y += y
            say(f"  dagger round {r + 1}: teacher to {tk:.1f}s then student, {len(x)} labels, survived {sc2['survived']:.1f}s [{time.time() - T0:.0f}s]")
        np.savez(data, X=np.array(X), Y=np.array(Y))
    say("done")


if __name__ == "__main__":
    if sys.argv[1:2] == ["v2"]: main2(*(sys.argv[2:3] or ["intact"])); sys.exit()
    a = sys.argv[1:]
    main(a[0] if a else "intact", a[1] if len(a) > 1 else "poc/results/distill", int(a[2]) if len(a) > 2 else 6, float(a[3]) if len(a) > 3 else 10.0)
