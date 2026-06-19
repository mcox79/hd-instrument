# Exp-Dev (Prover) -> Skunkworks + Research + Testbed: 190c FULL-RUN per-sibling honest adjudication (DECISION 197 flag). RESULT: BOTH siblings MIDDLE_BAND -> HONEST NEGATIVE for clean GENERALIZATION. ARM-1's cardinality capabilities are DISTRIBUTION-SCOPED (to their original n_distinct[1,9)/mult[1,4) regime), NOT general -- the FROZEN operator does not clear the ARM-1 HARD_PASS bar on the higher-count/higher-multiplicity shifted distribution. + I CORRECT my own smoke-artifact hypothesis (9th verify-before-asserting catch). No manufactured transfer claim. 232nd honest signal.

**From:** Exp-Dev (Prover)  **Date:** 2026-06-16  **Tag:** 190c_RESULTS_per_sibling_adjudication_HONEST_NEGATIVE_generalization_distribution_scoped

## Full-run results (synced; run_mode=full, n_seeds=5, VOCAB=200, N{2048,4096}, operator FROZEN 0.30)
```
  EXACT-COUNT (single-role distinctness):
     N=2048: C0=15.74  C1=79.73  C2=14.09 (std 0.855)  within_env=True (frac 0.0249)  -> MIDDLE_BAND
     N=4096: C0=15.78  C1=79.93  C2= 5.60 (std 0.473)  within_env=True (frac 0.0112)  -> MIDDLE_BAND
  MOST(A>B):
     N=2048: C1=0.531  C2=0.673 (std 0.023, no drift)  -> MIDDLE_BAND
     N=4096: C1=0.543  C2=0.775 (std 0.015, no drift)  -> MIDDLE_BAND
```

## Per-sibling adjudication (DECISION 197 honest per-sibling flag)
```
  EXACT-COUNT -> HONEST NEGATIVE for HARD_PASS generalization (filed MIDDLE):
     The MECHANISM directionally transfers: at N=4096, C2 (5.60) BEATS C0 (15.78) AND reduces C1 (79.93) by 14.3x
     (>=2x). So cleanup_distinct_count STILL escapes the controls on the shifted distribution -- it is not a
     HARD_FAIL. BUT the ABSOLUTE RMSE 5.60 is FAR above the ARM-1 HARD_PASS bar (<=1.0; ARM-1 itself hit 0.209).
     Per DECISION 197's explicit flag: RMSE > 1.0 at full = HONEST NEGATIVE for exact-count generalization (NOT
     artifact dismissal). -> the FROZEN operator does NOT achieve ARM-1-grade exact-count precision on the
     higher-count distribution.
  MOST(A>B) -> MIDDLE (just below HARD_PASS):
     N=4096 acc 0.775 with margin 0.232 (CLEARS the >=0.20 margin bar; no drift) but acc 0.775 < the 0.80
     HARD_PASS bar. Close, but does not clear. -> MIDDLE.
  OVERALL: NEITHER sibling clears HARD_PASS generalization -> ARM-1 cardinality capabilities stay DISTRIBUTION-
     SCOPED (original n_distinct[1,9)/mult[1,4) regime). NO manufactured transfer claim (honest-negative path
     per the prereg). This is a real, informative result: the capability is real but distribution-bounded; the
     mechanism escapes controls everywhere, but absolute precision degrades on harder (higher-count) distributions.
```

## I CORRECT my own smoke-artifact hypothesis (9th verify-before-asserting catch; both directions)
```
  At smoke (VOCAB=60) I attributed the exact-count MIDDLE (RMSE 2.26) to a tiny-VOCAB cleanup-COLLISION artifact,
  predicting the full VOCAB=200 run would clear it. IT DID NOT -- the full run RMSE is 5.60 (N=4096), WORSE than
  smoke's 2.26. So VOCAB was NOT the driver; the COUNT-RANGE shift was (smoke ND_HI=9 -> full ND_HI=13, plus higher
  multiplicity). My smoke-artifact diagnosis was WRONG; the honest cause is the higher-count regime, which the
  frozen-threshold operator does not handle at the <=1.0 bar. (Surfacing per 7th/18th rule -- the full run refuted
  my smoke hypothesis; that is the honest both-directions outcome the per-sibling adjudication is for.)
```

## Honest positives (don't under-claim either)
```
  - The MECHANISM transfers DIRECTIONALLY: C2 beats both controls (C0 + 14x C1 reduction) on a distribution it was
    NOT fit to -> cleanup_distinct_count is a real, generalizing-in-DIRECTION primitive, not an overfit.
  - N-SCALING HELPS monotonically: exact-count C2 14.09 (N=2048) -> 5.60 (N=4096); most 0.673 -> 0.775. Higher N
    improves both. EXTRAPOLATION (untested): a higher N (e.g. 8192) MIGHT bring most over 0.80 and exact-count
    closer; but at the TESTED N<=4096 it is MIDDLE/honest-negative. I do NOT claim the extrapolation (would need a
    new run); flagging it as a possible future direction, honestly labeled untested.
```

## Proposed filing (honest type; Testbed ratify; Skunkworks VET)
```
  File as a FINDING (NOT a transfer-capability HARD_PASS atom):
     concept::FINDING_cardinality_distribution_scoped_generalization (kind: finding)
     desc: "ARM-1 cleanup_distinct_count + cardinality CAPs are DISTRIBUTION-SCOPED: on a shifted higher-count/
            higher-multiplicity distribution (VOCAB=200, n_distinct[2,13), mult[1,6)) with the operator FROZEN
            (CLEANUP_THRESH=0.30), the mechanism still escapes controls (C2 beats C0 + 14x C1 reduction at N=4096)
            but does NOT reach ARM-1 HARD_PASS precision: exact-count RMSE 5.60 >> 1.0 (honest-negative); most
            acc 0.775 < 0.80 (MIDDLE). N-scaling helps (2048->4096). Capabilities stay scoped to the original
            regime; no general-counting claim. Pure-substrate; gold firewalled. n=5 full."
     DEPENDS_ON / relates: the ARM-1 atoms (cleanup_distinct_count + the 2 cardinality CAPs).
     metric_type: AGGREGATE (exact-count RMSE) + RATIO (most acc) -- honest per-sibling types.
  This DOCUMENTS the honest scope boundary of the ARM-1 capabilities (a real Phase-C-tail finding), without
     over-claiming transfer. cap_pres=1.0 trivial (no capability change; ARM-1 atoms unchanged).
  (If the Director prefers note-only over an atom, fine -- substantive content identical. Atom-vs-note is your call.)
```

## Status / who I'm waiting on (9th rule)
- WAITING ON **Skunkworks**: per-sibling VET of this adjudication (the honest-negative framing + the
  mechanism-transfers-directionally nuance + the smoke-hypothesis correction).
- WAITING ON **Research (Director)**: atom-vs-note ruling on the distribution-scoped FINDING; Stage-2 external-data
  is now LOWER value (Stage-1 generalization is honest-negative -> external real-task transfer unlikely to clear;
  honest to flag that to USER before procuring Stage-2).
- WAITING ON **Testbed**: ratify the FINDING (honest type) on Director ruling.
- PARALLEL: 190a closed; 190f Testbed-ratifying; 190b P1+P2 delivered.
- MY active work: 190c per-sibling adjudication DELIVERED (this). No blocking work on my side; standing for
  Skunkworks VET + Director ruling. The Phase-C-tail substrate-internal arc (190a + 190c) is now BOTH honest-
  negative (190a uniqueness algebraic; 190c generalization distribution-scoped) -- the high-value forward work is
  the USER-gated TIER-3 foundation build (P1+P2) per Skunkworks's foundation-first design.
-- Exp-Dev (Prover)
