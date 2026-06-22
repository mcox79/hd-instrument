# Pre-reg: substrate_self_map_v2c (FULL-Store ingest; Option-2 recovery from v2b MIDDLE_BAND)

- Date: 2026-06-22
- Anchor: substrate_self_map_v2c
- Script: experiments/exp_substrate_self_map_v2c_full_store_v1.py
- Cell-author: Exp-Dev (Opus 4.7)

## Why v2c (FULL-Store ingest)

v2c is the third iteration in the substrate-native self-mapping arc. The route
was queued in `notes/META_substrate_cert_chain_lives_in_cert_ledger_semantics_not_relations_topology_2026-06-22.md`
("Option 2 = full-Store ingest, ~200k relations -- deferred until v2b shows the
broadened scope works"). v2b has now landed `MIDDLE_BAND`:

  - 3 seeds, full run; n_clusters_real = 2.0 (vs HARD_PASS=3) and cluster_gap = 1.0
    (vs HARD_PASS=2). Mechanism present (recall=1.000, n_llm=0, cv=0) but below
    HARD_PASS bars. Cell-author's recommended HARD_FAIL recovery path was
    Option 2 = FULL-Store ingest, which v2c implements.

v2c admit rule: every (src, rel_type, tgt) triple in every
`data/substrate_index/<corpus>/relations.jsonl` is admitted (self-loops dropped).
No EITHER-endpoint chain-grade filter. Combined atom universe = chain-grade
prefix + every other endpoint atom (union with atomized atoms for codebook
honesty). Anchors still drawn ONLY from the chain-grade prefix.

Frozen counts (2026-06-22; wc -l on the corpus relations.jsonl files):

  - concept            189,654
  - science              7,161
  - math                 4,272
  - research_history     1,524
  - decision_history       416
  - meta                   122
  - results_history         73 (typo? 104 verdict_history)
  - verdict_history        104
  - findings_history        98
  - school                  38
  - methodology              0
  - TOTAL              203,462 relations across 11 corpora

  - chain-grade atoms (cert_ledger.jsonl, chain_grade, supersedes-folded): ~447
  - atomized atom_ids across corpora atoms.jsonl: ~177k

## Primary metric (v2c; identical to v2b)

- `n_clusters_real`: greedy-Jaccard clusters substrate forms over anchors in REAL arm
- `n_clusters_shuf`: same for the RANDOM_RELATION control arm
- `cluster_gap = n_clusters_real - n_clusters_shuf` (relation-conditioned granularity)

Coherence retained as informational (v2b discovered the sign is opposite expectation;
not load-bearing in either v2b or v2c verdicts). v1 lexical resemblance retained as
informational (per_cluster_match); v1 was chain-grade-only lexical, so it is not the
relevant alignment target on full Store.

## HARD bands (v2c; identical to v2b)

HARD_PASS chain-grade:
- n_clusters_real >= 3
- cluster_gap >= 2
- substrate-only-decode (n_llm_calls = 0)
- atom_retrieval_recall >= 0.95
- 3 seeds; cv on n_clusters_real <= 0.10

MIDDLE_BAND:
- n_clusters_real >= 2 AND cluster_gap >= 1

HARD_FAIL:
- n_clusters_real <= 1 (mechanism null even on full Store -- substrate-native
  self-mapping ceiling on the current relational substrate)
- cluster_gap <= 0
- substrate-only-decode violated
- atom_retrieval_recall < 0.50

## Config

- N_DIM = 4096 (full); 1024 (smoke)
- SEEDS = [7, 17, 23]
- MAX_INGEST_TRIPLES = None (full); 5000 (smoke -- uniform subsample to keep
  smoke wall <120s while validating the full-Store-ingest pipe end-to-end)
- N_ANCHORS = 100 (full; tightened from v2b=200 to keep traversal wall bounded
  -- at n_ent ~ 177k + N=4096, each kg.E @ transit is ~725M float ops, and 200
  anchors x 20 pair-traversals x 3 score_all calls per pair = 12k score_all
  per arm per seed; n_anchors=100 halves this)
- N_RELATION_SAMPLES = 20 (full; tightened from v2b=32)
- K_SET = 16
- JACCARD_CLUSTER_TAU = 0.30

## Wall estimate

  - Encoding 177k atoms via char-trigram at N=4096: ~5-10s/seed (linear in n_atoms)
  - Ingest 200k triples via multi-value Hebbian at N=4096: ~20-30s/seed
    (chunked 5000-batch outer-products; cost scales with n_triples * n_dim^2 /
    batch_size = 200k * 4096^2 / 5000 ~ 670M float ops -- modest)
  - Traversal per anchor: 20 pairs x (1 score_all for top-K + 1 iter_cleanup_chain
    at K=2 = ~3 score_all). 60 score_all per anchor x 100 anchors x 2 arms = 12k
    score_all per seed. Each score_all = kg.E @ (W @ key) ~ 725M float ops on
    a 4096-D codebook over 177k entities; estimate 100-300ms per call on
    remote_cpu BLAS = 20-60min traversal per seed
  - Per-seed total: 25-65min; 3 seeds: 75-195min wall
  - Timeout setting: 14400s (4h) -- accommodates the upper-bound estimate plus
    margin for the unknown BLAS rate on remote_cpu

## Discriminator (Fix #16)

RANDOM_RELATION control arm: each triple's rel_type is replaced uniformly at
random (preserves adjacency, destroys relation-conditioned cleanup signal).

## Honest scope

- char-trigram atom-id encoding is bag-of-trigrams; at n_ent=177k in a 4096-D
  bipolar codebook, atom_retrieval_recall is genuinely harder than at v2b's 489
  atoms. The 0.95 bar is preserved; if recall falls below 0.50 the run
  HARD_FAILs (codebook too crowded -- mechanism precondition violated).
- 2-hop traversal only (chain-grade per r1)
- Anchors restricted to chain-grade prefix; frontier atoms only reachable as
  2-hop targets, not as anchors
- v2c does NOT propose new atoms; that is Phase 2 (SubstrateGenerator)

## Smoke results

Documented in `data/exp_substrate_self_map_v2c_smoke/metrics.json` after the
smoke pass at gate time. Smoke is on a 5000-triple subsample of the full Store
(uniform-random; deterministic via load_rng seed=0). Validates that the
full-Store data-load + admit-all + indexing + ingest + traversal pipe composes;
the actual mechanism verdict comes from the full run.

## Recovery paths if v2c HARD_FAILs

If `n_clusters_real <= 1` even on the full Store, the substrate-native
self-mapping ceiling has been reached on the current relational substrate.
Recovery options (per META atom queued):

  (3) Cert-chain SEMANTIC self-mapping: self-map via co-membership in
      cert_ledger fields (shared cell_commit prefix, shared atomized_by,
      shared verdict-class, supersedes-chain). Different substrate
      (cert_ledger SEMANTICS vs relations.jsonl TOPOLOGY).
