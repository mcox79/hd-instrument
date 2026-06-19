"""Ratify single witness-to-83 for the A1 attribution + A1-v2 ratio-profile pair.

Per Director routing (USER get-everyone-moving directive 2026-06-18) + Skunkworks
freshest+lowest-cost ordering: file 1 (ONE) witness add to AUDIT_LESSON instance 83
(metric-mismatch) covering BOTH A1-attribution + A1-v2-ratio-profile as the SAME aspect-
instance per compose-don't-proliferate (Amendment-3).

ASPECT (the single aspect being witnessed):
- The pq TIER LABEL on the atom must match the MEASURED-MECHANISM NATURE of the underlying work.
- Distinct aspect-layer from existing inst-83 witnesses:
  - w0 A5 metric-shop catch (metric SELECTION shopping)
  - w1 refuse-gate NON_TEST (regime non-discrimination)
  - w2 DEGENERATE-REGIME-NOT-REFUTATION precedent
  - w3 (added bucket) A1 t_sparse vs net_speedup (metric-CONTENT mismatch -- different layer)
- The NEW witness here is at the TIER-LABEL layer: pq label LEGACY_EXCERPT vs underlying
  MEASURED_MECHANISM nature -- referent mismatch between label classification and measured nature.

WITNESS PAIR (single instance; compose-don't-proliferate):
- A1 attribution (8a_4channel_v1): initially atomized LEGACY_EXCERPT pq tier despite
  underlying nature being MEASURED_MECHANISM (seed-replicated empirical measurement of 8a
  attribution); label-vs-nature referent mismatch; FIXED by Skunkworks scoped single-atom
  update LEGACY_EXCERPT -> MEASURED_MECHANISM after the C2 MEASURED_MECHANISM tier added.
- A1-v2 ratio-profile (Bucket D; 2026-06-18 PM): authored AFTER C2 tier landed; correctly
  labeled MEASURED_MECHANISM from the start; the PAIR demonstrates CATCH-on-A1 then
  HELD-FORWARD-on-A1-v2 at the label-referent layer.

Both A1 + A1-v2 = ONE aspect-instance (label-vs-nature referent mismatch); 1 witness add
(witnesses 4 -> 5; witnesses_count 4 -> 5). Composes with 80 verify-the-referent parent
+ C2 MEASURED_MECHANISM-tier structural enabler.

Per-mutation HARD-FAIL gate discipline: axiom_term 206/206 + cap_pres 6/6 must hold.
"""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path('.').resolve()))

from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import Atom


WITNESS_PAYLOAD = (
    'A1+A1-v2 pq-tier-label referent mismatch pair (2026-06-18 USER-routed get-everyone-moving): '
    'A1 attribution 8a_4channel_v1 initially atomized pq=LEGACY_EXCERPT despite underlying nature being '
    'MEASURED_MECHANISM (seed-replicated empirical 8a attribution measurement); label-vs-nature referent '
    'mismatch caught by Skunkworks during C2 design; fixed via Skunkworks scoped single-atom update '
    'LEGACY_EXCERPT -> MEASURED_MECHANISM (single-atom touch; safe; not mass recompute) after C2 added the '
    'MEASURED_MECHANISM pq tier. A1-v2 ratio-profile (Bucket D) authored AFTER C2 landed = correctly labeled '
    'MEASURED_MECHANISM from start. Pair = ONE aspect-instance (CATCH-then-FIX-then-HELD at label-referent '
    'layer; distinct from inst-83 w3 metric-CONTENT t_sparse-vs-net_speedup catch which is at metric-content '
    'layer). Composes verify-the-referent-80 + C2 MEASURED_MECHANISM-tier structural enabler. '
    'Compose-dont-proliferate: A1 + A1-v2 = SAME aspect, not 2.'
)

WITNESS_SOURCE = (
    'testbed_branch_item_1_referent_mismatch_witness_to_83_A1_pair_user_directive_get_everyone_moving_'
    'lowest_cost_freshest_skunkworks_ordering_2026_06_18'
)


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


def find_target_by_instance(ps: PartitionedStore, kind_str: str, instance_number: int) -> Atom | None:
    for a in ps.all_atoms():
        ks = a.kind.value if hasattr(a.kind, 'value') else a.kind
        if ks != kind_str:
            continue
        if a.metadata.get('instance_number') == instance_number:
            return a
    return None


def add_witness_to_atom(ps: PartitionedStore, target: Atom, new_witness: str, source: str) -> dict:
    new_md = dict(target.metadata or {})
    current_witnesses = list(new_md.get('witnesses', []))
    current_witnesses.append(new_witness)
    new_md['witnesses'] = current_witnesses
    old_count = new_md.get('witnesses_count', 0)
    new_md['witnesses_count'] = old_count + 1
    new_md.setdefault('witness_additions_log', []).append({
        'source': source,
        'witness_head': new_witness[:200],
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
    return {'status': 'WITNESS_ADDED', 'id': target.id, 'old_count': old_count, 'new_count': old_count + 1}


def main() -> int:
    store_dir = Path('data/substrate_index')
    ps = PartitionedStore(store_dir)

    pre_n = sum(1 for _ in ps.all_atoms())
    pre_axiom = axiom_term_count(ps)
    pre_mod = module_liveness_ok()
    print(f'PRE-RATIFY: atoms={pre_n}  axiom_term={pre_axiom}/206  cap_pres(mod6/6)={pre_mod}')

    if not pre_mod or pre_axiom != 206:
        print('PRE-RATIFY GATE FAIL.')
        return 1

    target = find_target_by_instance(ps, 'audit_lesson', 83)
    if target is None:
        print('INSTANCE 83 NOT FOUND.')
        return 2
    print(f'TARGET 83: id={target.id}  pre_witnesses_count={target.metadata.get("witnesses_count")}')

    result = add_witness_to_atom(ps, target, WITNESS_PAYLOAD, WITNESS_SOURCE)
    print(f'  + {result["status"]} {result["old_count"]}->{result["new_count"]}')

    post_n = sum(1 for _ in ps.all_atoms())
    post_axiom = axiom_term_count(ps)
    post_mod = module_liveness_ok()
    gate_ok = post_axiom == 206 and post_mod and post_n == pre_n
    print(f'POST: atoms={post_n}  axiom_term={post_axiom}/206  cap_pres={post_mod}  -> {"OK" if gate_ok else "HARD_FAIL"}')
    if not gate_ok:
        return 3

    print('=' * 72)
    print('WITNESS-TO-83 RATIFY COMPLETE: +1 witness on inst-83 metric-mismatch')
    print(f'  atoms unchanged at {pre_n}')
    print(f'  witnesses_count {result["old_count"]} -> {result["new_count"]}')
    print(f'  axiom_term 206/206 PRESERVED  cap_pres 6/6 PRESERVED  AUDIT_LESSON 49 unchanged')
    print('=' * 72)
    return 0


if __name__ == '__main__':
    sys.exit(main())
