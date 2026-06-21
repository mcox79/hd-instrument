"""Skunkworks 2026-06-21 -- atomize (on Research's REQUEST) a Director-lane process METHODOLOGY_RULE (CERT-NEUTRAL, pq=None):
RESEARCH-DELIVERY-WITH-A-FALSIFIABLE-PREREG MUST ROUTE TO SKUNKWORKS (else TRANSLATION-GAP / dead-end in the cascade).
Verify-the-referent at the Director ROUTING layer: a Research delivery containing a falsifiable pre-reg / decisive-test
section MUST have a corresponding routing note to Skunkworks for SCHEMA-VET-or-defer triage; a falsifiable-pre-reg
WITHOUT a routing note is a DEAD-END (never enters the experiment cascade). Empirical witness: the 2026-06-21 audit of
past-4-days research deliveries found ~33% gap rate (4 of 12 sampled). Sibling to the verify-the-referent family
(eval-protocol-referent + verify-own-routing-claim). Research-authored substance; Skunkworks atom-author framing + A5.
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
    id='RULE_research_delivery_with_prereg_must_route_to_skunkworks_else_translation_gap',
    name=('Methodology rule (Director-lane process): a Research delivery containing a falsifiable pre-reg / decisive-test '
          'section MUST have a corresponding routing note to Skunkworks for SCHEMA-VET-or-defer triage -- a falsifiable-'
          'pre-reg WITHOUT a routing note is a TRANSLATION-GAP (dead-end, never enters the experiment cascade). '
          'Verify-the-referent at the Director routing layer'),
    description=(
        'Research-delivery-with-a-falsifiable-prereg-must-route-to-Skunkworks-else-translation-gap. A Research/Director '
        'deliverable that contains a FALSIFIABLE pre-reg or decisive-test section (HARD-PASS/FAIL bands, a cheap decisive '
        'test, pre-flight gates) MUST be accompanied by a ROUTING NOTE to Skunkworks (cert-owner) for SCHEMA-VET-or-defer '
        'triage. Filing the research delivery WITHOUT the routing note is a TRANSLATION-GAP: the pre-reg never enters the '
        'experiment cascade (no SCHEMA-VET -> no cell-author -> dead-end), even though the research is sound. This is the '
        'verify-the-referent family applied to the Director ROUTING layer -- the discipline equivalent of cite-without-'
        'verify, but for routing: producing a deliverable a downstream lane needs, without the hand-off that triggers it. '
        'ACTION (Director): for every delivery with a falsifiable-pre-reg/decisive-test section, file the Skunkworks '
        'routing note in the SAME cycle; periodically audit recent deliveries for un-routed pre-regs (the gap is silent). '
        'ACTION (Skunkworks): on triage, give a one-line disposition (SCHEMA-VET-when-bandwidth / DEFER-to-backlog / '
        'SUPERSEDED-by-X / RE-ROUTE) so the deliverable is not a dead-end. EMPIRICAL WITNESS: the 2026-06-21 audit of '
        'past-4-days research deliveries (USER-triggered) found a ~33% gap rate (4 of 12 sampled had falsifiable pre-regs '
        'never routed) -- higher than intuited; the silent gap warrants a standing audit. Research-authored substance '
        '(requested Skunkworks atomize on its behalf); CERT-NEUTRAL META rule (pq=None). Composes with the verify-the-'
        'referent family (eval-protocol-referent + verify-own-routing-claim + cited-number-must-reproduce).'),
    kind=AtomKind.METHODOLOGY_RULE, tier=Tier.TIER_METHODOLOGY, corpus=Corpus.META, algebra=None,
    metadata={'confidence':'high','eleventh_rule_clean':True,'extracted_by':'skunkworks','extracted_date':'2026-06-21',
              'rule_class':'process','status':'ADOPTED','substrate_internal_verified':True,
              'term_class':'PROCESS_KNOWLEDGE_NON_MATH','research_authored':True,'atomized_on_behalf_of':'research',
              'source':'translation_gap_routing_audit_research_requested_skunkworks_atomized_2026_06_21',
              'witnesses':['2026-06-21 USER-triggered audit of past-4-days research deliveries: ~33% gap rate '
                           '(4 of 12 sampled had falsifiable pre-regs never routed to Skunkworks for SCHEMA-VET)'],
              'composes_with':['RULE_metric_referent_carries_implicit_eval_protocol_match_it_to_reproduce',
                               'RULE_verify_own_routing_claim_on_cheap_synthetic_before_fleet_builds',
                               'RULE_cited_number_must_reproduce_from_the_cell_else_miscite',
                               'RULE_verify_referent_arrives_applies_to_data_paths_not_just_atoms']})


def main():
    ps = PartitionedStore(Path('data/substrate_index'))
    pre_cert, pre_ax, pre_mod = cert(ps), axiom(ps), modlive(); pre_atoms = len(list(ps.all_atoms()))
    print(f"PRE: atoms={pre_atoms} CERT={pre_cert} axiom={pre_ax} cap_pres={pre_mod}")
    if not pre_mod or pre_ax != 206 or pre_cert != 583:
        print(f"PRE-GATE FAIL (axiom={pre_ax}!=206 / cap_pres={pre_mod} / CERT={pre_cert}!=583). HALT."); return 1
    existed = ps.get_atom(ATOM.qualified_id) is not None
    if existed: print(f"  SKIP exists: {ATOM.id}")
    else:
        ps.add_atom(ATOM, source='skunkworks_atomize_translation_gap_routing_rule_on_behalf_research_2026_06_21', note='Director-lane process METHODOLOGY_RULE (CERT-neutral, pq=None); research-delivery-with-prereg-must-route-else-translation-gap')
        print(f"  ADD: {ATOM.id}")
    ps2 = PartitionedStore(Path('data/substrate_index'))
    post_cert, post_ax, post_mod = cert(ps2), axiom(ps2), modlive(); post_atoms = len(list(ps2.all_atoms()))
    a2 = ps2.get_atom(ATOM.qualified_id); landed = a2 is not None
    bad = landed and ((a2.algebra is not None) or (a2.metadata or {}).get('provenance_quality')=='CERT_CHAIN_GRADE'
                      or str(a2.kind.name)!='METHODOLOGY_RULE')
    print(f"POST: atoms={post_atoms} (+{post_atoms-pre_atoms}) CERT={post_cert} (expect 583 UNCHANGED) axiom={post_ax} (expect 206) cap_pres={post_mod} landed={landed} bad={bad}")
    gate = (post_cert==583 and post_ax==206 and post_mod and landed and not bad and post_atoms==pre_atoms+(0 if existed else 1))
    print("GATE:", "OK -- translation-gap routing RULE atomized (on Research's behalf), CERT 583 UNCHANGED" if gate else "FAIL")
    print(f"FOR_RECIPROCAL_CHECK: --expect-cert {post_cert} --expect-atoms {post_atoms}")
    return 0 if gate else 2


if __name__ == '__main__':
    raise SystemExit(main())
