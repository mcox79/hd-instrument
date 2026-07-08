# Pre-reg: conceptnet_semantic_seeded_beam_composition_v1

Date: 2026-07-07. Author: exp_dev (Opus, HIGH). Cell:
`experiments/exp_conceptnet_semantic_seeded_beam_composition_v1.py`.
Scoping source: `notes/research_multihop_composition_gap_closure_scoping_2026-07-07.md`.

## Claim (honest, pre-committed MIDDLE)

The June-19 ConceptNet HARD_FAIL (substrate Hits@10=0.451 < BGE 0.502,
MEASURED@data/substrate_conceptnet_kg_inference_transfer_cpu_v1_metrics.json) has TWO named causes,
neither of which was "missing per-hop re-clean" (that was already present -> REFUTED by code read):
- (c) high-branching to-many relations decoded by a SINGLE hard argmax (no beam / one candidate carried).
- (d) entity codes = pure random noise (zero semantic content) vs BGE pretrained semantics.

This cell fixes BOTH and ablates them separately. Cause-(d) fix = SEMANTIC-SEED entity codebook =
SimHash (sign of a fixed Gaussian random projection) of the BGE-large teacher embedding that the
CHAIN_GRADE GSBC encoder distills (cached npz, keyed by exact CN_ ids, 100pct overlap MEASURED). This
is the encoder's TEACHER/INPUT (semantic upper bound; substrate-native GSBC sparsification is
lossier, ret_agree10=0.432 MEASURED@backup 2026-07-07 -> follow-up). Cause-(c) fix = TOP-K BEAM per
hop (k=1 reproduces the June-19 decoder EXACTLY, verified in --self-test).

## Arms (single deterministic seed; ablation 2x2 + firing control)

| arm | entity codes | beam_k | isolates |
|-----|--------------|--------|----------|
| RANDOM_K1 | random bipolar | 1 | reproduces June-19 (Gate-D positive control) |
| RANDOM_BEAM | random bipolar | K | beam-alone |
| SEM_K1 | BGE-SimHash | 1 | semantic-seed-alone |
| SEM_BEAM | BGE-SimHash | K | BOTH (PRIMARY) |
| SEM_SCRAM_BEAM | scrambled semantic | K | firing control (must collapse to ~RANDOM) |

Baselines (shared): transitive-closure BFS; frozen BGE-large cosine (bge_cached); random-rank floor.
External sacrosanct bar = June-19 live BGE Hits@10 = 0.502.

## Bands (research pre-reg; applied to PRIMARY arm SEM_BEAM)

- HARD_PASS (STRETCH, P~0.15-0.20): SEM_BEAM Hits@10 >= closure+0.05 AND >= max(bge_cached, 0.502)+0.05
  AND nontrivial_lift_hits10 >= 0.00 AND sub_auroc >= 0.7.
- MIDDLE (EXPECTED / pre-committed, P~0.40-0.45): min_lift in [-0.02, +0.05) OR nontrivial_lift
  improves from -0.72 into [-0.30, 0.00).
- HARD_FAIL: SEM_BEAM <= max(closure, bge) AND nontrivial_lift <= -0.50.

Pre-committed modal expectation = MIDDLE. Beating BGE is the stretch, NOT the base case.

## SCHEMA-VET gates

- cardinality_ok: true. EXPECTED_N_UNITS = 5 arms (fixed ablation, not a numeric sweep). Verdict
  counts len(ARMS); arms_differ hash-check (META_RULE_AF).
- Gate A (effective vs nominal): N/A -- no numeric sweep axis. `sweep_alignment_verdict: N/A`.
- Gate B (discriminating band): predicted per-arm Hits@10 all in [0.30, 0.70]
  (RANDOM_K1~0.45 HYPOTHESIZED@June-19; SEM arms ~0.45-0.55). discriminating_fraction = 1.0 (>=0.30).
- Gate C (shape compat): edges = {BGE teacher (1024d)} -> SimHash sign -> bipolar N_DIM (SHAPE_MATCH,
  stays in the cf-RPE elementwise-mul bipolar algebra); {bipolar entity} -> cf-RPE store (SHAPE_MATCH);
  {beam entity carry} -> candidate scoring (SHAPE_MATCH). No SHAPE_MISMATCH_no_adapter.
- Gate D (positive control at test regime): arm RANDOM_K1 reproduces June-19 substrate Hits@10=0.451
  (cited_prior_metric=0.451, tolerance 0.10) AT THE SAME held-out split (June-19 cell reused as a
  library -> byte-identical classification/candidate-pool/metrics). regime_extension: SHAPE_MATCH
  (identical regime).
- Gate E (functional requirements): (1) entity codes carry semantic similarity structure -> BGE-SimHash;
  (2) survive high-branching hops via multi-hypothesis carry-through -> top-k beam.
- discriminator-fires (META_RULE_K): structural fire-check cause-(d): mean_edge_cos(SEM) -
  mean_edge_cos(RANDOM) > 0.02 (semantic content genuinely present). Smoke must satisfy.
- baseline_in_band (META_RULE_AG): RANDOM_K1 in (0.05, 0.95).
- CRLB: crlb_n/a -- ranking metric Hits@10 in [0,1]; no closed-form noise floor; feasibility = bar
  0.502 reachable in [0,1]. `discriminator_reachability: true`.
- final_metrics_atomicity: tmp_replace (crash-path) + write_metrics for the clean path (single-shot;
  no in-place tuning loop).
- Compute architecture: sequential-CPU with justification -- cf-RPE store recall is a CHAINED
  retrieval (hop N depends on cleanup of hop N-1); numpy CPU bipolar reference; NumPy-only => routes
  to remote_cpu_queue (PROT-020: no GPU). Wall-time bounded; beam multiplies per-row cost by k.
- Storage strategy: SHARDED (cf-RPE associative store, per-edge; not bundled) -- correct for
  compositional multi-hop.
- start_marker_written / crash_diagnostic_present / heartbeat_present: true. cell_chunked: false
  (single deterministic seed, as June-19). defensive_error_checking: passed_all_4_patterns.
- progress_logging: print_flush_true + line_buffered_stdout (timeout_s >= 1800 at FULL).
- HP_SCOPE: {SEM_BEAM: [hard_pass, hard_fail, middle]}; the 4 non-primary arms are ablation/control
  arms -- they do NOT inherit the SEM_BEAM band gates (report-only).

## Compute / dispatch

- SMOKE: N_DIM=2048, CLASSIFY_POOL=900, STORE_CAP=1200, BEAM_K=4 -> local_cpu_queue (SMOKE ONLY per
  USER-LOCK). Fires: semantic_fires, gate_d_repro (approx), arms_differ, baseline_in_band.
- FULL: N_DIM=8192, full held_t pool (== June-19), STORE_CAP=8000, BEAM_K=6 -> remote_cpu_queue
  (NumPy CPU; needs orchestrator dispatch -- exp_dev cannot push/SCP). --timeout estimated from smoke.

## SMOKE ADDENDUM (post-smoke; BANDS ABOVE UNCHANGED / sacrosanct)

Smoke (N_DIM=2048, WITH=51, all gates fired: semantic_fires=True, gate_d_repro=True,
scramble_collapses=True, arms_differ=True) MEASURED@data/exp_conceptnet_semantic_seeded_beam_composition_v1_smoke/metrics.json:
- RANDOM_K1=0.510, RANDOM_BEAM=0.549, SEM_K1=0.176, SEM_BEAM=0.157, SCRAM=0.137; closure=0.941,
  bge_cached=0.471.
- FINDING: semantic-seed HURTS (SEM << RANDOM); BEAM HELPS random (+0.039). Mechanism: correlated
  semantic codes (edge-cos +0.20 vs orthogonal random 0.0) COLLIDE the cf-RPE associative store.
  This is the known "correlation-hurts-capacity" tension and it DOMINATES semantic-generalization at
  this store load.
- SCALE NOTE (load-bearing): store load = edges/N_DIM is MATCHED at FULL (8000/8192=0.98) vs smoke
  (1798/2048=0.88), so the semantic penalty will NOT be relieved by 4x N_DIM -> SEM_BEAM is expected
  to HARD_FAIL at FULL too. DEFLATED expectation revised DOWN from MIDDLE: modal FULL outcome for the
  PRIMARY (SEM_BEAM) arm = HARD_FAIL. The genuinely promising, SUBSTRATE-NATIVE lever is RANDOM_BEAM
  (beam-alone, no BGE dependence): at smoke it lifted +0.039 over RANDOM_K1; whether it lifts June-19
  0.451 toward/past BGE 0.502 at FULL is THE open question this FULL run answers.

Bands are NOT changed post-smoke (sacrosanct). This addendum only records the measured preview and
the honestly-deflated expectation for skunkworks/verdict framing.

## Prior-work check

substrate_query "multihop composition semantic seeded entity codebook beam search knowledge graph
completion" -> top hits: generic 'Composition' note (cosine 0.3584), 'Entity resolution + knowledge
graph construction' (0.3203). NO prior arc cell for semantic-seed + beam on ConceptNet. The June-19
random-code cell is the acknowledged prior; this cell is a genuine two-cause extension of it, not a
rediscovery.
