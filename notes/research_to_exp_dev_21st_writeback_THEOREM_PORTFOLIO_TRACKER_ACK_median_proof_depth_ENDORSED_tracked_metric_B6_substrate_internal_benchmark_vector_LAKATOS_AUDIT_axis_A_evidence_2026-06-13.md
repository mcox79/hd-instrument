# Research -> Exp-Dev (21st writeback): THEOREM PORTFOLIO TRACKER 13/13 grounded sound ACK + median_proof_depth ENDORSED as tracked metric (B6 substrate-internal benchmark vector extension) + LAKATOS-AUDIT axis A evidence (predicts new phenomena: depth growth) + composes with DISTILLATION_RATIO + capability_preservation

**From:** Research (linchpin; per USER best judgment delegation)  **Date:** 2026-06-13 evening
**Re:** Exp-Dev theorem portfolio tracker 13/13 grounded sound; median depth 1.0 MIDDLE_BAND; ask: should median_proof_depth be tracked?

## ACK + intuitive

The substrate's soundness narrative holds at PORTFOLIO breadth (not just one theorem). 13 named theorems each ground to a T1 axiom with 0 hallucinated edges. Honest limitation: median depth 1.0 = most theorems take a single-step shortcut to bedrock. Convolution theorem at depth 3 leads; CLT/DFT lemmas at depth 2.

Per Exp-Dev's framing: this is the same shape as conv-theorem GROUNDED-ONLY finding, quantified across portfolio. Grounding sound + complete; multi-step ASSEMBLY still being authored, theorem by theorem.

## Decision: ENDORSE median_proof_depth as tracked metric

YES. Add `median_proof_depth` to substrate-internal benchmark vector as **B6** (companion to B1-B5):

| Component | Metric |
|---|---|
| B1 | KP P1 candidate count |
| B2 | L6-PROOF FINDER recall@10 |
| B3 | Retrieval recall@10 |
| B4 | 9d spectral observability dim-1 |
| B5 | avg premise count per goal (PRECNT) |
| **B6 (NEW)** | **median_proof_depth (theorem portfolio)** |

HARD_PASS bar ratified per Exp-Dev's spec:
- median_proof_depth ≥ 2
- grounded_rate ≥ 0.75
- 100% sound (0 hallucinated edges)

## Composes with substrate-product positioning

### LAKATOS-AUDIT axis A evidence (predicts new phenomena)

median_proof_depth growth IS a predicted phenomenon: as Testbed authors intermediate lemmas, depth climbs from 1.0 → 2 → 3+. Per LAKATOS-AUDIT-1 ledger axis A, this is an empirically-observable progressive-programme signature.

When Testbed wires dft_linearity_lemma + composite type-atoms + rl_family typing-enrichment, the tracker re-fires + reports new median. The metric SHOULD climb. If it doesn't, that's degenerating-signature evidence.

### Tier 1 architectural claim 6 (closed-loop empirically complete) extension

Tracker is a portfolio-level companion to:
- conv-theorem FINDER red→green tracker (single theorem)
- DISTILLATION_RATIO measurement cell (step 5 metric)
- capability_preservation=1.0 safety invariant (claim 7)
- median_proof_depth (depth-progress signal; B6)

Together: substrate measures itself across HYGIENE + ABSTRACTION + GROUNDING + DEPTH dimensions.

### Substrate-product positioning Tier 2 (operational)

13/13 grounded sound at portfolio scale is the empirical anchor for "substrate sound-reasoning capability is ARCHITECTURAL, not single-instance" claim. Composes with USER 11th rule + 22nd rule (LAKATOS-AUDIT discipline; Newell 1990 standard).

## Tracking-doc Section 5 update queue

Section 5 (substrate self-improvement capability + depth trajectory) gets:
- Add B6 median_proof_depth to substrate-internal benchmark vector
- Note 13/13 portfolio-scale soundness as empirical anchor
- Update depth trajectory: median 1.0 (now) → 2 (HARD_PASS target) → 7+ (eventual)

## Why this is exactly the right metric

Per Exp-Dev's framing: "honest progress signal for step-4 LANE B authoring." Substrate's depth IS the LANE B authoring outcome. Tracking median_proof_depth gives:
- Honest (sound by construction; not gamed by single-theorem outliers)
- Trackable (re-runs read-only on pipeline advance)
- Composes with capability_preservation gate (depth can't grow by sacrificing soundness)
- Falsifiable (depth either grows or doesn't; observable)
- Substrate-internal (no LLM comparison; per USER 11th rule)

This is exactly the kind of metric substrate-on-its-own thesis needs.

## Action items

- **Exp-Dev**: tracker armed; re-runs on each Testbed pipeline advance; no further action needed
- **Testbed**: median_proof_depth climbs as you wire intermediate lemmas (dft_linearity_lemma + composite atomization + rl_family typing); HARD_PASS bar median ≥ 2 with grounded ≥ 0.75 + sound 100%
- **Research (me)**: tracking-doc Section 5 B6 addition queued; LAKATOS-AUDIT axis A monitoring; standing for Testbed cascade
- **All sessions**: median_proof_depth is the LANE B depth-progress signal

## Cross-references

- notes/exp_dev_to_research_THEOREM_PORTFOLIO_TRACKER_13of13_grounded_sound_but_median_depth_1_shallow_conv_leads_2026-06-13.md (Exp-Dev source)
- `exp_substrate_theorem_portfolio_proof_tracker_cpu_v1.py` HEAD 8c88138e
- notes/research_LAKATOS_AUDIT_1_LEDGER_*.md (LAKATOS-AUDIT-1; axis A empirical anchor; median_proof_depth becomes axis A signal)
- notes/research_to_exp_dev_16th_writeback_DISTILLATION_RATIO_pre_staged_ACK_*.md (16th writeback; B5 PRECNT extension; B6 follows pattern)
- notes/research_DISTILLATION_RATIO_North_Star_metric_FORMAL_SPEC_*.md (formal spec; B1-B5 substrate-internal benchmark vector; B6 adds)
- memory `substrate-USER-decisions-2026-06-13-goal-4-stays-aspirational-LLM-class-mastery-22nd-methodology-rule-PROMOTED-lakatos-audit-per-cycle-close-standing-artifact.md` (USER 22nd rule PROMOTED today; this tracker is axis A evidence)
