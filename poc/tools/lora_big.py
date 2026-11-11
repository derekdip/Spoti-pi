#!/usr/bin/env python3
"""Larger adapters: the knee and the stopping rule for LoRAs of rank r on one matrix or on many at once (ED9).

  python lora_big.py run CONFIG.json OUT_DIR      fits, one checkpoint per condition
  python lora_big.py score OUT_DIR                the knees and the rule, from OUT_DIR/rows.json

An adapter in the config is {"targets": [MODULE, ...] | "all", "rank": r, optional "lr" and "seg"}; "all" is every 2-D weight of every
transformer block (for GPT-2: attn.c_attn, attn.c_proj, mlp.c_fc, mlp.c_proj of each layer, 48 matrices). Each
target gets its own rank-r LoRA (lora_knee.Lora: A at 0.02, B zero, no scaling), all trained together by one
Adam. Per condition and adapter: a full fit on the training contexts recording the test and validation
contexts, and two half-fits, each on one half watching the other; the same stopping of a recorded fit as
lora_knee.py, with the evaluation interval `seg` from the config (larger adapters turn in fewer steps).
Corpus draws, contexts and checkpoints as lora_knee.py; lora_knee.py itself is unchanged.
"""
from __future__ import annotations
import json, re, sys, time
from pathlib import Path
import numpy as np, torch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lora_knee as LK


def expand(model, targets):
    if targets != "all": return list(targets)
    out = []
    for n, m in model.named_modules():
        if re.fullmatch(r"(transformer\.h|model\.layers)\.\d+\.(attn|self_attn|mlp)\.[a-z_]+", n) and getattr(m, "weight", None) is not None and m.weight.dim() == 2: out.append(n)
    return out


def long_fit(model, targets, rank, data, watch, lr, cap, seed, seg, patience=5, drop=0.25):
    los = [LK.Lora(model, t, rank, seed + 7919 * i) for i, t in enumerate(targets)]
    opt = torch.optim.Adam([p for lo in los for p in (lo.A, lo.B)], lr=lr)
    inst = lambda: [lo.install() for lo in los]
    def losses():
        inst()
        with torch.no_grad(): return {s: float(LK.ce(model, t)) for s, t in data.items()}
    try:
        base = losses(); out = dict(step=[0], norm=[0.0], stopped="cap", **{s: [v] for s, v in base.items()}); peak, kpeak = -np.inf, 0
        for k in range(cap // seg):
            for _ in range(seg): inst(); opt.zero_grad(); LK.ce(model, data["tr"]).backward(); opt.step()
            cur = losses(); out["step"].append((k + 1) * seg); out["norm"].append(float(np.sqrt(sum(lo.norm() ** 2 for lo in los))))
            for s, v in cur.items(): out[s].append(v)
            g = base[watch] - cur[watch]
            if g > peak: peak, kpeak = g, k
            if k - kpeak >= patience and g <= drop * peak: out["stopped"] = "turned"; break
    finally:
        for lo in los: lo.restore()
    return out


def condition(model, encode, texts, c, cfg, ckpt):
    tr, ho, te = LK.corpus3(texts, encode, c["seed"], c["n"], c["n_val"], c["n_test"], c["transform"]); h = c["n"] // 2; tokens = LK.fingerprint(tr, ho, te)
    T = lambda a: torch.tensor(np.asarray(a), dtype=torch.long)
    st = json.load(open(ckpt)) if Path(ckpt).exists() else dict(tokens=tokens, full={}, half={}, seconds=0.0); assert st["tokens"] == tokens, f"{ckpt} was written for other contexts"
    save = lambda: json.dump(st, open(ckpt, "w"), indent=1)
    for i, name in enumerate(c["adapters"]):
        ad = cfg["adapters"][name]; tg = expand(model, ad["targets"]); r = ad["rank"]; seg = ad.get("seg", cfg.get("seg", 10)); lr = ad.get("lr", cfg["lr"])
        if name not in st["full"]:
            t = time.time(); tj = long_fit(model, tg, r, dict(tr=T(tr), ho=T(ho), te=T(te)), "te", lr, cfg["cap_full"], c["seed"] * 1000 + i, seg); tj["n_targets"] = len(tg); tj["params"] = int(sum(r * (sum(model.get_submodule(re.sub(r"\[.*", "", x)).weight.shape)) for x in tg))
            st["full"][name] = tj; st["seconds"] += time.time() - t; save(); kn = LK.knee(tj, "te")
            LK.log(f"  {c['name']} full {name} ({len(tg)} matrices, rank {r}): test gain peaks at step {kn['step']} ({kn['gain']:+.3f}) at training gain {kn['train_gain']:.2f}; ran {tj['step'][-1]} steps, {tj['stopped']}; at the end {tj['te'][0] - tj['te'][-1]:+.3f} ({time.time() - t:.0f}s)")
        for j, (hn, A, B) in enumerate((("A to B", tr[:h], tr[h:2 * h]), ("B to A", tr[h:2 * h], tr[:h]))):
            tag = f"{hn} {name}"
            if tag in st["half"]: continue
            t = time.time(); tj = long_fit(model, tg, r, dict(tr=T(A), ho=T(B)), "ho", lr, cfg["cap_half"], c["seed"] * 1000 + 100 + 10 * i + j, seg, drop=0.5)
            st["half"][tag] = tj; st["seconds"] += time.time() - t; save(); kn = LK.knee(tj, "ho")
            LK.log(f"  {c['name']} half {tag}: the other half's loss is lowest at step {kn['step']} ({kn['gain']:+.3f}) at training gain {kn['train_gain']:.2f}; ran {tj['step'][-1]} steps, {tj['stopped']} ({time.time() - t:.0f}s)")
    return dict(name=c["name"], cond=c, tokens=tokens, full=st["full"], half=st["half"], seconds=st["seconds"])


def run(cfg_path, out_dir):
    cfg = json.load(open(cfg_path)); out_dir = Path(out_dir); out_dir.mkdir(parents=True, exist_ok=True); torch.set_num_threads(cfg.get("threads", 4)); T0 = time.time()
    cp = out_dir / "config.json"
    if cp.resolve() != Path(cfg_path).resolve():
        assert not cp.exists() or json.load(open(cp)) == cfg, f"{cp} differs from {cfg_path}"
        json.dump(cfg, open(cp, "w"), indent=1)
    texts = LK.docs_text(cfg["repo"], cfg["corpus_commit"]); LK.log(f"corpus: docs/*.md at {cfg['corpus_commit']}, {len(texts)} files"); res = out_dir / "rows.json"
    out = json.load(open(res))["rows"] if res.exists() else []; done = {r["name"] for r in out}; model = encode = None
    for c in cfg["conditions"]:
        if c["name"] in done: LK.log(f"  {c['name']}: already done"); continue
        if model is None: model, encode = LK.load_model(cfg["model"]); LK.log(f"model: {sum(p.numel() for p in model.parameters()) / 1e6:.0f}M parameters")
        out.append(condition(model, encode, texts, c, cfg, out_dir / f"{c['name']}.ckpt.json")); json.dump(dict(rows=out), open(res, "w"), indent=1); LK.log(f"[{time.time() - T0:.0f}s]")
    LK.log(f"done in {time.time() - T0:.0f}s")


def kept(tj, g):
    gt = tj["tr"][0] - np.array(tj["tr"]); ge = tj["te"][0] - np.array(tj["te"]); pk = ge.max()
    if not (gt >= g).any(): return float(ge[-1] / pk), False
    i = int(np.argmax(gt >= g))
    if i == 0: return 0.0, True
    w = (g - gt[i - 1]) / (gt[i] - gt[i - 1]); return float((ge[i - 1] + w * (ge[i] - ge[i - 1])) / pk), True


def score(out_dir):
    out_dir = Path(out_dir); rows = json.load(open(out_dir / "rows.json"))["rows"]; recs = []
    L = ["# Larger adapters: the knee and the rule\n", "| condition | adapter | matrices | trainable | peak test gain (step) | training gain at the peak | own g* | kept at own g* | kept at the shared g* | kept at the validation minimum | at the last step |", "|" + "---|" * 11]
    for r in rows:
        hk = {k: tj["tr"][0] - tj["tr"][int(np.argmin(tj["ho"]))] for k, tj in r["half"].items()}; shared = float(np.median(list(hk.values())))
        for name, tj in r["full"].items():
            ge = tj["te"][0] - np.array(tj["te"]); k = int(np.argmax(ge)); own = float(np.mean([v for kk, v in hk.items() if kk.endswith(" " + name)]))
            x = dict(cond=r["name"], adapter=name, n_targets=tj.get("n_targets"), params=tj.get("params"), peak=float(ge[k]), peak_step=tj["step"][k], knee=float(tj["tr"][0] - tj["tr"][k]),
                     own=own, shared=shared, kept_own=kept(tj, own)[0], kept_shared=kept(tj, shared)[0], val=float(ge[int(np.argmin(tj["ho"]))] / ge[k]), last=float(ge[-1]), turned=tj["stopped"] == "turned")
            recs.append(x)
            L.append(f"| {x['cond']} | {name} | {x['n_targets']} | {x['params']} | {x['peak']:+.3f} ({x['peak_step']}) | {x['knee']:.2f} | {own:.2f} | {x['kept_own']:.2f} | {x['kept_shared']:.2f} | {x['val']:.2f} | {x['last']:+.2f} |")
        L.append(f"| {r['name']} | shared g* (median of all half-fits) | | | | | {shared:.2f} | | | | |")
    cfg = json.load(open(out_dir / "config.json")); B = cfg.get("bars")
    if B:
        grp = {n: a["group"] for n, a in cfg["adapters"].items()}; cv = lambda v: float(np.std(v) / np.mean(v)); conds = list(dict.fromkeys(x["cond"] for x in recs)); L.append("\n## Bars (docs/math-track-ed9-prereg.md)\n")
        b1 = []; b2 = []
        for c in conds:
            k = {g: [x["knee"] for x in recs if x["cond"] == c and grp[x["adapter"]] == g] for g in ("one", "all")}
            b1 += [cv(k["one"]), cv(k["all"])]; b2.append(float(np.mean(k["all"]) / np.mean(k["one"])))
            L.append(f"- {c}: knee, one matrix {np.mean(k['one']):.2f} (c.v. {cv(k['one']):.2f}); all matrices {np.mean(k['all']):.2f} (c.v. {cv(k['all']):.2f}); ratio {b2[-1]:.2f}")
        n = len(recs); need = int(np.ceil(B["keep_share"] * n))
        for key, lab in (("kept_own", "own"), ("kept_shared", "shared")):
            pos = sum(x[key] > 0 for x in recs); ok = sum(x[key] >= B["keep"] for x in recs)
            L.append(f"- **{'R1' if lab == 'own' else 'R2'}**, stopped at the {lab} g*: positive in {pos} of {n} (needs all), at least {B['keep']:.0%} of the peak in {ok} (needs {need}): **{'holds' if pos == n and ok >= need else 'fails'}**")
        L.append(f"- **B1**, rank does not move the knee within a reach: largest c.v. {max(b1):.2f} (needs below {B['cv_max']}): **{'holds' if max(b1) < B['cv_max'] else 'fails'}**")
        L.append(f"- **B2**, reach moves it: smallest ratio of the all-matrix to the one-matrix knee {min(b2):.2f} (needs above {B['ratio_min']}): **{'holds' if min(b2) > B['ratio_min'] else 'fails'}**")
        L.append(f"- Reported: share of the peak kept, mean, own g* {np.mean([x['kept_own'] for x in recs]):.2f}, shared g* {np.mean([x['kept_shared'] for x in recs]):.2f}, validation minimum {np.mean([x['val'] for x in recs]):.2f}; fits that turned {sum(x['turned'] for x in recs)} of {n}.")
    (out_dir / "report.md").write_text("\n".join(L) + "\n"); json.dump(recs, open(out_dir / "scores.json", "w"), indent=1); print("\n".join(L))


if __name__ == "__main__":
    if len(sys.argv) == 4 and sys.argv[1] == "run": run(sys.argv[2], sys.argv[3])
    elif len(sys.argv) == 3 and sys.argv[1] == "score": score(sys.argv[2])
    else: print(__doc__)
