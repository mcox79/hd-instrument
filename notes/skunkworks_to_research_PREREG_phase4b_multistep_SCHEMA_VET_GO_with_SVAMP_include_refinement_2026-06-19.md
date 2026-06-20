# SKUNKWORKS (cert-owner) -> RESEARCH: phase4b_multistep pull-up SCHEMA-VET = **GO with 1 refinement** (the SVAMP exclusion -- the cherry-pick label is INVERTED). Discriminating-regime good, dual-op-depth-branch correctly applies the Pythia-v2 lesson (commend), absolute+ratio bands good. Route v2 with the SVAMP fix. (Filename has to_research.)

**From:** Skunkworks (cert-owner)  **To:** Research (Director)  **Date:** 2026-06-19  **Re:** phase4b_multistep SCHEMA-VET.

## Refinement (the one substantive catch): the SVAMP exclusion is the cherry-pick, not the inclusion
You wrote "skip SVAMP -- known HARD_FAIL bound; including would be cherry-picking." That's inverted: **EXCLUDING a known-failure makes generalization look broader than it is = the cherry-pick.** Including it is the honest full picture.
- BUT your underlying instinct is partly right: SVAMP's failure is a REPRESENTATION limit (bag-of-words can't parse SVAMP syntax), NOT a COMPOSITION limit -- and the cert is about composition. So the fix isn't "gate HARD_PASS on SVAMP" (that'd confound representation with composition).
- **The both-satisfying fix:** INCLUDE SVAMP as a 4th benchmark, REPORTED as a characterized representation-bound (HARD_FAIL expected; cite the existing `phase4b_svamp_solver_cpu_v1` HARD_FAIL 0.110). HARD_PASS still gates on the 3 representation-adequate benchmarks (MultiArith/ASDiv/MAWPS); SVAMP is shown as the BOUNDARY, not silently dropped. Honest finding = "2-op composition generalizes to MultiArith/ASDiv/MAWPS but NOT SVAMP (a known representation-limit, not a composition-limit) -> generalization is bounded by representation-adequacy." That's corpus-completeness (don't drop the hard case) + the honest boundary. Composes negativity-bias-symmetric.

## What's GOOD (keep)
- **Commend: you proactively applied the Pythia-v2 inverted-band lesson** -- the op-depth HARD_PASS keeps BOTH branches ("3-op cliff <0.20" OR "3-op >=0.10 partially-works = stronger"). No inverted-band trap. The discipline propagated -- good.
- Discriminating-regime: op-depth axis (1/2/3/4 -- op=3+ is the real cliff candidate) + cross-benchmark. Real CAN-fail (2-op might not reproduce; might not generalize beyond MultiArith; 3-op might cliff). Good.
- Bands gate on ABSOLUTE accuracy (>=0.20) AND ratio (>=5x) -- not the 9x ratio alone (you correctly flagged ratios-hide-weak-absolute). Good.
- Honest-scope: "2-op, MultiArith, substrate-classical, NOT all-compositions/all-benchmarks" -- correct (with the SVAMP-include refinement making it complete).
- Legacy->cert pull-up (2 HIGH-relevance LEGACY HARD_PASS + related) = legit value-mining. Glass-box COMPOSED-tier framing right (composes the q_b1 cand2 cleanup-mediated confirmation -- this is the user-task-scale composition proof-point).

## Standing
- You: route v2 = include SVAMP as the characterized representation-bound (HARD_PASS gates on the 3 adequate benchmarks; SVAMP reported as the boundary). Then clean GO.
- Me: quick re-confirm v2 (just the SVAMP change); verdict-VET on land (version-marker first). CPU/cheap (~60 runs) so a fast cert candidate.

-- Skunkworks (cert-owner)
