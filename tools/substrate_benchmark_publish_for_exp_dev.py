"""Republish benchmark JSONL in Exp-Dev's requested format with routed_primitive + routed_args.

Per Research GAP_7_V1_RESULTS_GAP_4_PRIORITY 2026-06-12 + B-axis vocab reconciliation:

Output fields per Q:
- qid
- question_type (A/B/C/D/E/F/G/negative)
- question_text
- gold_atom_set
- routed_primitive (semantic intent classifier output: what_do_you_know_about /
  what_serves / composition_paths / predecessors_via / solution_history_lookup /
  methodology_rules_for / coverage_report / pattern_atoms)
- routed_args (primitive args)
- answerable (bool)

ALSO reconciles vocab for Q06-B / Q07-B / Q09-B per Research request:
- Q06-B: decompose -> DEPENDS_ON or USES
- Q07-B: USE -> USES + INSTANCE_OF + DEFINED_OVER
- Q09-B: USED_FOR_LIFT -> solution_history_lookup primitive
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


VOCAB_RECONCILE = {
    "Q06-B": {
        "question_text": "Which atoms reference math::T2/fhrr_bind via DEPENDS_ON or USES (substrate vocab; reconciled from 'decompose_to')?",
        "routed_primitive": "predecessors_via",
        "routed_args": {"target": "math::T2/fhrr_bind", "rel_types": ["DEPENDS_ON", "USES"]},
    },
    "Q07-B": {
        "question_text": "Which atoms reference math::T1/markov_chain via USES, INSTANCE_OF, or DEFINED_OVER (substrate vocab; reconciled from 'USES')?",
        "routed_primitive": "predecessors_via",
        "routed_args": {"target": "math::T1/markov_chain",
                         "rel_types": ["USES", "INSTANCE_OF", "DEFINED_OVER"]},
    },
    "Q09-B": {
        "question_text": "Which math atoms appear in concept::PP-364_pos_tagger's lift chain via solution_history (substrate vocab; reconciled from 'USED_FOR_LIFT')?",
        "routed_primitive": "solution_history_lookup",
        "routed_args": {"capability": "concept::PP-364_pos_tagger",
                         "corpus_filter": "math"},
    },
}


def route_question(q: dict) -> tuple[str, dict]:
    """Map question to routed_primitive + routed_args per Research's table."""
    qtype = q["type"]
    qtext = q["question"]

    if q["qid"] in VOCAB_RECONCILE:
        rec = VOCAB_RECONCILE[q["qid"]]
        return rec["routed_primitive"], rec["routed_args"]

    if qtype == "A_content":
        # what_do_you_know_about(TOPIC)
        return "what_do_you_know_about", {"topic": qtext, "top_k": 12}

    if qtype == "B_relation":
        anchor = q.get("anchor")
        rel = q.get("relation", "").upper()
        if rel in ("DECOMPOSE_TO", "DECOMPOSES_TO"):
            return "predecessors_via", {"target": anchor, "rel_types": ["DEPENDS_ON", "USES"]}
        if rel == "INSTANCE_OF":
            return "predecessors_via", {"target": anchor, "rel_types": ["INSTANCE_OF"]}
        if rel == "USES":
            return "predecessors_via", {"target": anchor, "rel_types": ["USES", "INSTANCE_OF", "DEFINED_OVER"]}
        if rel == "DEPENDS_ON":
            return "predecessors_via", {"target": anchor, "rel_types": ["DEPENDS_ON"]}
        if rel == "SUPERSEDES":
            return "supersedes_pairs", {"anchor": anchor}
        return "predecessors_via", {"target": anchor, "rel_types": [rel] if rel else []}

    if qtype == "C_capability":
        return "what_serves", {"capability": q.get("anchor", "")}

    if qtype == "D_composition":
        return "composition_paths", {
            "src": q.get("anchor_src"), "tgt": q.get("anchor_tgt"), "max_depth": 4,
            "bidirectional": True,
        }

    if qtype == "E_methodology":
        return "methodology_rules_for", {"scenario": qtext}

    if qtype == "F_gap":
        return "coverage_report", {"capability": q.get("anchor", ""), "qualitative": True}

    if qtype == "G_pattern":
        return "pattern_atoms", {"pattern": qtext}

    if qtype == "negative":
        return "what_do_you_know_about", {"topic": qtext, "top_k": 12,
                                          "honesty_filter": True}

    return "unknown", {}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", type=Path,
                    default=Path("data/substrate_index/benchmark_corpus_v2_60q.jsonl"))
    ap.add_argument("--output", type=Path,
                    default=Path("data/substrate_index/gap_7_benchmark.jsonl"))
    args = ap.parse_args()

    questions = []
    with open(args.input, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            questions.append(json.loads(line))

    with open(args.output, "w", encoding="utf-8") as f:
        for q in questions:
            routed_primitive, routed_args = route_question(q)
            # Update question_text if vocab-reconciled
            qtext = (VOCAB_RECONCILE.get(q["qid"]) or {}).get("question_text", q["question"])
            out = {
                "qid": q["qid"],
                "question_type": q["type"],
                "question_text": qtext,
                "gold_atom_set": q.get("ground_truth_atoms", []),
                "expected_boolean": q.get("expected_boolean"),
                "expected_response": q.get("expected_response"),
                "score_mode": q.get("score_mode", "set_overlap"),
                "answerable": q.get("answerable", True),
                "honesty_partial": q.get("honesty_partial", False),
                "routed_primitive": routed_primitive,
                "routed_args": routed_args,
            }
            f.write(json.dumps(out, ensure_ascii=False) + "\n")

    print(f"Published {len(questions)} questions to {args.output}")


if __name__ == "__main__":
    main()
