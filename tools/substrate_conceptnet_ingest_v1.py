"""ConceptNet ARC-3 second-direction ingest (Item 4, 20h sprint; 2026-06-18; APPLY DEFERRED until push-fix lands).

Ingests the ConceptNet 5.7 english assertions into the typed-atom Store (NOT the bge-KV pipeline in
backend/kb/conceptnet_ingest.py -- that is a separate architecture). One CONCEPT_NODE atom per english concept
(id=CN_<concept>, namespaced -> 0 cross-corpus collision; lemma-overlap with WN_/LEXICON is EXPECTED, not a collision).
ConceptNet relations are FIRST-CLASS rel_types (IsA->IS_A, PartOf->PART_OF, the rest CN_*; NEVER metadata-on-RELATES --
the edge-metadata-drop lesson). algebra=None + provenance_quality=RESEARCH_FINDING (ingest tier; FrameNet precedent).

DATA SOURCE (acquisition is a precursor; see --dry-run when absent): the canonical ConceptNet 5.7 assertions CSV
(conceptnet-assertions-5.7.0.csv[.gz]) -- a TSV: each row = `/a/[..]  /r/RelType  /c/LANG/start  /c/LANG/end  {json}`.
English-only (start+end both /c/en/) + weight>=MIN_WEIGHT. Configurable --csv path; default data/conceptnet/assertions.csv.

CHECKPOINT/RESUME/ASSEMBLE (USER item-6 long-cells directive; ConceptNet is large/long-running):
  - Process the CSV in CHUNK-row blocks. Each completed chunk -> a SHARD file cached_conceptnet/_shards_<csv_hash>/chunk_K.jsonl
    (atoms+edges for that chunk) + progress.json updated. A kill mid-run loses at most the in-flight chunk.
  - RESUME: on restart, skip chunks whose shard already exists; process only the remaining.
  - ASSEMBLE (only after ALL chunks sharded): load all shards -> dedup atoms -> BATCHED _index_atom + single save_atoms
    (the B1 single-flush pattern; NOT per-atom add_atom which is O(n^2)) -> edges via _index_relation + flush. So the
    design is BOTH resumable (per-chunk shards) AND single-flush (assemble-time). Mirrors the pre-cache item-6 cell.

GATES (pre-ingest cert-gate, on --apply): edge-budget (declared==actual readback), 0-phantom (every edge endpoint is a
CN_ atom we add -> self-consistent; verified), axiom_term==206 + cap_pres 6/6 + CERT unchanged snapshot, namespaced
0-collision (no CN_ id already in Store under a different kind). KILL-RESTART-TEST: --resume-test (mock CSV; 5 chunks;
write 2 shards; "die"; re-run; confirm skip-2 + process-3 + assemble). --self-test (parse/map/atom-build on synthetic
triples; no data). 11th-rule deterministic (ConceptNet is a curated KB, not an LLM). ASCII.
"""
from __future__ import annotations
import argparse
import gzip
import hashlib
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path('.').resolve()))
from backend.substrate_index.schema import RelationType

DEVICE = "cpu"            # 7th BLOCKING checklist item (device-exercise, USER-caught 2026-06-18): this cell is PURE-CPU
                          # (CSV parse + Store atom/edge writes; NO torch/bge -- the bge-KV pipeline is the SEPARATE
                          # backend/kb/conceptnet_ingest.py). MUST route to cpu_queue, NOT a GPU runner (would be 0% util).
DEFAULT_CSV = Path('data/conceptnet/assertions.csv')
SHARD_ROOT = Path('data/conceptnet/cached_conceptnet')
CHUNK = 100_000           # rows per shard (resume granularity)
MIN_WEIGHT = 1.0          # ConceptNet assertion weight floor (drop low-confidence)

# ConceptNet relation name -> first-class RelationType. IsA/PartOf reuse existing; rest CN_*.
REL_MAP = {
    'IsA': RelationType.IS_A, 'PartOf': RelationType.PART_OF,
    'RelatedTo': RelationType.CN_RELATED_TO, 'HasA': RelationType.CN_HAS_A,
    'UsedFor': RelationType.CN_USED_FOR, 'CapableOf': RelationType.CN_CAPABLE_OF,
    'AtLocation': RelationType.CN_AT_LOCATION, 'Causes': RelationType.CN_CAUSES,
    'HasSubevent': RelationType.CN_HAS_SUBEVENT, 'HasFirstSubevent': RelationType.CN_HAS_SUBEVENT,
    'HasLastSubevent': RelationType.CN_HAS_SUBEVENT, 'HasPrerequisite': RelationType.CN_HAS_PREREQUISITE,
    'HasProperty': RelationType.CN_HAS_PROPERTY, 'MotivatedByGoal': RelationType.CN_MOTIVATED_BY_GOAL,
    'ObstructedBy': RelationType.CN_OBSTRUCTED_BY, 'Desires': RelationType.CN_DESIRES,
    'CreatedBy': RelationType.CN_CREATED_BY, 'Synonym': RelationType.CN_SYNONYM,
    'Antonym': RelationType.CN_ANTONYM, 'DistinctFrom': RelationType.CN_DISTINCT_FROM,
    'DerivedFrom': RelationType.CN_DERIVED_FROM, 'SymbolOf': RelationType.CN_SYMBOL_OF,
    'DefinedAs': RelationType.CN_DEFINED_AS, 'MannerOf': RelationType.CN_MANNER_OF,
    'LocatedNear': RelationType.CN_LOCATED_NEAR, 'HasContext': RelationType.CN_HAS_CONTEXT,
    'SimilarTo': RelationType.CN_SIMILAR_TO, 'EtymologicallyRelatedTo': RelationType.CN_ETYMOLOGICALLY_RELATED_TO,
    'EtymologicallyDerivedFrom': RelationType.CN_ETYMOLOGICALLY_DERIVED_FROM,
    'CausesDesire': RelationType.CN_CAUSES_DESIRE, 'MadeOf': RelationType.CN_MADE_OF,
    'ReceivesAction': RelationType.CN_RECEIVES_ACTION, 'FormOf': RelationType.CN_FORM_OF,
}


def normalize_concept(uri: str) -> str:
    """/c/en/dog or /c/en/dog/n -> 'dog'. English-only -> '' otherwise."""
    if not uri:
        return ''
    p = uri.split('/')
    if len(p) < 4 or p[1] != 'c' or p[2] != 'en':
        return ''
    return p[3].replace('_', ' ').strip()


def rel_name(uri: str) -> str:
    return uri.rsplit('/', 1)[-1] if '/' in uri else uri


def cn_id(concept: str) -> str:
    return 'CN_' + concept.replace(' ', '_')


def parse_row(line: str):
    """One assertions.csv row -> (subj_concept, RelationType, obj_concept) or None (non-en / unmapped / low-weight)."""
    cols = line.rstrip('\n').split('\t')
    if len(cols) < 5:
        return None
    _, rel_uri, start_uri, end_uri, meta = cols[0], cols[1], cols[2], cols[3], cols[4]
    s = normalize_concept(start_uri); o = normalize_concept(end_uri)
    if not s or not o:
        return None
    rn = rel_name(rel_uri)
    rt = REL_MAP.get(rn)
    if rt is None:
        return None  # unmapped relation -> SKIP (counted), not coerced
    try:
        w = float(json.loads(meta).get('weight', 1.0))
    except Exception:
        w = 1.0
    if w < MIN_WEIGHT:
        return None
    return (s, rt, o)


def _open_csv(path: Path):
    if str(path).endswith('.gz'):
        return gzip.open(path, 'rt', encoding='utf-8')
    return open(path, 'r', encoding='utf-8')


def _csv_hash(path: Path) -> str:
    h = hashlib.sha256()
    h.update(str(path).encode())
    h.update(str(path.stat().st_size).encode())
    return h.hexdigest()[:8]


def _shard_dir(path: Path) -> Path:
    return SHARD_ROOT / ('_shards_' + _csv_hash(path))


def _chunk_to_records(rows):
    """rows: list[(s, rt, o)] -> ({concept,...}, [(s_id, rel, o_id),...]) for the chunk."""
    concepts = set()
    edges = []
    for (s, rt, o) in rows:
        concepts.add(s); concepts.add(o)
        edges.append((cn_id(s), rt.value, cn_id(o)))
    return concepts, edges


def _write_shard(shard_path: Path, concepts, edges):
    tmp = shard_path.with_suffix('.tmp.jsonl')
    with open(tmp, 'w', encoding='utf-8') as f:
        json.dump({'concepts': sorted(concepts), 'edges': edges}, f)
    import os
    os.replace(tmp, shard_path)


def process_csv(path: Path, row_iter=None, verbose=True):
    """Chunk -> shard with RESUME (skip existing shards). row_iter override = for --resume-test (mock)."""
    sd = _shard_dir(path)
    sd.mkdir(parents=True, exist_ok=True)
    it = row_iter if row_iter is not None else _row_generator(path)
    chunk_idx = 0
    buf = []
    skipped = 0
    processed = 0
    for parsed in it:
        buf.append(parsed)
        if len(buf) >= CHUNK:
            sp = sd / f'chunk_{chunk_idx}.jsonl'
            if sp.exists():
                skipped += 1
            else:
                c, e = _chunk_to_records(buf)
                _write_shard(sp, c, e)
                processed += 1
                if verbose:
                    print(f'  shard chunk_{chunk_idx}: {len(c)} concepts, {len(e)} edges', flush=True)
            buf = []
            chunk_idx += 1
    if buf:  # final partial chunk
        sp = sd / f'chunk_{chunk_idx}.jsonl'
        if sp.exists():
            skipped += 1
        else:
            c, e = _chunk_to_records(buf)
            _write_shard(sp, c, e)
            processed += 1
            if verbose:
                print(f'  shard chunk_{chunk_idx} (final): {len(c)} concepts, {len(e)} edges', flush=True)
        chunk_idx += 1
    return dict(shard_dir=sd, n_chunks=chunk_idx, processed=processed, skipped=skipped)


def _row_generator(path: Path):
    with _open_csv(path) as f:
        for line in f:
            p = parse_row(line)
            if p is not None:
                yield p


def assemble(shard_dir: Path):
    """Load all shards -> dedup concepts + edges. Returns (concepts:set, edges:set)."""
    concepts = set()
    edges = set()
    shards = sorted(shard_dir.glob('chunk_*.jsonl'), key=lambda p: int(p.stem.split('_')[1]))
    for sp in shards:
        d = json.loads(sp.read_text(encoding='utf-8'))
        concepts.update(d['concepts'])
        for (s, r, o) in d['edges']:
            edges.add((s, r, o))
    return concepts, edges, len(shards)


# ---------------- Store apply (DEFERRED until push-fix) ----------------

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


def _make_atom(concept: str):
    from backend.substrate_index.schema import Atom, AtomKind, Corpus, Tier
    return Atom(id=cn_id(concept), name=concept, corpus=Corpus.CONCEPT, tier=Tier.TIER_NA,
                kind=AtomKind.CONCEPT_NODE, description=f'ConceptNet english concept: {concept}',
                metadata={'provenance_quality': 'RESEARCH_FINDING', 'relevance_tier': 'ACTIVE',
                          'source': 'conceptnet_5.7_en', 'term_class': 'CONCEPT_NODE'})


def apply_run(csv_path: Path) -> int:
    from backend.substrate_index.partition import PartitionedStore
    from backend.substrate_index.schema import Corpus, Relation, save_atoms
    import os
    if not csv_path.exists():
        print(f'APPLY blocked: ConceptNet CSV not found at {csv_path} (data-acquisition precursor; see --dry-run).'); return 5
    print(f'STEP 1/3 chunk+shard (resume-aware) from {csv_path} ...', flush=True)
    pr = process_csv(csv_path)
    print(f'  chunks={pr["n_chunks"]} processed={pr["processed"]} skipped(resumed)={pr["skipped"]}', flush=True)
    print('STEP 2/3 assemble shards ...', flush=True)
    concepts, edges, n_sh = assemble(pr['shard_dir'])
    print(f'  assembled {len(concepts)} concepts + {len(edges)} edges from {n_sh} shards', flush=True)
    print('STEP 3/3 Store apply (batched single-flush + gates) ...', flush=True)
    ps = PartitionedStore(Path('data/substrate_index'))
    pre_axiom = axiom_term_count(ps); pre_mod = module_liveness_ok(); pre_cert = cert_count(ps)
    pre_atoms = len(list(ps.all_atoms()))
    if not pre_mod or pre_axiom != 206:
        print('PRE-GATE FAIL. Halt.'); return 1
    cs = ps._store_for(Corpus.CONCEPT)
    # 0-collision: a CN_ id already present under a DIFFERENT kind = collision (namespaced -> should be none)
    from backend.substrate_index.schema import AtomKind
    collisions = [c for c in concepts if cn_id(c) in cs._by_id and cs._by_id[cn_id(c)].kind != AtomKind.CONCEPT_NODE]
    if collisions:
        print(f'HARD_FAIL: {len(collisions)} CN_ id collisions with non-CONCEPT_NODE atoms (e.g. {collisions[:3]}). Halt.'); return 6
    intended_atoms = {cn_id(c) for c in concepts}
    intended_edges = set(edges)
    for c in sorted(concepts):                                  # batched _index_atom (NOT per-atom add_atom)
        if cn_id(c) not in cs._by_id:
            cs._index_atom(_make_atom(c))
    for attempt in range(12):
        try:
            save_atoms(list(cs._by_id.values()), cs.atoms_path); break
        except PermissionError:
            time.sleep(0.3 * (attempt + 1))
    else:
        print('HARD_FAIL: atoms flush race.'); return 3
    edge_added = 0
    for (s, r, o) in sorted(intended_edges):
        if (s, r, o) in cs._all_relations:
            continue
        cs._index_relation(Relation(src_id=s, tgt_id=o, rel_type=RelationType(r)))
        edge_added += 1
    for attempt in range(12):
        try:
            cs._flush_relations(); break
        except PermissionError:
            time.sleep(0.3 * (attempt + 1))
    # readback
    ps3 = PartitionedStore(Path('data/substrate_index'))
    post_axiom = axiom_term_count(ps3); post_mod = module_liveness_ok(); post_cert = cert_count(ps3)
    cs3 = ps3._store_for(Corpus.CONCEPT)
    atoms_present = intended_atoms.issubset(set(cs3._by_id.keys()))
    edges_present = intended_edges.issubset({(s, r, o) for (s, r, o) in cs3._all_relations})
    gate_ok = (post_axiom == 206 and post_mod and post_cert == pre_cert and atoms_present and edges_present)
    print(f'POST: axiom_term={post_axiom} cap_pres={post_mod} CERT={post_cert} (unchanged from {pre_cert}) '
          f'atoms_present={atoms_present} edges_present={edges_present} edge_added={edge_added}')
    if not gate_ok:
        print('HARD_FAIL: post-gate failed.'); return 2
    print(f'CONCEPTNET INGEST complete: +{len(intended_atoms)} CONCEPT_NODE atoms + {edge_added} first-class edges | axiom 206 | cap_pres 6/6 | CERT {post_cert} unchanged')
    return 0


# ---------------- tests ----------------

def self_test() -> int:
    # synthetic triples exercise parse/map/atom-build (NO data, NO Store)
    rows = [
        '/a/[..]\t/r/IsA\t/c/en/dog\t/c/en/animal\t{"weight": 2.0}',
        '/a/[..]\t/r/UsedFor\t/c/en/knife\t/c/en/cut\t{"weight": 1.5}',
        '/a/[..]\t/r/PartOf\t/c/en/wheel\t/c/en/car\t{"weight": 1.0}',
        '/a/[..]\t/r/RelatedTo\t/c/fr/chien\t/c/en/animal\t{"weight": 3.0}',   # non-en -> drop
        '/a/[..]\t/r/SomeUnknownRel\t/c/en/x\t/c/en/y\t{"weight": 2.0}',        # unmapped -> drop
        '/a/[..]\t/r/IsA\t/c/en/cat\t/c/en/animal\t{"weight": 0.2}',            # low-weight -> drop
    ]
    parsed = [parse_row(r) for r in rows]
    kept = [p for p in parsed if p is not None]
    ok = (len(kept) == 3
          and kept[0] == ('dog', RelationType.IS_A, 'animal')
          and kept[1] == ('knife', RelationType.CN_USED_FOR, 'cut')
          and kept[2] == ('wheel', RelationType.PART_OF, 'car')
          and cn_id('used for') == 'CN_used_for')
    c, e = _chunk_to_records(kept)
    # concepts = {dog, animal, knife, cut, wheel, car} = 6 distinct
    ok = ok and (len(c) == 6 and len(e) == 3 and ('CN_dog', 'IS_A', 'CN_animal') in e)
    print(f'[conceptnet_ingest] --self-test {"OK" if ok else "FAIL"} (parse/map/en-filter/unmapped-skip/low-weight-drop/atom-id; kept={len(kept)}/6, concepts={len(c)}, edges={len(e)}); NO Store mutation.')
    return 0 if ok else 1


def resume_test() -> int:
    """KILL-RESTART-TEST: mock 5 chunks; write 2 shards; 'die'; re-run; confirm skip-2 + process-3 + assemble. (demonstrate, don't assert.)"""
    import os, shutil, tempfile
    tmproot = Path(tempfile.mkdtemp(prefix='cn_resume_'))
    global SHARD_ROOT, CHUNK
    saved_root, saved_chunk = SHARD_ROOT, CHUNK
    SHARD_ROOT = tmproot / 'cached'
    CHUNK = 3   # tiny chunks
    fake_csv = tmproot / 'fake_assertions.csv'
    fake_csv.write_text('x\n', encoding='utf-8')   # exists -> _csv_hash works
    # 15 synthetic parsed rows -> 5 chunks of 3
    def gen_all():
        for i in range(15):
            yield (f'c{i}', RelationType.IS_A, f'c{i+1}')
    try:
        # run 1: process only first 2 chunks (simulate death after chunk 1)
        def gen_partial():
            n = 0
            for r in gen_all():
                yield r
                n += 1
                if n >= 6:   # 2 chunks of 3
                    return
        r1 = process_csv(fake_csv, row_iter=gen_partial(), verbose=False)
        after1 = len(list(_shard_dir(fake_csv).glob('chunk_*.jsonl')))
        # run 2 (RESUME): full iter -> skip 2 existing, process remaining 3
        r2 = process_csv(fake_csv, row_iter=gen_all(), verbose=False)
        after2 = len(list(_shard_dir(fake_csv).glob('chunk_*.jsonl')))
        concepts, edges, n_sh = assemble(_shard_dir(fake_csv))
        ok = (after1 == 2 and after2 == 5 and r2['skipped'] == 2 and r2['processed'] == 3
              and n_sh == 5 and len(edges) == 15)
        print(f'[conceptnet_ingest] --resume-test {"OK" if ok else "FAIL"}: run1 wrote {after1} shards (died); '
              f'run2 RESUMED skip={r2["skipped"]} process={r2["processed"]} -> {after2} shards; '
              f'assembled {len(concepts)} concepts/{len(edges)} edges. (demonstrated resume, not asserted.)')
        return 0 if ok else 1
    finally:
        SHARD_ROOT, CHUNK = saved_root, saved_chunk
        shutil.rmtree(tmproot, ignore_errors=True)


def dry_run(csv_path: Path) -> int:
    from backend.substrate_index.partition import PartitionedStore
    print('=' * 78)
    print('CONCEPTNET INGEST -- DRY-RUN (no mutation) for Skunkworks SCHEMA-VET')
    print('=' * 78)
    ps = PartitionedStore(Path('data/substrate_index'))
    print(f'DEVICE={DEVICE} (7th checklist item: PURE-CPU cell; route to cpu_queue, NOT a GPU runner).')
    print(f'SNAPSHOT: axiom_term={axiom_term_count(ps)} (206) | cap_pres={module_liveness_ok()} (6/6) | CERT={cert_count(ps)}')
    print(f'rel-map: {len(REL_MAP)} ConceptNet relations -> first-class rel_types (IsA->IS_A, PartOf->PART_OF, rest CN_*); unmapped -> SKIP (counted).')
    if not csv_path.exists():
        print(f'\nDATA-ACQUISITION PRECURSOR: ConceptNet 5.7 assertions CSV not at {csv_path}.')
        print('  Acquire conceptnet-assertions-5.7.0.csv.gz (https://github.com/commonsense/conceptnet5/wiki/Downloads)')
        print('  -> place at data/conceptnet/assertions.csv[.gz]. (infra/data lane; apply is DEFERRED until push-fix anyway.)')
        print('  Cell logic verified via --self-test + --resume-test (no data needed). Schema-add (CONCEPT_NODE + 29 CN_*) verify-loads OK.')
        print('=' * 78)
        return 0
    # sample-parse the first SAMPLE rows for a coverage preview
    SAMPLE = 200_000
    from collections import Counter
    kept = 0; seen = 0; relc = Counter(); concepts = set()
    with _open_csv(csv_path) as f:
        for line in f:
            seen += 1
            p = parse_row(line)
            if p:
                kept += 1; relc[p[1].name] += 1; concepts.add(p[0]); concepts.add(p[2])
            if seen >= SAMPLE:
                break
    print(f'\nSAMPLE parse (first {seen} rows): kept {kept} en-assertions ({100.0*kept/max(seen,1):.1f}%); {len(concepts)} distinct concepts')
    print('  rel distribution (top 10):', relc.most_common(10))
    print(f'  projected CHUNK={CHUNK} rows/shard -> resumable; assemble single-flush (B1).')
    print('  gates on --apply: edge-budget readback + 0-phantom (CN_ self-consistent) + 0-collision + axiom206/cap_pres/CERT unchanged.')
    print('=' * 78)
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--csv', default=str(DEFAULT_CSV))
    ap.add_argument('--apply', action='store_true')
    ap.add_argument('--self-test', action='store_true')
    ap.add_argument('--resume-test', action='store_true')
    args = ap.parse_args()
    if args.self_test:
        return self_test()
    if args.resume_test:
        return resume_test()
    csv_path = Path(args.csv)
    return apply_run(csv_path) if args.apply else dry_run(csv_path)


if __name__ == '__main__':
    raise SystemExit(main())
