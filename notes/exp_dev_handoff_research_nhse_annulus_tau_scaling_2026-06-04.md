# exp_dev hand-off -- research: NHSE-annulus tau-dependent gamma scaling 2x drill

**Filed-by:** research sub-agent (sonnet), 2026-06-04
**Trigger:** notes/research_drill_nhse_annulus_tau_scaling_2x_2026-06-04.md -- NHSE-annulus framework identified as correct mechanism for dual SCS failure; exponential gamma(tau) = 1.20 * exp(3.83 * tau) fit to 2 anchor points; tau-sweep probe pre-registered with HP/MID/HF bands.
**Pause state:** Check data/orchestrator_paused.flag before dispatching.

Per [[feedback-no-experiment-design-in-prompts]]: this file hands TASK + WHY + CONTRACT + AUTONOMY to exp_dev. Anchor names, sweep grids, threshold formulas, and cap_map decisions are exp_dev's responsibility. No inline experiment design here.

---

## Anchor Candidates (rank-ordered)

**1. tau-sweep gamma probe (tier: GPU smoke -> FULL)**
- Anchor pointer: measure gamma_emp at tau in {0.05, 0.10, 0.30, 0.50, 0.70, 0.90, 0.95} at fixed N; fixed M and d parameters consistent with prior runs.
- Substrate-product reading: discriminates NHSE-annulus (exponential gamma(tau)) from SCS (polynomial); identifies tau_crit in [0.25, 0.45]; validates or refutes the closed-form inversion tau_required(gamma_target).
- Tier hint: CPU smoke (5 seeds, 3-4 tau values) to verify monotone increase; GPU FULL if smoke is monotone and gamma(tau=0.50) >= 4.0.
- Why now: the exponential fit is calibrated from only 2 data points (low-tau cluster + tau=0.926). A 7-cell tau sweep is the cheap decisive test that either confirms the NHSE-annulus framework at P_deflated=0.31 or refutes it and triggers a framework revision. This is the highest-leverage 1-experiment test currently open.

**2. tau_crit boundary probe (tier: CPU FULL)**
- Anchor pointer: dense sampling at tau in {0.25, 0.30, 0.35, 0.40, 0.45, 0.50} to identify the regime transition point.
- Substrate-product reading: determines whether the transition is continuous (smooth crossover, consistent with NHSE) or discontinuous (spectral jump, consistent with critical NHSE). A discontinuous jump refutes the smooth exponential formula and implies a first-order spectral phase transition.
- Tier hint: CPU FULL (no GPU required for phase boundary identification; N can be moderate).
- Why now: the tau_crit prediction (0.25-0.45) is the most uncertain element of the NHSE-annulus framework. The boundary probe resolves this at low compute cost and informs whether the tau_required inversion formula is valid or breaks down at the transition.

---

## Context Pointers

- Research note (full algebraic derivations): d:/AI/hd-instrument/notes/research_drill_nhse_annulus_tau_scaling_2x_2026-06-04.md
- Prior first-pass drill (SCS framework; gamma_emp ~8.0 context): d:/AI/hd-instrument/notes/research_drill_spectral_gap_alternative_frameworks_2x_2026-06-04.md
- Cap-map correction routing note: d:/AI/hd-instrument/notes/routing_capmap_correction_scs_to_nhse_annulus_2026-06-04.md
- Capability implication note (spectral gap grounding): d:/AI/hd-instrument/notes/capability_implication_note_spectral_gap_scs_grounding_2026-06-04.md

---

## Contract

exp_dev designs anchors with preregs per envelope-fail-bands; no inline experiment design in this file. Dispatch via queue_add.sh GPU or CPU as appropriate. Post-ship REMOTE VERIFY per role contract. Formula self-tests required per [[feedback-strategy-spec-formula-selftests]] if any closed-form expressions appear in the anchor spec.

## Autonomy Declaration

exp_dev has full autonomy over: anchor naming, N/M/seed choices, queue assignment (GPU vs CPU), timeout formula application, pre-registration bands, smoke-vs-FULL gating, and cap_map annotation after verdict. The research note provides the theoretical framework and pre-registered HP/MID/HF bands as starting points; exp_dev may tighten or adjust these based on implementation constraints.
