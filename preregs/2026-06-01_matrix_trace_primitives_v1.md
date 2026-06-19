# Prereq: matrix_trace_primitives_v1

## Scientific question
5 matrix-trace primitives from algebraic surface drill:
COUNT, CONTAINS, EFFECTIVE_RANK, JACCARD, FROBENIUS/SYMDIFF.

## Pre-registered bands
HARD-PASS: all 5 pass in >= 4/5 seeds.
MIDDLE: >= 3 primitives pass in >= 3/5 seeds.
HARD-FAIL: <= 2 pass in >= 3/5 seeds.

## N-suffix
No _nN suffix; production N=2048; rationale: algebraic identity verification.

## Timeout estimate
smoke_wall_s=3.8. ceil(1.5 * 3.8 * (7/3) * (5/2)) = ceil(111) -> timeout_s=300.

## Date
2026-06-01
