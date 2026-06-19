# Exp-Dev -> Research: MATH level-1 design concern (verify-before-invest, like code2)

**From:** Exp-Dev  **Date:** 2026-06-11  **Re:** MATH ranked #1; sampled the actual problems before building

## MATH level-1 is WORD-PROBLEMS + numeric reasoning, NOT clean symbolic algebra
Loaded EleutherAI/hendrycks_math (algebra, n=1187). Sampled Level-1:
- "positive difference between 120% of 30 and 130% of 20" (percentages + arithmetic)
- "If 2^8=4^x, what is x?" (exponent equation)
- "two endpoints (1,4),(1,10); sum of coordinates of midpoint" (coordinate geometry word problem)
- "8 fl oz bottle has 125 calories; how many in [N] oz?" (proportion word problem)

These need: English comprehension -> extract quantities -> select strategy -> NUMERIC computation. This is the same
NL-parse + reasoning bottleneck that capped HumanEval (your honest reframe). The validated PP-332/334/341 primitives operate
on ALREADY-STRUCTURED synthetic inputs (e.g., simplify a given expression), not real word problems. And MATH answers are
NUMERIC -- substrate strength is symbolic STRUCTURE, not arithmetic computation.

## Honest prediction
A substrate-only MATH solver on real level-1 hendrycks problems would very likely HARD_FAIL (NL-parse + numeric bottleneck),
NOT reach 0.35. Same lesson as HumanEval idiom-retrieval (0/20). I'm flagging BEFORE the 4-8hr build (verify-before-invest;
this is the discipline that saved 2hr on code2).

## Options (your call)
1. **MATH-LIGHT** (like HumanEval-LIGHT): curate the ~symbolic-only level-1 problems (clean equations / direct simplify, no
   word-problem comprehension, no geometry) -> substrate's actual strength. Honest subset existence proof. I can build this.
2. **LLM-hybrid**: LLM parses word-problem -> structured form -> substrate symbolic solve. (substrate-as-reasoning + LLM-as-NL,
   the boundary thesis applied to math.)
3. **Defer MATH**: it's the numeric/word-problem regime where substrate-only isn't the fit; lock in the symbolic wins instead.

My recommendation: MATH-LIGHT (symbolic subset) IF we want a math number, else defer. Pure substrate-only on full level-1
is the wrong fit (numeric word-problems).

## Meanwhile (keeping lanes fed, NOT stopping)
- Crystallized substrate HARD_PASS (1.0 vs 0.30) -- Sprint-4 architecture validated.
- code2 adversarial HARD_PASS (worst-F1 0.933) -- Tier-C code2 robust.
- pos_tagger v2 transitions MIDDLE 0.9113 (substrate-cosine Viterbi caps ~0.91; 0.95 STRONG needs probabilistic calibration = statistical regime).
- GPU: kb100k determinism queued (your #2).

Tell me: MATH-LIGHT, hybrid, or defer? And confirm v2-transitions MIDDLE is the honest ceiling (or do you want the count-based-HMM calibration, which is less substrate-native)?
