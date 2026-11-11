"""Reference numbers from the JAX implementation on fixed tokens, for the PyTorch cross-check."""
import sys, json, os; sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import numpy as np, jax, jax.numpy as jnp
from poc.ecsdec import gpt2 as GM, prescreen as PS
from poc.ecsdec.rmt_check import shrink
S = sys.argv[1].rstrip('/') + '/'
P = GM.load_params(); tok = GM.tokenizer(); tr, ho = PS.corpus(7, 32, tok, "altcaps"); np.save(S + "train_tokens.npy", tr); np.save(S + "held_tokens.npy", ho)
lib = PS.LIBRARY; zeros = {m: jnp.zeros(GM.shape_of(m), jnp.float32) for m in lib}; loss = lambda P, x, y, D: PS._ce(GM.forward(P, x, D), y)
grad = jax.jit(lambda P, x, y: jax.grad(lambda D: loss(P, x, y, D))(zeros)); X = lambda a: (jnp.asarray(a[:, :PS.CTX]), jnp.asarray(a[:, 1:PS.CTX + 1]))
G = {k: grad(P, *X(v)) for k, v in dict(tr=tr, A=tr[:16], B=tr[16:], ho=ho).items()}; out = dict(loss_train=float(loss(P, *X(tr), {})), loss_held=float(loss(P, *X(ho), {})), modules={})
for m in lib:
    a, b = GM.shape_of(m); Gt = np.asarray(G["tr"][m], np.float64); E = (np.asarray(G["A"][m], np.float64) - np.asarray(G["B"][m], np.float64)) / 2
    U, s, Vt = np.linalg.svd(Gt, full_matrices=False); R = (U[:, :2] * s[:2]) @ Vt[:2]; nR = np.linalg.norm(R); e = np.linalg.svd(E, compute_uv=False); tau = e[0] / (np.sqrt(a) + np.sqrt(b))
    out["modules"][m] = dict(train_slope=float(nR), edge=float(e[0]), held_slope=float(np.vdot(np.asarray(G["ho"][m], np.float64), R) / nR), shrunk=float(sum(s[k] * shrink(s[k], tau, a, b) for k in range(2)) / nR))
json.dump(out, open(S + "jax_ref.json", "w"), indent=1); print("jax reference written", out["loss_train"], out["loss_held"])
