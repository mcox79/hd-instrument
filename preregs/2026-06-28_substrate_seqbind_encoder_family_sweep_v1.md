# Prereg: substrate_seqbind_encoder_family_sweep_v1

**Date:** 2026-06-28
**Author:** exp_dev (Opus 4.7 1M, agent-spawn) component-substitution phase-diagram
**Drill source:** Research directive 2026-06-28 — second systematic component-substitution sweep (encoder family for sequence binding K-cliff). Sibling to in-flight pattern-completion encoder sweep (a49b7c) on a different primitive.
**Stage:** Stage 1 (substrate primitive characterization — component-substitution phase coverage of sequence-binding K-cliff)
**P_deflated:** 0.55 (Kanerva-family encoder differences well-characterized in isolation; novel = systematic head-to-head on identical K x N grid for sequence binding specifically, with arms-must-differ-across-encoders hash gate)
**Phase-diagram axis:** outer = ENCODER_FAMILY; inner = K (sequence length) x N (dimensionality)

## SUBSTRATE-AS-CANONICAL prior work

- `exp_substrate_sequence_binding_v1` atom: K=20 cert-grade HRR sequence binding single point.
- `exp_substrate_sequence_binding_K_cliff_phase_diagram_full_v2_seed_{7,13,19}` (2026-06-28): full-sweep MID->HIGH coverage for **HRR alone**; K x N x Q phase diagram; landed in flight.
- Prior session 2026-06-23: "sparse-bipolar 20-300x bundle lift" surfaced; not deployed systematically for sequence binding.
- Plate 1995 (HRR), Plate 2003 (FHRR), Kanerva 2009 (SDM), MAP architectures.

## COMPONENT-SUBSTITUTION SCOPE (load-bearing)

The "phase diagram" axis being filled is **COMPONENT** (encoder family), not just config parameter within a fixed mechanism. This complements:
- The v2 K-cliff phase diagram (vary K, N, Q **within HRR**) → characterizes HRR's regime.
- This v1 sweep (vary encoder family at modest K x N grid) → characterizes **which encoder dominates which regime**.

Result is a 2D matrix: which (encoder, K, N) combinations satisfy mechanism vs. fail. Reveals if HRR is uniformly best, or if FHRR / sparse / binary dominates at specific scales.

## ENCODER FAMILIES (4)

1. **HRR** (real bipolar + FFT circular convolution; Plate 1995)
   - Codebook: V x N float32 +/-1 (no L2 norm; classic Plate)
   - Bind: FFT(p) * FFT(item+noise), then IFFT; sum-bundle
   - Unbind: FFT(c) * conj(FFT(query)), then IFFT
   - K_cap_theory(N) = N / (4 * log2(N))
   - At N=4096: K_cap ≈ 85; at N=1024: K_cap ≈ 26
2. **FHRR** (complex64 unit-magnitude phasors + elementwise complex mul; Plate 2003)
   - Codebook: V x N complex64 with each component e^{i*phi}, phi ~ U[0, 2pi)
   - Bind: elementwise complex mul; phase-noise = e^{i * Gaussian * 0.1}
   - Unbind: c * conj(query) elementwise
   - Cleanup: cosine of real part of normalized complex inner product
   - K_cap_theory(N) = N / 2 (higher capacity than HRR)
   - At N=4096: K_cap ≈ 2048
3. **SPARSE** (sparse bipolar +/-1 with density=0.02, MAP-style elementwise bind)
   - Codebook: V x N float32; 2% nonzero per row, +/-1 at nonzero
   - Bind: positions * items elementwise (MAP-style); sum-bundle
   - Unbind: c * query elementwise
   - K_cap_theory(N) = (density * N) / (4 * log2(N))
   - At N=4096: K_cap ≈ 1.7 (sparse capacity scales DOWN with density at same N)
   - At N=8192: K_cap ≈ 5.0
4. **BIN** (dense binary bipolar +/-1, elementwise mul; XOR-equivalent)
   - Codebook: V x N float32 +/-1
   - Bind: positions * items elementwise (no convolution / no shift)
   - Unbind: c * query elementwise
   - K_cap_theory(N) = N / (4 * log2(N)) (similar to HRR but no shift structure)
   - At N=4096: K_cap ≈ 85
   - NOTE: BIN's positional binding is NOT shift-based (positions are independent random vectors). Capacity ≈ HRR but the geometric structure differs.

## SWEEP AXES (LOCKED)

- **Encoder ∈ {HRR, FHRR, SPARSE, BIN}** — 4 families (outer COMPONENT axis)
- **K ∈ {10, 20, 50, 100, 200, 500}** — 6 sequence lengths
- **N ∈ {1024, 4096, 8192}** — 3 dimensionalities
- **Q noise level fixed at 1** (effective tag_density = 0.1) — keep grid tractable; varying noise is the v2 cell's job
- **= 4 × 6 × 3 = 72 phase points per seed**

## ARMS (3) — per phase-point, per encoder

1. **SUBSTRATE** — the encoder's native bind+bundle+unbind+cleanup pipeline. **The mechanism.**
2. **SHUFFLE** — same bundle S; query position SHUFFLED (broken pos→item map). **Order-matters baseline.** Re-rolls coincidences with true position (up to 50 retries).
3. **RANDOM** — encoder-native random vector independent of S; cosine vs item codebook. **Vector-floor baseline.**

**arms-must-differ at each phase point:** SUBSTRATE > max(RANDOM, SHUFFLE) by > 0.20 (mean across pts) at HARD_PASS bands. If avg_arms_diff < 0.05 → HARD_FAIL.

**META_RULE_AF encoder-arms-differ-across:** Each of 4 encoders produces a distinct SHA256 hash of its (K, N, SUBSTRATE_top1_recall) tuple sequence. Hash collision → HARD_FAIL `ENCODER_HASHES_NOT_DISTINCT_X_of_4`. Catches the "all encoders quietly run the same code" failure mode.

## PRE-REG BANDS (LOCKED; PROSPECTIVE; metric = mean top1_recall in [0,1])

- **recall ≥ 0.90** → **SAT** (saturated; encoder trivially solves at this K x N)
- **recall ∈ [0.30, 0.70]** → **MIDDLE_BAND** (discriminating regime; encoder's K-cliff zone)
- **recall ≤ 0.10** → **FLOOR** (cliff past; encoder fails at this K x N)
- recall ∈ (0.10, 0.30) ∪ (0.70, 0.90) → **TRANSITION** (informational)

**HARD_PASS** (chain-grade component-sweep HIGH coverage):
- `n_MB >= 22` of 72 phase points (≥30% in discriminating regime)
- `avg_arms_diff >= 0.20` (mechanism load-bearing across grid)
- `n_SAT >= 6` (at least one encoder works at low load)
- `n_FLOOR >= 6` (cliff observable for at least one encoder)
- `encoder_arms_differ == True` (all 4 encoder hashes distinct — META_RULE_AF)
- `cardinality_ok` (observed == 72)
- positive control: HRR at (K=20, N=4096) reproduces v2's recall ~ 1.000 (asserted in selftest; gates dispatch)

**MIDDLE_BAND**:
- `n_MB >= 10` (partial discriminating coverage)
- OR HARD_PASS gates partially met

**HARD_FAIL** (any of):
- `all_saturated` (every point ≥ 0.90; by-construction failure — grid doesn't reach cliff)
- `all_floored` (every point ≤ 0.10; no signal — all encoders broken)
- `arms_identical` (SUBSTRATE == RANDOM at all points; code bug)
- `encoder_arms_differ == False` (some encoders byte-identical; code bug)
- `avg_arms_diff < 0.05` (mechanism not load-bearing across the grid)

## DISCRIMINATING_FRACTION PREDICTION (per encoder)

Predicted band distribution per encoder (based on K_cap_theory):

| Encoder | N=1024 K_cap | N=4096 K_cap | N=8192 K_cap | Expected SAT pts | Expected MB pts | Expected FLOOR pts |
|---------|-------------:|-------------:|-------------:|-----------------:|-----------------:|-------------------:|
| HRR    | 26  | 85   | 153  | 3-5  | 5-7  | 4-6  |
| FHRR   | 512 | 2048 | 4096 | 12-14 | 2-4 | 0-2  |
| SPARSE | 0.4 | 1.7  | 5.0  | 0-2  | 1-3  | 13-16 |
| BIN    | 26  | 85   | 153  | 3-5  | 5-7  | 4-6  |

Aggregate predicted discriminating_fraction = (5+3+2+6)/72 ≈ 22% MB; close to HP boundary. Likely outcome = MIDDLE_BAND-to-HARD_PASS depending on smoke result.

## FAIRNESS GATES (META_RULE_AC/AE/AF)

- Identical (K, N) grid across all 4 encoders.
- Same seed RNG for sampling pos_idx + item_idx per phase point per encoder.
- Each encoder uses its OWN encoder-native codebook (HRR/BIN: bipolar; FHRR: complex phasor; SPARSE: density-0.02).
- Tag noise scale matched (effective tag_density=0.1 across all encoders).
- All 3 arms within a (encoder, K, N) point see SAME (pos, item) sampling.
- SHUFFLE re-rolls coincidences with true position (up to 50 retries) per encoder.
- META_RULE_AF: enc_hash(encoder) = SHA256((K, N, SUBSTRATE_top1_recall)_sorted)[:16]; all 4 distinct REQUIRED.

## CARDINALITY (META_RULE_H_ANCHOR)

- **EXPECTED_N_PHASE_POINTS_FULL per seed** = 4 enc × 6 K × 3 N = **72 points per seed**
- **EXPECTED_N_RECORDS_FULL per seed** = 72 × 3 arms × 50 queries = **10800 records per seed**
- **EXPECTED_N_PHASE_POINTS_SMOKE per seed** = **6 corners**
- **EXPECTED_N_RECORDS_SMOKE per seed** = 6 × 3 × 4 = **72 records per seed**
- **EXPECTED_N_SEEDS** = 3 chunked siblings (7, 13, 19)

CARDINALITY_OK declared in metrics: `observed_n_phase_points == 72` AND `observed_n_records == 10800` per sibling.

**HARD_FAIL_CARDINALITY_BREACH** if observed < expected.

## DISCRIMINATOR-SURVIVES-SCALE (USER 2026-06-26 + Fix #14)

Selftest gates (validated 2026-06-28; HARD_PASS):
- HRR (K=20, N=4096) positive control: SUBSTRATE=1.000 at n_q=4 (matches v2 expectation)
- HRR (K=500, N=1024) FLOOR check: SUBSTRATE=0.000 at n_q=4 (cliff observable)
- arms_diff at SAT corner = 1.000 (massive separation)

Smoke 6-corner gate (validated below).

## HARDENING

L1 STARTED early-write + L2 per-seed progress + L3 outer try/except + L4 import-crash sentinel + atomic per-seed partial via `experiments._seed_checkpoint`. PROT-021 anchor + run_mode stamping on every partial. META_RULE_X main-guard.

## DISPATCH

- **Local CPU** (numpy primary; matches v2 cell's local_cpu_queue pattern)
- Estimated smoke wall: ~5s observed
- Estimated full wall per seed: ~30-90s (HRR=~5s, FHRR=~10s due to complex64 N=8192 K=500, SPARSE=~5s, BIN=~5s; sum ~30-50s total; safety margin 2x)
- Per-sibling timeout: **600s** (10 min; ~10x projected; well below ceiling)
- 3 chunked seed siblings → local_cpu_queue (one at a time; serialized by local runner)

**No PROT-019 large-N anchor enforcement applies** — anchor lacks `_n<N>` suffix.

## CHUNKED ARCHITECTURE (USER 2026-06-28)

3 sibling files (one seed each):
- `exp_substrate_seqbind_encoder_family_sweep_v1_seed_7.py`
- `exp_substrate_seqbind_encoder_family_sweep_v1_seed_13.py`
- `exp_substrate_seqbind_encoder_family_sweep_v1_seed_19.py`

Shared core: `experiments/_substrate_seqbind_encoder_family_sweep_v1_core.py`
Resumability: `experiments/_seed_checkpoint.py` (PROT-021 anchor stamping).

**Aggregation post-hoc:** combine 3 sibling metrics.json → per-encoder K_cliff matrix; cross-seed agreement check on cliff locations within each encoder.

## FUNCTIONAL REQUIREMENTS (composition edges)

- HRR / BIN: bipolar codebook → bind (FFT-conv or Hadamard) → bundle (sum) → unbind → cleanup (cosine vs item codebook)
- FHRR: complex phasor codebook → bind (complex mul) → bundle (sum + magnitude normalize) → unbind (mul-conjugate) → cleanup (real-part cosine vs item codebook)
- SPARSE: sparse bipolar codebook → bind (elementwise mul) → bundle (sum) → unbind (elementwise mul) → cleanup (cosine vs item codebook)
- SHAPE_MATCH: per encoder, all intermediate tensor shapes are (K, N), (N,), (Q, N), (Q, V_items) compatible.

## SWEEP_ALIGNMENT_VERDICT

**ALIGNED.** All 4 encoders run on identical (K x N) grid with identical query sampling per (encoder, K, N) point. No per-encoder grid drift.

## PHASE-DIAGRAM DECISION TABLE

| Outcome | Phase-diagram verdict |
|---------|----------------------|
| HARD_PASS — >= 22 MB pts + SAT/FLOOR present + arms differ + encoder hashes distinct | Encoder-family component sweep for sequence binding promoted; identifies regime-dominant encoders |
| MIDDLE_BAND — 10-21 MB pts | Partial component coverage; needs finer grid or extra encoder family |
| HARD_FAIL — saturated / floored / hashes collision | Re-author with broader K x N envelope or fix encoder code bug |

## CROSS-SEED AGREEMENT CHECK (post-hoc, expected, not pre-reg'd as gate)

If 3 seeds agree on K_cliff location per (encoder, N) within ±1 K-grid-step, that's cross-seed cliff localization — strong signal. Reported in aggregated verdict; not a HARD_PASS gate (single-seed HARD_PASS already promotes coverage).

## EXPECTED REGIME-DOMINANT FINDINGS (HONEST PRIORS)

- FHRR likely dominates HIGH-K regime (K=100-500 at N=4096-8192) due to N/2 capacity.
- HRR / BIN should be similar in low-K (K<=50) regime; sequence-binding-via-Hadamard may surprise vs sequence-binding-via-conv.
- SPARSE should mostly FLOOR at the K levels probed (its capacity ~1-5 even at high N due to density=0.02). If SPARSE shows surprising HIGH-K recall — that's the "bundle lift" claim from prior session deserving deeper investigation.

If smoke shows: (a) one encoder dominating all bands → flag for v2 with stratified bands; (b) all encoders identical → code bug, FAIL; (c) SPARSE unexpectedly competitive at K>=100 → flag as positive lit-novelty.

## NOTES

- This cell EXTENDS sequence_binding_v1 (K=20 HRR cert anchor) to a COMPONENT phase diagram of 4 encoder families × 18 (K,N) points each.
- This is a Stage 1 (substrate-primitive characterization) cell, NOT Stage 3 composition or Stage 4 LM equivalence.
- Per USER 2026-06-27 substrate-as-canonical: builds on cert atom from `exp_substrate_sequence_binding_v1`; corroborates / extends v2 K-cliff sweep finding by varying the substituted COMPONENT.
- Per USER 2026-06-28 chunked architecture: 3 sibling files mirroring `substrate_sequence_binding_K_cliff_phase_diagram_full_v2` pattern.
- Per USER 2026-06-26 stage-progression: Stage 1 component-coverage phase diagram is exactly the right work — characterizes a load-bearing lever (encoder family) before composing into higher-stage cells.
- Independence: encoder-family PC sweep (a49b7c) in flight on different primitive (pattern completion); no shared cell files; no file collision.
