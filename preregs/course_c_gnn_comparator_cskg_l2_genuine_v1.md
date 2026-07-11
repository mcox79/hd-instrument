# Pre-reg: course_c_gnn_comparator_cskg_l2_genuine_v1

Phase-2 Anchor 4 -- same-split OPAQUE GNN comparator (CALIBRATION anchor, NOT on the reasoning critical path).

Cell: `experiments/exp_course_c_gnn_comparator_cskg_l2_genuine_v1.py`
Author: exp_dev (hdi_exp_dev)
Date: 2026-07-11
Trigger: `notes/exp_dev_handoff_research_reasoning_realization_gap_closure_prep_2026-07-11.md` (Anchor 4)
Pause state at authoring: CLEAR (data/orchestrator_paused.flag absent)

Prior-work check (substrate_query, cosine>0.30): top hits `graph_link_prediction_per_edge_keying_v1`
(MIDDLE_BAND, mean_auc=0.970 @ N=4096) and `graph_link_prediction_v1` (HARD_FAIL) are substrate-native
AUC link-DISCRIMINATION probes on the Hebbian W -- a DIFFERENT task/metric/graph/mechanism. This cell is
NOVEL: the first opaque path-aggregation GNN (NBFNet-lite) on the IDENTICAL CSKG L2-genuine filtered-ranking
harness the glass-box map-builder uses. NOT a rediscovery.

## Purpose

Bank a best-in-class OPAQUE reference number (filtered hits@1/hits@10/MRR + degree-stratified) MEASURED on
the SAME genuine-L2 held-out CSKG split the glass-box map-builder reports on, so the glass-box result can be
graded against an opaque baseline on OUR graph rather than a borrowed FB15k-237 analogy (different graph,
1-hop vs 2-hop, different difficulty).

The glass-box map-builder FULL landed 2026-07-11 14:37Z as `INCONCLUSIVE_GEOMETRY_READOUT_UNDERFIT`
(geom_best hits@10=0.0227 aggregate, HIGH=0.0581, POP=0.1746, ORACLE did not fire = readout under-fit).
That is exactly why a measured opaque reference matters. This comparator is banked now; the glass-box-vs-
comparator grading happens downstream once the glass-box ladder (Anchors 1-3) settles.

## CALIBRATION CAVEAT (attach to any external framing)

Per research handoff HEADLINE point 3: the reference banked here is TransE-tier ABSOLUTE for a HARDER 2-hop
task, NOT NBFNet-on-FB15k237-tier. NEVER market as SOTA. Recorded in metrics.json `calibration_caveat`.

## Apples-to-apples guarantee (load-bearing)

The cell IMPORTS the map-builder's OWN split + metric functions VERBATIM (verified at author time: the
imported `extract_l2_genuine / stratify_by_tail_degree / build_true_by_hr_int / filtered_hits_from_scores /
pop_hits / per_stratum_hits / per_stratum_pop / _sig / build_cskg_core_triples / Graph / build_ids /
mine_rules` are the SAME objects as in `exp_course_c_map_builder_cskg_l2_genuine_v1`). FULL split params are
COPIED verbatim from the map-builder FULL_CFG (cskg_max_lines=0, k_core=12, cskg_max_nodes=0, min_support=10,
min_conf=0.10, n_eval=6000, MAX_RULES_PER_HEAD=50, HUB_CAP=60000, seeds=[7,17,23]).

SPLIT-IDENTITY ASSERT (FULL only): after reconstructing the split per seed, the cell recomputes the POP rank
vector over the SAME L2-genuine held-out queries + SAME filtered candidate set and hashes it
(`_sig(pop_rank_vec)`); it MUST equal the map-builder's landed `arm_sigs[seed].BASELINE_POP` (a deterministic
bit-identical witness), AND N / n_rel / n_l2_genuine must match. Mismatch -> HARD_FAIL_SPLIT_IDENTITY_BREACH
(fail closed). Referent: `MEASURED@data/exp_course_c_map_builder_cskg_l2_genuine_v1/metrics.json`.

## Arms (PAIRED on the same held-out split + candidate set + strata)

- `GNN_TRAINED`   NBFNet-lite (generalized Bellman-Ford, DistMult relational messages, inverse edges,
                  boundary re-injection), trained with filtered cross-entropy. THE opaque reference arm.
- `GNN_UNTRAINED` identical architecture, random init, no training. Control: training MUST lift the arm.
- `BASELINE_POP`  POP_RELFREQ frequency incumbent (imported `pop_hits`). Apples-to-apples bar + the
                  split-identity witness.

## Primary metrics

Filtered hits@1, hits@10, MRR on the L2-genuine held-out subset; per-degree-stratum (low/mid/high by
gold-tail global degree tertile) hits@10; GNN vs POP reported per stratum. All via the imported harness.

## Pre-reg bands

### This comparator's OWN pass criterion (what THIS cell's verdict decides)

Per the handoff Contract: the comparison is glass-box-vs-comparator, so the comparator's own pass is "did it
train + produce a VALID ranking number on the correct split." Concretely:

- `COMPARATOR_REFERENCE_BANKED` (success): split_identity_ok (POP sig == landed, FULL) AND training_converged
  (final train loss < initial * 0.85) AND non-degenerate ranking (per-query GNN score std > 1e-6) AND arms
  differ (GNN_TRAINED sig != GNN_UNTRAINED sig).
- `HARD_FAIL_SPLIT_IDENTITY_BREACH`: recomputed POP sig != landed map-builder sig -> split is not the
  glass-box's; reference invalid.
- `HARD_FAIL_TRAINING_DEGENERATE`: training did not reduce the loss OR scores degenerate -> no valid ranking.

### Anchor-4 bands (for the LATER glass-box comparison -- RECORDED here, NOT gated by this cell)

Lifted verbatim from the handoff. These grade the glass-box's best result against THIS comparator's number
and are owned downstream (verdict_handler), NOT by this comparator:

- HARD-PASS: glass-box best result reaches >=85% of the same-split GNN comparator's score -- confirms the
  external ~90-95% precedent transfers to this task/graph.
- MIDDLE-BAND: 60-85% -- gap larger than external precedent suggests; investigate architecture-dependence
  vs fixable glass-box gap.
- HARD-FAIL: <60% -- possible genuine architecture-dependent expressiveness requirement; escalate to
  strategy before further glass-box tuning.

The cell RECORDS `gates.glassbox_vs_comparator` (ratio_glassbox_over_comparator using the landed map-builder
number) as INFORMATIONAL context with the calibration caveat attached; it does NOT gate on it.

## Compute architecture

class: (a) batched-GPU. Batched generalized Bellman-Ford: per query-batch the per-layer relational message
is a single (B, 2E, dim) gather-multiply then an index_add scatter to (B, N, dim); scores are (B, N),
NEVER an [N x N] map (the OOM trap at N~25.7k). Eval scores accumulate on CPU host RAM. Symbolic split build
(mine_rules / extract_l2_genuine / pop_hits) is sequential-CPU (combinatorial, no matmul). Storage: SHARDED.
device=auto (cuda on the GPU host); local = NO EXECUTION (no-local-smokes lock).

## Memory discipline (this GNN family OOM'd 3x on the shared 8GB card w/ BOINC ~1.2GB)

- never materialize [N x N]; scores (B, N); eval scores on CPU.
- chunk query batches: b_train=6 (under autograd), b_eval=16 (no grad); dim=32, n_layers=3 -> the sole large
  device tile (B, 2E, dim) at FULL ~= 6 * 920k * 32 * 4B ~= 0.7GB/layer, autograd L=3 ~2.1GB + overhead;
  peak budgeted ~3-4GB < (8GB - BOINC 1.2GB).
- per-seed teardown: fresh model, explicit del of model+optimizer+edge tensors+eval scores,
  torch.cuda.empty_cache(), reset_peak_memory_stats; per-seed `peak_gpu_mem_mb` logged.
- MANDATORY >=2-seed REMOTE memory smoke at reduced-but-meaningful scale (`memsmoke` run mode: ~4000 nodes,
  2 seeds, real GPU train) BEFORE the FULL -- single-seed masks multi-seed accumulation. Dispatched as a
  separate GPU job (the 180s queue_add pre-gate smoke is tiny SYN only; cannot host a full-scale memory job).

## Run modes

- `self_test`: 1 planted SYN_COMPOSITIONAL corpus; trained GNN vs untrained control vs POP; fast branch,
  exits 0, does NOT trigger a CSKG run (learns from the prior ladder self-test-gate bug). Fits 180s pre-gate.
- `smoke`: 2-seed planted SYN; validates multi-seed loop + metrics write. Fits 180s pre-gate.
- `memsmoke`: 2-seed REDUCED CSKG (~4000 nodes); real GPU train; logs peak_gpu_mem_mb; the mandatory
  memory smoke. Split-identity NOT asserted (reduced slice != FULL split). Separate GPU dispatch.
- `full`: 3-seed FULL CSKG (25752 nodes); identical-split params; split-identity ASSERTED; banks the number.

Run-mode keyed off flags (--self-test / --smoke) then HDLAB_EXP_NAME suffix (`_memsmoke` -> memsmoke), else
full. Also supports `--seeds 7` for single-seed process-isolated dispatch if multi-seed accumulation is ever
observed at FULL scale.

## Self-test (scale-invariant discriminator-fires proof)

On planted SYN_COMPOSITIONAL (rA(p,m)&rB(m,t)=>rC(p,t), uniform non-popular tails) through the IDENTICAL
split+metric code path: L2-genuine extraction non-empty; trained NBFNet-lite hits@10 >= 0.25; trained -
untrained hits@10 >= 0.10 (training is the lever); training converged; arms differ. VacuousSmokeError if the
UNTRAINED control already clears the trained bar.

## SCHEMA-VET fields

- cell_chunked: false (multi-seed in-process with per-seed teardown + leak-guard, matching the proven
  map-builder pattern on this identical graph; --seeds single-seed fallback available).
- start_marker_written: true
- crash_diagnostic_present: true (Exception -> CELL_CRASHED metrics.json + traceback; SystemExit/KI re-raised)
- heartbeat_present: true (_heartbeat.jsonl per seed / per training epoch)
- defensive_error_checking: passed_all_4_patterns
- final_metrics_atomicity: tmp_replace (write_metrics tmp + os.replace; write_partial per seed)
- arms_differ_verified: true (GNN_TRAINED vs GNN_UNTRAINED sigs)
- cardinality_ok: true (EXPECTED_N_UNITS = n_seeds; HARD_FAIL_CARDINALITY_BREACH_META_RULE_H on shortfall)
- baseline_in_band: POP is the imported measured confound (landed FULL POP h@10~0.175); GNN_UNTRAINED is the
  anti-triviality null.
- discriminator_reachability: n/a -- comparator is a MEASUREMENT (no HARD_PASS threshold); validity-gated.
- crlb_n/a: filtered hits@10 chance floor ~ 10/n_candidates (THEORETICAL); POP is the real bar; no
  quantitative HARD_PASS threshold to be unreachable.
- calibration_check: default_ok_for_this_regime (split params copied verbatim + asserted via POP sig).
- positive_control_arms: the split-identity POP-sig assert reproduces the map-builder's BASELINE_POP
  bit-identically AT THE TEST REGIME (SHAPE_MATCH: same split, same candidate set, same harness).
- progress_logging: print_flush_true (line-buffered stdout; per-seed / per-epoch / per-eval flush).
- sweep_alignment_verdict: ALIGNED (no nominal-vs-effective mismatch; single ARM x seed axis).
- composition_edges: n/a (single GNN arm; no primitive-to-primitive composition).
- HP_SCOPE: COMPARATOR_REFERENCE_BANKED applies to GNN_TRAINED (validity) + split-identity + arms-differ; no
  chain-grade HARD_PASS floor on any arm.

## metrics.json required fields

verdict, verdict_msg, summary, elapsed_s (via write_metrics), run_mode, gates (reference: gnn_hits_at_1/10,
gnn_mrr, untrained_hits_at_10, pop_hits_at_1/10, pop_mrr, gnn/pop strat_hits_at_10 per stratum), per_seed
(arm_hits, strat_hits, split_identity, validity, train, peak_gpu_mem_mb, cskg_provenance), calibration_caveat,
split_referent, selftest, seed_failures.

## Dispatch

- Queue: overnight_queue (GPU; idle at authoring). Cell imports torch -> passes the GPU routing-sanity gate.
- Deps already on remote (map-builder FULL ran there today): exp_course_c_map_builder_cskg_l2_genuine_v1,
  exp_gt_induction_fb15k237_dense_v1, exp_cskg_dense_core_headroom_acceptance_v1. _seed_checkpoint auto-SCPs
  via queue_add Pattern 5.
- Sequence: (1) memsmoke (entry `..._memsmoke`, 2-seed reduced CSKG memory job) FIRST; verify green + peak
  GPU mem well under budget + no OOM. (2) THEN full (entry `..._v1`, 3-seed identical-split comparator).
- Timeouts: memsmoke ~3000s; full ~14400s (3 seeds x full-graph Bellman-Ford training @ ~15 epochs/seed +
  per-seed CSKG assembly, GPU shared with BOINC; conservative).
