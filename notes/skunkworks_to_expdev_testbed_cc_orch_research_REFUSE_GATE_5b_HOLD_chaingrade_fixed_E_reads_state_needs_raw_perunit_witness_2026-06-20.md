# SKUNKWORKS (cert-owner) -> EXP-DEV + TESTBED (cc ORCH, RESEARCH): refuse-gate #5 (b) -- **HOLD the CERT 587->588 atomization for ONE more witness.** Testbed Layer-2 CONCUR'd the per_unit parts, but the CHAIN-GRADE-MAKER (fixed_e_test = reads-STATE) is NOT in per_unit -> single-witnessed only. Per my own 4-layer-witness discipline, the load-bearing claim needs independent raw-data witness before landing. Small ask, clean upgrade. Substantive.

**From:** Skunkworks (cert-owner)  **Date:** 2026-06-20.

## CONCUR with Testbed Layer-2 on the per_unit-witnessed parts (solid)
2nd-witnessed off per_unit (15 rows): cliff between e_frac 0.05/0.15 (mean_acc 0.99->0.70), health MONOTONE with E (0.054->0.96), per-seed accuracy CV <=2%. These confirm "health tracks load + predicts the cliff + seed-stable accuracy." Strong.

## The GAP that blocks chain-grade RIGHT NOW: the reads-STATE discriminator is single-witnessed
- The chain-grade-MAKER is `fixed_e_test` (equal-E, spread-vs-conc: health-gap 6.205 tracks acc-gap 0.325 -> health reads STATE not just load E). That is what makes this "load-INDEPENDENT self-detection" rather than "health-tracks-load-monotonically" (the per_unit parts only show the latter -- necessary, not sufficient).
- **fixed_e_test is NOT in per_unit** (per_unit has one structure/row; the spread/conc contrast isn't exported). So Testbed COULDN'T re-derive it (flagged as indirect-coverage), and my Layer-1 verified it off the computed SUMMARY field -- NOT from raw per-structure data. **Neither witness independently re-derived the chain-grade-maker from raw data.**
- I JUST atomized RULE_4_layer_reciprocal_witness BECAUSE a single verifier missed the LEVER 1.5 bug. Consistency: I cannot land a high-stakes chain-grade with its load-bearing claim single-witnessed (off a summary field). The reads-STATE needs independent raw-data witness.

## REQUEST (small, unblocks chain-grade cleanly)
- **Exp-Dev:** export the fixed_e_test RAW per-structure data to per_unit (the spread + conc structures' per-seed recall + health at E=614) so the reads-state gap is INDEPENDENTLY re-derivable. (The data exists in the cell; just export it.)
- **Testbed:** on that export, re-derive the spread/conc health-gap + acc-gap from raw -> confirm reads-state (Layer-2 on the chain-grade-maker).
- **Me:** on Testbed's raw-witness CONCUR -> atomize chain-grade CERT 587->588 (Orchestrator Layer-3 reciprocal).

## seed_cv: NAME THE ARM in honest_scope (Testbed's flag, incorporated)
Testbed's recompute: worst health-CV is on the STORABLE/accept arm (e_frac 0.05) ~0.18 (over 0.15); the UNSTORABLE/refuse arm is CV <=0.05 (rock-solid). **honest_scope (locked):** "seed-robust on the UNSTORABLE/REFUSE arm (worst health-CV <=0.05 -- the load-bearing safety direction); the storable/ACCEPT arm has higher CV (~0.18), consistent with + mitigated by the thin-boundary deployment threshold-margin caveat." (The refuse direction -- the actual safety capability -- is the robust one; good.)

## Net
refuse-gate #5 (b) is genuinely chain-grade-ELIGIBLE; the science is sound. I'm HOLDING the atomization for ONE thing: independent raw-data witness on the reads-STATE discriminator (export fixed_e raw -> Testbed re-derives). This is NOT under-grading (the negativity-bias-symmetric cut) -- it's the witness-completeness my discipline requires for ANY high-stakes chain-grade, applied consistently. Small cycle; clean CERT 588 on close. Per-query-fails stays the honest limit.

## Standing
- **Exp-Dev:** export fixed_e raw to per_unit (the one blocker). Also still queued: pythia re-VET, phase4b reframe, LEVER 1.5 v2 MM atomize, LEVER 2/3/4 cells.
- **Testbed:** raw-witness on the reads-state once exported -> Layer-2 complete on the chain-grade-maker.
- **Orchestrator:** Layer-3 reciprocal queued for the CERT 588 atomization (post raw-witness).
- **Research:** refuse-gate #5 (b) chain-grade HELD for the reads-state raw-witness; Milestone-1 refuse input is eligible-pending-this.
- **Me:** holding CERT 588 for the raw-witness. `fleet_waiting_on.md` updated. Silent-processing non-actionable events now (per USER token-reduction).

-- Skunkworks (cert-owner)
