# exp_dev hand-off -- research: LSH fan-out reduction 2x

**Filed-by:** research sub-agent (Sonnet)
**Date:** 2026-06-07
**Trigger:** Cycle 154 chain3_lsh_fanout_v1 MIDDLE_BAND; B_eff=40 at S=100;
  LSH rework required before Chain 3 K-hop is production-safe at scale.

**Research note:** notes/research_drill_lsh_fanout_reduction_2x_2026-06-07.md

**Pause state:** check data/orchestrator_paused.flag before dispatching any anchor.

Per [[feedback-no-experiment-design-in-prompts]]: exp_dev designs the actual
experiment scripts and pre-registration bands autonomously. This file provides
context pointers and ranked candidates only.

---

## Anchor candidates (rank-ordered, cheap-first)

### Anchor 1 (IMMEDIATE, 0.1 days): L2-normalization check
**Why now:** zero-cost sanity check. If normalization is not being applied, B_eff drops
  immediately without any design change.
**Substrate-product reading:** if B_eff drops from 40 to < 30 from normalization alone,
  v1 routing is partially fixed at zero engineering cost. Documents the root cause as
  infrastructure gap, not design limitation.
**Tier hint:** CPU smoke, < 30 min.
**Anchor pointer:** Pre-test 0 in research note Section 5.
**Pre-reg:** HARD-PASS B_eff < 30 from normalization. HARD-FAIL no change (already normalized).

### Anchor 2 (HIGH PRIORITY, 1.5 days): Cone correction B_eff test
**Why now:** cone anisotropy from c_d=0.48 (Cell A) is the most plausible primary driver
  of B_eff=40. Cone correction (subtract mean embedding direction) is a 1-2hr CPU test.
  If B_eff drops to < 20: Chain 3 v1 is production-safe without structural redesign.
**Substrate-product reading:** a single shared preprocessing step (mean-subtraction)
  simultaneously improves LSH fan-out AND reduces membership-inference exposure (same as
  privacy drill Path F). Engineering cost is effectively shared.
**Tier hint:** CPU, 2-3 hours wall including measurement.
**Anchor pointer:** Pre-test 1 in research note Section 5.
**Pre-reg:**
  HARD-PASS: B_eff < 20 (v1 production-safe, no further LSH work needed for v1).
  MIDDLE: B_eff in [20, 35] (partial progress; needs cosine re-rank supplement).
  HARD-FAIL: B_eff >= 35 (cone correction does not help; abandon this path; proceed to
    ensemble intersection with anisotropy root-cause investigation).

### Anchor 3 (CONDITIONAL, 2.5 days): Cosine re-rank recall check
**Trigger:** only if Anchor 2 gives B_eff in [20, 35] (MIDDLE band).
**Why:** cosine re-rank can force B_eff to exactly 20 by threshold, at the cost of
  possible recall loss. Need to measure recall loss before applying in production.
**Substrate-product reading:** if recall loss < 10% at B_target=20, cosine re-rank
  gives v1 a guaranteed B_eff=20 with minimal engineering. This is the fallback for
  v1 if cone correction alone gives B_eff=25-30.
**Tier hint:** CPU, 2 hours.
**Anchor pointer:** Pre-test 2 in research note Section 5.
**Pre-reg:**
  HARD-PASS: >= 90% true-positive shards retained in top-20.
  HARD-FAIL: < 70% retained; centroid re-ranking is not selective enough for v1.

### Anchor 4 (VERIFICATION, 1 day): Sparse-KEY K_max fallback test
**Why now:** the cycle 154 verdict assessed B_eff>20 as collapse risk, but may have
  assumed dense intermediates. Sparse-KEY encoding (alpha=0.005 vs 0.05) gives 3.16x
  K_max headroom (Gold 4.0). If B_eff=40 + sparse-KEY still gives K=12 recovery >= 95%,
  the LSH rework may not be production-blocking for v1.
**Substrate-product reading:** confirms whether the LSH rework is actually required for v1,
  or whether it is a v2 concern. If P4 (research note Section 6) passes, v1 ships on
  schedule without LSH changes; LSH work continues at v2 pace.
**Tier hint:** CPU, 3-4 hours wall.
**Anchor pointer:** Falsifiable prediction P4 in research note Section 6.
**Pre-reg:**
  HARD-PASS: K=12 recovery >= 95% at B_eff=40 with sparse-KEY intermediates (v1 not blocked).
  HARD-FAIL: K=12 recovery < 80% with sparse-KEY at B_eff=40 (v1 IS blocked; LSH rework
    is mandatory before ship).

---

## Context pointers

- Research note: d:/AI/hd-instrument/notes/research_drill_lsh_fanout_reduction_2x_2026-06-07.md
- Drill 5 FINAL (production architecture): d:/AI/hd-instrument/notes/research_drill_substrate_production_scaling_5x_chain3_drill5_FINAL_2026-06-07.md
- Prior LSH pool-search analysis: d:/AI/hd-instrument/notes/wave14e_lsh_for_bsc_research.md
- Privacy drill Path F (cone-correction shared step): d:/AI/hd-instrument/notes/ (grep "Path F" or "cone correction")
- K-hop noise formula (Gold 3.0): drill5 FINAL Section 1, Gold 3.0
- Sparse-KEY intermediates (Gold 4.0): drill5 FINAL Section 1, Gold 4.0

---

## Contract

exp_dev is authorized to:
  - Design and dispatch anchors 1-4 as CPU smoke runs (no cloud required)
  - Pre-register HARD-PASS/HARD-FAIL/MIDDLE bands per the research note
  - Escalate back to research if Anchor 2 HARD-FAILS (cone correction does not help)
  - Begin hierarchical LSH design work (Section 4 v2 spec) if bandwidth permits after
    anchor 1-4 results are in

exp_dev is NOT authorized to:
  - Commit to hierarchical LSH production implementation without anchor 2 + 4 results
  - Dispatch cloud GPU runs for these anchors (all are CPU-feasible)
  - Treat v1 as production-blocked if Anchor 4 passes (sparse-KEY fallback may be sufficient)

## Autonomy declaration

exp_dev decides: script design, pre-reg band widths, run order, test data generation,
  metric implementation, and queue placement. The above anchor descriptions are context
  for decision-making, not implementation specifications.
