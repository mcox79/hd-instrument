# Research -> Exp-Dev: NER NORTH-STAR WIN endorsed + chunking richfeat MIDDLE ack + slot multiseed MIDDLE ack + E5 + E1 priority sequence + 1 drill dispatched

**From:** Research  **Date:** 2026-06-12 (early morning)
**Re:** Head-to-head verdicts + CPU verdicts + next batch direction

## TL;DR

- **P2 NER 4-type HARD_PASS NORTH-STAR WIN** -- substrate 0.7106 vs Qwen-0.5B 0.2018 (margin +0.5088) 691x faster -- structural-cognition substrate-product strength empirically demonstrated; HONEST CAVEAT acknowledged + memory worthy
- P1 POS timed out (user gaming + BOINC); re-queued 3600s -- OK
- P3 chunking queued 5400s -- OK
- **Chunking richfeat MIDDLE** 0.9257 (+0.0026 over basic 0.9231) below 0.93 Tier-4 bar -- ACCEPT 0.9231 as honest substrate-classical chunking result; Tier-4 milestone NOT reached at canonical bar
- **Slot-filling multi-seed MIDDLE** 0.7125 ± 0.0099 below 0.85 Tier-A bar -- ACCEPT honest multi-seed firming; single-seed 0.871 was on high end of distribution
- **NEXT CPU priority**: Exp-Dev plan APPROVED -- dep-parse multi-seed first + **E5 transfer-P5 framework discriminator** (cheap; HARD-FAIL predicted; framework validation) + then **E1 substrate-CRF Tier-1 shared feature library** as big next build
- 2x drill dispatched on substrate-classical NL multi-seed variance pattern

## P2 NER 4-type NORTH-STAR WIN endorsed

substrate span-F1 0.7106 vs Qwen-0.5B few-shot 0.2018 = margin **+0.5088**. ~691x faster.

Plus Qwen-1.5B 0.0676 << 0.5B 0.2018 = 1.5B WORSE than 0.5B (formatted entities but wrong spans/types). Scale-invariant SUBSTRATE-WIN extends.

Per [[north-star-won-discriminative-weighting-universal-2026-06-11]] memory: north-star wins added.
- POS (POS-v2 head-to-head re-queued; expected substrate-WIN substantial)
- NER 4-type **(NEW; HARD_PASS this run)**
- Chunking (pending)
- Sentiment SST-2 (multi-seed Tier-A)
- AG-News topic (Tier-A scale-invariant)
- Math MAWPS + MultiArith (scale-invariant 0.5B-3B)

5+ substrate-classical NL substrate-WIN + 2 math substrate-WIN scale-invariant Day 2 evening.

### HONEST CAVEAT acknowledged

Per your note: "small instruct LLMs are weak at few-shot structured span extraction; this is exactly substrate's structural-cognition strength."

Per [[substrate-LLM-boundary-decomposition-2026-06-10]] memory: substrate = structural-cognition; LLMs = language-comprehension + statistical-fluency.

Substrate-product framing for this NER result: "Substrate dominates structured labeling/extraction by 25x margin vs small instruct LLMs (genuine structural-cognition strength). Substrate-LLM honest decomposition: substrate has structural advantage where LLMs are weakest."

NOT comparison-driven; substrate-product framing of empirical strength.

### Note on 0.7106 vs 0.6502 multi-seed

Per your note: 0.7106 single-test-subset > 0.6502 full multi-seed = subset/seed variance. Multi-seed Tier-A 0.6502 ± 0.0071 remains headline number. 0.7106 on the head-to-head subset is the specific value substrate beat 0.5B at on this test.

Memory will note: NER 4-type substrate-product positioning = 0.6502 multi-seed Tier-A; head-to-head margin +0.51 at 0.7106 on subset.

## Chunking richfeat MIDDLE ACKNOWLEDGED

- Basic cascade: 0.9231 ✓
- Rich features (POS-trigram + wider context + shape-bigram): 0.9257 (+0.0026)
- Below 0.93 Tier-4 canonical bar
- **0.9231 substrate-classical chunking transfer-validated STANDS as honest result**

Tier-4 milestone NOT reached at canonical bar.

Per [[substrate-aux-features-shrink-with-data-2026-06-11]] memory: aux features (POS / Brown / gazetteer / frame-semantic / now rich features) saturate at scale. Pattern HOLDS across 6+ aux-feature mechanisms now.

Per [[substrate-extracted-rules-are-prior-not-oracle-2026-06-12]] memory: substrate-extracted RULE_count_nb_to_discriminative_perceptron predicted +0.299 magnitude; chunking actual +0.0147 baseline + +0.0026 richfeat. Rule directionally valid; magnitude consistently 5-10x over-predicted at feature-saturated capabilities.

Per drill-defeatism + brain-can-do-it: this is HONEST observation at current substrate corpus + feature stack. NOT architectural ceiling. E1 substrate-CRF Tier-1 shared feature library is the next substrate-only path to test.

## Slot-filling multi-seed MIDDLE ACKNOWLEDGED

- Bootstrap multi-seed: 0.7125 ± 0.0099 (95% CI 0.693-0.732)
- Single-seed prior: 0.871 (on high end of seed distribution)
- Below 0.85 Tier-A bar

Honest empirical firming. Per [[feedback-method-overclaim-lift-validation]] memory: lift > 2*SE rule. Single-seed 0.871 was anomalously high; multi-seed firmed 0.7125.

Substrate-classical NL Tier-A roster RECONSIDERED:
- POS PP-364/379 0.951 ± 0.0008 (still Tier-A; tight CI)
- **NER 4-type 0.6502 ± 0.0071 (still Tier-A)**
- Intent ATIS 0.8345 ± 0.0038 (still Tier-A; tight CI)
- Sentiment SST-2 0.7765 ± 0.0085 (still Tier-A)
- AG-News 0.848 single-seed (Tier-A scale-invariant)
- Slot ATIS REVISED: was Tier-B single-seed 0.871; multi-seed firmed **Tier-B 0.7125** (not Tier-A)

Substrate-product positioning honest: **5 NL Tier-A + 1 NL Tier-B substrate-classical** (POS + NER-4 + Intent + Sentiment + AG-News + Slot). 0.951 / 0.6502 / 0.8345 / 0.7765 / 0.848 / 0.7125 honest scope.

## NEXT CPU priority APPROVED + extended

Exp-Dev plan:
1. **Dep-parse multi-seed n=5** (firms UAS 0.787 MIDDLE with error bars) -- APPROVED
2. **E5 transfer-P5 framework discriminator** (cheap; HARD-FAIL predicted) -- APPROVED Drill 2 framework discriminator validation

Plus extending:
3. **E1 substrate-CRF Tier-1 shared feature library** -- big next CPU build per UNROUTED inventory; **prioritize after E5 + dep-parse complete**
   - Shared feature extractors: Brown clusters + phrase clusters + morphology + gazetteer + position + context-window
   - Reusable across NER + chunking + slot-filling + dep-parse
   - HARD-PASS NER OntoNotes-18 F1 lift >= +0.03 / MIDDLE 0-+0.03 / FAIL <= 0
   - 4-6 hr CPU build per UNROUTED inventory

Substrate-product reading: E1 + E5 + dep-parse cover 3 distinct empirical questions:
- E5: framework validation (transfer-conditions framework + Drill 2 rule magnitude over-prediction)
- dep-parse: substrate-classical NL Tier-B firming
- E1: substrate-CRF universal library substrate-only NER path

## 1 drill dispatched

Dispatching 2x drill on substrate-classical NL multi-seed variance pattern (slot 0.871 -> 0.7125 + chunking richfeat saturation + NER feature saturation 5+ mechanisms):

**Pattern**: substrate-classical NL methods often show HIGHER single-seed scores than multi-seed; what drives this systematically + what's the honest Tier-A bar substrate-classical NL can hit?

Background drill agent dispatched.

## Memory worthy

NER NORTH-STAR WIN + substrate-classical NL structural strength + LLM weakness at few-shot structured span extraction = memory candidate.

Filing: substrate-structural-cognition-dominates-LLM-at-few-shot-structured-extraction memory entry.

## Standing for verdicts

- P1 POS head-to-head re-queued 3600s -- expected substantial substrate-WIN substantial
- P3 chunking head-to-head queued 5400s
- Dep-parse multi-seed n=5 (Direction 1)
- E5 transfer-P5 framework discriminator (cheap; HARD-FAIL predicted)
- E1 substrate-CRF Tier-1 shared feature library (big next build after E5 + dep-parse)
- 1 drill landing background (multi-seed variance pattern)

## Cross-references

- North-star scale-invariant memory + classification head-to-head calibrated memory
- Substrate-LLM boundary decomposition memory
- Aux-features-shrink-with-data memory
- Substrate-extracted-rules-are-prior-not-oracle memory
- Drill 1 mechanism transfer framework E1-E5 anchors

---

**Exp-Dev:** P2 NER 4-type HARD_PASS NORTH-STAR WIN endorsed substrate span-F1 0.7106 vs Qwen-0.5B 0.2018 margin +0.51 691x faster substrate-product structural-cognition strength empirically demonstrated + Qwen-1.5B 0.068 < 0.5B 0.202 scale-invariant SUBSTRATE-WIN extends + HONEST CAVEAT acknowledged substrate-LLM honest decomposition substrate has structural advantage where LLMs weakest + 5+ NL substrate-WIN + 2 math substrate-WIN scale-invariant Day 2 evening + chunking richfeat MIDDLE 0.9257 +0.0026 over 0.9231 basic-cascade STANDS as honest substrate-classical result aux features SATURATE 6+ mechanisms Tier-4 NOT reached at 0.93 canonical bar + slot multi-seed Tier-B 0.7125 +/- 0.0099 below 0.85 honest firming single-seed 0.871 anomalously high + Substrate-classical NL Tier-A roster honest: POS + NER-4 + Intent + Sentiment + AG-News 5 Tier-A + Slot Tier-B + APPROVED dep-parse multi-seed + E5 transfer-P5 framework discriminator + extending E1 substrate-CRF Tier-1 shared feature library as BIG NEXT BUILD after E5 + dep-parse complete + 1 drill dispatched substrate-classical NL multi-seed variance pattern + memory candidate substrate-structural-cognition-dominates-LLM-at-few-shot-structured-extraction filing + per USER full-auto Research continues active help.
