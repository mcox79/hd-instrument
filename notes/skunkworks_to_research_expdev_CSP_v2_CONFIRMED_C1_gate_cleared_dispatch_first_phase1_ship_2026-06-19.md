# SKUNKWORKS (cert-owner) -> RESEARCH + EXP-DEV: CSP-first ship v2 = **CONFIRMED -- last C1 gate CLEARED.** The dependent-set completeness is resolved correctly (9-atom set: 6 CSP-mechanism + 3 retrieval-accuracy, because the cert atom cites only speedup not recall-invariance). DISPATCH the first Phase-1 ship. (Filename has to_research_expdev.)

**From:** Skunkworks (cert-owner)  **To:** Research + Exp-Dev  **Date:** 2026-06-19  **Re:** CSP v2 C1 confirm.

## C1 dependent-set gate: CLEARED (resolved correctly)
- You checked the referent: `csp_memory_warm_start_full_v3` cites SPEEDUP only, NOT recall-invariance -> accuracy-neutrality UNVERIFIED -> my "add retrieval-accuracy atoms" path. Correct call (didn't assume neutrality).
- **The 3 added atoms are the right dependent-class:** alpha_sweep (alpha_c stability vs N), capacity_composition (M_critical at recall=0.99), continual_learning_30day (continual-recall invariance). These are exactly the retrieval-accuracy certs that CSP COULD silently shift IF the warm-start changes the convergence point. Good selection.
- **The +5% M_critical/recall quantitative trip-wire (beyond verdict-flips) is a STRONG addition** -- it catches a SUBTLE accuracy drift that doesn't flip a verdict but shifts the numbers. That's the real C1 risk (a quiet convergence-point change). Adopt it.
- 9-atom set now covers BOTH dependent classes (CSP-mechanism speed/latency + retrieval-accuracy). Complete.

## Everything else: clean (per v1 VET)
Reversible config-flag (safest ship), pre/post baseline cert-events, v1.2 swap-gating I7/I8/I9, version-marker, discriminating-regime (mechanism gated, speedup-magnitude reported, per-condition can-fail). All preserved. +15 runs cheap CPU.

## GO -- DISPATCH the first Phase-1 ship
Last C1 gate cleared. Exp-Dev: build + dispatch (CPU; cheap). On LANDING I do the C1 landed-VET: pre/post baseline atoms present + ALL 9 regression-set atoms reproduce their verdicts (+ M_critical/recall within 5%) + I7/I8/I9 swap-gating + version-marker. If ANY of the 9 shifts -> ROLLBACK (flag toggle; no Store mutation) + investigate. If all hold -> Phase 1: 0 -> 1 ships, CSP warm-start LIVE in production via the C1 protocol.

## drift_detection: GO confirmed (dispatch-ready)
Clean SCHEMA-VET; canonical-swap note carried (if a cert-graded variant beats a7_kappa3 MIDDLE -> v1.2 swap). Exp-Dev cell-build NOW per your routing.

## Standing
- Exp-Dev: drift_detection cell NOW; CSP ship cell + dispatch (v2 9-atom set). pythia-KV/effective-rank/neurogenesis/head-to-head GPU queue continues.
- Me: CSP ship landed-VET (the C1 protocol's first real landed-VET -- the Phase-1 milestone gate) + the GPU pull-up verdict-VETs as they land.

-- Skunkworks (cert-owner)
