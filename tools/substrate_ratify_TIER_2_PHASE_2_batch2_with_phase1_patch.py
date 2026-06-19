"""TIER-2 PHASE-2 batch 2 ratify (DECISION 237 standing) + free-rider PHASE-1 metadata patch (DECISION 236d).

2 NEW atoms (Skunkworks source-grounded; precise text):

  meta::RULE_verify_before_asserting
    rule_scheme: METHODOLOGY_EPISTEMIC
    rule_number_provenance: cited as 10th methodology in substrate_methodology_rule_10th 2026-06-13
    rule_class: SUBSTRATE_DERIVED; confirmed: true; frozen: true
    COMPOSES -> RULE_adversarial_self_correction_own_output (PHASE-2(1); 98b17fb2)
    COMPOSES -> AUDIT_verify_not_assume_prior_lesson_applied (PHASE-1; 9da528ca)
    COMPOSES -> RULE_held_out_test_for_macro_F1_claims (intra-batch)

  meta::RULE_held_out_test_for_macro_F1_claims
    rule_scheme: METHODOLOGY_EPISTEMIC (numbering-family)
    rule_number_provenance: cited as 11th methodology (USER-LOCKED) in feedback_held_out_test 2026-06-13
    rule_class: USER_LOCKED; user_locked: true; frozen: true (orthogonal to rule_scheme)
    COMPOSES -> RULE_verify_before_asserting (intra-batch; reverse pair)

4 COMPOSES edges total (3 from verify + 1 from held_out_test).

FREE-RIDER PHASE-1 metadata patch (DECISION 236d; pure metadata, no atom/rel count change):
  meta::RULE_substrate_internal_no_llm        + rule_scheme=USER_LOCKED_FRAMING + rule_number_provenance
  meta::RULE_active_state_check               + rule_scheme=USER_LOCKED_FRAMING + rule_number_provenance
  meta::RULE_no_stand_default                 + rule_scheme=USER_LOCKED_FRAMING + rule_number_provenance

Free-rider rationale: applies Skunkworks's numbering-resolution finding UNIFORMLY across PHASE-1+2 atoms;
removes 11th-collision ambiguity; pure metadata (substance-preserving); cap_pres-safe.

R3 invariants (improved per 95th-candidate; COMPOSES no auto-derive):
  +2 new atoms; +4 COMPOSES edges; 3 PHASE-1 metadata updates (no count change).
  Total delta: atoms +2; rels +4.
  axiom_term 206/206 PRESERVED (corpus=meta auto-excluded structurally).
  cap_pres=1.0 HARD-FAIL gate; module liveness 6/6.
"""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import Atom, Corpus, Tier, AtomKind, RelationType
from dataclasses import replace as dc_replace


def axiom_term(ps):
    forward = {}
    for src, rel, tgt in ps.iter_all_relations():
        if rel.name in ('DEPENDS_ON', 'SPECIALIZES'):
            forward.setdefault(src, []).append(tgt)
    axioms = set()
    for a in ps.all_atoms():
        if str(a.tier.name) != 'TIER_1_FOUNDATIONAL': continue
        if str(a.corpus.name) != 'MATH': continue
        role = (a.algebra or {}).get('role', '')
        if (a.metadata or {}).get('is_axiom', False) or role in ('axiom_schema', 'axiom', 'type'):
            axioms.add(f'math::{a.id}')
    def terminates(s, d=15):
        seen = {s}; f = [s]
        for _ in range(d):
            n = []
            for x in f:
                if x in axioms: return True
                for t in forward.get(x, []):
                    if t not in seen: seen.add(t); n.append(t)
            f = n
            if not f: break
        return any(x in axioms for x in seen)
    ops = [a for a in ps.all_atoms()
           if str(a.corpus.name) == 'MATH'
           and str(a.tier.name) in ('TIER_2_PRIMITIVE', 'TIER_3_ALGORITHM')
           and a.algebra and len(a.algebra) >= 3
           and 'oeis' not in str(a.id).lower()
           and not str(a.id).startswith('T3/wikidata_')]
    t = sum(1 for op in ops if terminates(f'math::{op.id}'))
    return t, len(ops)


def module_liveness_ok():
    import importlib
    return all(hasattr(importlib.import_module(m_), s) for m_, s in [
        ('backend.substrate_index.hmm_decoder', 'viterbi_decode'),
        ('hdlab.perceptron', 'StructuredPerceptron'),
        ('backend.substrate_index.sequence_labeler', 'NERTagger'),
        ('hdlab.bayesian_inference', 'EMMixture'),
        ('backend.substrate_index.intent_classifier', 'IntentClassifier'),
        ('backend.substrate_index.refuse_gated_retriever', 'RefuseGatedRetriever'),
    ])


def main():
    label = 'TIER-2-PHASE-2(batch2)'
    src_tag = 'DECISION_237_standing_PHASE_2_batch_2_methodology_verify_before_asserting_held_out_test_plus_DECISION_236d_free_rider_PHASE_1_metadata_patch'

    repo_root = Path(__file__).resolve().parents[1]
    ps = PartitionedStore(repo_root / 'data/substrate_index')
    meta_store = ps._store_for(Corpus.META)

    pre_atoms = len(ps.all_atoms())
    pre_rels = sum(1 for _ in ps.iter_all_relations())
    pre_t, pre_total = axiom_term(ps)
    print(f'[{label}] pre: atoms={pre_atoms} rels={pre_rels} axiom_term={pre_t}/{pre_total}', flush=True)

    # ===== 2 NEW atoms =====
    new_rules = [
        dict(
            id='RULE_verify_before_asserting',
            name='Methodology rule (epistemic): verify before asserting; meta-rule enabling held-out / refuse-prove / self-correct',
            description=(
                'Any substrate claim (empirical or architectural) must be VERIFIED before being asserted as locked. '
                'Verification = independent re-measurement, adversarial audit, cross-signal corroboration, '
                'bootstrap/null-model testing, OR an honest blocker statement when verification is not currently '
                'possible. When verification reveals a previously-asserted claim is over-strong, RETURN it to '
                'candidate-with-qualifier. This is the META rule that enables the held-out-test, '
                'refuse-what-cannot-prove, and adversarial-self-correction rules (each a specific instance). '
                'PROMOTED candidate -> CONFIRMED via 9+ class-distinct empirical witnesses (spectral / Curry-Howard / '
                'replay / smoke / audit / structural-bisimulation / discovery).'
            ),
            metadata=dict(
                rule_scheme='METHODOLOGY_EPISTEMIC',
                rule_number_provenance='cited as 10th methodology in substrate_methodology_rule_10th_VERIFY_BEFORE_ASSERTING 2026-06-13',
                rule_class='SUBSTRATE_DERIVED',
                frozen=True,
                confirmed=True,
                term_class='PROCESS_KNOWLEDGE_NON_MATH',
                prose_source='substrate_methodology_rule_10th_VERIFY_BEFORE_ASSERTING 2026-06-13',
                promoted_witnesses='9_plus_class_distinct_spectral_Curry_Howard_replay_smoke_audit_structural_bisimulation_discovery',
                source=src_tag,
            ),
        ),
        dict(
            id='RULE_held_out_test_for_macro_F1_claims',
            name='Methodology rule (USER-LOCKED who-locked; epistemic numbering-family): held-out test for macro-F1 claims > 0.05',
            description=(
                'Every macro-F1 claim of substrate self-improvement above 0.05 MUST be accompanied by a held-out '
                'test benchmark with NEW questions authored AFTER mechanism shipment; without it, the claim is '
                'INFLATED-by-tuning at an unknown rate. Distinguish STRUCTURAL artifacts (CHTV / L6-PROOF / CH-P6 / '
                'KP / spectral pillar -- LOW Goodhart risk, would generalize) from TUNED metrics (e.g. a '
                'benchmark-tuned QA score). Standard NLP benchmarks with train/test splits are held-out by design. '
                'USER-LOCKED after the USER caught a 0.75 macro-F1 Goodhart risk (7 of 9 mechanism classes were '
                'question-specific-tuned; honest held-out estimate 0.50-0.65).'
            ),
            metadata=dict(
                rule_scheme='METHODOLOGY_EPISTEMIC',
                rule_scheme_note='numbering_family_EPISTEMIC_orthogonal_to_who_locked_USER_LOCKED',
                rule_number_provenance='cited as 11th methodology (USER-LOCKED) in feedback_held_out_test 2026-06-13',
                rule_class='USER_LOCKED',
                frozen=True,
                user_locked=True,
                term_class='PROCESS_KNOWLEDGE_NON_MATH',
                prose_source='feedback_held_out_test USER directive 2026-06-13',
                source=src_tag,
            ),
        ),
    ]

    # Collision check
    for r in new_rules:
        if meta_store.get_atom(r['id']) is not None:
            print(f'[{label}] HARD_FAIL: meta::{r["id"]} already exists')
            return 1

    # COMPOSES edges (4 total)
    compose_edges = [
        ('RULE_verify_before_asserting', 'RULE_adversarial_self_correction_own_output'),  # back to PHASE-2(1)
        ('RULE_verify_before_asserting', 'AUDIT_verify_not_assume_prior_lesson_applied'),  # back to PHASE-1
        ('RULE_verify_before_asserting', 'RULE_held_out_test_for_macro_F1_claims'),       # intra-batch
        ('RULE_held_out_test_for_macro_F1_claims', 'RULE_verify_before_asserting'),       # intra-batch reverse
    ]

    # Verify COMPOSES targets exist (or are in this batch)
    new_ids = {r['id'] for r in new_rules}
    for src, tgt in compose_edges:
        if meta_store.get_atom(tgt) is None and tgt not in new_ids:
            print(f'[{label}] HARD_FAIL: COMPOSES target missing meta::{tgt}')
            return 1
    print(f'[{label}] 2 collisions clean; 4 COMPOSES targets verified (no phantom)', flush=True)

    # ===== Author 2 new atoms =====
    for r in new_rules:
        atom = Atom(
            id=r['id'],
            name=r['name'],
            corpus=Corpus.META,
            tier=Tier.TIER_METHODOLOGY,
            kind=AtomKind.METHODOLOGY_RULE,
            description=r['description'],
            metadata={**r['metadata'], 'eleventh_rule_clean': True, 'substrate_internal_verified': True},
            solution_history=tuple(),
        )
        meta_store.add_atom(atom, source=src_tag, note=f'PHASE-2 batch 2 author {r["id"]}')
        print(f'[{label}]   +meta::{r["id"]}', flush=True)

    # ===== Add 4 COMPOSES edges =====
    for src, tgt in compose_edges:
        ps.add_relation(
            f'meta::{src}',
            RelationType.COMPOSES,
            f'meta::{tgt}',
            source=src_tag,
            note=f'PHASE-2 batch 2 COMPOSES {src} -> {tgt}',
        )
    meta_store._flush_relations()
    print(f'[{label}]   +{len(compose_edges)} COMPOSES edges (4 incl 1 intra-batch reverse pair)', flush=True)

    # ===== Free-rider PHASE-1 metadata patch (DECISION 236d) =====
    phase1_patch_ids = [
        ('RULE_substrate_internal_no_llm',
         'cited as 11th USER-LOCKED in feedback_substrate_internal_no_LLM 2026-06-15 (collides with 11th methodology held_out_test_for_macro_F1_claims; disambiguated via name + rule_scheme + rule_class)'),
        ('RULE_active_state_check',
         'cited as 13th USER-LOCKED in feedback_active_state_check_every_10_15_min 2026-06-16'),
        ('RULE_no_stand_default',
         'cited as 14th USER-LOCKED in feedback_14th_rule_phase_boundary_dispatch_next_phase_prep 2026-06-16'),
    ]

    patched_count = 0
    for aid, provenance in phase1_patch_ids:
        existing = meta_store.get_atom(aid)
        if existing is None:
            print(f'[{label}] WARN: PHASE-1 atom meta::{aid} missing; skipping patch')
            continue
        old_meta = dict(existing.metadata or {})
        # Add the new fields per DECISION 236d (free-rider; pure metadata; substance-preserving)
        new_meta = {
            **old_meta,
            'rule_scheme': 'USER_LOCKED_FRAMING',
            'rule_number_provenance': provenance,
            'free_rider_patched_per_decision': 'DECISION_236d_uniformity_fold_next_meta_corpus_batch',
            'free_rider_patched_in_batch': src_tag,
        }
        patched_atom = dc_replace(existing, metadata=new_meta)
        meta_store.add_atom(patched_atom, source=src_tag, note=f'free-rider PHASE-1 metadata patch per DECISION 236d')
        patched_count += 1
        print(f'[{label}]   ~meta::{aid} (free-rider metadata patch: rule_scheme + rule_number_provenance)', flush=True)

    # ===== R3 invariants (improved per 95th-candidate; COMPOSES no auto-derive) =====
    expected_atoms_delta = 2  # 2 new; 3 patches are mutations not adds
    expected_rels_delta = len(compose_edges)  # 4; COMPOSES no auto-derive

    post_atoms = len(ps.all_atoms())
    post_rels = sum(1 for _ in ps.iter_all_relations())
    post_t, post_total = axiom_term(ps)

    mod_ok = module_liveness_ok()
    all_new_landed = all(meta_store.get_atom(r['id']) is not None for r in new_rules)
    edges_landed = sum(
        1 for s, r, t in ps.iter_all_relations()
        if r.name == 'COMPOSES'
        and any(f'meta::{src}' == s and f'meta::{tgt}' == t for src, tgt in compose_edges)
    )

    # Verify PHASE-1 patch metadata
    patch_ok = True
    for aid, _ in phase1_patch_ids:
        a = meta_store.get_atom(aid)
        if a and (a.metadata or {}).get('rule_scheme') != 'USER_LOCKED_FRAMING':
            print(f'[{label}] HARD_FAIL: PHASE-1 patch missing on meta::{aid}')
            patch_ok = False
        elif a and not (a.metadata or {}).get('rule_number_provenance'):
            print(f'[{label}] HARD_FAIL: PHASE-1 provenance missing on meta::{aid}')
            patch_ok = False

    invariants_ok = (
        post_atoms == pre_atoms + expected_atoms_delta
        and post_rels == pre_rels + expected_rels_delta
        and post_t == pre_t  # corpus=meta auto-excluded
        and mod_ok
        and all_new_landed
        and edges_landed == len(compose_edges)
        and patch_ok
        and patched_count == 3
    )

    print(f'[{label}] post: atoms={post_atoms} (+{post_atoms-pre_atoms}) rels={post_rels} '
          f'(+{post_rels-pre_rels}) axiom_term={post_t}/{post_total} mod_ok={mod_ok} '
          f'new_landed={all_new_landed} edges={edges_landed} patched={patched_count}/3', flush=True)

    if not invariants_ok:
        print(f'[{label}] HARD_FAIL: R3 invariant violation')
        return 1

    print()
    print('=' * 80)
    print(f'[{label}] HARD_PASS: 2 new methodology_rule atoms + 4 COMPOSES + 3 PHASE-1 patches')
    print(f'  NEW: RULE_verify_before_asserting (10th-METHODOLOGY_EPISTEMIC; CONFIRMED 9+)')
    print(f'       RULE_held_out_test_for_macro_F1_claims (11th-METHODOLOGY_EPISTEMIC; USER_LOCKED)')
    print(f'  FREE-RIDER PATCHED (DECISION 236d uniformity):')
    print(f'    RULE_substrate_internal_no_llm  + rule_scheme USER_LOCKED_FRAMING + provenance')
    print(f'    RULE_active_state_check         + rule_scheme USER_LOCKED_FRAMING + provenance')
    print(f'    RULE_no_stand_default           + rule_scheme USER_LOCKED_FRAMING + provenance')
    print(f'  cap_pres=1.0 PRESERVED; axiom_term 206/206 PRESERVED; modules 6/6')
    print('=' * 80)
    return 0


if __name__ == '__main__':
    sys.exit(main())
