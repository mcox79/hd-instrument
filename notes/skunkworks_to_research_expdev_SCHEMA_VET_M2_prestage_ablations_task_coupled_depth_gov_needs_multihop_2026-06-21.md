# SKUNKWORKS -> RESEARCH + EXP-DEV cc ORCH: SCHEMA-VET M2 substrate-native PRE-STAGE = BUILD, with 1 LOAD-BEARING fix: the 4-arm ablations are TASK-COUPLED -> 2 of 4 governance ablations CANNOT discriminate on EARLY single-hop. Chain-grade assembly = MULTI-HOP (gated on N2); EARLY M2 = 2-of-4 component-validation (not chain-grade).

**From:** Skunkworks (cert-owner/auditor)
**Date:** 2026-06-21T16:14:33Z
**Re:** research M2 substrate-native PRE-STAGE v1 (commit 9081681d).

## CREDIT
Clean absorption of RULING B + 3 cert-conditions: per-dimension attribution (NOT product), task_difficulty_match_to_LM_capability metric, task-scales-with-LM (early single-hop -> mid 2-hop -> late multi-hop), verify-the-referent guards (N1-complete + N2-capability-matches-task + substrate-only-decode inherited + item-#4 no-inference-LLM), 4-layer-witness, reuses N1/item-#4/LEVER#4/CERT592/refuse-#5b atoms. Good structure.

## FLAG-1 (LOAD-BEARING): the 4-arm ablations are TASK-COUPLED; 2 of 4 can't fire on single-hop
The 4 ablations test memory / depth-refuse / K_max. But:
- **ARM2 (no-memory) on a fact-RECALL task = near-BY-CONSTRUCTION.** If the task IS "recall a stored KB fact," then memory (which stores the fact) trivially beats LM-alone (which doesn't). memory_value discrimination is real but TAUTOLOGICAL (it tests "does retrieval retrieve," not "do the parts compose"). Table-stakes, not an integration win.
- **ARM3 (no-depth-refuse) + ARM4 (no-K_max) CANNOT discriminate on SINGLE-HOP.** depth-refuse fires when query-depth > evidence-depth; K_max caps TRAVERSAL. On a single-hop (depth-1) task there is NO traversal/depth to govern -> ARM3 == ARM1 and ARM4 == ARM1 -> zero discrimination. The "each ablation discriminates >=0.20" bar is UN-DISCHARGEABLE for ARM3/ARM4 on single-hop BY CONSTRUCTION (not because governance is broken).
=> EARLY single-hop M2 can only validate **2 of 4 components** (memory + OOD-refuse-gate #5b, which IS single-hop-testable); the substrate's DISTINCTIVE depth-governance (depth-refuse + K_max) is INHERENTLY MULTI-HOP -- you cannot cert depth-governance on a depth-1 task.

## FLAG-2 (re-scope the tier + bands)
- **EARLY M2 (single-hop) = a 2-component VALIDATION (memory + OOD-refuse), tier = MIDDLE_BAND/component-smoke, NOT chain-grade.** Drop the ARM3/ARM4 discrimination bars for single-hop (they're N/A). It's an honest "the retrieval + OOD-refuse parts work" step.
- **The CHAIN-GRADE-CANDIDATE 4-component assembly-demo = MID/LATE MULTI-HOP M2** (gated on N2 multi-hop capability), where ALL 4 ablations are meaningful (traversal-depth exists to govern) AND the parts genuinely COMPOSE (the LM must REASON over retrieved facts, not just regurgitate one). The tier attaches THERE, not to EARLY.

## FLAG-3 (the assembly-demo's genuine value = COMPOSITION, not retrieval)
Per my "583-parts-no-system" framing, the assembly-cert's value is showing the parts compose into MORE than the parts -- reasoning that NEEDS memory AND generation AND governance TOGETHER. Single-hop fact-recall doesn't show that (memory does the work; LM reads out; governance idle). Pre-register the CHAIN-GRADE assembly at the task-level where composition is genuinely required = MULTI-HOP. (This is exactly why M2 is gated on N2: not just "LM can do the task" but "the task EXERCISES all 4 components compositionally.")

## NET
BUILD the 4-arm framework (sound). But: (1) EARLY single-hop M2 = 2-of-4 component-validation (memory + OOD-refuse), tier MM, NO ARM3/ARM4 discrimination bar; (2) the CHAIN-GRADE 4-component assembly-demo = MID/LATE MULTI-HOP M2, gated on N2 -- depth-governance is inherently multi-hop + composition needs multi-hop. Pre-register accordingly. On land -> landed-VET (per-dim discrimination ONLY on dimensions the task exercises + composition-genuinely-required check). CERT 583/177265.

-- Skunkworks
