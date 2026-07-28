# Clean-CG shot: McCoy ambiguous-training paradigm -- does the substrate SELECT hierarchical over linear structure? (2026-07-23)

## WHY (brain-check that resolved the A/B fork on evidence)
29455 (learned depth accumulator generalizes productively to unseen depth) was honestly tiered MM because "the recursion is ARCHITECTURAL, only content is learned." Brain-check (live web):
- **McCoy, Frank & Linzen 2020 "Does syntax need to grow on trees?" (arXiv:2001.03632):** the ONLY factor that reliably yields a HIERARCHICAL inductive bias is ARCHITECTURAL structure (tree/stack); structure-free sequence models generalize LINEARLY. => the architectural scaffold is the NECESSARY condition, NOT a cheat. This is exactly why TEM (29448, structure-free gradient) failed and 29455 (pre-given accumulator) worked.
- **Perfors, Tenenbaum & Regier 2011 "Learnability of abstract syntactic principles":** an ideal learner infers hierarchy from child-directed speech via Bayesian MODEL SELECTION over a hypothesis space that INCLUDES hierarchical grammars. The brain SELECTS hierarchy over linear; it doesn't induce structure from nothing.
CONCLUSION: the genuine gap between 29455 (MM) and clean-CG is NOT "learn the scaffold from nothing" (impossible per McCoy; = the TEM wall). It is the PERFORS piece: does the substrate, given its architectural structural capacity, SELECT the hierarchical rule over the linear shortcut FROM DATA? That is the clean-CG question and it is brain-faithful + tractable.

## THE TEST (canonical McCoy ambiguous-training paradigm, applied to our substrate)
- TRAIN ONLY on cases where the HIERARCHICAL rule (depth-0 noun nearest verb) and the LINEAR rule (nearest noun / first noun) AGREE on the subject -- i.e. subject-first / non-buried items. Training is AMBIGUOUS: consistent with BOTH a hierarchical and a linear generalization.
- TEST on BURIED cases where the two rules DIVERGE (the hierarchical answer = subject; the linear answer = the attractor).
- MEASURE: does the substrate generalize the HIERARCHICAL way (buried acc ~0.75, tracks depth rule) or the LINEAR way (buried acc ~0.30, tracks nearest-noun)?
- LEARNING CURVE (flexible/improving property, USER directive): track the hierarchical-vs-linear generalization as training proceeds -- does the structural preference emerge/strengthen?

## ARMS (one variable = presence of architectural structure)
- ARM_ACCUM (the substrate): the incremental depth ACCUMULATOR architecture (VSA/register stack; the structural scaffold), content learnable. HYPOTHESIS: generalizes HIERARCHICALLY from ambiguous training = it HAS/SELECTS the hierarchical bias.
- ARM_FLAT (must-fail control): structure-free bag/linear readout over the SAME token features, no accumulator. HYPOTHESIS: generalizes LINEARLY (reproduces McCoy's sequential-model result) = FAILS the buried test.
- Optionally ARM_MIX: an explicit learned SELECTION/gate over {hierarchical, linear, first} structural hypotheses -- does the gate weight shift to hierarchical from ambiguous training (Perfors model-selection made literal)?

## DISCRIMINATOR (can-fail, symmetric)
- CLEAN-CG PASS: ARM_ACCUM generalizes HIERARCHICALLY from ambiguous training (buried >> majority/nearest, tracks depth rule ~0.75) WHILE ARM_FLAT generalizes LINEARLY (buried ~= nearest ~0.30). The architectural structure PROVABLY confers the hierarchical bias the flat model lacks; the substrate SELECTED hierarchy without buried supervision.
- HARD_FAIL (real, must be possible): ARM_ACCUM ALSO generalizes LINEARLY (buried ~= nearest) -> the accumulator architecture does NOT confer a hierarchical bias under ambiguous training; the earlier wins needed buried supervision -> an earned bound (and a Perfors-relevant negative: agreement signal on agree-cases doesn't drive hierarchical selection).
- ANTI-CHEAT: depth-scramble collapses ARM_ACCUM; number read AFTER selection (number_flip=0); NO buried items or their structural signature leak into training (airtight agree/diverge split); fair bit-exact baselines (majority, nearest, first, deterministic-depth) on the SAME buried test set. ONE variable = architecture (accum vs flat).
- COMPOSE 29455: if ARM_ACCUM passes, also confirm the hierarchical generalization holds to UNSEEN DEPTH (productivity, per 29455) -- selection + productivity together.

## INTERPRETATION
- PASS = the substrate's architecture SELECTS hierarchical structure over the linear shortcut from ambiguous real-text data = brain-faithful (McCoy architecture + Perfors selection) LEARNED compositional structure = the clean-CG landmark, and a direct answer to McCoy's question for a VSA/accumulator architecture. Composes 29455/29453/29450.
- FAIL = the accumulator confers productivity (29455) but NOT hierarchical SELECTION under ambiguity -> earned bound; the selection needs an explicit model-selection gate (ARM_MIX) or stronger prior -> next build.

## HONESTY GUARD (avoid goalpost-moving)
This is the FOURTH framing of the CG bar this arc (FW-holdout -> depth-productivity -> now selection-under-ambiguity). It is defensible ONLY because it is the CANONICAL published paradigm (McCoy) and brain-grounded (Perfors), not a bespoke bar. Pre-commit BOTH bands. If ARM_ACCUM fails, BANK THE NEGATIVE honestly and STOP re-defining -- do not invent a fifth bar without USER steer.

## POINTERS (read; do not re-summarize)
- experiments/exp_agreement_depth_productivity_generalization_v1.py -- 29455, the accumulator + depth machinery to reuse for ARM_ACCUM + the productivity compose.
- experiments/exp_agreement_learned_depth_accumulator_v1.py -- 29453, learned-delta accumulator.
- experiments/exp_agreement_glassbox_depth_rule_confirm_v1.py -- 29450 deterministic depth rule (hierarchical reference) + scramble harness.
- The agree/diverge split: for each buried-capable item, compute whether depth-rule and nearest-rule AGREE (train pool) or DIVERGE (test pool) on the gold subject; NEVER use the gold label at inference.

## AUTONOMY
exp_dev designs ALL params: the agree/diverge split thresholds, ARM_MIX inclusion, seeds, N/M/K, HARD-PASS/HARD-FAIL band VALUES, queue/inline, anchor name, ETA. Do NOT pre-bake them.
