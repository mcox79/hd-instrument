# Pre-registration: substrate_order_binding_family_v2 (interference-resilience revival)

**Date:** 2026-07-01
**Author:** exp_dev (Opus 4.7 1M, agent-spawn)
**Trigger:** Research Axis J revival drill (`notes/research_axis_J_revival_drill_2026-07-01.md`) candidate #1 — interference-resilience under multi-sequence load (P=0.55, 5x-drill-eligible, 3-domain support).

## v1 -> v2 pivot rationale

v1 (K-boundary sweep at single-sequence load) landed HARD_FAIL because the K*-boundary metric collapsed all 3 ops at K*=500 despite a real 3.5x top1 spread visible in the K=2000 FLOOR band:

- seed_13 K=2000: CYCLIC=0.04, PERM=0.08, PHASE=0.14 MEASURED@data/exp_substrate_order_binding_family_v1_seed_13/metrics.json:phase_map[*].top1_substrate
- seed_19 K=2000: CYCLIC=0.04, PERM=0.06, PHASE=0.18 MEASURED@data/exp_substrate_order_binding_family_v1_seed_19/metrics.json:phase_map[*].top1_substrate

v2 replaces the K*-boundary discriminator with **interference-resilience under multi-sequence load** — a discriminator the drill flagged as CG-eligible (3-domain support: VSA cross-talk theory + Cowan WM chunking + compressed-sensing basis-universality).

## Anchor

`substrate_order_binding_family_v2_seed_{7,13,19}` (chunked-per-seed per canonical §13). This filing covers seed_7 only; sibling seeds spawn IFF smoke_7 fires the discriminator.

Shared core: `experiments/_substrate_order_binding_family_v2_core.py`.

## Routing

- **Smoke queue:** local laptop CPU (.venv/Scripts/python.exe direct invocation). Full grid = smoke grid (18 pts/seed).
- **Full queue:** `remote_cpu_queue` (CPU-eligible; pure numpy). Not matmul-heavy at N=8192, V=4000, total_units<=1000 per bundle.
- **Push constraint:** harness-DENIED push from exp_dev. Full dispatch routes through Orchestrator via completion report post-smoke.
- **Timeout estimate:** 1800s per seed (18 pts x conservative 60s/pt = 1080s; 1.5x pad = 1620; round to 1800).

## Functional requirements (per canonical §15 gate E)

1. Encode L>=1 disjoint sequences into a shared bundle -> handled by _bundle_hadamard summed across per-sequence Hadamard products (each sequence has independent codebook seed slice).
2. Query (sequence_id, position) -> item -> handled by _unbind_hadamard with sequence-l's position vector and cleanup against sequence-l's item codebook.
3. Measure interference degradation per op -> handled by top1_substrate vs L axis; DISCRIMINATOR at (L=4, K=250).
4. Preserve 3-op distinctness (guard PHASE_ROTATION aliasing to CYCLIC_SHIFT at commensurate theta) -> handled by pair-distinctness gate on bundle_hash AND positions_hash (both required).

## Order-binding operations (3 ARMs, same as v1)

| Arm | Encoder family | Position encoding | Item bind + bundle | Unbind |
|---|---|---|---|---|
| `CYCLIC_SHIFT` (v1 CG baseline) | bipolar | P_k = roll(P_0, k) | Hadamard sum_k p_k * i_k | bundle * q_pos |
| `RANDOM_PERMUTATION` | bipolar | P_k = perm^k(P_0), perm fixed random | (same Hadamard) | (same Hadamard) |
| `PHASE_ROTATION` | HRR-real | P_k = ifft(fft(P_0) * exp(1j*k*theta*freqs)); theta=2*pi*0.618/N | (same Hadamard) | (same Hadamard) |

## Sweep axes (LOCKED)

- **N_DIM:** 8192 (fixed; matches v1 regime for regime-continuity)
- **L (load axis):** {1, 2, 4} — 1 = single sequence (v1 regime; positive control); 2 = mild interference; 4 = discriminator regime
- **K_per_seq:** {125, 250} — moderate per-seq load; total load L*K in {125, 250, 500, 1000}
- **Seeds:** {7, 13, 19} (seed_7 dispatched first; siblings gated on smoke pass)
- **n_queries per phase point:** 60 FULL / 8 SMOKE
- **V_ITEMS:** 4000 (>= max total load 1000 x 4 slack)
- **V_POS:** 4000

## Cardinality (META_RULE_H)

- **FULL per seed:** 3 ops x 3 L x 2 K = **18 phase points**
- **SMOKE per seed:** 3 ops x 3 L x 2 K = **18 phase points** (full grid at smoke; small enough)
- `cardinality_ok` field set true iff observed_n_units == expected_n_units == 18.

## Bands (LOCKED per META_RULE_L)

Per-(op, L, K) `top1_substrate` recall:

- **SAT band:** `top1 >= 0.90` — op is above cliff at this (L, K)
- **MB band:** `0.30 <= top1 <= 0.70` — on cliff
- **FLOOR band:** `top1 <= 0.10` — below cliff
- **TRANSITION:** rest
- **SUSPECT_SATURATION:** `top1 >= 0.9995` flagged per META_RULE_Q

## CRLB / capacity-feasibility (THEORETICAL@Var(unbind_noise)~L*K/N)

For any order-binding preserving code-independence, total bundle carries L*K bind pairs:
`Var(unbind_noise) ~ L*K/N`; `SNR ~ sqrt(N/(L*K))`.
Top1 cleanup over V_ITEMS via dot-product argmax.

| L | K | K_tot | K/N | SNR | Predicted top1 (well-preserved op) | Predicted band |
|---|---|---|---|---|---|---|
| 1 | 125 | 125 | 0.015 | 8.10 | ~1.00 | SAT (positive control) |
| 1 | 250 | 250 | 0.031 | 5.72 | ~0.98 | SAT |
| 2 | 125 | 250 | 0.031 | 5.72 | ~0.90 | SAT / edge |
| 2 | 250 | 500 | 0.061 | 4.05 | ~0.70 | MB / edge |
| 4 | 125 | 500 | 0.061 | 4.05 | ~0.55 | MB |
| 4 | 250 | 1000 | 0.122 | 2.86 | ~0.30 | **MB (DISCRIMINATOR)** |

The (L=4, K=250) point sits at CRLB-derived SAT floor + noise regime where op-specific deviations become measurable.

**discriminator_reachability:** TRUE. DISCRIMINATOR_MIN_PAIR_DIFF=0.15 is well below the SNR-derived MB spread (top1 span at this SNR typically 0.10-0.40 across ops per drill note).
**crlb_floor_computed:** ~0.30 top1 at (L=4, K=250) for random-permutation baseline.
**crlb_formula_reference:** `SNR = sqrt(N/(L*K))` for random-code interference; `top1 ~ Phi(SNR - k)` for k=alpha*log(V) cleanup.

## Effective vs nominal parameter audit (per canonical §15 gate A)

- **swept_params:** L in {1,2,4}, K_per_seq in {125,250}
- **effective_params_per_primitive:**
  - CYCLIC_SHIFT: effective_load = L * K_per_seq (linear; matches sweep)
  - RANDOM_PERMUTATION: effective_load = L * K_per_seq
  - PHASE_ROTATION: effective_load = L * K_per_seq
- **sweep_alignment_verdict:** ALIGNED (all 3 ops see the same effective L*K load)

## Discriminating-band coverage (per canonical §15 gate B)

Predicted top1 per sweep point per PREDICTED_ORDER (drill note assumes PERM > PHASE > CYCLIC):

| L,K | CYCLIC (predicted) | PERM (predicted) | PHASE (predicted) | in_disc_band (any)? |
|---|---|---|---|---|
| 1,125 | ~1.00 SAT | ~1.00 SAT | ~1.00 SAT | no (positive control) |
| 1,250 | ~0.98 SAT | ~0.98 SAT | ~0.95 SAT | no |
| 2,125 | ~0.90 SAT/edge | ~0.92 SAT/edge | ~0.85 SAT/edge | maybe |
| 2,250 | ~0.55 MB | ~0.70 MB | ~0.60 MB | **yes (3/3 in disc band)** |
| 4,125 | ~0.35 MB | ~0.55 MB | ~0.45 MB | **yes (3/3 in disc band)** |
| 4,250 | ~0.10 FLOOR | ~0.35 MB | ~0.20 TRANSITION | **yes (>=2/3 in disc band)** |

Points_in_discriminating_band: >=9/18 (~50%; well above 30% floor). Discriminating_fraction: >= 0.50.

## Composition / signal-shape audit (per canonical §15 gate C)

- **composition_edges:** none (v2 is a single-primitive-family cell; no new primitive composition).
- **A_natural_output_shape:** _build_positions -> (K, N); items -> (K, N); shape-match at Hadamard bind.
- **verdict:** SHAPE_MATCH.

## Positive-control at test regime (per canonical §15 gate D)

Since v2 REUSES v1 primitives at N=8192 but adds load axis, positive control = reproduce v1 CYCLIC_SHIFT at K=125-ish behavior AT MATCHED REGIME (L=1). Prior v1 point closest: K=50 -> 1.000 CG. v2 uses (L=1, K=125) which per CRLB SNR=8.10 predicts ~1.00.

- **positive_control_arm:** CYCLIC_SHIFT@(L=1, K=125)
- **cited_prior_atom:** substrate_order_binding_family_v1 CYCLIC@K=50 = 1.000 MEASURED@data/exp_substrate_order_binding_family_v1_seed_13/metrics.json
- **cited_prior_metric:** 1.000 (K=50); 0.66 (K=500)
- **cited_prior_regime:** {N: 8192, K: 50, L_implicit: 1, encoding: bipolar}
- **test_regime:** {N: 8192, K: 125, L: 1, encoding: bipolar}
- **tolerance:** 0.20 (test_regime slightly harder than prior K=50; SNR 8.10 vs 12.8; predicted mild drop from 1.00 to ~0.95)
- **if_outside_tolerance:** HARD_FAIL_META_RULE_BC test rig broken
- **regime_extension_audit:** SHAPE_MATCH (same N, same encoding, K_per_seq 125 within v1 sweep bracket)

Floor: `top1_floor_required=0.80`.

## Discriminator (LOCKED)

**HARD_PASS gate:** at (L=DISCRIMINATOR_L=4, K_per_seq=DISCRIMINATOR_K=250):
1. `max_pair_diff >= 0.15` across 3 op pairs (CYCLIC vs PERM, CYCLIC vs PHASE, PERM vs PHASE), AND
2. Pair-distinctness True on ALL 3 pairs (bundle_hash AND positions_hash), AND
3. Positive control passes, AND
4. Cardinality OK, AND
5. n_suspect_saturation < n_total_pts (not ALL points at 1.000)

**HONEST_ABORT (HARD_FAIL substantive):** all 3 pair diffs at (L=4, K=250) `<= 0.03`
  -> order-binding is capability-family-invariant under multi-sequence load AS WELL AS at single-seq cliff (v1)
  -> Axis J CLOSED as substantive negative; deprioritize position-encoding family cells program-wide.

**MIDDLE_BAND:** max_pair_diff in (0.03, 0.15) -> partial family-separation; regime nudge or FULL 60-query resolution may promote.

## Predicted ordering (drill note; direction check ONLY, not gate)

Per drill note candidate #1:
- RANDOM_PERMUTATION > PHASE_ROTATION > CYCLIC_SHIFT at (L=4, K=250)
- Basis for prediction: compressed-sensing basis-universality (Puy et al 2012), HRR SNR=1/m, VSA cross-talk theory.

**Direction check surfaces in verdict_msg** as observed ordering; NOT gated.

## SCHEMA-VET pre-dispatch checklist (canonical §7)

- [x] `cardinality_ok`: MANDATORY (§1) — EXPECTED_N_UNITS_FULL=EXPECTED_N_UNITS_SMOKE=18
- [x] failure-class instrumentation (§2) — `except Exception` (not bare/BaseException); crash-diag sentinel with traceback
- [x] discriminator-fires gate (§3) — smoke gate REQUIRES max_pair_diff >= 0.15 at (L=4,K=250)
- [x] strictly-above-floor target (§4) — HARD_PASS threshold 0.15 (band width from HONEST_ABORT 0.03 to gate 0.15 = 0.12; gate is at MAX of band, not floor)
- [x] HP_SCOPE (§5b) — HARD_PASS gate applies to (L=4, K=250) point only; positive control (L=1, K=125) has SEPARATE floor gate (0.80 top1)
- [x] calibration_check (§5) — `default_ok_for_this_regime`; CRLB-predicted SNR spread supports discriminator band
- [x] arms_differ_verified (§6) — smoke gate + selftest hash both bundle AND positions per op
- [x] final_metrics_atomicity (§7) — write_partial_key + `metrics.json` write; single-shot per seed
- [x] except SystemExit: raise (§8) — outer try in seed_7 uses `except Exception` after SystemExit + KeyboardInterrupt re-raise
- [x] CRLB / capacity feasibility (§9) — computed above; DISCRIMINATOR reachable at CRLB-derived MB regime
- [x] baseline-in-band (§10) — smoke gate checks NOT-ALL-SAT AND NOT-ALL-FLOOR at (L=4,K=250)
- [x] HYPOTHESIZED vs MEASURED marking (§11) — all v1 numbers are MEASURED@; all v2 predictions THEORETICAL@ or HYPOTHESIZED@
- [x] cell_chunked (§13) — one seed per file
- [x] start_marker_written — yes (init phase)
- [x] crash_diagnostic_present — yes (import_crash sentinel + main-outer catch)
- [x] heartbeat_present — print-flush per phase point (~60s cadence acceptable for CPU cells)
- [x] atoms.jsonl schema (§14) — N/A (cell does not write atoms; downstream skunkworks will)
- [x] test-design gates (§15) — A: ALIGNED. B: ~50% in disc band. C: SHAPE_MATCH single primitive. D: positive control @ v1-cited regime. E: 4 functional requirements decomposed.
- [x] run_mode verification post-dispatch (§16) — reporter verifies run_mode field matches dispatch expectation

## Smoke pre-flight assertion (DISCRIMINATOR-MUST-SURVIVE-SCALE)

Smoke grid = FULL grid (18 pts identical). n_queries=8 at smoke vs 60 at FULL is the only reduction. Discriminator gate fires at smoke IF discriminator would fire at FULL (same L, same K, same op set, same seed). Cost: smoke ~10-15min per seed; catches invariance / aliasing / regime-broken BEFORE full compute.

## Anti-aliasing (v1 mechanism-hash guard)

v2's bundle_hash includes explicit `V2_LOAD_SALT` bytes (`b"substrate_order_binding_family_v2_load_variant_2026-07-01"`) + `|op=X|L=Y|K=Z|` tag mixed BEFORE the raw bundle bytes. This guarantees:
- v1's identical (op, K) bundle NEVER hashes to v2's (op, L=1, K) even at numerically-identical bytes.
- Guards the STALE_QUEUE_ERROR_WITH_CLEAN_CURRENT_METRICS + mechanism_hash-aliasing failure modes.

Selftest step 4 verifies the salt is actually applied (compares salted vs unsalted hash; fails if equal).

## Cross-thread synthesis (drill note)

- If v2 lands HP: order-binding capability acquires a **choose-your-position-encoder** knob keyed to load; Stage 2 architectural lever composable with WM K=4096 CG primitive.
- If v2 lands HF (HONEST_ABORT): Axis J CLOSED substantively; deprioritize position-encoding family cells program-wide; Research pivots to other 5x-drill candidates (Axis F cleanup-family; serial-position candidate #2).
- 5x-drill escalation eligible on HARD_PASS per drill note (3-domain support: VSA cross-talk + WM literature + compressed-sensing).
