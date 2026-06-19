# exp_dev hand-off -- research: Pattern B payload magnitude control

Filed-by: research sub-agent
Trigger: notes/research_drill_pattern_b_payload_magnitude_control_2x_2026-06-07.md
  (C6 diagnostic confirmed payload-magnitude as dominant chain-k234 HF cause)
Pause state: check data/orchestrator_paused.flag before dispatching

Per [[feedback-no-experiment-design-in-prompts]]: this file provides TASK + WHY + CONTRACT +
AUTONOMY. Exp_dev designs ALL anchor parameters, sweep grids, threshold formulas, queue
placement, and ETA. This file does NOT specify numerical parameters beyond what appears in
the HARD-PASS/HARD-FAIL bands below (those are pre-registration constraints, not design).

---

## WHY NOW

Pattern B is in production at 16 bytes/fact and compliance-capable (Art 12 + Art 17 HP,
cycle 162). The remaining gap is chain-k234: chained multi-payload composition at K=2,3,4
returns HF because payload magnitude grows O(K^2) across chain steps. The C6 diagnostic
confirmed this is the dominant factor (payload-magnitude > K-depth > bundle-saturation).

Post-bind L2 normalization (Mechanism 1 in the research note) is a 2-3 day fix with
P_deflated=0.53 for full chain-k234 recovery. The compliance pitch (structured multi-attribute
queries like "list all AI decisions where deployer=EU-regulated AND audit-log=missing AND
date=after-2026-08") requires chain-k234 capability. This fix unblocks that.

All three pre-tests below are CPU-only, ~30 min each. No cloud required.

---

## ANCHOR CANDIDATES (rank-ordered)

### Anchor 1 -- chain-k234 normalization recovery smoke (PRIMARY)

Pointer: research note Section 4, Pre-Test A.
Substrate-product reading: measures chain-k composition acc at K=2, K=3, K=4 with and without
  post-bind L2 normalization. Determines whether Mechanism 1 recovers chain-k234 from HF to
  MID or HP. If HARD-PASS: ship normalization in v1.1. If HARD-FAIL: escalate.
Tier hint: laptop CPU; N=4096, M=50 bipolar production stack; numpy-only; ~30 min wall.
Why now: cheapest conclusive test available. Rules in or out Mechanism 1 in one run.

HARD-PASS band: chain_k234_acc_normalized >= 0.85 at K=2, K=3, K=4 simultaneously.
  AND unbind_substitute_acc = 1.0, khop_compose_acc = 1.0 (existing HP tests unchanged).
HARD-FAIL band: chain_k234_acc_normalized < 0.70 at K=4 despite normalization.
  OR any existing HP test drops below 0.90.
MID-BAND: 0.70 <= acc < 0.85 at K=4 -- partial recovery, acceptable if HP tests pass.

Required pre-step (exp_dev executes, not research): production stack audit.
  - grep Pattern B write path for L2-norm comparisons (||q - stored||, threshold on norm)
  - if found: convert to cosine equivalents before running smoke
  - log findings in anchor notes regardless

---

### Anchor 2 -- capacity retention under normalization (VALIDATION)

Pointer: research note Section 4, Pre-Test B.
Substrate-product reading: verifies normalization does not reduce bundle capacity M_crit.
  Theory predicts normalization should NOT hurt capacity (cosine SNR = 1/sqrt(K-1) unchanged).
  In practice: any magnitude-threshold gating in the bundle query path could cause a dip.
  This test is the safety check before v1.1 shipping.
Tier hint: laptop CPU; sweep M from 10 to 80; ~20 min wall. Can batch with Anchor 1.
Why now: Anchor 1 passing is necessary but not sufficient. Capacity retention is the
  complementary confirmation.

HARD-PASS band: M_crit_normalized >= M_crit_baseline (normalization does not reduce capacity).
  M_crit defined as M where retrieval acc drops below 0.90.
HARD-FAIL band: M_crit_normalized < 0.90 * M_crit_baseline (>10% capacity degradation).

---

### Anchor 3 -- causal chain depth-50 confirmatory under normalization

Pointer: research note Section 4, Pre-Test A additional check; Section 5 interaction 5.4.
Substrate-product reading: the causal-chain depth-50 test is an EXISTING HP result. Running
  it with post-bind normalization active confirms that normalization does not disturb the
  depth-50 capability. Theory predicts slight improvement (depth-50 has magnitude accumulation
  too, which normalization controls). This anchor generates the depth-50 HP confirmation
  needed before the v1.1 shipping brief.
Tier hint: laptop CPU; same N=4096, M=50; ~15 min wall. Batch with Anchors 1 and 2.
Why now: confirmatory test only. Zero additional cost if batched with Anchor 1.

HARD-PASS band: depth_50_acc >= depth_50_acc_baseline (normalization preserves or improves HP).
HARD-FAIL band: depth_50_acc < 0.95 * depth_50_acc_baseline (normalization hurts depth-50).

---

## CONTEXT POINTERS

Research note: d:/AI/hd-instrument/notes/research_drill_pattern_b_payload_magnitude_control_2x_2026-06-07.md
Afternoon brief: d:/AI/hd-instrument/notes/research_POST_COMPACTION_BRIEF_2026-06-07_afternoon.md
Compression analogs: d:/AI/hd-instrument/notes/research_drill_pattern_b_compression_analogs_3x_2026-06-07.md
Compositional storage: d:/AI/hd-instrument/notes/research_drill_pattern_b_compositional_storage_3x_2026-06-07.md
Cycle 162 HP verdict: causal_gdpr_erasure_composition HP and ptb_reuse_index_cache HP
  (exact metrics.json path: data/exp_<anchor>/metrics.json per [[feedback-metrics-path-exp_prefix]])

---

## CONTRACT

- Exp_dev designs ALL anchor parameters, sweep grids, threshold formulas, queue placement, ETA
- Exp_dev verifies formula self-tests before coding (per [[feedback-strategy-spec-formula-selftests]])
- Exp_dev checks queue.json for name collisions before shipping (per [[feedback-ship-name-collision]])
- ASCII-only in print()/verdict_msg (per [[feedback-ascii-only-in-scripts]])
- All three anchors are CPU-only: run on laptop CPU runner NOT remote GPU runner
- Production stack audit (grep for L2-norm comparisons) is required BEFORE Anchor 1 runs
- If HARD-FAIL on Anchor 1: do NOT modify production stack; file escalation note to research
- If HARD-PASS on all 3: file shipping authorization to orchestrator for v1.1 normalization patch

## AUTONOMY DECLARATION

Exp_dev has full autonomy to:
  - Choose exact parameter values within the pre-reg bands
  - Batch or sequence the three anchors
  - Select queue placement (laptop CPU is mandatory for all 3; GPU not needed)
  - Write the normalize_per_bind() function and integration points
  - Determine the exact L2-threshold audit scope
  - Write the v1.1 shipping brief if all 3 pass
  - Escalate to research if unexpected failure modes appear beyond the pre-reg spec
