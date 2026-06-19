# Pre-registration: program_exec_audit_v1

**Date:** 2026-06-01
**Anchor:** program_exec_audit_v1
**Script:** experiments/exp_program_exec_audit_v1.py
**Queue:** remote_cpu_queue
**N:** 4096, no _n suffix (production N=4096 per rule 3)

## Hypothesis

The substrate can serve as an auditable program-execution memory with three
auditable properties: (A) execution trace retrieval at high load, (B) targeted
deletion of a specific execution's record without affecting others, and
(C) compound-attribute querying by (instruction, result) pair.

## Pre-registered thresholds

- **HARD-PASS:** Cell A accuracy > 0.85 AND Cell B deletion cos < 0.15 AND Cell C precision > 0.80
- **HARD-FAIL:** Cell A accuracy < 0.60 OR Cell B deletion cos > 0.30 OR Cell C precision < 0.50
- **MIDDLE-BAND:** everything else

## Smoke result (2026-06-01)

Smoke HARD_PASS: A_acc=0.918, B_del_cos=0.124, C_prec=1.000. Wall ~158s at 2 seeds.

## Cap-map rows

- Verifiable erase (cell B deletion isolation)
- Auditable compound-attribute query (cell C)
- Execution trace retrieval at 50% load (cell A)
