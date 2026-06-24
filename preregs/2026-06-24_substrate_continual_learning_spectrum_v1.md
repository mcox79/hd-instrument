# Pre-registration: substrate_continual_learning_spectrum_v1

**Date:** 2026-06-24
**Anchor:** substrate_continual_learning_spectrum_v1
**Queue:** remote_cpu_queue (pure numpy at N=4096, fits CPU; routed via hdi_orchestrator)
**N:** 4096, **Seeds:** [7, 17, 23], **J_phases:** 5, **M_per_phase:** 400

## Scientific question
Do substrate's continual-learning primitives (cf-RPE delta-rule online updates, CLS-replay dual-W consolidation, K-bank routing) COMPOSE into a working CL system at production scale, or do they break when stacked? Each primitive has been validated in isolation (cf-RPE chain-grade at +0.14 BPC; CLS-replay smoke chain-grade; K=2 multi-bank chain-grade at smoke; modular macrocolumn K=32 chain-grade). The composed CL system has NEVER been tested. Strategic stakes: substrate's competitive moat vs transformers (continual learning at low compute cost without catastrophic forgetting) is real only if these primitives compose.

## Pre-registered bands

**Sanity rail (required):**
- ARM_BASELINE_STATIC Phase 1 initial recall in [0.85, 1.00] -- substrate actually stored Phase 1; else HARD_FAIL with sanity-violation flag.

**HARD-PASS (CL moat real; chain-grade-eligible substrate CL):**
- ARM_FULL_CL_SYSTEM forgetting_p1 <= 0.10
- AND ARM_FULL_CL_SYSTEM transfer_recall on final phase >= 0.60
- AND ARM_FULL_CL_SYSTEM beats ARM_DISCRETE_ADD on forgetting_p1 by delta >= 0.40 (real rescue, not flat-regime)

**CHAIN_GRADE_BONUS (transformers can't touch this):**
- ARM_FULL_CL_SYSTEM forgetting_p1 <= 0.05
- AND ARM_FULL_CL_SYSTEM transfer_recall >= 0.80

**MIDDLE:** characterized but no chain-grade point (e.g., HP_FORGETTING + HP_TRANSFER met but no delta-vs-DISCRETE rescue; would indicate substrate doesn't forget at tested alpha, requiring higher M).

**HARD-FAIL (CL moat is theoretical):**
- ARM_FULL_CL_SYSTEM forgetting_p1 > 0.50
- OR ARM_FULL_CL_SYSTEM transfer_recall < 0.30
- OR ARM_FULL_CL_SYSTEM no better than ARM_DISCRETE_ADD (delta_vs_DISCRETE < 0)

## Calibration rationale
The cell author smoke (2026-06-24) iterated through 3 composition designs:
- v0 (alpha_cfrpe=0.05, alpha_slow=0.1, recency=2; cf-RPE BEFORE replay): cf-RPE undershoots (recall 0.45-0.65); replay washes new-phase writes (transfer=0).
- v1 (alpha_cfrpe=0.3, alpha_slow=0.05, recency=4; replay BEFORE cf-RPE): aggressive cf-RPE WIPES Hebbian writes (CLS phase 1 -> 0 after phase 2 cf-RPE).
- v2 (alpha_cfrpe=0.05/5-passes, alpha_slow=0.1, recency=4; Hebbian-fast -> CLS-replay -> cf-RPE nudge): smoke shows transfer=0.825, forgetting=0.0 on FULL_CL_SYSTEM; MIDDLE_BAND because DISCRETE doesn't forget at smoke alpha_total=0.146.

The 5 arms span the CL spectrum from frozen-static (no learning) to full-stack (cf-RPE + CLS-replay + K-bank routing). The composition order is brain-faithful: Hebbian-fast first (hippocampal episodic write), then CLS-replay (slow consolidation with recency bias to W_cortex), then cf-RPE error-correction nudge (online learning signal).

HP_FORGETTING_MAX=0.10 is calibrated against cls_replay smoke v3.1 chain-grade target (P1 retention >= 0.80, i.e., forgetting <= 0.20). The 5-domain curriculum here is harder than 3-domain, so 0.10 is a tighter bar. HP_TRANSFER_MIN=0.60 calibrated against smoke FULL_CL transfer=0.825 -- bar set lower to leave headroom. HP_VS_DISCRETE_DELTA=0.40 ensures we see real rescue, not flat-regime artifact (the bar that the cls_replay smoke also enforces).

Full-run alpha_total = (5 * 400) / 4096 = 0.488 -- well past Hopfield cliff (alpha_c ~ 0.138). DISCRETE_ADD is therefore expected to catastrophic-forget; the rescue should be visible.

## N-suffix section
Anchor has NO _n<N> suffix (PROT-018 family-level naming). Production N_DIM = 4096; script asserts at config load. No mismatch possible.

## Timeout estimate
Smoke wall measured: 166.86s (J=3, M=200, N=4096, 2 seeds).
Full: J=5 (1.67x), M=400 (2x; scales as M^2 in Hebbian via Xi^T Xi), seeds=3 (1.5x).
   formula: ceil(1.5 * 166.86 * (5/3) * (400/200)**2 * (3/2)) ~= ceil(1.5 * 166.86 * 1.67 * 4 * 1.5) = 2506s
PROT-019 floor: N=4096 -> timeout >= 3600s.
Use timeout_s = 5400s (1.5x safety margin over both formula and PROT-019 floor).

## What this does NOT show
- NOT a head-to-head with transformer fine-tuning baseline (would need separate cell with HF Trainer + GPU FLOPs measurement; out-of-scope).
- NOT cross-CORPUS continual learning (uses synthetic per-domain bipolar permutations; real text8/wiki/code domains require separate cell).
- NOT a measurement of BPC; uses recall-accuracy (substrate-native CL metric). The "1% of transformer fine-tuning compute" claim is reported in numpy-flops-per-atom-written, NOT apples-to-apples PyTorch backprop FLOPs.
- K_BANK arm uses K=2 random-projection soft-gate; gate is NOT end-to-end trained (separate cell would test that).
- cf-RPE arm is ablation-isolated (cf-RPE alone, no Hebbian co-write); documents that cf-RPE-only is weak without companion mechanism.
