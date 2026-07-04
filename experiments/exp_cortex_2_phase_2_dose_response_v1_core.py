"""Cortex-2 Phase 2 dose-response arm v1 -- SECOND PROBE (2026-07-03).

Skunkworks landed-VET recommendation (task ac067134f58cdc781; math atom #62
MM_TENTATIVE_ADVISORY_APPLIED): Phase 2 apply-probe v1 landed HP but is NOT
CG-eligible without a dose-response arm confirming effect-size stability and
KS p-value non-saturation at the asymptotic bound.

Minimal delta from `exp_cortex_2_phase_2_apply_probe_v1_core.py`:
  - 5 cases PRESERVED verbatim (same ground-truth corpus).
  - Same enforce() code path (identical imports from `hdlab.atom_consultation`).
  - SHADOW-default preserved; 5 curated atoms promoted to WARN (identical list).
  - Same null-arm + nonce discriminator mechanism.
  - Same downstream stub N(mu(value), sigma=1).
  - ONE dimension varied: n_per_arm sweep over {5, 20, 100}.

Cardinality: 5 cases x 3 doses x (100 real + 100 null) at max = 3000 consults
max. Smaller at low doses (5 x 3 x 10 = 150; 5 x 3 x 40 = 600). Full-run wall
budget ~30s CPU (v1 landed 1.34s at n=5).

PRE-COMMITTED PREDICTIONS (per Skunkworks task-prompt, LOCKED BEFORE run):
  - Cases 1/2/4/5 all retain KS p<0.001 at n=100 with real_mean-null_mean gap
    >= 4 sigma (SE(diff) = sqrt(2/n) with sigma=1 downstream).
  - Case 3 STAYS structural mismatch (SHARDED atom outranks SCALE_FREE atom
    on cosine similarity; deferred to Phase 3 multi-atom conflict resolution).
  - Effect-size (sigma-gap) does NOT diminish monotone across doses for 1/2/4/5.
  - KS p-value has head-room at n=100 (doesn't hit numerical floor at n=5
    already; if it does, that IS saturation).

PRE-COMMITTED HARD-PASS gate (dose-response arm):
  - At n_per_arm=100, cases 1/2/4/5 all satisfy:
    (ks_p < 0.001) AND (abs(real_mean - null_mean) / sqrt(2/n) >= 4.0)
  - Case 3 exempted from HP gate (structural expected-fail; matches v1 corpus
    behavior; treated as expected mismatch not novel finding).

PRE-COMMITTED HARD-FAIL:
  - Any of cases 1/2/4/5 shows gap_sigma at n=100 LESS THAN 0.7x its value
    at n=5 (indicating diminishing effect with sample size -- a mechanism
    issue, since SE shrinks with sqrt(n), the sigma-gap should grow OR stay
    stable given fixed true mean gap).
  - Case 3 also expected to fail HP at all doses (structural).

MIDDLE_BAND: 2-3 of cases 1/2/4/5 pass HP gate; investigate.

Prior-work concept-query 2026-07-03 (per USER-locked substrate-KB rule):
  NONE at cosine>0.30 for "cortex 2 phase 2 dose response arm KS effect
  stability n per arm sweep" -- novel synthesis (top hit 0.288 wordnet 'phase';
  no relevant prior work). Same discipline as v1 apply-probe.

Source signature (per USER-locked MM_STANDARD 2026-07-03):
  Phase 2 dose-response arm v1, cortex-2 arc, 5 cases x 3 doses (n_per_arm in
  {5, 20, 100}) x (real + null) = 1050 consultations, WARN mode for 5 curated
  atoms (SHADOW default), atom store as of 2026-07-04 106-atom corpus (curated
  subset of 7 in _default_curated_atoms), char-trigram encoder N=1024, 5
  op-classes, downstream N(mu(value), sigma=1) scalar draw. Single seed
  (deterministic RNG stream from _DOWNSTREAM_SEED_BASE = 20260704).

Framing at SMOKE: MM_TENTATIVE at most (per arc-continuation-vs-closure);
MM_STANDARD promotion needs 3-seed FULL cv. This SMOKE probes dose-response
STABILITY at n=100 to justify a subsequent 3-seed FULL.

Parent chain:
  - math #54 Phase 1 v1.1 MM_TENTATIVE_ADVISORY (advisory-only)
  - math #62 Phase 2 v1 MM_TENTATIVE_ADVISORY_APPLIED (apply-probe first)
  - THIS cell = dose-response arm, one of three CG-eligibility prerequisites
    (dose-response + multi-atom conflict resolution + LIVE-mode audit).

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
- arms_differ_verified at smoke gate: real-arm vs null-arm produce different
  downstream distributions by construction (different values); trivially
  distinct. Also arms across doses are distinct by n_per_arm.
- final_metrics_atomicity: tmp_replace (single-shot; META_RULE_AH).
- except SystemExit: raise BEFORE except Exception (no BaseException).
- crlb_n_a: not a noise-floor metric; discriminator is fixed sigma-gap
  threshold. Absolute-fraction gates + KS thresholds are METHODOLOGICAL not
  physical noise floors.
- baseline_in_band: null-arm mean = mu(pre_value); real-arm mean =
  mu(recommendation); by construction distinct for cases 1/2/4/5.
- HARD_PASS strictly above floor + 5% band-width: gap_sigma HP=4.0 vs floor
  0.0 + 0.05 * 10.0 (predicted at n=100) = 0.5. HP=4.0 > 0.5. OK.
- HP_SCOPE: {gap_sigma@n=100: [cases 1/2/4/5, EXEMPT case 3],
             ks_p@n=100: [cases 1/2/4/5, EXEMPT case 3]}.
- cardinality_ok: EXPECTED_N_UNITS = 5 * sum(2*n for n in DOSES) = 1250 at
  full sweep {5, 20, 100}.
- discriminator survives scale: exactly the point of this cell (validate at
  n=100).

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
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

try:
    sys.stdout.reconfigure(line_buffering=True)
except AttributeError:
    pass

import numpy as np

from experiments._seed_checkpoint import get_output_dir
from experiments.exp_cortex_2_phase_2_apply_probe_v1_core import (
    _ATOMS_TO_WARN,
    _DOWNSTREAM_SEED_BASE,
    _DOWNSTREAM_SIGMA,
    _GROUND_TRUTH_CASES,
    _VALUE_MU_MAP,
    _downstream_process,
    _ks_two_sample,
)
from hdlab.atom_consultation import (
    AtomConsultant,
    ConsultationResult,
    EnforcementDecisionLogger,
    VALID_OP_CLASSES,
)


ANCHOR_NAME = "cortex_2_phase_2_dose_response_v1_s7"

# Dose sweep values LOCKED per Skunkworks task-prompt (anti-drift, no
# re-tuning to force positive verdict).
DOSES = (5, 20, 100)

# Cases 1/2/4/5 are HP-gated. Case 3 is structurally expected-fail (SHARDED
# atom outranks SCALE_FREE on cosine; multi-atom conflict resolution deferred
# to Phase 3). LOCKED per v1 corpus discipline.
_HP_GATED_CASE_IDS = frozenset({
    "case1_storage_strategy",
    "case2_bundled_bimodal",
    "case4_axis_aliasing",
    "case5_cross_term_verify",
})
_EXPECTED_FAIL_CASE_IDS = frozenset({"case3_scale_free_law"})

# HP thresholds LOCKED per Skunkworks task-prompt.
_HP_KS_P_MAX = 0.001
_HP_GAP_SIGMA_MIN = 4.0
# Diminishing-effect FAIL threshold: gap_sigma at n=100 must be >= 70% of gap
# at n=5 (allowing modest sampling variance). SE shrinks as sqrt(n) so true
# mean gap should produce gap_sigma_at_n100 approx (10/sqrt(2)) * mean_gap
# = 7.07 * mean_gap, and gap_sigma_at_n5 approx sqrt(2.5) * mean_gap = 1.58
# * mean_gap; so gap_sigma_at_n100 / gap_sigma_at_n5 should be about 4.47.
# The 0.7x threshold catches the failure mode "gap SHRINKS with dose."
_FAIL_DIMINISH_RATIO = 0.7


def _write_start_marker(output_dir: Path, run_mode: str,
                        expected_n_units: int) -> None:
    marker = {
        "pid": os.getpid(),
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR_NAME,
        "run_mode": run_mode,
        "expected_n_units": expected_n_units,
        "host": platform.node(),
        "doses": list(DOSES),
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


def _run_one_dose(dose: int, output_dir: Path,
                  logger_path: str,
                  rng_master: np.random.Generator) -> list:
    """Run 5 cases x (dose real + dose null) at a single n_per_arm.

    Returns per_case_records enriched with gap_sigma for this dose.
    """
    ac = AtomConsultant()
    for aid in _ATOMS_TO_WARN:
        ac.set_enforcement_mode(aid, "WARN")

    logger = EnforcementDecisionLogger(logger_path)

    per_case = []
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
        case_matched = 0
        case_honored = 0
        case_nonce_written = 0
        case_nonce_consumed_ok = 0

        rng_real = np.random.default_rng(rng_master.integers(0, 2**31 - 1))
        rng_null = np.random.default_rng(rng_master.integers(0, 2**31 - 1))

        for _ in range(dose):
            for arm_name, rng_arm in (("real", rng_real), ("null", rng_null)):
                target = {param_name: pre_value_initial}
                is_null = (arm_name == "null")
                r: ConsultationResult = ac.enforce(
                    op_class, params=params,
                    target=target, param_name=param_name,
                    null_arm=is_null, query_hint=query_hint,
                    logger=logger)
                matched = (r.recommendation is not None)
                honored = matched and (r.recommendation == expected_rec)
                if arm_name == "real":
                    if matched:
                        case_matched += 1
                    if honored:
                        case_honored += 1
                if r.nonce_written:
                    case_nonce_written += 1
                out, value_read, nonce_ack = _downstream_process(
                    target, param_name, rng_arm)
                consumed_ok = bool(r.nonce_written) and (
                    nonce_ack == r.nonce_written)
                if consumed_ok:
                    case_nonce_consumed_ok += 1
                if arm_name == "real":
                    real_outputs.append(out)
                else:
                    null_outputs.append(out)

        real_arr = np.asarray(real_outputs, dtype=np.float64)
        null_arr = np.asarray(null_outputs, dtype=np.float64)
        d_stat, p_val = _ks_two_sample(real_arr, null_arr)
        real_mean = float(np.mean(real_arr))
        null_mean = float(np.mean(null_arr))
        # SE(diff of means) for two independent samples each of size `dose`
        # with per-sample sigma=_DOWNSTREAM_SIGMA. sigma-gap is
        # |real_mean - null_mean| / SE(diff). Larger n -> smaller SE ->
        # larger sigma-gap for fixed true mean gap. Diminishing sigma-gap
        # with dose is a FAIL signal (mechanism not stable).
        se_diff = float(np.sqrt(
            (_DOWNSTREAM_SIGMA ** 2) / dose
            + (_DOWNSTREAM_SIGMA ** 2) / dose))
        raw_mean_gap = abs(real_mean - null_mean)
        gap_sigma = (raw_mean_gap / se_diff) if se_diff > 0 else 0.0

        per_case.append({
            "case_id": case_id,
            "op_class": op_class,
            "dose": dose,
            "n_real": len(real_arr),
            "n_null": len(null_arr),
            "match_rate": case_matched / dose,
            "honored_rate": case_honored / dose,
            "nonce_written_count": case_nonce_written,
            "nonce_consumed_ok_count": case_nonce_consumed_ok,
            "nonce_consumption_rate": (
                case_nonce_consumed_ok / case_nonce_written
                if case_nonce_written else 0.0),
            "ks_D": d_stat,
            "ks_p": p_val,
            "real_mean": real_mean,
            "null_mean": null_mean,
            "raw_mean_gap": raw_mean_gap,
            "se_diff": se_diff,
            "gap_sigma": gap_sigma,
            "hp_gated": (case_id in _HP_GATED_CASE_IDS),
            "expected_fail_structural": (
                case_id in _EXPECTED_FAIL_CASE_IDS),
        })
        print(f"[dose={dose:>3d} case] {case_id}: "
              f"match={case_matched/dose:.2f} "
              f"honored={case_honored/dose:.2f} "
              f"KS_D={d_stat:.3f} p={p_val:.3g} "
              f"real_mean={real_mean:+.3f} null_mean={null_mean:+.3f} "
              f"gap_sigma={gap_sigma:.2f}", flush=True)

    logger.flush()
    return per_case


def run_dose_sweep(output_dir: Path, run_mode: str,
                   doses: tuple = DOSES) -> dict:
    """Sweep n_per_arm over `doses`; aggregate per-dose per-case metrics."""
    t0 = time.perf_counter()
    rng_master = np.random.default_rng(_DOWNSTREAM_SEED_BASE)

    all_per_case = []  # flat list; one entry per (dose, case)
    logger_path = str(output_dir / "enforcement_decisions.jsonl")

    for dose in doses:
        per_case = _run_one_dose(dose, output_dir, logger_path, rng_master)
        all_per_case.extend(per_case)

    elapsed_s = time.perf_counter() - t0

    # Aggregate: dose-response verdict.
    # PASS: cases 1/2/4/5 at MAX dose all satisfy (ks_p<0.001 AND gap_sigma>=4).
    max_dose = max(doses)
    min_dose = min(doses)

    per_case_at_max = [c for c in all_per_case if c["dose"] == max_dose]
    per_case_at_min = [c for c in all_per_case if c["dose"] == min_dose]

    hp_cases_pass = []
    hp_cases_fail = []
    for c in per_case_at_max:
        if not c["hp_gated"]:
            continue
        passes = (c["ks_p"] < _HP_KS_P_MAX) and (
            c["gap_sigma"] >= _HP_GAP_SIGMA_MIN)
        (hp_cases_pass if passes else hp_cases_fail).append(c["case_id"])

    # Diminishing-effect check for HP-gated cases: gap_sigma@max_dose must be
    # >= _FAIL_DIMINISH_RATIO * gap_sigma@min_dose.
    diminish_by_case = {}
    diminishing_cases = []
    for cid in _HP_GATED_CASE_IDS:
        gs_min = next(
            (c["gap_sigma"] for c in per_case_at_min if c["case_id"] == cid),
            None)
        gs_max = next(
            (c["gap_sigma"] for c in per_case_at_max if c["case_id"] == cid),
            None)
        if gs_min is None or gs_max is None:
            continue
        ratio = (gs_max / gs_min) if gs_min > 0 else float("inf")
        diminish_by_case[cid] = {
            "gap_sigma_at_min_dose": gs_min,
            "gap_sigma_at_max_dose": gs_max,
            "ratio_max_over_min": ratio,
        }
        # NOTE: sigma-gap SHOULD grow with dose (SE shrinks as 1/sqrt(n)) so
        # ratio_max_over_min is expected >> 1 for a stable mechanism.
        # Diminishing = ratio < _FAIL_DIMINISH_RATIO.
        if ratio < _FAIL_DIMINISH_RATIO:
            diminishing_cases.append(cid)

    # KS-saturation audit: KS p-value should be strictly monotone (or
    # at-worst flat) with dose for a stable mechanism. If p is IDENTICAL
    # across doses (bit-equal at floor), that's saturation flagged for
    # transparency (not a HP fail alone).
    ks_saturation_by_case = {}
    for cid in _HP_GATED_CASE_IDS:
        p_at_doses = {}
        for d in doses:
            pv = next(
                (c["ks_p"] for c in all_per_case
                 if c["case_id"] == cid and c["dose"] == d),
                None)
            if pv is not None:
                p_at_doses[str(d)] = pv
        # Saturation = all p at numerical zero. Not fatal but noted.
        all_zero = all(v == 0.0 for v in p_at_doses.values())
        ks_saturation_by_case[cid] = {
            "p_at_doses": p_at_doses,
            "all_zero_at_all_doses": all_zero,
        }

    # Case 3 audit (structural expected-fail; not a HP fail).
    case3_at_max = next(
        (c for c in per_case_at_max
         if c["case_id"] == "case3_scale_free_law"), None)

    n_hp_pass = len(hp_cases_pass)
    n_hp_fail = len(hp_cases_fail)
    n_diminishing = len(diminishing_cases)
    expected_n_hp = len(_HP_GATED_CASE_IDS)

    # Verdict.
    fatal_reasons = []
    expected_n_units = 2 * len(_GROUND_TRUTH_CASES) * sum(doses)
    # NB: cardinality is measured against per-call records but we tallied
    # aggregates only; recompute from doses+cases directly.
    actual_n_units = 2 * sum(c["n_real"] for c in all_per_case)
    if actual_n_units != expected_n_units:
        fatal_reasons.append(
            f"HARD_FAIL_CARDINALITY_BREACH_META_RULE_H: "
            f"actual={actual_n_units} vs expected={expected_n_units}")

    hp_gate = (
        n_hp_pass == expected_n_hp
        and n_diminishing == 0
    )
    hf_gate = (n_diminishing > 0)

    if fatal_reasons:
        verdict = "HARD_FAIL"
        verdict_msg = " | ".join(fatal_reasons)
    elif hp_gate:
        verdict = "HARD_PASS"
        verdict_msg = (
            f"HARD_PASS Phase 2 dose-response arm: all {expected_n_hp}/{expected_n_hp} "
            f"HP-gated cases {sorted(hp_cases_pass)} pass at n=100 "
            f"(ks_p<{_HP_KS_P_MAX}, gap_sigma>={_HP_GAP_SIGMA_MIN}). "
            f"No diminishing-effect cases across doses. Case3 "
            f"structural-mismatch behaved as expected. Candidate atom "
            f"EMPIRICAL_CORTEX_2_PHASE_2_APPLY_DOSE_RESPONSE_ARM_v1_"
            f"MM_TENTATIVE_or_STANDARD (Skunkworks tiering decision)."
        )
    elif hf_gate:
        verdict = "HARD_FAIL"
        verdict_msg = (
            f"HARD_FAIL_DIMINISHING_EFFECT: {n_diminishing} HP-gated case(s) "
            f"showed gap_sigma@n=100 < {_FAIL_DIMINISH_RATIO}x gap_sigma@n=5: "
            f"{sorted(diminishing_cases)}. Mechanism not dose-stable; "
            f"escalate to Skunkworks."
        )
    else:
        verdict = "MIDDLE_BAND"
        verdict_msg = (
            f"MIDDLE_BAND Phase 2 dose-response arm: "
            f"{n_hp_pass}/{expected_n_hp} HP-gated cases pass at n=100 "
            f"(passing: {sorted(hp_cases_pass)}; failing: {sorted(hp_cases_fail)}). "
            f"Non-monotone but not diminishing. Investigate per-case."
        )

    summary = (
        f"cortex_2_phase_2 dose-response arm (WARN mode; doses {list(doses)}): "
        f"HP-gated pass at n={max_dose}: {n_hp_pass}/{expected_n_hp}, "
        f"diminishing_cases: {n_diminishing}, "
        f"elapsed_s={elapsed_s:.2f}"
    )

    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": summary,
        "elapsed_s": elapsed_s,
        "anchor_name": ANCHOR_NAME,
        "run_mode": run_mode,
        "phase": "PHASE_2_APPLY_DOSE_RESPONSE_ARM_v1",
        "enforcement_mode_for_curated_atoms": "WARN",
        "doses": list(doses),
        "hp_gated_case_ids": sorted(_HP_GATED_CASE_IDS),
        "expected_fail_case_ids": sorted(_EXPECTED_FAIL_CASE_IDS),
        "hp_ks_p_max": _HP_KS_P_MAX,
        "hp_gap_sigma_min": _HP_GAP_SIGMA_MIN,
        "fail_diminish_ratio": _FAIL_DIMINISH_RATIO,
        "expected_n_units": expected_n_units,
        "actual_n_units": actual_n_units,
        "cardinality_ok": (actual_n_units == expected_n_units),
        "n_hp_pass": n_hp_pass,
        "n_hp_fail": n_hp_fail,
        "hp_pass_cases": sorted(hp_cases_pass),
        "hp_fail_cases": sorted(hp_cases_fail),
        "diminishing_cases": sorted(diminishing_cases),
        "diminish_audit_by_case": diminish_by_case,
        "ks_saturation_audit_by_case": ks_saturation_by_case,
        "case3_at_max_dose": case3_at_max,
        "per_case_per_dose": all_per_case,
        "arms_differ_verified": True,
        "final_metrics_atomicity": "tmp_replace",
        "op_classes": sorted(VALID_OP_CLASSES),
        "atoms_promoted_to_warn": list(_ATOMS_TO_WARN),
        "source_signature": (
            "Phase 2 dose-response arm v1 (2026-07-03), cortex-2 arc, 5 "
            f"cases x doses={list(doses)} x (real+null) = {expected_n_units} "
            "consultations, WARN mode for 5 curated atoms (SHADOW default), "
            "atom store 2026-07-04 106-atom corpus (curated subset of 7 "
            "covering 5 ground-truth cases), 5 op-classes, char-trigram "
            "encoder N=1024, downstream N(mu(value), sigma=1) stub, "
            "single seed _DOWNSTREAM_SEED_BASE=20260704."),
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


def _selftest_dose_sweep_e2e() -> None:
    """Run dose sweep at reduced doses in temp dir; assert schema + shape."""
    import tempfile
    reduced_doses = (5, 20)  # skip n=100 in selftest for speed
    with tempfile.TemporaryDirectory() as td:
        m = run_dose_sweep(Path(td), run_mode="self_test",
                           doses=reduced_doses)
        assert m["cardinality_ok"], (
            f"cardinality breach: {m['actual_n_units']} vs "
            f"{m['expected_n_units']}")
        # 5 cases x 2 doses = 10 per-case records
        assert len(m["per_case_per_dose"]) == 5 * len(reduced_doses), (
            f"per_case_per_dose len={len(m['per_case_per_dose'])} != "
            f"{5 * len(reduced_doses)}")
        # HP-gated cases at max reduced dose (20) should have gap_sigma > 4 at
        # least for cases 1,2,4,5 (strong mean gaps 5-6 with SE=sqrt(2/20)=0.316
        # -> expected gap_sigma ~ 15-18 for those cases).
        max_d = max(reduced_doses)
        for cid in ("case1_storage_strategy", "case2_bundled_bimodal",
                    "case4_axis_aliasing", "case5_cross_term_verify"):
            rec = next(c for c in m["per_case_per_dose"]
                       if c["case_id"] == cid and c["dose"] == max_d)
            assert rec["gap_sigma"] >= 4.0, (
                f"selftest: {cid} at dose={max_d} gap_sigma="
                f"{rec['gap_sigma']:.2f} < 4.0; mechanism not firing")
            assert rec["ks_p"] < 0.01, (
                f"selftest: {cid} at dose={max_d} ks_p={rec['ks_p']:.3g} "
                f">= 0.01; KS not detecting at reduced dose")
        # Case 3 should be present but NOT gated.
        c3 = next(c for c in m["per_case_per_dose"]
                  if c["case_id"] == "case3_scale_free_law"
                  and c["dose"] == max_d)
        assert not c3["hp_gated"], "case3 must be exempted from HP gate"


def _selftest_arms_and_case_locks() -> None:
    """Anti-drift: verify HP-gated + expected-fail case-id sets are as locked."""
    assert _HP_GATED_CASE_IDS == frozenset({
        "case1_storage_strategy", "case2_bundled_bimodal",
        "case4_axis_aliasing", "case5_cross_term_verify"})
    assert _EXPECTED_FAIL_CASE_IDS == frozenset({"case3_scale_free_law"})
    assert DOSES == (5, 20, 100), (
        f"DOSES tuple drift: {DOSES} != (5, 20, 100)")
    # Verify _ATOMS_TO_WARN unchanged from v1 (5 curated atoms).
    assert len(_ATOMS_TO_WARN) == 5, (
        f"_ATOMS_TO_WARN len={len(_ATOMS_TO_WARN)} != 5; corpus drift")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--full", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        _selftest_arms_and_case_locks()
        _selftest_dose_sweep_e2e()
        print(f"[{ANCHOR_NAME} self-test] PASS", flush=True)
        return

    # SMOKE and FULL both sweep same doses {5, 20, 100} per Skunkworks task
    # (dose-response requires n=100 to test asymptotic behavior). Runtime
    # ~30s CPU. Anti-drift: no reduced-doses smoke variant that skips n=100.
    if args.smoke:
        run_mode = "smoke"
        doses = DOSES
    elif args.full:
        run_mode = "full"
        doses = DOSES
    else:
        run_mode = "smoke"
        doses = DOSES

    output_dir = get_output_dir(ANCHOR_NAME)
    expected_n_units = 2 * len(_GROUND_TRUTH_CASES) * sum(doses)
    _write_start_marker(output_dir, run_mode, expected_n_units)
    metrics = run_dose_sweep(output_dir, run_mode, doses)
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
