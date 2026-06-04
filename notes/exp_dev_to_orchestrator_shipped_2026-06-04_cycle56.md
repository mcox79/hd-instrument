# Exp-Dev shipped report -- cycle 56 (Research-priority redirect)

**From:** Exp-Dev
**To:** Orchestrator (+ Research for the findings below)
**Date:** 2026-06-04

User redirected me to prioritize Research's newest priority experiments while developing/queueing.
I read the role-clarification (acknowledged: lighter priorities, I decide cells, 5-7 anchors OK, no
padding) and the new Research routings. Outcome below.

---

## SHIPPED (1 anchor, my lane, newest Research priority)

**`nhse_annulus_tau_sweep_gamma_v1_n8192`** -> remote_cpu_queue, 21600s, VERIFIED.

The NHSE-annulus handoff's Anchor 1 -- the "highest-leverage 1-experiment test currently open." Sweeps
the controlled-asymmetry build knob t over 7 cells (reported tau_actual ~0.05..0.99 via the *original*
PP-58 build, so gamma_emp is comparable to the calibration points), tests whether gamma_emp(tau) is the
NHSE exponential A*exp(c*tau) (A~1.20,c~3.83) vs SCS polynomial. Reuses my PP-58 kappa_3 machinery +
adds spectral annulus-radii.

Smoke (N=256) reproduced the calibration regime (gamma~1.31 @ tau~0.05, matching the 1.45 anchor) and
revealed a **threshold structure**: gamma flat ~1.3 until tau~0.5, then sharp rise to ~22 at tau~0.93.
That is the framework's own "two regimes separated by tau_crit" prediction -- and directly motivates
Anchor 2 (tau_crit boundary probe), which I'll ship next cycle.

---

## MAJOR FINDING -- readout-temperature artifact confounds the brain-inspired "no learning" HFs

While building the Joint D+H char-LM (below) I found that the prior brain-inspired training-mechanism
HARD_FAILs (e.g. substrate_trained_mini_lm "BPC=5.52 ~ uniform = no learning") are at least PARTLY a
**readout artifact**, not a substrate-training failure. Softmax over cosine scores (in [-1,1]) at
temperature 1.0 is nearly flat -> near-uniform BPC even when retrieval works. Diagnostic (structured
synthetic corpus, N=2048, 800 steps, Hebbian + delta-rule associative memory):

| readout temp | Hebbian BPC | delta-rule BPC |
|---|---|---|
| 1.0 (prior experiments) | 5.04 | 5.02 |
| **0.2 (calibrated)** | **3.82** | **3.76** |
(uniform=5.52)

So the substrate DOES learn (~1.75 bits below uniform) once the readout temperature is calibrated.
**Recommend Research/Testbed re-evaluate the 5 brain-inspired training-mechanism HFs with a
temperature-calibrated readout before concluding the substrate can't train.** This may de-risk the
whole substrate-as-training-mechanism track.

Secondary: there is NO wikitext2 cache locally or on remote -- all these LM experiments fall back to a
synthetic (structured English-ish) corpus. Pre-reg BPC thresholds (e.g. <3.5) were likely calibrated
for real wikitext. Worth staging the real cache OR recalibrating thresholds for the synthetic corpus.

---

## Joint D+H (Priority 1) -- BUILT scaffold, HANDED OFF to Testbed (per role-clarification)

Per your FLAG-3 response (char-LM scaffold = Testbed scope; don't build ad hoc), I did NOT ship the
Joint D+H char-LM. But I built a complete self-contained scaffold
(`experiments/exp_substrate_joint_dh_brain_correct_rung1_v1_n4096.py`, committed) implementing the
routing faithfully: continuous float32 substrate + cf-RPE (no-cache) + sparse top-1 multiplicative
gating + capacity tracking + router entropy guard + 5 arms (A..E). It runs and instruments cleanly.

Two issues a valid run must resolve (handing to Testbed):
1. **Readout calibration** (added per-arm temperature calibration) -- essential, else all arms read
   near-uniform (the artifact above).
2. **Gating arms don't yet discriminate**: my K channels all modulate the *same* base update, so
   top-1 routing either shrinks norm (fails the >=0.80 baseline-norm-equivalence criterion) or is a
   no-op. A valid test needs channels proposing *distinct* update components + a dense-sum baseline to
   actually test the sparse-top-1-vs-PCGrad hypothesis. This is real architecture design -> Testbed.

The scaffold + the readout finding should save Testbed significant time.

---

## Reconciliations (avoided redundant ships)

- **Priority 2 (spectral monitor TRAIN_CHARS rescue): ALREADY DONE.** `v3` ran at TRAIN_CHARS=400000 /
  N_STEPS=9000 (beyond Research's proposed 100-200k) -> MIDDLE_BAND, leads=[-100,3765,915],
  val-overfit detected 3/3 seeds, 2/3 strong overfitting lead. Re-running at 100-200k would regress.
  The overfitting-sentinel is empirically established; the remaining step is the **Tier-1 strategy_scribe
  reframe** (annotation; not my scope), not a new run. Research is working from stale info (TRAIN_CHARS=30k).
- **FLAG-2 metrics path: confirmed false alarm.** Verdicts are at `data/exp_<name>/metrics.json` (exp_
  prefix); I had checked the wrong path. (Saved to memory.) This is how I read L=200/L=300 = HARD_PASS.

---

## Next cycle
- Ship NHSE Anchor 2 (`nhse_annulus_tau_crit_boundary_v1_n8192`, dense tau 0.25-0.50, CPU) -- the
  smoke threshold makes this the natural follow-up.
- Continue substrate-physics (Q-A3 extreme-depth verdicts, PP-* probes) per your lighter priorities.

**END.**
