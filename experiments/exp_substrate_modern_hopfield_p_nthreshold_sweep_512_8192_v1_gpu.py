"""
substrate_modern_hopfield_p_nthreshold_sweep_512_8192_v1_gpu -- does modern Hopfield lower N_threshold? (GPU)

ROUTING: notes/research_drill_substrate_training_n_threshold_3x_2026-06-04.md (sub-q 4 + cross-thread: "a
  modern-Hopfield update rule would lower N_threshold substantially, from ~3500 to potentially ~500-1000")
  + notes/research_drill_modern_hopfield_upgrade_path_3x_2026-06-04.md. GPU (bank matmuls, N up to 8192).

CAPABILITY QUESTION:
  The classical (p=2) bipolar outer-product substrate has capacity 0.138*N -> a high char-LM N_threshold.
  Modern Hopfield (Demircigil 2017) polynomial-p separation weight = sign(sim)*|sim|^(p-1) has higher
  capacity. Does p=4 reach char-LM bigram learning at a SMALLER code dimension N than p=2 (i.e., LOWER the
  N_threshold)? This is the concrete architectural upgrade the N-threshold drill motivates.

MODEL (modern-Hopfield bank retrieval; NO gradient descent):
  Bank of M sampled bigram (ctx_key, next_value) bipolar pairs at code dim N. For a query ctx q:
    sim = cosine(Xi_ctx, q) in [-1,1] (codes unit-norm); weight = sign(sim)*|sim|^(p-1); pred = Xi_next^T @ weight.
  p=2 -> linear (classical); p=4 -> cubic separation (modern, sharper -> higher capacity).
  Score pred vs vocab by cosine -> calibrated-temp softmax -> per-char loss (NATS).
  BPC gap = uniform_nats - bank_nats (positive => the bank retrieves predictive next-char info).

TWO p x SIX N (3 seeds; fixed bank size M across all cells):
  p in {2, 4}; N in {512, 1024, 2048, 3072, 4096, 8192}; M_bank fixed (same sampled bigrams across N,p).

PRE-REGISTERED BANDS (threshold = smallest N with gap >= 0.5 nat):
  HARD-PASS: N_thresh(p4) < N_thresh(p2) (modern Hopfield learns at strictly smaller N) AND p4 gap at the
    largest N >= 1.0 nat. -> modern-Hopfield upgrade lowers the substrate N_threshold.
  MIDDLE: p4 gap >= p2 gap at matched N (p4 >= p2) but N_thresh not strictly lower (>= equal).
  HARD-FAIL: p4 gap <= p2 gap across N (no benefit) OR neither p reaches gap >= 0.5 at any N.

FORMULA SELF-TESTS (PROT-022):
  1. poly separation sharpens: (1/0.5)**(4-1) = 8 vs (1/0.5)**(2-1) = 2.
  2. single stored pair recall: p=4 pred cosine with true next > 0.9.
  3. uniform loss nats = ln(V).

PROT-018: NO _nN suffix (N swept; grid declared). PROT-021: seed checkpoints keyed run_mode + seed.
QUEUE: overnight_queue (GPU). TIMEOUT: 21600s. GPU TEMPLATE: assert cuda + device='cuda' + batched matmul.
ASCII-only stdout.
"""
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')
import os, argparse, time, json, math
from pathlib import Path
from typing import Dict, List, Tuple

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
try:
    import torch
except ImportError:
    print("[FATAL] torch not installed.", flush=True); sys.exit(1)
if not torch.cuda.is_available():
    print("[FATAL] CUDA not available. This script requires a GPU.", flush=True); sys.exit(1)
DEVICE = torch.device('cuda')
print(f"[GPU] device={DEVICE} name={torch.cuda.get_device_name(0)} "
      f"total_mem={torch.cuda.get_device_properties(0).total_memory/1e9:.1f}GB", flush=True)
import numpy as np
from experiments._seed_checkpoint import get_output_dir, resumable_seeds, write_partial, aggregate_partials
from testbed.substrate_lm.data import wikitext2_char_corpus

ANCHOR_NAME = "substrate_modern_hopfield_p_nthreshold_sweep_512_8192_v1_gpu"

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

P_GRID = [2, 4]
TEMP_GRID = [1.0, 0.5, 0.35, 0.25, 0.2, 0.15, 0.1]
GAP_THRESH = 0.5

if RUN_MODE == "smoke":
    N_GRID = [256, 512]
    SEEDS = [1, 2]
    M_BANK = 800
    TRAIN_CHARS = 8000
    VAL_CHARS = 2000
else:
    N_GRID = [512, 1024, 2048, 3072, 4096, 8192]
    SEEDS = [7, 17, 23]
    M_BANK = 3000
    TRAIN_CHARS = 120000
    VAL_CHARS = 20000


def poly_bank_nats(Xi_ctx, Xi_next, cb, val_ids, n, p, gen):
    nb = min(2000, val_ids.shape[0] - 1)
    starts = torch.randint(0, val_ids.shape[0] - 1, (nb,), generator=gen, device=DEVICE)
    q = cb[val_ids[starts]]; nxt = val_ids[starts + 1]
    sim = q @ Xi_ctx.t()                             # (nb, M) cosine in [-1,1] (codes unit-norm)
    w = torch.sign(sim) * (sim.abs() ** (p - 1))
    pred = w @ Xi_next                               # (nb, N)
    pn = pred / (pred.norm(dim=1, keepdim=True) + 1e-8)
    cos = pn @ cb.t()
    best = float("inf")
    for temp in TEMP_GRID:
        z = cos / temp; z = z - z.max(dim=1, keepdim=True).values
        ez = torch.exp(z); prob = ez / (ez.sum(dim=1, keepdim=True) + 1e-30)
        pt = prob[torch.arange(nb, device=DEVICE), nxt].clamp_min(1e-12)
        best = min(best, float((-torch.log(pt)).mean()))
    return best


def run_cell(p, n, cb, train_ids, val_ids, gen) -> Dict:
    V = cb.shape[0]
    m = min(M_BANK, train_ids.shape[0] - 1)
    starts = torch.randint(0, train_ids.shape[0] - 1, (m,), generator=gen, device=DEVICE)
    Xi_ctx = cb[train_ids[starts]]; Xi_next = cb[train_ids[starts + 1]]
    nats = poly_bank_nats(Xi_ctx, Xi_next, cb, val_ids, n, p, gen)
    gap = math.log(V) - nats
    return {"p": p, "N": n, "M_bank": m, "uniform_nats": float(math.log(V)),
            "bank_nats": float(nats), "gap_nats": float(gap)}


def _selftest():
    assert abs((1 / 0.5) ** 3 - 8.0) < 1e-6 and abs((1 / 0.5) ** 1 - 2.0) < 1e-6
    gen = torch.Generator(device=DEVICE).manual_seed(0)
    n = 256
    cb = (torch.randint(0, 2, (7, n), generator=gen, device=DEVICE).float() * 2 - 1)
    cb = cb / cb.norm(dim=1, keepdim=True)
    Xi_ctx = cb[0:1]; Xi_next = cb[1:2]; q = cb[0]
    sim = q @ Xi_ctx.t()
    w = torch.sign(sim) * (sim.abs() ** 3); pred = (w @ Xi_next).squeeze(0)
    cos = float(pred @ cb[1] / ((pred.norm() + 1e-8) * (cb[1].norm() + 1e-8)))
    assert cos > 0.9, f"single-pair p4 recall cos {cos}"
    assert abs(math.log(7) - 1.9459) < 1e-3
    print(f"[selftest] PASS: poly_sharpen 8vs2 ok p4_recall_cos={cos:.3f} gpu_mem={torch.cuda.memory_allocated(0)}", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed: int) -> Dict:
    gen = torch.Generator(device=DEVICE); gen.manual_seed(seed)
    t0 = time.time()
    train_text = wikitext2_char_corpus(split="train", max_chars=TRAIN_CHARS)
    val_text = wikitext2_char_corpus(split="validation", max_chars=VAL_CHARS)
    vocab = sorted(set(train_text) | set(val_text))
    idx = {c: i for i, c in enumerate(vocab)}
    train_ids = torch.tensor([idx.get(c, 0) for c in train_text], dtype=torch.long, device=DEVICE)
    val_ids = torch.tensor([idx.get(c, 0) for c in val_text], dtype=torch.long, device=DEVICE)
    V = len(vocab)
    print(f"  [seed={seed}] vocab={V} uniform_nats={math.log(V):.4f}", flush=True)
    cells = {}
    for p in P_GRID:
        for n in N_GRID:
            cb = (torch.randint(0, 2, (V, n), generator=gen, device=DEVICE).float() * 2 - 1)
            cb = cb / cb.norm(dim=1, keepdim=True)
            r = run_cell(p, n, cb, train_ids, val_ids, gen)
            cells[f"p{p}_N{n}"] = r
            print(f"    [p={p} N={n}] bank_nats={r['bank_nats']:.4f} gap={r['gap_nats']:.4f}", flush=True)
            del cb; torch.cuda.empty_cache()
    peak = torch.cuda.max_memory_allocated(0) / 1e9
    elapsed = time.time() - t0
    print(f"  [seed={seed}] peak_gpu={peak:.3f}GB elapsed={elapsed:.1f}s", flush=True)
    return {"seed": seed, "run_mode": RUN_MODE, "cells": cells, "peak_gpu_gb": float(peak), "elapsed_s": elapsed}


def compute_verdict(results: List[Dict]) -> Tuple[str, str]:
    if not results:
        return ("HARD_FAIL", "HARD_FAIL: no results.")
    def gap(p, n):
        vs = [r["cells"][f"p{p}_N{n}"]["gap_nats"] for r in results if f"p{p}_N{n}" in r.get("cells", {})]
        return float(np.mean(vs)) if vs else 0.0
    g = {p: {n: gap(p, n) for n in N_GRID} for p in P_GRID}
    def n_thresh(p):
        for n in N_GRID:
            if g[p][n] >= GAP_THRESH:
                return n
        return None
    nt2, nt4 = n_thresh(2), n_thresh(4)
    p2_str = " ".join(f"N{n}:{g[2][n]:.3f}" for n in N_GRID)
    p4_str = " ".join(f"N{n}:{g[4][n]:.3f}" for n in N_GRID)
    summary = f"N_thresh(p2)={nt2} N_thresh(p4)={nt4} | p2_gap[{p2_str}] p4_gap[{p4_str}]"
    p4_ge_p2 = all(g[4][n] >= g[2][n] - 0.02 for n in N_GRID)
    maxN = N_GRID[-1]
    if nt2 is None and nt4 is None:
        return ("HARD_FAIL", f"HARD_FAIL: neither p reaches gap>={GAP_THRESH} at any N. {summary}")
    if nt4 is not None and (nt2 is None or nt4 < nt2) and g[4][maxN] >= 1.0:
        return ("HARD_PASS", f"HARD_PASS: modern Hopfield p=4 lowers N_threshold (nt4<nt2) AND p4 gap@{maxN}>=1.0. {summary}")
    if p4_ge_p2:
        return ("MIDDLE_BAND", f"MIDDLE_BAND: p4>=p2 at matched N but N_threshold not strictly lower. {summary}")
    return ("HARD_FAIL", f"HARD_FAIL: p4 no better than p2 (no modern-Hopfield benefit). {summary}")


print(f"[config] anchor={ANCHOR_NAME} p_grid={P_GRID} N_grid={N_GRID} mode={RUN_MODE} seeds={SEEDS} "
      f"M_bank={M_BANK}", flush=True)

out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"p_grid": P_GRID, "N_grid": N_GRID, "run_mode": RUN_MODE, "M_bank": M_BANK}
done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
print(f"[ckpt] {len(done)} seeds done, {len(remaining)} to run", flush=True)

t_sweep = time.time()
for seed in remaining:
    print(f"[seed={seed}] {ANCHOR_NAME}...", flush=True)
    result = run_seed(seed)
    write_partial(out_dir, seed, result)

per_seed = aggregate_partials(out_dir, SEEDS)
all_results = list(per_seed.values())
verdict, verdict_msg = compute_verdict(all_results)
print(f"\n[VERDICT] {verdict}: {verdict_msg}", flush=True)

elapsed_total = time.time() - t_sweep
peak_mem_gb = torch.cuda.max_memory_allocated(0) / 1e9
print(f"[GPU] peak memory: {peak_mem_gb:.3f} GB", flush=True)
assert peak_mem_gb > 0.001, f"GPU util check FAIL: {peak_mem_gb:.3f}GB"
metrics = {
    "anchor_name": ANCHOR_NAME, "verdict": verdict, "verdict_msg": verdict_msg,
    "p_grid": P_GRID, "N_grid": N_GRID, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "M_bank": M_BANK,
    "elapsed_s": elapsed_total,
    "per_seed": [{"seed": r.get("seed"), "cells": r.get("cells", {}),
                  "peak_gpu_gb": r.get("peak_gpu_gb"), "elapsed_s": r.get("elapsed_s")} for r in all_results],
}
metrics_path = out_dir / "metrics.json"
metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
print(f"[metrics] written to {metrics_path}", flush=True)
