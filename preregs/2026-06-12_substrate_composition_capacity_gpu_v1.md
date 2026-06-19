# Pre-registration: Cell A -- Composition capacity benchmark (HRR bind/unbind over 280-atom corpus)

**Date:** 2026-06-12 (Day 4 Cycle 50)
**Cell:** experiments/exp_substrate_composition_capacity_gpu_v1.py
**Routing:** research_to_exp_dev_testbed_5_NEW_CELLS Cell A + VSA-drill pre-reg LOCK. Substrate-quality-first; NO LLM frame.
**Lane:** overnight_queue (GPU; torch). Uses substrate canonical hdlab.bind/unbind/bundle over REAL algebra_hrr atom vectors.

## Design
A_bound = bundle( bind(R_i, B_i) ), F simultaneous role-filler bindings; B_i drawn from the 280-atom algebra-encoded
corpus (clustered codebook, tw_edge_z=-2.26); R_i UNITARY HRR roles (exact single-binding inverse). Recover B_j =
cleanup(unbind(A_bound, R_j)) over the codebook. Sweep F in {1,2,3,5,10,20}, 3 seeds x 20 trials. Report recovery cosine +
cleanup acc@{1,3,5} per F.

## METRIC FLAG (discovered at smoke; flagged to Research)
Recovery COSINE of an HRR superposition is analytically **1/sqrt(F)** (crosstalk = F-1 unit-norm ~orthogonal terms; bundle
norm cancels in cosine), INDEPENDENT of D. Smoke confirms exactly: F=2->0.708, F=3->0.573 (=1/sqrt(F)). So the VSA-drill
locked "cosine recovery >= 0.95 at F=3" bar is UNREACHABLE for HRR superposition cosine at ANY dimension -- it conflates
cosine with decode success. The substrate-meaningful capacity metric is **CLEANUP ACCURACY** (does the substrate decode the
composed state to the right atom?), which is high even at low cosine (smoke cleanup@1=0.94 at F=3).

## Pre-registered verdict bands (re-banded on the substrate-meaningful DECODE metric; cosine reported as analytic reference)
- **HARD-PASS:** cleanup@1 >= 0.80 at F=3 AND cleanup capacity F* >= 10 (largest F with cleanup@1 >= 0.80).
- **MIDDLE:** cleanup@1 0.50-0.80 at F=3.
- **HARD-FAIL:** cleanup@1 < 0.50 at F=3.
- **UNKNOWN:** corpus load fails.
Recovery cosine = 1/sqrt(F) reported alongside as the analytic reference; locked cosine bar flagged to Research for re-banding.

## Substrate-product artifact (stands alone, no LLM frame)
Whether substrate atoms COMPOSE into structured representations that DECODE back to the right atoms (substrate > atom-set),
and how the substrate's clustered codebook (tw_edge_z=-2.26, uncharted regime) shifts the cleanup-capacity cliff vs the
uniform-codebook Plate/Frady-Sommer prior.
