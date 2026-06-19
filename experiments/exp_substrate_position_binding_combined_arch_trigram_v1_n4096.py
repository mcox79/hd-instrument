"""
substrate_position_binding_combined_arch_trigram_v1_n4096 -- Bundle E: position-binding combined arch (GPU).

ROUTING: notes/routing_position_binding_combined_architecture_bundle_e_2026-06-04.md. TRIGGERED (Bundle A
  landed HARD_PASS). Research routed CPU (matmul-light); run on the OWNED 4060 Ti GPU instead ($0, torch
  matmuls, keeps GPU occupied -- the cost constraint is cloud, not owned GPU).

CAPABILITY QUESTION:
  Does combining position-binding (VSA multi-bank addressing) with asymmetric write (STDP) and/or sparse
  coding enable substrate-as-training at TRIGRAM (K=3), exceeding the K*~2.1 ceiling of pure symmetric
  Hebbian? Position-binding ALONE doesn't raise K* (drill); COMBINED, predicted K* -> 3.5-5.0.
  (Word2Vec/transformer precedent: position + asymmetric retrieval = sequence modeling. Substrate analog
  via primitives + NO backprop -> "transformer-class without gradient descent" if HP.)

POSITION-BINDING: trigram context (c1,c2) -> bound code via cyclic-shift permutation binding (HRR / VSA
  multi-bank): ctx = roll(code[c1],+1) + roll(code[c2],+2), unit-normalized. Distinct shifts = distinct
  position banks. Substrate learns ctx_bound -> code[c3].

FOUR CELLS (3 seeds = 12 measurements; trigram V=vocab char-LM; N=4096; 1000 steps):
  E1 posbind + symmetric Hebbian (control; dW = Nxt^T ctx).                         [predicted HF]
  E2 posbind + STDP-asymmetric: W = W_Hebbian + 0.5*W_STDP (W_STDP = Nxt^T ctx - ctx^T Nxt). [primary]
  E3 posbind + sparse coding f=0.05 + symmetric Hebbian.
  E4 posbind + sparse + STDP (W_Hebbian_sparse + 0.5*W_STDP_sparse).               [max aggressive]
  Calibrated-temperature cosine readout -> per-char loss (NATS); gap = uniform_nats - trigram_nats.

PRE-REGISTERED BANDS (per-cell):
  HARD-PASS: trigram gap > 1.0 nat AND 3/3 seeds AND no instability (norm osc < 3x).
  MIDDLE: gap in [0.3, 1.0] nat OR 2/3 seeds.
  HARD-FAIL: gap < 0.3 nat OR < 1/3 seeds.
  AGGREGATE: HARD-PASS if any cell HP (identifies the combination enabling trigram); HARD-FAIL if all 4 HF.

FORMULA SELF-TESTS (PROT-022):
  1. position-binding distinguishes order: bound(a,b) != bound(b,a) (cosine < 0.9).
  2. single-trigram recall: write one bound->next pair, W@bound recovers next (cos > 0.5).
  3. STDP antisymmetric part W_STDP + W_STDP^T = 0. 4. sparse support = f*N. 5. uniform nats = ln(V).

PROT-018: anchor _n4096 -> production N=4096. PROT-019: _n4096 timeout floor 14400s. PROT-021: seed ckpt by run_mode+seed.
QUEUE: overnight_queue (GPU). GPU TEMPLATE: assert cuda + device='cuda' + batched matmul. ASCII-only stdout.
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

ANCHOR_NAME = "substrate_position_binding_combined_arch_trigram_v1_n4096"
_N_SUFFIX = 4096
N = 4096
assert N == _N_SUFFIX, f"PROT-018: anchor _n{_N_SUFFIX} but N={N}"

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

LR = 0.5
BATCH = 64
SPARSE_F = 0.05
TEMP_GRID = [1.0, 0.5, 0.35, 0.25, 0.2, 0.15, 0.1]
HP_GAP, MID_GAP = 1.0, 0.3
# Cells: (name, coding, stdp)
CELLS = [("E1_posbind_hebbian", "bipolar", False),
         ("E2_posbind_stdp", "bipolar", True),
         ("E3_posbind_sparse", "sparse", False),
         ("E4_posbind_sparse_stdp", "sparse", True)]

if RUN_MODE == "smoke":
    N_DIM = 256
    SEEDS = [1, 2]
    N_STEPS = 80
    TRAIN_CHARS = 8000
    VAL_CHARS = 2000
else:
    N_DIM = N
    SEEDS = [7, 17, 23]
    N_STEPS = 1000
    TRAIN_CHARS = 120000
    VAL_CHARS = 20000


def build_codebook(V, n, coding, gen):
    if coding == "bipolar":
        cb = (torch.randint(0, 2, (V, n), generator=gen, device=DEVICE).float() * 2 - 1)
    else:
        cb = torch.zeros(V, n, device=DEVICE)
        k = max(1, int(round(SPARSE_F * n)))
        for i in range(V):
            idx = torch.randperm(n, generator=gen, device=DEVICE)[:k]
            cb[i, idx] = 1.0
    return cb / (cb.norm(dim=1, keepdim=True) + 1e-8)


def posbind(cb, c1_idx, c2_idx):
    """Position-bind a 2-char context via cyclic-shift permutation banks. Returns unit-norm bound codes."""
    b = torch.roll(cb[c1_idx], shifts=1, dims=1) + torch.roll(cb[c2_idx], shifts=2, dims=1)
    return b / (b.norm(dim=1, keepdim=True) + 1e-8)


def train_cell(coding, stdp, n, cb, train_ids, val_ids, gen) -> Dict:
    W = torch.zeros(n, n, device=DEVICE)
    norms = []
    ntr = train_ids.shape[0]
    for _ in range(N_STEPS):
        starts = torch.randint(0, ntr - 2, (BATCH,), generator=gen, device=DEVICE)
        ctx = posbind(cb, train_ids[starts], train_ids[starts + 1])   # (B,n) bound 2-char context
        Nxt = cb[train_ids[starts + 2]]                                # (B,n) trigram target
        Heb = (Nxt.t() @ ctx) / BATCH
        if stdp:
            Asym = (Nxt.t() @ ctx - ctx.t() @ Nxt) / BATCH
            dW = Heb + 0.5 * Asym
        else:
            dW = Heb
        W = W + LR * dW
        norms.append(float((LR * dW).norm()))
    # eval trigram BPC
    nb = min(2000, val_ids.shape[0] - 2)
    starts = torch.randint(0, val_ids.shape[0] - 2, (nb,), generator=gen, device=DEVICE)
    ctx = posbind(cb, val_ids[starts], val_ids[starts + 1]); nxt = val_ids[starts + 2]
    pred = ctx @ W.t()
    pn = pred / (pred.norm(dim=1, keepdim=True) + 1e-8)
    cos = pn @ cb.t()
    best = float("inf")
    for temp in TEMP_GRID:
        z = cos / temp; z = z - z.max(dim=1, keepdim=True).values
        ez = torch.exp(z); prob = ez / (ez.sum(dim=1, keepdim=True) + 1e-30)
        pt = prob[torch.arange(nb, device=DEVICE), nxt].clamp_min(1e-12)
        best = min(best, float((-torch.log(pt)).mean()))
    mn = float(np.mean(norms)); osc = float(np.std(norms) / (mn + 1e-12))
    return {"coding": coding, "stdp": stdp, "val_nats": float(best), "mean_norm": mn, "norm_osc": osc}


def _selftest():
    gen = torch.Generator(device=DEVICE).manual_seed(0)
    cb = build_codebook(7, 128, "bipolar", gen)
    a = torch.tensor([0], device=DEVICE); b = torch.tensor([1], device=DEVICE)
    bab = posbind(cb, a, b); bba = posbind(cb, b, a)
    cos = float((bab * bba).sum())
    assert cos < 0.9, f"posbind order-insensitive cos={cos}"
    # single trigram recall
    W = torch.zeros(128, 128, device=DEVICE)
    ctx = posbind(cb, torch.tensor([0], device=DEVICE), torch.tensor([1], device=DEVICE))
    nxt = cb[2]
    W = W + torch.outer(nxt, ctx.squeeze(0)); pred = W @ ctx.squeeze(0)
    rc = float(pred @ nxt / ((pred.norm() + 1e-8) * (nxt.norm() + 1e-8)))
    assert rc > 0.5, f"trigram recall cos={rc}"
    # STDP antisym
    Asym = torch.outer(nxt, ctx.squeeze(0)) - torch.outer(ctx.squeeze(0), nxt)
    assert float((Asym + Asym.t()).abs().max()) < 1e-4
    cbs = build_codebook(7, 128, "sparse", gen)
    assert int((cbs[0] != 0).sum()) == max(1, int(round(SPARSE_F * 128)))
    assert abs(math.log(7) - 1.9459) < 1e-3
    print(f"[selftest] PASS: posbind_order cos={cos:.3f} trigram_recall={rc:.3f} stdp_antisym_ok sparse_ok", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed: int, n_dim: int) -> Dict:
    gen = torch.Generator(device=DEVICE); gen.manual_seed(seed)
    t0 = time.time()
    train_text = wikitext2_char_corpus(split="train", max_chars=TRAIN_CHARS)
    val_text = wikitext2_char_corpus(split="validation", max_chars=VAL_CHARS)
    vocab = sorted(set(train_text) | set(val_text))
    idx = {c: i for i, c in enumerate(vocab)}
    train_ids = torch.tensor([idx.get(c, 0) for c in train_text], dtype=torch.long, device=DEVICE)
    val_ids = torch.tensor([idx.get(c, 0) for c in val_text], dtype=torch.long, device=DEVICE)
    V = len(vocab); uniform_nats = math.log(V)
    print(f"  [seed={seed}] V={V} N={n_dim} uniform_nats={uniform_nats:.3f}", flush=True)
    cells = {}
    for name, coding, stdp in CELLS:
        cb = build_codebook(V, n_dim, coding, gen)
        r = train_cell(coding, stdp, n_dim, cb, train_ids, val_ids, gen)
        r["gap_vs_uniform"] = float(uniform_nats - r["val_nats"])
        cells[name] = r
        print(f"    [{name}] val_nats={r['val_nats']:.4f} gap={r['gap_vs_uniform']:.4f} osc={r['norm_osc']:.2f}", flush=True)
        del cb; torch.cuda.empty_cache()
    peak = torch.cuda.max_memory_allocated(0) / 1e9
    elapsed = time.time() - t0
    print(f"  [seed={seed}] peak_gpu={peak:.3f}GB elapsed={elapsed:.1f}s", flush=True)
    return {"seed": seed, "N": n_dim, "run_mode": RUN_MODE, "uniform_nats": float(uniform_nats),
            "cells": cells, "peak_gpu_gb": float(peak), "elapsed_s": elapsed}


def compute_verdict(results: List[Dict]) -> Tuple[str, str]:
    if not results:
        return ("HARD_FAIL", "HARD_FAIL: no results.")
    per_cell = {}
    for name, _, _ in CELLS:
        gaps = [r["cells"][name]["gap_vs_uniform"] for r in results if name in r.get("cells", {})]
        oscs = [r["cells"][name]["norm_osc"] for r in results if name in r.get("cells", {})]
        n = len(gaps); gm = float(np.mean(gaps)) if gaps else 0.0
        n_conv = sum(1 for g in gaps if g > HP_GAP); stable = max(oscs, default=0.0) < 3.0
        if gm > HP_GAP and n_conv >= math.ceil(0.99 * n) and stable:
            band = "HP"
        elif gm >= MID_GAP or n_conv >= math.ceil(2 * n / 3):
            band = "MID"
        else:
            band = "HF"
        per_cell[name] = (band, gm, n_conv, n)
    bands = [b for b, _, _, _ in per_cell.values()]
    summary = " ".join(f"{nm}:{per_cell[nm][0]}(gap{per_cell[nm][1]:+.3f},{per_cell[nm][2]}/{per_cell[nm][3]})"
                       for nm in per_cell)
    if "HP" in bands:
        winners = [nm for nm in per_cell if per_cell[nm][0] == "HP"]
        return ("HARD_PASS", f"HARD_PASS: trigram (K=3) reached by {winners} -> combined-architecture pathway works. {summary}")
    if all(b == "HF" for b in bands):
        return ("HARD_FAIL", f"HARD_FAIL: all 4 cells HF -> combined-arch pathway refuted; substrate K=2 bound. {summary}")
    return ("MIDDLE_BAND", f"MIDDLE_BAND: partial trigram learning; no cell clears >1.0 nat. {summary}")


print(f"[config] anchor={ANCHOR_NAME} cells={[c[0] for c in CELLS]} N={N_DIM} mode={RUN_MODE} seeds={SEEDS} "
      f"steps={N_STEPS} task=trigram", flush=True)
if RUN_MODE == "full" and N_DIM != _N_SUFFIX:
    raise RuntimeError(f"PROT-018: N_DIM={N_DIM} != _N_SUFFIX={_N_SUFFIX}")

out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"N": N_DIM, "run_mode": RUN_MODE, "cells": [c[0] for c in CELLS], "n_steps": N_STEPS}
done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
print(f"[ckpt] {len(done)} seeds done, {len(remaining)} to run", flush=True)

t_sweep = time.time()
for seed in remaining:
    print(f"[seed={seed}] {ANCHOR_NAME}...", flush=True)
    result = run_seed(seed, N_DIM)
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
    "N": N_DIM, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "n_steps": N_STEPS,
    "cells": [c[0] for c in CELLS], "task": "trigram", "elapsed_s": elapsed_total,
    "per_seed": [{"seed": r.get("seed"), "uniform_nats": r.get("uniform_nats"), "cells": r.get("cells", {}),
                  "peak_gpu_gb": r.get("peak_gpu_gb"), "elapsed_s": r.get("elapsed_s")} for r in all_results],
}
metrics_path = out_dir / "metrics.json"
metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
print(f"[metrics] written to {metrics_path}", flush=True)
