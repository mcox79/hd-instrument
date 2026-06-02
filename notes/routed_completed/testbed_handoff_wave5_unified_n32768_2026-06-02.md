# Testbed handoff: Wave 5 cloud unified_n32768_v1 bundle

**Filed:** 2026-06-02
**Filed-by:** strategy_scribe (strategy sub-agent)
**Trigger:** User directive: "There may be a few for cloud gpu as well please route that to testbed first"; sourced from notes/research_high_priority_tests_v324_synthesis_2026-06-02.md Section 2 Wave 5
**To:** testbed session (cloud A100 / A100-80GB Lambda instance)
**Pause state:** orchestrator_paused.flag ABSENT at filing time -- dispatch authorized

Per [[feedback-no-experiment-design-in-prompts]]: this file names ANCHORS + POINTERS only. Cell implementation details, exact compute graphs, script structure, and instance choice belong to testbed autonomy.

---

## Context pointers

- Source synthesis: d:/AI/hd-instrument/notes/research_high_priority_tests_v324_synthesis_2026-06-02.md (Section 2 Wave 5, lines 96-114; Section 4 abort/skip, lines 151-158)
- Prior cloud handoff template: d:/AI/hd-instrument/notes/routed_completed/testbed_handoff_overnight_round6_cloud_h100_cells_a_b_2026-06-01.md
- Cloud launch protocol memory: feedback_cloud_launch_snapshot_reconcile.md
- Lambda no-spot API memory: feedback_lambda_no_spot_api.md
- Anchor name binding: feedback_no_label_vs_honest_anchor_names.md (PROT-018 exit-6)
- Timeout formula: feedback_per_experiment_timeout_required.md (PROT-019)
- Verbose tracing: feedback_always_verbose_remote_dispatch.md
- ASCII-only: feedback_ascii_only_in_scripts.md
- Composition classification: feedback_composition_classification.md
- Batch cloud: feedback-batch-cloud-experiments (single Lambda batch, single bootstrap)

---

## Sequencing constraint

Wave 5 fires LAST per research's 5-wave plan. Waves 1-4 run on local CPU + remote GPU first. Testbed begins engineering NOW (long lead time) but defers actual Lambda dispatch until Wave 5 trigger: either user explicit authorization OR automatic post-Wave-4-PASS signal from orchestrator.

---

## Anchor candidates (rank-ordered)

All 5 anchors ship inside a SINGLE Lambda batch, SINGLE bootstrap, SINGLE model load. PROT-018 `_n32768` suffix is a binding contract on every anchor name.

### Anchor 1: Q-D1 spectral primitives at N=32768

**Anchor pointer:** `qd1_spectral_primitives_n32768_v1`
**Substrate-product reading:** Sharper Tracy-Widom edge at N=32768 (sigma_TW ~ 0.0023 vs 0.0059 at N=8192) enables more sensitive audit primitive; production-grade BBP threshold.
**Tier hint:** spectral-audit production readiness; prerequisite for claiming N=32768 audit API envelope.
**Why now:** VRAM gate (N=32768 W matrix = 4 GB FP32) prevents running on remote GPU (8 GB VRAM limit). Cloud is the only feasible resource.
**Pre-reg HARD bands:** sigma_TW empirical within +/-5% of theoretical 0.0023.
**Composition classification:** SCORE (standalone spectral measurement, no handoff dependency).

### Anchor 2: kappa_4 + kappa_6 fingerprint extraction at N=32768

**Anchor pointer:** `kappa46_fingerprint_n32768_v1`
**Substrate-product reading:** 1D spectral fingerprint (kappa_3 alone) expands to 3D (kappa_3, kappa_4, kappa_6) at N=32768, making the audit certificate cryptographically harder to forge.
**Tier hint:** extends COMBO-3 audit API surface; locks in higher-cumulant production certificate.
**Why now:** Higher cumulants converge only at large N; N=8192 has insufficient sample for reliable kappa_6 estimation.
**Pre-reg HARD bands:** kappa_n matches alpha within 5% of free-Poisson prediction for both n=4 and n=6.
**Composition classification:** SCORE (measurement drill; outputs feed COMBO-3 cert but no discrete handoff required first).

### Anchor 3: Deletion-cert Z-ratio at N=32768

**Anchor pointer:** `deletion_cert_zratio_n32768_v1`
**Substrate-product reading:** Z-ratio ~3.6-5.1 sigma confidence at N=32768 vs ~2.0 sigma at N=8192. Crosses the production-grade GDPR audit threshold.
**Tier hint:** cap_map killer feature #1 (deletion certificate); this anchor is the production-N gate.
**Why now:** 2.0 sigma at N=8192 is marginal for product claims; 3.0+ sigma required for "production-grade GDPR audit" narrative.
**Pre-reg HARD bands:** Z-ratio >= 3.0 sigma over null.
**Composition classification:** SCORE (standalone certificate measurement).

### Anchor 4: COMBO-3 unified-API smoke at N=32768

**Anchor pointer:** `combo3_unified_api_n32768_v1`
**Substrate-product reading:** Validates the 5-method API uniformity theorem (algebraic theorem, not engineering convention) at production scale. All 9 matrix-trace primitives + kappa_3 update + CNDC + cert read from shared Krylov buffer {xi, W*xi, W^2*xi} at N=32768.
**Tier hint:** cap_map new row "5-method audit API as algebraic theorem" (currently 🔬 pending COMBO-3 HP1-HP5 at N=4096-8192). N=32768 cloud cell provides production-scale ratification.
**Why now:** N=4096 COMBO-3 runs in Wave 2 on remote GPU. Cloud cell validates the same theorem at 8x larger N in the same batch -- marginal cost near zero inside single Lambda load.
**Pre-reg HARD bands:** ALL 5-method primitives match closed-form within 1e-10 (same as Wave-2 COMBO-3 bands but at N=32768).
**Composition classification:** PIPELINE (5-method API: all 9 primitives + cert + kappa_3 read from same Krylov buffer; end-to-end functional test required; single-pipeline not SCORE because shared-buffer uniformity is the theorem being tested).

### Anchor 5: COMBO-1 implicit Gram-solve + kappa_3 at N=32768

**Anchor pointer:** `combo1_gram_kappa3_n32768_v1`
**Substrate-product reading:** Architecture lock -- audit primitive lives on M x M Gram side, NOT N x N retrieval operator. At N=32768, locks the decision at production scale.
**Tier hint:** conditional on cap_map row needing ratification post Wave 2 COMBO-1 PASS at N=4096. If Wave-2 COMBO-1 HARd-PASSes cleanly, this cell confirms the architecture extends to N=32768.
**Why now:** Same reasoning as COMBO-3 -- marginal cost near zero inside single Lambda load. GATE: only ship if Wave-2 COMBO-1 is not a HARD-FAIL (if HARD-FAIL, skip this cell and save ~20% compute in the bundle).
**Pre-reg HARD bands:** HP1 MMD <0.02 retrieval vs dense; HP2 kappa_3(G) within 5% of M/N; HP3 write wall-time linear-in-M; HP4 SNR_emp/SNR_pred in [0.85, 1.15].
**Composition classification:** HANDOFF (discrete architecture decision: audit lives on Gram side YES/NO; no end-to-end score property needed, only the directional decision).

---

## Testbed autonomy

Testbed session is authorized to:
- Choose A100 vs A100-80GB instance based on memory math (W matrix at N=32768 = 4 GB FP32; W + X + activations at alpha=0.25 approximately 5.5 GB; headroom for 5-cell batch favors A100-80GB if cost delta is acceptable).
- Decide bundle implementation style: single Python script vs orchestrator script + 5 cell scripts.
- Set per-experiment --timeout per PROT-019 formula (1.5 * smoke_wall_s * (FULL_N/smoke_N)^exp * (FULL_seeds/smoke_seeds)); flag any cell estimated >14400s to orchestrator before queueing.
- Harden SCP-back per existing testbed pattern; preserve ALL result files even on partial failure.
- Skip Anchor 5 (COMBO-1 at N=32768) if Wave-2 COMBO-1 is a HARD-FAIL.
- Reduce alpha (load factor) if VRAM is insufficient, documenting the change.
- Write deliverable to: d:/AI/hd-instrument/notes/testbed_wave5_unified_n32768_results_2026-06-02.md

Testbed session is NOT authorized to:
- Dispatch Lambda instance before Wave 5 trigger (user authorization or auto post-Wave-4-PASS).
- Modify cap_map (orchestrator only after verdict).
- Add anchors beyond the 5 named above without orchestrator approval (per [[feedback-no-padding-experiments]]).
- Use smoke-checkpoint files from prior runs without verifying checkpoint key includes run_mode (per [[feedback-smoke-checkpoint-contamination]]).

---

## Engineering constraints (all mandatory)

- SINGLE Lambda batch, SINGLE bootstrap, SINGLE model load per [[feedback-batch-cloud-experiments]].
- set -ex + python -u + stdbuf -oL + tee to remote log file SCP'd back even on failure, per [[feedback-always-verbose-remote-dispatch]].
- ASCII-only in all print() / verdict_msg output per [[feedback-ascii-only-in-scripts]].
- Cloud-launch snapshot + reconcile: snapshot state BEFORE launch, retry transient 5xx, reconcile post-call per [[feedback-cloud-launch-snapshot-reconcile]].
- Lambda on-demand only (no spot/preemptible) per [[feedback-lambda-no-spot-api]]; 300s stuck-boot fast-fail.
- PROT-018 anchor-name `_n32768` suffix is binding on every anchor; PROT-018 exit-6 enforced at queue_add.py.
- Per-experiment --timeout required (PROT-019); >14400s requires pre-ship review.
- Composition classification declared above (SCORE/HANDOFF/PIPELINE) per [[feedback-composition-classification]].

---

## Contract

**Pre-reg:** HARD bands declared per cell in Anchor candidates section above. No ex-post threshold setting.
**Self-test:** exp_dev verifies pre-reg bands and formula self-tests BEFORE coding (per [[feedback-strategy-spec-formula-selftests]]).
**Queue routing:** cloud queue (Lambda A100 / A100-80GB); NOT remote GPU (VRAM gate).
**Deliverable file:** d:/AI/hd-instrument/notes/testbed_wave5_unified_n32768_results_2026-06-02.md
**Ship command:** deferred to Wave 5 trigger; testbed prepares scripts now.
**Post-ship:** REMOTE VERIFY queue presence per [[feedback-ship-name-collision]] dedup check.

---

## Autonomy declaration

Testbed session has full autonomy over implementation, instance selection, and script structure. Testbed does NOT need to wait for orchestrator confirmation on engineering decisions within the bounds above. Testbed MUST confirm back to orchestrator before actual Lambda instance launch (cost commitment).

Acted-on 2026-06-02: testbed completed Wave 5 unified_n32768 bundle; results filed at testbed_wave5_unified_n32768_results_2026-06-02.md; cost $3.81 actual
