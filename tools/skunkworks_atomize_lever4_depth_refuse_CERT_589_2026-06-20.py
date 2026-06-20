"""Skunkworks 2026-06-20 -- atomize LEVER #4 (multiplicative-composition / depth-axis refuse-gate) CERT_CHAIN_GRADE: 588 -> 589.
2nd safety-capability chain-grade; composes with refuse-gate #5b (CERT 588, load-axis) -> 2-axis OOE refusal.
4-LAYER-WITNESS COMPLETE: L1 skunkworks (off detail.per_load) + L2 Testbed raw (off per_unit rows, per-seed margins
re-derived) + L4 Research Director cross-check; L3 Orchestrator reciprocal post-atomize.

1 atom: T3/EXP_multiplicative_composition_lever_v1_cpu_v1. A5: PRE CERT=588 -> POST 589 (+1); axiom 206; cap_pres 6/6;
+1 atom; Store re-loads. ASCII. Idempotent.
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
    id='T3/EXP_multiplicative_composition_lever_v1_cpu_v1',
    name=('Experiment record (CERT_CHAIN_GRADE, CERT 589): DEPTH-AXIS refuse-gate -- the substrate REFUSES chains deeper '
          'than the (empirically-calibrated) K_max(load) where chaining would FABRICATE a confident-wrong node; ROBUSTLY '
          'beats always-chain where fabrication is significant (always-chain utility goes NEGATIVE at high load), NEVER-worse '
          'elsewhere, non-circular calibrate/test. Composes with refuse-gate #5b -> 2-axis OOE refusal (load + depth)'),
    description=(
        'Composition-operator selector: chain for depth-K queries where K <= calibrated K_max(load), refuse/truncate when K > '
        'K_max (where per-hop raw-sign iteration accumulates errors and the final cleanup snaps to a WRONG codebook node = '
        'confident-wrong FABRICATION). GENUINE selection COST (passes the lever-design discipline that LEVER 1.5/2/3 failed): '
        'out-of-envelope chains genuinely fabricate -- ooe_chain_acc 0.348/0.090/0.027 at loads 0.6/1.0/1.5 (mostly-wrong; '
        '0.03 at high load = catastrophic confident-wrong) -- so always-chain UTILITY (risk-metric: correct +1 / fabricate -1 '
        '/ refuse 0) goes +0.71 -> +0.07 -> NEGATIVE -0.15 as load rises; the selector stays positive (+0.77/+0.47/+0.37) by '
        'REFUSING when fabrication-risk is high. NON-CIRCULAR (the LEVER 1.5 lesson): K_max calibrated on cal-seeds {101,102}, '
        'TESTED on disjoint held-out seeds {1,2,3}. RESULT (N=2048): per-seed-ROBUST beat at the high-fabrication loads '
        '[1.0,1.5] (per-seed margins {0.468,0.353,0.361} and {0.529,0.531,0.518}, all >> seed-noise); NEVER-worse on ALL loads '
        '(all 9 per-seed margins >= 0; the gate only refuses where chain fabricates -> cannot lose); beats always-flat on ALL '
        '(chain adds genuine depth value for K>=2); seed-stable. VERIFIED 4-layer (L1 cert-owner off per_load + L2 Testbed raw '
        're-derivation off per_unit per-seed rows + L4 Director). The PREMISE (refuse-gate-shared with #5b): the win rests on '
        'confident-wrong being harmful (-1); load 0.6 is marginal-but-never-worse (high K_max -> little fabrication to avoid). '
        'A 2nd substrate SAFETY capability (depth-axis); composes with refuse-gate #5b (load-axis) for 2-axis OOE refusal.'),
    kind=AtomKind.EXPERIMENT_RECORD, tier=Tier.TIER_3_ALGORITHM, corpus=Corpus.MATH, algebra=None,
    metadata={
        'provenance_quality': 'CERT_CHAIN_GRADE',
        'relevance_tier': 'HIGH',
        'verdict': 'HARD_PASS_chain_grade_depth_axis_refuse_gate_robust_at_high_fabrication_loads',
        'run_mode': 'full', 'N': 2048, 'cell_commit': '232a679c',
        'cal_seeds': [101, 102], 'test_seeds': [1, 2, 3],
        'metrics_path': 'data/exp_multiplicative_composition_lever_v1_cpu_v1/metrics.json',
        'metrics_source': 'measured_cpu_depth_axis_refuse_gate_chain_vs_kmax_held_out',
        'key_metrics': {
            'kmax_by_load': {'0.6': 6, '1.0': 4, '1.5': 4},
            'per_seed_margin_vs_chain': {'0.6': [0.150, 0.003, 0.015], '1.0': [0.468, 0.353, 0.361], '1.5': [0.529, 0.531, 0.518]},
            'U_always_chain_by_load': {'0.6': 0.715, '1.0': 0.071, '1.5': -0.152},
            'U_selector_by_load': {'0.6': 0.771, '1.0': 0.466, '1.5': 0.374},
            'ooe_chain_acc_by_load': {'0.6': 0.348, '1.0': 0.090, '1.5': 0.027},
            'loads_ROBUST_beat_chain': [1.0, 1.5], 'loads_marginal_never_worse': [0.6],
            'never_worse_than_chain_all_loads': True, 'beats_flat_all_loads': True, 'seed_stable': True,
        },
        'honest_scope': ('Depth-axis refuse-gate: ROBUST beat over always-chain ONLY at high-fabrication loads [1.0,1.5] '
                         '(where always-chain utility goes NEGATIVE); marginal-but-NEVER-worse at low-fab load 0.6 (high K_max '
                         '-> little fabrication to avoid). PREMISE: the win rests on confident-wrong fabrication being harmful '
                         '(-1); if fabrication were costless, refuse(0) would not beat fabricate -- the refuse-gate premise '
                         '(shared with #5b). K_max is INDEPENDENTLY EMPIRICALLY CALIBRATED here (cal {101,102} / test {1,2,3}), '
                         'NOT consuming CERT 592 K_max -- same PHENOMENON (chain-depth limit), independent calibration. '
                         'Non-circular. N=2048, 3 test seeds.'),
        'finding': ('2nd substrate SAFETY-capability chain-grade: depth-axis OOE refusal (refuse chains that would fabricate '
                    'beyond K_max). Composes with refuse-gate #5b (load-axis) -> the substrate refuses BOTH too-many-edges '
                    '(load) AND too-deep-to-chain (depth) before fabricating.'),
        'composes_with': ['T3/EXP_refuse_gate_5_graph_health_cpu_v1', 'T3/EXP_kmax_ness_envelope_corrected_v1'],
        'depends_on_text': ('per-hop raw-sign chain iteration (substrate) + empirically-calibrated K_max(load) refuse threshold; '
                            'same chain-depth phenomenon as CERT 592 (independently calibrated, NOT consumed); composes with '
                            'refuse-gate #5b load-axis. Recorded in metadata (phantom-safe).'),
        'cert_vet_status': ('LANDED_VET_skunkworks_2026-06-20_CERT_589_chain_grade_4_LAYER_WITNESS_COMPLETE: '
                            'L1_skunkworks_per_load + L2_testbed_raw_per_unit_perseed_margins + L4_research_director; L3_orch_reciprocal'),
        'verified_off_data': ('cert-owner Layer-1 off detail.per_load (robust[1.0,1.5]/never-worse/fabrication/beats-flat/seed-'
                              'stable reproduce) + Testbed Layer-2 independent per-seed margin re-derivation off per_unit rows '
                              '(all 9 margins >=0; always-chain negative at 1.5 confirmed).'),
        'atomized_by': 'skunkworks', 'atomized_date': '2026-06-20', 'era': 'comprehensive_program_phase3_glassbox',
        'milestone': ('2nd safety-capability chain-grade (depth-axis refuse-gate); composes with #5b (load-axis) -> 2-axis OOE '
                      'refusal. Passes the lever-design discipline (genuine fabrication cost -> real selection problem, unlike '
                      'LEVER 1.5/2/3). Exp-Dev self-caught the mean-beat overcount via per-seed-robust -- the verify-the-referent '
                      'lesson propagating to the prover.'),
    })


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
        ps.add_atom(ATOM, source='skunkworks_lever4_depth_refuse_CERT_589_2026_06_20',
                    note='depth-axis refuse-gate chain-grade (CERT 588->589; 4-layer-witness complete; composes #5b)')
        print(f"  ADD: {ATOM.id}")
    ps2 = PartitionedStore(Path('data/substrate_index'))
    post_cert, post_ax, post_mod = cert(ps2), axiom(ps2), modlive()
    post_atoms = len(list(ps2.all_atoms()))
    a2 = ps2.get_atom(ATOM.qualified_id); landed = a2 is not None; bad_alg = landed and a2.algebra is not None
    print(f"POST: atoms={post_atoms} (+{post_atoms-pre_atoms}) CERT={post_cert} (expect 589) axiom={post_ax} (expect 206) cap_pres={post_mod} landed={landed} algebra!=None={bad_alg}")
    gate = (post_cert==589 and post_ax==206 and post_mod and landed and not bad_alg and post_atoms==pre_atoms+(0 if existed else 1))
    print("GATE:", "OK -- CERT 589 (depth-axis refuse-gate chain-grade)" if gate else "FAIL")
    print(f"FOR_RECIPROCAL_CHECK: --expect-cert {post_cert} --expect-atoms {post_atoms}")
    return 0 if gate else 2


if __name__ == '__main__':
    raise SystemExit(main())
