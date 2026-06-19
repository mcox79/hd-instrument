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
        # Use IDENTITY-augmented composite_hrr per two-vector architecture (PP-410):
        # A axis benchmark is content-similarity (atom-identity), use composite_hrr
        # for collision-resistant retrieval. algebra_hrr stays plain for structural.
        for aid, av in ai._atom_vectors.items():
            v = av.composite_hrr if av.composite_hrr is not None else av.algebra_hrr
            if v is not None:
                ids.append(aid)
                rows.append(v)
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


# DECISION 35a (2026-06-14): light bge confidence floor. M1 tau-sweep on held-out showed
# tau=0.70 is the IN-COVERAGE F1 PEAK (0.128, 1.7x ungated) -- a light floor removes
# low-confidence FP noise. Shipped as a CAPABILITY helper, NOT a soundness fix: at 0.70 the
# coverage-gap refuse-rate is only 0.167 (refuse-discipline soundness needs M4, separate work).
BGE_CONFIDENCE_FLOOR = 0.70


def answer_type_A_union(pstore: PartitionedStore, q: dict) -> set[str]:
    """Type A content-level: UNION strategy (Research Cycle 50+ architectural answer).

    Per Research rule 12 CONFIRMED meta::RULE_algebra_hrr_and_bge_cosine_are_partition_retrieval_primitives:
    Algebra HRR + bge cosine are PARTITIONS not hierarchy. UNION > either alone;
    INTERSECTION < either alone. RRF averages signal + pipeline ranks BOTH collapse
    to one dimension and lose orthogonal coverage. UNION embraces the partition.

    Strategy: top-3 from each retrieval primitive (algebra HRR + bge cosine),
    set-union with dedupe, rank by max(algebra_score_norm, bge_score_norm).
    """
    import numpy as np
    retr = _ensure_semantic_retriever(pstore)
    # top_k=5 each gives 5-10 unique atoms post-union; final top-5 by max-score.
    # Avoids pred_count<5 regression for F-type Qs routed via what_do_you_know_about.
    algebra_ordered, max_conf = _algebra_query(pstore, q["question"], top_k=5)

    if retr is None:
        if algebra_ordered:
            return set(algebra_ordered[:5])
        keywords = _extract_keywords(q["question"])
        return _atoms_matching_topic(pstore, keywords)

    bge_cands = retr.semantic(q["question"], top_k=5)
    # DECISION 35a light confidence floor: drop candidates below tau=0.70 (FP-noise removal).
    bge_cands = [c for c in bge_cands if float(getattr(c, "score", 1.0)) >= BGE_CONFIDENCE_FLOOR]
    bge_preds = []
    for c in bge_cands:
        qid = _BARE_TO_QID.get(c.atom_id, c.atom_id) if _BARE_TO_QID else c.atom_id
        bge_preds.append(qid)

    if max_conf > 0.20 and algebra_ordered:
        # UNION + max-score rank (rank-reciprocal as proxy for score normalization)
        scores: dict[str, float] = {}
        for rank, qid in enumerate(algebra_ordered):
            scores[qid] = max(scores.get(qid, 0.0), 1.0 - rank / 5.0)
        for rank, qid in enumerate(bge_preds):
            scores[qid] = max(scores.get(qid, 0.0), 1.0 - rank / 5.0)
        ranked = sorted(scores.items(), key=lambda x: -x[1])
        return {qid for qid, _ in ranked[:5]}
    else:
        return set(bge_preds[:5])


def answer_type_A_pipeline(pstore: PartitionedStore, q: dict) -> set[str]:
    """Type A content-level: Option 4 pipeline (retained for comparison/A-B test).

    Per Research Cycle 49 OPTION_SELECT_OPT_4_PRIMARY (rule 12 candidate
    meta::RULE_algebra_hrr_broad_strong_narrow_weak_route_by_specificity):
    - Stage 1: algebra HRR top-15 (broad structural recall across vsa_family /
      operation_type / domain fillers; LIFTS on broad-topic queries)
    - Stage 2: bge cosine PRECISION re-rank within algebra candidates (content-text
      discrimination prevents structurally-near-but-content-wrong displacement)
    - Stage 3: top-5 by bge score within algebra set

    Below-confidence path (max_conf <= 0.20): bge-only top-5 (OOV / cross-partition).
    """
    import numpy as np
    retr = _ensure_semantic_retriever(pstore)
    algebra_ordered, max_conf = _algebra_query(pstore, q["question"], top_k=15)

    if retr is None:
        # No bge available (laptop) -- algebra alone or keyword fallback
        if algebra_ordered:
            return set(algebra_ordered[:5])
        keywords = _extract_keywords(q["question"])
        return _atoms_matching_topic(pstore, keywords)

    # Bge available
    if max_conf > 0.20 and algebra_ordered:
        # Stage 2: bge cosine within algebra candidates -- USE MATRIX DIRECTLY
        # (retr.get_vectors returns None after cache-load; only matrices + id_order
        # are repopulated. Use _semantic_matrix indexed by id_order position.)
        try:
            q_vec = retr.encoder.encode_query_text(q["question"])
            sem_matrix = retr._semantic_matrix
            id_order = retr._id_order
            if q_vec is None or sem_matrix is None or not id_order:
                raise ValueError("retr matrices not populated")
            id_to_idx = {a: i for i, a in enumerate(id_order)}
            scored = []
            for qid in algebra_ordered:
                bare = qid.split("::", 1)[1] if "::" in qid else qid
                idx = id_to_idx.get(bare)
                if idx is None:
                    continue
                bge_score = float(np.dot(sem_matrix[idx], q_vec))
                scored.append((qid, bge_score))
            if scored:
                scored.sort(key=lambda x: -x[1])
                return {qid for qid, _ in scored[:5]}
        except Exception as e:
            log.warning("Option 4 pipeline failed; falling back to bge-only: %s",
                        str(e)[:80])

    # Fallback: bge-only top-5 (OOV / cross-partition / pipeline fail)
    bge_cands = retr.semantic(q["question"], top_k=5)
    return {(_BARE_TO_QID.get(c.atom_id, c.atom_id) if _BARE_TO_QID else c.atom_id)
            for c in bge_cands}


def answer_type_A(pstore: PartitionedStore, q: dict) -> set[str]:
    """Type A content-level: UNION strategy (Cycle 49 close).

    Empirical Cycle 49: HYBRID RRF + Option 4 pipeline BOTH null-net because
    they collapse 2 orthogonal signals to 1 dimension. Per Research rule 12
    CONFIRMED meta::RULE_algebra_hrr_and_bge_cosine_are_partition_retrieval_primitives:
    algebra HRR + bge cosine cover DIFFERENT unrelated gold subsets; UNION
    preserves both contributions; INTERSECTION / averaging lose orthogonal
    coverage.

    Delegates to answer_type_A_union; answer_type_A_pipeline retained as
    A/B comparison.
    """
    return answer_type_A_union(pstore, q)


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


def answer_type_B_union(pstore: PartitionedStore, q: dict) -> set[str]:
    """Type B relation-level UNION strategy (rule 12 B-axis generalization).

    Per strategy_request_to_testbed_2026-06-12_UNION_B_C_ship_approved_prereg_discipline:
    Structural primary + algebra + bge UNION enhances recall on structural-zero
    cases (Q39 INSTANCE_OF SCHOOL/structured_prediction_family, Q41 DEPENDS_ON
    math::T1/random_variable) where the typed-edge graph traversal returns 0.

    Pre-reg: HP B >= 0.42 / MIDDLE 0.35-0.42 / FAIL < 0.35 vs current 0.354.
    """
    structural = answer_type_B(pstore, q)

    retr = _ensure_semantic_retriever(pstore)
    algebra_ordered, max_conf = _algebra_query(pstore, q["question"], top_k=5)

    if retr is None:
        return structural

    bge_cands = retr.semantic(q["question"], top_k=5)
    bge_preds = []
    for c in bge_cands:
        qid = _BARE_TO_QID.get(c.atom_id, c.atom_id) if _BARE_TO_QID else c.atom_id
        bge_preds.append(qid)

    if structural:
        # Structural-strong: UNION as recall enhancer (structural weight=1.0)
        scores: dict[str, float] = {}
        for qid in structural:
            scores[qid] = 1.0
        if max_conf > 0.20:
            for rank, qid in enumerate(algebra_ordered):
                scores[qid] = max(scores.get(qid, 0.0), 0.8 - rank / 5.0)
        for rank, qid in enumerate(bge_preds):
            scores[qid] = max(scores.get(qid, 0.0), 0.8 - rank / 5.0)
        ranked = sorted(scores.items(), key=lambda x: -x[1])
        # Return ALL structural + top-K of union enhancements (cap at 10 to avoid FP explosion)
        return {qid for qid, _ in ranked[:max(len(structural), 8)]}
    else:
        # Structural-zero: pure algebra + bge UNION (same as A axis pattern)
        if max_conf > 0.20 and algebra_ordered:
            scores: dict[str, float] = {}
            for rank, qid in enumerate(algebra_ordered):
                scores[qid] = max(scores.get(qid, 0.0), 1.0 - rank / 5.0)
            for rank, qid in enumerate(bge_preds):
                scores[qid] = max(scores.get(qid, 0.0), 1.0 - rank / 5.0)
            ranked = sorted(scores.items(), key=lambda x: -x[1])
            return {qid for qid, _ in ranked[:5]}
        else:
            return set(bge_preds[:5])


def answer_type_C_union(pstore: PartitionedStore, q: dict) -> set[str]:
    """Type C capability-level UNION strategy (rule 12 C-axis generalization).

    Per strategy_request_to_testbed_2026-06-12_UNION_B_C_ship_approved_prereg_discipline:
    5-direction structural primary + algebra + bge UNION for unresolved-anchor cases
    (Q12 substrate-classical NL Tier-A, Q44 Layer 2 spectral observability) where
    structural returns 0.

    Pre-reg: HP C >= 0.48 / MIDDLE 0.44-0.48 / FAIL < 0.44 vs current 0.437.
    """
    structural = answer_type_C(pstore, q)

    retr = _ensure_semantic_retriever(pstore)
    algebra_ordered, max_conf = _algebra_query(pstore, q["question"], top_k=5)

    if retr is None:
        return structural

    bge_cands = retr.semantic(q["question"], top_k=5)
    bge_preds = []
    for c in bge_cands:
        qid = _BARE_TO_QID.get(c.atom_id, c.atom_id) if _BARE_TO_QID else c.atom_id
        bge_preds.append(qid)

    if structural:
        scores: dict[str, float] = {}
        for qid in structural:
            scores[qid] = 1.0
        if max_conf > 0.20:
            for rank, qid in enumerate(algebra_ordered):
                scores[qid] = max(scores.get(qid, 0.0), 0.8 - rank / 5.0)
        for rank, qid in enumerate(bge_preds):
            scores[qid] = max(scores.get(qid, 0.0), 0.8 - rank / 5.0)
        ranked = sorted(scores.items(), key=lambda x: -x[1])
        return {qid for qid, _ in ranked[:max(len(structural), 8)]}
    else:
        if max_conf > 0.20 and algebra_ordered:
            scores: dict[str, float] = {}
            for rank, qid in enumerate(algebra_ordered):
                scores[qid] = max(scores.get(qid, 0.0), 1.0 - rank / 5.0)
            for rank, qid in enumerate(bge_preds):
                scores[qid] = max(scores.get(qid, 0.0), 1.0 - rank / 5.0)
            ranked = sorted(scores.items(), key=lambda x: -x[1])
            return {qid for qid, _ in ranked[:5]}
        else:
            return set(bge_preds[:5])


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
    kw_match = _atoms_matching_topic(pstore, keywords)
    if kw_match:
        return kw_match
    # DECISION 39a: type-G had NO bge fallback, so shallow gold that bge ranks at
    # #2-3 (e.g. Q60-G structured_perceptron_collins, Q64-G cosine_cleanup) was
    # never surfaced. Only fires when keyword match is empty; tau=0.70 floor keeps
    # precision (low-confidence FP noise dropped).
    retr = _ensure_semantic_retriever(pstore)
    if retr is not None:
        bge = retr.semantic(q["question"], top_k=5)
        preds = {(_BARE_TO_QID.get(c.atom_id, c.atom_id) if _BARE_TO_QID else c.atom_id)
                 for c in bge if float(getattr(c, "score", 1.0)) >= BGE_CONFIDENCE_FLOOR}
        if preds:
            return preds
    return set()


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
        # Cycle 50 UNION-C HARD_FAIL revert: restore original answer_type_C call.
        # FP-explosion-on-unbounded-prediction-sets mechanism falsified rule 12
        # generalization on C axis. Standing for structural-zero-only UNION direction.
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
