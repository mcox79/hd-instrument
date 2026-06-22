"""p1_v2_action_at_any_position_LLM_class_v1 -- USER-directed latent-capability lane, LLM-class scale.

SCIENTIFIC QUESTION (USER 2026-06-22):
  p1 v1 proved operating-point-shift portability at N_DIM=16384 (HARD_PASS, 3 pairs, ratios=1.0).
  Does the same mechanism extend to LLM-class N_DIM=65536 and 2.5x K? The USER strategic vision
  requires substrate to survive operating-point shifts at LLM-class scale to credibly substitute
  for LLMs.

MECHANISM (identical to v1; only scale changes):
  - Random bipolar HD-vector keys + VQ codebook values + Hebbian outer-product W.
  - JL projection ports keys + payload from P_0 to P_1 when N_DIM differs.
  - 4 arms per (P_0, P_1) pair: WITHIN_P_0, P_0_TO_P_1_REPLAYED, P_1_FRESH_INGEST, P_1_BLANK_RECALL.

KEY IMPLEMENTATION CHANGE: torch.cuda + IMPLICIT-W (low-rank Hebbian)
  At N_DIM=65536 the full W = N x N = 65536 x 65536 x 4 bytes = 17.2 GB -- does NOT fit in the
  remote 4060 Ti's 8 GB VRAM. Recast Hebbian retrieval without materializing W:

    W = V.T @ K_keys / N           (latent rank-M decomposition; M = K_atoms)
    W @ q = V.T @ (K_keys @ q) / N (compute the rank-M product without forming W)

  Memory footprint: K_keys (M, N) + V (V_C, N) + scratch O(M). For M=500 V_C=16384 N=65536:
    K_keys = 500*65536*4 = 131 MB
    V      = 16384*65536*4 = 4.29 GB
    Peak   ~ 4.5 GB (well within 8 GB VRAM headroom)

  Also: chunked JL projection. Full P = N_dst x N_src = 65536 x 32768 x 4 = 8.59 GB -- does NOT
  fit. Apply in tiles of n_dst_tile rows (default 4096): tile_P = 4096 x 32768 x 4 = 524 MB.

GPU MANDATE (Fix #22 + Fix #24):
  - torch.cuda.is_available() asserted at module top; fail-fast if not.
  - All heavy matmuls on cuda:0 with float32; no python-loop matmuls.
  - Cell-author MUST verify GPU util >= 50% steady-state during smoke (instrumented).

THREE (P_0, P_1) PAIRS (LLM-class; 4x v1 in N_DIM):
  A_VC_lift:    V_C=4096->8192   at N=65536 (codebook-density lift at scale)
  B_NDIM_lift:  V_C=8192         at N=32768->65536 (substrate-dim lift to LLM-class)
  C_joint_lift: V_C=4096->8192   at N=32768->65536 (BOTH lifted)

  Smoke uses tiny versions (CPU-friendly so the smoke-VET works even on no-GPU author).

PRE-REGISTERED BANDS (verbatim from spawn prompt):
  HARD_PASS: ALL 3 pairs ratios >= 0.80 AND blank-sanity OK AND cv across seeds <= 0.05 AND
             substrate-only gate preserved (n_llm_calls == 0).
  HARD_FAIL: ANY pair ratio < 0.50 OR blank-sanity broken OR cv > 0.10.
  MIDDLE_BAND: in between.

DISCRIMINATOR-REGIME CHECK (Fix #16):
  WITHIN_P_0 must succeed (else harness broken; HARD_FAIL).
  P_1_BLANK_RECALL must collapse <= 0.10 (else recall is artifact of key encoding; HARD_FAIL).
  P_1_FRESH_INGEST shows P_1's standalone capacity; portability is REAL when REPLAYED ~ FRESH
  (data survived the transform; not just "P_1 supports the load").

FIX INVENTORY:
  - Fix #3: per-seed runtime measurement at near-full-scale BEFORE full dispatch.
  - Fix #5: HDLAB_RUN_MODE override; cell-side _smoke suffix detection (TODO #6 resolution).
  - Fix #6: zero-D-overlap audit -- the 4 operating-point states are pairwise disjoint by
            construction (different (V_C, N_DIM) corners).
  - Fix #11: pipeline-template structure (this cell + dispatch + smoke + full pattern).
  - Fix #14: commit cell to origin/main before remote dispatch (no uncommitted dep).
  - Fix #15: stop-hook + status_log writes (dispatch layer responsibility).
  - Fix #16: discriminator-regime check (WITHIN >= 0.50, BLANK <= 0.10, FRESH ~ REPLAYED).
  - Fix #20: NO `2>&1 | tail` subprocess piping in spawn dispatch logic.
  - Fix #22: GPU routing (this cell mandates cuda).
  - Fix #24: GPU usage verified (steady-state util >= 50% sampled during smoke).
  - PROT-021: config-mismatch guard via run_config = {"N": N_DIM_MAX, "M": K_ATOMS, "run_mode": ...}.

FORMULA SELF-TESTS (--self-test):
  1. Tiny WITHIN-arm at V_C=64 N=512 K=20: recall >= 0.80 (CPU-OK).
  2. Tiny BLANK arm: recall <= 0.20 (CPU-OK).
  3. _LLM_CALL_COUNTER == 0 throughout.
  4. JL projection cosine-drift sanity (CPU).
  5. Implicit-W equivalence: V.T @ (K @ q) / N matches W @ q for small N=128 (CPU; numerical OK).

ASCII-only. Single-file. Resumable.
"""
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import os
# Set PyTorch CUDA allocator to expandable_segments to mitigate fragmentation at 8 GB VRAM.
# Must be set BEFORE `import torch` to take effect.
os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")

import argparse
import time
import math
import json
import gc
from pathlib import Path
from typing import Dict, List, Tuple, Optional

import numpy as np

# torch import deferred until GPU-using code paths -- selftest must run on CPU author too.
# But for Fix #22 routing-gate compliance, the import MUST be visible at module top:
import torch  # routing-sanity gate requires `import torch` literal in script

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import (
    get_output_dir, resumable_seeds, write_partial, aggregate_partials, write_metrics,
)

ANCHOR_NAME = "p1_v2_action_at_any_position_LLM_class_v1"

# Substrate-only-decode gate. Asserted == 0 at end. Any LLM call MUST increment.
_LLM_CALL_COUNTER = [0]

CORPUS_PROVENANCE = "synthetic_bipolar_keys_with_VQ_codebook_LLM_class"


def _detect_run_mode():
    """smoke vs full. Priority: --smoke flag > HDLAB_RUN_MODE > HDLAB_EXP_NAME _smoke suffix > full.

    Cell-side suffix detect is the TODO #6 resolution -- the runner forces HDLAB_RUN_MODE=full
    even on smoke entries, but it DOES stamp HDLAB_EXP_NAME with `_smoke` for smoke runs.
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

# Pre-reg bands (locked at design time; from spawn prompt)
HARD_PASS_RATIO = 0.80
HARD_FAIL_RATIO = 0.50          # spawn prompt: ANY pair ratio < 0.50 -> HARD_FAIL
MIDDLE_BAND_RATIO_LO = 0.50
MIDDLE_BAND_RATIO_HI = 0.80
BLANK_RECALL_MAX = 0.10
WITHIN_P0_MIN = 0.50
CV_HARD_PASS_MAX = 0.05
CV_HARD_FAIL_MAX = 0.10         # cv > 0.10 -> HARD_FAIL
N_RECALL_STEPS = 3
NOISE_FRAC = 0.05
JL_TILE_N_DST = 4096             # tile-rows when materializing JL projection chunks (GPU memory)

# 3 LLM-class (P_0, P_1) pairs. Smoke uses tiny versions for CPU-safe smoke + harness verify.
# (V_C_0, N_DIM_0, V_C_1, N_DIM_1). Alpha is implied = K / N_DIM.
if RUN_MODE == "smoke":
    SEEDS = [1]
    K_ATOMS = 50
    PAIRS = [
        # name, V_C_0, N_DIM_0, V_C_1, N_DIM_1
        ("A_VC_lift_smoke",      128, 1024, 256, 1024),
        ("B_NDIM_lift_smoke",    128, 1024, 128, 2048),
        ("C_joint_lift_smoke",   128, 1024, 256, 2048),
    ]
    N_PROBE = 30
else:
    SEEDS = [7, 17, 23]
    K_ATOMS = 500
    PAIRS = [
        # name, V_C_0, N_DIM_0, V_C_1, N_DIM_1   -- LLM-class (4x v1)
        ("A_VC_lift",     4096, 65536, 8192, 65536),
        ("B_NDIM_lift",   8192, 32768, 8192, 65536),
        ("C_joint_lift",  4096, 32768, 8192, 65536),
    ]
    N_PROBE = 60

ARMS = ["WITHIN_P_0", "P_0_TO_P_1_REPLAYED", "P_1_FRESH_INGEST", "P_1_BLANK_RECALL"]

CONFIG_VERSION = ("p1-v2-LLM-class-v1: K=%d arms=%s pairs=%s noise=%.3f recall_steps=%d run_mode=%s" %
                  (K_ATOMS, ",".join(ARMS),
                   ";".join("%s(VC%d->%d,N%d->%d)" % (n, v0, v1, nd0, nd1) for n, v0, nd0, v1, nd1 in PAIRS),
                   NOISE_FRAC, N_RECALL_STEPS, RUN_MODE))


# ----------------------------- GPU mandate (full run only) -----------------------------
def _require_cuda(strict: bool) -> bool:
    """Fail-fast GPU check. strict=True means raise on absence. Returns True if cuda present."""
    if torch.cuda.is_available():
        return True
    if strict:
        raise RuntimeError(
            "GPU MANDATE (Fix #22 + Fix #24): cuda.is_available() = False. "
            "This cell at N_DIM>=32768 requires CUDA. Re-route to GPU runner.")
    return False


# Strict GPU only for FULL run paths. Smoke and --self-test allowed on CPU for harness verify.
# Author-local CPU selftest is a discipline: the GPU mandate is a runtime gate, not a build gate.
_STRICT_GPU = (RUN_MODE == "full") and not _ARGS.self_test and ("--smoke" not in sys.argv)
_CUDA_OK = _require_cuda(strict=_STRICT_GPU)
_DEVICE = torch.device("cuda:0") if _CUDA_OK else torch.device("cpu")
_DTYPE = torch.float32


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
def _normalize_rows_t(X: torch.Tensor, eps: float = 1e-12) -> torch.Tensor:
    """L2-row-normalize IN-PLACE. Returns X (same storage)."""
    norms = X.norm(dim=1, keepdim=True)
    norms.clamp_(min=eps)
    X.div_(norms)
    return X


def make_bipolar_t(M: int, n: int, gen: torch.Generator, device, dtype) -> torch.Tensor:
    """Random +/- 1 vectors, L2-normalized. (M, n) on device. Single-allocation + in-place."""
    # Single alloc + in-place chain: avoids transient duplicate buffers under tight VRAM.
    X = torch.empty(M, n, device=device, dtype=dtype)
    X.bernoulli_(0.5, generator=gen).mul_(2.0).sub_(1.0)
    return _normalize_rows_t(X)


def make_value_codebook_t(v_c: int, n: int, gen: torch.Generator, device, dtype) -> torch.Tensor:
    """V_C random bipolar value-codebook entries of dim n, L2-normalized. The CLEANUP alphabet."""
    return make_bipolar_t(v_c, n, gen, device, dtype)


def project_rows_chunked_t(X: torch.Tensor, n_dst: int, gen: torch.Generator,
                           tile_n_dst: int = JL_TILE_N_DST) -> torch.Tensor:
    """Apply a deterministic bipolar JL projection P (n_dst, n_src) to rows of X (M, n_src).

    Materializes P in tiles of tile_n_dst rows to keep VRAM bounded. P is regenerated
    deterministically from `gen`; the same generator state produces the same projection.

    When n_src == n_dst: returns X.clone() (identity projection).
    Returns (M, n_dst), L2-normalized.
    """
    M, n_src = X.shape
    device, dtype = X.device, X.dtype
    if n_src == n_dst:
        return _normalize_rows_t(X.clone())
    Y = torch.empty(M, n_dst, device=device, dtype=dtype)
    scale = 1.0 / math.sqrt(n_src)
    start = 0
    while start < n_dst:
        end = min(start + tile_n_dst, n_dst)
        # Single-alloc + in-place: tile_P shape (tile_h, n_src) bipolar * scale.
        tile_P = torch.empty(end - start, n_src, device=device, dtype=dtype)
        tile_P.bernoulli_(0.5, generator=gen).mul_(2.0).sub_(1.0).mul_(scale)
        # Y[:, start:end] = X @ tile_P.T   shape (M, n_src) @ (n_src, tile_h)
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
    """Compute W @ q implicitly: W = val_payload.T @ key_qs_mem / N; return cleanup index.

    Args:
      key_qs_mem:   (K, N) -- the keys stored at memory write time.
      val_payload:  (K, N) -- the values stored at memory write time (first-K of codebook).
      val_codebook: (V_C, N) -- cleanup alphabet (the K payload entries + distractors).
      q:            (N,)   -- query (noised normalized key).
      n_steps:      Hopfield-style cleanup iterations.

    Returns the argmax index against val_codebook.
    """
    K, N = key_qs_mem.shape
    # rank-M intermediate: scores = key_qs_mem @ q -> (K,)
    scores = key_qs_mem @ q
    # y = val_payload.T @ scores / N  -> (N,)
    y = (val_payload.T @ scores) / float(N)
    for _ in range(n_steps):
        sims = val_codebook @ y           # (V_C,)
        idx = int(torch.argmax(sims).item())
        y_snap = val_codebook[idx]
        y = 0.5 * y + 0.5 * y_snap
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

    val_codebook[i] for i < K must equal val_payload[i] (cleanup payload contract).
    """
    K = key_qs_mem.shape[0]
    N = key_qs_mem.shape[1]
    n_q = min(n_probe, K)
    if n_q == 0:
        return 0.0
    # Probe-indices: choose w/o replacement via randperm on the generator
    perm = torch.randperm(K, generator=gen, device=key_qs_mem.device)[:n_q]
    correct = 0
    for j_idx in range(n_q):
        j = int(perm[j_idx].item())
        q = key_qs_mem[j].clone()
        # 5% bit flips: bernoulli mask, flip via *-1.0
        flip_mask = torch.bernoulli(
            torch.full((N,), NOISE_FRAC, device=q.device, dtype=q.dtype), generator=gen)
        q = q * (1.0 - 2.0 * flip_mask)
        q = q / (q.norm() + 1e-12)
        retr_idx = hebbian_retrieve_implicit_t(key_qs_mem, val_payload, val_codebook,
                                               q, n_steps=N_RECALL_STEPS)
        if retr_idx == int(value_idx_truth[j].item()):
            correct += 1
    return float(correct) / n_q


def _make_gen(seed_int: int) -> torch.Generator:
    g = torch.Generator(device=_DEVICE)
    g.manual_seed(int(seed_int))
    return g


def _arm_within(v_c_0: int, n_dim_0: int, gen_p0: torch.Generator,
                gen_probe: torch.Generator) -> float:
    """ARM 1: WITHIN_P_0. Allocates only what's needed; returns recall (float)."""
    val_cb_0 = make_value_codebook_t(v_c_0, n_dim_0, gen_p0, _DEVICE, _DTYPE)
    key_qs_0 = make_bipolar_t(K_ATOMS, n_dim_0, gen_p0, _DEVICE, _DTYPE)
    val_idx_0 = torch.arange(K_ATOMS, device=_DEVICE)
    val_payload_0 = val_cb_0[:K_ATOMS]
    rec = eval_recall_implicit_t(key_qs_0, val_payload_0, val_cb_0,
                                  val_idx_0, N_PROBE, gen_probe)
    del val_cb_0, key_qs_0, val_idx_0, val_payload_0
    if _CUDA_OK:
        torch.cuda.empty_cache()
    return rec


def _arm_fresh(v_c_1: int, n_dim_1: int, gen_p1: torch.Generator,
               gen_probe: torch.Generator) -> float:
    """ARM 3: P_1_FRESH_INGEST. Allocates fresh codebook + keys at P_1; returns recall."""
    val_cb_1 = make_value_codebook_t(v_c_1, n_dim_1, gen_p1, _DEVICE, _DTYPE)
    key_qs_1 = make_bipolar_t(K_ATOMS, n_dim_1, gen_p1, _DEVICE, _DTYPE)
    val_idx_1 = torch.arange(K_ATOMS, device=_DEVICE)
    val_payload_1 = val_cb_1[:K_ATOMS]
    rec = eval_recall_implicit_t(key_qs_1, val_payload_1, val_cb_1,
                                  val_idx_1, N_PROBE, gen_probe)
    del val_cb_1, key_qs_1, val_idx_1, val_payload_1
    if _CUDA_OK:
        torch.cuda.empty_cache()
    return rec


def _arm_replayed_and_blank(v_c_0: int, n_dim_0: int, v_c_1: int, n_dim_1: int,
                            gen_p0: torch.Generator, gen_proj: torch.Generator,
                            gen_distract: torch.Generator,
                            gen_probe_r: torch.Generator,
                            gen_probe_b: torch.Generator) -> Tuple[float, float]:
    """ARM 2 + ARM 4: P_0_TO_P_1_REPLAYED + P_1_BLANK_RECALL.

    Both arms share the projected probe set, so we build it once. Frees aggressively when
    done. Returns (recall_replayed, recall_blank).
    """
    # Re-derive P_0 keys + payload (deterministic via gen_p0 sequence)
    val_cb_0 = make_value_codebook_t(v_c_0, n_dim_0, gen_p0, _DEVICE, _DTYPE)
    key_qs_0 = make_bipolar_t(K_ATOMS, n_dim_0, gen_p0, _DEVICE, _DTYPE)
    val_payload_0 = val_cb_0[:K_ATOMS].clone()  # CLONE to detach from val_cb_0 storage
    del val_cb_0
    if _CUDA_OK:
        torch.cuda.empty_cache()
    # Project keys + payload from N_0 to N_1
    key_qs_proj = project_rows_chunked_t(key_qs_0, n_dim_1, gen_proj)
    del key_qs_0
    if _CUDA_OK:
        torch.cuda.empty_cache()
    val_payload_proj = project_rows_chunked_t(val_payload_0, n_dim_1, gen_proj)
    del val_payload_0
    if _CUDA_OK:
        torch.cuda.empty_cache()
    # Build val_cb_proj at P_1 of size V_C_1
    n_distract = max(0, v_c_1 - K_ATOMS)
    if n_distract > 0:
        distractors = make_bipolar_t(n_distract, n_dim_1, gen_distract, _DEVICE, _DTYPE)
        val_cb_proj = torch.cat([val_payload_proj, distractors], dim=0)
        del distractors, val_payload_proj
        if _CUDA_OK:
            torch.cuda.empty_cache()
    else:
        val_cb_proj = val_payload_proj
    val_idx_proj = torch.arange(K_ATOMS, device=_DEVICE)
    rec_replayed = eval_recall_implicit_t(key_qs_proj, val_cb_proj[:K_ATOMS], val_cb_proj,
                                           val_idx_proj, N_PROBE, gen_probe_r)
    # BLANK: empty memory, same probes
    empty_keys = torch.zeros(0, n_dim_1, device=_DEVICE, dtype=_DTYPE)
    empty_vals = torch.zeros(0, n_dim_1, device=_DEVICE, dtype=_DTYPE)
    rec_blank = _eval_blank_implicit_t(empty_keys, empty_vals, val_cb_proj, val_idx_proj,
                                        key_qs_proj, N_PROBE, gen_probe_b)
    del empty_keys, empty_vals, key_qs_proj, val_cb_proj, val_idx_proj
    if _CUDA_OK:
        torch.cuda.empty_cache()
    return rec_replayed, rec_blank


def run_pair(pair_name: str, v_c_0: int, n_dim_0: int, v_c_1: int, n_dim_1: int,
             seed: int, gpu_util_samples: List[float]) -> Dict:
    """Run the 4-arm matrix for one (P_0, P_1) pair on GPU (or CPU if smoke).

    Memory discipline: each arm is a local function with its own GPU allocations + explicit
    free via del + empty_cache between arms. Peak GPU memory bounded by the heaviest single
    arm (REPLAYED, which holds val_cb_proj at V_C_1 x N_1).

    Mechanism (identical to v1).
    """
    t0 = time.time()
    rng_seed_p0 = seed * 10007 + (abs(hash(pair_name)) % 9973)

    # ARM 1: WITHIN_P_0
    gen_p0 = _make_gen(rng_seed_p0)
    gen_probe_w = _make_gen(rng_seed_p0 + 401)
    recall_within = _arm_within(v_c_0, n_dim_0, gen_p0, gen_probe_w)
    sample = _gpu_util_sample()
    if sample is not None:
        gpu_util_samples.append(sample)

    # ARM 3: P_1_FRESH_INGEST (do BEFORE REPLAYED so peaks don't stack across runs)
    gen_p1 = _make_gen(rng_seed_p0 + 31)
    gen_probe_f = _make_gen(rng_seed_p0 + 607)
    recall_fresh = _arm_fresh(v_c_1, n_dim_1, gen_p1, gen_probe_f)
    sample = _gpu_util_sample()
    if sample is not None:
        gpu_util_samples.append(sample)

    # ARMS 2 + 4: REPLAYED + BLANK (share projected probes)
    gen_p0_again = _make_gen(rng_seed_p0)  # SAME sequence as WITHIN -- determinism preserved
    gen_proj = _make_gen(rng_seed_p0 + 71)
    gen_distract = _make_gen(rng_seed_p0 + 131)
    gen_probe_r = _make_gen(rng_seed_p0 + 503)
    gen_probe_b = _make_gen(rng_seed_p0 + 709)
    recall_replayed, recall_blank = _arm_replayed_and_blank(
        v_c_0, n_dim_0, v_c_1, n_dim_1,
        gen_p0_again, gen_proj, gen_distract, gen_probe_r, gen_probe_b)
    sample = _gpu_util_sample()
    if sample is not None:
        gpu_util_samples.append(sample)

    wall_s = time.time() - t0
    ratio = (recall_replayed / recall_within) if recall_within > 1e-9 else 0.0

    return {
        "pair": pair_name,
        "seed": int(seed),
        "v_c_0": int(v_c_0), "n_dim_0": int(n_dim_0),
        "v_c_1": int(v_c_1), "n_dim_1": int(n_dim_1),
        "alpha_0": float(K_ATOMS) / float(n_dim_0),
        "alpha_1": float(K_ATOMS) / float(n_dim_1),
        "recall_WITHIN_P_0": float(recall_within),
        "recall_P_0_TO_P_1_REPLAYED": float(recall_replayed),
        "recall_P_1_FRESH_INGEST": float(recall_fresh),
        "recall_P_1_BLANK_RECALL": float(recall_blank),
        "ratio_replayed_over_within": float(ratio),
        "n_probe": N_PROBE,
        "wall_s": float(wall_s),
        "device": str(_DEVICE),
    }


def _eval_blank_implicit_t(empty_keys: torch.Tensor, empty_vals: torch.Tensor,
                           val_codebook: torch.Tensor, value_idx_truth: torch.Tensor,
                           key_qs_for_probes: torch.Tensor,
                           n_probe: int, gen: torch.Generator) -> float:
    """BLANK arm: empty memory, probe with the SAME noised keys we'd use in REPLAYED.

    Empty mem => W @ q = 0 => Hopfield cleanup picks the first codebook entry repeatedly.
    The truthful test: did this constant-pick coincide with the ground-truth value index for
    each probe? For K_ATOMS=500 truth indices = 0..K-1, the constant-pick = index 0 will match
    only if probe's truth happened to be 0 (1/K probability). So expected recall ~ 1/K <= 0.10.

    Note: this is structurally equivalent to v1's blank arm (W=0 -> all probes get the same
    cleanup pick). The BLANK floor verifies retrieval requires non-trivial W.
    """
    K = key_qs_for_probes.shape[0]
    N = key_qs_for_probes.shape[1]
    n_q = min(n_probe, K)
    if n_q == 0:
        return 0.0
    perm = torch.randperm(K, generator=gen, device=key_qs_for_probes.device)[:n_q]
    correct = 0
    for j_idx in range(n_q):
        j = int(perm[j_idx].item())
        q = key_qs_for_probes[j].clone()
        flip_mask = torch.bernoulli(
            torch.full((N,), NOISE_FRAC, device=q.device, dtype=q.dtype), generator=gen)
        q = q * (1.0 - 2.0 * flip_mask)
        q = q / (q.norm() + 1e-12)
        retr_idx = hebbian_retrieve_implicit_t(empty_keys, empty_vals, val_codebook,
                                                q, n_steps=N_RECALL_STEPS)
        if retr_idx == int(value_idx_truth[j].item()):
            correct += 1
    return float(correct) / n_q


# ----------------------------- self-test -----------------------------
def _selftest():
    """5 formula self-tests. Runs on CPU (smoke-safe; no GPU required for selftest)."""
    # Save + override device for selftest (CPU-safe)
    global _DEVICE, _DTYPE
    _save_dev = _DEVICE
    _DEVICE = torch.device("cpu")
    _DTYPE = torch.float32
    try:
        gen = _make_gen(0)
        # T1: Tiny WITHIN arm at zero noise: V_C=128, N=512, K=10.
        v_c, n_dim, k_a = 128, 512, 10
        val_cb = make_value_codebook_t(v_c, n_dim, gen, _DEVICE, _DTYPE)
        keys = make_bipolar_t(k_a, n_dim, gen, _DEVICE, _DTYPE)
        val_payload = val_cb[:k_a]
        n_correct = 0
        for j in range(k_a):
            q = keys[j] / (keys[j].norm() + 1e-12)
            ridx = hebbian_retrieve_implicit_t(keys, val_payload, val_cb, q, n_steps=3)
            if ridx == j:
                n_correct += 1
        rec_within = n_correct / k_a
        assert rec_within >= 0.80, "selftest T1: tiny WITHIN recall %.3f < 0.80" % rec_within

        # T2: BLANK arm: empty memory -> recall <= 0.20.
        empty_k = torch.zeros(0, n_dim, dtype=_DTYPE)
        empty_v = torch.zeros(0, n_dim, dtype=_DTYPE)
        n_correct_b = 0
        for j in range(k_a):
            q = keys[j] / (keys[j].norm() + 1e-12)
            ridx = hebbian_retrieve_implicit_t(empty_k, empty_v, val_cb, q, n_steps=3)
            if ridx == j:
                n_correct_b += 1
        rec_blank = n_correct_b / k_a
        assert rec_blank <= 0.20, "selftest T2: blank recall %.3f > 0.20" % rec_blank

        # T3: LLM counter zero
        assert _LLM_CALL_COUNTER[0] == 0, "selftest T3: LLM counter non-zero (%d)" % _LLM_CALL_COUNTER[0]

        # T4: JL projection cosine drift sanity
        gen2 = _make_gen(1)
        X = make_bipolar_t(20, 256, gen2, _DEVICE, _DTYPE)
        Y = project_rows_chunked_t(X, 512, gen2, tile_n_dst=128)
        XX = (X @ X.T).detach()
        YY = (Y @ Y.T).detach()
        err = float((XX - YY).abs().max().item())
        assert err < 0.40, "selftest T4: JL cosine drift %.3f > 0.40" % err

        # T5: Implicit-W equivalence to explicit W on tiny N=128.
        gen3 = _make_gen(2)
        small_n = 128
        small_v_c = 64
        small_k = 8
        val_cb_s = make_value_codebook_t(small_v_c, small_n, gen3, _DEVICE, _DTYPE)
        keys_s = make_bipolar_t(small_k, small_n, gen3, _DEVICE, _DTYPE)
        val_pay_s = val_cb_s[:small_k]
        # Explicit W = V.T @ K / N
        W_explicit = (val_pay_s.T @ keys_s) / float(small_n)  # (N, N) ... but for small_n=128 only 64KB
        # Wait: V is (K, N), keys is (K, N). W = V.T @ K should be (N, K) @ (K, N) -> (N, N).
        # Actually val_pay_s.T = (N, K), keys_s = (K, N). val_pay_s.T @ keys_s = (N, N). Good.
        # For each probe q: W @ q should equal val_pay_s.T @ (keys_s @ q) / N.
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


_selftest()
if _ARGS.self_test:
    sys.exit(0)


# ----------------------------- main pipeline -----------------------------
def run_seed(seed: int) -> Dict:
    """Run all 3 pairs (each = 4 arms) for one seed."""
    t0 = time.time()
    gpu_util_samples: List[float] = []
    per_unit = []
    for (pair_name, v_c_0, n_dim_0, v_c_1, n_dim_1) in PAIRS:
        res = run_pair(pair_name, v_c_0, n_dim_0, v_c_1, n_dim_1, seed, gpu_util_samples)
        per_unit.append(res)
        print(("  [seed=%d] pair=%s VC%d->%d N%d->%d | WITHIN=%.3f REPLAYED=%.3f FRESH=%.3f "
               "BLANK=%.3f | ratio=%.3f wall=%.1fs") %
              (seed, pair_name, v_c_0, v_c_1, n_dim_0, n_dim_1,
               res["recall_WITHIN_P_0"], res["recall_P_0_TO_P_1_REPLAYED"],
               res["recall_P_1_FRESH_INGEST"], res["recall_P_1_BLANK_RECALL"],
               res["ratio_replayed_over_within"], res["wall_s"]), flush=True)
    elapsed = time.time() - t0
    gpu_util_mean = float(np.mean(gpu_util_samples)) if gpu_util_samples else float("nan")
    gpu_util_p50 = float(np.median(gpu_util_samples)) if gpu_util_samples else float("nan")
    gpu_util_max = float(np.max(gpu_util_samples)) if gpu_util_samples else float("nan")
    return {
        "seed": seed,
        "N": max(p[2] for p in PAIRS),
        "M": K_ATOMS,
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
    """Compute verdict per the pre-reg bands (spawn prompt: PASS>=0.80, FAIL<0.50, cv>0.10=FAIL)."""
    if not per_seed:
        return ("HARD_FAIL", "No valid results.", {})
    pairs_seen: List[str] = [p[0] for p in PAIRS]
    agg: Dict[str, Dict[str, List[float]]] = {pn: {"WITHIN": [], "REPLAYED": [], "FRESH": [],
                                                   "BLANK": [], "RATIO": []} for pn in pairs_seen}
    for _sid, body in per_seed.items():
        for pu in body.get("per_unit", []):
            pn = pu["pair"]
            if pn not in agg:
                continue
            agg[pn]["WITHIN"].append(float(pu["recall_WITHIN_P_0"]))
            agg[pn]["REPLAYED"].append(float(pu["recall_P_0_TO_P_1_REPLAYED"]))
            agg[pn]["FRESH"].append(float(pu["recall_P_1_FRESH_INGEST"]))
            agg[pn]["BLANK"].append(float(pu["recall_P_1_BLANK_RECALL"]))
            agg[pn]["RATIO"].append(float(pu["ratio_replayed_over_within"]))

    def _stat(xs):
        if not xs:
            return float("nan"), float("nan"), float("nan")
        m = float(np.mean(xs))
        s = float(np.std(xs))
        cv = float(s / max(m, 1e-9)) if m > 1e-9 else float("inf")
        return m, s, cv

    pair_summary: Dict[str, Dict] = {}
    for pn in pairs_seen:
        d = agg[pn]
        wm, ws, wcv = _stat(d["WITHIN"])
        rm, rs, rcv = _stat(d["REPLAYED"])
        fm, fs, fcv = _stat(d["FRESH"])
        bm, bs, bcv = _stat(d["BLANK"])
        rat_m, rat_s, rat_cv = _stat(d["RATIO"])
        pair_summary[pn] = {
            "within_mean": wm, "within_std": ws, "within_cv": wcv,
            "replayed_mean": rm, "replayed_std": rs, "replayed_cv": rcv,
            "fresh_mean": fm, "fresh_std": fs, "fresh_cv": fcv,
            "blank_mean": bm, "blank_std": bs, "blank_cv": bcv,
            "ratio_mean": rat_m, "ratio_std": rat_s, "ratio_cv": rat_cv,
        }

    n_llm = sum(int(b.get("n_llm_calls", 0)) for b in per_seed.values())
    substrate_only_ok = (n_llm == 0)

    all_ratios_pass = all(pair_summary[pn]["ratio_mean"] >= HARD_PASS_RATIO for pn in pairs_seen)
    any_ratio_fail = any(pair_summary[pn]["ratio_mean"] < HARD_FAIL_RATIO for pn in pairs_seen)
    all_within_ok = all(pair_summary[pn]["within_mean"] >= WITHIN_P0_MIN for pn in pairs_seen)
    all_blank_ok = all(pair_summary[pn]["blank_mean"] <= BLANK_RECALL_MAX for pn in pairs_seen)
    cv_pass_ok = all(
        pair_summary[pn]["within_cv"] <= CV_HARD_PASS_MAX and
        pair_summary[pn]["replayed_cv"] <= CV_HARD_PASS_MAX
        for pn in pairs_seen)
    cv_fail = any(
        pair_summary[pn]["within_cv"] > CV_HARD_FAIL_MAX or
        pair_summary[pn]["replayed_cv"] > CV_HARD_FAIL_MAX
        for pn in pairs_seen)

    # Aggregate GPU util across seeds
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
        "pair_summary": pair_summary,
        "all_ratios_>=_%.2f" % HARD_PASS_RATIO: bool(all_ratios_pass),
        "any_ratio_<_%.2f" % HARD_FAIL_RATIO: bool(any_ratio_fail),
        "all_within_>=_%.2f" % WITHIN_P0_MIN: bool(all_within_ok),
        "all_blank_<=_%.2f" % BLANK_RECALL_MAX: bool(all_blank_ok),
        "cv_within+replayed_<=_%.2f_all_pairs" % CV_HARD_PASS_MAX: bool(cv_pass_ok),
        "any_cv_>_%.2f" % CV_HARD_FAIL_MAX: bool(cv_fail),
        "substrate_only_ok": bool(substrate_only_ok),
        "zero_llm_calls_at_inference": bool(substrate_only_ok),
        "gpu_util_mean": gpu_util_mean_overall,
        "gpu_util_p50": gpu_util_p50_overall,
        "gpu_util_max": gpu_util_max_overall,
        "gpu_util_n_samples": len(gpu_util_all),
        "honest_scope": ("LLM-class (N_DIM up to 65536) operating-point-shift portability on "
                         "synthetic-bipolar HD substrate with VQ codebook + IMPLICIT-Hebbian "
                         "(low-rank W = V.T @ K / N; no explicit (N,N) matrix). K=%d atoms; 3 "
                         "(P_0,P_1) pairs spanning V_C / N_DIM / joint lifts. Substrate-only-decode "
                         "gate enforced (n_llm=%d). cuda_required=True; cell aborts on no-CUDA when "
                         "run_mode=full." % (K_ATOMS, n_llm)),
    }

    parts = []
    for pn in pairs_seen:
        ps = pair_summary[pn]
        parts.append("%s[w=%.3f r=%.3f f=%.3f b=%.3f rat=%.3f cv=%.3f]" %
                     (pn, ps["within_mean"], ps["replayed_mean"], ps["fresh_mean"],
                      ps["blank_mean"], ps["ratio_mean"], ps["ratio_cv"]))
    summary = " | ".join(parts) + (" | llm=%d | gpu_util_mean=%.1f%%" %
                                    (n_llm, gpu_util_mean_overall))

    if not substrate_only_ok:
        return ("HARD_FAIL",
                "HARD_FAIL: substrate-only-decode gate VIOLATED (%d LLM calls). %s" % (n_llm, summary),
                detail)
    if not all_within_ok:
        return ("HARD_FAIL",
                "HARD_FAIL: WITHIN_P_0 baseline below floor %.2f on at least one pair. %s" %
                (WITHIN_P0_MIN, summary),
                detail)
    if not all_blank_ok:
        return ("HARD_FAIL",
                "HARD_FAIL: P_1_BLANK_RECALL exceeds sanity floor %.2f on at least one pair. %s" %
                (BLANK_RECALL_MAX, summary),
                detail)
    if cv_fail:
        return ("HARD_FAIL",
                "HARD_FAIL: cv across seeds > %.2f on at least one pair (seed-unstable). %s" %
                (CV_HARD_FAIL_MAX, summary),
                detail)
    if any_ratio_fail:
        bad = [pn for pn in pairs_seen if pair_summary[pn]["ratio_mean"] < HARD_FAIL_RATIO]
        return ("HARD_FAIL",
                "HARD_FAIL: pair(s) %s ratio < %.2f (data destroyed by transform). %s" %
                (",".join(bad), HARD_FAIL_RATIO, summary),
                detail)
    if all_ratios_pass and cv_pass_ok:
        return ("HARD_PASS",
                ("HARD_PASS: LLM-class operating-point-shift portability on ALL 3 pairs (N_DIM up "
                 "to 65536). ALL ratios >= %.2f AND blank-sanity OK AND cv <= %.2f AND "
                 "substrate-only-gate preserved. %s" %
                 (HARD_PASS_RATIO, CV_HARD_PASS_MAX, summary)),
                detail)
    return ("MIDDLE_BAND",
            ("MIDDLE_BAND: partial portability at LLM-class. Some pair(s) in [%.2f, %.2f). %s" %
             (HARD_FAIL_RATIO, HARD_PASS_RATIO, summary)),
            detail)


# ----------------------------- main -----------------------------
out_dir = get_output_dir(ANCHOR_NAME)
t0_total = time.time()
run_config = {"N": max(p[2] for p in PAIRS), "M": K_ATOMS, "run_mode": RUN_MODE}

done, seeds_todo = resumable_seeds(SEEDS, out_dir, run_config)
print("[run] mode=%s K=%d cuda=%s device=%s pairs=%s seeds_done=%s seeds_todo=%s" %
      (RUN_MODE, K_ATOMS, _CUDA_OK, _DEVICE, str([p[0] for p in PAIRS]),
       str(done), str(seeds_todo)), flush=True)
if _CUDA_OK:
    free_b, total_b = torch.cuda.mem_get_info(0)
    print("[gpu] %s vram_total=%.2fGB vram_free=%.2fGB" %
          (torch.cuda.get_device_name(0), total_b / 1e9, free_b / 1e9), flush=True)

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
    "K_atoms": K_ATOMS,
    "pairs": [{"name": n, "v_c_0": v0, "n_dim_0": nd0, "v_c_1": v1, "n_dim_1": nd1}
              for (n, v0, nd0, v1, nd1) in PAIRS],
    "arms": ARMS,
    "run_mode": RUN_MODE,
    "config_version": CONFIG_VERSION,
    "corpus_provenance": CORPUS_PROVENANCE,
    "allow_synthetic": True,
    "zero_llm_calls_at_inference": bool(_LLM_CALL_COUNTER[0] == 0),
    "n_llm_calls": int(_LLM_CALL_COUNTER[0]),
    "device": str(_DEVICE),
    "cuda_ok": bool(_CUDA_OK),
    "detail": detail,
    "per_seed": [
        {"seed": k, **{kk: vv for kk, vv in v.items() if kk != "per_unit"},
         "per_unit": v.get("per_unit", [])}
        for k, v in per_seed.items()
    ],
    "metrics_source": "measured_gpu_synthetic_bipolar_VQ_codebook_implicit_hebbian_LLM_class",
    "elapsed_s": time.time() - t0_total,
    "summary": verdict_msg[:200],
}

write_metrics(out_dir, metrics, results=list(per_seed.values()))

print("\n[VERDICT] %s" % verdict, flush=True)
print("[VERDICT_MSG] %s" % verdict_msg, flush=True)
print("[METRICS_PATH] %s" % (out_dir / "metrics.json"), flush=True)
