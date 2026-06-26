# exp_dev -> orchestrator: GPU dispatch ask -- phase-diagram WM K-extension to 16384

**Filed:** 2026-06-25 (true UTC ~end-of-day)
**From:** exp_dev (USER-directed cell)
**To:** orchestrator
**Type:** dispatch_ask (overnight_queue / GPU)

## Ask

Dispatch `phase_diagram_working_memory_multibank_K_extension_to_16384_v1` to **overnight_queue (GPU)** per USER directive 2026-06-26 + Fix #24 GPU mandate.

Push to origin/main is harness-DENIED to exp_dev; routing to Orchestrator who owns hd_metrics_sync push authority.

## Dispatch command (verbatim)

```bash
bash tools/orchestrator/queue_add.sh \
  overnight_queue \
  phase_diagram_working_memory_multibank_K_extension_to_16384_v1 \
  experiments/exp_phase_diagram_working_memory_multibank_K_extension_to_16384_v1.py \
  preregs/2026-06-25_phase_diagram_working_memory_multibank_K_extension_to_16384_v1.md \
  18000
```

- queue: `overnight_queue` (GPU; PROT-020 verified torch import; Fix #24 mandate)
- name: `phase_diagram_working_memory_multibank_K_extension_to_16384_v1`
- script: `experiments/exp_phase_diagram_working_memory_multibank_K_extension_to_16384_v1.py`
- prereg: `preregs/2026-06-25_phase_diagram_working_memory_multibank_K_extension_to_16384_v1.md`
- timeout: 18000s (5h) — generous margin; anchor lacks `_n<N>` suffix so PROT-019 floor doesn't apply; PROT-021 satisfied (cell imports `_seed_checkpoint`)

No `--skip-smoke`: smoke can run on remote GPU during gate. Remote smoke will sanity-check gpu_util_p50 >= 50% (Fix #24).

Optional: pass `--skip-smoke` to skip remote smoke gate if local smoke (filed below) is sufficient. Local smoke ran on CPU (no CUDA locally); remote smoke will exercise the actual GPU code path.

## Cell + prereg location

- Cell: `experiments/exp_phase_diagram_working_memory_multibank_K_extension_to_16384_v1.py` (md5 `abd9bf92db991a9f3ace799c5b55dd1b`)
- Prereg: `preregs/2026-06-25_phase_diagram_working_memory_multibank_K_extension_to_16384_v1.md`
- Commit: `78f4af4e` (committed; NEEDS PUSH to origin/main before remote dispatch)

## Strategic intent (USER directive)

Multi-bank K=4096 chain-graded TODAY (`exp_substrate_working_memory_multi_bank_K_extension_adversarial_v1` 2026-06-25, MULTI_64x recall=0.9927 cv=0.0006 random; 0.9810 cv=0.0015 adversarial; chain-grade-eligible). Phase-diagram map question: where does multi-bank K cliff above 4096?

USER 2026-06-25: "we understand where everything operates best within the phase diagram." Brain working-memory effective capacity is ~7+/-2 conscious items, but routing/binding capacity at substrate level is much higher. Need to MAP CLIFF for production deployment confidence: K=8192? K=16384? Or no cliff in the substrate-product operating envelope?

## Design

Five K-points + rail:
- **K=4096 MULTI_64x** (RAIL; must reproduce 0.9927 within +/-0.02)
- **K=8192 MULTI_64x** (NEW; 64 banks, k_per_bank=128 — discriminator above chain-grade envelope)
- **K=8192 MULTI_128x** (NEW; 128 banks, k_per_bank=64 — preserves chain-grade envelope)
- **K=16384 MULTI_128x** (NEW; 128 banks, k_per_bank=128 — discriminator)
- **K=16384 MULTI_256x** (NEW; 256 banks, k_per_bank=64 — preserves chain-grade envelope)

Each at RANDOM + ADVERSARIAL regime (FEATURE_OVERLAP_FRAC=0.20).

Sentinel arms at K=4096:
- **ARM_KNN_BASELINE** M=400 (Fix #28 sentinel; HARD_FAIL if < 0.90)
- **ARM_NAIVE_SINGLE_BANK** (reproduces ~0.002 floor)

Total full-config units: 3 seeds * (1 + 2 + 2) K-arrangements * 2 regimes + 3 seeds * 2 sentinels = 36 + 6 = 42 units.

## Pre-reg bands (LOCKED at module init)

- **CHAIN_GRADE_K_EXTENDS_TO_16384 (HARD_PASS):** K=8192 AND K=16384 best arm recall >= 0.95 random AND adv within 0.05 AND cv <= 0.05 AND k_per_bank <= 64 (chain-grade envelope) AND route_acc >= 0.95 AND rail K=4096 within +/-0.02 AND KNN sentinel >= 0.90 AND n_llm == 0
- **PARTIAL_K_EXTENDS_TO_8192 (MIDDLE_BAND):** K=8192 chain-grade; K=16384 partial (recall in [0.50, 0.95) or adv > 0.05 below random or cv > 0.05)
- **MIDDLE_BAND_RAIL_DRIFT:** all extended chain-grade BUT rail K=4096 outside +/-0.02 (mechanism not bit-identically reproducing v1)
- **HARD_FAIL_K_4096_IS_CEILING:** K=8192 best random < 0.50
- **HARD_FAIL_ADVERSARIAL_BREAKS_AT_K_EXT:** at any K, adv recall drops >= 0.30 vs random best
- **HARD_FAIL_CV_INSTABILITY:** best arm cv > 0.10 at any K
- **HARD_FAIL_KNN_SENTINEL:** ARM_KNN_BASELINE < 0.90 (Fix #28 broken-metrics catch)
- **Q-DISCIPLINE:** any arm recall >= 0.995 with cv == 0 flags `_q_suspect_saturation` (cert-tier reduced, not HARD_FAIL)

## GPU mandate (Fix #24)

- `import torch` at module top (PROT-020 gate verified)
- `torch.cuda.is_available()` strict-required for full run; cell aborts `GPU_MANDATE_VIOLATED` on no-CUDA
- All heavy tensors on `cuda:0` in fp16; batched matmul throughout (no Python per-bank/per-slot loops in inner path)
- nvidia-smi GPU util sampled per arm
- metrics include: `gpu_avail`, `gpu_name`, `gpu_max_mem_alloc_mb`, `gpu_util_mean`, `gpu_util_p50`, `gpu_util_max`, `gpu_util_n_samples`
- GPU memory budget: peak ~1.1 GB during a bank-write batched matmul; well within 8 GB 4060Ti

## Pre-flight verifications (local)

- **PROT-020 torch import:** OK (line `import torch` at module top)
- **PROT-021 _seed_checkpoint import:** OK (`from experiments._seed_checkpoint import ...`)
- **PROT-018:** N/A (anchor has no `_n<N>` suffix)
- **PROT-019:** N/A (anchor has no `_n<N>` suffix)
- **ASCII-only:** OK (encode('ascii') succeeds)
- **Predispatch_check.py:** 0 matching landings / 0 matching atoms / RECOMMENDATION PROCEED
- **Self-test:** 6/6 PASS on CPU (T1 random codebook + bipolar; T2 adversarial overlap in=0.575 cross=0.483 expected ~0.60; T3 multi-bank 16x16_K256 recall=0.996 ra=1.000; T4 LLM counter=0; T5 KNN baseline=1.000; T6 bands locked)
- **Smoke (CPU local):** SMOKE_PASS in 3.0s; n_llm=0; 6 units; all REQUIRED_FIELDS present; valid metrics.json shape

## Smoke results (local, CPU fallback)

Smoke at N=2048, K_SWEEP=[1024, 4096], seeds=[11], N_ITEMS_PER_K=80:
- K=1024 MULTI_32x random recall=0.9932 / adv 0.9902 (clean)
- K=4096 MULTI_64x random recall=0.7986 / adv 0.7305 (smaller N => smaller recall; expected)
- ARM_KNN_BASELINE 1.000 (>=0.90 OK; Fix #28 sentinel passes)
- ARM_NAIVE_SINGLE_BANK 0.0027 (reproduces ~0.002 floor)
- n_llm=0; substrate-only gate OK

Note: rail check at K=4096 is parameterized for the FULL config (N=8192); smoke at N=2048 cannot reproduce v1's 0.9927. The rail check applies to the FULL remote run; local smoke verifies the harness end-to-end.

## Cross-cell rail check (BIAS-N)

Full run rail: K=4096 MULTI_64x random recall MUST reproduce v1 K-extension cell's 0.9927 within +/- 0.02. If outside, verdict tiers to MIDDLE_BAND_RAIL_DRIFT (mechanism not bit-identically reproducing; possible config drift). Anchor for v1: `exp_substrate_working_memory_multi_bank_K_extension_adversarial_v1` metrics.json `chain_grade_set[4096]='MULTI_64x'` recall_mean=0.9927.

## REMOTE VERIFY ask

Post-dispatch, please confirm:
1. `data/overnight_queue/queue.json` on marsh@home contains `phase_diagram_working_memory_multibank_K_extension_to_16384_v1` entry (status=pending)
2. Script md5 on remote matches local: `abd9bf92db991a9f3ace799c5b55dd1b`
3. (Optional) Remote smoke run on GPU completes with gpu_util_p50 >= 50% (Fix #24 actual-GPU-use verification)

## Timing estimate

- v1 K-extension at K=4096 on CPU at N=4096: ~467s/unit
- Extrapolation: K=16384 N=8192 on GPU with batched fp16 matmul + ~15x GPU speedup vs CPU: ~250s/unit
- 42 units * 250s = ~10500s ~= 2.9h
- Conservative timeout: 18000s (5h)

## Status

- Cell + prereg: COMMITTED (78f4af4e)
- Local self-test: PASS
- Local smoke: PASS (CPU fallback; SMOKE_PASS verdict)
- Predispatch check: PROCEED
- Pause flag: absent
- **AWAITING ORCHESTRATOR:** push to origin/main + dispatch via queue_add.sh + REMOTE VERIFY

## Pointers

- Cell: `experiments/exp_phase_diagram_working_memory_multibank_K_extension_to_16384_v1.py`
- Prereg: `preregs/2026-06-25_phase_diagram_working_memory_multibank_K_extension_to_16384_v1.md`
- v1 reference (rail source): `data/exp_substrate_working_memory_multi_bank_K_extension_adversarial_v1/metrics.json`
