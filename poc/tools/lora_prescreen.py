#!/usr/bin/env python3
"""A pre-screen for LoRA fine-tuning of a causal language model, in PyTorch (docs/prescreen-tool.md).

Before training anything, for every candidate weight matrix it reports how fast the loss would fall along the
best rank-r direction, how much of that is real rather than sampling noise, and how many directions the data
can support. It needs one pass of gradients over the training text (and one over held-out text if given).

  python lora_prescreen.py --model PATH --train train.txt [--held held.txt] [--rank 2] [--contexts 96]
                           [--ctx 64] [--targets REGEX] [--top 3] [--json out.json]

Per module, with G the training gradient of the next-token loss with respect to the weight matrix, G_A and G_B
the gradients on two halves of the training contexts, and E = (G_A - G_B) / 2 (an empirical null: it has the
law of the sampling noise in G):

  train_slope   sqrt(sum of the r largest squared singular values of G): the first-order rate at which the
                training loss falls per unit Frobenius norm of a rank-r change
  snr           largest singular value of G over largest singular value of E; near 1 means the direction is noise
  shrunk_slope  the part of train_slope predicted to generalise: optimal singular-value shrinkage at the
                null's measured edge (no held-out data used)
  lower_bound   train_slope minus the null's rank-r norm: a guaranteed floor on the population slope
  rank_above    how many of G's leading singular values exceed the null's largest: a floor on the rank the
                data supports, usually far below it
  cf_share      the cross-fitted real share of the rank-r direction: take the direction from one half of the
                contexts, measure its slope on the other half, divide by its slope on its own half, average
                both ways. No noise model. It describes a direction fitted on half the contexts, so it reads
                low; under 1/2 the direction's first step is mostly sampling noise. It does not say how long
                to train (see below)
  rank_cf       how many of the leading components have a cross-fitted share above 1/2: a cautious estimate
                of the rank worth fitting
  held_slope    <G_held, R> / ||R|| with R the rank-r truncation of G: the measured generalising slope
                (only with --held)

What is established and what is not (docs/prescreen-theory.md, docs/math-track-ed*-results.md): on GPT-2 base
the shrunk slope predicted the held-out slope to about ten percent across three text conditions and training
sets of 8 to 128 contexts. On the same runs rank_cf never exceeded the number of leading components that were
more than half real and was within 1.4 components of it on average, where rank_above stayed near 2; cf_share
read low in 13 of 15 conditions; with 8 contexts neither rank is reliable. None of these numbers says how long
to train: in a pilot at 8 contexts a LoRA trained past about 100 Adam steps ended below the unadapted model on
fresh text on all eight matrices tried, at shares from 0.2 to 0.6, while stopping at the validation minimum kept
the gain (docs/prescreen-theory.md, section 11). cf_share cannot see a difference
between the training text and the text the model will meet. A slope is an infinitesimal rate: it ranks where a
small change helps most and it does NOT say whether a full fine-tune will help, nor how far a module can
usefully move.
"""
from __future__ import annotations
import argparse, json, math, re, sys
import torch

DEFAULT_TARGETS = r"(attn|attention|mlp|\.fc|proj|query|key|value|dense)"


def shrink(s, tau, a, b):
    """Frobenius-optimal singular-value shrinkage for an a x b matrix in noise of entry level tau."""
    big, small = max(a, b), min(a, b); c = small / big; y = s / (tau * math.sqrt(big))
    return tau * math.sqrt(big) * math.sqrt(max((y * y - c - 1) ** 2 - 4 * c, 0.0)) / y if y > 1 + math.sqrt(c) else 0.0


def target_parameters(model, pattern=DEFAULT_TARGETS, exclude=r"(wte|wpe|embed|lm_head|ln_|norm)"):
    """Named 2-D weight matrices whose names match `pattern` and not `exclude`."""
    pat, exc = re.compile(pattern), re.compile(exclude)
    return {n: p for n, p in model.named_parameters() if p.dim() == 2 and pat.search(n) and not exc.search(n)}


def windows(ids, n, ctx, seed):
    """n windows of ctx + 1 token ids drawn from a 1-D tensor of ids."""
    g = torch.Generator().manual_seed(seed); starts = torch.randint(0, len(ids) - ctx - 1, (n,), generator=g)
    return torch.stack([ids[s:s + ctx + 1] for s in starts])


def mean_gradients(model, params, tokens, batch=16):
    """The gradient of the mean next-token loss over the given windows (inputs tokens[:, :-1], targets
    tokens[:, 1:]) with respect to each target matrix, and the loss."""
    acc = {n: torch.zeros_like(p, dtype=torch.float64) for n, p in params.items()}; total = 0.0
    for i in range(0, len(tokens), batch):
        t = tokens[i:i + batch]; logits = model(input_ids=t[:, :-1]).logits
        loss = torch.nn.functional.cross_entropy(logits.reshape(-1, logits.shape[-1]), t[:, 1:].reshape(-1), reduction="sum")
        grads = torch.autograd.grad(loss, list(params.values()))
        for (n, _), g in zip(params.items(), grads): acc[n] += g.double()
        total += loss.item()
    count = tokens.shape[0] * (tokens.shape[1] - 1)
    return {n: g / count for n, g in acc.items()}, total / count


def crossfit(GA, GB, r, lead):
    """The cross-fitted share of the rank-r direction and of each of the `lead` leading components: directions
    from one half's gradient, slope measured on the other half's, averaged over the two ways round."""
    share = 0.0; comp = torch.zeros(lead, dtype=torch.float64)
    for Gf, Gv in ((GA, GB), (GB, GA)):
        U, S, Vh = torch.linalg.svd(Gf, full_matrices=False); k = min(lead, len(S)); R = (U[:, :r] * S[:r]) @ Vh[:r]
        share += 0.5 * float((Gv * R).sum() / (R * R).sum()); comp[:k] += 0.5 * torch.stack([U[:, j] @ Gv @ Vh[j] / S[j] for j in range(k)])
    return share, comp


def prescreen(model, train_tokens, held_tokens=None, rank=2, targets=DEFAULT_TARGETS, batch=16, lead=8):
    """The table. train_tokens and held_tokens are (n, ctx + 1) LongTensors of token ids."""
    model.eval(); params = target_parameters(model, targets); n = len(train_tokens); half = n // 2
    for p in model.parameters(): p.requires_grad_(False)
    for p in params.values(): p.requires_grad_(True)
    GA, lossA = mean_gradients(model, params, train_tokens[:half], batch); GB, lossB = mean_gradients(model, params, train_tokens[half:2 * half], batch)
    GH, loss_held = mean_gradients(model, params, held_tokens, batch) if held_tokens is not None else (None, None)
    rows = []
    for name in params:
        G = (GA[name] + GB[name]) / 2; E = (GA[name] - GB[name]) / 2; a, b = G.shape
        U, S, Vh = torch.linalg.svd(G, full_matrices=False); e = torch.linalg.svdvals(E); r = min(rank, len(S))
        R = (U[:, :r] * S[:r]) @ Vh[:r]; nR = float(torch.linalg.norm(R)); edge = float(e[0]); tau = edge / (math.sqrt(a) + math.sqrt(b)); cf, comp = crossfit(GA[name], GB[name], r, lead)
        row = dict(module=name, shape=[a, b], train_slope=nR, snr=float(S[0]) / edge, shrunk_slope=sum(float(S[k]) * shrink(float(S[k]), tau, a, b) for k in range(r)) / nR,
                   lower_bound=nR - float(torch.sqrt((e[:r] ** 2).sum())), rank_above=int((S[:lead] > edge).sum()), cf_share=cf, rank_cf=int((comp > 0.5).sum()))
        if GH is not None: row["held_slope"] = float((GH[name] * R).sum()) / nR
        rows.append(row)
    key = "held_slope" if GH is not None else "shrunk_slope"; rows.sort(key=lambda x: -x[key])
    return dict(loss_train=(lossA + lossB) / 2, loss_held=loss_held, rank=rank, contexts=2 * half, ranked_by=key, modules=rows)


def report(res, top=3):
    L = [f"training loss {res['loss_train']:.3f}" + (f", held-out loss {res['loss_held']:.3f}" if res["loss_held"] is not None else "") + f"; {res['contexts']} contexts; rank {res['rank']}; ranked by {res['ranked_by']}", ""]
    held = res["loss_held"] is not None
    L.append(f"{'module':<40} {'shape':>11} {'train':>8} {'shrunk':>8} {'floor':>8}" + (f" {'held':>8}" if held else "") + f" {'snr':>6} {'above':>5} {'cf':>6} {'rank':>5}")
    for x in res["modules"]:
        L.append(f"{x['module']:<40} {x['shape'][0]:>5}x{x['shape'][1]:<5} {x['train_slope']:8.4f} {x['shrunk_slope']:8.4f} {x['lower_bound']:8.4f}" + (f" {x['held_slope']:8.4f}" if held else "") + f" {x['snr']:6.2f} {x['rank_above']:5d} {x['cf_share']:6.2f} {x['rank_cf']:5d}")
    snr = sorted(x["snr"] for x in res["modules"])[len(res["modules"]) // 2]; L.append("")
    L.append(f"largest {res['ranked_by']}: " + ", ".join(x["module"] for x in res["modules"][:top]))
    L.append(f"median signal-to-noise {snr:.2f}: " + ("the leading directions are mostly noise at this data size; add contexts before trusting any ranking" if snr < 1.5 else "the leading directions are partly noise; prefer the shrunk or held-out column to the training one" if snr < 2.5 else "the leading directions are real at this data size"))
    cf = sorted(x["cf_share"] for x in res["modules"])[len(res["modules"]) // 2]
    L.append(f"median cross-fitted share {cf:.2f}: " + ("under one half: the leading direction is mostly sampling noise at this data size; add contexts before trusting the ranking" if cf < 0.5 else "above one half: the leading direction is predicted to hold on more text like the training text"))
    L.append("none of these numbers says how long to train: hold text out and stop when its loss turns")
    L.append("a slope ranks where a small change helps most; it did not predict which matrix gains most over a whole fit (ED4), and it does not say whether a full fine-tune will help")
    return "\n".join(L)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0]); ap.add_argument("--model", required=True); ap.add_argument("--train", required=True); ap.add_argument("--held")
    ap.add_argument("--rank", type=int, default=2); ap.add_argument("--contexts", type=int, default=96); ap.add_argument("--ctx", type=int, default=64); ap.add_argument("--targets", default=DEFAULT_TARGETS)
    ap.add_argument("--top", type=int, default=3); ap.add_argument("--batch", type=int, default=16); ap.add_argument("--seed", type=int, default=0); ap.add_argument("--json"); a = ap.parse_args(argv)
    from transformers import AutoModelForCausalLM, AutoTokenizer
    tok = AutoTokenizer.from_pretrained(a.model); model = AutoModelForCausalLM.from_pretrained(a.model)
    ids = lambda path: torch.tensor(tok.encode(open(path, encoding="utf-8").read()), dtype=torch.long)
    tr = windows(ids(a.train), a.contexts, a.ctx, a.seed); ho = windows(ids(a.held), a.contexts, a.ctx, a.seed + 1) if a.held else None
    res = prescreen(model, tr, ho, a.rank, a.targets, a.batch); print(report(res, a.top))
    if a.json: json.dump(res, open(a.json, "w"), indent=1)


if __name__ == "__main__":
    main()
