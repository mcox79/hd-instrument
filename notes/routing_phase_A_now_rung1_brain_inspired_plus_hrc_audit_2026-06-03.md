# ROUTING — Phase A NOW (rung 1 brain-inspired + HRC v341 audit)

**From:** Research session
**To:** Testbed
**Date:** 2026-06-03
**Status:** USER AUTHORIZED 2026-06-03 ($0 CPU; ~1 hour total wall; dispatch IMMEDIATELY).
**Priority:** HIGH — user wants fast feedback before scheduling overnight batch.

---

## What this batch is (plain language)

Three small experiments that close the largest design-validation questions FAST. User stopped both cloud experiments (hd-phase05 + brain-batch) and adopted the rung-1-2-first methodology. Phase A validates whether the brain-inspired multi-channel orchestration designs even work at tiny scale BEFORE scheduling overnight batch work.

All three run on local CPU runner. Total batch wall ~1 hour. Cost $0.

---

## Experiment A1 — Spectral training monitor at tiny scale

**Anchor name:** `substrate_spectral_training_monitor_rung1_tinychar_v1_n4096`

**Plain-language description:** Tests whether substrate spectral fingerprint (κ_2 / κ_3 / κ_4_excess of residual-derived weight matrix) predicts training-phase changes BEFORE validation loss does. At tiny scale, this is a 1-2 layer char-LM training for 500-1000 steps. If substrate signal leads validation-loss indicator by ≥20 steps, the predictive-monitor claim is validated at tiny scale and worth scaling to rung 2.

**Resource:** local CPU
**Wall:** ~15 minutes
**Cost:** $0

### Test design

- Model: 1-2 layer LSTM or tiny transformer; char-level Shakespeare or simple synthetic corpus; ~5k-10k params
- Substrate observer attached at single hidden state
- Compute κ_2 / κ_3 / κ_4_excess every 5 steps (faster cadence than original cloud spec because tiny-LM trains fast)
- Train for 500-1000 steps with held-out validation set
- Annotate ground-truth training-phase changes from validation-loss curve (convergence onset / overfitting onset / divergence)
- Measure predictive lead time: does substrate fingerprint trajectory cross threshold N steps before validation-loss-curve crosses corresponding threshold?
- 3 seeds

### Pre-registered bands

- **HARD-PASS:** substrate signals each phase change ≥ 20 steps before validation-loss indicator AND across 3 seeds
- **MIDDLE:** lead time 10-20 steps OR 2/3 seeds
- **HARD-FAIL:** substrate signal lags or matches validation loss (no predictive lead)

### Outcome interpretation

- HP at rung 1 → escalate to rung 2 (4-layer char-LM, ~60 min CPU); validated design ready for overnight batch
- MIDDLE at rung 1 → which κ_k carries the predictive signal? Run variant sweep at rung 1 (cheap to iterate)
- HF at rung 1 → fundamental design issue at tiny scale; do NOT escalate to rung 2; surface findings to research

---

## Experiment A2 — 8-channel orchestration at tiny scale

**Anchor name:** `substrate_8channel_orchestration_rung1_tinychar_v1_n4096`

**Plain-language description:** Tests whether running 8 substrate channels jointly during LLM training beats running 4 channels beats running 1 channel (CE-only baseline). At tiny scale, 1-2 layer char-LM with 3 channel-count conditions. This is the load-bearing test of the multi-channel orchestration product claim. If 8-channel doesn't beat 4-channel at tiny scale, scaling to GPT-2-small / Pythia-160M / Llama is wasted compute.

**Resource:** local CPU
**Wall:** ~30 minutes
**Cost:** $0

### Test design

- Model: 1-2 layer LSTM or tiny transformer; ~5k-10k params (same scaffold as A1)
- 3 channel-count conditions: 1-channel (CE baseline) / 4-channel (CE + 3 substrate signals) / 8-channel (CE + 7 substrate signals)
- Substrate signals architectural specification: 4 tonic (κ_2 / κ_3 / κ_4 / capacity ratio) + 4 phasic (rank-1 cf / hippocampal place tag / anti-Hebbian / multi-bank addressing)
- σ_k learned per channel per Cipolla precision-weighting
- g_θ MLP gating + PCGrad conflict resolution + layer-zone gain
- 1000 training steps per condition
- 3 seeds per condition
- Metric: validation cross-entropy (held-out)
- Track per-channel gradient norm + per-channel σ_k weight at convergence (failure-mode isolation)

### Pre-registered bands

- **HARD-PASS:** 8-channel beats 1-channel by > 5% on validation CE AND beats 4-channel by > 2% AND no majority-antagonistic channel pairs detected AND gradient norm > 1% of input AND all 3 seeds replicate
- **MIDDLE:** 8-channel beats 1-channel by > 2% but < 5% OR doesn't beat 4-channel OR replicates 2/3 seeds
- **HARD-FAIL:** 8-channel < 4-channel OR PCGrad projection collapses gradient norm < 1% OR 8-channel fails to converge OR 0/3 seeds replicate

### Outcome interpretation

- HP at rung 1 → multi-channel orchestration claim validated at tiny scale; escalate to rung 2 (4-layer char-LM); overnight batch dispatches
- MIDDLE at rung 1 → which channels contribute / conflict? Run channel-ablation sweep at rung 1 (single channels alone; pairwise interactions)
- HF at rung 1 → fundamental orchestration design issue; do NOT scale to rung 2-5; surface to research for design rework before any further work

### Critical instrumentation

This experiment is where failure-mode isolation matters most. Record per-channel gradient norms, σ_k weights, PCGrad conflict frequency. At cloud scale these are invisible; at tiny scale we can stare at each channel's behavior individually. Surface ALL per-channel metrics in verdict_msg, not just final CE.

---

## Experiment A3 — HRC v341 audit (R2 rescue, drill-1 informed)

**Anchor name:** N/A — mechanical file audit, not a substrate experiment

**Plain-language description:** Drill 1 today found that PP-49 HRC HARD-FAIL (cos=1.000 saturation) is leaf-start protocol artifact — the cos=1 is mathematically correct for leaf-start measurement of rank-1 substitution in contractive recurrent retrieval. Drill 1 hypothesized that v341 (which HP'd at N=4096) may have used a different protocol that incidentally tested basin-crossing instead of basin-invariance. This audit identifies the protocol delta.

**Resource:** local mechanical (no compute)
**Wall:** ~10 minutes
**Cost:** $0

### Test design

1. Locate v341 script: `pp49_hrc_counterfactual_depth_8_v1_n4096`
2. Locate v370 script: `pp49_hrc_cross_n_d4_d6_d8_v1_n16384`
3. Diff the two scripts focusing on:
   - Counterfactual cos measurement formula (which T_d(x) vs which T_d(x') is being compared?)
   - Substitution pattern construction (is it leaf-start substitution of W only, or paired-pattern dual changing both W and x?)
   - Cell architecture (autoassociative vs heteroassociative chain)
4. Output: identified protocol delta + brief synthesis (1-2 paragraphs) on whether the v341 HP and v370 HF are both correct measurements of different quantities (per drill 1 hypothesis) or whether one is genuinely broken

### Pre-registered outcomes

- **Protocol delta CONFIRMED:** v341 measured basin-crossing (e.g., root-start protocol or paired-pattern dual); v370 measured basin-invariance (leaf-start). Drill 1 hypothesis confirmed. PP-49 HRC HF can be reclassified at orchestrator level as confirming evidence for deletion-certificate sub-capability.
- **Protocol delta REFUTED:** identical protocol in both scripts; one of them has a genuine bug. Flag for review.
- **Inconclusive:** scripts diverge in many ways; cannot isolate the responsible delta. Recommend follow-up.

### Outcome interpretation

- CONFIRMED → ship updated capability-implication note to orchestrator (the one I shipped today, but strengthened with empirical audit). Strengthens deletion-certificate killer-feature product claim.
- REFUTED → reopen rescue path; the v341 HP is a real result that needs reproducing.
- Inconclusive → drill 1 algebraic story stands but empirical audit doesn't close the question; paired-pattern dual probe (overnight) becomes the empirical test.

---

## Total batch summary

- 3 experiments
- ~55 min wall (15 min A1 + 30 min A2 + 10 min A3)
- $0 cost
- All on local CPU runner

Sequence: A3 (10 min) → A1 (15 min) → A2 (30 min). A3 first because it requires no engineering and surfaces immediately. A1 and A2 can run in parallel if CPU bandwidth allows; otherwise sequential.

---

## Status-check request

Before dispatching, verify:
- [ ] Is local CPU runner alive and idle? (per `project_cpu_resource_underutilized` — historically unstable; check before routing)
- [ ] Are the rung-1 scaffolds (tiny char-LM + substrate observer wiring) implementable in <30 min engineering, or do they need fresh scaffolding?

If scaffolds need fresh engineering: estimate engineering time and surface. The tiny-LM scaffolds should be cheap to write (PyTorch nn.LSTM(small) + forward hook + substrate primitive calls); if engineering exceeds 1h, flag back to research.

---

## What happens AFTER Phase A lands

Research-session synthesis based on three verdicts. Three branches:

**ALL THREE PASS** → ship overnight Phase B batch (rung 2 escalations + already-shipped data attribution sweep + paired-pattern dual probe + substrate-trained mini LM + curriculum + ICL). Estimated overnight batch: 12-18 hours CPU, $0.

**MIXED RESULTS** → ship overnight Phase B with PASSing rungs escalated + variant sweeps on MIDDLE-classified rungs. Adjust scope.

**ALL HF** → recursion to research. Do NOT ship overnight batch on broken designs. Re-examine the brain-inspired multi-channel premise at tiny scale.

---

## Discipline declarations

- Per `feedback_change_request_protocol`: change applied via this fresh Phase A routing (recasts brain-inspired B+C at rung 1 + closes HRC R2 mechanically); supersedes original cloud-scale routing
- Per `feedback_plain_language_experiment_tracking`: experiments described by what they test at each rung
- Per `feedback_no_padding_experiments`: each experiment closes a specific design-validation question that gates overnight work
- Per `feedback_no_smoke_preframing_in_task_prompts`: HP/MID/HF bands tied to drill predictions
- Per `feedback_obey_user_pause_explicitly`: rung-1-2-first methodology user-authorized 2026-06-03
- Per `feedback_testbed_progress_logging_and_restart`: per-cell partial JSON output
- PROT-018: anchor names use rung-tier-prefix + descriptor + _v1 family

---

**END.**

**Testbed:** dispatch A3 immediately (mechanical file audit, no compute); dispatch A1 + A2 once tiny-LM scaffold is in place. Surface verdicts as each lands. Total wall ~55 min; cost $0.

**Research session:** holds for all three verdicts; synthesizes; ships Phase B overnight batch routing based on outcomes.
