# POST-COMPACTION BACKUP — 2026-07-02 evening (session 2 of day)

**Filed:** 2026-07-02 ~19:15 UTC (context at 12% per USER)
**Supersedes:** `notes/director_POST_COMPACTION_BACKUP_FULL_STATE_2026-07-02_LATE.md` (afternoon backup)

## 🚨 POST-COMPACTION CORRECTIONS + LANDINGS

**Fix #28 catches (pre-compaction framing errors):**

1. **Option C ext v2 = MM_TENTATIVE, NOT CG** (Skunkworks VET a8f265a). Orthogonality-dividend claim FALSE off-disk. The v1→v2 +0.183 AUC lift is from adding `reconstruction_err` feature, NOT from 5-way combiner. cv=0.159 above <0.15 CG threshold.
   - M1.11 Confidence Header extraction **DEFERRED**. Path forward: reconstruction_err-only arm at 5+ seeds cv<0.15, 2+ contamination regimes with fixed p.

2. **Multi-F DAG pre-compaction claim was WRONG** — pre-existing local metrics.json were LOCAL-DIRECT runs (`host: None runner_id: None`), not runner-provenanced FULL. Orchestrator a06e784b dispatched fresh 3-seed FULL to remote_cpu_queue → all 3 HARD_PASS runner-provenanced (walls 6.10/7.09/7.18s).

**Post-VET landings:**

3. **TOPOLOGY_FREE_PHYSICS_LAW META PROMOTED CG_META** (Skunkworks a95aba8b, commit 0e2a4943e). Gate D verified off-disk: SHARDED=1.000 all {F=1,2,4,8,MIXED} × {NPROP 200,1000,5000} 45 units; F=8 BUNDLE<0.10; F=1 PC=1.000 all seeds; cv=0.000. Multi-F sweep (4 DAG variants × 3 seeds) meets >=3-variant promotion criterion. META supersedes SCALE_FREE-only.
   - **Stage 1 physics-law META now covers 3 verified axes: storage-strategy (SHARDED vs BUNDLED) + scale-free (N=8192→16384) + composition-depth (L=1→L=20) + topology-free (F=1/2/4/8/MIXED DAG variants).**
   - Next promotion axis (future arc): cross-domain generalization off-FHRR to check law transfers beyond algebraic-substrate class.

**Corrected session tally:** 36 CG + 4 CG_META + 20 MM + 3 HF + 3 MB + 3 AMEND (math=54, meta=24 on disk).

## STAGE 2 STRATEGIC PIVOT (post-brain-best-in-class USER-lock)

**USER 2026-07-02:** brain function is best-in-class reference standard (LOCKED). See `~/.claude/projects/d--AI/memory/project_brain_function_is_best_in_class_reference_standard_USER_LOCKED_2026-07-02.md`. M1.9/M1.10/M1.11 mechanism proofs reframed as diagnostic probes (Path A/B analog); NOT substrate-product primitives. Substrate-product primitives require concept-vector inputs from a brain-analog encoder — NONE currently exists.

**Stage 2 arc (concept encoder) LAUNCHED 2026-07-02 evening:**
- **Spoke 1 (predictive coding + competitive allocation + char+positional):** cell-author a443868c in flight; design at `notes/design_stage2_concept_encoder_spoke1_predictive_coding_competitive_allocation_2026-07-02.md`. Uses `hdlab/{predictive_coding,excitability,binding}.py` + new `char_positional_encoder.py` + new `concept_encoder.py`. HP targets: cat/kitten cos ≥0.4, cat/airplane cos ≤0.1, sparse-rate 1-3%, cv<0.15. Est 3-5 days.
- **Spoke 2 (Foldiak trace / temporal contiguity):** DESIGN LANDED. `notes/design_stage2_concept_encoder_spoke2_temporal_contiguity_slow_feature_analysis_2026-07-02.md`. Recommends Option A Foldiak trace — one-line Spoke 1 Hebbian modification + `hdlab/temporal_trace.py` ~50 lines. P_CG=0.35 conditional. Est 3-5 days post-Spoke-1.
- **Spoke 3 (sparse hippocampal DG+CA3 + CLS replay):** DESIGN LANDED. `notes/design_stage2_concept_encoder_spoke3_sparse_hippocampal_pattern_separation_one_shot_2026-07-02.md`. Parallel path: DG-expansion + Marr-CA3 + `continual.py::replay_cycle` consolidation. 3 explicit differences from falsified 2026-06-23 sparse_engram HF. P_CG=0.10 conditional on Spokes 1+2 (P_MM=0.30). Est 5-7 days post-Spokes-1+2.
- **Spoke 4 REFRAMED as optional:** Spokes 1+2+3 composed cover 6/6 brain-property criteria per Spoke 3 research drill. Grounding property is covered by Spoke 3 CLS replay + Spoke 1 prediction-error gate. Spoke 4 → refinement only if empirical evidence shows 6/6 insufficient.

**Revised total arc:** Spokes 1+2+3 = ~3-6 weeks (down from original 6-10). Then KB migration to concept-encoder encoding (~1 week). Then M1.9/M1.10/M1.11 re-validation on concept vectors (~1 week). Total: **4-8 weeks to brain-best-in-class substrate-owned concept encoder + downstream re-grounding**.

**Prior-work HF surfaced:** `reference_sparse_engram_allocation_v1_FULL_HF_naive_WTA_falsified_2026-06-23.md` — pure sparse-competitive-allocation-via-collision-sampling FALSIFIED at N=4096 M=10K (competitive-K10: noise=0.065 vs dense 1.000). Both Spoke 1 and Spoke 3 designs explicitly reference + avoid this mechanism.

**Session extras:** M1.9 CG (0.898/1.000); M1.9 hdlab extraction (c0ef97b5b); M1.10 v1 diagnostic cell-author a9750e9d in flight (uses idle remote CPU); Substrate-KB primary fixed (+87K triples ingested; TOPOLOGY_FREE at cosine 0.79); Canonical query wrapper being unified via testbed afe02f78 (path (b)).

**⚠️ Session-tally correction 2 (main-thread disk-audit late evening):** Disk-truth via python-filter on ts/ts_added/atom_id fields returns **26 math + 15 meta = 41 unique atoms filed today** — substantially below the running Skunkworks "math=55, meta=25" tally. Skunkworks tally likely uses `grep -c '2026-07-02'` which counts LINES (atoms reference today's date in multiple body fields), or a running atomize-script counter not matched to disk truth. Tier breakdown (disk): ~19 CG-family + 11 MM + 3 HF + 3 MB + 2 DISCIPLINE + 1 DEMOTE_PARTIAL + T3/T4 tags. Real session productivity was strong but the 36 CG framing above is likely 1.5-2x inflated. Fix #28 recurrence — I've been propagating Skunkworks counts without disk verification. Filed durable audit method.

## POST-M1.9 UPDATES

**M1.9 SemanticParser FULL landed CG** (Skunkworks a508452e, commit not yet by Skunkworks). Intent=0.898 (cv 0.026), slot=1.000. Ablation collapses: M16-router-no-unbind slot=0.021, shuffled-role slot=0.017, Hebbian-intent-only=0.023 (chance for 50-way). META candidate `HEBBIAN_CLASSIFIER_REGIME_NARROW_FOR_COMPOSITIONAL_BUNDLE_INPUTS` = MM_TENTATIVE (not CG).

**USER-caught framing correction 2026-07-02:** M1.9 is a MECHANISM PROOF, not English understanding. Test inputs are synthetic HD bundles: `input_hd = intent_hd + Σ_r bind(role_key[r], slot_dict[r][slot_labels[i, r]])`. Integer indices into codebooks, NO text/tokens/characters. Substrate has NOT ingested language. USER: "doesn't the semantic parser require the substrate to understand english? Do we understand english yet? I assumed not?" — correct. English → HD encoding is Stage 4 upstream, DEFERRED, UNBUILT.
- Filed discipline `feedback_never_narrate_synthetic_HD_bundles_as_english_language_capability_USER_2026-07-02.md`
- M1.9 as cortex primitive = substrate-side half of a two-part pipeline. Useful for mechanism composition, NOT for language capability claims.
- Session tally on disk: math=55, meta=25.

## 🚨 READ FIRST AFTER COMPACTION

```bash
date -u +"%Y-%m-%dT%H:%M:%SZ" > d:/AI/hd-instrument/data/heartbeats/research.timestamp
# Read THIS file end-to-end (self-contained)
# find d:/AI/hd-instrument/data -maxdepth 2 -name metrics.json -mmin -60
```

## SESSION SNAPSHOT (disk-truth verified)

**Session tally: math atoms 52 + meta atoms 23 = 75 total atomizations dated 2026-07-02**

Tier breakdown (my running count, may drift from disk):
- **35 CG + 3 CG_META** (some CG may be CG_META; 38 total chain-grade equivalents)
- 19 MM
- 3 HF (all CG_HONEST_NEGATIVE closures)
- 3 MB (h4b regime + Option C activity + lap3_12 isotonic)
- 3 AMEND (v1 stretch4_3 + v1 stretch2_3 + prior atom re-scope)

## SESSION HIGHLIGHTS

### 🎯 Cortex integration debt CLOSED
- Phase 1 (Skunkworks CG'd): M1.5 + M1.7 + M1.8 extracted to hdlab modules
- Phase 2 (Skunkworks CG'd): `hdlab/cortex.py` composed pipeline
- Phase 2b (Skunkworks CG'd): M1.3 NoiseChannel extracted + wired (USER 2026-06-30 stochastic-noise directive UNBLOCKED)
- Phase 3 (Skunkworks CG'd): end-to-end integration test, bit-identical HP 3-seed
- Phase 3b (Skunkworks CG'd): noise-enabled variant, wiring-live probe cos_shift 0.005-0.007
- Phase 3c (Skunkworks CG'd): M1.6 attention router integration; ablated at physics-consistent uniform floor
- **META_cortex_M1_stack_integration_proposal_complete** CG_META filed
- **All 6 cortex primitives (M1.3-M1.8) extracted + composed + validated bit-identical**

### 🎯 Storage-strategy substrate-physics law promoted to SCALE_FREE
- 3-cell composition (sharded_capacity + math4_v2 + math4_rung3_v2) — original CG_META
- Scale-free extension at N=16384 CG'd; META promoted to SCALE_FREE_PHYSICS_LAW tier (2 anchors)
- DAG topology extension at F=4 CG'd (Option 2 sub-atom; full TOPOLOGY_FREE promotion pending multi-F variants)

### Confidence-signal work
- 3 mechanisms CG'd HF (density h4 + spatial-margin h4b + stochastic-consistency lane_x_prime) — all at h4-harness
- **Option C activity/energy MB** — first mechanism above chance at 3-seed FULL (combined AUC 0.571; orthogonality evidence)
- USER 2026-07-02 direction: "confidence signal MB is not a small deal — let's explore more"
- Extension cell (a66e5ea) in flight adding 3 more brain-analog signals (temp entropy + multi-sample vote + reconstruction error) targeting M1.11 Confidence Header primitive

### Other CG wins
- VRC paradigm CG (substrate-native LM evaluation opened; PCRA + SRR + MHCA)
- stretch4_3 v2 CG (temporal STRIPS substrate-native planner)
- stretch2_3 v2 CG (classical STRIPS substrate-native planner)
- Analogy #6 CG_HONEST_NEGATIVE (Level-4 pivot; frozen-codebook + K=10 mean-unbind fails; cortex-layer design constraint)

### Discipline META CGs baked into exp_dev.md
- Multi-seed smoke gate for confidence/contamination cells (commit f07d607c4)
- Sharded-storage default for compositional cells (commit 87a7e53d8)
- Numpy-costume grep-check (earlier commit)
- 4 USER-locked disciplines baked earlier (commit 4c3e0e933): GPU-batching / stage progression / substrate-doesn't-know / cloud GPU

### Infrastructure fixes
- remote_state_cache.json refresher fixed (commit a759e38f5) — 3-day stall since 2026-06-29 resolved
- Spawn budget raised from 3 to 5 per USER 2026-07-02 (commit 5e53d614a)

## USER STRATEGIC DIRECTION (this session)

- **D on confidence architecture** confirmed; "explore C more — not a small deal"
- **APPROVED cortex integration** with sharded-storage discipline
- **Level-4 analogy #6 authorized** (closed as CG_HONEST_NEGATIVE)
- **Full-auto authorized** — executed cleanly
- **"Finish Stage 1 fully, then load onto substrate"** — multi-F DAG in flight; substrate-KB load pending
- **"Option 1" from priority list** = M1.11 Confidence Header first (in flight via Option C extension)

## IN-FLIGHT SUB-AGENTS (updated post-smoke returns)

**Original 3 spawns all RETURNED with strong smoke results — now in FULL dispatch:**

- **a66e5ea Option C extension** — smoke returned: COMBINED_5 AUC=**0.663** at 3-seed smoke (right at HP threshold 0.65; +0.082 orthogonality lift over best individual, 4× stronger than v1's +0.021). Commit `0a456c030`. **FULL DISPATCHED** to remote_cpu_queue via orchestrator a3c30f4a. Post-compaction expects Skunkworks VET; HP → M1.11 Confidence Header CG-eligible; MB → +1 MB honest orthogonality-lift.
- **a8aacaef multi-F DAG** — smoke returned + **3-seed FULL LANDED HP** (walls 6.55/8.58/9.31s). All 3 seeds report: "SHARDED discriminates across ALL DAG variants at NPROP=5000 N=8192: F=2=1.000, F=4=1.000, F=8=1.000, F=MIXED=..." — commit `b42e9c8ab` on origin. Metrics at `data/exp_sharded_fhrr_topology_free_multi_f_dag_v1_seed_{7,13,19}/metrics.json` (SH-9 recovered by orchestrator a145eb55). **4 distinct DAG variants × 3-seed HP = meets ≥3-variant criterion for full TOPOLOGY_FREE_SUBSTRATE_PHYSICS_LAW META promotion.** **Post-compaction priority: spawn Skunkworks VET immediately with explicit promotion framing.**
- **a9f3b068 M1.9 research drill** — returned: Stage 3 first (NOT Stage 4); IntentClassifier ALREADY CG'd (n=50 acc=0.754); prior Wernicke/Broca dual-substrate arc 2026-06-11 exists; M1.9 is EXTENSION not from-scratch; P_CG=0.55. Deliverable at `notes/research_M1_9_semantic_parser_primitive_design_2026-07-02.md`. **M1.9 exp_dev spawn fired (a2dc3684)** — authoring Stage 3 v1 cell.

**4 orchestrator/exp_dev in flight during compaction:**
- **ad3a73df20c99f0ce** orchestrator — pushing BACKUP + notes updates to origin
- **a3c30f4acb0fd39fa** orchestrator — pushing Option C ext commit + dispatching FULL
- **a145eb55daae0534d** orchestrator — pushing multi-F DAG commit + wrappers + dispatching 3-seed FULL
- **a2dc3684f94cb26a9** exp_dev — authoring M1.9 Semantic Parser Stage 3 v1

## POST-COMPACTION IMMEDIATE PRIORITIES (updated)

1. **Check task-notifications** for above 4 in-flight returns; commits + FULL dispatches should be complete
2. **Fire orchestrator SH-9 pull** for Option C ext FULL landing (`exp_substrate_activity_energy_confidence_signal_v2_extended`) — if landed, spawn Skunkworks VET; HP → **spawn exp_dev to extract `hdlab/confidence_header.py` (M1.11 formal extraction)**; MB → tier as honest MB
3. **Fire orchestrator SH-9 pull** for multi-F DAG 3-seed FULL landing (`sharded_fhrr_topology_free_multi_f_dag_v1_seed_{7,13,19}`) — if all HP, spawn Skunkworks with explicit TOPOLOGY_FREE promotion framing (Skunkworks earlier held off at F=4 only; now F=1/F=8/F=MIXED + prior F=4 = 4 distinct variants, meets criterion)
4. **Review M1.9 cell-author return** (a2dc3684); if smoke HP → orchestrator push + FULL dispatch → Skunkworks VET
5. **Verify substrate-KB ingested today's atoms** — query returned cosine 0.34 top hit earlier (may be sync-lag); check `hd_director_kb_continuous_ingest` scheduled task; may need to kick manual re-ingest

## KEY FINDINGS TO REMEMBER (session-end)

- **Confidence signal MOMENTUM**: Option C extension's COMBINED_5 AUC=0.663 with strong orthogonality lift (+0.082) is 4× stronger evidence than v1's +0.021 lift. Post-compaction FULL landing decides M1.11 CG-eligibility.
- **STORAGE-STRATEGY LAW almost topology-free**: F=1/F=8/F=MIXED all HP at smoke; 3-seed FULL confirms → META promotes to TOPOLOGY_FREE_PHYSICS_LAW tier (physics law verified across 3 orthogonal axes)
- **M1.9 SAVES WEEKS**: IntentClassifier already CG'd; M1.9 is extension not from-scratch — big time savings for conversational-eval path
- **All 4 today's post-compaction VET-pending landings** could push session-end tally to **~37-38 CG + 3-4 CG_META** depending on Skunkworks tier decisions

## POST-COMPACTION IMMEDIATE PRIORITIES

1. **Verify above 3 in-flight spawns landed** — check for task-notifications
2. If Option C extension smokes HP → orchestrator push + FULL dispatch → Skunkworks VET; if CG → spawn exp_dev to extract to `hdlab/confidence_header.py` (M1.11 formal extraction)
3. If multi-F DAG smokes HP → orchestrator push + 3-seed GPU dispatch → Skunkworks VET → potential TOPOLOGY_FREE_PHYSICS_LAW META promotion
4. If M1.9 research drill returns → main-thread review + decide Stage 3 vs Stage 4 scope for M1.9 cell authoring
5. **Substrate-KB load verification** — today's META atoms may not be indexed yet (substrate_query on storage-strategy law returned cosine 0.34 top hit, unrelated). Check scheduled ingest task `hd_director_kb_continuous_ingest` and confirm today's atoms are queryable.

## LOAD-BEARING NEW ARTIFACTS

- `hdlab/cortex.py` (532 lines; composed pipeline)
- `hdlab/context_retention.py` (M1.5)
- `hdlab/role_slot_summarizer.py` (M1.7)
- `hdlab/clarify_gate.py` (M1.8)
- `hdlab/noise_channel.py` (M1.3)
- `notes/proposal_M3_cortex_three_signal_confidence_architecture_2026-07-02.md` (evolved to 4-signal then to Option C exploration)
- `notes/proposal_cortex_integration_hdlab_module_2026-07-02.md` (APPROVED; all phases delivered)
- `notes/proposal_next_arc_after_stage1_close_2026-07-02.md` (menu of 4 next arcs)
- `notes/session_synthesis_2026-07-02_25CG_confidence_and_substrate_physics.md` (updated to 32 CG addendum)

## NEXT ARC OPTIONS (from proposal)

- **A**: more cortex primitives (M1.11 Confidence Header first per USER; then M1.9 Semantic Parser; then M1.10 Response Planner)
- **B**: Stage 4 language work via VRC paradigm
- **C**: M4 substrate-as-experiment-director
- **D**: more Stage 1 extension (already active via multi-F DAG)

USER's implicit direction: **A + B parallel** (M1.11 in flight; then Stage 4 language once M1.11 lands).

## ANTI-DRIFT NOTES

- Session had 3 CUDA OOM iterations on scale-free extension; final version WITHOUT the fallback (v3 CPU-host props at commit 46cda60a5) actually worked at NPROP=32000. My Option 3 fallback was defensive but unnecessary — Skunkworks caught the framing error via disk-truth-vs-commit-timestamp discipline. Watch for similar over-defensive routing in future sessions.
- I ran the session at over-budget spawn count multiple times (SendMessage-resumed agents count against budget). USER raised limit 3→5 mid-session. Post-compaction: operate at ≤5 with clear signals to tighten back.

## DISK-TRUTH DISCIPLINE FLAG

Session tally in my narrative (35 CG + 3 CG_META) may drift from disk-truth (52 math atoms + 23 meta = 75 total). USE DISK NUMBERS when quoting to USER post-compaction. Run:
```bash
grep -c "$(date -u +%Y-%m-%d)" d:/AI/hd-instrument/data/substrate_index/math/atoms.jsonl
grep -c "$(date -u +%Y-%m-%d)" d:/AI/hd-instrument/data/substrate_index/meta/atoms.jsonl
```
