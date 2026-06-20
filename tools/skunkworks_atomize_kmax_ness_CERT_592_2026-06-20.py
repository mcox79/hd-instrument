"""Skunkworks 2026-06-20 -- atomize K_max NESS as CERT_CHAIN_GRADE: CERT 591 -> 592 (the session's FIRST chain-grade
increment). Single-writer window. Values VERIFIED off the corrected remote data (my independent recompute matched the
cell's HARD_PASS + all gate conditions + all skeptic checks).

1 atom: T3/EXP_kmax_ness_envelope_corrected_v1 (EXPERIMENT_RECORD, pq=CERT_CHAIN_GRADE).
A5 gates: PRE CERT=591 -> POST CERT=592 (+1, the bump); axiom 206 UNCHANGED (algebra=None -> not axiom-counted);
cap_pres 6/6; +1 atom; Store-loads. ASCII. Idempotent skip-if-exists.
Pre-atomize satisfied: prereg doc-fix 284a02c3 (corrected discriminator + ext-check), corrected cell a2fdafc9, docfix f2ac8473.
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
               if str(a.corpus.name) == 'MATH' and str(a.tier.name) in ('TIER_2_PRIMITIVE', 'TIER_3_ALGORITHM')
               and a.algebra and len(a.algebra) >= 3 and 'oeis' not in str(a.id).lower()
               and not str(a.id).startswith('T3/wikidata_'))


def modlive():
    import importlib
    return all(hasattr(importlib.import_module(m), s) for m, s in [
        ('backend.substrate_index.hmm_decoder', 'viterbi_decode'),
        ('hdlab.perceptron', 'StructuredPerceptron'),
        ('backend.substrate_index.sequence_labeler', 'NERTagger'),
        ('hdlab.bayesian_inference', 'EMMixture'),
        ('backend.substrate_index.intent_classifier', 'IntentClassifier'),
        ('backend.substrate_index.refuse_gated_retriever', 'RefuseGatedRetriever'),
    ])


KMAX = Atom(
    id='T3/EXP_kmax_ness_envelope_corrected_v1',
    name=('Experiment record (CERT_CHAIN_GRADE, CERT 592): substrate NESS write-decay chain-recall depth GENUINELY '
          'exceeds the INDEPENDENT classical-Hopfield equilibrium ceiling 2x+ across the moderate regime (cand2 2.1-12.3x '
          'on 5/5; artifact-free control 1.27-8.35x on 5/5; cleanup genuinely TRAVERSES [ext_hopfrac ~1.0], NOT '
          'jump-to-a_K recovery) -- verified off data, seed-robust, non-circular baseline'),
    description=(
        'Substrate NESS (non-equilibrium steady-state, write-decay W = (1-alpha)*W + outer(a_{i+1},a_i)) chain-recall '
        'DEPTH K_obs vs the INDEPENDENT classical-Hopfield equilibrium ceiling K_eq = 3.3*(1-alpha/alpha_c)^2/alpha '
        '(alpha_c=0.138, parameter-free Hopfield theory constant [Amit-Gutfreund-Sompolinsky 1985 / Crisanti-Sompolinsky '
        '1988 / HKP], NON-CIRCULAR -- not substrate-fitted). MEASURED in the MODERATE discriminating regime alpha in '
        '[0.30,0.70]*alpha_c where K_eq is BOUNDED [3,39] (Skunkworks COMPLETE divide-by-near-zero guard: avoids BOTH '
        'alpha->0 K_eq->inf [unfair fail] AND alpha->alpha_c K_eq->0 [trivial pass]); K-grid to 120 so K_obs is MEASURED '
        '(not grid-capped). RESULT (N=8192, 5 alpha_fracs, 3 seeds): the substrate genuinely reasons DEEPER than the '
        'equilibrium ceiling -- the "formula pessimistic, substrate deeper" premise CONFIRMED genuinely, exceedance '
        'GROWING with decay (more non-equilibrium -> more NESS advantage). GENUINE on TWO independent grounds: (a) the '
        'ARTIFACT-FREE control arm (cleanup-OFF, NO codebook snap -> CANNOT be a cleanup-recovery artifact) alone exceeds '
        'K_eq on 5/5 (1.27-8.35x); (b) ext_hopfrac ~1.0 on all 5 -> the cleanup-augmentation genuinely snaps to the '
        'CORRECT next chain-node every hop (denoise-and-traverse), DEFINITIVELY NOT jump-to-a_K recovery. cand2 '
        '(cleanup-ON operational depth) exceeds K_eq >=2x on 5/5 (2.1-12.3x). VERIFIED OFF DATA by the cert-owner '
        '(independent recompute matched the cell HARD_PASS + all gate conditions); ALL skeptic checks pass: ext_hopfrac '
        'NOT by-construction (varies to 0.961 -> wrong-snaps lower it); seed-robust (per-seed CV of cand2/K_eq < 0.03); '
        'two-arm-independent (control floor holds without cleanup); UP-GUARD (cand2>=2x on 4/5 even excluding the af=0.70 '
        'small-K_eq point -> not riding a near-zero denominator); non-circular Hopfield baseline. The NESS predictive '
        'ALGEBRA (fitted eta/f_c/tau) stays a SEPARATE T3-conjecture (NOT this cert -- this is the EMPIRICAL envelope '
        'vs the independent equilibrium baseline).'),
    kind=AtomKind.EXPERIMENT_RECORD, tier=Tier.TIER_3_ALGORITHM, corpus=Corpus.MATH, algebra=None,
    metadata={
        'provenance_quality': 'CERT_CHAIN_GRADE',
        'relevance_tier': 'HIGH',
        'verdict': 'HARD_PASS_chain_grade_substrate_NESS_genuinely_exceeds_Hopfield_equilibrium',
        'run_mode': 'full',
        'n_alpha_fracs': 5, 'n_seeds': 3, 'N': 8192, 'K_grid_max': 120,
        'alpha_fracs_x_alpha_c': [0.30, 0.40, 0.50, 0.60, 0.70],
        'metrics_path': 'data/exp_kmax_ness_envelope_corrected_v1/metrics.json',
        'metrics_source': 'measured_gpu_kmax_ness_chain_recall_depth_vs_independent_hopfield_equilibrium',
        'key_metrics': {
            'K_eq_per_af': {'0.30': 39.06, '0.40': 21.52, '0.50': 11.96, '0.60': 6.38, '0.70': 3.07},
            'control_ratio_per_af': {'0.30': 1.27, '0.40': 1.74, '0.50': 2.44, '0.60': 4.07, '0.70': 8.35},
            'cand2_ratio_per_af': {'0.30': 2.12, '0.40': 2.91, '0.50': 4.21, '0.60': 6.17, '0.70': 12.27},
            'ext_hopfrac_per_af': {'0.30': 1.00, '0.40': 1.00, '0.50': 1.00, '0.60': 1.00, '0.70': 0.987},
            'control_exceeds_Keq': '5/5', 'cand2_ge_2x': '5/5', 'control_ge_2x': '3/5',
            'all_extension_genuine': True, 'mean_control_ratio': 3.57, 'mean_cand2_ratio': 5.54,
            'seed_cv_cand2_ratio_max': 0.026, 'K_eq_bounded_range': [3.07, 39.06], 'K_obs_grid_capped': False,
        },
        'honest_scope': ('Substrate NESS chain-recall depth GENUINELY exceeds the independent classical-Hopfield '
                         'equilibrium ceiling in the moderate regime (alpha in [0.3,0.7]*alpha_c, K_eq bounded [3,39]). '
                         'Genuine on the ARTIFACT-FREE control arm (5/5 > K_eq) AND ext_hopfrac~1.0 (cleanup traverses, '
                         'not recovers). NOT a claim about alpha outside the moderate regime; the NESS predictive algebra '
                         '(fitted eta/f_c/tau) is a separate T3-conjecture.'),
        'finding': ('The substrate NESS write-decay dynamics push retrievable chain-recall depth 2-12x ABOVE the static '
                    'Hopfield equilibrium ceiling, genuinely (control-arm + ext_hopfrac verified). First chain-grade '
                    'demonstration that the substrate reasons DEEPER than equilibrium theory predicts.'),
        'baseline_provenance': ('independent classical Hopfield: alpha_c=0.138 + formula (a) 3.3*(1-a/ac)^2/a from '
                                'Amit-Gutfreund-Sompolinsky 1985 / Crisanti-Sompolinsky 1988 / HKP -- parameter-free, '
                                'NOT substrate-fitted (Skunkworks cert-VET + Orchestrator substrate-mine confirmed).'),
        'composes_with': ['T3/EXP_kv_learned_projection_v1', 'T3/EXP_hebbian_capacity_projected_v2',
                          'T3/EXP_crosstalk_capacity_law_v1'],
        'depends_on_text': ('NESS write-decay dynamics (substrate); independent Hopfield equilibrium baseline (theory); '
                            'genuine-multi-hop verification (control>K_eq + ext_hopfrac) -- recorded in metadata '
                            '(phantom-safe; baseline is a theory reference, not a substrate atom).'),
        'cert_vet_status': 'LANDED_VET_skunkworks_2026-06-20_CERT_592_chain_grade_all_skeptic_checks_pass',
        'verified_off_data': ('cert-owner ssh-read remote corrected metrics + independent recompute matched the cell '
                              'HARD_PASS + all gate conditions; landed-VET tool committed 53374f39; all skeptic checks pass.'),
        'prereg': 'prereg_kmax_ness_envelope_v1 (doc-fixed 284a02c3 to the corrected discriminator + ext-check)',
        'atomized_by': 'skunkworks', 'atomized_date': '2026-06-20', 'era': 'comprehensive_program_phase3_glassbox',
        'milestone': 'session FIRST chain-grade increment 591->592 (earned via verify-the-referent; 4 inflated claims dissolved + this 1 confirmed genuine)',
    })


def main():
    ps = PartitionedStore(Path('data/substrate_index'))
    pre_cert, pre_ax, pre_mod = cert(ps), axiom(ps), modlive()
    pre_atoms = len(list(ps.all_atoms()))
    print(f"PRE: atoms={pre_atoms} CERT={pre_cert} axiom={pre_ax} cap_pres={pre_mod}")
    if not pre_mod or pre_ax != 206:
        print("PRE-GATE FAIL (axiom!=206 or cap_pres down). HALT."); return 1
    if pre_cert != 591:
        print(f"PRE-GATE WARN: CERT={pre_cert} (expected 591). Investigate before bump."); return 1
    if ps.get_atom(KMAX.qualified_id) is not None:
        print(f"  SKIP exists: {KMAX.id}")
    else:
        ps.add_atom(KMAX, source='skunkworks_kmax_ness_CERT_592_2026_06_20',
                    note='K_max NESS chain-grade: substrate genuinely exceeds Hopfield equilibrium (CERT 591->592)')
        print(f"  ADD: {KMAX.id}")
    ps2 = PartitionedStore(Path('data/substrate_index'))
    post_cert, post_ax, post_mod = cert(ps2), axiom(ps2), modlive()
    post_atoms = len(list(ps2.all_atoms()))
    landed = ps2.get_atom(KMAX.qualified_id) is not None
    bad_alg = landed and ps2.get_atom(KMAX.qualified_id).algebra is not None
    print(f"POST: atoms={post_atoms} (+{post_atoms-pre_atoms}) CERT={post_cert} (expect 592) "
          f"axiom={post_ax} (expect 206) cap_pres={post_mod} landed={landed} algebra!=None={bad_alg}")
    gate = (post_cert == 592 and post_ax == 206 and post_mod and landed and not bad_alg)
    print("GATE:", "OK -- CERT 592 (chain-grade)" if gate else "FAIL")
    print(f"FOR_RECIPROCAL_CHECK: --expect-cert {post_cert} --expect-atoms {post_atoms}")
    return 0 if gate else 2


if __name__ == '__main__':
    raise SystemExit(main())
