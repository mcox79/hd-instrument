# grounding_encoder_sparse_block_binding_v1 -- sparse BLOCK-CODE binding so DG-expansion composes with bindobj

## Cell
`experiments/exp_grounding_encoder_sparse_block_binding_v1.py`

## Purpose (Stage-3 encoder fix)
Stage-2 (`grounding_encoder_clean_codes_retrain_v1`, MIDDLE_BAND) MEASURED that the binding-consistency
training objective is the active ingredient (BINDOBJ_ONLY recall 0.3076 -> 0.4234, Pareto-dominates) BUT dense
HRR circular-convolution binding is INCOMPATIBLE with sparse DG codes: dense-bind + DG-expand regressed to
0.25 (expand_gain = -0.2117) and reach stayed 1 for EVERY arm. Diagnosed root cause: dense circ-conv makes a
DENSE bound product that a hard per-block argmax then destructively collapses. This cell swaps the dense bind
for SPARSE BLOCK-CODE binding (block-local circular convolution, Frady/Kleyko/Sommer arXiv:2009.06734) matched
to the GSBC graded block code the DG sparsifier already produces -- sparsity-preserving BY CONSTRUCTION -- plus
a resonator/factorizer iterative cleanup (Hersche et al. arXiv:2303.13957) for multi-hop, composed with the
UNCHANGED binding-consistency objective. Question: does this restore reach>=2 on the SPARSE learned codes while
keeping recall >= 0.42 and codes sparse, flipping DG-expansion from net-NEGATIVE to net-POSITIVE?

## Prior-work check (SUBSTRATE-KB concept-query, USER-locked)
`bash tools/substrate_query.sh "sparse block code binding local circular convolution resonator factorizer chainable reach"`
top hits (cosine 0.34-0.36):
- `notes/research_to_exp_dev_clarifications_R1_R2_R5_R6_2026-06-05.md` (R2 block-local binding spec, Frady-Sommer)
- prior HARD_PASS `exp_substrate_sparse_resonator_blocklocal_K26_v1` (block-local sparse resonator recovers
  K4/K8=1.00 on RANDOM codebook vectors, N=1000 smoke).
NOVELTY: the block-local binding OPERATOR is prior-validated on RANDOM codebook factorizer-recall. This cell is
GENUINELY NOVEL in composing it with (a) LEARNED encoder codes from a trained ProjHead, (b) the binding-
consistency TRAINING objective, and (c) the real-code multi-hop REACH probe over a ConceptNet subgraph. It is
NOT a rediscovery of the random-codebook resonator result; it tests whether the operator survives being driven
by learned, structured codes under a training objective tuned against dense HRR. REUSED not rebuilt: the block-
local circ-conv algebra (equals `hdlab.binding.bind` on reshaped [.,kb,blk_l]; self-test asserts allclose), the
GSBC graded block STE (`exp_encoder_v11_gsbc_graded_sparse_v1_core._gsbc_code_from_z`), the Stage-2 dense arms +
reach/recall machinery.

## Arms (per model-seed) + HP_SCOPE
- A `DENSE_BINDOBJ` -- Stage-2 winner reproduce (dense HRR bind + bidirectional bindobj, dense code). CONTRAST
  FLOOR: must reproduce recall ~0.42, reach 1. HP_SCOPE: reproduce-only (NOT a chaining-gate arm).
- B `DENSE_BIND_DGEXPAND` -- Stage-2 regression reproduce (dense HRR bind + DG k-WTA expand + bindobj). The net-
  NEGATIVE DG-expansion baseline. HP_SCOPE: reproduce-the-regression control.
- C `BLOCK_BINDOBJ__g{0,1,2}` -- RANK 1: block-local circ-conv bind + bidirectional bindobj on graded sparse
  block codes, at 3 block geometries (block-size/count sweep per the drill caveat). HP_SCOPE: chaining gates.
- D `BLOCK_RESONATOR__g0` -- RANK 1 + RANK 2: block bind + iterative resonator cleanup readout (primary geo).
  HP_SCOPE: chaining gates.

Block geometries (all dg_dim = kb*blk_l = 4096): g0=(kb32,blk128,m5) active 0.0391 [certified GSBC point];
g1=(kb32,blk128,m8) active 0.0625; g2=(kb64,blk64,m3) active 0.0469.

## Bands (pre-registered BEFORE FULL; MEASURED anchors from Stage-2)
MEASURED@data/exp_grounding_encoder_clean_codes_retrain_v1/metrics.json:
- BINDOBJ_ONLY recall=0.4234 reach=1.0 (the DENSE_BINDOBJ contrast floor)
- FULL_STACK (dense bind + DG expand) recall=0.25 reach=1.0; element_attribution.expand_gain=-0.2117
- ALL arms reach=1.0 (reach>=2 NEVER achieved on these learned codes with dense binding)

- `baseline_in_band` (DENSE_BINDOBJ): recall in [0.34, 0.50] (brackets 0.4234) AND reach <= 1. At FULL n=5000
  this is Stage-2-MEASURED clean (reach=1.0). At SMOKE n<=1800 the reach probe SATURATES (see smoke result) so
  the baseline-reproduce gate is only READABLE at FULL -- discriminator-survives-scale option (B), analytical
  justification anchored on Stage-2's MEASURED n=5000 baseline reach=1.0.
- `HARD_PASS`: a BLOCK arm with reach>=2 AND (reach - DENSE_BINDOBJ_reach) >= 1 AND recall >= 0.42
  (RECALL_KEEP_MIN) AND precision >= 0.10 (spurious-edge guard) AND sparse_rate <= 0.10 (sparsity preserved)
  AND non-collapsed/shuffle-gated reach. reach 1->2 is a full integer jump (strictly above floor+5%).
- `DG_expansion_net_positive`: block_expand_gain = recall(best BLOCK) - recall(DENSE_BINDOBJ) > 0
  (report vs Stage-2 dense expand_gain = -0.2117).
- `HARD_FAIL_BLOCK_BINDING_INSUFFICIENT`: ALL block arms reach <= 1 (chaining ceiling is NOT a bind-operator
  mismatch after all -> escalate mechanism) OR best BLOCK recall < DENSE_BINDOBJ - 0.05 (block-locality destroys
  cross-block info / costs capacity) OR block hop-1 unbind fidelity < 0.90 (block-locality itself lossy).
- `MIDDLE_BAND`: reach>=2 achieved but recall < 0.42, OR block_expand_gain only mildly positive.

Both outcomes are gold: PASS = the encoder wall cracks (sparse codes + clean chainable binding coexist);
FAIL = block-binding fidelity insufficient at our k-WTA regime (a deeper encoder-capacity finding).

## SCHEMA-VET fields
- `cardinality_ok`: true. EXPECTED_N_UNITS = n_seeds; each seed asserted to produce all 6 arm-metrics (arm-
  cardinality RuntimeError on breach) + HARD_FAIL_CARDINALITY_BREACH_META_RULE_H if seeds < expected.
- `arms_differ_verified`: true. encoder sha256 digests + recovered-edge-set hashes logged per arm; warn if all
  recovered-edge sets identical.
- `final_metrics_atomicity`: tmp_replace (via `_seed_checkpoint.write_metrics` + os.replace).
- `crlb_n/a`: reach ordering-acc chance floor = 0.5; discriminator is shuffle+collapse-gated reach + role-
  recovery edge_recall vs a reproduced dense baseline floor -- not a closed-form estimator noise floor.
- `discriminator_reachability`: reach=2 is reachable (self-test 2-hop block bind/unbind fidelity = 1.0 exact).
- `baseline_in_band`: gated at FULL (analytical, Stage-2 MEASURED reach=1.0); smoke saturates (documented).
- `calibration_check`: adaptive_with_discriminator_gate -- shuffled empirical null recomputed per run;
  over-smoothing collapse gate on the resonator (attractor_frac telemetry); crosstalk floor is codebook-size-
  aware sqrt(2 ln n / d).
- `sweep_alignment_verdict`: ALIGNED (block geometry g0/g1/g2 is the swept axis; each geometry trains its own
  encoder + roles at its own dg geometry; the block bind operates at the exact geometry swept).
- `discriminating_fraction`: n/a-by-sweep-axis (block geometry is a robustness sweep, not an accuracy-bracket
  sweep); the discriminating axis is the DENSE-vs-BLOCK binding-operator contrast.
- `composition_edges`: ProjHead -> graded block STE -> block-local circ-conv bind (SHAPE_MATCH: both operate on
  [.,kb,blk_l] block layout); block bind -> resonator cleanup (SHAPE_MATCH: cleanup re-projects to block
  manifold each iter).
- `positive_control_arms`: DENSE_BINDOBJ reproduces Stage-2 BINDOBJ_ONLY AT THE TEST REGIME (identical
  train_encoder_v2(expand=False, bindobj=True) + score_role); tolerance via baseline_in_band band.
- `functional_requirements`: (1) sparse codes for decorrelation/capacity -> graded GSBC block STE; (2) clean
  invertible binding on sparse codes -> block-local circ-conv (self-test hop-1 fidelity 1.0); (3) multi-hop
  chaining -> reach_over_recovered + resonator cleanup (self-test 2-hop fidelity 1.0).
- `defensive_error_checking`: passed_all_4_patterns (start_marker + crash_diagnostic + heartbeat +
  per-seed failure-class). `cell_chunked`: false (per-seed loop with write_partial checkpoints; 3 seeds).
- `progress_logging`: print_flush_true (line-buffered stdout + per-arm/per-epoch flush + heartbeat).

## Compute architecture
Class (b) sequential-CPU with justification: encoder training is sequential SGD (step N depends on N-1); the
recovery/reach probe is graph-algorithmic (BFS + field propagation, CPU). Matches Stage-2 (CPU, 226s FULL).
Storage strategy: no_storage (in-memory codes; the "chain" is graph reach over a recovered adjacency, not
bundled/sharded stored vectors). Teacher-free, no external LM/network.

## Self-test (formula / discriminator; MEASURED@data/exp_grounding_encoder_sparse_block_binding_v1_selftest)
PASS (58.7s): hop1_fidelity=1.0 (block bind then unbind EXACT recovery; >= 0.90 min; dense-HRR-on-sparse=0.80
CITED@arXiv:2009.06734); reuse_equiv_ok=True (block_bind allclose hdlab.binding.bind on reshaped);
sr_code=sr_bound=0.0391 (sparsity EXACTLY preserved through bind, materially sparse <= 0.10);
twohop_fidelity=1.0 (2-hop bind/unbind exact -> reach>=2 possible in principle); retrain_recall=0.919 vs
chance=0.05 (BLOCK_BINDOBJ learns role-recoverable codes); telemetry_sensitive=True (permute -> 0.919->0.053);
resonator non-vacuous (cleanup_moved=1.25) + non-collapsed (attractor_frac=0.37 at n=240).

## Smoke result (n=1525, 2 seeds; MEASURED@data/exp_grounding_encoder_sparse_block_binding_v1_smoke)
Verdict BASELINE_REPRO_FAIL -- BUT this is a SMALL-N reach-discriminator SATURATION artifact, not a cell defect:
DENSE_BINDOBJ reach was seed7=3, seed13=1 (mean 2.0) -- the small shallow graph (n=1525, bins d3=19/d4+=0) makes
reach=2 trivially reachable for the baseline, so the reach<=1 floor cannot be read at smoke N (exactly the
Stage-2-documented small-N inflation). What smoke DID fire cleanly (robust across both seeds):
- block_expand_gain = +0.284 (best BLOCK recall 0.654 vs DENSE_BINDOBJ 0.369); DG_expansion_net_positive=True --
  FLIPPED from Stage-2's dense expand_gain -0.2117. Headline enabling signal fired.
- All BLOCK arms sparse_rate 0.0391-0.0625 (sparsity preserved); all reach=2 with sparse codes.
- Arms differ; 6 arms x 2 seeds; cardinality intact; cell runs end-to-end.
- Resonator (arm D) OVER-SMOOTHS at scale (attractor_frac 0.03 at n>=1525; recall 0.26 reach 1) -- the over-
  smoothing guard fires. RANK-1 (plain block bind) is the load-bearing fix; RANK-2 resonator as specced
  (beta=12, 3 iters) collapses at our regime. Consistent with the drill's S3 open question (RANK-1 may suffice).
The reach discriminator is only cleanly readable at FULL n=5000 (Stage-2 MEASURED baseline reach=1.0, 3 seeds);
FULL dispatch is warranted on discriminator-survives-scale option (B) analytical justification.

## Dispatch
- Queue: remote_cpu_queue (CPU teacher-free; laptop is slowest resource; local reserved for smoke only).
- Timeout: 3600 s (Stage-2 MEASURED 226s for 4 arms/3seeds/n5000; 6 arms + resonator ~= 510s est; ~7x safety).
- FULL config: seeds [7,13,17], n_nodes=5000, epochs=120, code_dim=256, dg_dim=4096, feat_dim=8192.
- --skip-smoke justified: local smoke already ran (validated machinery); its BASELINE_REPRO_FAIL is a documented
  small-N reach-saturation artifact, not a crash; self-test PASS. A queue_add small-N smoke would repeat it.

## Discipline declarations
ASCII-only; no em dashes in code output; commit before remote dispatch; per-experiment timeout computed;
pause-flag re-checked before hand-off.
