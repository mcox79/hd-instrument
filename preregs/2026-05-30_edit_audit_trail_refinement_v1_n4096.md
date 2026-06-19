# C5 Edit Audit Trail Refinement v1 at N=4096

## Anchor
edit_audit_trail_refinement_v1_n4096

## Queue
remote_cpu_queue

## Script
experiments/exp_edit_audit_trail_refinement_v1_n4096.py

## Scientific question
Define + test audit trail schema for production compliance. Generate sample
audit reports across 6 compliance scenarios.

## Pre-registered bands
- HARD_PASS: all 6 scenarios produce complete audit trail AND integrity 100%
  (hash chain unbroken AND tamper detected) AND audit_size_per_op < 500 bytes.
- HARD_FAIL: any scenario produces incomplete or invalid trail.
- MIDDLE_BAND: otherwise (e.g. size > threshold but rest valid).

## Schema
Each entry: ts_ns, op (str), operands (dict), W_norm_before, W_norm_after,
delta_norm, link (sha256 of prev_hash + entry_body).

## Scenarios
- s1: single_edit
- s2: sequential_edits (3 in a row)
- s3: delete_with_certificate
- s4: interrupted_operation_recovery
- s5: concurrent_edits_serialization
- s6: failed_deletion_audit

## Config
- N = 4096 (PROT-018 _n4096)
- M = 2048
- Seeds: [7, 17, 23, 31, 41]

## Output
notes/audit_trail_schema_v1_2026-05-30.md - schema + sample reports per scenario.

## Self-test
- 6 scenarios produce complete trails at smoke
- Hash chain integrity verified
- Tampered entry breaks verification (integrity_under_failure)
- Verdict gates HP/HF/MB exercised
- Live CPU smoke at N=1024 M=128

## Timeout estimate
- smoke wall <1s; 5 seeds * 6 scenarios; each is small (few edits)
- scaling_exp = 1.0; estimate = ceil(1.5 * 1 * 1 * 5 * 6) = 45s; large margin
- timeout_s = 14400 (user spec).

## Importance
HIGH - production compliance foundation; killer feature KF-4 deliverable.
