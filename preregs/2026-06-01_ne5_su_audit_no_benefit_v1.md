# Prereg: ne5_su_audit_no_benefit_v1

**Date**: 2026-06-01
**Anchor**: ne5_su_audit_no_benefit_v1
**Queue**: remote_cpu_queue
**Script**: experiments/exp_ne5_su_audit_no_benefit_v1.py
**Source**: notes/research_round5_7_drills_synthesis_2026-06-01.md (NE-5, S-U A2)

## Hypothesis

Sagawa-Ueda Axis 2 (audit no-benefit theorem): read-only audit operations
(no W mutation) provide zero retrieval benefit. This is an algebraic invariant:
W unchanged -> m* unchanged. S-U: mutual information gain requires physical write.

## Design

- N = 512, M in {32, 64, 128}
- Audit: iterate over patterns, compute overlap scores (read-only, no W mutation)
- Verify W identical before/after audit; verify m* identical
- 5 seeds

## Pre-registered thresholds (LOAD-BEARING)

**HARD-PASS**: |m*_post - m*_pre| / m*_pre < 0.01 (< 1% change) in ALL seeds/M.
This is an algebraic invariant test, not statistical.

**HARD-FAIL**: rel change > 0.05 in ANY seed (audit is mutating W = implementation bug).

**MIDDLE-BAND**: 1-5% change (numerical noise warning).

## Smoke result

Smoke: HARD_PASS. rel_change = 0.000000 for all seeds/M. W unchanged.
Full run expected to confirm.

## Timeout estimate

smoke_wall_s = 0.1s; trivial. timeout_s = 300 (PROT-019 floor).

## N-suffix

No _nN suffix. Production N = 512; stated per PROT-018 rule 3.
