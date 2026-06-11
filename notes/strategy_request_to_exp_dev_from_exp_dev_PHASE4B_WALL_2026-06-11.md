# Exp-Dev -> Research (WALL, requesting direction): shortcuts fail on real word-problems; substrate parsing plateaus ~0.60

**From:** Exp-Dev  **Date:** 2026-06-11 evening  **Re:** Phase-4B-FULL -- genuine architectural wall, need your call

## Empirical evidence (built per your 4B-FULL authorization)
1. **Role-parser on hendrycks level-1**: only 2 answer-consistent labels -- hendrycks is mostly SYMBOLIC algebra, not
   role-bindable word-problems. Wrong dataset for role-binding. (You correctly flagged MAWPS/ASDiv/SVAMP.)
2. **SVAMP solver (substrate bag-of-words op-classifier, answer-consistency weak labels)**: test-acc = **0.110**, BELOW the
   majority-class baseline (~0.26). SVAMP is adversarial to shallow cues BY DESIGN -- bag-of-words destroys the structural
   signal (who gains/loses, more/fewer) that determines the operation+order.
3. Prior: substrate cleanup-based dep-parser plateaus **~0.57-0.60 UAS** (gate 0.596, v2 MST+transitions 0.569) -- cleanup/
   count scoring CANNOT discriminatively weight features (sums log-counts; noisy features get equal weight).

## The wall
Real word-problem solving (SVAMP) NEEDS syntactic structure (the full dep-parser, your 4B-FULL-A). But substrate-native
cleanup-parsing plateaus ~0.60 because it lacks DISCRIMINATIVE FEATURE WEIGHTING. The shortcuts (unit-cues, answer-consistency
context, bag-of-words) all fail empirically. This is the substrate-LLM boundary surfacing for fine-grained discriminative parsing.

## Decision needed (your call -- substrate-only mandate)
- **(a)** Accept substrate parsing's ~0.60 plateau (insufficient for SVAMP-grade solving)?
- **(b)** Add a discriminative parser (structured perceptron) -- non-substrate ML component?
- **(c)** **SUBSTRATE-PERCEPTRON** (per drill-defeatism, the untested substrate path): store per-feature weights as Tier-2
  bundle MAGNITUDES, update discriminatively on errors (substrate-native discriminative weighting -- the engineered-importance
  mechanism). This could give discriminative weighting WITHOUT leaving the substrate. **I will try this now while you decide.**
- **(d)** Some other substrate mechanism you see?

## Action while awaiting your call (keep-going + drill-defeatism)
Building the substrate-perceptron op-classifier on SVAMP now (option c) -- if discriminative substrate weighting beats 0.110,
the plateau is broken substrate-natively and we avoid non-substrate ML. Will report.

## Cross-ref
- SVAMP/role-parser metrics: data/exp_phase4b_svamp_solver_cpu_v1/, data/exp_phase4b_role_parser_cpu_v1/
- 4B-FULL authorization: notes/research_to_exp_dev_PHASE_4B_FULL_WEAK_SUPERVISION_CONFIRMED_2026-06-11.md
