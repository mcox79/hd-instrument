# grounding_multihop_perhop_cleanup_gate_v1 -- per-hop cleanup gate between hops of a learned-code chain

## Cell
`experiments/exp_grounding_multihop_perhop_cleanup_gate_v1.py`

## Purpose (Stage-4 reader; revival of the VET-confirmed Stage-3 HARD_FAIL negative)
Stage-3 established (block-code binding v1 + structured-encoder multihop v1; director backup 2026-07-08) that
reach>=2 multi-hop chaining on REAL learned (semantically-correlated) codes is walled by LEARNED-CODE CROSSTALK
at graph scale, NOT the bind operator (the operator was already swapped and ruled out). The brain-grounding
drill (`notes/research_learned_code_crosstalk_cleanup_decorrelation_at_scale_5x_2026-07-09.md`) converged --
across hippocampal DG/CA3/CA1, cerebellar expansion, and VSA/resonator theory -- on ONE mechanism SHAPE: a
repeated, LOCAL, per-hop re-sparsification + comparator/novelty gate inserted BETWEEN every step, built to strip
only INCIDENTAL redundancy while PRESERVING genuine semantic correlation (never global orthogonalization).
This cell inserts exactly that gate into a genuine hop-by-hop associative chain over the learned codes and asks:
does per-hop cleanup recover functional reach 2-3 where the no-cleanup chain collapses to reach 1?

## Honest ceiling (pre-registered target: REACH 2-3, NOT reach>=4-5)
CITED@notes/research_learned_code_crosstalk_cleanup_decorrelation_at_scale_5x_2026-07-09.md: three independent
lines (VSA capacity theory on correlated codebooks = open problem; predictive-coding preserves-informative-
correlation floor; hippocampal attractor capacity + transitive-inference reliable only ~4-7 items) agree the
brain does NOT beat the correlated-crosstalk limit -- it pushes the threshold back via per-hop cleanup targeting
INCIDENTAL noise and keeps chains short. So the bar is material reach-2-3 recovery over the no-cleanup baseline,
NOT unlimited-depth chaining. reach>=4-5 on genuinely-correlated learned codes is treated as a SEPARATE later
mechanism (hierarchical chunking / landmark-hub), not something more cleanup can solve. P_deflated (drill) =
0.35 that a candidate recovers reach-2 to a usable working fidelity.

## Prior-work check (SUBSTRATE-KB concept-query, USER-locked)
`bash tools/substrate_query.sh "per-hop cleanup decorrelation between hops multi-hop chain retrieval crosstalk sparse re-separation gate"`
top hits (cosine 0.31-0.34):
- `preregs/2026-07-03_stage2_benchmark_reframe_vsa_native_task_suite.md::chunk009` (0.344) -- the GENERAL multi-
  hop-reasoning task framing (chain over KB triples), NOT a per-hop cleanup mechanism.
- `notes/research_drill_optimal_shard_granularity_5x_2026-06-08.md` (0.315) -- K-hop/multi-hop retrieval shard
  granularity, NOT a between-hop cleanup gate.
NOVELTY: GENUINELY NOVEL. No prior arc cell inserts a between-hop re-separation/residual cleanup gate into the
learned-code chain. The two Stage-3 cells swapped the bind OPERATOR (dense->block-local) and the ENCODE-time
binding objective; neither touched the between-hop stage. This cell holds the operator + codes fixed (the
Stage-3 primary treatment) and varies ONLY the between-hop cleanup gate. REUSED not rebuilt: ProjHead / info_nce
/ vicreg / char_trigram_features (CG'd teacher-free encoder primitives), `load_typed_cn_subgraph` /
`make_unitary_roles` / `crosstalk_floor` (structured-encoder-multihop v1). The numeric core (device-aware chain
+ cleanup gates) is new by necessity (no prior between-hop-gate primitive exists).

## Arms (paired: identical planted chains + identical learned codes + identical seeds across all 4 arms) + HP_SCOPE
- A `NO_CLEANUP` -- the Stage-3 chain. Raw HRR accumulation carried forward each hop (no per-hop cleanup); a
  single global cleanup only at readout. MUST-FAIL / reference control. HP_SCOPE: reference-only (NOT a recovery
  arm; MUST FAIL at reach-2 for the discriminator to be valid). ARMS-DIFFER exempt-from-passing.
- B `PLAIN_CLEANUP` -- per-hop top-1 snap to the nearest codebook node code (generic cleanup, no re-separation,
  no residual). Candidate mechanism (simplest per-hop cleanup) AND attribution control for C/D. HP_SCOPE: recovery gates.
- C `DG_RESEP` -- Candidate 1 (DG/cerebellar pattern-separation): per-hop cleanup whose argmax-snap is computed
  in a FIXED-random sparse-expansion + k-WTA sketch space (granule-cell re-encoding; the k-WTA nonlinearity, not
  the linear projection, is what decorrelates). HP_SCOPE: recovery gates.
- D `CA1_RESIDUAL` -- Candidate 2 (CA1 novelty / predictive-coding explaining-away): per-hop comparator gate
  forwarding the novel component `pred - NOVELTY_LAMBDA*cue_parallel` (SOFT explaining-away; full removal
  over-suppresses -- MEASURED at smoke, see below). HP_SCOPE: recovery gates.

## Metric
fidelity@d = hit@K (true node at hop d in the top-K of the arm's readout score vs the codebook), K=HIT_K=10,
measured along the SAME planted true typed L-hop paths (L=MAX_REACH=4) for every arm. Cleanup arms commit top-1
each hop (compounding); NO_CLEANUP carries the raw accumulated bound vector. PAIRED across arms (identical
chains/codes/seeds) -- the arm-comparison discriminator is paired per USER-locked rule.

## Bands (pre-registered BEFORE FULL; RELATIVE to the measured single-hop cap)
Bands are relative to NO_CLEANUP@1 (the single-hop cap) per the drill's "reach-2 within ~15% of reach-1"
ceiling, NOT an absolute fidelity that ignores the encoder's single-hop ceiling.
- MEASURED@data/exp_grounding_multihop_perhop_cleanup_gate_v1_smoke/metrics.json (2-seed CPU smoke, n=1525):
  - NO_CLEANUP fid@1=0.444 (single-hop cap; >> chance ~0.007), fid@2=0.038 (COLLAPSES -- must-fail control
    genuinely fails at smoke scale), fid@3=0.015, fid@4=0.003.
  - PLAIN_CLEANUP fid@2=0.137 (gain2=+0.099), DG_RESEP fid@2=0.121 (gain2=+0.083), CA1_RESIDUAL fid@2=0.090
    (gain2=+0.052). All candidates give MATERIAL reach-2 gain over the collapsed baseline; none clears HARD_PASS
    at smoke scale (sub-HARD_PASS smoke -> MIDDLE_BAND, cleared for multi-seed FULL).
- `hop1_ok` (baseline_in_band, precondition): NO_CLEANUP@1 >= HOP1_MIN=0.30. If below -> INCONCLUSIVE_RECOVERY_FAILED.
- `baseline_collapses` (anti-saturation / discriminator-fires, USER-locked saturation-vacuous guard): NO_CLEANUP@2
  <= BASE_COLLAPSE_ABS=0.40 AND <= BASE_COLLAPSE_FRAC=0.50 * NO_CLEANUP@1. MUST hold at smoke (MEASURED: 0.038,
  collapsed 91%). If it does not collapse -> INCONCLUSIVE_BASELINE_DID_NOT_FAIL (re-spec).
- `HARD_PASS` (per candidate B/C/D): gain2 = cand@2 - NO_CLEANUP@2 >= GAIN2_HP=0.10 (absolute margin over the
  collapsed baseline) AND cand@2 >= RECOVER_FRAC=0.50 * cand@1 (reach-2 keeps >=half the single-hop cap) AND
  gain3 = cand@3 - NO_CLEANUP@3 >= PERSIST3_HP=0.05 (reach-2 gain persists to reach 3, so a reach-2-only fluke
  is MIDDLE_BAND not HARD_PASS). Verdict HARD_PASS if ANY candidate passes.
- `HARD_FAIL_CROSSTALK_FLOOR_FUNDAMENTAL`: best candidate gain2 < MATERIAL_MIN=0.05 (no cleanup variant helps at
  this correlation level -- crosstalk floor is fundamental; next mechanism = hierarchical chunking, not cleanup).
- `MIDDLE_BAND`: partial gain (0.05-0.10) OR reach-2 gain that does not persist to reach 3.

## Secondary telemetry (reported, not gated)
- Decay slope of fidelity across d=1..4 per arm (Candidate 2's native discriminator: does the gate flatten the
  crosstalk decay). Attribution: does the sophisticated gate (DG/CA1) beat the PLAIN cleanup control.

## Compute architecture
Class (c) MIXED with justification. Storage: `no_composition` of stored items (chain is over per-node learned
codes, no bundled multi-item store). Encoder training: device-aware torch (reused ProjHead + vicreg CG'd
primitives; light -- single Linear head, ~1s/seed at smoke). Chain retrieval: the hop-loop is SEQUENTIAL (hop N
depends on hop N-1 -- the explicit sequential-dependency exception to GPU-batching-mandatory) BUT within each
hop the codebook-cleanup matmuls + DG sketch projection are BATCHED across all chains on-device. Device = cuda
if available else cpu (auto): GPU node -> genuine cuda for the matmul-heavy cleanup (Fix24); laptop smoke -> cpu.
Wall: smoke ~8s CPU (n=1525, 2 seeds); FULL n=5000/3-seed expected < a few min on GPU.

## SCHEMA-VET fields
- arms_differ_verified: true (per-chain hit signatures hashed per arm; smoke MEASURED 4 distinct signatures).
- final_metrics_atomicity: tmp_replace (via `_seed_checkpoint.write_metrics` + os.replace).
- crlb: hit@K chance floor = K/n_nodes (~0.006 at n=5000). HARD_PASS is RELATIVE (>= 0.5*cand@1) and >> chance;
  the anti-saturation requirement is empirical (NO_CLEANUP@2 collapse verified at smoke), crlb_n/a for the gain.
- discriminator_reachability: true (candidates MEASURED above baseline at smoke; HARD_PASS bar relative-feasible).
- baseline_in_band: true at smoke (NO_CLEANUP@1=0.444 in-band, @2=0.038 collapsed).
- discriminator survives scale: the saturation-vacuous guard = the must-fail control failing AT smoke scale (it
  does, hard); at FULL n=5000 (bigger codebook) baseline crosstalk is stronger, so the discriminator survives/
  strengthens. SMOKE exercises the SAME 4 arms / same code path as FULL (only n/epochs/seeds/n_chains scale).
- cardinality_ok: EXPECTED_N_UNITS = n_seeds (FULL=3); each seed asserted to produce all 4 arms x all 4 depths.
- calibration_check: adaptive_with_discriminator_gate (baseline-collapse gate recomputed empirically per run;
  codebook-size-aware crosstalk floor; paired per-chain hits).
- cell_chunked: false (multi-seed within one cell; seeds are cheap + per-seed checkpointed via write_partial).
- start_marker_written: true. crash_diagnostic_present: true (Exception -> CELL_CRASHED + traceback, atomic).
  heartbeat_present: true (emit_heartbeat during encoder training). defensive_error_checking: passed_all_4_patterns.
- except SystemExit: raise BEFORE except Exception (no BaseException / no bare except): verified (grep clean).
- sweep gates (composition/sweep): sweep_alignment_verdict: ALIGNED (depth d is the swept axis; every arm
  experiences the same d). discriminating_fraction: reach-2 is the discriminating point (baseline collapsed,
  candidates measurable) -- >= 0.30 of depths in band. composition_edges: bind->cleanup->bind, SHAPE_MATCH
  (cleanup returns a code-space vector; DG cleanup returns a node index -> clean code, shape-matched). Gate D
  positive-control: NO_CLEANUP@1 reproduces the single-hop cap at the test regime (the reproducer arm).
  functional_requirements: (1) single-hop associative retrieval on learned codes -> hit@K over codebook;
  (2) between-hop crosstalk control -> the per-hop cleanup gate (new mechanism, flagged as new).
- run_mode: smoke MEASURED run_mode=smoke (8459 B, device=cpu); FULL must land run_mode=full (verify post-dispatch).
- progress_logging: print_flush_true (line-buffered stdout + flush=True _log + per-epoch heartbeat).

## Dispatch
- Queue: `overnight_queue` (GPU; gpu_runner_0 idle -- no contention with the two CPU grounding probes).
- FULL config: seeds [7,13,17], n_nodes 5000, code_dim 256, feat_dim 8192, epochs 140, dg_dim 8192, n_chains 1200.
- Timeout: 3600 s (cell is compute-light; heartbeat + progress logging catch any hang well inside this).
- Smoke: PASS on `.venv` CPU (self-test PASS; smoke MIDDLE_BAND, discriminator LIVE, must-fail control collapses).
