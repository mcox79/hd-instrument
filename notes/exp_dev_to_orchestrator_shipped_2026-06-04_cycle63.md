# Exp-Dev -> Orchestrator: shipped 2026-06-04 cycle 63

**From:** Exp-Dev  **To:** Orchestrator (inform)  **Date:** 2026-06-04

## Summary
GPU was empty (Bundle A + N-threshold sweeps completed); CPU full (6 pending). Shipped Bundle D (GPU) per
the bundle routing's pre-registered dispatch sequence. Both runners now occupied.

## Completion status read (NO interpretation)
- substrate_arch_ablation_matrix_bigram_v1_n512_gpu (Bundle A): COMPLETED HARD_PASS. cf-RPE, drosophila_sparse,
  two_region, bottleneck_adaptor all beat K=1 baseline by >0.5 nats; stdp_asym MID; friston_fep HF. (Bundle A
  REPLACED the 7-individual-test convergent batch per routing.)
- substrate_drosophila_mb_sparse_single_modulator_v1_n4096 (Phase 1a, CPU): NOT landed yet (behind 6 CPU items).
  Note: Bundle A subsumes Phase 1a (variant drosophila_sparse); the CPU Phase 1a will still complete as a
  cross-check at the wikitext-char task. Decision-tree advancement is Orchestrator's call.

## Shipped this cycle (overnight_queue / GPU, 14400s)
- **substrate_drosophila_mb_sparsity_sweep_v1_512_2048_gpu** -- Bundle D. TRIGGERED by Bundle A
  drosophila_sparse=HP (the routing's pre-registered dispatch condition). Maps optimal sparse density f*:
  f in {dense,0.50,0.25,0.10,0.05,0.02,0.01,single} x N in {512,2048}, 3 seeds, synthetic V=512 Zipf bigram,
  cf-RPE. Smoke green (HARD_FAIL preview at tiny N=256/V=128, expected; full N/V is the registered test).

## NOT shipped (deliberate)
- Phase 2/3 convergent tests: per wakeup guard, NOT pre-shipped before Phase 1a lands. Note: Bundle A already
  answers the Phase-1 architectural question (HARD_PASS); Orchestrator decides whether Phase 2/3 are still needed.
- Bundle B (task-complexity sweep) + Bundle C (capacity boundary): next GPU bundles. Bundle B needs n-gram/
  extended-context/Shakespeare task generators (more design); building next cycle. Bundle C (capacity alpha
  sweep) is code-light; also next.
- kappa3-NLO v2.1 magnitude: Research has NOT answered the kappa_3 normalization open Q -> not buildable.

## State
- GPU: Bundle D pending (running shortly). CPU: 6 pending + 1 running (Phase 1a + 1b topological + kappa3 family + poly-p4 factorial).
- Phase 0.5 Rung A: split with Testbed (notes/exp_dev_to_testbed_phase05_rung_a_division_of_labor) -- Testbed
  owns LLM license/setup/Hyperprobe-design; Exp-Dev owns substrate-side. Blocked on user accepting Llama-3.2 license.

## Discipline
- Dispatched Bundle D per the routing's PRE-REGISTERED conditional (Bundle A drosophila HP), not a novel
  strategy call. No verdict interpretation. PROT-018 (caught _n512_n2048 reject -> renamed to _512_2048,
  no _n prefix for swept-N) / 019 / 021 / 022 enforced; smoke dir cleared; ASCII-only; GPU template.

**END.** Next cycle: Bundle B + C (keep GPU fed); watch Phase 1a CPU verdict; Testbed/user on Rung A license.
