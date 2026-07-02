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
- **CERT actual: 662 → ~703** (Testbed audit + post-compaction Skunkworks batch VET + VRC paradigm CG + h4 HF: 47 session atoms; **21 CG + 15 MM + 2 DEMOTE + 2 DISCIPLINE + 1 MB + 1 HF**)
- **UPDATE (post-BACKUP-filing during compaction window): +4 tier changes:**
  - M1.8 CLARIFY 5-primitive stack 3-seed FULL — **CG** (5th cortex primitive closes)
  - M1.4 v9 joint-alpha-sigma-surface-controller 3-seed FULL — **CG** (v9 lifts low-load useful_recall 0.0→0.72-0.82; cv=0.066 marginal but honest)
  - Dim T joint-surface interaction 3-seed — **CG** (delta_sigma_crit cv=0.015 excellent; seed_7 ran as smoke-mode per config, transparently characterized)
  - VRC paradigm validation PCRA/MHCA/SRR 3-seed FULL — **CG paradigm_launch** (first substrate-native LM eval primitive; PCRA gap 0.996 / MHCA gap 1.000 / SRR clean; τ cv=0.0022; opens Cells 2-5 of substrate-native LM roadmap)
  - h4 cluster_density_confidence_calibration 3-seed FULL — **HF_STRUCTURAL_BOUND** (AUC=0.528 chance at commercial-scale; global mean-clipped-cosine density drowns in noise floor at M=3600; smoke was band-floor adjacent 0.757 vs 0.7575 strict-floor — should have blocked full dispatch per USER 2026-06-26 discriminator-must-survive-scale)
- **h4 revival drill returned** (a66bd7): top pick was h4b top-1/top-2 gap (P_CG=0.42); also surfaced 8-month-old un-shipped anchor `bio-calibrated-confidence-B1` (2026-06-08); 3-signal cortex confidence architecture proposal filed at `notes/proposal_M3_cortex_three_signal_confidence_architecture_2026-07-02.md`.
- **h4b landed smoke-HF at scale-preview** (commit 8c84c673a unpushed; agent a8b8): AUC=0.545 at N=8192/items=3600 (below 0.55 reject); cell-author correctly REFUSED FULL dispatch. Empirical closure of bio-calibrated-confidence-B1 (Ma et al 2006 population-code analog does NOT transfer to substrate at commercial N in h4-harness).
- **REGIME CAVEAT surfaced**: 2 mechanism classes now HF at same h4-harness regime (INTRA_COS=0.6, PER=60, M=3600, contam ~4.6%). Cell-author (h4b) hypothesized regime-not-mechanism confound. Regime-vs-mechanism research drill in flight (ac7fa91; reissued after first agent a743 no-op'd). If REGIME_CONFOUND: reframe confidence task at higher contam fraction OR different discriminator BEFORE Lane X + lap3_12.
- **Sharded_fhrr_cleanup_capacity_beyond_bundle_bound_v1** cell-author in flight (a13877) — Stage 1 substrate-physics probe; hidden CG candidate from math4 smoke NPROP sweep (perfect cleanup at NPROP=16000 at N=8192 = 15× beyond classical 0.14×N bundle-capacity bound).
- **math4_proof_chains** upgraded (commit 615e0c73f pushed) — pre-reg envelope shipped; FULL correctly REFUSED (SATURATION); redesign needed to v2 global-bundle per cell-author. math4_rung3 has same per-antecedent-sharded template = same trap.
- **Testbed state-cache fix** shipped (commit a759e38f5 pushed) — 3-day-stale remote_state_cache.json now current; heartbeat_watchdog symptom root-caused to remote_state_emitter.py dying + ONLOGON-only trigger not surviving reboot; runner_status.py now WARN-banners staleness. Any prior BACKUP claim of "13 pending / 27h serial worst-case" was cache-staleness artifact.
- My prior narrative said "26 CG" — WRONG. Testbed audit corrected to 17; post-VET+VRC 21; +1 HF (h4); +1 HF pending (h4b smoke-HF closure atomization).

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
- **Live state (SSH-verified 2026-07-02T14:42Z per orchestrator a9ea253a63ffc27f1):** 1 running + 11 pending. Running: `cross_axis_m_n_k_factorization_beta_5_bridging_v2_seed_13` (started 14:41:44Z). Head of pending: cross_axis seed_19, commercial_M_latency_percentiles v2 (3 seeds), dim_f_batched_qps v1 (3 seeds), learned_encoder v2 (3 seeds), hrr_depth_budget_curve v2.
- **NOTE:** `data/remote_state_cache.json` is STALE (snapshot_ts=2026-06-29T10:06Z; 3 days old; 137 landings missed). Session heartbeat file (`data/heartbeats/*.timestamp`) is FRESH but that's Director/session heartbeat NOT runner-process heartbeat — do NOT conflate. Live queue truth: SSH pull `remote:C:\dev\hd-instrument\data\overnight_queue\queue.json` and `remote:...\heartbeat.gpu_runner_0.json`. Local `data/remote_state_cache.json` refresher (heartbeat_watchdog / state-cache-pull task) is BROKEN; needs Testbed fix. Any prior-BACKUP claim of "13 pending" or "27h serial worst-case" comes from this stale cache.
- **Dim L v1 seed_19 correction:** NOT in overnight_queue (grep returns 0). Prior claim it was running on GPU is wrong — must have been remote_cpu_queue or never dispatched. BACKUP earlier said "Dim L v1 seed_19 running ~1h ago" — that came from the stale-cache misread.

### local_cpu_queue
- SMOKE ONLY per USER 2026-07-01 lock. Empty otherwise.

---

## LOAD-BEARING PENDING DECISIONS FOR USER

1. **VRC paradigm validation cell — dispatch decision** (once cell-author returns). Novel evaluation methodology; not-BPC-benchmark; likely CG at P_def=0.75.
2. **Dim L v1 seed_19 kill decision** (pending GPU util diagnostic). Same CPU-bottleneck pattern as Dim I A2 today likely.
3. **h4_cluster_density_confidence_calibration_v1 dispatch** — pre-reg exists un-dispatched; failure taxonomy identified as highest-leverage cheap cell.
4. **`hdlab/cortex.py` composed module + integration test cell** — cortex integration debt; USER proposed authoring; awaiting go/no-go.
5. **Language ingest infrastructure — CORRECTION (post-BACKUP audit):** ALL 3 blocking hdlab modules already exist on disk (`hdlab/lm_eval_harness.py` 248 lines, `hdlab/token_vocab.py` 301 lines, `hdlab/bigram_gap_measurement.py` 214 lines) — shipped via commit `df8511e82` by testbed as INFRA_1/2/3 for drill 3. The "~2.5-day blocking build" narrative in this BACKUP is STALE. Stage 4 LM-equivalence work is infra-unblocked; blocked only on Stage 3 maturity per USER-locked stage progression rule + USER "substrate doesn't know anything" until concept-oriented vectors + ingested language. Next language cell should be authored on top of these modules (post-VRC-CG opens the paradigm).
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
