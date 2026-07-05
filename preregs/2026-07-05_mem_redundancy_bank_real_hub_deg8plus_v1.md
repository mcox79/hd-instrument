# Pre-reg: redundancy-bank lever on REAL heterogeneous deg8+ hubs (cost or wall?)

**Anchor:** `mem_redundancy_bank_real_hub_deg8plus_v1`
**Cell:** `experiments/exp_mem_redundancy_bank_real_hub_deg8plus_v1.py`
**Author:** exp_dev, 2026-07-05. Filed from research spec
`notes/research_envelope_push_memory_deg8plus_bundle_capacity_residual_2026-07-05.md`.
**Prior-work check (substrate concept-query):** top hit cosine=0.2725 (< 0.30 threshold);
nearest note = `research_drill_erasure_coded_redundancy_3x_2026-06-11.md` "Population coding and
neural redundancy" at 0.2705. NONE at cosine>0.30 -> genuinely novel cell (real-data port of a
synthetic-validated lever), not a rediscovery.

## Question
Does the REDUNDANCY-BANK lever (R independent banks, mean-before-cleanup;
CITED@exp_mem_joint_capacity_hub_degree_redundancy_v1 HARD_PASS on SYNTHETIC deg20 min 0.82)
close the deg8+ residual on the REAL heterogeneous codebook that produced it
(idx_bind_top1=0.4662 MEASURED@exp_deep_reasoning_hub_robustness_v1)? Is the residual a COMPUTE
COST (buyable with R x storage) or a genuine WALL (real correlated intra-hub interference caps
the sqrt(R) population-averaging gain)?

## Arms (per hub, per degree bin)
- `r1/r4/r8` RAW cleanup: redundancy R in {1,4,8}. r1 raw == predecessor idx_bind BY CONSTRUCTION.
- `r1_mc/r4_mc/r8_mc` MEAN-CENTERED cleanup (whiten the cos~0.57 real cone; label-free readout).
- `ctrl_synth` (R): synthetic separable codebook, same roles/degrees -> isolates real-cone effect.
- `ctrl_degenerate` (R=8 identical banks) -> must equal r1; rules out free-averaging artifact.

## Bands (pre-registered; task + research note)
- **HARD-PASS (envelope CLOSED on real data):** best pooled deg8+ recall at R>=4 clearly PAST 0.47
  (>= 0.65) AND redundancy genuinely contributes (max(r8-r1 raw, r8_mc-r1_mc) >= 0.10).
  Research-note strict sub-gates (reported, not primary): r4_raw>=0.65, r8_raw>=0.75, sub-bin
  spread (8-12/13-19/20+) <= 0.20.
- **HARD-FAIL (genuine different wall):** best pooled deg8+ recall at R=8 <= 0.50.
- **MIDDLE_BAND:** 0.50 < best_R8 < 0.65 -> route to RNS/CRT hub-sharding or PP-354 erasure coding.
- HP=0.65 feasibility: below synthetic redundancy ceiling 0.82 (deg20)
  CITED@exp_mem_joint_capacity_hub_degree_redundancy_v1 -> reachable. `discriminator_reachability=True`.

## SCHEMA-VET fields
- `cardinality_ok`: EXPECTED_N_UNITS = seeds * bins * len(R_list). Verdict counts; HARD_FAIL on breach.
- `arms_differ_verified`: r1 vs r8 recovered-idx digests distinct on deg8+ bins (META_RULE_AF).
- `final_metrics_atomicity`: tmp_replace (os.replace) + per-seed resumable partials (_seed_checkpoint).
- `crlb_n/a`: floor = MEASURED r1=0.466 (positive control) + chance 1/M; no closed-form noise floor.
- `baseline_in_band`: r1 deg8+ (~0.40-0.47) in (0.05, 0.95) (META_RULE_AG). Smoke verified 0.396.
- `discriminator_survives_scale`: SMOKE at real M=8000 + real degree dist + real cone = full physics
  (option A). Smoke r1 deg20+=0.235 collapsed; R8=0.987 -> gap 0.75 >> HP-HF gap 0.15.
- `HP_SCOPE`: HP/HF gates apply to real deg8+ pooled arms (r1/r4/r8 raw+mc). NOT ctrl_synth (reference),
  NOT deg5 bin (saturated protected reference).
- `calibration_check`: default_ok (reuses landed predecessor primitives + same real codebook; no tuning;
  mean-centering label-free).
- Gate D positive control AT TEST REGIME: r1 raw deg8+ reproduces 0.4662 (same data, N=1024) tol 0.10.
- `sweep_alignment_verdict`: ALIGNED (each hub trace = its own d edges; R banks store same d values at full N).
- `discriminating_fraction`: deg8+ test bins land in [0.30,0.70] at R1 (0.235/0.396/0.867) -> >= 0.30. OK.
- `composition_edges`: bind -> bundle -> unbind -> cleanup, all SHAPE_MATCH (reused primitives).
- `positive_control_arms`: r1 raw == idx_bind (cited prior 0.4662, MATCHED regime: same codebook/N/edges).
- `functional_requirements`: "recover correct target for each edge of a high-degree hub" -> protected
  binding (collision-break) + redundancy averaging (crosstalk-reduce) + optional mc (cone-whiten).
- `progress_logging`: print_flush_true + line_buffered stdout (full timeout may reach ~30min).
- `defensive_error_checking`: passed_all_4_patterns (start_marker, crash_diagnostic, heartbeat,
  except SystemExit-before-Exception, no bare except / BaseException).
- `cell_chunked`: false -- per-seed resumable partials via _seed_checkpoint; light CPU (not GPU-zombie
  prone); matches proven exp_mem_joint_capacity_hub_degree_redundancy_v1 single-file pattern.

## Compute architecture
(b) sequential-CPU with justification: reuses hdlab.binding torch-fft primitives; per-hub independent;
N=1024 rfft is microseconds; no material GPU speedup at N=1024; reuses the CPU reference algebra of
the landed predecessor. Full wall ~ 20-30 min (3 seeds). Storage strategy: BUNDLED per hub (the object
of study = deg8+ bundle-capacity residual; SHARDED-STORAGE-DEFAULT exemption (b): bundle-storage IS the
discriminator). Cross-hub bundling NOT used (each trace = one hub's edges).

## DATA DEPENDENCY (load-bearing for dispatch)
Requires the LOCAL-ONLY BGE cache (1.3GB) + concept partition. VERIFIED ABSENT on remote (marsh@home:
BGE_on_remote=False, concept_on_remote=False, 2026-07-05). FULL cannot run on remote_cpu_queue without a
prior 1.3GB+ sync. Predecessor `exp_deep_reasoning_hub_robustness_v1` ran full LOCALLY on FrameworkMPC
(~18.5 min) for the same reason. Full-dispatch options: (a) local judgment-call full (remote-blocked +
light cell + predecessor precedent), OR (b) orchestrator syncs BGE cache + concept partition to remote
then dispatches remote_cpu_queue.

## SMOKE RESULT (1 seed, real M=8000; MEASURED@data/exp_mem_redundancy_bank_real_hub_deg8plus_v1_smoke)
VERDICT HARD_PASS_REAL_DEG8PLUS_REDUNDANCY_CLOSES_ENVELOPE (24.3s).
- deg20+ (true tail): raw R1=0.235 -> R4=0.894 -> R8=0.987
- deg8-12: raw R1=0.867 -> R4/R8=1.0
- pooled deg8+: raw R1=0.396 -> R4=0.921 -> R8=0.990 (lift +0.595); mc nearly identical (R8=0.989)
- degenerate R8==R1 True (0.235 stays; lift is genuine bank-independence, not free averaging)
- synth ctrl R8=1.0 (real cone did NOT break sqrt(R) gain -> HARD-FAIL risk did not materialize)
- Gate D r1=0.396 within 0.10 of 0.466; research strict gates all True; sub-bin spread 0.013.
Single-seed smoke acceptable: capacity sweep (deterministic recall given mechanism), exempt from the
multi-seed-smoke AUC-inflation rule; FULL adds 3 seeds + the 13to19 bin for cross-seed robustness.
