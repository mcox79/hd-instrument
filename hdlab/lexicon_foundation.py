#!/usr/bin/env python3
"""hdlab/lexicon_foundation.py -- THE ONE lexical foundation organ: a frozen, content-addressed lexical store
served at read time with NO external library in the call chain.

LANDED from the problem `the_nltk_library_is_called_at_read_time_in_37_hdlab_modules_78_sites_to_read_static_
lexica_freeze_wordnet_verbnet_framenet_into_one_offline_asset_behind_one_lexicon_organ_and_retire_the_model_
stand_ins` (priority 127).

BRAIN STRUCTURE (PINNED). The anterior-temporal semantic HUB and its modality spokes (Patterson, Nestor &
Rogers 2007; Binder & Desai 2011; Ralph, Jefferies, Patterson & Rogers 2017). Lexical-semantic knowledge --
the sense inventory of a word, its supersense/category, its taxonomic parents, its argument frames, its
polarity -- is STORED there and retrieved by CONTENT-ADDRESSED lookup during comprehension: an address (a word
form, a sense) activates its stored pattern. Two properties of that structure are load-bearing here and are
what this organ implements:
  (1) ACQUISITION IS OFFLINE, RETRIEVAL IS A READ. The store is laid down developmentally; nothing in the
      comprehension loop re-derives it. A library that parses index files, builds maps and walks a graph
      WHILE READING is the acquisition machinery running inside the read -- the wrong computation, and the
      measured cost was 4,348,472 library calls on the first document of a 4-document read (this organ's
      cell, phase 1a).
  (2) ONE STORE, MANY READS. The hub is ONE structure read by many consumers, not 36 private lookups. Every
      hdlab site now addresses the same organ; the relation types (taxonomy / supersense / frames / polarity)
      are ARMS of the one store, not separate organs.

THE COMPUTATION IS COPIED, NOT APPROXIMATED. Every accessor here reproduces nltk 3.9.4 / WordNet 3.0
byte-for-byte on the live path's own queries -- including `synsets()`'s order (POS_LIST order x morphy-form
order x the index's own offset order), nltk's ADJ -> ADJ_SAT index duplication, and its per-relation sort by
target name. The morphological arm is NOT re-implemented: it delegates to hdlab.morphology, the glass-box
morphy organ already proven byte-identical over 6.3M comparisons. Same shape as that organ: exception store +
rules + lexical check read from a one-time offline export.

THE ASSET (built ONCE by tools/build_lexicon_foundation_index.py, the only nltk importer in the repo):
    data/frontend_assets/lexicon_foundation_v1.sqlite       117,659 synset packets / 206,978 lemma sense-keys
                                                            / 176,766 lemma-index rows / 45 lexnames
                                                            / 429 VerbNet classes / 1,221 FrameNet frames
    data/frontend_assets/lexicon_foundation_graph_v1.npz     the frozen spreading-activation adjacency
sqlite (not JSON) because the store is 78 MB: an addressed store should be READ at an address, not loaded
whole, and a reader that never asks a lexical question pays nothing but the file handle.

WHAT IS *NOT* BRAIN-FOUNDATIONAL AND IS NOT HIDDEN: the CONTENT is a human-curated lexicon (admissible static
supply, owner 2026-08-16 / 09-08), not knowledge this substrate acquired. The online propose-and-verify growth
path is the learner's job (`consolidation_gate`); this organ is the developmental store it grows from, and
`observe()` is the hook that records which addresses the read actually asks for, so growth has a target.

Glass-box, ASCII, deterministic. NO nltk, NO LLM, NO external tool at inference.
"""
from __future__ import annotations

__bf_status__ = "BF_SPIRIT"   # BF | BF_SPIRIT | NOT_BF | BF_UNPINNED | BF_UNVERIFIED ; mirrors notes/bf_status_registry.jsonl
__bf_verified__ = ("2026-09-15 pri 127 solver: content-addressed lexical store replacing 75 read-time nltk library "
                   "sites in 36 modules; byte-identical to nltk 3.9.4/WordNet 3.0 on every query the default read makes "
                   "(parity witness), poisoned-import witness green, morphological arm delegated to hdlab.morphology")
__bf_note__ = ("the STRUCTURE (offline-acquired hub read by content address) is the brain's; the CONTENT is a curated "
               "human lexicon = admissible static supply, not substrate-acquired knowledge -- growth is the learner's path")
__bf_corrections__ = []

import json
import os
import sqlite3
import threading
import warnings
from collections import deque
from typing import Dict, List, Optional, Sequence

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSET_DIR = os.path.join(_REPO, "data", "frontend_assets")
DB_PATH = os.environ.get("HDLAB_LEXICON_ASSET", os.path.join(ASSET_DIR, "lexicon_foundation_v1.sqlite"))
GRAPH_PATH = os.path.join(ASSET_DIR, "lexicon_foundation_graph_v1.npz")

POS_LIST = ["n", "v", "a", "r"]          # nltk's own order; synsets() with pos=None walks it in this order
NOUN, VERB, ADJ, ADV, ADJ_SAT = "n", "v", "a", "r", "s"
_FILE_POS = {"n": "n", "v": "v", "a": "a", "s": "a", "r": "r"}
# all_synsets() iteration order is NOT POS_LIST: nltk walks its _FILEMAP {ADJ:'adj', ADV:'adv', NOUN:'noun',
# VERB:'verb'}, i.e. adjectives first, then adverbs, nouns, verbs -- each file in ascending offset order.
# (Caught by the parity replay: 1 of the first 100,000 queries differed, and it was this one.)
_POS_RANK = {"a": 0, "r": 1, "n": 2, "v": 3}


class WordNetError(Exception):
    """Same name and role as nltk's WordNetError so a call site's `except` behaves identically."""


class LexiconAssetMissing(RuntimeError):
    """The frozen asset is absent -- a hard, LOUD failure. A missing store must never silently degrade a read
    (the defect this organ replaces: nltk's `stopwords` corpus is absent on this machine and one site has been
    silently taking a 50-word hand fallback instead of the 179-word list)."""


# ======================================================================================= the store
class _Store:
    """Lazy sqlite reader + per-process memo. One connection, one row per address, cached after first read."""

    def __init__(self, path: str = DB_PATH):
        self.path = path
        self._con: Optional[sqlite3.Connection] = None
        self._lock = threading.Lock()
        self._syn: Dict[str, Optional[dict]] = {}
        self._off: Dict[tuple, Optional[str]] = {}
        self._lix: Dict[tuple, List[int]] = {}
        self._lkey: Dict[str, Optional[tuple]] = {}
        self._lrel: Dict[str, dict] = {}
        self._wl: Dict[str, Optional[list]] = {}
        self._meta: Optional[Dict[str, str]] = None
        self._all_loaded = False
        self.n_reads = 0                 # observe(): how many addresses the read actually asked for

    def con(self) -> sqlite3.Connection:
        if self._con is None:
            with self._lock:                   # one connection per process, even if two consumers race here
                return self._connect()
        return self._con

    def _connect(self) -> sqlite3.Connection:
        if self._con is None:
            if not os.path.exists(self.path):
                raise LexiconAssetMissing(
                    "frozen lexicon asset not found: %s -- build it once with "
                    "`python tools/build_lexicon_foundation_index.py --all`" % self.path)
            self._con = sqlite3.connect(self.path, check_same_thread=False)
            for p in ("query_only = 1", "journal_mode = OFF", "synchronous = OFF",
                      "temp_store = MEMORY", "cache_size = -65536", "mmap_size = 268435456"):
                try:
                    self._con.execute("PRAGMA " + p)
                except sqlite3.Error:      # a pragma a build of sqlite does not support must not break a read
                    pass
        return self._con

    # -- addressed reads ---------------------------------------------------------------------------
    def synset_row(self, name: str) -> Optional[dict]:
        if name in self._syn:
            return self._syn[name]
        self.n_reads += 1
        r = self.con().execute("SELECT name,pos,offset,lexname,definition,examples,frame_ids,lemmas,rels "
                               "FROM synset WHERE name=?", (name,)).fetchone()
        row = None if r is None else {"name": r[0], "pos": r[1], "offset": r[2], "lexname": r[3],
                                      "definition": r[4], "examples": json.loads(r[5]),
                                      "frame_ids": json.loads(r[6]), "lemmas": json.loads(r[7]),
                                      "rels": json.loads(r[8])}
        self._syn[name] = row
        return row

    def offset_name(self, file_pos: str, offset: int) -> Optional[str]:
        k = (file_pos, int(offset))
        if k in self._off:
            return self._off[k]
        self.n_reads += 1
        r = self.con().execute("SELECT name FROM synset_offset WHERE pos=? AND offset=?", k).fetchone()
        self._off[k] = None if r is None else r[0]
        return self._off[k]

    def lemma_offsets(self, form: str, pos: str) -> List[int]:
        k = (form, pos)
        if k in self._lix:
            return self._lix[k]
        self.n_reads += 1
        r = self.con().execute("SELECT offsets FROM lemma_index WHERE form=? AND pos=?", k).fetchone()
        self._lix[k] = [] if r is None else json.loads(r[0])
        return self._lix[k]

    def lemma_of_key(self, key: str) -> Optional[tuple]:
        if key in self._lkey:
            return self._lkey[key]
        r = self.con().execute("SELECT synset,idx FROM lemma_key WHERE key=?", (key,)).fetchone()
        self._lkey[key] = None if r is None else (r[0], r[1])
        return self._lkey[key]

    def lemma_rels(self, key: str) -> dict:
        if key in self._lrel:
            return self._lrel[key]
        r = self.con().execute("SELECT rels FROM lemma_rel WHERE key=?", (key,)).fetchone()
        self._lrel[key] = {} if r is None else json.loads(r[0])
        return self._lrel[key]

    def wordlist(self, name: str) -> Optional[list]:
        if name in self._wl:
            return self._wl[name]
        r = self.con().execute("SELECT words FROM wordlist WHERE name=?", (name,)).fetchone()
        self._wl[name] = None if r is None else json.loads(r[0])
        return self._wl[name]

    def meta(self) -> Dict[str, str]:
        if self._meta is None:
            self._meta = {k: v for k, v in self.con().execute("SELECT k,v FROM meta")}
        return self._meta

    def all_synset_names(self, pos: Optional[str] = None) -> List[str]:
        """Every synset name in WordNet DATA-FILE order (pos file order, then offset) -- nltk's all_synsets
        order. Bulk: one query, and the rows are cached so the caller's per-synset reads are free."""
        if not self._all_loaded:
            rows = self.con().execute("SELECT name,pos,offset,lexname,definition,examples,frame_ids,lemmas,rels "
                                      "FROM synset").fetchall()
            for r in rows:
                if r[0] not in self._syn:
                    self._syn[r[0]] = {"name": r[0], "pos": r[1], "offset": r[2], "lexname": r[3],
                                       "definition": r[4], "examples": json.loads(r[5]),
                                       "frame_ids": json.loads(r[6]), "lemmas": json.loads(r[7]),
                                       "rels": json.loads(r[8])}
            self._all_loaded = True
        names = [(_POS_RANK[_FILE_POS[v["pos"]]], v["offset"], k) for k, v in self._syn.items() if v]
        if pos is not None:
            names = [t for t in names if self._syn[t[2]]["pos"] == pos or (pos == "a" and self._syn[t[2]]["pos"] == "s")]
        names.sort()
        return [t[2] for t in names]

    # -- the small tables --------------------------------------------------------------------------
    def one(self, sql: str, args=()):
        return self.con().execute(sql, args).fetchone()

    def many(self, sql: str, args=()):
        return self.con().execute(sql, args).fetchall()


_STORE: Optional[_Store] = None


def store() -> _Store:
    global _STORE
    if _STORE is None:
        _STORE = _Store()
    return _STORE


def asset_meta() -> Dict[str, str]:
    """The frozen asset's provenance: source versions, row counts, build timestamp, recorded absences."""
    return dict(store().meta())


def observe() -> int:
    """How many distinct addresses this process has read from the store. The hook the learner needs: growth
    targets the addresses a read actually asks for (the store is frozen, the DEMAND is observed)."""
    return store().n_reads


# ======================================================================================= WordNet objects
class Lemma:
    """A frozen WordNet lemma. Same accessor surface (and repr) as nltk's Lemma for the methods hdlab calls."""
    __slots__ = ("_synset_name", "_idx", "_name", "_key", "_count")

    def __init__(self, synset_name: str, idx: int, name: str, key: str, count: int):
        self._synset_name = synset_name
        self._idx = idx
        self._name = name
        self._key = key
        self._count = int(count)

    def name(self) -> str:
        return self._name

    def key(self) -> str:
        return self._key

    def count(self) -> int:
        return self._count

    def synset(self) -> "Synset":
        return Synset(self._synset_name)

    def _rel(self, kind: str) -> List["Lemma"]:
        out = []
        for k in store().lemma_rels(self._key).get(kind, []):
            loc = store().lemma_of_key(k)
            if loc is None:
                continue
            ss = Synset(loc[0])
            lems = ss.lemmas()
            if loc[1] < len(lems):
                out.append(lems[loc[1]])
        return out

    def antonyms(self) -> List["Lemma"]:
        return self._rel("antonyms")

    def pertainyms(self) -> List["Lemma"]:
        return self._rel("pertainyms")

    def derivationally_related_forms(self) -> List["Lemma"]:
        return self._rel("derivationally_related_forms")

    def __repr__(self):
        return "Lemma('%s.%s')" % (self._synset_name, self._name)

    def __eq__(self, other):
        return isinstance(other, Lemma) and other._key == self._key

    def __hash__(self):
        return hash(("Lemma", self._key))

    def __lt__(self, other):
        return self._name < getattr(other, "_name", "")


_SYNSET_CACHE: Dict[str, "Synset"] = {}


class Synset:
    """A frozen WordNet synset: ONE addressed read of the store returns the whole packet (gloss, lemmas,
    supersense, every relation), which is how a hub retrieval works -- an address activates a pattern, not one
    attribute. Flyweight: one object per name per process."""
    __slots__ = ("_name",)

    def __new__(cls, name: str):
        s = _SYNSET_CACHE.get(name)
        if s is None:
            s = object.__new__(cls)
            object.__setattr__(s, "_name", name)
            _SYNSET_CACHE[name] = s
        return s

    # -- the packet ---------------------------------------------------------------------------------
    def _row(self) -> dict:
        r = store().synset_row(self._name)
        if r is None:
            raise WordNetError("no synset %r in the frozen lexicon asset" % self._name)
        return r

    def name(self) -> str:
        return self._name

    def pos(self) -> str:
        return self._row()["pos"]

    def offset(self) -> int:
        return self._row()["offset"]

    def lexname(self) -> str:
        return self._row()["lexname"]

    def definition(self, lang: str = "eng") -> str:
        return self._row()["definition"]

    def examples(self, lang: str = "eng") -> List[str]:
        return list(self._row()["examples"])

    def frame_ids(self) -> List[int]:
        return list(self._row()["frame_ids"])

    def lemmas(self, lang: str = "eng") -> List[Lemma]:
        return [Lemma(self._name, i, n, k, c) for i, (n, k, c) in enumerate(self._row()["lemmas"])]

    def lemma_names(self, lang: str = "eng") -> List[str]:
        return [n for (n, _k, _c) in self._row()["lemmas"]]

    # -- relations (nltk order preserved by the builder; nltk sorts each list by target name) --------
    def _rel(self, kind: str) -> List["Synset"]:
        return [Synset(n) for n in self._row()["rels"].get(kind, [])]

    def hypernyms(self):
        return self._rel("hypernyms")

    def instance_hypernyms(self):
        return self._rel("instance_hypernyms")

    def hyponyms(self):
        return self._rel("hyponyms")

    def instance_hyponyms(self):
        return self._rel("instance_hyponyms")

    def member_holonyms(self):
        return self._rel("member_holonyms")

    def part_holonyms(self):
        return self._rel("part_holonyms")

    def substance_holonyms(self):
        return self._rel("substance_holonyms")

    def member_meronyms(self):
        return self._rel("member_meronyms")

    def part_meronyms(self):
        return self._rel("part_meronyms")

    def substance_meronyms(self):
        return self._rel("substance_meronyms")

    def attributes(self):
        return self._rel("attributes")

    def similar_tos(self):
        return self._rel("similar_tos")

    def also_sees(self):
        return self._rel("also_sees")

    def verb_groups(self):
        return self._rel("verb_groups")

    def entailments(self):
        return self._rel("entailments")

    def causes(self):
        return self._rel("causes")

    def topic_domains(self):
        return self._rel("topic_domains")

    def region_domains(self):
        return self._rel("region_domains")

    def usage_domains(self):
        return self._rel("usage_domains")

    def in_topic_domains(self):
        return self._rel("in_topic_domains")

    def in_region_domains(self):
        return self._rel("in_region_domains")

    def in_usage_domains(self):
        return self._rel("in_usage_domains")

    # -- taxonomy walks (EXACT ports of nltk 3.9.4) --------------------------------------------------
    def hypernym_paths(self) -> List[List["Synset"]]:
        paths = []
        hypernyms = self.hypernyms() + self.instance_hypernyms()
        if len(hypernyms) == 0:
            paths = [[self]]
        for hypernym in hypernyms:
            for ancestor_list in hypernym.hypernym_paths():
                ancestor_list.append(self)
                paths.append(ancestor_list)
        return paths

    def root_hypernyms(self) -> List["Synset"]:
        result, seen, todo = [], set(), [self]
        while todo:
            nxt = todo.pop()
            if nxt not in seen:
                seen.add(nxt)
                ups = nxt.hypernyms() + nxt.instance_hypernyms()
                if not ups:
                    result.append(nxt)
                else:
                    todo.extend(ups)
        return result

    def max_depth(self) -> int:
        ups = self.hypernyms() + self.instance_hypernyms()
        return 0 if not ups else 1 + max(h.max_depth() for h in ups)

    def min_depth(self) -> int:
        ups = self.hypernyms() + self.instance_hypernyms()
        return 0 if not ups else 1 + min(h.min_depth() for h in ups)

    def closure(self, rel, depth: int = -1):
        """Breadth-first transitive closure under `rel`, cycles discarded (nltk's acyclic_breadth_first)."""
        seen = {self}
        queue = deque([(self, 0)])
        while queue:
            node, d = queue.popleft()
            if depth >= 0 and d >= depth:
                continue
            for nxt in rel(node):
                if nxt in seen:
                    continue
                seen.add(nxt)
                yield nxt
                queue.append((nxt, d + 1))

    def _iter_hypernym_lists(self):
        todo, seen = [self], set()
        while todo:
            for s in todo:
                seen.add(s)
            yield todo
            todo = [h for s in todo for h in (s.hypernyms() + s.instance_hypernyms()) if h not in seen]

    def common_hypernyms(self, other: "Synset") -> List["Synset"]:
        a = {s for lst in self._iter_hypernym_lists() for s in lst}
        b = {s for lst in other._iter_hypernym_lists() for s in lst}
        return list(a.intersection(b))

    def _needs_root(self) -> bool:
        return not (self.pos() == NOUN and wordnet.get_version() != "1.6")

    def _shortest_hypernym_paths(self, simulate_root: bool) -> Dict[object, int]:
        if self._name == "*ROOT*":
            return {self: 0}
        queue, path = deque([(self, 0)]), {}
        while queue:
            s, depth = queue.popleft()
            if s in path:
                continue
            path[s] = depth
            depth += 1
            queue.extend((h, depth) for h in s.hypernyms())
            queue.extend((h, depth) for h in s.instance_hypernyms())
        if simulate_root:
            path["*ROOT*"] = max(path.values()) + 1
        return path

    def shortest_path_distance(self, other: "Synset", simulate_root: bool = False):
        if self == other:
            return 0
        d1 = self._shortest_hypernym_paths(simulate_root)
        d2 = other._shortest_hypernym_paths(simulate_root)
        inf = float("inf")
        best = inf
        for s, a in d1.items():
            b = d2.get(s, inf)
            best = min(best, a + b)
        return None if best == inf else best

    def path_similarity(self, other: "Synset", verbose: bool = False, simulate_root: bool = True):
        need = simulate_root and (self._needs_root() or other._needs_root())
        d = self.shortest_path_distance(other, simulate_root=need)
        if d is None or d < 0:
            return None
        return 1.0 / (d + 1)

    # -- identity -----------------------------------------------------------------------------------
    def __repr__(self):
        return "Synset('%s')" % self._name

    def __eq__(self, other):
        return isinstance(other, Synset) and other._name == self._name

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(("Synset", self._name))

    def __lt__(self, other):
        return self._name < getattr(other, "_name", "")


# ======================================================================================= the facades
class _WordNet:
    """Drop-in for `nltk.corpus.wordnet` over the frozen store, for the surface hdlab calls."""

    NOUN, VERB, ADJ, ADV, ADJ_SAT = NOUN, VERB, ADJ, ADV, ADJ_SAT

    def __init__(self):
        self._morph = None

    # -- the morphological arm is NOT re-implemented: it IS hdlab.morphology ------------------------
    def _morphy_forms(self, form: str, pos: str, check_exceptions: bool = True) -> List[str]:
        if self._morph is None:
            from hdlab.morphology import GlassBoxMorphology
            # mode="morphy": the byte-identical port of nltk's arbitration. The substrate's LIVE lemma default
            # is "dualroute" (a measured +0.0233 on human lemma gold) -- but routing these sites to it would
            # CHANGE the read, so the freeze keeps the dictionary tool's answer and the flip stays a separate,
            # board-measured decision (see SOLVED.md NEXT STEPS).
            self._morph = GlassBoxMorphology(mode="morphy")
        return self._morph._morphy(form, pos, check_exceptions)

    def morphy(self, form: str, pos: Optional[str] = None, check_exceptions: bool = True) -> Optional[str]:
        for p in ([pos] if pos else POS_LIST):
            got = self._morphy_forms(form, p, check_exceptions)
            if got:
                return got[0]
        return None

    # -- addressed lookups --------------------------------------------------------------------------
    def synset_from_pos_and_offset(self, pos: str, offset: int) -> Optional[Synset]:
        name = store().offset_name(_FILE_POS.get(pos, pos), int(offset))
        if name is None:
            warnings.warn("No WordNet synset found for pos=%s at offset=%s." % (pos, offset))
            return None
        return Synset(name)

    def synsets(self, lemma: str, pos=None, lang: str = "eng", check_exceptions: bool = True) -> List[Synset]:
        """EXACT port of nltk's ordering: for each pos in POS_LIST, for each morphy form, for each offset in
        the index's own order. An unknown form yields [] (nltk's defaultdict miss)."""
        if lang != "eng":
            raise NotImplementedError("the frozen lexicon carries English only (lang=%r)" % lang)
        lemma = lemma.lower()
        if pos is None:
            pos = POS_LIST
        out = []
        for p in pos:
            for form in self._morphy_forms(lemma, p, check_exceptions):
                for offset in store().lemma_offsets(form, p):
                    s = self.synset_from_pos_and_offset(p, offset)
                    if s is not None:
                        out.append(s)
        return out

    def synset(self, name: str) -> Synset:
        lemma, pos, idx_str = name.lower().rsplit(".", 2)
        idx = int(idx_str) - 1
        offsets = store().lemma_offsets(lemma, pos)
        if not offsets:
            raise WordNetError("No lemma %r with part of speech %r" % (lemma, pos))
        if idx >= len(offsets) or idx < 0:
            raise WordNetError("Lemma %r with part of speech %r only has %d sense(s)"
                               % (lemma, pos, len(offsets)))
        s = self.synset_from_pos_and_offset(pos, offsets[idx])
        if s is None:
            raise WordNetError("No synset for %r" % name)
        if pos == "s" and s.pos() == "a":
            raise WordNetError("Adjective satellite requested but only plain adjective found for lemma %r" % lemma)
        assert s.pos() == pos or (pos == "a" and s.pos() == "s"), (name, s.pos())
        return s

    def all_synsets(self, pos: Optional[str] = None, lang: str = "eng"):
        for n in store().all_synset_names(pos):
            yield Synset(n)

    def all_lemma_names(self, pos: Optional[str] = None, lang: str = "eng"):
        q = "SELECT DISTINCT form FROM lemma_index" if pos is None else \
            "SELECT DISTINCT form FROM lemma_index WHERE pos=?"
        for (f,) in store().many(q, () if pos is None else (pos,)):
            yield f

    def lemmas(self, lemma: str, pos: Optional[str] = None, lang: str = "eng") -> List[Lemma]:
        low = lemma.lower().replace(" ", "_")
        return [lm for s in self.synsets(low, pos) for lm in s.lemmas() if lm.name().lower() == low]

    def get_version(self) -> str:
        return store().meta().get("wordnet_version", "3.0")

    def synset_from_sense_key(self, key: str) -> Optional[Synset]:
        loc = store().lemma_of_key(key)
        return None if loc is None else Synset(loc[0])


class _VerbNet:
    """Drop-in for `nltk.corpus.verbnet` over the frozen store: classids / lemmas / themroles / frames."""

    class VClass:
        __slots__ = ("cid",)

        def __init__(self, cid):
            self.cid = cid

        def get(self, k, default=None):
            return self.cid if k == "ID" else default

        def __repr__(self):
            return "VerbnetClass(%r)" % self.cid

    def _cid(self, x) -> str:
        return x.cid if isinstance(x, _VerbNet.VClass) else str(x)

    def classids(self, lemma: Optional[str] = None, **kw) -> List[str]:
        if lemma:
            r = store().one("SELECT cids FROM vn_lemma WHERE lemma=?", (lemma,))
            return [] if r is None else json.loads(r[0])
        return [c for (c,) in store().many("SELECT cid FROM vn_class ORDER BY cid")]

    def vnclass(self, cid):
        c = self._cid(cid)
        if store().one("SELECT 1 FROM vn_class WHERE cid=?", (c,)) is None:
            raise ValueError("unknown VerbNet class %r" % c)
        return _VerbNet.VClass(c)

    def lemmas(self, vnclass=None) -> List[str]:
        if vnclass is None:
            return [l for (l,) in store().many("SELECT lemma FROM vn_lemma ORDER BY lemma")]
        r = store().one("SELECT lemmas FROM vn_class WHERE cid=?", (self._cid(vnclass),))
        return [] if r is None else json.loads(r[0])

    def themroles(self, vnclass) -> List[dict]:
        r = store().one("SELECT themroles FROM vn_class WHERE cid=?", (self._cid(vnclass),))
        return [] if r is None else json.loads(r[0])

    def frames(self, vnclass) -> List[dict]:
        r = store().one("SELECT frames FROM vn_class WHERE cid=?", (self._cid(vnclass),))
        return [] if r is None else json.loads(r[0])


class _Obj:
    """Attribute + mapping access over a frozen dict, so a FrameNet consumer's `fr.type.name` /
    `fr.FE.keys()` / `fr['name']` all behave as they do on nltk's AttrDict."""
    __slots__ = ("_d",)

    def __init__(self, d):
        self._d = d

    def __getattr__(self, k):
        d = object.__getattribute__(self, "_d")
        if k in d:
            v = d[k]
            return _Obj(v) if isinstance(v, dict) and k in ("type", "superFrame", "subFrame") else v
        raise AttributeError(k)

    def __getitem__(self, k):
        return object.__getattribute__(self, "_d")[k]

    def keys(self):
        return object.__getattribute__(self, "_d").keys()

    def items(self):
        return object.__getattribute__(self, "_d").items()

    def values(self):
        return object.__getattribute__(self, "_d").values()

    def get(self, k, default=None):
        return object.__getattribute__(self, "_d").get(k, default)

    def __contains__(self, k):
        return k in object.__getattribute__(self, "_d")

    def __iter__(self):
        return iter(object.__getattribute__(self, "_d"))

    def __repr__(self):
        d = object.__getattribute__(self, "_d")
        return "frame(%r)" % d.get("name", "?")


def _fn_frame_obj(row) -> _Obj:
    name, fid, definition, fes, lus, rels = row
    fe = {k: _Obj(v) for k, v in json.loads(fes).items()}
    return _Obj({"name": name, "ID": int(fid), "definition": definition, "FE": _Obj(fe),
                 "lexUnit": {k: _Obj({"name": k}) for k in json.loads(lus)},
                 "frameRelations": [_Obj({"type": {"name": r["type"]},
                                          "superFrameName": r["sup"], "subFrameName": r["sub"],
                                          "superFrame": {"name": r["sup"]}, "subFrame": {"name": r["sub"]}})
                                    for r in json.loads(rels)]})


class _FrameNet:
    """Drop-in for `nltk.corpus.framenet` over the frozen store: frames / frame / frame_by_name /
    frame_relations / lus_by_lemma."""

    _COLS = "SELECT name,fid,definition,fes,lus,rels FROM fn_frame"

    def frames(self, name: Optional[str] = None) -> List[_Obj]:
        if name is None:
            return [_fn_frame_obj(r) for r in store().many(self._COLS + " ORDER BY fid")]
        return [_fn_frame_obj(r) for r in store().many(self._COLS + " WHERE name LIKE ? ORDER BY fid",
                                                       ("%" + name + "%",))]

    def frame_by_name(self, name: str) -> _Obj:
        r = store().one(self._COLS + " WHERE name=?", (name,))
        if r is None:
            raise ValueError("unknown FrameNet frame %r" % name)
        return _fn_frame_obj(r)

    def frame_by_id(self, fid: int) -> _Obj:
        r = store().one(self._COLS + " WHERE fid=?", (int(fid),))
        if r is None:
            raise ValueError("unknown FrameNet frame id %r" % fid)
        return _fn_frame_obj(r)

    def frame(self, fn_fid_or_fname) -> _Obj:
        if isinstance(fn_fid_or_fname, str):
            return self.frame_by_name(fn_fid_or_fname)
        return self.frame_by_id(int(fn_fid_or_fname))

    def frame_relations(self, frame=None, frame2=None, type=None) -> List[_Obj]:
        rows = store().many("SELECT sup,sub,type FROM fn_rel ORDER BY idx")
        out = [_Obj({"type": {"name": t}, "superFrameName": sup, "subFrameName": sub,
                     "superFrame": {"name": sup}, "subFrame": {"name": sub}}) for sup, sub, t in rows]
        if type is not None:
            out = [r for r in out if r.type.name == type]
        return out

    def frames_by_lemma(self, lemma: str) -> List[_Obj]:
        r = store().one("SELECT frames FROM fn_lemma WHERE lemma=?", (lemma.lower(),))
        return [] if r is None else [self.frame_by_name(n) for n in json.loads(r[0])]


class _WordListCorpus:
    """Drop-in for `nltk.corpus.opinion_lexicon` / `stopwords` over the frozen store. An ABSENT list raises
    LookupError -- exactly what nltk raises -- so a call site's fallback fires identically instead of a
    silently different word list travelling into a read."""

    def __init__(self, kind: str):
        self.kind = kind

    def _get(self, name: str) -> list:
        w = store().wordlist(name)
        if w is None:
            raise LookupError("the frozen lexicon asset carries no word list %r (recorded absent at build "
                              "time; see asset_meta()['absent_wordlists'])" % name)
        return list(w)

    def positive(self) -> list:
        return self._get("opinion_positive")

    def negative(self) -> list:
        return self._get("opinion_negative")

    def words(self, which: str = "english") -> list:
        if self.kind == "stopwords":
            return self._get("stopwords_" + which)
        return self._get("opinion_positive") + self._get("opinion_negative")


wordnet = _WordNet()
wn = wordnet                     # the alias the 66 WordNet sites use
verbnet = _VerbNet()
framenet = _FrameNet()
opinion_lexicon = _WordListCorpus("opinion")
stopwords = _WordListCorpus("stopwords")


# ======================================================================================= frozen graph
def graph_edges(sources: Sequence[str]):
    """The FROZEN spreading-activation adjacency: (names, rows, cols) for the requested edge sources, over the
    same sorted-by-name synset order GroundedSemanticGraph.build() uses. Replaces a 2-million-call rebuild of
    a static structure with a load -- the same matrix, by construction (witness: CSR bytes)."""
    import numpy as np
    if not os.path.exists(GRAPH_PATH):
        raise LexiconAssetMissing("frozen lexicon graph not found: %s -- build it once with "
                                  "`python tools/build_lexicon_foundation_index.py --graph`" % GRAPH_PATH)
    z = np.load(GRAPH_PATH, allow_pickle=True)
    names = [str(x) for x in z["names"]]
    rows, cols = [], []
    for src in sources:
        rk, ck = "rows_" + src, "cols_" + src
        if rk not in z:
            raise KeyError("the frozen graph carries no source %r (have: %s)"
                           % (src, sorted(k[5:] for k in z.files if k.startswith("rows_"))))
        rows.extend(int(x) for x in z[rk])
        cols.extend(int(x) for x in z[ck])
    return names, rows, cols


# ======================================================================================= the stand-in gate
STANDIN_ALLOWED = os.environ.get("HDLAB_ALLOW_NLTK_STANDIN", "0") == "1"


def standin_nltk(module: str, attr: Optional[str] = None, reason: str = ""):
    """THE ONLY route from hdlab/ to nltk, and it is CLOSED by default.

    Two NOT-brain-foundational MODEL stand-ins used to sit on this path: `nltk.tag.PerceptronTagger`
    (temporal_model, retired from the default 2026-09-13 in favour of the category organ's Penn arm) and
    `nltk.stem.PorterStemmer` (morphology_leakage, a leakage-test helper). Neither is reachable on the default
    read; both stay REACHABLE ONLY as an explicitly-requested baseline, behind HDLAB_ALLOW_NLTK_STANDIN=1, so
    (a) the poisoned-import witness holds on the default read and (b) a stand-in can never be selected by a
    typo or a missing asset."""
    if not STANDIN_ALLOWED:
        raise RuntimeError(
            "nltk stand-in %s%s is OFF the live path (reason: %s). It is a measured NOT-brain-foundational "
            "baseline: set HDLAB_ALLOW_NLTK_STANDIN=1 to run it deliberately."
            % (module, "." + attr if attr else "", reason or "not brain-foundational"))
    import importlib                                   # _BUILD_ONLY: baseline-only, gated above
    m = importlib.import_module(module)                 # _BUILD_ONLY
    return getattr(m, attr) if attr else m


# ======================================================================================= self-test
def _self_test() -> bool:
    """Structural self-checks that need no nltk (the byte-parity witness against nltk is the cell)."""
    m = asset_meta()
    assert int(m["n_synsets"]) == 117659, m.get("n_synsets")
    dog = wordnet.synsets("dogs", "n")
    assert dog and dog[0].name() == "dog.n.01", dog[:2]
    assert dog[0].lexname() == "noun.animal", dog[0].lexname()
    assert wordnet.synset("dog.n.01") is dog[0]
    assert "canine.n.02" in [h.name() for h in dog[0].hypernyms()]
    paths = dog[0].hypernym_paths()
    assert paths and all(p[0].name() == "entity.n.01" for p in paths), [p[0].name() for p in paths]
    assert wordnet.morphy("dogs", "n") == "dog" and wordnet.morphy("went", "v") == "go"
    good = wordnet.synsets("good", "a")
    assert good and any(s.pos() in ("a", "s") for s in good)
    ants = [a.name() for lm in good[0].lemmas() for a in lm.antonyms()]
    assert "bad" in ants, ants
    assert verbnet.classids("give") == ["give-13.1-1"], verbnet.classids("give")
    assert verbnet.themroles("give-13.1")[0]["type"] in ("Agent", "Theme", "Recipient")
    fr = framenet.frame_by_name("Motion")
    assert "Theme" in fr.FE.keys() and "move.v" in fr.lexUnit.keys()
    assert framenet.frame("Motion").ID == fr.ID
    assert len(framenet.frame_relations()) > 2000
    assert len(opinion_lexicon.positive()) == 2006
    try:
        stopwords.words("english")
        raise AssertionError("stopwords must raise LookupError on this asset (recorded absent)")
    except LookupError:
        pass
    try:
        standin_nltk("nltk.tag", "PerceptronTagger", reason="self-test")
        raise AssertionError("the stand-in gate must be closed by default")
    except RuntimeError:
        pass
    print("lexicon_foundation self-test OK: %s synsets, wordnet %s, %s reads"
          % (m["n_synsets"], wordnet.get_version(), observe()))
    return True


if __name__ == "__main__":
    _self_test()
