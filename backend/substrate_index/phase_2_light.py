"""Phase-2-light substrate-guided proposal tool per Cycle 50 Research design.

5-component LLM-free pipeline that proposes atom additions to substrate based on:
- Component 1: lightweight noun-phrase extraction over text files
- Component 2: distant supervision seed from existing Tier-3 atom names + aliases
- Component 3: hybrid-encoder cluster-novelty filter (per cluster_density.py)
- Component 4: Z-counts curriculum-difficulty + sparse-neighborhood ranking
- Component 5: gap-driven iterative outer loop (proposal batch)

Pre-reg smoke test: 50-file Snowball bootstrap on research_history;
P@30 HARD-PASS >= 0.60 / MIDDLE 0.40-0.60 / HARD-FAIL <0.40.

Note: Phase-2-LIGHT uses lightweight extraction (regex + Title-Case heuristics)
for the smoke. Production / Phase-2-FULL upgrades Component 1 to substrate
Tier-A NL primitives (POS / chunking / dep-parse / NER) per Research design.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Iterable
from collections import defaultdict, Counter
import re

import numpy as np

from .partition import PartitionedStore
from .algebra_index import AlgebraIndex
from .cluster_density import (
    cluster_atom_counts,
    nearest_cluster_with_density,
    proposal_route,
)
from .sparse_neighborhood_ranking import (
    rank_candidates_sparse_first,
    CandidateRank,
)


@dataclass
class CandidateExtraction:
    canonical_name: str
    source_files: list[str] = field(default_factory=list)
    raw_mentions: list[str] = field(default_factory=list)
    z_count: int = 0


@dataclass
class ProposalRecord:
    candidate: CandidateExtraction
    distant_supervision_score: float
    similarity_to_existing_T3: list[tuple[str, float]]
    nearest_cluster: Optional[int]
    nearest_density: int
    novelty: float
    route: str
    rank_score: float
    algebra_additions_template: dict


# ============================================================
# Component 1: atom-gap extraction frontend (lightweight)
# ============================================================

# Multi-word noun-phrase patterns common in research drill files
NOUN_PHRASE_PATTERNS = [
    # TitleCase multi-word phrases (e.g., "Random Matrix Theory")
    re.compile(r"\b([A-Z][a-zA-Z0-9]+(?:\s+[A-Z][a-zA-Z0-9]+){1,4})\b"),
    # snake_case identifiers from code/algebra (e.g., "tracy_widom_distribution")
    re.compile(r"\b([a-z][a-z0-9]+(?:_[a-z0-9]+){1,4})\b"),
    # Hyphenated multi-word (e.g., "free-probability")
    re.compile(r"\b([a-zA-Z][a-zA-Z0-9]+(?:-[a-zA-Z0-9]+){1,3})\b"),
]

STOPWORDS = {
    "the", "and", "for", "with", "from", "into", "onto", "this", "that", "these",
    "those", "have", "has", "had", "are", "was", "were", "been", "being", "what",
    "which", "where", "when", "while", "would", "could", "should", "may", "can",
    "will", "must", "but", "not", "all", "any", "each", "more", "most", "some",
    "such", "than", "then", "thus", "also", "very", "many", "much", "even",
    "still", "only", "just", "first", "second", "third", "next", "last",
}


def extract_candidates_from_text(text: str, source_file: str) -> dict[str, list[str]]:
    """Extract noun-phrase candidates from text using lightweight patterns.

    Returns dict mapping canonical_form -> list of raw mention forms.
    """
    raw_mentions: list[str] = []
    for pattern in NOUN_PHRASE_PATTERNS:
        raw_mentions.extend(pattern.findall(text))

    by_canonical: dict[str, list[str]] = defaultdict(list)
    for raw in raw_mentions:
        canonical = canonicalize_candidate(raw)
        if not canonical or _is_skip(canonical):
            continue
        by_canonical[canonical].append(raw)
    return dict(by_canonical)


def canonicalize_candidate(raw: str) -> str:
    """Normalize a raw mention to a canonical form (lowercase + underscore separator)."""
    s = raw.strip().lower()
    s = re.sub(r"[-\s]+", "_", s)
    s = re.sub(r"[^a-z0-9_]", "", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return s


# Option A (Cycle 50 Research direction): tighten filters to characterize floor.
# Production Component 1 will wire substrate Tier-A NL primitives per original design.

PREFIX_JARGON = ("sub_", "lit_", "full_", "re_", "op_", "all_", "non_", "per_",
                  "anti_", "post_", "pre_", "in_", "co_")
SUFFIX_JARGON = ("_specific", "_only", "_lite", "_only_", "_friendly", "_etc",
                  "_pending", "_optional", "_yet", "_so")

def _looks_like_paper_id(canonical: str) -> bool:
    """Match paper DOI fragments like s41565_023_01357_8, arxiv_2304_12345 etc."""
    # Heuristic: tokens with mixed digits/letters where digit-tokens > 1
    tokens = canonical.split("_")
    digit_tokens = sum(1 for t in tokens if any(c.isdigit() for c in t))
    if digit_tokens >= 2:
        return True
    # Long all-alphanum starting with letter+digits like s41565 or arxiv2304
    for t in tokens:
        if len(t) >= 6 and t[0].isalpha() and sum(1 for c in t if c.isdigit()) >= 4:
            return True
    return False


def _is_skip(canonical: str) -> bool:
    """Skip if canonical form is too short, too long, or stopword-only.

    Option A tightening per Research direction:
    - Require 2+ tokens for snake_case multi-word candidates
    - Filter prefix-jargon (sub_, lit_, full_, re_, op_, all_, non_, etc.)
    - Filter suffix-jargon (_specific, _only, _lite, etc.)
    - Filter paper-ID-like patterns (s41565_023_01357_8)
    """
    if len(canonical) < 4 or len(canonical) > 80:
        return True
    tokens = canonical.split("_")
    if len(tokens) == 1 and tokens[0] in STOPWORDS:
        return True
    # Skip if ALL tokens are stopwords
    if all(t in STOPWORDS for t in tokens):
        return True
    # Skip pure-numeric strings
    if canonical.replace("_", "").isdigit():
        return True
    # Option A: require multi-token for multi-word candidates (single tokens are too noisy)
    if len(tokens) == 1:
        return True
    # Option A: filter prefix-jargon (research-meta words)
    if canonical.startswith(PREFIX_JARGON):
        return True
    # Option A: filter suffix-jargon
    if any(canonical.endswith(suf) for suf in SUFFIX_JARGON):
        return True
    # Option A: filter paper-ID-like patterns
    if _looks_like_paper_id(canonical):
        return True
    # Option A: stopword-leading multi-token (e.g., "all_atom", "any_X")
    if tokens[0] in STOPWORDS:
        return True
    return False


def extract_from_files(files: list[Path]) -> dict[str, CandidateExtraction]:
    """Run Component 1 over a list of files; aggregate per-canonical-form."""
    by_canonical: dict[str, CandidateExtraction] = {}
    for f in files:
        try:
            text = f.read_text(encoding="utf-8")
        except Exception:
            continue
        per_file = extract_candidates_from_text(text, str(f))
        for canonical, mentions in per_file.items():
            if canonical not in by_canonical:
                by_canonical[canonical] = CandidateExtraction(canonical_name=canonical)
            ce = by_canonical[canonical]
            ce.source_files.append(str(f.name))
            ce.raw_mentions.extend(mentions[:5])  # cap raw mentions per file
            ce.z_count += 1
    return by_canonical


# ============================================================
# Component 2: distant supervision seed from Tier-3-ACCEPT atoms
# ============================================================

def build_existing_atom_lexicon(pstore: PartitionedStore) -> dict[str, set[str]]:
    """Build per-canonical-form lexicon of existing atom names + aliases.

    Returns dict mapping canonical_form -> set of qualified_ids that match it
    (an atom may register under multiple canonical forms: its name + aliases).
    """
    lex: dict[str, set[str]] = defaultdict(set)
    for atom in pstore.all_atoms():
        # Atom name
        n_canon = canonicalize_candidate(atom.name or "")
        if n_canon:
            lex[n_canon].add(atom.qualified_id)
        # Atom id last segment
        last = atom.id.split("/")[-1] if "/" in atom.id else atom.id
        l_canon = canonicalize_candidate(last)
        if l_canon:
            lex[l_canon].add(atom.qualified_id)
        # Aliases
        for al in (atom.aliases or []):
            a_canon = canonicalize_candidate(al)
            if a_canon:
                lex[a_canon].add(atom.qualified_id)
    return dict(lex)


def build_substrate_vocabulary(pstore: PartitionedStore) -> set[str]:
    """Collect all substrate-known tokens from atom names + aliases + algebra fields.

    Used as a SUBSTRATE-NATIVE quality filter (Option B-lite): candidates whose
    tokens are predominantly substrate-known are LEGITIMATE substrate-domain
    technical concepts. Candidates whose tokens are not in substrate vocabulary
    are likely meta-narrative jargon or out-of-domain.
    """
    vocab: set[str] = set()
    for atom in pstore.all_atoms():
        for source in (atom.name or "", atom.id or "",
                        " ".join(atom.aliases or [])):
            for t in re.findall(r"[a-z][a-z0-9_]+", source.lower()):
                for tok in t.split("_"):
                    if len(tok) >= 3 and tok not in STOPWORDS:
                        vocab.add(tok)
        # Algebra dict values (about_topic, operation_type, etc.)
        for d in (atom.algebra, atom.signature, atom.complexity):
            if not d:
                continue
            for v in d.values():
                if isinstance(v, str):
                    for t in re.findall(r"[a-z][a-z0-9_]+", v.lower()):
                        for tok in t.split("_"):
                            if len(tok) >= 3 and tok not in STOPWORDS:
                                vocab.add(tok)
    return vocab


def substrate_vocabulary_overlap(canonical: str, vocab: set[str]) -> float:
    """Fraction of candidate's tokens that appear in substrate vocabulary.

    Higher score = candidate uses substrate-known terminology = legitimate.
    Lower score = candidate is non-substrate jargon = filter.
    """
    tokens = [t for t in canonical.split("_") if len(t) >= 3 and t not in STOPWORDS]
    if not tokens:
        return 0.0
    known = sum(1 for t in tokens if t in vocab)
    return known / len(tokens)


def distant_supervision_score(
    candidate: CandidateExtraction,
    lex: dict[str, set[str]],
) -> tuple[float, list[tuple[str, float]]]:
    """Score candidate vs existing atoms (Option A+ stricter fuzzy match).

    Returns (score, similarity_list).
    score = 1.0 exact-match canonical_name in lex
    score = max Jaccard >= 0.40 = LIKELY-COVERED (skip if skip_existing)
    score = lower partial match = NEW candidate
    """
    if candidate.canonical_name in lex:
        return 1.0, [(qid, 1.0) for qid in lex[candidate.canonical_name]]
    # Token-Jaccard partial match (Option A+: lowered threshold 0.5 -> 0.40 for skip;
    # but report all >= 0.30 as supervision context)
    cand_tokens = set(candidate.canonical_name.split("_"))
    best_matches = []
    for existing_canon, qids in lex.items():
        ex_tokens = set(existing_canon.split("_"))
        if not ex_tokens or not cand_tokens:
            continue
        overlap = len(cand_tokens & ex_tokens) / max(len(cand_tokens | ex_tokens), 1)
        if overlap >= 0.30:
            for qid in qids:
                best_matches.append((qid, overlap))
    best_matches.sort(key=lambda x: -x[1])
    best_score = best_matches[0][1] if best_matches else 0.0
    return best_score, best_matches[:5]


# ============================================================
# Component 5: gap-driven iterative outer loop + pipeline
# ============================================================

def name_vec_for_candidate(canonical: str, ai: AlgebraIndex) -> np.ndarray:
    """Build a name-vector for a candidate from its canonical tokens."""
    tokens = [t for t in canonical.split("_") if len(t) >= 2]
    if not tokens:
        return np.zeros(ai.dim, dtype=np.float32)
    vecs = [ai._filler_vector(t) for t in tokens]
    return ai._bundle(vecs)


def algebra_additions_template(candidate: CandidateExtraction,
                                nearest_cluster: Optional[int]) -> dict:
    """Suggest algebra_additions for a CREATE proposal based on cluster context."""
    additions = {}
    if nearest_cluster is not None:
        additions["category_int"] = int(nearest_cluster)
    additions["about_topic"] = candidate.canonical_name
    # Heuristic: derive operation_type / domain from canonical tokens
    tokens = candidate.canonical_name.split("_")
    if "algorithm" in tokens or "method" in tokens:
        additions["operation_type"] = "algorithm"
    elif "theory" in tokens or "framework" in tokens:
        additions["operation_type"] = "theoretical_framework"
    elif "model" in tokens or "network" in tokens:
        additions["operation_type"] = "model_or_architecture"
    return additions


def run_phase_2_light_pipeline(
    files: list[Path],
    pstore: PartitionedStore,
    ai: AlgebraIndex,
    skip_existing: bool = True,
    top_k: int = 30,
    use_pos_filter: bool = False,
) -> list[ProposalRecord]:
    """Run the full 5-component Phase-2-light pipeline on a set of files.

    Returns ranked top-K proposal records.
    """
    # Component 1: extract candidates
    candidates = extract_from_files(files)

    # Option B (Cycle 50 Research direction): substrate POS filter
    pos_tagger = None
    if use_pos_filter:
        from .substrate_nl_pos import get_default_tagger, is_noun_phrase
        pos_tagger = get_default_tagger()

    # Component 2: distant supervision (lexicon + fuzzy match)
    lex = build_existing_atom_lexicon(pstore)

    # Option A+ tightening: skip near-matches + explicit substrate-meta-jargon blocklist
    SKIP_NEAR_MATCH_THRESHOLD = 0.40
    # Empirical meta-jargon tokens that recur in research narrative (not atom-worthy)
    META_JARGON_LEADING = {"substrate", "methodology", "feedback", "scope",
                            "demo", "literature", "failure"}
    filtered: list[tuple[CandidateExtraction, float, list, np.ndarray]] = []
    for canonical, ce in candidates.items():
        score, matches = distant_supervision_score(ce, lex)
        if skip_existing and score >= SKIP_NEAR_MATCH_THRESHOLD:
            continue
        if ce.z_count < 3:
            continue
        # Meta-jargon blocklist: drop candidates leading with meta-narrative tokens
        first_token = canonical.split("_")[0]
        if first_token in META_JARGON_LEADING:
            continue
        # Option B: substrate POS filter -- keep only noun-phrase candidates
        if use_pos_filter and pos_tagger is not None:
            from .substrate_nl_pos import is_noun_phrase
            tokens = canonical.split("_")
            if not is_noun_phrase(tokens, pos_tagger):
                continue
        vec = name_vec_for_candidate(canonical, ai)
        filtered.append((ce, score, matches, vec))

    # Components 3 + 4: cluster-novelty filter + sparse-neighborhood ranking
    ranking_inputs = [(ce.canonical_name, vec) for ce, _, _, vec in filtered]
    rankings = rank_candidates_sparse_first(ranking_inputs, pstore, ai)

    # Build full ProposalRecord per ranked candidate
    by_canonical = {ce.canonical_name: (ce, score, matches, vec)
                    for ce, score, matches, vec in filtered}
    proposals: list[ProposalRecord] = []
    for r in rankings:
        if r.candidate_id not in by_canonical:
            continue
        ce, ds_score, ds_matches, _ = by_canonical[r.candidate_id]
        additions = algebra_additions_template(ce, r.nearest_cluster)
        proposals.append(ProposalRecord(
            candidate=ce,
            distant_supervision_score=ds_score,
            similarity_to_existing_T3=ds_matches,
            nearest_cluster=r.nearest_cluster,
            nearest_density=r.nearest_density,
            novelty=r.novelty,
            route=r.route,
            rank_score=r.rank_score,
            algebra_additions_template=additions,
        ))

    return proposals[:top_k]
