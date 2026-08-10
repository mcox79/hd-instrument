# Design: DISCRIMINATOR iter-2 -- strengthen top-down coherence + ToM relation-gating, drop the bottom-up drag

Director design note (2026-08-10, self-drive). One mechanism-indicated iteration on 79c354a6d. SHAPE + pointers; exp_dev designs params.

## Why (iter-1 = 79c354a6d, DISK-VET'd)
First SCRAMBLE-CLEAN discriminator of the program (beats the ARC-sibling prior art, whose shuffled control never fully collapsed). Real-but-WEAK:
- Scramble collapses hard on all 3 arms -- on a scrambled graph the discriminator barely FIRES (1.3% vs 40% real) = it finds no coherent structure to lock onto (the top-down-control signature; the mechanism is REAL).
- But real margins ~0 (A -0.004 / B -0.010 / C -0.005 vs BoW) -- matches BoW, doesn't beat it. no-regression holds.
- KEY MECHANISM FINDING: raw multi-cue CONVERGENCE-COUNT is a NET DRAG. Arm C's learner over-weighted it (w0=0.123) because it correlates on TRAIN, but it does NOT generalize (dense graph -> convergence-count non-discriminative). Ablation dropping convergence-count -> real margin +0.013 (POSITIVE, still < +0.02 MIDDLE floor) with scramble deeply collapsed (-0.167). => the generalizable signal is the TOP-DOWN features (path-directness, relation-gating-delta, coherence), NOT bottom-up convergence. This maps to the brain: bottom-up flood does not discriminate; top-down semantic-control does.

## What to change (ONE mechanism-indicated iteration)
1. DROP raw convergence-count entirely (net drag + overfit trap).
2. STRENGTHEN the COHERENCE feature = the brain's DOMINANT top-down signal (DMN/AG situation-model constraint). Iter-1's "backward abductive coherence" is likely a thin scalar. Make it a proper retrieve-VALIDATE check via the owned Stage-2A loop: does the candidate, combined with its crutch path, form a COHERENT CONTINUATION of the context's event/mental-state structure (not just get reached by it)? This is the highest-value strengthening.
3. Make RELATION-GATING ToM-AWARE (SIQa is social/mental-state inference -> the mentalizing network). Gate on ATOMIC's mental-state relations by question type: motivation/"why...want" -> xIntent/xWant; feeling/"how...feel" -> xReact/oReact; consequence/"what happens next" -> xEffect/oEffect/xWant. Precise ToM-relation gating, not coarse question-type buckets.
4. KEEP path-directness/specificity (short, non-hub, typed path).

## Arms
- D1 = top-down features only (directness + ToM-relation-gating + strengthened coherence), fixed principled weights.
- D2 = same features, LEARNED weighting (held-out), scramble-controlled -- does learning help now that the drag feature is gone + coherence is stronger? (guards against the iter-1 overfit; report weights.)

## HARD-PASS shape (exp_dev sets bands); CONTROL is the whole game
1. Beats BoW on covered subset: target >=+0.05; a scramble-clean +0.02-0.05 = MIDDLE_BAND = real progress (iter-1's ablation already at +0.013).
2. SCRAMBLE COLLAPSES (load-bearing) -- must stay collapsed (iter-1 set the bar: scramble barely fires).
3. NO-REGRESSION overall via abstain gate.
4. Per-feature ablation -- WHICH top-down feature carries it (esp. is strengthened coherence the driver, as the brain predicts?).

## Wire-don't-island / pointers
- Extend experiments/exp_crutch_discriminative_selection_multicue_v1.py (iter-1 cell; reuse its evidence-gathering + positive-control + scramble harness; the GATE_THRESH median-of-positive-margins fix is already in).
- Stage-2A retrieve-VALIDATE loop (hdlab, HARD_PASS) = the coherence organ. hub-penalty. Crutch data/cskg_foundation (ATOMIC mental-state relations). Benchmark data/corpora/social_iqa.

## Honest deflator / exit
Discrimination on dense commonsense graphs is known-hard; iter-1 is real-but-weak. If iter-2 ALSO lands real-but-small (scramble-clean, < +0.05), that is the mechanism-indicated signal to STOP grinding discrimination and do the honest ceiling synthesis: the glass-box crutch-retrieval-discrimination path tops out near BoW for SIQa (itself a meaningful, evidence-rich conclusion) -- then the store's lesson applies (final selection may need the full situation-model loop, i.e. the extraction wall re-enters). This is the LAST discrimination-feature grind before that synthesis.

## Guardrails
Branch dataprep/mcguffey-graded-corpus. ONE variable (top-down feature strengthening). Real held-out dev. self-test PASS -> smoke -> FULL 3-seed. Resumable. Targeted commits (git SLOW). VET on disk; scramble load-bearing.
