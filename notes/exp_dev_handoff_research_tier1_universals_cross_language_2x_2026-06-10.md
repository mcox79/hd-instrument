# exp_dev hand-off -- research: Tier 1 universals cross-language 2x drill

Filed-by: research sub-agent
Date: 2026-06-10
Trigger: notes/research_drill_tier1_universals_cross_language_2x_2026-06-10.md
Urgency: MEDIUM -- 5 engineering anchors for validating cross-language universality of Tier 1 primitives; directly tests whether the product claim "universal Tier 1" is defensible or requires revision to "Tier 0 universal core + per-family Tier 1"

---

## Pause state

Experiments below are PROPOSED, not queued. Pause gate applies per normal exp_dev protocol.
Check data/orchestrator_paused.flag before dispatching.

---

Per [[feedback-no-experiment-design-in-prompts]]:
This file provides ROUTING POINTERS and ANCHOR CANDIDATES only.
Experiment design details (cell grids, hyperparameter values, script paths) are to be authored by exp_dev from the research note + cap_map context. Do NOT treat the descriptions below as implementation specs.

---

## Anchor candidates (rank-ordered)

### Anchor 1: tier0_universal_primitive_isA_crosslang_v1 (TIER0-ISA-XL)

Anchor pointer: Research note Section 6 Test 1 + Section 9 Anchor E1; Speer et al. 2017 ConceptNet 5.5; Vossen 1998 EuroWordNet; Navigli-Ponzetto 2012 BabelNet.
Substrate-product reading: Trains substrate on English IsA triples from ConceptNet; tests on Chinese ConceptNet IsA triples. Measures whether the taxonomic hierarchy (most robustly cross-linguistic relation) transfers without per-language tuning. If recall@1 > 0.50 on Chinese, the IsA-grounded Tier 0 claim is empirically supported. This directly gates the product claim on cross-language transfer.
Tier hint: CPU-local laptop. Pure ConceptNet subset -- no GPU, no cloud. Very fast. Run this first before any other anchor.
Why-now: The current overclaim ("universal Tier 1") is undefended empirically. This anchor is the cheapest possible gate for the most important sub-claim. One day CPU work, $0 cost.

Pre-reg bands:
  HARD-PASS: recall@1 > 0.50 on Chinese IsA queries using English-trained substrate
  MIDDLE-BAND: 0.25-0.50 (IsA partially transfers; needs per-family calibration)
  HARD-FAIL: recall@1 < 0.20 (IsA does NOT transfer; universality claim wrong at architecture level; product claim needs major revision)

### Anchor 2: tier1_usedFor_failure_confirm_v1 (USEDFOR-XL-FAIL)

Anchor pointer: Research note Section 6 Test 2 + Section 9 Anchor E2; Speer et al. 2017; Talmy 2000 satellite/verb-framing.
Substrate-product reading: Same setup as Anchor 1 but for UsedFor relation. This is a FAILURE VALIDATION anchor -- expected outcome is HARD-FAIL or MIDDLE-BAND (low Chinese recall). A HARD-FAIL here is scientifically CORRECT: it confirms UsedFor should not be in universal Tier 0 and must be in per-language Tier 1. Run in parallel with Anchor 1.
Tier hint: CPU-local. Can be bundled with Anchor 1 in same script (run both relation types in one pass).
Why-now: Confirms the model structure (Tier 0 = universal core, Tier 1 = per-family). Without this anchor, UsedFor's exclusion from Tier 0 is literature-only; this makes it empirical.

Pre-reg bands:
  EXPECTED (confirms model): recall@1 < 0.15 on Chinese UsedFor = CORRECT outcome
  UNEXPECTED (contradicts model): recall@1 > 0.40 = UsedFor IS cross-linguistic; add to Tier 0

### Anchor 3: causal_type_crosslang_force_dynamic_v1 (CAUSAL-XL)

Anchor pointer: Research note Section 6 Test 5 + Section 9 Anchor E4; Wolff & Song 2003; Talmy 1988 force dynamics.
Substrate-product reading: Constructs Cause/Enable/Prevent triples using force-dynamic encoding across English and Chinese ConceptNet. Tests whether the substrate correctly distinguishes the three causal types cross-linguistically. Wolff & Song (2003) established these three are cognitively universal; this anchor tests whether they are substrate-representationally universal. If HARD-PASS, causal primitives are the strongest Tier 0 candidates beyond IsA.
Tier hint: CPU-local. Requires hand-constructing ~30 triplets per causal type per language (~180 triplets total). Manual construction is the main cost.
Why-now: Causal primitives (CAUSE, ENABLE, PREVENT) are the most theoretically robust Tier 1 candidates beyond taxonomic IsA. Empirical validation here would significantly strengthen the product architecture claim.

Pre-reg bands:
  HARD-PASS: recall@1 > 0.55 for all three causal types across EN and ZH
  MIDDLE-BAND: 0.35-0.55 (some causal types transfer, others do not; document which)
  HARD-FAIL: recall@1 < 0.30 for any causal type (force-dynamic encoding insufficient; requires cross-lingual training)

### Anchor 4: spatial_frame_conflict_v1 (SPATIAL-FRAME-XL)

Anchor pointer: Research note Section 6 Test 4 + Section 9 Anchor E3; Levinson 2003 Frames of Reference; Levinson et al. 2002 Cognition.
Substrate-product reading: Constructs 20 absolute-frame spatial queries (north-of, uphill-from, across-river-from -- Guugu Yimithirr/Tzeltal style) vs 20 relative-frame queries (left-of, in-front-of -- English style). English-trained substrate expected to fail on absolute-frame. Expected outcome is HARD-FAIL on absolute-frame (< 0.20 recall). This anchor DOCUMENTS the failure mode and sets the scope for per-language Tier 1 spatial extension.
Tier hint: CPU-local. Diagnostic anchor -- documents a known gap, not testing a hypothesis that might be true.
Why-now: Spatial frame failure is the most literature-supported universality breakdown. If substrate spatial relations are used in any product feature, this failure mode must be documented before cross-language deployment.

Pre-reg bands:
  Expected (confirms Levinson): absolute-frame recall < 0.20 = correct outcome, documents gap
  Unexpected (contradicts Levinson): absolute-frame recall > 0.55 = English vertical axis partially rescues; needs deeper analysis

### Anchor 5: evidentiality_gap_audit_v1 (EVIDENTIAL-AUDIT)

Anchor pointer: Research note Section 3.2 + Section 9 Anchor E5; Whorf 1956; Wierzbicka 1996 NSM.
Substrate-product reading: Constructs 20 queries requiring evidential distinction (direct witness vs inference vs hearsay) using Turkish-style propositions. Tests whether English-trained substrate recovers evidential type. Expected: complete failure (English training has no evidential slot). This is a DIAGNOSTIC anchor -- no PASS/FAIL threshold, documents the required slot extension for 25% of world's languages. Outputs a concrete extension spec: what new relation type or property slot would cover evidentiality.
Tier hint: CPU-local. Manual query construction. Very fast to run (< 30 min once queries are built).
Why-now: Evidentiality is a structural gap in any English-centric Tier 1 for 25% of world's languages. Documenting it now prevents future cross-language deployment failures.

Pre-reg bands:
  Diagnostic only -- document failure mode and required slot extension. No numerical PASS/FAIL.

---

## Context pointers

- Research note (primary): d:/AI/hd-instrument/notes/research_drill_tier1_universals_cross_language_2x_2026-06-10.md
- HOL meta-reasoning drill (cross-thread -- ToM universality): d:/AI/hd-instrument/notes/research_drill_HOL_meta_reasoning_biology_3x_2026-06-09.md
- HOL exp_dev handoff (related): d:/AI/hd-instrument/notes/exp_dev_handoff_research_HOL_meta_reasoning_biology_3x_2026-06-09.md
- Substrate v3.0 compositional cliff note: d:/AI/hd-instrument/memory/substrate_v3_compositional_cliff_crossed.md
- NORTH STAR note: d:/AI/hd-instrument/memory/north_star_functional_system_beats_LLMs.md
- Active priorities: d:/AI/hd-instrument/notes/active_priorities.md

---

## Contract

exp_dev owns:
- Anchor prioritization within this file (may reorder based on queue depth + runner availability)
- Experiment design details: ConceptNet subset selection, query construction, script structure
- Pre-reg envelope refinement from the bands above
- Go/no-go decision per pause gate

Research sub-agent provided:
- Ranked anchor candidates with substrate-product readings
- Pre-reg band proposals (NOT final -- exp_dev calibrates from cap_map context)
- Context pointers (file paths, not summaries)
- Key literature citations (in research note) for any anchor that needs design justification

---

## Autonomy declaration

exp_dev may dispatch Anchors 1 and 2 immediately (bundle into one CPU script) if (a) pause gate is clear and (b) runner has CPU capacity. These are the cheapest possible validation anchors ($0, < 1 hour).
Anchor 3 (causal) requires manual triplet construction first; dispatch after Anchors 1-2 complete.
Anchors 4-5 are diagnostic and may be deferred until Anchors 1-3 have verdicts; they document failure modes, not validate positive claims.
No authorization needed for CPU-local anchors under the standing experiment authorization.
