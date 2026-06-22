# p1 phase-diagram-action cell HARD_FAIL-at-smoke (discriminator-invalid; HARNESS-too-small)

**Date:** 2026-06-22
**Cell:** `experiments/exp_p1_action_at_any_position_phase_diagram_v1.py` (commit pending)
**Smoke metrics:** `data/exp_p1_action_at_any_position_phase_diagram_v1/metrics.json` (HARD_FAIL; run_mode=smoke; n_seeds=1; elapsed 8.7s)
**Cell-author spawn:** ab893a942aaab5de6 (HALT-not-dispatched per Fix #16 discipline)

## Headline

The USER-directed lane sub-item (c) cell — "substrate acts at any position in the phase diagram + data survives phase transformations" — smoke-ran but HARD_FAILED at the HARNESS level. The within-P_0 baseline (the load-bearing sanity-check that anchors the operating-point-shift ratios) didn't reach the 0.50 floor at smoke scale.

Per Fix #16: this is HARNESS-OK + DISCRIMINATOR-INVALID at smoke scale. The mechanism itself was NOT tested — the smoke is too small for within-P_0 to converge. Mechanism not yet falsified.

## Smoke detail

| Pair | WITHIN_P_0 | REPLAYED | FRESH | BLANK | ratio (REPLAYED/WITHIN) |
|------|-----------:|---------:|------:|------:|-----------:|
| A: V_C lift (1024→2048) | 0.400 | 0.300 | 0.267 | 0.033 | 0.750 |
| B: N_DIM lift | 0.267 | 0.467 | 0.433 | 0.000 | ~1.75 (replayed BETTER than within!) |
| C: joint lift | similar | | | | |

Substrate-only-decode gate intact (zero LLM calls). cv=0.000 (n_seeds=1, so trivially). HALT-no-dispatch-full disposition correct.

## Honest scope

**The cell design is sound — the smoke scale is the issue.** The pre-reg DRAFT (`notes/p1_action_at_any_position_phase_diagram_cell_prereg_2026-06-22.md`) specifies K=200 atoms / 3 seeds / N_DIM=4096 for the full config. The smoke config used K=200 at SMALLER N_DIM (per the cell-author's smoke-config choice) which is below the substrate Hebbian saturation point where within-P_0 baseline should hit ≥0.95.

The interesting pair-B finding (REPLAYED 0.467 > WITHIN 0.267) is potentially substrate-favorable — at small N_DIM, replaying atoms into a larger substrate may IMPROVE recall (more capacity). But the within baseline is too low to interpret.

## Three options for revival

A. **v2 with larger smoke config:** K=500 OR N_DIM=8192 at smoke; verify within-P_0 ≥0.95 BEFORE running the operating-point-shift comparisons. Then full config at K=200/N=4096 retains the original test.

B. **v2 with N_DIM-scaled smoke:** keep K=200 but scale smoke N_DIM to where within ≥0.95 (likely N_DIM=2048 at smoke for K=200; full at N_DIM=4096 stays the same).

C. **Defer p1 + queue research drill on operating-point-shift survival mechanism:** the USER-directed claim was that data SURVIVES phase transformations. p1 v1 tested ONE specific mechanism (replay via re-encoded keys at new operating point) — there may be OTHER mechanisms (e.g. the whitening primitive shipped today; the c3 SequenceMatrix; direct W matrix transfer with re-projection).

## Director disposition

**Option A: v2 with larger smoke config.** Quick fix; the cell logic is correct; only the smoke regime needs adjustment. Next cycle: cell-author respawn with explicit smoke-N_DIM=8192 OR K=500 constraint; if within-P_0 ≥0.95 at smoke, dispatch full with original config.

## What this confirms (information-positive)

1. Cell-author + smoke-VET caught a real cell-design issue (smoke regime mismatch) without burning remote_cpu compute on a known-broken full run
2. The Fix #16 discriminator-regime check (within-P_0 floor 0.50) is doing its job — flagged the smoke as discriminator-invalid
3. Substrate-only-decode gate intact through the (broken) smoke
4. Pair-B result (REPLAYED > WITHIN at small N_DIM) is intriguing — substrate-favorable hint at the N_DIM-lift transform; warrants deeper investigation in v2

## Composes with

- USER-directed phase-diagram lane (the original directive note `project_phase_diagram_action_data_survives_phase_transformations_USER_2026-06-22.md`)
- Phase-portrait v3 INVENTORY_NON_CERT atom (cert-trail; lists transform-survival evidence atoms; p1 was meant to add a NEW chain-grade axis)
- Whitening primitive (today; `hdlab/whitening.py`) — could improve within-P_0 baseline by decorrelating encoder residuals before Hebbian write

Cell NOT committed to main per cell-author HALT discipline; diagnostic artifact only. v2 queued.

— Research (Director); p1 v1 HONEST_NEGATIVE-at-smoke; revival route = Option A; cert-trail durable artifact.
