"""T3 Phase A: targeted WordNet COMPLETENESS extension (Skunkworks ruling 2026-06-18: completeness-only, gold-independent).

The depth-cliff coverage-lever test (Phase A ingest -> Phase B B-alpha BROAD v2). RULING: ingest the gold-INDEPENDENT
completeness set = every out-of-5k DIRECT hypernym ("missing parent") of an in-5k synset, so every in-5k synset has its
WordNet-canonical direct parent in-corpus. DROP the frontier slice (POOL-3 subset POOL-1 -> already ingested; the only
gold-touching vector) + DROP corpus-frequency (depth-cliff-irrelevant confound). Clean SINGLE-VARIABLE 2-hop-coverage
test. NOT recursive (grandparents = Option B next-step, result-directed). Deterministic completeness rule (no RL/learned
-> 11th-rule clean). LEXICON tier (same as B1). Materializes the NEW HYPERNYM edges = in5k->new-parent ONLY (NO RECURSION;
among-new + new->in5k = the new parents' OWN upward edges = grandparent-recursion = Option B, EXCLUDED). 0-phantom (both
endpoints in-corpus post-ingest). APPLY captures intended_edges PRE-ingest (re-analyze post-ingest would FLIP in5k 5000->
6339 and recompute target->grandparent recursion -- Skunkworks HALT catch); edge READ-BACK gate enforces declared==actual.

DEFAULT --dry-run (NO mutation; counts + edge-budget + cross-corpus 0-ID-collision + axiom/cap_pres SNAPSHOT for the
pre-ingest cert-gate). --apply mutates SERIALLY (fresh-load + os.replace-retry; axiom_term/cap_pres gated; non-retroactive).
Laptop CPU, no bge. ASCII-only. 11th-rule.
"""
from __future__ import annotations
import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path('.').resolve()))
from backend.substrate_index.schema import Atom, AtomKind, Corpus, Tier, RelationType

WORDNET_VERSION = '3.0'
HYPONYM_CAP = 30
SRC_TAG = 'wordnet_completeness_t3_phaseA_2026_06_18'


def _synset_freq(s) -> int:
    return sum(l.count() for l in s.lemmas())


def _atom_id(s) -> str:
    return f"WN_{s.name()}"


def build_atom(s) -> Atom:
    direct_hyper = s.hypernyms() + s.instance_hypernyms()
    direct_hypo = s.hyponyms()
    meronyms = s.part_meronyms() + s.member_meronyms() + s.substance_meronyms()
    metadata = {
        'wordnet_version': WORDNET_VERSION, 'pos': s.pos(), 'synset_name': s.name(),
        'synset_offset': f"{s.offset():08d}", 'lexname': s.lexname(),
        'lemma_freq_semcor': _synset_freq(s),
        'synonyms': [l.name() for l in s.lemmas()],
        'hypernyms': [h.name() for h in direct_hyper],
        'hyponyms': [h.name() for h in direct_hypo[:HYPONYM_CAP]],
        'hyponyms_total': len(direct_hypo),
        'meronyms': [m.name() for m in meronyms[:HYPONYM_CAP]],
        'completeness_target': True,   # T3 Phase A provenance: added as a missing-direct-parent of an in-5k synset
        'source': SRC_TAG,
    }
    return Atom(id=_atom_id(s), name=s.name(), description=(s.definition() or '')[:500],
                kind=AtomKind.LEXICON, tier=Tier.TIER_LEXICON, corpus=Corpus.CONCEPT, algebra=None, metadata=metadata)


def compute_targets(wn, in5k_names):
    """The gold-INDEPENDENT completeness set: out-of-5k DIRECT hypernyms of in-5k synsets (missing parent links).
    Deterministic (sorted). Returns (target_synsets sorted by name, in_degree_from_in5k)."""
    from collections import Counter
    in_deg = Counter()
    for nm in sorted(in5k_names):
        try:
            s = wn.synset(nm)
        except Exception:
            continue
        for h in s.hypernyms() + s.instance_hypernyms():
            if h.name() not in in5k_names:
                in_deg[h.name()] += 1
    target_names = sorted(in_deg.keys())
    return [wn.synset(n) for n in target_names], in_deg


def compute_completeness_edges(wn, in5k_names, target_names):
    """NO-RECURSION (Skunkworks ruling): the Phase A edge-set is ONLY in5k -> new-direct-parent (the missing
    completeness links). EXCLUDES among-new (target->target) + new->in5k -- those are the new parents' OWN upward
    edges = grandparent-recursion = Option B, a SEPARATE later phase. Deterministic (sorted). Returns set(src,tgt)."""
    edges = set()
    for nm in sorted(in5k_names):
        try:
            s = wn.synset(nm)
        except Exception:
            continue
        for h in s.hypernyms() + s.instance_hypernyms():
            if h.name() in target_names:          # in5k synset -> its missing direct parent (now being added)
                edges.add((nm, h.name()))
    return edges


def module_liveness_ok() -> bool:
    import importlib
    return all(hasattr(importlib.import_module(m), sym) for m, sym in [
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


def _persisted_hypernym_edges(ps):
    from backend.substrate_index.schema import Corpus
    cs = ps._store_for(Corpus.CONCEPT)
    return {(src[3:], tgt[3:]) for (src, rt, tgt) in cs._all_relations
            if rt == RelationType.HYPERNYM.value and src.startswith('WN_') and tgt.startswith('WN_')}


def analyze():
    from backend.substrate_index.partition import PartitionedStore
    from nltk.corpus import wordnet as wn
    ps = PartitionedStore(Path('data/substrate_index'))
    all_atoms = list(ps.all_atoms())
    in5k_names = {a.id[3:] for a in all_atoms if str(a.id).startswith('WN_')}
    all_ids = {a.id for a in all_atoms}

    targets, in_deg = compute_targets(wn, in5k_names)
    target_names = {t.name() for t in targets}
    # cross-corpus 0-ID-COLLISION: no WN_<target> already exists as ANY atom id
    collisions = [t.name() for t in targets if f"WN_{t.name()}" in all_ids]
    # NO-RECURSION: ONLY in5k -> new-direct-parent edges (the completeness links). Subtract persisted (idempotent).
    completeness_edges = compute_completeness_edges(wn, in5k_names, target_names)
    persisted = _persisted_hypernym_edges(ps)
    new_edges = completeness_edges - persisted
    low_in_deg = sum(1 for n in target_names if in_deg[n] == 1)
    return dict(ps=ps, in5k=len(in5k_names), targets=targets, n_targets=len(targets),
                collisions=collisions, new_edges=new_edges, n_new_edges=len(new_edges),
                low_in_deg=low_in_deg)


def dry_run() -> int:
    a = analyze()
    ps = a['ps']
    print('=' * 74)
    print('T3 Phase A WordNet COMPLETENESS extension -- DRY-RUN (no mutation) for Skunkworks pre-ingest cert-gate')
    print('=' * 74)
    print(f"in-5k synsets (current): {a['in5k']}")
    print(f"COMPLETENESS targets (out-of-5k missing direct-parents; gold-INDEPENDENT): {a['n_targets']}")
    print(f"  low-in-degree (==1; Galarraga/Razniewski incompleteness targets): {a['low_in_deg']}")
    print(f"  cross-corpus ID-COLLISIONS (WN_<target> already an atom id): {len(a['collisions'])} (MUST be 0)")
    print(f"NEW HYPERNYM edges = in5k->new-parent ONLY (NO RECURSION; among-new + new->in5k EXCLUDED = Option B): {a['n_new_edges']}")
    print(f"SNAPSHOT before: axiom_term={axiom_term_count(ps)} (MUST stay 206) | cap_pres={module_liveness_ok()} | CERT={cert_count(ps)}")
    print('--- gates on --apply ---')
    print('  PRE: axiom_term==206 + cap_pres 6/6 (HALT else); 0 ID-collisions')
    print('  ingest: SERIAL batched atom-add (fresh-load + os.replace-retry) LEXICON/CONCEPT/algebra=None')
    print('  edge-mat: NEW HYPERNYM edges (0-phantom; both endpoints in-corpus post-ingest); _index_relation + flush-retry')
    print('  POST: axiom_term==206 (LEXICON has no algebra) + cap_pres 6/6 + CERT unchanged + read-back')
    print('=' * 74)
    print(f"DRY-RUN complete. Awaiting Skunkworks pre-ingest cert-gate-equiv before --apply. completeness-only, single-variable, deterministic.")
    return 0 if not a['collisions'] else 1


def _flush_relations_with_retry(cstore, attempts=12):
    for attempt in range(attempts):
        try:
            cstore._flush_relations(); return True
        except PermissionError:
            time.sleep(0.3 * (attempt + 1))
    return False


def apply_run() -> int:
    from backend.substrate_index.partition import PartitionedStore
    a = analyze()
    if a['collisions']:
        print(f"HALT: {len(a['collisions'])} ID-collisions (e.g. {a['collisions'][:3]})."); return 1
    ps = a['ps']
    # CAPTURE the intended edges PRE-ingest (Skunkworks HALT fix: re-analyze post-ingest flips in5k 5000->6339 ->
    # target->grandparent recursion. Materialize the CAPTURED in5k->target set; do NOT re-analyze.)
    intended_edges = set(a['new_edges'])
    persisted_pre = _persisted_hypernym_edges(ps)
    pre_axiom = axiom_term_count(ps); pre_mod = module_liveness_ok(); pre_cert = cert_count(ps)
    pre_atoms = len(list(ps.all_atoms()))
    print(f"PRE: atoms={pre_atoms} axiom_term={pre_axiom} cap_pres={pre_mod} CERT={pre_cert} | intended_edges={len(intended_edges)}")
    if not pre_mod or pre_axiom != 206:
        print('PRE-GATE FAIL. Halt.'); return 1

    # 1) SERIAL batched atom-add (fresh reload, single save, os.replace-retry handled by add_atom path)
    added = 0
    for t in a['targets']:
        aid = f"WN_{t.name()}"
        if ps.get_atom(f'concept::{aid}') is not None:
            continue
        ps.add_atom(build_atom(t), source=SRC_TAG, note='T3 Phase A completeness missing-direct-parent')
        added += 1
    print(f"  atoms added: {added}")

    # 2) edge-mat the CAPTURED intended edges (in5k->target; NOT a re-analyze). Atoms added first -> 0-phantom.
    from backend.substrate_index.schema import Corpus, Relation
    ps2 = PartitionedStore(Path('data/substrate_index'))
    cstore = ps2._store_for(Corpus.CONCEPT)
    edge_added = 0
    for (src, tgt) in sorted(intended_edges):
        triple = (f"WN_{src}", RelationType.HYPERNYM.value, f"WN_{tgt}")
        if triple in cstore._all_relations:
            continue
        cstore._index_relation(Relation(src_id=f"WN_{src}", tgt_id=f"WN_{tgt}", rel_type=RelationType.HYPERNYM))
        edge_added += 1
    if edge_added and not _flush_relations_with_retry(cstore):
        print('HARD_FAIL: os.replace race on relations flush.'); return 3
    print(f"  HYPERNYM edges added: {edge_added}")

    # 3) POST gates + EDGE READ-BACK (Skunkworks fix: the gate that would have caught the recursion-flip)
    ps3 = PartitionedStore(Path('data/substrate_index'))
    post_axiom = axiom_term_count(ps3); post_mod = module_liveness_ok(); post_cert = cert_count(ps3)
    post_atoms = len(list(ps3.all_atoms()))
    persisted_now = _persisted_hypernym_edges(ps3)
    edges_present = intended_edges.issubset(persisted_now)            # ALL intended edges actually persisted
    expected_new = len(intended_edges - persisted_pre)
    edge_count_ok = (edge_added == expected_new)                      # declared==actual for edges
    gate_ok = (post_axiom == 206 and post_mod and post_cert == pre_cert and added > 0
               and edges_present and edge_count_ok)
    print(f"POST: atoms={post_atoms} (+{post_atoms - pre_atoms}) axiom_term={post_axiom} cap_pres={post_mod} "
          f"CERT={post_cert} (unchanged from {pre_cert}) | edges_present={edges_present} edge_added={edge_added} expected_new={expected_new}")
    if not gate_ok:
        print('HARD_FAIL: gate failed (axiom_term/cap_pres/CERT preserved + ALL intended edges read-back + declared==actual).'); return 2
    print('=' * 74)
    print(f"T3 Phase A APPLY complete: +{added} LEXICON completeness synsets, +{edge_added} HYPERNYM edges (all {len(intended_edges)} intended read-back-verified) | axiom_term 206 | cap_pres 6/6 | CERT {post_cert} unchanged")
    print('=' * 74)
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--apply', action='store_true')
    args = ap.parse_args()
    return apply_run() if args.apply else dry_run()


if __name__ == '__main__':
    raise SystemExit(main())
