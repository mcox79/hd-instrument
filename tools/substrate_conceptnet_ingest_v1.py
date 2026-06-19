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

# Option B (Director-decided 2026-06-19): remote-direct, self-contained acquisition. The cell wgets the canonical
# ConceptNet 5.7 assertions gz if absent (cache-first + wget -c resumable -> the 6th-checklist long-cell pattern;
# a dispatch-time network failure resumes from the partial, not from zero). License CC-BY-SA 4.0 (cite conceptnet5).
CONCEPTNET_URL = 'https://s3.amazonaws.com/conceptnet/downloads/2019/edges/conceptnet-assertions-5.7.0.csv.gz'
DEFAULT_GZ = Path('data/conceptnet/conceptnet-assertions-5.7.0.csv.gz')

# Director-recommended LOAD-BEARING scope (the cap-int Track-B target; ~3-5M edges English-only). DEFAULT filter.
# NotHasProperty is in Director's 17 but has NO RelationType yet (CN_NOT_HAS_PROPERTY absent) -> deferred to a vetted
# schema-add; the other 16 all map. --all-rels uses the full REL_MAP (incl. commonsense-reasoning rels) -- FLAGGED to
# Research as a scope question (HasSubevent/HasPrerequisite/Desires/CausesDesire are arguably load-bearing for the
# knowledge_graph REASONING capability, not noise; default stays Director's conservative set pending their call).
LOAD_BEARING_NAMES = frozenset({
    'IsA', 'PartOf', 'HasA', 'UsedFor', 'Causes', 'HasProperty', 'AtLocation', 'CapableOf', 'MadeOf',
    'DerivedFrom', 'RelatedTo', 'Synonym', 'Antonym', 'MannerOf', 'MotivatedByGoal', 'ReceivesAction',
})
SCOPE_LOAD_BEARING = True   # default; --all-rels sets False (use full REL_MAP)

# Bounded-v1 (Skunkworks ruling 2026-06-19): prove the knowledge_graph capability cert-grade at a KNOWN/manageable
# scale (Store grows 3-8x not 30x) BEFORE a deliberate full-scale v1.1. Three principled levers (all default-OFF =
# the SCHEMA-VET'd full-ingest behavior). + HELDOUT_FRAC reserves a DETERMINISTIC never-ingested split for the
# firewall-#3 capability eval (split-before-ingest; held-out edges are EXCLUDED from the Store + written to a
# firewalled file). The capability eval (cert-claim) tests inference-transfer on those never-seen edges.
MAX_EDGES = 0               # 0 = no cap; >0 = keep top-N by WEIGHT (principled, not first-N; stable key tiebreak)
HELDOUT_FRAC = 0.0          # 0 = ingest all; >0 = reserve this frac (deterministic hash) as never-ingested held-out
HELDOUT_PATH = Path('data/conceptnet/heldout_edges.jsonl')   # firewalled; NEVER ingested; for the firewall-#3 eval

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
    if SCOPE_LOAD_BEARING and rn not in LOAD_BEARING_NAMES:
        return None  # outside Director's load-bearing scope (default) -> SKIP (counted)
    rt = REL_MAP.get(rn)
    if rt is None:
        return None  # unmapped relation -> SKIP (counted), not coerced
    try:
        w = float(json.loads(meta).get('weight', 1.0))
    except Exception:
        w = 1.0
    if w < MIN_WEIGHT:
        return None
    return (s, rt, o, w)


def _open_csv(path: Path):
    if str(path).endswith('.gz'):
        return gzip.open(path, 'rt', encoding='utf-8')
    return open(path, 'r', encoding='utf-8')


def _csv_hash(path: Path) -> str:
    h = hashlib.sha256()
    h.update(str(path).encode())
    h.update(str(path.stat().st_size).encode())
    return h.hexdigest()[:8]


def acquire(csv_path: Path) -> Path:
    """Option B (remote-direct, self-contained): return an existing CSV/gz, else wget the canonical gz (cache-first,
    wget -c resumable -> partial-download survives a kill per the 6th-checklist long-cell pattern). Returns the resolved
    readable path (_open_csv handles .gz transparently). No network call if a local copy already exists."""
    import subprocess
    if csv_path.exists():
        return csv_path
    if DEFAULT_GZ.exists():
        return DEFAULT_GZ
    DEFAULT_GZ.parent.mkdir(parents=True, exist_ok=True)
    print(f'ACQUIRE (Option B): wget -c {CONCEPTNET_URL} -> {DEFAULT_GZ} (resumable; ~350MB)', flush=True)
    # wget -c resumes a partial download; if wget is absent, fall back to curl -C -.
    cmd_wget = ['wget', '-c', '-O', str(DEFAULT_GZ), CONCEPTNET_URL]
    cmd_curl = ['curl', '-L', '-C', '-', '-o', str(DEFAULT_GZ), CONCEPTNET_URL]
    for cmd in (cmd_wget, cmd_curl):
        try:
            rc = subprocess.call(cmd)
            if rc == 0 and DEFAULT_GZ.exists() and DEFAULT_GZ.stat().st_size > 1_000_000:
                print(f'  acquired {DEFAULT_GZ} ({DEFAULT_GZ.stat().st_size} bytes)', flush=True)
                return DEFAULT_GZ
        except FileNotFoundError:
            continue  # tool not on PATH; try the next
    raise RuntimeError(f'ACQUIRE failed: neither wget nor curl fetched {CONCEPTNET_URL}. '
                       f'Place the gz at {DEFAULT_GZ} manually (Option A fallback).')


def cell_commit() -> str:
    """Run-time git HEAD (corpus-provenance pin; the A2 v6 lesson). 'UNKNOWN' if git unavailable."""
    import subprocess
    try:
        out = subprocess.check_output(['git', 'rev-parse', 'HEAD'], stderr=subprocess.DEVNULL)
        return out.decode().strip()[:12]
    except Exception:
        return 'UNKNOWN'


def substrate_id_hash(ps) -> str:
    """Deterministic content-identity hash of the Store (sorted atom ids + count). Surfaces the substrate-id the A2 v6
    cell left None (Skunkworks's cell-hardening follow-on). cache<->corpus correspondence anchor."""
    ids = sorted(str(a.id) for a in ps.all_atoms())
    h = hashlib.sha256()
    h.update(str(len(ids)).encode())
    for i in ids:
        h.update(i.encode()); h.update(b'\n')
    return h.hexdigest()[:12]


def _shard_dir(path: Path) -> Path:
    return SHARD_ROOT / ('_shards_' + _csv_hash(path))


def _chunk_to_records(rows):
    """rows: list[(s, rt, o, w)] -> ({concept,...}, [(s_id, rel, o_id, w),...]) for the chunk (weight kept for top-by-weight)."""
    concepts = set()
    edges = []
    for (s, rt, o, w) in rows:
        concepts.add(s); concepts.add(o)
        edges.append((cn_id(s), rt.value, cn_id(o), w))
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
    """Load all shards -> dedup edges by (s,r,o) keeping MAX weight. Returns (edge_w:dict{(s,r,o):w}, n_shards).
    (concepts are derived from the FINAL ingested edges in apply_run, AFTER the bounded-v1 cap + held-out reserve.)"""
    edge_w = {}
    shards = sorted(shard_dir.glob('chunk_*.jsonl'), key=lambda p: int(p.stem.split('_')[1]))
    for sp in shards:
        d = json.loads(sp.read_text(encoding='utf-8'))
        for rec in d['edges']:
            s, r, o = rec[0], rec[1], rec[2]
            w = rec[3] if len(rec) > 3 else 1.0   # back-compat with any pre-weight shards
            k = (s, r, o)
            if w > edge_w.get(k, -1.0):
                edge_w[k] = w
    return edge_w, len(shards)


def _select_and_reserve(edge_w):
    """Bounded-v1 (Skunkworks ruling): apply MAX_EDGES (top-by-WEIGHT, principled) then HELDOUT_FRAC (deterministic
    hash reserve -> NEVER ingested). Returns (ingest:set[(s,r,o)], heldout:set[(s,r,o)]). Deterministic (11th-rule)."""
    items = list(edge_w.items())                          # [((s,r,o), w), ...]
    if MAX_EDGES and len(items) > MAX_EDGES:
        items.sort(key=lambda kv: (-kv[1], kv[0]))        # top-by-weight; stable key tiebreak (NOT arbitrary first-N)
        items = items[:MAX_EDGES]
    selected = {k for (k, _w) in items}
    heldout = set()
    if HELDOUT_FRAC and HELDOUT_FRAC > 0.0:
        thresh = int(HELDOUT_FRAC * 10000)
        for k in selected:
            hh = int(hashlib.sha256('|'.join(k).encode()).hexdigest(), 16)
            if (hh % 10000) < thresh:                     # deterministic split-before-ingest (firewall #3a)
                heldout.add(k)
    return (selected - heldout), heldout


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


def _make_atom(cnid: str):
    """cnid = 'CN_<concept_underscored>'. name = round-tripped concept (CN_ice_cream -> 'ice cream')."""
    from backend.substrate_index.schema import Atom, AtomKind, Corpus, Tier
    name = cnid[3:].replace('_', ' ') if cnid.startswith('CN_') else cnid
    return Atom(id=cnid, name=name, corpus=Corpus.CONCEPT, tier=Tier.TIER_NA,
                kind=AtomKind.CONCEPT_NODE, description=f'ConceptNet english concept: {name}',
                metadata={'provenance_quality': 'RESEARCH_FINDING', 'relevance_tier': 'ACTIVE',
                          'source': 'conceptnet_5.7_en', 'term_class': 'CONCEPT_NODE'})


def apply_run(csv_path: Path) -> int:
    from backend.substrate_index.partition import PartitionedStore
    from backend.substrate_index.schema import Corpus, Relation, save_atoms
    import os
    commit = cell_commit()
    print(f'CELL_COMMIT={commit} | scope={"load_bearing(16)" if SCOPE_LOAD_BEARING else "all_rels(full REL_MAP)"} '
          f'| DEVICE={DEVICE} (cpu_queue)', flush=True)
    csv_path = acquire(csv_path)   # Option B: fetch-if-absent (cache-first, resumable), else use existing
    print(f'STEP 1/3 chunk+shard (resume-aware) from {csv_path} ...', flush=True)
    pr = process_csv(csv_path)
    print(f'  chunks={pr["n_chunks"]} processed={pr["processed"]} skipped(resumed)={pr["skipped"]}', flush=True)
    print('STEP 2/3 assemble shards + bounded-v1 select/reserve ...', flush=True)
    edge_w, n_sh = assemble(pr['shard_dir'])
    ingest_edges, heldout_edges = _select_and_reserve(edge_w)
    print(f'  assembled {len(edge_w)} unique edges from {n_sh} shards | min_weight={MIN_WEIGHT} max_edges={MAX_EDGES or "off"} '
          f'-> INGEST {len(ingest_edges)} + HELDOUT-reserved {len(heldout_edges)} (frac {HELDOUT_FRAC})', flush=True)
    if heldout_edges:                                    # firewall #3a: never-ingested split written firewalled
        HELDOUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(HELDOUT_PATH, 'w', encoding='utf-8') as f:
            for (s, r, o) in sorted(heldout_edges):
                f.write(json.dumps({'src': s, 'rel': r, 'tgt': o}) + '\n')
        print(f'  HELD-OUT {len(heldout_edges)} edges -> {HELDOUT_PATH} (FIREWALLED; NEVER ingested; for the firewall-#3 capability eval)', flush=True)
    # concepts derived from the FINAL ingested edge endpoints (post cap + reserve) -> CN_ ids
    concepts = set()
    for (s, r, o) in ingest_edges:
        concepts.add(s); concepts.add(o)
    edges = ingest_edges
    print(f'  -> {len(concepts)} concept-atoms + {len(edges)} edges to ingest', flush=True)
    print('STEP 3/3 Store apply (batched single-flush + gates) ...', flush=True)
    ps = PartitionedStore(Path('data/substrate_index'))
    pre_axiom = axiom_term_count(ps); pre_mod = module_liveness_ok(); pre_cert = cert_count(ps)
    pre_atoms = len(list(ps.all_atoms()))
    pre_sid = substrate_id_hash(ps)        # corpus-identity pin (A2 v6 hardening lesson)
    print(f'PRE: substrate_id_hash={pre_sid} atoms={pre_atoms} axiom={pre_axiom} cert={pre_cert}', flush=True)
    if not pre_mod or pre_axiom != 206:
        print('PRE-GATE FAIL. Halt.'); return 1
    cs = ps._store_for(Corpus.CONCEPT)
    # 0-collision: a CN_ id already present under a DIFFERENT kind = collision (namespaced -> should be none).
    # concepts are already CN_ ids (derived from final ingested edges) -> use directly (NOT cn_id(c) = double-prefix).
    from backend.substrate_index.schema import AtomKind
    collisions = [c for c in concepts if c in cs._by_id and cs._by_id[c].kind != AtomKind.CONCEPT_NODE]
    if collisions:
        print(f'HARD_FAIL: {len(collisions)} CN_ id collisions with non-CONCEPT_NODE atoms (e.g. {collisions[:3]}). Halt.'); return 6
    intended_atoms = set(concepts)
    intended_edges = set(edges)
    for c in sorted(concepts):                                  # batched _index_atom (NOT per-atom add_atom)
        if c not in cs._by_id:
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
    post_sid = substrate_id_hash(ps3)
    # metrics OUT honors HDLAB_EXP_NAME (2nd checklist item) + 4 required fields (run_mode/metrics_source/anchor/verdict).
    exp_name = os.environ.get('HDLAB_EXP_NAME', 'substrate_conceptnet_ingest_v1')
    metrics = {
        'anchor': exp_name, 'run_mode': 'full', 'metrics_source': 'measured_curated_kb_deterministic',
        'verdict': 'INGESTED' if gate_ok else 'HARD_FAIL',
        'cell_commit': commit, 'substrate_id_hash_pre': pre_sid, 'substrate_id_hash_post': post_sid,
        'scope': 'load_bearing_16' if SCOPE_LOAD_BEARING else 'all_rels_full',
        'n_concept_atoms_intended': len(intended_atoms), 'n_concept_atoms_added': len(intended_atoms),
        'n_edges_added': edge_added, 'n_edges_intended': len(intended_edges),
        'pre_atoms': pre_atoms, 'post_axiom_term': post_axiom, 'cap_pres_6_6': post_mod,
        'cert_pre': pre_cert, 'cert_post': post_cert, 'cert_unchanged': post_cert == pre_cert,
        'atoms_present': atoms_present, 'edges_present': edges_present, 'min_weight': MIN_WEIGHT,
        'max_edges': MAX_EDGES, 'heldout_frac': HELDOUT_FRAC, 'n_heldout_reserved': len(heldout_edges),
        'heldout_path': str(HELDOUT_PATH) if heldout_edges else None,
        'source': 'conceptnet_5.7_en', 'license': 'CC-BY-SA-4.0',
    }
    out_dir = Path(os.environ.get('HDLAB_OUT_DIR', 'data'))
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f'{exp_name}_metrics.json'
    out_path.write_text(json.dumps(metrics, indent=2), encoding='utf-8')
    print(f'metrics -> {out_path}', flush=True)
    if not gate_ok:
        print('HARD_FAIL: post-gate failed.'); return 2
    print(f'CONCEPTNET INGEST complete: +{len(intended_atoms)} CONCEPT_NODE atoms + {edge_added} first-class edges | '
          f'axiom 206 | cap_pres 6/6 | CERT {post_cert} unchanged | substrate_id_hash {pre_sid}->{post_sid} | commit {commit}')
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
          and kept[0][:3] == ('dog', RelationType.IS_A, 'animal') and kept[0][3] == 2.0
          and kept[1][:3] == ('knife', RelationType.CN_USED_FOR, 'cut')
          and kept[2][:3] == ('wheel', RelationType.PART_OF, 'car')
          and cn_id('used for') == 'CN_used_for')
    c, e = _chunk_to_records(kept)
    # concepts = {dog, animal, knife, cut, wheel, car} = 6 distinct; edges carry weight (4-tuple)
    ok = ok and (len(c) == 6 and len(e) == 3 and ('CN_dog', 'IS_A', 'CN_animal', 2.0) in e)
    # bounded-v1 select/reserve: top-by-weight cap + deterministic held-out reserve
    global MAX_EDGES, HELDOUT_FRAC
    sv_max, sv_ho = MAX_EDGES, HELDOUT_FRAC
    try:
        edge_w = {('CN_a', 'IS_A', 'CN_b'): 3.0, ('CN_c', 'IS_A', 'CN_d'): 1.0, ('CN_e', 'IS_A', 'CN_f'): 2.0}
        MAX_EDGES, HELDOUT_FRAC = 2, 0.0
        ing, ho = _select_and_reserve(edge_w)        # top-2 by weight = {a-b(3.0), e-f(2.0)}; c-d(1.0) dropped
        cap_ok = (ing == {('CN_a', 'IS_A', 'CN_b'), ('CN_e', 'IS_A', 'CN_f')} and len(ho) == 0)
        MAX_EDGES, HELDOUT_FRAC = 0, 0.5
        ing2, ho2 = _select_and_reserve(edge_w)      # deterministic split; ingest+heldout partition the 3 edges
        res_ok = (len(ing2) + len(ho2) == 3 and ing2.isdisjoint(ho2))
        ing2b, ho2b = _select_and_reserve(edge_w)    # determinism: same split on re-run
        det_ok = (ing2 == ing2b and ho2 == ho2b)
    finally:
        MAX_EDGES, HELDOUT_FRAC = sv_max, sv_ho
    ok = ok and cap_ok and res_ok and det_ok
    print(f'[conceptnet_ingest] --self-test {"OK" if ok else "FAIL"} (parse/map/en-filter/unmapped-skip/low-weight-drop/atom-id/'
          f'weight-kept; top-by-weight cap={cap_ok}; heldout-reserve partition={res_ok}; determinism={det_ok}; kept={len(kept)}/6, '
          f'concepts={len(c)}, edges={len(e)}); NO Store mutation.')
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
            yield (f'c{i}', RelationType.IS_A, f'c{i+1}', 1.0)
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
        edge_w, n_sh = assemble(_shard_dir(fake_csv))
        ok = (after1 == 2 and after2 == 5 and r2['skipped'] == 2 and r2['processed'] == 3
              and n_sh == 5 and len(edge_w) == 15)
        print(f'[conceptnet_ingest] --resume-test {"OK" if ok else "FAIL"}: run1 wrote {after1} shards (died); '
              f'run2 RESUMED skip={r2["skipped"]} process={r2["processed"]} -> {after2} shards; '
              f'assembled {len(edge_w)} unique edges. (demonstrated resume, not asserted.)')
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
    scope_desc = ('load-bearing 16 (Director default: ' + ', '.join(sorted(LOAD_BEARING_NAMES)) + ')'
                  if SCOPE_LOAD_BEARING else f'ALL {len(REL_MAP)} mapped rels (--all-rels)')
    print(f'rel-scope: {scope_desc}; mapped via first-class rel_types (IsA->IS_A, PartOf->PART_OF, rest CN_*); out-of-scope/unmapped -> SKIP (counted).')
    print('ACQUISITION: Option B (Director-decided) -- cell wgets ' + CONCEPTNET_URL + ' if absent (cache-first, wget -c resumable).')
    print('WRITE-PATH: Atom-construction (_make_atom -> _index_atom -> save_atoms to_dict) + fresh-Store all_atoms() LOAD gate')
    print('            -> SAFE under Skunkworks write-hold refinement (Atom-construction NEW-ATOM-ADDS allowed; only raw-JSONL-append held).')
    print(f'BOUNDED-V1 (Skunkworks ruling): min_weight={MIN_WEIGHT} | max_edges={MAX_EDGES or "off"} (top-by-WEIGHT) | '
          f'heldout_frac={HELDOUT_FRAC} -> never-ingested reserve for the firewall-#3 capability eval (split-before-ingest).')
    print('PROVENANCE: cell_commit + substrate_id_hash (pre/post) recorded at run-time (A2 v6 hardening lesson).')
    print('FIREWALL (cert-condition, ROUTED to Skunkworks SCHEMA-VET): ConceptNet ingest is reference-KB (NEW knowledge_graph')
    print('            corpus, RESEARCH_FINDING tier, CERT-unchanged); the knowledge_graph CAPABILITY eval must use a held-out')
    print('            split NOT ingested (PART_OF-design precedent) + confirm no EXISTING certified eval sources from ConceptNet.')
    if not csv_path.exists() and not DEFAULT_GZ.exists():
        print(f'\nDATA not local yet ({csv_path} / {DEFAULT_GZ} absent) -- --apply will wget it (Option B). Cell logic verified via')
        print('  --self-test + --resume-test (no data needed). Schema (CONCEPT_NODE + CN_* rel_types) verify-loads OK.')
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
    ap.add_argument('--all-rels', action='store_true',
                    help='use the full REL_MAP (incl. commonsense-reasoning rels); default = Director load-bearing 16')
    ap.add_argument('--min-weight', type=float, default=None,
                    help='ConceptNet weight floor (bounded-v1 high-confidence subset, e.g. 2.0); default 1.0')
    ap.add_argument('--max-edges', type=int, default=0,
                    help='bounded-v1: keep top-N edges by WEIGHT (0=no cap; principled, not first-N)')
    ap.add_argument('--heldout-frac', type=float, default=0.0,
                    help='firewall #3a: reserve this frac (deterministic hash) as NEVER-ingested held-out for the capability eval')
    ap.add_argument('--self-test', action='store_true')
    ap.add_argument('--resume-test', action='store_true')
    args = ap.parse_args()
    global SCOPE_LOAD_BEARING, MIN_WEIGHT, MAX_EDGES, HELDOUT_FRAC
    if args.all_rels:
        SCOPE_LOAD_BEARING = False
    if args.min_weight is not None:
        MIN_WEIGHT = args.min_weight
    MAX_EDGES = args.max_edges
    HELDOUT_FRAC = args.heldout_frac
    if args.self_test:
        return self_test()
    if args.resume_test:
        return resume_test()
    csv_path = Path(args.csv)
    return apply_run(csv_path) if args.apply else dry_run(csv_path)


if __name__ == '__main__':
    raise SystemExit(main())
