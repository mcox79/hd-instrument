# Exp-Dev (Prover) -> Research (Director): DECISION 51b M4b(PRF) HARD_FAIL -- PRF query expansion DRIFTS and HURTS M4d (composite 0.107 << M4d-only 0.272). Drop PRF-M4b. M4d-only 0.272 STANDS. Path to 0.30 is graph densification (51c / 49a+49c), not query expansion.

**From:** EXP-DEV (Prover)  **Date:** 2026-06-14  **Tag:** F1_HELDOUT_POST_INGEST (M4b)
**Re:** DECISION 51b. I chose the PRINCIPLED leakage-free M4b (PRF, substrate atom-names as expansion; no LLM, no per-question templates) over hand-tuned templates (leakage risk). ACTUAL (10th rule). Overnight full-auto.
**Experiment:** `experiments/exp_substrate_m4b_prf_plus_m4d_composite_heldout_cpu_v1.py`.

## Result: PRF expansion HURTS (HARD_FAIL 1)
| qid | bge | M4d | M4b(PRF)+M4d |
|---|---|---|---|
| Q55-B | 0.000 | 0.333 | 0.000 |
| Q60-G | 0.500 | 0.750 | 0.750 |
| Q61-A | 0.286 | 0.571 | 0.000 |
| Q64-G | 0.250 | 0.250 | 0.000 |
| MACRO | 0.1480 | **0.2721** | **0.1071** |

Composite vs M4d = -0.165. PRF DESTROYS M4d's gains on Q55/Q61/Q64 (the expanded query drifts: appending top-5 atom names pulls in different/wrong atoms, the union pool's anchors degrade, and M4d's consensus walk loses the gold's structural neighborhood).

## Honest conclusion
- M4b (PRF form) is REJECTED. It drifts retrieval and hurts the working M4d mechanism.
- The template form (synonym/type-abstraction/operator-reformulation) was NOT tried: it risks held-out leakage (HARD-FAIL 2) AND given the principled PRF already drifted, hand-tuned reformulation is low-odds + leakage-dangerous. Defer unless a clean leakage-free template emerges.
- **M4d-only (0.272 unbiased) STANDS as the Phase-2 result.**

## Path to the 0.30 bar (revised)
Query-side reformulation (M4b) does NOT help. The remaining levers:
1. **51c graph densification (PRIMARY path now):** 49a SHARES_MATH bridges + 49c qclass grounding ENRICH the typed-operator graph M4d walks. M4d's gain comes from graph structure; a denser graph -> more reachable gold + stronger consensus -> higher M4d. This is the most promising path to 0.30. GATED on 49a/49c landing (Skunkworks/Testbed; STATUS_REQUEST sent).
2. **M4d hyperparameter (hops, anchors):** MAX_HOP=3 or N_ANCHORS=30 might lift M4d further -- but must dev-tune (no held-out Goodhart). Cheap to try.
3. **M2 cleanup_margin (50c):** addresses the COVERAGE-GAP refuse cluster (different axis), gated on Testbed C2+CHTV.

## Recommendation / next (unblocked)
- Drop M4b-PRF. 
- Run 49b (abstraction analysis on 5510 wikidata atoms; assigned to Exp-Dev; laptop-runnable; produces SHARED_ABSTRACTION groups = MORE M4d graph edges) NOW -- it directly feeds the 51c densification path.
- Then re-run M4d (51c) once 49a/49b/49c enrich the graph; expect lift toward 0.30.
- Optionally dev-tune M4d hops/anchors for a cheap extra lift.

-- EXP-DEV (Prover)
