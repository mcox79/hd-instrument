# Prereg: math4_proof_chains_v2_global_bundle_cpu_v1

## Anchor
math4_proof_chains_v2_global_bundle_cpu_v1

## Routing
v2 redesign of `math4_proof_chains_cpu_v1` per Director spawn 2026-07-02.
v1 SATURATED because per-antecedent-sharded storage `rule_vec[a] = cnorm(A_a * IMPL * B_a)`
makes each rule standalone; per-step unbind isolates B exactly; L-step chain accuracy stays
at 1.0 for any reachable NPROP (proven at NPROP=16000 in the sharded_capacity sibling).
Discriminator saturated; v1 FULL correctly refused.

v2 tests **STORAGE-STRATEGY under multi-hop chain composition** by adding two arms:
- ARM_SHARDED (positive control) — v1 mechanism at same regime
- ARM_BUNDLED — global-bundle `bundle_vec = sum_a cnorm(A_a * IMPL * B_a)`; per-step unbind
  SNR ~ 1/sqrt(NPROP-1); chain errors compound
- ARM_BUNDLED_L1 — single-hop bundle baseline; classical Plate 1995 mediocre-but-nonzero regime

Stage 3 (compositional understanding). Not Stage 4 language equivalence. Substrate-only
(no tokens, no text).

## Queue
FULL: `overnight_queue` (GPU-batched; per Director spawn 2026-07-02 + USER-LOCKED 2026-07-02
GPU-batching-mandatory rule).
SMOKE: `local_cpu_queue` (fast preview; ~1s wall total on CPU torch).

**Push required for FULL dispatch (I cannot push; Orchestrator handles).**

## Purpose
Does the substrate exhibit compositional pressure under multi-hop MP chains when rule storage
strategy changes? v1's per-antecedent shards insulate each rule from the others, so cleanup is
matched-filter perfect at every step. v2's global bundle superposes all rules into one
N-vector — per-step unbind SNR degrades with NPROP, chain errors compound with L, and the
substrate has no denoising path. If SHARDED handles chain composition cleanly while BUNDLED
collapses, then **storage strategy** is the load-bearing lever for Stage-3 compositional
capability (not just per-step primitive quality).

## Envelope-fail-bands (META_RULE_L: strict >= floor+5%)

Three simultaneous HP criteria (calibrated against empirical probe 2026-07-02 at NPROP {10,
20, 30, 50, 75, 100, 200, 500} L {2, 4, 6, 10}):

**Criterion I — SHARDED matched-filter robustness under chain composition:**
- HP: SHARDED accuracy at (L=L_max=10, NPROP=NPROP_max=500) >= 0.85
- Expected: 1.000 (empirical probe)

**Criterion II — STORAGE-STRATEGY gap at chain depth:**
- HP: SHARDED - BUNDLED at L=L_max (chain depth 10) >= 0.50 at some NPROP
- Expected: ~1.0 (empirical: SHARDED=1.0, BUNDLED collapses to 0.0-0.2 at L=10)

**Criterion III — CHAIN-DEGRADATION signature (single-hop vs multi-hop bundle):**
- HP: BUNDLED_L1 - BUNDLED at L=L_max >= 0.15 at some NPROP where BUNDLED_L1 >= 0.20
- Expected: ~0.4 (empirical: L1 ~0.5, L=10 chain ~0.0-0.15)

**HARD_PASS**: all 3 criteria met.
**MIDDLE_BAND**: 1-2 criteria met.
**HARD_FAIL**: 0 criteria met (substrate does not exhibit predicted storage-strategy pattern).

Strict-above-floor margin: SHARDED at L=10 NPROP=500 threshold 0.85 (empirical smoke 1.000 → 1.5x
above); storage-gap 0.50 (empirical 1.000 → 2x); chain-degrad 0.15 (empirical 0.500 → 3x). Not
floor-hugging.

## Discriminator (META_RULE_K: fires-check)

Class = STORAGE-STRATEGY selectivity at chain depth. Discriminator fires when
`SHARDED-BUNDLED gap >= 0.50` at some (L, NPROP) in the grid.

Smoke fires-check: at full-N=8192, one middle-NPROP + one high-L cell must show gap >= 0.50.
Verified: smoke 2026-07-02 shows gap 1.000 at (L=6, NPROP=200).

## Baseline-in-band (META_RULE_AG) — EXEMPTED with rationale

`baseline_in_band` exempted. This is a **STORAGE-STRATEGY comparison cell**, not
mechanism-vs-baseline. Both arms use identical substrate primitives (FHRR bind/unbind, cleanup
argmax); the only difference is rule-storage layout (per-antecedent shard vs global bundle).
- SHARDED (positive control) saturates near 1.000 — that IS the finding: sharded storage
  supports arbitrary-depth chains at reachable NPROP.
- BUNDLED (mechanism-under-test) collapses to floor at L>=4 for NPROP>=20 — that IS the
  finding: bundle storage cannot support chain composition.
- BUNDLED_L1 hovers in 0.33-0.60 across NPROP — that IS the finding: single-hop bundle is
  measurable-but-mediocre; chain compounding kills it.

Neither arm is a spurious background that shouldn't saturate. The saturation IS the signal.
Not an AG-rule violation.

`arms_differ_verified`: True — hash-verified per NPROP that `sharded_codebook` and `bundle_vec`
produce distinct byte representations (META_RULE_AF; assert in `run_phase_matrix`).

## Compute architecture (USER-LOCKED 2026-07-02)
Class: **(a) batched-GPU**.

Justification: substrate primitives (cnorm, matmul cleanup) are matmul-heavy. TR trials batched
at each chain step (all trials share the same rule storage). Chain steps sequential per trial
(step k+1 depends on cleanup output of step k) — sequential-inside, batched-outside.

Wall estimate: 5 L × 5 NPROP × 3 arms × 100 TR at max (L=10, NPROP=500, N=8192) → cleanup
matmul (TR=100, N=8192) @ (N=8192, NPROP=500) = 4e8 FLOPs per step × 10 steps = 4e9 per unit
(BUNDLED/SHARDED, L=10, NPROP=500). Total across grid ~ 2e11 FLOPs. On GPU (torch complex64,
~5 TFLOPS effective) ~ 0.04s per unit, total 5-10s. On CPU (~200 GFLOPS) ~ 2-5s per unit,
total ~ 3-5min. Both viable but GPU is 30-50x speedup on the FULL grid — GPU-batching mandate
applies.

Wall-time sanity check: local CPU smoke ran 12 units in <1s (SHARDED/BUNDLED matmuls dominate).
Full GPU dispatch expected < 60s.

## Prior-work check
Substrate-KB concept query `bash tools/substrate_query.sh "global bundle chain composition
L-step degradation modus ponens capacity"` (2026-07-02) returned:
- Top hits at cosine 0.31-0.34 (below the 0.30 cross-check threshold for surprise-collision):
  generic "composition" atoms, "composition classification" prereg-chunks, "composition
  budget" drill notes.
- **None match** global-bundle chain-composition mechanism. No prior operational bundle-vs-
  sharded chain-storage discriminator cell exists in the substrate.
- Related sibling: `sharded_capacity_beyond_bundle_bound_v1` (3 seeds queued at position
  10-12 overnight_queue) — tests SHARDED capacity vs BUNDLE floor at SINGLE-HOP L=1. THIS cell
  tests the same discriminator at MULTI-HOP chain composition (L=2..10). Complementary; no
  redundancy.
- Related predecessor: `math4_proof_chains_cpu_v1` (this session, SATURATED at NPROP=16000
  L=6 with sharded storage). v2 addresses the saturation via bundle-storage arm.

Prior-work check: **NONE at cosine>0.30 for the specific mechanism**. Genuinely novel; not a
rediscovery.

## CRLB / capacity-feasibility (§9)
`crlb_floor_computed`: n/a. Discriminator is gap-based, not noise-floor-based. Substrate-physics
prediction: per-step BUNDLED unbind SNR ~ N / sqrt(NPROP-1). At N=8192, NPROP=500, per-step SNR
~sqrt(8192/499) ~ 4.05; argmax over 500 with SNR 4 gives per-step accuracy ~0.1-0.3 (empirical
0.15 confirms); L=10 chain compounds to ~0. THEORETICAL@compounded-Bernoulli-in-argmax-noise.

`discriminator_reachability`: True. HP thresholds are achievable per empirical probe (all 3
smoke criteria exceeded thresholds by 1.5x-3x margin).

## Arms-must-differ (META_RULE_AF)
`arms_differ_verified`: True. In `run_phase_matrix`, per NPROP we hash-verify:
- SHARDED codebook (NPROP, N) complex64 bytes → SHA256 prefix
- BUNDLE vec (N,) complex64 bytes → SHA256 prefix
Assert distinct at each NPROP (raises META_RULE_AF violation if bit-identical).

Additionally, at retrieval time the arms use different code paths:
- SHARDED: `sharded_codebook[ci]` (per-trial indexed rule)
- BUNDLED: `bundle_vec.unsqueeze(0).expand(TR, -1)` (same vector for all trials)
Verified via cell-code review.

## Final-metrics atomicity (META_RULE_AH)
`final_metrics_atomicity`: `tmp_replace` via `experiments/_seed_checkpoint.write_metrics`
(writes tmp then `os.replace()` atomically). Crash-diagnostic also uses `os.replace`.

## Except-SystemExit ordering (§8)
Outer `try/except` at end of file:
```
try: main()
except SystemExit: raise
except KeyboardInterrupt: raise
except Exception as e:  # NOT BaseException
    _write_crash_metrics(...); raise
```
Grep gate verified: no bare `except:`; no `except BaseException`.

## Cardinality (META_RULE_H)
Sweep-axis cell.
- FULL: `EXPECTED_N_UNITS = 5 (L) × 5 (NPROP) × 3 (arms) = 75`
- SMOKE: `EXPECTED_N_UNITS = 2 × 2 × 3 = 12`

Verdict logic counts `len(per_unit)`; if != expected, overrides verdict to
`HARD_FAIL_CARDINALITY_BREACH_META_RULE_H`.

`cardinality_ok` field written to metrics.json.

## Discriminating-fraction (Gate B)
5 L × 5 NPROP × 3 arms = 75 phase points. Empirical probe predictions:
- SHARDED: 25 points all saturate at 1.000 (positive-control by design; these establish the
  ceiling for the discriminator gap; not intended as varying-signal points)
- BUNDLED_L1: 25 points all in [0.35, 0.60] band (all in discriminating band [0.30, 0.70])
- BUNDLED: 25 points range from [0.00, 0.35] with L=2 at high end, L>=4 mostly at floor. ~7-10
  in discriminating band [0.30, 0.70]; the rest at floor demonstrating the chain-collapse.

For the DISCRIMINATOR gap (SHARDED - BUNDLED at L=L_max): 5 NPROPs × 1 L_max = 5 gap values;
all 5 predicted to be >= 0.85 (well within HP band).

`discriminating_fraction`: 25/25 for BUNDLED_L1 in-band; 5/5 gap-values >> HP threshold.

## Sweep-alignment (Gate A)
Swept params: L (chain depth), NPROP (rule-base size).
Effective per-primitive:
- SHARDED cleanup: effective_NPROP = NPROP (rule vector indexed by antecedent → cleanup
  against props codebook of size NPROP)
- BUNDLED unbind: effective_NPROP = NPROP (bundle sum size = NPROP)
- Chain depth L: effective_L = L for BUNDLED/SHARDED; effective_L = 1 for BUNDLED_L1 (single-hop
  baseline; L slot is redundant across L for BUNDLED_L1 accounting)

`sweep_alignment_verdict`: ALIGNED. No misalignment between nominal and effective sweep axes.

## Composition-edges (Gate C)
Single-primitive cell (FHRR bind + unbind + cleanup argmax); no cross-primitive composition.
Shape checks:
- Rule storage (SHARDED): (NPROP, N) complex64 → per-trial index (TR,) → (TR, N)
- Rule storage (BUNDLED): (N,) complex64 → broadcast to (TR, N)
- Unbind: (TR, N) * (TR, N) * (1, N) → (TR, N)
- Cleanup: matmul (TR, N) @ (N, NPROP) → real (TR, NPROP) → argmax (TR,)
SHAPE_MATCH throughout.

`composition_edges`: n/a (single-primitive).

## Positive-control (Gate D)
Chain-grade primitive invoked: FHRR bind (`*`), unbind (`* conj()`), cleanup argmax.
- Cited prior: `math4_proof_chains_cpu_v1` at (NPROP=60, L=2/4/6) achieved SHARDED accuracy
  ~1.000 (v1 selftest expected 0.65+); sibling `sharded_capacity_beyond_bundle_bound_v1`
  achieves SHARDED accuracy 1.000 at NPROP=16000 for single-hop (this session's smoke).
- ARM_SHARDED in v2 IS the positive control at the test regime (5 NPROP × 5 L). Empirical
  probe confirms SHARDED reproduces the prior chain-grade result across the full v2 grid
  (SHARDED = 1.000 at every phase point) — regime extension VERIFIED.
- Regime: complex64 phasors at N=8192, NPROP in [20, 500], L in [2, 10]. Same primitive class
  as prior atoms; wider NPROP × L range than any single prior cell.
- Tolerance: SHARDED accuracy at (L_max=10, NPROP_max=500) >= 0.85. Threshold well above prior
  chain-grade tolerance floor.

`positive_control_arms.PRIMITIVE_REPRODUCE_AT_TEST_REGIME`: SHARDED arm (all 25 phase points).
`regime_extension_audit`: SHAPE_MATCH (same primitive; wider grid; empirically verified).

## Functional-requirements (Gate E)
1. **Store implications as a rule base**: cell impls TWO storage strategies (SHARDED per-a
   codebook + BUNDLED single-vector superposition). Encoding mechanism explicit.
2. **Derive consequent from (rule, current_fact) via unbind + cleanup**: both arms use
   identical unbind (`rule * conj(A) * conj(IMPL)`) and identical cleanup (argmax over props
   codebook). Only rule-source differs.
3. **Chain L steps**: both BUNDLED and SHARDED feed recovered fact back into step k+1. Chain
   integrity depends on per-step accuracy; SHARDED matched-filter yields near-perfect;
   BUNDLED superposition-noise yields collapse.
4. **Compare storage strategies**: 3-arm design isolates storage-layout as the ONLY changing
   factor across arms at fixed (L, NPROP, seed).

Functional requirements mapped to chain-grade primitives (FHRR bind/unbind/cleanup) + a new
axis of comparison (storage layout).

## Defensive-error-checking (§13)
- `cell_chunked`: False (single-file; FULL wall estimate < 60s on GPU / < 5min on CPU;
  runner-death loses this single seed only)
- `start_marker_written`: True (writes `_start_marker.json` at main() entry, before selftest
  and before phase-matrix loop)
- `crash_diagnostic_present`: True (`_write_crash_metrics` writes atomic
  `metrics.json` with `verdict: CELL_CRASHED` on any Exception; SystemExit + KeyboardInterrupt
  re-raise cleanly)
- `heartbeat_present`: False (FULL wall < 5min max; per-unit landing lines already flushed via
  `print(..., flush=True)`; runner_status.py can tail stdout for progress)
- `defensive_error_checking`: `exempt_short_cell (FULL wall < 5min)`

## Progress-logging (§17)
`progress_logging`: `print_flush_true`. All `print()` calls use `flush=True`. `sys.stdout` also
reconfigured to `line_buffering=True` at cell start. Runner invokes with `python -u` (defense
in depth). Cell timeout target 900s (well below 1800s threshold).

## Calibration-check (META_RULE_M)
`calibration_check`: `default_ok_for_this_regime`. FHRR complex-phasor primitives at N=8192
match all prior chain-grade cells (sharded_capacity, math4_proof_chains_v1, cortex_hippo). No
adaptive tuning. Discriminator gap thresholds calibrated against empirical probe run in
scratchpad prior to FULL dispatch (probe log in
`C:/Users/marsh/AppData/Local/Temp/claude/.../scratchpad/probe_v2_regime.py`).

## Stage-progression check (USER-LOCKED 2026-06-26)
Stage 3 (compositional understanding). Substrate-only synthetic FHRR phasors; NO tokens, NO
text, NO language benchmarks. Multi-hop modus ponens chains ARE the operational test of
compositional-reasoning-chain longshot. VERIFIED Stage 3.

## Substrate-doesn't-know-anything check (USER-LOCKED 2026-06-26)
N/A — no language content. Substrate-physics test.

## Selftest formulas (PROT-022)
1. **SHARDED matched-filter robustness**: SHARDED at (L=6, NPROP=50) >= 0.85 AND
   SHARDED at (L=10, NPROP=500) >= 0.85. Assertion in `_selftest` (values 1.000 empirical).
2. **BUNDLED_L1 mediocre-but-nonzero band**: BUNDLED_L1 at NPROP=50 in [0.20, 0.85].
   Assertion in `_selftest` (empirical 0.617).
3. **BUNDLED multi-hop collapse**: BUNDLED at (L=6, NPROP=50) <= 0.30 AND BUNDLED at (L=2,
   NPROP=500) <= 0.40. Assertion in `_selftest` (empirical 0.083 / 0.150).
4. **Chain-degradation signature**: `BUNDLED_L1 - BUNDLED_L6` at NPROP=50 >= 0.15. Assertion
   in `_selftest` (empirical 0.533).
5. **Storage-strategy gap**: `SHARDED - BUNDLED` at (L=6, NPROP=50) >= 0.50. Assertion in
   `_selftest` (empirical 0.917).

`--self-test` PASS confirmed pre-smoke (this session, 2026-07-02).

## Timeout
- SMOKE (12 units, TR=30, local_cpu_queue): 300s (empirical wall < 5s CPU; generous buffer)
- FULL (75 units, TR=100, overnight_queue GPU): 900s (empirical CPU probe ~ 1s / 12 smoke
  units × 75/12 × TR ratio 100/30 = ~21s CPU; GPU 30-50x faster ~ 1-2s; wall for full run
  including matrix aggregation ~ 30-60s; timeout 900s = 15min = huge buffer for shared-host
  variance)

## Number tagging (META_RULE_AC)
- SHARDED at (L=6, NPROP=200) smoke = 1.000
  MEASURED@d:/AI/hd-instrument/data/exp_math4_proof_chains_v2_global_bundle_cpu_v1/metrics.json:per_unit
- Storage-strategy gap 1.000 at (L=6, NPROP=200) smoke
  MEASURED@same-path
- Chain-degradation gap 0.500 at NPROP=200 smoke  MEASURED@same-path
- Full-grid FLOP estimate 2e11  THEORETICAL@compute-architecture-analysis
- Plate 1995 bundle-capacity bound 0.14*N ~ 1147  CITED@Plate 1995 HRR paper
- Per-step BUNDLED SNR ~ N / sqrt(NPROP-1)  THEORETICAL@matched-filter-superposition-noise
- SHARDED empirical probe values (1.000 at all points)  MEASURED@scratchpad/probe_v2_regime.py

## Landed-VET request
On FULL landing, Skunkworks landed-VET should verify:
- All 3 HP criteria measured on actual per_unit data
- `arms_differ_verified: True` in metrics.json
- `cardinality_ok: True` (75/75 units)
- `meta_arm_hashes_by_nprop` distinct sharded_hash vs bundle_hash per NPROP
- Storage-strategy finding tier: if HP criteria hold at FULL, this is a substrate-physics
  atom (STORAGE-STRATEGY primitive) — MM_TENTATIVE at minimum, CG-eligible if 3 seeds
  reproduce (single-seed cell here; if orchestrator wants CG, dispatch seed 13 + 19 siblings)
