# Pre-registration: substrate_anisotropy_rescue_M100k_adversarial_similarity_keys_v2_batched

**Date:** 2026-06-25
**Anchor:** substrate_anisotropy_rescue_M100k_adversarial_similarity_keys_v2_batched
**Script:** experiments/exp_substrate_anisotropy_rescue_M100k_adversarial_similarity_keys_v2_batched.py
**Queue:** overnight_queue (GPU; Fix #24 torch.cuda actively used on big matmuls)
**Seeds:** [11, 13, 19] (cross-cell consistent; identical to v1)
**M_SWEEP (full):** [10000, 50000, 100000] (identical to v1)
**Encoder (full):** EleutherAI/pythia-2.8b (hidden states encoded ONCE per seed; substrate-only at inference)
**Eval M:** verdict computed at M_max = 100000
**Q_BATCH (new):** 200 (per-chunk sim output = 200 * 100000 * 4 = 80 MB; well under 8 GB)

## Promotion context (OOM-FIX of v1 with same scientific question)

v1 (`exp_substrate_anisotropy_rescue_M100k_adversarial_similarity_keys_v1`) CRASHED with CUDA OOM
during remote GPU dispatch 2026-06-25. Stderr trace:

```
torch.cuda.OutOfMemoryError: ... allocator wants 288 MiB
6.47 GiB allocated, 230 MiB reserved, 0 free
File ".../experiments/exp_substrate_anisotropy_rescue_M100k_adversarial_similarity_keys_v1.py", line 297
    sim_c2 = Qtc @ Ktc.t()
```

**Per-arm partial evidence from before crash (M=10k slice, seed 11):**
- raw = 0.021
- B_fly_lsh = 0.189
- B_charikar = 0.193
- AB_CTRL = 0.240

**Preliminary anti-LSH signal:** at M=10k adversarial keys, AB_CONTROL (generic dense Gaussian random
hash) actually scores HIGHER than both LSH arms. If this holds at full M=100k, v2's
"55x LSH rescue" attribution from non-adversarial M=10k synthetic keys was an artifact — random
projection at d'=3840 explains the apparent rescue, not LSH-specific structure. That outcome
would be HARD_FAIL_CONTROL_ALSO_PASSES per the prereg bands.

v2_batched will complete the M sweep at M=50k and M=100k to give us the chain-grade discriminator.

## Root cause of v1 OOM

The MAX_Q x M cosine-sim matmuls accumulate GPU residency at M=100k:

| matmul              | shape (Q,K)          | output bytes (fp32)   | K-side resident bytes |
| ------------------- | -------------------- | --------------------- | --------------------- |
| sim_fly = Qt @ Kt.t | (1500, 3840) x (M, 3840) | 1500*M*4 = 600 MB  | M*3840*4 = 1.46 GB    |
| sim_c = Qc @ Kc.t   | (1500, 3840) x (M, 3840) | 600 MB             | 1.46 GB               |
| sim_ab = ...        | (1500, 3840) x (M, 3840) | 600 MB             | 1.46 GB               |
| sim_c2 = Qtc @ Ktc.t (CRASH) | (1500, 3840) x (M, 3840) | 600 MB    | 1.46 GB               |
| attn_D x4 betas     | (1500, 768) x (M, 768)   | 600 MB x 4         | M*768*4 = 300 MB      |

Plus encoder (pythia-2.8b bf16) + accumulated A/A'/Kexp/cue_exp + cb_dp + various overhead.
Allocator hits the wall around sim_c2 (4th big arm-K resident concurrently).

## OOM-FIX (this cell)

**v2_batched** changes are MEMORY-LAYOUT ONLY; numeric results identical to v1 by construction:

1. **`_batched_argmax_sim(Q, K, q_batch=200)`** replaces the 4 monolithic cosine-sim matmuls
   (sim_fly, sim_c, sim_ab, sim_c2). Chunks Q-rows so per-chunk output is q_batch*M*4 = 80 MB.
   PyTorch argmax is row-local first-occurrence-on-ties -> identical results vs monolithic.

2. **`_batched_attn_recall(cue, Ks, codebook_d, ...)`** replaces the per-beta `cue @ Ks.t()`
   inside `_attention_arm_d_t`. Chunks cue-rows; softmax+readout per-chunk; identical recall
   (modulo FP softmax ordering, <1e-3 tolerance asserted in self-test).

3. **Aggressive per-arm K-side `del` + `torch.cuda.empty_cache()`** between arms. Only ONE arm's
   K-side tensor (1.46 GB) resident at a time, never all four concurrently.

4. **Kexp/cue_exp freed BEFORE Ktc allocation** in ARM C (the crash-point arm). CPU copy taken
   first; then GPU tensors released; then Ktc built. Estimated peak GPU footprint at M=100k:
   ~2.5 GB (encoder + cb_dp + Kp + Ks + Ktc + ~80 MB sim chunk) -- fits comfortably in 8 GB.

## Correctness assertion (load-bearing)

Self-test `_selftest()` extends v1's checks with:

- **batched_argmax_sim numeric equivalence:** monolithic `argmax(Q @ K.t())` vs
  `_batched_argmax_sim(Q, K, q_batch=qb)` for `qb in {1, 17, 64, 200, 300}` on random
  300x800x64 tensors. `torch.equal(mono_idx, bat_idx)` MUST hold for every qb. PASSES locally.

- **batched_attn_recall numeric equivalence:** monolithic softmax-attn vs
  `_batched_attn_recall(q_batch=37)` -> recall diff <= 1e-3. PASSES locally (mono=0.0033 bat=0.0033).

Self-test PASSES locally on .venv with both new assertions firing.

## Pre-registered bands (IDENTICAL TO v1 — locked at module init via assert)

### HARD_PASS_CHAIN_GRADE_CONFIRMED_FLY_LSH
- ARM_B_fly_lsh median >= **0.85** at M=100k
- ARM_RAW <= **0.30**
- (ARM_B_fly_lsh - ARM_B_charikar) >= **0.05**
- (ARM_B_fly_lsh - ARM_AB_control) >= **0.10**
- cv across 3 seeds for ARM_B_fly_lsh <= **0.05**

### HARD_PASS_CHAIN_GRADE_CONFIRMED_CHARIKAR
- ARM_B_charikar median >= **0.85** at M=100k
- ARM_RAW <= **0.30**
- (ARM_B_charikar - ARM_B_fly_lsh) >= **0.05**
- (ARM_B_charikar - ARM_AB_control) >= **0.10**
- cv across 3 seeds for ARM_B_charikar <= **0.05**

### HARD_PASS_BOTH_LSH_RESCUE
- ARM_B_fly_lsh AND ARM_B_charikar BOTH >= **0.85** at M=100k
- Both beat AB_control by >= **0.10**
- cv for both <= **0.05**
- RAW <= **0.30**

### MIDDLE_BAND_PARTIAL_RESCUE
- ARM_B_fly_lsh and/or ARM_B_charikar in **[0.50, 0.85)** at M=100k
- ARM_AB_control beats ARM_RAW by >= **0.20**

### HARD_FAIL_RESCUE_DOESNT_HOLD
- BOTH ARM_B_fly_lsh AND ARM_B_charikar <= **0.30** at M=100k

### HARD_FAIL_CONTROL_ALSO_PASSES  *(this is the band v1's M=10k partial signaled)*
- ARM_AB_control >= **0.85** at M=100k adversarial
- "Any random projection at d'=3840 works"; LSH-specific story is wrong

### MIDDLE_BAND_MEASURED_MECHANISM_NO_DISCRIMINATOR (default)

## Q-discipline (BIAS-Q USER explicit, even at M=100k)

If any arm hits >= **0.995** at full M=100k adversarial:
- Verdict carries `[Q-DISCIPLINE: suspect saturation even at M=100k adversarial; need M=500k+ or harder construction]`
- Tier remains the band-determined value; flag is documentation, not auto-demotion

## Cross-cell discipline (this batch)

- ASCII only (verified — no unicode in script)
- Substrate-only at inference (encoder hoisted ONCE; no LLM forward at verdict time)
- Per-arm metrics in verdict_msg AND per-seed/per-M in `per_unit` (Fix #28 mandatory)
- Bands locked at module init via assert (META_PROSPECTIVE_BANDS_FRESH_SEEDS)
- Seeds [11, 13, 19] (cross-cell consistent; matches v1)
- META_M6: NAIVE baseline (raw) measured IN-CELL at M=100k adversarial regime, NOT copied from v2
- META_M7: smoke (M=[500, 2000], pythia-160m, 1 seed) is for PIPELINE SANITY ONLY
- Discriminator margins (peer + control) baked into HARD_PASS bands directly (Fix #28 default under-claim)
- Fix #24: torch.cuda actively used; all 4 big sim matmuls + attn recall now batched on cuda

## Capacity-feasibility analysis (v2_batched memory budget)

Per-arm GPU peak at M=100k with Q_BATCH=200:

| component                                    | bytes (fp32) |
| -------------------------------------------- | ------------ |
| Encoder (pythia-2.8b bf16)                   | ~5.6 GB at rest, but FREED before arms |
| Kp (input, M*d=100k*768)                     | 300 MB       |
| Ks (M*d=100k*768)                            | 300 MB       |
| cb_dp (C*dp=256*3840)                        | 4 MB         |
| One K-side arm tensor at a time (M*dp=100k*3840) | 1.46 GB  |
| One Q-side arm tensor at a time (MAX_Q*dp=1500*3840) | 22 MB |
| Per-chunk sim output (q_batch=200 x M)       | 80 MB        |
| **Peak during one arm**                      | **~2.2 GB**  |

Encoder model is loaded for forward only; FREED before arms via `torch.cuda.empty_cache()`.
8 GB GPU comfortably accommodates 2.2 GB peak per-arm with margin.

## Wall estimate

v1 ran cleanly through M=10k (~5 min) before crashing on M=50k or M=100k.
Per-seed wall estimate:
- Encoder forward (pythia-2.8b on 110k 16-token windows): ~5 min
- Arms at M=10k: ~5 min (8 arms x ~30s with batching overhead trivial)
- Arms at M=50k: ~15 min (linear scale on argmax dominated by 8 arms x ~2 min)
- Arms at M=100k: ~30 min (linear scale, 8 arms x ~4 min)

Per-seed total: ~55 min. 3 seeds: ~3 hours wall.

## Timeout estimate

Formula: timeout_s = ceil(1.5 * wall_estimate_s)
= ceil(1.5 * 3*3600)
= ceil(16200)
= **16200s (4.5h)**

This EXCEEDS the 14400s PROT-021 long-timeout threshold; explicitly set 16200 and rely on
per-seed `_seed_checkpoint` resume. Cell already imports `_seed_checkpoint`; verified.

If 16200s is rejected by queue gate, fall back to 14400s with explicit per-seed-resume reliance.
Honest budget: I'd rather dispatch at 16200 with checkpoints than under-budget and re-dispatch.

**Dispatched timeout: 16200s**

## PROT compliance

- **PROT-018** (`_n<N>` suffix): anchor has no `_n<N>` suffix; rule does not apply.
- **PROT-019** (large-N timeout floor): no `_n<N>` suffix; rule does not apply.
- **PROT-020** (GPU queue requires torch): script `import torch` verified; OK.
- **PROT-021** (long-timeout needs checkpoint): script imports `_seed_checkpoint`; OK. Timeout 16200 > 14400 -> checkpoint reliance EXPLICIT.

## Pre-flight smoke gate

- Smoke runs with `RUN_MODE=smoke`: ENCODER=pythia-160m, SEEDS=[11], M_SWEEP=[500, 2000]
- Wall ~90-120s; queue_add.py default smoke gate 180s fits. HDLAB_SMOKE_TIMEOUT_S=300 fallback if marginal.
- Self-test (numpy + GPU correctness check, no encoder) asserts:
  - anisotropic raw collapses (got 0.001 < 0.30) PASS
  - isotropic raw works (got 0.958 > 0.5) PASS
  - isotropic attention meter D >= 0.80 (got 1.000) PASS
  - AB_control works (got 1.000) PASS
  - adversarial-prose construction (overlap 14/16 >= 14) PASS
  - **NEW: batched_argmax_sim == monolithic argmax** for q_batch in {1, 17, 64, 200, 300} PASS
  - **NEW: batched_attn_recall == monolithic attn-recall** to <1e-3 (mono=0.0033 bat=0.0033) PASS

## Fix #24 GPU dispatch must actually use GPU

Script:
- imports torch (PROT-020 satisfied)
- emits `gpu_avail`, `gpu_name`, `gpu_max_mem_alloc_mb` to metrics
- ALL big matmuls now on cuda AND batched (the v1 crash showed they were ACTUALLY on GPU; this fixes the magnitude)
- Encoder forward (pythia-2.8b) on GPU via flagship helpers (ENC_DTYPE=float16 on cuda)

## Symmetric verify rail (USER NEGATIVITY-BIAS rule)

Verdict reports BOTH:
- HARD_PASS conditions (rescue mechanism confirmed) AND
- HARD_FAIL conditions (rescue doesn't hold OR control also passes)
- Per-seed, per-M, per-arm breakdown in `per_unit` for Skunkworks step-0 honest re-read
- AB_CONTROL is the symmetric-verify mechanism

## Strategic significance (decision-grade)

The v1 partial M=10k slice (AB_CTRL=0.240 > B_fly=0.189 > B_char=0.193) is preliminary
evidence that fly-LSH is NOT load-bearing -- but at v1's stated M=10k it's NOT a discriminator
(saturation regime, low values likely just reflect adversarial-key difficulty at the small M).
The M=100k completion is what gives us the chain-grade answer.

Outcome paths:
- HARD_FAIL_CONTROL_ALSO_PASSES: Skunkworks's demotion of v2's "55x rescue" validated;
  substrate-product anisotropy story = partition-routing bypass + learned KV projection (the
  OTHER two paths). LSH framing dropped.
- HARD_PASS_CHAIN_GRADE_CONFIRMED_FLY_LSH or _CHARIKAR: LSH IS load-bearing at substrate-product
  scale on adversarial keys; v2's mechanism attribution promoted to chain-grade.
- HARD_PASS_BOTH_LSH_RESCUE: joint LSH-rescue; substrate-product picks one by cost.
- MIDDLE_BAND_PARTIAL_RESCUE: partial honest signal; non-conclusive but informs prior.
- HARD_FAIL_RESCUE_DOESNT_HOLD: LSH dies entirely at scale; anisotropy bypass via partition routing only.

Either honest outcome is decision-grade for substrate-product positioning.

## Honest negatives possible

- All v1 honest-negative possibilities still apply
- BATCHED-CORRECTNESS ASSERTION could in theory fail at the GPU smoke pre-flight (would be a torch FP edge case; self-test on local CPU already passes; very low prior)
- 16200s timeout may still under-budget if encoder forward at pythia-2.8b on 110k windows is slower than estimated; per-seed checkpoint mitigates -- partial seeds resume on next dispatch

## Dispatch plan

1. Author cell + prereg (this file) -- DONE
2. Self-test PASSED locally on .venv -- DONE
3. Path-scoped commit BEFORE remote dispatch (cell + prereg only; NEVER `git add -A` / `.`) -- TODO
4. Dispatch via `bash tools/orchestrator/queue_add.sh overnight_queue substrate_anisotropy_rescue_M100k_adversarial_similarity_keys_v2_batched experiments/exp_substrate_anisotropy_rescue_M100k_adversarial_similarity_keys_v2_batched.py preregs/2026-06-25_substrate_anisotropy_rescue_M100k_adversarial_similarity_keys_v2_batched.md 16200`
5. queue_add.sh SCPs script + prereg to marsh@home; SSH triggers remote queue_add.py with HDLAB_QUEUE_ADD_ON_REMOTE=1; harness-DENIED push handled by separate hd_metrics_sync OR Orchestrator if dispatch needs push
6. Post-ship verification: queue_add.sh confirms entry present in remote `data/overnight_queue/queue.json`
7. File dispatch notification: `notes/exp_dev_to_research_anisotropy_M100k_v2_batched_DISPATCHED_2026-06-25.md`

## Routing rationale

- **GPU queue (overnight_queue) per Fix #24:** identical to v1 -- pythia-2.8b encoder forward + 8 arms with dp=3840 dense matmuls remains matmul-bound.
- **PUSH constraint:** harness-DENIED to exp_dev; cell ships only after `hd_metrics_sync` pushes origin/main OR Orchestrator dispatches. The commit step (#3) is local-only; remote `git pull` happens on the home runner's next sync OR is handled by the sync task.

## Test plan post-landing

- Skunkworks step-0 honest re-read of per_unit per_M arm metrics (NOT verdict_msg framing) per Fix #28
- Verify cv_arm_B_fly_lsh and cv_arm_B_charikar across 3 seeds at M=100k
- Verify ARM_AB_control did NOT saturate (or did, depending on outcome)
- Cross-cell consistency: compare M=10k slice of v2_batched to v1's M=10k partial (seed 11 partial: raw=0.021 B_fly=0.189 B_char=0.193 AB_CTRL=0.240) -- sanity check that batching is numerically equivalent at the regime where v1 produced partial output
- If HARD_FAIL_CONTROL_ALSO_PASSES: atomize anti-LSH finding; close anisotropy-as-LSH story; route partition-routing + learned-KV-projection to remaining anisotropy lanes
- If HARD_PASS_CHAIN_GRADE_CONFIRMED: queue composition cell `substrate_anisotropy_rescue_fly_LSH_PLUS_hierarchical_routing_M_10M_v1`
