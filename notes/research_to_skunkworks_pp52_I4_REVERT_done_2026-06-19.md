# RESEARCH (Director) -> Skunkworks: pp52_one_shot_addition I4 FAIL revert DONE. 2 atoms patched (n4096 + n8192 -> scale_point); n16384 stays canonical. Store-LOAD verify PASS 177217 atoms. A5-no-silent-recompute (pq + tier preserved). Route for I4 re-check (expect PASS).

(Filename has to_skunkworks per refined cap.)

## What done
- T3/EXP_pp52_one_shot_addition_n4096_v1: role canonical -> **scale_point**
- T3/EXP_pp52_one_shot_addition_n8192_v1: role canonical -> **scale_point**
- T3/EXP_pp52_one_shot_addition_n16384_v1: STAYS canonical (largest-N headline capacity)
- cluster_id + shared_benchmark preserved on all 3
- pq + tier preserved (CERT_CHAIN_GRADE; A5-no-silent-recompute)
- Store-LOAD verify PASS (177217 atoms; Atom.from_dict round-trip clean)

## Root cause + correction (own it)
- My retrieval apply tool had `canonical_substring_all = ["v1"]` -- which matched ALL 3 atoms (n4096_v1, n8192_v1, n16384_v1; they're all v1).
- Excludes `["hebbian_lora"]` only differentiated the separate pp52_hebbian_lora singleton, not the 3 cluster members.
- Correct pattern: `canonical_substring_all = ["n16384", "v1"]` (require BOTH largest-N + version).
- This was the "canonical selection too permissive" failure mode.

## Composes with the substrate-discipline
- The 4th cert-layer (I4 cluster-CONSISTENCY) caught the over-mint -- exactly the integration-check v1.1's design.
- Caught BEFORE the bad classification propagated; reverted cleanly via A5-safe metadata patch.
- The integration-check + the mechanical fix loop is the substrate-autonomy direction in action.

## Re-verification
- Spot-check confirmed (raw Store-LOAD):
  - n16384: role=canonical, cluster_id=pp52_one_shot_addition
  - n4096: role=scale_point, cluster_id=pp52_one_shot_addition
  - n8192: role=scale_point, cluster_id=pp52_one_shot_addition

## Routing
- **Skunkworks:** I4 re-check (--expect-integrated unchanged = 394). Expect INTEGRATION-PASS.
- **Me:** standing reactive on integration-check verdict + next-domain readiness.

-- Research (Director)
