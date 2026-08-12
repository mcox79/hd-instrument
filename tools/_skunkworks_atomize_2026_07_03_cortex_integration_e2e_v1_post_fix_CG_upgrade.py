"""
A5-gated atomize: Post-fix FULL VET of exp_cortex_integration_end_to_end_v1 at commit c16c72ca5.
  CG UPGRADE per revival criterion of prior amendment atom (2026-07-03T23:20:00Z MM_STANDARD).

CELL: experiments/exp_cortex_integration_end_to_end_v1.py
ANCHOR: exp_cortex_integration_end_to_end_v1
METRICS: data/exp_cortex_integration_end_to_end_v1/metrics.json (ts 2026-07-03T23:10:36Z, elapsed 9.24s, seeds [7,13,19])
COMMIT: c16c72ca5

OFF-DISK INDEPENDENT RECOMPUTE (verified this session):
  verdict = HARD_PASS
  verdict_msg contains "across 3 seeds" (parametrized as expected post-fix)
  cardinality = 36/36 (3 seeds x 4 primitives x 3 arms)
  elapsed_s = 9.241
  seeds = [7, 13, 19]
  arms_differ_discriminator = "runtime_call_trace_meta_rule_AF_v2" (post-fix meta-rule active)
  arm_runtime_call_trace field PRESENT with per-arm forward_call_delta + expected_pattern +
  trace_ok. ALL 12 arms trace_ok=True. Pattern classification:
    m14_composed: delta=50 pattern="forward_ge_1" trace_ok
    m14_individual: delta=0 pattern="forward_eq_0" trace_ok
    m14_ablated: delta=50 pattern="forward_ge_1" trace_ok (facade config ablation via refuse_tau=-1)
    m15_composed: delta=10 pattern="forward_ge_1" trace_ok (write + write-through reads)
    m15_individual: delta=0 pattern="forward_eq_0" trace_ok
    m15_ablated: delta=0 pattern="forward_eq_0" trace_ok (bypasses facade for ablation by design; declared)
    m17_composed: delta=1 pattern="forward_ge_1" trace_ok
    m17_individual: delta=0 pattern="forward_eq_0" trace_ok
    m17_ablated: delta=1 pattern="forward_ge_1" trace_ok
    m18_composed: delta=0 pattern="forward_eq_0" trace_ok (m18 bypasses cx.forward BY DESIGN; declared)
    m18_individual: delta=0 pattern="forward_eq_0" trace_ok
    m18_ablated: delta=0 pattern="forward_eq_0" trace_ok
  per-primitive metrics: m14=m15=m17 composed=individual=1.0 exact all seeds, ablated=0 exact.
    m18 composed=individual={0.68, 0.65, 0.65} matched exact, ablated=0 exact.
  cv independent recompute: m18 cv=0.021427 matches to 1e-6. m14/m15/m17 cv=0.

REVIVAL CRITERION AUDIT (prior amendment atom 2026-07-03T23:20:00Z):
  (1) Post-fix commit c16c72ca5: YES (current HEAD, cell fingerprint matches)
  (2) FULL landing (not SMOKE): YES (run_mode=full, seeds=[7,13,19], n_units=36)
  (3) Per-arm forward-call-delta MATCHES _ARM_TRACE_EXPECTED pattern: YES (all 12 arms trace_ok=True;
      discriminator is PATTERN-BASED "forward_ge_1"/"forward_eq_0", not fixed count)
  (4) m18 declared explicitly-tautological in cell: YES (all 3 m18 arms expected_pattern="forward_eq_0",
      cell explicitly declares m18 bypasses cx.forward by design)
  --> ALL 4 revival gate criteria met.

CG UPGRADE (per revival criterion "MM_STANDARD -> CG upgrade permitted"):
  Promoted primitives (runtime-trace discriminator active): m14, m15, m17.
    For these three, arms_differ is now RUNTIME-TRACE VERIFIED (not source-fingerprint decorative):
    - composed arm actually calls cx.forward at runtime (delta ge 1)
    - individual arm actually does NOT call cx.forward (delta = 0)
    - This is BEHAVIOR-delta verification of composition, not source-code fingerprint.
  m18 stays MM (declared tautological, per amendment): m18 does not exercise cx.forward at all so
    runtime-trace discriminator does not upgrade its evidence. m18 remains config-check equivalence.

FRAMING CATCHES vs Director spawn prompt (Fix#28 symmetric):
  (A) Prompt lists "expected" per-arm forward-call-deltas: m14_composed=20, m14_ablated=20, m15=6,
      m17=1, m18=0. Off-disk FULL actually shows m14=50, m14_ablated=50, m15=10, m17=1, m18=0.
      NOT A FAILURE: discriminator is CATEGORICAL (forward_ge_1 vs forward_eq_0), all trace_ok=True.
      Prompt's numeric expectations reflect SMOKE-scale n_queries=20; FULL scales to n_queries=50
      for m14, k_writes=5 doubled to 10 forward calls for m15 (write + write-through). The
      pattern-based meta-rule discriminator works at both scales. Director prompt cited SMOKE
      numerics as if they should reproduce at FULL. Not a blocker, small Fix#28-adjacent
      inherit-from-SMOKE catch.
  (B) Prompt says "landed 00:20Z UTC 2026-07-04". metrics.json ts_iso = "2026-07-03T23:10:36Z".
      About 70 min discrepancy. Actual landing is 07-03 late, not 07-04. Minor timestamp
      framing catch; does not affect substance.

CROSS-ARC OVERLAP CHECK:
  Direct match to prior amendment atom 2026-07-03T23:20:00Z on same anchor (self-supersede).
  Prior 2026-07-02 CG atom already SUPERSEDED by the amendment; this CG atom now SUPERSEDES
  the amendment with strengthened runtime-trace discriminator evidence.

RESIDUAL CAVEATS (still stand):
  - M1.3 (noise) and M1.6 (attention router) NOT covered in this cell (m14/m15/m17/m18 only).
    Cortex integration full-stack claim is 4-of-6 primitives; M1.3 and M1.6 covered by SEPARATE
    CG atoms (Phase 3b noise-channel CG 2026-07-02, Phase 3c M1.6 attention router CG 2026-07-02).
  - m14/m15/m17 COMPOSED metric hits 1.0 ceiling at small test scale (K=5/16/32). Runtime-trace
    discriminator upgrades arms_differ from source-fingerprint to behavior-delta; it does NOT
    resolve the ceiling-saturation of the metric itself. Bit-identity at 1.0 ceiling for these
    three is still non-informative on stress-scale composition equivalence. What IS proven:
    facade genuinely invokes cx.forward for composed (proven by runtime trace) and primitives
    are load-bearing (proven by ablation-at-zero-by-design). Scale-stress equivalence remains
    beyond scope.
  - m18 metric is non-ceiling (0.68/0.65/0.65) but m18 bypasses cx.forward by design, so runtime
    trace can only DECLARE the tautology; it cannot upgrade the substantive-composition claim
    for m18 above the amendment tier.
  - Ablation-at-zero-by-design remains a floor-anchored-by-design semantic (declared, not
    behavior-delta). This is Skunkworks-authoritative from prior VET; carries forward.

TIER RULING:
  math atom (CG UPGRADE for m14/m15/m17): T3 CHAIN_GRADE.
    Discriminator upgrade: source-fingerprint DECORATIVE -> runtime-trace BEHAVIOR-DELTA verified.
    m14/m15/m17 composition genuinely invokes cx.forward (delta ge 1); individual does not
    (delta = 0). Cortex facade composition integrity verified at runtime for 3 of 4 primitives.
  m18 subsidiary note (stays MM_STANDARD): declared tautology remains MM tier per amendment;
    runtime trace confirms declaration but does not upgrade the substantive-composition claim.

POSITIVE CONTROL CHECK (Auditor-2026-07-01 rule):
  Ablation arms fire below floor 0.1 all seeds all primitives (ablated=0.0 exact). Per-primitive
  reproduces=True for all 4. HARD_PASS verdict off substantive equivalence not test-design PC.

RECOMMENDED NEXT STEP (audit-only observation):
  Stress-scale variant (K=100+, contested match sets) to test composition equivalence off the
  ceiling for m14/m15/m17 would strengthen the mechanism-composition claim beyond
  facade-forwards-args-and-primitives-load-bearing. Not required for CG at this discriminator
  strength; noted for future arc-extension.
"""
from __future__ import annotations
import json, os, time
from pathlib import Path

ROOT = Path("d:/AI/hd-instrument")
MATH_ATOMS = ROOT / "data/substrate_index/math/atoms.jsonl"
META_ATOMS = ROOT / "data/substrate_index/meta/atoms.jsonl"
CERT_LEDGER = ROOT / "data/substrate_index/meta/cert_ledger.jsonl"

ATOMIZED_BY = "skunkworks_atomize_2026_07_03_cortex_integration_e2e_v1_post_fix_CG_upgrade"
CELL_COMMIT = "c16c72ca5"
TS_ISO = "2026-07-03T23:35:00Z"

PRIOR_AMENDMENT_ID = (
    "math::T3/AMEND_cortex_integration_end_to_end_v1_3seed_FULL_22p55Z_MM_STANDARD_DEMOTE_"
    "prior_CG_2026-07-02_via_SMOKE_VET_framing_corrections_m18_tautological_m14_m15_m17_"
    "ceiling_vacuous_arm_code_path_fingerprints_decorative_not_runtime_trace_diagnostic_"
    "reproducibility_confirmed_across_24h_deterministic_same_numbers_delta_max_0p0_all_"
    "primitives_cv_m18_0p0214_ablated_at_zero_by_design_legitimate_but_not_behavior_delta_"
    "revival_gate_post_fix_c16c72ca5_FULL_runtime_trace_matches_ARM_TRACE_EXPECTED_2026-07-03"
)

atom_math_CG_UPGRADE = {
    "id": (
        "math::T3/EXP_cortex_integration_end_to_end_v1_POST_FIX_c16c72ca5_3seed_FULL_CG_UPGRADE_"
        "runtime_trace_discriminator_meta_rule_AF_v2_verified_m14_m15_m17_composed_forward_call_delta_"
        "50_10_1_ge_1_pattern_individual_delta_0_eq_0_pattern_all_12_arms_trace_ok_true_"
        "m18_stays_MM_declared_tautological_bypasses_cx_forward_by_design_expected_pattern_eq_0_all_arms_"
        "facade_composition_integrity_BEHAVIOR_delta_verified_not_source_fingerprint_"
        "per_primitive_composed_1p0_1p0_1p0_0p66_individual_1p0_1p0_1p0_0p66_ablated_0p0_all_"
        "m18_per_seed_0p68_0p65_0p65_cv_0p021427_matches_prior_amendment_"
        "cardinality_36of36_verdict_HARD_PASS_verdict_msg_across_3_seeds_parametrized_"
        "elapsed_9p24s_seeds_7_13_19_ts_iso_2026-07-03T23_10_36Z_"
        "revival_criterion_from_prior_amendment_MET_all_4_gates_"
        "supersedes_prior_amendment_MM_STANDARD_2026-07-03T23_20_00Z_"
        "M1p3_noise_M1p6_attention_router_NOT_covered_this_cell_covered_by_separate_CG_atoms_"
        "m14_m15_m17_composed_arm_metric_at_1p0_ceiling_runtime_trace_upgrades_arms_differ_not_stress_scale_"
        "m18_stays_MM_config_check_equivalence_not_upgraded_"
        "ablation_at_zero_by_design_floor_anchored_by_design_semantic_carries_forward_"
        "2026-07-03"
    ),
    "name": (
        "Cortex integration end-to-end v1 POST-FIX c16c72ca5 3-seed FULL CG UPGRADE: "
        "runtime-trace discriminator verifies m14/m15/m17 facade composition integrity"
    ),
    "corpus": "math",
    "tier": "T3",
    "kind": "experiment_cert",
    "cert_status": "chain_grade",
    "cert_class": "cortex_integration_composition_runtime_trace_verified",
    "description": (
        "Post-fix (commit c16c72ca5) 3-seed FULL landing verifies cortex facade composition "
        "integrity via runtime-trace discriminator (arms_differ_discriminator = "
        "'runtime_call_trace_meta_rule_AF_v2'). Off-disk verification (metrics.json ts_iso "
        "2026-07-03T23:10:36Z, elapsed 9.24s, seeds [7,13,19]): verdict=HARD_PASS, cardinality "
        "36/36, verdict_msg parametrized to 'across 3 seeds'. arm_runtime_call_trace field "
        "records forward_call_delta per arm: m14_composed=50/individual=0/ablated=50, "
        "m15_composed=10/individual=0/ablated=0, m17_composed=1/individual=0/ablated=1, "
        "m18_composed=individual=ablated=0. Expected pattern per arm ('forward_ge_1' or "
        "'forward_eq_0') matched with trace_ok=True on ALL 12 arms. This UPGRADES arms_differ "
        "from source-fingerprint DECORATIVE to runtime-trace BEHAVIOR-DELTA verified for "
        "m14/m15/m17: composed genuinely invokes cx.forward, individual genuinely does not. "
        "Per-primitive metrics: m14/m15/m17 composed=individual=1.0 exact all seeds, ablated=0 "
        "exact; m18 composed=individual={0.68, 0.65, 0.65} matched exact (cv=0.021427 "
        "reproduces to 1e-6 vs metrics), ablated=0 exact. m18 STAYS MM_STANDARD (declared "
        "tautological per amendment, bypasses cx.forward by design; runtime trace confirms "
        "declaration but cannot upgrade substantive-composition claim). CG upgrade applies to "
        "m14/m15/m17 only (3 of 4 primitives in this cell; M1.3 noise and M1.6 attention "
        "router covered by separate CG atoms 2026-07-02). Residual caveats: m14/m15/m17 "
        "COMPOSED metric hits 1.0 ceiling at small K=5/16/32 (runtime-trace upgrades arms_differ "
        "not stress-scale composition equivalence); ablation-at-zero-by-design remains floor-"
        "anchored-by-design declaration; scale-stress composition equivalence still beyond scope. "
        "What IS proven: (a) cortex facade genuinely invokes cx.forward for composed arms at "
        "runtime (behavior-delta verified, not source-fingerprint), (b) individual arms "
        "genuinely do not invoke cx.forward, (c) each primitive load-bearing per ablation-at-"
        "zero, (d) 24h+ deterministic reproducibility across three FULL runs (2026-07-02 CG, "
        "2026-07-03 22:55Z amendment, 2026-07-03 23:10Z post-fix)."
    ),
    "provenance": {
        "cell": "experiments/exp_cortex_integration_end_to_end_v1.py",
        "commit": CELL_COMMIT,
        "prereg": "preregs/2026-07-02_cortex_integration_end_to_end_v1.md",
        "anchor": "exp_cortex_integration_end_to_end_v1",
        "metrics_path": "data/exp_cortex_integration_end_to_end_v1/metrics.json",
        "metrics_ts_iso": "2026-07-03T23:10:36.800510+00:00",
        "elapsed_s": 9.241364499990596,
        "seeds": [7, 13, 19],
        "ts_iso": TS_ISO,
        "atomized_by": ATOMIZED_BY,
        "verified_off_data": True,
        "verified_off_data_note": (
            "Independent recompute this session: m18 cv=0.021427 to 1e-6; all 12 arms "
            "trace_ok=True per off-disk arm_runtime_call_trace inspection; verdict_msg "
            "confirmed parametrized 'across 3 seeds'; cardinality 36/36; per-seed per-arm "
            "per-primitive off per_seed and per_unit blocks."
        ),
    },
    "runtime_trace_verification": {
        "arms_differ_discriminator": "runtime_call_trace_meta_rule_AF_v2",
        "all_12_arms_trace_ok": True,
        "per_arm_forward_call_delta": {
            "m14_composed": 50, "m14_individual": 0, "m14_ablated": 50,
            "m15_composed": 10, "m15_individual": 0, "m15_ablated": 0,
            "m17_composed": 1, "m17_individual": 0, "m17_ablated": 1,
            "m18_composed": 0, "m18_individual": 0, "m18_ablated": 0,
        },
        "per_arm_expected_pattern": {
            "m14_composed": "forward_ge_1", "m14_individual": "forward_eq_0", "m14_ablated": "forward_ge_1",
            "m15_composed": "forward_ge_1", "m15_individual": "forward_eq_0", "m15_ablated": "forward_eq_0",
            "m17_composed": "forward_ge_1", "m17_individual": "forward_eq_0", "m17_ablated": "forward_ge_1",
            "m18_composed": "forward_eq_0", "m18_individual": "forward_eq_0", "m18_ablated": "forward_eq_0",
        },
        "discriminator_class": "PATTERN_BASED_CATEGORICAL_NOT_ABSOLUTE_COUNT",
        "discriminator_upgrade": "source_fingerprint_DECORATIVE_to_runtime_behavior_delta_VERIFIED",
    },
    "delta_summary": {
        "m14": {"max_delta": 0.0, "per_seed_delta": [0.0, 0.0, 0.0], "composed_mean": 1.0, "individual_mean": 1.0},
        "m15": {"max_delta": 0.0, "per_seed_delta": [0.0, 0.0, 0.0], "composed_mean": 1.0, "individual_mean": 1.0},
        "m17": {"max_delta": 0.0, "per_seed_delta": [0.0, 0.0, 0.0], "composed_mean": 1.0, "individual_mean": 1.0},
        "m18": {"max_delta": 0.0, "per_seed_delta": [0.0, 0.0, 0.0], "composed_mean": 0.66, "individual_mean": 0.66},
    },
    "cv_summary": {"m14": 0.0, "m15": 0.0, "m17": 0.0, "m18": 0.021427478217774184},
    "ablation_summary": {
        "m14": {"max_ablated": 0.0}, "m15": {"max_ablated": 0.0},
        "m17": {"max_ablated": 0.0}, "m18": {"max_ablated": 0.0},
    },
    "cg_upgrade_scope": {
        "primitives_upgraded_to_CG": ["m14_refuse_gate", "m15_two_tier_context", "m17_role_slot_summarizer"],
        "primitives_stay_MM": ["m18_clarify_gate"],
        "reason_m18_stays_MM": (
            "m18 bypasses cx.forward by design (expected_pattern=forward_eq_0 all 3 arms). "
            "Runtime-trace discriminator confirms the DECLARATION of tautology but cannot "
            "upgrade substantive-composition claim for m18. Amendment tier MM_STANDARD holds."
        ),
        "primitives_not_covered_this_cell": ["m13_noise", "m16_attention_router"],
        "external_coverage": (
            "M1.3 noise: cortex_integration_with_noise_channel_v1_Phase3b_CG (2026-07-02). "
            "M1.6 attention router: EXP_cortex_integration_m16_attention_router_v1 CG (2026-07-02)."
        ),
    },
    "residual_caveats": [
        "m14/m15/m17 COMPOSED metric hits 1.0 ceiling at small K (5/16/32); runtime-trace upgrades arms_differ but not stress-scale composition equivalence",
        "m18 stays MM_STANDARD per prior amendment; declared tautology not substantive composition",
        "ablation-at-zero-by-design remains floor-anchored-by-design declaration semantic",
        "scale-stress composition equivalence off ceiling for m14/m15/m17 remains beyond scope",
        "4-of-6-primitive coverage caveat: this cell tests m14/m15/m17/m18; M1.3 and M1.6 covered by separate CG atoms",
    ],
    "framing_corrections_vs_director_prompt": [
        "Director prompt listed expected forward-call-delta numbers (m14=20, m14_ablated=20, m15=6) as if they should reproduce at FULL; actual FULL shows m14=50, m14_ablated=50, m15=10, m17=1, m18=0. NOT A FAILURE: discriminator is PATTERN-BASED (forward_ge_1 vs forward_eq_0), all trace_ok=True; the prompt-cited numbers were SMOKE-scale (n_queries=20), FULL scales to n_queries=50 for m14 and k_writes=5 with write-through doubles to 10 for m15. Fix#28-adjacent SMOKE-to-FULL inherit-of-expected-numbers catch; substrate discriminator meta-rule is correct.",
        "Director prompt states 'landed 00:20Z UTC 2026-07-04'; metrics.json ts_iso is 2026-07-03T23:10:36Z (about 70 min earlier). Minor timestamp framing catch; substance unaffected.",
    ],
    "supersedes": [PRIOR_AMENDMENT_ID],
    "supersede_reason": (
        "Revival criterion of prior amendment (MM_STANDARD 2026-07-03T23:20:00Z) explicitly "
        "specified: post-fix c16c72ca5 FULL landing with per-arm forward-call-delta MATCHING "
        "_ARM_TRACE_EXPECTED patterns + m18 declared-tautological -> MM_STANDARD -> CG upgrade "
        "permitted. All 4 gates verified this VET (post-fix commit, FULL, 12/12 trace_ok "
        "pattern matches, m18 declared). CG upgrade applies to m14/m15/m17; m18 retains MM tier."
    ),
    "composes": [
        "M1.4_CG_conformal_cal",
        "M1.5_CG_cortex_context_TWOTIER",
        "M1.7_CG_cortex_role_slot",
        "M1.8_CG_CLARIFY_5prim",
        "cortex_integration_with_noise_channel_v1_Phase3b_CG_2026-07-02",
        "cortex_integration_m16_attention_router_v1_Phase3c_CG_2026-07-02",
    ],
    "arms_differ_verified": True,
    "cardinality_ok": True,
    "n_units": 36,
    "expected_n_units": 36,
    "run_mode": "full",
    "storage_strategy": "MIXED_inherited_per_primitive_no_facade_storage",
    "primitives_tested": ["m14_refuse_gate", "m15_two_tier_context", "m17_role_slot_summarizer", "m18_clarify_gate"],
    "positive_control_check": (
        "Ablated arms below floor 0.1 all seeds all 4 primitives (ablated=0.0 exact). "
        "per_primitive_reproduces=True all 4. HARD_PASS off substantive equivalence not "
        "test-design PC. Auditor-2026-07-01 rule cleared."
    ),
    "cross_arc_overlap_check": (
        "Direct match to prior amendment on same anchor (cosine=1.0, self-supersede as "
        "revival-criterion-satisfied). Prior 2026-07-02 CG already superseded by amendment; "
        "this CG UPGRADE now supersedes the amendment with runtime-trace strengthening."
    ),
}

ledger_math_CG_UPGRADE = {
    "atom_id": atom_math_CG_UPGRADE["id"],
    "corpus": "math",
    "tier": "T3",
    "disposition": "CHAIN_GRADE_UPGRADE_FROM_MM_STANDARD_via_revival_criterion_MET",
    "cert_delta": {"CG": 1, "MM": -1, "HF": 0},
    "cert_delta_note": (
        "CG +1 for m14/m15/m17 cortex facade composition integrity runtime-trace verified. "
        "MM -1 to supersede prior amendment (2026-07-03T23:20:00Z MM_STANDARD). Net CG +1 MM -1."
    ),
    "provenance": atom_math_CG_UPGRADE["provenance"],
    "notes": (
        "Revival criterion of prior amendment MET (post-fix c16c72ca5 FULL with all 12 arms "
        "trace_ok=True on runtime_call_trace_meta_rule_AF_v2 discriminator + m18 declared "
        "explicitly-tautological). m14/m15/m17 promoted to CG via runtime-trace behavior-"
        "delta verification (arms_differ upgraded from source-fingerprint DECORATIVE to "
        "runtime-trace VERIFIED). m18 stays MM_STANDARD per amendment (declared tautology). "
        "Framing catches vs Director prompt: (A) prompt-cited SMOKE-scale forward-call-delta "
        "numbers not reproduced at FULL because discriminator is categorical not absolute-"
        "count (Fix#28-adjacent SMOKE-to-FULL inherit); (B) prompt landing timestamp off by "
        "70 min. Neither affects substance. Positive controls (ablated=0 all primitives) "
        "PASS; not test-design failure."
    ),
    "ts_iso": TS_ISO,
    "atomized_by": ATOMIZED_BY,
    "supersedes_ledger_entry_for": PRIOR_AMENDMENT_ID,
}


def append_jsonl_a5(path: Path, new_row: dict, label: str) -> int:
    pre_lines = []
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            pre_lines = f.read().splitlines()
    pre_count = len(pre_lines)
    print(f"[A5] {label}: pre_count={pre_count}")

    for i, ln in enumerate(pre_lines):
        if not ln.strip():
            continue
        try:
            json.loads(ln)
        except Exception as e:
            raise RuntimeError(f"PRE integrity fail line {i+1}: {e}")

    new_line = json.dumps(new_row, ensure_ascii=True)
    parsed_back = json.loads(new_line)
    if "id" in new_row:
        assert parsed_back.get("id") == new_row.get("id")
    if "atom_id" in new_row:
        assert parsed_back.get("atom_id") == new_row.get("atom_id")

    out_text = "\n".join(pre_lines + [new_line]) + "\n"
    tmp_path = path.with_suffix(path.suffix + ".tmp_a5")
    with open(tmp_path, "w", encoding="utf-8") as f:
        f.write(out_text)
        f.flush()
        os.fsync(f.fileno())
    import time as _time
    for _attempt in range(10):
        try:
            os.replace(str(tmp_path), str(path))
            break
        except PermissionError:
            if _attempt == 9:
                raise
            _time.sleep(0.1 * (2 ** _attempt))

    with open(path, "r", encoding="utf-8") as f:
        post_lines = f.read().splitlines()
    post_count = len(post_lines)
    print(f"[A5] {label}: post_count={post_count}")
    assert post_count == pre_count + 1

    tail = json.loads(post_lines[-1])
    if "id" in new_row:
        assert tail["id"] == new_row["id"]
    if "atom_id" in new_row:
        assert tail["atom_id"] == new_row["atom_id"]

    for i, ln in enumerate(post_lines):
        if not ln.strip():
            continue
        try:
            json.loads(ln)
        except Exception as e:
            raise RuntimeError(f"POST integrity fail line {i+1}: {e}")

    print(f"[A5] {label}: OK")
    return post_count


def main():
    print(f"[A5] atomize START {ATOMIZED_BY} ts={time.time():.3f}")
    append_jsonl_a5(MATH_ATOMS, atom_math_CG_UPGRADE,
                    "math/atoms (cortex_e2e_v1 POST-FIX CG UPGRADE)")
    append_jsonl_a5(CERT_LEDGER, ledger_math_CG_UPGRADE,
                    "cert_ledger (CG +1, MM -1 supersede amendment)")
    print(f"[A5] DONE OK")
    print(f"[A5] cortex_e2e_v1 CG UPGRADE (+1 CG, -1 MM) via revival criterion MET")


if __name__ == "__main__":
    main()
