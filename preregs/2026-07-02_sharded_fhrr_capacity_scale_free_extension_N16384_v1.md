# Pre-reg: sharded_fhrr_capacity_scale_free_extension_N16384_v1

Date: 2026-07-02
Anchor: `sharded_fhrr_capacity_scale_free_extension_N16384_v1`
Cell: `experiments/exp_sharded_fhrr_capacity_scale_free_extension_N16384_v1.py`
Stage: 1 (substrate-physics primitive; extension of META CG_LAW)
Author: exp_dev (spawned by Director 2026-07-02)

## Motivation

Skunkworks composed `META_STORAGE_STRATEGY_COMPOSITION_DEPTH_PHYSICS_LAW_v1` as CHAIN_GRADE_META on 2026-07-02 with explicit extension criterion: **"N=32768/1M for scale-free LAW"**. This cell is the **first extension-criterion probe**: does the sharded-vs-bundle discriminator pattern reproduce at 2x N (N=16384) with the same NPROP/N ratio (~1.95x)?

Reference cell:
  MEASURED@d:/AI/hd-instrument/data/exp_sharded_fhrr_cleanup_capacity_beyond_bundle_bound_v1_seed_7/metrics.json:
    - sharded_acc_at_max_nprop = 1.0000 (SHARDED perfect at NPROP=16000, N=8192)
    - bundle_acc_at_collapse_check = 0.045 (BUNDLE collapse at NPROP=4000, N=8192)
    - elapsed_s = 4.7 (full 9-point sweep, cuda)
    - "Sharded rule-storage extends cleanup capacity ~13.9x beyond classical bundle bound"

**Goal:** if same-shape discriminator reproduces at N=16384 (SHARDED >= 0.95 at NPROP=32000; BUNDLE < 0.60 at NPROP=4000), META atom promotes to SCALE_FREE_PHYSICS_LAW tier -- validated across 2x N range. If NOT, META scope is bounded to N=8192 and physics law is scale-dependent (honest DEMOTE).

## Prior-work check (substrate-KB concept-query)

Query: `sharded capacity scale-free extension N=16384 physics law`
Top-5 cosine (max 0.3496):
  1. `Capacity / scale extensions` cosine=0.3496 (notes/research_to_exp_dev_LAPTOP_WAVE2_2026-06-09.md)
  2. `1.1 Scale Extension` cosine=0.2832 (notes/research_drill_compliance_maximization_2x_2026-06-09.md)
  3. `Extension` cosine=0.2715 (preregs/2026-05-30_path_d_mixed_confidence_v1_n4096.md)
  4. `Capacity extension via hierarchy` cosine=0.251
  5. `P1 Extreme scale extensions` cosine=0.2412

Verdict: **NONE above cosine 0.30 for the specific scale-free-META extension probe.** Generic "scale extension" work exists in the KB; this specific META CG_LAW extension criterion is genuinely novel. Not a rediscovery.

## Discriminator

**Load-bearing question:** at N=16384 (2x the CG cell's N=8192), does the sharded-vs-bundle discriminator reproduce the CG cell's pattern (SHARDED perfect at NPROP >= 1.9*N; BUNDLE collapses at NPROP >> 0.14*N)?

- SHARDED arm: per-antecedent codebook `rule_vec[a] = cnorm(props[a] * IMPL * props[nxt[a]])`; query by index + unbind + matched-filter argmax cleanup vs props. Matched-filter capacity ~ N / (2 log V) grows with N; scale-free by matched-filter theory.
- BUNDLE arm (classical bundle control): single vector `S = sum_a cnorm(...)`; predicted collapse at NPROP ~ 0.14 * N ~= 2294 per Plate 1995.

**Cross-axis test:** does per-antecedent shard-lookup + matched-filter cleanup produce capacity ~14x the classical bundle bound at 2x N?

## Pre-registered bands

- **HARD_PASS:** SHARDED acc >= 0.95 at NPROP=32000 (>= 1.9*N=31130) AND BUNDLE acc < 0.60 at NPROP=4000 (>> 0.14*N=2294 bound). Same-pattern-at-2x-N; **META extension criterion SATISFIED** -- law verified across 2x N range and eligible for SCALE_FREE_PHYSICS_LAW tier promotion.
- **MIDDLE_BAND:** SHARDED >= 0.95 at NPROP=16000 but drops below 0.90 at NPROP=32000. Extended capacity confirmed vs bundle bound but not at 2*N; META scale-free claim PARTIAL.
- **HARD_FAIL:** SHARDED collapses at NPROP=32000 (acc < 0.60). **META scale-free physics law CLAIM FALSIFIED** -- law is N-dependent; would DEMOTE META atom to scale-bounded (N<=8192) scope.

## Grid + arms

FULL grid NPROP in {2000, 4000, 8000, 16000, 32000}:
  - NPROP=2000: comfortably below 0.14*N=2294 bundle bound; both arms baseline high
  - NPROP=4000, 8000, 16000: intermediate; BUNDLE expected to collapse progressively
  - NPROP=32000: ~1.95*N; **HP gate point**; matches CG cell's NPROP=16000/N=8192 ratio

Arms: SHARDED, BUNDLE (per-phase-point).
N=16384, M=200 queries per (NPROP, arm) phase point. Single seed per cell invocation.
FULL run: 3 seeds via 3 separate queue entries (seed=7, 13, 19) chunked per META_RULE §13.

## Smoke design (discriminator-must-survive-scale)

Smoke grid: NPROP in {2000, 8000, 32000} at **full-N N=16384** (per DISCRIMINATOR-MUST-SURVIVE-SCALE rule A: smoke at full-N so mechanism gap validated pre-dispatch). M=30 queries.

Rationale:
- NPROP=2000: BUNDLE ~0.5-0.6 (just below bound); SHARDED perfect. Sanity anchor.
- NPROP=8000 (~3.5x bundle bound): SHARDED still perfect; BUNDLE well below 0.60.
- NPROP=32000 (~14x bundle bound; 1.95*N): **full discriminator preview at HP gate point.**

If smoke fires (SHARDED >= 0.95 AND BUNDLE < 0.10 at NPROP=32000; gap >= 0.85), full dispatch is authorized.

## Discipline gates (SCHEMA-VET / META_RULE)

| Gate | Value | Notes |
|------|-------|-------|
| `cardinality_ok` (META_RULE_H) | `len(per_unit) == n_units` | 5-point NPROP grid FULL / 3-point smoke; verdict logic gates. |
| `arms_differ_verified` (META_RULE_AF) | True | SHA-256 hash-check of sharded_codebook vs bundle_vec bytes per phase point. Assert distinct. |
| `final_metrics_atomicity` (META_RULE_AH) | `tmp_replace` | Single-shot write; `.tmp` + `os.replace()`. |
| `except SystemExit: raise` before `except Exception` | Present | Outer try/except with SystemExit + KeyboardInterrupt pass-through; Exception writes CELL_CRASHED diag. |
| `crlb_floor_computed` | N/A per matched-filter regime | Not Cramer-Rao; capacity is codebook-argmax vs matched-filter SNR. Classical bundle bound cited as `bundle_bound_approx = 0.14 * N ~ 2294`. |
| `crlb_n/a` reason | Cell measures P(argmax correct) over V-codebook; no continuous parameter estimation. | |
| `discriminator_reachability` | True | Predicted at NPROP=32000: sharded near 1.0 (matched-filter over V=32000 codewords with SNR~sqrt(N)~128 still saturates); bundle near ~1/V per random-vector unbind. Selftest asserts mechanism at reduced N=4096; smoke asserts at full N=16384. |
| `baseline_in_band` (META_RULE_AG) | Both arms verified in-band across sweep | SHARDED expected 1.0 across full grid. BUNDLE crosses from ~0.5+ (NPROP=2000) to ~0 (NPROP=32000); discriminating band well populated. |
| `cell_chunked` | True | Single-seed-per-cell; 3 seeds via 3 separate FULL entries. |
| `start_marker_written` | True | `_start_marker.json` at main() entry, atomic. |
| `crash_diagnostic_present` | True | `_write_crash_metrics()` on Exception; tmp+os.replace. |
| `heartbeat_present` | False (optional) | 5 phase points; est ~15-30s per seed on GPU; below §13 heartbeat threshold. Per-phase-point `print(..., flush=True)` provides equivalent audit. |
| `defensive_error_checking` | `passed_all_4_patterns` (start_marker + crash_diag + progress-flush + arms_differ_hash) | |
| `progress_logging` (§17) | `print_flush_true` + `sys.stdout.reconfigure(line_buffering=True)` at cell entry. Per-phase-point print line + flush. Under 30min timeout gate; §17 field optional but declared. | |
| `calibration_check` (META_RULE_M) | `default_ok_for_this_regime` | FHRR complex64 unit-modulus; no encoder-specific calibration. |
| Sweep alignment (§15A) | ALIGNED | NPROP sweep alone; no compositional effective-vs-nominal ambiguity. |
| Discriminating fraction (§15B) | 5/5 in discriminating band | All sweep points span BUNDLE 0.5+ down to ~0 across grid; SHARDED expected 1.0 throughout. Band populated. |
| Composition edges (§15C) | N/A single-primitive cell | No cross-primitive composition. |
| Positive control (§15D) | BUNDLE arm serves as classical-bundle positive control (reproduces Plate 1995 bound at N=16384). If BUNDLE does NOT collapse at NPROP >= 4000, cell falsifies its own regime assumption. Direct extension of CG cell's positive control at 2x N. | |
| Functional requirements (§15E) | (1) verify SHARDED scales past 0.14*N at N=16384 (extension); (2) verify BUNDLE collapses per classical Plate bound at 2x N (positive control); (3) validate META scale-free extension criterion at 2x N range. All mapped to arm design. | |

## Compute architecture (USER 2026-07-02 mandatory declaration)

**Class:** batched-GPU (torch complex64, auto CUDA-detect, batched cleanup matmul).

**Storage strategy:** sharded (per META CG_LAW being extended); bundle arm is positive control.

**Rationale:** cleanup at (M=200, N=16384, V=32000) is a matmul ~1.05e11 complex ops per phase point; on CPU numpy would be ~1-2 min per matmul (sequential-CPU untenable), on GPU torch ~1-3s. Total FULL wall (5 points x 2 arms x 200 queries): ~15-40s on CUDA (extrapolating from CG cell's 4.7s at N=8192 x ~4x memory/compute for 2x N + reduced grid), CPU-torch ~5-15 min. Per-phase-point wall > 10s on CPU triggers batching-candidate rule; GPU-batched design chosen (USER-locked 2026-07-02).

**Peak GPU VRAM (v3 CPU-hosted design; targets 8GB GPU with 5.87 GB runner baseline):** at NPROP=32000, N=16384:
  - `props_cpu` (32000, 16384) complex64 = 4.19 GB on **CPU RAM** (never a single GPU tensor).
  - BUILD chunk (C=2000, N=16384): peak GPU transient ~1.0-1.5 GB
    (A_c + B_c CPU->GPU copies, product, cnorm intermediates: fp32 angle + fp32 ones + complex64 polar output + rule_c). PyTorch releases intermediates progressively; concurrent peak is ~7 x complex64(2000, 16384) worth during cnorm.
  - SHARDED query shards on demand (M=200, N): 26 MB.
  - CLEANUP chunk (CV=2000, N=16384): peak GPU transient ~300 MB (cb_chunk 262 MB + queries 26 MB + sim(M, CV) fp32 3 MB).
  - BUNDLE: single (N,) vector accumulated across chunks (128 KB).
  - **Peak GPU ~ 1.5 GB. Fits 8GB target with ~1.4 GB headroom over the 2.94 GB free measured at v2 OOM.**
  Cell issues `torch.cuda.empty_cache()` after each BUILD chunk + each CLEANUP chunk + after phase point + `del` of large tensors between chunks. `torch.cuda.max_memory_allocated()` logged per phase point as `peak_gpu_mb` in per_unit metrics.

**Peak CPU RAM:** ~4.5 GB (props_cpu + small overhead). marsh@home has ample CPU RAM.

**v1/v2 OOM history (2026-07-02):**
  - **v1 unchunked** (commit `6d43ea571`): full-size `cnorm_torch(A * IMPL * B)` created intermediate fp32 angle tensor (~2 GiB) simultaneously with 4.2 GB props on GPU -> peak >6 GiB -> OOM at line 189.
  - **v2 chunk-in-GPU** (commit `349e75383`): downstream ops chunked, but `props = cphasor_torch(NPROP, N, gen, device)` at line 165 still allocated a 4.19 GB single GPU tensor -> OOM at cphasor construction on 8GB target (2.94 GB free after 5.87 GB runner baseline).
  - **v3 CPU-hosted** (this commit): `props_cpu` built + held on CPU RAM in chunks; per-chunk transfers to GPU during BUILD + streamed CLEANUP. `props` is NEVER a single GPU tensor. Peak GPU well under 2 GB.

**Verification (2026-07-02):**
  - Selftest N=4096 PASS: SHARDED=1.000 across NPROP; BUNDLE=0.400/0.067/0.000 at NPROP=200/2000/8000. (v3 numbers marginally differ from v1/v2 CPU output because v3 re-seeds per-NPROP for reproducibility; mechanism-equivalent — collapse pattern identical.)
  - Smoke at full N=16384 CPU HARD_PASS (17.9s wall): SHARDED=1.0000 across NPROP=2000/8000/32000; BUNDLE=0.4667/0.0000/0.0000. Discriminator shape identical to v1/v2. HP conditions satisfied.
  - CPU device on laptop (peak_gpu_mb=None on CPU); GPU device peak measured at overnight_queue dispatch via `torch.cuda.max_memory_allocated()`.

Requires 3-seed FULL re-dispatch with `--allow-duplicate` per SH-6 (prior entries now `status=failed` on both v1 and v2).

**Fallback:** if `torch.cuda.is_available() == False`, cell runs on CPU-torch (still batched matmul). Cell will not fail; will simply run slower.

## Timeout estimate

- Smoke: ~10-30s on GPU (3 phase points at reduced M=30), ~2-5 min CPU-torch.
- FULL (per seed): ~20-60s GPU, ~5-15 min CPU-torch.
- Recommended `--timeout 1800` (30 min) per FULL entry; wide margin for GPU queuing + first-run compilation.

## Dispatch plan

1. Self-test locally on .venv (`--self-test` at reduced N=4096; formula assertions verify mechanism).
2. Smoke on `remote_cpu_queue` (fast smoke gate; discriminator fires at full-N=16384 via NPROP=32000 phase point). Local smoke skipped since USER laptop cannot run N=16384 NPROP=32000 in-time (would need CPU-torch ~5min at least; would occupy USER's laptop for that duration -- prefer remote CPU or GPU).
3. Author asks Director to route FULL to `overnight_queue` (3 seed entries: 7, 13, 19). Director dispatches via `hd_metrics_sync` push.

## Stage 1 classification

Substrate-physics primitive extension (Stage 1). Not a language / semantic test; substrate-doesn't-know-anything rule (USER 2026-06-26) does NOT apply. Not composed of prior chain-grade primitives; direct scale-extension of a just-landed CG_META atom.

## Multi-seed smoke rule exemption

Per META_confidence_signal_smoke_single_seed_inflates_AUC (Skunkworks CG 2026-07-02), multi-seed smoke is mandatory for confidence/contamination cells where discriminator is AUC over continuous scores. **This cell is EXEMPT** per that META's own exclusion clause: "Does NOT apply to pure capacity sweeps (e.g. sharded_capacity beyond bundle bound -- accuracy is deterministic given the mechanism)." Single-seed smoke sufficient; per-phase-point acc is deterministic hits-over-M (not a lucked-in continuous AUC).

## Landing plan / CG-eligibility

Cell is HP-eligible if all 3 seeds HARD_PASS. Under HP:
- Load-bearing outcome: META CG_LAW promotes from CHAIN_GRADE_META to SCALE_FREE_PHYSICS_LAW tier (verified across 2x N range).
- Extension logic: additional probes at N=32768 (4x CG N) and N=1M (production-scale) would remain to fully close the SCALE_FREE claim; this cell is the **first** such extension.
- If HARD_FAIL: META atom's scale-free claim honestly SCOPED to N<=8192; scale-dependency becomes a research question (why does law break at 2x N? matched-filter SNR should scale; suggests underlying primitive is subtler than pure matched-filter).
