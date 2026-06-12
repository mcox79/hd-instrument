# Exp-Dev -> Research: Path 5 schema retrieval HARD_FAIL 0.36 -- 4th triangulation angle (operand-selection corpus-bound); Path 1 SRL decision?

**Date:** 2026-06-12  **From:** Exp-Dev (full-auto)  **Re:** operand-selection drill HANDOFF Path 5 (cheap-first)

## Path 5 hippocampal schema retrieval: acc 0.3592 -- HARD_FAIL (<+0.04 over 0.39)

| approach | acc | note |
|---|---|---|
| naive majority-op (no retrieval) | 0.2385 | baseline |
| **Path 5 schema retrieval (k=7)** | **0.3592** | retrieval WORKS (+0.12 over majority -- exploits ASDiv schema-repetition) |
| discriminative perceptron | ~0.39 | global classifier |

Schema retrieval lifts +0.12 over naive majority (so retrieving similar solved scenarios DOES add signal), but lands BELOW the
discriminative classifier and does NOT break the plateau (lift -0.03 vs 0.39). The retrieval transfers the OPERATION from similar
problems, but selecting WHICH numbers for the new problem still needs its specific scenario semantics = the corpus bottleneck.

## 4th INDEPENDENT triangulation angle -> operand-selection is corpus-bound

| # | mechanism class | ASDiv-1op | 
|---|---|---|
| 1 | discriminative perceptron | 0.39 |
| 2 | world-model schema-simulation (E4) | 0.34 |
| 3 | BMA ensemble (4 operand strategies) | gain=0 |
| 4 | **hippocampal schema retrieval (Path 5)** | **0.36** |

FOUR distinct mechanism classes plateau 0.34-0.39. Per the drill fail-band + [[substrate-mwp-triangulation-corpus-bound-3rd-confirmation]]:
this is the 4th independent angle confirming the MWP operand-selection plateau is COMPREHENSION/CORPUS-bound, NOT mechanism-bound.
Per refined brain-can-do-it: honest negative IS evidence; strongly supports the USER math+science ingestion priority. NOT a ceiling.

## Path 1 SRL decision (your call)

Per drill sequencing: "Path 5 first (cheap); Path 1 SRL second only if Path 5 < +0.06." Path 5 IS < +0.06 (-0.03), so Path 1 SRL
(P_deflated 0.55, +0.10-0.18 predicted) is the drill's next path. BUT it's MEDIUM cost (3-5d: CoNLL-2005 SRL ingestion + perceptron +
HRR binding), and the triangulation is now 4-DEEP (strong corpus-bound evidence).

Two honest options:
1. **Build Path 1 SRL** -- highest-predicted path; the linguistic-comprehension angle is genuinely DIFFERENT from the 4 structural/
   statistical mechanisms tried; per brain-can-do-it I should try it before fully concluding corpus-bound. (3-5d; needs CoNLL-2005 bundled.)
2. **Defer Path 1 to Phase-6** -- 4-deep triangulation already strongly supports corpus-deficiency; Phase-6 math+science ingestion is
   the empirically-supported lever; re-run all paths post-ingest with richer grounding.

I lean toward (1) IF you can bundle CoNLL-2005 SRL data (substrate has no SRL corpus yet) -- it's the one genuinely-different angle
(linguistic ARG-role ground truth) not yet tried. Otherwise (2). Your call. Path 5 queued (official).
