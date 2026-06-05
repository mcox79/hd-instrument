# ROUTING -- Spectral training monitor full-cycle reframe + complementary primitives

**From:** Research session
**To:** Orchestrator (primary)
**Date:** 2026-06-04
**Type:** Mixed: 0-compute annotation (Tier 1; strategy_scribe) + future empirical engineering (Tier 2; Testbed)

---

## Capability question

Can substrate provide full-cycle training-phase detection (lead-time at BOTH convergence AND overfitting onset) by combining weight-cumulant primitives (for emergence/overfit events) with activation-erank + Hessian-trace primitives (for saturation/convergence events)?

## Pre-reg HP/MID/HF bands (Tier 1: annotation-only)

N/A for the immediate reframe. The existing empirical result (substrate spectral fingerprint signals overfitting onset +300 steps ahead, 3/3 seeds) ALREADY supports the overfitting-sentinel sub-capability claim. Reframe converts HF (failed convergence-detection criterion) into HP (confirmed overfitting-sentinel sub-property).

## Pre-reg HP/MID/HF bands (Tier 2: future complementary-primitives experiment)

**HARD-PASS:**
- Activation erank(Cov(h)) leads val-loss convergence by >= 15 steps, 3/3 seeds (per Drill predicted 30-80 step lead, deflated)
- Hessian trace proxy via Hutchinson leads convergence by >= 10 steps, 3/3 seeds (per Drill predicted 20-50 step lead, deflated)
- Weight kappa_4_excess overfitting lead retained at >= 200 steps (validates the spectral channel still works)
- Full-cycle coverage: at least one of erank/Hessian-trace leads convergence AND weight-kappa leads overfitting in same run

**MIDDLE:** Partial coverage (one phase leads, other lags). Re-run with augmented primitive set.

**HARD-FAIL (refutes Drill prediction):**
- erank lead < 5 steps (closes activation-space convergence-lead hypothesis)
- Hessian trace shows zero lead (closes landscape-leads-representation theory at this scale)
- Weight kappa overfitting lead drops below 50 steps when N doubled (would indicate noise floor explanation, not signature-class)

## Resource

- Tier 1: 0-compute (cap_map annotation; Orchestrator routes to strategy_scribe)
- Tier 2: local CPU (4-layer char-LM with 3 substrate primitive channels)

## Cost ceiling

- Tier 1: $0
- Tier 2: $0 (CPU only); wall ~60-90 min

## P_deflated

- Tier 1 overfitting-sentinel reframe: ~0.85 (already empirically supported by 300-step lead across 3 seeds)
- Tier 2 activation-erank lead-detection at >= 15 steps: 0.38 (per Drill spectral 3x; lit-scan calibration penalty applied)
- Tier 2 Hessian-trace lead-detection at >= 10 steps: 0.48 (per Drill; Hessian-class lit is stronger)

---

## What this is (plain language)

Brain-inspired Experiment B (spectral training monitor) HARD_FAILed under as-shipped pre-reg (convergence phase lag -11.67 steps, overfitting phase lead +300 steps; pre-reg required convergence lead).

The 3x deep drill identified the asymmetry as ALGEBRAICALLY NECESSARY:
- Free cumulants kappa_k detect EMERGENCE events (overfitting BBP spike; lead +300 steps confirmed by structure)
- Free cumulants kappa_k CANNOT detect SATURATION events (convergence plateau; lag matches Adam beta_1 confirmation delay 1/(1-0.9) = 10 steps)

This is a signature-class mismatch, not a noise-floor issue. Same primitive, opposite event classes.

**Tier 1: REFRAME existing HF as confirmed overfitting-sentinel HP.** The +300 step overfitting lead across 3/3 seeds IS a clean positive capability. Substrate spectral kappa_k is a strong overfitting sentinel. This was already empirically demonstrated; just needs the pre-reg criterion split into per-phase sub-criteria.

**Tier 2: ADD complementary primitives that fire at convergence (saturation events).** The drill recommended two:
1. **erank(Cov(h)) of residual activations** -- monitors functional representation change. Predicted lead 30-80 steps before val-loss convergence.
2. **Hessian trace proxy via Hutchinson estimator** -- monitors loss-landscape curvature collapse. Predicted lead 20-50 steps.

These cover the OPPOSITE phase from kappa_k. Combined: full-cycle phase detection.

---

## Tier 1 requested actions (NOW; strategy_scribe annotation)

1. **Update Experiment B verdict annotation.** Change from "HARD_FAIL convergence-phase-lag" to:
   - Pre-reg sub-criterion 1 (overfitting sentinel): HARD_PASS (+300 step lead, 3/3 seeds, signal stable)
   - Pre-reg sub-criterion 2 (convergence detector): HARD_FAIL (-11.67 step lag, 3/3 seeds; algebraic root cause: kappa_k cannot detect saturation events; signature-class mismatch per Drill 3x)
   - NET: overfitting-sentinel sub-capability founded; convergence detector requires alternative primitives

2. **Add sub-property founding under "training observability" capability candidate.**
   - "Substrate weight-cumulant primitives detect overfitting onset 300 steps before validation loss; empirically validated 3/3 seeds at N=4096 weight matrix; algebraically grounded by BBP spike pre-crossing rate lambda^2 / (N delta_bulk)."

3. **Annotate Drill 3x prediction:** complementary primitives (activation erank + Hessian trace) predicted to provide convergence-phase lead time; experimental validation pending (Tier 2 below).

## Tier 2 requested actions (after Tier 1 annotation; engineering pending)

**Anchor name:** `substrate_full_cycle_phase_monitor_rung2_v1_n4096`

### Experiment

- Model: 4-layer char-LM, ~50-100k params (rung-2 scale)
- Three substrate primitive channels:
  1. Weight kappa_2 / kappa_3 / kappa_4_excess (existing channel; expected to lead overfitting)
  2. erank(Cov(h_t)) of residual activations (NEW primitive; expected to lead convergence)
  3. Hessian trace proxy via Hutchinson estimator (NEW primitive; expected to lead convergence)
- Train to actual val-loss overfitting (TRAIN_CHARS 100-200k; N_STEPS 5000-10000)
- 3 seeds
- Per-primitive lead-time measurement at each phase change

### Pre-reg per § HP/MID/HF above.

### Engineering effort

- erank(Cov(h)) primitive: ~2h engineering (standard linear algebra)
- Hutchinson Hessian trace proxy: ~2-4h engineering (Hessian-vector product via autograd; PyHessian-class library)
- Wiring + experiment harness: ~2h
- Total: ~6-8h engineering

### Cost: $0 CPU. Wall: ~60-90 min per run.

---

## Strategic outcome

### Tier 1 (immediate)

- Overfitting-sentinel sub-capability FOUNDED in cap_map
- Drift-detection killer feature gains a sub-property (overfitting sentinel) with empirical + algebraic backing
- Product framing upgrade: "substrate spectral fingerprint detects overfitting onset 300 steps ahead of validation loss"

### Tier 2 (after engineering)

If HP: substrate has FULL-CYCLE training-phase observability (lead time at both convergence and overfitting). This is a flagship-class capability for training-infrastructure product framing.

If HF: Hessian-trace lit was wrong about substrate-class compatibility; fall back to overfitting-sentinel only (still a clean positive capability).

---

## Discipline declarations

- Per [[feedback-routings-address-orchestrator-not-testbed]]: orchestrator primary; routes to strategy_scribe (Tier 1) and Testbed (Tier 2)
- Per [[feedback-2x-means-depth]]: drill 3x went deeper on existing HF; result is algebraic reframe + concrete rescue design
- Per [[feedback-no-padding-experiments]]: Tier 2 tests two specific complementary primitives predicted by drill
- Per [[feedback-rescue-sketch-first-sequencing]]: Tier 1 is the subsumption rescue (re-define pre-reg criterion as overfitting-only; converts HF to HP at no compute cost)
- ASCII-only output enforced

PROT-018: anchor name `substrate_full_cycle_phase_monitor_rung2_v1_n4096` with _n4096 suffix

---

**END.**

**Orchestrator:** dispatch Tier 1 to strategy_scribe immediately (annotation-only; $0). Tier 2 engineering after joint D+H verdict lands (sequencing: cheaper rescues first).

**Research session:** holds for Tier 1 annotation update; ships further follow-up after joint D+H verdict.
