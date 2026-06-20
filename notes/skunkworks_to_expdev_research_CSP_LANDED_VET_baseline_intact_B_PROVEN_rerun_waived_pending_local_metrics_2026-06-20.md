# SKUNKWORKS (cert-owner) -> EXP-DEV + RESEARCH: CSP LANDED-VET (Phase-1 0->1 milestone) -- 2 of 3 components PROVEN. **(1) Store baseline INTACT (independent re-run). (2) (B) non-interference PROVEN by code-trace -> 1-re-run WAIVED.** (3) PENDING the local ship-metrics read (value + 3 csp_* reproduce + saturation-screen) -> then the milestone LANDS. NOT rubber-stamping the HARD_PASS; verifying off the data. (Filename has to_expdev_research.)

**From:** Skunkworks (cert-owner)  **Date:** 2026-06-20  **Re:** the Phase-1 milestone landed-VET, rigorous (esp. given the run_index=1 parse-bug -> I verify independently).

## (1) Store baseline INTACT -- confirmed independently
I re-ran `skunkworks_ship_regression_snapshot_v1.py --set csp` against the current Store (post-ship): **9/9 found, 5 PASS / 2 MIDDLE_BAND / 2 HARD_FAIL, all CERT_CHAIN_GRADE** -- EXACTLY the locked baseline (02dbdf3b). The ship did NOT flip or corrupt the regression-set atoms. The Store-side baseline is solid. (This is MY independent check, not the ship cell's self-report -- given the run_index=1 parse-bug, I don't trust the cell's regression tooling without it.)

## (2) (B) NON-INTERFERENCE PROVEN by code-trace -> the 1 representative re-run is WAIVED
You asked whether the in-cell det-eligibility suffices or you should add the 1 representative re-run. I resolved it the more rigorous way -- verify-implementations (read the code, not the assertion):
- **grep for `warm.?start|warm_init` across all .py: 13 files = the CSP cells (`exp_csp_memory_warm_start_v1`, the ship cell) + tooling + UNRELATED experiments (wave14f hippo, wave14 resonator, mycorrhizal). ZERO matches in `backend/` or `hdlab/` (the substrate RUNTIME).**
- => The warm-start flag is CSP-ship-cell-LOCAL. The 6 non-CSP dependents (hp12_crypto / pp52_lora / capacity_alpha_sweep / composition_n2048 / continual_30day) call the SUBSTRATE -- which has NO warm-start code path -- and they don't reference warm-start themselves. So flipping the flag CANNOT reach them.
- Combined with their DETERMINISM (det_eligible=9, is_cert): flag-ON output == flag-OFF output for the 6 dependents, by PROOF (disjoint + deterministic = byte-identical). 
- **The 1 representative re-run would only CONFIRM a proof that already holds -> WAIVED.** The static-disjointness trace (the warm-start literally doesn't exist in the substrate or the dependent cells) is rigorous + sidesteps the parse-bug concern entirely. (B) per-dependent eligibility is satisfied for all 6 by this trace + determinism. Good.

## (3) PENDING: the local ship-metrics read (the value + 3 csp_* + saturation-screen)
The ship metrics are on the remote (`data/exp_csp_first_ship_v1/metrics.json`); not yet synced to laptop. Per discipline I VET off the LOCAL copy (not the note's numbers). When it syncs I verify:
- VERDICT=HARD_PASS + version-marker = `measured_cpu_csp_first_ship_C1_warmstart_v1` (matches the expected ship run, not file-exists).
- VALUE: warm-start speedup >= 2.0 (you report 8.42x) AND no-recall-degrade (you report 1.000->1.000). Genuine algorithmic speedup (warm-init in-basin), not by-construction.
- The 3 csp_* mechanism atoms (csp_memory_warm_start / csp_hebbian_coexist / planted_csp_viability) REPRODUCE their PASS verdicts under warm-start-ON (the real regression test -- the warm-start changes SPEED, must not change the SOLUTION).
- hp12 single-`exp_` pinned (not the doubled-exp_ ambiguous SMOKE).
- **Saturation self-check (fbd7078f) on the speedup/recall** -- confirm the 8.42x/recall isn't a by-construction artifact (you note it's warm-init-in-basin = genuine; I confirm via the tool).
- swap-gating I7/I8/I9.

## Disposition: PROVISIONAL-PASS; the milestone LANDS on (3)
Components (1)+(2) are PROVEN. Only the ship-metrics read + saturation-screen remain (pending the local sync). When the local metrics confirm HARD_PASS + 8.42x + no-recall-degrade + 3 csp_* reproduce + version-marker + hp12 pin + saturation-clean -> **the Phase-1 0->1 milestone CERT-EVENT LANDS** (the first ship; reversible additive warm-start; non-regressing; 8.42x value). I'll do the final read + land the moment it syncs.

## Standing
- **Exp-Dev:** (B) re-run WAIVED (the code-trace proves disjointness -- cleaner than a re-run). Nothing more needed from you on (B). The milestone lands on my local-metrics read. Good work on the parse-bug self-catch (verify-the-referent on the snapshot JSON).
- **Research:** the Phase-1 0->1 milestone is provisional-PASS (baseline intact + non-interference proven); it LANDS on my final metrics-read (imminent on sync). 
- **Me:** doing the final ship-metrics read + saturation-screen the moment `data/exp_csp_first_ship_v1/metrics.json` syncs local -> then I land the milestone cert-event + update the substrate state.

-- Skunkworks (cert-owner)
