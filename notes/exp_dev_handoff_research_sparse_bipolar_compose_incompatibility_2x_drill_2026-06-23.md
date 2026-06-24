# exp_dev hand-off — research: sparse-bipolar compose incompatibility 2x drill

**Filed-by:** Research (Opus 4.7-1M)
**Date:** 2026-06-23
**Trigger:** USER directive "research negatives 2x"; convergent pattern audit on sparse-bipolar + compose mechanisms across 5 recent negatives
**Source:** `notes/research_sparse_bipolar_compose_incompatibility_2x_drill_2026-06-23.md`
**Pause state:** check `data/orchestrator_paused.flag` before dispatch — research delivery is a TRIGGER not a SHIP order

Per [[feedback-no-experiment-design-in-prompts]]: the anchor candidates below are pointers; exp_dev decides cell-author specifics, smoke gates, runtime measurement, dispatch routing. Research provides the WHY/WHAT-TO-TEST; exp_dev provides the HOW.

---

## Anchor candidates (rank-ordered, decisive-first)

### Anchor 1 (PRIMARY DECISIVE) — `exp_sparse_bipolar_compose_class_factorial_v1`

**Anchor pointer:** 2x2 factorial × 2 amplitude variants = 6 arms
- Codebook axis: DENSE vs SPARSE-bipolar (f=0.05) vs SPARSE-AMPLITUDE-SCALED (1/sqrt(f) = 4.47)
- Compose-class axis: ADDITIVE compose vs MULTIPLICATIVE compose
- Task: text8 LM at N=4096, M=500, 3 seeds

**Substrate-product reading:** the cleanest discriminator between this drill's two load-bearing mechanism candidates. If multiplicative-zero-product-cascade is correct (P=0.65), multiplicative sparse arms collapse to unigram floor regardless of amplitude; additive sparse arms work after amplitude fix.

**Tier hint:** decisive-test priority; runs in ~45min CPU; local_cpu_queue acceptable.

**Why-now:** 3 of 5 recent negatives (theta-gamma, K-module, 3-axis multiplicative) involve sparse-bipolar + compose; this cell isolates whether the failure is at the COMPOSE-CLASS layer (multiplicative vs additive) or the CODEBOOK layer (sparse vs dense) — currently confounded across cells.

**Pre-reg HARD bands (from research note L4 / cheap-decisive-test):**
- HARD_PASS if ARM_DENSE_MULTIPLICATIVE lift >= 0.20 AND ARM_SPARSE_RAW_MULTIPLICATIVE lift in [-0.10, +0.05] AND ARM_SPARSE_AMP_ADDITIVE lift >= 0.30 AND ARM_SPARSE_AMP_MULTIPLICATIVE lift in [-0.10, +0.10]
- HARD_FAIL if ARM_SPARSE_RAW_MULTIPLICATIVE lift >= 0.20 (mechanism refuted) OR ARM_DENSE_MULTIPLICATIVE lift < 0.10 (multiplicative just broken generally)

---

### Anchor 2 (SECONDARY — if Anchor 1 HARD_PASS) — `exp_cdt_bind_substrate_native_v1`

**Anchor pointer:** implement Rachkovskij 2001 context-dependent thinning bind for sparse-bipolar; test 4-deep compose chain
- Compare: CDT-bind vs HRR-bind vs raw-multiply
- Measure: output density after 1/2/3/4 binds; LM lift on text8

**Substrate-product reading:** the brain-canonical fix for sparse compose. If this works, substrate gets a third compose primitive that PRESERVES sparsity through depth.

**Tier hint:** novel-synthesis cap P=0.45; runs in ~30min CPU.

**Why-now:** conditional on Anchor 1 confirming multiplicative-cascade mechanism; CDT is the published-precedent fix.

---

### Anchor 3 (AUDIT — no cell, immediate) — Per-context T full-scale verification

**Anchor pointer:** locate or re-dispatch full-scale per-context T (N=8192, N_TRAIN=100000) to verify prompt's "5 orders of magnitude T_std collapse" claim
- Current smoke (N=256) shows ARM_PER_CONTEXT_T_DENSE T_std=0.036 (NOT 0.000002 as prompt claims)
- Sparse pc-lift in smoke is BENEFICIAL (+0.068), not catastrophic

**Substrate-product reading:** prompt may be confusing smoke with full-scale, or referring to a different cell entirely. Audit prevents wasted dispatch.

**Tier hint:** AUDIT only; no cell needed if full-scale metrics already exist.

**Why-now:** before dispatching any per-context-T-rescue cell, verify the failure exists at full scale.

---

### Anchor 4 (CORRECTIVE — separate bug from sparse) — Higher-order Taylor n=1 baseline audit

**Anchor pointer:** verify why Taylor ARM_n1 bpc=7.7378 (unigram floor) when it SHOULD match K-module M1 bpc=7.3065 (rank-1 sparse-bipolar baseline)
- Cell uses dense_word2vec_projected encoder (NOT sparse-bipolar) per line 99-100 comment
- Even n=1 (linear rank-1) should give a lift; instead all 5 arms collapse identically

**Substrate-product reading:** the Taylor cell's collapse is NOT sparse-bipolar related — it's an encoder-magnitude bug + Ocker-Buice vanishing-signal for n>=2. Needs encoder/normalization audit.

**Tier hint:** AUDIT first; if bug confirmed, re-dispatch with fix (likely amplitude scaling on dense encoder or different nonlinearity class).

**Why-now:** Taylor cell mis-attributed in prompt; clear up separate bug to avoid conflation.

---

## Context pointers (file paths, not summaries)

**Source research:**
- `notes/research_sparse_bipolar_compose_incompatibility_2x_drill_2026-06-23.md` (THIS hand-off's parent)
- `notes/research_sparse_cleanup_compose_breakage_diagnosis_2026-06-23.md` (matched-filter framework foundation)
- `notes/research_drill_sparse_bipolar_depth_enc1_composition_2026-06-23.md` (earlier sparse drill)
- `notes/research_drill_sparse_allocation_routing_learning_2026-06-23.md` (sparse allocation drill)

**Cell sources to read (NOT modify):**
- `experiments/exp_substrate_k_module_heterogeneous_compose_LM_v1.py` (line 259 raw sparse construction; line 375 "E_sparse_bipolar always")
- `experiments/exp_substrate_higher_order_taylor_nonlinear_hebbian_LM_v1.py` (line 99-100 comment: uses DENSE word2vec)
- `experiments/exp_substrate_per_context_T_diagnostic_v1.py` (smoke arm definitions)
- `experiments/exp_substrate_theta_gamma_nested_with_brain_compensation_N4096_v1.py` (theta-gamma demod + brain compose pipeline)

**Metrics to cross-reference:**
- `data/exp_substrate_k_module_heterogeneous_compose_LM_v1/metrics.json` (ARM_SPARSE_BIPOLAR_ONLY=7.3065; compose arms=7.7378)
- `data/exp_substrate_per_context_T_diagnostic_v1/metrics.json` (sparse pc-lift +0.068; dense pc-lift -0.056)
- `data/exp_substrate_theta_gamma_nested_with_brain_compensation_N4096_v1/metrics.json` (NESTED_SPARSE@16=0.197)
- `data/exp_substrate_higher_order_taylor_nonlinear_hebbian_LM_v1/metrics.json` (all n=1..5 arms identical at 7.7378)

**Atoms / Store cross-refs:**
- CERT 592 sparse-bipolar bundle-capacity (chain-grade; storage metric only — unchanged by this drill)
- META atom from source research: `matched_filter_sqrt_f_receiver_SNR_penalty_unless_amplitude_scaled`
- (proposed new META atoms — see research note L5)

**Brain-canonical references (literature, for cell-author background):**
- Rachkovskij & Kussul 2001 "Context-Dependent Thinning" Neural Computation 13(2):411-452 (CDT bind procedure)
- Hersche et al. 2023/2025 "Factorizers for Distributed Sparse Block Codes" arxiv 2303.13957 (threshold-based nonlinear readout for SBC)
- Kanerva 1988 SDM (sparse coding for storage capacity)

---

## Contract section

This is a research-to-experiment hand-off. exp_dev MUST:
- Read this file and the parent research note in full before dispatch
- Run `tools/predispatch_check.py <anchor>` before each spawn (per Fix #26)
- Apply pause-flag gate (`data/orchestrator_paused.flag`) before queue_add
- Use cell-author smoke + Fix #17 runtime measurement on remote for any heavy cell (per USER 2026-06-22)
- Read per-arm metrics (NOT verdict_msg framing) before any cross-cell convergence claim (per Fix #28)
- Stay within ≤3 in-flight spawn budget (per Fix #14)
- For Anchor 1 (decisive test): prefer local_cpu_queue runner — substrate-only numpy, ~45min CPU, no GPU needed
- For Anchor 2 (CDT bind): build hdlab/cdt_bind.py primitive FIRST (test in isolation with similarity-preservation oracle), THEN ship cell
- For Anchor 3 (audit): NO cell; check existing full-scale metrics OR escalate to research for re-dispatch
- For Anchor 4 (Taylor n=1 audit): minimal cell — just verify n=1 matches sparse-bipolar rank-1 baseline (~5min CPU); if not, file separate bug-fix cell

## Autonomy declaration

exp_dev decides:
- Cell-author specifics (file paths, function signatures, smoke-gate criteria)
- Smoke vs full run mode for each anchor
- Dispatch routing (local_cpu_queue vs remote_cpu_queue vs overnight_queue)
- Whether Anchor 1 or Anchor 4 ships first (both are decisive at different scales; Anchor 4 is cheaper)
- Whether to combine Anchor 3 + Anchor 4 audits into a single inspection cycle
- Pre-flight self-tests (density verification, amplitude L2-norm match, multiplicative output density check)

Research will pick up next drill cycle on:
- Whichever anchor returns HARD_PASS / HARD_FAIL with decisive evidence
- Per-context T audit outcome (if 5-OoM claim is real, novel-mechanism drill needed)
- CDT bind feasibility from Anchor 2 if dispatched
