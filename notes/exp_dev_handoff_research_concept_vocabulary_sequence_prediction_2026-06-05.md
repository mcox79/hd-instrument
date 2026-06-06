# exp_dev hand-off -- research: concept vocabulary vs sequence prediction regime (2x drill)

Filed-by: research sub-agent (2x drill, 2026-06-05)
Trigger: d:/AI/hd-instrument/notes/research_drill_concept_vocabulary_vs_sequence_prediction_regime_2x_2026-06-05.md
Pause state: CHECK data/orchestrator_paused.flag before dispatching

Per [[feedback-no-experiment-design-in-prompts]]: this file identifies WHAT to test and WHY, not HOW to implement it. exp_dev designs the anchors, sweep grids, and thresholds autonomously.

---

## Anchor candidates (rank-ordered)

### Rank 1 -- Write rule comparison: Hebbian vs predictive coding residual

Anchor pointer: cap_map row for sequence prediction / write rule capability
Substrate-product reading: predictive coding residual write (W += lr * outer(phi(c_{t+1}) - W*phi(c_t), phi(c_t))) should shift substrate from n-gram-statistics class to conditional-distribution class. Algebraic analysis predicts this breaks the V_c^4 training requirement of Hebbian outer-product writes. This is the highest-ROI write-rule change available.
Tier hint: CPU smoke then GPU depth (N=8192, V_c sweep, write rule comparison)
Why now: research analysis shows write rule is the PRIMARY architectural lever -- more impactful than V_c or K tuning alone. Blocking question for sequence prediction capability claim.

### Rank 2 -- V_c threshold sweep at N=8192

Anchor pointer: cap_map row for vocabulary/dimension regime boundary
Substrate-product reading: algebraic analysis predicts transition from n-gram to concept-structure regime at V_c ~ sqrt(N) = 91 for N=8192. Empirical sweep across V_c = {20, 64, 128, 256, 512} with BOTH Hebbian and predictive coding writes should confirm transition point and validate V_c^4 scaling law.
Tier hint: CPU (N=8192 is modest; sweep across V_c values is parallelizable)
Why now: validates the algebraic derivation and sets engineering spec for V_c in product deployment

### Rank 3 -- Extended context K comparison at small vs large V_c

Anchor pointer: cap_map row for context-binding capability (K scaling)
Substrate-product reading: analysis predicts K=5 HURTS at V_c<=64 and K=2 HELPS at V_c>=256. This is a hard prediction with clear PASS/FAIL bands. Cheap test: fix N=8192, vary V_c={20, 64, 256}, vary K={1, 2, 5, 10}, measure accuracy vs trigram-Markov.
Tier hint: CPU (parameter sweep, no deep learning required)
Why now: K=2 is proposed as the product sweet spot; this validates the recommendation before engineering investment

### Rank 4 -- Sparse coding activation fraction sweep

Anchor pointer: cap_map row for sparsity / activity fraction
Substrate-product reading: analysis predicts a <= 0.05 required at V_c=256, N=8192 to keep T_required manageable. Sweep a = {0.01, 0.05, 0.10, 0.25, 1.0} at V_c=256, Hebbian write, K=2. Expect accuracy peaks at a ~ 0.05 and degrades for a=1.0.
Tier hint: CPU
Why now: sparsity is a prerequisite for the V_c=256 regime to work; must confirm before committing to sparse architecture

---

## Context pointers

Research note: d:/AI/hd-instrument/notes/research_drill_concept_vocabulary_vs_sequence_prediction_regime_2x_2026-06-05.md
Field advisor state: d:/AI/hd-instrument/tools/orchestrator/research_field_advisor.py
Cap map: d:/AI/hd-instrument/data/cap_map.json (or .md equivalent in notes/)
Status log: d:/AI/hd-instrument/data/orchestrator_status_log.jsonl

Key algebraic results for pre-registration:
- Hebbian SNR: requires T > N * V_c^4 * 2 * log(V_c) for correct bigram retrieval
- Sparse correction factor: T_required reduces by a^4 with activity fraction a
- PC write convergence: lr < 1 / lambda_max(outer(phi,phi)) = 1 (random bipolar patterns)
- Regime boundary: V_c ~ sqrt(N) = 91 for N=8192

---

## Contract

exp_dev autonomously designs: anchor names, sweep grids, threshold formulas, queue assignment, wall time estimates, pre-reg bands.
exp_dev does NOT encode: the algebraic derivations above (those are research-layer, not experiment-layer).
exp_dev MUST pre-register HARD-PASS and HARD-FAIL bands per [[feedback-envelope-expansion-fail-bands]] BEFORE shipping.

## Autonomy declaration

exp_dev has full autonomy on implementation choices, sweep ranges, and queue routing within the research context above. The rank ordering above is advisory -- exp_dev may reorder based on queue state, cap_map gaps, and cost considerations.
