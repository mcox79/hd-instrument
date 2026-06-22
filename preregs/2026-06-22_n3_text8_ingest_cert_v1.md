# Pre-registration: n3_text8_ingest_cert_v1

**Date:** 2026-06-22
**Anchor name:** n3_text8_ingest_cert_v1
**Script:** experiments/exp_n3_text8_ingest_cert_v1.py
**Queue:** remote_cpu_queue (smoke arm first; full TBD by Director on smoke-green)
**Authority:** exp_dev (per parent prompt: "first ingest-breadth expansion. text8 was Exp-Dev pre-STANDSTILL N3 primary cert corpus; never executed.")
**Bands source:** Skunkworks N3 absolute-floor (notes/skunkworks_to_expdev_research_cc_orch_N3_corpus_eval_cert_bands_canonical_BPC_benchmark_2026-06-21.md) + Exp-Dev N3 corpus scope-DECISION (notes/exp_dev_to_research_N3_corpus_scope_DECISION_2026-06-21.md)
**Composes with:** N1 v3.1 token-level substrate-LM (architecture-agnostic eval; text8 is CHAR-level so SubstrateCharLM is the substrate-LM plugged in for text8).

---

## What this tests

First exp on the field-standard text8 char-level benchmark (first 100MB of cleaned
Wikipedia, 27-char vocab a-z + space). Substrate-native 4-primitive char-LM
(SubstrateCharLM) trained Hebbian/anti-Hebbian on text8 train + scored char-BPC on
held-out validation. Absolute-floor cert-bands replace the gameable ratio band
(phase_d_tier6 lesson). Zero LLM forward calls at inference (substrate-only-decode).

---

## Configurable params (defaults pre-registered here)

| Param         | Full default | Smoke default | How to set                    |
|---------------|--------------|---------------|-------------------------------|
| N_DIM         | 4096         | 512           | HDLAB_N_DIM or --n-dim        |
| N_LAYERS      | 4            | 2             | HDLAB_N_LAYERS env            |
| ALPHA_MAX     | 0.10         | 0.10          | HDLAB_ALPHA_MAX env           |
| N_STEPS/LAYER | 3            | 2             | HDLAB_N_STEPS_PER_LAYER env   |
| MAX_CHARS_TRAIN | 2_000_000  | 10_000        | HDLAB_MAX_CHARS_TRAIN env     |
| MAX_CHARS_TEST  | 100_000    | 1_000         | HDLAB_MAX_CHARS_TEST env      |
| SEEDS         | [7,17,23]    | [7]           | HDLAB_SEEDS env (comma)       |
| ALLOW_SYNTHETIC | False (LOCKED) | False     | code-locked: fail-loud only   |

Smoke is tuned to fit the queue_add SMOKE_TIMEOUT_S=180s local-gate (measured ~0.8s wall).

---

## Substrate-LM choice (architecture-agnostic resolution)

Parent prompt cites "N1 v3.1 substrate-LM" -- N1 v3.1 is TOKEN-level (pythia residual
per-token + concept VQ). text8 is CHAR-level by convention; the substrate-native CHAR
LM is `testbed.substrate_lm.char_lm.SubstrateCharLM` (validated by N3 Shakespeare
shakedown). Per Research's N3 architecture-AGNOSTIC ruling, N3 grades WHICHEVER
substrate-native LM is plugged in. This cell plugs SubstrateCharLM in for text8.

A separate token-level text8 cell (N1 v3.1 + text8 BPE tokenizer) could be authored
later to evaluate the token-LM on text8 corpus -- not in scope here.

---

## Pre-registered verdict bands (parent-prompt absolute-BPC, replaces ratio band)

**HARD_PASS (chain-grade):**
  substrate_bpc_mean <= 1.90 (beats 5-gram-KN literature baseline)
  AND cv <= 0.05 across seeds (seed-stable)
  AND substrate-only-decode verified (zero LLM forward calls; structural + counter-asserted)
  AND gain_vs_bigram_ceiling >= 0.05 (substrate beats by-construction floor by meaningful margin)
  AND corpus_provenance_real = True (allow_synthetic=False, real text8)
  AND no primitive collapse

**MIDDLE_BAND:**
  substrate_bpc_mean in (1.90, 3.00]  (between 5-gram-KN and bigram baselines)
  OR (HARD_PASS BPC + cv > 0.05): seed-unstable demote
  OR (HARD_PASS BPC + gain_vs_ceiling < 0.05): by-construction-saturation demote

**HARD_FAIL:**
  substrate_bpc_mean > 3.00 (worse than text8 bigram baseline; no real structure)
  OR any LLM forward call in inference path (substrate-only violated)
  OR corpus_provenance_real == False (synthetic-fallback fail-loud)
  OR any primitive collapse

The HARD_PASS direction is correctly oriented (lower BPC = better; threshold is the
upper-bound substrate must FALL BELOW). Verdict logic asserted in T7 selftest.

---

## Text8 literature absolute-floor reference (the bar ladder)

- uniform-27   = log2(27) ~= 4.755
- bigram       ~ 3.00 BPC  (=> MIDDLE_BAND upper)
- 5-gram-KN    ~ 1.70-1.90 BPC  (=> HARD_PASS upper)
- PPM          ~ 1.40-1.55 BPC
- Shannon human ~ 0.60-1.30 BPC

---

## By-construction guards (Skunkworks N3 spec compliance)

1. **NO LEAK:** deterministic 90/5/5 char-position split of single-file text8 (per
   `testbed.substrate_lm.data.text8_char_corpus`). Train + test ranges non-overlapping
   by construction. Bigram baseline counts fit on TRAIN, scored on TEST.

2. **VQ-FLOOR analog (bigram-ceiling):** for a CHAR-LM with no explicit concept VQ
   codebook, the analog of the VQ-granularity floor is `bigram_ceiling_bpc` =
   bigram-MLE FIT ON TEST itself (the irreducible bigram-context entropy on held-out).
   This is the tightest floor a bigram-context architecture can achieve. The
   load-bearing claim is `gain_vs_ceiling = bigram_ceiling - substrate`. If
   substrate ~ bigram_ceiling, substrate is doing nothing beyond bigram-lookup
   (by-construction-saturated; HARD_PASS demoted to MIDDLE_BAND).

3. **Substrate-only-decode is the CEILING, not a target:** the substrate cannot beat
   an ingested-LLM (it distills from it). Distillation gap is reported but NOT a
   verdict criterion. (This cell ingests no LLM; SubstrateCharLM is purely Hebbian.)

4. **CORPUS_PROVENANCE_REAL = True asserted + LOGGED:** ALLOW_SYNTHETIC=False
   passed to loader (fail-loud per phase_d_tier6 wikitext2 silent-fallback lesson).
   Also independently fingerprinted at runtime (real text8 has 27-char vocab in
   {a-z + space}; synthetic fallback has ~78-char vocab -- vocab-size mismatch
   would surface).

5. **Substrate-only code-trace:** this cell imports NO transformers/torch.
   SubstrateCharLM imports no transformers. `_LLM_CALL_COUNTER` asserted == 0 before
   metrics write. T4 selftest validates the counter stays at 0 through the pipeline.

6. **cv <= 0.05 required for HARD_PASS:** computed across 3 seeds for the full run.
   Smoke (1 seed) cannot satisfy this; smoke is structural validation only.

---

## Instrumentation (Skunkworks N2 chain-grade structural blockers, all 4 baked)

1. **per_unit**: per-seed entry stored in `per_seed`; recompute-off-per_unit ready.
2. **cv <= 0.05**: computed across seeds in verdict().
3. **zero_llm_calls_at_inference: True LOGGED** in metrics (asserted False if any
   call sneaked in; structural guarantee + counter audit).
4. **VQ-floor decomposition** = `bigram_ceiling_bpc` per seed; the load-bearing
   gain = `bigram_ceiling - substrate` reported per-unit.

---

## Config version (checkpoint invalidation)

`N=<NDIM>,LAYERS=<NLAYERS>,ALPHA=<ALPHA>,STEPS=<STEPS>,V_CHAR=27,CORPUS=text8,
CORPUS_VER=matt_mahoney_2006,TRAIN=<MAXTRAIN>,TEST=<MAXTEST>,SEEDS=<SEEDS>,
SYNTH=False,BANDS=HP<=1.90/MB<=3.00`

Any change to any of these invalidates existing per-seed checkpoints (PROT-021
guard via `experiments/_seed_checkpoint.py` + run_config dict).

---

## Seeds

- Full run: SEEDS = [7, 17, 23] (3 seeds; cv computed across all 3)
- Smoke:    SEEDS = [7] (single-seed pipeline validation only; cv undefined)

---

## Timeout estimate

**Smoke arm** (this dispatch):
- Measured local wall (cached text8, 10k train / 1k test, N=512, 2 layers, 2 steps):
  ~0.8s on Windows laptop CPU
- Remote_cpu_queue is roughly similar-class CPU. Smoke wall on remote:
  estimated **<= 60s** (allow 10x margin)
- queue_add SMOKE_TIMEOUT_S default 180s: ample headroom
- **Smoke entry timeout pre-reg: 600s** (safety margin for runner overhead)

**Full run extrapolation** (held in queue but NOT dispatched in this turn):
- Per-seed wall ~ smoke_wall * (FULL_N/smoke_N)**1.5 * (FULL_TRAIN/smoke_TRAIN)
  = 0.8 * (4096/512)**1.5 * (2_000_000/10_000)
  = 0.8 * 22.6 * 200
  = ~3620s (60min) per seed
- 3 seeds * 3620s * 1.5 margin = ~16290s (4.5 hours)
- This exceeds 14400s (4h) -- if/when Director dispatches FULL, will need
  --allow-no-checkpoint NOT needed (per-seed checkpoint is on),
  OR cap MAX_CHARS_TRAIN at 1M and re-estimate (the smaller corpus still vastly
  exceeds bigram convergence ~ 1M chars on 27-vocab).
- **Full entry timeout pre-reg: 18000s** (5 hours; flag noted; Director may scope down
  TRAIN to fit a 4h cap)

---

## Dispatch plan (this prereg covers SMOKE only)

1. Self-test PASS (8/8) on .venv -- DONE.
2. Local smoke wall measured -- DONE (~0.8s).
3. queue_add to remote_cpu_queue with --timeout 600 (smoke; queue_add's local
   smoke gate validates the cell, then queues for remote runner).
4. Return after dispatch confirmation (queue.json entry present).
5. Director polls smoke result on remote; on smoke-green dispatches FULL via
   a follow-up queue_add (separate prereg cycle: tighten TRAIN cap if needed,
   set --timeout 18000 or per Director's scope ruling).

---

## N-suffix note (PROT-018)

Anchor `n3_text8_ingest_cert_v1` has no `_nN` suffix. N is configurable via
HDLAB_N_DIM env (smoke=512, full=4096). Per PROT-018 rule 3: no _nN suffix
because N is sweepable.

---

## Risk surface (honest)

- text8 download (~100MB) on first remote run if not cached on remote. The
  loader caches under data/text8_cache/text8.txt after download. Locally cached
  (verified 100MB file). REMOTE may not have it; first remote smoke includes
  the download in wall.
- SubstrateCharLM at N=512 + 10k chars almost certainly DOES NOT learn (smoke
  validates HARNESS, not learning). Expected smoke verdict: HARD_FAIL with
  substrate_bpc ~ 4.7 (near uniform). This is OK -- queue_add gates on
  metrics-shape, not verdict-PASS. The full run at N=4096 + 2M chars is where
  learning is expected (target HARD_PASS <= 1.90 vs 5-gram-KN).
- Architecture-agnostic eval boundary may need Skunkworks SCHEMA-VET: this
  cell plugs SubstrateCharLM (CHAR-level) in for text8. If Skunkworks/Research
  prefer a token-level substrate-LM on text8 BPE, that's a separate v2 cell.
- N1 v3.1 referent NOT plugged in (token-level vs char-level grain mismatch).
  Honest surfacing of the boundary; parent prompt cited N1 v3.1, but text8's
  established baselines (bigram/5-gram-KN) are char-level by convention.
