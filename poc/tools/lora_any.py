#!/usr/bin/env python3
"""lora_knee.py's experiment for any causal language model transformers loads with AutoModelForCausalLM
(Llama-style, Qwen, GPT-2, ...), without changing the frozen lora_knee.py.

  python lora_any.py run CONFIG.json OUT_DIR      as lora_knee.py run; a model spec is dict(dir=..., kind="auto")
  python lora_any.py targets MODEL_DIR            the four default targets, and the model's layer count

The fits, corpus draws, checkpoints and rows are lora_knee.py's (LK.condition); only the loader differs:
weights in float32, and text encoded without special tokens, so a window never carries a BOS token.
Default targets are the counterparts of ED5's: the MLP output matrix of an early layer (L/6) and of an upper
one (2L/3), the value matrix of the early layer's attention and the attention output matrix of the upper one.
"""
from __future__ import annotations
import json, sys, time
from pathlib import Path
import torch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lora_knee as LK


def load_auto(d):
    import transformers
    transformers.logging.set_verbosity_error()
    tok = transformers.AutoTokenizer.from_pretrained(d)
    model = transformers.AutoModelForCausalLM.from_pretrained(d, dtype=torch.float32); model.eval()
    for p in model.parameters(): p.requires_grad_(False)
    return model, (lambda text: tok.encode(text, add_special_tokens=False))


def load_model(spec):
    return load_auto(spec["dir"]) if spec.get("kind", "auto") == "auto" else LK.load_model(spec)


def default_targets(model):
    """(targets, n_layers, early, upper) for GPT-2-style or Llama/Qwen-style module names."""
    names = {n for n, _ in model.named_modules()}
    if any(n.startswith("model.layers.") for n in names):
        L = model.config.num_hidden_layers; e, u = max(1, round(L / 6)), round(2 * L / 3); p = "model.layers"
        return [f"{p}.{e}.mlp.down_proj", f"{p}.{u}.mlp.down_proj", f"{p}.{e}.self_attn.v_proj", f"{p}.{u}.self_attn.o_proj"], L, e, u
    if any(n.startswith("transformer.h.") for n in names):
        L = model.config.n_layer; e, u = max(1, round(L / 6)), round(2 * L / 3); d = model.config.n_embd; p = "transformer.h"
        return [f"{p}.{e}.mlp.c_proj", f"{p}.{u}.mlp.c_proj", f"{p}.{e}.attn.c_attn[{2 * d}:{3 * d}]", f"{p}.{u}.attn.c_proj"], L, e, u
    raise ValueError("unknown module layout: name the targets explicitly")


def run(cfg_path, out_dir):
    cfg = json.load(open(cfg_path)); out_dir = Path(out_dir); out_dir.mkdir(parents=True, exist_ok=True); torch.set_num_threads(cfg.get("threads", 4)); T0 = time.time()
    texts = LK.docs_text(cfg["repo"], cfg["corpus_commit"]); LK.log(f"corpus: docs/*.md at {cfg['corpus_commit']}, {len(texts)} files"); res = out_dir / "rows.json"
    out = json.load(open(res))["rows"] if res.exists() else []; done = {r["name"] for r in out}; loaded = (None, None, None)
    for c in cfg["conditions"]:
        if c["name"] in done: LK.log(f"  {c['name']}: already done"); continue
        if loaded[0] != c["model"]: loaded = (c["model"], *load_model(cfg["models"][c["model"]])); LK.log(f"model {c['model']}: {sum(p.numel() for p in loaded[1].parameters()) / 1e6:.0f}M parameters")
        out.append(LK.condition(loaded[1], loaded[2], texts, c, cfg, out_dir / f"{c['name']}.ckpt.json")); json.dump(dict(rows=out), open(res, "w"), indent=1); LK.log(f"[{time.time() - T0:.0f}s]")
    LK.log(f"done in {time.time() - T0:.0f}s")


if __name__ == "__main__":
    if len(sys.argv) == 4 and sys.argv[1] == "run": run(sys.argv[2], sys.argv[3])
    elif len(sys.argv) == 3 and sys.argv[1] == "targets":
        m, _ = load_auto(sys.argv[2]); t, L, e, u = default_targets(m); print(json.dumps(dict(layers=L, early=e, upper=u, targets=t), indent=1))
    else: print(__doc__)
