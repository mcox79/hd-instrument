# Design: PRELIM middle tier + generalization-fed staged consolidation (crutch-fade)

Director design note (USER-directed 2026-08-10). Task SHAPE + pointers for exp_dev; exp_dev designs all params.

## Why (the fault this fixes)
The crutch-fade SIQa arc hit a clean BINARY tradeoff (commit 74d310e11, DISK-VET'd):
- HIGH promote gate (pme8): consolidation-fidelity OK, but fade tiny (fire-rate rel-drop 0.124) + only 90/6768 banked items promote.
- LOW gate (pme4): fade real (rel-drop 0.346) BUT consolidation-fidelity COLLAPSES (native lib_acc 0.39 < crutch cru_acc 0.45 = lossy per-item copies).
- Comprehension flat ~+0.012-0.03 (< +0.05) at every gate. ~6678 sub-threshold crutch-fills sit INERT.
So: promote-or-discard cannot buy both fade AND fidelity. DO NOT resolve by loosening the gate (that is the lossy-copy trap).

## What to build (USER architecture; brain = Complementary Learning Systems, graded consolidation)
A real 3-tier staged consolidation, replacing the binary cliff with promote-or-ACCUMULATE:
- **Tier 0 CRUTCH (CSKG)**: fires only on a predictive-coding-flagged gap. Fades. (unchanged)
- **Tier 1 PRELIM** (hippocampal fast store): when the crutch fills a gap, RETAIN the fill (native-format, LOW trust) even below the promote gate. On RE-ENCOUNTER of a similar gap: (a) consult PRELIM first and USE it to answer -> this is the fade lever (crutch fires less because prelim covers the gap, gate untouched); (b) INCREMENT its evidence (exposure++, consistency strengthens if the new observation agrees).
- **Tier 2 NATIVE** (neocortical schema): only well-evidenced, GENERALIZED items cross the still-STRICT gate -> high-fidelity, so fidelity never collapses.

## The crux (the missing wiring, already-owned organs)
Feed the GENERALIZATION organ off the PRELIM tier (the resume synthesis flagged this as "owned, not yet fed crutch content"):
- CLUSTER related prelim traces (CA3/DG attractor clustering) + induce a schema (learner MDL rule-induction).
- The CLUSTER's COMBINED exposure x consistency can cross the HIGH promote gate even when NO single item did -> "combined info eventually passes the gate" (USER).
- Promote the GENERALIZED schema (not a lossy per-item polarity copy) -> keeps native high-fidelity AND covers UNSEEN gaps -> comprehension climbs beyond memorized items.

## Owned-organ pointers (verify + reuse; do NOT rebuild)
- `hdlab/grounding_acquisition_loop.py` -- `consolidation_pass` (the two gates: schema-coherence BANK -> overlay; exposure/consistency -> `native_store` promotion; `_vote_margin`; `promotion_log`; `native_store=None` preserves prior behavior). This is where the PRELIM retain + accumulate + generalization-feed wire in.
- `hdlab/hd_fact_store.py` -- native trust-bound (REL/ARG/SOURCE/TRUST) store; supports a TRUST GRADIENT (candidate for prelim=low-trust vs native=high-trust in one store, or a separate prelim store -- exp_dev's call).
- `hdlab/script_grain_acquisition_loop.py` -- `ScriptLibrary.match_or_spawn` = the schema-induction / CA3-DG clustering organ (the generalization).
- `hdlab/learner/` (core.py + plugins + registry.py) -- MDL rule-induction / generalization plugins. (NB: the learner MEMORIZED WIQA edge-polarity because that was un-learnable world-knowledge; HERE the target is clustering/abstracting crutch-SUPPLIED facts, a different regime.)
- `hdlab/predictive_coding.py` -- the gap-flag gate.
- Cell: `experiments/exp_crutch_fade_social_iqa_v1.py` (the 4-arm SIQa fade-curve harness w/ BOW/LIBRARY/CRUTCH/ABSTAIN telemetry, exposure checkpoints, scramble control, re-encounter-fade + consolidation-fidelity metrics). EXTEND it; keep the binary as the baseline arm to beat.

## HARD-PASS criteria (exp_dev sets exact bands; these are the SHAPE)
1. FADE GROWS vs binary WITHOUT loosening the gate: prelim-tier fire-rate rel-drop > binary's 0.124 at the SAME strict pme.
2. FIDELITY PRESERVED: consolidation_fidelity_ok stays True (native lib_acc >= crutch cru_acc) -- native must not go lossy.
3. COMPREHENSION CLIMBS: gap_driven lift > binary's +0.012, and RISES across exposure checkpoints as the generalized native library grows (the thesis curve).
4. COMBINED-EVIDENCE PROMOTION WORKS: count of items promoted via CLUSTER/generalized combined-evidence > 0, and those promotions are high-fidelity (answer >= crutch).
5. CONTROLS HOLD (non-negotiable, VET hardest): scramble-clean (scramble never beats real) + no-regression-below-BoW (abstain-gate guarantee) preserved. Prelim must not inject wrong facts (bounded leakage; inconsistent prelim traces not pulled as confident answers).

## Ablations that make it a real test (not a construction proof)
- prelim-WITHOUT-generalization (retain+pull but no clustering) -- isolates whether the generalization FEED is what lets combined evidence cross + comprehension climb.
- prelim-WITHOUT-pull (retain but not consulted at re-encounter) -- isolates whether the re-encounter pull is the fade lever.
Both must underperform the full 3-tier for the mechanism claim to hold.

## Guardrails
Branch dataprep/mcguffey-graded-corpus (NOT main/origin). Resumable per-unit. Real held-out dev. self-test PASS before smoke; smoke before FULL. Commit after each landed result. Only benchmark = Social IQa (ATOMIC-matched crutch). VET every arm on disk; scramble is the load-bearing control.
