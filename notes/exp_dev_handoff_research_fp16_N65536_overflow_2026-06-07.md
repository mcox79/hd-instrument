# exp_dev hand-off -- research: fp16 N=65536 overflow 3x deep

**Filed-by:** research sub-agent (2026-06-07)
**Trigger:** LVH #244 -- fp16 at N=65536 BLOCKED (production gate; cycle 144 G3 finding)
**Research note:** d:/AI/hd-instrument/notes/research_drill_fp16_N65536_overflow_3x_deep_2026-06-07.md
**Pause state:** Check data/orchestrator_paused.flag before dispatching.

Per [[feedback-no-experiment-design-in-prompts]]: this file specifies WHAT and WHY, not HOW.
exp_dev designs the anchors; selects sweep grids, thresholds, and queue placement autonomously.

---

## Why this is urgent

This is the substrate's ONE open production gate. All other deployment axes are locked.
The fix is theoretically trivial (dtype change) but must be empirically validated before
the production HP claim is made. The research note gives full theoretical grounding and
pre-registration thresholds.

---

## Anchor candidates (rank-ordered)

### Anchor 1 (MUST-DO FIRST): bf16 overflow elimination at N=65536
**Pointer:** Research note Section 2.1 + Section 5 Prediction 1
**Substrate-product reading:** Directly tests whether the one-line fix (torch.bfloat16) eliminates
NaN/Inf in all intermediate buffers at production N=65536. Binary smoke: overflow present or not.
**Tier hint:** Smoke / infrastructure validation. CPU may not suffice (bf16 requires A100+).
**Why now:** This is the production gate. If it passes, the gate closes. If it fails, escalate
to fp32 accumulation path immediately.
**Pre-reg from research note:** HARD-PASS = zero NaN/Inf at N=65536 for M <= 26,214.
HARD-FAIL = NaN/Inf in final retrieval output in bf16.

### Anchor 2: bf16 capacity parity vs fp32 at N=65536
**Pointer:** Research note Section 2.1 + Section 5 Prediction 2
**Substrate-product reading:** alpha_c(bf16) / alpha_c(fp32) ratio at N=65536.
Validates that the 7-mantissa-bit precision of bf16 does not degrade capacity beyond 5%.
**Tier hint:** Full validation. GPU required (bf16 compute native on A100/H100).
**Why now:** Needed to close the HP claim on production N=65536 capacity.
**Pre-reg from research note:** HARD-PASS = ratio > 0.95. MIDDLE-BAND = 0.80-0.95. HARD-FAIL = < 0.80.

### Anchor 3 (CONTINGENCY): fp32 accumulation fallback for legacy hardware
**Pointer:** Research note Section 2.2 + Section 5 Prediction 3
**Substrate-product reading:** Validates mixed fp16-store / fp32-accumulate path for V100/T4.
**Tier hint:** Only needed if Anchor 1 fails or if V100 deployment is required.
**Why now:** Contingency for non-A100 deployments; can be batched with Anchor 2.
**Pre-reg from research note:** HARD-PASS = alpha_c ratio > 0.98 with no NaN/Inf.

### Anchor 4 (RETROACTIVE AUDIT): Re-run 4 pending M_max audits under bf16
**Pointer:** Research note Section 8 (implications for 11 capabilities)
**Substrate-product reading:** The 4 pending M_max audits (norm-gate, kf1_contradiction,
kf1_truthfulqa, multi_head_x_corruption) may have been measured in fp16, understating true capacity.
Re-run under bf16 to verify or correct.
**Tier hint:** Can batch with Anchor 2 cycle.
**Why now:** Closes the retroactive audit backlog opened in cycle 144.

---

## Context pointers

- Research note (full analysis): d:/AI/hd-instrument/notes/research_drill_fp16_N65536_overflow_3x_deep_2026-06-07.md
- Cycle 144 verdict summary: d:/AI/hd-instrument/notes/orchestrator_to_research_results_summary_2026-06-06_cycle144.md
- Pseudoinverse throughput finding: notes/orchestrator_to_research_results_summary_2026-06-06_cycle144.md (g2 section)
- cap_map current state: check latest cap_map commit via git log

---

## Contract

exp_dev owns: anchor naming, sweep grids, queue routing, pre-reg thresholds (may refine
from research note bounds), cell recipes, self-test formulas.

Research has provided: theoretical characterization, overflow site identification, solution
path ranking, P_deflated estimates, and pre-registration bands.

Research has NOT provided: specific anchor names, eta sweep arrays, exact HP/MID/HF numerical
bounds (exp_dev calibrates these against its own formula-selftest protocol), queue choice or ETA.

## Autonomy declaration

exp_dev is fully autonomous within the bounds above. No further research input required to
dispatch Anchors 1 and 2. Anchor 3 and 4 may be batched at exp_dev's discretion.
