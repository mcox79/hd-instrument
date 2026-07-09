# Pre-reg: LOCAL-neighborhood-scoped multi-hop chain cleanup (reader WIN-CELL v2)

- **Anchor:** `grounding_multihop_local_chain_index_v2`
- **Cell:** `experiments/exp_grounding_multihop_local_chain_index_v2.py`
- **Filed:** 2026-07-09 (exp_dev)
- **Target queue:** `overnight_queue` (GPU; gpu_runner_0). FULL = 3 seeds.
- **Builds on:** `exp_grounding_multihop_decisive_win_v1` (MIDDLE_BAND_PARTIAL_CROSSING;
  `data/exp_grounding_multihop_decisive_win_v1/metrics.json`) + `exp_grounding_multihop_perhop_cleanup_gate_v1`
  (VET-landed Stage-4 primitives reused VERBATIM) + drill
  `notes/research_reader_load_reduction_feasible_dim_win_path_2026-07-09.md`.

## Question

Does restricting the per-hop cleanup candidate set to the current node's LOCAL graph neighborhood (mean out-degree
~6.65) -- instead of the full global vocabulary (n_nodes ~4440) -- collapse the load and cross the multi-hop WIN
bar at a MODEST dimension (~2k, NOT the naive 79k the global-count bound demanded)?

## Thesis (from the drill + the landed VET)

The multi-hop reader is LOAD-limited, not semantic-floor-limited (VET atom MULTIHOP_READER_IS_LOAD_LIMITED). The
landed diagnostic backed out `dim_needed = n_nodes / 0.056 = 4440/0.056 = 79286`
(MEASURED@data/exp_grounding_multihop_decisive_win_v1/metrics.json:gates.df_over_n.dim_needed_resonator), i.e. it
charged the cleanup crosstalk against the FULL 4440-node vocabulary. A KG walk only ever has to discriminate the
true target from the LOCAL neighborhood of the current node. Charge the resonator against ~6.65 instead of 4440
and `dim_needed` collapses ~670x to `6.65/0.056 = 119`
(THEORETICAL@D_f/N<=0.056 per arXiv:1906.11684, CITED). The fix is architectural, not dimensional.

## GLOBAL-vs-LOCAL cheap pre-test (arm-0)

Instrumented in the self-test + reported in every run (`gates.df_recompute`): the landed harness cleanup does
`score = _l2t(pred) @ Z.t()` (Z = [n_nodes, d]) then `argmax` over ALL nodes => GLOBAL. `dim_needed` backs out to
`n_nodes/0.056` exactly. CONFIRMED GLOBAL. Recompute with local D_f = mean_out_degree collapses `dim_needed`
(measured collapse_factor: 273x on the real subgraph at smoke, 668x in the self-test).

## Arms (4; PAIRED: identical chains + identical learned codes Z + identical roles + identical seeds; the ONLY
difference is the cleanup candidate set, so GLOBAL-vs-LOCAL is a clean within-dim attribution)

1. `NO_CLEANUP` -- must-fail control. Raw HRR accumulation carried forward; top-1 global readout. MUST collapse
   at reach>=2 (anti-saturation).
2. `GLOBAL_CLEANUP` -- baseline = current landed behavior. Per-hop top-1 snap over the FULL codebook. The
   reference the LOCAL arm must beat.
3. `LOCAL_CLEANUP` -- THE win lever. Per-hop top-1 snap restricted to the current node's out-neighbors (hop-0 =
   the TRUE start, whose adjacency is legitimately known in a KG walk). Errors propagate honestly.
4. `LOCAL_DECORR` -- LOCAL + light decorrelation (subtract the local candidate centroid before scoring; removes
   the shared semantic component among neighbors). Targets the residual within-neighborhood aliasing.

**HP_SCOPE:** WIN gate applies ONLY to `{LOCAL_CLEANUP, LOCAL_DECORR}`. `NO_CLEANUP` = must-fail control;
`GLOBAL_CLEANUP` = baseline reference (reported, not gated).

## Metric

**Primary (gated):** `reach@d` = TOP-1 COMMIT accuracy at hop d (committed node == true target). Honest chaining
metric -- the chain carries exactly one node forward, so top-1 is what propagates; also avoids the small-
candidate-set inflation `hit@K` causes for local arms (when |neighbors| <= K, hit@K degenerates to trivial).
**Secondary (diagnostic, NOT gated):** `hit@10` (global top-10 for continuity with the landed PLAIN@2=0.106).

## Pre-registered WIN bands (picked BEFORE the FULL run)

- **HARD_PASS_LOCAL_WIN** = LOCAL arm `reach2 >= 0.60` AND `reach3 >= 0.35` AND `slope_flatten >= 0.40`, at MODEST
  dim (2048 <= ~5k). `slope_flatten` = relative (log-decay) flatten vs NO_CLEANUP (level-invariant). Level-lift
  alone is NOT a win -- the decay must flatten (VET's key requirement).
- **HARD_FAIL_SEMANTIC_FLOOR** = best LOCAL `reach2 < 0.60` AND `local_aliasing_frac >= 0.50` AND
  `aliasing_excess_over_base >= 0.15` (the residual is DISPROPORTIONATELY same-relation sibling ambiguity --
  genuine graph confusability, not a base-rate artifact -> no code/dim fix helps; it IS a semantic floor).
- **MIDDLE_BAND_PARTIAL** = LOCAL lifts materially over GLOBAL but misses a WIN band and the miss is not a genuine
  semantic floor.
- Guards: `INCONCLUSIVE_HOP1_ABSENT` (GLOBAL@1 < 0.08); `INCONCLUSIVE_BASELINE_DID_NOT_FAIL` (NO_CLEANUP@2 does
  not collapse).

### Band values
`HOP1_PRESENT=0.08` `BASE_IN_BAND_HI=0.95` `BASE_COLLAPSE_ABS=0.10` `BASE_COLLAPSE_FRAC=0.50`
`WIN_REACH2=0.60` `WIN_REACH3=0.35` `WIN_SLOPE_FLATTEN=0.40` `ALIAS_FLOOR_HI=0.50` `ALIAS_EXCESS_MIN=0.15`
`HIT_K=10` `MAX_REACH=4`.

## Smoke result (PROVISIONAL -- mechanism-story HELD until landed-VET)

n=1525, dim=512, 2 seeds (seeds 7,13), CPU, 10.8s. All numbers
MEASURED@data/exp_grounding_multihop_local_chain_index_v2/metrics.json (smoke run, pre-FULL):
- NO_CLEANUP @1=0.164 @2=0.017 (collapses=True) -- must-fail control fires.
- GLOBAL_CLEANUP @1=0.164 (in_band=True) @2=0.042 @3=0.014.
- LOCAL_CLEANUP @1=0.491 @2=0.146 @3=0.052, `flat=0.362`. LOCAL_DECORR @1=0.491 @2=0.141.
- `local_lift2(vs GLOBAL)=0.104`; `local_aliasing_frac=0.847` `base_rate=0.504` `excess=0.343`;
  `df.collapse=273x`, `local_load/hop=0.0109 << 0.056`.
- Smoke verdict = HARD_FAIL_SEMANTIC_FLOOR. Directionally the LOCAL count-tax fix WORKS decisively (reach1 3x,
  reach2 +0.104, decay 36% flatter) but does not clear the ambitious WIN bar at smoke scale; the residual is
  genuine same-relation sibling aliasing (34pp over base rate). FULL upgrades the ENCODER (dim 4x, epochs 2.3x,
  feat 2x) -- the binding constraint (single-hop LOCAL=0.49) -- so the canonical run either crosses the bar or
  decisively locates the wall. Both outcomes are gold.

## SCHEMA-VET mandatory fields

- `cardinality_ok`: true. EXPECTED_N_UNITS = n_seeds = 3 (no sweep axis; hop-depth d in {1..4} is asserted per
  arm per seed via ARM_DEPTH_CARDINALITY_BREACH).
- `arms_differ_verified`: true (per-chain top-1-commit signatures; LOCAL/LOCAL_DECORR asserted != NO_CLEANUP AND
  != GLOBAL_CLEANUP, else RuntimeError ARMS_MUST_DIFFER_META_RULE_AF). `arms_differ_exempted`: none.
- `final_metrics_atomicity`: `tmp_replace` (write_metrics + os.replace).
- `crlb_floor_computed`: top-1 chance floor = 1/n_nodes ~ 0.0002 at n=5000. `crlb_formula_reference`:
  `chance_top1 = 1/n_nodes`; local load `mean_out_deg/dim = 6.65/2048 = 0.0032 << 0.056` (THEORETICAL@
  arXiv:1906.11684) so dim is NOT the local constraint. `discriminator_reachability`: true (WIN reach2>=0.60 >>
  chance and above the local load floor). `crlb_n/a`: the semantic-floor branch (measured aliasing, not a closed-
  form floor).
- `baseline_in_band`: GLOBAL_CLEANUP@1 in (0.05,0.95) verified per run (smoke MEASURED 0.164). NO_CLEANUP@2
  collapse verified (anti-saturation must-fail control; smoke MEASURED 0.017).
- `calibration_check`: `adaptive_with_discriminator_gate` (baseline-collapse + baseline-in-band recomputed
  empirically per run; paired per-chain top-1 commits).
- `defensive_error_checking`: `passed_all_4_patterns` -- start_marker_written true; crash_diagnostic_present true
  (except SystemExit/KeyboardInterrupt raise BEFORE except Exception; no BaseException / no bare except -- grep
  gate CLEAN); heartbeat_present true (train loop emits _heartbeat.jsonl via _cell_heartbeat); cell_chunked false
  (per-seed loop with write_partial + per-seed failure-class instrumentation; 3 seeds, single cell -- runner-death
  loses at most the in-progress seed, prior seeds checkpointed via write_partial).
- `run_mode` default = `full` (defensive; explicit `--self-test`/`--smoke` for the reduced modes). RUN_MODE
  VERIFICATION post-dispatch: orchestrator confirms landed metrics `run_mode==full`, size, elapsed.
- `progress_logging`: `print_flush_true` (line-buffered stdout + per-epoch/per-seed flush prints + heartbeat;
  required as timeout_s >= 1800).

### The 5 composition/sweep gates (§15)
- **Gate A (effective vs nominal):** `sweep_alignment_verdict: ALIGNED`. No parameter sweep; each primitive
  experiences its nominal config. The candidate set the cleanup scores against is the EFFECTIVE discriminator
  variable and it is exactly what the arms vary (GLOBAL=n_nodes, LOCAL=mean_out_degree) -- measured + reported.
- **Gate B (discriminating band):** `discriminating_fraction: 1.0`. The discriminator is LOCAL-vs-GLOBAL top-1
  reach; smoke MEASURED LOCAL 0.49/0.15/0.05 and GLOBAL 0.16/0.04/0.01 across hops 1-3 -- all in the (0.01,0.60)
  discriminating band, none saturated.
- **Gate C (shape compatibility):** all arms consume the same [C,d] bound-prediction and score against [.,d]
  codes; only the candidate SET differs. `verdict: SHAPE_MATCH` for every arm edge.
- **Gate D (positive control at test regime):** GLOBAL_CLEANUP reproduces the landed cell's cleanup behavior AT
  THIS regime (same encoder/roles/subgraph loader reused VERBATIM from the VET-landed Stage-4 cell). The landed
  PLAIN cleanup and this GLOBAL_CLEANUP are the same code path over the full codebook; hit@10 is reported for
  numeric continuity. `positive_control_arms: [GLOBAL_CLEANUP reproduces landed global cleanup]`. Regime-
  extension: SHAPE_MATCH (same subgraph, same encoder family, top-1 vs hit@10 metric change documented).
- **Gate E (functional requirements):** (1) multi-hop chain traversal -> the reused chain primitive; (2) per-hop
  disambiguation among candidates -> cleanup (global vs local candidate set); (3) local candidate construction ->
  build_nbr_table (graph adjacency, legitimately known in a KG walk); (4) residual local aliasing measurement ->
  local_error_decomposition with same-relation base-rate control.

## Compute architecture

- **Class: (c) mixed with justification.** Encoder training = batched GPU matmul. Per-hop cleanup = batched GPU
  (global matmul [C,n]; local scoring chunked einsum [chunk,Dmax,d]). Sequential dependency exists ACROSS the 4
  hops (hop h's candidate set depends on hop h-1's commit) -- a GENUINE chain dependency, only 4 steps, each fully
  batched over all C chains. Not a batching flaw.
- **Storage strategy: SHARDED** (each node its own code Z row; no bundling). Compositional chain cell -> sharded
  per the STORAGE-STRATEGY law.
- **Device:** cuda if available else cpu (runner does not pass argv; auto-resolves to cuda on GPU node).

## Honesty

Real CG'd teacher-free relational learned codes over the REAL ConceptNet typed subgraph; top-1 commit fidelity;
NO language understanding claimed. Local-scoping is LEGITIMATE for KG traversal (adjacency known at each step; the
VSA analog of HippoRAG's graph-index-in-front-of-dense-embeddings) and NOT oracle-cheating: the model still must
pick the RIGHT neighbor among ~6.65 using the role-bound query; the target identity is never handed to it; wrong
commits propagate to wrong candidate sets. Teacher-free, ASCII-only.

## Number tags
- `dim_needed=79286` MEASURED@data/exp_grounding_multihop_decisive_win_v1/metrics.json:gates.df_over_n.dim_needed_resonator
- `D_f/N<=0.056` THEORETICAL@arXiv:1906.11684 (CITED, re-verified in the drill)
- `mean_out_degree~6.65` MEASURED@data/exp_grounding_multihop_decisive_win_v1/metrics.json:subgraph_meta.mean_degree
- smoke LOCAL reach2=0.146, aliasing_excess=0.343 MEASURED@data/exp_grounding_multihop_local_chain_index_v2/metrics.json (smoke)
- WIN bands reach2>=0.60 / reach3>=0.35 / flatten>=0.40 HYPOTHESIZED@this prereg (Director WIN spec, ambition-first)

## Dispatch

```
bash tools/orchestrator/queue_add.sh overnight_queue grounding_multihop_local_chain_index_v2 experiments/exp_grounding_multihop_local_chain_index_v2.py preregs/grounding_multihop_local_chain_index_v2.md 1800
```

Timeout 1800s: smoke wall 10.8s (n=1525,dim512,2seed); FULL scales dim 4x + epochs 2.3x + seeds 1.5x + n 3x;
`ceil(1.5 * 10.8 * (4440/1525)^1.5 * 1.5) ~ 120s` on CPU-equivalent, far less on GPU -- 1800s is generous headroom
(well under the 14400 cap). exp_dev hands off; orchestrator ships (SCP) + owns REMOTE VERIFY (run_mode=full, exit-5
referent check).
