"""The ECS-Decision suite on the tiny transformer (docs/math-track-ed1-prereg.md).

  /usr/bin/python3 -m poc.ecsdec.suite pilot 0          the declared pilot on world 0 (nothing scored)
  /usr/bin/python3 -m poc.ecsdec.suite pilot2 0         its second block (the corrected collinear case, student restarts)
  /usr/bin/python3 -m poc.ecsdec.suite pilot3 0         its third block (the joint full fits of the augmented model)
  /usr/bin/python3 -m poc.ecsdec.suite arm full 1       one arm (full, A, B, C, D, E or sweeps) on world 1 -> poc/results/ed1/arm_<name>.json
  /usr/bin/python3 -m poc.ecsdec.suite merge            the arms -> ed1.json, per_case_metrics.csv, equivalence_summary.csv, sweeps.csv

Cases, each with its right action by construction (the target is the base model plus planted deltas):
  refine_early   planted rank-2 on wv@0; student rank-2 on wv@0 after a small fraction of the budget
  refine_mid     the same after a larger fraction, still inadequate
  saddle         the same, student at the all-zero point (B = A = 0: stationary, indefinite)
  reuse          planted rank-4 on wv@0; student rank-1 on wv@0 fitted to the budget           -> EXPAND:wv@0
  collinear      planted rank-2 on wv@0; student rank-4 whose A rows agree to 1e-6             -> REPARAMETERIZE
  extend         planted rank-2 on w2@1; student rank-2 on wv@0 fitted to the budget           -> EXPAND:w2@1
  noise          target = base plus independent noise on the training and held-out probes     -> FALLBACK
  adequate       the rank-2 student fitted to the budget on the rank-2 target (D below D_max)  -> STOP
  pairs          wv@1 | wo@1 (one first-order span by construction) and wv@0 | w2@1             -> COLLAPSE, KEEP DISTINCT
  sweeps         noise on refine_early, reuse, extend, adequate; the extend magnitude across D_max
"""
from __future__ import annotations
import csv, json, sys, time
from pathlib import Path
import jax, jax.numpy as jnp, numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from poc.ecsdec import model as M
from poc.ecsdec import decide as Dc

OUT = Path(__file__).resolve().parents[2] / "poc/results/ed1"; OUT.mkdir(parents=True, exist_ok=True)
STEPS, LR, N_PROBE = 300, 0.02, 256
CAND_RANK = 4
# a candidate syntax is a module: its first-order geometry is read from the dense delta at the neutral state (a
# LoRA's Jacobian at B = A = 0 is zero), and it is fitted and costed as a rank-CAND_RANK adapter on that module
CANDS = {n: dict(geom=[(n, "bias" if n == "out_bias" else "full", 0)], fit=[(n, "bias" if n == "out_bias" else "lora", 0 if n == "out_bias" else CAND_RANK)])
         for n in ("wv@0", "wo@0", "wv@1", "wo@1", "w1@1", "w2@1", "out_bias")}
FALLBACK = [c["fit"][0] for c in CANDS.values()]                              # every module at once
CASES = ["refine_early", "refine_mid", "saddle", "reuse", "collinear", "extend", "noise", "adequate"]
PAIRS = (("wv@1", "wo@1"), ("wv@0", "w2@1"))
log = lambda m: print(f"[{time.strftime('%H:%M:%S')}] {m}", flush=True)


def world(seed):
    """The base model and the probe sets, deterministic in the seed."""
    gen = M.make_generator(seed); params, curve = M.train_base(jax.random.PRNGKey(seed), gen, steps=1500, seed=seed, log=log)
    rng = np.random.default_rng(seed + 1); probes = jnp.asarray(M.sample_sequences(gen, rng, 2 * N_PROBE, M.CFG["ctx"]))
    return dict(seed=seed, params=params, probes_tr=probes[:N_PROBE], probes_ho=probes[N_PROBE:], loss=curve[-1],
                G=M.probe_fn(params, probes[:N_PROBE]), Gh=M.probe_fn(params, probes[N_PROBE:]))


def planted(key, module, rank, scale):
    shp = M.shape_of(module); k1, k2 = jax.random.split(key)
    A = jax.random.normal(k1, (rank, shp[1])) / np.sqrt(shp[1]); Bm = jax.random.normal(k2, (shp[0], rank)) / np.sqrt(rank)
    return {module: scale * Bm @ A}, (A, Bm)


def target_x(W, deltas, noise=0.0, key=None):
    """The target's probe distributions, with optional independent noise at `noise` of x's rms on each set."""
    x = W["G"]([], deltas)(jnp.zeros(0)); xh = W["Gh"]([], deltas)(jnp.zeros(0))
    if noise > 0:
        k1, k2 = jax.random.split(key); rms = float(jnp.sqrt(jnp.mean(x ** 2)))
        x = x + noise * rms * jax.random.normal(k1, x.shape); xh = xh + noise * rms * jax.random.normal(k2, xh.shape)
    return x, xh


def build_case(name, W, key, cfg, noise=0.0, mag=1.0):
    """Returns (truth, fam, theta, x, x_held, note)."""
    sc = cfg["plant_scale"]; ks = jax.random.split(key, 4); G = W["G"]
    if name in ("refine_early", "refine_mid", "saddle", "collinear", "adequate"):
        deltas, (A, Bm) = planted(ks[0], "wv@0", 2, sc); x, xh = target_x(W, deltas, noise, ks[1])
        if name == "collinear":
            fam = [("wv@0", "lora", 4)]; r, din = 4, 32; row = np.asarray(M.init_theta(fam, ks[2])[:din]); rng = np.random.default_rng(int(ks[3][0]) % 2 ** 31)
            A_flat = jnp.asarray(np.stack([row + cfg["collinear_eps"] * rng.standard_normal(din) for _ in range(r)]).reshape(-1))
            b, _ = M.fit(lambda b_: G(fam)(jnp.concatenate([A_flat, b_])), x, jnp.zeros(r * 32), STEPS, LR)        # A held, B fitted
            return "REPARAMETERIZE", fam, jnp.concatenate([A_flat, b]), x, xh, f"rank 4, A rows equal to {cfg['collinear_eps']:g}, B fitted with A held"
        fam = [("wv@0", "lora", 2)]
        if name == "saddle": return "GLOBALIZE", fam, jnp.zeros(M.family_size(fam)), x, xh, "theta = 0"
        if name == "adequate":
            return "STOP", fam, best_fit(G(fam), x, fam, ks[2], cfg), x, xh, "rank 2 fitted to the budget"
        frac = cfg["refine_fracs"][0 if name == "refine_early" else 1]
        th, _ = M.fit(G(fam), x, M.init_theta(fam, ks[2]), int(frac * STEPS), LR); return "REFINE", fam, th, x, xh, f"fitted {frac:.0%} of the budget"
    if name == "reuse":
        deltas, _ = planted(ks[0], "wv@0", 4, sc); x, xh = target_x(W, deltas, noise, ks[1]); fam = [("wv@0", "lora", 1)]
        return "EXPAND:wv@0", fam, best_fit(G(fam), x, fam, ks[2], cfg), x, xh, "rank 1 against planted rank 4"
    if name == "extend":
        deltas, _ = planted(ks[0], "w2@1", 2, sc * mag); x, xh = target_x(W, deltas, noise, ks[1]); fam = [("wv@0", "lora", 2)]
        return "EXPAND:w2@1", fam, best_fit(G(fam), x, fam, ks[2], cfg), x, xh, f"planted on w2@1 at {mag} of the scale"
    if name == "noise":
        x, xh = target_x(W, {}); rms = float(jnp.sqrt(jnp.mean(x ** 2))); k1, k2 = jax.random.split(ks[1]); a = cfg["noise_case_level"] * rms
        x = x + a * jax.random.normal(k1, x.shape); xh = xh + a * jax.random.normal(k2, xh.shape); fam = [("wv@0", "lora", 2)]
        return "FALLBACK", fam, best_fit(G(fam), x, fam, ks[2], cfg), x, xh, "base plus independent noise"
    raise ValueError(name)


def best_fit(G, x, fam, key, cfg):
    """The student of the fitted cases: the best of `student_restarts` fits at the budget."""
    best = None
    for k in jax.random.split(key, cfg.get("student_restarts", 1)):
        th, Fv = M.fit(G, x, M.init_theta(fam, k), STEPS, LR)
        if best is None or Fv < best[1]: best = (th, Fv)
    return best[0]


def correct(got, truth):
    """EXPAND truths name the planted module; wv@l and wo@l are one syntax class at first order and exactly
    (one head: Wv' delta_o = delta_v Wo), so either is accepted where the truth names one of them."""
    if not truth.startswith("EXPAND"): return got.split(":")[0] == truth
    m = truth.split(":")[1]; ok = {m, m.replace("wv@", "wo@") if m.startswith("wv@") else m.replace("wo@", "wv@")}
    return got.startswith("EXPAND:") and got.split(":")[1] in ok


def run_case(name, W, key, cfg, abl=None, noise=0.0, mag=1.0):
    truth, fam, th, x, xh, note = build_case(name, W, key, cfg, noise, mag)
    rec = Dc.decide(W["G"], W["Gh"], fam, th, x, xh, CANDS, FALLBACK, jax.random.fold_in(key, 77), STEPS, LR, abl)
    got = rec["action"] + (":" + rec["chosen"] if rec["action"] == "EXPAND" else "")
    rec.update(case=name, truth=truth, got=got, note=note, abl=abl or "full", noise=noise, mag=mag, correct=correct(got, truth))
    return rec


def pair_case(W, key, cfg, pair, abl=None):
    """The equivalence stage alone, on the extend case's residual."""
    truth, fam, th, x, xh, _ = build_case("extend", W, key, cfg); g = Dc.geometry(W["G"](fam), x, th)
    cg = Dc.candidate_geometry(W["G"], fam, th, {p: CANDS[p]["geom"] for p in pair}, g, abl); pg = Dc.pair_geometry(cg[pair[0]], cg[pair[1]])
    return dict(pair=list(pair), geometry=pg, collapse=Dc.equivalent(pg), collapse_matched=Dc.equivalent_matched(pg), truth=(pair == PAIRS[0]),
                dims=[cg[p]["dim"] for p in pair], eta={p: cg[p]["eta"] for p in pair})


def fmt(rec):
    return (f"{rec['abl']:<6} {rec['case']:<13} truth {rec['truth']:<14} got {rec['got']:<16} {'ok' if rec['correct'] else 'MISS'}  D {rec['D']:.3f} s {rec['stat']:.1e} "
            f"tau {rec['tau']:.2f} kappa {rec['kappa']:.1e} lam {rec['lam_min']:.1e}/{rec['hnorm']:.1e} stage {rec['first_stage']} fits {rec['fits_run']}")


def pilot(seed):
    """The declared pilot: the numbers the prereg freezes from. Nothing here is scored."""
    W = world(seed); G = W["G"]; key = jax.random.PRNGKey(100); log(f"base final loss {W['loss']:.3f}")
    base = G([], {})(jnp.zeros(0))
    for scale in (0.5, 1.0, 2.0):
        deltas, _ = planted(key, "wv@0", 2, scale); x, _ = target_x(W, deltas)
        log(f"planted scale {scale}: normalised distance base to target {float(jnp.linalg.norm(x - base) / jnp.linalg.norm(x)):.3f}")
    scale = 1.0; deltas, (A, Bm) = planted(key, "wv@0", 2, scale); x, xh = target_x(W, deltas); fam = [("wv@0", "lora", 2)]
    for steps in (6, 15, 30, 60, 120, 300):
        th, _ = M.fit(G(fam), x, M.init_theta(fam, jax.random.PRNGKey(5)), steps, LR); g = Dc.geometry(G(fam), x, th)
        log(f"rank-2 student, {steps:>3} of {STEPS} steps: D {g['D']:.3f} s {g['stat']:.2e} tau {g['tau']:.3f} gamma {g['gamma']:.2e} kappa {g['kappa']:.1e} lam_min {g['lam_min']:.2e} |H| {g['hnorm']:.2e} rank {g['rank']}/{g['n_theta']}")
    g0 = Dc.geometry(G(fam), x, jnp.zeros(M.family_size(fam))); log(f"theta = 0: D {g0['D']:.3f} s {g0['stat']:.1e} lam_min {g0['lam_min']:.2e} |H| {g0['hnorm']:.2e} rank {g0['rank']}")
    cfg = dict(plant_scale=scale, refine_fracs=(0.05, 0.15), collinear_eps=1e-6, noise_case_level=0.5, student_restarts=1)
    for name, k in (("reuse", 4), ("extend", 6), ("noise", 8), ("adequate", 9)):
        _, f, t, xx, xxh, _ = build_case(name, W, jax.random.PRNGKey(k), cfg); gg = Dc.geometry(G(f), xx, t)
        log(f"{name} fitted to the budget: D {gg['D']:.3f} s {gg['stat']:.2e} tau {gg['tau']:.2f} kappa {gg['kappa']:.1e} lam_min {gg['lam_min']:.2e} |H| {gg['hnorm']:.2e} D_held {Dc.held_D(W['Gh'](f), t, xxh):.3f}")
        if name in ("reuse", "extend"):
            gl = Dc.globalize(G(f), f, xx, t, jax.random.PRNGKey(11), STEPS, LR); log(f"  budget of {Dc.TH['multistarts']} multistarts: F {gl['F0']:.3e} -> {gl['F_best']:.3e} ({100 * (1 - gl['F_best'] / gl['F0']):.1f} percent)")
            cg = Dc.candidate_geometry(G, f, t, {n: c["geom"] for n, c in CANDS.items()}, gg, None)
            log("  candidates eta p1/p3/p12/full (dim): " + ", ".join(f"{n} {c['eta'][1]:.2f}/{c['eta'][3]:.2f}/{c['eta'][12]:.2f}/{c['eta_full']:.2f} ({c['dim']})" for n, c in cg.items()))
            for a, b in PAIRS + (("wv@0", "wo@0"), ("w1@1", "w2@1")):
                pg = Dc.pair_geometry(cg[a], cg[b])
                log(f"  pair {a}|{b}: " + " ".join(f"p{p} mu {v['mu']:.2f} d {v['d']:.2f}" for p, v in pg["p"].items()) + f" | full containment {pg['c_ij']:.2f}/{pg['c_ji']:.2f} align {pg['align']:.3f}")
            for n in ("wv@0", "wo@0", "w2@1", "w1@1", "out_bias", "fallback"):
                cf = FALLBACK if n == "fallback" else CANDS[n]["fit"]; th, Fv, Dh = Dc.joint_fit(G, W["Gh"], f, t, cf, xx, xxh, jax.random.PRNGKey(12), STEPS, LR)
                log(f"  joint fit with {n} ({M.family_size(cf)} params added): D_train {float(np.sqrt(2 * Fv) / np.linalg.norm(np.asarray(xx))):.3f} D_held {Dh:.3f}")
    for mag in (0.01, 0.03, 0.1, 0.3):
        _, f, t, xx, _, _ = build_case("extend", W, jax.random.PRNGKey(6), cfg, mag=mag); gg = Dc.geometry(G(f), xx, t)
        log(f"extend at {mag} of the scale, fitted: D {gg['D']:.3f} (base to target {float(jnp.linalg.norm(xx - base) / jnp.linalg.norm(xx)):.3f})")


def pilot2(seed):
    """The second declared pilot block: the corrected collinear construction (A held, B fitted) at three
    tolerances, and whether a budget of multistarts beats a student that is itself the best of restarts."""
    W = world(seed); G = W["G"]; cfg = dict(plant_scale=1.0, refine_fracs=(0.05, 0.15), collinear_eps=1e-6, noise_case_level=0.5, student_restarts=1)
    for eps in (1e-4, 1e-6, 1e-8):
        cfg["collinear_eps"] = eps; _, f4, t4, x4, _, _ = build_case("collinear", W, jax.random.PRNGKey(3), cfg); g4 = Dc.geometry(G(f4), x4, t4)
        log(f"collinear rank-4, A rows equal to {eps:g}, B fitted: D {g4['D']:.3f} s {g4['stat']:.2e} gamma {g4['gamma']:.2e} kappa {g4['kappa']:.1e} rank {g4['rank']}/{g4['n_theta']} lam_min {g4['lam_min']:.1e}")
    for restarts in (1, 4):
        cfg["student_restarts"] = restarts
        for name, k in (("reuse", 4), ("extend", 6)):
            _, f, t, xx, xxh, _ = build_case(name, W, jax.random.PRNGKey(k), cfg); gg = Dc.geometry(G(f), xx, t)
            gl = Dc.globalize(G(f), f, xx, t, jax.random.PRNGKey(11), STEPS, LR)
            log(f"{name}, student = best of {restarts}: D {gg['D']:.3f} s {gg['stat']:.2e} lam_min {gg['lam_min']:.2e} |H| {gg['hnorm']:.2e}; budget F {gl['F0']:.3e} -> {gl['F_best']:.3e} ({100 * (1 - gl['F_best'] / gl['F0']):.1f} percent)")


def pilot3(seed):
    """The third declared pilot block: the joint full fits (section 13) on the reuse and extend cases."""
    W = world(seed); G = W["G"]; cfg = dict(plant_scale=1.0, refine_fracs=(0.05, 0.10), collinear_eps=1e-6, noise_case_level=0.5, student_restarts=4)
    for name, k in (("reuse", 4), ("extend", 6), ("noise", 8)):
        _, f, t, xx, xxh, _ = build_case(name, W, jax.random.PRNGKey(k), cfg); gg = Dc.geometry(G(f), xx, t)
        log(f"{name}: D {gg['D']:.3f} s {gg['stat']:.2e} D_held {Dc.held_D(W['Gh'](f), t, xxh):.3f}")
        for n in ("wv@0", "wo@0", "w2@1", "w1@1", "out_bias", "fallback"):
            cf = FALLBACK if n == "fallback" else CANDS[n]["fit"]; th, Fv, Dh = Dc.joint_fit(G, W["Gh"], f, t, cf, xx, xxh, jax.random.PRNGKey(12), STEPS, LR)
            log(f"  joint fit with {n} ({M.family_size(cf)} params added): D_train {float(np.sqrt(2 * Fv) / np.linalg.norm(np.asarray(xx))):.3f} D_held {Dh:.3f}")


def arm(name, seed):
    cfg = json.load(open(OUT / "config.json")); Dc.TH.update(cfg["thresholds"]); W = world(seed); T0 = time.time(); out = dict(arm=name, seed=seed, rows=[], pairs=[], sweeps=[])
    if name == "sweeps":
        for noise in cfg["noise_levels"]:
            for i, case in enumerate(("refine_early", "reuse", "extend", "adequate")):
                rec = run_case(case, W, jax.random.PRNGKey(2000 + i), cfg, None, noise=noise); out["sweeps"].append(dict(kind="noise", level=noise, **{k: rec[k] for k in ("case", "truth", "got", "correct", "D", "D_held", "stat", "tau", "first_stage")}))
                log(f"noise {noise:<5} " + fmt(rec) + f" [{time.time() - T0:.0f}s]")
        for mag in cfg["misspec_levels"]:
            rec = run_case("extend", W, jax.random.PRNGKey(3000), cfg, None, mag=mag)
            truth = "STOP" if rec["D"] <= Dc.TH["D_max"] else "EXPAND:w2@1"; rec["truth"] = truth; rec["correct"] = correct(rec["got"], truth)
            out["sweeps"].append(dict(kind="misspec", level=mag, **{k: rec[k] for k in ("case", "truth", "got", "correct", "D", "D_held", "stat", "tau", "first_stage")}))
            log(f"misspec {mag:<5} " + fmt(rec) + f" [{time.time() - T0:.0f}s]")
    else:
        abl = None if name == "full" else name
        for i, case in enumerate(CASES):
            rec = run_case(case, W, jax.random.PRNGKey(1000 + i), cfg, abl); out["rows"].append(rec); log(fmt(rec) + f" [{time.time() - T0:.0f}s]")
        for pair in PAIRS:
            pr = pair_case(W, jax.random.PRNGKey(1005), cfg, pair, abl); pr["abl"] = name; out["pairs"].append(pr)
            log(f"{name:<6} pair {pair[0]}|{pair[1]}: {'COLLAPSE' if pr['collapse'] else 'KEEP DISTINCT'} (matched-p rule {'COLLAPSE' if pr['collapse_matched'] else 'KEEP DISTINCT'}) align {pr['geometry']['align']:.3f} [{time.time() - T0:.0f}s]")
    out["seconds"] = time.time() - T0
    json.dump(out, open(OUT / f"arm_{name}.json", "w"), indent=1, default=lambda o: float(o) if isinstance(o, (np.floating, np.integer)) else str(o))
    log(f"done arm {name} in {out['seconds']:.0f}s")


def merge():
    arms = {p.stem[4:]: json.load(open(p)) for p in sorted(OUT.glob("arm_*.json"))}
    rows = [r for a in arms.values() for r in a["rows"]]; pairs = [p for a in arms.values() for p in a["pairs"]]; sweeps = [s for a in arms.values() for s in a["sweeps"]]
    json.dump(dict(arms=list(arms), rows=rows, pairs=pairs, sweeps=sweeps, seconds={k: a["seconds"] for k, a in arms.items()}), open(OUT / "ed1.json", "w"), indent=1)
    with open(OUT / "per_case_metrics.csv", "w", newline="") as f:
        w = csv.writer(f); w.writerow(["arm", "case", "truth", "got", "correct", "D", "D_held", "stat", "tau", "gamma", "kappa", "lam_min", "hnorm", "first_stage", "glob_improvement", "beam", "collapsed", "fits_run"])
        for r in rows: w.writerow([r["abl"], r["case"], r["truth"], r["got"], r["correct"], r["D"], r["D_held"], r["stat"], r["tau"], r["gamma"], r["kappa"], r["lam_min"], r["hnorm"], r["first_stage"], r.get("glob_improvement", ""), " ".join(r.get("beam", [])), " ".join(r.get("collapsed", [])), r["fits_run"]])
    with open(OUT / "equivalence_summary.csv", "w", newline="") as f:
        w = csv.writer(f); w.writerow(["arm", "pair", "truth_collapse", "collapse", "collapse_matched", "align", "c_ij", "c_ji"] + [f"p{p}_{k}" for p in Dc.TH["p_set"] for k in ("mu", "d")])
        for p in pairs:
            g = p["geometry"]; w.writerow([p["abl"], "|".join(p["pair"]), p["truth"], p["collapse"], p["collapse_matched"], g["align"], g["c_ij"], g["c_ji"]] + [g["p"].get(str(q), g["p"].get(q, {})).get(k, "") for q in Dc.TH["p_set"] for k in ("mu", "d")])
    if sweeps:
        with open(OUT / "sweeps.csv", "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(sweeps[0])); w.writeheader(); w.writerows(sweeps)
    log(f"merged {len(arms)} arms: {len(rows)} case rows, {len(pairs)} pair rows, {len(sweeps)} sweep rows")


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[0] == "pilot": pilot(int(a[1]) if len(a) > 1 else 0)
    elif a[0] == "pilot2": pilot2(int(a[1]) if len(a) > 1 else 0)
    elif a[0] == "pilot3": pilot3(int(a[1]) if len(a) > 1 else 0)
    elif a[0] == "arm": arm(a[1], int(a[2]) if len(a) > 2 else 1)
    elif a[0] == "merge": merge()
    else: raise SystemExit(__doc__)
