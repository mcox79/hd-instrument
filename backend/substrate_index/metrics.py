"""Measurement framework for the substrate self-index pilot.

Per user direction 2026-06-11: "we need a way to measure how well it works, how
to improve it." This module is the load-bearing measurement contract that the
substrate retrieval system implements against. Comparative-vs-LLM scoring AND
self-diagnosis live here.

Public surface:
  - QueryScore       per-query scoring breakdown
  - SystemDiagnostic aggregate metrics + improvement recommendations
  - FailureMode      enum of why a query failed (drives improvement signals)
  - score_query()    score one QueryResult against one TestQuery
  - diagnose()       aggregate over a set of (query, result) pairs
  - render_report()  human-readable markdown report

Design principles:
  1. Every failed query gets a failure-mode tag so improvement signals are concrete.
  2. Aggregate metrics include both substrate-internal scores AND comparative
     (substrate vs LLM) scores when an LLM result is provided.
  3. Improvement recommendations are auto-generated from the failure-mode histogram.
  4. Sealed queries can be scored privately (only the aggregate leaks before Day 2-3
     joint validation; per Research's no-cherry-picking rule).
"""
from __future__ import annotations

import enum
import math
import statistics
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from backend.substrate_index.schema import QueryResult, QueryType, TestQuery


# ============================================================
# Failure mode classification
# ============================================================


class FailureMode(enum.Enum):
    """Why a query failed. Drives improvement recommendations."""
    NONE = "none"                          # Query succeeded; not a failure
    NO_MATCH = "no_match"                  # No candidate atom returned at all
    WRONG_RANKING = "wrong_ranking"        # Correct atom in top-K but not top-1
    MISSED_RELATION = "missed_relation"    # Atom found but typed-edge missing
    EMBEDDING_DRIFT = "embedding_drift"    # Wrong atom returned at top-1 (semantic mismatch)
    COVERAGE_GAP = "coverage_gap"          # Query references atom that doesn't exist
    LATENCY_FAIL = "latency_fail"          # Returned correct but too slow (>500ms)
    LLM_LOSS = "llm_loss"                  # Substrate correct but LLM judged better

    @classmethod
    def classify(
        cls,
        query: TestQuery,
        result: QueryResult,
        known_atom_ids: set[str],
        latency_budget_ms: float = 500.0,
    ) -> "FailureMode":
        """Classify a query's failure mode. Returns NONE if successful.

        Heuristics, in priority order:
        1. expected atoms reference an atom not in the corpus  -> COVERAGE_GAP
        2. no atoms returned at all  -> NO_MATCH
        3. top-1 wrong + expected atom NOT in top-K  -> EMBEDDING_DRIFT
        4. top-1 wrong + expected atom IS in top-K  -> WRONG_RANKING
        5. atoms match but expected relations missing  -> MISSED_RELATION
        6. all match but latency > budget  -> LATENCY_FAIL
        7. otherwise  -> NONE
        """
        expected_ids = set(query.expected_atom_ids)
        returned = list(result.returned_atom_ids)

        # 1. coverage gap
        missing_expected = expected_ids - known_atom_ids
        if missing_expected and not expected_ids.issubset(known_atom_ids):
            return cls.COVERAGE_GAP

        # 2. no match
        if not returned:
            return cls.NO_MATCH if expected_ids else cls.NONE

        # If no expected atoms (purely structural query), only relations matter
        if not expected_ids:
            if query.expected_relations:
                expected_rel_set = set(query.expected_relations)
                returned_rel_set = set(result.returned_relations)
                if not (expected_rel_set & returned_rel_set):
                    return cls.MISSED_RELATION
            return cls.NONE

        # 3 & 4: top-1 mismatch
        top1 = returned[0]
        if top1 not in expected_ids:
            top_k = set(returned[:5])
            if not (top_k & expected_ids):
                return cls.EMBEDDING_DRIFT
            return cls.WRONG_RANKING

        # 5. relation miss
        if query.expected_relations:
            expected_rel_set = set(query.expected_relations)
            returned_rel_set = set(result.returned_relations)
            if not (expected_rel_set & returned_rel_set):
                return cls.MISSED_RELATION

        # 6. latency
        if result.latency_ms > latency_budget_ms:
            return cls.LATENCY_FAIL

        return cls.NONE


# ============================================================
# Per-query scoring
# ============================================================


@dataclass(frozen=True)
class QueryScore:
    """Scoring breakdown for one query/result pair."""
    qid: str
    query_type: QueryType
    sealed: bool

    # Atom-list scoring
    recall_at_1: float       # 1.0 if any expected atom is in top-1
    recall_at_3: float
    recall_at_5: float
    recall_at_10: float
    mrr: float               # mean reciprocal rank of first expected atom (0 if none in top-10)
    ndcg_at_10: float        # discounted cumulative gain over top-10

    # Relation scoring
    relations_recall: float  # |expected_rels ∩ returned_rels| / |expected_rels|

    # Combined
    exact_atom_match: bool   # top-1 is in expected AND len(returned)==len(expected)
    latency_ms: float
    failure_mode: FailureMode

    def to_dict(self) -> dict:
        return {
            "qid": self.qid,
            "query_type": self.query_type.value,
            "sealed": self.sealed,
            "recall_at_1": self.recall_at_1,
            "recall_at_3": self.recall_at_3,
            "recall_at_5": self.recall_at_5,
            "recall_at_10": self.recall_at_10,
            "mrr": self.mrr,
            "ndcg_at_10": self.ndcg_at_10,
            "relations_recall": self.relations_recall,
            "exact_atom_match": self.exact_atom_match,
            "latency_ms": self.latency_ms,
            "failure_mode": self.failure_mode.value,
        }


def _recall_at_k(returned: list[str], expected: set[str], k: int) -> float:
    if not expected:
        return 1.0  # vacuous; nothing to recall
    top_k = set(returned[:k])
    return 1.0 if (top_k & expected) else 0.0


def _mrr(returned: list[str], expected: set[str]) -> float:
    if not expected:
        return 0.0
    for i, atom_id in enumerate(returned[:10]):
        if atom_id in expected:
            return 1.0 / (i + 1)
    return 0.0


def _ndcg_at_k(returned: list[str], expected: set[str], k: int = 10) -> float:
    if not expected:
        return 0.0
    dcg = 0.0
    for i, atom_id in enumerate(returned[:k]):
        rel = 1.0 if atom_id in expected else 0.0
        dcg += rel / math.log2(i + 2)
    # ideal DCG: all expected at top
    ideal_n = min(len(expected), k)
    idcg = sum(1.0 / math.log2(i + 2) for i in range(ideal_n))
    return dcg / idcg if idcg > 0 else 0.0


def score_query(
    query: TestQuery,
    result: QueryResult,
    known_atom_ids: set[str],
    latency_budget_ms: float = 500.0,
) -> QueryScore:
    """Score one QueryResult against one TestQuery.

    known_atom_ids: the full set of atom IDs present in the corpus; used to
        distinguish COVERAGE_GAP (corpus is missing the atom) from
        EMBEDDING_DRIFT (atom exists but wasn't retrieved).
    """
    returned = list(result.returned_atom_ids)
    expected = set(query.expected_atom_ids)

    # Atom scoring
    r1 = _recall_at_k(returned, expected, 1)
    r3 = _recall_at_k(returned, expected, 3)
    r5 = _recall_at_k(returned, expected, 5)
    r10 = _recall_at_k(returned, expected, 10)
    mrr = _mrr(returned, expected)
    ndcg = _ndcg_at_k(returned, expected, 10)

    # Relation scoring
    exp_rels = set(query.expected_relations)
    ret_rels = set(result.returned_relations)
    rel_recall = (len(exp_rels & ret_rels) / len(exp_rels)) if exp_rels else 1.0

    exact = (
        bool(returned)
        and bool(expected)
        and returned[0] in expected
        and set(returned[: len(query.expected_atom_ids)]) == expected
    )

    failure = FailureMode.classify(query, result, known_atom_ids, latency_budget_ms)

    return QueryScore(
        qid=query.qid,
        query_type=query.query_type,
        sealed=query.sealed,
        recall_at_1=r1,
        recall_at_3=r3,
        recall_at_5=r5,
        recall_at_10=r10,
        mrr=mrr,
        ndcg_at_10=ndcg,
        relations_recall=rel_recall,
        exact_atom_match=exact,
        latency_ms=result.latency_ms,
        failure_mode=failure,
    )


# ============================================================
# Aggregate diagnostics
# ============================================================


@dataclass(frozen=True)
class SystemDiagnostic:
    """Aggregate metrics + recommendations over a full benchmark run."""
    n_queries: int
    n_sealed: int
    mean_recall_at_1: float
    mean_recall_at_3: float
    mean_recall_at_5: float
    mean_mrr: float
    mean_ndcg: float
    mean_relations_recall: float
    mean_latency_ms: float
    p95_latency_ms: float
    n_exact_matches: int

    # Failure-mode histogram
    failure_histogram: dict      # {FailureMode value: count}

    # Comparative (when LLM scores provided)
    substrate_wins: int = 0      # substrate ndcg > llm ndcg
    llm_wins: int = 0
    ties: int = 0

    # Auto-generated improvement recommendations
    recommendations: tuple[str, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict:
        return {
            "n_queries": self.n_queries,
            "n_sealed": self.n_sealed,
            "mean_recall_at_1": self.mean_recall_at_1,
            "mean_recall_at_3": self.mean_recall_at_3,
            "mean_recall_at_5": self.mean_recall_at_5,
            "mean_mrr": self.mean_mrr,
            "mean_ndcg": self.mean_ndcg,
            "mean_relations_recall": self.mean_relations_recall,
            "mean_latency_ms": self.mean_latency_ms,
            "p95_latency_ms": self.p95_latency_ms,
            "n_exact_matches": self.n_exact_matches,
            "failure_histogram": dict(self.failure_histogram),
            "substrate_wins": self.substrate_wins,
            "llm_wins": self.llm_wins,
            "ties": self.ties,
            "recommendations": list(self.recommendations),
        }


def _recommend(failure_hist: Counter, n: int) -> list[str]:
    """Auto-generate improvement recommendations from failure-mode histogram.

    Each recommendation is concrete and actionable. The intent is to translate
    "5 of 10 failures are X" into "do Y to fix X" without ambiguity.
    """
    recs = []
    if n == 0:
        return ["no queries scored -- populate the test set"]

    # Threshold: > 30% of queries failing in one mode triggers a rec
    threshold = max(2, int(0.3 * n))

    if failure_hist[FailureMode.NO_MATCH.value] >= threshold:
        recs.append(
            f"NO_MATCH dominates ({failure_hist[FailureMode.NO_MATCH.value]}/{n}): "
            "retrieval pipeline is dropping queries before scoring. Check encoder "
            "warm-up, atom-vector cache populated, and similarity threshold floor."
        )

    if failure_hist[FailureMode.EMBEDDING_DRIFT.value] >= threshold:
        recs.append(
            f"EMBEDDING_DRIFT dominates ({failure_hist[FailureMode.EMBEDDING_DRIFT.value]}/{n}): "
            "atom descriptions are not landing where queries point. Consider richer "
            "descriptions (add aliases, formal definitions, example invocations) and "
            "re-running with a stronger encoder."
        )

    if failure_hist[FailureMode.WRONG_RANKING.value] >= threshold:
        recs.append(
            f"WRONG_RANKING dominates ({failure_hist[FailureMode.WRONG_RANKING.value]}/{n}): "
            "correct atom is in top-K but losing the top-1 fight. Consider a re-ranking "
            "step (cross-encoder), or weighting by tier/corpus, or adding query expansion."
        )

    if failure_hist[FailureMode.MISSED_RELATION.value] >= threshold:
        recs.append(
            f"MISSED_RELATION dominates ({failure_hist[FailureMode.MISSED_RELATION.value]}/{n}): "
            "atoms are retrieved but typed-edge lookup is failing. Add more relation "
            "types or improve the relation-index encoding. Verify HAS_USERS reverse "
            "derivation is being applied."
        )

    if failure_hist[FailureMode.COVERAGE_GAP.value] >= threshold:
        recs.append(
            f"COVERAGE_GAP dominates ({failure_hist[FailureMode.COVERAGE_GAP.value]}/{n}): "
            "queries reference atoms that don't exist in the corpus. Expand the corpus "
            "to include the missing atoms (each COVERAGE_GAP names a concrete missing atom)."
        )

    if failure_hist[FailureMode.LATENCY_FAIL.value] >= threshold:
        recs.append(
            f"LATENCY_FAIL dominates ({failure_hist[FailureMode.LATENCY_FAIL.value]}/{n}): "
            "correct results but too slow. Profile the retrieval path, cache atom vectors "
            "and relation indices in memory, batch query encoding."
        )

    if not recs:
        if failure_hist[FailureMode.NONE.value] == n:
            recs.append("All queries succeeded. Add harder queries to stress the system.")
        else:
            recs.append(
                "Failure modes are diverse (no single mode > 30%); "
                "address each failed query individually."
            )

    return recs


def diagnose(scores: list[QueryScore], llm_scores: Optional[list[QueryScore]] = None) -> SystemDiagnostic:
    """Aggregate query scores into a system-level diagnostic + recommendations.

    If llm_scores is provided (same qids), comparative substrate-vs-LLM win/loss
    counts are computed by NDCG.
    """
    n = len(scores)
    if n == 0:
        return SystemDiagnostic(
            n_queries=0, n_sealed=0,
            mean_recall_at_1=0, mean_recall_at_3=0, mean_recall_at_5=0,
            mean_mrr=0, mean_ndcg=0, mean_relations_recall=0,
            mean_latency_ms=0, p95_latency_ms=0, n_exact_matches=0,
            failure_histogram={},
            recommendations=("no queries scored -- populate the test set",),
        )

    n_sealed = sum(1 for s in scores if s.sealed)
    mean_r1 = statistics.mean(s.recall_at_1 for s in scores)
    mean_r3 = statistics.mean(s.recall_at_3 for s in scores)
    mean_r5 = statistics.mean(s.recall_at_5 for s in scores)
    mean_mrr = statistics.mean(s.mrr for s in scores)
    mean_ndcg = statistics.mean(s.ndcg_at_10 for s in scores)
    mean_rels = statistics.mean(s.relations_recall for s in scores)
    latencies = [s.latency_ms for s in scores]
    mean_lat = statistics.mean(latencies)
    sorted_lat = sorted(latencies)
    p95_lat = sorted_lat[int(0.95 * (n - 1))]
    exact = sum(1 for s in scores if s.exact_atom_match)

    failure_hist = Counter(s.failure_mode.value for s in scores)

    # Comparative
    s_wins = l_wins = ties = 0
    if llm_scores is not None:
        by_qid = {s.qid: s for s in scores}
        for llm_s in llm_scores:
            sub_s = by_qid.get(llm_s.qid)
            if sub_s is None:
                continue
            if sub_s.ndcg_at_10 > llm_s.ndcg_at_10 + 0.01:
                s_wins += 1
            elif llm_s.ndcg_at_10 > sub_s.ndcg_at_10 + 0.01:
                l_wins += 1
            else:
                ties += 1

    recs = tuple(_recommend(failure_hist, n))

    return SystemDiagnostic(
        n_queries=n,
        n_sealed=n_sealed,
        mean_recall_at_1=round(mean_r1, 3),
        mean_recall_at_3=round(mean_r3, 3),
        mean_recall_at_5=round(mean_r5, 3),
        mean_mrr=round(mean_mrr, 3),
        mean_ndcg=round(mean_ndcg, 3),
        mean_relations_recall=round(mean_rels, 3),
        mean_latency_ms=round(mean_lat, 1),
        p95_latency_ms=round(p95_lat, 1),
        n_exact_matches=exact,
        failure_histogram=dict(failure_hist),
        substrate_wins=s_wins,
        llm_wins=l_wins,
        ties=ties,
        recommendations=recs,
    )


# ============================================================
# Drift tracking
# ============================================================


# ============================================================
# Spectral observability (substrate-novel; LLM has no equivalent)
# ============================================================
#
# Per Research FREE_PROBABILITY_OBSERVABILITY_INTEGRATION 2026-06-11. Four
# spectral measures on the substrate codebook eigenvalue distribution:
#   1. Marchenko-Pastur bulk           (codebook eigenvalue density)
#   2. Tracy-Widom edge                (largest-eigenvalue fluctuations)
#   3. kappa_4 free cumulant           (semicircle deviation)
#   4. Spectral gap                    (separability regime)
#
# Full numpy implementation referenced in:
#   notes/research_drill_free_probability_substrate_framework_3x_2026-06-11.md
#
# Scheduled to populate after batch 02 lands (M >= 100 atoms required for
# reliable Tracy-Widom estimates per Research). For now, stub returns the
# raw eigenvalue stats so callers can wire the function shape without
# waiting on the drill output.


def spectral_observability(codebook_matrix) -> dict:
    """Compute substrate-novel spectral measures on the atom-vector codebook.

    Input: codebook_matrix shape (M, N) -- M atoms x N-dim vectors (typically
    M = #atoms in the index, N = 1024 for bge-large).

    Output: dict with mp_bulk, tw_edge, kappa_4, spectral_gap.

    Implementation per Research's free-probability drill (post-batch-02
    activation; current stub returns raw eigenvalue summary).
    """
    import numpy as np
    M, N = codebook_matrix.shape
    if M < 4:
        return {"insufficient_M": M, "min_required": 4}
    W = codebook_matrix @ codebook_matrix.T / N
    eig = np.linalg.eigvalsh(W)
    return {
        "M": M,
        "N": N,
        "eig_min": float(eig[0]),
        "eig_max": float(eig[-1]),
        "eig_mean": float(eig.mean()),
        "eig_var": float(eig.var()),
        "spectral_gap": float(eig[-1] - eig[-2]),
        # mp_bulk / tw_edge / kappa_4: filled in post-batch-02 from
        # Research's drill numpy implementation
        "mp_bulk": None,
        "tw_edge": None,
        "kappa_4": None,
        "_status": "stub_pending_batch_02_and_drill_code",
    }


# ============================================================
# Drift detection
# ============================================================


def detect_drift(
    current: SystemDiagnostic,
    baseline: SystemDiagnostic,
    drop_threshold_pp: float = 5.0,
) -> list[str]:
    """Compare current diagnostic against a baseline; flag regressions.

    Returns a list of human-readable drift flags. Empty list means no
    regressions detected.
    """
    flags = []
    drops = {
        "mean_recall_at_1": current.mean_recall_at_1 - baseline.mean_recall_at_1,
        "mean_recall_at_3": current.mean_recall_at_3 - baseline.mean_recall_at_3,
        "mean_recall_at_5": current.mean_recall_at_5 - baseline.mean_recall_at_5,
        "mean_mrr": current.mean_mrr - baseline.mean_mrr,
        "mean_ndcg": current.mean_ndcg - baseline.mean_ndcg,
    }
    for metric, delta in drops.items():
        if delta < -drop_threshold_pp / 100.0:
            flags.append(
                f"REGRESSION on {metric}: dropped {abs(delta) * 100:.1f}pp "
                f"(baseline {getattr(baseline, metric):.3f} -> current {getattr(current, metric):.3f})"
            )
    if current.mean_latency_ms > baseline.mean_latency_ms * 1.5:
        flags.append(
            f"LATENCY REGRESSION: {current.mean_latency_ms:.1f}ms vs baseline "
            f"{baseline.mean_latency_ms:.1f}ms (1.5x slower)"
        )
    return flags


# ============================================================
# Reporting
# ============================================================


def render_report(
    diagnostic: SystemDiagnostic,
    scores: list[QueryScore],
    title: str = "Substrate Self-Index Benchmark Report",
    notes: str = "",
) -> str:
    """Human-readable markdown report of the diagnostic + per-query scores.

    Sealed queries are reported only by qid + aggregate; the query text and
    expected-answer details stay private until Day 2-3 joint validation.
    """
    lines = []
    lines.append(f"# {title}")
    if notes:
        lines.append("")
        lines.append(notes)
    lines.append("")
    lines.append("## Aggregate metrics")
    lines.append("")
    lines.append(f"- queries scored: **{diagnostic.n_queries}** ({diagnostic.n_sealed} sealed)")
    lines.append(f"- mean recall@1: **{diagnostic.mean_recall_at_1:.3f}**")
    lines.append(f"- mean recall@3: {diagnostic.mean_recall_at_3:.3f}")
    lines.append(f"- mean recall@5: {diagnostic.mean_recall_at_5:.3f}")
    lines.append(f"- mean MRR: **{diagnostic.mean_mrr:.3f}**")
    lines.append(f"- mean NDCG@10: {diagnostic.mean_ndcg:.3f}")
    lines.append(f"- mean relations recall: {diagnostic.mean_relations_recall:.3f}")
    lines.append(f"- mean latency: {diagnostic.mean_latency_ms:.1f} ms / p95 {diagnostic.p95_latency_ms:.1f} ms")
    lines.append(f"- exact-atom matches: {diagnostic.n_exact_matches} / {diagnostic.n_queries}")
    if diagnostic.substrate_wins or diagnostic.llm_wins or diagnostic.ties:
        lines.append("")
        lines.append("## Substrate vs LLM (head-to-head by NDCG)")
        lines.append("")
        lines.append(f"- substrate wins: **{diagnostic.substrate_wins}**")
        lines.append(f"- LLM wins: {diagnostic.llm_wins}")
        lines.append(f"- ties: {diagnostic.ties}")
    lines.append("")
    lines.append("## Failure-mode histogram")
    lines.append("")
    if diagnostic.failure_histogram:
        for mode, count in sorted(diagnostic.failure_histogram.items(), key=lambda x: -x[1]):
            pct = 100.0 * count / max(1, diagnostic.n_queries)
            lines.append(f"- `{mode}`: {count} ({pct:.0f}%)")
    else:
        lines.append("- (none)")
    lines.append("")
    lines.append("## Recommendations")
    lines.append("")
    for r in diagnostic.recommendations:
        lines.append(f"- {r}")
    lines.append("")
    lines.append("## Per-query scores")
    lines.append("")
    lines.append("| qid | type | sealed | r@1 | r@3 | mrr | ndcg | rel | latency | failure |")
    lines.append("|---|---|---|---|---|---|---|---|---|---|")
    for s in scores:
        qid_display = s.qid if not s.sealed else f"SEALED ({s.qid[:6]})"
        lines.append(
            f"| {qid_display} | {s.query_type.value} | {'Y' if s.sealed else 'N'} | "
            f"{s.recall_at_1:.0f} | {s.recall_at_3:.0f} | {s.mrr:.2f} | {s.ndcg_at_10:.2f} | "
            f"{s.relations_recall:.2f} | {s.latency_ms:.0f}ms | {s.failure_mode.value} |"
        )
    return "\n".join(lines)
