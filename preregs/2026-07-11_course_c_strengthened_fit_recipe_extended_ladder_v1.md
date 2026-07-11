# Pre-reg: course_c_strengthened_fit_recipe_extended_ladder_v1

Date: 2026-07-11. Author: exp_dev. Branch: Branch-3 (LADDER_FIT_LIMITED) of
notes/research_decisive_rerun_decision_tree_oracle_capacity_ladder_2026-07-11.md.
Cell: experiments/exp_course_c_strengthened_fit_recipe_extended_ladder_v1.py

## Question
The oracle-capacity-ladder landed LADDER_FIT_LIMITED: the transductive ORACLE did not fire at any of 6 rungs,
and it is FIT-limited not readout-limited -- the DIRECT-DISTANCE readout CLIMBS with capacity
(L0 h@10=0.140 -> L5 anchor1 k32/dim8192 h@10=0.424 MEASURED@data/exp_course_c_oracle_capacity_ladder_v1/
metrics.json:ladder[5].oracle_direct_h10) while the FPE bounded-kernel readout stays flat ~0.03 (exactly 0.000
on the anchor1 rungs). Push the cheapest high-leverage FIT levers to move the DIRECT-readout transductive
ORACLE toward firing (hits@10 -> 0.90), reading out with DIRECT-DISTANCE (the FPE kernel is the wrong readout
here). Simultaneously diagnose the FPE exact-0.000 as a cheap parallel check (coordinator flag).

## Escalation levers (ranked; Branch-3 KGE-convergence lit-scan)
1. EPOCHS / dataset-passes (TOP lever): RotatE ~376-472 passes on a comparable graph vs our L5 top of 150.
2. LEARNING-RATE mismatch: A1_LR=0.05 (Adam) is ~1000x RotatE's published ~5e-5. Ladder evidence localizes it:
   on anchor1 epochs 60->150 barely moved direct (L3=0.362 -> L4=0.372, +0.010) while k 24->32 moved it
   (+0.052) -- consistent with LR-too-high so more steps cannot REFINE. Fixing LR is what lets epochs matter.
3. COORD capacity k: demonstrably the strongest single lever the ladder tested (L4 k24 -> L5 k32: +0.052).
n_neg is DEMOTED (lit-scan diminishing-returns evidence) and NOT swept -- held at 64.

## Extended ladder (isolates levers for weak-point localization)
All anchor1, minibatch=8192, reciprocal=True, transductive, seed=7, dim=8192 (FPE diagnostic only):
| rung | k | epochs | lr | n_neg | isolates |
|---|---|---|---|---|---|
| E0_repro_L5   | 32 | 150 | 0.05 | 64 | Gate-D positive control (reproduce L5 direct=0.424) |
| E1_ep450_hiLR | 32 | 450 | 0.05 | 64 | epochs lever AT high LR (predicts ~no gain) |
| E2_lrfix_ep450| 32 | 450 | 5e-3 | 64 | LR-fix at ep450 (E2 vs E1 isolates LR) |
| E3_kcap_ep300 | 48 | 300 | 5e-3 | 64 | + coord capacity on fixed LR |
Plus RANDOM untrained must-fail control (metric-can-move / not structurally frozen).

## Readouts (dual, kept every rung per contract)
- oracle_direct_h10: DIRECT-DISTANCE -||x_hat - X_c|| on standardized coords. PRIMARY; the oracle-fire GATE.
- oracle_fpe_h10: FPE at pre-registered ell=0.55 (intended geometric readout; diagnostic).
- oracle_fpe_medht_h10: FPE READOUT-FIX lever = median-heuristic bandwidth on this rung's standardized coords.
  Cheap parallel check of the coordinator FPE-exact-0.000 flag (the underflow diagnosis: ell=0.55 << typical
  standardized pairwise distance ~sqrt(2k)~7-8 => kernel underflows to constant => degenerate ranking).
- fpe_prereg_health / fpe_medht_health: score std + range (near-0 std = degenerate/structural, not capacity).

## HARD-PASS / HARD-FAIL bands (lifted from Branch-3; not invented here)
- HARD-PASS (fit closed; licenses the Branch-1 decisive re-run): some rung gets oracle_direct >= 0.90 within
  <= 4x the L5 rung's elapsed (per-rung budget ~5317s). oracle_fpe (+medht) re-checked at that rung.
  Verdict = EXTENDED_LADDER_FIT_FIRES.
- HARD-FAIL / ESCALATION TRIGGER (MANDATORY explicit): best oracle_direct < 0.90 AND core dense (avgdeg>=30,
  measured ~39.7 -> 'not enough data' ruled out) -> escalate to strategy with the functional-form /
  representational-capacity framing; do NOT keep sweeping recipe knobs. Verdict =
  EXTENDED_LADDER_FIT_LIMITED_ESCALATE_STRATEGY. UN-CONFOUNDED by the FPE readout: the FPE bug is diagnosed +
  the median-heuristic-recalibrated FPE reported, so an escalate verdict means the WORKING direct readout still
  does not fire = a genuine fit/representation wall, not a masked readout bug.
- MIDDLE (honest, not auto-license infinite cranking): best oracle_direct < 0.90 but still climbing
  monotonically with capacity (top escalated rung is best AND improved >= PLATEAU_EPS=0.03 on the prior).
  Verdict = EXTENDED_LADDER_FIT_CLIMBING_UNDER_BUDGET -- flags the trajectory to strategy for the call
  (one more capacity rung vs representation change); does NOT silently keep escalating capacity.

## Integrity gates (take precedence over the fire/escalate verdict)
- Gate-D positive control (META_RULE reproduce-prior-at-test-regime): E0_repro_L5 (config identical to ladder
  L5) must reproduce oracle_direct h@10 = 0.424 within tol 0.10, else HARD_FAIL_REGIME_OR_INVOCATION_MISMATCH
  (downstream rungs suspect). cited_prior=MEASURED@data/exp_course_c_oracle_capacity_ladder_v1/metrics.json.
- Must-fail control: RANDOM untrained coords oracle_direct h@10 must stay < 0.05 (chance ~0.0004), else
  HARD_FAIL_CONTROL_METRIC_BROKEN (readout leaking / metric frozen-high; nothing trustworthy).

## Weak-point localization
- Degree-stratified direct readout per rung (LOW/MID/HIGH gold-tail-degree tertile) -> localizes WHERE the fit
  breaks (do high-degree tails memorize while low-degree fail, or uniform).
- lever_attribution: fit_escalation_direct_gain (epochs+LR+k on direct) vs readout_fix_fpe_gain (bandwidth fix
  on FPE) -> reports WHICH lever moved the oracle (coordinator point 4).
- fpe_diagnosis: FPE_BANDWIDTH_BUG_CONFIRMED (median-heuristic recovers FPE to ~direct = cheap config bug) |
  FPE_STRUCTURAL_DEEPER_USE_DIRECT | FPE_OK.

## SCHEMA-VET fields
- cardinality_ok: true. EXPECTED_N_UNITS = 4 ladder rungs + 1 random control = 5 (single seed by design).
- discriminating_fraction: n/a-single-mechanism-ladder. The direct readout is in-band and MOVES (RANDOM~0.0004
  floor -> fit 0.14-0.42; must reach 0.90 to fire) -- not saturated, not structurally frozen (RANDOM control
  proves movement). baseline_in_band: the ORACLE direct arm is 0.14-0.42 (0.05 < x < 0.95); RANDOM is the
  intentional must-fail floor (arms_differ_exempted: RANDOM is a chance control, not the mechanism baseline).
- arms_differ_verified: true by construction (each rung a distinct fit config; RANDOM is untrained; direct vs
  fpe vs fpe_medht are distinct readouts). arms_differ_exempted: [(E0, ladder-L5) intentionally identical --
  E0 IS the reproduce control].
- final_metrics_atomicity: tmp_replace (write_metrics + os.replace; crash path os.replace).
- except SystemExit: raise BEFORE except Exception (verified; no BaseException / no bare except in work loops).
- crlb_n/a: "transductive memorization CAPACITY probe, not a Gaussian estimation-noise floor. Feasibility of
  the 0.90 bar: filtered hits@10 masks OTHER true tails of the same (h,r) out of the ranking, so a strong
  transductive fit CAN reach >=0.90 even on many-to-many relations; the direct readout already climbs
  0.14->0.424 monotone with capacity, demonstrating headroom + movement." discriminator_reachability: true.
- baseline_in_band: true (ORACLE direct 0.14-0.42). calibration_check: default_ok_for_this_regime (ell=0.55
  is the pre-registered bandwidth; the median-heuristic recalibration is an ADDITIVE diagnostic lever with its
  own discriminator, not a tuning of the primary direct gate).
- cell_chunked: false (single seed; single CSKG assembly reused across rungs -> memory FLAT; no cross-seed
  accumulation; the multi-seed-OOM driver is absent by construction). start_marker_written: true.
  crash_diagnostic_present: true. heartbeat_present: true (per-rung _heartbeat.jsonl). defensive_error_checking:
  passed_all_4_patterns.
- progress_logging: print_flush_true (line-buffered stdout + per-rung/per-readout flush). Required because
  timeout_s >= 1800.
- run_mode default = full (runner runs FULL; §16). Self-test is a separate branch (--self-test / --run-mode
  self_test): tiny synthetic functional graph, NO CSKG, seconds, exits 0/1, does NOT trigger the full run.
- effective_vs_nominal: swept params (epochs, lr, k) are experienced DIRECTLY by the single anchor1 fit
  primitive (no partition routing); sweep_alignment_verdict: ALIGNED.
- positive_control_arms: E0_repro_L5 (Gate-D) reproduces the ladder L5 at the identical test regime.
- functional_requirements: (a) transductive memorization of held-out edges -> anchor1 CE self-adversarial fit;
  (b) recover gold from coords -> direct-distance + FPE-kernel readouts; (c) localize break -> degree strata.

## Compute architecture
class (c) MIXED. CSKG assembly + degree map = symbolic (sequential-CPU correct). Coord fit = minibatch SGD
(vectorized torch); readout = query-chunked matmul. SINGLE seed, SINGLE CSKG assembly reused across rungs ->
memory FLAT. device=cpu on remote_cpu_queue: CPU is memory-UNBOUNDED so the deliberate epoch-escalation carries
ZERO OOM-kill risk on the reasoning-critical path (a GPU OOM mid-rung would delay the decisive re-run MORE than
CPU's slower wall). Matches the ladder's proven-safe routing (6 rungs in 5414s on remote_cpu_queue). The fit is
vectorized torch either way (not a numpy Python-loop) so the GPU-batching mandate's core concern does not apply.
Storage strategy: no_storage (KGE coordinate fit, not an associative store). LOCAL = NEVER (no-local-smokes
lock; remote --self-test is the ship gate).

## Routing + timeout
- Queue: remote_cpu_queue (device=cpu; SCP-based dispatch, no origin push needed).
- Timeout: 21600s (6h). Justification for exceeding the 14400s soft-cap: 4 full transductive KGE fits at
  300-450 epochs over 460k edges (920k with reciprocal) at batch 8192, scaled from the ladder's MEASURED L5
  (ep150 = 1329.3s, ~linear in epochs): E0~1330 + E1~4000 + E2~4000 + E3~4000 + RANDOM~30 + FPE-diagnostic
  (median-heuristic readout per rung) ~800 + CSKG assembly ~ ladder-overhead ~= 14.2ks compute; 1.5x safety
  margin for CPU variance -> 21.3ks -> 21600s. Each rung is held <= 4x L5 elapsed (~5317s) per the Branch-3
  per-rung budget (within_budget flag reported). The >14400 cap is justified by the deliberate epoch-escalation
  (the #1 lever) on the reasoning-critical path; cannot be cheaper without defeating the test.

## Ship gate
Remote --self-test on marsh@home .venv (tiny synthetic functional graph; exercises _fit_anchor1(lr/nneg) +
direct + FPE(ell=0.55) + FPE(median-heuristic) + per-stratum + RANDOM control code paths; exits 0 on
SELFTEST_PASS). No local execution (no-local-smokes lock).
