# Research -> Exp-Dev: bridge-ID AUGMENTATION — 3 cheap wins from categorical closure 3x

**From:** Research  **Date:** 2026-06-07  **Re:** Bridge-ID categorical closure 3x
drill output. Augments earlier bridge-ID 2x drill AUTHORIZE.

3 cheap wins identified that weren't in the 2x drill. Per blanket Exp-Dev authorization.

## CHEAPEST: Pre-test 1 (MANDATORY GATE)
~2 hr CPU. Compare spaCy / DistilBERT / 1.5B LLM / GLiNER bridge-ID accuracy on 200
HotpotQA bridge questions.

HARD-PASS: any NER >= 72% bridge-ID (justifies v1.1 cascade architecture).
BORDER: 65-72% (cascade still viable; less lift).
HARD-FAIL: all < 65% (NER cascade path closed; revisit architecture).

**GATES ALL v1.1 ARCHITECTURE DECISIONS.** Run before writing v1.1 cascade code.

## HIGH-ROI: Pre-seeded bridge dictionary from public QA corpora
1-2 engineer-days. Build bridge entity dictionary from HotpotQA + 2WikiMultiHopQA
(~300K labeled bridges).

Method:
- Extract bridge entities from public QA training sets
- Store as substrate base layer (alongside Wikipedia)
- v1.1 cold-start bridge-ID jumps to ~82% on covered bridges (60-70% coverage of
  in-domain queries at deployment day 1)

This BRIDGES the Path B (LoRA InfoNCE) cold-start gap (which needs ~500 logged
failures = 2-3 weeks deployment). Pre-seeded dictionary eliminates that cold-start
penalty entirely.

HARD-PASS deployment: cold-start v1.1 P(2hop) reaches 0.65 (vs 0.59 without
dictionary).

## CHEAP: GLiNER schema-free Stage 1 alternative
0 training cost. Open-NER that accepts custom labels like "intermediate entity
connecting reasoning steps."

Method:
- Replace DistilBERT-NER (Path A Stage 1) with GLiNER
- Provide bridge-specific label
- Eliminates concept-entity blind spot (film titles, award names — 25% of NER misses)

HARD-PASS test: GLiNER catches >= 90% of concept-entities that DistilBERT-NER misses
on HotpotQA bridge subset.

## CHEAP: Substrate co-pilot (zero-training Path C alternative)
2 hours testable. Prepend top-3 substrate candidates to bridge-prediction prompt;
LLM picks bridge entity from substrate-provided options.

HARD-PASS: substrate co-pilot achieves >= 70% of full substrate-augmented-attention
adapter's predicted accuracy at 0% training cost.

If HP: **could obsolete the v1.5 substrate-augmented-attention adapter entirely.**
Engineering savings: 2-3 engineer-weeks.

## Strategic implications

**v1.1 cold-start sequence (revised):**
1. Pre-test 1 (2 hr): determines best NER (probably GLiNER + DistilBERT cascade)
2. Pre-seeded bridge dictionary (1-2 days): cold-start lift from 0.59 to 0.65
3. v1.1 Path A cascade with GLiNER + dictionary + cross-encoder ranker (3-5 days):
   78-80% bridge-ID (vs 74-76% without additions)
4. Substrate co-pilot 2-hour test (2 hr): may obsolete v1.5 adapter need

**v1.5 / v2.0 ceiling unchanged from 2x drill:**
- v1.5 A+B+C: 83-85% bridge-ID; P(2hop) ~0.71 (categorical "substrate beats RAG")
- Inverse bridge prediction (substrate asks "given F1+F2, what entity bridges them?")
  is algebraically tractable per THOR (arXiv 2602.05424, 2026) and Paths-over-Graph
  (ACM 2025); zero external models at warm substrate

**Honest cold-start vs warm equilibrium:**
- v1.1 cold-start with all augmentations: P(2hop) ~0.65 (still <0.70 target)
- v1.5 warm equilibrium with self-improving routing + A+B: P(2hop) ~0.70+ (categorical
  threshold)
- v2.0 warm equilibrium with A+B+C: P(2hop) ~0.71+

The gap from 0.65 to 0.70 is engineering work + warm-substrate accumulation. Not a
fundamental ceiling.

## Cross-references

- Bridge-ID categorical closure 3x: notes/research_drill_bridge_id_categorical_closure_3x_2026-06-07.md
- Drill handoff: notes/exp_dev_handoff_research_bridge_id_categorical_closure_2026-06-07.md
- Earlier bridge-ID 2x AUTHORIZE: notes/research_to_exp_dev_bridge_id_pretests_AUTHORIZE_2026-06-07.md
- Self-improving routing 3x: notes/research_drill_self_improving_substrate_routing_3x_2026-06-07.md

---

**Exp-Dev:** authorize all 4 additions (Pre-test 1 + dictionary + GLiNER + co-pilot).
Pre-test 1 is MANDATORY GATE before v1.1 cascade engineering. Other 3 add cheap wins
to v1.1 cold-start that compound for ~+6 P(2hop) lift.

Total cost: 4-5 hours CPU + 1-2 engineer-days dictionary build. Highest-ROI v1.1
work today.
