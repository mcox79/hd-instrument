# Prereg: substrate_per_context_T_diagnostic_v1

**Filed:** 2026-06-23
**Anchor:** substrate_per_context_T_diagnostic_v1
**Queue:** remote_cpu_queue
**Script:** experiments/exp_substrate_per_context_T_diagnostic_v1.py

---

## Research Question

Viability shotgun P8 (LIVE, 83% entropy-variance delta) contradicts production cell
substrate_per_context_decode_temperature_LM_v1 (HARD_FAIL, per-context arms -0.32 to -0.37 bits
vs unigram). This cell isolates the root cause.

---

## Hypothesis Space

- H1: Implementation difference -- production entropy formula differs from shotgun binary-search formula
- H2: Lambda-mix incompatibility -- lambda=0.3 mixes substrate into the prediction; if substrate < unigram,
  lambda>0 HURTS regardless of T routing
- H3: Scale-dependence -- per-context T benefit inverts at production N (8192) vs shotgun N (2048)
- H4: Codebook interaction -- sparse-bipolar codebook is incompatible with per-context T;
  dense random codebook (shotgun) works; sparse bipolar (production) does not

---

## Design

5 arms x 3 seeds x text8 N_TRAIN=10k N_DIM=4096:

| Arm | Codebook | T routing | lambda |
|-----|----------|-----------|--------|
| ARM_UNIGRAM | -- | -- | -- |
| ARM_GLOBAL_T_DENSE | dense random | global sweep | best from dev |
| ARM_PER_CONTEXT_T_DENSE | dense random | per-context (entropy + 50pct methods) | best 0.0 or 0.3 |
| ARM_GLOBAL_T_SPARSE_BIPOLAR | sparse f=0.05 | global sweep | best from dev |
| ARM_PER_CONTEXT_T_SPARSE_BIPOLAR | sparse f=0.05 | per-context (entropy + 50pct methods) | best 0.0 or 0.3 |

Per-context T arm tests BOTH lambda=0.0 (pure substrate) and lambda=0.3 (fair_harness best)
to isolate H2 (lambda confound).

Per-context T arm tests BOTH the production entropy formula (high-H -> T_low) AND the shotgun
50pct-target binary-search formula to isolate H1 (implementation difference).

---

## Pre-registered HARD Bands

### Primary verdict bands (codebook factor)

**CODEBOOK_DEPENDENT** (H4 confirmed):
- ARM_PER_CONTEXT_T_DENSE beats ARM_GLOBAL_T_DENSE by >= 0.05 bits BPC
- AND ARM_PER_CONTEXT_T_SPARSE_BIPOLAR does NOT beat ARM_GLOBAL_T_SPARSE_BIPOLAR by >= 0.05 bits
- Interpretation: per-context T works with dense encoder; fails with sparse-bipolar

**SCALE_DEPENDENT_OR_IMPLEMENTATION_BUG** (H3 or H1):
- ARM_PER_CONTEXT_T_DENSE does NOT beat ARM_GLOBAL_T_DENSE by >= 0.05 bits
- AND ARM_PER_CONTEXT_T_SPARSE_BIPOLAR does NOT beat ARM_GLOBAL_T_SPARSE_BIPOLAR
- Sub-discriminator: if T_std < 0.001 for both arms -> H1 (mechanism degenerate); if T_std > 0.001 -> H3 (scale)

**BOTH_CODEBOOKS_BENEFIT** (H2 = lambda confound; or production scale jump):
- Both per-context arms beat global by >= 0.05 bits at N_TRAIN=10k
- But production cell HARD_FAILed at N_TRAIN=100k -> scale hypothesis or lambda confound

### Guard condition

CONFOUNDED: ARM_GLOBAL_T_DENSE lift_vs_unigram < 0.05 bits.
Dense substrate not above unigram at N_TRAIN=10k. All H-tests unreliable.
Action: escalate to Strategy for N_TRAIN sweep.

---

## Calibration note

No prior empirical anchor isolating codebook type x T routing cross-factorially.
Bands are set at 0.05 bits (half of production's 0.10 HARD_PASS threshold).
This is a diagnostic not a performance cell; CODEBOOK_DEPENDENT or CONFOUNDED are the
two most informative verdicts.

---

## Timeout estimate

Smoke estimate: N_DIM=256 N_TRAIN=2k, 1 seed. Expect ~30-60s on remote CPU.
Full scale: N_DIM=4096 N_TRAIN=10k, 3 seeds, 5 arms.

Rough scaling:
- W matrix: 4096x4096 x 10k pairs -> dominant cost ~N_DIM^2 x N_TRAIN
- Scale factor vs smoke: (4096/256)^2 x (10000/2000) x 3 seeds = 256 x 5 x 3 = 3840x
- But RECALL_BATCH reduces peak memory; effective scaling ~N_DIM x N_TRAIN x seeds
- Per-context binary-search adds ~20x overhead per test token for method_B

Estimated FULL wall on remote_cpu: ~600-1800s (10-30 min) based on production cell
seed wall ~670-990s at N_DIM=8192 N_TRAIN=100k, scaled down to 4096/8192 and 10k/100k.
Scaling: 1800 * (4096/8192)^1.5 * (10000/100000) = 1800 * 0.354 * 0.1 = ~64s per seed.
3 seeds x 5 arms (dense + sparse, dev + test) x 2 methods: ~1200s max.

Timeout registered: 2700s (45min, 2x safety margin for 50pct-target binary search overhead).

---

## N-suffix note

No _nN suffix; production N = 4096 (N_DIM); rationale: this is a diagnostic cell not a
capacity-sweep cell. N is chosen for fast iteration to isolate the codebook x T interaction.
