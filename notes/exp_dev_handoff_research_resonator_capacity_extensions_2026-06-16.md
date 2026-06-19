# exp_dev hand-off - research: resonator capacity extensions

filed: 2026-06-16
trigger: research drill `notes/research_resonator_capacity_extensions_2026-06-16.md` identified a lit-anchored capacity-extension recipe (Langenegger 2024 ACF/IMF noise injection) with single-knob tuning that the substrate can drop in at fixed budget. The research drill was filed in response to a HONEST_BOUNDED verdict on the substrate's resonator-cleanup primitive at its prior breakdown threshold.

pause state: check d:/AI/hd-instrument/data/orchestrator_paused.flag before shipping any anchor. If paused, this hand-off is read-only structural context for the orchestrator to pick up post-resume; do NOT ship to queue until the flag is cleared and the orchestrator/USER confirms.

Per [[feedback-no-experiment-design-in-prompts]]: this hand-off names anchors and substrate-product readings; it does NOT prescribe cell-level experiment parameters. exp_dev owns the design call. The role of this file is to surface lit-anchored candidates with pre-registered HARD-PASS/HARD-FAIL bands so exp_dev can ship with confidence.

---

## Anchor candidates (rank-ordered)

### ANCHOR 1 (RANK 1, lit-anchored, cheapest, highest expected gain)

ANCHOR: ACF (Asymmetric Codebook Factorizer) variant per Langenegger et al. 2024 arXiv:2412.00354.

- substrate-product reading: at the substrate's prior HONEST_BOUNDED breakdown threshold, apply a single bitflip-perturbation pass to ONE codebook copy at init time (no per-iteration noise, no algebra extension, no new operator). Measure capacity envelope shift at SAME restarts cap + iters cap.
- tier hint: TIER-2 capacity extension at fixed algebra. Not a tier-3 architectural primitive; not a tier-1 polish.
- why-now: directly addresses the HONEST_BOUNDED verdict via the published-dominant failure-mode mitigation (limit-cycle escape). 50x-1e5x quoted gain in literature; substrate-realistic 5x-10x given residue+FPE composition confound.
- pre-registered HARD-PASS: >=10x M_break shift with single-noise-knob p in {0.05, 0.10, 0.20} at fixed restarts+iters cap, iter-count vs M curve sub-linear past prior M_break.
- pre-registered HARD-FAIL: <2x shift at all three knob values OR catastrophic accuracy drop (<0.50) inside prior envelope.
- pre-registered MIDDLE_BAND (most-likely outcome): 1.5x-3x shift; substrate's residue+FPE composition introduces additional collision-floor that pure ACF cannot escape.
- cost: ~1-2 hr CPU pre-flight on existing resonator primitive.
- risk class: structural-additive (no operator, no algebra change). LOW.

### ANCHOR 2 (RANK 2, lit-anchored, second to ANCHOR 1)

ANCHOR: IMF (Iterative-noise Factorizer) variant per same Langenegger 2024 paper.

- substrate-product reading: add Gaussian noise per resonator step at single sigma value. Tests whether per-step noise or init-only noise is dominant for substrate's failure mode (PRED-2 in research note).
- tier hint: TIER-2 capacity extension.
- why-now: discriminator between basin-shrinkage and limit-cycle failure modes; if ACF >= IMF gain, limit-cycle dominant (matches lit consensus); if IMF >> ACF, substrate's failure mode is novel.
- pre-registered HARD-PASS: same as ANCHOR 1 (>=10x M_break shift).
- pre-registered HARD-FAIL: same as ANCHOR 1.
- cost: ~1-2 hr CPU.
- risk class: structural-additive. LOW.

### ANCHOR 3 (RANK 3, contingent on ANCHOR 1+2 outcome)

ANCHOR: composed ACF + modern-Hopfield single-step cleanup head (per Yeung 2024 arXiv:2403.13218 + Ramsauer 2020 closed-form beta).

- substrate-product reading: stacks Axis 1 (stochastic injection) + Axis 2 (Hopfield-attention readout). Tests whether composed extension closes the gap to lit-quoted 50x when single-axis delivers MIDDLE_BAND only.
- tier hint: TIER-2/TIER-3 boundary (algebra not changed but readout primitive added).
- why-now: ONLY dispatch if ANCHOR 1 OR ANCHOR 2 returns MIDDLE_BAND (1.5x-3x). If ANCHOR 1 returns HARD_PASS, skip; if both return HARD_FAIL, drill failure-mode characterization (Lu/Bremer 2024 kernel-aware decoder family) instead.
- pre-registered HARD-PASS: gain >=10x with composed stack.
- pre-registered HARD-FAIL: composed stack still <3x.
- cost: ~3-5 person-days impl + ~1-2 hr CPU validation.
- risk class: structural-additive + new readout primitive. MEDIUM.

### ANCHOR 4 (DEFERRED, do NOT ship from this hand-off)

ANCHOR: hierarchical-resonator partition per Renner 2024 arXiv:2208.12880.

- why deferred: requires task-surface partition that the substrate may not naturally expose at current dim. Heavy per-scale tuning per published results (k differs per factor, sigma differs, hysteresis differs) - NOT fixed-budget-compatible without significant adaptation work.
- substrate-product reading: this anchor needs strategy-level decision before exp_dev should touch it. Surface as "open option for after ANCHOR 1+2+3 outcomes."

---

## Context pointers (file paths, not summaries)

- research note: `d:/AI/hd-instrument/notes/research_resonator_capacity_extensions_2026-06-16.md`
- cross-thread prior 1: `d:/AI/hd-instrument/notes/research_DEEP_DRILL_cleanup_noise_FPE_interaction_20260616_1435.md`
- cross-thread prior 2: `d:/AI/hd-instrument/notes/research_bundle_norm_null_hypothesis_2026-06-16.md`
- cross-thread prior 3: `d:/AI/hd-instrument/notes/research_DEEP_DRILL_phase_C_tier_3_architecture_decision_prep_20260616_1414.md`
- cap_map: `d:/AI/hd-instrument/notes/substrate_capability_map.md` (HONEST_BOUNDED row for resonator-cleanup is the trigger)
- pause flag check: `d:/AI/hd-instrument/data/orchestrator_paused.flag`

---

## Contract

This file is auto-discovered by exp_dev on emergency-refill cycles (it scans `notes/exp_dev_handoff_*.md` sorted by mtime). It surfaces lit-anchored anchors with pre-registered failure bands - exp_dev decides the cell parameters, smoke-gate, and ship order.

The pre-registered HARD-PASS/HARD-FAIL bands above are AUTHORITATIVE - they were derived during the research drill against published literature and substrate-product positioning constraints. exp_dev should not soften them at design time; if cell parameters force a softer threshold, that itself is a finding worth surfacing back to research before shipping.

The ordering rank 1 -> 2 -> 3 is a sequential gate: ship ANCHOR 1 (or 1+2 in parallel if queue capacity allows); read verdict; only ship ANCHOR 3 if MIDDLE_BAND; never ship ANCHOR 4 from this hand-off without strategy/USER approval.

---

## Autonomy declaration

exp_dev owns:
- cell parameter selection (N, M, F, exact noise knob values within the {0.05, 0.10, 0.20} ACF and {0.01, 0.05, 0.1} IMF ranges)
- smoke-gate design (pre-flight cheap test)
- queue ship order
- post-ship REMOTE VERIFY discipline
- self-test per formula-selftests rule

exp_dev does NOT own (these stay with research/strategy):
- the HARD-PASS/HARD-FAIL bands (pre-registered above)
- the anchor ranking (1 > 2 > 3, 4 deferred)
- the cap_map row binding (research will close the HONEST_BOUNDED row based on verdict)

Research will be re-dispatched as 2x-drill IF: (a) HARD_FAIL on ANCHOR 1+2 (need FPE-kernel collision-floor characterization), OR (b) MIDDLE_BAND on composed ANCHOR 3 (need to escalate to GHRR or hierarchical partition decision).
