# Research — 5 new directions worth exploring (USER ANALYSIS, verbatim)

**Filed**: 2026-05-24
**Source**: User analysis delivered to orchestrator inline cycle, treated as Research deliverable
**Pause state at filing**: ACTIVE
**Cap_map at filing**: v183 (commit cf69a58 last referenced in exp_dev handoff)
**Context**: 5 new substrate-research directions ranked by leverage. All five reframe Bet B's ceiling as a CHARACTERIZATION problem rather than a CLOSURE problem.

---

## VERBATIM USER ANALYSIS

> 5 new research directions worth exploring, ordered by leverage:
>
> **1. Sample-complexity and storage-capacity scaling for multi-task retention.** Missing axis under Bet B's ceiling. Hold task count fixed, sweep M (substrate width or pool size) over 2x-4x, measure retention_A. If retention rises monotonically with M, ceiling is capacity-bound -> product story becomes "retention scales with substrate size." If plateaus, ceiling is interference-bound -> product story is "70-92% retention is what this substrate does." Single most informative experiment for Bet B closure that hasn't been run. Adjacent research angle: PAC-Bayes bounds for outer-product Hebbian memories under sequential tasks.
>
> **2. Replay-composition theory.** Substrate-specific question: does replaying Phase A data weighted by bundle-norm (high-density regions of W) outperform random replay? Replay-by-vulnerability is unexplored. Cheap experiment, potentially closes the 7pp gap to compound.
>
> **3. Task representation geometry as load-bearing variable.** HIGHEST-LEVERAGE per user. Project each corpus's bigram PPMI distribution into substrate W-space, compute pairwise spectral distance (KL on eigenvalue distributions, Wasserstein on bundle distributions). Plot retention_A vs A->B distance, A->C distance. If 91-92% ceiling moves predictably with task-pair geometry, product story becomes "substrate retains X% at distance D; predict any task pair before training."
>
> **4. MoE M-dependence as phase transition in cross-talk.** Derive critical M_c above which MoE gating noise drops below cleanup tolerance. Tractable with M-P/BBP machinery R16 used for noise-sigma=16 prediction. Closed-form prediction within 20% of empirical pass/fail boundary moves MoE from "3/8 cells pass" to "passes above predicted M_c."
>
> **5. Substrate-as-disordered-magnet coarsening dynamics.** R29 predicted Allen-Cahn t^(1/2) decay for Bet B retention; not measured. Measure retention_A as function of Phase-C training duration t. If retention_A(t) ~ 1 - c*t^(1/2), substrate-novel prediction validated. Cheap; addresses Bet M's first multi-probe criterion directly.

**User explicit framing**:
- "All five reframe Bet B's ceiling as a characterization problem rather than a closure problem."
- "Direction 3 is single highest-leverage."
- "Directions 1, 3, 4 attack characterization; 2, 5 are cheap additions."

---

## Triage classification

| Dir | Title | Type | Leverage | Cost | Cluster |
|---|---|---|---|---|---|
| 1 | Sample-complexity scaling for multi-task retention | Empirical (Bet B M-sweep) + PAC-Bayes adjunct (pure math) | HIGH (informative for closure) | Medium GPU (multi-N x M sweep) | Characterization |
| 2 | Replay-composition by bundle-norm weighting | Empirical (cheap) | MEDIUM (7pp gap rescue) | Cheap GPU | Cheap addition |
| 3 | Task-representation geometry as load-bearing variable | Empirical (spectral distance regression) | **HIGHEST** | Medium-cheap (analytic on existing corpora + small sweep) | Characterization |
| 4 | MoE M-dependence as phase transition | Pure-math closed form (M_c derivation via M-P/BBP) THEN empirical verification | HIGH (cap_map MoE row state-change) | Cheap (math derivation; empirical re-use existing scripts) | Characterization |
| 5 | Allen-Cahn coarsening retention_A(t) ~ 1 - c*t^(1/2) | Empirical (cheap; existing Bet B pipeline + t-sweep) | MEDIUM (Bet M multi-probe criterion #1) | Cheap GPU | Cheap addition |

## Ship-list ordering (locked)

**Empirical experiments to ship via exp_dev (in this order)**:
1. Direction 3 (task-geometry; highest leverage)
2. Direction 1 (Bet B M-sweep)
3. Direction 5 (Allen-Cahn t^(1/2); cheap)
4. Direction 2 (replay-by-bundle-norm; cheap)

**Pure-math Research drills to dispatch in parallel**:
- Direction 1 adjunct: PAC-Bayes bounds for outer-product Hebbian memories under sequential tasks
- Direction 4: closed-form M_c prediction for MoE cross-talk via M-P/BBP

Direction 4 empirical verification waits until Research delivers M_c formula.

## Discipline citations carried into dispatch prompts

- Per [[feedback-no-experiment-design-in-prompts]]: orchestrator hands the DIRECTION; exp_dev/Research design parameters/thresholds/queue/anchor-name.
- Per [[feedback-no-smoke]]: HARD-PASS and HARD-FAIL bands pre-registered before run.
- Per [[feedback-2x-means-depth]]: not applicable here (these are NEW directions, not 2x re-runs).
- Per [[feedback-dispatch-wrappers-default]]: Agent unavailable in sub-agent context (post-compaction brief Section 2) -- orchestrator dispatches sub-agents inline this cycle.
- Per [[feedback-for-you-tab-primary-channel]]: status_log entry with plain_language + importance after dispatch.
