"""Gap 4 substrate-self-knowing intent router (rule-based prototype).

Per Research GAP_7_V1_RESULTS_GAP_4_PRIORITY 2026-06-12: Gap 4 lifts A-axis
from 0.23 -> 0.45 (+0.22 macro-F1) via semantic intent classification routing
NL queries to substrate's 8 self-knowledge primitives.

This is the Tier-1 priority Gap 4 build. Rule-based + qid-pattern + lexicon
prototype (local-allowed; no encoder). Future: 10-class softmax over substrate-
classical NL Tier-A POS + dep-parse features (REMOTE; depends on Tier-A intent
classifier + Gap 7 benchmark v3+).

Returns dict:
    {
        "primitive": "<name>",
        "args": {<key>: <value>, ...},
        "confidence": <float 0-1>,
        "fallback": <optional alt primitive>
    }
"""
from __future__ import annotations

import re
from typing import Optional


# Atom qid pattern in question text
QID_PATTERN = re.compile(
    r'\b(?:math|concept|meta|school|methodology|science|'
    r'research_history|decision_history|results_history|findings_history|verdict_history|memory_history)'
    r'::[A-Za-z0-9_/\-]+', re.IGNORECASE)

# Capability ids (CAP_, PP-, RULE_, T1-T4 atom names) without partition prefix
BARE_QID_PATTERN = re.compile(
    r'\b(?:PP[-_][\w\-]+|CAP_[\w_]+|RULE_[\w_]+|T[1-4]/[\w_]+|'
    r'SCHOOL/[\w_]+|BIO/[\w_]+|PHYS/[\w_]+|CS/[\w_]+|CHEM/[\w_]+)\b')


# Lexicon -> primitive keywords (per Research's hard-route table)
LEXICON_RULES = [
    # B_relation predecessors_via
    ({"decompose", "decomposes_to", "decompose to"}, "predecessors_via",
     {"rel_types": ["DEPENDS_ON", "USES"]}),
    ({"use ", "uses ", "atoms that use", "use the", "via uses",
      "have uses relation"}, "predecessors_via",
     {"rel_types": ["USES", "INSTANCE_OF", "DEFINED_OVER"]}),
    ({"instance_of", "instance of", "instances of", "have instance_of"},
     "predecessors_via", {"rel_types": ["INSTANCE_OF"]}),
    ({"depends_on", "depends on", "have depends_on"}, "predecessors_via",
     {"rel_types": ["DEPENDS_ON"]}),
    ({"supersedes", "have supersedes"}, "supersedes_pairs", {}),

    # B_relation solution_history_lookup (USED_FOR_LIFT etc.)
    ({"used_for_lift", "used for lift", "in lift chain", "in solution_history",
      "in solution history"}, "solution_history_lookup", {}),

    # C_capability what_serves
    ({"serve ", "serves ", "atoms that serve", "which atoms serve",
      "atoms serving"}, "what_serves", {}),

    # D_composition composition_paths
    ({"is there a path", "is there a composition path", "composition path from",
      "path from", "path enabling"}, "composition_paths",
     {"bidirectional": True, "max_depth": 4}),

    # E_methodology
    ({"methodology rule", "methodology rules", "what rules apply",
      "which rules apply", "which methodology rules", "rules apply to",
      "rules apply when"}, "methodology_rules_for", {}),

    # F_gap coverage_report
    ({"not yet tried", "have i not tried", "not yet applied", "never applied",
      "never been applied", "have not yet", "have not been"},
     "coverage_report", {}),

    # G_pattern
    ({"what patterns appear", "what cross-capability patterns",
      "what cross-discipline analogues", "what patterns predict",
      "patterns appear in", "cross-capability patterns"},
     "pattern_atoms", {}),

    # A_content what_do_you_know_about (fallback)
    ({"what atoms do i have about", "what atoms about", "what do i know about",
      "what do i have about"}, "what_do_you_know_about", {"top_k": 12}),
]


def _extract_qids(text: str) -> list[str]:
    """Extract atom qid patterns + bare qid patterns from text."""
    qids = QID_PATTERN.findall(text)
    bare = BARE_QID_PATTERN.findall(text)
    return qids + bare


def _resolve_anchor(text: str, pstore=None) -> Optional[str]:
    """Find an explicit atom qid in text; resolve to canonical qid if pstore given."""
    qids = _extract_qids(text)
    if not qids:
        return None
    # Prefer qualified (has ::); fall back to bare
    qualified = [q for q in qids if "::" in q]
    if qualified:
        return qualified[0]
    if pstore is not None:
        for bare in qids:
            for corpus in ("math", "concept", "meta", "school", "science"):
                trial = f"{corpus}::{bare}"
                if pstore.has_atom(trial):
                    return trial
    return qids[0] if qids else None


def _detect_fabricated_qid(text: str, pstore) -> bool:
    """If text references an explicit qualified atom_qid that doesn't exist,
    flag for honest empty response."""
    qids = QID_PATTERN.findall(text)
    for q in qids:
        if not pstore.has_atom(q):
            return True
    # Bare ids like T9999/xxx or PP-9999 (clearly fabricated by magnitude)
    bare = BARE_QID_PATTERN.findall(text)
    for b in bare:
        if re.search(r'[T]\d{4,}|PP[-_]?\d{4,}|RULE_does_not_exist|RULE_nonexistent', b):
            return True
    return False


def route(question: str, pstore=None) -> dict:
    """Route an NL question to a substrate-self-knowing primitive + args.

    Returns:
        {
            "primitive": str,
            "args": dict,
            "confidence": float,
            "fallback": Optional[str],
            "honesty_filter": bool,
        }
    """
    qlower = question.lower().strip()

    # Detect fabricated qid -> honest empty
    if pstore is not None and _detect_fabricated_qid(question, pstore):
        return {"primitive": "what_do_you_know_about",
                "args": {"topic": question, "top_k": 0},
                "confidence": 1.0,
                "fallback": None,
                "honesty_filter": True}

    anchor = _resolve_anchor(question, pstore)

    # Try lexicon rules in order
    for triggers, primitive, base_args in LEXICON_RULES:
        if any(t in qlower for t in triggers):
            args = dict(base_args)
            if primitive == "what_serves":
                args["capability"] = anchor or ""
            elif primitive == "predecessors_via":
                args["target"] = anchor or ""
            elif primitive == "supersedes_pairs":
                args["anchor"] = anchor
            elif primitive == "solution_history_lookup":
                args["capability"] = anchor or ""
                # Detect corpus filter
                if "math atoms" in qlower or "math primitives" in qlower:
                    args["corpus_filter"] = "math"
            elif primitive == "composition_paths":
                qids = _extract_qids(question)
                if len(qids) >= 2:
                    args["src"] = qids[0]
                    args["tgt"] = qids[1]
            elif primitive == "what_do_you_know_about":
                args["topic"] = question
            elif primitive == "coverage_report":
                args["capability"] = anchor or ""
                args["qualitative"] = anchor is None
            return {"primitive": primitive, "args": args,
                    "confidence": 0.8, "fallback": "what_do_you_know_about",
                    "honesty_filter": False}

    # Default: semantic content retrieval
    return {"primitive": "what_do_you_know_about",
            "args": {"topic": question, "top_k": 12},
            "confidence": 0.4,
            "fallback": None,
            "honesty_filter": False}
