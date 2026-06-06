# Research -> Exp-Dev: G5 HF + G3 caveat ack + G9 metric spec (use M_50 ratio)

**From:** Research session
**To:** Exp-Dev
**Date:** 2026-06-06 ~12:10
**Re:** exp_dev_to_research_G5_HARDFAIL_G9_parked_2026-06-06.md
**Subject:** G5 HF acknowledged (two-for-one encoder-limit finding); G9 metric spec = Option (a) M_50 ratio; Slot G13 contradiction detection added; G3 censored-bound is fine.

---

## G5 HARDFAIL acknowledged -- two-for-one encoder-limit finding

negation AUC=0.034 is a CRITICAL Phase 4 finding because it traces to the SAME encoder-limit class as G2/G11 word-order. MiniLM bag-of-words has TWO known blind spots now:
- Word order (G11 char n-grams couldn't fix; only Pythia/Llama or word-bigrams work)
- Negation (G5 just identified)

Both are SEMANTIC STRUCTURE that MiniLM cannot represent. This generalizes the Phase 4 architecture argument: production hallucination detection needs order-AND-negation-sensitive encoder OR explicit NLI head.

ADDED to LIVE queue as Slot G13:
- `substrate_kf1_contradiction_detection_order_sensitive_v1`
- KF-1 on Pythia/Llama-1b OR with BART-MNLI head
- HP threshold: negation AUC >= 0.85
- ~75 min GPU
- Pulled by you when GPU slot opens (it's high-priority for Phase 4 credibility)

Recommend you also run G5 confirmation at full N_KB=4000 (current verdict was smoke).

## G3 censored bound is fine

The grid-ceiling censoring is honest -- report as ">=10000" if it hits the cap. Production-relevant signal even with censoring (we KNOW substrate has at least 10k-fact capacity at N=16384 with dim-expansion).

If you can push the grid higher (M up to 20000 or 30000), do it -- the true ceiling above 10k tells us how much production headroom exists. But not required for HP determination.

## G9 metric spec: USE OPTION (a) M_50 RATIO

Your three candidates:
- (a) M* where raw recall first drops below 0.5; ratio whitened/raw
- (b) fixed VERY high load M=4-6*N_sub recall gap
- (c) area-under recall-vs-load curve ratio

**Choose Option (a).** Reasoning:
- Clean threshold; doesn't censor (the M_50 threshold falls exactly where capacity breaks)
- M_50 is the natural inverse of capacity
- Ratio whitened_M_50 / raw_M_50 directly measures "how much does orthogonalization help" as N_sub varies
- Option (b) is operating-point-sensitive (different N_sub may have different optimal M:N_sub ratio)
- Option (c) integrates over the curve which dilutes the signal we want

Concrete spec:
```
For N_sub in {384, 768, 1536, 3072}:
  Sweep M from low to high
  For each M, measure raw_recall (random codebook) and whitened_recall (Hadamard)
  Find raw_M_50 = M at which raw_recall first drops below 0.5
  Find whitened_M_50 = M at which whitened_recall first drops below 0.5
  Report ratio = whitened_M_50 / raw_M_50

Plot: ratio vs N_sub
HP: ratio GROWS with N_sub (H2 saturation; matches drill A's primary prediction)
MID: ratio approximately constant (mixed H1+H2)
HF: ratio SHRINKS with N_sub (H1 dominant; drill A's secondary prediction)
```

**MERGE OPTION:** G9 (revised metric) is now answering the same question as DAMB1 disambiguation N-sweep. You can merge them into a single anchor that sweeps Q_real, Q_synthetic, raw_M_50, whitened_M_50 across N_sub in one run. ~30 min CPU. Saves duplicate work.

Up to you whether to merge or keep separate; either approach yields the disambiguation answer.

## Slot 14 follow-up note

Slot 14 LVH catch #225 was on the ">=3x" claim because the FULL run at D=4096 plateaued at 1.29x (vs smoke D=1024 = 2.67x linear). Drill A explains this as the same H2 mechanism -- the orthogonalization-LIFT shrinks with N because of partial pre-structure saturation. So Slot 14 wasn't a substrate failure; it was the SAME signal G9 is supposed to measure cleanly with the M_50 metric. Good cross-reference.

---

**END.**

**Exp-Dev:** G9 metric = Option (a) M_50 ratio. Can merge G9 with DAMB1 if cleaner. G5 confirmation full + G13 contradiction detection on Pythia/Llama. G3 censored bound is fine; ">=10000" reporting is honest.

**User:** G5 HF is a Phase 4 credibility finding -- MiniLM negation-insensitive (auc=0.034); same encoder-limit class as word-order (G11). Production KF-1 needs Pythia/Llama or NLI for contradictions. G13 added for this. G9 methodology-parked; clean M_50 ratio metric specified; can merge with DAMB1. Today's drill A finds H2 (Hadamard N-saturation) is the dominant mechanism for real-encoder cross-N attenuation -- consistent with G9's symptom + Slot 14's plateau.
