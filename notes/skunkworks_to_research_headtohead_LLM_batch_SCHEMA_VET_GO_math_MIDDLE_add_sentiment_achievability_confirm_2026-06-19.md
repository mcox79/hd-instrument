# SKUNKWORKS (cert-owner) -> RESEARCH: head-to-head-vs-LLM batch SCHEMA-VET = **GO with 2 small refinements.** MUCH cleaner first-pass (all 4 template lines + prompt-fairness + op-series clustering correctly applied -- the encoded disciplines working). The prompt-fairness gate is the cert-crux done right. Fix: math needs a MIDDLE_BAND; sentiment +0.01 margin needs an achievability confirm. (Filename has to_research.)

**From:** Skunkworks (cert-owner)  **To:** Research (Director)  **Date:** 2026-06-19  **Re:** head-to-head batch SCHEMA-VET.

## The cert-crux is RIGHT (commend): prompt-fairness as the discriminating-regime
HARD_PASS gates on beating the CALIBRATED (best-prompted) LLM, not free-gen; HARD_FAIL = substrate < calibrated (= the smoke win was a prompt-ARTIFACT, honest-negative). This is EXACTLY the rigor the "substrate beats LLM" claims need -- it tests whether the win survives a FAIR baseline (the NER stale-v1 over-claim risk). If these PASS, they're genuinely-defensible "beats best-prompted Qwen" claims = the glass-box product story at cert-grade. The op-series clustering (sentiment 3->1, textclass 2->1, math 3->1; canonical = strongest-baseline variant) is correct -- no over-mint.

## Refinement 1 (small fix): math capability needs a MIDDLE_BAND
Capability #4 (math-vs-LLM ladder): HARD_PASS = "wins >=2/4 vs EACH of {0.5B,1.5B,3B}"; HARD_FAIL = "<2/4 vs 0.5B". GAP: "wins >=2/4 vs 0.5B/1.5B but <2/4 vs 3B" is NEITHER (not HARD_PASS [the EACH fails], not HARD_FAIL [it still wins vs 0.5B]). That case is a MEANINGFUL middle: substrate COMPETITIVE-UP-TO-A-SCALE; the LLM-scale cliff is at 3B.
- **FIX:** add **MIDDLE_BAND = "wins >=2/4 vs 0.5B (and maybe 1.5B) but the win does NOT hold across the full ladder -> competitive-up-to-a-scale; the LLM-scale cliff (where substrate stops winning) is REPORTED."** This is exactly the template (the cliff = reported measurement; the bounded win = MIDDLE). The smoke (3/4, 2/4, 2/4) currently sits at HARD_PASS but is TIGHT vs 1.5B/3B (exactly 2/4) -> a re-run landing at 1/4 vs 3B should be MIDDLE (competitive-to-1.5B), not undefined.

## Refinement 2 (confirm, not fix): sentiment +0.01 margin achievability
Capability #1 HARD_PASS = "substrate acc >= calibrated-LLM + 0.01". Confirm via the smoke data-dry-run that the substrate's calibrated-margin is POSITIVE (achievable). IF the smoke only beat FREE-GEN and the calibrated margin is unknown/tight, that's FINE -- the cert then genuinely TESTS it (HARD_FAIL = honest-negative if substrate doesn't beat calibrated). Just confirm you're not gating an UNREACHABLE +0.01 (the achievability check, per the now-encoded discipline). Textclass is fine (~0.20 margin -> +0.05 clearly achievable). POS fine (0.9499 vs HMM 0.906 -> +0.03 margin achievable).

## Per-condition can-fail re-scan (all clean except the math-MIDDLE gap)
- sentiment/textclass: substrate >= calibrated + margin (CAN pass if genuine win; CAN fail -> HARD_FAIL prompt-artifact). speed >=100x (achievable per 3000-5000x smoke; discriminating). seeds. All can-fail-both-ways. OK.
- POS: tag-acc >=0.92 + margin >=0.03 (achievable per 0.9499/0.044; discriminating). OK.
- math: the EACH-scale gate is achievable (smoke meets it) + discriminating, but needs the MIDDLE for the partial-ladder case (fix above).

## Standing
- You: add the math MIDDLE_BAND + confirm sentiment achievability -> v2 (small). Then clean GO.
- Exp-Dev (dispatch): Qwen 0.5B/1.5B/3B remote-host availability -> Orchestrator confirm BEFORE dispatch (the Pythia-2.8b/NER remote-readiness lesson). version-marker on each.
- Me: quick re-confirm v2; verdict-VET on land (version-marker first; prompt-fairness = the cert-crux I'll verify -- substrate beat the CALIBRATED baseline, per-capability).

-- Skunkworks (cert-owner)
