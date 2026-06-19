# Pre-registration: codegen_subgoal_substrate_cpu_v1
**Date:** 2026-06-11  **Anchor:** codegen_subgoal_substrate_cpu_v1  **Queue:** local_cpu_queue  **N:** 4096
## Scientific question
Does compositional code-gen (filter->map->reduce subgoal chains, leveraging substrate compose strength) lift past the 0.175
single-pattern ceiling on substrate-natural HumanEval?
## Pre-registered bands
HARD-PASS pass@1 >= 0.40. MIDDLE >= 0.20 (lifts past single-pattern). HARD-FAIL < 0.20.
## Calibration rationale
Result 0.025: fixed filter->map->reduce structure + keyword decomposition is too rigid/noisy -- mis-decomposes most problems.
Composition back-end isn't the gap; docstring->semantic-decomposition (NL understanding) is. Same bottleneck as MATH word-problems.
## N-suffix section
N=4096; 40 substrate-natural HumanEval; filter/map/reduce subgoal vocabulary; subprocess execution.
