# Pre-reg: sharded_fhrr_cleanup_capacity_beyond_bundle_bound_v1

Date: 2026-07-02
Anchor: `sharded_fhrr_cleanup_capacity_beyond_bundle_bound_v1`
Cell: `experiments/exp_sharded_fhrr_cleanup_capacity_beyond_bundle_bound_v1.py`
Stage: 1 (substrate-physics primitive)
Author: exp_dev (spawned by Director 2026-07-02)

## Motivation

Discovered inside math4_proof_chains smoke saturation (2026-07-02, agent a704c99fb61cf4cd2): sharded FHRR rule storage supported NPROP >= 2 * N (N=8192, NPROP=16000) with **perfect single-hop cleanup**. Classical bundle-capacity bound is ~0.14 * N ~= 1147 (Plate 1995). That is ~15x beyond classical.

## Prior-work check (substrate-KB concept-query)

Query: `sharded FHRR cleanup capacity beyond bundle bound rule storage`
Top-5 cosine (max 0.3818):
  1. `Bundle storage` cosine=0.3818 (research_drill_substrate_wikidata_ingest_optimization_2x_2026-06-09.md)
  2. `1.2 Plate Bundle Capacity Bound (1995)` cosine=0.3193 (research_drill_codebook_capacity_structural_3x_2026-06-10.md)
  3. `Capacity analysis: the FHRR bundle SNR` cosine=0.3184 (research_drill_negative_GPU_Khop_infra_2x_2026-06-08.md)
  4. `Capacity bounds` cosine=0.3086 (wave14e_hierarchical_composition_research.md)
  5. `2.4 FHRR vs BSC Bundle Capacity` cosine=0.2939 (research_drill_bundle_capacity_limits_2x_2026-06-09.md)

Verdict: **NONE at cosine > 0.30 for direct hits.** Bundle-capacity work exists (Plate 1995, FHRR/BSC bundle SNR, Löwe correlated-key alpha_c(rho)). Sharded-vs-bundle comparison for rule-storage capacity is **genuinely novel** for the arc.

## Discriminator

**Load-bearing question:** at what NPROP does per-antecedent SHARDED cleanup accuracy drop below 0.95 for N=8192?

- SHARDED arm: per-antecedent codebook `rule_vec[a] = cnorm(props[a] * IMPL * props[nxt[a]])`; query by index lookup + unbind + argmax cleanup vs props. Cleanup is matched-filter over V=NPROP unit-norm codebook entries; predicted capacity ~ N / (2 log V) = 8192 / (2 * log 16000) = 8192 / 19.4 ~= 422 pattern-completion under Plate bound (but this cell's cleanup is not pattern-completion, it's matched-filter argmax over V codewords, which extends further; see below).
- BUNDLE arm (positive control): single vector `S = sum_a cnorm(props[a] * IMPL * props[nxt[a]])`; query by unbind + argmax cleanup vs props. Predicted collapse at NPROP ~ 0.14 * N ~= 1147 per classical Plate 1995 bundle-capacity bound.

**Cross-axis test:** does per-antecedent shard-lookup + matched-filter cleanup produce capacity ~15x the classical bundle bound?

## Pre-registered bands

- **HARD_PASS:** SHARDED acc >= 0.95 at NPROP=16000 (>= 1.9*N ~= 2*N regime) AND BUNDLE acc < 0.60 at NPROP >= 4000. Both mechanisms fire (sharded scales; bundle collapses per Plate bound). Note: grid tops at NPROP=16000 (1.95*N); HP gate uses 1.9*N so this max clears.
- **MIDDLE_BAND:** SHARDED >= 0.95 at NPROP=8000 but drops below 0.90 at NPROP=16000. Extended capacity confirmed vs bundle bound but not at 2*N.
- **HARD_FAIL:** SHARDED collapses at NPROP=16000 (acc < 0.60). math4 finding was noise / test-config artifact.

## Grid + arms

Sweep NPROP in {200, 500, 1000, 2000, 4000, 6000, 8000, 12000, 16000}
Arms: SHARDED, BUNDLE (per-phase-point).
N=8192, M=200 queries per (NPROP, arm) phase point. Single seed per cell invocation.
FULL run: 3 seeds via 3 separate queue entries (seed=7, 13, 19) chunked per META_RULE §13.

## Smoke design (discriminator-must-survive-scale)

Smoke grid: NPROP in {200, 4000, 16000} at **full-N N=8192** (per DISCRIMINATOR-MUST-SURVIVE-SCALE rule A: smoke at full-N so mechanism gap is validated pre-dispatch). M=30 queries.

Rationale:
- NPROP=200 (well below 0.14 * N): both arms expected near-perfect.
- NPROP=4000 (>= 3x bundle bound): SHARDED still perfect; BUNDLE should be well below 0.60.
- NPROP=16000 (~14x bundle bound; 2*N): full discriminator preview.

If smoke fires (SHARDED gap - BUNDLE gap >= 0.70 at NPROP=16000), full dispatch is authorized.

## Discipline gates (SCHEMA-VET / META_RULE)

| Gate | Value | Notes |
|------|-------|-------|
| `cardinality_ok` (META_RULE_H) | `len(per_unit) == n_units` | 9-point NPROP grid FULL / 3-point smoke. |
| `arms_differ_verified` (META_RULE_AF) | True | SHA-256 hash-check of sharded_codebook vs bundle_vec bytes per phase point. Assert distinct. |
| `final_metrics_atomicity` (META_RULE_AH) | `tmp_replace` | Single-shot write; `.tmp` + `os.replace()`. |
| `except SystemExit: raise` before `except Exception` | Present | `try main() ... except Exception` guard writes CELL_CRASHED diag; SystemExit + KeyboardInterrupt pass through. |
| `crlb_floor_computed` | N/A per matched-filter regime | Not a Cramer-Rao problem; capacity is codebook-argmax vs matched-filter SNR. Classical bundle bound cited as `bundle_bound_approx = 0.14 * N ~ 1147`. |
| `crlb_n/a` reason | Cell measures P(argmax correct) over V-codebook; no continuous parameter estimation. | |
| `discriminator_reachability` | True | Predicted gap at NPROP=16000: sharded ~1.0, bundle ~1/16000 (matched-filter over pure-noise vector). Selftest asserts both. |
| `baseline_in_band` (META_RULE_AG) | Both arms verified in-band across sweep | SHARDED expected 1.0 across full grid (matched-filter). BUNDLE crosses from ~1.0 (NPROP=200) to ~0.0 (NPROP=16000); discriminating band well populated. |
| `cell_chunked` | True | Single-seed-per-cell; 3 seeds via 3 separate FULL entries. |
| `start_marker_written` | True | `_start_marker.json` at main() entry, atomic. |
| `crash_diagnostic_present` | True | `_write_crash_metrics()` on Exception; tmp+os.replace. |
| `heartbeat_present` | False (optional) | 9 phase points * ~5s each = ~45s per seed on GPU; below §13 heartbeat threshold (15min). Progress `print(..., flush=True)` per phase point provides equivalent audit. |
| `defensive_error_checking` | `passed_all_4_patterns` (start_marker + crash_diag + progress-flush + arms_differ_hash) | |
| `progress_logging` (§17) | `print_flush_true` + `sys.stdout.reconfigure(line_buffering=True)` at cell entry. Per-phase-point print line + flush. Well under 30min timeout gate. | |
| `calibration_check` (META_RULE_M) | `default_ok_for_this_regime` | Substrate is FHRR complex64 unit-modulus; no encoder-specific calibration. |
| Sweep alignment (§15A) | ALIGNED | NPROP sweep alone; no compositional effective-vs-nominal ambiguity. |
| Discriminating fraction (§15B) | 9/9 in discriminating band (all sweep points span 1.0 down to ~0 for BUNDLE). | |
| Composition edges (§15C) | N/A single-primitive cell | No cross-primitive composition. |
| Positive control (§15D) | BUNDLE arm serves as classical-bundle positive control (reproduces Plate 1995 bound). If BUNDLE does NOT collapse at NPROP >= 4000, cell falsifies its own regime assumption. | |
| Functional requirements (§15E) | (1) verify sharded storage scales past 0.14*N; (2) reproduce bundle collapse as sanity. Both mapped to arm design. | |

## Compute architecture (USER 2026-07-02 mandatory declaration)

**Class:** batched-GPU (torch complex64, auto CUDA-detect, batched cleanup matmul `(M, N) @ (N, V)^H`).

**Rationale:** cleanup at (M=200, N=8192, V=16000) is a matmul ~2.6e10 complex ops per phase point; on CPU numpy ~20s per matmul, on GPU torch < 0.5s. Total FULL wall (9 points x 2 arms x 200 queries): ~2-3 min on CUDA, ~5-10 min on CPU. Per-phase-point wall > 10s at NPROP=16000 on CPU triggers batching-candidate rule; GPU-batched design chosen.

**Fallback:** if `torch.cuda.is_available() == False` cell runs on CPU-torch (still batched matmul, no Python loop over queries).

## Timeout estimate

- Smoke: ~30s on GPU (3 phase points * 30 queries * <0.5s matmul), ~10-15s CPU-torch.
- FULL (per seed): ~2-3 min GPU, ~5-10 min CPU-torch.
- Recommended `--timeout 1800` (30 min) per FULL entry; ~10-15x margin.

## Dispatch plan

1. Self-test locally (`--self-test` exits 0, formula assertions verify).
2. Smoke on `local_cpu_queue` (fast smoke gate; discriminator fires at full-N).
3. Author asks Director to route FULL to `overnight_queue` (3 seed entries: 7, 13, 19). Director dispatches via `hd_metrics_sync` push.

## Stage 1 classification

Substrate-physics primitive: sharded-storage capacity vs classical bundle bound. Not a language / semantic test; substrate-doesn't-know-anything rule (USER 2026-06-26) does NOT apply. Not composed of prior chain-grade primitives; single-primitive characterization.

## Landing plan / CG-eligibility

Cell is CG-eligible if all 3 seeds HARD_PASS. Under HARD_PASS:
- CG atom: `sharded_fhrr_cleanup_capacity_ratio_v1` (extends classical Plate bundle bound by measured ~15x for per-antecedent storage; complements Löwe correlated-key alpha_c(rho) bundle finding).
- Load-bearing for M3 cortex: sharded storage of primitives (rule library, fact library, cortex-primitive registry) is the natural pattern. Grants sharded capacity headroom for cortex primitive count >> N.
