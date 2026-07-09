"""Same-different (identity / relational-match) BAKE-IN probe (innate-scaffolding bake-in #3).

Joins the dual-number MM + object-permanence MM bake-in track. Tests two BAKED,
zero-training, by-construction same-different mechanisms as arms, both operating on
the substrate's quasi-orthogonal codebook with NO learned readout, both required to
GENERALIZE to NOVEL held-out items (the abstract-relation test). Brain/lit-grounded:
notes/research_same_different_identity_bakein_primitive_2x_2026-07-09.md (item-level
match = hippocampal comparator, free-by-construction; relational RMTS = individuate +
expose-only-relation-value, capacity-limited by scene/composition complexity).

TWO ARMS (both structural, both zero training, both applied unchanged to novel vectors):

  ARM 1 -- ITEM-LEVEL FREE COMPARATOR (the FLOOR; sanity, do NOT over-claim):
    Fixed cosine-threshold comparator on the existing quasi-orthogonal codebook.
      same trial:  (X, corrupt(X, p_flip))  -> cos ~ 1 - 2*p_flip
      diff trial:  (X, Y)                   -> cos ~ 0 +/- 1/sqrt(N)
    classify "same" iff cos >= TAU_ITEM. Score accuracy on SEEN items (drawn from a
    construction pool) vs NOVEL items (freshly drawn, never in any pool). Nothing was
    trained, so novel MUST equal seen -> the generalization GAP is the discriminator.
    (It doubles as a codebook-leakage detector: a real gap => construction-time
    correlation => codebook not truly quasi-orthogonal at this operating point.)

  ARM 2 -- RELATIONAL-TIER unbind-then-compare (the HEADLINE; capacity-limited):
    An abstract relation is a random vector T. An INSTANCE of T with novel filler F is
    the ordered pair (A1, A2) = (F, bind(F, T)); the four constituents across two
    instances are mutually dissimilar. Extract the relation by unbind-then-compare:
      R = bind(A1, inverse(A2))  = F * (F * T) = T   (bipolar self-inverse; exact)
    A depth-D SCENE bundles the queried relation instance with D-1 distractor relation
    instances (scene/composition complexity, the literature's honest ceiling):
      scene = T_query + sum_{k=1..D-1} T_distractor_k   (fillers cancel exactly)
    Compare two scenes that SHARE T_query (same-relation) vs two with independent
    relations (different-relation, the null). Signal cos(same) ~ 1/D; null spread
    std(cos(diff)) ~ 1/sqrt(N). The discriminator is a z-score over composition depth:
      z(D) = (mean cos_same - mean cos_diff) / std cos_diff  ~  sqrt(N) / D   (THEORETICAL)
    Passes z>3 at low depth, degrades gracefully, crosses below z>3 at high depth -- the
    beatable bar, NOT an unwinnable "works at all scales". Novel-filler generalization is
    filler-invariant by construction (F cancels): z_novel == z_seen (reported to confirm).

MUST-FAIL CONTROL (vacuous-guard; assert_discriminator_fires at smoke):
  SCRAMBLED relation: build instances with A2 = independent random G (NOT bind(F,T)),
  so R = F*G is random and two "same" scenes share NO true relation vector. Its z MUST
  stay below the z>3 floor (at chance). If the scrambled control clears z>3 at smoke
  scale, the discriminator measures an artifact (non-orthogonal codebook / leak) and a
  green verdict is meaningless -> VacuousSmokeError.

DISCRIMINATOR BANDS (research pre-reg; author-picked, BEFORE running):
  Item tier (FLOOR sanity): item_ok = acc_seen>=0.95 AND acc_novel>=0.95 AND
    gap<=0.02 AND diff-pair false-positive rate<=0.02.
  Relational tier (HEADLINE), z evaluated on NOVEL fillers:
    HARD_PASS = z_same(D_LOW=8) >= Z_PASS=5.0 (strictly above the z>3 floor) AND graceful
      degradation (z(D_min) > z(D_max) AND z(D_max) < Z_FLOOR=3.0, proving a real ceiling,
      not saturation) AND material novel generalization (z_novel(D_LOW) >= 0.70*z_seen(D_LOW))
      AND scrambled control at chance (z_scr(D_LOW) < Z_FLOOR) AND item_ok.
    HARD_FAIL = z_same(D_LOWEST=4) < Z_FLOOR on NOVEL items (baked unbind-compare gives NO
      abstract 2nd-order same-different) OR control leak (z_scr(D_LOW) >= Z_FLOOR) OR
      item sanity fails (codebook not quasi-orthogonal -> everything contaminated).
    MIDDLE = clears low-depth z but no crossing (all depths z>3 -> saturation concern) OR
      novel-gen below 0.70 but still above chance.

Both outcomes are gold (honest, architectural-support / mechanism-analog framing, like the
dual-number + object-permanence bake-ins; NOT task-analog): PASS bakes a structural item-level
same-different comparator (free) + maps the relational-tier composition-depth ceiling; FAIL
routes to the individuate-then-expose-only-relation-value fix (LARS-VSA / RESOLVE pattern).

SCOPE / HONESTY: this cell tests the MECHANISM on clean synthetic quasi-orthogonal bipolar
vectors (idealized codebook; clean-test discipline + sibling bake-in precedent). A variant on
the REAL substrate codebook-at-scale (which the same-day crosstalk finding flags as NOT iid /
quasi-orthogonal at scale) is the honest next stressor of the "free" claim -- deferred.

# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; item pair vs relational scene bit-distinct)
# - final_metrics_atomicity = tmp_replace (write_metrics) + per-seed write_partial
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_n/a: discriminator is a z-score of relational cos vs quasi-orthogonal null; the
#   reachability floor is z ~ sqrt(N)/D (THEORETICAL), not a Cramer-Rao noise floor.
# - baseline_in_band at smoke (null/different-relation mean cos ~ 0; item FP < 0.05; META_RULE_AG)
# - discriminator survives scale: smoke runs at FULL N=8192, all D, 1 seed, reduced trials
#   (z ~ sqrt(N)/D is N-based; smoke N == full N -> z behaves identically)
# - HARD_PASS strictly above floor (Z_PASS=5.0 vs Z_FLOOR=3.0; META_RULE_L)
# - cardinality_ok: EXPECTED_N_UNITS = n_seeds * n_D (verdict counts (seed,D) cells)
# - per-unit failure-class instrumentation (no bare except; crash-diagnostic metrics)
# - calibration_check: default_ok_for_this_regime (clean synthetic; analytical z=sqrt(N)/D)
# - all numbers tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@ in comments

Numbers in this docstring / config (tagged):
  - z(D) ~ sqrt(N)/D at N=8192: D4=22.6 D8=11.3 D16=5.66 D24=3.77 D32=2.83 D48=1.89
      THEORETICAL@z = (mean cos_same)/(std cos_diff) = (1/D)/(1/sqrt(N)) = sqrt(N)/D
  - item same-cos ~ 1 - 2*p_flip = 0.60 at p_flip=0.20  THEORETICAL@bipolar Hamming-to-cos
  - item diff-cos ~ 0 +/- 1/sqrt(N) = +/-0.011 at N=8192  THEORETICAL@random bipolar dot
  - chance z ~ 0 (null centered)  THEORETICAL@different-relation scenes share no component
  - P(relational bake-in transfers at scale) ~ 0.30 deflated  CITED@notes/research_same_different_identity_bakein_primitive_2x_2026-07-09.md:P_deflated

ASCII-only per feedback_ascii_only_in_scripts.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
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

ANCHOR_NAME = "exp_same_different_bakein_relational_tier_v1"

# ----------------------------------------------------------------------------
# Config (SMOKE=FULL parity: identical code path + identical N; only trial-count
# and seed count differ. z ~ sqrt(N)/D is N-based, so smoke at full N discriminates).
# ----------------------------------------------------------------------------
N_DIM = 8192               # substrate dimensionality (project default anchor)
V_POOL = 256               # construction pool size for "seen" fillers (novel drawn fresh)
P_FLIP_ITEM = 0.20         # item-tier "same"-trial corruption (bit-flip fraction)
TAU_ITEM = 0.30            # item-tier fixed cosine threshold (same iff cos >= TAU_ITEM)

D_GRID = (4, 8, 16, 24, 32, 48)   # relational composition-depth sweep axis
D_LOW = 8                  # low-depth headline point (must clear Z_PASS)
D_LOWEST = D_GRID[0]       # 4; HARD_FAIL if even this is below Z_FLOOR

SEEDS_FULL = (7, 17, 23)
SEEDS_SMOKE = (7,)
M_TRIALS_FULL = 400
M_TRIALS_SMOKE = 120

# Discriminator bands (research pre-reg; author-picked BEFORE running).
Z_FLOOR = 3.0              # the "z > 3" relational bar (clears -> above chance)
Z_PASS = 5.0              # HARD_PASS: z_same(D_LOW) strictly above the floor
GEN_FRAC = 0.70            # material novel generalization: z_novel >= GEN_FRAC * z_seen
ITEM_ACC_FLOOR = 0.95      # item-tier accuracy floor (seen AND novel)
ITEM_GAP_MAX = 0.02        # item-tier seen-vs-novel generalization gap ceiling
ITEM_FP_MAX = 0.02         # item-tier diff-pair false-positive ceiling
NULL_BAND_Z = 1.5          # null (different-relation) mean must be within this many
                           #   of 0 (in std-of-mean units): |mean|/(sd/sqrt(M)) < this*...
                           #   (used loosely as a self-centering sanity, not a hard gate)
EPS = 1e-12


# ----------------------------------------------------------------------------
# Substrate primitives (bipolar BSC: bind = elementwise mul, self-inverse).
# ----------------------------------------------------------------------------
def _rng(seed: int) -> np.random.Generator:
    return np.random.default_rng(seed)


def _bipolar(rng: np.random.Generator, rows: int, n: int) -> np.ndarray:
    """(rows, n) bipolar {-1,+1} float32 matrix."""
    return (rng.integers(0, 2, size=(rows, n)).astype(np.float32) * 2.0) - 1.0


def _corrupt(rng: np.random.Generator, X: np.ndarray, p_flip: float) -> np.ndarray:
    """Flip the sign of p_flip fraction of dims of each row (bipolar noise)."""
    flip = (rng.random(X.shape) < p_flip)
    return X * np.where(flip, -1.0, 1.0).astype(np.float32)


def _rows_cos(A: np.ndarray, B: np.ndarray) -> np.ndarray:
    """Row-wise cosine similarity of two (M, N) arrays -> (M,)."""
    num = np.sum(A * B, axis=1)
    da = np.linalg.norm(A, axis=1)
    db = np.linalg.norm(B, axis=1)
    da = np.where(da > 0, da, 1.0)
    db = np.where(db > 0, db, 1.0)
    return num / (da * db)


# ----------------------------------------------------------------------------
# ARM 1 -- item-level free comparator (seen vs novel generalization gap).
# ----------------------------------------------------------------------------
def _item_tier(rng: np.random.Generator, m: int) -> dict:
    """Fixed-threshold cosine comparator; accuracy on SEEN vs NOVEL items.

    Returns acc_seen, acc_novel, gap, fp (max diff-pair false-positive rate) and a
    representative "same"-pair hash (for the arms-must-differ check).
    """
    pool = _bipolar(rng, V_POOL, N_DIM)                       # construction pool (seen)

    def _score(X: np.ndarray, Y_diff: np.ndarray) -> tuple:
        # same trials: (X, corrupt(X)); diff trials: (X, Y_diff)
        Xc = _corrupt(rng, X, P_FLIP_ITEM)
        cos_same = _rows_cos(X, Xc)
        cos_diff = _rows_cos(X, Y_diff)
        pred_same_on_same = (cos_same >= TAU_ITEM)            # want True
        pred_same_on_diff = (cos_diff >= TAU_ITEM)            # want False (FP)
        acc_same = float(np.mean(pred_same_on_same))
        fp = float(np.mean(pred_same_on_diff))
        acc = 0.5 * acc_same + 0.5 * (1.0 - fp)              # balanced accuracy
        return acc, fp, Xc

    # SEEN: X and diff-partner Y both drawn from the construction pool.
    idx_x = rng.integers(0, V_POOL, size=m)
    idx_y = (idx_x + 1 + rng.integers(0, V_POOL - 1, size=m)) % V_POOL   # y != x
    Xs, Ys = pool[idx_x], pool[idx_y]
    acc_seen, fp_seen, Xc_seen = _score(Xs, Ys)

    # NOVEL: X and Y freshly drawn (never in the pool). No training -> same stats.
    Xn = _bipolar(rng, m, N_DIM)
    Yn = _bipolar(rng, m, N_DIM)
    acc_novel, fp_novel, _ = _score(Xn, Yn)

    h_item = hashlib.sha256(np.ascontiguousarray(Xc_seen[0]).tobytes()).hexdigest()[:16]
    return {
        "acc_seen": acc_seen, "acc_novel": acc_novel,
        "gap": abs(acc_novel - acc_seen),
        "fp": max(fp_seen, fp_novel),
        "hash_item": h_item,
    }


# ----------------------------------------------------------------------------
# ARM 2 -- relational tier: build depth-D scenes, unbind-then-compare.
# ----------------------------------------------------------------------------
def _build_scenes(rng: np.random.Generator, T_query: np.ndarray, D: int,
                  filler_pool: np.ndarray | None, scramble: bool) -> np.ndarray:
    """(M, N) scenes = instance(T_query) + sum of D-1 distractor-relation instances.

    The QUERY instance is built by LITERAL unbind-then-extract of an observed ordered pair
    (auditable mechanism):
      R = bind(A1, inverse(A2)) = A1 * A2  (bipolar self-inverse).
      Non-scrambled: A1 = F, A2 = F * T_query -> R = T_query (filler cancels exactly).
      Scrambled:     A1 = F, A2 = G (indep)   -> R = F * G   (random; no relation T).

    The D-1 DISTRACTOR relation instances are drawn independently. Each distractor's
    extracted relation R = F_k * (F_k * T_k) = T_k is exactly a fresh random bipolar
    vector (filler cancels), so their SUM is generated distributionally-identically in a
    single vectorized draw (sum of k iid +/-1 per dim = 2*Binomial(k, 0.5) - k). This is
    a pure speedup of the identical computation, not a change in the science.

    filler_pool None -> novel fresh fillers; else draw filler rows from the pool ("seen").
    """
    M, N = T_query.shape

    def _draw_fillers(count_rows: int) -> np.ndarray:
        if filler_pool is None:
            return _bipolar(rng, count_rows, N)
        idx = rng.integers(0, filler_pool.shape[0], size=count_rows)
        return filler_pool[idx]

    # Query instance (literal unbind-then-extract).
    A1 = _draw_fillers(M)
    if scramble:
        A2 = _draw_fillers(M)                    # independent second item -> no relation
    else:
        A2 = A1 * T_query                         # bind(F, T_query)
    scene = (A1 * A2).astype(np.float32)          # R_query = unbind(A1, A2)

    # D-1 distractor relations, summed (each ~ fresh random bipolar; vectorized).
    if D > 1:
        k = D - 1
        distract = (2.0 * rng.binomial(k, 0.5, size=(M, N)) - k).astype(np.float32)
        scene = scene + distract
    return scene


def _relational_z(rng: np.random.Generator, D: int, m: int,
                  filler_pool: np.ndarray | None) -> dict:
    """z-score of same-relation vs different-relation cosine at composition depth D.

    z_same = (mean cos_same - mean cos_diff) / std cos_diff  (headline; ~ sqrt(N)/D)
    z_scr  = (mean cos_scr  - mean cos_diff) / std cos_diff  (must-fail control; ~ 0)
    """
    T_query = _bipolar(rng, m, N_DIM)                       # shared relation per same-trial
    T_other = _bipolar(rng, m, N_DIM)                       # independent relation for null

    # SAME-relation: two scenes share T_query (independent distractors + fillers).
    s1 = _build_scenes(rng, T_query, D, filler_pool, scramble=False)
    s2 = _build_scenes(rng, T_query, D, filler_pool, scramble=False)
    cos_same = _rows_cos(s1, s2)

    # DIFFERENT-relation (null): scenes with independent query relations.
    d1 = _build_scenes(rng, T_query, D, filler_pool, scramble=False)
    d2 = _build_scenes(rng, T_other, D, filler_pool, scramble=False)
    cos_diff = _rows_cos(d1, d2)

    # SCRAMBLED control: "same"-style scenes but instances carry NO relation (A2 random).
    c1 = _build_scenes(rng, T_query, D, filler_pool, scramble=True)
    c2 = _build_scenes(rng, T_query, D, filler_pool, scramble=True)
    cos_scr = _rows_cos(c1, c2)

    mu_same = float(np.mean(cos_same))
    mu_diff = float(np.mean(cos_diff))
    sd_diff = float(np.std(cos_diff))
    mu_scr = float(np.mean(cos_scr))
    z_same = (mu_same - mu_diff) / (sd_diff + EPS)
    z_scr = (mu_scr - mu_diff) / (sd_diff + EPS)
    return {
        "D": D, "mu_same": mu_same, "mu_diff": mu_diff, "sd_diff": sd_diff,
        "mu_scr": mu_scr, "z_same": z_same, "z_scr": z_scr,
        "hash_scene": hashlib.sha256(
            np.ascontiguousarray(s1[0]).tobytes()).hexdigest()[:16],
    }


# ----------------------------------------------------------------------------
# Per-seed run.
# ----------------------------------------------------------------------------
def run_one_seed(seed: int, m_trials: int) -> dict:
    """Run item tier + relational D-sweep (novel and seen fillers) for one seed."""
    t0 = time.perf_counter()
    rng = _rng(seed)
    pool = _bipolar(rng, V_POOL, N_DIM)                     # shared "seen" filler pool

    item = _item_tier(_rng(seed + 1), m_trials)

    rel_novel: dict = {}
    rel_seen: dict = {}
    rng_r = _rng(seed + 2)
    for D in D_GRID:
        rel_novel[str(D)] = _relational_z(rng_r, D, m_trials, filler_pool=None)
        rel_seen[str(D)] = _relational_z(rng_r, D, m_trials, filler_pool=pool)

    # No silent skip: every depth must be present (META_RULE_H / no-phantom).
    if len(rel_novel) != len(D_GRID) or len(rel_seen) != len(D_GRID):
        raise RuntimeError(
            f"D-sweep cardinality breach: novel={len(rel_novel)} seen={len(rel_seen)} "
            f"expected={len(D_GRID)} (seed={seed})")

    z_novel = {D: rel_novel[str(D)]["z_same"] for D in D_GRID}
    z_seen = {D: rel_seen[str(D)]["z_same"] for D in D_GRID}
    z_scr = {D: rel_novel[str(D)]["z_scr"] for D in D_GRID}

    z_low = z_novel[D_LOW]
    z_lowest = z_novel[D_LOWEST]
    z_dmin = z_novel[D_GRID[0]]
    z_dmax = z_novel[D_GRID[-1]]
    control_z_low = z_scr[D_LOW]
    control_z_max = max(abs(z_scr[D]) for D in D_GRID)

    item_ok = (item["acc_seen"] >= ITEM_ACC_FLOOR
               and item["acc_novel"] >= ITEM_ACC_FLOOR
               and item["gap"] <= ITEM_GAP_MAX
               and item["fp"] <= ITEM_FP_MAX)

    graceful = (z_dmin > z_dmax) and (z_dmax < Z_FLOOR)     # real ceiling, not saturation
    gen_ok = z_novel[D_LOW] >= GEN_FRAC * max(z_seen[D_LOW], EPS)
    control_ok = control_z_low < Z_FLOOR
    control_leak = control_z_low >= Z_FLOOR

    rel_hp = (z_low >= Z_PASS and graceful and gen_ok and control_ok)
    rel_hf = (z_lowest < Z_FLOOR) or control_leak

    if not item_ok:
        seed_verdict = "HARD_FAIL_ITEM_SANITY"
    elif rel_hf:
        seed_verdict = "HARD_FAIL"
    elif rel_hp and item_ok:
        seed_verdict = "HARD_PASS"
    else:
        seed_verdict = "MIDDLE_BAND"

    return {
        "seed": seed, "N": N_DIM, "run_mode": None, "m_trials": m_trials,
        # item tier
        "item_acc_seen": item["acc_seen"], "item_acc_novel": item["acc_novel"],
        "item_gap": item["gap"], "item_fp": item["fp"], "item_ok": bool(item_ok),
        "hash_item": item["hash_item"],
        # relational tier
        "z_novel": {str(D): z_novel[D] for D in D_GRID},
        "z_seen": {str(D): z_seen[D] for D in D_GRID},
        "z_scr": {str(D): z_scr[D] for D in D_GRID},
        "z_low": z_low, "z_lowest": z_lowest, "z_dmin": z_dmin, "z_dmax": z_dmax,
        "control_z_low": control_z_low, "control_z_max": control_z_max,
        "graceful": bool(graceful), "gen_ok": bool(gen_ok),
        "control_ok": bool(control_ok), "control_leak": bool(control_leak),
        "rel_hp": bool(rel_hp), "rel_hf": bool(rel_hf),
        "hash_scene": rel_novel[str(D_LOW)]["hash_scene"],
        "rel_novel_detail": rel_novel, "rel_seen_detail": rel_seen,
        "n_depths": len(D_GRID),
        "seed_verdict": seed_verdict,
        "z_floor": Z_FLOOR, "z_pass": Z_PASS,
        "elapsed_s": time.perf_counter() - t0,
    }


# ----------------------------------------------------------------------------
# Aggregation + verdict.
# ----------------------------------------------------------------------------
def _aggregate(per_seed: list, expected_seeds: int) -> dict:
    n = len(per_seed)
    expected_cells = expected_seeds * len(D_GRID)
    n_cells = sum(s.get("n_depths", 0) for s in per_seed)
    if n < expected_seeds or n_cells < expected_cells:
        return {
            "verdict": "HARD_FAIL_CARDINALITY_BREACH_META_RULE_H",
            "verdict_msg": (f"CARDINALITY_BREACH: {n}/{expected_seeds} seeds, "
                            f"{n_cells}/{expected_cells} (seed,D) cells completed"),
            "summary": "CARDINALITY_BREACH",
            "n_units": n, "expected_n_units": expected_seeds,
            "n_cells": n_cells, "expected_cells": expected_cells,
        }

    def _mean(key):
        return float(np.mean([s[key] for s in per_seed]))

    def _mean_z(bucket, D):
        return float(np.mean([s[bucket][str(D)] for s in per_seed]))

    m_z_low = _mean("z_low")
    m_z_lowest = _mean("z_lowest")
    m_z_dmax = _mean("z_dmax")
    m_z_dmin = _mean("z_dmin")
    m_control_z_low = _mean("control_z_low")
    m_item_seen = _mean("item_acc_seen")
    m_item_novel = _mean("item_acc_novel")
    m_item_gap = _mean("item_gap")
    m_item_fp = _mean("item_fp")
    m_gen_low_novel = _mean_z("z_novel", D_LOW)
    m_gen_low_seen = _mean_z("z_seen", D_LOW)

    item_ok = (m_item_seen >= ITEM_ACC_FLOOR and m_item_novel >= ITEM_ACC_FLOOR
               and m_item_gap <= ITEM_GAP_MAX and m_item_fp <= ITEM_FP_MAX)
    graceful = (m_z_dmin > m_z_dmax) and (m_z_dmax < Z_FLOOR)
    gen_ok = m_gen_low_novel >= GEN_FRAC * max(m_gen_low_seen, EPS)
    control_ok = m_control_z_low < Z_FLOOR
    control_leak = m_control_z_low >= Z_FLOOR

    rel_hp = (m_z_low >= Z_PASS and graceful and gen_ok and control_ok)
    rel_hf = (m_z_lowest < Z_FLOOR) or control_leak

    n_hp = sum(1 for s in per_seed if s["seed_verdict"] == "HARD_PASS")
    n_hf = sum(1 for s in per_seed if s["seed_verdict"].startswith("HARD_FAIL"))

    if not item_ok:
        verdict = "HARD_FAIL_ITEM_SANITY"
    elif rel_hf and (control_leak or n_hf >= (n + 1) // 2):
        verdict = "HARD_FAIL"
    elif rel_hp and item_ok and n_hp >= (n + 1) // 2:
        verdict = "HARD_PASS"
    else:
        verdict = "MIDDLE_BAND"

    z_by_depth_novel = {str(D): round(_mean_z("z_novel", D), 3) for D in D_GRID}
    z_by_depth_scr = {str(D): round(_mean_z("z_scr", D), 3) for D in D_GRID}

    msg = (f"{verdict}: [relational HEADLINE] z_same(D={D_LOW})={m_z_low:.2f} "
           f"(Z_PASS={Z_PASS}) ; z_same(D={D_LOWEST})={m_z_lowest:.2f} "
           f"(Z_FLOOR={Z_FLOOR}) ; z_by_depth_novel={z_by_depth_novel} ; "
           f"graceful_degradation={graceful} (z_dmin={m_z_dmin:.2f} > z_dmax={m_z_dmax:.2f} "
           f"< {Z_FLOOR}) ; novel_gen z_novel(D{D_LOW})={m_gen_low_novel:.2f} vs "
           f"z_seen={m_gen_low_seen:.2f} (gen_ok={gen_ok}) ; scrambled-control "
           f"z_scr(D{D_LOW})={m_control_z_low:.2f} (control_ok={control_ok}, leak={control_leak}) "
           f"z_scr_by_depth={z_by_depth_scr} ; [item FLOOR] acc_seen={m_item_seen:.3f} "
           f"acc_novel={m_item_novel:.3f} gap={m_item_gap:.4f} fp={m_item_fp:.4f} "
           f"(item_ok={item_ok}) ; seeds HP={n_hp}/{n} HF={n_hf}/{n}")

    gate_claims = [
        record_gate("rel_z_low_ge_pass", m_z_low, Z_PASS, ">="),
        record_gate("rel_z_lowest_ge_floor", m_z_lowest, Z_FLOOR, ">="),
        record_gate("rel_z_dmax_lt_floor_ceiling", m_z_dmax, Z_FLOOR, "<"),
        record_gate("rel_novel_gen_ge_frac_seen", m_gen_low_novel,
                    GEN_FRAC * m_gen_low_seen, ">="),
        record_gate("control_scrambled_z_lt_floor", m_control_z_low, Z_FLOOR, "<"),
        record_gate("item_acc_seen_ge_floor", m_item_seen, ITEM_ACC_FLOOR, ">="),
        record_gate("item_acc_novel_ge_floor", m_item_novel, ITEM_ACC_FLOOR, ">="),
        record_gate("item_gap_le_max", m_item_gap, ITEM_GAP_MAX, "<="),
        record_gate("item_fp_le_max", m_item_fp, ITEM_FP_MAX, "<="),
    ]

    return {
        "verdict": verdict, "verdict_msg": msg, "summary": msg,
        "n_units": n, "expected_n_units": expected_seeds,
        "n_cells": n_cells, "expected_cells": expected_cells,
        "mean_z_low": m_z_low, "mean_z_lowest": m_z_lowest,
        "mean_z_dmin": m_z_dmin, "mean_z_dmax": m_z_dmax,
        "mean_control_z_low": m_control_z_low,
        "mean_z_by_depth_novel": z_by_depth_novel,
        "mean_z_by_depth_scrambled": z_by_depth_scr,
        "mean_item_acc_seen": m_item_seen, "mean_item_acc_novel": m_item_novel,
        "mean_item_gap": m_item_gap, "mean_item_fp": m_item_fp,
        "mean_gen_low_novel": m_gen_low_novel, "mean_gen_low_seen": m_gen_low_seen,
        "item_ok": bool(item_ok), "graceful": bool(graceful),
        "gen_ok": bool(gen_ok), "control_ok": bool(control_ok),
        "control_leak": bool(control_leak), "rel_hp": bool(rel_hp), "rel_hf": bool(rel_hf),
        "n_seeds_hard_pass": n_hp, "n_seeds_hard_fail": n_hf,
        "per_seed": per_seed,
        "gate_claims": gate_claims,
        "config": {
            "N_DIM": N_DIM, "V_POOL": V_POOL, "P_FLIP_ITEM": P_FLIP_ITEM,
            "TAU_ITEM": TAU_ITEM, "D_GRID": list(D_GRID), "D_LOW": D_LOW,
            "D_LOWEST": D_LOWEST, "Z_FLOOR": Z_FLOOR, "Z_PASS": Z_PASS,
            "GEN_FRAC": GEN_FRAC, "ITEM_ACC_FLOOR": ITEM_ACC_FLOOR,
            "ITEM_GAP_MAX": ITEM_GAP_MAX, "ITEM_FP_MAX": ITEM_FP_MAX,
        },
    }


# ----------------------------------------------------------------------------
# Runner scaffolding: start marker, crash metrics.
# ----------------------------------------------------------------------------
def _write_start_marker(output_dir, run_mode, expected_n_units):
    marker = {
        "pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
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
        seeds, m_trials = SEEDS_SMOKE, M_TRIALS_SMOKE
    else:
        seeds, m_trials = SEEDS_FULL, M_TRIALS_FULL
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
            res = run_one_seed(seed, m_trials)
            res["run_mode"] = run_mode
            res["config_version"] = f"ANCHOR={ANCHOR_NAME},N={N_DIM},run_mode={run_mode}"
            write_partial(out_dir, seed, res)
            hb.tick(i, extra={"seed": seed, "seed_verdict": res["seed_verdict"],
                              "z_low": round(res["z_low"], 2)})
            print(f"[progress] seed={seed} verdict={res['seed_verdict']} "
                  f"z_low(D{D_LOW})={res['z_low']:.2f} z_lowest(D{D_LOWEST})={res['z_lowest']:.2f} "
                  f"z_dmax(D{D_GRID[-1]})={res['z_dmax']:.2f} ctrl_z={res['control_z_low']:.2f} "
                  f"item_acc_novel={res['item_acc_novel']:.3f} item_gap={res['item_gap']:.4f} "
                  f"elapsed={time.perf_counter()-t0:.1f}s", flush=True)

    agg_all = aggregate_partials(out_dir, list(seeds), run_config=run_config)
    per_seed = [agg_all[str(s)] for s in seeds if str(s) in agg_all]
    metrics = _aggregate(per_seed, expected)
    metrics["run_mode"] = run_mode
    metrics["elapsed_s"] = time.perf_counter() - t0
    metrics["ts_iso"] = datetime.now(timezone.utc).isoformat()

    # ---- SMOKE gates: discriminator must fire + must-fail control guard -----
    if run_mode == "smoke" and per_seed:
        s0 = per_seed[0]
        # META_RULE_AF: the two arms (item pair vs relational scene) must be bit-distinct.
        assert s0["hash_item"] != s0["hash_scene"], \
            "META_RULE_AF: item-comparator pair and relational scene bit-identical"
        metrics["arms_differ_verified"] = True
        # Vacuous-guard: the scrambled (no-relation) control must NOT clear z>3.
        assert_discriminator_fires(
            bool(s0["control_leak"]),
            control_name="scrambled_no_relation_pairs",
            headline_name="relational_z_gt_3",
            run_mode="smoke",
            remedy="scrambled (no-shared-relation) scenes clear z>3 at smoke scale -> "
                   "the relational discriminator is measuring an artifact (codebook not "
                   "quasi-orthogonal / leak); fix the scene construction or the codebook "
                   "before FULL dispatch")
        # Baseline-in-band (META_RULE_AG): item diff-pair FP low (null comparator sane).
        metrics["baseline_in_band"] = bool(s0["item_fp"] <= 0.05)
        # Discriminator fires at smoke scale: passes at low depth AND crosses below the
        # floor at high depth (a real ceiling, not saturation), AND item sanity holds.
        smoke_fires = (s0["z_low"] >= Z_PASS and s0["graceful"]
                       and s0["control_ok"] and s0["item_ok"])
        metrics["smoke_discriminator_fires"] = bool(smoke_fires)
        if not smoke_fires:
            metrics["verdict"] = "SMOKE_GATE_FAIL_DISCRIMINATOR_INERT"
            metrics["verdict_msg"] = (
                "SMOKE_GATE_FAIL: same-different discriminator did not fire cleanly at "
                f"smoke scale (z_low(D{D_LOW})={s0['z_low']:.2f}>=Z_PASS={Z_PASS}? ; "
                f"graceful={s0['graceful']} (z_dmax={s0['z_dmax']:.2f}<{Z_FLOOR}?) ; "
                f"control_ok={s0['control_ok']} (z_scr={s0['control_z_low']:.2f}) ; "
                f"item_ok={s0['item_ok']}); re-spec regime before FULL dispatch")
            metrics["summary"] = metrics["verdict_msg"]

    gate_claims = metrics.pop("gate_claims", None)
    write_metrics(out_dir, metrics, results=per_seed, gate_claims=gate_claims)
    print(f"[done] run_mode={run_mode} verdict={metrics['verdict']}", flush=True)
    print(metrics["verdict_msg"], flush=True)
    return metrics


def self_test() -> int:
    """Fast correctness + telemetry-sensitivity checks (no FULL/SMOKE output path)."""
    print("[selftest] same-different bake-in (item + relational tiers)", flush=True)

    # T1: bipolar bind/unbind self-inverse (exact relation extraction).
    N_T, V_T = 512, 16
    rng = _rng(0)
    cb = _bipolar(rng, V_T, N_T)
    F, T = cb[0], cb[1]
    A1, A2 = F, F * T
    R = A1 * A2                                   # unbind-then-extract
    assert np.allclose(R, T), "bipolar unbind not self-inverse (R != T)"
    print("[selftest] T1 PASS: unbind-then-extract R = bind(A1, inv(A2)) == T (exact)",
          flush=True)

    # T2: relational z ~ sqrt(N)/D (THEORETICAL) at full N; check a couple of depths.
    rng_r = _rng(1)
    pred = lambda D: math.sqrt(N_DIM) / D
    for D in (8, 16):
        r = _relational_z(rng_r, D, 400, filler_pool=None)
        z, zp = r["z_same"], pred(D)
        assert abs(z - zp) / zp < 0.35, (
            f"z_same(D={D})={z:.2f} deviates >35% from THEORETICAL sqrt(N)/D={zp:.2f}")
        # scrambled control at chance (|z| well below floor).
        assert abs(r["z_scr"]) < Z_FLOOR, \
            f"scrambled control z_scr(D={D})={r['z_scr']:.2f} not below Z_FLOOR={Z_FLOOR}"
        print(f"[selftest] T2 D={D}: z_same={z:.2f} ~ sqrt(N)/D={zp:.2f} ; "
              f"z_scr={r['z_scr']:.2f} (< {Z_FLOOR})", flush=True)
    print("[selftest] T2 PASS: relational z ~ sqrt(N)/D; scrambled control at chance",
          flush=True)

    # T3: full per-seed run -- headline passes low depth, crosses floor at high depth,
    #     item sanity holds, novel generalization material.
    s = run_one_seed(7, 400)
    print(f"[selftest] seed7 z_low(D{D_LOW})={s['z_low']:.2f} "
          f"z_lowest(D{D_LOWEST})={s['z_lowest']:.2f} z_dmax(D{D_GRID[-1]})={s['z_dmax']:.2f} "
          f"ctrl_z={s['control_z_low']:.2f} | item acc_seen={s['item_acc_seen']:.3f} "
          f"acc_novel={s['item_acc_novel']:.3f} gap={s['item_gap']:.4f} fp={s['item_fp']:.4f} "
          f"| verdict={s['seed_verdict']}", flush=True)
    assert s["z_low"] >= Z_PASS, f"z_low={s['z_low']:.2f} below Z_PASS={Z_PASS}"
    assert s["graceful"], "no graceful degradation (headline saturates or no crossing)"
    assert s["control_ok"] and not s["control_leak"], "scrambled control leaked (z>=floor)"
    assert s["item_ok"], "item-tier sanity failed (codebook not quasi-orthogonal?)"
    assert s["gen_ok"], "novel generalization below GEN_FRAC of seen"
    assert s["item_gap"] <= ITEM_GAP_MAX, \
        f"item generalization gap {s['item_gap']:.4f} > {ITEM_GAP_MAX}"
    assert s["seed_verdict"] == "HARD_PASS", f"seed verdict {s['seed_verdict']} != HARD_PASS"
    print("[selftest] T3 PASS: headline z>Z_PASS at low D, crosses floor at high D; "
          "item sanity + novel-gen hold", flush=True)

    # T4: telemetry-sensitivity -- perturbing the seed moves the metrics.
    s2 = run_one_seed(17, 400)
    assert s["hash_scene"] != s2["hash_scene"], \
        "two seeds gave identical relational scenes (not telemetry-sensitive)"
    assert (round(s["z_low"], 4), round(s["z_dmax"], 4)) != \
           (round(s2["z_low"], 4), round(s2["z_dmax"], 4)), \
        "two seeds gave identical z values (not telemetry-sensitive)"
    assert s["hash_item"] != s["hash_scene"], "item and relational arms bit-identical"
    print(f"[selftest] T4 PASS: telemetry-sensitive (seed17 z_low={s2['z_low']:.2f} "
          f"z_dmax={s2['z_dmax']:.2f})", flush=True)
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
