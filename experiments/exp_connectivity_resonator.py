"""Three-mode multi-hop comparison: VSA algebra vs Hebbian spread vs resonator refinement.

The resonator/Hopfield-style mode adds a cleanup step at every iteration. After each unbind,
project onto entity-space via similarity, then form a softmax-weighted sum of entity atoms
as the next query vector. This is conceptually a soft cleanup at every hop, which kills the
per-bind crosstalk that hurts pure VSA-algebra spreading.

Inspired by:
- Frady, Kent, Olshausen, Sommer (2020) - Resonator networks for VSA decomposition
- Ramsauer et al (2020) - Modern Hopfield networks, attention-equivalence
- Standard graph signal processing for the Hebbian baseline

Same knowledge graph and protocol as exp_connectivity_multihop.py for direct comparison.
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
N_HOPS_TESTED = [1, 2, 3, 4, 5]
TRIALS_PER_HOP = 30
N_SUBSTRATE = 4096
SEED = 42
NUM_HEBBIAN_TRAINING_PASSES = 50
RESONATOR_TEMPERATURE = 5.0  # softmax sharpness; higher = more like top-1 cleanup


def build_knowledge_graph(n_entities, n_facts, gen):
    pairs = set()
    while len(pairs) < n_facts:
        a = int(torch.randint(0, n_entities, (1,), generator=gen).item())
        b = int(torch.randint(0, n_entities, (1,), generator=gen).item())
        if a == b:
            continue
        edge = (a, b) if a < b else (b, a)
        pairs.add(edge)
    return list(pairs)


def find_k_hop_neighbors(graph, n_entities, source, k):
    adj = {i: set() for i in range(n_entities)}
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


def encode_vsa_facts(graph, entity_vecs):
    fact_vectors = []
    for a, b in graph:
        fact_vectors.append(binding.bind(entity_vecs[a], entity_vecs[b]))
        fact_vectors.append(binding.bind(entity_vecs[b], entity_vecs[a]))
    return bundling.bundle(torch.stack(fact_vectors))


def vsa_query_khop(knowledge, source_idx, entity_vecs, k_hops, top_k):
    """Pure VSA mode: k repeated unbinds. No cleanup between steps."""
    n = entity_vecs.shape[-1]
    current = entity_vecs[source_idx]
    for _ in range(k_hops):
        current = binding.unbind(knowledge, current)
    sims = (entity_vecs @ current.conj()).real / n
    return sims.argsort(descending=True).tolist()[:top_k]


def resonator_query_khop(knowledge, source_idx, entity_vecs, k_hops, top_k, temperature):
    """Resonator mode: at each step, soft-cleanup the unbind result by projecting onto entity space
    via similarity, then form a softmax-weighted sum of entity atoms as the next query.
    """
    n = entity_vecs.shape[-1]
    current = entity_vecs[source_idx]
    for _ in range(k_hops):
        raw = binding.unbind(knowledge, current)
        # Soft cleanup: similarity vs every entity, softmax to get weights, weighted sum back to entity space
        sims = (entity_vecs @ raw.conj()).real / n
        weights = torch.softmax(sims * temperature, dim=0)
        # weighted sum of entity vectors (complex valued)
        current = (weights.unsqueeze(-1) * entity_vecs).sum(dim=0)
    final_sims = (entity_vecs @ current.conj()).real / n
    return final_sims.argsort(descending=True).tolist()[:top_k]


def hebbian_spread(weight_matrix, source_idx, k_hops, n_entities):
    activation = torch.zeros(n_entities, dtype=torch.float32, device=DEVICE)
    activation[source_idx] = 1.0
    for _ in range(k_hops):
        new_act = weight_matrix @ activation
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
        graph = build_knowledge_graph(N_ENTITIES, N_FACTS, gen)

        entity_vecs = torch.stack([atoms.make_atom_fhrr(n, gen) for _ in range(N_ENTITIES)]).to(DEVICE)

        knowledge = encode_vsa_facts(graph, entity_vecs)

        # Hebbian form
        h = learning.HebbianAssociations(decay=0.01)
        entity_names = [f"e{i:03d}" for i in range(N_ENTITIES)]
        with modulators.using(reward=1.0, arousal=1.0):
            for _ in range(NUM_HEBBIAN_TRAINING_PASSES):
                for a, b in graph:
                    h.update([entity_names[a], entity_names[b]])
        W = torch.zeros((N_ENTITIES, N_ENTITIES), dtype=torch.float32, device=DEVICE)
        for i in range(N_ENTITIES):
            for j in range(N_ENTITIES):
                if i != j:
                    W[i, j] = h.weight(entity_names[i], entity_names[j])
        row_sums = W.sum(dim=1, keepdim=True)
        row_sums = torch.where(row_sums > 0, row_sums, torch.ones_like(row_sums))
        W_norm = W / row_sums

        results: dict[int, dict[str, float]] = {}
        for k in N_HOPS_TESTED:
            vsa_hits = 0
            res_hits = 0
            heb_hits = 0
            attempts = 0

            for _ in range(TRIALS_PER_HOP):
                source = int(torch.randint(0, N_ENTITIES, (1,), generator=gen).item())
                truth_set = find_k_hop_neighbors(graph, N_ENTITIES, source, k)
                if not truth_set:
                    continue

                # VSA mode
                top = [t for t in vsa_query_khop(knowledge, source, entity_vecs, k, len(truth_set) + 1) if t != source][: len(truth_set)]
                vsa_hits += len([t for t in top if t in truth_set])

                # Resonator mode
                top = [t for t in resonator_query_khop(knowledge, source, entity_vecs, k, len(truth_set) + 1, RESONATOR_TEMPERATURE) if t != source][: len(truth_set)]
                res_hits += len([t for t in top if t in truth_set])

                # Hebbian mode
                activation = hebbian_spread(W_norm, source, k, N_ENTITIES)
                ranked = activation.argsort(descending=True).tolist()
                top = [t for t in ranked if t != source][: len(truth_set)]
                heb_hits += len([t for t in top if t in truth_set])

                attempts += len(truth_set)

            results[k] = {
                "vsa_recall": vsa_hits / max(attempts, 1),
                "resonator_recall": res_hits / max(attempts, 1),
                "hebbian_recall": heb_hits / max(attempts, 1),
            }

    def page_compare(pdf):
        fig, ax = plt.subplots(figsize=(11, 8.5))
        hops = sorted(results.keys())
        ax.plot(hops, [results[k]["vsa_recall"] for k in hops], marker="o", color="firebrick", linewidth=2, label="VSA algebra (repeated unbind)")
        ax.plot(hops, [results[k]["resonator_recall"] for k in hops], marker="s", color="darkorange", linewidth=2, label=f"Resonator (cleanup per hop, T={RESONATOR_TEMPERATURE})")
        ax.plot(hops, [results[k]["hebbian_recall"] for k in hops], marker="^", color="seagreen", linewidth=2, label="Hebbian spreading (graph matmul)")
        ax.set_xlabel("hop distance from source")
        ax.set_ylabel("recall @ |truth_set|")
        ax.set_title(
            f"Three modes of multi-hop retrieval over a knowledge graph\n"
            f"({N_ENTITIES} entities, {N_FACTS} facts, N={N_SUBSTRATE}, {TRIALS_PER_HOP} trials/hop)"
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
        "resonator_temperature": RESONATOR_TEMPERATURE,
        "results_by_hop": results,
        "headline": (
            f"2-hop: VSA={results[2]['vsa_recall']:.2f}, "
            f"resonator={results[2]['resonator_recall']:.2f}, "
            f"hebbian={results[2]['hebbian_recall']:.2f}"
        ),
        "_pdf_extras": [page_compare],
    }


def main() -> None:
    spec = experiment.ExperimentSpec(name="exp_connectivity_resonator", seed=SEED, n=N_SUBSTRATE)
    result = experiment.run(spec, workload)
    print(json.dumps(result.metrics, indent=2, default=str))


if __name__ == "__main__":
    main()
