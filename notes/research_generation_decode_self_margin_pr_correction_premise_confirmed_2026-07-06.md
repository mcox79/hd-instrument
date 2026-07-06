# Prep-drill: generation-decode self-margin via PR-correction -- PREMISE CONFIRMED, dispatch-ready

Date: 2026-07-06. Director main-thread prep drill (off-disk verification, zero new trials), run while
Tier-2 retrieval-coverage + Tier-3 FP-fix agents were in flight. De-risks the NEXT self-margin rung:
extend the exact self-margin self-prediction from COMPREHENSION (order-recovery) to GENERATION (decoder).

## The premise that had to hold (and does)
The comprehension self-margin was revived by the PARTICIPATION-RATIO correction: the effective competitor
count is n_comp = PR(V)-1 (PR ~16-29, the effective rank of the codeword Gram) NOT V-1 ~999, because the
GSBC codes are correlated JL-projections. PR-correction is a property of the CODEWORD GRAM GEOMETRY, so it
transfers to any decode that competes the SAME codewords in an argmax/order-statistic.

VERIFIED off-disk that generation and comprehension share that geometry:
- exp_generation_decoder_gsbc_native_blocklocal_v1.py: N_DIM=8192, F_SPARSE=0.02, block-local sparse
  bipolar codebook via _blocklocal_codebook_gsbc, k = round(F_SPARSE*bs). Decode = resonate() over
  [pos_book, lex_book] then argmax q @ lex_book.t() -- an order-statistic over the V GSBC lex codewords.
- exp_comprehension_order_recovery_pr_corrected_margin_v1.py: N_DIM = base.N_DIM = 8192, BS = 1024,
  K_LOCAL = round(base.F_SPARSE*BS) with the in-code comment "== GSBC codebook k, ~20"; imports
  base._active_cb (the SAME block-local codebook builder). participation_ratio(codewords) = the correction.
=> SAME codebook construction, SAME competitor set, SAME order-statistic collapse family. Premise holds.

## Mechanism match
Generation decode collapse = the extreme-value order statistic (Gauss-Hermite 64-pt, already CG'd for
RNS/FHRR/reasoning-depth) over the correlated GSBC lex codewords => n_comp = PR(V)-1 is the right
effective competitor count, identical to the comprehension fix.

## HONEST expectation (do not oversell)
Comprehension landed MIDDLE_BAND at FULL, not CG: the PR-corrected prediction was genuinely unbiased
(mean_ratio ~1.007, ~2x tighter than naive-V) BUT the naive-V baseline turned out NOT-biased-enough at the
FULL regime, so PR's ADVANTAGE-over-naive shrank below the accept-boundary. Expect the same failure mode
to be the risk for generation. THE HOPEFUL ANGLE: the generation decoder runs at HIGHER vocab (a highvocab
RNS/CRT sibling exists, exp_generation_decoder_rns_crt_highvocab_v1) where the V-1-vs-PR(V) gap is LARGER,
so naive-V should over-predict MORE strongly at generation's FULL regime -> PR-correction's edge could be
cleaner than comprehension's. Genuinely uncertain: P_deflated ~0.4-0.5 for CG, ~0.8 for at-least-MIDDLE.

## Dispatch recipe (ready after Tier-2 / Tier-3 land)
- NEW cell: predict the generation decoder's decode-collapse boundary vs (V, D) using the GH64 extreme-value
  order statistic with n_comp = PR(V)-1, reusing the comprehension PR machinery (participation_ratio,
  _independent_codebook control) against the generation decoder's OWN codebook + resonator decode.
- Pre-reg bands as PR-corrected-UNBIASED vs NAIVE-V-OVER-predicts (the "beat loose 1.5x" gate is
  unreachable-by-construction here, same as comprehension -- do NOT reuse it). Add the independent-codebook
  control (matched V/bs/k, decorrelated) so a clean firing control separates correlation from tail-shape.
- Multi-seed (>=5). Smoke local; FULL to remote_cpu_queue (referent-gate FIXED this session). Honestly
  accept MIDDLE if the naive baseline is again not-biased-enough at generation's FULL regime.
- FRAMING: monitor-not-control (predicts its own decode reliability; never edits codebook/decoder). Narrow
  glass-box step, not fluent-language, not self-improvement.

## Where this sits
Self-margin family currently = 3 CHAIN_GRADE (RNS decode / FHRR capacity / reasoning-depth chain-survival)
INTERIOR + comprehension MIDDLE (PR-revived) on the language FRONTIER. This drill makes the GENERATION-side
extension dispatch-ready. If it lands, the self-margin generalization spans perception(encoder-bounded) ->
comprehension -> generation across the GSBC/language substrate, not just the orthogonal-codebook interior.
Composes with reference_crt_residue... and research_sub_gaussian_tail_self_margin_revival_participation_ratio_2026-07-06.
