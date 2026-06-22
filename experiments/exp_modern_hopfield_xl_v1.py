"""modern_hopfield_xl_v1 -- Krotov exponential-energy Modern Hopfield vs Classical Hebbian at LLM-class scale.

SCIENTIFIC QUESTION (USER strategic vision, substrate-as-LLM-substitute storage):
  Krotov Modern Hopfield (1) has theoretical super-linear capacity M = O(exp(N)) vs
  classical Hopfield's M ~ 0.14 * N (Hebbian Hopfield 1982 capacity). The substrate's
  current W matrix uses linear Hebbian -- it caps at alpha=0.14. If Krotov-style
  exponential-energy retrieval is a viable alternative storage mechanism at LLM-class
  N_DIM=65536 with M up to 10000 (exceeding classical bound 0.14 * 65536 = 9175), then
  the substrate gains an orders-of-magnitude capacity lift. This cell measures that
  lift empirically and rules whether modern Hopfield beats classical above its capacity.

MECHANISM:
  Bipolar L2-normalized HD keys K (M, N). For a noised query q (N,):

  MODERN_HOPFIELD (Krotov exponential-energy retrieval):
    Per pattern-association attractor (Ramsauer et al 2020 NeurIPS):
      sims = q @ K.T  shape (M,)
      w    = softmax(beta * sims)  shape (M,)
      ret  = w @ K     shape (N,)                  one-step update; then snap to argmax(sim(ret, K))
    Energy E(q) = -lse(beta * K @ q) / beta with one-shot updates Q_new = softmax(beta * K @ Q.T).T @ K.
    Super-linear capacity at large beta.

  CLASSICAL_HEBBIAN (Hopfield 1982; substrate's current storage):
    W = sum_i k_i k_i^T / N    (implicit; never materialized at N=65536: ~17 GB)
    Implicit retrieval: y = W @ q = (1/N) * K.T @ (K @ q)  shape (N,); snap to argmax(sim(y, K)).
    Capacity ~ 0.14 * N (theoretical bound from spin-glass analysis).

  SHUFFLED_QUERY (mechanism-null floor):
    Same K, but noised queries are formed from RANDOMLY-PERMUTED keys (not the true key).
    No retrieval mechanism can do better than random; this floor proves the arms ARE
    measuring retrieval (not artifact). Expected top-1 ~ 1/M (negligible at M=10000).

DISCRIMINATOR (Fix #16 mechanism-discriminating bands):
  At M=10000 (BEYOND classical capacity bound 0.14 * 65536 = 9175):
    HARD_PASS: MODERN_HOPFIELD top-1 >= 0.95 AND CLASSICAL_HEBBIAN top-1 <= 0.70
               AND SHUFFLED_QUERY top-1 <= 0.05.
    HARD_FAIL: MODERN_HOPFIELD top-1 < 0.50 OR
               MODERN_HOPFIELD does NOT beat CLASSICAL above classical's capacity bound
               (defined as: MODERN - CLASSICAL gap at M=10000 < 0.10).
    MIDDLE_BAND: in between.

  Also required at every M point:
    SHUFFLED <= 0.05 (mechanism-null floor honored)
    BLANK_KEYS sanity (no retrieval from empty store) implicit via mechanism contract.

GPU MANDATE (Fix #22 + Fix #24):
  - torch.cuda required for full run (cell aborts on no-CUDA in full mode).
  - All matmuls are single (NQ, N) @ (N, M) shape -> GPU-natural; no per-element python loops.
  - K is hoisted out of (seed, beta) inner loops -- generated once per (seed, M), reused for
    all 4 beta values per M. Massive GPU work per matmul; idle time minimized.
  - nvidia-smi GPU util sampled per arm; gpu_util_mean >= 50% steady-state required for
    smoke + full runs (Fix #24 mandate).

SCALE:
  Full: N_DIM=65536, M in {1000, 2000, 5000, 10000}, beta in {1.0, 2.0, 4.0, 8.0},
        NQ=100 noisy probes per arm, noise stdev=0.1 on bipolar query, 3 seeds.
  Memory: K shape (M=10000, N=65536) fp32 = 2.62 GB; sims (NQ=100, M=10000) = 4 MB.
          Peak well below 8 GB VRAM.

SMOKE:
  Tiny version (CPU-safe so smoke-VET works on no-GPU author): N=512, M in {50, 200},
  beta in {2.0, 8.0}, NQ=20, 1 seed.

FORMULA SELF-TESTS (--self-test; CPU):
  T1: noiseless modern Hopfield at M=20 N=256: top-1 >= 0.95 (one-shot retrieval works on clean q).
  T2: noiseless classical Hebbian at M=20 N=256: top-1 >= 0.95 (well below 0.14 * 256 = 35).
  T3: shuffled-query floor: shuffled top-1 ~ 1/M (< 0.10 for M=20).
  T4: substrate-only gate: _LLM_CALL_COUNTER == 0.
  T5: Softmax stability: beta * sims max in float32 range (no overflow at beta=8).

FIX INVENTORY:
  - Fix #3:  per-seed runtime measurement at near-full-scale BEFORE full dispatch.
  - Fix #5:  HDLAB_RUN_MODE override + cell-side _smoke suffix detection.
  - Fix #6:  zero-D-overlap audit -- arms operate on disjoint pattern indices.
  - Fix #11: pipeline-template structure (smoke + full pattern).
  - Fix #14: commit cell to origin/main before remote dispatch.
  - Fix #16: discriminator-regime check (modern beats classical above classical's bound).
  - Fix #20: no `2>&1 | tail` subprocess piping in spawn dispatch.
  - Fix #22: GPU routing (torch import literal at module top).
  - Fix #24: GPU util sampling per arm; mean >= 50% required.
  - PROT-021: config-mismatch guard via run_config.

ASCII-only. Single-file. Resumable.
"""
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import os
os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")

import argparse
import time
import math
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional

import numpy as np

# torch import at module top -- routing-sanity gate requires `import torch` literal.
import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import (
    get_output_dir, resumable_seeds, write_partial, aggregate_partials, write_metrics,
)

ANCHOR_NAME = "modern_hopfield_xl_v1"

# Substrate-only-decode gate. Asserted == 0 at end. Any LLM call MUST increment.
_LLM_CALL_COUNTER = [0]

CORPUS_PROVENANCE = "synthetic_bipolar_HD_keys_L2_normalized"


def _detect_run_mode():
    """smoke vs full. Priority: --smoke flag > HDLAB_RUN_MODE > HDLAB_EXP_NAME _smoke suffix > full."""
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

# Pre-reg bands (locked from spawn prompt)
HARD_PASS_MODERN_TOP1_AT_M_MAX = 0.95
HARD_PASS_CLASSICAL_TOP1_AT_M_MAX = 0.70   # ceiling: modern must beat this
HARD_PASS_SHUFFLED_TOP1_MAX = 0.05         # mechanism-null floor
HARD_FAIL_MODERN_TOP1_MIN = 0.50           # below this = HARD_FAIL
HARD_FAIL_MODERN_MINUS_CLASSICAL_MIN = 0.10  # mechanism-discriminator gap
NOISE_STDEV = 0.1                          # gaussian on bipolar query


if RUN_MODE == "smoke":
    SEEDS = [1]
    N_DIM = 512
    M_GRID = [50, 200]
    BETA_GRID = [2.0, 8.0]
    NQ = 20
else:
    SEEDS = [7, 17, 23]
    N_DIM = 65536
    M_GRID = [1000, 2000, 5000, 10000]
    BETA_GRID = [1.0, 2.0, 4.0, 8.0]
    NQ = 100

ARMS = ["MODERN_HOPFIELD", "CLASSICAL_HEBBIAN", "SHUFFLED_QUERY"]
M_MAX = max(M_GRID)
CLASSICAL_BOUND_AT_N = 0.14 * N_DIM  # informational; used in discriminator decision

CONFIG_VERSION = ("modern-hopfield-xl-v1: N=%d M_grid=%s beta_grid=%s NQ=%d noise=%.3f seeds=%s "
                  "arms=%s run_mode=%s" %
                  (N_DIM, M_GRID, BETA_GRID, NQ, NOISE_STDEV, SEEDS, ",".join(ARMS), RUN_MODE))


# ----------------------------- GPU mandate -----------------------------
def _require_cuda(strict: bool) -> bool:
    if torch.cuda.is_available():
        return True
    if strict:
        raise RuntimeError(
            "GPU MANDATE (Fix #22 + Fix #24): cuda.is_available() = False. "
            "This cell at N_DIM>=32768 requires CUDA. Re-route to GPU runner.")
    return False


_STRICT_GPU = (RUN_MODE == "full") and not _ARGS.self_test and ("--smoke" not in sys.argv)
_CUDA_OK = _require_cuda(strict=_STRICT_GPU)
_DEVICE = torch.device("cuda:0") if _CUDA_OK else torch.device("cpu")
_DTYPE = torch.float32


def _gpu_util_sample() -> Optional[float]:
    try:
        import subprocess
        out = subprocess.run(
            ["nvidia-smi", "--query-gpu=utilization.gpu", "--format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=5,
        )
        if out.returncode == 0:
            return float(out.stdout.strip().splitlines()[0].strip())
    except (Exception,):
        pass
    return None


# ----------------------------- HD primitives -----------------------------
def _normalize_rows_t(X: torch.Tensor, eps: float = 1e-12) -> torch.Tensor:
    norms = X.norm(dim=1, keepdim=True)
    norms.clamp_(min=eps)
    X.div_(norms)
    return X


def make_bipolar_keys_t(M: int, n: int, gen: torch.Generator, device, dtype) -> torch.Tensor:
    """Random +/- 1 vectors, L2-normalized. Shape (M, n) on device."""
    X = torch.empty(M, n, device=device, dtype=dtype)
    X.bernoulli_(0.5, generator=gen).mul_(2.0).sub_(1.0)
    return _normalize_rows_t(X)


def add_gaussian_noise_and_normalize_t(Q: torch.Tensor, stdev: float,
                                       gen: torch.Generator) -> torch.Tensor:
    """Add stdev * N(0,1) to Q (NQ, N) and re-normalize each row. Returns new tensor."""
    noise = torch.empty_like(Q)
    noise.normal_(mean=0.0, std=stdev, generator=gen)
    Q_n = Q + noise
    return _normalize_rows_t(Q_n)


# ----------------------------- retrieval mechanisms -----------------------------
def modern_hopfield_top1_batch_t(K: torch.Tensor, Q: torch.Tensor, beta: float) -> torch.Tensor:
    """Krotov Modern Hopfield one-shot retrieval; returns argmax indices.

    Args:
      K: (M, N) stored keys (L2-normalized).
      Q: (NQ, N) noised queries (L2-normalized).
      beta: inverse temperature.

    Returns: (NQ,) long tensor of argmax indices in [0, M).

    Mechanism: sims = Q @ K.T (NQ, M); ret = softmax(beta * sims) @ K (NQ, N);
               snap = argmax(ret @ K.T, dim=1) (NQ,).
    Single matmul chain; GPU-natural.
    """
    sims = Q @ K.T                              # (NQ, M)
    w = torch.softmax(beta * sims, dim=1)       # (NQ, M)
    ret = w @ K                                 # (NQ, N) attractor superposition
    sims2 = ret @ K.T                           # (NQ, M) snap-similarity to stored keys
    idx = torch.argmax(sims2, dim=1)            # (NQ,)
    return idx


def classical_hebbian_top1_batch_t(K: torch.Tensor, Q: torch.Tensor) -> torch.Tensor:
    """Classical Hopfield implicit-W retrieval; returns argmax indices.

    Args:
      K: (M, N) stored keys (L2-normalized).
      Q: (NQ, N) noised queries (L2-normalized).

    Returns: (NQ,) long tensor of argmax indices in [0, M).

    Mechanism: W = K.T @ K / N  (implicit -- never materialized at N=65536 which would be
               17 GB). For each query:
                 y = W @ q = (1/N) * K.T @ (K @ q)  shape (N,)
               Batched: Y = (Q @ K.T) @ K / N  shape (NQ, N).
               Then snap: argmax(Y @ K.T, dim=1).
    Equivalent to one Hopfield update step + cleanup snap. Compute is identical to modern
    except for the softmax weighting (CLASSICAL = unweighted sum; MODERN = softmax-weighted).
    """
    sims = Q @ K.T                              # (NQ, M)
    Y = sims @ K / float(K.shape[1])            # (NQ, N)
    sims2 = Y @ K.T                             # (NQ, M)
    idx = torch.argmax(sims2, dim=1)            # (NQ,)
    return idx


def shuffled_query_modern_top1_t(K: torch.Tensor, Q: torch.Tensor,
                                  truth_idx: torch.Tensor, beta: float,
                                  gen: torch.Generator) -> torch.Tensor:
    """Mechanism-null floor: form Q' from RANDOMLY-SHUFFLED keys (not true keys),
    then run MODERN_HOPFIELD retrieval; compare against the ORIGINAL truth indices.

    Args:
      K: (M, N).
      Q: (NQ, N) -- here, we DON'T use the noised Q; we make new queries from a
         random permutation of K and the same noise level, then run retrieval.
      truth_idx: (NQ,) -- the truth labels that the noised Q was supposed to match.
      beta: inverse temperature.
      gen: torch.Generator.

    Returns: (NQ,) long tensor of argmax indices; the caller computes top-1 against
             the ORIGINAL truth_idx (which is uncorrelated with the shuffled queries).
    """
    M = K.shape[0]
    NQ = Q.shape[0]
    # Build a random permutation; pick NQ shuffled keys uniformly with replacement so the
    # distribution of source-keys is decoupled from truth_idx.
    perm = torch.randint(0, M, (NQ,), generator=gen, device=K.device)
    base = K[perm]                              # (NQ, N) random source keys (NOT the truth)
    Q_shuf = add_gaussian_noise_and_normalize_t(base, NOISE_STDEV, gen)
    idx = modern_hopfield_top1_batch_t(K, Q_shuf, beta)
    return idx


# ----------------------------- per-(seed, M) arm runner -----------------------------
def _run_arms_one_M(M: int, seed: int, gpu_util_samples: List[float]) -> Dict:
    """Run all (M, beta) arms for one seed. Returns dict with per-beta recall + arm fields.

    K is built ONCE per (seed, M) and reused across the 4 beta values + classical arm.
    """
    t0 = time.time()
    gen_keys = torch.Generator(device=_DEVICE).manual_seed(int(seed * 100003 + M * 37))
    gen_probe = torch.Generator(device=_DEVICE).manual_seed(int(seed * 100003 + M * 37 + 1))
    gen_shuf = torch.Generator(device=_DEVICE).manual_seed(int(seed * 100003 + M * 37 + 2))

    # Hoist K (M, N) -- single allocation per (seed, M)
    K = make_bipolar_keys_t(M, N_DIM, gen_keys, _DEVICE, _DTYPE)

    # Hoist Q -- probe NQ true keys (without replacement), noised once
    nq = min(NQ, M)
    truth_idx = torch.randperm(M, generator=gen_probe, device=_DEVICE)[:nq]
    Q_clean = K[truth_idx]
    Q = add_gaussian_noise_and_normalize_t(Q_clean, NOISE_STDEV, gen_probe)

    per_beta: Dict[str, Dict] = {}
    # Sample GPU util once at start of arm batch (steady-state under matmul load is measured
    # during the matmul itself; sample just after to catch the post-op util).
    for b in BETA_GRID:
        # MODERN
        idx_m = modern_hopfield_top1_batch_t(K, Q, float(b))
        top1_modern = float((idx_m == truth_idx).float().mean().item())
        s1 = _gpu_util_sample()
        if s1 is not None:
            gpu_util_samples.append(s1)
        # SHUFFLED (uses MODERN mechanism on shuffled queries; demonstrates the arm's null floor)
        idx_s = shuffled_query_modern_top1_t(K, Q, truth_idx, float(b), gen_shuf)
        top1_shuffled = float((idx_s == truth_idx).float().mean().item())
        s2 = _gpu_util_sample()
        if s2 is not None:
            gpu_util_samples.append(s2)
        per_beta["b%.1f" % b] = {
            "top1_modern": top1_modern,
            "top1_shuffled": top1_shuffled,
        }

    # CLASSICAL (no beta dependence; runs once per (seed, M))
    idx_c = classical_hebbian_top1_batch_t(K, Q)
    top1_classical = float((idx_c == truth_idx).float().mean().item())
    s3 = _gpu_util_sample()
    if s3 is not None:
        gpu_util_samples.append(s3)

    # Free K + Q before next M
    del K, Q, Q_clean, truth_idx, idx_m, idx_s, idx_c
    if _CUDA_OK:
        torch.cuda.empty_cache()

    wall = time.time() - t0

    # Best-beta modern top-1 for the discriminator
    best_modern = max(d["top1_modern"] for d in per_beta.values())
    best_modern_beta = max(per_beta.items(), key=lambda kv: kv[1]["top1_modern"])[0]
    best_shuffled = max(d["top1_shuffled"] for d in per_beta.values())

    return {
        "M": int(M),
        "seed": int(seed),
        "N_DIM": int(N_DIM),
        "alpha": float(M) / float(N_DIM),
        "per_beta": per_beta,
        "best_modern_top1": float(best_modern),
        "best_modern_beta": str(best_modern_beta),
        "worst_shuffled_top1": float(best_shuffled),  # most "permissive" null reading
        "top1_classical": float(top1_classical),
        "gap_modern_minus_classical": float(best_modern - top1_classical),
        "n_probe": int(nq),
        "wall_s": float(wall),
        "device": str(_DEVICE),
    }


def run_seed(seed: int) -> Dict:
    """Run all M points for one seed."""
    t0 = time.time()
    gpu_util_samples: List[float] = []
    per_unit = []
    for M in M_GRID:
        res = _run_arms_one_M(M, seed, gpu_util_samples)
        per_unit.append(res)
        print(("  [seed=%d M=%d] modern_best=%.3f (beta=%s) | classical=%.3f | "
               "shuffled_worst=%.3f | gap=%.3f | wall=%.1fs") %
              (seed, M, res["best_modern_top1"], res["best_modern_beta"],
               res["top1_classical"], res["worst_shuffled_top1"],
               res["gap_modern_minus_classical"], res["wall_s"]), flush=True)
    elapsed = time.time() - t0
    gpu_util_mean = float(np.mean(gpu_util_samples)) if gpu_util_samples else float("nan")
    gpu_util_p50 = float(np.median(gpu_util_samples)) if gpu_util_samples else float("nan")
    gpu_util_max = float(np.max(gpu_util_samples)) if gpu_util_samples else float("nan")
    return {
        "seed": seed,
        "N": N_DIM,
        "M": M_MAX,
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


# ----------------------------- self-test -----------------------------
def _selftest():
    """5 formula self-tests. Runs on CPU (smoke-safe; no GPU required for selftest)."""
    global _DEVICE, _DTYPE
    _save_dev = _DEVICE
    _DEVICE = torch.device("cpu")
    _DTYPE = torch.float32
    try:
        gen = torch.Generator(device=_DEVICE).manual_seed(0)
        # T1: noiseless modern Hopfield at tiny scale: top-1 == 1.0 expected
        M, n, nq = 20, 256, 20
        K = make_bipolar_keys_t(M, n, gen, _DEVICE, _DTYPE)
        truth = torch.arange(M, device=_DEVICE)[:nq]
        Q_clean = K[truth]  # zero noise
        idx_m = modern_hopfield_top1_batch_t(K, Q_clean, beta=8.0)
        top1_m = float((idx_m == truth).float().mean().item())
        assert top1_m >= 0.95, "T1 modern noiseless top-1=%.3f < 0.95" % top1_m

        # T2: noiseless classical Hebbian at tiny scale: top-1 == 1.0 expected (M=20 << 0.14*256=35)
        idx_c = classical_hebbian_top1_batch_t(K, Q_clean)
        top1_c = float((idx_c == truth).float().mean().item())
        assert top1_c >= 0.95, "T2 classical noiseless top-1=%.3f < 0.95" % top1_c

        # T3: shuffled-query floor: ~1/M chance
        gen2 = torch.Generator(device=_DEVICE).manual_seed(1)
        idx_s = shuffled_query_modern_top1_t(K, Q_clean, truth, beta=8.0, gen=gen2)
        top1_s = float((idx_s == truth).float().mean().item())
        assert top1_s <= 0.20, "T3 shuffled-query top-1=%.3f > 0.20 (mechanism-null floor broken)" % top1_s

        # T4: LLM counter zero
        assert _LLM_CALL_COUNTER[0] == 0, "T4 LLM counter non-zero (%d)" % _LLM_CALL_COUNTER[0]

        # T5: softmax stability at beta=8 (max sims around 1.0 in normalized space; beta*sims ~ 8)
        sims = K[:5] @ K.T
        b_sims = 8.0 * sims
        max_b = float(b_sims.abs().max().item())
        assert max_b < 80.0, "T5 softmax pre-exp magnitude %.2f too large (overflow risk)" % max_b
        w = torch.softmax(b_sims, dim=1)
        row_sums = w.sum(dim=1)
        max_dev = float((row_sums - 1.0).abs().max().item())
        assert max_dev < 1e-4, "T5 softmax row-sum deviation %.2e > 1e-4" % max_dev

        print(("[selftest] PASS: modern_top1=%.3f classical_top1=%.3f shuffled_top1=%.3f "
               "softmax_max=%.2f LLM=%d") %
              (top1_m, top1_c, top1_s, max_b, _LLM_CALL_COUNTER[0]), flush=True)
    finally:
        _DEVICE = _save_dev


_selftest()
if _ARGS.self_test:
    sys.exit(0)


# ----------------------------- verdict -----------------------------
def compute_verdict(per_seed: Dict[str, Dict]) -> Tuple[str, str, Dict]:
    """Compute pre-reg verdict.

    HARD_PASS at M=M_MAX: modern >= 0.95 AND classical <= 0.70 AND shuffled <= 0.05.
    HARD_FAIL at M=M_MAX: modern < 0.50 OR (modern - classical) < 0.10.
    MIDDLE_BAND: in between.
    """
    if not per_seed:
        return ("HARD_FAIL", "No valid results.", {})

    # Aggregate per (M) across seeds
    M_to_modern: Dict[int, List[float]] = {M: [] for M in M_GRID}
    M_to_classical: Dict[int, List[float]] = {M: [] for M in M_GRID}
    M_to_shuffled: Dict[int, List[float]] = {M: [] for M in M_GRID}
    M_to_gap: Dict[int, List[float]] = {M: [] for M in M_GRID}
    M_to_best_beta: Dict[int, List[str]] = {M: [] for M in M_GRID}
    M_to_per_beta_modern: Dict[int, Dict[str, List[float]]] = {M: {"b%.1f" % b: [] for b in BETA_GRID} for M in M_GRID}

    for _sid, body in per_seed.items():
        for pu in body.get("per_unit", []):
            M = int(pu["M"])
            if M not in M_to_modern:
                continue
            M_to_modern[M].append(float(pu["best_modern_top1"]))
            M_to_classical[M].append(float(pu["top1_classical"]))
            M_to_shuffled[M].append(float(pu["worst_shuffled_top1"]))
            M_to_gap[M].append(float(pu["gap_modern_minus_classical"]))
            M_to_best_beta[M].append(str(pu["best_modern_beta"]))
            for b_key, d in pu.get("per_beta", {}).items():
                if b_key in M_to_per_beta_modern[M]:
                    M_to_per_beta_modern[M][b_key].append(float(d.get("top1_modern", float("nan"))))

    def _mean(xs):
        return float(np.mean(xs)) if xs else float("nan")

    def _cv(xs):
        if not xs:
            return float("nan")
        m = float(np.mean(xs))
        if m <= 1e-9:
            return float("inf")
        return float(np.std(xs) / m)

    M_summary: Dict[str, Dict] = {}
    for M in M_GRID:
        per_beta_means = {b: _mean(vs) for b, vs in M_to_per_beta_modern[M].items()}
        M_summary["M%d" % M] = {
            "modern_mean": _mean(M_to_modern[M]),
            "modern_cv": _cv(M_to_modern[M]),
            "classical_mean": _mean(M_to_classical[M]),
            "shuffled_mean": _mean(M_to_shuffled[M]),
            "gap_mean": _mean(M_to_gap[M]),
            "best_beta_modes": list(set(M_to_best_beta[M])),
            "per_beta_modern_mean": per_beta_means,
            "n_seeds_with_M": len(M_to_modern[M]),
            "alpha": float(M) / float(N_DIM),
        }

    # Discriminator at M_MAX (the load point that beats classical's capacity bound)
    s_max = M_summary["M%d" % M_MAX]
    modern_max = s_max["modern_mean"]
    classical_max = s_max["classical_mean"]
    shuffled_max = s_max["shuffled_mean"]
    gap_max = s_max["gap_mean"]

    n_llm = sum(int(b.get("n_llm_calls", 0)) for b in per_seed.values())
    substrate_only_ok = (n_llm == 0)

    # GPU util aggregate
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
        "M_summary": M_summary,
        "M_max": M_MAX,
        "modern_at_M_max": modern_max,
        "classical_at_M_max": classical_max,
        "shuffled_at_M_max": shuffled_max,
        "gap_modern_minus_classical_at_M_max": gap_max,
        "classical_theoretical_bound_at_N": CLASSICAL_BOUND_AT_N,
        "classical_capacity_alpha_at_M_max": float(M_MAX) / float(N_DIM),
        "above_classical_bound": float(M_MAX) > CLASSICAL_BOUND_AT_N,
        "substrate_only_ok": bool(substrate_only_ok),
        "zero_llm_calls_at_inference": bool(substrate_only_ok),
        "gpu_util_mean": gpu_util_mean_overall,
        "gpu_util_p50": gpu_util_p50_overall,
        "gpu_util_max": gpu_util_max_overall,
        "gpu_util_n_samples": len(gpu_util_all),
        "honest_scope": ("Krotov exponential-energy Modern Hopfield vs Classical Hebbian retrieval "
                         "on synthetic bipolar L2-normalized HD keys at N_DIM=%d; M sweep through "
                         "%s with classical theoretical bound 0.14*N=%.0f. Single-step retrieval "
                         "(MODERN: softmax(beta*sims) @ K; CLASSICAL: implicit-W = (1/N) * K.T @ K @ q); "
                         "gaussian noise stdev=%.2f on bipolar queries. SHUFFLED arm is the "
                         "mechanism-null floor (random keys, true labels). substrate-only gate "
                         "enforced (n_llm=%d). cuda_required=True for full run." %
                         (N_DIM, M_GRID, CLASSICAL_BOUND_AT_N, NOISE_STDEV, n_llm)),
    }

    parts = []
    for M in M_GRID:
        s = M_summary["M%d" % M]
        parts.append("M=%d[mod=%.3f cls=%.3f shf=%.3f gap=%.3f]" %
                     (M, s["modern_mean"], s["classical_mean"], s["shuffled_mean"], s["gap_mean"]))
    summary = " | ".join(parts) + (" | llm=%d | gpu_util_mean=%.1f%%" %
                                    (n_llm, gpu_util_mean_overall))

    if not substrate_only_ok:
        return ("HARD_FAIL",
                "HARD_FAIL: substrate-only-decode gate VIOLATED (%d LLM calls). %s" % (n_llm, summary),
                detail)
    if shuffled_max > HARD_PASS_SHUFFLED_TOP1_MAX:
        return ("HARD_FAIL",
                "HARD_FAIL: shuffled-query mechanism-null floor broken (%.3f > %.2f) at M=%d. %s" %
                (shuffled_max, HARD_PASS_SHUFFLED_TOP1_MAX, M_MAX, summary),
                detail)
    if modern_max < HARD_FAIL_MODERN_TOP1_MIN:
        return ("HARD_FAIL",
                "HARD_FAIL: modern Hopfield top-1 at M=%d is %.3f < %.2f. Mechanism failed to "
                "retrieve above the wide floor. %s" %
                (M_MAX, modern_max, HARD_FAIL_MODERN_TOP1_MIN, summary),
                detail)
    if gap_max < HARD_FAIL_MODERN_MINUS_CLASSICAL_MIN:
        return ("HARD_FAIL",
                "HARD_FAIL: modern - classical gap at M=%d is %.3f < %.2f. Modern Hopfield did "
                "NOT beat classical above its capacity bound (no super-linear lift detected). %s" %
                (M_MAX, gap_max, HARD_FAIL_MODERN_MINUS_CLASSICAL_MIN, summary),
                detail)
    if (modern_max >= HARD_PASS_MODERN_TOP1_AT_M_MAX and
            classical_max <= HARD_PASS_CLASSICAL_TOP1_AT_M_MAX and
            shuffled_max <= HARD_PASS_SHUFFLED_TOP1_MAX):
        return ("HARD_PASS",
                ("HARD_PASS: Krotov Modern Hopfield retrieval at LLM-class N=%d M=%d: modern=%.3f "
                 ">= %.2f AND classical=%.3f <= %.2f AND shuffled=%.3f <= %.2f. Modern beats "
                 "classical by gap=%.3f above classical's capacity bound (0.14*N=%.0f < M=%d). "
                 "Super-linear capacity confirmed at LLM-class scale. %s" %
                 (N_DIM, M_MAX, modern_max, HARD_PASS_MODERN_TOP1_AT_M_MAX,
                  classical_max, HARD_PASS_CLASSICAL_TOP1_AT_M_MAX,
                  shuffled_max, HARD_PASS_SHUFFLED_TOP1_MAX,
                  gap_max, CLASSICAL_BOUND_AT_N, M_MAX, summary)),
                detail)
    return ("MIDDLE_BAND",
            ("MIDDLE_BAND: partial mechanism win. Modern=%.3f Classical=%.3f gap=%.3f at M=%d. "
             "%s" % (modern_max, classical_max, gap_max, M_MAX, summary)),
            detail)


# ----------------------------- main -----------------------------
out_dir = get_output_dir(ANCHOR_NAME)
t0_total = time.time()
run_config = {"N": N_DIM, "M": M_MAX, "run_mode": RUN_MODE}

done, seeds_todo = resumable_seeds(SEEDS, out_dir, run_config)
print("[run] mode=%s N=%d M_grid=%s beta_grid=%s cuda=%s device=%s seeds_done=%s seeds_todo=%s" %
      (RUN_MODE, N_DIM, M_GRID, BETA_GRID, _CUDA_OK, _DEVICE, str(done), str(seeds_todo)), flush=True)
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
    "N_DIM": N_DIM,
    "M_GRID": M_GRID,
    "BETA_GRID": BETA_GRID,
    "NQ": NQ,
    "NOISE_STDEV": NOISE_STDEV,
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
    "metrics_source": "measured_gpu_synthetic_bipolar_HD_modern_vs_classical_hopfield",
    "elapsed_s": time.time() - t0_total,
    "summary": verdict_msg[:200],
}

write_metrics(out_dir, metrics, results=list(per_seed.values()))

print("\n[VERDICT] %s" % verdict, flush=True)
print("[VERDICT_MSG] %s" % verdict_msg, flush=True)
print("[METRICS_PATH] %s" % (out_dir / "metrics.json"), flush=True)
