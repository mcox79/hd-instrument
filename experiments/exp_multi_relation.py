"""Multi-relation graph traversal: composing several connection types via vector + graph ops.

Tests the user's hypothesis that connections are orthogonal to the substrate -- multiple
relation graphs over the same entities should compose, and queries combining several relations
should work even when a single-substrate VSA encoding cannot hold all the relations cleanly.

Setup:
  - K entities (people)
  - R relation types (parent_of, spouse_of, lives_in, works_at, owns, ...) each as a separate
    Hebbian sub-graph over the same K entities
  - Multi-hop queries that compose several relations:
      Q1 (1-hop): "X's parent" -- single relation traversal
      Q2 (2-hop): "X's parent's spouse" -- compose two relations
      Q3 (2-hop, different): "where X's parent lives" -- different relation pair
      Q4 (3-hop): "where X's parent's spouse works"
      Q5 (3-hop): "owner of where X's parent's spouse works"

For each query type, compare:
  1. Multi-relation graph traversal (Hebbian spreading per relation, sequentially)
  2. Single-substrate VSA encoding all relations in one bundle, query via VSA algebra

Hypothesis: graph traversal scales gracefully with composition depth and relation count;
single-substrate VSA degrades because all R relations compete in the same N-dim bundle.
"""

from __future__ import annotations

import json
import math

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import torch  # noqa: E402

from hdlab import atoms, binding, bundling, experiment, tracing  # noqa: E402




DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
N_SUBSTRATE = 4096
N_ENTITIES = 30
RELATION_NAMES = ["parent_of", "spouse_of", "lives_in", "works_at", "owns", "friend_of"]
TRIALS_PER_QUERY = 30
EDGES_PER_RELATION = 25  # how many facts per relation type


def build_relation_graph(
    n_entities: int,
    edges_per_relation: int,
    gen: torch.Generator,
) -> dict[str, list[tuple[int, int]]]:
    """For each relation, sample edges (a -> b) without self-loops or duplicates."""
    graphs: dict[str, list[tuple[int, int]]] = {}
    for rel in RELATION_NAMES:
        pairs: set[tuple[int, int]] = set()
        while len(pairs) < edges_per_relation:
            a = int(torch.randint(0, n_entities, (1,), generator=gen).item())
            b = int(torch.randint(0, n_entities, (1,), generator=gen).item())
            if a == b:
                continue
            pairs.add((a, b))
        graphs[rel] = list(pairs)
    return graphs


def build_relation_matrices(
    graphs: dict[str, list[tuple[int, int]]],
    n_entities: int,
) -> dict[str, torch.Tensor]:
    """For each relation, build an n_entities x n_entities transition matrix.
    M[i, j] = 1 if (i, j) is an edge, else 0. Row-normalize to get probabilities.
    """
    matrices: dict[str, torch.Tensor] = {}
    for rel, edges in graphs.items():
        M = torch.zeros((n_entities, n_entities), dtype=torch.float32, device=DEVICE)
        for a, b in edges:
            M[a, b] = 1.0
        row_sum = M.sum(dim=1, keepdim=True)
        row_sum = torch.where(row_sum > 0, row_sum, torch.ones_like(row_sum))
        matrices[rel] = M / row_sum
    return matrices


def graph_query(
    source_idx: int,
    relation_sequence: list[str],
    matrices: dict[str, torch.Tensor],
    n_entities: int,
) -> torch.Tensor:
    """Multi-hop graph traversal: start at source, apply each relation in turn."""
    activation = torch.zeros(n_entities, dtype=torch.float32, device=DEVICE)
    activation[source_idx] = 1.0
    for rel in relation_sequence:
        activation = matrices[rel].T @ activation  # M.T because M[i,j]=row i to col j
        # Re-normalize (defensive)
        s = activation.sum()
        if float(s) > 0:
            activation = activation / s
    return activation


def graph_truth(
    source_idx: int,
    relation_sequence: list[str],
    graphs: dict[str, list[tuple[int, int]]],
    n_entities: int,
) -> set[int]:
    """True set of entities reachable from source via relation sequence."""
    current = {source_idx}
    for rel in relation_sequence:
        adj: dict[int, set[int]] = {i: set() for i in range(n_entities)}
        for a, b in graphs[rel]:
            adj[a].add(b)
        next_set = set()
        for x in current:
            next_set.update(adj[x])
        current = next_set
        if not current:
            break
    return current


def build_vsa_encoding(
    graphs: dict[str, list[tuple[int, int]]],
    entity_vecs: torch.Tensor,
    relation_atoms: dict[str, torch.Tensor],
    n: int,
) -> torch.Tensor:
    """Encode all relations in one VSA bundle.
    For each fact (a, rel, b): bind(rel_atom, bind(a, b)).
    Then bundle all facts together.
    """
    facts: list[torch.Tensor] = []
    for rel, edges in graphs.items():
        for a, b in edges:
            facts.append(binding.bind(relation_atoms[rel], binding.bind(entity_vecs[a], entity_vecs[b])))
    return bundling.bundle(torch.stack(facts))


def vsa_query(
    source_idx: int,
    relation_sequence: list[str],
    knowledge: torch.Tensor,
    entity_vecs: torch.Tensor,
    relation_atoms: dict[str, torch.Tensor],
    n: int,
) -> int:
    """Multi-hop VSA query. For each relation, unbind by relation_atom and current entity."""
    n_entities = entity_vecs.shape[0]
    current = entity_vecs[source_idx]
    for rel in relation_sequence:
        # The relation fact stored as bind(rel_atom, bind(entity_a, entity_b))
        # Unbind by rel_atom first to get bind(entity_a, entity_b)
        unbound_rel = binding.unbind(knowledge, relation_atoms[rel])
        # Then unbind by current entity to get the connected entity
        unbound_entity = binding.unbind(unbound_rel, current)
        # Cleanup against entity pool to advance
        sims = (entity_vecs @ unbound_entity.conj()).real / n
        next_idx = int(sims.argmax().item())
        current = entity_vecs[next_idx]
    # Final cleanup
    sims = (entity_vecs @ current.conj()).real / n
    return int(sims.argmax().item())


def workload(ctx: experiment.ExperimentContext) -> dict:
    gen = ctx.generator
    quiet_bus = tracing.TraceBus(enabled=False)
    n = N_SUBSTRATE

    with tracing.using(quiet_bus):
        # Build entities and relation atoms
        entity_vecs = torch.stack([atoms.make_atom_fhrr(n, gen) for _ in range(N_ENTITIES)]).to(DEVICE)
        relation_atoms = {rel: atoms.make_atom_fhrr(n, gen) for rel in RELATION_NAMES}

        # Build the multi-relation knowledge graph
        graphs = build_relation_graph(N_ENTITIES, EDGES_PER_RELATION, gen)
        matrices = build_relation_matrices(graphs, N_ENTITIES)

        # Build single-substrate VSA encoding of all facts
        knowledge = build_vsa_encoding(graphs, entity_vecs, relation_atoms, n)

        # Define query types: relation sequences of varying length
        query_types = {
            "1-hop (parent)":      ["parent_of"],
            "1-hop (spouse)":      ["spouse_of"],
            "2-hop (par-spouse)":  ["parent_of", "spouse_of"],
            "2-hop (par-lives)":   ["parent_of", "lives_in"],
            "3-hop (par-sp-work)": ["parent_of", "spouse_of", "works_at"],
            "3-hop (4 rel chain)": ["parent_of", "spouse_of", "works_at", "owns"],
        }

        # Evaluate
        results: dict[str, dict] = {}
        for query_name, rel_seq in query_types.items():
            graph_correct = 0
            vsa_correct = 0
            graph_in_set = 0  # graph's top-1 in truth set
            attempts = 0
            for _ in range(TRIALS_PER_QUERY):
                src = int(torch.randint(0, N_ENTITIES, (1,), generator=gen).item())
                truth_set = graph_truth(src, rel_seq, graphs, N_ENTITIES)
                if not truth_set:
                    continue
                # Graph traversal
                activation = graph_query(src, rel_seq, matrices, N_ENTITIES)
                ranked = activation.argsort(descending=True).tolist()
                top_truth = [r for r in ranked if r != src][: len(truth_set)]
                graph_correct += len([t for t in top_truth if t in truth_set])
                if ranked[0] in truth_set:
                    graph_in_set += 1
                # VSA
                vsa_top = vsa_query(src, rel_seq, knowledge, entity_vecs, relation_atoms, n)
                if vsa_top in truth_set:
                    vsa_correct += 1
                attempts += 1

            if attempts == 0:
                continue
            total_truth = sum(
                len(graph_truth(int(torch.randint(0, N_ENTITIES, (1,), generator=gen).item()), rel_seq, graphs, N_ENTITIES))
                for _ in range(0)
            )
            results[query_name] = {
                "graph_recall_at_truthset_size": graph_correct / max(attempts * len(rel_seq), 1),
                "graph_top1_in_set": graph_in_set / attempts,
                "vsa_top1_in_set": vsa_correct / attempts,
                "attempts": attempts,
                "n_relations": len(rel_seq),
            }

    headline = (
        f"1-hop: graph_top1={results['1-hop (parent)']['graph_top1_in_set']:.2f}, "
        f"vsa_top1={results['1-hop (parent)']['vsa_top1_in_set']:.2f}; "
        f"3-hop: graph_top1={results['3-hop (par-sp-work)']['graph_top1_in_set']:.2f}, "
        f"vsa_top1={results['3-hop (par-sp-work)']['vsa_top1_in_set']:.2f}"
    )

    def page_compare(pdf):
        fig, ax = plt.subplots(figsize=(11, 8.5))
        names = list(results.keys())
        graph_vals = [results[n]["graph_top1_in_set"] for n in names]
        vsa_vals = [results[n]["vsa_top1_in_set"] for n in names]
        x = list(range(len(names)))
        width = 0.4
        ax.bar([i - width / 2 for i in x], graph_vals, width, color="seagreen", label="Multi-relation graph (Hebbian per relation)")
        ax.bar([i + width / 2 for i in x], vsa_vals, width, color="firebrick", label="Single-substrate VSA (all relations in one bundle)")
        ax.set_xticks(x)
        ax.set_xticklabels(names, rotation=20, ha="right")
        ax.set_ylabel("top-1 in truth set")
        ax.set_title(
            f"Multi-relation reasoning: {N_ENTITIES} entities, "
            f"{len(RELATION_NAMES)} relations x {EDGES_PER_RELATION} edges each at N={N_SUBSTRATE}"
        )
        ax.axhline(1.0, color="black", linestyle="--", alpha=0.3, label="perfect")
        ax.axhline(0.5, color="gray", linestyle="--", alpha=0.3, label="50%")
        ax.legend(loc="best", fontsize=9)
        ax.grid(True, alpha=0.3, axis="y")
        ax.set_ylim(-0.05, 1.05)
        plt.tight_layout()
        pdf.savefig(fig)
        plt.close(fig)

    return {
        "n_substrate": N_SUBSTRATE,
        "n_entities": N_ENTITIES,
        "relation_names": RELATION_NAMES,
        "edges_per_relation": EDGES_PER_RELATION,
        "trials_per_query": TRIALS_PER_QUERY,
        "total_facts": EDGES_PER_RELATION * len(RELATION_NAMES),
        "results": results,
        "headline": headline,
        "_pdf_extras": [page_compare],
    }


def main() -> None:
    spec = experiment.ExperimentSpec(name="exp_multi_relation", seed=42, n=N_SUBSTRATE)
    result = experiment.run(spec, workload)
    print(json.dumps(result.metrics, indent=2, default=str))


if __name__ == "__main__":
    main()
