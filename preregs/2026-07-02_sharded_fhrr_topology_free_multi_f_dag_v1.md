# Pre-reg: sharded_fhrr_topology_free_multi_f_dag_v1

Date: 2026-07-02
Anchor: `sharded_fhrr_topology_free_multi_f_dag_v1`
Cell: `experiments/exp_sharded_fhrr_topology_free_multi_f_dag_v1.py`
Stage: 1 (substrate-physics primitive; extension of META CG_LAW)
Author: exp_dev (spawned by Director 2026-07-02)

## Motivation

`sharded_fhrr_topology_free_dag_extension_v1` (this session, CG a270f4d2) verified
the SHARDED-vs-BUNDLE discriminator at DAG fan-out F=4 (extending the prior CG
META atom `META_STORAGE_STRATEGY_COMPOSITION_DEPTH_PHYSICS_LAW_v1` beyond linear
chains). Skunkworks preliminary judgment (a19d86c6): **F=4 alone is one axis;
full `TOPOLOGY_FREE_SUBSTRATE_PHYSICS_LAW` META promotion requires >= 3 distinct
DAG variants + a mixed-topology case.**

This cell provides the multi-variant evidence base:

  F=1      : positive control (linear-chain reproduction)
  F=2      : small branching
  F=4      : matches prior CG DAG cell (reproducibility)
  F=8      : deep branching stress
  F=MIXED  : per-src fan-out ~ Uniform({1,2,4,8}) -- realistic DAG topology

If HP holds across ALL {F=2, F=4, F=8, MIXED} at NPROP=5000 N=8192, the storage-
strategy law is verified across a third orthogonal axis (SCALE + COMPOSITION_DEPTH
+ TOPOLOGY), and Skunkworks likely promotes META to `TOPOLOGY_FREE_SUBSTRATE_
PHYSICS_LAW` tier.

## Prior-work check (substrate-KB concept-query)

Query: `DAG topology fan-in factor mixed branching sharded FHRR variants`
Top-5 cosine (max 0.2188):
  1. `1.1 Shard Typology` cosine=0.2188
  2. `B3. Topological invariants` cosine=0.2178
  3. `Branching tree` cosine=0.2139
  4. `5.2 Two variants` cosine=0.209
  5. `Recipe Variants` cosine=0.209

Verdict: **NONE above cosine 0.30.** Metadata-index KB does not surface prior arc
above the noise floor. Known on-disk siblings via filename match:
  - `exp_sharded_fhrr_topology_free_dag_extension_v1.py` (prior CG at F=4; **this cell is DIRECT EXTENSION**, not rediscovery).
  - `exp_sharded_fhrr_cleanup_capacity_beyond_bundle_bound_v1.py` (prior CG at linear F=1).
  - `exp_sharded_fhrr_capacity_scale_free_extension_N16384_v1.py` (prior CG at scale axis).

**This cell is a scope-extension along the topology axis; NOT a rediscovery.**

## Discriminator

**Load-bearing question:** at N=8192, does SHARDED cleanly retrieve target vectors
across a batch of >= 4 distinct DAG variants (F=2, 4, 8, MIXED) while BUNDLE
collapses per Plate 1995 bound at each variant's NRULES?

- SHARDED arm: per-edge codebook `rule[edge_idx] = cnorm(props[src]*POS[pos]*IMPL*props[dst])`;
  query by `edge_idx` -> shard lookup + 3-unbind + matched-filter argmax cleanup vs props.
- BUNDLE arm (positive control): single vector `S = sum_edge cnorm(...)`;
  predicted collapse at NRULES ~ 0.14 * N = 1147 for N=8192.

At F=8, NPROP=5000: NRULES = 40000 = 34.9x bundle bound. BUNDLE must collapse.
At F=MIXED, NPROP=5000: NRULES ~ 18750 (avg F=3.75) = 16.4x bundle bound. BUNDLE collapses.

**Cross-axis test:** does the storage-strategy law extend from L=1-20 linear +
F=4 DAG (prior CG cells) to F in {2, 4, 8, MIXED} DAG topology (this cell)?
Success => full TOPOLOGY_FREE META promotion.

## Pre-registered bands

- **HARD_PASS:** SHARDED acc >= 0.85 at ALL {F=2, F=4, F=8, MIXED} at NPROP=5000 N=8192
  AND BUNDLE acc < 0.10 at F=8 NPROP=5000 (highest-NRULES gate)
  AND F=1 positive control SHARDED >= 0.85 at NPROP=5000 (Gate D reproduction).
  **META topology-free evidence SATISFIED across 4 distinct DAG variants** =>
  Skunkworks likely promotes META to `TOPOLOGY_FREE_SUBSTRATE_PHYSICS_LAW`.
- **MIDDLE_BAND:** SHARDED in [0.60, 0.85) at any of {F=2, 4, 8, MIXED} at NPROP=5000;
  partial topology extension; would require regime probe or scope amendment.
- **HARD_FAIL:** SHARDED < 0.60 at any of {F=2, 4, 8, MIXED} at NPROP=5000.
  **META topology-free CLAIM SCOPE-BOUNDED**; law does NOT hold at that F variant;
  Skunkworks demotes META to specific-topology scope + records failure mode as
  named DAG-topology gap.
- **HARD_FAIL (Gate D):** F=1 positive control SHARDED < 0.85 at NPROP=5000 =>
  cell mechanism drift; downstream multi-F conclusion UNRELIABLE.

## Grid + arms

FULL grid: F in {1, 2, 4, 8, MIXED} x NPROP in {200, 1000, 5000} = **15 phase points**.
Smoke grid: F in {1, 8, MIXED} x NPROP in {200, 5000} = **6 phase points at full-N N=8192**
  (per DISCRIMINATOR-MUST-SURVIVE-SCALE rule A: fires discriminator at new axes F=8 + MIXED).

Arms per phase point: SHARDED, BUNDLE (2 arms).
N=8192 fixed. M=200 queries per (F, NPROP) phase point FULL / M=30 smoke.
FULL run: 3 seeds via 3 separate queue entries (seed=7, 13, 19) chunked per META_RULE §13.

## Smoke design (discriminator-must-survive-scale)

Smoke fires the discriminator at the NEW axes (F=8, MIXED) at NPROP=5000 N=8192.
Preview arm at F=8 NPROP=5000 N=8192 verifies SHARDED-BUNDLE gap AT FULL PARAMETERS
before FULL dispatch (per DISCRIMINATOR-MUST-SURVIVE-SCALE rule A + rule C).

Expected smoke wall: ~5-15s CPU (M=30, 6 phase points; heaviest is F=8 NPROP=5000).

**MEASURED@d:/AI/hd-instrument/data/exp_sharded_fhrr_topology_free_multi_f_dag_v1/metrics.json (smoke, 2026-07-02, CPU, seed=7):**
  - F=1     NPROP=200:  sharded=1.000 bundle=0.7333 (baseline in-band; below bound)
  - F=1     NPROP=5000: sharded=1.000 bundle=0.0000 (**positive control Gate D HP satisfied**)
  - F=8     NPROP=200:  sharded=1.000 bundle=0.5667 (baseline in-band; F=8 sanity)
  - F=8     NPROP=5000: sharded=1.000 bundle=0.0000 (**F=8 stress HP gate satisfied**)
  - F=MIXED NPROP=200:  sharded=1.000 bundle=0.7333 (baseline in-band)
  - F=MIXED NPROP=5000: sharded=1.000 bundle=0.0000 (**MIXED HP gate satisfied**)

**Smoke wall: 13.1s CPU.** Discriminator gap 1.000 - 0.000 = 1.000 at all HP gates.
Selftest at reduced N=4096 also PASS (F=8 gap 0.967, F=MIXED gap 0.933). FULL dispatch authorized.

## Discipline gates (SCHEMA-VET / META_RULE)

| Gate | Value | Notes |
|------|-------|-------|
| `cardinality_ok` (META_RULE_H) | `len(per_unit) == 15 FULL / 6 smoke` | Verdict logic gates on HP gate points presence in per_unit. |
| `arms_differ_verified` (META_RULE_AF) | True | SHA-256 hash of first-batch shard bytes vs bundle_vec bytes per phase point; assert distinct. |
| `final_metrics_atomicity` (META_RULE_AH) | `tmp_replace` (via `write_metrics` + `_write_crash_metrics` uses tmp+os.replace) | |
| `except SystemExit: raise` before `except Exception` | Present | Outer try/except with SystemExit + KeyboardInterrupt pass-through. |
| `crlb_floor_computed` | N/A per matched-filter regime | Cell measures P(argmax correct) over V=NPROP codebook; no continuous parameter estimation. |
| `crlb_n/a` reason | Categorical argmax not Cramer-Rao; capacity is codebook-argmax vs matched-filter SNR. | |
| `discriminator_reachability` | True | HYPOTHESIZED@this-file: at F=8 NPROP=5000 N=8192, matched-filter SNR ~ sqrt(N)/sqrt(3-bind noise) ~ 90/1.7 ~ 52; argmax over V=5000 saturates cleanup. Prior DAG cell MEASURED sharded=1.000 at F=4 NPROP=5000; expected similar at F=8. |
| `baseline_in_band` (META_RULE_AG) | Both arms verified in-band across grid | SHARDED expected ~1.0 across full grid at N=8192. BUNDLE crosses discriminating band 0.5 -> 0.03 across NPROP axis. |
| `cell_chunked` | True | Single-seed-per-cell; 3 FULL seeds via 3 separate queue entries. |
| `start_marker_written` | True | `_start_marker.json` at main() entry, atomic. |
| `crash_diagnostic_present` | True | `_write_crash_metrics()` on Exception; tmp+os.replace. |
| `heartbeat_present` | False (optional) | 15 phase points; est ~30-90s per seed on GPU (M=200 x 2 arms x 15 pts, heaviest at F=8 NPROP=5000). Per-phase-point `print(..., flush=True)` provides audit. |
| `defensive_error_checking` | `passed_all_4_patterns` (start_marker + crash_diag + progress-flush + arms_differ_hash) | |
| `progress_logging` (§17) | `print_flush_true` + `sys.stdout.reconfigure(line_buffering=True)` at cell entry. Per-phase-point print line + flush. Timeout gate 1800s but expected wall < 300s. |
| `calibration_check` (META_RULE_M) | `default_ok_for_this_regime` | FHRR complex64 unit-modulus; no encoder-specific calibration. |
| Sweep alignment (§15A) | ALIGNED | 2-axis sweep (F, NPROP); F axis is the mechanism variable itself. No compositional effective-vs-nominal ambiguity. |
| Discriminating fraction (§15B) | HYPOTHESIZED 15/15 in discriminating band (SHARDED-BUNDLE gap spans 0.5 -> 0.97 across grid). |
| Composition edges (§15C) | N/A single-primitive cell | No cross-primitive composition; rule is a single 3-bind + cleanup mechanism. |
| Positive control (§15D) | F=1 row serves as positive control (linear-chain reproduction under uniform 3-bind mechanism). Cited prior atom: `sharded_fhrr_topology_free_dag_extension_v1` F=1 NPROP=5000 MEASURED sharded=1.000. Tolerance: SHARDED >= 0.85 at F=1 NPROP=5000. |
| Functional requirements (§15E) | (1) SHARDED discriminates under multi-F DAG variants (topology-free extension); (2) BUNDLE collapses per Plate bound at each F NRULES >> bound (positive control); (3) F=1 reproduces prior linear-chain regime (Gate D). All mapped to arm design. |

## Compute architecture (USER 2026-07-02 mandatory declaration)

**Class:** batched-GPU (torch complex64, auto CUDA-detect, batched cleanup matmul,
batched build via edge-groups of size 2000).

**Storage strategy:** sharded (per META CG_LAW being extended); bundle arm is
positive control.

**Rationale:** cleanup at (M=200, N=8192, V=NPROP=5000) is a matmul of ~8.2e9
complex ops per phase point. On CPU numpy would be ~15-30s per matmul (sequential-CPU
untenable); on GPU torch ~0.1-0.5s. Total FULL wall (15 pts x 2 arms x 200 queries):
~30-90s per seed on CUDA. CPU-torch FULL wall estimate ~2-4 min per seed. Batched-GPU
class chosen per USER-locked 2026-07-02 GPU-batching mandate.

**Peak GPU VRAM at F=8, NPROP=5000, N=8192 (highest-NRULES point):**
  - codebook (NRULES=40000, N=8192) complex64 = 2.62 GB
  - props (NPROP=5000, N=8192) complex64 = 328 MB
  - POS (F_POS_MAX=8, N=8192) complex64 = 512 KB
  - Build batch peak (B=2000, N complex64) = 131 MB transient
  - Cleanup query (M=200, N=8192) = 13 MB
  - Chunked cleanup V-slice (CV=2000, N=8192) = 131 MB transient
  - **Peak GPU: ~3.5 GB.** Fits 8GB target with ~4 GB headroom.

Cell issues `torch.cuda.empty_cache()` after each build batch + each phase point +
`del` of large tensors. `torch.cuda.max_memory_allocated()` logged per phase point.

**Peak CPU RAM:** ~700 MB (build_dag ragged Python lists + torch overhead + numpy
tobytes for arm-differ hash). marsh@home has ample CPU RAM.

**Fallback:** if `torch.cuda.is_available() == False`, cell runs on CPU-torch
(still batched matmul; wall ~2-4 min per seed).

## Timeout estimate

- Selftest: ~10-20s on CPU (reduced N=4096, 3 phase points at F=1/8/MIXED, NPROP=200/1000).
- Smoke: ~5-15s CPU (6 phase points at full N=8192, M=30).
- FULL (per seed): ~30-90s on GPU (batched); ~2-4 min on CPU-torch.
- **Recommended `--timeout 1800` (30 min)** per FULL entry; wide margin for GPU
  queuing + first-run compilation.

## Dispatch plan

1. Self-test locally on .venv (reduced N=4096; 3-point formula assertions).
2. Smoke locally on laptop CPU at full N=8192 with F in {1,8,MIXED} x NPROP in {200,5000}.
3. Author asks Director to route 3-seed FULL to `overnight_queue` (GPU) with
   `HDLAB_SEED` env var (seed=7, 13, 19). Director dispatches via `hd_metrics_sync` push.

## Stage 1 classification

Substrate-physics primitive extension (Stage 1). Not a language / semantic test;
substrate-doesn't-know-anything rule (USER 2026-06-26) does NOT apply. Direct
scope-extension of a chain-grade META atom's named extension axis (topology).

## Multi-seed smoke rule exemption

Per META_confidence_signal_smoke_single_seed_inflates_AUC (Skunkworks CG 2026-07-02),
multi-seed smoke is mandatory for confidence/contamination cells where discriminator
is AUC over continuous scores. **This cell is EXEMPT** per that META's own exclusion
clause: "Does NOT apply to pure capacity sweeps (e.g. sharded_capacity beyond bundle
bound -- accuracy is deterministic given the mechanism)." Single-seed smoke sufficient;
per-phase-point acc is deterministic hits-over-M.

## Landing plan / CG-eligibility

Cell is HP-eligible if all 3 seeds HARD_PASS. Under HP:
- Load-bearing outcome: META atom's topology-free evidence satisfied across
  {F=2, 4, 8, MIXED} -- Skunkworks likely promotes META to
  `TOPOLOGY_FREE_SUBSTRATE_PHYSICS_LAW` tier.
- Downstream implication: M3 cortex can rely on SHARDED storage for any DAG-
  structured knowledge without topology-specific mechanism engineering (fan-out
  1-8 covered directly; MIXED covers realistic variable-fan-out KGs).
- OPEN gaps for later:
  - Fan-IN (dual axis): multiple predecessors converging on same successor node
    (this cell tests fan-OUT).
  - Cyclic-graph topology (out of scope; introduces infinite composition).
  - DAG composition-depth L > 1 (multi-hop on branching graph): requires
    additional cell (traversal + branch-select mechanism).
- If HARD_FAIL: META atom scope-bounded to failed F variant boundary
  (e.g., topology-free at F <= 4 but breaks at F=8) -- honest scope characterization.
