# ROUTING -- Substrate-trained mini LM N-sweep with calibrated readout

**From:** Research session
**To:** Exp-Dev (primary)
**Inform:** Orchestrator
**Date:** 2026-06-04
**Type:** Empirical experiment / CPU N-scaling probe
**Status:** USER AUTHORIZED 2026-06-04 ($0 CPU; ~3-5h total wall; 6 N values).

---

## Capability question

At what substrate dimension N does the substrate-trained mini LM with calibrated readout temperature (temp=0.2) cross the threshold from "no learning" (N=512 HF, bpc gap = 0.019 nats) to "substantive learning" (Exp-Dev preview at higher N, bpc gap ~ 1.76 nats)?

This sweep characterizes the N-scale-dependence of substrate-as-training-mechanism emergence.

## Pre-reg HP/MID/HF bands

**HARD-PASS (clear N-threshold detected):**
- BPC < uniform - 1.0 nat at N >= N_threshold (substantial learning at sufficient substrate dimension)
- BPC > uniform - 0.3 nat at N < N_threshold (no learning at insufficient dimension)
- Monotone improvement in BPC as N increases (no inversions)
- 3/3 seeds consistent at each N tested
- N_threshold lies within the tested range {512, 1024, 2048, 4096, 8192, 16384}

**MIDDLE (partial confirmation):**
- BPC improvement visible at large N but doesn't reach uniform - 1.0 nat
- OR threshold visible but at edge of tested range (e.g., barely emerges at N=16384)
- OR 2/3 seeds consistent

**HARD-FAIL (refutes de-confound entirely):**
- No learning at any tested N up to 16384 (BPC gap < 0.3 nat at all N)
- Refutes Exp-Dev's preview observation
- Substrate-as-training-mechanism HF stays standing; joint D+H redesign or DeltaNet fallback becomes primary path

## Resource

Local CPU. Same substrate-trained mini LM scaffold as substrate_trained_mini_lm_rung1_readout_fix_v2; one parameter sweep (N).

## Cost ceiling

$0. Per-N wall scales with N (Hopfield write + cf-RPE compute):
- N=512: ~10 min
- N=1024: ~15 min
- N=2048: ~25 min
- N=4096: ~40 min
- N=8192: ~70 min
- N=16384: ~120 min
- Total ~3-5h sequential; faster if parallel slots available

## P_deflated

- Learning emerges at N >= 4096 with calibrated readout: **0.55** (Exp-Dev preview at presumed N=4096 is the strong empirical anchor; aligned with Grouped 2x drill's quantization-MI-per-N prediction)
- Learning emerges only at N >= 8192: 0.30
- Learning emerges at N <= 2048: 0.18 (would be surprising; lit predicts higher N needed)
- No learning at any N up to 16384: 0.15 (would refute de-confound and substantiate the joint D+H redesign as the right rescue)

Lit-scan calibration penalty applied (0.15-0.25); cap novel-synthesis at 0.50.

---

## What this is (plain language)

Exp-Dev's de-confound said: softmax-temp=1.0 was masking substrate learning at the readout. Re-eval at N=512 with temp=0.2 showed still no learning (bpc gap = 0.019). Exp-Dev's earlier preview at higher N showed substantive learning (bpc gap = 1.76).

**The de-confound is N-scale-dependent.** Readout-fix is necessary but not sufficient. Substrate signal strength scales with N (per Grouped 2x drill: 97% MI loss per bipolar coord; effective MI scales linearly with N; SNR ~ sqrt(N)).

This sweep formalizes the N-threshold:
- At N=512: 15 nats preserved MI (per Grouped drill estimate); insufficient for char-LM
- At N=4096: 123 nats preserved MI; likely sufficient
- At N=16384: 492 nats preserved MI; comfortably sufficient

The transition between insufficient and sufficient is the N_threshold. Identifying it locks the substrate-as-training-mechanism story to a specific scale claim.

---

## Cell list

Anchor name template: `substrate_trained_mini_lm_readout_fix_N{N}_v1`

N sweep:
- N=512: re-confirm prior HF baseline (cross-validate with prior re-eval)
- N=1024: closest to N=512; tests if doubling helps
- N=2048: intermediate
- N=4096: matches Exp-Dev's preview substrate dimension (most-likely emergence point)
- N=8192: higher confidence margin
- N=16384: substrate-physics-class N; ensures emergence if it exists

3 seeds per N. Same LM scaffold (~10k char-LM params), same corpus, calibrated readout temp=0.2, fixed cf-RPE no-cache discipline.

## Pre-reg measurements per cell

- BPC mean across 3 seeds
- BPC std across seeds
- Per-seed convergence trajectory (BPC vs training step)
- Substrate capacity tracking (alpha = M/N at each training step)
- Per-cell pass/fail at HP threshold (BPC < uniform - 1.0 nat)

---

## What this changes for joint D+H

Joint D+H routing (`routing_joint_DH_brain_correct_rung1_redesign_2026-06-04.md`) on HOLD pending N-sweep verdict.

If N-sweep HP (substrate learning emerges at N >= some threshold): joint D+H scope changes from "rescue broken substrate" to "test incremental improvements via brain-correct architecture vs. working baseline." Different pre-reg bands and motivations.

If N-sweep MIDDLE: joint D+H stays as primary rescue at substrate dimension where partial learning emerges.

If N-sweep HF (no learning at any N): joint D+H is the primary rescue; DeltaNet fallback also becomes more relevant.

---

## Follow-up drill in flight

3x deep drill dispatched parallel to this routing: `research_drill_substrate_training_n_threshold_3x_2026-06-04.md` (in-flight; ~30-45 min). Drill characterizes the algebraic mechanism setting N_threshold:
- Information-theoretic minimum N for char-LM conditional probability representation
- SNR vs N for three-factor Hebbian convergence (BCM theory)
- Bipolar quantization gap vs N (preserved MI scaling)
- Modern Hopfield exponential capacity threshold vs N
- High-dimensional concentration regime threshold

If drill output recommends a DIFFERENT N range (e.g., narrower around predicted threshold, or wider to include N=32768), ship change-request before dispatch. Otherwise standard N range above applies.

---

## Discipline declarations

- Per [[feedback-routings-direct-to-exp-dev]]: Exp-Dev primary; Orchestrator informed
- Per [[feedback-no-padding-experiments]]: 6 N values sweep is genuinely informative; not padding
- Per [[feedback-small-scale-first-methodology]]: stays at rung-1 LM scale (~10k params); only varies substrate dimension
- Per [[feedback-no-smoke-preframing-in-task-prompts]]: HP/MID/HF bands explicit; HF threshold = refutes de-confound
- Per [[feedback-negative-results-2x-research]]: 3x deep drill on the negative finding running in parallel
- Per [[feedback-rescue-sketch-first-sequencing]]: cheapest rescue (single-parameter N sweep) before structural rescue (joint D+H redesign)
- ASCII-only output enforced

PROT-018: anchor names use _N{N}_v1 suffix in each cell
PROT-021: source=local CPU, run_mode=full, n_seeds=3

---

**END.**

**Exp-Dev:** dispatch 6 N-values sequentially or in parallel. Same script as substrate_trained_mini_lm_rung1_readout_fix_v2 with N parameter varied. Estimated total wall ~3-5h. Cost $0.

**Orchestrator:** informed. Cap_map sub-property founding pending verdict outcome:
- HP: N-threshold characterization for substrate-as-training-mechanism row
- MIDDLE: partial N-scale-dependence noted
- HF: refutes de-confound; joint D+H redesign promoted to primary

**Research session:** holds for sweep verdict + parallel 3x drill output; synthesizes both within same cap_map cycle.
