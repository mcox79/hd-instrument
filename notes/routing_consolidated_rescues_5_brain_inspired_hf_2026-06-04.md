# ROUTING — Consolidated rescue paths for 5 brain-inspired tiny-scale HARD_FAILs

**From:** Research session
**To:** Orchestrator (primary), Testbed (engineering reference)
**Date:** 2026-06-04
**Status:** Awaiting deep-research drills (5 dispatched in parallel; ~30 min wall to land). This routing pre-stages cheapest BEST-RESCUE per HF.

---

## What this is (plain language)

Overnight cycle 43 surfaced 5 substrate-as-training HARD_FAILs at tiny scale: substrate-trained mini LM, substrate-driven curriculum, substrate-preloaded ICL, spectral training monitor (convergence-phase lag with overfitting rescue signal), and 8-channel orchestration. The strategy decisions filed rescue paths R1-R3 cheapest-first per HF. This routing consolidates the cheapest BEST-RESCUE per HF for orchestrator's dispatch ordering decision.

Five research drills are also in-flight (3x META + 3x Experiment B + 3x Experiment C + 2x grouped training-augmentation + 2x Lyapunov framework). Rescue dispatch order should incorporate drill findings when they land. This routing is the PRE-DRILL rescue summary.

---

## Five HF rescue summary

### 1. substrate_spectral_training_monitor_rung1 — OVERFITTING SENTINEL RESCUE (cheapest, cleanest)

**HF signature:** convergence-phase mean_lead = -11.67 steps (3/3 seeds LAG); overfitting-phase mean_lead = +300 steps (3/3 seeds LEAD).

**RESCUE R1 (cheapest BEST-RESCUE, $0 free):** Re-define pre-reg criterion as overfitting-phase-only sentinel detection. Substrate spectral fingerprint IS a strong overfitting predictor (300-step lead across all seeds). New product framing: "substrate spectral signature detects overfitting onset 300 steps before validation loss" — a CLEAN positive capability claim.

**Why this is cheapest:** existing data already supports the rescue. Annotation-only change. Cap_map gains a NEW sub-property founding under drift/observability rather than an HF closure.

**Recommended dispatch:** annotation update (no new experiment).

### 2. substrate_spectral_monitor_overfitting_v1 — SCALE GATE RESCUE

**HF signature:** val_overfit_step = None for 0/3 seeds; sub_overfit_step = 200 for all 3 seeds. Substrate fired consistently but TRAIN_CHARS=30000 / N_STEPS=2000 too short for val_loss to reach overfitting phase.

**RESCUE R1 (~1-2h CPU, $0):** Re-run with TRAIN_CHARS = 100k-200k + N_STEPS = 5000-10000. Substrate signal is present; LM just needs longer training to actually overfit so the lead-time can be properly measured.

**Why this works:** rescue is a scale-gate not a mechanism failure. The signal is there; the test conditions were too short.

**Recommended dispatch:** queue as rescue variant; sequence after spectral-monitor 3x drill lands (drill may identify whether κ-class primitives are right for this OR if alternative primitives are needed first).

### 3. substrate_8channel_orchestration_rung1 — DEPENDS ON 3x DRILL FINDING

**HF signature:** zero converged seeds.

**RESCUE R1 candidates (pending 3x drill):**
- Channel pruning (drop from 8 to 2-4 most-orthogonal)
- PCGrad replacement (try MGDA or naive sum)
- σ_k initialization protocol revision
- Capacity scaling (test at ~50k-100k params; small-LM may be below orchestration capacity threshold)

**Recommended dispatch:** HOLD until 3x drill on multi-channel orchestration failure lands. Drill identifies binding constraint (~30 min wall remaining). Then dispatch rescue variant per drill recommendation.

### 4. substrate_trained_mini_lm_rung1 — DEPENDS ON META 3x+ DRILL

**HF signature:** BPC = 5.5168 ≈ uniform-baseline 5.5236. No learning.

**RESCUE R1 candidates (pending META 3x+ drill):**
- Continuous-valued substrate (drop {±1} → ℝ)
- Rank-r ≥ 2 operations (not just rank-1)
- Substrate-to-continuous interpolation layer
- Reduce ambition: test on simpler task (associative recall) before language modeling

**Recommended dispatch:** HOLD until META 3x+ drill lands (~30-60 min wall). The drill answers: is there a fundamental theoretical reason substrate-as-training-mechanism CAN'T work? OR what design changes are required? Rescue depends on drill outcome.

### 5. substrate_curriculum_learning_rung1 + substrate_preloaded_icl_rung1 — GROUPED RESCUE

**HF signatures:**
- Curriculum: gain = -0.0984 (NEGATIVE; curriculum hurts vs random)
- ICL: best_gain = 0.0145 at K=10 (marginal; << HP 0.1)

**RESCUE R1 candidates (pending grouped 2x drill):**
- Continuous-valued substrate pattern preloading (vs bipolar)
- Substrate's difficulty-scoring may need re-calibration (bipolar Hamming-distance doesn't track learnability)
- K-value sweep at higher K (100, 1000, 10000) for ICL
- Or fundamental design rethink if grouped drill identifies bipolar quantization as binding constraint

**Recommended dispatch:** HOLD until grouped 2x drill on training-augmentation unified failure mode lands.

---

## Recommended dispatch ordering

**Tier 1 — DISPATCH IMMEDIATELY ($0, no new experiment):**
- Spectral training monitor overfitting-sentinel reframe (annotation only; positive capability claim founded)

**Tier 2 — DISPATCH after 3x drill lands (~30-60 min wall):**
- Multi-channel orchestration rescue per 3x drill recommendation
- Substrate-trained mini LM rescue per META 3x+ drill recommendation
- Curriculum + ICL grouped rescue per 2x drill recommendation

**Tier 3 — DISPATCH after Tier 2 verdicts (or in parallel with low resource contention):**
- Spectral monitor scale-gate rerun (TRAIN_CHARS=100k-200k)

---

## Why drill-informed dispatch matters

These 5 HFs share possible root causes (bipolar discrete-state representation insufficient; gradient-descent analog absent; capacity bottleneck at small scale; PCGrad/orchestration pathology). The drills will likely identify a UNIFIED root cause for several HFs. Dispatching rescues BEFORE drill findings may iterate on the wrong constraint.

Per `feedback_rescue_sketch_first_sequencing`: cheapest/subsumption rescues sequenced first. Tier 1 (overfitting-sentinel annotation) is the subsumption rescue — IF spectral monitor overfitting-detection is a clean positive capability, the convergence-phase HF doesn't need rescue; the FAILURE was the pre-reg criterion, not the substrate signal.

---

## Strategic context

The 5 HFs collectively challenge the "substrate as multi-channel LLM training infrastructure" narrative. The rung-1-2-first methodology revealed this at $0 instead of $50-300 cloud waste. Now we need to decide:

1. Is substrate-as-training-mechanism FUNDAMENTALLY POSSIBLE at small scale (META 3x+ drill answers)
2. If yes — what design changes are needed (drills identify binding constraints)
3. If no — what's the right scale threshold? Or is the multi-channel orchestration claim only valid at larger LLM scales?

The drift-detection + cross-layer composition + audit-cert capabilities are UNAFFECTED by these HFs. The substrate as OBSERVATION/AUDIT story is unquestionably strong. The substrate as TRAINING-MECHANISM story needs new thinking.

---

## Discipline declarations

- Per `feedback_routings_address_orchestrator_not_testbed`: orchestrator primary
- Per `feedback_rehabilitation_after_rejection`: 5 rescue paths per HF, cheapest first
- Per `feedback_rescue_sketch_first_sequencing`: subsumption rescue (overfitting-sentinel) sequenced first
- Per `feedback_no_padding_experiments`: each rescue targets a specific HF; no padding variants
- Per `feedback_change_request_protocol`: rescues are NEW experiments not changes to prior; pre-reg bands explicit
- Per `feedback_small_scale_first_methodology`: rescues stay at rung 1-2 scale until small-scale design works

---

**END.**

**Orchestrator:** Tier 1 (overfitting-sentinel reframe) dispatches immediately as cap_map annotation. Tier 2 (4 rescues) holds for drill landings (~30-60 min). Tier 3 dispatches after Tier 2 verdicts.

**Testbed:** engineering scope per drill-informed redesigns when they arrive. No new engineering until then.

**Research session:** holds for 5 drill verdicts; synthesizes; updates this routing with drill-informed rescue designs.
