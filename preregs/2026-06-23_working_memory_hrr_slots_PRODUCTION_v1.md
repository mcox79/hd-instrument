# Pre-registration: working_memory_hrr_slots_PRODUCTION_v1

**Date:** 2026-06-23
**Anchor:** working_memory_hrr_slots_PRODUCTION_v1
**Queue:** local_cpu_queue
**N:** 4096, **CODEBOOK_SIZE:** 256, **Seeds:** [7, 17, 23],
**ARMS:** 3 (FLAT_SUPERPOSITION, HRR_SLOTS, HRR_SLOTS_PLUS_CLEANUP)
**K_VALUES:** [8, 16, 32, 64, 128, 256] (extends well beyond Miller's 7+/-2)
**SIGMAS:** [0.0, 0.5, 1.0, 1.5, 2.0] (extends INTO the Shannon-floor)
**N_ITEMS_PER_K:** 200

## Scientific question
Where does the substrate's HRR-slot working memory ACTUALLY break? The smoke
(working_memory_hrr_slots_smoke_v1) saturated at recall 1.000 across K=2..16,
sigma=0..1.0 -- the discriminator was too easy and the mechanism witness was
confirmed only at sub-Miller scale. This production cell pushes the regime past
human PFC capacity (K=32..256) and into the noise floor we already characterized
in prior arc (sigma=1.5..2.0) to find the capacity envelope of the
substrate-native working-memory primitive.

## Pre-registered bands

**HARD-PASS (chain-grade-eligible substrate working-memory primitive at
super-human scale):**
- ARM_HRR_SLOTS_PLUS_CLEANUP cross-seed mean recall at K=32, sigma=1.0 >= 0.80
- (substrate holds 32 items -- ~5x Miller's 7 -- in a single HD vector at
  meaningful noise with 80%+ recall; this is the discriminator)

**MIDDLE:** otherwise. Characterizes the capacity envelope across the K x sigma
grid (where the cleanup arm passes Miller, where it crosses sub-Miller chance,
where the no-cleanup slots arm degrades into the Shannon-floor).

**HARD-FAIL (working-memory primitive structurally broken at modest load+noise):**
- ARM_HRR_SLOTS (no cleanup) cross-seed mean recall at K=16, sigma=0.5 < 0.50
  (substrate cannot even hold 16 items at modest noise without the cleanup
  stage; cleanup is load-bearing -- routes to alternative scratch-space mech)

**Sanity self-test (in --self-test path; T7):** K=2 sigma=0.0 recall >= 0.99
across ARM_HRR_SLOTS and ARM_HRR_SLOTS_PLUS_CLEANUP. (FLAT arm cannot
distinguish slot positions by design -- see T10 in the cell for that complement
test.)

## Calibration rationale

HRR-superposition crosstalk math at N=4096:
- After unbind, the recovered vector ~ item_i + noise where noise variance
  ~ (K-1)/N (sum of K-1 random bipolar binds dot-with slot tag). SNR (in units
  of codebook self-cosine = sqrt(N)) is ~ sqrt(N/(K-1)).

| K   | unbind SNR     | cleanup margin vs 256-atom codebook |
|-----|----------------|--------------------------------------|
| 8   | sqrt(4096/7)  ~ 24.2 | well above any reasonable threshold |
| 16  | sqrt(4096/15) ~ 16.5 | comfortable; should clear with cleanup |
| 32  | sqrt(4096/31) ~ 11.5 | DISCRIMINATOR -- expect ~0.85-0.95 cleanup |
| 64  | sqrt(4096/63) ~  8.1 | tightening; expect 0.50-0.85 cleanup |
| 128 | sqrt(4096/127)~  5.7 | degraded; expect 0.20-0.60 cleanup |
| 256 | sqrt(4096/255)~  4.0 | near codebook noise floor (sqrt(256)=16); near chance |

Noise sigmas:
- sigma=0.0..1.0 reuses smoke regime (sanity that production confirms smoke).
- sigma=1.5..2.0 extends into the noise floor already characterized in prior
  arc (Shannon-floor calibrated at sigma>=1.5 in adjacent cells); tests
  intersection of the working-memory capacity envelope with the noise envelope.

K=32 discriminator: between Miller (~7) and the unbind-SNR cliff (~64).
sigma=1.0 discriminator: meaningful noise (workspace ~~half-bit-corrupted by
quantization-after-noise) without being in the Shannon-floor regime.

ARM_HRR_SLOTS (no cleanup) at K=16, sigma=0.5: the cleanup-is-load-bearing
control. If raw nearest-neighbour without cleanup can't hold 16 items at
modest noise, the substrate working-memory primitive requires the cleanup
stage -- HARD_FAIL signals that the architectural complement (per c3 + g1b
precedent) is non-negotiable.

## N-suffix section
Anchor has no `_n<N>` suffix; PROT-018 / PROT-019 / PROT-021 do not apply
(production cell at N=4096 fixed; K, sigma swept as inner-loop). N_ITEMS_PER_K
controls trial count (= ceil(200/K)); N_DIM is held at 4096 throughout.

## Timeout estimate

Per-(K, sigma, arm, seed) cost: ceil(200/K) trials, each trial = K binds +
1 codebook matmul (256 x 4096) + K retrievals (each = 1 bind + 1 matmul). Per
trial dominant cost ~ 256 * 4096 + K * (4096 + 256 * 4096) ~ K * 1e6 flops at
K=8 and ~K * 1e6 flops at K=256 (codebook matmul per-retrieve is the dominant
term and is K-independent per retrieval). Numpy on a single core gives ~3e9
flops/s; per-(K, sigma, arm, seed) wall ~ 0.3-2.0s.

Total cells = 3 arms * 6 K * 5 sigma * 3 seeds = 270 cells. Worst case 2.0s/cell
= 540s = 9 min. Realistic 0.5s/cell = 135s = 2.25 min. Add codebook + slot-tag
build per seed (negligible).

Formula: ceil(1.5 * smoke_wall * (FULL_seeds/smoke_seeds))
       = ceil(1.5 * ~300s smoke wall measured below * 3 / 1)
       ~ 1350s -> rounded up to 3600s (1h) for safety + checkpoint headroom.
timeout_s = 3600

## Mechanism (informative)
Same as smoke (working_memory_hrr_slots_smoke_v1): bipolar random codebook +
slot tags; bind = elementwise product (involutive); workspace = sum of K binds;
add gaussian noise sigma; bipolar-quantize; retrieve_i = bind(noisy_ws, slot_i);
optional cleanup = argmax cosine(retrieved, codebook). Only the sweep ranges
change.

## Cites
- experiments/exp_working_memory_hrr_slots_smoke_v1.py (smoke; saturated
  recall 1.000 across K=2..16, sigma=0..1.0 -- discriminator too easy)
- preregs/2026-06-23_working_memory_hrr_slots_smoke_v1.md (smoke prereg;
  capacity math precedent)
- USER 2026-06-23 production-regime upgrade routing: "smoke saturated at
  1.000 across K=2..16; production needs harder regime to find where substrate
  working memory ACTUALLY breaks"
- Gap-3 composition enabler (substrate-native scratch space for multi-hop
  reasoning at super-human capacity bound)
