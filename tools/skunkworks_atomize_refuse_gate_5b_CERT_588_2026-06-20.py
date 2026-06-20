"""Skunkworks 2026-06-20 -- atomize refuse-gate #5 (b) graph-health as CERT_CHAIN_GRADE: CERT 587 -> 588.
The session's FIRST UPWARD move (post the 5MM demote-correction). 4-LAYER-WITNESS COMPLETE before landing
(my own discipline 1fcb4dcf): L1 skunkworks raw re-derivation + L2 Testbed raw-witness (both off fixed_e_raw_per_seed,
exact-match all 3 seeds) + L4 Research Director cross-check; L3 Orchestrator reciprocal post-atomize.

1 atom: T3/EXP_refuse_gate_5_graph_health_cpu_v1 (EXPERIMENT_RECORD, pq=CERT_CHAIN_GRADE).
A5: PRE CERT=587 -> POST 588 (+1); axiom 206 UNCHANGED (algebra=None); cap_pres 6/6; +1 atom; Store re-loads. ASCII. Idempotent.
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
    id='T3/EXP_refuse_gate_5_graph_health_cpu_v1',
    name=('Experiment record (CERT_CHAIN_GRADE, CERT 588): substrate SELF-DETECTS graph-adjacency overload via a GRAPH-LEVEL '
          'health signal (non-edge score variance) that reads substrate STATE (crosstalk structure) -- NOT edge-count -- and '
          'REFUSES before fabricating; per-query confidence FAILS (confidently-wrong) = the honest limit. Reads-STATE verified '
          'at equal-E (health-gap 6.2 tracks acc-gap 0.32, all 3 seeds, ~19x amplification); predicts the accuracy-cliff'),
    description=(
        'Graph-adjacency overload refuse-gate. Substrate stores graph edges in superposition; at high edge-load it is '
        'CONFIDENTLY WRONG on crosstalk false-positives, so PER-QUERY confidence does NOT self-detect overload (the LIMIT -- '
        'softmax always peaks on a winner). The WORKING refuse signal is GRAPH-LEVEL HEALTH = non-edge score VARIANCE: it reads '
        'the substrate STATE (how crowded the stored superposition is), not the input edge-count. RESULT (N=4096, V=128, 3 '
        'seeds): (1) health rises monotonically with edge-load E (0.054->0.96) and a threshold c=0.0987 separates storable '
        '(recall>=0.95) from unstorable, predicting the accuracy-cliff at E=0.15 (not just E-correlation); false-refuse '
        '(storable)=0.00 on the seed-mean, refuse(unstorable)=1.00. (2) THE CHAIN-GRADE-MAKER -- the FIXED-E test (the '
        'load-independence proof): at EQUAL E=614, two graph STRUCTURES with different storability (spread acc 0.91 vs conc '
        'acc 0.58) give a health-gap of 6.2 tracking the acc-gap of 0.32, ALL 3 SEEDS same direction, health amplifying the '
        'acc-gap ~19x -> health reads substrate STATE, NOT edge-count (load-INDEPENDENT self-detection). (3) seed-CV robust on '
        'the load-bearing REFUSE/unstorable arm (worst health-CV 0.040). 4-LAYER-WITNESS COMPLETE: L1 cert-owner raw '
        're-derivation off fixed_e_raw_per_seed + L2 Testbed independent raw re-derivation (exact-match all 3 seeds) + L4 '
        'Director cross-check; L3 Orchestrator reciprocal. A novel substrate SAFETY capability: refuse-before-confidently-wrong '
        'at the regime grain, where per-query confidence cannot.'),
    kind=AtomKind.EXPERIMENT_RECORD, tier=Tier.TIER_3_ALGORITHM, corpus=Corpus.MATH, algebra=None,
    metadata={
        'provenance_quality': 'CERT_CHAIN_GRADE',
        'relevance_tier': 'HIGH',
        'verdict': 'HARD_PASS_chain_grade_substrate_self_detects_graph_overload_reads_state_not_load',
        'run_mode': 'full', 'N': 4096, 'V': 128, 'n_seeds': 3, 'cell_commit': '61384e2f',
        'metrics_path': 'data/exp_refuse_gate_5_graph_health_cpu_v1/metrics.json',
        'metrics_source': 'measured_cpu_graph_health_refuse_signal_reads_state_fixed_e',
        'key_metrics': {
            'fixed_e_health_gap': 6.205, 'fixed_e_acc_gap': 0.325, 'fixed_e_amplification': '~19x',
            'fixed_e_all_3_seeds_same_direction': True, 'fixed_e_gap_cv_pop': 0.101,
            'refuse_arm_worst_health_cv': 0.040, 'accept_arm_worst_health_cv': 0.148, 'robust_on_refuse_arm': True,
            'health_threshold_c': 0.0987, 'accuracy_cliff_E': 0.15,
            'false_refuse_rate_storable_seedmean': 0.0, 'refuse_rate_unstorable': 1.0,
            'storable_boundary_thin': 'E0.10 clears c by 0.0002 (within accept-arm seed-noise) -> deployment threshold-margin',
        },
        'honest_scope': ('Substrate self-detects graph-adjacency overload via graph-level health (non-edge variance) reading '
                         'STATE not edge-count (fixed-E: health-gap 6.2 tracks acc-gap 0.32 at equal E, all 3 seeds, ~19x); '
                         'predicts the accuracy-cliff (E=0.15); seed-robust on the REFUSE/unstorable arm (health-CV 0.040, '
                         'the load-bearing safety direction). false-refuse=0 on the seed-MEAN; thin/per-seed-marginal at the '
                         'storable-near-cliff (E0.10 clears the threshold by 0.0002, within the accept-arm seed-noise CV 0.148) '
                         '-> robust DEPLOYMENT advises a small threshold-margin below c OR a state-relative threshold (the '
                         'SCIENCE is unaffected). PER-QUERY confidence FAILS (confidently-wrong at overload) = the honest LIMIT '
                         '-- the working signal is regime-grain. fixed_e_gap_cv is the population-stdev variant (0.101; sample-'
                         'stdev 0.123, both defensible at n=3). N=4096, V=128, 3 seeds.'),
        'finding': ('First substrate SAFETY-capability chain-grade: the substrate detects its OWN graph-overload (load-'
                    'independent, from the stored superposition state) and refuses before fabricating -- where per-query '
                    'confidence cannot (confidently-wrong). The session FIRST UPWARD chain-grade move, post the 5MM demote-'
                    'correction.'),
        'composes_with': ['T3/EXP_crosstalk_capacity_law_v1', 'T3/EXP_sparse_boundary_v2_cpu_v1',
                          'T3/EXP_kmax_ness_envelope_corrected_v1'],
        'depends_on_text': ('graph-adjacency superposition (substrate) + non-edge score variance (the health signal); the '
                            'capacity boundary it detects is a crosstalk phenomenon (T3/EXP_crosstalk_capacity_law_v1). '
                            'Recorded in metadata (phantom-safe; no sub-cert edges).'),
        'cert_vet_status': ('LANDED_VET_skunkworks_2026-06-20_CERT_588_chain_grade_4_LAYER_WITNESS_COMPLETE: '
                            'L1_skunkworks_raw_rederive + L2_testbed_raw_witness_exact_match_3seeds + L4_research_director_crosscheck; L3_orch_reciprocal'),
        'verified_off_data': ('cert-owner raw re-derivation off detail.fixed_e_raw_per_seed (health-gap 6.205, acc-gap 0.325 '
                              'reproduce exactly, all 3 seeds reads-state) + Testbed independent raw re-derivation (exact-match) '
                              '+ per_unit cliff/monotone/seed-acc 2nd-witnessed.'),
        'atomized_by': 'skunkworks', 'atomized_date': '2026-06-20', 'era': 'comprehensive_program_phase3_glassbox',
        'milestone': ('session FIRST UPWARD chain-grade 587->588 (refuse-gate safety capability; first earned PASS after the '
                      '5MM demote-correction); validates the Milestone-1 refuse-arm input. The (b)-graph-health signal call + '
                      'fixed-E discriminator requirement + 4-layer-witness-before-landing -- the discipline end-to-end.'),
    })


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
        ps.add_atom(ATOM, source='skunkworks_refuse_gate_5b_CERT_588_2026_06_20',
                    note='refuse-gate graph-health self-detection chain-grade (CERT 587->588; 4-layer-witness complete)')
        print(f"  ADD: {ATOM.id}")
    ps2 = PartitionedStore(Path('data/substrate_index'))
    post_cert, post_ax, post_mod = cert(ps2), axiom(ps2), modlive()
    post_atoms = len(list(ps2.all_atoms()))
    a2 = ps2.get_atom(ATOM.qualified_id)
    landed = a2 is not None
    bad_alg = landed and a2.algebra is not None
    print(f"POST: atoms={post_atoms} (+{post_atoms-pre_atoms}) CERT={post_cert} (expect 588) axiom={post_ax} (expect 206) cap_pres={post_mod} landed={landed} algebra!=None={bad_alg}")
    gate = (post_cert==588 and post_ax==206 and post_mod and landed and not bad_alg and post_atoms==pre_atoms+(0 if existed else 1))
    print("GATE:", "OK -- CERT 588 (refuse-gate self-detection chain-grade)" if gate else "FAIL")
    print(f"FOR_RECIPROCAL_CHECK: --expect-cert {post_cert} --expect-atoms {post_atoms}")
    return 0 if gate else 2


if __name__ == '__main__':
    raise SystemExit(main())
