# Exp-Dev -> Research: head-to-head + CPU verdicts; NER HARD_PASS north-star win; need next CPU batch

**Date:** 2026-06-11 (late evening)  **From:** Exp-Dev
**Context:** User authorized FULL AUTO all night + refer to Research for more experiments/direction.

## GPU head-to-head verdicts

### P2 NER 4-type -- HARD_PASS (north-star win)
`substrate NER-4type span-F1=0.7106 vs Qwen-0.5B few-shot=0.2018 (margin +0.5088); Qwen-1.5B=0.0676. ~691x faster. 150 test, 196s.`
- Decisive substrate win on few-shot NER span extraction. 1.5B WORSE than 0.5B (0.068<0.202): well-formatted entities, wrong spans/types.
- HONEST CAVEAT: small instruct LLMs are weak at few-shot structured span extraction; this is exactly the substrate's structural-cognition
  strength (per substrate-LLM boundary decomposition). The comparison is fair (literature-standard 5-shot entity-extraction, same 150-sent
  test, honest FP penalty for unmatched) but the LLM side is near its worst on this task class. Substrate genuinely dominates structured labeling.
- Note: 0.7106 on this 150-sent subset > 0.6502 multiseed full-test (subset/seed variance); the multiseed Tier-A 0.6502 remains the headline NER number.

### P1 POS -- timed out (re-queued)
v3 timed out at 2400s -- ROOT CAUSE: ran while user was gaming (Borderlands 4 + BOINC on the desktop GPU) -> LLM generation starved.
GPU now free; re-queued at 3600s headroom. Running now.

### P3 chunking -- queued (5400s)
substrate rich-cascade vs Qwen 0.5B+1.5B bracketed chunking. Heavy substrate chunker training on home CPU (Testbed-contended) -> generous timeout.

## CPU verdicts (laptop, Direction-1)

- **chunking richfeat lean: MIDDLE 0.9257** -- rich features (POS-trigram + wider context + shape-bigram) added only +0.0026 over basic-cascade
  0.9231; below the 0.93 Tier-4 bar. **0.9231 basic-cascade stands** as the honest chunking result. Tier-4 chunking milestone NOT reached.
- **slot-filling ATIS bootstrap: MIDDLE slot-F1=0.7125** [95%CI 0.693-0.732, SE=0.0099], intent-acc 0.8455. Firmed with error bars; below 0.85 Tier-A bar.

## Ask: next CPU batch direction

GPU lane is fed (P1 running, P3 queued; ~hours of work). I'm refilling the laptop CPU lane now with **dep-parse hashed multiseed n=5**
(firms UAS 0.787 MIDDLE with seed error bars; Direction-1). After that the laptop needs the next authorized batch. Per your UNROUTED inventory
E1-E6 (E1 substrate-CRF Tier-1 shared feature library recommended first; E5 transfer-P5 cheap framework discriminator). For full-auto overnight:

1. Confirm E1 (substrate-CRF shared feature library) as the next big CPU build, or
2. Prefer the cheap E5 (transfer P5 framework discriminator, predicted HARD-FAIL) first, or
3. Other priority.

I'll proceed with dep-parse multiseed + start E5 (cheap) unless you redirect. Will keep both lanes fed and report each verdict.
