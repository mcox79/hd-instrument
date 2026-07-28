# Parser lift: LEARNED verb-valency/subcategorization features -- the real lever the HARD_FAIL pointed to (2026-07-23)

## WHY (the negative + brain-drill converge)
Global-beam training HARD_FAILED (earned bound, clean metrics): global_beam 0.8090 ~= local_greedy 0.8109 (2SE margin -0.006), beam-hurts control reproduced (+0.072). Global training REMOVED the beam-hurts pathology but could NOT exceed greedy -> the ~0.81 ceiling is a FEATURE/REPRESENTATION limit, NOT a search/training-regime limit.

BRAIN-DRILL (how the brain parses robustly where we saturate):
- Verb SUBCATEGORIZATION/VALENCY has IMMEDIATE effects on human parsing (MacDonald/Pearlmutter/Seidenberg 1994; Trueswell; constraint-based lexicalist). A verb KNOWS its expected arguments; lexical/valency biases are the MOST RELIABLE cues and are used first. Plausibility + argument-structure guide attachment.
- Proven in NLP: subcategorization frames are LEARNABLE from dependency corpora (UDLex; Lippincott graphical models); "a SMART LEXICALIZATION driven by subcategorization leads to FAR BETTER results in dependency parsing" (Zeman COLING 2002). Argument-vs-adjunct discrimination is the mechanism.
- Our substrate: the transition parser (29451) uses POS + stack-config features (generic). It LACKS the verb's learned argument-frame expectations. The LCCP argstruct cell already HARD_PASSED (valency reduces misattachment + generalizes) -> the lever is real; integrate it INTO the UAS parser.

## WHAT to build
Add LEARNED verb-valency/subcategorization features to the arc-eager transition parser (reuse 29451 transition system + averaged perceptron):
- LEARN from the training treebank, per head lemma (esp. verbs): a frame signature = the distribution over expected dependent relations (nsubj, obj, iobj, ccomp, xcomp, obl, ...) and their typical count/order (argument vs adjunct). Back off to POS/verb-class for unseen lemmas (open-class generalization).
- At each attachment decision, add features: (a) does the proposed dependent's relation/position MATCH the head's learned frame? (b) is the head's expected-argument slot still UNFILLED (valency saturation)? (c) argument-vs-adjunct likelihood. "Smart lexicalization" = head-lemma x expected-frame features.
- Glass-box: inspectable frame tables + linear weights, no autograd.

## ARMS (one variable = valency features)
- ARM_BASE (= 29451): POS + config features only. Expect ~0.81.
- ARM_VALENCY: + learned verb-valency/subcat features. HYPOTHESIS: breaks the feature ceiling -> UAS toward 0.84-0.88 (approaching classical), esp. on verb-argument attachments.

## DISCRIMINATOR (can-fail; the negative said features are the lever, this tests THAT lever)
- HARD_PASS: ARM_VALENCY beats ARM_BASE by >= +0.03 UAS (2SE-clean), approaching classical 0.86-0.89; the gain concentrates on VERB-ARGUMENT attachments (arg-vs-adjunct accuracy up); LEARNING CURVE rises (the frame tables improve with exposure = flexible/improving); back-off generalizes to held-out verb lemmas (heldout >= majority-attach).
- HARD_FAIL (must be possible): valency features do NOT lift >= +0.03 -> the ceiling is deeper than lexicalization too (a real representational bound; then the lever is a different representation, e.g. contextual/semantic). This must be a live outcome.
- FAIR: identical parser/training/eval split; ONE variable = valency features; NO gold-frame leakage at test (frames learned from TRAIN only; test verbs scored via learned/backed-off frames); report all + nopunct + verb-arg breakdown; real UD-EWT. LEARNING CURVE measured (USER-mandated flexible/improving property).
- ANTI-CHEAT: shuffle the frame table (random frames) -> lift collapses (proves the LEARNED frames carry the signal, not just extra parameters).

## POINTERS (read; dedup yourself)
- experiments/exp_depparse_transition_arceager_cpu_v1.py (29451) -- parser to extend; transition system + perceptron + eval harness.
- experiments/exp_depparse_global_beam_earlyupdate_cpu_v1.py -- the HARD_FAIL (search-not-features) that motivates this; ARM_BASE baseline.
- experiments/exp_learned_argstruct_parser_lccp_independent_gold_v1.py -- the valency/argstruct HARD_PASS (reduces misattach, generalizes); reuse its frame-learning approach; DEDUP against it (that was a separate argstruct parser; this integrates valency into the UAS transition parser).
- experiments/exp_parser_uas_feateng_struct_v1.py -- the +0.04 structural features (already in base; valency is ORTHOGONAL lexical-semantic signal).

## AUTONOMY
exp_dev designs ALL params + final dedup: frame-signature representation, back-off scheme, feature specifics, seeds, band VALUES, queue/inline, anchor, ETA. If dedup finds valency already integrated into the UAS transition parser + banked, REPORT + do not re-run.
