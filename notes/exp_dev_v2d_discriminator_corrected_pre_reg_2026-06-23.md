# PRE-REG: substrate_self_map_v2d_discriminator_corrected_v1

**Date:** 2026-06-23
**Author:** exp_dev (cell author; spawn-and-die)
**Cell:** `experiments/exp_substrate_self_map_v2d_discriminator_corrected_v1.py`
**Anchor:** `substrate_self_map_v2d_discriminator_corrected_v1`
**Queue routing:** remote_cpu_queue (numpy-only; CPU bound; 4096-D ingest + traversal ~2hr/seed; 3 seeds)
**Parent:** `substrate_self_map_v2c_full_store_v1` HARD_FAIL 2026-06-22

## Motivation

Per `notes/research_2x_revival_overnight_negatives_2026-06-23.md`, the parent v2c HARD_FAIL
("shuffle as granular as real; cluster_gap=-3.0 across 3 seeds") may be a
DISCRIMINATOR-DIRECTION bug:
- Real relations BUNDLE chain-grade anchors into LARGER coherent clusters.
- Shuffle FRAGMENTS them into more, smaller clusters.
- "n_clusters_real > n_clusters_shuf" is therefore the WRONG-direction discriminator;
  the correct test is via ARI vs ground-truth labels OR mean_cluster_size.

Highest-leverage revival: P=0.50 (top of revival drill); biggest verdict-flip upside.
Three parent v2 lineage HARD_FAIL/MIDDLE_BAND verdicts could flip simultaneously
(v2 MIDDLE_BAND + v2b MIDDLE_BAND + v2c HARD_FAIL).

## Cell design

Re-uses ALL v2c primitives end-to-end (FULL-Store ingest, char_trigram_encode,
KGStore_multivalue_Hebbian, multi_hop 2-hop neighborhood + greedy Jaccard cluster). Module
imports from `exp_substrate_self_map_v2c_full_store_v1`.

ONLY discriminator changes:
- PRIMARY: ARI(real_clustering, v1_families) vs ARI(shuf_clustering, v1_families)
  - v1 families = parse `notes/capability_family_map_v1_*.md` (existing v2c primitive)
  - Library: sklearn.metrics.adjusted_rand_score (handoff autonomy chose sklearn)
  - Anchors not in any v1 family get a UNIQUE SINGLETON label (so ARI doesn't reward
    false-match to "uncategorized")
- SECONDARY: mean_cluster_size_real / mean_cluster_size_shuf
  - mean_cluster_size = mean size of clusters with >=2 members (singletons excluded)

Diagnostic-recorded (NOT used for verdict): cluster_count, cluster_gap (parent's discriminator),
cluster_coherence, avg_jaccard_vs_v1.

Config:
- FULL: N_DIM=4096, MAX_INGEST_TRIPLES=None (all ~203k), N_ANCHORS=100, N_REL_SAMPLES=20, K_SET=16
  3 seeds {7, 17, 23}
- SMOKE: N_DIM=1024, MAX_INGEST=5000, N_ANCHORS=20 (degenerate ARI expected at small N; smoke
  proves end-to-end pipe + valid metrics.json; HARD_PASS evaluation requires FULL)

## Pre-registered HARD bands (handoff verbatim)

**HARD_PASS (chain-grade, ANY of A/B AND all of C):**
- A: ARI_real >= 0.10 AND ARI_real / ARI_shuf >= 2.0
- B: mean_cluster_size_real / mean_cluster_size_shuf >= 1.5
- C: atom_retrieval_recall >= 0.95 AND cv(ARI_real) across 3 seeds <= 0.20 AND n_llm_calls = 0

**HARD_FAIL (ANY of):**
- ARI_real <= 0.02
- ARI_ratio <= 1.1 AND size_ratio <= 1.1 (both discriminators null)
- atom_retrieval_recall < 0.50
- n_llm_calls > 0 (substrate-only-decode violated)

**MIDDLE_BAND:** partial signal between thresholds.

## Pre-flight discipline

1. --self-test: ARI endpoints (same=1.0, permuted~0) + clustering_to_labels +
   mean_cluster_size + v1_family_labels mapping + n_llm=0. (Plus v2c primitive selftest
   auto-runs at module import.)
2. REQUIRED_FIELDS: anchor_name, verdict, verdict_msg, summary, elapsed_s, run_mode, n_seeds,
   per_seed, zero_llm_calls_at_inference, config_version, DESIGN_NOTE.
3. Per-seed checkpoint via _seed_checkpoint.
4. ASCII-only.
5. Substrate-only-decode gate: `_LLM_CALL_COUNTER = [0]` asserted in metrics.
6. Smoke first (local CPU manual) -> remote_cpu_queue FULL (3 seeds, ~6hr total).

## Honest scope

- Discriminator-direction fix ONLY. No other change vs v2c (same atoms, same encoder, same
  KG ingest, same anchor sampling, same Jaccard cluster).
- ARI depends on v1 families having coverage of the chain-grade anchors. The smoke confirmed
  parsing works (6 v1 families + 18 cross-family atoms loaded). In full N_ANCHORS=100 of 450
  chain-grade atoms, expected ~30-60 anchors in some v1 family (significant coverage).
- cv on ARI relaxed to 0.20 (vs v2c=0.10 on n_clusters) because ARI is naturally more variable
  across seeds than cluster-count.
- If both ARI AND size_ratio discriminators come back null even at FULL, the mechanism IS
  truly rejected (revival exhausted -- route to next research drill).

## 2x-revival angle (if HARD_FAIL or MIDDLE_BAND)

- Modularity Q (Newman 2006) -- alternative graph-theoretic discriminator (no v1 dependency)
- Per-relation-type ARI (test whether SPECIFIC rel_types carry the signal)
- Anchor-coverage filter: subsample to anchors that ARE in v1 families
- Different clustering algo (Louvain, agglomerative) -- greedy Jaccard may be too sparse

## Cites

- `notes/research_2x_revival_overnight_negatives_2026-06-23.md` (revival drill)
- `notes/exp_dev_handoff_research_2x_revival_overnight_negatives_2026-06-23.md` (handoff)
- Parent: `notes/research_brain_mechanism_x_HD_broad_exploration_drill_2026-06-22`
- v2b/v2c lineage: `preregs/2026-06-22_substrate_self_map_v2c_full_store.md`
- Hubert & Arabie 1985 (Adjusted Rand Index original)
- Newman 2006 PNAS (Modularity Q -- 2x-revival arm if v2d MIDDLE)
