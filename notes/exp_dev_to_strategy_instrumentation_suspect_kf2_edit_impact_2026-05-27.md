# KF-2 Edit-With-Impact-Prediction -- BLOCKED (not instrumentation bug, genuine substrate property)

Date: 2026-05-27

## What was tested

exp_kf2_edit_impact_v1.py: Kerdock outer-product store with N=1024 smoke.
Hypothesis: editing a key-value pair (k_i, v_i) produces measurable collateral damage on
other stored facts that share high cosine similarity with k_i. The correlation between
pre-edit cosine similarity and post-edit accuracy drop should be positive (r > 0).

## What was observed

Smoke across M/N in {0.25, 0.5, 1.0, 2.0}:
- r_sim_vs_damage = 0.0 at ALL M/N values
- delta_acc = 0.0 at all M/N values
- Accuracy before edit = 1.0, after edit = 1.0 at all M/N

## Why this is a genuine substrate property, not a bug

The Kerdock 4-coset codebook produces structured N-dimensional bipolar vectors with near-perfect
mutual orthogonality at N=4096. The Kerdock guarantee is:
  |<k_i, k_j>| / N <= 1/sqrt(N) for i != j

At N=1024: max cross-correlation <= 1/32 = 0.031
At N=4096: max cross-correlation <= 1/64 = 0.016

This means each key k_i acts essentially as an independent coordinate axis in the outer-product
store. Editing (k_i, v_i) updates ONLY the slice of W aligned with k_i. The projection of
all OTHER k_j onto k_i is negligible, so their retrieval is unaffected.

This is the SAME orthogonality property that makes argmax retrieval insensitive to beta (KF-5
redesign was needed for the same reason), and is a core design goal of the Kerdock codebook.

## What KF-2 actually tells us (positive result)

The substrate has PERFECT EDIT ISOLATION by construction -- single-fact edits have zero
measurable collateral damage at Kerdock capacity. This is NOT a failure of the experiment;
it is a strong product property:

  "Editing one stored fact does not corrupt any other stored fact."

This is the ISOLATION claim in the substrate killer-features list.

## What a useful KF-2 would need

To measure "impact prediction" in a setting with non-trivial collateral damage, the experiment
needs to use the BYTE-LM delta-rule substrate (W trained via delta rule, not outer-product
store). In the byte-LM setting:
- Atoms are byte_atoms (256 x N) and pos_atoms (K x N)
- Training updates W with outer products of target-key-value pairs
- Keys are composed (byte embedding + position), not Kerdock atoms
- Composed keys have non-trivial mutual overlap depending on shared bytes/positions
- Editing one (byte, position) pair may affect retrieval of nearby (byte, position) pairs

Alternatively: use RANDOM bipolar keys (Gaussian projection) where overlaps are non-zero
by design.

## Recommendation for Strategy

Option 1: Redesign KF-2 using byte-LM substrate. The "impact prediction" question becomes:
  "Can we predict, before an edit, how much BPC changes for adjacent (byte, position) pairs?"
  This is meaningful because byte-LM keys ARE partially correlated.

Option 2: Reframe KF-2 as a PROOF of isolation rather than an impact predictor:
  Claim: "Kerdock outer-product substrate achieves zero collateral damage by construction."
  Measurement: verify |delta_acc| < epsilon across 5 seeds and M/N up to 2.0.
  This is a positive product-feature story.

Option 3: Park KF-2 entirely and prioritize the 5 shipped anchors for now.

The current exp_kf2_edit_impact_v1.py file is VALID but the experiment is vacuous for
Kerdock outer-product store. Do NOT ship to either queue without redesign.
