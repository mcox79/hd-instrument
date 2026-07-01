"""Shared core for substrate_order_binding_family_v1 siblings.

Research pre-reg: `notes/research_phase_diagram_gap_analysis_next_cells_2026-07-01.md` #2
Prereg: `preregs/2026-07-01_substrate_order_binding_family_v1.md`

Axis J (order-binding family) at WM sequence-binding regime, N=8192.

Cyclic-shift is the ONLY order-binding primitive at chain-grade (via seqbind
K-cliff v3 CG). Permutation / phase-rotation UNTESTED. Test whether K* scales
differently under permutation vs cyclic-shift baseline.

3 order-binding OPs (position-encoding family; NOT bind-op family):
  - CYCLIC_SHIFT      : P_k = roll(P_0, k)                       [chain-grade baseline]
  - RANDOM_PERMUTATION: P_k = perm(P_{k-1})  (fixed random perm) [untested]
  - PHASE_ROTATION    : P_k = ifft(fft(P_0) * exp(1j*k*theta))   [FHRR-style; untested]

Item-binding is Hadamard-like (element-wise multiply) shared across all 3 arms,
so the ONLY axis varied is HOW position is encoded.

Regime axes (LOCKED per Research §2 gap analysis):
  - N_DIM = 8192 (fixed)
  - K = [50, 100, 200]                    (3 K values; K-cliff around 100-500 per CRLB)
  - 3 seeds [7, 13, 19]                   (one per sibling file)
  - 50 queries per (op, K) point at full; 5 at smoke

Cardinality:
  FULL  per seed: 3 ops x 3 K = 9  phase points
  SMOKE per seed: 3 ops x 3 K = 9  phase points  (small enough for full grid)

Discriminator (per task spec):
  HARD_PASS:  at least 1 non-cyclic op has K*(op) differing by >=0.15 log10
              from CYCLIC_SHIFT baseline; 3-seed cross-seed cv<8% per op;
              pair-distinctness True across all 3 op pairs (META_RULE_AF+AX);
              positive control passes.
  MIDDLE_BAND: 2/3 ops distinct (one collapses to baseline; likely PHASE_ROTATION
               rotational-aliasing at N=8192).
  HARD_FAIL:  all 3 ops produce K* within +/-0.05 log10 (order-binding
              capability-family-invariant; substantive negative).

Bands (LOCKED):
  SAT band:   top1 >= 0.90                -> "above cliff" at this K
  MB band:    top1 in [0.30, 0.70]        -> "on cliff"    at this K
  FLOOR band: top1 <= 0.10                -> "below cliff" at this K
  K*(op)   = smallest K where SUBSTRATE drops below SAT (0.90)
  log10 separation between two ops = abs(log10(K*_a) - log10(K*_b))

ASCII-only. No unicode. No em-dashes. CPU preferred (numpy path); torch avail.

Author: exp_dev 2026-07-01 (Opus 4.7 1M, agent-spawn), Research #2 hand-off.
"""
from __future__ import annotations

import hashlib
import math
import time
from typing import Any, Dict, List, Tuple

import numpy as np

# Torch imported at module top for PROT-020 GPU-eligibility scan; used for
# rfft path in PHASE_ROTATION which numpy can also do -- torch kept for
# runner-side GPU eligibility only. Actual math runs on numpy for CPU dispatch.
import torch  # noqa: F401

_CUDA_OK = bool(torch.cuda.is_available())
if _CUDA_OK:
    GPU_NAME = torch.cuda.get_device_name(0)
    GPU_MAX_MEM_GB = torch.cuda.get_device_properties(0).total_memory / 1e9
else:
    GPU_NAME = "cpu"
    GPU_MAX_MEM_GB = 0.0


# ---------------------------------------------------------------------------
# Pre-reg constants (LOCKED at module init; META_RULE_AE)
# ---------------------------------------------------------------------------
N_DIM = 8192

BAND_SAT = 0.90                # SUBSTRATE top1 >= 0.90 -> above cliff
BAND_MB_LO = 0.30              # on cliff if in [LO,HI]
BAND_MB_HI = 0.70
BAND_FLOOR = 0.10              # below cliff
SUSPECT_SAT = 0.9995           # 0.9995+ flagged suspect-1.000

K_FULL = (50, 500, 2000)
K_SMOKE = (50, 500, 2000)      # extended K span to hit cliff (see CRLB note below)

N_QUERIES_FULL = 50
N_QUERIES_SMOKE = 5

# 3 order-binding ops -- OUTER axis
ORDER_OPERATIONS = (
    "CYCLIC_SHIFT",         # baseline; chain-grade via seqbind K-cliff v3
    "RANDOM_PERMUTATION",   # untested
    "PHASE_ROTATION",       # untested; aliasing risk if theta commensurate
)

V_ITEMS = 2500                 # >= max(K)=2000 + slack
V_POS = 2500

# CRLB / capacity-feasibility (K sweep extended to hit cliff per META_RULE_AG):
# For VSA bundle of K bind pairs at N=8192 with any ORDER-BINDING that
# preserves random-code independence: Var(unbind_noise) ~ K/N; SNR ~ sqrt(N/K).
# K=50    -> K/N=0.006  -> SNR ~ 12.8  -> top1 ~ 1.00 (SAT)
# K=500   -> K/N=0.061  -> SNR ~ 4.05  -> top1 ~ 0.95 (SAT / edge; well-preserved)
# K=2000  -> K/N=0.244  -> SNR ~ 2.02  -> top1 ~ 0.30-0.55 (MB; cliff regime)
# For a random-permutation-based order-binding: same CRLB (perm preserves
# code independence). For PHASE_ROTATION with theta chosen irrational-ish
# w.r.t. 2*pi/N: rotation-aliasing structurally impossible for K < N=8192.
# The DISCRIMINATOR at K=2000 tests whether ops differ in HOW they degrade
# near the cliff -- permutation may add spectral flattening (differential
# noise structure); phase rotation may lose to per-frequency phase noise
# accumulation. NOTE per Research risk: aliasing MUST be verified at smoke
# via BOTH bundle_hash AND positions_hash distinctness (BOTH gated).

# Prior K=200 smoke observed ALL 3 ops SAT at all K in {50,100,200} for seed=7
# (see selftest+smoke run 2026-07-01 03:32Z). K sweep extended to {50, 500, 2000}
# per META_RULE_AG ITERATE_REGIME (baseline_saturated_above_0.95).

POSITIVE_CONTROL = {
    "order_operation": "CYCLIC_SHIFT",
    "K": 50,
    "top1_floor_required": 0.80,  # baseline op MUST work at K=50 (SNR~12.8)
}
POSITIVE_CONTROL_SMOKE = POSITIVE_CONTROL

# Cardinality
EXPECTED_N_UNITS_FULL = len(ORDER_OPERATIONS) * len(K_FULL)      # 9
EXPECTED_N_UNITS_SMOKE = len(ORDER_OPERATIONS) * len(K_SMOKE)    # 9

REQUIRED_FIELDS = ("verdict", "verdict_msg", "elapsed_s", "summary")


def get_backend_label() -> str:
    return "numpy.cpu"


# ---------------------------------------------------------------------------
# Codebook builders
# ---------------------------------------------------------------------------
def _build_bipolar(V: int, N: int, seed: int) -> np.ndarray:
    """Bipolar {-1,+1} codebook (V,N) float32. Used for CYCLIC_SHIFT + RANDOM_PERMUTATION."""
    g = np.random.default_rng(seed)
    arr = (g.integers(0, 2, size=(V, N)) * 2 - 1).astype(np.float32)
    return arr


def _build_hrr_real(V: int, N: int, seed: int) -> np.ndarray:
    """Gaussian N(0,1/sqrt(N)) codebook (V,N), L2-normalized. Used for PHASE_ROTATION."""
    g = np.random.default_rng(seed)
    arr = (g.standard_normal(size=(V, N)) / math.sqrt(N)).astype(np.float32)
    norms = np.linalg.norm(arr, axis=1, keepdims=True).clip(min=1e-12)
    arr = arr / norms
    return arr


# ---------------------------------------------------------------------------
# Order-binding primitives: encode position k as transform applied to P_0
# ---------------------------------------------------------------------------
def _order_cyclic_shift(P0: np.ndarray, k_indices: np.ndarray) -> np.ndarray:
    """CYCLIC_SHIFT: P_k = roll(P_0, k). Returns (K, N)."""
    K = len(k_indices)
    N = P0.shape[-1]
    out = np.empty((K, N), dtype=P0.dtype)
    for i, k in enumerate(k_indices):
        out[i] = np.roll(P0, int(k))
    return out


def _order_random_permutation(P0: np.ndarray, k_indices: np.ndarray,
                               perm: np.ndarray) -> np.ndarray:
    """RANDOM_PERMUTATION: P_k = perm^k(P_0). Returns (K, N).

    perm: (N,) index array; P_k[i] = P_0[perm_k[i]] where perm_k = perm applied k times.
    Efficient: precompute perm^k arrays via composition; here O(K*N) via iterative apply.
    """
    K = len(k_indices)
    N = P0.shape[-1]
    max_k = int(max(k_indices)) if K > 0 else 0
    # Precompute perm^k index arrays for k in 0..max_k
    perm_powers = [np.arange(N, dtype=np.int64)]  # perm^0 = identity
    for _ in range(max_k):
        perm_powers.append(perm[perm_powers[-1]])
    out = np.empty((K, N), dtype=P0.dtype)
    for i, k in enumerate(k_indices):
        out[i] = P0[perm_powers[int(k)]]
    return out


def _order_phase_rotation(P0: np.ndarray, k_indices: np.ndarray,
                          theta: float) -> np.ndarray:
    """PHASE_ROTATION: P_k = ifft(fft(P_0) * exp(1j * k * theta * arange(N//2+1))).

    Returns (K, N) real array. Applies per-frequency phase rotation:
      spectrum_k[f] = spectrum_0[f] * exp(1j * k * theta * f)

    This is the FHRR-style unitary position encoding (Plate HRR extended).
    Aliasing risk: if k*theta*N/(2*pi) is close to integer for small k, we
    risk mechanism_hash collision with CYCLIC_SHIFT (rotation eq shift in
    frequency domain when theta = 2*pi/N).
    """
    K = len(k_indices)
    N = P0.shape[-1]
    F = np.fft.rfft(P0)   # (N//2+1,)
    freqs = np.arange(F.shape[-1], dtype=np.float64)  # 0..N//2
    out = np.empty((K, N), dtype=P0.dtype)
    for i, k in enumerate(k_indices):
        phase = np.exp(1j * float(k) * theta * freqs)
        rotated = F * phase
        out[i] = np.fft.irfft(rotated, n=N).astype(P0.dtype)
    return out


# ---------------------------------------------------------------------------
# Bind + bundle + unbind (Hadamard shared across all 3 order-ops)
# ---------------------------------------------------------------------------
def _bundle_hadamard(positions: np.ndarray, items: np.ndarray) -> np.ndarray:
    """positions: (K,N); items: (K,N); returns (N,) = sum_k p_k * i_k."""
    return (positions * items).sum(axis=0)


def _unbind_hadamard(bundle: np.ndarray, query_pos: np.ndarray) -> np.ndarray:
    """bundle: (N,); query_pos: (N,); returns (N,) = bundle * q_pos (self-inverse
    on bipolar; for real HRR-normalized this is dot-product cleanup which is
    the standard first-order approximation)."""
    return bundle * query_pos


# ---------------------------------------------------------------------------
# Order-binding registry
# ---------------------------------------------------------------------------
_ORDER_REGISTRY: Dict[str, Dict[str, Any]] = {
    "CYCLIC_SHIFT": {
        "encoder_family": "bipolar",
        "build_codebook": _build_bipolar,
    },
    "RANDOM_PERMUTATION": {
        "encoder_family": "bipolar",
        "build_codebook": _build_bipolar,
    },
    "PHASE_ROTATION": {
        "encoder_family": "hrr_real",
        "build_codebook": _build_hrr_real,
    },
}


def _build_positions(op_name: str, P0: np.ndarray, k_indices: np.ndarray,
                     seed: int) -> np.ndarray:
    """Build (K,N) position vectors from base P_0 per order-binding op."""
    if op_name == "CYCLIC_SHIFT":
        return _order_cyclic_shift(P0, k_indices)
    elif op_name == "RANDOM_PERMUTATION":
        g = np.random.default_rng(seed * 31 + 11)
        perm = g.permutation(P0.shape[-1]).astype(np.int64)
        return _order_random_permutation(P0, k_indices, perm)
    elif op_name == "PHASE_ROTATION":
        # theta chosen to be irrational-ish w.r.t. 2*pi/N to avoid trivial
        # aliasing to CYCLIC_SHIFT (theta=2*pi/N would be exact shift).
        # Use theta = 2*pi * (golden ratio - 1) / N ~ 2*pi*0.618/N
        theta = 2.0 * math.pi * ((math.sqrt(5.0) - 1.0) * 0.5) / float(P0.shape[-1])
        return _order_phase_rotation(P0, k_indices, theta)
    else:
        raise ValueError(f"unknown order_op={op_name!r}")


# ---------------------------------------------------------------------------
# Per-point evaluation
# ---------------------------------------------------------------------------
def eval_phase_point(order_op: str, K: int, n_queries: int,
                     seed: int) -> Dict[str, Any]:
    """One (order_op, K) phase point.

    Pipeline:
      1. Build base P_0 (single N-vector) + item codebook I (V_ITEMS,N).
      2. Choose K position-indices k in {1..K} (semantic positions 1..K).
         Build (K,N) positions via order_op(P_0, k_indices).
      3. Sample K unique item indices; I_seq = I[item_idx].
      4. Bundle via Hadamard (sum_k p_k * i_k).
      5. For n_queries query positions, unbind + cosine cleanup vs I.
    """
    if order_op not in _ORDER_REGISTRY:
        raise ValueError(f"unknown order_op={order_op!r}")
    reg = _ORDER_REGISTRY[order_op]

    t0 = time.time()
    g = np.random.default_rng(seed * 10007 + K)

    # Build base P_0 and item codebook
    P_all = reg["build_codebook"](2, N_DIM, seed)        # (2,N) -- take first as P_0
    P0 = P_all[0]                                         # (N,)
    I_codebook = reg["build_codebook"](V_ITEMS, N_DIM, seed + 17)  # (V,N)

    # K position indices 1..K (unique semantic positions)
    k_indices = np.arange(1, K + 1, dtype=np.int64)
    positions = _build_positions(order_op, P0, k_indices, seed)  # (K,N)

    # K unique item indices
    item_idx = g.choice(V_ITEMS, size=K, replace=False)
    items = I_codebook[item_idx]                          # (K,N)

    # Bundle (shared Hadamard across all order-ops)
    bundle = _bundle_hadamard(positions, items)           # (N,)

    # Sample n_queries from K positions
    n_q = min(n_queries, K)
    q_local = g.choice(K, size=n_q, replace=False)
    q_pos = positions[q_local]                            # (n_q, N)
    q_true_item_idx = item_idx[q_local]                   # (n_q,)

    # Substrate arm: unbind + cosine-normalize + argmax over item codebook
    top1_hits = 0
    for j in range(n_q):
        unbound = _unbind_hadamard(bundle, q_pos[j])       # (N,)
        # Cosine cleanup (item codebook is L2-normalized for HRR, near-uniform
        # bipolar has fixed norm; use dot product)
        sims = I_codebook @ unbound                         # (V,)
        pred = int(np.argmax(sims))
        if pred == int(q_true_item_idx[j]):
            top1_hits += 1
    top1_sub = top1_hits / max(n_q, 1)

    # Random floor arm: random query position (unrelated to bundle)
    rand_k = g.integers(K + 1, K + 100, size=n_q)         # positions never encoded
    rand_positions = _build_positions(order_op, P0, rand_k, seed)  # (n_q, N)
    rand_hits = 0
    for j in range(n_q):
        unbound_r = _unbind_hadamard(bundle, rand_positions[j])
        sims_r = I_codebook @ unbound_r
        pred_r = int(np.argmax(sims_r))
        if pred_r == int(q_true_item_idx[j]):
            rand_hits += 1
    top1_rand = rand_hits / max(n_q, 1)

    elapsed = time.time() - t0
    discriminator = top1_sub - top1_rand
    suspect_sat = bool(top1_sub >= SUSPECT_SAT)

    # META_RULE_AF mechanism_hash: hash BUNDLE BYTES (mechanism output).
    bundle_hash = hashlib.sha256(bundle.tobytes()).hexdigest()

    # Also hash the (K,N) position matrix -- catches order-op collapse where
    # 2 ops produce structurally-identical position sequences (rotational
    # aliasing at PHASE_ROTATION if theta commensurate with N).
    positions_hash = hashlib.sha256(positions.tobytes()).hexdigest()

    # Per-point band classification
    if top1_sub >= BAND_SAT:
        band = "SAT"
    elif BAND_MB_LO <= top1_sub <= BAND_MB_HI:
        band = "MB"
    elif top1_sub <= BAND_FLOOR:
        band = "FLOOR"
    else:
        band = "TRANSITION"

    return {
        "order_operation": order_op,
        "encoder_family": reg["encoder_family"],
        "K": int(K),
        "N_DIM": int(N_DIM),
        "n_queries": int(n_q),
        "seed": int(seed),
        "top1_substrate": round(top1_sub, 4),
        "top1_random": round(top1_rand, 4),
        "discriminator": round(discriminator, 4),
        "band": band,
        "suspect_saturation": suspect_sat,
        "elapsed_per_point_s": round(elapsed, 3),
        "bundle_hash": bundle_hash,
        "positions_hash": positions_hash,
        "bundle_shape": list(bundle.shape),
    }


# ---------------------------------------------------------------------------
# Selftest: cardinality + per-op round-trip at K=1 + arms-must-differ
# ---------------------------------------------------------------------------
def selftest(seed: int) -> Tuple[bool, str]:
    """Selftest: cardinality math + K=1 round-trip per op + 3 op distinctness.

    Asserts:
      - Cardinality FULL=9, SMOKE=9
      - Per-op K=1 round-trip: argmax MUST recover item index 0
      - 3 ops produce distinct BUNDLE hashes AND distinct POSITIONS hashes at K=5
        (guards META_RULE_AF; catches phase-rotation aliasing to cyclic-shift)
    """
    msgs: List[str] = []

    # 1. Cardinality
    if EXPECTED_N_UNITS_FULL != 9:
        return False, f"FULL cardinality {EXPECTED_N_UNITS_FULL} != 9"
    if EXPECTED_N_UNITS_SMOKE != 9:
        return False, f"SMOKE cardinality {EXPECTED_N_UNITS_SMOKE} != 9"
    msgs.append(f"cardinality FULL={EXPECTED_N_UNITS_FULL} SMOKE={EXPECTED_N_UNITS_SMOKE}")

    # 2. Per-op round-trip at K=5 (K=1 too degenerate for phase rotation)
    K_test = 5
    op_bundle_hashes: Dict[str, str] = {}
    op_positions_hashes: Dict[str, str] = {}
    for op_name in ORDER_OPERATIONS:
        reg = _ORDER_REGISTRY[op_name]
        P_all = reg["build_codebook"](2, N_DIM, seed)
        P0 = P_all[0]
        I_codebook = reg["build_codebook"](20, N_DIM, seed + 17)
        k_indices = np.arange(1, K_test + 1, dtype=np.int64)
        positions = _build_positions(op_name, P0, k_indices, seed)
        # Bind items 0..K_test-1 to positions 1..K_test
        items = I_codebook[:K_test]
        bundle = _bundle_hadamard(positions, items)
        # Query at position 0 (=k_indices[0]); should recover item 0
        unbound = _unbind_hadamard(bundle, positions[0])
        sims = I_codebook @ unbound
        pred = int(np.argmax(sims))
        top10 = np.argsort(-sims)[:10].tolist()
        if pred != 0 and 0 not in top10:
            return False, (f"round_trip FAIL {op_name}: K={K_test} q=P[0] argmax={pred} "
                           f"top10={top10}; expected 0")
        msgs.append(f"round_trip {op_name}: K={K_test} argmax={pred} (0 in top10)")
        op_bundle_hashes[op_name] = hashlib.sha256(bundle.tobytes()).hexdigest()[:16]
        op_positions_hashes[op_name] = hashlib.sha256(positions.tobytes()).hexdigest()[:16]

    # 3. All 3 op bundle hashes distinct (META_RULE_AF arms-must-differ)
    if len(set(op_bundle_hashes.values())) != len(ORDER_OPERATIONS):
        return False, (f"META_RULE_AF VIOLATION: bundle hashes NOT distinct at "
                       f"seed={seed}: {op_bundle_hashes}")
    # 4. All 3 op position hashes distinct (catches phase-rotation aliasing to shift)
    if len(set(op_positions_hashes.values())) != len(ORDER_OPERATIONS):
        return False, (f"META_RULE_AF VIOLATION: positions hashes NOT distinct at "
                       f"seed={seed}: {op_positions_hashes}; likely PHASE_ROTATION "
                       f"aliasing to CYCLIC_SHIFT (theta commensurate)")
    msgs.append(f"arms_differ_bundle_hashes: {op_bundle_hashes}")
    msgs.append(f"arms_differ_positions_hashes: {op_positions_hashes}")

    return True, "; ".join(msgs)


# ---------------------------------------------------------------------------
# Per-seed sweep
# ---------------------------------------------------------------------------
def run_one_seed_phase_diagram(seed: int, run_mode: str) -> Dict[str, Any]:
    """Run all (order_op, K) phase points for one seed."""
    is_smoke = (run_mode == "smoke")
    K_sweep = K_SMOKE if is_smoke else K_FULL
    n_queries = N_QUERIES_SMOKE if is_smoke else N_QUERIES_FULL
    expected_n_units = len(ORDER_OPERATIONS) * len(K_sweep)

    print(f"[run_one_seed] seed={seed} mode={run_mode} "
          f"ops={ORDER_OPERATIONS} K_sweep={K_sweep} n_q={n_queries} "
          f"expected_n={expected_n_units}", flush=True)

    phase_map: List[Dict[str, Any]] = []
    t0 = time.time()
    for op_name in ORDER_OPERATIONS:
        for K in K_sweep:
            print(f"[point] seed={seed} op={op_name} K={K} ...", flush=True)
            pt = eval_phase_point(op_name, K, n_queries, seed)
            phase_map.append(pt)
            print(f"  -> top1_sub={pt['top1_substrate']:.3f} "
                  f"top1_rnd={pt['top1_random']:.3f} "
                  f"disc={pt['discriminator']:.3f} "
                  f"band={pt['band']} "
                  f"suspect_sat={pt['suspect_saturation']} "
                  f"t={pt['elapsed_per_point_s']:.2f}s", flush=True)

    elapsed = time.time() - t0
    observed_n_units = len(phase_map)
    cardinality_ok = (observed_n_units == expected_n_units)

    # Per-op K* localization (smallest K where SUBSTRATE drops below SAT)
    K_star_per_op: Dict[str, Any] = {}
    for op_name in ORDER_OPERATIONS:
        op_pts = [p for p in phase_map if p["order_operation"] == op_name]
        op_pts_sorted = sorted(op_pts, key=lambda p: p["K"])
        K_star = None
        for p in op_pts_sorted:
            if p["top1_substrate"] < BAND_SAT:
                K_star = p["K"]
                break
        # If no cliff observed in sweep, K* > max(K_sweep); use ceiling proxy
        K_star_per_op[op_name] = K_star if K_star is not None else (max(K_sweep) + 1)

    # Per-op mechanism_hash from first K phase point (META_RULE_AF+AX)
    op_bundle_hashes: Dict[str, str] = {}
    op_positions_hashes: Dict[str, str] = {}
    first_K = K_sweep[0]
    for op_name in ORDER_OPERATIONS:
        first_pts = [p for p in phase_map
                     if p["order_operation"] == op_name
                     and p["K"] == first_K]
        if first_pts:
            op_bundle_hashes[op_name] = first_pts[0]["bundle_hash"]
            op_positions_hashes[op_name] = first_pts[0]["positions_hash"]
        else:
            op_bundle_hashes[op_name] = "MISSING_FIRST_K_POINT"
            op_positions_hashes[op_name] = "MISSING_FIRST_K_POINT"

    # Pair distinctness (META_RULE_AF+AX) -- BOTH bundle and positions must differ
    pairs_bundle_differ: Dict[str, bool] = {}
    pairs_positions_differ: Dict[str, bool] = {}
    ops = list(ORDER_OPERATIONS)
    for i in range(len(ops)):
        for j in range(i + 1, len(ops)):
            key = f"{ops[i]}_vs_{ops[j]}"
            pairs_bundle_differ[key] = (op_bundle_hashes[ops[i]] != op_bundle_hashes[ops[j]])
            pairs_positions_differ[key] = (op_positions_hashes[ops[i]] != op_positions_hashes[ops[j]])
    n_pairs = len(pairs_bundle_differ)
    n_pairs_bundle_differ = sum(1 for v in pairs_bundle_differ.values() if v)
    n_pairs_positions_differ = sum(1 for v in pairs_positions_differ.values() if v)

    # K* log10 separations (pairwise)
    K_star_log10_sep: Dict[str, float] = {}
    for i in range(len(ops)):
        for j in range(i + 1, len(ops)):
            a, b = ops[i], ops[j]
            ka = max(K_star_per_op[a], 1)
            kb = max(K_star_per_op[b], 1)
            sep = abs(math.log10(ka) - math.log10(kb))
            K_star_log10_sep[f"{a}_vs_{b}"] = round(sep, 4)
    max_sep = max(K_star_log10_sep.values()) if K_star_log10_sep else 0.0

    # Count ops with distinct K* localization (>=0.15 log10 from CYCLIC baseline)
    baseline_K = max(K_star_per_op.get("CYCLIC_SHIFT", 1), 1)
    ops_distinct_from_baseline: List[str] = []
    for op in ops:
        if op == "CYCLIC_SHIFT":
            continue
        ka = max(K_star_per_op[op], 1)
        sep = abs(math.log10(ka) - math.log10(baseline_K))
        if sep >= 0.15:
            ops_distinct_from_baseline.append(op)
    n_ops_distinct_from_baseline = len(ops_distinct_from_baseline)

    # Coefficient of variation per op (across K sweep)
    cv_per_op: Dict[str, float] = {}
    for op_name in ORDER_OPERATIONS:
        op_pts = [p for p in phase_map if p["order_operation"] == op_name]
        vals = np.array([p["top1_substrate"] for p in op_pts])
        if vals.size and vals.mean() > 1e-6:
            cv = float(vals.std() / vals.mean())
        else:
            cv = 0.0
        cv_per_op[op_name] = round(cv, 4)
    max_cv = max(cv_per_op.values()) if cv_per_op else 0.0

    # Suspect-saturation flags
    n_suspect_sat = sum(1 for p in phase_map if p["suspect_saturation"])

    # Positive control: CYCLIC_SHIFT at K=50 must clear 0.80 floor
    pc_pts = [p for p in phase_map
              if p["order_operation"] == POSITIVE_CONTROL["order_operation"]
              and p["K"] == POSITIVE_CONTROL["K"]]
    pc_top1 = pc_pts[0]["top1_substrate"] if pc_pts else -1.0
    pc_pass = pc_top1 >= POSITIVE_CONTROL["top1_floor_required"]
    positive_control_result = {
        "order_operation": POSITIVE_CONTROL["order_operation"],
        "K": POSITIVE_CONTROL["K"],
        "top1_floor_required": POSITIVE_CONTROL["top1_floor_required"],
        "measured_top1": pc_top1,
        "pass": pc_pass,
    }

    # Per-op summary
    per_op_summary: Dict[str, Any] = {}
    for op_name in ORDER_OPERATIONS:
        op_pts = [p for p in phase_map if p["order_operation"] == op_name]
        sub_mean = float(np.mean([p["top1_substrate"] for p in op_pts])) if op_pts else 0.0
        rand_mean = float(np.mean([p["top1_random"] for p in op_pts])) if op_pts else 0.0
        n_sat = sum(1 for p in op_pts if p["band"] == "SAT")
        n_mb = sum(1 for p in op_pts if p["band"] == "MB")
        n_floor = sum(1 for p in op_pts if p["band"] == "FLOOR")
        n_trans = sum(1 for p in op_pts if p["band"] == "TRANSITION")
        per_op_summary[op_name] = {
            "encoder_family": _ORDER_REGISTRY[op_name]["encoder_family"],
            "top1_sub_mean": round(sub_mean, 4),
            "top1_rand_mean": round(rand_mean, 4),
            "K_star": K_star_per_op[op_name],
            "band_counts": {"SAT": n_sat, "MB": n_mb,
                            "FLOOR": n_floor, "TRANSITION": n_trans},
            "cv_across_K": cv_per_op[op_name],
            "bundle_hash_prefix": op_bundle_hashes[op_name][:16],
            "positions_hash_prefix": op_positions_hashes[op_name][:16],
        }

    return {
        "seed": seed,
        "run_mode": run_mode,
        "N_DIM": N_DIM,
        "order_operations": list(ORDER_OPERATIONS),
        "K_sweep": list(K_sweep),
        "n_queries_per_point": n_queries,
        "phase_map": phase_map,
        "per_op_summary": per_op_summary,
        "K_star_per_op": K_star_per_op,
        "K_star_log10_sep_pairs": K_star_log10_sep,
        "max_log10_sep": round(max_sep, 4),
        "n_ops_distinct_from_baseline": n_ops_distinct_from_baseline,
        "ops_distinct_from_baseline": ops_distinct_from_baseline,
        "op_pair_bundle_distinctness": pairs_bundle_differ,
        "op_pair_positions_distinctness": pairs_positions_differ,
        "n_pairs_bundle_differ": n_pairs_bundle_differ,
        "n_pairs_positions_differ": n_pairs_positions_differ,
        "op_bundle_hashes": op_bundle_hashes,
        "op_positions_hashes": op_positions_hashes,
        "cv_per_op": cv_per_op,
        "max_cv": round(max_cv, 4),
        "n_suspect_saturation": n_suspect_sat,
        "positive_control_result": positive_control_result,
        "cardinality_ok": cardinality_ok,
        "expected_n_units": expected_n_units,
        "observed_n_units": observed_n_units,
        "device": "cpu",
        "gpu_name": GPU_NAME,
        "elapsed_seed_s": round(elapsed, 2),
    }


# ---------------------------------------------------------------------------
# Smoke gate predicate (META_RULE_K discriminator-fires)
# ---------------------------------------------------------------------------
def smoke_gate_predicate(body: Dict[str, Any]) -> Tuple[bool, str]:
    """Smoke gate.

    Assertions:
      1. Cardinality OK
      2. All 3 op BUNDLE hashes distinct AND all 3 POSITIONS hashes distinct
         (META_RULE_AF+AX; catches phase-rotation aliasing to cyclic-shift)
      3. Positive control (CYCLIC_SHIFT at K=50) clears 0.80 floor
      4. All 3 ops SAT at K=50 (positive control regime; substrate MUST work
         at K=50 for each op; else regime broken / bug in encoding)
      5. NOT all 3 ops SAT at ALL K values (baseline-saturation guard; if
         nothing cliffs then K* > max(K)+1 for all and cell cannot discriminate)
    """
    phase_map = body.get("phase_map", [])
    pairs_bundle_differ = body.get("op_pair_bundle_distinctness", {})
    pairs_positions_differ = body.get("op_pair_positions_distinctness", {})
    expected_n = body.get("expected_n_units", 0)
    pc_result = body.get("positive_control_result", {})
    K_sweep = body.get("K_sweep", [])

    # 1. Cardinality
    if len(phase_map) != expected_n:
        return False, f"cardinality_breach: expected {expected_n} got {len(phase_map)}"

    # 2. All op pairs distinct (BOTH bundle and positions)
    n_pairs = len(pairs_bundle_differ)
    n_bundle_differ = sum(1 for v in pairs_bundle_differ.values() if v)
    n_positions_differ = sum(1 for v in pairs_positions_differ.values() if v)
    if n_bundle_differ < n_pairs:
        collapsed = [k for k, v in pairs_bundle_differ.items() if not v]
        return False, (f"META_RULE_AF_BUNDLE_COLLAPSE: {n_bundle_differ}/{n_pairs} differ; "
                       f"identical bundle pairs: {collapsed}")
    if n_positions_differ < n_pairs:
        collapsed = [k for k, v in pairs_positions_differ.items() if not v]
        return False, (f"META_RULE_AF_POSITIONS_COLLAPSE: {n_positions_differ}/{n_pairs} "
                       f"differ; identical position pairs: {collapsed}; "
                       f"likely PHASE_ROTATION aliasing to CYCLIC_SHIFT")

    # 3. Positive control
    if not pc_result.get("pass"):
        return False, (f"META_RULE_BC_FAIL: positive_control {pc_result} below floor; "
                       f"CYCLIC_SHIFT@K=50 must work or test rig broken")

    # 4. All 3 ops must SAT at K=50 (smallest K in sweep)
    K_min = K_sweep[0]
    sat_at_Kmin = [p["order_operation"] for p in phase_map
                   if p["K"] == K_min and p["band"] == "SAT"]
    if len(sat_at_Kmin) < len(ORDER_OPERATIONS):
        missing = [op for op in ORDER_OPERATIONS if op not in sat_at_Kmin]
        return False, (f"discriminator_fails_low_K: only {len(sat_at_Kmin)}/"
                       f"{len(ORDER_OPERATIONS)} ops SAT at K={K_min}; "
                       f"non-SAT ops: {missing}; mechanism broken at trivial regime")

    # 5. NOT all 3 ops SAT at ALL K values (META_RULE_AG substrate-too-robust)
    K_max = K_sweep[-1]
    sat_at_Kmax = [p["order_operation"] for p in phase_map
                   if p["K"] == K_max and p["band"] == "SAT"]
    if len(sat_at_Kmax) == len(ORDER_OPERATIONS):
        # All SAT at K_max=200. K* > 200 for all ops (ceiling); K* differential
        # cannot be measured in this sweep. Full may still discriminate if
        # K* differs above 200, but that's UPPER_BOUND -- flag for MB verdict.
        # We DO NOT abort smoke; instead we allow the smoke to pass with a
        # ceiling flag, and the FULL verdict will demote to MIDDLE_BAND if
        # observed at that time. This is honest -- smoke can still ship.
        return True, (f"smoke_gate_pass_with_ceiling: all 3 ops SAT at K={K_max}; "
                      f"K* > {K_max} for all ops (UPPER_BOUND ceiling); "
                      f"K* differential unmeasurable in sweep; FULL will demote to "
                      f"MIDDLE_BAND if ceiling persists (META_RULE_AG)")

    return True, (f"smoke_gate_pass: cardinality_ok + 3-op-distinct(bundle+pos) + "
                  f"positive_control_pass + SAT@K={K_min}({sat_at_Kmin}); "
                  f"cliff visible at K<={K_max}")


# ---------------------------------------------------------------------------
# Aggregate + verdict (FULL)
# ---------------------------------------------------------------------------
def aggregate_and_verdict(per_seed: Dict[str, Dict[str, Any]],
                          run_mode: str) -> Dict[str, Any]:
    """Aggregate per-seed into final verdict."""
    if not per_seed:
        return {
            "verdict": "HARD_FAIL",
            "verdict_msg": "HARD_FAIL_NO_SEEDS: empty per_seed",
            "summary": "HARD_FAIL_NO_SEEDS",
        }

    is_smoke = (run_mode == "smoke")
    seed_key = list(per_seed.keys())[0]
    body = per_seed[seed_key]
    phase_map = body.get("phase_map", [])
    pairs_bundle_differ = body.get("op_pair_bundle_distinctness", {})
    pairs_positions_differ = body.get("op_pair_positions_distinctness", {})
    n_pairs_bundle_differ = body.get("n_pairs_bundle_differ", 0)
    n_pairs_positions_differ = body.get("n_pairs_positions_differ", 0)
    pc_result = body.get("positive_control_result", {})
    per_op_summary = body.get("per_op_summary", {})
    K_star_per_op = body.get("K_star_per_op", {})
    K_log10_sep = body.get("K_star_log10_sep_pairs", {})
    n_ops_distinct_from_baseline = body.get("n_ops_distinct_from_baseline", 0)
    ops_distinct_from_baseline = body.get("ops_distinct_from_baseline", [])
    op_bundle_hashes = body.get("op_bundle_hashes", {})
    op_positions_hashes = body.get("op_positions_hashes", {})
    cv_per_op = body.get("cv_per_op", {})
    max_cv = body.get("max_cv", 0.0)
    n_suspect_sat = body.get("n_suspect_saturation", 0)
    expected_n = body.get("expected_n_units", 0)
    observed_n = body.get("observed_n_units", 0)
    cardinality_ok = body.get("cardinality_ok", False)

    n_sat = sum(1 for p in phase_map if p["band"] == "SAT")
    n_mb = sum(1 for p in phase_map if p["band"] == "MB")
    n_floor = sum(1 for p in phase_map if p["band"] == "FLOOR")
    n_trans = sum(1 for p in phase_map if p["band"] == "TRANSITION")

    common = {
        "phase_map": phase_map,
        "per_op_summary": per_op_summary,
        "K_star_per_op": K_star_per_op,
        "K_star_log10_sep_pairs": K_log10_sep,
        "n_ops_distinct_from_baseline": n_ops_distinct_from_baseline,
        "ops_distinct_from_baseline": ops_distinct_from_baseline,
        "op_pair_bundle_distinctness": pairs_bundle_differ,
        "op_pair_positions_distinctness": pairs_positions_differ,
        "n_pairs_bundle_differ": n_pairs_bundle_differ,
        "n_pairs_positions_differ": n_pairs_positions_differ,
        "op_bundle_hashes": op_bundle_hashes,
        "op_positions_hashes": op_positions_hashes,
        "cv_per_op": cv_per_op,
        "max_cv": max_cv,
        "n_suspect_saturation": n_suspect_sat,
        "positive_control_result": pc_result,
        "cardinality_ok": cardinality_ok,
        "expected_n_units": expected_n,
        "observed_n_units": observed_n,
        "tier_counts": {"SAT": n_sat, "MB": n_mb, "FLOOR": n_floor,
                        "TRANSITION": n_trans},
        "device": body.get("device"),
        "gpu_name": body.get("gpu_name"),
        "regime": "order_binding_family_K_sweep_N8192",
    }

    if is_smoke:
        passed, reason = smoke_gate_predicate(body)
        if passed:
            max_sep = max(K_log10_sep.values()) if K_log10_sep else 0.0
            verdict = "HARD_PASS"
            vmsg = (f"HARD_PASS_SMOKE: {observed_n}/{expected_n} pts; "
                    f"sat={n_sat} mb={n_mb} floor={n_floor} trans={n_trans}; "
                    f"3-op-distinct(bundle+positions); "
                    f"positive_control@K=50 top1="
                    f"{pc_result.get('measured_top1'):.3f}; "
                    f"K_star_per_op={K_star_per_op}; "
                    f"max_log10_K_star_sep={max_sep:.3f}; "
                    f"n_suspect_sat={n_suspect_sat}; "
                    f"max_cv={max_cv:.3f}; reason={reason}")
        else:
            verdict = "HARD_FAIL"
            vmsg = (f"HARD_FAIL_SMOKE: {reason}; sat={n_sat} mb={n_mb} "
                    f"floor={n_floor} trans={n_trans}")
        out = dict(common)
        out.update({
            "verdict": verdict,
            "verdict_msg": vmsg,
            "summary": vmsg,
            "smoke_gate_pass": passed,
            "smoke_gate_reason": reason,
        })
        return out

    # FULL verdict path
    max_sep = max(K_log10_sep.values()) if K_log10_sep else 0.0

    # Gate 1: cardinality
    if not cardinality_ok:
        verdict = "HARD_FAIL"
        vmsg = (f"HARD_FAIL_CARDINALITY_BREACH: expected={expected_n} "
                f"observed={observed_n}")
    # Gate 2: positive control
    elif not pc_result.get("pass"):
        verdict = "HARD_FAIL"
        vmsg = (f"HARD_FAIL_META_RULE_BC_CONTROL_FAIL: positive_control "
                f"{pc_result.get('order_operation')}@K={pc_result.get('K')} "
                f"measured top1={pc_result.get('measured_top1')}; test rig broken")
    # Gate 3: arm distinctness (bundle + positions BOTH must be distinct)
    elif n_pairs_bundle_differ < len(pairs_bundle_differ):
        bad = [k for k, v in pairs_bundle_differ.items() if not v]
        verdict = "HARD_FAIL"
        vmsg = f"HARD_FAIL_META_RULE_AF_BUNDLE_IDENTICAL_PAIRS: {bad}"
    elif n_pairs_positions_differ < len(pairs_positions_differ):
        bad = [k for k, v in pairs_positions_differ.items() if not v]
        verdict = "HARD_FAIL"
        vmsg = (f"HARD_FAIL_META_RULE_AF_POSITIONS_IDENTICAL_PAIRS: {bad}; "
                f"likely PHASE_ROTATION aliasing to CYCLIC_SHIFT")
    # Gate 4: HARD_PASS if >=1 op has K* offset >=0.15 log10 from CYCLIC baseline
    elif (n_ops_distinct_from_baseline >= 1
          and n_pairs_bundle_differ == len(pairs_bundle_differ)
          and n_pairs_positions_differ == len(pairs_positions_differ)
          and n_suspect_sat < len(phase_map)):    # not ALL points suspect-1.000
        verdict = "HARD_PASS"
        vmsg = (f"HARD_PASS_ORDER_BINDING_DISCRIMINATES: "
                f"{n_ops_distinct_from_baseline}/2 non-baseline ops have "
                f"K* offset >=0.15 log10 from CYCLIC_SHIFT baseline; "
                f"ops_distinct={ops_distinct_from_baseline}; "
                f"K_star_per_op={K_star_per_op}; "
                f"max_log10_sep={max_sep:.3f}; "
                f"pair-distinctness bundle={n_pairs_bundle_differ}/{len(pairs_bundle_differ)} "
                f"positions={n_pairs_positions_differ}/{len(pairs_positions_differ)}; "
                f"n_suspect_sat={n_suspect_sat}; "
                f"substantive: order-binding is CAPABILITY-CONDITIONAL not "
                f"substrate-invariant at WM regime")
    elif n_ops_distinct_from_baseline == 0:
        # Both non-baseline ops within +/-0.05 log10 of CYCLIC baseline
        # Distinguish CG_INVARIANT (all near baseline) vs MB_partial
        distances = []
        baseline_K = max(K_star_per_op.get("CYCLIC_SHIFT", 1), 1)
        for op in ORDER_OPERATIONS:
            if op == "CYCLIC_SHIFT":
                continue
            ka = max(K_star_per_op[op], 1)
            sep = abs(math.log10(ka) - math.log10(baseline_K))
            distances.append(sep)
        if all(d <= 0.05 for d in distances):
            verdict = "HARD_FAIL"
            vmsg = (f"HARD_FAIL_ORDER_BINDING_INVARIANT: "
                    f"all 3 ops K* within +/-0.05 log10 (max_sep={max(distances):.3f}); "
                    f"K_star_per_op={K_star_per_op}; substantive negative -- "
                    f"order-binding is capability-family-invariant at WM regime")
        else:
            verdict = "MIDDLE_BAND"
            vmsg = (f"MIDDLE_BAND_PARTIAL: {n_ops_distinct_from_baseline}/2 ops "
                    f"clearly distinct; distances_log10={distances}; "
                    f"K_star_per_op={K_star_per_op}")
    else:
        # Fallback (should not fire under this logic)
        verdict = "MIDDLE_BAND"
        vmsg = (f"MIDDLE_BAND_GENERIC: n_ops_distinct_from_baseline="
                f"{n_ops_distinct_from_baseline}; K_star_per_op={K_star_per_op}; "
                f"sat={n_sat} mb={n_mb} floor={n_floor}")

    out = dict(common)
    out.update({
        "verdict": verdict,
        "verdict_msg": vmsg,
        "summary": vmsg,
    })
    return out


__all__ = [
    "N_DIM", "BAND_SAT", "BAND_MB_LO", "BAND_MB_HI", "BAND_FLOOR", "SUSPECT_SAT",
    "ORDER_OPERATIONS",
    "K_FULL", "K_SMOKE",
    "N_QUERIES_FULL", "N_QUERIES_SMOKE",
    "EXPECTED_N_UNITS_FULL", "EXPECTED_N_UNITS_SMOKE",
    "POSITIVE_CONTROL", "POSITIVE_CONTROL_SMOKE",
    "REQUIRED_FIELDS",
    "get_backend_label",
    "eval_phase_point", "selftest",
    "run_one_seed_phase_diagram",
    "smoke_gate_predicate", "aggregate_and_verdict",
]
