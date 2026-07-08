# Pre-registration: glass_box_micro_loop_conceptnet_multihop_SCALE_v1

Date: 2026-07-08
Author: exp_dev (Opus 4.8 1M, agent-spawn)
Cell: experiments/exp_glass_box_micro_loop_conceptnet_multihop_SCALE_v1.py
Extends (CG certified): experiments/exp_glass_box_micro_loop_conceptnet_multihop_v1.py (commit 200b66c3f)
Reuses (mechanism-level, not re-run): experiments/exp_reasoning_chain_replay_v1.py (Merkle helpers transcribed)

## Deep-prize question
Does NON-CEILING multi-hop reasoning AND the glass-box self-audit (retrieve->gate->audit->requery with
Merkle replay + tamper-detect + causal hand-edit) HOLD when the certified toy-real loop (V~580) must
disambiguate the answer among 10-80x more REAL ingested ConceptNet entities? This is the direct line to the
locked deep prize: substrate reasoning OVER ingested knowledge, glass-box, self-auditing, AT SCALE.

## Scaling design
- SCALING AXIS = V = codebook entity count = number of distinct REAL ConceptNet nodes the per-hop cleanup
  must resolve the true answer AMONG. This is the "entity count" of the deep prize. The single-cue bundle
  capacity law M < N/(2 ln V) has V (codebook) as the disambiguation term -- growing V is the physics-
  relevant "reason over a bigger KB" stressor.
- V grid: {600, 6000, 24000, 48000} = ~{1x, 10x, 40x, 80x} over the certified base V~580. V=600 is an
  exact-machinery replica (positive control for "same loop, tiny KB").
- STORE HELD FIXED across the grid: n_hard=n_easy=120, M_SYN=120 edges, M_ISA=240 edges (bit-identical to
  the certified base operating point). Per-hop REASONING difficulty is therefore constant; the SOLE thing
  that scales is codebook crosstalk. Any degradation is cleanly attributable to entity-count scale.
- The extra (V - corpus_nodes) codebook entries are REAL ConceptNet node names drawn from the graph node
  set (confusable cleanup decoys), so every codebook entry is real ingested structure.
- N SCHEDULE: N held at 8192 across the ENTIRE grid. The single-cue bundle wall N/(2 ln V) recedes only
  LOGARITHMICALLY with V, so N=8192 stays off the wall through V=48000 (wall=380 > M=240, 63% of wall,
  oracle=0.929 MEASURED). Raising N over-provisions the fixed small store: the non-ceiling difficulty is
  set by gate-routing error on the real hard-margin distribution ((top1-top2)/N), and doubling N sharpens
  the margin so accB SATURATES > 0.95 (MEASURED: the N=16384 variant trips SATURATION_TOO_EASY). Holding
  N=8192 keeps accB non-ceiling and tests whether it HOLDS at 80x.

## Documented HONEST LIMIT (becomes the next drill)
CO-scaling the bundled store (M proportional to V) would require N ~ M ln V -- QUADRATIC in entity count
(codebook memory ~ V*N ~ V^2 ln V), infeasible past V~5-8k on any single machine. This is the known bundle
bound; the established fix is SHARDED storage (reference_sharded_fhrr_cleanup_capacity_beyond_bundle_bound;
+13.9x, holds at L=20+). This cell tests the codebook-scale axis (feasible to 80x) and NAMES the bundled-
store quadratic wall as the reason store co-scaling is deferred to a sharded follow-up.

## peel/SIC readout
NOT APPLICABLE and deliberately NOT used. Every readout is a single-cue top1 lookup (unbind one relation,
cleanup argmax). Established (exp_encoder_peel_sic_readout_realcodes_v1): peel/SIC helps ONLY where the loop
bundles MULTIPLE items; it does not benefit single-cue top1. A future multi-bridge fan-out variant is where
peel/SIC would apply.

## Arms (HP_SCOPE)
- ARM_A_SINGLE_SHOT (baseline): always commit the single shot. accA ~ frac_easy = 0.5 (in-band). No HP gate.
- ARM_B_WM_REQUERY (mechanism): gated (marginA >= tau => Go else WM-mediated re-query). Carries all HP gates.
- ARM_B_SCRAMBLE (telemetry control): re-query with a RANDOM bridge. Must collapse (scramble_gap gate).
- ARM_ALWAYS_REQUERY (control): always re-query. Breaks EASY (gate_route_margin gate).
- ARM_ORACLE_BRIDGE (positive control): TRUE bridge into ISA. Carries only the >=0.85 retrieval rail.
HP gates (resolve_lift / scramble_gap / routing / non-ceiling / discriminator / causal_flip) apply to ARM_B
vs {ARM_A, ARM_ALWAYS, ARM_B_SCRAMBLE}. Exempted arm-pair (bit-identical allowed): ARM_ALWAYS vs ARM_ORACLE
on EASY (both undefined-bridge fallbacks).

## Pre-registered bands (gates evaluated PER SCALE; HARD_PASS = top-scale headline + all-scale integrity)
- HARD_PASS: at the TOP scale (V=48000) resolve_lift(accB-accA) >= 0.25 AND accB-accALWAYS >= 0.15 AND
  paired sign-test p < 0.05 AND accB <= 0.95 (NON-CEILING) AND accA_hard <= 0.15 (discriminator fires) AND
  gate_separation >= 0.10 AND gate_routing_acc >= 0.85 AND scramble_gap >= 0.25 AND causal_edit_flip >= 0.80
  AND arms_differ; AND at EVERY scale oracle_bridge_acc >= 0.85 AND hop1_retrieve_acc >= 0.80 AND
  deterministic_replay == 1.0 AND merkle_verify == 1.0 AND tamper_detect == 1.0 AND accA_hard <= 0.15 AND
  accB <= 0.95 AND resolve_lift >= 0.25.
- SCALE_WALL: loop + audit HOLD at small V but DEGRADE with scale (some larger-V tier drops resolve_lift
  < 0.25, or oracle < 0.85, or accB > 0.95). HONEST high-value finding -> names the exact wall.
- MIDDLE_BAND: integrity holds at all scales but a top-scale headline gate lands in a middle band.
- HARD_FAIL: any scale resolve_lift < 0.10 OR tamper_detect < 1.0 OR deterministic_replay < 1.0.
- INCONCLUSIVE_{DISCRIMINATOR_DEAD, TAUTOLOGICAL_METRIC}: per-scale accA_hard > 0.15 / scramble_gap < 0.10.

## SCHEMA-VET mandatory fields
- cardinality_ok: EXPECTED_N_UNITS = len(SCALES) * len(SEEDS) = 4 * 5 = 20 (FULL); verdict counts completed.
- final_metrics_atomicity: tmp_replace (os.replace) + per-(scale,seed) partial checkpoint (PROT-021 resume).
- cell_chunked: false (single cell; per-(scale,seed) partial checkpointing via write_partial_key, so a
  kill/resume loses at most one unit; total FULL ~160s so single-cell is safe).
- start_marker_written: true. crash_diagnostic_present: true (except Exception -> CELL_CRASHED + traceback).
- heartbeat_present: true (per-unit _heartbeat.jsonl). defensive_error_checking: passed_all_4_patterns.
- arms_differ_verified: true (SHA256 of per-arm answer arrays; A/B/SCRAMBLE/ALWAYS diverge at smoke).
- crlb_n/a: accuracy-gap discriminator; no single closed-form noise floor. Reachability by bundle-SNR
  feasibility (N=8192/M=240 at 63% of wall at V48000, SNR=5.84); oracle positive control reachable (0.929).
- discriminator_reachability: true (oracle >= 0.85 and accA_hard <= 0.15 both reachable at every V, MEASURED).
- baseline_in_band: true (ARM_A on the MIXED corpus accA ~ 0.5, strictly in (0.05, 0.95)).
- baseline_saturated: false (max accB across grid = 0.923 < 0.95).
- discriminator survives scale (option A): SMOKE runs the SAME V grid + SAME N + SAME store as FULL; the
  must-fail control (single-shot on HARD) is asserted to FAIL at EVERY V incl. the top V=48000 via
  assert_discriminator_fires; oracle asserted >= 0.85 and scramble collapse asserted per-scale in smoke.
- calibration_check: default_ok_for_this_regime -- TAU_GATE=0.11 (same as certified base; scale-robust
  because M is held fixed so the easy/hard margin distributions do not move with V). NOT tuned per-seed/scale.
- HP strictly above floor (META_RULE_L): top-scale resolve_lift=0.394 (floor 0.25, +0.144), gate_sep=0.266
  (floor 0.10), oracle_min=0.929 (floor 0.85); all well above floor + 5% band-width.
- generator guard: every hard chain verified X-syn->A-isa->B with B not in isa[X] (well-posed 2-hop); every
  codebook entry verified a real graph node; distinct hard anchors asserted.
- progress_logging: print_flush_true (line-buffered stdout + flush per progress line) + per-unit heartbeat.

## §15 composition/sweep gates
- effective_vs_nominal_parameter_audit: swept V is the codebook size directly experienced by every cleanup
  (the argmax is over V candidates). sweep_alignment_verdict: ALIGNED.
- bracket_includes_discriminating_band: MEASURED smoke accB per scale {0.919, 0.923, 0.871, 0.871} -- all in
  the discriminating band [0.30, 0.95] and none saturated; discriminating_fraction = 4/4 = 1.0 (>= 0.30).
- signal_shape_compatibility_audit: hop1 WM active-slot content (a node code) -> hop2 bind into ISA store;
  SHAPE_MATCH (both are N-dim bipolar codes). No adapter needed.
- positive_control_arms: ARM_ORACLE_BRIDGE reproduces the single-cue ISA retrieval at EACH test regime
  (MEASURED oracle 0.929-0.996 across scales, >= 0.85 floor). Regime-extension audit: SHAPE_MATCH (same
  bipolar-code substrate as the certified base; only V and codebook decoys change).
- functional_requirements: (1) retrieve bridge into WM -> hop1 cleanup; (2) decide commit-vs-requery ->
  margin gate; (3) compose two hops -> WM re-binding; (4) audit every step -> Merkle chain + tamper; (5)
  monitor-not-control -> causal hand-edit recompute. Each maps to a certified primitive reused verbatim.

## Compute architecture
(c) mixed with justification. Sequential across hops (hop-2 depends on hop-1 WM); per-trial Merkle/tamper/
causal audit is scalar CPU. The codebook cleanup matvecs (the cost that scales with V) are STAGE-BATCHED
into single BLAS gemms across all trials (E @ Probes.T), so V=48000 is CPU-feasible. No torch/GPU: the
certified base is numpy-only and total FULL work is ~13 TFLOP (BLAS multi-threaded), well under the hours-
scale threshold the GPU-batching mandate targets. Storage: mixed -- bundled single-hop stores (exemption a:
single-hop read within a hop), sharded cross-hop via WM re-binding.

## Dispatch
- queue: remote_cpu_queue (FULL runs go remote per USER-LOCKED smoke-only-local; CPU-BLAS, no GPU dep).
- timeout_s: 5400 (matrix_sweep floor via tools/exp_guard.py; true FULL wall ~160s, floor is a safety cap).
- SMOKE (this preflight): 2 seeds x 4 scales, 64s local wall, HARD_PASS, all 14 structured gates True,
  discriminator fires at every scale (accA_hard=0.000, oracle>=0.929, scramble_gap>=0.438).
- FULL: 5 seeds x 4 scales (EXPECTED_N_UNITS = 20).

## Smoke result (MEASURED@data/exp_glass_box_micro_loop_conceptnet_multihop_SCALE_v1_smoke/metrics.json)
Verdict HARD_PASS (2 seeds). Per-scale: V=600 accB=0.919 resolve=0.423 oracle=0.996; V=6000 accB=0.923
resolve=0.438 oracle=0.979; V=24000 accB=0.871 resolve=0.392 oracle=0.950; V=48000 accB=0.871 resolve=0.394
oracle=0.929. accA_hard=0.000 and det/merkle/tamper=1.0 and causal_flip=1.0 at every scale.
