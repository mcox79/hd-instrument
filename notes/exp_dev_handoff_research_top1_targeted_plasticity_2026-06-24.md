# exp_dev hand-off — research: TOP1-targeted plasticity (cf-RPE family ceiling alternative)

**Filed by:** research (Opus 4.7, 1M context)
**Date:** 2026-06-24
**Trigger:** Skunkworks landed-VET 2026-06-24 — cf-RPE per-token adaptive cell ruled MEASURED_MECHANISM. BPC +0.345 over hebbian, top1 delta vs coarse cf-RPE = +0.0005 (0.10sigma, seed noise). cf-RPE family bounded at ~+12% top1 vs unigram while n1_v3 readout achieves +61.6%. The 5x lift-ratio gap lives in the READOUT, not the plasticity — OR in plasticity-rule TARGETING (BPC vs top1).
**Source research note:** `d:/AI/hd-instrument/notes/research_top1_targeted_plasticity_2x_drill_2026-06-24.md`
**Pause state:** check `d:/AI/hd-instrument/data/orchestrator_paused.flag` before dispatching. Per [[feedback-no-experiment-design-in-prompts]] this hand-off provides anchor pointers and pre-reg bands; exp_dev owns the cell-author cycle (smoke gate, AST self-test, queue_add).

---

## Anchor candidates (rank-ordered by P_deflated x cheap-test-coverage)

### ANCHOR #1 — `substrate_top1_plasticity_4arm_smoke_v1` (PRIORITY 1)

**Why now:** decisive cheap test of the drill question. 4 arms in one cell. CPU smoke ~30min. If any arm clears +0.05 top1 absolute over ARM_CFRPE -> promote to full N_DIM=8192. If all four within +/-0.02 -> decisively close plasticity-as-top1-lever hypothesis.

**Substrate-product reading:** chain-grade-eligible single-arm path IF best plasticity composes with n1_v3 readout to push top1 > 0.50 (first substrate-LM single-arm to clear bigram top1 at text8 V=4000).

**Tier hint (per `feedback-empowered-to-experiment-where-lit-says-dismissed` + brain-existence-proof prior):** novel-synthesis composition; not dismissed but uncharted. Standard CHARTED regime (extensive lit) -> 0.20 calibration deflation. Brain-existence-proof + 4 brain-canonical mechanisms (BCPNN, gated-perceptron, lateral-inhibition, CHL) -> prior 0.55-0.75 modulated down by substrate-novel-composition risk to P_deflated 0.30-0.40 per arm.

**Composite ceiling estimate:** at-least-one arm HARD-PASS (top1 >= 0.30 absolute) ~0.55 probability.

**Pre-reg HARD bands (substrate-product-relevant):**
- **HARD-PASS (chain-grade-eligible):** any arm top1 >= 0.30 absolute (= +38% relative over unigram 0.2171) AND cv < 0.05 across 3 seeds. PRED-5 HARD-PASS-PLUS: any arm > 0.47 (clears bigram).
- **MIDDLE_BAND (MEASURED_MECHANISM):** any arm top1 in [0.255, 0.30] = +0.05 absolute lift over cf-RPE 0.2427 but not chain-grade.
- **HARD_FAIL (decisive closure):** ALL arms within +/-0.02 absolute of ARM_CFRPE (top1 in [0.222, 0.262] across all arms). Closes plasticity-as-top1-lever hypothesis; routes top1 effort to readout axis.

**Discriminator:** all four arms use the SAME readout (cosine-NN over codebook C, matching n1_v3 architecture). Only the plasticity rule on W differs. This isolates plasticity contribution from readout contribution. Pre-reg `discriminator_axis = plasticity_rule`; `readout_axis_held_fixed = cosine_nn_C`.

**Smoke config:** N_DIM=2048, V=2000, N_TRAIN=20k, 3 seeds [7, 17, 23]. Smoke pass = ARM_HEBB and ARM_CFRPE reproduce known top1 within +/-0.02; cv < 0.05.

**Full config (if any arm clears +0.05 over CFRPE at smoke):** N_DIM=8192, V=4000, N_TRAIN=100k, 3 seeds. Composes with fair_harness anchor (cell-author should match fair_harness encoder + V split).

**Context pointers (exp_dev reads these before cell-author):**
- `d:/AI/hd-instrument/notes/research_top1_targeted_plasticity_2x_drill_2026-06-24.md` — full drill note with formulas, brain literature, P estimates
- `d:/AI/hd-instrument/notes/skunkworks_LANDED_VET_cfrpe_per_token_adaptive_lr_v1_MEASURED_MECHANISM_2026-06-24.md` — empirical anchor (cf-RPE +11.78% top1 ceiling)
- `d:/AI/hd-instrument/notes/orchestrator_to_skunkworks_N1v3_FAIR_BPC_real_top1_unigram_level_perplexity_2026-06-21.md` — n1_v3 readout chain-grade reference (+61.6% top1)
- `d:/AI/hd-instrument/notes/research_brain_mechanisms_NOT_yet_tested_2x_drill_2026-06-24.md` — Block B lateral inhibition row REOPENED at W-readout granularity
- `d:/AI/hd-instrument/notes/research_nonlinear_readout_frontier_2026-06-17.md` — readout-axis precedent (5 underexplored families)

---

### ANCHOR #2 — `substrate_bcpnn_W_readout_v1` (PRIORITY 2, gated on Anchor #1)

**Why now:** if Anchor #1 surfaces ARM_BCPNN as the strongest arm (Ravichandran 2024 3x lit precedent makes this the most likely outcome), the substrate gets a dedicated BCPNN cell at production scale.

**Substrate-product reading:** if BCPNN matches lit precedent (3x lift over additive Hebb on prototype-recall composite), then 30%-100% transfer to text8-LM regime gives top1 in [0.35, 0.45] single-arm. Composed with n1_v3 reach top1 > 0.50.

**Pre-reg HARD bands:**
- HARD-PASS: substrate_top1 >= 0.35 absolute at N_DIM=8192, V=4000, N_TRAIN=100k.
- MIDDLE_BAND: substrate_top1 in [0.27, 0.35].
- HARD_FAIL: substrate_top1 <= 0.27 (within +0.02 of cf-RPE family ceiling).

**Tier hint:** strongest lit precedent of the four families; brain-canonical (BCPNN biologically grounded in cortical microcircuit per Lansner 2009).

**Context pointers:**
- Same as Anchor #1, plus:
- BCPNN formula in research note section MECHANISM 1 — substrate-native HD-coded form
- Ravichandran NB et al. 2024 *PLOS-CB* arXiv:2401.00335

---

### ANCHOR #3 — `substrate_argmax_delta_W_v1` (PRIORITY 3, gated on Anchor #1)

**Why now:** if Anchor #1 surfaces ARM_ARGMAX_DELTA, this is the substrate's perceptron-class primitive. Forward-only, local-Hebbian. Composes with cf-RPE in a 2-phase rule.

**Substrate-product reading:** opens "fast hint via margin updates + slow distribution via cf-RPE" two-rule composition. Brain-canonical via three-factor gated plasticity (Fremaux-Gerstner).

**Pre-reg HARD bands:**
- HARD-PASS: substrate_top1 >= 0.32 absolute AND effective_update_fraction in [0.30, 0.80] (rule not collapsed).
- MIDDLE_BAND: substrate_top1 in [0.27, 0.32].
- HARD_FAIL: substrate_top1 <= 0.27 OR effective_update_fraction < 0.10 (rule starves) OR > 0.95 (rule never gates).

**Variant:** ARM_ARGMAX_DELTA_MARGIN — gate on margin_threshold = cos(W@src, C[target]) - cos(W@src, C[runner_up]) < tau. Always-on, threshold-modulated. Avoids self-saturation when most tokens become correct.

---

### ANCHOR #4 — `substrate_chl_W_v1` (PRIORITY 4, gated on Anchor #1)

**Why now:** Krotov 2024 MHC achieves MLP-class top1 on MNIST/CIFAR with LOCAL Hebbian — strongest single lit precedent that "right rule, not right readout" can deliver top1 lift. CHL is the closest backprop-analog under substrate's forward-only constraint. Foundational for the glass-box-LM direction.

**Substrate-product reading:** if CHL HARD-PASS, substrate has its first MLP-class plasticity primitive without backprop. Direct path to "glass-box LM INSIDE substrate" milestone.

**Pre-reg HARD bands:**
- HARD-PASS: substrate_top1 >= 0.32 absolute (= +47% relative over unigram).
- MIDDLE_BAND: substrate_top1 in [0.27, 0.32].
- HARD_FAIL: substrate_top1 <= 0.27.

---

### Composition cell — `substrate_plasticity_x_n1v3_compose_v1` (PRIORITY 5, gated on best-arm-from-#1)

**Why now:** after best plasticity arm lands, this cell tests whether plasticity x n1_v3 composes additively.

**Pre-reg HARD bands:**
- HARD-PASS (chain-grade-bonus single-arm): substrate_top1 > 0.50 absolute (= first substrate-LM to clear 0.50).
- HARD-PASS (chain-grade-eligible): substrate_top1 > 0.47 (clears bigram).
- MIDDLE_BAND: substrate_top1 in [0.45, 0.47] (matches n1_v3 alone — composition gives nothing).
- HARD_FAIL: substrate_top1 <= 0.45 (composition is destructive).

---

## Context pointers (file paths, not summaries)

- `d:/AI/hd-instrument/notes/research_top1_targeted_plasticity_2x_drill_2026-06-24.md` (this drill, full formulas + P estimates)
- `d:/AI/hd-instrument/notes/skunkworks_LANDED_VET_cfrpe_per_token_adaptive_lr_v1_MEASURED_MECHANISM_2026-06-24.md` (empirical anchor)
- `d:/AI/hd-instrument/notes/orchestrator_to_skunkworks_N1v3_FAIR_BPC_real_top1_unigram_level_perplexity_2026-06-21.md` (n1_v3 chain-grade reference)
- `d:/AI/hd-instrument/notes/research_brain_mechanisms_NOT_yet_tested_2x_drill_2026-06-24.md` (Block B "lateral inhibition")
- `d:/AI/hd-instrument/notes/research_2x_drill_ARCH_A_Drosophila_MIDDLE_BAND_linear_readout_ceiling_nonlinear_alternatives_2026-06-18.md` (DESIGN-INCOMPLETE-NOT-REFUTATION discipline; orthogonalize axes)
- `d:/AI/hd-instrument/notes/research_nonlinear_readout_frontier_2026-06-17.md` (readout-axis precedent)
- `d:/AI/hd-instrument/notes/research_dopamine_modulated_LR_alternatives_2x_drill_2026-06-23.md` (the prior 2x of plasticity-rule space; cf-RPE-modulation family)
- `d:/AI/hd-instrument/hdlab/ablation.py` (existing kWTA / lateral primitives in hdlab; may inform implementation reuse)
- `d:/AI/hd-instrument/experiments/exp_substrate_cfrpe_per_token_adaptive_lr_v1.py` (anchor cell for plasticity-cell scaffolding — copy + replace plasticity rule)

---

## Contract (per `[[feedback-no-experiment-design-in-prompts]]`)

- Research provides: anchor names, pre-reg HARD bands per anchor, P_deflated estimates, brain-literature provenance, formulas as starting point in research note.
- Exp_dev provides: cell-author cycle (cell scaffolding from anchor experiment; AST self-test; smoke gate with cell-author smoke + Fix #17 measurement + Fix #28 per-arm metric read; queue_add via path-scoped commit; remote-verify metrics path).
- Skunkworks provides: landed-VET cycle (recompute-off-per_seed; verify-off-data; cert routing per by-construction-saturation tiering; Fix #28 per-arm reads).
- Director (main thread) provides: USER-facing framing + atomic-write tooling per Track-A apply.

---

## Autonomy declaration

Per role contracts:
- exp_dev decides cell-author specifics (config defaults; smoke seed; AST self-tests; encoder choice within fair_harness constraint).
- Skunkworks decides cert routing (which tier; by-construction-saturation check; Fix #28 read; HARD_PASS/MIDDLE_BAND/HARD_FAIL band assignment).
- Research has provided pre-reg HARD bands; exp_dev MAY amend if cell-author surfaces honest implementation constraint (e.g., BCPNN log-form requires double-precision; substrate is float32 — substitute covariance-Hebbian subtractive form per research note MECHANISM 1).

---

## Pause-state check

- [ ] Before dispatching ANY anchor: check `d:/AI/hd-instrument/data/orchestrator_paused.flag` — if exists, do NOT dispatch; route via routing-handler to Director for ratification.

---

## Discipline cross-check

- [x] No experiment design in main thread per [[feedback-no-experiment-design-in-prompts]] — this hand-off file is the structural feed
- [x] Anchor names rank-ordered by P_deflated x test-coverage
- [x] Pre-reg HARD bands per anchor with substrate-product framing
- [x] Brain-existence-proof prior cited per arm
- [x] Lit-scan calibration penalty applied (0.20 deflation; novel-synthesis cap 0.50)
- [x] Discriminator (plasticity_rule axis; readout_axis_held_fixed) explicit per anchor
- [x] Context pointers as file paths, not summaries
- [x] ASCII-only; no emoji; no em-dash
