# SKUNKWORKS BUILD VET CHECKLIST -- consolidated for the 2026-06-17 GO (SINGLE EXECUTABLE REFERENCE)
Consolidates the full session's accumulated gates (DECISIONs 165/171/172/174/175 + my VETs) into one ordered
list. Run this per verdict as the graded cells land. Supersedes the scattered VET notes for execution purposes.
Posture: GATE-READY HOLD; Phase B GO = Option B 2026-06-17 morning (USER-direct). run_mode=full tier-A is the
ONLY load-bearing verdict.

## A. PRE-FLIGHT (before STAGE 1 smoke runs tomorrow) -- pre-registration gates (Lakatos no-ex-post)
- [ ] Smoke abort-thresholds PRE-REGISTERED IN CODE (K, M, pass/fail lines) -- no ex-post tuning.
- [ ] Smoke-gate MIDDLE-band action pre-registered: FPE top-1 in [0.80,0.95) OR confusion in (0.10,0.30]
      -> proceed to STAGE 2 but cardinality verdict = cleanup-confound-SUSPECT -> dual-head control MANDATORY.
- [ ] Dual switch-trigger RECONCILED to ONE rule: amplification-delta >=0.05 = dual-head-control trigger;
      FPE top-1 <0.80 = hard STAGE-2 block. Both lines pre-registered.
- [ ] cardinality compute_verdict() bands already pre-registered + 8 self-tests PASS (confirmed).

## B. SMOKE-GATE ASYMMETRY (STAGE 1) -- one-directional evidence
- [ ] smoke FAIL -> valid cheap abort/redesign (informative).
- [ ] smoke PASS -> licenses STAGE 2 ONLY. ZERO load-bearing verdict; NEVER recorded as HARD-PASS/PARTIAL/
      corroboration. Does NOT clear the 3 HARD-FAIL modes at scale -> STAGE 2 re-checks all 3.

## C. PER-VERDICT CROSS-CUTTING GATES (apply to EVERY STAGE-2 cell)
- [ ] run_mode=full, N=4096, n_seeds>=3 (tier A). Smoke/single-seed = NOT load-bearing.
- [ ] compute-backend provenance recorded (backend+dtype+device). Near-threshold (within ~1e-3 of bar)
      cross-checked on alternate backend. Same backend within a sibling-set for fair margin comparison.
- [ ] control-leak-free: identical input across configs; no target-in-key (the ternary leak class).
- [ ] vector-native readout (no graph-walk bypass / no learned codebook -- 11th rule).
- [ ] no-stale-artifact: no partial metrics.json from the killed Option-C run (b56ijrsbc) persists as a result.
- [ ] cell-verdict sourced from write_metrics.json, NOT cell name (the Collins mis-sourcing class).

## D. CARDINALITY arm (3 siblings x C0/C1/C2/C3)
- [ ] C0 graph-walk-trace control instrumented (rules out graph-walk readout).
- [ ] C2 ESCAPES: exact-count RMSE<=1.0 AND >=2x C1 reduction (AGGREGATE); quantifier acc>=0.80 AND
      (C2-C1)>=0.20 (RATIO/accuracy). Per-sibling metric TYPE correct (exact-count=RMSE; quantifier=accuracy).
- [ ] C1 FAIR-NULL: best-honest-basis, crosstalk-subtracted; fails for the CARDINALITY reason. EVADABLE-DROP:
      if C1>=0.70 the basis already closes it -> NOT a cardinality gap (report EVADABLE, a TRUE result).
- [ ] single-role CONFOUND-ISOLATION.
- [ ] CAPACITY-ENVELOPE: out-of-envelope low C2 = ARTIFACT, not HARD-FAIL (regime-calibrated alpha).
- [ ] FPE-CONFOUND DUAL-HEAD CONTROL -- DOWNGRADED to CONTINGENCY for the INTEGER arm (DECISION 176 + my 196th VET).
      WHY: integer-power FPE codewords are ORTHOGONAL (E[cos((a-b)theta)]=0, integer d!=0); STAGE-1.2 empirical
      confirmed amp=0.000, nn_confusion=0.000 at N=4096 M=2000 k=5 -> cause (c) FPE near-neighbor confusion is
      EMPIRICALLY RULED OUT for integer counts. So a cardinality HARD-FAIL now has 2 live causes for the integer
      arm: (a) substrate lacks the primitive = TRUE HARD-FAIL; (b) classical capacity exceeded = ARTIFACT (capacity-envelope).
      CONTINGENCY (fires only if a STAGE-2 integer cell UNEXPECTEDLY shows amp>=0.05 OR nn_confusion>0.10):
        run the dual-head (naive-max-cos vs Hopfield/kernel-aware) as a regression-to-continuous-grid check.
      RE-ESCALATE to MANDATORY if any cardinality sibling uses CONTINUOUS/fractional magnitude (e.g. proportion-
      based "most") -> the sinc-kernel concern returns there; Drill-4 length-scale + kernel-aware cleanup apply.
      CAVEAT (asymmetry): the integer-clean result is SMOKE -> STAGE 2 full CONFIRMS it holds (not yet load-bearing).

## E. TERNARY arm (partial-symmetric corr(bundle,c))
- [ ] CLEAN-SYMMETRY two-layer scope: MATH-corpus-scoped + RELATES-excluded; document/provenance anchors dropped.
- [ ] Canonical base = math-scoped MOTIF-B = 20, AT THRESHOLD (>=20 bar, zero margin) -> require majority-close,
      not a razor 20-count; one contested instance matters.
- [ ] PER-EFFECTIVE-FAMILY (5 families; DFT-meta 45% dominant): require >=majority close AND >=2 NON-DFT
      families. DFT-only closure = Fourier-specific, NOT general -- report as such.
- [ ] 38-op BIMODAL full-basis equivalence-check: C2 corr(bundle,c) closes where ALL 38 single binders fail
      (the ghrr lesson -- no single-op exclusion).
- [ ] FAIR-NULL (over-strict-null): assembly_2 random target recoverable-in-principle by corr(bundle,c)
      (design-checked: corr=1.0 on a non-DFT family; confirm at full scale across 5 families n>=3). c-sensitivity
      + a-b asymmetry are the ONLY added discriminators.
- [ ] no-gerrymander (real mined motifs; incl no document-citation + no facet-counting soft-gerrymander).

## F. C3 (both arms; internal-abstraction-discovery)
- [ ] discovery != leakage: seed EXCLUDES the C2 composite.
- [ ] reusability: PROVABLY_EQUIVALENT_BY_CAPABILITY + extends to a 2nd signature (not just >=0.80).
- [ ] composes with existing 38-op basis; substrate-internal (no learned codebook).
- [ ] cardinality-C3 FAIL -> DISTINGUISH search-limited (tuning) vs tier-3-boundary (USER-architectural Phase-C
      trigger; FPE TIER-3 recipe ready per Drill 2+4). ternary-C3 = definitively-tier-2 pure-discoverability
      (FAIL = search-limited only).

## G. VERDICT-TYPE + PROMOTION
- [ ] Honest priors (TIGHTENED per DECISION 177): MIDDLE_BAND most likely (~0.45-0.50); C2 HARD-PASS ~0.27-0.30
      (modest upward from 0.22 -- FPE-decode SUBPATH de-risked by smoke, but full C2 = cleanup-distinct-count +
      sibling probes + multi-seed is UNTESTED; NOT the over-aggressive 0.35-0.40); C3 0.18. MIDDLE_BAND is a real
      reportable outcome (per-sibling breakdown, no spin) -- not a near-miss.
- [ ] Any HARD-PASS -> atom: 3-of-3 gate (cap-pres + re-expressibility + closes-gap/serves-utility) + 4-gate
      pre-check (forward-walk + corpus-monotone + axiom-term + dangling) + STRICT vet. Provenance per metric
      type. cap_pres=1.0 HARD-FAIL gate (Testbed). Don't fabricate grounding-deps to phantom atoms (verify first).

## H. META (when reporting)
- [ ] Cross-drill convergence claims: discount by SHARED-SOURCE overlap (Drill 3+4 both cite Frady-Kleyko-
      Sommer -> bounded, not full, independent confirmation).
- [ ] modern-Hopfield/kernel-aware cleanup IF activated: beta closed-form (Ramsauer Thm-4), NOT learned (11th);
      cap_pres=1.0 under BOTH heads; additive (naive-max-cos stays default); activation gated on smoke trigger.
- [ ] supplementary bAbI-7 / Steinert-Threlkeld: substrate-standalone measured FIRST (11th); eval-only, NOT
      ingested (22nd firewall).

-- SKUNKWORKS (Auditor), consolidated 2026-06-16 ~14:46; run per-verdict at the 2026-06-17 GO.
