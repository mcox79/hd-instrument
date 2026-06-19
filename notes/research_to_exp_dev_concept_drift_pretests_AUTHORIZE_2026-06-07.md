# Research -> Exp-Dev: concept drift detection 3 pre-tests AUTHORIZED

**From:** Research  **Date:** 2026-06-07  **Re:** Concept drift detection 2x drill output.

Per blanket authorization. v1.1 candidate capability per drill (8/10 creativity).

## Authorize 3 pre-tests from drill handoff

Per `exp_dev_handoff_research_concept_drift_detection_2026-06-07.md`.

### Pre-test 1: Misra-Gries window comparison on synthetic drift
~30 min - 1 hr CPU. Plant 30% topic shift in synthetic stream; measure detection
recall + false-positive rate.

HARD-PASS: detection recall >= 90%; false-positive rate <= 10%.

### Pre-test 2: Per-entity alert generation
~1 hr CPU. 100 stored facts with planted entity drift; generate per-entity alerts.

HARD-PASS: all planted drifts surface as actionable alerts; no spurious alerts.

### Pre-test 3: Drift narrative LLM
~1 hr CPU. Small LLM (Llama-1B) summarizes top-K shifts in natural language; verify
narrative quality on synthetic drift data.

HARD-PASS: narrative correctly describes drift in natural language (qualitative
assessment).

## v1.1 ship pathway

If PT1+2 HP: ship Misra-Gries-based drift alerting in v1.1 substrate stack (cheap
addition; integrates with sleep defrag's existing counters).

PT3 (drift narrative) is v1.5 enhancement; not required for v1.1.

## Customer pitch addition (v1.1)

"Substrate continuously monitors your KB for topic shifts. You get alerts BEFORE
knowledge staleness causes problems. Frontier LLMs cannot detect their own knowledge
staleness; vector DBs have no native time-series counters. Substrate's structural
drift detection from Misra-Gries time windows is a categorical capability."

## Cross-references

- Concept drift 2x: notes/research_drill_concept_drift_detection_2x_2026-06-07.md
- Drill handoff: notes/exp_dev_handoff_research_concept_drift_detection_2026-06-07.md

---

**Exp-Dev:** authorize all 3 pre-tests. PT1+2 are quick wins; PT3 is qualitative
v1.5 enhancement.
