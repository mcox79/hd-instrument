"""TESTBED branch-item-2: Bucket A 4 PROOF_RECORD INDEPENDENT-HARNESS 2nd-witness verify.

Per Director routing (USER get-everyone-moving 2026-06-18): "replicate each in independent
harness" -- higher bar than the per-atom-landing Store-state delta verify I already did.

Independent harness = re-verify each PROOF_RECORD atom against an INDEPENDENT specification
(not just re-reading the atom). Composes Skunkworks SEMANTICS-MATCH rubric (real-not-complex
+ exact + non-vacuous + canonical-lemma + honest-scope) with the structural cert-conditions
that make a PROOF_RECORD load-bearing in this substrate.

12-point INDEPENDENT-HARNESS check per proof:
 1. Atom exists with kind=PROOF_RECORD                     (structural)
 2. algebra is None                                         (0-algebra guard for proof records)
 3. confidence_tier == T0_PROVEN_FORMAL                     (cert-tier)
 4. corpus == MATH                                          (domain-correct)
 5. Lean file exists at expected path                       (referent exists)
 6. Lean file contains the named theorem identifier         (referent matches)
 7. Lean file is sorry-free (no `sorry` keyword)            (no admit)
 8. semantics_match_vet metadata present + vet_by populated (auditor-vetted)
 9. proof_obligation field non-empty                        (proof-obligation declared)
10. no_algebra_structural_guard flag True                   (structural-guard recorded)
11. eleventh_rule_clean flag True                           (USER-LOCKED 11th)
12. references_methodology_rule field present + non-empty   (lineage to M_LEAN methodology)

All 12 must PASS for a PROOF_RECORD to be 2nd-witness HARD_PASS in independent harness.
Outputs structured matrix. No mutations (verify-only).
"""
from __future__ import annotations
import sys
import re
from pathlib import Path

sys.path.insert(0, str(Path('.').resolve()))

from backend.substrate_index.partition import PartitionedStore


# Map proof slug -> (expected Lean file path, expected theorem identifier)
PROOF_SPECS = {
    'PROOF_pythagoras_ip_real_inner_product': (
        Path('lean_oracle/pythagoras_ip_v1/PythagorasIpV1/Pythagoras.lean'),
        'pythagoras_ip',
    ),
    'PROOF_cauchy_schwarz_real_inner_product': (
        Path('lean_oracle/pythagoras_ip_v1/PythagorasIpV1/CauchySchwarz.lean'),
        'cauchy_schwarz_ip',
    ),
    'PROOF_triangle_inequality_real_inner_product': (
        Path('lean_oracle/pythagoras_ip_v1/PythagorasIpV1/Triangle.lean'),
        'triangle_ip',
    ),
    'PROOF_parallelogram_law_real_inner_product': (
        Path('lean_oracle/pythagoras_ip_v1/PythagorasIpV1/Parallelogram.lean'),
        'parallelogram_law_ip',
    ),
    'PROOF_orthonormal_linearly_independent_real_inner_product': (
        Path('lean_oracle/pythagoras_ip_v1/PythagorasIpV1/OrthonormalIndependent.lean'),
        'orthonormal_linear_independent',
    ),
}


def check_one_proof(atom, lean_path: Path, theorem_id: str) -> dict:
    checks = {}

    # 1. kind == PROOF_RECORD
    kind_str = atom.kind.value if hasattr(atom.kind, 'value') else atom.kind
    checks['1_kind_PROOF_RECORD'] = (kind_str == 'proof_record')

    # 2. algebra is None
    checks['2_algebra_None'] = (atom.algebra is None)

    # 3. confidence_tier == T0_PROVEN_FORMAL
    md = atom.metadata or {}
    checks['3_confidence_tier_T0_PROVEN_FORMAL'] = (md.get('confidence_tier') == 'T0_PROVEN_FORMAL')

    # 4. corpus == MATH
    corpus_str = atom.corpus.value if hasattr(atom.corpus, 'value') else atom.corpus
    checks['4_corpus_MATH'] = (str(corpus_str).lower() == 'math')

    # 5. Lean file exists
    checks['5_lean_file_exists'] = lean_path.exists()

    # 6. Lean file contains the named theorem identifier
    lean_text = ''
    if lean_path.exists():
        try:
            lean_text = lean_path.read_text(encoding='utf-8', errors='replace')
        except Exception:
            lean_text = ''
    checks['6_theorem_identifier_present'] = bool(
        re.search(r'\btheorem\s+' + re.escape(theorem_id) + r'\b', lean_text)
    )

    # 7. Lean file is sorry-free
    # check for `sorry` as a token (not as substring inside an identifier or comment)
    sorry_pattern = re.compile(r'(?:^|[^A-Za-z0-9_])sorry(?:[^A-Za-z0-9_]|$)')
    if lean_text:
        # naive: strip line comments to avoid false-positives in `-- sorry-free`
        scrub = re.sub(r'--.*$', '', lean_text, flags=re.MULTILINE)
        scrub = re.sub(r'/-.*?-/', '', scrub, flags=re.DOTALL)
        checks['7_sorry_free'] = (sorry_pattern.search(scrub) is None)
    else:
        checks['7_sorry_free'] = False

    # 8. semantics_match_vet metadata present + vet_by populated
    smv = md.get('semantics_match_vet')
    vet_by = md.get('vet_by')
    checks['8_semantics_match_vet_and_vet_by'] = bool(smv) and bool(vet_by)

    # 9. proof_obligation non-empty
    checks['9_proof_obligation_non_empty'] = bool(md.get('proof_obligation'))

    # 10. no_algebra_structural_guard True
    checks['10_no_algebra_structural_guard_True'] = (md.get('no_algebra_structural_guard') is True)

    # 11. eleventh_rule_clean True
    checks['11_eleventh_rule_clean_True'] = (md.get('eleventh_rule_clean') is True)

    # 12. references_methodology_rule non-empty
    checks['12_references_methodology_rule_non_empty'] = bool(md.get('references_methodology_rule'))

    return checks


def main() -> int:
    store_dir = Path('data/substrate_index')
    ps = PartitionedStore(store_dir)
    by_id = {a.id: a for a in ps.all_atoms()}

    print('=' * 78)
    print('BUCKET A 4 PROOF_RECORD INDEPENDENT-HARNESS 2nd-WITNESS')
    print('=' * 78)

    all_hard_pass = True
    summary_rows = []

    for atom_id, (lean_path, theorem_id) in PROOF_SPECS.items():
        atom = by_id.get(atom_id)
        if atom is None:
            print(f'\n[{atom_id}]  ATOM NOT FOUND IN STORE  -> HARD_FAIL')
            all_hard_pass = False
            summary_rows.append((atom_id, 'NOT_FOUND', 0, 12))
            continue

        checks = check_one_proof(atom, lean_path, theorem_id)
        passes = sum(1 for v in checks.values() if v)
        total = len(checks)
        verdict = 'HARD_PASS' if passes == total else 'HARD_FAIL'
        all_hard_pass = all_hard_pass and (passes == total)
        summary_rows.append((atom_id, verdict, passes, total))

        print(f'\n[{atom_id}]')
        print(f'  Lean file: {lean_path}  (exists={lean_path.exists()})')
        print(f'  Theorem id expected: {theorem_id}')
        for k, v in checks.items():
            mark = 'PASS' if v else 'FAIL'
            print(f'    [{mark}] {k}')
        print(f'  -> {verdict}  ({passes}/{total} checks)')

    print()
    print('=' * 78)
    print('SUMMARY MATRIX')
    print('=' * 78)
    print(f'{"PROOF_RECORD":<54} {"VERDICT":<11} {"CHECKS"}')
    print('-' * 78)
    for atom_id, verdict, passes, total in summary_rows:
        print(f'{atom_id[:53]:<54} {verdict:<11} {passes}/{total}')
    print('=' * 78)
    if all_hard_pass:
        print('OVERALL: BUCKET A 4 PROOF_RECORD INDEPENDENT-HARNESS 2nd-WITNESS HARD_PASS')
        return 0
    print('OVERALL: BUCKET A 4 PROOF_RECORD INDEPENDENT-HARNESS 2nd-WITNESS HARD_FAIL')
    return 1


if __name__ == '__main__':
    sys.exit(main())
