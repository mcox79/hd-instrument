"""Bucket-2 TRACK-3: edge-materialization (B-alpha prereq) -- materialize B1 WordNet + B2 GO
hierarchy METADATA into TYPED EDGES.

The graph is sparse (~7720 edges / 41k atoms = 0.19 edges/atom); the B1/B2 ingest carried the
hierarchy relations as METADATA fields (per the ratified internal-relations-as-metadata rule), so
multi-hop reasoning over the hierarchy is impossible until they are materialized as edges.

Materialized edges (0-PHANTOM: emitted ONLY when BOTH endpoints are atoms in the store):
  WordNet (CONCEPT corpus, WN_ atoms):
    - HYPERNYM: synset X -> its hypernym Y  (X is-a-kind-of Y)        [from metadata.hypernyms]
    - PART_OF : part Y -> whole X            (Y is a part of X)        [from metadata.meronyms]
  GO (SCIENCE corpus, GO_ atoms):
    - IS_A    : term X -> its superclass Y   (ontological subsumption) [from metadata.is_a]
  (hyponym = reverse of HYPERNYM -> redundant, not materialized; synonym = intra-synset lemmas,
   not an inter-synset edge -> stays metadata; GO part_of/regulates were not parsed in B2 ->
   a follow-up re-parse, flagged.)

DEFAULT = --dry-run (NO mutation; candidate-edge counts + coverage + samples for Skunkworks SCHEMA-VET).
--apply mutates SERIALLY (batched relation write + os.replace-retry; axiom_term/cap_pres gated; non-retroactive).

NEW rel_types (schema-add, verify-loads done): HYPERNYM / IS_A / PART_OF (+ E2 STRENGTHENS/MECHANISM_FOR/
REPLICATES, handled in a separate E2 re-typing step). ASCII-only. No LLM. Laptop-safe.
"""
from __future__ import annotations
import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path('.').resolve()))

from backend.substrate_index.schema import RelationType


def _wn_id(synset_name: str) -> str:
    return f'WN_{synset_name}'


def _go_id(go_id: str) -> str:
    return go_id.replace(':', '_')


def compute_edges(ps):
    """Return (edges, stats). edges = list of (src_qid, rel_type, tgt_qid). 0-phantom enforced."""
    atoms = list(ps.all_atoms())
    by_id = {a.id: a for a in atoms}
    wn = [a for a in atoms if str(a.id).startswith('WN_')]
    go = [a for a in atoms if str(a.id).startswith('GO_')]

    edges = []
    stats = {'wn_atoms': len(wn), 'go_atoms': len(go),
             'hypernym_total': 0, 'hypernym_in5k': 0, 'partof_total': 0, 'partof_in5k': 0,
             'isa_total': 0, 'isa_in5k': 0}

    # WordNet HYPERNYM (X -> hypernym Y) + PART_OF (meronym Y of X -> X)
    for a in wn:
        for hyper in (a.metadata.get('hypernyms') or []):
            stats['hypernym_total'] += 1
            tgt = _wn_id(hyper)
            if tgt in by_id:
                stats['hypernym_in5k'] += 1
                edges.append((f'concept::{a.id}', RelationType.HYPERNYM, f'concept::{tgt}'))
        for mero in (a.metadata.get('meronyms') or []):
            stats['partof_total'] += 1
            part = _wn_id(mero)                          # mero is a PART of a (mero PART_OF a)
            if part in by_id:
                stats['partof_in5k'] += 1
                edges.append((f'concept::{part}', RelationType.PART_OF, f'concept::{a.id}'))

    # GO IS_A (X -> superclass Y)
    for a in go:
        for parent in (a.metadata.get('is_a') or []):
            stats['isa_total'] += 1
            tgt = _go_id(parent)
            if tgt in by_id:
                stats['isa_in5k'] += 1
                edges.append((f'science::{a.id}', RelationType.IS_A, f'science::{tgt}'))

    # dedup (a metadata list could repeat; and HYPERNYM/PART_OF could collide-free but be safe)
    edges = list(dict.fromkeys(edges))
    return edges, stats


def _flush_relations_with_retry(cstore, attempts=12):
    """Single relation-flush with os.replace-race retry (bulk concurrency gotcha). Uses the
    store's own _flush_relations (correct explicit-relation reconstruction from _all_relations)."""
    for attempt in range(attempts):
        try:
            cstore._flush_relations()
            return True
        except PermissionError:
            time.sleep(0.3 * (attempt + 1))
    return False


def dry_run() -> int:
    from backend.substrate_index.partition import PartitionedStore
    ps = PartitionedStore(Path('data/substrate_index'))
    edges, stats = compute_edges(ps)

    from collections import Counter
    by_rel = Counter(rt.value for _, rt, _ in edges)
    print('=' * 72)
    print('Edge-materialization DRY-RUN (no Store mutation) -- for Skunkworks SCHEMA-VET')
    print('=' * 72)
    print(f"WN_ atoms: {stats['wn_atoms']}  |  GO_ atoms: {stats['go_atoms']}")
    print(f"HYPERNYM: {stats['hypernym_in5k']} materializable / {stats['hypernym_total']} total "
          f"({100.0*stats['hypernym_in5k']/max(stats['hypernym_total'],1):.0f}% in-5k; rest point outside the 5k -> 0-phantom skip)")
    print(f"PART_OF (meronym): {stats['partof_in5k']} / {stats['partof_total']} "
          f"({100.0*stats['partof_in5k']/max(stats['partof_total'],1):.0f}% in-5k)")
    print(f"IS_A (GO): {stats['isa_in5k']} / {stats['isa_total']} "
          f"({100.0*stats['isa_in5k']/max(stats['isa_total'],1):.0f}% in-5k)")
    print(f"TOTAL materializable typed edges (0-phantom, deduped): {len(edges)}")
    print(f"  by rel_type: {dict(by_rel)}")
    print()
    print('--- SAMPLE edges (first 4 per rel_type) ---')
    for rel in ('HYPERNYM', 'PART_OF', 'IS_A'):
        sample = [(s, t) for s, rt, t in edges if rt.value == rel][:4]
        for s, t in sample:
            print(f'  {s} -{rel}-> {t}')
    print()
    print('--- gates on --apply ---')
    print('  PRE: axiom_term==206 + cap_pres 6/6 (HALT else)')
    print('  POST: relations += len(edges) (idempotent: existing 3-tuples skip), axiom_term==206 (edges do NOT touch')
    print('        axiom_term -- that is an atom-algebra metric), cap_pres 6/6, 0-phantom (both endpoints verified in-store)')
    print('  batched single relation-flush + os.replace-retry (bulk concurrency gotcha)')
    print('=' * 72)
    print('DRY-RUN complete. NO mutation. Awaiting Skunkworks SCHEMA-VET (rel_type names + mapping + 0-phantom) before --apply.')
    return 0


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


def axiom_term_count(ps) -> int:
    return sum(
        1 for a in ps.all_atoms()
        if str(a.corpus.name) == 'MATH'
        and str(a.tier.name) in ('TIER_2_PRIMITIVE', 'TIER_3_ALGORITHM')
        and a.algebra and len(a.algebra) >= 3
        and 'oeis' not in str(a.id).lower()
        and not str(a.id).startswith('T3/wikidata_')
    )


def apply_run() -> int:
    from backend.substrate_index.partition import PartitionedStore
    ps = PartitionedStore(Path('data/substrate_index'))
    pre_axiom = axiom_term_count(ps)
    pre_mod = module_liveness_ok()
    print(f'PRE: axiom_term={pre_axiom}  cap_pres={pre_mod}')
    if not pre_mod or pre_axiom != 206:
        print('PRE-GATE FAIL. Halt.')
        return 1

    from backend.substrate_index.schema import Corpus, Relation
    edges, stats = compute_edges(ps)
    # count existing relations (for delta)
    pre_rel = sum(len(s._all_relations) for s in ps._stores.values())
    added = 0
    touched = set()
    # BATCH index into the source-corpus sub-store via _index_relation (correct LOCAL-id format +
    # _out/_in indexing) WITHOUT per-edge flush (avoid O(n^2) rewrites + N race windows).
    for src_qid, rt, tgt_qid in edges:
        src_corpus, src_local = src_qid.split('::', 1)
        _, tgt_local = tgt_qid.split('::', 1)          # within-corpus -> LOCAL ids (verified Store format)
        cstore = ps._store_for(Corpus[src_corpus.upper()])
        triple = (src_local, rt.value, tgt_local)
        if triple in cstore._all_relations:
            continue
        cstore._index_relation(Relation(src_id=src_local, tgt_id=tgt_local, rel_type=rt))
        touched.add(cstore)
        added += 1
    # single flush per touched sub-store, with retry
    for cstore in touched:
        if not _flush_relations_with_retry(cstore):
            print('HARD_FAIL: os.replace race on relations flush after retries.')
            return 3

    ps2 = PartitionedStore(Path('data/substrate_index'))   # fresh reload verify
    post_rel = sum(len(s._all_relations) for s in ps2._stores.values())
    post_axiom = axiom_term_count(ps2)
    post_mod = module_liveness_ok()
    print(f'POST: relations {pre_rel} -> {post_rel} (added {added})  axiom_term={post_axiom}  cap_pres={post_mod}')
    gate_ok = post_axiom == 206 and post_mod and added > 0
    if not gate_ok:
        print('HARD_FAIL: gate failed.')
        return 2
    print('=' * 72)
    print(f'Edge-materialization APPLY complete: +{added} typed edges (HYPERNYM/PART_OF/IS_A)  |  axiom_term 206/206  |  cap_pres 6/6')
    print('=' * 72)
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--apply', action='store_true')
    args = ap.parse_args()
    return apply_run() if args.apply else dry_run()


if __name__ == '__main__':
    raise SystemExit(main())
