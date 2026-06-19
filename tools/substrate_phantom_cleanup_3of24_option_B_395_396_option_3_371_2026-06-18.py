"""3/24 cert-hygiene phantom cleanup (Skunkworks cert-call 2026-06-18: investigate-first; B-for-395/396, 3-for-371).

Three CAPABILITY atoms carry a current_best_solution that does NOT resolve to any atom (layer-3 value-RESOLVES
phantom, surfaced by the mining-script enhancement). Investigation (Exp-Dev) -> evidence-tier per phantom -> resolution:

  PP-395_svamp_role_asymmetry  current_best 'math::T3/discriminative_perceptron_with_role_features' -> NO ATOM.
    Variant separately MEASURED but MIDDLE_BAND/LEGACY_EXCERPT (T3/EXP_svamp_role_asymmetry_cpu_v1 + v2 SMOKE) -> NOT cert
    -> rules out Option A. Parent 'math::T3/discriminative_perceptron' RESOLVES + was measured ON THIS capability
    (history: 0.2867 SVAMP base). => OPTION B: current_best -> parent (resolving, measured); variant -> build-candidate.

  PP-396_svamp_learned_selector  current_best 'math::T3/discriminative_perceptron_with_learned_selector' -> NO ATOM.
    Variant MEASURED but MIDDLE_BAND/LEGACY_EXCERPT (T3/EXP_svamp_learned_selector_cpu_v1; +0.37pp marginal) -> NOT cert.
    Parent RESOLVES + measured ON THIS capability (history: 0.363 heuristic base). => OPTION B: current_best -> parent.

  RETRIEVAL_reasoning_routing_pp371  current_best 'T2/prototype_bundle_cleanup' -> NO ATOM. 0.967 real but
    LEGACY_EXCERPT (corroborated T3/EXP_reasoning_routing_oracle_cpu_v1 PASS) + solution-atom never created; the only
    resolving history atom 'T2/cleanup' is the SUPERSEDED baseline (NOT current-best-grade). => OPTION 3: current_best
    -> None + annotate + build-candidate. PP-371_reasoning_routing stays None (no back-fill).

For every resolution: the new current_best either RESOLVES (parent, value-RESOLVES lesson applied FORWARD) or is None.
The phantom solution_atom_id in each 'current' history entry is set to None + the knowledge preserved in replacement_reason
(annotate step; nothing lost). The non-cert specialized/bundle method is filed as a build-candidate via a metadata key.

A5-safe: per-record snapshot before mutation; POST-gate axiom_term==206 + cap_pres 6/6 + CERT unchanged (CAPABILITY atoms
-> no cert delta) + new current_best RESOLVES-or-None readback. frozen Atom -> dataclasses.replace. DEFAULT --dry-run
(snapshot + planned mutations + gate-preview for landed-verify); --apply (mutate + post-gate + readback). 11th-rule
deterministic; gold-independent (Store-internal hygiene). ASCII.
"""
from __future__ import annotations
import argparse
import dataclasses
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path('.').resolve()))

PARENT = 'math::T3/discriminative_perceptron'
TS = '2026-06-18'

# resolution plan keyed by atom id
PLAN = {
    'PP-395_svamp_role_asymmetry': dict(
        option='B', new_current_best=PARENT,
        phantom_value='math::T3/discriminative_perceptron_with_role_features',
        variant='role-asymmetry features (target-aligned operand selection + subject/object/transfer-direction)',
        variant_metric='accuracy 0.3633 (+7.67pp vs base 0.2867)',
        variant_evidence='T3/EXP_svamp_role_asymmetry_cpu_v1 (MIDDLE_BAND/LEGACY_EXCERPT) + _v2 (MIDDLE_BAND/SMOKE_ONLY/ARCHIVE)',
        parent_measured_on_cap='history superseded entry: parent discriminative_perceptron measured 0.2867 SVAMP base (PP-377 SVAMP baseline)',
        build_candidate='create math::T3/discriminative_perceptron_with_role_features as a cert-grade specialized atom (gated on a STRUCTURED-cert SVAMP role-asymmetry measurement); only then promote current_best to it',
    ),
    'PP-396_svamp_learned_selector': dict(
        option='B', new_current_best=PARENT,
        phantom_value='math::T3/discriminative_perceptron_with_learned_selector',
        variant='learned operand-pair selector (selector-pair-acc 0.6457)',
        variant_metric='accuracy 0.3667 (+0.37pp vs heuristic 0.363; marginal)',
        variant_evidence='T3/EXP_svamp_learned_selector_cpu_v1 (MIDDLE_BAND/LEGACY_EXCERPT)',
        parent_measured_on_cap='history superseded entry: parent discriminative_perceptron measured 0.363 heuristic base (PP-377 heuristic baseline)',
        build_candidate='create math::T3/discriminative_perceptron_with_learned_selector as a cert-grade specialized atom (gated on a STRUCTURED-cert measurement); marginal +0.37pp may not justify a current_best even then',
    ),
    'RETRIEVAL_reasoning_routing_pp371': dict(
        option='3', new_current_best=None,
        phantom_value='T2/prototype_bundle_cleanup',
        variant='prototype-bundle cleanup (substrate-as-classifier reasoning routing)',
        variant_metric='routing 0.967 + answer 0.892 Tier C',
        variant_evidence='corroborated by T3/EXP_reasoning_routing_oracle_cpu_v1 PASS + exp_dev_to_research_REASONING_ROUTING_PASS_2026-06-11; LEGACY_EXCERPT (headline-only, key_metrics empty)',
        parent_measured_on_cap='NONE current-best-grade: only resolving history atom T2/cleanup is the SUPERSEDED ~0.85 cosine baseline, not a current-best',
        build_candidate='create a prototype_bundle_cleanup solution atom (gated on a STRUCTURED-cert measurement: re-atomize EXP_reasoning_routing_oracle with structured key_metrics OR re-run as a proper cert experiment); current_best stays None until then',
    ),
    # PP-371_reasoning_routing: stays None (no back-fill); annotate only for findability.
    'PP-371_reasoning_routing': dict(
        option='3-partner', new_current_best=None,
        phantom_value=None,
        variant='partner capability of RETRIEVAL_reasoning_routing_pp371 (same 0.967 prototype-bundle-cleanup result)',
        variant_metric='n/a (already current_best=None)',
        variant_evidence='see RETRIEVAL_reasoning_routing_pp371 build-candidate',
        parent_measured_on_cap='n/a',
        build_candidate='no back-fill (Skunkworks: both stay None until the prototype_bundle_cleanup solution atom is properly created)',
    ),
}


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


def axiom_term_count(ps) -> int:
    return sum(1 for a in ps.all_atoms()
               if str(a.corpus.name) == 'MATH' and str(a.tier.name) in ('TIER_2_PRIMITIVE', 'TIER_3_ALGORITHM')
               and a.algebra and len(a.algebra) >= 3 and 'oeis' not in str(a.id).lower()
               and not str(a.id).startswith('T3/wikidata_'))


def cert_count(ps) -> int:
    return sum(1 for a in ps.all_atoms() if (a.metadata or {}).get('provenance_quality') == 'CERT_CHAIN_GRADE')


def _resolves(ps, value) -> bool:
    if value is None:
        return True  # None is a valid honest state
    ids = set()
    for a in ps.all_atoms():
        ids.add(a.id)
        try:
            ids.add(a.qualified_id)
        except Exception:
            pass
    return value in ids


def _annotate_history(history, plan):
    """Set the 'current' (replaced_date is None) phantom entry's solution_atom_id -> None + preserve knowledge in replacement_reason."""
    out = []
    for e in history:
        e = dict(e)
        if e.get('replaced_date') is None and e.get('solution_atom_id') == plan['phantom_value']:
            note = (f"[phantom-cleanup {TS} OPTION-{plan['option']}: the '{plan['phantom_value']}' specialization was MEASURED "
                    f"({plan['variant_metric']}; evidence {plan['variant_evidence']}) but NEVER atomized -> non-resolving "
                    f"current_best removed. current_best -> {plan['new_current_best'] or 'None'} "
                    f"({'resolving measured parent' if plan['new_current_best'] else 'honest None'}). "
                    f"build-candidate: {plan['build_candidate']}.]")
            prev = e.get('replacement_reason') or ''
            e['solution_atom_id'] = None
            e['status'] = 'measured_legacy_excerpt_not_atomized'
            e['replacement_reason'] = (prev + ' ' + note).strip()
        out.append(e)
    return tuple(out)


def _build_replacement(atom, plan, ps):
    md = dict(atom.metadata or {})
    md['phantom_cleanup_2026_06_18'] = {
        'option': plan['option'],
        'phantom_value_removed': plan['phantom_value'],
        'new_current_best': plan['new_current_best'],
        'variant': plan['variant'],
        'variant_metric': plan['variant_metric'],
        'variant_evidence': plan['variant_evidence'],
        'parent_measured_on_capability': plan['parent_measured_on_cap'],
        'build_candidate': plan['build_candidate'],
        'ruling': 'Skunkworks 3-phantom cert-call investigate-first 2026-06-18 (B for 395/396 parent-measured + variant-LEGACY_EXCERPT; Option 3 for 371 no current-best-grade parent)',
        'applied_by': 'exp_dev',
    }
    new_history = _annotate_history(atom.solution_history or (), plan) if plan['phantom_value'] else atom.solution_history
    return dataclasses.replace(atom, current_best_solution=plan['new_current_best'],
                               solution_history=new_history, metadata=md)


def _get_concept_store(ps):
    from backend.substrate_index.schema import Corpus
    return ps._store_for(Corpus.CONCEPT)


def _save_with_retry(cstore, attempts=12) -> bool:
    from backend.substrate_index.schema import save_atoms
    for attempt in range(attempts):
        try:
            save_atoms(list(cstore._by_id.values()), cstore.atoms_path)
            return True
        except PermissionError:
            time.sleep(0.3 * (attempt + 1))
    return False


def snapshot(ps):
    rows = {}
    for a in ps.all_atoms():
        if a.id in PLAN:
            rows[a.id] = dict(current_best=a.current_best_solution,
                              n_history=len(a.solution_history or ()),
                              md_keys=sorted((a.metadata or {}).keys()))
    return rows


def dry_run() -> int:
    from backend.substrate_index.partition import PartitionedStore
    ps = PartitionedStore(Path('data/substrate_index'))
    pre_axiom = axiom_term_count(ps); pre_mod = module_liveness_ok(); pre_cert = cert_count(ps)
    snap = snapshot(ps)
    print('=' * 78)
    print('3/24 PHANTOM CLEANUP -- DRY-RUN (no mutation) for Skunkworks landed-verify (cert-call applied)')
    print('=' * 78)
    print(f"SNAPSHOT: axiom_term={pre_axiom} (206) | cap_pres={pre_mod} (6/6) | CERT={pre_cert}")
    for aid, plan in PLAN.items():
        s = snap.get(aid)
        if s is None:
            print(f"  !! {aid}: NOT FOUND in Store"); continue
        nb = plan['new_current_best']
        resolves = _resolves(ps, nb)
        print('-' * 78)
        print(f"  {aid}  [OPTION {plan['option']}]")
        print(f"    current_best: {s['current_best']!r}  ->  {nb!r}  (new RESOLVES-or-None: {resolves})")
        print(f"    evidence-tier: {plan['variant_metric']} | {plan['variant_evidence']}")
        print(f"    parent-measured-on-cap: {plan['parent_measured_on_cap']}")
        print(f"    build-candidate: {plan['build_candidate'][:90]}...")
        if not resolves:
            print(f"    !! WOULD-FAIL: new current_best {nb!r} does not resolve")
    print('-' * 78)
    print('POST-gate on --apply: axiom_term==206 + cap_pres 6/6 + CERT unchanged + every new current_best RESOLVES-or-None (readback).')
    print('=' * 78)
    return 0


def apply_run() -> int:
    from backend.substrate_index.partition import PartitionedStore
    from backend.substrate_index.store import ChangeEvent
    ps = PartitionedStore(Path('data/substrate_index'))
    pre_axiom = axiom_term_count(ps); pre_mod = module_liveness_ok(); pre_cert = cert_count(ps)
    pre_atoms = len(list(ps.all_atoms()))
    snap = snapshot(ps)
    print(f"PRE: atoms={pre_atoms} axiom_term={pre_axiom} cap_pres={pre_mod} CERT={pre_cert}")
    if not pre_mod or pre_axiom != 206:
        print('PRE-GATE FAIL. Halt.'); return 1
    cstore = _get_concept_store(ps)
    changed = []
    for aid, plan in PLAN.items():
        atom = cstore._by_id.get(aid)
        if atom is None:
            print(f"  !! {aid} not in CONCEPT store -- skip"); continue
        new_atom = _build_replacement(atom, plan, ps)
        if not _resolves(ps, new_atom.current_best_solution):
            print(f"  HARD_FAIL: {aid} new current_best {new_atom.current_best_solution!r} does not resolve. Halt (no save)."); return 2
        cstore._index_atom(new_atom)   # in-place update (same id/corpus/tier -> idempotent set membership)
        changed.append((aid, plan))
    if not _save_with_retry(cstore):
        print('HARD_FAIL: os.replace race on atoms flush.'); return 3
    # audit
    for aid, plan in changed:
        cstore._append_audit(ChangeEvent(ts=time.time(), op='update_atom', target=aid,
                                         note=f"phantom-cleanup option-{plan['option']} current_best->{plan['new_current_best']}",
                                         source='exp_dev_phantom_cleanup_3of24_2026-06-18'))
    # POST readback (fresh load)
    ps3 = PartitionedStore(Path('data/substrate_index'))
    post_axiom = axiom_term_count(ps3); post_mod = module_liveness_ok(); post_cert = cert_count(ps3)
    post_atoms = len(list(ps3.all_atoms()))
    by_id = {a.id: a for a in ps3.all_atoms()}
    all_resolve = True
    print('-' * 78)
    for aid, plan in changed:
        a = by_id[aid]
        r = _resolves(ps3, a.current_best_solution)
        all_resolve = all_resolve and r
        print(f"  {aid}: current_best={a.current_best_solution!r} RESOLVES-or-None={r} | annotation_present={'phantom_cleanup_2026_06_18' in (a.metadata or {})}")
    gate_ok = (post_axiom == 206 and post_mod and post_cert == pre_cert and post_atoms == pre_atoms and all_resolve)
    print('-' * 78)
    print(f"POST: atoms={post_atoms} (delta {post_atoms-pre_atoms}; MUST be 0) axiom_term={post_axiom} cap_pres={post_mod} "
          f"CERT={post_cert} (unchanged from {pre_cert}) all_current_best_resolve_or_none={all_resolve}")
    if not gate_ok:
        print('HARD_FAIL: post-gate failed.'); return 4
    print('=' * 78)
    print(f"PHANTOM CLEANUP APPLY complete: {len(changed)} atoms updated | 0 phantom current_bests remain (in these 3/24) | "
          f"axiom 206 | cap_pres 6/6 | CERT {post_cert} unchanged | 0 new atoms")
    print('  Now: re-run scour_capability_optimality (layer-3) -> confirm phantoms=0; route landed-verify to Skunkworks.')
    print('=' * 78)
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--apply', action='store_true')
    args = ap.parse_args()
    return apply_run() if args.apply else dry_run()


if __name__ == '__main__':
    raise SystemExit(main())
