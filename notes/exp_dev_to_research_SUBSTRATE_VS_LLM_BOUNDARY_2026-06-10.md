# Exp-Dev -> Research: the PRECISE substrate-vs-LLM boundary (Sprint-1+2 autonomous-output consolidated)

**From:** Exp-Dev  **Date:** 2026-06-10 late evening  **Re:** AGGRESSIVE_OVERNIGHT 3-thrusts + Sprint-2 both-paths -- consolidated finding

## The finding (clean, precise, ~18 anchors)
**Substrate is a SYMBOLIC / STRUCTURAL / SYSTEMATIC cognition engine. The LLM boundary is STATISTICAL NATURAL LANGUAGE.**

### Substrate-native (strong, substrate-only):
| capability | anchors | result |
|---|---|---|
| symbolic math | MATH-1 algebra, MATH-2 equations, MATH-3 calculus, MATH-4 proofs | all 1.0 |
| code | CODE-1 compose+exec, CODE-6 pipelines, HUMANEVAL-STRUCT synth-from-spec | 1.0 / 1.0 / 0.75 |
| communicate STRUCTURE | COMM-1 paragraph, COMM-6 intent-decode, COMM-LEX emit-from-lexicon | all 1.0 |
| SYSTEMATIC generation | LEX-WUG (morphological rule -> novel stems, 1-shot) | 1.0 |
| judgment/detection | CODE-2 bug-detection | 0.57 MIDDLE (weak) |

### LLM-only boundary (precisely two things):
1. **Parsing arbitrary English** -> unambiguous structure. (HumanEval-structural ISOLATES this: given a clean keyword-spec the
   substrate synthesizes+executes at 0.75; the benchmark difficulty is the English-parse, NOT synthesis/execution.)
2. **Statistical fluency** -- which novel words/phrases are natural. (Substrate has SYSTEMATIC generation: composition, retrieval-
   emission, Wug-test morphology all 1.0; the gap is the learned distributional language model, NOT systematic rule-based generation.)

## Why this matters (commercial / strategic)
- Substrate-as-symbolic-engine claim is EMPIRICALLY strong: math/code/structured-communication/systematic-generation all work substrate-only.
- The LLM is the NATURAL-LANGUAGE INTERFACE (parse English in, fluent English out); the substrate is the SYMBOLIC REASONING CORE.
- This is the honest architecture: LLM front-end (NL <-> structure) + substrate back-end (symbolic cognition, memory, reasoning).
  Clean division of labor, each doing what it is strong at. NOT "substrate replaces LLM" -- "substrate is the reasoning/memory
  engine the LLM lacks."

## Only honest weak spot inside substrate-native
- Judgment/DETECTION (bug-detection 0.57) -- anomaly-margin signal is weak for localized defects. (code2 rescue dispatched separately.)

## Production decider (parallel)
- kb25k genuine HELD-OUT 0.996 at real 25K facts (validated after DISC_POOL-cap fix). kb50k genuine running (~4h, slow-eval).
  Curve so far: 10k=0.9945, 25k=0.996.

## Next (recommend)
- Quantify the English-parse bottleneck with ONE real benchmark end-to-end (MATH or HumanEval real) -> expect low (confirms
  the decomposition with a real number).
- code2 bug-detection rescue R1 (verified-correct bundle).
- kb50k -> kb100k genuine scaling.
- Path-A statistical-fluency is the genuine LLM boundary -- recommend NOT chasing it substrate-only (it IS the LM); instead
  position substrate as the symbolic core behind an LLM NL-interface.
