# PRE-REG: substrate_cross_layer_compose_LM_v1

**Date:** 2026-06-24
**Anchor:** `substrate_cross_layer_compose_LM_v1`
**Author:** exp_dev
**Routing:** local_cpu_queue OR remote_cpu_queue (CPU; word2vec encoder + matmul-bound)

---

## HYPOTHESIS

Composition fact-finder (`notes/director_composition_store_mine_inventory_2026-06-24.md`)
identified the diagnostic split:

- **Cross-layer hierarchical stacking** (independent W per hop) succeeds chain-grade
  at L=100 (`exp_q_a3_l100_cross_layer_composition_v1_n16384` lacc=1.0).
- **Same-W stacking** catastrophically collapses (A1 5-arm joint = 7.89 BPC,
  WORSE than unigram 7.738).

This cell tests whether the cross-layer architecture pattern transfers to the
**LM regime** at LM-relevant scale (text8 N_TRAIN=100k, V=4000, N_DIM=8192).

If HARD_PASS, substrate has a real path past the same-W composition ceiling
(intra-layer 5-primitive joint is closed; cross-layer is open).

If HARD_FAIL, cross-layer architecture works only for pure compositional
retrieval (independent hop targets), not for next-token LM where every layer
must contribute to the SAME final next-token target.

---

## ARMS

Four arms, 3 seeds each, joint (T, lambda) sweep on dev / eval on test:

1. **ARM_SINGLE_LAYER_CFRPE** — reference / sanity rail. cf-RPE single-layer at
   N=8192, identical to fair_harness ARM_CFRPE_ONLY mechanism. Expected BPC
   in the cf-RPE-only neighborhood (fair_harness ARM_CFRPE_ONLY landed ~7.04
   at this scale per Director-cited prior).

2. **ARM_2_LAYER_INDEPENDENT_CFRPE** — LOAD-BEARING. Two layers, each with its
   OWN independent W. Layer 1 trained cf-RPE on (token_t -> token_t+1). Layer 2
   trained cf-RPE on (layer1_out_t -> E[token_t+1]). Independent gradients per
   layer. Forward: x -> L1_W -> normalize -> L2_W -> decode.

3. **ARM_3_LAYER_INDEPENDENT_CFRPE** — extends ARM 2 to 3 layers. Same
   independent-W pattern. Tests whether more depth helps OR introduces
   per-layer-error compounding.

4. **ARM_2_LAYER_SHARED_W_CFRPE** — CONTROL. Two layers, but SHARED W (i.e.,
   x -> W -> normalize -> W -> decode; same matrix applied twice). Expected
   to reproduce A1-style sub-additive collapse (validates the same-W vs
   independent-W diagnosis is the operative axis, not "having multiple layers"
   per se).

---

## ENCODING

word2vec-google-news-300 projected to N_DIM=8192 sparse-bipolar (f=0.05) —
identical to fair_harness chain-grade baseline. Each arm builds its own W
stack from scratch (no cross-contamination).

OOV fallback: char-trigram bipolar encoding.

---

## CONFIG

- N_DIM = 8192
- N_TRAIN = 100,000 tokens (text8)
- N_HELD = 20,000 tokens (held-out split, dev/test = 50/50)
- VOCAB_CAP = 4000
- SEEDS = [7, 17, 23] (3 seeds)
- N_STEPS = 1000 (iterative cf-RPE update steps per layer; matches fair_harness)
- INGEST_BATCH = 64
- CFRPE_LR = 0.5
- SPARSE_BIPOLAR_F = 0.05
- TEMP_GRID = [0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0]
- LAMBDA_GRID = [0.1, 0.3, 0.5, 0.7, 1.0]   # EXCLUDES 0.0 per META C7 (no pure-unigram)
- MRR_K = 10

---

## PRE-REG BANDS

**Sanity rails (MUST hold for cell to be interpretable):**
- ARM_SINGLE_LAYER_CFRPE BPC within +/- 0.30 of 7.04 (provenance against
  fair_harness ARM_CFRPE_ONLY chain-grade reference). Wider rail than +/-
  0.05 because the fair_harness reference is a related cell, not an exact
  re-run.
- ARM_2_LAYER_SHARED_W must NOT beat ARM_SINGLE_LAYER_CFRPE by >= 0.05 bits
  (sub-additive or no-lift expected; validates same-W collapse pattern).

**Verdict bands (independent-layer best arm BPC, denoted `best_indep_bpc`):**
- **CHAIN_GRADE_BONUS**: best_indep_bpc <= 6.70 (substantial gain via
  cross-layer; >= 0.34 bits below single-layer reference).
- **HARD_PASS**: best_indep_bpc <= 6.90 (cross-layer breaks composition
  collapse AND beats single-layer by >= 0.14 bits).
- **MIDDLE_BAND**: best_indep_bpc in (6.90, 7.05] (neutral; cross-layer
  doesn't materially help OR hurt).
- **HARD_FAIL**: best_indep_bpc > 7.05 OR best_indep_bpc > shared_W_bpc
  (cross-layer doesn't transfer to LM; or worse than the supposedly-broken
  same-W control).

**Stability:** cv across seeds of HARD_PASS arm <= 0.05 mandatory (else
downgrade to MIDDLE_BAND_HIGH_CV).

**READOUT_DEGENERATE:** if best_indep raw_bpc_at_T1_L1 within +/- 0.5 of
vocab-entropy (log2(V) ~= 12.0 bits for V=4000), the arm collapsed to
uniform-output regime; verdict = READOUT_DEGENERATE regardless of joint-swept
BPC.

---

## INSTRUMENTATION REQUIREMENTS

Per Skunkworks's structural blocker (banked in N2-cell-design plan):
- Per-seed-per-arm metrics in `per_seed` list (no early aggregation).
- cv reported per arm.
- LAMBDA_GRID excludes 0.0 (no pure-unigram blend; load-bearing per META C7).
- Real-data assertion: text8 corpus path verified at startup; no synthetic fallback.

Forward-call counter: this cell uses NO LLM at inference (pure substrate
plasticity over word2vec projection). No `transformers` forward calls
occur in the score path. Documented in metrics.json `by_construction_guards`.

---

## SMOKE GATE

Smoke config (auto-activated via `--smoke` or `_smoke` HDLAB_EXP_NAME):
- N_DIM=512, N_TRAIN=2000, N_HELD=400, VOCAB_CAP=300, SEEDS=[0], N_STEPS=80
- char-trigram encoder fallback (gensim not required for smoke)
- Must produce valid metrics.json with REQUIRED_FIELDS + per-arm per_seed entries.
- Must NOT crash on any of the 4 arms (multi-layer build callable).
- Expected smoke wall: 20-60s on laptop CPU.

---

## TIMEOUT ESTIMATE

Scaling from fair_harness cf-RPE neighbor:
- fair_harness ARM_CFRPE_STDP at N_DIM=8192 N_TRAIN=100k 3 seeds ~ 30 min CPU
  (matches plan-doc "~25-30min").
- This cell has more arms (4 vs 4 - same arm count, but multi-layer arms do
  2x or 3x the W-build + recall passes).
- Estimated full-wall: ~45-60 min CPU.
- **Requested timeout: 3600s (1h)** — comfortable margin over estimate.

This is below PROT-019 large-N tier-floor of 14400s; the anchor name has no
`_n<N>` suffix so PROT-019 does not apply. PROT-021 (long-timeout checkpoint
requirement) does not apply since timeout < 14400s, but checkpointing is
implemented anyway via `experiments/_seed_checkpoint.py` per role discipline.

---

## CITES

- `notes/director_composition_store_mine_inventory_2026-06-24.md` (composition fact-finder)
- `experiments/exp_substrate_heterogeneous_plasticity_cfrpe_stdp_fair_harness_v1.py` (cf-RPE reference; harness shape)
- `experiments/exp_substrate_compose_fair_harness_cfrpe_hetplasticity_K2_modern_hopfield_cleanup_v1.py` (A1 5-arm HARD_FAIL counter-example)
- `experiments/exp_q_a3_l100_cross_layer_composition_v1_n16384.py` (cross-layer L=100 lacc=1.0 reference)
- `experiments/exp_fair_harness_substrate_as_lm_v1.py` (chain-grade baseline 7.3065 BPC)

---

## ROLE DISCIPLINES APPLIED

- ASCII-only in source + prereg
- Per-seed checkpoint via _seed_checkpoint
- Fix #14 ONE cell (no parallel siblings)
- Fix #28 per-arm metrics verification (no cross-cell convergence claim until per_arm metrics inspected)
- Fix #26 predispatch_check ran; no prior landings, PROCEED
- LAMBDA_GRID excludes 0.0 (META C7 no-pure-unigram-blend)
- Smoke gate mandatory before full dispatch
