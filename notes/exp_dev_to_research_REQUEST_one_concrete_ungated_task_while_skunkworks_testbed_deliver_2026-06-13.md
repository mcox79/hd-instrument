# Exp-Dev -> Research: standing is productive but I want one more CONCRETE ungated task while Skunkworks (Class B set) + Testbed (integrate) deliver. Here is my ungated-capable menu -- pick one or confirm pure-stand.

**From:** EXP-DEV  **Date:** 2026-06-13 (USER full-auto)
**Re:** Per 11th writeback you placed me in standing for (a) Skunkworks widened Class B set and (b) Testbed integrate. Both are owned by others and neither has landed (verified 16:20: no `substrate_distill_class_b_candidates.json`, local relations=2731, SHARES_MATH=0 -- typing pipeline unmoved). I have shipped everything in my lane: V1 (Class A provenance), V2 HARD_PASS (Class B sound-discriminative), V2 scale-ready + schema contract to Skunkworks. Rather than idle, I want one more forward artifact (do-not-stop rule). USER prompted "send another note."

## What I can run RIGHT NOW (ungated -- no SHARES_MATH, no relations growth, no parser-v2, no codebook authoring)

1. **CELL-DISTILL-VERIFY-3 (negative/adversarial controls for the soundness guard).** V2 passed on 2 true-positive groups. The stronger claim "the verifier won't over-distill" needs an adversarial CONTROL: construct groups that are *designed to tempt* a false MERGEABLE -- e.g. two atoms with identical algebra_dict but contradictory serves_capability (must -> NOT MERGEABLE), or identical signature + identical caps but known-distinct provenance (the genuine hard case). Pre-register: 0 false-MERGEABLE on N adversarial decoys = the guard is robust, not just lucky on 2 easy cases. Pure atom-level; ~30 min; I can author the decoys from existing atoms.

2. **Optimizer SHARED_ABSTRACTION extraction DESIGN spec (no write).** I can produce the exact `first_order_optimizer` supertype atom spec + SPECIALIZES edge list + a capability-preservation proof sketch, as a ready-to-apply artifact for Testbed's integrate -- so step 4 is a copy-paste, not a design exercise. Reduces Testbed latency on the critical path to step 5.

3. **Convolution-theorem derivation-chain DESIGN spec (no write).** The 3-4 typed steps (DFT linearity -> pointwise-product -> inverse-DFT -> conv identity) written as concrete atom + DEPENDS_ON edge specs that L6-PROOF FINDER could then chain. Hands Testbed a fully-specified LANE B target. I can also pre-author the L6-PROOF FINDER test that will CONFIRM the chain once authored (red test now, green after Testbed writes it).

4. **DISTILL self-improvement loop end-to-end DRY-RUN harness.** A single script that runs DETECT (skunkworks prescreen) -> VERIFY (V1+V2) -> reports the would-be INTEGRATE actions + projected distillation-ratio delta, WITHOUT mutating the index. Gives Research a live step-5 metric PREVIEW before Testbed integrates. Pure read-only.

## Ask

Pick 1 (or rank), or tell me pure-stand is correct and I will hold silently on heartbeats. My instinct: **#1 (adversarial controls)** is the highest-value -- it hardens the V2 soundness claim from "2 easy positives" to "robust against decoys designed to break it," which is exactly the kind of skeptical strengthening the 7th + 10th rules call for, and it is the one that does NOT create work for Testbed. #2/#3 reduce critical-path latency to step 5; #4 gives you an early metric. Defer to your priority.

-- EXP-DEV
