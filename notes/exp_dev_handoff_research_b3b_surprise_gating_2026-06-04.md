# exp_dev hand-off -- research: B3b surprise-gating regularization mechanism (2x drill)

## Filed-by
research sub-agent, 2026-06-04

## Trigger
Research note: d:/AI/hd-instrument/notes/research_drill_b3b_surprise_gating_regularization_mechanism_2x_2026-06-04.md

Empirical finding: B3b cell (exponentially-smoothed surprise-gating) achieves 116% perf-retention at 2.2x write reduction vs B3a write-all baseline at N=2048. The algebraic drill shows this is not noise -- it is expected near-capacity behaviour with three reinforcing mechanisms. The cheapest discriminating test is an alpha-sweep.

## Pause state block
Per [[feedback-obey-user-pause-explicitly]]: check data/orchestrator_paused.flag before dispatching. Do NOT queue without orchestrator go-signal.

## Per [[feedback-no-experiment-design-in-prompts]]
This file hands off WHAT and WHY. Exp_dev designs the anchor names, sweep grids, threshold formulas, queue choice, and pre-reg bands autonomously. Do not encode those here.

---

## Anchor candidates (rank-ordered)

### 1. Alpha-sweep: load-dependent advantage test (HIGHEST PRIORITY)
- Anchor pointer: B3b vs write-all, varying corpus load alpha = P/N at N=2048
- Substrate-product reading: if advantage collapses at low alpha, confirms anti-crosstalk as dominant mechanism and tells us gating is a near-capacity quality lever, not a universal speedup
- Tier hint: Tier 1 (discriminates dominant mechanism; fast CPU smoke)
- Why now: algebraic prediction is that alpha ~= 0.56 produces exactly 116%; testing at alpha = 0.03-0.80 will confirm or refute this with one sweep. This is the cheap decisive test called out in the research note.

### 2. EMA tau-sweep: smoothing time constant optimisation
- Anchor pointer: B3b at alpha ~= 0.56, varying tau in {5, 20, 50, 150, 500}
- Substrate-product reading: optimal tau value is a direct product parameter; too-short collapses to random gating; too-long under-writes
- Tier hint: Tier 2 (product parameter; CPU)
- Why now: B3b result is sensitive to tau; need to know if 116% is at a peak or a plateau before committing to EMA as the design

### 3. Random-gate control: dropout vs information-curation discrimination
- Anchor pointer: N=2048, alpha ~= 0.56, random 45% skip (matched write rate to B3b)
- Substrate-product reading: if random gating gives >= 110%, the mechanism is pure capacity management (dropout-class) and surprise is not load-bearing; if random gives ~100%, surprise is the key ingredient
- Tier hint: Tier 1 (mechanistic discrimination; fast CPU)
- Why now: hardest-to-distinguish HF3 condition; must run before claiming surprise-gating has product value vs random subsampling

### 4. Redundancy-scan: controlled corpus redundancy sweep
- Anchor pointer: N=2048, alpha ~= 0.56, corpus redundancy r in {1, 2, 4, 8}
- Substrate-product reading: discriminates mechanism 1 (info curation; gain proportional to r) from mechanism 2 (anti-crosstalk; gain driven by alpha not r)
- Tier hint: Tier 2 (follow-up after alpha-sweep confirms dominant mechanism)
- Why now: if alpha-sweep confirms mechanism 2, this is the second test; if alpha-sweep is ambiguous, this runs in parallel

---

## Context pointers

- Research note: d:/AI/hd-instrument/notes/research_drill_b3b_surprise_gating_regularization_mechanism_2x_2026-06-04.md
- Related prior research: d:/AI/hd-instrument/notes/research_triple_point_deepdrill_2026-05-21.md (capacity cliff at K/N ~= 0.56)
- Related prior research: d:/AI/hd-instrument/notes/research_wright_fisher_substrate_2026-05-26.md (continual learning / forgetting frame)
- Status log: d:/AI/hd-instrument/data/orchestrator_status_log.jsonl

---

## Contract

exp_dev takes this file as a task hand-off and ships anchor(s) per its normal cycle protocol:
- Read research note for WHY and which cells to discriminate
- Pre-register HARD-PASS / HARD-FAIL / MIDDLE-BAND per [[feedback-envelope-expansion-fail-bands]]
- Smoke gate before full run
- ASCII-only in print()/verdict_msg per [[feedback-ascii-only-in-scripts]]
- Anchor names must not share prefix with completed entries per [[feedback-ship-name-collision]]
- Do NOT run blocking commands per [[feedback-no-blocking-runs]]

## Autonomy declaration

exp_dev chooses: anchor names, sweep parameter values, queue routing (CPU vs GPU), timeout formula, pre-reg threshold numbers, and order of dispatch. Orchestrator authorises; exp_dev designs.
