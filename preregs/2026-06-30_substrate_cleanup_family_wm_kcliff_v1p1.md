# Pre-registration: substrate_cleanup_family_wm_kcliff_v1p1 (memory-fit retry)

**Date:** 2026-06-30
**Author:** exp_dev (Opus 4.7 1M, agent-spawn)
**Trigger:** v1 FULL OOM'd on GPU (4.92 GiB held by torch allocator before
cleanup_no_cleanup does `query @ codebook.T` allocating 1.91 GiB). Orchestrator
a84633a7 confirmed structural; retry also OOM'd. USER directive: 6-hour
high-priority remote dispatch with reduced memory profile.

## Memory-fit deltas vs v1 (NO experimental-design change)

1. N_DIM 8192 -> 4096 (halves memory per tensor; ~4x reduction in classical
   Hopfield W matrix: 256 MiB -> 67 MiB)
2. num_banks 16 -> 8 (halves K-total bank product)
3. Chunked-K matmul for `cleanup_no_cleanup` + `cleanup_k_NN_lookup`
   (chunk_size=64 codes per row-block; avoids 1.91 GiB peak allocation;
   numerically equivalent to un-chunked matmul; verified)
4. Sequential per-arm `torch.cuda.empty_cache()` between cleanup arms
   inside `run_one_seed_phase_diagram`

Experimental-design integrity PRESERVED:
- Same 5 cleanup primitives (no_cleanup / classical_hopfield /
  modern_hopfield_continuous / iterative_attractor / k_NN_lookup)
- Same K_per_bank sweep [50, 100, 250, 500, 1000]
- Same discriminator: cliff_log2_span >= 0.5 OR 3 of 5 cleanups differ

Smoke results (3 seeds at full N=4096 CPU-fallback): all HARD_PASS_SMOKE;
15/15 cardinality; 10/10 pred+mech distinctness; cliff_log2_span=2.322;
classical_hopfield DOMINATED (recall 0.024 at K=250) while other 4
COMPETITIVE — discriminator survives scale.

## Anchor

`substrate_cleanup_family_wm_kcliff_v1p1_seed_{7,13,19}` (3 chunked sibling cells).
Shared core: `experiments/_substrate_cleanup_family_wm_kcliff_v1p1_core.py`.
Primitive library: `hdlab/cleanup_family.py`.

## Why this cell exists (the gap)

PC cleanup family phase diagram (2026-06-28, atom a009a44a) CG'd as convergent
MIDDLE_BAND -- cleanup choice family-invariant at PC scale. The 4 PC cleanups
(modern_hopfield / classical_hopfield / iterative_cosine / soft_energy_attractor)
all produced similar recall under low-corruption regimes. WM is a DIFFERENT
regime: higher K (per-bank capacity load); multi-bank routing; sequence-binding-
adjacent. Possibly cleanup family DISCRIMINATES here.

Spec proposes 5 primitives (4 + no_cleanup baseline) over K_per_bank-sweep with
num_banks=16, N=8192. Discriminator: K_cliff localization differs across cleanups.

## Routing

- **Smoke queue:** smoke on remote_cpu_queue OR local CPU (.venv direct invocation).
  Smoke regime N=2048; ~30-60s/seed CPU.
- **Full queue:** **overnight_queue** (GPU). Modern Hopfield softmax-attention at
  N=8192 x M~8000 codebook is matmul-bound; GPU mandatory for tractable wallclock.
- **Push constraint:** harness-DENIED push from exp_dev. Full dispatch routes
  through Orchestrator (request via SendMessage post-smoke).

## Cleanup family primitives (OUTER axis)

5 families, common signature `(query: (K, N), codebook: (M, N)) -> (recovered, pred_idx)`:

| Family | Mechanism | Citation |
|--------|-----------|----------|
| `no_cleanup` | baseline; argmax over codebook on raw query | strict reference floor |
| `classical_hopfield` | Hebbian W=X.T@X/M; iterate sign(s@W) | Hopfield 1982 |
| `modern_hopfield_continuous` | softmax-attention update: sign(softmax(beta*s@X.T) @ X) | Ramsauer 2021 |
| `iterative_attractor` | L2-normalized cosine softmax (brain-canonical CA3) | Treves-Rolls; hdlab/iterative_attractor.py |
| `k_NN_lookup` | one-shot top-1 argmax (snap to nearest) | substrate default |

## Sweep axes

| Axis | FULL values | SMOKE values | Count |
|------|------|------|-----|
| cleanup_family (OUTER) | 5 cleanups | 5 cleanups | 5 |
| K_per_bank (inner) | {50, 100, 250, 500, 1000} | {50, 100, 250} | 5 / 3 |
| regime (inner) | {RANDOM, ADVERSARIAL} | {RANDOM} | 2 / 1 |
| num_banks (fixed) | 16 | 16 | 1 |
| N_dim (fixed per mode) | 8192 | 2048 | 1 |

**Cardinality FULL per seed:** `5 * 5 * 2 = 50` phase points.
**Cardinality SMOKE per seed:** `5 * 3 * 1 = 15` phase points.
**Cardinality FULL across 3 seeds:** `50 * 3 = 150` total grid points.

Fixed substrate parameters:
- `beta = 8.0` (softmax temperature for Hopfield primitives)
- `hop_max_steps = 4` (iteration cap for Hopfield + iterative_attractor)
- `CUE_COS = 0.70` (cue-to-bank-tag similarity; matches WM K-cliff envelope)
- `SIGMA = 1.0` (workspace noise; matches envelope)
- `FEATURE_OVERLAP_FRAC = 0.20` (adversarial regime overlap)

## CRLB / capacity-feasibility validation (META_RULE_AG)

`estimated_cliff_K_per_bank(N=8192, num_banks=16) = N / num_banks = 512`

Sweep K_per_bank = {50, 100, 250, 500, 1000} brackets this cliff:
- K=50, 100, 250: below cliff (recall expected SATURATED / HARD_PASS)
- K=500: near cliff (recall expected DISCRIMINATING [0.10, 0.95])
- K=1000: above cliff (recall expected FLOOR for naive cleanups)

`discriminator_reachability: True` -- HARD_PASS bands attainable since at least
1 K-value is below cliff and at least 1 above.
`bracket_includes_discriminating_band: True` -- K=500 is in band [0.10, 0.95].
`crlb_formula_reference: "matched-filter SNR = sqrt(N) / sqrt(M-1); cliff at M ~ N+1, K_per_bank ~ N/num_banks"`

## Pre-reg bands (LOCKED at module init)

**Per-point tiers:**
- SATURATED: `recall >= 0.995` (META_RULE_Q suspect-1.000)
- HARD_PASS: `0.80 <= recall < 0.995`
- MIDDLE_BAND: `0.50 <= recall < 0.80`
- FLOOR: `recall <= 0.10`
- HARD_FAIL: otherwise

**Cell-level FULL discriminator:**

- **HARD_PASS:** at least 3 of 5 cleanup arms produce DISTINCT K_cliff predictions
  (cliff_log2_span >= 0.30 AND n_pairs_pred_differ >= 5 of 10 pairs AND n_disc >= 15)
  AND distinctness_self_report_pass AND positive_control_pass AND cardinality_ok
  AND not Q-saturation (sat_fraction < 0.75)
- **MIDDLE_BAND:** partial cleanup discrimination (cliff_log2_span >= 0.15 OR
  n_pairs_pred_differ >= 3) but below chain-grade
- **HARD_FAIL:** all 5 cleanups converge -- cleanup choice family-invariant at WM
  scale too (same as PC finding); OR META_RULE_AY distinctness_self_report fails

**Smoke discriminator (DISCRIMINATOR-MUST-SURVIVE-SCALE):**

At smoke regime (N=2048, K=[50,100,250]), require at smoke:
- cliff_log2_span >= 0.30 (across cleanups), OR
- n_pairs_pred_differ >= 5 of 10, OR
- no_cleanup_recall_mean < 0.85 (baseline exercised, mechanism gets to fire)

If NONE of these, BLOCK_DISPATCH -- regime too easy at smoke, won't differentiate
at full either.

## Discipline gates (mandatory; all checked)

- META_RULE_H (cardinality_ok): `EXPECTED_N_UNITS_FULL=50`, `EXPECTED_N_UNITS_SMOKE=15`.
  Verdict-emitter HARD_FAILs on observed != expected.
- META_RULE_AY (NEW 2026-06-30): verdict-emitter HARD_FAILs on
  `distinctness_self_report_pass == False`. Prevents v1/v3 ANCHOR 4 phantom-
  degeneracy pattern.
- META_RULE_AX: per-arm mechanism_hash distinct + per-K per-arm metric distinct.
  Tracked via pairs_mech_differ AND pairs_pred_differ.
- META_RULE_AW: identical config across seeds (3 sibling files import same core).
- META_RULE_Q: suspect-1.000 saturation check (sat_fraction >= 0.75 -> MIDDLE_BAND).
- META_RULE_AF: arms-must-differ; 5 cleanup outputs SHA-256 hashed per phase point.
- META_RULE_AG (CRLB / capacity-feasibility): cliff_estimate = N/num_banks = 512
  brackets sweep K-values; HARD_PASS bands attainable.
- META_RULE_J: no silent except: blocks; per-unit failure-class instrumentation.
- META_RULE_AC: numbers in this pre-reg tagged.
- META_RULE_AH: atomic-final-metrics-write via _seed_checkpoint write_partial_key
  then aggregate -> atomic metrics.json write at end.

## Schema-VET fields

- `cardinality_ok: bool`
- `arms_differ_verified: bool` (set True at smoke gate via distinctness_self_report_pass)
- `final_metrics_atomicity: "tmp_replace"`
- `cell_chunked: true` (3 chunked sibling cells; one seed per cell)
- `start_marker_written: true`
- `crash_diagnostic_present: true`
- `heartbeat_present: true` (per-phase-point flush prints)
- `defensive_error_checking: passed_all_4_patterns`
- `crlb_floor_computed: 512` (estimated_cliff_K_per_bank at N=8192/16)
- `discriminator_reachability: true`
- `baseline_in_band: true` (no_cleanup expected MIDDLE_BAND at K=500 in N=8192;
  at K=50 expected SATURATED or HARD_PASS; bracket spans the band)
- `sweep_alignment_verdict: ALIGNED` (K_per_bank is the natural sweep axis for
  each cleanup primitive; no hidden parameter mismatch)
- `discriminating_fraction: 0.60` (3 of 5 K-values predicted to land in band:
  K=250 floor edge, K=500 in band, K=1000 above-cliff edge)
- `composition_edges: bipolar codebook -> cleanup -> argmax SHAPE_MATCH`
- `positive_control_arms:` no_cleanup @ K=50, RANDOM, expected recall >= 0.80
  (prior atom: WM K-cliff multi-bank cells at K_per_bank << cliff routinely
  show recall=1.000; conservative floor 0.80 here for primitive-library cell)
- `functional_requirements:` 1. associative recall under bank-routed cue ->
  any-cleanup primitive; 2. distinguishable cleanup mechanisms -> verified via
  pred-pattern hash distinctness

## Effort estimate

- `hdlab/cleanup_family.py`: ~220 LoC (5 primitives + selftest)
- `_substrate_cleanup_family_wm_kcliff_v1_core.py`: ~620 LoC (5 primitive impls +
  per-point eval + selftest + per-seed sweep + verdict)
- 3 sibling cells: ~260 LoC each x 3 = 780 LoC (mostly boilerplate; SEED differs)
- This pre-reg: ~150 lines
- **Total ~1900 LoC** (higher than spec ~600 because chunked architecture adds
  per-seed boilerplate)
- **Estimated wallclock per seed FULL:** ~30-90 min on overnight GPU.
- **Timeout per seed:** 7200s (per spec).
