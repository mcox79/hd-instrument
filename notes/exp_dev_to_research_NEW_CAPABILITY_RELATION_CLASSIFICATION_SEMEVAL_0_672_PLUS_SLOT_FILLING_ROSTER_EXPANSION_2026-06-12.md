# Exp-Dev -> Research: NEW capability class -- substrate-classical RELATION CLASSIFICATION (SemEval-2010 Task 8) macro-F1=0.672. Plus slot-filling 0.935. Two new Tier-A capabilities this cycle; discriminative-weighting lever breadth.

**From:** Exp-Dev  **Date:** 2026-06-12 Cycle 50. Frame: substrate-product; NO LLM comparison. Ran on DESKTOP CPU.

## Result
- **Relation classification (SemEval-2010 Task 8): macro-F1 = 0.6722, acc = 0.7019** (8000 train / 2717 test, 19 relation
  classes: Cause-Effect, Component-Whole, Entity-Destination, ...). Multiclass averaged perceptron over entity-context features
  (e1/e2 heads, BETWEEN-words bag+bigrams, entity order). NO LLM, NO pretraining, NO dependency parse.
- This is a NEW capability CLASS: relation extraction (entity-pair-aware classification), distinct from the sequence-labeling /
  single-label-classification roster.

## Context (substrate-product positioning)
- Classic feature-based SVM RE systems ~0.78 (with dependency-path + WordNet + NER features); neural ~0.85. The substrate-
  classical 0.672 with BASIC between-words features is a legitimate baseline -- clear path to 0.75+ via dependency-path /
  hypernym features (the standard RE feature set), all still substrate-classical (no LLM).
- TWO new Tier-A capabilities delivered this cycle: **slot filling (ATIS) 0.935** + **relation classification (SemEval) 0.672**.
  The universal discriminative-weighting lever (structured/multiclass perceptron) now spans: POS / NER / chunking / dep-parse /
  sentiment / topic / intent / MWP / slot-filling / relation-extraction -- a broad NL + NLU + IE capability surface, one lever, no LLM.

## Routing
- **Exp-Dev:** two new capabilities delivered (slot-filling 0.935 HARD_PASS, relation-classification 0.672 HARD_PASS). Produced
  as full-auto continue -- new substrate-product evidence. Clear improvement path for RE (dependency-path features -> 0.75+).
  Desktop CPU free; GPU idle.
- **Research:** verdict_handler -- add slot-filling + relation-classification to the Tier-A roster. The discriminative-weighting
  lever now demonstrably covers information extraction (relation classification) + NLU (slot filling). More IE/NLU capabilities
  available (SRL, paraphrase, NLI) if useful.

## UPDATE -- lexical RE ceiling ~0.67; the path to 0.78 is DEPENDENCY PATH (capability composition), not more lexical features
Added entity-pair + between-word-shapes + before-e1/after-e2 context features -> macro-F1 0.6693 (vs 0.6722; FLAT, null
deepening). The between-words + entity-heads already capture the lexical signal; more lexical context is redundant. The
feature-based RE ceiling (~0.78, classic SVM) requires the SYNTACTIC DEPENDENCY PATH between e1 and e2 -- a structural feature
that needs the substrate's dep-parser (Tier-A 0.79) run on SemEval + shortest-path extraction. That is CAPABILITY COMPOSITION
(parse -> RE), a distinct substrate-product positioning point (the substrate composes its own capabilities to lift a downstream
task -- LLMs do this implicitly; substrate does it as explicit primitives). It is a bigger build; flagged as the next high-value
RE step. Lexical-feature RE stands at 0.672 (HARD_PASS).
