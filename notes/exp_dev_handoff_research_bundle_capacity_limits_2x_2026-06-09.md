# exp_dev hand-off -- research: bundle capacity limits 2x

Filed-by: research sub-agent (Sonnet 4.6), 2026-06-09
Trigger: notes/research_drill_bundle_capacity_limits_2x_2026-06-09.md
Pause state: check data/orchestrator_paused.flag before dispatching

Per [[feedback-no-experiment-design-in-prompts]]: this file names anchor candidates and WHY-NOW
context only. exp_dev designs all sweep parameters, thresholds, and queue choices autonomously.

---

## Anchor candidates (rank-ordered)

### 1. Per-shard capacity multiplier validation (HIGHEST PRIORITY, 5-10 min CPU)
Anchor pointer: bundle_capacity_shard_multiplier_cpu_v1
Substrate-product reading: HP-1 in research note -- at N=4096, P=20 shards with K/P items per
  shard, total K=1000 items distributed uniformly, should achieve recall > 0.99 per shard.
  This is the fastest decisive test of the compound capacity model (PP-244 + PP-127 sharding).
  HARD-PASS: mean recall > 0.995 across shards at K=1000 total / P=20. HARD-FAIL: recall drops
  below 0.90 when K_per_shard < 0.5 * kstar (would indicate cross-shard contamination).
Tier hint: Tier 1 (directly tests the most important product-relevant capacity lever already deployed)
Why-now: PP-244 established kstar=200 per flat bundle. Sharding is in production. We do NOT yet
  have a clean empirical measurement of the compound capacity (P * kstar). This is the missing
  characterization that closes the "how many total facts can the substrate hold?" product question.

### 2. Learned (near-orthogonal) codebook vs random codebook (15 min CPU)
Anchor pointer: bundle_capacity_orthogonal_codebook_cpu_v1
Substrate-product reading: HP-4 in research note -- Gram-Schmidt orthogonalized codebook (K <= N)
  vs standard random FHRR codebook at K=150 (75% of kstar). HARD-PASS: orthogonal codebook
  achieves recall > 0.999 vs random codebook ~0.85 at K=150; gap > 10pp confirms learned
  codebook is worth engineering. HARD-FAIL: orthogonal codebook performs worse than random
  (would indicate semantic structure is helping retrieval, reversal of prior assumption).
Tier hint: Tier 1 (closes the "can we 2-3x capacity by optimizing atoms?" question cheaply)
Why-now: Research drill identifies this as the lever that bridges 0.0488 empirical to 0.14N
  theoretical Hopfield floor. If it works, it directly closes the theory-empirical gap.
  Gram-Schmidt is O(K*N) CPU, trivial for K=200 at N=4096. 

### 3. Population coding (P=10 ensemble) at K=2*kstar cliff (5 min CPU)
Anchor pointer: bundle_capacity_ensemble_cliff_cpu_v1
Substrate-product reading: HP-3 in research note -- 10 independent substrate instances, majority
  vote at K=400 (2x kstar). HARD-PASS: ensemble recall > 0.95 at K=400 (vs single-instance ~0.794).
  HARD-FAIL: ensemble recall < 0.80 at K=400 (Gaussian independence assumption violated).
Tier hint: Tier 1 (validates PP-249 ensemble gain specifically at the bundle capacity cliff, not
  just at the earlier accuracy floor)
Why-now: PP-249 measured ensemble gain on NOISY QUERIES at K=200. This anchor measures ensemble
  gain at the CAPACITY CLIFF (K=2*kstar, where single-instance recall has already degraded). These
  are different operating regimes. The K=400 cliff is where customers will actually push the system.

### 4. GHRR block-diagonal vs flat FHRR bundle capacity comparison (10 min CPU)
Anchor pointer: bundle_capacity_ghrr_vs_flat_cpu_v1
Substrate-product reading: HP-2 in research note -- GHRR with 4 blocks of N/4=1024 vs flat FHRR
  at N=4096. Measure K* for each (at 50% recall threshold). HARD-PASS: GHRR K* > 1.5x flat FHRR K*.
  HARD-FAIL: GHRR K* < 1.1x flat FHRR K* (block structure provides no measurable bundle gain).
Tier hint: Tier 2 (confirms or refutes the block-diagonal bundle capacity gain; lower priority than
  1-3 because GHRR is a larger implementation change)
Why-now: Drill 7 confirmed GHRR for some use case but that may have been binding capacity not
  bundle capacity. This anchor isolates the bundle superposition regime specifically.

---

## Context pointers

- Research note: d:/AI/hd-instrument/notes/research_drill_bundle_capacity_limits_2x_2026-06-09.md
- PP-244 result: substrate_capability_map.md (kstar/N=0.0488 at N=4096, kstar=200)
- Cycle 178 cliff measurement: bundle_capacity_cliff_gpu_v1 HF (K_crit=200, K400=0.794)
- Cycle 180 large-N measurement: bundle_capacity_largeN_gpu_v1 MIDDLE_BAND (N8192 K_crit=662)
- PP-249 (ensemble coding): lap9_population_substrate_cpu_v1 HP (P=10, gain +12pp)
- Per-predicate sharding: PP-127/131/132/147 (in production)
- GHRR paper: arxiv 2405.09689 (Generalized HRR, block-diagonal structure)

---

## Contract

The research note provides falsifiable prediction bands. exp_dev is responsible for:
- Designing sweep parameters independently (K range, N, P, block sizes)
- Pre-registering HARD-PASS / MIDDLE-BAND / HARD-FAIL per envelope-fail-bands feedback
- Routing to correct queue (CPU for all anchors above; no GPU required)
- Following feedback-small-scale-first-methodology: smoke at K=50,100 before full sweep
- Following feedback-pre-dispatch-speed-harden-progress: JSONL streaming, resume capability

## Autonomy declaration

exp_dev decides: exact K sweep points, N values, P values, codebook construction method,
GHRR block count, ensemble size. The research note provides the WHAT; exp_dev owns the HOW.
Do not re-consult Research for parameter values; the note is complete.
