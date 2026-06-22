# Pre-registration: r2c_conformal_LLR_compound_v1

**Author:** Exp-Dev
**Date:** 2026-06-22
**Anchor:** `r2c_conformal_LLR_compound_v1`
**Cell:** `experiments/exp_r2c_conformal_LLR_compound_v1.py`
**Driver:** Research 2x-revival drill 2026-06-22 (notes/research_multihop_2x_revival_compound_margin_path_to_2x_drill_2026-06-22.md); r2 (exp_r2_successor_TEM_compound_v1) partial-positive (compound_ratio = 1.13-1.19x consistent across K=2,3,4,10).

## Headline

r2 showed compound_margin_ratio = 1.13-1.19x ACROSS ALL K -- a consistent partial-positive that says the geometric-product compound IS reading chain-structure signal, but at a CAP. Research drill diagnosis: the 1.13x -> 2.0x gap is a CALIBRATION-stack gap, not a mechanism gap. Replace the geometric-product compound aggregator with a statistically-calibrated stack (LLR / Conformal-Fisher / PASC-joint / MIN) on the SAME r2 harness; one of them should close the gap.

This cell tests 5 chain-score aggregators on r2's W matrix, R/E codebooks, perm, chain set, and OOD set:

1. **GEOMETRIC_ANCHOR** -- r2's TEM compound-margin-mean (anchor; must reproduce r2 +/- 0.02 per-K ratio)
2. **LLR** -- per-hop log-likelihood-ratio sum via Gaussian-KDE density estimation; chain-score = sum_k LLR_k (Neyman-Pearson chain score)
3. **CONFORMAL_FISHER** -- per-hop p-value via split-conformal on calibration OOD set; chain-score = -2 * sum log p_k (Fisher's combined-probability; chi2 with df=2K under independent null)
4. **PASC_JOINT** -- one joint tau over the (score, K)-pair distribution (PASC pipeline-aware conformal); chain-score = mean over hops of (score - tau)
5. **MIN** -- min-over-hops (weakest-link emphasis); chain-score = min_k score_k

All 5 arms operate on the SAME per-chain per-hop top1-top2 margin sequence collected during TEM iter-cleanup. The underlying retrieval is r2's TEM mechanism (unchanged); only the score-aggregation rule differs.

## Independent variables

- `chain_aggregator` in {GEOMETRIC_ANCHOR, LLR, CONFORMAL_FISHER, PASC_JOINT, MIN}
- `K_hops` in {2, 3, 4}

## Fixed (match r2 for direct comparison)

- N_DIM = 8192
- M_TRIPLES = 50000
- K_set = 8 (iterative-cleanup top-K bundle size)
- K_inner = 1
- N_CHAINS = 500
- N_OOD = 500
- SEEDS = [7, 17, 23, 31, 41, 53, 67] (7 seeds, same primes as r2)
- GAMMA = 0.8
- PERM_TYPE = "random" (Kanerva HDC primitive)
- BETA_CLEANUP = float(N_DIM)
- Corpus: FB15k-237 train (`data/datasets/fb15k_237_train_50k.jsonl`)

## New cell parameters

- CAL_FRAC = 0.5 (250/500 chains used as calibration for conformal/LLR density estimation; remaining 250 as test)
- CONFORMAL_ALPHA = 0.10 (target marginal coverage 90% for split-conformal)
- LLR Gaussian-KDE bandwidth = 0.05 (fixed; not optimised within cell scope)
- LLR clipped to [-20, +20] to prevent log-domain explosions on outliers
- Fisher df = 2K under independence null (chi2(2K)); high chi2 => anomalous vs OOD null => in-KB-like

## Anchors (precondition replicates)

The GEOMETRIC_ANCHOR arm reproduces r2's TEM compound-margin ratio on the SAME harness. It MUST match r2's reference ratios within +/- 0.02 per K:

| K | r2 compound_ratio | tolerance band |
|---|---|---|
| 2 | 1.1336 | [1.1136, 1.1536] |
| 3 | 1.1318 | [1.1118, 1.1518] |
| 4 | 1.1522 | [1.1322, 1.1722] |

Anchor-fail (out-of-tol) => harness drift => HARD_FAIL inconclusive (NOT a mechanism-negative on aggregator).

## Pre-registered HARD bands

### HARD_PASS (calibration-stack gap closed; chain-grade promotion via aggregator)

ANY ONE of {LLR, CONFORMAL_FISHER, PASC_JOINT, MIN} at K=4 must satisfy ALL of:

1. `chain_aggregator_ratio >= 2.0x` (in-KB-mean / OOD-mean of aggregated chain score)
2. `chain_aggregator_ood_refuse >= 0.90` (test-split OOD refuse rate at calibrated tau)
3. `chain_aggregator_inkb_accept >= 0.40` (test-split in-KB accept rate at calibrated tau)
4. `cv across 7 seeds <= 0.08` (slightly looser than r2's 0.06 per Research drill -- aggregator adds variance)
5. `GEOMETRIC_ANCHOR ratio reproduces r2 within +/- 0.02` at K=2,3,4 (harness intact)
6. Substrate-only-decode counter == 0 (no LLM forward calls)

### MIDDLE_BAND (partial closure)

Best of {LLR, CONFORMAL_FISHER, PASC_JOINT, MIN} at K=4 has `chain_aggregator_ratio` in [1.50x, 2.00x] AND GEOMETRIC_ANCHOR reproduces r2.

### HARD_FAIL (calibration-stack hypothesis exhausted)

EITHER:
- NO arm in {LLR, CONFORMAL_FISHER, PASC_JOINT, MIN} reaches `chain_aggregator_ratio >= 1.50x` at K=4 (no aggregator closes the gap; the geometric-product cap is a substrate-mechanism cap, not a calibration gap)
- OR GEOMETRIC_ANCHOR ratio drifts > 0.02 vs r2 (harness changed; HARD_FAIL inconclusive, not mechanism-negative)

## Compute / cost / routing

Per Research drill estimate: ~20-30min CPU-laptop wall.

Detailed estimate:
- Ingest + W build: ~3s/seed (r2 measured 3.3s)
- Per K: 500 in-KB chains + 500 OOD chains, each traverse-and-collect (K matvecs + permutation binding); K=2 ~10s/seed, K=3 ~13s/seed, K=4 ~17s/seed at GPU. On CPU: 5-10x slower, so K=2 ~50-100s/seed, K=3 ~65-130s/seed, K=4 ~85-170s/seed.
- Aggregator overhead (KDE + Fisher per chain): adds ~5-10% over r2 traversal.
- Total per seed: ~200-400s CPU; 7 seeds: ~25-50 min CPU.
- Total per seed: ~50-100s GPU; 7 seeds: ~6-12 min GPU.

**Routing decision:** workload is matmul-bound at N=8192. Route to **remote_cpu_queue** per drill (banked Fix: laptop CPU is slowest compute; remote CPU faster + persistent + no laptop tie-up). The cell uses torch.cuda if available; falls back to CPU. If routed to GPU (overnight_queue), satisfies PROT-020 (import torch).

Per-experiment timeout: PROT-019 floor for _n8192 anchors = 21600s (6h). With ~50min CPU expected and 6h budget = 7x safety margin (plenty for cold-start, queue scheduling, etc.).

## Smoke gate

- 1 seed (7), N_DIM=2048, M_TRIPLES=5000, K_HOPS in {2, 3}, N_CHAINS=100, N_OOD=100
- All 5 arms run + cal/test split functional
- Self-test on tiny synthetic KG: verify all 5 aggregators return finite ratios + GEOMETRIC + MIN ratios > 1.0 (sanity)
- Smoke wall expected: <30s on CPU laptop

## Version markers (baked into metrics.json)

`chain_aggregator`, `cal_frac`, `conformal_alpha`, `fisher_df_mult`, `N_DIM`, `M_TRIPLES`, `n_seeds`, `n_chains`, `device` (cuda|cpu), `r2_compound_reference_ratios`.

## Discriminating-regime check (C5; per Research drill)

- GEOMETRIC_ANCHOR is the CAN-FAIL discriminator: if its ratio drifts > 0.02 vs r2, the cell harness is broken (NOT mechanism-negative). This is the by-construction-saturation tier-check.
- If GEOMETRIC_ANCHOR reproduces r2 BUT no calibrated aggregator reaches >= 1.50x, the substrate's geometric-product cap is a mechanism cap, not a calibration gap (Research drill HARD_FAIL diagnosis).

## Falsifiable predictions (from Research drill, calibrated; deflated)

| Prediction | P(HARD-PASS) |
|---|---|
| 1 (primary): CONFORMAL_FISHER at K=4 ratio >= 2.0x + OOD-refuse >= 0.90 + inkb-accept >= 0.40 | 0.40 |
| 2 (secondary): LLR alone ratio >= 1.50x at K=4 | 0.45 |
| 3 (tertiary): MIN aggregator ratio >= 1.30x at K=4 | 0.55 |
| 4 (null bracket): all aggregators converge at K=1 to single-hop anchor | high-confidence sanity (deferred per r2 sampler design; K=1 not in K_HOPS_LIST) |
| 5 (negativity-check): GEOMETRIC_ANCHOR reproduces r2 within +/- 0.02 | high-confidence (same harness) |

P_overall_deflated = 0.40 (capped novel-synthesis per Research drill).

## Composes with

- r2 (anchor reproduction of compound_ratio; same W, R, E, perm, chains)
- hdlab/conformal.py (split-conformal primitive; conformal_fisher arm extends to multi-hop)
- hdlab/refuse_gate.py (per-key refuse-gate; chain aggregator is its multi-hop generalization)
- IF HARD_PASS: META atom on conformal-Fisher chain-aggregator as substrate primitive
- IF HARD_PASS: drill #2 c2 cascade-STC compose follow-on (`r2e_cascade_W_conformal_Fisher_v1`)
- IF HARD_PASS: capacity sweep M=50k -> 200k for chain-grade evidence at higher capacity

## Honest limits

- All HARD bands are METHOD/CONFIG-contingent (N=8192, M=50000, 7 seeds, 500 chains, FB15k-237; "envelope of THIS method/config, extension untested").
- LLR Gaussian-KDE bandwidth fixed at 0.05 (not optimised); a bandwidth sweep would be a follow-on if LLR is the winning arm but ratio is close to threshold.
- Conformal-Fisher independence-null assumption: per-hop scores under random OOD chains are approximately independent; if substrate-induced correlation is strong, Fisher's chi2 is mis-calibrated (diagnose via chi2 distribution KS-stat under null).
- PASC_JOINT single-tau is the simplest variant; a tau-per-hop with shared budget is the full PASC; deferred to follow-on if PASC_JOINT is winning but partial.
- Anchor reproduction tolerance +/- 0.02 is set per Research drill (looser than r2's per-K mean +/- 0.01 because we're checking the COMPOUND ratio, which has more sources of noise).

-- Exp-Dev, 2026-06-22
