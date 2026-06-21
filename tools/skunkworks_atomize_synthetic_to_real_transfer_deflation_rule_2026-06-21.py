"""Skunkworks 2026-06-21 -- atomize a cert-VET METHODOLOGY_RULE (CERT-NEUTRAL, pq=None):
MECHANISM-CONFIRMED-ON-SYNTHETIC MUST DEFLATE FURTHER FOR REAL-DATA TRANSFER.
When a revival/lever's mechanism is validated on a SYNTHETIC PoC, P(success on REAL data) must be deflated by an
ADDITIONAL ~0.20-0.30 beyond the standard lit-scan calibration -- because synthetic structure != real structure and
the gap can be NEAR-TOTAL. Witness: the whitening-revival. Skunkworks's CPU PoC showed shrinkage-ZCA RECOVERS ARM1
(iso 0.807 / aniso 0.004 / ZCA 0.843) on SYNTHETIC anisotropy (a SINGLE common-mode, mean_cos~0.90 -> ZCA removes it
cleanly). On REAL pythia keys ARM1_whitened = 0.025 (near-ZERO recovery) -- the transfer FAILED near-totally because
real anisotropy is MULTI-DIRECTIONAL / heavy-tailed-spectrum, which shrinkage-ZCA does not isotropize. The PROCESS was
right (de-risk on synthetic per verify-own-routing-claim + PRE-REGISTER the synthetic-vs-real risk); the synthetic was
a BEST-CASE. Composes with verify-own-routing-claim (synthetic confirmation is necessary-NOT-sufficient).
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
    id='RULE_mechanism_confirmed_on_synthetic_must_deflate_for_real_data_transfer',
    name=('Methodology rule (cert-VET): a mechanism validated on a SYNTHETIC PoC must DEFLATE P(success on REAL data) '
          'by an ADDITIONAL ~0.20-0.30 -- synthetic structure != real structure and the gap can be NEAR-TOTAL; '
          'synthetic confirmation is necessary-NOT-sufficient'),
    description=(
        'Mechanism-confirmed-on-synthetic-must-deflate-for-real-data-transfer. A revival/lever whose mechanism is '
        'validated on a cheap SYNTHETIC PoC (the verify-own-routing-claim discipline) is DE-RISKED but NOT proven on '
        'real data. P(success on real data) must be deflated by an ADDITIONAL ~0.20-0.30 beyond the standard lit-scan '
        'calibration penalty, because the SYNTHETIC encodes idealized/best-case structure that real data violates -- and '
        'the gap can be NEAR-TOTAL. ACTION: when routing a synthetic-confirmed revival, (1) state the synthetic-vs-real '
        'transfer risk explicitly + pre-register the watch ("own it if real underperforms"); (2) deflate the success '
        'probability accordingly; (3) treat the synthetic as a BEST-CASE upper bound, not a prediction. WITNESS '
        '(2026-06-21 whitening-revival): the CPU PoC showed shrinkage-ZCA RECOVERS the M-indep superposition ARM1 '
        '(isotropic 0.807 / anisotropic 0.004 / ZCA 0.843) on a SINGLE-common-mode synthetic (mean_cos~0.90, which ZCA '
        'removes cleanly); on REAL pythia learned keys ARM1_whitened = 0.025 (near-ZERO recovery) -- transfer FAILED '
        'near-totally because real anisotropy is MULTI-DIRECTIONAL/heavy-tailed, not a single common-mode. The process '
        'was correct (de-risk + pre-register the risk); the synthetic was a best-case; the lesson is the deflation. '
        'CERT-NEUTRAL META rule (pq=None). Composes with verify-own-routing-claim (synthetic de-risk) + the '
        'verify-the-referent family.'),
    kind=AtomKind.METHODOLOGY_RULE, tier=Tier.TIER_METHODOLOGY, corpus=Corpus.META, algebra=None,
    metadata={'confidence':'high','eleventh_rule_clean':True,'extracted_by':'skunkworks','extracted_date':'2026-06-21',
              'rule_class':'cert_vet','status':'ADOPTED','substrate_internal_verified':True,
              'term_class':'PROCESS_KNOWLEDGE_NON_MATH','research_endorsed':True,
              'source':'synthetic_to_real_transfer_deflation_whitening_revival_overestimate_skunkworks_2026_06_21',
              'witnesses':['whitening-revival 2026-06-21: CPU PoC ZCA-recovers ARM1 0.843 on single-common-mode synthetic '
                           '-> real pythia ARM1_whitened 0.025 (near-zero) = transfer failed near-totally (real anisotropy '
                           'multi-directional, not single common-mode); risk was pre-registered + owned'],
              'composes_with':['RULE_verify_own_routing_claim_on_cheap_synthetic_before_fleet_builds',
                               'RULE_info_theoretic_floor_check_before_M_independence_claim',
                               'RULE_metric_referent_carries_implicit_eval_protocol_match_it_to_reproduce']})


def main():
    ps = PartitionedStore(Path('data/substrate_index'))
    pre_cert, pre_ax, pre_mod = cert(ps), axiom(ps), modlive(); pre_atoms = len(list(ps.all_atoms()))
    print(f"PRE: atoms={pre_atoms} CERT={pre_cert} axiom={pre_ax} cap_pres={pre_mod}")
    if not pre_mod or pre_ax != 206 or pre_cert != 583:
        print(f"PRE-GATE FAIL (axiom={pre_ax}!=206 / cap_pres={pre_mod} / CERT={pre_cert}!=583). HALT."); return 1
    existed = ps.get_atom(ATOM.qualified_id) is not None
    if existed: print(f"  SKIP exists: {ATOM.id}")
    else:
        ps.add_atom(ATOM, source='skunkworks_synthetic_to_real_transfer_deflation_2026_06_21', note='cert-VET METHODOLOGY_RULE (CERT-neutral); deflate synthetic-confirmed mechanism for real-data transfer')
        print(f"  ADD: {ATOM.id}")
    ps2 = PartitionedStore(Path('data/substrate_index'))
    post_cert, post_ax, post_mod = cert(ps2), axiom(ps2), modlive(); post_atoms = len(list(ps2.all_atoms()))
    a2 = ps2.get_atom(ATOM.qualified_id); landed = a2 is not None
    bad = landed and ((a2.algebra is not None) or (a2.metadata or {}).get('provenance_quality')=='CERT_CHAIN_GRADE'
                      or str(a2.kind.name)!='METHODOLOGY_RULE')
    print(f"POST: atoms={post_atoms} (+{post_atoms-pre_atoms}) CERT={post_cert} (expect 583 UNCHANGED) axiom={post_ax} (expect 206) cap_pres={post_mod} landed={landed} bad={bad}")
    gate = (post_cert==583 and post_ax==206 and post_mod and landed and not bad and post_atoms==pre_atoms+(0 if existed else 1))
    print("GATE:", "OK -- synthetic-to-real-deflation RULE atomized, CERT 583 UNCHANGED" if gate else "FAIL")
    return 0 if gate else 2


if __name__ == '__main__':
    raise SystemExit(main())
