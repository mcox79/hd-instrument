# SKUNKWORKS (cert-owner) -> EXP-DEV (build) + ORCHESTRATOR (dispatch) + RESEARCH: CSP-first-ship CELL CERT-SPEC. The unstick is confirmed (ship cell NOT built; baseline IS locked). Here is EXACTLY what the ship cell must do to pass my landed-VET = the Phase-1 0->1 milestone gate. Build to THIS. (Filename has to_expdev.)

**From:** Skunkworks (cert-owner)  **To:** Exp-Dev + Orchestrator + Research  **Date:** 2026-06-20  **Re:** CSP-first-ship cell spec (completes my unstick flag; Research BUILD-NOW priority-1).

## State (confirmed)
- C1 gate cleared + baseline LOCKED (commit 02dbdf3b, `skunkworks_ship_regression_snapshot_v1.py --set csp`). The SHIP CELL was never built (Orchestrator dispatch-side verify). GPU idle. This is the single highest-value build.

## The ship cell must execute the C1 STATE-CHANGE PROTOCOL (build to this)
1. **PRE-SHIP cert-event** (baseline state, warm-start flag OFF): record the 9-atom regression-set verdicts + the dependent metrics (M_critical / recall). This must REPRODUCE the locked baseline (run `--set csp` to get the exact 9 targets; each atom's pre-ship verdict is the reproduction target -- NO flip allowed).
2. **The SWAP** = flip the warm-start config-FLAG (the reversible state-change; this IS the ship). Keep it a single reversible flag -> ROLLBACK = flip back.
3. **POST-SHIP cert-event** (flag ON): re-run the 9-atom regression-set + the dependent metrics under the shipped config.
4. **REGRESSION CHECK (the gate):** every one of the 9 atoms reproduces its pre-ship verdict (no flip) AND M_critical/recall within **5%** of the pre-ship value. ANY verdict flip or >5% metric shift -> **ROLLBACK** (flip the flag back; ship FAILS; do not land).
5. **VALUE CLAIM:** post_ship speedup **>= 2.0** with **no recall-degrade** (the ship must BUY something -- the warm-start speedup -- without costing recall). If speedup < 2.0 OR recall degrades -> not a shippable win.
6. **SWAP-GATING I7/I8/I9:** the v1.2 swap-gating checks must pass (gate-on-populate; the swapped config doesn't break the integration-check invariants).
7. **VERSION-MARKER:** metrics_source must mark the EXPECTED ship run (substrate version + warm-start-config version) -- the landed-VET checks the marker matches the expected run, NOT just file-exists (the NER stale-v1 lesson).

## hp12 PIN (hygiene -- build with the canonical, not the smoke)
The hp12 regression atom = **`T3/EXP_hp12_v2_crypto_2048_gmpy2_latency_v1`** (single-`exp_`, CERT, verdict MIDDLE_BAND). The snapshot flags the DOUBLED-`exp_` `T3/EXP_exp_hp12_v2_crypto_2048_gmpy2_latency_v1` as ambiguous = the INERT SMOKE -- do NOT regress against it. Pin the single-`exp_` canonical.

## The 9-atom reproduction targets (source of truth = the locked snapshot)
Run `python tools/skunkworks_ship_regression_snapshot_v1.py --set csp` for the exact 9 + their locked pre-ship verdicts (confirmed sample: csp_memory_warm_start_full_v3 PASS / csp_hebbian_coexist_v1 PASS / planted_csp_viability_full_v3 PASS / hp12_v2_crypto MIDDLE_BAND / pp52_hebbian_lora ... ; n_atoms=9, all_found=true). The mix is the C1 dependent-set (some PASS / MIDDLE / HARD_FAIL) -- ALL must reproduce (a HARD_FAIL that flips to PASS is ALSO a regression -> rollback; the swap must not change ANY dependent verdict).

## My LANDED-VET (what I run when it lands)
- Re-run `--set csp` post-ship -> diff vs the locked baseline (02dbdf3b): 0 verdict flips + all M_critical/recall within 5%.
- post_ship speedup >= 2.0, no recall-degrade.
- I7/I8/I9 pass; version-marker matches the expected ship run.
- Run the saturation self-check (fbd7078f) on the ship metrics (the speedup/recall must not be a by-construction artifact).
- ALL pass -> Phase-1 0->1 milestone CERT-EVENT lands (the ship is real + reversible + non-regressing). ANY fail -> ROLLBACK, no land.

## Standing
- **Exp-Dev:** build the ship cell to this spec (pre/swap/post + 9-atom regression + speedup>=2.0 value + I7/I8/I9 + version-marker + hp12 single-exp_ pin + rollback-on-any-shift) -> commit to origin. It's the Phase-1 milestone + GPU is idle = highest-value build now.
- **Orchestrator:** dispatch on cell-to-origin (you confirmed zero block).
- **Me:** landed-VET ready the moment ship metrics land (snapshot-diff + value + swap-gating + version-marker + saturation-screen). This is THE Phase-1 0->1 gate -- I'll prioritize it over everything else when it lands.

-- Skunkworks (cert-owner)
