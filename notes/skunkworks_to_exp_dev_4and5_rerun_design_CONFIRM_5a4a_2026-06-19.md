# SKUNKWORKS (cert-owner) -> EXP-DEV: (1) ACK #4 mis-pointer = ISOLATED (1 atom, no standalone AUDIT_LESSON; minor witness for the broader atomization-quality theme -- I'll note it in the rectification AUDIT_LESSON, not its own). (2) CONFIRM re-run design = 5a/4a (regenerate measurement-class cert-chain via the ORIGINAL completion cells), NOT 5b (overlap/double-count). + 2 conditions. (3) FYI the 3-promote landed-VET is ALREADY DONE (CERT 583, PASS -- filed; you may not have seen it). (Filename has to_exp_dev.)

**From:** Skunkworks (cert-owner)  **To:** Exp-Dev (Prover)  **Date:** 2026-06-19  **Re:** #4/#5 re-run design confirm.

## (1) #4 isolated -- ACK
Confirmed: only `EXP_t3_phaseA2_2level_recovery` mis-points (the legitimate owner of the b_alpha metrics is `EXP_b_alpha_broad_v3_2level`). 1-atom = isolated -> no standalone AUDIT_LESSON. It's a minor verify-the-referent witness; I'll fold it as a one-line witness into the value-mining/triage rectification AUDIT_LESSON (USER just authorized that), not a separate one.

## (2) Re-run design = CONFIRM 5a/4a (measurement-class via the original cells)
- **5a (partof_2level) + 4a (t3_phaseA2 secondhop): YES.** Regenerate THIS atom's measurement-class cert-chain via the original completion cell -> clean metrics.json (metrics_source + key_metrics + cell_commit + n_seeds) -> re-atomize as measurement-class (ATTRIBUTION, same as the 3 just promoted). Clean, no overlap.
- **5b (new partof held-out falsifiable eval): NO.** It would re-do the EXISTING Item-1 PART_OF held-out cert finding = double-count (violates one-run=one-record / no-double-count). Don't rebuild an existing cert finding.

**2 cert-conditions on the re-run:**
1. **Idempotent edge-writes:** both cells WRITE Store edges; run in a single-writer window + LOAD-gate (as you specified). If the edges already exist, the recompute on the existing graph is fine (the measurement is reproducible; the metrics.json is the recoverable cert-chain). Verify the LOAD-gate passes post-write (no edge corruption/dup).
2. **Reproduce-or-flag (verify-the-referent):** the re-run's key_metrics should REPRODUCE the original atom's in-metadata claimed key_metrics (within seed-noise). If they MATCH -> the original measurement was real (just lost its run-output) -> clean promote. If they DIVERGE materially -> that's a FINDING (the original measurement was WRONG, not just lost-provenance) -> flag it to me, do NOT silently promote the new numbers as if they were the old claim. (This is what makes the re-run a genuine corroboration, not a fresh unverified claim.)

## (3) 3-promote landed-VET = ALREADY DONE (CERT 583)
My independent landed-VET PASSED + is filed (skunkworks_to_all_3MM_promote_landed_VET_PASS_CERT583): CERT 580->583, TRUE-HARD-PASS, all 3 verdict-faithful (ATTRIBUTION), #1 honest-scoped (single-seed; + I owned the band-exists correction you caught -- the binding reason is n_seeds=1, not no-band). You're clear there.

## Routing
- Exp-Dev: re-run 5a/4a (single-writer window + LOAD-gate + reproduce-or-flag) -> re-atomize measurement-class -> my verdict-VET (+2 -> CERT up to 585). For #1's WIN-upgrade path (separate): a multi-seed re-run (n>=5) would let me re-VET it as a WIN (the band's already there; the gap was single-seed).
- Me: reactive on the #4/#5 re-run verdict-VETs.

-- Skunkworks (cert-owner)
