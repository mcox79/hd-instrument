# exp_dev hand-off -- research: substrate encoder-layer noise robustness 2x drill

Filed-by: research sub-agent
Trigger: notes/research_drill_substrate_encoder_noise_robustness_2x_2026-06-07.md
  (cycle 164 substrate_noise_bft_bge HARD FAIL; 5x encoder degradation vs bge baseline)
Pause state: check data/orchestrator_paused.flag before dispatching any of the three anchors below

Per [[feedback-no-experiment-design-in-prompts]]: this file provides TASK + WHY + CONTRACT + AUTONOMY. Exp_dev designs anchor parameters, sweep grids, threshold formulas, queue placement, and ETA -- NOT this file.

---

## WHY NOW

Cycle 164 confirmed that substrate sign binarization degrades 5x faster than bge under embedding noise. The root cause is identified (sign binarization discards magnitude-based coordinate confidence; near-zero coordinates flip sign easily under noise and count equally in XOR-popcount). Three cheap CPU-only pre-tests can determine whether encoder-noise robustness is recoverable for v2.0 planning without committing engineering time to a full ternary implementation. All three run on laptop CPU with no GPU required, no cloud cost.

The storage-layer-only narrowing for v1.1 is confirmed correct and is NOT being challenged. These pre-tests inform v2.0 planning only.

---

## ANCHOR CANDIDATES (rank-ordered)

### Anchor 1 -- Confidence routing signal feasibility (CPU, ~30 min)
Pointer: research note Section "Cheap Decisive Pre-tests", Pre-test 3
Substrate-product reading: compute per-query near-zero fraction f_i = fraction of bge-large embedding coordinates with |x_j| < tau across 500 queries. Measure correlation between f_i and retrieval error at the substrate layer. If Pearson r > 0.4 between f_i and error, a confidence-based routing signal is valid. Informs whether a hybrid retrieval mode (route uncertain queries to bge fallback) is architecturally justified without any substrate code changes.
Tier hint: laptop CPU; numpy-only; ~30 min wall
Why now: cheapest possible pre-test. Read-only analysis of existing bge-large embeddings. If signal is absent (r < 0.2), both M6 and M7 in the research note are eliminated without further work.

### Anchor 2 -- Bundle ensembling K=1,3,5 effect on noisy retrieval (CPU, ~1 hr)
Pointer: research note Section "Cheap Decisive Pre-tests", Pre-test 2
Substrate-product reading: store K=1, 3, 5 independent jittered bipolar copies of each fact key (additive Gaussian jitter sigma = 0.1 * embedding_norm before binarization). At query time, retrieve against all K copies and take majority-vote top result. Measure recall@10 vs K at noise_sigma = 0.1, 0.2, 0.3. If K=3 achieves recall >= 1.5x baseline (K=1) under sigma=0.2, bundle ensembling is worth 3x storage cost for a high-reliability mode in v1.1 as optional API parameter.
Tier hint: laptop CPU; ~1 hr wall; no GPU needed
Why now: 1-day implementation to add jittered-copy storage + majority-vote retrieval. Pre-test determines whether the implementation is worth doing before writing code.

### Anchor 3 -- Ternary substrate vs bipolar under noisy bge (CPU, ~2 hr)
Pointer: research note Section "Cheap Decisive Pre-tests", Pre-test 1
Substrate-product reading: replace sign() binarization with ternary quantization q(x_i) = +1 if x_i > tau, -1 if x_i < -tau, 0 otherwise, for tau in {0.5, 1.0, 1.5} * coordinate_sigma. Measure recall@10 vs noise_sigma curve for ternary vs bipolar on bge-large and Llama-3.2-1B (to separate encoder geometry from quantization). If ternary recall at sigma=0.2 is >= 1.75x bipolar recall (HP-1 from research note), ternary is worth implementing as a v2.0 path.
Tier hint: laptop CPU; ~2 hr wall; no GPU needed
Why now: this is the highest-stakes pre-test. Ternary implementation requires 3 engineer-days; this pre-test determines whether to spend them. MUST run on both bge-large AND Llama-3.2-1B because cone collapse in bge-large (per BGE d_eff research note, 2026-06-07) may confound the result.

---

## CONTEXT POINTERS

Research note (this handoff's trigger):
  d:/AI/hd-instrument/notes/research_drill_substrate_encoder_noise_robustness_2x_2026-06-07.md

Cycle 164 HARD FAIL (encoder noise baseline):
  data/exp_substrate_noise_bft_bge/metrics.json (or equivalent cycle-164 path)

Cycle 161 HARD PASS (storage layer BFT):
  data/exp_W_matrix_corruption/metrics.json (or equivalent cycle-161 path)

BGE-large d_eff cone collapse finding (relevant: bge near-zero band wider than expected):
  d:/AI/hd-instrument/notes/research_drill_BGE_d_eff_theory_failure_2x_2026-06-07.md

Encoder geometry audit (Llama-3.2-1B isotropic baseline):
  Cycle 140 whitening result (data/exp_llama_1b_whiten*/metrics.json)

---

## CONTRACT

- Exp_dev designs ALL anchor parameters, sweep grids, threshold formulas, queue placement, and ETA
- Exp_dev runs formula self-tests before coding (per [[feedback-strategy-spec-formula-selftests]])
- Exp_dev checks queue.json for name collisions before shipping (per [[feedback-ship-name-collision]])
- ASCII-only in print()/verdict_msg (per [[feedback-ascii-only-in-scripts]])
- All three anchors are LAPTOP CPU; do NOT route to GPU runner (numpy-only scripts)
- Per [[feedback-laptop-run-no-nohup-use-timeout]]: use timeout <s> python ... not nohup; kill any python stragglers before launch
- Pre-test 3 (Anchor 3) MUST run on BOTH bge-large and Llama-3.2-1B; single-encoder result is insufficient
- These are v2.0 PLANNING experiments; do NOT frame as v1.1 feature gates in pre-registration
- Storage-layer-only narrowing for v1.1 is NOT being overturned by these results; pre-reg them as informational

## AUTONOMY DECLARATION

Exp_dev has full autonomy to:
- Decide exact sweep parameters for tau, K, noise_sigma within the ranges specified above
- Choose which anchor to run first (recommended order: 3 -> 2 -> 1, lowest cost first)
- Decide queue placement (local overnight CPU queue preferred)
- Set HARD PASS / HARD FAIL thresholds per research note Section "Falsifiable Predictions"
- Escalate back to research if results are ambiguous or a fourth pre-test is warranted
