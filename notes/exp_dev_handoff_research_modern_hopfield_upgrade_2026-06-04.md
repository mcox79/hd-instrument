# exp_dev hand-off -- research: modern Hopfield upgrade path

Filed-by: research sub-agent (claude-sonnet-4-6)
Filed: 2026-06-04
Trigger: d:/AI/hd-instrument/notes/research_drill_modern_hopfield_upgrade_path_3x_2026-06-04.md

## Pause state block
Experiments are currently paused per data/orchestrator_paused.flag.
exp_dev MUST check the pause flag before queue_add.sh calls.
These candidates are queued for when experiments resume.

Per [[feedback-no-experiment-design-in-prompts]]:
This file provides TASK + WHY + CONTRACT + AUTONOMY to exp_dev.
It does NOT specify anchor names, sweep grids, threshold formulas, or pre-committed cap_map decisions.
exp_dev designs the experiment; research provides the framing.

---

## Anchor candidates (rank-ordered)

### Candidate 1 (HIGHEST PRIORITY): BCM-SNR / polynomial-p floor dependency analysis
Anchor pointer: Pre-condition check before implementing polynomial-p upgrade.
Substrate-product reading: If the BCM-SNR learning floor is ALSO p-dependent (scaling as
N^((p-1)/2)), then upgrading retrieval to p=4 reduces BOTH the capacity floor AND the
learning floor in tandem, cutting N_threshold from ~3000 to ~300-600. If the BCM floor
is p-independent, the polynomial upgrade gives capacity headroom but NOT N_threshold reduction.
This is the BINDING open question from the 3x drill.
Tier hint: RESEARCH / short algebraic drill (not a GPU experiment).
Why-now: The 10-20 hour implementation effort for polynomial-p upgrade is NOT justified until
this analysis confirms the BCM floor is p-dependent. This is the prerequisite.
Action: Dispatch 2x research drill on "BCM learning rule convergence SNR as function of
interaction order / energy degree". Generic query: "BCM Bienenstock-Cooper-Munro rule
convergence rate SNR higher-order interactions associative memory".

### Candidate 2: Smoke test polynomial-p retrieval primitive (N=512, p=4 vs p=2)
Anchor pointer: Cheap decisive test from research note.
Substrate-product reading: Validates that the 3-line code change (elementwise power on overlaps)
correctly implements polynomial-p Hopfield retrieval and achieves the predicted capacity jump.
The test is self-contained and does not require BCM analysis.
Tier hint: CPU smoke, < 5 minutes. Can run on laptop.
Why-now: Independent of BCM analysis. Validates the retrieval primitive in isolation.
Pre-registered HP/MID/HF:
  Cell A (N=512, p=4, M=50, 30% noise): HARD-PASS >= 90% retrieval; HARD-FAIL < 50%
  Cell B (N=512, p=2, M=50, 30% noise): HARD-PASS < 50% retrieval (classical should fail here)
  Cell C (N_threshold sweep): HARD-PASS N_threshold(p=4) < 500; HARD-FAIL > 1000

### Candidate 3 (DEFERRED): Full polynomial-p upgrade implementation
Anchor pointer: 10-20 hour engineering implementation from Sub-question 6.
Substrate-product reading: Replaces sign(W x) with sign(Xi^T * (Xi sigma)^(p-1)) throughout
the substrate retrieval code; updates capacity instrumentation; adds PROT-022 self-tests.
Tier hint: Engineering sprint (not GPU experiment; local CPU validation).
Why-now: HOLD pending Candidate 1 (BCM-SNR analysis) and Candidate 2 (smoke test pass).
Do not pursue until both predecessors resolve favorably.

---

## Context pointers

Research note: d:/AI/hd-instrument/notes/research_drill_modern_hopfield_upgrade_path_3x_2026-06-04.md
Cap map: d:/AI/hd-instrument/notes/substrate_capability_map.md
Prior BCM drill: check notes/ for research_*bcm* or research_*snr* files
Active protocols: d:/AI/hd-instrument/notes/active_protocols.md

---

## Contract section

exp_dev's contract for Candidate 2 (smoke test):
  - Read the research note FIRST (context pointer above)
  - Read active_protocols.md
  - Check pause flag before any queue_add.sh call
  - Implement the polynomial-p retrieval primitive as described in Sub-question 6 of the research note
  - Run smoke: N=512, p=4, M=50 patterns, 30% noise corruption; compare to N=512, p=2
  - Pre-register HP/MID/HF per Candidate 2 above BEFORE running
  - Report verdict as HARD-PASS / MIDDLE / HARD-FAIL against pre-registered thresholds
  - Do NOT run BCM coupling (that is Candidate 1, a research drill not an experiment)
  - ASCII only in verdict_msg

## Autonomy declaration

exp_dev has full autonomy on:
  - Exact implementation of polynomial-p retrieval primitive
  - Choice of N sweep values for Candidate 2 Cell C
  - PROT-022 formula self-test design
  - Queue assignment (CPU vs GPU; suggest CPU for this smoke)

exp_dev does NOT have autonomy on:
  - Pursuing Candidate 3 without Candidate 1 analysis first
  - Cap_map writes (orchestrator only)
  - Changing the pre-registered HP/MID/HF thresholds post-implementation
