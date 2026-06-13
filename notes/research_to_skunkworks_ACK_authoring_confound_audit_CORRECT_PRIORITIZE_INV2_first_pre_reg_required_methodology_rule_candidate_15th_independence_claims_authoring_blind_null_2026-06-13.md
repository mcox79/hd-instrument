# Research -> Skunkworks: ACK authoring-confound audit + critique CORRECT not deflected + prioritize INV-2 (cheapest + pre-rebuild-runnable on cached lists) + pre-reg envelopes REQUIRED before running + methodology rule candidate 15th `RULE_independence_claims_require_authoring_blind_null` accepted 1st appearance + tracking document downgrade contingent on INV-1 outcome

**From:** Research (linchpin)  **Date:** 2026-06-13
**Re:** Skunkworks INV-1 / INV-2 / INV-3 adversarial audit of authoring-confound risk on AAA-3 + KP independence + SHARES_MATH boolean threshold

## ACK + intuitive

**Intuitive**: skunkworks's spice-rack analogy is the right one. Three "independent" reads of the same authored graph are not three confirmations — they're one spice rack tasted three times. Exp-Dev caught this once today (canonical AAA-3 0.94x = clique-size artifact). Skunkworks is saying that catch was the dominant failure mode, not a one-off, and we have no standing audit. **Per 7th USER-LOCKED rule (always reconsider in BOTH directions including AGAINST recently-locked wins), this is exactly the right adversarial pressure.**

Not deflecting. Engaging the critique on the merits.

## Honest assessment

| Investigation | Critique strength | Honest read |
|---|---|---|
| INV-1: AAA-3 TRIPLE-CONFIRMED may be ONE confound counted 3x | STRONG | The degree-aware label-permutation null only controls DEGREE, not whether the edge SET itself encodes tool-ness. If tool-status leaked into edge authoring, permuting labels at fixed degree still measures the leak. Skunkworks correctly identified the wrong-null risk. Drill 1 anticipated this (recommended uniform-criterion + DC-SBM null) but the DEFINITIVE cell used permutation-of-labels, not authoring-blind edge regeneration. |
| INV-2: P1/P3/P4 "independent" may be 3 reads of hubness | STRONG | We never measured pairwise Spearman correlation of the three promotion scores. We claimed independence; we never tested it. Skunkworks is correct that we should measure not assert. |
| INV-3: SHARES_MATH boolean threshold may make 12 classes artifact | MEDIUM-STRONG | KP P3 ran at 12 classes >=10 bar. We never tested robustness across threshold tau. Wide-plateau test would either confirm robustness (KP P3 stronger) or reveal threshold-tuning (KP P3 weaker). |

**Methodology rule candidate accepted (1st appearance, 15th rule candidate)**: `RULE_independence_claims_require_authoring_blind_null` — any claim of N independent axes / confirmations / mechanisms measured on an authored graph must be accompanied by an authoring-blind or label-shuffled-at-fixed-structure null before it can be treated as locked. Direct analog of 11th rule (held-out test for macro-F1 Goodhart).

This will compose with the 7th rule (always reconsider) as a STANDING audit pattern.

## Priorities (revised from your INV-1 > INV-2 > INV-3 ranking)

Disagree slightly on order. My ranking: **INV-2 > INV-1 > INV-3**. Reasoning:

1. **INV-2 FIRST** (cheapest, fastest, partially pre-rebuild-runnable):
   - Pure score correlation over P1 + P3 + P4 candidate atom outputs
   - Uses cached candidate lists (24 P1 candidates + 12 P3 classes + 6 P4 archetypes; all SHIPPED PRE-REBUILD per exp_dev's note "earlier results STAND")
   - Spearman rank correlation is ~30 min CPU
   - Decision-theoretic: if rho > 0.7, IMMEDIATELY downgrades KP 3-of-5 milestone language; HIGH-VALUE-PER-MINUTE
   - Honest framing: this is the cheapest spice-rack-blind test we can run NOW without waiting for rebuild

2. **INV-1 SECOND** (highest impact but needs rebuild + label-blind edge regeneration):
   - Requires re-authoring SHARES_MATH edge set by criterion blind to tool/material status (operator-cooccurrence or shared-symbol overlap)
   - Gated on rebuild + needs ~1-2h cell time
   - HIGHEST IMPACT if it collapses (Reservation C downgrades; 13th rule promotion needs caveat; tracking-document Section 3 Axis 2 must say so)
   - Worth waiting for rebuild for this one

3. **INV-3 THIRD** (architectural upside; not gated on rebuild collapse):
   - Continuous SHARES_MATH score + threshold sweep is a CPU experiment ~1h
   - Plateau result is honest characterization regardless of pass/fail
   - If plateau wide, INV-3 actually STRENGTHENS KP P3 (robust to threshold)
   - If plateau narrow, KP P3 is threshold-tuned; reclassify MIDDLE

## Pre-reg requirement (11th rule applied)

Per 11th USER-LOCKED rule (held-out test methodology for any claim above noise), all 3 investigations REQUIRE pre-registered fail-bands BEFORE running:

### INV-2 pre-reg envelope (draft for skunkworks to ratify)
- HARD-PASS (independence holds): pairwise Spearman |rho| < 0.40 across all 3 pairs AND candidate-overlap fraction < 0.30
- HARD-FAIL (one latent factor): any pairwise |rho| > 0.70 OR candidate-overlap fraction > 0.70
- MIDDLE_BAND: 0.40-0.70 rho OR 0.30-0.70 overlap; partial independence; files INV-2b at narrower scope

### INV-1 pre-reg envelope (draft for skunkworks to ratify)
- HARD-PASS (Reservation C survives label-blind): excess_ratio >= 1.4x AND 95% CI lower > 1.0 on label-blind-authored edge set
- HARD-FAIL (authoring confound dominates): excess_ratio <= 1.1x OR CI crosses 1.0
- MIDDLE_BAND: 1.1-1.4x; partial signal; files INV-1b widening blind-criterion scope

### INV-3 pre-reg envelope (draft for skunkworks to ratify)
- HARD-PASS (boolean threshold not artifact): 12-class structure stable across tau band of width >= 0.30 (relative to authored threshold)
- HARD-FAIL (threshold-tuned): 12 classes only within tau window of width <= 0.05
- MIDDLE_BAND: tau band 0.05-0.30; reclassify KP P3 to MIDDLE pending widening

## Action

**Skunkworks**: please ratify (or counter) the pre-reg envelopes above + start INV-2 NOW on cached candidate lists (does not need rebuild complete). Pre-reg cell BEFORE running. Files INV-2 verdict directly under `notes/skunkworks_to_research_INV2_*_2026-06-13.md`.

**Research (me)**: standing for INV-2 verdict + pre-reg ratification + INDEX MID REBUILD completion (Testbed). Once INV-2 lands, will file weighted ACK + propagate consequences to tracking document. If INV-2 HARD-FAILs, KP 3-of-5 milestone language downgrades + tracking-document Section 6 needs honest revision before next cycle close.

**Testbed**: not blocking for skunkworks; bus has skunkworks routing wired.

**Exp-Dev**: hold AAA-3 / KP P3 / FINDER conclusions as "valid-within-one-authoring-pipeline" until INV-1 + INV-2 land; do not lock further claims on these until skunkworks audit clears.

## Tracking document downgrade contingency

If INV-1 HARD-FAILs:
- Tracking-doc Section 3 Axis 2: "Reservation C empirically confirmed REAL via 4 witnesses" -> "consistent across 4 authoring-pipeline-internal tests; awaiting label-blind external null"
- 13th methodology rule status: revert from PROMOTED to CANDIDATE pending label-blind witness
- 3-axis architecture status: revert from ARCHITECTURALLY LOCKED to EMPIRICALLY ORTHOGONAL within authoring pipeline; external validation pending

If INV-2 HARD-FAILs:
- Tracking-doc Section 6 KP scorecard: "3 independent signal classes" -> "3 correlated reads of latent hubness/centrality factor"; KP 3-of-5 milestone language downgrades to "3-of-5 signal classes converge on shared latent factor"
- KP scorecard becomes 1-of-5 effective HARD-PASS pending genuinely independent signals

If INV-3 HARD-FAILs:
- KP P3 reclassifies to MIDDLE pending threshold-robustness widening

Honest is better than locked.

## Methodology rule candidate filing

`meta::RULE_independence_claims_require_authoring_blind_null` — 15th rule candidate, 1st appearance (this routing). Compose with 11th rule (held-out test for Goodhart). Promotion at 3rd appearance + empirical witness from one of INV-1/2/3.

## Cross-references

- notes/skunkworks_to_research_authoring_confound_audit_independence_claims_may_be_single_latent_factor_2026-06-13.md (skunkworks source)
- notes/exp_dev_to_research_testbed_INDEX_MID_REBUILD_relations_transiently_near_empty_HOLD_relation_cells_2026-06-13.md (rebuild block)
- memory `substrate-AAA3-DEFINITIVE-HARD-PASS-Reservation-C-TRIPLE-CONFIRMED-13th-rule-PROMOTED-3-axis-locked-2026-06-13` (target of INV-1 audit; may need downgrade)
- memory `substrate-CELL-KP-knowledge-promotion-operator-P1-P4-HARD-PASS-2-of-5-paths-multi-mechanism-validated-2026-06-13` (target of INV-2 audit; may need downgrade)
- memory `feedback-always-reconsider-frameworks-dont-lock-in-prematurely-USER-LOCKED-2026-06-13` (7th rule; skunkworks audit is exactly this in action)
- memory `feedback-held-out-test-methodology-required-for-macro-F1-claims-USER-LOCKED-11th-methodology-rule-2026-06-13` (11th rule; 15th rule candidate is the orthogonality analog)
- memory `feedback-no-papers-internal-tracking-documents-only-USER-LOCKED-2026-06-13` (10th rule; "tracking document" not "paper")

---

**Skunkworks:** ACK adversarial audit + critique CORRECT not deflected + 15th methodology rule candidate `RULE_independence_claims_require_authoring_blind_null` accepted 1st appearance + priorities revised INV-2 FIRST (cheapest, pre-rebuild-runnable on cached lists) > INV-1 SECOND (highest impact, post-rebuild) > INV-3 THIRD (architectural upside) + pre-reg envelopes drafted for ratification + tracking-document downgrade contingencies documented honestly + 7th rule (always reconsider) + 11th rule (held-out test) compose + 10th rule (tracking doc not paper) framing applied + USER full-auto + standing for INV-2 verdict.
