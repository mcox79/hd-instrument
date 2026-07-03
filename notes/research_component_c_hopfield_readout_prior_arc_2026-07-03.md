# Research: Component-C modern-Hopfield readout HF -- empirical prior-arc mining (5x drill 3/5)

## (a) HEADLINE

The substrate's own prior work does NOT predict that modern-Hopfield readout is
fundamentally unsuited to this task -- it predicts the opposite (dense Hopfield at a
correctly-scaled beta should track cosine cleanup within noise). What the prior arc DOES
surface is a concrete BETA/TEMPERATURE-SCALING BUG in the Component-C cell itself: it
reuses beta={4,8} from a prior cell that operated on RAW un-normalized dot products
(`exp_modern_hopfield_replication_gpu_v1_n8192`, N=1024, perfect recall=1.0 at both
betas), but Component C's formula is `softmax(beta * cos(q,K) / sqrt(N)) @ K` -- cosine
is ALREADY bounded to [-1,1], and dividing by an EXTRA sqrt(N)=45.25 (N=2048) crushes the
effective temperature far below the discriminative regime. The cell's own docstring
(line 34-37) states that with equal-norm patterns, ranking by attention weight should be
IDENTICAL to cosine argmax -- yet observed Hopfield r@1=0.010 is statistically
indistinguishable from the RANDOM baseline r@1=0.010, while cosine on the SAME embeddings
scores r@1=0.103. This is not "geometry mismatch," it is the one-step attractor blend
`y = softmax(...) @ K` collapsing to the corpus centroid because the softmax is
over-flattened by the redundant sqrt(N) division -- then re-ranking by cos(y, K_i) picks
up corpus-background structure, not query-specific signal. This is a formula bug, testable
and fixable before any composition (Option A) or storage-lever (Option 2) work is
justified.

## (b) Cheap decisive test

Re-run the SAME Component-C smoke cell (N=2048, 3 seeds) with two isolated formula
variants, holding everything else fixed:
1. `VARIANT_NO_SQRT_N`: drop the `/sqrt(N)` term -- score = `beta * cos(q,K)` directly.
2. `VARIANT_BETA_RESCALED`: keep `/sqrt(N)` but set `beta_eff = beta * sqrt(N)` (i.e.
   beta={4,8} -> beta={181, 362} at N=2048) so the net temperature matches what the
   replication cell validated.
Compare Hopfield r@1/r@5/r@10 in both variants against the existing cosine arm (r@5=0.16)
and trigram floor (r@5=0.28). Cost: <5 min CPU, no new corpus, no new encoder --
pure post-hoc formula patch re-run on cached embeddings if available, else re-fit is
already 3.5s wall per the landed metrics.

## (c) Falsifiable predictions

HARD-PASS (bug hypothesis CONFIRMED -- Hopfield mechanism is fine, formula was broken):
- Either variant lifts Hopfield r@5 to within 0.03 of the cosine arm's r@5=0.16 (i.e.
  r@5 >= 0.13), recovering the "ranking should equal cosine argmax at equal-norm" identity
  the cell's own docstring claims.
- r@1 rises measurably above the random-baseline r@1=0.01 (>=0.05, a 5x lift), showing the
  attractor step is no longer collapsing to centroid.

HARD-FAIL (bug hypothesis REFUTED -- deeper geometry problem, Option A/2 back on table):
- Both variants stay within 0.01 of the current r@5=0.05 (no material change) -- would mean
  the failure is NOT primarily a temperature-scaling artifact and the storage geometry
  (non-equal norm, correlated real embeddings vs random prior-cell patterns) is the
  binding constraint after all.
- Rescaled beta destabilizes (softmax saturates to single nearest-neighbor everywhere,
  r@1 matches cosine but r@5/r@10 collapse below cosine's r@5/r@10) -- would indicate the
  attractor-blend re-ranking step (cos(y,K_i) rather than cos(q,K_i) directly) is itself
  the wrong readout for this embedding, independent of temperature.

MIDDLE-BAND: partial lift (r@5 in [0.06, 0.12]) -- temperature scaling is A factor but not
the whole story; queue a second drill on whether concept_hds are actually equal-norm
(the docstring's stated precondition) before re-judging the mechanism.

## (d) Cross-thread synthesis with prior substrate evidence

1. **`data/exp_modern_hopfield_replication_gpu_v1_n8192/metrics.json`** (May 2026,
   G6_MIDDLE_BAND, verdict_msg "PARTIAL_BETA_ROBUST 0/2 beta>=N"): tested beta={4,16} on
   N=1024 RANDOM sparse-bipolar patterns, RAW dot-product energy (not cosine-then-/sqrt(N)).
   recall=1.0 at every (M,beta) cell tested (M<=512). Task class = capacity replication on
   i.i.d. random patterns, NOT semantic retrieval among correlated real embeddings.
   Transferable lesson: perfect recall at these exact beta CONSTANTS was achieved under a
   DIFFERENT normalization convention (raw dot product, not bounded-cosine/sqrt(N)) --
   reusing the numeric constants 4/8 across conventions without re-deriving beta_eff is the
   proximate bug candidate. Skunkworks' "related-but-different-task" flag was correct on
   task class but the more load-bearing transfer is the SILENT CONVENTION MISMATCH.

2. **`data/exp_encoder_cocktail_composition_v1_seed_7/metrics.json`** (HARD_FAIL,
   HF_CROSS_ENCODER_ZERO): cross_recall=0.004 when FHRR queries hit sparse_bipolar keys,
   vs 0.31-0.43 for same-family pairs. This is direct substrate evidence AGAINST naive
   Option-A-style composition of heterogeneous vector-family geometries without an
   explicit alignment/calibration step -- structurally the same failure SHAPE as
   Component C (a geometry/scale mismatch silently producing near-chance output while
   same-family baselines look fine). Reinforces: check normalization/scale compatibility
   FIRST, in both the Hopfield-beta case and any future Option-A composition.

3. **`notes/exp_dev_handoff_research_drill_sparse_bipolar_depth_enc1_composition_2026-06-23.md`**
   (ENC1, HARD_FAIL all 5 arms incl. ARM_SPARSE_FANIN_K5_N4096=0.018 at sigma=1.5,
   Shannon-floor classification): prior attempt to rescue a cleanup/composition ceiling via
   sparse-bipolar storage swap FAILED under noise. This tempers Option 2 (storage-lever
   swap) as a default rescue -- it is not a free win and has NOT rescued a structurally
   similar composition problem before.

4. **`notes/research_modern_hopfield_capacity_retrieval_crossover_2026-06-16.md`** (2x
   research, P_deflated ~0.10-0.15 for sparse-Hopfield advantage): predicted dense Hopfield
   at Ramsauer tune-free beta should be WITHIN 0.5pp of naive flat-cosine cleanup in the
   well-separated regime (its own HARD-PASS band). Observed Component-C gap is 11pp in the
   WRONG direction (Hopfield worse, not equal) -- this VIOLATES that note's HARD-PASS band,
   which is itself evidence the failure is a configuration/calibration artifact rather than
   a validated theoretical prediction (the literature-grounded prediction says they
   should roughly match; a large violation points at implementation, not mechanism).

5. Null results (searched, not found in substrate): no prior note or metrics file uses the
   terms "magnitude weighted prototype," "confidence weighted storage," or "attention over
   unnormalized store" verbatim. No prior WordNet-retrieval-only baseline (pre-brain-analog
   concept_encoder) was found -- the only WordNet substrate work located is the STEP-B
   ingest scoping brief (`exp_dev_to_skunkworks_research_STEP_B_WordNet_scoping_brief...
   2026-06-17.md`), which is about ingesting WordNet as a LEXICON reference corpus, not a
   retrieval-accuracy baseline experiment. This is a genuine coverage gap, not a refuted
   direction.

## (e) Substrate-product implications

If the beta/temperature-scaling bug is confirmed by the cheap decisive test above, the
practical product implication is: modern-Hopfield readout should NOT be marked as a dead
end for concept-retrieval work. The mechanism has substrate precedent (replication cell,
perfect recall) and literature precedent (should roughly match cosine in well-separated
regimes) both pointing toward "fixable config," not "wrong mechanism." Conversely, this
also means Skunkworks' May-2026 cell should be re-flagged: its beta={4,16} constants are
NOT portable to bounded-similarity formulas without rescaling by the normalization factor
in use -- any future re-use of that cell's beta values elsewhere in the substrate should
carry an explicit unit/convention check. For the immediate decision in front of Skunkworks
(Option A composition vs Option 2 storage-lever): dispatch the cheap decisive test FIRST;
it is one cell re-run at near-zero cost and directly discriminates between "fix the
formula" (verdict IV below) vs "the mechanism genuinely doesn't fit this task" (would
revive verdict II).

## (f) Chain-of-reasoning verdict

**(IV) Prior arc surfaces a THIRD option not yet considered: FIX THE BETA/TEMPERATURE-
SCALING CONVENTION MISMATCH before dispatching either Option A (v3 composition) or
Option 2 (storage-lever swap).** The substrate's own May-2026 replication cell and the
2x capacity-retrieval-crossover research note both predict dense-Hopfield-at-correct-beta
should be competitive with cosine cleanup, not catastrophically worse. The observed
near-random r@1 (0.010, indistinguishable from random baseline 0.010) combined with the
cell's own docstring claim that equal-norm ranking should equal cosine argmax is the
signature of an over-flattened softmax (attractor blend collapsing to centroid), most
plausibly caused by dividing already-bounded cosine similarity by an extra sqrt(N)=45
factor while reusing beta constants tuned for a different (raw dot-product) formula in a
prior cell. This is cheap and fast to test in isolation and should be run BEFORE either
Option A or Option 2 is queued, since a positive result there would make both of those
options premature.

P_deflated = 0.55 (raw confidence ~0.75 in the beta/temperature-scaling diagnosis, per
[[feedback-lit-scan-calibration-penalty]] deflated 0.20 for not yet having re-run the
isolated formula-patch test).

## Citations (verified count)

4 substrate-internal artifacts read and verified in full (metrics.json / note content, not
summary text): `data/exp_modern_hopfield_replication_gpu_v1_n8192/metrics.json`,
`data/exp_encoder_cocktail_composition_v1_seed_7/metrics.json`,
`notes/exp_dev_handoff_research_drill_sparse_bipolar_depth_enc1_composition_2026-06-23.md`,
`notes/research_modern_hopfield_capacity_retrieval_crossover_2026-06-16.md`. Plus 1 direct
source-code read (`experiments/exp_substrate_concept_encoder_component_C_modern_hopfield_readout_2026-07-03.py`,
lines 34-37, 112-115, 417-465) confirming the formula and beta-constant provenance. 0
external/lit citations (empirical prior-arc mining task, no external search authorized).
