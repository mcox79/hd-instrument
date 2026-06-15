# Research (Director) -> Skunkworks (Auditor): SUBSTRATE-INTERNAL CELL -- measure in-coverage gold connectivity profile BEFORE 55a blind-author pass (informs edge budget + HARD-PASS bar; substrate-on-its-own per 11th rule)

**From:** Research (DIRECTOR)  **Date:** 2026-06-15 ~07:25
**Re:** d11b8b42 hop/beta ceiling result + 27th honest correction (49a NEUTRAL on held-out). Two corroborating signals say the in-coverage held-out gold lives in a SPARSE 2-hop neighborhood. Quantify BEFORE 55a authors edges into it.
**Per:** USER overnight full-auto + auto mode

## Why this cell now

Two corroborating ceiling signals:
- d11b8b42: hop=3 identical to hop=2 (sparse graph fully reached at 2 hops within current density)
- 27th finding (51c preview): 49a generic-foundation bridges delta +0.0000 (not on gold neighborhood paths)

Both say the gold neighborhood is structurally thin. Quantifying that thinness:
- Tells us the a priori HARD-PASS bar for 55a (how many edges does it actually need)
- Lets us check if 0.30 is achievable at all from gold-targeted edges OR if M4d 0.272 is the architectural ceiling regardless
- Substrate-on-its-own (11th rule): measure substrate's own structure before authoring into it

## What to measure (substrate-internal; no held-out question inspection)

The 7 in-coverage gold atoms are PUBLIC math concepts (their NAMES are known; the QUESTIONS asking about them are NOT):
- kl_divergence, mutual_information, fhrr_unbind, cosine_cleanup, structured_perceptron, and the two others from Exp-Dev's 51c preview gold inventory

For each gold atom in the SUBSTRATE GRAPH (not bge), measure:
1. **hop-1 degree** = number of direct edges (DEPENDS_ON / SHARES_MATH / SPECIALIZES / USES / INSTANCE_OF / INVERSE_PAIR) incident to the gold atom
2. **hop-1 typed-degree breakdown** = how many of each edge type
3. **hop-2 reachable-set size** = unique atoms reachable in <=2 hops
4. **hop-2 reachable-set composition** = which atoms (gold's textbook neighbors? generic foundations? unrelated?)
5. **anchor-overlap** = of the M4d anchor set (N_ANCHORS=20 on bge), how many lie within hop-2 of the gold? (this is the consensus-path density the walk actually uses)

Aggregate stats:
- median / min / max hop-1 degree across 7 golds
- median / min / max hop-2 reachable size
- median anchor-overlap

## HARD-PASS / HARD-FAIL

**HARD-PASS (the cell completes):** report delivered with the 5 measurements + interpretation: is the gold neighborhood thin (median hop-1 degree <= 5), medium (5-15), or already dense (>15)?

**HARD-FAIL:**
- Inspecting held-out questions to derive gold list (READ ONLY the gold-atom NAMES from substrate; do not open `data/heldout/q*.json` or equivalent question files)
- Fabricating any number (10th rule: validate-method-on-data before report)
- LLM-as-judge (forbidden)

## Why this is Skunkworks (Auditor), not Exp-Dev

This is a STRUCTURAL DESCRIPTION of the substrate (Auditor lane: measurement honesty + falsification floor), not a NEW MECHANISM run (Prover lane). Skunkworks substrate-internal counting routine -- cheap; CPU; ~20-30 min.

## Output

`notes/skunkworks_to_research_GOLD_CONNECTIVITY_PROFILE_*.md` with the 5 measurements + interpretation + a priori HARD-PASS bar suggestion for 55a (e.g., "median hop-1=3, so 55a should author ~5x as many edges per gold to materially shift M4d's consensus walk; expect ceiling lift +0.X if achievable").

## Composition with DECISION 55a (blind-author pass)

This cell runs BEFORE 55a authoring. Its output:
- Informs the edge-count budget per gold atom
- Sets a priori HARD-PASS bar for the 51d M4d re-run AFTER 55a
- Gives a STRUCTURAL ESTIMATE of whether 0.30 is reachable from edge authoring alone OR if 0.272 is the architectural ceiling needing a different mechanism

If output says "gold already has median hop-1 >= 15 and hop-2 reachable >= 100" -> the graph is NOT structurally thin; M4d 0.272 is bge-bound or scorer-bound, not graph-bound. STOP 55a authoring; pivot to a different mechanism (Phase 3 CO-EVOLVE-1 or M2 cleanup_margin).

If output says "gold median hop-1 <= 5 and hop-2 reachable <= 30" -> graph IS thin; 55a authoring has real headroom; proceed per DECISION 55a spec with budget = (target_density - current) * gold_count.

## Safety / invariants

- ASCII only
- Substrate-on-its-own (11th rule)
- No held-out question inspection (R2 / 15th rule)
- No LLM-as-judge
- No fabricated numbers (10th rule)
- Local CPU only

Tag: SUBSTRATE_INTERNAL_CELL_GOLD_CONNECTIVITY_PROFILE -- Research (Director)
