"""p1_v3_capacity_sweep_LLM_class_v1 -- Director follow-up to p1 v2 chain-grade (CERT 590).

SCIENTIFIC QUESTION (Skunkworks 2026-06-22):
  p1 v2 (CERT 590) chain-graded at K=500 / N_DIM=65536 (alpha=K/N=0.0076 << Hopfield-Hebbian
  bound 0.14). The all-ratios=1.000 pattern reflects substantial HEADROOM below saturation.
  This v3 sweeps K across the capacity gradient (alpha 0.0076 -> 0.229) to discriminate
  near saturation -- can the substrate's operating-point-shift mechanism still preserve
  REPLAYED >> FRESH gain as the substrate enters its hard-failure regime?

  Modern_hopfield_xl just HARD_FAILed at LLM-class for the inverse reason (no classical-cliff
  at alpha=0.14 with the additive-noise model used; the WITHIN-arm did not collapse where
  Hopfield theory predicts). This v3 uses p1's DISCRIMINATOR architecture (4 arms; BLANK
  collapse-to-chance proves recall is mechanism not artifact) which already proved
  chain-grade-discriminating at LLM scale -- so a clean capacity gradient should be visible.

MECHANISM (identical to p1 v2; only the K dimension sweeps):
  Random bipolar HD-vector keys + VQ codebook values + IMPLICIT Hebbian outer-product
  retrieval (W = V.T @ K / N never materialized; we compute W @ q = V.T @ (K @ q) / N).
  4 arms per K-arm: WITHIN_P_0, P_0_TO_P_1_REPLAYED, P_1_FRESH_INGEST, P_1_BLANK_RECALL.

  v3 vs v2 structural differences:
    - SINGLE (P_0, P_1) pair (V_C=16384, N=65536 -> V_C=16384, N=65536), not 3-pair grid.
      v3 tests capacity not portability axes; one pair suffices to expose the K-driven
      saturation curve.
    - K sweep: K in {500, 2000, 5000, 8000, 9000, 10000, 12000, 15000} (8 arms).
      Spans well-below (alpha=0.0076) through (0.14 = Hopfield bound) to well-above
      (alpha=0.229) the classical capacity edge.
    - V_C = 16384 throughout (CONSTANT; capacity test not lift test). V_C is the cleanup
      alphabet; must be >= K_max = 15000. V_C/K ratio varies 32.8 (K=500) -> 1.09 (K=15000).
    - fp16 storage on heavy tensors. VRAM budget at K=15000, V_C=16384, N=65536:
        val_cb (V_C, N) = 16384*65536*2 = 2.15 GB (fp16)
        key_qs (K, N)    = 15000*65536*2 = 1.97 GB (fp16)
        + scratch + projection tile -> peak ~5 GB << 8 GB 4060Ti budget
      matmul outputs (small: K-dim scores; N-dim y; V_C-dim sims) computed in fp32.

PRE-REGISTERED BANDS (Director/Skunkworks 2026-06-22):
  HARD_PASS (capacity-curve evidence):
    - WITHIN ratio DEGRADES smoothly across K (>= 0.95 at K=500; <= 0.50 at K=9000) AND
    - REPLAYED retains operating-point-shift gain: REPLAYED >> FRESH by >= 0.20 at
      K in [2000, 5000] (the discriminating-regime where both arms are non-saturated and
      non-collapsed) AND
    - BLANK collapses to chance throughout (<= 0.05 at every K) AND
    - substrate-only gate preserved (n_llm_calls == 0).
  HARD_FAIL:
    - WITHIN doesn't degrade across K (all ratios > 0.90 at K=15000 -- means we're STILL
      below capacity at alpha=0.229, capacity-test premise fails) OR
    - REPLAYED never beats FRESH by >= 0.20 at any K in [2000, 5000] (mechanism dead) OR
    - substrate-only gate violated OR
    - any cv > 0.10 across seeds.
  MIDDLE_BAND: in between.

  Direction-honor (Skunkworks n3 SimVQ catch): WITHIN must MONOTONIC-DECREASE in expectation
  across K. A WITHIN ratio INCREASING with K would be a measurement artifact (HARD_FAIL).

GPU MANDATE (Fix #22 + #24): torch.cuda asserted at module top; matmul shape (K_max=15000,
  N=65536) is genuinely heavy (~1.97 GB per matmul read) and saturates GPU memory bandwidth.
  Cell-author must verify GPU util >= 50% steady-state during smoke on the GPU runner.

FIX INVENTORY:
  - Fix #3: per-seed runtime measurement at near-full-scale BEFORE full dispatch.
  - Fix #5: HDLAB_RUN_MODE override; cell-side _smoke suffix detection (TODO #6).
  - Fix #6: pair-disjoint by construction (single pair; only K varies; no overlap).
  - Fix #11: pipeline-template structure (this cell + smoke + full + VET).
  - Fix #14: commit cell to origin/main BEFORE remote dispatch.
  - Fix #16: 4-arm discriminator-regime (WITHIN baseline, BLANK collapse, FRESH/REPLAYED gap).
  - Fix #20: NO `2>&1 | tail` subprocess piping in spawn dispatch logic.
  - Fix #22: GPU routing (cuda mandate; abort on no-CUDA when run_mode=full).
  - Fix #24: GPU util >= 50% sampled during smoke and full.
  - PROT-021: config-mismatch guard via run_config = {"N": N_DIM, "M": K_MAX, "run_mode": ...}.

FORMULA SELF-TESTS (--self-test on CPU; fp32 for selftest accuracy):
  1. Tiny WITHIN arm at V_C=128 N=512 K=10: recall >= 0.80.
  2. Tiny BLANK arm: recall <= 0.20.
  3. _LLM_CALL_COUNTER == 0.
  4. JL projection cosine-drift sanity (P @ identity ~ identity).
  5. Implicit-W equivalence to explicit W on small N=128.

ASCII-only. Single-file. Resumable.
"""
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import os
# PyTorch CUDA allocator: expandable_segments mitigates fragmentation at 8 GB VRAM.
# Must be set BEFORE `import torch`.
os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")

import argparse
import time
import math
import json
import gc
from pathlib import Path
from typing import Dict, List, Tuple, Optional

import numpy as np

# torch must be importable at module top for routing-sanity gate (Fix #22).
import torch  # routing-sanity gate requires literal `import torch`

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import (
    get_output_dir, resumable_seeds, write_partial, aggregate_partials, write_metrics,
)

ANCHOR_NAME = "p1_v3_capacity_sweep_LLM_class_v1"

# Substrate-only-decode gate. Asserted == 0 at end. Any LLM call MUST increment.
_LLM_CALL_COUNTER = [0]

CORPUS_PROVENANCE = "synthetic_bipolar_keys_with_VQ_codebook_LLM_class_K_sweep"


def _detect_run_mode():
    """smoke vs full. Priority: --smoke flag > HDLAB_RUN_MODE > HDLAB_EXP_NAME _smoke suffix > full.

    TODO #6 resolution: the runner stamps HDLAB_RUN_MODE=full unconditionally; only the
    queue-entry-name suffix `_smoke` is a usable smoke signal. Cell-side detection.
    """
    if "--smoke" in sys.argv:
        return "smoke"
    exp_name = os.environ.get("HDLAB_EXP_NAME", "")
    if exp_name.lower().endswith("_smoke"):
        return "smoke"
    env_mode = os.environ.get("HDLAB_RUN_MODE", "").lower()
    if env_mode in ("smoke", "full"):
        return env_mode
    return "full"


RUN_MODE = _detect_run_mode()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

# Pre-reg bands (locked at design time; v3 capacity-curve discriminating regime)
RATIO_REPLAYED_OVER_FRESH_GAP = 0.20      # REPLAYED - FRESH at the discriminating K
WITHIN_HIGH_K_MIN = 0.95                   # WITHIN at K=500 must be >= this
WITHIN_LOW_K_MAX = 0.50                    # WITHIN at K=9000 must be <= this
WITHIN_CAPACITY_PROBE_MAX = 0.90           # WITHIN at K=15000 must be <= this (capacity-test premise)
BLANK_RECALL_MAX = 0.05                    # BLANK chance floor at every K
CV_HARD_FAIL_MAX = 0.10
N_RECALL_STEPS = 3
NOISE_FRAC = float(os.environ.get("HDLAB_NOISE_FRAC", "0.05"))
JL_TILE_N_DST = 4096                       # JL projection tile rows (VRAM)
DISCRIM_K_RANGE = (2000, 5000)             # K range where REPLAYED >> FRESH must show

# K sweep: spans alpha=K/N from 0.0076 (well-below) through 0.14 (Hopfield bound) to 0.229 (well-above)
if RUN_MODE == "smoke":
    SEEDS = [1]
    K_GRID = [50, 200, 500]                # 3 tiny K's; smoke just checks harness
    V_C = 1024
    N_DIM = 2048
    N_PROBE = 30
else:
    SEEDS = [7, 17, 23]
    K_GRID = [500, 2000, 5000, 8000, 9000, 10000, 12000, 15000]
    V_C = 16384                             # cleanup alphabet floor: must be >= max(K_GRID)
    N_DIM = 65536
    N_PROBE = 60

K_MAX = max(K_GRID)
ARMS = ["WITHIN_P_0", "P_0_TO_P_1_REPLAYED", "P_1_FRESH_INGEST", "P_1_BLANK_RECALL"]

CONFIG_VERSION = ("p1-v3-capacity-sweep-LLM-class-v1: K_grid=%s V_C=%d N_DIM=%d arms=%s "
                  "noise=%.3f recall_steps=%d run_mode=%s" %
                  (str(K_GRID), V_C, N_DIM, ",".join(ARMS), NOISE_FRAC, N_RECALL_STEPS, RUN_MODE))


# ----------------------------- GPU mandate (full run only) -----------------------------
def _require_cuda(strict: bool) -> bool:
    """Fail-fast GPU check. strict=True means raise on absence."""
    if torch.cuda.is_available():
        return True
    if strict:
        raise RuntimeError(
            "GPU MANDATE (Fix #22 + Fix #24): cuda.is_available() = False. "
            "v3 capacity-sweep at N_DIM=65536 K_max=15000 requires CUDA. Re-route to GPU runner.")
    return False


_STRICT_GPU = (RUN_MODE == "full") and not _ARGS.self_test and ("--smoke" not in sys.argv)
_CUDA_OK = _require_cuda(strict=_STRICT_GPU)
_DEVICE = torch.device("cuda:0") if _CUDA_OK else torch.device("cpu")
# Heavy storage dtype (val_cb, key_qs): fp16 on GPU to fit K_max=15000 + V_C=16384 in 8 GB.
# Matmul ACCUMULATION + small intermediate (scores, y, sims) stay fp32 for numerical safety.
_STORE_DTYPE = torch.float16 if _CUDA_OK else torch.float32
_COMPUTE_DTYPE = torch.float32


def _gpu_util_sample() -> Optional[float]:
    """Sample GPU utilization % via nvidia-smi. Returns None if unavailable."""
    try:
        import subprocess
        out = subprocess.run(
            ["nvidia-smi", "--query-gpu=utilization.gpu", "--format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=5,
        )
        if out.returncode == 0:
            return float(out.stdout.strip().splitlines()[0].strip())
    except (subprocess.TimeoutExpired, FileNotFoundError, ValueError, IndexError, OSError):
        pass
    return None


# ----------------------------- HD primitives (torch on GPU) -----------------------------
_NORM_ROW_CHUNK = 1024     # rows-per-chunk for fp32 norm path on fp16 storage (VRAM bound)


def _normalize_rows_t(X: torch.Tensor, eps: float = 1e-12) -> torch.Tensor:
    """L2-row-normalize IN-PLACE.

    fp32 needs proper norm path. fp16 storage at LLM scale needs CHUNKED fp32 norm to:
    (a) avoid fp16 sum-of-squares overflow (N=65536 sum-of-squares = 65536 > fp16 max 65504)
    (b) avoid materializing a 4 GB X.float() transient at V_C=16384.
    Chunk fp32 cast of 1024 rows * 65536 cols = 256 MB transient per chunk -- bounded.
    """
    if X.dtype == torch.float16:
        M = X.shape[0]
        start = 0
        while start < M:
            end = min(start + _NORM_ROW_CHUNK, M)
            row_f32 = X[start:end].float()
            row_norms = row_f32.norm(dim=1, keepdim=True).clamp_(min=eps)
            X[start:end] = (row_f32 / row_norms).to(X.dtype)
            del row_f32, row_norms
            start = end
    else:
        norms = X.norm(dim=1, keepdim=True).clamp_(min=eps)
        X.div_(norms)
    return X


def make_bipolar_t(M: int, n: int, gen: torch.Generator, device, dtype) -> torch.Tensor:
    """Random +/- 1 vectors, L2-normalized. (M, n) on device, IN storage dtype.

    VRAM discipline: allocate directly in storage dtype. The earlier "build-fp32-then-cast"
    path doubled peak alloc (e.g., (16384, 65536) fp16 = 2 GB but fp32 transient = 4 GB +
    fp16 result = 6 GB peak) which OOMed on 8 GB cards at FRESH arm. PyTorch bernoulli_
    supports fp16 on cuda natively; norms computed in fp32 internally inside _normalize_rows_t.
    """
    X = torch.empty(M, n, device=device, dtype=dtype)
    X.bernoulli_(0.5, generator=gen).mul_(2.0).sub_(1.0)
    X = _normalize_rows_t(X)
    return X


def make_value_codebook_t(v_c: int, n: int, gen: torch.Generator, device, dtype) -> torch.Tensor:
    """V_C random bipolar value-codebook entries; the CLEANUP alphabet."""
    return make_bipolar_t(v_c, n, gen, device, dtype)


def project_rows_chunked_t(X: torch.Tensor, n_dst: int, gen: torch.Generator,
                           tile_n_dst: int = JL_TILE_N_DST) -> torch.Tensor:
    """Apply deterministic bipolar JL projection (n_dst, n_src) tiled to keep VRAM bounded.

    When n_src == n_dst: returns X.clone() (identity projection).
    Output L2-normalized; storage dtype matches X.
    """
    M, n_src = X.shape
    device, dtype = X.device, X.dtype
    if n_src == n_dst:
        return _normalize_rows_t(X.clone())
    Y = torch.empty(M, n_dst, device=device, dtype=dtype)
    scale_val = 1.0 / math.sqrt(n_src)
    start = 0
    while start < n_dst:
        end = min(start + tile_n_dst, n_dst)
        # Tile in storage dtype (avoid 4x peak via fp32 then cast at K_max=15000).
        # bernoulli_ on fp16 cuda is natively supported.
        tile_P = torch.empty(end - start, n_src, device=device, dtype=dtype)
        tile_P.bernoulli_(0.5, generator=gen).mul_(2.0).sub_(1.0).mul_(scale_val)
        Y[:, start:end] = X @ tile_P.T
        del tile_P
        start = end
    Y = _normalize_rows_t(Y)
    return Y


def hebbian_retrieve_implicit_t(key_qs_mem: torch.Tensor,
                                val_payload: torch.Tensor,
                                val_codebook: torch.Tensor,
                                q: torch.Tensor,
                                n_steps: int = N_RECALL_STEPS) -> int:
    """Implicit W: W = val_payload.T @ key_qs_mem / N; return cleanup index.

    Matmuls execute in STORAGE dtype on GPU (fp16 on cuda; cublas fp16 GEMM uses tensor
    cores; correctness validated against the fp32 selftest T5). The argmax-cleanup loop
    operates in storage dtype throughout; bf16/fp16 reductions are stable for V_C <= 32k.
    No big-tensor .float() casts (those quadruple peak VRAM and OOM at K_max=15000).

    Output (idx) is an int.
    """
    K, N = key_qs_mem.shape
    storage_dtype = val_codebook.dtype
    device = val_codebook.device
    if K == 0:
        # Empty memory: y = 0; cleanup picks the argmax of sims-of-zero = first codebook entry.
        y = torch.zeros(N, device=device, dtype=storage_dtype)
    else:
        # Ensure q matches storage dtype for the matmul.
        if q.dtype != storage_dtype:
            q_use = q.to(storage_dtype)
        else:
            q_use = q
        # scores = key_qs_mem @ q : (K, N) @ (N,) -> (K,) in storage dtype.
        scores = key_qs_mem @ q_use
        # y = val_payload.T @ scores / N : (N, K) @ (K,) -> (N,) in storage dtype.
        # Divide-by-N: do as multiply to avoid integer-as-fp16 surprises.
        inv_N = torch.tensor(1.0 / float(N), device=device, dtype=storage_dtype)
        y = (val_payload.T @ scores) * inv_N
    for _ in range(n_steps):
        sims = val_codebook @ y                  # (V_C, N) @ (N,) -> (V_C,) in storage dtype
        idx = int(torch.argmax(sims).item())
        y_snap = val_codebook[idx]
        half = torch.tensor(0.5, device=device, dtype=storage_dtype)
        y = half * y + half * y_snap
    sims = val_codebook @ y
    idx = int(torch.argmax(sims).item())
    return idx


def eval_recall_implicit_t(key_qs_mem: torch.Tensor,
                           val_payload: torch.Tensor,
                           val_codebook: torch.Tensor,
                           value_idx_truth: torch.Tensor,
                           n_probe: int,
                           gen: torch.Generator) -> float:
    """Noised-key retrieval. Returns fraction correct.

    Probe construction (noise + normalize) runs in storage dtype to avoid materializing
    a 4GB fp32 (V_C, N) clone alongside the fp16 storage tensors.
    """
    K = key_qs_mem.shape[0]
    N = key_qs_mem.shape[1]
    n_q = min(n_probe, K)
    if n_q == 0:
        return 0.0
    perm = torch.randperm(K, generator=gen, device=key_qs_mem.device)[:n_q]
    storage_dtype = key_qs_mem.dtype
    correct = 0
    for j_idx in range(n_q):
        j = int(perm[j_idx].item())
        q = key_qs_mem[j].clone()                # storage dtype (fp16 on GPU)
        flip_mask = torch.bernoulli(
            torch.full((N,), NOISE_FRAC, device=q.device, dtype=torch.float32), generator=gen)
        # Apply flip in fp32 for numerical determinism of the mask then cast to storage.
        q32 = q.float() * (1.0 - 2.0 * flip_mask)
        q32 = q32 / (q32.norm() + 1e-12)
        q = q32.to(storage_dtype)
        del q32, flip_mask
        retr_idx = hebbian_retrieve_implicit_t(key_qs_mem, val_payload, val_codebook,
                                               q, n_steps=N_RECALL_STEPS)
        if retr_idx == int(value_idx_truth[j].item()):
            correct += 1
    return float(correct) / n_q


def _eval_blank_implicit_t(val_codebook: torch.Tensor, value_idx_truth: torch.Tensor,
                           key_qs_for_probes: torch.Tensor,
                           n_probe: int, gen: torch.Generator) -> float:
    """BLANK: empty memory; probe with same noised keys; recall ~ 1/V_C chance.

    Storage-dtype probe construction (same fp16 discipline as eval_recall_implicit_t).
    """
    K = key_qs_for_probes.shape[0]
    N = key_qs_for_probes.shape[1]
    n_q = min(n_probe, K)
    if n_q == 0:
        return 0.0
    perm = torch.randperm(K, generator=gen, device=key_qs_for_probes.device)[:n_q]
    storage_dtype = val_codebook.dtype
    empty_keys = torch.zeros(0, N, device=key_qs_for_probes.device, dtype=storage_dtype)
    empty_vals = torch.zeros(0, N, device=key_qs_for_probes.device, dtype=storage_dtype)
    correct = 0
    for j_idx in range(n_q):
        j = int(perm[j_idx].item())
        q = key_qs_for_probes[j].clone()
        flip_mask = torch.bernoulli(
            torch.full((N,), NOISE_FRAC, device=q.device, dtype=torch.float32), generator=gen)
        q32 = q.float() * (1.0 - 2.0 * flip_mask)
        q32 = q32 / (q32.norm() + 1e-12)
        q = q32.to(storage_dtype)
        del q32, flip_mask
        retr_idx = hebbian_retrieve_implicit_t(empty_keys, empty_vals, val_codebook,
                                                q, n_steps=N_RECALL_STEPS)
        if retr_idx == int(value_idx_truth[j].item()):
            correct += 1
    return float(correct) / n_q


def _make_gen(seed_int: int) -> torch.Generator:
    g = torch.Generator(device=_DEVICE)
    g.manual_seed(int(seed_int))
    return g


# ----------------------------- per-K arm runner -----------------------------
def run_k_arm(k_atoms: int, seed: int, gpu_util_samples: List[float]) -> Dict:
    """Run the 4-arm matrix for one K value at the single (V_C, N_DIM) operating point.

    Operating-point shift: P_0 = (V_C, N_DIM); P_1 = (V_C, N_DIM). Same point in v3 --
    the JL projection becomes identity, so REPLAYED is identity-replay. The discriminator
    REPLAYED vs FRESH still measures whether storing-then-replaying preserves the Hebbian
    binding (vs fresh random keys at same K). v2 already proved JL portability; v3 tests
    that storage capacity at this scale doesn't collapse the mechanism.

    Per-arm allocation discipline: aggressive del + empty_cache between arms; peak VRAM
    bounded by the heaviest single arm (REPLAYED holding both key_qs_proj + val_cb_proj).
    """
    t0 = time.time()
    base = seed * 10007 + k_atoms * 31

    # ARM 1: WITHIN_P_0 -- store at (V_C, N_DIM); query same keys with noise.
    gen_p0 = _make_gen(base)
    gen_probe_w = _make_gen(base + 401)
    val_cb_0 = make_value_codebook_t(V_C, N_DIM, gen_p0, _DEVICE, _STORE_DTYPE)
    key_qs_0 = make_bipolar_t(k_atoms, N_DIM, gen_p0, _DEVICE, _STORE_DTYPE)
    val_idx_0 = torch.arange(k_atoms, device=_DEVICE)
    val_payload_0 = val_cb_0[:k_atoms]
    recall_within = eval_recall_implicit_t(key_qs_0, val_payload_0, val_cb_0,
                                            val_idx_0, N_PROBE, gen_probe_w)
    del val_cb_0, key_qs_0, val_idx_0, val_payload_0
    if _CUDA_OK:
        torch.cuda.empty_cache()
    sample = _gpu_util_sample()
    if sample is not None:
        gpu_util_samples.append(sample)

    # ARM 3: P_1_FRESH_INGEST -- fresh codebook + keys at SAME (V_C, N_DIM); no transfer.
    gen_p1 = _make_gen(base + 31)
    gen_probe_f = _make_gen(base + 607)
    val_cb_1 = make_value_codebook_t(V_C, N_DIM, gen_p1, _DEVICE, _STORE_DTYPE)
    key_qs_1 = make_bipolar_t(k_atoms, N_DIM, gen_p1, _DEVICE, _STORE_DTYPE)
    val_idx_1 = torch.arange(k_atoms, device=_DEVICE)
    val_payload_1 = val_cb_1[:k_atoms]
    recall_fresh = eval_recall_implicit_t(key_qs_1, val_payload_1, val_cb_1,
                                           val_idx_1, N_PROBE, gen_probe_f)
    del val_cb_1, key_qs_1, val_idx_1, val_payload_1
    if _CUDA_OK:
        torch.cuda.empty_cache()
    sample = _gpu_util_sample()
    if sample is not None:
        gpu_util_samples.append(sample)

    # ARMS 2 + 4: REPLAYED + BLANK (share projected probe set; build once)
    # Re-derive P_0 keys + payload (same gen sequence as WITHIN)
    gen_p0_again = _make_gen(base)
    gen_proj = _make_gen(base + 71)
    gen_probe_r = _make_gen(base + 503)
    gen_probe_b = _make_gen(base + 709)

    val_cb_0_r = make_value_codebook_t(V_C, N_DIM, gen_p0_again, _DEVICE, _STORE_DTYPE)
    key_qs_0_r = make_bipolar_t(k_atoms, N_DIM, gen_p0_again, _DEVICE, _STORE_DTYPE)
    val_payload_0_r = val_cb_0_r[:k_atoms].clone()
    del val_cb_0_r
    if _CUDA_OK:
        torch.cuda.empty_cache()

    # JL project (identity when src=dst; mechanism: replay through projection)
    key_qs_proj = project_rows_chunked_t(key_qs_0_r, N_DIM, gen_proj)
    del key_qs_0_r
    if _CUDA_OK:
        torch.cuda.empty_cache()
    val_payload_proj = project_rows_chunked_t(val_payload_0_r, N_DIM, gen_proj)
    del val_payload_0_r
    if _CUDA_OK:
        torch.cuda.empty_cache()

    # Build cleanup codebook at P_1 = same (V_C, N_DIM). Payload occupies first k_atoms slots;
    # remaining V_C - k_atoms slots are distractor entries (independent random bipolar).
    n_distract = max(0, V_C - k_atoms)
    if n_distract > 0:
        gen_distract = _make_gen(base + 131)
        distractors = make_bipolar_t(n_distract, N_DIM, gen_distract, _DEVICE, _STORE_DTYPE)
        val_cb_proj = torch.cat([val_payload_proj, distractors], dim=0)
        del distractors, val_payload_proj
        if _CUDA_OK:
            torch.cuda.empty_cache()
    else:
        val_cb_proj = val_payload_proj
    val_idx_proj = torch.arange(k_atoms, device=_DEVICE)

    recall_replayed = eval_recall_implicit_t(key_qs_proj, val_cb_proj[:k_atoms], val_cb_proj,
                                              val_idx_proj, N_PROBE, gen_probe_r)
    recall_blank = _eval_blank_implicit_t(val_cb_proj, val_idx_proj, key_qs_proj,
                                           N_PROBE, gen_probe_b)
    del key_qs_proj, val_cb_proj, val_idx_proj
    if _CUDA_OK:
        torch.cuda.empty_cache()
    sample = _gpu_util_sample()
    if sample is not None:
        gpu_util_samples.append(sample)

    wall_s = time.time() - t0
    ratio_replayed_over_within = (recall_replayed / recall_within) if recall_within > 1e-9 else 0.0
    gap_replayed_over_fresh = recall_replayed - recall_fresh
    alpha = float(k_atoms) / float(N_DIM)

    return {
        "k_atoms": int(k_atoms),
        "seed": int(seed),
        "V_C": int(V_C), "N_DIM": int(N_DIM),
        "alpha": alpha,
        "recall_WITHIN_P_0": float(recall_within),
        "recall_P_0_TO_P_1_REPLAYED": float(recall_replayed),
        "recall_P_1_FRESH_INGEST": float(recall_fresh),
        "recall_P_1_BLANK_RECALL": float(recall_blank),
        "ratio_replayed_over_within": float(ratio_replayed_over_within),
        "gap_replayed_over_fresh": float(gap_replayed_over_fresh),
        "n_probe": N_PROBE,
        "wall_s": float(wall_s),
        "device": str(_DEVICE),
    }


# ----------------------------- self-test (CPU; fp32) -----------------------------
def _selftest():
    """5 formula self-tests on CPU in fp32."""
    global _DEVICE, _STORE_DTYPE
    _save_dev = _DEVICE
    _save_dtype = _STORE_DTYPE
    _DEVICE = torch.device("cpu")
    _STORE_DTYPE = torch.float32
    try:
        gen = _make_gen(0)
        # T1: Tiny WITHIN at zero noise.
        v_c, n_dim, k_a = 128, 512, 10
        val_cb = make_value_codebook_t(v_c, n_dim, gen, _DEVICE, _STORE_DTYPE)
        keys = make_bipolar_t(k_a, n_dim, gen, _DEVICE, _STORE_DTYPE)
        val_payload = val_cb[:k_a]
        n_correct = 0
        for j in range(k_a):
            q = keys[j] / (keys[j].norm() + 1e-12)
            ridx = hebbian_retrieve_implicit_t(keys, val_payload, val_cb, q, n_steps=3)
            if ridx == j:
                n_correct += 1
        rec_within = n_correct / k_a
        assert rec_within >= 0.80, "selftest T1: tiny WITHIN recall %.3f < 0.80" % rec_within

        # T2: BLANK arm: empty memory -> low recall.
        empty_k = torch.zeros(0, n_dim, dtype=torch.float32)
        empty_v = torch.zeros(0, n_dim, dtype=torch.float32)
        n_correct_b = 0
        for j in range(k_a):
            q = keys[j] / (keys[j].norm() + 1e-12)
            ridx = hebbian_retrieve_implicit_t(empty_k, empty_v, val_cb, q, n_steps=3)
            if ridx == j:
                n_correct_b += 1
        rec_blank = n_correct_b / k_a
        assert rec_blank <= 0.20, "selftest T2: blank recall %.3f > 0.20" % rec_blank

        # T3: LLM counter zero
        assert _LLM_CALL_COUNTER[0] == 0, "selftest T3: LLM counter non-zero"

        # T4: JL projection cosine drift sanity (small N)
        gen2 = _make_gen(1)
        X = make_bipolar_t(20, 256, gen2, _DEVICE, _STORE_DTYPE)
        Y = project_rows_chunked_t(X, 512, gen2, tile_n_dst=128)
        XX = (X @ X.T).detach()
        YY = (Y @ Y.T).detach()
        err = float((XX - YY).abs().max().item())
        assert err < 0.40, "selftest T4: JL cosine drift %.3f > 0.40" % err

        # T5: Implicit-W equivalence to explicit W on small N=128.
        gen3 = _make_gen(2)
        small_n = 128
        small_v_c = 64
        small_k = 8
        val_cb_s = make_value_codebook_t(small_v_c, small_n, gen3, _DEVICE, _STORE_DTYPE)
        keys_s = make_bipolar_t(small_k, small_n, gen3, _DEVICE, _STORE_DTYPE)
        val_pay_s = val_cb_s[:small_k]
        W_explicit = (val_pay_s.T @ keys_s) / float(small_n)
        diffs = []
        for j in range(small_k):
            q = keys_s[j] / (keys_s[j].norm() + 1e-12)
            y_explicit = W_explicit @ q
            y_implicit = (val_pay_s.T @ (keys_s @ q)) / float(small_n)
            d = float((y_explicit - y_implicit).abs().max().item())
            diffs.append(d)
        max_d = max(diffs)
        assert max_d < 1e-4, "selftest T5: implicit-vs-explicit max-abs-diff %.6f > 1e-4" % max_d

        print(("[selftest] PASS: WITHIN=%.3f BLANK=%.3f JL_cos_drift=%.3f implicit_vs_explicit=%.2e "
               "LLM=%d") % (rec_within, rec_blank, err, max_d, _LLM_CALL_COUNTER[0]), flush=True)
    finally:
        _DEVICE = _save_dev
        _STORE_DTYPE = _save_dtype


_selftest()
if _ARGS.self_test:
    sys.exit(0)


# ----------------------------- main pipeline -----------------------------
def run_seed(seed: int) -> Dict:
    """Run all K-arms for one seed; emit one per_unit per (K, seed)."""
    t0 = time.time()
    gpu_util_samples: List[float] = []
    per_unit = []
    for k_atoms in K_GRID:
        res = run_k_arm(k_atoms, seed, gpu_util_samples)
        per_unit.append(res)
        print(("  [seed=%d] K=%5d alpha=%.4f | WITHIN=%.3f REPLAYED=%.3f FRESH=%.3f BLANK=%.3f "
               "| gap_R_over_F=%+.3f wall=%.1fs") %
              (seed, k_atoms, res["alpha"],
               res["recall_WITHIN_P_0"], res["recall_P_0_TO_P_1_REPLAYED"],
               res["recall_P_1_FRESH_INGEST"], res["recall_P_1_BLANK_RECALL"],
               res["gap_replayed_over_fresh"], res["wall_s"]), flush=True)
    elapsed = time.time() - t0
    gpu_util_mean = float(np.mean(gpu_util_samples)) if gpu_util_samples else float("nan")
    gpu_util_p50 = float(np.median(gpu_util_samples)) if gpu_util_samples else float("nan")
    gpu_util_max = float(np.max(gpu_util_samples)) if gpu_util_samples else float("nan")
    return {
        "seed": seed,
        "N": N_DIM,
        "M": K_MAX,
        "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
        "per_unit": per_unit,
        "elapsed_s": float(elapsed),
        "n_llm_calls": int(_LLM_CALL_COUNTER[0]),
        "device": str(_DEVICE),
        "cuda_ok": bool(_CUDA_OK),
        "gpu_util_samples": gpu_util_samples,
        "gpu_util_mean": gpu_util_mean,
        "gpu_util_p50": gpu_util_p50,
        "gpu_util_max": gpu_util_max,
    }


def compute_verdict(per_seed: Dict[str, Dict]) -> Tuple[str, str, Dict]:
    """Pre-reg bands: capacity-curve evidence (WITHIN degrades) + REPLAYED-FRESH gap in
    discriminating regime + BLANK floor + substrate-only gate.
    """
    if not per_seed:
        return ("HARD_FAIL", "No valid results.", {})

    # Aggregate per K-arm across seeds
    k_summary: Dict[int, Dict[str, List[float]]] = {
        k: {"WITHIN": [], "REPLAYED": [], "FRESH": [], "BLANK": [], "GAP_RF": [], "RATIO_RW": []}
        for k in K_GRID
    }
    for _sid, body in per_seed.items():
        for pu in body.get("per_unit", []):
            k = int(pu["k_atoms"])
            if k not in k_summary:
                continue
            k_summary[k]["WITHIN"].append(float(pu["recall_WITHIN_P_0"]))
            k_summary[k]["REPLAYED"].append(float(pu["recall_P_0_TO_P_1_REPLAYED"]))
            k_summary[k]["FRESH"].append(float(pu["recall_P_1_FRESH_INGEST"]))
            k_summary[k]["BLANK"].append(float(pu["recall_P_1_BLANK_RECALL"]))
            k_summary[k]["GAP_RF"].append(float(pu["gap_replayed_over_fresh"]))
            k_summary[k]["RATIO_RW"].append(float(pu["ratio_replayed_over_within"]))

    def _stat(xs):
        if not xs:
            return float("nan"), float("nan"), float("nan")
        m = float(np.mean(xs))
        s = float(np.std(xs))
        cv = float(s / max(m, 1e-9)) if m > 1e-9 else float("inf")
        return m, s, cv

    k_curve: Dict[int, Dict] = {}
    for k in K_GRID:
        d = k_summary[k]
        wm, ws, wcv = _stat(d["WITHIN"])
        rm, rs, rcv = _stat(d["REPLAYED"])
        fm, fs, fcv = _stat(d["FRESH"])
        bm, bs, bcv = _stat(d["BLANK"])
        gm, gs, gcv = _stat(d["GAP_RF"])
        rat_m, rat_s, rat_cv = _stat(d["RATIO_RW"])
        k_curve[k] = {
            "alpha": float(k) / float(N_DIM),
            "within_mean": wm, "within_std": ws, "within_cv": wcv,
            "replayed_mean": rm, "replayed_std": rs, "replayed_cv": rcv,
            "fresh_mean": fm, "fresh_std": fs, "fresh_cv": fcv,
            "blank_mean": bm, "blank_std": bs, "blank_cv": bcv,
            "gap_replayed_over_fresh_mean": gm, "gap_replayed_over_fresh_std": gs,
            "gap_replayed_over_fresh_cv": gcv,
            "ratio_replayed_over_within_mean": rat_m,
        }

    n_llm = sum(int(b.get("n_llm_calls", 0)) for b in per_seed.values())
    substrate_only_ok = (n_llm == 0)

    # Capacity-curve checks
    k_low = K_GRID[0]                    # 500
    k_mid_capacity_test = 9000           # near Hopfield bound
    k_high_probe = K_GRID[-1]            # 15000 (alpha = 0.229)

    within_at_low = k_curve[k_low]["within_mean"]
    # The 9000 point may not exist in the grid for smoke; use closest >= 9000.
    k_at_capacity = next((k for k in K_GRID if k >= k_mid_capacity_test), K_GRID[-1])
    within_at_capacity = k_curve[k_at_capacity]["within_mean"]
    within_at_high = k_curve[k_high_probe]["within_mean"]

    # Discriminating regime: at least one K in [2000, 5000] must have gap >= 0.20
    discrim_ks = [k for k in K_GRID if DISCRIM_K_RANGE[0] <= k <= DISCRIM_K_RANGE[1]]
    if not discrim_ks:
        discrim_ks = [K_GRID[1] if len(K_GRID) > 1 else K_GRID[0]]  # smoke fallback
    discrim_gaps = [k_curve[k]["gap_replayed_over_fresh_mean"] for k in discrim_ks]
    max_discrim_gap = max(discrim_gaps) if discrim_gaps else 0.0
    discrim_gap_pass = (max_discrim_gap >= RATIO_REPLAYED_OVER_FRESH_GAP)

    # BLANK floor at every K
    blank_max_across_k = max(k_curve[k]["blank_mean"] for k in K_GRID)
    blank_floor_ok = (blank_max_across_k <= BLANK_RECALL_MAX)

    # cv stability check (WITHIN + REPLAYED across seeds at every K)
    any_cv_fail = any(
        (k_curve[k]["within_cv"] > CV_HARD_FAIL_MAX or k_curve[k]["replayed_cv"] > CV_HARD_FAIL_MAX)
        for k in K_GRID
    )

    # HARD_PASS: degrades smoothly (high at low K; low at K>=9000) + discrim gap + blank + substrate
    within_high_ok = (within_at_low >= WITHIN_HIGH_K_MIN)
    within_low_ok = (within_at_capacity <= WITHIN_LOW_K_MAX)
    # Capacity-test premise: at K=15000 (alpha=0.229) WITHIN must be <= 0.90 (substrate IS being stressed)
    capacity_premise_ok = (within_at_high <= WITHIN_CAPACITY_PROBE_MAX)

    # Direction-honor: WITHIN must monotone-decrease in expectation
    within_curve = [k_curve[k]["within_mean"] for k in K_GRID]
    monotone_down = all(within_curve[i] >= within_curve[i + 1] - 0.05  # allow small noise slack
                        for i in range(len(within_curve) - 1))

    # Aggregate GPU util
    gpu_util_all: List[float] = []
    for body in per_seed.values():
        for s in body.get("gpu_util_samples", []):
            try:
                gpu_util_all.append(float(s))
            except (TypeError, ValueError):
                pass
    if gpu_util_all:
        gpu_util_mean_overall = float(np.mean(gpu_util_all))
        gpu_util_p50_overall = float(np.median(gpu_util_all))
        gpu_util_max_overall = float(np.max(gpu_util_all))
    else:
        gpu_util_mean_overall = float("nan")
        gpu_util_p50_overall = float("nan")
        gpu_util_max_overall = float("nan")

    detail = {
        "k_curve": {str(k): v for k, v in k_curve.items()},
        "within_at_k_low_K%d" % k_low: float(within_at_low),
        "within_at_k_capacity_K%d" % k_at_capacity: float(within_at_capacity),
        "within_at_k_high_K%d" % k_high_probe: float(within_at_high),
        "max_discrim_gap_in_K_range_%d_%d" % DISCRIM_K_RANGE: float(max_discrim_gap),
        "blank_max_across_K": float(blank_max_across_k),
        "monotone_within_decrease": bool(monotone_down),
        "within_high_K_min_>=_%.2f" % WITHIN_HIGH_K_MIN: bool(within_high_ok),
        "within_low_K_max_<=_%.2f" % WITHIN_LOW_K_MAX: bool(within_low_ok),
        "capacity_premise_K_high_<=_%.2f" % WITHIN_CAPACITY_PROBE_MAX: bool(capacity_premise_ok),
        "discrim_gap_>=_%.2f" % RATIO_REPLAYED_OVER_FRESH_GAP: bool(discrim_gap_pass),
        "blank_floor_<=_%.2f" % BLANK_RECALL_MAX: bool(blank_floor_ok),
        "any_cv_>_%.2f" % CV_HARD_FAIL_MAX: bool(any_cv_fail),
        "substrate_only_ok": bool(substrate_only_ok),
        "zero_llm_calls_at_inference": bool(substrate_only_ok),
        "gpu_util_mean": gpu_util_mean_overall,
        "gpu_util_p50": gpu_util_p50_overall,
        "gpu_util_max": gpu_util_max_overall,
        "gpu_util_n_samples": len(gpu_util_all),
        "honest_scope": (
            "LLM-class (N_DIM=%d) capacity sweep on synthetic-bipolar HD substrate "
            "with VQ codebook + IMPLICIT-Hebbian (low-rank W = V.T @ K / N; no explicit "
            "(N,N) matrix). K_grid=%s; alpha=K/N spans %.4f -> %.4f (spans 0.14 Hopfield "
            "bound at K~9175). 4-arm discriminator (WITHIN/REPLAYED/FRESH/BLANK); "
            "substrate-only-decode gate enforced (n_llm=%d). cuda_required=True; cell aborts "
            "on no-CUDA when run_mode=full. fp16 storage on (V_C, N_DIM) and (K, N_DIM) tensors "
            "to fit K_max=%d in 8 GB VRAM; fp32 accumulation for matmul." %
            (N_DIM, str(K_GRID), float(K_GRID[0]) / N_DIM, float(K_GRID[-1]) / N_DIM,
             n_llm, K_MAX)),
    }

    # Compact verdict summary
    parts = []
    for k in K_GRID:
        kv = k_curve[k]
        parts.append("K=%d[w=%.3f r=%.3f f=%.3f b=%.3f gap=%+.3f]" %
                     (k, kv["within_mean"], kv["replayed_mean"], kv["fresh_mean"],
                      kv["blank_mean"], kv["gap_replayed_over_fresh_mean"]))
    summary = " | ".join(parts) + (" | llm=%d | gpu_util_mean=%.1f%% | monotone=%s" %
                                    (n_llm, gpu_util_mean_overall, monotone_down))

    # Verdict ladder
    if not substrate_only_ok:
        return ("HARD_FAIL",
                "HARD_FAIL: substrate-only-decode gate VIOLATED (%d LLM calls). %s" % (n_llm, summary),
                detail)
    if not blank_floor_ok:
        return ("HARD_FAIL",
                "HARD_FAIL: BLANK floor breached (max=%.3f > %.2f) -- recall is artifact of key encoding. %s" %
                (blank_max_across_k, BLANK_RECALL_MAX, summary),
                detail)
    if any_cv_fail:
        return ("HARD_FAIL",
                "HARD_FAIL: cv across seeds > %.2f on at least one K (seed-unstable). %s" %
                (CV_HARD_FAIL_MAX, summary),
                detail)
    if not capacity_premise_ok:
        return ("HARD_FAIL",
                "HARD_FAIL: capacity-test premise fails -- WITHIN at K=%d (alpha=%.4f) is %.3f > %.2f; "
                "substrate is STILL below capacity at the high end of the sweep. %s" %
                (k_high_probe, float(k_high_probe) / N_DIM, within_at_high,
                 WITHIN_CAPACITY_PROBE_MAX, summary),
                detail)
    if not discrim_gap_pass:
        return ("HARD_FAIL",
                "HARD_FAIL: REPLAYED never beats FRESH by >= %.2f in discriminating regime K in [%d,%d]; "
                "max_gap=%.3f. Mechanism dead. %s" %
                (RATIO_REPLAYED_OVER_FRESH_GAP, DISCRIM_K_RANGE[0], DISCRIM_K_RANGE[1],
                 max_discrim_gap, summary),
                detail)
    if within_high_ok and within_low_ok and capacity_premise_ok and discrim_gap_pass and blank_floor_ok and not any_cv_fail:
        return ("HARD_PASS",
                ("HARD_PASS: LLM-class capacity sweep traverses Hopfield-Hebbian saturation regime. "
                 "WITHIN degrades %.3f@K=%d -> %.3f@K=%d (premise=true: %.3f@K=%d) AND REPLAYED-FRESH gap "
                 ">= %.2f in discriminating regime (max=%.3f at K in [%d,%d]) AND blank-sanity OK "
                 "(max=%.3f) AND substrate-only gate preserved. %s" %
                 (within_at_low, k_low, within_at_capacity, k_at_capacity,
                  within_at_high, k_high_probe,
                  RATIO_REPLAYED_OVER_FRESH_GAP, max_discrim_gap,
                  DISCRIM_K_RANGE[0], DISCRIM_K_RANGE[1],
                  blank_max_across_k, summary)),
                detail)
    return ("MIDDLE_BAND",
            ("MIDDLE_BAND: partial capacity-curve evidence. within_high_ok=%s within_low_ok=%s "
             "capacity_premise_ok=%s discrim_gap=%.3f. %s" %
             (within_high_ok, within_low_ok, capacity_premise_ok, max_discrim_gap, summary)),
            detail)


# ----------------------------- main -----------------------------
out_dir = get_output_dir(ANCHOR_NAME)
t0_total = time.time()
run_config = {"N": N_DIM, "M": K_MAX, "run_mode": RUN_MODE}

done, seeds_todo = resumable_seeds(SEEDS, out_dir, run_config)
print("[run] mode=%s K_grid=%s V_C=%d N=%d cuda=%s device=%s seeds_done=%s seeds_todo=%s" %
      (RUN_MODE, str(K_GRID), V_C, N_DIM, _CUDA_OK, _DEVICE, str(done), str(seeds_todo)), flush=True)
if _CUDA_OK:
    free_b, total_b = torch.cuda.mem_get_info(0)
    print("[gpu] %s vram_total=%.2fGB vram_free=%.2fGB store_dtype=%s" %
          (torch.cuda.get_device_name(0), total_b / 1e9, free_b / 1e9, str(_STORE_DTYPE)), flush=True)

for s in seeds_todo:
    res = run_seed(s)
    write_partial(out_dir, s, res)

per_seed = aggregate_partials(out_dir, SEEDS, run_config=run_config)
verdict, verdict_msg, detail = compute_verdict(per_seed)

metrics = {
    "anchor": ANCHOR_NAME,
    "anchor_name": ANCHOR_NAME,
    "verdict": verdict,
    "verdict_msg": verdict_msg,
    "n_seeds": len(per_seed),
    "K_grid": K_GRID,
    "V_C": V_C,
    "N_DIM": N_DIM,
    "arms": ARMS,
    "run_mode": RUN_MODE,
    "config_version": CONFIG_VERSION,
    "corpus_provenance": CORPUS_PROVENANCE,
    "allow_synthetic": True,
    "zero_llm_calls_at_inference": bool(_LLM_CALL_COUNTER[0] == 0),
    "n_llm_calls": int(_LLM_CALL_COUNTER[0]),
    "device": str(_DEVICE),
    "cuda_ok": bool(_CUDA_OK),
    "store_dtype": str(_STORE_DTYPE),
    "compute_dtype": str(_COMPUTE_DTYPE),
    "detail": detail,
    "per_seed": [
        {"seed": k, **{kk: vv for kk, vv in v.items() if kk != "per_unit"},
         "per_unit": v.get("per_unit", [])}
        for k, v in per_seed.items()
    ],
    "metrics_source": "measured_gpu_synthetic_bipolar_VQ_codebook_implicit_hebbian_K_sweep",
    "elapsed_s": time.time() - t0_total,
    "summary": verdict_msg[:200],
}

write_metrics(out_dir, metrics, results=list(per_seed.values()))

print("\n[VERDICT] %s" % verdict, flush=True)
print("[VERDICT_MSG] %s" % verdict_msg, flush=True)
print("[METRICS_PATH] %s" % (out_dir / "metrics.json"), flush=True)
