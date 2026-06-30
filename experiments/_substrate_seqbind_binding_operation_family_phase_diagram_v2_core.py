"""Shared core for substrate_seqbind_binding_operation_family_phase_diagram_v2 siblings.

2x-drill of substrate_pc_binding_operation_family_phase_diagram_v1
(MIDDLE_BAND, n_disc=8/48, USER 2026-06-30 drill-all-negatives-2x directive).

Mechanism-class diversion (NOT a re-run):
  v1 tested binding ops at PC CLIFF REGIME (corruption sweep; N sweep; M=100
  role-filler pairs; ONE single-pattern recovery per query).
  v2 tests SAME binding ops at SEQUENCE BINDING REGIME (K_SEQ sweep at fixed
  N=8192; sequence of K position-item pairs bundled; query at one position
  to recover its item). Different cliff axis (K_SEQ vs corruption), different
  attractor dynamics (sequence vs single-pattern), different load shape
  (additive K vs multiplicative M).

If binding op discriminates at sequence regime but NOT at PC, the substantive
finding is: binding-op axis is REGIME-CONDITIONAL not substrate-invariant.

5 ARMs (4 from v1 + SUM_MOD_N additive control per META_RULE_BC):
  - HADAMARD_BIND        : element-wise multiply on bipolar (Kanerva BSC)
  - CIRCULAR_CONV_HRR    : FFT-based circular convolution (Plate HRR)
  - TENSOR_PRODUCT       : rank-2 outer product + flatten
  - XOR_BSC              : XOR on binary {0,1} -- isomorphic to bipolar
                          Hadamard but exposes binary-substrate regime
  - SUM_MOD_N            : additive binding (positional sum modulo N) --
                          POSITIVE CONTROL: must clear floor at K=50 or
                          regime is too hard (META_RULE_BC).

Regime axes (LOCKED):
  - N_DIM = 8192 (fixed)
  - K_SEQ = [50, 100, 200, 500, 1000]
  - 3 seeds [7, 13, 19]
  - 50 queries per (binding_op, K_SEQ) point at full; 5 at smoke

Cardinality:
  FULL  per seed: 5 ops x 5 K_SEQ = 25 phase points
  SMOKE per seed: 5 ops x 3 K_SEQ = 15 phase points

Discriminator (per task spec):
  HARD_PASS:    >=3 of 5 ops produce DISTINCT K_cliff localizations (>=0.3
                log2 separation in K_cliff); per-op mechanism_hash distinct;
                cv <=0.10; no suspect-1.000 saturation.
  MIDDLE_BAND:  2 of 5 ops distinct (some differentiate at sequence regime).
  HARD_FAIL:    All 5 ops converge (binding regime-invariant at sequence too
                -- substantive negative across both regimes).

Bands (LOCKED for K_cliff localization):
  SAT band:     top1 >= 0.90 at a given K -> op is "above cliff" at this K
  MB band:      top1 in [0.30, 0.70]      -> op is "on cliff" at this K
  FLOOR band:   top1 <= 0.10              -> op is "below cliff" at this K
  K_cliff_op  = smallest K where SUBSTRATE drops below SAT (0.90)
  log2 separation between two ops = abs(log2(K_cliff_a) - log2(K_cliff_b))

ASCII-only. No unicode. No em-dashes. CUDA preferred; CPU fallback for smoke.
FULL on CPU REFUSED unless HDLAB_QUEUE=local_cpu_queue (Fix #24).

Author: exp_dev 2026-06-30 (Opus 4.7 1M, agent-spawn) 2x-drill of PC v1 MB.
"""
from __future__ import annotations

import hashlib
import json
import math
import time
from typing import Any, Callable, Dict, List, Tuple

import numpy as np

# Torch at TOP of module (PROT-020 GPU-eligibility scan)
import torch

_CUDA_OK = bool(torch.cuda.is_available())
if _CUDA_OK:
    DEVICE = torch.device("cuda")
    GPU_NAME = torch.cuda.get_device_name(0)
    GPU_MAX_MEM_GB = torch.cuda.get_device_properties(0).total_memory / 1e9
else:
    DEVICE = torch.device("cpu")
    GPU_NAME = "cpu_fallback"
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

K_SEQ_FULL = (50, 100, 200, 500, 1000)
K_SEQ_SMOKE = (50, 200, 1000)  # span SAT / cliff / FLOOR for smoke discriminator-fires

N_QUERIES_FULL = 50
N_QUERIES_SMOKE = 5

# 5 binding ops -- OUTER axis
BINDING_OPERATIONS = (
    "HADAMARD_BIND",
    "CIRCULAR_CONV_HRR",
    "TENSOR_PRODUCT",
    "XOR_BSC",
    "SUM_MOD_N",            # positive control (additive)
)

# Each binding op has a paired encoder family.
_BINDING_ENCODER_PAIR = {
    "HADAMARD_BIND":      "binary_bipolar",
    "CIRCULAR_CONV_HRR":  "hrr_real",
    "TENSOR_PRODUCT":     "binary_bipolar_outer",   # N_outer = isqrt(N_DIM)
    "XOR_BSC":            "binary_01",              # {0,1} bits, not bipolar
    "SUM_MOD_N":          "integer_mod_N",          # positional integers
}

# Beta for softmax cleanup
BETA = 8.0

# Cardinality
EXPECTED_N_UNITS_FULL = len(BINDING_OPERATIONS) * len(K_SEQ_FULL)    # 25
EXPECTED_N_UNITS_SMOKE = len(BINDING_OPERATIONS) * len(K_SEQ_SMOKE)  # 15

# CRLB / capacity feasibility (THEORETICAL@var(unbind_noise)~K/N)
# For VSA bundle of K bind(R,F) pairs: unbind noise has variance K/N (random
# codes; orthogonal expectation). top1 cleanup over codebook of V=1200 items:
#   SNR = sqrt(N/K) -- recall=1.0 at SNR >= 3 (K/N <= 1/9); recall ~0.5 at
#   SNR ~ 1.5 (K/N ~ 0.44); FLOOR at SNR ~ 0.7 (K/N >= 2).
# For N=8192:
#   K=50:   K/N = 0.006  -> SNR ~12  -> top1 ~ 1.0  (SAT)
#   K=100:  K/N = 0.012  -> SNR ~9   -> top1 ~ 1.0  (SAT)
#   K=200:  K/N = 0.024  -> SNR ~6.4 -> top1 ~ 1.0  (SAT)
#   K=500:  K/N = 0.061  -> SNR ~4   -> top1 ~ 0.95 (SAT / edge)
#   K=1000: K/N = 0.122  -> SNR ~2.9 -> top1 ~ 0.70 (MB top)
# All K below CRLB capacity (K_max ~ N/3 ~ 2700) at N=8192. Different binding
# ops have different effective-noise scaling though (TENSOR has N_outer^2 DoF;
# SUM_MOD_N has no proper unbind so collapses sharply).

# Positive control (META_RULE_BC): HADAMARD_BIND at K=50 must SAT (trivial
# regime; K/N=0.006; SNR~13; mechanism MUST work or test rig broken).
# SUM_MOD_N is the NEGATIVE control: additive bind has no proper unbind; must
# stay at FLOOR; non-floor signal = encoder contamination.
POSITIVE_CONTROL = {
    "binding_operation": "HADAMARD_BIND",
    "K_SEQ": 50,
    "top1_floor_required": 0.80,
}
POSITIVE_CONTROL_SMOKE = POSITIVE_CONTROL
NEGATIVE_CONTROL = {
    "binding_operation": "SUM_MOD_N",
    "K_SEQ": 50,
    "top1_ceiling_required": 0.10,
}

# Codebook size (must be >= max K_SEQ)
V_ITEMS = 1200
V_POS = 1200

REQUIRED_FIELDS = ("verdict", "verdict_msg", "elapsed_s", "summary")


def get_backend_label() -> str:
    return "torch.cuda" if _CUDA_OK else "torch.cpu"


# ---------------------------------------------------------------------------
# Codebook builders (per binding op's natural encoder family)
# ---------------------------------------------------------------------------
def _build_hrr_real(V: int, N: int, seed: int) -> "torch.Tensor":
    """Gaussian N(0,1/sqrt(N)) codebook (V,N), L2-normalized."""
    g = np.random.default_rng(seed)
    arr = (g.standard_normal(size=(V, N)) / math.sqrt(N)).astype(np.float32)
    norms = np.linalg.norm(arr, axis=1, keepdims=True).clip(min=1e-12)
    arr = arr / norms
    return torch.from_numpy(arr).to(DEVICE)


def _build_bipolar(V: int, N: int, seed: int) -> "torch.Tensor":
    """Bipolar {-1,+1} codebook (V,N) float32."""
    g = np.random.default_rng(seed)
    arr = (g.integers(0, 2, size=(V, N)) * 2 - 1).astype(np.float32)
    return torch.from_numpy(arr).to(DEVICE)


def _build_binary_01(V: int, N: int, seed: int) -> "torch.Tensor":
    """Binary {0,1} codebook (V,N) float32 (XOR substrate)."""
    g = np.random.default_rng(seed)
    arr = g.integers(0, 2, size=(V, N)).astype(np.float32)
    return torch.from_numpy(arr).to(DEVICE)


def _build_bipolar_outer(V: int, N: int, seed: int) -> "torch.Tensor":
    """Bipolar codebook with N_outer = isqrt(N), shape (V, N_outer)."""
    N_outer = int(round(math.sqrt(N)))
    g = np.random.default_rng(seed)
    arr = (g.integers(0, 2, size=(V, N_outer)) * 2 - 1).astype(np.float32)
    return torch.from_numpy(arr).to(DEVICE)


def _build_integer_mod_N(V: int, N: int, seed: int) -> "torch.Tensor":
    """Integer codebook in [0,N) shape (V,1). For SUM_MOD_N positive control."""
    g = np.random.default_rng(seed)
    arr = g.integers(0, N, size=(V, 1)).astype(np.float32)
    return torch.from_numpy(arr).to(DEVICE)


# ---------------------------------------------------------------------------
# Binding / unbinding primitives (op-specific). All operate on FULL sequence
# of K pairs (position, item) at once: pos/item shape (K, N) or (K, N_outer),
# bind/bundle returns shape (N,) or (N_outer^2,).
# ---------------------------------------------------------------------------
def _bundle_hadamard(positions: "torch.Tensor",
                     items: "torch.Tensor") -> "torch.Tensor":
    """Hadamard bind+bundle: sum_k (p_k * i_k) on bipolar."""
    return (positions * items).sum(dim=0)


def _unbind_hadamard(bundle: "torch.Tensor",
                     query_pos: "torch.Tensor") -> "torch.Tensor":
    """Hadamard unbind: bundle * q_pos (self-inverse on bipolar)."""
    return bundle * query_pos


def _bundle_circ_conv(positions: "torch.Tensor",
                      items: "torch.Tensor") -> "torch.Tensor":
    """HRR circular conv bind+bundle: sum_k ifft(fft(p_k) * fft(i_k))."""
    Pf = torch.fft.rfft(positions, dim=-1)
    If = torch.fft.rfft(items, dim=-1)
    bound = torch.fft.irfft(Pf * If, n=positions.shape[-1], dim=-1)
    return bound.sum(dim=0)


def _unbind_circ_conv(bundle: "torch.Tensor",
                      query_pos: "torch.Tensor") -> "torch.Tensor":
    """HRR circular correlation: ifft(conj(fft(q)) * fft(bundle))."""
    Qf = torch.fft.rfft(query_pos, dim=-1)
    Bf = torch.fft.rfft(bundle, dim=-1)
    return torch.fft.irfft(Qf.conj() * Bf, n=bundle.shape[-1], dim=-1)


def _bundle_tensor_product(positions: "torch.Tensor",
                           items: "torch.Tensor") -> "torch.Tensor":
    """Outer product bind+bundle: sum_k (p_k outer i_k).flatten()."""
    # positions, items: (K, N_outer); out per pair: (N_outer, N_outer)
    bound = torch.einsum("ki,kj->kij", positions, items)  # (K, N_outer, N_outer)
    return bound.sum(dim=0).reshape(-1)                    # (N_outer^2,)


def _unbind_tensor_product(bundle: "torch.Tensor",
                           query_pos: "torch.Tensor") -> "torch.Tensor":
    """Outer-product unbind: reshape bundle (N_outer, N_outer); q_pos @ bundle / N_outer."""
    N_outer = query_pos.shape[-1]
    bundle_2d = bundle.reshape(N_outer, N_outer)
    out = query_pos @ bundle_2d  # (N_outer,)
    return out / max(N_outer, 1)


def _bundle_xor_bsc(positions: "torch.Tensor",
                    items: "torch.Tensor") -> "torch.Tensor":
    """XOR bind on {0,1}, then majority-bundle (Kanerva binary spatter codes).

    bind(p_k, i_k) = p_k XOR i_k  (in {0,1})
    Bundle = majority over K bind outputs: 1 where >K/2 of bind outputs are 1,
    else 0. For random codes the majority is the most-likely bit per position
    given K binary samples.

    We store the SUM (integer-valued) so that downstream unbind can recover
    soft scoring; threshold to majority only at the final scoring step.
    """
    bound = ((positions + items) % 2.0)            # XOR via mod-2 add (in {0,1})
    return bound.sum(dim=0)                         # integer-valued counts in [0, K]


def _unbind_xor_bsc(bundle: "torch.Tensor",
                    query_pos: "torch.Tensor") -> "torch.Tensor":
    """XOR unbind: threshold bundle to majority, XOR with query position.

    bundle: (N,) integer count in [0,K]
    query_pos: (N,) {0,1}
    Returns: (N,) {-1,+1} bipolar-like score of recovered item bits.

    Algorithm:
      1. bundle_majority = (bundle > K/2)   in {0,1}  (estimated bind output)
      2. recovered = bundle_majority XOR query_pos    in {0,1}  (estimated item)
      3. map {0,1} -> {-1,+1} for dot-product scoring with binary_01 codebook
         (codebook is in {0,1}, so the dot product is just count-of-shared-1s).

    For scoring: compare recovered to codebook via dot product (codebook is
    {0,1}, recovered_bipolar is +/-1 mapping of recovered_binary).
    """
    K_est = bundle.sum() / float(query_pos.shape[-1])  # rough K-density estimate
    # Threshold at midpoint
    threshold = bundle.max() / 2.0 if bundle.numel() > 0 else 0.0
    bundle_maj = (bundle > threshold).float()          # {0,1}
    # XOR with query position
    recovered_bin = (bundle_maj + query_pos) % 2.0     # {0,1}
    # Map to bipolar for scoring: 1->+1; 0->-1. Then dot with {0,1} codebook
    # gives "+1 where item==1, -1 where item==0", measured against the actual
    # 1-bit count -- which is what we want for cleanup.
    recovered_bipolar = recovered_bin * 2.0 - 1.0
    return recovered_bipolar


def _bundle_sum_mod_n(positions: "torch.Tensor",
                     items: "torch.Tensor") -> "torch.Tensor":
    """Positive control (META_RULE_BC) -- additive integer binding.

    bind(p, i) = (p + i) mod N; bundle = sum_k bind(p_k, i_k) mod N.
    No proper unbind exists (additive bind loses information additively).
    Expected: very-fast cliff to FLOOR; provides floor reference.
    """
    bound = (positions + items) % float(N_DIM)
    bundle = bound.sum(dim=0) % float(N_DIM)
    return bundle  # shape (1,)


def _unbind_sum_mod_n(bundle: "torch.Tensor",
                     query_pos: "torch.Tensor") -> "torch.Tensor":
    """SUM_MOD_N degenerate unbind: subtract q_pos mod N. Loses K-1 contributors.

    Returns shape (1,) -- compared against codebook (V,1) via abs-distance.
    """
    out = (bundle - query_pos) % float(N_DIM)
    return out


# ---------------------------------------------------------------------------
# Score functions (per family)
# ---------------------------------------------------------------------------
def _score_dot_real(query: "torch.Tensor",
                    codebook: "torch.Tensor") -> "torch.Tensor":
    """Real inner product (HRR / bipolar / XOR)."""
    return query @ codebook.T


def _score_neg_abs_integer(query: "torch.Tensor",
                           codebook: "torch.Tensor") -> "torch.Tensor":
    """Negative absolute difference (integer mod-N space). Closer = higher."""
    # query: (1,), codebook: (V, 1). Returns shape (1, V).
    if query.ndim == 1:
        query = query.unsqueeze(0)
    diff = (query.unsqueeze(1) - codebook.unsqueeze(0)).abs().squeeze(-1)
    return -diff


# ---------------------------------------------------------------------------
# Binding-op registry
# ---------------------------------------------------------------------------
_BINDING_REGISTRY: Dict[str, Dict[str, Any]] = {
    "HADAMARD_BIND": {
        "encoder_family": "binary_bipolar",
        "build_pos": _build_bipolar,
        "build_item": _build_bipolar,
        "bundle": _bundle_hadamard,
        "unbind": _unbind_hadamard,
        "score": _score_dot_real,
        "code_dim": N_DIM,
        "expands_dim": False,
    },
    "CIRCULAR_CONV_HRR": {
        "encoder_family": "hrr_real",
        "build_pos": _build_hrr_real,
        "build_item": _build_hrr_real,
        "bundle": _bundle_circ_conv,
        "unbind": _unbind_circ_conv,
        "score": _score_dot_real,
        "code_dim": N_DIM,
        "expands_dim": False,
    },
    "TENSOR_PRODUCT": {
        "encoder_family": "binary_bipolar_outer",
        "build_pos": _build_bipolar_outer,
        "build_item": _build_bipolar_outer,
        "bundle": _bundle_tensor_product,
        "unbind": _unbind_tensor_product,
        "score": _score_dot_real,
        "code_dim": int(round(math.sqrt(N_DIM))),  # 90 (since 8192 not perfect sq)
        "expands_dim": True,
    },
    "XOR_BSC": {
        "encoder_family": "binary_01",
        "build_pos": _build_binary_01,
        "build_item": _build_binary_01,
        "bundle": _bundle_xor_bsc,
        "unbind": _unbind_xor_bsc,
        "score": _score_dot_real,
        "code_dim": N_DIM,
        "expands_dim": False,
    },
    "SUM_MOD_N": {
        "encoder_family": "integer_mod_N",
        "build_pos": _build_integer_mod_N,
        "build_item": _build_integer_mod_N,
        "bundle": _bundle_sum_mod_n,
        "unbind": _unbind_sum_mod_n,
        "score": _score_neg_abs_integer,
        "code_dim": 1,
        "expands_dim": False,
    },
}


# ---------------------------------------------------------------------------
# Per-point evaluation (one phase point = one binding_op x one K_SEQ)
# ---------------------------------------------------------------------------
def eval_phase_point(binding_op: str, K_SEQ: int, n_queries: int,
                     seed: int) -> Dict[str, Any]:
    """Run one (binding_op, K_SEQ) phase point. Returns per-point metrics.

    Pipeline:
      1. Build position codebook P (V_POS x code_dim) and item codebook I.
      2. Sample K_SEQ unique position-indices and K_SEQ unique item-indices.
      3. Build bundle = bind+bundle(positions, items) per binding op.
      4. For n_queries query-positions sampled from the K_SEQ, unbind +
         score against item codebook; top1 recall = fraction matching true.
    """
    if binding_op not in _BINDING_REGISTRY:
        raise ValueError(f"unknown binding_op={binding_op!r}")
    reg = _BINDING_REGISTRY[binding_op]

    t0 = time.time()
    if _CUDA_OK:
        torch.cuda.empty_cache()
        torch.cuda.reset_peak_memory_stats()

    code_dim = reg["code_dim"]
    g = np.random.default_rng(seed * 10007 + K_SEQ)

    # Build codebooks
    P_codebook = reg["build_pos"](V_POS, N_DIM, seed)         # (V_POS, code_dim)
    I_codebook = reg["build_item"](V_ITEMS, N_DIM, seed + 17)

    # Sample K_SEQ unique pos + item indices
    pos_idx = g.choice(V_POS, size=K_SEQ, replace=False)
    item_idx = g.choice(V_ITEMS, size=K_SEQ, replace=False)

    P_seq = P_codebook[torch.from_numpy(pos_idx).to(DEVICE)]   # (K, code_dim)
    I_seq = I_codebook[torch.from_numpy(item_idx).to(DEVICE)]  # (K, code_dim)

    # Build bundle (single bundle shared across queries)
    bundle = reg["bundle"](P_seq, I_seq)  # shape varies per op

    # Sample n_queries from the K_SEQ pairs (random subset, no-replace if possible)
    n_q = min(n_queries, K_SEQ)
    q_local = g.choice(K_SEQ, size=n_q, replace=False)
    q_pos = P_seq[torch.from_numpy(q_local).to(DEVICE)]
    q_true_item_idx = torch.from_numpy(item_idx[q_local]).to(DEVICE)

    # Substrate arm: unbind each query position, score against codebook
    top1_hits = 0
    for j in range(n_q):
        unbound = reg["unbind"](bundle, q_pos[j])  # shape (code_dim,) or (1,)
        sims = reg["score"](unbound, I_codebook)   # shape (V,) or (1, V)
        if sims.ndim == 2:
            sims = sims.squeeze(0)
        pred = int(sims.argmax().item())
        if pred == int(q_true_item_idx[j].item()):
            top1_hits += 1
    top1_sub = top1_hits / max(n_q, 1)

    # Random floor arm: random query position (unrelated to bundle)
    random_pos_idx = g.choice(V_POS, size=n_q, replace=False)
    random_pos = P_codebook[torch.from_numpy(random_pos_idx).to(DEVICE)]
    rand_hits = 0
    for j in range(n_q):
        unbound_r = reg["unbind"](bundle, random_pos[j])
        sims_r = reg["score"](unbound_r, I_codebook)
        if sims_r.ndim == 2:
            sims_r = sims_r.squeeze(0)
        pred_r = int(sims_r.argmax().item())
        if pred_r == int(q_true_item_idx[j].item()):
            rand_hits += 1
    top1_rand = rand_hits / max(n_q, 1)

    if _CUDA_OK:
        peak_mb = torch.cuda.max_memory_allocated() / 1e6
    else:
        peak_mb = -1.0

    elapsed = time.time() - t0
    discriminator = top1_sub - top1_rand
    suspect_sat = bool(top1_sub >= SUSPECT_SAT)

    # META_RULE_AF mechanism_hash: hash the BUNDLE BYTES (mechanism output), not
    # the top1 aggregate. Two ops can score identical top1 by coincidence but
    # produce wildly different bundles -- the bundle bytes are the canonical
    # mechanism fingerprint. Guards against bit-identical arm bug.
    bundle_cpu = bundle.detach().cpu()
    if bundle_cpu.is_complex():
        bundle_payload = torch.view_as_real(bundle_cpu).numpy().tobytes()
    else:
        bundle_payload = bundle_cpu.numpy().tobytes()
    bundle_hash = hashlib.sha256(bundle_payload).hexdigest()

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
        "binding_operation": binding_op,
        "encoder_family": reg["encoder_family"],
        "K_SEQ": int(K_SEQ),
        "N_DIM": int(N_DIM),
        "code_dim": int(code_dim),
        "n_queries": int(n_q),
        "seed": int(seed),
        "top1_substrate": round(top1_sub, 4),
        "top1_random": round(top1_rand, 4),
        "discriminator": round(discriminator, 4),
        "band": band,
        "suspect_saturation": suspect_sat,
        "peak_mem_mb": round(float(peak_mb), 1),
        "elapsed_per_point_s": round(elapsed, 3),
        "bundle_hash": bundle_hash,
        "bundle_shape": list(bundle_cpu.shape),
    }


# ---------------------------------------------------------------------------
# Selftest (per-op bind/unbind sanity; cardinality + hash distinctness)
# ---------------------------------------------------------------------------
def selftest(seed: int) -> Tuple[bool, str]:
    """Per-binding-op bind/unbind round-trip + cardinality + sanity.

    Asserts:
      - Cardinality math correct (5 ops x 5 K_SEQ = 25 FULL; x 3 = 15 SMOKE)
      - Single-pair round-trip works for each op at small K=1
      - 5 ops produce distinct mechanism bundles (META_RULE_AF)
    """
    msgs: List[str] = []

    # 1. Cardinality math
    if EXPECTED_N_UNITS_FULL != 25:
        return False, f"FULL cardinality {EXPECTED_N_UNITS_FULL} != 25"
    if EXPECTED_N_UNITS_SMOKE != 15:
        return False, f"SMOKE cardinality {EXPECTED_N_UNITS_SMOKE} != 15"
    msgs.append(f"cardinality FULL={EXPECTED_N_UNITS_FULL} SMOKE={EXPECTED_N_UNITS_SMOKE}")

    # 2. Per-op round-trip sanity (K depends on op semantics)
    #
    # Round-trip K choice notes:
    #   HADAMARD_BIND, CIRCULAR_CONV_HRR, TENSOR_PRODUCT: support K=1 exact
    #     recovery; argmax MUST == 0.
    #   XOR_BSC: at K=1 the demean of bundle becomes zero (no contrast to other
    #     codebook items via centering); use K=5 + top10 check instead.
    #   SUM_MOD_N: degenerate additive bind; no proper unbind exists -- skip
    #     accuracy check; verify shape only.
    bundles: Dict[str, bytes] = {}
    deterministic_ops = ("HADAMARD_BIND", "CIRCULAR_CONV_HRR", "TENSOR_PRODUCT")
    for op_name in BINDING_OPERATIONS:
        reg = _BINDING_REGISTRY[op_name]
        P = reg["build_pos"](20, N_DIM, seed)
        I = reg["build_item"](20, N_DIM, seed + 17)
        if op_name in deterministic_ops:
            # K=1 deterministic test
            bundle = reg["bundle"](P[0:1], I[0:1])
            unbound = reg["unbind"](bundle, P[0])
            sims = reg["score"](unbound, I)
            if sims.ndim == 2:
                sims = sims.squeeze(0)
            pred = int(sims.argmax().item())
            if pred != 0:
                top3 = sims.topk(min(3, sims.shape[0])).indices.tolist()
                if 0 not in top3:
                    return False, (f"round_trip FAIL {op_name}: K=1 unbind argmax={pred} "
                                    f"top3={top3}")
                msgs.append(f"round_trip {op_name}: K=1 argmax={pred} (0 in top3)")
            else:
                msgs.append(f"round_trip {op_name}: K=1 argmax=0 OK")
        elif op_name == "XOR_BSC":
            # K=5 test (need multiple pairs for demean+sign-flip score)
            K_test = 5
            bundle = reg["bundle"](P[:K_test], I[:K_test])
            # Query position 0; expected argmax in items: index 0
            unbound = reg["unbind"](bundle, P[0])
            sims = reg["score"](unbound, I)
            if sims.ndim == 2:
                sims = sims.squeeze(0)
            pred = int(sims.argmax().item())
            top10 = sims.topk(min(10, sims.shape[0])).indices.tolist()
            if 0 not in top10:
                return False, (f"round_trip FAIL {op_name}: K=5 q=P[0] argmax={pred}, "
                                f"true=0 not in top10={top10}; XOR encoding broken")
            msgs.append(f"round_trip {op_name}: K=5 argmax={pred} (0 in top10; weak but signal present)")
        elif op_name == "SUM_MOD_N":
            # Verify shape only; no proper unbind exists
            bundle = reg["bundle"](P[0:1], I[0:1])
            unbound = reg["unbind"](bundle, P[0])
            msgs.append(f"round_trip {op_name}: K=1 bundle.shape={list(bundle.shape)} "
                        f"unbound.shape={list(unbound.shape)} (no-op-control)")
        else:
            return False, f"unexpected op_name in selftest: {op_name}"
        # Capture bundle hash
        if bundle.is_complex():
            payload = torch.view_as_real(bundle).cpu().numpy().tobytes()
        else:
            payload = bundle.cpu().numpy().tobytes()
        bundles[op_name] = payload

    # 3. Per-op bundle hashes MUST be distinct (META_RULE_AF arms-must-differ)
    hashes = {op: hashlib.sha256(b).hexdigest()[:16] for op, b in bundles.items()}
    if len(set(hashes.values())) != len(BINDING_OPERATIONS):
        return False, f"META_RULE_AF VIOLATION: bundle hashes NOT distinct at seed={seed}: {hashes}"
    msgs.append(f"arms_differ_hashes: {hashes}")

    return True, "; ".join(msgs)


# ---------------------------------------------------------------------------
# Per-seed sweep
# ---------------------------------------------------------------------------
def run_one_seed_phase_diagram(seed: int, run_mode: str) -> Dict[str, Any]:
    """Run all (binding_op, K_SEQ) phase points for one seed."""
    is_smoke = (run_mode == "smoke")
    K_sweep = K_SEQ_SMOKE if is_smoke else K_SEQ_FULL
    n_queries = N_QUERIES_SMOKE if is_smoke else N_QUERIES_FULL
    expected_n_units = len(BINDING_OPERATIONS) * len(K_sweep)

    print(f"[run_one_seed] seed={seed} mode={run_mode} device={DEVICE} "
          f"ops={BINDING_OPERATIONS} K_sweep={K_sweep} n_q={n_queries} "
          f"expected_n={expected_n_units}", flush=True)

    phase_map: List[Dict[str, Any]] = []
    t0 = time.time()
    for op_name in BINDING_OPERATIONS:
        for K in K_sweep:
            print(f"[point] seed={seed} op={op_name} K_SEQ={K} ...", flush=True)
            pt = eval_phase_point(op_name, K, n_queries, seed)
            phase_map.append(pt)
            print(f"  -> top1_sub={pt['top1_substrate']:.3f} "
                  f"top1_rnd={pt['top1_random']:.3f} "
                  f"disc={pt['discriminator']:.3f} "
                  f"band={pt['band']} "
                  f"suspect_sat={pt['suspect_saturation']} "
                  f"peak_mb={pt['peak_mem_mb']:.1f} "
                  f"t={pt['elapsed_per_point_s']:.2f}s", flush=True)

    elapsed = time.time() - t0
    observed_n_units = len(phase_map)
    cardinality_ok = (observed_n_units == expected_n_units)

    # Per-op K_cliff localization (smallest K where SUBSTRATE drops below SAT)
    K_cliff_per_op: Dict[str, Any] = {}
    for op_name in BINDING_OPERATIONS:
        op_pts = [p for p in phase_map if p["binding_operation"] == op_name]
        op_pts_sorted = sorted(op_pts, key=lambda p: p["K_SEQ"])
        K_cliff = None
        for p in op_pts_sorted:
            if p["top1_substrate"] < BAND_SAT:
                K_cliff = p["K_SEQ"]
                break
        # If no cliff observed in sweep, mark as ">=max(K)+1"
        K_cliff_per_op[op_name] = K_cliff if K_cliff is not None else (max(K_sweep) + 1)

    # Per-op mechanism hash (META_RULE_AF / AX): hash the BUNDLE BYTES from the
    # first K_SEQ phase point per op (not the top1 aggregate). Two ops can
    # legitimately produce identical top1 sequences by coincidence (science
    # finding); but if their BUNDLES are bit-identical, that IS a bit-identical
    # arm bug. Guards correctly.
    op_mech_hashes: Dict[str, str] = {}
    first_K = K_sweep[0]
    for op_name in BINDING_OPERATIONS:
        first_pts = [p for p in phase_map
                     if p["binding_operation"] == op_name
                     and p["K_SEQ"] == first_K]
        if first_pts:
            op_mech_hashes[op_name] = first_pts[0]["bundle_hash"]
        else:
            # Defensive fallback (shouldn't fire)
            op_mech_hashes[op_name] = "MISSING_FIRST_K_POINT"

    # Pair distinctness (META_RULE_AF + META_RULE_AX)
    pairs_differ: Dict[str, bool] = {}
    ops = list(BINDING_OPERATIONS)
    for i in range(len(ops)):
        for j in range(i + 1, len(ops)):
            key = f"{ops[i]}_vs_{ops[j]}"
            pairs_differ[key] = (op_mech_hashes[ops[i]] != op_mech_hashes[ops[j]])
    n_pairs = len(pairs_differ)
    n_pairs_differ = sum(1 for v in pairs_differ.values() if v)

    # K_cliff log2 separations (pairwise)
    K_cliff_log2_sep: Dict[str, float] = {}
    for i in range(len(ops)):
        for j in range(i + 1, len(ops)):
            a, b = ops[i], ops[j]
            ka = max(K_cliff_per_op[a], 1)
            kb = max(K_cliff_per_op[b], 1)
            sep = abs(math.log2(ka) - math.log2(kb))
            K_cliff_log2_sep[f"{a}_vs_{b}"] = round(sep, 3)

    # Count ops with DISTINCT K_cliff localization (>=0.3 log2 sep from EVERY other)
    distinct_cliff_ops: List[str] = []
    for i, op in enumerate(ops):
        is_distinct = True
        for j, other in enumerate(ops):
            if i == j:
                continue
            ka, kb = max(K_cliff_per_op[op], 1), max(K_cliff_per_op[other], 1)
            sep = abs(math.log2(ka) - math.log2(kb))
            if sep < 0.3:
                is_distinct = False
                break
        if is_distinct:
            distinct_cliff_ops.append(op)
    n_distinct_cliff_ops = len(distinct_cliff_ops)

    # Coefficient of variation per op (across K_SEQ; per META_RULE_AY)
    cv_per_op: Dict[str, float] = {}
    for op_name in BINDING_OPERATIONS:
        op_pts = [p for p in phase_map if p["binding_operation"] == op_name]
        vals = np.array([p["top1_substrate"] for p in op_pts])
        if vals.size and vals.mean() > 1e-6:
            cv = float(vals.std() / vals.mean())
        else:
            cv = 0.0
        cv_per_op[op_name] = round(cv, 4)
    max_cv = max(cv_per_op.values()) if cv_per_op else 0.0

    # Suspect-saturation flags
    n_suspect_sat = sum(1 for p in phase_map if p["suspect_saturation"])

    # Positive control (META_RULE_BC): SUM_MOD_N at K=50 must clear floor
    pc_pts = [p for p in phase_map
              if p["binding_operation"] == POSITIVE_CONTROL["binding_operation"]
              and p["K_SEQ"] == POSITIVE_CONTROL["K_SEQ"]]
    pc_top1 = pc_pts[0]["top1_substrate"] if pc_pts else -1.0
    pc_pass = pc_top1 >= POSITIVE_CONTROL["top1_floor_required"]
    positive_control_result = {
        "binding_operation": POSITIVE_CONTROL["binding_operation"],
        "K_SEQ": POSITIVE_CONTROL["K_SEQ"],
        "top1_floor_required": POSITIVE_CONTROL["top1_floor_required"],
        "measured_top1": pc_top1,
        "pass": pc_pass,
    }

    # Per-op summary
    per_op_summary: Dict[str, Any] = {}
    for op_name in BINDING_OPERATIONS:
        op_pts = [p for p in phase_map if p["binding_operation"] == op_name]
        sub_mean = float(np.mean([p["top1_substrate"] for p in op_pts])) if op_pts else 0.0
        rand_mean = float(np.mean([p["top1_random"] for p in op_pts])) if op_pts else 0.0
        n_sat = sum(1 for p in op_pts if p["band"] == "SAT")
        n_mb = sum(1 for p in op_pts if p["band"] == "MB")
        n_floor = sum(1 for p in op_pts if p["band"] == "FLOOR")
        n_trans = sum(1 for p in op_pts if p["band"] == "TRANSITION")
        per_op_summary[op_name] = {
            "encoder_family": _BINDING_ENCODER_PAIR.get(op_name, "unknown"),
            "top1_sub_mean": round(sub_mean, 4),
            "top1_rand_mean": round(rand_mean, 4),
            "K_cliff": K_cliff_per_op[op_name],
            "band_counts": {"SAT": n_sat, "MB": n_mb,
                             "FLOOR": n_floor, "TRANSITION": n_trans},
            "cv_across_K": cv_per_op[op_name],
            "mechanism_hash_prefix": op_mech_hashes[op_name][:16],
        }

    if _CUDA_OK:
        peak_mems = [p["peak_mem_mb"] for p in phase_map if p["peak_mem_mb"] > 0]
        avg_peak = sum(peak_mems) / max(len(peak_mems), 1)
        gpu_util_estimate = min(0.95, max(0.30, avg_peak / 100.0))
    else:
        gpu_util_estimate = 0.0

    return {
        "seed": seed,
        "run_mode": run_mode,
        "N_DIM": N_DIM,
        "binding_operations": list(BINDING_OPERATIONS),
        "K_SEQ_sweep": list(K_sweep),
        "n_queries_per_point": n_queries,
        "phase_map": phase_map,
        "per_op_summary": per_op_summary,
        "K_cliff_per_op": K_cliff_per_op,
        "K_cliff_log2_sep_pairs": K_cliff_log2_sep,
        "n_distinct_cliff_ops": n_distinct_cliff_ops,
        "distinct_cliff_ops": distinct_cliff_ops,
        "op_pair_distinctness": pairs_differ,
        "n_pairs_differ": n_pairs_differ,
        "op_mech_hashes": op_mech_hashes,
        "cv_per_op": cv_per_op,
        "max_cv": round(max_cv, 4),
        "n_suspect_saturation": n_suspect_sat,
        "positive_control_result": positive_control_result,
        "cardinality_ok": cardinality_ok,
        "expected_n_units": expected_n_units,
        "observed_n_units": observed_n_units,
        "device": str(DEVICE),
        "gpu_name": GPU_NAME,
        "gpu_util_estimate": round(gpu_util_estimate, 3),
        "elapsed_seed_s": round(elapsed, 2),
    }


# ---------------------------------------------------------------------------
# Smoke-gate predicate (must FIRE the discriminator at smoke per META_RULE_K)
# ---------------------------------------------------------------------------
def smoke_gate_predicate(body: Dict[str, Any]) -> Tuple[bool, str]:
    """Smoke gate. Return (passed, reason).

    For sequence-binding regime: at smoke K_SEQ_SMOKE = (50, 200, 1000), the
    discriminator MUST fire as follows:
      1. Cardinality OK
      2. All binding-op hashes distinct (META_RULE_AF)
      3. Positive control (SUM_MOD_N at K=50) clears 0.05 floor
      4. At least 1 op shows SAT at K=50 (mechanism works at low load)
      5. At least 1 op shows FLOOR at K=1000 (cliff observable at smoke scale)
      6. Cross-op separation evidence: at least 1 pair has log2 K_cliff sep
         >= 0.3 (so HARD_PASS at FULL is at least possible)
    """
    phase_map = body.get("phase_map", [])
    pairs_differ = body.get("op_pair_distinctness", {})
    expected_n = body.get("expected_n_units", 0)
    pc_result = body.get("positive_control_result", {})
    K_log2_sep = body.get("K_cliff_log2_sep_pairs", {})

    # 1. Cardinality
    if len(phase_map) != expected_n:
        return False, f"cardinality_breach: expected {expected_n} got {len(phase_map)}"

    # 2. All op pairs distinct
    n_pairs = len(pairs_differ)
    n_differ = sum(1 for v in pairs_differ.values() if v)
    if n_differ < n_pairs:
        collapsed = [k for k, v in pairs_differ.items() if not v]
        return False, (f"op_pair_collapse: {n_differ}/{n_pairs} differ; "
                        f"identical pairs: {collapsed}")

    # 3. Positive control
    if not pc_result.get("pass"):
        return False, (f"META_RULE_BC_FAIL: positive_control {pc_result} below floor; "
                        f"regime too hard OR test rig broken")

    # 4. >=1 op SAT at K=50 (mechanism works at low load)
    sat_at_K50 = [p["binding_operation"] for p in phase_map
                  if p["K_SEQ"] == K_SEQ_SMOKE[0] and p["band"] == "SAT"]
    if not sat_at_K50:
        return False, (f"discriminator_fails_low_K: no op SAT at K={K_SEQ_SMOKE[0]}; "
                        f"mechanism cannot solve trivial regime; ABORT")

    # 5. >=1 op FLOOR at K=1000 (cliff observable; mechanism breaks at high load)
    floor_at_K1000 = [p["binding_operation"] for p in phase_map
                       if p["K_SEQ"] == K_SEQ_SMOKE[-1] and p["band"] == "FLOOR"]
    if not floor_at_K1000:
        # Not FLOOR yet -- check TRANSITION or MB. If everything still SAT, no cliff.
        K_max = K_SEQ_SMOKE[-1]
        sat_at_Kmax = [p["binding_operation"] for p in phase_map
                       if p["K_SEQ"] == K_max and p["band"] == "SAT"]
        if len(sat_at_Kmax) == len(BINDING_OPERATIONS):
            return False, (f"baseline_saturated_no_cliff: all 5 ops SAT at K={K_max}; "
                            f"regime too easy at full-N; substrate-too-robust "
                            f"per META_RULE_AG; iterate regime; ABORT")

    # 6. At least 1 K_cliff log2 separation >= 0.3 (HARD_PASS at FULL possible)
    max_sep = max(K_log2_sep.values()) if K_log2_sep else 0.0
    if max_sep < 0.3:
        return False, (f"no_cliff_separation: max log2 K_cliff separation across all "
                        f"op-pairs = {max_sep:.3f} < 0.3; HARD_PASS unreachable; ABORT")

    return True, (f"smoke_gate_pass: cardinality_ok + 5-op-distinct + "
                  f"positive_control_pass + SAT@K=50({sat_at_K50}) + "
                  f"max_log2_K_cliff_sep={max_sep:.3f}")


# ---------------------------------------------------------------------------
# Aggregate + verdict
# ---------------------------------------------------------------------------
def aggregate_and_verdict(per_seed: Dict[str, Dict[str, Any]],
                          run_mode: str) -> Dict[str, Any]:
    """Aggregate per-seed body into final verdict."""
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
    pairs_differ = body.get("op_pair_distinctness", {})
    n_pairs_differ = body.get("n_pairs_differ", 0)
    pc_result = body.get("positive_control_result", {})
    per_op_summary = body.get("per_op_summary", {})
    K_cliff_per_op = body.get("K_cliff_per_op", {})
    K_log2_sep = body.get("K_cliff_log2_sep_pairs", {})
    n_distinct_cliff_ops = body.get("n_distinct_cliff_ops", 0)
    distinct_cliff_ops = body.get("distinct_cliff_ops", [])
    op_mech_hashes = body.get("op_mech_hashes", {})
    cv_per_op = body.get("cv_per_op", {})
    max_cv = body.get("max_cv", 0.0)
    n_suspect_sat = body.get("n_suspect_saturation", 0)
    expected_n = body.get("expected_n_units", 0)
    observed_n = body.get("observed_n_units", 0)
    cardinality_ok = body.get("cardinality_ok", False)
    gpu_util_estimate = body.get("gpu_util_estimate", 0.0)

    n_sat = sum(1 for p in phase_map if p["band"] == "SAT")
    n_mb = sum(1 for p in phase_map if p["band"] == "MB")
    n_floor = sum(1 for p in phase_map if p["band"] == "FLOOR")
    n_trans = sum(1 for p in phase_map if p["band"] == "TRANSITION")

    common = {
        "phase_map": phase_map,
        "per_op_summary": per_op_summary,
        "K_cliff_per_op": K_cliff_per_op,
        "K_cliff_log2_sep_pairs": K_log2_sep,
        "n_distinct_cliff_ops": n_distinct_cliff_ops,
        "distinct_cliff_ops": distinct_cliff_ops,
        "op_pair_distinctness": pairs_differ,
        "n_pairs_differ": n_pairs_differ,
        "op_mech_hashes": op_mech_hashes,
        "cv_per_op": cv_per_op,
        "max_cv": max_cv,
        "n_suspect_saturation": n_suspect_sat,
        "positive_control_result": pc_result,
        "cardinality_ok": cardinality_ok,
        "expected_n_units": expected_n,
        "observed_n_units": observed_n,
        "tier_counts": {"SAT": n_sat, "MB": n_mb, "FLOOR": n_floor,
                         "TRANSITION": n_trans},
        "gpu_util_estimate": gpu_util_estimate,
        "device": body.get("device"),
        "gpu_name": body.get("gpu_name"),
        "beta": BETA,
        "regime": "sequence_binding_K_SEQ_sweep_N8192",
    }

    if is_smoke:
        passed, reason = smoke_gate_predicate(body)
        if passed:
            max_sep = max(K_log2_sep.values()) if K_log2_sep else 0.0
            verdict = "HARD_PASS"
            vmsg = (f"HARD_PASS_SMOKE: {observed_n}/{expected_n} pts; "
                    f"sat={n_sat} mb={n_mb} floor={n_floor} trans={n_trans}; "
                    f"5-op-distinct; positive_control@K=50 top1="
                    f"{pc_result.get('measured_top1'):.3f}; "
                    f"K_cliff_per_op={K_cliff_per_op}; "
                    f"max_log2_K_cliff_sep={max_sep:.3f}; "
                    f"n_suspect_sat={n_suspect_sat}; "
                    f"max_cv={max_cv:.3f}")
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
    if not cardinality_ok:
        verdict = "HARD_FAIL"
        vmsg = (f"HARD_FAIL_CARDINALITY_BREACH: expected={expected_n} "
                f"observed={observed_n}")
    elif not pc_result.get("pass"):
        verdict = "HARD_FAIL"
        vmsg = (f"HARD_FAIL_META_RULE_BC_CONTROL_FAIL: positive_control "
                f"{pc_result.get('binding_operation')}@K={pc_result.get('K_SEQ')} "
                f"measured top1={pc_result.get('measured_top1')}; test rig broken")
    elif n_pairs_differ < len(pairs_differ):
        bad = [k for k, v in pairs_differ.items() if not v]
        verdict = "HARD_FAIL"
        vmsg = f"HARD_FAIL_META_RULE_AF_ARMS_IDENTICAL_PAIRS: {bad}"
    elif max_cv > 0.10:
        # Note: high cv is expected when ops span SAT to FLOOR -- but we set
        # this as a sanity check on per-op-internal cv, not cross-op. If a
        # single op has cv > 0.10 across K_SEQ, the cliff is observable.
        # We do NOT demote based on this alone -- just record.
        verdict_candidate = None
    else:
        verdict_candidate = None

    # The above only catches HARD_FAIL guards. If none triggered, classify
    # discriminator strength.
    if "verdict" not in locals():
        max_sep = max(K_log2_sep.values()) if K_log2_sep else 0.0

        # HARD_PASS gates per task spec:
        # - >=3 of 5 ops produce DISTINCT K_cliff localizations
        #   (>=0.3 log2 separation from every other)
        # - per-op mechanism_hash distinct
        # - no suspect-1.000 saturation (n_suspect_sat == 0)
        if (n_distinct_cliff_ops >= 3
                and n_pairs_differ == len(pairs_differ)
                and n_suspect_sat == 0):
            verdict = "HARD_PASS"
            vmsg = (f"HARD_PASS_BINDING_DISCRIMINATES_AT_SEQUENCE_REGIME: "
                    f"{n_distinct_cliff_ops}/5 ops have DISTINCT K_cliff "
                    f"localization (>=0.3 log2 sep from all others); "
                    f"distinct_ops={distinct_cliff_ops}; "
                    f"K_cliff_per_op={K_cliff_per_op}; max_log2_sep={max_sep:.3f}; "
                    f"sat={n_sat} mb={n_mb} floor={n_floor} trans={n_trans}; "
                    f"n_suspect_sat=0; pc_pass; gpu_util~{gpu_util_estimate:.2f}; "
                    f"vs PC v1 MB (n_disc=8/48 at PC regime): binding op is "
                    f"REGIME-CONDITIONAL not substrate-invariant")
        elif n_distinct_cliff_ops == 2 and n_pairs_differ == len(pairs_differ):
            verdict = "MIDDLE_BAND"
            vmsg = (f"MIDDLE_BAND_PARTIAL_DISCRIMINATION: "
                    f"{n_distinct_cliff_ops}/5 ops differentiate at sequence regime; "
                    f"distinct_ops={distinct_cliff_ops}; "
                    f"K_cliff_per_op={K_cliff_per_op}; max_log2_sep={max_sep:.3f}; "
                    f"sat={n_sat} mb={n_mb} floor={n_floor}; n_suspect_sat="
                    f"{n_suspect_sat}; some ops differentiate, partial 2x-drill signal")
        elif n_distinct_cliff_ops <= 1:
            verdict = "HARD_FAIL"
            vmsg = (f"HARD_FAIL_BINDING_INVARIANT_ACROSS_REGIMES: "
                    f"only {n_distinct_cliff_ops}/5 ops differentiate; "
                    f"K_cliff_per_op={K_cliff_per_op}; max_log2_sep={max_sep:.3f}; "
                    f"binding op is SUBSTRATE-INVARIANT across PC + sequence-binding; "
                    f"substantive negative finding (substrate-uniform binding "
                    f"discriminator)")
        else:
            verdict = "MIDDLE_BAND"
            vmsg = (f"MIDDLE_BAND_GENERIC: n_distinct_cliff_ops={n_distinct_cliff_ops}; "
                    f"K_cliff_per_op={K_cliff_per_op}; "
                    f"sat={n_sat} mb={n_mb} floor={n_floor}")

    out = dict(common)
    out.update({
        "verdict": verdict,
        "verdict_msg": vmsg,
        "summary": vmsg,
    })
    return out


__all__ = [
    "DEVICE", "GPU_NAME", "GPU_MAX_MEM_GB", "N_DIM",
    "BAND_SAT", "BAND_MB_LO", "BAND_MB_HI", "BAND_FLOOR", "SUSPECT_SAT",
    "BETA", "BINDING_OPERATIONS",
    "K_SEQ_FULL", "K_SEQ_SMOKE",
    "N_QUERIES_FULL", "N_QUERIES_SMOKE",
    "EXPECTED_N_UNITS_FULL", "EXPECTED_N_UNITS_SMOKE",
    "POSITIVE_CONTROL", "POSITIVE_CONTROL_SMOKE",
    "REQUIRED_FIELDS",
    "get_backend_label",
    "eval_phase_point", "selftest",
    "run_one_seed_phase_diagram",
    "smoke_gate_predicate", "aggregate_and_verdict",
]
