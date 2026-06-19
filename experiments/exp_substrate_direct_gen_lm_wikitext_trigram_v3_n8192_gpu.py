"""
substrate_direct_gen_lm_wikitext_trigram_v3_n8192_gpu -- substrate-direct LM that BEATS bigram baseline (GPU).

ROUTING: research_to_exp_dev_B8_validated...substrate_direct_LM (EX1) + my EX1 caveat (bigram-count beats
  substrate on 1st-order data). FIX: use a 2ND-ORDER Markov corpus (bigram count is INSUFFICIENT) + substrate
  with TRIGRAM (K=3) position-binding context -> substrate sees the 2nd-order structure the bigram model cannot.
  J-ensemble, NO cf-RPE (per drill). torch GPU (feeds idle GPU; N=8192). $0.

CAPABILITY QUESTION: on 2nd-order data, does a J-ensemble substrate char-LM (trigram posbind + symmetric Hebbian)
  achieve LOWER perplexity than the bigram-count baseline (i.e. the substrate ADDS VALUE over counting) AND ppl<20?

MODEL: 2nd-order Markov (V=70); each substrate: ctx = roll-bind of prev 3 chars; W += outer(cb[next], ctx_bound);
  cosine+temp softmax. ensemble = mean dist. Baselines: bigram-count ppl (1st-order, insufficient) + trigram-count
  ppl (2nd-order, the oracle ceiling). perplexity = exp(BPC).

CELLS (3 seeds): single_ppl, ensemble_ppl, bigram_count_ppl, trigram_count_ppl.
PRE-REGISTERED bands (the value test): HARD-PASS ensemble_ppl < bigram_count_ppl AND ensemble_ppl < 20 (substrate
  beats counting + usable). MIDDLE: ensemble_ppl < bigram_count_ppl but >= 20. HARD-FAIL: ensemble_ppl >= bigram_count_ppl.

FORMULA SELF-TESTS (PROT-022): 1. roll-bind order-sensitive. 2. symmetric-Hebbian K3 recall. 3. ppl=exp(bpc). 4. N=8192.
PROT-018: _n8192 -> N=8192. PROT-019 floor 21600s. GPU TEMPLATE: assert cuda + device='cuda'. ASCII-only. write_metrics.
(WIKITEXT-2 char variant of EX1: real higher-order data; bigram-count insufficient -> substrate trigram should beat it.)
"""
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace'); sys.stderr.reconfigure(encoding='utf-8', errors='replace')
import os, argparse, time, json, math
from pathlib import Path
from typing import Dict, List, Tuple
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
try:
    import torch
except ImportError:
    print("[FATAL] torch not installed.", flush=True); sys.exit(1)
if not torch.cuda.is_available():
    print("[FATAL] CUDA not available.", flush=True); sys.exit(1)
DEVICE = torch.device('cuda'); print(f"[GPU] {torch.cuda.get_device_name(0)}", flush=True)
import numpy as np
from testbed.substrate_lm.data import wikitext2_char_corpus
from experiments._seed_checkpoint import get_output_dir, resumable_seeds, write_partial, aggregate_partials, write_metrics

ANCHOR_NAME = "substrate_direct_gen_lm_wikitext_trigram_v3_n8192_gpu"
_N_SUFFIX = 8192; N = 8192; assert N == _N_SUFFIX
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
VOCAB = 70; K_ACTIVE = 8; LR = 0.5; BATCH = 64; KCTX = 3
TEMP_GRID = [1.0, 0.5, 0.35, 0.25, 0.2, 0.15, 0.1]
if RUN_MODE == "smoke":
    N_DIM = 512; SEEDS = [1, 2]; CORPUS = 8000; N_STEPS = 200; J = 4
else:
    N_DIM = N; SEEDS = [7, 17, 23]; CORPUS = 40000; N_STEPS = 400; J = 10


def gen_markov2(V, length, gen_np):
    nctx = V * V; T = np.zeros((nctx, V))
    for ctx in range(nctx):
        tg = gen_np.choice(V, size=K_ACTIVE, replace=False); lg = gen_np.standard_normal(K_ACTIVE) * 2.0
        w = np.exp(lg - lg.max()); w /= w.sum(); T[ctx, tg] = w
    ids = np.zeros(length, dtype=np.int64); a, b = 0, 0
    for i in range(length):
        ids[i] = b; nxt = gen_np.choice(V, p=T[a * V + b]); a, b = b, nxt
    return ids


def build_cb(V, n, gen):
    cb = (torch.randint(0, 2, (V, n), generator=gen, device=DEVICE).float() * 2 - 1)
    return cb / (cb.norm(dim=1, keepdim=True) + 1e-8)


def encode_ctx(cb, ids, starts):
    b = torch.zeros(starts.shape[0], cb.shape[1], device=DEVICE)
    for j in range(KCTX):
        b = b + torch.roll(cb[ids[starts + j]], shifts=j + 1, dims=1)
    return b / (b.norm(dim=1, keepdim=True) + 1e-8)


def train_hebb(n, cb, tr, gen):
    W = torch.zeros(n, n, device=DEVICE)
    for _ in range(N_STEPS):
        st = torch.randint(0, len(tr) - KCTX - 1, (BATCH,), generator=gen, device=DEVICE)
        ctx = encode_ctx(cb, tr, st); nxt = cb[tr[st + KCTX]]
        W = W + LR * (nxt.t() @ ctx) / BATCH
    return W


def ens_ppl(Ws, cb, va):
    nb = min(2000, len(va) - KCTX - 1); st = torch.arange(nb, device=DEVICE); nxt = va[st + KCTX]; best = float("inf")
    for t in TEMP_GRID:
        Ps = []
        for W in Ws:
            ctx = encode_ctx(cb, va, st); pred = ctx @ W.t(); pred = pred / (pred.norm(dim=1, keepdim=True) + 1e-8)
            cos = pred @ cb.t(); z = cos / t; z = z - z.max(dim=1, keepdim=True).values; ez = torch.exp(z)
            Ps.append(ez / (ez.sum(dim=1, keepdim=True) + 1e-30))
        P = torch.stack(Ps).mean(0); pt = P[torch.arange(nb, device=DEVICE), nxt].clamp_min(1e-12)
        best = min(best, float((-torch.log(pt)).mean()))
    return math.exp(best)


def _selftest():
    gen = torch.Generator(device=DEVICE).manual_seed(0); cb = build_cb(7, 128, gen)
    s = torch.tensor([0, 1, 2, 3], device=DEVICE)
    b1 = encode_ctx(cb, s, torch.tensor([0], device=DEVICE)); b2 = encode_ctx(cb, torch.tensor([2, 1, 0, 3], device=DEVICE), torch.tensor([0], device=DEVICE))
    assert float((b1 * b2).sum()) < 0.95, "roll-bind not order-sensitive"
    W = torch.zeros(128, 128, device=DEVICE); ctx = encode_ctx(cb, s, torch.tensor([0], device=DEVICE)); nxt = cb[3]
    W = W + torch.outer(nxt, ctx.squeeze(0)); pred = W @ ctx.squeeze(0)
    assert float(pred @ nxt / (pred.norm() * nxt.norm() + 1e-8)) > 0.5, "K3 recall"
    assert abs(math.exp(1.6094) - 5.0) < 0.01 and N == 8192
    print("[selftest] PASS: rollbind_order K3_recall ppl_exp", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed: int, n_dim: int) -> Dict:
    gen = torch.Generator(device=DEVICE).manual_seed(seed)
    txt_tr = wikitext2_char_corpus(split="train", max_chars=CORPUS)
    txt_va = wikitext2_char_corpus(split="validation", max_chars=CORPUS // 4)
    vocab = sorted(set(txt_tr) | set(txt_va)); vidx = {c: i for i, c in enumerate(vocab)}
    Vw = len(vocab)
    ids = np.array([vidx[c] for c in txt_tr], dtype=np.int64)
    ids_va = np.array([vidx.get(c, 0) for c in txt_va], dtype=np.int64)
    tr = torch.tensor(ids, device=DEVICE); va = torch.tensor(ids_va, device=DEVICE)
    cb = build_cb(Vw, n_dim, gen)
    global VOCAB; VOCAB = Vw
    idx = np.array_split(np.arange(len(tr)), J)
    Ws = [train_hebb(n_dim, cb, tr[torch.tensor(idx[i], device=DEVICE)], torch.Generator(device=DEVICE).manual_seed(seed * 50 + i)) for i in range(J)]
    single = ens_ppl([Ws[0]], cb, va); ens = ens_ppl(Ws, cb, va)
    # count baselines (numpy)
    tn = ids
    ve_arr = ids_va
    c2 = np.ones((VOCAB, VOCAB))
    for i in range(len(tn) - 1):
        c2[tn[i], tn[i + 1]] += 1
    Pb = c2 / c2.sum(axis=1, keepdims=True)
    c3 = np.ones((VOCAB * VOCAB, VOCAB))
    for i in range(len(tn) - 2):
        c3[tn[i] * VOCAB + tn[i + 1], tn[i + 2]] += 1
    Pt = c3 / c3.sum(axis=1, keepdims=True)
    ve = ve_arr; nb = min(2000, len(ve) - 2)
    big = math.exp(-np.mean([math.log(max(Pb[ve[i + 1], ve[i + 2]], 1e-12)) for i in range(nb)]))
    tri = math.exp(-np.mean([math.log(max(Pt[ve[i] * VOCAB + ve[i + 1], ve[i + 2]], 1e-12)) for i in range(nb)]))
    peak = torch.cuda.max_memory_allocated(0) / 1e9
    return {"seed": seed, "N": n_dim, "J": J, "single_ppl": float(single), "ensemble_ppl": float(ens),
            "bigram_count_ppl": float(big), "trigram_count_ppl": float(tri), "peak_gpu_gb": float(peak), "elapsed_s": 0.0}


def compute_verdict(rs) -> Tuple[str, str]:
    if not rs:
        return ("HARD_FAIL", "no results")
    e = float(np.mean([r["ensemble_ppl"] for r in rs])); s = float(np.mean([r["single_ppl"] for r in rs]))
    b = float(np.mean([r["bigram_count_ppl"] for r in rs])); t = float(np.mean([r["trigram_count_ppl"] for r in rs]))
    summary = f"single={s:.1f} ensemble={e:.1f} bigram_count={b:.1f} trigram_count(oracle)={t:.1f}"
    if e < b and e < 20:
        return ("HARD_PASS", f"HARD_PASS: substrate ensemble BEATS bigram-count + ppl<20 (adds value over counting). {summary}")
    if e < b:
        return ("MIDDLE_BAND", f"MIDDLE_BAND: ensemble beats bigram-count but ppl>=20. {summary}")
    return ("HARD_FAIL", f"HARD_FAIL: ensemble does NOT beat bigram-count. {summary}")


print(f"[config] anchor={ANCHOR_NAME} mode={RUN_MODE} seeds={SEEDS} N={N_DIM} J={J} K={KCTX}", flush=True)
if RUN_MODE == "full" and N_DIM != _N_SUFFIX:
    raise RuntimeError("PROT-018 N mismatch")
out_dir = get_output_dir(ANCHOR_NAME)
done, remaining = resumable_seeds(SEEDS, out_dir, run_config={"N": N_DIM, "run_mode": RUN_MODE, "J": J})
for seed in remaining:
    print(f"[seed={seed}] ...", flush=True); t0 = time.time(); r = run_seed(seed, N_DIM); r["elapsed_s"] = time.time() - t0
    print(f"  single={r['single_ppl']:.1f} ensemble={r['ensemble_ppl']:.1f} bigram={r['bigram_count_ppl']:.1f} trigram={r['trigram_count_ppl']:.1f} ({r['elapsed_s']:.0f}s)", flush=True)
    write_partial(out_dir, seed, r)
all_results = list(aggregate_partials(out_dir, SEEDS).values())
verdict, vmsg = compute_verdict(all_results)
print(f"\n[VERDICT] {verdict}: {vmsg}", flush=True)
peak = torch.cuda.max_memory_allocated(0) / 1e9; print(f"[GPU] peak {peak:.3f} GB", flush=True); assert peak > 0.001
metrics = {"anchor_name": ANCHOR_NAME, "verdict": verdict, "verdict_msg": vmsg, "N": N_DIM, "J": J,
           "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": all_results}
write_metrics(out_dir, metrics, all_results)
print("[metrics] written", flush=True)
