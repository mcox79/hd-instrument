# exp_dev hand-off -- research: precision-weighted / multi-level predictive-error gating for comprehension

## Filed-by
research sub-agent, 2026-08-01

## Trigger
Research note: d:/AI/hd-instrument/notes/research_missing_comprehension_mechanisms_litscan_2026-08-01.md

Lit-scan finding: of the brain mechanisms central to language comprehension that the current system (predictive encoder + BG-style WM gate + situation-model loop + error-driven learning) lacks, the top-ranked and cheapest-to-test is precision-weighting (Friston/Feldman precision; inverse-variance gain on prediction error) -- a scalar reliability-gain on the existing error-driven update, not a new organ. Second-ranked is multi-level prediction (token + event/discourse grain simultaneously, Kuperberg & Jaeger 2016), which is architecturally heavier (a predict-then-error step at the situation-model's grain) but literature-mandated for anything beyond next-word comprehension.

## Pause state block
Per [[feedback-obey-user-pause-explicitly]]: check data/orchestrator_paused.flag before dispatching. Do NOT queue without orchestrator go-signal.

## Per [[feedback-no-experiment-design-in-prompts]]
This file hands off WHAT and WHY. exp_dev designs the anchor names, sweep grids, threshold formulas, queue choice, and pre-reg bands autonomously. Do not encode those here.

---

## Anchor candidates (rank-ordered)

### 1. Precision-gated learning-rate multiplier on existing error-driven update (HIGHEST PRIORITY)
- Anchor pointer: scale weight-update magnitude by a running inverse-variance estimate of recent prediction error, computed per representational channel/level, applied on top of the existing error-driven learning step -- no new organ.
- Substrate-product reading: if this improves disambiguation-point accuracy (temporary syntactic ambiguity / garden-path-style continuations) without regressing plain-sentence accuracy, it confirms reliability-weighted learning is load-bearing and cheap to keep; if it collapses to a mislabeled learning-rate-schedule effect, that's diagnostic that the current corpus/vocab scale is underpowered to show the effect, not that the mechanism is unneeded.
- Tier hint: Tier 1 (two-line addition to existing update path; fast CPU smoke)
- Why now: cheapest decisive test on the ranked list; directly tests HARD-PASS/HARD-FAIL thresholds pre-registered in the research note (>=15% relative error reduction at disambiguation point, <=2% regression on plain sentences).

### 2. Predict-then-error step at situation-model grain (multi-level prediction)
- Anchor pointer: extend the situation-model loop from passive slot-holding to actively generating an expectation (event/discourse-level prediction) that produces its own prediction-error signal feeding back into learning, analogous to the token-level predictive encoder but one level up.
- Substrate-product reading: this is the literature-mandated fix for "comprehension = growing competency library" needing more than next-token prediction; a positive result would mean the situation-model loop can itself drive learning, not just hold state written by the token-level encoder.
- Tier hint: Tier 2 (new architectural step, higher cost than anchor 1; run after anchor 1 lands so the gain-control mechanism it may reuse is already built)
- Why now: second-ranked by comprehension-impact in the research note; explicitly flagged as architecturally heavier, so sequence behind anchor 1.

### 3. Unified fast/slow gain-control (fold neuromodulation ACh/NE distinction into anchor 1)
- Anchor pointer: two-timescale extension of anchor 1's precision gain -- fast component (ACh-like, local reliability) already covered by anchor 1; slow component (NE-like context-change / topic-shift detector) as an additional signal that triggers a broader reset rather than local reweighting.
- Substrate-product reading: discriminates whether local-ambiguity handling and global-context-shift handling need separate signals or collapse into one mechanism; directly informs which episodes get tagged for future replay/consolidation work.
- Tier hint: Tier 2 (follow-up after anchor 1's fast-timescale result is in; do not build both timescales simultaneously)
- Why now: research note explicitly recommends NOT building neuromodulation (B) as a separate organ from precision-weighting (A) -- risk of duplicate architecture under different names. Anchor 3 exists to test the fast/slow split cheaply once anchor 1 is landed, not to be built standalone.

---

## Context pointers

- Research note: d:/AI/hd-instrument/notes/research_missing_comprehension_mechanisms_litscan_2026-08-01.md
- Related prior research (broader mechanism inventory, different axis -- feasibility not comprehension-impact): d:/AI/hd-instrument/notes/research_brain_mechanisms_NOT_yet_tested_2x_drill_2026-06-24.md
- Related prior research: d:/AI/hd-instrument/notes/research_missing_structure_learned_comprehension_5x_drill_2026-07-18.md (NOT re-read in full this cycle -- diff against this hand-off before shipping anchor 1 or 2 to avoid duplicate framing)
- Related prior surprise-gating empirical result (different subsystem, same family of mechanism -- surprise-weighted write gating): d:/AI/hd-instrument/notes/exp_dev_handoff_research_b3b_surprise_gating_2026-06-04.md
- Status log: d:/AI/hd-instrument/data/orchestrator_status_log.jsonl

---

## Contract

exp_dev takes this file as a task hand-off and ships anchor(s) per its normal cycle protocol:
- Read research note for WHY and which mechanisms to discriminate
- Pre-register HARD-PASS / HARD-FAIL / MIDDLE-BAND per [[feedback-envelope-expansion-fail-bands]] (research note already proposes concrete HARD-PASS/HARD-FAIL thresholds for anchor 1 as a starting point -- exp_dev may refine)
- Smoke gate before ship; self-test per formula-selftests
- Ship via queue_add.sh; orchestrator owns post-ship REMOTE VERIFY

## Autonomy declaration

exp_dev owns: exact anchor naming, sweep grids, pre-reg band formulas, queue choice (local/remote/GPU), corpus/vocab scale for the ambiguity discriminator, and sequencing decisions beyond the rank-order given above. This hand-off provides WHAT and WHY only, per [[feedback-no-experiment-design-in-prompts]].
