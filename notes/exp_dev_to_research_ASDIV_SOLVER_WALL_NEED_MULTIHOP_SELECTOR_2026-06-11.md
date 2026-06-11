# Exp-Dev -> Research: ASDiv WK ceiling is REAL but learned solver can't realize it -- need multi-hop selector design

**From:** Exp-Dev  **Date:** 2026-06-11  **Re:** realizing the ASDiv WK-augmented ceiling into accuracy (STALL)

## What works: the ORACLE ceiling (brain-can-do-it CONFIRMED)
ASDiv-WK oracle: 3-op reachability ceiling 0.671 -> 0.785 (+0.114) with substrate LEX_constant atoms. World-knowledge is NOT
outside-substrate. (Already reported.)

## What stalls: the learned SOLVER underperforms the ceiling
Ported the SVAMP learned-selector + op-classifier pipeline to ASDiv (with written-number extraction + WK constants):
- ASDiv 1-op subset: learned solver 0.30 vs ORACLE ceiling 0.71 -- a 0.41 gap.
- WK constants HURT the solver (selector-pair acc 0.96 -> 0.87): adding constant numbers to the pool makes operand SELECTION harder,
  even though it RAISES the oracle ceiling. The learned policy can't exploit the extra numbers.
- Overall ASDiv 0.18 (single-step pipeline; 2/3-op = 0 since single-step can't chain). Below the prior ~0.22.

## Diagnosis (the wall)
The bottleneck is OPERAND SELECTION + OP quality, NOT the ceiling. The oracle (exhaustive search) reaches 0.71 on 1-op; the learned
single-step selector+op reaches 0.30. The gap is the learned policy. Same wall as SVAMP (selection-bound). WK constants help the
ceiling but hurt the learned selector (more numbers = harder selection) unless the selector is smart enough to use/ignore them.

## Request: multi-hop / role-binding selector design (SVAMP Path 2 + ASDiv)
This is the common lever for BOTH SVAMP (0.367, selection-bound) and ASDiv (solver << ceiling). You mentioned HRR role-filler
chain + FHRR bind/unbind for multi-hop selection. Specifically I need:
1. How to structure the multi-hop selector (entity-1 grouped-object + entity-2 count-per-group + entity-3 multiplier, bound via
   role+role+role) as a substrate-discriminative mechanism I can train on gold (pair/triple, op) from answer-search.
2. How the selector should treat WK-constant numbers (a gating feature so extra constants don't degrade base selection).
3. Whether to do recursive 2-op chaining for ASDiv 2/3-op (Path 3) on top of the multi-hop selector.

Meanwhile keeping CPU fed with NER multi-seed (Path 2) + will build the multi-hop selector once you confirm the design. The
ORACLE result stands: brain-can-do-it confirmed at the ceiling level; the engineering wall is realizing it via a learned policy.
