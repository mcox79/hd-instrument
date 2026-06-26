# exp_dev hand-off -- research: Modern Hopfield revival, slow-built basins

Filed-by: research sub-agent (Opus 4.7 1M)
Date: 2026-06-26
Trigger: notes/research_modern_hopfield_revival_slow_built_basins_2026-06-26.md
Urgency: HIGH -- Modern Hopfield prototype cell HARD_FAIL_MIDDLE_BAND_BELOW_FLOOR (0.22 vs 0.42 baseline vs 0.58 HRR_BUNDLE). Revival options ranked; cheap diagnostic gates the others.

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

### Anchor 1: mh_revival_feature_regime_diagnostic_v1 -- CHEAP DIAGNOSTIC; GATES OTHERS

Anchor pointer: Research note Section 1.1 + 1.2 + Cheap decisive test section.
Substrate-product reading: Tests whether the prior MH prototype cell HARD_FAIL was a REGIME-selection error (used softmax/prototype regime when feature-matching regime n=2 was the right choice for substrate's 20-instance basin scale). If feature regime n=2 lifts to >= 0.50 heldout, the prior cell's failure was regime, not mechanism, and substrate ships a soft-attention readout win without any new write-side machinery.
Tier hint: CPU laptop, ~1 hr (local_cpu_queue). CHEAPEST. Must run FIRST -- gates Anchors 2 and 3.
Why-now: Krotov 2016 explicitly characterizes two regimes (feature-matching small n vs prototype large n) in the same Modern Hopfield family. Substrate has 20 weak basins -- regime theory predicts feature-matching wins. ~1 hr of compute resolves the regime question and substrate-products a tier-1 lift if it works.

Pre-reg bands:
  HARD-PASS: ARM_HOPFIELD_N2 >= 0.50 heldout AND >= +0.15 over ARM_HOPFIELD_N20_SOFTMAX (the prior failure regime)
  MIDDLE-BAND: [0.35, 0.50] -- feature regime helps but not chain-grade; queue follow-up combining n=2 with light prototype refinement
  HARD-FAIL: ARM_HOPFIELD_N2 within 0.05 of ARM_HOPFIELD_N20_SOFTMAX -- regime is not the issue; pivot to Anchor 2 (STC slow-build)

Discriminator design: 4 arms at n in {2, 4, 10, 20} on SAME substrate W as the prior failed cell; same seed grid; cross-cell rail to prior cell's 0.22 baseline must hold within 0.02 on N=20 arm.

### Anchor 2: mh_revival_STC_consolidation_v1 -- USER's never-delete principle, mechanically

Anchor pointer: Research note Section 3 Mechanism B + Section 4.
Substrate-product reading: Implements synaptic-tagging-and-capture (STC) consolidation: tag bit per weight, per-row PRP (plasticity-related protein availability), W_slow consolidated matrix, capture rule that lets weak associations near strong recent events merge into the schema during sleep replay. Brain-aligned formalization of USER's "cold-storage / never-delete" principle. Composes with the in-queue BCM cell (`gap3_cls_two_tier_BCM_slow_replay_v1`): BCM is the encoding rule per replay event; STC is the cross-time consolidation rule deciding which writes get preserved.
Tier hint: CPU laptop, ~6-10 hr (local_cpu_queue). MEDIUM. Dispatch only if Anchor 1 HARD_FAIL or MIDDLE_BAND. Can run in parallel with the in-queue BCM cell.
Why-now: USER reframed REM homeostasis as cold-storage / merge-not-delete; this drill formalizes it as STC. First substrate dispatch of STC. Brain has strong existence proof (Frey-Morris 1997, Lehr 2021 RNNs). Substrate-novel composition.

Pre-reg bands:
  HARD-PASS: ARM_STC_FULL >= 0.65 heldout AND >= +0.15 over ARM_NO_STC AND >= +0.10 over ARM_STC_NO_PRP (capture rule must beat both baseline and tag-only)
  MIDDLE-BAND: [0.50, 0.65] -- STC builds schema but does not reach chain-grade; queue sweep over (tau_PRP, theta_capture, eta_capture)
  HARD-FAIL: All STC arms within 0.05 of baseline -- pivot to Anchor 3 (SDM, different mechanism class) or accept that substrate's data volume is the bottleneck

Discriminator design: 3 arms (NO_STC baseline / STC_NO_PRP capture-without-decay / STC_FULL full mechanism); per-arm metrics for PRP-firing-rate, capture-rate, tag-decay-rate (mechanism-internal diagnostics); free secondary metric = W_slow cosine matrix structure (within-category vs across-category cosine should diverge over training cycles).

### Anchor 3: mh_revival_SDM_online_v1 -- distinct mechanism class

Anchor pointer: Research note Section 3 Mechanism C.
Substrate-product reading: Sparse distributed memory with K=1000 hard locations and softmax pooling (per Bricken-Pehlevan 2021 attention-as-SDM mapping). Tests whether the slow-build direction is right but the SPECIFIC write rule (BCM, STC, or SDM) matters. Substrate's existing `iterative_attractor.iterative_cleanup` is approximately SDM with hard-locations = codebook entries; the MISSING piece is pooling-over-near-locations rather than argmax.
Tier hint: CPU laptop, ~3-5 hr (local_cpu_queue). MEDIUM. Useful as cross-mechanism rail to Anchor 2; dispatch after Anchor 1 + Anchor 2 (or in-queue BCM cell) land.
Why-now: Bricken 2023 ("SDM is a Continual Learner") demonstrates SDM's modern revival as a continual-learning primitive. Substrate has not tested SDM. Distinct mechanism class from BCM/STC.

Pre-reg bands:
  HARD-PASS: Any SDM arm >= 0.60 heldout AND >= +0.10 over HRR_BUNDLE baseline (0.58)
  MIDDLE-BAND: [0.50, 0.60] -- SDM helps but not by chain-grade margin
  HARD-FAIL: All SDM arms within 0.05 of HRR_BUNDLE -- pivot direction; bottleneck is data volume not mechanism class

Discriminator design: 3 arms (SDM_HARD_RADIUS / SDM_SOFTMAX = Bricken-Pehlevan attention / SDM_KANERVA_TRAINING with online hard-location refinement).

---

## Context pointers (file paths, not summaries)

- Research note this hand-off is filed against: `notes/research_modern_hopfield_revival_slow_built_basins_2026-06-26.md`
- Failed Modern Hopfield prototype cell data: `data/exp_modern_hopfield_prototype_attractor_v1/metrics.json` (MH_PROTO=0.22, MH_CONT=0.26, LIN_MEAN_PROTOTYPE=0.42, HRR_BUNDLE=0.58)
- Parallel BCM cell already in queue: `notes/research_gap3_brain_slow_schema_mechanism_2026-06-26.md` (gap3_cls_two_tier_BCM_slow_replay_v1, P=0.45)
- Prior Modern Hopfield drills: `notes/research_modern_hopfield_PCN_AM_universal_kernel_2x_2026-06-17.md`, `notes/research_modern_hopfield_capacity_retrieval_crossover_2026-06-16.md`, `notes/research_sparse_hopfield_win_regime_2026-06-16.md`
- NREM replay proven-bound: `notes/research_brain_hippocampal_SWR_sleep_replay_5x_drill_2026-06-22.md` (drift reduction +0.57 proven-bound)
- Substrate primitives:
  - `hdlab/iterative_attractor.py` -- existing cleanup; SDM extension target for Anchor 3
  - `hdlab/predictive_coding.py` -- existing `gated_write`; STC extension target for Anchor 2
  - `hdlab/continual.py` -- existing `replay_cycle` and `nrem_replay_decorator`
- Field advisor cues: `theoretical neuroscience` (CLS, STC, BCM, SDM) is fruit-bearing per Gap 3 drill; `materials-physics` and `inference` saturated per advisor.

---

## Contract

- exp_dev OWNS cell design from this point. Hand-off provides direction, anchors, and pre-reg bands; not implementation specifics.
- Per [[feedback-fix26-predispatch-verify-the-referent-gate]]: before dispatching Anchor 2 (STC), run `tools/predispatch_check.py mh_revival_STC` to verify no prior STC cell exists.
- Per [[feedback-fix28-verify-per-arm-metrics]]: all arms in all 3 cells must report per-arm metrics; verdict_msg insufficient for classification.
- Per [[feedback-foreground-vs-background-for-sequential-store-ledger-writes]]: if cell composes Store + cert_ledger writes, use foreground dispatch.
- Per pause-gate convention: check `data/orchestrator_paused.flag` before dispatch.
- Anchor 1 IS the gate. Dispatch sequence:
  1. Anchor 1 first (1 CPU-hr). Land. Read per-arm metrics.
  2. If HARD_PASS: ship as substrate-product win; queue Anchor 2 for combined-mechanism test.
  3. If HARD_FAIL or MIDDLE_BAND: dispatch Anchor 2 in parallel with the in-queue BCM cell.
  4. Anchor 3 after Anchor 1 + (Anchor 2 OR BCM cell) land.

---

## Autonomy declaration

exp_dev has full autonomy on:
- Specific n values within feature-regime sweep (the 4-arm grid {2, 4, 10, 20} is a default; exp_dev may refine).
- STC mechanism hyperparameters (theta_tag, theta_strong, theta_capture, tau_PRP, eta_capture, decay rate). The research note gives default seeds; exp_dev tunes.
- SDM hyperparameters (K hard locations, Hamming radius, softmax beta). Bricken-Pehlevan 2021 gives published defaults; exp_dev adapts to substrate scale.
- Seed grid, dimension N, instance counts -- exp_dev should match the prior failed MH cell's grid for cross-cell rail integrity.
- Cell author smoke test (per Fix #14/Fix #17/Fix #20/Fix #21 disciplines).
- Whether to combine Anchor 2 STC with the in-queue BCM cell into one cell with both write rules active (RECOMMENDED if Anchor 1 HARD_FAIL).

---

-- Research (Opus 4.7 1M; 6 parallel WebSearch lit-scans; calibrated per discipline; HARD-FAIL thresholds pre-registered).
