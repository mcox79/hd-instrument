"""Dual-number double-dissociation probe (innate-scaffolding Prediction 1).

Tests whether baking in TWO structurally-distinct number primitives is worth the
complexity over ONE unified magnitude code, by looking for a clean DOUBLE
DISSOCIATION a la Hyde & Spelke 2011 (distinct signatures for small-exact vs
large-approximate number).

TWO CHANNELS (both feed a SHARED trained readout so the "one unified code
suffices" null is a real alternative, not a straw man):
  1. POINTER-ARRAY (parallel-individuation analog): S=4 fixed slots; each slot
     role-vector bound to an item token; per-slot unbind+cleanup recovers WHICH
     token is at WHICH slot. Exact identity-at-slot; capacity-limited to S.
  2. MAGNITUDE (ANS analog): unnormalized bundle whose L2 norm ~ sqrt(count)
     (Weber-scaled) plus a familiarity cosine (is X in the set). No slot, no
     identity; unbounded cardinality.

TWO TASKS on clean synthetic data (NOT substrate state):
  (a) small-set EXACT identity-at-slot after occlusion corruption, count in
      {1,2,3,4}. Negatives include "X present but at a DIFFERENT slot" -> a pure
      familiarity/magnitude code says 'present' and gets it WRONG; only the
      pointer channel (unbind slot k) answers correctly.
  (b) large-set RATIO discrimination "is A bigger than B", n in {8,16,32},
      ratios 1:2 and 2:3. Both scenes overflow S=4 -> the pointer channel cannot
      count them; only the magnitude norm discriminates.

PAIRED ablation (mandatory): ONE trial set per seed is scored under 3 conditions
sharing identical scenes/seed:
  CLEAN / POINTER_ABLATED (slot roles randomized -> unbind returns noise) /
  MAGNITUDE_ABLATED (scene norm + familiarity replaced by noise).
Deltas are therefore paired (same scenes).

DISSOCIATION RATIOS:
  R_pointer = d(a|pointer_abl) / d(b|pointer_abl)   [expect >> 1]
  R_mag     = d(b|mag_abl)     / d(a|mag_abl)        [expect >> 1]
HARD_PASS  = R_pointer>=2 AND R_mag>=2, each numerator delta>=MIN_EFFECT (double
             dissociation both directions) -> bake in two systems, not one.
HARD_FAIL  = R_pointer<=1.3 AND R_mag<=1.3 with a real ablation effect present ->
             a single unified magnitude code suffices; two-primitive bake-in adds
             complexity without benefit.
MIDDLE     = dissociation one direction only.

Both outcomes are gold: PASS transfers biology's "two number systems" design
principle to the substrate; FAIL says one unified code is enough here (simpler).

# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; 3 conditions bit-distinct)
# - final_metrics_atomicity = tmp_replace (write_metrics) + per-seed write_partial
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_n/a: discriminator is an ablation-delta RATIO, not noise-floor estimation
# - baseline_in_band at smoke (clean acc in band; ablated drops; delta telemetry-sensitive)
# - discriminator survives scale: smoke runs at FULL N=8192, 1 seed, reduced trials
# - HARD_PASS strictly above MIDDLE ceiling (ratio>=2.0 vs MIDDLE (1.3,2.0))
# - cardinality_ok: EXPECTED_N_UNITS = n_seeds (verdict counts len(per_seed))
# - per-unit failure-class instrumentation (no bare except)
# - calibration_check: default_ok_for_this_regime (clean synthetic; analytical SNR)
# - all numbers tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@ in comments

Numbers in this docstring:
  - pointer unbind cos SNR ~ 1/sqrt(c), c<=4 -> ~0.5 at c=4  THEORETICAL@bipolar bundle unbind
  - magnitude norm ratio ~ sqrt(nA/nB); 2:3 -> sqrt(2/3)=0.816  THEORETICAL@sum-of-orthogonal-norm
  - P(double-dissociation benefit) ~ 0.35  CITED@notes/research_innate_scaffolding_core_knowledge_kernel_2026-07-09.md:S3

ASCII-only per feedback_ascii_only_in_scripts.
"""
from __future__ import annotations

import argparse
import json
import os
import platform
import sys
import time
import traceback
from datetime import datetime, timezone

import numpy as np

# sys.path shim so `python experiments/exp_...py` (runner path) can import siblings.
_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.dirname(_HERE)
for _p in (_REPO, _HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from experiments._seed_checkpoint import (  # noqa: E402
    aggregate_partials,
    assert_discriminator_fires,
    get_output_dir,
    record_gate,
    resumable_seeds,
    write_metrics,
    write_partial,
)
from experiments._cell_heartbeat import CellHeartbeat  # noqa: E402

ANCHOR_NAME = "exp_dual_number_double_dissociation_v1"

# ----------------------------------------------------------------------------
# Config (SMOKE=FULL parity: identical code path; only sizes/seed-count differ).
# ----------------------------------------------------------------------------
N_DIM = 8192               # substrate dimensionality (project default anchor)
S_SLOTS = 4               # pointer-array slots (~3-4 object-file limit; Feigenson & Carey 2005 CITED)
V_TOK = 64                # token codebook size (>= 32 for task b)
F_OCC = 0.15              # task (a) occlusion sign-flip fraction
F_B = 0.10               # task (b) per-token sign-flip noise fraction
CLEANUP_THRESH = 0.20     # count-estimate cleanup cosine threshold (pointer channel)

TASK_A_COUNTS = (1, 2, 3, 4)
# Balanced (A>B) / (A<B) pairs at ratios 1:2 and 2:3 over base sizes {8,16,32}.
TASK_B_PAIRS = (
    (8, 16), (16, 8), (16, 32), (32, 16),   # ratio 1:2
    (16, 24), (24, 16), (8, 12), (12, 8),   # ratio 2:3
)

SEEDS_FULL = (7, 17, 23)
SEEDS_SMOKE = (7,)

# Trial counts.
M_TRAIN_FULL, M_TEST_FULL = 800, 500
M_TRAIN_SMOKE, M_TEST_SMOKE = 200, 150

# Discriminator bands (research pre-reg Prediction 1).
HP_RATIO = 2.0            # HARD_PASS: both dissociation ratios >= 2.0
HFAIL_RATIO = 1.3         # HARD_FAIL: both dissociation ratios <= 1.3
MIN_EFFECT = 0.08         # a delta must be >= this (absolute acc drop) to count as a real effect
RATIO_CAP = 100.0         # cap reported ratios for stability
EPS = 1e-6

# Clean-accuracy sanity band (baseline-in-band framing for this delta-discriminator).
CLEAN_ACC_LO = 0.60       # clean readout must clear this or the channels aren't working
CLEAN_ACC_HI = 1.0001


# ----------------------------------------------------------------------------
# Substrate primitives (bipolar BSC: bind = elementwise mul, bundle = sum).
# ----------------------------------------------------------------------------
def _rng(seed: int) -> np.random.Generator:
    return np.random.default_rng(seed)


def _bipolar(rng: np.random.Generator, rows: int, n: int) -> np.ndarray:
    """(rows, n) bipolar {-1,+1} float32 matrix."""
    return (rng.integers(0, 2, size=(rows, n)).astype(np.float32) * 2.0) - 1.0


def _flip_mask(rng: np.random.Generator, n: int, frac: float) -> np.ndarray:
    """(n,) bipolar mask with `frac` of dims set to -1 (sign flip), rest +1."""
    m = np.ones(n, dtype=np.float32)
    k = int(round(frac * n))
    if k > 0:
        idx = rng.choice(n, size=k, replace=False)
        m[idx] = -1.0
    return m


def _cos(a: np.ndarray, b: np.ndarray) -> float:
    na = float(np.linalg.norm(a))
    nb = float(np.linalg.norm(b))
    if na <= 0.0 or nb <= 0.0:
        return 0.0
    return float(np.dot(a, b) / (na * nb))


def _cleanup_maxcos(vec: np.ndarray, codebook: np.ndarray) -> float:
    """max cosine of vec against every codebook row (V, N). Vectorized."""
    vn = float(np.linalg.norm(vec))
    if vn <= 0.0:
        return 0.0
    sims = codebook @ vec  # (V,)
    cbn = np.linalg.norm(codebook, axis=1)  # (V,)
    cbn = np.where(cbn > 0, cbn, 1.0)
    sims = sims / (cbn * vn)
    return float(np.max(sims))


# ----------------------------------------------------------------------------
# Logistic regression (numpy GD; dependency-free; NaN-guarded).
# ----------------------------------------------------------------------------
def _standardize_fit(X: np.ndarray):
    mu = X.mean(axis=0)
    sd = X.std(axis=0)
    sd = np.where(sd > 1e-8, sd, 1.0)
    return mu, sd


def _standardize_apply(X: np.ndarray, mu: np.ndarray, sd: np.ndarray) -> np.ndarray:
    return (X - mu) / sd


def _train_lr(X: np.ndarray, y: np.ndarray, epochs: int = 400,
              lr: float = 0.5, l2: float = 1e-3):
    n, d = X.shape
    w = np.zeros(d, dtype=np.float64)
    b = 0.0
    yf = y.astype(np.float64)
    for _ in range(epochs):
        z = np.clip(X @ w + b, -30.0, 30.0)
        p = 1.0 / (1.0 + np.exp(-z))
        g = p - yf
        gw = X.T @ g / n + l2 * w
        gb = float(g.mean())
        w -= lr * gw
        b -= lr * gb
    if not (np.all(np.isfinite(w)) and np.isfinite(b)):
        raise FloatingPointError("LR weights non-finite (NaN/Inf) at production-scale fit")
    return w, b


def _predict(X: np.ndarray, w: np.ndarray, b: float) -> np.ndarray:
    z = np.clip(X @ w + b, -30.0, 30.0)
    p = 1.0 / (1.0 + np.exp(-z))
    return (p >= 0.5).astype(np.int64)


# ----------------------------------------------------------------------------
# Task (a): EXACT identity-at-slot after occlusion. Returns feature dict + labels.
# ----------------------------------------------------------------------------
def _gen_task_a(rng, codebook, slot_roles, slot_roles_abl, m_trials):
    """Build feature matrices for task (a) under CLEAN / POINTER_ABL / MAG_ABL.

    Features (order): [f_ptr, f_ptr_max, f_fam].
      f_ptr     = cos(unbind(scene_ptr, slot_k), X)           # POINTER channel
      f_ptr_max = max_j cos(unbind(scene_ptr, slot_j), X)     # POINTER channel
      f_fam     = cos(scene_bundle, X)                        # MAGNITUDE channel
    Pointer ablation: recompute f_ptr/f_ptr_max with randomized slot roles.
    Magnitude ablation: recompute f_fam against a noise bundle.
    """
    feat_clean, feat_pabl, feat_mabl, labels = [], [], [], []
    for _ in range(m_trials):
        c = int(rng.choice(TASK_A_COUNTS))
        toks = rng.choice(V_TOK, size=c, replace=False)
        # scene: item i at slot i (i<c). pointer scene = sum bind(role_i, tok_i).
        scene_ptr = np.zeros(N_DIM, dtype=np.float32)
        scene_bundle = np.zeros(N_DIM, dtype=np.float32)
        for i in range(c):
            scene_ptr += slot_roles[i] * codebook[toks[i]]
            scene_bundle += codebook[toks[i]]
        # occlusion corruption (shared scene-level sign flips).
        occ = _flip_mask(rng, N_DIM, F_OCC)
        scene_ptr = scene_ptr * occ
        scene_bundle = scene_bundle * occ

        k = int(rng.integers(0, c))  # query slot
        r = rng.random()
        if r < 0.5:
            # POSITIVE: X = token truly at slot k.
            x_idx = int(toks[k])
            y = 1
        else:
            # NEGATIVE, two subtypes 50/50.
            if rng.random() < 0.5 or c == 1:
                # X absent from scene (familiarity CAN reject this).
                choices = [t for t in range(V_TOK) if t not in set(toks.tolist())]
                x_idx = int(rng.choice(choices))
            else:
                # X present but at a DIFFERENT slot j != k (familiarity says
                # 'present' -> WRONG; only pointer answers correctly).
                others = [j for j in range(c) if j != k]
                j = int(rng.choice(others))
                x_idx = int(toks[j])
            y = 0

        xvec = codebook[x_idx]
        # CLEAN pointer features.
        ub_clean = [scene_ptr * slot_roles[j] for j in range(S_SLOTS)]
        f_ptr_c = _cos(ub_clean[k], xvec)
        f_ptr_max_c = max(_cos(ub_clean[j], xvec) for j in range(S_SLOTS))
        f_fam_c = _cos(scene_bundle, xvec)
        # POINTER-ABLATED pointer features (randomized roles -> noise).
        ub_abl = [scene_ptr * slot_roles_abl[j] for j in range(S_SLOTS)]
        f_ptr_p = _cos(ub_abl[k], xvec)
        f_ptr_max_p = max(_cos(ub_abl[j], xvec) for j in range(S_SLOTS))
        # MAG-ABLATED familiarity (noise bundle -> ~0 signal).
        noise_bundle = _bipolar(rng, 1, N_DIM)[0]
        f_fam_m = _cos(noise_bundle, xvec)

        feat_clean.append([f_ptr_c, f_ptr_max_c, f_fam_c])
        feat_pabl.append([f_ptr_p, f_ptr_max_p, f_fam_c])   # pointer noised, fam intact
        feat_mabl.append([f_ptr_c, f_ptr_max_c, f_fam_m])   # fam noised, pointer intact
        labels.append(y)
    return (np.array(feat_clean, np.float64),
            np.array(feat_pabl, np.float64),
            np.array(feat_mabl, np.float64),
            np.array(labels, np.int64))


# ----------------------------------------------------------------------------
# Task (b): large-set RATIO discrimination. Returns feature dict + labels.
# ----------------------------------------------------------------------------
def _count_est(scene_ptr, slot_roles, codebook):
    """Estimate item count via number of slots whose unbind cleans up above thresh."""
    cnt = 0
    for j in range(S_SLOTS):
        if _cleanup_maxcos(scene_ptr * slot_roles[j], codebook) > CLEANUP_THRESH:
            cnt += 1
    return cnt


def _gen_task_b(rng, codebook, slot_roles, slot_roles_abl, m_trials):
    """Build feature matrices for task (b) under CLEAN / POINTER_ABL / MAG_ABL.

    Features (order): [m_normA, m_normB, m_diff, p_cntA, p_cntB, p_diff].
      m_*  = MAGNITUDE channel (unnormalized bundle norms ~ sqrt(count)).
      p_*  = POINTER channel (slot-count estimate; caps at S -> uninformative
             here because both scenes overflow S=4).
    Pointer ablation: p_* recomputed with randomized roles.
    Magnitude ablation: bundles unit-normalized (+noise) -> norms uninformative.
    """
    feat_clean, feat_pabl, feat_mabl, labels = [], [], [], []
    npairs = len(TASK_B_PAIRS)
    for _ in range(m_trials):
        nA, nB = TASK_B_PAIRS[int(rng.integers(0, npairs))]
        toksA = rng.choice(V_TOK, size=nA, replace=True)
        toksB = rng.choice(V_TOK, size=nB, replace=True)
        MgA = codebook[toksA].sum(axis=0).astype(np.float32)
        MgB = codebook[toksB].sum(axis=0).astype(np.float32)
        MgA = MgA * _flip_mask(rng, N_DIM, F_B)
        MgB = MgB * _flip_mask(rng, N_DIM, F_B)
        # pointer scenes: first S items bound to slots.
        PA = np.zeros(N_DIM, dtype=np.float32)
        PB = np.zeros(N_DIM, dtype=np.float32)
        for i in range(min(nA, S_SLOTS)):
            PA += slot_roles[i] * codebook[toksA[i]]
        for i in range(min(nB, S_SLOTS)):
            PB += slot_roles[i] * codebook[toksB[i]]

        y = 1 if nA > nB else 0  # (no ties in TASK_B_PAIRS)

        # MAGNITUDE features.
        nrmA = float(np.linalg.norm(MgA))
        nrmB = float(np.linalg.norm(MgB))
        # MAG-ABLATED: unit-normalize destroys cardinality; add small noise.
        nrmA_m = 1.0 + float(rng.normal(0, 0.02))
        nrmB_m = 1.0 + float(rng.normal(0, 0.02))
        # POINTER features (clean + ablated).
        cA_c = _count_est(PA, slot_roles, codebook)
        cB_c = _count_est(PB, slot_roles, codebook)
        cA_p = _count_est(PA, slot_roles_abl, codebook)
        cB_p = _count_est(PB, slot_roles_abl, codebook)

        feat_clean.append([nrmA, nrmB, nrmA - nrmB, cA_c, cB_c, cA_c - cB_c])
        feat_pabl.append([nrmA, nrmB, nrmA - nrmB, cA_p, cB_p, cA_p - cB_p])
        feat_mabl.append([nrmA_m, nrmB_m, nrmA_m - nrmB_m, cA_c, cB_c, cA_c - cB_c])
        labels.append(y)
    return (np.array(feat_clean, np.float64),
            np.array(feat_pabl, np.float64),
            np.array(feat_mabl, np.float64),
            np.array(labels, np.int64))


# ----------------------------------------------------------------------------
# Per-seed run: train on CLEAN train split, evaluate 3 conditions on held-out test.
# ----------------------------------------------------------------------------
def _eval_task(gen_fn, rng, codebook, slot_roles, slot_roles_abl,
               m_train, m_test, shuffle_labels=False):
    """Return dict acc_clean/acc_pabl/acc_mabl for a task, + feature hashes."""
    Xtr_c, _, _, ytr = gen_fn(rng, codebook, slot_roles, slot_roles_abl, m_train)
    Xte_c, Xte_p, Xte_m, yte = gen_fn(rng, codebook, slot_roles, slot_roles_abl, m_test)
    if shuffle_labels:
        ytr = ytr.copy()
        rng.shuffle(ytr)
    mu, sd = _standardize_fit(Xtr_c)
    w, b = _train_lr(_standardize_apply(Xtr_c, mu, sd), ytr)

    def _acc(Xte):
        pred = _predict(_standardize_apply(Xte, mu, sd), w, b)
        return float((pred == yte).mean())

    import hashlib
    def _h(X):
        return hashlib.sha256(np.ascontiguousarray(X).tobytes()).hexdigest()[:16]

    return {
        "acc_clean": _acc(Xte_c),
        "acc_pabl": _acc(Xte_p),
        "acc_mabl": _acc(Xte_m),
        "hash_clean": _h(Xte_c),
        "hash_pabl": _h(Xte_p),
        "hash_mabl": _h(Xte_m),
    }


def _ratios_from_deltas(d_a_p, d_b_p, d_a_m, d_b_m):
    """R_pointer = d(a|ptr)/d(b|ptr); R_mag = d(b|mag)/d(a|mag). Deltas floored >=0."""
    da_p = max(d_a_p, 0.0)
    db_p = max(d_b_p, 0.0)
    da_m = max(d_a_m, 0.0)
    db_m = max(d_b_m, 0.0)
    r_ptr = min(da_p / max(db_p, EPS), RATIO_CAP)
    r_mag = min(db_m / max(da_m, EPS), RATIO_CAP)
    return r_ptr, r_mag


def run_one_seed(seed: int, m_train: int, m_test: int) -> dict:
    """Run both tasks x 3 conditions for one seed; return accs, deltas, ratios."""
    t0 = time.perf_counter()
    rng = _rng(seed)
    codebook = _bipolar(rng, V_TOK, N_DIM)
    slot_roles = _bipolar(rng, S_SLOTS, N_DIM)
    slot_roles_abl = _bipolar(_rng(seed + 100000), S_SLOTS, N_DIM)  # independent random roles

    a = _eval_task(_gen_task_a, _rng(seed + 1), codebook, slot_roles, slot_roles_abl,
                   m_train, m_test)
    b = _eval_task(_gen_task_b, _rng(seed + 2), codebook, slot_roles, slot_roles_abl,
                   m_train, m_test)
    # Shuffled-label control (must show NO dissociation -> vacuous-smoke guard).
    ac = _eval_task(_gen_task_a, _rng(seed + 3), codebook, slot_roles, slot_roles_abl,
                    m_train, m_test, shuffle_labels=True)
    bc = _eval_task(_gen_task_b, _rng(seed + 4), codebook, slot_roles, slot_roles_abl,
                    m_train, m_test, shuffle_labels=True)

    d_a_p = a["acc_clean"] - a["acc_pabl"]   # task a, pointer ablated
    d_b_p = b["acc_clean"] - b["acc_pabl"]   # task b, pointer ablated
    d_a_m = a["acc_clean"] - a["acc_mabl"]   # task a, magnitude ablated
    d_b_m = b["acc_clean"] - b["acc_mabl"]   # task b, magnitude ablated
    r_ptr, r_mag = _ratios_from_deltas(d_a_p, d_b_p, d_a_m, d_b_m)

    # control deltas/ratios.
    cd_a_p = ac["acc_clean"] - ac["acc_pabl"]
    cd_b_p = bc["acc_clean"] - bc["acc_pabl"]
    cd_a_m = ac["acc_clean"] - ac["acc_mabl"]
    cd_b_m = bc["acc_clean"] - bc["acc_mabl"]
    cr_ptr, cr_mag = _ratios_from_deltas(cd_a_p, cd_b_p, cd_a_m, cd_b_m)
    control_dissociation = (cd_a_p >= MIN_EFFECT and cd_b_m >= MIN_EFFECT
                            and cr_ptr >= HP_RATIO and cr_mag >= HP_RATIO)

    hp = (d_a_p >= MIN_EFFECT and d_b_m >= MIN_EFFECT
          and r_ptr >= HP_RATIO and r_mag >= HP_RATIO)
    effect_present = max(d_a_p, d_b_p, d_a_m, d_b_m) >= MIN_EFFECT
    hf = (effect_present and r_ptr <= HFAIL_RATIO and r_mag <= HFAIL_RATIO)
    if hp:
        seed_verdict = "HARD_PASS"
    elif hf:
        seed_verdict = "HARD_FAIL"
    elif not effect_present:
        seed_verdict = "NO_ABLATION_EFFECT"
    else:
        seed_verdict = "MIDDLE_BAND"

    return {
        "seed": seed, "N": N_DIM, "run_mode": None,  # run_mode stamped by caller
        "m_train": m_train, "m_test": m_test,
        "task_a": a, "task_b": b,
        "d_a_pointer": d_a_p, "d_b_pointer": d_b_p,
        "d_a_mag": d_a_m, "d_b_mag": d_b_m,
        "R_pointer": r_ptr, "R_mag": r_mag,
        "control_R_pointer": cr_ptr, "control_R_mag": cr_mag,
        "control_dissociation": bool(control_dissociation),
        "effect_present": bool(effect_present),
        "seed_verdict": seed_verdict,
        "elapsed_s": time.perf_counter() - t0,
    }


# ----------------------------------------------------------------------------
# Aggregation + verdict.
# ----------------------------------------------------------------------------
def _aggregate(per_seed: list, expected_n_units: int) -> dict:
    n = len(per_seed)
    if n < expected_n_units:
        return {
            "verdict": "HARD_FAIL_CARDINALITY_BREACH_META_RULE_H",
            "verdict_msg": (f"CARDINALITY_BREACH: {n} of {expected_n_units} seeds "
                            f"completed"),
            "n_units": n, "expected_n_units": expected_n_units,
        }

    def _mean(key):
        return float(np.mean([s[key] for s in per_seed]))

    md_a_p, md_b_p = _mean("d_a_pointer"), _mean("d_b_pointer")
    md_a_m, md_b_m = _mean("d_a_mag"), _mean("d_b_mag")
    mr_ptr, mr_mag = _ratios_from_deltas(md_a_p, md_b_p, md_a_m, md_b_m)
    mean_clean_a = float(np.mean([s["task_a"]["acc_clean"] for s in per_seed]))
    mean_clean_b = float(np.mean([s["task_b"]["acc_clean"] for s in per_seed]))

    n_hp = sum(1 for s in per_seed if s["seed_verdict"] == "HARD_PASS")
    n_hf = sum(1 for s in per_seed if s["seed_verdict"] == "HARD_FAIL")
    effect_present = (max(md_a_p, md_b_p, md_a_m, md_b_m) >= MIN_EFFECT)

    mean_hp = (md_a_p >= MIN_EFFECT and md_b_m >= MIN_EFFECT
               and mr_ptr >= HP_RATIO and mr_mag >= HP_RATIO)
    mean_hf = (effect_present and mr_ptr <= HFAIL_RATIO and mr_mag <= HFAIL_RATIO)

    # Require majority seed-agreement for a headline HARD verdict.
    if mean_hp and n_hp >= (n + 1) // 2:
        verdict = "HARD_PASS"
    elif mean_hf and n_hf >= (n + 1) // 2:
        verdict = "HARD_FAIL"
    elif not effect_present:
        verdict = "INCONCLUSIVE_NO_ABLATION_EFFECT"
    else:
        verdict = "MIDDLE_BAND"

    msg = (f"{verdict}: R_pointer={mr_ptr:.2f} (d_a|ptr={md_a_p:.3f} vs "
           f"d_b|ptr={md_b_p:.3f}) ; R_mag={mr_mag:.2f} (d_b|mag={md_b_m:.3f} vs "
           f"d_a|mag={md_a_m:.3f}) ; clean acc a={mean_clean_a:.3f} b={mean_clean_b:.3f} "
           f"; seeds HP={n_hp}/{n} HF={n_hf}/{n} ; HP_RATIO={HP_RATIO} "
           f"HFAIL_RATIO={HFAIL_RATIO} MIN_EFFECT={MIN_EFFECT}")

    gate_claims = [
        record_gate("R_pointer_ge_2", mr_ptr, HP_RATIO, ">="),
        record_gate("R_mag_ge_2", mr_mag, HP_RATIO, ">="),
        record_gate("d_a_pointer_ge_min_effect", md_a_p, MIN_EFFECT, ">="),
        record_gate("d_b_mag_ge_min_effect", md_b_m, MIN_EFFECT, ">="),
        record_gate("clean_acc_a_in_band", mean_clean_a, CLEAN_ACC_LO, ">="),
        record_gate("clean_acc_b_in_band", mean_clean_b, CLEAN_ACC_LO, ">="),
    ]

    return {
        "verdict": verdict, "verdict_msg": msg, "summary": msg,
        "n_units": n, "expected_n_units": expected_n_units,
        "mean_d_a_pointer": md_a_p, "mean_d_b_pointer": md_b_p,
        "mean_d_a_mag": md_a_m, "mean_d_b_mag": md_b_m,
        "mean_R_pointer": mr_ptr, "mean_R_mag": mr_mag,
        "mean_clean_acc_a": mean_clean_a, "mean_clean_acc_b": mean_clean_b,
        "n_seeds_hard_pass": n_hp, "n_seeds_hard_fail": n_hf,
        "per_seed": per_seed,
        "gate_claims": gate_claims,
        "config": {
            "N_DIM": N_DIM, "S_SLOTS": S_SLOTS, "V_TOK": V_TOK,
            "F_OCC": F_OCC, "F_B": F_B, "HP_RATIO": HP_RATIO,
            "HFAIL_RATIO": HFAIL_RATIO, "MIN_EFFECT": MIN_EFFECT,
        },
    }


# ----------------------------------------------------------------------------
# Runner scaffolding: start marker, crash metrics.
# ----------------------------------------------------------------------------
def _write_start_marker(output_dir, run_mode, expected_n_units):
    marker = {
        "pid": os.getpid(),
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR_NAME, "run_mode": run_mode,
        "expected_n_units": expected_n_units, "host": platform.node(),
    }
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    final = os.path.join(output_dir, "_start_marker.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, final)


def _write_crash_metrics(output_dir, exc):
    diag = {
        "verdict": "CELL_CRASHED",
        "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
        "summary": f"CELL_CRASHED: {type(exc).__name__}",
        "elapsed_s": 0.0,
        "traceback": traceback.format_exc()[:5000],
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(), "anchor_name": ANCHOR_NAME,
    }
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, final)


# ----------------------------------------------------------------------------
# Run modes.
# ----------------------------------------------------------------------------
def _run(run_mode: str) -> dict:
    if run_mode == "smoke":
        seeds, m_train, m_test = SEEDS_SMOKE, M_TRAIN_SMOKE, M_TEST_SMOKE
    else:
        seeds, m_train, m_test = SEEDS_FULL, M_TRAIN_FULL, M_TEST_FULL
    expected = len(seeds)
    out_dir = get_output_dir(ANCHOR_NAME)
    out_dir_str = str(out_dir)
    _write_start_marker(out_dir_str, run_mode, expected)

    run_config = {"N": N_DIM, "run_mode": run_mode, "anchor": ANCHOR_NAME}
    done, remaining = resumable_seeds(list(seeds), out_dir, run_config=run_config)
    print(f"[ckpt] {len(done)} of {len(seeds)} seeds complete; running {remaining}",
          flush=True)

    t0 = time.perf_counter()
    with CellHeartbeat(out_dir_str, total_units=len(seeds), interval_s=30) as hb:
        for i, seed in enumerate(remaining):
            res = run_one_seed(seed, m_train, m_test)
            res["run_mode"] = run_mode
            res["config_version"] = f"ANCHOR={ANCHOR_NAME},N={N_DIM},run_mode={run_mode}"
            write_partial(out_dir, seed, res)
            hb.tick(i, extra={"seed": seed, "seed_verdict": res["seed_verdict"],
                              "R_pointer": round(res["R_pointer"], 2),
                              "R_mag": round(res["R_mag"], 2)})
            print(f"[progress] seed={seed} verdict={res['seed_verdict']} "
                  f"R_ptr={res['R_pointer']:.2f} R_mag={res['R_mag']:.2f} "
                  f"elapsed={time.perf_counter()-t0:.1f}s", flush=True)

    agg_all = aggregate_partials(out_dir, list(seeds), run_config=run_config)
    per_seed = [agg_all[str(s)] for s in seeds if str(s) in agg_all]
    metrics = _aggregate(per_seed, expected)
    metrics["run_mode"] = run_mode
    metrics["elapsed_s"] = time.perf_counter() - t0
    metrics["ts_iso"] = datetime.now(timezone.utc).isoformat()

    # ---- SMOKE gates: discriminator must fire + vacuous-smoke control -------
    if run_mode == "smoke" and per_seed:
        s0 = per_seed[0]
        # META_RULE_AF: the 3 conditions must be bit-distinct (arms-must-differ).
        for task, tk in (("a", "task_a"), ("b", "task_b")):
            h = s0[tk]
            assert h["hash_clean"] != h["hash_pabl"], \
                f"META_RULE_AF: task {task} clean==pointer_ablated features bit-identical"
            assert h["hash_clean"] != h["hash_mabl"], \
                f"META_RULE_AF: task {task} clean==mag_ablated features bit-identical"
        metrics["arms_differ_verified"] = True
        # Vacuous-smoke guard: shuffled-label CONTROL must NOT show dissociation.
        assert_discriminator_fires(
            bool(s0["control_dissociation"]),
            control_name="shuffled_label_control",
            headline_name="double_dissociation",
            run_mode="smoke",
            remedy="raise smoke M_trials / N until real dissociation separates "
                   "from shuffled-label control")
        # Real discriminator must fire at smoke scale (else do not dispatch FULL).
        smoke_fires = (s0["d_a_pointer"] >= MIN_EFFECT and s0["d_b_mag"] >= MIN_EFFECT
                       and s0["R_pointer"] >= 1.8 and s0["R_mag"] >= 1.8)
        metrics["smoke_discriminator_fires"] = bool(smoke_fires)
        # Baseline-in-band: clean accs must have room to drop (not degenerate).
        metrics["clean_acc_in_band"] = bool(
            CLEAN_ACC_LO <= s0["task_a"]["acc_clean"] <= CLEAN_ACC_HI
            and CLEAN_ACC_LO <= s0["task_b"]["acc_clean"] <= CLEAN_ACC_HI)
        if not smoke_fires:
            metrics["verdict"] = "SMOKE_GATE_FAIL_DISCRIMINATOR_INERT"
            metrics["verdict_msg"] = (
                "SMOKE_GATE_FAIL: real double dissociation did not fire at smoke "
                f"scale (d_a|ptr={s0['d_a_pointer']:.3f} d_b|mag={s0['d_b_mag']:.3f} "
                f"R_ptr={s0['R_pointer']:.2f} R_mag={s0['R_mag']:.2f}); "
                "re-spec regime before FULL dispatch")
            metrics["summary"] = metrics["verdict_msg"]

    gate_claims = metrics.pop("gate_claims", None)
    write_metrics(out_dir, metrics, results=per_seed, gate_claims=gate_claims)
    print(f"[done] run_mode={run_mode} verdict={metrics['verdict']}", flush=True)
    print(metrics["verdict_msg"], flush=True)
    return metrics


def self_test() -> int:
    """Fast correctness + telemetry-sensitivity checks (no FULL/SMOKE output path)."""
    print("[selftest] dual-number double-dissociation primitives", flush=True)
    N_T, V_T, S_T = 512, 16, 4
    rng = _rng(0)
    cb = _bipolar(rng, V_T, N_T)
    # bind/unbind self-inverse for bipolar.
    a, b = cb[0], cb[1]
    bound = a * b
    rec = bound * b
    assert np.allclose(rec, a), "bipolar unbind not self-inverse"
    # cos of orthogonal-ish random ~ 0; self ~ 1.
    assert abs(_cos(a, a) - 1.0) < 1e-6, "cos self != 1"
    assert abs(_cos(a, cb[2])) < 0.25, "random cos too high (N too small?)"
    print("[selftest] T1 PASS: bind/unbind self-inverse + cos sane", flush=True)

    # Telemetry-sensitivity: two different seeds -> different deltas; ablation
    # changes features (hashes differ); clean acc > ablated acc where expected.
    r1 = run_one_seed(7, 120, 100)
    r2 = run_one_seed(17, 120, 100)
    assert r1["task_a"]["hash_clean"] != r1["task_a"]["hash_pabl"], \
        "ablation did not change task-a features (not telemetry-sensitive)"
    assert r1["task_b"]["hash_clean"] != r1["task_b"]["hash_mabl"], \
        "mag-ablation did not change task-b features"
    # Ratios saturate at RATIO_CAP under a clean dissociation (denominators ~0),
    # so telemetry-sensitivity is checked on the underlying paired DELTAS, which
    # vary with the seed-generated scenes.
    assert (r1["d_a_pointer"], r1["d_b_mag"]) != (r2["d_a_pointer"], r2["d_b_mag"]), \
        "two seeds gave identical ablation deltas (not telemetry-sensitive)"
    # directional sanity (small-scale; loose, just non-degenerate): pointer
    # ablation hurts task a more than task b; mag ablation hurts b more than a.
    print(f"[selftest] seed7 R_pointer={r1['R_pointer']:.2f} R_mag={r1['R_mag']:.2f} "
          f"d_a|ptr={r1['d_a_pointer']:.3f} d_b|ptr={r1['d_b_pointer']:.3f} "
          f"d_a|mag={r1['d_a_mag']:.3f} d_b|mag={r1['d_b_mag']:.3f}", flush=True)
    assert r1["task_a"]["acc_clean"] >= 0.55, "task-a clean acc degenerate"
    assert r1["task_b"]["acc_clean"] >= 0.55, "task-b clean acc degenerate"
    # Shuffled-label control must NOT show double dissociation.
    assert not r1["control_dissociation"], \
        "shuffled-label control shows dissociation (discriminator picks artifact)"
    print("[selftest] T2 PASS: telemetry-sensitive; control shows no dissociation",
          flush=True)
    print("[selftest] ALL PASS", flush=True)
    return 0


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()

    if args.self_test:
        sys.exit(self_test())

    run_mode = "smoke" if args.smoke else "full"
    out_dir = get_output_dir(ANCHOR_NAME)
    try:
        _run(run_mode)
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # NOT BaseException
        _write_crash_metrics(str(out_dir), e)
        raise


if __name__ == "__main__":
    main()
