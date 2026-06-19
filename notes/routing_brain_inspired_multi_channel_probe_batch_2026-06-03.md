# ROUTING — Brain-inspired multi-channel substrate probe batch (3 experiments)

**From:** Research session
**To:** Orchestrator + Testbed
**Date:** 2026-06-03
**Status:** USER AUTHORIZED 2026-06-03 ($15-20 total cloud + ~1-2 days wall).
**Discipline:** plain-language experiment naming per `feedback_plain_language_experiment_tracking`; pre-registered HP/MID/HF bands per probe; cell-design parameters specified. Per-PROT compliance.

---

## 0. WHAT THIS BATCH IS (plain language)

Three small empirical experiments testing whether substrate can serve as a multi-channel training-signal source for LLM training, analogous to how brain neuromodulators provide parallel training signals (dopamine, acetylcholine, etc.). Each experiment tests one specific brain-analog channel + has a measurable product-capability claim. All three are cheap. Total batch: ~$15-20 cloud, ~1-2 days wall.

The three experiments are derived from three brain-inspired research drills landed 2026-06-03 (cascade drills on substrate-multi-channel LLM training).

---

## 1. THE THREE EXPERIMENTS

### Experiment A — Data attribution via substrate counterfactual (dopamine-RPE analog)

**Anchor name:** `substrate_data_attribution_counterfactual_rpe_v1_n4096`

**Plain-language description:** Tests whether substrate can identify which training examples contributed to which model behaviors, at 10-100× lower compute than TracIn (the current published-best data-attribution method). The substrate primitive doing the work is counterfactual rank-1 substitution ("what would retrieval have been if a specific stored pattern had been different"). Theoretically maps onto dopamine reward-prediction-error — same bipolar difference signal, same credit-assignment-via-history mechanism.

**Resource:** local CPU
**Wall:** <10 minutes
**Cost:** $0
**P_deflated:** 0.38

**Test design:**
- Synthetic corpus with KNOWN per-example contribution to a small model's final loss
- Substrate observes the model; computes counterfactual ranking of training examples
- Compare substrate ranking against ground-truth contribution ranking via rho correlation
- 5 seeds

**Pre-registered bands:**
- HARD-PASS: rho > 0.8 across 5 seeds (substrate matches expensive attribution methods)
- MIDDLE: rho in [0.5, 0.8]
- HARD-FAIL: rho < 0.3 (substrate provides no attribution signal)

**exp_dev handoff (already on disk):** `notes/exp_dev_handoff_research_counterfactual_rpe_training_2026-06-03.md`

### Experiment B — Training-phase prediction via substrate spectral fingerprint (acetylcholine-novelty analog)

**Anchor name:** `substrate_spectral_training_monitor_predictive_v1_gpt2small`

**Plain-language description:** Tests whether substrate can predict LLM training-phase changes (convergence onset / overfitting onset / divergence) 100-500 training steps BEFORE conventional loss-curve indicators reveal them. The substrate primitive doing the work is free-cumulant spectral fingerprint (kappa_2, kappa_3, kappa_4) of residual-derived weight matrix. Theoretically maps onto acetylcholine novelty signaling (Yu-Dayan 2005) — substrate signals "expected uncertainty" prospectively, before behavior signals it.

**Resource:** cheap cloud GPU (T4 or RTX 4090) — or local GPU if available
**Wall:** ~1-2 GPU-hours
**Cost:** ~$2
**P_deflated:** 0.38

**Test design:**
- Train GPT-2-small or smaller transformer LM with standard cross-entropy loss
- Attach substrate observer to layer 0.7L; compute spectral fingerprint trajectory across training
- Annotate ground-truth training phases (convergence onset / overfitting onset / divergence) from held-out validation loss
- Measure predictive lead time: does substrate spectral trajectory cross threshold N steps before validation-loss-curve crosses corresponding threshold?
- 3 seeds

**Pre-registered bands:**
- HARD-PASS: substrate signals each phase change ≥ 100 steps before validation-loss indicator AND across 3 seeds
- MIDDLE: lead time 50-100 steps OR 2/3 seeds
- HARD-FAIL: substrate signal lags or matches validation loss (no predictive lead)

**Strategic gain if HP:** auto-stop saves 10-20% LLM training compute (~$100-200K per Llama-class model).

**exp_dev handoff (already on disk):** `notes/exp_dev_handoff_research_spectral_cumulant_training_monitor_2026-06-03.md`

### Experiment C — Multi-channel orchestration ablation (Friston precision + LC + BG analog)

**Anchor name:** `substrate_8channel_orchestration_ablation_gpt2small_v1`

**Plain-language description:** Tests whether running multiple substrate channels jointly during LLM training beats running fewer channels, validating that brain-style multi-channel orchestration works in this regime. Specifically: trains GPT-2-small with 1 channel (CE-only baseline) vs 4 channels (CE + 3 substrate signals) vs 8 channels (CE + 7 substrate signals). The architectural pattern (4 tonic always-on + 4 phasic event-triggered with PCGrad conflict resolution and layer-zone gain) mirrors brain neuromodulator orchestration via Friston precision-weighting + locus coeruleus phasic/tonic split + basal ganglia gating.

**Resource:** cloud GPU (T4 or A100)
**Wall:** 4-8 GPU-hours
**Cost:** ~$10-15
**P_deflated:** 0.38

**Test design:**
- GPT-2-small (~117M params)
- 3 channel-count conditions: 1-channel (CE baseline) / 4-channel (CE + 3 substrate) / 8-channel (CE + 7 substrate)
- Training: 50k steps per condition
- 3 seeds per condition
- Metric: BLiMP grammaticality score (held-out)
- Track gradient norm (sanity check that PCGrad projection doesn't collapse it)

**Pre-registered bands:**
- HARD-PASS: 8-channel beats 1-channel by > 5% on BLiMP AND beats 4-channel by > 2% AND no majority-antagonistic channel pairs detected AND gradient norm stays above 1% of input
- MIDDLE: 8-channel beats 1-channel by > 2% but < 5% OR doesn't beat 4-channel
- HARD-FAIL: 8-channel < 4-channel OR PCGrad projection collapses gradient norm < 1% of input

**Strategic gain if HP:** 15-30% fewer training steps + 2-5% OOD accuracy gain + substrate-native auto-curriculum. Substrate as brain-inspired multi-channel LLM-training infrastructure validated at small scale.

**exp_dev handoff (already on disk):** `notes/exp_dev_handoff_research_8channel_orchestration_2026-06-03.md`

---

## 2. STATUS-CHECK REQUEST (per workflow rule)

Before dispatching, please verify:

- [ ] Has Experiment A (`substrate_data_attribution_counterfactual_rpe_v1_n4096`) already been dispatched / engineered / run?
- [ ] Has Experiment B (`substrate_spectral_training_monitor_predictive_v1_gpt2small`) already been dispatched / engineered / run?
- [ ] Has Experiment C (`substrate_8channel_orchestration_ablation_gpt2small_v1`) already been dispatched / engineered / run?

Expected answer: NONE have been dispatched (these are new experiments derived from cascade drills landed today; not in prior routings or `experiment_queue_pending.md`).

If any HAS been dispatched somehow → confirm status to research session; do not re-dispatch.
If NONE dispatched → proceed per §3 below.

---

## 3. DISPATCH INSTRUCTIONS

**IF NONE dispatched (expected case):**

- Add all 3 experiments to `notes/experiment_queue_pending.md`
- Experiment A is CPU-only and the cheapest; can dispatch immediately to local CPU runner
- Experiment B + C need cheap cloud GPU; can share single Lambda T4 or RTX 4090 bootstrap if scheduled together
- All 3 can run in parallel where resources allow
- Pre-registered bands per §1 above
- exp_dev handoffs already on disk for each (paths in §1)
- Cost ceiling: $20 total (alert at $15)
- Status-log updates per `feedback_for_you_tab_primary_channel` at: each experiment launch + each verdict + final batch synthesis

---

## 4. CONTEXT FOR ORCHESTRATOR + TESTBED

These three experiments emerged from a deliberate research-cascade:

- A foundational drill on substrate-as-LLM-training-mechanism identified 12 substrate primitives that map onto 8 independent training-signal channels (NO published LLM training uses more than 2 channels)
- Three follow-on cascade drills probed the three most-promising brain-inspired channels (dopamine-RPE / acetylcholine-novelty / Friston-precision-weighted orchestration)
- Each cascade drill produced (a) clean theoretical brain-biology mapping, (b) concrete measurable product capability, (c) cheap empirical probe with HP/MID/HF bands

The user explicitly authorized this batch with directive: brain-training speculation OK; pursue the most aggressive substrate-multi-channel-LLM-training claims with cheap empirical validation.

---

## 5. CAP_MAP IMPACT IF BATCH ALL-HP

If all 3 experiments HARD-PASS:
- Substrate-as-multi-channel-LLM-training story has 3 independent empirical anchors at brain-inspired channels
- Three NEW substrate-capability-row candidates founded (data-attribution / training-monitor / multi-channel-orchestration)
- Sets up Phase E candidate: full-pipeline substrate-native training at Pythia-160M scale with 8 channels orchestrated
- Substrate's product narrative gains 3 dollar-denominated capability claims

If MIDDLE outcomes: which subset of channels work informs next-cycle design refinement
If HARD-FAIL outcomes: each tells us a specific brain-analog channel doesn't transfer cleanly to this substrate class; informs scope reduction

---

## 6. DISCIPLINE DECLARATIONS

- Per `feedback_plain_language_experiment_tracking`: each experiment described in plain language; anchor names as backup labels
- Per `feedback_change_request_protocol`: this is a NEW routing (not a change to existing experiments), but follows the status-check-first discipline anyway
- Per `feedback_no_padding_experiments`: each of 3 experiments tests a distinct brain-analog channel + has a concrete product capability + is cheap
- Per `feedback_no_smoke_preframing_in_task_prompts`: HARD-FAIL trip-wires explicit
- Per `feedback_obey_user_pause_explicitly`: $15-20 batch authorized 2026-06-03
- Per `feedback_batch_cloud_experiments`: Experiments B + C share cheap cloud bootstrap if scheduled together; Experiment A is CPU-only
- Per `feedback_brain_inspired`: brain analogs (dopamine RPE / acetylcholine novelty / Friston precision-weighting + LC + BG) are durable framing
- Per `feedback_testbed_progress_logging_and_restart`: per-cell partial JSON output enforced
- PROT-018: anchor names use plain-tier-prefix + descriptor + _v1 family

---

**END.**

**Orchestrator:** ingest into `experiment_queue_pending.md`; dispatch Experiment A to local CPU immediately (cheapest); queue Experiments B + C for cheap cloud bootstrap (shared if possible).

**Testbed:** engineering scaffolding per exp_dev handoffs already on disk (paths in §1); Experiments B + C share Lambda T4 / RTX 4090 if scheduled together.

**User:** batch dispatched. Expected ~1-2 days wall to first verdicts. Will surface findings as they land.
