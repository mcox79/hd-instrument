# exp_dev hand-off — research: brain-to-LM relevance audit (2x drill)

Filed-by: research sub-agent (Opus synthesis over 8 parallel WebSearch lit-scans)
Date: 2026-06-23
Trigger: notes/research_brain_to_lm_relevance_audit_2x_drill_2026-06-23.md
Urgency: MEDIUM-HIGH — three CONFIRMED brain-grounded gaps with substrate-readiness; meta-learning anchor (CLAIM 8) is the highest-leverage single-cell candidate after current arc

---

## Pause state

Experiments below are PROPOSED, not queued. Pause gate applies per normal exp_dev protocol.
Check data/orchestrator_paused.flag before dispatching.

---

Per [[feedback-no-experiment-design-in-prompts]]:
This file provides ROUTING POINTERS and ANCHOR CANDIDATES only.
Experiment design details (cell grids, hyperparameter values, script paths) are to be authored by exp_dev from the research note + cap_map context. Do NOT treat the descriptions below as implementation specs.

---

## Anchor candidates (rank-ordered)

### Anchor 1: substrate_meta_lr_dopamine_analog_v1 (PRIMARY)

Anchor pointer: Research note CLAIM 8 verdict (A) + Per-claim table row 8 + Priority queue item #1
Substrate-product reading: Tests whether substrate-native adaptive learning rate (RPE-modulated, dopamine-analog) closes the highest-evidence brain-LM gap. AWD-LSTM + meta-learner achieves 46.9 vs 64.8 perplexity on WikiText-2 (~28% reduction). Substrate has modulatory primitives (per modulatory_architectural_parameter_taxonomy 2026-06-23); this cell tests whether per-token RPE-modulated learning rate produces measurable BPC lift on text8 LM next-token prediction.
Tier hint: GPU remote, ~30-40min wall time. 3 arms (FIXED_LR baseline / GLOBAL_RPE_LR / PER_TOKEN_RPE_LR) x 3 seeds x text8 N_TRAIN=100k.
Why-now: Highest LM-evidence-strength of all 8 audited claims; substrate has the primitives; cheap-decisive. Director's "Tier 11 wide open" framing is justified — this is the concrete cell to ship.

Pre-reg bands:
  HARD-PASS: ARM_PER_TOKEN_RPE_LR BPC lift >= +0.15 bits vs ARM_FIXED_LR baseline AND >= +0.05 bits vs ARM_GLOBAL_RPE_LR (per-token adaptive granularity matters)
  MIDDLE-BAND: ARM_PER_TOKEN_RPE_LR beats FIXED_LR by +0.05 to +0.15 bits
  HARD-FAIL: ARM_PER_TOKEN_RPE_LR within +/-0.05 of FIXED_LR baseline => meta-learning gap is NOT load-bearing for substrate-LM at this scale; recast as "needs structural prerequisite" investigation
  CV < 0.05 across seeds mandatory; per-arm metrics via tools/peek_arm_metrics.py per Fix #28

### Anchor 2: substrate_fast_slow_weights_v1 (PARALLEL-RECOMMENDED to Anchor 1)

Anchor pointer: Research note CLAIM 5 verdict (A) + Priority queue item #3
Substrate-product reading: Tests whether substrate fast-weight overlay (decay τ=10-100 tokens) on top of slow-weight V_C codebook produces in-context-adaptation lift. Hinton-Plaut 1987 + Ba 2016 lineage; multi-timescale plasticity is canonical brain-LM mechanism. Substrate's V_C codebook = slow weights; per-token state can be reframed as fast weights. Two-timescale arm vs single-timescale baseline isolates the gap.
Tier hint: GPU remote, ~40-60min wall time. 3 arms (SINGLE_TS baseline / FAST_TAU_10 / FAST_TAU_100) x 3 seeds x text8.
Why-now: Second-highest LM-evidence; complementary to Anchor 1 (RPE-modulation IS the gradient-signal for fast weights). If both PASS, the next-cycle cell tests their composition.

Pre-reg bands:
  HARD-PASS: ARM_FAST_TAU_10 OR ARM_FAST_TAU_100 BPC lift >= +0.10 bits vs SINGLE_TS baseline
  MIDDLE-BAND: lift +0.05 to +0.10 bits
  HARD-FAIL: lift < +0.05 bits => fast-slow split is NOT load-bearing at substrate scale; gap downgrades to "training-dynamics nice-to-have"

### Anchor 3: substrate_iteration_count_ablation_v1 (CHEAP MARGINAL TEST)

Anchor pointer: Research note CLAIM 3 verdict (C → leaning A) + LoopUS/LoopFormer evidence
Substrate-product reading: Resolves the CLAIM 3 ambiguity. Lit shows diminishing-returns lift with iteration; substrate-side measurement settles whether to add iterative refinement as Tier-bump option. Three arms: 1-iter / 3-iter / 7-iter on substrate cleanup at fixed encoder. If gain at 7-iter is < 2% vs 1-iter, mark CLAIM 3 OVER-MAPPED; if > 5%, mark as marginal-gap and bump iteration-budget Tier.
Tier hint: GPU remote, ~20-30min wall time. 3 arms x 3 seeds; cheap.
Why-now: Resolves an unresolved verdict cheaply; output directly updates substrate→brain mapping (de-list or keep CLAIM 3).

Pre-reg bands:
  HARD-PASS (real-gap): 7-iter > 1-iter by >= +5% perplexity; bump iteration as Tier option
  MIDDLE-BAND: 2-5% gain at 7-iter
  HARD-FAIL (over-mapped): < 2% gain at 7-iter => remove from gap list

### Anchor 4: substrate_cell_type_ablation_diagnostic_v1 (CONTINGENT on Anchor 1+2 yielding meaningful lift)

Anchor pointer: Research note CLAIM 7 verdict (C) — only relevant if substrate-LM is on a productive trajectory
Substrate-product reading: Tests whether substrate's single-threshold + soft-WTA is sufficient or whether multi-cell-type analog (gain-normalization arm + disinhibition arm) provides LM lift. Lit shows +20% accuracy on Vision Transformer with sWTA module but NO direct language evidence. Conservative: only run after Anchor 1+2 establish substrate-LM has lift-headroom; otherwise wasted compute.
Tier hint: GPU remote, ~45-60min wall time. 3 arms (SINGLE_THRESH baseline / GAIN_NORM / DISINHIB) x 3 seeds.
Why-now: Lower priority than meta-LR + fast-slow because lit evidence is vision-only. CONDITIONAL anchor; defer if Anchors 1+2 hit MIDDLE-BAND or worse.

Pre-reg bands:
  HARD-PASS: either modulatory arm gives >= +0.05 bits BPC vs baseline
  HARD-FAIL: both arms within +/-0.02 of baseline => CLAIM 7 confirmed OVER-MAPPED for LM (vision-only mechanism)

---

## Anti-anchors (DO NOT spawn experiments for these — CLAIM verdicts already resolved)

Per CLAIM 2 (theta-gamma OVER-MAPPED for LM): do NOT dispatch theta-gamma phase-coding cells targeting next-token prediction. Director's prior dispatch of `exp_dev_handoff_research_theta_gamma_SNR_compensation_brain_mechanism_2026-06-23.md` may need re-scoping — it's likely valid for SNR-compensation but should not be framed as LM-prediction gap closure.

Per CLAIM 4 (continuous-time OVER-MAPPED): do NOT dispatch continuous-time membrane integration cells; SpikeLLM/SpikeGPT already showed discrete is sufficient.

Per CLAIM 1 (bidirectional PC OVER-MAPPED at inference): do NOT dispatch PC-inference-feedback cells. If substrate-native local-credit-assignment is a separate research question, route it as a NEW drill (not this one).

---

## Context pointers (file paths only, exp_dev reads them)

- d:/AI/hd-instrument/notes/research_brain_to_lm_relevance_audit_2x_drill_2026-06-23.md  (this drill — load-bearing)
- d:/AI/hd-instrument/notes/research_neuromodulator_orthogonal_composition_brain_mechanism_2026-06-23.md  (CLAIM 8 mechanism detail)
- d:/AI/hd-instrument/notes/research_substrate_modulatory_architectural_parameter_taxonomy_2026-06-23.md  (substrate's modulatory primitives — what's available for Anchor 1)
- d:/AI/hd-instrument/notes/research_brain_continual_learning_CLS_5x_drill_2026-06-22.md  (CLAIM 5 fast-slow mechanism detail)
- d:/AI/hd-instrument/notes/research_brain_hippocampal_SWR_sleep_replay_5x_drill_2026-06-22.md  (CLAIM 6 confirmation; relevant for follow-up CLS-replay cell)
- d:/AI/hd-instrument/tools/peek_arm_metrics.py  (Fix #28 mandatory pre-framing check)
- d:/AI/hd-instrument/tools/predispatch_check.py  (Fix #26 pre-dispatch verify)

---

## Contract

- Pre-reg per envelope-fail-bands (Fix #19; bands stated above for each anchor)
- Smoke gate via tools/predispatch_check.py before cell-author spawn (Fix #26)
- Per-arm metrics via tools/peek_arm_metrics.py before any tier/framing claim (Fix #28)
- Foreground Store + cert_ledger writes (Fix #20: no background pipe-tail monitoring)
- Verify-the-referent on cross-arm metrics (Fix #28 recurring)
- GPU dispatch must actually use GPU (Fix #24): torch.cuda + batched ops + concurrent-seed harness
- Default classification = MM not chain-grade; let Skunkworks tier UP (Fix #28 recurring 2026-06-23)

## Autonomy declaration

exp_dev decides:
- Exact substrate scaffold to extend (existing baseline cell vs fresh cell vs fork prior modulatory cell)
- Hyperparameter grids within pre-reg bands
- Smoke-test data slice
- Whether Anchor 3 (cheap iteration ablation) can be parallelized into the same dispatch as Anchor 1 to save spawn-budget
- Whether to defer Anchor 4 until Anchor 1+2 results land

Research does NOT decide implementation. This is a routing pointer.
