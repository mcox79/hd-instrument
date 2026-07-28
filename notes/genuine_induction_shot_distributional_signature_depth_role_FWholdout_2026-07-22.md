# Genuine chain-grade shot: distributional-signature depth-role, FW-HOLDOUT pass criterion (2026-07-22)

## WHY (the VET that defined this)
The learned per-function-word depth accumulator (atom 29453) is REAL and survives every fairness probe, but was HONESTLY DOWN-RATED to MM (not chain-grade). The decisive diagnostic: **FW-HOLDOUT** -- freeze the ~14 high-frequency depth-opener function words and retrain -> accuracy collapses to 0.6425 ~= majority 0.6279. So it learned a per-function-word SCALAR LOOKUP, not a generative rule. Its "held-out-lexeme generalization" is trivially true by construction (content-agnostic: delta=0 on all nouns), so the content split is NOT a demanding OOD test. Genuine structural induction must EXTRAPOLATE to function words it has never seen.

BRAIN-FAITHFUL basis: a child infers a NOVEL closed-class word's structural role from its DISTRIBUTIONAL SIGNATURE (high frequency, phrase-edge position, precedes content words, phonological reduction) -- not from a memorized per-token scalar. Distributional/prosodic bootstrapping = the generative mechanism.

## THE BAR (what "passes" now means)
A LEARNED rule that predicts a token's depth-DELTA from its DISTRIBUTIONAL/POSITIONAL SIGNATURE, and EXTRAPOLATES to HELD-OUT function words. PASS = FW-holdout accuracy HOLDS (does NOT collapse to majority ~0.64) on buried subjects, i.e. depth-role is inferred for unseen function words from their signature.

## WHAT to build
On the same real-Linzen buried-subject testbed (agreement_word_cache_v1, SNF subset, same definition as 29450/29453):
- For each token compute an UNSUPERVISED distributional/positional SIGNATURE (NO per-lexeme function-word identity): e.g. corpus log-frequency bucket, P(precedes a content word), P(at phrase/clause edge), left/right coarse-POS context distribution, closed-class-ness proxy, relative position. Compute these from corpus statistics so a HELD-OUT function word gets a signature the same way.
- Learn depth-DELTA = f(signature) (small glass-box map: linear or low-order, inspectable coefficients over the signature features; gradient at BUILD-time only, hard argmin at runtime -- same invariant as 29453).
- Accumulate depth incrementally left-to-right, select depth-0 noun nearest verb, read number AFTER selection.

## DISCRIMINATOR (must be able to fail; FW-holdout is the core)
- CORE PASS: FW-HOLDOUT -- split function words into train/test folds; train f(signature) on train-fold FWs ONLY; at test the held-out FWs are seen ONLY through their signature. Accuracy on buried subjects must HOLD (target: clearly above majority 0.6279, approaching the 0.75 capability), NOT collapse to ~0.64.
- MUST-FAIL control (reproduces 29453): a per-FW-scalar-lookup arm MUST collapse on FW-holdout to ~majority -> proves the signature-map is doing generative work the lookup cannot.
- ANTI-CHEAT: depth-scramble must collapse below nearest-noun (as 29450/29453).
- NO LEAK: number read after selection (number-flip=0); signature computed WITHOUT the agreement label; the signature must NOT encode subjecthood/number directly (audit the feature list).
- FAIRNESS: bit-exact baselines (majority, nearest-noun, first-noun); ONE variable (signature-map vs per-FW-scalar); real text.

## INTERPRETATION
- HARD_PASS (signature-map HOLDS on FW-holdout while the scalar-lookup control collapses) = GENUINE generative structural induction on real text -- the first that extrapolates to unseen structural markers -> this is the chain-grade landmark -> hardest VET. Composes 29453/29450.
- HARD_FAIL (signature-map ALSO collapses on FW-holdout) = the depth-opening role is NOT predictable from distributional signature at this scale -> an EARNED, precise bound (the induction needs richer input than surface distribution), and we will know exactly that.

## POINTERS (read; do not re-summarize)
- experiments/exp_agreement_learned_depth_accumulator_v1.py -- 29453, the per-FW-scalar version = the MUST-FAIL control + the testbed/accumulator harness to reuse.
- experiments/exp_agreement_glassbox_depth_rule_confirm_v1.py -- 29450 deterministic ceiling + scramble anti-cheat.
- The skunkworks VET of 29453 (this session) established the FW-holdout collapse to 0.6425 -- reproduce that as the control's expected behavior.
- notes/chain_grade_shot_learned_incremental_functionword_depth_accumulator_2026-07-22.md -- the prior design + diagnosis.

## AUTONOMY
exp_dev designs ALL params: signature feature set + how computed, map form/dim, FW-fold count + split, seeds, N/M/K, HARD-PASS/HARD-FAIL band VALUES, queue, anchor name, ETA, smoke/FULL profile. Do NOT pre-bake them.
