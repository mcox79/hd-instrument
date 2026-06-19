# Research -> Exp-Dev: L-B REROUTE per substrate-quality-first -- CANCEL LLM-0.5B-FT crossover + substitute substrate-only mechanism deepening (CRF transition + char-CNN + gazetteer ablations) + L-A Adversarial NER LLM reference frame OPTIONAL

**From:** Research  **Date:** 2026-06-12 (Day 4 morning)
**Re:** L-B follow-on reroute -- USER caught LLM-comparison drift; substrate-quality-first re-baseline

## TL;DR

- **USER caught drift**: my prior L-B routing approved LLM-0.5B-FT crossover as "decisive substrate-product positioning" -- that's the LLM-comparison frame methodology rule 7 says to avoid
- **CANCEL LLM-FT crossover GPU cell** -- not needed; L-B curve stands alone as substrate-product positioning artifact
- **SUBSTITUTE substrate-only mechanism deepening** -- 3 ablations at 5pct/10pct data: CRF transition features + char-CNN embedding + gazetteer feature contribution
- **L-A Adversarial NER**: KEEP; LLM reference frame OPTIONAL (can drop if you prefer pure substrate-classical robustness curve)
- **Substrate-product positioning frame**: substrate IS structured cognitive architecture with measurable mechanism + provenance + composability; NOT defined as "the thing that beats / loses to LLM at task X"

## USER pushback (verbatim intent)

"why are we still doing comparisons to LLMs?"

Frame check:
- Methodology rule 7 (memory file: methodology_rule_7_substrate_quality_first): substrate-quality-first not LLM-comparison
- I drifted on L-B follow-on by framing it as "decisive substrate beats LLM-0.5B at low-data crossover"
- USER right to push back. The L-B curve at 0.40 at 5pct data + 63pct relative-to-full IS the substrate-product positioning artifact. LLM-FT comparison adds a relative number that doesn't change substrate truth and reinforces the wrong frame.

## What the L-B finding actually IS

| fraction | substrate NER F1 |
|---|---|
| 1pct | 0.203 |
| 5pct | 0.404 |
| 10pct | 0.501 |
| 50pct | 0.571 |
| 100pct | 0.644 |

This curve IS the substrate-product positioning. Factual claims it supports:
- "Substrate-classical NER usable at 5-10 pct labeled data without pretraining (0.40-0.50 span-F1)"
- "63 pct of full-data F1 at 5 pct data" (steep early curve = low-data architectural fit)
- "Diminishing returns above 10 pct data (per substrate-aux-features-shrink-with-data memory)"
- "Substrate-classical mechanism has architectural advantage in low-data regime via shared-feature-library + structured prediction inductive bias"

These claims are substrate-property claims. No LLM reference frame needed.

## Substrate-only mechanism deepening (substitute for LLM-FT crossover)

Three ablations at 5pct + 10pct + 100pct data fractions (CPU; estimated ~2-3 hr total):

### Ablation 1: CRF transition features
- Current: structured perceptron with memoryless emissions (each token tagged independently given features)
- Test: add learned BIO->BIO transition features (CRF-style transitions)
- Hypothesis: transition features lift low-data regime (5pct +0.05-0.10) by constraining BIO consistency
- Pre-reg: HP CRF transition F1 at 5pct >= 0.45 (+0.05 over current 0.40)
- Architectural question: does substrate-classical structured perceptron approach saturation under CRF transitions at low-data?

### Ablation 2: Char-CNN embedding
- Current: word + char-shape + prefix/suffix features
- Test: add char-CNN window-3 + window-5 embeddings (dim 32 each)
- Hypothesis: char-CNN captures sub-word morphology bge can't reach with shape features alone
- Pre-reg: HP char-CNN F1 at 5pct >= 0.43 (+0.03 over baseline)
- Architectural question: substrate-product capacity for low-data morphological generalization via mechanism extension

### Ablation 3: Gazetteer feature ablation
- Current: no gazetteer features
- Test: add binary gazetteer features (token in person-names / location-names / org-names lists)
- Hypothesis: gazetteer helps STRONGLY at 1pct/5pct data (high-precision feature), saturates at 100pct
- Pre-reg: HP gazetteer F1 at 5pct >= 0.50 (+0.10 over baseline); flat at 100pct (current 0.644 unchanged)
- Architectural question: substrate-product low-data win via discrete feature library

### Combined ablation (optional, after individual)
- All 3 added: CRF + char-CNN + gazetteer
- Pre-reg: HP combined F1 at 5pct >= 0.55 (HARD-PASS bar from original L-B)

## L-A Adversarial NER frame

Per language drill REC-A: substrate Tier-A NER under char/word/sentence perturbations.

KEEP, but reframe:
- PRIMARY: substrate-classical NER robustness curve at perturbation levels 0pct / 10pct / 25pct / 50pct
- OPTIONAL: LLM-0.5B reference frame (drops without loss of substrate-product positioning artifact)

Substrate-product claim from L-A: "Substrate-classical NER F1 degrades by X at 25pct perturbation -- adversarial-robustness intrinsic property of structured prediction + Viterbi decoding."

LLM comparison would add: "LLM-0.5B-FT degrades by Y at 25pct perturbation" -- doesn't change substrate truth; OPTIONAL.

Exp-Dev call: keep LLM reference or drop. Either way substrate-product positioning artifact preserved.

## Methodology rule clarification (for future reference)

methodology-rule-7 (substrate-quality-first):
- Substrate is defined by INTRINSIC capability + mechanism + provenance + composability
- NOT defined as "the thing that compares favorably/unfavorably to LLM"
- LLM comparisons are SECONDARY reference frames, never PRIMARY substrate-product positioning
- When a measurement is approved, ask: would this experiment still produce a substrate-product positioning artifact if the LLM comparison cell were dropped entirely? If YES -> proceed substrate-only. If NO -> reframe.

For L-B: substrate curve alone IS the artifact. Drop LLM comparison.

For L-A: substrate robustness curve alone IS the artifact. LLM comparison optional.

For HYBRID semantic_v2: substrate's algebra HRR + bge cosine partition coverage IS the artifact. No LLM reference frame needed.

## Routing

**Exp-Dev**:
- CANCEL L-B LLM-0.5B-FT crossover GPU cell
- ADD L-B substrate-only mechanism deepening (3 ablations CPU ~2-3 hr; pre-reg above)
- KEEP L-A Adversarial NER GPU substrate-classical robustness curve; LLM reference frame OPTIONAL Exp-Dev call
- Cell 2 PP-394 ASDiv-WK multi-seed CPU continues
- C-D4 + C-D5 after Testbed breadth ingest

**Research**:
- This re-route (substrate-quality-first re-baseline)
- Standing for L-B mechanism deepening + L-A measurements
- 2x DEEP drill on substrate-only low-data NER architecture (was already configured around substrate-classical; remains valid + informs ablation design)

## Cross-references

- research_to_exp_dev_LB_NER_MIDDLE_ACK_LLM_05B_FT_CROSSOVER_FOLLOWON_GPU_LA_ALSO_QUEUE_2026-06-12.md (PRIOR routing -- LLM comparison frame SUPERSEDED by this note)
- exp_dev_to_research_LB_SUBSTRATE_NER_FEWSHOT_CURVE_MIDDLE_63PCT_AT_5PCT_DATA_2026-06-12.md (Exp-Dev L-B verdict)
- methodology_rule_7 memory (substrate-quality-first frame)

---

**Exp-Dev:** L-B REROUTE per USER pushback substrate-quality-first methodology rule 7 + CANCEL LLM-0.5B-FT crossover GPU cell L-B curve alone IS substrate-product positioning artifact + SUBSTITUTE substrate-only mechanism deepening 3 ablations CPU ~2-3 hr CRF transition features pre-reg HP F1 5pct >=0.45 + char-CNN window 3+5 dim 32 pre-reg HP F1 5pct >=0.43 + gazetteer features person/location/org pre-reg HP F1 5pct >=0.50 + combined ablation pre-reg HP F1 5pct >=0.55 + L-A Adversarial NER KEEP substrate-classical robustness curve PRIMARY LLM reference frame OPTIONAL Exp-Dev call + methodology rule 7 future clarification substrate-product positioning artifact must stand alone if LLM comparison dropped + USER full-auto continuing.
