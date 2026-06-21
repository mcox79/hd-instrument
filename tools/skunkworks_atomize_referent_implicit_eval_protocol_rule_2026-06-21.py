"""Skunkworks 2026-06-21 -- atomize a new cert-VET METHODOLOGY_RULE (CERT-NEUTRAL, pq=None):
A METRIC REFERENT CARRIES AN IMPLICIT EVAL PROTOCOL -- MATCH IT TO REPRODUCE (model+precision is necessary-NOT-sufficient).
Emerged from the dense-KV follow-up GATE-1 FALSE HALT: GATE-1 tried to reproduce CERT591's recall@1=0.827 referent but did a
10000-way retrieval vs CERT591's 2500-way (HELDOUT_FRAC 0.25) + trained on 4000 vs 7500 -> cal=0.411 -> HALT-by-design fired,
which (without this rule) reads as "meter invalid / substrate fails". Root cause = the 0.827 referent is candidate-set-size-
AND train-size-DEPENDENT; we matched model (pythia-2.8b) + precision (fp16) but NOT the eval protocol. recall@k / accuracy@N /
any rank- or candidate-count-dependent metric is only reproducible when the EVAL PROTOCOL matches (N candidates in the argmax,
train/held-out split, sampling). 0.411 was >> chance (1/10000) -> the mechanism worked; the comparison was mis-specified.
Research-endorsed (Director META insight). Composes with cited-number-must-reproduce + verify-the-referent.
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
    id='RULE_metric_referent_carries_implicit_eval_protocol_match_it_to_reproduce',
    name=('Methodology rule (cert-VET): a METRIC REFERENT (recall@k / accuracy@N / any rank- or candidate-count-'
          'dependent number) carries an IMPLICIT EVAL PROTOCOL -- to reproduce it you must match that protocol '
          '(# candidates in the argmax, train/held-out split, sampling), NOT just the model + precision + data-source. '
          'A reproduce-attempt that mismatches the protocol gives a FALSE miss (looks like a meter/capability failure '
          'when the mechanism is fine)'),
    description=(
        'Metric-referent-carries-an-implicit-eval-protocol. When a NEW cell tries to reproduce a known metric referent '
        '(e.g. a calibration HALT-gate "reproduce CERT591 recall@1=0.827, else HALT"), matching the model + numeric '
        'precision + data-source is NECESSARY-BUT-NOT-SUFFICIENT. Metrics like recall@1, recall@k, accuracy@N, MRR, and '
        'any retrieval/ranking score are FUNCTIONS OF THE EVAL PROTOCOL: the number of candidates in the argmax (a '
        '10000-way retrieval is far harder than a 2500-way one for the SAME embeddings), the train/held-out split sizes '
        '(less training -> weaker projection -> lower recall), the sampling, the chance baseline. To reproduce the '
        'referent you MUST replicate its eval protocol, not just its model. ACTION: before using a metric number as a '
        'reproduce-target/HALT-gate, extract its FULL eval protocol from the producing cell (candidate-set size = '
        'held-out N, train size, split frac, sampling) and match it; if a reproduce-attempt misses, FIRST check the '
        'protocol delta (and whether the miss is still >> chance, indicating the mechanism works) BEFORE concluding the '
        'meter/capability failed. PROVENANCE: dense-KV follow-up GATE-1 false HALT (2026-06-21) -- GATE-1 did a 10000-way '
        'retrieval + train=4000 against CERT591\'s 0.827 referent (which was 2500-way [HELDOUT_FRAC 0.25] + train=7500) -> '
        'cal=0.411 -> HALT-by-design fired; without this rule it reads as "meter invalid / substrate M-indep store fails", '
        'but 0.411 >> chance (1/10000=0.0001) -> the projection + meter WORK; it was a protocol mismatch. The HALT-gate '
        'design (refuse to interpret on non-reproduction) was GOOD (inflation-backstop); the FIX is to match the protocol, '
        'not to demote. CERT-NEUTRAL META rule (pq=None); Research-endorsed. Composes with cited-number-must-reproduce '
        '(this is its dual: when REPRODUCING a referent, match its eval protocol) + verify-the-referent.'),
    kind=AtomKind.METHODOLOGY_RULE, tier=Tier.TIER_METHODOLOGY, corpus=Corpus.META, algebra=None,
    metadata={'confidence':'high','eleventh_rule_clean':True,'extracted_by':'skunkworks','extracted_date':'2026-06-21',
              'rule_class':'cert_vet','status':'ADOPTED','substrate_internal_verified':True,
              'term_class':'PROCESS_KNOWLEDGE_NON_MATH','research_endorsed':True,
              'source':'metric_referent_implicit_eval_protocol_dense_KV_followup_GATE1_false_halt_skunkworks_2026_06_21',
              'witnesses':['dense-KV follow-up GATE-1 false HALT 2026-06-21: cal=0.411 vs CERT591 0.827 = 10000-way vs '
                           '2500-way retrieval (HELDOUT_FRAC 0.25) + train 4000 vs 7500; 0.411>>chance(1e-4) -> mechanism '
                           'works, protocol mismatch; matched model+fp16 but not eval protocol'],
              'composes_with':['RULE_cited_number_must_reproduce_from_the_cell_else_miscite',
                               'RULE_verify_referent_arrives_applies_to_data_paths_not_just_atoms',
                               'RULE_info_theoretic_floor_check_before_M_independence_claim']})


def main():
    ps = PartitionedStore(Path('data/substrate_index'))
    pre_cert, pre_ax, pre_mod = cert(ps), axiom(ps), modlive(); pre_atoms = len(list(ps.all_atoms()))
    print(f"PRE: atoms={pre_atoms} CERT={pre_cert} axiom={pre_ax} cap_pres={pre_mod}")
    if not pre_mod or pre_ax != 206 or pre_cert != 583:
        print(f"PRE-GATE FAIL (axiom={pre_ax}!=206 / cap_pres={pre_mod} / CERT={pre_cert}!=583). HALT."); return 1
    existed = ps.get_atom(ATOM.qualified_id) is not None
    if existed: print(f"  SKIP exists: {ATOM.id}")
    else:
        ps.add_atom(ATOM, source='skunkworks_metric_referent_implicit_eval_protocol_rule_2026_06_21', note='cert-VET METHODOLOGY_RULE (CERT-neutral, pq=None); metric referent carries implicit eval protocol -- match it to reproduce')
        print(f"  ADD: {ATOM.id}")
    ps2 = PartitionedStore(Path('data/substrate_index'))
    post_cert, post_ax, post_mod = cert(ps2), axiom(ps2), modlive(); post_atoms = len(list(ps2.all_atoms()))
    a2 = ps2.get_atom(ATOM.qualified_id); landed = a2 is not None
    bad = landed and ((a2.algebra is not None) or (a2.metadata or {}).get('provenance_quality')=='CERT_CHAIN_GRADE'
                      or str(a2.kind.name)!='METHODOLOGY_RULE')
    print(f"POST: atoms={post_atoms} (+{post_atoms-pre_atoms}) CERT={post_cert} (expect 583 UNCHANGED) axiom={post_ax} (expect 206) cap_pres={post_mod} landed={landed} bad={bad}")
    gate = (post_cert==583 and post_ax==206 and post_mod and landed and not bad and post_atoms==pre_atoms+(0 if existed else 1))
    print("GATE:", "OK -- eval-protocol-referent RULE atomized, CERT 583 UNCHANGED (CERT-neutral METHODOLOGY_RULE)" if gate else "FAIL")
    print(f"FOR_RECIPROCAL_CHECK: --expect-cert {post_cert} --expect-atoms {post_atoms}")
    return 0 if gate else 2


if __name__ == '__main__':
    raise SystemExit(main())
