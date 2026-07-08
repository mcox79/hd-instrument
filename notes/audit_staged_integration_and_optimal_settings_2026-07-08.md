# Staged-Integration + Optimal-Settings Audit (disk-grounded) -- 2026-07-08

Read-only map (nothing changed). Answers: what is the operational substrate actually running on, and are its defaults the certified-optimal ones. Basis for the bottom-up (brain-evolution-ordered) integration plan.

## Structural facts
- 4,741 `experiments/*.py` cells vs ~73 `hdlab/` modules vs ~633 chain-grade cert atoms (1,521 ledger rulings). hdlab is a CURATED SUBSET -- certified experiments are NOT auto-promoted.
- `verification/` suite re-run on main NOW: **132 passed, 3 skipped, 44s** (on-disk data/certification.md report is stale 2026-06-19, but code is green). The IMPLEMENTED layer provably works.
- The gap is INTEGRATION DEBT, not Stage-1 correctness.

## Stage-by-stage (cert / in-hdlab / default-optimal)
STAGE 1 (foundation): substantially IMPLEMENTED + near-optimal. Every primitive has a real module; defaults CG-anchored (WM K/bank=64 banks=64 env=4096; refuse V_REL=256; clarify tau 0.35/0.55; LTM alpha=1200/8192; cortex n_dim=8192; HRR/FHRR dtype-dispatched). GAPS: (1) BSC is NOT a first-class binding primitive (only ad-hoc _bipolar_bind in context_retention) despite the "BSC for edge" claim; (2) cleanup readout default = argmax/Hopfield, NOT the certified peel/SIC.
STAGE 2 (meta): schema/time-decay/ultrametric/coarse-grain/NREM-consolidation IMPLEMENTED + optimal. EXP-ONLY (CG'd but not promoted): lock-in amp, compose-freq routing.
STAGE 3 (capability): multi-hop/generation/attention IMPLEMENTED. EXP-ONLY / not-default: combinedgate_v8 arbitration; BG Go/NoGo action-selection; and THIS SESSION's CG wins -- peel/SIC readout, retained-trace coarse-to-fine, glass-box retrieve-gate-audit-requery loop (cortex has only advisory scaffold), teacher-free encoder -- all cert-only. CLS discrete-budget partial (core CA3/CLS in hippocampal_encoder). CA3-completion now firm-MM at n=8 (was tentative).
ENCODER: concept_encoder.py (native WTA) EXISTS, but the OPERATIONAL KB query defaults to `char_trigram_v1` (LEXICAL) -- biggest default gap (confirmed by dogfood: confidence ~0.31, misses semantic + same-session work).
STAGE 4 (LM): deferred.

## Verdicts
- Is Stage 1 implemented + optimal? SUBSTANTIALLY YES (green suite, CG-anchored defaults) EXCEPT the peel/SIC readout gap (a Stage-1-level lever) and BSC-not-first-class.
- Are we using the optimal low-level settings? Mostly yes for the certified CORE; NO for the two highest-value levers: cleanup readout (argmax not peel/SIC) and encoder default (lexical char_trigram, not semantic).

## Bottom-up integration order (recommended)
1. STAGE-1 COMPLETENESS (cheapest, everything inherits): promote peel/SIC into cleanup_family.PRIMITIVES (selectable bundled-recovery readout); add BSC as a first-class binding.py primitive.
2. STAGE-2 promotion: lock-in amp + compose-freq routing -> hdlab.
3. STAGE-3 readout/retrieval: wire retained-trace coarse-to-fine into context_retention; consolidate CLS discrete-budget onto hippocampal_encoder; promote the glass-box loop to a hdlab module.
4. ENCODER (gated on in-flight R1 landmark rescue): land native semantic encoder, flip the operational KB default off char_trigram_v1, fold in teacher-free objective.
5. DEFERRED: cross-modal binding, BG Go/NoGo, self-manager dials (exp-only/immature).

## Provably-suboptimal defaults = highest-value cheap wins
1. Cleanup readout argmax/Hopfield, not peel/SIC (certified 0.204->0.940 @J8, +0.74, 5-seed, no retrain) -- not even in the module. BIGGEST CHEAP WIN.
2. Encoder default lexical char_trigram_v1 (native/teacher-free certified better).
3. Retained-trace dense read not wired (certified 0.992 recovery at 0.20x cost).
(Minor: ExperimentSpec default N=1024/FHRR below the CG operating point 4096-8192; harmless, callers override.)
