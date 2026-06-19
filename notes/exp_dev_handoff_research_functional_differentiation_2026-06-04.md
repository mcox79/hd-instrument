# exp_dev hand-off -- research: functional-differentiation-substrate-regions

**Filed-by**: research sub-agent (sonnet), 2026-06-04
**Trigger**: research_drill_functional_differentiation_substrate_regions_3x_2026-06-04.md
**Pause state**: check data/orchestrator_paused.flag before dispatching any anchor

Per [[feedback-no-experiment-design-in-prompts]]: this file hands task + why + context
pointers to exp_dev. It does NOT specify sweep grids, exact threshold formulas, queue
choice, or pre-committed cap_map decisions. exp_dev resolves those autonomously.

---

## Anchor Candidates (rank-ordered)

### Anchor 1 (Tier: CHEAP DECISIVE TEST -- run first)
**What**: Two-region substrate vs monolithic at matched parameter budget.
  - Region A: slow Hebbian outer-product write (current architecture), N_A=2048
  - Region B: sparse Hebbian write with sparse random projection phi (sparseness ~0.05),
    high learning rate (eta_B ~ 10x eta_A), novelty-gated activation, N_B=2048
  - Baseline: monolithic substrate N=4096 (current architecture, same W param count)
  - Metric: BPC on held-out text after same number of training steps

**Why now**: CLS theory predicts the first functional differentiation gain appears at
the cortical-class + hippocampal-class split (not the BG or cerebellum classes). This
is the minimum falsifiable test. If no gain here, the 4-region architecture is unlikely
to help. If gain appears, it justifies the full 4-region build.

**Substrate-product reading**: Region B (hippocampal-class sparse write) maps directly
to the "per-fact retention policy" and "rapid one-shot binding" killer features. If the
2-region test passes, it provides the first empirical anchor for those product claims.

**Tier hint**: cheap -- same wall as current ablation run; local GPU sufficient;
requires implementing sparse random projection phi and novelty routing signal only.

**Pre-reg anchor pointer**: research note Section "Cheap Decisive Test" + FP3 prediction.
  HARD PASS: BPC improvement > 0.10 nats over monolithic at matched N
  HARD FAIL: BPC regression > 0.05 nats (functional differentiation actively hurts)

---

### Anchor 2 (Tier: MEDIUM -- contingent on Anchor 1 result)
**What**: Four-region substrate vs monolithic at matched parameter budget (N_region=2048
each, 4 regions, total params matched to single N~4096).
  Add Region C (BG-class: reward-gated write, delta_bpc gating) and Region D
  (cerebellum-class: anti-Hebbian spectral correction targeting kappa_3).
  Add 2-signal binary router (novelty signal + BPC delta sign signal).

**Why now**: Only if Anchor 1 shows positive gain. The 4-region architecture requires
more engineering work; do not build until the 2-region case confirms the core hypothesis.

**Substrate-product reading**: Full 4-region architecture enables all 4 killer features
simultaneously. Region C enables "edit-with-impact-prediction"; Region D enables
"live drift detection."

**Tier hint**: medium -- requires implementing 2 new write rule classes and routing;
probably 1-2 eng-days before GPU run.

---

### Anchor 3 (Tier: ALGEBRAIC CHECK -- no GPU, cheap CPU or theory-only)
**What**: Verify Treves-Rolls CA3 capacity formula for discrete bipolar substrate.
  Check whether M_CA3 ~ 0.038 * N / (a * log(1/a)) holds when the underlying
  storage rule uses bipolar +/-1 states (vs continuous activations assumed in
  original Treves-Rolls derivation).

**Why now**: FP3 in the research note makes a prediction about Region B capacity that
depends on this formula. If it fails for bipolar states, the hippocampal-class region
needs a corrected capacity estimate before the empirical test is pre-registered correctly.

**Tier hint**: algebraic derivation + minimal CPU verification; ~1 day theory work.

---

## Context Pointers

- Research note: d:/AI/hd-instrument/notes/research_drill_functional_differentiation_substrate_regions_3x_2026-06-04.md
- Cap map: d:/AI/hd-instrument/data/cap_map.md (check Cap 2, Cap 3, Cap 4 rows)
- Recent ablation data (5-arm result): check data/Research/ for most recent 5-arm ablation
  output -- this is the "all variants BPC 3.73-3.81" result that motivates this work
- CLS theory: McClelland et al. 1995 (PMID 7624455), Kumaran et al. 2016 (PMID 27315762)
- DeltaNet hybrid gain: arXiv 2406.06484 (closest published analog for heterogeneous write)

---

## Contract

exp_dev MUST:
- Read this file + the research note BEFORE designing any anchor
- Pre-register HARD-PASS / MIDDLE-BAND / HARD-FAIL thresholds for each anchor it ships
- Verify parameter count is truly matched between monolithic baseline and multi-region
  candidate before shipping (the research note flags a 4x parameter mismatch risk if
  N_region=1024 is used; N_region=2048 is the correct matched configuration)
- Check data/orchestrator_paused.flag before any queue_add call
- Check queue dedup before ship (per [[feedback-ship-name-collision]])

## Autonomy Declaration

exp_dev decides:
- Exact sparse random projection phi implementation (random matrix vs learned)
- Novelty threshold theta_novelty value and measurement method
- Whether to run Anchor 3 (algebraic check) before or in parallel with Anchor 1
- Queue assignment (CPU vs GPU) based on smoke wall estimate
- Whether Anchor 2 is ready based on Anchor 1 result
- Cap_map update if Anchor 1 HARD PASSes (exp_dev writes; orchestrator commits)
