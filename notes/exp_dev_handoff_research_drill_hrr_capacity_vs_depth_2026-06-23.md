# exp_dev hand-off -- research: HRR capacity-vs-depth drill

Filed-by: research sub-agent (2026-06-23)
Trigger: notes/research_drill_hrr_capacity_vs_depth_2026-06-23.md
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

The just-landed contextual-encoding HRR-binding smoke (`exp_contextual_encoding_hrr_binding_smoke_v1` HARD_PASS, WSD acc=1.0 at depth=1, M=5 bundle) validates context-conditional encoding via bipolar element-wise bind. USER 2026-06-23 substrate-only product direction depends on whether this mechanism extends to LM-relevant context windows (k≥8 tokens deep). Without measured depth-budget, we can't deploy context-conditional encoding at scale.

Research drill found:
- substrate's `bind_elementwise` is involutive (depth-LOSSLESS on pure chains, NOT 1/sqrt(k) per Plate)
- real depth-budget bottleneck is BUNDLE WIDTH M per layer (sigma ~ 1/sqrt(M))
- cleanup-per-layer (substrate has `iterative_attractor.py`; works at V/N < 0.138) is load-bearing compensator
- circular convolution alternative (Plate original) is depth-INFERIOR for substrate's regime
- SHALLOW+WIDE composition (cortical column analog) likely beats DEEP+NARROW at k=20

One CPU cell `exp_hrr_depth_budget_curve_v1` is the cheapest decisive test. Smoke ~1hr CPU; full ~14hr CPU OR ~3hr GPU. De-risks top-tier enabling path #1.

---

## Anchor Candidates (rank-ordered)

### A. HRR-DEPTH-BUDGET-CURVE-SMOKE (HIGHEST PRIORITY -- runs first)

Anchor pointer: HRR-DEPTH-BUDGET-CURVE-SMOKE-A (new; not yet queued)
Substrate-product reading: Validates that substrate's bipolar HRR-bind primitive supports context windows of k=20 tokens with cleanup-per-layer compensation. If HARD_PASS, the context-conditional encoding mechanism is depth-safe for production LM. If HARD_FAIL, signals a bind-operator upgrade is required (VTB or sparse-bipolar) before LM deployment.
Tier hint: CPU laptop; ~1hr wall time (k=[1,5,20] x M=[1,5,64] x 1 seed x 200 trials at N_DIM=4096)
Why-now: Smoke just HARD_PASSed at depth=1; we need depth-budget envelope BEFORE the next scaling step on context-conditional LM. Cheapest possible test. De-risks top-tier enabling path #1.

Pre-reg bands (research recommendation; exp_dev validates):
  HARD_PASS:
    - recall@1 at (k=20, M=1, ELEM_WISE_BIPOLAR, cleanup_OFF) >= 0.99 (validates involutive prediction)
    - AND recall@1 at (k=5, M=5, cleanup_ON) >= 0.97 (validates cleanup compensation)
    - AND recall@1 at (k=20, M=5, cleanup_ON) >= 0.80 (validates depth-budget at LM-relevant width)
  HARD_FAIL:
    - recall@1 at (k=20, M=1, cleanup_OFF) < 0.95 (involutive prediction WRONG; hidden noise source or implementation bug)
    - OR recall@1 at (k=5, M=5, cleanup_ON) < 0.85 (cleanup-per-layer not load-bearing; M_bundle is depth-killer immediately)
  MID-BAND: anything in between -> queue full sweep before declaring chain-grade

Setup (research recommendation; exp_dev refines):
  - N_DIM=4096; V=100 random bipolar atoms (cleanup memory at M/N=0.024, safely below att1 alpha_c)
  - reuse bind_elementwise + bundle_mean_norm_bipolar from experiments/exp_contextual_encoding_hrr_binding_smoke_v1.py
  - implement cleanup_per_layer as: project to V via dot products, take argmax, return V[argmax] (single-pass nearest neighbor)
  - per (k, M) point: generate random binding sequence; bind+bundle through k layers; unbind to recover leaf; measure recall@1 vs V[true_leaf_idx]
  - 200 trials per point; report recall@1 mean across trials

### B. HRR-DEPTH-BUDGET-CURVE-FULL (runs after A HARD_PASS)

Anchor pointer: HRR-DEPTH-BUDGET-CURVE-FULL-B (new; not yet queued)
Substrate-product reading: Full sweep of depth-budget envelope across all (k, M, bind_variant, cleanup, composition_strategy) factors. Generates the empirical capacity curve and the SHALLOW+WIDE vs DEEP+NARROW tradeoff measurement. Chain-grade-eligible if 3 seeds pass primary discriminator with cv<=0.05.
Tier hint: GPU desktop; ~3hr wall time (full grid 7 k x 5 M x 2 bind x 2 cleanup x 2 strategy x 3 seeds x 200 trials = ~840 points x ~13s)
Why-now: Only dispatch if SMOKE-A HARD_PASSes. Generates the depth-budget envelope used to plan context-conditional LM scale and to populate substrate META atom.

Pre-reg bands:
  HARD_PASS (substrate chain-grade for depth-budget):
    - recall@1 at (k=12, M=5, ELEM_WISE_BIPOLAR, cleanup_ON, all 3 seeds) >= 0.95 AND cv <= 0.05
    - AND recall@1 at (k=20, M=5, cleanup_ON) >= 0.85 across all 3 seeds
    - AND pure-chain (M=1) recall@1 at k=20 >= 0.99 (involutive validation)
    - AND SHALLOW+WIDE recall@1 (k=4, M=20, cleanup_ON) >= DEEP+NARROW recall@1 (k=20, M=4, cleanup_ON) by >= 0.10 (validates cortical-column-analog)
  HARD_FAIL:
    - any of: recall@1 at (k=12, M=5, cleanup_ON) < 0.85; cv > 0.10; pure-chain at k=20 < 0.95
  MID-BAND: route to N_DIM=8192 sweep

Setup:
  - same primitives as A; expand to 3 seeds [7, 17, 23]
  - add bind_variant_grid = [ELEM_WISE_BIPOLAR, CIRCULAR_CONV_FFT_REAL]
  - add cleanup_per_layer = [OFF, ON_NEAREST_NEIGHBOR]
  - add composition_strategy = [DEEP_NARROW, SHALLOW_WIDE]
  - report per-arm metrics.json with by_arm_agg per Fix #28 discipline

### C. HRR-DEPTH-BUDGET-WITH-SPARSE-ENCODER (DEFERRED to ENC1 HARD_PASS)

Anchor pointer: HRR-DEPTH-BUDGET-SPARSE-C (deferred)
Substrate-product reading: Tests whether sparse-bipolar encoding (per Frady-Kleyko-Sommer 2023) extends depth-budget by predicted ~2-3x. Composes substrate's encoder-side fix (ENC1) with depth-budget bind layer.
Tier hint: GPU desktop; ~4hr wall time
Why-now: Only dispatch if ENC1 (in flight per notes/research_encoder_side_cleanup_ceiling_break_*) HARD_PASSes AND HRR-DEPTH-BUDGET-CURVE-FULL-B HARD_PASSes. Both upstream gates required.

Pre-reg bands: depth-budget extends to k=30+ at M=5 cleanup_ON with sparse-bipolar bind; HARD_FAIL = no improvement vs dense-bipolar.

---

## Context pointers (file paths, not summaries)

Research note:
- `notes/research_drill_hrr_capacity_vs_depth_2026-06-23.md` (THIS DRILL — empirical curve predictions + cleanup compensation analysis + HARD_PASS/HARD_FAIL bands)

Parent drills:
- `notes/research_5x_deeper_substrate_LM_gap_2026-06-23.md` (parent on HRR composition; HYBRID dispatch awaits this drill's verdict)
- `notes/research_encoder_side_cleanup_ceiling_break_2026-06-23.md` (ENC1 sparse-fan-in encoder in flight; composes with depth-budget mechanism)

Substrate primitives:
- `experiments/exp_contextual_encoding_hrr_binding_smoke_v1.py` (bind_elementwise, bundle_mean_norm_bipolar, bipolar_quantize — primitives to reuse)
- `hdlab/binding.py` (FFT-based circular convolution variant for CIRCULAR_CONV_FFT_REAL arm; complex FHRR variant)
- `hdlab/iterative_attractor.py` (cleanup memory for cleanup_per_layer; note att1 v1+v2 HARD_FAIL family — works only at V/N < 0.138; safe at V=100 N=4096)
- `hdlab/sequence_memory.py` (sequence binding primitives; cross-check composition order)
- `hdlab/whitening.py` (composition with ENC1 if anchor C dispatches)

Cell metrics (smoke baseline):
- `data/exp_contextual_encoding_hrr_binding_smoke_v1_smoketest/metrics.json` (depth=1 HARD_PASS, WSD acc=1.0 lift=0.80 N_DIM=4096 PRETRAIN_DIM=300)

Cert ledger META anchors:
- row 675: `T3/META_cleanup_ceiling_shannon_floor_substrate_operating_envelope_sigma_leq_1p0_2026-06-23` (this drill's predictions stay within validated sigma <= 1.0 envelope)

External literature (verified):
- Plate 1995 HRR (ijcai.org/Proceedings/91-1/Papers/006.pdf)
- Schlegel-Neubert-Protzel 2021 VSA comparison (link.springer.com/article/10.1007/s10462-021-10110-3)
- Frady-Sommer 2018 capacity analysis (openreview.net/pdf?id=6tazBqPem3)
- Frady-Kleyko-Sommer 2023 sparse binding (arxiv.org/pdf/2009.06734)
- Salvatori 2024 associative memory of structured knowledge (nature.com/articles/s41598-022-25708-y)

---

## Contract section

exp_dev's job:
1. Read research note + this hand-off in full.
2. Verify pause state.
3. Pre-flight: confirm smoke cell exists and reproduces depth=1 HARD_PASS baseline (re-run with seed=7 if needed).
4. Validate research's pre-reg bands. exp_dev may TIGHTEN or REFINE. If exp_dev disagrees with research's bands, document the disagreement in the cell pre-reg note and proceed with exp_dev's chosen bands.
5. Smoke A FIRST. If smoke HARD_PASSes, queue full B. If smoke HARD_FAILs or MID-BANDs, surface to research for next-cycle drill.
6. Per [[feedback-fix28-verify-per-arm-metrics-not-summary-verdict-text]]: report per-arm recall@1 in metrics.json, not just verdict_msg summary.
7. Per [[feedback-long-cells-must-checkpoint-resume-restartable]]: full B cell (~3hr GPU) must checkpoint per-seed.
8. Per Fix #14 (spawn budget <=3): ensure dispatch slot available before queue_add.
9. Per Fix #20 (no `2>&1 | tail -N`): use file-redirect for any subprocess monitoring inside cell.
10. Per Fix #28: read metrics.json per-arm before any cross-arm claim.

Research is NOT writing this cell. exp_dev designs implementation, anchor naming, queue assignment, runtime measurement, and HARD-PASS verification autonomously.

---

## Autonomy declaration

This hand-off provides:
- WHY (research rationale for depth-budget question + lit-scan findings)
- WHAT (anchor candidates with substrate-product implications)
- WHEN (priority ordering + dependency on smoke A HARD_PASS for full B + ENC1 dependency for C)
- HARD_PASS/HARD_FAIL bands as RESEARCH RECOMMENDATIONS

It does NOT provide:
- Exact code for the cell (exp_dev writes; reuses smoke cell primitives)
- Final queue choice (laptop vs remote desktop vs GPU) -- exp_dev decides per Fix #14 + GPU-routing rules
- Final HARD-PASS thresholds (exp_dev validates research's recommendations)
- Anchor names committed to ledger (exp_dev decides naming convention)

exp_dev owns the cell design and queue execution end-to-end.
