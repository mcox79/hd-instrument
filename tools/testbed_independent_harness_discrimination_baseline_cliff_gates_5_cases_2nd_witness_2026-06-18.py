"""TESTBED branch-item-4 + REACTIVE on 3rd-gate: discrimination_gate + baseline_cliff_gate
INDEPENDENT-HARNESS 5-CASE FUNCTIONAL REPLICATE 2nd-witness verify.

Per Director get-everyone-moving routing + Skunkworks's 2 commits today:
- B-epsilon (2nd self-cert gate; 0aa86078): discrimination_gate (encodes audit-79 degenerate-
  regime-not-refutation as deterministic producer-attest + consumer-enforce)
- Working-baseline-cliff (3rd self-cert gate; 1790b16d; nested-fixed): baseline_cliff_gate
  (a lift over a FLOORED baseline is NOT a lever; B-delta v1 catch)

Both ADDITIVE + NON-RETROACTIVE: cells WITHOUT the self-check field pass through UNCHANGED.

The functional-replicate higher bar (vs prior atomizer-source-grep witness): construct test
metrics dicts that match the 5 cases each gate must handle + invoke the gate functions
directly + assert the output verdict matches the spec.

discrimination_gate 6-case spec (extended for nested-fixed):
 D1: flat {discriminates: False} + verdict=PASS                 -> NON_TEST
 D2: flat {discriminates: False} + verdict=HARD_FAIL            -> NON_TEST
 D3: flat {discriminates: True} + verdict=PASS                  -> PASS (no false override)
 D4: NO field present -> verdict UNCHANGED (legacy-safe)
 D5: field present but non-dict (e.g. None / string) -> verdict UNCHANGED (defensive)
 D6: NESTED {taskA: {discriminates: False}, taskB: {discriminates: True}} -> NON_TEST (any False)

baseline_cliff_gate 6-case spec:
 B1: flat {is_working_baseline_cliff: False} + verdict=PASS     -> NON_TEST
 B2: flat {is_working_baseline_cliff: False} + verdict=HARD_FAIL-> NON_TEST
 B3: flat {is_working_baseline_cliff: True} + verdict=PASS      -> PASS (no false override)
 B4: NO field present -> verdict UNCHANGED (legacy-safe)
 B5: field present but non-dict -> verdict UNCHANGED (defensive)
 B6: NESTED {taskA: {is_working_baseline_cliff: False}, taskB: {is_working_baseline_cliff: True}}
     + verdict=PASS                                              -> NON_TEST (any False)

12 total cases. Verify-only (no Store mutation).
"""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path('.').resolve()))

from tools.atomize_experiment_records import discrimination_gate, baseline_cliff_gate


DISCRIMINATION_CASES = [
    ('D1_flat_False_PASS_NONTEST',
     {'discrimination_self_check': {'discriminates': False}}, 'PASS', 'NON_TEST'),
    ('D2_flat_False_HARDFAIL_NONTEST',
     {'discrimination_self_check': {'discriminates': False}}, 'HARD_FAIL', 'NON_TEST'),
    ('D3_flat_True_PASS_NO_OVERRIDE',
     {'discrimination_self_check': {'discriminates': True}}, 'PASS', 'PASS'),
    ('D4_no_field_legacy_UNCHANGED',
     {}, 'PASS', 'PASS'),
    ('D5_field_non_dict_UNCHANGED',
     {'discrimination_self_check': None}, 'PASS', 'PASS'),
    ('D6_nested_any_False_NONTEST',
     {'discrimination_self_check': {'taskA': {'discriminates': False},
                                    'taskB': {'discriminates': True}}}, 'PASS', 'NON_TEST'),
]

BASELINE_CLIFF_CASES = [
    ('B1_flat_False_PASS_NONTEST',
     {'baseline_cliff_self_check': {'is_working_baseline_cliff': False}}, 'PASS', 'NON_TEST'),
    ('B2_flat_False_HARDFAIL_NONTEST',
     {'baseline_cliff_self_check': {'is_working_baseline_cliff': False}}, 'HARD_FAIL', 'NON_TEST'),
    ('B3_flat_True_PASS_NO_OVERRIDE',
     {'baseline_cliff_self_check': {'is_working_baseline_cliff': True}}, 'PASS', 'PASS'),
    ('B4_no_field_legacy_UNCHANGED',
     {}, 'PASS', 'PASS'),
    ('B5_field_non_dict_UNCHANGED',
     {'baseline_cliff_self_check': None}, 'PASS', 'PASS'),
    ('B6_nested_any_False_NONTEST',
     {'baseline_cliff_self_check': {'taskA': {'is_working_baseline_cliff': False},
                                    'taskB': {'is_working_baseline_cliff': True}}}, 'PASS', 'NON_TEST'),
]


def run_cases(name: str, gate_fn, cases: list) -> tuple[int, int]:
    print('=' * 78)
    print(f'{name} 6-CASE INDEPENDENT-HARNESS')
    print('=' * 78)
    passes = 0
    for case_id, metrics, verdict_in, expected_out in cases:
        actual = gate_fn(metrics, verdict_in)
        ok = actual == expected_out
        mark = 'PASS' if ok else 'FAIL'
        print(f'  [{mark}] {case_id:<40}  in={verdict_in:<10}  expected={expected_out:<10}  actual={actual}')
        if ok:
            passes += 1
    print(f'  {name}: {passes}/{len(cases)} cases PASS')
    return passes, len(cases)


def main() -> int:
    print('TESTBED branch-item-4 + 3rd-gate-reactive INDEPENDENT-HARNESS 5-CASE (extended to 6) FUNCTIONAL REPLICATE')
    print()
    p1, n1 = run_cases('discrimination_gate (B-epsilon; 0aa86078)', discrimination_gate, DISCRIMINATION_CASES)
    print()
    p2, n2 = run_cases('baseline_cliff_gate (3rd gate; 1790b16d nested-fixed)', baseline_cliff_gate, BASELINE_CLIFF_CASES)
    total_pass = p1 + p2
    total_n = n1 + n2
    print()
    print('=' * 78)
    if total_pass == total_n:
        print(f'OVERALL: HARD_PASS  ({total_pass}/{total_n} cases across 2 gates)')
        print('  - discrimination_gate B-epsilon: ADDITIVE + NON-RETROACTIVE verified across 6 cases')
        print('  - baseline_cliff_gate 3rd-gate:  ADDITIVE + NON-RETROACTIVE verified across 6 cases')
        print('  - NESTED-fixed schema handled correctly in both gates')
        print('  - Legacy-safe (no-field) and defensive (non-dict) cases verified')
        return 0
    print(f'OVERALL: HARD_FAIL  ({total_pass}/{total_n} cases)')
    return 1


if __name__ == '__main__':
    sys.exit(main())
