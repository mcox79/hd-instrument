# Post-compaction BACKUP — hd-instrument substrate program

**Last updated:** 2026-06-28 EOD
**Audience:** fresh post-compaction session
**How to use:** read this file end-to-end. Self-contained snapshot of program state, in-flight work, pending VETs, and forward direction.

---

## OPERATING MODEL (read first)

Research is the director. Main session does judgment, strategy, direction, and 1-off important work. Sub-agents do the rote and heavy work — cell authoring, smoke iteration, landed-VET, atomization, dispatch, infra refinements.

Available agents: `hdi_exp_dev` (cell author + smoke + local dispatch), `hdi_skunkworks` (landed-VET + atomization; AUDIT-ONLY), `hdi_orchestrator` (push + remote queue_add + state sync), `hdi_testbed` (infra + 2nd-witness on cross-cutting changes).

**Lean spawn prompts:** pass paths + raw context. Do NOT pre-bake numbers, predicted analysis, or prescribed conclusions — that turns sub-agents into rubber-stamps.

**Pre-spawn check (three criteria):** (1) independent from in-flight work, (2) bounded scope, (3) returns as a summary you can act on.

**Spot-check, don't re-do:** verify sub-agent outputs by reading 1-2 metrics; escalate via SendMessage with delta if wrong; don't restart with a fuller prompt.

**Spawn budget:** ≤3 in flight by default; USER may authorize exceeding.

**Main thread is for:** strategy + thinking + 1-off important docs (BACKUP, memory rules, plan), reading metrics.json, observability tools, queue state, git commits, dispatching agents.

**NOT in main thread:** cell editing, smoke via Bash, pre-reg writing, landed-VET, atomization, capacity-stress drills, SSH dispatch.

---

## PROGRAM AT A GLANCE

**Target:** M3 milestone — glass-box conversational AI (12-18mo) with substrate as memory + composition + retrieval + audit layer + external cortex layer for hint derivation / planning / coref / surface-form access.

**Stage progression (load-bearing; do not skip):** Stage 1 (foundational primitives) → Stage 2 (meta-primitives + optimization) → Stage 3 (capability primitives) → Stage 4 (LM equivalence; deferred).

**Substrate state:** chain-grade portfolio across all stages; cert_ledger at **494** chain-grade certifications (positive-delta-summed from cert_ledger.jsonl; the authoritative count). The +2 this cycle came from WM K-cliff v3 + ultrametric clustering chain-grade promotions. Pending atomizations could push 495+ on next Skunkworks batch.

---

## CHARACTERISTICS TABLE (2026-06-28 EOD)

**Legend:** CG = chain-grade ✓ | MM = measured mechanism | CLOSED = capability bound proven (positive or negative) | UNTESTED = no cells yet

### Stage 1 — Foundational Substrate Primitives (~88% mature)

| Capability | Status | Coverage | Brain analog | Notes |
|---|---|---|---|---|
| HRR bind/unbind | CG ✓ | HIGH | None | Core primitive |
| Cleanup attractor | CG ✓ | HIGH (cliff sharp at N-scaled corruption) | Hopfield/cortex | PC v2.2 chain-grade-promotion-ready |
| Pattern completion | CG ✓ | HIGH (3-seed cliff localized N→corruption: 0.47/0.48/0.485/0.49) | Hippocampal CA3 | PC v2.2 GPU HP cross-CRLB |
| Sequence binding K-cliff | CG ✓ | HIGH (3-seed cross-cell agreement; K* tracks Kanerva form) | Hippocampal time cells | Phase-coverage MID → HIGH this session |
| Multi-bank WM K-cliff | CG ✓ | HIGH (3-seed; K_cliff(B)=256·B perfect scaling) | dlPFC + parietal | WM v3 chain-grade this session (+1 CERT) |
| Refuse-gate V_REL=256 | CG ✓ | HIGH | Posterior parietal | Stable |
| Continual learning CRISPR | CG ✓ | MID | mPFC consolidation | forget=0.006 |
| KG ingest FB15k/CN/HotpotQA | CG ✓ | HIGH | Cortex semantic | 3 corpora |
| Partition routing M=10M | CG ✓ | HIGH (routing_acc=0.97) | Cortex + thalamus context-gating | Workhorse |
| Intent classifier n=100 | CG ✓ | MID | Sensory cortex categorization | Stable |
| Capacity multi-bank α-K | CG ✓ | MID (GPU 3-seed MB; cliff observable but phase fill incomplete) | None direct | Just landed this session |
| Action-at-any-position lever (p1_v2) | CG ✓ | MID | None direct | p1_action_at_any_position_phase_diagram_v1 + p1_v2_LLM_class_v1 (2 CG entries 2026-06-22) |

### Stage 2 — Meta-Primitives + Optimization (~78% mature)

| Capability | Status | Coverage | Brain analog | Notes |
|---|---|---|---|---|
| TWO_TIER generational W | CG ✓ | HIGH | STM→LTM consolidation | Foundation of cortex_hippo |
| NREM replay | CG ✓ | HIGH at small-M; chain-grade-scale BLOCKED at M=8192 (Willshaw cap 36 items at sparsity=0.1) | Hippocampal replay | Cortex_hippo handoff CLOSED-negative at chain-grade scale this session |
| ULTRAMETRIC clustering | CG ✓ | HIGH (3-seed phase diagram; honest-downward: KMEANS dominates 67% of phase space, ULTRA wins 35-42%) | Cortex schema foundation | Chain-grade phase-characterization this session (+1 CERT) |
| ANCHOR 1 partition-by-source | CG ✓ | HIGH | None | Substrate-design |
| Lock-in amp | CG ✓ | MID (3-seed MB landed; chain-grade-eligible with SNR×√t physics; awaits Skunkworks VET) | None direct | USER intuition validated |
| Order-sensitive seq binding | CG ✓ | PARTIAL | Hippocampal sequence | Stable |
| ANCHOR 3 coarse-grain | CG ✓ | MID | Cortex chunking | Stable |
| ANCHOR 4 time-decay eviction | CG ✓ | MID | Synaptic decay | Stable |
| Schema exemplar-Bayes | CG ✓ | MID → HIGH-eligible (3-seed MM + capacity-stress v2 smoke MB; FULL queued) | vmPFC schema | Capacity-stress promotion path filed this session |
| Compose-freq routing v5 | CG ✓ | MID (DEFINITIVE) | None direct | substrate_compose_freq_routing_v5 DEFINITIVE (CG 2026-06-25); first Stage 2 architectural definitive |

### Stage 3 — Capability Primitives (~55% banked; mixed outcomes)

| Capability | Status | Coverage | Brain analog | Notes |
|---|---|---|---|---|
| Multi-hop reasoning depth-15 | CG ✓ | HIGH | PFC context-gated routing (Mante 2013) | Barrier 1 BROKEN this session via partition-oracle hint (3-seed verified; +0.47 lift; cv 3.96%) |
| Compositional generation lift +0.724 | CG ✓ | MID | Cortex hierarchical | Stable |
| Schema exemplar-Bayes (ANCHOR 3) | CG ✓ | MID | vmPFC schema | Stable |
| TASK_VECTOR HRR ICL K-cliff | CG ✓ | MID (3 seeds in flight; seed_13 FULL just HP) | None direct | K-cliff at K=100; promotion path live |
| TOM Sally-Anne 2nd-order | MM | PARTIAL | TPJ + mPFC | Single MM smoke (nested_hrr_v1); cert_class=mechanism_characterization; no chain-grade evidence |
| CF regret vmPFC (Cell 1) | CG ✓ | PARTIAL | vmPFC | R²=0.987 |
| CF latency delta-stack (Cell 2) | MM | PARTIAL | None direct | Single MM smoke; 5.47x speedup observed but only mechanism-characterization (CF regret vmPFC Cell 1 separately CG) |
| Cross-modal binding visual+auditory | CG ✓ | HIGH (3-seed HP; TPJ-analog characterized) | TPJ multisensory | Stage 3 UNTESTED → HIGH this session |
| Sequence binding for narrative Q3 | MM | PARTIAL | Hippocampal time cells | Single MM single-seed (narrative_Q3 temporal-via-sequence-replay); Stage 1 sequence binding K-cliff primitive separately CG |
| Hypothesis-gen pipeline composition | MM (smoke HP+0.56) | PARTIAL | DMN + SWR-preplay | FULL queued |
| Parietal MOVABLE-rebind | MM | PARTIAL (FULL re-dispatched) | Parietal cortex | Cliff at n_obj=200 |
| Parietal RELATIONAL-spatial | MM | PARTIAL | Parietal cortex | Smoke promising |
| Higher-order TOM 3rd+ | CLOSED-INSTRUMENT-BOUND (v1 MB + v2 HF flat-depth; both witness same 4-location cleanup-attractor ceiling per 2x-drill) | N/A | TPJ recursive | Bound is on TEST INSTRUMENT (4-location ceiling), not substrate capability. v3 with larger N_LOCATIONS + per-level distractor scaling + higher-rank tensor encoder needed for true substrate-capability characterization |
| Self-explanation richness | MM bounded 0.467 | PARTIAL | ACC + lateral PFC | Workable bounded |
| Long-narrative Q2 coref | CLOSED-negative | N/A | Hippocampal pattern completion | HRR-recency drill 1 + substrate-faithful Lappin-Leass drill 2 both HF; cortex layer with surface-form access required |
| Barrier 1 hint derivation | CLOSED-negative-mechanism-class-2 | N/A | PFC + cortex | 5 drills HF (cosine + 3 brain-comp + supervised linear); M3 cortex layer load-bearing |
| Hierarchical planning (substrate-native) | CLOSED-negative | N/A | PFC + basal ganglia | Closed earlier; needs external planner |
| 4-primitive brain-composition (substrate-native) | CLOSED-negative | N/A | CLS architecture | 2x-drill discipline satisfied |
| CLS handoff at chain-grade M=8192 | CLOSED-negative (substrate-only path) | N/A | Hippocampal replay → cortex | Willshaw capacity floor 227x exceeded; chain-grade scale needs different protocol or LLM cortex |

### Stage 4 — LM equivalence (DEFERRED per stage-progression rule)

Not pursuing. Substrate is memory + composition + retrieval + audit device; build understanding first; language is downstream.

---

## CHAIN-GRADE PROMOTIONS THIS SESSION

1. **Barrier 1 substrate-side BROKEN at depth-15** — partition-oracle goal-conditioning 3-seed verified; commit f3e51bb8
2. **Sequence binding K-cliff full v2 phase diagram** — 3-seed cross-cell agreement (log10(K*) SD=0.031); commit 68714d0e
3. **WM K-cliff v3 GPU phase diagram** — K_cliff(B)=256·B perfect cross-seed scaling; commit 7274bafb (+1 CERT)
4. **Ultrametric clustering phase diagram** — 3-seed phase regime structure; honest-downward; commit 7274bafb (+1 CERT)
5. **Cross-modal binding visual+auditory** — Stage 3 UNTESTED → HIGH characterized; commit 09c40db3 (+1 CERT)

**CERT trajectory this session:** 490 → 492 per ledger (+2 confirmed atomizations; +1-3 more pending Skunkworks VETs below).

---

## LANDED, AWAITING SKUNKWORKS VET

These should be the FIRST hdi_skunkworks spawns after compaction:

1. **Pattern_completion v2.2 GPU 3-seed × HARD_PASS_PHASE_DIAGRAM_LOCALIZED_CLIFF** (commit ac706494)
   - 180/180 grid pts; cliff at N-scaled corruption (0.47/0.48/0.485/0.49)
   - CRLB-consistent (0.005-0.01 below CRLB predictions)
   - gpu_util=0.95; torch.cuda confirmed
   - Chain-grade-eligible: Stage 1 pattern_completion phase coverage MID → HIGH; CERT +1 candidate
   - Paths: `marsh@home:C:/dev/hd-instrument/data/exp_substrate_pattern_completion_corruption_cliff_v2p2_dense_cliff_grid_seed_{7,13,19}_GPU/metrics.json`

2. **Lock_in_amp phase diagram v1 3-seed × MIDDLE_BAND**
   - seed_7 + seed_13 + seed_19 all MB
   - Discriminator FIRES at SNR×√(t/2) physics regime
   - Paths: `d:/AI/hd-instrument/data/exp_substrate_lock_in_amp_phase_diagram_v1_seed_{7,13,19}/metrics.json`

3. **Capacity multi-bank α-K GPU 3-seed × MIDDLE_BAND**
   - All 3 seeds MB; K_per_bank × num_banks × N grid
   - Composes with WM K-cliff v3 chain-grade primitive
   - Paths: `marsh@home:C:/dev/hd-instrument/data/exp_substrate_capacity_multibank_alpha_K_phase_diagram_v1_GPU_seed_{7,13,19}/metrics.json`

4. **TASK_VECTOR HRR ICL K-cliff v1 3-seed × HARD_PASS FULL**
   - All 3 seeds (7, 13, 19) FULL HARD_PASS landed
   - Chain-grade-eligible phase-characterization
   - Paths: `d:/AI/hd-instrument/data/exp_substrate_task_vector_K_cliff_phase_diagram_v1_seed_{7,13,19}/metrics.json`

5. **Schema exemplar-Bayes capacity-stress v2** — seed_7 HARD_PASS landed; seed_13 MIDDLE_BAND landed; seed_19 pending. VET when 3-seed complete or take partial.
   - Paths: `d:/AI/hd-instrument/data/exp_substrate_schema_exemplar_bayes_capacity_stress_v2_seed_{7,13,19}/metrics.json`

---

## IN FLIGHT

- **Schema_bayes capacity-stress v2 seed_19** on local CPU
- **Cortex_hippo seed_23** + queue tail on remote CPU
- **10 cells** still pending on remote_cpu queue (hypothesis_gen × 3 + parietal MOVABLE FULL × 3 + multihop v4 smoke + others)

GPU is idle and available for new work.

---

## INFRA STATE

- **Substrate-index Store** loads clean (177583 atoms across 11 partitions); 6 poison atoms patched this session; cross-modal atomize source script patched to use AtomKind enum
- **runner_v2_prod.py** META RULE patch (commit 9f9c74fe): exports HDLAB_QUEUE env var to child env
- **runner_status.py** is canonical "what's running" observability tool
- **GPU runner** (`hd_gpu_runner_0` schtasks lineage) alive
- **Local cpu_runner_local** PID 5776 zombie (SYSTEM-elevated; unkillable from session); USER admin needed to clear for local_cpu dispatch
- **hd_metrics_sync** scheduled task pushing to origin/main on cadence
- **Substrate-Director-KB v1** (filename-metadata index) operational; `--filename-contains` reliable rank-1 at cosine 1.0

## DOC HYGIENE STATE

Startup docs (CLAUDE.md, .claude/agents/*.md) cleaned of archaeology; rules stated as forward fact. Latest additions to CLAUDE.md STEP 2 + research.md Coordination:
- Director-vs-rote separation (main thread = judgment + 1-offs; agents = cell authoring / smoke / VET / atomization / dispatch)
- Lean spawn prompts (no pre-baked analysis)
- 3-criterion pre-spawn check (independent / bounded / returnable)
- Spot-check discipline (verify without re-doing)
- ≤3 in-flight spawn budget

8 deprecated memory entries removed from MEMORY.md index. `NO EXPERIMENTS LOCAL` rule softened to `PREFER REMOTE` (judgment call routing).

---

## STANDING META-RULES (load-bearing)

1. **Spawn agents for all bounded work** — main thread for strategy + dispatching only
2. **Lean spawn prompts** — paths + raw context; don't pre-bake analysis
3. **Substrate doesn't know language** — Stage 4 LM equivalence deferred until Stages 1-3 mature
4. **2x-drill before capability closure** — closure-atom requires 2 different mechanism classes both null
5. **Every HF gets Skunkworks-VET + intuitive USER explanation** — automatic
6. **Functional-requirement-first test design** — decompose capability into requirements; map to existing primitives
7. **Discriminator must survive scale** — smoke discriminator must fire at full-N regime
8. **No hallucinated numbers** — verify on disk before citing
9. **Verify-the-referent** — read per-arm metrics not just verdict_msg
10. **Skunkworks correctly overrides Director on by-construction-saturation** — default classification = MM; let cert-owner tier up

---

## GOING FORWARD

**Immediate post-compaction priorities:**

1. **Spawn Skunkworks for 3 pending VETs** (PC v2.2 + lock_in_amp + capacity_multibank) — likely +2-3 CERT
2. **Process TASK_VECTOR v1 FULL** when 3 seeds land
3. **Continue phase-diagram fill** for Stage 1/2 cells at MID coverage
4. **Author follow-ups for promotion paths:** PC v2.2 chain-grade, lock_in_amp chain-grade if HP at FULL, capacity_multibank chain-grade extension
5. **M3 architecture work** — substrate-only blockers (Barrier 1 hint + CLS handoff at chain-grade) jointly justify external cortex layer; consider Phase 1 LLM router prototype as next architectural step
6. **Higher-order TOM v3 reframe** with richer encoding (higher-rank tensor / positional binding) — closed at v2 reframe but capability still TBD with proper test design

**Longer-term direction:**

- **Stage 3 fill** — many Stage 3 capabilities at MM/PARTIAL coverage; continue dispatch chain via agents
- **Substrate-Director-KB Wave 4** content-chunk rebuild (in flight) → content-queryable substrate replaces filename-metadata index
- **M3 cortex layer** — Phase 1 LLM router prototype + downstream handoff to substrate chain-grade primitives
- **CRISPR slab-partition phase-diagram fill** (per CRISPR cell-author option 3 — pivot away from generic CRISPR to the actual chain-grade primitive)
- **Bidirectional meet-in-middle** characteristics-table entry needs correction to HF (v3 disproof 38hr ago); not a CG primitive

**What NOT to do:**
- Test against language (Stage 4 deferred)
- Edit cell files / run smoke in main thread (agent-spawn rule)
- Pre-bake analysis in spawn prompts (lean prompts)
- Atomize in main thread (Skunkworks owns this)
- Push to origin/main directly (harness-DENIED; orchestrator owns push lane)
- File inter-session routing notes (`_to_<role>_` filenames deprecated)

---

## RECOVERY COMMANDS

```bash
# 1. Heartbeat
date -u +"%Y-%m-%dT%H:%M:%SZ" > d:/AI/hd-instrument/data/heartbeats/research.timestamp

# 2. Silence stop hook
date -u -d "+168 hours" +"%Y-%m-%dT%H:%M:%SZ" > d:/AI/hd-instrument/data/last_processed_auto_7c6e8deae7.timestamp

# 3. Catch up on recent landings
find d:/AI/hd-instrument/data -maxdepth 2 -name metrics.json -mmin -180 -printf '%TH:%TM %p\n' | sort

# 4. Canonical runner status
python d:/AI/hd-instrument/tools/runner_status.py --remote

# 5. Verify scheduled tasks (PowerShell, NOT bash)
schtasks /query /tn hd_landing_notifier /fo LIST
schtasks /query /tn hd_substrate_capability_registry_scan /fo LIST

# 6. Re-arm notes_monitor (CLAUDE.md ritual)
```

---

## FIRST 5 SUBSTANTIVE ACTIONS AFTER COMPACTION

1. Spawn hdi_skunkworks: VET + atomize PC v2.2 GPU 3-seed HP (chain-grade-eligible; lean prompt: paths + context only)
2. Spawn hdi_skunkworks (or batch with #1): VET + atomize lock_in_amp 3-seed MB + capacity_multibank 3-seed MB
3. Check TASK_VECTOR v1 FULL remaining seeds (7 + 19) — when 3-seed landed, spawn Skunkworks VET
4. Check schema_bayes capacity-stress v2 FULL landings
5. Continue Stage 1/2 phase-diagram fill via hdi_exp_dev spawns (anchor candidates: ANCHOR 3 coarse-grain phase fill, ANCHOR 4 time-decay phase fill, continual learning slab-partition CRISPR phase fill)
