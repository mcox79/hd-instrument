# PRE-REG: Joint capacity x hub-degree x redundancy sweep (compute-cost vs wall)

**Anchor:** `mem_joint_capacity_hub_degree_redundancy_v1`
**Cell:** `experiments/exp_mem_joint_capacity_hub_degree_redundancy_v1.py`
**Author:** exp_dev  **Date:** 2026-07-05
**Queue:** remote_cpu_queue (CPU-only; no GPU, no LLM)  **Timeout:** 7200s
**Source design:** `notes/research_5x_drill_memory_spec_and_brain_mechanism_2026-07-05.md` (the decisive test, Section E + "Cheap decisive test").

## Prior-work check (substrate-KB concept-query, USER-locked)
`bash tools/substrate_query.sh "joint capacity hub-degree sweep protected index binding associative memory graceful degradation"` -> top hit cosine=0.332 (`degradation` wordnet), then `Capability E4: Graceful capacity degradation policy` (0.311) and immune-system `protected binding exemption` (0.272). All conceptually adjacent but NONE is this joint (load x hub-degree x redundancy) protected-index bundle-capacity sweep. **Prior-work check: NONE at cosine>0.30 that matches; genuinely novel joint sweep** (continuation of the validated hub-rescue arc `exp_deep_reasoning_hub_robustness_v1`, not a rediscovery).

## Question
Is the substrate's superposition/bundle-capacity limit a COMPUTE COST (buyable with redundancy/dimension) or a fundamental WALL? And establish the (load x degree x redundancy) recall envelope two downstream build cells depend on. Answers the 3 open gaps from the 5x drill: (1) does PROTECTED/INDEX binding generalize across the full hub-degree spectrum and under load; (2) does protection tax raw non-hub capacity; (3) wall vs cost.

## Model (glass-box synthetic vector algebra; clean-synthetic per USER)
One global superposition bundle `B = sum over L associations of bind(addr, value)`, N=8192, unit i.i.d. vectors.
- A hub key reused K times with distinct values (hub-degree K); leaves = unique keys.
- UNPROTECTED addr = key (K reuses collide -> recall ~1/K). PROTECTED addr = roll(key, j) (distinct per-slot address; permutation index = unitary rotation = DIMENSION-FREE). Redundancy R = R independent banks (mean of R unbinds before cleanup).
- Retrieval: unbind by addr -> argmax cleanup vs codebook of all stored values.

## Axes / cardinality
- load L/N in {0.1, 0.2, 0.3, 0.4}; degree K in {1,2,3,5,10,20}; arm in {unprotected, protected}; redundancy R in {1,4}; seeds {7,13,19}.
- `EXPECTED_N_UNITS = seeds(3) x loads(4) x degrees(6) x arms(2) x R(2) = 288`. Verdict counts collected cells; `< 288` => HARD_FAIL_CARDINALITY_BREACH_META_RULE_H. `cardinality_ok: true`.
- Auxiliary arms: B = redundancy lever (leaf-only, R in {1,2,4,8}); C = dimension lever (leaf-only, N in {4096,8192,16384}); D = sharded-vs-bundled diagnostic (deg{5,10,20}). Not gated; establish the envelope for build cells.

## Operating point for primary gates
`op_load=0.2, op_R=4` (a modest realistic compute budget). Positive control / lift at `lo_load=0.1, R=1` (validated-win regime).

## HARD-PASS (ALL; joint gate; strictly above floor per META_RULE_L)
- **HP1 generalization:** protected hub recall >= 0.65 for EVERY deg in {2,3,5,10,20} at op AND degree-spread <= 0.20 (flat = degree-decoupled).  Feasibility (sim, seed7 N=8192): deg{1..20}=0.92/0.85/0.85/0.87/0.83/0.84 -> min 0.83>=0.65, spread 0.09<=0.20. MEASURED@feasibility sim.
- **HP2 lift:** protected - unprotected deg5+ recall >= 0.30 at lo_load R=1.  Feasibility: 0.476-0.109=+0.367.
- **HP3 cost-not-wall:** leaf recall gain R1->R8 at op_load >= 0.30 AND leaf_recall(R8) >= 2x leaf_recall(R1).  Feasibility: 0.139->0.997 (+0.858; 7.2x).
- **HP4 parity:** |protected leaf recall - unprotected leaf recall| <= 0.05 at op (protection dimension-free).  Feasibility: 0.000 (identical by construction; MEASURED to confirm).
- **HP5 fidelity:** protected hub post-cleanup round-trip fidelity (deg5+) >= 0.65 at op.  Feasibility: ~0.84.
- Positive control (Gate D): unprotected deg5 recall in [0.10,0.35] (brackets 1/5=0.20 and measured 0.219).

## HARD-FAIL (ANY)
- HF1: protected hub recall < 0.40 at op (protection collapses before ceiling).
- HF2: protected leaf recall > 0.25 below unprotected leaf at op (protection taxes capacity).
- HF3: protected hub fidelity < 0.40 (protection breaks algebra).
- HF4: redundancy R1->R8 raises leaf recall by < 0.10 (the limit IS a wall).

## MIDDLE_BAND
Partial (some HP gates pass, some fail; e.g. capacity cost in 0.05-0.25, or hub recall in 0.40-0.65). Routes to erasure-coding (PP-354) / larger fixed index-dimension budget rescue.

## Discriminator-fires assertion (META_RULE_K) -- smoke MUST satisfy
(i) unprotected deg5+ < 0.30 (a hub wall exists to rescue) AND (ii) protected-unprotected >= 0.20 (mechanism fires) AND (iii) leaf recall R4 > R1 by >= 0.10 (lever fires). If any fails in smoke: STOP, do not dispatch full.

## baseline_in_band (META_RULE_AG)
Unprotected deg5+ ~0.11-0.20 in (0.05,0.95); leaf@R1 load0.2 ~0.14 in band. Baseline measurably fails => mechanism differentiable.

## Compute architecture
Class (b) sequential/vectorized-CPU. Batched numpy rfft HRR bundle algebra at N=8192; roll via freq-domain phase (bit-identical to np.roll-then-bind, asserted vs hdlab.binding in --self-test). No material GPU speedup at N=8192; cell IS the CPU reference for the substrate bundle primitive. Full wall estimate < 25 min (3 seeds).

## Storage strategy
BUNDLED = the object of study (bundle-capacity characterization; exempt (b) per SHARDED-STORAGE-DEFAULT: bundle-storage IS the discriminator). ARM D adds a SHARDED reference point to quantify sharded headroom for the downstream build cells.

## SCHEMA-VET fields
- `cardinality_ok: true`  `arms_differ_verified: true` (protected vs unprotected recovery digests distinct for deg>=2; deg1 exempt by design: single-item permutation is identity-like).
- `final_metrics_atomicity: tmp_replace`  `cell_chunked: false` (single cell; per-seed checkpoint via `_seed_checkpoint`; ~20min wall so zombie-loss <=1 seed and restartable).
- `start_marker_written: true`  `crash_diagnostic_present: true`  `heartbeat_present: true`  `defensive_error_checking: passed_all_4_patterns`.
- `progress_logging: print_flush_true` (timeout_s>=1800; per-cell progress line every 8 cells + per-arm).
- `calibration_check: default_ok_for_this_regime` (synthetic i.i.d. unit vectors; no data leakage; deterministic given mechanism).
- `crlb_floor_computed`: retrieval SNR simulated at N=8192 (feasibility script); unprot ~1/K, protected/leaf capacity envelope measured directly; HP thresholds below the simulated ceilings.  `discriminator_reachability: true`.
- `run_mode` default full (runner sets HDLAB_RUN_MODE=full); `--self-test` fast path exit 0 <180s (measured 0.4s); `--run-mode smoke` at FULL N=8192 (discriminator-survives-scale option A).
- HP_SCOPE: HP gates apply to PROTECTED arm + leaf-parity + redundancy-lever; UNPROTECTED is the baseline (not gated by HP floors).
- effective-vs-nominal: load L/N and degree K are the EFFECTIVE parameters each primitive experiences (no partition routing). sweep_alignment_verdict: ALIGNED.
- discriminating_fraction: protected (load x K) grid spans saturated(load0.1~1.0) -> in-band(load0.3~0.55, load0.4~0.37) -> and unprotected spans in-band/floor; >=30% in [0.30,0.70]. ALIGNED.
- positive_control_arms: unprotected deg5 reproduces the measured ~0.219 hub-collapse floor AT TEST REGIME (N=8192 synthetic -> 1/K=0.20; tolerance bracket [0.10,0.35]).
