# exp_dev hand-off -- research: sparse-bipolar depth-budget + ENC1 composition

Filed-by: research sub-agent (2026-06-23, Opus 4.7)
Trigger: notes/research_drill_sparse_bipolar_depth_enc1_composition_2026-06-23.md
Pause state: check data/orchestrator_paused.flag before acting

Per [[feedback-no-experiment-design-in-prompts]]: this file provides anchor candidates,
context pointers, and strategic rationale. exp_dev designs actual anchors, sweep grids,
thresholds, and queue assignment autonomously. Pre-reg bands below are RESEARCH
recommendations -- exp_dev validates and may refine before queue dispatch.

---

## Pause state block

Before dispatching any anchor: verify data/orchestrator_paused.flag does NOT exist (or
confirm with orchestrator). Do not ship if paused.

---

## Why this hand-off exists

Parent HRR depth drill (2026-06-23) identified bundle width M (sigma ~ 1/sqrt(M)) as the real depth-budget bottleneck. Independently, substrate has DIRECT MEASUREMENT (CERT 592, MEASURED_MECHANISM) of 20-300x bundle-capacity lift via sparse-bipolar codes at f=0.005-0.02 N>=2048. Composing these: sparse-bipolar bundle should unbottleneck the parent's identified bottleneck and shift the k=20 prediction P from 0.65 to 0.85.

Separately, ENC1 (5-arm cleanup-ceiling cell) HARD_FAILED all 5 arms incl. ARM_SPARSE_FANIN_K5_N4096 = 0.018 at sigma=1.5. This drill REFUTES the framing that sparse-bipolar rescues ENC1 (it does not at sigma=1.5; honor "Shannon-floor" classification).

Net: ONE cell to dispatch -- adds sparse-bipolar bundle variants to parent HRR depth drill's grid. Cell is the cheapest decisive test of whether substrate should switch default bundle representation dense -> K-sparse bipolar.

---

## Anchor Candidates (rank-ordered)

### A. HRR-DEPTH-BUDGET-SPARSE-BIPOLAR-SMOKE (HIGHEST PRIORITY)

Anchor pointer: HRR-DEPTH-BUDGET-SPARSE-A (new; not yet queued)
Substrate-product reading: Validates that K-sparse bipolar bundle (f=0.02 at N=4096, K=82 active) extends parent's HRR depth-budget envelope at k=20 M=20 from P=0.65 (dense) to P>=0.85 (sparse). If HARD_PASS, ships `hdlab/sparse_bipolar.py` SAME CYCLE per results-to-application cadence. Unbottlenecks substrate's path-#1 enabling mechanism (context-conditional LM encoding).
Tier hint: CPU laptop; ~30 min wall time (smoke); ~3 hr full
Why-now: Parent HRR depth drill identified bundle width M as the bottleneck. CERT 592 already MEASURED 20-300x sparse bundle-capacity lift at substrate scale. The composition is direct, cheap, and load-bearing.

Pre-reg bands (research recommendation; exp_dev validates):
  HARD_PASS:
    - recall@1 at (k=20, M_bundle=20, K_SPARSE_SUM_THEN_TOPK at f=0.02, cleanup_ON, 3 seeds) >= 0.90 AND cv <= 0.05
    - AND recall@1 at (k=20, M_bundle=20, DENSE_SUM_THEN_SIGN, cleanup_ON) <= 0.70 (validates the sparse-lift IS the mechanism vs dense at same M)
    - AND LCC_PER_BLOCK matches or beats K_SPARSE_SUM_THEN_TOPK at k=20 (validates Frady-Kleyko-Sommer 2023 LCC bind is the canonical involutive operator)
    - AND pure-chain (M=1) K_SPARSE recall@1 at k=20 >= 0.95 (validates support-preservation involution)
  HARD_FAIL:
    - recall@1 at (k=20, M_bundle=20, K_SPARSE, cleanup_ON) <= 0.60 (sparse provides no usable lift; bundle-width bottleneck is intrinsic)
    - OR pure-chain K_SPARSE recall@1 at k=20 <= 0.80 (element-wise sparse-bipolar support drift kills chains; LCC must be used instead -- adjust framing)
    - OR LCC_PER_BLOCK pure-chain recall@1 <= 0.95 (LCC implementation bug or block-size wrong -- diagnose before mechanism rejection)
  MID-BAND: anything in between -> queue M_bundle sweep up to 80 (substrate's CERT 592 measured headroom)

Setup (research recommendation; exp_dev refines):
  - N_DIM = 4096; vocab V = 100 sparse-bipolar atoms (f=0.02 = K=82 active per atom; or B=64 blocks of N/B=64 with K=1 active per block for LCC)
  - reuse bind_elementwise + bundle_mean_norm_bipolar from experiments/exp_contextual_encoding_hrr_binding_smoke_v1.py as parent's primitives
  - NEW bundle variants:
    * K_SPARSE_SUM_THEN_TOPK: sum the K-sparse vectors; keep TOP-K positions by absolute value; sign-quantize within the K active positions
    * LCC_PER_BLOCK: for each B-sized block, sum the per-block circular-convolution outputs; keep K=1 active per block via argmax-within-block; sign-quantize
  - k_grid = [1, 5, 12, 20]
  - M_bundle_grid = [5, 20, 64]
  - cleanup_per_layer = [OFF, ON_NEAREST_NEIGHBOR]
  - seeds = [7, 17, 23] (3 seeds for smoke is fine; cell is cheap)
  - 200 trials per point
  - Sanity self-test before mechanism call: at sigma=0 (no noise) all sparse-arms must achieve recall@1 = 1.0 (clean cue = atom-recovery is by construction)

### B. HRR-DEPTH-BUDGET-SPARSE-FULL (runs after A HARD_PASS)

Anchor pointer: HRR-DEPTH-BUDGET-SPARSE-FULL-B (new; not yet queued)
Substrate-product reading: Full sweep across f-sparsity grid + M_bundle expansion to substrate's measured capacity ceiling. Generates the depth-budget x sparse-fraction phase diagram needed for production LM scale.
Tier hint: GPU desktop; ~4-6 hr wall time
Why-now: Only dispatch if SMOKE-A HARD_PASSes. Populates substrate META atom and unblocks Path A pseudo-LM at sparse-bundle encoding (potential 0.3-0.7 bit closure on bigram-gap).

Pre-reg bands:
  HARD_PASS (chain-grade for sparse-bipolar default):
    - all of A's HARD_PASS conditions hold at 3 seeds with cv <= 0.05
    - AND f-sparsity sweep f in {0.005, 0.01, 0.02, 0.05} shows monotone capacity-lift with decreasing f (validates CERT 592's super-capacity finding at depth-budget regime)
    - AND M_bundle = 64 K_SPARSE recall@1 at k=20 >= 0.80 (validates 13x capacity headroom usable at k=20)
  HARD_FAIL:
    - any of A's HARD_FAIL conditions; OR f-sparsity sweep does NOT show monotone lift (the CERT 592 effect does not extend to depth-chained regime)
  MID-BAND: route to N_DIM=8192 sweep at f=0.005

Setup:
  - same primitives as A; expand grid
  - add f_grid = [0.005, 0.01, 0.02, 0.05] (with K = N*f)
  - add M_bundle = 80 (substrate's CERT 592 measured M_max ceiling at f=0.02 N=4096)
  - report per-arm metrics.json with by_arm_agg per Fix #28 discipline

### C. ENC1-AT-SPARSE-BIPOLAR-BUNDLE-LAYER (deferred, conditional)

Anchor pointer: ENC1-SPARSE-BUNDLE-C (deferred)
Substrate-product reading: Tests whether substrate's PRODUCTION encoder pipeline (pythia/BGE -> CERT 591 projection -> dense bipolar) gains capacity-headroom by swapping the dense-bundle stage for K-sparse bipolar bundle. Different mechanism than parent ENC1 (which tested encoder GEOMETRY); this tests bundle WIDTH.
Tier hint: GPU desktop; ~2-3 hr wall time
Why-now: Only dispatch if A HARD_PASS AND if the substrate's working-envelope (sigma <= 1.0) allows it. DO NOT dispatch at sigma=1.5 (Shannon-floor per ENC1 verdict).

Pre-reg bands:
  HARD_PASS: ENC1-style argmax recall@1 at sigma=0.5 with K_SPARSE bundle >= +0.10 vs dense bundle baseline (at same M)
  HARD_FAIL: no lift; sparse-bipolar bundle does not transfer to production encoder regime

---

## Context pointers (file paths, not summaries)

Research notes:
- `notes/research_drill_sparse_bipolar_depth_enc1_composition_2026-06-23.md` (THIS DRILL -- full analysis + bands + Q1-Q5 answers)
- `notes/research_drill_hrr_capacity_vs_depth_2026-06-23.md` (PARENT drill -- depth-budget envelope; identifies bundle width M as bottleneck)
- `notes/research_encoder_side_cleanup_ceiling_break_2026-06-23.md` (ENC1 design; HARD_FAIL all 5 arms at sigma=1.5)
- `notes/research_canonical_evidence_map_v5_MINI_REFRESH_sparse_300x_LANDED_supersedes_8_20x_placeholder_a3f473dd_2026-06-20.md` (CERT 592 META atom: sparse 300x bundle-capacity lift MEASURED)

Substrate data (for reproduction + reference):
- `data/exp_sparse_boundary_v2_cpu_v1/metrics.json` (substrate's 20x capacity lift MEASURED at f=0.02 N=2048; load-bearing internal evidence)
- `data/exp_enc1_structured_n_lift_v1/metrics.json` (ENC1 HARD_FAIL: ARM_SPARSE_FANIN_K5_N4096 = 0.018 at sigma=1.5)
- `data/exp_contextual_encoding_hrr_binding_smoke_v1_smoketest/metrics.json` (parent HRR smoke HARD_PASS WSD=1.0 at depth=1)

Substrate primitives:
- `hdlab/binding.py` (FHRR + HRR bind primitives; no element-wise bipolar or sparse-bipolar yet -- new primitive needed for SMOKE-A)
- `experiments/exp_contextual_encoding_hrr_binding_smoke_v1.py` (substrate's custom bind_elementwise + bundle_mean_norm_bipolar -- parent's primitives, reuse)
- `hdlab/iterative_attractor.py` (cleanup memory; att1 family; safe at V/N < 0.138 -- this cell's V=100/N=4096 = 0.024 is well-within)
- `hdlab/whitening.py` (ZCA whitening -- composes if needed at production)

External:
- Frady, Kleyko, Sommer 2023 "Variable Binding for Sparse Distributed Representations" TNNLS (PMC12180425; LCC-per-block bind is canonical sparse-VSA operator; involutive per block via FFT-conjugate)
- Litwin-Kumar 2017 + Cayco-Gajic 2017 + eLife 2023 (cerebellar K=4 task-INDEPENDENT; brain analog applies to single-layer encoder NOT nested-bind depth)

---

## Strategic rationale

1. **Bundle-width bottleneck is real (parent HRR drill MEASURED)**: depth-budget envelope at k=20 is dominated by sigma ~ 1/sqrt(M_bundle).
2. **Sparse-bipolar lift is real (substrate CERT 592 MEASURED, NOT lit-extrapolated)**: 20-300x bundle-capacity lift at f<=0.02 N>=2048.
3. **Direct composition opportunity**: parent's identified bottleneck + substrate's measured lift = single cheap cell (~30 min CPU smoke) validates the composition.
4. **ENC1-rescue framing REFUTED at sigma=1.5**: parent ENC1 already measured the null; do NOT redispatch ENC1 with sparse-bipolar; honor Shannon-floor classification.
5. **Brain analog REFUTES nested-bind framing**: cerebellar K=4-8 applies to single-layer encoder (which ENC1 already tested + failed); sequential GC activation gives temporal depth (different mechanism).
6. **Frady-Kleyko-Sommer 2023 LCC-per-block IS the canonical sparse-bipolar bind operator**, provably invertible; substrate's element-wise sparse-bipolar bind suffers support drift on chains > k=2 -- LCC is the rescue.

If HARD_PASS: substrate ships 2 new hdlab primitives (`sparse_bipolar.py` + `lcc_block_bind.py`) SAME CYCLE per results-to-application discipline. META atom candidate: T1/substrate_sparse_bipolar_bundle_20x_capacity_unbottlenecks_hrr_depth_budget_2026-06-23. Path A pseudo-LM bigram-gap closure pathway opens (predicted 0.3-0.7 bit closure on 1.13-bit gap to text8 word-bigram).

If HARD_FAIL: atomize `substrate_sparse_bipolar_bundle_does_not_lift_hrr_depth_envelope_at_N_4096`; fall back to parent's dense bundle envelope at M_max ~ 80-220.

---

## Contract section

- exp_dev is autonomous on cell design, sweep grid refinement, queue assignment (local_cpu_queue OR overnight_queue depending on smoke vs full), and pre-flight smoke gates.
- Research recommends `local_cpu_queue` for SMOKE-A (cell is cheap, laptop CPU); `overnight_queue` for FULL-B (GPU desktop).
- Research recommends Fix #26 verify-the-referent pre-dispatch check (tools/predispatch_check.py SMOKE-A) before queue add.
- Research recommends per-arm metrics.json with by_arm_agg per Fix #28 (verify per-arm metrics, not cross-cell verdict_msg).
- exp_dev validates HARD_PASS/HARD_FAIL bands and may tighten/loosen based on cell-author smoke results.

## Autonomy declaration

Research filed THIS hand-off. exp_dev owns:
- Cell-author design + smoke
- Queue dispatch (route via hdi_orchestrator if N_DIM>=8192 OR multi-arm-heavy OR matmul-bound per Fix #24 GPU dispatch discipline; SMOKE-A is N=4096 + cheap, so local_cpu_queue is fine)
- Post-ship REMOTE VERIFY if dispatched to remote
- Verdict-handler hand-off on completion

Research does NOT pre-design the cell or pre-stage queue commits. exp_dev refines and ships.
