"""Skunkworks 2026-06-21 -- atomize a new cert-VET METHODOLOGY_RULE (CERT-NEUTRAL, pq=None):
INFO-THEORETIC-FLOOR-CHECK-BEFORE-M-INDEPENDENCE-CLAIM. Emerged from the dense-projected-KV envelope SCHEMA-VET:
"M-independent memory for M DISTINCT arbitrary values is information-theoretically IMPOSSIBLE" -- M distinct d-vectors
need O(M*d) just to REPRESENT (entropy floor), so no mechanism (superposition/attention/anything) can store them
M-independently. An M-independence claim is only COHERENT when the value-space has FIXED cardinality (a vocabulary /
codebook of size C, M-independent); then recall is value-CLASS recall, and M-indep mechanisms (superposition O(d^2) +
fixed C-codebook decode) are possible. Before pre-registering/claiming "M-independent storage", check the entropy floor
of the value-space; if values are M distinct arbitrary vectors the claim fails by THEOREM (not by mechanism) -- reframe
to fixed-codebook value-class recall or drop the M-independence claim.
A5: PRE CERT=583 -> POST 583 UNCHANGED (METHODOLOGY_RULE pq=None); axiom 206; cap_pres 6/6; +1 atom; reloads. ASCII. Idempotent.
"""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path('.').resolve()))
from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import Atom, AtomKind, Corpus, Tier


def cert(p):
    return sum(1 for a in p.all_atoms() if (a.metadata or {}).get('provenance_quality') == 'CERT_CHAIN_GRADE')
def axiom(p):
    return sum(1 for a in p.all_atoms()
               if str(a.corpus.name)=='MATH' and str(a.tier.name) in ('TIER_2_PRIMITIVE','TIER_3_ALGORITHM')
               and a.algebra and len(a.algebra)>=3 and 'oeis' not in str(a.id).lower() and not str(a.id).startswith('T3/wikidata_'))
def modlive():
    import importlib
    return all(hasattr(importlib.import_module(m), s) for m, s in [
        ('backend.substrate_index.hmm_decoder','viterbi_decode'),('hdlab.perceptron','StructuredPerceptron'),
        ('backend.substrate_index.sequence_labeler','NERTagger'),('hdlab.bayesian_inference','EMMixture'),
        ('backend.substrate_index.intent_classifier','IntentClassifier'),('backend.substrate_index.refuse_gated_retriever','RefuseGatedRetriever')])


ATOM = Atom(
    id='RULE_info_theoretic_floor_check_before_M_independence_claim',
    name=('Methodology rule (cert-VET): before claiming/pre-registering "M-INDEPENDENT storage", check the '
          'INFORMATION-THEORETIC FLOOR of the value-space -- M DISTINCT ARBITRARY values cost O(M*d) by entropy '
          'alone, so M-independence is IMPOSSIBLE BY THEOREM there (regardless of mechanism); it is only coherent '
          'with a FIXED-cardinality value-space (vocab/codebook size C), as value-CLASS recall'),
    description=(
        'Info-theoretic-floor-check-before-M-independence-claim. When a capability claims M-INDEPENDENT memory '
        '(storage cost not growing with the number of stored items M -- e.g. a superposition store W=sum v k^T at '
        'O(d^2)), CHECK THE VALUE-SPACE ENTROPY FLOOR FIRST: M distinct arbitrary d-dim values require O(M*d) bits '
        'just to REPRESENT (information-theoretic lower bound) -- so NO mechanism (superposition, modern-Hopfield/'
        'attention, sparse, anything) can store M distinct arbitrary values M-independently. The M-independence claim '
        'fails by THEOREM, not by mechanism, and an experiment that "tests" it would be measuring an impossibility. '
        'The claim is ONLY coherent when the value-space has FIXED cardinality C (a vocabulary / fixed codebook, '
        'M-independent): then the task is value-CLASS recall (which of C classes), and M-independent mechanisms '
        '(superposition O(d^2) store + fixed C-codebook decode, O(C*d)) ARE possible. ACTION: before pre-registering '
        'or certifying an M-independence claim, (1) identify the value-space cardinality; (2) if values are M distinct '
        'arbitrary vectors -> the M-independence claim is info-theoretically void -> reframe to fixed-codebook value-'
        'CLASS recall (the realistic LM/vocab semantics: C=vocab_size, M=facts mapping into it) OR drop the claim; '
        '(3) ensure BOTH the store AND the readout/cleanup are M-independent (a fixed-codebook decode, NOT argmax over '
        'M stored values -- else O(M*d) sneaks back in at readout). This is verify-the-referent on the CLAIM TYPE '
        '(is M-independence even achievable for this value-space?), sibling to the capacity-relative gate and the '
        'lever-design cost gate. PROVENANCE: emerged from the dense-projected-KV envelope SCHEMA-VET (2026-06-21); '
        'caught that the win-axis (recall>=0.80 at M-independent memory) was incoherent with M distinct values and '
        'that Exp-Dev lean-(a) argmax-over-M-values reintroduced O(M*d) at readout; resolved by a fixed C=256 codebook '
        'decode for all arms. CERT-NEUTRAL META rule (pq=None); Research-endorsed (Director catalog).'),
    kind=AtomKind.METHODOLOGY_RULE, tier=Tier.TIER_METHODOLOGY, corpus=Corpus.META, algebra=None,
    metadata={'confidence':'high','eleventh_rule_clean':True,'extracted_by':'skunkworks','extracted_date':'2026-06-21',
              'rule_class':'cert_vet','status':'ADOPTED','substrate_internal_verified':True,
              'term_class':'PROCESS_KNOWLEDGE_NON_MATH','research_endorsed':True,
              'source':'info_theoretic_floor_M_independence_dense_projected_KV_envelope_schema_vet_skunkworks_2026_06_21',
              'witnesses':['dense-projected-KV envelope SCHEMA-VET 2026-06-21: win-axis (M-indep recall>=0.80) incoherent '
                           'with M distinct arbitrary values (O(M*d) entropy floor) -> reframed to fixed C=256 codebook '
                           'value-CLASS recall; resolved Exp-Dev lean-(a) argmax-over-M-values disguised-O(M*d)-at-readout'],
              'composes_with':['RULE_selector_lever_chain_grade_requires_genuine_cost_else_collapses_to_fixed_best',
                               'RULE_verify_referent_arrives_applies_to_data_paths_not_just_atoms',
                               'RULE_cited_number_must_reproduce_from_the_cell_else_miscite']})


def main():
    ps = PartitionedStore(Path('data/substrate_index'))
    pre_cert, pre_ax, pre_mod = cert(ps), axiom(ps), modlive(); pre_atoms = len(list(ps.all_atoms()))
    print(f"PRE: atoms={pre_atoms} CERT={pre_cert} axiom={pre_ax} cap_pres={pre_mod}")
    if not pre_mod or pre_ax != 206 or pre_cert != 583:
        print(f"PRE-GATE FAIL (axiom={pre_ax}!=206 / cap_pres={pre_mod} / CERT={pre_cert}!=583). HALT."); return 1
    existed = ps.get_atom(ATOM.qualified_id) is not None
    if existed: print(f"  SKIP exists: {ATOM.id}")
    else:
        ps.add_atom(ATOM, source='skunkworks_info_theoretic_floor_M_independence_rule_2026_06_21', note='cert-VET METHODOLOGY_RULE (CERT-neutral, pq=None); info-theoretic floor before M-independence claim')
        print(f"  ADD: {ATOM.id}")
    ps2 = PartitionedStore(Path('data/substrate_index'))
    post_cert, post_ax, post_mod = cert(ps2), axiom(ps2), modlive(); post_atoms = len(list(ps2.all_atoms()))
    a2 = ps2.get_atom(ATOM.qualified_id); landed = a2 is not None
    bad = landed and ((a2.algebra is not None) or (a2.metadata or {}).get('provenance_quality')=='CERT_CHAIN_GRADE'
                      or str(a2.kind.name)!='METHODOLOGY_RULE')
    print(f"POST: atoms={post_atoms} (+{post_atoms-pre_atoms}) CERT={post_cert} (expect 583 UNCHANGED) axiom={post_ax} (expect 206) cap_pres={post_mod} landed={landed} bad={bad}")
    gate = (post_cert==583 and post_ax==206 and post_mod and landed and not bad and post_atoms==pre_atoms+(0 if existed else 1))
    print("GATE:", "OK -- info-theoretic-floor RULE atomized, CERT 583 UNCHANGED (CERT-neutral METHODOLOGY_RULE)" if gate else "FAIL")
    print(f"FOR_RECIPROCAL_CHECK: --expect-cert {post_cert} --expect-atoms {post_atoms}")
    return 0 if gate else 2


if __name__ == '__main__':
    raise SystemExit(main())
