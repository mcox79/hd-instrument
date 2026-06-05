# CHANGE REQUEST -- Polynomial-p engineering: 2x2 factorial cells per BCM-SNR drill

**From:** Research session
**To:** Exp-Dev (primary)
**Inform:** Orchestrator
**Date:** 2026-06-04
**Subject:** Update polynomial-p modern Hopfield engineering routing cells to 2x2 factorial (p × write-mode) at N=512, per BCM-SNR-vs-p 2x drill output landed this turn.

**Supersedes cell list in:** `routing_polynomial_p_modern_hopfield_engineering_2026-06-04.md` (shipped earlier this turn)

---

## Status check requested

- [ ] Has polynomial-p=4 engineering started?
- [ ] If yes, can the cell list be updated before the empirical test dispatches?
- [ ] If engineering not started: this change-request applies directly

Expected: engineering not yet started (just shipped earlier this turn).

---

## What this change-request does (plain language)

The polynomial-p engineering routing originally specified 3 cells:
- N=200 p=4
- N=500 p=4
- N=3000 p=2 (classical baseline)

BCM-SNR-vs-p drill (just landed) identified that **WRITE MODE is a critical confound** previously unmeasured. The drill recommends a 2x2 factorial (p × write-mode) at N=512 as the cheapest decisive test. This change-request updates the cell list accordingly.

---

## Updated cell list (5 cells, 3 seeds each)

Anchor name template: `substrate_modern_hopfield_2x2_factorial_v1_N{N}_p{p}_{mode}`

| Cell | N | p | Write mode | Predicted outcome |
|---|---|---|---|---|
| A | 512 | 2 | cumulative | HARD_FAIL (current baseline; matches existing N=512 HF) |
| B | 512 | 2 | episodic | ??? (UNMEASURED; could reveal episodic alone rescues) |
| C | 512 | 4 | cumulative | HARD_FAIL (Hopfield floor freed but eigenvalue floor still binds at ~2000-3000) |
| D | 512 | 4 | episodic | HARD_PASS (both floors fall; N_threshold = 300-600 per drill) |
| E | 200 | 4 | episodic | HARD_PASS aspirational (most aggressive; tests super-linear N_threshold reduction; drill predicts ~60-200 capacity floor) |

3 seeds per cell = 15 measurements total.

Per-cell wall: ~10-30 min CPU. Total wall ~3-4h sequential.

---

## Write mode definitions

**Cumulative write mode (current default):**
- Substrate accumulates patterns across training samples
- M_eff grows without bound (until storage saturates)
- Eigenvalue-convergence floor binds: N > 1.5 * M_eff fails as M_eff -> N

**Episodic write mode (new variant; like REM-sleep consolidation):**
- Substrate resets between training samples (or after small batch)
- M_eff stays bounded (one sample worth of patterns)
- Eigenvalue-convergence floor stays low (N > 1.5 * M_eff_sample)
- Lit anchor: hippocampal pattern separation (Yassa-Stark 2011); RBM contrastive divergence (Hinton 2002)

Implementation: write-mode is a config flag in the training loop. Episodic adds a `substrate.reset()` call after each training sample (or per N-sample episode). No new primitives required; just a loop-control change.

---

## Pre-reg HP/MID/HF bands per cell

**Per-cell HP/MID/HF (same for each cell):**
- HARD-PASS: BPC < uniform - 1.0 nat (substantial learning); 3/3 seeds
- MIDDLE: BPC in [uniform - 1.0, uniform - 0.3] nat
- HARD-FAIL: BPC > uniform - 0.3 nat (no meaningful learning)

**Joint analysis pre-reg:**

Outcomes by 2x2:

1. **All four fail (Cell A/B/C/D all HF):** N=512 fundamentally insufficient regardless of p or write mode. Substrate-as-training-mechanism HF at this scale stands. Falls back to N>=2000 classical regime OR Joint D+H redesign.

2. **Cell B HP (episodic-alone rescues p=2):** **Game-changing simplification.** Write mode is the binding constraint; polynomial-p upgrade not needed. Engineering effort saved.

3. **Cell C HP (p=4 alone rescues; episodic not needed):** Both floors are p-dependent. Drill's prediction that BCM-SNR is partially p-independent refuted. Modern Hopfield upgrade alone sufficient.

4. **Cell D HP (joint required; B and C both fail):** Drill's prediction confirmed. Need BOTH polynomial-p AND episodic. Joint architecture required.

5. **Cell E HP (most aggressive cell works):** N_threshold << 500. Substrate becomes viable at very small scales. Highest-value outcome.

---

## Why this redesign is informative

Original 3-cell design didn't disambiguate write mode. Would have shown N=200/500 p=4 HF if cumulative writes were used, leading to incorrect conclusion that modern Hopfield upgrade doesn't help.

Updated 5-cell design:
- Cell A confirms baseline (cheap sanity)
- Cell B isolates episodic-write effect (could be sufficient alone)
- Cell C isolates polynomial-p effect at N=512 (drill predicts insufficient alone)
- Cell D tests joint effect (drill predicts HP)
- Cell E tests super-linear N_threshold scaling at N=200

Each cell rules out a specific hypothesis. Total compute budget unchanged from original 3-cell design (same per-cell wall + 2 extra cells = ~3-4h sequential).

---

## Engineering scope (updated)

In addition to the original polynomial-p=4 primitive swap (~10-20h), add:
- Write-mode config flag (cumulative vs episodic) in training loop: ~30-60 min engineering
- Per-cell anchor naming with mode suffix
- Per-sample substrate.reset() hook for episodic mode (1 line of code; reuses existing capacity-tracking primitive)

Total engineering increment: ~1-2h on top of original ~10-20h. Negligible.

---

## P_deflated estimates (updated per BCM drill)

- Cell D (p=4 episodic at N=512) HP: **0.40** (BCM drill prediction; episodic + p=4 should hit ~300-600 threshold; N=512 just above)
- Cell B (p=2 episodic at N=512) HP: **0.18** (drill suggests episodic alone insufficient; needs polynomial-p boost; but worth checking)
- Cell C (p=4 cumulative at N=512) HP: **0.10** (drill predicts eigenvalue floor still binds)
- Cell E (p=4 episodic at N=200) HP: **0.20** (most aggressive; drill predicts ~60-200 floor at p=4 episodic; N=200 at boundary)
- All four fail: **0.30** (would refute BCM drill predictions)

Joint probability that AT LEAST ONE of B/C/D/E lands HP: ~0.50.

This is meaningful — combined likelihood substrate-as-training-mechanism gets a positive empirical rescue at N <= 512 is ~50/50, with the joint D+H architecture as the next-aggressive fallback.

---

## Sequencing

1. **Engineering** (~10-20h): single-primitive polynomial-p swap + write-mode config flag
2. **Experiment dispatch** (~3-4h CPU wall sequential): 5 cells, 3 seeds each
3. **Verdict synthesis:** which cells HP determines next steps
4. **If Cell D or E HP:** ship cap_map sub-property founding ("substrate-as-training-mechanism viable at N=200-500 with episodic + p=4 modern Hopfield")
5. **If all HF:** ship Joint D+H redesign or DeltaNet fallback dispatch

---

## What I am NOT changing

- Engineering scope for polynomial-p primitive (still single-primitive swap; ~10-20h)
- Compatibility tests on observability primitives (cross-layer composition + deletion cert + drift detection at p=4)
- PROT-022 self-tests at new energy class
- Cost ceiling ($0)

Only changing: cell list and pre-reg analysis.

---

## Discipline declarations

- Per [[feedback-routings-direct-to-exp-dev]]: Exp-Dev primary; Orchestrator informed
- Per [[feedback-change-request-protocol]]: this is a change-request, not silent edit; status-check first
- Per [[feedback-2x-means-depth]]: BCM-SNR drill went deeper on the modern Hopfield finding; 2x2 factorial is the resulting design refinement
- Per [[feedback-no-padding-experiments]]: 5 cells each discriminate a specific hypothesis
- Per [[feedback-rescue-sketch-first-sequencing]]: cheapest rescue (write-mode-only) before structural rescue (polynomial-p upgrade)
- ASCII-only output enforced

PROT-018: anchor names use `_N{N}_p{p}_{mode}` suffix

---

**END.**

**Exp-Dev:** apply 2x2 factorial cells to the polynomial-p engineering routing. Engineering scope unchanged. Experiment cells updated. Total compute budget unchanged.

**Orchestrator:** informed. Verdict synthesis will indicate which architectural changes are binding for substrate-as-training-mechanism at small scale.

**Research:** holds for engineering completion + experiment verdicts; ships capability-implication note per outcome.
