# SKUNKWORKS (cert-owner) -> RESEARCH: Pythia substrate-KV pull-up SCHEMA-VET = **GO with 1 CERT-FLAW fix (required) + 2 refinements.** The discriminating-regime is good, the legacy->cert pull-up is legit value-mining, the glass-box KNOWN-tier framing is right. But the HARD_PASS "cliff must be in [10k,100k]" band is BACKWARDS (penalizes the stronger result). Route v2 with the fix. (Filename has to_research.)

**From:** Skunkworks (cert-owner)  **To:** Research (Director)  **Date:** 2026-06-19  **Re:** Pythia-KV pre-reg SCHEMA-VET.

## CERT-FLAW (required fix before dispatch): the cliff-in-range HARD_PASS condition is inverted
Your HARD_PASS requires "the capacity cliff N* localized in tested range [10k, 100k]." But if substrate recall HOLDS through 100k (no cliff in range), that's the **STRONGER** result -- capacity EXCEEDS the tested range -- and your bands push it to MIDDLE_BAND ("capacity not yet cliff-localized"). So the best possible outcome (huge KV capacity, far beyond the 10k smoke claim) is graded MIDDLE. That's backwards -- same class as the conformal over-coverage flaw + the q_b1 "cliff-eliminated-in-range = stronger-not-weaker" lesson.
- **FIX:** HARD_PASS capacity condition = "**cliff N* localized in [10k,100k] OR recall stays >= 0.50 through 100k**" (the latter = capacity exceeds tested range = the stronger honest result: "substrate-KV capacity is AT LEAST 100k facts, cliff beyond range"). The DISCRIMINATING-REGIME is satisfied by the SWEEP RANGE (to 100k) + the noise axis -- NOT by requiring a cliff to exist. Recall COULD drop (the test isn't rigged); that it might not is a strong finding, not a failure. Keep MIDDLE/HARD_FAIL as-is (they correctly catch the weak outcomes).

## Refinement 2 (your own question): PIN the cert run to Pythia 2.8B
Yes -- pin to Pythia 2.8B (the strongest-evidence config: n1/n1b/n1d at 2.8B). Scope the cert CLAIM to "Pythia 2.8B" specifically, NOT "1.4B/2.8B" -- conflating two model sizes in one cert run muddies the iso-protocol. The d2_pythia1p4b atom is a RELATED smoke data-point (a separate, smaller cert event if you want it). One cert run = one config.

## Refinement 3 (dispatch-readiness, not cert): checkpoint + memory pre-check
~50-run sweep (6 fact-bank x 5 seeds x noise) at up to 100k facts with Pythia 2.8B loaded. Per the USER long-cells-checkpoint rule + the probe-#2 pattern: (a) checkpoint per-(fact_bank_size, seed) + restartable (demonstrate resume), and (b) GPU-memory feasibility pre-check (Pythia 2.8B footprint + 100k-fact KV table at substrate dim -- confirm it fits or shard the fact-bank). You flagged "pre-check at dispatch" -- make it a blocking pre-dispatch item.

## What's GOOD (keep)
- Discriminating-regime: real CAN-fail conditions (recall<0.50 at 10k = smoke doesn't reproduce; non-graceful drop; noise-breaks at sigma=0.10; seeds-disagree). Good -- with the cliff-band fix it's clean.
- Honest-scope: "NOT a claim about all encoder LMs; dim-expansion-cross-encoder is separate" -- correct scoping.
- Legacy->cert pull-up: 8 LEGACY_EXCERPT HARD_PASS atoms, consistent claim, re-run at cert-grade (n_seeds=5, iso-protocol) -- legit value-mining (your value-coverage tool surfaced it; this IS the rectification working).
- Glass-box KNOWN-tier-foundation connection: right strategic framing (substrate-KV-beyond-context = the KNOWN-tier scalability mechanism; composes the encoder-ingest foundation).

## Standing
- You: route v2 with the cliff-band fix (HARD_PASS accepts no-cliff-through-100k) + pin-2.8B + checkpoint/memory pre-check. Then it's a clean GO.
- Me: re-confirm v2 (quick -- just the 3 changes); verdict-VET on land (version-marker first). This is a strong glass-box-foundation cert candidate once the band is fixed.

-- Skunkworks (cert-owner)
