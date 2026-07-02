# Pre-reg: sharded_fhrr_topology_free_dag_extension_v1

Date: 2026-07-02
Anchor: `sharded_fhrr_topology_free_dag_extension_v1`
Cell: `experiments/exp_sharded_fhrr_topology_free_dag_extension_v1.py`
Stage: 1 (substrate-physics primitive; extension of META CG_LAW)
Author: exp_dev (spawned by Director 2026-07-02)

## Motivation

Skunkworks composed `META_STORAGE_STRATEGY_COMPOSITION_DEPTH_PHYSICS_LAW_v1` as
CHAIN_GRADE_META on 2026-07-02, then promoted to SCALE_FREE this session via the
N=16384 extension probe. The named next-axis extension criterion is `DAG topology
for topology-free LAW`. All prior cells that established the META atom used
LINEAR chain rules (single successor per node): `math4_v2` at L=2-6, `math4_rung3`
at L=8-20, `sharded_capacity_beyond_bundle_bound_v1` and `scale_free_extension_N16384`
at L=1.

This cell tests whether the SHARDED-vs-BUNDLE discriminator holds when rules form
a DAG with **fan-out F > 1** (each source node has F distinct outgoing edges to
random target nodes). Load-bearing for M3 cortex, which must handle DAG-structured
knowledge (multiple facts implying same conclusion; multiple conclusions from same
fact).

Reference cells:

  MEASURED@d:/AI/hd-instrument/data/exp_sharded_fhrr_cleanup_capacity_beyond_bundle_bound_v1_seed_7/metrics.json:
    - sharded_acc_at_max_nprop = 1.0000 (SHARDED perfect at NPROP=16000, N=8192, LINEAR)
    - bundle_acc_at_collapse_check = 0.045 (BUNDLE collapse at NPROP=4000, N=8192)

  MEASURED@d:/AI/hd-instrument/data/exp_sharded_fhrr_topology_free_dag_extension_v1_smoke/metrics.json (this cell smoke, 2026-07-02):
    - F=1 NPROP=5000: sharded=1.0000 bundle=0.0667 (positive control OK)
    - F=4 NPROP=5000: sharded=1.0000 bundle=0.0333 (HP gate satisfied; DAG discriminates)

**Goal:** if same discriminator pattern reproduces at F=4 (DAG fan-out), META atom
promotes to `TOPOLOGY_FREE_SUBSTRATE_PHYSICS_LAW` tier. If NOT, META scope is
bounded to linear chains only and physics law is topology-specific.

## Prior-work check (substrate-KB concept-query)

Query: `DAG topology-free rule storage sharded branching fan-in composition`
Top-5 cosine (max 0.2764):
  1. `Composition` cosine=0.2764 (general chunk_notes)
  2. `Branching tree` cosine=0.2451 (geometric_generalization_experiment_designs_v278)
  3. `research_biology_cross_system_composition_strategies_2x_drill::chunk001` cosine=0.2432
  4. `HARD_FAIL Composition Cells` cosine=0.2354
  5. Non-LLM autonomous KG completion drill chunk cosine=0.2314

Verdict: **NONE above cosine 0.30.** No prior arc for topology-free extension of
the storage-strategy META atom. Novel probe, not a rediscovery.

## Discriminator

**Load-bearing question:** at N=8192 with **DAG fan-out F=4** (each source node
has 4 distinct outgoing edges via random targets), does SHARDED cleanly retrieve
the correct target for each edge while BUNDLE collapses per Plate 1995 bound?

- SHARDED arm: per-edge codebook `rule[edge_idx] = cnorm(props[src]*POS[i]*IMPL*props[dst])`;
  query by `(src, edge_pos)` -> shard lookup + unbind + matched-filter argmax cleanup vs props.
- BUNDLE arm (classical bundle control): single vector `S = sum_edge cnorm(...)`;
  predicted collapse at NRULES ~ 0.14 * N = 1147 for N=8192.

At F=4, NPROP=5000: NRULES = 20000 = 17.4x bundle bound. BUNDLE must collapse.
SHARDED must survive via per-edge shard + matched-filter over V=NPROP codewords.

**Cross-axis test:** does the storage-strategy law extend from L=1-20 linear
chains (prior CG) to F=4 fan-out DAG structure (this cell)?

## Pre-registered bands

- **HARD_PASS:** SHARDED acc >= 0.85 at F=4, NPROP=5000, N=8192 AND
  BUNDLE acc < 0.10 at F=4, NPROP=5000 AND
  F=1 positive control SHARDED >= 0.85 at NPROP=5000 (Gate D reproduction).
  **META topology-free evidence SATISFIED at DAG fan-out F=4.**
- **MIDDLE_BAND:** SHARDED 0.60-0.85 at F=4, NPROP=5000; partial topology invariance.
- **HARD_FAIL:** SHARDED < 0.60 at F=4, NPROP=5000. **META topology-free CLAIM
  FALSIFIED**; law is topology-specific (holds for linear chains only). Would
  DEMOTE META atom to linear-topology-bounded scope.
- **HARD_FAIL (Gate D):** F=1 positive control SHARDED < 0.85 at NPROP=5000 =>
  cell mechanism drift vs prior regime; downstream DAG-branching conclusion
  UNRELIABLE.

## Grid + arms

FULL grid: F in {1, 2, 4} x NPROP in {200, 1000, 5000} = **9 phase points**.
  - F=1 rows: SHARDED_LINEAR positive control (Gate D reproduction under uniform 3-bind mechanism)
  - F=2, F=4 rows: DAG-branching discriminator arms
  - NPROP=200 (below bound=1147): both arms baseline high
  - NPROP=1000 (near bound): BUNDLE partial collapse
  - NPROP=5000 (~4.4x bound linear, 17.4x bound at F=4): BUNDLE collapse; HP gate at F=4

Arms per phase point: SHARDED, BUNDLE (2 arms).
N=8192, M=200 queries per (F, NPROP, arm) phase point. Single seed per cell invocation.
FULL run: 3 seeds via 3 separate queue entries (seed=7, 13, 19) chunked per META_RULE §13.

## Smoke design (discriminator-must-survive-scale)

Smoke grid: F in {1, 4} x NPROP in {200, 5000} = 4 phase points at **full-N N=8192**
(per DISCRIMINATOR-MUST-SURVIVE-SCALE rule A). M=30 queries.

MEASURED@d:/AI/hd-instrument/data/exp_sharded_fhrr_topology_free_dag_extension_v1_smoke/metrics.json (2026-07-02, CPU):
  - F=1 NPROP=200: sharded=1.000 bundle=0.500 (baseline in-band; below bound)
  - F=1 NPROP=5000: sharded=1.000 bundle=0.067 (positive control HP satisfied)
  - F=4 NPROP=200: sharded=1.000 bundle=0.633 (baseline in-band; DAG-mechanism sanity)
  - F=4 NPROP=5000: sharded=1.000 bundle=0.033 (**HP gate satisfied at DAG fan-out F=4**)

**Smoke wall: 6.1s CPU.** Discriminator gap 1.00 - 0.033 = 0.967 at HP gate.
FULL dispatch authorized.

## Discipline gates (SCHEMA-VET / META_RULE)

| Gate | Value | Notes |
|------|-------|-------|
| `cardinality_ok` (META_RULE_H) | `len(per_unit) == 9 FULL / 4 smoke` | Verdict logic gates on HP-point presence in per_unit. |
| `arms_differ_verified` (META_RULE_AF) | True | SHA-256 hash of first-batch shard bytes vs bundle_vec bytes per phase point; assert distinct. |
| `final_metrics_atomicity` (META_RULE_AH) | `tmp_replace` (via `write_metrics` helper + `_write_crash_metrics` uses tmp+os.replace) | |
| `except SystemExit: raise` before `except Exception` | Present | Outer try/except with SystemExit + KeyboardInterrupt pass-through; grep clean. |
| `crlb_floor_computed` | N/A per matched-filter regime | Not Cramer-Rao; capacity is codebook-argmax vs matched-filter SNR. |
| `crlb_n/a` reason | Cell measures P(argmax correct) over V=NPROP codebook; no continuous parameter estimation. | |
| `discriminator_reachability` | True | HYPOTHESIZED@this-file: at F=4 NPROP=5000 N=8192, matched-filter SNR ~ sqrt(N)/sqrt(3-bind noise) ~ 90/1.7 ~ 52 easily saturates cleanup over V=5000. **MEASURED at smoke: sharded=1.000 at HP gate.** |
| `baseline_in_band` (META_RULE_AG) | Both arms verified in-band across smoke | SHARDED expected ~1.0 across full grid. BUNDLE crosses from 0.50 (F=1, NPROP=200) / 0.63 (F=4, NPROP=200) down to 0.03-0.07 (NPROP=5000); discriminating band well populated at intermediate NPROP. MEASURED@smoke. |
| `cell_chunked` | True | Single-seed-per-cell; 3 FULL seeds via 3 separate queue entries. |
| `start_marker_written` | True | `_start_marker.json` at main() entry, atomic. |
| `crash_diagnostic_present` | True | `_write_crash_metrics()` on Exception; tmp+os.replace. |
| `heartbeat_present` | False (optional) | 9 phase points; est ~30-60s per seed on GPU (M=200 x 2 arms x 9 pts); below §13 heartbeat threshold. Per-phase-point `print(..., flush=True)` provides equivalent audit. |
| `defensive_error_checking` | `passed_all_4_patterns` (start_marker + crash_diag + progress-flush + arms_differ_hash) | |
| `progress_logging` (§17) | `print_flush_true` + `sys.stdout.reconfigure(line_buffering=True)` at cell entry. Per-phase-point print line + flush. Below 30-min timeout gate; §17 field optional but declared. |
| `calibration_check` (META_RULE_M) | `default_ok_for_this_regime` | FHRR complex64 unit-modulus; no encoder-specific calibration. |
| Sweep alignment (§15A) | ALIGNED | 2-axis sweep (F, NPROP); no compositional effective-vs-nominal ambiguity. |
| Discriminating fraction (§15B) | 9/9 in discriminating band per HYPOTHESIZED design (smoke: 4/4 measured; SHARDED-BUNDLE gap spans 0.5 -> 0.97 across grid). |
| Composition edges (§15C) | N/A single-primitive cell | No cross-primitive composition; rule is a single 3-bind + cleanup mechanism. |
| Positive control (§15D) | F=1 row serves as positive control (linear-chain reproduction under uniform 3-bind mechanism). Cited prior atom: `sharded_fhrr_cleanup_capacity_beyond_bundle_bound_v1` (sharded=1.0 at NPROP=16000, N=8192). Tolerance: SHARDED >= 0.85 at F=1, NPROP=5000. Regime drift: 3-bind (this cell) vs 2-bind (prior cell) — extra POS[0] binding is a constant multiplier under F=1, so effective mechanism reduces to 2-bind on cancel. MEASURED@smoke F=1 NPROP=5000: sharded=1.000 (well above 0.85 threshold; reproduction validated). |
| Functional requirements (§15E) | (1) verify SHARDED discriminates under DAG fan-out F=4 (topology-free extension); (2) verify BUNDLE collapses per Plate bound at F=4 NRULES >> bound (positive control); (3) verify F=1 reproduces linear-chain regime (Gate D). All mapped to arm design. |

## Compute architecture (USER 2026-07-02 mandatory declaration)

**Class:** batched-GPU (torch complex64, auto CUDA-detect, batched cleanup matmul,
batched build via row-groups of size 500).

**Storage strategy:** sharded (per META CG_LAW being extended); bundle arm is
positive control.

**Rationale:** cleanup at (M=200, N=8192, V=NPROP=5000) is a matmul of ~8.2e9
complex ops per phase point. On CPU numpy would be ~15-30s per matmul (sequential-CPU
untenable); on GPU torch ~0.1-0.5s. Total FULL wall (9 pts x 2 arms x 200 queries):
~5-20s on CUDA (extrapolating from smoke 6.1s at reduced M=30 CPU + build overhead).
CPU-torch FULL wall estimate ~30-60s per seed. Batched-GPU class chosen per
USER-locked 2026-07-02 GPU-batching mandate.

**Peak GPU VRAM at F=4, NPROP=5000, N=8192:**
  - codebook (NRULES=20000, N=8192) complex64 = 1.31 GB
  - props (NPROP=5000, N=8192) complex64 = 328 MB
  - POS (F=4, N=8192) complex64 = 256 KB
  - Build batch peak (B=500, F=4 -> 2000 rows x N complex64) = 131 MB transient
  - Cleanup query (M=200, N=8192) = 13 MB
  - Chunked cleanup V-slice (CV=2000, N=8192) = 131 MB transient
  - **Peak GPU: ~2.5-3.0 GB.** Fits 8GB target with runner baseline (~4-5 GB headroom).

Cell issues `torch.cuda.empty_cache()` after each build batch + each phase point
+ `del` of large tensors between phase points. `torch.cuda.max_memory_allocated()`
logged per phase point as `peak_gpu_mb`.

**Peak CPU RAM:** ~500 MB (mostly torch overhead + numpy tobytes for arm-differ
hash). marsh@home has ample CPU RAM.

**Fallback:** if `torch.cuda.is_available() == False`, cell runs on CPU-torch
(still batched matmul; wall ~30-60s per seed).

## Timeout estimate

- Selftest: ~5s on CPU (reduced N=4096, 3 phase points at F=1/4 x NPROP=200/2000).
- Smoke: 6.1s CPU (MEASURED@this session).
- FULL (per seed): ~5-20s on GPU (batched); ~30-60s on CPU-torch.
- **Recommended `--timeout 1800` (30 min)** per FULL entry; wide margin for GPU
  queuing + first-run compilation + torch.compile if enabled.

## Dispatch plan

1. Self-test locally on .venv (reduced N=4096; 3-point formula assertions). **PASS 2026-07-02** (gap=1.000).
2. Smoke locally on laptop CPU at full N=8192 with F in {1,4} x NPROP in {200,5000}.
   **HARD_PASS 2026-07-02** (6.1s wall; discriminator gap 0.967 at HP gate; positive control 1.000).
3. Author asks Director to route 3-seed FULL to `overnight_queue` (GPU) with
   `HDLAB_SEED` env var (seed=7, 13, 19). Director dispatches via `hd_metrics_sync` push.

## Stage 1 classification

Substrate-physics primitive extension (Stage 1). Not a language / semantic test;
substrate-doesn't-know-anything rule (USER 2026-06-26) does NOT apply. Direct
scope-extension of a chain-grade META atom's named extension axis.

## Multi-seed smoke rule exemption

Per META_confidence_signal_smoke_single_seed_inflates_AUC (Skunkworks CG 2026-07-02),
multi-seed smoke is mandatory for confidence/contamination cells where discriminator
is AUC over continuous scores. **This cell is EXEMPT** per that META's own exclusion
clause: "Does NOT apply to pure capacity sweeps (e.g. sharded_capacity beyond bundle
bound -- accuracy is deterministic given the mechanism)." Single-seed smoke sufficient;
per-phase-point acc is deterministic hits-over-M (not a lucked-in continuous AUC).

## Landing plan / CG-eligibility

Cell is HP-eligible if all 3 seeds HARD_PASS. Under HP:
- Load-bearing outcome: META atom promotes from SCALE_FREE_SUBSTRATE_PHYSICS_LAW
  to **TOPOLOGY_FREE_SUBSTRATE_PHYSICS_LAW** (extended across LINEAR L=1-20 chains
  from prior CG cells AND DAG fan-out F=4 from this cell).
- Downstream implication: M3 cortex can rely on SHARDED storage for DAG-structured
  knowledge without topology-specific mechanism engineering. Multiple predecessors
  can imply the same conclusion; multiple conclusions from same fact — both handled.
- OPEN gaps for later:
  - Fan-in F > 1 (dual axis): multiple predecessors pointing to same successor.
    This cell tests fan-OUT; fan-IN is a natural next extension.
  - Cyclic-graph (out of scope per director spawn prompt; would introduce infinite composition).
  - DAG composition-depth L > 1 (multi-hop on branching graph): requires additional
    cell (traversal + branch-select mechanism).
- If HARD_FAIL: META atom's topology-free claim honestly SCOPED to linear chains
  (L=1-20 with single-successor). Topology dependency becomes a research question.
