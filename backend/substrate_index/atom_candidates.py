"""Substrate-proposed atom-candidate generation (Tier 3 capability).

Per Research 5-tier progression: Tier 3 = "substrate-native atom-candidate
generation pipeline." Substrate looks at its own corpus and proposes atoms
that should exist but don't.

Four sources of candidates:

1. **Unmet decomposes_to references**: concept atoms reference math atoms
   that don't yet exist in the corpus. Each unmet reference is an
   atom-candidate.

2. **Cross-corpus orphan candidates**: math atoms with no concept-corpus
   atom decomposing-to them might warrant a concept atom describing their
   downstream capability use.

3. **Algebra-cluster centroids without canonical representative**: an
   algebra cluster of T3 sub-ops without a parent T2 primitive may need
   a canonical T2 atom.

4. **Repeated-name candidates from substrate-eval**: terms repeatedly mentioned
   in research notes that name-match no existing atom. Surface via the
   name-match index built for composite C.

These are PROPOSALS not creations -- substrate proposes, Research validates
hand-authored content per [[substrate-content-sources-us-or-substrate-2026-06-11]].
"""
from __future__ import annotations

import logging
import re
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from backend.substrate_index.algebra_index import AlgebraIndex
from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import Atom, Corpus, RelationType, Tier

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class AtomCandidate:
    """A substrate-proposed atom that should exist but doesn't yet."""
    proposed_id: str
    suggested_corpus: str
    suggested_tier: str
    suggested_kind: str
    justification_type: str   # "unmet_decomposes_to" / "algebra_centroid_orphan" / etc.
    referenced_by: tuple[str, ...]  # existing atoms that point at this candidate
    confidence: float
    notes: str

    def to_dict(self) -> dict:
        return {
            "proposed_id": self.proposed_id,
            "suggested_corpus": self.suggested_corpus,
            "suggested_tier": self.suggested_tier,
            "suggested_kind": self.suggested_kind,
            "justification_type": self.justification_type,
            "referenced_by": list(self.referenced_by),
            "confidence": self.confidence,
            "notes": self.notes,
        }


# ============================================================
# Source 1: unmet decomposes_to references
# ============================================================


def unmet_decomposes_to_candidates(pstore: PartitionedStore) -> list[AtomCandidate]:
    """Find atom IDs referenced in concept atoms' decomposes_to lists that
    don't exist in the corpus."""
    references: dict[str, list[str]] = defaultdict(list)
    for atom in pstore.all_atoms():
        decomp = atom.metadata.get("decomposes_to") or []
        for tgt in decomp:
            qid = tgt if "::" in tgt else f"math::{tgt}"
            references[qid].append(atom.qualified_id)

    candidates: list[AtomCandidate] = []
    for tgt_qid, referrers in references.items():
        if pstore.has_atom(tgt_qid):
            continue
        # Extract suggested corpus + tier from qualified id
        if "::" in tgt_qid:
            corpus_part, local_id = tgt_qid.split("::", 1)
        else:
            corpus_part, local_id = "math", tgt_qid
        if local_id.startswith("T1/"):
            tier = "T1"
        elif local_id.startswith("T2/"):
            tier = "T2"
        elif local_id.startswith("T3/"):
            tier = "T3"
        elif local_id.startswith("T4/"):
            tier = "T4"
        elif local_id.startswith("T2_FAM"):
            tier = "T2_FAM"
        else:
            tier = "NA"
        kind = "family_tag" if "T2_FAM" in local_id else "sub_op" if tier == "T3" else "primitive"
        candidates.append(AtomCandidate(
            proposed_id=tgt_qid,
            suggested_corpus=corpus_part,
            suggested_tier=tier,
            suggested_kind=kind,
            justification_type="unmet_decomposes_to",
            referenced_by=tuple(referrers),
            confidence=min(1.0, 0.5 + 0.1 * len(referrers)),
            notes=f"Referenced by {len(referrers)} concept atom(s) but missing from corpus",
        ))
    return sorted(candidates, key=lambda c: -c.confidence)


# ============================================================
# Source 2: cross-corpus orphans (math atoms with NO concept user)
# ============================================================


def cross_corpus_orphan_concept_candidates(pstore: PartitionedStore) -> list[AtomCandidate]:
    """Math atoms with no incoming USES (no concept depends on them) may
    indicate a missing concept-corpus atom that should describe a capability
    using this math atom."""
    candidates: list[AtomCandidate] = []
    for atom in pstore.math.all_atoms():
        if atom.kind.value == "family_tag":
            continue
        # Check if any concept atom decomposes_to this atom
        has_user = False
        for in_edge in pstore.in_neighbors(atom.qualified_id, RelationType.USES):
            if in_edge.startswith("concept::"):
                has_user = True
                break
        if has_user:
            continue
        # Propose: concept atom that uses this math primitive
        proposed = f"concept::CAPABILITY_using_{atom.id.split('/')[-1]}"
        candidates.append(AtomCandidate(
            proposed_id=proposed,
            suggested_corpus="concept",
            suggested_tier="T2",
            suggested_kind="capability",
            justification_type="math_atom_has_no_concept_user",
            referenced_by=(atom.qualified_id,),
            confidence=0.4,
            notes=f"Math primitive {atom.qualified_id} has no concept-corpus capability decomposing to it; substrate may need a capability that uses this primitive",
        ))
    return candidates


# ============================================================
# Source 3: algebra cluster centroids without canonical representative
# ============================================================


def algebra_centroid_candidates(
    pstore: PartitionedStore,
    aidx: AlgebraIndex,
    min_cluster_size: int = 3,
) -> list[AtomCandidate]:
    """For each algebra category, if T3 sub-ops cluster tightly but lack a
    canonical T2 primitive describing the cluster's core operation, propose
    one."""
    from backend.substrate_index.algebra_cluster import _agglomerative_cluster
    import numpy as np

    if aidx._algebra_matrix is None:
        return []

    cluster_idx = _agglomerative_cluster(aidx._algebra_matrix, distance_threshold=0.25)
    candidates: list[AtomCandidate] = []
    for cid, members in enumerate(cluster_idx):
        if len(members) < min_cluster_size:
            continue
        # Get the cluster member atom ids
        member_qids = [aidx._algebra_atom_ids[i] for i in members]
        member_atoms = [pstore.get_atom(qid) for qid in member_qids]
        member_atoms = [a for a in member_atoms if a is not None]
        # Are all members T3 sub-ops, with no T2 atom in cluster?
        t3_count = sum(1 for a in member_atoms if a.tier.value == "T3")
        t2_count = sum(1 for a in member_atoms if a.tier.value in ("T2", "T2_FAM"))
        if t3_count >= min_cluster_size and t2_count == 0:
            # Propose T2 primitive for this cluster
            shared_algebra = member_atoms[0].algebra if member_atoms[0].algebra else {}
            structure = shared_algebra.get("structure", "unknown")
            proposed_id = f"math::T2_proposed/{structure}_canonical"
            candidates.append(AtomCandidate(
                proposed_id=proposed_id,
                suggested_corpus="math",
                suggested_tier="T2",
                suggested_kind="primitive",
                justification_type="algebra_cluster_lacks_T2_canonical",
                referenced_by=tuple(member_qids),
                confidence=0.5 + 0.05 * len(members),
                notes=f"Algebra cluster of {len(members)} T3 sub-ops (structure={structure}) has no canonical T2 primitive describing the shared operation",
            ))
    return candidates


# ============================================================
# Source 5 (Research-proposed): substrate-eval references unknown math term
# ============================================================


_MATH_TERM_PATTERNS = [
    # Hyphenated proper-noun pairs ("Tracy-Widom", "Chu-Liu-Edmonds")
    r"(?<![a-z])([A-Z][a-z]+(?:-[A-Z][a-z]+){1,3})(?![a-z])",
    # Specific known acronyms (substrate / VSA / formal-systems jargon)
    r"\b(BOCPD|GHRR|DisCoCat|FHRR|HRR|TPR|SDM|RWA|CRF|SSVM|CLS|EM|SVD|TLDR)\b",
    # kappa_N / F_N notation
    r"\b(kappa_[0-9]+|F[0-9]+_[a-z_]+)\b",
    # Named theorems / phenomena
    r"\b(Marchenko-Pastur|Tracy-Widom|Wigner semicircle|Reed-Solomon|Voiculescu|Glauber|Dyson Brownian|Ramsauer)\b",
]


# Stop list: common English phrases caught by the proper-noun pattern
_STOP_TERMS = {
    "this is", "this makes", "this gives", "this means", "this implies",
    "the the", "et al", "et alii", "the substrate", "the bge",
    "verified citation", "verified citation count",
}


# Math-context keywords per Research Q1 source #5 noise fix
_MATH_CONTEXT_KEYWORDS = {
    "theorem", "algorithm", "method", "transform", "distribution", "regime",
    "inequality", "matrix", "space", "bound", "rule", "divergence",
    "identity", "metric", "norm", "operator", "primitive", "functor",
    "equation", "lemma", "proposition", "corollary",
}


# Math acronyms (one half can be these in hyphenated names)
_MATH_ACRONYMS_HALF = {
    "lp", "mp", "rmt", "vsa", "hdc", "fhrr", "hrr", "ica", "pca", "lda",
    "svd", "fft", "dft", "qr", "lu", "svm", "crf", "hmm", "cls", "tpr",
    "rl", "ml", "ai", "nn",
}


def _has_math_context(text: str, term: str, window: int = 20) -> bool:
    """Check if a math-context keyword appears within `window` words of the term."""
    text_lower = text.lower()
    term_lower = term.lower()
    pos = text_lower.find(term_lower)
    if pos < 0:
        return False
    start = max(0, pos - 200)
    end = min(len(text_lower), pos + 200)
    snippet = text_lower[start:end]
    words = snippet.split()
    for kw in _MATH_CONTEXT_KEYWORDS:
        if kw in snippet:
            return True
    return False


def _hyphenated_term_acceptable(term: str) -> bool:
    """For hyphenated terms, require both halves are surnames OR one half is a math acronym."""
    if "-" not in term:
        return True  # not hyphenated; this filter doesn't apply
    parts = term.split("-")
    # Both halves capitalized words (surname-pattern)
    if all(p[0].isupper() and p[1:].islower() and len(p) >= 3 for p in parts):
        return True
    # One half is a known math acronym
    if any(p.lower() in _MATH_ACRONYMS_HALF for p in parts):
        return True
    return False


def substrate_eval_references_unknown_math_term(
    pstore: PartitionedStore,
    source_files: list[Path],
    min_referrers: int = 2,         # Q1 fix #2: >=2 distinct sources
    require_math_context: bool = True,  # Q1 fix #1
    top_cap: int = 50,              # Q1 fix #4
) -> list[AtomCandidate]:
    """Source #5 per Research FINDINGS_09 validation:
    Find math terms mentioned in research/drill/exp_dev notes that don't
    exist as atoms in the corpus.

    Inverse of source #2 (math-with-no-concept-user): this finds
    concept-with-no-math-atom.
    """
    import re

    # Build existing math-atom-name set (lowercase normalized; including
    # individual word stems so 'fhrr' matches T2/fhrr_bind)
    existing_names: set[str] = set()
    for atom in pstore.all_atoms():
        if atom.corpus.value == "math":
            existing_names.add(atom.name.lower())
            for alias in atom.aliases:
                existing_names.add(alias.lower())
            local = atom.id.split("/")[-1].lower()
            existing_names.add(local)
            existing_names.add(local.replace("_", " "))
            # Add individual word components ('fhrr', 'bind' from 'fhrr_bind')
            for word in local.split("_"):
                if len(word) >= 3:
                    existing_names.add(word)
    # Stem-noise filter: compound-word prefixes that produce English-phrase
    # hits with the hyphen pattern (not substrate-specific terms)
    COMMON_COMPOUND_PREFIXES = (
        "multi", "real", "cross", "self", "sub", "super", "non", "pre",
        "post", "co", "un", "re", "out", "over", "under", "off",
    )

    # Extract candidate terms from source files
    term_referrers: dict[str, list[str]] = defaultdict(list)
    for src_path in source_files:
        try:
            text = src_path.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        for pattern in _MATH_TERM_PATTERNS:
            for match in re.finditer(pattern, text):
                term = match.group(0).strip()
                if len(term) < 3:
                    continue
                # Normalize
                norm = term.lower().replace("-", " ").replace("_", " ")
                norm = " ".join(norm.split())
                if norm in existing_names:
                    continue
                if norm in _STOP_TERMS:
                    continue
                # Drop terms with common English stems
                if any(stop in norm for stop in ("citation", "consistent", "makes the",
                                                  "is the", "the the", "et al")):
                    continue
                # Drop compound-word prefixes (multi-, cross-, self-, etc.)
                first_word = norm.split(" ")[0]
                if first_word in COMMON_COMPOUND_PREFIXES:
                    continue
                # Drop terms that contain only generic substrate-vocabulary words
                if any(any(w == norm or w in norm.split() for w in
                           ("substrate", "the", "this", "that", "from", "into",
                            "case", "term", "step", "level", "thread")) for _ in [0]):
                    if not any(c.isupper() for c in term):
                        # If the term has no uppercase chars and contains generic
                        # vocabulary, skip it
                        continue
                # Q1 fix #3: hyphenated terms require both halves surnames OR one is math acronym
                if "-" in term and not _hyphenated_term_acceptable(term):
                    continue
                # Q1 fix #1: math-context keyword filter
                if require_math_context and not _has_math_context(text, term):
                    continue
                term_referrers[norm].append(str(src_path))

    # Build candidates
    candidates: list[AtomCandidate] = []
    for term, referrers in term_referrers.items():
        n_distinct = len(set(referrers))
        if n_distinct < min_referrers:
            continue
        # Suggested id (lowercase + underscore)
        suggested_local = term.replace(" ", "_")
        candidates.append(AtomCandidate(
            proposed_id=f"math::T?/{suggested_local}",
            suggested_corpus="math",
            suggested_tier="unknown",
            suggested_kind="primitive",
            justification_type="substrate_eval_references_unknown_math_term",
            referenced_by=tuple(sorted(set(referrers))),
            confidence=min(0.90, 0.40 + 0.10 * min(5, n_distinct)),
            notes=f"Term '{term}' mentioned in {n_distinct} research source(s); no math atom with this name exists",
        ))
    candidates.sort(key=lambda c: -c.confidence)
    # Q1 fix #4: cap at top_cap by confidence
    return candidates[:top_cap]


# ============================================================
# Aggregate report
# ============================================================


@dataclass(frozen=True)
class AtomCandidateReport:
    n_candidates: int
    by_justification: dict
    candidates: tuple[AtomCandidate, ...]

    def to_dict(self) -> dict:
        return {
            "n_candidates": self.n_candidates,
            "by_justification": dict(self.by_justification),
            "candidates": [c.to_dict() for c in self.candidates],
        }


def generate_candidates(
    pstore: PartitionedStore,
    aidx: Optional[AlgebraIndex] = None,
    source_files: Optional[list[Path]] = None,
) -> AtomCandidateReport:
    """Run all candidate-generation sources; return aggregated report."""
    all_candidates: list[AtomCandidate] = []
    all_candidates.extend(unmet_decomposes_to_candidates(pstore))
    all_candidates.extend(cross_corpus_orphan_concept_candidates(pstore))
    if aidx is not None:
        all_candidates.extend(algebra_centroid_candidates(pstore, aidx))
    if source_files:
        all_candidates.extend(substrate_eval_references_unknown_math_term(pstore, source_files))

    by_just: Counter = Counter()
    for c in all_candidates:
        by_just[c.justification_type] += 1

    return AtomCandidateReport(
        n_candidates=len(all_candidates),
        by_justification=dict(by_just),
        candidates=tuple(sorted(all_candidates, key=lambda c: -c.confidence)),
    )
