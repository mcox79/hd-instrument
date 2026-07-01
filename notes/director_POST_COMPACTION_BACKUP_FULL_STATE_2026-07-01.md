# Post-Compaction BACKUP — Full State 2026-07-01 (end of massive 6-CG session)

**Last updated:** 2026-07-01 ~15:35 UTC (pre-compaction snapshot)
**Audience:** Post-compaction Director + USER
**How to use:** read SNAPSHOT section first (self-contained recovery)

---

## 🎯 SNAPSHOT 2026-07-01 — END OF SESSION

### CERT + tally
- **CERT: 639 → 645** (+6 chain-grade promotions in one day; new record)
- **Session final: CG +6 / MM +16 / HF +13 + 4 amend/meta = 39 atoms + 39 ledger rows in 21 commits**

### 🎯 SIX CG PROMOTIONS (in order landed)

| # | Cell | Commit | Substantive finding |
|---|---|---|---|
| 1 | A v2 pc_sparsity × encoder capacity-lift | c7feb0c4 | M=300→M=600 escapes META_RULE_Q; fhrr uniquely sparsity-sensitive |
| 2 | E v5 INT8-Pareto-optimal specialization | 716174a7 | INT8 = FP32 within 0.0015 recall at 0.25x memory; hdlab primitive shipped |
| 3 | Cell D v2 dense-Hopfield READOUT-REPLACEMENT M=8192 | 863e14b5 | Cortex-Hebbian must be REPLACED not COMPOSED; 3.5x recall lift; cv=0.000 |
| 4 | ANCHOR4 encoder family N=16384 | 5ec1b83b | 5/5 encoders CG at 2x N; refutes v4 saturation rationale |
| 5 | Capacity multi-bank α-K HIGH-K extension | 6c6a271d | M/B (per-bank load) is real predictor NOT M/B/K_per (design falsified at smoke) |
| 6 | Cross-modal binding 4/5-modality | 4110bcd6 | Substrate supports up to 5-modality binding at CG; extends 2-modality CG |

### 🎯 M3 architecture insights + milestones

**MM_STANDARD promotions (formerly TENTATIVE):**
- **M3 architecture meta atom** promoted to MM_STANDARD (2/3 expansion criteria satisfied): (a) 3 seeds cv=0.000 ✓, (b) v2 3-seed FULL ✓, (c) cross-M validation pending
- **Binding-family capacity-axis invariance** MM_TENTATIVE (D×O + Axis J synthesis)

**Milestones landed:**
- **M3 M1.3 NoiseChannel** (c5e5e66a) — cortex-side stochastic noise injection module + 5/5 smoke tests
- **M3 M1.4 refuse-gate** — HF across v3 (mechanism class wrong) + v4 (baseline saturated) + v5 pending. NOT closed; blocker for cortex.
- **hdlab primitives shipped:** `int8_dense.py` (c3ca7dab) + `k_cliff_scaling.py` (K_cliff=0.87·N/log2(N); analytical closed-form derived via 5x-drill) + `schema_exemplar_bayes.py`

**Substrate design implications now chain-grade:**
1. INT8_DENSE Pareto-optimal at capacity-crack M∈{40k,80k} — default for WM
2. Dense-Hopfield REPLACE (not COMPOSE) cortex-Hebbian at M=8192 chain-grade
3. Binding-family axes are capacity-invariant (choose for performance not memory)
4. M/B is real capacity predictor at HIGH-K (calibrates hdlab primitives)
5. cos_margin=0.94 not 0.7 for v3 regime → adaptive β=13 (matches Cell D v2 CG observed)
6. Substrate is β-robust in [5,32] for Cell D v2 (no fine-tuning needed)

### USER-locked directives (all durable via memory)

**Substrate discipline:**
- **Substrate-KB concept-query MANDATORY before any cell/framing/assertion** — use `bash tools/substrate_query.sh "<concept>"` (auto-passes --chunk-content --schema-version v2 --tau 0.15 --k 5). Caught July 1 INT8 rediscovery (May 29 exp_kf2_be1_fp16_n8192 already had 5/5-seed HP). Discipline added to hdi_research/exp_dev/skunkworks .md files.
- **Glass-box LLM = SUBSTRATE-NATIVE language** (NOT hybrid with external LLM). Stage 4 LM equivalence is the actual endpoint. Do NOT frame M3 as "substrate as memory backend for LLM."
- **Stage-by-stage consolidation** (not big-bang): Stage 1 100% → consolidate → Stage 2 → consolidate → Stage 3. Match cadence to stage-progression discipline.

**Dispatch discipline:**
- **Local CPU: SMOKE ONLY** (rule added to hdi_exp_dev.md). Full runs to remote_cpu_queue or overnight_queue.
- **Cloud GPU: ONCE-per-STAGE final push** (NOT ongoing overflow). Bundle candidates per stage in `notes/director_cloud_gpu_bundle_candidates_2026-07-01.md`. Currently has: Cell D N-sweep (CUDA OOM at N=32768) + Batch B seqbind (Windows-capped at N=16384) + Cell D M-ultra + Cortex_hippo replace+refuse-gate v2 + Compositional gen depth-15+
- **STANDARD_* macros** for Orchestrator + Skunkworks (persistent in .md files): STANDARD_PUSH_QUEUE_VERIFY, STANDARD_REDISPATCH, STANDARD_KICKSTART, STANDARD_SSH_LANDING_PULL, STANDARD_LANDED_VET, STANDARD_SSH_VET, STANDARD_HF_CLOSURE, STANDARD_META_SYNTHESIS

**Auditor discipline:**
- **Broken positive control before structural framing** — verify flat baseline clears its own expected floor BEFORE tiering an HF as structural. Caught July 1 Axis H v2 falsification of v1 revival criterion.
- **Fix #28 recurrence at Orchestrator level** — Director sanity-check VERIFIED claims against live remote grep before propagating to USER.

**Infrastructure disciplines:**
- **PyTorch Windows does NOT support expandable_segments** (RTX 4060 Ti 8GB ceiling); cells that need N=32768+ go to cloud bundle.
- **CUDA env vars must precede torch import in wrapper** (not _core.py which imports later).
- **Ledger discipline restored** — atoms.jsonl + cert_ledger.jsonl atomic writes; 6 orphan atoms back-filled today.
- **Orphan python sweeper** shipped in hd_health_check.ps1 (runs every 15 min; auto-catches runaway pythonw > 30 min age > 100 MB with empty cmdline).

### Infrastructure improvements this arc

**Testbed shipped:**
- Orphan-python sweeper (allowlist-based; won't kill dashboard)
- queue_add.sh Pattern 5 shared framework auto-SCP
- queue_add.sh status-field grep-back verify
- back_fill_cert_ledger.py (ledger reconciliation)
- verify_atom_kind_registered.py (enum pre-write check)

**Orchestrator self-heal patterns (SH-1..SH-6):** PROT-019 timeout floor / shared-framework SCP / GPU→CPU numpy re-route / double-exp cosmetic / CUDA OOM escalation / --allow-duplicate

**Bug diagnostics found:**
- Sync-hang bug (SYSTEM-owned ssh zombies) — Testbed shipped Invoke-BoundedSsh fix (commit 22e848d2)
- Windows expandable_segments unsupported → Batch B N cap at 16384
- Cell D N-sweep CUDA OOM at N=32768 → cloud bundle candidate
- Cell D + refuse-gate META_RULE_AF false-positive when arms co-saturate (Testbed candidate)

### Current fleet state (pre-compaction ~15:35 UTC)

**Queues:**
- **overnight_queue:** 0/0 (drained; will refill when in-flight cell-authors return smokes)
- **remote_cpu_queue:** ~13 pending (sparsity_free ×3 + cortex_hippo_M_sweep_v3 ×3 + P 3-tier v1p1 seeds + population coding + CRISPR slab-replay + KG encoder + refuse V_REL sweep + multihop hint-alt + TASK_VECTOR K-extended + others)
- **local_cpu_queue:** DISABLED + pause flag (USER laptop safety)

**Sub-agents in flight (~4-6):**
- Skunkworks (standby for landings VET)
- Orchestrator (standby for push+queue events)
- Cell-authors: refuse V_REL sweep (a449526f done; queued), TASK_VECTOR K-extended (a34791d0 done; queued), cross-modal 4/5 CG'd, multihop hint alt (a135c556 done; queued), Cell D beta (MM'd)

**Landings pending VET or FULL run:**
- theta-gamma v3 N=16384 3-seed
- P 3-tier v1p1 3-seed (long CPU wall)
- population coding 3-seed CG-lift
- CRISPR slab-replay 3-seed (transfer +0.200 vs 0.000; Stage 1 CG-lift candidate)
- KG ingest encoder family (smoke was in flight)
- Multihop hint alternatives (attention-hint substantive 0.38)
- TASK_VECTOR K-extended (cliff cross K=1000-2000)
- Refuse-gate V_REL sweep (smoke HP)

### Immediate priorities for post-compaction session

1. **HIGHEST: Wait for landing VETs from cooking cells** — theta-gamma v3, P 3-tier, population coding, CRISPR slab-replay — any could be 7th+ CG
2. **HIGH: M3 M1.4 refuse-gate closure** — 3 attempts today all HF; may need mechanism-class research drill (conformal prediction / SDT 2-sided ROC / M3-cortex-external calibrator)
3. **MEDIUM: Stage 1 shoring cells continuing** — population coding CG-lift, CRISPR slab-replay CG-lift, capacity multi-bank now CG (extending toward 100% Stage 1)
4. **MEDIUM: Continue Stage 3 breadth** — TASK_VECTOR K-extended, multihop hint-alternatives, cross-modal 4/5 (already CG)
5. **LOWER: Cloud GPU bundle** — deferred until Stage complete per USER-locked policy

### Recovery ritual (for post-compaction session)

```bash
# 1. Heartbeat
date -u +"%Y-%m-%dT%H:%M:%SZ" > d:/AI/hd-instrument/data/heartbeats/research.timestamp

# 2. Query substrate for post-compaction docs (concept-check discipline)
bash tools/substrate_query.sh "post compaction backup 2026-07-01 six CG day"

# 3. READ THIS FILE END-TO-END (self-contained recovery)

# 4. Check landings since 15:35 UTC
find d:/AI/hd-instrument/data -maxdepth 2 -name metrics.json -mmin -60

# 5. Check remote runners alive
python tools/runner_status.py --remote

# 6. Check queue depths
python -c "import json; e=json.load(open(r'd:/AI/hd-instrument/data/local_cpu_queue/queue.json'))['experiments']; print('local:', sum(1 for x in e if x.get('status')=='pending'))"
# similar via SSH for remote_cpu_queue + overnight_queue
```

### Memory rules filed this arc (all durable via ~/.claude/projects/d--AI/memory/)

- `feedback_substrate_kb_query_needs_v2_schema_flags_2026-07-01.md` (INT8 rediscovery caught)
- `feedback_use_standard_macros_hdi_orchestrator_skunkworks_2026-07-01.md` (token efficiency)
- `feedback_auditor_flag_broken_pc_before_structural_framing_2026-07-01.md` (Axis H false structural framing)
- `feedback_smoke_only_local_cpu_no_full_dispatches_USER_LOCKED_2026-07-01.md`
- `feedback_cloud_gpu_once_per_stage_last_run_USER_LOCKED_2026-07-01.md`
- `feedback_cuda_env_var_must_precede_torch_import_import_order_2026-07-01.md`
- `feedback_orchestrator_verified_hallucination_fix28_recurrence_2026-07-01.md`
- `reference_pytorch_windows_expandable_segments_unavailable_2026-07-01.md`
- `project_glass_box_LLM_substrate_native_language_no_external_LLM_USER_LOCKED_2026-07-01.md` (KEY: language is substrate-native, NOT hybrid)

### Historical prior CG count trajectory

- 2026-06-28 end: CERT ~625
- 2026-06-30 end: CERT ~639 (+14 across arc)
- **2026-07-01 end: CERT 645 (+6 today = record single-day)**

### Session honest read

Today was the strongest single-day performance of the project. Six chain-grade promotions covering: sparsity × encoder (Stage 1), INT8-Pareto-optimal (Stage 2 storage), dense-Hopfield replacement (Stage 2/M3 architecture), encoder N=16384 (Stage 1 scaling), capacity multi-bank HIGH-K (Stage 1), cross-modal 4/5-modality (Stage 3). Plus M3 architecture meta atom promoted to MM_STANDARD, M1.3 NoiseChannel shipped, hdlab primitives (INT8, K_cliff formula), and substantive design guidance from cell-author + Skunkworks honest catches. Also caught significant methodology gaps: INT8 rediscovery (substrate-KB query discipline gap now fixed with wrapper + agent rule updates); auditor structural-framing bias (Axis H self-critique); Fix #28 recurrence at Orchestrator level.

The substrate is now materially closer to Stage 1 complete + Stage 2 60-70% + Stage 3 building broadly. M3 architecture direction (dense-Hopfield READ-REPLACE) validated at chain-grade — this is the load-bearing insight for the next 6-18 months of cortex-layer development.

M1.4 refuse-gate remains the sharpest current blocker for M3 milestone closure; consider mechanism-class research drill in next session if v5 (still in flight or blocked) doesn't close it.

---

*(Historical BACKUPs from prior days retained below for reference; SNAPSHOT above is self-contained.)*
