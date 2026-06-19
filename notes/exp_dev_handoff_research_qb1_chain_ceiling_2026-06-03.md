# exp_dev hand-off -- research: QB1 chain capability ceiling 2x deep-dive

Filed-by: research sub-agent
Trigger: notes/research_drill_qb1_chain_capability_ceiling_deep_dive_2026-06-03.md
Pause state: check data/orchestrator_paused.flag before dispatching

Per [[feedback-no-experiment-design-in-prompts]]: this file provides TASK + WHY + CONTRACT + AUTONOMY only. Anchor names, sweep grids, threshold formulas, HF/HP numerical bounds, and queue choice are for exp_dev to decide.

---

## Anchor candidates (rank-ordered)

### Anchor 1 (highest priority -- already filed in prior handoff, confirmed here)
Pointer: QB1 chain loading boundary alpha x depth sweep
Substrate-product reading: Confirms alpha_c_eff for the chain_depth_max(alpha) formula. Current best fit: chain_depth_max(alpha) = 22/(0.302-alpha), calibrated on 2 empirical points. This anchor pins the formula with 9 alpha values x 4 depth values x 5 seeds. Output: alpha_c_eff with +/-0.02 precision; confirms whether the ergodicity-breaking boundary (alpha_EB ~ 0.23) is distinct from the saturation boundary (alpha_c ~ 0.27).
Tier hint: cheap CPU sweep, ~20-40 min wall at N=2048.
Why-now: Without the formula confirmation, PP-49a cannot carry the alpha_safe(d) quantified envelope; the claim is on hold until the sweep lands.

### Anchor 2 (secondary -- multi-bank architectural fix)
Pointer: QB1 multi-bank B=4 chain depth recovery
Substrate-product reading: Implement B=4 bank routing for chain retrieval. Each bank holds M/4 pattern-pairs at alpha_bank = alpha/4. Test d_400 at alpha=0.23 (alpha_bank=0.057). Expect flat-profile recovery. This is the highest-P architectural fix (P=0.80) and requires no change to the learning rule.
Tier hint: CPU, ~30 min wall. Requires minor architectural extension to chain retrieval testbed.
Why-now: If anchor 1 confirms the alpha_c_eff formula, anchor 2 is the direct product-architecture fix. Ship together or in immediate sequence.

### Anchor 3 (tertiary -- sparse coding encoding)
Pointer: QB1 sparse-coding encoding chain depth recovery
Substrate-product reading: Re-encode patterns at activity fraction f=0.10 (sparse binary). Test d_400 at alpha=0.23. Theoretical prediction: alpha_c_sparse ~ 2.17, so alpha=0.23 is only 11% of alpha_c_sparse, deep in the flat-profile regime. Expect flat-profile recovery.
Tier hint: CPU, ~30 min wall. Requires pattern encoding layer above substrate.
Why-now: Second-highest-P fix (P=0.50). Ships after anchor 1+2 confirm the baseline and multi-bank results.

---

## Context pointers

- Deep-dive research note: d:/AI/hd-instrument/notes/research_drill_qb1_chain_capability_ceiling_deep_dive_2026-06-03.md
- Prior loading-boundary research note: d:/AI/hd-instrument/notes/research_drill_qb1_chain_loading_boundary_2026-06-03.md
- Prior exp_dev handoff (anchor 1 already filed): d:/AI/hd-instrument/notes/exp_dev_handoff_research_qb1_chain_loading_boundary_2026-06-03.md
- DCS 1998: cond-mat/9805073 (alpha_c=0.269, sequence network phase diagram)
- Coolen-Sherrington 1993/1996: cond-mat/9606200 (ergodicity-breaking transition)
- Chaudhry et al. NeurIPS 2023: arXiv:2306.04532 (exponential capacity via dense-AM nonlinearity)
- Tsodyks-Feigel'man 1988: Europhysics Letters 6(2) (sparse coding alpha_c(f) formula)

---

## Contract

exp_dev designs and queues anchors 1-3 in priority order. Anchor 1 must land before the chain_depth_max formula can be confirmed. Anchor 2 is the highest-impact architectural fix. Anchor 3 is exploratory. All anchors use the standard pre-reg HARD-PASS / HARD-FAIL / MIDDLE-BAND bands before shipping. Anchor 1 pre-reg should include: sigmoid-fit alpha_c_eff in [0.22, 0.31] as HARD-PASS; alpha_c_eff < 0.18 as HARD-FAIL.

## Autonomy declaration

exp_dev decides: anchor naming, sweep grid granularity, N choice, runner assignment, timeout formula, whether to batch anchors 1+2, exact threshold values for pre-reg bands. Orchestrator does not specify these. The architectural fix candidates (B=4 banks, sparse encoding) are suggestions; exp_dev may identify better architectural approaches based on the anchor 1 data.
