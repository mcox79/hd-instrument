"""Skunkworks 2026-06-21 -- atomize the 2-axis refuse-gate composition: MM experiment-record + the composition DISCIPLINE.
Both CERT-NEUTRAL. VET-off-DATA PASS: independent recompute from per_unit matched ALL cited numbers EXACTLY
(joint_vs_load_only +0.061 / joint_vs_depth_only -0.098 / joint_vs_always -0.037; per-seed overloaded joint
0.277/0.278/0.277, depth 0.493/0.475/0.454, load 0.156/0.155/0.152; robust_beats_depth=False; run_mode=full 6 units).
2 witnesses (Exp-Dev produced+reproduced + Skunkworks independent recompute) -> 2-layer (MM/CERT-neutral, non-destination).
A5: PRE CERT=588 -> POST 588 (+2 atoms -> 177255); axiom 206; cap_pres 6/6; reloads. ASCII. Idempotent.
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


MM = Atom(
    id='T3/EXP_twoaxis_refuse_gate_compose_v1_cpu_v1',
    name=('Experiment record (MEASURED_MECHANISM): naive 2-axis refuse-gate composition (#5b adjacency-load OR #4 '
          'depth) LOSES to depth-only -- the #5b SAFETY gate over-refuses net-positive adjacency under a UTILITY metric'),
    description=(
        'Composes refuse-gate #5b (load-axis: refuse adjacency at acc<0.95, a SAFETY threshold) with LEVER #4 (depth-axis: '
        'refuse traversal that would fabricate, a UTILITY threshold) by naive OR, on a mixed adjacency+traversal workload '
        'under a risk-utility metric (correct +1 / fabricate -1 / refuse 0). FULL 3-seed, 2 loads (0.05, 1.0). RESULT '
        '(verified off per_unit, independent recompute matched EXACTLY): joint vs load_only=+0.061 (joint > load-only: the '
        'depth-gate IS necessary -- load-only is depth-blind + fabricates deep traversal), but joint vs depth_only=-0.098 '
        '(joint LOSES to depth-only) and joint vs always-answer=-0.037 (joint even loses to always-answer). At the overloaded '
        'load (per-seed, cv~0): depth_only 0.47 > always 0.35 > joint 0.28 > load_only 0.155. MECHANISM: adjacency-binding is '
        'ROBUST (adj net-positive even at acc<0.95), so #5b\'s SAFETY-refuse (acc<0.95) OVER-refuses net-positive adjacency '
        'under the UTILITY metric -> drags joint below depth-only. NOT chain-grade (composition does not beat the best single '
        'component = depth-only -> lever-design discipline 99392cca -> MEASURED_MECHANISM). The bankable value is the '
        'composition discipline (see RULE_compose_safety_and_utility_refuse_gates_needs_unified_cost_model).'),
    kind=AtomKind.EXPERIMENT_RECORD, tier=Tier.TIER_3_ALGORITHM, corpus=Corpus.MATH, algebra=None,
    metadata={'provenance_quality':'MEASURED_MECHANISM','relevance_tier':'MEDIUM','run_mode':'full','verdict':'MEASURED_MECHANISM',
              'metrics_path':'data/exp_twoaxis_refuse_gate_compose_v1_cpu_v1/metrics.json',
              'key_metrics':{'joint_vs_load_only':0.061,'joint_vs_depth_only':-0.098,'joint_vs_always':-0.037,
                             'robust_beats_load_only':False,'robust_beats_depth_only':False,'n_seeds':3,'loads':[0.05,1.0],
                             'overloaded_per_seed_joint':[0.277,0.278,0.277],'overloaded_per_seed_depth_only':[0.493,0.475,0.454],
                             'overloaded_per_seed_load_only':[0.156,0.155,0.152]},
              'honest_scope':('Naive 2-axis refuse-gate OR (#5b load + #4 depth) loses to depth-only because the #5b SAFETY '
                              'threshold (acc<0.95) over-refuses net-positive adjacency under the UTILITY metric. Depth-gate '
                              'alone suffices for THIS substrate (adjacency robust). A genuine 2-axis chain-grade needs a '
                              'UNIFIED cost model (align both gates to one refuse-philosophy) OR a substrate where BOTH '
                              'operations go net-negative. MEASURED_MECHANISM (not chain-grade; data-decided off full 3-seed).'),
              'composes_with':['T3/EXP_refuse_gate_5_graph_health_cpu_v1','T3/EXP_multiplicative_composition_lever_v1_cpu_v1',
                               'RULE_compose_safety_and_utility_refuse_gates_needs_unified_cost_model',
                               'RULE_selector_lever_chain_grade_requires_genuine_cost_else_collapses_to_fixed_best'],
              'verified_off_data':('skunkworks independent recompute from per_unit util_* matched ALL cited numbers EXACTLY '
                                   '(+0.061/-0.098/-0.037; per-seed overloaded joint 0.277/0.278/0.277 etc); 2-layer witness '
                                   '(Exp-Dev produced+reproduced + Skunkworks recompute); smoke-mislabel caught + corrected to full first.'),
              'cert_vet_status':'landed_VET_skunkworks_2026-06-21_MEASURED_MECHANISM_verified_off_data',
              'atomized_by':'skunkworks','atomized_date':'2026-06-21','era':'comprehensive_program_phase3_glassbox'})

RULE = Atom(
    id='RULE_compose_safety_and_utility_refuse_gates_needs_unified_cost_model',
    name=('Methodology rule: composing a SAFETY-calibrated refuse-gate with a UTILITY-calibrated refuse-gate under ONE '
          'utility metric requires a UNIFIED cost model -- naive OR makes the safety-gate over-refuse -> the composition '
          'loses to the better single gate'),
    description=(
        'A SAFETY refuse-gate (refuse when a conservative quality threshold is missed, e.g. #5b adjacency acc<0.95) and a '
        'UTILITY refuse-gate (refuse when answering is net-negative, e.g. #4 depth-fabrication) embody DIFFERENT refuse '
        'philosophies. OR-ing them under a single UTILITY metric makes the SAFETY gate look over-cautious: it refuses '
        'cases that are net-POSITIVE under the utility metric (conservative safety threshold > utility break-even), dragging '
        'the joint below the better single gate. EVIDENCE (2-axis compose, full 3-seed, verified off-data): joint vs '
        'depth-only = -0.098 (joint LOSES); the #5b safety-refuse (acc<0.95) over-refused net-positive adjacency (robust: '
        'net-positive even at acc<0.95) -> joint < depth-only < even always-answer. RULE: to compose heterogeneous '
        'refuse-gates, either (a) align both to ONE refuse-threshold philosophy (a unified cost model where each gate\'s '
        'refuse-point = the same utility break-even), or (b) weight the fabrication-cost to match the safety-gate\'s '
        'conservatism. Do NOT naive-OR a safety gate and a utility gate under one utility metric. (Corollary of the '
        'lever-design discipline 99392cca: a composition earns chain-grade only if it beats the best single component.)'),
    kind=AtomKind.METHODOLOGY_RULE, tier=Tier.TIER_METHODOLOGY, corpus=Corpus.META, algebra=None,
    metadata={'extracted_by':'skunkworks','extracted_date':'2026-06-21','term_class':'methodology','eleventh_rule_clean':True,
              'substrate_internal_verified':True,'status':'active','confidence':'high','rule_class':'composition_design',
              'witnesses':['twoaxis_refuse_gate_compose_joint_loses_to_depth_only_safety_overrefuses_utility_2026-06-21'],
              'composes_with':['RULE_selector_lever_chain_grade_requires_genuine_cost_else_collapses_to_fixed_best',
                               'T3/EXP_twoaxis_refuse_gate_compose_v1_cpu_v1'],
              'source':'skunkworks_session_2026-06-21_2axis_refuse_gate_compose_MM'})

ATOMS = [MM, RULE]


def main():
    ps = PartitionedStore(Path('data/substrate_index'))
    pre_cert, pre_ax, pre_mod = cert(ps), axiom(ps), modlive()
    pre_atoms = len(list(ps.all_atoms()))
    print(f"PRE: atoms={pre_atoms} CERT={pre_cert} axiom={pre_ax} cap_pres={pre_mod}")
    if not pre_mod or pre_ax != 206 or pre_cert != 588:
        print(f"PRE-GATE FAIL (axiom={pre_ax}!=206 / cap_pres={pre_mod} / CERT={pre_cert}!=588). HALT."); return 1
    added = 0
    for at in ATOMS:
        if ps.get_atom(at.qualified_id) is not None:
            print(f"  SKIP exists: {at.id}")
        else:
            ps.add_atom(at, source='skunkworks_2axis_compose_MM_plus_discipline_2026_06_21',
                        note='2-axis refuse-gate compose MM + composition discipline (CERT-neutral, verified off-data)')
            print(f"  ADD: {at.id}"); added += 1
    ps2 = PartitionedStore(Path('data/substrate_index'))
    post_cert, post_ax, post_mod = cert(ps2), axiom(ps2), modlive()
    post_atoms = len(list(ps2.all_atoms()))
    landed = all(ps2.get_atom(at.qualified_id) is not None for at in ATOMS)
    bad = any((ps2.get_atom(at.qualified_id).algebra is not None) or
              ((ps2.get_atom(at.qualified_id).metadata or {}).get('provenance_quality')=='CERT_CHAIN_GRADE') for at in ATOMS)
    print(f"POST: atoms={post_atoms} (+{post_atoms-pre_atoms}) CERT={post_cert} (expect 588) axiom={post_ax} (expect 206) cap_pres={post_mod} landed={landed} bad={bad}")
    gate = (post_cert==588 and post_ax==206 and post_mod and landed and not bad and post_atoms==pre_atoms+added)
    print("GATE:", "OK -- 2-axis MM + composition discipline atomized, CERT 588 UNCHANGED (CERT-neutral)" if gate else "FAIL")
    print(f"FOR_RECIPROCAL_CHECK: --expect-cert {post_cert} --expect-atoms {post_atoms}")
    return 0 if gate else 2


if __name__ == '__main__':
    raise SystemExit(main())
