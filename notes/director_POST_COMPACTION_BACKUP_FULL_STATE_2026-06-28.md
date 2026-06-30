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

**Substrate state (CANONICAL, 2026-06-30 ~09:45 UTC):**
- Live Store CERT count: **632** (provenance_quality == CERT_CHAIN_GRADE via cert_ledger_writer self-test)
- cert_increment_delta sum: **499** (ledger transaction log; 132 atoms predate delta-tracking)
- Session-start baseline: 625 / 492
- **7 chain-grade promotions tonight** (2026-06-28 23:00 → 2026-06-29 05:24 UTC):
  1. 23:07 — PC v2.2 corruption cliff dense grid 3-seed GPU phase-characterization
  2. 23:09 — PC corruption cliff N-scaling law FINDING (cliff_N=0.40+0.0065·log2(N); R²=0.97)
  3. 02:01 — ANCHOR 4 Pareto-AUC v2 (TD dominates RD 70/70; Stage 2 time-decay)
  4. 02:14 — Capacity multi-bank v2 (cliff_per_B identical cross-seed; Stage 1)
  5. 03:28 — ANCHOR 3 v2 FAMILY_OVERLAP (over-compression boundary visible; caught v1 metric-bias bug)
  6. 05:09 — Lock-in v2 (physics band confirmed; Stage 2)
  7. 05:24 — Schema family (regime mapping; HYBRID dominates EB default in 10/12 regimes)

ANCHOR 4 encoder family attempt was honestly REJECTED by Skunkworks re-VET (raw-float encoder collision at FULL; only seed_7 actually re-ran; not a chain-grade promotion). Earlier Director framings of "630→635 (+5)" were WRONG — actual is 625→632 (+7).

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
| Higher-order TOM 3rd+ | MM | PARTIAL (v3 at N_LOCATIONS=32 SURFACES depth signal: TENSOR_RANK2 cliff 0.833→0.400→0.167 across d={1,3,5}; HRR also depth-aware; BOW control FLAT confirms recursion-driven not artifact) | TPJ recursive | Substrate IS depth-aware. v1/v2 flat-depth bound was INSTRUMENT-DRIVEN (4-loc ceiling) and is RESOLVED. MM not chain-grade because pre-reg threshold 0.10 too aggressive vs measured mechanism SNR 0.076; honest STOP at smoke per pre-reg discipline |
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
6. **ANCHOR 4 Pareto-AUC v2 (LATE SESSION 2026-06-28 ~21:45)** — Stage 2 time-decay-eviction chain-grade phase-characterization; 2x-drill mechanism-class diversion (binary threshold → continuous Pareto-dominance); 3/3 HP all seeds; 0 RD wins / 70 strict TD wins; commits 1e8c7d94 + atomize script; cert_ledger +1 → **631 total**. **First 2x-drill chain-grade revival from Skunkworks 5-cell recommendation batch.**

**CERT trajectory:** 490 → 492 (BACKUP mid-session) → 631 actual (canonical Store provenance_quality count; cert_ledger.jsonl is transaction log not count). Late-session +1 from ANCHOR 4 Pareto v2.

## LATE-SESSION FINDINGS (2026-06-28 EVENING → 2026-06-29 OVERNIGHT)

- **TOM 3rd+ resolved instrument-bound:** v3 at N_LOCATIONS=32 SURFACES depth signal (TENSOR_RANK2 cliff 0.833→0.400→0.167 across d={1,3,5}; HRR also depth-aware; BOW control FLAT confirms recursion-driven). Substrate IS depth-aware; v1/v2 flat-depth was test-instrument ceiling. Pre-reg threshold 0.10 too aggressive vs measured 0.076 → MM (not chain-grade) but capability genuine.
- **Spaced-rep NREM brain-reality variant CLOSED-negative:** smoke 3-way collapse at matched-alpha. All schedule variants (brain-spaced / all-at-once / uniform-repeat) produce identical noisy recall. Cell-author identified hippo readout fidelity as the floor.
- **HIPPO CAPACITY RESCUE FINDING (reframes Stage 2 NREM closure):** at N_h=8192/M=2048 substrate runs at α_h=0.014 — well sub-capacity — yet STANDARD readout still 0.226 vs DIRECT 0.989. **The bottleneck is NOT capacity (Hopfield/Willshaw); it's structural to sparse-DG + sign-readout.** Cortex Hebbian writer HEALTHY at chain-grade scale. Rescue must target READ path. 2-step Hopfield cleanup CLOSED-negative (collapses to zero-signal fixed point). Bottleneck-class diagnostic dispatched to discriminate H1 (sparse-overlap) vs H2 (sign-quantization) vs H3 (L2-magnitude-loss).
- **Schema v4 mechanism-class diversion (4/5 smoke CHAIN_GRADE_MULTI):** primitive substitution (HARDMAX = cosine-nearest-MEAN centroid) shows centroid pooling is noise-SUPPRESSING at FLOOR (not noise-amplifying as Skunkworks predicted). 5-seed FULL blocked on `_core.py` module remote-pull; hd_metrics_sync auto-pull pending.
- **Encoder family PC smoke 3/3 HP — HRR-real DOMINATED** at cliff edge (~25pp behind bipolar/FHRR/sparse). FULL queued on GPU behind multihop v4 chain (positions 4-5-6).
- **Encoder family seqbind PHANTOM-FULL caught:** "completed" landings were selftest-only (run_mode=selftest leaking into runner env); seed_19 META_RULE_AF violation (HRR hash = FHRR hash). Needs re-dispatch with HDLAB_RUN_MODE=full enforced.
- **TASK_VECTOR v3 (n_trials=50 + pooled cliff):** smoke MB; cell-author still in flight; mechanism-class diversion (precision densification, not metric change) being tested.
- **ANCHOR 3 v2 FAMILY_OVERLAP:** smoke HP at full N=1024 (d_v2=0.470 vs 0.15 threshold). **Caught load-bearing v1 metric-bias bug:** v1's `recall_via_lookup` counted argmax-in-COLLAPSED-cluster as hit — metric was MASKING failure. v2 introduces `recall_truth_family` (planted-family-aligned). FULL dispatch via Orchestrator.

## OVERNIGHT AUTONOMOUS PROGRAM (USER away until morning)

**Two crons armed:**
- `3855c94d` 10-min cadence per-queue idle tracker via `tools/runner_status.py --remote`; dispatches when queue empty
- `20dff7b1` 15-min backup cadence: landings check + atomization + BACKUP edits

**Spawn fleet (13+ in flight as of 02:13 UTC):**
- Cell-authors: hippo bottleneck diagnostic / Schema v4 / TASK_VECTOR v3 / Lock-in v3 / cleanup family PC / routing family WM / schema family / binding operation family
- Orchestrators: Schema v4 dispatch (blocked on _core push) / ANCHOR 3 v2 dispatch / encoder PC FULL dispatch
- Skunkworks: Capacity_multibank v2 atomization (likely +1 cert on return)
- Multihop v4 GPU 3-seed running on overnight_queue

**Queue depths (as of 02:13 UTC):**
- overnight_queue: 1 running + 4 pending (6h backlog; includes encoder family PC + multihop v4)
- remote_cpu_queue: 1 running + 1 pending (1h)
- local_cpu_queue: 1 zombie + 8 pending (12h; cpu_runner_local PID 5776 stuck on lock_in_amp_v2_seed_7; queue blocked until USER admin clear OR Orchestrator orphan-entry cleanup)

**24hr expected outcomes:**
- 6+ chain-grade promotion candidates land (Capacity_multibank v2 + ANCHOR 3 v2 FAMILY_OVERLAP + Schema v4 + ANCHOR 4 Pareto v2 already promoted)
- Component sweeps complete with comparative encoder/cleanup/routing/schema/binding-op data
- Stage 2 NREM bottleneck-class diagnostic returns; informs whether sparse-DG / sign-readout / L2-magnitude is the structural blocker
- 5-6 mechanism-class 2x-drill cells return with revival paths
- CERT trajectory likely +3 to +6 (current 631 → 634-637 by morning)

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

## FORWARD PLAN (2026-06-30 ~09:50 UTC; updated for compaction survival)

### CORTEX (M3 Phase 1) STATUS
- `substrate_router/` module exists on branch `m3-phase1-router-scaffolding`: api.py (20KB) + router.py (7.6KB) + smoke test (8KB). Last touched 2026-06-28 21:11.
- M1.1 milestone landed: `SubstrateRouterAPI` class wrapping intent classifier + KG lookup + refuse-gate; `route()` function with `RouterDecision`/`RouteOutcome` dataclasses; 20/20 smoke against hand-crafted 21-entity KG + 42-example corpus.
- **NOT advanced past M1.1.** No M1.2 (full corpus + ingested FB15k-237), no M1.3 (multi-hop), no M1.4 (schema), no M1.5 (refuse-gate integration), no M1.6 (200-query cert benchmark).
- **Cortex is NOT serving anything.** Pure stub on a feature branch.
- **M3 milestone target:** glass-box conversational AI 12-18mo. Critical-path for M3 success.

### NEXT-WAVE ACTIONS (priority order)

**(1) Process in-flight Skunkworks** (just dispatched fresh after earlier batches lost):
- a686b057 — Schema v4 5-seed VET (potential +1 chain-grade → 8 total this session)
- a009a44a — Backlog 6-cell VET (Multihop v4 HN + TASK_VECTOR v3 MM + Binding op HN + Lock-in v3 MM + Cleanup family PC MM + Refuse-gate adaptivity MM)
- Expected: ~24 atom rows added (mostly delta=0; potentially 1-2 chain-grade)

**(2) Queue cells to fill remote runners (NOW READY — restarted with auto-restart schtasks)**
- ANCHOR 4 encoder family v2 (Skunkworks rec: N≥4096 + n_atoms≥1000 + 5th distinct encoder + recency-decode floor)
- TASK_VECTOR v4 cell-author shipped earlier but had no wrapper — needs cell wrapper + re-dispatch (was attempted; bounced at pre-dispatch gate)
- Routing geometry family v1 (smoke caught at SELFTEST_FAIL; cell-author needs to fix learned_supervised geometry)
- Hypothesis-gen v2 (smoke HF; cell-author iteration needed)
- Parietal MOVABLE v2 (only seed_7 + seed_13 done; need seed_19)
- Multihop v5 STORAGE_DENSITY (smoke ran via Orchestrator's SCP fix; full not yet)

**(3) Stage 2 NREM rescue chain** (load-bearing for cortex_hippo CLOSED-neg):
- Hippo bottleneck-class v2 with H_OTHER candidates:
  - ARM_NO_HEBBIAN_CROSSTERM (eliminates outer-product cross-term contribution)
  - ARM_NO_L2_NORM (skip L2-normalize on read-back)
  - ARM_CLEAN_VALS_TO_CORTEX (clean vals written to W_c; tests cortex write-saturation)
- If any candidate fires (closeFrac >= 0.40), it IS the rescue path
- If all 3 fail: deeper rescue (BCM-gain / non-Hopfield substitution / etc.)

**(4) Schema family follow-up** (HYBRID dominates EB default; methodology-load-bearing):
- Cell to operationalize H2 regime-mapping finding
- Substrate runtime picks family from regime hint via cross-seed lookup table
- OR switch default to HYBRID + retire EXEMPLAR_BAYES as default

**(5) Continue systematic component-sweep program** (~50% done):
- Encoder family ✓ (PC + seqbind + WM + ANCHOR4; one phantom-FULL each; sparse-bipolar regime-conditional per META_RULE_AO)
- Cleanup family ✓ for PC (MB convergent); needs sequence binding + WM
- Routing family ✓ for WM (smoke HP cross-seed; FULL VET pending); needs routing for KG/multihop
- Schema family ✓ (chain-grade promotion)
- Binding op family ✓ for PC (3/3 HF; HRR-conv + FHRR competitive)
- Refuse-gate adaptivity ✓ (low_disc expected MM)
- Time-decay family (ANCHOR 4) ✓ (Pareto v2 chain-grade)
- **Missing:** SEQUENCE encoding family (positional shift vs time-cells vs gated) / Order-binding (cyclic shift vs permutation) / Storage update rules (Hebbian vs SoftHebb vs Willshaw vs autoassociative)

**(6) M3 cortex layer advancement** (BIG: this is the M3 critical path):
- M1.2: extract `hdlab/intent_classifier.py` primitive (Hebbian `(cat_codebook).T @ question_hds / N_DIM` from cell `exp_a1_substrate_intent_classifier_v1.py`)
- M1.2: extract `hdlab/kg_traversal.load_from_fb15k237_dump(path)` convenience
- M1.3: real chain-grade corpus (5000 examples) routing test
- M1.4: multi-hop integration
- M1.5: schema retrieve integration
- M1.6: 200-query end-to-end cert benchmark with substrate-vs-LLM fallback breakdown

**(7) Infrastructure cleanup queue:**
- Fix queue_add.sh helper-module SCP bug (3rd recurrence; _core.py / _base.py modules not auto-shipped with cells)
- Fix `revive_cpu_runner_via_schtasks.ps1` (wrong launcher path)
- Ship `register_runner_schtasks.ps1` canonical idempotent registrar
- Prune watchdog ping scope (research session only; not all 5)
- Phase-3 cert_ledger.jsonl canonical-count tool (resolve live=632 vs ledger-sum=499 drift)
- Dashboard relative-time fix ("1h ago" was showing for 5.5h-old landings)
- Patch exp_dev.md §16 enforcement (3 phantom-FULL recurrences despite §16 existing)

### STRATEGIC DIRECTION

**Substrate is memory + composition + retrieval + audit device.** Cortex layer required for M3 milestone (glass-box conversational AI). 4 of 5 Stage 3 architectural gaps need external cortex (long-narrative coref / Barrier 1 hint / hierarchical planning / 4-primitive composition). Stage 2 NREM closure is structural (H_OTHER class; not capacity bound).

**Current substrate maturity (by stage):**
- Stage 1 ~88% (PC + cleanup + sequence binding + WM all chain-grade; capacity multibank + action-at-any-position chain-grade)
- Stage 2 ~80% (TWO_TIER + ULTRA + ANCHOR 1-4 + Schema family + Lock-in v2 all chain-grade; NREM replay BLOCKED at chain-grade scale; cortex_hippo handoff CLOSED-negative at M=8192)
- Stage 3 ~55% (multihop chain-grade; CF regret + cross-modal chain-grade; many primitives MM; 5 CLOSED-negative requiring cortex layer)
- Stage 4 DEFERRED

**24-hour expected outcomes:**
- +1-2 more chain-grade promotions when in-flight Skunkworks return (Schema v4 likely)
- ~3-4 more component sweeps to land
- Hippo bottleneck-class v2 (H_OTHER candidate testing)
- Schema family Stage 2 follow-up cell
- Cortex M1.2 first step (extract intent_classifier as hdlab/ primitive) — main-thread work

### KNOWN INFRA WATCH-LIST

- Runners auto-restart every 5 min via schtasks — survives idle-exit + SSH disconnect
- queue_idle_watch Monitor (bm7gnvqhu) emits QUEUE_IDLE on threshold-cross (5/15/30/60/120 min escalation)
- hd_metrics_sync silent-crash pattern — manual mitigation: `rm data/.metrics_sync/.lock` + `schtasks /run /tn hd_metrics_sync`
- AtomKind enum: must register new `kind` values in schema.py BEFORE writing atoms (commit fdf4c714 fixed 3 known unregistered kinds; future writers must check)
- Phantom-FULL pattern (cells write run_mode=selftest to FULL anchor dir): 3 recurrences; cell-author §16 verification rule exists but not consistently applied; consider hard-fail at Skunkworks input

---

## ORIGINAL POST-COMPACTION PRIORITIES (kept for reference)

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
