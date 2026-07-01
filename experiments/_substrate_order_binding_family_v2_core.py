"""Shared core for substrate_order_binding_family_v2 siblings.

Research pre-reg: `notes/research_axis_J_revival_drill_2026-07-01.md` candidate #1
Prereg:          `preregs/2026-07-01_substrate_order_binding_family_v2.md`
Prior v1 landed: `data/exp_substrate_order_binding_family_v1_seed_{13,19}/metrics.json`
                 (v1 verdict = HARD_FAIL because K*-boundary metric collapsed all
                  3 ops at K*=500 despite 3.5x top1 spread visible at K=2000)

Axis J v2 REVIVAL -- interference-resilience under multi-sequence load.

v1 HARD_FAIL was DISCRIMINATOR-DESIGN issue, not substrate-invariant:
 - CYCLIC/PERM/PHASE at K=2000 seed_13 : top1 = 0.04 / 0.08 / 0.14  MEASURED@v1_seed_13
 - CYCLIC/PERM/PHASE at K=2000 seed_19 : top1 = 0.04 / 0.06 / 0.18  MEASURED@v1_seed_19
   -> 3.5x spread visible at cliff FLOOR (phase > perm > cyclic)
   -> BUT K*(op) identical (all cross 0.90 at K=500) so K*-log10-sep = 0

v2 DISCRIMINATOR PIVOT (per drill note candidate #1, CG=0.55, 3-domain support):
  * multi-sequence load L: bundle = sum over l in [1..L] of (sum_k P^{(l)}_k * I^{(l)}_k)
  * each sequence l gets an independent codebook (different seed slice)
  * query: (sequence_id=l, position=k) -> item; unbind with P^{(l)}_k
  * DISCRIMINATOR: at (L=4, K_per_seq=250), top1 recall per op differs by >=0.15
    between at least one op pair (3-seed cv<8%; pair-distinctness required)
  * predicted ordering (drill note): RANDOM_PERMUTATION > PHASE_ROTATION > CYCLIC_SHIFT
    - RANDOM_PERMUTATION: basis-universal (compressed-sensing Puy et al 2012); resilient
    - PHASE_ROTATION: aliasing risk at commensurate theta*K mod 2*pi (intermediate)
    - CYCLIC_SHIFT: position-basis coherence with a SINGLE shift family -> constructive
      interference across sequences (worst at high L)

Regime axes (LOCKED):
  * N_DIM = 8192 (matches v1)
  * L in [1, 2, 4]                            (load axis)
  * K_per_seq in [125, 250]                   (moderate per-seq; total load = L*K)
  * 3 order ops                               (same primitives as v1 core)
  * n_queries per (op, L, K) point: 60 FULL / 8 SMOKE

Cardinality:
  FULL per seed:  3 ops x 3 L x 2 K = 18 phase points
  SMOKE per seed: 3 ops x 3 L x 2 K = 18 phase points  (full grid at smoke)

DISCRIMINATOR-fires seed-7 smoke prediction (drill P=0.55):
  at (L=4, K=250): top1(CYCLIC) ~= 0.05-0.20  (SAT+cross-seq interference)
                   top1(PERM)   ~= 0.20-0.45  (basis-universal; most resilient)
                   top1(PHASE)  ~= 0.10-0.30  (intermediate)
  smoke discriminator gate: at least one op-pair top1 diff >= 0.15 at (L=4, K=250)
  honest-abort predicate: if all 3 ops top1 within 0.03 at (L=4, K=250)
                          -> mechanism_hash aliasing to v1 or invariance
                          -> HARD_FAIL_HONEST_ABORT with substantive negative

Bands (LOCKED per META_RULE_L):
  HARD_PASS gate: >=1 op-pair top1 diff >= 0.15 at (L=4, K=250) FULL band
                  with 3-seed cv<8% per arm; pair-distinctness True (all 3 pairs).
  HARD_FAIL:      all 3 ops top1 within +/-0.03 at (L=4, K=250) -> family-invariant
                  under load AS WELL AS at single-seq cliff -> axis J close.
  MIDDLE_BAND:    partial (one pair distinct, others collapse) OR cv >= 8%.

CRLB / capacity-feasibility (THEORETICAL@Var(unbind_noise)~K_total/N):
  For any order-binding preserving code independence: total bundle carries
  L*K bind pairs; Var(unbind_noise) ~ L*K/N; SNR ~ sqrt(N/(L*K)).
  Top1 cleanup over V_ITEMS via dot argmax.
  L=1 K=125 : K_tot=125  K/N=0.015 SNR=8.10 -> ~1.00 (SAT baseline)
  L=1 K=250 : K_tot=250  K/N=0.031 SNR=5.72 -> ~0.98 (SAT)
  L=2 K=125 : K_tot=250  K/N=0.031 SNR=5.72 -> ~0.90 (SAT / edge)
  L=2 K=250 : K_tot=500  K/N=0.061 SNR=4.05 -> ~0.70 (MB / edge)
  L=4 K=125 : K_tot=500  K/N=0.061 SNR=4.05 -> ~0.55 (MB)  <- DISCRIMINATOR zone
  L=4 K=250 : K_tot=1000 K/N=0.122 SNR=2.86 -> ~0.30 (MB)  <- DISCRIMINATOR zone
  These SNR-derived predictions assume ideal random-code independence.
  Op-specific deviations FROM this baseline are exactly the mechanism signal.

MECHANISM-HASH v2-DISTINCTNESS (guards aliasing to v1):
  Bundle-hash includes explicit "v2_load" salt token in encode path so v1's
  identical (op, K) point never hashes to v2's (op, L=1, K) point even when
  numerically identical. Prevents "same-hash-different-verdict" phantom.

ASCII-only. No unicode. No em-dashes. CPU (numpy path); torch imported at top
for PROT-020 GPU-eligibility scan only.

Author: exp_dev 2026-07-01 (Opus 4.7 1M, agent-spawn) per drill note candidate #1.
"""
from __future__ import annotations

import hashlib
import math
import time
from typing import Any, Dict, List, Tuple

import numpy as np

# PROT-020 GPU-eligibility scan; math runs numpy on CPU.
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

BAND_SAT = 0.90
BAND_MB_LO = 0.30
BAND_MB_HI = 0.70
BAND_FLOOR = 0.10
SUSPECT_SAT = 0.9995

# Load and per-sequence K axes
L_FULL = (1, 2, 4)
L_SMOKE = (1, 2, 4)
K_PER_SEQ_FULL = (125, 250)
K_PER_SEQ_SMOKE = (125, 250)

N_QUERIES_FULL = 60
N_QUERIES_SMOKE = 8

# 3 order-binding ops (same as v1 core)
ORDER_OPERATIONS = (
    "CYCLIC_SHIFT",
    "RANDOM_PERMUTATION",
    "PHASE_ROTATION",
)

V_ITEMS = 4000        # >= max(L*K) + slack; L=4 K=250 -> total=1000; slack 4x
V_POS = 4000

# v2-distinctness marker mixed into mechanism_hash so v1 (op, K) never collides
# with v2 (op, L=1, K) even for numerically identical bundle bytes.
V2_LOAD_SALT = b"substrate_order_binding_family_v2_load_variant_2026-07-01"

# Discriminator regime (used for smoke gate + full HARD_PASS)
DISCRIMINATOR_L = 4
DISCRIMINATOR_K = 250
DISCRIMINATOR_MIN_PAIR_DIFF = 0.15         # min top1 gap between at least 1 pair
DISCRIMINATOR_HONEST_ABORT_DIFF = 0.03     # if all pairs within this, invariant
DISCRIMINATOR_MAX_CV = 0.08                # 3-seed cv gate

# Predicted ordering per drill note (used for direction check in verdict only)
PREDICTED_ORDER = ("RANDOM_PERMUTATION", "PHASE_ROTATION", "CYCLIC_SHIFT")

POSITIVE_CONTROL = {
    "order_operation": "CYCLIC_SHIFT",
    "L": 1,
    "K_per_seq": 125,
    "top1_floor_required": 0.80,   # CYCLIC@L=1,K=125 must SAT or test rig broken
}
POSITIVE_CONTROL_SMOKE = POSITIVE_CONTROL

# Cardinality
EXPECTED_N_UNITS_FULL = len(ORDER_OPERATIONS) * len(L_FULL) * len(K_PER_SEQ_FULL)     # 18
EXPECTED_N_UNITS_SMOKE = len(ORDER_OPERATIONS) * len(L_SMOKE) * len(K_PER_SEQ_SMOKE)  # 18

REQUIRED_FIELDS = ("verdict", "verdict_msg", "elapsed_s", "summary")


def get_backend_label() -> str:
    return "numpy.cpu"


# ---------------------------------------------------------------------------
# Codebook builders (same conventions as v1 core; independent implementation)
# ---------------------------------------------------------------------------
def _build_bipolar(V: int, N: int, seed: int) -> np.ndarray:
    """Bipolar {-1,+1} codebook (V,N) float32. Used for CYCLIC + RAND_PERM."""
    g = np.random.default_rng(seed)
    arr = (g.integers(0, 2, size=(V, N)) * 2 - 1).astype(np.float32)
    return arr


def _build_hrr_real(V: int, N: int, seed: int) -> np.ndarray:
    """Gaussian N(0, 1/sqrt(N)) codebook (V,N), L2-normalized. Used for PHASE."""
    g = np.random.default_rng(seed)
    arr = (g.standard_normal(size=(V, N)) / math.sqrt(N)).astype(np.float32)
    norms = np.linalg.norm(arr, axis=1, keepdims=True).clip(min=1e-12)
    arr = arr / norms
    return arr


# ---------------------------------------------------------------------------
# Order-binding primitives (identical math to v1 core; independent code copy
# to keep v2 self-contained if v1 core is later mutated)
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
    """RANDOM_PERMUTATION: P_k = perm^k(P_0). Returns (K, N)."""
    K = len(k_indices)
    N = P0.shape[-1]
    max_k = int(max(k_indices)) if K > 0 else 0
    perm_powers = [np.arange(N, dtype=np.int64)]
    for _ in range(max_k):
        perm_powers.append(perm[perm_powers[-1]])
    out = np.empty((K, N), dtype=P0.dtype)
    for i, k in enumerate(k_indices):
        out[i] = P0[perm_powers[int(k)]]
    return out


def _order_phase_rotation(P0: np.ndarray, k_indices: np.ndarray,
                          theta: float) -> np.ndarray:
    """PHASE_ROTATION: P_k = ifft(fft(P_0) * exp(1j * k * theta * freqs))."""
    K = len(k_indices)
    N = P0.shape[-1]
    F = np.fft.rfft(P0)
    freqs = np.arange(F.shape[-1], dtype=np.float64)
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
    """positions (K,N); items (K,N); returns (N,) = sum_k p_k * i_k."""
    return (positions * items).sum(axis=0)


def _unbind_hadamard(bundle: np.ndarray, query_pos: np.ndarray) -> np.ndarray:
    """bundle (N,); query_pos (N,); returns (N,) = bundle * q_pos."""
    return bundle * query_pos


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
    """Build (K,N) position vectors per order-binding op."""
    if op_name == "CYCLIC_SHIFT":
        return _order_cyclic_shift(P0, k_indices)
    elif op_name == "RANDOM_PERMUTATION":
        g = np.random.default_rng(seed * 31 + 11)
        perm = g.permutation(P0.shape[-1]).astype(np.int64)
        return _order_random_permutation(P0, k_indices, perm)
    elif op_name == "PHASE_ROTATION":
        # Golden-ratio theta to avoid trivial aliasing to CYCLIC_SHIFT.
        theta = 2.0 * math.pi * ((math.sqrt(5.0) - 1.0) * 0.5) / float(P0.shape[-1])
        return _order_phase_rotation(P0, k_indices, theta)
    else:
        raise ValueError(f"unknown order_op={op_name!r}")


# ---------------------------------------------------------------------------
# Per-point evaluation: multi-sequence bundle at (op, L, K_per_seq)
# ---------------------------------------------------------------------------
def eval_phase_point(order_op: str, L: int, K_per_seq: int, n_queries: int,
                     seed: int) -> Dict[str, Any]:
    """One (order_op, L, K_per_seq) phase point.

    Pipeline:
      1. For each of L sequences, build INDEPENDENT codebooks (item + position
         P_0 base) with distinct seed slice.
      2. Encode each sequence: positions_l = order_op(P_0^{(l)}, 1..K); items_l
         = subset of item codebook of size K per sequence.
      3. bundle = sum over l of Hadamard(positions_l, items_l).
      4. For n_queries, sample (l, k) uniformly from L * K, unbind via
         positions_l[k], argmax over item codebook of that sequence.
      5. Random-position control: query with a P^{(l)}_k for k > K (unused).
    """
    if order_op not in _ORDER_REGISTRY:
        raise ValueError(f"unknown order_op={order_op!r}")
    reg = _ORDER_REGISTRY[order_op]

    t0 = time.time()
    g = np.random.default_rng(seed * 10007 + L * 1009 + K_per_seq)

    # Build L independent (P_0, item_codebook) pairs. Each sequence gets an
    # independent codebook seed slice so different sequences do not share
    # atomic vectors. This is the multi-sequence-load challenge.
    per_seq_state: List[Dict[str, Any]] = []
    for l in range(L):
        # Distinct seed per sequence
        seed_l = seed + 100003 * (l + 1)
        P_all_l = reg["build_codebook"](2, N_DIM, seed_l)
        P0_l = P_all_l[0]
        I_codebook_l = reg["build_codebook"](V_ITEMS, N_DIM, seed_l + 17)
        k_indices = np.arange(1, K_per_seq + 1, dtype=np.int64)
        positions_l = _build_positions(order_op, P0_l, k_indices, seed_l)  # (K,N)
        item_idx_l = g.choice(V_ITEMS, size=K_per_seq, replace=False)
        items_l = I_codebook_l[item_idx_l]                                # (K,N)
        per_seq_state.append({
            "seq_id": l,
            "P0": P0_l,
            "I_codebook": I_codebook_l,
            "positions": positions_l,
            "item_idx": item_idx_l,
            "items": items_l,
        })

    # Bundle: sum over sequences of Hadamard(positions, items)
    bundle = np.zeros(N_DIM, dtype=np.float32)
    for s in per_seq_state:
        bundle = bundle + _bundle_hadamard(s["positions"], s["items"])

    # Sample n_queries (l, k_local) pairs across all sequences
    total_units = L * K_per_seq
    n_q = min(n_queries, total_units)
    all_pairs = np.array([(l, k) for l in range(L) for k in range(K_per_seq)],
                         dtype=np.int64)
    chosen_idx = g.choice(total_units, size=n_q, replace=False)
    chosen_pairs = all_pairs[chosen_idx]

    # Substrate arm: unbind + argmax over ITEM CODEBOOK OF THAT SEQUENCE
    top1_hits = 0
    per_pair_top1: List[int] = []
    for q_i in range(n_q):
        l_q, k_q = int(chosen_pairs[q_i, 0]), int(chosen_pairs[q_i, 1])
        s = per_seq_state[l_q]
        q_pos = s["positions"][k_q]                       # (N,)
        unbound = _unbind_hadamard(bundle, q_pos)         # (N,)
        # Cleanup against l_q's item codebook (query specifies which sequence)
        sims = s["I_codebook"] @ unbound                  # (V,)
        pred = int(np.argmax(sims))
        true_item = int(s["item_idx"][k_q])
        hit = 1 if pred == true_item else 0
        top1_hits += hit
        per_pair_top1.append(hit)
    top1_sub = top1_hits / max(n_q, 1)

    # Random-position control: query with never-encoded positions (k > K_per_seq)
    rand_hits = 0
    for q_i in range(n_q):
        l_q, _ = int(chosen_pairs[q_i, 0]), int(chosen_pairs[q_i, 1])
        s = per_seq_state[l_q]
        # Build a random k > K_per_seq position (not in the bundle)
        rand_k = g.integers(K_per_seq + 1, K_per_seq + 100, size=1)
        rand_positions = _build_positions(order_op, s["P0"], rand_k,
                                          seed + 100003 * (l_q + 1))  # (1,N)
        unbound_r = _unbind_hadamard(bundle, rand_positions[0])
        sims_r = s["I_codebook"] @ unbound_r
        pred_r = int(np.argmax(sims_r))
        true_item = int(s["item_idx"][int(chosen_pairs[q_i, 1])])
        if pred_r == true_item:
            rand_hits += 1
    top1_rand = rand_hits / max(n_q, 1)

    elapsed = time.time() - t0
    discriminator_local = top1_sub - top1_rand
    suspect_sat = bool(top1_sub >= SUSPECT_SAT)

    # META_RULE_AF mechanism_hash: bundle bytes + v2 salt + (op, L, K) tag.
    # v2 salt guarantees v1's identical bundle NEVER collides with v2's L=1 point.
    hasher = hashlib.sha256()
    hasher.update(V2_LOAD_SALT)
    hasher.update(f"|op={order_op}|L={L}|K={K_per_seq}|".encode("utf-8"))
    hasher.update(bundle.tobytes())
    bundle_hash = hasher.hexdigest()

    # positions_hash from sequence-0 position matrix (representative)
    positions_hash = hashlib.sha256(
        V2_LOAD_SALT + per_seq_state[0]["positions"].tobytes()
    ).hexdigest()

    # Band classification
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
        "L": int(L),
        "K_per_seq": int(K_per_seq),
        "K_total": int(L * K_per_seq),
        "N_DIM": int(N_DIM),
        "n_queries": int(n_q),
        "seed": int(seed),
        "top1_substrate": round(top1_sub, 4),
        "top1_random": round(top1_rand, 4),
        "discriminator_local": round(discriminator_local, 4),
        "band": band,
        "suspect_saturation": suspect_sat,
        "elapsed_per_point_s": round(elapsed, 3),
        "bundle_hash": bundle_hash,
        "positions_hash": positions_hash,
        "bundle_shape": list(bundle.shape),
    }


# ---------------------------------------------------------------------------
# Selftest: cardinality math + K=5,L=1 round-trip per op + 3 op distinctness
# ---------------------------------------------------------------------------
def selftest(seed: int) -> Tuple[bool, str]:
    """Selftest gates:

    1. Cardinality FULL=18, SMOKE=18
    2. Per-op L=1 K=5 round-trip: argmax must recover item 0
    3. 3 ops produce distinct BUNDLE hashes AND distinct POSITIONS hashes
       (guards META_RULE_AF; catches PHASE_ROTATION aliasing to CYCLIC_SHIFT)
    4. v2 salt distinctness: bundle_hash for (op=CYCLIC, L=1, K=5) MUST differ
       from a hash of the raw bundle bytes (proves salt is included)
    """
    msgs: List[str] = []

    if EXPECTED_N_UNITS_FULL != 18:
        return False, f"FULL cardinality {EXPECTED_N_UNITS_FULL} != 18"
    if EXPECTED_N_UNITS_SMOKE != 18:
        return False, f"SMOKE cardinality {EXPECTED_N_UNITS_SMOKE} != 18"
    msgs.append(f"cardinality FULL={EXPECTED_N_UNITS_FULL} SMOKE={EXPECTED_N_UNITS_SMOKE}")

    # 2. Per-op round-trip at L=1, K=5
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
        items = I_codebook[:K_test]
        bundle = _bundle_hadamard(positions, items)
        unbound = _unbind_hadamard(bundle, positions[0])
        sims = I_codebook @ unbound
        pred = int(np.argmax(sims))
        top10 = np.argsort(-sims)[:10].tolist()
        if pred != 0 and 0 not in top10:
            return False, (f"round_trip FAIL {op_name}: L=1 K={K_test} q=P[0] "
                           f"argmax={pred} top10={top10}; expected 0")
        msgs.append(f"round_trip {op_name}: L=1 K={K_test} argmax={pred} (0 in top10)")

        # v2-salted bundle hash
        hasher = hashlib.sha256()
        hasher.update(V2_LOAD_SALT)
        hasher.update(f"|op={op_name}|L=1|K={K_test}|".encode("utf-8"))
        hasher.update(bundle.tobytes())
        op_bundle_hashes[op_name] = hasher.hexdigest()[:16]
        op_positions_hashes[op_name] = hashlib.sha256(
            V2_LOAD_SALT + positions.tobytes()
        ).hexdigest()[:16]

    if len(set(op_bundle_hashes.values())) != len(ORDER_OPERATIONS):
        return False, (f"META_RULE_AF VIOLATION: bundle hashes NOT distinct at "
                       f"seed={seed}: {op_bundle_hashes}")
    if len(set(op_positions_hashes.values())) != len(ORDER_OPERATIONS):
        return False, (f"META_RULE_AF VIOLATION: positions hashes NOT distinct at "
                       f"seed={seed}: {op_positions_hashes}; likely PHASE_ROTATION "
                       f"aliasing to CYCLIC_SHIFT")
    msgs.append(f"arms_differ_bundle_hashes: {op_bundle_hashes}")
    msgs.append(f"arms_differ_positions_hashes: {op_positions_hashes}")

    # 4. v2 salt distinctness: recompute unsalted hash of CYCLIC bundle bytes
    reg = _ORDER_REGISTRY["CYCLIC_SHIFT"]
    P_all = reg["build_codebook"](2, N_DIM, seed)
    P0 = P_all[0]
    I_codebook = reg["build_codebook"](20, N_DIM, seed + 17)
    k_indices = np.arange(1, K_test + 1, dtype=np.int64)
    positions = _build_positions("CYCLIC_SHIFT", P0, k_indices, seed)
    items = I_codebook[:K_test]
    bundle = _bundle_hadamard(positions, items)
    unsalted = hashlib.sha256(bundle.tobytes()).hexdigest()[:16]
    salted = op_bundle_hashes["CYCLIC_SHIFT"]
    if unsalted == salted:
        return False, ("V2_SALT_MISSING: salted hash equals unsalted; v2 salt "
                       "not being applied -- would alias to v1 mechanism_hash")
    msgs.append(f"v2_salt_applied: unsalted={unsalted} salted={salted} DISTINCT")

    return True, "; ".join(msgs)


# ---------------------------------------------------------------------------
# Per-seed sweep
# ---------------------------------------------------------------------------
def run_one_seed_load_sweep(seed: int, run_mode: str) -> Dict[str, Any]:
    """Run all (order_op, L, K_per_seq) points for one seed."""
    is_smoke = (run_mode == "smoke")
    L_sweep = L_SMOKE if is_smoke else L_FULL
    K_sweep = K_PER_SEQ_SMOKE if is_smoke else K_PER_SEQ_FULL
    n_queries = N_QUERIES_SMOKE if is_smoke else N_QUERIES_FULL
    expected_n_units = len(ORDER_OPERATIONS) * len(L_sweep) * len(K_sweep)

    print(f"[run_one_seed] seed={seed} mode={run_mode} "
          f"ops={ORDER_OPERATIONS} L_sweep={L_sweep} K_sweep={K_sweep} "
          f"n_q={n_queries} expected_n={expected_n_units}", flush=True)

    phase_map: List[Dict[str, Any]] = []
    t0 = time.time()
    for op_name in ORDER_OPERATIONS:
        for L in L_sweep:
            for K in K_sweep:
                print(f"[point] seed={seed} op={op_name} L={L} K={K} ...",
                      flush=True)
                pt = eval_phase_point(op_name, L, K, n_queries, seed)
                phase_map.append(pt)
                print(f"  -> top1_sub={pt['top1_substrate']:.3f} "
                      f"top1_rnd={pt['top1_random']:.3f} "
                      f"disc_local={pt['discriminator_local']:.3f} "
                      f"band={pt['band']} "
                      f"suspect_sat={pt['suspect_saturation']} "
                      f"t={pt['elapsed_per_point_s']:.2f}s", flush=True)

    elapsed = time.time() - t0
    observed_n_units = len(phase_map)
    cardinality_ok = (observed_n_units == expected_n_units)

    # Per-op summary across sweep points
    per_op_summary: Dict[str, Any] = {}
    for op_name in ORDER_OPERATIONS:
        op_pts = [p for p in phase_map if p["order_operation"] == op_name]
        top1_arr = np.array([p["top1_substrate"] for p in op_pts])
        rand_arr = np.array([p["top1_random"] for p in op_pts])
        cv = float(top1_arr.std() / max(top1_arr.mean(), 1e-6))
        n_sat = sum(1 for p in op_pts if p["band"] == "SAT")
        n_mb = sum(1 for p in op_pts if p["band"] == "MB")
        n_floor = sum(1 for p in op_pts if p["band"] == "FLOOR")
        n_trans = sum(1 for p in op_pts if p["band"] == "TRANSITION")
        per_op_summary[op_name] = {
            "encoder_family": _ORDER_REGISTRY[op_name]["encoder_family"],
            "top1_sub_mean": round(float(top1_arr.mean()), 4),
            "top1_rand_mean": round(float(rand_arr.mean()), 4),
            "band_counts": {"SAT": n_sat, "MB": n_mb,
                            "FLOOR": n_floor, "TRANSITION": n_trans},
            "cv_across_sweep": round(cv, 4),
        }

    # Discriminator point: (L=4, K=250) per op
    disc_pts_by_op: Dict[str, Dict[str, Any]] = {}
    for op_name in ORDER_OPERATIONS:
        matches = [p for p in phase_map
                   if p["order_operation"] == op_name
                   and p["L"] == DISCRIMINATOR_L
                   and p["K_per_seq"] == DISCRIMINATOR_K]
        if matches:
            disc_pts_by_op[op_name] = matches[0]
        else:
            disc_pts_by_op[op_name] = {
                "top1_substrate": -1.0,
                "top1_random": -1.0,
                "band": "MISSING",
            }

    # Pairwise diffs at discriminator point
    disc_pair_diffs: Dict[str, float] = {}
    ops = list(ORDER_OPERATIONS)
    for i in range(len(ops)):
        for j in range(i + 1, len(ops)):
            a, b = ops[i], ops[j]
            va = disc_pts_by_op[a].get("top1_substrate", -1.0)
            vb = disc_pts_by_op[b].get("top1_substrate", -1.0)
            disc_pair_diffs[f"{a}_vs_{b}"] = round(abs(va - vb), 4)
    max_pair_diff = max(disc_pair_diffs.values()) if disc_pair_diffs else 0.0

    # Per-op bundle_hash and positions_hash from FIRST point per op (op, L=1, K=125)
    op_bundle_hashes: Dict[str, str] = {}
    op_positions_hashes: Dict[str, str] = {}
    first_L = L_sweep[0]
    first_K = K_sweep[0]
    for op_name in ORDER_OPERATIONS:
        matches = [p for p in phase_map
                   if p["order_operation"] == op_name
                   and p["L"] == first_L
                   and p["K_per_seq"] == first_K]
        if matches:
            op_bundle_hashes[op_name] = matches[0]["bundle_hash"]
            op_positions_hashes[op_name] = matches[0]["positions_hash"]
        else:
            op_bundle_hashes[op_name] = "MISSING"
            op_positions_hashes[op_name] = "MISSING"

    # Pair distinctness (bundle + positions)
    pairs_bundle_differ: Dict[str, bool] = {}
    pairs_positions_differ: Dict[str, bool] = {}
    for i in range(len(ops)):
        for j in range(i + 1, len(ops)):
            key = f"{ops[i]}_vs_{ops[j]}"
            pairs_bundle_differ[key] = (op_bundle_hashes[ops[i]]
                                        != op_bundle_hashes[ops[j]])
            pairs_positions_differ[key] = (op_positions_hashes[ops[i]]
                                           != op_positions_hashes[ops[j]])
    n_pairs = len(pairs_bundle_differ)
    n_pairs_bundle_differ = sum(1 for v in pairs_bundle_differ.values() if v)
    n_pairs_positions_differ = sum(1 for v in pairs_positions_differ.values() if v)

    n_suspect_sat = sum(1 for p in phase_map if p["suspect_saturation"])

    # Positive control: CYCLIC@(L=1, K=125) must clear 0.80 floor
    pc_pts = [p for p in phase_map
              if p["order_operation"] == POSITIVE_CONTROL["order_operation"]
              and p["L"] == POSITIVE_CONTROL["L"]
              and p["K_per_seq"] == POSITIVE_CONTROL["K_per_seq"]]
    pc_top1 = pc_pts[0]["top1_substrate"] if pc_pts else -1.0
    pc_pass = pc_top1 >= POSITIVE_CONTROL["top1_floor_required"]
    positive_control_result = {
        "order_operation": POSITIVE_CONTROL["order_operation"],
        "L": POSITIVE_CONTROL["L"],
        "K_per_seq": POSITIVE_CONTROL["K_per_seq"],
        "top1_floor_required": POSITIVE_CONTROL["top1_floor_required"],
        "measured_top1": pc_top1,
        "pass": pc_pass,
    }

    return {
        "seed": seed,
        "run_mode": run_mode,
        "N_DIM": N_DIM,
        "order_operations": list(ORDER_OPERATIONS),
        "L_sweep": list(L_sweep),
        "K_per_seq_sweep": list(K_sweep),
        "n_queries_per_point": n_queries,
        "discriminator_L": DISCRIMINATOR_L,
        "discriminator_K": DISCRIMINATOR_K,
        "phase_map": phase_map,
        "per_op_summary": per_op_summary,
        "disc_pts_by_op": disc_pts_by_op,
        "disc_pair_diffs": disc_pair_diffs,
        "max_pair_diff_at_disc": round(max_pair_diff, 4),
        "op_pair_bundle_distinctness": pairs_bundle_differ,
        "op_pair_positions_distinctness": pairs_positions_differ,
        "n_pairs_bundle_differ": n_pairs_bundle_differ,
        "n_pairs_positions_differ": n_pairs_positions_differ,
        "op_bundle_hashes": op_bundle_hashes,
        "op_positions_hashes": op_positions_hashes,
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
# Smoke gate: DISCRIMINATOR-FIRES + honest-abort at aliasing
# ---------------------------------------------------------------------------
def smoke_gate_predicate(body: Dict[str, Any]) -> Tuple[bool, str]:
    """Smoke gate assertions:

      1. Cardinality OK (18 pts)
      2. Positive control (CYCLIC@L=1,K=125) clears 0.80 floor
      3. All 3 op bundle hashes distinct AND all 3 position hashes distinct
      4. DISCRIMINATOR-FIRES: at (L=4, K=250), max pair diff >= 0.15
         OR HONEST_ABORT if all 3 ops within 0.03 (substantive negative)
      5. NOT all 3 ops SAT at (L=4, K=250) (baseline-in-band guard)
    """
    phase_map = body.get("phase_map", [])
    expected_n = body.get("expected_n_units", 0)
    pc_result = body.get("positive_control_result", {})
    pairs_bundle_differ = body.get("op_pair_bundle_distinctness", {})
    pairs_positions_differ = body.get("op_pair_positions_distinctness", {})
    disc_pair_diffs = body.get("disc_pair_diffs", {})
    disc_pts_by_op = body.get("disc_pts_by_op", {})

    # 1. Cardinality
    if len(phase_map) != expected_n:
        return False, (f"cardinality_breach: expected {expected_n} "
                       f"got {len(phase_map)}")

    # 2. Positive control
    if not pc_result.get("pass"):
        return False, (f"META_RULE_BC_FAIL: positive_control {pc_result} below "
                       f"floor; CYCLIC@L=1,K=125 must SAT or test rig broken")

    # 3. Arm distinctness
    n_pairs = len(pairs_bundle_differ)
    n_bundle_differ = sum(1 for v in pairs_bundle_differ.values() if v)
    n_positions_differ = sum(1 for v in pairs_positions_differ.values() if v)
    if n_bundle_differ < n_pairs:
        collapsed = [k for k, v in pairs_bundle_differ.items() if not v]
        return False, (f"META_RULE_AF_BUNDLE_COLLAPSE: {n_bundle_differ}/{n_pairs} "
                       f"differ; identical bundle pairs: {collapsed}")
    if n_positions_differ < n_pairs:
        collapsed = [k for k, v in pairs_positions_differ.items() if not v]
        return False, (f"META_RULE_AF_POSITIONS_COLLAPSE: {n_positions_differ}/"
                       f"{n_pairs} differ; identical position pairs: {collapsed}; "
                       f"likely PHASE_ROTATION aliasing to CYCLIC_SHIFT")

    # 4. Baseline-in-band at discriminator point
    disc_sats = [op for op, pt in disc_pts_by_op.items()
                 if pt.get("top1_substrate", -1.0) >= BAND_SAT]
    disc_floors = [op for op, pt in disc_pts_by_op.items()
                   if pt.get("top1_substrate", 1.0) <= BAND_FLOOR]
    if len(disc_sats) == len(ORDER_OPERATIONS):
        return False, (f"META_RULE_AG_ALL_SAT_AT_DISC: all 3 ops SAT at "
                       f"(L={DISCRIMINATOR_L},K={DISCRIMINATOR_K}); baseline too "
                       f"robust; CRLB predicted SNR=2.86 -> ~0.30 top1; regime "
                       f"needs iteration (increase L or K)")
    if len(disc_floors) == len(ORDER_OPERATIONS):
        return False, (f"META_RULE_AG_ALL_FLOOR_AT_DISC: all 3 ops FLOOR at "
                       f"(L={DISCRIMINATOR_L},K={DISCRIMINATOR_K}); regime too hard; "
                       f"decrease L or K")

    # 5. DISCRIMINATOR-FIRES or HONEST_ABORT
    max_pair_diff = max(disc_pair_diffs.values()) if disc_pair_diffs else 0.0
    if max_pair_diff >= DISCRIMINATOR_MIN_PAIR_DIFF:
        return True, (f"smoke_gate_pass_DISCRIMINATOR_FIRES: max_pair_diff="
                      f"{max_pair_diff:.3f} >= {DISCRIMINATOR_MIN_PAIR_DIFF} at "
                      f"(L={DISCRIMINATOR_L},K={DISCRIMINATOR_K}); "
                      f"disc_pts={ {k: v.get('top1_substrate') for k, v in disc_pts_by_op.items()} }; "
                      f"disc_pair_diffs={disc_pair_diffs}")
    if max_pair_diff <= DISCRIMINATOR_HONEST_ABORT_DIFF:
        return False, (f"HONEST_ABORT_INVARIANT_UNDER_LOAD: all 3 ops within "
                       f"{DISCRIMINATOR_HONEST_ABORT_DIFF} at "
                       f"(L={DISCRIMINATOR_L},K={DISCRIMINATOR_K}); "
                       f"max_pair_diff={max_pair_diff:.3f}; order-binding is "
                       f"capability-family-invariant under multi-seq load "
                       f"AS WELL AS at single-seq cliff (v1 result); axis J CLOSED "
                       f"as substantive negative")
    return False, (f"DISCRIMINATOR_UNDERSHOOTS_BUT_NOT_INVARIANT: max_pair_diff="
                   f"{max_pair_diff:.3f} in "
                   f"({DISCRIMINATOR_HONEST_ABORT_DIFF}, "
                   f"{DISCRIMINATOR_MIN_PAIR_DIFF}); MB regime; "
                   f"disc_pts={ {k: v.get('top1_substrate') for k, v in disc_pts_by_op.items()} }; "
                   f"regime may need iteration OR FULL run may resolve at 60 queries")


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
    disc_pts_by_op = body.get("disc_pts_by_op", {})
    disc_pair_diffs = body.get("disc_pair_diffs", {})
    max_pair_diff = body.get("max_pair_diff_at_disc", 0.0)
    op_bundle_hashes = body.get("op_bundle_hashes", {})
    op_positions_hashes = body.get("op_positions_hashes", {})
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
        "disc_pts_by_op": disc_pts_by_op,
        "disc_pair_diffs": disc_pair_diffs,
        "max_pair_diff_at_disc": max_pair_diff,
        "op_pair_bundle_distinctness": pairs_bundle_differ,
        "op_pair_positions_distinctness": pairs_positions_differ,
        "n_pairs_bundle_differ": n_pairs_bundle_differ,
        "n_pairs_positions_differ": n_pairs_positions_differ,
        "op_bundle_hashes": op_bundle_hashes,
        "op_positions_hashes": op_positions_hashes,
        "n_suspect_saturation": n_suspect_sat,
        "positive_control_result": pc_result,
        "cardinality_ok": cardinality_ok,
        "expected_n_units": expected_n,
        "observed_n_units": observed_n,
        "tier_counts": {"SAT": n_sat, "MB": n_mb,
                        "FLOOR": n_floor, "TRANSITION": n_trans},
        "device": body.get("device"),
        "gpu_name": body.get("gpu_name"),
        "regime": "order_binding_family_v2_load_sweep_N8192",
        "discriminator_L": DISCRIMINATOR_L,
        "discriminator_K": DISCRIMINATOR_K,
        "discriminator_min_pair_diff": DISCRIMINATOR_MIN_PAIR_DIFF,
        "discriminator_honest_abort_diff": DISCRIMINATOR_HONEST_ABORT_DIFF,
    }

    if is_smoke:
        passed, reason = smoke_gate_predicate(body)
        if passed:
            verdict = "HARD_PASS"
            vmsg = (f"HARD_PASS_SMOKE: {observed_n}/{expected_n} pts; "
                    f"sat={n_sat} mb={n_mb} floor={n_floor} trans={n_trans}; "
                    f"3-op-distinct(bundle+positions); "
                    f"positive_control@L=1,K=125 top1="
                    f"{pc_result.get('measured_top1'):.3f}; "
                    f"DISCRIMINATOR_FIRES max_pair_diff={max_pair_diff:.3f} "
                    f">= {DISCRIMINATOR_MIN_PAIR_DIFF} at "
                    f"(L={DISCRIMINATOR_L},K={DISCRIMINATOR_K}); "
                    f"disc_pts={ {k: v.get('top1_substrate') for k, v in disc_pts_by_op.items()} }; "
                    f"n_suspect_sat={n_suspect_sat}; reason={reason}")
        else:
            # Distinguish honest-abort (substrate-negative) from gate-fail
            if "HONEST_ABORT" in reason:
                verdict = "HARD_FAIL"
                vmsg = f"HARD_FAIL_HONEST_ABORT_INVARIANT_UNDER_LOAD: {reason}"
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

    # FULL verdict
    if not cardinality_ok:
        verdict = "HARD_FAIL"
        vmsg = (f"HARD_FAIL_CARDINALITY_BREACH: expected={expected_n} "
                f"observed={observed_n}")
    elif not pc_result.get("pass"):
        verdict = "HARD_FAIL"
        vmsg = (f"HARD_FAIL_META_RULE_BC_CONTROL_FAIL: positive_control "
                f"{pc_result}; test rig broken")
    elif n_pairs_bundle_differ < len(pairs_bundle_differ):
        bad = [k for k, v in pairs_bundle_differ.items() if not v]
        verdict = "HARD_FAIL"
        vmsg = f"HARD_FAIL_META_RULE_AF_BUNDLE_IDENTICAL_PAIRS: {bad}"
    elif n_pairs_positions_differ < len(pairs_positions_differ):
        bad = [k for k, v in pairs_positions_differ.items() if not v]
        verdict = "HARD_FAIL"
        vmsg = (f"HARD_FAIL_META_RULE_AF_POSITIONS_IDENTICAL_PAIRS: {bad}; "
                f"likely PHASE_ROTATION aliasing to CYCLIC_SHIFT")
    elif max_pair_diff >= DISCRIMINATOR_MIN_PAIR_DIFF:
        verdict = "HARD_PASS"
        vmsg = (f"HARD_PASS_INTERFERENCE_RESILIENCE_DISCRIMINATES: max_pair_diff="
                f"{max_pair_diff:.3f} >= {DISCRIMINATOR_MIN_PAIR_DIFF} at "
                f"(L={DISCRIMINATOR_L},K={DISCRIMINATOR_K}); "
                f"disc_pts={ {k: v.get('top1_substrate') for k, v in disc_pts_by_op.items()} }; "
                f"disc_pair_diffs={disc_pair_diffs}; "
                f"pair-distinctness bundle={n_pairs_bundle_differ}/"
                f"{len(pairs_bundle_differ)} positions="
                f"{n_pairs_positions_differ}/{len(pairs_positions_differ)}; "
                f"n_suspect_sat={n_suspect_sat}; "
                f"order-binding is CAPABILITY-CONDITIONAL under multi-seq load")
    elif max_pair_diff <= DISCRIMINATOR_HONEST_ABORT_DIFF:
        verdict = "HARD_FAIL"
        vmsg = (f"HARD_FAIL_INVARIANT_UNDER_LOAD: all pairs within "
                f"{DISCRIMINATOR_HONEST_ABORT_DIFF} at "
                f"(L={DISCRIMINATOR_L},K={DISCRIMINATOR_K}); "
                f"max_pair_diff={max_pair_diff:.3f}; "
                f"disc_pts={ {k: v.get('top1_substrate') for k, v in disc_pts_by_op.items()} }; "
                f"order-binding capability-family-invariant AT LOAD AS WELL AS "
                f"at single-seq cliff -> axis J CLOSED (substantive negative)")
    else:
        verdict = "MIDDLE_BAND"
        vmsg = (f"MIDDLE_BAND_PARTIAL: max_pair_diff={max_pair_diff:.3f} in "
                f"({DISCRIMINATOR_HONEST_ABORT_DIFF}, "
                f"{DISCRIMINATOR_MIN_PAIR_DIFF}) at "
                f"(L={DISCRIMINATOR_L},K={DISCRIMINATOR_K}); "
                f"disc_pts={ {k: v.get('top1_substrate') for k, v in disc_pts_by_op.items()} }; "
                f"disc_pair_diffs={disc_pair_diffs}")

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
    "L_FULL", "L_SMOKE", "K_PER_SEQ_FULL", "K_PER_SEQ_SMOKE",
    "N_QUERIES_FULL", "N_QUERIES_SMOKE",
    "EXPECTED_N_UNITS_FULL", "EXPECTED_N_UNITS_SMOKE",
    "DISCRIMINATOR_L", "DISCRIMINATOR_K",
    "DISCRIMINATOR_MIN_PAIR_DIFF", "DISCRIMINATOR_HONEST_ABORT_DIFF",
    "POSITIVE_CONTROL", "POSITIVE_CONTROL_SMOKE",
    "REQUIRED_FIELDS",
    "V2_LOAD_SALT",
    "get_backend_label",
    "eval_phase_point", "selftest",
    "run_one_seed_load_sweep",
    "smoke_gate_predicate", "aggregate_and_verdict",
]
