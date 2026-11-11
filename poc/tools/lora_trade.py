#!/usr/bin/env python3
"""The trade the stopping rule is for: spend every training context on training and stop at the cross-fitted
knee g*, or hold some of them out and stop where the held-out loss is lowest (docs/prescreen-theory.md,
section 14, "What the rule has not been tested against").

  python lora_trade.py run CONFIG.json OUT_DIR      fits, one checkpoint per condition
  python lora_trade.py score OUT_DIR                the comparison, from OUT_DIR/rows.json

Per condition and target matrix (fits from poc/tools/lora_knee.py, same LoRA, optimiser and corpus draws):
- the rule: a full fit on all n training contexts, recorded on the test contexts, and the condition's eight
  half-fits; g* is their median knee, and the rule's test gain is the full fit's at training gain g*;
- for each held-out split in the config ("k" folds, the folds listed in "folds"): a fit on the n - n/k other
  contexts, watching the fold, recorded on the test contexts; its test gain is taken where the fold's loss is
  lowest. Two refits are read off the full fit's curve with no new training: at the same step, and at the same
  training gain, as the split's fit had at its held-out minimum.
The test contexts are never used to stop anything. The extra validation set that corpus3 draws (n_val) is
used only for a reference arm (stop at its minimum), which is not a trade: it is extra data.
"""
from __future__ import annotations
import json, sys, time
from pathlib import Path
import numpy as np, torch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lora_knee as LK


def at_gain(tj, g):
    """Test gain of a recorded fit where its training gain first reaches g (linear between records); the last
    record's if it never does."""
    gt = tj["tr"][0] - np.array(tj["tr"]); ge = tj["te"][0] - np.array(tj["te"])
    if not (gt >= g).any(): return float(ge[-1]), False
    i = int(np.argmax(gt >= g))
    if i == 0: return 0.0, True
    w = (g - gt[i - 1]) / (gt[i] - gt[i - 1]); return float(ge[i - 1] + w * (ge[i] - ge[i - 1])), True


def at_step(tj, s):
    ge = tj["te"][0] - np.array(tj["te"]); st = np.array(tj["step"])
    return float(np.interp(s, st, ge)), bool(s <= st[-1])


def holdout_fits(model, c, cfg, tr, te, st, save):
    T = lambda a: torch.tensor(np.asarray(a), dtype=torch.long); n = c["n"]
    for i, m in enumerate(c["targets"]):
        for sp in cfg["splits"]:
            v = n // sp["k"]
            for j in sp["folds"]:
                tag = f"{sp['name']} fold {j} {m}"
                if tag in st["hold"]: continue
                idx = np.arange(n); val = idx[j * v:(j + 1) * v]; rest = np.setdiff1d(idx, val)
                t = time.time(); tj = LK.long_fit(model, m, dict(tr=T(tr[rest]), ho=T(tr[val]), te=T(te)), "ho", cfg["lr"], cfg["cap_full"], cfg["rank"],
                                                  seed=c["seed"] * 1000 + 500 + 50 * i + 10 * cfg["splits"].index(sp) + j, drop=0.5)
                st["hold"][tag] = tj; st["seconds"] += time.time() - t; save(); k = int(np.argmin(tj["ho"]))
                LK.log(f"  {c['name']} {tag}: held-out loss lowest at step {tj['step'][k]}, test gain there {tj['te'][0] - tj['te'][k]:+.3f}; ran {tj['step'][-1]} steps, {tj['stopped']} ({time.time() - t:.0f}s)")


def run(cfg_path, out_dir):
    cfg = json.load(open(cfg_path)); out_dir = Path(out_dir); out_dir.mkdir(parents=True, exist_ok=True); torch.set_num_threads(cfg.get("threads", 4)); T0 = time.time()
    cp = out_dir / "config.json"
    if cp.resolve() != Path(cfg_path).resolve():
        assert not cp.exists() or json.load(open(cp)) == cfg, f"{cp} differs from {cfg_path}"
        json.dump(cfg, open(cp, "w"), indent=1)
    texts = LK.docs_text(cfg["repo"], cfg["corpus_commit"]); LK.log(f"corpus: docs/*.md at {cfg['corpus_commit']}, {len(texts)} files"); res = out_dir / "rows.json"
    out = json.load(open(res))["rows"] if res.exists() else []; done = {r["name"] for r in out}; loaded = (None, None, None)
    for c in cfg["conditions"]:
        if c["name"] in done: LK.log(f"  {c['name']}: already done"); continue
        if loaded[0] != c["model"]: loaded = (c["model"], *LK.load_model(cfg["models"][c["model"]])); LK.log(f"model {c['model']}: {sum(p.numel() for p in loaded[1].parameters()) / 1e6:.0f}M parameters")
        model, encode = loaded[1], loaded[2]
        row = LK.condition(model, encode, texts, c, cfg, out_dir / f"{c['name']}.ckpt.json")
        tr, ho, te = LK.corpus3(texts, encode, c["seed"], c["n"], c["n_val"], c["n_test"], c["transform"])
        ck = out_dir / f"{c['name']}.hold.ckpt.json"; st = json.load(open(ck)) if ck.exists() else dict(tokens=row["tokens"], hold={}, seconds=0.0)
        assert st["tokens"] == row["tokens"], f"{ck} was written for other contexts"
        holdout_fits(model, c, cfg, tr, te, st, lambda: json.dump(st, open(ck, "w"), indent=1))
        row["hold"] = st["hold"]; row["seconds"] += st["seconds"]; out.append(row); json.dump(dict(rows=out), open(res, "w"), indent=1); LK.log(f"[{time.time() - T0:.0f}s]")
    LK.log(f"done in {time.time() - T0:.0f}s")


def score(out_dir):
    out_dir = Path(out_dir); rows = json.load(open(out_dir / "rows.json"))["rows"]; cfg = json.load(open(out_dir / "config.json")); recs = []
    for r in rows:
        knees = [tj["tr"][0] - tj["tr"][int(np.argmin(tj["ho"]))] for tj in r["half"].values()]; gstar = float(np.median(knees))
        for m, tj in r["full"].items():
            ge = tj["te"][0] - np.array(tj["te"]); rule, reached = at_gain(tj, gstar)
            rec = dict(cond=r["name"], n=r["cond"]["n"], transform=r["cond"]["transform"], m=m, gstar=gstar, peak=float(ge.max()), rule=rule, reached=reached,
                       extra_val=float(ge[int(np.argmin(tj["ho"]))]))
            for sp in cfg["splits"]:
                fs = [r["hold"][f"{sp['name']} fold {j} {m}"] for j in sp["folds"]]; ks = [int(np.argmin(h["ho"])) for h in fs]
                rec[sp["name"]] = float(np.mean([h["te"][0] - h["te"][k] for h, k in zip(fs, ks)]))
                rec[sp["name"] + "+refit@step"] = float(np.mean([at_step(tj, h["step"][k])[0] for h, k in zip(fs, ks)]))
                rec[sp["name"] + "+refit@gain"] = float(np.mean([at_gain(tj, h["tr"][0] - h["tr"][k])[0] for h, k in zip(fs, ks)]))
            recs.append(rec)
    arms = ["rule"] + [sp["name"] + s for sp in cfg["splits"] for s in ("", "+refit@step", "+refit@gain")] + ["extra_val", "peak"]
    L = ["# The trade: the rule on all n against held-out splits\n", "Test gain in nats on the condition's test contexts; held-out arms averaged over their folds. "
         "`extra_val` stops at the minimum on 32 extra contexts and `peak` is the best the full fit reached; neither is available in the use case.\n",
         "| condition | matrix | g* | " + " | ".join(arms) + " |", "|---|---|---|" + "---|" * len(arms)]
    for x in recs: L.append(f"| {x['cond']} | {x['m']} | {x['gstar']:.2f} | " + " | ".join(f"{x[a]:+.3f}" + ("" if a != "rule" or x["reached"] else " (g* not reached)") for a in arms) + " |")
    L += ["\n| arm | mean test gain | rule minus arm: mean | fits where the rule is ahead |", "|---|---|---|---|"]
    for a in arms:
        d = np.array([x["rule"] - x[a] for x in recs]); L.append(f"| {a} | {np.mean([x[a] for x in recs]):+.3f} | {d.mean():+.3f} | {(d > 0).sum()} of {len(d)} |")
    L += ["\nBy condition, rule minus arm (mean over matrices):\n", "| condition | " + " | ".join(arms[1:-2]) + " |", "|---|" + "---|" * (len(arms) - 3)]
    for c in dict.fromkeys(x["cond"] for x in recs):
        xs = [x for x in recs if x["cond"] == c]; L.append(f"| {c} | " + " | ".join(f"{np.mean([x['rule'] - x[a] for x in xs]):+.3f}" for a in arms[1:-2]) + " |")
    (out_dir / "report.md").write_text("\n".join(L) + "\n"); json.dump(recs, open(out_dir / "scores.json", "w"), indent=1); print("\n".join(L))


if __name__ == "__main__":
    if len(sys.argv) == 4 and sys.argv[1] == "run": run(sys.argv[2], sys.argv[3])
    elif len(sys.argv) == 3 and sys.argv[1] == "score": score(sys.argv[2])
    else: print(__doc__)
