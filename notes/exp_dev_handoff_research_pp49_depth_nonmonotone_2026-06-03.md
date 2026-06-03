# exp_dev hand-off -- research: PP-49 counterfactual depth non-monotonicity

**Filed-by:** research sub-agent
**Date:** 2026-06-03
**Trigger:** Research note d:/AI/hd-instrument/notes/research_drill_pp49_counterfactual_depth_nonmonotone_2026-06-03.md
**Pause state:** Respect orchestrator_paused.flag; do not queue without orchestrator auth.

Per [[feedback-no-experiment-design-in-prompts]]: this file hands TASK + WHY + CONTRACT + AUTONOMY. exp_dev decides anchor names, sweep grids, threshold formulas, HF1/HF2/HF3 numerical bounds, queue choice + ETA, and pre-committed cap_map decisions.

---

## Anchor candidates (rank-ordered)

### 1. HRC depth-parity discriminator (tier: DECISIVE -- cheap decisive test for mechanism)

**Anchor pointer:** Measure cf_cos at depths 1 through 8 for the same xi_cf configuration used in the depth-5 HARD-FAIL / depth-8 PASS run. Do NOT change N, alpha, pattern set, or rank-1 substitution parameters. Only sweep depth d in {1, 2, 3, 4, 5, 6, 7, 8}.

**Substrate-product reading:** Confirms or refutes parity-class mechanism for HRC. If confirmed (odd fail / even pass), the product API constraint is deterministic and algebraically predictable. If refuted (monotone failure, depth 1-5 fail then 6-8 pass), a different mechanism (forbidden-eigenspace or capacity-growth-with-depth) drives the failure and needs its own fix.

**Tier hint:** CPU smoke, <5 min wall, N=4096. Low cost, decisive.

**Why now:** The product narrative "HRC works at arbitrary depth" is currently WRONG per PP-49 data. Before Phase 0.5b distillation MVP ships, the depth-band envelope must be characterized. This is the cheapest possible characterization.

---

### 2. Odd-depth sign-flip check (tier: CONFIRMING -- verify anti-alignment not just low cosine)

**Anchor pointer:** At depth-5 (HARD-FAIL) and depth-7, measure the SIGNED cf_cos (not absolute value). Record mean and sign across seeds. If cf_cos is consistently NEGATIVE (not just near zero), parity mechanism is confirmed even if magnitude is low. Compare cf_cos(d=5) vs -cf_cos(d=5) vs threshold.

**Substrate-product reading:** Distinguishes parity-class (negative cosine) from noise-floor failure (near-zero cosine). Needed to decide whether odd-depth fix is NEGATE-xi_cf (works for parity) vs ADD-PADDING-LAYER (works for either).

**Tier hint:** CPU smoke, <2 min, add to same sweep as Anchor 1 with negligible cost.

**Why now:** Same anchor, zero marginal cost. Sign data is collected automatically if cf_cos is reported as signed scalar.

---

### 3. HRC even-depth capacity envelope (tier: EXPLORATORY -- medium priority)

**Anchor pointer:** For even depths d in {2, 4, 6, 8, 10, 12} and alpha in {0.02, 0.05, 0.10}, measure cf_cos to find alpha_max(d) where even-depth counterfactual recovery degrades below HP. Maps the full envelope for product spec.

**Substrate-product reading:** Defines the full HRC product envelope: (d, alpha) pairs that guarantee cf_cos >= HP. Essential for Phase 0.5b MVP product documentation.

**Tier hint:** CPU medium, ~20 min wall (6 depths * 3 alpha values * N=4096 * 5 seeds). Queue after Anchors 1+2 confirm parity mechanism.

**Why now:** After Anchors 1+2 confirm parity, this maps the full product guarantee. Do not run before parity is confirmed -- design may need adjustment.

---

## Context pointers

- Research note: d:/AI/hd-instrument/notes/research_drill_pp49_counterfactual_depth_nonmonotone_2026-06-03.md
- PP-49 baseline context: d:/AI/hd-instrument/notes/research_phase0_0c_r2_kbump_pp47xpp49_baseline_2026-06-02.md
- SKAH-M class note: d:/AI/hd-instrument/notes/ (see project memory project_substrate_skahm_class_confirmed_2026-05-27.md)
- Cap map: d:/AI/hd-instrument/data/substrate_capability_map.md

---

## Contract

exp_dev designs the anchor, selects queue, writes the testbed script, pre-registers HP/MID/HF bands, and ships. Research has NOT pre-committed any threshold formulas or anchor names -- those are exp_dev's domain.

The parity-class mechanism prediction (Section 3 of research note) is the THEORETICAL PRIOR, not a pre-committed threshold. exp_dev reads it and decides whether it warrants a HARD-PASS band or a MIDDLE band.

## Autonomy declaration

exp_dev decides: anchor name, exact depth sweep, N, seeds, timeout, queue assignment, HP/MID/HF formulas, and cap_map annotation post-verdict. Research has handed the TASK (parity discriminator), WHY (product claim revision for Phase 0.5b MVP), and CONTRACT (per feedback_no_experiment_design_in_prompts). The rest is exp_dev's domain.
