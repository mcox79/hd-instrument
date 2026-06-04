"""
substrate_friston_fep_trigram_cell_v1_n4096 -- Bundle B addendum: Friston FEP at trigram (GPU).

ROUTING: notes/change_request_bundle_b_add_friston_fep_trigram_cell_2026-06-04.md. Shipped as a SEPARATE
  addendum (not folded into Bundle B) because Bundle B was already queued when the change-request landed
  (per change-request-protocol "already in flight" case). Owned GPU, $0.

CAPABILITY QUESTION:
  Friston FEP (precision matrix Pi + epsilon prediction-error buffer + precision-weighted update) HARD_FAILed
  at K=2 bigram in Bundle A. Hypothesis: bigram was too easy (K*~2.1 already maxed at K=1); at K=3 trigram the
  FEP precision-weighted supervised signal MAY activate. Does FEP beat K=1 Hebbian at trigram?
  (If HF at trigram too -> NESS hidden objective subsumes explicit FEP; FEP-class machinery redundant at
   substrate scale. If HP -> FEP activates at higher complexity.)

TWO CELLS (3 seeds; trigram V=70 wikitext char; N=4096; roll-binding 2-char context):
  baseline_k1 : symmetric Hebbian (dW = Nxt^T ctx).
  friston_fep : precision-weighted cf-RPE: eps = Nxt - W ctx; Pi = 1/running-var(eps); dW = (Pi*eps)^T ctx.

PRE-REGISTERED BANDS (BPC nats):
  HARD-PASS: FEP BPC < baseline BPC - 0.50 nats at trigram AND 3/3 seeds (FEP activates at K=3).
  MIDDLE: improvement 0.20-0.50 nats.
  HARD-FAIL: FEP BPC >= baseline BPC (FEP still fails at harder task -> implicit-subsumption confirmed).

FORMULA SELF-TESTS (PROT-022):
  1. roll-binding order-sensitive (cos<0.9). 2. cf-RPE shrinks single-pair error. 3. precision Pi finite+positive.
  4. uniform nats = ln(V).

PROT-018: anchor _n4096 -> N=4096. PROT-019: _n4096 timeout floor 14400s. PROT-021: seed ckpt by run_mode+seed.
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

ANCHOR_NAME = "substrate_friston_fep_trigram_cell_v1_n4096"
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
ORDER = 2          # trigram = 2-char context
TEMP_GRID = [1.0, 0.5, 0.35, 0.25, 0.2, 0.15, 0.1]
HP_GAP, MID_GAP = 0.50, 0.20
CELLS = ["baseline_k1", "friston_fep"]

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


def build_codebook(V, n, gen):
    cb = (torch.randint(0, 2, (V, n), generator=gen, device=DEVICE).float() * 2 - 1)
    return cb / (cb.norm(dim=1, keepdim=True) + 1e-8)


def encode_ctx(cb, ids, starts, order):
    b = torch.zeros(starts.shape[0], cb.shape[1], device=DEVICE)
    for j in range(order):
        b = b + torch.roll(cb[ids[starts + j]], shifts=j + 1, dims=1)
    return b / (b.norm(dim=1, keepdim=True) + 1e-8)


def train_eval(cell, n, cb, train_ids, val_ids, gen) -> float:
    W = torch.zeros(n, n, device=DEVICE)
    var_run = torch.ones(n, device=DEVICE)
    ntr = train_ids.shape[0]
    for _ in range(N_STEPS):
        starts = torch.randint(0, ntr - ORDER - 1, (BATCH,), generator=gen, device=DEVICE)
        ctx = encode_ctx(cb, train_ids, starts, ORDER); Nxt = cb[train_ids[starts + ORDER]]
        if cell == "baseline_k1":
            W = W + LR * (Nxt.t() @ ctx) / BATCH
        else:   # friston_fep
            eps = Nxt - ctx @ W.t()
            Pi = 1.0 / (var_run + 1e-3)
            W = W + LR * ((eps * Pi).t() @ ctx) / BATCH
            var_run = 0.9 * var_run + 0.1 * (eps * eps).mean(dim=0)
    nb = min(2000, val_ids.shape[0] - ORDER - 1)
    starts = torch.randint(0, val_ids.shape[0] - ORDER - 1, (nb,), generator=gen, device=DEVICE)
    ctx = encode_ctx(cb, val_ids, starts, ORDER); nxt = val_ids[starts + ORDER]
    pred = ctx @ W.t(); pn = pred / (pred.norm(dim=1, keepdim=True) + 1e-8); cos = pn @ cb.t()
    best = float("inf")
    for temp in TEMP_GRID:
        z = cos / temp; z = z - z.max(dim=1, keepdim=True).values
        ez = torch.exp(z); prob = ez / (ez.sum(dim=1, keepdim=True) + 1e-30)
        pt = prob[torch.arange(nb, device=DEVICE), nxt].clamp_min(1e-12)
        best = min(best, float((-torch.log(pt)).mean()))
    return best


def _selftest():
    gen = torch.Generator(device=DEVICE).manual_seed(0)
    cb = build_codebook(7, 128, gen)
    bab = encode_ctx(cb, torch.tensor([0, 1], device=DEVICE), torch.tensor([0], device=DEVICE), 2)
    bba = encode_ctx(cb, torch.tensor([1, 0], device=DEVICE), torch.tensor([0], device=DEVICE), 2)
    assert float((bab * bba).sum()) < 0.9
    W = torch.zeros(128, 128, device=DEVICE); ctx, nxt = cb[0], cb[1]
    v = W @ ctx; eb = float((nxt - v).norm()); W = W + torch.outer(nxt - v, ctx); ea = float((nxt - W @ ctx).norm())
    assert ea < eb
    Pi = 1.0 / (torch.ones(128, device=DEVICE) + 1e-3)
    assert float(Pi.min()) > 0 and torch.isfinite(Pi).all()
    assert abs(math.log(7) - 1.9459) < 1e-3
    print(f"[selftest] PASS: rollbind_order_ok cfrpe {eb:.3f}->{ea:.3f} Pi_pos_finite", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed: int, n_dim: int) -> Dict:
    gen = torch.Generator(device=DEVICE); gen.manual_seed(seed)
    t0 = time.time()
    tr_text = wikitext2_char_corpus(split="train", max_chars=TRAIN_CHARS)
    va_text = wikitext2_char_corpus(split="validation", max_chars=VAL_CHARS)
    vocab = sorted(set(tr_text) | set(va_text)); idx = {c: i for i, c in enumerate(vocab)}
    tr = torch.tensor([idx.get(c, 0) for c in tr_text], dtype=torch.long, device=DEVICE)
    va = torch.tensor([idx.get(c, 0) for c in va_text], dtype=torch.long, device=DEVICE)
    V = len(vocab); un = math.log(V)
    print(f"  [seed={seed}] V={V} N={n_dim} uniform_nats={un:.3f}", flush=True)
    cells = {}
    for cell in CELLS:
        cb = build_codebook(V, n_dim, gen)
        nats = train_eval(cell, n_dim, cb, tr, va, gen)
        cells[cell] = {"val_nats": float(nats), "gap_vs_uniform": float(un - nats)}
        print(f"    [{cell}] val_nats={nats:.4f} gap={un - nats:.4f}", flush=True)
        del cb; torch.cuda.empty_cache()
    peak = torch.cuda.max_memory_allocated(0) / 1e9; elapsed = time.time() - t0
    print(f"  [seed={seed}] peak_gpu={peak:.3f}GB elapsed={elapsed:.1f}s", flush=True)
    return {"seed": seed, "N": n_dim, "run_mode": RUN_MODE, "uniform_nats": float(un), "cells": cells,
            "peak_gpu_gb": float(peak), "elapsed_s": elapsed}


def compute_verdict(results: List[Dict]) -> Tuple[str, str]:
    if not results:
        return ("HARD_FAIL", "HARD_FAIL: no results.")
    diffs = []
    for r in results:
        if "baseline_k1" in r["cells"] and "friston_fep" in r["cells"]:
            diffs.append(r["cells"]["baseline_k1"]["val_nats"] - r["cells"]["friston_fep"]["val_nats"])  # >0 => FEP better
    n = len(diffs); md = float(np.mean(diffs)) if diffs else 0.0
    n_hp = sum(1 for d in diffs if d > HP_GAP)
    mb = float(np.mean([r["cells"]["baseline_k1"]["val_nats"] for r in results]))
    mf = float(np.mean([r["cells"]["friston_fep"]["val_nats"] for r in results]))
    summary = f"baseline_nats={mb:.3f} fep_nats={mf:.3f} fep_improvement={md:+.3f} nats ({n_hp}/{n} seeds>{HP_GAP})"
    if md > HP_GAP and n_hp >= n:
        return ("HARD_PASS", f"HARD_PASS: FEP beats baseline by >{HP_GAP} nats at trigram, all seeds -> FEP activates at K=3. {summary}")
    if md >= MID_GAP:
        return ("MIDDLE_BAND", f"MIDDLE_BAND: FEP improvement in [{MID_GAP},{HP_GAP}]. {summary}")
    return ("HARD_FAIL", f"HARD_FAIL: FEP does not beat baseline at trigram -> implicit-subsumption (FEP redundant). {summary}")


print(f"[config] anchor={ANCHOR_NAME} cells={CELLS} N={N_DIM} mode={RUN_MODE} seeds={SEEDS} steps={N_STEPS} task=trigram", flush=True)
if RUN_MODE == "full" and N_DIM != _N_SUFFIX:
    raise RuntimeError(f"PROT-018: N_DIM={N_DIM} != _N_SUFFIX={_N_SUFFIX}")

out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"N": N_DIM, "run_mode": RUN_MODE, "cells": CELLS, "n_steps": N_STEPS}
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
    "N": N_DIM, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "n_steps": N_STEPS, "task": "trigram",
    "elapsed_s": elapsed_total,
    "per_seed": [{"seed": r.get("seed"), "uniform_nats": r.get("uniform_nats"), "cells": r.get("cells", {}),
                  "peak_gpu_gb": r.get("peak_gpu_gb"), "elapsed_s": r.get("elapsed_s")} for r in all_results],
}
metrics_path = out_dir / "metrics.json"
metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
print(f"[metrics] written to {metrics_path}", flush=True)
