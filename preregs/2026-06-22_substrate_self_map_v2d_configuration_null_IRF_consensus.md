# Pre-reg: substrate_self_map_v2d (v2c HARD_FAIL 2x revival; three coupled mechanism fixes)

- Date: 2026-06-22
- Anchor: substrate_self_map_v2d_configuration_null_IRF_consensus
- Script: experiments/exp_substrate_self_map_v2d_configuration_null_IRF_consensus_v1.py
- Cell-author: Exp-Dev (Opus 4.7)
- Drill source: notes/research_substrate_self_map_2x_revival_full_store_mechanism_null_drill_2026-06-22.md

## Why v2d (HARD_FAIL revival)

v2c landed HARD_FAIL with cluster_gap=-3 (shuffle 38 > real 35 clusters) over 3
seeds at full Store scope (~200k relations / 449 chain-grade anchors). Research
drill diagnosed the v2c null as a compound of THREE measurement misspecifications,
NOT substrate-can't-self-map:

  1. Uniform-relation-shuffle null destroys degree heterogeneity, making the
     shuffled graph spuriously MORE clusterable. Configuration-model degree-
     preserving rewire is the textbook null for community detection.
  2. Uniform-Hebbian weight dilutes rare-relation signal. IRF (Inverse Relation
     Frequency, TF-IDF analog) up-weights rare relations which carry the
     structural discriminating power.
  3. Cluster-count is high-variance at scale (v2c cv=0.314). Consensus clustering
     co-cluster matrix is CV-stable by construction.

v2d holds scope constant (full Store, char_trigram encoding, chain-grade anchors)
and changes ONLY the measurement: applies all 3 fixes as the primary arm (ABC)
plus 3 single-fix ablation arms (A_irf, B_cfg, C_cons) to discriminate which
fix(es) are load-bearing per the drill's 4 falsifiable predictions.

## Drill-pinned bands (HARD bands)

HARD_PASS (P_deflated=0.42; novel-synthesis cap 0.50; 0.15 deflation for
compounded uncertainty on three coupled fixes):
- ABC arm consensus_gap >= 0.05
- ABC arm consensus_cv <= 0.10
- atom_retrieval_recall >= 0.95
- arrows_mean >= 50% of v2c's new_arrows_mean (= 5.33 * 0.5 = 2.67)
- substrate-only-decode (n_llm_calls = 0)

MIDDLE_BAND (P=0.30):
- consensus_gap in [0.01, 0.05) OR consensus_cv in (0.10, 0.20]
- AND recall >= 0.95

HARD_FAIL (P=0.28):
- consensus_gap < 0.01
- OR consensus_cv > 0.20
- OR substrate-only-decode violated
- OR atom_retrieval_recall < 0.50

## Discriminator (Fix C, primary)

Consensus co-cluster matrix M (N_anchors x N_anchors): M[i,j] = fraction of
K_CONSENSUS random-restarts in which anchors i and j co-cluster. Consensus
stability = mean(|M_ij - 0.5| * 2) over off-diagonal entries, in [0, 1].
Real-arm stability vs shuffle-arm stability difference = consensus_gap.

## Null (Fix B, primary)

Configuration-model rewire: within each relation type, permute the target list.
Preserves per-source per-relation out-degree multiset (verified by selftest).
Approximates the per-target in-degree distribution (target-perm, the standard
substrate-native lit approximation rather than full half-edge matching).

## Weighting (Fix A, primary)

Per-relation IRF weight = log(N_total / freq_r) + 1.0. Frequent relations get
weight ~ 1.0; rare relations get weight ~ log(N_total). Applied by per-relation
ingest pass with E[o] pre-scaled by the IRF weight before Hebbian
outer-product accumulation (mathematically equivalent to scalar weight on the
(key, value) pair).

## 4 falsifiable predictions (drill)

- P1: Fix A alone -> cluster_gap rises from v2c -3 toward 0 (MIDDLE_BAND).
  Falsifiable: gap >= 2 means Issue 2 was dominant.
- P2: Fix B alone -> cluster_gap turns POSITIVE (degree-preserving shuffle loses
  spurious-cluster advantage). Falsifiable: gap >= 2 means Issue 1 was dominant.
- P3: Fix C alone -> consensus_cv < 0.10 by construction; consensus_gap small.
  Falsifiable: consensus_gap >= 0.05 means Issue 3 was dominant.
- P4: ABC combined -> HARD_PASS at P_deflated=0.42.

## Local smoke results (verifying pipe composes; informational signal)

Smoke wall: 277s on laptop with 5000 triples / N=1024 / 20 anchors / 4 arms.

  ABC arm:    cons_gap=+0.0386 (MIDDLE -- just below 0.05 PASS)
              cluster_gap=+4 (POSITIVE; v2c was -3 -- sign FLIPPED)
  A_irf arm:  cluster_gap=+1 (small lift; P1 consistent)
  B_cfg arm:  cluster_gap=+3 (clear lift; P2 consistent -- config-null carries
                              most of the signal)
  C_cons arm: consensus_gap=-0.04 (negative; P3 consistent -- consensus alone
                                   doesn't help; cluster-count + IRF + config-null
                                   needed to feed it real structure)

Smoke signal: the three fixes compound. Sign-flip on cluster_gap (-3 -> +4)
under the smoke triple subsample is the strongest signal the drill predicted.
Full run validates whether the lift survives the ~40x triple-count increase
+ the noise from 5 seeds.

## Config

- N_DIM = 4096 (full); 1024 (smoke)
- SEEDS = [7, 17, 23, 31, 41] (full; 5 seeds per drill; v2c used 3)
- MAX_INGEST_TRIPLES = None (full); 5000 (smoke)
- N_ANCHORS = 100 (full; same as v2c)
- N_RELATION_SAMPLES = 20 (full; same as v2c)
- K_SET = 16 (full; same as v2c)
- K_CONSENSUS = 10 (full; consensus-restart count for co-cluster matrix); 3 (smoke)
- JACCARD_CLUSTER_TAU = 0.30

## Wall estimate

Smoke benchmark: 277s for 1 seed / 5000 triples / N=1024 / 20 anchors / 4 arms
(K_CONSENSUS=3, n_rel_samples=8, k_set=12).

Full scaling:
- Triples 40x (5000 -> 200k); ingest is linear -> ingest ~10x at higher N
- N_DIM 4x (1024 -> 4096); score_all is O(n_ent * n_dim) per call; 4x heavier
- N_ANCHORS 5x (20 -> 100); n_rel_samples 2.5x; k_set 1.3x; net ~16x more
  score_all calls per arm
- Per arm: ~50-90min on remote_cpu BLAS at 100-300ms/score_all
- 4 arms per seed: ~3.5-6h per seed
- 5 seeds: 17-30h total wall WITHOUT seed parallelism

This is too long for a single dispatch; per-seed checkpointing means each seed
write_partial lands independently. Set --timeout 21600s (6h) per seed-batch, which
covers 1-2 seeds per spawn cycle. Remaining seeds resume from checkpoint on next
spawn cycle.

PROT-019: N_DIM=4096 requires --timeout >= 3600s. 21600 satisfies.

## Routing

remote_cpu_queue (CPU-bound: numpy + torch.matmul on CPU; substrate primitives
are dense BLAS).

## Recovery paths if v2d HARD_FAILs

If consensus_gap < 0.01 even with three coupled fixes, the substrate-native
self-mapping ceiling has been reached on the current char_trigram-encoded
relational substrate. Recovery options (per drill):
- Atomize META: "char-trigram + KGStore + 2-hop Jaccard at full Store scope is
  mechanism-null even with degree-preserving null + IRF + consensus."
- Escalate to mechanism-substitution (richer encoding via cert-trail metadata
  bundling) as v2e -- 5-7 cycle effort, not 1 cycle.

If MIDDLE_BAND, ablation arm diagnostics will discriminate which single fix is
dominant; follow-up cell adds the missing fix.

## Promotion candidates if v2d HARD_PASS

Two new hdlab primitives become chain-grade-promotion candidates per drill:
- hdlab/relational_weighting.py (IRF-weighted Hebbian write)
- hdlab/configuration_null.py (degree-preserving relation-rewire substrate-native control)

These close 2 of 7 hdlab/ backlog items.
