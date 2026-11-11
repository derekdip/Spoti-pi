#!/usr/bin/env python3
"""Long LoRA fits and the cross-fitted knee, in PyTorch, for any causal language model the transformers library
loads (docs/prescreen-theory.md, sections 12 and 13; the JAX original is poc/ecsdec/knee.py).

  python lora_knee.py run CONFIG.json OUT_DIR      runs the conditions of CONFIG, one checkpoint per condition

A fit puts a rank-r LoRA on one weight matrix and trains it with Adam on the next-token loss of the training
contexts, recording the loss on every set of contexts each `seg` steps, until the watched gain has turned or a
cap. Per condition: a full fit per target on all the training contexts (watching the test contexts, validation
recorded too) and two half-fits per target, each on one half of the training contexts watching the other half.
The knee of a fit is its training gain where the watched loss is lowest; g* is the median of the half-fits'
knees; the rule stops a full fit when its training gain first reaches g*. Rows are written in the format
poc/ecsdec/score5.py reads.

A target is "MODULE" or "MODULE[a:b]" (a column block of the module's weight, e.g. the value block of GPT-2's
c_attn); the module must have a 2-D `weight` (transformers' Conv1D, in x out, or torch.nn.Linear, out x in).
"""
from __future__ import annotations
import hashlib, json, re, subprocess, sys, time
from pathlib import Path
import numpy as np, torch

CTX = 16
_LEET = str.maketrans("aeiostAEIOST", "431057431057")
TRANSFORMS = {"none": lambda t: t, "leet": lambda t: t.translate(_LEET)}
log = lambda m: print(f"[{time.strftime('%H:%M:%S')}] {m}", flush=True)


def docs_text(root, commit):
    """The texts of docs/*.md at a commit of the repository at `root`, in name order."""
    git = lambda *a: subprocess.run(["git", "-C", str(root), *a], check=True, capture_output=True, text=True).stdout
    return [git("show", f"{commit}:{p}") for p in sorted(x for x in git("ls-tree", "--name-only", commit, "docs/").split("\n") if x.endswith(".md"))]


def corpus3(texts, encode, seed, n, n_val, n_test, transform):
    """Training, validation and test windows of CTX + 1 tokens from three disjoint sets of files (the same
    draws as poc/ecsdec/prescreen.py: corpus3, so the same tokenizer gives the same windows)."""
    rng = np.random.default_rng(seed); f = TRANSFORMS[transform]
    def draw(ts, k):
        toks = [np.array(encode(f(t))) for t in ts]; out = []
        while len(out) < k:
            t = toks[rng.integers(len(toks))]
            if len(t) < CTX + 2: continue
            i = rng.integers(0, len(t) - CTX - 1); out.append(t[i:i + CTX + 1])
        return np.stack(out)
    return draw(texts[::2], n), draw(texts[1::4], n_val), draw(texts[3::4], n_test)


def fingerprint(*sets):
    """The hash poc/ecsdec uses for a condition's contexts (inputs then targets of each set, int32)."""
    return hashlib.sha1(b"".join(np.asarray(a[:, :CTX], np.int32).tobytes() + np.asarray(a[:, 1:CTX + 1], np.int32).tobytes() for a in sets)).hexdigest()


def load_model(spec):
    """A causal LM and its tokenizer's encode from a local directory: config.json, pytorch_model.bin, vocab.json,
    merges.txt. spec = dict(dir=..., kind="gpt2" | "openai-gpt")."""
    import transformers
    transformers.logging.set_verbosity_error(); d = spec["dir"]
    if spec["kind"] == "gpt2":
        model = transformers.GPT2LMHeadModel(transformers.GPT2Config.from_json_file(d + "/config.json")); tok = transformers.GPT2Tokenizer(d + "/vocab.json", d + "/merges.txt")
    else:
        model = transformers.OpenAIGPTLMHeadModel(transformers.OpenAIGPTConfig.from_json_file(d + "/config.json")); tok = transformers.OpenAIGPTTokenizer(d + "/vocab.json", d + "/merges.txt")
    sd = torch.load(d + "/pytorch_model.bin", map_location="cpu", weights_only=True)
    res = (model if any(k.startswith("transformer.") for k in sd) else model.transformer).load_state_dict(sd, strict=False); model.tie_weights(); model.eval()
    missing = [k for k in res.missing_keys if not re.search(r"(attn\.bias|masked_bias|lm_head\.weight|position_ids)$", k)]; assert not missing, f"weights missing: {missing[:5]}"
    for p in model.parameters(): p.requires_grad_(False)
    return model, (lambda text: tok.encode(text))


class Lora:
    """A rank-r LoRA on one weight matrix (or a column block of it), installed by replacing the module's weight
    with a tensor recomputed from the factors; restore() puts the parameter back."""
    def __init__(self, model, target, rank, seed):
        m = re.fullmatch(r"(.+?)(?:\[(\d+):(\d+)\])?", target); self.mod = model.get_submodule(m.group(1)); W = self.mod.weight
        self.linear = isinstance(self.mod, torch.nn.Linear); self.W0 = W.detach().clone(); n_in, n_out = (W.shape[1], W.shape[0]) if self.linear else W.shape
        self.cols = (int(m.group(2)), int(m.group(3))) if m.group(2) else (0, n_out); g = torch.Generator().manual_seed(seed)
        self.A = (torch.randn(rank, self.cols[1] - self.cols[0], generator=g) * 0.02).requires_grad_(True); self.B = torch.zeros(n_in, rank, requires_grad=True)
        del self.mod._parameters["weight"]; self.n_out = n_out

    def delta(self):
        d = self.B @ self.A
        if self.cols != (0, self.n_out): d = torch.nn.functional.pad(d, (self.cols[0], self.n_out - self.cols[1]))
        return d.T if self.linear else d

    def install(self): self.mod.weight = self.W0 + self.delta()
    def norm(self): return float(torch.linalg.norm(self.B.detach() @ self.A.detach()))
    def restore(self):
        if "weight" in self.mod.__dict__: del self.mod.__dict__["weight"]
        self.mod._parameters["weight"] = torch.nn.Parameter(self.W0, requires_grad=False)


def ce(model, toks):
    logits = model(input_ids=toks[:, :-1]).logits
    return torch.nn.functional.cross_entropy(logits.reshape(-1, logits.shape[-1]), toks[:, 1:].reshape(-1))


def long_fit(model, target, data, watch, lr, cap, rank=2, seed=0, seg=10, patience=5, drop=0.25):
    """`data` maps set names to LongTensors of windows; 'tr' is trained on. Returns the losses on every set each
    `seg` steps; stops once the gain on `watch` has fallen to `drop` of its peak at least `patience` evaluations
    after the peak, or at `cap` steps."""
    lo = Lora(model, target, rank, seed); opt = torch.optim.Adam([lo.A, lo.B], lr=lr, betas=(0.9, 0.999), eps=1e-8)
    def losses():
        lo.install()
        with torch.no_grad(): return {s: float(ce(model, t)) for s, t in data.items()}
    try:
        base = losses(); out = dict(step=[0], norm=[0.0], stopped="cap", **{s: [v] for s, v in base.items()}); peak, kpeak = -np.inf, 0
        for k in range(cap // seg):
            for _ in range(seg):
                lo.install(); opt.zero_grad(); ce(model, data["tr"]).backward(); opt.step()
            cur = losses(); out["step"].append((k + 1) * seg); out["norm"].append(lo.norm())
            for s, v in cur.items(): out[s].append(v)
            g = base[watch] - cur[watch]
            if g > peak: peak, kpeak = g, k
            if k - kpeak >= patience and g <= drop * peak: out["stopped"] = "turned"; break
    finally:
        lo.restore()
    return out


def knee(tj, watch):
    k = int(np.argmin(tj[watch])); return dict(step=tj["step"][k], train_gain=tj["tr"][0] - tj["tr"][k], gain=tj[watch][0] - tj[watch][k])


def condition(model, encode, texts, c, cfg, ckpt):
    tr, ho, te = corpus3(texts, encode, c["seed"], c["n"], c["n_val"], c["n_test"], c["transform"]); h = c["n"] // 2; tokens = fingerprint(tr, ho, te); T = lambda a: torch.tensor(np.asarray(a), dtype=torch.long)
    st = json.load(open(ckpt)) if Path(ckpt).exists() else dict(tokens=tokens, full={}, half={}, seconds=0.0); assert st["tokens"] == tokens, f"{ckpt} was written for other contexts"
    if st["full"] or st["half"]: log(f"  {c['name']}: resumed with {len(st['full'])} full fits and {len(st['half'])} half-fits")
    save = lambda: json.dump(st, open(ckpt, "w"), indent=1)
    for i, m in enumerate(c["targets"]):
        if m not in st["full"]:
            t = time.time(); tj = long_fit(model, m, dict(tr=T(tr), ho=T(ho), te=T(te)), "te", cfg["lr"], cfg["cap_full"], cfg["rank"], seed=c["seed"] * 1000 + i); st["full"][m] = tj; st["seconds"] += time.time() - t; save(); kn = knee(tj, "te")
            log(f"  {c['name']} full {m}: test gain peaks at step {kn['step']} ({kn['gain']:+.3f}) at training gain {kn['train_gain']:.2f}; ran {tj['step'][-1]} steps, {tj['stopped']}; base test loss {tj['te'][0]:.3f}; at the end {tj['te'][0] - tj['te'][-1]:+.3f} ({time.time() - t:.0f}s)")
        for j, (name, A, B) in enumerate((("A to B", tr[:h], tr[h:2 * h]), ("B to A", tr[h:2 * h], tr[:h]))):
            tag = f"{name} {m}"
            if tag in st["half"]: continue
            t = time.time(); tj = long_fit(model, m, dict(tr=T(A), ho=T(B)), "ho", cfg["lr"], cfg["cap_half"], cfg["rank"], seed=c["seed"] * 1000 + 100 + 10 * i + j, drop=0.5); st["half"][tag] = tj; st["seconds"] += time.time() - t; save(); kn = knee(tj, "ho")
            log(f"  {c['name']} half {tag}: the other half's loss is lowest at step {kn['step']} ({kn['gain']:+.3f}) at training gain {kn['train_gain']:.2f}; ran {tj['step'][-1]} steps, {tj['stopped']} ({time.time() - t:.0f}s)")
    return dict(name=c["name"], cond=c, tokens=tokens, full=st["full"], half=st["half"], seconds=st["seconds"])


def run(cfg_path, out_dir):
    cfg = json.load(open(cfg_path)); out_dir = Path(out_dir); out_dir.mkdir(parents=True, exist_ok=True); torch.set_num_threads(cfg.get("threads", 4)); T0 = time.time()
    texts = docs_text(cfg["repo"], cfg["corpus_commit"]); log(f"corpus: docs/*.md at {cfg['corpus_commit']}, {len(texts)} files"); res = out_dir / "rows.json"
    out = json.load(open(res))["rows"] if res.exists() else []; done = {r["name"] for r in out}; loaded = (None, None, None)
    for c in cfg["conditions"]:
        if c["name"] in done: log(f"  {c['name']}: already done"); continue
        if loaded[0] != c["model"]: loaded = (c["model"], *load_model(cfg["models"][c["model"]])); log(f"model {c['model']}: {sum(p.numel() for p in loaded[1].parameters()) / 1e6:.0f}M parameters")
        out.append(condition(loaded[1], loaded[2], texts, c, cfg, out_dir / f"{c['name']}.ckpt.json")); json.dump(dict(rows=out), open(res, "w"), indent=1); log(f"[{time.time() - T0:.0f}s]")
    log(f"done in {time.time() - T0:.0f}s")


if __name__ == "__main__":
    if len(sys.argv) == 4 and sys.argv[1] == "run": run(sys.argv[2], sys.argv[3])
    else: print(__doc__)
