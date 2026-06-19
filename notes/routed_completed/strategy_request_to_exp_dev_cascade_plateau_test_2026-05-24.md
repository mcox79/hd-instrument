# strategy_request_to_exp_dev: cascade-plateau falsifier (candidate v)

**Filed.** 2026-05-24 by Research (deep-drill alt-theoretical-homes).
**Trigger.** Research-drill candidate (v) saddle-cascade plateaus identified as highest-P alternative theoretical home for substrate's three-plateau retention (P=0.46 after lit-scan calibration penalty). Pred-4-orthogonal; Pred-4 verdict still pending.
**Pause-flag check.** Orchestrator must verify `data/orchestrator_paused.flag` absent before queue_add. At file-write time: ABSENT.
**Source note.** notes/research_alternative_theoretical_homes_2026-05-24.md (see Top-2 deep drill, candidate v).

---

## TASK

Test whether substrate's three retention plateaus (0.94 / 0.74 / 0.60) emerge from saddle-cascade dynamics in the student-teacher overlap ODE structure (Saad-Solla 1995, Biehl-Schwarze 1995). Saddle-cascade framework predicts plateau heights are DISCRETE fixed-points of the overlap-matrix permutation-symmetry structure — should be IMMUNE to continuous parameters (matching empirical signature) and should SHIFT DISCRETELY as teacher-overlap fraction crosses integer-mode-count thresholds.

## WHY (without designing the experiment)

If candidate (v) fits, it replaces 1-RSB as the explanatory framework for the surviving plateau structure. 1-RSB has accumulated 6+ negative observations; we need a backup home BEFORE Pred-4 lands. Cascade-plateau framework is established in classical online-learning theory and predicts EXACTLY the substrate's signature (categorical discreteness, parameter-axis immunity). The drill identified this as a literature-coverage gap that R18/R23/R24 missed by privileging stat-mech framing.

## CONTRACT

Pre-register HARD-PASS / HARD-FAIL / MIDDLE-BAND thresholds before queue_add. Per envelope-fail-bands rule:

- **HARD-PASS:** retention vs corpus-overlap-fraction f ∈ {0.0, 0.25, 0.5, 0.75, 1.0} shows DISCRETE step structure: at most 5 distinct retention values, each plateau-internal-variance < 0.02. Bonus: plateau-count tracks K-mode-count exactly.
- **HARD-FAIL:** retention(f) is smooth-monotone (R² of linear-or-sigmoid fit ≥ 0.95) with NO discrete-jump structure.
- **MIDDLE-BAND:** partial step structure (2-3 visible jumps but with intermediate-variance > 0.02) or fit-R² in [0.85, 0.95].

Self-test cells required per [[feedback-strategy-spec-formula-selftests]] — exp_dev to derive the overlap-fraction → expected-saddle-fixed-point formula from Saad-Solla 1995 framework and verify 3-4 (input → expected) pairs before coding the main experiment.

## AUTONOMY

Exp_dev owns: anchor names, sweep grid (the f-fraction values listed are illustrative; exp_dev may add/refine), seed count, N choice (consistent with substrate operating point), CPU vs remote-CPU queue choice, ETA, pre-reg numerical bounds, self-test design, all script-level decisions.

Research did NOT specify the design. Per [[feedback-no-experiment-design-in-prompts]]: this is TASK + WHY + CONTRACT + AUTONOMY only.

## Falsifier cost estimate (informational, exp_dev may refine)

Research's drill estimated ~30-60 min CPU. If exp_dev's design is more expensive, that's exp_dev's call; flag to orchestrator if > 4 GPU-hours.

## Pred-4 orthogonality

This test does NOT assume hysteresis sign, does NOT use the M-axis sweep that Pred-4 sweeps, and does NOT interpret the result through 1-RSB framework. Safe to ship in parallel with Pred-4. **If Pred-4 lands first with HARD-PASS, this test still informs whether saddle-cascade is a *co-explanation* (both frameworks active).**

## Routing

To orchestrator: dispatch via routing_handler / orchestrator-routing skill. exp_dev_handoff file will be filed by exp_dev once design is set, per usual protocol.

---
BULK-ARCHIVED 2026-06-01: pre-2026-05-25 backlog OR processed-but-not-archived; cap_map v311+ reflects evidence of acted-on work; per dashboard inbox-clearance Path A.
