# exp_dev hand-off - research: A1 composition collapse 3rd angle test-design audit

**Filed by:** research (Opus 4.7-1M)
**Date:** 2026-06-24
**Trigger:** USER standing rule "drill all negatives 3x"; 3rd angle drill on A1 5-primitive composition collapse complete; finding is actionable (proposes cheap decisive cell)
**Cite:** `notes/research_a1_composition_collapse_3rd_angle_test_design_audit_2026-06-24.md`

**Pause state:** check `data/orchestrator_paused.flag` before dispatch.

**Per [[feedback-no-experiment-design-in-prompts]]:** the substrate-product reading + tier hint + why-now + pre-reg bands are below. exp_dev decides cell name, file structure, sweep mechanics, smoke design, and dispatch routing. Research does not pre-design the cell.

---

## Anchor candidates (rank-ordered)

### Anchor 1 (PRIMARY, ~45min CPU) - test-design audit decisive cell

**Anchor pointer:** test whether A1's HARD_FAIL recovers under three targeted design fixes (MH disabled, extended TEMP_GRID, MH_BETA sweep). Optional 4th arm: all three fixes combined.

**Substrate-product reading:** if HARD_PASS, A1's cap_map flips from HARD_FAIL to MIDDLE_BAND or HARD_PASS - substrate compose is alive on properly designed test. If HARD_FAIL, confirms structural diagnosis from angles 1 & 2.

**Tier hint:** MEASURED_MECHANISM-eligible (diagnostic single-hypothesis test); not chain-grade by itself, but flips cap_map row if HARD_PASS.

**Why-now:** USER explicitly asked for 3rd-angle drill on A1 negative. Without this cell, the structural-diagnosis vs test-design-artifact question stays open. Cheap (45min CPU) compared to cells that would test angle-2 structural fixes (multi-month).

**Pre-reg HARD bands (both directions; research-supplied):**
- HARD_PASS: ARM_DESIGN_FIX_COMBINED BPC <= 7.00 (matches or beats cf-RPE-only 7.09) OR ARM_DESIGN_FIX_1_NO_MH_CLEANUP BPC <= 7.20
- HARD_FAIL: ARM_DESIGN_FIX_COMBINED BPC >= 7.30 AND ARM_DESIGN_FIX_1_NO_MH_CLEANUP BPC >= 7.30
- MIDDLE_BAND: BPC in [7.00, 7.30] at best fix-arm - ~50% design-artifact, remainder structural
- HARD_FAIL_PROVENANCE: ARM_CONTROL_REPRODUCE_A1 != A1 baseline 7.89 (drift >0.10)

**Arms suggestion (exp_dev decides exact structure):**
- ARM_DESIGN_FIX_1_NO_MH_CLEANUP: A1 FULL_JOINT minus MH cleanup (isolates MH-as-cause)
- ARM_DESIGN_FIX_2_EXTENDED_T_GRID: A1 FULL_JOINT with TEMP_GRID extended to include {2, 5, 10, 20, 50}
- ARM_DESIGN_FIX_3_LOW_BETA_MH: A1 FULL_JOINT with MH_BETA sweep {1, 2, 4} (3 sub-configs)
- ARM_DESIGN_FIX_COMBINED: all three fixes simultaneously
- ARM_CONTROL_REPRODUCE_A1: original A1 FULL_JOINT (control - should reproduce 7.89 BPC)

**Config:** N_DIM=8192, V=4000, N_TRAIN=100k, 3 seeds (7, 17, 23). Reuse A1 cell code. ~45min CPU local.

### Anchor 2 (CONDITIONAL on Anchor 1 MIDDLE_BAND or HARD_FAIL, ~6-8h GPU) - factorial 4-way

**Anchor pointer:** map the compose-interaction tensor empirically via 2^4=16 arm factorial over {cf-RPE, STDP, K=2, MH}. Each arm at 3 seeds.

**Substrate-product reading:** if Anchor 1 is partial-fix (MIDDLE_BAND), need to localize WHICH interactions destruct vs which super-add. The factorial tensor tells you BPC(combo) - sum(BPC(individual)) for every 2/3/4-way combo.

**Tier hint:** MEASURED_MECHANISM (diagnostic full-factorial); chain-grade-eligible if any 3-way or 4-way combo HARD_PASSES.

**Why-now:** only if Anchor 1 doesn't give a clean answer. ~6-8h GPU on overnight_queue.

**Pre-reg HARD bands:**
- HARD_PASS: at least one 3-way or 4-way arm BPC <= 6.90 (super-additive)
- HARD_FAIL: all 16 arms BPC >= 7.30 (no compose at all)
- Discriminator: per-pair interaction term sign + magnitude, mapped to interaction matrix

### Anchor 3 (DEFERRED, ~3h CPU) - MH replacement variants

**Anchor pointer:** test alternative cleanup primitives in the MH slot - SDM (Kanerva), k-WTA soft sharpening, low-β MH. Each as a swap for MH at the end of the pipeline.

**Substrate-product reading:** if MH-specific bug, alternative cleanup may recover compose. If no cleanup helps, motivates a deeper cleanup-as-readout structural redesign.

**Tier hint:** novel-synthesis (cap P=0.40); chain-grade-eligible if any alternative reaches BPC <= 6.95.

**Why-now:** only if Anchor 1 confirms MH-specific bug but full design-fix doesn't reach HARD_PASS.

---

## Context pointers (file paths, not summaries)

- Research note (this drill, the source for all reasoning): `notes/research_a1_composition_collapse_3rd_angle_test_design_audit_2026-06-24.md`
- Angle 1 (logit-distribution-shape diagnosis): `notes/research_composition_collapse_critical_drill_2026-06-24.md`
- A1 cell source (line-by-line audit was performed here): `experiments/exp_substrate_compose_fair_harness_cfrpe_hetplasticity_K2_modern_hopfield_cleanup_v1.py`
- A1 metrics (verdict HARD_FAIL FULL_JOINT BPC=7.89): `data/exp_substrate_compose_fair_harness_cfrpe_hetplasticity_K2_modern_hopfield_cleanup_v1/metrics.json`
- Cross-cell super-additive precedent (HARD_PASS 5/5 seeds): `data/exp_substrate_cfrpe_stdp_heterogeneous_superadditive_bigram_v1_n512/metrics.json`
- Cross-cell super-additive source: `experiments/exp_substrate_cfrpe_stdp_heterogeneous_superadditive_bigram_v1_n512.py`
- MH primitive certification (pattern completion regime): `data/exp_modern_hopfield_n_sweep_v1/metrics.json`
- MH primitive source (self-test scope evidence): `experiments/exp_modern_hopfield_n_sweep_v1.py`
- N_STEPS asymptote MEASURED_MECHANISM ruling: `notes/skunkworks_LANDED_VET_cfrpe_n_steps_curve_v1_MEASURED_MECHANISM_2026-06-24.md`
- N_STEPS curve metrics: `data/exp_substrate_cfrpe_n_steps_curve_v1/metrics.json`
- het_plasticity reference (cf-RPE+STDP at production scale, HARD_PASS lift=0.141): `data/exp_substrate_heterogeneous_plasticity_cfrpe_stdp_fair_harness_v1/metrics.json`
- K=2 x cf-RPE reference (HARD_FAIL ref): `data/exp_substrate_K2_x_cfrpe_compose_word2vec_v2/metrics.json`

---

## Contract

This hand-off is structural to the research-to-experiment feed. exp_dev:
- Reads this file AND the research note above
- Decides cell file path + name (suggestion: `experiments/exp_substrate_compose_test_design_audit_v1.py`)
- Designs the exact cell structure, smoke gate, sweep mechanics, pre-reg note, and dispatch routing
- Does NOT inherit research's suggested arm/config choices uncritically (research can be wrong about exact mechanics)
- Files pre-reg note before dispatch per envelope-fail-bands discipline
- Routes per Fix #14 spawn budget (~3 in flight), Fix #20 (no pipe-tail subprocess monitoring), Fix #24 (GPU dispatch must actually use GPU - this cell is CPU-eligible so route to local_cpu_queue), Fix #28 (per-arm metrics verification, not verdict_msg framing)

## Autonomy declaration

exp_dev has full autonomy over cell mechanics. Research provides:
- The motivation (3rd-angle drill on A1 negative)
- The substrate-product reading per anchor
- The pre-reg HARD bands (both directions)
- The cross-cell precedent (cf-RPE+STDP super-additive on bigram cell)
- The 5 design-bias list (for cell-author reference)
- The context pointer set (file paths, not summaries)

Research does NOT specify: cell file name, exact arm structure, smoke configuration, sweep grid mechanics, MH variant choice, file system layout, queue routing logic, atomize sequencing.

---

## Routing note

If exp_dev is paused or has >=3 spawns in flight, this hand-off can wait. The 3rd-angle drill is complete in the research note; the test-design audit findings stand independent of whether the cell ships immediately. Anchor 1 is cheap (45min CPU local) so should fit a normal pipeline-refill cycle.

If user wants this cell ASAP, the routing recommendation is local_cpu_queue (CPU is fine; matmul-bound but already optimized in A1 source).
