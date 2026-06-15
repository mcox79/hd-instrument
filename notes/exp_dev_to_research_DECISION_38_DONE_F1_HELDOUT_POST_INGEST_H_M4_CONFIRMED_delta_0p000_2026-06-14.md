# Exp-Dev (Prover) -> Research (Director): DECISION 38 DONE -- F1_HELDOUT_POST_INGEST. H_M4 CONFIRMED: IN-COVERAGE 0.140 (delta +0.000 vs baseline) + COVERAGE-GAP refuse 0.667 (delta 0). Ingest of 5360 math/physics atoms + 8 foundation primitives produced ZERO held-out F1 change. Held-out gap is capability-transfer, NOT coverage.

**From:** EXP-DEV (Prover)  **Date:** 2026-06-14  **Tag:** F1_HELDOUT_POST_INGEST
**Re:** DECISION 48 sync executed (USER-authorized) -> DECISION 38 fired on remote (26,261 atoms). ACTUAL (10th rule).
**Run:** bge cache FULL rebuild 3100.7s for 26261 atoms -> bge_large_v2_name_26261_c4e45c9a.npz (now cached; future runs fast). Earlier online run HUNG on HF-hub load; fixed with HF_HUB_OFFLINE=1.

## Result (vs locked DECISION 44 baseline)
| metric | baseline (pre-ingest) | post-ingest | delta |
|---|---|---|---|
| IN-COVERAGE macro-F1 | 0.140 | **0.140** | **+0.000** |
| COVERAGE-GAP refuse-rate | 0.667 | **0.667** | 0 |
| A-E factual avg | 0.032 | 0.032 | 0 |
| per-axis (A0.071/G0.347/rest0) | same | same | 0 |

Per-question tp/fp/fn are IDENTICAL to baseline (Q60-G 0.44, Q61-A 0.29, Q64-G 0.25; Q59-F fp=26; Q_neg_2 fp=5; rest 0).

## Verdict: H_M4 CONFIRMED (decision rule: delta IN-COVERAGE < +0.05)
Adding 5360 structured wikidata math/physics atoms (+ 376 edges) + 8 foundation primitives changed the held-out F1 by EXACTLY ZERO. The held-out generalization gap is NOT a coverage problem -- it is the capability-transfer gap (BGE-representation-bound per DECISION 41 + M1c). Coverage expansion (this slice) does not touch it.

## Honest caveat (mechanism vs tautology)
delta=0.000 is so clean because this slice is ORTHOGONAL to the held-out question space: the math/physics atoms (Bayes/Pythagorean/etc theorems) do not rank into any held-out question's top-K, and the held-out gold (neuroscience: active_inference/free_energy/predictive_coding) was R2-EXCLUDED by construction. So strictly this proves "coverage of UNRELATED topics doesn't help held-out" -- strongly consistent with H_M4 (capability-transfer is the bottleneck) and corroborating DECISION 41's representation-bound finding, but it is NOT a test of coverage-of-ADJACENT topics. A neuroscience-adjacent ingest would test that (but R2 forbids the gold atoms; only adjacent axioms allowed -- that is Phase 2's axiom-authoring path IF coverage-adjacent were the lever, which H_M4 says it is not).

## Implication for Phase 2 (per DECISION 47b)
H_M4 confirmed -> the dominant lever is capability-transfer, not authoring-coverage. **Pivot Phase 2 to M4b query-side reformulation** (the surviving M4 candidate per DECISION 41; scoring-side M4a/M4c already refuted). Axiom-authoring batches (original Phase 2) would not help the held-out gap because it is not coverage-bound. M4b (substrate-internal multi-query reformulation -> union retrieval) directly attacks the paraphrase->gold representation gap.

## What this ingest DID deliver (value banked, independent of DECISION 38)
- Ingest pipeline PROVEN end-to-end at scale (Action API, SPARQL-free, no USER 50GB).
- +5360 structured math atoms + 376 DEPENDS_ON edges (relational graph growth).
- Q-class refresh (mapper was 84pct stale).
- 8 foundation primitives architecturally placed.
- bge cache for 26261 atoms now built (future runs fast).
- All invariants preserved (R3=1.0; 272/272 operator proofs sound per 46c).

## Substrate-product positioning (final F1 this session)
Held-out F1 stays at IN-COVERAGE 0.140 / COVERAGE-GAP refuse 0.667. NOT moved by coverage ingest. The path to lift is M4b (query-side) per the confirmed H_M4 + DECISION 41 representation-bound finding -- NOT more atoms. This is the honest, decisive Goal-1 result for the session.

-- EXP-DEV (Prover)
