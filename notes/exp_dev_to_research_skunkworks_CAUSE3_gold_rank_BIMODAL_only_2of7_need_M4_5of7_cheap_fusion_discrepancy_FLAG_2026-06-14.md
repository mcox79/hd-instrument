# Exp-Dev (Prover) -> Research (Director) + Skunkworks (Auditor): Cause-3 gold-rank-depth RESCOPES M4 -- present-gold rank is BIMODAL; only 2/7 in-coverage need representation-level M4; 5/7 are shallow-medium. PLUS discrepancy FLAG: 3 questions have gold at bge rank 2-3 yet scored ~0 (union/fusion or id-match dropping shallow gold -> cheap win independent of M4).

**From:** EXP-DEV (Prover)  **Date:** 2026-06-14  **Tag:** F1_HELDOUT_DECOMPOSED (Cause-3 scope)
**Re:** Scoping the deferred M4 decision (DECISION 35b) with a CHEAP diagnostic (NOT the M4 build). For each in-coverage held-out q, ranked ALL 20,787 atoms by bge cosine and found where the PRESENT gold sits. 7th rule (characterize before committing). ACTUAL (10th rule).
**Experiment:** `experiments/exp_substrate_cause3_gold_rank_depth_heldout_cpu_v1.py` (remote; bge cache).

## Result: present-gold rank is BIMODAL (median 21)

| qid | n_present | best_gold_rank | gold_score | top1_score | band |
|---|---|---|---|---|---|
| Q61-A | 2 | 2 | 0.7153 | 0.7534 | SHALLOW |
| Q64-G | 3 | 2 | 0.7248 | 0.7282 | SHALLOW |
| Q60-G | 4 | 3 | 0.7594 | 0.7938 | SHALLOW |
| Q55-B | 1 | 21 | 0.6675 | 0.7417 | MEDIUM |
| Q54-A | 1 | 69 | 0.6054 | 0.6900 | MEDIUM |
| Q63-A | 2 | 539 | 0.5863 | 0.7214 | DEEP |
| Q62-B | 2 | 3635 | 0.5481 | 0.6726 | DEEP |

Buckets: top5=3, top20=0, top100=2, deeper=2. Median best-gold-rank=21.

## This RESCOPES M4 (the key input for the USER decision)
- **Only 2/7 (Q62 rank 3635, Q63 rank 539) genuinely need representation-level paraphrase-invariance (M4a-d).** For these bge places the held-out paraphrase FAR from its gold -- no cutoff tweak helps.
- **2/7 (Q54 rank 69, Q55 rank 21) are MEDIUM** -- a top-K increase to 50-100 surfaces them. Cheap.
- **3/7 (Q60, Q61, Q64) are SHALLOW (rank 2-3)** -- the gold is already at the TOP of bge ranking. These need NO retrieval work at all.
- So M4 (heavy, weeks) is genuinely required for AT MOST 2/7 in-coverage questions. The earlier "capability does not transfer, period" framing was too pessimistic: the representation mostly DOES place gold near the top; the failure is downstream (cutoff + fusion) for 5/7.

## DISCREPANCY FLAG (verify-before-asserting; needs reconciliation)
3 questions (Q60 gold@rank3 score0.759, Q61 gold@rank2 score0.715, Q64 gold@rank2 score0.725) have gold WELL within bge top-5 AND above the tau=0.70 floor -- yet the canonical union scorer scored them tp=0 (Q60/Q64) / tp=1 (Q61). bge alone would retrieve these; the union answer path does not.

**Hypotheses (unconfirmed -- needs a reconciliation run before asserting):**
1. answer_type_A_union mixes algebra-HRR candidates that OUTRANK the correct bge gold, pushing it out of the final top-5.
2. id-matching mismatch: the converted held-out file's gold qualification vs the scorer's _BARE_TO_QID map drops the match (my diagnostic uses _short normalization; the scorer uses qualified-id matching -- they may disagree).

EITHER hypothesis, if confirmed, is a CHEAP capability win INDEPENDENT of M4: fixing fusion or id-matching recovers 3/7 in-coverage directly.

## Recommendation (rescopes the USER M4 decision)
Before committing to heavy M4, run the cheap intermediate (1 cycle, my lane, unblocked):
1. **Reconcile the rank-2-3-but-tp-0 discrepancy** (fusion vs id-match) -- likely recovers 3/7.
2. **Test top-K=50** in answer_type_A_union -- likely recovers the 2/7 medium (Q54/Q55).
3. Re-measure in-coverage F1. If it lifts from 0.029 toward ~0.5 on 5/7, **heavy M4 is only needed for the 2/7 deep cases** -- a much smaller, better-justified investment.

This is the 7th-rule cheap-alternative-first discipline applied to M4 (as it was to M1): characterize + try the cheap fix before the expensive representation work. M4 stays directionally justified but its SCOPE shrinks from "all in-coverage" to "2/7 deep cases."

I can run steps 1-2 next (unblocked, my lane) if the Director/USER approves -- it does NOT require ingest or Testbed.

-- EXP-DEV (Prover)
