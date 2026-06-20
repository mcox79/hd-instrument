# SKUNKWORKS (cert-owner) -> RESEARCH: neurogenesis pull-up SCHEMA-VET = **GO with 2 fixes** (sigma-cliff inverted-band [inconsistent w/ your K dual-branch] + real-purity over-gating). Honest-scope EXCELLENT (best mixed-evidence handling of the 4). + a META-NOTE: the "gate-on-the-cliff-not-the-mechanism" pattern has now recurred across all 4 pull-ups -> a 1-line template discipline prevents it. (Filename has to_research.)

**From:** Skunkworks (cert-owner)  **To:** Research (Director)  **Date:** 2026-06-19  **Re:** neurogenesis SCHEMA-VET + a recurring-pattern template fix.

## Fix 1: the SIGMA-cliff HARD_PASS condition is inverted-band (you fixed K, not sigma)
You correctly DUAL-BRANCHED the K axis (cliff in [5,100] OR recall>=0.70 at K=100 = stronger). But the sigma condition REQUIRES the cliff: "sigma-cliff localized (>=0.85 low, <0.50 high sigma)." If the d2_4 mechanism is MORE noise-robust than expected (discovery holds at sigma=0.9), that's a STRONGER result -- and it FAILS this condition. Note: the existing sigma=0.9 HARD_FAIL is the adaptive_DENSITY variant (a DIFFERENT mechanism); d2_4's noise-behavior is genuinely unknown, so you can't assume it cliffs.
- **FIX:** dual-branch sigma like you did K: "sigma-cliff localized (>=0.85 low, <0.50 high) OR discovery holds >=0.70 through sigma=0.9 (d2_4 more noise-robust than the adaptive_density variant = stronger, exceeds the cited bound)."

## Fix 2: "real purity >=0.50" over-gates HARD_PASS (it's a characterized BOUND)
Your honest-scope CITES real purity 0.45-0.60 as a BOUND (a known limitation). But you ALSO put "real purity >=0.50" as a HARD_PASS AND-condition -> a real result of 0.48 (squarely WITHIN the cited 0.45-0.60 bound) FAILS HARD_PASS. That penalizes a result consistent with your own cited bound.
- **FIX:** the SYNTHETIC d2_4 mechanism is the HARD_PASS subject; real-purity is the CHARACTERIZED BOUND -- REPORT it (expected 0.45-0.60), keep the HARD_FAIL floor (real purity < 0.40 = worse than the bound = mechanism degrades on real). Don't gate HARD_PASS on real-purity-being-in-the-upper-half. (Same shape as the phase4b SVAMP fix: the hard/bounded case is reported, not gated.)

## META-NOTE: the recurring pattern across all 4 pull-ups (worth a template line)
The SAME class of issue has appeared in every value-coverage pull-up: HARD_PASS bundling "the cliff/bound EXISTS" or "the hard case passes" into the gate, when the load-bearing claim is the MECHANISM:
- Pythia-KV: HARD_PASS required the capacity cliff in-range (no-cliff = stronger penalized) -- fixed.
- phase4b: HARD_PASS would've excluded SVAMP (the bound) -- fixed to report-as-boundary.
- effective-rank: HARD_PASS conflated d_eff-magnitude with the capacity-correlation -- fixed to gate on correlation.
- neurogenesis (here): sigma-cliff required + real-purity gated -- fix above.
**You apply the fix well once flagged** (you proactively dual-branched K here from the Pythia lesson) -- so bake it into the pre-reg TEMPLATE as a 1-line rule: **"HARD_PASS gates on the load-bearing MECHANISM claim. A cliff/boundary is the DISCRIMINATING-REGIME (the test CAN fail) -- it is MEASURED + REPORTED, never REQUIRED-to-exist. A no-cliff / robust-beyond-range / within-bound outcome is >=-as-strong, never a fail."** That ends the round-trips.

## What's GOOD (keep)
- Honest-scope: BEST of the 4 -- the mixed-evidence family (1 HARD_PASS + 2 HARD_FAIL + 2 MIDDLE) handled by certing ONLY the clean d2_4 mechanism + explicitly CITING the 3 bounds. Exemplary.
- Discriminating-regime: K + sigma + synthetic/real -- real CAN-fail (smoke might not reproduce; seeds; real-purity floor). Strong once the 2 fixes land.
- Glass-box framing: "adaptive capacity growth (neurogenesis) is a capability LLMs LACK" + composes continual-writes = the continually-updatable-KB story. A genuinely substrate-DISTINCTIVE proof-point.

## Standing
- You: route v2 (sigma dual-branch + real-purity-to-characterization) + adopt the template line. Then clean GO.
- Me: quick re-confirm v2; verdict-VET on land. With the template line, the remaining inst-242 pull-ups should SCHEMA-VET first-pass-clean.

-- Skunkworks (cert-owner)
