"""Refuse-gated retrieval wrapper -- addresses F1 refuse-discipline failure.

Per F1 RETRACTION 2026-06-14 (commit history): substrate's retrieve primitives
return top-k candidates UNCONDITIONALLY, even when no candidate has confidence
above a meaningful threshold. This causes hallucinated false-positives on
held-out (unknown-topic) queries: substrate returns ranked-but-spurious atoms
instead of REFUSING.

USER 18th rule: substrate refuses what it cannot prove. This wrapper enforces
that at the retrieval layer: returns an EMPTY candidate list when the
top-score is below `min_confidence`. Calling code interprets empty as
"substrate refuses; no atoms matched at meaningful confidence."

Atom grounded as executable:
  meta::SELF/capability_reason_about_self (refuse-when-unknown is part of
                                            substrate's self-reasoning)

Generic; wraps any object implementing semantic/structural/hybrid methods.
Pure-Python; no LLM, no bge, no torch (this is infrastructure; the underlying
retriever uses bge on the remote desktop where torch is installed).

Test uses a MOCK retriever (since laptop forbids torch model load) to verify
the refuse-discipline logic in isolation. Real-substrate integration is on
runner-desktop.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, Sequence


@dataclass
class GatedCandidate:
    """Retrieval candidate after refuse-gate filtering."""
    atom_id: str
    score: float
    via: str = "refuse_gated"


class RetrieverProtocol(Protocol):
    """Subset of backend.substrate_index.retrieve.Retriever interface used here."""
    def semantic(self, text: str, top_k: int = 10) -> list: ...
    def structural(self, atom_id: str, rel_type, top_k: int = 10) -> list: ...
    def hybrid(self, text: str, top_k: int = 10, **filters) -> list: ...


class RefuseGatedRetriever:
    """Wrap a Retriever and refuse-when-low-confidence per USER 18th rule.

    Args:
        retriever: any object with semantic/structural/hybrid methods
        min_confidence: score floor; if NO candidate scores above this,
                        return empty list (substrate refuses)
        margin_floor: optional secondary check; if top-2 score gap is below
                      this margin, substrate "is uncertain between candidates"
                      and also refuses
        refuse_log: optional callable invoked with (query, mode, top_score)
                    when substrate refuses; for audit / 19th-rule self-correction

    Returns: empty list if refuse; otherwise filtered + ranked candidates.
    """

    def __init__(
        self,
        retriever,
        min_confidence: float = 0.35,
        margin_floor: float = 0.0,
        refuse_log=None,
    ):
        if not (0.0 <= min_confidence <= 1.0):
            raise ValueError(
                f"min_confidence must be in [0, 1]; got {min_confidence}"
            )
        if margin_floor < 0.0:
            raise ValueError(
                f"margin_floor must be non-negative; got {margin_floor}"
            )
        self.retriever = retriever
        self.min_confidence = min_confidence
        self.margin_floor = margin_floor
        self.refuse_log = refuse_log

    def _get_score(self, cand) -> float:
        """Extract score from a candidate; accepts dataclass, dict, or tuple."""
        if hasattr(cand, "score"):
            return float(cand.score)
        if isinstance(cand, dict) and "score" in cand:
            return float(cand["score"])
        if isinstance(cand, (tuple, list)) and len(cand) >= 2:
            return float(cand[1])
        raise TypeError(
            f"cannot extract score from candidate of type {type(cand)}"
        )

    def _filter(self, candidates: Sequence, query: str, mode: str) -> list:
        """Apply refuse-discipline: return [] if no candidate passes the gate."""
        if not candidates:
            self._log_refusal(query, mode, top_score=None, reason="no_candidates")
            return []
        # Sort by score descending (defensive; retriever should already)
        ranked = sorted(candidates, key=self._get_score, reverse=True)
        top_score = self._get_score(ranked[0])
        if top_score < self.min_confidence:
            self._log_refusal(
                query, mode, top_score=top_score, reason="below_min_confidence"
            )
            return []
        # Margin check between top-1 and top-2 (if margin_floor > 0)
        if self.margin_floor > 0 and len(ranked) >= 2:
            second_score = self._get_score(ranked[1])
            if top_score - second_score < self.margin_floor:
                self._log_refusal(
                    query, mode, top_score=top_score, reason="below_margin_floor"
                )
                return []
        # Pass: return all candidates with score >= min_confidence
        return [c for c in ranked if self._get_score(c) >= self.min_confidence]

    def _log_refusal(self, query, mode, top_score, reason):
        if self.refuse_log is not None:
            try:
                self.refuse_log({
                    "query": query, "mode": mode,
                    "top_score": top_score, "reason": reason,
                })
            except Exception:
                pass  # log failure must not bubble up to substrate

    def semantic(self, text: str, top_k: int = 10) -> list:
        candidates = self.retriever.semantic(text, top_k=top_k)
        return self._filter(candidates, query=text, mode="semantic")

    def structural(self, atom_id: str, rel_type, top_k: int = 10) -> list:
        candidates = self.retriever.structural(atom_id, rel_type, top_k=top_k)
        return self._filter(
            candidates,
            query=f"{atom_id}.{rel_type}",
            mode="structural",
        )

    def hybrid(self, text: str, top_k: int = 10, **filters) -> list:
        candidates = self.retriever.hybrid(text, top_k=top_k, **filters)
        return self._filter(candidates, query=text, mode="hybrid")


# ============================================================
# Live-query test (verifies refuse-discipline logic in isolation)
# ============================================================

@dataclass
class _MockCandidate:
    atom_id: str
    score: float


class _MockRetriever:
    """Mock Retriever for testing refuse-discipline without bge/torch."""

    def __init__(self, fake_results: dict[str, list[_MockCandidate]]):
        self.fake_results = fake_results

    def semantic(self, text: str, top_k: int = 10) -> list:
        return self.fake_results.get(text, [])

    def structural(self, atom_id: str, rel_type, top_k: int = 10) -> list:
        return self.fake_results.get(f"{atom_id}.{rel_type}", [])

    def hybrid(self, text: str, top_k: int = 10, **filters) -> list:
        return self.fake_results.get(text, [])


def _live_query_test() -> dict:
    """Verify refuse-discipline gate works correctly on synthetic scores."""
    # In-coverage query: top score 0.82 (high confidence) -> should pass
    # Coverage-gap query: top score 0.18 (low confidence) -> should refuse
    # Margin-ambiguous query: top1=0.55, top2=0.53 (low margin) -> refuse
    # Empty results: -> refuse
    fake = {
        "in_coverage_query": [
            _MockCandidate("math::T1/inner_product", 0.82),
            _MockCandidate("math::T1/cosine_similarity", 0.41),
            _MockCandidate("math::T2/circular_convolution", 0.32),
        ],
        "coverage_gap_query": [
            _MockCandidate("random1", 0.18),
            _MockCandidate("random2", 0.17),
            _MockCandidate("random3", 0.15),
        ],
        "margin_ambiguous_query": [
            _MockCandidate("candidate1", 0.55),
            _MockCandidate("candidate2", 0.53),
            _MockCandidate("candidate3", 0.20),
        ],
        "empty_query": [],
    }
    mock = _MockRetriever(fake)
    refusals = []
    gated = RefuseGatedRetriever(
        mock,
        min_confidence=0.35,
        margin_floor=0.1,
        refuse_log=refusals.append,
    )
    results = {
        "in_coverage": [c.atom_id for c in gated.semantic("in_coverage_query")],
        "coverage_gap": [c.atom_id for c in gated.semantic("coverage_gap_query")],
        "margin_ambiguous": [c.atom_id for c in gated.semantic("margin_ambiguous_query")],
        "empty": [c.atom_id for c in gated.semantic("empty_query")],
        "refusal_log_entries": len(refusals),
        "refusals": refusals,
    }
    return results


if __name__ == "__main__":
    print("=== REFUSE-GATED RETRIEVER -- live-query test ===")
    r = _live_query_test()
    print(f"\nin_coverage:      returns {r['in_coverage']}")
    print(f"coverage_gap:     returns {r['coverage_gap']} (REFUSED; below min_confidence)")
    print(f"margin_ambiguous: returns {r['margin_ambiguous']} (REFUSED; low margin)")
    print(f"empty:            returns {r['empty']} (REFUSED; no candidates)")
    print(f"\nrefusal log entries: {r['refusal_log_entries']}")
    for entry in r["refusals"]:
        print(f"  {entry['reason']}: query='{entry['query'][:30]}' top={entry['top_score']}")

    # Soundness gates
    assert r["in_coverage"] == ["math::T1/inner_product", "math::T1/cosine_similarity"], \
        f"in_coverage should return both above-threshold candidates; got {r['in_coverage']}"
    assert r["coverage_gap"] == [], \
        f"coverage_gap should refuse; got {r['coverage_gap']}"
    assert r["margin_ambiguous"] == [], \
        f"margin_ambiguous should refuse; got {r['margin_ambiguous']}"
    assert r["empty"] == [], \
        f"empty should refuse; got {r['empty']}"
    assert r["refusal_log_entries"] == 3, \
        f"expected 3 refusals logged; got {r['refusal_log_entries']}"
    print("\nLIVE QUERY PASS: refuse-discipline gate enforces USER 18th rule on retrieval.")
