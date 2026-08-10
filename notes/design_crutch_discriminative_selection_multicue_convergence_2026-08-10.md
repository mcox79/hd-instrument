# Design: DISCRIMINATIVE selection over the crutch spreading-activation candidate set

Director design note (2026-08-10, self-drive). Task SHAPE + pointers for exp_dev; exp_dev designs params. The wall is now DISCRIMINATION, not coverage.

## Why (VET'd, 508ee9b0d)
Coverage diagnosis settled it: crutch misses are 94% MECHANISM-MISS (answer reachable <=3 hops in CSKG; genuine-gap only 5.7%). Spreading-activation recovers reachability (coverage 0.25->0.78) BUT does NOT convert to comprehension: newly-covered accuracy 0.379 ~ BoW 0.344, and SCRAMBLE FAILS (scramble reaches 0.535 at k3; scramble argmax accuracy 0.521 > real 0.376). ROOT: CSKG is densely small-world -> within 2-3 hops you reach almost anything (incl wrong answers) -> reachability is NON-DISCRIMINATIVE. Raw-activation-argmax + CA3 attractor both fail. So the missing piece is a DISCRIMINATOR that picks the right reached fact -- identical in structure to the STORE arc's final-selection wall (candidate-retrieval solved to a shortlist; single-argmax was the wall -> context-validation's job).

## What to build (brain-foundational = multi-cue CONVERGENCE / coincidence-detection)
A discriminative selector over the spreading-activation candidate set for SIQa's 3-way MC:
- RETRIEVE: spreading-activation from MULTIPLE context+question SEED cues over CSKG, gated (k<=2, hub-penalty) -> a per-cue activation field. (reuse the diagnosis cell's spreading-activation.)
- DISCRIMINATE (the new piece): for each of the 3 answer candidates, score CONVERGENCE = how many DISTINCT context cues' activation reach the candidate's concept-neighborhood (coincidence detection), weighted by (i) relation-relevance -- the QUESTION TYPE gates which relation families count (e.g. a motivation/"why did X want" question weights xWant/xIntent/xReact edges, not generic association), and (ii) specificity (hub-penalty, validated at 1-hop). Pick argmax convergence.
- BRAIN MECHANISM: the right answer = the node where activation from SEVERAL cues CONVERGES; a scramble/random node is reached by ONE cue by chance, so multi-cue convergence is EXACTLY the signal that separates real from random. SHAPE = convergence over distinct-cue activations; POSITION = after retrieval, before selection; METRIC = beat scramble on the covered subset.

## Two arms to isolate the mechanism
- A: pure multi-cue convergence (distinct-cue count + specificity).
- B: convergence + RELATION-GATING (question-type -> relevant relation families). Tests whether relation-gating adds discrimination over pure convergence.

## HARD-PASS shape (exp_dev sets exact bands); the CONTROL is the whole game
1. Discriminator beats BoW by a real margin on the crutch-COVERED subset (target >=+0.05; a scramble-clean +0.02-0.05 = MIDDLE_BAND = real progress given known-hardness).
2. SCRAMBLE COLLAPSES (load-bearing): on a scrambled/random CSKG, the right candidate must NOT get more convergent support than wrong ones -- scramble margin must drop to ~chance. The raw prototype FAILED exactly here; this is the decisive test.
3. NO-REGRESSION: augment-not-replace -- keep BoW always-on; discriminator route fires only when the crutch covers >=2 candidates AND convergence margin is confident, else ABSTAIN->BoW (no-regression by construction).

## Wire-don't-island (reuse; check registry FIRST, READ THE CODE not the label)
- arc_retrieval_multicue_ppr_discriminative_v1 (arm-C = idf-weighted multi-cue PPR discriminative scorer) -- the diagnosis agent's recommended reuse target; ADAPT its discriminative re-rank, do not rebuild. NB it got RETRIEVAL_MIDDLE_BAND twice on ARC/WorldTree with shuffled-control not fully collapsing -> the scramble control here is the bar it must clear.
- Stage-2A retrieve-VALIDATE loop (hdlab, HARD_PASS) -- the owned context-validation organ; the convergence/validate step can reuse it.
- hub-penalty (validated 1-hop, +0.03-0.04) + community-routing store + the diagnosis cell's spreading-activation (experiments/exp_crutch_retrieval_coverage_diag_v1.py).
- Crutch data/cskg_foundation; benchmark data/corpora/social_iqa; the validated 9-arm harness experiments/exp_crutch_fade_social_iqa_v1.py (import read-only, do NOT edit its arms).

## Honest deflator
Discrimination on dense commonsense graphs is KNOWN-HARD (ARC-sibling MIDDLE_BAND, shuffled-control never fully collapsed). P moderate. A scramble-CLEAN win of any size is the meaningful result -- it would be the first discriminative, scramble-clean crutch->comprehension conversion of the program.

## Guardrails
Branch dataprep/mcguffey-graded-corpus (NOT main/origin). ONE variable (the discriminator). Real held-out dev. self-test PASS -> smoke -> FULL. Resumable per-unit. Targeted commits only (churner active, git SLOW). VET every arm on disk; scramble is the load-bearing control.
