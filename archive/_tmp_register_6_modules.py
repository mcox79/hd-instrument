#!/usr/bin/env python3
"""One-shot A5-gated append of 6 registry rows (skunkworks audit 2026-08-12).
Atomic write (tmp + os.replace), verify-load, integrity check. Does NOT touch
any existing row -- append-only."""
from __future__ import annotations
import json
import os
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parent.parent
REGISTRY = ROOT / "data" / "capability_registry.jsonl"
NOW = "2026-08-12T19:03:54Z"

NEW_ROWS = [
    {
        "id": "gap_detector_familiarity_gate",
        "name": "hdlab/gap_detector.py -- GapDetector familiarity/novelty gate ('do I already know this word')",
        "kind": "hdlab-module",
        "path": ["hdlab/gap_detector.py"],
        "status": "validated_hard_pass_signal_detection_2026-08-12",
        "gate_decision": "WIRE",
        "gate_decision_target": "Already wired: real `from hdlab.gap_detector import GapDetector` in hdlab/reading_grounding_loop.py (GAP_FLOOR=0.625 gate at read time); also consumed by hdlab/gap_driven_reader.py and hdlab/foundation_persistence.py.",
        "integration_status": "WIRED",
        "used_by": [
            "hdlab/reading_grounding_loop.py",
            "hdlab/gap_driven_reader.py",
            "hdlab/foundation_persistence.py",
            "experiments/exp_gap_detection_autonomous_confidence_v1.py",
        ],
        "revival_criteria": None,
        "supersedes": None,
        "superseded_by": None,
        "current_best_for": "familiarity/novelty signal (know-vs-unknown gate) for the self-directed reading-grounding pipeline",
        "provenance": "data/exp_gap_detection_autonomous_confidence_v1/metrics.json verdict=HARD_PASS ('all 4 axes (signal-detection / not-a-lookup / scramble / end-to-end) HARD_PASS', t1_auc=1.0000, t1_dprime=5.1517); disk-verified 2026-08-12 skunkworks registry audit (import lines confirmed live in hdlab/reading_grounding_loop.py:96).",
        "last_audit_utc": NOW,
        "last_decision_utc": NOW,
        "pipeline_status": "WIRED_AND_PIPELINE_USED",
    },
    {
        "id": "gap_driven_reader_self_directed_order",
        "name": "hdlab/gap_driven_reader.py -- self-directed 'what to read next' prerequisite-ID + reading-order selector",
        "kind": "hdlab-module",
        "path": ["hdlab/gap_driven_reader.py"],
        "status": "validated_hard_pass_full_2026-08-12",
        "gate_decision": "WIRE",
        "gate_decision_target": "Validated standalone (exp_gap_driven_reader_controlled_v1 HARD_PASS full run); NOT YET imported by hdlab/reading_grounding_loop.py itself as of this audit (grep-verified: zero hits) -- next step is to wire its read-selection into that loop's per-cycle ordering, currently hand-ordered curriculum.",
        "integration_status": "TRAPPED_SHARED",
        "used_by": [
            "experiments/exp_gap_driven_reader_controlled_v1.py",
            "hdlab/gap_detector.py (consumed as a dependency, not a consumer)",
        ],
        "revival_criteria": None,
        "supersedes": None,
        "superseded_by": None,
        "current_best_for": "autonomous prerequisite-identification + read-order prioritization ('read math before QM')",
        "provenance": "data/exp_gap_driven_reader_controlled_v1/metrics.json verdict=HARD_PASS ('all bands cleared with >5% margin'); MEMORY.md 2026-08-12 cites autonomous prereq-ID precision 1.0/ablated 0.0, grounds 8/8 real vs 0/8 ablated vs 0.125 random. Disk-verified 2026-08-12; NOT yet wired into the active pipeline (honest gap noted, not overstated).",
        "last_audit_utc": NOW,
        "last_decision_utc": NOW,
        "pipeline_status": "WIRED_BUT_NOT_PIPELINE_REACHABLE",
    },
    {
        "id": "foundation_persistence_roundtrip",
        "name": "hdlab/foundation_persistence.py -- foundation save/reload persistence (bit-identical round-trip, resumable per-segment)",
        "kind": "hdlab-module",
        "path": ["hdlab/foundation_persistence.py"],
        "status": "validated_hard_pass_at_scale_2026-08-12",
        "gate_decision": "WIRE",
        "gate_decision_target": "Consumed directly by experiments/exp_reading_grounding_loop_cycle2_v1.py and exp_reading_grounding_loop_cycle3_groundingfix_v1.py (the active reading-loop cycle cells, concurrently in-flight in another session) and validated standalone via exp_foundation_validation_harness_v1. Not yet imported by hdlab/reading_grounding_loop.py's own module body (grep-verified) -- persistence is currently invoked at the cell layer, not inside the hdlab organ; note for future consolidation.",
        "integration_status": "TRAPPED_SHARED",
        "used_by": [
            "experiments/exp_foundation_validation_harness_v1.py",
            "experiments/exp_reading_grounding_loop_cycle2_v1.py",
            "experiments/exp_reading_grounding_loop_cycle3_groundingfix_v1.py",
        ],
        "revival_criteria": None,
        "supersedes": None,
        "superseded_by": None,
        "current_best_for": "durable foundation store persistence across reading-loop cycles (crash-resumable)",
        "provenance": "data/exp_foundation_validation_harness_v1/metrics.json verdict=HARD_PASS_foundation_validated ('claim1=HARD_PASS(gap=0.2533) claim2=HARD_PASS(cohesion=0.4765,contra=0) claim3=HARD_PASS(mech=1.0,scr=0.0,abl=0.0)'); MEMORY.md 2026-08-12 cites bit-identical round-trip at scale + survived mid-run process death. Disk-verified 2026-08-12.",
        "last_audit_utc": NOW,
        "last_decision_utc": NOW,
        "pipeline_status": "WIRED_BUT_NOT_PIPELINE_REACHABLE",
    },
    {
        "id": "closed_class_lexicon_function_word_gate",
        "name": "hdlab/closed_class_lexicon.py -- UD-functional-class + spaCy-stopword closed-class (function-word) eligibility gate",
        "kind": "hdlab-module",
        "path": ["hdlab/closed_class_lexicon.py"],
        "status": "validated_measured_2026-08-12",
        "gate_decision": "WIRE",
        "gate_decision_target": "Already wired: real import in hdlab/reading_grounding_loop.py (is_closed_class/is_eligible_meaning, killed also/say/like/more/most as false 'meanings'), hdlab/definitional_extraction.py, hdlab/low_information_filter.py, experiments/exp_definitional_grounding_v3.py.",
        "integration_status": "WIRED",
        "used_by": [
            "hdlab/reading_grounding_loop.py",
            "hdlab/definitional_extraction.py",
            "hdlab/low_information_filter.py",
            "experiments/exp_definitional_grounding_v3.py",
            "experiments/exp_reading_grounding_loop_cycle3_groundingfix_v1.py",
        ],
        "revival_criteria": None,
        "supersedes": None,
        "superseded_by": None,
        "current_best_for": "function-word / no-referential-content exclusion for grounding-object eligibility, corpus-measured (UD EWT majority-tag + spaCy stopwords), not hand-listed",
        "provenance": "hdlab/closed_class_lexicon.py docstring cites the 2026-08-12 foundation audit (also=31/say=15/people=10/like=5/more=5/most=5 as false top 'meanings') as the measured motivation; import verified live in 3 hdlab modules + 2 exp cells 2026-08-12.",
        "last_audit_utc": NOW,
        "last_decision_utc": NOW,
        "pipeline_status": "WIRED_AND_PIPELINE_USED",
    },
    {
        "id": "definitional_extraction_surface_patterns",
        "name": "hdlab/definitional_extraction.py -- glass-box definitional-sentence extractor (copula/appositive/glossary-colon/called/refers-to)",
        "kind": "hdlab-module",
        "path": ["hdlab/definitional_extraction.py"],
        "status": "structural_pass_pending_b3_2026-08-12",
        "gate_decision": "VET_PENDING",
        "gate_decision_target": "exp_definitional_grounding_v3 verdict is STRUCTURAL_PASS_PENDING_B3 (DEF arm banked 1751 facts, 1749 not produced by the distributional path; B3 hand-scored comparison NOT YET DONE). Do not WIRE into hdlab/reading_grounding_loop.py's grounding-object selection until B3 hand-scoring lands; module's own 12-case regression self-test passes (python -m hdlab.definitional_extraction). Registry-checked BEFORE build 2026-08-12 (capability_registry_query.py --serves returned 0/107); independently confirmed via git-history + registry-blob search: no prior module implements copula/appositive/glossary-colon/called/refers-to definitional extraction (MAVEN-ERE = causal/subevent relation classification, disjoint job; the '0.90 reading extractor' cited in notes/SUBSTRATE_CHARTER = experiments/exp_stated_entity_fate_reading_extractor_v2_highprecision.py, a (entity,fate_via_verb)->CREATE/MOVE/DESTROY process-state extractor, also disjoint job). VERDICT: genuinely novel, not a duplicate.",
        "integration_status": "TRAPPED_SHARED",
        "used_by": ["experiments/exp_definitional_grounding_v3.py"],
        "revival_criteria": None,
        "supersedes": None,
        "superseded_by": None,
        "current_best_for": "orthogonal EXPLICIT-definitional-structure signal alongside the distributional canonicalize() grounding path (see module docstring 'WHY THIS EXISTS')",
        "provenance": "data/exp_definitional_grounding_v3/metrics.json verdict=STRUCTURAL_PASS_PENDING_B3. Skunkworks Task-A audit 2026-08-12: checked git log -S 'definiendum'/'appositive'/'copula' across full history + capability_registry.jsonl blob search + hdlab/reading_grounding_loop.py (concurrent-session file, read-only) -- no prior definitional extractor found. DISJOINT from MAVEN-ERE (causal/subevent, F1 14.78/13.63) and from exp_stated_entity_fate_reading_extractor_v2 (0.90-precision ENTITY-FATE extractor, not definitions).",
        "last_audit_utc": NOW,
        "last_decision_utc": NOW,
        "pipeline_status": "N_A",
    },
    {
        "id": "low_information_filter_pmi_flatness_gate",
        "name": "hdlab/low_information_filter.py -- corpus-measured PMI flatness gate for grounding objects (kills 'people'-class flat nouns)",
        "kind": "hdlab-module",
        "path": ["hdlab/low_information_filter.py"],
        "status": "structural_pass_pending_b3_2026-08-12",
        "gate_decision": "VET_PENDING",
        "gate_decision_target": "Same parent cell as definitional_extraction.py (exp_definitional_grounding_v3, STRUCTURAL_PASS_PENDING_B3). Floor calibrated off the closed-class PMI reference distribution (p75=2.10 removes all 20 X->people facts, measured on 32,955 sentences), not hand-invented. Not yet imported by hdlab/reading_grounding_loop.py -- pending B3 before wiring alongside closed_class_lexicon in that loop's grounding-object gate.",
        "integration_status": "TRAPPED_SHARED",
        "used_by": ["experiments/exp_definitional_grounding_v3.py"],
        "revival_criteria": None,
        "supersedes": None,
        "superseded_by": None,
        "current_best_for": "distributional-flatness exclusion (complements closed_class_lexicon's syntactic/lexical exclusion) for the grounding-object gate",
        "provenance": "hdlab/low_information_filter.py docstring: PMI floor measured off closed-class reference PMI (p50=0.96/p75=2.10/p90=3.33); rejected alternatives (DF-threshold, raw PMI-as-quality) documented in-module with measured counter-examples (shed->quirky PMI 9.9). Disk-verified 2026-08-12; consumed by exp_definitional_grounding_v3 only so far.",
        "last_audit_utc": NOW,
        "last_decision_utc": NOW,
        "pipeline_status": "N_A",
    },
]


def main() -> int:
    with open(REGISTRY, "r", encoding="utf-8") as f:
        before_lines = [l for l in f if l.strip()]
    before_ids = {json.loads(l)["id"] for l in before_lines}
    for r in NEW_ROWS:
        if r["id"] in before_ids:
            raise SystemExit(f"REFUSING: id already present, would duplicate: {r['id']}")

    tmp = REGISTRY.with_suffix(".jsonl.tmp")
    with open(tmp, "w", encoding="utf-8", newline="") as f:
        for line in before_lines:
            f.write(line if line.endswith("\n") else line + "\n")
        for r in NEW_ROWS:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    os.replace(tmp, REGISTRY)

    # verify-load + integrity check
    with open(REGISTRY, "r", encoding="utf-8") as f:
        after_lines = [l for l in f if l.strip()]
    after_rows = [json.loads(l) for l in after_lines]
    assert len(after_lines) == len(before_lines) + len(NEW_ROWS), (
        f"row count mismatch: before={len(before_lines)} after={len(after_lines)} "
        f"expected_added={len(NEW_ROWS)}")
    after_ids = [r["id"] for r in after_rows]
    assert len(after_ids) == len(set(after_ids)), "duplicate id introduced"
    for r in NEW_ROWS:
        assert r["id"] in after_ids, f"missing after write: {r['id']}"
    print(f"OK: {len(before_lines)} -> {len(after_lines)} rows "
          f"(+{len(NEW_ROWS)}), verify-load clean, no duplicate ids")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
