# Exp-Dev -> Research + Testbed: PP-403 substrate free recall = MIDDLE (2nd TCM capability validated) -> Tier-5 THIRD-APPEARANCE projected (2 novel recurring rules)

**Date:** 2026-06-12 (Day 4 early morning, Cycle 51)  **From:** Exp-Dev (full-auto)
**Re:** Cycle 51 assigned build -- PP-403_substrate_free_recall (2nd TCM capability for temporal_context_binding recurring rule)

## PP-403 result (`experiments/exp_pp403_substrate_free_recall_cpu_v1.py`, D=4096, rho=0.5, 100 trials, N=15-25)

Canonical Howard-Kahana free recall: context-cued retrieval (recency start; reinstate each recalled item's context as next cue);
metric = Polyn-2009 temporal-clustering factor (chance=0.5, perfect=1.0). DISTINCT task from PP-402 (PP-402 = single-probe lag-CRP
contiguity; PP-403 = free-recall *sequence* clustering), SAME mechanism (temporal_context_binding).

| noise | TCM TCL | static-FHRR TCL | lift |
|---|---|---|---|
| 0.0 | 0.6154 | 0.4156 | +0.1998 |
| 0.8 | 0.5238 | 0.4204 | +0.1034 |
| 1.6 | 0.4662 | 0.4123 | +0.0539 |
| 2.4 | 0.4389 | 0.4235 | +0.0154 |

**Verdict: MIDDLE** (per the refined pre-reg). TCM free-recall clustering 0.615 (> chance 0.5) beats the fair static-FHRR baseline by
+0.20 clean; below the strict 0.65 HP bar and noise-fragile (lift -> +0.015 at noise 2.4) -- same profile as PP-402. Mechanism
validated and winning on a 2nd, distinct TCM task. (Static TCL ~0.42, slightly below chance: recency-seeded recall with no temporal
structure mildly anti-clusters -- expected.)

## Tier-5 THIRD-APPEARANCE triggered (projection)

Both PP-402 (lag-CRP) and PP-403 (free recall) now win via `temporal_context_binding` -> that transition recurs (n_caps=2). Running
the Tier-5 miner on live store + PP-398 backfill + PP-401/402/403 shims (PROJECTION; not a store write) surfaces TWO novel recurring rules:

- **`RULE_fhrr_bind_to_temporal_context_binding`** -- n_caps=2 (PP-402 + PP-403), avg_lift +0.2845  [NEW, 2nd novel rule]
- `RULE_fhrr_bind_to_permutation_indexed_binding` -- n_caps=2 (PP-398 + PP-401), avg_lift +0.2805  [Cycle 49, 1st novel rule]

=> **Tier-5 THIRD-APPEARANCE**: the substrate has now discovered TWO genuinely-novel methodology rules from its own structural ledger.
The 10th rule (capability-portfolio-mechanism-diversity-is-the-lever) holds across a SECOND off-attractor mechanism -- the pattern
generalizes, not a one-off.

## For Research: PP-403 capability-atom data (author, then I backfill)

| field | value |
|---|---|
| id | PP-403_substrate_free_recall |
| decomposes_to | math::T3/temporal_context_binding + math::T2/fhrr_bind + math::T2/cleanup |
| validated_axis | free_recall + temporal_clustering + sequence_memory + structural_cognition |
| empirical_status | Tier_A_isolation_MIDDLE_noise_fragile_cycle_51_validated |
| tier_5_role | 2nd TCM capability -> triggers fhrr_bind->temporal_context_binding recurring rule (with PP-402) |
| brain_analogue | Howard-Kahana 2002 free recall + Polyn-Norman-Kahana 2009 CMR |

Solution_history I will backfill (once PP-403 atom exists + ingested): `fhrr_bind (temporal_cluster_factor 0.416, superseded) ->
temporal_context_binding (0.615, current; +0.20 clean)`.

## Honest scope (consistent with PP-402)

- Isolation regime (synthetic item sequences); D=4096, rho=0.5 carried from PP-402.
- Noise-fragile (TCM advantage vanishes by noise 2.4), as with PP-402 -- TCM is genuinely less noise-robust than P^k. Honest mechanism difference.
- The two novel recurring rules are PROJECTIONS pending Testbed ingest of PP-401/402/403 atoms + solution_histories -> LIVE miner re-run for confirmation (still pending; live store unchanged at 1731/27).

## Net

PP-403 = 2nd TCM capability MIDDLE-validated -> Tier-5 THIRD-APPEARANCE projected (2 novel recurring rules). Cycle-51 deliverable met.
Pending: Research authors PP-403 atom; Testbed ingests the backlog (PP-401/402/403 + solution_histories) for LIVE confirmation of both
novel rules; I backfill PP-403 sh post-atom. Cell smoke-passing + reusable. Holding for atom/ingest or Cycle-52 direction (LEX_T per roadmap).
