# Strategy -> Exp Dev request — 5 new research directions (post-v183, 2026-05-24)

**From**: Orchestrator inline (Strategy role) acting on user-delivered substantive 5-direction analysis
**To**: Exp Dev (next cycle)
**Cap_map**: v183 (commit cf69a58)
**Source analysis**: `notes/research_5_new_directions_2026-05-24.md`
**Pause state**: ACTIVE
**Companion Research request**: `notes/strategy_request_to_research_2026-05-24_5_directions_math.md` (pure-math drills for Direction 1 PAC-Bayes adjunct + Direction 4 closed-form M_c)

## Why this hand-off exists

Per [[feedback-no-experiment-design-in-prompts]]: orchestrator main thread MUST NOT specify N/M/seeds/thresholds/queue/anchor-names. This file hands the DIRECTION + falsifier statements + script-base pointers; exp_dev decides parameters and ships.

Per [[feedback-dispatch-wrappers-default]]: Agent tool unavailable in sub-agent context (post-compaction brief Section 2). Orchestrator's role this cycle is to file this routing note so the next exp_dev cycle can pick it up.

User explicit framing on these five directions: "All five reframe Bet B's ceiling as a characterization problem rather than a closure problem. Direction 3 is single highest-leverage. Directions 1, 3, 4 attack characterization; 2, 5 are cheap additions."

## Priority order (locked by user leverage ranking; exp_dev may surface objections via upstream-push if any direction's script-base is incompatible)

| # | Direction | User priority | Type | Default queue (exp_dev may revise) | Base script (reuse) |
|---|---|---|---|---|---|
| 1 | **Direction 3 — Task-representation geometry (HIGHEST LEVERAGE)** | TOP | Empirical: spectral distance regression vs retention_A | overnight_queue if compute-heavy / remote_cpu_queue if analytic | `experiments/exp_wave14d_betB_kovacs_v1.py` + spectral-distance utilities adapted from `experiments/exp_wave14_spectral_universality_kerdock_v1.py` |
| 2 | **Direction 1 — Sample-complexity / storage-capacity M-sweep for Bet B** | HIGH | Empirical: M-sweep at fixed task count | overnight_queue (multi-N x multi-M sweep is compute-heavy) | `experiments/exp_wave14_betB_4stage_continual_v1.py` or `experiments/exp_wave14d_betB_kovacs_v1.py` |
| 3 | **Direction 5 — Allen-Cahn t^(1/2) coarsening retention_A(t)** | MEDIUM (cheap addition) | Empirical: Phase-C duration sweep | overnight_queue (existing Bet B pipeline + t-sweep) | `experiments/exp_wave14_betB_4stage_continual_v1.py` or `exp_wave14d_betB_kovacs_v1.py`; reference theory at `notes/research_R29_ferromagnetism_domains_2026-05-21.md` |
| 4 | **Direction 2 — Replay-by-bundle-norm weighted vs random** | MEDIUM (cheap addition) | Empirical: weighted-replay vs random-replay comparison | overnight_queue (Bet B pipeline; small additional cost) | `experiments/exp_wave14_betB_compound_pertask_replay_v1.py` (already has replay machinery to extend) |
| 5 | **Direction 4 — MoE M-dependence empirical verification** | DEFER until Research delivers M_c | Empirical (waits on Research's M_c closed-form) | overnight_queue once Research drill closes | `experiments/exp_wave14e_moe_xtalk_smoke_v1.py` + full re-shipped MoE script (already in queue / completed) |

## Direction 3 — Task-representation geometry (HIGHEST LEVERAGE)

**Scope**: Project each corpus's bigram PPMI distribution into substrate W-space; compute pairwise spectral distance between task pairs (KL on eigenvalue distributions, Wasserstein on bundle distributions). Plot retention_A vs A->B distance and A->C distance across the existing Bet B corpora plus additional corpus pairs if available. Goal: show 91-92% retention ceiling moves PREDICTABLY with task-pair geometry.

**Falsifier statements (pre-reg these in your prereg)**:
- HARD-PASS: monotone-decreasing retention_A as spectral distance increases; r^2 of regression >= 0.6 across N >= 3 task-pairs -> substrate's retention ceiling is geometry-bound; product story becomes "substrate retains X% at distance D; predict any task pair before training."
- HARD-FAIL: r^2 < 0.2 OR non-monotone -> retention ceiling NOT geometry-bound; rules out the "predict any task pair before training" product story; suggests interference is dominated by something orthogonal to spectral structure.
- MIDDLE: 0.2 <= r^2 < 0.6; report bands and propose follow-up.

**Discipline citations**:
- Per [[feedback-no-smoke]]: both HARD-PASS and HARD-FAIL bands pre-reg before run.
- Per [[feedback-verify-implementations]]: spectral distance computation must match cited definition (KL on eigenvalue distributions, Wasserstein on bundle distributions). Audit the implementation against the math, not just the name.
- Per [[feedback-rehabilitation-after-rejection]]: if HARD-FAIL, file 3-5 axis-combination rescue sketches with closure.

**Autonomy declaration**: You (exp_dev) decide:
- Which spectral distance metric (KL on eigenvalues vs Wasserstein on bundle distributions vs both) leads.
- Which corpora pairs beyond the existing Bet B A/B/C; whether to synthesize additional corpora to extend the distance range.
- Whether to project PPMI into W-space via direct matrix product, randomized projection, or substrate's existing encoder.
- N, M, seeds, regression model, r^2 thresholds (within the bands above).
- Queue (overnight_queue vs remote_cpu_queue depending on compute profile).
- Anchor name.

## Direction 1 — Sample-complexity / storage-capacity M-sweep for Bet B

**Scope**: Hold task count fixed at Bet B's 3-corpus A->B->C pipeline. Sweep M (substrate width or pool size) over 2x-4x the current M. Measure retention_A at each M. Goal: determine if Bet B's ceiling is capacity-bound (rises with M) or interference-bound (plateaus).

**Falsifier statements**:
- HARD-PASS (capacity-bound): retention_A monotone-increasing in M across the sweep with retention_A(M_max) - retention_A(M_min) >= 10 percentage points -> ceiling is capacity-bound; product story is "retention scales with substrate size."
- HARD-FAIL (interference-bound): retention_A plateaus within +- 3 percentage points across the M-sweep -> ceiling is interference-bound; product story is "70-92% retention is what this substrate does."
- MIDDLE: any intermediate scaling; report bands.

**Discipline citations**:
- Per [[feedback-no-smoke]]: bands pre-reg before run.
- Per [[feedback-verify-implementations]]: M means substrate width OR pool size, exp_dev picks one and documents which.

**Autonomy declaration**: You decide M-sweep specifics (which interpretation of M, exact sweep values within 2x-4x range, N, seeds, thresholds, queue, anchor name).

## Direction 5 — Allen-Cahn coarsening retention_A(t) ~ 1 - c*t^(1/2)

**Scope**: Measure Bet B retention_A as a function of Phase-C training duration t. Goal: verify R29's substrate-novel prediction that retention follows Allen-Cahn t^(1/2) coarsening.

**Falsifier statements**:
- HARD-PASS: log-log regression of (1 - retention_A) vs t has slope in [0.4, 0.6] (consistent with t^(1/2)) with r^2 >= 0.7 -> substrate-as-disordered-magnet coarsening prediction validated; addresses Bet M's first multi-probe criterion.
- HARD-FAIL: slope outside [0.3, 0.7] OR r^2 < 0.4 -> Allen-Cahn coarsening NOT the right scaling law; Bet M multi-probe criterion #1 unsatisfied.
- MIDDLE: slope in [0.3, 0.4] or [0.6, 0.7] with r^2 >= 0.4; report bands.

**Reference**: `notes/research_R29_ferromagnetism_domains_2026-05-21.md` for the original prediction.

**Autonomy declaration**: You decide t-sweep range, N, seeds, thresholds (within the bands above), queue, anchor name.

## Direction 2 — Replay-by-bundle-norm weighted replay

**Scope**: Substrate-specific replay scheme. Weight Phase A replay samples by their bundle-norm (high-density regions of W) and compare retention_A vs uniform/random replay. Goal: test whether replay-by-vulnerability outperforms random replay; potentially closes the 7pp gap to compound.

**Falsifier statements**:
- HARD-PASS: bundle-norm weighted replay achieves retention_A >= 80% (closes 7pp gap from 73% baseline) at the same replay_frac as random -> replay-by-vulnerability validated; cheap rescue path for compound.
- HARD-FAIL: bundle-norm weighted replay achieves retention_A within +- 2pp of random replay across replay_frac values -> bundle-norm not the load-bearing weighting axis; replay-composition theory rejected.
- MIDDLE: 75% <= retention_A < 80% OR delta vs random in [2, 7]pp; report bands.

**Autonomy declaration**: You decide bundle-norm computation, replay_frac values, N, seeds, thresholds, queue, anchor name.

## Direction 4 — MoE M-dependence empirical verification (BLOCKED until Research delivers M_c)

**Scope**: Empirical verification of Research's closed-form M_c prediction for MoE cross-talk phase transition. WAIT for Research's drill at `notes/strategy_request_to_research_2026-05-24_5_directions_math.md` to deliver an M_c formula.

**Falsifier statement (placeholder until M_c arrives)**:
- HARD-PASS: empirical MoE pass/fail boundary matches predicted M_c to within +- 20%.
- HARD-FAIL: empirical boundary diverges from M_c by > 50% in either direction.
- MIDDLE: 20-50% divergence; report.

**Action**: Do NOT ship Direction 4 empirical script until Research delivers M_c. Surface to Strategy when ready.

## Discipline citations (carry into each prereg)

- Per [[feedback-no-experiment-design-in-prompts]]: you (exp_dev) own parameters; this note hands DIRECTIONS only.
- Per [[feedback-no-smoke]]: HARD-PASS and HARD-FAIL bands pre-reg before run.
- Per [[feedback-rehabilitation-after-rejection]]: if HARD-FAIL on any direction, file 3-5 rescue sketches per PROT-004.
- Per [[feedback-ascii-only-in-scripts]]: ASCII-only in print() / verdict_msg.
- Per [[feedback-pipeline-pacing]]: ship Direction 3 + Direction 1 first to keep GPU queue depth >= 2.

## Top-3 anchors to ship FIRST per user leverage ranking

1. **Direction 3** (task geometry; HIGHEST leverage) -> ship this cycle if smoke-pass.
2. **Direction 1** (Bet B M-sweep; single most informative for closure) -> ship this cycle if smoke-pass.
3. **Direction 5** (Allen-Cahn t^(1/2); cheap; Bet M criterion #1) -> ship this cycle.

Direction 2 (replay-by-bundle-norm) is the FOURTH ship priority; ship next cycle or this cycle if bandwidth allows.

Direction 4 (MoE M_c empirical) BLOCKED on Research drill.

## Queue state at hand-off (verified 2026-05-24)

- **overnight_queue** (GPU runner): GPU=RUN, depth=1 (per state_check); pipeline NOT in emergency-refill state.
- **remote_cpu_queue** (CPU runner): CPU=RUN, depth=9.
- **local_cpu_queue**: 0 (DEAD per cpu_runner_0 note in MEMORY.md).

Pipeline-pacing invariant per [[feedback-pipeline-pacing]]: depth >= 1 on GPU is satisfied but ship-this-cycle of Directions 3 + 1 + 5 keeps GPU depth healthy through next 24h.

## No blockers

User-delivered substantive analysis is the authoritative source. Exp Dev reads this file + `notes/research_5_new_directions_2026-05-24.md` for full context.

---
BULK-ARCHIVED 2026-06-01: pre-2026-05-25 backlog OR processed-but-not-archived; cap_map v311+ reflects evidence of acted-on work; per dashboard inbox-clearance Path A.
