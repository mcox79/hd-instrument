"""exp_attention_salience_reliability_gate_derived_v1.py

ATTENTION / SALIENCE RELIABILITY-GATE -- DERIVED-SIGNAL CORRECTION of exp_attention_salience_reliability_gate_v1.

v1 (preregs/attention_salience_reliability_gate_v1_2026-07-19.md) landed HARD_PASS but adversarial VET
(data/substrate_index/math/atoms.jsonl, MEASURED_MECHANISM downgrade) found the per-observation confidence
score was an EXOGENOUS Beta(8,2)|Beta(2,8) proxy KEYED on the hidden correctness label (measured
conf-vs-correctness AUC = 0.999, near-oracle leak, not the claimed 0.85-0.90 -- a material miscite). The
atom's revival_criteria requires: (a) a DERIVED signal from real input properties (no injection), (b) a
MEASURED (not stipulated) correctness-AUC honestly reported, in-band <0.90, and (c) a NON-CEILING do-no-harm
test. This cell is that correction.

DERIVED SIGNAL (no injection; per-observation, computed only from the item's OTHER observations):
  loo_j   = sum_{k != j} obs_k                  (leave-one-out sum of the OTHER observations for this item)
  score_j = cosine(obs_j, loo_j)                (cross-observation / cross-view consistency)
A recurring TRUE observation reinforces other TRUE draws of the same item (identical vector, positive
cosine); an i.i.d. random corruption has ~zero expected correlation with anything else. NEVER uses the
hidden is_correct label -- score is purely a function of the observed data.

MECHANISM (see preregs/attention_salience_reliability_gate_derived_v1_2026-07-20.md for full pre-reg +
dev-sim regime search + pre-registered failure hypothesis):
  V items, half "reliable-source" (r=0.45) half "unreliable-source" (r=0.25) -- LOWERED from v1's
  (0.92, 0.15) specifically so the reliable-source subset is NOT at ceiling (v1's do-no-harm check was
  vacuous: acc_ungated_rel=1.000 on every seed). n_obs in [4,6] per item (narrowed from v1's [6,10]).

  Consolidation = weighted bipolar sum -> sign cleanup: consolidated_i = sign(sum_j w_j * obs_j).
  ARMS (one variable = the weight function w_j; derived score computation shared across all arms):
    ungated            : w_j = 1                          (REAL BASELINE -- today's default)
    hard_gate           : w_j = 1[score_j >= TAU]           (MECHANISM -- hard suppression, TAU=0.0)
    soft_multiplier     : w_j = clip(score_j, 0, 1)         (MECHANISM -- continuous weight)
    shuffled_hard_gate  : hard_gate on score PERMUTED within-item (MUST-FAIL CONTROL)
    shuffled_multiplier : soft_multiplier on score PERMUTED within-item (MUST-FAIL CONTROL)
    oracle              : w_j = hidden true-correctness label (DIAGNOSTIC CEILING ONLY, not HARD_PASS-scoped)

  METRIC: nearest-neighbor cleanup accuracy of consolidated_i against the full V-item codebook, split by
  item-reliability tier (_unrel = PRIMARY/LOAD-BEARING; _rel = do-no-harm, NOW NON-CEILING; _all = overall).
  AUC: correctness-AUC of `score` vs hidden is_correct, reported BOTH pooled (all observations) and
  restricted to the _unrel tier (the load-bearing population); auc_unrel is the PRIMARY declared/gating
  number (auc_pooled is inflated by the easy reliable-source population -- see pre-reg for the honest
  reasoning on why, disclosed not hidden).

PRE-REG BANDS (locked; see pre-reg doc for full HP_SCOPE + dev-sim iteration log):
  HARD_PASS: 0.55 <= auc_unrel <= 0.90 AND mean_5seed(delta_hard_unrel) >= 0.05 AND
             mean_5seed(delta_mult_unrel) >= 0.05 AND >=4/5 seeds positive-direction on both AND
             shuffled controls <= 0.00 delta on ALL 5 seeds AND do-no-harm (delta_*_rel >= -0.03) AND
             baseline_rel_non_ceiling (ungated_rel < 0.97 every seed) AND baseline_in_band.
  HARD_FAIL: auc_unrel < 0.55 (HARD_FAIL_NO_SIGNAL) OR auc_unrel > 0.90 (DISQUALIFIED_LEAK_PROXY) OR
             mean_5seed(delta_hard_unrel) <= 0.02 AND mean_5seed(delta_mult_unrel) <= 0.02
             (HARD_FAIL_INERT_OR_HARMFUL) OR baseline_in_band/baseline_rel_non_ceiling violated (non-test).
  MIDDLE_BAND: anything else.

DEFLATE: self-contained numpy; ASCII-only; local-runnable foreground (<1s total, all 5 seeds); glass-box;
no external LLM; no queue dispatch (compute-proportionality -- a directional gate question).

# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (hash over per-arm consolidated-vector sets)
# - final_metrics_atomicity: tmp_replace (single-shot, <1s total, no iteration)
# - except SystemExit/KeyboardInterrupt: raise BEFORE except Exception (no BaseException)
# - crlb_n/a: not a JL/capacity cell; bottleneck is derived-signal information content on singleton-true items
# - baseline_in_band at smoke (META_RULE_AG; 0.05 < acc_ungated_unrel < 0.95)
# - baseline_rel_non_ceiling at smoke (NEW gate vs v1: acc_ungated_rel < 0.97, do-no-harm not vacuous)
# - discriminator survives scale: Option A -- smoke IS full-N/full-V (1 seed), no separate scale-up regime
# - HARD_PASS strictly above floor (0.05 mean lift, not >=0); HARD_FAIL <=0.02 (ties/loses)
# - AUC in-band gate: 0.55 <= auc_unrel <= 0.90 (>0.90 = leak/proxy disqualify; <0.55 = no signal)
# - HP_SCOPE per-arm declaration: oracle + shuffled arms explicitly OUT of HARD_PASS/HARD_FAIL scope
# - cardinality_ok: EXPECTED_N_UNITS = len(SEEDS); verdict counts len(per_seed)
# - per-unit failure-class instrumentation (no bare except)
# - calibration_check: default_ok_for_this_regime (TAU=0.0 at the analytical zero-crossing, locked BEFORE
#   measuring full-run lift; dev-sim tau-sweep found no config materially better, see pre-reg)
# - all numbers in comments tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@
"""
from __future__ import annotations

# OMP/OpenBLAS single-thread BEFORE numpy import (bit-repro; OpenBLAS DYNAMIC_ARCH non-determinism)
import os as _os
_os.environ.setdefault("OMP_NUM_THREADS", "1")
_os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
_os.environ.setdefault("MKL_NUM_THREADS", "1")
_os.environ.setdefault("NUMEXPR_NUM_THREADS", "1")

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
import platform
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

ANCHOR_NAME = "attention_salience_reliability_gate_derived_v1"

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true", dest="self_test")
_ARGS, _ = _ap.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = "_smoke" in _HDLAB_EXP_NAME.lower()
RUN_MODE = ("smoke" if (_ARGS.smoke or _ARGS.self_test or _NAME_SAYS_SMOKE)
            else os.environ.get("HDLAB_RUN_MODE", "full").lower())
SMOKE = RUN_MODE == "smoke"
SELF_TEST_MODE = bool(_ARGS.self_test)

# --- Config (Option A: smoke = SAME regime, 1 seed; full = 5 seeds) --------------------------------------
V = 100                       # MEASURED@dev-sim: total items (50 reliable-source / 50 unreliable-source)
N = 64                        # bipolar vector dimensionality (down from v1's 128; see pre-reg regime search)
N_RELIABLE = V // 2
N_UNRELIABLE = V - N_RELIABLE
R_RELIABLE = 0.45             # MEASURED@dev-sim: lowered from v1's 0.92 (and from an initial 0.55 that
                              # still hit 0.98 on one seed) so rel-tier is NOT at ceiling on ANY of the 5 seeds
R_UNRELIABLE = 0.25           # MEASURED@dev-sim: tuned so baseline lands in-band (see pre-reg regime search)
N_OBS_MIN, N_OBS_MAX = 4, 6   # observations per item (narrowed from v1's [6,10])
TAU = 0.0                     # hard-gate threshold; analytical positive/negative-correlation zero-crossing
SEEDS = [7] if SMOKE else [7, 17, 23, 31, 41]
EXPECTED_N_UNITS = len(SEEDS)

# Pre-registered bands (envelope-fail-bands; LOCKED, see preregs/attention_salience_reliability_gate_derived_v1_2026-07-20.md)
AUC_BAND = (0.55, 0.90)       # auc_unrel must land inside this (open) band
HP_MEAN_LIFT_FLOOR = 0.05     # mean_5seed(delta_{hard,mult}_unrel) must clear this for HARD_PASS
HP_MAJORITY_SEEDS = 4         # of 5, must show positive-direction delta
HP_CONTROL_CEIL = 0.00        # shuffled-control delta must be <= this on ALL seeds
HP_DO_NO_HARM_FLOOR = -0.03   # delta_*_rel must clear this (mean)
HF_MEAN_LIFT_CEIL = 0.02      # mean_5seed(delta_{hard,mult}_unrel) <= this -> HARD_FAIL (ties/loses)
BASELINE_BAND = (0.05, 0.95)  # META_RULE_AG: acc_ungated_unrel must be strictly inside this band
BASELINE_REL_NON_CEILING = 0.97  # acc_ungated_rel must be strictly BELOW this on every seed


def _write_start_marker(output_dir: Path, expected_n_units: int) -> None:
    marker = {
        "pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR_NAME, "run_mode": RUN_MODE,
        "expected_n_units": expected_n_units, "host": platform.node(),
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    tmp = output_dir / "_start_marker.json.tmp"
    final = output_dir / "_start_marker.json"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, final)


def _write_crash_metrics(output_dir: Path, exc: BaseException) -> None:
    diag = {
        "verdict": "CELL_CRASHED",
        "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
        "summary": f"CELL_CRASHED: {type(exc).__name__}",
        "elapsed_s": 0.0,
        "traceback": traceback.format_exc()[:5000],
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(),
        "anchor_name": ANCHOR_NAME,
        "run_mode": RUN_MODE,
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    tmp = output_dir / "metrics.json.tmp"
    final = output_dir / "metrics.json"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, final)


def _bipolar(rng: np.random.Generator, shape) -> np.ndarray:
    x = (rng.integers(0, 2, size=shape) * 2 - 1).astype(np.float32)
    return x


def _cleanup_sign(v: np.ndarray) -> np.ndarray:
    s = np.sign(v)
    s[s == 0] = 1.0
    return s


def _cons_from_weights(obs: np.ndarray, weights: np.ndarray) -> np.ndarray:
    """Weighted bipolar sum -> sign cleanup. Falls back to uniform if all weights ~0 (empty hard-gate)."""
    n_obs = obs.shape[0]
    w = weights if float(weights.sum()) >= 1e-9 else np.ones(n_obs, dtype=np.float32)
    return _cleanup_sign((obs * w[:, None]).sum(axis=0))


def _auc(scores: np.ndarray, labels: np.ndarray) -> float:
    """Mann-Whitney U / rank-sum AUC of `scores` predicting `labels` (True=positive). NaN if degenerate."""
    n_pos = int(labels.sum())
    n_neg = int(len(labels) - n_pos)
    if n_pos == 0 or n_neg == 0:
        return float("nan")
    order = np.argsort(scores)
    ranks = np.empty_like(order, dtype=np.float64)
    ranks[order] = np.arange(1, len(scores) + 1)
    return float((ranks[labels].sum() - n_pos * (n_pos + 1) / 2.0) / (n_pos * n_neg))


def run_one_seed(seed: int) -> Dict:
    """Run all 6 arms for one seed over V items using the DERIVED (not injected) reliability score;
    return per-arm accuracy (all/unrel/rel) + pooled/unrel AUC + diagnostics."""
    rng = np.random.default_rng(seed)
    codebook = _bipolar(rng, (V, N))
    reliab = np.concatenate([
        np.full(N_RELIABLE, R_RELIABLE, dtype=np.float64),
        np.full(N_UNRELIABLE, R_UNRELIABLE, dtype=np.float64),
    ])
    is_unreliable = np.concatenate([
        np.zeros(N_RELIABLE, dtype=bool), np.ones(N_UNRELIABLE, dtype=bool),
    ])
    n_obs_per_item = rng.integers(N_OBS_MIN, N_OBS_MAX + 1, size=V)

    arm_names = ["ungated", "hard_gate", "soft_multiplier", "shuffled_hard_gate", "shuffled_multiplier", "oracle"]
    correct: Dict[str, List[bool]] = {a: [] for a in arm_names}
    consolidated_digest_inputs: Dict[str, List[np.ndarray]] = {a: [] for a in arm_names}

    scores_all: List[float] = []
    labels_all: List[bool] = []
    scores_unrel: List[float] = []
    labels_unrel: List[bool] = []

    for i in range(V):
        n_obs = int(n_obs_per_item[i])
        true_v = codebook[i]
        obs = np.empty((n_obs, N), dtype=np.float32)
        c_true = np.empty(n_obs, dtype=bool)
        for j in range(n_obs):
            is_correct = rng.random() < reliab[i]
            c_true[j] = is_correct
            obs[j] = true_v if is_correct else _bipolar(rng, (N,))

        # --- DERIVED reliability score (NO injection): leave-one-out cross-observation consistency ---
        total = obs.sum(axis=0)
        score = np.empty(n_obs, dtype=np.float64)
        for j in range(n_obs):
            loo = total - obs[j]
            denom = float(np.linalg.norm(obs[j]) * np.linalg.norm(loo)) + 1e-9
            score[j] = float(np.dot(obs[j], loo) / denom) if denom > 1e-9 else 0.0

        scores_all.extend(score.tolist())
        labels_all.extend(c_true.tolist())
        if is_unreliable[i]:
            scores_unrel.extend(score.tolist())
            labels_unrel.extend(c_true.tolist())

        cons: Dict[str, np.ndarray] = {}
        cons["ungated"] = _cons_from_weights(obs, np.ones(n_obs, dtype=np.float32))
        cons["hard_gate"] = _cons_from_weights(obs, (score >= TAU).astype(np.float32))
        cons["soft_multiplier"] = _cons_from_weights(obs, np.clip(score, 0.0, 1.0).astype(np.float32))
        score_shuf = rng.permutation(score)
        cons["shuffled_hard_gate"] = _cons_from_weights(obs, (score_shuf >= TAU).astype(np.float32))
        cons["shuffled_multiplier"] = _cons_from_weights(obs, np.clip(score_shuf, 0.0, 1.0).astype(np.float32))
        cons["oracle"] = _cons_from_weights(obs, c_true.astype(np.float32))

        for a in arm_names:
            sims = codebook @ cons[a]
            hit = bool(int(np.argmax(sims)) == i)
            correct[a].append(hit)
            consolidated_digest_inputs[a].append(cons[a])

    out: Dict = {"seed": seed}
    for a in arm_names:
        c = np.array(correct[a])
        out[f"{a}_all"] = float(c.mean())
        out[f"{a}_unrel"] = float(c[is_unreliable].mean())
        out[f"{a}_rel"] = float(c[~is_unreliable].mean())

    out["auc_pooled"] = _auc(np.array(scores_all), np.array(labels_all, dtype=bool))
    out["auc_unrel"] = _auc(np.array(scores_unrel), np.array(labels_unrel, dtype=bool))

    # arms-must-differ hash (META_RULE_AF): digest each arm's stacked consolidated-vector matrix
    digests = {}
    for a in arm_names:
        mat = np.stack(consolidated_digest_inputs[a]).astype(np.int8)
        digests[a] = hashlib.sha256(mat.tobytes()).hexdigest()
    out["_arm_digests"] = digests
    return out


def _arms_must_differ(digests_by_seed: List[Dict[str, str]]) -> Dict[str, bool]:
    """META_RULE_AF: verify arms produce distinct outputs (using seed=SEEDS[0] as the representative check)."""
    d = digests_by_seed[0]
    names = list(d.keys())
    pairs_ok = {}
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            pairs_ok[f"{a}__vs__{b}"] = (d[a] != d[b])
    return pairs_ok


def aggregate_and_verdict(per_seed: List[Dict]) -> Dict:
    seeds = [r["seed"] for r in per_seed]

    def deltas(arm: str, tier: str) -> List[float]:
        return [r[f"{arm}_{tier}"] - r[f"ungated_{tier}"] for r in per_seed]

    d_hard_unrel = deltas("hard_gate", "unrel")
    d_mult_unrel = deltas("soft_multiplier", "unrel")
    d_hard_rel = deltas("hard_gate", "rel")
    d_mult_rel = deltas("soft_multiplier", "rel")
    d_shuf_hard_unrel = deltas("shuffled_hard_gate", "unrel")
    d_shuf_mult_unrel = deltas("shuffled_multiplier", "unrel")
    d_oracle_unrel = deltas("oracle", "unrel")

    mean_d_hard_unrel = float(np.mean(d_hard_unrel))
    mean_d_mult_unrel = float(np.mean(d_mult_unrel))
    mean_d_hard_rel = float(np.mean(d_hard_rel))
    mean_d_mult_rel = float(np.mean(d_mult_rel))

    n_pos_hard = sum(1 for x in d_hard_unrel if x > 0)
    n_pos_mult = sum(1 for x in d_mult_unrel if x > 0)

    baseline_unrel_vals = [r["ungated_unrel"] for r in per_seed]
    baseline_rel_vals = [r["ungated_rel"] for r in per_seed]
    baseline_in_band = all(BASELINE_BAND[0] < v < BASELINE_BAND[1] for v in baseline_unrel_vals)
    baseline_rel_non_ceiling = all(v < BASELINE_REL_NON_CEILING for v in baseline_rel_vals)

    auc_unrel_vals = [r["auc_unrel"] for r in per_seed]
    auc_pooled_vals = [r["auc_pooled"] for r in per_seed]
    mean_auc_unrel = float(np.mean(auc_unrel_vals))
    mean_auc_pooled = float(np.mean(auc_pooled_vals))
    auc_in_band = AUC_BAND[0] <= mean_auc_unrel <= AUC_BAND[1]

    control_ok = (all(x <= HP_CONTROL_CEIL for x in d_shuf_hard_unrel)
                  and all(x <= HP_CONTROL_CEIL for x in d_shuf_mult_unrel))
    do_no_harm_ok = (mean_d_hard_rel >= HP_DO_NO_HARM_FLOOR and mean_d_mult_rel >= HP_DO_NO_HARM_FLOOR)
    majority_ok = (n_pos_hard >= HP_MAJORITY_SEEDS and n_pos_mult >= HP_MAJORITY_SEEDS)
    lift_ok = (mean_d_hard_unrel >= HP_MEAN_LIFT_FLOOR and mean_d_mult_unrel >= HP_MEAN_LIFT_FLOOR)

    hard_fail_lift = (mean_d_hard_unrel <= HF_MEAN_LIFT_CEIL and mean_d_mult_unrel <= HF_MEAN_LIFT_CEIL)

    if not baseline_in_band:
        verdict = "NON_TEST_BASELINE_SATURATED_OR_FLOORED"
        verdict_msg = (f"baseline_in_band violated: ungated_unrel per seed = {baseline_unrel_vals}; "
                        f"outside band {BASELINE_BAND}; regime re-spec needed, not a mechanism verdict.")
    elif not baseline_rel_non_ceiling:
        verdict = "NON_TEST_DO_NO_HARM_VACUOUS_CEILING"
        verdict_msg = (f"baseline_rel_non_ceiling violated: ungated_rel per seed = {baseline_rel_vals}; "
                        f">= {BASELINE_REL_NON_CEILING} on at least one seed; do-no-harm check would be "
                        f"vacuous (this is the v1 flaw this cell exists to fix). Regime re-spec needed.")
    elif mean_auc_unrel > AUC_BAND[1]:
        verdict = "DISQUALIFIED_LEAK_PROXY"
        verdict_msg = (f"auc_unrel={mean_auc_unrel:.4f} > {AUC_BAND[1]} -- derived signal is near-oracle on "
                        f"the load-bearing subset, a construction artifact (v1-class leak), not a genuine "
                        f"reliability estimate. auc_pooled={mean_auc_pooled:.4f} (reported, not gating). "
                        f"Not evaluated for lift; disqualified before mechanism claim.")
    elif mean_auc_unrel < AUC_BAND[0]:
        verdict = "HARD_FAIL_NO_SIGNAL"
        verdict_msg = (f"auc_unrel={mean_auc_unrel:.4f} < {AUC_BAND[0]} -- derived signal carries no usable "
                        f"correctness information on the load-bearing subset. auc_pooled={mean_auc_pooled:.4f}.")
    elif lift_ok and majority_ok and control_ok and do_no_harm_ok:
        verdict = "HARD_PASS"
        verdict_msg = (f"HARD_PASS: DERIVED reliability signal (auc_unrel={mean_auc_unrel:.4f} in-band "
                        f"{AUC_BAND}, auc_pooled={mean_auc_pooled:.4f} reported) measurably improves "
                        f"consolidation on the low-reliability item subset. "
                        f"mean_delta_hard_unrel={mean_d_hard_unrel:.4f} mean_delta_mult_unrel={mean_d_mult_unrel:.4f} "
                        f"(both >= {HP_MEAN_LIFT_FLOOR}); positive-direction {n_pos_hard}/{len(seeds)} (hard) "
                        f"{n_pos_mult}/{len(seeds)} (mult) >= {HP_MAJORITY_SEEDS}/5; shuffled controls all "
                        f"<= {HP_CONTROL_CEIL} (max_shuf_hard={max(d_shuf_hard_unrel):.4f} "
                        f"max_shuf_mult={max(d_shuf_mult_unrel):.4f}); do-no-harm "
                        f"mean_delta_hard_rel={mean_d_hard_rel:.4f} mean_delta_mult_rel={mean_d_mult_rel:.4f} "
                        f"(both >= {HP_DO_NO_HARM_FLOOR}) on a NON-CEILING rel-tier (ungated_rel per seed "
                        f"{baseline_rel_vals}, all < {BASELINE_REL_NON_CEILING}); "
                        f"oracle ceiling mean_delta_unrel={float(np.mean(d_oracle_unrel)):.4f} (diagnostic only).")
    elif hard_fail_lift:
        verdict = "HARD_FAIL_INERT_OR_HARMFUL"
        verdict_msg = (f"HARD_FAIL: DERIVED signal is IN-BAND and non-injected (auc_unrel={mean_auc_unrel:.4f}, "
                        f"auc_pooled={mean_auc_pooled:.4f}) but does NOT translate into a usable gate: "
                        f"mean_delta_hard_unrel={mean_d_hard_unrel:.4f} mean_delta_mult_unrel={mean_d_mult_unrel:.4f} "
                        f"both <= {HF_MEAN_LIFT_CEIL} (ties/loses ungated baseline). shuffled-control deltas "
                        f"hard={d_shuf_hard_unrel} mult={d_shuf_mult_unrel}. Per pre-registered mechanism "
                        f"hypothesis: with R_UNRELIABLE={R_UNRELIABLE} and n_obs in [{N_OBS_MIN},{N_OBS_MAX}], "
                        f"most unreliable items carry 0-1 true observations; a singleton true draw has no "
                        f"reinforcing partner and is statistically indistinguishable from a corrupt draw under "
                        f"this cross-consistency score, so gating on it is a wash-to-negative even though the "
                        f"AGGREGATE auc_unrel looks decent (driven by the minority of items with >=2 true "
                        f"draws, which the ungated baseline already handles well). Genuine negative: derived "
                        f"cross-observation consistency does not close the reliability-estimation gap here.")
    else:
        verdict = "MIDDLE_BAND"
        verdict_msg = (f"MIDDLE_BAND: partial signal, gates not all cleared. auc_unrel={mean_auc_unrel:.4f} "
                        f"auc_pooled={mean_auc_pooled:.4f} mean_delta_hard_unrel={mean_d_hard_unrel:.4f} "
                        f"mean_delta_mult_unrel={mean_d_mult_unrel:.4f} lift_ok={lift_ok} majority_ok={majority_ok} "
                        f"control_ok={control_ok} do_no_harm_ok={do_no_harm_ok} "
                        f"(n_pos_hard={n_pos_hard} n_pos_mult={n_pos_mult}).")

    return {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": verdict_msg,
        "per_seed": per_seed,
        "auc_unrel_mean": mean_auc_unrel,
        "auc_pooled_mean": mean_auc_pooled,
        "auc_unrel_per_seed": auc_unrel_vals,
        "auc_pooled_per_seed": auc_pooled_vals,
        "auc_in_band": auc_in_band,
        "mean_delta_hard_unrel": mean_d_hard_unrel,
        "mean_delta_mult_unrel": mean_d_mult_unrel,
        "mean_delta_hard_rel": mean_d_hard_rel,
        "mean_delta_mult_rel": mean_d_mult_rel,
        "delta_hard_unrel_per_seed": d_hard_unrel,
        "delta_mult_unrel_per_seed": d_mult_unrel,
        "delta_shuffled_hard_unrel_per_seed": d_shuf_hard_unrel,
        "delta_shuffled_mult_unrel_per_seed": d_shuf_mult_unrel,
        "delta_oracle_unrel_per_seed": d_oracle_unrel,
        "baseline_unrel_per_seed": baseline_unrel_vals,
        "baseline_rel_per_seed": baseline_rel_vals,
        "baseline_in_band": baseline_in_band,
        "baseline_rel_non_ceiling": baseline_rel_non_ceiling,
        "n_pos_hard": n_pos_hard,
        "n_pos_mult": n_pos_mult,
        "hp_scope_note": ("oracle + shuffled_hard_gate + shuffled_multiplier are diagnostic/control arms, "
                           "explicitly OUT of HARD_PASS/HARD_FAIL decision scope (HP_SCOPE per pre-reg)."),
        "revival_of": "data/exp_attention_salience_reliability_gate_v1/metrics.json (v1, MEASURED_MECHANISM construction-proof per atoms.jsonl)",
    }


def _self_test() -> None:
    """Tiny, deterministic, real-code-path exercise (V=100,N=64,seed=7 -- same regime as smoke/full,
    just 1 seed) + arms-must-differ assertion + baseline-in-band + non-ceiling-rel assertions."""
    t0 = time.perf_counter()
    r = run_one_seed(7)
    assert 0.0 < r["ungated_unrel"] < 1.0, f"self-test: ungated_unrel degenerate ({r['ungated_unrel']})"
    assert 0.0 <= r["ungated_rel"] <= 1.0
    assert r["ungated_rel"] < BASELINE_REL_NON_CEILING, (
        f"self-test: ungated_rel={r['ungated_rel']} at/above ceiling {BASELINE_REL_NON_CEILING} "
        f"-- do-no-harm check would be vacuous (the v1 flaw this cell exists to fix)")
    pairs_ok = _arms_must_differ([r["_arm_digests"]])
    n_diff = sum(1 for v in pairs_ok.values() if v)
    assert n_diff == len(pairs_ok), f"META_RULE_AF VIOLATION: some arm pairs bit-identical: {pairs_ok}"
    d_hard = r["hard_gate_unrel"] - r["ungated_unrel"]
    d_mult = r["soft_multiplier_unrel"] - r["ungated_unrel"]
    d_shuf_hard = r["shuffled_hard_gate_unrel"] - r["ungated_unrel"]
    d_shuf_mult = r["shuffled_multiplier_unrel"] - r["ungated_unrel"]
    print(f"[self-test] ungated_unrel={r['ungated_unrel']:.3f} ungated_rel={r['ungated_rel']:.3f} "
          f"(non_ceiling={r['ungated_rel'] < BASELINE_REL_NON_CEILING}) "
          f"hard_gate_unrel={r['hard_gate_unrel']:.3f} (delta={d_hard:+.3f}) "
          f"soft_multiplier_unrel={r['soft_multiplier_unrel']:.3f} (delta={d_mult:+.3f}) "
          f"shuffled_hard_delta={d_shuf_hard:+.3f} shuffled_mult_delta={d_shuf_mult:+.3f} "
          f"auc_unrel={r['auc_unrel']:.4f} auc_pooled={r['auc_pooled']:.4f}", flush=True)
    assert n_diff == len(pairs_ok)
    elapsed = time.perf_counter() - t0
    print(f"[self-test] PASS in {elapsed:.3f}s (arms_differ={n_diff}/{len(pairs_ok)} pairs distinct)", flush=True)


def main() -> None:
    out_dir = REPO / "data" / f"exp_{ANCHOR_NAME}" if not SMOKE else REPO / "data" / f"exp_{ANCHOR_NAME}_smoke"
    _write_start_marker(out_dir, EXPECTED_N_UNITS)

    if SELF_TEST_MODE:
        _self_test()
        diag = {
            "verdict": "SELFTEST_OK", "verdict_msg": "SELFTEST_OK: real code path exercised, arms differ, non-ceiling rel-tier",
            "summary": "SELFTEST_OK", "elapsed_s": 0.01, "run_mode": "self_test",
            "ts_iso": datetime.now(timezone.utc).isoformat(), "anchor_name": ANCHOR_NAME,
        }
        tmp = out_dir / "metrics.json.tmp"
        final = out_dir / "metrics.json"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(diag, f, indent=2)
        os.replace(tmp, final)
        return

    t0 = time.perf_counter()
    per_seed = []
    for seed in SEEDS:
        r = run_one_seed(seed)
        per_seed.append(r)
        print(f"[progress] seed={seed} done ungated_unrel={r['ungated_unrel']:.3f} "
              f"hard_gate_unrel={r['hard_gate_unrel']:.3f} soft_multiplier_unrel={r['soft_multiplier_unrel']:.3f} "
              f"auc_unrel={r['auc_unrel']:.4f} auc_pooled={r['auc_pooled']:.4f}",
              flush=True)

    if len(per_seed) != EXPECTED_N_UNITS:
        raise RuntimeError(
            f"HARD_FAIL_CARDINALITY_BREACH_META_RULE_H: expected {EXPECTED_N_UNITS} units, got {len(per_seed)}"
        )

    for r in per_seed:
        pairs_ok = _arms_must_differ([r["_arm_digests"]])
        if not all(pairs_ok.values()):
            bad = {k: v for k, v in pairs_ok.items() if not v}
            raise RuntimeError(f"META_RULE_AF VIOLATION at seed={r['seed']}: bit-identical arm pairs: {bad}")

    result = aggregate_and_verdict(per_seed)
    elapsed = time.perf_counter() - t0
    result["elapsed_s"] = elapsed
    result["run_mode"] = RUN_MODE
    result["anchor_name"] = ANCHOR_NAME
    result["ts_iso"] = datetime.now(timezone.utc).isoformat()
    result["cardinality_ok"] = (len(per_seed) == EXPECTED_N_UNITS)
    result["expected_n_units"] = EXPECTED_N_UNITS
    result["config"] = {
        "V": V, "N": N, "N_RELIABLE": N_RELIABLE, "N_UNRELIABLE": N_UNRELIABLE,
        "R_RELIABLE": R_RELIABLE, "R_UNRELIABLE": R_UNRELIABLE,
        "N_OBS_MIN": N_OBS_MIN, "N_OBS_MAX": N_OBS_MAX, "TAU": TAU, "SEEDS": SEEDS,
        "signal": "leave_one_out_cross_observation_cosine_consistency_NO_INJECTION",
    }
    for r in result["per_seed"]:
        r["_arm_digests_short"] = {k: v[:16] for k, v in r.pop("_arm_digests").items()}

    tmp = out_dir / "metrics.json.tmp"
    final = out_dir / "metrics.json"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
    os.replace(tmp, final)
    print(f"[done] verdict={result['verdict']} elapsed_s={elapsed:.4f}", flush=True)
    print(f"[done] auc_unrel={result['auc_unrel_mean']:.4f} auc_pooled={result['auc_pooled_mean']:.4f}", flush=True)
    print(f"[done] {result['verdict_msg']}", flush=True)


if __name__ == "__main__":
    _out_dir_for_crash = REPO / "data" / (f"exp_{ANCHOR_NAME}_smoke" if SMOKE else f"exp_{ANCHOR_NAME}")
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # NOT BaseException; preserves SystemExit/KeyboardInterrupt
        _write_crash_metrics(_out_dir_for_crash, e)
        raise
