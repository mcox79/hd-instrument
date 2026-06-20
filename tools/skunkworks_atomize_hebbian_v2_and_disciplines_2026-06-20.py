"""Skunkworks 2026-06-20 -- atomize the Hebbian-superposition v2 LANDED-VET disposition + the 3 disciplines
from this arc. Single-writer window (Orchestrator stood down Store-writes; reciprocal post-land check offered).

Batch (4 atoms, one window to minimize concurrency-hazard exposure):
  1. T3/EXP_hebbian_capacity_projected_v2  (EXPERIMENT_RECORD, pq=MEASURED_MECHANISM)  -- the result.
     The CERT headline counts CERT_CHAIN_GRADE only -> MEASURED_MECHANISM leaves CERT unchanged (591). Correct:
     no NEW capability (the substrate-KV mechanism = NN is already #7/CERT 591); this is supporting evidence +
     a characterized-negative on the rejected alternative (Hebbian-superposition).
  2-4. 3 METHODOLOGY_RULE / META / algebra=None disciplines -> NOT cert-counted, NOT axiom_term.

A5-safe: snapshot CERT/axiom/cap_pres/atoms -> idempotent add (skip-if-exists) -> verify-after + read-back.
Expect: CERT 591 UNCHANGED, axiom 206 UNCHANGED, cap_pres 6/6, +4 atoms, no algebra on any added atom. ASCII only.
All metric values verified off the actual remote metrics.json (ssh-read by the cert-owner), not the verdict-note.
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


def _rule(rid, name, desc, rule_class, witnesses, composes, source, extra=None):
    md = dict(_COMMON); md.update({'rule_class': rule_class, 'witnesses': witnesses, 'composes_with': composes,
                                   'source': source})
    if extra:
        md.update(extra)
    return Atom(id=rid, name=name, description=desc, kind=AtomKind.METHODOLOGY_RULE, tier=Tier.TIER_METHODOLOGY,
                corpus=Corpus.META, algebra=None, metadata=md)


HEBBIAN = Atom(
    id='T3/EXP_hebbian_capacity_projected_v2',
    name=('Experiment record (MEASURED_MECHANISM, characterized-negative): Hebbian-superposition associative-memory '
          'capacity on #7-de-crowded Pythia-2.8b keys = M_crit ~327 (measured, 4/5 seeds in-grid); cleanup-argmax boost '
          'c~17 over raw-SNR 1/E[<ki,kj>^2]~19; NN-retrieval (#7) >> Hebbian -> substrate-KV mechanism = NN-retrieval, '
          'not superposition'),
    description=(
        'Hebbian-superposition (W = sum_k k_k k_k^T; argmax-cleanup readout) associative-memory capacity, measured on '
        'the SAME #7-de-crowded projected Pythia-2.8b keys that NN-retrieval (#7, CERT 591) uses -- the FAIR test. '
        'Result: M_crit ~327 (recall crosses 0.8 at M~100-480 IN-GRID; 4/5 seeds measured, seed0 floor-clamped at the '
        'M=100 grid edge). Cleanup-argmax boost c = M_crit_obs(327)/raw-SNR(1/E[<>^2]=18.9) = 17.3 (a FIT ratio, NOT a '
        'derived parameter-free law). recall@1k proj=0.619 vs raw=0.001 = 619x (the #7 de-crowding projection works '
        'massively; confound resolved). FINDING: NN-retrieval (#7, works to M=10k) >> Hebbian-superposition (M_crit '
        '~few-hundred, crosstalk-limited even on de-crowded keys) -> SETTLES the substrate-KV memory mechanism = '
        'NN-retrieval; Hebbian-superposition is a real-but-lower-capacity alternative. CAVEATS: (a) CV=0.418 (seed '
        'spread 100-480; seed0 at the grid floor) -- the QUALITATIVE finding (Hebbian few-hundred << NN 10k) is robust, '
        'the specific 327 carries the CV caveat; (b) the cell verdict HARD_FAIL is on a recall@1k>=0.80 gate that is '
        'MIS-CALIBRATED (capacity 327<1k -> recall@1k is past-capacity, NOT a failure-at-1k); the correct framing is '
        '"capacity=327, characterized". VERIFIED OFF DATA: cert-owner ssh-read the remote metrics.json; per-seed '
        'rho_mean = 0.0504/0.0538/0.0504/0.0536/0.0366 (preflight_fail=false all 5 -> de-crowded to #7 level, matching '
        '#7\'s 0.03-0.05); half-dim can-fail control = 140 < main 327 (all 5 seeds half<main -> a REAL measurement '
        'responding to proj-dim, NOT the v1 ~201 code-floor artifact). SUPERSEDES the INVALID v1 (rho_mean 0.28-0.35 '
        'crowded keys [offset=10M distribution-shift] + extrapolation-artifact M_crit~201; v1 was HELD, never atomized). '
        'On de-crowded keys E[<>^2]~0.053 is rho_var-dominated (rho_mean^2~0.0027 negligible) -> the full-crosstalk '
        'isotropy formula applies cleanly; no bulk-vs-tail subtlety needed (that reconciliation was retracted as '
        'unnecessary). c(M)-derivation HELD (not on the enabling path: characterizes a mechanism we decided AGAINST).'),
    kind=AtomKind.EXPERIMENT_RECORD, tier=Tier.TIER_3_ALGORITHM, corpus=Corpus.MATH, algebra=None,
    metadata={
        'provenance_quality': 'MEASURED_MECHANISM',
        'relevance_tier': 'MEDIUM',
        'verdict': 'CHARACTERIZED_NEGATIVE_mechanism_choice_NN',
        'cell_verdict_as_gated': 'HARD_FAIL_on_miscalibrated_recall_at_1k_gate',
        'run_mode': 'full',
        'encoder': 'EleutherAI/pythia-2.8b',
        'n_seeds': 5,
        'proj_dim': 256,
        'M_sweep': [100, 250, 500, 1000, 2500, 5000, 10000, 25000, 50000],
        'metrics_path': 'data/exp_hebbian_capacity_projected_v2/metrics.json',
        'metrics_source': 'measured_gpu_pythia2p8b_hebbian_capacity_projected_keys',
        'key_metrics': {
            'm_crit_obs_mean': 327.21, 'm_crit_raw_snr_pred_mean': 18.92, 'cleanup_boost_c_fit': 17.3,
            'recall_1k_proj': 0.6194, 'recall_1k_raw': 0.001, 'proj_over_raw': 619.4,
            'm_crit_cv': 0.418, 'canfail_halfdim_mcrit_mean': 140.11,
            'rho_mean_per_seed': [0.0504, 0.0538, 0.0504, 0.0536, 0.0366], 'preflight_passed_all_seeds': True,
            'm_crit_obs_per_seed': [100.0, 287.04, 312.5, 456.52, 480.0],
        },
        'honest_scope': ('Hebbian-superposition capacity on #7-de-crowded keys (rho_mean~0.05 = #7). M_crit measured '
                         'in-grid (4/5 seeds; seed0 floor-clamped). c=17.3 is FIT (m_crit_obs/raw-SNR), NOT derived. '
                         'CV=0.418. recall@1k>=0.80 verdict-gate is mis-calibrated (capacity 327<1k).'),
        'finding': ('NN-retrieval (#7, CERT 591, M=10k) >> Hebbian-superposition (M_crit~327). Substrate-KV memory '
                    'mechanism = NN-retrieval. Hebbian-superposition = real-but-lower-capacity alternative.'),
        'supersedes_invalid_v1': ('exp_hebbian_capacity_projected_v1 HELD (keys not de-crowded rho_mean 0.28-0.35 + '
                                  'extrapolation-artifact M_crit~201); v1 never atomized -- invalid run.'),
        'composes_with': ['T3/EXP_kv_learned_projection_v1'],
        'related_text_refs_not_edges': ('#6 isotropy law M_crit ~ 1/E[<ki,kj>^2] (this is the de-crowded-keys '
                                        'CAPACITY-regime test of it; #6 pending-not-atomized so referenced in text, '
                                        'phantom-safe); n1_substrate_kv (the NN-retrieval capability it supports).'),
        'enabling_outcome': 'substrate_kv_memory_mechanism_selection = NN-retrieval (confirms #7)',
        'cleanup_boost_c_derivation': ('HELD -- Orchestrator offer not pursued (fit-not-derived + CV-high + non-used '
                                       'mechanism); revisit IF Phase-3 glass-box-LLM needs a parameter-free '
                                       'Hebbian-capacity bound for encoder-selection.'),
        'cert_vet_status': 'LANDED_VET_skunkworks_2026-06-20_option1_characterized_negative',
        'verified_off_data': ('cert-owner ssh-read remote metrics.json; per-seed rho_mean + recall-curves + half-dim '
                              'control + run_mode=full(1306s) all verified, not taken from the verdict-note.'),
        'atomized_by': 'skunkworks', 'atomized_date': '2026-06-20', 'era': 'comprehensive_program_phase3_glassbox',
    })


ATOMS = [
    HEBBIAN,

    _rule('RULE_capacity_cell_gate_must_be_capacity_relative_not_fixed_M',
          'Methodology rule (cert-VET): a capacity/associative-memory cell must gate recall at an M chosen RELATIVE to '
          'the measured M_crit (recall at M << M_crit, or gate on M_crit itself), NEVER at a fixed arbitrary M -- else a '
          'low-capacity-but-REAL mechanism reads as a false failure-at-M',
          'Capacity-cell gates must be capacity-RELATIVE. When a cell measures storage/retrieval CAPACITY (M_crit, where '
          'recall crosses a threshold), a PASS/FAIL gate fixed at an arbitrary M (e.g. recall@1k>=0.80) silently assumes '
          'capacity >= that M. If the true capacity is BELOW it, recall@M is PAST-CAPACITY (expected to be low) and the '
          'cell HARD_FAILs a clean, real capacity measurement -- mis-framing "capacity=327, characterized" as '
          '"fails@1k". The gate must be set relative to the MEASURED M_crit (recall at M well below M_crit) or report '
          'M_crit directly and gate on it. The up-direction twin of the saturation/can-fail gate: there the metric '
          'cannot FAIL (tautology); here the metric is FORCED to fail by an over-high fixed threshold (false-negative). '
          'Caught: Hebbian-superposition v2 (M_crit~327 measured, de-crowded keys) HARD_FAILed a recall@1k>=0.80 gate '
          'purely because 327<1000 -> re-framed as a characterized capacity, not a failure. Orchestrator internalized '
          'it for capacity-cell dispatch-readiness pre-checks.',
          'cert_vet',
          ['Hebbian-superposition v2 recall@1k>=0.80 gate mis-calibrated (capacity 327<1k) 2026-06-20',
           'Orchestrator ACK + internalized for capacity-cell dispatch pre-checks 2026-06-20'],
          ['RULE_by_construction_saturation_canfail_gate_tier_not_cert',
           'RULE_key_separability_input_degeneracy_preflight'],
          'capacity_cell_gate_capacity_relative_hebbian_v2_skunkworks_2026_06_20'),

    _rule('RULE_reconciliation_must_use_the_runs_own_moments_not_a_reference_value',
          'Methodology rule (cert-VET): when reconciling an observed metric against a theory prediction, plug in the '
          "RUN'S OWN measured moments/parameters -- NOT a reference/expected value from a DIFFERENT run; a reconciliation "
          'that matches only with a foreign parameter is an artifact, not a validation',
          "Reconciliation-uses-the-run's-own-moments. A subtle verify-the-referent failure in ANALYSIS (not just data): "
          'reconciling obs vs a closed-form prediction by substituting a parameter value ASSUMED/expected (from a '
          'reference run, a sibling cert, or the design intent) rather than the value THIS run actually produced. The '
          'reconciliation can look spot-on while being internally inconsistent (two different parameter regimes). Before '
          'a reconciliation is load-bearing, assert every plugged-in moment/parameter is read from THIS run\'s metrics. '
          'Caught: the Hebbian v1 "bulk M_crit~178 ~ obs 201, spot-on" used rho_mean=0.03 (#7\'s DE-CROWDED value) '
          'against a run whose ACTUAL rho_mean was ~0.30 (crowded) -> on the real keys it collapses to 1.8; the match '
          'was an artifact of the foreign rho_mean coinciding with an extrapolation-floor obs. Orchestrator self-caught '
          '+ retracted. Twin of grade-verify-the-referent (that verifies the cited GRADE; this verifies the cited '
          'PARAMETER VALUE used in an analysis).',
          'cert_vet',
          ['Hebbian v1 bulk-vs-tail reconciliation used #7 de-crowded rho_mean=0.03 on a crowded-key run 2026-06-20',
           'Orchestrator self-corrected + retracted the "resolved" claim 2026-06-20',
           'v2 confirms: on the run\'s OWN de-crowded moments (rho_mean~0.05, E[<>^2]~0.053) the cleanup-boost is the '
           'right story, no foreign-parameter needed'],
          ['RULE_grade_verify_the_referent_before_citing_as_load_bearing',
           'AUDIT_verify_referent_atom_field_multi_layer_value_resolves_id_form'],
          'reconciliation_uses_runs_own_moments_hebbian_v1_skunkworks_2026_06_20'),

    _rule('RULE_same_distribution_train_test_split_or_projection_wont_generalize',
          'Methodology rule (cert-classification): a learned projection / encoder-fit must be trained and held-out '
          'tested on the SAME data distribution -- an offset/segmented split that induces a distribution-shift (e.g. '
          'offset=10M -> different value-format regime) silently breaks generalization and the projection fails to '
          'transfer (de-crowd / separate) on the held-out set',
          "Same-distribution train/test split for learned projections. When a projection (or any fitted encoder/whitener) "
          'is trained to make held-out items separable, the train and held-out sets must be drawn from the SAME '
          'distribution. A split that offsets or segments the index (intending non-overlap) can induce a '
          'DISTRIBUTION-SHIFT: the held-out items occupy a region/format the projection never saw -> it fails to '
          'generalize -> the held-out keys stay CROWDED (the projection looks applied but is ineffective). The symptom '
          '(crowded keys, rho_mean high) is downstream; the root cause is the split, not the projection code. Verify the '
          'held-out distribution matches train BEFORE attributing a generalization failure to the method. Root-caused: '
          'Hebbian v1 used offset=10M for the held-out CAP keys -> 8-digit-year value-format shift -> #7\'s projection '
          "(trained on the in-distribution facts) didn't de-crowd them (rho_mean 0.28 vs #7's 0.05). The "
          'same-distribution random split (v2) fixed it (rho_mean 0.05, matching #7). Composes with the rho_mean '
          'pre-flight gate (assert de-crowded BEFORE measuring) as the detection backstop.',
          'cert_classification',
          ['Hebbian v1 offset=10M distribution-shift -> crowded held-out keys (Exp-Dev root-cause) 2026-06-20',
           'Hebbian v2 same-distribution split -> de-crowded rho_mean 0.05 = #7 level, generalization restored 2026-06-20'],
          ['RULE_key_separability_input_degeneracy_preflight',
           'RULE_held_out_test_not_circular_fit_parameter_free_prediction',
           'feedback_held_out_test_methodology_required_for_macro_F1_claims'],
          'same_distribution_split_for_projection_generalization_hebbian_v1_skunkworks_2026_06_20'),
]


def main():
    ps = PartitionedStore(Path('data/substrate_index'))
    pre_cert, pre_ax, pre_mod = cert(ps), axiom(ps), modlive()
    pre_atoms = len(list(ps.all_atoms()))
    print(f"PRE: atoms={pre_atoms} CERT={pre_cert} axiom={pre_ax} cap_pres={pre_mod}")
    if not pre_mod or pre_ax != 206:
        print("PRE-GATE FAIL (axiom!=206 or cap_pres down). HALT."); return 1
    added = 0
    for a in ATOMS:
        if ps.get_atom(a.qualified_id) is not None:
            print(f"  SKIP exists: {a.id}"); continue
        ps.add_atom(a, source='skunkworks_hebbian_v2_landed_vet_2026_06_20',
                    note='Hebbian-superposition v2 MEASURED_MECHANISM characterized-negative + 3 arc disciplines')
        added += 1
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
