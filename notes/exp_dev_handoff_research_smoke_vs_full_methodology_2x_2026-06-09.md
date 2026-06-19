# exp_dev hand-off -- research: smoke vs full methodology (2x drill)

Filed-by: research sub-agent
Date: 2026-06-09
Trigger: notes/research_drill_smoke_vs_full_methodology_2x_2026-06-09.md
Pause state: check data/orchestrator_paused.flag before dispatching any anchor below

Per [[feedback-no-experiment-design-in-prompts]]: this file contains anchor candidates and context pointers only. exp_dev designs the actual anchors, pre-reg bands, and run configurations independently.

---

## Why this hand-off exists

Research found that smoke alpha=0.333 (n=80) closed a capability that full alpha=0.65 (n=1200) confirmed viable. Statistical analysis establishes:
1. The n=80 power to detect alpha=0.65 vs threshold=0.40 is essentially 100% (required n ~24). Therefore composition mismatch drove the gap, not sample size.
2. The Wilson 95% CI at n=80 was [0.232, 0.434] -- the threshold 0.40 was inside the CI. Point-estimate-based decisive closure was statistically unsupported.
3. PP-181 single-seed 0.781 -> 3-seed mean 0.697 (HP->HF) matches a false-pass rate of ~4.6% per seed at plausible metric sigma=0.05 and HP threshold=0.78.

Three protocol anchors emerge from this analysis that are ready for empirical validation.

---

## Anchor candidates (rank-ordered)

### Anchor P-SMOKE-1: Stratified smoke vs SRS smoke comparison
Anchor pointer: [SMOKE-STRAT-A]
Substrate-product reading: If stratified smoke alpha (3 strata, matched difficulty weights) agrees with full-run alpha within 0.05, that confirms composition mismatch was the primary driver of the smoke-vs-full gap. This closes the diagnostic loop and authorizes the stratified smoke protocol for all future capability gates.
Tier hint: Tier 2 validation (protocol calibration, not new capability)
Why now: The prior smoke-vs-full discrepancy is unresolved. Until we know whether composition or some other factor drove the gap, every subsequent smoke-based closure is under suspicion. This is a low-cost experiment (~1-2 CPU hours) with high diagnostic value.

### Anchor P-SMOKE-2: Multi-seed false-pass rate characterization
Anchor pointer: [SEED-VARIANCE-B]
Substrate-product reading: Run a capability anchor 10 times with different seeds. Compute the distribution of seed-to-seed variance (sigma_seed). Validate the analytical prediction that sigma_seed ~= 0.04-0.06 for perplexity-based metrics and ~0.01-0.02 for retrieval metrics. This calibrates the 3-seed rule and sets the HP-fragility boundary empirically.
Tier hint: Tier 2 calibration
Why now: The PP-181 false-pass cost a full-run dispatch to discover what a 3-seed smoke would have caught. Understanding sigma_seed per metric family prevents repeat classification errors.

### Anchor P-SMOKE-3: CI-band verdict logic A/B test
Anchor pointer: [CI-VERDICT-C]
Substrate-product reading: Re-run 5-10 historical smokes (archived query sets + results) under CI-band decision logic vs original point-estimate logic. Count disagreements (AMBIGUOUS classifications under CI-band that were decisive under point-estimate). This quantifies the false-closure rate in the historical smoke pipeline.
Tier hint: Tier 1 protocol audit (no GPU required, CPU/data analysis)
Why now: Retroactive audit requires only existing data. No new experiments, no cloud cost. If it reveals 2+ false closures, those anchors get re-promoted to AMBIGUOUS and eligible for stratified re-smoke.

### Anchor P-SMOKE-4: C1-FACT held-out stratum isolation
Anchor pointer: [FACT-RECALL-STRAT-D]
Substrate-product reading: The C1-FACT held-out fact-recall = 0 finding may have a composition explanation if smoke queries for that experiment were drawn from training-adjacent examples. A stratified re-smoke using only held-out facts as the query stratum would distinguish memorization-masking (alpha_smoke high due to in-dist queries) from genuine generalization failure (alpha_strat also 0).
Tier hint: Tier 3 (rescues a hard-fail row if composition explains it)
Why now: The 240-fact rescue is drafted and held. The composition audit is cheaper than a full rescue run and could avoid dispatching the rescue if the capability is already viable on a representative distribution.

---

## Context pointers

- Research note (primary findings): d:/AI/hd-instrument/notes/research_drill_smoke_vs_full_methodology_2x_2026-06-09.md
- PP-181 exp_dev brief: d:/AI/hd-instrument/notes/exp_dev_POST_COMPACTION_BRIEF_2026-06-09.md
- C1-FACT rescue draft: referenced in exp_dev_POST_COMPACTION_BRIEF_2026-06-09.md (240-fact rescue, held pending Research design)
- Stratified sampling theory: Cochran (1977) Sampling Techniques Ch.5-6 (cited in research note)
- Wilson CI and power analysis: research note section "Confidence interval bounds for binary capability tests"
- Pre-dispatch audit checklist: d:/AI/hd-instrument/memory/feedback_pre_dispatch_speed_harden_progress_discipline.md

---

## Contract

exp_dev designs anchors per envelope-fail-bands independently.
No inline experiment design is specified in this file.
Dispatch via queue_add.sh (CPU queue for P-SMOKE-1 and P-SMOKE-3; may use local runner; check queue depth first).
Post-ship REMOTE VERIFY per role contract.
Self-test per formula-selftests before declaring any anchor complete.

## Autonomy declaration

exp_dev has full autonomy to:
- Re-rank the anchors above based on current queue depth and runner state
- Combine P-SMOKE-1 and P-SMOKE-3 into a single dispatch if they share infrastructure
- Skip P-SMOKE-2 if sigma_seed has already been empirically characterized from PP-181 follow-ups
- Escalate P-SMOKE-4 to Research if the C1-FACT composition question requires deeper design work

exp_dev does NOT have autonomy to:
- Modify cap_map rows based on this handoff alone (requires full verdict cycle)
- Re-open closed anchors without running the stratified re-smoke first
