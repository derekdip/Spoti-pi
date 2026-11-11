"""Cross-check: the PyTorch tool on GPT-2 (Hugging Face weights) against the JAX implementation (Keras preset
weights) on the same token windows.

  /usr/bin/python3 poc/tools/crosscheck_jax_ref.py OUT_DIR                 writes the tokens and the JAX numbers
  /usr/bin/python3 -I poc/tools/crosscheck_gpt2.py OUT_DIR GPT2_HF_DIR      compares (GPT2_HF_DIR holds config.json
                                                                           and pytorch_model.bin)
Result on 2026-11-11: losses agree to six digits, every slope to 7e-5 relative."""
import sys, json, math, time
sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.abspath(__file__)))
import numpy as np, torch
torch.set_num_threads(1)
from transformers import GPT2Config, GPT2LMHeadModel
import lora_prescreen as LP
S = sys.argv[1]; D = sys.argv[2]; t = time.time()
cfg = GPT2Config.from_json_file(D + '/config.json'); model = GPT2LMHeadModel(cfg); sd = torch.load(D + '/pytorch_model.bin', map_location='cpu', weights_only=True)
res = model.transformer.load_state_dict(sd, strict=False); model.tie_weights(); print("loaded; missing", list(res.missing_keys)[:3], "unexpected", len(res.unexpected_keys), f"({time.time() - t:.0f}s)", flush=True)
tr = torch.tensor(np.load(S + '/train_tokens.npy'), dtype=torch.long); ho = torch.tensor(np.load(S + '/held_tokens.npy'), dtype=torch.long); ref = json.load(open(S + '/jax_ref.json'))
out = LP.prescreen(model, tr, ho, rank=2, targets=r"h\.(2|5|8|11)\.(attn\.c_proj|mlp\.c_fc|mlp\.c_proj|attn\.c_attn)", batch=16)
print(f"loss train: torch {out['loss_train']:.6f} jax {ref['loss_train']:.6f}; held: torch {out['loss_held']:.6f} jax {ref['loss_held']:.6f}", flush=True)
name = {"attn.c_proj": "o", "mlp.c_fc": "fc", "mlp.c_proj": "proj"}; worst = 0.0
print(f"{'module':<9} {'train slope torch/jax':>26} {'held slope torch/jax':>26} {'shrunk torch/jax':>26} {'edge torch/jax':>24}")
for x in out["modules"]:
    parts = x["module"].split("."); L = parts[2]; kind = ".".join(parts[3:5])
    if kind not in name: continue
    m = f"{name[kind]}@{L}"; r = ref["modules"][m]
    rel = max(abs(x["train_slope"] / r["train_slope"] - 1), abs(x["held_slope"] / r["held_slope"] - 1), abs(x["shrunk_slope"] / r["shrunk"] - 1)); worst = max(worst, rel)
    print(f"{m:<9} {x['train_slope']:12.6f} {r['train_slope']:12.6f}  {x['held_slope']:12.6f} {r['held_slope']:12.6f}  {x['shrunk_slope']:12.6f} {r['shrunk']:12.6f}")
# the value block of c_attn, by hand with the tool's own gradient routine
params = {n: p for n, p in model.named_parameters() if n.endswith("attn.c_attn.weight") and n.split(".")[2] in ("2", "5", "8", "11")}
for p in model.parameters(): p.requires_grad_(False)
for p in params.values(): p.requires_grad_(True)
GA, _ = LP.mean_gradients(model, params, tr[:16]); GB, _ = LP.mean_gradients(model, params, tr[16:]); GH, _ = LP.mean_gradients(model, params, ho)
for n in params:
    L = n.split(".")[2]; sl = slice(1536, 2304); G = ((GA[n] + GB[n]) / 2)[:, sl]; E = ((GA[n] - GB[n]) / 2)[:, sl]; U, Sv, Vh = torch.linalg.svd(G, full_matrices=False); R = (U[:, :2] * Sv[:2]) @ Vh[:2]; nR = float(torch.linalg.norm(R))
    e = float(torch.linalg.svdvals(E)[0]); tau = e / (2 * math.sqrt(768)); sh = sum(float(Sv[k]) * LP.shrink(float(Sv[k]), tau, 768, 768) for k in range(2)) / nR; hs = float((GH[n][:, sl] * R).sum()) / nR; r = ref["modules"][f"v@{L}"]
    rel = max(abs(nR / r["train_slope"] - 1), abs(hs / r["held_slope"] - 1), abs(sh / r["shrunk"] - 1), abs(e / r["edge"] - 1)); worst = max(worst, rel)
    print(f"{'v@' + L:<9} {nR:12.6f} {r['train_slope']:12.6f}  {hs:12.6f} {r['held_slope']:12.6f}  {sh:12.6f} {r['shrunk']:12.6f}  {e:10.6f} {r['edge']:10.6f}")
print(f"largest relative difference over all compared numbers: {worst:.2e} ({time.time() - t:.0f}s)")
print(); print(LP.report(out, 3))
