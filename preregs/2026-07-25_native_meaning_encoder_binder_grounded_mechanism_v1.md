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

## Design (one variable = the input SOURCE to the SAME ridge->Binder-65 map; SOURCES ISOLATED)
Director refinement: relations are SPARSE (141/534 Binder concepts have WT relations), so ISOLATE and
report the input source separately -- do NOT conflate.
- relations_only_earned (PRIMARY, the brain-consistent test): input = native RELATION-structure vec
  ONLY (WT typed relations composed via native E over values + R over relation types). Earning grounded
  meaning FROM RELATIONAL STRUCTURE = the claim we care about.
- context_only_earned (the distributional lever): input = native SGNS ARC-context vec ONLY. If THIS
  carries the win, the cell is a native Feature2Vec (context->grounded-features) = weaker/less-brain-
  consistent, and must be LABELED so, NOT sold as "grounding works."
- both_earned: input = [context + relations].
- glove_earned (borrowed ref): frozen GloVe vec (SMOKE-local; CITED if gensim absent).
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

## Bands (a priori; verdict states WHICH source carries any generalization signal)
- GROUNDED-FROM-RELATIONS-CARRIES = relations_only generalizes (p@10 CI-lower > chance AND >
  untrained) AND relations_only - context_only >= MARGIN (0.02) AND shuffle collapses. The
  brain-consistent win.
- BOTH-SOURCES-EARN-relations-genuine = relations_only generalizes AND |relations_only -
  context_only| < MARGIN: relations carry a genuine brain-grounded signal comparable to context.
- CONTEXT-CARRIES-distributional-to-grounded = context_only carries it (context_only > relations_only,
  relations underperforms): distributional->grounded projection (native Feature2Vec), the weaker/less-
  brain-consistent lever; NOT "grounding-from-relations works."
- NULL-neither-source-generalizes = neither source beats the floor.
- INVALID = shuffle does not collapse (leak) OR n_test < 40.

## SMOKE RESULT (MEASURED@data/exp_native_meaning_encoder_binder_grounded_v1_smoke/metrics.json; CPU, 70k ARC sentences, 1 seed) -- SOURCES ISOLATED
- relations_only_earned p@10 = 0.139 (Wilson CI 0.122-0.158), disc = 0.121
- context_only_earned  p@10 = 0.2426 (Wilson CI 0.221-0.266), disc = 0.114
- both_earned p@10 = 0.2043 (relations DILUTE context)
- untrained_input p@10 = 0.0333 ; shuffle p@10 = 0.0418 ; chance p@10 = 0.0262
- relations_only - context_only = -0.104 -> VERDICT = CONTEXT-CARRIES-distributional-to-grounded
- rel_generalizes = True (0.139 >> chance 0.026, shuffle-collapses = GENUINE weak signal, not memorized)
- ctx_generalizes = True ; shuffle_collapsed = True ; arms_differ = True ; n_test = 141
- glove = CITED-only (gensim absent locally)
INTERPRETATION (VET-PENDING): the generalization is carried by CONTEXT (distributional -> grounded =
native Feature2Vec), NOT by relations. Relations-only DOES earn a real-but-weak brain-grounded signal
(p@10 0.139 >> chance, shuffle-collapses -> genuine relational structure, not memorization), but it is
much weaker than distributional context (0.243) and adding relations to context HURTS (both 0.204 <
context 0.243). HONEST: this is NOT "grounding-from-relations works"; it is distributional-to-grounded
projection, the weaker/less-brain-consistent lever.

## SCALE / GPU decision: CPU-ONLY, NO GPU (Director + analysis)
No GPU dispatch. The WT relation structure is FIXED and ARC-independent (141 concepts, ~2 rels each);
more ARC improves only the distributional arm, so a GPU scale run cannot rescue the relations-only
signal and would only widen the context lead -- the source-attribution verdict is scale-robust. Data
too thin for a GPU-scale science follow-up. This CPU smoke is the deliverable.

## Contract
prereg + self-test + smoke committed by explicit path; FULL to overnight_queue (GPU) via queue_add on
Director/orch go; no atom banking (skunkworks owns VET); no borrowed vectors in the native encoder;
ASCII-only; VET-PENDING.
