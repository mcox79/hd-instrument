# PRE-REG: text8_substrate_pseudoLM_v2_temperature_calibrated_v1

**Date:** 2026-06-23
**Author:** exp_dev (cell author; spawn-and-die)
**Cell:** `experiments/exp_text8_substrate_pseudoLM_v2_temperature_calibrated_v1.py`
**Anchor:** `text8_substrate_pseudoLM_v2_temperature_calibrated_v1`
**Queue routing:** overnight_queue (GPU; per Fix #24 -- cell uses torch.cuda + GPU encoder hoist + batched matmul)
**Parent:** `text8_substrate_pseudoLM_gpu_v1` HARD_FAIL 2026-06-22

## Motivation

Per `notes/research_2x_revival_overnight_negatives_2026-06-23.md` (revival drill):

Parent v1 finding (smoke at N_DIM=4096 N_TRAIN=100k V=4000):
- Substrate BPC 9.371 vs unigram BPC 8.024 (substrate WORSE on BPC).
- BUT substrate top-1 acc 0.198 ~ bigram top-1 acc 0.213 (competitive on accuracy).
- Diagnosis: Hebbian outer-product produces single-spike distributions with low probability
  mass on the correct token when top-1 is wrong; BPC penalizes the spike.

Revival hypothesis: this is a CALIBRATION problem, not a mechanism failure.
- Lit: Stolcke 1998 (log-linear interp); Guo et al 2017 ICML "On Calibration of Modern NNs"
- Standard fix = temperature scaling + log-linear interp w/ unigram
- Parent's "backoff" arm used HARD threshold (substrate_prob < 0.05 -> bigram); log-linear interp
  is the standard composition.

If calibration closes the BPC gap, Path A pseudo-LM becomes viable -- core to bigram-gap closure
and L2 glass-box-LLM vision.

## Cell design

GPU dispatch (Fix #24): torch.cuda + GPU-hoisted encoder + batched matmul for ingest & recall.

Config (FULL):
- N_DIM = 4096
- N_TRAIN = 100,000 tokens (smoke-scale; full at higher N_TRAIN deferred to PASS+1 cycle)
- N_HELD = 20,000 (split into 10k dev / 10k test)
- VOCAB_CAP = 4,000
- INGEST_CHUNK = 8192
- RECALL_BATCH = 1024
- 3 seeds {7, 17, 23}

Held set split:
- dev = first half of held (for choosing best T and best lambda)
- test = second half (for reporting BPC)

Three arms (+ unigram floor):
1. SUBSTRATE_HEBBIAN_BPC_RAW
   - Hebbian W = sum outer(E[w_t+1], E[w_t]); raw softmax at T=1.0 on test.
   - Control (= parent v1 mechanism).
2. SUBSTRATE_HEBBIAN_TEMP_CALIBRATED
   - Sweep T in {0.5, 1.0, 2.0, 5.0} on dev split; report BPC at best-dev T on test.
3. SUBSTRATE_LOG_LINEAR_UNIGRAM
   - p_combined propto exp(lambda * log P_sub + (1-lambda) * log P_uni)
   - Sweep lambda in {0.1, 0.3, 0.5, 0.7, 1.0} on dev split; report best-dev lambda on test.

Plus UNIGRAM_BASELINE on test (CAN-FAIL floor; the BPC bar to beat).

Substrate-only-decode gate: _LLM_CALL_COUNTER = [0] at module top; asserted in metrics.

## Pre-registered HARD bands (from handoff verbatim)

**HARD_PASS (chain-grade, ALL of):**
- best calibrated arm test_BPC <= 7.5 (closes >= 0.5 bits vs unigram 8.024)
- cv across seeds <= 0.10
- substrate-only-decode gate: zero_llm_calls_at_inference = True

**HARD_FAIL (ANY of):**
- best calibrated arm test_BPC >= 8.024 (no calibration arm beats unigram)
- substrate-only-decode gate violated

**MIDDLE_BAND:** best calibrated arm test_BPC in (7.5, 8.024) -- improvement but below target.

## Pre-flight discipline

1. --self-test: encoder determinism + norm + cycle-recall + log-linear endpoint checks
   (lambda=1.0 reproduces substrate; lambda=0.0 reproduces unigram per handoff selftest spec)
   + unigram analytic + LLM counter clean.
2. REQUIRED_FIELDS: anchor, anchor_name, verdict, verdict_msg, summary, elapsed_s, run_mode,
   n_seeds, detail, per_seed, zero_llm_calls_at_inference, n_llm_calls.
3. Per-seed checkpoint via _seed_checkpoint (resumable_seeds + write_partial).
4. atexit/SIGTERM synthesizer.
5. ASCII-only (no unicode).
6. PROT-020 OK (imports torch; GPU queue routing justified).
7. Fix #24 GPU mandate: encoder + W on GPU; matmul on GPU; per-batch sync every 16 batches.

## Honest scope

- Calibration is POST-HOC (temperature + log-linear interp on dev split). Does NOT modify the
  Hebbian W ingest itself. If HARD_PASS, NEXT cycle can scale to full N_TRAIN=1M / V=20000.
- Held split is in-sequence (dev first, test second); could leak temporal drift if text8 has
  trend. Mitigation: text8 is shuffled-ish Wikipedia text; no strong temporal trend expected.
- 5-knob lambda grid + 4-knob T grid; finer search deferred to PASS+1 cycle.

## 2x-revival angle (if HARD_FAIL or MIDDLE_BAND)

- Per-context calibration (T per source-token frequency tier)
- Log-linear w/ bigram (instead of unigram) -- composition rises with stronger prior
- Add length-norm / position-conditional calibration
- Scale N_TRAIN x10 (1M tokens) to see if calibration gap shrinks with more data

## Cites

- `notes/research_2x_revival_overnight_negatives_2026-06-23.md` (revival drill)
- `notes/exp_dev_handoff_research_2x_revival_overnight_negatives_2026-06-23.md` (handoff)
- Stolcke 1998 ICASSP "Entropy-based Pruning of Backoff LMs"
- Guo et al 2017 ICML "On Calibration of Modern Neural Networks"
- Parent: parent prereg + `data/exp_text8_substrate_pseudoLM_gpu_v1_smoke_remote/metrics.json`
