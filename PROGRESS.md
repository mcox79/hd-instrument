# Progress

## Current phase (2026-07-04)

**Framing (USER-locked):** this is a MEMORY SYSTEM modeled after neuroscience — storage, retrieval, cleanup, composition of stored traces. Neuro references are MECHANISM analogies, not task/capability claims.

**PRIMARY FOCUS (USER 2026-07-04): the concept encoder.** It is the load-bearing component — the substrate's word/concept -> vector frontend that every downstream layer (retrieval, composition, Cortex-2 atom-consultation) inherits quality from. Currently borrows BGE-large (0.54 semantic cosine on USER test query); native concept encoder targets 0.85+. Getting it RIGHT (optimal sparsity + objective + algebraic fidelity), not just finished, is the current thrust — with empirical ablation because the design space (controllable-sparsity code feeding an algebraic memory) is genuinely new. M4 (consolidation, attention gating) defers behind it.

**Active arcs (2026-07-04 latest):**
- **Encoder rescue** (PRIMARY): the orthographic Step-1 and the BGE-distillation v2 approaches FAILED at full corpus scale (v2 MLP FULL: BLOCK 0.31, DENSE 0.368 — worse than the CHARPOS orthographic baseline 0.66). Diagnosed FAIR + root-caused: the in-batch RKD objective does not supervise global geometry over 178k concepts. Fix under test = R1 global/landmark objective (validating; DENSE-recovery gate). 5x rescue battery sequenced (global-obj -> brain dense-first-sparsify -> internal self-teacher -> predictive -> K256 diagnostic). Brain drill: no external teacher + sparsify-after-geometry.
- **M3 Cortex-2 atom-consultation** (4 primitives deep, advisory->SHADOW->dose-response->multi-atom): LIVE-mode ring rollout DEFERRED behind the encoder.
- **Stage 1 regime map** (CORRECTED): the mechanism-moderation cross-term family (Probes 1/6/7/8, incl the Probe-1 CG_META) was DEMOTED 4/4 as unpaired-sampling artifacts — the mechanisms are argmax-readout-degenerate (bit-identical). MAIN-EFFECT laws stand (storage 0.93, scale-free, M-scaling, N x L additive). Genuine paired replacement probe_18 (storage-advantage boundary SCALES with N, cv=1%) landed HARD_PASS. Discipline filed: paired-trials mandatory for arm-comparison.
- **Task-analog arc: DEFINITIVELY CLOSED** (v1-v4 double-lock; LDPC framework).

**Live Store CERT count: ~633** (was 634 floor @ 2026-06-30; -1 from the Probe-1 cross-term demote this session; treat as a floor, not re-counted).

**Session-state canonical:** `notes/director_POST_COMPACTION_BACKUP_FULL_STATE_2026-07-04.md` (clean rewrite; the 07-03_LATE file is SUPERSEDED).

---

## Prior phase (2026-06-30 EOD)

Substrate program is on the M3-milestone path: glass-box conversational AI 12-18mo via substrate as memory+composition+retrieval+audit layer + external cortex layer for hint derivation / planning / coref / surface-form access.

**Stage progression** (load-bearing; do not skip):
- **Stage 1 — Foundational primitives:** ~88% mature. 12 chain-grade primitives (HRR/FHRR/BSC bind+unbind; cleanup attractor; pattern completion; sequence binding K-cliff; WM multi-bank; refuse-gate V_REL=256; KG ingest FB15k/CN/HotpotQA; partition routing M=10M; intent classifier; capacity multi-bank α-K; action-at-any-position).
- **Stage 2 — Meta-primitives + optimization:** ~85% mature. Schema family CG, ANCHOR 4 time-decay CG, Lock-in amp CG, ANCHOR 3 coarse-grain CG, ULTRAMETRIC CG, Compose-freq routing v5 CG. **NREM replay bottleneck partially characterized 2026-06-30:** Ha (Hebbian cross-term) = 51% of gap (MM atomized); Cell C v2 compartmentalized cortex K-banks LANDED HARD_PASS at K=200 covering 92% of bottleneck gap (Skunkworks VET in flight for 9th CG promotion).
- **Stage 3 — Capability primitives:** ~60% banked. Multi-hop reasoning depth-15 CG; compositional generation lift CG; cross-modal binding CG; CF regret vmPFC CG; TASK_VECTOR HRR ICL K-cliff CG. Within-structure substrate-only gaps in flight 2026-06-30: TOM 3rd+ v5 d=5-isolated (smoke HP confirms dilution hypothesis; FULL pending), CF latency v2 (running), Parietal RELATIONAL v2 (pending), Narrative Q3 v2 Q_per_type=15 (in flight). Multi-structure-bio gaps deferred to M3 cortex layer.
- **Stage 4 — LM equivalence:** DEFERRED per stage-progression rule.

**M3 cortex layer (Phase 1):** `substrate_router/` module on `m3-phase1-router-scaffolding` branch. M1.1 done (SubstrateRouterAPI + route()). M1.2 advanced 2026-06-30: `hdlab/intent_classifier.py` extracted from production-scale v2 cell + `hdlab.kg_traversal.load_from_fb15k237_dump` helper shipped.

**Methodology META rules atomized this arc (~12-13):** centroid pooling (AT), GPU-mandate-breach signature (AU), selftest-not-FULL (AV), seed-config-identical (AW), arms-distinct-across-family-axis (AX), verdict-HARD_FAIL-on-self-reported-distinctness-False (AY proposed 2026-06-30).

**Infrastructure 2026-06-30 fixes:**
- `hd_metrics_sync` merger: preserve-existing → mtime-newer-wins (commit be4cec83); first sync after fix overwrote 3873 stale local files
- `queue_add.sh`: auto-SCP sibling helper modules (commit e0435992)
- SSH-immune schtasks runner lineage; gpu_runner_0 + cpu_runner_0 with 5-min auto-restart

For session state see `notes/director_POST_COMPACTION_BACKUP_FULL_STATE_2026-06-28.md` + `notes/director_TRUE_PHASE_DIAGRAM_COVERAGE_2026-06-30.md`.

---

## Historical (Week 8) phase

**Week 8 complete + depth-mechanism follow-up done:**

- **FHRR capacity**: `k_50% ~ N^1.003` (R^2 = 0.99999734)
- **BSC capacity**: `k_50% ~ N^1.004` (R^2 = 0.9999), FHRR/BSC ratio constant at 2.52x
- **FHRR depth**: `depth_50% = 0.717 * log2(N) - 0.629` (sub-linear)
- **HRR depth**: `depth_50% = 1.273 * log2(N) - 7.20` (**super-linear**)

Two-hypothesis investigation resolved why FHRR depth scales sub-linearly: H1 (shared-role cross-talk) falsified; H2 (FHRR per-component renormalization) confirmed by HRR test. Notes in [notes/week8_depth_mechanism.md](notes/week8_depth_mechanism.md) and [notes/production_considerations.md](notes/production_considerations.md).

**Bottom line for production:** HRR is the substrate of choice for compositional / deep workloads (the depth ceiling was an FHRR property, not a HDC property). BSC for memory-bound edge; FHRR for capacity-bound GPU; HRR for depth-bound reasoning.

## Next milestone

**Week 9 - Standalone release.** Publish `hd-instrument` v0.1.0 to PyPI, MIT-licensed; MkDocs site with the scaling-law plots embedded; quickstart notebook that runs the diagnostic.

Then **Week 10+ - Case study**: continual learning on Split-CIFAR-10 with substrate behaviour empirically mapped.

## Open questions

- HRR inverse fidelity at low N - test currently asserts sim > 0.5 at N>=1024; tighten after collecting empirical distribution.
- Trace bus overhead at micro-bench scale is dominated by Python call overhead; Week 4 batched/sampled tracing should bring it under 10% on representative workloads.
- Storage choice: DuckDB vs SQLite for trace persistence - currently DuckDB.
- Recency uses geometric decay (1-r)^(k-1-i); alternative is exponential weighting. Reassess after molecule experiments in Week 7.

## Phase status

| Phase | Status | Notes |
|---|---|---|
| Week 0 - Scaffold | done | Repo, deps, CI, stubs |
| Week 1 - Substrate + trace (FHRR + HRR) | done | 15 verification tests passing |
| Week 2 - Modulators | done | attention + recency wired; reward/arousal/gating staged for Week 3+ |
| Week 3 - Learning | done | reward-modulated Hebbian, lazy decay, steady-state matches theory within 1% |
| Week 4 - Observability | done | DuckDB store, perf_counter timing, replay reconstructs state, PDF + Streamlit dashboards |
| Week 5 - Harness + go/no-go | done | Declarative ExperimentSpec, harness, same-seed determinism, GO decision |
| Week 6 - Atomic experiments | done | A1-A4 + A5 envelope; substrate cliff at sigma=pi |
| Week 7 - Molecule experiments | done | M1-M7; capacity 3-4x higher than predicted; learning boost; BSC tradeoff |
| Week 8 - Scaling-law (FHRR + BSC + depth) | done | FHRR a=1.003, BSC a=1.004, FHRR depth beta=0.717; see week8_scaling_summary.md |
| Week 8b - Depth mechanism deep-dive | done | HRR depth beta=1.273 (super-linear); FHRR per-component renorm identified as cause |
| Week 3 - Learning | pending | |
| Week 4 - Observability | pending | |
| Week 5 - Harness + go/no-go | pending | |
| Week 6 - Atomic experiments | pending | |
| Week 7 - Molecule experiments (incl. density sweep M7) | pending | |
| Week 8 - Scaling-law experiment | pending | Pre-registered N sweep; publishable on its own |
| Week 9 - Standalone release | pending | |
| Week 10+ - Case study (continual learning) | pending | |
