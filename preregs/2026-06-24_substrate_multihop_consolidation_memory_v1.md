# Pre-reg: substrate_multihop_consolidation_memory_v1
Date: 2026-06-24
Author: exp_dev (Wave E retry)
Routing: remote_cpu_queue via orchestrator handoff
Lane: 1 (substrate-native; chance + intra-arm controls)

## Barrier addressed
Barrier 1: substrate 2-hop chained retrieval saturates around top1 ~ 0.65 vs 1-hop
ceiling of ~1.0. Prior decoder-side beta-sweeps did not break the ceiling.

## USER directive
Instead of decoder-side rescue, USE the chain-grade memory primitive: when a 2-hop
chain (A, R1, B) then (B, R2, C) is observed K_THRESH times, write a DIRECT compound
atom bind(A, R_compound(R1, R2), C) into W. Substrate then answers the 2-hop query
at 1-hop after consolidation: chain-grade top1 ~= 1.0 in the limit.

## Brain analogy
Squire-Wixted hippocampal-cortical consolidation: PFC consolidates frequent paths
from episodic hippocampal traces into direct cortical associations.

## Verify-the-referent (Skunkworks N1 discipline)
- exp_substrate_concept_kg_storage_retrieval_v1/metrics.json: verdict=MIDDLE_BAND (NOT chain-grade); USER citation of "top1=1.000 generalization" comes from SEMANTIC battery, not concept_kg itself. FLAGGED. We proceed: this cell builds on the concept_kg primitives (ingest_hebbian + chained retrieval) without claiming concept_kg was chain-grade.
- exp_hopfield_beta_sweep_v1/metrics.json: verdict=HARD_PASS but run_mode=smoke, elapsed=0.04s; not a load-bearing referent for the "naive=0.65" claim. We measure the naive 2-hop baseline IN-CELL (ARM_NAIVE_2HOP) and report it directly rather than citing the smoke beta-sweep.

## Mechanism
- V_C concepts, V_P primitive predicates + V_compound compound predicates (1 per ordered (R1,R2) pair observed >= K_THRESH times).
- pure-numpy HRR (the U1 chain-grade primitive); dense bipolar codebooks per seed.
- Hebbian-accumulate ingest: W = sum_i outer(E[o_i], E[s_i] * R[p_i] * sqrt(N)) / N.
- Consolidation: after streaming the 2-hop training set, count co-occurrences of
  (R1, R2) along each chain; for chains whose (R1, R2) ordered pair count >= K_THRESH,
  add the compound atom bind(A, R_compound(R1, R2), C) directly into W.
- Retrieval: 2-hop query (s, R1, R2, ?) uses BOTH (a) the naive chain (s,R1)->x_hat, then (x_hat,R2)->o_hat AND (b) the compound key (s, R_compound(R1,R2)). Substrate-side answer is the higher-confidence top1 (max score).

## Arms (4)
1. ARM_NAIVE_2HOP -- control; the standard chained-bind retrieval; no consolidation.
2. ARM_CONSOLIDATE_AFTER_THRESHOLD -- consolidation with K_THRESH=3; baseline test of the USER mechanism.
3. ARM_CONSOLIDATE_IMMEDIATE -- K_THRESH=1 (every 2-hop pair gets a compound atom); upper-bound test for "ceiling reachable".
4. ARM_HYBRID_NAIVE_PLUS_CONSOLIDATED -- consolidated atoms for frequent chains, naive for everything else (max-confidence pick); expected best operating point.

## Config
- V_C=200, V_P=10, V_compound=auto, N=8192, K_SET=20 distinct keys per evaluation chain.
- n_chains=300.
- seeds = [7, 17, 23].
- pure numpy; CPU; per-seed checkpoint via _seed_checkpoint helper.

## HARD bands (pre-reg; both directions of NEGATIVITY-BIAS check)
- HARD_PASS_BREAK_CEILING (chain-grade): best arm top1 >= 0.95 AND beats ARM_NAIVE_2HOP by >= 5x (multiplicative).
- HARD_PASS: best arm top1 >= 0.85 AND beats ARM_NAIVE_2HOP by >= 0.15 (additive).
- MIDDLE_BAND: best in (NAIVE, 0.85).
- HARD_FAIL: best arm top1 <= 0.75.

## Sanity rails (PROT-018 referent + by-construction-saturation guard)
- ARM_NAIVE_2HOP must NOT trivially hit top1 >= 0.90 (would mean the chained primitive is by-construction saturating at this V/M scale; verdict needs to be downgraded). Expected band: top1 in [0.40, 0.75]; if observed > 0.85, flag REPRODUCIBILITY_DIVERGENCE in verdict_msg.
- 1-hop oracle top1 (hop2 with ground-truth x; reported for context) must be >= 0.95 (proves the SECOND hop is sound; otherwise something is broken upstream).
- chance_top1 = 1 / V_C = 1/200 = 0.005; reported explicitly.

## Discriminator
- ARM_CONSOLIDATE_IMMEDIATE > ARM_NAIVE_2HOP isolates the compound-atom mechanism.
- ARM_HYBRID > ARM_CONSOLIDATE_IMMEDIATE proves the picker is doing useful work (NOT just consolidation).
- ARM_CONSOLIDATE_AFTER_THRESHOLD > ARM_NAIVE_2HOP at K_THRESH=3 proves consolidation works at realistic frequency.

## Timeout budget
- 1800s per queue spec; pure-numpy at N=8192, M ~ 600 train atoms, 4 arms x 3 seeds.

## Routing
- remote_cpu_queue via orchestrator handoff (no GPU needed; pure-numpy matmul).
- Anchor: substrate_multihop_consolidation_memory_v1 (no _n suffix; PROT-018 free, PROT-019 floor not triggered).
