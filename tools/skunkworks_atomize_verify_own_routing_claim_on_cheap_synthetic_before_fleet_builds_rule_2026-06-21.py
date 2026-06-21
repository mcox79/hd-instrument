"""Skunkworks 2026-06-21 -- atomize a new cert-VET METHODOLOGY_RULE (CERT-NEUTRAL, pq=None):
VERIFY YOUR OWN ROUTING CLAIM ON CHEAP SYNTHETIC BEFORE THE FLEET BUILDS (auditor-due-diligence; the DUAL of verify-the-referent).
When you ROUTE a substantive next-cycle dispatch (a revival drill, a GPU cell, any claim that will cost the fleet expensive
compute), FIRST run a cheap synthetic/CPU verification of the routing CLAIM's MECHANISM yourself. If the mechanism doesn't hold
on synthetic, you saved the fleet an expensive build on a wrong claim; if it holds, the routing claim is grounded (and you can
hand the validated recipe to the cell-author). This is verify-the-referent turned on YOUR OWN output: don't make others rely on
a routing claim you haven't cheaply checked. Emerged from the whitening-revival CPU PoC (2026-06-21): Skunkworks routed
"the learned-key ARM1 collapse is fixable by isotropization", then ran a CPU PoC (isotropic holds / anisotropic collapses /
mean-center+shrinkage-ZCA recover) BEFORE Exp-Dev built the GPU cell -> mechanism CONFIRMED + cell recipe facilitated.
Research-endorsed (Director catalog). Composes with the verify-the-referent family + USER's negatives-to-revival standing.
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
    id='RULE_verify_own_routing_claim_on_cheap_synthetic_before_fleet_builds',
    name=('Methodology rule (cert-VET): before ROUTING a substantive next-cycle dispatch (a revival, a GPU cell, any '
          'claim that will cost the fleet expensive compute), cheaply VERIFY THE ROUTING CLAIM\'S MECHANISM YOURSELF '
          '(synthetic/CPU) -- the DUAL of verify-the-referent (don\'t make others build on a claim you haven\'t checked); '
          'saves fleet bandwidth if wrong, grounds + supplies a validated recipe if right'),
    description=(
        'Verify-your-own-routing-claim-on-cheap-synthetic-before-the-fleet-builds (auditor-due-diligence). When you ROUTE '
        'a substantive next-cycle dispatch -- a revival drill, a GPU cell, a strategy pivot, any claim a peer will spend '
        'expensive compute building on -- FIRST run a CHEAP (synthetic / CPU / closed-form) verification of the routing '
        'CLAIM\'S MECHANISM. This is verify-the-referent turned on YOUR OWN output: the verify-the-referent family checks '
        'things you RELY ON (cited atom mechanism / data-path provenance / implicit eval protocol / routing-subagent '
        'output); THIS rule checks the claim YOU PRODUCE before others rely on it. PAYOFF: (1) if the mechanism does NOT '
        'hold on the cheap check, you just saved the fleet an expensive build on a wrong routing claim; (2) if it holds, '
        'the routing claim is grounded AND you can hand the cell-author a validated recipe (params, expected magnitudes) -> '
        'faster, more-confident build. ACTION: before a routed dispatch, ask "can I cheaply test the core mechanism of this '
        'claim without the expensive resource (GPU/runner/model)?" -- usually yes via a synthetic stand-in that reuses the '
        'real mechanism code; run it; report the result with the routing. PROVENANCE: whitening-revival CPU PoC '
        '(2026-06-21) -- Skunkworks routed "the learned-key ARM1 superposition collapse is FIXABLE by isotropization", '
        'then ran a synthetic CPU PoC (isotropic ARM1 holds 0.807 / anisotropic collapses to chance 0.004 / mean-center '
        '0.806 + shrinkage-ZCA 0.843 RECOVER) BEFORE Exp-Dev built the GPU cell -> mechanism CONFIRMED across all 4 legs + '
        'the GPU cell recipe (shrinkage-ZCA, d x d M-indep whiten-matrix) facilitated. CERT-NEUTRAL META rule (pq=None); '
        'Research-endorsed. Composes with the verify-the-referent family + USER\'s route-negatives-to-revival-drills '
        'standing rule (don\'t just route revivals -- verify the revival\'s mechanism is grounded before the fleet builds).'),
    kind=AtomKind.METHODOLOGY_RULE, tier=Tier.TIER_METHODOLOGY, corpus=Corpus.META, algebra=None,
    metadata={'confidence':'high','eleventh_rule_clean':True,'extracted_by':'skunkworks','extracted_date':'2026-06-21',
              'rule_class':'cert_vet','status':'ADOPTED','substrate_internal_verified':True,
              'term_class':'PROCESS_KNOWLEDGE_NON_MATH','research_endorsed':True,
              'source':'verify_own_routing_claim_on_synthetic_whitening_revival_cpu_poc_skunkworks_2026_06_21',
              'witnesses':['whitening-revival CPU PoC 2026-06-21: routed "ARM1 collapse fixable by isotropization", then '
                           'synthetic PoC (iso holds 0.807 / aniso collapses 0.004 / mean-center 0.806 + ZCA 0.843 recover) '
                           'BEFORE the GPU cell -> mechanism confirmed + recipe facilitated'],
              'composes_with':['RULE_metric_referent_carries_implicit_eval_protocol_match_it_to_reproduce',
                               'RULE_info_theoretic_floor_check_before_M_independence_claim',
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
        ps.add_atom(ATOM, source='skunkworks_verify_own_routing_claim_on_synthetic_rule_2026_06_21', note='cert-VET METHODOLOGY_RULE (CERT-neutral, pq=None); verify your own routing claim on cheap synthetic before the fleet builds')
        print(f"  ADD: {ATOM.id}")
    ps2 = PartitionedStore(Path('data/substrate_index'))
    post_cert, post_ax, post_mod = cert(ps2), axiom(ps2), modlive(); post_atoms = len(list(ps2.all_atoms()))
    a2 = ps2.get_atom(ATOM.qualified_id); landed = a2 is not None
    bad = landed and ((a2.algebra is not None) or (a2.metadata or {}).get('provenance_quality')=='CERT_CHAIN_GRADE'
                      or str(a2.kind.name)!='METHODOLOGY_RULE')
    print(f"POST: atoms={post_atoms} (+{post_atoms-pre_atoms}) CERT={post_cert} (expect 583 UNCHANGED) axiom={post_ax} (expect 206) cap_pres={post_mod} landed={landed} bad={bad}")
    gate = (post_cert==583 and post_ax==206 and post_mod and landed and not bad and post_atoms==pre_atoms+(0 if existed else 1))
    print("GATE:", "OK -- verify-own-routing-claim RULE atomized, CERT 583 UNCHANGED (CERT-neutral METHODOLOGY_RULE)" if gate else "FAIL")
    print(f"FOR_RECIPROCAL_CHECK: --expect-cert {post_cert} --expect-atoms {post_atoms}")
    return 0 if gate else 2


if __name__ == '__main__':
    raise SystemExit(main())
