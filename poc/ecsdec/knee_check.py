"""The knee: where a LoRA fit's gain on fresh text turns, in units of training gain (docs/prescreen-theory.md,
sections 11 and 12). Exploratory, beside ED4; it imports the frozen prescreen module and changes nothing in it.

  /usr/bin/python3 -m poc.ecsdec.knee_check      -> poc/results/ed4/knee_check.json and a table

Background, from the eight long fits of the ED4 pilot (plain text, 8 contexts, pilot3.json). Along a fit the test
gain rises with the training gain at a roughly constant rate, close to the pre-screen's real share, and then
turns. The training gain at the turn is nearly the same for every matrix (mean 1.29 nats, coefficient of
variation 0.22) although the step at which it is reached is not (50 to 110, c.v. 0.33) and the adapter's norm
there is not (c.v. 0.54). If the turn belongs to the data and not to the matrix, it can be found once, without
held-out text, by cross-fitting: fit on one half of the training contexts, watch the loss on the other half,
note the training gain at which that loss is lowest.

Written before the run:
  K1. Cross-fitted on the pilot's sample (halves of 4 contexts, four matrices, both ways round), the training
      gain at the turn of the other half's loss has a coefficient of variation below 0.35 across the eight
      half-fits, while its step differs by a factor of 2 or more between the MLP and the attention matrices.
  K2. Stopping each of the pilot's eight full fits when its training gain first reaches g*, the median of those
      eight cross-fitted values, leaves a positive test gain in 8 of 8 and at least two thirds of the peak test
      gain in at least 6 of 8. (A half-sample turns earlier, so the rule should stop early, not late.)
  K3. On the 16 long fits of ED4's scored run (other contexts, leet and plain text), which have not been looked
      at in these terms: the training gain at the test peak has a c.v. below 0.35 within each condition; and
      across the 16 the test gain over the training gain in the first 30 steps has a rank correlation above
      0.5 with the pre-screen's real share rho.
"""
from __future__ import annotations
import json, sys, time, hashlib
from pathlib import Path
import numpy as np, jax, jax.numpy as jnp
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from poc.ecsdec import gpt2 as GM
from poc.ecsdec import prescreen as PS

OUT = PS.OUT; log = PS.log; cv = lambda v: float(np.std(v) / np.mean(v)); rk = lambda a: np.argsort(np.argsort(np.asarray(a, float)))


def peak_stats(base, tj, ev):
    gt = base["tr"] - np.array(tj["tr"]); ge = base[ev] - np.array(tj[ev]); k = int(np.argmax(ge))
    return dict(peak_step=tj["step"][k], gt_peak=float(gt[k]), ge_peak=float(ge[k]), early=float(np.mean([ge[i] / gt[i] for i in (1, 2, 3)])), gt=gt, ge=ge)


def main(steps=150):
    pilot = json.load(open(OUT / "pilot3.json"))[0]; ck = json.load(open(OUT / "pilot3_stop-none-8.ckpt.json"))
    PS.CORPUS_COMMIT = "73b70e427570835c249b7948bf8cd6b4baf7f986"; P = GM.load_params(); tok = GM.tokenizer(); tr, ho, te = PS.corpus3(0, 8, 96, 96, tok, "none")
    X = lambda a: jnp.asarray(a[:, :PS.CTX]); Y = lambda a: jnp.asarray(a[:, 1:PS.CTX + 1])
    same = hashlib.sha1(b"".join(np.asarray(X(a)).tobytes() + np.asarray(Y(a)).tobytes() for a in (tr, ho, te))).hexdigest() == ck["tokens"]; log(f"the pilot's contexts reproduced: {same}"); assert same
    mods = ["proj@2", "proj@8", "v@2", "o@8"]; halves = [("A to B", tr[:4], tr[4:]), ("B to A", tr[4:], tr[:4])]; W = PS.CEWorld(P, halves[0][1], halves[0][2], library=mods, te=te); rows = []
    for name, A, B in halves:
        W.x["tr"], W.y["tr"], W.x["ho"], W.y["ho"] = X(A), Y(A), X(B), Y(B)
        for s_ in ("tr", "ho"): W.L0[s_] = float(PS._ce(W._logits(P, W.x[s_]), W.y[s_]))
        for i, m in enumerate(mods):
            t = time.time(); tj = W.fit_traj(m, jax.random.fold_in(jax.random.PRNGKey(7), i), 1e-3, steps); k = int(np.argmin(tj["ho"])); kt = int(np.argmin(tj["te"]))
            rows.append(dict(half=name, module=m, base=dict(W.L0), traj=tj, knee_step=tj["step"][k], knee_gain=W.L0["tr"] - tj["tr"][k], other_gain=W.L0["ho"] - tj["ho"][k], test_peak_step=tj["step"][kt], test_peak_train_gain=W.L0["tr"] - tj["tr"][kt]))
            log(f"{name} {m}: the other half's loss is lowest at step {tj['step'][k]}, training gain {rows[-1]['knee_gain']:.2f} (other-half gain {rows[-1]['other_gain']:+.2f}); the test loss is lowest at step {tj['step'][kt]}, training gain {rows[-1]['test_peak_train_gain']:.2f} ({time.time() - t:.0f}s)")
            json.dump(rows, open(OUT / "knee_check.json", "w"), indent=1, default=float)
    g = np.array([r["knee_gain"] for r in rows]); st = {m: np.mean([r["knee_step"] for r in rows if r["module"] == m]) for m in mods}; gstar = float(np.median(g))
    log(f"K1: cross-fitted training gain at the turn: {' '.join(f'{v:.2f}' for v in g)}; c.v. {cv(g):.2f} (needs below 0.35); mean step of the turn: " + ", ".join(f"{m} {st[m]:.0f}" for m in mods) +
        f"; slowest over fastest {max(st.values()) / max(min(st.values()), 1e-9):.1f} (needs 2 or more, MLP against attention)")
    kept = []
    for m, tj in pilot["traj"].items():
        s = peak_stats(pilot["base"], tj, "te"); i = int(np.argmax(s["gt"] >= gstar)) if (s["gt"] >= gstar).any() else len(s["gt"]) - 1
        if i > 0 and s["gt"][i] > s["gt"][i - 1]: w = (gstar - s["gt"][i - 1]) / (s["gt"][i] - s["gt"][i - 1]); ge = s["ge"][i - 1] + w * (s["ge"][i] - s["ge"][i - 1]); step = tj["step"][i - 1] + w * (tj["step"][i] - tj["step"][i - 1])
        else: ge = s["ge"][i]; step = tj["step"][i]
        kept.append(ge / s["ge_peak"]); log(f"   pilot full fit {m}: stopped at training gain g* = {gstar:.2f} (step {step:.0f}): test gain {ge:+.3f}, {ge / s['ge_peak']:.2f} of its peak {s['ge_peak']:+.3f} (peak at step {s['peak_step']}, training gain {s['gt_peak']:.2f})")
    kept = np.array(kept); log(f"K2: g* = {gstar:.2f}; test gain positive in {int((kept > 0).sum())}/8 (needs 8); at least two thirds of the peak in {int((kept >= 2 / 3).sum())}/8 (needs 6); median share of the peak {np.median(kept):.2f}")
    scored = [r for r in json.load(open(OUT / "ed4.json"))["rows"] if r.get("kind") == "stopping"]; early, rho = [], []
    for r in scored:
        ss = {m: peak_stats(r["base"], tj, "te") for m, tj in r["traj"].items()}; gp = np.array([s["gt_peak"] for s in ss.values()]); early += [s["early"] for s in ss.values()]; rho += [r["scores"][m]["rho"] for m in ss]
        log(f"K3: {r['name']}: training gain at the test peak {' '.join(f'{v:.2f}' for v in gp)}; mean {gp.mean():.2f}, c.v. {cv(gp):.2f} (needs below 0.35); peak steps {' '.join(str(s['peak_step']) for s in ss.values())}, c.v. {cv(np.array([s['peak_step'] for s in ss.values()], float)):.2f}")
    log(f"K3: over the {len(rho)} scored long fits, rank correlation of the early test-over-training gain with rho: {np.corrcoef(rk(early), rk(rho))[0, 1]:+.2f} (needs above 0.5); pairs (rho, early): " + " ".join(f"({a:.2f}, {b:.2f})" for a, b in zip(rho, early)))
    log("knee check done")


if __name__ == "__main__":
    main()
