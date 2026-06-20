"""Skunkworks 2026-06-20 -- atomize the SYSTEMIC lever-design discipline (CERT-NEUTRAL).
From LEVER 1.5 v2 (no-cost sparsity selector collapsed: fixed-f=0.01 never beaten) + the LEVER 2/3/4 batch VET.
METHODOLOGY_RULE / META / TIER_METHODOLOGY / algebra=None / pq=None -> CERT 587 UNCHANGED.
A5: PRE CERT=587 -> POST 587; axiom 206; cap_pres 6/6; +1 atom; Store re-loads. ASCII. Idempotent.
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
    id='RULE_selector_lever_chain_grade_requires_genuine_cost_else_collapses_to_fixed_best',
    name=('Methodology rule: a SELECTOR lever (auto-picks a config knob from measured inputs) earns chain-grade ONLY if a '
          'genuine COST/tradeoff makes the naive-best-fixed value LOSE; no cost -> "always use the best fixed value" wins '
          '-> MEASURED_MECHANISM, not chain-grade'),
    description=(
        'For any SELECTOR-type lever (a runtime flag that auto-selects a config knob -- sparsity f, dimension k, composition '
        'operator -- from measured inputs), the load-bearing chain-grade question is: WHAT MAKES THE NAIVE-BEST-FIXED VALUE '
        'LOSE? A selector is only a genuine WIN if a real COST/tradeoff makes a single fixed value fail somewhere; absent a '
        'cost, "always use the best fixed value" matches-or-beats the selector everywhere and the measurement machinery adds '
        'NOTHING -> MEASURED_MECHANISM, not chain-grade. EVIDENCE: LEVER 1.5 v2 (capacity sweet-spot, sparsity selector) -- '
        'even after fixing the selector to be genuinely adaptive AND adding a K_MIN precision cost, a fixed sparsest-f (0.01) '
        'was NEVER BEATEN (earns_keep=False; the sweet-spot was broad), because there was no cost making over-sparsity LOSE in '
        'the tested regime. COROLLARIES: (1) the naive baseline MUST be the value the selector ACTUALLY lands on (not an '
        'arbitrary value it trivially beats -- e.g. compare vs fixed-f=0.01 the selector picks, not fixed-f=0.05). (2) a '
        'predictor that is NEAR-BY-CONSTRUCTION with the target is near-CIRCULAR -- e.g. using crosstalk-moment to predict '
        'capacity when crosstalk IS capacity near-by-construction (7315be3c); verify the selector uses INDEPENDENT out-of-sample '
        'signal, measured on actual RECALL, not on a near-tautological formula. (3) the genuine COUNTER-EXAMPLE: LEVER 4 '
        '(composition selector) HAS a cost -- chaining beyond K_max FABRICATES -- so "always chain" genuinely loses '
        'out-of-envelope and the selector earns its keep (the cost is what makes it a real selection problem). RULE applies '
        'at SCHEMA-VET (ask "what makes the naive-best-fixed lose?" before cell-author) and at landed-VET (if the selector '
        'ties a fixed-best, rule MEASURED_MECHANISM not chain-grade, regardless of the headline verdict).'),
    kind=AtomKind.METHODOLOGY_RULE, tier=Tier.TIER_METHODOLOGY, corpus=Corpus.META, algebra=None,
    metadata={'extracted_by':'skunkworks','extracted_date':'2026-06-20','term_class':'methodology',
              'eleventh_rule_clean':True,'substrate_internal_verified':True,'status':'active','confidence':'high',
              'rule_class':'lever_design',
              'witnesses':['LEVER_1_5_v2_fixed_sparsest_f_0p01_never_beaten_no_cost_earns_keep_False_2026-06-20',
                           'LEVER_4_composition_HAS_cost_chain_beyond_Kmax_fabricates_genuine_selection_problem',
                           'LEVER_2_PCA_crosstalk_moment_near_circular_predictor_per_7315be3c'],
              'composes_with':['RULE_cited_number_must_reproduce_from_the_cell_else_miscite',
                               'RULE_4_layer_reciprocal_witness_for_high_stakes_ships'],
              'source':'skunkworks_session_2026-06-20_LEVER_1_5_v2_plus_2_3_4_batch_VET'})


def main():
    ps = PartitionedStore(Path('data/substrate_index'))
    pre_cert, pre_ax, pre_mod = cert(ps), axiom(ps), modlive()
    pre_atoms = len(list(ps.all_atoms()))
    print(f"PRE: atoms={pre_atoms} CERT={pre_cert} axiom={pre_ax} cap_pres={pre_mod}")
    if not pre_mod or pre_ax != 206 or pre_cert != 587:
        print(f"PRE-GATE FAIL (axiom={pre_ax}!=206 / cap_pres={pre_mod} / CERT={pre_cert}!=587). HALT."); return 1
    existed = ps.get_atom(ATOM.qualified_id) is not None
    if existed:
        print(f"  SKIP exists: {ATOM.id}")
    else:
        ps.add_atom(ATOM, source='skunkworks_lever_design_discipline_2026_06_20', note='lever-design discipline (CERT-neutral)')
        print(f"  ADD: {ATOM.id}")
    ps2 = PartitionedStore(Path('data/substrate_index'))
    post_cert, post_ax, post_mod = cert(ps2), axiom(ps2), modlive()
    post_atoms = len(list(ps2.all_atoms()))
    landed = ps2.get_atom(ATOM.qualified_id) is not None
    a2 = ps2.get_atom(ATOM.qualified_id)
    bad = a2.algebra is not None or (a2.metadata or {}).get('provenance_quality') == 'CERT_CHAIN_GRADE'
    print(f"POST: atoms={post_atoms} (+{post_atoms-pre_atoms}) CERT={post_cert} (expect 587) axiom={post_ax} (expect 206) cap_pres={post_mod} landed={landed} bad={bad}")
    gate = (post_cert==587 and post_ax==206 and post_mod and landed and not bad and post_atoms==pre_atoms+(0 if existed else 1))
    print("GATE:", "OK -- lever-design discipline atomized, CERT 587 UNCHANGED (CERT-neutral)" if gate else "FAIL")
    print(f"FOR_RECIPROCAL_CHECK: --expect-cert {post_cert} --expect-atoms {post_atoms}")
    return 0 if gate else 2


if __name__ == '__main__':
    raise SystemExit(main())
