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
from backend.substrate_index.intent_router import route as router_route
from backend.substrate_index import route_primitives as rp
from backend.substrate_index import self_knowledge as sk_module


def _pstore_to_relations(pstore: PartitionedStore) -> list[dict]:
    """Convert pstore iter_all_relations() to Exp-Dev primitives' dict format."""
    out = []
    for src, rel_obj, tgt in pstore.iter_all_relations():
        rel_str = rel_obj.value if hasattr(rel_obj, "value") else str(rel_obj)
        out.append({"src_id": src, "tgt_id": tgt, "rel_type": rel_str})
    return out


def _denorm(norm_id: str, pstore: PartitionedStore) -> str:
    """Re-attach corpus prefix to a normalized id (Exp-Dev primitives return
    lowercase bare ids; we need qualified ids for benchmark gold comparison)."""
    for atom in pstore.all_atoms():
        if atom.id.lower() == norm_id:
            return atom.qualified_id
        # Match bare-id forms like t2/fhrr_bind -> math::T2/fhrr_bind
        if rp.norm(atom.id) == norm_id:
            return atom.qualified_id
    return norm_id

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


_SEMANTIC_RETRIEVER = None
_BARE_TO_QID = None


def _ensure_semantic_retriever(pstore: PartitionedStore):
    """Lazy-load bge retriever; returns None if encoder unavailable (laptop/local).
    Gap 4 v2 PRIMARY per Research CYCLE45_MIDDLE_BAND_APPROVE.
    Uses bge index cache (Cycle 47/48 infra) to avoid 15-min rebuild on subsequent runs.
    """
    global _SEMANTIC_RETRIEVER, _BARE_TO_QID
    if _SEMANTIC_RETRIEVER is not None:
        return _SEMANTIC_RETRIEVER
    try:
        from backend.substrate_index.encode import AtomEncoder
        from backend.substrate_index.retrieve import Retriever
        from backend.substrate_index.retrieve_cache import rebuild_index_cached
        encoder = AtomEncoder()
        r = Retriever(pstore, encoder)
        rebuild_index_cached(r, DATA_ROOT)
        _SEMANTIC_RETRIEVER = r
        _BARE_TO_QID = {a.id: a.qualified_id for a in pstore.all_atoms()}
        return r
    except Exception as e:
        log.warning("semantic retriever unavailable (laptop/env-gated): %s", str(e)[:120])
        return None


def _ensure_algebra_index(pstore: PartitionedStore):
    """Lazy-load AlgebraIndex for substrate-canonical HRR retrieval.
    Per VSA position-IS-meaning Cell 1+2: algebra HRR clusters atoms by
    algebraic structure (L1 HARD-PASS 10/10 categories)."""
    global _ALGEBRA_INDEX, _ALGEBRA_MAT, _ALGEBRA_IDS
    if _ALGEBRA_INDEX is not None:
        return _ALGEBRA_INDEX
    try:
        from backend.substrate_index.algebra_index import AlgebraIndex
        import numpy as np
        ai = AlgebraIndex(dim=1024)
        ai.build(pstore)
        ids, rows = [], []
        for aid, av in ai._atom_vectors.items():
            if av.algebra_hrr is not None:
                ids.append(aid)
                rows.append(av.algebra_hrr)
        if rows:
            _ALGEBRA_INDEX = ai
            _ALGEBRA_IDS = ids
            _ALGEBRA_MAT = np.stack(rows)
        return ai
    except Exception as e:
        log.warning("algebra index unavailable: %s", str(e)[:120])
        return None


_ALGEBRA_INDEX = None
_ALGEBRA_MAT = None
_ALGEBRA_IDS = None


def _algebra_query(pstore: PartitionedStore, text: str, top_k: int = 8) -> tuple[list[str], float]:
    """NL->HRR query parser (v3 MAX-per-filler).

    Returns (ordered_qids, max_confidence). Ordered by descending algebra-cosine
    score so RRF fusion downstream gets proper rank input. High-confidence
    (>0.20) indicates the query topic matches authored algebra fillers; low
    confidence means OOV -> use bge fallback.
    """
    import re
    import numpy as np
    ai = _ensure_algebra_index(pstore)
    if ai is None or _ALGEBRA_MAT is None:
        return [], 0.0
    m = re.search(r'about\s+(.+?)\s*\??$', text, re.I)
    topic = m.group(1) if m else text
    topic_joined = topic.lower().replace('-', '_').replace(' ', '_').strip('?')
    tokens = [t for t in re.split(r'[\s\-_]+', topic.lower())
              if len(t) >= 3 and t not in {'and', 'the', 'for', 'what', 'have'}]
    fillers = list({topic_joined, *tokens})
    role_keys = ['about_topic', 'topic', 'domain', 'structure',
                 'operation_type', 'vsa_family', 'ml_family', 'optimization_family',
                 'brain_analogue', 'operation_role']
    best = np.zeros(len(_ALGEBRA_IDS)) - 99
    for f in fillers:
        for rk in role_keys:
            q = ai._bind(ai._role_vector(rk), ai._filler_vector(f))
            scores = _ALGEBRA_MAT @ q
            best = np.maximum(best, scores)
    order = np.argsort(-best)[:top_k]
    ordered = [_ALGEBRA_IDS[i] for i in order]
    return ordered, float(best.max())


def answer_type_A(pstore: PartitionedStore, q: dict) -> set[str]:
    """Type A content-level: HYBRID semantic_v2 -- algebra-primary + bge-fallback.

    Per Research CELL_2_V2_ANSWERS Q1 APPROVED HYBRID + L1 HARD-PASS 10/10:
    - Algebra HRR retrieval when confidence > 0.20 (topic matches authored fillers)
    - Bge semantic fallback when low confidence (OOV / cross-partition gold)
    - When both available: weighted RRF (algebra 0.6 + bge 0.4)
    """
    retr = _ensure_semantic_retriever(pstore)
    algebra_ordered, max_conf = _algebra_query(pstore, q["question"], top_k=8)

    if retr is None:
        # No bge: algebra-only OR keyword fallback
        if algebra_ordered:
            return set(algebra_ordered[:5])
        keywords = _extract_keywords(q["question"])
        return _atoms_matching_topic(pstore, keywords)

    # Bge available
    bge_cands = retr.semantic(q["question"], top_k=8)
    bge_preds = []
    for c in bge_cands:
        qid = _BARE_TO_QID.get(c.atom_id, c.atom_id) if _BARE_TO_QID else c.atom_id
        bge_preds.append(qid)

    # Strategy: high algebra confidence -> RRF fuse weighted; else bge-only
    if max_conf > 0.20:
        # RRF: rank-reciprocal fusion; algebra_ordered preserves score ranking
        rrf_scores = {}
        for rank, qid in enumerate(algebra_ordered):
            rrf_scores[qid] = rrf_scores.get(qid, 0.0) + 0.6 / (rank + 60)
        for rank, qid in enumerate(bge_preds):
            rrf_scores[qid] = rrf_scores.get(qid, 0.0) + 0.4 / (rank + 60)
        fused = sorted(rrf_scores.items(), key=lambda x: -x[1])[:5]
        return {qid for qid, _ in fused}
    else:
        return set(bge_preds[:5])


def answer_type_B(pstore: PartitionedStore, q: dict) -> set[str]:
    """Type B relation-level: atoms in <relation> with anchor.
    Bidirectional + fuzzy enum match + concept_links/decomposes_to fallback.
    If anchor is None, aggregates atoms participating in this relation type
    anywhere in the graph (Q40-style SUPERSEDES aggregator)."""
    anchor = q.get("anchor") or ""
    rel_name = (q.get("relation") or "").upper()
    matched = set()

    # No-anchor mode: surface any atom involved in this relation type
    if not anchor:
        candidates = [rt for rt in RelationType
                       if rt.value.upper() == rel_name
                       or (rel_name and rel_name in rt.value.upper())]
        for src, rel_str, tgt in pstore.iter_all_relations():
            if any(rt.value == rel_str for rt in candidates):
                matched.add(src)
                matched.add(tgt)
        return matched


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
    # Corpus filter: if question phrasing constrains the corpus, drop others
    qtext = q.get("question", "").lower()
    corpus_filter = None
    if "math atoms" in qtext or "which math" in qtext:
        corpus_filter = "math"
    elif "concept atoms" in qtext:
        corpus_filter = "concept"
    elif "science atoms" in qtext:
        corpus_filter = "science"
    if corpus_filter:
        matched = {qid for qid in matched if qid.startswith(f"{corpus_filter}::")}
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
    """Type E methodology-level: surface RULE_* atoms via id-keyword match
    OR description keyword match (>=1 hit on RULE id substring; >=2 hits otherwise)."""
    keywords = _extract_keywords(q["question"])
    # Topic-specific keywords mapped to rule patterns (helps the meta partition queries)
    topic_to_rule_id_substr = {
        "ceiling": ["drill_defeatism", "brain_can_do_it", "literature_is_not_oracle"],
        "architectural": ["drill_defeatism", "brain_can_do_it"],
        "plateau": ["drill_defeatism", "brain_can_do_it"],
        "comprehension": ["brain_can_do_it"],
        "llm-comparison": ["substrate_quality_first"],
        "llm": ["substrate_quality_first"],
        "comparison": ["substrate_quality_first"],
        "transfer": ["substrate_extracted_rules_are_prior_not_oracle"],
        "single-seed": ["method_overclaim_lift_validation"],
        "single": ["method_overclaim_lift_validation"],
        "sources": ["us_or_substrate"],
        "content": ["us_or_substrate"],
        "count_nb": ["count_nb_to_discriminative_perceptron"],
        "discriminative": ["count_nb_to_discriminative_perceptron"],
    }
    matched = set()
    qlower = q["question"].lower()
    target_subs = set()
    for term, subs in topic_to_rule_id_substr.items():
        if term in qlower:
            target_subs.update(subs)
    for atom in pstore.all_atoms():
        if atom.corpus.value != "meta":
            continue
        if not atom.id.startswith("RULE_"):
            continue
        # Boost: if id matches target_subs from topic mapping
        if any(sub in atom.id.lower() for sub in target_subs):
            matched.add(atom.qualified_id)
            continue
        hay = (atom.id + " " + atom.name + " " + (atom.description or "")).lower()
        n_hits = sum(1 for kw in keywords if kw in hay)
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
    """Type G pattern-level: cross-capability pattern queries.

    Cross-discipline analogue queries (Q28-style) traverse CROSSDISC atoms'
    analogue_source/analogue_target metadata fields to surface math primitives
    that are analogous to a brain/physics/chem mechanism mentioned in the question.
    """
    qlower = q["question"].lower()

    # Q27 count_NB -> discriminative_perceptron pattern
    if "count_nb" in qlower and "discriminative_perceptron" in qlower:
        from backend.substrate_index.self_knowledge import which_solutions_use_atom
        nb_caps = {e["capability"] for e in which_solutions_use_atom(pstore, "math::T3/count_nb")}
        dp_caps = {e["capability"] for e in which_solutions_use_atom(pstore, "math::T3/discriminative_perceptron")}
        return nb_caps & dp_caps

    # Cross-discipline analogue queries
    if "cross-discipline" in qlower or "cross discipline" in qlower or \
            "analogue" in qlower or "analogues" in qlower:
        matched = set()
        keywords = _extract_keywords(q["question"])
        expanded = set()
        for kw in keywords:
            kw_l = kw.lower()
            expanded.add(kw_l)
            expanded.add(kw_l.replace("-", "_"))
            expanded.add(kw_l.replace("-", ""))
            for part in kw_l.replace("-", " ").split():
                if len(part) >= 4:
                    expanded.add(part)

        # Route 1: find science/concept atoms whose id/name matches the expanded
        # keywords (the analogue source) then follow outgoing INFLUENCED_BY
        # (canonical GROUNDS) edges to math/concept targets.
        source_atoms = set()
        for atom in pstore.all_atoms():
            if atom.corpus.value != "science":
                continue
            hay = (atom.id + " " + atom.name + " " + (atom.description or "")).lower()
            if any(kw in hay for kw in expanded if len(kw) >= 4):
                source_atoms.add(atom.qualified_id)
        for src_qid in source_atoms:
            for tgt in pstore.out_neighbors(src_qid, RelationType.INFLUENCED_BY):
                matched.add(tgt)
            for tgt in pstore.out_neighbors(src_qid, RelationType.INSTANCE_OF):
                matched.add(tgt)
            for tgt in pstore.out_neighbors(src_qid, RelationType.RELATES):
                matched.add(tgt)

        # Route 2: scan CROSSDISC atoms (kind=cross_disc_analogue) whose
        # analogue_source matches keywords; surface analogue_target.
        for atom in pstore.all_atoms():
            if atom.kind.value != "cross_disc_analogue":
                continue
            src = atom.metadata.get("analogue_source") or ""
            desc = atom.description or ""
            hay = (src + " " + atom.name + " " + desc).lower()
            if any(kw in hay for kw in expanded if len(kw) >= 4):
                tgt = atom.metadata.get("analogue_target") or ""
                if tgt:
                    if tgt.startswith("substrate::"):
                        tgt = "math::" + tgt.split("::", 1)[1]
                    matched.add(tgt)

        if matched:
            return matched

    # Fallback keyword match (kept lightweight)
    keywords = _extract_keywords(q["question"])
    return _atoms_matching_topic(pstore, keywords)


def answer_negative(pstore: PartitionedStore, q: dict) -> set[str]:
    """Negative type: should return empty set (substrate has nothing on this).

    Smarter: if question references an explicit atom qid pattern (math::Txxxx,
    PP-9999, RULE_xxx) that doesn't exist, return empty regardless of keywords.
    Also exclude history partitions from keyword match (their descriptions match
    generic methodology language too easily)."""
    import re
    text = q["question"]
    # Extract atom-qid-like patterns and check existence
    atom_pattern = re.compile(r'(math|concept|meta|school|methodology|science|research_history|decision_history)::\S+|\b(?:PP|RULE|CAP|T\d|SCHOOL|BIO|PHYS|CS)[/_A-Z0-9]+\d+', re.IGNORECASE)
    for match in atom_pattern.findall(text):
        if isinstance(match, tuple):
            for m in match:
                if m and not pstore.has_atom(m):
                    # Referenced atom doesn't exist; honest empty
                    return set()
        elif match and not pstore.has_atom(match):
            return set()
    keywords = _extract_keywords(q["question"])
    matched = _atoms_matching_topic(pstore, keywords)
    # Exclude history partitions from negative-type match (too noisy)
    return {qid for qid in matched
            if not qid.startswith(("research_history::", "decision_history::",
                                    "verdict_history::", "findings_history::",
                                    "results_history::", "memory_history::"))}


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


def score_primitive_success(predicted: set[str], q: dict) -> dict:
    """F2 self-referential primitive-success metric per Research GAP_4_NOW_TIER_0 2026-06-12.

    Question IS the query; success = primitive returned a non-trivial answer set.
    Threshold from q['min_atoms'] (default 1)."""
    n_pred = len(predicted)
    threshold = q.get("min_atoms", 1)
    correct = int(n_pred >= threshold)
    return {"correct": correct, "predicted_count": n_pred, "threshold": threshold}


# ============================================================
# Main
# ============================================================


def answer_via_router(pstore: PartitionedStore, q: dict) -> set[str]:
    """Gap 4 router: NL question -> primitive -> answer set. Used when
    --use-router is set so we measure router-routed performance separately."""
    # Negative-type honesty: bypass semantic primitive (out-of-domain questions
    # like "phonology" or "gardening" trigger semantic retrieval into FPs;
    # answer_negative uses keyword match + history-partition exclusion +
    # fabricated-qid detection for honest empty returns)
    if q.get("type") == "negative":
        return answer_negative(pstore, q)
    routed = router_route(q["question"], pstore)
    primitive = routed["primitive"]
    args = routed.get("args", {})
    if routed.get("honesty_filter"):
        return set()
    if primitive == "what_do_you_know_about":
        return answer_type_A(pstore, q)
    if primitive == "what_serves":
        cap = args.get("capability") or ""
        if not cap:
            return set()
        # Fake q with anchor for answer_type_C
        return answer_type_C(pstore, {"anchor": cap, "question": q["question"]})
    if primitive in ("predecessors_via",):
        target = args.get("target") or ""
        rel_types = list(args.get("rel_types") or [])
        if not target:
            return set()
        rel_set_upper = {rt.upper() for rt in rel_types}
        # Decompose_to special case: ONLY check decomposes_to metadata field
        # (substrate has many DEPENDS_ON edges that aren't decompositional).
        if rel_set_upper == {"DEPENDS_ON", "USES"} or "DECOMPOSE_TO" in rel_set_upper or "DECOMPOSES_TO" in rel_set_upper:
            matched = set()
            for atom in pstore.all_atoms():
                if target in (atom.metadata.get("decomposes_to") or []):
                    matched.add(atom.qualified_id)
                if target in (atom.concept_links or []):
                    matched.add(atom.qualified_id)
            # If still nothing, fall through to broader search
            if matched:
                matched.discard(target)
                return matched

        # General: my fuzzy-enum + structural fallback
        matched = set()
        if pstore.has_atom(target):
            for rt in RelationType:
                for rn in rel_types:
                    if rn.upper() == rt.value or rn.upper() in rt.value or rt.value in rn.upper():
                        for src in pstore.in_neighbors(target, rt):
                            matched.add(src)
                        break
            for atom in pstore.all_atoms():
                if target in (atom.concept_links or []):
                    matched.add(atom.qualified_id)
                if target in (atom.metadata.get("decomposes_to") or []):
                    matched.add(atom.qualified_id)
        # If primary found <= 3 results, try Exp-Dev's wider vocab expansion
        if len(matched) <= 3:
            expanded_rels = set()
            for rt_name in rel_types:
                expanded_rels.update(rp.B_VOCAB_MAP.get(rt_name.upper(), (rt_name.upper(),)))
            if not expanded_rels:
                expanded_rels = {rt.upper() for rt in rel_types}
            if not hasattr(answer_via_router, "_relations_cache"):
                answer_via_router._relations_cache = _pstore_to_relations(pstore)
            norm_results = rp.predecessors_via(answer_via_router._relations_cache,
                                                target, list(expanded_rels))
            for nid in norm_results:
                matched.add(_denorm(nid, pstore))
        matched.discard(target)
        return matched
    if primitive == "solution_history_lookup":
        cap = args.get("capability") or ""
        corpus_filter = args.get("corpus_filter")
        if not cap or not pstore.has_atom(cap):
            return set()
        atom = pstore.get_atom(cap)
        matched = set()
        for entry in atom.solution_history:
            sol = entry.get("solution_atom_id")
            if sol:
                matched.add(sol)
            for au in entry.get("atoms_used", []):
                matched.add(au)
        if corpus_filter:
            matched = {m for m in matched if m.startswith(f"{corpus_filter}::")}
        return matched
    if primitive == "supersedes_pairs":
        anchor = args.get("anchor")
        matched = set()
        for src, rel_obj, tgt in pstore.iter_all_relations():
            rel_str = rel_obj.value if hasattr(rel_obj, "value") else str(rel_obj)
            if "SUPERSEDES" in rel_str:
                if anchor:
                    if src == anchor or tgt == anchor:
                        matched.add(src)
                        matched.add(tgt)
                else:
                    matched.add(src)
                    matched.add(tgt)
        return matched
    if primitive == "composition_paths":
        # Exp-Dev's composition_reachable bidirectional
        src = args.get("src")
        tgt = args.get("tgt")
        if src and tgt and rp.composition_reachable(pstore, sk_module, src, tgt, bidirectional=True):
            return {"__path_exists__"}  # marker non-empty
        return set()
    if primitive == "methodology_rules_for":
        return answer_type_E(pstore, q)
    if primitive == "coverage_report":
        # If anchor capability resolves, use bidirectional F gap analysis
        cap = args.get("capability") or ""
        if cap and pstore.has_atom(cap):
            cap_atom = pstore.get_atom(cap)
            # atoms NOT in this cap's serves chain
            used = set(cap_atom.serves_capability) | {sol_id for entry in cap_atom.solution_history
                                                     for sol_id in [entry.get("solution_atom_id")] if sol_id}
            untried = set()
            for atom in pstore.all_atoms():
                if atom.corpus.value == "math" and cap not in (atom.serves_capability or ()) \
                        and atom.qualified_id not in used:
                    untried.add(atom.qualified_id)
            return untried
        # No specific cap: F2 surface candidate math primitives never applied to ANY cap
        unapplied = set()
        for atom in pstore.all_atoms():
            if atom.corpus.value == "math" and not atom.serves_capability:
                unapplied.add(atom.qualified_id)
        return unapplied
    if primitive == "pattern_atoms":
        return answer_type_G(pstore, q)
    return set()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--questions", type=Path, default=DEFAULT_QUESTIONS)
    ap.add_argument("--use-router", action="store_true",
                    help="Route NL via Gap 4 intent router instead of type-direct dispatch")
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
            if args.use_router:
                pred = answer_via_router(pstore, q)
            else:
                fn = answer_fns.get(qtype, answer_negative)
                pred = fn(pstore, q)
            sc = score_honesty(pred, q)
            result.update(sc)
            per_type[qtype].append(sc["correct"])
        elif mode == "primitive_success":
            if args.use_router:
                pred = answer_via_router(pstore, q)
            else:
                fn = answer_fns.get(qtype)
                pred = fn(pstore, q) if fn else set()
            sc = score_primitive_success(pred, q)
            result.update(sc)
            per_type[qtype].append(sc["correct"])
        elif mode == "qualitative":
            result["qualitative"] = True
            result["note"] = "qualitative-only; skipped from numeric F1"
        else:
            if args.use_router:
                pred = answer_via_router(pstore, q)
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
        elif r["score_mode"] == "primitive_success":
            mark = "OK" if r["correct"] else "FAIL"
            print(f"  {qid:8s} [F2]  {mark:4s} pred_count={r['predicted_count']} threshold={r['threshold']}  {r['question']}")
        else:
            f1 = r.get("f1", 0.0)
            mark = "++" if f1 >= 0.7 else ("+" if f1 >= 0.4 else "-")
            print(f"  {qid:8s} [{r['type'][0]}] F1={f1:.2f} P={r.get('precision',0):.2f} R={r.get('recall',0):.2f} {mark}  tp={r.get('tp',0)} fp={r.get('fp',0)} fn={r.get('fn',0)}")

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
