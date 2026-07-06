# Pre-reg: exp_integration_full_stack_full_fidelity_v1

Author: exp_dev (Opus 4.8 1M, agent-spawn) 2026-07-05
Cell: `experiments/exp_integration_full_stack_full_fidelity_v1.py`
Anchor: `integration_full_stack_full_fidelity_v1`
Stage: 3 (compositional integration / higher function)
Dispatch: CPU probe -> `remote_cpu_queue` (canonical FULL). Local smoke ONLY (done). No GPU.

## WHY / question
The just-passed hard-regime harness (`exp_integration_full_stack_hard_regime_v1`, c912ba56b) showed the
4-stage chain COMPOSES not compounds (REGEN compounding_ratio ~0.974 canonical / ~1.01 local;
ANALOG 0.000). BUT 2 of its 4 stages were REDUCED-FIDELITY stand-ins:
- COMPREHEND: HRR-unbind of a role-bound BGE superposition + partition-typing (stand-in) vs the REAL
  block-local envelope role-typed matched filter of `exp_comprehension_envelope_superposition_vocab_v1`.
- CONTROL-GATE: ridge-fit goal transport `M_hat` (stand-in) vs the REAL cfrpe SR-TD transport `M`
  (`train_sr_transport`) of `exp_pfc_gate_cfrpe_trained_v2` (the SR-TD gate).

This cell SWAPS both stand-ins for their proven mechanisms and re-tests compounding. Question: do the REAL
mechanisms still COMPOSE multiplicatively across the chain, or do they COMPOUND where the lighter stand-ins
did not (i.e. is integration fidelity-dependent)?

Stages 2 (STORE+REASON, HRR multi-hop `hdlab.binding`) and 4 (GENERATE, bipolar-BSC decode) are UNCHANGED
from the harness (already real/proven).

## Operating point (apples-to-apples with the stand-in harness)
The 2 real mechanisms are tuned to a per-stage operating point COMPARABLE to the stand-in harness, so the
compounding comparison is like-for-like (same difficulty, swapped mechanism) and the pre-registered bands are
capacity-feasible:
- Stand-in harness hard stages: C=0.79, R=0.84, G=0.84, Gen=1.0, product ~0.566, e2e[REGEN] ~0.572.
- Full-fidelity hard stages (MEASURED@smoke): C=0.847, R=0.903, G=0.514, Gen=1.0, product=0.401,
  e2e[REGEN]=0.431. Comparable strength; gate is the proven cfrpe FAIR band (~0.51), a touch harder than the
  stand-in's 0.84.

## Arms (paired; same propositions + frames across arms per unit)
- REGEN (regenerative relay): snap noisy inter-stage estimate to nearest KNOWN codeword at every seam.
- ANALOG (no relay): pass raw/soft-blended estimate at every seam (comprehend softmax-blend BGE; raw noisy HV
  into gate; sign(noisy HV @ P_gen) code into generate).
- ORACLE_CHAIN (WIRING gate): every stage fed ground truth -> machinery ceiling.
- BROKEN (discriminator): sever object identity at the reason hop (unbind by UNSTORED role path) -> chance.
Stage-oracle isolation: each stage fed ground truth -> comprehend/reason/gate/generate acc; product_of_stages
= their product; compounding_ratio[arm] = end2end[arm] / product_of_stages.

## Bands (envelope-fail-bands; HP strictly above floor per META_RULE_L)
- HARD_PASS (deliverable YES): compounding_ratio[REGEN] >= 0.70 AND e2e[REGEN] >= 0.35 AND
  margin(REGEN-ANALOG) >= 0.20 AND cv(REGEN across seeds) < 0.15, WITH all rails satisfied (below).
  => full-fidelity components integrate; REGEN e2e near product-of-stages; integration NOT fidelity-dependent.
- HARD_FAIL (decisive negative): e2e[REGEN] < 0.25 AND compounding_ratio[REGEN] < 0.50
  => real mechanisms compound where the stand-ins did not (integration IS fidelity-dependent; point-to-point
  relay necessary-but-not-sufficient; needs a cross-stage working-memory/thalamic buffer).
- MIDDLE_BAND: REGEN composes better than ANALOG but does not clear the full HP bar.
- RAILS (by-construction, both regimes): ORACLE_CHAIN e2e >= 0.80 (WIRING); BROKEN e2e <= 0.05 (identity);
  isolated stages in band (comprehend/reason in (0.05,0.98); gate in FAIR [0.35,0.90]; generate >= 0.80).

MEASURED@smoke preview (data/exp_integration_full_stack_full_fidelity_v1/metrics.json, 3 seeds, 24 trials):
e2e[REGEN]=0.4306, compounding_ratio[REGEN]=1.1194, margin=+0.4306, cv=0.1207; ANALOG e2e=0.000;
ORACLE_CHAIN=1.0, BROKEN=0.0; stages C=0.847/R=0.903/G=0.514/Gen=1.0; arms_differ=True. All HP gates cleared
in preview (FULL-only is canonical).

## SCHEMA-VET gates
- cardinality_ok: True. EXPECTED_N_UNITS = n_seeds(3) x n_regimes(2) x n_arms(4) = 24. Verdict counts units.
- Gate A effective_vs_nominal: sweep-free (2 fixed regimes easy/hard, not a parameter sweep). ALIGNED n/a.
- Gate B discriminating_fraction: 4 isolated stages measured; the LOSSY stages (comprehend 0.85, reason 0.90,
  gate 0.51) are all in the discriminating band (0.05,0.98) at hard; not saturated/floored. Preview confirms.
- Gate C composition_edges (signal-shape):
  - comprehend -> store+reason: REAL block-local recovers concept ID; adapter = ID -> BGE lookup (REGEN clean /
    ANALOG softmax-blend). SHAPE_MATCH_with_adapter (id->BGE is the natural regen snap).
  - block-local codebook sourced from BGE (not GSBC): identical construction (JL + top-k + sign) as the proven
    cell; sourcing from BGE carries the REAL semantic cone (harder, not easier). SHAPE_MATCH.
  - store+reason -> gate: HV -> snap to BGE candidate; reach over BGE. SHAPE_MATCH.
  - gate SR-TD transport: trained over the object-partition goal-relation graph (deterministic permutation
    successor operator) rollouts; reach = cos(cand@M, E[succ[O]]). cfrpe model-based hygiene: train on graph
    rollouts, test on held-out selection queries. SHAPE_MATCH_with_adapter (goal-relation -> operator graph).
  - gate -> generate: clean BGE codeword -> bipolar-BSC decode. SHAPE_MATCH.
  No SHAPE_MISMATCH_no_adapter.
- Gate D positive_control_arms (reproduce prior CG at test regime):
  - comprehend: real block-local role-typed matched filter reproduces the proven envelope shape (works when
    easy/injective, degrades under load): probe MEASURED L_ctx=4->exact_both~1.0, L_ctx=8->0.667, L_ctx=12->0.10
    (cliff), matching the comprehension-envelope cell's D-load cliff. Chosen hard L_ctx=6 -> C~0.81.
  - gate: SR-TD reach isolated Go-accuracy lands in the proven cfrpe FAIR band (~0.51-0.65; cited
    v1-smoke closure=0.426 / gonogo=0.479); MEASURED@smoke isolated gate=0.514. reproduces proven fair band.
  - regime_extension_audit: synthetic-GSBC comprehension -> real-BGE-block-local is SHAPE_DRIFT with declared
    risk (BGE cone is denser -> HARDER); ridge-transport -> SR-TD is the intended fidelity UPGRADE (declared).
- Gate E functional_requirements:
  1. who-did-what parse under superposition -> REAL block-local role-typed matched filter (comprehend).
  2. multi-hop relational recall among distractors -> HRR bind/unbind (store+reason; unchanged proven).
  3. goal-conditioned Go/NoGo selection among confusables -> cfrpe SR-TD reach WTA + abstain (gate).
  4. emit ordered proposition -> bipolar-BSC partition-restricted decode (generate; unchanged proven).
- CRLB / capacity-feasibility: chance obj acc = 1/V (hard V=4096 -> 2.44e-4 THEORETICAL); BROKEN lands in the
  chance band. crlb_n_a for the composition itself (no closed-form noise floor for a 4-stage cleanup chain);
  compounding_ratio IS the feasibility test. FEASIBILITY of HP bands: product_of_stages=0.401 at the chosen
  operating point, so e2e[REGEN] up to ~0.40+ is reachable and HP_END2END=0.35 is on the achievable side;
  cv<0.15 is reachable at e2e~0.43 with 60 FULL trials (sampling std ~sqrt(0.43*0.57/60)=0.064 -> cv~0.15;
  MEASURED smoke cv=0.121). discriminator_reachability=True.
- HP_SCOPE: compounding HP gates apply ONLY to REGEN vs ANALOG; WIRING gate -> ORACLE_CHAIN; collapse gate ->
  BROKEN; isolated in-band gates -> the 4 stage oracles.
- arms_differ_verified: REGEN/ANALOG/BROKEN inter-stage id streams hash-distinct per unit (True@smoke);
  ORACLE_CHAIN==REGEN bit-identity on ground-truth trials is the INTENDED decoder-WIRING coincidence (exempt).
- final_metrics_atomicity: tmp_replace.
- calibration_check: adaptive_with_discriminator_gate (cfrpe adaptive per-sample LR clamp [0.25,4.0] + linear
  decay; gate tau = low percentile of true-successor reach so Go-rate high and error is genuine selection;
  discriminator-fires verified in smoke: gate in FAIR band, comprehension in band, REGEN>>ANALOG).
- defensive_error_checking: passed_all_4_patterns (start_marker + crash_diagnostic + heartbeat +
  `except SystemExit: raise` before `except Exception`; no bare/BaseException).
- cell_chunked: False (2 seeds-per-regime loop in one cell; each unit fast; restart-cheap). start_marker_written
  True; crash_diagnostic_present True; heartbeat_present True.
- discriminator survives scale: difficulty axes (V, V_subj, L_ctx, D_store, hops, hub, gate n_tight) held at
  FULL in smoke; smoke reduces only trials + SR steps/transitions (option A: full-N in-band + REGEN>>ANALOG
  preview IS the compounding preview).

## Compute architecture
Class: (c) mixed. The gate SR-TD transport training is a batched-CPU matmul loop (torch, N_R=1024, per
(regime,seed)); comprehension block-local matched filter + HRR store/reason are numpy. No GPU (task-mandated
CPU probe; no LLM). Genuine sequential dependency: SR training is iterative TD(0); chain hops are sequential.
Storage strategy: no_bundled_store for composition; SR M is a learned value operator, HRR store is per-fact
sharded bind superposition (proven regime). progress_logging: print_flush_true (line-buffered stdout +
flush=True per (regime,seed) + heartbeat). timeout: recommend 1800s on remote_cpu_queue (smoke=127.5s at
sr_steps=1500/trials=24/3seeds; FULL sr_steps=3000/trials=60 ~ 3-4x -> ~450-550s + remote-CPU margin).

## Run-mode
`--self-test` (PASS, ~8s) / `--smoke` (SMOKE_MACHINERY_OK, ~128s local) / bare or HDLAB_RUN_MODE=full -> full.
Data dependency: `data/gen_integration_loop_cache/bge_concept_subset_12288_v1.npz` (untracked; SCP to remote
before FULL dispatch -- queue_add does NOT auto-ship it). No GSBC pool needed (block-local sourced from BGE).
