# Pre-registration: substrate_compose_heterogeneous_routing_v1

**Date:** 2026-06-24
**Anchor:** substrate_compose_heterogeneous_routing_v1
**Script:** experiments/exp_substrate_compose_heterogeneous_routing_v1.py
**Queue:** local_cpu_queue (~45min wall per drill estimate; fits in 3600s timeout)
**Timeout:** 3600s (1h)
**Drill source:** notes/research_untested_composition_architectures_2x_drill_2026-06-24.md (ANCHOR 1, PRIMARY)
**USER directive (load-bearing):** "I refuse to accept this" — cf-RPE +12% top1 / 7.07 BPC cap framing REJECTED. Brain achieves +60-80% top1; substrate at +12% cannot be a STRUCTURAL cap.

## Why this cell (load-bearing)

A1 5-primitive joint compose HARD_FAIL_SUB_ADDITIVE (catastrophic 7.89 BPC). MH beta-sweep HARD_FAIL_STRUCTURAL. ALL composition tests so far use SAME-W stacking. 3 UNTESTED brain-canonical architectures may break the cap. This cell is the cheapest decisive test: 4 arms × 3 seeds × N_DIM=8192 × text8 N_TRAIN=100k V=4000; ~45min wall on local CPU.

## Hypothesis

Heterogeneous-routing composition (different mechanisms on different W banks / subspaces / phases) breaks the cf-RPE +12% cap because the cap is an architectural consequence of forcing distinct plasticity rules through ONE shared W with ONE readout — not a substrate-capacity cap. Three architectures redundantly probe heterogeneity:

1. **THETA-PHASE TWO_W** — separate W_enc / W_ret by per-token phase (encoding/retrieval routing)
2. **FREQ_ROUTED_K2** — deterministic frequency-based routing (top-100 → W_freq, rare → W_rare)
3. **ORTHOG_SUBSPACE** — orthogonal Gram-Schmidt subspaces with cf-RPE in subspace_1, STDP in subspace_2

P_deflated=0.62 per drill (deflated from 0.78 raw; 3 architectures redundantly point at heterogeneity).

## Design — four arms

| Arm | Architecture | Plasticity | Routing | Notes |
|-----|---|------|-----------|---|
| ARM_BASELINE_FAIR_HARNESS | K=1 single bank | Hebbian | (none) | Sanity rail 7.3065 ± 0.05 |
| ARM_THETA_PHASE_TWO_W | 2 full-N_DIM W banks | cf-RPE on W_enc; STDP on W_ret | Alternating-phase per token | Brain anchor: theta-gamma 2024 |
| ARM_FREQ_ROUTED_K2 | 2 full-N_DIM W banks | cf-RPE (W_freq); cf-RPE+STDP (W_rare) | Deterministic by token-rank | Brain anchor: hippocampus/cortex; MaskMoE 2024 |
| ARM_ORTHOG_SUBSPACE | 2 small W's (4096×4096) in orthogonal subspaces | cf-RPE in subspace_1; STDP in subspace_2 | Gram-Schmidt QR split | Brain anchor: V1/V4 orthogonal axes; ORTHOG-SUBSPACE 2020 |

**Encoder:** word2vec-google-news-300 → Gaussian-project(300→8192) → L2 → sparse-bipolar f=0.05 → L2. Identical to fair_harness ARM_SUBSTRATE_SPARSE_BIPOLAR.

**Plasticity primitives:**
- Hebbian: W = sum E[t+1]^T E[t]
- cf-RPE: iterative dW = (Nxt - Ctx @ W^T)^T @ Ctx / batch
- STDP: dW = (Nxt^T @ Ctx - Ctx^T @ Nxt) / batch
- Theta routing: phase = step % 2; phase 0 → W_enc cf-RPE update; phase 1 → W_ret STDP update
- Frequency routing: per-batch tgt rank masks the update direction (W_freq vs W_rare)
- Orthogonal subspace: QR decomposition of N_DIM Gaussian → P1, P2 (half-dim each); cf-RPE writes via P1; STDP via P2

**Readouts (per arm):**
- BASELINE: pred = L2(ctx @ W.T) → logits = pred @ E.T
- THETA: logits = α × (pred_enc @ E.T) + (1-α) × (pred_ret @ E.T); α ∈ {0.3, 0.5, 0.7}; best by dev BPC
- FREQ: logits_v = is_high_freq[v] × logit_freq_v + (1 - is_high_freq[v]) × logit_rare_v
- ORTHOG: logits = (E1 @ pred1.T) + (E2 @ pred2.T); E1 = E @ P1, E2 = E @ P2

**Eval grids:**
- TEMP_GRID = [0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0]
- LAMBDA_GRID = [0.1, 0.3, 0.5, 0.7, 1.0] (excludes 0.0 per META C7)
- Joint (T, λ) sweep on dev half; report best on test half

## Pre-registered threshold bands (HARD)

All verdicts apply to the BEST of the 3 heterogeneous-routing arms (theta / freq / orthog). Sanity rail fires BEFORE verdict bands.

| Verdict | Condition |
|---------|-----------|
| HARD_FAIL_LLM_CALL | `_LLM_CALL_COUNTER > 0` (substrate-only invariant) |
| HARD_FAIL (all het arms fail) | All 3 het arms compute-fail all seeds |
| HARD_FAIL_PROVENANCE_BASELINE | ARM_BASELINE_FAIR_HARNESS BPC drifts > ±0.05 from 7.3065 |
| MIDDLE_BAND_HIGH_CV | best_het arm cv > 0.05 across seeds |
| HARD_PASS_CHAIN_GRADE_BONUS | best_het BPC ≤ 6.80 AND cv ≤ 0.05 (decisive cap-refutation + substantial gain) |
| HARD_PASS_CAP_BROKEN | best_het BPC ≤ 6.95 AND cv ≤ 0.05 (cap refuted; heterogeneous routing works) |
| MIDDLE_BAND_PARTIAL_SIGNAL | best_het BPC in [6.95, 7.05] |
| MIDDLE_BAND_INTER_GAP | best_het BPC in (7.05, 7.30) |
| HARD_FAIL_DECISIVE | all 3 het arms BPC ≥ 7.30 |

## Discriminating-regime metrics (mandatory per drill C5)

Each het arm must demonstrate routing has MEASURABLE effect, not just same-W in disguise. Reported in `detail.by_arm_agg[arm].discriminating_per_seed`:

- **ARM_THETA_PHASE_TWO_W:**
  - `enc_vs_ret_bank_corr` — cosine between vec(W_enc) and vec(W_ret); MUST be < 0.95 to confirm banks store distinct content
  - `logit_enc_ret_corr_mean` — per-query Pearson corr between pred_enc-logits and pred_ret-logits; high values imply banks converged
  - `n_phase0_steps` / `n_phase1_steps` — must roughly split (~500/500 in full)
  - `best_alpha` — winning alpha from {0.3, 0.5, 0.7}
- **ARM_FREQ_ROUTED_K2:**
  - `top1_high_freq_tokens` / `top1_low_freq_tokens` / `freq_top1_differential` — differential ≥ 0.05 required to confirm routing has effect
  - `n_high_freq_steps` / `n_rare_steps` — routing depths
- **ARM_ORTHOG_SUBSPACE:**
  - `orthog_residual_max` — max |P1.T @ P2|; must be < 1e-3 (Gram-Schmidt sanity)
  - `cross_subspace_grad_corr_mean_abs` — mean abs corr between dW1 (cf-RPE) and dW2 (STDP) gradients; must be < 0.70 to confirm orthogonality holds

## Outcome plan for each verdict

- **HARD_PASS_CHAIN_GRADE_BONUS (best_het ≤ 6.80):** USER directive vindicated decisively. Atomize as chain-grade-eligible 5-architecture-class lift. Identify WHICH architecture wins; route to Strategy for next-cycle deeper drill on that architecture (capacity scaling; T-grid extension; pair with cf-RPE-LR sweep). Route to Skunkworks for landed-VET.

- **HARD_PASS_CAP_BROKEN (best_het ≤ 6.95):** USER directive vindicated. Heterogeneous routing breaks the cap. Atomize as MEASURED_MECHANISM with chain-grade-pending. Route to Research for 2x revival drill: which mechanism in winning architecture is load-bearing? Can stacking 2 or 3 heterogeneous architectures additively beat single-arch?

- **MIDDLE_BAND_PARTIAL_SIGNAL / INTER_GAP:** partial routing benefit but not decisive. Route to Research for next-drill: end-to-end-trained gate; K>2 arch sweep; pair with multi-scale hierarchical or hypernetwork (drill secondary architectures).

- **HARD_FAIL_DECISIVE (all 3 het BPC ≥ 7.30):** cap MAY indeed be structural at this regime. Honest finding for USER. Route to Research for architectural pivot: attention-as-compose; multi-scale hierarchical; hypernetwork weight conditioning. Does NOT rule out heterogeneous-routing under different conditions (different encoder, larger N, different STDP weight).

- **HARD_FAIL_PROVENANCE_BASELINE:** encoder/Hebbian pipeline mismatch. Debug.

- **HARD_FAIL_LLM_CALL:** substrate-only invariant broken. Patch + re-dispatch.

## Smoke gate (load-bearing)

**Smoke scale:** N_DIM=1024, N_TRAIN=2000 synthetic markov-bigram, 1 seed, 80 steps, V=300.

**Smoke encoder:** clean synthetic gaussian (NOT word2vec state) per memory rule.

**Smoke MUST verify:**
- All 4 arms produce non-null, non-sentinel, finite BPC / top1 / mrr
- All 14 self-tests pass at small scale
- Theta-phase produces alpha-stack [3, N_HELD, V] valid; phase steps balanced
- Freq-routed produces valid is_high_freq_vocab_mask + n_high_steps + n_rare_steps > 0
- Orthog subspace produces orthog_residual_max < 1e-3 + cross_subspace_grad_corr_mean_abs finite
- LLM call counter == 0
- raw_bpc_at_T1_L1 finite for all arms (DEGEN gate)
- All 4 arm logits non-identical pairwise (diversity check)

**Smoke wall target:** < 180s.

Provenance rails OFF at smoke scale (V/N differ structurally; absolute BPC will diverge by construction).

## Timeout estimate

**Per-seed wall on local CPU (estimated from theta+freq+orthog matrix ops at N_DIM=8192, V=4000, n_steps=1000, batch=64):**

- ARM_BASELINE_FAIR_HARNESS (Hebbian K=1, one-pass): ~50s/seed (ingest+recall on 8192×8192 W, 100k pairs)
- ARM_THETA_PHASE_TWO_W (2 banks × 8192×8192 × 1000 steps): ~250s/seed
- ARM_FREQ_ROUTED_K2 (2 banks × 8192×8192 × 1000 steps + per-batch masking): ~280s/seed
- ARM_ORTHOG_SUBSPACE (2 banks × 4096×4096 × 1000 steps + QR setup 8192×8192 once): ~150s/seed (smaller W's)
- Encoder + corpus + ranks per seed: ~30s
- Joint sweep + bookkeeping per arm: ~10s × 4 = 40s
- Discriminating metrics (per-query corr + stratified top1): ~5s/seed

**Per-seed total ~805s ≈ 13.5min**
**3 seeds: ~40min**
**With 1.5× safety: ~60min**

**timeout_s = 3600 (1h)** — fits drill's ~45min estimate with safety margin. No PROT-019 trigger (no _nN suffix). No PROT-021 trigger (timeout < 14400s) but _seed_checkpoint imported anyway for safety.

## What this does NOT show

- Does not test K > 2 routing variants
- Does not test end-to-end-trained gates (routing is deterministic-by-construction)
- Does not stack modern-Hopfield cleanup on het-routing logits (orthogonal axis to drill primary; reserved for secondary drills if HARD_PASS)
- Does not test multi-scale hierarchical / attention-as-compose / hypernetwork (drill L3.4-L3.6; reserved for tertiary drills)
- Does not test alternative theta-phase periods (only 2-phase; brain has continuous theta)
- Does not sweep FREQ_ROUTE_RANK (fixed at 100; drill notes 50/100/200/500 sweep is future work)
- Does not test alternative orthogonal subspace partitions (only 50/50 split; could try 25/75, 75/25)
- HARD_FAIL_DECISIVE does NOT rule out heterogeneous routing under different encoder, larger N, longer training, or different plasticity-rule combinations

## Cites

- notes/research_untested_composition_architectures_2x_drill_2026-06-24.md (ANCHOR 1; this cell's mandate)
- USER directive 2026-06-24: "I refuse to accept this" — cf-RPE +12% cap framing rejected
- data/exp_fair_harness_substrate_as_lm_v1/metrics.json (sanity rail 7.3065)
- experiments/exp_substrate_compose_fair_harness_cfrpe_hetplasticity_K2_modern_hopfield_cleanup_v1.py (plasticity primitive source)
- Skunkworks META C7 (LAMBDA_GRID excludes 0.0)
- Fix #26 (predispatch verify-the-referent — passed: PROCEED; 0 prior matching landings)
- Fix #28 (per-arm metrics ONLY; discriminating-regime metrics mandatory)
- USER 2026-06-23 (smoke clean synthetic data; not substrate state)
