# Chain-grade shot (correctly-specified axis): DEPTH-PRODUCTIVITY generalization -- train shallow, test deep (2026-07-22)

## WHY (the reframe)
Two axes were conflated. The learned depth accumulator (atom 29453) was down-rated because it collapses on FW-HOLDOUT (extrapolate to unseen function words). But BRAIN-CHECK on that test: function words are a CLOSED CLASS; humans learn them AS ITEMS over years and do NOT extrapolate depth-role to novel function words (there essentially are none). So FW-holdout is likely the WRONG generalization axis -- a bar the brain doesn't clear either. The sigmap experiment (exp_agreement_sigmap_depth_induction_v1, HARD_FAIL) confirmed surface distribution can't do FW-holdout, but that axis may not be what "chain-grade" should mean here.

The RIGHT compositional-generalization axis = PRODUCTIVITY over STRUCTURE (Fodor-Pylyshyn systematicity/productivity; Lake-Baroni SCAN length generalization; COGS depth generalization): generalize to structures DEEPER/more-nested than seen in training. An incremental per-FW-scalar depth accumulator SHOULD generalize to arbitrary nesting depth BY CONSTRUCTION -- IF its selection is genuinely the recursive "depth-0 noun nearest verb." This directly tests whether 29453 is genuinely recursive/productive or a shallow pattern.

## THE BAR (what "chain-grade" means on the right axis)
Train the learned accumulator ONLY on SHALLOW buried subjects (<= K intervening embeddings / attractor-openers between subject and verb). Test on DEEPER held-out buried subjects (> K). PASS = accuracy HOLDS on the deep held-out set (tracks the deterministic recursive rule, stays well above nearest-noun which degrades as attractors stack). This is productive systematic generalization to unseen structural complexity on real text.

## WHAT to build
On the real-Linzen buried-subject testbed (agreement_word_cache_v1, SNF subset; reuse 29453/29450 harness):
- Define per-item EMBEDDING DEPTH of the subject->verb span (e.g. count of function-word-opened embeddings / intervening attractor nouns at depth>0 between subject and verb). Bin items by this depth.
- TRAIN the 29453-style learned accumulator (per-FW-scalar deltas, incremental accumulation, hard-argmin runtime, number read after selection) on SHALLOW bin only (<= K).
- TEST on the DEEP held-out bin (> K). Report accuracy vs the reference set.
- REFERENCE CEILING = deterministic rule 29450 (nearest depth-0 noun) -- recursive by construction, so it should HOLD at all depths = the shape of full productivity.
- Also report the learned accumulator's own depth curve (accuracy vs depth) to see where/if it degrades.

## DISCRIMINATOR (can-fail; not a rescue)
- PASS: learned accumulator HOLDS on deep held-out (within ~noise of its shallow accuracy AND clearly above nearest-noun on the same deep items; tracks the deterministic rule's depth curve).
- HARD_FAIL: learned accumulator DEGRADES with depth toward nearest-noun/majority on the deep held-out -> confirmed SHALLOW, NOT productive -> the 29453 negative gets STRONGER (it's a depth-bounded lookup, no recursion). This MUST be a real possible outcome.
- FAIR BASELINES (bit-exact) computed on the SAME deep held-out items: majority, nearest-noun, first-noun, deterministic-29450.
- ANTI-CHEAT: depth-scramble still collapses; number-flip=0; number read after selection.
- ONE variable: train-shallow/test-deep generalization (the depth split), everything else = 29453.
- HONESTY GUARD (avoid motivated rescue): deep buried subjects are RARE in real text -> if the deep held-out N is small, REPORT it and widen CIs; do NOT synthesize deep templates that would make the outcome construction-determined. If real-text deep-N is too small for a verdict, say so and propose the minimal honest augmentation separately.

## INTERPRETATION
- PASS = the learned accumulator is genuinely RECURSIVE/PRODUCTIVE = productive systematic generalization on real text = the correctly-specified chain-grade landmark (composes 29453/29450) -> hardest VET, and re-frame 29453 as chain-grade-on-the-productivity-axis (FW-holdout was the wrong bar).
- FAIL = 29453 is a depth-bounded shallow lookup with no productivity -> earned bound; the recursion must come from a richer structural representation (multi-level STACK, roadmap #1 parser-stack feature) -> that becomes the next build.

## POINTERS (read; do not re-summarize)
- experiments/exp_agreement_learned_depth_accumulator_v1.py -- atom 29453, the accumulator to train/test on the depth split.
- experiments/exp_agreement_glassbox_depth_rule_confirm_v1.py -- 29450 deterministic recursive rule = the reference ceiling + scramble harness.
- experiments/exp_agreement_sigmap_depth_induction_v1.py -- the sigmap HARD_FAIL (FW-holdout axis) that motivated the reframe.
- notes/genuine_induction_shot_distributional_signature_depth_role_FWholdout_2026-07-22.md -- the FW-holdout attempt + its collapse.

## AUTONOMY
exp_dev designs ALL params: the depth metric + bin threshold K, train/test split, seeds, N/M/K, HARD-PASS/HARD-FAIL band VALUES, deep-N adequacy call, queue/inline, anchor name, ETA. Do NOT pre-bake them.
