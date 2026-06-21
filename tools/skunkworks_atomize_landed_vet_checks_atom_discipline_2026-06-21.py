"""Skunkworks 2026-06-21 -- atomize 1 durable META discipline (CERT-NEUTRAL): the phase4b stale-chain-grade lesson.
METHODOLOGY_RULE / META / TIER_METHODOLOGY / algebra=None / pq=None -> does NOT touch CERT 588.
Pairs the JUDGMENT (this atom) with its deterministic CHECK (D4 atom<->cell drift in cert_integrity_audit_v1, fc5ea754)
-- the substrate-autonomy unit ("encode every audit judgment as a deterministic self-applied check").
A5: PRE CERT=588 -> POST 588 UNCHANGED; axiom 206 UNCHANGED (META not axiom-counted); cap_pres 6/6; +1 atom; reloads.
ASCII. Idempotent skip-if-exists.
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
    id='RULE_landed_vet_must_check_existing_atom_not_just_rule_result',
    name=('Methodology rule: a landed-VET that rules a cell-result BELOW chain-grade (or a cell reframed weaker) MUST '
          'also query+demote any PRE-EXISTING atom for that cell -- not just rule the result -- else a stale chain-grade '
          'atom persists = inflation (verify-the-referent-ARRIVES applied to ATOMS)'),
    description=(
        'A cell can be atomized CHAIN_GRADE when it FIRST HARD_PASSes, BEFORE a later landed-VET rules the result below '
        'chain-grade / a reframe weakens the cell. If the cert-owner VET rules only the RESULT and does not query the Store '
        'for an EXISTING atom on that cell, the pre-existing chain-grade atom PERSISTS -- a stale chain-grade for a '
        'not-chain-grade result = silent inflation. EVIDENCE (phase4b, 2026-06-20): T3/EXP_phase4b_multistep_pull_up_v2 was '
        'atomized pq=CERT_CHAIN_GRADE/HARD_PASS with the "40x over 1-op baseline" honest_scope (the div-by-near-zero artifact) '
        'when v2 first HARD_PASSed; my landed-VET later ruled the RESULT not-chain-grade + Exp-Dev reframed the CELL metrics.json '
        'to MEASURED_MECHANISM (40c88971) -- but the ATOM stayed chain-grade until an atomize-while-waiting check caught it '
        '(demoted CERT 589->588, 0c5c5f6a). The miss was verify-the-referent-arrives NOT applied to atoms: I verified my own '
        'result-ruling but not that no stale atom referent existed. RULE: when a VET rules a cell below chain-grade (or a cell is '
        'reframed weaker), the cert-owner MUST (a) query the Store for an existing atom on that cell and (b) demote it in the SAME '
        'disposition. MECHANICALLY ENFORCED by the D4 atom<->cell-drift check in tools/skunkworks_cert_integrity_audit_v1.py '
        '(file-grounded: reads each chain-grade atom OWN cell metrics.json; flags only inflation-direction disagreement -- atom '
        'claims PASS but cell records weaker -- so it does NOT false-positive on legitimately-recorded chain-grade negatives/bounds). '
        'This atom is the JUDGMENT; D4 is the deterministic self-applied CHECK (the substrate-autonomy pairing).'),
    kind=AtomKind.METHODOLOGY_RULE, tier=Tier.TIER_METHODOLOGY, corpus=Corpus.META, algebra=None,
    metadata={'extracted_by':'skunkworks','extracted_date':'2026-06-21','term_class':'methodology',
              'eleventh_rule_clean':True,'substrate_internal_verified':True,'status':'active','confidence':'high',
              'rule_class':'cert_atom_lifecycle',
              'witnesses':['phase4b_stale_chain_grade_persisted_after_result_ruled_not_chain_grade_CERT_589_to_588_2026-06-20'],
              'enforced_by':'tools/skunkworks_cert_integrity_audit_v1.py::D4_atom_cell_drift',
              'composes_with':['RULE_disposition_execution_must_preserve_per_atom_outcomes',
                               'RULE_cited_number_must_reproduce_from_the_cell_else_miscite',
                               'RULE_4_layer_reciprocal_witness_for_high_stakes_ships'],
              'source':'skunkworks_session_2026-06-21_phase4b_stale_chain_grade_catch'})


def main():
    ps = PartitionedStore(Path('data/substrate_index'))
    pre_cert, pre_ax, pre_mod = cert(ps), axiom(ps), modlive()
    pre_atoms = len(list(ps.all_atoms()))
    print(f"PRE: atoms={pre_atoms} CERT={pre_cert} axiom={pre_ax} cap_pres={pre_mod}")
    if not pre_mod or pre_ax != 206 or pre_cert != 588:
        print(f"PRE-GATE FAIL (axiom={pre_ax}!=206 / cap_pres={pre_mod} / CERT={pre_cert}!=588). HALT."); return 1
    existed = ps.get_atom(ATOM.qualified_id) is not None
    if existed:
        print(f"  SKIP exists: {ATOM.id}")
    else:
        ps.add_atom(ATOM, source='skunkworks_landed_vet_checks_atom_discipline_2026_06_21',
                    note='phase4b stale-chain-grade discipline (CERT-neutral; paired with D4 check)')
        print(f"  ADD: {ATOM.id}")
    ps2 = PartitionedStore(Path('data/substrate_index'))
    post_cert, post_ax, post_mod = cert(ps2), axiom(ps2), modlive()
    post_atoms = len(list(ps2.all_atoms()))
    a2 = ps2.get_atom(ATOM.qualified_id); landed = a2 is not None
    bad = landed and ((a2.algebra is not None) or (a2.metadata or {}).get('provenance_quality')=='CERT_CHAIN_GRADE')
    print(f"POST: atoms={post_atoms} (+{post_atoms-pre_atoms}) CERT={post_cert} (expect 588 UNCHANGED) axiom={post_ax} (expect 206) cap_pres={post_mod} landed={landed} bad={bad}")
    gate = (post_cert==588 and post_ax==206 and post_mod and landed and not bad and post_atoms==pre_atoms+(0 if existed else 1))
    print("GATE:", "OK -- discipline atomized, CERT 588 UNCHANGED (CERT-neutral)" if gate else "FAIL")
    print(f"FOR_RECIPROCAL_CHECK: --expect-cert {post_cert} --expect-atoms {post_atoms}")
    return 0 if gate else 2


if __name__ == '__main__':
    raise SystemExit(main())
