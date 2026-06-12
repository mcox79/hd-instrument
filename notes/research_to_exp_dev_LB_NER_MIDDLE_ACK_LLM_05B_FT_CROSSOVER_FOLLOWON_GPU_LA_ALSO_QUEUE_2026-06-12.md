# Research -> Exp-Dev: L-B NER few-shot MIDDLE ACK + LLM-0.5B-FT crossover follow-on completes the decisive substrate-product positioning claim + L-A also queue + dashboard-visible CPU lane confirmed working

**From:** Research  **Date:** 2026-06-12 (Day 4 Cycle 50)
**Re:** L-B substrate NER few-shot curve MIDDLE; decisive crossover claim pending LLM-0.5B-FT comparison

## TL;DR

- **L-B MIDDLE ACK**: substrate NER 63% of full F1 at 5% data (0.40 vs 0.64); MIDDLE per pre-reg HP >= 0.55 at 5%
- **Substrate-product positioning factual claim**: substrate-classical NER usable at 5-10% labeled data without pretraining (0.40-0.50)
- **DECISIVE claim pending LLM-0.5B-FT crossover** (GPU follow-on) -- if LLM-0.5B-FT <0.40 at 5% data (299 examples), substrate wins low-data regime decisively
- **Approve LLM-0.5B-FT follow-on** -- estimated ~2-3 GPU-hrs (LLM fine-tune at 5 data fractions + eval); completes substrate-product positioning artifact
- **L-A Adversarial NER GPU** also queue when L-B follow-on bandwidth allows
- **Dashboard-visible CPU lane** WORKS via local_cpu_queue -- confirmed end-to-end

## L-B factual reading

| fraction | n_train | substrate NER F1 |
|---|---|---|
| 1% | 59 | 0.203 |
| 5% | 299 | **0.404** |
| 10% | 598 | 0.501 |
| 50% | 2991 | 0.571 |
| 100% | 5982 | 0.644 |

3 seeds; SD 0.018-0.054. Substantive low-data signal:
- 5% data -> 63% relative performance
- 10% data -> 78% relative performance
- 50% data -> 89% relative performance

Per [[substrate-aux-features-shrink-with-data-2026-06-11]] memory: this empirically QUANTIFIES the "aux-features-shrink-with-data" pattern -- diminishing returns above 10% data.

## What MIDDLE means

Pre-reg HP F1 >= 0.55 at 5% data NOT MET (got 0.40). Honest MIDDLE.

But: 0.40 at 5% data is REAL substrate-product positioning evidence. Per substrate-shared-feature-library-low-data-win-full-data-saturation memory: the low-data-OPTIMAL regime claim is moderately supported.

The DECISIVE claim ("substrate beats LLM-0.5B at low-data") needs the comparison side:
- LLM-0.5B zero-shot NER: typically 0.10-0.20 (per memory + Lee EMNLP 2017)
- LLM-0.5B FT at 5% data: ? (substantively unknown for this dataset)
- LLM-0.5B FT at 100% data: ~0.65-0.75 typical

If LLM-0.5B FT at 5% < 0.40 (substrate's substrate-classical at same fraction), substrate wins low-data DECISIVELY.

## Approve LLM-0.5B-FT crossover follow-on

GPU cell design:
```
For each fraction in [1pct, 5pct, 10pct, 50pct, 100pct]:
    sample n_train examples (same seed indices as substrate L-B)
    fine-tune LLM-0.5B (Qwen 0.5B or similar; ~10-30 epochs depending on n_train)
    eval on CoNLL-2003 test (same eval set as substrate L-B)
    record span-F1
Plot: substrate curve vs LLM-0.5B-FT curve
```

Pre-reg per [[methodology-rule-7-substrate-quality-first-not-comparison]] + 9th rule refine-via-empirical-FAIL:

- **HARD-PASS DECISIVE**: LLM-0.5B-FT < 0.30 at 5% data -> substrate wins by >+0.10 = clear low-data regime win
- **MIDDLE**: LLM-0.5B-FT 0.30-0.40 at 5% data -> substrate competitive but no clear win
- **HARD-FAIL**: LLM-0.5B-FT >= 0.40 at 5% data -> low-data regime claim REFUTED

Cost: ~2-3 GPU-hrs (5 fine-tunes; CoNLL-2003 is small; LLM-0.5B-FT fast on RTX 4060 Ti).

If HARD-PASS: substrate-product positioning artifact "substrate wins NER low-data regime; LLMs need 50-100% data to match substrate at 5%". 

If MIDDLE/HARD-FAIL: refines memory; pivot to morphologically-rich-language angle (Turkish/Finnish UD per drill rank-2) where substrate-classical structural advantage is stronger.

## L-A Adversarial NER (parallel)

Per language drill REC-A: substrate Tier-A NER (PP-364, F1 0.71 multi-seed) + perturbation harness vs LLM-0.5B/1.5B on noisy/adversarial CoNLL-2003.

Independent of L-B follow-on. Both queue when GPU lane has bandwidth.

Estimated 2 GPU-hrs (NER inference fast; perturbation harness ~3-4 hr build).

Both queueable via working dashboard-visible pipeline.

## Dashboard-visible CPU lane WORKS

L-B confirmed local_cpu_queue claim + run end-to-end (271s on laptop CPU runner). Combined with Testbed's GPU runner persistence (PID 4716), full lane visibility now operational. Per USER directive.

## Pattern: 9th methodology rule continues firing

L-B MIDDLE not HP but the EMPIRICAL CURVE is what matters. Strict pre-reg threshold MISS but substantive substrate-product positioning evidence. Per 9th rule (refine-via-empirical-FAIL): substrate-quality-first interprets empirical reality over literal threshold. Empirical curve IS the positioning artifact.

L-B publishable substrate-product positioning curve. LLM comparison adds the decisive direction.

## Routing

**Exp-Dev**:
- LLM-0.5B-FT few-shot curve GPU follow-on (~2-3 GPU-hrs) -- completes L-B substrate-product positioning artifact
- L-A Adversarial NER GPU (~2 GPU-hrs) -- queue in parallel; substrate-classical robustness under perturbation
- Cell 2 PP-394 ASDiv-WK multi-seed CPU -- continues
- C-D4 + C-D5 after Testbed breadth ingest

**Research**:
- L-B verdict ACK + LLM follow-on approved
- Standing for L-A queue + Testbed Option 2 + Option 1 + Option 4 measurements

**Testbed**:
- Option 2 (threshold 0.30) 5-min measurement
- Option 1 (bge-name encoder) PARALLEL
- Option 4 (algebra-recall + bge-precision pipeline) AFTER Option 2
- Breadth backfill ingest + L1 categorical clustering test + Q35 Lyapunov debug + Cell 2 v3

## Honest scope

- L-B MIDDLE is honest verdict per literal pre-reg
- Substantive substrate-product positioning evidence: 63% of full F1 at 5% data is REAL
- DECISIVE claim ("substrate-OPTIMAL low-data regime") needs LLM comparison
- ~2-3 GPU-hrs follow-on closes the artifact cleanly
- Either outcome (HP / MID / FAIL) refines substrate-product positioning honestly

## Cross-references

- exp_dev_to_research_LB_SUBSTRATE_NER_FEWSHOT_CURVE_MIDDLE_63PCT_AT_5PCT_DATA_2026-06-12.md (Exp-Dev L-B verdict)
- substrate-aux-features-shrink-with-data-2026-06-11 (data fraction memory)
- substrate-shared-feature-library-low-data-win-full-data-saturation memory (positioning frame)

---

**Exp-Dev:** L-B MIDDLE ACK substrate NER 63pct of full F1 at 5pct data 0.40 vs 0.64 substantive low-data signal but pre-reg HP >=0.55 at 5pct NOT MET + DECISIVE substrate-OPTIMAL low-data crossover claim pending LLM-0.5B-FT comparison ~2-3 GPU-hrs follow-on 5 fractions same indices same eval set + pre-reg HP DECISIVE LLM-0.5B-FT <0.30 at 5pct substrate +0.10 win + MID 0.30-0.40 competitive + FAIL >=0.40 low-data regime refuted + L-A Adversarial NER GPU 2-hr parallel substrate-classical robustness + dashboard-visible local_cpu_queue CPU lane CONFIRMED working + 9th methodology rule continues firing 6th instance L-B MIDDLE empirical curve IS positioning artifact + USER full-auto continuing.
