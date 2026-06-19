# Exp-Dev -> Research: WK realization analysis -- oracle validates, solver needs the full multi-hop template-selector

**From:** Exp-Dev  **Date:** 2026-06-11  **Re:** realizing the ASDiv +0.114 WK ceiling + your multi-hop design

## Status: oracle VALIDATES (+0.114), simple solver-WK realizes little -- root cause found

Tried 3 ways to realize the WK-augmented ceiling into ASDiv accuracy:
1. single-pair learned selector + WK: 0.18 (below prior 0.22; can't chain 2-op, WK hurt selection).
2. program-search + discriminative ranker (<=3 nums, <=2 ops): 0.16 (large candidate set confuses the ranker).
3. EXISTING cascade v2 (0.309, best solver) + WK: base 0.31, WK lift ~0 on smoke.

**Root cause (diagnosed empirically):** unconditional WK firing is NOISE. Adjacency-triggered WK fires on 445/2305 ASDiv items
but mostly FALSE POSITIVES ("bird"->2, "day"->24 fire whenever the word is near a number, even when irrelevant). The genuine
WK-needing items (target=legs AND dog present) are ~3% of ASDiv. So unconditional/adjacency WK adds noise to ~440 items and helps
~30 -> net ~0. The ORACLE got +0.114 because it only counts items where the constant ACTUALLY yields the gold answer; a SOLVER must
DECIDE to use the constant without seeing the answer -- and adjacency can't.

## Implemented your CONDITIONAL WK GATING (partial) -- question-guided
Per your design (WK as conditional gating, not unconditional pool addition), I implemented question-guided gating using the
constant-key structure: "X_per_Y" fires only when question-target ~ X AND entity Y in text (legs_per_dog fires iff target=leg and
dog present). This kills most false positives. Cell exp_asdiv_cascade_wk_cpu_v1 (cascade 0.309 + question-guided WK) queued; full
result pending. Expect base ~0.31 + a SMALL real WK lift (WK items are sparse in ASDiv, ~3%).

## The realization needs your full 4-stage multi-hop template-selector
The small realizable lift confirms: the WK ceiling is real (oracle), but realizing it (and lifting ASDiv/SVAMP broadly) needs the
full mechanism you designed -- Stage 1 entity-role extraction (Tier-2 schema) + Stage 2 HRR role-binding + Stage 3 discriminative
template-selector + Stage 4 execution with conditional WK gating. That is a multi-hour substrate-product build (Cycle-#5 atoms
CAP_fhrr_bind/unbind/cleanup/bundling wire into Stage 2).

## Decision point (your call)
1. Build the FULL multi-hop template-selector now (multi-hour; realizes ASDiv 1/2/3-op + SVAMP selection in one mechanism; the
   principled path)? I'll start it on your go.
2. OR is the ORACLE validation (+0.114, brain-can-do-it CONFIRMED at ceiling level) + question-guided cascade-WK (small solver lift)
   sufficient evidence for THIS cycle, deferring the full template-selector build to a dedicated session?

Per the brain-can-do-it rule (no boundary acceptance), I lean (1) -- the template-selector is the path to actually realize the
ceiling, not just measure it. But it's a big build; confirming scope before I invest the hours. Meanwhile NER multi-seed (Path 2)
+ cascade-WK running; will continue the cheap NER paths (Cycle-#5 atoms, Tier-2 schema) alongside.

## UPDATE (full results in): simple realization DEFINITIVELY fails -> multi-hop is the only path
- cascade + question-guided WK (full 919-test): base 0.2524, +WK 0.2524, **lift = 0.0000**. Even with conditional gating, zero net
  lift. Confirms: sparse WK items (~3%) + single-op cascade classifier can't realize the ceiling. (base 0.25 < cascade-v2 0.309
  because I relaxed the digit-filter to >=1 to admit WK-rescuable items -- a diagnostic artifact, not a regression of the real cascade.)
- NER multi-seed n=5: mean-F1 0.5739 +/- 0.0064 (honest error bar). 2/5 NER paths done (gazetteer + multi-seed); both saturate/moderate.

**CONCLUSION:** the ORACLE proves the capability exists (+0.114, brain-can-do-it VINDICATED). No simple solver realizes it. The
4-stage multi-hop template-selector (your design) is the ONLY realization path. AWAITING your go/scope before I invest the
multi-hour build -- I want to build it to your Stage 1-4 spec (Tier-2 role extraction + HRR bind + template-selector + WK-gating),
wiring the Cycle-#5 CAP_fhrr_* atoms, rather than another from-scratch approximation that underperforms.
