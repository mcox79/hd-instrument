# exp_dev hand-off -- research: F4 multi_head_x_corruption re-audit

Filed-by: research sub-agent
Trigger: notes/research_drill_F4_multi_head_corruption_2x_2026-06-07.md
Pause state: check data/orchestrator_paused.flag before dispatch

Per [[feedback-no-experiment-design-in-prompts]]: this file names anchor candidates
and provides WHY + CONTRACT context only. Exp-dev owns all design decisions
(sweep grid, threshold formula, queue choice, ETA).

---

## Anchor candidates (rank-ordered)

### Anchor 1 (TIER-1, highest leverage)
Pointer: F4_pinv_reaudit
Substrate-product reading: cycle 137 F4 HARD_FAIL used Hebb write rule + M_max=50;
production stack now uses PINV + M_c=200 + sparse-KEY excluded. Re-testing under
production conditions is required to determine if the HF carries forward or is
Hebb-specific. The 2025 PRE literature (arXiv:2503.00241) shows PINV qualitatively
changes the noise envelope by eliminating spurious cross-term interference.
Tier hint: CPU ~30 min; straightforward parameterization of flip-fraction sweep.
Why now: F4 is the last unresolved item from the cycle 142 retroactive audit list.
The other 3 (F1/F2/F3) stood on category-mismatch grounds; F4 requires an actual
re-test because production conditions changed materially (write rule flip).

### Anchor 2 (TIER-2, architectural clarification)
Pointer: F4_wsharding_vs_wsharing
Substrate-product reading: the BFT analogy for multi-head retrieval holds ONLY if
heads query independent W shards. If all M heads share the same W matrix, corruption
of W corrupts all heads simultaneously (no BFT benefit). The 3.5x advantage at 5%
flip rate in cycle 137 is ambiguous -- could be shard-independent sampling or just
query diversity. Clarifying W-sharing vs W-sharding architecture determines whether
the multi-head advantage is BFT-robust or coincidental.
Tier hint: CPU smoke, ~10 min; architecture inspection + targeted test.
Why now: directly determines whether Anchor 1 results generalize to adversarial scenarios.

---

## Context pointers (file paths only)

- Research drill (full analysis): notes/research_drill_F4_multi_head_corruption_2x_2026-06-07.md
- Cycle 143 PINV LOCK context: check cap_map rows for pseudoinverse write rule lock
- Cycle 142 M_max censoring analysis: notes/ (grep retroactive_audit or cycle_142)
- HP-12 V1 RSA accumulator context: cap_map HP-12 row
- Production architecture (sparse-KEY exclusion): cap_map latest version

---

## Contract

Exp-dev delivers: at least one pre-registered anchor with HARD-PASS / HARD-FAIL /
MIDDLE-BAND thresholds; smoke gate before full run; write_metrics() used; verdict
written to data/exp_<anchor>/metrics.json.

## Autonomy declaration

Exp-dev owns: anchor naming, sweep grid parameters, threshold formula with self-test
cells, queue routing (CPU vs GPU), ETA estimate, cap_map implications. This handoff
provides task + why + context only.
