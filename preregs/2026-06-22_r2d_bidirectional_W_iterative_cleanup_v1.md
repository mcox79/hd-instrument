# Pre-registration: r2d_bidirectional_W_iterative_cleanup_v1

**Author:** Exp-Dev
**Date:** 2026-06-22
**Anchor:** `r2d_bidirectional_W_iterative_cleanup_v1`
**Cell:** `experiments/exp_r2d_bidirectional_W_iterative_cleanup_v1.py`
**Driver:** Research 3x-revival drill 2026-06-22 (notes/research_multihop_3x_revival_beyond_calibration_drill_2026-06-22.md); r2c (exp_r2c_conformal_LLR_compound_v1) HARD_FAIL with K-decay signature CONFORMAL_FISHER 1.899x@K=2 -> 1.448x@K=4.

## Headline

r2c showed that the calibration-stack hypothesis is EXHAUSTED: CONFORMAL_FISHER (the best calibrator) reached 1.899x at K=2 but DECAYED to 1.448x at K=4. The K-decay slope (~24%) is the forward-only iteration noise-compounding fingerprint per Wang 1990 BAM stability + 2025 Modern Hopfield survey (arxiv 2507.06211). Forward-only error variance grows ~sqrt(K); bidirectional ~O(1) under symmetric conditions. The substrate's W is heteroassociative (forward-only); composing with W.T (backward) at every cleanup step is the noise-stable form.

This cell tests 6 chain-mechanism arms on the SAME r2c harness (W, R, E, perm, chains), HOLDING CONFORMAL_FISHER aggregator FIXED across arms 1-5. The bidirectional-W axis is what r2d isolates (beyond the calibration axis that r2c tested).

1. **FORWARD_BASELINE** -- forward-only iter-cleanup (CAN-FAIL anchor reproducing r2c CONFORMAL_FISHER K=4 1.448x)
2. **BIDIR_AVG** -- 0.5 * (forward + backward) iter-cleanup; backward = W.T @ (e_{k+1} * R_p * sq) inverse-relation cleanup (PRIMARY mechanism per Wang 1990)
3. **BIDIR_FORWARD_HEAVY** -- 0.7 forward + 0.3 backward (asymmetric mix)
4. **BIDIR_BACKWARD_HEAVY** -- 0.3 forward + 0.7 backward (asymmetric mix)
5. **BIDIR_LEARNED_WEIGHT** -- per-hop weight w_k (current cell: defaults to 0.5; future r2e variant will learn weights via held-out conformal calibration)
6. **COMPOUND_CHAIN_COSINE** -- single chain-similarity cos(query_chain_sum, key_chain_sum) using permutation-bound compound (theta-cycle full-chain test per PNAS 2024 hippocampal theta-gamma coupling)

CONFORMAL_FISHER aggregator HELD FIXED across arms 1-5 (one-score-per-chain arm 6 uses calibrated single-score gate). This isolates the bidirectional-W mechanism from the calibration layer.

## Independent variables

- `chain_mechanism` in {FORWARD_BASELINE, BIDIR_AVG, BIDIR_FORWARD_HEAVY, BIDIR_BACKWARD_HEAVY, BIDIR_LEARNED_WEIGHT, COMPOUND_CHAIN_COSINE}
- `K_hops` in {2, 3, 4}
- `forward_weight` in {1.0 (baseline), 0.7, 0.5, 0.3} for bidirectional arms

## Fixed (match r2c for direct comparison)

- N_DIM = 8192 (same as r2c)
- M_TRIPLES = 50000 (same as r2c)
- K_set = 8 (iterative-cleanup top-K bundle size)
- K_inner = 1
- N_CHAINS = 500
- N_OOD = 500
- SEEDS = [7, 17, 23, 31, 41] (5 seeds; lower than r2c's 7 for time budget per drill estimate)
- GAMMA = 0.8
- PERM_TYPE = "random" (Kanerva HDC primitive)
- BETA_CLEANUP = float(N_DIM)
- Aggregator: CONFORMAL_FISHER (held fixed from r2c best)
- CAL_FRAC = 0.5
- CONFORMAL_ALPHA = 0.10
- Corpus: FB15k-237 train (`data/datasets/fb15k_237_train_50k.jsonl`)

## New cell parameters

- Bidirectional cleanup spec: at each interior hop k in [1..K-1], compute backward state `e_k_back = cleanup(W.T @ (chain_fwd[k+1] * R[p_k] * sq))`; combine `e_k = forward_weight * chain_fwd[k] + (1 - forward_weight) * e_k_back`; re-cleanup against codebook for final state; per-hop margin from top1-top2 of re-cleanup ent_scores
- Terminal hop k=K uses forward-only (no successor for backward)
- COMPOUND_CHAIN_COSINE: query_compound = sum_k P^k(E[s] * prod_{j<=k} R[p_j]); key_compound = sum_k P^k(chain_fwd[k]); score = cosine(query_compound, key_compound)
- All BIDIR_* mechanisms use the SAME CONFORMAL_FISHER aggregator across the per-hop margin sequence

## Anchors (precondition replicates)

The FORWARD_BASELINE arm reproduces r2c's CONFORMAL_FISHER per-K ratio on the SAME harness. It MUST match r2c's reference ratios within +/- 0.05 per K:

| K | r2c CONFORMAL_FISHER ratio | tolerance band |
|---|---|---|
| 2 | 1.899 | [1.849, 1.949] |
| 3 | 1.644 | [1.594, 1.694] |
| 4 | 1.448 | [1.398, 1.498] |

Anchor-fail (out-of-tol) => harness drift => HARD_FAIL inconclusive (NOT a mechanism-negative on bidirectional-W).

## Pre-registered HARD bands

### HARD_PASS (bidirectional-W mechanism load-bearing; chain-grade promotion at K=4)

ANY ONE of {BIDIR_AVG, BIDIR_FORWARD_HEAVY, BIDIR_BACKWARD_HEAVY, BIDIR_LEARNED_WEIGHT} at K=4 must satisfy ALL of:

1. `chain_aggregator_ratio >= 2.0x` (chain-grade bar; same as r2c HARD_PASS threshold)
2. `K-decay slope (ratio_K4 / ratio_K2) >= 0.85` (bidirectional flattens the slope -- r2c CONFORMAL_FISHER had 1.448/1.899 = 0.762)
3. `chain_aggregator_ood_refuse >= 0.90` (refuse-gate intact at K=4)
4. `cv across 5 seeds <= 0.10` (slightly looser than r2c's 0.08 because fewer seeds + bidirectional adds variance)
5. `FORWARD_BASELINE` reproduces r2c CONFORMAL_FISHER per-K within +/- 0.05 (harness intact)
6. Substrate-only-decode counter == 0 (no LLM forward calls)

### MIDDLE_BAND (partial closure)

Best bidirectional arm at K=4 has `chain_aggregator_ratio` in [1.50x, 2.00x] AND slope (K4/K2) > 0.7 AND FORWARD_BASELINE reproduces r2c.

### HARD_FAIL (bidirectional-W mechanism wrong / structurally deferred)

EITHER:
- NO bidirectional arm exceeds FORWARD_BASELINE at K=4 (mechanism does not help -- substrate's bipolar W is spectrally asymmetric and W.T does not provide noise cancellation)
- OR best bidirectional arm K-decay slope drop K=2->K=4 > 0.40 (bidirectional did not flatten the decay; substrate-specific failure of the BAM stability prediction)
- OR FORWARD_BASELINE drifts >+/- 0.05 vs r2c CONFORMAL_FISHER (harness changed; HARD_FAIL inconclusive)

## Compute / cost / routing

Per Research drill estimate: ~40-60min CPU-laptop wall (~2x r2c due to bidirectional pass).

Detailed estimate:
- Ingest + W build: ~3s/seed (matches r2c)
- Per K forward-only: matches r2c (~50-100s/seed CPU at N=8192)
- Per K bidirectional: ~2x forward (extra backward pass + recombine + re-cleanup); ~100-200s/seed
- Per K compound-chain cosine: ~forward + permutation binding; ~60-120s/seed
- 6 arms * 3 K * 5 seeds = 90 per-arm-per-K evaluations
- Total per seed: ~500-1000s CPU; 5 seeds: ~40-90 min CPU
- Per drill: 40-60 min CPU laptop estimate; 6h timeout = 6-9x safety margin

**Routing decision:** remote_cpu_queue per drill (banked: laptop CPU is slowest compute; remote CPU faster + persistent + no laptop tie-up). The cell uses torch.cuda if available; falls back to CPU. Per-experiment timeout: 10800s (3hr; drill estimate 40-60min + slack for cold-start, queue scheduling, sequence-after-v2d).

## Smoke gate

- 1 seed (7), N_DIM=2048, M_TRIPLES=5000, K_HOPS in {2, 3}, N_CHAINS=100, N_OOD=100
- All 6 arms run + bidirectional traversal functional + CONFORMAL_FISHER aggregator applied
- Self-test on tiny synthetic KG: verify forward + bidirectional + compound-chain cosine return finite ratios; forward ratio > 1.0 (sanity)
- Smoke wall expected: <60s on CPU laptop

## Version markers (baked into metrics.json)

`chain_mechanism`, `aggregator_held_fixed=CONFORMAL_FISHER`, `bidir_weights`, `K_inner`, `gamma`, `permutation_type`, `forward_weight` per arm, `N_DIM`, `M_TRIPLES`, `n_seeds`, `n_chains`, `device` (cuda|cpu), `r2c_conformal_fisher_reference_ratios`.

## Discriminating-regime check (C5; per Research drill)

- FORWARD_BASELINE is the CAN-FAIL discriminator: if its ratio drifts >+/-0.05 vs r2c CONFORMAL_FISHER, the cell harness is broken (NOT mechanism-negative on bidirectional-W). This is the by-construction-saturation tier-check + Fix #16 discriminator-regime.
- The K=2 NULL bracket: if BIDIR_* underperforms at K=2 vs FORWARD_BASELINE, the mechanism is harmful at short chains (rejects bidirectional as a load-bearing mechanism even if it helps at K=4).
- If FORWARD_BASELINE reproduces r2c BUT no BIDIR_* arm flattens the slope, the substrate's bipolar Hebbian W has spectral asymmetry that defeats the BAM stability prediction (substrate-specific failure of well-validated lit).

## Falsifiable predictions (from Research drill, calibrated; deflated)

| Prediction | P(HARD-PASS) |
|---|---|
| 1 (primary): BIDIR_AVG at K=4 ratio >= 2.0x + slope >= 0.85 + ood-refuse >= 0.90 | 0.40 |
| 2 (secondary): COMPOUND_CHAIN_COSINE at K=4 ratio >= 1.50x (theta-cycle alone) | 0.25 |
| 3 (hybrid; conditional): BIDIR_* + COMPOUND beats either alone (composes multiplicatively) | 0.30 (conditional on Prediction 1) |
| 4 (null bracket): BIDIR_* at K=2 within 5% of CONFORMAL_FISHER 1.899x (no underperformance) | high-confidence (negativity-rebuttal: if BIDIR_* under-performs at K=2, mechanism is wrong) |
| 5 (negativity-check): FORWARD_BASELINE reproduces r2c CONFORMAL_FISHER within +/- 0.05 | high-confidence (same harness) |

P_overall_deflated = 0.40 (capped novel-synthesis per Research drill; BAM bidirectional is well-validated, substrate-specific transfer is the only novelty).

## Composes with

- r2c (CONFORMAL_FISHER aggregator + harness + per-K reference ratios)
- r2 (W, R, E, perm, chains via same FB15k-237 50k sample protocol)
- hdlab/chain_score.py (bidirectional cleanup primitive if HARD_PASS -> Store atom + hdlab primitive update SAME CYCLE per Results-to-Application cadence USER 2026-06-22)
- IF HARD_PASS: META atom on substrate-validated bidirectional-W BAM stability prediction
- IF HARD_PASS: `r2e_cascade_W_bidirectional_v1` follow-on (compose with drill #2 c2 if it re-attempts)
- IF HARD_PASS: `g1b_bidirectional_W_generation_v1` (bigram-gap closure via bidirectional generation)
- IF HARD_PASS: `r4_hotpotqa_bidirectional_K_geq_3_v1` (HotpotQA K=3-4 chain-grade extension)
- IF MIDDLE_BAND: capacity sweep M=50k -> 200k per by-construction-saturation discipline

## Honest limits

- All HARD bands are METHOD/CONFIG-contingent (N=8192, M=50000, 5 seeds, 500 chains, FB15k-237; "envelope of THIS method/config, extension untested").
- Bidirectional backward step assumes substrate's bipolar Hebbian W is symmetric in expectation under random binding (standard HDC condition per Wang 1990); if substrate's normalized W has spectral asymmetry per-edge-ingest, the BAM stability prediction may not transfer cleanly.
- 5 seeds (vs r2c's 7) is a time-budget compromise per drill; CV bound loosened from 0.08 to 0.10 to compensate.
- BIDIR_LEARNED_WEIGHT in this cell uses 0.5 default (the same as BIDIR_AVG mechanism); the per-hop weight LEARNING extension is deferred to r2e (avoid combining mechanism + learning experiment in one cell).
- COMPOUND_CHAIN_COSINE is a single-score gate (not multi-hop conformal); its calibration is necessarily different from arms 1-5 (gate on the cosine directly vs Fisher chi2 on per-hop p-values). The COMPOUND comparison is INFORMATIVE rather than apples-to-apples with bidirectional arms.
- Anchor-faithfulness tolerance +/- 0.05 is wider than r2c's +/- 0.02 because we're comparing FORWARD_BASELINE (this cell's r2c-equivalent re-implementation) vs r2c's CONFORMAL_FISHER reference (different cell, possibly different RNG threading even with same seeds). +/- 0.05 is the realistic re-implementation noise budget per drill.

-- Exp-Dev, 2026-06-22
