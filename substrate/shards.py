"""
substrate.shards -- KG sharding strategies (PP-127/128/129/130 + MERGE).

Port of exp_kg_sharding_strategy_compare_gpu_v1.py + exp_hierarchical_subshard_kg_cpu_v1.py.

CORE IDEA:
A monolithic substrate matrix M = Σ ents[s] * rels[r] * ents[o] saturates as facts grow:
crosstalk drowns out individual facts past M ~ 0.1 * N. Sharding splits the matrix into
many smaller per-key memories that each stay below the saturation threshold.

Sharding key choices (Research finding: subject and relation both 1.0 on FB15K; per-subject
is the recommended production default because subject access is the dominant pattern in
KG-QA workloads — start with the subject entity, traverse out).

This module provides:
  - ShardManager: write triples, look up subject memories, list shards
  - per-subject sharding (default)
  - per-relation sharding (for relation-skewed KBs)
  - hierarchical sub-sharding when a single shard gets too large (>10K facts)

Production sharding properties (cycle 187):
  FB15K-237 sharded 1-hop r@5 = 1.000  vs monolithic 0.007 = 140x gap
"""
from __future__ import annotations
import json
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional

import numpy as np

import math

from substrate.core import DEFAULT_DIM, Codebook
from substrate.persistence import ShardMetadata, load_shard, save_shard, list_shards


# Per Research VERIFY response 2026-06-08: cycle 187+188 capacity formula
# SNR = sqrt(N / (VE * deg)). At N=8192 deg=2, VE_safe ~ 400-574 entities = ~800-1148 facts.
# Conservative safe threshold = 500 facts/shard (deg=2 implies ~250 entities; stays
# safely above SNR threshold). Dynamic threshold via dynamic_shard_threshold() preferred.
SHARD_FULL_THRESHOLD = 500


def dynamic_shard_threshold(N: int = DEFAULT_DIM, observed_avg_degree: float = 2.0,
                             safety_margin: float = 2.0) -> int:
    """Compute capacity-safe shard threshold from cycle 187+188 SNR formula.

    SNR ~ sqrt(N / (VE * deg)). Production target: ~500 facts at N=8192 deg=2 baseline.
    Denser graphs (higher deg) saturate the shard's bundling SNR faster, so use smaller
    shards. Larger N permits larger shards proportionally.

    Args:
        N: substrate vector dimensionality
        observed_avg_degree: average outgoing edges per subject in the KB (~2 typical)
        safety_margin: divisor applied to the SNR-derived cap (default 2.0 for headroom)

    Returns:
        int max-facts-per-shard. Use this to set ShardManager's threshold dynamically.
    """
    # Baseline: 500 facts at N=8192 deg=2 safety=2 (per Research VERIFY 2026-06-08).
    # Formula: facts_safe = (0.0625 * N) / max(1, deg/2) / (safety_margin/2)
    deg = max(1.0, float(observed_avg_degree))
    facts_safe = int(0.0625 * N / max(1.0, deg / 2.0) / max(1.0, safety_margin / 2.0))
    return max(50, facts_safe)


class ShardStrategy(str, Enum):
    SUBJECT = "subject"        # one shard per subject entity (DEFAULT, prod-validated)
    RELATION = "relation"      # one shard per relation type
    HIERARCHICAL = "hierarchical"  # subject default + sub-shard when full


@dataclass
class Triple:
    subject: str
    relation: str
    obj: str
    valid_time: Optional[int] = None
    source: Optional[str] = None


@dataclass
class ShardManager:
    """In-memory shard manager. Persists to disk via save() / load().

    Each shard is a single bundled complex64 vector M_s = Σ_i rels[r_i] * ents[o_i]
    for all (s, r_i, o_i) triples sharing the subject s.

    To answer "s, r -> ?": unbind shard[s] by rels[r], cleanup against ents codebook.
    """
    strategy: ShardStrategy = ShardStrategy.SUBJECT
    dim: int = DEFAULT_DIM
    rng_seed: int = 42

    ent_codebook: Codebook = field(init=False)
    rel_codebook: Codebook = field(init=False)
    shard_memory: dict = field(default_factory=dict)        # shard_key -> bundled vector
    shard_fact_count: dict = field(default_factory=dict)    # shard_key -> int
    triples_by_shard: dict = field(default_factory=dict)    # shard_key -> list[Triple]

    def __post_init__(self):
        self.ent_codebook = Codebook("entities", dim=self.dim, seed=self.rng_seed)
        self.rel_codebook = Codebook("relations", dim=self.dim, seed=self.rng_seed + 1)

    def _shard_key_for(self, triple: Triple) -> str:
        if self.strategy == ShardStrategy.SUBJECT:
            return triple.subject
        if self.strategy == ShardStrategy.RELATION:
            return triple.relation
        if self.strategy == ShardStrategy.HIERARCHICAL:
            base = triple.subject
            count = self.shard_fact_count.get(base, 0)
            if count >= SHARD_FULL_THRESHOLD:
                return f"{base}__sub{count // SHARD_FULL_THRESHOLD}"
            return base
        raise ValueError(f"unknown sharding strategy {self.strategy}")

    def write(self, triple: Triple) -> str:
        """Bundle triple's (relation, object) into the appropriate shard. Returns shard key."""
        s_vec = self.ent_codebook.get_or_add(triple.subject)
        r_vec = self.rel_codebook.get_or_add(triple.relation)
        o_vec = self.ent_codebook.get_or_add(triple.obj)
        contribution = r_vec * o_vec
        key = self._shard_key_for(triple)
        if key in self.shard_memory:
            self.shard_memory[key] = self.shard_memory[key] + contribution
        else:
            self.shard_memory[key] = contribution
        self.shard_fact_count[key] = self.shard_fact_count.get(key, 0) + 1
        self.triples_by_shard.setdefault(key, []).append(triple)
        return key

    def write_many(self, triples) -> dict:
        """Bulk write; returns counts per shard for stats."""
        counts: dict = {}
        for t in triples:
            k = self.write(t)
            counts[k] = counts.get(k, 0) + 1
        return counts

    def get_subject_memory(self, subject: str) -> Optional[np.ndarray]:
        """Return the bundled memory for a subject (or None if no facts)."""
        # For HIERARCHICAL, sum across sub-shards
        if self.strategy == ShardStrategy.HIERARCHICAL:
            keys = [k for k in self.shard_memory if k == subject or k.startswith(subject + "__sub")]
            if not keys:
                return None
            return sum(self.shard_memory[k] for k in keys)
        # SUBJECT / RELATION: direct lookup
        if self.strategy == ShardStrategy.SUBJECT:
            return self.shard_memory.get(subject)
        # For relation strategy, traversal-by-subject needs different access; gracefully fail
        return self.shard_memory.get(subject)

    def get_entity_codebook_dict(self) -> dict:
        """Return {name: vec} for use with substrate.khop.traverse()."""
        return {n: self.ent_codebook.get(n) for n in self.ent_codebook.names()}

    def get_relation_codebook_dict(self) -> dict:
        return {n: self.rel_codebook.get(n) for n in self.rel_codebook.names()}

    def get_subject_memory_dict(self) -> dict:
        """Return {subject_name: bundled_vec} for use with substrate.khop.traverse()."""
        if self.strategy != ShardStrategy.HIERARCHICAL:
            # Direct mapping
            return {s: self.get_subject_memory(s) for s in self.ent_codebook.names()
                    if self.get_subject_memory(s) is not None}
        # For HIERARCHICAL we already sum in get_subject_memory
        return {s: self.get_subject_memory(s) for s in self.ent_codebook.names()
                if self.get_subject_memory(s) is not None}

    def stats(self) -> dict:
        return {
            "strategy": self.strategy.value,
            "dim": self.dim,
            "n_shards": len(self.shard_memory),
            "n_entities": len(self.ent_codebook),
            "n_relations": len(self.rel_codebook),
            "total_facts": sum(self.shard_fact_count.values()),
            "avg_facts_per_shard": (
                sum(self.shard_fact_count.values()) / max(1, len(self.shard_memory))
            ),
            "max_facts_per_shard": max(self.shard_fact_count.values()) if self.shard_fact_count else 0,
        }

    def list_subjects(self) -> list[str]:
        return list(self.ent_codebook.names())


def _self_test():
    mgr = ShardManager(strategy=ShardStrategy.SUBJECT, dim=1024)
    triples = [
        Triple("OpenAI", "ceo", "Sam_Altman"),
        Triple("OpenAI", "founded", "2015"),
        Triple("Sam_Altman", "founded", "Loopt"),
        Triple("Sam_Altman", "previous_role", "YC_president"),
        Triple("Loopt", "founded", "2005"),
    ]
    mgr.write_many(triples)

    stats = mgr.stats()
    assert stats["n_shards"] == 3, f"expected 3 subject shards, got {stats['n_shards']}"
    assert stats["total_facts"] == 5

    # Test 1-hop traversal via khop using shard manager's codebooks
    from substrate.khop import traverse
    result = traverse(
        start_entity="OpenAI",
        relation_path=["ceo"],
        ent_codebook=mgr.get_entity_codebook_dict(),
        rel_codebook=mgr.get_relation_codebook_dict(),
        subject_memory=mgr.get_subject_memory_dict(),
        query_id="shards_test_1hop",
    )
    assert result.final_entity == "Sam_Altman", f"1-hop expected Sam_Altman, got {result.final_entity}"

    # Test 2-hop OpenAI ceo founded -> Loopt
    result = traverse(
        start_entity="OpenAI",
        relation_path=["ceo", "founded"],
        ent_codebook=mgr.get_entity_codebook_dict(),
        rel_codebook=mgr.get_relation_codebook_dict(),
        subject_memory=mgr.get_subject_memory_dict(),
        query_id="shards_test_2hop",
    )
    assert result.final_entity == "Loopt", f"2-hop expected Loopt, got {result.final_entity}"

    # Hierarchical sub-sharding test (threshold is now 500 per Research VERIFY)
    mgr_h = ShardManager(strategy=ShardStrategy.HIERARCHICAL, dim=512)
    big_subject = "BigEntity"
    for i in range(SHARD_FULL_THRESHOLD + 100):
        mgr_h.write(Triple(big_subject, f"rel_{i % 10}", f"obj_{i}"))
    h_stats = mgr_h.stats()
    assert h_stats["n_shards"] >= 2, "hierarchical should sub-shard"

    # Dynamic threshold validation
    t8k = dynamic_shard_threshold(N=8192, observed_avg_degree=2.0)
    t4k = dynamic_shard_threshold(N=4096, observed_avg_degree=2.0)
    t8k_high_deg = dynamic_shard_threshold(N=8192, observed_avg_degree=10.0)
    assert t8k > t4k, "larger N should permit larger shards"
    assert t8k_high_deg < t8k, "denser graphs should use smaller shards"

    print(f"[substrate.shards] self-test PASS (strategy=subject: {stats['n_shards']} shards, "
          f"{stats['total_facts']} facts; hierarchical sub-shards on big entity OK; "
          f"dynamic threshold N=8192 deg=2: {t8k} facts; N=4096 deg=2: {t4k}; N=8192 deg=10: {t8k_high_deg})")


if __name__ == "__main__":
    _self_test()
