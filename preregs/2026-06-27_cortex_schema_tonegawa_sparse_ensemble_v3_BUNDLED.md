# PRE-REG: cortex_schema_tonegawa_sparse_ensemble_v3_BUNDLED

**Date:** 2026-06-27
**Author:** exp_dev (Opus 4.7-1M agent spawn, Research team-lead dispatch)
**Barrier:** B3 (cortex schema integration) - Wave 2 redesign
**Skunkworks audit:** notes/skunkworks_mechanism_null_audit_wave2_2026-06-27.md (commit edee21b3) Wave 2F TOP-1 path
**Predecessor:** experiments/exp_cortex_schema_tonegawa_sparse_ensemble_v2.py

## TRIGGERS v3 OVER v2

v2 used isolated-bank retrieval (each cluster owns its own row in sparse_bank_k20 shape (K, N_SCHEMA_CELLS)). When clusters are separated (BCC=0.45), per-row cosine/overlap recovery is trivial because row-rank is preserved -- PROTOTYPE_CENTROID and TONEGAWA recover most schemas at small K. The interference advantage of sparse codes (Treves-Rolls ~10x at sparsity 0.01) is HIDDEN by isolated-bank architecture.

Skunkworks Wave 2F TOP-1 fix: BUNDLED capacity test where all K schemas share ONE substrate vector via XOR-binding.

## HYPOTHESIS

In bundled-substrate regime:
- TONEGAWA SPARSE: lower per-schema interference because each schema contributes k=20 of N=2000 nonzero entries (1% load per schema)
- PROTOTYPE_CENTROID: every schema contributes ~all-N entries (dense load); interference accumulates ~K times faster
- DIAG_RANDOM_SPARSE: tests false-accept (no structural overlap with queries)

Treves-Rolls capacity scaling predicts TONEGAWA capacity@95%-recall ~ 10x PROTOTYPE at 1% sparsity. We accept >= 1.5x as load-bearing evidence.

## ARCHITECTURE

```
TONEGAWA_BUNDLED:
  S_bundle = sum_k XOR(schema_id_k, sparse_code_k)  where sparse_code_k = k-WTA(W @ centroid_k)
  Query: probe = XOR(schema_id_k, S_bundle); decode to sparse_q via sign;
         match k-WTA(W @ query) overlap

PROTOTYPE_BUNDLED:
  C_bundle = sum_k XOR(schema_id_k, sign(centroid_k))
  Query: probe = XOR(schema_id_k, C_bundle); cosine to query_centroid

RANDOM_BUNDLED:
  S_bundle = sum_k XOR(schema_id_k, random_k_subset_bipolar)
  Same scoring as TONEGAWA but with random sparse codes
```

## CAPACITY SWEEP

K in {25, 50, 100, 200} (full); {10, 25} smoke.
Per K: measure recall@TOP_1 across N_QUERIES_PER_CLUSTER * K queries.
capacity@95%-recall = max K such that recall@1 >= 0.95.

## ARMS (3)

1. ARM_PROTOTYPE_CENTROID_BUNDLED -- dense bundled baseline
2. ARM_TONEGAWA_SPARSE_K20_BUNDLED -- 1% sparse bundled (PRIMARY)
3. ARM_DIAG_RANDOM_SPARSE_BUNDLED -- random k-subset bundled (false-accept floor)

## PRE-REG BANDS

**HARD_PASS:**
- TONEGAWA capacity >= 1.5 * PROTOTYPE capacity
- AND DIAG capacity <= 0.5 * TONEGAWA capacity (random sparse doesn't structurally match)
- AND cv across seeds < 0.10 (full only)

**MIDDLE_BAND:**
- TONEGAWA capacity in [1.1, 1.5)x PROTOTYPE (lift but not Treves-Rolls scaling)

**HARD_FAIL:**
- DIAG capacity >= TONEGAWA capacity (random matches structure; mechanism null)
- OR TONEGAWA capacity <= PROTOTYPE capacity (sparse-code interference NOT lower than dense)
- OR cardinality breach

## REGIME

N_DIM = N_SCHEMA_CELLS = 2000 (BUNDLED arch requires equal dimension)
K_SPARSE=20 (1% sparsity, Tonegawa-grounded)
N_PER_CLUSTER=10
BCC=0.30 (harder than v2's 0.45; better discrimination in bundled regime)
WITHIN_CLUSTER_NOISE=0.70
Seeds: full=[7,17,23]; smoke=[7].

## CARDINALITY_OK

EXPECTED_N_UNITS = 3 arms * len(K_SWEEP) * n_seeds.
Full = 3*4*3 = 36; smoke = 3*2*1 = 6.

## FAIRNESS (META_RULE_AA)

- All arms operate on SAME bundled-substrate regime (one S_bundle of length N_DIM)
- Schema IDs are fresh-random per seed (no leakage from cluster generation)
- Discriminator FIRES at K_smallest in smoke (capacity > K_smallest required to show trend)
- TONEGAWA vs PROTOTYPE diff is purely architectural (sparse-vs-dense per-schema contribution)

## DISPATCH

Queue: remote_cpu_queue (~3 CPU-hr full).
Timeout: 10800s (3 hours wall).

## EXPECTED OUTCOMES

- HARD_PASS: Treves-Rolls sparse-code capacity advantage confirmed in our substrate
- MIDDLE_BAND: partial lift; may need k-sensitivity sweep (k=10 vs k=40)
- HARD_FAIL via TONEGAWA<=PROTOTYPE: bundled-substrate interference doesn't favor sparse codes in HRR-style binding
