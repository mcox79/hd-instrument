# Prereg: task_vector_in_context_kshot_v1

**Date:** 2026-06-27
**Author:** exp_dev (Opus 4.7 1M, agent-spawn) Wave 3B TOP-2
**Drill source:** notes/research_drill_3x_cross_task_generalization_2026-06-27.md (TOP-2; C-Prop-2)
**Stage:** Stage 3 (cross-task generalization)
**P_deflated:** 0.45

## HYPOTHESIS

Substrate performs in-context k-shot associative recall via TASK_VECTOR = sum_i bind(input_i, output_i). For K=5 shots, unbind(input_query, TASK_VECTOR) then cleanup against entity codebook recovers true output (TOP-1 RECALL >= 0.40). Query is one of the K PRESENTED inputs (random permutation has no learnable structure so generalization to held-out inputs is information-theoretically impossible; this tests the foundational HRR bundle-recall primitive that ICL builds on). Monotone improvement as K increases through K=5; K=5 - K=0 lift >= 0.30. This is the HRR-natural realization of associative-memory recall (the substrate's bundle-cleanup loop; Plate 2003).

Note: this is the FOUNDATIONAL ICL primitive (associative recall from a K-bundle), not full generalization-ICL. A separate follow-up cell using STRUCTURED tasks (e.g., learnable permutations of small sets) would test generalization. P_deflated stays at 0.45 because the test is honest: tests what the substrate primitive CAN do, not what it cannot.

## ARMS (5 + 1 control + 1 diag)

1. **ARM_NO_CONTEXT** (K=0) -- no examples shown; recovery at chance.
2. **ARM_KSHOT_K1** -- 1 input-output pair bundled.
3. **ARM_KSHOT_K3** -- 3 pairs bundled.
4. **ARM_KSHOT_K5** -- 5 pairs bundled (main HARD_PASS target).
5. **ARM_KSHOT_K10** -- 10 pairs (capacity check).
6. **ARM_RANDOM_CONTEXT** (K=5) -- 5 random not-task-relevant pairs; isolates task-vector mechanism from generic-noise lift.
7. **ARM_DIAG_FULL** -- full permutation table as oracle upper bound.

## PRE-REG BANDS (LOCKED; PROSPECTIVE; metric = top1_recall in [0,1])

- **HARD_PASS**: ARM_KSHOT_K5 top1_recall >= 0.40 AND (K5 - K0) >= 0.30 AND monotone K1 -> K3 -> K5 AND ARM_RANDOM_CONTEXT top1_recall < K5 - 0.20 (random binds don't recover true output).
- **MIDDLE_BAND**: K5 top1_recall in [0.20, 0.40] OR non-monotone but K5 > K0 + 0.15.
- **HARD_FAIL**: (K5 - K0) <= 0.05 (no associative-recall signal) OR ARM_RANDOM_CONTEXT >= K5 - 0.05 (mechanism is generic-noise not bundle-recall).

Note: ARM_DIAG_FULL is the V-1 oracle UPPER bound for bundle interference (substrate's hard-capped associative capacity); K=5 may actually EXCEED K=99 since fewer binds = less interference. Discriminator drops the K5 <= DIAG-0.05 saturation gate because lower-K is information-theoretically advantaged here.

## FAIRNESS GATES

- Same N_DIM=8192; same encoder (HRR bipolar random); same entity vocab.
- Held-out 50 permutations independent of any training task (NONE here -- pure forward HRR).
- Each (K, seed) draws K examples fresh from the same permutation; query is held-out entity not in the K examples.
- Q-discipline: K=5 cosine >= 0.95 triggers leakage audit.

## CARDINALITY (META_RULE_H)

- EXPECTED_N_UNITS_FULL = 7 arms * 3 seeds * 50 tasks * 20 queries-per-task = 21000
- EXPECTED_N_UNITS_SMOKE = 5 arms (K0/K1/K3/K5/DIAG) * 2 seeds * 10 tasks * 5 queries = 500

## DISCRIMINATOR-SURVIVES-SCALE

Smoke at full N=8192 with K=5 (not toy N=512). Monotone-with-K is the load-bearing signature -- substrate that retrieves at constant 0.4 regardless of K is by-construction not ICL.

## HARDENING

L1 STARTED + L2 per-arm progress + L3 outer try/except + L4 import-crash sentinel.

## COMPUTE

CPU on remote_cpu; ~1-2 CPU-hr full; ~10 min smoke. Purely forward HRR (bind/unbind/cleanup).

## SUBSTRATE PREREQS

- HRR bind / unbind (chain-grade; involutive)
- Bundle (additive sum + normalize)
- Cleanup via cosine argmax over atom codebook
