"""Traceable multi-hop probe: instrument one concrete query end-to-end + ablation diff.

The point of this experiment is not the accuracy number. The point is to demonstrate that
the observability layer (semantic events + ablation context + snapshots) lets you see
*exactly* which connections carried a multi-hop query, and to causally verify by removing
them and re-running.

Setup: a small, hand-constructed knowledge graph over 12 people with 4 relations. Then:
  Run A: full query, all relations active.
  Run B: same query, ablate one relation -> show that the answer changes.
  Run C: same query, ablate a specific edge -> show that the answer changes in a different way.

Each run is a separate tracing.query_span; the trace can be filtered per-run in the dashboard.
"""

from __future__ import annotations

import json

import torch

from hdlab import ablation, experiment, learning, modulators, semantic, snapshots, tracing




DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
SEED = 7

# Hand-constructed graph so we can name a definite answer.
ENTITIES = [
    "alice", "bob", "carol", "dave",
    "eve", "frank", "grace", "henry",
    "iris", "jack", "kate", "leo",
]

# Each relation is asymmetric: (src, dst).
GRAPH: dict[str, list[tuple[str, str]]] = {
    "parent_of": [
        ("alice", "bob"),
        ("bob", "carol"),
        ("dave", "eve"),
        ("eve", "frank"),
        ("grace", "henry"),
    ],
    "spouse_of": [
        ("bob", "iris"),
        ("eve", "jack"),
        ("henry", "kate"),
    ],
    "works_at": [
        ("iris", "leo"),     # leo is treated as an "employer" entity
        ("jack", "alice"),
        ("kate", "dave"),
    ],
    "lives_in": [
        ("bob", "carol"),
        ("iris", "frank"),
    ],
}

# Query: alice -> parent_of -> bob; bob -> spouse_of -> iris; iris -> works_at -> leo.
QUERY = {
    "source": "alice",
    "relation_chain": ["parent_of", "spouse_of", "works_at"],
    "expected": "leo",
}


def _adj(graph: dict[str, list[tuple[str, str]]], relation: str) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for src, dst in graph[relation]:
        out.setdefault(src, []).append(dst)
    return out


def graph_truth(source: str, relation_chain: list[str]) -> set[str]:
    current = {source}
    for rel in relation_chain:
        adj = _adj(GRAPH, rel)
        nxt: set[str] = set()
        for x in current:
            nxt.update(adj.get(x, []))
        current = nxt
    return current


def run_query_traced(
    query_id: str,
    hebbian: dict[str, learning.HebbianAssociations],
    source: str,
    relation_chain: list[str],
) -> tuple[str | None, list[str]]:
    """Multi-hop graph spread with semantic event emission at every connection.

    Returns (final_answer, hops_path). Answer is None if no edge fired.
    """
    with tracing.query_span(
        query_id,
        kind="multi_hop_relation_chain",
        source=source,
        chain=",".join(relation_chain),
    ):
        snapshots.capture("pre-query", hebbian=hebbian["parent_of"], extra={"source": source})

        frontier = {source: 1.0}
        path: list[str] = [source]

        for hop_idx, rel in enumerate(relation_chain):
            semantic.hop(hop_idx, current_frontier=list(frontier.keys()), relation=rel)

            if ablation.is_relation_ablated(rel):
                semantic.relation_activated(rel, contribution=0.0, hop_idx=hop_idx, n_edges_fired=0)
                frontier = {}
                break

            h = hebbian[rel]
            next_frontier: dict[str, float] = {}
            edges_fired = 0
            for src, weight_in in frontier.items():
                for (a, b), _w in list(h._weights.items()):
                    if a != src and b != src:
                        continue
                    dst = b if a == src else a
                    if ablation.is_edge_ablated(rel, src, dst):
                        continue
                    w = h.weight(src, dst)
                    if w <= 0:
                        continue
                    semantic.edge_traversed(rel, src, dst, weight=w, hop_idx=hop_idx)
                    next_frontier[dst] = next_frontier.get(dst, 0.0) + weight_in * w
                    edges_fired += 1

            contribution = sum(next_frontier.values())
            semantic.relation_activated(rel, contribution=contribution, hop_idx=hop_idx, n_edges_fired=edges_fired)
            # Cleanup: pick the dominant entity
            if next_frontier:
                best = max(next_frontier.items(), key=lambda kv: kv[1])
                semantic.cleanup_hit(best[0], score=best[1] / max(contribution, 1e-9), threshold=0.0, hop_idx=hop_idx, accepted=True)
                path.append(best[0])
                # Normalize and keep the top entity as the new frontier
                total = contribution
                frontier = {k: v / total for k, v in next_frontier.items()}
            else:
                semantic.cleanup_hit(None, score=0.0, threshold=0.0, hop_idx=hop_idx, accepted=False)
                frontier = {}
                break

        answer = max(frontier.items(), key=lambda kv: kv[1])[0] if frontier else None
        confidence = max(frontier.values()) if frontier else 0.0
        semantic.query_answer(answer, confidence=confidence, hops_taken=len(path) - 1)
        snapshots.capture("post-query", hebbian=hebbian["parent_of"], extra={"answer": answer})
        return answer, path


def _train_hebbian_from_graph() -> dict[str, learning.HebbianAssociations]:
    """One HebbianAssociations per relation, trained from the hand-constructed graph."""
    h: dict[str, learning.HebbianAssociations] = {}
    for rel, edges in GRAPH.items():
        ha = learning.HebbianAssociations(decay=0.0)
        with modulators.using(reward=1.0, arousal=1.0):
            for _ in range(5):  # repeated reinforcement so weights are clearly positive
                for src, dst in edges:
                    ha.update([src, dst])
        h[rel] = ha
    return h


def workload(ctx: experiment.ExperimentContext) -> dict:
    hebbian = _train_hebbian_from_graph()

    truth = graph_truth(QUERY["source"], QUERY["relation_chain"])

    # Run A: no ablation
    ans_a, path_a = run_query_traced("q-A-full", hebbian, QUERY["source"], QUERY["relation_chain"])

    # Run B: ablate the spouse_of relation
    with ablation.relation("spouse_of"):
        ans_b, path_b = run_query_traced("q-B-no-spouse", hebbian, QUERY["source"], QUERY["relation_chain"])

    # Run C: ablate a single edge (iris -> leo)
    with ablation.edges("works_at", [("iris", "leo")]):
        ans_c, path_c = run_query_traced("q-C-no-iris-leo", hebbian, QUERY["source"], QUERY["relation_chain"])

    runs = {
        "A_full": {"answer": ans_a, "path": path_a, "matches_truth": ans_a in truth},
        "B_ablate_relation_spouse_of": {"answer": ans_b, "path": path_b, "matches_truth": ans_b in truth if ans_b else False},
        "C_ablate_edge_iris_leo": {"answer": ans_c, "path": path_c, "matches_truth": ans_c in truth if ans_c else False},
    }

    causality_demonstrated = (
        runs["A_full"]["matches_truth"]
        and runs["B_ablate_relation_spouse_of"]["answer"] != ans_a
        and runs["C_ablate_edge_iris_leo"]["answer"] != ans_a
    )

    return {
        "entities": ENTITIES,
        "graph": {rel: edges for rel, edges in GRAPH.items()},
        "query": QUERY,
        "truth_set": sorted(truth),
        "runs": runs,
        "causality_demonstrated": causality_demonstrated,
        "headline": (
            f"A={ans_a} (truth match={runs['A_full']['matches_truth']}); "
            f"B (no spouse_of)={ans_b}; "
            f"C (no iris->leo)={ans_c}; "
            f"causal observability: {causality_demonstrated}"
        ),
    }


def main() -> None:
    spec = experiment.ExperimentSpec(name="exp_traceable_multi_hop", seed=SEED, n=1024)
    result = experiment.run(spec, workload)
    print(json.dumps(result.metrics, indent=2, default=str))


if __name__ == "__main__":
    main()
