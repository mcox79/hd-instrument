# exp_dev hand-off — research: schema-inference PHASE DIAGRAM (cosine vs structure)

**Filed-by:** Research (Director, Opus 4.7-1M)
**Date:** 2026-06-27
**Trigger:** `notes/research_drill_2x_schema_inference_phase_diagram_cosine_vs_structure_2026-06-27.md`
**Pause state:** check `data/orchestrator_paused.flag` before dispatch

Per [[feedback-no-experiment-design-in-prompts]]: this file provides anchor candidates, context pointers, and strategic rationale. exp_dev designs actual cells, sweep grids, thresholds, queue assignment autonomously. Pre-reg bands below are RESEARCH RECOMMENDATIONS — exp_dev validates and may refine.

---

## Pause state block

Before dispatching any anchor: verify `data/orchestrator_paused.flag` does NOT exist. Do not ship if paused.

---

## Why this hand-off exists

3 schema-inference cells today (ANCHOR 1/2/3) MEASURED substrate-cosine at default regime (M=6, V=8, NEX=20, sum-encoding, N=2048). All three CONVERGED at ~0.728 recall (90% of ORACLE=0.809). Richer mechanisms (MAC+FAC, vmPFC context-prior) tied or hurt. **Open question:** at what regime does cosine BREAK + at what regime do richer mechanisms START helping? Answering this maps the substrate-as-schema-device operating envelope and tells us when to deploy which primitive.

---

## Anchor Candidates (rank-ordered)

### A. CAPACITY-CLIFF M-SWEEP (HIGHEST PRIORITY — runs first)

**Anchor pointer:** `exp_schema_inference_phase_diagram_cosine_capacity_cliff_v1` (new; not yet queued)
**Substrate-product reading:** Establishes the M_SLOTS boundary where sum-encoding cosine breaks. At default M=6, substrate captures schema structure (chain-grade-eligible per ANCHOR 3); this cell measures the operational envelope of that primitive. Produces the SINGLE most-cited phase-diagram axis for substrate-product positioning.
**Tier hint:** CPU laptop; ~30s smoke wall (7 M-points × 3 arms × 3 seeds at N=2048; per ANCHOR 3 timing ~0.4s/cell-unit)
**Why-now:** Cheapest decisive test in this drill. Settles cone-collapse math at the regime brain-default schemas operate near. De-risks substrate-product schema positioning.

**Pre-reg bands (research recommendation; exp_dev validates):**
- HARD_PASS:
  - EXEMPLAR_BAYES_K20 at M=6 in [0.65, 0.80] (reproduces ANCHOR 3 baseline)
  - AND at M=24 in [0.40, 0.55] (cliff onset)
  - AND at M=48 ≤ 0.40 (deep into break)
  - AND BASELINE at M=48 in [0.10, 0.20] (chance 1/V=0.125 holds; no saturation)
- HARD_FAIL:
  - EXEMPLAR at M=48 ≥ 0.65 (no cliff; mechanism understanding wrong; substrate more tolerant than predicted)
  - OR EXEMPLAR at M=6 < 0.50 (regression vs ANCHOR 3)
  - OR baseline ≥ 0.40 at any M (saturation rail violated)
- MIDDLE_BAND: cliff at different M than predicted (e.g. M=16 not M=24); refine boundary in v2

**Setup (research recommendation; exp_dev refines):**
- Reuse `experiments/exp_cortex_schema_exemplar_bayes_importance_sample_v1.py` as template
- M_SLOTS sweep ∈ {6, 12, 16, 24, 32, 48, 64}; V_SLOT=8, NEX=20, N=2048 fixed
- Arms: ARM_EXEMPLAR_BAYES_K20 + ARM_NO_SCHEMA_BASELINE + ARM_ORACLE_TRUE_SCHEMA
- 3 seeds [7, 17, 23]; cardinality_ok = (7 M × 3 arms × 3 seeds = 63)
- Compute formula in code: `predicted_cliff_recall_at_M = phi(1 / sqrt(M * V_SLOT / N_DIM))` — log for validation
- Smoke at N=1024 must FIRE discriminator (raise SMOKE_DISCRIMINATOR_FAILED if cliff signal absent — same monotone decrease with M as full would show)

### B. CROSS-SCHEMA OVERLAP MAC+FAC CROSSING (runs after A HARD_PASS)

**Anchor pointer:** `exp_schema_inference_phase_diagram_cross_schema_overlap_macfac_crossing_v1` (new; not yet queued)
**Substrate-product reading:** Establishes the cross-schema-interference regime where MAC+FAC structure-mapping starts to beat surface-cosine exemplar Bayes. Tells us when to deploy substrate's richer cortical primitives.
**Tier hint:** CPU laptop; ~60s smoke wall (4 overlap × 4 arms × 3 seeds at M=12)
**Why-now:** Validates the orthogonal-lift conjecture from ANCHOR 2 author's roadmap. Closes or opens the MAC+FAC product story.

**Pre-reg bands:**
- HARD_PASS:
  - At 0% overlap: EXEMPLAR ≥ MAC+FAC by ≥0.05 (reproduces today's ordering at higher M=12)
  - At 50% overlap: |EXEMPLAR - MAC+FAC| ≤ 0.05 (parity zone)
  - At 75% overlap: MAC+FAC ≥ EXEMPLAR by ≥0.08 (orthogonal lift in cross-schema regime)
  - ORACLE > EXEMPLAR at all overlap points (sanity rail)
- HARD_FAIL:
  - At 75%: MAC+FAC ≤ EXEMPLAR + 0.02 (orthogonality never emerges; MAC+FAC line closed)
  - OR EXEMPLAR collapses to BASELINE at any overlap (over-degradation — bug)
  - OR cardinality breach

**Setup:**
- Reuse `experiments/exp_cortex_schema_MACFAC_two_stage_retrieval_v1.py` template
- Fix M=12 (richer than default M=6; matches MAC+FAC original Gentner-Forbus regime); V=8; NEX=20; N=2048
- Sweep cross-schema slot-overlap fraction ∈ {0%, 25%, 50%, 75%}
- Arms: EXEMPLAR_BAYES + MAC+FAC + BASELINE + ORACLE; 3 seeds; cardinality_ok = (4 × 4 × 3 = 48)

### C. SUM-POOL vs HRR-BIND ENCODING SWEEP (runs after A HARD_PASS; UPSIDE cell)

**Anchor pointer:** `exp_schema_inference_phase_diagram_encoding_mode_sum_vs_hrr_bind_v1` (new; not yet queued)
**Substrate-product reading:** Tests whether substrate's bipolar HRR-bind primitive (chain-grade per 2026-06-23 depth-budget) extends substrate's schema-inference operating regime BEYOND the sum-encoding cone-collapse boundary. If HARD_PASS, substrate becomes super-biological in slot-count dimension.
**Tier hint:** CPU laptop or remote_cpu_queue; ~5min smoke wall (3 M × 2 encoding × 3-4 arms × 3 seeds at N=2048)
**Why-now:** Tests substrate-NOVEL composition (existing chain-grade HRR-bind applied at schema-inference phase boundary). Largest substrate-product upside if HARD_PASS.

**Pre-reg bands:**
- HARD_PASS:
  - At M=6: SUM_POOL ≥ HRR_BIND by ≥0.05 (HRR-bind costs SNR at low M)
  - At M=32: HRR_BIND ≥ SUM_POOL by ≥0.08 (HRR factorization preserves slot identity beyond cone-collapse)
  - At M=32: ARM_RESONATOR ≥ HRR_BIND by ≥0.08 (iterative factor disentanglement adds value when superposition heavy)
- HARD_FAIL:
  - HRR_BIND ≤ SUM_POOL + 0.02 at M=32 (HRR no benefit even at predicted-break)
  - OR ARM_RESONATOR ≤ HRR_BIND + 0.02 (iteration adds nothing)

**Setup:**
- Reuse `experiments/exp_cortex_schema_exemplar_bayes_importance_sample_v1.py` as base
- Add HRR_BIND encoding mode: bipolar role atom per slot; bipolar filler atom per (slot, value); exemplar = bundle of M role-filler binds via element-wise bipolar bind from `hdlab/binding.py`
- Add ARM_RESONATOR: iterative factor disentanglement per Frady-Kent-Sommer 2020 (substrate primitive exists in lit; needs cell-author implementation; cleanup pool = filler bank per slot)
- M sweep ∈ {6, 16, 32}; encoding ∈ {SUM_POOL, HRR_BIND_ELEMENTWISE}; V=8, NEX=20, N=2048

---

## Context pointers (file paths, not summaries)

**Research note (this drill):**
- `notes/research_drill_2x_schema_inference_phase_diagram_cosine_vs_structure_2026-06-27.md`

**MEASURED-today cells (3 cells, all metrics.json absolute paths):**
- `data/exp_cortex_schema_exemplar_bayes_importance_sample_v1_smoke/metrics.json` (ANCHOR 3 HARD_PASS recall=0.728)
- `data/exp_cortex_schema_instantiation_context_prior_v1_smoke/metrics.json` (ANCHOR 1 MIDDLE_BAND recall=0.731)
- `data/exp_cortex_schema_MACFAC_two_stage_retrieval_v1_smoke/metrics.json` (ANCHOR 2 HARD_FAIL recall=0.665)

**Cell-author templates:**
- `experiments/exp_cortex_schema_exemplar_bayes_importance_sample_v1.py` (template for anchors A and C)
- `experiments/exp_cortex_schema_MACFAC_two_stage_retrieval_v1.py` (template for anchor B)

**Substrate primitives (anchor C reuses):**
- `hdlab/binding.py` (bipolar bind_elementwise; FFT circular convolution)
- `hdlab/iterative_attractor.py` (cleanup memory for ARM_RESONATOR — note att1 family works only at V/N < 0.138; safe at V=8 N=2048)

**Composing prior research drills:**
- `notes/exp_dev_handoff_research_drill_hrr_capacity_vs_depth_2026-06-23.md` (HRR depth-budget; sigma~1/sqrt(M) math; relevant for anchor C)
- `notes/research_drill_2x_triple_revival_BCM_HRR_STUBE_2026-06-27.md` (resonator network revival mechanism; relevant for anchor C)
- `notes/p1_phase_diagram_action_HARD_FAIL_at_smoke_discriminator_invalid_2026-06-22.md` (discriminator-invalid-at-smoke lesson; anchor A must verify within-baseline reproduces)

**External lit (verified):**
- Plate 1995 HRR
- Frady-Sommer 2018 arxiv 1707.01429 (superposition theory; capacity 0.5 bits/neuron)
- Frady-Kleyko-Sommer 2023 arxiv 2009.06734 (sparse binding theory)
- Frady-Kent-Sommer 2020 resonator networks (rctn.org/bruno/papers/resonator1.pdf)
- Frontiers AI 2026 nonlinear cleanup in resonators (frai.2026.1793314)
- arxiv 2606.11391 (2026) recursive binding subspace carving
- arxiv 2301.10352 (2023) VSA capacity analysis
- Gilboa-Moscovitch 2017 schema neurobiology (PubMed 28551107)
- Sun et al 2024 Neuron — structured slots in PFC
- PMC11870651 adaptive chunking PFC-BG

---

## Contract section

exp_dev's job:
1. Read research note + this hand-off in full.
2. Verify pause state.
3. Pre-flight: confirm ANCHOR 3 cell reproduces at default M=6 (re-run smoke if needed; should hit ~0.728).
4. Validate research's pre-reg bands. exp_dev may TIGHTEN or REFINE. If exp_dev disagrees with research's bands, document the disagreement in the cell pre-reg note and proceed with exp_dev's chosen bands.
5. Dispatch ORDER: Anchor A FIRST (cheapest decisive test). If A HARD_PASSes, dispatch B + C in parallel. If A HARD_FAILs (no cliff observed), surface to research for next-cycle drill (likely substrate is MORE tolerant — pivot phase-diagram axes).
6. Per [[feedback-fix28-verify-per-arm-metrics-not-summary-verdict-text]]: report per-arm recall@K in metrics.json, NOT just verdict_msg summary. Use `tools/peek_arm_metrics.py` before any framing claim.
7. Per Fix #14: spawn budget ≤ 3 in flight. Dispatch A solo first.
8. Per Fix #16 (discriminator-must-survive-scale): smoke at smaller N (e.g. N=1024) must FIRE the cliff discriminator at smaller M (e.g. cliff onset at M=12 instead of M=24); if smoke doesn't show monotone decrease with M, HALT-no-dispatch-full.
9. Per Fix #20: no `2>&1 | tail -N` pipes inside cells.
10. Per META_RULE_H: cardinality_ok mandatory; EXPECTED_N_UNITS pre-registered.
11. Per META_RULE_J: no silent except blocks.

Research is NOT writing these cells. exp_dev designs implementation, anchor naming, queue assignment, runtime measurement, and HARD-PASS verification autonomously.

---

## Autonomy declaration

This hand-off provides:
- WHY (research rationale for phase-diagram question + lit-scan findings + MEASURED-today substrate cells)
- WHAT (3 anchor candidates with substrate-product implications)
- WHEN (priority ordering: A first; B + C conditional on A HARD_PASS)
- HARD_PASS/HARD_FAIL bands as RESEARCH RECOMMENDATIONS

It does NOT provide:
- Exact code for cells (exp_dev writes; reuses substrate primitives)
- Final queue choice (CPU laptop vs remote_cpu_queue) — exp_dev decides per Fix #14 + routing rules
- Final HARD-PASS thresholds (exp_dev validates research recommendations)
- Anchor names committed to ledger (exp_dev decides naming convention)

exp_dev owns cell design and queue execution end-to-end.

— Research; phase-diagram drill complete; 3 anchors filed; conditional-hold pending exp_dev acceptance.
