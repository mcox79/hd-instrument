"""
A5-gated atomize: META_RULE -- env-var-contract-must-survive-runner-dispatch

NEW diagnosis category added to test-design-failure-and-hardening rule
(USER 2026-06-28). Caught by skunkworks during PC v2.2 dense-cliff-grid
landed-VET: all 3 sibling cells (seeds 7, 13, 19) refused FULL run at
gpu_mandate_check gate because runner did not export HDLAB_QUEUE=local_cpu_queue.

This atom is CERT-NEUTRAL methodology (no CERT delta). Filed in `meta`
corpus per Skunkworks discipline (Methodology atoms in meta; experiment
atoms in math).

Pattern detected:
  - Cell ships with env-var-gated dispensation (e.g. Fix #24 GPU mandate with
    HDLAB_QUEUE=local_cpu_queue override)
  - Pre-reg notes the contract (lines 129-137 of v2.2 prereg)
  - Runner dispatches without exporting the required env var
  - Cell-author gate refuses with clear sentinel (verdict_msg, _phase tag, elapsed_s ~ 0)
  - 3 seeds x identical refusal sentinel = dispatch-infra cross-seed pattern

Distinguishable from genuine substrate negative results by:
  - elapsed_s near zero (cell never reached sweep code)
  - _phase tag stops at infra gate (not at sweep / aggregation)
  - All seeds produce IDENTICAL refusal message (no per-seed variance)
  - cardinality fields are missing or zero (no phase points recorded)

PROPOSED HARDENING:

1. CELL-AUTHOR contract (exp_dev/CLAUDE.md amendment):
   Cells with env-var-gated dispensation MUST include a HEADER COMMENT block:
   ```
   # PRESERVE_ENV_VARS: HDLAB_QUEUE=local_cpu_queue
   # PRESERVE_ENV_VARS_RATIONALE: Fix #24 GPU mandate dispensation; cell will
   #   refuse FULL CPU runs unless HDLAB_QUEUE=local_cpu_queue is set.
   ```
   Greppable marker for pre-dispatch verify AND post-hoc audit.

2. SKUNKWORKS SCHEMA-VET gate (added to pre-dispatch checklist):
   On any cell pre-reg SCHEMA-VET, if cell source contains env-var dispensation
   gates (regex: `os.environ.get\(['\"](HDLAB_|HDI_)`), verify the runner
   dispatches with those env vars exported. If env-var-contract mismatch
   detected, SCHEMA-VET auto-fails and routes back to exp_dev for runner
   amendment.

3. RUNNER hardening (orchestrator-level, future):
   queue_add.sh / dispatch wrappers SHOULD greppably extract PRESERVE_ENV_VARS
   headers from cell source and propagate them as runtime env vars. Until
   automated, cell-author + skunkworks pre-dispatch check is the manual fallback.

Atom: 1 (meta corpus; methodology rule; CERT-neutral).
"""
import json
import os
import time
from pathlib import Path

ROOT = Path("d:/AI/hd-instrument")
META_ATOMS = ROOT / "data/substrate_index/meta/atoms.jsonl"
CERT_LEDGER = ROOT / "data/substrate_index/meta/cert_ledger.jsonl"

ATOMIZED_BY = "skunkworks_atomize_meta_rule_env_var_contract_must_survive_runner_dispatch_2026-06-28"
ATOMIZED_DATE = "2026-06-28"
CELL_COMMIT = "ac706494"

TRIGGER_ATOM = "math::T3/EXP_substrate_pattern_completion_corruption_cliff_v2p2_dense_cliff_grid_CROSS_SEED_AGG_3_of_3_DISPATCH_INFRA_FAILURE_NOT_substrate_hypothesis_test_outcome_v2p1_MM_stands_v2p3_recommended_with_HDLAB_QUEUE_set_2026-06-28"

ATOM_ID = "T_methodology/META_RULE_env_var_contract_must_survive_runner_dispatch_dispatch_infra_failure_new_diagnosis_category_under_test_design_failure_rule_2026-06-28"


atom_meta = {
    "id": ATOM_ID,
    "name": (
        "META_RULE: env-var-contract-must-survive-runner-dispatch -- "
        "new diagnosis category 'dispatch_infrastructure_failure' under test-design-failure rule"
    ),
    "corpus": "meta",
    "tier": "T_methodology",
    "kind": "methodology_rule",
    "description": (
        "METHODOLOGY RULE (CERT-neutral): Cells with env-var-gated dispensation gates "
        "(e.g. Fix #24 GPU mandate with HDLAB_QUEUE=local_cpu_queue override) require their env-var "
        "contract to survive the runner dispatch. When the runner does not export the required env vars, "
        "the cell refuses at the gate (cell-author intent honored as designed) -- but downstream parties "
        "may misclassify this as a substrate hypothesis HARD_FAIL. "
        "DIAGNOSIS CATEGORY (new; added to test-design-failure-and-hardening rule USER 2026-06-28): "
        "dispatch_infrastructure_failure -- distinguishable from substrate negatives by: "
        "(a) elapsed_s near zero (~0.01s) -- cell never reached sweep code; "
        "(b) _phase tag stops at infra gate (e.g. gpu_mandate_check), not at sweep/aggregation; "
        "(c) all seeds produce IDENTICAL refusal verdict_msg with no per-seed variance; "
        "(d) cardinality fields are missing or zero (no phase points recorded); "
        "(e) verdict_msg references specific env-var-contract gate (e.g. 'GPU_MANDATE_BREACH', "
        "'HDLAB_QUEUE='', 'Refusing'). "
        "PROPOSED HARDENING: (1) cell-author HEADER comment marker PRESERVE_ENV_VARS: <NAME>=<value> "
        "(greppable for pre-dispatch + post-hoc audit); (2) skunkworks SCHEMA-VET pre-dispatch gate "
        "verifies runner contract matches cell-source env-var-gated dispensation regex "
        "`os.environ.get\\(['\\\"](HDLAB_|HDI_)`; if mismatch, SCHEMA-VET auto-fails dispatch; "
        "(3) runner-level (orchestrator) automated header extraction + env-var propagation, future. "
        "TRIGGER: pattern_completion_corruption_cliff_v2p2_dense_cliff_grid landed 3 seeds x HARD_FAIL "
        "(verdict_msg=GPU_MANDATE_BREACH; elapsed=0.01s; _phase=gpu_mandate_check) on 2026-06-28; "
        "skunkworks landed-VET caught the dispatch-infra pattern and avoided misclassifying as substrate "
        "hypothesis HF. The cell's pre-reg explicitly noted the HDLAB_QUEUE=local_cpu_queue contract at "
        "lines 129-137 of preregs/2026-06-28_substrate_pattern_completion_corruption_cliff_v2p2_dense_cliff_grid.md "
        "but the runner dispatch did not export it. v2.1 MEASURED_MECHANISM atom stands; v2.3 re-dispatch "
        "recommended with runner-side HDLAB_QUEUE=local_cpu_queue export. "
        "DOWNSTREAM IMPACT: ~3 cell-author hours of work + 3 dispatch slots wasted (all 3 seeds refused at "
        "0.01s; tractable but wasteful); skunkworks audit time +30min to diagnose root cause; promotion path "
        "to chain-grade for pattern_completion delayed by ~1 dispatch cycle. The rule itself is the "
        "single biggest mitigation -- making the cell-runner env-var contract explicit + greppable."
    ),
    "aliases": [
        "META_RULE_env_var_contract_must_survive_runner_dispatch_2026-06-28",
        "dispatch_infrastructure_failure_new_diagnosis_category_under_test_design_failure_rule_2026-06-28",
        "PRESERVE_ENV_VARS_cell_author_header_contract_skunkworks_schema_vet_gate_2026-06-28",
        "Fix_24_GPU_mandate_dispensation_env_var_contract_must_survive_dispatch_2026-06-28",
    ],
    "metadata": {
        "provenance_quality": "OBSERVATION",
        "cert_status": "observation",
        "cert_class": "methodology_rule",
        "verdict": "META_RULE_env_var_contract_must_survive_runner_dispatch_NEW_DIAGNOSIS_CATEGORY_dispatch_infrastructure_failure_added_to_test_design_failure_catalog",
        "atomized_by": ATOMIZED_BY,
        "atomized_date": ATOMIZED_DATE,
        "cell_commit": CELL_COMMIT,
        "verified_off_data": True,
        "verified_off_data_evidence": (
            "Pattern detected via OFF-DATA read of pattern_completion_v2p2 3 sibling metrics.json: "
            "all 3 verdicts=HARD_FAIL with identical verdict_msg='GPU_MANDATE_BREACH...HDLAB_QUEUE=...Refusing'; "
            "elapsed_s=0.01 each; _phase='gpu_mandate_check' each; routed_queue='' each. "
            "Confirmed against cell source ac706494 line 191-203 + prereg lines 129-137 -- "
            "cell-author intent matches gate behavior; runner did not provide required env var."
        ),
        "triggered_by_atom": TRIGGER_ATOM,
        "trigger_anchor": "substrate_pattern_completion_corruption_cliff_v2p2_dense_cliff_grid",
        "rule_category": "test_design_failure_diagnosis_category",
        "rule_subcategory": "dispatch_infrastructure_failure",
        "new_diagnosis_category_added": True,
        "distinguishing_features": {
            "elapsed_s_near_zero": "elapsed_s ~ 0.01s (cell never executed sweep)",
            "_phase_tag_at_infra_gate": "e.g. _phase='gpu_mandate_check' not 'sweep_complete'",
            "identical_seed_verdict_msg": "all seeds produce same refusal sentinel; no per-seed variance",
            "cardinality_fields_missing": "no observed_n_units / cardinality_ok (cell pre-sweep)",
            "verdict_msg_references_gate": "explicit env-var-contract gate text (e.g. 'HDLAB_QUEUE=' empty)",
        },
        "proposed_hardening": {
            "1_cell_author_header_contract": {
                "rule": "Cells with env-var-gated dispensation MUST include a HEADER COMMENT block with PRESERVE_ENV_VARS: <NAME>=<value> markers (greppable)",
                "owner": "exp_dev (CLAUDE.md amendment)",
                "format": "# PRESERVE_ENV_VARS: HDLAB_QUEUE=local_cpu_queue\n# PRESERVE_ENV_VARS_RATIONALE: Fix #24 GPU mandate dispensation; cell will refuse FULL CPU runs unless this env var is set",
            },
            "2_skunkworks_schema_vet_gate": {
                "rule": "On pre-dispatch SCHEMA-VET, if cell source contains env-var dispensation regex `os.environ.get\\(['\\\"](HDLAB_|HDI_)`, verify runner exports those env vars before dispatch; if mismatch, auto-fail SCHEMA-VET",
                "owner": "skunkworks (pre-dispatch checklist amendment)",
                "regex": "os.environ.get\\(['\\\"](HDLAB_|HDI_)",
            },
            "3_runner_orchestrator_automation": {
                "rule": "queue_add.sh / dispatch wrappers SHOULD extract PRESERVE_ENV_VARS headers from cell source and propagate as runtime env vars",
                "owner": "orchestrator (future)",
                "status": "deferred until cell-author + skunkworks manual fallback proven insufficient",
            },
        },
        "downstream_impact_observed": {
            "cell_author_hours_wasted": 3,
            "dispatch_slots_wasted": 3,
            "skunkworks_audit_time_added_min": 30,
            "promotion_path_delay_cycles": 1,
            "substrate_hypothesis_state": "UNCHANGED (sweep never ran; v2.1 MM stands)",
        },
        "applies_to_cells_with_pattern": [
            "Fix #24 GPU mandate gate cells (HDLAB_QUEUE env var contract)",
            "Future env-var-gated dispensation cells of any kind (HDLAB_RUN_MODE, HDLAB_EXP_NAME, etc.)",
        ],
        "supersedes": None,
        "cert_increment_delta": 0,
        "discipline_tags": [
            "Fix_24_GPU_mandate_HDLAB_QUEUE_env_var_contract",
            "test_design_failure_diagnosis_and_hardening_USER_2026-06-28",
            "verify_OFF_DATA_not_reports_USER_LOCKED_skunkworks_discipline",
            "feedback_no_hallucinated_numbers_verify_on_disk_2026-06-27",
            "meta_corpus_methodology_atom_CERT_neutral",
        ],
        "ts_iso_atomized": ATOMIZED_DATE,
    },
}


_t0 = time.time()
ledger_meta = {
    "ts": _t0,
    "op": "meta_rule_observation",
    "atom_id": f"meta::{atom_meta['id']}",
    "cert_status": "observation",
    "cert_class": "methodology_rule",
    "verified_off_data": True,
    "atomized_by": ATOMIZED_BY,
    "cell_commit": CELL_COMMIT,
    "verdict": "META_RULE_env_var_contract_must_survive_runner_dispatch_new_diagnosis_category_dispatch_infrastructure_failure_added_to_test_design_failure_catalog_proposed_hardening_3_layer_cell_author_header_skunkworks_schema_vet_gate_runner_orchestrator_automation",
    "cert_increment_delta": 0,
    "cv": None,
    "referent_pointer": {
        "atom_qualified_id": f"meta::{atom_meta['id']}",
        "triggered_by_atom": TRIGGER_ATOM,
    },
    "supersedes": None,
    "note": "META_RULE env_var_contract_must_survive_runner_dispatch CERT_neutral methodology atom new diagnosis category dispatch_infrastructure_failure under test_design_failure_rule proposed_hardening_cell_author_PRESERVE_ENV_VARS_header_skunkworks_schema_vet_gate_runner_orchestrator_automation_future",
}


def append_jsonl_a5(path: Path, new_row: dict, label: str):
    """Atomic append with verify-load + integrity-check."""
    print(f"[A5] {label}: path={path}")
    assert path.exists(), f"target does not exist: {path}"
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
        assert parsed_back.get("id") == new_row.get("id"), "round-trip id mismatch"
    if "atom_id" in new_row:
        assert parsed_back.get("atom_id") == new_row.get("atom_id"), "round-trip atom_id mismatch"
    out_lines = pre_lines + [new_line]
    out_text = "\n".join(out_lines) + "\n"
    tmp_path = path.with_suffix(path.suffix + ".tmp_a5")
    with open(tmp_path, "w", encoding="utf-8") as f:
        f.write(out_text)
        f.flush()
        os.fsync(f.fileno())
    os.replace(str(tmp_path), str(path))
    with open(path, "r", encoding="utf-8") as f:
        post_lines = f.read().splitlines()
    post_count = len(post_lines)
    print(f"[A5] {label}: post_count={post_count}")
    assert post_count == pre_count + 1, f"count delta mismatch: {pre_count} -> {post_count}"
    tail = json.loads(post_lines[-1])
    if "id" in new_row:
        assert tail["id"] == new_row["id"], "tail id mismatch"
    if "atom_id" in new_row:
        assert tail["atom_id"] == new_row["atom_id"], "tail atom_id mismatch"
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
    print(f"[A5] META RULE: env-var-contract-must-survive-runner-dispatch")
    print(f"[A5] NEW diagnosis category: dispatch_infrastructure_failure")
    print(f"[A5] CERT delta = 0 (CERT-neutral methodology atom)")

    append_jsonl_a5(META_ATOMS, atom_meta, "meta/atoms.jsonl (META_RULE env_var_contract)")
    append_jsonl_a5(CERT_LEDGER, ledger_meta, "meta/cert_ledger.jsonl (META_RULE obs)")

    print(f"[A5] DONE OK")
    print(f"[A5] PROPOSED HARDENING:")
    print(f"[A5]   1. exp_dev cell-author PRESERVE_ENV_VARS header contract")
    print(f"[A5]   2. skunkworks SCHEMA-VET env-var-contract-must-survive-runner-dispatch gate")
    print(f"[A5]   3. orchestrator runner-level header extraction automation (future)")


if __name__ == "__main__":
    main()
