# Pre-reg: Binder-grounded meaning MECHANISM test (Option A, brain-native fair test)

anchor: `native_meaning_encoder_binder_grounded_v1`
cell: experiments/exp_native_meaning_encoder_binder_grounded_v1.py
date: 2026-07-25
author: exp_dev
status: SELF-TEST PASS + LOCAL SMOKE COMPLETE (verdict NULL-grounded~=distributional); FULL pending Director/orch

## Question (the mechanism)
Can the substrate EARN a held-out concept's Binder-65 brain-grounded feature vector FROM ITS
RELATIONS + native-encoded CONTEXT (error-driven; native encoder input ONLY -- NOT GloVe/BERT/
Feature2Vec projection), and does that earned grounded meaning GENERALIZE to held-out concepts? KEY
DISCRIMINATOR: does RELATIONAL grounding beat pure DISTRIBUTIONAL context?

## Coverage finding (why this framing; reported not hidden)
Binder-2016 = 534 concrete/embodied common words x 65 human-rated brain-system features (Barsalou
grounding). WorldTree = science concepts + property VALUES; disjoint where the v2 task needs it (0 of
2264 v2 items fully grounded; ~6% of candidate values Binder-covered). So the mechanism is tested on
Binder's OWN clean brain gold (a fair test the data supports); the SCIENCE-reasoning application
(same earn-from-relations approach on WorldTree-PROP features for ARC) is the FOLLOW-UP, not this cell.
Test set = 141 Binder concepts with >=1 WT relation (50 with >=2); retrieval pool = all 534 true
Binder-65 vectors. NaN (verbs/adj miss Complexity/Practice/Caused) imputed with Binder-INTERNAL column
mean (178 cells, ~0.5%), logged -- NOT borrowed.

## Design (one variable = the input encoder to the SAME ridge->Binder-65 map)
- grounded_earned (PRIMARY): input = [native context vec + native RELATION-structure vec] (WT typed
  relations composed via native E over values + R over relation types + native SGNS context).
- distributional_earned (BASELINE): input = native SGNS context vec only.
- glove_earned (BASELINE, borrowed ref): frozen GloVe vec (SMOKE-local; CITED if gensim absent).
Ridge (error-driven least-squares) input->Binder-65, 5-fold CV over the 141 (no-leak: held concepts'
Binder vectors NEVER in map training). Native encoder = exp_native_meaning_encoder_scale_v1 (tied SGNS
over ARC context + WT relations; NO borrowed vectors).

## Metrics (held-out generalization; gold = Binder-65 cosine neighborhoods from the ratings)
- A2 (PRIMARY): retrieval precision@10 (+ Spearman) of predicted-vector neighborhood vs true gold
  neighborhood over the 533-concept pool.
- A1: 10-way discrimination -- predicted_c picks c's true profile among 9 hard (nearest-gold) distractors, gold randomized (chance 0.10).

## Controls (pre-registered)
chance (random predicted vectors); shuffle (permute concept->Binder target in map TRAIN -> held-out
MUST collapse to ~chance = no-leak/anti-memorization); untrained_input (map over untrained encoder
vectors); no-leak (5-fold CV, asserted).

## Bands (a priori)
- GROUNDED-EARNS-AND-GENERALIZES = grounded p@10 - distributional p@10 >= MARGIN (0.02) AND grounded
  generalizes (p@10 CI-lower > chance AND > untrained) AND shuffle collapses.
- NULL-grounded~=distributional (HONEST NULL, pre-registered) = grounded - distributional <= EPS
  (0.005): relational grounding adds nothing over distributional readout here.
- MIDDLE = grounded beats distributional by (EPS, MARGIN) and generalizes.
- INVALID = shuffle does not collapse (leak) OR n_test < 40 OR baselines out of band.

## SMOKE RESULT (MEASURED@data/exp_native_meaning_encoder_binder_grounded_v1_smoke/metrics.json; CPU, 70k ARC sentences, 1 seed)
- grounded_earned p@10 = 0.2043 (Wilson CI 0.184-0.226), disc = 0.1064
- distributional_earned p@10 = 0.2426, disc = 0.1135
- untrained_input p@10 = 0.0333 ; shuffle p@10 = 0.0362 ; chance p@10 = 0.0262
- grounded - distributional = -0.0383 (grounded LOSES) -> VERDICT = NULL-grounded~=distributional
- generalizes = True (both >> chance/untrained) ; shuffle_collapsed = True ; arms_differ = True ; n_test = 141
- glove = CITED-only (gensim absent locally; portable FULL is gensim-free)
INTERPRETATION (VET-PENDING): the native DISTRIBUTIONAL context encoder ALREADY earns generalizing
brain-grounded (Binder-65) neighborhood structure well above chance; adding WT relational structure
does NOT help (slightly hurts). The hard 10-way discrimination is near chance for both (nearest-
neighbor confusability), while coarse neighborhood retrieval (p@10) is strong.

## FULL / scale note (Director discretion)
The ONLY GPU-worthy part is training the native SGNS encoder over ARC at scale (millions of sentences
-> better absolute grounding quality + fairer distributional baseline). CAVEAT (honest scale read):
the WT relation structure is FIXED (141 concepts, ~2 rels each) and ARC-INDEPENDENT, so more ARC data
improves the distributional arm but NOT the grounded arm's relational component -> the
grounded-vs-distributional NULL is likely SCALE-ROBUST (may even widen for distributional). FULL's
value = the at-scale ABSOLUTE grounding numbers (does native distributional earn strong Binder
grounding at scale?), not a likely flip of the mechanism verdict.

## Contract
prereg + self-test + smoke committed by explicit path; FULL to overnight_queue (GPU) via queue_add on
Director/orch go; no atom banking (skunkworks owns VET); no borrowed vectors in the native encoder;
ASCII-only; VET-PENDING.
