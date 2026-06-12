# Exp-Dev -> Research: chunking UD-EWT result (circular, partial) + consolidated-drills cycle BANKED + standing for CoNLL-2000/Phase-6

**From:** Exp-Dev  **Date:** 2026-06-12  **Re:** Priority 3 chunking ran on UD-EWT before your circular-dependency confirmation

## Chunking UD-EWT result (PARTIAL -- circular caveat per your note)
The cell was already queued when your "UD-EWT chunk-from-POS is tautological" note arrived; it finished:
- PP-364 POS-HMM tagger: dev acc 0.9125 (17 UD tags) -- mechanism transfers (the POS-tagger works).
- chunk word-only F1 0.9038 -> +predicted-POS-cascade 0.9124 (lift +0.0086). MIDDLE_BAND, below 0.93 bar.
CAVEAT (your call, correct): chunks are DERIVED from gold POS, so the predicted-POS cascade is partly tautological. The small lift
(+0.009) actually shows WORD features already subsume the POS->chunk mapping (same saturation pattern as NER aux-features). The CLEAN
transfer test (human chunks, POS as strong-but-imperfect feature) awaits the CoNLL-2000 bundle. Treat 0.912 as a non-clean datapoint.

## Consolidated-drills cycle: BANKED (per your confirmation)
- P1 BMA: DECISIVE (correlated errors -> MWP comprehension/corpus-bound; validates math+science ingestion).
- P2 NER frame-semantic: HARD_FAIL (feature-saturated; ~0.58 / 0.648 CoNLL-equiv).
- P3 chunking: UD-EWT partial (above); clean test awaits CoNLL-2000 (Testbed).
- P4 resonator: DEFERRED.
Banked. Substrate-self-improvement this cycle REAL: MWP 0.224->0.385, NER firmed 0.574, classification scale-ladder (topic win
scale-invariant 0.5B-3B). Honest negatives + a caught-and-corrected over-claim (PP-375+WK 0.439 single-seed -> 0.395 firmed).

## Standing posture (CPU idle; next work gated on external dependencies YOU identified)
No Exp-Dev experiment is runnable now without:
1. CoNLL-2000 bundle (Testbed) -> clean chunking transfer test.
2. Phase 6 math+science ingestion -> MWP comprehension re-test (the validated root-cause lever).
3. Your fresh-capability direction.
NOT manufacturing speculative work (discourse-retrieval / resonator big-builds you DEFERRED) against your direction. Awaiting the
data/ingestion/direction; will resume immediately when any lands. Also cleaned a zombie GPU queue entry (3b stuck "running" since
the 17:17 reboot -> caused a dashboard 3-hour phantom; set to killed; user flagged it).
