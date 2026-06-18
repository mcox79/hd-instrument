"""DRAFT guarded creation of the 4th PROOF_RECORD atom: Bucket A parallelogram law.

STATUS: DRAFT -- DO NOT RUN until Skunkworks SEMANTICS-MATCH VET PASS + claim_scope finalized.
Mirrors substrate_create_cauchy_schwarz_PROOF_RECORD_2026-06-18.py (proven template).

This is the genuinely INNER-PRODUCT-SPECIFIC proof of the batch: the parallelogram law FAILS in
general normed spaces and characterizes inner-product norms.

Schema model: AtomKind=PROOF_RECORD + metadata.confidence_tier='T0_PROVEN_FORMAL'.

verify-the-referent (Exp-Dev, pre-VET):
 - lake build PythagorasIpV1.Parallelogram -> exit 0 (1905 jobs; 14s incremental)
 - olean artifact: .lake/build/lib/lean/PythagorasIpV1/Parallelogram.olean (17768 bytes)
 - source: no sorry/admit/axiom/native_decide
 - #print axioms parallelogram_law_ip -> [propext, Classical.choice, Quot.sound] (standard trio; no sorryAx)
 - commit 7d64d1c6
"""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path('.').resolve()))

from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import Atom, AtomKind, Corpus, Tier

ATOM_ID = 'PROOF_parallelogram_law_real_inner_product'

# Condition 3: DRAFT scope (Skunkworks finalizes verbatim at VET).
CLAIM_SCOPE = (
    "Certifies the EXACT parallelogram law for REAL inner-product spaces, holding "
    "UNCONDITIONALLY for all u, v: ||u + v||^2 + ||u - v||^2 = 2*(||u||^2 + ||v||^2). "
    "This identity is genuinely INNER-PRODUCT-SPECIFIC: it FAILS in general normed spaces "
    "and characterizes norms induced by an inner product (unlike the triangle inequality, "
    "which holds in any normed space). Real, not complex."
)

DESCRIPTION = (
    "PROOF_RECORD (confidence_tier T0_PROVEN_FORMAL): parallelogram law in real inner product spaces. "
    "theorem parallelogram_law_ip {F} [NormedAddCommGroup F] [InnerProductSpace R F] (u v : F) "
    ": ||u + v||^2 + ||u - v||^2 = 2*(||u||^2 + ||v||^2) := by exact parallelogram_law_with_norm (R) u v. "
    + CLAIM_SCOPE
)


def module_liveness_ok() -> bool:
    import importlib
    return all(
        hasattr(importlib.import_module(m), s)
        for m, s in [
            ('backend.substrate_index.hmm_decoder', 'viterbi_decode'),
            ('hdlab.perceptron', 'StructuredPerceptron'),
            ('backend.substrate_index.sequence_labeler', 'NERTagger'),
            ('hdlab.bayesian_inference', 'EMMixture'),
            ('backend.substrate_index.intent_classifier', 'IntentClassifier'),
            ('backend.substrate_index.refuse_gated_retriever', 'RefuseGatedRetriever'),
        ]
    )


def axiom_term_count(ps: PartitionedStore) -> int:
    atoms = list(ps.all_atoms())
    return sum(
        1 for a in atoms
        if str(a.corpus.name) == 'MATH'
        and str(a.tier.name) in ('TIER_2_PRIMITIVE', 'TIER_3_ALGORITHM')
        and a.algebra and len(a.algebra) >= 3
        and 'oeis' not in str(a.id).lower()
        and not str(a.id).startswith('T3/wikidata_')
    )


def build_atom() -> Atom:
    metadata = {
        'confidence_tier': 'T0_PROVEN_FORMAL',
        'claim_scope': CLAIM_SCOPE,
        'proof_obligation': {
            'file': 'lean_oracle/pythagoras_ip_v1/PythagorasIpV1/Parallelogram.lean',
            'theorem': 'parallelogram_law_ip',
            'lean_toolchain': 'leanprover/lean4:v4.31.0',
            'mathlib': 'mathlib4 (lake cache; parallelogram_law_with_norm)',
            'olean_artifact': 'lean_oracle/pythagoras_ip_v1/.lake/build/lib/lean/PythagorasIpV1/Parallelogram.olean (17768 bytes)',
            'lean_commit': '7d64d1c6',
            'lake_build': 'exit 0; 1905 jobs; target theorem built; no sorry/admit/axiom',
            'print_axioms': '[propext, Classical.choice, Quot.sound] (standard mathlib trio; no sorryAx)',
        },
        'no_algebra_structural_guard': True,
        'axiom_term_promotion': 'SEPARATE explicit USER/PHASE-III authority; NEVER automatic on lake-PASS',
        'inner_product_specific': 'TRUE -- parallelogram law fails in general normed spaces; characterizes IP norms',
        'semantics_match_vet': 'PENDING',   # Skunkworks sets PASS at VET
        'vet_by': 'skunkworks',
        'vet_date': 'PENDING',
        'vet_checks': 'real-not-complex + exact-not-approximate + non-vacuous + canonical-lemma(parallelogram_law_with_norm) + olean-artifact-verified + no-sorry-axiom + print-axioms-standard-trio + ip-specific',
        'references_methodology_rule': 'RULE_M_LEAN_semantics_match_necessary_lake_pass_necessary_not_sufficient_T0_PROVEN_FORMAL',
        'eleventh_rule_clean': True,
        'phase': 'PHASE-2',
        'bucket': 'A_cert_stream_lean_batch_proof_3_of_3_IP_specific',
        'corrected_model': 'AtomKind=PROOF_RECORD + confidence_tier=T0_PROVEN_FORMAL (kind separate from trust-tier)',
        'source': 'bucket_a_exp_dev_authors_skunkworks_semantics_match_vet_testbed_2nd_witness',
    }
    return Atom(
        id=ATOM_ID,
        name='Proof record (T0_PROVEN_FORMAL): parallelogram law in real inner product spaces',
        description=DESCRIPTION,
        kind=AtomKind.PROOF_RECORD,
        tier=Tier.TIER_NA,
        corpus=Corpus.MATH,
        algebra=None,
        metadata=metadata,
    )


def main() -> int:
    ps = PartitionedStore(Path('data/substrate_index'))

    pre_n = sum(1 for _ in ps.all_atoms())
    pre_axiom = axiom_term_count(ps)
    pre_mod = module_liveness_ok()
    print(f'PRE: atoms={pre_n}  axiom_term={pre_axiom}  cap_pres(mod6/6)={pre_mod}')
    if not pre_mod or pre_axiom != 206:
        print('PRE-GATE FAIL (cap_pres or axiom_term != 206). Halting; no mutation.')
        return 1

    atom = build_atom()
    if atom.metadata.get('semantics_match_vet') != 'PASS':
        print('REFUSE: semantics_match_vet != PASS. This is a DRAFT; Skunkworks must VET + set PASS first.')
        return 3

    existing = {a.id for a in ps.all_atoms()}
    if atom.id in existing:
        print(f'SKIP (idempotent; already present): {atom.id}')
        return 0

    ps.add_atom(atom, source='bucket_a_proof_record_parallelogram', note='4th PROOF_RECORD; Skunkworks SEMANTICS-MATCH VET PASS')

    post_n = sum(1 for _ in ps.all_atoms())
    post_axiom = axiom_term_count(ps)
    post_mod = module_liveness_ok()
    rb = ps.get_atom(f'math::{ATOM_ID}')
    rb_ok = (
        rb is not None
        and rb.kind == AtomKind.PROOF_RECORD
        and rb.algebra is None
        and rb.metadata.get('confidence_tier') == 'T0_PROVEN_FORMAL'
        and CLAIM_SCOPE in (rb.metadata.get('claim_scope') or '')
    )
    gate_ok = (post_axiom == 206) and post_mod and (post_n == pre_n + 1) and rb_ok
    print(f'POST: atoms={post_n}  axiom_term={post_axiom}  cap_pres={post_mod}')
    print(f'  read-back: kind={rb.kind.value if rb else None}  algebra={rb.algebra if rb else None}  '
          f'confidence_tier={rb.metadata.get("confidence_tier") if rb else None}  scope_present={CLAIM_SCOPE in (rb.metadata.get("claim_scope") or "") if rb else False}')
    if not gate_ok:
        print('HARD_FAIL: gate or read-back failed. Reverting.')
        ps.remove_atom(f'math::{ATOM_ID}', source='revert', note='gate fail')
        return 2

    print('=' * 72)
    print(f'4th PROOF_RECORD landed: math::{ATOM_ID}')
    print(f'  atoms {pre_n} -> {post_n}  |  axiom_term 206/206 PRESERVED  |  cap_pres 6/6 PRESERVED  |  no-algebra confirmed')
    print('=' * 72)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
