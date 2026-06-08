"""
substrate.disambig -- Two-stage entity disambiguation + K-hop (PP-125).

Port of exp_two_stage_disambig_khop_cpu_v1.py.

CORE IDEA:
A natural-language question often mentions an entity ambiguously ("OpenAI" might mean
the company OR a paper OR a job posting). Stage 1 uses a fuzzy embedding similarity to
identify the top-B candidate START entities. Stage 2 runs native substrate K-hop from
each candidate in parallel; the K-hop result with highest confidence wins.

Implementation needs an external fuzzy encoder (production: bge-large; validated cycle 187).
For tests we substitute random embeddings to verify the dispatch logic.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Callable, Optional

import numpy as np

from substrate.khop import KHopResult, traverse


@dataclass
class DisambigResult:
    question: str
    relation_path: list[str]
    candidates_considered: list[str]   # entities tried in stage 2
    khop_results: list[KHopResult]
    best_result: Optional[KHopResult]
    elapsed_ms: float


def two_stage_resolve(
    question: str,
    relation_path: list[str],
    fuzzy_match_fn: Callable[[str], list[str]],
    ent_codebook: dict,
    rel_codebook: dict,
    subject_memory: dict,
    top_b: int = 3,
    query_id: str = "disambig_0",
) -> DisambigResult:
    """Two-stage entity resolution.

    Args:
        question: the natural-language question (used for fuzzy matching)
        relation_path: relation names to traverse (already extracted from question)
        fuzzy_match_fn: callable(question) -> list of top-B candidate entity names
        ent_codebook / rel_codebook / subject_memory: substrate state
        top_b: how many fuzzy candidates to try
        query_id: identifier for audit chains

    Returns: DisambigResult with the best K-hop result by confidence.
    """
    import time
    t0 = time.perf_counter()

    candidates = fuzzy_match_fn(question)[:top_b]
    results: list[KHopResult] = []
    for i, candidate in enumerate(candidates):
        if candidate not in subject_memory:
            continue
        r = traverse(
            start_entity=candidate,
            relation_path=relation_path,
            ent_codebook=ent_codebook,
            rel_codebook=rel_codebook,
            subject_memory=subject_memory,
            query_id=f"{query_id}_cand{i}",
        )
        results.append(r)

    if not results:
        elapsed_ms = (time.perf_counter() - t0) * 1000
        return DisambigResult(
            question=question,
            relation_path=relation_path,
            candidates_considered=candidates,
            khop_results=[],
            best_result=None,
            elapsed_ms=elapsed_ms,
        )

    # Pick highest final_confidence among results that didn't fail mid-traversal
    best = max(results, key=lambda r: (r.final_entity is not None, r.final_confidence))
    elapsed_ms = (time.perf_counter() - t0) * 1000
    return DisambigResult(
        question=question,
        relation_path=relation_path,
        candidates_considered=candidates,
        khop_results=results,
        best_result=best,
        elapsed_ms=elapsed_ms,
    )


def _self_test():
    """Smoke test with synthetic fuzzy matcher and tiny KG."""
    import math
    from substrate.core import cphasor

    rng = np.random.default_rng(0)
    dim = 1024
    entity_names = ["OpenAI_Company", "OpenAI_paper", "OpenAI_job_post", "Sam_Altman"]
    relation_names = ["ceo"]
    book = cphasor(len(entity_names), dim=dim, rng=rng)
    rels_book = cphasor(len(relation_names), dim=dim, rng=rng)
    ents = {n: book[i] for i, n in enumerate(entity_names)}
    rels = {n: rels_book[i] for i, n in enumerate(relation_names)}

    # Only OpenAI_Company has a CEO fact
    subject_memory = {"OpenAI_Company": rels["ceo"] * ents["Sam_Altman"]}

    # Fuzzy matcher returns 3 candidates (the right one + 2 wrong)
    def fuzzy_match(q: str):
        return ["OpenAI_paper", "OpenAI_Company", "OpenAI_job_post"]

    result = two_stage_resolve(
        question="who is the ceo of OpenAI?",
        relation_path=["ceo"],
        fuzzy_match_fn=fuzzy_match,
        ent_codebook=ents,
        rel_codebook=rels,
        subject_memory=subject_memory,
        top_b=3,
    )
    assert result.best_result is not None
    assert result.best_result.start_entity == "OpenAI_Company", \
        f"Expected OpenAI_Company as best, got {result.best_result.start_entity}"
    assert result.best_result.final_entity == "Sam_Altman"
    print(f"[substrate.disambig] self-test PASS (two-stage resolved {result.best_result.start_entity} "
          f"-> {result.best_result.final_entity} from {len(result.candidates_considered)} candidates)")


if __name__ == "__main__":
    _self_test()
