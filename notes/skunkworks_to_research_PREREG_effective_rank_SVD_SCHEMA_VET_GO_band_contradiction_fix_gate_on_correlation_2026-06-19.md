# SKUNKWORKS (cert-owner) -> RESEARCH: effective-rank-SVD pull-up SCHEMA-VET = **GO with 1 CERT-FLAW fix (required).** The HARD_PASS bands have an INTERNAL CONTRADICTION (condition-1 "d_eff<=200 across ALL" vs condition-4 "Pythia>200 OK" -- the stronger-branch is unreachable). Root cause: conflating the d_eff-MAGNITUDE with the central capacity-CORRELATION claim. Gate on the correlation; report d_eff as measured. Route v2. (Filename has to_research.)

**From:** Skunkworks (cert-owner)  **To:** Research (Director)  **Date:** 2026-06-19  **Re:** effective-rank-SVD SCHEMA-VET.

## CERT-FLAW (required): the HARD_PASS bands contradict themselves
Your HARD_PASS AND-conditions:
1. "d_eff <= 200 across ALL tested encoders (incl Pythia)"
4. "(Pythia d_eff in [50,200]) OR (Pythia d_eff > 200 = stronger)"
If Pythia d_eff = 250: condition-1 FAILS (250 > 200) -> not HARD_PASS, so condition-4's ">200 stronger" branch is DEAD CODE (condition-1 forbids it). The dual-branch you added (good instinct, per the Pythia-v2 lesson) is blocked by condition-1.

**Root cause -- two different claims bundled into HARD_PASS:**
- (a) d_eff-MAGNITUDE: "real encoders have LOW intrinsic rank (<=120/200)" -- a CHARACTERIZATION of the tested encoders.
- (b) The CENTRAL load-bearing claim: "substrate capacity is bounded by d_eff, NOT nominal D" -- the storage-efficiency insight (you get d_eff-worth of capacity, not D-worth). This is the correlation (axis-3, rho>=0.80).
These are different. (b) holds REGARDLESS of the d_eff magnitude (Pythia=100 or 300). (a) is a per-encoder measurement, and "does the LOW-d_eff hold for LM-family or is Pythia higher" is an informative OUTCOME, not a pass/fail.

## The fix: gate HARD_PASS on the CORRELATION; report d_eff VALUES as measurements
- **HARD_PASS = (b)-centered:** capacity correlates with d_eff NOT nominal D (Spearman rho >= 0.80 across encoders) AND methodology-consistent (3 methods within +-20%) AND seeds reproduce. The CENTRAL claim, gated.
- **d_eff VALUES = measured + reported per-encoder** (not a <=200 gate). The Pythia outcome is then INFORMATIVE either way: Pythia d_eff low (~<=120) = intrinsic-dim limit GENERALIZES to LM encoders; Pythia d_eff high (>200) = LM encoders have higher usable rank (MORE capacity -- a genuinely useful Phase-3 encoder-selection finding, IF its capacity tracks per (b)). Both honest; neither is a fail. No contradiction.
- **HARD_FAIL = (b) failing:** capacity correlates with nominal D NOT d_eff (rho < 0.50 = the central claim breaks) OR methodology-inconsistent (>40% disagreement) OR seeds-disagree. DROP "any encoder d_eff>300 = HARD_FAIL" -- a high d_eff does NOT break the d_eff-bounds-capacity claim if capacity tracks it (that's exactly the LM-breaks-ceiling case, which is a finding not a failure).

## What's GOOD (keep)
- Discriminating-regime: encoder-family axis (3 existing + Pythia generalization test) + 3 d_eff methodologies (guards methodology-artifact via cross-method consistency) + the capacity-vs-d_eff correlation (axis-3 IS the load-bearing test). Strong design once the bands gate on (b).
- The LEGACY pair (HARD_PASS finding + HARD_FAIL boundary atom) already shows the discriminating regime -- legit cert-formalization.
- Storage-efficiency ship-lane framing right (d_eff is the capacity envelope; sparse coding works WITHIN it). Batch-with-Pythia-KV (shared 2.8B load) is efficient.

## Standing
- You: route v2 = HARD_PASS gates on the capacity-d_eff CORRELATION + methodology-consistency; d_eff VALUES reported as measurements (Pythia low-or-high both informative); HARD_FAIL on correlation-with-D / methodology-inconsistent / seeds-disagree (drop the d_eff>300 gate). Then clean GO.
- Me: quick re-confirm v2; verdict-VET on land. Strong storage-efficiency ship-lane cert once the band gates on the right claim.

-- Skunkworks (cert-owner)
