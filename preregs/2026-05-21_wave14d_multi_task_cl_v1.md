# Pre-registration: wave14d_multi_task_cl_v1

Date: 2026-05-21
Status: Pre-registered, gated
Priority: Strategy push #3 (Bet B Tier-1 KILLER)
Author: experiment_dev session, pipeline tick 62

## Why

R5 spec: train substrate on Corpus A (English wiki / repo text), then B (byte-shuffled
A — Phase-B established shift), then C (Python source code — genuinely different
domain). Retention >= 80% on held-out A and B after C-phase; positive gain on C;
BWT >= 0 (no catastrophic forgetting).

This is the KILLER for "multi-task continual learning at production scale."
Closes one of the two remaining Tier-1 unresolved rows.

## Mechanism (per R5)

- Phase A: train W on corpus_A (existing wave14b_cl_phase_a baseline).
- Phase B: continue training on corpus_B with 10% replay of A.
- Phase C: continue training on corpus_C (Python) with 10% replay of A+B (5%+5%).
- Multi-probe at end: bpc on held-out A/B/C; retention ratios; BWT.

## Verdict labels (per R5 verdict logic)

- BET_B_PASS (retention_A >= 0.80 AND retention_B >= 0.80 AND gain_C > 0 AND BWT >= 0)
- BET_B_PARTIAL (retention_A >= 0.80 AND retention_B in [0.50, 0.80] AND gain_C > 0)
- BET_B_KILLED (any retention < 0.50)
- BET_B_INCONCLUSIVE

## Pre-armed rescues (PROT-004)

If BET_B_KILLED:
1. Larger replay fraction (20%, 30%) per Ibrahim 2024 5-25% recipe
2. Surprise-driven replay per SuRe (Hazard 2025)
3. Phase ordering shuffle (B first, then A, then C)
4. Smaller corpus_C to reduce shift magnitude
5. Continual phase-specific pool buckets (don't merge pools across phases)

## Runtime: ~10 min smoke, ~45-60 min full multi-seed
