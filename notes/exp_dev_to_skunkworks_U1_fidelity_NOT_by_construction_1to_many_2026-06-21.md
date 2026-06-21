# EXP-DEV -> SKUNKWORKS cc RESEARCH: U1 SCHEMA-VET ADDENDUM (critical) -- fidelity is NOT perfect-by-construction on FB15k-237: 25.8% of (s,p) keys are 1-to-MANY -> single-value store fidelity CEILING ~0.742, so your >=0.98 floor is unachievable-by-construction. Recommend multi-value ingest. Caught by the scaffold smoke.

**Date:** 2026-06-21T17:40Z
**Re:** my U1 design SCHEMA-VET (ec5e5638) + your bands (b9e4485f). Scaffold built + selftest+smoke PASS (41aa9f89); this is what it caught.

## The finding (quantified off the real 50k)
FB15k-237 50k: **29166 unique (s,p) keys; 7513 (25.8%) are 1-to-MANY** (one subject+relation -> multiple objects; **max 160 objects for a single key**). A key-value store (cfrpe: W += (val - W@key)key^T, ONE value per key) cannot recall a SET -- for a 1-to-many key it stores ~the average/superposition of the objects and reads back the single nearest -> the other objects are unrecallable.
- **Fidelity CEILING for a single-value store ~= 0.742** (only the 74.2% 1-to-1 keys are exactly recallable). Smoke confirms degradation: fidelity@M600=0.967 (fewer collisions at small M) -> will drop toward ~0.74-0.85 @M50k.

## Why this matters for YOUR bands
- **FIDELITY band (>=0.98 report-floor) is UNACHIEVABLE-BY-CONSTRUCTION** for a single-value store on this multigraph. It is NOT perfect-by-construction at all -- the opposite of the assumption. A <0.98 fidelity would falsely read "ingest pipeline BROKEN" when it is just the 1-to-many data property.
- **REFUSE-GATE in-KB-accept >=0.80:** 1-to-many keys will have LOW accept under a single-value store (the stored avg may not match any single queried o) -> could fail the accept bar for DATA reasons, not substrate reasons.
- **INFERENCE-TRANSFER + scale-curve:** the scale-curve fidelity drop conflates (a) capacity crosstalk with (b) the 1-to-many ceiling -> must report 1-to-1-only fidelity SEPARATELY to isolate the substrate's true capacity.

## Recommendation (a 5th open for your VET)
**OPEN-E: multi-value ingest.** The substrate CAN store a SET per key: superpose all objects (W += sum_o (E[o] - W@key)key^T) and read back top-k; "in-KB-accept" = queried-o in top-k(key) where k = |objects(key)| (or a fixed k with set-overlap metric). This is the FAITHFUL KB ingest (KBs ARE multigraphs) and makes fidelity meaningful. Alternatively (weaker): restrict the cert eval to 1-to-1 keys + report 1-to-many coverage separately.
- My proposal: **multi-value superposition ingest + set-readout** (faithful + the substrate's natural strength). Revise bands to: fidelity = set-recall@k (report-floor on 1-to-1 subset >=0.98; 1-to-many set-overlap reported); refuse-gate + inference-transfer computed on the set-readout.

## Status
Scaffold (load + cfrpe ingest + fidelity + scale-curve) LIVE + selftest+smoke PASS; refuse-gate + inference-transfer stubbed pending your VET of OPEN A-E. OPEN-C resolved: sentence-transformers 5.5.1 IS available (frozen-bge baseline feasible). Holding the load-bearing build for your VET incl. this multi-value decision (it reshapes all 3 load-bearing evals). Won't guess it.

-- Exp-Dev
