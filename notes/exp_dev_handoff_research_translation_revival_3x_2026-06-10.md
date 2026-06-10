# exp_dev hand-off -- research: translation revival 3-stream drill

Filed-by: research sub-agent
Date: 2026-06-10
Trigger: notes/research_drill_translation_revival_3x_2026-06-10.md
Urgency: MEDIUM -- 5 engineering anchors for testing cross-lingual substrate mechanisms; cheapest (T2) requires no substrate modification and can run in 3 hours

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

### Anchor 1: action_verb_crosslingual_alignment_v1 (MOTORP-XLM)

Anchor pointer: Research note Section D2.4 + Test T2 + Stream A3 (Pulvermüller motor cortex); King & Janik 2013; Mikolov 2013 cross-lingual alignment.
Substrate-product reading: Uses XLM-R middle-layer representations (no substrate modification needed) to test whether action verbs (kick, grab, bite, walk, throw...) have systematically higher cross-lingual cosine similarity than matched abstract nouns (freedom, concept, obligation...) across EN, ZH, AR. This is the cheapest possible gate for the embodied-verb-grounding hypothesis. A HARD-PASS here confirms that motor-primitive grounding is detectable in cross-lingual embeddings, making EMBODIED-VERB-GROUNDING (D2.4) the first engineering priority. A HARD-FAIL does not refute the mechanism; it means the test path goes through explicit motor primitives rather than distributional proxies.
Tier hint: CPU-local laptop or runner. HuggingFace XLM-R inference only. No training. Estimated runtime: < 3 hours. $0.
Why-now: Cheapest gate across all 8 crazy-math proposals. Run this first before any substrate modification. Informs prioritization of D2.1 vs D2.4 as primary engineering path.

Pre-reg bands:
  HARD-PASS: action-verb mean cross-lingual cosine similarity > abstract-noun mean by > 0.15 cosine units across all 3 language pairs (EN-ZH, EN-AR, ZH-AR)
  MIDDLE-BAND: 0.05-0.15 gap (motor grounding partially detectable; needs more targeted test)
  HARD-FAIL: < 0.05 gap or reverse direction (motor grounding not detectable in distributional embeddings; pivot to explicit motor-primitive corpus approach for D2.4)

### Anchor 2: interlingua_fhrr_crosslingual_retrieval_v1 (INTERLINGUA-XL)

Anchor pointer: Research note Section D2.1 + Test T1 + Stream C6 (Conneau interlingua) + C10 (Wendler mechanistic interpretability).
Substrate-product reading: Trains separate Tier-3 codebooks on English and Chinese ConceptNet; constructs 100 matched concept-pair FHRR compositions (3-gram: concept-relation-concept); tests whether Chinese Tier-3 retrieval from English-composed vectors beats a random baseline by > 0.30 margin. This directly tests whether the FHRR space constitutes an implicit interlingua without any cross-lingual training signal. If HARD-PASS: the architecture of Tier-0 shared FHRR space is validated as a natural interlingua; D2.1 is the primary translation mechanism. If HARD-FAIL: cross-lingual training signal is required (parallel text); D2.8 becomes primary.
Tier hint: CPU-local. ConceptNet subset (N=10K concepts, EN + ZH). No GPU. Estimated runtime: < 2 hours once codebooks are trained. $0.
Why-now: The interlingua hypothesis is the most foundational of the 8 proposals. If FHRR naturally implements an interlingua, the entire translation architecture rests on a clean algebraic base. This test runs in parallel with Anchor 1.

Pre-reg bands:
  HARD-PASS: top-5 cross-lingual retrieval accuracy > 0.50 on 100 matched EN-ZH concept pairs
  MIDDLE-BAND: 0.25-0.50 (partial interlingua; semantic drift prevents clean mapping; need cross-lingual anchor concepts)
  HARD-FAIL: < 0.20 (FHRR space is NOT a natural interlingua; parallel-text training required; D2.1 alone insufficient)

### Anchor 3: whorfian_modulation_language_tag_v1 (WHORF-MOD)

Anchor pointer: Research note Section D2.6 + Test T3 + Stream A9 (Thierry et al. 2009 ERP; Winawer 2007 Russian color).
Substrate-product reading: Constructs a bilingual substrate with a language-tag modulation operator W_L applied to Tier-3 retrieval. Tests whether the modulation W_ZH vs W_EN produces systematically different retrieval near color category boundaries (mid-blue range: siniy/goluboy zone) while leaving clearly within-category colors unaffected. This tests whether the Whorfian modulation proposal (D2.6) is implementable and produces the Winawer/Thierry-predicted pattern. Requires language-tag substrate implementation -- non-trivial engineering.
Tier hint: CPU-local. Requires implementing W_L as a learned linear modulation on top of existing substrate. Estimated 1 day implementation + 1 hour inference. $0.
Why-now: Whorfian modulation is a unique substrate feature not present in any LLM (which cannot externally control language-mode modulation). If this works, it is a categorical product differentiator. Run after Anchors 1 and 2 have verdicts.

Pre-reg bands:
  HARD-PASS: boundary-region retrieval changes > 0.10 cosine units between EN-tag and ZH-tag; within-category queries stable (< 0.02 change)
  MIDDLE-BAND: some modulation but below 0.10 threshold
  HARD-FAIL: no modulation (language tag does not affect semantic retrieval; W_L collapses to identity; D2.6 requires different architecture)

### Anchor 4: grammar_operator_noncommutativity_v1 (GRAMMAR-ALG)

Anchor pointer: Research note Section D2.2 + Test T4 + Stream A5 (Slobin "thinking for speaking"); Talmy 2000 satellite/verb-framing.
Substrate-product reading: Implements 3 core grammar operators (TOPICALIZE, ASPECT, CASE) as linear maps on FHRR semantic representations. Tests non-commutativity: operator pairs that should produce different outputs when applied in different orders are tested for output distinctness. Commuting pairs (two independent case-role assignments) are tested for output equivalence. This validates whether the grammatical packaging algebra (D2.2) captures the basic structural property required for grammatically-distinct outputs across language families.
Tier hint: CPU-local. Requires implementing 3 grammar operators from scratch. Estimated 2 days implementation + 30 min inference. $0.
Why-now: The grammar operator algebra is required for any cross-lingual substrate translation pipeline beyond lexical lookup. Without non-commutative operators, word order differences between languages cannot be captured. This is the enabling architecture for the full translation pipeline.

Pre-reg bands:
  HARD-PASS: > 85% of non-commuting operator pairs produce distinct FHRR output (> 0.10 cosine distance); commuting pairs produce near-identical output (< 0.05 cosine distance)
  MIDDLE-BAND: 65-85% distinctness for non-commuting pairs (operators are partially but not consistently non-commutative)
  HARD-FAIL: < 60% distinctness (grammar operators are effectively commutative; linear map representation collapses grammatical distinctions; need tensor/bilinear operators instead)

### Anchor 5: bilingual_dual_substrate_tier0_sharing_v1 (DUAL-SUB)

Anchor pointer: Research note Section D2.8 + Test T5 + Stream A1 (Abutalebi-Green) + A2 (Patterson-Lambon Ralph hub-and-spoke).
Substrate-product reading: Trains a dual-substrate on parallel EN-ZH sentence pairs (100K from OPUS corpus). Tests whether mode-free Tier-0 queries retrieve the same top concept as language-specific EN-mode and ZH-mode queries in > 70% of cases. This directly tests the biological claim that the ATL hub (Tier 0) is shared between L1 and L2 while Tier-3 spokes are language-specific. If HARD-PASS: the hub-and-spoke architecture is empirically validated for the substrate; D2.8 is confirmed as the primary bilingual substrate architecture. This is the most computationally expensive anchor in this set (requires parallel-text training) but is the most foundational for the translation product claim.
Tier hint: CPU-local is feasible at N=1024, 100K pairs but slow (12-24 hours). GPU (runner) preferred if available. Check remote runner state before dispatching.
Why-now: This is the most biologically-grounded test (hub-and-spoke has the most neuroscientific validation). Dispatch after Anchors 1-3 have verdicts; use their findings to set the Tier-0 dimensionality and codebook design for this anchor.

Pre-reg bands:
  HARD-PASS: mode-free Tier-0 query matches EN-mode top-1 in > 70% of cases AND ZH-mode top-1 in > 70% of cases; language-mode residuals (W_L component) account for < 30% of total retrieval variance
  MIDDLE-BAND: 50-70% match (Tier 0 partially shared; language-specific drift is significant; need larger D_0 or more parallel data)
  HARD-FAIL: < 40% match for either language (Tier 0 is NOT shared; dual-substrate is actually two independent substrates; D2.8 collapses; requires fundamental architecture change)

---

## Context pointers

- Research note (primary): d:/AI/hd-instrument/notes/research_drill_translation_revival_3x_2026-06-10.md
- Prior universals drill (cross-thread): d:/AI/hd-instrument/notes/research_drill_tier1_universals_cross_language_2x_2026-06-10.md
- Prior universals exp_dev handoff: d:/AI/hd-instrument/notes/exp_dev_handoff_research_tier1_universals_cross_language_2x_2026-06-10.md
- Compositional cliff crossed (memory): d:/AI/hd-instrument/memory/substrate_v3_compositional_cliff_crossed.md
- NORTH STAR: d:/AI/hd-instrument/memory/north_star_functional_system_beats_LLMs.md
- Active priorities: d:/AI/hd-instrument/notes/active_priorities.md

---

## Contract

exp_dev owns:
- Anchor prioritization within this file (may reorder based on queue depth + runner availability)
- Experiment design details: ConceptNet/OPUS subset selection, XLM-R layer selection, script structure
- Pre-reg envelope refinement from the bands above
- Go/no-go decision per pause gate

Research sub-agent provided:
- Ranked anchor candidates with substrate-product readings
- Pre-reg band proposals (NOT final -- exp_dev calibrates from cap_map context)
- Context pointers (file paths, not summaries)
- Key literature citations (in research note) for any anchor that needs design justification

---

## Autonomy declaration

exp_dev may dispatch Anchor 1 (MOTORP-XLM) and Anchor 2 (INTERLINGUA-XL) immediately in parallel if (a) pause gate is clear and (b) runner has CPU capacity. Both are CPU-local, $0, no substrate modification needed.

Anchor 3 (WHORF-MOD) requires implementing language-tag modulation; dispatch after Anchors 1-2 complete and their verdicts inform the design.

Anchor 4 (GRAMMAR-ALG) requires implementing 3 grammar operators; can run in parallel with Anchor 3 after Anchors 1-2.

Anchor 5 (DUAL-SUB) is the most expensive; dispatch last, using Anchors 1-4 verdicts to set architecture parameters.

No authorization needed for CPU-local anchors under the standing experiment authorization. GPU dispatch for Anchor 5 requires normal queue routing.
