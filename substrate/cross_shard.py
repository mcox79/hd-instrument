"""
substrate.cross_shard -- Mechanism C cross-shard chain extraction (consensus voting).

Port-inspired by exp_mechanism_composition_v1_n4096.py + exp_cross_shard_chain_extraction_cpu_v1.py.

CORE IDEA:
When a multi-hop K-hop query crosses shard boundaries (e.g. subject in shard A, traversal
continues into entities residing in shard B), naive single-shard K-hop loses the chain.
Scatter-gather across all shards + consensus voting (>=2/N shards agree) gives accurate
cross-shard answers.

Production model: dispatch the query to each shard in parallel; each returns top-K
candidate paths with confidence; aggregate via softmax-weighted voting; output the
argmax if consensus is high (else abstain).

This is the BIG architectural win on real KGs (cycle 187: FB15K-237 sharded 140x recall
gap over monolithic).
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional

import numpy as np

from substrate.audit import AuditChain
from substrate.khop import KHopResult, traverse


@dataclass
class CrossShardResult:
    query_id: str
    start_entity: str
    relation_path: list[str]
    per_shard_results: list[KHopResult]   # one per attempted shard
    consensus_entity: Optional[str]        # final answer if consensus, else None
    consensus_confidence: float
    consensus_method: str                  # "majority" / "weighted" / "intersection" / "no_consensus"
    audit_chain: AuditChain
    elapsed_ms: float

    @property
    def chain_root(self) -> str:
        return self.audit_chain.root


def scatter_gather(
    start_entity: str,
    relation_path: list[str],
    shard_keys: list[str],
    ent_codebook: dict,
    rel_codebook: dict,
    subject_memory_per_shard: dict,    # {shard_key: {subject: memory_vec}}
    method: str = "weighted",          # "weighted" / "majority" / "intersection"
    query_id: str = "cs_0",
) -> CrossShardResult:
    """Scatter-gather K-hop across multiple shards.

    For each shard that contains the start_entity in its subject_memory, run K-hop.
    Aggregate results by the chosen consensus method:
      - majority: pick the entity that >=ceil(N/2) shards return as final
      - weighted: softmax weights by confidence; argmax of summed weight
      - intersection: pick top-1 only if ALL shards agree
    """
    import time
    t0 = time.perf_counter()
    chain = AuditChain(chain_id=f"cs:{query_id}")
    chain.append("scatter", {"start": start_entity, "path": relation_path, "shards": shard_keys})

    per_shard_results: list[KHopResult] = []
    for shard_key in shard_keys:
        subject_memory = subject_memory_per_shard.get(shard_key, {})
        if start_entity not in subject_memory:
            continue
        r = traverse(
            start_entity=start_entity,
            relation_path=relation_path,
            ent_codebook=ent_codebook,
            rel_codebook=rel_codebook,
            subject_memory=subject_memory,
            query_id=f"{query_id}_{shard_key}",
        )
        per_shard_results.append(r)
        chain.append("shard_result", {
            "shard": shard_key,
            "final_entity": r.final_entity,
            "confidence": round(r.final_confidence, 4),
        })

    consensus_entity, consensus_conf, consensus_method = _aggregate(per_shard_results, method)
    chain.append("consensus", {"method": consensus_method, "entity": consensus_entity,
                                "confidence": round(consensus_conf, 4)})

    elapsed_ms = (time.perf_counter() - t0) * 1000
    return CrossShardResult(
        query_id=query_id,
        start_entity=start_entity,
        relation_path=relation_path,
        per_shard_results=per_shard_results,
        consensus_entity=consensus_entity,
        consensus_confidence=consensus_conf,
        consensus_method=consensus_method,
        audit_chain=chain,
        elapsed_ms=elapsed_ms,
    )


def _aggregate(results: list[KHopResult], method: str) -> tuple[Optional[str], float, str]:
    """Aggregate per-shard final_entity into a consensus pick."""
    if not results:
        return (None, 0.0, "no_results")
    valid = [r for r in results if r.final_entity is not None]
    if not valid:
        return (None, 0.0, "no_results")
    if method == "intersection":
        entities = {r.final_entity for r in valid}
        if len(entities) == 1:
            ent = entities.pop()
            avg_conf = sum(r.final_confidence for r in valid) / len(valid)
            return (ent, avg_conf, "intersection")
        return (None, 0.0, "no_consensus")
    if method == "majority":
        # >=ceil(N/2) shards must agree
        counts: dict = {}
        for r in valid:
            counts[r.final_entity] = counts.get(r.final_entity, 0) + 1
        best_ent, best_count = max(counts.items(), key=lambda kv: kv[1])
        if best_count >= (len(valid) + 1) // 2:
            confs = [r.final_confidence for r in valid if r.final_entity == best_ent]
            return (best_ent, sum(confs) / len(confs), "majority")
        return (None, 0.0, "no_consensus")
    # "weighted": softmax-weight confidences; sum per-entity
    entity_scores: dict = {}
    confs = np.array([r.final_confidence for r in valid])
    exps = np.exp(confs - confs.max())
    weights = exps / exps.sum()
    for r, w in zip(valid, weights):
        entity_scores[r.final_entity] = entity_scores.get(r.final_entity, 0.0) + float(w)
    best_ent = max(entity_scores, key=lambda k: entity_scores[k])
    return (best_ent, entity_scores[best_ent], "weighted")


def _self_test():
    """Synthesise a 2-shard substrate; verify scatter-gather picks the right answer."""
    import math
    from substrate.core import cphasor

    rng = np.random.default_rng(0)
    dim = 1024
    ent_names = ["OpenAI", "Sam_Altman", "Loopt", "Y_Combinator"]
    rel_names = ["ceo", "founded"]
    e_book = cphasor(len(ent_names), dim=dim, rng=rng)
    r_book = cphasor(len(rel_names), dim=dim, rng=rng)
    ents = {n: e_book[i] for i, n in enumerate(ent_names)}
    rels = {n: r_book[i] for i, n in enumerate(rel_names)}

    # Shard A has the CEO fact; Shard B has the founded fact (start_entity is in both)
    shard_a_memory = {"OpenAI": rels["ceo"] * ents["Sam_Altman"]}
    shard_b_memory = {"OpenAI": rels["ceo"] * ents["Sam_Altman"] + 0.1 * (rels["founded"] * ents["Loopt"])}

    result = scatter_gather(
        start_entity="OpenAI",
        relation_path=["ceo"],
        shard_keys=["A", "B"],
        ent_codebook=ents,
        rel_codebook=rels,
        subject_memory_per_shard={"A": shard_a_memory, "B": shard_b_memory},
        method="weighted",
        query_id="test_cs",
    )
    assert result.consensus_entity == "Sam_Altman"
    assert result.audit_chain.verify()

    # Intersection method (both shards return Sam_Altman -> consensus)
    result2 = scatter_gather(
        start_entity="OpenAI",
        relation_path=["ceo"],
        shard_keys=["A", "B"],
        ent_codebook=ents,
        rel_codebook=rels,
        subject_memory_per_shard={"A": shard_a_memory, "B": shard_b_memory},
        method="intersection",
    )
    assert result2.consensus_entity == "Sam_Altman"
    assert result2.consensus_method == "intersection"

    print(f"[substrate.cross_shard] self-test PASS (scatter-gather 2 shards -> "
          f"consensus={result.consensus_entity} via {result.consensus_method})")


if __name__ == "__main__":
    _self_test()
