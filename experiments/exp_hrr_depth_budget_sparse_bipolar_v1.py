"""hrr_depth_budget_sparse_bipolar_v1 -- sparse-bipolar bundle-capacity lift vs dense.

Verifies the sparse-bipolar drill's MAJOR claim (research_drill_sparse_bipolar_
depth_enc1_composition_2026-06-23.md): 20-300x bundle-capacity lift at f<=0.02
sparsity vs dense bipolar, using LCC-per-block bind (Frady-Kleyko-Sommer 2023
canonical involutive sparse-VSA bind).

Substrate-product reading: parent HRR depth drill identified bundle width M as
the real depth-budget bottleneck (sigma ~ 1/sqrt(M) per layer). CERT 592
already MEASURED 20-300x bundle-capacity lift at f<=0.02 N>=2048. This cell
composes those two findings directly: does sparse-bipolar bundle hold ~140-2100
items per bundle at N=4096 instead of the dense ~7-item ceiling?

DESIGN (5 arms x 5 M values x 3 seeds at N_DIM=4096):

  ARM_DENSE_f1.0    -- control; dense bipolar bundle (per-block conv, all active).
  ARM_SPARSE_f0.1   -- 10% sparse.
  ARM_SPARSE_f0.05  -- 5% sparse.
  ARM_SPARSE_f0.02  -- 2% sparse; predicted optimal per CERT 592.
  ARM_SPARSE_f0.01  -- 1% sparse; tests beyond predicted optimum.

  M_grid = [8, 32, 128, 512, 2048]
  seeds  = [7, 17, 23]
  V      = 256 (smoke uses 32)
  trials = 50 (smoke uses 5)

bind = LCC-per-block: divide N_DIM into B=64 blocks of N/B=64; per block apply
       circular convolution (FFT-conjugate) which is involutive on each block.
bundle = sum across M items then top-K-by-abs-value sign-quantize (k-sparse
         output preserves f-sparsity band).

Evaluation:
  For each (arm, M, seed, trial):
    1. Sample M random atoms a_1..a_M from V vocab.
    2. Bundle = topK_sparse(sum_i a_i)
    3. For each a_i in the bundle: query = a_i directly; pred = argmax_v cos(query, v)
       in V vocab; correct iff pred == i (recovered the bundled atom from cleanup
       against full V vocab when starting from the bundle as cue).

  Honest framing: this is "did the bundle preserve enough signal to recover each
  bundled item via cleanup". Recall@1 = mean over (i, trial) correct.

Note on bind: this cell focuses on BUNDLE capacity (the parent's identified
bottleneck) -- bind chain depth is tested separately in the parent HRR depth
drill. We expose LCC bind primitives for compositionality but the metric only
exercises bundle recall.

PRE-REG bands (preregs/2026-06-23_hrr_depth_budget_sparse_bipolar_v1.md):
  HARD_PASS = ARM_SPARSE_f0.02 @ M=128 recall_mean >= 0.80
              AND >= 20 * ARM_DENSE_f1.0 @ M=128 recall_mean
              AND cv <= 0.15
  HARD_FAIL = ARM_SPARSE_f0.02 @ M=128 recall_mean <= 2 * ARM_DENSE_f1.0 @ M=128
  MIDDLE    = lift in (2x, 20x) interval

SANITY: M=1 -> all arms recall = 1.0 (single item is trivial).

SUBSTRATE-ONLY: numpy; no torch; ASCII-only; no LLM at inference.
"""
from __future__ import annotations
import sys
import os
import argparse
import time
import signal
import atexit
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import (
    get_output_dir, write_partial_key, aggregate_partials, write_metrics,
)

ANCHOR_NAME = "hrr_depth_budget_sparse_bipolar_v1"

# Pre-reg HARD bands (sacrosanct)
HP_RECALL_THRESH = 0.80
HP_LIFT_RATIO = 20.0
HP_CV_MAX = 0.15
HF_LIFT_RATIO = 2.0
HP_M_POINT = 128

_P = argparse.ArgumentParser()
_P.add_argument("--self-test", action="store_true", dest="self_test")
_P.add_argument("--smoke", action="store_true")
_ARGS, _ = _P.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = "_smoke" in _HDLAB_EXP_NAME.lower()
RUN_MODE = "smoke" if (_ARGS.smoke or _ARGS.self_test or _NAME_SAYS_SMOKE) else os.environ.get("HDLAB_RUN_MODE", "full")

# Config
N_DIM = 4096
B_BLOCKS = 64
BLOCK_SIZE = N_DIM // B_BLOCKS  # 64

F_GRID = [1.0, 0.1, 0.05, 0.02, 0.01]
ARMS = ["ARM_DENSE_f1.0", "ARM_SPARSE_f0.1", "ARM_SPARSE_f0.05",
        "ARM_SPARSE_f0.02", "ARM_SPARSE_f0.01"]
ARM_TO_F = dict(zip(ARMS, F_GRID))

# M_GRID set after RUN_MODE so smoke can use a smaller grid (skip M=2048 to
# stay under 3min smoke timeout + keep V/M ratio >=4 for genuine selectivity).

if RUN_MODE == "full":
    SEEDS = [7, 17, 23]
    # V_VOCAB must be much larger than max(M_GRID)=2048 so the top-M cleanup
    # is a genuine discriminator (not trivially saturated when V <= M). Use
    # V = 4 * M_max for a real bundle-capacity test: at M=2048, top-2048 of
    # 8192 = picking the right quarter, hard if bundle saturated.
    V_VOCAB = 8192
    N_TRIALS = 30
    M_GRID = [8, 32, 128, 512, 2048]
else:
    SEEDS = [7]
    # Smoke must still exercise the M=128 HARD_PASS reference point with
    # genuine selectivity (V/M_max ratio >= 4). Smaller V + skip M=2048.
    V_VOCAB = 1024
    N_TRIALS = 5
    M_GRID = [8, 32, 128, 256]

CONFIG_VERSION = (
    "hrr_depth_budget_sparse_bipolar_v1; N_DIM=%d B=%d BLOCK=%d arms=%s "
    "f_grid=%s M_grid=%s seeds=%s V=%d trials=%d mode=%s; "
    "bands HP_recall>=%.2f @M=%d HP_lift>=%.1fx HP_cv<=%.2f HF_lift<=%.1fx"
) % (N_DIM, B_BLOCKS, BLOCK_SIZE, ARMS, F_GRID, M_GRID, SEEDS, V_VOCAB,
     N_TRIALS, RUN_MODE,
     HP_RECALL_THRESH, HP_M_POINT, HP_LIFT_RATIO, HP_CV_MAX, HF_LIFT_RATIO)


# ============================================================================
# Substrate primitives: sparse-bipolar atom + LCC-per-block bind + sparse bundle
# ============================================================================

def make_sparse_bipolar_atom(rng: np.random.Generator, n_dim: int, f: float) -> np.ndarray:
    """K-sparse bipolar atom: K = max(1, round(f*N)) nonzero positions in {-1,+1}.

    For f=1.0 (dense), all positions are bipolar (no zeros).
    Returns float32 array shape (n_dim,).
    """
    out = np.zeros(n_dim, dtype=np.float32)
    if f >= 1.0:
        # Dense bipolar
        s = rng.integers(0, 2, size=n_dim, dtype=np.int8) * 2 - 1
        out[:] = s.astype(np.float32)
        return out
    k = max(1, int(round(f * n_dim)))
    idx = rng.choice(n_dim, size=k, replace=False)
    vals = rng.integers(0, 2, size=k, dtype=np.int8) * 2 - 1
    out[idx] = vals.astype(np.float32)
    return out


def make_vocab(seed: int, n_dim: int, f: float, v_size: int) -> np.ndarray:
    """V vocab of K-sparse bipolar atoms; shape (v_size, n_dim)."""
    rng = np.random.default_rng(seed * 991 + int(f * 1e6) + 17)
    V = np.zeros((v_size, n_dim), dtype=np.float32)
    for i in range(v_size):
        V[i] = make_sparse_bipolar_atom(rng, n_dim, f)
    return V


def lcc_block_bind(a: np.ndarray, b: np.ndarray, b_blocks: int = B_BLOCKS) -> np.ndarray:
    """LCC-per-block bind: per-block circular convolution (Frady-Kleyko-Sommer 2023).

    Involutive when paired with circular correlation per block (unbind below).
    Operates on the BLOCK structure of the vectors; preserves block-locality.
    """
    n = a.shape[0]
    block_size = n // b_blocks
    a2 = a.reshape(b_blocks, block_size)
    b2 = b.reshape(b_blocks, block_size)
    # Per-block circular convolution via FFT
    A = np.fft.fft(a2, axis=1)
    B = np.fft.fft(b2, axis=1)
    C = A * B
    out = np.real(np.fft.ifft(C, axis=1)).astype(np.float32)
    return out.reshape(n)


def lcc_block_unbind(c: np.ndarray, b: np.ndarray, b_blocks: int = B_BLOCKS,
                     eps: float = 1e-8) -> np.ndarray:
    """LCC-per-block unbind: per-block Fourier-domain pseudoinverse of bind.

    bind(a, b) then unbind(., b) -> a (exactly involutive for nonzero-spectrum
    blocks; FFT pseudoinverse for safety).
    """
    n = c.shape[0]
    block_size = n // b_blocks
    c2 = c.reshape(b_blocks, block_size)
    b2 = b.reshape(b_blocks, block_size)
    C = np.fft.fft(c2, axis=1)
    B = np.fft.fft(b2, axis=1)
    # Per-block Fourier pseudoinverse: A = C / B (with eps regularization)
    B_safe = np.where(np.abs(B) < eps, eps, B)
    A = C / B_safe
    out = np.real(np.fft.ifft(A, axis=1)).astype(np.float32)
    return out.reshape(n)


def sparse_bundle(items: np.ndarray, f: float, n_dim: int) -> np.ndarray:
    """Bundle K-sparse bipolar atoms.

    items: shape (M, N) of K-sparse bipolar atoms.
    f: target sparsity for the bundled output (matches arm's f).

    Method: sum across M; keep top-K_total positions by absolute value; sign
    quantize within active positions, zero elsewhere. K_total = max(K, round(f*N))
    where K is the per-atom sparsity budget. This preserves the K-sparse band.

    For dense (f=1.0), keeps all N positions and sign-quantizes.
    """
    if items.shape[0] == 0:
        return np.zeros(n_dim, dtype=np.float32)
    s = items.sum(axis=0)
    if f >= 1.0:
        out = np.sign(s).astype(np.float32)
        out[out == 0] = 1.0
        return out
    k_total = max(1, int(round(f * n_dim)))
    abs_s = np.abs(s)
    # top-k positions by abs value
    if k_total >= n_dim:
        idx = np.arange(n_dim)
    else:
        idx = np.argpartition(abs_s, -k_total)[-k_total:]
    out = np.zeros(n_dim, dtype=np.float32)
    out[idx] = np.sign(s[idx]).astype(np.float32)
    # Handle any sign==0 within active positions -> +1
    out[idx] = np.where(out[idx] == 0, 1.0, out[idx])
    return out


def cleanup_argmax(query: np.ndarray, vocab: np.ndarray) -> int:
    """Cosine-argmax over vocab. Returns index of nearest vocab atom."""
    # cos(q, v_i) proportional to q @ v_i (for non-zero norms); but since both
    # q and v_i are k-sparse bipolar with same K, q @ v_i / (||q|| * ||v_i||)
    # = (q @ v_i) / K when both have K active positions. We just argmax q @ V.T.
    # For dense f=1.0, ||v_i|| = sqrt(N) for all i, so same.
    sims = vocab @ query
    return int(np.argmax(sims))


# ============================================================================
# Per-(arm, M) bundle-recall trial
# ============================================================================

def bundle_recall_for(arm: str, M: int, vocab: np.ndarray, n_trials: int,
                      seed: int, n_dim: int) -> float:
    """Mean recall@1 over n_trials of bundling M random atoms + recovering each."""
    f = ARM_TO_F[arm]
    V_size = vocab.shape[0]
    rng = np.random.default_rng(seed * 1009 + int(f * 1e6) + M * 31)
    correct = 0
    total = 0
    for _trial in range(n_trials):
        # Sample M atoms (with replacement if M > V_size; else without)
        if M <= V_size:
            idx = rng.choice(V_size, size=M, replace=False)
        else:
            idx = rng.choice(V_size, size=M, replace=True)
        items = vocab[idx]  # (M, N)
        bundled = sparse_bundle(items, f, n_dim)  # (N,)
        # For each bundled item, query = the original atom; cleanup against V.
        # Recall: does the bundle "remember" each item -> nearest neighbor in V
        # of (item + bundle perturbation) lands on the right vocab id?
        # Standard bundle-recall: query is the bundle itself looking for items;
        # but a single bundle can't decode all M items via top-1 against V.
        # Honest bundle recall: for each bundled item i, query the bundle for
        # similarity with each vocab atom; an item is "recovered" iff that
        # vocab atom is in the top-M nearest neighbors of the bundle.
        # We use top-M cleanup: bundle is correct on item i iff vocab[idx[i]]
        # is among the top-M nearest vocab atoms to bundle.
        sims = vocab @ bundled  # (V,)
        if M >= V_size:
            top_m = set(range(V_size))
        else:
            top_m_idx = np.argpartition(sims, -M)[-M:]
            top_m = set(top_m_idx.tolist())
        for original_idx in idx:
            if int(original_idx) in top_m:
                correct += 1
            total += 1
    return float(correct) / float(max(total, 1))


# ============================================================================
# Per-seed unit
# ============================================================================

def run_unit(seed: int) -> Dict:
    t0 = time.time()
    by_arm = {}
    for arm in ARMS:
        f = ARM_TO_F[arm]
        t_arm = time.time()
        # Build vocab once per arm (one f, one seed)
        vocab = make_vocab(seed, N_DIM, f, V_VOCAB)
        m_results = {}
        for M in M_GRID:
            recall = bundle_recall_for(arm, M, vocab, N_TRIALS, seed, N_DIM)
            m_results["M%d" % M] = {"recall_mean": round(recall, 4)}
        wall = time.time() - t_arm
        by_arm[arm] = {
            "f": f,
            "M_results": m_results,
            "wall_s": round(wall, 2),
        }
        print("  [seed=%d arm=%s] f=%.3f wall=%.1fs recall@M=%s" % (
            seed, arm, f, wall,
            ",".join("M%d:%.2f" % (M, m_results["M%d" % M]["recall_mean"]) for M in M_GRID)
        ), flush=True)
    return {
        "seed": seed,
        "by_arm": by_arm,
        "N_DIM": N_DIM,
        "V_VOCAB": V_VOCAB,
        "N_TRIALS": N_TRIALS,
        "M_GRID": M_GRID,
        "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
        "elapsed_s_seed": round(time.time() - t0, 2),
    }


# ============================================================================
# Verdict
# ============================================================================

def compute_verdict(units):
    if not units:
        return ("HARD_FAIL", "no results", {})

    # Aggregate across seeds: by_arm_agg[arm].M{M} = {recall_mean, recall_std, recall_cv}
    arms = list(units[0]["by_arm"].keys())
    by_arm_agg = {}
    for arm in arms:
        m_agg = {}
        for M in M_GRID:
            recalls = [u["by_arm"][arm]["M_results"]["M%d" % M]["recall_mean"] for u in units]
            r_mean = float(np.mean(recalls))
            r_std = float(np.std(recalls))
            r_cv = r_std / max(abs(r_mean), 1e-6)
            m_agg["M%d" % M] = {
                "recall_mean": round(r_mean, 4),
                "recall_std": round(r_std, 4),
                "recall_cv": round(r_cv, 4),
                "recall_per_seed": [round(r, 4) for r in recalls],
            }
        by_arm_agg[arm] = {"f": ARM_TO_F[arm], "M_results": m_agg}

    # Discriminator: sparse_f0.02 vs dense_f1.0 at M=HP_M_POINT
    sparse_arm = "ARM_SPARSE_f0.02"
    dense_arm = "ARM_DENSE_f1.0"
    m_key = "M%d" % HP_M_POINT
    sp_recall = by_arm_agg[sparse_arm]["M_results"][m_key]["recall_mean"]
    sp_cv = by_arm_agg[sparse_arm]["M_results"][m_key]["recall_cv"]
    dn_recall = by_arm_agg[dense_arm]["M_results"][m_key]["recall_mean"]
    lift_ratio = sp_recall / max(dn_recall, 1e-6)

    # Compute lifts at all M points for visibility
    lifts_by_M = {}
    for M in M_GRID:
        mk = "M%d" % M
        sp = by_arm_agg[sparse_arm]["M_results"][mk]["recall_mean"]
        dn = by_arm_agg[dense_arm]["M_results"][mk]["recall_mean"]
        lifts_by_M[mk] = round(sp / max(dn, 1e-6), 3)

    detail = {
        "by_arm_agg": by_arm_agg,
        "HP_M_point": HP_M_POINT,
        "sparse_f0_02_recall_at_HP_M": round(sp_recall, 4),
        "sparse_f0_02_cv_at_HP_M": round(sp_cv, 4),
        "dense_recall_at_HP_M": round(dn_recall, 4),
        "lift_ratio_sparse_f0_02_vs_dense_at_HP_M": round(lift_ratio, 3),
        "lifts_sparse_f0_02_vs_dense_by_M": lifts_by_M,
        "n_seeds": len(units),
        "CONFIG_VERSION": CONFIG_VERSION,
        "honest_scope": (
            "Substrate-native sparse-bipolar bundle-capacity test: 5 arms x 5 M "
            "values x %d seeds at N_DIM=%d V=%d trials=%d; LCC-per-block bind "
            "primitive shipped but metric exercises BUNDLE recall (parent's "
            "identified bottleneck); HARD_PASS = ARM_SPARSE_f0.02 @ M=%d recall "
            ">=%.2f AND >=%.1fx lift over dense AND cv<=%.2f; HARD_FAIL = lift "
            "<=%.1fx (sparse claim refuted)." % (
                len(units), N_DIM, V_VOCAB, N_TRIALS, HP_M_POINT,
                HP_RECALL_THRESH, HP_LIFT_RATIO, HP_CV_MAX, HF_LIFT_RATIO)),
        "cites": [
            "preregs/2026-06-23_hrr_depth_budget_sparse_bipolar_v1.md",
            "notes/research_drill_sparse_bipolar_depth_enc1_composition_2026-06-23.md",
            "notes/exp_dev_handoff_research_drill_sparse_bipolar_depth_enc1_composition_2026-06-23.md",
            "data/exp_sparse_boundary_v2_cpu_v1/metrics.json (CERT 592 measurement)",
            "Frady-Kleyko-Sommer 2023 PMC12180425 (LCC-per-block bind)",
        ],
    }

    # Verdict classification per pre-reg
    if (sp_recall >= HP_RECALL_THRESH
            and lift_ratio >= HP_LIFT_RATIO
            and sp_cv <= HP_CV_MAX):
        msg = (
            "HRR_BUNDLE_SPARSE HARD_PASS: ARM_SPARSE_f0.02 @ M=%d recall=%.3f "
            "(>=%.2f) AND lift=%.1fx over dense (>=%.0fx) AND cv=%.3f (<=%.2f); "
            "substrate-native sparse-bipolar bundle delivers ~%.0fx capacity "
            "headroom at f=0.02 vs dense bipolar bundle at same M; unbottlenecks "
            "parent HRR depth drill's bundle-width sigma~1/sqrt(M) ceiling; "
            "chain-grade-eligible substrate-native compression primitive. "
            "Lifts by M: %s" % (
                HP_M_POINT, sp_recall, HP_RECALL_THRESH, lift_ratio,
                HP_LIFT_RATIO, sp_cv, HP_CV_MAX, lift_ratio, lifts_by_M)
        )
        return ("HARD_PASS", msg, detail)

    if lift_ratio <= HF_LIFT_RATIO:
        msg = (
            "HRR_BUNDLE_SPARSE HARD_FAIL: ARM_SPARSE_f0.02 @ M=%d lift=%.2fx "
            "over dense (<=%.1fx threshold); sparse-bipolar bundle does NOT "
            "lift bundle-width capacity at the HARD_PASS discriminator point; "
            "bundle-width bottleneck remains intrinsic at this f/M/N regime. "
            "sp_recall=%.3f dn_recall=%.3f. Lifts by M: %s" % (
                HP_M_POINT, lift_ratio, HF_LIFT_RATIO, sp_recall, dn_recall,
                lifts_by_M)
        )
        return ("HARD_FAIL", msg, detail)

    msg = (
        "HRR_BUNDLE_SPARSE MIDDLE_BAND: ARM_SPARSE_f0.02 @ M=%d lift=%.2fx "
        "(>2x but <20x threshold); partial sparse lift, characterize via M-sweep. "
        "sp_recall=%.3f sp_cv=%.3f dn_recall=%.3f. Lifts by M: %s" % (
            HP_M_POINT, lift_ratio, sp_recall, sp_cv, dn_recall, lifts_by_M)
    )
    return ("MIDDLE_BAND", msg, detail)


# ============================================================================
# atexit synthesizer (partial-rescue)
# ============================================================================
_METRICS_WRITTEN = [False]
_OUT_DIR_REF = [None]
_T0_REF = [None]


def _synthesize_on_exit():
    if _METRICS_WRITTEN[0]:
        return
    out_dir = _OUT_DIR_REF[0]
    if out_dir is None or not out_dir.exists():
        return
    try:
        partials = aggregate_partials(out_dir, ["s%d" % sd for sd in SEEDS])
        units = list(partials.values())
        if not units:
            return
        try:
            verdict, msg, detail = compute_verdict(units)
        except Exception as e:
            verdict, msg, detail = ("PARTIAL_TIMEOUT",
                                    "atexit synthesize: compute_verdict failed: %s" % e,
                                    {"n_seeds_recovered": len(units)})
        metrics = {
            "anchor_name": ANCHOR_NAME,
            "verdict": ("TIMEOUT_PARTIAL_NSEEDS_%d" % len(units)) if verdict != "PARTIAL_TIMEOUT" else verdict,
            "verdict_msg": "[atexit-synthesize] " + msg,
            "run_mode": RUN_MODE,
            "N_DIM": N_DIM,
            "n_seeds": len(units),
            "n_seeds_expected": len(SEEDS),
            "detail": detail,
            "metrics_source": "atexit_synthesize_partial_hrr_depth_budget_sparse_bipolar_v1",
            "per_unit": units,
            "elapsed_s": (time.time() - _T0_REF[0]) if _T0_REF[0] else 0.0,
            "summary": "[atexit-synthesize from %d/%d partials] %s" % (len(units), len(SEEDS), msg),
            "substrate_only_decode_gate": "TRUE",
            "zero_llm_calls_at_inference": True,
            "_synthesized_by_atexit": True,
        }
        write_metrics(out_dir, metrics, units)
        _METRICS_WRITTEN[0] = True
        sys.stderr.write("[atexit] synthesized metrics.json from %d/%d partials\n" % (
            len(units), len(SEEDS)))
        sys.stderr.flush()
    except Exception as e:
        sys.stderr.write("[atexit] synthesize failed: %s\n" % e)
        sys.stderr.flush()


# ============================================================================
# Self-test (mechanism + sanity + verdict-shape)
# ============================================================================

def _selftest():
    rng = np.random.default_rng(0)

    # T1: LCC-per-block bind involutive (real-valued; bind then unbind == identity)
    n_test = 256
    b_test = 8
    a = rng.standard_normal(n_test).astype(np.float32)
    b = rng.standard_normal(n_test).astype(np.float32)
    ab = lcc_block_bind(a, b, b_blocks=b_test)
    a_rec = lcc_block_unbind(ab, b, b_blocks=b_test)
    assert np.allclose(a, a_rec, atol=1e-4), \
        "T1 LCC bind/unbind not involutive: max diff %s" % float(np.max(np.abs(a - a_rec)))

    # T2: make_sparse_bipolar_atom respects K
    for f in [1.0, 0.1, 0.02]:
        v = make_sparse_bipolar_atom(rng, n_test, f)
        k_expected = max(1, int(round(f * n_test))) if f < 1.0 else n_test
        k_actual = int(np.count_nonzero(v))
        assert k_actual == k_expected, \
            "T2 sparse atom f=%.3f K_actual=%d expected=%d" % (f, k_actual, k_expected)
        # Bipolar in active positions
        active = v[v != 0]
        assert set(np.unique(active).tolist()).issubset({-1.0, 1.0}), \
            "T2 sparse atom not bipolar in active: %s" % np.unique(active)

    # T3: sparse_bundle keeps K-sparse band
    items = np.stack([make_sparse_bipolar_atom(rng, n_test, 0.1) for _ in range(5)])
    bun = sparse_bundle(items, 0.1, n_test)
    k_expected = max(1, int(round(0.1 * n_test)))
    k_actual = int(np.count_nonzero(bun))
    assert k_actual == k_expected, \
        "T3 sparse_bundle K_actual=%d expected=%d" % (k_actual, k_expected)
    active = bun[bun != 0]
    assert set(np.unique(active).tolist()).issubset({-1.0, 1.0}), \
        "T3 bundle not bipolar in active: %s" % np.unique(active)

    # T4: cleanup_argmax recovers self
    V = np.stack([make_sparse_bipolar_atom(rng, n_test, 0.1) for _ in range(8)])
    for i in range(8):
        pred = cleanup_argmax(V[i], V)
        assert pred == i, "T4 cleanup_argmax did not recover self at i=%d (got %d)" % (i, pred)

    # T5: at M=1, recall=1.0 for every f (single item is trivial via cleanup
    # — the bundle is the item itself + maybe re-quantized; nearest neighbor
    # in V is the item itself when item is in V)
    for f in [1.0, 0.1, 0.02]:
        rng_local = np.random.default_rng(7)
        V_local = np.stack([make_sparse_bipolar_atom(rng_local, n_test, f) for _ in range(8)])
        # Mimic bundle_recall_for at M=1 directly
        target_idx = 3
        items = V_local[[target_idx]]
        bun = sparse_bundle(items, f, n_test)
        sims = V_local @ bun
        top_m_idx = set(np.argpartition(sims, -1)[-1:].tolist())
        assert target_idx in top_m_idx, "T5 M=1 recall failed at f=%.2f" % f

    # T6: verdict-shape sanity (synthetic units)
    def _mk_unit(recalls_per_arm_per_M):
        """recalls_per_arm_per_M: dict[arm][M_int] -> recall_mean."""
        ba = {}
        for arm in ARMS:
            mr = {}
            for M in M_GRID:
                mr["M%d" % M] = {"recall_mean": recalls_per_arm_per_M[arm][M]}
            ba[arm] = {"f": ARM_TO_F[arm], "M_results": mr, "wall_s": 0.0}
        return {"seed": 0, "by_arm": ba, "N_DIM": N_DIM, "V_VOCAB": V_VOCAB,
                "N_TRIALS": N_TRIALS, "M_GRID": M_GRID, "run_mode": "smoke",
                "config_version": "selftest", "elapsed_s_seed": 0.01}

    # Synth units must use the live M_GRID (varies by RUN_MODE). Pick recall
    # values per arm, then expand to a dict keyed by the active M_GRID using
    # the M=128 HARD_PASS point as the discriminator.
    def _expand(per_arm_at_128: Dict[str, float], dense_factor_at_M: Dict[int, float],
                sparse_factor_at_M: Dict[int, float]) -> Dict[str, Dict[int, float]]:
        out = {}
        for arm in ARMS:
            base = per_arm_at_128[arm]
            row = {}
            for M in M_GRID:
                if arm == "ARM_DENSE_f1.0":
                    row[M] = base * dense_factor_at_M.get(M, 1.0)
                else:
                    row[M] = base * sparse_factor_at_M.get(M, 1.0)
            out[arm] = row
        return out

    # M-shape factors are illustrative; the verdict only checks M=128.
    dense_shape = {M: 1.0 for M in M_GRID}
    sparse_shape = {M: 1.0 for M in M_GRID}

    # T6a HARD_PASS: f=0.02 @ M=128 = 0.90, dense = 0.04 (lift 22.5x)
    hp_per_arm_128 = {
        "ARM_DENSE_f1.0":   0.04,
        "ARM_SPARSE_f0.1":  0.40,
        "ARM_SPARSE_f0.05": 0.70,
        "ARM_SPARSE_f0.02": 0.90,
        "ARM_SPARSE_f0.01": 0.92,
    }
    u_hp = _mk_unit(_expand(hp_per_arm_128, dense_shape, sparse_shape))
    v, m, d = compute_verdict([u_hp, u_hp, u_hp])
    assert v == "HARD_PASS", "T6a HARD_PASS expected, got %s msg=%s" % (v, m[:200])

    # T6b HARD_FAIL: sparse barely beats dense (lift <2x)
    hf_per_arm_128 = {
        "ARM_DENSE_f1.0":   0.04,
        "ARM_SPARSE_f0.1":  0.06,
        "ARM_SPARSE_f0.05": 0.07,
        "ARM_SPARSE_f0.02": 0.07,
        "ARM_SPARSE_f0.01": 0.07,
    }
    u_hf = _mk_unit(_expand(hf_per_arm_128, dense_shape, sparse_shape))
    v, m, d = compute_verdict([u_hf, u_hf, u_hf])
    assert v == "HARD_FAIL", "T6b HARD_FAIL expected, got %s msg=%s" % (v, m[:200])

    # T6c MIDDLE: lift in (2x, 20x)
    mid_per_arm_128 = {
        "ARM_DENSE_f1.0":   0.10,
        "ARM_SPARSE_f0.1":  0.30,
        "ARM_SPARSE_f0.05": 0.40,
        "ARM_SPARSE_f0.02": 0.50,
        "ARM_SPARSE_f0.01": 0.50,
    }
    u_mid = _mk_unit(_expand(mid_per_arm_128, dense_shape, sparse_shape))
    v, m, d = compute_verdict([u_mid, u_mid, u_mid])
    assert v == "MIDDLE_BAND", "T6c MIDDLE expected, got %s msg=%s" % (v, m[:200])

    # T7: integration smoke at small N to verify run_unit shape (1 seed, small V/trials)
    # No actual run -- just verify config plumbs through.
    assert N_DIM % B_BLOCKS == 0, "T7 N_DIM not divisible by B_BLOCKS"

    print("[selftest] PASS: T1 LCC bind involutive + T2 sparse atom K-band + "
          "T3 sparse bundle K-band + T4 cleanup self-recover + T5 M=1 trivial + "
          "T6 verdict bands (HP, HF, MID) + T7 config divisibility OK", flush=True)


if __name__ == "__main__":
    _selftest()
    if _ARGS.self_test:
        raise SystemExit(0)
    print("[config] %s mode=%s N_DIM=%d arms=%s f=%s M=%s seeds=%s V=%d trials=%d | %s" % (
        ANCHOR_NAME, RUN_MODE, N_DIM, ARMS, F_GRID, M_GRID, SEEDS, V_VOCAB,
        N_TRIALS, CONFIG_VERSION), flush=True)
    out_dir = get_output_dir(ANCHOR_NAME)
    _OUT_DIR_REF[0] = out_dir
    atexit.register(_synthesize_on_exit)
    try:
        signal.signal(signal.SIGTERM, lambda *a: (_synthesize_on_exit(), sys.exit(143)))
    except (ValueError, AttributeError):
        pass
    run_cfg = {"run_mode": RUN_MODE, "N": N_DIM, "V": V_VOCAB,
               "schema": "hrr-depth-budget-sparse-bipolar-v1"}
    t0 = time.time()
    _T0_REF[0] = t0
    for seed in SEEDS:
        key = "s%d" % seed
        if key in aggregate_partials(out_dir, [key], run_config=run_cfg):
            print("[ckpt] %s done; skip" % key, flush=True)
            continue
        write_partial_key(out_dir, key, run_unit(seed))
    units = list(aggregate_partials(out_dir, ["s%d" % sd for sd in SEEDS], run_config=run_cfg).values())
    verdict, msg, detail = compute_verdict(units)
    print("\n[VERDICT] " + msg, flush=True)
    metrics = {
        "anchor_name": ANCHOR_NAME,
        "verdict": verdict,
        "verdict_msg": msg,
        "run_mode": RUN_MODE,
        "N_DIM": N_DIM,
        "V_VOCAB": V_VOCAB,
        "N_TRIALS": N_TRIALS,
        "M_GRID": M_GRID,
        "F_GRID": F_GRID,
        "n_seeds": len(SEEDS),
        "detail": detail,
        "metrics_source": "measured_cpu_hrr_depth_budget_sparse_bipolar_v1",
        "per_unit": units,
        "elapsed_s": time.time() - t0,
        "summary": msg,
        "substrate_only_decode_gate": "TRUE (substrate-native sparse-bipolar + LCC-per-block bind; numpy only; zero LLM at inference)",
        "zero_llm_calls_at_inference": True,
        "_name_says_smoke_workaround": _NAME_SAYS_SMOKE,
    }
    write_metrics(out_dir, metrics, units)
    _METRICS_WRITTEN[0] = True
    print("[metrics] written to %s" % (out_dir / "metrics.json"), flush=True)
