"""Wire 237d <-> 92nd dual edge (Skunkworks deferred per recursive 92nd rule when 92nd not in-store).

Both atoms now in-store (92nd at 52789caf; 237d at f16bb7ae); the dual relationship
(DUAL of phantom-dep-false-positive vs drop-criterion-false-negative; same provenance-
integrity family opposite direction) is well-defined in both atoms' descriptions.

Adding 2 COMPOSES edges (bidirectional dual pair):
  AUDIT_atomizer_drop_criterion_loses_older_schema_records COMPOSES -> AUDIT_phantom_dep_pre_ratify
  AUDIT_phantom_dep_pre_ratify COMPOSES -> AUDIT_atomizer_drop_criterion_loses_older_schema_records

Per 12th never-passive + 14th no-stand-default: forward-execute the deferred follow-up
(Skunkworks said they'd do it after 92nd lands; both atoms have been in-store for hours).
"""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import Corpus, RelationType


def main():
    label = 'AUDIT-LESSON-DUAL-EDGE'
    src_tag = 'audit_lesson_237d_92nd_dual_edge_DUAL_phantom_dep_false_positive_atomizer_drop_false_negative_provenance_integrity_family'
    repo_root = Path(__file__).resolve().parents[1]
    ps = PartitionedStore(repo_root / 'data/substrate_index')
    meta_store = ps._store_for(Corpus.META)

    pre_rels = sum(1 for _ in ps.iter_all_relations())
    print(f'[{label}] pre: rels={pre_rels}', flush=True)

    src_qid = 'meta::AUDIT_atomizer_drop_criterion_loses_older_schema_records'
    tgt_qid = 'meta::AUDIT_phantom_dep_pre_ratify'

    if meta_store.get_atom('AUDIT_atomizer_drop_criterion_loses_older_schema_records') is None:
        print(f'[{label}] HARD_FAIL: 237d not in-store')
        return 1
    if meta_store.get_atom('AUDIT_phantom_dep_pre_ratify') is None:
        print(f'[{label}] HARD_FAIL: 92nd not in-store')
        return 1
    print(f'[{label}] both atoms verified in-store', flush=True)

    # Bidirectional dual edges
    ps.add_relation(
        src_qid, RelationType.COMPOSES, tgt_qid,
        source=src_tag,
        note='237d (drop-criterion-loss false-negative) COMPOSES 92nd (phantom-dep false-positive) -- DUAL provenance-integrity opposite direction',
    )
    ps.add_relation(
        tgt_qid, RelationType.COMPOSES, src_qid,
        source=src_tag,
        note='92nd (phantom-dep false-positive) COMPOSES 237d (drop-criterion-loss false-negative) -- DUAL reverse',
    )
    meta_store._flush_relations()

    post_rels = sum(1 for _ in ps.iter_all_relations())
    print(f'[{label}] post: rels={post_rels} (+{post_rels-pre_rels}; expected +2 bidirectional dual)', flush=True)

    if post_rels - pre_rels != 2:
        print(f'[{label}] HARD_FAIL: expected +2 rels')
        return 1

    print()
    print('=' * 80)
    print(f'[{label}] HARD_PASS: 237d <-> 92nd DUAL edge pair wired')
    print(f'  DUAL: phantom-dep-false-positive <-> drop-criterion-false-negative')
    print(f'  Provenance-integrity family closure (opposite direction)')
    print('=' * 80)
    return 0


if __name__ == '__main__':
    sys.exit(main())
