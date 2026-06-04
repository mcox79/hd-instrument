# Exp-Dev -> Orchestrator: shipped 2026-06-04 cycle 62

**From:** Exp-Dev  **To:** Orchestrator (inform)  **Date:** 2026-06-04

## Summary
Shipped the full Convergent Brain-Architecture **Phase 1** batch (3 tests) from
notes/routing_convergent_brain_architecture_empirical_batch_2026-06-04.md, plus PP-50 v4 earlier this
session. Both runners now occupied (CPU 6 pending +1 running; GPU 1 pending). Per user directive this cycle:
ship all new high-priority tests, ~5 at a time, keep BOTH CPU and GPU busy.

## Shipped this cycle
1. **substrate_drosophila_mb_sparse_single_modulator_v1_n4096** (CPU, 14400s) -- Phase 1a, the CHEAPEST
   DECISIVE TEST gating Phase 2/3. Dense-bipolar-K8 vs sparse-{0,1}-f0.05 + single cf-RPE. Bands in nats.
   Smoke green (gap~0 at N=256 expected; sparse advantage needs full N=4096).
2. **substrate_rem_replay_retrieval_energy_baseline_v1_n8192_gpu** (GPU, 21600s) -- Phase 1c, routed to the
   OWNED GPU to keep it occupied. Crick-Mitchison (1983) REM UNLEARNING (NOT basin-strengthening -- my first
   mechanism raised energy; unlearning is the literature-correct consolidation). Smoke: unlearning reduces
   energy (B 75-78%, C 94-96%); the N>=8192-vs-N=4096 conditional is the full-scale question.
3. **substrate_topological_beta0_mapper_baseline_v1_n1024** (CPU, 7200s) -- Phase 1b, EXPLORATORY. beta_0
   union-find connectivity + Mapper + kappa_2-invariant drift KS. Smoke PREVIEW: beta_0 does NOT detect
   random kappa_2-invariant swaps (ks_p=0.999) -> likely HARD_FAIL at full scale (random->random swaps are
   topologically invisible). Shipped honest/un-rigged; a clean negative is still a cap_map data point.

## Earlier this session (already committed)
- **pp50_lambda1_nsweep_tw_vs_hadamard_v4_gpu** -- Research's stable-observable reformulation (lambda_1
  power iteration; std across seeds) replacing the unstable v2/v3 sigma_sep ratio. COMPLETED: verdict
  MIDDLE_BAND (smoke had beta_std=0.700 Tracy-Widom; full grid landed MIDDLE -- Orchestrator interprets).
- substrate_polynomial_p4_bcm_factorial_rung1_v1_n512 (CPU, running).

## NOT shipped (deliberate)
- **Phase 2** (STDP / FEP / 2-region / bottleneck-adaptor): CONDITIONAL on Phase 1a outcome per the routing
  -- not pre-shipped (would be gated work).
- **Phase 3 convergent build** (~15-20h engineering): deferred; the routing says it can start in parallel but
  it is a multi-cycle engineering effort, not a one-cycle ship.
- **Full polynomial-p=4 primitive engineering**: the routing (line 312) explicitly SUPERSEDES it with the
  convergent architecture if Phase 1a HP. Holding (the p4 factorial empirical probe is already running).
- PP-50 sigma_sep v-anything: superseded by v4. kappa_3 NLO v2.1 magnitude: Research has NOT answered the
  exact-normalization open Q yet -> not buildable.

## Scope declarations
- No verdict interpretation (read metrics.json for completion status only).
- No padding: all 3 Phase-1 tests are explicitly drill-routed; Phase 2/3 correctly withheld.
- PROT-018/019/021/022 enforced; ASCII-only; smoke-checkpoint dirs cleared before each GPU ship (hit the
  PROT-021 stale-partial contamination twice on 1c -- cleared each time).

**END.** Next cycle: watch Phase 1a verdict (gates Phase 2 dispatch); if 1a HP, begin Phase 3 convergent
engineering; else dispatch Phase 2 isolation tests.
