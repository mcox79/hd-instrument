# Pre-registration: substrate_anisotropy_rescue_4arm_sweep_v2_calibrated_meter_full

**Date:** 2026-06-25
**Anchor:** substrate_anisotropy_rescue_4arm_sweep_v2_calibrated_meter_full
**Script:** experiments/exp_substrate_anisotropy_rescue_4arm_sweep_v2_calibrated_meter_full.py
**Queue:** overnight_queue (GPU; Fix #24 torch.cuda actively used on big matmuls)
**Seeds:** [11, 13, 19] (cross-cell consistent with today's batch)
**M_SWEEP (full):** [1000, 3000, 10000]
**Encoder (full):** EleutherAI/pythia-2.8b (hidden states encoded ONCE per seed; substrate-only at inference)
**Eval M:** verdict computed at M_max = 10000

## Promotion context

The v1 smoke (1 seed, pythia-160m, M=[400, 1000]) returned MIDDLE_BAND with **Arm D (attention upper-bound) = 0.445 < 0.80**.
Per the v1 cell's own calibration flag, the meter is under-calibrated -> the arms are interpretable only RELATIVE to one another.

The substantive result hiding behind the meter bug:
- Arm B (fly-LSH) = 0.612 at M=1k
- Arm B' (Charikar hyperplane LSH; v1 had this as the NEGATIVE control) = **0.982** at M=1k
- Arm C (compose A -> B) = 0.573
- raw superposition = 0.019 (collapsed; the anisotropy IS real)

The Charikar arm — labelled as a control that "should underperform" — actually BEAT fly-LSH AND beat the upper-bound D
at v1 smoke. Either (a) Charikar genuinely chain-grades on this regime, OR (b) the meter is so broken that everything is
uninterpretable. v2 is the test that resolves which.

Today's deep-dive (`notes/research_deep_dive_partial_and_open_capabilities_intuitive_2026-06-25.md`) frames the substrate's
anisotropy-on-real-Pythia-keys problem as bypassed (partition routing + KV learned projection chain-grade), NOT solved.
A calibrated v2 with a chain-grade B-arm would change that story.

## v2 key changes (load-bearing)

1. **Calibrated meter via beta-sweep.** v1 used `beta = 1/sqrt(d)` (theory-default). At d=768, M=1000 with noise SIGMA=0.1
   that's a flat softmax — mass spreads across all M keys, argmax-decode collapses. v2 reframes Arm D as the MAX over a
   beta multiplier sweep `[1.0, 4.0, 16.0, 64.0] * (1/sqrt(d))`. Real attention picks its temperature; an "upper-bound"
   meter should reflect that. Self-test asserts the beta-sweep recovers >= 0.80 on an isotropic synthetic regime
   (M=400, d=128) BEFORE the cell can dispatch.

2. **Relative-band safety net.** Verdict ALSO reports `arm_B_fly_lsh / arm_D` and `arm_B_charikar / arm_D`. If Arm D is
   still under-calibrated at full mode, MIDDLE_BAND_RELATIVE_PROMISE catches a real mechanism even when the meter struggles.

3. **3 seeds [11, 13, 19] + cv ceilings** for chain-grade tiering. cv <= 0.05 for HARD_PASS_SOLVED; cv <= 0.07 for partial.

4. **Fix #24 GPU actively used.** All big matmuls (cue @ Ks.T, kWTA, attention softmax, sign sketches) on torch.cuda. GPU
   availability + max-mem-allocated emitted to metrics for post-hoc evidence.

5. **Q-discipline (BIAS-Q).** If any arm hits >= 0.995, verdict carries `[Q-DISCIPLINE: suspect saturation]` note.

6. **Arm renaming for honesty (Fix #28).** v1 labelled Charikar as "B' negative control of B". v2 renames to `B_fly_lsh` and
   `B_charikar` — they are PEER candidate mechanisms (both LSH variants), not control + control-of-control. Verdict reads
   per-arm metrics, not the v1 framing.

## Arms (preserved + renamed)

- **ARM 1 raw:** dense d-dim superposition store on real Pythia keys. The COLLAPSE baseline (v1 saw 0.019 at M=1k pythia-160m).
- **ARM A (cerebellar):** sparse-fan-in expand d' = 5d, K=5 random input dims, kWTA top-10% -> superposition.
- **ARM A' (control):** dense-Gaussian fan-in at same d'+kWTA. MUST HARD-FAIL -> credits sparse-fan-in.
- **ARM B_fly_lsh:** median-subtract -> sparse random proj (5% nonzero) -> WTA top-20 -> tag-overlap argmax.
- **ARM B_charikar:** dense Gaussian hyperplanes -> sign sketches -> Hamming-via-sign-product argmax. v1's 0.982 winner.
- **ARM C (compose):** sparse-fan-in expand -> fly-LSH on expanded code.
- **ARM D (meter):** attention 1-step softmax MAX over beta multiplier sweep {1, 4, 16, 64} * (1/sqrt(d)).

## Pre-registered bands (LOCKED at module init via assert META_PROSPECTIVE_BANDS_FRESH_SEEDS)

### HARD_PASS_ANISOTROPY_SOLVED_VIA_LSH_FANOUT (fly-LSH chain-grade)
- arm_B_fly_lsh median across seeds >= **0.80** at M=10k
- arm_D (meter) >= **0.80** at M=10k
- cv across 3 seeds for arm_B_fly_lsh <= **0.05**

### HARD_PASS_CHARIKAR_RESCUE (Charikar chain-grade; v1's 0.982 winner)
- arm_B_charikar median across seeds >= **0.80** at M=10k
- arm_D >= **0.80** at M=10k
- cv across 3 seeds for arm_B_charikar <= **0.05**

### HARD_PASS_PARTIAL_LSH (partial chain-grade for either LSH variant)
- arm_B_{fly_lsh|charikar} median >= **0.60** AND arm_D >= **0.80** AND cv <= **0.07**

### MIDDLE_BAND_RELATIVE_PROMISE (safety net for meter-still-broken)
- (arm_B_{fly_lsh|charikar} / arm_D) >= **0.80** even if arm_X absolute < 0.80
- meter regime needs revisiting; mechanism still mechanistically real

### HARD_FAIL_LSH_DOESNT_HOLD
- BOTH arm_B_fly_lsh <= **0.40** AND arm_B_charikar <= **0.40** at M=10k
- meter calibrated -> LSH mechanisms do NOT rescue anisotropy at pythia-2.8b regime
- (would invalidate v1 smoke 0.982 as artifact / pythia-160m vs pythia-2.8b regime shift)

### METER_UNDER_CALIBRATED (cell uninterpretable)
- arm_D < **0.80** AND no relative-promise win
- cell aborts honest; verdict notes meter state; redesign for v3 (encoder upgrade or smaller M)

## Q-discipline (BIAS-Q USER explicit)

If any arm hits **>= 0.995** at full (v1 smoke showed 0.982 for Charikar; v2 may hit ceiling):
- Verdict carries `[Q-DISCIPLINE: suspect saturation; corpus-may-be-easy; honest under-claim]`
- Tier as MEASURED_MECHANISM unless mechanism story explains the ceiling

## Cross-cell discipline (this batch)

- ASCII only (verified)
- Substrate-only at inference (encoder hoisted ONCE; no LLM forward at verdict time)
- Per-arm metrics in verdict_msg (Fix #28) — per-seed, per-M reported
- Bands locked at module init via assert (META_PROSPECTIVE_BANDS_FRESH_SEEDS)
- Seeds [11, 13, 19] (cross-cell consistent)
- Sigma0 cleanup integrity: per-arm raw recall AND tag-overlap distribution recorded per seed
- NaN detection at production-scale matmul: torch float32 + chunk softmax (max-subtract for stability)
- META_M6: NAIVE baseline = arm1_raw measured in-cell at the same regime (NOT copied)
- Smoke-vs-full discipline: smoke matches full on PROJ_DIM, C, EXPAND, K_FANIN, KWTA_FRAC, FLY_TOPK, FLY_NONZERO, SIGMA, BETA_MULT_SWEEP. Only ENCODER (pythia-160m smoke vs 2.8b full), SEEDS (1 vs 3), M_SWEEP ([400,1000] vs [1k,3k,10k]), TRAIN_M/STEPS differ.

## Capacity-feasibility analysis

Per (seed, M) GPU wall:
- M=1k: ~5s (encoder forward + 6 arms; arm matmuls O(M*d^2 / d') ~ 768^2 = 0.6M ops)
- M=3k: ~15s
- M=10k: ~60s (kWTA topk + sign sketches dominate at this M)
- Per seed: encoder forward ~5-15s (one-time) + ~80s arms total
- 3 seeds: ~5 min compute + ~30s encoder overhead per seed = ~10 min total

Memory: peak at M=10k with codebook d'=3840 = ~10k * 3840 float32 = 150MB; W matrix 256 * 3840 = 4MB; OK on any GPU.

## Timeout estimate

v1 smoke wall (1 seed, M=[400, 1000], pythia-160m): 85s.
v2 full vs v1 smoke scaling factor: M_max 10000 vs 1000 = 10x; encoder 2.8b vs 160m = ~5x forward time;
seeds 3 vs 1 = 3x; total scaling ~ 10 * 5 * 3 = 150x conservative; but encoder is one-shot per seed (not per M)
so effective is closer to ~20-40x.

Formula: timeout_s = ceil(1.5 * 85 * (10000/1000)^1.3 * (3/1)) = ceil(1.5 * 85 * 19.95 * 3) = 7626s = ~2.1h.

Conservative budget: **timeout_s = 5400 (90 min)** — accounts for encoder warm-up, GPU memory mgmt, per-seed checkpoint resume.
Below the 14400s (4h) PROT-021 long-timeout-needs-checkpoint floor; checkpoint is wired anyway (`_seed_checkpoint`).

## PROT compliance

- **PROT-018** (`_n<N>` suffix binding): anchor name has no `_n<N>` suffix; rule does not apply.
- **PROT-019** (large-N timeout floor): no `_n<N>` suffix; rule does not apply.
- **PROT-020** (GPU queue requires torch): script `import torch` verified; OK.
- **PROT-021** (long-timeout needs checkpoint): script imports `_seed_checkpoint`; OK. Timeout 5400s < 14400s threshold anyway.

## Pre-flight smoke gate (queue_add.py)

- Smoke runs with `RUN_MODE=smoke`: ENCODER=pythia-160m, SEEDS=[11], M_SWEEP=[400, 1000]
- Smoke takes ~85s (v1 evidence)
- queue_add.py smoke gate cap = 180s default; will fit. If marginal, set `HDLAB_SMOKE_TIMEOUT_S=300` at dispatch.
- Self-test (numpy, no GPU) asserts meter beta-sweep works on isotropic synthetic BEFORE smoke runs.

## Fix #24 GPU dispatch must actually use GPU

Script:
- imports torch (PROT-020 satisfied)
- asserts gpu_avail at smoke/full + logs gpu_name
- all big matmuls (cue@Ks.T, kWTA topk, attention softmax, sign sketches) on torch.cuda (when available)
- emits `gpu_avail`, `gpu_name`, `gpu_max_mem_alloc_mb` to metrics for post-hoc evidence
- numpy fallback ONLY for self-test (cheap synthetic check; GPU not needed)

## Symmetric verify rail (USER NEGATIVITY-BIAS rule)

Verdict reports both directions per arm:
- Absolute: arm_X median across seeds with cv
- Relative: arm_X / arm_D ratio (safety net when meter still struggles)
- Per-seed/per-M breakdown in `per_unit` (for Skunkworks step-0 honest re-read)
- Per-beta breakdown for Arm D (so meter-failure-mode visible)

## Strategic significance (decision-grade)

If a chain-grade pass:
- Substrate has a REAL solution to anisotropy on real-data keys (vs being bypassed via partition routing + KV learned projection)
- Stage 4 LM-equivalence deferral could be revisited (per USER strategic frame: brain-grounded mechanisms with substrate-native
  paths get high prior; this is one of them)
- Three distinct KG retrieval paths: dense-KV + partition-routing + LSH-fanout

If HARD_FAIL or persistent METER_UNDER_CALIBRATED:
- v1 smoke 0.982 was noise / regime artifact / single-seed luck
- Anisotropy remains bypassed; existing positioning stands
- Close cell with honest negative; v3 would need fundamentally different design (e.g. learned codebook + retrieval)

Either outcome is decision-grade.

## Honest negatives possible

- Charikar 0.982 may not survive pythia-2.8b (larger hidden dim -> sign sketches noisier per bit)
- fly-LSH median may drift across seeds (5% sparse projection has variance)
- Arm D beta-sweep may still cap below 0.80 at d=768, M=10k due to genuine attention upper-bound limits in this regime
- Per-seed cv may exceed 0.05 if seeds catch different anisotropic eigendirections

Any of these tier the result honestly per the prereg bands. No padding.

## Dispatch plan

1. Author cell + prereg (this file) -- DONE
2. Smoke-gate via queue_add.py: runs `--self-test` (numpy meter assertion) then `--smoke` (1 seed, M=[400,1000], pythia-160m)
3. queue_add.py validates metrics.json under data/exp_<anchor>_smoke/ has required fields
4. Path-scoped commit BEFORE remote dispatch (cell + prereg only)
5. Dispatch via `bash tools/orchestrator/queue_add.sh overnight_queue substrate_anisotropy_rescue_4arm_sweep_v2_calibrated_meter_full experiments/exp_substrate_anisotropy_rescue_4arm_sweep_v2_calibrated_meter_full.py preregs/2026-06-25_substrate_anisotropy_rescue_4arm_sweep_v2_calibrated_meter_full.md 5400`
6. queue_add.sh SCPs script + prereg to marsh@home; SSH triggers remote queue_add.py with HDLAB_QUEUE_ADD_ON_REMOTE=1
7. Post-ship verification: queue_add.sh confirms entry present in remote `data/overnight_queue/queue.json`
8. File dispatch notification note
