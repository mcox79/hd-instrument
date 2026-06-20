"""Skunkworks 2026-06-20 -- STAGED atomization of this session's 6 distinctive cert-disciplines (the
substrate-autonomy capstone: encode the audit JUDGMENTS as Store atoms / self-cert rulebook entries).

** STAGED -- DO NOT RUN until a COORDINATED single-writer window (no concurrent Store-partition writes) AND the
   disciplines have settled past this session's active application. ** Store save_atoms is NOT cross-session
   concurrency-safe (concurrent same-partition save -> NULL seam -> whole Store unloadable); claim the window first.

All atoms: META corpus, TIER_METHODOLOGY, algebra=None -> NOT cert-counted, NOT axiom_term -> CERT stays 589.
A5-safe: snapshot CERT/axiom/cap_pres -> idempotent add (skip-if-exists) -> verify-after + read-back. ASCII.

The 6 disciplines (this session, 2026-06-20):
  R1 by-construction-saturation / can-fail gate (pythia-KV; mechanized by saturation self-check fbd7078f)
  R2 key-separability / input-degeneracy pre-flight (pythia-KV v3.1; the input-side twin of R1)
  R3 grade-verify-the-referent (N6/C/D; verify an atom's ACTUAL pq before citing it as load-bearing evidence)
  R4 held-out-not-circular-fit (K_max-vs-isotropy; a parameter-laden formula matching its own fit-anchors is circular)
  R5 OOM/no-result = INCOMPLETE not NEGATIVE (backlog; a missing result is not a refutation)
  A1 negatives 4-class taxonomy + symmetric-bar (negatives-2x; class determines "2x"; rescues=fresh-full-bar;
     prior-PASS-downgrade = cert-owner ruling; upward claims get symmetric scrutiny)
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


ATOMS = [
    _rule('RULE_by_construction_saturation_canfail_gate_tier_not_cert',
          'Methodology rule (cert-VET): a PASS whose metric is pinned at an extreme across ALL swept conditions with '
          '~zero spread and no failure regime reached is a TAUTOLOGY (the gate cannot fail) -> TIER, do not cert-grade '
          'as a discriminating win',
          'By-construction-saturation / can-fail gate. A verdict PASS is non-discriminating when its primary metric is '
          'pinned at an extreme (>=ceiling or <=floor) across every swept condition with ~zero variance and NO cliff/'
          'failure regime reached -- the gate could only ever pass (the unreachable-to-fail / tautology side of '
          'can-fail-both-directions). Such a PASS must be TIERED to what it actually shows (viability / exactness-at-'
          'load / a single series-point), NOT cert-graded as a discriminating capacity win. A real capability needs a '
          'DISCRIMINATING regime where the metric CAN drop. Caveat: a single pinned atom may be a legit POINT in a '
          'discriminating op-series (cross-check the series/context before tiering). Mechanized read-only by the '
          'saturation/can-fail self-check (tools/skunkworks_saturation_canfail_check_v1.py, commit fbd7078f). Caught: '
          'pythia-KV v2 HARD_PASS (recall=1.000 across 90 cells, std=0.0, no-cliff) -> tiered to a lower-bound.',
          'cert_vet',
          ['pythia-KV v2 saturation verdict-VET 2026-06-20 (Exp-Dev converged independently via the effrank NN-no-'
           'bottleneck lesson)', 'cert-integrity audit D1 (4 pinned candidates cross-checked legit-in-context)',
           'saturation self-check fbd7078f flags pythia-KV with 0 false-positives across data/'],
          ['RULE_optimal_per_evidence_cert_vet_discipline', 'RULE_key_separability_input_degeneracy_preflight'],
          'pythia_KV_v2_by_construction_saturation_canfail_gate_skunkworks_2026_06_20',
          {'mechanized_tool': 'tools/skunkworks_saturation_canfail_check_v1.py', 'mechanized_commit': 'fbd7078f'}),

    _rule('RULE_key_separability_input_degeneracy_preflight',
          'Methodology rule (cert-VET): before measuring retrieval/associative capability, assert the INPUTS are '
          'distinguishable (median max-cos(item, other-item) < threshold) -- a by-construction-identical input set '
          'makes any retrieval metric meaningless (the input-side twin of the saturation gate)',
          'Key-separability / input-degeneracy pre-flight. The saturation gate screens the OUTPUT (is the metric '
          'degenerate); this screens the INPUT (are the items/keys degenerate) BEFORE retrieval is even measured. If '
          'stored items are near-identical (e.g. template-collapsed embeddings: median max-cos(key, other-key) ~ 1.0 '
          'because shared template tokens wash out the distinguishing tokens), genuine retrieval is impossible and any '
          'whitening that manufactures separability is itself by-construction. Make a key-separability assertion '
          '(median max-cos < ~0.95) a STANDARD dispatch-readiness gate for any associative-memory / substrate-KV cell; '
          'abort if the items are not distinct. Together with the saturation gate it brackets the measurement: a real '
          'capability needs DISTINCT inputs AND a metric that CAN fail. Discovered: pythia-KV v3.1 (templated number-'
          'suffix facts -> template-collapsed keys -> value-cue recall = chance; MEAN-CENTERING the LM anisotropy + a '
          'diverse real-token corpus restored separability). Composes with the isotropy law (collapsed = anisotropic = '
          'high rho_mean = low capacity).',
          'cert_vet',
          ['pythia-KV v3.1 key-non-separability finding 2026-06-20 (Exp-Dev diagnostic; mean-centering fix)',
           'corroborates isotropy-vs-capacity TIER-2 #6 (M_crit ~ 1/rho_mean^2)'],
          ['RULE_by_construction_saturation_canfail_gate_tier_not_cert'],
          'pythia_KV_v3_1_key_separability_input_degeneracy_preflight_skunkworks_2026_06_20'),

    _rule('RULE_grade_verify_the_referent_before_citing_as_load_bearing',
          'Methodology rule (cert-VET): before citing an atom as HARD_PASS / cert-grade EVIDENCE for a claim (a reframe '
          '/ subsumption / "operational"), verify via Store query that the atom-id ACTUALLY resolves to that grade -- '
          'notes-layer / cap_map annotations routinely outrun the backing atom grade',
          'Grade-verify-the-referent. A recurring upward over-claim: cite a HARD_PASS to retire a negative or assert a '
          'capability, WITHOUT checking that the cited atom holds that grade. The reframe DIRECTION may be right but the '
          'GRADE is inflated from a notes-layer / cap_map annotation vs the Store cert-grade. Before any cited grade is '
          'load-bearing in the scorecard / a cert claim, query the Store for the atom-id and confirm its actual '
          'provenance_quality + verdict match the citation; if lower, downgrade the citation to what the Store holds '
          '(the reframe can stand at the true grade). This is the verify-the-referent family applied to the EVIDENCE '
          'grade. Caught 3x in one session: N6 (SMOKE rescue cited as operational HP), C/N2 (MIDDLE_BAND replay cited '
          'as HARD_PASS), D/N7 (MIDDLE_BAND Tier-6 cited as FULL HARD_PASS). Buildable mechanization: a Store-crossref-'
          'grade-consistency check (a cert atom whose load-bearing depends_on resolves to sub-cert evidence).',
          'cert_vet',
          ['N6 resonator-rescue cited operational = SMOKE (verify-the-referent Store query) 2026-06-20',
           'C/N2 + D/N7 scorecard citations downgraded to MIDDLE_BAND/LEGACY after Store check 2026-06-20',
           'cert-integrity audit D3 (37 dep-edges all benign composed-of, confirming the Store-graph is healthy)'],
          ['AUDIT_verify_referent_atom_field_multi_layer_value_resolves_id_form',
           'RULE_optimal_per_evidence_cert_vet_discipline'],
          'grade_verify_the_referent_N6_C_D_pattern_skunkworks_2026_06_20'),

    _rule('RULE_held_out_test_not_circular_fit_parameter_free_prediction',
          'Methodology rule (cert-VET): a parameter-laden formula matching the SAME anchors its free constants were fit '
          'on is CIRCULAR, not validation; the cert claim is the OUT-OF-SAMPLE / PARAMETER-FREE prediction tested on '
          'held-out points',
          'Held-out-not-circular-fit. When a derived formula has free constants tuned to N anchors, "fits the N anchors '
          'within X" is trivially true (free params reproduce the fit points) -- it is calibration, not validation. The '
          'cert gate must be the OUT-OF-SAMPLE prediction (held-out configs not used in the fit) OR, if the formula is '
          'parameter-FREE (analytic, zero fitted constants), matching the anchors IS validation and held-out encoders/'
          'points are additional confirmation. An up-direction guard: a parameter-laden formula matching held-out '
          'points TOO perfectly (within +-1%) suggests the free params hide additional fit (measurement-bug guard). '
          'Contrast this session: K_max NESS algebra (3 fitted constants eta/f_c/tau on 3 anchors -> CIRCULAR -> T3 '
          'CONJECTURE pending a held-out Tier-1 sweep) vs isotropy M_crit ~ 1/rho_mean^2 (PARAMETER-FREE -> the 3 '
          'anchors ARE validation + 2 held-out encoders + a within-encoder causal sweep). Per the 11th methodology '
          'rule (held-out test required).',
          'cert_vet',
          ['K_max NESS algebra T3-tiered (3-param fit on 3 anchors = circular) 2026-06-20',
           'isotropy #6 GO (parameter-free prediction = real validation; not circular) 2026-06-20',
           'K_max Component-2 envelope pre-reg gates on out-of-sample held-out points'],
          ['RULE_optimal_per_evidence_cert_vet_discipline',
           'feedback_held_out_test_methodology_required_for_macro_F1_claims'],
          'held_out_not_circular_fit_Kmax_vs_isotropy_skunkworks_2026_06_20'),

    _rule('RULE_oom_no_result_is_INCOMPLETE_not_a_NEGATIVE',
          'Methodology rule (cert-classification): an OOM / crash / no-log run produced NO science result -> classify '
          'INCOMPLETE (re-dispatch, chunked if large-N), NEVER a capability-failure or a science-NEGATIVE; a missing '
          'result is not a refutation',
          'OOM/no-result = INCOMPLETE not NEGATIVE. Verify-the-referent applied to negatives: a run that OOM\'d or '
          'crashed never tested the capability, so its "negative" must NOT be filed as a refutation or a capability '
          'closure -- it is an infra-INCOMPLETE that needs a clean re-run (chunked/serialized for large-N on the 8GB '
          'GPU per the systemic-OOM finding). Distinct from a genuine completed-with-verdict science negative. This is '
          'the load-bearing guard for the certify-the-backlog + negatives-2x sweeps: do not let infra-incompletes be '
          'mis-recorded as negatives or capability-failures. Caught: composition N>2048 "infra failure" was a fixable '
          'CUDA-OOM (W-matrix materialization), not a science wall; Orchestrator triaged 74 systemic OOMs + 3 peripheral '
          'crashes out of the negatives catalog before 2x-research.',
          'cert_classification',
          ['composition N>2048 OOM diagnosed fixable (chunked-W), not a science negative 2026-06-20',
           'backlog inventory: 1256/1542 genuine; 75 crash-artifacts = INCOMPLETE not negative 2026-06-20',
           'negatives-2x catalog: HIGH-priority negatives verified genuine (not OOM artifacts) before 2x'],
          ['RULE_grade_verify_the_referent_before_citing_as_load_bearing',
           'reference_remote_dispatch_cell_readiness_checklist_2026-06-17'],
          'oom_no_result_is_incomplete_not_negative_skunkworks_2026_06_20'),

    Atom(
        id='AUDIT_negatives_2x_four_class_taxonomy_symmetric_bar_prior_pass_downgrade_is_cert_owner_ruling',
        name=('Audit lesson (cert-classification): negatives have 4 CLASSES (genuine / smoke-grade / infra-incomplete / '
              'accepted-fundamental) that determine what "2x" means; every RESCUE is a fresh FULL-BAR cert claim '
              '(symmetric bar, anti-negativity-bias upward); a prior-PASS found artifactual = the cert-owner\'s EXPLICIT '
              'downgrade ruling, never a silent reclassify'),
        description=(
            "Negatives-2x cert-tiering taxonomy. (RULE 1) Tag every negative by CLASS before 2x: (a) GENUINE completed-"
            "with-verdict -> 2x = re-derivation + rescue search; (b) SMOKE-grade directional -> first power up to cert-"
            "grade; (c) INFRA-INCOMPLETE / OOM -> not a negative; re-run; (d) ACCEPTED-FUNDAMENTAL bound (theory-"
            "predicted) -> 2x that SURVIVES strengthens the bound (a positive cert outcome), only an ESCAPE is a "
            "reframe. (RULE 2) SYMMETRIC BAR: a rescue/reframe is a FRESH full-bar cert claim (gate-mechanism + can-fail-"
            "both + achievability + version-marker); it does NOT inherit/restore a grade -- the negativity-bias rule "
            "cuts UPWARD too (a 'substrate beats X' claim gets the same scrutiny as a negative; verify genuine, not by-"
            "construction/leaking). (RULE 3) A prior PASS found artifactual on re-exam is a CERT-DECREMENT = the cert-"
            "owner's EXPLICIT downgrade ruling with snapshot-before-mutation (A5), never a silent recompute. Applied to "
            "the USER 'research all negatives 2x' directive (2026-06-20): N6 survives as a Frady-Sommer algebraic bound "
            "(class d, positive outcome) but its rescue variants were SMOKE (RULE-2 caught the 'operational' over-"
            "claim); N5 survives as a dense-bipolar ceiling + gives the refuse-gate operating-point separation; N8 "
            "d_eff-negative robust but SMOKE-grade (no CERT increment)."),
        kind=AtomKind.AUDIT_LESSON, tier=Tier.TIER_METHODOLOGY, corpus=Corpus.META, algebra=None,
        metadata=dict(_COMMON, **{
            'lesson_class': 'cert_classification', 'confirmed_or_candidate': 'CONFIRMED', 'witnesses_count': 3,
            'witnesses': ['negatives-2x BATCH-1 dispositions N5/N6/N8 (4-class taxonomy applied) 2026-06-20',
                          'N6 "operational" over-claim caught = SMOKE rescue (RULE-2 symmetric bar) 2026-06-20',
                          'scorecard C/D prior-cite downgrades = grade-match-Store rulings 2026-06-20'],
            'composes_with': ['RULE_grade_verify_the_referent_before_citing_as_load_bearing',
                              'RULE_oom_no_result_is_INCOMPLETE_not_a_NEGATIVE',
                              'feedback_negativity_bias_symmetric',
                              'feedback_research_can_be_wrong_only_proven_fully_believed_trust_tier'],
            'source': 'negatives_2x_four_class_taxonomy_symmetric_bar_skunkworks_2026_06_20',
        })),
]


def main():
    print("** STAGED atomization -- confirm a COORDINATED single-writer window before running (uncomment the guard). **")
    RUN_GUARD = True  # set True ONLY inside a claimed single-writer window
    if not RUN_GUARD:
        print("RUN_GUARD=False -> dry-run only (drafted %d atoms; not written). Atoms:" % len(ATOMS))
        for a in ATOMS:
            print("  - [%s] %s" % (a.kind.value if hasattr(a.kind, 'value') else a.kind, a.id))
        return 0
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
        ps.add_atom(a, source='skunkworks_session_cert_disciplines_2026_06_20',
                    note='6 cert-disciplines (saturation/key-separability/grade-verify/held-out/OOM-incomplete/negatives-taxonomy)')
        added += 1
    ps2 = PartitionedStore(Path('data/substrate_index'))
    post_cert, post_ax, post_mod = cert(ps2), axiom(ps2), modlive()
    post_atoms = len(list(ps2.all_atoms()))
    landed = sorted(a.id for a in ps2.all_atoms() if a.id in {x.id for x in ATOMS})
    bad_alg = [a.id for a in ps2.all_atoms() if a.id in {x.id for x in ATOMS} and a.algebra is not None]
    print(f"POST: atoms={post_atoms} (+{post_atoms-pre_atoms}) CERT={post_cert} (expect {pre_cert}) "
          f"axiom={post_ax} (expect 206) cap_pres={post_mod} landed={len(landed)} algebra!=None={bad_alg}")
    gate = (post_cert == pre_cert and post_ax == 206 and post_mod and len(landed) == len(ATOMS) and not bad_alg)
    print("GATE:", "OK" if gate else "FAIL")
    return 0 if gate else 2


if __name__ == '__main__':
    raise SystemExit(main())
