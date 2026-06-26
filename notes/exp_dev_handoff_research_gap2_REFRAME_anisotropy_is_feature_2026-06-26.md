# exp_dev hand-off — research: GAP 2 REFRAME anisotropy is feature not bug

**Filed-by:** Research (Director, Opus)
**Date:** 2026-06-26
**Trigger:** Reframe research note `notes/research_gap2_REFRAME_anisotropy_is_feature_2026-06-26.md`
**Pause state:** check `data/orchestrator_paused.flag` before dispatch

Per [[feedback-no-experiment-design-in-prompts]] this hand-off carries anchor pointers + substrate-
product reading + tier hint + why-now. exp_dev owns experiment-design via cell-author skill.

## Anchor candidates (rank-ordered)

### Anchor 1 (TOP, dispatch first) — substrate_partition_routing_anisotropic_scann_quantizer_v1

- **Anchor pointer:** R2 in research note section 4.
- **Mechanism (one-line):** Replace partition routing's k-means quantizer with Guo et al 2020
  anisotropic-VQ loss; production billion-scale recipe (ScaNN) strengthens chain-grade spine.
- **Substrate-product reading:** "Substrate's chain-grade partition routing M=10M gets an
  anisotropy-aware quantizer drop-in; should improve recall/route_acc by exploiting cone clusters
  during quantization the way Google ScaNN does." Tier 4 if works.
- **Tier hint:** chain-grade-eligible at M=100k if HARD_PASS; otherwise still informative
  (locks in current isotropic k-means as already-optimal for substrate cone).
- **Why-now:** TWO Tier-A isotropization HARD_FAILs this morning + 1 prior whitening HARD_FAIL =
  3-independent-falsifications closes the "fight the cone" path. Substrate-product pivot must move
  to "exploit the cone" — anisotropic ScaNN is the production-validated head of that path.
- **Cost (research-estimate):** ~3 hr CPU.
- **P_deflated:** 0.50 (lit precedent strong; substrate already has partition routing infra).

### Anchor 2 — substrate_anisotropic_tikhonov_regularizer_v1

- **Anchor pointer:** R1 in research note section 4.
- **Mechanism (one-line):** Replace uniform Tikhonov (lambda * I) with anisotropic Tikhonov
  (lambda * Cov(K)^alpha) in the dense KV cleanup pseudo-inverse.
- **Substrate-product reading:** "Substrate's cleanup regularizer becomes cone-aware via one-line
  matrix-multiply change; informative either way — HARD_PASS adds 0.05 lift, HARD_FAIL proves
  current uniform Tikhonov is already optimal for substrate's cluster regime."
- **Tier hint:** MEASURED_MECHANISM expected (not chain-grade by itself; complementary to Anchor 1).
- **Why-now:** Companion to Anchor 1 — anisotropic-aware quantizer at routing time pairs with
  anisotropic-aware regularizer at cleanup time. Cheap; gives ablation data either way.
- **Cost (research-estimate):** ~2 hr CPU.
- **P_deflated:** 0.40.

### Anchor 3 — substrate_hierarchical_partition_3level_aniso_clusters_v1

- **Anchor pointer:** R3 in research note section 4.
- **Mechanism (one-line):** Extend chain-grade 2-level hierarchical to 3-level with anisotropy-aware
  (Mahalanobis-style) clusters at coarse level + isotropic-within-cluster fine level (matches
  Cai-Kanai-Belkin ICLR 2021 "isotropy within clusters, anisotropy between").
- **Substrate-product reading:** "Tightens existing chain-grade hierarchical from 0.978 toward
  0.99+ at M=10M; gives architecture story that explicitly matches lit's cluster-isotropy result."
- **Tier hint:** chain-grade-tightening (small headroom).
- **Why-now:** Extends already-chain-grade infrastructure with minimal risk. Lower priority than
  Anchors 1+2 because discriminator headroom is small (current already ~0.98).
- **Cost (research-estimate):** ~6 hr CPU.
- **P_deflated:** 0.35.

### Anchor 4 (BACKUP) — substrate_learned_per_cluster_tikhonov_v1

- **Anchor pointer:** R4 in research note section 4.
- **Mechanism (one-line):** Learn lambda per partition based on local density; combines R1 + R2.
- **Substrate-product reading:** "Per-cluster adaptive regularization for the partition-routed
  cleanup primitive."
- **Tier hint:** MEASURED_MECHANISM.
- **Why-now:** Backup only — dispatch AFTER Anchors 1+2 land; data from those informs the lambda
  schedule.
- **Cost (research-estimate):** ~4 hr CPU.
- **P_deflated:** 0.35.

### Anchor 5 (CHEAP PROBE) — substrate_mahalanobis_cleanup_readout_v1

- **Anchor pointer:** R5 in research note section 4.
- **Mechanism (one-line):** Replace L2 argmax in cleanup readout with Mahalanobis argmax using
  cleanup-residual covariance.
- **Substrate-product reading:** "Cheap experiment; readout-side anisotropy-awareness; conceptually
  overlaps Anchor 2 — discriminator headroom limited."
- **Tier hint:** MEASURED_MECHANISM (low).
- **Why-now:** Lowest priority — cheap but largely redundant with Anchor 2.
- **Cost (research-estimate):** ~1 hr CPU.
- **P_deflated:** 0.30.

## Cumulative-evidence gating

Two cells already in flight (dispatched 2026-06-25 before reframe):
- `substrate_anisotropy_fly_lsh_expansion_sweep_v2_cpu_path` (running remote_cpu, ~3h)
- `substrate_anisotropy_polarimetric_multi_probe_retrieval_v1` (queued remote_cpu)

**Pre-dispatch advisory for exp_dev:**
- Do NOT dispatch Anchors 1-5 until v4 CPU + polarimetric LAND. Their verdicts inform reframe
  confidence:
  - Both HARD_PASS the "exploit-the-cone" mechanism class -> dispatch Anchor 1 first with high
    confidence
  - Both HARD_FAIL -> reframe weakens; sanity-check (Read research note section 5 cumulative table)
    before dispatching ANY Anchor; may need to reroute to capacity-cap analysis instead
- Run `tools/predispatch_check.py` per Fix #26 before each Anchor dispatch — checks for duplicate
  anchor names + recent HARD_FAIL re-dispatches.

## Context pointers (file paths only, not summaries)

- `notes/research_gap2_REFRAME_anisotropy_is_feature_2026-06-26.md` (full research synthesis with
  sections 1-6)
- `notes/exp_dev_anisotropy_mimo_waterfill_v1_SMOKE_HARD_FAIL_2026-06-26.md` (this morning Anchor #1
  fail)
- `notes/exp_dev_anisotropy_dg_pattern_separation_prewrite_v1_SMOKE_HARD_FAIL_2026-06-26.md` (this
  morning Anchor #2 fail)
- `notes/research_anisotropy_drill_2_solutions_brain_substrate_2026-06-25.md` (prior drill that
  already identified the partition-and-sparse-fan-in pattern in section D.1)
- `data/exp_substrate_partition_routing_hierarchical_2level_v1/metrics.json` (chain-grade ledger
  reference)
- `data/exp_substrate_partition_routing_10M_full_v2/metrics.json` (chain-grade ledger reference)
- `data/exp_kv_learned_projection_v1/metrics.json` (anchor for KV-learned-projection capability)
- `data/exp_substrate_anisotropy_rescue_4arm_sweep_v2_calibrated_meter_full/metrics.json` (fly-LSH
  chain-grade-candidate)

## Contract

Per the standard hand-off contract (v195 template):
- exp_dev OWNS cell design (no inline design in this file).
- exp_dev OWNS pre-reg bands + smoke gates per cell-author discipline.
- exp_dev OWNS dispatch routing (which queue) based on cost + load.
- Research filed the WHY-NOW + WHICH ANCHOR; exp_dev decides HOW.

## Autonomy declaration

exp_dev MAY:
- Re-rank Anchors 1-5 based on cumulative-evidence verdicts from in-flight cells
- Substitute equivalent mechanisms within the SAME framework class (e.g. use a different anisotropic
  k-means loss formulation than Guo et al's specific one, provided it's still anisotropy-aware)
- Bundle Anchors 1+2 into a single multi-arm cell if the cell-author judges the combined-discriminator
  to be cleaner than separate cells
- Defer dispatch if pipeline is full (overnight_queue >= 5 or remote_cpu busy AND laptop CPU busy)
- DECLINE to dispatch any Anchor if the v4 + polarimetric cells both HARD_FAIL (filing a routing
  note back to Research with "reframe weakens; recommend pivot to capacity analysis")

exp_dev MAY NOT:
- Dispatch a 4th GLOBAL ISOTROPIZATION variant (already 3 independent HARD_FAILs; this is
  cap_map-locked by the reframe)
- Skip the Fix #26 pre-dispatch check on any Anchor
- Treat any Anchor's HARD_PASS as substrate-product-ready without a chain-grade follow-up at M=100k
  or M=1M

## Pause-flag check at time-of-write
PASS (no `data/orchestrator_paused.flag` exists at filing time per orchestrator state).

## Companion routing
Status log entry: research_delivery importance=HIGH (reframe is decision-grade, flips a research
direction).
