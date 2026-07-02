# POST-COMPACTION BACKUP — 2026-07-02 late afternoon session

**Filed:** 2026-07-02 ~13:45 UTC (context at 9% per USER)
**Session type:** post-post-compaction continuation from 2026-07-01 late-night + 2026-07-02 full-day session
**Supersedes:** `notes/director_POST_COMPACTION_BACKUP_FULL_STATE_2026-07-01_LATE.md`

---

## 🚨 READ FIRST AFTER COMPACTION

```bash
# 1. Heartbeat
date -u +"%Y-%m-%dT%H:%M:%SZ" > d:/AI/hd-instrument/data/heartbeats/research.timestamp

# 2. Read THIS file end-to-end (self-contained)

# 3. Check recent landings
find d:/AI/hd-instrument/data -maxdepth 2 -name metrics.json -mmin -60

# 4. Verify queue state
python d:/AI/hd-instrument/tools/runner_status.py --remote

# 5. Check for sub-agent task-notifications (they'll fire in-context)
```

---

## SESSION SNAPSHOT

### CERT (Testbed-audited today, load-bearing)
- **CERT actual: 662 → ~699** (Testbed ledger audit today: 42 session atoms; **17 CG + 15 MM + 2 DEMOTE + 2 DISCIPLINE + 1 MB**)
- My prior narrative said "26 CG" — WRONG. Correct is 17 CG per disk.
- Session synthesis note (see below) needs revision to reflect audited numbers.

### Strategic drills this session (9/9 done + 1 paradigm drill)
All filed to `notes/`:
- Testbed calibration audit — Sonnet drills over-estimate fragility 2-10×; R1 mechanism-verify mandatory
- Sonnet OOD — compositional-query P(success)=0.15-0.25; needs cortex decomposition
- Sonnet M4 — EVALUATE-OUTCOME primitive can start NOW (P_CG=0.45); M4 realistic mo 20-26
- Sonnet LTM consolidation — M1.5 TWO-TIER doesn't specify trigger; explicit-mark trivial 2-3 day ship
- Sonnet hybrid runtime — **ARCHITECTURALLY WRONG per USER 2026-07-01 lock** (no LLM hybrid); reframe under substrate-native
- Sonnet failure taxonomy — h4_cluster_density_confidence_calibration_v1 highest-leverage cheap
- Skunkworks cross-atom audit — methodology issues; not critical
- Skunkworks salvage VET — +2 CERT (commercial_M v1 MM + salvage discipline META MM)
- Testbed ledger integrity — 42 session atoms; **17 CG; ledger structurally sound**
- **Sonnet VRC paradigm drill — proposed OPTIMAL substrate-native LM eval; PCRA + SRR + MHCA metrics; cell design ready**

### USER-locked directives (durable memory)
NEW today:
- `feedback_gpu_batching_mandatory_when_speedup_available_USER_LOCKED_2026-07-02.md` — for ANY cell where GPU batching gives speedup, MUST batch on GPU. Dim I A2 lost 12h to CPU-sequential loop when GPU-batched would be 30 min.

Standing durable rules (from MEMORY.md still in force):
- Glass-box LLM = SUBSTRATE-NATIVE language (2026-07-01) — NOT hybrid with external LLM. Substrate does everything an LLM does INCLUDING language generation.
- Substrate doesn't know anything — build understanding before language testing (2026-06-26).
- Cloud GPU = once-per-stage final push (2026-07-01).
- SMOKE only on local_cpu_queue (2026-07-01).

### USER's active direction (this session)
- LLM ingestion strategy: **step 1 = digest existing LLMs to feed into substrate**. Do NOT force into pre-existing benchmarks (BPC, perplexity). If new paradigm needed, invent it.
- Cortex is required for basically every conversational failure mode — **integration debt is the M3 bottleneck**. Build `hdlab/cortex.py` composed module.
- Don't accept LLM hybrid architecture right now.

---

## IN-FLIGHT SUB-AGENTS (post-compaction task-notifications will fire)

- **a4afe99ee9a1a9814** (hdi_exp_dev) — VRC paradigm validation cell `vrc_paradigm_validation_pcra_mhca_srr_v1` authoring
- **a473ccc4d1c0f4e54** (hdi_orchestrator) — kill+salvage done for Dim I A2; also authoring `hrr_depth_budget_curve_v2_gpu_batched` per USER's GPU-batching discipline
- **aed89662e49752fc2** (hdi_orchestrator) — diagnosing Dim L v1 seed_19 GPU utilization (suspected CPU-bottleneck-on-GPU-host)

---

## QUEUE STATE (as of 13:45 UTC)

### remote_cpu_queue
- Running: Dim T joint-surface seed_13 (started 09:42Z)
- Pending: Dim T seed_19, M1.4 v9 seed_7, M1.4 v9 seed_13, M1.4 v9 seed_19
- CLARIFY 3 seeds show `run_mode: self_test` on disk (NOT full — same META_RULE_U pattern as INT2 v1 today). Full runs are still pending.

### overnight_queue
- Running: Dim L v1 seed_19 (started ~1h ago; likely CPU-bottleneck; will hit 7200s timeout if pattern from seed_7+13 holds)
- Pending (12 cells): Dim L v2 × 3 (incremental checkpoint fix), cross-axis β=5 × 3, commercial_M v2 timeout-fixed × 3, Dim F batched QPS × 3

### local_cpu_queue
- SMOKE ONLY per USER 2026-07-01 lock. Empty otherwise.

---

## LOAD-BEARING PENDING DECISIONS FOR USER

1. **VRC paradigm validation cell — dispatch decision** (once cell-author returns). Novel evaluation methodology; not-BPC-benchmark; likely CG at P_def=0.75.
2. **Dim L v1 seed_19 kill decision** (pending GPU util diagnostic). Same CPU-bottleneck pattern as Dim I A2 today likely.
3. **h4_cluster_density_confidence_calibration_v1 dispatch** — pre-reg exists un-dispatched; failure taxonomy identified as highest-leverage cheap cell.
4. **`hdlab/cortex.py` composed module + integration test cell** — cortex integration debt; USER proposed authoring; awaiting go/no-go.
5. **Language ingest infrastructure (per drill 3):** 3 blocking hdlab modules needed (~2.5 days) before language cells can run: `lm_eval_harness.py` (META_M7), `token_vocab.py`, `bigram_gap_measurement.py`. Dispatch as USER direction.
6. **Cortex integration architecture:** substrate-native only (no LLM). Drills that assumed LLM router in the loop (Hybrid runtime, OOD Phase 1 fallback claim, M4 director) need reframing under substrate-native constraint.

---

## PRIOR ARC NOT LOOKED AT THIS SESSION

- **Substrate-vs-LLM head-to-head math wins (multiple CGs):** substrate <100MB beats Qwen 0.5B/1.5B/3B on 2-3 of 4 math benchmarks; substrate 1000× faster; substrate 0 false-accepts vs LLM 1 (soundness gap CG).
- **n1_v3 substrate LM CG** at top1=0.4455 (+61.6% lift over unigram) — reference for VRC/language cells
- **Language ingest drill 1 (vocab_scale) + drill 2 (segmentation) + drill 3 (pipeline composition):** notes filed 2026-06-26; ANCHOR_1 blocked on 2.5-day infra build
- **2026-06-23 RIGGED-HARNESS finding:** 7+ prior BPC HFs were methodology-confound. Cert ledger row 698 documents.

---

## KEY DISK ARTIFACTS

- Session synthesis (needs revision for 17-CG not 26-CG): `notes/session_synthesis_M3_architecture_readiness_2026-07-02.md`
- Testbed calibration audit: `notes/testbed_sonnet_drill_calibration_audit_2026-07-02.md`
- Testbed ledger integrity: — filed as agent report, not .md
- VRC paradigm drill: `notes/research_optimal_substrate_native_lm_evaluation_paradigm_2026-07-02.md`
- OOD drill: `notes/research_ood_compositional_generalization_for_M3_2026-07-02.md`
- Failure taxonomy: `notes/research_conversational_failure_mode_taxonomy_M3_2026-07-02.md`
- LTM consolidation: `notes/research_ltm_consolidation_cortex_across_days_weeks_2026-07-02.md`
- M4 director: `notes/research_M4_substrate_as_experiment_director_2026-07-02.md`
- Hybrid runtime (ARCHITECTURALLY INVALID under substrate-native lock): `notes/research_llm_substrate_hybrid_runtime_api_M3_phase_1_2026-07-02.md`
- Language ingest drill 3: `notes/exp_dev_handoff_research_language_ingest_drill3_pipeline_composition_substrate_native_2026-06-26.md`
- Dim I A2 salvage partial: `d:/AI/hd-instrument/data/exp_hrr_depth_budget_curve_v1/partial_metrics.json` (167/504 arms; seed_7 only)
- Commercial_M v1 salvage partials: `d:/AI/hd-instrument/data/exp_stage2_commercial_M_latency_percentiles_v1_seed_{7,13,19}/partial_metrics.json`

---

## POST-COMPACTION IMMEDIATE PRIORITIES

1. Verify VRC cell-author (a4afe99ee9a1a9814) return + dispatch decision
2. Verify Dim I A2 salvage cell-author (a473ccc4d1c0f4e54) v2 GPU-batched return + dispatch
3. Verify Dim L v1 seed_19 GPU util diagnostic (aed89662e49752fc2) + kill decision
4. Skunkworks batch VET on Dim T seed_13 landing (when it lands)
5. Cortex integration proposal — awaiting USER go/no-go
6. GPU-batching discipline: audit other cells in queue for CPU-bottleneck-on-GPU-host pattern

---

*(Self-contained BACKUP — post-compaction session has everything needed to continue. Written at ~9% context per USER's interface.)*
