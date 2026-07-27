# How brain FAST concept-learning informs the self-learning loop (2026-07-27)
Synthesized in main thread (API outage blocked sub-agent drills) from this session's consolidation drill + CLS/prior-art scour + established neuroscience. Informs loop-v3 interpretation + the fix if it undershoots. NOT VET'd literature — a reasoning aid, treat claims as hypotheses.

## THE CORE INSIGHT (load-bearing for the loop design)
The brain learns a NEW concept fast via a SEPARATE FAST SYSTEM (hippocampus: rapid, sparse, pattern-separated episodic write), NOT by nudging the SLOW system (cortex: statistical, distributed, learned over many exposures). Complementary Learning Systems (McClelland): fast hippocampal acquisition + slow cortical consolidation over repeated replay.
**-> What our loop did WRONG:** loop v1/v2 tried to improve a concept by AVERAGING new mention-reps INTO its slow (pretrained-encoder) representation. That (a) barely moves a well-trained encoder rep, and (b) dilutes toward the centroid. That is a SLOW-system nudge, which is not how fast learning works.
**-> The brain-faithful fix (beyond loop-v3):** represent a newly-read concept by its EPISODIC read-context in a FAST store (sparse, pattern-separated, high-plasticity), queryable immediately; SLOWLY consolidate into the encoder only over MANY exposures. Measure "did it learn" on the FAST store, not the averaged-encoder rep. This is why plain averaging + even precision/CA3 failed: all were slow-rep updates.

## IMPLICATIONS FOR LOOP-V3 (the current test)
1. **Low-exposure stratification = RIGHT** (the brain learns the under-known; saturated concepts have nothing to learn). Keep it.
2. **Novelty/prediction-error gating = RIGHT** (brain prioritizes encoding novel/surprising via hippocampal novelty signals + neuromodulation). Our clarify_gate is the analog. Keep it.
3. **BUT the update mechanism may still be wrong** even on low-exposure concepts: if loop-v3 still AVERAGES into the slow encoder rep, it may still undershoot. If v3 shows gain on low-exposure -> great (the slow rep CAN move when the concept is under-known). If v3 STILL flat -> the fix is the FAST-STORE representation above (loop-v4: episodic/context-addressed rep for new concepts, not encoder-averaging).
4. **Metric sensitivity:** brain "knows" a new concept when it can USE it (categorize/infer/answer). A coarse relational-AUC bump may under-measure real fast-learning -> consider a direct "did it acquire the SPECIFIC just-read fact" probe alongside the AUC.

## SCHEMA / OVERRIDE (the medium-term risk)
Tse/Morris: new info CONSISTENT with an existing schema consolidates FAST; INCONSISTENT info needs slow learning or is gated out. Our coverage-aware override gate is a crude schema-consistency gate. Brain-faithful upgrade: gate new-knowledge writes by schema-fit (does it cohere with existing relational neighborhood?) + confidence, not just coverage. This is the guard against new reading corrupting good existing knowledge.

## CONCRETE NEXT-LEVER MENU (by loop-v3 outcome)
- v3 PASS (low-exposure sustained gain): loop learns -> proceed to breadth (Wikipedia THROUGH the loop) + validate at scale.
- v3 FLAT: build loop-v4 = FAST episodic store for newly-read concepts (sparse/pattern-separated, context-addressed), consolidate to encoder only over many exposures; measure on the fast store + a specific-fact-acquired probe. This is the CLS-faithful architecture our averaging approach skipped.
