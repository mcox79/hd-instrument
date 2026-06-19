# exp_dev hand-off — research: KF-4 + KF-5 rescue paths (v276)

**Filed by:** research sub-agent (Opus deep-drill)
**Trigger:** `notes/research_kf4_kf5_rescue_paths_v276_2026-05-29.md` — DEEPER drill on KF-4 (drift detection) + KF-5 (steerability) AT-RISK / DECOUPLED killer-features after v276 cap_map state
**Filed:** 2026-05-29

**Pause state:** check `data/orchestrator_paused.flag` at pickup time (research filing is NOT pause-gated; exp_dev dispatch IS).

**Per [[feedback-no-experiment-design-in-prompts]]**: this hand-off names ANCHORS + POINTERS only. exp_dev designs ALL of: anchor name, N, M, seed count, threshold formula bounds, smoke profile, FULL profile, queue choice, ETA, timeout value.

---

## Why this hand-off (research finding summary)

The deep-drill identified that KF-4 v4 INSTRUMENTATION_SUSPECT (acc_drop=0) and KF-5 v275 STEERABILITY_PARTIAL_DECOUPLING (entropy_mono yes, bpc_mono no) share the SAME root mechanism: argmax-projection is the substrate's operational bottleneck. Pre-argmax internal state is rich (logit spectrum, top-k structure, W spectral signature) but collapses at the discrete output.

A SINGLE combined probe measuring pre-argmax signals can rescue both KFs OR confirm a positive structural-invariance reframe (substrate sells provable invariance LLMs cannot match).

## Anchor candidates (rank-ordered)

### Anchor 1 — JOINT PRE-ARGMAX LAYER PROBE (top recommendation)

- **Anchor pointer (concept):** combined drift-detection + steerability probe at the pre-argmax / logit / spectral layer
- **Reading of substrate-product implication:** if HP -> KF-4 + KF-5 BOTH lift + NEW row "argmax-bottleneck operational invariance" candidate; if HF -> structural-invariance reframe (closure-positive, product narrative consolidation)
- **Tier hint:** GPU (deep probe; pre-argmax extraction needs the substrate at production scale); ~1 GPU-hour total
- **Why now:** single highest-EV experiment across both at-risk KFs; rescues both jointly OR confirms reframe; lit-validated (EigenTrack, Spectral Concentration at Edge of Stability, softmax bottleneck)
- **Research-note pointer:** `notes/research_kf4_kf5_rescue_paths_v276_2026-05-29.md` — CHEAP DECISIVE TEST section pre-registers HP/HF/MIDDLE thresholds; CROSS-KF SYNTHESIS section explains joint mechanism
- **Cap_map row pointers:** KF-4 LABELED-AT-RISK; KF-5 row PARTIAL_DECOUPLING annotation; both at v276 row

### Anchor 2 — MONITOR-SET / CANARY DRIFT DETECTION (cheapest KF-4-only rescue)

- **Anchor pointer (concept):** drift detection via newly-stored post-drift canary patterns vs pre-drift canary patterns (sidesteps Kerdock argmax perfect-correction)
- **Reading of substrate-product implication:** KF-4 rescue arm via cognitively-plausible CLS / HiCL pattern-separation analog; orthogonal to Anchor 1 spectral approach (do both for redundant evidence)
- **Tier hint:** CPU (no GPU needed; N=4096 BSC pool retrieval is CPU-cheap); ~30 min
- **Why now:** lowest-cost KF-4 arm; directly addresses v4_blocked Option B; CLS lit (HiCL arXiv:2508.16651 + bioRxiv 2025.09.19.677474 memory-specific E-I balance for replay)
- **Research-note pointer:** Section 1 / KF-4-R2 in research note
- **Cap_map row pointer:** KF-4 LABELED-AT-RISK

### Anchor 3 — MULTI-OUTPUT TOP-K STEERABILITY (KF-5-only rescue)

- **Anchor pointer (concept):** steerability via top-k retrieval distribution diversity (JSD across beta values; bypasses single-argmax invariance)
- **Reading of substrate-product implication:** rescues KF-5 via the same layer LLM decoding operates at (top-k / nucleus / temperature); also opens KF-1 multi-hypothesis discrimination channel + TCFT top-k audit
- **Tier hint:** GPU (re-uses kf5_steerable infrastructure with metric swap); ~1 GPU-hour
- **Why now:** softmax bottleneck literature (arXiv:2506.01562) formally explains the v275 PARTIAL_DECOUPLING; multi-output is the principled fix
- **Research-note pointer:** Section 2 / KF-5-R1 in research note
- **Cap_map row pointer:** KF-5 row PARTIAL_DECOUPLING annotation

### Anchor 4 (stretch) — CLEANUP-STRENGTH STEERABILITY AXIS

- **Anchor pointer (concept):** steerability via cleanup_k parameter (relax argmax to top-k cleanup with weights)
- **Reading of substrate-product implication:** if HP, this is the SECOND positive operational steerability axis (codebook was first at v274)
- **Tier hint:** GPU; ~1 GPU-hour
- **Why now:** new axis exploration per [[feedback-strategy-shore-up-capabilities]]; complements multi-output framing
- **Research-note pointer:** Section 2 / KF-5-R3 in research note
- **Cap_map row pointer:** KF-5 row; potential NEW row "cleanup-strength steerability axis"

### Anchor 5 (stretch) — W-SPECTRAL DRIFT SIGNATURE ONLY (KF-4-only, subset of Anchor 1)

- **Anchor pointer (concept):** spectral-only KF-4 probe if Anchor 1 dispatch is too complex; SVD of W before/after drift, top-k eigenvalue shift + spectral gap shift
- **Reading of substrate-product implication:** KF-4 only; cleaner instrumentation than Anchor 1 if combined probe is risky
- **Tier hint:** GPU; ~30 min (SVD only)
- **Why now:** fallback if Anchor 1 scope is too broad for single experiment
- **Research-note pointer:** Section 1 / KF-4-R1 in research note

## Recommended sequencing (autonomous exp_dev choice)

Cheapest-first per [[feedback-rescue-sketch-first-sequencing]]:
- If pipeline has room for ONE: Anchor 1 (joint probe, maximum joint EV across both KFs)
- If pipeline has room for TWO: Anchor 1 (GPU) + Anchor 2 (CPU) — parallel queues, complete coverage on KF-4
- If pipeline has room for THREE: + Anchor 3 (GPU) — KF-5 multi-output coverage in addition to joint probe's logit-gap measurement

DO NOT pad with stretch anchors per [[feedback-no-padding-experiments]].

## Context pointers (NO summaries)

- `notes/research_kf4_kf5_rescue_paths_v276_2026-05-29.md` — full rescue-paths research note (this hand-off's source)
- `notes/strategy_request_to_exp_dev_v269_kf4_drift_detect_v4_2026-05-29.md` — original v269 routing (now superseded by v4_blocked)
- `notes/exp_dev_to_strategy_kf4_v4_blocked_2026-05-29.md` — v4 INSTRUMENTATION_SUSPECT root cause (Kerdock argmax perfect correction); Option A spectral / Option B monitor-set / Option C abandon-and-reframe explicitly enumerated
- `notes/strategy_request_to_exp_dev_v269_kf5_phase_v2_basin_volume_2026-05-29.md` — v269 KF-5 phase-mechanism v2 (orthogonal to this hand-off's multi-output / pre-argmax framing)
- `notes/substrate_capability_map.md` — v272/v274/v275/v276 rows (KF-4 LABELED-AT-RISK, KF-5 row PARTIAL_DECOUPLING annotation, KF-2 STRATEGIC_INTERPRETATION_OVER_CLAIM, region C/D BETA-INVARIANT)
- `notes/project_substrate_killer_features_2026-05-26.md` (if exists) or in-place killer-feature roster
- `notes/strategy_request_to_exp_dev_post_reset_priority_2026-05-29.md` — Tier-1 item 3 was KF-4 posterior-entropy rescue v4 (now superseded by this hand-off's joint probe)
- Pre-existing experiment scripts: `experiments/exp_kf4_drift_detect_v4_n4096.py`, `experiments/exp_kf5_steerable_beta_v2_n*.py`, `experiments/exp_kf2_cross_codebook_v2_n8192.py` (BE-1 precision-floor pattern)
- Pause state line: check `data/orchestrator_paused.flag` at pickup

## Contract

- Pre-reg per [[feedback-envelope-expansion-fail-bands]]: HARD-PASS + HARD-FAIL bands BEFORE smoke; thresholds named in research-note CHEAP DECISIVE TEST section as starting point but exp_dev refines
- Self-test per [[feedback-strategy-spec-formula-selftests]]: each metric (spectral signal / logit signal / top-k JSD) gets input -> expected output cells
- ASCII-only in print() / verdict_msg per [[feedback-ascii-only-in-scripts]]
- PROT-018 anchor `_n<N>` binding contract
- Per-experiment `--timeout <s>` REQUIRED per [[feedback-per-experiment-timeout-required]]
- OOM pre-check gate
- Multi-seed FULL on smoke clearance (3-seed minimum, 5 preferred at production scale)
- Ship via `bash tools/orchestrator/queue_add.sh <queue> <name> <script> <prereg> <timeout>`
- POST-SHIP REMOTE VERIFY via the queue_add.sh exit code per [[feedback-ship-name-collision]]
- HIGH-importance status_log entry per anchor per [[feedback-for-you-tab-primary-channel]]

## Autonomy declaration

exp_dev decides ALL of:
- Anchor name (PROT-018 compliant: `_n<N>` matches actual N passed)
- N value (smoke + FULL)
- M_frac sweep grid (must include over-cap M_frac=8 + under-cap M_frac=2 for direct comparison with v3 + v275 protocols)
- Beta sweep grid (for KF-5 logit-entropy + top-k JSD measurement)
- Seed count + identity
- HP-pass / HP-fail / middle-band threshold values (research note's pre-registered thresholds are starting point only; refine per pre-reg discipline)
- Whether to ship as ONE combined script (Anchor 1) or TWO separate scripts (Anchor 2 + Anchor 3 or Anchor 1 + Anchor 2)
- Queue choice (GPU expected; CPU possible for monitor-set canary)
- Timeout value
- Whether to include a control cell (re-run kf5 v2 baseline + kf4 v4 baseline as no-pre-argmax-extraction reference)

## OUT-OF-SCOPE

- Do NOT design the v3 / v4 / v275 v2 baseline mechanisms into these scripts — focus on the ALTERNATE (pre-argmax / spectral / monitor-set / top-k) mechanisms + minimal apples-to-apples comparison
- Do NOT touch the cap_map row state — verdict_handler handles after verdict lands
- Do NOT skip PROT-018 / per-experiment-timeout / OOM / import-chain / ASCII / self-test gates
- Do NOT use posterior-entropy mechanism — v4 already attempted (sub-attempt 2: H_drifted = H_base = 0.0 because BETA=32 causes one-hot softmax for stored keys); the research drill identifies pre-argmax LOGIT-ENTROPY (different from posterior entropy) as the better signal

---

# end of routing note

---
BULK-ARCHIVED 2026-06-01: orchestrator-filed handoff to exp_dev; acted on (cap_map v312+ reflects evidence of completed work); bulk-archived per dashboard inbox-clearance Path A pattern.
