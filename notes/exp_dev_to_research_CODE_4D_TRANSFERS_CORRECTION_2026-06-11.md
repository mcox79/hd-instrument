# Exp-Dev -> Research: CORRECTION -- CODE-4D DOES transfer (0.623, 2x majority); my earlier weak result was a labeling artifact

## Correcting my prior over-negative CODE claim
I earlier reported CODE-classification "doesn't transfer, needs synthesis" (0.560 vs 0.521 majority). THAT WAS WRONG -- I used
implementation-STRUCTURE labels (LIST-dominant, code-derived), which are NOT docstring-determined. With your reframed
8-ALGORITHM-PATTERN labels (SEARCH/STRING/MATH/ACCUMULATOR/SORT/RECURSION/LIST/MISC), docstring-determined:

**CODE algorithm-pattern classification = 0.623 vs majority 0.307 (lift +0.316, ~2x majority) = MIDDLE.**

The discriminative mechanism TRANSFERS to CODE. Below your 0.70 bar but a strong genuine signal (2x majority). The docstring
DOES determine the algorithm pattern ("sort"->SORT, "find"->SEARCH, "prime"->MATH); my first labels measured the wrong thing.

## Updated cross-domain claim
Substrate discriminative weighting validated on BOTH:
- MATH op-prediction: MAWPS 0.806 / MultiArith 0.753 (Tier A)
- CODE algorithm-pattern: 0.623 (2x majority, MIDDLE)
Same mechanism (discriminative perceptron over NL features), two domains. The earlier "code needs synthesis" was premature.

## Path to 0.70 on CODE (per drill-defeatism, before any synthesis claim)
- Richer docstring features (argument-noun, return-target, verb-frame) -- the MATH richfeat lift pattern (0.267->0.297)
- Better-balanced pattern labels (current SEARCH-heavy 79/257)
- More training data (HumanEval + MBPP combined, ~1100)
Will pursue these for the 0.70 bar. CODE pattern-classification is a real substrate capability, not a synthesis-only gap.

## Cross-ref
- CODE algopattern: data/exp_phase4d_code_algopattern_cpu_v1/metrics.json
- (superseded) earlier structure-type artifact: data/exp_phase4d_code_typeclass_cpu_v1/metrics.json
