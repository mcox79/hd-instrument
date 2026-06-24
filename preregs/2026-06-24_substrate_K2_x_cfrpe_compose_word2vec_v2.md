# Pre-registration: substrate_K2_x_cfrpe_compose_word2vec_v2

**Date:** 2026-06-24
**Anchor:** substrate_K2_x_cfrpe_compose_word2vec_v2
**Script:** experiments/exp_substrate_K2_x_cfrpe_compose_word2vec_v2.py
**Queue:** overnight_queue (GPU) — torch+CUDA; N_DIM_TOTAL=8192 matmul-heavy
**Timeout:** 3600s (1h)
**Routing rationale:** Fix #24 (GPU dispatch must actually use GPU); matmul-bound K=2 x cf-RPE on 8192-dim x V=4000 = ~3GB transient working set; 100k tokens x 300 steps cf-RPE per arm.

## Why this rescue

v1 (substrate_K2_x_cfrpe_compose_LM_v1) landed MIDDLE_BAND but used **char-trigram encoder**, not the word2vec-projected sparse-bipolar that fair_harness validated chain-grade. v1's ARM_BASELINE_RANK1_K1 came in at 7.6968 BPC, while the fair_harness chain-grade sparse-bipolar baseline is 7.3065. The ~0.39 BPC drift IS the encoder, not the architecture-plasticity compose under test.

Consequence: v1's measurement is a **methodology-confound**. The 4 arms cluster around BPC 7.6 (char-trigram regime), not around the 7.3065 fair-harness anchor. The K=2 x cf-RPE compose signal cannot be cleanly read off v1 because the encoder shift dominates the variance.

This v2:
- Replaces encoder with **word2vec-projected sparse-bipolar** (matches fair_harness chain-grade encoder pipeline exactly: word2vec-300 → Gaussian-project to N_DIM → L2 normalize → sparse-bipolar f=0.05 → L2)
- Ports build_W_rank1_hebbian / build_W_cfrpe / K=2 gate to **torch+CUDA** (Fix #24; GPU dispatch actually uses GPU)
- Excludes **lambda=0.0** from LAMBDA_GRID (Skunkworks META C7; lambda=0 entirely ignores substrate — cannot inform substrate-quality)
- Adds **per-context-T diagnostic** (per_lambda_T_summary captures best T at each lambda in joint sweep — exposes whether substrate prefers different temperatures at different lambda)
- Adds **provenance sanity rail**: ARM_BASELINE_RANK1_K1 within ±0.05 of 7.3065 — if encoder pipeline fails to reproduce, verdict = HARD_FAIL_PROVENANCE before any compose claim

## Hypothesis

K=2 multi-bank architecture and cf-RPE delta-rule plasticity are the 2 best validated substrate-as-LM lift levers. Under the chain-grade encoder this cell measures whether they compose super-additively, additively, or interfere.

Independent chain-grade or smoke-validated lift evidence (with correct encoder):
- cf-RPE single-arm chain-grade reference: 7.1052 BPC (lift +0.20 vs sparse-bipolar baseline 7.3065)
- K=2 multi-bank: +1.07 BPC lift over K=1 at smoke scale (notes/shotgun_smoke_K_bank_count_sweep_2026-06-23.md)

## Design

**Arms:** 4 arms × 3 seeds × text8 N_TRAIN=100k N_DIM_TOTAL=8192

| Arm | K | Plasticity | Description |
|-----|---|------------|-------------|
| ARM_BASELINE_RANK1_K1 | 1 | Hebbian | Single bank rank-1; SANITY RAIL: must reproduce fair_harness 7.3065 ± 0.05 |
| ARM_CFRPE_K1 | 1 | cf-RPE | Single bank cf-RPE; expected ≈ 7.1052 (chain-grade ref) |
| ARM_K2_RANK1 | 2 | Hebbian | 2 banks × 4096 dims; rank-1 Hebbian per bank |
| ARM_K2_CFRPE | 2 | cf-RPE | 2 banks × 4096 dims; cf-RPE per bank (combined arm) |

**Encoder:** word2vec-google-news-300 → Gaussian-project(300→8192) → L2 normalize → sparse-bipolar f=0.05 → L2 normalize. Identical to fair_harness `ARM_SUBSTRATE_SPARSE_BIPOLAR`. OOV fallback: char-trigram (defensive; on text8 V=4000 most words hit word2vec).

**N-suffix note (PROT-018):** Anchor name contains no _nN suffix. Production N_DIM_TOTAL=8192 stated explicitly in script config section (line: `N_DIM_TOTAL = 8192`).

**Eval grids:**
- TEMP_GRID = [0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0]
- LAMBDA_GRID = [0.1, 0.3, 0.5, 0.7, 1.0]  (excludes 0.0 per Skunkworks META C7)
- Joint (T, λ) sweep on dev half; report best on test half
- Per-lambda best-T captured as diagnostic (per_lambda_T_summary)

## Pre-registered threshold bands

All "lift" measured as BPC reduction. Lower BPC is better.

| Verdict | Condition |
|---------|-----------|
| HARD_PASS_PROVENANCE_PREREQ | ARM_BASELINE_RANK1_K1 BPC within ±0.05 of 7.3065 (must pass first; else HARD_FAIL_PROVENANCE) |
| HARD_PASS (compose) | ARM_K2_CFRPE BPC ≤ 7.0552 AND (ARM_CFRPE_K1 BPC − ARM_K2_CFRPE BPC) ≥ +0.10 |
| HARD_PASS CHAIN_GRADE_BONUS | ARM_K2_CFRPE BPC ≤ 6.95 (beats all known cf-RPE single-arm) |
| MIDDLE_BAND | (ARM_CFRPE_K1 BPC − ARM_K2_CFRPE BPC) in [+0.03, +0.10) |
| MIDDLE_BAND_HIGH_CV | Any compose condition met but cv_K2CFRPE > 0.05 |
| HARD_FAIL (no compose) | (ARM_CFRPE_K1 BPC − ARM_K2_CFRPE BPC) < +0.03 |
| HARD_FAIL_PROVENANCE | Sanity rail fails (baseline drift > 0.05) |
| HARD_FAIL (LLM-call violation) | _LLM_CALL_COUNTER > 0 (substrate-only invariant) |

Additional constraints:
- cv < 0.05 across seeds for ALL arms (mandatory; high-cv demotes to MIDDLE_BAND_HIGH_CV)
- LLM call counter must read 0 at metrics write (substrate-only audit)

## Outcome plan for each verdict

- **HARD_PASS CHAIN_GRADE_BONUS:** K=2 × cf-RPE delivers chain-grade compose lift; atomize as new substrate-LM frontier; route to Strategy for next-cycle synthesis (which mechanism does the bank-split exploit at production scale?).
- **HARD_PASS (compose):** ARM_K2_CFRPE meaningfully beats cf-RPE single-arm; atomize the combined config; route to Strategy for production-encoder replication + capacity scaling.
- **MIDDLE_BAND:** Knobs compose sub-additively; the bank-split costs resolution but cf-RPE recoups some. Route to Strategy for gate-mechanism deeper analysis (does end-to-end gate training change the slope?).
- **HARD_FAIL (no compose):** K=2 and cf-RPE interfere or fail to compose under the chain-grade encoder. Report which single knob is stronger. Route to Strategy to rule out the composition + investigate interference mechanism. Route to Research for revival-angle 2x drill (alternate gate / hard-WTA / per-bank cf-RPE temperature).
- **HARD_FAIL_PROVENANCE:** Encoder pipeline ported wrong; debug the gensim → projection → sparse-bipolar chain; the cell is non-cert-able until baseline reproduces.
- **HARD_FAIL (LLM-call violation):** Substrate-only invariant broken; cell rejected — patch the call-site, re-dispatch.

## Smoke gate (load-bearing)

**Smoke scale:** N_DIM=1024, N_TRAIN=2000, 1 seed, 80 steps, V=300
**Smoke encoder:** word2vec (NOT char-trigram) — this is the load-bearing rescue verification
**Smoke wall target:** < 180s on CPU

**Smoke MUST verify:**
- All 4 arms produce non-null, non-sentinel, finite BPC / top1 / mrr
- Word2vec encoder pipeline loads + projects + sparsifies without error
- per_lambda_T_summary captured for at least 1 arm
- LLM call counter == 0 at metrics write
- raw_bpc_at_T1_L1 is finite (DEGEN gate diagnostic)

Smoke effect-size expectation: at N_DIM=1024 and N_TRAIN=2000, per-bank resolution = 512 (half of K=1's 1024). Smoke may show interference (K2 < K1) — this is expected at smoke scale due to dimension halving; not a fail signal. Full N_DIM_TOTAL=8192 (4096/bank) is the correct measurement scale.

**Walk-back gate:** if smoke ARM_BASELINE_RANK1_K1 BPC differs from "small-scale word2vec sparse-bipolar baseline" by an order of magnitude (e.g. baseline running at uniform ≈ -log2(1/300) ≈ 8.23 with no learning), abort and debug. If baseline learns at smoke scale (BPC < uniform - 0.5), proceed.

## Timeout estimate

**Empirical benchmarks (laptop CPU; smoke scale; will be faster on GPU):**
- word2vec load + project + sparsify: ~10s per seed (cached after first seed)
- Encoder forward through V x N_DIM: ~5s
- ARM_HEBBIAN_K1 ingest (100k pairs, chunk 4096): ~10-30s on GPU
- ARM_CFRPE_K1 (300 steps, batch 64): ~5-10s on GPU
- ARM_K2_HEBBIAN (gated ingest): ~30-60s on GPU
- ARM_K2_CFRPE (gated 300 steps): ~10-20s on GPU
- Joint sweep (7 T × 5 λ × 4 arms × 2 halves): ~20s on CPU per seed
- Per-seed estimate (GPU): ~300-600s
- 3 seeds: ~900-1800s
- With 1.5× safety: ~2700s → **timeout_s = 3600s (1h)** matches USER spec

If runner is under load, may take up to ~2-3h; well within 4h ceiling (no PROT-019 floor since no _n suffix).

## What this does NOT show

- Does not test K > 2 (only K=2 vs K=1 contrast)
- Does not test cf-RPE with STDP heterogeneous composition (separate prior cell)
- Soft gate (softmax) is not hard winner-takes-all as in Drosophila MB
- Gate parameters not trained end-to-end; gate is fixed-random Gaussian projection
- K=2 arms use N=4096 per bank vs K=1 uses N=8192 (resolution tradeoff is baked into the test)
- Result at N_TRAIN=100k text8 V=4000; may not generalize to other corpora or larger V

## Cites

- preregs/2026-06-23_substrate_K2_x_cfrpe_compose_LM_v1.md (v1 prereg; this rescue's predecessor)
- preregs/2026-06-23_fair_harness_substrate_as_lm_v1.md (chain-grade encoder reference)
- preregs/2026-06-23_substrate_heterogeneous_plasticity_cfrpe_stdp_fair_harness_v1.md (cf-RPE chain-grade)
- experiments/exp_fair_harness_substrate_as_lm_v1.py (encoder pipeline source)
- experiments/exp_substrate_K2_x_cfrpe_compose_LM_v1.py (v1 cell; methodology-confound)
- notes/shotgun_smoke_K_bank_count_sweep_2026-06-23.md (K=2 lift smoke)
- Skunkworks META C7 (LAMBDA_GRID excludes 0.0)
- Fix #24 (GPU dispatch must actually use GPU)
