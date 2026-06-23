# Pre-reg: encoder_dual_gain_softhebb_v1 (Shannon-floor META branch-3 PIVOT)

**Date:** 2026-06-23
**Anchor:** encoder_dual_gain_softhebb_v1
**Cell:** experiments/exp_encoder_dual_gain_softhebb_v1.py
**Queue:** remote_cpu_queue (numpy-only; N_DIM=4096; matmul-bound; laptop CPU full ~60min; remote_cpu both idle per USER 2026-06-22 GPU underutilization directive)
**Run-mode:** full (smoke for gate)
**Author:** Exp-Dev (cell author + dispatch)
**Pre-reg source-of-truth:** notes/research_5x_deeper_encoder_upgrade_dual_gain_2026-06-23.md
**Handoff:** notes/exp_dev_handoff_research_5x_deeper_encoder_upgrade_dual_gain_2026-06-23.md

## Question

Does a substrate-native learned/structured encoder rescue cleanup at sigma=1.5 AND close the substrate-LM BPC gap to unigram, simultaneously? This fills branch #3 of the Shannon-floor META (cert row 675) and tests Research's dual-gain prediction that a single encoder upgrade lifts BOTH cleanup AND Path-A.

## Substrate-native arms (USER directive 2026-06-22 compliant; no MiniLM / no BGE / no proprietary)

1. **ARM_CHAR_TRIGRAM** -- existing `hdlab/char_trigram_encoder.py`; branch-3 baseline ("learned-keys" via deterministic hash-bipolar trigram bundling).
2. **ARM_SOFTHEBB_FORWARD** -- forward-only soft-WTA Hebbian encoder (Journe-Caporale / Moraitis 2021); single linear layer on top of char-trigram input; trained streaming-Hebbian on text8; soft top-k WTA selection at write.
3. **ARM_FOLDIAK_ANTI_HEBB** -- Foldiak 1990 lateral-inhibition decorrelation; W_lateral subtraction during write applied to codebook entries (substrate auto-whitens its own codebook on the fly).
4. **ARM_FPE_CONTRASTIVE_FORWARD** -- Forward-Forward (Hinton 2022) 2-phase Hebbian update; positive phase on (real_input, real_output), negative phase decrement on sampled negatives. Pure forward; no backprop.

All four arms ingest the **same upstream char-trigram bundled input** from text8; each arm RE-ENCODES via its own encoder into a substrate codebook atom.

## Config (full)

- N_DIM = 4096
- M = 200 (cleanup codebook size)
- N_EVAL = 200
- Seeds = [7, 17, 23]
- Sigmas (cleanup sweep) = [0.0, 0.5, 1.0, 1.5, 2.0]
- DISCRIMINATOR_SIGMA = 1.5
- text8 N_TRAIN = 100_000 tokens (path-A BPC)
- text8 N_HELD = 20_000 tokens (path-A BPC eval)
- VOCAB_CAP = 4000
- INGEST_CHUNK = 8192
- LAMBDA_GRID = [0.1, 0.3, 0.5, 0.7, 1.0] (log-linear interp w/ unigram; lambda=1.0 = pure substrate sanity)

## Pre-reg HARD bands

### Metric A: cleanup recall@1 at sigma=1.5 (per arm)

- **HARD_PASS_CLEANUP:** recall(sigma=1.5) >= 0.20 AND cv <= 0.30 (production-meaningful lift; ~9x baseline 0.022)
- **HARD_FAIL_CLEANUP:** recall(sigma=1.5) <= 0.05 (within 2.3x baseline; null)
- **MIDDLE_BAND_CLEANUP:** 0.05 < recall(sigma=1.5) < 0.20

### Metric B: substrate-LM BPC on text8 held (per arm)

- **HARD_PASS_BPC:** best_calibrated_BPC < 7.738 (substrate finally beats unigram) AND cv <= 0.05
- **HARD_FAIL_BPC:** best_calibrated_BPC >= 7.864 (no improvement over current text8 v2 calibrated cell)
- **MIDDLE_BAND_BPC:** 7.738 < BPC < 7.864

### Cell-level verdict (chain-grade candidate)

- **HARD_PASS (chain-grade tier candidate):** ANY arm clears BOTH Metric A AND Metric B simultaneously (dual-gain confluence; substrate-product unblock; triple-leverage primitive).
- **HARD_FAIL (Shannon-floor scope-wide saturated):** NO arm clears EITHER Metric A or Metric B; branch #3 closes; META promoted to chain-grade scope-wide. Substrate-as-LM structurally dead with current architectures.
- **MIDDLE_BAND (partial mechanism):** one or more arms clears Metric A only OR Metric B only; characterize as measured-mechanism; route to second-tier follow-up.

## Sanity gates (CONFOUND_FAIL detector)

- **sigma=0 sanity:** all 4 arms must produce recall@1=1.000 at sigma=0 (clean cue -> exact recovery by construction). Failure = implementation bug; NOT mechanism rejection.
- **lambda=1.0 BPC sanity:** lambda=1.0 in log-linear interp = pure substrate (no unigram weight); BPC at lambda=1.0 should be substrate's raw BPC (sanity for Metric B interp).

## Wall budget

- Smoke (1 seed, N_TRAIN=10k, N_HELD=2k, N_EVAL=50): target <= 5 min CPU.
- Full (3 seeds, N_TRAIN=100k, N_HELD=20k, N_EVAL=200): estimated 20-40 min CPU (no GPU needed; numpy matmul N=4096 x V=4000 ~ acceptable on remote CPU).
- Per Fix #17: timeout = ceil(1.5 * smoke_wall_s * (FULL_N/smoke_N)^1.5 * (FULL_seeds/smoke_seeds)) -- expect ~3600s timeout cap.

## Implementation notes

- ASCII-only per `feedback_ascii_only_in_scripts`.
- numpy-only (no torch needed at N=4096; remote_cpu_queue gate accepts numpy when N<16384).
- Per-seed checkpoint + restartable via `experiments/_seed_checkpoint.py`.
- atexit synthesizer (per Skunkworks #4) -- always produce metrics.json even on timeout / SIGTERM.
- _LLM_CALL_COUNTER = [0] (substrate-only-decode gate; zero LLM at inference).
- Mechanism implementations:
  - **SoftHebb forward:** W initialized small; for each text8 token-pair (x_t, x_{t+1}) compute z = W @ x_t; apply soft-WTA (softmax * top-k mask, k=5); update W += eta * (z_topk[:, None] @ x_t[None, :] - eta * W * z_topk). No backprop. Forward-only.
  - **Foldiak anti-Hebb:** maintain lateral W_lat (M x M); during codebook write, codebook[i] -= sum_{j != i} W_lat[i, j] * codebook[j]; update W_lat via anti-Hebb: W_lat[i, j] += eta * y_i * y_j - decay * W_lat[i, j] where y = sign(codebook @ x).
  - **Forward-Forward contrastive:** positive phase (real x_t, real x_{t+1}) -> W += eta * outer(x_{t+1}, x_t); negative phase (real x_t, sampled negative x_neg from unigram) -> W -= eta * outer(x_neg, x_t). Pure forward; no backprop.
- For Metric A: each arm produces M=200 codebook atoms (from first 200 text8 word types after vocab cut); cleanup-recall@1 over sigma sweep with gaussian noise.
- For Metric B: each arm produces V=4000 vocab encoder + Hebbian LM; same log-linear+unigram calibration pipeline as text8 v2 cell.

## Per-Fix discipline

- **Fix #26 (pre-dispatch verify-the-referent):** `tools/predispatch_check.py encoder_dual_gain_softhebb_v1` -> PROCEED (0 prior matches).
- **Fix #20 (no pipe-tail subprocess monitoring):** monitor via mtime polling.
- **Fix #28 (per-arm metrics, not summary verdict):** post-landing, run `tools/peek_arm_metrics.py` on metrics.json BEFORE propagating cross-arm narratives.
- **Long-cells discipline:** per-unit per-seed checkpoint via `_seed_checkpoint.write_partial_key`; smoke + full both restartable.
- **ASCII-only:** all print(), verdict_msg.

## Cites

- notes/research_5x_deeper_encoder_upgrade_dual_gain_2026-06-23.md (source-of-truth)
- notes/research_encoder_side_cleanup_ceiling_break_2026-06-23.md (parent; ENC1 HARD_FAIL)
- Shannon-floor META cert row 675 (chain-grade-eligible per branch-c closure)
- experiments/exp_text8_substrate_pseudoLM_v2_temperature_calibrated_v1.py (Path-A baseline cell; 7.864 BPC)
- experiments/exp_enc1_structured_n_lift_v1.py (parent encoder-side; HARD_FAIL on synthetic)
- hdlab/char_trigram_encoder.py (substrate-native baseline + ARM_CHAR_TRIGRAM)
- Moraitis et al. 2021 / 2107.05747 (SoftHebb foundation)
- Foldiak 1990 Biol Cybern (anti-Hebbian decorrelation)
- Hinton 2022 Forward-Forward (no-backprop contrastive)
- USER directive 2026-06-22 (no MiniLM; no BGE)
- USER directive 2026-06-22 (GPU underutilization -> route heavy cells via remote)

-- Exp-Dev
