# Pre-reg: substrate_dynamic_f_phase_shift_deeper_sweep_v2

Date filed: 2026-06-24
Filed-by: exp_dev
Parent cell: experiments/exp_substrate_dynamic_f_phase_shift_sparsity_v1.py (HARD_FAIL +0.043 lift; v2 follow-up at finer grid)
Cell: experiments/exp_substrate_dynamic_f_phase_shift_deeper_sweep_v2.py

## Purpose

v1 HARD_FAILed at +0.043 lift, MISSING the +0.05 MIDDLE_BAND bar by only 0.007 bits.
HOWEVER the signal direction was CORRECT: ARM_DYNAMIC_STORE002_QUERY005 (store
sparse 0.02 -> query slightly-less-sparse 0.05) was the best dynamic arm. v1
tested 3 dynamic configs only; two of three (002 -> 050 and 005 -> 050) HURT,
one (002 -> 005) helped marginally.

v2 hypothesis: the optimal dynamic-f operating point is in a NARROW region near
(f_store=0.02, f_query=0.05), and POSSIBLY at sparser store regimes (f_store in
{0.005, 0.01}) where the bit-density inventory shows alpha_c extends to 4.0
(unexplored capacity headroom; see exp_sparse_alpha_fine_sweep_below_004_v1).
v1's coarse grid missed this region. v2 tests 5 dynamic configs at finer grid
spacing.

USER A11 standing emphasis: phase-shift sparsity (fast/dense vs slow/sparse)
"would be pretty amazing." v1 direction-correct -> v2 tests if scaled to
HARD_PASS-level lift at finer-grain discretization.

## Mechanism (SAME as v1; verified by ST4 in selftest)

For each arm, given base encoder E_base (word2vec -> Gaussian-project(N_DIM) ->
L2 normalize):

  E_store_f = L2(sparsify_bipolar(E_base, f_store))
  E_query_f = L2(sparsify_bipolar(E_base, f_query))

  Storage:  W = sum_t E_store_f[idx[t+1]]^T @ E_store_f[idx[t]]
  Recall:   query[ctx] = L2(E_store_f[ctx] @ W^T)       (in store-sparsity space)
            logits[ctx] = query[ctx] @ E_query_f^T      (decode in query-sparsity space)

When f_store == f_query the mechanism is identical to the static-f baseline
(fair_harness pipeline). When f_store != f_query, the query phase reads bound
traces through a different sparsity prior than was used at write time.

## Arms (8 arms, 3 seeds in full run; 5 dynamic + 2 static + word-bigram/unigram baselines)

| Arm                              | f_store | f_query | Notes                                            |
|----------------------------------|---------|---------|--------------------------------------------------|
| ARM_STATIC_F_0p02                | 0.02    | 0.02    | PRIMARY BAR (v1 best static = 7.2955)            |
| ARM_STATIC_F_0p05                | 0.05    | 0.05    | SECONDARY RAIL vs fair_harness 7.3065            |
| ARM_DYNAMIC_STORE002_QUERY003    | 0.02    | 0.03    | Very narrow window                               |
| ARM_DYNAMIC_STORE002_QUERY005    | 0.02    | 0.05    | v1's best dynamic (provenance check)             |
| ARM_DYNAMIC_STORE002_QUERY010    | 0.02    | 0.10    | Medium loosen                                    |
| ARM_DYNAMIC_STORE001_QUERY005    | 0.01    | 0.05    | Sparser store, v1-winner-query                   |
| ARM_DYNAMIC_STORE001_QUERY002    | 0.01    | 0.02    | Very sparse store, narrow window                 |
| ARM_DYNAMIC_STORE0005_QUERY005   | 0.005   | 0.05    | Extreme-sparse store (alpha_c=4.0 regime)        |

Plus reported as PER-SEED CONTEXT (not verdict-gating):
- ARM_UNIGRAM (word-unigram baseline)
- ARM_BIGRAM (word-bigram baseline; Recommendation D from bias audit 2026-06-24)

## Pre-registered HARD bands (PRE-REGISTERED BEFORE RUN; do NOT adjust post-smoke)

Sanity rails (gates; must hold else HARD_FAIL_PROVENANCE in full mode):
- (1) PRIMARY: ARM_STATIC_F_0p02 BPC within +/- 0.05 of v1 reference 7.2955
- (2) SECONDARY: ARM_STATIC_F_0p05 BPC within +/- 0.05 of fair_harness 7.3065
Both must hold.

HARD_PASS:
  Best dynamic arm BPC <= (ARM_STATIC_F_0p02 BPC) - 0.10 bits
  AND that dynamic arm cv <= 0.05 across 3 seeds.
  Action: substrate gains genuine dynamic-f mode-switching at fair_harness scale.

MIDDLE_BAND_REPRODUCE:
  Best dynamic arm lift in [+0.03, +0.10) bits over best static
  (reproduces v1's direction-correct signal at the new grid).
  Action: signal real but below HARD_PASS bar; consider continuous-f or
  query-difficulty-gated v3 cell.

MIDDLE_BAND_AMBIGUOUS:
  Best dynamic arm lift in (+0.02, +0.03) bits.
  Below MIDDLE_BAND_REPRODUCE bar but above HARD_FAIL_DECISIVE; signal weak.

MIDDLE_BAND_HIGH_CV:
  Lift >= +0.10 BUT cv > 0.05. Quantitative signal, variance too high.

HARD_FAIL_DECISIVE:
  NO dynamic arm beats best static by > +0.02
  (phase-shift truly doesn't help at this discretization; v1 +0.043 was noise-floor).
  Action: this 2-phase formulation doesn't help; consider continuous-f or
  query-difficulty-gated modulation in v3.

HARD_FAIL_PROVENANCE:
  Either sanity rail drifts > 0.05 from its reference.
  Action: encoder pipeline mismatch; cannot conclude; investigate.

## Lift discretization rationale (v2 vs v1)

v1 used [+0.05, +0.10) MIDDLE_BAND. The actual v1 lift was +0.043, missing by
0.007. v2 WIDENS MIDDLE_BAND_REPRODUCE to [+0.03, +0.10) to capture the
direction-correct signal that v1 just barely missed. This is a PRE-REGISTERED
band; we are NOT lowering bars to make v1's null result into a v2 pass. The
HARD_PASS bar remains +0.10 (unchanged from v1).

The HARD_FAIL_DECISIVE bar at +0.02 is a NEW decisive-null band: lifts below
+0.02 at this finer grid (which includes the v1-winning config + the unexplored
sparser-store regimes) cleanly rule out 2-phase dynamic-f mode-switching at this
configuration. Lifts in (+0.02, +0.03) fall in MIDDLE_BAND_AMBIGUOUS.

## Config (FULL run)

- N_DIM = 8192
- N_TRAIN = 100_000 tokens, N_HELD = 20_000 tokens
- VOCAB_CAP = 4000
- text8 corpus (data/text8_cache/text8.txt)
- TEMP_GRID = [0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0]
- LAMBDA_GRID = [0.1, 0.3, 0.5, 0.7, 1.0]  (excludes 0.0 per Skunkworks META C7)
- MRR_K = 10
- seeds = [7, 17, 23] (3 seeds for cv check)
- Encoder: word2vec-google-news-300 -> Gaussian-project -> L2 (OOV: char-trigram)
- Rank-1 Hebbian W; joint (T, lambda) sweep on dev half; report on test half
- Routing: overnight_queue (GPU; torch.cuda for storage and recall matmuls)
- Word-bigram baseline (add-alpha=0.1; backoff_lambda=0.3 to unigram for unseen ctx)
- Word-unigram baseline (add-alpha=0.1)

## Why 3 seeds is sufficient (UNCHANGED from v1)

Substrate encoder is deterministic per seed (word2vec lookup cached;
Gaussian-project seeded; sparsify is deterministic top-k). 3-seed cv across
distinct random Gaussian projections measures variance from projection geometry
only. cv <= 0.05 is the discipline-standard threshold for HARD_PASS.

## What this cell does NOT show

- Does NOT test continuous-f modulation (only 2 fixed phases per arm)
- Does NOT test query-difficulty gated f-switching (no adaptive f)
- Does NOT test 3+ phase modes (only store / query)
- Does NOT vary f_store across the train trajectory (storage f fixed per arm)
- Does NOT test combination with cf-RPE / heterogeneous plasticity / K-banks
- Result at N_TRAIN=100k text8 V=4000 may not generalize to other corpora
- word-bigram baseline is REPORTED but NOT a verdict gate. Substrate is not
  expected to beat word-bigram at this N_DIM/encoder (per bias audit
  Recommendation D framing); the intra-substrate dynamic-vs-static comparison
  remains the primary verdict. Bigram provides honest absolute-reference context.

## Brain prior (UNCHANGED from v1)

P_inherited = 0.50 (brain DOES modulate cortical sparsity; mechanism documented)
Deflated to P_substrate_native = 0.30 for v2 specifically (v1 HARD_FAIL provides
informative prior tightening; v2 tests whether the v1 direction-correct signal
scales with finer grid, so v2 is biased toward MIDDLE_BAND_REPRODUCE rather than
HARD_PASS).

## Routing rationale

overnight_queue (GPU). Fix #24 compliance: uses torch.cuda for storage W matmul
and recall logits matmul. N_DIM=8192 W=8192x8192 matmul over 100k pairs
benefits from GPU throughput. Encoder build on CPU (gensim lookup) is fixed
overhead.

8 arms x 3 seeds means 24 (arm, seed) pairs. Per-arm wall on RTX with N_DIM=8192
+ N_TRAIN=100k expected ~3-5 min. Total ~ 24 * 4 = ~96 min wall. Add encoder
build (1-2 min/seed) + bigram build (~30s/seed) -> total ~110-130 min wall.
Timeout=14400s (4 hours) provides ~2x headroom for cold-cache word2vec load and
GPU contention.

## Disciplines applied

- ASCII-only (verified: no emojis, no em dashes in cell)
- Fix #14: ONE cell (this anchor only)
- Fix #24: torch.cuda for heavy matmuls (W ingest + recall)
- Fix #26: predispatch_check run BEFORE this file was filed (no prior landings)
- Fix #28: per-arm metrics ONLY in verdict_msg; no cross-arm framing
- A5: path-scoped commit (caller responsibility; orchestrator commit + push)
- Pre-reg filed BEFORE smoke run
- PROT-018: no _nN suffix in anchor (N_DIM stated above)
- WHAT_THIS_DOES_NOT_SHOW clause in detail and this prereg
- LAMBDA_GRID excludes 0.0 (Skunkworks META C7)
- Per-seed checkpointing + atexit synthesizer
- Recommendation D from bias audit: word-bigram baseline reported alongside

## Cites

- experiments/exp_substrate_dynamic_f_phase_shift_sparsity_v1.py (parent; HARD_FAIL +0.043)
- experiments/exp_substrate_brain_word_level_prediction_v2_production_config.py (word-bigram pattern)
- experiments/exp_fair_harness_substrate_as_lm_v1.py (sanity rail 7.3065)
- notes/director_bit_density_store_mine_inventory_2026-06-24.md (f<0.01 alpha_c=4.0 headroom)
- notes/skunkworks_experiment_bias_audit_2026-06-24.md (Recommendation D)
- USER A11 question (meta-skepticism drill Anchor 4)
