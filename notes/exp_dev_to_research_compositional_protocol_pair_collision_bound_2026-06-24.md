# exp_dev_to_research: compositional protocol is pair-collision-bound, NOT mechanism-bound

Date: 2026-06-24
From: exp_dev
To: research (primary); cc: skunkworks, orchestrator
Re: substrate_compositional_generalization_CORRECTED_v1 -- HALTED at smoke gate

## Headline finding (pre-flight smoke caught a deeper issue than the fact-finder identified)

The corrected cell smoke verdict is `HARD_FAIL_DEEPER_ISSUE` with all 4 arms returning IDENTICAL numbers:

```
ARM_BROKEN_SPARSE_NO_NORM:     in_dist=0.250  holdout=0.000  (chance 0.125)
ARM_DENSE_HRR_NORMALIZED:      in_dist=0.250  holdout=0.000
ARM_FHRR_NORMALIZED:           in_dist=0.250  holdout=0.000
ARM_SPARSE_HRR_NORMALIZED:     in_dist=0.250  holdout=0.000
```

At smoke config (N_DIM=1024, n_subj=n_obj=8, coverage=0.50 -> 32 train / 32 holdout pairs).

Mechanism-side sanity:
- 3-disjoint-pairs unit test (1 binding per subject): DENSE/FHRR/SPARSE_NORM all 100% recall. Mechanisms work.
- HRR involutive on dense unit-norm + FHRR involutive on complex-phase: confirmed.

The 0.250 in_dist ceiling is NOT a mechanism failure -- it's a PROTOCOL CEILING.

## Why 0.250 is the structural ceiling (the missing analysis from the fact-finder)

The brain-aligned shotgun ARM 2 protocol binds:
```
bank = sum_{(i,j) in train} bind(subj[i], obj[j])  # train = 200 pairs / 32 in smoke
```

With n_subj=8 and 32 train pairs, AVERAGE pairs-per-subject = 4. So when we
`rec = unbind(bank, subj[i])`, we get:
```
rec ~= sum_{j : (i,j) in train} obj[j]  +  crosstalk
```
i.e. a superposition over the ~4 objects that were ever paired with subj[i].

The `argmax cosine(rec, OBJ codebook)` returns ONE obj -- it can match at most 1 of those ~4 trained
pairs. Expected in_dist = 1 / (pairs_per_subj) = 1/4 = 0.25. That is exactly what we see across ALL
4 arms; the mechanism choice doesn't matter when the protocol is upper-bounded.

The brain-aligned shotgun original ran at n_subj=20, 200 train -> ~10 pairs-per-subj -> ceiling 0.10.
Its in_distribution_top1=0.10 matches this exactly. The fact-finder's "sparse-bipolar config bug" was
ONE contributing factor; the PROTOCOL is the dominant ceiling.

For HOLDOUT pairs (subj, obj) where the binding was never put in the bank: argmax recovers a TRAINED
obj for that subj, so holdout cannot match the heldout obj target (which has zero presence in the bank).
Holdout=0 is mathematically forced.

## What this means

1. **Protocol-as-written doesn't measure compositional generalization.** It measures
   "1-of-N-trained pick" where N = avg-pairs-per-subj. The "right config" can't get past 1/N because
   each subj's unbind result is a superposition, not a single target.

2. **The fact-finder's diagnosis is partially correct but incomplete.** Per-bind normalization fixes the
   bank L2 blowup (a real bug), but doesn't change the protocol ceiling. A normalized DENSE arm at the
   FULL config (n_subj=20, 200 train, N=4096) would land at ~0.10 in_dist for the SAME reason the
   broken sparse arm did -- the dominant constraint isn't mechanism, it's pairs-per-subj.

3. **Substrate compositional generalization needs a DIFFERENT protocol.** Plate's canonical HRR
   demonstrations use ONE role-filler binding per "frame" (not many objs per subj in superposition).
   Cross-frame compositionality is testing whether `bind(role, filler)` lets you SWAP the filler --
   not whether you can resolve which of N objs a subj was paired with.

## Pre-flight verdict

I am HALTING the dispatch. Shipping this cell at FULL config would land HARD_FAIL_DEEPER_ISSUE for the
PROTOCOL reason, not the substrate-aliveness reason. That would (a) consume CPU cycles for a
predictable no-info result and (b) get mis-interpreted as "substrate broken on compositional gen" when
the real finding is "this measurement is mis-specified".

## Recommended next-step protocol (for research drill)

A proper HRR compositional-generalization test would look like:

```
# Test: substrate can compose role-filler bindings into NEW frames
roles = {SUBJ, VERB, OBJ}  # 3 role keys
fillers = {Alice, Bob, ate, sang, apple, song}  # 6 filler keys

# Training frames: each frame is ONE bind per role
frame1 = bind(SUBJ, Alice) + bind(VERB, ate) + bind(OBJ, apple)
frame2 = bind(SUBJ, Bob) + bind(VERB, sang) + bind(OBJ, song)
# ... K training frames at 1 binding per role per frame

# Query: unbind(frame_i, SUBJ) -> should recover Alice/Bob/etc cleanly
# COMPOSITIONAL GEN: build NEW frame using only TRAINED bindings:
#   frame_new = bind(SUBJ, Alice) + bind(VERB, sang) + bind(OBJ, apple)
# and test: unbind(frame_new, OBJ) -> apple (never seen this filler in OBJ position before)
```

This is OG-Plate HRR composition: substrate can recombine ROLES with FILLERS it has seen in OTHER
positions. THAT'S the brain-canonical "compositional" claim, and it's what existing
`exp_contextual_encoding_hrr_PRODUCTION_held_out_v1` partially demonstrated at lift=+0.212.

I have NOT designed this cell -- that's a research-drill task. Calling out the work item:

- Cell name: `substrate_compositional_role_filler_recombination_v1` (placeholder).
- Discriminator: holdout (role, filler) combinations the substrate never saw bound in that role.
- Sanity floor: same-frame role-filler unbind > 0.70 (one binding per role per frame; trivial recall).
- HARD_PASS: novel-recombination unbind > 0.50 across heldout fillers.
- Cite: Plate 1995 canonical HRR role-filler example; existing contextual_encoding HRR lift evidence.

## Cell artifacts (cleanup decision: KEPT for audit)

- `experiments/exp_substrate_compositional_generalization_CORRECTED_v1.py` (smoke passes; full would
  land HARD_FAIL_DEEPER_ISSUE for protocol reason)
- `preregs/2026-06-24_substrate_compositional_generalization_CORRECTED_v1.md`
- `data/exp_substrate_compositional_generalization_CORRECTED_v1_smoke/metrics.json`

Not committed to git yet (pending Research disposition).

## Discipline notes

- Pre-flight smoke gate caught the issue in 6s wall vs ~5min full-config wall. Smoke-first discipline
  saved a misleading land.
- Fix #28 verify-per-arm: I read per_arm metrics (not just verdict_msg). All 4 arms IDENTICAL is the
  smoking gun the per-arm view exposed; verdict_msg summary would have read "HARD_FAIL_DEEPER_ISSUE"
  without that detail.
- Sanity floor (in_dist > 0.70 mandatory) worked as designed -- it caught the structural ceiling
  rather than letting a 0.250-holdout-0.000 result get framed as a "substrate is not compositionally
  alive" finding.

## Honest scope

This finding does NOT overturn the USER intuition that the substrate is compositionally alive. The
existing `exp_contextual_encoding_hrr_PRODUCTION_held_out_v1` ARM_BIND_RECENT_5 lift=+0.212 result is
still positive evidence for HRR compositional capability. This finding ONLY rules out that the
brain-aligned-shotgun ARM 2 protocol can ever be a clean discriminator -- the protocol's structural
ceiling is too low to distinguish "mechanism broken" from "mechanism working".

Cites:
- USER 2026-06-24 compositional reasoner product story.
- Fact-finder note (partially superseded by this finding):
  `notes/director_compositional_failure_USER_test_wrong_VSA_modality_inventory_2026-06-24.md`.
- Brain-aligned shotgun ARM 2 partial: `data/exp_substrate_brain_aligned_aliveness_shotgun_v1/partial_metrics_s7.json`.
- Existing HRR-can-generalize: `data/exp_contextual_encoding_hrr_PRODUCTION_held_out_v1/metrics.json`.
- Plate 1995 canonical HRR role-filler composition.
