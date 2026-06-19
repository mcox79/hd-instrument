"""Remove the 3 dangling phantom SUPERSEDES edges (completion of the 3/24 phantom cleanup; Director ACCEPT 2026-06-19).

The invariant-check (Skunkworks v1.x) found 3 phantom typed-edges = SUPERSEDES edges whose SOURCE is a never-existed
suffixed-id:
  T3/discriminative_perceptron_with_role_features    --SUPERSEDES--> T3/discriminative_perceptron        [MATH]
  T3/discriminative_perceptron_with_learned_selector --SUPERSEDES--> T3/discriminative_perceptron        [MATH]
  PP-MATH_WK_LEX_FAMILY                              --SUPERSEDES--> math::T3/discriminative_perceptron  [CONCEPT]

Provenance (Exp-Dev trace): the first two SOURCEs are the PP-395/396 phantom current_best suffixed-ids (the 3/24 cleanup
nulled the FIELD; these orphaned SUPERSEDES edges are the edge-residue). The supersession is INVALID -- the superseder
never existed as an atom + the Option-B cleanup established the base discriminative_perceptron IS the current_best (the
suffixed variant was MIDDLE_BAND/LEGACY_EXCERPT, not a cert-grade superseder). PP-MATH_WK_LEX_FAMILY = a 3rd dangling
SUPERSEDES source (removed atom), same class. ref-safe (SUPERSEDES-from-a-phantom is not load-bearing).

Finds the phantom-source SUPERSEDES edges DYNAMICALLY (any SUPERSEDES whose SOURCE does not resolve to an atom), so it
removes exactly the dangling ones. DEFAULT --dry-run (locate + confirm phantom-source + snapshot). --apply: remove via the
Store's remove_relation (auto-flush + audit) + post-gate (axiom 206 / cap_pres 6/6 / CERT 572 unchanged / 0 atom delta /
the targeted edges GONE / 0 phantom SUPERSEDES remain). 11th-rule deterministic. ASCII. RUN --apply only on Skunkworks confirm.
"""
from __future__ import annotations
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path('.').resolve()))
from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import RelationType


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


def _resolvable_ids(ps):
    ids = set()
    for a in ps.all_atoms():
        ids.add(a.id)
        try:
            ids.add(a.qualified_id)
        except Exception:
            pass
    bare = {i.split('::')[-1] for i in ids}
    return ids, bare


def find_phantom_supersedes(ps):
    """Return [(corpus_obj, src, rel_str, tgt)] for SUPERSEDES edges whose SOURCE does not resolve to any atom."""
    ids, bare = _resolvable_ids(ps)
    def resolves(x):
        return x in ids or x.split('::')[-1] in bare
    out = []
    for cname, store in ps._stores.items():
        for (s, rt, t) in store._all_relations:
            if rt == RelationType.SUPERSEDES.value and not resolves(s):
                out.append((cname, s, rt, t))
    return out


def dry_run() -> int:
    ps = PartitionedStore(Path('data/substrate_index'))
    found = find_phantom_supersedes(ps)
    print('=' * 78)
    print('REMOVE 3 PHANTOM SUPERSEDES EDGES -- DRY-RUN (no mutation)')
    print('=' * 78)
    print(f"SNAPSHOT: axiom_term={axiom_term_count(ps)} (206) | cap_pres={module_liveness_ok()} (6/6) | CERT={cert_count(ps)} (572)")
    print(f"phantom-source SUPERSEDES edges found: {len(found)}")
    for (cname, s, rt, t) in found:
        cn = cname.name if hasattr(cname, 'name') else str(cname)
        print(f"  [{cn}] {s}  --{rt}-->  {t}   (SOURCE phantom -> remove)")
    print('--- gates on --apply ---')
    print('  remove_relation per edge (auto-flush + audit) | POST: axiom 206 + cap_pres 6/6 + CERT 572 unchanged + 0 atom delta + 0 phantom-SUPERSEDES remain')
    print('=' * 78)
    print('DRY-RUN complete. Awaiting Skunkworks confirm before --apply (cert-owner gate; Director ACCEPTED).')
    return 0


def apply_run() -> int:
    ps = PartitionedStore(Path('data/substrate_index'))
    pre_axiom = axiom_term_count(ps); pre_mod = module_liveness_ok(); pre_cert = cert_count(ps)
    pre_atoms = len(list(ps.all_atoms()))
    found = find_phantom_supersedes(ps)
    print(f"PRE: atoms={pre_atoms} axiom_term={pre_axiom} cap_pres={pre_mod} CERT={pre_cert} | phantom-SUPERSEDES={len(found)}")
    if not pre_mod or pre_axiom != 206:
        print('PRE-GATE FAIL. Halt.'); return 1
    removed = 0
    for (cname, s, rt, t) in found:
        store = ps._stores[cname]
        if store.remove_relation(s, RelationType.SUPERSEDES, t,
                                 source='exp_dev_phantom_edge_cleanup_2026-06-19',
                                 note='dangling SUPERSEDES from never-existed source (3/24 cleanup edge-residue; supersession INVALID)'):
            removed += 1
            cn = cname.name if hasattr(cname, 'name') else str(cname)
            print(f"  removed: [{cn}] {s} --SUPERSEDES--> {t}")
    # readback
    ps3 = PartitionedStore(Path('data/substrate_index'))
    post_axiom = axiom_term_count(ps3); post_mod = module_liveness_ok(); post_cert = cert_count(ps3)
    post_atoms = len(list(ps3.all_atoms()))
    remaining = find_phantom_supersedes(ps3)
    gate_ok = (post_axiom == 206 and post_mod and post_cert == pre_cert
               and post_atoms == pre_atoms and len(remaining) == 0 and removed == len(found))
    print(f"POST: atoms={post_atoms} (delta {post_atoms-pre_atoms}; MUST be 0) axiom_term={post_axiom} cap_pres={post_mod} "
          f"CERT={post_cert} (unchanged from {pre_cert}) | removed={removed} phantom-SUPERSEDES-remaining={len(remaining)}")
    if not gate_ok:
        print('HARD_FAIL: post-gate failed.'); return 2
    print('=' * 78)
    print(f"PHANTOM-EDGE CLEANUP complete: removed {removed} dangling SUPERSEDES edges | 0 phantom-SUPERSEDES remain | "
          f"axiom 206 | cap_pres 6/6 | CERT {post_cert} unchanged | 0 atom delta. 3/24 cleanup now complete at the EDGE layer.")
    print('=' * 78)
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--apply', action='store_true')
    args = ap.parse_args()
    return apply_run() if args.apply else dry_run()


if __name__ == '__main__':
    raise SystemExit(main())
