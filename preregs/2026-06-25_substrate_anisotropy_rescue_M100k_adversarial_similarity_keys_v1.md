# Pre-registration: substrate_anisotropy_rescue_M100k_adversarial_similarity_keys_v1

**Date:** 2026-06-25
**Anchor:** substrate_anisotropy_rescue_M100k_adversarial_similarity_keys_v1
**Script:** experiments/exp_substrate_anisotropy_rescue_M100k_adversarial_similarity_keys_v1.py
**Queue:** overnight_queue (GPU; Fix #24 torch.cuda actively used on big matmuls)
**Seeds:** [11, 13, 19] (cross-cell consistent)
**M_SWEEP (full):** [10000, 50000, 100000]
**Encoder (full):** EleutherAI/pythia-2.8b (hidden states encoded ONCE per seed; substrate-only at inference)
**Eval M:** verdict computed at M_max = 100000

## Promotion context (the chain-grade DISCRIMINATOR)

v2 (`exp_substrate_anisotropy_rescue_4arm_sweep_v2_calibrated_meter_full`) landed today with:
- ARM_B_fly_lsh = 0.997 at M=10k, cv = 0.001 across 3 seeds
- ARM_B_charikar = 1.000 at M=10k, cv = 0.000
- ARM_C_compose = 0.996, ARM_D_meter = 1.000
- raw collapsed to 0.018 (anisotropy IS real)
- 55x rescue magnitude (0.018 -> 0.997) MEASURED

Skunkworks ruling: by-construction-saturation tiering -> Director's "chain-grade-candidate" promoted to
MEASURED_MECHANISM only. 4/4 working arms at >=0.995 hits cell's OWN Q_SUSPECT_SATURATION band ->
cannot DISCRIMINATE which mechanism is load-bearing at M=10k. Same pattern that Skunkworks correctly
overrode Director on for g1 generation (USER 2026-06-22 endorsed the discipline).

v3 is the DISCRIMINATOR follow-up that Skunkworks explicitly recommended (see
`notes/skunkworks_tier_ruling_5_artifact_late_wave_2026-06-25.md` -> "For Director routing #1: dispatch
`exp_substrate_anisotropy_rescue_M100k_adversarial_similarity_keys_v1` ...").

## v3 key changes (load-bearing)

1. **M scaled to {10k, 50k, 100k}** -- at M=100k the capacity bound becomes load-bearing per v2's
   lit-scan (effective dimensionality drops as 1/M for an anisotropic cone past the capacity ceiling).

2. **Adversarial-similarity keys via consecutive-token stride-1 windows.** v2 used synthetic
   adj-noun-residue keys with no by-construction similarity. v3 generates each key as a 16-token sliding
   window of natural prose; adjacent keys share 15/16 tokens => HIGH cosine sim by construction. Cues are
   the same windows shifted by 1 token. Arms that just hash uniformly will COLLIDE on adjacent windows;
   arms that USE / RESCUE the anisotropy correctly will SEPARATE them.

3. **NEW ARM_AB_CONTROL:** generic dense Gaussian random hash (no sparsity, no signs). Output dim
   matches LSH arms (dp = 5*d = 3840). If THIS arm also saturates at M=100k adversarial, the LSH
   attribution is artifact -- "any random projection works", not LSH-specific. Failsafe negative
   control for the chain-grade-confirmed promotion.

4. **Bands rewritten for discrimination, not just rescue magnitude.** Chain-grade requires winning
   arm to beat (a) the OTHER LSH peer by >= 0.05 AND (b) AB_CONTROL by >= 0.10 -- mere absolute
   threshold is no longer sufficient (we know the M=10k absolute saturated).

5. **Q-discipline strengthened.** If any arm hits >= 0.995 EVEN AT M=100k ADVERSARIAL, BIAS-Q flag
   fires; corpus is STILL too easy and we need M=500k+ or harder construction (semantic paraphrases,
   contrastive hard negatives) before claiming chain-grade.

6. **Meter floor RELAXED (BAND_METER_FLOOR = 0.50 vs v2's 0.80).** At M=100k attention upper-bound
   is intrinsically harder than at M=10k (capacity-feasible); the meter still informs interpretability
   but a meter D in [0.50, 0.80] should NOT block the verdict at this scale.

## Pre-registered bands (LOCKED at module init via assert META_PROSPECTIVE_BANDS_FRESH_SEEDS)

### HARD_PASS_CHAIN_GRADE_CONFIRMED_FLY_LSH (fly-LSH is THE mechanism)
- ARM_B_fly_lsh median across seeds >= **0.85** at M=100k
- ARM_RAW <= **0.30** (collapse confirms anisotropy)
- (ARM_B_fly_lsh - ARM_B_charikar) >= **0.05** (fly beats Charikar peer)
- (ARM_B_fly_lsh - ARM_AB_control) >= **0.10** (fly beats generic dense hash control)
- cv across 3 seeds for ARM_B_fly_lsh <= **0.05**

### HARD_PASS_CHAIN_GRADE_CONFIRMED_CHARIKAR (Charikar is THE mechanism)
- ARM_B_charikar median >= **0.85** at M=100k
- ARM_RAW <= **0.30**
- (ARM_B_charikar - ARM_B_fly_lsh) >= **0.05**
- (ARM_B_charikar - ARM_AB_control) >= **0.10**
- cv across 3 seeds for ARM_B_charikar <= **0.05**

### HARD_PASS_BOTH_LSH_RESCUE (joint mechanism; both fly and Charikar work; cannot single-attribute)
- ARM_B_fly_lsh AND ARM_B_charikar BOTH >= **0.85** at M=100k
- Both beat AB_control by >= **0.10**
- cv for both <= **0.05**
- RAW <= **0.30**
- Verdict atomizes as joint LSH-rescue chain-grade; substrate-product picks one based on cost / runtime

### MIDDLE_BAND_PARTIAL_RESCUE
- ARM_B_fly_lsh and/or ARM_B_charikar in **[0.50, 0.85)** at M=100k
- ARM_AB_control beats ARM_RAW by >= **0.20** (any random expansion partially helps)
- Mechanism partially real but not chain-grade-discriminator-pass

### HARD_FAIL_RESCUE_DOESNT_HOLD
- BOTH ARM_B_fly_lsh AND ARM_B_charikar <= **0.30** at M=100k
- v2 M=10k 0.997 was M=10k-easy-regime artifact; LSH does NOT rescue at substrate-product scale

### HARD_FAIL_CONTROL_ALSO_PASSES (kills LSH attribution)
- ARM_AB_control >= **0.85** at M=100k adversarial
- "Any random projection at d'=3840 works"; LSH-specific story is wrong

### MIDDLE_BAND_MEASURED_MECHANISM_NO_DISCRIMINATOR (default)
- Arms measured cleanly but no chain-grade-confirmed attribution and no clean MIDDLE/FAIL pattern

## Q-discipline (BIAS-Q USER explicit, even at M=100k)

If any arm hits >= **0.995** at full M=100k adversarial:
- Verdict carries `[Q-DISCIPLINE: suspect saturation even at M=100k adversarial; need M=500k+ or harder construction]`
- Tier remains the band-determined value; flag is documentation, not auto-demotion

## Cross-cell discipline (this batch)

- ASCII only (verified)
- Substrate-only at inference (encoder hoisted ONCE; no LLM forward at verdict time)
- Per-arm metrics in verdict_msg (Fix #28) -- per-seed, per-M reported
- Bands locked at module init via assert (META_PROSPECTIVE_BANDS_FRESH_SEEDS)
- Seeds [11, 13, 19] (cross-cell consistent)
- META_M6: NAIVE baseline (raw) measured IN-CELL at M=100k adversarial regime, NOT copied from v2
- META_M7: smoke (M=[500, 2000], pythia-160m, 1 seed) is for PIPELINE SANITY ONLY -- verdict reasoning
  happens at full M=100k adversarial. Smoke regime saturating is EXPECTED and does NOT inform verdict.
- Discriminator margins (peer + control) baked into HARD_PASS bands directly (Fix #28 default under-claim)

## Capacity-feasibility analysis

Per (seed, M) GPU wall on RTX 4060 Ti (v2 evidence: M=10k arms ~ 60s; matmul O(M^2 d) at MAX_Q=1500 cap):

| M | matmul shape per arm | est wall per arm |
|---|---|---|
| 10000 | 1500 x 10000 x 768 | ~5s |
| 50000 | 1500 x 50000 x 768 | ~25s |
| 100000 | 1500 x 100000 x 768 | ~50s |

8 arms per (seed, M); 3 M-values; 3 seeds. Per seed: 8*(5+25+50) = 640s arms + ~30s encoder forward
(pythia-2.8b on 100000+10000 facts) = ~11 min/seed. 3 seeds = ~33 min total.

Add encoder hoist overhead (~3-5 min per seed for 110k facts at batch=32) -> ~45-60 min total wall.

Memory: peak at M=100k with codebook d'=3840 = 100k * 3840 float32 = ~1.5GB activations + ~7GB
encoder weights (pythia-2.8b bf16) = ~10GB total, fits on RTX 4060 Ti (16GB).

## Timeout estimate

Formula: timeout_s = ceil(1.5 * smoke_wall_s * (FULL_N/smoke_N)^scaling_exp * (FULL_seeds/smoke_seeds))

v2 (M_max=10k, 3 seeds, ~7.7 min total) -> ~150s/seed.
v3 (M_max=100k, 3 seeds): M scales 10x (linear in M for argmax decode); arms saturate cost at M=100k
because MAX_Q cap is 1500. Effective compute per seed ~ 3-4x v2 = ~600-800s/seed.

Formula: timeout_s = ceil(1.5 * 770 (v2 total) * (100000/10000)^0.8 * (3/3)) = ceil(1.5 * 770 * 6.31) = 7293s = ~2.0h.

Conservative budget: **timeout_s = 9000 (2.5h)** -- accounts for encoder warm-up at pythia-2.8b, GPU
memory mgmt, per-seed checkpoint resume, 110k-facts encode forward. Below 14400s (PROT-021 long-timeout
threshold); checkpoint wired anyway (`_seed_checkpoint`).

## PROT compliance

- **PROT-018** (`_n<N>` suffix): anchor has no `_n<N>` suffix; rule does not apply.
- **PROT-019** (large-N timeout floor): no `_n<N>` suffix; rule does not apply.
- **PROT-020** (GPU queue requires torch): script `import torch` verified; OK.
- **PROT-021** (long-timeout needs checkpoint): script imports `_seed_checkpoint`; OK. Timeout 9000s < 14400s anyway.

## Pre-flight smoke gate (queue_add.py)

- Smoke runs with `RUN_MODE=smoke`: ENCODER=pythia-160m, SEEDS=[11], M_SWEEP=[500, 2000]
- N_TOKENS_BUDGET=2200 -- builds ~2200-word prose from canned pool (no external fetch)
- Smoke takes ~90-120s (1 encoder forward at 160m + 2 M-points * 8 arms, all small)
- queue_add.py smoke gate cap = 180s default; will fit. If marginal, HDLAB_SMOKE_TIMEOUT_S=300 at dispatch.
- Self-test (numpy, no GPU) asserts: anisotropic raw collapses + isotropic raw works + attention meter
  beta-sweep recovers >= 0.80 + AB_control works on isotropic + adversarial-prose window construction
  produces expected 15/16 token overlap. Self-test PASSED LOCAL (verified before dispatch).

## Fix #24 GPU dispatch must actually use GPU

Script:
- imports torch (PROT-020 satisfied)
- asserts gpu_avail at smoke/full + logs gpu_name
- ALL big matmuls (cue@Ks.T, kWTA topk, attention softmax, sign sketches, AB_control dense projection)
  on torch.cuda when available
- Encoder forward (pythia-2.8b) on GPU via flagship helpers (ENC_DTYPE=bfloat16 on cuda)
- emits `gpu_avail`, `gpu_name`, `gpu_max_mem_alloc_mb` to metrics

## Symmetric verify rail (USER NEGATIVITY-BIAS rule)

Verdict reports BOTH:
- HARD_PASS conditions (rescue mechanism confirmed) AND
- HARD_FAIL conditions (rescue doesn't hold OR control also passes)
- Per-seed, per-M, per-arm breakdown in `per_unit` for Skunkworks step-0 honest re-read
- AB_CONTROL is the symmetric-verify mechanism: makes the chain-grade-confirmed-FLY/CHARIKAR claim
  falsifiable by an independent measurement.

## Strategic significance (decision-grade)

If HARD_PASS_CHAIN_GRADE_CONFIRMED (fly or Charikar):
- Anisotropy SOLVED at substrate-product scale (M=100k+) on adversarial keys
- Skunkworks MM -> chain-grade promotion path complete with mechanism attribution
- Specific rescue mechanism identified for substrate-as-LM Stage 4 revival
- Composes with hierarchical 2-level routing (already chain-grade @ M=10M) for substrate-product KG retrieval

If HARD_PASS_BOTH_LSH_RESCUE:
- LSH-rescue is real but mechanism-attribution undetermined; atomize joint -- both fly and Charikar
  are substrate-product candidates; pick by cost/runtime
- Composes with hierarchical routing similarly

If HARD_FAIL_RESCUE_DOESNT_HOLD:
- v2 M=10k 0.997 WAS too-easy-regime artifact; substrate's anisotropy story changes
- Anisotropy bypass via partition routing remains the substrate-product path
- Honest negative; closes the question

If HARD_FAIL_CONTROL_ALSO_PASSES:
- The apparent rescue isn't LSH-specific -- any random expansion at d' works
- LSH narrative collapses; "random expansion in higher-dim works" is the honest story
- Mechanism-of-action research needed for chain-grade attribution

Either outcome is decision-grade for substrate-product positioning.

## Honest negatives possible

- LSH arms may collapse below 0.30 at M=100k adversarial (capacity bound binding)
- AB_control may also saturate (random expansion suffices; LSH attribution wrong)
- fly-LSH and Charikar may BOTH saturate at 0.85+ but with cv > 0.05 (variance kills chain-grade)
- Encoder forward on 110k facts may push memory limits (cell may need to chunk encoder forward)
- Per-seed adversarial-prose realizations may not hit identical regime (TRAIN_M / held-out split shuffles)

Any of these tier the result honestly per the prereg bands. No padding.

## Dispatch plan

1. Author cell + prereg (this file) -- DONE
2. Self-test PASSED locally -- DONE (numpy meter calibration + AB_control sanity + adversarial-prose construction)
3. Path-scoped commit BEFORE remote dispatch (cell + prereg only; NEVER `git add -A` / `.`)
4. Dispatch via `bash tools/orchestrator/queue_add.sh overnight_queue substrate_anisotropy_rescue_M100k_adversarial_similarity_keys_v1 experiments/exp_substrate_anisotropy_rescue_M100k_adversarial_similarity_keys_v1.py preregs/2026-06-25_substrate_anisotropy_rescue_M100k_adversarial_similarity_keys_v1.md 9000`
5. queue_add.sh SCPs script + prereg to marsh@home; SSH triggers remote queue_add.py with HDLAB_QUEUE_ADD_ON_REMOTE=1
6. Post-ship verification: queue_add.sh confirms entry present in remote `data/overnight_queue/queue.json`
7. File dispatch notification: `notes/exp_dev_to_research_anisotropy_M100k_adversarial_v1_DISPATCHED_2026-06-25.md`

## Routing rationale

- **GPU queue (overnight_queue) per Fix #24:** pythia-2.8b encoder forward at M=110k, 8 arms with dp=3840
  dense matmuls -- matmul-bound workload, fits GPU sweet spot. Routing to CPU would balloon to 10x+ wall
  and miss the discriminator window.
- **Fix #14 spawn budget acknowledged:** this is the 4th in flight (over the ~3 ceiling) but USER
  explicitly authorized this dispatch per Skunkworks recommendation; GPU currently idle while CPU runs
  laptop matmul workloads; non-conflicting with other 3 in flight.
- **Pause flag verified NOT set** at dispatch authorship time. Re-checked before queue_add.sh.

## Test plan post-landing

- Skunkworks step-0 honest re-read of per_unit per_M arm metrics (NOT verdict_msg framing)
- Verify cv_arm_B_fly_lsh and cv_arm_B_charikar across 3 seeds at M=100k
- Verify ARM_AB_control did NOT saturate (or did, depending on outcome)
- Cross-cell consistency: compare M=10k slice of v3 to v2 (sanity check encoder regime parity)
- If chain-grade-confirmed: queue composition cell `substrate_anisotropy_rescue_fly_LSH_PLUS_hierarchical_routing_M_10M_v1`
