# exp_dev hand-off -- research: strategic_priority_analysis

**Filed-by:** research sub-agent (2026-06-07)
**Trigger:** Strategic priority analysis drill -- step-back survey of blocking characteristics and performance barriers
**Research note:** d:/AI/hd-instrument/notes/research_drill_strategic_priority_analysis_2026-06-07.md

Per [[feedback-no-experiment-design-in-prompts]]: this file provides task + why + context pointers. Exp_dev decides anchor names, sweep grids, threshold formulas, queue routing, and all cell-design specifics autonomously.

---

## Pause state block

Check d:/AI/hd-instrument/data/orchestrator_paused.flag before dispatching anything. If flag exists: do NOT queue. Read flag first line for context.

---

## Anchor candidates (rank-ordered)

### 1. Encoder geometric alignment audit
**Why:** Rank-1 blocker. The 17.43x capacity lift from Llama-1B + PCA whitening has no geometric characterization. The BGE-large d_eff=40 empirical cap (Drill 5 theory refuted) has no replacement model. Geometric alignment may be the operative variable governing encoder capacity and could degrade silently on out-of-distribution inputs.
**Substrate-product reading:** If alignment entropy < 2 bits in any domain, the encoder geometry is the binding capacity tax -- the 17.43x lift is domain-specific, not stable. If alignment entropy > 3.5 bits, PCA whitening is working as intended across domains.
**Tier hint:** CPU smoke viable, then CPU full. No GPU needed at N=500 keys.
**Why-now:** This is a characterization task ($0, ~20 min CPU) that could close or reopen multiple research lines. The sooner this number exists, the sooner the product narrative can be grounded.

### 2. Adaptive adversarial KF-1 stress test
**Why:** Rank-2 blocker. KF-1 reports 0.977/0.983 on non-adaptive paraphrase. Adaptive attackers (iterative confidence-guided word substitution) are structurally harder and untested. The compliance-sidecar GTM requires this to hold under adversarial conditions.
**Substrate-product reading:** Evasion rate > 3x non-adaptive at 10 iterations means the KF-1 architecture requires adversarial training before deployment. Evasion rate < 1.5x means current architecture is robust.
**Tier hint:** CPU. Non-trivial loop but no GPU. ~1 hour wall.
**Why-now:** Product narrative (physics-grade guarantees) is directly tested here. Any product claim about KF-1 adversarial robustness must survive this test.

### 3. Pseudoinverse write throughput vs N benchmark
**Why:** Rank-3 blocker. Pseudoinverse write rule gives "infinite" lift on real keys vs Hebb (cycle 141). The throughput (writes/second at production N) is unmeasured. O(N^2.376) matrix inversion may be a hard production ceiling.
**Substrate-product reading:** If throughput < 50 writes/second at N=8192, the write rule requires approximation (SMW incremental update or rank-k pseudoinverse). If throughput > 200 writes/second at N=16384 GPU, the rule is production-viable as-is.
**Tier hint:** CPU for N<=4096; GPU for N=8192/16384. Profiling run, not a multi-seed sweep.
**Why-now:** This is the number a customer will ask first. It does not exist yet. $0 or minimal GPU cost.

### 4. Compound stack integration test
**Why:** Rank-10 blocker. 9 production components are individually validated; the full stack is untested as a unit. Compound failure modes (e.g., pseudoinverse + sparse-KEY + multi-head interaction) could silently degrade any individual-component guarantee.
**Substrate-product reading:** Stack recall@1 < 0.65 (worse than best single component by >15pp) = destructive interaction present; must bisect before deployment claims. Stack recall@1 > 0.82 = compound stack is coherent; integration is clean.
**Tier hint:** GPU beneficial (N=8192, 500 passages). ~1 hour.
**Why-now:** No deployment claim is credible without a stack-level integration test. This is the empirical grounding for all 11 production-ready capability claims.

### 5. M_max=50 censoring re-audit interpretation
**Why:** Rank-5. Four HF closures (norm-gate, kf1_contradiction, kf1_truthfulqa, multi_head_x_corruption) may be M_max=50 artifacts. Batch F re-audit is pending. If any of these are false negatives, the research lines should be reopened.
**Substrate-product reading:** If Batch F confirms all 4 are genuine HF, move resources to Blue Ocean priorities. If any one reverses, reopen that research line.
**Tier hint:** Interpret Batch F results when available. CPU re-run if needed. Exp_dev reads Batch F metrics and decides.
**Why-now:** These are research lines that may be incorrectly closed. The cost of reopening a true negative is low; the cost of missing a viable capability is high.

---

## Context pointers

- Research note (full analysis): d:/AI/hd-instrument/notes/research_drill_strategic_priority_analysis_2026-06-07.md
- Cap_map current state: d:/AI/hd-instrument/notes/substrate_capability_map.md
- Post-compaction brief: d:/AI/hd-instrument/notes/orchestrator_post_compaction_brief.md
- Production architecture snapshot: in task prompt (Llama-1B + PCA + pinv + alpha=0.005 + M=2 + CRT + sharding + continual-KV + KF-1)
- Batch F re-audit results: check d:/AI/hd-instrument/data/exp_*/metrics.json for norm-gate, kf1_contradiction, kf1_truthfulqa, multi_head_x_corruption

---

## Contract section

Exp_dev is expected to:
1. Check pause flag before any dispatch
2. Design cells for priorities 1-3 as CPU-first characterization tasks (not multi-seed sweeps; profiling runs)
3. Design priority 4 compound stack integration as a smoke first then full
4. Interpret Batch F results for priority 5 before queuing any new re-run
5. Write preregs with explicit HP/MID/HF bands (exp_dev decides thresholds)
6. Post-ship REMOTE VERIFY per standard protocol

Exp_dev does NOT need to:
- Re-derive the geometric alignment theory
- Re-run the KF-1 baseline (use existing 0.977/0.983 numbers as comparison baseline)
- Design sweep grids -- these are characterization/profiling runs, not sweeps

---

## Autonomy declaration

Exp_dev has full autonomy over: anchor names, N values, seed counts, queue routing, timeout formulas, pre-registration threshold formulas, smoke-to-full scaling decision, and order of dispatch. The research note provides strategic rationale; exp_dev decides all implementation specifics.
