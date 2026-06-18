"""DRAFT guarded creation of the 3rd PROOF_RECORD atom: Bucket A triangle inequality.

STATUS: DRAFT -- DO NOT RUN until Skunkworks SEMANTICS-MATCH VET PASS + claim_scope finalized.
Mirrors substrate_create_cauchy_schwarz_PROOF_RECORD_2026-06-18.py (proven template).

Framing A (Skunkworks CONCUR): canonical norm_add_le. MANDATORY honest scope (per her ruling):
the triangle inequality is TRUE IN ANY NORMED SPACE (does NOT use the inner-product structure);
certified here SPECIALIZED to real IP. Do NOT imply it is IP-specific (the parallelogram law is
the IP-specific result).

Schema model: AtomKind=PROOF_RECORD + metadata.confidence_tier='T0_PROVEN_FORMAL'.

verify-the-referent (Exp-Dev, pre-VET):
 - lake build PythagorasIpV1.Triangle -> exit 0 (1905 jobs; 20s incremental)
 - olean artifact: .lake/build/lib/lean/PythagorasIpV1/Triangle.olean (13192 bytes)
 - source: no sorry/admit/axiom/native_decide
 - #print axioms triangle_ip -> [propext, Classical.choice, Quot.sound] (standard trio; no sorryAx)
 - commit 44c47a17
"""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path('.').resolve()))

from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import Atom, AtomKind, Corpus, Tier

ATOM_ID = 'PROOF_triangle_inequality_real_inner_product'

# Condition 3: FINALIZED scope (Skunkworks SEMANTICS-MATCH VET PASS 2026-06-18, verbatim).
CLAIM_SCOPE = (
    "Certifies the EXACT triangle inequality ||u + v|| <= ||u|| + ||v|| for all u, v in a "
    "real inner-product space, holding UNCONDITIONALLY. This inequality is TRUE IN ANY NORMED "
    "SPACE and does NOT use the inner-product structure (proof: the canonical norm_add_le); it "
    "is certified here SPECIALIZED to the real inner-product setting for batch consistency. It "
    "is NOT an inner-product-specific result -- the inner-product-specific identity in this "
    "batch is the parallelogram law. Real, not complex."
)

DESCRIPTION = (
    "PROOF_RECORD (confidence_tier T0_PROVEN_FORMAL): triangle inequality in real inner product spaces. "
    "theorem triangle_ip {F} [NormedAddCommGroup F] [InnerProductSpace R F] (u v : F) "
    ": ||u + v|| <= ||u|| + ||v|| := by exact norm_add_le u v. "
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
            'file': 'lean_oracle/pythagoras_ip_v1/PythagorasIpV1/Triangle.lean',
            'theorem': 'triangle_ip',
            'lean_toolchain': 'leanprover/lean4:v4.31.0',
            'mathlib': 'mathlib4 (lake cache; norm_add_le)',
            'olean_artifact': 'lean_oracle/pythagoras_ip_v1/.lake/build/lib/lean/PythagorasIpV1/Triangle.olean (13192 bytes)',
            'lean_commit': '44c47a17',
            'lake_build': 'exit 0; 1905 jobs; target theorem built; no sorry/admit/axiom',
            'print_axioms': '[propext, Classical.choice, Quot.sound] (standard mathlib trio; no sorryAx)',
        },
        'no_algebra_structural_guard': True,
        'axiom_term_promotion': 'SEPARATE explicit USER/PHASE-III authority; NEVER automatic on lake-PASS',
        'framing': 'A_canonical_norm_add_le_holds_in_any_normed_space_specialized_to_real_IP_NOT_ip_specific',
        'semantics_match_vet': 'PASS',   # Skunkworks SEMANTICS-MATCH VET PASS 2026-06-18
        'vet_by': 'skunkworks',
        'vet_date': '2026-06-18',
        'vet_checks': 'real-not-complex + exact-not-approximate + non-vacuous + canonical-lemma(norm_add_le) + olean-artifact-verified + no-sorry-axiom + print-axioms-standard-trio + honest-scope-any-normed-space',
        'references_methodology_rule': 'RULE_M_LEAN_semantics_match_necessary_lake_pass_necessary_not_sufficient_T0_PROVEN_FORMAL',
        'eleventh_rule_clean': True,
        'phase': 'PHASE-2',
        'bucket': 'A_cert_stream_lean_batch_proof_3_of_3',
        'corrected_model': 'AtomKind=PROOF_RECORD + confidence_tier=T0_PROVEN_FORMAL (kind separate from trust-tier)',
        'source': 'bucket_a_exp_dev_authors_skunkworks_semantics_match_vet_testbed_2nd_witness',
    }
    return Atom(
        id=ATOM_ID,
        name='Proof record (T0_PROVEN_FORMAL): triangle inequality in real inner product spaces',
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

    ps.add_atom(atom, source='bucket_a_proof_record_triangle', note='3rd PROOF_RECORD; Skunkworks SEMANTICS-MATCH VET PASS')

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
    print(f'3rd PROOF_RECORD landed: math::{ATOM_ID}')
    print(f'  atoms {pre_n} -> {post_n}  |  axiom_term 206/206 PRESERVED  |  cap_pres 6/6 PRESERVED  |  no-algebra confirmed')
    print('=' * 72)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
