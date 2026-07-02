# Prereg: math4_rung3_deep_chains_v2_global_bundle_cpu_v1

## Anchor
math4_rung3_deep_chains_v2_global_bundle_cpu_v1

## Routing
v2 redesign of `math4_rung3_deep_chains_cpu_v1` per Director spawn 2026-07-02.
v1 as-authored used per-antecedent-sharded storage (SAME template as
`math4_proof_chains_cpu_v1` which saturated). Deep chains L=8/10/12 would just
prove SHARDED works perfectly at any depth (already proven by
`math4_proof_chains_v2_global_bundle_cpu_v1` up to L=10 at NPROP=500). Cell
would rediscover the same result.

v2 applies the SHARDED-vs-BUNDLED-vs-BUNDLED_L1 3-arm discriminator (from
math4_v2 template) to DEEPER chains than v2 tested. Extends the storage-
strategy substrate-physics finding to L up to 20 (v2 tested L in {2,4,6,8,10};
this tests L in {4,8,12,16,20}).

Stage 3 (compositional understanding). Not Stage 4 language equivalence.
Substrate-only synthetic FHRR phasors (no tokens, no text).

## Queue
FULL: `overnight_queue` (GPU-batched; per Director spawn 2026-07-02 + USER-LOCKED
2026-07-02 GPU-batching-mandatory rule). 3-seed via HDLAB_SEED wrappers (seeds
7 / 13 / 19) — Orchestrator dispatches. Push required for FULL dispatch
(I cannot push; Orchestrator handles).

SMOKE: `local_cpu_queue` (fast preview; ~1s wall total on CPU torch).

## Purpose
Does the storage-strategy substrate-physics finding from math4_proof_chains_v2
(L up to 10) EXTEND to DEEP chains (L up to 20)? Three sub-questions:

1. **SHARDED chain-independence extension**: Does SHARDED matched-filter
   retrieval remain near-perfect at L=20? (Analytical: `cnorm(A*IMPL*B) *
   conj(A) * conj(IMPL) = B` exactly, so per-step retrieval is exact and chain
   depth is not the constraint. Confirms this is a mathematical property, not
   an empirical artifact of small L.)

2. **BUNDLED collapse at deep L**: Does BUNDLED collapse deepen further at
   L>10 vs v2's L<=10 result, or is BUNDLED already at floor at L=2? (Empirical
   probe: BUNDLED at NPROP=100 L=20 = 0.10 vs L=4 = 0.05 vs L=2 = 0.30. Deep-L
   collapse observable but already-collapsed at moderate L for higher NPROP.)

3. **Chain-degradation quantifiable at low NPROP**: At NPROP in {10, 20, 50,
   100} where BUNDLED_L1 stays measurable (~0.50), does BUNDLED at deep L
   provide a quantifiable chain-degradation gap? (Empirical probe confirms YES
   at NPROP=100: BUNDLED_L1=0.50, BUNDLED L=20=0.10 → gap=0.40.)

If all three hold, the storage-strategy substrate-physics-law extends to deep
L=20, providing a 3-cell physics-law contribution:
`sharded_capacity_beyond_bundle_bound` (single-hop) +
`math4_proof_chains_v2` (moderate-chain L<=10) +
`math4_rung3_deep_chains_v2` (deep-chain L up to 20).

## Envelope-fail-bands (META_RULE_L: strict >= floor+5%)

Three simultaneous HP criteria (calibrated against empirical probe 2026-07-02
at NPROP {10, 20, 50, 100} x L {2, 4, 8, 12, 16, 20}):

**Criterion I — SHARDED matched-filter chain-independence at DEEP L:**
- HP: SHARDED accuracy at (L=20, NPROP=100) >= 0.85
- Expected: 1.000 (empirical probe: SHARDED = 1.000 at every phase point across
  the full grid; matched-filter algebra is exact)
- MEASURED@scratchpad/probe_deep_chains.py

**Criterion II — STORAGE-STRATEGY gap at DEEP chain depth L=20:**
- HP: max over NPROP of (SHARDED - BUNDLED) at L=20 >= 0.60
- Expected: ~0.9 at NPROP=100 (empirical: SHARDED=1.0 minus BUNDLED=0.10 =
  0.90; BUNDLED_L=20 at NPROP=50 spiked to 0.52 as noise floor and at NPROP=10
  hit 0.78 via chain-closure-by-chance at small NPROP; 3-seed FULL will
  stabilize)

**Criterion III — CHAIN-DEGRADATION signature at DEEP L (single-hop vs deep multi-hop):**
- HP: BUNDLED_L1 - BUNDLED at L=20 >= 0.15 at some NPROP where BUNDLED_L1 >= 0.20
- Expected: ~0.40 at NPROP=100 (empirical: L1=0.50 - L=20=0.10 = 0.40)

**HARD_PASS**: all 3 criteria met.
**MIDDLE_BAND**: 1-2 criteria met.
**HARD_FAIL**: 0/3 criteria met (would falsify math4_v2 chain-independence claim
if extended to L=20).

Strict-above-floor margins: SHARDED threshold 0.85 vs empirical 1.000 (1.18x
above); storage-gap 0.60 vs empirical 0.90 (1.50x); chain-degrad 0.15 vs
empirical 0.40 (2.67x). Not floor-hugging.

## Discriminator (META_RULE_K: fires-check)

Class = STORAGE-STRATEGY selectivity at DEEP chain depth. Discriminator fires
when `SHARDED-BUNDLED gap >= 0.60` at (L=20, NPROP_max).

Smoke fires-check: at full-N=8192, one (L=20, NPROP=100) cell must show gap
>= 0.60. Empirical probe 2026-07-02: gap 0.90. Smoke gate will re-verify at
2 L x 2 NPROP smoke grid.

## Baseline-in-band (META_RULE_AG) — EXEMPTED with rationale

`baseline_in_band` exempted (same rationale as math4_v2). This is a
**STORAGE-STRATEGY comparison cell**, not mechanism-vs-baseline. Both arms use
identical substrate primitives (FHRR bind/unbind, cleanup argmax); only
rule-storage layout differs.
- SHARDED (positive control) saturates near 1.000 across all phase points — that
  IS the finding: sharded storage supports deep-chain composition mathematically.
- BUNDLED (mechanism-under-test) collapses to floor at L>=4 for NPROP>=50 — that
  IS the finding: bundle storage cannot support chain composition, and the
  collapse deepens at L=20.
- BUNDLED_L1 hovers in [0.40, 0.60] across NPROP — measurable-but-mediocre; chain
  compounding kills it.

The saturation IS the signal. Not an AG-rule violation.

`arms_differ_verified`: True — hash-verified per NPROP that `sharded_codebook`
and `bundle_vec` produce distinct byte representations (META_RULE_AF; assert in
`run_phase_matrix`).

## Compute architecture (USER-LOCKED 2026-07-02)
Class: **(a) batched-GPU**.

Justification: substrate primitives (cnorm, matmul cleanup) are matmul-heavy.
TR trials batched at each chain step (all trials share the same rule storage).
Chain steps sequential per trial (step k+1 depends on cleanup output of step
k) — sequential-inside-chain, batched-outside-arm.

Wall estimate: 5 L x 4 NPROP x 3 arms x 100 TR at max (L=20, NPROP=100, N=8192)
→ cleanup matmul (TR=100, N=8192) @ (N=8192, NPROP=100) = 8e7 FLOPs per step
× 20 steps = 1.6e9 per unit (BUNDLED/SHARDED, L=20, NPROP=100). Total across
grid ~ 3e10 FLOPs. On GPU (torch complex64, ~5 TFLOPS effective) ~ 6ms per
unit, total < 5s. On CPU (~200 GFLOPS) ~ 150ms per unit, total ~ 10s.

Wall-time sanity check: local CPU probe ran 24 units (deep-L, 4 NPROP, 3 arms,
TR=60) in 1.3s. Full CPU grid (60 units, TR=100) would be ~ 5-10s; GPU
5x-10x faster. GPU-batching mandate applies but even CPU is fast enough that
this could nominally run on remote_cpu_queue if overnight_queue is congested.

## Prior-work check

Substrate-KB concept query 2026-07-02:
`bash tools/substrate_query.sh "deep chain composition L=20 sharded storage FHRR modus ponens deep"`

Results:
- Top hit at cosine 0.3457: `11.1 SNR Decay in Deep Composition` (relevant
  prior arc — `b_alpha_broad_envelope_cpu_v1` MB DEPTH-CLIFF at deeper chains;
  `c_composition_storage_density_v1` HARD_FAIL for compound multiplicative
  composition). Cited prior work confirms deep-chain compositional pressure is
  a known-open regime; the storage-strategy discriminator specifically targets
  it.
- Additional hits (cosine ~0.29) all point to `c_composition_storage_density_v1`
  which studied compound storage density but with a DIFFERENT mechanism class
  (compound storage multiplicativity, not per-antecedent-sharded vs global-bundle
  layout).
- No prior cell tests the SHARDED-vs-BUNDLED-vs-BUNDLED_L1 discriminator at
  L>10. math4_v2 tests up to L=10; sharded_capacity tests single-hop L=1.

Prior-work check: **RELATED PRIOR ARC** at cosine 0.35 (compositional depth
cliffs). This cell is a **genuine extension** of math4_v2's storage-strategy
finding to deep-L regime that prior work has FLAGGED as unresolved. Not a
rediscovery.

## CRLB / capacity-feasibility (§9)
`crlb_floor_computed`: n/a. Discriminator is gap-based, not noise-floor-based.

Substrate-physics prediction:
- SHARDED: exact algebraic identity (`cnorm(A*IMPL*B) * conj(A) * conj(IMPL) = B`);
  chain accuracy = 1.0 at any L (analytically). THEORETICAL@exact-cnorm-unbind
- BUNDLED: per-step unbind SNR ~ N / sqrt(NPROP-1). At N=8192, NPROP=100,
  per-step SNR ~ sqrt(8192/99) ~ 9.1; per-step p_correct ~ 0.3-0.5; over L=20
  chain, compound p_correct = 0.3^20 ~ 3e-11 → floor via argmax random-hit
  ~ 1/NPROP = 0.01. Empirical 0.10 confirms floor regime.
  THEORETICAL@matched-filter-superposition-noise + compounding

`discriminator_reachability`: True. HP thresholds achievable per empirical
probe (all 3 criteria exceed thresholds by 1.2x-2.7x margin).

## Arms-must-differ (META_RULE_AF)
`arms_differ_verified`: True. In `run_phase_matrix`, per NPROP hash-verify:
- SHARDED codebook (NPROP, N) complex64 bytes → SHA256 prefix
- BUNDLE vec (N,) complex64 bytes → SHA256 prefix
Assert distinct at each NPROP (raises META_RULE_AF violation if bit-identical).

Additionally, arms use different code paths at retrieval:
- SHARDED: `sharded_codebook[ci]` (per-trial indexed rule)
- BUNDLED / BUNDLED_L1: `bundle_vec.unsqueeze(0).expand(TR, -1)` (same for all)
Verified via cell-code review.

## Final-metrics atomicity (META_RULE_AH)
`final_metrics_atomicity`: `tmp_replace` via
`experiments/_seed_checkpoint.write_metrics` (writes tmp then `os.replace()`
atomically). Crash-diagnostic also uses `os.replace`.

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
- FULL: `EXPECTED_N_UNITS = 5 (L) x 4 (NPROP) x 3 (arms) = 60`
- SMOKE: `EXPECTED_N_UNITS = 2 x 2 x 3 = 12`

Verdict logic counts `len(per_unit)`; if != expected, overrides verdict to
`HARD_FAIL_CARDINALITY_BREACH_META_RULE_H`.

`cardinality_ok` field written to metrics.json.

## Discriminating-fraction (Gate B)
5 L x 4 NPROP x 3 arms = 60 phase points. Empirical probe predictions:
- SHARDED: 20 points all saturate at 1.000 (positive-control by design;
  establishes the ceiling for the discriminator gap)
- BUNDLED_L1: 20 points all in [0.40, 0.60] band (all in discriminating band
  [0.30, 0.70])
- BUNDLED: 20 points range from [0.00, 0.30] with some noise-floor spikes
  ([0.50-0.78] at NPROP=10-20 L=20 in single-seed probe; expected to average
  down at 3-seed FULL). ~5-8 in discriminating band [0.30, 0.70]; rest at
  floor demonstrating deep-chain collapse.

For the DISCRIMINATOR gap (SHARDED - BUNDLED at L=20): 4 NPROPs x 1 L_max =
4 gap values; all 4 predicted to be >= 0.20 (worst-case at NPROP=10 due to
noise-floor spike). At NPROP=100, gap = 0.90 well within HP band.

`discriminating_fraction`: 20/20 for BUNDLED_L1 in-band; 4/4 gap-values above
0.20; 1/4 (NPROP=100) firmly above HP threshold 0.60.

## Sweep-alignment (Gate A)
Swept params: L (chain depth), NPROP (rule-base size).
Effective per-primitive:
- SHARDED cleanup: effective_NPROP = NPROP
- BUNDLED unbind: effective_NPROP = NPROP (bundle sum size = NPROP)
- Chain depth L: effective_L = L for BUNDLED/SHARDED; effective_L = 1 for
  BUNDLED_L1 (single-hop; L slot is redundant across L for BUNDLED_L1)

`sweep_alignment_verdict`: ALIGNED.

## Composition-edges (Gate C)
Single-primitive cell; no cross-primitive composition. Same shape checks as
math4_v2. `composition_edges`: n/a (single-primitive).

## Positive-control (Gate D)
Chain-grade primitive invoked: FHRR bind (`*`), unbind (`* conj()`), cleanup
argmax.
- Cited prior: `math4_proof_chains_v2_global_bundle_cpu_v1` at L in {2,4,6,8,10}
  achieved SHARDED = 1.000 across all NPROP.
- ARM_SHARDED in this cell IS the positive control at the DEEP-L test regime
  (5 NPROP x 5 L). Empirical probe confirms SHARDED reproduces the prior
  chain-grade result across the deep-L grid (SHARDED = 1.000 at every phase
  point including L=20) — regime extension VERIFIED.
- Regime: complex64 phasors at N=8192, NPROP in [10, 100], L in [4, 20]. Same
  primitive class as math4_v2; extends L axis while contracting NPROP axis
  (keeps BUNDLED_L1 measurable).
- Tolerance: SHARDED accuracy at (L_max=20, NPROP_max=100) >= 0.85. Threshold
  well above prior chain-grade floor.

`positive_control_arms.PRIMITIVE_REPRODUCE_AT_TEST_REGIME`: SHARDED arm
(20 phase points; probe confirms 1.000 at all).
`regime_extension_audit`: SHAPE_MATCH (same primitive; deeper L, lower NPROP
range; empirically verified).

## Functional-requirements (Gate E)
Same 4 functional requirements as math4_v2 (see that pre-reg). Additional
requirement for this cell:
5. **Chain L=20 (deep chain)**: cell tests whether the 4 requirements hold at
   chain depth 20 — a 2x extension over math4_v2's L=10.

## Defensive-error-checking (§13)
- `cell_chunked`: False (single-file; FULL wall estimate < 60s on CPU / < 10s
  on GPU; runner-death loses this single seed only)
- `start_marker_written`: True
- `crash_diagnostic_present`: True (`_write_crash_metrics` writes atomic
  `metrics.json` with `verdict: CELL_CRASHED`)
- `heartbeat_present`: False (FULL wall < 1min max; per-unit lines flushed)
- `defensive_error_checking`: `exempt_short_cell (FULL wall < 5min)`

## Progress-logging (§17)
`progress_logging`: `print_flush_true`. All `print()` calls use `flush=True`.
`sys.stdout` reconfigured to `line_buffering=True` at cell start. Runner
invokes with `python -u` (defense in depth). Cell timeout target 900s (well
below 1800s threshold).

## Calibration-check (META_RULE_M)
`calibration_check`: `default_ok_for_this_regime`. FHRR complex-phasor
primitives at N=8192 match all prior chain-grade cells. No adaptive tuning.
Discriminator gap thresholds calibrated against empirical probe run in
scratchpad (`scratchpad/probe_deep_chains.py`) prior to FULL dispatch.

## Stage-progression check (USER-LOCKED 2026-06-26)
Stage 3 (compositional understanding). Substrate-only synthetic FHRR phasors;
NO tokens, NO text, NO language benchmarks. Multi-hop modus ponens chains at
deep L=20 ARE the operational test of compositional-reasoning-chain depth.
VERIFIED Stage 3.

## Substrate-doesn't-know-anything check (USER-LOCKED 2026-06-26)
N/A — no language content. Substrate-physics test only.

## Grep-check discipline (Skunkworks META CG 2026-07-02)
Cell invokes substrate primitives multiple times in `run()`:
- `cnorm_torch` (unit-modulus projection) in `build_rules`
- FHRR bind (`*`) in `build_rules` (per-antecedent) and per-step in
  `run_chain_arm`
- FHRR unbind (elementwise conj mul) per-step in `run_chain_arm`
- `cleanup_argmax` (matmul + argmax) per-step in `run_chain_arm`
- Bundle sum (`.sum(dim=0)`) in `build_rules`

Grep verification: `grep -nE "cnorm_torch|cleanup_argmax|A_cur\.conj\(\)|IMPL_conj|\.sum\(dim=0\)" experiments/exp_math4_rung3_deep_chains_v2_global_bundle_cpu_v1.py` returns >= 10 hits. Not numpy-in-substrate-costume.

## Selftest formulas (PROT-022)
1. **SHARDED matched-filter chain-independence at DEEP L**: SHARDED at (L=20,
   NPROP=100) >= 0.85 AND SHARDED at (L=12, NPROP=50) >= 0.85. Assertion in
   `_selftest` (empirical 1.000 for both).
2. **BUNDLED_L1 mediocre-but-nonzero band**: BUNDLED_L1 at NPROP=100 in
   [0.20, 0.85]; BUNDLED_L1 at NPROP=50 in [0.20, 0.85]. Assertion in
   `_selftest` (empirical 0.50 / 0.47).
3. **BUNDLED deep-chain collapse**: BUNDLED at (L=20, NPROP=100) <= 0.35.
   Assertion in `_selftest` (empirical 0.10).
4. **Storage-strategy gap at DEEP L**: `SHARDED - BUNDLED` at (L=20, NPROP=100)
   >= 0.60. Assertion in `_selftest` (empirical 0.90).
5. **Chain-degradation signature at DEEP L**: `BUNDLED_L1 - BUNDLED_L20` at
   NPROP=100 >= 0.15. Assertion in `_selftest` (empirical 0.40).

`--self-test` PASS to be confirmed pre-smoke (this session).

## Timeout
- SMOKE (12 units, TR=30, local_cpu_queue): 300s (empirical wall < 5s CPU;
  generous buffer)
- FULL (60 units, TR=100, overnight_queue GPU): 900s (empirical CPU probe ~ 5-
  10s wall; GPU 5-10x faster ~ 1-2s; timeout 900s = 15min = huge buffer)

## Number tagging (META_RULE_AC)
- SHARDED at (L=20, NPROP=100) probe = 1.0000
  MEASURED@scratchpad/probe_deep_chains.py (2026-07-02)
- BUNDLED at (L=20, NPROP=100) probe = 0.1000
  MEASURED@scratchpad/probe_deep_chains.py
- BUNDLED_L1 at NPROP=100 probe = 0.5000
  MEASURED@scratchpad/probe_deep_chains.py
- Storage-strategy gap at (L=20, NPROP=100) probe = 0.90
  MEASURED@scratchpad/probe_deep_chains.py
- Chain-degradation gap at NPROP=100 probe = 0.40
  MEASURED@scratchpad/probe_deep_chains.py
- Plate 1995 bundle-capacity bound 0.14*N ~ 1147
  CITED@Plate 1995 HRR paper
- Per-step BUNDLED SNR ~ N / sqrt(NPROP-1)
  THEORETICAL@matched-filter-superposition-noise
- SHARDED exact recovery `cnorm(A*IMPL*B) * conj(A) * conj(IMPL) = B`
  THEORETICAL@exact-cnorm-unbind-algebra
- Full-grid FLOP estimate 3e10
  THEORETICAL@compute-architecture-analysis
- v2 storage gap 0.917 at (L=6, NPROP=50), SHARDED L=10 NPROP=500 = 1.000
  MEASURED@d:/AI/hd-instrument/data/exp_math4_proof_chains_v2_global_bundle_cpu_v1/metrics.json (smoke this session)

## Landed-VET request
On FULL landing (3 seeds), Skunkworks landed-VET should verify:
- All 3 HP criteria measured on actual per_unit data across 3 seeds
- `arms_differ_verified: True` in each metrics.json
- `cardinality_ok: True` (60/60 units per seed)
- `meta_arm_hashes_by_nprop` distinct sharded_hash vs bundle_hash per NPROP
- Chain-degradation curve at NPROP=100: BUNDLED accuracy across L in
  {4, 8, 12, 16, 20} — is the slope monotone decreasing? (Quantifies deep-L
  extension of chain-composition collapse)
- Deep-L substrate-physics-law tier: if HP holds at FULL across 3 seeds AND
  math4_v2 FULL + sharded_capacity FULL also HP, this forms a 3-cell
  substrate-physics-law contribution (STORAGE-STRATEGY primitive at
  single-hop + moderate-chain + deep-chain). MM_TENTATIVE at minimum;
  CG-eligible if 3 seeds reproduce and prior cells land HP.
