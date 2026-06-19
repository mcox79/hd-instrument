# exp_dev hand-off -- research: ZKL methodology stability 2x

Filed-by: research sub-agent (2026-06-07)
Trigger: notes/research_drill_zkl_methodology_stability_2x_2026-06-07.md
Pause state: check data/orchestrator_paused.flag before acting

Per [[feedback-no-experiment-design-in-prompts]]: this file provides anchor candidates,
context pointers, and strategic rationale. exp_dev designs actual anchors, sweep grids,
thresholds, and queue assignment autonomously. Pre-reg bands below are RESEARCH
recommendations -- exp_dev validates and may refine before queue dispatch.

---

## Pause state block

Before dispatching any anchor: verify data/orchestrator_paused.flag does NOT exist (or
confirm with orchestrator). Do not ship if paused.

---

## Why this hand-off exists

The cycle-164 entropy-max FALSE PASS root cause analysis revealed that MarianMT
do_sample=True temperature=1.3 top_k=50 with no seed is an extreme-value statistic
estimator. Run-to-run variance is structural, not a bug. The cycle-151 ZKL=0.22 and
cycle-164 ZKL=0.748 baseline are both valid draws from the same process. This means
the 0.22 number in the privacy pitch is not a reproducible system property.

Three cheap CPU pre-tests characterize this variance. They are independent of the T1-T5
nonlinear-mitigation pre-tests in the prior handoff (exp_dev_handoff_research_zkl_alternatives_crazy_ideas_2026-06-07.md).
These can run in parallel with T1/T2.

---

## Anchor Candidates (rank-ordered by cost and criticality)

### A. ZKL-SEED-SWEEP (HIGHEST PRIORITY -- runs first)

Anchor pointer: ZKL-SEED-SWEEP-A (new; not yet queued)
Substrate-product reading: Quantifies run-to-run variance of the existing ZKL(50) harness
  under seed variation alone. Determines whether seed discipline alone makes the 0.22
  baseline defensible or whether the methodology is structurally fragile.
Tier hint: CPU laptop; ~3-4 hours wall time (10 sequential runs of existing harness)
Why-now: Fastest path to knowing whether "ZKL=0.22" is a defensible number or a lucky
  draw. Results directly update what we can say to customers. Can run this week.
  Blocks accurate framing of the customer privacy pitch.

Pre-reg bands (research recommendation; exp_dev validates):
  HARD-PASS: std(ZKL_max across 10 seeds) < 0.05 AND max-min < 0.12
    -> Seed discipline rescues single-point metric; adopt seeded protocol; 0.22 is defensible
  HARD-FAIL: std(ZKL_max) >= 0.12 OR max-min >= 0.35 across 10 seeds
    -> Max-over-K methodology cannot support single-point claims; switch to mean-over-K + CI
  MID-BAND: std in [0.05, 0.12] AND max-min in [0.12, 0.35]
    -> Report CI; mean-over-K may be sufficient; run pre-test B before deciding

Setup: torch.manual_seed(seed) for seed in range(10) before each MarianMT paraphrase
  batch. Same KB, same 50 member/non-member query pairs, same T=1.3 top_k=50 do_sample=True.
  Record ZKL(50) for each seed. Report [ZKL_0, ..., ZKL_9], mean, std, min, max.

Expected outcome (research prediction, not pre-reg): HARD-FAIL (std >= 0.12). Based on
  extreme-value theory, K=50 at T=1.3 is far below the sample size needed for stable
  extreme-value estimation. The cycle-151 vs cycle-164 3.4x ratio is evidence.

### B. ZKL-MEAN-VS-MAX (runs after A, or in parallel on same data)

Anchor pointer: ZKL-MEAN-VS-MAX-B (new; not yet queued)
Substrate-product reading: Tests whether switching from max-over-K to mean-over-K
  reduces variance enough to support stable privacy reporting. Mean-over-K is the
  simplest methodological fix -- one line change in the harness.
Tier hint: CPU laptop; zero additional compute if using pre-test A data
Why-now: If pre-test A HARD-FAILs (as expected), pre-test B determines the easiest fix.
  Mean-over-K can be implemented in 2 hours and changes no other harness logic.

Pre-reg bands:
  HARD-PASS: std(ZKL_mean across 10 seeds) < 0.04
    -> Mean construction is stable; adopt as primary metric; privacy claim is defensible
  HARD-FAIL: std(ZKL_mean) >= 0.08 across 10 seeds
    -> Even mean is too noisy at K=50; must increase K or switch model or use bootstrap CI
  MID-BAND: std(ZKL_mean) in [0.04, 0.08]
    -> Mean + CI framing (report range) is the right protocol

Note: this anchor has zero wall time overhead if run on the same 10 seeded batches as A.
The only cost is computing mean(ZKL_k) instead of max(ZKL_k) from the same paraphrases.
Implement both statistics in the same A run.

### C. ZKL-TEMP-SWEEP (independent of A and B; runs in parallel)

Anchor pointer: ZKL-TEMP-SWEEP-C (new; not yet queued)
Substrate-product reading: Tests whether lower temperature (T=0.5 or T=1.0) reduces
  run-to-run variance while preserving attack strength (ZKL_mean > 0.15). This determines
  whether a simple temperature reduction can replace mean-over-K as the variance fix,
  while keeping the max construction as the attack paradigm.
Tier hint: CPU laptop; ~1.5 hours wall (45 total runs: 3 temps x 5 seeds x K=50 paraphrases)
Why-now: If mean-over-K weakens the attack signal too much, lower temperature may offer a
  better diversity-stability tradeoff. Independent of A and B; no prerequisites.

Pre-reg bands:
  ACTIONABLE (T=0.5 viable): std(ZKL_max, 5 seeds) < 0.05 at T=0.5 AND ZKL_mean > 0.15
    -> Adopt T=0.5 seeded as standardized attack protocol
  DISQUALIFYING: T=0.5 produces ZKL_mean < 0.10 at std < 0.05
    -> Temperature reduction kills attack strength; lower T is not the right lever
  INFORMATIVE: T=1.0 gives std in [0.05, 0.09] with ZKL_mean > 0.15
    -> T=1.0 may offer better diversity-stability balance than T=0.5 or T=1.3

Sweep: temperatures [0.5, 1.0, 1.3], 5 independent seeds each, K=50 paraphrases per run.
  Report: [mean_ZKL_max, std_ZKL_max, mean_ZKL_mean, std_ZKL_mean] at each temperature.

---

## Dispatch order

A and C are independent -- dispatch in parallel.
B runs on the same data as A -- implement both statistics in the same A run (no extra cost).
None of A/B/C require orchestrator approval (CPU laptop tier, low cost, diagnostic).

Expected total compute: ~5-6 hours wall time for A+C (B is free from A data).

---

## Decision rules after A/B/C complete

If A HARD-PASS: seeded 0.22 is defensible. Use "ZKL=0.22 under seeded T=1.3 MarianMT
  attack" in technical docs. Qualified posture confirmed with a specific number.

If A HARD-FAIL AND B HARD-PASS: switch harness to mean-over-K. New baseline will differ
  from 0.22 (expect mean < max). Report mean ZKL with std across seeds in customer docs.
  Update privacy framing to Option A from research note Section 6.2.

If A HARD-FAIL AND B HARD-FAIL: ZKL harness is structurally unstable at K=50 T=1.3.
  Option 1 (fast): increase K to 100-200 and re-run B (more samples reduce mean variance).
  Option 2 (medium): implement bootstrap CI protocol (10-20 independent batches).
  Option 3 (long-term): LiRA KB-shadow adaptation (see research note Section 3.4).
  Escalate to orchestrator with recommendation before implementing option 2 or 3.

If C ACTIONABLE (T=0.5 viable): consider adopting T=0.5 seeded as the standardized
  protocol for all future ZKL runs. This changes the baseline (T=0.5 will produce lower
  attack-strength paraphrases than T=1.3). Escalate to orchestrator for protocol change
  decision -- do not silently change the baseline.

---

## Context pointers

- Research note (full analysis, 3000 words):
  d:/AI/hd-instrument/notes/research_drill_zkl_methodology_stability_2x_2026-06-07.md
- Prior ZKL alternatives drill (T1-T5 nonlinear mitigation pre-tests):
  d:/AI/hd-instrument/notes/exp_dev_handoff_research_zkl_alternatives_crazy_ideas_2026-06-07.md
- Prior privacy FINAL lock note (confirmed 0.22 floor, locked qualified posture):
  d:/AI/hd-instrument/notes/exp_dev_to_research_zkl_FINAL_lock_qualified_2026-06-07.md
- Privacy harness implementation:
  look for ZKL harness scripts in data/exp_*/; use same harness as cycle-151 and cycle-164

---

## Contract section

This hand-off is research-to-experiment. The 3 pre-test specs (A/B/C) are provided as
pre-reg recommendations. exp_dev is responsible for:
- Implementing seed control in the existing ZKL harness (torch.manual_seed before paraphrase)
- Computing both max and mean statistics in the same run
- Assigning all 3 pre-tests to CPU laptop queue
- Writing verdict notes for each pre-test per standard protocol
- Escalating A HARD-FAIL result to orchestrator before any customer-facing privacy
  documentation is finalized (the 0.22 number may need to be updated or qualified)

## Autonomy declaration

exp_dev may dispatch A, B, C without orchestrator approval (all are CPU diagnostic runs,
low cost, non-destructive). A HARD-FAIL result that would change the customer-facing
privacy number (currently 0.22) MUST be escalated to orchestrator before any product-tier
or compliance documentation is changed. Do not silently update the privacy baseline.
