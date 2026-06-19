# Testbed session state and plan (filed 2026-05-30)

Persistent state file written BEFORE context compaction. Read this FIRST on session resume.

**2026-05-30 UPDATE:** Experiment-side handoff received — testbed priorities reshaped.
Read `testbed/EXPERIMENT_SIDE_HANDOFF_2026-05-30.md` for the new priority order.
Old T7 (LLM-substrate integration) is now **Priority 1** (Pattern B + Path B multi-hop).
Most of Tier 2 (T2/T3/T4) is shipped; T5 async cert remains. Currently in **verdict-wait**
mode for experiment-side P1/P2/Q1/Q2/Q3 (24-48h horizon) before committing to multi-week
P1 engineering.

**2026-05-30 UPDATE 2:** User filed comprehensive 14-item testbed track queue
(6 tracks: multi-hop perf, critical-op timing, MH capability extension, prod
stress, comparison battery, optimization). See
`testbed/TESTBED_TRACK_QUEUE_2026-05-30.md`. Six items are READY (no
experiment-side dependency); eight are BLOCKED on multi-hop primitives or
verdicts.

**2026-05-30 UPDATE 3:** v288 cap_map shifted production multi-hop mechanism
from Path B to **Path D (Bayesian path-probability propagation)**. New queue
v2 filed at `testbed/TESTBED_TRACK_QUEUE_v2_PATH_D_2026-05-30.md` with 8 new
Path-D-focused Tier-3-5 items (T10 posterior max opt, T11 batch parallelism,
T12 GPU, T13 cached priors, T17 hybrid extreme depth, T18 sustained workload,
T19 vector DB comparison, T21 multi-tenant) + 3 cross-track items (T14
mixed-confidence, T15 edit isolation, T22 N=16384). Multi-hop items wait on
S2 latency_crossover verdict (experiment-session) and/or Path D primitives in
testbed/. Q3/Q4/Q11 parallel-track READY items unchanged.

**Recommended cadence:** Hold for N=16384 envelope bench (in flight) ->
launch Q3 (composition latency, pre-authorized) -> start Q4 in parallel ->
monitor S2 verdict for T10 unblock.

**2026-05-30 UPDATE 4 — N=16384 ENVELOPE RESULT LANDED:**
Bench finished at 22:39 local after 11.5h wall (vs 45-90 min estimate, 8-15x
underestimate). Result: `max_M_at_95_recall = 8192 = N/2` at N=16384,
**2x the linear N/4 extrapolation from N<=8192**. Modern Hopfield exponential
capacity does NOT activate (no exponential bend), but envelope is super-linear
at large N. Per-cell: KF-1 near_uniform_frac=1.0 across all 4 cells, KF-2
max_iso=0.0 across all cells (killer features hold at N=16384). TCFT degrades
0.20 -> 0.66 with M; HARD_PASS only at M=N/4. See updated CAPABILITY_MAP.md
section "Recall envelope is SUPER-LINEAR at large N".

**2026-05-30 UPDATE 5 — Q3 LAUNCHED + v3 QUEUE FILED:**
Q3 (composition_latency) shipped to remote and launched as background task
bhgup5p8r. Expected wall ~3-4 hours (5 mix ratios x 100K ops x backend
substrate/faiss/dict). Per-ratio progress + partial JSON enabled per
[[feedback-testbed-progress-logging-and-restart]].

User filed v3 queue (testbed/TESTBED_TRACK_QUEUE_v3_POST_N16384_2026-05-30.md)
post-N=16384: TB1 cost model (READY, 4-6h doc work, NEXT), TB2 Pattern B with
large-N framing (BLOCKED on Path D), TB3 adversarial defense (BLOCKED on GPU 5),
TB4 multi-tenant at larger scale (READY, supersedes Q10).

**Recommended cadence:** TB1 cost model NOW (no compute contention with Q3) ->
Q4 cold/warm in parallel if time -> TB4 after hardware-feasibility check for
K=20 N=16384 -> wait on verdicts for TB2/TB3/Tier 3.

## Immediate state (what's running, what's next)

### Currently running on remote (marsh@home)
- **Bench bkqr6mzla**: `large_N_envelope` at N=16384 with M_per_N_ratios=[0.25, 0.5, 1.0, 2.0]. Config: `testbed/configs/large_N_envelope_extended.yaml`. Started ~01:30 2026-05-30. Estimated wall ~45-90 min. Memory budget ~24 GB; remote has 32 GB free.
- Will write results to `testbed_data/benchmarks/results/<ts>/per_scenario/large_N_envelope_substrate.json` with `envelope.max_M_at_95_recall_per_N` field.

### Next action (user-directed, hold-then-proceed)
USER DIRECTIVE: "hold for results then start t4."
1. WAIT for N=16384 bench notification (background task bkqr6mzla)
2. Pull report; check whether modern Hopfield exponential capacity activates at N=16384 (the empirical test of the linear-vs-exponential question)
3. Start T4 (cached retrieval layer)
4. After T4: re-run batched workloads at production scale with hashed-codebook fix (closes T2 + T3 production validation)

## Tier 2-5 plan (user verbatim, ranked)

User filed comprehensive plan in their previous message. Status as of 2026-05-30:

### Tier 2: Production engineering (performance closure)
| Test | Cost | Status | Path |
|---|---|---|---|
| T2 Hashed codebook lookup | 3-5 days | **SHIPPED** | Path 9; smoke 22.9x lift (113->2589 ops/s at N=1024 C=8192 batch=64); bit-identical W parity |
| T3 Batched operations | 1 week | **SHIPPED** | Smoke 22x (170->3723 ops/s at N=512); production validation pending T2-rerun |
| T4 Cached retrieval layer | 1-2 days | **NEXT (user-directed)** | Read-through cache; verify cached results match substrate state for audit |
| T5 Async deletion certificate | 1-2 weeks | DEFERRED | Decouple user-facing delete latency from cert generation |

### Tier 3: Cross-substrate operations
| Test | Cost | Status |
|---|---|---|
| T6 Cross-shard correlation | 1 week | DEFERRED |

### Tier 4: Product validation (load-bearing)
| Test | Cost | Status |
|---|---|---|
| T7 LLM-substrate integration (Pattern B) | 3-4 weeks + $5-20 API | DEFERRED - **THE load-bearing product positioning test** |

### Tier 5: Capacity extension (depend on experimentation)
| Test | Cost | Status |
|---|---|---|
| T8 Continuous-output validation | 3-4 weeks | DEFERRED |
| T9 Multi-signal KF-1 validation | 1-2 weeks | **PARTIAL** (Path 15 smoke: +30-50pp; HARD_PASS at saturation not met) |
| T10 Adaptive thresholds | 2-3 weeks | DEFERRED |
| T11 Block-structured W | 2 weeks | DEFERRED |
| T12 Tensor binding | 1-2 weeks | DEFERRED |
| T13 Tiered storage | 3-4 weeks | DEFERRED |

USER NOTE: "ignore t1 we're already running that experiment" (TCFT completion handled elsewhere).

## Shipped variants and scenarios (capability inventory)

### Variants (testbed/variants/)
- `v1_reference.py` - reference substrate (alias substrate_v1)
- `v2_softdelete.py` - soft erase variant
- `v3_kerdock.py` - Kerdock codebook with BSC fallback
- `v4_double_hebbian.py` - double-outer-product variant
- `sharded_substrate.py` - **K shards + shared codebook + cross-shard audit chain** (substrate_sharded). Disk constant via composition; recall craters at K*C/4.
- `factorized_substrate.py` - **U(N,M) + V(N,M) instead of dense W**. Math identity bit-exact. 5x memory at M/N=0.10. Latency win pending N>=2048.
- `hierarchical_substrate.py` - **top + K leaves with cross-level chain**. Routing 100% at smoke; capacity-extension proof needs production-scale M.

### Scenarios (testbed/scenarios/)
- `point_recall` / `edit_isolation` / `deletion_verify` / `hallu_detect` / `continual_4stage` / `storage_latency` - original 6
- `large_M_constant_cost` - M-sweep showing substrate constant vs FAISS linear (with adaptive codebook caveat)
- `audit_chain_validation` - 100 sequential deletes + SHA256 chain + 10 tamper injections. 100/100/100% substrate.
- `multi_substrate_sharding` - tests sharded variant; cross-shard chain holds at K=10 M=20K.
- `large_N_envelope` - N x M_ratio sweep; **envelope `max_M = N/4` linear**; N=16384 RUNNING.
- `write_heavy_stream` / `edit_heavy_stream` / `hot_path_skew` / `mixed_crud_workload` - realistic workloads
- `multi_signal_kf1` - Path 15; 4-signal composite KF-1; +30-50pp over single-signal
- `approx_retrieve_sweep` - Path 5; sample_frac sweep. Recall flat down to sf=0.1; latency dividend pending N>=2048
- `factorized_vs_dense` - Path 1; math-identity gate. Bit-exact across store/edit/delete.
- `hierarchical_capacity` - Path 2/19; routing accuracy + cross-level chain integrity.

### Configs (testbed/configs/)
- `default.yaml` (N=4096 M=10000), `mid.yaml` (N=2048 M=2000), `smoke.yaml` (N=512 M=64)
- `crossover_sweep.yaml` - storage_latency M=[2k,5k,10k,20k]
- `M10k_full.yaml`, `realistic_workloads.yaml`, `workloads_batched.yaml`
- `shine.yaml` - large_M + audit_chain (Aug shine adds)
- `shard.yaml`, `shard_smoke.yaml` - sharded substrate
- `large_N_envelope.yaml`, `large_N_envelope_smoke.yaml`, `large_N_envelope_extended.yaml` (N=16384 - RUNNING)
- `approx_retrieve.yaml`, `approx_retrieve_smoke.yaml`
- `multi_signal_kf1.yaml`
- `factorized.yaml`, `factorized_smoke.yaml`
- `hierarchical.yaml`, `hierarchical_smoke.yaml`
- `sweeps/grid_explore.yaml`, `grid_substrate_optim.yaml`, `grid_variants.yaml`

## Empirical findings (capability map summary)

Detailed in `testbed/CAPABILITY_MAP.md`. Key reference numbers:

### Proven via implementation
- **Audit chain integrity 100%** (single + sharded; 10/10 tamper injections caught)
- **TCFT var_ratio = 0.0566** at N=2048 (HARD_PASS threshold 0.10)
- **Edit isolation max_iso = 0.0000** + within_theory_frac = 1.00
- **Sharded substrate disk constant** at 235 MB across M=2K-20K (1% growth) with K=10 C=8192
- **Single-substrate envelope max_M = N/4 at 95% recall** strictly linear in N=2048,4096,8192
- **Hashed codebook 22.9x lift** at N=1024 C=8192 batch=64
- **Factorized substrate math identity bit-exact** + 5x memory at M/N=0.10
- **Hierarchical routing 100%** at smoke + cross-level chain 100% (110/110 anchors)

### Failed hypotheses (honest negatives)
1. "100K facts single geometric space at N=16384" - NOT supported by N=2048-8192 linear scaling
2. "Batched ops 22x in production" - smoke confirmed; production blocked by codebook overhead (FIXED by hashed codebook; rerun pending)
3. "Multi-signal KF-1 90% at all regimes" - composite +30-50pp but only 32.5% at M/N=2.0
4. "BE-1 32x cost-advantage" - probe didn't exercise W magnitude (v272 catch)
5. "Hot-path advantage over FAISS" - all backends uniform per query; FAISS just has lower constant

### Open questions awaiting data
- N=16384 envelope - does modern Hopfield exponential capacity activate? (RUNNING)
- Production-scale batched throughput with hashed codebook (rerun pending)
- Approximate retrieval latency dividend at N>=2048 (pending)

## Recent commits (git history pointer)

Push to origin/main:
- `90b12e5` - tensor-factorized + hierarchical + CAPABILITY_MAP.md
- `02676e3` - Path 5 (approx retrieval) + Path 15 (multi-signal KF-1)
- `6f40cb1` - hashed codebook (Path 9)
- `c55a3fd`, `235fc01`, `919a901`, `2ebb2ad`, `edef23c`, `ca1523d`, `5e24bd9`, `91c8bc9` - earlier testbed work

## Critical user discipline from prior messages

These guide all benchmark design + reporting:
1. "Always run comparison baselines" - every scenario must run dict, FAISS, sqlite_vec, and substrate
2. "Document failure modes honestly" - failure characterization equals success characterization
3. "Audit trail integrity always" - implementation changes that break audit chain are not acceptable regardless of performance gains
4. "Killer feature regression suite" - re-run KF-1, KF-2, deletion certificate, audit chain tests after every implementation change
5. "Lock substrate config per benchmark" - N, codebook_C, beta, M fixed per run; sweep across benchmarks not within them
6. "Save raw data alongside summaries" - per-query raw data, not just aggregates

User also flagged repeatedly: be **token efficient** in responses.

## T4 (cached retrieval) implementation sketch for next session

Per user spec from Tier 2 plan:
- Read-through cache with key-to-result lookup
- Cache verifies against substrate state for audit trail (cache hits remain verifiable)
- Re-run hot_path_skew scenario with realistic Zipfian distributions
- Measurements: hot query latency (cached path), cold query latency (substrate retrieval path), cache hit rate, audit chain across cache hits
- Success criteria: hot queries below 1ms (FAISS-competitive); cache hit rate above 80% for realistic Zipfian; cached results verifiable against substrate state
- Cost: ~1-2 days

Recommended dispatch: Opus agent, single turn. Layered on `SubstrateMemory` as a wrapper or new variant. Audit-chain-preserving (cached result includes substrate state hash for verification on read).

## Remote environment

- Host: marsh@home (Windows PowerShell)
- Repo: C:\dev\hd-instrument\
- Python: .\.venv\Scripts\python.exe
- Memory: 64 GB total, ~32 GB free during N=16384 bench
- CPU: i5-12400F (12 threads, 6 cores), CPU-only (no GPU)
- Required env var: `set KMP_DUPLICATE_LIB_OK=TRUE` (faiss + torch coexistence)
- File access quirks: leading-underscore files can hit Windows file lock; rename to remove leading underscore
- Background tasks notify on completion; do NOT poll/sleep

## Testbed data layout (remote)

```
C:\dev\hd-instrument\testbed_data\
  substrate_state\demo\               # carved persistent substrate state
  benchmarks\results\<iso_timestamp>\
    summary.json
    report.md
    per_scenario\<scenario>_<backend>.json
  baselines\faiss_indices\, chroma_db\, sqlite_vec\
```

Local has same structure under d:/AI/hd-instrument/testbed_data/ (gitignored).

## Production validation results (added 2026-05-30 post-restart)

### T4 cached_hot_path PROD VALIDATION (N=2048 M=2000 Zipfian alpha=1.2)
- substrate_cached: hot=1770us cold=8568us hit_rate=86.32% verification_failures=0 (audit holds)
- substrate (uncached): 7142us uniform
- faiss: 708us uniform
- dict: 11114us
- Findings: cache hit rate clears 80% target; 4x lift over uncached; misses <1ms stretch goal at N=2048 (smoke at N=512 was 85us). Audit integrity preserved.

### T2+T3 batched workloads PROD VALIDATION (N=1024 M=5000 batch=64)
- substrate write_heavy: 4419 ops/s (from 170 original, 113 broken-batched -> 26x lift)
- substrate mixed_crud: 131 ops/s (from 45 -> 2.9x lift)
- faiss write_heavy: 116,542 ops/s
- Substrate now 26x slower than FAISS on write_heavy (was 260x before hashed codebook). Gap closed dramatically.
- Smoke 22.9x lift HELD at production scale.

### N=16384 envelope STILL RUNNING (bench 3 of chain b29dfhv12)
- Will answer modern Hopfield exponential capacity question
- Expected wall ~45-90 min; ~30 min elapsed at last check

## End of state file. Repo SHA at write: 90b12e5 + later commits 4803c0c (T4)
