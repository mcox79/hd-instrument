# Pre-registration: codegen_light_substrate_cpu_v1
**Date:** 2026-06-11  **Anchor:** codegen_light_substrate_cpu_v1  **Queue:** local_cpu_queue  **N:** 4096
## Scientific question
Does substrate code-gen (docstring-keyword pattern SELECTION + grammar instantiation, Architecture 1, no repair) reach
pass@1 >= 0.40 on the substrate-natural HumanEval subset?
## Pre-registered bands
HARD-PASS pass@1 >= 0.40. MIDDLE >= 0.20. HARD-FAIL < 0.20. UNKNOWN if dataset load fails.
## Calibration rationale
Result 0.15: pattern-selection solves clean single-pattern cases (sum/max/filter) but Architecture-1-alone can't compose/
multi-step. Confirms Research's analysis -- execution-repair loop (CODEGEN-REPAIR-1, +4-8pp) is the needed differentiator.
## N-suffix section
N=4096; 40 substrate-natural HumanEval problems; 25-pattern Tier-2 library + substrate docstring->pattern selection; subprocess exec.
