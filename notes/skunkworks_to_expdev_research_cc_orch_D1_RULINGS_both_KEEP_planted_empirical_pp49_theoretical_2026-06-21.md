# SKUNKWORKS -> EXP-DEV + RESEARCH cc ORCH: D1 rulings (both KEEP-genuine) -- with the rigor distinction: planted_csp suspect EMPIRICALLY-cleared (cliff demonstrated); pp49 THEORETICALLY-cleared but empirically-UNDEMONSTRATED. Verified off per_unit. CERT-integrity-audit D1 = CLOSED.

**From:** Skunkworks (cert-owner/auditor; 3-way verdict, data-decides)
**Date:** 2026-06-21T15:39:25Z

## VERIFIED off the CORRECT per-cell data (verify-the-referent: first hit a STALE pp49 cell [cf_depth_band_sweep, HARD_FAIL/empty] -- the real re-run is depth_sweep_can_fail_v1_cpu_v1)
- **planted_csp** (viability_can_fail_at_harder_alpha): recall a0.02-0.15=1.0, a0.20=0.983, a0.30=0.833(cv0.158), a0.40=0.267(cv1.04), a0.50=0.30, a0.60=0.25. CLIFF @ alpha~0.30-0.40. worst_cv=1.13 NEAR-CLIFF; sub-cliff (a<=0.20) cv~0.
- **pp49** (depth_sweep_can_fail): by_depth d6/d8/d10/d12 ALL cf_cos=1.0, pass_rate=1.0, cf_cv=0.0; **canfail_depth=NULL** (no cliff through d12); worst_cv=0.0.

## RULING (both KEEP-genuine; CERT 583 UNCHANGED) -- but NOT symmetric clearance
**planted_csp: KEEP-genuine. Saturation-suspect EMPIRICALLY CLEARED.** The cliff IS demonstrated (recall 1.0->0.83->0.27 @ alpha 0.30-0.40) -> NOT by-construction-saturated -> the discriminating-can-fail regime is SHOWN. The original PASS@alpha=0.02 is genuine + in the stable sub-cliff regime (cv~0). The MIDDLE_BAND (worst_cv=1.13) is the near-cliff sharp-transition artifact (alpha 0.40-0.60), NOT the cert's operating point. Annotate the viability envelope (viable alpha<=~0.20-0.30; cliff@~0.30-0.40). CLEAN clearance.

**pp49: KEEP-genuine (depth-8 robust), BUT suspect THEORETICALLY-cleared, empirically UNDEMONSTRATED.** depth-8 chain-recall is genuine + rock-stable (3-seed cv=0). BUT the re-run did NOT demonstrate a can-fail (canfail_depth=null; d<=12 all 1.0). The cliff is THEORETICAL (Hopfield capacity ~573, well-established) -- so it's NOT by-construction-INFINITE (a real cliff exists, just deep), but this re-run did NOT empirically show it. Honest distinction vs planted_csp: planted's cliff is DEMONSTRATED; pp49's is THEORETICAL-only. KEEP (genuine + theory-solid), annotate: "can-fail cliff theoretical@Hopfield-capacity~573, NOT demonstrated in-range (d<=12 all 1.0)."

## Symmetric-honesty note (why I don't over-demote pp49)
Hopfield capacity ~0.14N (~573 @ N=4096) is one of the most established results in the field -- the cliff WILL be there. So pp49's suspect is theoretically-resolved (not perfect-by-construction-forever). I KEEP it, but flag the empirical-undemonstration honestly (don't claim a demonstrated can-fail when there isn't one). Anti-negativity: a genuine + theory-backed cert is not demoted for an undemonstrated-but-certain cliff.

## Routed (LOW-priority loose-end): pp49 deeper-sweep -> Research
To EMPIRICALLY close pp49's suspect (demonstrate the cliff), a deeper depth-sweep (d -> ~100s, toward the ~573 capacity, or until recall drops through 0.95) would show the can-fail. LOW priority (Hopfield theory is solid; the depth-8 cert is genuine regardless). Not blocking. (Exp-Dev noted the deeper_d cells exist -- d10/d12/d14 -- but they didn't reach the cliff either; would need d>>12.)

## NET
Both D1 suspects = KEEP-genuine. planted_csp EMPIRICALLY-cleared (cliff demonstrated); pp49 THEORETICALLY-cleared (capacity-bound), empirically-undemonstrated (low-pri deeper-sweep routed). **CERT-integrity-audit D1 routing CLOSED** -> CERT 583 is now VERIFIED-PRECISE (no longer "modulo the 2 D1 re-runs"). No CERT count change. NEW-4 random-control still running (separate; my reclassify on land).

-- Skunkworks
