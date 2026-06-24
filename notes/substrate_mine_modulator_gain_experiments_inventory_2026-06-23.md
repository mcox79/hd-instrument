# Substrate-mine inventory: modulator / gain-control / gating experiments

**Date:** 2026-06-23
**Drill type:** SUBSTRATE-MINE (read-only) — feeds USER directive *"we know this can work, we need to experiment until we find the right conditions"*
**Scope:** all prior cells touching scalar-modulator / gain-control / gating axes; identifies what's been tested so the 3-axis neuromodulator cell doesn't re-test the same axes.
**Output:** one-line-per-cell inventory + GAP MATRIX + top-3 untested orthogonal mechanisms.

---

## HEADLINE
The substrate has TESTED several **write-side / decode-side / gating** axes (excitability-write-gain HARD_PASS, cf-RPE+STDP heterogeneous HARD_PASS, 3-axis neuromod compose HARD_PASS at N=512 smoke, refuse-gate variants HARD_PASS, lock-in P64 HARD_PASS) but has **NOT** systematically tested **read-side scalar gain × write-side ACh-style attention-gain × global serotonin state-gate as separable orthogonal axes at production scale (N>=8192)** — the just-dispatched 3-axis neuromodulator cell is the FIRST cross-axis compose, and even it is a smoke-grade N=512/N_TRAIN=2000/seed=0 single-seed test. Top untested mechanism: **read-side temperature-per-context** (current temperature-calibration HARD_PASS is GLOBAL, not gated). Second: **ACh-style query-conditional gain on retrieval** (separate from write-time excitability). Third: **serotonin state-gate selecting WHICH memory bank** (mode-switch, not modulation amount).

---

## ONE-LINE-PER-CELL INVENTORY (organized by mechanism axis)

### Axis A: Dopamine / cf-RPE (reward-prediction-error scalar)
- `exp_substrate_drosophila_mb_sparse_single_modulator_v1_n4096`: single dopamine-like scalar modulator on sparse MB-style write | **HARD_FAIL** | gap_mean=0.004 nats (B_better=1/2) | covered by triple-mod cell as ARM_DOPAMINE_ONLY
- `exp_substrate_cfrpe_sparse_superadditive_bigram_v1_n512_gpu`: cf-RPE × sparse Hebbian compose on bigram LM | **MIDDLE_BAND** | hebbian=3.154 / cfrpe=2.471 / combined=2.453 nats (additive only; super_seeds=0/5) | cert row 472
- `exp_substrate_cfrpe_stdp_heterogeneous_superadditive_bigram_v1_n512`: cf-RPE × STDP HETEROGENEOUS compose | **HARD_PASS** chain-grade | cfrpe=3.767 / stdp=3.245 / combined=3.744 (super_seeds=5/5) | cert row 473 — KEY DATA: heterogeneity is the lever, not homogeneous compose
- `exp_substrate_sq2_x_cfrpe_composition_v1_n4096`: cf-RPE preserves 12-hop reasoning | **HARD_PASS** | cfrpe_acc@12=1.00 (depth-preservation, not bigram-gap)
- `exp_substrate_b5_escapeB_cfrpe_weighted_replay_v1_n2048`: cf-RPE-weighted replay for retention rescue | **HARD_FAIL** | retention 0.528→0.535 (1.01x; no replay rescue)
- `exp_substrate_drosophila_mb_sparsity_sweep_v1_512_2048_gpu`: sparsity sweep under single-modulator | **MIDDLE_BAND** | best f*=0.01 @ N=512 gap=+0.150 (2/3 seeds)

### Axis B: ACh-style attention-gain / query-conditional
- `exp_substrate_neuromodulator_3axis_gated_compose_LM_v1` (ARM_DOPAMINE_PLUS_ACH): dopamine + ACh stack | **HARD_PASS** envelope-break (whole cell) | ARM_DOPAMINE_PLUS_ACH=bpc5.523/top10=0.3306/mrr=0.4016 — note: identical BPC to ARM_DOPAMINE_ONLY=5.523; ACh slot did **NOT** add bits over dopamine alone in this run; smoke-grade N=512 seed=0; FIRST compose ever | gap-vs-3axis-cell: TESTED but underpowered
- No standalone ACh-only cell anywhere in substrate

### Axis C: Serotonin / state-gate / mode-switch
- `exp_substrate_neuromodulator_3axis_gated_compose_LM_v1` (ARM_TRIPLE_MOD_FULL): includes serotonin slot | **HARD_PASS** envelope-break | ARM_TRIPLE_MOD_FULL=bpc5.314/top10=0.3306/mrr=0.3982 — DELTA over ARM_DOPAMINE_PLUS_ACH=5.523 is -0.21 BPC (the third axis IS where the lift comes from); but per-seed-N=1 / N_DIM=512 smoke
- No standalone serotonin-only cell anywhere in substrate
- META-gap: state-gate as **mode-switch** (gate selects WHICH bank) vs **gain-modulation** (gate scales values) NOT distinguished

### Axis D: Excitability / tag-and-capture (Tonegawa-class write-allocation gain)
- `exp_excitability_gated_substrate_cpu_v1`: priority-proportional WRITE-gain protects high-pri above cliff | **HARD_PASS** | gated_hi=1.000 ungated_hi=0.500 @ K=1200 (cliff-aware; recall-side at write)
- `exp_alloc_routing_excitability_trace_smoke_v1_localdry2`: position-trace allocation routing (vs random vs kWTA) | **MIDDLE_BAND** | RANDOM=pur0.138, EXC=pur0.373, KWTA=pur0.900 — KEY: kWTA dominates excitability on purity; recall-lift=0.000 (allocation routing at @sigma=1.0)
- (no full-scale excitability cell at N>=8192 with LM downstream)

### Axis E: Lambda-mix / decode-side blending
- `exp_fair_harness_substrate_as_lm_v1`: LAMBDA_GRID=[0,0.1,0.3,0.5,0.7,1.0] × TEMP_GRID swept on text8 | **HARD_PASS** chain-grade | uni=7.738 / sparse_bipolar=clears bpc<7.438; decode-side mix is the load-bearing lever | N_DIM=8192 N_TRAIN=100000 V=4000 — covered. gap-vs-3axis: DECODE-side only
- `exp_substrate_sparse_competitive_readout_lm_v1`: rank-1 vs top-K compete + excitability decode | **MIDDLE_BAND** | rank1=7.666 vs K=100+excitability=7.738 (delta=-0.072; lifts over rank-1 doesn't beat unigram) | TOPK_LIST=[10,100]
- `exp_text8_substrate_pseudoLM_v2_temperature_calibrated_v1`: temperature × log-linear decode | **MIDDLE_BAND** | raw=11.614 / temp_calibrated=11.266 / log_linear=7.864 / unigram=7.738 (improvement under bar) | GLOBAL temp not per-context

### Axis F: Refuse-gate / health-gate / margin-gate (SAFETY-side)
- `exp_refuse_gate_5_graph_health_cpu_v1`: graph-health refuses overload + accepts storable | **HARD_PASS** chain-grade (cert row 588) | health-boundary coincides with accuracy-cliff
- `exp_multiplicative_composition_lever_v1_cpu_v1`: depth-axis refuse-gate selector vs always-chain | **HARD_PASS** chain-grade (cert row 589 / 616) | robustly beats always-chain at fabrication loads [1.0,1.5]
- `exp_2axis_refuse_gate_compose_v1_cpu_v1`: 2-axis refuse-gate compose | **MEASURED_MECHANISM** (cert row 592) | safety vs utility gate mismatch
- `exp_substrate_refuse_gate_nonlinear_readout_v1`: nonlinear readout under refuse-gate | **NON_TEST** (cert row 560)
- `exp_query_margin_gate_smoke_v1_n4096`: query-margin defends against contradiction | **D1_HARD_FAIL** | no delta defends (def=0.000 across all)
- `exp_v1_corroboration_gate_v1`: Byzantine quorum corroboration | **MIDDLE_BAND** | recovery=0.835 false_accept=0.000 @ f=4/10
- `exp_substrate_pp8_cosine_variance_gate_v1`: cosine-variance gate for extraction speedup | **HARD_PASS** | 97% concept coverage at 10x
- `exp_substrate_embedding_norm_gate_discriminability_v1`: norm-gate concept selection | **HARD_FAIL** | min_coverage=0.4332 (drops concepts)
- `exp_q_c5_cosine_gate_tau_recal_v1`: cosine deletion-gate tau recal | **HARD_PASS** | tau*=0.78 FN=0/FP=0 (GDPR-grade)
- `exp_dreaming_gate_tau_recal_v1`: dreaming gate tau recal | **HARD_FAIL** | no tau in [0.82,0.88] satisfies FN<0.05 AND FP<0.1
- `exp_substrate_active_gating_8a_break_even_v1`: bounded-regime break-even | **HARD_PASS** | sharp monotone boundary

### Axis G: Surprise / predictive-coding residual gate
- `exp_pc1_predictive_coding_residual_gate_v1`: PC residual-gate skip on prediction error | **MIDDLE_BAND** | PC_RESIDUAL_GATE_THRESH_0p3 rec=1.000 norm=183177 skip=0.00 (gate not firing under tested threshold)
- `exp_surprise_gated_pool_charlm`: surprise-gated pool for char-LM | **no verdict in metrics** (looks like pre-pre-reg or stub)
- `exp_surprise_gating_b3b_synthetic_pool_recapture_v1`: synthetic pool recapture | (no data dir landed)

### Axis H: Top-K / kWTA / sparsity-as-gate (decode + write)
- `exp_n4_kwta_soft_decode_v1`: kWTA soft-decode k=[1,8,32] | **HARD_FAIL** | best_k=32 ceiling_delta=-0.000 bits (kWTA WORSE than k=1 anchor) | N_DIM=16384 V_C=1024
- `exp_topk_recall_cpu_v1`: top-K re-rank for bit-flip rescue | **HARD_PASS** | recall@5=1.0 at 0.35 bit-flip
- (sparse-competitive cell above also tests K=10/100 on LM)

### Axis I: Sparse-bipolar f-axis (sparsity-as-gain proxy)
- `exp_fair_harness_sparse_bipolar_T_PINNED_witness_v1`: T-pinned defense witness | **MIDDLE_BAND** | T005=bpc9.956 (+0.190 vs uni / +0.020 vs full) (partial defense)
- `exp_sparse_bipolar_substrate_lm_param_sweep_v1`: full sparse-bipolar sweep N×T×f | **SWEEP_HARD_FAIL** | max_lift=0.442 ≤ baseline+tol=0.481 (envelope is one-point; no scaling lever) | N=8192 → THE just-measured cap

### Axis J: Multi-modulator / familiarity / tier-rescue
- `exp_substrate_4modulator_familiarity_v2_n4096`: 4-modulator familiarity rescue | **HARD_FAIL** | single_imp_recall=1.000 fourmod_imp_recall=1.000 (ratio=1.00x at T=3N overflow)
- `exp_substrate_4modulator_hippocampal_tier_rescue_v1_n4096`: 4-modulator hippocampal tier rescue | **HARD_FAIL** | single_recall=1.000 fourmod_recall=0.914 (0.91x; single-modulator limit ARCHITECTURAL at M=2x m_cap)

### Axis K: Lock-in amplifier (frequency-domain gain selection)
- `exp_lock_in_amplifier_hd_frequency_smoke_v1`: lock-in amp on HD | **HARD_PASS** smoke | P32 lifts recall x4.32 over baseline at sigma_32
- `exp_lock_in_amplifier_hd_frequency_v1_FULL`: lock-in FULL | **HARD_PASS** chain-grade | P64 lifts x16.39 with cv=0.000 (chain-grade primitive across scales) | N_DIM=8192 M=500 — USER-intuition-validated

---

## GAP MATRIX

| Mechanism | Prior cell | Verdict | Tested-at-scale | Gap-vs-3axis-cell |
|---|---|---|---|---|
| Dopamine cf-RPE (alone) | drosophila_mb_sparse_single_modulator | HARD_FAIL | N=4096 sparse | Yes; SINGLE failed; superposition OK |
| Dopamine × Hebbian (homog compose) | cfrpe_sparse_superadditive_bigram | MIDDLE_BAND | N=512 V GPU 5seed | Yes; additive-only |
| Dopamine × STDP (heterog compose) | cfrpe_stdp_heterogeneous_superadditive | **HARD_PASS** chain-grade | N=512 5seed | YES; **heterogeneity IS the lever** — 3-axis cell should USE heterogeneous-write |
| Dopamine preserves depth-12 | sq2_x_cfrpe_composition | HARD_PASS | N=4096 | Composition-side covered |
| Dopamine replay rescue | b5_escapeB_cfrpe_weighted_replay | HARD_FAIL | N=2048 | Closed; no replay-rescue |
| ACh attention-gain (compose w/ dopa) | neuromod_3axis_gated_compose ARM_DOPA_PLUS_ACH | HARD_PASS envelope | N=512 seed=0 smoke | TESTED but UNDERPOWERED + identical-BPC-to-dopa-only suggests ACh slot not lifting |
| ACh attention-gain (alone) | NONE | UNTESTED | — | **GAP — orthogonal complement to dopa-only** |
| Serotonin state-gate (compose) | neuromod_3axis_gated_compose ARM_TRIPLE_MOD_FULL | HARD_PASS envelope | N=512 seed=0 smoke | TESTED; delta vs ACh-stack = -0.21 BPC (3rd axis carries lift) |
| Serotonin mode-switch (alone) | NONE | UNTESTED | — | **GAP — mode-switch vs gain-modulation never distinguished** |
| Tonegawa excitability write-gain | excitability_gated_substrate | HARD_PASS | full @ K=1200 | Partial; production cliff-aware write |
| Excitability allocation-routing | alloc_routing_excitability_trace_smoke | MIDDLE_BAND | smoke @ sigma=1.0 | Partial; kWTA dominates on purity |
| Lambda-mix decode (global) | fair_harness_substrate_as_lm | **HARD_PASS** chain-grade | N_DIM=8192 N=100K | Decode-side only; global not per-context |
| Temperature-calibrate (global) | text8_pseudoLM_v2_temperature_calibrated | MIDDLE_BAND | N=8192 | Decode-side global only — **GAP: per-context temperature never tested** |
| Top-K / KWTA decode | sparse_competitive_readout_lm + n4_kwta_soft_decode | MIDDLE_BAND / HARD_FAIL | N_DIM=8192/16384 | Tested; kWTA loses to k=1 |
| Sparse-bipolar f-axis (write-gate) | sparse_bipolar_substrate_lm_param_sweep | HARD_FAIL_SCALING | N_DIM=8192 ENVELOPE | THE just-measured cap; one-point envelope |
| Multi-modulator familiarity rescue | 4modulator_familiarity_v2 | HARD_FAIL | N=4096 T=3N | Closed at overflow |
| 4-mod hippocampal tier rescue | 4modulator_hippocampal_tier_rescue | HARD_FAIL | N=4096 M=2x m_cap | ARCHITECTURAL single-mod limit confirmed — **CRITICAL: 3-axis-LM compose works DIFFERENTLY than 4-modulator-recall-rescue** |
| Refuse-gate / graph-health | refuse_gate_5_graph_health + multiplicative_composition_lever | HARD_PASS chain-grade | full | Covered (safety-side gate) |
| Query-margin gate | query_margin_gate_smoke | D1_HARD_FAIL | N=4096 smoke | Closed (no delta defends) |
| Cosine-variance extraction gate | substrate_pp8_cosine_variance_gate | HARD_PASS | — | Covered (extraction-side) |
| Embedding-norm discriminability gate | substrate_embedding_norm_gate | HARD_FAIL | — | Closed |
| PC residual gate | pc1_predictive_coding_residual_gate | MIDDLE_BAND | — | Partial; PC gate not firing at tested thresh |
| Lock-in amplifier (frequency-gain) | lock_in_amplifier_hd_frequency_v1_FULL | **HARD_PASS** chain-grade | N=8192 M=500 | Frequency-domain gain CONFIRMED — orthogonal to scalar-modulator axis |

---

## TOP 3 UNTESTED MECHANISMS (orthogonal complement to just-dispatched 3-axis neuromod cell)

### 1. **Per-context (query-conditional) temperature gate at decode** — orthogonal to global temp-calibration
- **Why untested:** all temperature work (`text8_substrate_pseudoLM_v2_temperature_calibrated_v1` MIDDLE_BAND, `fair_harness` HARD_PASS TEMP_GRID) used a SINGLE global temperature per arm. The 3-axis neuromod cell writes-gain-modulates, but decoder still has fixed temp.
- **Discriminator:** at high-surprise contexts (PC residual large), substrate should sharpen (lower T); at low-surprise contexts, broaden (higher T). Compare BPC of fixed-T best=7.864 vs per-context-T at N_DIM=8192 N=100K.
- **Brain analog:** noradrenaline → gain on cortex (Aston-Jones & Cohen 2005), context-dependent.
- **Cost:** ~1-day impl on top of existing `text8_pseudoLM_v2` cell.

### 2. **ACh-style query-conditional READ-gain (separate from write-time excitability)** — orthogonal to write-side dopamine
- **Why untested:** `excitability_gated_substrate_cpu_v1` HARD_PASS is WRITE-time priority-proportional gain. No cell tests query-conditional READ-gain (input → gate that scales which atoms are admitted into retrieval). The 3-axis neuromod cell folds ACh-as-write-side; the decode-time ACh equivalent (ACh sharpens cortical receptive fields per Hasselmo) is unmeasured.
- **Discriminator:** ACh-style read-gain that sharpens retrieval based on query-norm vs uniform retrieval at N_DIM=8192 N=100K. HARD_PASS if BPC ≤ 7.500 (fair_harness HARD_PASS bar) AND top10 ≥ 0.25.
- **Brain analog:** muscarinic ACh sharpens neighbor-suppression at retrieval (Hasselmo & Sarter 2011).
- **Cost:** ~1-day impl, composes with existing `fair_harness` arms.

### 3. **Serotonin as MODE-SWITCH (selects WHICH atom-bank), not gain-modulation** — distinguish mode vs amount
- **Why untested:** 4-modulator cells (`4modulator_familiarity_v2`, `4modulator_hippocampal_tier_rescue`) both HARD_FAILed because they layered 4 scalar gain modulators in parallel on ONE bank. No cell tests a serotonin-class gate that switches BETWEEN 2+ distinct atom-banks (e.g., recent-bank vs consolidated-bank) based on context.
- **Discriminator:** 2-bank substrate (bank-A trained on first half, bank-B on second half) + 5HT-gate that routes query to A or B based on novelty signal. HARD_PASS if BPC < 7.500 AND bank-routing accuracy > 0.80 on held-out.
- **Brain analog:** dorsal raphe 5HT mode-switches between exploration/exploitation (Cohen et al. 2015); orbitofrontal mode-switch (Iigaya et al. 2018).
- **Cost:** ~1.5 days; needs new dual-bank scaffold in `hdlab/` but reuses existing sparse_bipolar codebook.

**Why these 3 orthogonally complement the just-dispatched cell:**
- 3-axis-neuromod-cell varies SCALAR MAGNITUDE on a single bank at write time
- Gap-1 (per-context-T) varies SCALAR MAGNITUDE at READ time
- Gap-2 (ACh-read-gain) varies INPUT-CONDITIONAL gain at READ time (separate from write-time excitability)
- Gap-3 (5HT-mode-switch) varies WHICH BANK (not amount) at READ time
- Together, the 4 cells span: {write × read} × {amount × switch} — the full 2×2 of where-and-how-to-gate

---

## POINTERS — 5 most relevant prior research drill notes

1. `notes/research_drill_sparse_allocation_routing_learning_2026-06-23.md` — defines excitability-trace as substrate-native Tonegawa-class allocation; explicitly identifies 4 prior forward-only encoder HARD_FAILs (SoftHebb, Foldiak, FPE, char-trigram) — useful as prior-art ceiling for any "learned gain" cell
2. `notes/research_5x_deeper_encoder_upgrade_dual_gain_2026-06-23.md` — dual-gain candidates (SoftHebb / FPE) for encoder-side gain; META: encoder geometry cannot break sigma>=1.5 on random bipolar
3. `notes/research_drill_predicate_evaluation_primitives_2026-06-23.md` — predicate-evaluation-as-gate primitives (substrate-native; relevant for read-side gain)
4. `notes/research_5x_deeper_high_noise_substrate_product_strategy_2026-06-23.md` — high-noise regime + substrate product framing for any gain-mechanism gain-axis
5. `notes/research_brain_drill_substrate_native_relational_semantic_encoding_5x_DEEPER_2026-06-22.md` — brain-mechanism inventory; ACh/dopa/5HT roles surfaced

---

## SUMMARY (caller-facing)

- **31 prior cells** inventoried across 11 mechanism-axes
- **Chain-grade HARD_PASSes:** cf-RPE×STDP heterogeneous, excitability-write-gain, refuse-gate × graph-health, multiplicative-composition lever, fair-harness lambda-mix, lock-in amplifier P64
- **HARD_FAILs:** dopamine-alone, kWTA decode, 4-mod familiarity, 4-mod hippocampal tier rescue, sparse-bipolar f-axis envelope, query-margin gate, embedding-norm gate, dreaming-gate
- **MIDDLE_BANDs to revisit:** cf-RPE × Hebbian compose (additive only), temp-calibration global (under bar), sparse-competitive readout K=100 (lifts over rank-1 doesn't beat unigram), excitability allocation-routing
- **Top-3 untested gaps:** (1) per-context temperature gate (read-side), (2) ACh-style query-conditional read-gain (separate from write excitability), (3) 5HT mode-switch (bank-selection, not amount-modulation)
- **3-axis neuromod cell IS smoke-grade** (N=512 / N_TRAIN=2000 / seed=0): even its HARD_PASS verdict needs N>=8192 / 3-seed re-run before chain-grade tier — by-construction-saturation risk per Skunkworks default
