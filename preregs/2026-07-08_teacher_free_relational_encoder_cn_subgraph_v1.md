# Pre-reg: teacher-free relational encoder on the ConceptNet subgraph (decisive CPU test)

- **Anchor:** `teacher_free_relational_encoder_cn_subgraph_v1`
- **Cell:** `experiments/exp_teacher_free_relational_encoder_cn_subgraph_v1.py`
- **Date:** 2026-07-08
- **Author:** exp_dev
- **Queue target:** `remote_cpu_queue` (CPU-only; no GPU needed per the decisive-test note). Smoke ran LOCAL.
- **Source note:** `notes/research_teacher_free_relational_encoder_objective_2026-07-08.md` (course-corrected framing: repulsion-is-load-bearing + graph-relational-discriminability-on-CN-subgraph; BGE is a NON-GATING reference line, NOT a pass/fail bar).

## Prior-work check (substrate-KB concept-query, mandatory)
`bash tools/substrate_query.sh "teacher-free encoder contrastive relational graph neighbor InfoNCE repulsion uniformity concept discriminability"` -> top hit cosine=0.3037 ("Discriminator reachability", a generic prereg field name, NOT substantively related); all other hits < 0.30. No prior teacher-free graph-contrastive encoder cell exists; genuinely novel. One relevant confound surfaced (research_drill_p9, 2026-06-10): ConceptNet concept-words carry lexical/orthographic priors that can masquerade as relational structure -> CONTROLLED here by the `ARM_RANDOM_INIT` lexical-floor arm + a lift-over-floor HARD_PASS gate.

## Objective (teacher-free; NO BGE in any loss)
Learn discriminative concept codes from the substrate's OWN ConceptNet relational graph with NO external teacher. Positive-pair signal = graph relational-neighbors (Rank 3) OR encoder-perturbation views (Rank 2 / SimGRACE). Explicit REPULSION term (in-batch InfoNCE uniformity + VICReg covariance/variance) is MANDATORY (Rank 1; the load-bearing, degree-agnostic ingredient per 3 convergent lit-scans: Pehlevan-Chklovskii anti-Hebbian, Barlow redundancy-reduction, Wang-Isola uniformity). Surface features = deterministic hashed char-trigram bag (substrate-native V1 featurization; no lexical semantics injected).

## Arms
- `ARM_GRAPH_REPULSION` [PRIMARY]: InfoNCE over graph-neighbor positives (in-batch negatives = repulsion) + VICReg covariance+variance repulsion.
- `ARM_NO_REPULSION` [CONTROL/ablation]: alignment ONLY over graph-neighbor positives (mean 1-cos; NO negatives, NO covariance). MUST COLLAPSE/CROWD (proves repulsion is load-bearing -- synthesis R1, highest-P claim).
- `ARM_SIMGRACE_REPULSION` [SECONDARY positive arm]: InfoNCE over encoder weight-perturbation views (degree-agnostic) + VICReg repulsion.
- `ARM_RANDOM_INIT` [FLOOR / p9 lexical-confound control]: untrained encoder on the same char-trigram features. Its Z quantifies how much assortativity is lexically accessible with NO learning.
- `ARM_BGE_REFERENCE` [NON-GATING reference line]: BGE-small embedding of node words (loaded from local HF cache; best-effort, never gates).

## Discriminators (telemetry-sensitive; NOT analytically pinned)
1. **Embedding assortativity Z-score** (Newman-modularity analog): `M_true = mean over induced edges of cos(z_u,z_v)`; null = mean edge-endpoint cosine under a DEGREE-PRESERVING (configuration-model / Chung-Lu) null, `k_rewire` draws; `Z = (M_true - null_mean)/null_std`.
2. **Off-target mean-pairwise-cosine**: mean cosine over random NON-EDGE node pairs (lower = better separated / less crowded).
3. **Dimensional-collapse guard**: fraction of variance in top-1% of code dims (>= 0.90 == collapsed) + effective rank (participation ratio).

Telemetry-sensitivity self-test (MANDATORY, always runs): planted-community synthetic -> structure-respecting emb gives Z=130.8; random emb Z=-0.51; perturbing 50% of rows drops Z to 20.7 (sensitivity, not analytic pin); dimensional collapse detected (frac_top=0.999) while well-spread structure NOT flagged (frac_top=0.077). MEASURED@data/exp_*_selftest/metrics.json.

## Pre-reg bands (per source note; applied to `ARM_GRAPH_REPULSION` primary, `ARM_SIMGRACE_REPULSION` secondary)
- `HARD_PASS` (joint): Z_primary >= 2.0 (note lower HP bound, 2-3 sigma) AND lift_over_lexical_floor (Z_primary - Z_random_init) >= 2.0 AND off-target-cosine margin vs no-repulsion control >= 0.03 AND no dimensional collapse AND ablation_collapses (control crowds/collapses).
- `HARD_FAIL`: Z_primary < 1.0 OR off-target margin vs control <= 0 OR lift_over_floor <= 0.
- `MIDDLE_BAND`: otherwise (e.g. 1.0 <= Z < 2.0, or margins between fail and pass).
- **Load-bearing ablation gate:** `ARM_NO_REPULSION` MUST collapse/crowd (dim-collapse OR off-target cosine >= 0.5 OR Z < 1.0). If the control does NOT collapse, that is itself reported honestly (graph attraction alone would then be sufficient, contradicting the brain-grounding).
- **p9 lexical-confound gate:** HARD_PASS requires the LEARNED lift (>= 2 sigma beyond the random-init lexical floor), not merely absolute Z. `lexical_leak_warning` (floor Z >= 1.5) is a REPORTED diagnostic, not a blanket blocker -- the lift gate is the rigorous control.

Rationale for band choice: BGE is NOT a pass/fail bar (per course-correction: graph-only is not expected to beat BGE across the board; the whole-KB stays inconclusive; only the CN subgraph clears the gate). The gate is on intrinsic discriminability (assortativity-Z + separation) + the load-bearing ablation, exactly the note's "cheap decisive test".

## SCHEMA-VET fields
- `cardinality_ok`: true. `EXPECTED_N_UNITS = n_seeds` (smoke 3, full 5). Verdict emits `HARD_FAIL_CARDINALITY_BREACH_META_RULE_H` if fewer seeds complete.
- `arms_differ_verified`: true (SHA-256 hash of each arm's final embedding asserted distinct at every seed).
- `final_metrics_atomicity`: `tmp_replace` (via `_seed_checkpoint.write_metrics` + `os.replace` crash path; per-seed `write_partial`).
- `crlb_n/a`: "No closed-form noise floor; the discriminator is an empirical Z-score against a per-run degree-preserving null. Reachability is verified empirically -- the discriminator-selftest shows structure-respecting emb clears Z>=2 and random emb does not."
- `discriminator_reachability`: true (selftest demonstrates the HARD_PASS threshold is reachable by structure-respecting embeddings and unreachable by random ones).
- `baseline_in_band`: the controls (`ARM_NO_REPULSION`, `ARM_RANDOM_INIT`) are NOT accuracy-baselines that can saturate in [0,1]; Z is unbounded. Discriminator-fires check = learned lift > 0 above the random-init floor (verified at smoke: lift = 152.9 sigma).
- `calibration_check`: `adaptive_with_discriminator_gate` -- the degree-preserving null is recomputed per run from the induced degree sequence; the discriminator-selftest verifies it still fires.
- `cell_chunked`: false. Justification: fast CPU cell (smoke 57.6s / 3 seeds; full est. 10-25 min / 5 seeds), well under the multi-hour runner-zombie risk profile; the metric is a CROSS-SEED statistic so seeds aggregate in one cell; per-seed `write_partial` gives restartability + start-marker + crash-diagnostic + heartbeat instrument silent death.
- `start_marker_written`: true. `crash_diagnostic_present`: true (Exception -> CELL_CRASHED metrics + traceback; `except SystemExit: raise` before `except Exception`; no BaseException/bare-except -- grep gate clean). `heartbeat_present`: true (per-arm-epoch `_heartbeat.jsonl` via `_cell_heartbeat.emit_heartbeat`). `defensive_error_checking`: passed_all_4_patterns.
- `progress_logging`: `print_flush_true` (all `_log` + interior epoch-progress lines flush; interior epoch log every epochs//5). Applies for FULL timeout_s >= 1800.
- `run_mode`: explicit `--run-mode {self_test,smoke,full}` (default full) + `--self-test`/`--smoke` bare-flag compatibility. RUN_MODE verified post-run (smoke metrics.json run_mode=smoke, 7992B).

## Compute architecture
- Class: **(b) sequential-CPU with justification.** The decisive-test note explicitly specifies CPU-only, no GPU. Wall < 25 min at full. Training uses vectorized torch matmuls (batched, not python-loop-over-phase-points); the per-run degree-preserving null is a vectorized numpy operation. No GPU speedup is warranted for a minutes-scale CPU pilot; GPU dispatch would violate the note's "no GPU dispatch" scoping.
- Storage strategy: `no_storage / no_composition` (encoder-training cell; not a memory/composition cell).
- Sweep axis: none (fixed regime; seed axis only) -> cardinality via EXPECTED_N_UNITS = n_seeds.

## Functional requirements (gate E)
1. Teacher-free positive signal from the graph -> graph-neighbor InfoNCE (Rank 3) + SimGRACE perturbation views (Rank 2). No primitive existed; newly designed here.
2. Explicit anti-collapse repulsion -> InfoNCE in-batch uniformity + VICReg covariance/variance (Rank 1; brain-grounded).
3. Discriminability measurement without a teacher -> assortativity-Z vs degree-preserving null + off-target-cosine (reuses the substrate-self-mapping modularity-Z idea + whitening-revival off-target-cosine diagnostic).
4. Lexical-confound control -> random-init floor arm + lift-over-floor gate (addresses p9).

## HONEST density caveat (material; for Director reconciliation)
The raw `data/substrate_index/concept/relations.jsonl` CN graph is SPARSER than the note's cited figure: MEASURED@disk 133,284 nodes, 173,751 CN-CN edges, **median degree 1.0, mean 2.61, 10.2% at deg>=5**, largest connected component 110,340 nodes (82.8%). This is the RAW relations file. The note's "median degree 6.0, 99.99% >= 5" is for the KB-INGESTED `concept_relations` graph in `entities.jsonl` -- a different/denser construction. This cell operates on relations.jsonl directly and therefore snowballs within the giant component + extracts the 2-core (every node degree >= 2) so relational-neighbor two-view positives are constructable. Induced 2-core at smoke: 2143 nodes / 6240 edges / median degree 3.0 / mean 5.82 / 100% deg>=2. Full targets ~12,000 nodes. The verdict holds on this 2-core; the graph-relational objective is validated where degree>=2 holds. Whether it extends to the median-1 tail is OUT OF SCOPE (the note itself scopes this to the dense subgraph only; the degree-1 tail falls below the Rank-3 hard floor of degree>=2, where SimGRACE -- ARM_SIMGRACE_REPULSION, degree-agnostic -- is the fallback).

## Smoke result (LOCAL; MEASURED@data/exp_teacher_free_relational_encoder_cn_subgraph_v1_smoke/metrics.json)
3 seeds [7,13,17], n_nodes=2143 2-core, 57.6s wall, verdict **HARD_PASS**:
- ARM_GRAPH_REPULSION Z=183.17 (min 163.45), off-target cosine 0.004, not collapsed.
- ARM_NO_REPULSION Z=24.89, off-target cosine 0.957 (CROWDED) -> ablation_collapses=True. Repulsion drops off-target cosine 0.957 -> 0.004 (margin 0.953, load-bearing R1 confirmed, confound-free).
- ARM_RANDOM_INIT floor Z=30.24 (lexical); lift_over_lexical_floor = 152.9 sigma.
- ARM_SIMGRACE_REPULSION Z=38.85, off-target cosine ~0 (degree-agnostic positive arm works).
- ARM_BGE_REFERENCE (NON-GATING) Z~109, off-target cosine 0.558. Reference observation: on this CN 2-core the teacher-free graph-repulsion code has HIGHER assortativity-Z (183 vs 109) AND far better separation (off-target cosine 0.004 vs 0.558) than BGE -- BGE's 0.558 is the crowding the note describes. Per the course-correction this is a REFERENCE line only, on ONE subgraph, NOT a pass/fail claim; graph-only is not expected to beat BGE across the board.

## FULL dispatch (pause-gated; hand-off)
`remote_cpu_queue`, n_nodes=12000, 5 seeds, epochs=100, timeout 3600s. CPU-only. No push needed to origin (queue_add.sh is SCP-based). See exp_dev completion report for the exact queue_add.sh command.
