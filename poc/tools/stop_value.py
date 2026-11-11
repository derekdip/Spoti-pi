#!/usr/bin/env python3
"""The stopping value for your own data, in one command (the rule of docs/prescreen-theory.md, sections 12 to 15).

  python poc/tools/stop_value.py MODEL_DIR DATA [--save ADAPTER.pt] [options]

MODEL_DIR  a local Hugging Face causal language model (config.json, weights, tokenizer files).
DATA       a .jsonl file with a "text" field per line, or a text file whose examples are separated by blank
           lines. Meant for small sets, 8 to a few hundred examples; every step uses all of them.

What it does: splits the examples into two halves at random, fits a rank-r LoRA on one half while watching the
loss on the other, for each target matrix and both ways round, and notes the drop in training loss (nats per
token) at which the other half's loss was lowest. The median of those knees is the stopping value g*. Then, with
--save, it trains one LoRA on all the examples, stops when the training loss has fallen by g*, and saves it.
No example is held out of that final fit.

Options:
  --targets T [T ...]  modules to fit (default: four per model, see lora_any.py targets)
  --save PATH          train the final adapter on all examples and save it (torch.save of a dict)
  --final-target T     the module the final adapter goes on (default: the first target)
  --rank 2  --lr 1e-3  --max-len 128  --seed 0  --threads 4  --cap 500 (half-fits)  --final-cap 800

What it does not promise: the rule was tested on 8 to 64 short contexts of one corpus, rank 2, one learning
rate, on GPT-2-family models (ED4 to ED6). Its estimate runs high at 8 examples; at that size, stopping on a
held-out quarter and refitting was as good or better in ED7's pilot.
"""
from __future__ import annotations
import argparse, json, sys, time
from pathlib import Path
import numpy as np, torch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lora_knee as LK, lora_any as LA


def read_examples(path):
    p = Path(path); txt = p.read_text()
    if p.suffix == ".jsonl": return [json.loads(l)["text"] for l in txt.splitlines() if l.strip()]
    return [e.strip() for e in txt.split("\n\n") if e.strip()]


def batch(tok_lists):
    """Right-padded ids and a mask of the predicted positions."""
    L = max(len(t) for t in tok_lists); ids = torch.zeros(len(tok_lists), L, dtype=torch.long); m = torch.zeros(len(tok_lists), L - 1)
    for i, t in enumerate(tok_lists): ids[i, :len(t)] = torch.tensor(t); m[i, :len(t) - 1] = 1
    return ids, m


def loss(model, b):
    ids, m = b; lg = model(input_ids=ids[:, :-1]).logits
    ce = torch.nn.functional.cross_entropy(lg.reshape(-1, lg.shape[-1]), ids[:, 1:].reshape(-1), reduction="none").reshape(m.shape)
    return (ce * m).sum() / m.sum()


def fit(model, target, tr, watch, rank, lr, cap, seed, stop_gain=None, seg=10, patience=5, drop=0.5):
    """Train a LoRA on `tr`. With `watch`, stop once the watched gain has fallen to `drop` of its peak (patience
    evaluations after it) and return the training gain at the watched minimum. With `stop_gain`, stop when the
    training gain reaches it and return the LoRA."""
    lo = LK.Lora(model, target, rank, seed); opt = torch.optim.Adam([lo.A, lo.B], lr=lr)
    def ev(b):
        lo.install()
        with torch.no_grad(): return float(loss(model, b))
    try:
        t0 = ev(tr); w0 = ev(watch) if watch else None; best = (np.inf, 0.0, 0); peak, kp = -np.inf, 0
        for k in range(cap // seg):
            for _ in range(seg): lo.install(); opt.zero_grad(); loss(model, tr).backward(); opt.step()
            g = t0 - ev(tr); step = (k + 1) * seg
            if stop_gain is not None and g >= stop_gain: return dict(lora=lo, gain=g, step=step, reached=True)
            if watch:
                w = ev(watch)
                if w < best[0]: best = (w, g, step)
                if w0 - w > peak: peak, kp = w0 - w, k
                if k - kp >= patience and w0 - w <= drop * peak: break
        if watch: return dict(knee=best[1], step=best[2], watched_gain=w0 - best[0], turned=k - kp >= patience)
        return dict(lora=lo, gain=g, step=step, reached=False)
    finally:
        if watch or stop_gain is None: lo.restore()


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0]); ap.add_argument("model"); ap.add_argument("data")
    ap.add_argument("--targets", nargs="+"); ap.add_argument("--save"); ap.add_argument("--final-target"); ap.add_argument("--rank", type=int, default=2)
    ap.add_argument("--lr", type=float, default=1e-3); ap.add_argument("--max-len", type=int, default=128); ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--threads", type=int, default=4); ap.add_argument("--cap", type=int, default=500); ap.add_argument("--final-cap", type=int, default=800)
    a = ap.parse_args(); torch.set_num_threads(a.threads); torch.manual_seed(a.seed)
    model, enc = LA.load_auto(a.model); targets = a.targets or LA.default_targets(model)[0]
    toks = [t[:a.max_len] for t in (enc(x) for x in read_examples(a.data)) if len(t) >= 2]; n = len(toks)
    if n < 4: sys.exit(f"need at least 4 examples with 2 or more tokens, got {n}")
    perm = np.random.default_rng(a.seed).permutation(n); A, B = batch([toks[i] for i in perm[:n // 2]]), batch([toks[i] for i in perm[n // 2:]])
    LK.log(f"{n} examples, halves of {n // 2} and {n - n // 2}; targets: {', '.join(targets)}"); knees = []
    for i, t in enumerate(targets):
        for j, (x, y, name) in enumerate(((A, B, "A on B"), (B, A, "B on A"))):
            r = fit(model, t, x, y, a.rank, a.lr, a.cap, a.seed * 1000 + 10 * i + j); knees.append(r["knee"])
            LK.log(f"  {t} {name}: other half best at step {r['step']} (gain {r['watched_gain']:+.3f}), training loss down {r['knee']:.3f}{'' if r['turned'] else ' (did not turn: raise --cap)'}")
    g = float(np.median(knees)); cv = float(np.std(knees) / np.mean(knees))
    print(json.dumps(dict(stop_value=g, knees=knees, cv=cv, n=n, targets=targets), indent=1))
    if a.save:
        t = a.final_target or targets[0]; r = fit(model, t, batch(toks), None, a.rank, a.lr, a.final_cap, a.seed * 1000 + 999, stop_gain=g)
        lo = r["lora"]; torch.save(dict(target=t, rank=a.rank, A=lo.A.detach(), B=lo.B.detach(), stop_value=g, steps=r["step"], model=a.model), a.save); lo.restore()
        LK.log(f"final adapter on {t}: training loss down {r['gain']:.3f} at step {r['step']}{'' if r['reached'] else ' (stop value not reached: raise --final-cap)'}; saved to {a.save}")


if __name__ == "__main__":
    main()
