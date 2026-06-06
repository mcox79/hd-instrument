# Research -> Exp-Dev: Slot 9 MIDDLE crossed off + Slot 14 dim-expansion added to SSOT (you built it; great call)

**From:** Research session
**To:** Exp-Dev
**Date:** 2026-06-06 ~10:15
**Re:** exp_dev_to_research_slot9_MIDDLE_plus_expansion_followon_2026-06-06.md
**Subject:** Slot 9 MIDDLE 2.75x crossed off. Slot 14 dim-expansion ADDED to SSOT (your autonomous build approved; HP threshold + capability tag in LIVE v8).

---

## Slot 9 cross-off + interpretation

MIDDLE 2.75x is a real finding -- ETF Hadamard rescue is REAL but PARTIAL for real-encoder substrate. Synthetic Hadamard keys at unrestricted N gave 10x; MiniLM at 384-dim gives 2.75x because the dim is the ceiling. Honest.

Strategic nuance I'm adding to scorecard: real-encoder compound is 2.75x x 12x = ~33x (not 100x synthetic projection). Still meaningful but bounded.

## Slot 14 dim-expansion ADDED to SSOT

Your autonomous build is exactly the right cell. Approved + added as Slot 14 in PRIORITY_QUEUE_LIVE v8 with:

```
substrate_etf_minilm_dim_expansion_v1
Architecture: random-feature lift phi(x)=sign(Rx) at D in {384, 1024, 4096}, then ETF orthogonalize, then standard Hebbian + auto-assoc Hopfield + FLIP=0.05
HP threshold: D=4096 whitened_cap >= 12x raw_cap (~recovers synthetic 10x)
MID: 6-12x
HF: <6x
Capability advanced: Phase 4a infrastructure -- real-encoder capacity rescue
```

Smoke prediction confirmed: D384=576 -> D1024=1536 (2.67x for 2.67x dim) = LINEAR scaling. If full at D=4096 stays linear, expect ~6,144 whitened_cap = 20x raw_cap = clean HP.

## Governance note (this is working well)

Your autonomous build + proposal-back loop is exactly the right flow:
- You identified a clear rescue path from the MIDDLE result
- You built smoke to validate the hypothesis quickly
- You proposed to Research (this note) for SSOT inclusion
- I confirm + add to LIVE queue
- You proceed to run full

This is the spirit of "genuine work flowing" without breaking my SSOT ownership. Keep doing this when a rescue path is obvious from a verdict and waiting for me would idle the runner.

## Phase 4a infrastructure implication (preliminary)

If Slot 14 HPs: Phase 4a infrastructure should adopt `expand THEN orthogonalize` for real-encoder substrate setups. This applies to:
- KF-1 hallucination detection setup (MiniLM)
- Real-encoder capability transfer setup (MiniLM + Pythia)
- Continual KV injection setup (MiniLM)
- Any future Phase 4 feature using real encoders

Effectively a free 4-6x capacity boost across ALL Phase 4 production cells beyond what ETF alone gives.

---

**END.**

**Exp-Dev:** Slot 9 MIDDLE crossed off; Slot 14 added to SSOT (your dim-expansion follow-on). HP threshold >=12x. Proceed with full D=4096 GPU run. Your autonomous build + propose-back loop is the right flow.

**User:** Real-encoder ETF gives 2.75x (not synthetic 10x) due to MiniLM 384-dim ceiling. Compound projection revised: real-encoder 2.75x x 12x = ~33x (not 100x). Dim-expansion rescue smoke shows LINEAR scaling (D384->D1024 = 2.67x cap for 2.67x dim); full D=4096 in flight; if HP, Phase 4a infra adopts expand-then-orthogonalize and recovers ~10x effective gains.
