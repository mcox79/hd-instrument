# strategy_request_to_exp_dev: KF battery refill + axis1 chunk2 + Bet B options

**From**: verdict_handler (v254 BATCHED 6-VERDICT)
**Date**: 2026-05-27 22:30
**To**: exp_dev
**Trigger**: GPU overnight_queue pending=0 running=0 post-verdict-batch; remote_cpu_queue pending=2 running=1; pause flag ABSENT (ACTIVE); per [[feedback-pipeline-pacing]] source-queue invariant queue ≥ 1 VIOLATED on GPU lane; per [[feedback-no-padding-experiments]] every shipment justified by open strategic-priority

## Context

Six verdicts landed simultaneously from the user's phase-boundary KF battery dispatch (kf5 + axis1 + kf1 + kf3 + kf4 + bet_b_phaseD). v254 cap_map bump committed at `4239418`. Phase-boundary direct-test row LIFT 50-65 → 55-70%. Framework reliability product-feature LIFT 65-77 → 68-80%. Portfolio 14+19 → 14+22 (+3 evidence-strength rows: KF-1 hallucination-impossibility + KF-3 multi-substrate isolation DUAL-FRAMING + KF-4 continuous drift detection).

**Open strategic priorities from this batch** (in order of strategic-value-per-compute ratio):

### Priority 1 — HIGHEST: kf5_steerable_beta_v2 FULL re-ship

KF-5 was the user's HIGHEST-PRIORITY KF per dispatch ("Run it first"). v1 returned `_source=local` smoke artifact (remote SSH None → fallback per role-contract Step 0 fix; FIRST POST-FIX OBSERVATION). The phase-boundary β-steering sub-claim is the STRONGEST single sub-claim and remains UNTESTED AT FULL. Smoke at N=1024 1-seed shows monotone β-driven entropy/gap/bpc-bowl (positive-consistent) — needs FULL N=4096 5-seed across β ∈ {16, 32, 64, 128} per user dispatch.

**Spec for exp_dev**:
- TASK: re-ship KF-5 at FULL N=4096 5-seed multi-seed [7, 17, 23, 31, 41] across β ∈ {16, 32, 64, 128}
- WHY: strongest single phase-boundary sub-claim test; v1 metrics-source-fallback prevented call; product framing depends on this clearing
- CONTRACT: pre-reg HP gate `mean_entropy_range > 1.0 bits across β-axis` (matches v1 verdict_msg threshold) + `monotone-in-β top1_top2_gap` + `bpc interior min at some β*`; HF gate `entropy_range < 0.5 bits AND all-β-bpc-monotonic` (= no qualitative profile shift = phase-boundary refuted)
- INFRASTRUCTURE: per [[feedback-per-experiment-timeout-required]] timeout formula `1.5 × smoke_wall_s × (FULL_N/smoke_N)^exp × (FULL_seeds/smoke_seeds)`; per-seed metrics.json checkpointing so partial data survives any runner crash; REMOTE VERIFY post-ship; PROT-018 anchor `_n4096` if N-binding contract claimed
- AUTONOMY: exp_dev decides script path, GPU vs CPU lane choice, exact timeout budget number, smoke-then-FULL or direct-FULL ship strategy

### Priority 2 — HIGH: axis1_mb_chunk2 over-capacity regime

axis1 chunk 1 (M ∈ {1024, 2048, 4096, 8192} = M ≤ 2N) caught retention saturated everywhere — NO retention phase transition in chunk-1 regime. Chunk 2 needs M > 2N to find the actual retention boundary.

**Spec for exp_dev**:
- TASK: ship axis1_mb_chunk2_v1 at M ∈ {8192, 16384, 32768, 65536} × β ∈ {1, 4, 16, 32, 64, 128, 256} at N=4096 (over-capacity regime M/N ∈ [2, 16])
- WHY: map the retention phase boundary missed in chunk 1; phase-diagram completion (axis 1 of the substrate phase diagram per dispatch context)
- CONTRACT: pre-reg HP gate `retention falls below 0.5 at some M*` + `retention monotone-decreasing in M past M*` + `BNV continues scaling`; HF gate `retention=1.0 across all M up to 65536` (= no retention boundary in tested regime = chunk needs to extend further)
- INFRASTRUCTURE: per [[feedback-per-experiment-timeout-required]] timeout formula; per-seed checkpointing; PROT-018 anchor `_n4096` if N-binding
- AUTONOMY: exp_dev decides if larger-M cells need shorter run / chunked execution; smoke-vs-FULL strategy

### Priority 3 — MEDIUM-HIGH: kf1_hallu_impossibility_v2 multi-seed FULL

KF-1 v1 was 1-seed-equivalent at multiple M-fractions (single seed=7 sweep) at N=4096. The product-spec defensibility ("structurally cannot hallucinate at M ≤ N") needs MULTI-SEED 5-seed FULL confirmation before being committed to a Tier-1 product feature.

**Spec for exp_dev**:
- TASK: re-ship KF-1 at FULL N=4096 5-seed [7, 17, 23, 31, 41] across M-fractions {0.25, 0.5, 1.0, 2.0, 4.0}
- WHY: cross-seed reproducibility of bounded hallucination-impossibility before Tier-1 product feature row commit
- CONTRACT: pre-reg HP gate `5/5 seeds show mean_oos_max_conf < 0.001 at M ≤ N` + `above_thresh_frac == 0` at under-cap cells; HF gate `≥1 seed shows oos_max_conf > 0.01 at M ≤ N`
- AUTONOMY: exp_dev decides if cells reduce to (M=N, M=N/2) single-cell deep test or stay broad sweep

### Priority 4 — MEDIUM: kf4_drift_detect_v2 5-seed extension

KF-4 v1 was 3-seed FULL N=4096 with r_bnv=0.994. Extension to 5-seed [7, 17, 23, 31, 41] is defense-in-depth before Cat-B drift-detection killer feature commit.

**Spec for exp_dev**:
- TASK: re-ship KF-4 at FULL N=4096 5-seed
- WHY: defense-in-depth for Cat-B drift-detection killer feature foundation; r_bnv=0.994 at 3-seed merits 5-seed confirmation
- CONTRACT: pre-reg HP gate `5/5 seeds r_drift ≥ 0.9` + `5/5 r_bnv ≥ 0.9`; HF gate `≥2 seeds r_drift < 0.5`
- AUTONOMY: exp_dev decides scope/parameters

### Priority 5 — MEDIUM: bet_b_4stage_n16384_v1 scale-extension

Bet B retA=0.74 floor is intrinsic at N=8192 across 3 architectural axes. The remaining unanswered question is whether scale (N=16384) lifts the floor or confirms it as N-invariant.

**Spec for exp_dev**:
- TASK: ship Bet B 4-stage CL at N=16384 5-seed, baseline config (no architectural rescue)
- WHY: test if retA=0.74 floor is N-scale-dependent or intrinsic to substrate; if N=16384 retA stays at 0.74 = floor is fundamental, accept bar-lowering reframe (retA ≥ 0.70 product threshold); if N=16384 retA lifts to 0.80+ = floor was finite-N artifact, ship at production N
- CONTRACT: pre-reg HP gate `retA ≥ 0.80 at N=16384`; HF gate `retA ≤ 0.78 at N=16384` (= confirms floor is intrinsic, triggers bar-lowering reframe)
- AUTONOMY: exp_dev decides if this fits in single ship or requires chunked / smoke-first

### Priority 6 — LOW: kf5_dual_v1 β-extension

If KF-5 v2 clears, dual probe across HIGHER β range {64, 128, 256, 512} maps the full steerability β-axis. Lower priority since v2 is the immediate gating priority.

## Pipeline-pacing constraints

- GPU overnight_queue pending=0 running=0 → ship Priority 1 first for GPU lane
- remote_cpu_queue pending=2 running=1 (bid_n_stability_v2 + tcft_m_sweep_v1 + spectral_graph_lambda2_v4) — already covered for CPU lane next 2-4h
- local_cpu_queue 0/0 — available for quick CPU probes
- Pause flag ABSENT (ACTIVE); exp_dev proceeds normally
- Per [[feedback-pipeline-pacing]] GPU is depth-probe lane; CPU is design-space-sweep lane
- Per [[feedback-no-padding-experiments]] all 6 priorities above are justified by open KF-battery handoffs; not padding

## Recipient autonomy

exp_dev decides:
- Which priorities to ship in this refill cycle (recommend Priorities 1 + 2 + 3 minimum; Priorities 4-6 can be next cycle)
- Target queue per priority (Priority 1 GPU; Priority 2-5 GPU or remote_cpu per cost; Priority 6 GPU if Priority 1 clears)
- Exact timeout budget numbers per priority
- Smoke-vs-FULL ship strategy (Priority 1 needs smoke-first to verify the remote-SSH-disconnect isn't the script-side problem)
- Pre-reg HP/HF threshold specifics per script
- Script paths and any infrastructure prerequisites

## Termination conditions

Ship enough to restore GPU queue depth ≥ 2 (one running + one pending = pipeline-pacing invariant). Recommend Priorities 1, 2, 3 ship from this refill (= ~6-12h GPU work batch).
