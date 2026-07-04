# Pre-registration: Concept-Encoder Design Ablation v1 (sparsity x fidelity Pareto)

- Date: 2026-07-04
- Anchor: `encoder_design_ablation_v1`
- Cell: `experiments/exp_encoder_design_ablation_v1_core.py`
- Author: hdi_exp_dev
- Class: EMPIRICAL DESIGN-SEARCH (not a capability PASS/FAIL cell). Deliverable is
  a Pareto frontier over (semantic fidelity, algebraic fidelity) across sparsity
  levels, to test whether the Step-1 encoder's locked ~2%/[18,22] sparsity target
  is on the frontier or dominated.

## Motivation

The production concept encoder
(`exp_encoder_migration_step1_train_concept_encoder_970K_KB_v1_core.py`) LOCKS a
sparsity rate `K_SPARSITY=0.02` (mean_nnz in [18,22] at N=1024 self-test; k=82 at
N=4096 FULL) and ONE training objective (Hebbian context-mean of char-positional
surface HDs + top-K WTA). These are inherited from Spoke-1 v3-D CG defaults, NOT
empirically optimized for the concept-encoding task. USER directive: the concept
encoder is the load-bearing component of the neuro-modeled MEMORY system; find the
optimal design point empirically rather than assume the current one is right.

## Prior-work check (SUBSTRATE-KB CONCEPT-QUERY BEFORE AUTHORING)

`bash tools/substrate_query.sh "concept encoder sparsity level active dimensions
semantic fidelity algebraic bind unbind roundtrip Pareto"` (confidence=0.27, top
hits below 0.30 cosine but directly relevant; READ):

1. `notes/research_sparse_bipolar_compose_incompatibility_2x_drill_2026-06-23.md`
   (cos 0.2725): sparse-bipolar ELEMENTWISE-MULTIPLY bind COLLAPSES sparsity
   (density = f^k -> near-zero after k binds); brain's bind PRESERVES sparsity.
   NOTE: this is the MAP/FHRR elementwise-multiply failure mode. This cell uses
   the substrate's REAL-vector bind = HRR circular convolution (hdlab.binding.bind
   on real input), which does NOT collapse sparsity the same way. The algebraic
   axis here tests HRR bind+bundle+cleanup, not elementwise-multiply compose.
2. `notes/strategy_decisions_2026-06-08.md` (cos 0.2617): sparse-VALUE encoding was
   found 60% worse than dense for STORAGE capacity at N=1024; "higher sparsity is
   actively harmful" for value encoding. Sparse-KEY axis unaffected.

Prior-work verdict: NOT a rediscovery. Prior findings measured (a) elementwise-
multiply compose collapse and (b) sparse-VALUE storage capacity in synthetic
regimes. This cell is NOVEL: it measures the two-axis (semantic RSA vs HRR
bind/bundle/cleanup) Pareto trade-off of the ACTUAL production concept encoder on
REAL KB concepts with BGE-large semantic gold. The prior sparse-value-storage
finding PREDICTS dense should win the storage/capacity axis; this cell tests
whether semantic fidelity trades against it (the two-axis tension the task targets).

## Design

### Data
- Concepts sampled deterministically from the intersection of:
  (a) KB entities in `data/substrate_director_kb_v1/entities.jsonl` that have >=1
      atom-context in `atoms.jsonl`, AND
  (b) names present in the cached BGE-large name-embedding index
      `data/substrate_index/cached_indices/bge_large_v2_name_*.npz` (largest by
      coverage; ~43905 names; `semantic` 1024-d float32 + `id_order_json`).
  Measured intersection over first 200K KB entities = 16382 names
  (MEASURED@probe 2026-07-04). Real structured concepts: `T1/vector_space`,
  `GO_0005126`, `WN_piece.n.05`, `T2/oeis_A000300`.
- SMOKE: N_CONCEPTS = 600. FULL: N_CONCEPTS = 5000. Deterministic seeded sample.
- Contexts built via the SAME logic as Step-1 `_build_entity_context_map`
  (predicate+object / subject+predicate phrase per atom; single atom-scan).

### Encoding (SAME code path smoke==full; objective held at current)
- Surface encoder: `hdlab.char_positional_encoder.CharPositionalEncoder`
  (N_DIM=1024, max_pos=24, seed_prefix fixed). Encode each context sentence;
  Hebbian mean -> dense float32 accumulator `acc[n, N]` (PRE-WTA). Encode ONCE.
- Sparsity sweep derives all code tables from the SAME `acc` by top-k WTA:
  the load-bearing knob is the ONLY thing that varies across arms.

### Sweep axis (load-bearing)
`K_LEVELS = [8, 16, 20, 32, 64, 1024]` (1024 = dense; sign of acc, no WTA).
At N_DIM=1024 these are rates {0.78%, 1.56%, 2.0%, 3.13%, 6.25%, 100%}. The
production 2% rate is the k=20 point; brackets [18,22] in BOTH directions.
N_DIM=1024 chosen to match the Step-1 self-test reference band [18,22] and keep
absolute sparsity counts meaningful; finding is expressed as a RATE (k/N) so it
transfers to the FULL N=4096 regime (caveat: rate-transfer flagged, not proven).

### Objective axis
Held at the CURRENT objective (Hebbian context-mean + WTA) for SMOKE. Distillation-
from-BGE vs contrastive vs reconstruction objective sweep is FLAGGED as a FULL
follow-on (requires a learned BGE->HD projection + train/held-out split; not
tractable in SMOKE budget without a training pipeline). Per task authorization:
"If only one is tractable in SMOKE budget, do sparsity sweep at the current
objective and flag the objective sweep as a FULL follow-on."

### Fidelity axes (BOTH measured per sparsity level -- key discipline)

**A. Semantic fidelity (cross-space; RSA / neighbor-preservation).**
Direct per-vector cosine to BGE-gold is DIMENSIONALLY INCOMPATIBLE (concept code =
1024-d sparse bipolar in a hash basis; BGE = 1024-d dense in a learned basis;
their axes are unrelated). The principled cross-space semantic metric is second-
order (representational similarity): does the code preserve BGE's semantic
NEIGHBORHOOD structure?
- Primary: `neighbor_recall@10` -- for each of Q=150 held-out query concepts, the
  fraction of its BGE-gold top-10 neighbors recovered in its concept-code top-10
  neighbors (neighbors over the full sampled codebook, self excluded).
- Secondary: `rsa_spearman` -- Spearman rank-correlation of the two pairwise
  cosine-similarity matrices over the query set.
Prediction (HYPOTHESIZED): semantic fidelity INCREASES with k (aggressive sparsity
discards Hebbian signal -> loses neighborhood structure; dense retains most).

**B. Algebraic fidelity (does the code survive the substrate bind/bundle/cleanup
algebra).** Uses the REAL `hdlab.binding.bind/unbind` primitives (real input ->
HRR circular convolution), NOT a reimplementation.
- Primary: `bundle_cleanup_acc@M` -- bundle M role-filler pairs
  sum_j bind(code_j, role_j); unbind by role_0; argmax-cleanup against the full
  SHARDED codebook; accuracy = argmax == correct index. Role vectors random
  bipolar from fixed generator. 3 role-seeds x 150 trials; report mean +/- std.
  M-grid = [24, 40, 64, 96] (capacity pressure). `reporting_M` chosen adaptively
  as the M whose DENSE (k=1024) accuracy is closest to 0.7 and inside (0.05,0.95)
  -- keeps the baseline in a measurable band (META_RULE_AG); discriminator-fires
  logged (META_RULE_M adaptive_with_discriminator_gate).
- Secondary sanity: `roundtrip_cos@M1` -- single bind/unbind roundtrip cosine
  (expected ~1.0 all k; confirms codes are algebra-usable at all).
Prediction (HYPOTHESIZED): algebraic capacity PEAKS at intermediate k (dense =
more superposition crosstalk; k=8 = fragile) -- creating the Pareto tension vs
semantic fidelity.

### Pareto frontier
Report table k x (neighbor_recall@10, bundle_cleanup_acc@reporting_M). Compute the
non-dominated set. Report whether k=20 ([18,22]) is on the frontier or dominated,
and which k dominates it if so. DO NOT pre-bake the conclusion.

## Envelope (PASS / FAIL bands) -- gates the MACHINERY, not the finding

This is a design-search: the SCIENTIFIC finding (frontier shape, optimal k) is
REPORTED, not gated. The verdict gates whether the sweep is a clean, non-degenerate
frontier ready to promote to FULL.

- HARD_FAIL:
  - `n_nan > 0` or `n_inf > 0` anywhere, OR
  - `len(per_level) != 6` (HARD_FAIL_CARDINALITY_BREACH_META_RULE_H), OR
  - any two code tables bit-identical (META_RULE_AF).
- MIDDLE_BAND (sweep ran but weak / vacuous):
  - discriminator does NOT fire: `max(semantic_spread, algebraic_spread) < 0.05`
    (frontier is a single point -> sparsity does not matter in this regime;
    inconclusive, re-spec before FULL), OR
  - dense baseline cannot be placed in (0.05, 0.95) at any M in the grid
    (`baseline_in_band == False`).
- HARD_PASS (frontier non-degenerate, promote to FULL):
  - cardinality_ok, arms_differ_verified, no NaN/Inf, baseline_in_band True, AND
  - `max(semantic_spread, algebraic_spread) >= 0.05` (discriminator fires:
    sparsity measurably moves at least one fidelity axis).

`semantic_spread = max_k(recall@10) - min_k(recall@10)`;
`algebraic_spread = max_k(acc@reporting_M) - min_k(acc@reporting_M)`.

## Discipline gates (SCHEMA-VET)

- `cardinality_ok`: EXPECTED_N_UNITS = len(K_LEVELS) = 6 (each level fully measured
  on both axes; the 3 role-seeds are averaged WITHIN the algebraic metric of a
  level). Verdict asserts `len(per_level) == 6`.
- `arms_differ_verified`: sha256 of each int8 code table; all 6 must be distinct.
- `baseline_in_band`: dense (k=1024) algebraic acc at reporting_M in (0.05, 0.95).
- `discriminator survives scale`: SMOKE=600 concepts, FULL=5000 concepts, SAME
  code path (encode-once + WTA-sweep + same fidelity fns). The discriminator is
  the SPREAD across sparsity, which is a property of the code family not the
  concept count; multi-seed (3) role-randomness variance probed in smoke per
  META_RULE_smoke_single_seed_inflates_AUC (algebraic acc is a continuous score).
- `calibration_check`: `adaptive_with_discriminator_gate` (reporting_M adaptive to
  land dense in band; discriminator-fires spread logged to metrics).
- `crlb_n/a`: "design-search; no fixed quantitative pass threshold. The frontier is
  descriptive; the only gate is discriminator-spread >= 0.05, which is verified
  empirically in smoke, not against a Cramer-Rao floor."
- `final_metrics_atomicity`: `tmp_replace` (write_metrics -> atomic).
- `cell_chunked`: false (single-seed encoder; role-seeds looped inside one cell,
  fast, no runner-death multi-seed-loss risk at <2min wall).
- `start_marker_written`: true. `crash_diagnostic_present`: true (Exception ->
  CELL_CRASHED + traceback, except SystemExit/KeyboardInterrupt raised first).
  `heartbeat_present`: true (per-sparsity-level heartbeat).
  `defensive_error_checking`: passed_all_4_patterns.
- `progress_logging`: `print_flush_true` (line-buffered stdout + flush).

## Compute architecture
- Class: `(b) sequential-CPU with justification`.
- Justification: (1) cell VALIDATES substrate primitives (HRR bind/unbind via
  hdlab.binding) -- primitive-validation exemption; (2) total smoke wall < 2 min,
  per-unit wall < 10s -- below the batching-candidate threshold; (3) bind is
  already BATCHED across the M pairs of a bundle (bind([M,N],[M,N]) row-wise FFT);
  (4) no GPU on this laptop (torch 2.8.0+cpu, cuda=False). Semantic-sim matmuls are
  numpy BLAS (not python loops). No python-loop matmul over the scaling axis.
- Storage strategy: SHARDED codebook for cleanup (each concept = its own vector);
  the bundle-capacity arm INTENTIONALLY bundles M pairs as the capacity
  discriminator (positive control for bundled superposition under the substrate
  algebra). Declared per SHARDED-default rule; bundling here is the measured
  discriminator, not a storage default.

## Functional requirements
1. "Concept code must carry real semantics" -> semantic axis (neighbor_recall@10
   vs BGE-large gold). Primitive: CharPositionalEncoder Hebbian context-mean.
2. "Concept code must survive composition (bind/bundle/cleanup)" -> algebraic axis
   (bundle_cleanup_acc). Primitive: hdlab.binding HRR bind/unbind + argmax cleanup.
3. "Find the sparsity design point that best balances 1 and 2" -> Pareto frontier
   over K_LEVELS; report whether k=20 is on it.

## Sweep-composition gates
- `sweep_alignment_verdict`: ALIGNED. The swept parameter (k active dims) is EXACTLY
  the parameter each fidelity primitive experiences (top-k WTA applied directly to
  the code the fidelity fns consume). No routing/partition indirection.
- `discriminating_fraction`: >= 0.30 required. Predicted per-point placement:
  semantic recall expected to rise across k (>=2 of 6 points in [0.30,0.70] band);
  algebraic acc at reporting_M placed adaptively so dense ~0.7 with sparse spread
  (>=2 points in band). Empirically verified in smoke (discriminator-fires gate);
  if smoke shows <0.30 in band on both axes -> MIDDLE_BAND (re-spec M / N_CONCEPTS).
- `composition_edges`: encoder-output (int8 sparse bipolar) -> hdlab.binding.bind
  input (real float32); SHAPE_MATCH (cast int8->float32, same N_DIM). encoder-output
  -> BGE-gold comparison: cross-space, handled by RSA (no direct-cosine adapter
  needed; RSA IS the adapter).
- `positive_control_arms`: dense (k=1024) arm is the reference; single-bind
  `roundtrip_cos@M1 ~ 1.0` sanity-confirms the HRR primitive is invoked correctly
  at THIS regime (N=1024 real bipolar-sparse codes), tolerance 0.10 vs 1.0.

## HYPOTHESIZED numbers (all tagged; none are data)
- intersection(KB first 200K, BGE names) = 16382  MEASURED@probe 2026-07-04 stdout.
- clean bundle-cleanup @M8, random proxies = 1.00 all k  MEASURED@probe (why M
  pushed to [24..96] for real codes).
- clean bundle-cleanup @M64, random proxies: k8=0.75 k20=0.89 k64=0.75 dense=0.85
  MEASURED@probe (modest spread on RANDOM codes; real correlated codes expected to
  spread more).
- semantic recall@10 monotone-increasing in k  HYPOTHESIZED@this prereg (Hebbian-
  signal-retention argument).
- optimal k UNKNOWN -- reported from smoke, not pre-baked.
