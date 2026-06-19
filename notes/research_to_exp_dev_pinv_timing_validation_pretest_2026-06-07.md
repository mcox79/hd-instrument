# Research -> Exp-Dev: production pinv timing pre-test (validates Tier 4 strongest claim)

**From:** Research session
**To:** Exp-Dev
**Date:** 2026-06-07
**Re:** Tier 4 speed/energy 2x drill's recommended pre-test. Validates the strongest
quantitative claim (knowledge updates 240k-8.8Mx faster than LLM fine-tune).

## Pre-test: measure substrate pinv write timing on production hardware

The drill claimed substrate pinv write at 1.23 ms for 1000 facts at production N. This
needs MEASURED confirmation before the customer pitch ships with the number.

Method:
- Set up production-config substrate at N=4096 (modern Hopfield from cycle 155 HP)
- 4-bit W quantization (cycle 161 HP)
- d=30 PCA truncation on keys (cycle 159 HP)
- Use bge-small encoded fillers (production retrieval encoder per two-encoder lock)
- Write 1000 random facts via pinv update
- Measure wall time per 100-fact batch + total

HARD-PASS: total wall time < 5 ms for 1000 facts (4x margin over the 1.23 ms claim).
BORDER: 5-20 ms (use the measured number in customer pitch).
HARD-FAIL: > 100 ms (claim breaks; revise pitch downward).

Wall: ~30 min CPU.

## Why this matters

The substrate's knowledge update advantage is the STRONGEST quantitative claim in the
Tier 4 customer pitch — 240,000x to 8,800,000x faster than LoRA fine-tune. Other claims
narrow:
- FLOPs 184x is real but mostly from 8B vs 200B LLM, not substrate's bipolar arithmetic
- Energy 10-90x system-level today (not 100-1000x as ASIC future-roadmap claim)
- Latency 5x for 100-token answers; narrows at long answers

The knowledge update claim is architectural (substrate's Hebbian write is genuinely O(1)
per fact regardless of LLM size). It's the one number that frontier LLMs cannot match
at any scale. Confirming the 1.23 ms wall time empirically anchors the entire customer
pitch around this number.

## Decision rule

HARD-PASS: ship the "240,000x faster knowledge updates" claim in customer materials with
the measured number.

BORDER: ship with the measured number, just be honest about the multiplier (e.g.,
"100,000x faster" if measured shows substrate at 10 ms for 1000 facts vs LoRA at
~10 min).

HARD-FAIL: knowledge update advantage shrinks materially; revisit which Tier 4 customer-
pitch claims are anchored on this number.

## Cross-references

- Tier 4 speed/energy 2x drill: notes/research_drill_tier4_speed_energy_quantified_2x_2026-06-07.md
- Tier 4 consolidated routing: notes/research_to_exp_dev_tier4_consolidated_routing_2026-06-07.md

---

**END.**

**Exp-Dev:** authorize 30-min CPU pinv timing test. Apply HARD-PASS / BORDER / HARD-FAIL
autonomously. File measured wall time to me. Pre-test #4 in the Tier 4 program (Pythia
pre-tests 1-3 + this timing test = full Tier 4 gating battery).
