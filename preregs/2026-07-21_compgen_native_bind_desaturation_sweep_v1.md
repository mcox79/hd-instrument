# Pre-reg: compgen native-bind DE-SATURATION sweep v1

**Anchor:** `compgen_native_bind_desaturation_sweep_v1`
**Cell:** `experiments/exp_compgen_native_bind_desaturation_sweep_v1.py`
**Filed:** exp_dev, 2026-07-21. LOCAL-only (no push/persist/bank; Skunkworks VETs on land).
**Parent:** `exp_compgen_native_bind_role_filler_v1` (commit 34544d2b, HARD_PASS, gap=1.0 SATURATED).

## Question
The base cell showed native-bind LEARNED encoder generalizes to held-out (concept, role)
combos 1.0 vs fair-flat 0.0 -- but on a CLEAN regime (N=1024, 24 near-orthogonal FHRR codes,
no noise), so gap=1.0 is SATURATED (construction-favorable magnitude). Does native's edge
SURVIVE realistic ambiguity/noise, or is it a clean-regime artifact? SWEEP difficulty.

## Difficulty axes (two INDEPENDENT single-knob sweeps, both anchored at the base regime)
- **SWEEP A -- CLEANUP NOISE (test-time robustness):** train each arm CLEAN once per seed, then
  EVALUATE in-dist + held-out under additive complex Gaussian noise on the composed FHRR vector.
  `sigma in {0, 4, 8, 12, 18, 24, 32, 48}` at N=1024, V=24. Fine-grained erosion curve.
  THEORETICAL@ cleanup transition `sigma_crit ~ sqrt(N / ln V) ~ 18`; grid brackets it.
- **SWEEP B -- ORTHOGONALITY / VOCAB (genuinely harder LEARNED task):** train+eval from scratch at
  `(N_DIM, N_FILL, N_VERB) in {(1024,24,12),(256,48,16),(128,96,24),(64,96,24),(48,96,24)}`. Smaller
  dimension + larger vocab => codes NOT near-orthogonal => cleanup crosstalk rises => in-dist
  non-trivial. A DIFFERENT erosion mechanism (code packing, not additive noise) as cross-check.

Both axes share the base point (positive control that must reproduce native 1.0 / flat 0.0).

## Arms (reused from base cell; one variable A vs B = readout binding-vs-flat)
- A `native_bind_shared` [MECHANISM]; B `flat` [FAIR BASELINE]; C `native_bind_scramble` [MUST-FAIL];
  D `native_bind_tied` [LIVE-ALT / free-algebra locus].

**Flat noise transparency:** SWEEP A additive noise lives on the FHRR composed vector, which flat
does NOT consume. Flat is noise-invariant by architecture. This is HONEST and non-confounding
because flat's held-out is STRUCTURALLY ~0 at EVERY level (a role-head gets no gradient for a
concept never seen in that role). Gap native-flat reduces to native's held-out; flat's role at each
level = structural-0 floor + "task remains in-dist learnable" control. The de-saturation WITNESS is
NATIVE'S OWN in-dist dropping off 1.0 (cleanup now hard).

## Pre-registered bands (design-gate)
- **Positive control (Gate D):** base sigma=0 / N=1024 => native in-dist >= 0.95, native held-out
  >= 0.90, flat held-out <= 0.10. Fail => HARD_FAIL_POSITIVE_CONTROL.
- **DE-SATURATION valid:** native in-dist must drop <= 0.90 at SOME swept level (else regime too
  easy -> INCONCLUSIVE_REGIME_TOO_EASY).
- **CG_ROBUST** (edge survives realistic difficulty): at every level where native in-dist >= 0.60,
  native held-out >= 0.85*in-dist - 0.05 (held-out erodes no faster than in-dist) AND native beats
  tied held-out by >= 0.30; AND native held-out at the de-sat onset (first sigma with in-dist<=0.95)
  >= 0.70.
- **CLEAN_REGIME_ONLY** (honest bound): native held-out < 0.40 while native in-dist still >= 0.90
  (held-out collapses BEFORE cleanup gets hard = compgen-specific fragility).
- **GRACEFUL_EROSION**: de-sat valid, no early collapse, but robust/onset thresholds not fully met.
- **HARD sentinels (design integrity, all levels):** flat held-out < 0.30; scramble held-out <= 0.20.

## SCHEMA-VET / cell-template compliance
- arms_differ_verified: true (SHA256 on base-regime seed0 arm signatures + scramble sig; asserted in run()).
- final_metrics_atomicity: tmp_replace.
- except SystemExit: raise BEFORE except Exception (no BaseException; no bare except -- grep-clean).
- crlb: THEORETICAL cleanup transition sigma_crit ~ sqrt(N/ln V); sweep brackets it; discriminator reachable.
- baseline_in_band / DE-SAT gate: native in-dist verified to drop <= 0.90 at smoke (sweepA sigma=48
  -> 0.043; sweepB N=128/V=96 -> 0.858) MEASURED.
- discriminator survives scale: SWEEP A runs at FULL N=1024; smoke keeps full N (fewer seeds/epochs/sigmas).
- cardinality_ok: EXPECTED_N_UNITS = len(sigmas)*seeds*arms + len(regimes)*seeds*arms.
- deterministic_seeding: fixed int seeds + sorted() splits + index-derived noise generators; NO hash()-seeded RNG.
- progress_logging: line_buffered_stdout (flush prints; timeout set 1800 conservative).
- Compute architecture: (b) sequential-CPU with justification -- small complex matmuls (dim<=1024,
  V<=96); base cell ran CPU at 92s; per-unit wall < 10s; GPU batching not worth setup at these dims.
- No composition of prior chain-grade primitives beyond the base cell's own arms (positive control
  IS the base-regime reproduction); Gate D satisfied by the sigma=0/N=1024 anchor reproducing base.

## Smoke result (MEASURED@ data/exp_compgen_native_bind_desaturation_sweep_v1/metrics.json, run_mode=smoke, 1 seed)
- verdict=GRACEFUL_EROSION; positive control + all sentinels + de-sat gate GREEN; cardinality_ok.
- SWEEP A (N=1024): sigma 0 -> nat_ind/ho 1.00/1.00; sigma 12 -> 0.263/0.207; sigma 32 -> 0.075/0.100;
  sigma 48 -> 0.043/0.050 (chance 0.042). Held-out TRACKS in-dist (no compgen-specific fragility).
- SWEEP B: N=1024/V=24 -> 1.00/1.00; N=128/V=96 -> nat_ind 0.858 / nat_ho 0.829 (flat_ind 0.873,
  flat_ho 0.000, tied_ho 0.021). Native holds a large held-out edge at genuinely non-trivial cleanup.
- Full run (3 seeds, 8 sigmas, 5 regimes, 60 ep) sharpens the knee + confirms across seeds.

## LOCAL-only
No push, no store mutation, no atom bank. Skunkworks VETs on land.
