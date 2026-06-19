# Pre-registration: codegen_repair_substrate_cpu_v1
**Date:** 2026-06-11  **Anchor:** codegen_repair_substrate_cpu_v1  **Queue:** local_cpu_queue  **N:** 4096
## Scientific question
Is the CODEGEN-LIGHT 0.15 bottleneck SELECTION or the PATTERN LIBRARY? Measures pass@k-oracle (any pattern passes hidden test
= library ceiling) vs docstring-select pass@1. Determines whether to build a repair/selection loop or composition.
## Pre-registered bands
HARD-PASS oracle ceiling >= 0.40 (patterns rich; selection is the gap; build repair). MIDDLE 0.20-0.40. HARD-FAIL < 0.20 (patterns insufficient; need composition).
## Calibration rationale
Result oracle=0.175, docstring-select=0.150, gap=0.025: selection is near-optimal; the single-pattern library caps ~0.175.
Repair loop would add only ~0.025. The genuine path to 0.40 is composition/subgoal decomposition (Architecture 3), NOT repair.
## N-suffix section
N=4096; 40 substrate-natural HumanEval; 25-pattern library; subprocess execution. High-value diagnostic redirecting the build.
