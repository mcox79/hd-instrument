# Prereg: online_conv_oneshot_taskvec_hippo_v1

**Date:** 2026-06-27
**Author:** exp_dev (Opus 4.7 1M, agent-spawn) — Stage 3 USER concern #4 unblocker
**Drill source:** notes/research_drill_2x_online_learning_conversation_primitive_stage3_2026-06-27.md
**Handoff:** notes/exp_dev_handoff_research_drill_2x_online_learning_conversation_primitive_stage3_2026-06-27.md (Anchor #1)
**Stage:** Stage 3 compositional understanding (USER pivot 2026-06-26 LOCKED)
**P_deflated:** 0.45

## HYPOTHESIS

Substrate composes 5 chain-grade primitives (HRR task-vector ICL bundle + sparse-DG/dense-cortex
hippo handoff with N_replay=5 between-turn consolidation + refuse-gate V_REL=256 OOD detection +
CRISPR continual-learning append-only + multi-bank context partitioning) into a glass-box
conversational online-learning capability: in a synthetic 10-turn dialogue with single-shot fact
injections at turns 3 (allergy) and 7 (name), the substrate retrieves BOTH facts jointly at turn 10
("what should Alice avoid?") at top-1 >= 0.85, while a vanilla-retrieval baseline collapses to
<= 0.30 (forgetting). This is the M3-USER-concern-#4 unblocker (online learning during
conversation) and screen-recordable as the M3 demo.

## ARMS (5)

1. **ARM_VANILLA_RETRIEVAL** -- baseline; concatenates last-K-turn raw vectors, cosines to query
   against entity codebook. NO task-vector binding, NO cortex_hippo, NO refuse-gate. Expected to
   FORGET turn-3 fact by turn-10 query.
2. **ARM_TASKVEC_ONLY** -- substrate's task_vector_in_context_kshot_v1 primitive applied per turn
   (CG smoke today): every utterance's role->filler bind accumulates in TV. Query unbinds at turn 10.
   No cortex consolidation. Expected partial: bundle saturates at ~10 binds; turn-3 may degrade.
3. **ARM_TASKVEC_PLUS_HIPPO** (MECHANISM) -- full stack:
   - per-turn: bind(role, filler) -> in-context TV bundle
   - between-turn: sparse-DG hippo write (k-WTA 0.1) + 5-cycle uniform replay to dense cortex
   - turn 10 query: refuse-gate V_REL=256 first (is query in-context?) then unbind from TV +
     cortex_readout; cleanup by argmax cosine.
4. **ARM_ORACLE** -- knows facts directly via lookup table mapping (Alice, allergy) -> peanuts.
   Upper-bound sanity ceiling. No mechanism; just direct dictionary access.
5. **ARM_RANDOM_INJECT** -- control: at turns 3 & 7 inject RANDOM facts (not Alice-allergy and
   not Alice-name). Same mechanism as TASKVEC_ONLY otherwise. Expected ~chance.

## PRE-REG BANDS (LOCKED at module init; PROSPECTIVE; metric = top1_integrated_recall in [0,1])

**HARD_PASS (chain-grade-eligible):**
- ARM_TASKVEC_PLUS_HIPPO integrated_query_acc >= 0.85 (turn-10 joint-fact retrieval)
- ARM_VANILLA_RETRIEVAL integrated_query_acc <= 0.30 (baseline forgets)
- ARM_ORACLE integrated_query_acc >= 0.95 (sanity ceiling)
- ARM_RANDOM_INJECT integrated_query_acc in [0.00, 0.30] (control sanity)
- delta(TASKVEC_PLUS_HIPPO - VANILLA) >= +0.50
- delta(TASKVEC_PLUS_HIPPO - TASKVEC_ONLY) >= +0.05 (cortex_hippo measurable beyond bundle)
- arms_distinct = True (SHA-256 of per-arm prediction sequences differ for >= 3/C(N,2) pairs)
- cv across seeds < 0.15 for TASKVEC_PLUS_HIPPO
- cardinality_ok = True (arms x seeds x scenarios all complete)

**MIDDLE_BAND:**
- TASKVEC_PLUS_HIPPO in [0.50, 0.85)
- OR delta(TASKVEC_PLUS_HIPPO - VANILLA) in [+0.20, +0.50]

**HARD_FAIL:**
- TASKVEC_PLUS_HIPPO < 0.50 (substrate cannot do conversational integration)
- OR TASKVEC_PLUS_HIPPO ~= VANILLA (no integration signal; delta < 0.10)
- OR ARM_ORACLE < 0.80 (pipeline broken)
- OR cardinality breach OR substrate-only-decode gate violated

## DISCRIMINATOR-SURVIVES-SCALE (USER 2026-06-26 LOCKED)

Smoke runs at FULL conversational scale (10-turn, 2-fact injection, N=2048 dims).
Smoke verifies the 10-turn integration discriminator FIRES (not a 3-turn re-test of task_vector_kshot).
Full extends only n_scenarios and N_DIM.

## FAIRNESS GATES (META_RULE_AA / META_RULE_AF)

- Same N_DIM per run; same encoder (HRR bipolar bind/unbind); same entity vocab.
- Per-trial randomization: allergy in {peanuts, shellfish, gluten, dairy, eggs}; name in
  {Alice, Bob, Carol, Dan, Eve}; role/filler positions shuffled. Prevents content-leak (bias-N).
- ARM_VANILLA uses NO online-learning mechanism (cosine to concatenated turn vectors only).
- ARM_TASKVEC_PLUS_HIPPO has NO oracle access; must integrate facts purely via composition.
- arms_distinct verified via SHA-256 hash of per-scenario top-1 prediction sequences (META_RULE_AF).

## CARDINALITY (META_RULE_H)

- EXPECTED_N_UNITS_SMOKE = 5 arms * 2 seeds * 30 scenarios = 300
- EXPECTED_N_UNITS_FULL  = 5 arms * 3 seeds * 100 scenarios = 1500

## HARDENING

L1 STARTED + L2 per-arm + L3 outer try/except + L4 import-crash sentinel.
SystemExit re-raise BEFORE BaseException.
__main__ guard. Atomic-write metrics.json (META_RULE_AH).

## SUBSTRATE-ONLY-DECODE GATE

n_llm_calls_total == 0 (verified in metrics.json).

## VERSION MARKERS (in metrics.json)

anchor_name, N_DIM, V_ENTITIES, n_turns, n_facts_injected, fact_turn_indices,
N_h, N_c, hippo_sparsity, n_replay_cycles, refuse_threshold, alpha_decay, seeds, n_scenarios, RUN_MODE.

## COMPUTE

CPU on remote_cpu_queue (per USER 2026-06-27 NO_LOCAL); HRR is matmul-light.
Smoke: ~10-15 min wall. Full: ~30-60 min wall.

## SUBSTRATE PREREQS (composed; ALL CG today)

- HRR bind/unbind (chain-grade; involutive) -- hdlab/binding.py analog
- Bundle additive sum + normalize -- hdlab/bundling.py analog
- task_vector_in_context_kshot_v1 smoke CG (K1=K3=1.000 K5=0.980 K5-K0=+0.97 mono=True)
- cortex_hippo_handoff smoke CG (FULL=1.000 NO_REPLAY=0.003 gap=+0.998)
- continual_learning_crispr CG-banked (forget=0.006)
- refuse_gate V_REL=256 CG-banked
- multi-bank partition CG-banked
