"""Ratify C3 5-candidate per-candidate dispositions per Skunkworks rulings (2026-06-18).

Skunkworks's per-candidate rulings:
- cand1 METHOD-GATE-IN-pq-derivation: COMPOSE catch w/80 + ELEVATE forward-principle to
   METHODOLOGY_RULE (Skunkworks authors in C2; NOT new audit_lesson from Testbed)
- cand2 cert-tier-recompute-scope-violation: COMPOSE w/80 (1 witness; 2 symptoms 1 root)
- cand3 sync-delta-gating-wrong-referent: COMPOSE w/80 (1 witness; siblings 81/71/84/v5)
- cand4 atom-payload-vs-spec-completeness: NEW CANDIDATE (w=2; A5+A1; bears_on same aspect)
- cand5 VET'd-verdict-must-arrive-in-corpus: COMPOSE w/72 (1 witness; consumer-feed variant)

Execution:
- +1 NEW CANDIDATE atom: AUDIT_atom_payload_carries_what_cert_decision_referenced
- +3 witnesses to 80 (cand1 catch + cand2 + cand3): w 8 -> 11
- +1 witness to 72 (cand5)

Per-atom HARD-FAIL gate discipline.
"""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path('.').resolve()))

from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import Atom, AtomKind, Corpus, Tier


CAND4_SPEC = {
    'slug': 'atom_payload_carries_what_cert_decision_referenced',
    'name': 'Audit lesson (CANDIDATE; instance 93; verify): atom-payload-carries-what-cert-decision-referenced',
    'description': (
        "The atom's PAYLOAD must carry what the cert-decision referenced. Distinct from corpus-completeness "
        "(which is about the atom EXISTING in Store) and from verify-the-referent (which is about referent in "
        "general). Today witnesses: (A) A5 payload truncation -- Skunkworks's atomize-GO was conditional on "
        "readout-C1 strengthens-payload preserved; atom's key_metrics empty + metrics_headline truncated mid-"
        "sentence + strengthens metadata field empty; cert decision rested on payload content not actually "
        "queryable in atom (only on prereg/source files). Required Exp-Dev durable atomizer fix (1a32e892) + "
        "Skunkworks SCHEMA-VET PASS. (B) A1 attribution localization-truncation -- same metrics_headline mid-"
        "sentence cut at 'is the operati'; key_metrics initially empty; bears_on metadata empty (edge is cross-"
        "reference). Required Exp-Dev completeness fix (99b0975f). CANDIDATE: 2 witnesses (A5 + A1; bears_on "
        "empty is SAME metadata-truncation aspect present in both, NOT 3rd independent witness per Skunkworks "
        "ruling). Promote on 3rd distinct-cell witness. Composes verify-the-referent 80 + corpus-completeness "
        "72 + metric-mismatch 83 (the cert decision metric requires the payload to ACTUALLY CONTAIN what was "
        "ruled on)."
    ),
    'lesson_class': 'verify',
    'confirmed_or_candidate': 'CANDIDATE',
    'witnesses_count': 2,
    'instance_number': 93,
    'instance_number_provenance': (
        'Skunkworks 2026-06-18 C3 per-candidate ruling: NEW CANDIDATE (w=2; A5 + A1; bears_on same aspect not 3rd); '
        'promote on 3rd distinct-cell witness; distinct from corpus-completeness-72 (atom exists) and verify-the-'
        'referent-80 (referent general); specifically: atom PAYLOAD carries cert-decision-referenced content'
    ),
    'witnesses': [
        'A5 drosophila_2x2_ablation_preflight_v1 (2026-06-18 evening): Skunkworks atomize-GO conditional on strengthens-C1 readout payload (>=42x lift + 18 key_metrics) preserved; atom\'s key_metrics empty + metrics_headline truncated + strengthens metadata field empty; cert decision rested on payload not queryable; fixed via Exp-Dev durable atomizer fix 1a32e892 + Skunkworks SCHEMA-VET PASS + UPDATE-path APPLY',
        'A1 attribution 8a_4channel_v1 (2026-06-18 morning): Skunkworks A1 landed verify flagged 2 completeness gaps (bears_on edge MISSING + framing TRUNCATED); metrics_headline truncated mid-sentence at \'is the operati\'; key_metrics initially empty; bears_on metadata empty; fixed via Exp-Dev completeness fix 99b0975f (key_metrics 9 keys + bears_on RELATES edge to measured-8a)',
    ],
    'composes_with': [
        'AUDIT_verify_the_referent_check_passed_on_wrong_object_verify_referent_reaches_consumer',
        'AUDIT_audit_input_corpus_completeness_verify_before_output',
        'AUDIT_metric_mismatch_test_mechanism_on_its_claimed_benefit_switch_metrics_once_principled_pre_registered',
    ],
    'verify_the_referent_parent': 'AUDIT_verify_the_referent_check_passed_on_wrong_object_verify_referent_reaches_consumer',
}


def module_liveness_ok() -> bool:
    import importlib
    return all(
        hasattr(importlib.import_module(m), s)
        for m, s in [
            ('backend.substrate_index.hmm_decoder', 'viterbi_decode'),
            ('hdlab.perceptron', 'StructuredPerceptron'),
            ('backend.substrate_index.sequence_labeler', 'NERTagger'),
            ('hdlab.bayesian_inference', 'EMMixture'),
            ('backend.substrate_index.intent_classifier', 'IntentClassifier'),
            ('backend.substrate_index.refuse_gated_retriever', 'RefuseGatedRetriever'),
        ]
    )


def axiom_term_count(ps: PartitionedStore) -> int:
    atoms = list(ps.all_atoms())
    return sum(
        1 for a in atoms
        if str(a.corpus.name) == 'MATH'
        and str(a.tier.name) in ('TIER_2_PRIMITIVE', 'TIER_3_ALGORITHM')
        and a.algebra and len(a.algebra) >= 3
        and 'oeis' not in str(a.id).lower()
        and not str(a.id).startswith('T3/wikidata_')
    )


def build_cand4_atom(spec: dict) -> Atom:
    metadata = {
        'lesson_class': spec['lesson_class'],
        'confirmed_or_candidate': spec['confirmed_or_candidate'],
        'witnesses_count': spec['witnesses_count'],
        'witnesses': spec['witnesses'],
        'instance_number': spec['instance_number'],
        'instance_number_provenance': spec['instance_number_provenance'],
        'term_class': 'PROCESS_KNOWLEDGE_NON_MATH',
        'NOT_load_bearing_until_3_witnesses': True,
        'prose_source': 'testbed_to_skunkworks_C3_5_candidate_specs_for_per_candidate_ruling_2026-06-18.md + skunkworks_to_testbed_C3_per_candidate_rulings_2026-06-18.md',
        'eleventh_rule_clean': True,
        'substrate_internal_verified': True,
        'composes_with': spec['composes_with'],
        'verify_the_referent_family': True,
        'verify_the_referent_parent': spec['verify_the_referent_parent'],
        'source': 'C3_atom_payload_completeness_NEW_CANDIDATE_skunkworks_per_candidate_ruling_2026_06_18_amendment_3_compose_dont_proliferate_w_2_A5_A1_bears_on_same_aspect_not_3rd_witness_promote_on_3rd_distinct_cell',
    }
    return Atom(
        id=f"AUDIT_{spec['slug']}",
        name=spec['name'],
        description=spec['description'],
        kind=AtomKind.AUDIT_LESSON,
        tier=Tier.TIER_METHODOLOGY,
        corpus=Corpus.META,
        algebra=None,
        metadata=metadata,
    )


def add_witness_to_atom(ps: PartitionedStore, atom_id: str, new_witness: str, source: str) -> dict:
    """Add a witness to an existing audit_lesson atom (increments witnesses_count + appends to witnesses list)."""
    atoms = list(ps.all_atoms())
    target = next((a for a in atoms if str(a.id) == atom_id), None)
    if target is None:
        return {'status': 'NOT_FOUND', 'id': atom_id}

    new_md = dict(target.metadata or {})
    current_witnesses = list(new_md.get('witnesses', []))
    current_witnesses.append(new_witness)
    new_md['witnesses'] = current_witnesses
    old_count = new_md.get('witnesses_count', 0)
    new_md['witnesses_count'] = old_count + 1
    new_md.setdefault('witness_additions_log', []).append({
        'source': source,
        'witness': new_witness[:200],
        'old_count': old_count,
        'new_count': old_count + 1,
    })

    updated = Atom(
        id=target.id,
        name=target.name,
        description=target.description,
        kind=target.kind,
        tier=target.tier,
        corpus=target.corpus,
        algebra=target.algebra,
        metadata=new_md,
        aliases=target.aliases,
        concept_links=target.concept_links,
        complexity=target.complexity,
        current_best_solution=target.current_best_solution,
        equivalences=target.equivalences,
        serves_capability=target.serves_capability,
        signature=target.signature,
        solution_history=target.solution_history,
    )
    ps.add_atom(updated, source=source, note=f'witness add {old_count}->{old_count+1}')
    return {'status': 'WITNESS_ADDED', 'id': atom_id, 'old_count': old_count, 'new_count': old_count + 1}


WITNESS_ADDS_TO_80 = [
    {
        'source': 'C3_cand1_method_gate_in_pq_derivation_catch_compose_skunkworks_ruling_2026_06_18',
        'witness': '8a cost-model HARD_PASS inversion (2026-06-18): atomizer pq-derivation certified run_mode=full + n_seeds>=3 -> CERT_CHAIN_GRADE without checking metrics_source field; cost-model HARD_PASS got CERT_CHAIN_GRADE = INVERSION of measured HARD_FAIL; caught by Testbed 2nd-witness on A5-queryability APPLY (567 vs expected 566); verify the pq-derivation referent is metrics_source not just run_mode/n_seeds; fixed via Skunkworks Ruling-1 + Exp-Dev 305c2e61 (method-gate now STRUCTURAL in atomizer pq-derivation; cost-model can never auto-cert). Forward-principle elevated to METHODOLOGY_RULE (Skunkworks authors in C2). This witness is the CATCH only.',
    },
    {
        'source': 'C3_cand2_cert_tier_recompute_scope_violation_compose_skunkworks_ruling_2026_06_18',
        'witness': 'A5-queryability APPLY scope violation (2026-06-18): UPDATE-path re-ran full build_atom_spec when spec only asked for scoped {key_metrics, strengthens, content_hash} update; 2 symptoms (pq-recompute 296 atoms + edge-extraction +401 DEPENDS_ON) from 1 ROOT (build_atom_spec re-run); verify the operation\'s actual SCOPE not its name; fixed via Skunkworks Sharpened Ruling 1 + Exp-Dev 305c2e61 SCOPED update (touches only 3 fields; no build_atom_spec re-run).',
    },
    {
        'source': 'C3_cand3_sync_delta_gating_wrong_referent_compose_skunkworks_ruling_2026_06_18',
        'witness': 'hd_metrics_sync count-delta bug (2026-06-18): sync gated remote-to-local tar pull on GLOBAL count delta; local-OLD > remote-NEW = negative delta = silent SKIP; identical pattern to siblings 81/71/84/v5-monitor (count/proxy used for the actual referent file-set); same false-success class as queue_add-exit-0 / cron-substring / cost-model-cert / monitor-mtime; root cause of cert-coherence gap (refuse_gate + measured-8a never synced); fixed via 95f76878 file-set diff (same shape as v5 monitor).',
    },
]

WITNESS_ADD_TO_72 = {
    'source': 'C3_cand5_vetd_verdict_must_arrive_in_corpus_compose_skunkworks_ruling_2026_06_18',
    'witness': 'cert-coherence gap (2026-06-18): Skunkworks VET\'d 8a measured HARD_FAIL + refuse-gate NON_TEST verdicts from remote pastes; neither reached Store as atom (synced metrics.json absent until manual scp + corpus-completeness pull); substrate had stale smoke/cost-model representations of canonical-VET\'d findings; consumer-feed variant of corpus-completeness: VET\'d verdict must be STORE-RESIDENT not just VET\'d-in-note; fixed via Orchestrator corpus-completeness pull + Exp-Dev method-gate-aware atomize + SUPERSEDED_BY edges (8a cost-model -> measured; refuse-gate smoke -> NON_TEST).',
}


def main() -> int:
    store_dir = Path('data/substrate_index')
    ps = PartitionedStore(store_dir)

    pre_n = sum(1 for _ in ps.all_atoms())
    pre_axiom = axiom_term_count(ps)
    pre_mod = module_liveness_ok()
    print(f'PRE-RATIFY: atoms={pre_n}  axiom_term={pre_axiom}/{pre_axiom}  cap_pres(mod6/6)={pre_mod}')

    if not pre_mod or pre_axiom != 206:
        print('PRE-RATIFY GATE FAIL.')
        return 1

    # Step 1: Add NEW CANDIDATE atom (cand4)
    cand4_atom = build_cand4_atom(CAND4_SPEC)
    existing = {a.id for a in ps.all_atoms()}
    if cand4_atom.id in existing:
        print(f'  SKIP cand4 (already present): {cand4_atom.id}')
    else:
        ps.add_atom(cand4_atom, source='C3_cand4_atom_payload_NEW_CANDIDATE_skunkworks_ruling_2026_06_18', note='NEW CANDIDATE w=2 A5+A1')
        post_n = sum(1 for _ in ps.all_atoms())
        post_axiom = axiom_term_count(ps)
        post_mod = module_liveness_ok()
        gate_ok = post_axiom == 206 and post_mod
        print(f'  + CAND4 NEW CANDIDATE: {cand4_atom.id}')
        print(f'    atoms_now={post_n}  axiom_term={post_axiom}  cap_pres={post_mod}  -> {"OK" if gate_ok else "HARD_FAIL"}')
        if not gate_ok:
            return 2

    # Step 2: Add 3 witnesses to 80 (verify-the-referent parent)
    parent_80 = 'AUDIT_verify_the_referent_check_passed_on_wrong_object_verify_referent_reaches_consumer'
    print()
    print('Adding 3 witnesses to verify-the-referent parent (80):')
    for w in WITNESS_ADDS_TO_80:
        result = add_witness_to_atom(ps, parent_80, w['witness'], w['source'])
        print(f"  + {result['status']} {result.get('old_count','?')}->{result.get('new_count','?')}")
        post_axiom = axiom_term_count(ps)
        post_mod = module_liveness_ok()
        if post_axiom != 206 or not post_mod:
            print('  HARD_FAIL on witness add: halting.')
            return 3

    # Step 3: Add 1 witness to 72 (corpus-completeness)
    parent_72 = 'AUDIT_audit_input_corpus_completeness_verify_before_output'
    print()
    print('Adding 1 witness to corpus-completeness (72):')
    result = add_witness_to_atom(ps, parent_72, WITNESS_ADD_TO_72['witness'], WITNESS_ADD_TO_72['source'])
    print(f"  + {result['status']} {result.get('old_count','?')}->{result.get('new_count','?')}")
    post_axiom = axiom_term_count(ps)
    post_mod = module_liveness_ok()
    if post_axiom != 206 or not post_mod:
        print('  HARD_FAIL on witness add 72: halting.')
        return 4

    post_n = sum(1 for _ in ps.all_atoms())
    print()
    print('=' * 72)
    print(f'C3 RATIFY COMPLETE: +1 new CANDIDATE atom (cand4) + 3 witnesses to 80 + 1 witness to 72')
    print(f'  atoms {pre_n} -> {post_n} (+1)')
    print(f'  axiom_term 206/206 PRESERVED  cap_pres 6/6 PRESERVED')
    print(f'  Expected: AUDIT_LESSON 48 -> 49; parent 80 w=8 -> 11; parent 72 w+1')
    print('=' * 72)
    return 0


if __name__ == '__main__':
    sys.exit(main())
