"""Connectivity-as-operation: Hebbian spreading activation vs nested VSA retrieval.

The same knowledge graph is encoded two ways:
1. VSA form: each related-pair fact as a bound structure, all facts bundled.
2. Hebbian form: each fact reinforces a co-activation weight between the two entities.

Then queries at hop distance k = 1, 2, 3:
- VSA mode tries to recover k-hop neighbors via nested unbinding (hits the depth ceiling).
- Hebbian mode propagates activation through the weight matrix k times.

If Hebbian wins for k >= 2 while VSA wins for k = 1, we have empirical evidence that
graph-connectivity dynamics enable a class of operations the substrate algebra structurally
cannot perform - the connectivity-as-computation finding the original goal targeted.
"""

from __future__ import annotations

import json
import math

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import torch  # noqa: E402

from hdlab import atoms, binding, bundling, experiment, learning, modulators, tracing  # noqa: E402




DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
N_ENTITIES = 50
N_FACTS = 150
N_HOPS_TESTED = [1, 2, 3, 4]
TRIALS_PER_HOP = 30
N_SUBSTRATE = 4096
SEED = 42
NUM_HEBBIAN_TRAINING_PASSES = 50  # how many times to re-train each fact pair


def build_knowledge_graph(n_entities: int, n_facts: int, gen: torch.Generator) -> list[tuple[int, int]]:
    """A random graph of n_facts (undirected) entity pairs, sampled without self-loops or dupes."""
    pairs = set()
    while len(pairs) < n_facts:
        a = int(torch.randint(0, n_entities, (1,), generator=gen).item())
        b = int(torch.randint(0, n_entities, (1,), generator=gen).item())
        if a == b:
            continue
        edge = (a, b) if a < b else (b, a)
        pairs.add(edge)
    return list(pairs)


def find_k_hop_neighbors(graph: list[tuple[int, int]], n_entities: int, source: int, k: int) -> set[int]:
    """BFS k hops out from source. Returns the set of entities at exactly hop distance k."""
    adj: dict[int, set[int]] = {i: set() for i in range(n_entities)}
    for a, b in graph:
        adj[a].add(b)
        adj[b].add(a)
    current = {source}
    visited = {source}
    for _ in range(k):
        next_level = set()
        for x in current:
            for y in adj[x]:
                if y not in visited:
                    next_level.add(y)
                    visited.add(y)
        current = next_level
        if not current:
            break
    return current


def encode_vsa_facts(
    graph: list[tuple[int, int]],
    entity_vecs: torch.Tensor,
    related_role: torch.Tensor,  # unused now, kept for API compat
    n: int,
) -> torch.Tensor:
    """Encode the knowledge graph as Plate's classic associative memory: each undirected
    fact (a, b) contributes bind(a, b) + bind(b, a). Then unbind(knowledge, source) returns
    approximately the sum of source's neighbors (plus crosstalk).
    """
    fact_vectors: list[torch.Tensor] = []
    for a, b in graph:
        fact_vectors.append(binding.bind(entity_vecs[a], entity_vecs[b]))
        fact_vectors.append(binding.bind(entity_vecs[b], entity_vecs[a]))
    return bundling.bundle(torch.stack(fact_vectors))


def vsa_query_khop(
    knowledge: torch.Tensor,
    source_idx: int,
    entity_vecs: torch.Tensor,
    k_hops: int,
    top_k: int,
) -> list[int]:
    """k-hop spreading via repeated VSA unbinding. After k unbinds, the result vector
    approximates the sum of entities reachable in exactly k hops (with mounting crosstalk).
    """
    n = entity_vecs.shape[-1]
    current = entity_vecs[source_idx]
    for _ in range(k_hops):
        current = binding.unbind(knowledge, current)
    sims = (entity_vecs @ current.conj()).real / n
    ranked = sims.argsort(descending=True).tolist()
    return ranked[:top_k]


def hebbian_spread(
    weight_matrix: torch.Tensor,
    source_idx: int,
    k_hops: int,
    n_entities: int,
) -> torch.Tensor:
    """Spread activation k hops from source. Returns activation vector over all entities."""
    activation = torch.zeros(n_entities, dtype=torch.float32, device=DEVICE)
    activation[source_idx] = 1.0
    for _ in range(k_hops):
        new_act = weight_matrix @ activation
        # Don't let the source dominate after self-loops; zero it out, normalize.
        new_act[source_idx] = 0.0
        s = new_act.sum()
        if float(s) > 0:
            new_act = new_act / s
        activation = new_act
    return activation


def workload(ctx: experiment.ExperimentContext) -> dict:
    n = N_SUBSTRATE
    gen = ctx.generator
    quiet_bus = tracing.TraceBus(enabled=False)

    with tracing.using(quiet_bus):
        # 1. Build the knowledge graph (entity pairs)
        graph = build_knowledge_graph(N_ENTITIES, N_FACTS, gen)

        # 2. Generate FHRR atoms for each entity, and a related_role atom
        entity_vecs = torch.stack([atoms.make_atom_fhrr(n, gen) for _ in range(N_ENTITIES)]).to(DEVICE)
        related_role = atoms.make_atom_fhrr(n, gen)

        # 3. Build VSA form (single bundled structure)
        knowledge = encode_vsa_facts(graph, entity_vecs, related_role, n)

        # 4. Build Hebbian form: train co-activation for each fact pair, many passes for saturation
        h = learning.HebbianAssociations(decay=0.01)
        entity_names = [f"e{i:03d}" for i in range(N_ENTITIES)]
        with modulators.using(reward=1.0, arousal=1.0):
            for _ in range(NUM_HEBBIAN_TRAINING_PASSES):
                for a, b in graph:
                    h.update([entity_names[a], entity_names[b]])

        # Build the dense weight matrix from the Hebbian state
        W = torch.zeros((N_ENTITIES, N_ENTITIES), dtype=torch.float32, device=DEVICE)
        for i in range(N_ENTITIES):
            for j in range(N_ENTITIES):
                if i != j:
                    W[i, j] = h.weight(entity_names[i], entity_names[j])

        # Row-normalize so each row sums to 1 (probability of transition)
        row_sums = W.sum(dim=1, keepdim=True)
        row_sums = torch.where(row_sums > 0, row_sums, torch.ones_like(row_sums))
        W_norm = W / row_sums

        # 5. For each hop count, measure recovery rates of both modes
        results: dict[int, dict[str, float]] = {}
        for k in N_HOPS_TESTED:
            vsa_hits = 0
            vsa_attempts = 0
            heb_hits = 0
            heb_attempts = 0
            heb_top1_in_set = 0

            for _ in range(TRIALS_PER_HOP):
                source = int(torch.randint(0, N_ENTITIES, (1,), generator=gen).item())
                truth_set = find_k_hop_neighbors(graph, N_ENTITIES, source, k)
                if not truth_set:
                    continue

                # VSA mode: repeated unbinding (k-hop spreading via the algebra)
                top_k_vsa = vsa_query_khop(
                    knowledge=knowledge,
                    source_idx=source,
                    entity_vecs=entity_vecs,
                    k_hops=k,
                    top_k=len(truth_set) + 1,
                )
                # Score: of the top-|truth_set|+1 entities returned, how many are in truth_set?
                top_k_vsa_excluding_source = [t for t in top_k_vsa if t != source][: len(truth_set)]
                hits = len([t for t in top_k_vsa_excluding_source if t in truth_set])
                vsa_hits += hits
                vsa_attempts += len(truth_set)

                # Hebbian spreading mode
                activation = hebbian_spread(W_norm, source, k, N_ENTITIES)
                # Rank entities by activation
                ranked = activation.argsort(descending=True).tolist()
                # Top-|truth_set| accuracy
                top_truth = [r for r in ranked if r != source][: len(truth_set)]
                hits = len([t for t in top_truth if t in truth_set])
                heb_hits += hits
                heb_attempts += len(truth_set)
                # Top-1 in truth set?
                top1 = next(r for r in ranked if r != source)
                if top1 in truth_set:
                    heb_top1_in_set += 1

            results[k] = {
                "vsa_recall": vsa_hits / max(vsa_attempts, 1),
                "hebbian_recall": heb_hits / max(heb_attempts, 1),
                "hebbian_top1_in_set_rate": heb_top1_in_set / TRIALS_PER_HOP,
            }

    # Build comparison plot
    def page_compare(pdf):
        fig, ax = plt.subplots(figsize=(11, 8.5))
        hops = sorted(results.keys())
        vsa_recall = [results[k]["vsa_recall"] for k in hops]
        heb_recall = [results[k]["hebbian_recall"] for k in hops]
        heb_top1 = [results[k]["hebbian_top1_in_set_rate"] for k in hops]
        ax.plot(hops, vsa_recall, marker="o", color="firebrick", linewidth=2,
                label="VSA direct query (recall)")
        ax.plot(hops, heb_recall, marker="s", color="seagreen", linewidth=2,
                label="Hebbian spreading (recall@|truth_set|)")
        ax.plot(hops, heb_top1, marker="^", color="steelblue", linewidth=2,
                label="Hebbian spreading (top-1 in truth set)")
        ax.set_xlabel("hop distance from source")
        ax.set_ylabel("retrieval quality")
        ax.set_title(
            f"Connectivity vs structure: VSA query vs Hebbian spread\n"
            f"(N={N_SUBSTRATE}, {N_ENTITIES} entities, {N_FACTS} facts, "
            f"{NUM_HEBBIAN_TRAINING_PASSES} training passes)"
        )
        ax.set_ylim(-0.05, 1.05)
        ax.set_xticks(hops)
        ax.axhline(0.5, color="black", linestyle="--", alpha=0.3)
        ax.legend(loc="best")
        ax.grid(True, alpha=0.3)
        pdf.savefig(fig)
        plt.close(fig)

    return {
        "n_entities": N_ENTITIES,
        "n_facts": N_FACTS,
        "n_substrate": N_SUBSTRATE,
        "trials_per_hop": TRIALS_PER_HOP,
        "n_hops_tested": N_HOPS_TESTED,
        "num_hebbian_training_passes": NUM_HEBBIAN_TRAINING_PASSES,
        "results_by_hop": results,
        "headline": (
            f"1-hop: VSA={results[1]['vsa_recall']:.2f}, Hebbian={results[1]['hebbian_recall']:.2f}; "
            f"3-hop: VSA={results[3]['vsa_recall']:.2f}, Hebbian={results[3]['hebbian_recall']:.2f}"
        ),
        "_pdf_extras": [page_compare],
    }


def main() -> None:
    spec = experiment.ExperimentSpec(name="exp_connectivity_multihop", seed=SEED, n=N_SUBSTRATE)
    result = experiment.run(spec, workload)
    print(json.dumps(result.metrics, indent=2, default=str))


if __name__ == "__main__":
    main()
