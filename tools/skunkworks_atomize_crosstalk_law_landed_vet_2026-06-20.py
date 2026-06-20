"""Skunkworks 2026-06-20 -- atomize the crosstalk-law (reframed isotropy #6) LANDED-VET = MEASURED_MECHANISM.
Single-writer window. Values VERIFIED OFF DATA (my independent recompute off the remote full per_unit matched the
cell exactly: Pearson 0.976 / Spearman 0.964 / d_eff -0.212 / IsoScore 0.304 / partials -0.349/-0.499 / c-spread 5.045).

Batch (2 atoms, one window):
  1. T3/EXP_crosstalk_capacity_law_v1 (EXPERIMENT_RECORD, pq=MEASURED_MECHANISM) -- the result. CERT stays 591.
  2. RULE_controls_fail_claim_needs_partial_correlation_not_just_dominance (METHODOLOGY) -- the arc's discipline.

A5-safe: PRE snapshot -> idempotent add (skip-if-exists) -> POST verify. Expect CERT 591 UNCHANGED, axiom 206, cap_pres 6/6,
+2 atoms, no algebra. ASCII only.
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


_COMMON = {'extracted_by': 'skunkworks', 'extracted_date': '2026-06-20', 'term_class': 'PROCESS_KNOWLEDGE_NON_MATH',
           'eleventh_rule_clean': True, 'substrate_internal_verified': True, 'status': 'ADOPTED', 'confidence': 'high'}


RESULT = Atom(
    id='T3/EXP_crosstalk_capacity_law_v1',
    name=('Experiment record (MEASURED_MECHANISM): the direct crosstalk moment E[<ki,kj>^2] on RAW keys is the DOMINANT + '
          'ROBUST cross-encoder predictor of Hebbian-superposition capacity (Pearson 0.976 / Spearman 0.964, n=11 encoders '
          'incl pythia-2.8b); SVD d_eff + IsoScore far weaker; c unbounded (5.04x) -> not a parameter-free LAW. Reframes + '
          'supersedes the isotropy #6 hypothesis (overturned: an independent isotropy measure does NOT predict capacity)'),
    description=(
        'REFRAME of isotropy #6. The hypothesis "embedding isotropy predicts Hebbian capacity" was tested with an '
        'INDEPENDENT IsoScore (mean-centered covariance-eigenvalue, the non-circular predictor per Skunkworks pre-flag-B); '
        'IsoScore is FLAT + does NOT predict capacity -> the prediction VANISHES with a genuinely-independent measure -> '
        '"isotropy predicts capacity" was circular (capacity IS the crosstalk; IsoScore mean-centers away the shared-mean '
        'cone that limits RAW-key Hebbian capacity). The REFRAMED result (FULL run, 11 encoders x 5 seeds, M_keys=8000): '
        'the DIRECT crosstalk moment E[<ki,kj>^2] on raw unit-normed keys (D x D gram, no MxM) is the DOMINANT + ROBUST '
        'cross-encoder predictor of capacity -- Pearson(log 1/E[<>^2], log M_crit) = 0.976, Spearman = 0.964 (robust at '
        'n=11, NOT the n=4 smoke fragility). The bare relation is NEAR-BY-CONSTRUCTION (E[<>^2] IS the readout-noise '
        'variance in the SNR that defines M_crit; V=IR is too generous -- here the "R" is the noise that SETS the result). '
        'The non-trivial content is the CONTROLS: SVD d_eff (raw -0.21) and mean-centered IsoScore (raw 0.30) are FAR '
        'weaker direct predictors. Their partials controlling for crosstalk are -0.35 / -0.50 -- WEAK + NOT significant at '
        'n=11 (SE ~ 1/sqrt(n-3) ~ 0.35 -> ~1.0-1.4 SE from zero): so the controls are NOT clean crosstalk-in-disguise '
        '(partials not ~0, unlike the n=4 smoke 0.006) BUT NOT robust independent predictors either (weak, non-significant '
        'residual inverse). HONEST CLAIM: crosstalk is the DOMINANT + ROBUST capacity axis; d_eff + IsoScore are far '
        'sub-dominant with weak non-significant residual inverse signal. TIER = MEASURED_MECHANISM (CERT 591), NOT '
        'chain-grade: (a) the cleanup-boost c is UNBOUNDED (spread 5.04x; c_vs_D=-0.10 not predictable, c_vs_IsoScore=-0.63 '
        'no tight bound) -> not a parameter-free law; (b) partial_controls_fail=False. VERIFIED OFF DATA: cert-owner '
        'ssh-read the remote full metrics + independently recomputed every correlation/partial/c-spread off per_unit '
        '(matched the cell exactly). 2 encoders (gtr-t5/sentence-t5) skipped cleanly (T5 encoder-decoder AutoModel needs '
        'decoder inputs -> try/except, no outcome-selection bias). The 592 chain-grade path stays OPEN but blocked on '
        'bounding c + a significant partial-controls-fail at higher n.'),
    kind=AtomKind.EXPERIMENT_RECORD, tier=Tier.TIER_3_ALGORITHM, corpus=Corpus.MATH, algebra=None,
    metadata={
        'provenance_quality': 'MEASURED_MECHANISM',
        'relevance_tier': 'MEDIUM',
        'verdict': 'MEASURED_MECHANISM_crosstalk_dominant_robust_c_unbounded',
        'run_mode': 'full',
        'n_encoders': 11,
        'n_seeds': 5,
        'encoders': ['all-MiniLM-L6-v2', 'all-mpnet-base-v2', 'all-distilroberta-v1', 'bge-small-en-v1.5',
                     'bge-large-en-v1.5', 'e5-base-v2', 'gpt2-medium', 'pythia-160m', 'pythia-410m', 'pythia-1.4b',
                     'pythia-2.8b'],
        'encoders_skipped_clean': ['gtr-t5-base', 'sentence-t5-base (T5 enc-dec AutoModel needs decoder inputs; no bias)'],
        'metrics_path': 'data/exp_crosstalk_capacity_law_v1_gpu_v1/metrics.json',
        'metrics_source': 'measured_gpu_13enc_crosstalk_capacity_law_raw_keys',
        'key_metrics': {
            'pearson_crosstalk_vs_logMcrit': 0.976, 'spearman_crosstalk_vs_Mcrit': 0.964,
            'pearson_deff_CONTROL': -0.212, 'pearson_isoscore_CONTROL': 0.304,
            'partial_deff_given_crosstalk': -0.349, 'partial_isoscore_given_crosstalk': -0.499,
            'partials_weak_not_significant_at_n11_SE_~0.35': True,
            'c_spread_max_over_min': 5.045, 'c_bound_pearson_c_vs_D': -0.101, 'c_bound_pearson_c_vs_isoscore': -0.632,
            'worst_m_crit_cv': 0.343,
        },
        'honest_scope': ('Direct crosstalk E[<>^2] (raw keys) = DOMINANT + ROBUST cross-encoder capacity predictor '
                         '(0.976/0.964, n=11); near-by-construction (E[<>^2] is the SNR noise variance). Controls (d_eff, '
                         'IsoScore) far weaker (raw 0.21/0.30; partials -0.35/-0.50 WEAK + not significant at n=11). c '
                         'unbounded (5.04x) -> MEASURED_MECHANISM, not parameter-free LAW.'),
        'finding': ('crosstalk is THE robust capacity axis; isotropy (independent IsoScore) + SVD d_eff are NOT separate '
                    'predictors. Overturns the isotropy #6 hypothesis. Substrate-KV: capacity is set by raw-key crosstalk.'),
        'supersedes': 'isotropy #6 draft (hypothesis overturned: independent IsoScore does not predict capacity)',
        'composes_with': ['T3/EXP_hebbian_capacity_projected_v2', 'T3/EXP_kv_learned_projection_v1'],
        'chain_grade_592_path_blocked_on': 'bound c (5.04x spread; c_vs_iso -0.63 weak lead) + significant partial-controls-fail at higher n',
        'c_derivation_status': 'SHELVED -- c not empirically boundable on this data (condition for activation FAILED)',
        'cert_vet_status': 'LANDED_VET_skunkworks_2026-06-20_MEASURED_MECHANISM',
        'verified_off_data': ('cert-owner ssh-read remote full metrics + independent recompute off per_unit (55 units) '
                              'matched the cell exactly; tool committed 4b08a49b.'),
        'atomized_by': 'skunkworks', 'atomized_date': '2026-06-20', 'era': 'comprehensive_program_phase3_glassbox',
    })


DISCIPLINE = Atom(
    id='RULE_controls_fail_claim_needs_partial_correlation_not_just_dominance',
    name=('Methodology rule (cert-VET): when a cert\'s non-trivial content is "control X FAILS to predict Y" (the predictor '
          'is unique/dominant), test the PARTIAL correlation (X | the-real-predictor) -- a control can be DOMINATED yet '
          'retain independent residual signal, OR appear to predict only THROUGH its correlation with the real predictor '
          '(in-disguise); and apply small-n significance (SE ~ 1/sqrt(n-3))'),
    description=(
        'Controls-fail claim needs the PARTIAL correlation. When the cert content is "of candidate predictors, only Z '
        'predicts the outcome; controls X,Y fail" (the controls-failure IS the non-trivial evidence), neither a raw |r| '
        'threshold nor dominance (|r_Z| > |r_X|) is sufficient to establish "X fails." Two distinct cases must be '
        'separated by the PARTIAL correlation partial(X | Z): (1) partial ~ 0 -> X correlated with the outcome ONLY '
        'through Z -> X is "in-disguise" -> genuinely fails (even if raw |r_X| is high); (2) partial SURVIVES -> X carries '
        'independent residual signal -> "X fails" is FALSE; report X as a real (weaker) predictor, do not bury it. AND '
        'apply small-n significance: a partial at n points has SE ~ 1/sqrt(n-3); an EXTREME partial at tiny n (e.g. -0.97 '
        'at n=4, ~1 df) is degeneracy not signal, and a moderate partial (e.g. -0.35 at n=11 ~ 1.0 SE) is NOT significant '
        '-- defer/down-weight rather than over-read "independent predictor." Caught + applied: crosstalk-law (reframed '
        'isotropy #6) -- d_eff raw -0.68 at n=4 was crosstalk-in-disguise (partial 0.006); washed to -0.21 at n=11 with a '
        'weak NON-significant residual partial -0.35; IsoScore partial -0.97 at n=4 was an n=4 degeneracy, -0.50 (~1.4 SE) '
        'at n=11. The honest claim is "dominant predictor + weak non-significant residual controls," neither "controls add '
        'zero power" nor "independent predictors." Mechanized in the landed-VET tool (4b08a49b) with a small-n guard.'),
    kind=AtomKind.METHODOLOGY_RULE, tier=Tier.TIER_METHODOLOGY, corpus=Corpus.META, algebra=None,
    metadata=dict(_COMMON, **{
        'rule_class': 'cert_vet',
        'witnesses': ['crosstalk-law isotropy#6-reframe: d_eff partial 0.006 (n=4 in-disguise) -> -0.35 (n=11 weak/ns) 2026-06-20',
                      'IsoScore partial -0.97 (n=4 degeneracy) -> -0.50 (n=11 ~1.4 SE, not significant) 2026-06-20',
                      'mechanized in landed-VET tool 4b08a49b with small-n guard'],
        'composes_with': ['RULE_held_out_test_not_circular_fit_parameter_free_prediction',
                          'RULE_key_separability_input_degeneracy_preflight',
                          'RULE_capacity_cell_gate_must_be_capacity_relative_not_fixed_M',
                          'AUDIT_negatives_2x_four_class_taxonomy_symmetric_bar_prior_pass_downgrade_is_cert_owner_ruling'],
        'source': 'controls_fail_needs_partial_correlation_crosstalk_law_skunkworks_2026_06_20',
    }))


ATOMS = [RESULT, DISCIPLINE]


def main():
    ps = PartitionedStore(Path('data/substrate_index'))
    pre_cert, pre_ax, pre_mod = cert(ps), axiom(ps), modlive()
    pre_atoms = len(list(ps.all_atoms()))
    print(f"PRE: atoms={pre_atoms} CERT={pre_cert} axiom={pre_ax} cap_pres={pre_mod}")
    if not pre_mod or pre_ax != 206:
        print("PRE-GATE FAIL (axiom!=206 or cap_pres down). HALT."); return 1
    for a in ATOMS:
        if ps.get_atom(a.qualified_id) is not None:
            print(f"  SKIP exists: {a.id}"); continue
        ps.add_atom(a, source='skunkworks_crosstalk_law_landed_vet_2026_06_20',
                    note='crosstalk-law (reframed isotropy #6) MEASURED_MECHANISM + partial-correlation-controls-fail discipline')
        print(f"  ADD: {a.id}")
    ps2 = PartitionedStore(Path('data/substrate_index'))
    post_cert, post_ax, post_mod = cert(ps2), axiom(ps2), modlive()
    post_atoms = len(list(ps2.all_atoms()))
    ids = {x.id for x in ATOMS}
    landed = sorted(a.id for a in ps2.all_atoms() if a.id in ids)
    bad_alg = [a.id for a in ps2.all_atoms() if a.id in ids and a.algebra is not None]
    print(f"POST: atoms={post_atoms} (+{post_atoms-pre_atoms}) CERT={post_cert} (expect {pre_cert}) "
          f"axiom={post_ax} (expect 206) cap_pres={post_mod} landed={len(landed)}/{len(ATOMS)} algebra!=None={bad_alg}")
    gate = (post_cert == pre_cert and post_ax == 206 and post_mod and len(landed) == len(ATOMS) and not bad_alg)
    print("GATE:", "OK" if gate else "FAIL")
    print(f"FOR_RECIPROCAL_CHECK: --expect-cert {post_cert} --expect-atoms {post_atoms}")
    return 0 if gate else 2


if __name__ == '__main__':
    raise SystemExit(main())
