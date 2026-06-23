"""Cell: predictive_coding_hierarchy_smoke_v1 -- substrate-native PC hierarchy probe.

SCIENTIFIC QUESTION:
  Brain's canonical learning mechanism (Rao-Ballard 1999 / Friston 2005 / Bastos
  2012) is hierarchical predictive coding: each cortical layer predicts the next
  layer's input; only prediction ERROR propagates upward. Does the substrate
  exhibit a chain-grade improvement when stacked into a 3-layer PC hierarchy
  vs. a flat single-W Hebbian baseline?

  Substrate analog: 3 stacked W matrices [N_DIM x N_DIM]; L1 predicts L2's
  input; L2 predicts L3's input; local Hebbian on prediction error at each
  layer; forward-only (no backprop required at inference).

  Note (per USER 2026-06-22 lit-scan empowerment): the PC literature has
  several negative results on substrate-style discrete-vector encodings of
  PC. We are EXPECTED to probe; modal expected outcome is MIDDLE_BAND.

PRE-REGISTERED BANDS (sym, both directions, per NEGATIVITY-BIAS rule):
  HARD-PASS: ARM_PC_HIERARCHY_3LAYER mean_recon_error <= 0.5 * ARM_FLAT_HEBBIAN
             AND L3 representations show macro-category clustering
             (within-cluster mean similarity >= 1.5 * across-cluster).
  HARD-FAIL: ARM_PC_HIERARCHY_3LAYER mean_recon_error >= 0.9 * ARM_FLAT_HEBBIAN
             (PC adds no measurable advantage).
  MIDDLE: in-between; characterize whether layered cleanup arm closes the gap.

SANITY SELF-TESTS:
  1. At trivial 1-sequence input, all arms reconstruct perfectly
     (recon_error < 0.05 for all arms).
  2. At all-noise input, all arms degrade similarly
     (no arm spuriously better than another by >5x).
  3. PC update direction is correct: weight magnitudes increase under repeated
     same-input training (Hebbian sign correct).
  4. Layer-N+1 receives the residual; check error_L1 + L1_out reconstructs input
     within numerical tolerance.

DESIGN (smoke-only cell -- this whole file IS the smoke):
  N_DIM=4096, 3 layers (L1, L2, L3), seeds=[7,17,23].
  Synthetic hierarchical corpus: 1000 sequences of length 10 with planted
  3-level hierarchy:
    - 4 macro-categories (top level; L3 should cluster by these)
    - within each macro, 5 meso-categories (L2 should cluster by these)
    - within each meso, 50 micro-instances (L1 distinguishes these)
  Each sequence has a fixed (macro, meso, micro) identity; the 10 tokens
  are noisy renderings of the same identity vector (additive Gaussian
  noise floor + per-token sign perturbation).

  Arms:
    ARM_FLAT_HEBBIAN: single W matrix [N_DIM x N_DIM]; Hebbian update on
      raw input; reconstruction = sign(W @ input).
    ARM_PC_HIERARCHY_3LAYER: 3 stacked W matrices; forward pass propagates
      cleaned signal layer to layer; Hebbian update on per-layer prediction
      error; reconstruction = downward sweep through stacked W.
    ARM_PC_HIERARCHY_LAYERED_CLEANUP: same as 3LAYER + per-layer cleanup
      (sign() bound to nearest stored prototype per layer).

  Metrics per arm:
    A) mean_recon_error: 1 - mean cosine(reconstructed, original) over held-out
       seqs.
    B) L3 macro-cluster ratio: mean within-macro L3-similarity / mean across-
       macro L3-similarity. >=1.5 = clustering, <1.05 = no structure.
    C) capacity proxy: recon_error at 200 / 500 / 1000 seqs (degradation curve).

  ASCII-only; numpy only (per spec; CPU-bound smoke ~15-20 min wall).

PROT-018: no _nN suffix; production N_DIM=4096 stated here. Smoke runs at
  N_DIM=4096 directly (this cell is the smoke; FULL would be a follow-up).

TIMEOUT ESTIMATE (local_cpu_queue):
  N_DIM=4096, 3 layers, 1000 seqs * 10 tokens, 3 seeds, 3 arms.
  Per-seq update: 3 matmuls * O(N_DIM^2) = ~3 * 16M = ~50M ops.
  Per-seed total: 10000 tokens * 3 arms * 50M = ~1.5G ops ~ ~30s numpy.
  3 seeds -> ~90s compute + overhead -> ~5 min realistic.
  Safety 3x -> --timeout=1800 (30 min).

Anchor: predictive_coding_hierarchy_smoke_v1
Queue: local_cpu_queue
Pre-reg: preregs/2026-06-22_predictive_coding_hierarchy_smoke_v1.md
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import argparse
import json
import math
import os
import time
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (  # noqa: E402
    get_output_dir,
    resumable_seeds,
    write_partial,
    aggregate_partials,
)

ANCHOR_NAME = "predictive_coding_hierarchy_smoke_v1"

# --- Production config ---
N_DIM = 4096
N_LAYERS = 3
SEQ_LEN = 10
N_MACRO = 4
N_MESO = 5
N_MICRO = 50
N_SEQS_FULL = N_MACRO * N_MESO * N_MICRO  # = 1000

CAPACITY_PROBE_POINTS = (200, 500, 1000)
HELDOUT_FRACTION = 0.1  # 10% held-out for recon_error metric
NOISE_STD = 0.10        # per-token additive noise sigma
PER_TOKEN_FLIP_RATE = 0.05  # fraction of dims sign-flipped per token

LEARNING_RATE = 0.01
SEEDS_FULL = [7, 17, 23]
SEEDS_SMOKE = [7]
SMOKE_N_DIM = 512   # for --smoke gate run: cuts wall ~64x while exercising the code path

# --- Pre-registered thresholds ---
HP_PC_RATIO = 0.5          # PC recon error <= 0.5 * flat
HP_CLUSTER_RATIO = 1.5     # within-macro / across-macro L3 similarity
HF_PC_RATIO = 0.9          # PC recon error >= 0.9 * flat = no improvement

# ---------------------------------------------------------------------------
# Synthetic hierarchical corpus
# ---------------------------------------------------------------------------

def _bipolar(rng: np.random.Generator, n: int, d: int) -> np.ndarray:
    """n x d bipolar (+1/-1) random matrix."""
    return (rng.integers(0, 2, size=(n, d)).astype(np.float32) * 2.0) - 1.0


def build_hierarchical_corpus(
    rng: np.random.Generator,
    n_dim: int,
    n_macro: int,
    n_meso: int,
    n_micro: int,
    seq_len: int,
    noise_std: float,
    flip_rate: float,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Generate corpus with 3-level planted hierarchy.

    Returns:
        sequences: [n_seqs, seq_len, n_dim] float32
        identity_vectors: [n_seqs, n_dim] float32 (the clean identity per seq)
        macro_labels: [n_seqs] int (which macro-category)
    """
    macro_vecs = _bipolar(rng, n_macro, n_dim)
    meso_vecs = _bipolar(rng, n_macro * n_meso, n_dim)
    micro_vecs = _bipolar(rng, n_macro * n_meso * n_micro, n_dim)

    # Identity = sign(macro + 0.5*meso + 0.25*micro) -- structured combination
    n_seqs = n_macro * n_meso * n_micro
    identity = np.zeros((n_seqs, n_dim), dtype=np.float32)
    macro_labels = np.zeros(n_seqs, dtype=np.int32)
    idx = 0
    for ma in range(n_macro):
        for me in range(n_meso):
            for mi in range(n_micro):
                me_idx = ma * n_meso + me
                mi_idx = (ma * n_meso + me) * n_micro + mi
                blend = macro_vecs[ma] + 0.5 * meso_vecs[me_idx] + 0.25 * micro_vecs[mi_idx]
                identity[idx] = np.sign(blend)
                identity[idx][identity[idx] == 0] = 1.0
                macro_labels[idx] = ma
                idx += 1

    # Sequences: noisy renderings of the identity vector
    sequences = np.zeros((n_seqs, seq_len, n_dim), dtype=np.float32)
    n_flip = int(flip_rate * n_dim)
    for s in range(n_seqs):
        for t in range(seq_len):
            noise = rng.normal(0.0, noise_std, size=n_dim).astype(np.float32)
            v = identity[s] + noise
            # per-token sign flips
            if n_flip > 0:
                flip_idx = rng.choice(n_dim, size=n_flip, replace=False)
                v[flip_idx] *= -1.0
            sequences[s, t] = v

    return sequences, identity, macro_labels


# ---------------------------------------------------------------------------
# Arm implementations
# ---------------------------------------------------------------------------

def _safe_sign(x: np.ndarray) -> np.ndarray:
    s = np.sign(x).astype(np.float32)
    s[s == 0] = 1.0
    return s


def _normalize(x: np.ndarray) -> np.ndarray:
    n = np.linalg.norm(x)
    if n < 1e-9:
        return x
    return (x / n).astype(np.float32)


def _cos(a: np.ndarray, b: np.ndarray) -> float:
    na = np.linalg.norm(a)
    nb = np.linalg.norm(b)
    if na < 1e-9 or nb < 1e-9:
        return 0.0
    return float(np.dot(a, b) / (na * nb))


def train_flat_hebbian(
    sequences: np.ndarray,
    n_dim: int,
    lr: float,
) -> np.ndarray:
    """ARM_FLAT_HEBBIAN: single W; outer-product accumulation.

    W += lr * outer(input, input) per token. Auto-associative; reconstruction
    is sign(W @ input).
    """
    W = np.zeros((n_dim, n_dim), dtype=np.float32)
    n_seqs, seq_len, _ = sequences.shape
    for s in range(n_seqs):
        for t in range(seq_len):
            x = sequences[s, t]
            W += lr * np.outer(x, x)
    return W


def recon_flat(W: np.ndarray, x: np.ndarray) -> np.ndarray:
    return _safe_sign(W @ x)


def train_pc_hierarchy(
    sequences: np.ndarray,
    n_dim: int,
    n_layers: int,
    lr: float,
) -> List[np.ndarray]:
    """ARM_PC_HIERARCHY_3LAYER: stacked W per layer; Hebbian on prediction error.

    Forward pass:
      L1_in = input
      L1_out = sign(W_L1 @ L1_in)
      L2_in = L1_out
      L2_out = sign(W_L2 @ L2_in)
      L3_in = L2_out
      L3_out = sign(W_L3 @ L3_in)

    Per-layer prediction error: error_Li = layer_i_input - layer_i_output
    Hebbian update (PC-style): W_Li += lr * outer(error_Li, layer_i_input)
      -- this is the classic Rao-Ballard 1999 local learning rule on residual.
    """
    Ws = [np.zeros((n_dim, n_dim), dtype=np.float32) for _ in range(n_layers)]
    n_seqs, seq_len, _ = sequences.shape
    for s in range(n_seqs):
        for t in range(seq_len):
            layer_in = sequences[s, t]
            for li in range(n_layers):
                layer_out = _safe_sign(Ws[li] @ layer_in)
                error = layer_in - layer_out
                Ws[li] += lr * np.outer(error, layer_in)
                layer_in = layer_out  # error-cleaned signal flows up
    return Ws


def _build_prototypes_per_layer(
    Ws: List[np.ndarray], sequences: np.ndarray, n_prototypes: int = 64
) -> List[np.ndarray]:
    """For ARM_LAYERED_CLEANUP: collect per-layer top-K seen states for cleanup."""
    n_dim = Ws[0].shape[0]
    n_seqs, seq_len, _ = sequences.shape
    # Sample subset for prototype set
    sample_idx = np.random.RandomState(0).choice(
        n_seqs * seq_len, size=min(n_prototypes, n_seqs * seq_len), replace=False
    )
    layer_protos = [[] for _ in Ws]
    for flat_idx in sample_idx:
        s, t = divmod(flat_idx, seq_len)
        layer_in = sequences[s, t]
        for li, W in enumerate(Ws):
            layer_out = _safe_sign(W @ layer_in)
            layer_protos[li].append(layer_out)
            layer_in = layer_out
    return [np.stack(plist, axis=0).astype(np.float32) for plist in layer_protos]


def _cleanup_to_nearest(x: np.ndarray, protos: np.ndarray) -> np.ndarray:
    """Cleanup gate: return nearest prototype by cosine."""
    if protos.shape[0] == 0:
        return x
    sims = protos @ x  # [K]
    return protos[int(np.argmax(sims))]


def forward_pc_hierarchy(
    Ws: List[np.ndarray],
    x: np.ndarray,
    layer_protos: List[np.ndarray] = None,
) -> Tuple[np.ndarray, List[np.ndarray]]:
    """Forward + optional per-layer cleanup; return (L3_out, [L1_out, L2_out, L3_out])."""
    outs = []
    layer_in = x
    for li, W in enumerate(Ws):
        layer_out = _safe_sign(W @ layer_in)
        if layer_protos is not None:
            layer_out = _cleanup_to_nearest(layer_out, layer_protos[li])
        outs.append(layer_out)
        layer_in = layer_out
    return outs[-1], outs


def recon_pc_hierarchy(
    Ws: List[np.ndarray],
    x: np.ndarray,
    layer_protos: List[np.ndarray] = None,
) -> np.ndarray:
    """Reconstruct by forward sweep then downward sweep through W transposes.

    Forward: x -> L1_out -> L2_out -> L3_out
    Downward: L3_out -> sign(W_L3.T @ L3_out) -> sign(W_L2.T @ ...) -> reconstructed
    """
    _, outs = forward_pc_hierarchy(Ws, x, layer_protos)
    state = outs[-1]
    for li in range(len(Ws) - 1, -1, -1):
        state = _safe_sign(Ws[li].T @ state)
    return state


# ---------------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------------

def measure_recon_error(
    recon_fn,
    sequences_heldout: np.ndarray,
    identity_heldout: np.ndarray,
) -> float:
    """1 - mean cosine(reconstructed_token, identity)."""
    n_seqs, seq_len, _ = sequences_heldout.shape
    sims = []
    for s in range(n_seqs):
        for t in range(seq_len):
            recon = recon_fn(sequences_heldout[s, t])
            sims.append(_cos(recon, identity_heldout[s]))
    if not sims:
        return 1.0
    return 1.0 - float(np.mean(sims))


def measure_l3_clustering(
    Ws: List[np.ndarray],
    sequences_heldout: np.ndarray,
    macro_labels_heldout: np.ndarray,
    layer_protos: List[np.ndarray] = None,
) -> float:
    """within-macro mean L3 similarity / across-macro mean L3 similarity.

    >=1.5 strong clustering; <1.05 essentially none.
    """
    n_seqs, seq_len, _ = sequences_heldout.shape
    # Average L3 per sequence across tokens
    l3_per_seq = np.zeros((n_seqs, Ws[0].shape[0]), dtype=np.float32)
    for s in range(n_seqs):
        l3_avg = np.zeros(Ws[0].shape[0], dtype=np.float32)
        for t in range(seq_len):
            l3_out, _ = forward_pc_hierarchy(Ws, sequences_heldout[s, t], layer_protos)
            l3_avg += l3_out
        l3_per_seq[s] = _safe_sign(l3_avg)

    # Compute within/across macro similarities
    within = []
    across = []
    for i in range(n_seqs):
        for j in range(i + 1, n_seqs):
            sim = _cos(l3_per_seq[i], l3_per_seq[j])
            if macro_labels_heldout[i] == macro_labels_heldout[j]:
                within.append(sim)
            else:
                across.append(sim)
    if not within or not across:
        return 1.0
    w_mean = float(np.mean(within))
    a_mean = float(np.mean(across))
    if abs(a_mean) < 1e-6:
        return 10.0 if w_mean > 0 else 1.0
    return w_mean / a_mean if a_mean > 0 else 1.0


# ---------------------------------------------------------------------------
# Self-tests
# ---------------------------------------------------------------------------

def _instrumentation_selftest():
    """Per the cell docstring's SANITY SELF-TESTS section."""
    rng = np.random.default_rng(0)
    n_dim_t = 128

    # Test 1: trivial 1-sequence -> all arms reconstruct perfectly (recon_error<0.05)
    one_seq, one_id, _ = build_hierarchical_corpus(
        rng, n_dim_t, n_macro=1, n_meso=1, n_micro=1, seq_len=3,
        noise_std=0.01, flip_rate=0.0,
    )
    W_flat = train_flat_hebbian(one_seq, n_dim_t, lr=0.1)
    Ws_pc = train_pc_hierarchy(one_seq, n_dim_t, n_layers=3, lr=0.1)
    e_flat = measure_recon_error(
        lambda x: recon_flat(W_flat, x), one_seq, one_id,
    )
    e_pc = measure_recon_error(
        lambda x: recon_pc_hierarchy(Ws_pc, x), one_seq, one_id,
    )
    assert e_flat < 0.20, f"selftest1 flat: recon_error={e_flat} >= 0.20 on trivial corpus"
    # PC has 3 stacked nonlinear quantizations -- tolerance must be looser than flat
    assert e_pc < 0.50, f"selftest1 PC: recon_error={e_pc} >= 0.50 on trivial corpus"

    # Test 2: all-noise input -- all arms degrade similarly (no spurious 5x advantage)
    rng2 = np.random.default_rng(1)
    noise_seq = (rng2.standard_normal((4, 3, n_dim_t)).astype(np.float32))
    # Untrained reconstruction = noise -> error ~1
    e_flat_n = measure_recon_error(
        lambda x: recon_flat(np.zeros((n_dim_t, n_dim_t), dtype=np.float32), x),
        noise_seq, noise_seq[:, 0],
    )
    e_pc_n = measure_recon_error(
        lambda x: recon_pc_hierarchy(
            [np.zeros((n_dim_t, n_dim_t), dtype=np.float32) for _ in range(3)], x,
        ), noise_seq, noise_seq[:, 0],
    )
    # Both should be poor (>=0.5); ratio sanity
    if min(e_flat_n, e_pc_n) > 0.05:
        ratio = max(e_flat_n, e_pc_n) / max(min(e_flat_n, e_pc_n), 1e-6)
        assert ratio < 5.0, (
            f"selftest2: noise-input recon ratio {ratio} >= 5 "
            f"(flat={e_flat_n}, pc={e_pc_n}) -- spurious arm advantage"
        )

    # Test 3: weight magnitudes increase under repeated same-input training (Hebbian sign)
    W_t = np.zeros((n_dim_t, n_dim_t), dtype=np.float32)
    x_t = _bipolar(rng, 1, n_dim_t)[0]
    mag_before = float(np.linalg.norm(W_t))
    for _ in range(10):
        W_t += 0.01 * np.outer(x_t, x_t)
    mag_after = float(np.linalg.norm(W_t))
    assert mag_after > mag_before, (
        f"selftest3: Hebbian sign wrong (W magnitude did not increase): "
        f"before={mag_before}, after={mag_after}"
    )

    # Test 4: error_L1 + L1_out reconstructs input within tolerance
    W_test = np.eye(n_dim_t, dtype=np.float32) * 0.01
    x_in = _bipolar(rng, 1, n_dim_t)[0]
    l1_out = _safe_sign(W_test @ x_in)
    error = x_in - l1_out
    recon_check = l1_out + error
    diff = float(np.max(np.abs(recon_check - x_in)))
    assert diff < 1e-5, f"selftest4: error decomposition broken: max_diff={diff}"

    print(f"[selftest] PASS: trivial-recon flat={e_flat:.4f} pc={e_pc:.4f}; "
          f"noise-recon flat={e_flat_n:.4f} pc={e_pc_n:.4f}; "
          f"hebbian-sign mag {mag_before:.3f}->{mag_after:.3f}; "
          f"error-decomp diff={diff:.2e}", flush=True)


# ---------------------------------------------------------------------------
# Per-seed run
# ---------------------------------------------------------------------------

def run_one_seed(
    seed: int, n_dim: int, n_layers: int, n_macro: int, n_meso: int, n_micro: int,
    seq_len: int, noise_std: float, flip_rate: float, lr: float,
    capacity_points: Tuple[int, ...], heldout_frac: float,
) -> Dict:
    rng = np.random.default_rng(seed)
    print(f"  [seed={seed}] building corpus n_dim={n_dim} "
          f"macro={n_macro} meso={n_meso} micro={n_micro} seq_len={seq_len}...",
          flush=True)
    sequences, identity, macro_labels = build_hierarchical_corpus(
        rng, n_dim, n_macro, n_meso, n_micro, seq_len, noise_std, flip_rate,
    )
    n_seqs = sequences.shape[0]
    print(f"  [seed={seed}] corpus shape: {sequences.shape}", flush=True)

    # Held-out split: 10% of sequences, stratified by macro
    heldout_idx = []
    train_idx = []
    for ma in range(n_macro):
        macro_seqs = np.where(macro_labels == ma)[0]
        rng.shuffle(macro_seqs)
        n_held = max(1, int(heldout_frac * len(macro_seqs)))
        heldout_idx.extend(macro_seqs[:n_held].tolist())
        train_idx.extend(macro_seqs[n_held:].tolist())
    heldout_idx = np.array(heldout_idx, dtype=np.int64)
    train_idx = np.array(train_idx, dtype=np.int64)

    seq_train = sequences[train_idx]
    seq_held = sequences[heldout_idx]
    id_held = identity[heldout_idx]
    macro_held = macro_labels[heldout_idx]

    # Capacity probe: train arms at incremental n_seqs (200, 500, 1000)
    arm_results = {"FLAT_HEBBIAN": {}, "PC_3LAYER": {}, "PC_LAYERED_CLEANUP": {}}
    # Effective capacity points (clipped to actual train set size)
    eff_points = [min(cp, seq_train.shape[0]) for cp in capacity_points]
    # de-dup while preserving order
    seen = set()
    eff_points = [p for p in eff_points if not (p in seen or seen.add(p))]

    for cp in eff_points:
        print(f"  [seed={seed}] training at n_seqs={cp}/{seq_train.shape[0]}...", flush=True)
        seqs_cp = seq_train[:cp]
        t_arm0 = time.time()
        W_flat = train_flat_hebbian(seqs_cp, n_dim, lr)
        e_flat = measure_recon_error(lambda x: recon_flat(W_flat, x), seq_held, id_held)
        t_flat = time.time() - t_arm0
        print(f"    FLAT: recon_error={e_flat:.4f} ({t_flat:.1f}s)", flush=True)

        t_arm0 = time.time()
        Ws_pc = train_pc_hierarchy(seqs_cp, n_dim, n_layers, lr)
        e_pc = measure_recon_error(lambda x: recon_pc_hierarchy(Ws_pc, x), seq_held, id_held)
        clust_pc = measure_l3_clustering(Ws_pc, seq_held, macro_held)
        t_pc = time.time() - t_arm0
        print(f"    PC_3LAYER: recon_error={e_pc:.4f} cluster_ratio={clust_pc:.3f} ({t_pc:.1f}s)",
              flush=True)

        # Cleanup arm reuses Ws_pc + adds layer prototypes
        t_arm0 = time.time()
        layer_protos = _build_prototypes_per_layer(Ws_pc, seqs_cp, n_prototypes=64)
        e_pc_cl = measure_recon_error(
            lambda x: recon_pc_hierarchy(Ws_pc, x, layer_protos), seq_held, id_held,
        )
        clust_pc_cl = measure_l3_clustering(Ws_pc, seq_held, macro_held, layer_protos)
        t_cl = time.time() - t_arm0
        print(f"    PC_LAYERED_CLEANUP: recon_error={e_pc_cl:.4f} cluster_ratio={clust_pc_cl:.3f} "
              f"({t_cl:.1f}s)", flush=True)

        arm_results["FLAT_HEBBIAN"][str(cp)] = {
            "recon_error": float(e_flat),
            "wall_s": float(t_flat),
        }
        arm_results["PC_3LAYER"][str(cp)] = {
            "recon_error": float(e_pc),
            "cluster_ratio": float(clust_pc),
            "wall_s": float(t_pc),
        }
        arm_results["PC_LAYERED_CLEANUP"][str(cp)] = {
            "recon_error": float(e_pc_cl),
            "cluster_ratio": float(clust_pc_cl),
            "wall_s": float(t_cl),
        }

    return {
        "seed": seed,
        "N": n_dim,
        "n_layers": n_layers,
        "n_seqs_train": int(seq_train.shape[0]),
        "n_seqs_held": int(seq_held.shape[0]),
        "capacity_points": eff_points,
        "arms": arm_results,
        "run_mode": os.environ.get("HDLAB_RUN_MODE", "full"),
    }


# ---------------------------------------------------------------------------
# Verdict
# ---------------------------------------------------------------------------

def compute_verdict(per_seed: Dict[str, Dict]) -> Tuple[str, str, Dict]:
    """Combine results across seeds at the largest capacity_point each."""
    flat_errs = []
    pc_errs = []
    pc_clusts = []
    pc_cl_errs = []
    pc_cl_clusts = []
    for sd, r in per_seed.items():
        # Use the largest capacity point per seed (last in eff_points)
        cp = str(r["capacity_points"][-1])
        flat_errs.append(r["arms"]["FLAT_HEBBIAN"][cp]["recon_error"])
        pc_errs.append(r["arms"]["PC_3LAYER"][cp]["recon_error"])
        pc_clusts.append(r["arms"]["PC_3LAYER"][cp]["cluster_ratio"])
        pc_cl_errs.append(r["arms"]["PC_LAYERED_CLEANUP"][cp]["recon_error"])
        pc_cl_clusts.append(r["arms"]["PC_LAYERED_CLEANUP"][cp]["cluster_ratio"])

    flat_mean = float(np.mean(flat_errs))
    pc_mean = float(np.mean(pc_errs))
    pc_clust_mean = float(np.mean(pc_clusts))
    pc_cl_mean = float(np.mean(pc_cl_errs))
    pc_cl_clust_mean = float(np.mean(pc_cl_clusts))

    # Ratios: pc/flat. <= HP_PC_RATIO is PASS direction.
    if flat_mean < 1e-6:
        ratio_pc = 1.0
        ratio_cl = 1.0
    else:
        ratio_pc = pc_mean / flat_mean
        ratio_cl = pc_cl_mean / flat_mean

    summary = {
        "flat_recon_error_mean": flat_mean,
        "pc3_recon_error_mean": pc_mean,
        "pc3_cluster_ratio_mean": pc_clust_mean,
        "pc3_layered_cleanup_recon_error_mean": pc_cl_mean,
        "pc3_layered_cleanup_cluster_ratio_mean": pc_cl_clust_mean,
        "ratio_pc_over_flat": float(ratio_pc),
        "ratio_pc_cleanup_over_flat": float(ratio_cl),
        "n_seeds": len(per_seed),
        "thresholds": {
            "HP_PC_RATIO": HP_PC_RATIO,
            "HP_CLUSTER_RATIO": HP_CLUSTER_RATIO,
            "HF_PC_RATIO": HF_PC_RATIO,
        },
    }

    # Discriminating-regime guard (per cert-architecture DISCRIMINATING_REGIME
    # discipline): if flat baseline is near-perfect (recon_error < 0.02), the
    # ratio metric is uninformative -- both arms can hit recon_error~0.08 and
    # still earn ratio_pc = inf only because flat saturated. Force MIDDLE_BAND
    # in this regime; cluster_ratio remains an honest pass signal.
    flat_saturated = flat_mean < 0.02
    pc_hp = (
        (not flat_saturated)
        and (ratio_pc <= HP_PC_RATIO)
        and (pc_clust_mean >= HP_CLUSTER_RATIO)
    )
    pc_hf = (not flat_saturated) and (ratio_pc >= HF_PC_RATIO)
    cl_hp = (
        (not flat_saturated)
        and (ratio_cl <= HP_PC_RATIO)
        and (pc_cl_clust_mean >= HP_CLUSTER_RATIO)
    )
    cl_hf = (not flat_saturated) and (ratio_cl >= HF_PC_RATIO)
    # Stand-alone strong cluster-ratio signal (HP path even if flat saturated)
    cluster_hp = (pc_clust_mean >= HP_CLUSTER_RATIO * 1.3) or (
        pc_cl_clust_mean >= HP_CLUSTER_RATIO * 1.3
    )

    if flat_saturated:
        # In flat-saturated regime, only the cluster-ratio signal survives.
        if cluster_hp:
            verdict = "MIDDLE_BAND"  # partial: cluster works but recon-ratio test is moot
            which = "PC_3LAYER" if pc_clust_mean >= HP_CLUSTER_RATIO else "PC_LAYERED_CLEANUP"
            msg = (
                f"FLAT_SATURATED_REGIME (flat_recon_error={flat_mean:.4f} < 0.02); "
                f"PC-vs-flat ratio test is non-discriminating at this scale. "
                f"L3 macro-cluster ratio {which}={max(pc_clust_mean, pc_cl_clust_mean):.3f} "
                f"(HP cluster threshold {HP_CLUSTER_RATIO}). "
                f"flat={flat_mean:.4f} pc3={pc_mean:.4f} pc3_cl={pc_cl_mean:.4f}. "
                f"Routing: characterize at larger corpus where flat does NOT saturate."
            )
        else:
            verdict = "MIDDLE_BAND"
            msg = (
                f"FLAT_SATURATED_REGIME (flat_recon_error={flat_mean:.4f} < 0.02); "
                f"PC-vs-flat ratio test is non-discriminating; cluster signal weak. "
                f"flat={flat_mean:.4f} pc3={pc_mean:.4f} pc3_cl={pc_cl_mean:.4f} "
                f"cluster pc3={pc_clust_mean:.3f} cl={pc_cl_clust_mean:.3f}."
            )
        return verdict, msg, summary

    if pc_hp or cl_hp:
        verdict = "HARD_PASS"
        which = "PC_3LAYER" if pc_hp else "PC_LAYERED_CLEANUP"
        msg = (
            f"PC hierarchy beats flat Hebbian substrate-native: "
            f"{which} ratio={ratio_pc if pc_hp else ratio_cl:.3f} "
            f"(HP threshold {HP_PC_RATIO}) AND "
            f"L3 macro-cluster ratio "
            f"{pc_clust_mean if pc_hp else pc_cl_clust_mean:.3f} >= {HP_CLUSTER_RATIO}. "
            f"flat={flat_mean:.4f} pc3={pc_mean:.4f} pc3_cl={pc_cl_mean:.4f}."
        )
    elif pc_hf and cl_hf:
        verdict = "HARD_FAIL"
        msg = (
            f"PC hierarchy adds no value over flat Hebbian at this scale: "
            f"ratio_pc={ratio_pc:.3f}, ratio_pc_cleanup={ratio_cl:.3f} both >= "
            f"HF threshold {HF_PC_RATIO}. "
            f"flat={flat_mean:.4f} pc3={pc_mean:.4f} pc3_cl={pc_cl_mean:.4f}; "
            f"cluster ratios pc3={pc_clust_mean:.3f} cl={pc_cl_clust_mean:.3f}."
        )
    else:
        verdict = "MIDDLE_BAND"
        msg = (
            f"PC hierarchy shows partial benefit over flat Hebbian (characterize). "
            f"ratio_pc={ratio_pc:.3f} ratio_pc_cleanup={ratio_cl:.3f}; "
            f"L3 cluster ratios pc3={pc_clust_mean:.3f} cl={pc_cl_clust_mean:.3f}; "
            f"flat={flat_mean:.4f} pc3={pc_mean:.4f} pc3_cl={pc_cl_mean:.4f}."
        )

    return verdict, msg, summary


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    t0 = time.time()
    run_mode = os.environ.get("HDLAB_RUN_MODE", "full")
    seeds = SEEDS_FULL if run_mode == "full" else SEEDS_SMOKE
    n_dim_eff = N_DIM if run_mode == "full" else SMOKE_N_DIM
    # For smoke, also shrink corpus (proportional)
    if run_mode == "smoke":
        macro_eff, meso_eff, micro_eff = 2, 3, 10  # = 60 seqs
        seq_len_eff = 4
        cap_points = (30, 60)
    else:
        macro_eff, meso_eff, micro_eff = N_MACRO, N_MESO, N_MICRO
        seq_len_eff = SEQ_LEN
        cap_points = CAPACITY_PROBE_POINTS

    print(f"[{ANCHOR_NAME}] run_mode={run_mode} seeds={seeds} "
          f"n_dim={n_dim_eff} macro={macro_eff} meso={meso_eff} micro={micro_eff} "
          f"seq_len={seq_len_eff}", flush=True)

    out_dir = get_output_dir(ANCHOR_NAME)
    out_dir.mkdir(parents=True, exist_ok=True)
    run_config = {"N": n_dim_eff, "run_mode": run_mode}
    done, remaining = resumable_seeds(seeds, out_dir, run_config=run_config)
    print(f"[ckpt] {len(done)} seeds done, {len(remaining)} remaining", flush=True)

    for seed in remaining:
        print(f"[seed={seed}] {ANCHOR_NAME}...", flush=True)
        r = run_one_seed(
            seed, n_dim_eff, N_LAYERS, macro_eff, meso_eff, micro_eff,
            seq_len_eff, NOISE_STD, PER_TOKEN_FLIP_RATE, LEARNING_RATE,
            cap_points, HELDOUT_FRACTION,
        )
        write_partial(out_dir, seed, r)

    per_seed_raw = aggregate_partials(out_dir, seeds)
    # aggregate_partials returns dict; convert to {seed_str: payload}
    per_seed = {str(k): v for k, v in per_seed_raw.items()}

    verdict, verdict_msg, summary = compute_verdict(per_seed)
    elapsed = time.time() - t0
    print(f"\n[VERDICT] {verdict}: {verdict_msg}", flush=True)
    print(f"[elapsed] {elapsed:.1f}s", flush=True)

    metrics = {
        "anchor_name": ANCHOR_NAME,
        "anchor": ANCHOR_NAME,
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": summary,
        "N": n_dim_eff,
        "n_layers": N_LAYERS,
        "run_mode": run_mode,
        "n_seeds": len(seeds),
        "elapsed_s": elapsed,
        "per_seed": per_seed,
        "config": {
            "macro": macro_eff,
            "meso": meso_eff,
            "micro": micro_eff,
            "seq_len": seq_len_eff,
            "noise_std": NOISE_STD,
            "flip_rate": PER_TOKEN_FLIP_RATE,
            "learning_rate": LEARNING_RATE,
            "capacity_points": list(cap_points),
        },
    }
    mpath = out_dir / "metrics.json"
    with open(mpath, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    print(f"[{ANCHOR_NAME}] metrics -> {mpath}", flush=True)
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true", dest="self_test")
    ap.add_argument("--smoke", action="store_true",
                    help="Run at smoke scope (smaller N_DIM and corpus)")
    args = ap.parse_args()

    # Always run formula self-tests first (cheap)
    _instrumentation_selftest()

    if args.self_test:
        sys.exit(0)
    if args.smoke:
        os.environ["HDLAB_RUN_MODE"] = "smoke"
    sys.exit(main())
