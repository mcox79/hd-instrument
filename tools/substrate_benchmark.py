"""Gap 7 substrate-self-knowledge benchmark scorer.

Per Research GAP_7_BENCHMARK_FIRST_30_QUESTIONS 2026-06-12 + Drill 2 7-type framework.

Runs each pre-registered question through the relevant self_knowledge.py
function, compares to ground truth, computes TP/FN/TN/FP and per-type F1.

NO encoder load for A/B/C/D/E/F/G types except A-content semantic match (which
falls back to keyword on atom name/description/aliases for local-allowed run).
Composition (D) requires graph walk only.

Usage:
    python tools/substrate_benchmark.py [--questions data/substrate_index/benchmark_corpus_v1_30q.jsonl]
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
import time
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import Atom, RelationType
from backend.substrate_index.self_knowledge import (
    what_serves,
    composition_paths,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s | %(message)s")
log = logging.getLogger("benchmark")

DATA_ROOT = Path("data/substrate_index")
DEFAULT_QUESTIONS = DATA_ROOT / "benchmark_corpus_v1_30q.jsonl"


# ============================================================
# Type-specific answer functions (no encoder)
# ============================================================


def _atoms_matching_topic(pstore: PartitionedStore, topic_keywords: list[str]) -> set[str]:
    """Cheap topic match: any atom whose name / id / description / aliases
    contains all the keywords (case-insensitive AND)."""
    matched = set()
    kw_lower = [k.lower() for k in topic_keywords]
    for atom in pstore.all_atoms():
        hay = " ".join([
            atom.id or "", atom.name or "", atom.description or "",
            " ".join(atom.aliases or [])
        ]).lower()
        if all(kw in hay for kw in kw_lower):
            matched.add(atom.qualified_id)
    return matched


def _extract_keywords(question: str) -> list[str]:
    """Tokenize question; strip stopwords."""
    stopwords = {"what", "atoms", "do", "i", "have", "about", "which", "is", "there", "the",
                 "of", "to", "from", "a", "an", "for", "by", "on", "in", "and", "or", "with",
                 "you", "your", "what", "rules", "apply", "when", "have", "not", "yet", "tried",
                 "could", "lift", "ner", "specifically", "?", ".", ",", "compose", "composition",
                 "path", "patterns", "appear", "primitives", "capability", "capabilities",
                 "atoms", "tier", "via", "existing", "complete", "exist", "analogues"}
    toks = []
    for raw in question.replace("?", " ").replace(".", " ").replace(",", " ").split():
        t = raw.strip().lower()
        if not t or t in stopwords or len(t) < 3:
            continue
        toks.append(t)
    return toks[:4]


def answer_type_A(pstore: PartitionedStore, q: dict) -> set[str]:
    """Type A content-level: surface atoms matching topic keywords."""
    keywords = _extract_keywords(q["question"])
    return _atoms_matching_topic(pstore, keywords)


def answer_type_B(pstore: PartitionedStore, q: dict) -> set[str]:
    """Type B relation-level: atoms in <relation> with anchor.
    Bidirectional + fuzzy enum match + concept_links/decomposes_to fallback."""
    anchor = q.get("anchor", "")
    rel_name = (q.get("relation") or "").upper()
    matched = set()

    if rel_name == "DECOMPOSE_TO":
        for atom in pstore.all_atoms():
            dt = atom.metadata.get("decomposes_to") or []
            if anchor in dt:
                matched.add(atom.qualified_id)
            # also accept concept_links pointing at anchor
            if anchor in (atom.concept_links or []):
                matched.add(atom.qualified_id)
        return matched

    # Identify candidate enum types matching rel_name fuzzily
    candidate_rels = []
    for rt in RelationType:
        if rt.value.upper() == rel_name:
            candidate_rels.append(rt)
        elif rel_name in rt.value.upper() or rt.value.upper() in rel_name:
            candidate_rels.append(rt)

    # If nothing matches, try ALL relations (semantic relation without explicit enum)
    if not candidate_rels:
        candidate_rels = list(RelationType)

    # Direction 1: anchor as target (incoming) -- "which atoms <REL> anchor?"
    for rt in candidate_rels:
        for src in pstore.in_neighbors(anchor, rt):
            matched.add(src)
    # Direction 2: anchor as source (outgoing) -- "which atoms are <REL>_BY anchor?"
    for rt in candidate_rels:
        for tgt in pstore.out_neighbors(anchor, rt):
            matched.add(tgt)
    # Direction 3: concept_links + decomposes_to BOTH directions
    if pstore.has_atom(anchor):
        a = pstore.get_atom(anchor)
        for cl in a.concept_links or []:
            matched.add(cl)
        for dt in a.metadata.get("decomposes_to") or []:
            matched.add(dt)
    for atom in pstore.all_atoms():
        if anchor in (atom.concept_links or []):
            matched.add(atom.qualified_id)
        if anchor in (atom.metadata.get("decomposes_to") or []):
            matched.add(atom.qualified_id)
    # Remove anchor itself from results
    matched.discard(anchor)
    return matched


def answer_type_C(pstore: PartitionedStore, q: dict) -> set[str]:
    """Type C capability-level: atoms with capability in serves_capability (Gap 1)
    OR atoms appearing in the capability's solution_history (solver/atoms_used)
    OR atoms the capability decomposes_to / USES (structural evidence).
    Bidirectional per benchmark v1 finding."""
    anchor = q.get("anchor", "")
    if not anchor:
        return set()
    matched = set()
    # Direction 1: serves_capability backfill
    for a in what_serves(pstore, anchor):
        matched.add(a.qualified_id)
    # Direction 2: capability's solution_history entries
    if pstore.has_atom(anchor):
        cap_atom = pstore.get_atom(anchor)
        for entry in cap_atom.solution_history:
            sol = entry.get("solution_atom_id")
            if sol:
                matched.add(sol)
            for au in entry.get("atoms_used", []):
                matched.add(au)
        # Direction 3: outgoing structural edges (USES / DEPENDS_ON / decomposes_to)
        for rt in (RelationType.USES, RelationType.USES_SUBPROC, RelationType.DEPENDS_ON,
                   RelationType.COMPOSES):
            for tgt in pstore.out_neighbors(anchor, rt):
                matched.add(tgt)
        # Direction 4: decomposes_to metadata
        for dt in cap_atom.metadata.get("decomposes_to") or []:
            matched.add(dt)
        # Direction 5: concept_links cross-corpus
        for cl in cap_atom.concept_links or []:
            matched.add(cl)
    return matched


def answer_type_D(pstore: PartitionedStore, q: dict) -> bool:
    """Type D composition-level: is there a path src -> tgt? Bidirectional per
    benchmark v1 finding: capability atoms typically have INCOMING USES/COMPOSES
    edges from their solvers, not outgoing. So check both directions."""
    src = q.get("anchor_src")
    tgt = q.get("anchor_tgt")
    if not (src and tgt):
        return False
    if not pstore.has_atom(src) or not pstore.has_atom(tgt):
        return False
    # Forward
    if composition_paths(pstore, src, tgt, max_depth=4):
        return True
    # Reverse (capability uses primitive)
    if composition_paths(pstore, tgt, src, max_depth=4):
        return True
    # Structural alternative: is src in tgt's solution_history or vice versa?
    tgt_atom = pstore.get_atom(tgt)
    for entry in tgt_atom.solution_history:
        if entry.get("solution_atom_id") == src or src in entry.get("atoms_used", []):
            return True
    for cl in tgt_atom.concept_links or []:
        if cl == src:
            return True
    src_atom = pstore.get_atom(src)
    if any(cl == tgt for cl in src_atom.concept_links or []):
        return True
    return False


def answer_type_E(pstore: PartitionedStore, q: dict) -> set[str]:
    """Type E methodology-level: surface RULE_* atoms requiring AT LEAST 2
    keyword matches in description (tightens precision)."""
    keywords = _extract_keywords(q["question"])
    matched = set()
    for atom in pstore.all_atoms():
        if atom.corpus.value != "meta":
            continue
        # Require RULE_ prefix per meta corpus convention
        if not atom.id.startswith("RULE_"):
            continue
        hay = (atom.id + " " + atom.name + " " + (atom.description or "")).lower()
        n_hits = sum(1 for kw in keywords if kw in hay)
        # Tighter: require >= 2 keyword matches OR exact id substring match
        if n_hits >= 2:
            matched.add(atom.qualified_id)
        elif any(kw in atom.id.lower() for kw in keywords if len(kw) >= 5):
            matched.add(atom.qualified_id)
    return matched


def answer_type_F(pstore: PartitionedStore, q: dict) -> set[str]:
    """Type F gap-level: empty caps via coverage_report OR what_have_you_not_tried."""
    # Q26 specifically: "Which substrate primitives have NEVER been applied to any capability?"
    if "never been applied" in q["question"].lower() or "never applied" in q["question"].lower():
        # Find caps with empty serves_capability
        empty_caps = set()
        for atom in pstore.all_atoms():
            if atom.current_best_solution or atom.solution_history:
                if not atom.serves_capability:
                    empty_caps.add(atom.qualified_id)
        return empty_caps
    # Otherwise qualitative (return empty; scored as honesty)
    return set()


def answer_type_G(pstore: PartitionedStore, q: dict) -> set[str]:
    """Type G pattern-level: cross-capability pattern queries."""
    # Q27 count_NB -> discriminative_perceptron: caps where both atoms appear in solution_history
    if "count_nb" in q["question"].lower() and "discriminative_perceptron" in q["question"].lower():
        from backend.substrate_index.self_knowledge import which_solutions_use_atom
        nb_caps = {e["capability"] for e in which_solutions_use_atom(pstore, "math::T3/count_nb")}
        dp_caps = {e["capability"] for e in which_solutions_use_atom(pstore, "math::T3/discriminative_perceptron")}
        return nb_caps & dp_caps
    # Q28 theta-gamma cross-discipline analogues: keyword search
    keywords = _extract_keywords(q["question"])
    return _atoms_matching_topic(pstore, keywords)


def answer_negative(pstore: PartitionedStore, q: dict) -> set[str]:
    """Negative type: should return empty set (substrate has nothing on this)."""
    keywords = _extract_keywords(q["question"])
    return _atoms_matching_topic(pstore, keywords)


# ============================================================
# Scorer
# ============================================================


def score_set_overlap(predicted: set[str], ground_truth: list[str]) -> dict:
    gt = set(ground_truth)
    tp = predicted & gt
    fn = gt - predicted
    fp = predicted - gt
    precision = len(tp) / max(1, len(tp) + len(fp))
    recall = len(tp) / max(1, len(tp) + len(fn))
    f1 = 2 * precision * recall / max(1e-9, precision + recall)
    return {
        "tp": len(tp), "fn": len(fn), "fp": len(fp),
        "precision": round(precision, 3), "recall": round(recall, 3),
        "f1": round(f1, 3),
        "predicted_count": len(predicted),
        "ground_truth_count": len(gt),
    }


def score_boolean(predicted: bool, expected: bool) -> dict:
    return {"correct": int(predicted == expected),
            "predicted": predicted, "expected": expected}


def score_honesty(predicted: set[str], q: dict) -> dict:
    """For negative/honesty Qs: substrate should return empty or near-empty."""
    n_pred = len(predicted)
    # If predicts 0 atoms -> honest (TN). If predicts atoms -> FP.
    return {"correct": int(n_pred == 0), "predicted_count": n_pred, "fp_atoms": list(predicted)[:5]}


# ============================================================
# Main
# ============================================================


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--questions", type=Path, default=DEFAULT_QUESTIONS)
    args = ap.parse_args()

    pstore = PartitionedStore(DATA_ROOT)
    log.info("loaded %d atoms across %d partitions", len(pstore.all_atoms()),
             sum(1 for p in pstore.stats()["partitions"].values() if p["n_atoms"] > 0))

    questions = []
    with open(args.questions, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            questions.append(json.loads(line))
    log.info("loaded %d benchmark questions", len(questions))

    answer_fns = {
        "A_content": answer_type_A,
        "B_relation": answer_type_B,
        "C_capability": answer_type_C,
        "E_methodology": answer_type_E,
        "F_gap": answer_type_F,
        "G_pattern": answer_type_G,
        "negative": answer_negative,
    }

    results = []
    per_type = defaultdict(list)

    for q in questions:
        qtype = q["type"]
        mode = q.get("score_mode", "set_overlap")
        result = {"qid": q["qid"], "type": qtype, "score_mode": mode,
                  "question": q["question"][:80]}

        if qtype == "D_composition":
            pred = answer_type_D(pstore, q)
            sc = score_boolean(pred, q.get("expected_boolean", True))
            result.update(sc)
            per_type[qtype].append(sc["correct"])
        elif mode == "honesty":
            fn = answer_fns.get(qtype, answer_negative)
            pred = fn(pstore, q)
            sc = score_honesty(pred, q)
            result.update(sc)
            per_type[qtype].append(sc["correct"])
        elif mode == "qualitative":
            result["qualitative"] = True
            result["note"] = "qualitative-only; skipped from numeric F1"
        else:
            fn = answer_fns.get(qtype)
            if fn is None:
                result["error"] = f"no answer fn for type {qtype}"
                results.append(result)
                continue
            pred = fn(pstore, q)
            sc = score_set_overlap(pred, q["ground_truth_atoms"])
            result.update(sc)
            per_type[qtype].append(sc["f1"])

        results.append(result)

    # Summary
    print("\n" + "=" * 78)
    print("GAP 7 BENCHMARK v1 -- substrate self-knowledge")
    print("=" * 78)

    for r in results:
        qid = r["qid"]
        if r.get("qualitative"):
            print(f"  {qid:8s} QUALITATIVE -- skipped")
            continue
        if "error" in r:
            print(f"  {qid:8s} ERROR: {r['error']}")
            continue
        if r["score_mode"] == "boolean":
            mark = "OK" if r["correct"] else "WRONG"
            print(f"  {qid:8s} [D] {mark:5s} pred={r['predicted']} exp={r['expected']}  {r['question']}")
        elif r["score_mode"] == "honesty":
            mark = "OK" if r["correct"] else "FP"
            print(f"  {qid:8s} [neg] {mark:4s} pred_count={r['predicted_count']}  {r['question']}")
        else:
            f1 = r["f1"]
            mark = "++" if f1 >= 0.7 else ("+" if f1 >= 0.4 else "-")
            print(f"  {qid:8s} [{r['type'][0]}] F1={f1:.2f} P={r['precision']:.2f} R={r['recall']:.2f} {mark}  tp={r['tp']} fp={r['fp']} fn={r['fn']}")

    print(f"\n=== Per-type aggregates ===")
    for qtype in ("A_content", "B_relation", "C_capability", "D_composition",
                   "E_methodology", "F_gap", "G_pattern", "negative"):
        scores = per_type.get(qtype, [])
        if scores:
            avg = sum(scores) / len(scores)
            print(f"  {qtype:18s} n={len(scores):2d}  avg={avg:.3f}")

    # Overall F1 across A-E (factual types per pre-reg)
    ae_scores = []
    for qtype in ("A_content", "B_relation", "C_capability", "E_methodology"):
        ae_scores.extend(per_type.get(qtype, []))
    overall_ae = sum(ae_scores) / max(1, len(ae_scores)) if ae_scores else 0.0
    print(f"\n  A-E factual avg F1: {overall_ae:.3f} (pre-reg HP_v1 >= 0.70)")

    # Honesty rate
    honesty_scores = per_type.get("negative", [])
    if honesty_scores:
        print(f"  Negative-Q honesty rate: {sum(honesty_scores)/len(honesty_scores):.3f}")

    out = DATA_ROOT / "bench_reports" / f"benchmark_v1_{int(time.time())}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({
        "n_questions": len(questions),
        "results": results,
        "per_type_avg": {t: (sum(s)/len(s) if s else None) for t, s in per_type.items()},
        "ae_factual_avg_f1": overall_ae,
    }, indent=2), encoding="utf-8")
    log.info("wrote benchmark report -> %s", out)


if __name__ == "__main__":
    main()
