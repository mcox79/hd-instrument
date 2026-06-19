# exp_dev hand-off -- research: B8 logit residual analysis RECAPTURE

Filed-by: research:opus 2026-06-17
Trigger: 3x deep research drill on B8 logit sparse residual MIDDLE r=0.27 + scorecard self-flagged M_crit_gain proxy-measurement bug
Source research note: d:/AI/hd-instrument/notes/research_B8_logit_residual_recapture_2026-06-17.md

Per [[feedback-no-experiment-design-in-prompts]]: this hand-off names ANCHOR CANDIDATES and points at substrate cells; experiment design (cell topology, loop counts, gates) is the Exp-Dev session's autonomous call.

Pause state: hand-off written REGARDLESS of pause flag; pickup is gated by data/orchestrator_paused.flag at exp_dev dispatch time. If paused, queue as next-cycle pickup.

## Anchor candidates (rank-ordered)

### Anchor 1 (PRIMARY) -- B8 hetero-r-gated rebuild

- Anchor pointer: cap_map row B8 (logit residual analysis); MIDDLE r=0.27 with self-flagged M_crit_gain proxy-measurement bug
- Substrate-product reading: the canonical interpretability literature (Bricken 2023, Belinkov 2022, Rajamanoharan 2024, Vig 2020) prescribes a held-out-counterfactual-pair hetero-association protocol with Gated-SAE shrinkage correction. The substrate's current 0.27 is most likely a method-contingent auto-association proxy floor, NOT a fundamental B8 ceiling.
- Tier hint: Tier-1 (closes a self-flagged scorecard integrity bug); HARD-PASS at hetero-r-gated >= 0.55, HARD-FAIL at hetero-r-gated < 0.30 AND auto-r > 0.50
- Why-now: the scorecard already self-flagged the proxy bug; running B8 at higher resolution without the protocol rebuild would re-trigger the bug. This rebuild is the rule-19 operational response that the scorecard self-flag already entitles.
- Pre-reg HARD bands: PRED-1, PRED-2, PRED-3 in source note section (c)

### Anchor 2 (DIAGNOSTIC) -- auto-vs-hetero gap calibration

- Anchor pointer: same B8 cell, additional measurement
- Substrate-product reading: report BOTH auto-r and hetero-r on the SAME held-out split. The gap (auto-r minus hetero-r) is the most-replicated proxy-bug diagnostic in the probing-survey literature (Belinkov 2022 selectivity).
- Tier hint: Tier-2 (diagnostic for anchor 1; not a standalone capability claim)
- Why-now: cheap; computed for free as a side-effect of anchor 1; necessary for integrity reporting per the 2026-06-16 method-contingent-bound framing rule

### Anchor 3 (LONG-TAIL) -- shrinkage knob ablation

- Anchor pointer: same B8 cell, ablation
- Substrate-product reading: re-fit decode WITHOUT Gated-SAE shrinkage correction to measure how load-bearing the Rajamanoharan 2024 knob is in the VSA regime. The literature value of the knob is established for transformer-MLP-residual; the VSA codebook geometry is mathematically adjacent but not identical, so the knob's load-bearingness is empirically open.
- Tier hint: Tier-3 (knob-ablation; low-leverage but cheap)
- Why-now: optional; defer if compute is tight

## Context pointers

- d:/AI/hd-instrument/notes/research_B8_logit_residual_recapture_2026-06-17.md (this drill's source note; all method details + HARD bands + cross-thread synthesis)
- d:/AI/hd-instrument/notes/research_modern_hopfield_capacity_retrieval_crossover_2026-06-16.md (sister honest-bounded method/config framing)
- d:/AI/hd-instrument/notes/research_drift_detection_backbone_invariant_2026-06-17.md (parallel measurement-coupling-bug finding)
- d:/AI/hd-instrument/MEMORY.md (substrate_methodology_rule_19_adversarial_self_correction; scorecard_overstates_clean_core)

## Contract section

- Per [[feedback-no-experiment-design-in-prompts]]: exp_dev owns experiment topology
- Per [[feedback-query-privacy-decomposition]]: no substrate-specific terms surfaced in research drill
- Per [[feedback-lit-scan-calibration-penalty]]: P estimates deflated; HARD bands pre-registered in source note
- Per [[feedback-measured-bounds-are-method-config-contingent]]: framing throughout note is method/config-contingent, not fundamental
- Per [[feedback-no-papers-product-only]]: substrate-product implications in source note (e); no paper framing

## Autonomy declaration

Exp-Dev session has autonomy on: cell topology, exact split sizes, training-loop counts within the smoke gate, ordering of anchors 1/2/3, and ship-or-defer-anchor-3 call. Research has pre-registered the HARD bands and method-contingent framing; Exp-Dev does not need to re-derive those.
