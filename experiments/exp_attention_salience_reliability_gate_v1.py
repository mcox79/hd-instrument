"""exp_attention_salience_reliability_gate_v1.py

ATTENTION / SALIENCE RELIABILITY-GATE -- base-loop-INDEPENDENT self-monitoring cell.

Per notes/SYNTHESIS_missing_elements_prior_art_adopt_adapt_buildfresh_2026-07-20.md (Attention/salience row):
credited prior art = precision-weighting/Kalman-gain (Feldman-Friston), divisive-normalization
(Reynolds-Heeger), sparsemax, IDF/Itti-Koch. Hypothesis: the substrate's existing surprise signal is
ALREADY IDF-family (CONFIRMED below -- see PRIOR-WORK section in the pre-reg: exp_surprise_gating_b3b's
`surprise = -log(p)` is the literal IDF formula). The missing DELTA this cell tests: a RELIABILITY
MULTIPLIER + HARD-GATE that down-weights/suppresses low-reliability INPUTS before they contaminate a
consolidated representation -- a different axis from novelty/surprise (should-we-care) and a different
downstream harm (consolidation contamination) than the prior surprise-gated-WRITE-eviction cell
(exp_surprise_gating_b3b_synthetic_pool_recapture_v1.py, landed HONEST_BOUNDED) or the residual-gated
predictive-coding write (hdlab/predictive_coding.py, novelty not reliability).

MECHANISM (see preregs/attention_salience_reliability_gate_v1_2026-07-19.md for full pre-reg):
  V items, half "reliable-source" (r=0.92) half "unreliable-source" (r=0.15) -- per-item fixed observation
  reliability (heterogeneous input sources, e.g. clean vs noisy extraction pipelines). Each item observed
  n_obs in [6,10] times: true bipolar code w.p. r_i, else an unrelated random "corruption" w.p. 1-r_i. Each
  observation ALSO carries an EXOGENOUS confidence score (Beta(8,2) if the draw happened to be true,
  Beta(2,8) if corrupted) -- informative but noisy (OCR-confidence / extraction-confidence analog); the gate
  NEVER sees the hidden correctness label directly.

  Consolidation = weighted bipolar sum -> sign cleanup: consolidated_i = sign(sum_j w_j * obs_j).
  ARMS (one variable = the weight function w_j; confidence-score computation shared across all arms):
    ungated            : w_j = 1                          (REAL BASELINE -- today's default, no reliability layer)
    hard_gate           : w_j = 1[conf_j >= TAU]            (MECHANISM -- hard suppression)
    soft_multiplier     : w_j = clip(conf_j, 0, 1)          (MECHANISM -- Kalman-gain-style continuous weight)
    shuffled_hard_gate  : hard_gate on conf PERMUTED within-item (MUST-FAIL CONTROL)
    shuffled_multiplier : soft_multiplier on conf PERMUTED within-item (MUST-FAIL CONTROL)
    oracle              : w_j = hidden true-correctness label (DIAGNOSTIC CEILING ONLY, not HARD_PASS-scoped)

  METRIC: nearest-neighbor cleanup accuracy of consolidated_i against the full V-item codebook, split by
  item-reliability tier (_unrel = PRIMARY/LOAD-BEARING low-reliability-item subset per the contract's "cuts
  harm from low-reliability inputs"; _rel = do-no-harm check; _all = overall).

PRE-REG BANDS (locked; see pre-reg doc for full HP_SCOPE):
  HARD_PASS: mean_5seed(delta_hard_unrel) >= 0.05 AND mean_5seed(delta_mult_unrel) >= 0.05
             AND >=4/5 seeds positive-direction on both AND shuffled controls <= 0.00 delta on ALL 5 seeds
             AND do-no-harm (delta_*_rel >= -0.03) AND baseline_in_band (0.05 < acc_ungated_unrel < 0.95).
  HARD_FAIL: mean_5seed(delta_hard_unrel) <= 0.02 AND mean_5seed(delta_mult_unrel) <= 0.02 (ties/loses;
             gate INERT) OR baseline_in_band violated (non-test).
  MIDDLE_BAND: anything else.

DEFLATE: self-contained numpy; ASCII-only; local-runnable foreground (<1s total, all 5 seeds); glass-box;
no external LLM; no queue dispatch (compute-proportionality -- a directional gate question, not a training fit).

# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (hash over per-arm consolidated-vector sets)
# - final_metrics_atomicity: tmp_replace (single-shot, <1s total, no iteration)
# - except SystemExit/KeyboardInterrupt: raise BEFORE except Exception (no BaseException)
# - crlb_n/a: not a JL/capacity cell; bottleneck is pre-cleanup contamination, not argmax noise (see pre-reg)
# - baseline_in_band at smoke (META_RULE_AG; 0.05 < acc_ungated_unrel < 0.95)
# - discriminator survives scale: Option A -- smoke IS full-N/full-V (1 seed), no separate scale-up regime
# - HARD_PASS strictly above floor (0.05 mean lift, not >=0); HARD_FAIL <=0.02 (ties/loses)
# - HP_SCOPE per-arm declaration: oracle + shuffled arms explicitly OUT of HARD_PASS/HARD_FAIL scope
# - cardinality_ok: EXPECTED_N_UNITS = len(SEEDS); verdict counts len(per_seed)
# - per-unit failure-class instrumentation (no bare except)
# - calibration_check: default_ok_for_this_regime (TAU=0.5 at the Beta(8,2)/Beta(2,8) crossover)
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

ANCHOR_NAME = "attention_salience_reliability_gate_v1"

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
N = 128                       # bipolar vector dimensionality
N_RELIABLE = V // 2
N_UNRELIABLE = V - N_RELIABLE
R_RELIABLE = 0.92             # CITED@this-doc: high-reliability source correctness prob
R_UNRELIABLE = 0.15           # MEASURED@dev-sim: tuned so baseline lands in-band (see pre-reg regime-search)
N_OBS_MIN, N_OBS_MAX = 6, 10  # observations per item
TAU = 0.5                     # hard-gate threshold; sits at the Beta(8,2)/Beta(2,8) crossover
CONF_HI = (8.0, 2.0)          # Beta params for confidence score | observation is TRUE
CONF_LO = (2.0, 8.0)          # Beta params for confidence score | observation is CORRUPTED
SEEDS = [7] if SMOKE else [7, 17, 23, 31, 41]
EXPECTED_N_UNITS = len(SEEDS)

# Pre-registered bands (envelope-fail-bands; LOCKED, see preregs/attention_salience_reliability_gate_v1_2026-07-19.md)
HP_MEAN_LIFT_FLOOR = 0.05     # mean_5seed(delta_{hard,mult}_unrel) must clear this for HARD_PASS
HP_MAJORITY_SEEDS = 4         # of 5, must show positive-direction delta
HP_CONTROL_CEIL = 0.00        # shuffled-control delta must be <= this on ALL seeds
HP_DO_NO_HARM_FLOOR = -0.03   # delta_*_rel must clear this (mean)
HF_MEAN_LIFT_CEIL = 0.02      # mean_5seed(delta_{hard,mult}_unrel) <= this -> HARD_FAIL (ties/loses)
BASELINE_BAND = (0.05, 0.95)  # META_RULE_AG: acc_ungated_unrel must be strictly inside this band


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


def run_one_seed(seed: int) -> Dict:
    """Run all 6 arms for one seed over V items; return per-arm accuracy (all/unrel/rel) + diagnostics."""
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

    for i in range(V):
        n_obs = int(n_obs_per_item[i])
        true_v = codebook[i]
        obs = np.empty((n_obs, N), dtype=np.float32)
        c_true = np.empty(n_obs, dtype=bool)
        conf = np.empty(n_obs, dtype=np.float64)
        for j in range(n_obs):
            is_correct = rng.random() < reliab[i]
            c_true[j] = is_correct
            if is_correct:
                obs[j] = true_v
                conf[j] = rng.beta(*CONF_HI)
            else:
                obs[j] = _bipolar(rng, (N,))
                conf[j] = rng.beta(*CONF_LO)

        cons: Dict[str, np.ndarray] = {}
        cons["ungated"] = _cons_from_weights(obs, np.ones(n_obs, dtype=np.float32))
        cons["hard_gate"] = _cons_from_weights(obs, (conf >= TAU).astype(np.float32))
        cons["soft_multiplier"] = _cons_from_weights(obs, np.clip(conf, 0.0, 1.0).astype(np.float32))
        conf_shuf = rng.permutation(conf)
        cons["shuffled_hard_gate"] = _cons_from_weights(obs, (conf_shuf >= TAU).astype(np.float32))
        cons["shuffled_multiplier"] = _cons_from_weights(obs, np.clip(conf_shuf, 0.0, 1.0).astype(np.float32))
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
    # arms-must-differ hash (META_RULE_AF): digest each arm's stacked consolidated-vector matrix
    digests = {}
    for a in arm_names:
        mat = np.stack(consolidated_digest_inputs[a]).astype(np.int8)
        digests[a] = hashlib.sha256(mat.tobytes()).hexdigest()
    out["_arm_digests"] = digests
    return out


def _arms_must_differ(digests_by_seed: List[Dict[str, str]]) -> Dict[str, bool]:
    """META_RULE_AF: verify arms produce distinct outputs (using seed=SEEDS[0] as the representative check).
    ungated vs hard_gate vs soft_multiplier vs shuffled_hard_gate vs shuffled_multiplier vs oracle must be
    pairwise distinct (each arm's weight-transform is genuinely different)."""
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
    baseline_in_band = all(BASELINE_BAND[0] < v < BASELINE_BAND[1] for v in baseline_unrel_vals)

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
    elif lift_ok and majority_ok and control_ok and do_no_harm_ok:
        verdict = "HARD_PASS"
        verdict_msg = (f"HARD_PASS: reliability-gate delta measurably improves consolidation on the "
                        f"low-reliability item subset. mean_delta_hard_unrel={mean_d_hard_unrel:.4f} "
                        f"mean_delta_mult_unrel={mean_d_mult_unrel:.4f} (both >= {HP_MEAN_LIFT_FLOOR}); "
                        f"positive-direction {n_pos_hard}/{len(seeds)} (hard) {n_pos_mult}/{len(seeds)} (mult) "
                        f">= {HP_MAJORITY_SEEDS}/5; shuffled controls all <= {HP_CONTROL_CEIL} "
                        f"(max_shuf_hard={max(d_shuf_hard_unrel):.4f} max_shuf_mult={max(d_shuf_mult_unrel):.4f}); "
                        f"do-no-harm mean_delta_hard_rel={mean_d_hard_rel:.4f} "
                        f"mean_delta_mult_rel={mean_d_mult_rel:.4f} (both >= {HP_DO_NO_HARM_FLOOR}); "
                        f"oracle ceiling mean_delta_unrel={float(np.mean(d_oracle_unrel)):.4f} (diagnostic only).")
    elif hard_fail_lift:
        verdict = "HARD_FAIL"
        verdict_msg = (f"HARD_FAIL: reliability-gate delta INERT (ties/loses ungated baseline). "
                        f"mean_delta_hard_unrel={mean_d_hard_unrel:.4f} mean_delta_mult_unrel={mean_d_mult_unrel:.4f} "
                        f"both <= {HF_MEAN_LIFT_CEIL}. The exogenous confidence signal does not carry enough "
                        f"information (or the gate/multiplier transform does not exploit it) at this regime.")
    else:
        verdict = "MIDDLE_BAND"
        verdict_msg = (f"MIDDLE_BAND: partial signal, gates not all cleared. "
                        f"mean_delta_hard_unrel={mean_d_hard_unrel:.4f} mean_delta_mult_unrel={mean_d_mult_unrel:.4f} "
                        f"lift_ok={lift_ok} majority_ok={majority_ok} control_ok={control_ok} "
                        f"do_no_harm_ok={do_no_harm_ok} (n_pos_hard={n_pos_hard} n_pos_mult={n_pos_mult}).")

    return {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": verdict_msg,
        "per_seed": per_seed,
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
        "baseline_in_band": baseline_in_band,
        "n_pos_hard": n_pos_hard,
        "n_pos_mult": n_pos_mult,
        "hp_scope_note": ("oracle + shuffled_hard_gate + shuffled_multiplier are diagnostic/control arms, "
                           "explicitly OUT of HARD_PASS/HARD_FAIL decision scope (HP_SCOPE per pre-reg)."),
    }


def _self_test() -> None:
    """Tiny, deterministic, real-code-path exercise (V=100,N=128,seed=7 -- same regime as smoke/full,
    just 1 seed) + arms-must-differ assertion + baseline-in-band assertion."""
    t0 = time.perf_counter()
    r = run_one_seed(7)
    assert 0.0 < r["ungated_unrel"] < 1.0, f"self-test: ungated_unrel degenerate ({r['ungated_unrel']})"
    assert 0.0 <= r["ungated_rel"] <= 1.0
    pairs_ok = _arms_must_differ([r["_arm_digests"]])
    n_diff = sum(1 for v in pairs_ok.values() if v)
    assert n_diff == len(pairs_ok), f"META_RULE_AF VIOLATION: some arm pairs bit-identical: {pairs_ok}"
    # sanity: hard/mult should beat ungated on the informative low-reliability subset for THIS mechanism
    # to be worth full dispatch (not asserted as a hard gate here -- that's the FULL verdict's job -- but
    # print for visibility so a self-test run surfaces the discriminator-fires check per Pattern 2).
    d_hard = r["hard_gate_unrel"] - r["ungated_unrel"]
    d_mult = r["soft_multiplier_unrel"] - r["ungated_unrel"]
    d_shuf_hard = r["shuffled_hard_gate_unrel"] - r["ungated_unrel"]
    d_shuf_mult = r["shuffled_multiplier_unrel"] - r["ungated_unrel"]
    print(f"[self-test] ungated_unrel={r['ungated_unrel']:.3f} hard_gate_unrel={r['hard_gate_unrel']:.3f} "
          f"(delta={d_hard:+.3f}) soft_multiplier_unrel={r['soft_multiplier_unrel']:.3f} (delta={d_mult:+.3f}) "
          f"shuffled_hard_delta={d_shuf_hard:+.3f} shuffled_mult_delta={d_shuf_mult:+.3f}", flush=True)
    assert n_diff == len(pairs_ok)
    elapsed = time.perf_counter() - t0
    print(f"[self-test] PASS in {elapsed:.3f}s (arms_differ={n_diff}/{len(pairs_ok)} pairs distinct)", flush=True)


def main() -> None:
    out_dir = REPO / "data" / f"exp_{ANCHOR_NAME}" if not SMOKE else REPO / "data" / f"exp_{ANCHOR_NAME}_smoke"
    _write_start_marker(out_dir, EXPECTED_N_UNITS)

    if SELF_TEST_MODE:
        _self_test()
        # self-test also writes a minimal metrics.json so runner/queue_add health checks see a valid file
        diag = {
            "verdict": "SELFTEST_OK", "verdict_msg": "SELFTEST_OK: real code path exercised, arms differ",
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
              f"hard_gate_unrel={r['hard_gate_unrel']:.3f} soft_multiplier_unrel={r['soft_multiplier_unrel']:.3f}",
              flush=True)

    # cardinality gate (META_RULE_H)
    if len(per_seed) != EXPECTED_N_UNITS:
        raise RuntimeError(
            f"HARD_FAIL_CARDINALITY_BREACH_META_RULE_H: expected {EXPECTED_N_UNITS} units, got {len(per_seed)}"
        )

    # arms-must-differ gate (META_RULE_AF) -- check every seed, not just the first
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
        "N_OBS_MIN": N_OBS_MIN, "N_OBS_MAX": N_OBS_MAX, "TAU": TAU,
        "CONF_HI": list(CONF_HI), "CONF_LO": list(CONF_LO), "SEEDS": SEEDS,
    }
    # strip non-JSON-friendly digest dicts from per_seed before final write (keep a compact hash summary only)
    for r in result["per_seed"]:
        r["_arm_digests_short"] = {k: v[:16] for k, v in r.pop("_arm_digests").items()}

    tmp = out_dir / "metrics.json.tmp"
    final = out_dir / "metrics.json"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
    os.replace(tmp, final)
    print(f"[done] verdict={result['verdict']} elapsed_s={elapsed:.4f}", flush=True)
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
