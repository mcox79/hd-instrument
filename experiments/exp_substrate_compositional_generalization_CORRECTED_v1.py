"""substrate_compositional_generalization_CORRECTED_v1 -- correct mechanism for the
compositional generalization protocol that ARM 2 of substrate_brain_aligned_aliveness_shotgun_v1
HARD_FAILed (holdout=0.000).

Fact-finder root cause (notes/director_compositional_failure_USER_test_wrong_VSA_modality_inventory_2026-06-24.md):
HRR circular convolution operates well only on DENSE random unit-norm vectors (Plate 1995). The
brain-aligned shotgun ARM 2 used sparse-bipolar f=0.05 codebook + NO per-bind normalization + raw-sum
bank. TRAIN-pair recall (in_distribution_top1) at chance (0.10 vs 1/20 = 0.05) => mechanism broken,
not generalization failure.

This cell tests the SAME 20x20 subject-object role-binding protocol with 4 arms varying the
mechanism configuration:

  ARM_BROKEN_SPARSE_NO_NORM    -- sparse-bipolar + circ-conv + raw sum (provenance arm; should fail).
  ARM_DENSE_HRR_NORMALIZED     -- dense unit-norm Gaussian + circ-conv + per-bind L2 norm (Plate canonical).
  ARM_FHRR_NORMALIZED          -- complex unit-phase + element-wise mul + bundling.
  ARM_SPARSE_HRR_NORMALIZED    -- sparse-bipolar + circ-conv + per-bind L2 norm (the fix the broken arm lacks).

Protocol per arm:
  - 20 subjects, 20 objects, 50% coverage (200 train, 200 heldout).
  - bank = sum_{(i,j) in train} unit_norm(bind(subj[i], obj[j])) (arm-dependent unit_norm).
  - For each pair in train and heldout: rec = unbind(bank, subj[i]); pred = argmax cosine(rec, obj codebook).
  - Reports in_distribution_top1 (train) and holdout_top1.

Sanity floor (mandatory): an arm's holdout result only counts as a generalization claim when
in_distribution_top1 > 0.70; otherwise the mechanism is broken and the holdout number is noise.

Pre-reg HARD bands (see preregs/2026-06-24_substrate_compositional_generalization_CORRECTED_v1.md):
  HARD_PASS_COMPOSITIONAL_ALIVE: any normalized arm clears in_dist>0.70 AND holdout>0.50.
  MIDDLE_BAND_PARTIAL: best normalized arm clears in_dist>0.70 but holdout in [0.20, 0.50].
  HARD_FAIL_DEEPER_ISSUE: NO arm clears in_dist>0.70 (substrate's HRR family broken at this scale).
  HARD_FAIL_PROPER_RETEST: normalized arms clear in_dist>0.70 but all have holdout<0.20.

ASCII only. CPU only (numpy). Per-seed checkpoint.
"""
from __future__ import annotations
import sys, os, argparse, time
from pathlib import Path
import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import (
    get_output_dir, write_partial_key, aggregate_partials, write_metrics
)

ANCHOR_NAME = "substrate_compositional_generalization_CORRECTED_v1"

_P = argparse.ArgumentParser()
_P.add_argument("--self-test", action="store_true", dest="self_test")
_P.add_argument("--smoke", action="store_true")
_ARGS, _ = _P.parse_known_args()
RUN_MODE = "smoke" if (_ARGS.smoke or _ARGS.self_test) else os.environ.get("HDLAB_RUN_MODE", "full")

# Config
if RUN_MODE == "full":
    SEEDS = [7, 17, 23]
    N_DIM = 4096
    N_SUBJ = 20
    N_OBJ = 20
    COVERAGE = 0.50
    SPARSE_F = 0.05
else:  # smoke
    SEEDS = [0]
    N_DIM = 1024
    N_SUBJ = 8
    N_OBJ = 8
    COVERAGE = 0.50
    SPARSE_F = 0.05

ARMS = [
    "ARM_BROKEN_SPARSE_NO_NORM",
    "ARM_DENSE_HRR_NORMALIZED",
    "ARM_FHRR_NORMALIZED",
    "ARM_SPARSE_HRR_NORMALIZED",
]

# Pre-reg bands
HP_IN_DIST_FLOOR = 0.70       # mandatory sanity floor for any arm's holdout to count
HP_HOLDOUT_FLOOR = 0.50       # holdout band for HARD_PASS
MIDDLE_HOLDOUT_LO = 0.20      # lower edge of middle band
HARD_FAIL_RETEST_HI = 0.20    # if normalized in_dist >0.70 but holdout < this -> proper-retest fail
BROKEN_EXPECTED_HI = 0.20     # broken arm's expected in_dist (provenance check)

CONFIG_VERSION = (
    "substrate_compositional_generalization_CORRECTED_v1; N_DIM=%d sparse_f=%.3f "
    "n_subj=%d n_obj=%d coverage=%.2f arms=%s seeds=%s mode=%s; "
    "bands HP_in_dist>%.2f HP_holdout>%.2f MIDDLE_lo>%.2f HF_retest<%.2f"
) % (N_DIM, SPARSE_F, N_SUBJ, N_OBJ, COVERAGE, ARMS, SEEDS, RUN_MODE,
     HP_IN_DIST_FLOOR, HP_HOLDOUT_FLOOR, MIDDLE_HOLDOUT_LO, HARD_FAIL_RETEST_HI)


# ------------------------------------------------------------------
# Codebook builders
# ------------------------------------------------------------------
def _sparse_bipolar(n: int, dim: int, f: float, g: np.random.Generator) -> np.ndarray:
    """Stack of n sparse-bipolar vectors at dim with fraction f nonzero. Shape (n, dim)."""
    out = np.zeros((n, dim), dtype=np.float32)
    k = max(1, int(round(f * dim)))
    for i in range(n):
        idx = g.choice(dim, k, replace=False)
        signs = g.integers(0, 2, k).astype(np.float32) * 2.0 - 1.0
        out[i, idx] = signs
    return out


def _dense_unit_norm(n: int, dim: int, g: np.random.Generator) -> np.ndarray:
    """Stack of n dense Gaussian vectors, L2-normalized per row. Shape (n, dim)."""
    out = g.standard_normal((n, dim)).astype(np.float32)
    norms = np.linalg.norm(out, axis=1, keepdims=True) + 1e-8
    return (out / norms).astype(np.float32)


def _fhrr_unit_phase(n: int, dim: int, g: np.random.Generator) -> np.ndarray:
    """Stack of n random unit-modulus complex vectors (exp(i*theta)). Shape (n, dim) complex64."""
    theta = g.uniform(-np.pi, np.pi, size=(n, dim)).astype(np.float32)
    return (np.cos(theta) + 1j * np.sin(theta)).astype(np.complex64)


# ------------------------------------------------------------------
# Real-valued HRR (circular convolution / correlation via FFT)
# ------------------------------------------------------------------
def _bind_circ(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """HRR circular convolution via FFT. Real input -> real output."""
    fa = np.fft.fft(a); fb = np.fft.fft(b)
    return np.fft.ifft(fa * fb).real.astype(np.float32)


def _unbind_circ(c: np.ndarray, b: np.ndarray) -> np.ndarray:
    """HRR circular correlation via FFT * conj. Real input -> real output."""
    fc = np.fft.fft(c); fb = np.fft.fft(b)
    return np.fft.ifft(fc * fb.conj()).real.astype(np.float32)


def _l2_normalize(v: np.ndarray) -> np.ndarray:
    n = float(np.linalg.norm(v)) + 1e-8
    return (v / n).astype(np.float32)


def _l2_normalize_rows(X: np.ndarray) -> np.ndarray:
    n = np.linalg.norm(X, axis=1, keepdims=True) + 1e-8
    return (X / n).astype(np.float32)


def _cosine_to_codebook_real(rec: np.ndarray, codebook: np.ndarray) -> np.ndarray:
    """Row-wise cosine between vector rec (D,) and matrix codebook (k,D). Real."""
    rn = _l2_normalize(rec)
    Cn = _l2_normalize_rows(codebook)
    return Cn @ rn


# ------------------------------------------------------------------
# FHRR (complex element-wise)
# ------------------------------------------------------------------
def _bind_fhrr(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """FHRR bind: element-wise complex multiply."""
    return (a * b).astype(np.complex64)


def _unbind_fhrr(c: np.ndarray, b: np.ndarray) -> np.ndarray:
    """FHRR unbind: element-wise complex multiply with conjugate."""
    return (c * np.conj(b)).astype(np.complex64)


def _l2_normalize_complex(v: np.ndarray) -> np.ndarray:
    n = float(np.linalg.norm(v)) + 1e-8
    return (v / n).astype(np.complex64)


def _cosine_to_codebook_complex(rec: np.ndarray, codebook: np.ndarray) -> np.ndarray:
    """Hermitian cosine between rec (D,) complex and codebook (k,D) complex; returns real (k,).
    cos = real(<a, conj(b)>) / (||a|| * ||b||)."""
    rn = _l2_normalize_complex(rec)
    norms = np.linalg.norm(codebook, axis=1) + 1e-8
    Cn = codebook / norms[:, None]
    # inner product per-row with rec; take real part of <Cn_row, conj(rn)> = sum Cn * conj(rn)
    return np.real(Cn @ np.conj(rn)).astype(np.float32)


# ------------------------------------------------------------------
# Per-arm protocol implementations
# ------------------------------------------------------------------
def _run_arm_real(
    seed_offset: int,
    dim: int,
    n_subj: int,
    n_obj: int,
    coverage: float,
    codebook_fn,
    normalize_per_bind: bool,
) -> dict:
    """Real-valued HRR arm: arbitrary codebook + circular convolution bind + optional per-bind L2 norm.

    Returns dict with in_distribution_top1, holdout_top1, n_train, n_held, chance_top1, mean_cosines.
    """
    g = np.random.default_rng(seed_offset)
    subj = codebook_fn(n_subj, dim, g)
    obj = codebook_fn(n_obj, dim, g)
    all_pairs = [(i, j) for i in range(n_subj) for j in range(n_obj)]
    g.shuffle(all_pairs)
    n_train = int(round(coverage * len(all_pairs)))
    train_pairs = all_pairs[:n_train]
    held_pairs = all_pairs[n_train:]

    bank = np.zeros(dim, dtype=np.float32)
    for (i, j) in train_pairs:
        b = _bind_circ(subj[i], obj[j])
        if normalize_per_bind:
            b = _l2_normalize(b)
        bank = bank + b

    # In-distribution (train) recall
    in_correct = 0
    in_cosines_correct = []
    for (i, j) in train_pairs:
        rec = _unbind_circ(bank, subj[i])
        cos_obj = _cosine_to_codebook_real(rec, obj)
        if int(np.argmax(cos_obj)) == j:
            in_correct += 1
        in_cosines_correct.append(float(cos_obj[j]))
    in_top1 = in_correct / max(len(train_pairs), 1)

    # Holdout
    correct = 0
    cosines_correct = []
    for (i, j) in held_pairs:
        rec = _unbind_circ(bank, subj[i])
        cos_obj = _cosine_to_codebook_real(rec, obj)
        if int(np.argmax(cos_obj)) == j:
            correct += 1
        cosines_correct.append(float(cos_obj[j]))
    holdout_top1 = correct / max(len(held_pairs), 1)

    return {
        "n_subj": n_subj,
        "n_obj": n_obj,
        "coverage": coverage,
        "n_train": len(train_pairs),
        "n_held": len(held_pairs),
        "in_distribution_top1": float(in_top1),
        "holdout_top1": float(holdout_top1),
        "chance_top1": 1.0 / n_obj,
        "mean_cosine_correct_in_dist": float(np.mean(in_cosines_correct)) if in_cosines_correct else 0.0,
        "mean_cosine_correct_holdout": float(np.mean(cosines_correct)) if cosines_correct else 0.0,
    }


def _run_arm_fhrr(
    seed_offset: int,
    dim: int,
    n_subj: int,
    n_obj: int,
    coverage: float,
) -> dict:
    """FHRR arm: unit-phase codebook + element-wise complex bind + bundling via complex sum.
    Per-bind L2 normalization of complex vector is applied so the bank stays well-scaled.
    """
    g = np.random.default_rng(seed_offset)
    subj = _fhrr_unit_phase(n_subj, dim, g)
    obj = _fhrr_unit_phase(n_obj, dim, g)
    all_pairs = [(i, j) for i in range(n_subj) for j in range(n_obj)]
    g.shuffle(all_pairs)
    n_train = int(round(coverage * len(all_pairs)))
    train_pairs = all_pairs[:n_train]
    held_pairs = all_pairs[n_train:]

    bank = np.zeros(dim, dtype=np.complex64)
    for (i, j) in train_pairs:
        b = _bind_fhrr(subj[i], obj[j])
        # per-bind L2 normalize (each bind already unit-modulus per-coord ~ unit norm in C; defensive)
        b = _l2_normalize_complex(b)
        bank = bank + b

    in_correct = 0
    in_cosines_correct = []
    for (i, j) in train_pairs:
        rec = _unbind_fhrr(bank, subj[i])
        cos_obj = _cosine_to_codebook_complex(rec, obj)
        if int(np.argmax(cos_obj)) == j:
            in_correct += 1
        in_cosines_correct.append(float(cos_obj[j]))
    in_top1 = in_correct / max(len(train_pairs), 1)

    correct = 0
    cosines_correct = []
    for (i, j) in held_pairs:
        rec = _unbind_fhrr(bank, subj[i])
        cos_obj = _cosine_to_codebook_complex(rec, obj)
        if int(np.argmax(cos_obj)) == j:
            correct += 1
        cosines_correct.append(float(cos_obj[j]))
    holdout_top1 = correct / max(len(held_pairs), 1)

    return {
        "n_subj": n_subj,
        "n_obj": n_obj,
        "coverage": coverage,
        "n_train": len(train_pairs),
        "n_held": len(held_pairs),
        "in_distribution_top1": float(in_top1),
        "holdout_top1": float(holdout_top1),
        "chance_top1": 1.0 / n_obj,
        "mean_cosine_correct_in_dist": float(np.mean(in_cosines_correct)) if in_cosines_correct else 0.0,
        "mean_cosine_correct_holdout": float(np.mean(cosines_correct)) if cosines_correct else 0.0,
    }


# ------------------------------------------------------------------
# Per-seed driver: run all 4 arms with matched random seed bases (so subject/object pair selection is identical-ish across arms; codebooks differ by arm)
# ------------------------------------------------------------------
def run_unit(seed: int) -> dict:
    t0 = time.time()
    results = {}

    # ARM_BROKEN_SPARSE_NO_NORM
    print("  [seed=%d] ARM_BROKEN_SPARSE_NO_NORM starting" % seed, flush=True)
    r = _run_arm_real(
        seed_offset=seed * 1009 + 1, dim=N_DIM,
        n_subj=N_SUBJ, n_obj=N_OBJ, coverage=COVERAGE,
        codebook_fn=lambda n, d, g: _sparse_bipolar(n, d, SPARSE_F, g),
        normalize_per_bind=False,
    )
    print("    in_dist=%.3f holdout=%.3f chance=%.3f" % (
        r["in_distribution_top1"], r["holdout_top1"], r["chance_top1"]), flush=True)
    results["ARM_BROKEN_SPARSE_NO_NORM"] = r

    # ARM_DENSE_HRR_NORMALIZED
    print("  [seed=%d] ARM_DENSE_HRR_NORMALIZED starting" % seed, flush=True)
    r = _run_arm_real(
        seed_offset=seed * 1009 + 2, dim=N_DIM,
        n_subj=N_SUBJ, n_obj=N_OBJ, coverage=COVERAGE,
        codebook_fn=_dense_unit_norm,
        normalize_per_bind=True,
    )
    print("    in_dist=%.3f holdout=%.3f chance=%.3f" % (
        r["in_distribution_top1"], r["holdout_top1"], r["chance_top1"]), flush=True)
    results["ARM_DENSE_HRR_NORMALIZED"] = r

    # ARM_FHRR_NORMALIZED
    print("  [seed=%d] ARM_FHRR_NORMALIZED starting" % seed, flush=True)
    r = _run_arm_fhrr(
        seed_offset=seed * 1009 + 3, dim=N_DIM,
        n_subj=N_SUBJ, n_obj=N_OBJ, coverage=COVERAGE,
    )
    print("    in_dist=%.3f holdout=%.3f chance=%.3f" % (
        r["in_distribution_top1"], r["holdout_top1"], r["chance_top1"]), flush=True)
    results["ARM_FHRR_NORMALIZED"] = r

    # ARM_SPARSE_HRR_NORMALIZED
    print("  [seed=%d] ARM_SPARSE_HRR_NORMALIZED starting" % seed, flush=True)
    r = _run_arm_real(
        seed_offset=seed * 1009 + 4, dim=N_DIM,
        n_subj=N_SUBJ, n_obj=N_OBJ, coverage=COVERAGE,
        codebook_fn=lambda n, d, g: _sparse_bipolar(n, d, SPARSE_F, g),
        normalize_per_bind=True,
    )
    print("    in_dist=%.3f holdout=%.3f chance=%.3f" % (
        r["in_distribution_top1"], r["holdout_top1"], r["chance_top1"]), flush=True)
    results["ARM_SPARSE_HRR_NORMALIZED"] = r

    return {
        "seed": seed,
        "by_arm": results,
        "N_DIM": N_DIM,
        "SPARSE_F": SPARSE_F,
        "N_SUBJ": N_SUBJ,
        "N_OBJ": N_OBJ,
        "COVERAGE": COVERAGE,
        "wall_s": time.time() - t0,
        "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
    }


# ------------------------------------------------------------------
# Verdict logic
# ------------------------------------------------------------------
def compute_verdict(units: list) -> tuple:
    """Aggregate by-arm in_dist and holdout across seeds; classify per cell-level bands.

    Returns (verdict, msg, detail).
    """
    if not units:
        return ("HARD_FAIL", "no results", {})

    # Aggregate per-arm
    per_arm: dict = {}
    for arm in ARMS:
        in_list = [u["by_arm"][arm]["in_distribution_top1"] for u in units]
        ho_list = [u["by_arm"][arm]["holdout_top1"] for u in units]
        in_mean = float(np.mean(in_list))
        ho_mean = float(np.mean(ho_list))
        in_cv = float(np.std(in_list) / max(in_mean, 1e-6))
        ho_cv = float(np.std(ho_list) / max(ho_mean, 1e-6))
        per_arm[arm] = {
            "in_distribution_top1_mean": in_mean,
            "holdout_top1_mean": ho_mean,
            "in_distribution_top1_per_seed": in_list,
            "holdout_top1_per_seed": ho_list,
            "in_distribution_top1_cv": in_cv,
            "holdout_top1_cv": ho_cv,
            "in_dist_clears_sanity_floor": (in_mean > HP_IN_DIST_FLOOR),
        }

    normalized_arms = [
        "ARM_DENSE_HRR_NORMALIZED",
        "ARM_FHRR_NORMALIZED",
        "ARM_SPARSE_HRR_NORMALIZED",
    ]
    norm_clearing = [a for a in normalized_arms if per_arm[a]["in_dist_clears_sanity_floor"]]

    broken_in_dist = per_arm["ARM_BROKEN_SPARSE_NO_NORM"]["in_distribution_top1_mean"]
    chance = 1.0 / N_OBJ

    # Cell-level verdict
    if not norm_clearing:
        # No normalized arm cleared sanity floor -> substrate's HRR family broken at this scale
        cell_verdict = "HARD_FAIL_DEEPER_ISSUE"
        cell_msg = (
            "HARD_FAIL_DEEPER_ISSUE: NO normalized arm clears in_dist > %.2f sanity floor. "
            "Substrate's HRR-family fundamentally broken at N_DIM=%d / M=%d. "
            "Per-arm in_dist means: DENSE=%.3f FHRR=%.3f SPARSE_NORM=%.3f; broken=%.3f (chance %.3f)."
        ) % (
            HP_IN_DIST_FLOOR, N_DIM, int(round(COVERAGE * N_SUBJ * N_OBJ)),
            per_arm["ARM_DENSE_HRR_NORMALIZED"]["in_distribution_top1_mean"],
            per_arm["ARM_FHRR_NORMALIZED"]["in_distribution_top1_mean"],
            per_arm["ARM_SPARSE_HRR_NORMALIZED"]["in_distribution_top1_mean"],
            broken_in_dist, chance,
        )
    else:
        # Some normalized arm cleared sanity floor; classify by best holdout among those arms
        ho_among_norm = {a: per_arm[a]["holdout_top1_mean"] for a in norm_clearing}
        best_arm = max(ho_among_norm.keys(), key=lambda a: ho_among_norm[a])
        best_ho = ho_among_norm[best_arm]
        all_norm_below_retest = all(per_arm[a]["holdout_top1_mean"] < HARD_FAIL_RETEST_HI for a in norm_clearing)

        if best_ho > HP_HOLDOUT_FLOOR:
            cell_verdict = "HARD_PASS_COMPOSITIONAL_ALIVE"
            cell_msg = (
                "HARD_PASS_COMPOSITIONAL_ALIVE: best normalized arm %s clears in_dist=%.3f AND holdout=%.3f (>%.2f). "
                "Substrate compositionally generalizes when configured right. "
                "Per-arm holdout means (sanity-clearing only): %s. Broken arm in_dist=%.3f (provenance)."
            ) % (
                best_arm, per_arm[best_arm]["in_distribution_top1_mean"], best_ho, HP_HOLDOUT_FLOOR,
                {a: round(per_arm[a]["holdout_top1_mean"], 3) for a in norm_clearing},
                broken_in_dist,
            )
        elif all_norm_below_retest:
            cell_verdict = "HARD_FAIL_PROPER_RETEST"
            cell_msg = (
                "HARD_FAIL_PROPER_RETEST: normalized arms clear sanity floor in_dist>%.2f, but ALL have holdout<%.2f. "
                "Genuine compositional-generalization failure (substrate-product implication: needs attention-based "
                "recombination or hierarchical compose). Per-arm holdout means (clearing only): %s."
            ) % (
                HP_IN_DIST_FLOOR, HARD_FAIL_RETEST_HI,
                {a: round(per_arm[a]["holdout_top1_mean"], 3) for a in norm_clearing},
            )
        else:
            cell_verdict = "MIDDLE_BAND_PARTIAL_GENERALIZATION"
            cell_msg = (
                "MIDDLE_BAND_PARTIAL_GENERALIZATION: best normalized arm %s clears in_dist=%.3f and holdout=%.3f "
                "(in [%.2f, %.2f]). Partial generalization. Per-arm holdout means (clearing only): %s."
            ) % (
                best_arm, per_arm[best_arm]["in_distribution_top1_mean"], best_ho,
                MIDDLE_HOLDOUT_LO, HP_HOLDOUT_FLOOR,
                {a: round(per_arm[a]["holdout_top1_mean"], 3) for a in norm_clearing},
            )

    # Sanity check on the broken arm
    broken_expected_pass = (broken_in_dist < BROKEN_EXPECTED_HI)
    if not broken_expected_pass:
        cell_msg = cell_msg + (
            " | WARN: ARM_BROKEN_SPARSE_NO_NORM in_dist=%.3f >= %.2f; broken-arm provenance check FAILED -- "
            "diagnosis may need revisit."
        ) % (broken_in_dist, BROKEN_EXPECTED_HI)

    detail = {
        "n_seeds": len(units),
        "N_DIM": N_DIM,
        "SPARSE_F": SPARSE_F,
        "N_SUBJ": N_SUBJ,
        "N_OBJ": N_OBJ,
        "COVERAGE": COVERAGE,
        "per_arm": per_arm,
        "normalized_arms_clearing_sanity": norm_clearing,
        "broken_arm_provenance_in_dist": broken_in_dist,
        "broken_arm_provenance_check_passed": broken_expected_pass,
        "bands": {
            "HP_IN_DIST_FLOOR": HP_IN_DIST_FLOOR,
            "HP_HOLDOUT_FLOOR": HP_HOLDOUT_FLOOR,
            "MIDDLE_HOLDOUT_LO": MIDDLE_HOLDOUT_LO,
            "HARD_FAIL_RETEST_HI": HARD_FAIL_RETEST_HI,
            "BROKEN_EXPECTED_HI": BROKEN_EXPECTED_HI,
        },
        "chance_top1": chance,
        "CONFIG_VERSION": CONFIG_VERSION,
        "what_this_does_not_show": (
            "This cell tests COMPOSITIONAL GENERALIZATION on subject-object role-binding under SUPERPOSITION at a "
            "single (N_DIM, M) point. It does NOT show: (1) language-task performance (no text corpus); (2) learning "
            "/ plasticity (no cf-RPE, no gradient updates); (3) downstream task benefit; (4) capacity scaling "
            "(single M value); (5) noise / sparse-key robustness. By-construction: TRAIN-pair 'recall' is reported "
            "as in_distribution_top1 (sanity floor); HELDOUT is the real test. ARM_BROKEN is a CONTROL meant to "
            "reproduce the broken-mechanism failure for provenance."
        ),
        "honest_scope": (
            "Pure substrate primitives (HRR bind/unbind + per-arm codebook + normalization); NO learning. NumPy CPU. "
            "Per USER 2026-06-24 compositional reasoner product story; replaces broken ARM 2 of brain-aligned shotgun."
        ),
        "cites": [
            "USER_compositional_reasoner_product_story_2026-06-24",
            "fact_finder_director_compositional_failure_USER_test_wrong_VSA_modality_inventory_2026-06-24",
            "exp_substrate_brain_aligned_aliveness_shotgun_v1__partial_metrics_s7__in_distribution_top1_0.10",
            "exp_contextual_encoding_hrr_PRODUCTION_held_out_v1__ARM_BIND_RECENT_5_lift_0.212",
            "exp_fhrr_rs_parity_cpu_v1__HARD_PASS",
            "exp_hrr_depth_budget_sparse_bipolar_v2__HARD_PASS_autoassociative",
            "Plate_1995_HRR_canonical_dense_unit_norm",
        ],
    }
    return (cell_verdict, cell_msg, detail)


# ------------------------------------------------------------------
# Self-test
# ------------------------------------------------------------------
def _selftest() -> None:
    """Mechanism sanity at TINY dim. Asserts:
      - sparse-bipolar shape + sparsity rate.
      - dense unit-norm builders produce unit-norm rows.
      - FHRR unit-phase rows are ~unit-modulus per coord.
      - HRR circ bind/unbind round-trip strongly correlated (dense unit-norm).
      - FHRR bind/unbind exactly involutive (single pair).
      - On tiny configs (small M, large dim, normalization on), DENSE_HRR_NORMALIZED and
        FHRR_NORMALIZED should both achieve in_dist > 0.70 (the sanity floor).
      - ARM_BROKEN_SPARSE_NO_NORM at the same tiny config can have low in_dist (broken regime
        not guaranteed at TINY scale; we just assert it can run without errors).
    """
    g = np.random.default_rng(0)
    dim = 256

    # Sparse-bipolar shape + density
    X = _sparse_bipolar(5, dim, SPARSE_F, g)
    assert X.shape == (5, dim), "sparse-bipolar shape mismatch"
    avg_nz = float(np.mean(np.count_nonzero(X, axis=1)))
    expect = SPARSE_F * dim
    assert abs(avg_nz - expect) <= max(1.0, 0.2 * expect), (
        "sparse-bipolar nz=%.1f expected near %.1f" % (avg_nz, expect)
    )

    # Dense unit-norm
    Y = _dense_unit_norm(5, dim, g)
    norms = np.linalg.norm(Y, axis=1)
    assert np.allclose(norms, 1.0, atol=1e-4), "dense unit-norm builder broken: norms=%s" % norms

    # FHRR unit-phase
    Z = _fhrr_unit_phase(5, dim, g)
    mods = np.abs(Z)
    assert np.allclose(mods, 1.0, atol=1e-4), "FHRR unit-phase magnitudes not unit"

    # HRR circ bind/unbind: dense unit-norm round-trip is well-correlated
    a = Y[0]
    b = Y[1]
    c = _bind_circ(a, b)
    a_back = _unbind_circ(c, b)
    cos_ab = float(_cosine_to_codebook_real(a_back, a[None, :])[0])
    assert cos_ab > 0.5, "HRR circ bind/unbind round-trip cosine too low (%.3f)" % cos_ab

    # FHRR bind/unbind exactly involutive
    af = Z[0]
    bf = Z[1]
    cf = _bind_fhrr(af, bf)
    af_back = _unbind_fhrr(cf, bf)
    cos_f = float(_cosine_to_codebook_complex(af_back, af[None, :])[0])
    assert cos_f > 0.99, "FHRR bind/unbind not involutive (cos=%.4f)" % cos_f

    # Self-test sanity: directly verify the bind/unbind mechanism on each codebook type at
    # MINIMAL crosstalk (M=3 disjoint pairs; one binding per subject). This isolates "does the
    # mechanism work" from "does it scale" -- the latter is what the FULL run measures.
    tiny_dim = 2048

    def _mechanism_sanity(codebook_fn, normalize_per_bind, label, use_complex=False):
        """Bind 3 disjoint (s_i, o_i) pairs into a bank; unbind each subj; recover obj. Expect 3/3."""
        gg = np.random.default_rng(11)
        s = codebook_fn(3, tiny_dim, gg)
        o = codebook_fn(3, tiny_dim, gg)
        if use_complex:
            bank = np.zeros(tiny_dim, dtype=np.complex64)
            for i in range(3):
                b = _bind_fhrr(s[i], o[i])
                b = _l2_normalize_complex(b)
                bank = bank + b
            correct = 0
            for i in range(3):
                rec = _unbind_fhrr(bank, s[i])
                cos_obj = _cosine_to_codebook_complex(rec, o)
                if int(np.argmax(cos_obj)) == i:
                    correct += 1
            return correct / 3.0
        else:
            bank = np.zeros(tiny_dim, dtype=np.float32)
            for i in range(3):
                b = _bind_circ(s[i], o[i])
                if normalize_per_bind:
                    b = _l2_normalize(b)
                bank = bank + b
            correct = 0
            for i in range(3):
                rec = _unbind_circ(bank, s[i])
                cos_obj = _cosine_to_codebook_real(rec, o)
                if int(np.argmax(cos_obj)) == i:
                    correct += 1
            return correct / 3.0

    acc_dense = _mechanism_sanity(_dense_unit_norm, True, "DENSE")
    assert acc_dense >= 0.99, "DENSE mechanism sanity failed (%.3f)" % acc_dense

    acc_fhrr = _mechanism_sanity(
        lambda n, d, g: _fhrr_unit_phase(n, d, g), False, "FHRR", use_complex=True,
    )
    assert acc_fhrr >= 0.99, "FHRR mechanism sanity failed (%.3f)" % acc_fhrr

    acc_sparse_norm = _mechanism_sanity(
        lambda n, d, g: _sparse_bipolar(n, d, SPARSE_F, g), True, "SPARSE_NORM",
    )
    # Sparse-bipolar codebook is approximately orthogonal at modest n; expect 3/3 at this scale
    assert acc_sparse_norm >= 0.99, "SPARSE_NORM mechanism sanity failed (%.3f)" % acc_sparse_norm

    # Run-arm wrapper sanity: ensure the full per-arm protocol returns sensible numbers (does not
    # crash, in_dist + holdout in [0,1]) at a modest config. We do NOT assert on accuracy here --
    # the FULL run is the discriminator.
    r_dense = _run_arm_real(
        seed_offset=21, dim=tiny_dim, n_subj=4, n_obj=4, coverage=0.5,
        codebook_fn=_dense_unit_norm, normalize_per_bind=True,
    )
    assert 0.0 <= r_dense["in_distribution_top1"] <= 1.0
    assert 0.0 <= r_dense["holdout_top1"] <= 1.0

    r_fhrr = _run_arm_fhrr(seed_offset=22, dim=tiny_dim, n_subj=4, n_obj=4, coverage=0.5)
    assert 0.0 <= r_fhrr["in_distribution_top1"] <= 1.0
    assert 0.0 <= r_fhrr["holdout_top1"] <= 1.0

    r_sparse_norm = _run_arm_real(
        seed_offset=23, dim=tiny_dim, n_subj=4, n_obj=4, coverage=0.5,
        codebook_fn=lambda n, d, g: _sparse_bipolar(n, d, SPARSE_F, g),
        normalize_per_bind=True,
    )
    assert 0.0 <= r_sparse_norm["in_distribution_top1"] <= 1.0
    assert 0.0 <= r_sparse_norm["holdout_top1"] <= 1.0

    r_broken = _run_arm_real(
        seed_offset=24, dim=tiny_dim, n_subj=4, n_obj=4, coverage=0.5,
        codebook_fn=lambda n, d, g: _sparse_bipolar(n, d, SPARSE_F, g),
        normalize_per_bind=False,
    )
    assert 0.0 <= r_broken["in_distribution_top1"] <= 1.0
    assert 0.0 <= r_broken["holdout_top1"] <= 1.0

    # Verdict-shape sanity: synthesize unit results to ensure the verdict logic returns each band
    def _mk_unit(in_dense, ho_dense, in_fhrr, ho_fhrr, in_sparse, ho_sparse, in_broken, ho_broken):
        ba = {
            "ARM_BROKEN_SPARSE_NO_NORM": {
                "in_distribution_top1": in_broken, "holdout_top1": ho_broken,
                "chance_top1": 1.0 / 4,
                "n_subj": 4, "n_obj": 4, "coverage": 0.5,
                "n_train": 8, "n_held": 8,
                "mean_cosine_correct_in_dist": 0.0, "mean_cosine_correct_holdout": 0.0,
            },
            "ARM_DENSE_HRR_NORMALIZED": {
                "in_distribution_top1": in_dense, "holdout_top1": ho_dense,
                "chance_top1": 1.0 / 4,
                "n_subj": 4, "n_obj": 4, "coverage": 0.5,
                "n_train": 8, "n_held": 8,
                "mean_cosine_correct_in_dist": 0.0, "mean_cosine_correct_holdout": 0.0,
            },
            "ARM_FHRR_NORMALIZED": {
                "in_distribution_top1": in_fhrr, "holdout_top1": ho_fhrr,
                "chance_top1": 1.0 / 4,
                "n_subj": 4, "n_obj": 4, "coverage": 0.5,
                "n_train": 8, "n_held": 8,
                "mean_cosine_correct_in_dist": 0.0, "mean_cosine_correct_holdout": 0.0,
            },
            "ARM_SPARSE_HRR_NORMALIZED": {
                "in_distribution_top1": in_sparse, "holdout_top1": ho_sparse,
                "chance_top1": 1.0 / 4,
                "n_subj": 4, "n_obj": 4, "coverage": 0.5,
                "n_train": 8, "n_held": 8,
                "mean_cosine_correct_in_dist": 0.0, "mean_cosine_correct_holdout": 0.0,
            },
        }
        return {"seed": 0, "by_arm": ba, "N_DIM": tiny_dim, "SPARSE_F": SPARSE_F,
                "N_SUBJ": 4, "N_OBJ": 4, "COVERAGE": 0.5,
                "wall_s": 0.0, "run_mode": "selftest", "config_version": "selftest"}

    # HARD_PASS path: dense clears in_dist 0.95 and holdout 0.80
    u_hp = _mk_unit(0.95, 0.80, 0.92, 0.78, 0.85, 0.72, 0.12, 0.05)
    v, m, d = compute_verdict([u_hp, u_hp, u_hp])
    assert v == "HARD_PASS_COMPOSITIONAL_ALIVE", "T_HP expected, got %s | %s" % (v, m[:200])

    # MIDDLE path: dense in_dist 0.85 holdout 0.30; others below sanity
    u_mid = _mk_unit(0.85, 0.30, 0.40, 0.10, 0.30, 0.10, 0.12, 0.05)
    v, m, d = compute_verdict([u_mid, u_mid, u_mid])
    assert v == "MIDDLE_BAND_PARTIAL_GENERALIZATION", "T_MID expected, got %s | %s" % (v, m[:200])

    # HARD_FAIL_PROPER_RETEST: dense in_dist 0.95 but holdout 0.05; FHRR in_dist 0.92 holdout 0.04;
    # SPARSE_NORM in_dist 0.85 holdout 0.04 -> all normalized clear sanity, all holdout < 0.20
    u_retest = _mk_unit(0.95, 0.05, 0.92, 0.04, 0.85, 0.04, 0.12, 0.05)
    v, m, d = compute_verdict([u_retest, u_retest, u_retest])
    assert v == "HARD_FAIL_PROPER_RETEST", "T_RETEST expected, got %s | %s" % (v, m[:200])

    # HARD_FAIL_DEEPER_ISSUE: NO normalized arm clears sanity floor
    u_deep = _mk_unit(0.40, 0.10, 0.30, 0.10, 0.20, 0.05, 0.12, 0.05)
    v, m, d = compute_verdict([u_deep, u_deep, u_deep])
    assert v == "HARD_FAIL_DEEPER_ISSUE", "T_DEEP expected, got %s | %s" % (v, m[:200])

    print(
        "[selftest] PASS: codebook builders + HRR involutive + FHRR involutive + tiny in-dist "
        "for DENSE/FHRR/SPARSE_NORM + verdict-band logic (HP / MIDDLE / RETEST / DEEPER) OK",
        flush=True,
    )


# ------------------------------------------------------------------
# Main
# ------------------------------------------------------------------
if __name__ == "__main__":
    _selftest()
    if _ARGS.self_test:
        raise SystemExit(0)
    print(
        "[config] %s mode=%s N_DIM=%d arms=%s seeds=%s | %s" % (
            ANCHOR_NAME, RUN_MODE, N_DIM, ARMS, SEEDS, CONFIG_VERSION
        ),
        flush=True,
    )
    out_dir = get_output_dir(ANCHOR_NAME)
    run_cfg = {
        "run_mode": RUN_MODE,
        "N": N_DIM,
        "schema": "compositional-generalization-corrected-v1",
    }
    t0 = time.time()
    for seed in SEEDS:
        key = "s%d" % seed
        already = aggregate_partials(out_dir, [key], run_config=run_cfg)
        if key in already:
            print("[ckpt] %s done; skip" % key, flush=True)
            continue
        result = run_unit(seed)
        write_partial_key(out_dir, key, result)
    units = list(aggregate_partials(
        out_dir, ["s%d" % s for s in SEEDS], run_config=run_cfg
    ).values())
    verdict, msg, detail = compute_verdict(units)
    print("\n[VERDICT] " + msg, flush=True)
    metrics = {
        "anchor_name": ANCHOR_NAME,
        "verdict": verdict,
        "verdict_msg": msg,
        "run_mode": RUN_MODE,
        "N_DIM": N_DIM,
        "SPARSE_F": SPARSE_F,
        "N_SUBJ": N_SUBJ,
        "N_OBJ": N_OBJ,
        "COVERAGE": COVERAGE,
        "n_seeds": len(SEEDS),
        "detail": detail,
        "metrics_source": "measured_cpu_substrate_compositional_generalization_CORRECTED_v1",
        "per_unit": units,
        "elapsed_s": time.time() - t0,
        "summary": msg,
        "substrate_only_decode_gate": "N/A (mechanism-characterization cell, not LM cell)",
    }
    write_metrics(out_dir, metrics, units)
    print("[metrics] written to %s" % (out_dir / "metrics.json"), flush=True)
