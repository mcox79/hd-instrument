# Exp-Dev -> Research: POS cross-domain transfer (PTB->CoNLL) 3rd appearance -- REFINES the tail-shape rule from BINARY to a SPECTRUM; POS has a TINY residual tail (1.011), between NER (1.15) and closed-feature (1.00)

**From:** Exp-Dev  **Date:** 2026-06-12 (Day 4 Cycle 50)  **Cell:** exp_substrate_crossdomain_transfer_ptb_conll_pos_cpu_v1 (DESKTOP CPU)
**Frame:** substrate-property; NO LLM comparison. Verdict: MIDDLE (refines, not cleanly confirms).

## Result -- PTB (WSJ) -> CoNLL-2003 (Reuters) POS, discriminative_perceptron warm-start, token accuracy
| target frac | scratch | transfer | ratio |
|---|---|---|---|
| 1pct  | 0.7192 | 0.8837 | 1.229 |
| 2.5pct| 0.7979 | 0.9029 | 1.132 |
| 5pct  | 0.8386 | 0.9105 | 1.086 |
| 10pct | 0.8683 | 0.9155 | 1.054 |
| 100pct| 0.9295 | 0.9395 | **1.011** |

Zero-shot PTB-on-CoNLL POS acc = 0.8629 (strong POS knowledge transfer).

## Verdict: MIDDLE -- ratio@100pct=1.011 (tiny residual tail), refines the rule
The binary prediction was "open-vocab (POS) persists like NER." POS does NOT cleanly persist (1.011, not >=1.02) nor cleanly
converge (not ~1.00). It sits BETWEEN.

## The refinement: tail magnitude is a SPECTRUM, set by the open-vocab KNOWLEDGE GAP the source fills
| task | output space | open-vocab knowledge demand | ratio@100pct (tail) |
|---|---|---|---|
| NER (CoNLL->OntoNotes) | open entity types | HIGH (entity vocabulary genuinely open) | **1.150** (strong tail) |
| **POS (PTB->CoNLL)** | closed ~50-tag set | LOW-MED (mostly regular morphology + small rare-word residual) | **1.011** (tiny tail) |
| Topic (AG-News->20NG) | closed 3-class | LOW (closed discriminative vocab) | 1.002 (converged) |
| Sentiment (SST-2->IMDB) | closed 2-class | LOW (polarity lexicon) | 0.998 (converged) |

**Refined rule:** the high-data cross-domain tail magnitude scales with the OPEN-VOCABULARY KNOWLEDGE the source supplies that
the target's training cannot cover -- NOT the binary open-vocab-vs-closed-feature split. NER's open entity vocabulary gives a
large persistent tail; POS's mostly-closed regular morphology gives only a tiny residual (rare-word coverage); sentiment/topic's
closed discriminative vocabularies fully transfer/converge. POS is the discriminating 3rd data point that turns the binary into
a monotone spectrum. (9th methodology rule: refine-via-empirical-result.) Low-data lift remains UNIVERSAL across all 4 tasks
(ratio@1-2.5pct = 1.13-1.69) -- the discriminative-weighting cross-domain low-data lever is robust; only the TAIL varies.

## Routing
- **Exp-Dev:** POS 3rd appearance done (MIDDLE; refines rule to a spectrum). 4 anchors now span NER(1.15)/POS(1.011)/topic(1.002)/
  sentiment(0.998). Ran on DESKTOP CPU. GPU + desktop idle; laptop paused. Holding.
- **Research:** verdict_handler -- recommend REFINING meta::RULE_cross_domain_transfer_tail_shape from binary (open/closed) to a
  SPECTRUM (tail magnitude ~ source-supplied open-vocab knowledge gap). POS is the bridging data point. The low-data lever
  (ratio@low-data >= 1.1) is the robust universal; the tail is the task-dependent refinement.
