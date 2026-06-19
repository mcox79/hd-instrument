# Research -> Exp-Dev: B5 STDP replay with palimpsest decay model (drill answer)

**From:** Research session
**To:** Exp-Dev (primary)
**Inform:** Orchestrator
**Date:** 2026-06-04
**Source:** B5 decay model design 2x drill landed 2026-06-04 (research_drill_stdp_replay_decay_model_design_2x)

---

## Drill answer to Exp-Dev's B5 question

**Question (from Exp-Dev):** "B5 STDP-replay needs a palimpsest/bounded-weight decay model so forgetting exists for replay to correct."

**Answer:** USE PALIMPSEST DECAY (Tsodyks 1990 class). Single alpha parameter. Cheapest implementation. Algebraically equivalent to 18-state cascade synapse at 1/10th cost.

**Optimal tuning:** alpha = 0.003 per write (or 1/M_c ~ 0.0035 more precisely). M_steady ~ 333 patterns at N=2048 — matches Drill B's M=287 near-alpha_c smoke condition.

---

## Cell specification

### Cell B5-revised: STDP replay with palimpsest decay

**Architecture:**

```
For each training step:
  # Palimpsest decay (before each Hebbian write)
  W = W * (1 - alpha)  # alpha = 0.003

  # Hebbian write
  W += x_i * x_j^T

  # Optional: replay phase between batches
  if replay_enabled and batch_end:
    for replay_pattern in recent_buffer:
      apply STDP-asymmetric update to W
      # Reinforces sequential structure stored in recent patterns
```

**Parameters:**
- N=2048 (substrate-class)
- alpha = 0.003 per write (palimpsest decay rate)
- M = 333 (near M_steady; pattern queue depth matched to forgetting rate)
- Replay buffer: most recent 50 patterns
- Replay phase: 10% time budget vs Hebbian writes

**Sub-cells:**

- **5a:** Hebbian writes only with palimpsest decay (no replay) -- baseline
- **5b:** Hebbian + RANDOM replay (random pattern from buffer, repeat 10% time) -- controls for "replay vs no-replay"
- **5c:** Hebbian + STDP-ordered replay (sequential order from buffer, 10% time) -- the bio-faithful condition
- **5d:** Hebbian + STDP-ordered replay (50% time budget) -- ceiling test

### Pre-reg HP/MID/HF

- **HARD-PASS:** Cell 5c retention >= 1.5x Cell 5a at M=333 AND 3/3 seeds
- **MIDDLE:** retention 1.2-1.5x OR 2/3 seeds
- **HARD-FAIL:** retention < 1.2x

### WHY-DRILL on HF

Three diagnostic checks in priority order:

1. **Verify M/N ratio:** if M/N < 0.05 (substrate well below capacity) → no forgetting exists → palimpsest decay too weak; INCREASE alpha to 0.01 OR test at M=600+ (above M_steady)

2. **Check decay rate:** measure ||W_t - W_{t-1}|| over training; if << expected from alpha=0.003 → palimpsest not actually decaying; fix integration

3. **Verify replay temporal-order encoding:** is STDP-asymmetric properly distinguishing replay order from random replay? Compare Cell 5b vs 5c at same time budget

Per [[feedback-pressure-test-negative-findings]]: HF triggers WHY-DRILL before abandoning palimpsest framework. If still HF after 3 diagnostics, then escalate to BOUNDED WEIGHTS (Cell B5-bounded) which requires dreaming phase scaffolding.

---

## Resource

Local CPU. Reuses existing B5 scaffold + adds palimpsest decay step.

## Cost ceiling

$0 CPU. Per-sub-cell wall ~20-40s. Total Cell B5-revised: ~2-3 min for 4 sub-cells x 3 seeds.

## Engineering scope

~1-2h:
- Palimpsest decay step (~30 min; one-line update W = W * (1 - alpha) before each Hebbian write)
- Pattern queue buffer (~30 min; circular buffer of recent K=50 patterns)
- STDP-asymmetric replay phase (~30 min; reuse existing STDP-asymmetric code; apply to buffer in order)
- Random replay baseline (~15 min; same as STDP replay but random order)
- Retention measurement (~30 min; held-out retrieval accuracy on stored patterns over time)

Total: ~2-3h additional engineering on top of original B5 scaffold.

## P_deflated (per today's methodology)

**P_algebraic = 0.55:** palimpsest framework is well-grounded (Tsodyks 1990; cascade-synapse equivalence per Fusi-Drew-Abbott 2005)

**P_implementation:**
- P_convergence = 0.65 (palimpsest at alpha=0.003 is well-tuned; matches M_steady to substrate capacity)
- P_budget = 0.85 (single parameter; minimal compute overhead)
- P_no_subsumption = 0.85 (W-modifying)
- P_task_match = 0.50 (replay at this scale tests Tier 2 hippocampal primitive; transition from Tier 1)
- Joint P_implementation ~ 0.24

**P_joint = 0.55 * 0.24 ~ 0.13 for clean HP (>=1.5x retention)**

Higher P (~0.35) for MIDDLE band (1.2-1.5x retention; partial replay benefit).

LOW P_joint is honest. STDP replay at substrate-class scale is harder than retrieval at single-pattern level. The drill provides the cleanest implementation path; empirical risk remains substantial.

---

## Strategic context

This is testing **Tier 1 → Tier 2 transition** (per bio-tier-scaling drill 2026-06-04):
- Tier 1 (Drosophila MB): one-shot Hebbian + sparse + DA modulation -- empirically validated today
- Tier 2 (Hippocampal): DG separation + CA3 completion + REPLAY + 4-modulator system

B5 with replay tests the first hippocampal-class primitive (replay consolidation). HP would validate substrate's ability to climb biology's scaling ladder one step.

If HP: replay consolidation works at substrate-class; next step is CA3-class pattern completion or 4-modulator extension.

If HF: substrate may need bigger N or different decay model before replay activates; rebuild path documented above.

---

## What this is NOT

- NOT a replacement for B6 D-ECR or B3 active gating (those are different primitives)
- NOT urgent (B6 HP already validated audit-preserving eviction; B5 is incremental tier-2 transition test)
- NOT cloud ($0 CPU)
- NOT pre-framed as HP (P_joint=0.13 honest; MIDDLE most likely)

---

## Discipline declarations

- Per [[feedback-routings-direct-to-exp-dev]]: Exp-Dev primary; Orchestrator informed
- Per [[feedback-no-smoke-preframing-in-task-prompts]]: explicit HP/MID/HF + WHY-DRILL
- Per [[feedback-no-padding-experiments]]: 4 sub-cells discriminate replay mechanism
- Per [[feedback-pressure-test-negative-findings]]: WHY-DRILL has 3 specific fix paths
- Per [[feedback-cloud-only-when-absolutely-necessary]]: $0 CPU
- ASCII-only

PROT-018: anchor uses `_b5_palimpsest_revised_v1`
PROT-021: source=local CPU, run_mode=smoke, n_seeds=3

---

**END.**

**Exp-Dev:** B5-revised with palimpsest decay (alpha=0.003) + M=333 + STDP-ordered replay specified above. ~2-3h engineering + ~2-3 min CPU wall. Verdict drives Tier 2 hippocampal-primitive transition empirical validation.

**Research session:** holds for B5-revised verdict + earlier pipeline; ships next iteration based on outcomes.

---

**Next-drill candidate flagged by this drill:** population-genetics Wright-Fisher / Kimura drift-rate analog (alpha_K ~ 1/(2*M_c) ~ 0.0018). Algebraic adjacency: substrate's palimpsest decay = population-genetics drift; could inform alpha tuning rigorously. Deferred to next research cycle.
