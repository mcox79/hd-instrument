#!/usr/bin/env python3
"""build_lexicon_foundation_index.py -- ONE-TIME OFFLINE BUILD of the frozen lexicon foundation asset.

problem: the_nltk_library_is_called_at_read_time_in_37_hdlab_modules_78_sites_... (priority 127)

THIS IS THE ONLY PLACE IN THE REPO THAT IS ALLOWED TO IMPORT nltk. It runs ONCE, offline, and writes
    data/frontend_assets/lexicon_foundation_v1.sqlite      the addressed lexical store
    data/frontend_assets/lexicon_foundation_graph_v1.npz   the frozen spreading-activation adjacency
which hdlab/lexicon_foundation.py then serves at read time with NO external library in the call chain.

WHY AN ASSET AND NOT A LIBRARY CALL (the brain's mechanism). Lexical knowledge -- the sense inventory of a
word, its supersense, its taxonomic parents, its argument frames, its polarity -- is STORED in the anterior-
temporal hub and its spokes and retrieved by content-addressed lookup at read time (Patterson, Nestor & Rogers
2007; Binder & Desai 2011). Acquisition is a DEVELOPMENTAL, offline process; retrieval is an address ->
content read. A library that re-derives the store while reading is the acquisition machinery running inside
the read. This builder IS the development phase, run once.

WHAT IS FROZEN (exactly the API surface hdlab/ calls, enumerated from the 75 import sites at HEAD):
  wordnet   per-synset packet: name, pos, offset, lexname, definition, examples, frame_ids, lemmas
            (name/key/count, in WordNet order) and every relation list nltk's Synset accessors return, IN
            NLTK'S OWN ORDER (nltk sorts each relation by target name, so order is inherited, not invented):
            hypernyms, instance_hypernyms, hyponyms, instance_hyponyms, member/part/substance holonyms and
            meronyms, attributes, similar_tos, also_sees, verb_groups, entailments, causes, topic/region/usage
            domains + members. Lemma-level: antonyms, pertainyms, derivationally_related_forms.
            Plus the two INDEXES synsets()/synset() need: form -> pos -> [offsets] (nltk's
            _lemma_pos_offset_map, including its ADJ -> ADJ_SAT duplication) and (file-pos, offset) -> name.
  verbnet   classids() and classids(lemma), lemmas(cid), themroles(cid), frames(cid) -- frames reduced to the
            fields the call sites read (description/example/syntax primary + semantics predicate names).
  framenet  frame names/ids, per-frame FE table with coreType, lemma -> frames, frame_relations().
  opinion_lexicon positive()/negative(); stopwords words('english').
  GRAPH     the GroundedSemanticGraph base edge list per source (relations_glosses / conceptnet / syntagnet)
            over the same sorted-by-name synset order, so build() becomes a LOAD of the identical matrix.

Run (offline, ~10 min):
    .venv/Scripts/python.exe tools/build_lexicon_foundation_index.py --all
    .venv/Scripts/python.exe tools/build_lexicon_foundation_index.py --wordnet --verbnet --framenet --wordlists
    .venv/Scripts/python.exe tools/build_lexicon_foundation_index.py --graph
"""
from __future__ import annotations
import argparse
import json
import os
import sqlite3
import sys
import time

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

ASSET_DIR = os.path.join(_REPO, "data", "frontend_assets")
DB_PATH = os.path.join(ASSET_DIR, "lexicon_foundation_v1.sqlite")
GRAPH_PATH = os.path.join(ASSET_DIR, "lexicon_foundation_graph_v1.npz")

# Every Synset relation accessor nltk exposes that any hdlab site calls, plus the ones a frozen taxonomy walk
# needs (instance_hyponyms for symmetry, the domain pointers for completeness). The VALUE is the accessor name;
# the builder calls it and stores the names it returns IN ORDER.
SYNSET_RELATIONS = (
    "hypernyms", "instance_hypernyms", "hyponyms", "instance_hyponyms",
    "member_holonyms", "part_holonyms", "substance_holonyms",
    "member_meronyms", "part_meronyms", "substance_meronyms",
    "attributes", "similar_tos", "also_sees", "verb_groups", "entailments", "causes",
    "topic_domains", "region_domains", "usage_domains",
    "in_topic_domains", "in_region_domains", "in_usage_domains",
)
LEMMA_RELATIONS = ("antonyms", "pertainyms", "derivationally_related_forms")

SCHEMA = """
CREATE TABLE IF NOT EXISTS meta (k TEXT PRIMARY KEY, v TEXT);
CREATE TABLE IF NOT EXISTS synset (
    name TEXT PRIMARY KEY, pos TEXT, offset INTEGER, lexname TEXT, definition TEXT,
    examples TEXT, frame_ids TEXT, lemmas TEXT, rels TEXT);
CREATE TABLE IF NOT EXISTS synset_offset (pos TEXT, offset INTEGER, name TEXT, PRIMARY KEY (pos, offset));
CREATE TABLE IF NOT EXISTS lemma_index (form TEXT, pos TEXT, offsets TEXT, PRIMARY KEY (form, pos));
CREATE TABLE IF NOT EXISTS lemma_rel (key TEXT PRIMARY KEY, rels TEXT);
CREATE TABLE IF NOT EXISTS lemma_key (key TEXT PRIMARY KEY, synset TEXT, idx INTEGER);
CREATE TABLE IF NOT EXISTS wordlist (name TEXT PRIMARY KEY, words TEXT);
CREATE TABLE IF NOT EXISTS vn_class (cid TEXT PRIMARY KEY, themroles TEXT, frames TEXT, lemmas TEXT);
CREATE TABLE IF NOT EXISTS vn_lemma (lemma TEXT PRIMARY KEY, cids TEXT);
CREATE TABLE IF NOT EXISTS fn_frame (name TEXT PRIMARY KEY, fid INTEGER, definition TEXT, fes TEXT,
                                     lus TEXT, rels TEXT);
CREATE TABLE IF NOT EXISTS fn_lemma (lemma TEXT PRIMARY KEY, frames TEXT);
CREATE TABLE IF NOT EXISTS fn_rel (idx INTEGER PRIMARY KEY, sup TEXT, sub TEXT, type TEXT);
"""


def _db(path=DB_PATH):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    con = sqlite3.connect(path)
    con.executescript(SCHEMA)
    return con


def _J(x):
    return json.dumps(x, separators=(",", ":"), sort_keys=False)


def _meta(con, k, v):
    con.execute("INSERT OR REPLACE INTO meta (k, v) VALUES (?, ?)", (k, str(v)))


# ------------------------------------------------------------------------------- WordNet
def build_wordnet(con, verbose=True):
    from nltk.corpus import wordnet as wn
    import nltk
    t0 = time.time()
    syns = list(wn.all_synsets())
    if verbose:
        print("wordnet: %d synsets (%.0fs)" % (len(syns), time.time() - t0), flush=True)
    rows, offs, lrels = [], [], []
    for n, s in enumerate(syns):
        name = s.name()
        pos = s.pos()
        rels = {}
        for r in SYNSET_RELATIONS:
            acc = getattr(s, r, None)
            if acc is None:
                continue
            try:
                got = [t.name() for t in acc()]
            except Exception:
                got = []
            if got:
                rels[r] = got
        lems = []
        for lm in s.lemmas():
            lems.append([lm.name(), lm.key(), int(lm.count())])
            lr = {}
            for r in LEMMA_RELATIONS:
                try:
                    got = [x.key() for x in getattr(lm, r)()]
                except Exception:
                    got = []
                if got:
                    lr[r] = got
            if lr:
                lrels.append((lm.key(), _J(lr)))
        try:
            fids = [int(x) for x in s.frame_ids()]
        except Exception:
            fids = []
        rows.append((name, pos, int(s.offset()), s.lexname(), s.definition(),
                     _J(list(s.examples())), _J(fids), _J(lems), _J(rels)))
        file_pos = "a" if pos in ("a", "s") else pos
        offs.append((file_pos, int(s.offset()), name))
        if verbose and (n + 1) % 20000 == 0:
            print("  ... %d/%d (%.0fs)" % (n + 1, len(syns), time.time() - t0), flush=True)
    con.executemany("INSERT OR REPLACE INTO synset VALUES (?,?,?,?,?,?,?,?,?)", rows)
    con.executemany("INSERT OR REPLACE INTO synset_offset VALUES (?,?,?)", offs)
    con.executemany("INSERT OR REPLACE INTO lemma_rel VALUES (?,?)", lrels)

    # the lemma -> pos -> offsets index, VERBATIM from nltk's own loaded map (including its
    # ADJ -> ADJ_SAT duplication), so synsets()/synset() reproduce nltk's ORDER exactly.
    idx = wn._lemma_pos_offset_map        # populated by WordNetCorpusReader.__init__, before any query
    lrows = []
    for form, per_pos in idx.items():
        for p, offsets in per_pos.items():
            lrows.append((form, p, _J([int(o) for o in offsets])))
    con.executemany("INSERT OR REPLACE INTO lemma_index VALUES (?,?,?)", lrows)
    _meta(con, "wordnet_version", wn.get_version())
    _meta(con, "nltk_version", nltk.__version__)
    _meta(con, "n_synsets", len(rows))
    _meta(con, "n_lemma_forms", len(idx))
    _meta(con, "n_lemma_index_rows", len(lrows))
    _meta(con, "n_lemma_rel_rows", len(lrels))
    _meta(con, "n_lexnames", len({r[3] for r in rows}))
    con.commit()
    if verbose:
        print("wordnet: %d synset rows, %d offset rows, %d lemma-index rows, %d lemma-rel rows (%.0fs)"
              % (len(rows), len(offs), len(lrows), len(lrels), time.time() - t0), flush=True)
    return len(rows)


def build_key_index(con, verbose=True):
    """lemma sense-key -> (synset, position) so a frozen lemma-level relation (antonym / pertainym /
    derivationally-related) resolves to a Lemma. Pure post-process of the synset table: NO nltk."""
    rows = []
    for name, lems in con.execute("SELECT name, lemmas FROM synset"):
        for i, (_n, key, _c) in enumerate(json.loads(lems)):
            rows.append((key, name, i))
    con.executemany("INSERT OR REPLACE INTO lemma_key VALUES (?,?,?)", rows)
    _meta(con, "n_lemma_keys", len(rows))
    con.commit()
    if verbose:
        print("key index: %d lemma sense-keys" % len(rows), flush=True)
    return len(rows)


# ------------------------------------------------------------------------------- VerbNet
def build_verbnet(con, verbose=True):
    from nltk.corpus import verbnet as vn
    t0 = time.time()
    cids = sorted(vn.classids())
    per_lemma = {}
    rows = []
    for cid in cids:
        try:
            roles = vn.themroles(cid)
        except Exception:
            roles = []
        rr = []
        for r in roles:
            rr.append({"modifiers": [{"type": m.get("type"), "value": m.get("value")}
                                     for m in r.get("modifiers", [])],
                       "type": r.get("type")})
        frames = []
        try:
            for f in vn.frames(cid):
                frames.append({"description": f.get("description"),
                               "example": f.get("example"),
                               "syntax": [{"pos_tag": e.get("pos_tag"), "modifiers": e.get("modifiers")}
                                          for e in f.get("syntax", [])],
                               "semantics": [{"predicate_value": p.get("predicate_value")}
                                             for p in f.get("semantics", [])]})
        except Exception:
            pass
        try:
            lems = sorted(vn.lemmas(cid))
        except Exception:
            lems = []
        rows.append((cid, _J(rr), _J(frames), _J(lems)))
        for lm in lems:
            per_lemma.setdefault(lm, [])
    # classids(lemma) returns the SUBCLASS ids for that lemma, in nltk's order -- take it verbatim
    for lm in list(per_lemma):
        try:
            per_lemma[lm] = list(vn.classids(lm))
        except Exception:
            per_lemma[lm] = []
    con.executemany("INSERT OR REPLACE INTO vn_class VALUES (?,?,?,?)", rows)
    con.executemany("INSERT OR REPLACE INTO vn_lemma VALUES (?,?)",
                    [(lm, _J(cs)) for lm, cs in sorted(per_lemma.items())])
    _meta(con, "n_vn_classes", len(rows))
    _meta(con, "n_vn_lemmas", len(per_lemma))
    con.commit()
    if verbose:
        print("verbnet: %d classes, %d lemmas (%.0fs)" % (len(rows), len(per_lemma), time.time() - t0), flush=True)
    return len(rows)


# ------------------------------------------------------------------------------- FrameNet
def build_framenet(con, verbose=True):
    from nltk.corpus import framenet as fn
    t0 = time.time()
    frows, lemmap, rels = [], {}, []
    for f in fn.frames():
        fes = {}
        for nm, fe in (f.FE or {}).items():
            fes[nm] = {"coreType": getattr(fe, "coreType", None), "name": nm}
        lus = list(f.lexUnit or {})                     # "move.v" keys -- every call site reads .lexUnit.keys()
        frels = []
        for r in (getattr(f, "frameRelations", []) or []):
            try:
                frels.append({"type": r.type.name, "sup": r.superFrameName, "sub": r.subFrameName})
            except Exception:
                continue
        frows.append((f.name, int(f.ID), getattr(f, "definition", "") or "", _J(fes), _J(lus), _J(frels)))
        for lu in lus:
            lemma = str(lu).rsplit(".", 1)[0].lower()
            lemmap.setdefault(lemma, [])
            if f.name not in lemmap[lemma]:
                lemmap[lemma].append(f.name)
    for i, r in enumerate(fn.frame_relations()):
        try:
            rels.append((i, r.superFrameName, r.subFrameName, r.type.name))
        except Exception:
            continue
    con.executemany("INSERT OR REPLACE INTO fn_frame VALUES (?,?,?,?,?,?)", frows)
    con.executemany("INSERT OR REPLACE INTO fn_lemma VALUES (?,?)",
                    [(k, _J(v)) for k, v in sorted(lemmap.items())])
    con.executemany("INSERT OR REPLACE INTO fn_rel VALUES (?,?,?,?)", rels)
    _meta(con, "n_fn_frames", len(frows))
    _meta(con, "n_fn_lemmas", len(lemmap))
    _meta(con, "n_fn_relations", len(rels))
    con.commit()
    if verbose:
        print("framenet: %d frames, %d lemmas, %d relations (%.0fs)"
              % (len(frows), len(lemmap), len(rels), time.time() - t0), flush=True)
    return len(frows)


# ------------------------------------------------------------------------------- word lists
def build_wordlists(con, verbose=True):
    """Freeze the two flat word lists the live path reads. PER-CORPUS TOLERANT ON PURPOSE: on this machine
    nltk's `stopwords` corpus is NOT INSTALLED (measured 2026-09-15), so `causation_typing.py:669` has been
    silently taking its 50-word hand-written `except` fallback instead of nltk's 179-word list. Freezing an
    ABSENT list as present would CHANGE the read; the asset records the absence, the organ raises the same
    LookupError nltk raises, and the site's fallback fires exactly as today (byte-identical). The absence is
    reported in meta so it is a recorded fact rather than a silent degradation."""
    got, missing = [], []
    for name, fetch in (("opinion_positive", lambda: __import__("nltk.corpus", fromlist=["opinion_lexicon"]).opinion_lexicon.positive()),
                        ("opinion_negative", lambda: __import__("nltk.corpus", fromlist=["opinion_lexicon"]).opinion_lexicon.negative()),
                        ("stopwords_english", lambda: __import__("nltk.corpus", fromlist=["stopwords"]).stopwords.words("english"))):
        try:
            got.append((name, _J(list(fetch()))))
        except Exception as e:
            missing.append(name)
            _meta(con, "absent_" + name, type(e).__name__)
    con.executemany("INSERT OR REPLACE INTO wordlist VALUES (?,?)", got)
    for nm, js in got:
        _meta(con, "n_" + nm, len(json.loads(js)))
    _meta(con, "absent_wordlists", _J(missing))
    con.commit()
    if verbose:
        print("wordlists: %s%s" % (", ".join("%s=%d" % (nm, len(json.loads(js))) for nm, js in got),
                                   ("  ABSENT: %s" % ",".join(missing)) if missing else ""), flush=True)
    return len(got)


# ------------------------------------------------------------------------------- the frozen graph
def build_graph(verbose=True):
    """Freeze GroundedSemanticGraph's BASE edge list per source. The build is run with nltk exactly as it
    ships today, so the loaded matrix is identical by construction; the witness checks the CSR bytes."""
    import numpy as np
    from hdlab import grounded_semantic_graph as G
    t0 = time.time()
    syns = G._synsets_ordered()
    names = [s.name() for s in syns]
    syn2idx = {n: i for i, n in enumerate(names)}
    out = {"names": np.array(names, dtype=object)}
    for src, fn in G._SOURCE_EDGES.items():
        r, c = fn(syns, syn2idx)
        out["rows_" + src] = np.asarray(r, dtype=np.int32)
        out["cols_" + src] = np.asarray(c, dtype=np.int32)
        if verbose:
            print("graph: %-18s %9d edges (%.0fs)" % (src, len(r), time.time() - t0), flush=True)
    os.makedirs(os.path.dirname(GRAPH_PATH), exist_ok=True)
    np.savez_compressed(GRAPH_PATH, **out)
    if verbose:
        print("graph: wrote %s (%.1f MB, %.0fs)"
              % (GRAPH_PATH, os.path.getsize(GRAPH_PATH) / 1e6, time.time() - t0), flush=True)
    return GRAPH_PATH


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--wordnet", action="store_true")
    ap.add_argument("--verbnet", action="store_true")
    ap.add_argument("--framenet", action="store_true")
    ap.add_argument("--wordlists", action="store_true")
    ap.add_argument("--keyindex", action="store_true")
    ap.add_argument("--graph", action="store_true")
    ap.add_argument("--db", default=DB_PATH)
    a = ap.parse_args()
    do = lambda f: a.all or f                                   # noqa: E731
    if do(a.wordnet) or do(a.verbnet) or do(a.framenet) or do(a.wordlists) or do(a.keyindex):
        con = _db(a.db)
        _meta(con, "built_ts", time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
        _meta(con, "builder", "tools/build_lexicon_foundation_index.py")
        if do(a.wordnet):
            build_wordnet(con)
        if do(a.verbnet):
            build_verbnet(con)
        if do(a.framenet):
            build_framenet(con)
        if do(a.wordlists):
            build_wordlists(con)
        if do(a.keyindex):
            build_key_index(con)
        con.execute("VACUUM")
        con.commit()
        con.close()
        print("db: %s (%.1f MB)" % (a.db, os.path.getsize(a.db) / 1e6))
    if do(a.graph):
        build_graph()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
