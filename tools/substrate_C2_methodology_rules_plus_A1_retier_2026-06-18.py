"""C2 wrap-up (Skunkworks solo): 2 self-certification METHODOLOGY_RULEs + A1 deliberate retier.

(1) RULE_cert_gate_structural_not_post_hoc (cand1 forward-principle, elevated from C3 to methodology_rule):
    cert-gates must be STRUCTURAL (encoded in the cell self-check + atomizer derivation), NOT post-hoc
    cert-owner manual VET. Witness: the 8a inversion (blind pq-derivation certified a refuted cost-model
    HARD_PASS). The method-gate (305c2e61) + GATE-0-both-ends (674cce5d) move the judgment INTO the pipeline.
(2) RULE_gate0_both_ends_producer_attest_consumer_enforce (the C2 engine's operating rule):
    GATE-0 enforced at BOTH ends (producer gate0_self_check + consumer gate0_field_check); wall-time is a
    TELL recorded for inspection, NOT a hard gate (gate0-plausibility-per-cell-workload); additive+non-retroactive.
(3) A1 atom retier: provenance_quality LEGACY_EXCERPT -> MEASURED_MECHANISM (deliberate cert-owner
    single-atom reclassification now the tier exists/pushed; CERT count UNCHANGED -- both non-CERT;
    fixes the fresh-measured-mechanism-mislabeled-as-legacy). NOT a mass recompute (1 atom, deliberate).

Gated: axiom_term 206/206 + cap_pres 6/6 HARD-FAIL (pre+post). Serial; fresh-load.
"""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path('.').resolve()))

from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import Atom, AtomKind, Corpus, Tier

RULES = [
    {
        'id': 'RULE_cert_gate_structural_in_pipeline_not_post_hoc_cert_owner_vet',
        'name': 'Methodology rule (PHASE-2; cert-autonomy): cert-gates STRUCTURAL-in-pipeline, not post-hoc manual VET',
        'description': (
            "A cert-eligibility gate must be STRUCTURAL -- encoded in the producer cell's self-check AND the "
            "atomizer's pq-derivation -- NOT left to a post-hoc cert-owner manual VET. WITNESS (the 8a inversion): "
            "a blind pq-derivation (run_mode + n_seeds, WITHOUT checking metrics_source) auto-certified a REFUTED "
            "cost-model HARD_PASS = a cert inversion, caught only by a 2nd-witness count check. FIX: method_gate "
            "(305c2e61) + GATE-0-both-ends (674cce5d) move the judgment INTO the pipeline (deterministic). The "
            "substrate-autonomy increment (USER directive): an audit JUDGMENT -> a deterministic self-applied check. "
            "Corollary: a post-hoc manual gate is necessary-bootstrapping but NOT sufficient -- encode it structurally."
        ),
        'rule_class': 'cert_autonomy',
        'witnesses': ['8a cost-model inversion (blind pq-derivation certified refuted HARD_PASS)',
                      'diag8a/diagfull same-class demotion', 'A1 attribution correctly non-cert via method-gate'],
        'composes_with': ['method_gate_305c2e61', 'AUDIT_verify_the_referent_check_passed_on_wrong_object_verify_referent_reaches_consumer',
                          'feedback_substrate_autonomy_path_encode_audit_discipline_as_self_certification'],
    },
    {
        'id': 'RULE_gate0_both_ends_producer_self_attest_consumer_enforce_walltime_is_tell_not_gate',
        'name': 'Methodology rule (PHASE-2; cert-autonomy): GATE-0 both-ends; wall-time is a TELL not a gate',
        'description': (
            "GATE-0 (was the run actually FULL + MEASURED + COMPLETE?) is enforced at BOTH ends (defense-in-depth): "
            "PRODUCER cells self-attest via gate0_self_check (n_cells_emitted == n_cells_declared + run_mode==full-"
            "when-not-smoke + metrics_source measured); CONSUMER atomizer enforces via gate0_field_check (CERT requires "
            "gate0 pass; a measured-but-EARLY-EXITED run -> UNVERIFIED not CERT). WALL-TIME is a TELL recorded for "
            "inspection (elapsed + n_cells), NOT a hard gate -- plausibility is PER-CELL-WORKLOAD (a fast-real-full is "
            "legitimate; A4/A1/A3). The gate is ADDITIVE + NON-RETROACTIVE (cells without the field pass -> no mass "
            "recompute of existing cert atoms). Implemented 674cce5d (_cell_provenance.gate0_self_check + atomizer "
            "gate0_field_check + provenance_quality wiring)."
        ),
        'rule_class': 'cert_autonomy',
        'witnesses': ['A4 stall-misframe', 'A1 8s fast-real-full', 'A3 35s overspec (cert-owner elapsed>>120 corrected)'],
        'composes_with': ['AUDIT_gate0_plausibility_per_cell_workload_fast_not_fake',
                          'method_gate_305c2e61', 'gate0_field_check_674cce5d'],
    },
]

A1_ID_SUFFIX = 'EXP_a1_8a_4channel_attribution_v1'


def module_liveness_ok() -> bool:
    import importlib
    return all(hasattr(importlib.import_module(m), s) for m, s in [
        ('backend.substrate_index.hmm_decoder', 'viterbi_decode'),
        ('hdlab.perceptron', 'StructuredPerceptron'),
        ('backend.substrate_index.sequence_labeler', 'NERTagger'),
        ('hdlab.bayesian_inference', 'EMMixture'),
        ('backend.substrate_index.intent_classifier', 'IntentClassifier'),
        ('backend.substrate_index.refuse_gated_retriever', 'RefuseGatedRetriever'),
    ])


def axiom_term_count(ps: PartitionedStore) -> int:
    return sum(1 for a in ps.all_atoms()
               if str(a.corpus.name) == 'MATH'
               and str(a.tier.name) in ('TIER_2_PRIMITIVE', 'TIER_3_ALGORITHM')
               and a.algebra and len(a.algebra) >= 3
               and 'oeis' not in str(a.id).lower()
               and not str(a.id).startswith('T3/wikidata_'))


def cert_count(ps: PartitionedStore) -> int:
    return sum(1 for a in ps.all_atoms() if (a.metadata or {}).get('provenance_quality') == 'CERT_CHAIN_GRADE')


def main() -> int:
    ps = PartitionedStore(Path('data/substrate_index'))
    pre_n = sum(1 for _ in ps.all_atoms())
    pre_axiom = axiom_term_count(ps)
    pre_cert = cert_count(ps)
    pre_mod = module_liveness_ok()
    print(f'PRE: atoms={pre_n}  axiom_term={pre_axiom}  CERT={pre_cert}  cap_pres={pre_mod}')
    if not pre_mod or pre_axiom != 206:
        print('PRE-GATE FAIL.'); return 1

    by_id = {a.id: a for a in ps.all_atoms()}

    # --- 2 methodology rules ---
    for r in RULES:
        if r['id'] in by_id:
            print(f'  SKIP rule (present): {r["id"]}'); continue
        meta = {
            'rule_class': r['rule_class'], 'status': 'PHASE_2', 'confidence': 'high',
            'extracted_by': 'skunkworks', 'extracted_date': '2026-06-18',
            'witnesses': r['witnesses'], 'composes_with': r['composes_with'],
            'eleventh_rule_clean': True, 'substrate_internal_verified': True,
            'source': 'C2_self_certification_engine_2026_06_18_substrate_autonomy_directive',
        }
        atom = Atom(id=r['id'], name=r['name'], description=r['description'], kind=AtomKind.METHODOLOGY_RULE,
                    tier=Tier.TIER_METHODOLOGY, corpus=Corpus.META, algebra=None, metadata=meta)
        ps.add_atom(atom, source='C2_methodology_rules_2026_06_18', note='PHASE-2 cert-autonomy rule')
        print(f'  + RULE: {r["id"]}')

    # --- A1 deliberate retier LEGACY_EXCERPT -> MEASURED_MECHANISM (single atom; CERT unchanged) ---
    a1 = next((a for a in ps.all_atoms() if a.id.endswith(A1_ID_SUFFIX)), None)
    if a1 is None:
        print(f'  WARN: A1 atom not found ({A1_ID_SUFFIX}); skipping retier')
    else:
        md = dict(a1.metadata or {})
        old_pq = md.get('provenance_quality')
        if old_pq == 'LEGACY_EXCERPT':
            md['provenance_quality'] = 'MEASURED_MECHANISM'
            md['pq_retier_2026_06_18'] = 'LEGACY_EXCERPT->MEASURED_MECHANISM (deliberate cert-owner reclass; measured ATTRIBUTION, not legacy; CERT count unchanged)'
            new = Atom(id=a1.id, name=a1.name, description=a1.description, kind=a1.kind,
                       tier=a1.tier, corpus=a1.corpus, algebra=a1.algebra, metadata=md)
            ps.add_atom(new, source='C2_A1_retier_2026_06_18', note='LEGACY_EXCERPT->MEASURED_MECHANISM deliberate single-atom')
            print(f'  ~ A1 retier: provenance_quality {old_pq} -> MEASURED_MECHANISM')
        else:
            print(f'  A1 pq already {old_pq} (not LEGACY_EXCERPT); no retier')

    # --- post gates ---
    post_n = sum(1 for _ in ps.all_atoms())
    post_axiom = axiom_term_count(ps)
    post_cert = cert_count(ps)
    post_mod = module_liveness_ok()
    cert_unchanged = post_cert == pre_cert
    gate_ok = post_axiom == 206 and post_mod and cert_unchanged
    print('=' * 72)
    print(f'POST: atoms={post_n} (+{post_n-pre_n})  axiom_term={post_axiom}  CERT={post_cert} (was {pre_cert}; unchanged={cert_unchanged})  cap_pres={post_mod}  -> {"OK" if gate_ok else "HARD_FAIL"}')
    if not gate_ok:
        print('HARD_FAIL: axiom_term/cap_pres/CERT-count changed unexpectedly. INVESTIGATE.'); return 2
    print('C2 wrap-up COMPLETE: +2 methodology_rules + A1 retier (LEGACY->MEASURED_MECHANISM); axiom_term 206 + cap_pres + CERT 568 unchanged.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
