# Pre-reg: substrate_self_map_v2b (broadened-scope chain-grade OR atomized)

- Date: 2026-06-22
- Anchor: substrate_self_map_v2b
- Script: experiments/exp_substrate_self_map_v2.py (in-place edit; ANCHOR_NAME = substrate_self_map_v2b, CONFIG_VERSION bumped)
- Cell-author: Exp-Dev (Opus 4.7)

## Why v2b (broadened scope)

v2 single-seed full-scale run discovered that the chain-grade-INTERNAL relation
subgraph is structurally near-empty: 447 chain-grade atoms, only 16 relations
across 2 distinct relation types (7 non-trivial after dropping self-loops).
Single-seed verdict on real data: clusters=1, avg_J=0.020, recall=1.000,
n_llm=0 -- mechanism null on this scope.

The pre-reg estimate of ~8000 relations across 17 relation types was the
FULL-Store inventory, NOT the chain-grade subgraph. The cert chain lives in
cert_ledger.jsonl SEMANTICS, not in relations.jsonl TOPOLOGY -- chain-grade
atoms are linked into the substrate via co-membership in the cert ledger, not
via dense within-chain-grade relations.

v2b admit rule: a triple (src, rel_type, tgt) is admitted iff
    (src is chain-grade OR tgt is chain-grade) AND (src and tgt are both atomized).
Anchors for 2-hop traversal are STILL drawn from the chain-grade subset; v2b
maps how chain-grade atoms sit in the broader atomized Store.

(Option 2 = full-Store ingest, ~200k relations -- deferred until v2b shows the
broadened scope works.)

## Primary metric (v2b)

- `n_clusters_real`: number of greedy-Jaccard clusters the substrate forms over
  anchor atoms in the REAL-relations arm.
- `n_clusters_shuffle`: same for the SHUFFLE (RANDOM_RELATION) arm.
- `cluster_gap = n_clusters_real - n_clusters_shuffle` (the relation-conditioned
  granularity gain).

Smoke-time discovery (documented in `data/exp_substrate_self_map_v2b_smoke/metrics.json`):
within-cluster coherence has the OPPOSITE sign of expectation. The shuffle arm
collapses into one giant blob with high internal coherence (everything reachable
through uniform-random noise); the real arm produces more, smaller, more-
distinguishable clusters. The discriminator is therefore cluster-count delta
(real - shuffle), NOT coherence-gap.

v1 lexical resemblance retained as informational only (per_cluster_match), not
a HARD gate, because the broadened scope now includes outward atomized atoms
whose lexical clustering structure differs from chain-grade-only v1 families.

## HARD bands

HARD_PASS chain-grade:
- n_clusters_real >= 3
- cluster_gap >= 2 (real has at least 2 more clusters than shuffle)
- substrate-only-decode (n_llm_calls = 0)
- atom_retrieval_recall >= 0.95
- 3 seeds; cv on n_clusters_real <= 0.10

MIDDLE_BAND:
- n_clusters_real >= 2 AND cluster_gap >= 1

HARD_FAIL:
- n_clusters_real <= 1 (recommend Option 2: full-Store ingest)
- cluster_gap <= 0 (shuffle as granular as real -- relation-conditioned mechanism null)
- substrate-only-decode violated
- atom_retrieval_recall < 0.50

## Config

- N_DIM = 4096 (full); 1024 (smoke)
- SEEDS = [7, 17, 23]
- N_ANCHORS = 200
- N_RELATION_SAMPLES = 32
- K_SET = 16
- JACCARD_CLUSTER_TAU = 0.30

## Discriminator (Fix #16)

RANDOM_RELATION control arm: each triple's rel_type is replaced uniformly at
random (preserves adjacency, destroys relation-conditioned cleanup signal).
Real-arm coherence > shuffle-arm coherence = relation-conditioned mechanism real.

## Honest scope

- char-trigram atom-id encoding is bag-of-trigrams (no positional info)
- 2-hop traversal only (chain-grade per r1)
- Anchors restricted to chain-grade prefix of the atom universe; frontier
  atomized atoms are only reachable as 2-hop targets
- v2b does NOT propose new atoms; that is Phase 2 (SubstrateGenerator)

## Smoke results (smoke gate)

Documented in `data/exp_substrate_self_map_v2b_smoke/metrics.json` after the
smoke pass at gate time.
