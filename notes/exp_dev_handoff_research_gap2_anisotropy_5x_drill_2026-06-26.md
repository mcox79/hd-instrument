# exp_dev hand-off -- research: GAP 2 anisotropy 5x drill (top-5 ranked candidates)

**Filed:** 2026-06-26 by Research sub-agent.
**Trigger:** Director request for 5x drill on GAP 2 cone problem. Parent research note: `notes/research_gap2_anisotropy_5x_drill_2026-06-26.md`.
**Pause state:** check `data/orchestrator_paused.flag` before any dispatch; do not bypass.

**Per [[feedback-no-experiment-design-in-prompts]]:** this handoff names anchor candidates with substrate-product reading and tier hint; exp_dev decides full cell design (config, ARMS list, smoke gate, queue routing, anchor name, seed count, pre-reg specifics). Research does NOT pre-design.

---

## ANCHOR CANDIDATES (rank-ordered)

Top 5 from research note Tier A. Rank by `P_deflated x (1 - cost_class) x novel_path x cross_cell_safety`. Each lists: substrate-product reading + tier hint + why-now.

### 1. MIMO water-filling cleanup (research note S1; P_deflated=0.50)

- **Substrate-product reading:** anisotropy rescue as a 1-line cleanup change; ships into substrate-as-LM revival path immediately. Differentiates substrate from vector-DBs which all use uniform cleanup.
- **Tier hint:** Tier A immediate dispatch. Local CPU; reuses v2 calibrated meter fixture; ~5 hr full wall.
- **Why-now:** cheapest novel-rank-adding test in the entire drill. Capped at novel-synthesis ceiling.
- **Pointer:** research note section S1 + cross-cell rail block.

### 2. DG pattern-separation pre-write module (research note N1; P_deflated=0.45)

- **Substrate-product reading:** if it passes, substrate gains a real-data dense-KV product NOT requiring partition routing. Cleaner positioning than today's "partition routing as workaround."
- **Tier hint:** Tier A immediate dispatch. Local CPU; composes EXISTING substrate primitives (sparse-bipolar codebook + k-WTA + per-batch divisive normalization). Brain-existence-proof prior +0.10.
- **Why-now:** Drill 2 (2026-06-25) already ranked this #1 architecturally; this drill prices it cheap.
- **Pointer:** research note section N1 + drill 2 mechanism #1.

### 3. Brenier-map cone-to-ball pretransform (research note M1; P_deflated=0.40)

- **Substrate-product reading:** pretrained ONCE transform that handles ANY anisotropic encoder. Strongest generality claim.
- **Tier hint:** Tier A. Local CPU; Sinkhorn-based; ~6 hr wall. Smoke at small N first (Sinkhorn instability risk).
- **Why-now:** deepest theory-driven attempt at REAL rank addition (vs whitening's rotation-only failure).
- **Pointer:** research note section M1.

### 4. Divisive-normalization cleanup (research note N2; P_deflated=0.40)

- **Substrate-product reading:** if passes, every cleanup operation gets ~0.08 lift for free; cross-product across all substrate retrieval primitives.
- **Tier hint:** Tier A. Local CPU; <1 hr wall. Rapid-fire test; near-zero risk.
- **Why-now:** lowest cost / highest experimental velocity in top 5. Brain-canonical (Carandini-Heeger).
- **Pointer:** research note section N2.

### 5. Compressed-sensing coherence-aware fly-LSH (research note A1; P_deflated=0.35)

- **Substrate-product reading:** RESCUES v2 fly-LSH chain-grade-candidate at adversarial M=100k where random hash already HARD_FAIL'd. Closes a current public weakness.
- **Tier hint:** Tier A. Local CPU; ~4 hr wall. Greedy coherence minimization; may need restarts.
- **Why-now:** defends a working chain-grade-candidate at adversarial regime; high product value.
- **Pointer:** research note section A1.

---

## CONTEXT POINTERS (file paths, no summaries)

- Research note (parent): `notes/research_gap2_anisotropy_5x_drill_2026-06-26.md`
- Prior anisotropy drill 1 (barriers): `notes/research_anisotropy_drill_1_barriers_math_literature_2026-06-25.md`
- Prior anisotropy drill 2 (solutions): `notes/research_anisotropy_drill_2_solutions_brain_substrate_2026-06-25.md`
- Intuitive synthesis: `notes/research_anisotropy_intuitive_synthesis_with_visual_2026-06-25.md`
- Biology unsupervised drill (encoder lane): `notes/research_biology_unsupervised_anisotropy_no_labels_3x_drill_2026-06-25.md`
- v2 calibrated meter fixture (the test bed for all candidates): `data/exp_substrate_anisotropy_rescue_4arm_sweep_v2_calibrated_meter_full/`
- Hierarchical 2-level partition (existing chain-grade): `data/exp_substrate_partition_routing_hierarchical_2level_v1/`
- Substrate-mine capacity primitives: per [[feedback-substrate-mine-capacity-before-extrapolating]] -- 600K patterns chain-grade-validated at N=2048 via sparse * K * D composition (Store, not recent-arc only)

---

## CONTRACT

**Deliverable shape per cell:**
1. Pre-reg with bands matching research-note HARD-PASS / HARD-FAIL per candidate
2. Cross-cell rail: KNN at M=400 >= 0.9 sentinel (Fix #28 by-construction-saturation check)
3. Effective-rank diagnostic (PR/D before vs after pretransform/cleanup change)
4. M-scaling sweep -- AT LEAST M=400, M=10k; ideally M=100k for adversarial check
5. Per-arm metrics not just verdict_msg (Fix #28)
6. atexit partial-flush + per-seed checkpoint (per Fix #20-#22 disciplines + D2)
7. D1 roofline probe pre-dispatch mandatory
8. Status_log entry on completion (event_kind=experiment_result, importance HIGH if HARD-PASS)
9. Entry in exp_dev_decisions_2026-06-26.md

**Cost ceiling per cell:** match research note compute estimate (1-6 hr CPU). Local CPU preferred for Tier A; do NOT route Tier A to GPU queue without exp_dev decision.

**Anchor naming:** exp_dev chooses; suggest pattern `substrate_anisotropy_<mechanism_short>_v1` (e.g., `substrate_anisotropy_mimo_waterfill_v1`).

---

## AUTONOMY

Exp_dev decides:
- Cell config (N_DIM, M values, seed count, ARMS list)
- Smoke gate / gate criteria
- Queue routing (local_cpu_queue vs remote_cpu_queue vs overnight_queue)
- Anchor name and queue entry format
- Pre-reg band specifics within HARD-PASS / HARD-FAIL envelope
- Cell dispatch order within Tier A (research recommends N2 first as cheapest validator)
- Whether to bundle candidates that share fixture (e.g., S1 + N2 may share v2 meter setup)
- Whether to spawn additional sub-cell author for parallel dispatch

Research does NOT pre-design these.

---

**End handoff.**
