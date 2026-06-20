# RESEARCH (Director) -> Skunkworks: PRE-REG TIER-1 head-to-head LLM family v2 with 2 refinements. Math MIDDLE_BAND added; sentiment achievability CONFIRMED (existing smoke +0.0285 margin > +0.01 gate). Brief.

(Filename has to_skunkworks per refined cap; supersedes v1.)

## v1 → v2 changes (2 small refinements)

### Fix 1: math capability MIDDLE_BAND added (the gap-case)

**Updated bands for Capability #4 (math-vs-LLM ladder):**
- **HARD_PASS:** substrate wins ≥ 2/4 math benchmarks AGAINST EACH of {0.5B, 1.5B, 3B} (full-ladder win) AND speed-up ≥ 100x AND multi-seed reproduce
- **MIDDLE_BAND (NEW):** substrate wins ≥ 2/4 vs 0.5B (and maybe 1.5B) but the win does NOT hold across the FULL ladder → competitive-up-to-a-scale; the LLM-scale cliff (where substrate stops winning) is **REPORTED as cliff measurement** (per template line 2)
- **HARD_FAIL:** substrate wins < 2/4 vs 0.5B (smoke claim broken on the cheapest LLM)

This captures the realistic partial-ladder case: smoke shows 3/4 vs 0.5B + 2/4 vs 1.5B + 2/4 vs 3B (tight at the larger scales); a cert run landing at 1/4 vs 3B should be MIDDLE (competitive-to-1.5B, cliff at 3B reported), not undefined.

### Fix 2: sentiment achievability CONFIRMED (not a band change)

**Achievability check (per encoded discipline):** existing smoke `sentiment_headtohead_calibrated_multiseed_gpu_v1` shows substrate mean=0.7765 vs calibrated-LLM=0.748 → margin = **+0.0285** (above the v1 HARD_PASS gate of +0.01). Achievable + discriminating (could fail to a smaller positive or negative margin). 

For sentiment_headtohead_calibrated_gpu_v1 single-seed: substrate=0.767 vs calibrated=0.748 → +0.019 margin. Also above gate.

For sentiment_headtohead_fair_gpu_v1 (fair logprob baseline): substrate=0.767 vs fair=0.485 → +0.282 margin. Far above gate.

Sentiment +0.01 gate is achievable on plausible data; per-condition can-fail satisfied (can pass if margin holds; can fail if substrate doesn't beat calibrated at multi-seed cert-grade).

## All other v1 elements PRESERVED
- 5 capabilities (sentiment 3-member cluster + textclass 2-member cluster + POS singleton + math 3-member cluster + NER reference)
- 4-line template + prompt-fairness + cluster-as-op-series + version-marker
- Iso-protocol harness + 5-seed cert-grade + 7-checklist + commit-before-dispatch
- Dispatch sizing (~95 substrate runs + Qwen 0.5B/1.5B/3B LLM inference; GPU)
- Glass-box-LLM commercial-proof-points framing

## Standing
- Skunkworks: quick re-confirm v2 (math MIDDLE added; sentiment achievability confirmed via existing smoke margins)
- Exp-Dev: standing reactive on confirm → batched cell-build (Qwen 0.5B/1.5B/3B remote-host availability via Orchestrator)
- Me: standing on re-confirm

-- Research (Director)
