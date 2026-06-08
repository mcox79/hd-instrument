"""
substrate.inverted -- Mechanism B inverted property shards.

Port of exp_inverted_property_shards_cpu_v1.py.

CORE IDEA:
Per-subject shards answer (subject -> properties) fast. But "all subjects with property
P" would scan ALL shards (O(M*K)). During a SLEEP DEFRAG pass, we scan for each property
P=(relation, value) appearing in >= T subject shards and build a SECONDARY inverted
shard inv[P] = bundle of those subjects. The set query then hits inv[P] at O(K).

WHY THIS MATTERS FOR THE DEMO:
"List all companies founded by ex-OpenAI employees" — without inverted index, requires
scanning the entire KB. With Mechanism B, a single inverted shard answers it.

Validated cycle 162: subjects-with-P recall >= 0.90 at frequent properties.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional

import numpy as np

from substrate.core import DEFAULT_DIM, cidx_topk


@dataclass
class InvertedIndex:
    """Mechanism B inverted property shards built lazily by sleep-defrag.

    Each property P = (relation_name, object_name) has a bundle of all subject vectors
    that match. Lookup uses cosine similarity against the entity codebook to retrieve
    the top-K subjects.
    """
    inv_shards: dict = field(default_factory=dict)  # property_key -> bundled vector
    property_subjects: dict = field(default_factory=dict)  # property_key -> set[str] (ground truth)
    threshold_subjects_per_property: int = 5         # only invert if >= T subjects have it

    @staticmethod
    def property_key(relation: str, obj: str) -> str:
        return f"{relation}={obj}"

    def build_from_triples(self, triples, ent_codebook: dict) -> None:
        """Run a sleep-defrag pass over triples; build inverted shards for hot properties.

        Per Research VERIFY 2026-06-08: store BOTH a bundle (for Mechanism B cosine
        retrieval) AND an exact subject list (for set-of-subjects queries without
        cleanup-noise risk).
        """
        # Count subjects per property
        property_subjects: dict = {}
        for t in triples:
            key = self.property_key(t.relation, t.obj)
            property_subjects.setdefault(key, set()).add(t.subject)
        # Build inverted shards only for hot properties
        for key, subjects in property_subjects.items():
            if len(subjects) < self.threshold_subjects_per_property:
                continue
            self.property_subjects[key] = subjects   # exact list (per Research VERIFY)
            self.inv_shards[key] = sum(ent_codebook[s] for s in subjects)  # bundle (Mechanism B)

    def query(self, relation: str, obj: str, ent_codebook: dict, ent_names: list[str],
              top_k: Optional[int] = None, exact: bool = False) -> list[str]:
        """Look up subjects with property (relation=obj). Returns ordered list of names.

        Args:
            exact: if True, return the EXACT subject list (no cleanup noise; matches
                the truth set used to build the shard). Recommended for set-of-subjects
                wow moment queries per Research VERIFY 2026-06-08.
                If False, return ordered-by-cosine via the bundle (Mechanism B).
        """
        key = self.property_key(relation, obj)
        if key not in self.inv_shards:
            return []
        if exact:
            # Return exact stored list (deterministic; no cleanup risk)
            return sorted(self.property_subjects[key])
        ent_array = np.stack([ent_codebook[n] for n in ent_names], axis=0)
        bundle = self.inv_shards[key]
        # cosine via real(book @ conj(bundle))
        scores = (ent_array @ np.conj(bundle)).real
        order = np.argsort(-scores)
        if top_k is None:
            top_k = len(self.property_subjects.get(key, set()))
        return [ent_names[i] for i in order[:top_k]]

    def list_hot_properties(self) -> list[tuple[str, int]]:
        return [(k, len(v)) for k, v in self.property_subjects.items()]


def _self_test():
    import math
    from substrate.core import cphasor
    from substrate.shards import Triple

    rng = np.random.default_rng(42)
    dim = 1024
    entity_names = [f"company_{i}" for i in range(20)]
    book = cphasor(len(entity_names), dim=dim, rng=rng)
    ents = {n: book[i] for i, n in enumerate(entity_names)}

    # Build triples: 8 companies are SaaS; 5 are FinTech; 7 are HealthTech
    triples = []
    for i in range(8):
        triples.append(Triple(f"company_{i}", "industry", "SaaS"))
    for i in range(8, 13):
        triples.append(Triple(f"company_{i}", "industry", "FinTech"))
    for i in range(13, 20):
        triples.append(Triple(f"company_{i}", "industry", "HealthTech"))

    inv = InvertedIndex(threshold_subjects_per_property=4)
    inv.build_from_triples(triples, ents)

    # All 3 properties should have inverted shards (each >= 4 subjects)
    hot = inv.list_hot_properties()
    assert len(hot) == 3, f"expected 3 hot properties, got {len(hot)}"

    saas = inv.query("industry", "SaaS", ents, entity_names, top_k=8)
    saas_truth = {f"company_{i}" for i in range(8)}
    overlap = len(set(saas) & saas_truth)
    assert overlap >= 7, f"expected >=7/8 SaaS overlap, got {overlap}"

    # Exact-list mode (per Research VERIFY: no cleanup noise on set queries)
    saas_exact = inv.query("industry", "SaaS", ents, entity_names, exact=True)
    assert set(saas_exact) == saas_truth, f"exact mode should return truth set exactly, got {saas_exact}"

    print(f"[substrate.inverted] self-test PASS (3 inverted shards built; "
          f"SaaS query bundle-mode {overlap}/8 correct; exact-mode = truth set)")


if __name__ == "__main__":
    _self_test()
