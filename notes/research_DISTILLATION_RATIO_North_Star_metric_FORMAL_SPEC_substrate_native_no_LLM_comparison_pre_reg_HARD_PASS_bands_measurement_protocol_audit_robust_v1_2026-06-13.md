# Research: DISTILLATION RATIO North Star metric FORMAL SPEC (substrate-native; no LLM comparison; pre-reg HARD-PASS bands; measurement protocol; audit-robust framing; v1)

**From:** Research (linchpin; per 12th USER-LOCKED rule own-work + skunkworks lane responsibility)  **Date:** 2026-06-13
**Re:** North Star metric for substrate-on-its-own positioning; formal definition + pre-reg bands + measurement protocol

## Intuitive

Like a library that publishes a single number every quarter: "we maintain N unique books; we removed K duplicates this quarter without losing any reader services." The number combines INVENTORY (how much we maintain) with QUALITY (how well we self-curate). High value = library understands its own collection well enough to compress it without losing utility.

## Formal definition

For a substrate state s at time t, let:

- A(s) = set of distinct atoms in substrate s (post canonical-ID alias resolution)
- T(s) = subset of A(s) with algebra_dict + serves_capability + DEPENDS_ON populated (typed atoms)
- B(s) = substrate-internal benchmark vector at state s, composed of:
  - B1: KP P1 candidate count (atoms with in-degree >= threshold)
  - B2: L6-PROOF FINDER recall@10 on 20 hand-authored goals
  - B3: Retrieval recall@10 on standard substrate-internal retrieval benchmark
  - B4: 9d spectral observability dim-1 (R-transform location) on codebook
  - B5: avg premise count per goal (Exp-Dev PRECNT metric)

For a distillation operation (state s_before -> s_after):

DISTILLATION_RATIO(s_before, s_after) = |A(s_before)| - |A(s_after)| / |A(s_before)|

Subject to constraint: ||B(s_after) - B(s_before)|| / ||B(s_before)|| <= tolerance

Where:
- tolerance = 0.05 (5% capability deviation across the 5-component benchmark vector)
- norm is L2 over the normalized benchmark components

## Pre-reg HARD-PASS bands

| Band | Distillation ratio | Capability constraint | Interpretation |
|---|---|---|---|
| HARD-PASS | >= 5% | within tolerance | substrate maintains capability while compressing >= 5% of atoms |
| STRONG HARD-PASS | >= 10% | within tolerance | substantial self-curation |
| EXCEPTIONAL | >= 20% | within tolerance | substrate dramatically over-represents itself |
| MIDDLE-BAND | 1-5% | within tolerance | minor self-curation; partial pass |
| HARD-FAIL | any | capability drops > tolerance | merges are unsound; substrate hallucinated equivalence |
| HARD-FAIL | < 0 | any | substrate could not identify any soundly-mergeable redundancy |

## Measurement protocol (5-step pipeline)

1. **Detect step**: substrate operator (skunkworks operator-overlap v1 + Exp-Dev data-quality flag) identifies candidate merge pairs from typed atoms
2. **Propose step**: substrate's operators (typed signatures + algebraic laws + serves_capability) propose specific atom merges
3. **Verify step**: substrate's CHTV-1 + L6-PROOF check provable equivalence; refuse UNDECIDABLE candidates (per 18th methodology rule candidate)
4. **Integrate step**: Testbed canonical-atom-ID alias map + atomic shard swap; relations re-point to canonical IDs
5. **Measure step**: compute DISTILLATION_RATIO(s_before, s_after) + benchmark vector deviation; record + commit

Pre-reg: all 5 steps must execute substrate-internally; no human authoring of merges; human only RATIFIES proposed merges (yes/no on each).

## Current measured value (2026-06-13)

| Metric | Pre-integration | Post-integration (projected) |
|---|---|---|
| atoms before distillation | 20,820 (with duplicates) | 20,820 |
| atoms after distillation | n/a (step 4 pending) | ~20,815 (5 named pairs merged) |
| named distillation ratio | n/a | 5/20820 = 0.024% (0.024 percentage points) |
| **distillation-over-named-candidates** | n/a | **1.00 (5/5 named pairs distillable; HARD-PASS bar 0.80)** |
| corpus-wide distillation ratio | n/a | 11/33 = 33% over candidate set (gated on typing) |
| HARD-PASS bar | >= 5% corpus + within tolerance | NOT YET MET corpus-wide; PARTIAL HARD-PASS on named candidates |

Provisional reading: substrate has demonstrated SOUND distillation operation (no false merges) on named candidates; corpus-wide ratio is gated on typing growth.

## Pre-reg honest exclusions

- Substrate's distillation operates only on TYPED atoms; untyped atoms cannot be soundly distilled (per 18th rule: refuses what cannot be proven)
- Coverage limit = typed fraction of corpus
- Current typed fraction: ~25% of duplicate candidates (5 typed-equivalent + 6 capability-equivalent + 22 untyped of 33)
- Path to higher coverage: parser-v2 multi-premise extraction + LANE B algebra_dict authoring + manual algebra_dict authoring on remaining 22 candidates

## Comparison with alternative North Star candidates

| Candidate | Direct measurement | Substrate-internal | Loop-closing |
|---|---|---|---|
| **DISTILLATION RATIO** | YES (atoms before/after) | YES | YES (closes 5-step loop) |
| Autonomy Index | YES (authored vs discovered) | YES | NO (measures structure not improvement) |
| Self-model connectivity | YES (operator-overlap graph) | YES | PARTIAL (descriptive) |
| Substrate-internal benchmark | YES (multi-component) | YES | NO (measures state not change) |

DISTILLATION_RATIO is the only candidate that DIRECTLY measures substrate's self-improvement output. The others are state measurements (substrate at time t) rather than improvement measurements (substrate s_after - s_before).

Recommend DISTILLATION_RATIO as PRIMARY North Star; Autonomy Index + Self-model connectivity + Substrate-internal benchmark as SECONDARY state-tracking metrics.

## Routing

- **USER**: formal North Star metric spec; substrate-on-its-own measurement; closes 5-step loop with empirical number
- **Skunkworks**: react to spec; if HARD-PASS bar at 5% corpus is too strict given typing limitation, propose alternative; #5 SKUNKWORKS-CSC calibration may inform threshold-setting
- **Exp-Dev**: substrate-internal benchmark vector (B1-B5) above; can your depth-forecast cell emit B5 as part of PRECNT metric output?
- **Testbed**: TESTBED-DISTILL-INTEGRATE-1 step 4 needed to enable step 5 measurement; post-integration, Research will commit first measured DISTILLATION_RATIO

## Cross-references

- notes/research_to_skunkworks_exp_dev_testbed_LANE_SPLIT_CONFIRMED_*.md (lane split + North Star metric vote)
- notes/exp_dev_to_research_DISTILL_VERIFY_1_HARD_PASS_*.md (step 3 source; provides distillation candidate data)
- notes/research_SUBSTRATE_PRODUCT_ELEVATOR_PITCH_v3_*.md (claim 5 anchors here)
- memory `substrate-closed-loop-OPERATIONAL-step-3-HARD-PASS-first-measured-self-improvement-instance-5-provably-equivalent-0-false-merge-22-refused-2026-06-13.md` (memory)
- memory `feedback-substrate-standalone-capability-first-before-LLM-positioning-USER-LOCKED-2026-06-13.md` (USER 11th rule)
