# Pre-registration: phase_diagram_working_memory_multibank_K_extension_to_16384_v1

**Date:** 2026-06-25
**Anchor:** phase_diagram_working_memory_multibank_K_extension_to_16384_v1
**Queue:** overnight_queue (GPU; Fix #24 mandate)
**Author:** exp_dev (USER-directed; 2026-06-25)

## Strategic intent — phase-diagram K-extension closure

Multi-bank K=4096 chain-graded (`exp_substrate_working_memory_multi_bank_K_extension_adversarial_v1` 2026-06-25, MULTI_64x recall=0.9927 cv=0.0006, adversarial within 0.05). Phase-diagram map question: where does K cliff above 4096? Brain working-memory effective capacity is ~7+/-2 conscious items but routing/binding capacity at substrate level is much higher. Need to map cliff for production deployment confidence (USER 2026-06-25: "we understand where everything operates best within the phase diagram").

## Mechanism (reused from v1 K-extension; GPU-batched)

Per (seed, K_total, n_banks, regime):
- Build codebook of CODEBOOK_SIZE bipolar items at N_DIM=8192
- For RANDOM regime: items are independent random bipolar
- For ADVERSARIAL regime: items grouped into 4 groups; first FEATURE_OVERLAP_FRAC=0.20 of bits copied from group template (shared-prefix). Same construction as v1; same controlled query ambiguity.
- Multi-bank write: items partitioned into n_banks of k_per_bank=K_total/n_banks; each bank tagged + bipolar-quantized sum of (item * slot_tag)
- Query: bank-route via bipartite tag cleanup; slot-decode via cleanup-to-codebook (one extra iteration of mixture)
- Baseline arms: ARM_KNN_BASELINE (top-1 over codebook on noised key at small M=400; sentinel >= 0.9), ARM_NAIVE_SINGLE_BANK (single bank; cliffs naturally past K~64; reproduces 0.0020 floor)

GPU-batched: codebook + slot_tags + bank_tags allocated as torch fp16 cuda tensors. Per-bank writes and reads use batched matmul (torch.matmul on (n_banks, k_per_bank, N_DIM) tensors). Eval-loop hoisted: noised cues batched across n_eval_items at once. NO per-item Python loop in inner cleanup path.

## Sweep design

K_SWEEP and arrangements:
- K=4096 [MULTI_64x] (rail; reproduces 0.9927 within 0.02; load-bearing sanity)
- K=8192 [MULTI_64x, MULTI_128x] (2x extension; novel)
- K=16384 [MULTI_128x, MULTI_256x] (4x extension; novel)

Each at RANDOM + ADVERSARIAL (FEATURE_OVERLAP_FRAC=0.20) for cross-regime robustness.

Plus rail arms (at K=4096 only; sentinels):
- ARM_KNN_BASELINE M=400 (Fix #28 sentinel; >= 0.9)
- ARM_NAIVE_SINGLE_BANK (reproduces ~0.002 floor)

Per-K config:
- K=4096:  k_per_bank=64 in MULTI_64x   (64 banks * 64 slots)
- K=8192:  k_per_bank=128 in MULTI_64x  (64 banks * 128 slots — k_per_bank above chain-grade envelope; DISCRIMINATOR arm)
            k_per_bank=64 in MULTI_128x (128 banks * 64 slots — preserves chain-grade envelope)
- K=16384: k_per_bank=128 in MULTI_128x (128 banks * 128 slots — DISCRIMINATOR)
            k_per_bank=64 in MULTI_256x (256 banks * 64 slots — preserves chain-grade envelope)

## Pre-registered bands (LOCKED at module init via assert)

### CHAIN_GRADE_K_EXTENDS_TO_16384 (HARD_PASS)
- K=8192 best arm recall_mean >= 0.95 (random) AND adversarial within 0.05
- K=16384 best arm recall_mean >= 0.95 (random) AND adversarial within 0.05
- All passing arms: cv across 3 seeds <= 0.05
- All passing arms: k_per_bank >= 64 AND <= 64 (preserves Cell D chain-grade envelope; per META rule)
- All arms: route_acc_mean >= 0.95
- Rail check: K=4096 MULTI_64x recall reproduces 0.9927 within +/-0.02
- ARM_KNN_BASELINE sentinel: top1 >= 0.9 at M=400 (Fix #28; no broken metrics)
- substrate-only gate: n_llm_calls == 0

### PARTIAL_K_EXTENDS_TO_8192 (MIDDLE_BAND)
- K=8192 chain-grade (best arm >= 0.95 random AND adversarial within 0.05 AND cv <= 0.05)
- K=16384 partial: best random recall in [0.50, 0.95) OR adversarial > 0.05 below random OR cv > 0.05

### K_4096_IS_CEILING (HARD_FAIL)
- K=8192 best arm recall < 0.50 in random regime
- (Indicates K-extension does not scale past saturated K=4096 rail)

### ADVERSARIAL_BREAKS_AT_K_EXT (HARD_FAIL)
- At K=8192 OR K=16384: adversarial recall drops by >= 0.30 vs random best arm
- (Routing layer fails under query ambiguity at extended scale)

### CV_INSTABILITY (HARD_FAIL)
- Any K_total has best arm cv > 0.10 across seeds

### Q-DISCIPLINE saturation guard
- Any arm reports recall >= 0.995 with cv == 0: flag BIAS-Q `_q_suspect_saturation = True` in metrics; verdict_msg notes; not HARD_FAIL but cert-tier reduced

### Direction-honor
- Per (K, regime, arm): adversarial recall must be <= random + 0.02 (adversarial cannot beat random; if violated, MEASUREMENT_BUG flag)

## GPU mandate (Fix #24)

- `import torch` at module top (PROT-020 gate)
- `torch.cuda.is_available()` strict-required for full run; abort cleanly with `GPU_MANDATE_VIOLATED` on no-CUDA
- All heavy tensors (codebook, slot_tags, bank_tags, workspaces) allocated on `cuda:0` in fp16
- Per-bank writes use batched matmul: workspaces = (items_per_bank * slot_tags).sum(dim=1) shape (n_banks, N_DIM)
- Eval-loop noised cues batched: cues = CUE_COS * bank_tags[bank_true] + noise_scale * noise shape (n_query, N_DIM); sims = cues @ bank_tags.T
- nvidia-smi util sampled every arm; gpu_util_mean reported; smoke gate requires gpu_util_p50 >= 50 (Fix #24)
- metrics report: gpu_avail, gpu_name, gpu_max_mem_alloc_mb, gpu_util_mean, gpu_util_p50, gpu_util_max, gpu_util_n_samples

## Memory budget (K=16384, n_banks=256, V_C=32768, N=8192, fp16)

- codebook: 32768 * 8192 * 2 = 537 MB
- slot_tags max (k_per_bank=128): 128 * 8192 * 2 = 2 MB
- bank_tags max (n_banks=256): 256 * 8192 * 2 = 4 MB
- workspaces max: 256 * 8192 * 2 = 4 MB
- Per-bank write transient: (n_banks=256, k_per_bank=128, N=8192) fp16 = 537 MB (allocate per bank loop; del after each bank)
- Per-eval batched cues: (n_eval, N) fp16 = trivial
- Peak: ~1.1 GB during a bank-write; well within 8 GB 4060Ti budget

## Smoke gate (BLOCKING; per Fix #17)

- N_DIM=2048; CODEBOOK_SIZE=4096
- K_SWEEP=[1024, 4096]; arrangements limited to one per K
- N_ITEMS_PER_K=80; SEEDS=[11]
- Verify: gpu_util_p50 >= 50% (Fix #24); n_llm == 0; valid metrics.json with required fields
- Verify rail: K=1024 MULTI_32x recall >= 0.95 (consistent with v1 rail)
- Verify K=4096 MULTI_64x recall >= 0.80 (loose smoke band; full has stricter rail check 0.9927 +/- 0.02)

## Q-discipline (META + bias rules)

- META_M6: ARM_KNN_BASELINE measured IN-CELL at same N=8192 (not borrowed)
- META_M7: smoke matches full on N_DIM-affecting params; only N_ITEMS_PER_K + SEEDS + K_SWEEP reduce
- BIAS-Q: any arm recall >= 0.995 with cv == 0: flag suspect saturation
- BIAS-N (verify-referent): rail-check K=4096 MULTI_64x recall reproduces v1 result within tolerance; logs cross-cell ratio
- BIAS-P (anisotropy): codebook items are bipolar random (RANDOM regime) or controlled-overlap shared-prefix (ADVERSARIAL); both isotropy-controlled by construction
- BIAS-S (band calibration): bands derived from v1 K-extension chain-grade rails; same k_per_bank=64 envelope; same recall floor 0.95 + cv 0.05

## Routing

`overnight_queue` (GPU). Per USER directive 2026-06-26 + Fix #24.

## Resume + checkpoint discipline

- `experiments/_seed_checkpoint.write_partial_key` per (seed, K_total, regime, arm); resumable from any partial set
- `_ckpt_key = "seed%d_K%d_regime%s_arm%s"`
- CONFIG_VERSION includes every recall-affecting param; PROT-021 config-mismatch guard active

## Estimated wall (timeout planning)

- v1 K=4096 took ~467s/unit on CPU at N=4096; GPU at N=8192 with batched matmul expected ~250s/unit at K=16384
- 3 seeds * 3 K-points * 2 regimes * (avg 1.5 arrangements/K) * 250s ~= 6750s ~= 1.9h
- Plus baselines + setup + nvidia-smi sampling overhead
- **Timeout request: 18000s (5h)** — generous margin; anchor lacks `_n<N>` suffix so PROT-019 floor doesn't apply; PROT-021 requires _seed_checkpoint import (satisfied)

## Disciplines

- ASCII-only (no unicode in code/comments/output)
- Per-(seed, K, regime, arm) checkpoint (PROT-021)
- substrate-only-decode gate (n_llm == 0 asserted before metrics write)
- LLM-call counter monkey-patch at module import (catches accidental encoder calls)
- Real-data N/A (synthetic substrate-bipolar codebook); allow_synthetic=True logged in metrics
- Path-scoped commit (cell + prereg only); push to origin/main BEFORE remote dispatch
- REMOTE VERIFY post-dispatch: queue.json contains entry + script md5 matches local

## Cross-cell rail check (BIAS-N enforcement)

K=4096 MULTI_64x random recall must reproduce v1 K-extension cell's 0.9927 within +/- 0.02. If outside band, flag `RAIL_DRIFT` in verdict_msg and tier down to MIDDLE_BAND (mechanism not bit-identically reproducing; possible config drift).

## Honest scope statement

This cell maps the phase diagram of multi-bank working-memory K-capacity at N_DIM=8192 via batched GPU implicit-Hebbian per-bank superposition + bank-routing. It does NOT test:
- Real-token / encoder-derived items (synthetic bipolar substrate basis only)
- Continual writes (single-write phase; eval immediately after)
- Cross-bank interference under controlled overlap beyond FEATURE_OVERLAP_FRAC=0.20
- Compute-cost relative to LLM attention (out of scope; capacity question only)

A HARD_PASS extends substrate-native working-memory operating envelope to K=16384 at N=8192 with substrate-only readout and zero LLM forward calls. A HARD_FAIL or MIDDLE_BAND identifies the K-cliff location in the phase diagram.
