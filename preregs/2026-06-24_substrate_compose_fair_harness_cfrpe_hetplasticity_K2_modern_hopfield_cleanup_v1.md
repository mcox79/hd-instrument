# Pre-registration: substrate_compose_fair_harness_cfrpe_hetplasticity_K2_modern_hopfield_cleanup_v1

**Date:** 2026-06-24
**Anchor:** substrate_compose_fair_harness_cfrpe_hetplasticity_K2_modern_hopfield_cleanup_v1
**Script:** experiments/exp_substrate_compose_fair_harness_cfrpe_hetplasticity_K2_modern_hopfield_cleanup_v1.py
**Queue:** overnight_queue (GPU) — torch+CUDA; N_DIM_TOTAL=8192 matmul-heavy + 5 arms × 3 seeds + modern-Hopfield iterations
**Timeout:** 14400s (4h)
**Routing rationale:** Fix #24 — torch+CUDA matmul-bound for 5 arms × 3 seeds at N_DIM_TOTAL=8192 V=4000 (joint compose ~5× heavier than K2_x_cfrpe v2). Modern-Hopfield cleanup adds [chunk, V] × [V, N_DIM] matmul per cleanup iter. GPU required.

## Why this cell (load-bearing)

Per research substrate-mining-drill A1 anchor (`notes/research_substrate_aliveness_FULL_store_mined_map_2026-06-24.md`): substrate has 6 chain-grade aliveness dimensions (cf-RPE, het-plasticity STDP, K=2 multi-bank, modern-Hopfield, sparse-bipolar encoder, fair-harness baseline) but the joint compose of 5 has never been tested. P_deflated=0.78 the 1.5-bit gap from fair_harness rail (BPC 7.30) to bigram floor (~5.5 BPC) is achievable via cross-primitive composition.

This cell is the discriminating test:
- **Super-additive compose**: substrate is alive enough to clear bigram regime; substrate-as-LM becomes real product story.
- **Sub-additive compose**: substrate has alive PRIMITIVES but no compose-stacking — architectural rethink needed.

## Hypothesis

Five chain-grade substrate primitives, composed cumulatively, deliver super-additive lift over the best single knob: cf-RPE alone (7.1052 BPC). The HARD_PASS ceiling 6.85 requires that joint compose buys at least 0.26 BPC beyond cf-RPE single-arm — substantially more than any single additional primitive demonstrated alone.

## Design — five cumulative-build arms

| Arm | K | Plasticity | MH cleanup | Reference / Expected |
|-----|---|------------|-----------|----------------------|
| ARM_BASELINE_fair_harness | 1 | Hebbian | No | sanity rail 7.3065 ± 0.05 (fair_harness sparse-bipolar) |
| ARM_FAIR_HARNESS_PLUS_CFRPE | 1 | cf-RPE | No | sanity rail 7.1052 ± 0.05 (het_plasticity ARM_CFRPE_ONLY) |
| ARM_FAIR_HARNESS_PLUS_CFRPE_PLUS_HETPLASTICITY | 1 | cf-RPE + STDP | No | sanity rail 7.1654 ± 0.05 (het_plasticity ARM_CFRPE_STDP_HETEROGENEOUS) |
| ARM_FAIR_HARNESS_PLUS_CFRPE_PLUS_HETPLASTICITY_PLUS_K2 | 2 | cf-RPE + STDP per bank | No | NEW MEASUREMENT (K=2 lift on hetPlast base; no prior chain-grade reference) |
| ARM_FULL_JOINT_COMPOSE | 2 | cf-RPE + STDP per bank | Yes (modern-Hopfield β=8.0 iters=3) | THE LOAD-BEARING ARM |

**Encoder:** word2vec-google-news-300 → Gaussian-project(300→8192) → L2 normalize → sparse-bipolar f=0.05 → L2. Identical to fair_harness `ARM_SUBSTRATE_SPARSE_BIPOLAR`. OOV fallback: char-trigram.

**N-suffix note (PROT-018):** Anchor name contains no `_nN` suffix. Production `N_DIM_TOTAL = 8192` stated explicitly in script config section.

**Plasticity rules:**
- Hebbian (K1): W = sum E[t+1]^T E[t] (one-pass, ingest_chunk=4096)
- cf-RPE (K1): iterative dW = (Nxt - Ctx @ W^T)^T @ Ctx / batch, lr=0.5, n_steps=1000, batch=64
- cf-RPE + STDP (K1, het-plasticity): dW = dW_cf + 0.5 × (Nxt^T @ Ctx - Ctx^T @ Nxt) / batch
- K=2 multi-bank cf-RPE+STDP: per-bank W with gate-weighted plasticity (gate via bank-0 slice, soft-softmax τ=0.5)

**Modern-Hopfield cleanup (ARM_FULL_JOINT_COMPOSE only):** post-recall, on the [n_held, V] logits — interpret as soft pattern-assignment over E rows, iterate `softmax(β × logits) → mix E → L2 → re-score against E.T` for 3 iterations at β=8.0. Sharpens toward vocab attractors.

**Eval grids:**
- TEMP_GRID = [0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0]
- LAMBDA_GRID = [0.1, 0.3, 0.5, 0.7, 1.0] (excludes 0.0 per Skunkworks META C7)
- Joint (T, λ) sweep on dev half; report best on test half
- Per-lambda best-T captured (diagnostic)

## Pre-registered threshold bands (HARD)

All bands are on `ARM_FULL_JOINT_COMPOSE` BPC (the load-bearing arm). Sanity rails fire BEFORE the verdict bands.

| Verdict | Condition |
|---------|-----------|
| HARD_FAIL_LLM_CALL | `_LLM_CALL_COUNTER > 0` (substrate-only invariant) |
| HARD_FAIL (all seeds fail) | ARM_FULL_JOINT_COMPOSE all seeds compute-fail |
| HARD_FAIL_PROVENANCE_BASELINE | ARM_BASELINE_fair_harness BPC drifts > ±0.05 from 7.3065 |
| HARD_FAIL_PROVENANCE_CFRPE | ARM_FAIR_HARNESS_PLUS_CFRPE BPC drifts > ±0.05 from 7.1052 |
| HARD_FAIL_PROVENANCE_HETPLAST | ARM_FAIR_HARNESS_PLUS_CFRPE_PLUS_HETPLASTICITY BPC drifts > ±0.05 from 7.1654 |
| MIDDLE_BAND_HIGH_CV | ARM_FULL_JOINT_COMPOSE cv > 0.05 |
| HARD_PASS (super-additive; chain-grade-eligible) | ARM_FULL_JOINT_COMPOSE BPC ≤ 6.85 AND cv ≤ 0.05 |
| MIDDLE_BAND_ADDITIVE | ARM_FULL_JOINT_COMPOSE BPC in [6.85, 7.05] |
| MIDDLE_BAND_INTER_GAP | ARM_FULL_JOINT_COMPOSE BPC in (7.05, 7.15) |
| HARD_FAIL_SUB_ADDITIVE | ARM_FULL_JOINT_COMPOSE BPC ≥ 7.15 |

## Outcome plan for each verdict

- **HARD_PASS (super-additive):** substrate-as-LM clears bigram floor regime. Atomize as 5-primitive joint-compose chain-grade. Route to Strategy for next-cycle synthesis (which mechanism the joint exploits at production scale; capacity-scaling probe). Route to Skunkworks for landed-VET as chain-grade-candidate. SHIP: substrate-as-product story has its real evidence.

- **MIDDLE_BAND_ADDITIVE:** composition is additive but not super-additive. Substrate envelope at +0.30–0.50 over fair_harness. Atomize as MEASURED_MECHANISM. Route to Research for next-lever 2x revival drill: what beats the additive ceiling? Candidates: end-to-end gate training (currently fixed-random gate); K>2 sweep; modern-Hopfield β-iters tuning; alternative cleanup primitives (e.g. multi-iter cf-RPE on logits).

- **MIDDLE_BAND_INTER_GAP / MIDDLE_BAND_HIGH_CV:** marginal sub-additive or high-variance. Route to Skunkworks audit for whether per-seed variation hides a real signal. Route to Research for 2x drill: stability fix or primitive replacement.

- **HARD_FAIL_SUB_ADDITIVE:** compose-saturation. Substrate has alive primitives but no compose-stacking. Architectural rethink needed. Route to Strategy + Research for: (a) is one primitive interfering with another (interference matrix)? (b) what would architecture-level changes (vs primitive stacking) look like? (c) is the encoder the bottleneck, not the substrate primitives?

- **HARD_FAIL_PROVENANCE (any rail):** primitive pipeline mismatch. Debug the offending primitive vs its reference source cell. Cell non-cert-able until rail reproduces.

- **HARD_FAIL_LLM_CALL:** substrate-only invariant broken. Patch the call-site; re-dispatch.

## Smoke gate (load-bearing)

**Smoke scale:** N_DIM=1024, N_TRAIN=2000 synthetic markov-bigram corpus, 1 seed, 80 steps, V=300, K_BANKS=2 (per-bank=512).

**Smoke encoder:** clean synthetic gaussian (NOT substrate's word2vec state) per memory rule "smoke tests must use clean synthetic data, NOT substrate's existing atoms/labels/encoding". Provenance sanity rails are disabled at smoke scale (V/N differ structurally; baseline absolute BPC will diverge by construction).

**Smoke wall target:** < 180s on local CPU.

**Smoke MUST verify:**
- All 5 arms produce non-null, non-sentinel, finite BPC / top1 / mrr
- Encoder pipeline + sparsify_bipolar + per-arm plasticity + modern-Hopfield cleanup all complete
- per_lambda_T_summary captured for at least 1 arm
- LLM call counter == 0 at metrics write
- raw_bpc_at_T1_L1 is finite (DEGEN gate diagnostic)
- ARM_FULL_JOINT_COMPOSE BPC differs from ARM_FAIR_HARNESS_PLUS_CFRPE_PLUS_HETPLASTICITY_PLUS_K2 BPC (cleanup non-identity at smoke scale)

Smoke effect-size expectation: at synthetic-bigram + N_DIM=1024 V=300, ARMS should learn (BPC < uniform 8.23 with margin). Provenance rails NOT enforced at smoke scale (run_mode=smoke gates them off explicitly in verdict).

**Walk-back gate:** if smoke ARM_BASELINE_fair_harness BPC is essentially uniform (≈ -log2(1/300) ≈ 8.23 with no learning), abort and debug. If baseline learns at smoke scale (BPC < uniform - 0.5), proceed.

## Timeout estimate

**Per-arm wall (GPU estimate, scaled from K2_x_cfrpe word2vec v2 baseline ~300-600s/seed):**

- ARM_BASELINE_fair_harness (Hebbian K1, one-pass): ~30s ingest + 5s recall = 35s/seed
- ARM_FAIR_HARNESS_PLUS_CFRPE (K1 cf-RPE 1000 steps): ~50s/seed
- ARM_FAIR_HARNESS_PLUS_CFRPE_PLUS_HETPLASTICITY (K1 het-plast 1000 steps): ~55s/seed (additional STDP outer per step)
- ARM_FAIR_HARNESS_PLUS_CFRPE_PLUS_HETPLASTICITY_PLUS_K2 (K2 het-plast 1000 steps): ~120s/seed (2 banks, 4x more matmul)
- ARM_FULL_JOINT_COMPOSE (K2 het-plast 1000 steps + MH cleanup 3 iters): ~130s/seed (+10s cleanup)
- Joint sweep + bookkeeping per arm: ~10s/seed × 5 arms = 50s/seed
- Encoder + corpus per seed: ~30s/seed

**Per-seed total estimate (GPU): ~480s = 8 min**
**3 seeds: ~1440s = 24 min**
**With 1.5× safety + GPU contention: ~2160s = 36 min**
**With CPU-fallback buffer (if GPU unavailable): up to ~3-4h**

**timeout_s = 14400 (4h)** — provides ample headroom for GPU-CPU fallback, gensim load delay (first seed only), and seed-checkpoint resume. PROT-021 satisfied: script imports `_seed_checkpoint`.

## What this does NOT show

- Does not test K > 2 (only K=2 vs K=1 in cumulative build)
- Gate parameters not trained end-to-end; gate is fixed-random Gaussian projection
- Modern-Hopfield cleanup acts on logits post-W, NOT on E directly (Ramsauer 2020 original frame applies to E itself; cleanup-on-logits is the substrate-LM adaptation)
- K=2 het-plasticity arm has no prior chain-grade reference (its sanity is not pre-checkable; deviates from its absence rather than against a number)
- Plasticity learning rate, batch, gate temperature, MH β, MH iters all frozen at chain-grade-source values (no tuning)
- Result at text8 V=4000 N_TRAIN=100k; may not generalize to other corpora or larger V
- ARM_FULL_JOINT_COMPOSE failure does NOT rule out the same primitives composing under a DIFFERENT architecture (e.g. end-to-end gate training, hard WTA, multi-iter cf-RPE on logits)

## Cites

- notes/exp_dev_handoff_research_substrate_aliveness_FULL_store_mined_2026-06-24.md (A1 anchor; this cell's mandate)
- notes/research_substrate_aliveness_FULL_store_mined_map_2026-06-24.md (full Store-mined map)
- data/exp_fair_harness_substrate_as_lm_v1/metrics.json (baseline rail 7.3065)
- data/exp_substrate_heterogeneous_plasticity_cfrpe_stdp_fair_harness_v1/metrics.json (cf-RPE 7.1052 / hetPlast 7.1654)
- data/exp_modern_hopfield_n_sweep_v1/metrics.json (modern-Hopfield exponential energy chain-grade row 100; β=8.0 source)
- data/exp_substrate_K2_x_cfrpe_compose_word2vec_v2/metrics.json (encoder pipeline base; provenance gate template)
- experiments/exp_substrate_K2_x_cfrpe_compose_word2vec_v2.py (this cell's torch+CUDA encoder + K2 base)
- experiments/exp_substrate_heterogeneous_plasticity_cfrpe_stdp_fair_harness_v1.py (STDP primitive source)
- experiments/exp_modern_hopfield_n_sweep_v1.py (modern-Hopfield primitive source)
- Skunkworks META C7 (LAMBDA_GRID excludes 0.0)
- Fix #24 (GPU dispatch must actually use GPU)
- Fix #28 (per-arm metrics ONLY, not summary verdict text)
- Fix #26 (predispatch verify-the-referent — passed: PROCEED)
- USER 2026-06-23 (smoke clean synthetic data; not substrate state)
