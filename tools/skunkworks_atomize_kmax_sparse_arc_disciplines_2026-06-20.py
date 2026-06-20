"""Skunkworks 2026-06-20 -- atomize the 5 genuinely-NEW disciplines from the K_max NESS + sparse-#2 arcs (the deferred
batch, in a CERT-neutral single-writer window during the sparse-#2 run). Already-atomized (NOT duplicated): capacity-relative-
gate / reconciliation-uses-runs-own-moments / same-distribution-split (baa06f0a) + controls-fail-needs-partial-correlation
(7315be3c) + the ae088f94 six.

5 atoms: METHODOLOGY_RULE / TIER_METHODOLOGY / META / algebra=None -> NOT cert-counted, NOT axiom -> CERT stays 592.
A5-safe: snapshot CERT/axiom/cap_pres -> idempotent add (skip-if-exists) -> verify-after. Expect CERT 592 UNCHANGED, axiom 206,
cap_pres 6/6, +5 atoms, no algebra. ASCII.
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


def _rule(rid, name, desc, rule_class, witnesses, composes, source):
    md = dict(_COMMON); md.update({'rule_class': rule_class, 'witnesses': witnesses, 'composes_with': composes, 'source': source})
    return Atom(id=rid, name=name, description=desc, kind=AtomKind.METHODOLOGY_RULE, tier=Tier.TIER_METHODOLOGY,
                corpus=Corpus.META, algebra=None, metadata=md)


ATOMS = [
    _rule('RULE_cited_number_must_reproduce_from_the_cell_else_miscite',
          'Methodology rule (cert-VET): before a cited number (in a scorecard / note / prereg / report) is load-bearing in a '
          'cert claim or a gate, it MUST reproduce from the cell\'s ACTUAL code/data; if it does not, it is a MISCITE/PHANTOM '
          '-- do NOT gate or claim on it (verify-the-referent applied to the cited NUMBER, not just the grade)',
          'Cited-number-must-reproduce-from-the-cell. A recurring high-frequency failure: a number cited in the notes-layer / '
          'scorecard / prereg (a ratio, a capacity, a prediction) does NOT reproduce when you run the cell\'s actual code on '
          'its actual data. Such a number is a MISCITE or a PHANTOM (a sweep-endpoint artifact, a transcription typo, a '
          'construction from the wrong axis, a stale report) -- it must NOT be a reproduction-gate target NOR a cert claim. '
          'The fix: re-derive the cited number from the cell\'s code/data BEFORE it is load-bearing; if it doesn\'t '
          'reproduce, file it as a miscite + use the cell-reproducible value. Caught FIVE times this session (the dominant '
          'failure mode): sparse 6x/25x = LOAD-sweep-ENDPOINT ratios (0.20/0.033), not measured gains; K_eq "47 at 0.1*ac" = '
          'a scorecard alpha-mislabel (47 is at 0.27*ac per the formula); sparse "1.4x" = does NOT reproduce from '
          'sparse_vs_dense\'s recall (which gives 8x, identical to the new cell -> miscite); isotropy "predicts capacity" '
          'evaporated under an independent measure; K_max "exceeds 2x at low alpha" was an extrapolation. The matched-config '
          're-derivation (run the cited measurement\'s actual code at matched config) is the definitive resolver.',
          'cert_vet',
          ['sparse 6x/25x phantom (LOAD-sweep-endpoint) 2026-06-20', 'K_eq 47-at-0.1ac scorecard-typo (47 at 0.27ac) 2026-06-20',
           'sparse 1.4x miscite (does not reproduce from sparse_vs_dense recall = 8x identical) 2026-06-20',
           'matched-config diff = the definitive reproduce-or-miscite resolver (Exp-Dev) 2026-06-20'],
          ['RULE_grade_verify_the_referent_before_citing_as_load_bearing',
           'RULE_reconciliation_must_use_the_runs_own_moments_not_a_reference_value',
           'AUDIT_verify_referent_atom_field_multi_layer_value_resolves_id_form'],
          'cited_number_must_reproduce_from_cell_sparse_kmax_skunkworks_2026_06_20'),

    _rule('RULE_complete_divide_by_near_zero_guard_BOTH_limits',
          'Methodology rule (cert-VET): a ratio-gate (obs/baseline) must guard BOTH degenerate limits of the baseline -- '
          'baseline->0 (ratio blows up -> trivial pass) AND baseline->inf (ratio->0 -> unfair fail). Gate ONLY in the regime '
          'where the baseline is BOUNDED on both sides (the discriminating window). A half-guard (one limit only) is incomplete',
          'Complete divide-by-near-zero guard (BOTH limits). A ratio cert-gate obs/baseline has TWO ways the baseline can be '
          'degenerate, and BOTH must be guarded: (1) baseline -> 0 -> ratio -> inf -> TRIVIAL PASS (the by-construction-'
          'saturation hazard); (2) baseline -> inf -> ratio -> 0 -> UNFAIR FAIL (the obs cannot possibly exceed a blown-up '
          'baseline). Gate ONLY in the MODERATE regime where the baseline is BOUNDED on both sides -- the discriminating '
          'window where the ratio CAN genuinely pass OR fail. Caught: K_max NESS K_eq = 3.3*(1-a/ac)^2/a -> 0 as a->ac '
          '(trivial pass; I flagged this) AND -> inf as a->0 via the /a (unfair fail; Exp-Dev SMOKE caught this -- the '
          'original {0.05..0.25}*ac sweep auto-failed on the blown-up baseline). The COMPLETE guard = moderate alpha '
          '[0.3,0.7]*ac (K_eq bounded ~3-39). Discipline-lesson: a divide-by-near-zero caveat that flags ONE limit is HALF-'
          'complete; verify-the-referent on your own caveat (the cert-owner OWNED the gap; the smoke completed it).',
          'cert_vet',
          ['K_max NESS K_eq both-limits (a->ac K_eq->0 + a->0 K_eq->inf) 2026-06-20',
           'Skunkworks half-caveat (flagged a->ac, missed a->0) + Exp-Dev smoke caught the gap -> completed guard 2026-06-20',
           'moderate regime [0.3,0.7]*ac = the bounded discriminating window'],
          ['RULE_capacity_cell_gate_must_be_capacity_relative_not_fixed_M',
           'RULE_by_construction_saturation_canfail_gate_tier_not_cert'],
          'complete_divide_by_near_zero_guard_both_limits_kmax_skunkworks_2026_06_20'),

    _rule('RULE_data_decides_tier_no_preemptive_downgrade_without_data',
          'Methodology rule (cert-classification): do NOT preemptively DOWNGRADE a tier based on a WRONG-REGIME or INCOMPLETE '
          'result -- a wrong-regime/incomplete outcome is NOT evidence the capability fails; run the DISCRIMINATING regime + '
          'let the DATA decide the tier (the symmetric twin of no-preemptive-UPGRADE)',
          'Data-decides-tier; no preemptive-downgrade-without-data. The negativity-bias rule cuts the downgrade direction '
          'too: a tier must not be DOWNGRADED (chain-grade -> MEASURED_MECHANISM) on the basis of a result from the WRONG '
          'regime or an INCOMPLETE run. A wrong-regime result (e.g. a gate auto-failing because the baseline blew up outside '
          'the discriminating window) is NOT evidence the capability fails -- it is a mis-measurement. The correct move: fix '
          'the regime / complete the run, then let the DATA in the discriminating regime decide the tier. Pre-registering '
          'the tier as DATA-DECIDES (chain-grade IF gates met in the valid regime, else lower) avoids both preemptive-'
          'downgrade and gerrymander-to-pass. Caught: K_max NESS was preemptively reframed chain-grade -> MEASURED_MECHANISM '
          'on the WRONG-REGIME (low-alpha K_eq-blowup) smoke; RETRACTED once the moderate-regime guard showed the chain-grade '
          'was genuinely testable -> it then EARNED CERT 592 on the data (Director self-catch #11). Mirror of the upward '
          'negativity-bias-symmetric rule (verify both directions).',
          'cert_classification',
          ['K_max NESS premature MEASURED_MECHANISM reframe (wrong-regime smoke) -> RETRACTED -> data earned CERT 592 2026-06-20',
           'Director self-catch #11 preemptive-tier-downgrade-without-data 2026-06-20'],
          ['RULE_oom_no_result_is_INCOMPLETE_not_a_NEGATIVE', 'feedback_negativity_bias_symmetric',
           'AUDIT_negatives_2x_four_class_taxonomy_symmetric_bar_prior_pass_downgrade_is_cert_owner_ruling'],
          'data_decides_tier_no_preemptive_downgrade_kmax_skunkworks_2026_06_20'),

    _rule('RULE_genuine_reasoning_check_must_test_the_artifact_free_arm',
          'Methodology rule (cert-VET): a genuine-reasoning / not-an-artifact screen must test the ARTIFACT-FREE arm at the '
          'RIGHT measurement (e.g. the cleanup-OFF control which CANNOT have the cleanup-recovery artifact), NOT a mis-spec\'d '
          'proxy that fails by-construction whenever the augmentation helps at all',
          'Genuine-reasoning check must test the artifact-free arm. When screening whether a deep/strong result is GENUINE vs '
          'an AUGMENTATION-ARTIFACT (e.g. cleanup-recovery leaking the target), the check must be measured on the ARTIFACT-'
          'FREE arm -- the arm that BY CONSTRUCTION cannot have the artifact (e.g. cleanup-OFF control: no codebook snap -> '
          'cannot be cleanup-recovery). A mis-spec\'d check that tests the control at the AUGMENTED depth (deeper than the '
          'control\'s own range by construction whenever augmentation helps) fails on ANY augmentation -> it conflates '
          'desired augmentation with the artifact. The right discriminators: (a) does the ARTIFACT-FREE arm alone exceed the '
          'baseline (genuine without the augmentation)? (b) does the augmentation TRAVERSE correctly per-step (e.g. '
          'ext_hopfrac = fraction of hops snapping to the CORRECT next node) vs jump-to-target (recovery)? Caught: K_max NESS '
          'genuine-multi-hop check mis-spec\'d (control recall at cand2\'s deep_K -> False on any cleanup boost); corrected to '
          'control K_obs > K_eq (artifact-free) + ext_hopfrac>=0.85 (per-hop correct-next-node) -> CERT 592 genuine. The '
          'two-arm-independence (control alone) is the strongest genuineness evidence.',
          'cert_vet',
          ['K_max NESS genuine-multi-hop misspec (control-at-cand2-deep_K) -> corrected to control>K_eq + ext_hopfrac 2026-06-20',
           'CERT 592 genuine on BOTH the artifact-free control arm (5/5) AND ext_hopfrac~1.0 2026-06-20'],
          ['RULE_by_construction_saturation_canfail_gate_tier_not_cert',
           'RULE_controls_fail_claim_needs_partial_correlation_not_just_dominance'],
          'genuine_check_must_test_artifact_free_arm_kmax_skunkworks_2026_06_20'),

    _rule('RULE_disambiguate_parameter_semantics_before_compare_load_vs_sparse_fraction',
          'Methodology rule (cert-VET): a parameter\'s SEMANTICS must be disambiguated before comparing/citing across cells '
          '-- conflating two distinct meanings of the same symbol (e.g. alpha = LOAD M/N vs alpha = SPARSE-FRACTION f) '
          'produces phantom comparisons and wrong axes',
          'Disambiguate-parameter-semantics-before-compare. The same symbol can mean different things across cells/contexts '
          '(classic: "alpha" = storage LOAD M/N in one cell vs the SPARSE-FRACTION f / activity in another). Comparing or '
          'citing a number across cells WITHOUT pinning which semantics each uses produces a phantom (apples-vs-oranges). '
          'Before a cross-cell comparison/citation: state the symbol\'s exact definition in EACH cell; ensure the comparison '
          'holds the SAME-semantics axis fixed. Caught: the sparse 6x/25x phantom CONFLATED load-alpha (the load-sweep '
          'axis) with sparse-fraction-f (the sparsity axis) -- "25x@sparse_alpha=0.05" mixed the two. The reframe pinned the '
          'AXIS = sparse-fraction f (sweep f, report alpha_c(f)) -> the honest capacity-vs-sparsity curve. The right axis is '
          'a prerequisite for a meaningful gate.',
          'cert_vet',
          ['sparse 6x/25x phantom = load-alpha vs sparse-fraction-f conflation (Director self-catch #9) 2026-06-20',
           'sparse-#2 reframe pinned AXIS = sparse-fraction f -> honest alpha_c(f) curve 2026-06-20'],
          ['RULE_cited_number_must_reproduce_from_the_cell_else_miscite',
           'RULE_grade_verify_the_referent_before_citing_as_load_bearing'],
          'disambiguate_parameter_semantics_load_vs_sparse_fraction_skunkworks_2026_06_20'),
]


def main():
    ps = PartitionedStore(Path('data/substrate_index'))
    pre_cert, pre_ax, pre_mod = cert(ps), axiom(ps), modlive()
    pre_atoms = len(list(ps.all_atoms()))
    print(f"PRE: atoms={pre_atoms} CERT={pre_cert} axiom={pre_ax} cap_pres={pre_mod}")
    if not pre_mod or pre_ax != 206 or pre_cert != 592:
        print("PRE-GATE FAIL (expect CERT 592, axiom 206, cap_pres). HALT."); return 1
    for a in ATOMS:
        if ps.get_atom(a.qualified_id) is not None:
            print(f"  SKIP exists: {a.id}"); continue
        ps.add_atom(a, source='skunkworks_kmax_sparse_arc_disciplines_2026_06_20',
                    note='5 new K_max+sparse arc cert-disciplines (cited-number-reproduce / both-limits-divide-guard / data-decides-tier / genuine-artifact-free-arm / param-semantics-disambiguate)')
        print(f"  ADD: {a.id}")
    ps2 = PartitionedStore(Path('data/substrate_index'))
    post_cert, post_ax, post_mod = cert(ps2), axiom(ps2), modlive()
    post_atoms = len(list(ps2.all_atoms()))
    ids = {x.id for x in ATOMS}
    landed = sorted(a.id for a in ps2.all_atoms() if a.id in ids)
    bad_alg = [a.id for a in ps2.all_atoms() if a.id in ids and a.algebra is not None]
    print(f"POST: atoms={post_atoms} (+{post_atoms-pre_atoms}) CERT={post_cert} (expect 592) "
          f"axiom={post_ax} (expect 206) cap_pres={post_mod} landed={len(landed)}/{len(ATOMS)} algebra!=None={bad_alg}")
    gate = (post_cert == 592 and post_ax == 206 and post_mod and len(landed) == len(ATOMS) and not bad_alg)
    print("GATE:", "OK" if gate else "FAIL")
    print(f"FOR_RECIPROCAL_CHECK: --expect-cert {post_cert} --expect-atoms {post_atoms}")
    return 0 if gate else 2


if __name__ == '__main__':
    raise SystemExit(main())
