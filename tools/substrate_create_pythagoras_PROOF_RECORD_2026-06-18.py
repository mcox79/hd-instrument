"""One-off guarded creation of the FIRST PROOF_RECORD atom: PHASE II Lean Pythagoras-IP.

Path A (USER+Research CONCUR 2026-06-18; Skunkworks authors, Orchestrator witnesses, Testbed invariant-verifies).
Corrected schema model: AtomKind=PROOF_RECORD (the structural kind) + metadata.confidence_tier='T0_PROVEN_FORMAL'
(the trust level), mirroring RESEARCH_FINDING. NOT a kind literally named T0_PROVEN_FORMAL.

Skunkworks SEMANTICS-MATCH VET = PASS (2026-06-18): .olean artifact verified (45224 bytes), proof source verified
(real InnerProductSpace, exact orthogonality, no sorry/axiom, real-specialized norm_add_sq_real lemma).

6 SCHEMA-VET conditions (all inline):
 1. kind=AtomKind.PROOF_RECORD (not experiment_record)
 2. algebra=None (no-algebra structural guard -> excluded from axiom_term)
 3. mandatory claim-text scope VERBATIM (exact-not-approximate; real-not-complex) in description + metadata
 4. proof_obligation metadata (file + theorem + toolchain + olean + commit + RULE_M_LEAN ref)
 5. idempotent (id collision-skip) + inline gates (axiom_term 206/206 + cap_pres 6/6) + atomic + ASCII
 6. laptop-safe (single add_atom; no bge/CUDA)
"""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path('.').resolve()))

from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import Atom, AtomKind, Corpus, Tier

ATOM_ID = 'PROOF_pythagoras_ip_real_inner_product'

# Condition 3: the mandatory claim-text scope, VERBATIM (Skunkworks PHASE II SEMANTICS-MATCH VET).
CLAIM_SCOPE = (
    "Certifies the EXACT Pythagorean identity for REAL inner-product spaces under EXACT orthogonality "
    "(inner u v = 0): ||u + v||^2 = ||u||^2 + ||v||^2. Does NOT certify the substrate's "
    "APPROXIMATE-orthogonality binding regime (near-orthogonal random keys, inner ~= 0); the formal proof "
    "is the idealized identity ONLY. Real, not complex."
)

DESCRIPTION = (
    "PROOF_RECORD (confidence_tier T0_PROVEN_FORMAL): Pythagoras in real inner product spaces. "
    "theorem pythagoras_ip {V} [NormedAddCommGroup V] [InnerProductSpace R V] (u v : V) "
    "(h : inner u v = 0) : ||u + v||^2 = ||u||^2 + ||v||^2 := by rw [norm_add_sq_real, h]; ring. "
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
        # Condition 3: trust level (NOT the kind) + the verbatim scope
        'confidence_tier': 'T0_PROVEN_FORMAL',
        'claim_scope': CLAIM_SCOPE,
        # Condition 4: proof_obligation provenance (verify-the-referent: points at the VET'd proof)
        'proof_obligation': {
            'file': 'lean_oracle/pythagoras_ip_v1/PythagorasIpV1/Pythagoras.lean',
            'theorem': 'pythagoras_ip',
            'lean_toolchain': 'leanprover/lean4:v4.31.0',
            'mathlib': 'mathlib4 (lake cache; norm_add_sq_real)',
            'olean_artifact': 'lean_oracle/pythagoras_ip_v1/.lake/build/lib/lean/PythagorasIpV1/Pythagoras.olean (45224 bytes)',
            'lean_commit': '32e4a9a8',
            'lake_build': 'exit 0; target theorem built; no sorry/admit/axiom',
        },
        # Condition 2: no-algebra structural guard (mirrors RESEARCH_FINDING)
        'no_algebra_structural_guard': True,
        'axiom_term_promotion': 'SEPARATE explicit USER/PHASE-III authority; NEVER automatic on lake-PASS',
        # SEMANTICS-MATCH VET provenance
        'semantics_match_vet': 'PASS',
        'vet_by': 'skunkworks',
        'vet_date': '2026-06-18',
        'vet_checks': 'real-not-complex + exact-not-approximate + non-vacuous + real-specialized-lemma + olean-artifact-verified + no-sorry-axiom',
        'references_methodology_rule': 'RULE_M_LEAN_semantics_match_necessary_lake_pass_necessary_not_sufficient_T0_PROVEN_FORMAL',
        'eleventh_rule_clean': True,
        'phase': 'PHASE-2',
        'first_proof_record': True,
        'corrected_model': 'AtomKind=PROOF_RECORD + confidence_tier=T0_PROVEN_FORMAL (kind separate from trust-tier; USER+Research CONCUR 2026-06-18)',
        'source': 'path_A_one_off_skunkworks_authors_orchestrator_witnesses_testbed_invariant_verify_USER_decision_proxy',
    }
    return Atom(
        id=ATOM_ID,
        name='Proof record (T0_PROVEN_FORMAL): Pythagoras in real inner product spaces',
        description=DESCRIPTION,
        kind=AtomKind.PROOF_RECORD,   # condition 1
        tier=Tier.TIER_NA,            # structural tier; trust is metadata.confidence_tier
        corpus=Corpus.MATH,
        algebra=None,                 # condition 2: no-algebra
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
    existing = {a.id for a in ps.all_atoms()}
    if atom.id in existing:
        print(f'SKIP (idempotent; already present): {atom.id}')
        return 0

    ps.add_atom(atom, source='path_A_proof_record_pythagoras_ip', note='first PROOF_RECORD; Skunkworks SEMANTICS-MATCH VET PASS')

    post_n = sum(1 for _ in ps.all_atoms())
    post_axiom = axiom_term_count(ps)
    post_mod = module_liveness_ok()
    # POST verify-the-referent: read the atom back from the store
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
    print(f'FIRST PROOF_RECORD landed: math::{ATOM_ID}')
    print(f'  atoms {pre_n} -> {post_n}  |  axiom_term 206/206 PRESERVED  |  cap_pres 6/6 PRESERVED  |  no-algebra confirmed')
    print('=' * 72)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
