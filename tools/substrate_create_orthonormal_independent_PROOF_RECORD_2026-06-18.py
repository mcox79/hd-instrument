"""DRAFT guarded creation of the 5th PROOF_RECORD atom: orthonormal -> linearly independent (real IP).

STATUS: DRAFT -- DO NOT RUN until Skunkworks SEMANTICS-MATCH VET PASS + claim_scope finalized.
Mirrors the proven substrate_create_parallelogram_PROOF_RECORD template. Refuse-until-VET-PASS guard.

verify-the-referent (Exp-Dev, pre-VET):
 - lake build PythagorasIpV1.OrthonormalIndependent -> exit 0
 - olean: .lake/build/lib/lean/PythagorasIpV1/OrthonormalIndependent.olean (12184 bytes)
 - source: no sorry/admit/axiom/native_decide
 - canonical lemma Orthonormal.linearIndependent (Mathlib/Analysis/InnerProductSpace/Orthonormal.lean:181)
 - commit 3ce1d2a7
"""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path('.').resolve()))

from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import Atom, AtomKind, Corpus, Tier

ATOM_ID = 'PROOF_orthonormal_linearly_independent_real_inner_product'

CLAIM_SCOPE = (
    "Certifies that an ORTHONORMAL family in a REAL inner-product space is LINEARLY INDEPENDENT "
    "(theorem orthonormal_linear_independent: Orthonormal R v -> LinearIndependent R v). A genuinely "
    "inner-product-STRUCTURAL result (orthonormality, an inner-product notion, implies a linear-algebra "
    "property) -- distinct from the norm-identity/inequality batch (Pythagoras/Cauchy-Schwarz/triangle/"
    "parallelogram). Real, not complex. Idealized identity ONLY (no substrate approximate-regime claim)."
)

DESCRIPTION = (
    "PROOF_RECORD (confidence_tier T0_PROVEN_FORMAL): orthonormal family is linearly independent (real IP). "
    "theorem orthonormal_linear_independent {F} [NormedAddCommGroup F] [InnerProductSpace R F] {iota} "
    "{v : iota -> F} (hv : Orthonormal R v) : LinearIndependent R v := by exact hv.linearIndependent. "
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


def axiom_term_count(ps) -> int:
    return sum(
        1 for a in ps.all_atoms()
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
            'file': 'lean_oracle/pythagoras_ip_v1/PythagorasIpV1/OrthonormalIndependent.lean',
            'theorem': 'orthonormal_linear_independent',
            'lean_toolchain': 'leanprover/lean4:v4.31.0',
            'mathlib': 'mathlib4 (lake cache; Orthonormal.linearIndependent)',
            'olean_artifact': 'lean_oracle/pythagoras_ip_v1/.lake/build/lib/lean/PythagorasIpV1/OrthonormalIndependent.olean (12184 bytes)',
            'lean_commit': '3ce1d2a7',
            'lake_build': 'exit 0; target theorem built; no sorry/admit/axiom',
            'print_axioms': '[propext, Classical.choice, Quot.sound] CONFIRMED (standard trio; no sorryAx; Testbed 2nd-witness re-run)',
        },
        'no_algebra_structural_guard': True,
        'axiom_term_promotion': 'SEPARATE explicit USER/PHASE-III authority; NEVER automatic on lake-PASS',
        'inner_product_structural': 'TRUE -- orthonormality (IP notion) implies linear independence (structural, not a norm identity)',
        'semantics_match_vet': 'PENDING',   # Skunkworks sets PASS at VET
        'vet_by': 'skunkworks',
        'vet_date': 'PENDING',
        'vet_checks': 'real-not-complex + exact-not-approximate + non-vacuous + canonical-lemma(Orthonormal.linearIndependent) + olean-verified + no-sorry-axiom',
        'references_methodology_rule': 'RULE_M_LEAN_semantics_match_necessary_lake_pass_necessary_not_sufficient_T0_PROVEN_FORMAL',
        'eleventh_rule_clean': True,
        'phase': 'PHASE-2',
        'bucket': 'A_cert_stream_lean_batch_proof_5_orthonormal_independence_IP_structural',
        'corrected_model': 'AtomKind=PROOF_RECORD + confidence_tier=T0_PROVEN_FORMAL',
        'source': 'bucket_a_proof_5_orthonormal_independent_user_get_everyone_moving',
    }
    return Atom(
        id=ATOM_ID,
        name='Proof record (T0_PROVEN_FORMAL): orthonormal family is linearly independent (real inner product space)',
        description=DESCRIPTION,
        kind=AtomKind.PROOF_RECORD,
        tier=Tier.TIER_NA,
        corpus=Corpus.MATH,
        algebra=None,
        metadata=metadata,
    )


def main() -> int:
    ps = PartitionedStore(Path('data/substrate_index'))
    pre_n = sum(1 for _ in ps.all_atoms()); pre_axiom = axiom_term_count(ps); pre_mod = module_liveness_ok()
    print(f'PRE: atoms={pre_n}  axiom_term={pre_axiom}  cap_pres(mod6/6)={pre_mod}')
    if not pre_mod or pre_axiom != 206:
        print('PRE-GATE FAIL. Halting; no mutation.'); return 1
    atom = build_atom()
    if atom.metadata.get('semantics_match_vet') != 'PASS':
        print('REFUSE: semantics_match_vet != PASS. DRAFT; Skunkworks must VET + set PASS first.'); return 3
    if ps.get_atom(f'math::{ATOM_ID}') is not None:
        print(f'SKIP (idempotent): {ATOM_ID}'); return 0
    ps.add_atom(atom, source='bucket_a_proof_record_orthonormal_independent', note='5th PROOF_RECORD; Skunkworks SEMANTICS-MATCH VET PASS')
    post_n = sum(1 for _ in ps.all_atoms()); post_axiom = axiom_term_count(ps); post_mod = module_liveness_ok()
    rb = ps.get_atom(f'math::{ATOM_ID}')
    rb_ok = (rb is not None and rb.kind == AtomKind.PROOF_RECORD and rb.algebra is None
             and rb.metadata.get('confidence_tier') == 'T0_PROVEN_FORMAL' and CLAIM_SCOPE in (rb.metadata.get('claim_scope') or ''))
    gate_ok = (post_axiom == 206) and post_mod and (post_n == pre_n + 1) and rb_ok
    print(f'POST: atoms={post_n}  axiom_term={post_axiom}  cap_pres={post_mod}  read-back_ok={rb_ok}')
    if not gate_ok:
        print('HARD_FAIL: gate/read-back failed. Reverting.')
        ps.remove_atom(f'math::{ATOM_ID}', source='revert', note='gate fail'); return 2
    print('=' * 72)
    print(f'5th PROOF_RECORD landed: math::{ATOM_ID}  atoms {pre_n}->{post_n}  axiom_term 206/206  cap_pres 6/6  no-algebra')
    print('=' * 72)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
