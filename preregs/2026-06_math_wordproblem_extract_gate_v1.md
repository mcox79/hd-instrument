# Pre-registration: math_wordproblem_extract_gate_cpu_v1
**Date:** 2026-06-11  **Anchor:** math_wordproblem_extract_gate_cpu_v1  **Queue:** local_cpu_queue  **N:** 4096
## Scientific question
Can substrate-style shallow extraction (numbers + operation-keyword associative recall) recover computable structure from
level-1 MATH word-problems? Gates the multi-day dep-parser/NL-extraction build.
## Pre-registered bands
HARD-PASS accuracy >= 0.40 on attempted AND coverage >= 0.30 (dep-parser justified). MIDDLE >= 0.25. HARD-FAIL < 0.25.
## Calibration rationale
Result accuracy 0.023 at coverage 0.801: extraction finds numbers+op for 80% but the "numbers+one-op" structure is WRONG for
most word-problems -- they need semantic multi-step REASONING, not shallow extraction. Refutes the shallow-extraction keystone;
a dep-parser would parse but not solve. Front-end is the LLM-reasoning regime; substrate is the symbolic back-end.
## N-suffix section
N=4096; hendrycks prealgebra+algebra level-1; number+op extraction + substrate op-recall. Verify-before-invest gate.
