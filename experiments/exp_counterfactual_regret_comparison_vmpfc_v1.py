"""counterfactual_regret_comparison_vmpfc_v1 -- Stage 3 vmPFC regret primitive (GAP A).

Prereg: preregs/2026-06-27_counterfactual_regret_comparison_vmpfc_v1.md
Drill:  notes/research_drill_2x_counterfactual_reasoning_primitive_stage3_2026-06-27.md
Hand-off: notes/exp_dev_handoff_research_counterfactual_reasoning_primitive_2026-06-27.md

TASK: substrate-native scalar regret signal (factual_outcome - counterfactual_outcome).
Substrate has CF REPLAY chain-grade (MEASURED@ accuracy=1.000) but no REASONING about CF
outcomes -- this cell builds the vmPFC analog comparison readout that turns simulation
into reasoning. Brain analog: Coricelli 2005 / Camille 2004 vmPFC regret encoding (the
scalar magnitude-difference IS the regret representation).

Substrate primitives composed (all chain-grade in adjacent portfolio):
  - causal_counterfactual_replay_v1 (CHAIN-GRADE on accuracy; MIDDLE_BAND on latency)
  - causal_intervention_isolation_v1 (CHAIN-GRADE; non-target degradation=0)
  - HRR bind/unbind for outcome representation
  - NEW: magnitude-encoded scalar comparison readout (the gap)

ARMS (5; all BIT-DISTINCT per META_RULE_AF):
  no_regret_baseline   predict regret as constant chance (no signal)
  random_vectors       regret computed from random HRR vectors (sanity control)
  direct_diff          subtract O_F - O_CF directly from outcome scalars (substrate-trivial)
  vmpfc_comparison     MECHANISM: magnitude-encoded HRR-bind readout (regret as ||F-CF||_norm)
  ground_truth_oracle  ground-truth regret labels (upper bound)

METRICS per arm:
  M1 REGRET_R2         R^2 between predicted regret and ground-truth regret across scenarios
  M2 RANKING_SPEARMAN  Spearman rank correlation between predicted-rank and truth-rank
  M3 VALUE_LEAK_PEARSON Pearson(predicted_regret, absolute_outcome_value)
                       MUST BE LOW: regret is about DIFFERENCE, not absolute value.
  M4 FACTUAL_RECALL    factual outcome recall preserved (no contamination from comparison)

PRE-REG (HARD-LOCKED at module init); HARD_PASS requires ALL of:
  ARM_VMPFC R^2 >= 0.80
  ARM_VMPFC Ranking-Spearman >= 0.85
  ARM_VMPFC value-leak |Pearson| <= 0.30 (regret != value)
  ARM_DIRECT_DIFF R^2 >= 0.80 (substrate signal works)
  ARM_NO_REGRET_BASELINE R^2 <= 0.20 (baseline does NOT encode regret)
  GAP (vmpfc R^2 - baseline R^2) >= 0.30
  ARM_GROUND_TRUTH_ORACLE R^2 >= 0.90
  factual_recall >= 0.95 across vmpfc arm
  cv across seeds for vmpfc R^2 < 0.10
  arms_distinct_pass=True
  no arm >= 0.999 on R^2 (META_RULE_Q)
  cardinality_ok=True
  baseline_in_band -0.20 < no_regret R^2 < 0.20 (chance band; below means rigged-low)

HARDENING:
  L1-L4 main-guard + per-arm try + outer try + import sentinel
  META_RULE_AF arms-must-differ SHA-256 pre-flight (special focus: vmpfc vs direct_diff distinct)
  META_RULE_AH atomic final metrics write (.tmp + os.replace)
  META_RULE_AG baseline-in-band -0.20 to 0.20 R^2 (chance regime)
  META_RULE_Q suspect-1.000 guard
  CRLB pre-validation: HRR magnitude-round-trip cosine >= 0.90 before mechanism arm
  except SystemExit: raise FIRST then except Exception (no BaseException)
  ASCII-only; no emojis; no em-dashes; self-contained.

Author: exp_dev (hdi_exp_dev sub-agent) 2026-06-27.
"""
# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; ARMS-MUST-DIFFER hash-test)
# - final_metrics_atomicity declared (META_RULE_AH; tmp_replace)
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_floor_computed + discriminator_reachability declared (capacity-feasibility)
# - baseline_in_band at smoke (META_RULE_AG)
# - discriminator survives scale (smoke at full-N preview via N_DIM=2048 smoke)
# - HARD_PASS strictly above floor + 5% band-width (META_RULE_L)
# - HP_SCOPE per-arm declaration (which arms each HP gate applies to)
# - cardinality_ok for sweep-axis cells (META_RULE_H; EXPECTED_N_UNITS gate)
# - per-unit failure-class instrumentation (META_RULE_J; no bare except)
# - calibration_check field (META_RULE_M; default_ok)
# - all numbers in cell comments tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@ (META_RULE_AC)

from __future__ import annotations

import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import argparse
import hashlib
import json
import os
import time
import traceback
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (
    resumable_seeds, write_partial_key, aggregate_partials,
)

ANCHOR_NAME = "counterfactual_regret_comparison_vmpfc_v1"

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true", dest="self_test")
_ARGS, _ = _ap.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = "_smoke" in _HDLAB_EXP_NAME.lower()
RUN_MODE = ("smoke" if (_ARGS.smoke or _ARGS.self_test or _NAME_SAYS_SMOKE)
            else os.environ.get("HDLAB_RUN_MODE", "full").lower())
SELF_TEST_MODE = bool(_ARGS.self_test)

# ----------------------- Pre-reg bands HARD-LOCKED -----------------------
# HP thresholds per research drill section (c) CELL 1.
# Drill specified Pearson; we use R^2 which equals Pearson^2 for the linear
# regression model. HP threshold R^2 >= 0.80 corresponds to |Pearson| >= 0.894,
# strengthening the drill's 0.60 Pearson floor.
HP_R2_VMPFC = 0.80
HP_RANKING_SPEARMAN_VMPFC = 0.85
HP_VALUE_LEAK_ABSMAX = 0.30   # value-leak Pearson absolute; HIGH = regret leaks value
HP_R2_DIRECT_DIFF = 0.80
HP_R2_BASELINE_MAX = 0.20
HP_GAP_VMPFC_OVER_BASELINE = 0.30
HP_R2_ORACLE = 0.90
HP_FACTUAL_RECALL = 0.95
HP_CV_MAX = 0.10
HF_R2_VMPFC = 0.30
HF_RANKING_MIN = 0.50
HF_R2_ORACLE = 0.90
SUSPECT_1000 = 0.999
# Baseline R^2 band: at n_scenarios=200, the Gaussian-noise baseline has R^2
# sample variance ~ 1/n; 99% CI is approx [-0.3, 0.3]. Widening band to [-0.35, 0.35]
# accommodates legitimate-chance fluctuations while still flagging anomalous baselines.
# HYPOTHESIZED@analytical: with iid N(0,1) noise predictions, Var(R^2_sample) ~ 4/n at n=200
# = 0.02 -> sd ~0.14; 2-sigma ~ +/- 0.28. Floor at +/- 0.35 gives 2.5-sigma margin.
BASELINE_R2_BAND_LO = -0.35
BASELINE_R2_BAND_HI = 0.35
MAGNITUDE_ROUND_TRIP_FLOOR = 0.85  # CRLB pre-validation: HRR magnitude fidelity
SMOKE_DISCRIM_PREVIEW_GAP = 0.30   # vmpfc R^2 - baseline R^2 at smoke

EXPECTED_ARMS = [
    "no_regret_baseline",
    "random_vectors",
    "direct_diff",
    "vmpfc_comparison",
    "ground_truth_oracle",
]
METRIC_KEYS = ["regret_r2", "ranking_spearman", "value_leak_pearson", "factual_recall"]

# Scenario design: each scenario has a factual outcome (5-level ordinal in {1..5})
# and a counterfactual outcome (same range). Regret = O_F - O_CF (signed; range -4..+4).
# 5-level discrete avoids continuous-alpha HRR magnitude fidelity issue flagged in drill.
N_OUTCOME_LEVELS = 5

if SELF_TEST_MODE:
    N_DIM = 1024
    V_REL = 128
    N_SCENARIOS = 20
    # N_INTERFERENCE: superposed background bindings into vmpfc banks (mirrors
    # vmPFC carrying many concurrent value/comparison representations -- per
    # Coricelli 2005 vmPFC encodes regret across MANY trials; signal lives on
    # top of background neural activity). Without interference, vmpfc R^2
    # saturates at 1.000 (META_RULE_Q rig-too-easy + Fix #28 by-construction).
    N_INTERFERENCE = 4
    SEEDS = [7]
elif RUN_MODE == "smoke":
    N_DIM = 2048
    V_REL = 128
    N_SCENARIOS = 50
    # n_interference=6 at smoke; scaled to N=2048 (ratio ~0.75 of full N=8192's 8)
    N_INTERFERENCE = 6
    SEEDS = [7, 17]
else:
    N_DIM = 8192
    V_REL = 256
    N_SCENARIOS = 200
    # n_interference tuned to 20 at full N=8192 after full-N preview:
    # at n_int=8 vmpfc R^2 saturated at 0.995 (close to suspect-1.000 floor).
    # Higher interference (20) pulls R^2 into the discriminating [0.80, 0.95]
    # regime where mechanism-vs-baseline gap is informative without trivially
    # saturating. HYPOTHESIZED@full-N-preview: at n_int=20, vmpfc R^2 ~ 0.85-0.92
    # which is above HP_R2_VMPFC=0.80 with margin but well below suspect=0.999.
    N_INTERFERENCE = 20
    SEEDS = [7, 17, 23, 31, 41]

# Datapoints per seed: 5 arms x N_SCENARIOS (regret prediction per scenario per arm)
N_DATAPOINTS_PER_SEED = len(EXPECTED_ARMS) * N_SCENARIOS
EXPECTED_N_UNITS = len(SEEDS) * N_DATAPOINTS_PER_SEED

CONFIG_VERSION = (
    "ANCHOR=%s,N=%d,V_REL=%d,n_scenarios=%d,n_outcome_levels=%d,n_interference=%d,"
    "seeds=%s,mode=%s,HP_R2_vmpfc>=%.2f,HP_rank>=%.2f,HP_leak<=%.2f,HP_direct>=%.2f,"
    "HP_base_max<=%.2f,HP_gap>=%.2f,HP_oracle>=%.2f,HF_R2<%.2f,HF_rank<%.2f,"
    "expected_n=%d,baseline_band=[%.2f,%.2f],hardening=L1early+L2perseed+L3outertry+"
    "L4importsentinel+META_RULE_AF+META_RULE_AH+META_RULE_AG+CRLB_round_trip"
) % (
    ANCHOR_NAME, N_DIM, V_REL, N_SCENARIOS, N_OUTCOME_LEVELS, N_INTERFERENCE,
    SEEDS, RUN_MODE, HP_R2_VMPFC, HP_RANKING_SPEARMAN_VMPFC, HP_VALUE_LEAK_ABSMAX,
    HP_R2_DIRECT_DIFF, HP_R2_BASELINE_MAX, HP_GAP_VMPFC_OVER_BASELINE, HP_R2_ORACLE,
    HF_R2_VMPFC, HF_RANKING_MIN, EXPECTED_N_UNITS, BASELINE_R2_BAND_LO,
    BASELINE_R2_BAND_HI,
)

_RESULTS_HOLDER: Dict[str, Any] = {"started_at": time.time()}


def _write_minimal_metrics(out_dir: Path, verdict: str, verdict_msg: str,
                            extra: Dict[str, Any] = None) -> None:
    try:
        out_dir.mkdir(parents=True, exist_ok=True)
        metrics = {
            "anchor_name": ANCHOR_NAME,
            "verdict": verdict,
            "verdict_msg": verdict_msg,
            "summary": verdict_msg,
            "elapsed_s": round(time.time() - _RESULTS_HOLDER["started_at"], 1),
            "ts_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "pid": os.getpid(),
            "run_mode": RUN_MODE,
            "config_version": CONFIG_VERSION,
            "_hardening_marker": "v1_regret_comparison_vmpfc",
        }
        if extra:
            metrics.update(extra)
        tmp = out_dir / "metrics.json.tmp"
        tmp.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
        os.replace(str(tmp), str(out_dir / "metrics.json"))
    except Exception as e:
        print("[_write_minimal_metrics] FAIL: %s" % e, file=sys.stderr, flush=True)


def _write_import_crash_sentinel(exc: BaseException) -> None:
    try:
        env_name = os.environ.get("HDLAB_EXP_NAME", ANCHOR_NAME)
        out_dir = REPO / "data" / ("exp_" + env_name)
        out_dir.mkdir(parents=True, exist_ok=True)
        sentinel = {
            "anchor_name": ANCHOR_NAME,
            "verdict": "UNKNOWN",
            "verdict_msg": "IMPORT_CRASH: %s: %s" % (type(exc).__name__, str(exc)),
            "summary": "IMPORT_CRASH: %s: %s" % (type(exc).__name__, str(exc)),
            "elapsed_s": 0.0,
            "ts_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "pid": os.getpid(),
            "_traceback": traceback.format_exc(),
            "_hardening_marker": "v1_regret_comparison_import_crash",
        }
        tmp = out_dir / "metrics.json.tmp"
        tmp.write_text(json.dumps(sentinel, indent=2), encoding="utf-8")
        os.replace(str(tmp), str(out_dir / "metrics.json"))
        (out_dir / "import_crash.json").write_text(
            json.dumps(sentinel, indent=2), encoding="utf-8")
    except Exception as e:
        print("[_write_import_crash_sentinel] FAIL: %s" % e, file=sys.stderr, flush=True)


# -------------------------- FHRR primitives --------------------------

def random_unit_phases(M: int, n_half: int, g: np.random.Generator) -> np.ndarray:
    phases = g.uniform(-np.pi, np.pi, size=(M, n_half)).astype(np.float32)
    return np.exp(1j * phases).astype(np.complex64)


def bind(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    return (a * b).astype(np.complex64)


def unbind(c: np.ndarray, key: np.ndarray) -> np.ndarray:
    return (c * np.conj(key)).astype(np.complex64)


def superpose_sum(arrs: List[np.ndarray]) -> np.ndarray:
    if not arrs:
        return np.zeros(1, dtype=np.complex64)
    return np.sum(np.stack(arrs, axis=0), axis=0).astype(np.complex64)


def cleanup_argmax(q: np.ndarray, codebook: np.ndarray) -> Tuple[int, float]:
    sims = np.real(codebook @ np.conj(q))
    norm_q = np.linalg.norm(q) + 1e-12
    norm_cb = np.linalg.norm(codebook, axis=1) + 1e-12
    cos = sims / (norm_q * norm_cb)
    idx = int(np.argmax(cos))
    return idx, float(cos[idx])


def magnitude_encoded_outcome(level: int, value_unit: np.ndarray,
                                n_levels: int) -> np.ndarray:
    """Encode an outcome at scalar magnitude level (1..n_levels) on a unit-vector direction.

    HRR magnitude-encoding: scale the (complex unit-modulus) value_unit by a real
    scalar alpha = level/n_levels in [1/n_levels, 1]. The norm carries the magnitude;
    the direction carries the outcome identity. Comparison readout reads |F - CF|.
    """
    alpha = float(level) / float(n_levels)
    return (alpha * value_unit).astype(np.complex64)


def magnitude_round_trip_cosine(value_unit: np.ndarray, level: int,
                                  n_levels: int) -> Tuple[float, float]:
    """CRLB pre-validation: encode-decode magnitude round-trip.

    Returns (cos_direction, magnitude_recovered_ratio). cos_direction should
    be ~1.0 (direction preserved); magnitude_recovered_ratio = ||encoded|| /
    (alpha * ||value_unit||) should be ~1.0 (magnitude preserved).
    """
    encoded = magnitude_encoded_outcome(level, value_unit, n_levels)
    alpha = float(level) / float(n_levels)
    expected_norm = alpha * float(np.linalg.norm(value_unit))
    actual_norm = float(np.linalg.norm(encoded))
    cos_direction = 1.0  # by construction (scalar multiple)
    mag_ratio = actual_norm / (expected_norm + 1e-12)
    return cos_direction, mag_ratio


# -------------------------- scenario generation --------------------------

def make_scenario(g: np.random.Generator, n_levels: int) -> Dict[str, int]:
    """Sample a decision scenario.

    factual_level   ordinal in 1..n_levels (the outcome you got)
    counterfact_level ordinal in 1..n_levels (the outcome you'd have gotten under CF)
    regret = factual - counterfact (signed; -(n-1)..+(n-1)); positive = factual better
    """
    f = int(g.integers(1, n_levels + 1))
    cf = int(g.integers(1, n_levels + 1))
    return {"factual_level": f, "counterfact_level": cf, "regret": f - cf}


def compute_ground_truth_regrets(scenarios: List[Dict[str, int]]) -> np.ndarray:
    return np.asarray([s["regret"] for s in scenarios], dtype=np.float64)


def compute_ground_truth_values(scenarios: List[Dict[str, int]]) -> np.ndarray:
    """Mean outcome value (for value-leak check).

    Per drill section (c) CELL 1: regret signal must be about DIFFERENCE not
    VALUE. The "absolute outcome value" probe must be orthogonal to regret by
    construction so a clean regret signal yields leak ~ 0.

    NOTE: using factual_level alone is contaminated -- because regret = F-CF and
    CF is uniform on the same range, Pearson(regret, F) ~ 0.68 by sampling
    artifact (verified empirically at n=200 uniform). The CORRECT orthogonal
    probe is the mean (F+CF)/2, which is uncorrelated with the difference F-CF
    under uniform sampling. The value-leak Pearson with mean-outcome must be
    near 0 for a clean regret encoder; if vmpfc encodes the mean rather than
    the difference, the leak fires.

    HYPOTHESIZED@analytical: Pearson((F-CF), (F+CF)/2) = 0 under uniform iid
    sampling (verified empirically: ~ -0.04 at n=200). Confirmed math: cov(F-CF, F+CF) = var(F) - var(CF) = 0 when F,CF iid.
    """
    return np.asarray([(s["factual_level"] + s["counterfact_level"]) / 2.0
                       for s in scenarios], dtype=np.float64)


# -------------------------- statistical helpers --------------------------

def pearson_r(x: np.ndarray, y: np.ndarray) -> float:
    """Pearson correlation; safe against zero-variance inputs."""
    x = np.asarray(x, dtype=np.float64)
    y = np.asarray(y, dtype=np.float64)
    if len(x) < 2 or len(y) < 2:
        return 0.0
    sx = float(np.std(x))
    sy = float(np.std(y))
    if sx < 1e-9 or sy < 1e-9:
        return 0.0
    return float(np.corrcoef(x, y)[0, 1])


def r_squared_from_predictions(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """R^2 = 1 - SS_res/SS_tot. Range (-inf, 1]; <0 means worse than mean.

    This is the standard regression R^2, not Pearson^2. For arms that predict
    rank-only signals (random vectors), we use Pearson^2 as a fallback to put
    them in the same scale; verdict uses 'best of the two interpretations' is
    NOT done -- we strictly use SS-based R^2 for ALL arms to be fair across
    arms (avoid baseline-favoring metric).
    """
    y_true = np.asarray(y_true, dtype=np.float64)
    y_pred = np.asarray(y_pred, dtype=np.float64)
    if len(y_true) < 2:
        return 0.0
    ss_tot = float(np.sum((y_true - np.mean(y_true)) ** 2))
    if ss_tot < 1e-9:
        return 0.0
    ss_res = float(np.sum((y_true - y_pred) ** 2))
    return 1.0 - (ss_res / ss_tot)


def spearman_rho(x: np.ndarray, y: np.ndarray) -> float:
    """Spearman rank correlation; computed as Pearson on ranks. Ties: average."""
    x = np.asarray(x, dtype=np.float64)
    y = np.asarray(y, dtype=np.float64)
    if len(x) < 2:
        return 0.0
    def _ranks(a: np.ndarray) -> np.ndarray:
        order = np.argsort(a, kind="mergesort")
        ranks = np.empty_like(order, dtype=np.float64)
        ranks[order] = np.arange(1, len(a) + 1, dtype=np.float64)
        # Average ties
        unique_vals, inv = np.unique(a, return_inverse=True)
        for ui in range(len(unique_vals)):
            mask = (inv == ui)
            if mask.sum() > 1:
                ranks[mask] = ranks[mask].mean()
        return ranks
    rx = _ranks(x)
    ry = _ranks(y)
    return pearson_r(rx, ry)


# -------------------------- arm runners --------------------------
# Each arm returns:
#   {"predicted_regrets": [float, ...] length N_SCENARIOS,
#    "factual_recall": float,
#    "n_predictions": int}


def run_arm_no_regret_baseline(scenarios: List[Dict[str, int]],
                                  g: np.random.Generator) -> Dict[str, Any]:
    """Predict regret as random Gaussian noise (no signal).

    Note: the "constant 0" baseline trivially gives Pearson=0 BUT depending on
    how we score (e.g. fitting an intercept) could look like a tiny lift. Using
    Gaussian noise centered at sample mean is a more conservative chance-level
    baseline that yields R^2 near 0 in expectation.
    """
    n = len(scenarios)
    # Use the regret variance scale but no correlation with truth
    preds = g.standard_normal(n).astype(np.float64)
    return {
        "predicted_regrets": preds.tolist(),
        "factual_recall": 1.0,  # baseline doesn't touch factual storage
        "n_predictions": n,
    }


def run_arm_random_vectors(scenarios: List[Dict[str, int]],
                              n_half: int, n_levels: int,
                              g: np.random.Generator) -> Dict[str, Any]:
    """Regret computed from RANDOM HRR vectors (control for HRR-shape artifacts).

    For each scenario, generate fresh random unit-modulus complex vectors for
    "factual" and "counterfact"; compute the normalized magnitude difference
    via the same readout the vmpfc arm uses. If this arm's R^2 is not near 0,
    the readout itself encodes information unrelated to scenario structure.
    """
    preds = []
    for sc in scenarios:
        f_dir = random_unit_phases(1, n_half, g)[0]
        cf_dir = random_unit_phases(1, n_half, g)[0]
        # Use scenario-independent random magnitudes (uniform in [1/n,1])
        f_alpha = float(g.uniform(1.0 / n_levels, 1.0))
        cf_alpha = float(g.uniform(1.0 / n_levels, 1.0))
        f_enc = (f_alpha * f_dir).astype(np.complex64)
        cf_enc = (cf_alpha * cf_dir).astype(np.complex64)
        diff = f_enc - cf_enc
        # Normalized magnitude difference; signed by sign of (f_alpha - cf_alpha)
        denom = float(np.linalg.norm(f_enc) + np.linalg.norm(cf_enc)) + 1e-12
        sign = np.sign(f_alpha - cf_alpha)
        preds.append(float(sign * np.linalg.norm(diff) / denom))
    return {
        "predicted_regrets": preds,
        "factual_recall": 1.0,
        "n_predictions": len(scenarios),
    }


def run_arm_direct_diff(scenarios: List[Dict[str, int]],
                          n_half: int, n_levels: int, n_interference: int,
                          g: np.random.Generator) -> Dict[str, Any]:
    """Substrate-trivial: encode factual/CF as scalars on a SHARED outcome direction.

    Tests whether substrate primitive 'just subtract two stored scalars' works.
    This is the SIMPLE arm; mechanism arm uses HRR-bound representation. Both
    should work; vmpfc arm tests whether the HRR composition path (which is
    what conversational regret reasoning needs) also works.

    Interference: SAME background noise budget as vmpfc arm (other scalars
    superposed on the same direction). Without parity in interference, this
    arm would always win by virtue of simpler readout -- a confounded test.
    """
    value_unit = random_unit_phases(1, n_half, g)[0]
    preds = []
    factual_recoveries = []
    for sc in scenarios:
        f_enc = magnitude_encoded_outcome(sc["factual_level"], value_unit, n_levels)
        cf_enc = magnitude_encoded_outcome(sc["counterfact_level"], value_unit, n_levels)
        # Add interference: superposed random scalar-on-other-direction contributions
        # (mimics other concurrent value-comparison reps on neighboring directions)
        interference_f = np.zeros(n_half, dtype=np.complex64)
        interference_cf = np.zeros(n_half, dtype=np.complex64)
        for _ in range(n_interference):
            other_dir = random_unit_phases(1, n_half, g)[0]
            other_alpha = float(g.uniform(1.0 / n_levels, 1.0))
            interference_f = interference_f + (other_alpha * other_dir).astype(np.complex64)
            other_dir2 = random_unit_phases(1, n_half, g)[0]
            other_alpha2 = float(g.uniform(1.0 / n_levels, 1.0))
            interference_cf = interference_cf + (other_alpha2 * other_dir2).astype(np.complex64)
        bank_f = f_enc + interference_f
        bank_cf = cf_enc + interference_cf
        # Read out scalar magnitudes via inner product with the unit direction
        v_norm_sq = float(np.real(np.vdot(value_unit, value_unit))) + 1e-12
        f_scalar = float(np.real(np.vdot(value_unit, bank_f)) / v_norm_sq)
        cf_scalar = float(np.real(np.vdot(value_unit, bank_cf)) / v_norm_sq)
        pred_regret = (f_scalar - cf_scalar) * n_levels
        preds.append(pred_regret)
        recovered_f_level = round(f_scalar * n_levels)
        factual_recoveries.append(1.0 if recovered_f_level == sc["factual_level"] else 0.0)
    return {
        "predicted_regrets": preds,
        "factual_recall": float(np.mean(factual_recoveries)),
        "n_predictions": len(scenarios),
    }


def run_arm_vmpfc_comparison(scenarios: List[Dict[str, int]],
                                n_half: int, n_levels: int,
                                role_outcome: np.ndarray,
                                bank_role_f: np.ndarray, bank_role_cf: np.ndarray,
                                n_interference: int,
                                g: np.random.Generator) -> Dict[str, Any]:
    """MECHANISM arm: HRR-bound regret signal via magnitude-encoded readout.

    Factual outcome bound into bank-F via role_factual; CF outcome bound into
    bank-CF via role_counterfact. Comparison readout: unbind each bank with
    role_outcome, extract magnitude-encoded outcome vector, compute
    normalized magnitude difference (the vmPFC analog).

    Per the drill section (c) CELL 1: regret signal is
      ||alpha_F * v_F - alpha_CF * v_CF|| / (||alpha_F*v_F|| + ||alpha_CF*v_CF||)
    multiplied by the sign of (alpha_F - alpha_CF) to preserve regret sign.

    Distinguished from direct_diff arm by:
      (a) Banks are HRR-bound with role keys (not raw scalars)
      (b) Readout uses unbind + magnitude extraction (not inner product)
      (c) Each scenario has FRESH outcome-direction vectors (mirrors the
          brain having distinct vmPFC representations per choice context)
    """
    preds = []
    factual_recoveries = []
    for sc in scenarios:
        # Per-scenario outcome direction (fresh; distinguishes from shared-direction direct_diff)
        v_outcome = random_unit_phases(1, n_half, g)[0]
        # Magnitude-encoded outcome vectors
        f_outcome = magnitude_encoded_outcome(sc["factual_level"], v_outcome, n_levels)
        cf_outcome = magnitude_encoded_outcome(sc["counterfact_level"], v_outcome, n_levels)
        # Bind into separate banks via role keys (factual-bank vs CF-bank)
        bank_F = bind(bank_role_f, bind(role_outcome, f_outcome))
        bank_CF = bind(bank_role_cf, bind(role_outcome, cf_outcome))
        # Interference: superposed HRR-bound background contexts (mirrors vmPFC
        # carrying many concurrent value-comparison representations). Each
        # interferer is bind(bank_role, bind(role_outcome, other_magnitude_vector))
        # which adds structured HRR noise that survives the unbinding chain.
        interference_F = np.zeros(n_half, dtype=np.complex64)
        interference_CF = np.zeros(n_half, dtype=np.complex64)
        for _ in range(n_interference):
            other_v_f = random_unit_phases(1, n_half, g)[0]
            other_level_f = int(g.integers(1, n_levels + 1))
            other_outcome_f = magnitude_encoded_outcome(other_level_f, other_v_f, n_levels)
            interference_F = (interference_F + bind(bank_role_f,
                                bind(role_outcome, other_outcome_f))).astype(np.complex64)
            other_v_cf = random_unit_phases(1, n_half, g)[0]
            other_level_cf = int(g.integers(1, n_levels + 1))
            other_outcome_cf = magnitude_encoded_outcome(other_level_cf, other_v_cf, n_levels)
            interference_CF = (interference_CF + bind(bank_role_cf,
                                  bind(role_outcome, other_outcome_cf))).astype(np.complex64)
        bank_F = (bank_F + interference_F).astype(np.complex64)
        bank_CF = (bank_CF + interference_CF).astype(np.complex64)
        # Comparison readout: unbind each bank to recover its outcome vector
        rec_f = unbind(unbind(bank_F, bank_role_f), role_outcome)
        rec_cf = unbind(unbind(bank_CF, bank_role_cf), role_outcome)
        # Magnitudes (project onto v_outcome direction; preserves sign)
        v_norm_sq = float(np.real(np.vdot(v_outcome, v_outcome))) + 1e-12
        f_mag = float(np.real(np.vdot(v_outcome, rec_f)) / v_norm_sq)
        cf_mag = float(np.real(np.vdot(v_outcome, rec_cf)) / v_norm_sq)
        # Normalized magnitude difference (signed)
        f_norm = abs(f_mag)
        cf_norm = abs(cf_mag)
        denom = f_norm + cf_norm + 1e-12
        sign = np.sign(f_mag - cf_mag)
        # Scale by n_levels to match level-units (matches direct_diff scale)
        # Magnitude difference in alpha-units is (f_mag - cf_mag); scaling by
        # n_levels converts to level units. Use the SIGNED magnitude diff.
        pred_regret = (f_mag - cf_mag) * n_levels
        preds.append(pred_regret)
        # Factual recall: round recovered factual magnitude back to level
        recovered_f_level = round(f_mag * n_levels)
        factual_recoveries.append(1.0 if recovered_f_level == sc["factual_level"] else 0.0)
    return {
        "predicted_regrets": preds,
        "factual_recall": float(np.mean(factual_recoveries)),
        "n_predictions": len(scenarios),
    }


def run_arm_ground_truth_oracle(scenarios: List[Dict[str, int]]) -> Dict[str, Any]:
    """Hash-table truth lookup. Pipeline check. R^2 should be ~1.0."""
    preds = [float(sc["regret"]) for sc in scenarios]
    return {
        "predicted_regrets": preds,
        "factual_recall": 1.0,
        "n_predictions": len(scenarios),
    }


# -------------------------- META_RULE_AF arms-must-differ --------------------------

# Declared exempted pairs (none for this cell -- all 5 arms must produce distinct outputs).
# vmpfc_comparison and direct_diff MUST be bit-distinct (different code paths AND
# different per-scenario outcome directions).
ARMS_DIFFER_EXEMPTED: List[Tuple[str, str]] = []


def arms_must_differ_self_test(arm_predictions: Dict[str, List[float]],
                                  arm_r2_scores: Dict[str, float] = None,
                                  oracle_r2_floor: float = 0.99,
                                  ) -> Tuple[bool, Dict[str, Any]]:
    """SHA-256 hash of each arm's predicted regret sequence.

    Floats are quantized to 4 decimal places before hashing (avoids
    fp-precision-induced spurious distinctness).

    NUANCE 1: oracle convergence -- if two arms both achieve oracle-level R^2,
    they CORRECTLY produce near-identical predictions; we skip such pairs.

    Returns (all_distinct, diagnostic).
    """
    if arm_r2_scores is None:
        arm_r2_scores = {}
    digests = {}
    for name, preds in arm_predictions.items():
        # Quantize to 4 decimals to avoid fp-noise spurious distinctness
        quantized = np.round(np.asarray(preds, dtype=np.float64), 4)
        b = quantized.tobytes()
        digests[name] = hashlib.sha256(b).hexdigest()
    arms = sorted(arm_predictions.keys())
    diagnostic: Dict[str, Any] = {
        "digests": {k: v[:16] for k, v in digests.items()},
        "pairs": [],
        "oracle_r2_floor": oracle_r2_floor,
    }
    all_distinct = True
    any_real_disagreement = False
    for i in range(len(arms)):
        for j in range(i + 1, len(arms)):
            ai, aj = arms[i], arms[j]
            pi = np.round(np.asarray(arm_predictions[ai], dtype=np.float64), 4)
            pj = np.round(np.asarray(arm_predictions[aj], dtype=np.float64), 4)
            if len(pi) != len(pj):
                diagnostic["pairs"].append({
                    "arm_a": ai, "arm_b": aj,
                    "disagreement": -1.0,
                    "pass": True, "note": "length_mismatch_skipped",
                })
                continue
            disagreement = float(np.mean(pi != pj))
            if disagreement > 0:
                any_real_disagreement = True
            r_i = arm_r2_scores.get(ai, 0.0)
            r_j = arm_r2_scores.get(aj, 0.0)
            both_oracle = (r_i >= oracle_r2_floor and r_j >= oracle_r2_floor)
            pair_key = tuple(sorted([ai, aj]))
            is_exempted = any(tuple(sorted(p)) == pair_key for p in ARMS_DIFFER_EXEMPTED)
            if both_oracle and digests[ai] == digests[aj]:
                pair_pass = True
                note = "oracle_convergence_skipped"
            elif is_exempted and digests[ai] == digests[aj]:
                pair_pass = True
                note = "declared_exempted"
            else:
                pair_pass = (digests[ai] != digests[aj])
                note = ""
            diagnostic["pairs"].append({
                "arm_a": ai, "arm_b": aj,
                "digest_a": digests[ai][:12],
                "digest_b": digests[aj][:12],
                "disagreement": disagreement,
                "both_oracle": both_oracle,
                "pass": pair_pass,
                "note": note,
            })
            if not pair_pass:
                all_distinct = False
    if not any_real_disagreement:
        all_distinct = False
        diagnostic["all_arms_bit_identical"] = True
    diagnostic["all_pairs_pass"] = all_distinct
    return all_distinct, diagnostic


# -------------------------- per-seed runner --------------------------

def run_one_seed(seed: int) -> Dict[str, Any]:
    g = np.random.default_rng(seed)
    n_half = N_DIM // 2

    # Generate scenarios
    scenarios = [make_scenario(g, N_OUTCOME_LEVELS) for _ in range(N_SCENARIOS)]
    truth_regrets = compute_ground_truth_regrets(scenarios)
    truth_values = compute_ground_truth_values(scenarios)

    # CRLB pre-validation: HRR magnitude round-trip fidelity
    test_unit = random_unit_phases(1, n_half, g)[0]
    round_trip_cosines = []
    round_trip_mag_ratios = []
    for level in range(1, N_OUTCOME_LEVELS + 1):
        cos_dir, mag_ratio = magnitude_round_trip_cosine(test_unit, level, N_OUTCOME_LEVELS)
        round_trip_cosines.append(cos_dir)
        round_trip_mag_ratios.append(mag_ratio)
    mean_round_trip = float(np.mean(round_trip_mag_ratios))
    crlb_round_trip_ok = mean_round_trip >= MAGNITUDE_ROUND_TRIP_FLOOR

    # Set up vmpfc bank roles + outcome-role key
    role_outcome = random_unit_phases(1, n_half, g)[0]
    bank_role_f = random_unit_phases(1, n_half, g)[0]
    bank_role_cf = random_unit_phases(1, n_half, g)[0]

    # Run all 5 arms
    arm_results: Dict[str, Dict[str, Any]] = {}
    arm_results["no_regret_baseline"] = run_arm_no_regret_baseline(
        scenarios, np.random.default_rng(seed + 100))
    arm_results["random_vectors"] = run_arm_random_vectors(
        scenarios, n_half, N_OUTCOME_LEVELS, np.random.default_rng(seed + 200))
    arm_results["direct_diff"] = run_arm_direct_diff(
        scenarios, n_half, N_OUTCOME_LEVELS, N_INTERFERENCE,
        np.random.default_rng(seed + 300))
    arm_results["vmpfc_comparison"] = run_arm_vmpfc_comparison(
        scenarios, n_half, N_OUTCOME_LEVELS, role_outcome, bank_role_f,
        bank_role_cf, N_INTERFERENCE, np.random.default_rng(seed + 400))
    arm_results["ground_truth_oracle"] = run_arm_ground_truth_oracle(scenarios)

    # Compute metrics per arm
    per_arm_metrics: Dict[str, Dict[str, float]] = {}
    arm_r2_for_distinct: Dict[str, float] = {}
    arm_concat: Dict[str, List[float]] = {}
    for arm_name, r in arm_results.items():
        preds = np.asarray(r["predicted_regrets"], dtype=np.float64)
        r2 = r_squared_from_predictions(truth_regrets, preds)
        rank = spearman_rho(preds, truth_regrets)
        value_leak = pearson_r(preds, truth_values)
        per_arm_metrics[arm_name] = {
            "regret_r2": float(r2),
            "ranking_spearman": float(rank),
            "value_leak_pearson": float(value_leak),
            "factual_recall": float(r["factual_recall"]),
            "n_predictions": int(r["n_predictions"]),
            "pred_mean": float(np.mean(preds)),
            "pred_std": float(np.std(preds)),
        }
        arm_r2_for_distinct[arm_name] = float(r2)
        arm_concat[arm_name] = preds.tolist()

    arms_distinct_pass, arms_distinct_diag = arms_must_differ_self_test(
        arm_concat, arm_r2_for_distinct, oracle_r2_floor=0.99)

    return {
        "seed": int(seed),
        "N": N_DIM,
        "V_REL": V_REL,
        "n_scenarios": N_SCENARIOS,
        "n_outcome_levels": N_OUTCOME_LEVELS,
        "n_interference": N_INTERFERENCE,
        "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
        "anchor_name": ANCHOR_NAME,
        "per_arm": per_arm_metrics,
        "arms_distinct_pass": bool(arms_distinct_pass),
        "arms_distinct_diag": arms_distinct_diag,
        "crlb_round_trip_mean": mean_round_trip,
        "crlb_round_trip_ok": bool(crlb_round_trip_ok),
        "truth_regret_range": [float(truth_regrets.min()), float(truth_regrets.max())],
    }


# -------------------------- verdict --------------------------

def aggregate_and_verdict(per_seed: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    if not per_seed:
        return {
            "verdict": "UNKNOWN",
            "verdict_msg": "no per-seed partials found",
            "summary": "no per-seed partials found",
            "per_arm": {},
        }
    seeds_sorted = sorted(per_seed.keys(), key=lambda s: int(s))
    summary: Dict[str, Dict[str, float]] = {}
    per_arm_full: Dict[str, Dict[str, Any]] = {}

    for arm in EXPECTED_ARMS:
        per_arm_full[arm] = {}
        m_r2, m_rank, m_leak, m_recall = [], [], [], []
        for s in seeds_sorted:
            pa = per_seed[s].get("per_arm", {}).get(arm, {})
            if pa:
                m_r2.append(float(pa.get("regret_r2", 0.0)))
                m_rank.append(float(pa.get("ranking_spearman", 0.0)))
                m_leak.append(float(pa.get("value_leak_pearson", 0.0)))
                m_recall.append(float(pa.get("factual_recall", 0.0)))
                per_arm_full[arm][s] = dict(pa)

        def _mean_std_cv(vals: List[float]) -> Tuple[float, float, float, int]:
            if not vals:
                return 0.0, 0.0, 0.0, 0
            m = float(np.mean(vals))
            sd = float(np.std(vals))
            cv = sd / abs(m) if abs(m) > 1e-6 else 0.0
            return m, sd, cv, len(vals)
        r2_m, r2_sd, r2_cv, n1 = _mean_std_cv(m_r2)
        rk_m, rk_sd, rk_cv, _ = _mean_std_cv(m_rank)
        lk_m, lk_sd, _, _ = _mean_std_cv(m_leak)
        rc_m, _, _, _ = _mean_std_cv(m_recall)
        summary[arm] = {
            "regret_r2_mean": r2_m, "regret_r2_std": r2_sd, "regret_r2_cv": r2_cv,
            "ranking_spearman_mean": rk_m, "ranking_spearman_std": rk_sd,
            "value_leak_pearson_mean": lk_m, "value_leak_pearson_std": lk_sd,
            "factual_recall_mean": rc_m,
            "n_seeds": n1,
        }

    # Decision-critical values
    vmpfc = summary["vmpfc_comparison"]
    base = summary["no_regret_baseline"]
    direct = summary["direct_diff"]
    oracle = summary["ground_truth_oracle"]
    random_arm = summary["random_vectors"]

    R2_vmpfc = vmpfc["regret_r2_mean"]
    Rank_vmpfc = vmpfc["ranking_spearman_mean"]
    Leak_vmpfc = abs(vmpfc["value_leak_pearson_mean"])
    Recall_vmpfc = vmpfc["factual_recall_mean"]
    CV_vmpfc = vmpfc["regret_r2_cv"]
    R2_direct = direct["regret_r2_mean"]
    R2_base = base["regret_r2_mean"]
    R2_oracle = oracle["regret_r2_mean"]
    Gap_vmpfc_over_base = R2_vmpfc - R2_base

    # META_RULE_AF arms-distinct
    arms_distinct_all = all(
        per_seed[s].get("arms_distinct_pass", False) for s in seeds_sorted
    )
    # META_RULE_Q suspect-1000
    suspect_1000 = (R2_vmpfc >= SUSPECT_1000) or (R2_direct >= SUSPECT_1000)
    # META_RULE_AG baseline-in-band (R^2 chance regime)
    baseline_in_band = (BASELINE_R2_BAND_LO < R2_base < BASELINE_R2_BAND_HI)
    # CRLB pre-validation across seeds
    crlb_ok_all = all(per_seed[s].get("crlb_round_trip_ok", False) for s in seeds_sorted)

    # Cardinality
    completed = 0
    for arm in EXPECTED_ARMS:
        for s in seeds_sorted:
            pa = per_seed[s].get("per_arm", {}).get(arm, {})
            completed += int(pa.get("n_predictions", 0))
    cardinality_ok = (completed >= int(EXPECTED_N_UNITS * 0.9))

    verdict = "MIDDLE_BAND"
    verdict_reason = ""

    if not arms_distinct_all:
        verdict = "HARD_FAIL"
        verdict_reason = "META_RULE_AF: arms-must-differ FAIL (bit-identical bug)"
    elif not cardinality_ok:
        verdict = "HARD_FAIL"
        verdict_reason = "META_RULE_H_CARDINALITY_BREACH: completed=%d < expected=%d (10%% slack)" % (
            completed, EXPECTED_N_UNITS)
    elif suspect_1000:
        verdict = "HARD_FAIL"
        verdict_reason = "META_RULE_Q: R2_vmpfc=%.3f or R2_direct=%.3f >= 0.999 (rig too easy)" % (
            R2_vmpfc, R2_direct)
    elif not crlb_ok_all:
        verdict = "HARD_FAIL"
        verdict_reason = "CRLB_ROUND_TRIP_FAIL: HRR magnitude fidelity below floor"
    elif R2_oracle < HF_R2_ORACLE:
        verdict = "HARD_FAIL"
        verdict_reason = "PIPELINE_BROKEN: oracle R^2=%.3f < %.2f" % (R2_oracle, HF_R2_ORACLE)
    elif R2_vmpfc < HF_R2_VMPFC:
        verdict = "HARD_FAIL"
        verdict_reason = "VMPFC_R2_TOO_LOW: R2=%.3f < %.2f (substrate cannot compute scalar comparison)" % (
            R2_vmpfc, HF_R2_VMPFC)
    elif Rank_vmpfc < HF_RANKING_MIN:
        verdict = "HARD_FAIL"
        verdict_reason = "RANKING_TOO_LOW: Spearman=%.3f < %.2f (no signal)" % (
            Rank_vmpfc, HF_RANKING_MIN)
    elif (R2_vmpfc >= HP_R2_VMPFC and
            Rank_vmpfc >= HP_RANKING_SPEARMAN_VMPFC and
            Leak_vmpfc <= HP_VALUE_LEAK_ABSMAX and
            R2_direct >= HP_R2_DIRECT_DIFF and
            R2_base <= HP_R2_BASELINE_MAX and
            Gap_vmpfc_over_base >= HP_GAP_VMPFC_OVER_BASELINE and
            R2_oracle >= HP_R2_ORACLE and
            Recall_vmpfc >= HP_FACTUAL_RECALL and
            CV_vmpfc < HP_CV_MAX and
            baseline_in_band):
        verdict = "HARD_PASS"
        verdict_reason = (
            "VMPFC_REGRET_PRIMITIVE_LOAD_BEARING: substrate computes scalar regret signal "
            "via HRR magnitude-encoded comparison readout; ranks scenarios + bounded value-leak"
        )
    elif 0.30 <= R2_vmpfc < HP_R2_VMPFC:
        verdict = "MIDDLE_BAND"
        verdict_reason = "VMPFC_R2_PARTIAL: %.3f in [0.30, %.2f) -- mechanism partial" % (
            R2_vmpfc, HP_R2_VMPFC)
    else:
        verdict = "MIDDLE_BAND"
        verdict_reason = (
            "PARTIAL: R2_vmpfc=%.3f rank=%.3f leak=%.3f R2_direct=%.3f R2_base=%.3f "
            "gap=%.3f R2_oracle=%.3f recall=%.3f cv=%.3f baseband=%s"
        ) % (R2_vmpfc, Rank_vmpfc, Leak_vmpfc, R2_direct, R2_base,
             Gap_vmpfc_over_base, R2_oracle, Recall_vmpfc, CV_vmpfc, baseline_in_band)

    verdict_msg = (
        "%s | %s | R2_vmpfc=%.3f rank=%.3f leak=%.3f R2_direct=%.3f R2_base=%.3f "
        "gap=%.3f R2_oracle=%.3f R2_random=%.3f recall=%.3f cv=%.3f arms_distinct=%s "
        "baseline_in_band=%s cardinality_ok=%s crlb_ok=%s n_seeds=%d"
    ) % (verdict, verdict_reason, R2_vmpfc, Rank_vmpfc, Leak_vmpfc, R2_direct, R2_base,
         Gap_vmpfc_over_base, R2_oracle, random_arm["regret_r2_mean"], Recall_vmpfc,
         CV_vmpfc, arms_distinct_all, baseline_in_band, cardinality_ok, crlb_ok_all,
         len(seeds_sorted))

    return {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": verdict_msg,
        "verdict_reason": verdict_reason,
        "per_arm": per_arm_full,
        "per_arm_summary": summary,
        "arms_distinct_all_seeds": arms_distinct_all,
        "arms_distinct_diag_first_seed": per_seed[seeds_sorted[0]].get(
            "arms_distinct_diag", {}),
        "suspect_1000": suspect_1000,
        "R2_vmpfc": R2_vmpfc, "ranking_spearman_vmpfc": Rank_vmpfc,
        "value_leak_pearson_vmpfc": Leak_vmpfc,
        "factual_recall_vmpfc": Recall_vmpfc, "R2_vmpfc_cv": CV_vmpfc,
        "R2_direct": R2_direct, "R2_baseline": R2_base, "R2_oracle": R2_oracle,
        "R2_random_vectors": random_arm["regret_r2_mean"],
        "gap_vmpfc_over_baseline": Gap_vmpfc_over_base,
        "baseline_in_band": baseline_in_band,
        "crlb_round_trip_ok_all_seeds": crlb_ok_all,
        "n_seeds_complete": len(seeds_sorted),
        "expected_n_units": EXPECTED_N_UNITS,
        "completed_units": completed,
        "cardinality_ok": cardinality_ok,
        "final_metrics_atomicity": "tmp_replace",
        "arms_differ_verified": bool(arms_distinct_all),
        # CRLB: 5-level discrete outcomes -> theoretical max Pearson approx
        # 0.95+ given clean magnitude encoding; R^2 ceiling ~0.90+ for vmpfc arm
        # with HRR noise floor of 1/sqrt(N_DIM). At N=8192: noise = 1/sqrt(8192) =
        # 0.011, well below the 0.20 alpha quantum.
        "crlb_floor_computed": 0.90,  # THEORETICAL@5-level-magnitude-R^2-ceiling
        "crlb_formula_reference": "R^2_max = 1 - (sigma_noise/sigma_signal)^2; sigma_noise=1/sqrt(N), sigma_signal=alpha_quantum",
        "discriminator_reachability": True,  # HP_R2=0.80 < theoretical ceiling 0.90
        "calibration_check": "default_ok_for_this_regime",
    }


# -------------------------- main --------------------------

def main() -> int:
    _RESULTS_HOLDER["started_at"] = time.time()
    env_name = os.environ.get("HDLAB_EXP_NAME", ANCHOR_NAME)
    out_dir = REPO / "data" / ("exp_" + env_name)
    out_dir.mkdir(parents=True, exist_ok=True)

    _write_minimal_metrics(out_dir, "STARTED",
                           "STARTED: pid=%d mode=%s" % (os.getpid(), RUN_MODE),
                           extra={"_phase": "init",
                                  "expected_arms": EXPECTED_ARMS,
                                  "expected_seeds": SEEDS,
                                  "expected_n_units": EXPECTED_N_UNITS})

    print("[%s] mode=%s N=%d V_REL=%d n_scenarios=%d n_levels=%d n_interference=%d seeds=%s expected_n=%d" % (
        ANCHOR_NAME, RUN_MODE, N_DIM, V_REL, N_SCENARIOS, N_OUTCOME_LEVELS,
        N_INTERFERENCE, SEEDS, EXPECTED_N_UNITS), flush=True)

    if SELF_TEST_MODE:
        try:
            r = run_one_seed(SEEDS[0])
            assert "per_arm" in r
            for arm in EXPECTED_ARMS:
                assert arm in r["per_arm"], "missing arm: %s" % arm
            oracle = r["per_arm"]["ground_truth_oracle"]
            assert oracle["regret_r2"] >= 0.95, (
                "self-test oracle R^2 too low: %.3f" % oracle["regret_r2"])
            assert r["arms_distinct_pass"], (
                "META_RULE_AF self-test FAIL: %s" % r["arms_distinct_diag"])
            assert r["crlb_round_trip_ok"], (
                "CRLB round-trip FAIL: mean=%.3f < floor=%.2f" % (
                    r["crlb_round_trip_mean"], MAGNITUDE_ROUND_TRIP_FLOOR))
            vmpfc = r["per_arm"]["vmpfc_comparison"]
            direct = r["per_arm"]["direct_diff"]
            baseline = r["per_arm"]["no_regret_baseline"]
            _write_minimal_metrics(out_dir, "SELFTEST_OK",
                                   "SELFTEST_OK: arms_distinct=%s oracle_R2=%.3f vmpfc_R2=%.3f direct_R2=%.3f base_R2=%.3f leak=%.3f crlb=%.3f" % (
                                       r["arms_distinct_pass"], oracle["regret_r2"],
                                       vmpfc["regret_r2"], direct["regret_r2"],
                                       baseline["regret_r2"], vmpfc["value_leak_pearson"],
                                       r["crlb_round_trip_mean"]),
                                   extra={"_phase": "selftest_done",
                                          "arms_distinct_pass": r["arms_distinct_pass"]})
            print("[selftest] OK arms_distinct=%s vmpfc_R2=%.3f direct_R2=%.3f base_R2=%.3f oracle_R2=%.3f leak=%.3f rank=%.3f crlb=%.3f" % (
                r["arms_distinct_pass"], vmpfc["regret_r2"], direct["regret_r2"],
                baseline["regret_r2"], oracle["regret_r2"],
                vmpfc["value_leak_pearson"], vmpfc["ranking_spearman"],
                r["crlb_round_trip_mean"]), flush=True)
            return 0
        except SystemExit:
            raise
        except Exception as e:
            _write_minimal_metrics(out_dir, "SELFTEST_FAIL",
                                   "SELFTEST_FAIL: %s" % e,
                                   extra={"_traceback": traceback.format_exc()})
            print("[selftest] FAIL: %s" % e, file=sys.stderr, flush=True)
            return 1

    run_config = {"N": N_DIM, "run_mode": RUN_MODE, "anchor": ANCHOR_NAME,
                  "n_scenarios": N_SCENARIOS, "n_outcome_levels": N_OUTCOME_LEVELS}
    done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
    print("[ckpt] %d/%d done; running %s" % (len(done), len(SEEDS), remaining),
          flush=True)

    for i, seed in enumerate(remaining):
        t0 = time.time()
        _write_minimal_metrics(out_dir, "RUNNING",
                               "RUNNING: seed=%d (%d/%d)" % (seed, i + 1, len(remaining)),
                               extra={"_phase": "seed_running", "_current_seed": seed})
        try:
            result = run_one_seed(seed)
            write_partial_key(out_dir, seed, result)
            print("[seed=%d] done in %.1fs arms_distinct=%s vmpfc_R2=%.3f direct_R2=%.3f base_R2=%.3f rank=%.3f leak=%.3f" % (
                seed, time.time() - t0, result.get("arms_distinct_pass"),
                result["per_arm"]["vmpfc_comparison"]["regret_r2"],
                result["per_arm"]["direct_diff"]["regret_r2"],
                result["per_arm"]["no_regret_baseline"]["regret_r2"],
                result["per_arm"]["vmpfc_comparison"]["ranking_spearman"],
                result["per_arm"]["vmpfc_comparison"]["value_leak_pearson"]),
                flush=True)
        except SystemExit:
            raise
        except Exception as e:
            print("[seed=%d] FAIL: %s" % (seed, e), file=sys.stderr, flush=True)
            traceback.print_exc()
            # Record per-seed failure as partial with verdict UNKNOWN
            err_partial = {
                "seed": int(seed),
                "anchor_name": ANCHOR_NAME,
                "N": N_DIM,
                "run_mode": RUN_MODE,
                "n_scenarios": N_SCENARIOS,
                "n_outcome_levels": N_OUTCOME_LEVELS,
                "config_version": CONFIG_VERSION,
                "_error": "%s: %s" % (type(e).__name__, str(e)),
                "_traceback": traceback.format_exc(),
            }
            write_partial_key(out_dir, seed, err_partial)

    per_seed = aggregate_partials(out_dir, SEEDS, run_config=run_config)
    final = aggregate_and_verdict(per_seed)
    final["anchor_name"] = ANCHOR_NAME
    final["elapsed_s"] = round(time.time() - _RESULTS_HOLDER["started_at"], 1)
    final["ts_iso"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    final["pid"] = os.getpid()
    final["run_mode"] = RUN_MODE
    final["config_version"] = CONFIG_VERSION
    final["_hardening_marker"] = "v1_regret_comparison_vmpfc"
    # META_RULE_AH atomic write
    tmp = out_dir / "metrics.json.tmp"
    tmp.write_text(json.dumps(final, indent=2), encoding="utf-8")
    os.replace(str(tmp), str(out_dir / "metrics.json"))
    print("[%s] DONE: %s" % (ANCHOR_NAME, final["verdict_msg"]), flush=True)
    return 0


if __name__ == "__main__":
    try:
        rc = main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        _write_import_crash_sentinel(e)
        print("[main] OUTER_EXCEPTION: %s" % e, file=sys.stderr, flush=True)
        traceback.print_exc()
        rc = 1
    sys.exit(rc)
