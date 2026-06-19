# exp_dev hand-off -- research: substrate-direct generative language modeling (3x drill)

Filed-by: research sub-agent, 2026-06-04
Trigger: notes/research_drill_substrate_direct_generative_language_modeling_3x_2026-06-04.md
Pause state: CHECK data/orchestrator_paused.flag before dispatching any anchor below.

Per [[feedback-no-experiment-design-in-prompts]]: this file names anchor candidates and
context pointers only. exp_dev designs sweep grids, threshold formulas, queue assignments,
and HF/HP numerical bounds without further input from research.

---

## Background

Full 3x algebraic drill on substrate-direct generative char-LM at N=8192 with all validated
bio-primitives composed. Key findings:
  - Coverage-based perplexity model predicts ppl ~ 36 (single substrate, no cf-RPE) or
    ppl ~ 10-12 (J=10 B4 ensemble), both IMPORTANT product gates.
  - cf-RPE (B3a) INVERTS for generative LM: write common patterns, not surprise.
    This is a USE-CASE BIFURCATION finding -- B3a direction depends on task type.
  - CHEAP TEST: ~5-30 min CPU, $0, directly answers whether substrate-direct LM is viable.
    No other test in cap_map history has been this cheap vs this decisive.
  - K*_corr ~ 4-5 (single substrate), 5-6 (J=10): consistent with today's empirical K*=4.
  - P_deflated(ppl < 20 at J=10) = 0.25 (MIDDLE-BAND most likely at P=0.55).

Pre-reg bands (LOCKED by research drill):
  HARD-PASS single substrate: ppl_T1 < 20
  MIDDLE-BAND: ppl_T1 20-60
  HARD-FAIL: ppl_T1 > 60

---

## Anchor Candidates (rank-ordered by decisiveness and cheapness)

### 1. T1 -- Single substrate char-LM on Wikitext-2 (cheapest decisive test)
- Anchor pointer: N=8192; f=0.02 DG-sparse; K=5 position-binding; J=1; B3a DISABLED; B6 D-ECR.
  One-pass Hebbian writes on Wikitext-2 train split. Eval: held-out ppl on test split.
- Substrate-product reading: if HARD-PASS (ppl<20), substrate-direct LM is product-viable
  at substrate-class scale WITHOUT ensemble -- immediate product path. If MIDDLE-BAND (20-60),
  ensemble (J=10) is the next gate. If HARD-FAIL (>60), cf-RPE inversion or coverage model
  is broken -- run T4 diagnostic immediately.
- Tier hint: CPU smoke, ~5-30 min wall, $0. Laptop CPU sufficient.
- Why-now: Cheapest decisive cap_map experiment ever. No GPU needed. No blocker.

### 2. T2 -- J=10 ensemble char-LM on Wikitext-2 (HARD-PASS territory test)
- Anchor pointer: Same as T1 but J=10 independent sub-substrates with product-of-experts
  aggregation. Tests algebraic prediction ppl ~ 10-12 at J=10.
- Substrate-product reading: if ppl < 15, substrate-direct LM at J=10 is competitive with
  deep char-transformers (64L, ppl~26) at 370x lower inference cost -- primary product claim.
  If ppl > 30, independence assumption fails (correlated codebooks) or coverage model wrong.
- Tier hint: CPU (10 parallel sub-substrates); ~30-60 min wall; $0. Embarrassingly parallel.
- Why-now: Directly tests the HARD-PASS product claim. Runs in parallel with T1.

### 3. T3 -- K sweep (K=3,5,8) at N=8192, J=1, no B3a
- Anchor pointer: ppl vs K curve at N=8192. Tests K*_capacity prediction (K* ~ 5 optimal).
  Runs 3 configurations in sequence or parallel.
- Substrate-product reading: if ppl minimum is at K=5-6 (predicted), confirms K* theory.
  If ppl minimum is at K=3, capacity is more constrained than algebraic model predicts.
  If ppl is still decreasing at K=8, single substrate K* is higher than predicted.
- Tier hint: CPU, ~15-30 min total for 3 K values; $0.
- Why-now: Resolves K* empirically for the first time on a real language task.

### 4. T4 -- B3a inversion test (cf-RPE ON vs OFF vs INVERTED)
- Anchor pointer: Three-way test: B3a disabled / B3a as-validated (write on high-surprise) /
  B3a inverted (write on low-surprise = common patterns). Measures ppl for each mode.
- Substrate-product reading: if inverted B3a achieves lowest ppl, confirms USE-CASE
  BIFURCATION: B3a direction is task-type specific. Major architectural finding.
  If B3a active (as-validated) achieves ppl > 60 but disabled achieves < 40, confirms
  that B3a is HARMFUL for LM in current polarity. If all three similar, B3a is irrelevant.
- Tier hint: CPU, ~30 min for 3 modes at N=8192; $0.
- Why-now: Directly tests cf-RPE inversion hypothesis from this drill. High leverage finding.

### 5. T5 -- STDP-only (E2, no position binding) at K=3 on Wikitext-2
- Anchor pointer: Does STDP-asymmetric alone achieve ppl < 30 at K=3 on Wikitext-2?
  Compares to E1 (position-binding) and combined E1+E2.
- Substrate-product reading: if STDP-only achieves ppl < 30, it is an alternative to
  position-binding for K=3 with lower implementation overhead. If combined E1+E2 beats
  either alone, synergy is confirmed -- STDP extends K* for position-binding substrate.
- Tier hint: CPU smoke, ~10 min; $0.
- Why-now: Completes the Bundle E empirical picture for LM tasks; lowest cost test.

---

## Context Pointers

- Research note (this drill):
  d:/AI/hd-instrument/notes/research_drill_substrate_direct_generative_language_modeling_3x_2026-06-04.md
- B4 cortical column prior validation: cap_map B4 row
- B6 D-ECR prior validation: cap_map B6 row (L=10000 composition HP)
- B2 DG sparse-expansion prior validation: cap_map B2 row (N=512 bigram HP)
- B3a cf-RPE prior validation: cap_map B3a row (13.8x write reduction HP)
- E1 position-binding prior validation: cap_map Bundle E E1 row (trigram HP, N=4096)
- E2 STDP-asymmetric prior validation: cap_map Bundle E E2 row (trigram HP)
- True-task-complexity K* formula (2x drill):
  d:/AI/hd-instrument/notes/research_drill_substrate_true_task_complexity_scaling_law_2x_2026-06-04.md
- K=8 HP (Bundle B task-complexity sweep): cap_map Bundle B row

---

## Contract

exp_dev designs all anchors from context pointers above and its own cap_map read.
Deliverables:
  - One queue entry per anchor (T1, T2 together; T3, T4, T5 lower priority)
  - Explicit pre-reg HP/MID/HF bands per anchor (T1 bands are LOCKED above; T2-T5 exp_dev sets)
  - Baseline comparison: include simple KN-5-gram as reference (confirms substrate adds value)
  - ASCII-only in all script output (feedback-ascii-only-in-scripts)
  - Per-cell JSON output for partial restarts (feedback-testbed-progress-logging)

## Autonomy Declaration

exp_dev has FULL autonomy over:
  - Anchor names, sweep grids, N choices within substrate-class (N=4096-16384)
  - Queue assignment (CPU for all T1-T5; no GPU needed at these scales)
  - Implementation of position-binding, DG-sparse, palimpsest decay, D-ECR, B4 ensemble
  - Exact threshold values for HF/HP bands for T2-T5 anchors
  - Whether to batch T1+T2+T3 in single run or separate queue entries
  - Corpus preprocessing (Wikitext-2 char-level; standard train/val/test splits)
