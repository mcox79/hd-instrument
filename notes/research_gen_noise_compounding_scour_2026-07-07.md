# Research: fast targeted scour -- prior verdicts on predictive generation + noise-compounding (Stage-4 build guard)

**Date:** 2026-07-07. **Type:** Targeted internal scour (no cell dispatch, no lit-scan sub-agents -- corpus-only,
time-boxed). **Trigger:** guard the Stage-4 generation build against re-treading already-concluded ground.

## HEADLINE

**The exact question this scour was sent to answer was already fully answered TODAY, twice over, by
`notes/research_brain_predictive_generation_mechanism_2026-07-07.md` (+ its exp_dev companion
`notes/research_brain_predictive_generation_predict_residual_build_spec_2026-07-07.md`) and its sibling
`notes/research_stage4_generation_load_bearing_gap_and_gpu_probe_2026-07-07.md`, both of which sit on top of
`notes/research_noise_compounding_bound_deep_mechanism_2026-07-07.md`'s regenerative-repeater framing.** This note
does not re-derive that work -- it verifies-on-disk that it exists, tabulates the 4 underlying generation cells
those notes are built on, and gives the Director the one-line pointer set needed to route straight to the build
without re-running the scan.

## Generation cells -- prior verdicts (verified on disk, data/exp_*/metrics.json)

| Cell | Verdict | Key metric | Failure reason (from verdict_msg) |
|---|---|---|---|
| `exp_n2_context_depth_hd_binding_v1` (FULL, 3 seeds) | HARD_FAIL | bpc K=1:5.00 -> K=2:5.05 -> K=3:5.18 (token_gain negative both steps; concept_top1 barely moves +0.01-0.02) | "depth provides no benefit (best_gain=0.000 bits < 0.02 threshold). HD-binding does not capture higher-order structure beyond K=1 / fully floor-masked." Raw HD-binding context accumulation gets WORSE with depth. |
| `exp_n5_trigram_concept_lm_v1` (FULL, 3 seeds) | HARD_FAIL | TRIGRAM_HRR bpc=6.86 vs BIGRAM_BASELINE bpc=4.95 (depth_gain=-1.89 bits); +backoff arm only partially recovers to bpc=6.62, still far above the 4.70 MIDDLE-band ceiling | "best trigram bpc=6.622 > 4.700 (MIDDLE upper)." HRR trigram binding is strictly worse than the bigram baseline it's supposed to extend. |
| `exp_substrate_direct_gen_lm_2ndorder_trigram_v2_n8192_gpu` (FULL, 3 seeds, N=8192) | MIDDLE_BAND | single_ppl=62.1, ensemble_ppl=43.1, bigram_count_ppl=55.8, trigram_count_oracle_ppl=20.4 | "ensemble beats bigram-count but ppl>=20." Ensembling helps and beats the bigram-count baseline, but stays far from the trigram-count oracle ceiling -- this is the ONE cell in the family that shows ANY positive signal, and it's the cell the two 2026-07-07 build notes above target for the next arm. |
| `exp_substrate_direct_gen_lm_wikitext_trigram_v3_n8192_gpu` (SMOKE only, 2 seeds, N=512) | HARD_FAIL | single_ppl=14.2, ensemble_ppl=13.5, bigram_count_ppl=9.3, trigram_count_oracle_ppl=6.6 | "ensemble does NOT beat bigram-count" -- at this (smaller/different corpus) scale even ensembling fails to clear the bigram-count bar. |

Net: **3 HARD_FAIL + 1 MIDDLE_BAND** across the 4 generation cells. The one bright spot (2ndorder-trigram GPU
cell) is a MIDDLE_BAND, not a pass, and it's exactly the cell the two same-day build notes already propose
extending with `CLEANUP_PER_STEP` and `PREDICT_RESIDUAL_TD` arms.

## Accumulated noise-compounding wisdom (from `research_noise_compounding_bound_deep_mechanism_2026-07-07.md`)

Reasoning-depth chains (multi-hop) survive compounding because each hop hard-resets to a fixed EXTERNAL
codebook/ground-truth alphabet -- a textbook **digital regenerative repeater**: per-hop error stays close to
i.i.d. because stale noise is discarded at every hop, not because noise doesn't occur. Reset-per-hop chaining
survives; self-referential/no-reset chaining does not (resonator/comparator family, already documented as the
HURTS-noisy-readout side of the CRT cross-cell law). Generation is diagnosed by the 07-07 predictive-generation
note as a genuinely HARDER case than reasoning-depth: there is no external ground-truth codebook to reset against
mid-generation (the next token is itself unknown), so a pure hard-reset repeater is not directly available --
which is why that note's build recommendation adds a SECOND, complementary mechanism (predictive-residual
encoding, i.e. inject only the prediction error per step, not the raw token) on top of the CA3-style
per-step-cleanup repeater, rather than relying on cleanup alone.

## Decisive question 1: did we already test per-step-cleanup on generation, and conclude capacity-ceiling-vs-noise-compounding?

**No -- per-step cleanup on generation is PROPOSED, not yet run.** The 4 cells above never included an
attractor-cleanup step inside the generation loop; all 4 accumulate raw (or HRR-bound) context without any
per-step re-clean. `CLEANUP_PER_STEP` is the already-queued-but-not-yet-executed next GPU arm on the
2ndorder-trigram cell (per `research_stage4_generation_load_bearing_gap_and_gpu_probe_2026-07-07.md`), and
`PREDICT_RESIDUAL_TD` is its proposed sibling arm (per the predictive-generation note). Neither has landed a
metrics.json yet as of this scour. So: **CA3-cleanup-on-generation is NOT a retread -- it is queued but unrun.**
The capacity-ceiling-vs-noise-compounding question is explicitly left OPEN and sequenced: the decision table in
`research_brain_predictive_generation_mechanism_2026-07-07.md` Section 3 says a HARD_FAIL on cleanup-alone
should redirect to a capacity-ceiling branch (disjoint-block/frame-slot context encoding), not conclude
noise-compounding is unfixable -- that branch-point has not yet been reached because the cleanup arm hasn't run.

## Decisive question 2: is predictive-coding / successor-representation genuinely untried?

**Predictive coding: partially tried, but only as a SEQUENCE-COMPRESSION mechanism, never as a
generation/context mechanism.** `T3/EXP_lap2_9_predictive_coding_cpu_v1` (HARD_PASS, LEGACY_EXCERPT,
PRE_SUBSTRATE_BUILD era) tested "store transition residuals not full items" for compression/reconstruction on a
Markov sequence over a small transition codebook (recall>=0.85 at 0.35x bits) -- a genuine, positive, on-disk
precedent for the residual-injection PRINCIPLE, but it is a pre-substrate-build, reconstruction-only cell, not a
generation cell, and it predates the current substrate encoder entirely. It does NOT test TD-bootstrapped
learning or generation-loop context accumulation.

**Successor representation: genuinely untried as an implementation.** No atom or note shows an SR/TD-bootstrap
cell ever built or run on this substrate -- only the design-stage docs
(`design_stage2_concept_encoder_spoke1_predictive_coding_competitive_allocation_2026-07-02.md` and siblings,
which are encoder-side WTA/competitive-allocation designs, not generation-context designs) and today's
mechanism-grounding note propose it. **So: predictive-coding-as-residual-compression has ONE old positive
precedent (pre-substrate); TD-bootstrapped successor-representation-on-`W_hetero` is genuinely novel -- exactly
as the 07-07 build spec already states.**

## Guiding takeaway for the Stage-4 build

Do not re-scan; route straight to execution. The full analysis, ranked mechanism table, composed pseudocode,
pre-registered HARD-PASS/HARD-FAIL bands, and exp_dev anchor already exist in
`notes/research_brain_predictive_generation_mechanism_2026-07-07.md` +
`notes/research_brain_predictive_generation_predict_residual_build_spec_2026-07-07.md`. The correct next action
is dispatching `CLEANUP_PER_STEP` and `PREDICT_RESIDUAL_TD` as sibling arms on the SAME already-GPU-proven cell
(`exp_substrate_direct_gen_lm_2ndorder_trigram_v2_n8192_gpu.py`, MIDDLE_BAND baseline already on disk), per the
decision-sequencing table those notes already specify -- this scour's only new contribution is confirming (a)
neither arm has landed yet (not a retread), (b) the 3 HARD_FAIL / 1 MIDDLE_BAND prior verdicts are the correct
and complete set of prior generation attempts (no missed cell), and (c) SR/TD-bootstrap-on-`W_hetero` is
confirmed genuinely novel on this substrate.

## Substrate-product implications

If exp_dev ships the two sibling arms and either or both land HARD_PASS: Stage-4 generation gets its first
positive-signal context mechanism, with a principled brain-grounded explanation (repeater + differential encoder,
not one mechanism). If both HARD_FAIL: the pre-committed redirect (disjoint-block/frame-slot context encoding,
i.e. treat context as a capacity problem not a noise-accumulation problem) is already named and ready, so no new
research cycle is needed even in the negative case -- the fallback lever is already on file.

## Citations (verified count this cycle)

0 external citations this cycle (pure on-disk/internal scour per task scope; all neuroscience citations are
carried by reference from the same-day notes cited above, already independently verified there -- 19
web-verified + 11 training-recall-flagged, per that note's own citation ledger).
