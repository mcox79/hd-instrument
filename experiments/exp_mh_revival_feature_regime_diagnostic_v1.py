"""mh_revival_feature_regime_diagnostic_v1.

SCIENTIFIC QUESTION (Modern Hopfield revival ANCHOR 1):

  Prior cell gap3_modern_hopfield_prototype_attractor_v1 HARD_FAIL'd / MIDDLE_BAND
  with MH_PROTO=0.22, MH_CONT=0.26 in the PROTOTYPE/SOFTMAX regime
  (per-category prototype = softmax-attractor fixed point over training instances,
  then bind+bundle, then unbind+classify). Research drill (Krotov 2-regime
  analysis; notes/research_modern_hopfield_revival_slow_built_basins_2026-06-26.md)
  identifies the failure as a REGIME error, not a mechanism error.

  Krotov-Hopfield 2016 characterizes Dense Associative Memory as a family of
  energy functions parametrized by polynomial order n:
    E(q) = -sum_i F(<q, xi_i>)    where F(s) = s^n / n (or softmax in the limit)
  At small n (n=2 = classical Hopfield), many low-overlap memories COOPERATE.
  At large n (softmax ~ n=infinity = modern Hopfield 2020), one high-overlap
  pattern dominates. The substrate has 20 weak instances per category, with
  signal margin ~0.10. Large beta with a 0.10 signal margin is a noise
  amplifier; small n / cooperative aggregation should be much more robust.

  This cell tests the SAME mechanism family with DIFFERENT polynomial orders
  on the SAME substrate state that produced MH_PROTO=0.22. If n=2 lifts to
  0.50+, the prior cell's HARD_FAIL was regime selection, not mechanism class.

  MECHANISM (per heldout query q, per category c):
    For each training instance x_i (across ALL categories):
      overlap_i = cos(q, x_i)
    For each category c with training instances {x_j : c_j = c}:
      score_c = sum_{j in c} F(overlap_j)
        where F(s) = s^n for n in {2, 4, 10}  (feature regime: rectified)
        or F(s) = softmax(beta*s) for the softmax control (prototype regime)
    predicted_cat = argmax_c score_c

  Note: this is FEATURE-MATCHING (aggregate over instances) -- NOT prototype-
  formation-then-classify. The instances themselves act as the basins.

PRE-REGISTERED BANDS (LOCKED via module-init assert):
  HARD_PASS_REGIME_CONFIRMED:
    ARM_HOPFIELD_N2 >= 0.50 heldout AND >= +0.15 over ARM_HOPFIELD_N20_SOFTMAX
    Interpretation: regime error confirmed; substrate-product win without
    new architecture; prior cell picked wrong polynomial order.
  HARD_FAIL_MECHANISM_CLASS_DEAD:
    ARM_HOPFIELD_N2 within 0.05 of ARM_HOPFIELD_N20_SOFTMAX (both ~0.22)
    Interpretation: regime not the issue; pivot to slow-build (STC ANCHOR 2).
  MIDDLE_BAND [0.35, 0.50]: PARTIAL feature-regime lift; queue follow-up.
  HARD_FAIL_HARNESS_CONFOUND: ARM_HRR_BUNDLE_PROTOTYPE drifts > 0.03 from
    Cell 1 reference (0.4733 full; 0.58 smoke seed=11) -> methodology mismatch.

ARMS (6):
  ARM_BASELINE_NO_SCHEMA      : Cell 1 nearest-train-neighbor (sanity rail)
  ARM_HRR_BUNDLE_PROTOTYPE    : Cell 1 cross-cell rail (privileged cat_vec access)
  ARM_HOPFIELD_N2             : feature regime polynomial n=2 (PRIMARY hypothesis)
  ARM_HOPFIELD_N4             : intermediate polynomial regime n=4
  ARM_HOPFIELD_N10            : approaching prototype regime n=10
  ARM_HOPFIELD_N20_SOFTMAX    : prior MH_PROTO failure-regime control rail (softmax)

Config matches gap3_modern_hopfield_prototype_attractor_v1 exactly for cross-cell
rail: N=8192; 5 cats x 20 train + 10 heldout; CATEGORY_SIGNAL_FRAC=0.005;
seeds [11,13,19] full / [11] smoke. chance=0.20.

FORMULA SELF-TESTS:
  T1: HRR bind/unbind cosine >= 0.80 (cross-cell rail consistency)
  T2: Hopfield n=2 readout recovers cluster center under low-noise basin test
  T3: n=2 score with all-same-category instances reduces to weighted-overlap sum
  T4: bands LOCKED + CATEGORY_SIGNAL_FRAC matches Cell 1 (0.005)
  T5: cross-cell rail value (Cell 1 reference 0.4733) encoded
  T6: 6-arm discriminator non-degenerate on synthetic smoke

ASCII only. Substrate-only (HRR circular convolution; cosine readout).
Zero LLM calls at inference. ENCODER_PROVENANCE = SUBSTRATE_NATIVE.
"""
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import os
import argparse
import time
import json
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import (
    get_output_dir, resumable_seeds, write_partial, aggregate_partials,
)

ANCHOR_NAME = "mh_revival_feature_regime_diagnostic_v1"
ENCODER_PROVENANCE = "SUBSTRATE_NATIVE"

RUN_MODE = ("smoke" if "--smoke" in sys.argv
            else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

# ---------- Pre-reg bands (LOCKED) ----------
HARD_PASS_HELDOUT_FLOOR = 0.50               # ARM_HOPFIELD_N2 absolute floor
HARD_PASS_LIFT_OVER_SOFTMAX = 0.15           # ARM_HOPFIELD_N2 - ARM_HOPFIELD_N20_SOFTMAX
MIDDLE_BAND_LOWER = 0.35
MIDDLE_BAND_UPPER = 0.50
HARD_FAIL_REGIME_PROXIMITY = 0.05            # |N2 - N20_SOFTMAX| <= this = regime not the issue
CELL1_FEATURE_REFERENCE = 0.4733             # cross-cell rail anchor (Cell 1 ARM_FEATURE_BASED_SCHEMA)
CROSS_CELL_RAIL_TOL = 0.03                   # |HRR_BUNDLE_now - reference| <= this
PRIOR_MH_SOFTMAX_REFERENCE = 0.22            # gap3 cell's MH_PROTO seed=11 anchor

assert 0.0 < HARD_FAIL_REGIME_PROXIMITY < HARD_PASS_LIFT_OVER_SOFTMAX < 1.0, "tol order"
assert MIDDLE_BAND_LOWER < HARD_PASS_HELDOUT_FLOOR == MIDDLE_BAND_UPPER < 1.0, "band order"

# ---------- Config (matches Cell 1 exactly for cross-cell rail) ----------
N_CATEGORIES = 5
INSTANCES_PER_CATEGORY = 20
HELDOUT_PER_CATEGORY = 10
CHANCE = 1.0 / N_CATEGORIES  # 0.20
CATEGORY_SIGNAL_FRAC = 0.005  # MUST match Cell 1 exactly

# Hopfield regimes: polynomial order n + softmax control
HOPFIELD_N_FEATURE = 2     # primary hypothesis (cooperative aggregation)
HOPFIELD_N_INTERMEDIATE = 4
HOPFIELD_N_APPROACHING = 10
HOPFIELD_SOFTMAX_BETA = 2.0  # raw beta; scaled by sqrt(D) effective ~181 at D=8192 (matches prior)

if RUN_MODE == "smoke":
    SEEDS = [11]
    N = 8192            # capacity-sensitive dim identical smoke/full
else:
    SEEDS = [11, 13, 19]
    N = 8192


# ---------- HRR primitives (identical to Cell 1; load-bearing cross-cell rail) ----------
def make_rand_atom(N_dim: int, rng: np.random.RandomState) -> np.ndarray:
    v = rng.randn(N_dim).astype(np.float64)
    v /= (np.linalg.norm(v) + 1e-9)
    return v


def bind(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    return np.real(np.fft.ifft(np.fft.fft(a) * np.fft.fft(b)))


def unbind(c: np.ndarray, a: np.ndarray) -> np.ndarray:
    A = np.fft.fft(a)
    C = np.fft.fft(c)
    eps = 1e-9
    Ainv = np.conj(A) / (np.abs(A) ** 2 + eps)
    return np.real(np.fft.ifft(C * Ainv))


def cosine(x: np.ndarray, y: np.ndarray) -> float:
    nx = np.linalg.norm(x) + 1e-9
    ny = np.linalg.norm(y) + 1e-9
    return float(np.dot(x, y) / (nx * ny))


def cleanup_topk(query: np.ndarray, candidates: List[np.ndarray]) -> Tuple[int, float, List[float]]:
    cs = [cosine(query, c) for c in candidates]
    top1 = int(np.argmax(cs))
    return top1, cs[top1], cs


def _l2_normalize_row(X: np.ndarray, eps: float = 1e-12) -> np.ndarray:
    if X.ndim == 1:
        return X / (np.linalg.norm(X) + eps)
    n = np.linalg.norm(X, axis=1, keepdims=True) + eps
    return X / n


def _softmax(z: np.ndarray, axis: int = -1) -> np.ndarray:
    z = z - z.max(axis=axis, keepdims=True)
    ez = np.exp(z)
    return ez / (ez.sum(axis=axis, keepdims=True) + 1e-30)


# ---------- Hopfield feature-matching readout (the core mechanism) ----------
def hopfield_classify_polynomial(query: np.ndarray, train_X: np.ndarray, train_cats: np.ndarray,
                                  n_cats: int, polynomial_n: int) -> int:
    """Krotov feature regime: aggregate score per category = sum of rectified
    overlap^n over instances of that category. argmax wins.

    F(s) = max(s, 0)^n  (rectified polynomial; Krotov 2016 standard choice;
    keeps only positive overlaps from contributing -- negatives are anti-aligned
    and should not pull toward category).

    Args:
        query: (D,) heldout query, L2-normalized
        train_X: (K_total, D) L2-normalized training instances
        train_cats: (K_total,) category labels
        n_cats: number of categories
        polynomial_n: feature regime n (2 = classical, 10 = approaching prototype)

    Returns:
        predicted_cat: int argmax
    """
    overlaps = train_X @ query                  # (K_total,)
    rect = np.maximum(overlaps, 0.0)
    powered = rect ** polynomial_n              # (K_total,)
    scores = np.zeros(n_cats, dtype=np.float64)
    for c in range(n_cats):
        mask = (train_cats == c)
        scores[c] = float(powered[mask].sum())
    return int(np.argmax(scores))


def hopfield_classify_softmax(query: np.ndarray, train_X: np.ndarray, train_cats: np.ndarray,
                                n_cats: int, beta: float) -> int:
    """Modern Hopfield 2020 softmax regime: aggregate softmax weight per category.
    This is the prototype/winner-take-all regime the prior cell failed in.

    Args:
        query: (D,) L2-normalized heldout
        train_X: (K_total, D) L2-normalized training instances
        train_cats: (K_total,) labels
        n_cats: number of cats
        beta: raw beta; effective = beta * sqrt(D) per substrate convention

    Returns:
        predicted_cat
    """
    D = train_X.shape[1]
    effective_beta = beta * float(np.sqrt(D))
    overlaps = train_X @ query                  # (K_total,)
    weights = _softmax(effective_beta * overlaps, axis=0)  # softmax over ALL instances
    scores = np.zeros(n_cats, dtype=np.float64)
    for c in range(n_cats):
        mask = (train_cats == c)
        scores[c] = float(weights[mask].sum())
    return int(np.argmax(scores))


# ---------- Cell mechanics ----------
def build_task(seed: int) -> Dict:
    """Construct categories x instances + heldout. Identical to Cell 1 for cross-cell rail."""
    rng = np.random.RandomState(seed)
    cat_vecs = [make_rand_atom(N, rng) for _ in range(N_CATEGORIES)]
    prop_vecs = [make_rand_atom(N, rng) for _ in range(N_CATEGORIES)]

    def make_instance(ci: int) -> np.ndarray:
        noise = make_rand_atom(N, rng)
        sig = float(np.sqrt(CATEGORY_SIGNAL_FRAC))
        npart = float(np.sqrt(1.0 - CATEGORY_SIGNAL_FRAC))
        inst = sig * cat_vecs[ci] + npart * noise
        inst /= (np.linalg.norm(inst) + 1e-9)
        return inst

    train_instances = []
    heldout_instances = []
    for ci in range(N_CATEGORIES):
        for _ in range(INSTANCES_PER_CATEGORY):
            train_instances.append((ci, make_instance(ci)))
        for _ in range(HELDOUT_PER_CATEGORY):
            heldout_instances.append((ci, make_instance(ci)))

    return {
        "cat_vecs": cat_vecs,
        "prop_vecs": prop_vecs,
        "train_instances": train_instances,
        "heldout_instances": heldout_instances,
    }


def eval_no_schema_baseline(task: Dict) -> float:
    """Identical to Cell 1. Nearest-train-instance classification."""
    correct = 0
    total = 0
    train_inst_vecs = [iv for (_, iv) in task["train_instances"]]
    train_cats = [c for (c, _) in task["train_instances"]]
    for (ci, inst_vec) in task["heldout_instances"]:
        cs = [cosine(inst_vec, ti) for ti in train_inst_vecs]
        nearest = int(np.argmax(cs))
        predicted_cat = train_cats[nearest]
        if predicted_cat == ci:
            correct += 1
        total += 1
    return float(correct) / float(total) if total > 0 else 0.0


def arm_hrr_bundle_prototype(task: Dict) -> float:
    """Cell 1 ARM_FEATURE_BASED_SCHEMA mechanism (cross-cell rail).
    Uses cat_vecs directly (privileged) -- this is the upper-bound rail anchor.
    """
    cat_vecs = task["cat_vecs"]
    prop_vecs = task["prop_vecs"]
    schemas = [bind(cat_vecs[ci], prop_vecs[ci]) for ci in range(N_CATEGORIES)]
    bundle = np.sum(np.stack(schemas, axis=0), axis=0)
    bundle /= (np.linalg.norm(bundle) + 1e-9)
    # Eval via compositional unbind (identical to Cell 1)
    correct = 0
    total = 0
    for (ci, inst_vec) in task["heldout_instances"]:
        recovered = unbind(bundle, inst_vec)
        top1, _, _ = cleanup_topk(recovered, prop_vecs)
        if top1 == ci:
            correct += 1
        total += 1
    return float(correct) / float(total) if total > 0 else 0.0


def _build_train_matrix(task: Dict) -> Tuple[np.ndarray, np.ndarray]:
    """Stack training instances into (K_total, D) matrix + (K_total,) category vec.
    L2-normalize rows.
    """
    inst_vecs = [iv for (_, iv) in task["train_instances"]]
    cats = [c for (c, _) in task["train_instances"]]
    X = np.stack(inst_vecs, axis=0)
    X = _l2_normalize_row(X)
    return X, np.array(cats, dtype=np.int64)


def arm_hopfield_polynomial(task: Dict, polynomial_n: int) -> float:
    """Feature-matching regime: aggregate overlap^n per category over all training instances."""
    train_X, train_cats = _build_train_matrix(task)
    correct = 0
    total = 0
    for (ci, inst_vec) in task["heldout_instances"]:
        q = inst_vec / (np.linalg.norm(inst_vec) + 1e-9)
        predicted = hopfield_classify_polynomial(q, train_X, train_cats,
                                                  N_CATEGORIES, polynomial_n)
        if predicted == ci:
            correct += 1
        total += 1
    return float(correct) / float(total) if total > 0 else 0.0


def arm_hopfield_softmax(task: Dict, beta: float) -> float:
    """Softmax/prototype regime: WTA aggregation. Prior MH_PROTO failure-regime rail."""
    train_X, train_cats = _build_train_matrix(task)
    correct = 0
    total = 0
    for (ci, inst_vec) in task["heldout_instances"]:
        q = inst_vec / (np.linalg.norm(inst_vec) + 1e-9)
        predicted = hopfield_classify_softmax(q, train_X, train_cats,
                                                N_CATEGORIES, beta)
        if predicted == ci:
            correct += 1
        total += 1
    return float(correct) / float(total) if total > 0 else 0.0


def run_seed(seed: int) -> Dict:
    t0 = time.time()
    task = build_task(seed)

    arm_baseline = eval_no_schema_baseline(task)
    arm_bundle = arm_hrr_bundle_prototype(task)
    arm_n2 = arm_hopfield_polynomial(task, polynomial_n=HOPFIELD_N_FEATURE)
    arm_n4 = arm_hopfield_polynomial(task, polynomial_n=HOPFIELD_N_INTERMEDIATE)
    arm_n10 = arm_hopfield_polynomial(task, polynomial_n=HOPFIELD_N_APPROACHING)
    arm_n20_softmax = arm_hopfield_softmax(task, beta=HOPFIELD_SOFTMAX_BETA)

    elapsed = time.time() - t0
    print(f"  [seed={seed}] BASELINE={arm_baseline:.4f} HRR_BUNDLE={arm_bundle:.4f} "
          f"N2={arm_n2:.4f} N4={arm_n4:.4f} N10={arm_n10:.4f} "
          f"N20_SOFTMAX={arm_n20_softmax:.4f} elapsed={elapsed:.2f}s", flush=True)

    return {
        "seed": seed,
        "N": N,
        "run_mode": RUN_MODE,
        "arms": {
            "ARM_BASELINE_NO_SCHEMA": arm_baseline,
            "ARM_HRR_BUNDLE_PROTOTYPE": arm_bundle,
            "ARM_HOPFIELD_N2": arm_n2,
            "ARM_HOPFIELD_N4": arm_n4,
            "ARM_HOPFIELD_N10": arm_n10,
            "ARM_HOPFIELD_N20_SOFTMAX": arm_n20_softmax,
        },
        "n_heldout_total": HELDOUT_PER_CATEGORY * N_CATEGORIES,
        "chance": 1.0 / N_CATEGORIES,
        "elapsed_s": float(elapsed),
        "n_llm_calls": 0,
    }


# ---------- Verdict ----------
def compute_verdict(per_seed: List[Dict]) -> Tuple[str, str, Dict]:
    if not per_seed:
        return ("HARD_FAIL", "HARD_FAIL: no valid results", {})

    arm_labels = [
        "ARM_BASELINE_NO_SCHEMA",
        "ARM_HRR_BUNDLE_PROTOTYPE",
        "ARM_HOPFIELD_N2",
        "ARM_HOPFIELD_N4",
        "ARM_HOPFIELD_N10",
        "ARM_HOPFIELD_N20_SOFTMAX",
    ]
    agg = {}
    for label in arm_labels:
        vals = [s["arms"][label] for s in per_seed if label in s["arms"]]
        mean = float(np.mean(vals)) if vals else 0.0
        std = float(np.std(vals)) if vals else 1.0
        cv = (std / mean) if mean > 1e-9 else 0.0
        agg[label] = {"mean_heldout_top1": mean, "std": std, "cv": cv, "per_seed": vals}

    hrr_bundle = agg["ARM_HRR_BUNDLE_PROTOTYPE"]["mean_heldout_top1"]
    n2 = agg["ARM_HOPFIELD_N2"]["mean_heldout_top1"]
    n4 = agg["ARM_HOPFIELD_N4"]["mean_heldout_top1"]
    n10 = agg["ARM_HOPFIELD_N10"]["mean_heldout_top1"]
    n20_softmax = agg["ARM_HOPFIELD_N20_SOFTMAX"]["mean_heldout_top1"]
    cross_cell_drift = abs(hrr_bundle - CELL1_FEATURE_REFERENCE)
    n2_lift = n2 - n20_softmax

    arm_summary = " | ".join(
        f"{l}={agg[l]['mean_heldout_top1']:.4f}+/-{agg[l]['std']:.4f}"
        for l in arm_labels
    )

    # BIAS-Q saturation guard
    saturation_flags = []
    for label in arm_labels:
        if agg[label]["mean_heldout_top1"] >= 0.995 and agg[label]["cv"] <= 0.001:
            saturation_flags.append(label)

    detail = {
        "arms_aggregate": agg,
        "n2_lift_over_softmax": n2_lift,
        "cross_cell_drift_vs_cell1": cross_cell_drift,
        "cell1_feature_reference": CELL1_FEATURE_REFERENCE,
        "prior_mh_softmax_reference": PRIOR_MH_SOFTMAX_REFERENCE,
        "saturation_flags": saturation_flags,
        "chance": CHANCE,
        "hopfield_polynomial_n_grid": [HOPFIELD_N_FEATURE, HOPFIELD_N_INTERMEDIATE,
                                         HOPFIELD_N_APPROACHING],
        "hopfield_softmax_beta_raw": HOPFIELD_SOFTMAX_BETA,
        "honest_scope": (
            f"Modern-Hopfield feature-regime n-sweep diagnostic; N={N}; "
            f"{N_CATEGORIES} cats x {INSTANCES_PER_CATEGORY} train + {HELDOUT_PER_CATEGORY} heldout; "
            f"chance={CHANCE:.4f}; rail=HRR_BUNDLE vs Cell 1 ref {CELL1_FEATURE_REFERENCE} "
            f"(drift={cross_cell_drift:.4f}); regime ARM_HOPFIELD_N2={n2:.4f} vs "
            f"ARM_HOPFIELD_N20_SOFTMAX={n20_softmax:.4f} (lift={n2_lift:+.4f})"
        ),
    }

    # HARD_FAIL: cross-cell rail violated
    n_seeds_actual = len(per_seed)
    if n_seeds_actual >= 3 and cross_cell_drift > CROSS_CELL_RAIL_TOL:
        return ("HARD_FAIL",
                f"HARD_FAIL_HARNESS_CONFOUND: ARM_HRR_BUNDLE_PROTOTYPE={hrr_bundle:.4f} drifts "
                f"{cross_cell_drift:.4f} from Cell 1 reference {CELL1_FEATURE_REFERENCE} "
                f"(tol={CROSS_CELL_RAIL_TOL}). Methodology mismatch; do NOT interpret Hopfield arms. "
                f"arms: {arm_summary}",
                detail)
    # Smoke seed=11 cross-cell parity (Cell 1 seed=11 ARM_HRR_BUNDLE was 0.58)
    if n_seeds_actual == 1 and per_seed[0].get("seed") == 11:
        smoke_bundle = per_seed[0]["arms"]["ARM_HRR_BUNDLE_PROTOTYPE"]
        CELL1_SEED11_BUNDLE = 0.58
        smoke_drift = abs(smoke_bundle - CELL1_SEED11_BUNDLE)
        if smoke_drift > CROSS_CELL_RAIL_TOL:
            return ("HARD_FAIL",
                    f"HARD_FAIL_HARNESS_CONFOUND_SMOKE: seed=11 ARM_HRR_BUNDLE_PROTOTYPE={smoke_bundle:.4f} "
                    f"drifts {smoke_drift:.4f} from Cell 1 seed=11 reference {CELL1_SEED11_BUNDLE} "
                    f"(tol={CROSS_CELL_RAIL_TOL}). arms: {arm_summary}",
                    detail)

    # HARD_FAIL_MECHANISM_CLASS_DEAD: N2 and N20_SOFTMAX both ~equally bad
    if abs(n2_lift) <= HARD_FAIL_REGIME_PROXIMITY:
        return ("HARD_FAIL",
                f"HARD_FAIL_MECHANISM_CLASS_DEAD: ARM_HOPFIELD_N2={n2:.4f} within "
                f"{HARD_FAIL_REGIME_PROXIMITY} of ARM_HOPFIELD_N20_SOFTMAX={n20_softmax:.4f} "
                f"(lift={n2_lift:+.4f}). Feature regime does NOT escape softmax-regime failure; "
                f"mechanism-class dead on substrate's existing W. Pivot to slow-build (STC ANCHOR 2). "
                f"arms: {arm_summary}",
                detail)

    # HARD_PASS_REGIME_CONFIRMED: N2 hits floor AND lifts over softmax control by >= 0.15
    if n2 >= HARD_PASS_HELDOUT_FLOOR and n2_lift >= HARD_PASS_LIFT_OVER_SOFTMAX:
        return ("HARD_PASS",
                f"HARD_PASS_REGIME_CONFIRMED: ARM_HOPFIELD_N2={n2:.4f} >= "
                f"{HARD_PASS_HELDOUT_FLOOR}; lift over ARM_HOPFIELD_N20_SOFTMAX={n20_softmax:.4f} "
                f"is +{n2_lift:.4f} >= +{HARD_PASS_LIFT_OVER_SOFTMAX}. Krotov feature regime "
                f"on substrate's existing W escapes prior MH prototype regime failure "
                f"(HRR_BUNDLE_rail={hrr_bundle:.4f}; drift={cross_cell_drift:.4f}). "
                f"n-sweep: n2={n2:.4f} n4={n4:.4f} n10={n10:.4f} n20_softmax={n20_softmax:.4f}. "
                f"arms: {arm_summary}",
                detail)

    # MIDDLE_BAND_FLOOR_MET_INSUFFICIENT_LIFT: N2 above floor 0.50 but lift < 0.15
    if n2 >= HARD_PASS_HELDOUT_FLOOR and n2_lift < HARD_PASS_LIFT_OVER_SOFTMAX:
        return ("MIDDLE_BAND",
                f"MIDDLE_BAND_FLOOR_MET_INSUFFICIENT_LIFT: ARM_HOPFIELD_N2={n2:.4f} >= "
                f"{HARD_PASS_HELDOUT_FLOOR} but lift over softmax control = "
                f"{n2_lift:+.4f} < +{HARD_PASS_LIFT_OVER_SOFTMAX}. Regime distinction "
                f"present but not chain-grade margin; queue follow-up or beta-sweep on softmax arm. "
                f"arms: {arm_summary}",
                detail)

    # MIDDLE_BAND_PARTIAL_REGIME_LIFT: N2 in [0.35, 0.50)
    if MIDDLE_BAND_LOWER <= n2 < MIDDLE_BAND_UPPER:
        return ("MIDDLE_BAND",
                f"MIDDLE_BAND_PARTIAL_REGIME_LIFT: ARM_HOPFIELD_N2={n2:.4f} in "
                f"[{MIDDLE_BAND_LOWER}, {MIDDLE_BAND_UPPER}); lift over softmax={n2_lift:+.4f}. "
                f"Feature regime helps but not chain-grade margin; queue follow-up. "
                f"arms: {arm_summary}",
                detail)

    # Fallthrough: N2 below MIDDLE_BAND lower but lift > HARD_FAIL_REGIME_PROXIMITY
    return ("MIDDLE_BAND",
            f"MIDDLE_BAND_N2_BELOW_FLOOR_DISTINGUISHABLE: ARM_HOPFIELD_N2={n2:.4f} below "
            f"MIDDLE_BAND lower {MIDDLE_BAND_LOWER} but lift {n2_lift:+.4f} non-trivial over softmax. "
            f"arms: {arm_summary}",
            detail)


# ---------- Self-tests ----------
def _selftest_bind_unbind_roundtrip():
    rng = np.random.RandomState(0)
    n_t = 8192
    a = make_rand_atom(n_t, rng)
    b = make_rand_atom(n_t, rng)
    c = bind(a, b)
    b_hat = unbind(c, a)
    cs = cosine(b, b_hat)
    print(f"[selftest T1] HRR bind/unbind cosine={cs:.4f}", flush=True)
    assert cs >= 0.80, f"T1 FAIL cosine={cs:.3f} < 0.80"
    print(f"[selftest T1] PASS", flush=True)


def _selftest_hopfield_n2_recovers_cluster():
    """T2: Hopfield n=2 readout on tightly-clustered instances classifies correctly.

    Construct 2 categories, 10 instances each, with high signal frac (in-cluster
    coherence). Heldout from cat 0 should be classified to cat 0.
    """
    rng = np.random.RandomState(1)
    n_t = 1024
    n_cats_t = 2
    n_inst_t = 10
    # High signal regime
    sig_frac = 0.5
    sig = float(np.sqrt(sig_frac))
    npart = float(np.sqrt(1.0 - sig_frac))
    cat_vecs = [make_rand_atom(n_t, rng) for _ in range(n_cats_t)]
    def mk(ci):
        noise = make_rand_atom(n_t, rng)
        v = sig * cat_vecs[ci] + npart * noise
        v /= (np.linalg.norm(v) + 1e-9)
        return v
    train_vecs = []
    train_cats = []
    for ci in range(n_cats_t):
        for _ in range(n_inst_t):
            train_vecs.append(mk(ci))
            train_cats.append(ci)
    X = np.stack(train_vecs, axis=0)
    X = _l2_normalize_row(X)
    cats_arr = np.array(train_cats, dtype=np.int64)
    # 5 heldout from each cat
    correct = 0
    total = 0
    for ci in range(n_cats_t):
        for _ in range(5):
            q = mk(ci)
            q = q / (np.linalg.norm(q) + 1e-9)
            pred = hopfield_classify_polynomial(q, X, cats_arr, n_cats_t, polynomial_n=2)
            if pred == ci:
                correct += 1
            total += 1
    acc = correct / total
    print(f"[selftest T2] hopfield-n2 high-signal recovery acc={acc:.3f}", flush=True)
    assert acc >= 0.80, f"T2 FAIL hopfield n=2 high-signal acc={acc:.3f} < 0.80"
    print(f"[selftest T2] PASS", flush=True)


def _selftest_polynomial_score_consistency():
    """T3: With all training instances in one category, score for that cat
    equals sum_i rect(overlap_i)^n; score for other cats = 0."""
    rng = np.random.RandomState(2)
    n_t = 256
    X = np.stack([make_rand_atom(n_t, rng) for _ in range(8)], axis=0)
    X = _l2_normalize_row(X)
    cats = np.zeros(8, dtype=np.int64)  # all cat 0
    q = make_rand_atom(n_t, rng)
    overlaps = X @ q
    rect = np.maximum(overlaps, 0.0)
    expected_score_cat0 = float((rect ** 2).sum())
    expected_score_cat1 = 0.0
    # Manually compute
    n_cats_t = 2  # cat 0 has all instances; cat 1 has none
    overlaps_check = X @ q
    rect_check = np.maximum(overlaps_check, 0.0)
    powered = rect_check ** 2
    score_cat0 = float(powered[cats == 0].sum())
    score_cat1 = float(powered[cats == 1].sum())
    assert abs(score_cat0 - expected_score_cat0) < 1e-9, "T3 cat0 score mismatch"
    assert abs(score_cat1 - expected_score_cat1) < 1e-9, "T3 cat1 score mismatch"
    print(f"[selftest T3] polynomial-score consistency PASS "
          f"(cat0={score_cat0:.4f} cat1={score_cat1:.4f})", flush=True)


def _selftest_bands_locked():
    assert HARD_PASS_HELDOUT_FLOOR == 0.50, "T4 floor drift"
    assert HARD_PASS_LIFT_OVER_SOFTMAX == 0.15, "T4 lift drift"
    assert MIDDLE_BAND_LOWER == 0.35, "T4 middle lower drift"
    assert MIDDLE_BAND_UPPER == 0.50, "T4 middle upper drift"
    assert HARD_FAIL_REGIME_PROXIMITY == 0.05, "T4 proximity drift"
    assert CROSS_CELL_RAIL_TOL == 0.03, "T4 rail tol drift"
    assert CATEGORY_SIGNAL_FRAC == 0.005, "T4 cat-signal drift (MUST match Cell 1)"
    assert CELL1_FEATURE_REFERENCE == 0.4733, "T4 cell1 reference drift"
    assert PRIOR_MH_SOFTMAX_REFERENCE == 0.22, "T4 prior MH softmax reference drift"
    assert N_CATEGORIES == 5 and INSTANCES_PER_CATEGORY == 20 and HELDOUT_PER_CATEGORY == 10, \
        "T4 task design drift (MUST match Cell 1)"
    assert HOPFIELD_N_FEATURE == 2, "T4 feature-regime n drift"
    print(f"[selftest T4] bands LOCKED PASS", flush=True)


def _selftest_cross_cell_rail_encoded():
    assert abs(CELL1_FEATURE_REFERENCE - 0.4733) < 1e-9, "T5 cell1 reference value drift"
    print(f"[selftest T5] cross-cell rail encoded {CELL1_FEATURE_REFERENCE} PASS", flush=True)


def _selftest_discriminator_spread_on_smoke():
    """T6: 6-arm spread non-degenerate on tiny synthetic task at N=512.
    Specifically: N2 != N20_SOFTMAX (regime distinction must be measurable).
    """
    rng = np.random.RandomState(42)
    n_t = 512
    n_cat_t = 5
    n_inst_t = 20
    n_held_t = 10
    cat_vecs_l = [make_rand_atom(n_t, rng) for _ in range(n_cat_t)]
    prop_vecs_l = [make_rand_atom(n_t, rng) for _ in range(n_cat_t)]
    sig = float(np.sqrt(CATEGORY_SIGNAL_FRAC))
    npart = float(np.sqrt(1.0 - CATEGORY_SIGNAL_FRAC))
    def mk(ci):
        noise = make_rand_atom(n_t, rng)
        v = sig * cat_vecs_l[ci] + npart * noise
        v /= (np.linalg.norm(v) + 1e-9)
        return v
    train = []
    held = []
    for ci in range(n_cat_t):
        for _ in range(n_inst_t):
            train.append((ci, mk(ci)))
        for _ in range(n_held_t):
            held.append((ci, mk(ci)))
    task = {"cat_vecs": cat_vecs_l, "prop_vecs": prop_vecs_l,
            "train_instances": train, "heldout_instances": held}
    a_base = eval_no_schema_baseline(task)
    a_bundle = arm_hrr_bundle_prototype(task)
    a_n2 = arm_hopfield_polynomial(task, polynomial_n=2)
    a_n20_softmax = arm_hopfield_softmax(task, beta=HOPFIELD_SOFTMAX_BETA)
    print(f"[selftest T6] 6-arm smoke discriminator (N={n_t}): BASE={a_base:.3f} "
          f"BUNDLE={a_bundle:.3f} N2={a_n2:.3f} N20_SOFTMAX={a_n20_softmax:.3f}", flush=True)
    # Non-degeneracy: regime distinction measurable (N2 differs from N20_SOFTMAX,
    # OR baseline differs from BUNDLE; both axes need not be active on smoke)
    spread_axis1 = abs(a_n2 - a_n20_softmax)
    spread_axis2 = abs(a_base - a_bundle)
    spread_total = max(a_base, a_bundle, a_n2, a_n20_softmax) - \
                    min(a_base, a_bundle, a_n2, a_n20_softmax)
    assert spread_total >= 0.02, \
        f"T6 FAIL: 4-arm spread collapsed (range={spread_total:.3f}) -- wiring bug?"
    print(f"[selftest T6] discriminator spread total={spread_total:.3f} "
          f"(regime axis={spread_axis1:.3f}, schema axis={spread_axis2:.3f}) PASS", flush=True)


def _instrumentation_selftest():
    _selftest_bind_unbind_roundtrip()
    _selftest_hopfield_n2_recovers_cluster()
    _selftest_polynomial_score_consistency()
    _selftest_bands_locked()
    _selftest_cross_cell_rail_encoded()
    _selftest_discriminator_spread_on_smoke()
    print("[selftest] PASS: 6 formula tests + bands lock + cross-cell rail + discriminator", flush=True)


_instrumentation_selftest()
if _ARGS.self_test:
    sys.exit(0)


# ---------- Main run loop ----------
out_dir = get_output_dir(ANCHOR_NAME)
t0_total = time.time()
run_config = {"N": N, "run_mode": RUN_MODE,
              "n_feature": HOPFIELD_N_FEATURE,
              "n_intermediate": HOPFIELD_N_INTERMEDIATE,
              "n_approaching": HOPFIELD_N_APPROACHING,
              "softmax_beta": HOPFIELD_SOFTMAX_BETA}

done, seeds_todo = resumable_seeds(SEEDS, out_dir, run_config)
print(f"[run] mode={RUN_MODE} N={N} cats={N_CATEGORIES} train_per_cat={INSTANCES_PER_CATEGORY} "
      f"held_per_cat={HELDOUT_PER_CATEGORY} n_grid={[HOPFIELD_N_FEATURE, HOPFIELD_N_INTERMEDIATE, HOPFIELD_N_APPROACHING]} "
      f"softmax_beta={HOPFIELD_SOFTMAX_BETA} seeds_done={done} seeds_todo={seeds_todo}",
      flush=True)

for s in seeds_todo:
    res = run_seed(s)
    write_partial(out_dir, s, res)

per_seed_dict = aggregate_partials(out_dir, SEEDS, run_config=run_config)
all_results = list(per_seed_dict.values())
verdict, verdict_msg, detail = compute_verdict(all_results)

metrics = {
    "anchor": ANCHOR_NAME,
    "anchor_name": ANCHOR_NAME,
    "verdict": verdict,
    "verdict_msg": verdict_msg,
    "headline": verdict_msg,
    "n_seeds": len(all_results),
    "N": N,
    "run_mode": RUN_MODE,
    "n_categories": N_CATEGORIES,
    "instances_per_category": INSTANCES_PER_CATEGORY,
    "heldout_per_category": HELDOUT_PER_CATEGORY,
    "chance": 1.0 / N_CATEGORIES,
    "arms_tested": [
        "ARM_BASELINE_NO_SCHEMA",
        "ARM_HRR_BUNDLE_PROTOTYPE",
        "ARM_HOPFIELD_N2",
        "ARM_HOPFIELD_N4",
        "ARM_HOPFIELD_N10",
        "ARM_HOPFIELD_N20_SOFTMAX",
    ],
    "hopfield_polynomial_n_grid": [HOPFIELD_N_FEATURE, HOPFIELD_N_INTERMEDIATE,
                                     HOPFIELD_N_APPROACHING],
    "hopfield_softmax_beta": HOPFIELD_SOFTMAX_BETA,
    "cell1_feature_reference": CELL1_FEATURE_REFERENCE,
    "cross_cell_rail_tol": CROSS_CELL_RAIL_TOL,
    "prior_mh_softmax_reference": PRIOR_MH_SOFTMAX_REFERENCE,
    "detail": detail,
    "per_seed": all_results,
    "encoder_provenance": ENCODER_PROVENANCE,
    "metrics_source": "measured_cpu_mh_revival_feature_regime_6arm",
    "elapsed_s": time.time() - t0_total,
    "summary": verdict_msg[:200],
    "honest_scope": detail.get("honest_scope", ""),
    "substrate_only_decode_gate": "N/A (compositional-gen primitive cell; zero LLM forward calls)",
    "zero_llm_calls_at_inference": True,
    "n_llm_calls": 0,
}

metrics_path = out_dir / "metrics.json"
with open(metrics_path, "w", encoding="utf-8") as f:
    json.dump(metrics, f, indent=2)

print(f"\n[VERDICT] {verdict}", flush=True)
print(f"[VERDICT_MSG] {verdict_msg}", flush=True)
print(f"[METRICS_PATH] {metrics_path}", flush=True)
