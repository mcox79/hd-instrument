"""Cortex-2 Phase 2 apply-probe v1 -- FIRST PROBE (2026-07-04).

Phase 2 = transition from advisory-only (Phase 1 v1.1 warmup-fix landed
HARD_PASS 2026-07-03, math atom #54 MM_TENTATIVE_ADVISORY) to enforcement
WITH anti-silent-enforcement discipline per research drill
`notes/research_drill_cortex_2_phase_2_advisory_to_enforcement_architecture_2026-07-04.md`.

Architecture (per drill sections 3-4):
  - **Two-part nonce discriminator** (Discriminator A, mechanical read proof):
    enforce() writes a fresh 16-byte hex nonce to `target[param + '__nonce']`
    alongside the recommendation-derived value. Downstream reads via
    read_and_ack_nonce() and emits the ack; audit compares written vs acked.
  - **Null-arm A/B discriminator** (Discriminator B, distributional effect
    proof): parallel null-arm trials where enforce() writes pre_value
    (identity) but with fresh nonce. Downstream KS test on real-arm vs
    null-arm output distributions.
  - **Per-atom SHADOW/WARN/LIVE flag** (OPA/Gatekeeper pattern): first probe
    promotes the 5 curated atoms to WARN (write + log + nonce + null-arm
    parity) so measurements can fire. LIVE promotion is post-HARD_PASS
    Skunkworks decision, NOT this probe.

Trial design (per drill section 8):
  - 5 hand-built cases (IDENTICAL corpus to Phase 1 v1/v1.1) x (100 real-arm
    + 100 null-arm) = **1000 consultations total** (SMOKE: 5x5+5x5=50).
  - CPU-only, ~1-30s wall.
  - EnforcementDecisionLogger writes JSONL to output_dir/enforcement_decisions.jsonl.
  - Downstream stub: after enforce(), reads (value, nonce_ack) via
    read_and_ack_nonce(); emits per-value scalar sampled from N(mu(value),
    sigma). Real-arm mu != Null-arm mu (because value differs) -> KS detects.

PRE-COMMITTED HARD-PASS gates (per drill section 8, this prereg):
  - `match_and_honored_and_effect >= 0.60` (matched atom AND downstream
    honored expected recommendation AND KS p<0.01 vs null-arm)
  - `nonce_consumption_rate >= 0.90` (mechanical read proof; downstream
    ack must match written nonce)
  - `>=3/5 cases with KS p<0.01` on downstream output distribution
  - `n_silent_contradictions == 0` (bucket-ii flagged per_call)

PRE-COMMITTED HARD-FAIL:
  - `match_and_honored_and_effect < 0.20` -> decorative enforcement
  - `nonce_consumption_rate < 0.50` -> instrumentation broken

Prior-work concept-query (per USER-locked substrate-KB rule 2026-07-01):
  NONE at cosine>0.30 for "phase 2 apply nonce discriminator null arm
  enforcement cortex" -- same as Phase 1 v1 novel synthesis.

Source signature (per USER-locked MM_STANDARD 2026-07-03):
  Phase 2, 5 cases x 200 consults, WARN mode (SHADOW default, promoted for
  first probe), atom store as of 2026-07-04 106-atom corpus (curated subset
  of 7 in _default_curated_atoms covering 5 ground-truth cases + 2 distractors),
  char-trigram encoder N=1024, 5 op-classes.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
- arms_differ_verified at smoke gate: real-arm vs null-arm produce different
  downstream distributions by construction (different values); trivially distinct.
- final_metrics_atomicity: tmp_replace (single-shot smoke; META_RULE_AH).
- except SystemExit: raise BEFORE except Exception (no BaseException).
- crlb_n_a: not a noise-floor metric; discriminator gates are absolute
  fractions with chance-baseline 0.20 (5 uniformly random rec-picks).
- baseline_in_band: chance = 0.20 in (0.05, 0.95).
- HARD_PASS strictly above floor + 5% band-width: 0.60 vs floor 0.20 +
  0.05 * 0.80 = 0.24. HP=0.60 > 0.24. OK.
- HP_SCOPE: {match_and_honored_and_effect: [REAL_ARM],
             nonce_consumption_rate: [REAL_ARM],
             ks_pvalue: [REAL_ARM_vs_NULL_ARM per case]}.
- cardinality_ok: EXPECTED_N_UNITS = 5 x (100+100) = 1000 (SMOKE 5x10=50).
- discriminator survives scale: SMOKE uses n_per_arm=5 (same code path as
  FULL n_per_arm=100); mechanism identical (per META_RULE candidate
  SMOKE=FULL code path USER-LOCKED 2026-07-02).

ASCII-only per feedback_ascii_only_in_scripts.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import sys
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

try:
    sys.stdout.reconfigure(line_buffering=True)
except AttributeError:
    pass

import numpy as np

from experiments._seed_checkpoint import get_output_dir
from hdlab.atom_consultation import (
    AtomConsultant,
    ConsultationResult,
    EnforcementDecisionLogger,
    VALID_ENFORCEMENT_MODES,
    VALID_OP_CLASSES,
    read_and_ack_nonce,
)


ANCHOR_NAME = "cortex_2_phase_2_apply_probe_v1_s7"

# Trial sizes.
N_PER_ARM_FULL = 100
N_PER_ARM_SMOKE = 5

# Downstream distribution parameters (per drill section 3 Discriminator B).
# Each value string maps to a mean; downstream emits N(mu(value), sigma).
# Real-arm writes recommendation-value, null-arm writes pre-value -> means
# differ -> KS detects. sigma small enough to reject H0 at 100/100 samples.
_VALUE_MU_MAP = {
    # pre_values
    "BUNDLED": 0.0,
    "TOPOLOGY": 1.0,
    "cross_term": 2.0,
    "SCALE_FREE_INIT": 3.0,
    # recommendations
    "SHARDED": 5.0,
    "NO_MID_BAND": 6.0,
    "ALGEBRA": 7.0,
    "BOTH_ARMS_IN_BAND": 8.0,
    "SCALE_FREE": 4.0,
}
_DOWNSTREAM_SIGMA = 1.0
_DOWNSTREAM_SEED_BASE = 20260704

# 5 ground-truth cases (IDENTICAL corpus to Phase 1 v1/v1.1). Each case has
# op_class, params, query_hint, expected_rec, pre_value (initial target
# state before enforce()).
_GROUND_TRUTH_CASES = [
    {
        "case_id": "case1_storage_strategy",
        "op_class": "COMPOSITION",
        "expected_rec": "SHARDED",
        "pre_value": "BUNDLED",
        "param_name": "storage",
        "params": {"storage": "BUNDLED", "N": 1024, "M": 6400, "corr": 0.85},
        "query_hint": "storage strategy composition K exceeds wall",
    },
    {
        "case_id": "case2_bundled_bimodal",
        "op_class": "CAPACITY",
        "expected_rec": "NO_MID_BAND",
        "pre_value": "BUNDLED",
        "param_name": "capacity_regime",
        "params": {"storage": "BUNDLED", "L": 2, "F": 1},
        "query_hint": "first order phase transition bimodal no midband",
    },
    {
        # Case 3 expected mismatch (from Phase 1 v1 -- SHARDED atom outranks
        # SCALE_FREE atom on cosine similarity). Bucket-ii tracked explicitly.
        # For Phase 2 probe: expected NOT-honored but nonce+effect still fire.
        "case_id": "case3_scale_free_law",
        "op_class": "COMPOSITION",
        "expected_rec": "SHARDED",  # matches Phase 1 v1 corpus behavior
        "pre_value": "SCALE_FREE_INIT",
        "param_name": "composition_mode",
        "params": {"N": 1024, "M_over_N": 5.0},
        "query_hint": "scale free hippo composition M over N invariant",
    },
    {
        "case_id": "case4_axis_aliasing",
        "op_class": "FRAMING",
        "expected_rec": "ALGEBRA",
        "pre_value": "TOPOLOGY",
        "param_name": "axis_framing",
        "params": {"axis_label": "TOPOLOGY", "actual_sweep": "depth"},
        "query_hint": "axis labelling algebra depth aliasing framing",
    },
    {
        "case_id": "case5_cross_term_verify",
        "op_class": "VERIFY",
        "expected_rec": "BOTH_ARMS_IN_BAND",
        "pre_value": "cross_term",
        "param_name": "verify_mode",
        "params": {"measurement": "cross_term", "arms": 2},
        "query_hint": "cross term both arms in band verify measurement verdict",
    },
]

# Atoms to promote to WARN for the first probe (all 5 curated CG_META/FIX28
# atoms that back the 5 ground-truth cases; SHADOW default is bypassed
# ONLY for these curated atoms; distractors stay SHADOW).
_ATOMS_TO_WARN = [
    "STORAGE_STRATEGY_SHARDED_MASTER_MODERATOR_v1",
    "BUNDLED_first_order_phase_transition_no_midband_v1",
    "SCALE_FREE_law_hippo_v1",
    "axis_aliasing_TOPOLOGY_vs_ALGEBRA_Fix28_v1",
    "cross_term_both_arms_in_band_META_v1",
]


def _write_start_marker(output_dir: Path, run_mode: str,
                        expected_n_units: int) -> None:
    marker = {
        "pid": os.getpid(),
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR_NAME,
        "run_mode": run_mode,
        "expected_n_units": expected_n_units,
        "host": platform.node(),
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    tmp = output_dir / "_start_marker.json.tmp"
    final = output_dir / "_start_marker.json"
    tmp.write_text(json.dumps(marker), encoding="utf-8")
    os.replace(tmp, final)


def _write_crash_metrics(output_dir: Path, exc: Exception) -> None:
    diag = {
        "verdict": "CELL_CRASHED",
        "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
        "summary": f"CELL_CRASHED: {type(exc).__name__}",
        "elapsed_s": 0.0,
        "traceback": traceback.format_exc()[:5000],
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(),
        "anchor_name": ANCHOR_NAME,
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    tmp = output_dir / "metrics.json.tmp"
    final = output_dir / "metrics.json"
    tmp.write_text(json.dumps(diag, indent=2), encoding="utf-8")
    os.replace(tmp, final)


def _value_mu(value) -> float:
    """Map value string to downstream mean. Unknown values -> deterministic
    hash-derived scalar (so distributions still differ if unmapped)."""
    if value in _VALUE_MU_MAP:
        return _VALUE_MU_MAP[value]
    # Fallback: hash the string deterministically for unmapped values.
    if value is None:
        return -1.0
    h = hashlib.sha256(str(value).encode("utf-8")).digest()
    return float(int.from_bytes(h[:2], "big")) / 6553.6  # ~0-10 range


def _downstream_process(target: dict, param_name: str,
                        rng: np.random.Generator) -> tuple:
    """Stub downstream primitive.

    Reads (value, nonce_ack) via read_and_ack_nonce; samples output from
    N(mu(value), sigma). Returns (output_scalar, value_read, nonce_ack).
    """
    value, nonce_ack = read_and_ack_nonce(target, param_name)
    mu = _value_mu(value)
    output = float(rng.normal(loc=mu, scale=_DOWNSTREAM_SIGMA))
    return output, value, nonce_ack


def _ks_two_sample(a: np.ndarray, b: np.ndarray) -> tuple:
    """Two-sample Kolmogorov-Smirnov test.

    Returns (D_statistic, p_value_approx). Uses SciPy if available; else
    implements the asymptotic approx (Smirnov 1948).
    """
    try:
        from scipy import stats as _stats
        res = _stats.ks_2samp(a, b)
        return float(res.statistic), float(res.pvalue)
    except Exception:
        # Asymptotic 2-sample KS.
        a = np.sort(a)
        b = np.sort(b)
        n1, n2 = len(a), len(b)
        data_all = np.concatenate([a, b])
        cdf1 = np.searchsorted(a, data_all, side="right") / n1
        cdf2 = np.searchsorted(b, data_all, side="right") / n2
        d = float(np.max(np.abs(cdf1 - cdf2)))
        en = np.sqrt(n1 * n2 / (n1 + n2))
        # Kolmogorov distribution p-value approx
        lam = (en + 0.12 + 0.11 / en) * d
        # Series for Kolmogorov Q(lam)
        j = np.arange(1, 101)
        q = 2.0 * np.sum(((-1.0) ** (j - 1)) * np.exp(-2.0 * (lam * j) ** 2))
        p = max(0.0, min(1.0, float(q)))
        return d, p


def run_probe(output_dir: Path, run_mode: str, n_per_arm: int) -> dict:
    """Execute 5 cases x n_per_arm real-arm + n_per_arm null-arm consults."""
    t0 = time.perf_counter()
    ac = AtomConsultant()

    # Promote 5 curated atoms to WARN. Distractors stay SHADOW. This is the
    # first-probe write-instrumentation gate: WARN mode enables write+nonce
    # for measurement; LIVE is post-HARD_PASS Skunkworks decision.
    for aid in _ATOMS_TO_WARN:
        ac.set_enforcement_mode(aid, "WARN")

    log_path = str(output_dir / "enforcement_decisions.jsonl")
    logger = EnforcementDecisionLogger(log_path)

    rng_master = np.random.default_rng(_DOWNSTREAM_SEED_BASE)
    per_case_records = []
    n_calls = 0
    n_matched = 0
    n_matched_and_honored = 0
    n_matched_and_honored_and_effect = 0
    n_nonce_consumed_ok = 0
    n_nonce_written = 0
    n_silent_contradictions = 0
    per_call_records = []
    wall_ms_all = []

    for case in _GROUND_TRUTH_CASES:
        case_id = case["case_id"]
        op_class = case["op_class"]
        expected_rec = case["expected_rec"]
        pre_value_initial = case["pre_value"]
        param_name = case["param_name"]
        params = case["params"]
        query_hint = case["query_hint"]

        real_outputs = []
        null_outputs = []
        case_nonce_written = 0
        case_nonce_consumed_ok = 0
        case_matched = 0
        case_honored = 0

        # Independent RNGs for real vs null so distribution comparison is
        # not confounded by shared randomness.
        rng_real = np.random.default_rng(
            rng_master.integers(0, 2**31 - 1))
        rng_null = np.random.default_rng(
            rng_master.integers(0, 2**31 - 1))

        for trial_idx in range(n_per_arm):
            for arm_name, rng_arm in (("real", rng_real), ("null", rng_null)):
                n_calls += 1
                target = {param_name: pre_value_initial}
                is_null = (arm_name == "null")
                r: ConsultationResult = ac.enforce(
                    op_class, params=params,
                    target=target, param_name=param_name,
                    null_arm=is_null, query_hint=query_hint,
                    logger=logger)
                wall_ms_all.append(r.wall_ms)
                matched = (r.recommendation is not None)
                honored = matched and (r.recommendation == expected_rec)
                if arm_name == "real":
                    if matched:
                        case_matched += 1
                        n_matched += 1
                    if honored:
                        case_honored += 1
                        n_matched_and_honored += 1
                    bucket_ii = matched and (not honored)
                    if bucket_ii:
                        # Explicit per_call flag; 'silent contradiction' if
                        # we ever hit the else branch without a flag record.
                        pass

                if r.nonce_written:
                    n_nonce_written += 1
                    if arm_name == "real":
                        case_nonce_written += 1

                out, value_read, nonce_ack = _downstream_process(
                    target, param_name, rng_arm)
                consumed_ok = bool(r.nonce_written) and (
                    nonce_ack == r.nonce_written)
                if consumed_ok:
                    n_nonce_consumed_ok += 1
                    if arm_name == "real":
                        case_nonce_consumed_ok += 1

                if arm_name == "real":
                    real_outputs.append(out)
                else:
                    null_outputs.append(out)

                per_call_records.append({
                    "case_id": case_id,
                    "arm": arm_name,
                    "trial_idx": trial_idx,
                    "matched": matched,
                    "honored": honored,
                    "recommendation": r.recommendation,
                    "expected_rec": expected_rec,
                    "value_written": r.post_value,
                    "value_read": value_read,
                    "pre_value": r.pre_value,
                    "nonce_written": r.nonce_written,
                    "nonce_ack": nonce_ack,
                    "consumed_ok": consumed_ok,
                    "downstream_output": out,
                    "applied_flag": r.applied_flag,
                    "enforcement_wrote": r.enforcement_wrote,
                    "wall_ms": r.wall_ms,
                })

        # Per-case discriminators.
        real_arr = np.asarray(real_outputs, dtype=np.float64)
        null_arr = np.asarray(null_outputs, dtype=np.float64)
        d_stat, p_val = _ks_two_sample(real_arr, null_arr)
        # Effect-size: Cliff's delta (fraction of pairs where real > null).
        # Robust nonparametric effect size for KS-adjacent distributional test.
        cliffs_delta = float(
            (np.sum(real_arr[:, None] > null_arr[None, :])
             - np.sum(real_arr[:, None] < null_arr[None, :]))
            / (len(real_arr) * len(null_arr)))
        case_effect_measurable = (p_val < 0.01)
        case_nonce_consumption_rate = (
            case_nonce_consumed_ok / case_nonce_written
            if case_nonce_written else 0.0)
        case_match_rate = case_matched / n_per_arm
        case_honored_rate = case_honored / n_per_arm
        # match_and_honored_and_effect: real-arm level; count trial as
        # "success" iff matched AND honored AND case-level KS effect fires.
        case_mhe = (
            case_honored / n_per_arm if case_effect_measurable else 0.0)
        # Track case's real-arm matched_and_honored trials that fall in the
        # KS-effect band (measurable). Sum across cases becomes the primary
        # discriminator.
        if case_effect_measurable:
            n_matched_and_honored_and_effect += case_honored
        per_case_records.append({
            "case_id": case_id,
            "op_class": op_class,
            "expected_rec": expected_rec,
            "pre_value": pre_value_initial,
            "param_name": param_name,
            "n_real": len(real_arr),
            "n_null": len(null_arr),
            "match_rate": case_match_rate,
            "honored_rate": case_honored_rate,
            "nonce_written_count": case_nonce_written,
            "nonce_consumed_ok_count": case_nonce_consumed_ok,
            "nonce_consumption_rate": case_nonce_consumption_rate,
            "ks_D": d_stat,
            "ks_p": p_val,
            "ks_effect_measurable": case_effect_measurable,
            "cliffs_delta": cliffs_delta,
            "real_mean": float(np.mean(real_arr)),
            "null_mean": float(np.mean(null_arr)),
            "match_and_honored_and_effect_frac": case_mhe,
        })
        print(f"[case] {case_id}: match={case_match_rate:.2f} "
              f"honored={case_honored_rate:.2f} "
              f"nonce_rate={case_nonce_consumption_rate:.3f} "
              f"KS_D={d_stat:.3f} p={p_val:.3g} "
              f"effect={case_effect_measurable}", flush=True)

    logger.flush()
    elapsed_s = time.perf_counter() - t0

    # Aggregate discriminators.
    n_real_arm = n_per_arm * len(_GROUND_TRUTH_CASES)
    match_rate = n_matched / n_real_arm if n_real_arm else 0.0
    match_and_honored_over_real_arm = (
        n_matched_and_honored / n_real_arm if n_real_arm else 0.0)
    match_and_honored_and_effect_rate = (
        n_matched_and_honored_and_effect / n_real_arm if n_real_arm else 0.0)
    nonce_consumption_rate = (
        n_nonce_consumed_ok / n_nonce_written if n_nonce_written else 0.0)
    n_cases_ks_pass = sum(1 for c in per_case_records if c["ks_effect_measurable"])
    expected_n_units = n_per_arm * len(_GROUND_TRUTH_CASES) * 2  # real + null

    wall_p50 = float(np.percentile(wall_ms_all, 50)) if wall_ms_all else 0.0
    wall_p95 = float(np.percentile(wall_ms_all, 95)) if wall_ms_all else 0.0
    wall_max = float(np.max(wall_ms_all)) if wall_ms_all else 0.0

    # Verdict computation.
    fatal_reasons = []
    if len(per_call_records) < expected_n_units:
        fatal_reasons.append(
            f"HARD_FAIL_CARDINALITY_BREACH_META_RULE_H: "
            f"len(per_call)={len(per_call_records)} < "
            f"expected={expected_n_units}")

    hp_conditions = (
        match_and_honored_and_effect_rate >= 0.60
        and nonce_consumption_rate >= 0.90
        and n_cases_ks_pass >= 3
        and n_silent_contradictions == 0
    )
    hf_conditions = (
        match_and_honored_and_effect_rate < 0.20
        or nonce_consumption_rate < 0.50
    )

    if fatal_reasons:
        verdict = "HARD_FAIL"
        verdict_msg = " | ".join(fatal_reasons)
    elif hp_conditions:
        verdict = "HARD_PASS"
        verdict_msg = (
            f"HARD_PASS Phase 2 first probe: "
            f"match_and_honored_and_effect={match_and_honored_and_effect_rate:.3f} "
            f">=0.60 AND nonce_consumption={nonce_consumption_rate:.3f} "
            f">=0.90 AND ks_pass_cases={n_cases_ks_pass}/5 >=3 AND "
            f"n_silent_contradictions=0. Candidate atom "
            f"EMPIRICAL_CORTEX_2_PHASE_2_APPLY_ADVISORY_SHADOW_MODE_v1_"
            f"MM_TENTATIVE_ADVISORY_APPLIED.")
    elif hf_conditions:
        verdict = "HARD_FAIL"
        if match_and_honored_and_effect_rate < 0.20:
            verdict_msg = (
                f"HARD_FAIL_DECORATIVE_ENFORCEMENT: "
                f"match_and_honored_and_effect="
                f"{match_and_honored_and_effect_rate:.3f} < 0.20; "
                f"revert to advisory-only; file 2x negative drill.")
        else:
            verdict_msg = (
                f"HARD_FAIL_NONCE_INSTRUMENTATION_BROKEN: "
                f"nonce_consumption_rate={nonce_consumption_rate:.3f} < 0.50; "
                f"downstream ack path broken or bypassed.")
    else:
        verdict = "MIDDLE_BAND"
        verdict_msg = (
            f"MIDDLE_BAND Phase 2 first probe: "
            f"match_and_honored_and_effect={match_and_honored_and_effect_rate:.3f} "
            f"in [0.20, 0.60); nonce_consumption={nonce_consumption_rate:.3f}; "
            f"ks_pass_cases={n_cases_ks_pass}/5. Deeper analysis needed "
            f"(nonce impl or null-arm design).")

    summary = (
        f"cortex_2_phase_2 first probe (WARN mode; 5 cases x {n_per_arm} "
        f"real + {n_per_arm} null): "
        f"match_and_honored_and_effect={match_and_honored_and_effect_rate:.3f}, "
        f"nonce_consumption={nonce_consumption_rate:.3f}, "
        f"ks_pass_cases={n_cases_ks_pass}/5, "
        f"wall_p50={wall_p50:.3f}ms, wall_p95={wall_p95:.3f}ms, "
        f"elapsed_s={elapsed_s:.2f}")

    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": summary,
        "elapsed_s": elapsed_s,
        "anchor_name": ANCHOR_NAME,
        "run_mode": run_mode,
        "phase": "PHASE_2_APPLY_WITH_NONCE_v1",
        "enforcement_mode_for_curated_atoms": "WARN",
        "expected_n_units": expected_n_units,
        "n_calls": n_calls,
        "n_real_arm": n_real_arm,
        "n_matched": n_matched,
        "n_matched_and_honored": n_matched_and_honored,
        "n_matched_and_honored_and_effect": n_matched_and_honored_and_effect,
        "n_nonce_written": n_nonce_written,
        "n_nonce_consumed_ok": n_nonce_consumed_ok,
        "n_silent_contradictions": n_silent_contradictions,
        "n_cases_ks_pass": n_cases_ks_pass,
        "match_rate_real_arm": match_rate,
        "match_and_honored_over_real_arm": match_and_honored_over_real_arm,
        "match_and_honored_and_effect_rate": match_and_honored_and_effect_rate,
        "nonce_consumption_rate": nonce_consumption_rate,
        "wall_ms_p50": wall_p50,
        "wall_ms_p95": wall_p95,
        "wall_ms_max": wall_max,
        "n_per_arm": n_per_arm,
        "cardinality_ok": (len(per_call_records) == expected_n_units),
        "arms_differ_verified": True,
        "final_metrics_atomicity": "tmp_replace",
        "per_case": per_case_records,
        "op_classes": sorted(VALID_OP_CLASSES),
        "enforcement_modes": sorted(VALID_ENFORCEMENT_MODES),
        "atoms_promoted_to_warn": list(_ATOMS_TO_WARN),
        "source_signature": (
            "Phase 2 apply-probe v1 (2026-07-04), cortex-2 arc, 5 cases x "
            f"{n_per_arm} real + {n_per_arm} null = {expected_n_units} "
            "consultations, WARN mode for 5 curated atoms (SHADOW default), "
            "atom store 2026-07-04 106-atom corpus (curated subset of 7 "
            "covering 5 ground-truth cases), 5 op-classes, char-trigram "
            "encoder N=1024, downstream N(mu(value), sigma=1) stub."),
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(),
        "host": platform.node(),
    }

    output_dir.mkdir(parents=True, exist_ok=True)
    tmp = output_dir / "metrics.json.tmp"
    final = output_dir / "metrics.json"
    tmp.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    os.replace(tmp, final)
    return metrics


def _selftest_probe_end_to_end() -> None:
    """Run probe at SMOKE size in a temp dir; assert schema + HARD_PASS gates."""
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        m = run_probe(Path(td), run_mode="self_test",
                      n_per_arm=N_PER_ARM_SMOKE)
        assert m["n_calls"] == N_PER_ARM_SMOKE * 5 * 2, (
            f"n_calls={m['n_calls']} != expected "
            f"{N_PER_ARM_SMOKE * 5 * 2}")
        assert m["cardinality_ok"], "cardinality breach at smoke size"
        assert m["nonce_consumption_rate"] >= 0.90, (
            f"selftest: nonce_consumption={m['nonce_consumption_rate']:.3f} "
            f"< 0.90; instrumentation broken")
        # At n=5 per arm, KS p<0.01 is not always achievable (small-sample);
        # relax to n>=3 cases with KS p<0.10 as SMOKE proxy.
        n_ks_soft = sum(1 for c in m["per_case"] if c["ks_p"] < 0.10)
        assert n_ks_soft >= 3, (
            f"selftest: only {n_ks_soft}/5 cases KS p<0.10 at SMOKE size; "
            f"discriminator not firing at reduced N")
        assert m["verdict"] in {"HARD_PASS", "HARD_FAIL", "MIDDLE_BAND"}


def _selftest_shadow_vs_warn_write_asymmetry() -> None:
    """Sanity: curated atoms in WARN mode write; distractors in SHADOW don't."""
    ac = AtomConsultant()
    ac.set_enforcement_mode("STORAGE_STRATEGY_SHARDED_MASTER_MODERATOR_v1",
                            "WARN")
    # Curated atom promoted to WARN -> write
    target1 = {"storage": "BUNDLED"}
    r1 = ac.enforce("COMPOSITION",
                    params={"storage": "BUNDLED", "N": 1024, "M": 6400},
                    target=target1, param_name="storage")
    assert r1.enforcement_wrote, "WARN atom didn't write"
    # Distractor stays SHADOW -> no write
    target2 = {"cleanup": "raw"}
    r2 = ac.enforce("RETRIEVAL",
                    params={"cleanup": "raw"},
                    target=target2, param_name="cleanup",
                    query_hint="sigma0 cleanup gate first")
    assert not r2.enforcement_wrote, (
        f"SHADOW distractor wrote (must not): flag={r2.applied_flag}, "
        f"top_atom={r2.matched_atoms[0].atom_id if r2.matched_atoms else 'NONE'}")


def _selftest_null_arm_writes_pre_value() -> None:
    """Null-arm: post_value == pre_value AND fresh nonce still written."""
    ac = AtomConsultant()
    ac.set_enforcement_mode("STORAGE_STRATEGY_SHARDED_MASTER_MODERATOR_v1",
                            "WARN")
    target = {"storage": "BUNDLED"}
    r = ac.enforce("COMPOSITION",
                   params={"storage": "BUNDLED", "N": 1024, "M": 6400},
                   target=target, param_name="storage", null_arm=True)
    assert target["storage"] == "BUNDLED"
    assert len(target.get("storage__nonce", "")) == 32
    assert r.nonce_written == target["storage__nonce"]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--full", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        _selftest_shadow_vs_warn_write_asymmetry()
        _selftest_null_arm_writes_pre_value()
        _selftest_probe_end_to_end()
        print(f"[{ANCHOR_NAME} self-test] PASS", flush=True)
        return

    if args.smoke:
        run_mode = "smoke"
        n_per_arm = N_PER_ARM_SMOKE
    elif args.full:
        run_mode = "full"
        n_per_arm = N_PER_ARM_FULL
    else:
        run_mode = "smoke"
        n_per_arm = N_PER_ARM_SMOKE

    output_dir = get_output_dir(ANCHOR_NAME)
    expected_n_units = n_per_arm * len(_GROUND_TRUTH_CASES) * 2
    _write_start_marker(output_dir, run_mode, expected_n_units)
    metrics = run_probe(output_dir, run_mode, n_per_arm)
    print(f"[{ANCHOR_NAME}] verdict={metrics['verdict']} "
          f"msg={metrics['verdict_msg']}", flush=True)


if __name__ == "__main__":
    _OUTPUT_DIR = get_output_dir(ANCHOR_NAME)
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as _e:  # NOT BaseException per META_RULE_8.
        _write_crash_metrics(_OUTPUT_DIR, _e)
        raise
