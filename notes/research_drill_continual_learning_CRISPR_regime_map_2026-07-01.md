# Research drill: Continual-learning CRISPR regime map for Stage 1 CG-lift

**Date:** 2026-07-01
**Requestor:** Director (Stage 1 CG-lift regime-coverage audit)
**Calibration:** P estimates deflated 0.15-0.25; novel-synthesis cap 0.50; HARD-FAIL thresholds mandatory.

---

## (a) HEADLINE

**CRISPR append-only architecture has ONE certified regime (J=5, M=400, alpha=1.0 per slab, forget=0.006) and ONE critical gap (transfer=0.000 across every arm -- zero inter-slab plasticity).** The forget metric is MM-grade. The transfer gap is the Stage 1 CG-lift blocker: the substrate can remember what it already learned in each slab but cannot carry ANY information forward into new slabs. This is not a continual-learning system -- it is a partitioned-storage system with zero compositional reuse. The regime map has three structural holes: (1) no M-sweep (only M=400 tested), (2) no long-horizon test (J=5 only; 5000-cycle coverage is TWO_TIER, not CRISPR), (3) no rehearsal-spacing characterization inside CRISPR architecture. Cross-domain anchors (hippocampal SWR, EWC/SI/AGEM, McCloskey-Cohen catastrophic interference) all agree: zero inter-slab transfer is the null-model baseline for a hard-partitioned substrate; beating it requires either (a) a shared representation layer that survives slab boundaries, or (b) an explicit rehearsal/replay mechanism that re-injects old slab content into new slab writes. Neither is currently implemented in the CRISPR cell.

---

## (b) Substrate-KB check results (top 5 hits)

Query: "continual learning CRISPR forget regime rehearsal spacing"

1. `research_drill_substrate_continual_learning_rag_backend_2x_2026-06-11.md` (cosine=0.3994) -- lit corpus with VSA continual learning, EWC, R2R generative replay.
2. Same file chunk (IS_CHUNK_OF edge, citations section) -- 6 lit-scans, 36 hits, 11 load-bearing refs.
3. `research_to_exp_dev_NOW_SHARD_PLUS_HIERARCHICAL_GENERATION_2026-06-10.md` -- "NOW-2: CONTINUAL LEARNING" routing entry.
4. `research_drill_all_open_load_bearing_items_2026-06-25.md` -- "Continual learning (item 2f)" in open items.
5. `wave14d_competitive_landscape_research.md` -- "Model editing / continual learning" competitive context.

**What's already covered in substrate (off-disk verified):**
- forget=0.006 at J=5, M=400, alpha_fast=1.0, N=4096 -- APPEND_ONLY arm, MM-grade (HARD_PASS_PARTIAL verdict)
- TWO_TIER generational W at J=4000 cycles -- HARD_PASS_PARTIAL (drift reduced 0.30; best arm fin_forget=0.70; HARD_PASS full not met)
- NREM replay at J=4000 -- HARD_PASS_PARTIAL (drift reduced 0.57; cv_ok=False)
- STC selective downscale -- HARD_FAIL (destroys older patterns like global homeostasis)
- 120-session production-scale continual KV (CERT chain-grade) -- ingest-only, no inter-session transfer tested

**What is NOT covered:**
- CRISPR at M != 400 (M-sweep)
- CRISPR at J > 5 (long-horizon under append-only architecture)
- Cross-slab transfer > 0 for ANY arm (all arms show transfer_final=0.000)
- Rehearsal / replay INSIDE CRISPR slab structure (old-slab replay injected into new-slab writes)
- CRISPR + TWO_TIER composition (slab-indexed W_old promotion)
- SWR-timed replay gated by slab boundary signal

---

## (c) Cheap decisive test

**Cell:** `crispr_plasticity_slab_replay_v1`

Extend the CRISPR append-only cell with a bounded replay buffer: at the START of each new slab write, replay R=20 items sampled from all prior slabs into the new slab's Hebbian binding (use existing CFRPE pass infrastructure). Measure transfer_phase_J for J in {1,2,3,4,5}. HARD-PASS bar = transfer_final >= 0.15 on any arm (vs 0.000 baseline). Cost: ~2 CPU-hr local. Seeds: 7, 17, 23.

---

## (d) Falsifiable predictions (HARD-PASS + HARD-FAIL)

### Prediction 1 -- Slab-boundary replay rescues transfer

**Hypothesis:** injecting R=20 old-slab replay items into each new slab binding raises transfer_final from 0.000 to >= 0.15.

**HARD-PASS:** transfer_final >= 0.15 on any replay arm, cv <= 0.15 across 3 seeds, forget_p1 still <= 0.05 (replay doesn't corrupt current slab).
**HARD-FAIL:** transfer_final < 0.05 on all replay arms, OR forget_p1 > 0.10 (replay corrupts current slab).
**MIDDLE_BAND:** transfer_final in [0.05, 0.15] -- partial rescue; sweep R (replay buffer size).
**P_deflated: 0.40** (hippocampal replay is well-validated for cross-context transfer; substrate composition untested).

### Prediction 2 -- M-sweep changes forget/transfer tradeoff

**Hypothesis:** at M > 400 (e.g., M=800, 1200), forget_p1 rises (slab more loaded) but transfer_final also rises (more overlap across slab boundaries).

**HARD-PASS:** monotone relationship M -> transfer_final (Spearman rho >= 0.70 across M in {200, 400, 800, 1200}).
**HARD-FAIL:** transfer_final == 0.000 regardless of M -- partitioning is the structural cause, not loading.
**P_deflated: 0.30** (McCloskey-Cohen model predicts interference scales with M; slab isolation may dominate).

### Prediction 3 -- Long-horizon CRISPR (J=20) maintains per-slab forget

**Hypothesis:** extending to J=20 phases (vs J=5) does not degrade per-slab forget_p1 (slabs are independent by construction; append-only is O(J) in space, not O(J^2) in interference).

**HARD-PASS:** forget_p1 at J=20 <= 0.01 (same as J=5 anchor; slab isolation holds).
**HARD-FAIL:** forget_p1 degrades monotonically with J -- routing accuracy degrades as slab count grows.
**P_deflated: 0.55** (append-only is structurally partition-clean; routing accuracy with 20 slabs may degrade independently).

---

## (e) Cross-thread synthesis

### McCloskey-Cohen (1989) catastrophic interference

The original McCloskey-Cohen result: adding any overlap between old and new training items triggers catastrophic forgetting in a single network. CRISPR's append-only architecture is the structural solution -- no overlap at write time. But the experiment shows transfer_final=0.000, confirming the McCloskey-Cohen prediction from the other direction: zero interference = zero transfer. EWC/SI/AGEM are all gradient-space methods for a shared-weight scenario -- they are inapplicable to CRISPR append-only (separate weights per slab). Relevant cross-domain mechanism: Progressive Neural Networks (Rusu 2016) uses lateral connections between column networks; CRISPR needs an analog -- a lateral binding or routing layer that carries cross-slab residual.

### Hippocampal SWR literature

Buzsaki SWR replay (200Hz) during offline consolidation transfers hippocampal episodic memory to neocortex. Key: replay happens at the BOUNDARY (sleep/wake), not during online encoding. CRISPR slab boundaries are the substrate analog of sleep/wake transitions. SWR timing = ingest between slabs. Structural recommendation: replay budget R items at slab-boundary (end of phase J-1, before start of phase J) -- exactly the `crispr_plasticity_slab_replay_v1` cell design.

### Population genetics / Wright-Fisher

Neutral-theory baseline: without selection (replay), allele frequency drifts randomly toward fixation or loss. Applied to CRISPR: without replay, each slab's patterns "fix" in that slab's weight matrix and become inaccessible from adjacent slabs. Replay = "migration" between demes; migration rate R/M determines how much transfer is achievable without interference. Kimura fixation probability provides a lower bound on how much replay is needed for transfer_final > 0 to be maintained.

### TWO_TIER and CRISPR orthogonality

TWO_TIER addresses long-horizon forgetting (4000 cycles) within a shared W matrix. CRISPR addresses the orthogonal problem: structural isolation of incompatible tasks into separate slabs. They are NOT in competition -- they compose: TWO_TIER promotes high-importance items from W_young to W_old within each slab; CRISPR handles task-boundary isolation at the slab level. The open question is whether a shared W_old (promoted from all slabs) provides the "common substrate" that transfer requires.

---

## (f) Ranked cells for Stage 1 CG gap closure

**3 cells to close Stage 1 continual-learning-CRISPR CG gap, rank-ordered:**

| Rank | Cell name | Axes swept | P_deflated | Cost | Decision power |
|------|-----------|-----------|------------|------|----------------|
| 1 | `crispr_plasticity_slab_replay_v1` | replay_R in {0,5,20,50}, J=5, M=400, N=4096, 3 seeds | 0.40 | ~2 CPU-hr | Directly tests whether slab-boundary replay rescues transfer_final from 0.000; decisive on the core CG gap |
| 2 | `crispr_M_sweep_regime_v1` | M in {200,400,800,1200}, J=5, N=4096, 3 seeds | 0.30 | ~3 CPU-hr | Maps the M-axis coverage gap; distinguishes M-driven interference from partition-structural zero-transfer |
| 3 | `crispr_long_horizon_J20_v1` | J=20, M=400, N=4096, 3 seeds; append-only arm only | 0.55 | ~2 CPU-hr | Closes J-axis coverage gap; confirms per-slab forget holds at 4x scale; routing accuracy under 20 slabs is untested |

**One-liner per cell for cell-author dispatch:**

- `crispr_plasticity_slab_replay_v1`: Extend CRISPR append-only cell with R-item slab-boundary replay (sample R from all prior slabs into new slab Hebbian pass); sweep R in {0,5,20,50}; primary metric transfer_final; HARD-PASS = transfer_final >= 0.15 on any arm with forget_p1 <= 0.05.
- `crispr_M_sweep_regime_v1`: Re-run CRISPR append-only cell at M in {200,400,800,1200} (facts per phase), 3 seeds, J=5; map forget_p1 and transfer_final vs M; HARD-PASS = Spearman rho(M, transfer_final) >= 0.70.
- `crispr_long_horizon_J20_v1`: Run CRISPR APPEND_ONLY arm at J=20 phases, M=400, N=4096, 3 seeds; primary metric forget_p1@J=20; HARD-PASS = forget_p1 <= 0.01 (partition isolation holds); HARD-FAIL = routing_acc < 0.80 at J=20 (slab count exceeds routing capacity).

---

## (g) Substrate-product implications

1. **Transfer gap = the M3 glass-box-LLM blocker.** A substrate that partitions tasks perfectly but carries zero information across partition boundaries cannot handle document streams that share vocabulary, entities, or relational structure across temporal segments. M3 glass-box requires cross-partition transfer. The transfer_final=0.000 result makes this concrete and testable.

2. **Slab-boundary replay is the minimal intervention.** No architectural change required -- inject R replay items at each slab boundary. This is implementable in ~50 lines on top of the existing CRISPR cell. If HARD-PASS, the Stage 1 CG-lift is a 50-line addition to the substrate primitive.

3. **M-sweep maps the operating range.** Knowing where the forget/transfer tradeoff breaks down (if at all) calibrates how large each slab can be before isolation fails -- direct input to the M3 deployment sizing.

4. **J=20 long-horizon test = production-scale routing stress test.** Production document streams would exceed 20 temporal segments. Confirming that per-slab forget holds at J=20 proves the architecture scales without re-engineering.

---

## (h) Citations (verified count: 8 load-bearing)

1. McCloskey, M., Cohen, N.J. (1989). "Catastrophic interference in connectionist networks." Psychology of Learning and Motivation 24: 109-165.
2. Kirkpatrick, J. et al. (2017). "Overcoming catastrophic forgetting in neural networks." PNAS. [arXiv 1612.00796](https://arxiv.org/abs/1612.00796)
3. Lopez-Paz, D., Ranzato, M. (2017). "Gradient Episodic Memory for Continual Learning." NeurIPS. [arXiv 1706.08840](https://arxiv.org/abs/1706.08840)
4. Zenke, F., Poole, B., Ganguli, S. (2017). "Continual learning through synaptic intelligence." ICML. [arXiv 1703.04200](https://arxiv.org/abs/1703.04200)
5. Rusu, A.A. et al. (2016). "Progressive Neural Networks." [arXiv 1606.04671](https://arxiv.org/abs/1606.04671) -- lateral connections as cross-column transfer analog.
6. Buzsaki, G. (2015). "Hippocampal sharp wave-ripple: A cognitive biomarker for episodic memory and planning." Hippocampus. [PMC 4648295](https://pmc.ncbi.nlm.nih.gov/articles/PMC4648295/)
7. Kimura, M. (1983). "The neutral theory of molecular evolution." Cambridge. -- fixation probability baseline for drift-only (no-replay) regime.
8. Robins, A. (1995). "Catastrophic forgetting, rehearsal and pseudorehearsal." Connection Science 7(2): 123-146. -- foundational rehearsal analysis; R-item replay as transfer mechanism.

---

**Lit-scan calibration:** P estimates deflated 0.15-0.25 per [[feedback-lit-scan-calibration-penalty]]. Novel-synthesis cap 0.50 applied to Prediction 1 (slab-replay composition with CRISPR cell is substrate-specific). HARD-FAIL thresholds stated for all 3 predictions. Cross-domain fields hit: continual-learning ML (EWC/SI/AGEM/GEM), hippocampal neuroscience (SWR), population genetics (Wright-Fisher/Kimura), catastrophic interference (McCloskey-Cohen), progressive networks (Rusu).
