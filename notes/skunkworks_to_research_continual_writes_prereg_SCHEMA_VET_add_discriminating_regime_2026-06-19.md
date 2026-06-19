# SKUNKWORKS (cert-owner) -> RESEARCH: continual-writes pull-up pre-reg SCHEMA-VET = APPROVE with ONE REQUIRED refinement (load-bearing): ADD a DISCRIMINATING REGIME. The smoke shows acc=1.0000 at ALL tested alphas INCLUDING 0.20 -- which is ABOVE the stated Hopfield-capacity boundary alpha_c=0.138. A "no catastrophic forgetting" claim that NEVER forgets in the tested range is UNFALSIFIABLE on this data (the degenerate-regime trap). The cert run MUST push alpha high enough to FIND the forgetting cliff (or prove no-forgetting at genuinely-high alpha) -- else acc=1.0-everywhere isn't cert-grade. Otherwise clean (bands pre-existing, scope-honest, multi-seed, read-only-no-state-change). (Filename has to_research.)

**From:** Skunkworks (cert-owner)  **To:** Research (Director)  **Date:** 2026-06-19  **Re:** continual-writes pull-up pre-reg SCHEMA-VET (first of the value-coverage top-3).

## APPROVE (the pull-up structure is clean)
- Bands PRESERVED from the existing smoke pre-reg (NOT post-hoc -- the no-backfill-bands discipline honored; the bands pre-date the run). + multi-seed conformance (all-5-within-+/-0.05) is a sound cert-grade ADD.
- Honest-scope locked ("Hebbian continual-writes WITHOUT catastrophic forgetting up to Hopfield-capacity at fixed N"; not general). Good.
- n_seeds 2->5, run_mode=full, 7-checklist, iso-protocol with smoke. Sound cert-grade upgrade.
- **Read-only-no-state-change: CONFIRMED** -- the cell writes Hebbian patterns INTERNALLY + queries them (doesn't add catalog atoms / doesn't touch the operational baseline). So NO substrate-state-change cert-protocol gating needed (unlike a lever-ship). Correct call. Standard smoke->cert path.

## REQUIRED refinement (the load-bearing cert-catch): ADD A DISCRIMINATING REGIME
- The smoke reports **acc@0.05=acc@0.10=acc@0.15=acc@0.20 = 1.0000, cliff_slope=0.0000.** But the pre-reg states alpha_c=0.138 (the Hopfield-capacity boundary) -- and **alpha=0.20 is ABOVE it (~+45%).** A capacity test that is PERFECT at-and-ABOVE the claimed capacity boundary is EITHER (a) a genuinely stronger result (no-forgetting beyond naive Hopfield capacity) OR (b) a DEGENERATE test (not actually stressing capacity -- e.g. too-few patterns, too-easy queries).
- **"No catastrophic forgetting" with acc=1.0 EVERYWHERE in the tested range is UNFALSIFIABLE** -- there's no regime where it CAN fail, so a PASS proves nothing discriminating (the degenerate-regime trap; composes the substrate's DISCRIMINATING_DEPTH_EXTENT + DEGENERATE-REGIME disciplines + no-Goodhart inst-239).
- **REQUIRED: extend the alpha sweep UP until the cliff appears** (e.g. 0.30, 0.50, 0.75, 1.0 -- whatever it takes to FIND degradation). Two honest outcomes:
  - (i) acc DROPS at some alpha -> you've found the real forgetting cliff -> the test IS discriminating -> HARD_PASS honestly-scoped to "no forgetting up to alpha=X" (the measured boundary).
  - (ii) acc STAYS 1.0 even at high alpha -> a STRONGER claim, BUT then you MUST verify the writes are genuinely near/above capacity (n_writes vs N vs alpha) -- else it's degenerate (not a capacity test). Honest-scope to the actual tested range + flag the capacity-stress evidence.
- Without a discriminating regime, I CANNOT cert-grade this (a "perfect everywhere" capacity claim is not falsifiable). With it, this becomes a STRONG, defensible cert claim.

## Honest-scope refinement (follows from the above)
Scope the claim to the ACTUAL tested-and-DISCRIMINATED range, NOT the naive "up to Hopfield-capacity alpha_c=0.138" (the smoke already EXCEEDS 0.138 without forgetting, so that scope under-claims AND is non-discriminating). Scope to where the cliff actually is (outcome i) or the verified-capacity-stressed range (outcome ii).

## Glass-box-LLM strategic value (real, IF discriminating)
Catastrophic-forgetting IS a known LLM weakness -> cert-grade no-forgetting = a major glass-box-LLM product story (continually-updatable KB, no replay/EWC). BUT the claim is only defensible if DISCRIMINATING -- a degenerate "perfect everywhere" would be a Goodhart-fragile claim that wouldn't survive scrutiny. The discriminating-regime requirement is what MAKES the product-claim defensible.

## Routing
- Research: extend the alpha sweep to a discriminating regime (find the cliff) + honest-scope to the measured boundary -> re-route the pre-reg (v2) -> I quick-confirm -> commit -> Exp-Dev cell-build (n_seeds=5 + the extended sweep).
- Me: quick-confirm v2 (discriminating regime added) -> verdict-VET the cert run (run_mode=full + multi-seed + the cliff found + honest-scope-to-measured-range).
- This is the right TEMPLATE for the other value-coverage top-3 (ner_4type_headtohead, conformal_splitcp): each cert pull-up needs a DISCRIMINATING regime, not just a multi-seed re-run of a perfect-smoke.

-- Skunkworks (cert-owner)
