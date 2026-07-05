# Pre-registration: exp_integration_full_stack_hard_regime_v1

**Anchor:** `integration_full_stack_hard_regime_v1`
**Cell:** `experiments/exp_integration_full_stack_hard_regime_v1.py`
**Author:** hdi_exp_dev (Opus 4.8 1M, agent-spawn), 2026-07-05
**Hand-off:** `notes/exp_dev_handoff_research_integration_full_stack_hard_regime_2026-07-05.md`
**Research note:** `notes/research_integration_full_stack_hard_regime_compose_2026-07-05.md`
**Queue tier:** CPU (no GPU). SMOKE local (done, gate cleared). FULL -> `remote_cpu_queue` (needs push; exp_dev cannot push).

## Question (USER direct, 5x-drill angle 3)

Are the substrate's brain components not just individually proven but INTEGRATED? Chain 4 real subsystems
(comprehend/role-type -> store+reason multi-hop -> control-gate goal -> generate) end-to-end at a HARD
regime and measure whether error COMPOUNDS across stages or stays near-INDEPENDENT, and whether REGENERATIVE
cleanup (snap-to-nearest-codeword at every seam, the "digital repeater") keeps errors near-independent while
raw ANALOG pass-through compounds to floor.

## Mechanism hypothesis under test

At the one hard seam already tested (`exp_integration_end_to_end_loop_bridge_HARD_v2`), regenerative cleanup
kept per-slot errors near-independent (0.939*0.861=0.808 ~= observed 0.806) while analog pass-through
compounded (0.467*0.228=0.106 ~= observed 0.10). Open (2/3 lit-scans found NO published benchmark of
chaining 3+ cleanup stages in series): does this survive a genuine 4-STAGE chain, or does a confident-wrong-
attractor cascade appear only once >=4 real subsystems are composed?

## Stages (reuse proven mechanisms; operating points verified off-disk INSIDE proven envelopes)

1. COMPREHEND (selectional-restriction role-typing). Role-bound perceptual scene under context-load
   superposition; unbind subject/object roles then TYPE by matched filter over DISJOINT vocab partitions.
   MEASURED@data/exp_comprehension_envelope_superposition_vocab_v1/metrics.json:grid.D6_V500.order_content_
   perrole_mean=1.0, parse_holds=True (proven mechanism; this cell's operating point is a HARD-regime
   realization of the same content-typing, declared SHAPE_DRIFT below).
2. STORE+REASON (multi-hop HRR, hub-crowded). HRR circular-conv bind/unbind (hdlab.binding) over real BGE,
   V=4096, hops=3, D_store=10, near-neighbour hub cluster. Reuses `exp_integration_end_to_end_loop_bridge_
   HARD_v2` hard regime.
3. CONTROL-GATE (goal-conditioned Go/NoGo WTA + abstain). reach=cos(cand @ M_hat, goal); M_hat ridge-fit on
   a small held-out pool; WTA over O + tightest cosine-neighbours; Go iff max reach > tau else abstain (miss).
   Proven gate fair operating point MEASURED@data/exp_pfc_gate_cfrpe_trained_v2/metrics.json:V1200_d4
   gonogo=0.653, oracle=0.962.
4. GENERATE (bipolar-BSC partition-restricted decode). Compose ordered triple, decode per slot. Reuses the
   HARD_v2 / generation-decoder roundtrip decoder.

## Arms

- REGEN (digital repeater): argmax-to-nearest-known-codeword snap at every seam.
- ANALOG (analog repeater): raw noisy inter-stage estimate through the SAME codec at every seam, NO snap.
- ORACLE_CHAIN (WIRING control; arms_differ-exempt vs regen): ground-truth at every seam + gate-pass forced
  -> pure decoder-wiring ceiling.
- BROKEN (discriminator): object identity severed at the reason hop (unbind by an unstored role path).

STAGE-ORACLE isolation (diagnostic): each stage run in isolation fed ground-truth input -> comprehend/reason/
gate/generate accuracy. product_of_stages = their product = naive-independence prediction.
compounding_ratio[arm] = full_chain_end2end[arm] / product_of_stages.

## Metrics (the decisive numbers)

- `full_chain_end2end[arm]` (exact-ordered triple == truth AND Go).
- `product_of_stages`, `compounding_ratio[arm]`.
- `wrong_attractor_rate` (self-calibrated: fraction of REGEN cleanup steps that are WRONG with margin >= the
  median CORRECT-commit margin), plus `cleanup_error_rate` and `confident_wrong_frac` (glass-box auditability).

## Pre-registered bands (envelope-expansion fail-bands; FULL-only canonical = remote)

- WIRING gate: `ORACLE_CHAIN end2end >= 0.80` (both regimes). Below -> machinery broken, not composition.
- BROKEN_CEIL: `BROKEN end2end <= 0.05` (chance obj acc = 1/V = 0.000244 THEORETICAL at hard V=4096).
- STAGE-in-band (META_RULE_AG): lossy stages `0.05 < comprehend,reason < 0.98`; gate in FAIR band
  `[0.35, 0.90]`; generate (decoder wiring) `>= 0.80`. Out-of-band -> INCONCLUSIVE_STAGE_OUT_OF_BAND.
- HARD_PASS (components integrate at 4-stage hard regime): `end2end[REGEN] >= 0.35` AND
  `compounding_ratio[REGEN] >= 0.70` AND `(REGEN - ANALOG) >= 0.20` AND `cv(REGEN) < 0.15`.
- HARD_FAIL (components do NOT integrate even with cleanup): `end2end[REGEN] < 0.25` AND
  `compounding_ratio[REGEN] < 0.50` (relay itself compounds worse than independence predicts -> next lever is
  a sustained cross-stage working-memory/thalamic buffer, not point cleanup).
- MIDDLE_BAND: partial integration (in-between).

## SMOKE preview (MEASURED@data/exp_integration_full_stack_hard_regime_v1/metrics.json, run_mode=smoke)

hard: end2end regen=0.625 analog=0.000 oracle_chain=1.000 broken=0.000; stage_acc C=0.82 R=0.90 G=0.88
Gen=1.00; product=0.643; compounding_ratio regen=0.974 analog=0.000; margin(regen-analog)=+0.625;
cv(regen)=0.000; wrong_attractor_rate=0.018 cleanup_error_rate=0.139 confident_wrong_frac=0.167. All gates
fire; FULL predicted HARD_PASS (P_deflated=0.45).

## Compute architecture

Class: (b) sequential-CPU with justification. Task-mandated CPU probe (no LLM, no GPU). Per-trial ops are
HRR FFT bind/unbind + matched-filter/decode argmaxes over V=4096 x N_G=8192 codebooks (numpy). The chain has
GENUINE sequential dependencies (each stage consumes the previous stage's output); trials are independent but
the per-trial cost is small (smoke 24x3x2 units ~19s wall). FULL 60x3x2 ~ 50s local; remote CPU generous
timeout 900s. No batching-GPU needed (wall << 10min).
Storage strategy: HRR per-trace role-bound superposition (each fact its own role-bound term; the trace is a
standard HRR bundle of role-bound facts, NOT a bundled item-store used for chained retrieval). The
composition under test is the CHAIN OF SUBSYSTEMS, not chained retrieval over a bundled store. Declared:
sharded-appropriate (per-fact role binding); no global bundled-item store.
progress_logging: line_buffered_stdout (sys.stdout.reconfigure line_buffering + print flush=True via _say +
per-seed heartbeat). timeout_s < 1800 so not mandatory, provided anyway.

## SCHEMA-VET fields

- cardinality_ok: True. EXPECTED_N_UNITS = n_seeds(3) x n_regimes(2) x n_arms(4) = 24.
- arms_differ_verified: True. MECHANISM arms {regen, analog, broken} inter-stage id streams hash-distinct
  per unit. arms_differ_exempted: [("regen","oracle_chain")] -- oracle_chain is the decoder-WIRING control
  and coincides EXACTLY with regen on trials where regen recovers ground truth (the machinery ceiling); they
  diverge at hard (regen < oracle) and that divergence is measured.
- final_metrics_atomicity: tmp_replace (metrics.json.tmp then os.replace).
- except ordering: `except SystemExit: raise` and `except KeyboardInterrupt: raise` BEFORE `except Exception`
  (no bare except, no BaseException; grep-verified).
- crlb / capacity-feasibility: crlb_n_a for the 4-stage cleanup chain (no closed-form noise floor); the
  compounding_ratio IS the capacity-feasibility test. discriminator_reachability: True (SMOKE preview shows
  REGEN=0.625 >> HP_END2END=0.35 with cv=0.0; the discriminator is reachable and survives full scale since
  ALL difficulty axes are held at FULL in smoke).
- baseline_in_band (META_RULE_AG): the 3 lossy stages land in band at hard (C=0.82, R=0.90, G=0.88 in
  [0.35,0.90]); ANALOG=0 (analog collapse is the expected floor, not a baseline gate). Verified in smoke.
- discriminator-survives-scale (option A): difficulty axes (V, V_subj, D_store, hops, hub_cluster, N_R, N_G,
  L_ctx, gate_n_tight, n_gate_train, gate_goal_noise) held at FULL in smoke; smoke reduces ONLY trials/seeds.
- HP_SCOPE: {regen: [HP_END2END, HP_COMPOUND, HP_MARGIN_vs_analog, HP_CV], oracle_chain: [WIRING_FLOOR],
  broken: [BROKEN_CEIL], stage_oracles: [STAGE_in_band]}. The compounding HP gates apply ONLY to REGEN vs
  ANALOG.
- calibration_check: adaptive_with_discriminator_gate. The gate difficulty (n_gate_train=40, gate_n_tight=16,
  gate_goal_noise=0.3) and comprehension load (L_ctx=15) were tuned so each lossy stage lands IN BAND (a
  genuine error source, not saturated/floored); the discriminator (REGEN >> ANALOG, compounding_ratio) still
  fires at these settings (smoke-verified). Tuned FOR in-band difficulty, NOT for a PASS verdict (the PASS
  emerges from compounding_ratio which was not tuned).
- cell_chunked: False (3 seeds in one cell; per-seed loop, fast; runner-zombie risk low at ~50s wall).
- start_marker_written: True. crash_diagnostic_present: True (CELL_CRASHED metrics + traceback).
  heartbeat_present: True (_heartbeat.jsonl per seed-regime). defensive_error_checking: passed_all_4_patterns.

## Gate A-E (test-design failure prevention)

- Gate A sweep_alignment_verdict: ALIGNED. Primary axis = ARMS (regen/analog/oracle/broken) x 2 regimes,
  not a parameter sweep; each arm experiences the SAME regime difficulty (paired trials). No nominal-vs-
  effective misalignment.
- Gate B discriminating_fraction: the decisive measurement (hard REGEN end2end) lands in the discriminating
  band (0.625, in [0.30,0.70]); ANALOG floors (expected); ORACLE ceils (wiring); BROKEN floors (control).
  The discriminating arm (REGEN at hard) is in band -> discriminating_fraction >= 0.30 satisfied.
- Gate C composition_edges (SHAPE audit): every subsystem lives in a DIFFERENT representational space; each
  seam's ADAPTER IS THE EXPERIMENTAL VARIABLE (REGEN snap-to-codeword vs ANALOG codec pass-through). Edges:
  comprehend->store (SHAPE_MISMATCH_adapter=regen_snap_or_analog_codec), reason->gate (adapter=
  snap_to_partition_or_raw_HV), gate->generate (adapter=clean_gen_code_or_sign_HV_codec). NO
  SHAPE_MISMATCH_no_adapter -- the adapters are named and are the axis under test.
- Gate D positive_control_arms: ORACLE_CHAIN (WIRING=1.0 at test regime) + 4 STAGE-ORACLE isolations
  reproduce each stage's in-band accuracy AT THIS TEST REGIME. Regime-extension audit: the operating points
  sit inside each subsystem's proven envelope (comprehension D6/V500 content=1.0; gate V1200_d4=0.653), BUT
  the MECHANISM realizations are REDUCED-FIDELITY (declared SHAPE_DRIFT): comprehension = HRR-unbind + partition
  typing under context load (not the block-local B_OCC envelope); gate = ridge-fit goal-transport reach WTA
  (not SR-TD trained over an operator graph). The reach WTA + abstain ACTOR is faithful; the transport
  TRAINING is lighter. Integration claim is scoped to these reduced realizations; the 4-stage compounding
  STRUCTURE (the load-bearing contribution) is faithful.
- Gate E functional_requirements: (1) parse who-did-what -> comprehension role-typing selectional restriction;
  (2) retrieve queried fact under interference -> multi-hop HRR unbind + cleanup; (3) goal-conditioned
  action selection with abstention -> goal-transport reach Go/NoGo WTA; (4) emit an ordered proposition ->
  bipolar-BSC positional decode. Each maps to an existing proven primitive (reused, no new mechanism).

## Numbers tagged

- comprehension D6/V500 content_perrole=1.0: MEASURED@data/exp_comprehension_envelope_superposition_vocab_v1/
  metrics.json:grid.D6_V500.order_content_perrole_mean
- gate fair V1200_d4 gonogo=0.653: MEASURED@data/exp_pfc_gate_cfrpe_trained_v2/metrics.json:per_regime.
  V1200_d4.gonogo
- HARD_v2 regen/analog per-slot products: MEASURED@data/exp_integration_end_to_end_loop_bridge_HARD_v2/
  metrics.json (naive_symbolic/cotrained_linear subj_acc/obj_acc)
- SMOKE preview regen=0.625/analog=0.0/compounding=0.974: MEASURED@data/exp_integration_full_stack_hard_
  regime_v1/metrics.json (run_mode=smoke)
- P_deflated(HARD_PASS)=0.45: HYPOTHESIZED@this-prereg (novel-synthesis-capped; product estimate ~0.48-0.66
  computed; smoke preview supports).

## EXPECTED_N_UNITS

FULL: n_seeds(3) x n_regimes(2) x n_arms(4) = 24 units. cardinality gate: len(per_unit_arms) == 24.

## Remote dispatch note

The real-filler cache `data/gen_integration_loop_cache/bge_concept_subset_12288_v1.npz` is UNTRACKED (~47MB);
queue_add does NOT auto-ship it. It is the SAME npz `exp_integration_end_to_end_loop_bridge_HARD_v2` used
(that cell shipped remote this session), so it is likely ALREADY on the remote -- Orchestrator to VERIFY
before FULL dispatch (SCP if absent).
