# Pre-reg: cortex_pkm_layer_v1

## Motivation
Cell D v2 (cortex_hippo_dense_layer_M8192_v2) established dense-Hopfield attention
as chain-grade READ-REPLACEMENT for cortex readout. Product-Key Memory
(Lample et al., 2019; arxiv/1907.05242) was one of four cross-domain sources
cited by the Cell D drill as supporting REPLACE-not-COMPOSE. PKM factors the
key space into two sqrt(K) sub-key spaces, giving theoretically higher
capacity per parameter and O(sqrt(K)) attention cost.

This cell tests whether the PKM structure gives a MEASURABLE advantage over
dense-Hopfield replacement in the same substrate/regime, at the discriminating
alpha = M/N_c = 1.0 regime where standard cortex Hebbian is over-subscribed.

## Falsifiable predictions
- HARD_PASS (new capacity primitive):
    - recall(ARM_PKM_REPLACE) - recall(ARM_HA_DENSE_REPLACE) >= 0.05
    - AND recall(ARM_PKM_REPLACE) >= 0.80
    - AND arms_differ_verified (META_RULE_AF hash-test)
- MIDDLE_BAND (equivalent):
    - abs(recall(PKM) - recall(DENSE)) < 0.05
    - AND both >= 0.60
- HARD_FAIL (PKM underperforms):
    - recall(PKM) - recall(DENSE) < -0.05
    - OR recall(PKM) < 0.30 (mechanism collapse)
    - OR fairness leak: recall(HA_ONLY) >= 0.20
    - OR cardinality breach (n_core_arms != 4)
    - OR beta_computed degenerate for either attention arm

## Regime
- N_h = 4096, N_c = 8192 (Cell D used 4096; this uses 8192 per task spec)
- M = 8192 (matches Cell D v2)
- alpha_simple = M / N_c = 1.0 (higher-alpha than Cell D's 2.0; STANDARD saturates)
- sparsity = 0.10 (hippo sparse-DG k-WTA)
- eta_h = 1.0
- 3 seeds: {7, 13, 19}, one cell file per seed (chunked)
- Backend: torch.cuda on remote GPU; numpy fallback on CPU smoke.

## PKM structure
Product-Key Memory (Lample 2019 eq.1-3):
- Split query q in R^{N_c} into two halves q1, q2 in R^{N_c/2}.
- Two sub-key spaces K1, K2 each of size sqrt(K) = 91, in R^{N_c/2}.
- Sub-key scores: s1 = beta * K1 @ q1 (91 values); s2 = beta * K2 @ q2.
- Top-h from each half (h = 8): top-h1, top-h2 with associated scores.
- Cartesian product: candidate keys = {(i1, i2) : i1 in top-h1, i2 in top-h2}
  giving h*h = 64 candidates per query.
- Full-key indices: idx = i1 * sqrt(K) + i2. Score = s1[i1] + s2[i2].
- Softmax over the h*h candidates; weighted read of V_c[idx].

## Effective_key_count = 91 * 91 = 8281 >= M = 8192; subselect first M keys.

## Arms
- ARM_STANDARD: direct cortex Hebbian readout (sanity ceiling reference).
- ARM_HA_ONLY: sparse hippo write only; tape not read (fairness floor ~1/M).
- ARM_HA_DENSE_REPLACE: Cell D v2 mechanism at N_c=8192 (baseline to beat).
- ARM_PKM_REPLACE: PKM-structured attention read at N_c=8192 (new).

## Schema-vet gates (META_RULE_H/J/K/L/M/AC/AF/AG/AH)
- cardinality_ok = True; EXPECTED_N_UNITS = 4 core arms.
- arms_differ_verified: True at smoke gate via META_RULE_AF hash-test.
- final_metrics_atomicity: tmp_replace.
- crlb_floor_computed: 0.00552 THEORETICAL@sqrt(0.25/M=8192).
- discriminator_reachability: True (HP gap 0.05 = 9.1 sigma; well-reachable).
- baseline_in_band: STANDARD at alpha=1.0 predicted 0.10 to 0.40 (below 0.95;
  in discriminating band). HYPOTHESIZED@this-prereg.
- discriminator survives scale: smoke includes FULL-N preview arm for PKM
  at M=8192, N_c=8192.
- HP_SCOPE: {
    ARM_PKM_REPLACE: [pkm_beats_dense, pkm_absolute_recall, arms_differ],
    ARM_HA_DENSE_REPLACE: [pkm_beats_dense (comparison arm)],
    ARM_STANDARD: [sanity_ceiling],
    ARM_HA_ONLY: [fairness_floor]
  }.
- calibration_check: adaptive_with_discriminator_gate (beta = log2(M)/margin,
  computed per-arm independently for DENSE and PKM tapes).

## Signal-shape compatibility (Gate 15C)
- DENSE and PKM both consume L2-normed projected keys_c (M x N_c) and
  vals_c (M x N_c). Same encoder, same tape layout. Only the READ operation
  differs. SHAPE_MATCH across all composition edges.

## Positive control (Gate 15D)
- ARM_HA_DENSE_REPLACE reproduces Cell D v2's mechanism at N_c=8192 (Cell D
  ran N_c=4096). Not exact reproduction; SHAPE_DRIFT with documented risk:
  at higher alpha (=1.0 vs Cell D's 2.0 -- actually LOWER alpha at N_c=8192,
  since alpha = M/N_c decreases as N_c increases), DENSE should stay high.
  Cell D v2 smoke DENSE_REPLACE = 1.000 at alpha=0.5; here at alpha=1.0
  expect >= 0.90 by capacity theory (spherical-code cap >> M).
- Tolerance: DENSE recall >= 0.90 at this regime. If < 0.90, cell invocation
  suspect; PKM comparison unreliable.

## Effective vs nominal parameter audit (Gate 15A)
- Cell has no sweep axis (single regime). N/A; declare aligned_no_sweep.

## Bracket discriminating band (Gate 15B)
- N/A (no sweep axis). Discriminator = single HP threshold (>= 0.05 delta).

## Functional requirements decomposition (Gate 15E)
- FR1: cortex must read stored (key, value) pairs at higher-than-Hebbian-alpha
  regime. Existing chain-grade primitive: dense-Hopfield attention (Cell D v2).
- FR2: PKM structure factorizes attention to sub-quadratic cost while
  preserving retrieval accuracy. New candidate primitive; this cell tests.

## Timeout
- Smoke: 600s (10 min; PKM slightly slower than DENSE due to top-h selection).
- Full: 3600s (60 min; per-seed at M=8192 N_c=8192 on GPU).

## Prior chain-grade evidence
- Cell D v2 M=8192 N_c=4096: DENSE_REPLACE recall_cortex = 1.000, gap
  vs HA_ONLY = +0.998, CHAIN_GRADE @ commit 863e14b5
  MEASURED@d:/AI/hd-instrument/data/exp_cortex_hippo_dense_layer_M8192_v2_seed_7/metrics.json:per_seed[0].arms[2].recall_cortex
- Product-Key Memory: Lample et al. 2019, arxiv/1907.05242 CITED@
- Substrate KB check 2026-07-01: no prior PKM cells found; closest hits =
  Kronecker attention primitive discussion in 2x-drill.
