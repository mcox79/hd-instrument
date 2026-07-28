# Chain-grade shot: LEARNED incremental function-word DEPTH accumulator (2026-07-22)

## WHY (the diagnosis this fixes)
Every induction attempt on buried subjects collapsed to majority (~0.63) for ONE reason, now confirmed from the cell code: the inducers were given `N_STRUCT=10` **LOCAL** features (position-from-start/end, a 1-step `prev in PREPS` boolean) and a **linear/tanh readout**. The feature that actually separates a buried subject from an attractor is **cumulative embedding DEPTH** -- a *running* count that opens on each preposition/relativizer across the whole prefix (e.g. "the keys TO the cabinet IN the corner ARE"). A local prev-prep flag cannot see it, and a linear readout over a bag of local features **structurally cannot compute a running accumulation** (needs sequential state). The deterministic depth rule (atom 29450) wins at 0.759 BECAUSE it does this incremental accumulation by hand.

Proof it is a WIRING flaw, not a bound: oracle-select+morph = 0.9925 (representation is fine); subject-first ~0.75 everywhere (works when position suffices); "learner GIVEN the depth feature improves +0.083" (wiring in the feature helps). The "5 unanimous failures" = ONE flaw replicated 5x.

BRAIN-FAITHFUL basis: infants bootstrap phrase structure from FUNCTION WORDS incrementally (prosodic bootstrapping; Christophe/Shi/Gervain); agreement is resolved by INCREMENTAL cue-based retrieval at the verb (Lewis-Vasishth 2005; agreement attraction = Wagers/Phillips/Lau). The brain wins on buried subjects via a STRUCTURAL depth cue built left-to-right, not via nearness. Our failed method (post-hoc bag + linear) was NOT the brain's method.

## WHAT to build
A **glass-box, sequential, LEFT-TO-RIGHT** subject-selector on the existing real-Linzen buried-subject testbed (`agreement_word_cache_v1`, buried/SNF subset, same SNF definition as 29443/29448/29449/29450):
- Maintain a scalar (or low-dim) **DEPTH REGISTER** updated token-by-token.
- The function-word -> depth UPDATE is **LEARNED** (which closed-class items increment/decrement depth, and the update dynamics) -- NOT hand-coded. This is the induction: it must DISCOVER the depth-opening role of function words from data.
- At the verb, **retrieve the depth-0 noun nearest the verb** (cue-based retrieval), read its number AFTER selection (no number leak into selection).
- Generalization test: **held-out lexeme pools disjoint** (train/test), so any win is learned generalization, not memorization.
- Glass-box: the register + the learned function-word weights are fully inspectable; NO opaque operator at runtime. Gradient (if used to learn the update weights) is BUILD-time only (pivot-authorized).

## The discriminator (must be able to fail)
- KEY: does the LEARNED accumulator **beat the positional shortcut baseline** (nearest-noun / first-noun / local-prev-prep bag ~0.55-0.63) on held-out-lexeme BURIED subjects, and **approach the deterministic ceiling 0.759**?
- MUST-FAIL control: **fixed-RANDOM** function-word->depth weights (no learning) should NOT beat the shortcut -> proves the LEARNING did the work.
- ANTI-CHEAT: depth-scramble (permute the depth multiset over positions) must COLLAPSE the accumulator below nearest-noun (as it did for 29450: 0.759->0.53) -> proves the lift is DEPTH not verb-adjacency.
- FAIRNESS: bit-exact baselines; ONE variable (learned-sequential-cumulative-depth vs local-bag); real text; number read after selection; verify zero selections change on target-number flip.

## Interpretation
- HARD_PASS (learned accumulator beats shortcut + approaches 0.759 + must-fail control fires + scramble collapses on held-out lexemes) = the FIRST LEARNED structural-generalization result on real text -> hardest VET, landmark.
- HARD_FAIL (even the sequential learned architecture cannot beat the shortcut) = THEN and only then is it a real bound, and we will know it is the LEARNING of depth (not the representation, not the readout) that is the wall -- a precise, earned negative.

## Pointers (read these; do NOT re-summarize)
- `experiments/exp_agreement_glassbox_depth_rule_confirm_v1.py` -- the deterministic 0.759 ceiling + the testbed + the SNF/buried definition + the depth-scramble anti-cheat harness to reuse.
- `experiments/exp_agreement_tem_on_vsa_trained_codes_v1.py` and `experiments/exp_agreement_attractor_select_vsa_v1.py` -- the FAILED inducers; see `N_STRUCT=10` local features (~line 170-202) + linear/tanh readout = the flaw this fixes. Reuse their held-out-lexeme split + majority_ref harness for a like-for-like baseline.
- `notes/director_POST_COMPACTION_BACKUP_FULL_STATE_2026-07-17.md` -- CURRENT STATE + NEXT STEPS block.
- `notes/research_incremental_stack_parsing_paradigm_2026-07-22.md` -- the incremental stack = depth register connection (this build's stack IS the parser's stack).

## Autonomy
exp_dev designs ALL parameters: register dim, learned-update parametrization (e.g. per-function-word learned increment + gate), seeds, N/M/K, HARD-PASS/HARD-FAIL band values, queue, anchor name, ETA, smoke + FULL profile. Do NOT let me pre-bake them.
