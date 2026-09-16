"""pri 146 -- THE SPREADING-ACTIVATION MEMO, PER READER, AND THE PER-PASSAGE CATEGORY STATE ON THE READER.

61% of a document read is one graph walk (personalised PageRank over the frozen lexicon graph,
`hdlab/grounded_semantic_graph._ppr`), and two sibling functions in `hdlab/force_dynamics_valence`
ask it the IDENTICAL question about the same verb in the same sentence, so 26-40% of the walks
inside one document are exact repeats (pri 142: 46 of 116; 7 of 27).

THE BRAIN'S FORM.  Spreading activation in a semantic network (Collins & Loftus 1975) read at the
anterior-temporal hub (Patterson, Nestor & Rogers 2007) PERSISTS across the reading of a passage --
that is priming.  The brain does not re-spread from the same cues in the same passage.  A memo of a
pure function, held BY THE READER for the duration of one read, IS that persistence.  Nothing about
the walk changes: not the damping, not the iteration count, not the graph.  The gate is IDENTITY.

AND THE PRECONDITION.  To certify 'no answer changed' the reader must read one document the same way
twice, which needs the per-passage category state (`lexical_categories._INST` / `._REG_GEN` -- pri 142
probe A) to live on the READER rather than in the import system: ONE READER = ONE BRAIN.

WHAT THIS CELL IS.  The proposed change is written ONCE, as source strings (SRC_* below).  Those
strings are BOTH exec'd into the live modules (the runtime shim that lets both arms run in one
process) AND used as the replacement half of the anchors that generate
`notes/problems/<slug>/ppr_memo_patch.diff` -- so the arm measured here IS the shipped diff.  On a
tree where the patch has LANDED the shim is skipped and the same arms are selected by the memo's
capacity (0 = inert), so this cell and its witness run green before and after landing.

USAGE
  .venv/Scripts/python.exe experiments/exp_ppr_memo_v1.py --self-test
  .venv/Scripts/python.exe experiments/exp_ppr_memo_v1.py --stability [--docs 12]
  .venv/Scripts/python.exe experiments/exp_ppr_memo_v1.py --identity  [--docs 12]
  .venv/Scripts/python.exe experiments/exp_ppr_memo_v1.py --twin      [--docs 2]
  .venv/Scripts/python.exe experiments/exp_ppr_memo_v1.py --timing    [--docs 6] [--pairs 3]
  .venv/Scripts/python.exe experiments/exp_ppr_memo_v1.py --make-diff
"""
from __future__ import annotations

import argparse
import dataclasses
import difflib
import json
import os
import sys
import tempfile
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from experiments._seed_checkpoint import get_output_dir          # noqa: E402  (Q115: canonical out dir)

ANCHOR = "exp_ppr_memo_v1"
OUT_DIR = str(get_output_dir(ANCHOR))
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

GSG_PATH = os.path.join(REPO, "hdlab", "grounded_semantic_graph.py")
LC_PATH = os.path.join(REPO, "hdlab", "lexical_categories.py")
SR_PATH = os.path.join(REPO, "hdlab", "situation_reader.py")


# =====================================================================================================================
# 1. THE PROPOSED CHANGE, WRITTEN ONCE  (the shim source IS the patch source)
# =====================================================================================================================

SRC_GSG_MEMO = '''PPR_MEMO_MAX = 128          # ENTRIES.  One entry is a float32 activation vector over EVERY synset node --
                            # MEASURED on this graph at 470,636 bytes (117,659 nodes), so 128 entries is 57.5 MB,
                            # freed when the read ends; the memo measures its own footprint (`stats()`) rather
                            # than assuming it.  It is a CAPACITY, not a tuned parameter: eviction is least-
                            # recently-used (the decay) and an evicted cue set is simply re-spread, so no answer
                            # depends on its value.  MEASURED over 12 GUM TEST documents (12 genres, 817
                            # sentences): peak 20-128 entries, 7 evictions in all (GUM_court_property, the one
                            # document that reached the cap), and the read is byte-identical at cap 0, 1 and 128.
SEED_MEMO = True            # remember the CUE SET too, not only the activation it settles to (see _sense_ppr):
                            # building the seed is one lexicon lookup per context word, and the same two callers
                            # ask for the same sentence's cue set twice.  Set False to run the walk memo alone.
                            # MEASURED marginal over the walk memo alone: +2.4 points of read time (3 documents,
                            # positive on 2, NEGATIVE on 1), i.e. NOT a separated saving -- and byte-identical
                            # either way (3/3).  It ships ON because it is the same repeat, the same brain claim
                            # and the same identity certificate.  THIS SWITCH IS A TIMING LEVER, NOT A
                            # CAPABILITY FLAG: it cannot change an answer, so the project's no-default-off rule
                            # (which exists for capabilities that are measurably dormant) does not apply to it.
_ACTIVE_MEMO = None         # the activation memo of the reading in progress (see SituationReader.read); None
                            # outside a read -- module level holds the BINDING, never the activation.


class ActivationMemo:
    """THE PERSISTENCE OF SPREADING ACTIVATION WITHIN ONE READING (pri 146).

    Spreading activation from a cue set is a pure function of the cue set and the graph, and the brain does not
    re-spread from the same cues in the same passage -- the activation is still there (Collins & Loftus 1975;
    the ATL hub read, Patterson, Nestor & Rogers 2007).  This is that persistence, and it is the READER's: one
    reader = one brain, so it is created per read, dies with the read, and is capacity-bounded with the least
    recently used cue set dropped first (the decay).

    The graph is pinned by IDENTITY (`_bind`): the activation depends on the cue set AND the network, so a memo
    can never serve a vector spread over a different graph.
    """

    def __init__(self, cap=None):
        self.d = {}
        self.cap = PPR_MEMO_MAX if cap is None else int(cap)
        self.hits = 0
        self.misses = 0
        self.evictions = 0
        self.peak = 0
        self.vec_bytes = 0          # measured, not assumed: one activation vector's size on this graph
        self.seeds = {}             # the CUE SET for a context list (see _sense_ppr) -- a list of node indices
        self.seed_hits = 0
        self.seed_misses = 0
        self._graph = None

    def _bind(self, Tt):
        if self._graph is None:
            self._graph = Tt
        elif self._graph is not Tt:
            self.d.clear()
            self.seeds.clear()
            self._graph = Tt

    def get(self, key, Tt):
        self._bind(Tt)
        v = self.d.get(key)
        if v is None:
            self.misses += 1
            return None
        self.d[key] = self.d.pop(key)          # least-recently-used first
        self.hits += 1
        return v

    def put(self, key, r, Tt):
        self._bind(Tt)
        if self.cap <= 0:
            return
        if not self.vec_bytes:
            self.vec_bytes = int(getattr(r, "nbytes", 0))
        self.d[key] = r
        while len(self.d) > self.cap:
            self.d.pop(next(iter(self.d)))
            self.evictions += 1
        if len(self.d) > self.peak:
            self.peak = len(self.d)

    def stats(self):
        n = self.hits + self.misses
        return {"hits": self.hits, "misses": self.misses, "calls": n, "held": len(self.d),
                "peak_entries": self.peak, "evictions": self.evictions, "vector_bytes": self.vec_bytes,
                "peak_bytes": self.peak * self.vec_bytes, "cap_bytes": self.cap * self.vec_bytes,
                "hit_share": round(self.hits / n, 4) if n else 0.0, "cap": self.cap,
                "seed_hits": self.seed_hits, "seed_misses": self.seed_misses, "seeds_held": len(self.seeds)}

    def seed(self, ckey):
        """The remembered CUE SET for this context list, or None.  Capacity-bounded like the activation (a cue
        set is a list of node indices -- small -- so it is held four to a vector's worth of headroom)."""
        v = self.seeds.get(ckey)
        if v is None:
            return None
        self.seeds[ckey] = self.seeds.pop(ckey)
        self.seed_hits += 1
        return v

    def put_seed(self, ckey, seed_idx):
        self.seed_misses += 1
        if self.cap <= 0:
            return
        self.seeds[ckey] = seed_idx
        while len(self.seeds) > 4 * self.cap:
            self.seeds.pop(next(iter(self.seeds)))


class _Spreading:
    """`with spreading(memo):` -- lend THIS reader's activation memo to the walk for one read."""

    def __init__(self, memo):
        self.memo = memo
        self.saved = None

    def __enter__(self):
        global _ACTIVE_MEMO
        self.saved = _ACTIVE_MEMO
        _ACTIVE_MEMO = self.memo
        return self.memo

    def __exit__(self, *exc):
        global _ACTIVE_MEMO
        _ACTIVE_MEMO = self.saved
        return False


def spreading(memo):
    """Bind a reader's ActivationMemo for the duration of one read (SituationReader.read)."""
    return _Spreading(memo)
'''

SRC_GSG_PPR = '''def _ppr(seed_idx: List[int], Tt: sp.csr_matrix, n: int, d: float = DAMPING, iters: int = PPR_ITERS):
    """stationary spreading-activation vector: r = (1-d)*p + d*T^T r, p uniform over seed synsets.

    ASKED TWICE PER EVENT (pri 146).  `sense_posterior_in_context` and `context_sense_sign` build byte-identical
    context lists for one (verb, sentence) and each spread independently: 26-40% of the walks inside one
    document are exact repeats, and this walk is 61% of a read.  When the reader has lent its ActivationMemo
    (see `spreading`), a repeat is READ BACK instead of re-spread.  The key is the EXACT seed tuple (never the
    context words), so a caller that legitimately seeds differently never collides, and nothing about the walk
    changes: not d, not iters, not the graph.  With no memo bound this function is exactly what it was.
    """
    if not seed_idx:
        return None
    memo = _ACTIVE_MEMO
    key = None
    if memo is not None:
        key = (tuple(seed_idx), n, d, iters)
        hit = memo.get(key, Tt)
        if hit is not None:
            return hit
    p = np.zeros(n, np.float32)
    p[seed_idx] = 1.0 / len(seed_idx)
    r = p.copy()
    for _ in range(iters):
        r = (1.0 - d) * p + d * (Tt @ r)
    if memo is not None:
        memo.put(key, r, Tt)
    return r
'''

SRC_GSG_SENSE_PPR = '''def _seed_set(wn, context_words, syn2idx, tgt_names):
    """THE CUE SET the activation spreads from: every synset of every context word, minus the target lemma's own
    senses.  Split out of `_sense_ppr` unchanged (pri 146) so that building it can be remembered for a passage the
    way the activation it seeds is -- see `_sense_ppr`."""
    seed = []
    tgt_set = set(tgt_names)
    for w in context_words:
        for gs in wn.synsets(w):
            j = syn2idx.get(gs.name())
            if j is not None and gs.name() not in tgt_set:
                seed.append(j)
    return sorted(set(seed))


def _sense_ppr(wn, lemma, pos, context_words, syn2idx, T, n, tgt, tgt_names):
    """THE CUE SET IS ASKED TWICE TOO (pri 146, the second repeat on this path).  Building the seed is one
    lexicon lookup per context word (`wn.synsets` -> a sqlite read per synset), and the two sibling callers in
    force_dynamics_valence hand this function the SAME context list for one (verb, sentence).  Lexical access
    happens once per word per sentence in the brain -- not once per question asked about that sentence -- so the
    settled cue set is remembered on the SAME per-read memo as the activation it seeds.  The key is the exact
    context list AND the SET of target names -- the target's own synsets are excluded from the seed, so a
    different target set is a different cue set, but the ORDER of the targets cannot change it and must not
    split the key (the two callers reach here with the same synsets in different orders).  Set
    SEED_MEMO = False to run the activation memo alone."""
    memo = _ACTIVE_MEMO
    ckey = (tuple(context_words), tuple(sorted(set(tgt_names)))) \
        if (memo is not None and SEED_MEMO and memo.cap > 0) else None
    seed_idx = memo.seed(ckey) if ckey is not None else None
    if seed_idx is None:
        seed_idx = _seed_set(wn, context_words, syn2idx, tgt_names)
        if ckey is not None:
            memo.put_seed(ckey, seed_idx)
    r = _ppr(seed_idx, T, n)
    if r is None:
        return None
    return np.array([float(r[syn2idx[s.name()]]) if s.name() in syn2idx else 0.0 for s in tgt])
'''

SRC_LC_PASSAGE = '''class PassageFile:
    """ONE READER = ONE BRAIN (pri 146).  Everything about the passage currently being comprehended -- Heim's
    (1982) file cards and their ACT-R clock, the passage-register accumulator, and the memo of the tags this
    passage has settled on -- is ONE object, created at the passage boundary and OWNED BY THE READER that opened
    it (`SituationReader.read` takes it back through `detach_passage` when the read ends).  The organ object
    itself stays a READ-ONLY asset shared by every holder (the frontend tagger binds it once at construction),
    so the file is LENT to the organ for the duration of one read and taken back afterwards: after a read the
    import system holds no passage state at all, and the next reader cannot see this one's cards.

    Before pri 146 the same state lived at module level behind a generation counter (`_REG_GEN`) -- pri 142's
    probe A measured `_INST` and `_REG_GEN` as the only module-level names that moved when one document was read
    twice."""

    __slots__ = ("reg", "doc_shape", "gen", "pos_memo")

    def __init__(self, gen: int = 1, open_register: bool = True):
        self.reg = DiscourseRegister() if open_register else None
        self.doc_shape = {}
        self.gen = int(gen)
        self.pos_memo = {}          # the affect path's per-passage POS memo (situation_reader._affect_pos)


_ACTIVE_PASSAGE = None      # the file open in the reading in progress; None outside a read


def current_passage():
    """The passage file of the reading currently in progress, or None outside a read.  A memo of anything that
    depends on the register (the reader's affect-path POS memo) belongs ON THIS OBJECT: the tags for a string are
    constant within a passage and not across passages, and this object dies with the read."""
    return _ACTIVE_PASSAGE


def open_memo_passage():
    """A passage file with NO file cards -- for a reader whose tagger is not this organ (HDLAB_TAG_SOURCE=
    perceptron): the register stays closed exactly as it was, and the passage still owns its POS memo."""
    global _ACTIVE_PASSAGE
    _ACTIVE_PASSAGE = PassageFile(1, open_register=False)
    return _ACTIVE_PASSAGE


def detach_passage(organ=None):
    """END OF READ: hand the open passage file back to the reader that opened it and leave the organ with NO
    passage.  This is the half that makes a read order-independent -- without it the organ still holds document
    1's file cards while anything asks it about document 2, until the next `new_document()`."""
    global _ACTIVE_PASSAGE
    m = organ if organ is not None else get()
    p = _ACTIVE_PASSAGE
    _ACTIVE_PASSAGE = None
    m._reg = None
    m._doc_shape = {}
    m._reg_gen = 0
    return p


def register_generation() -> int:
    """The identity of the passage currently open on the organ (bumped by `new_document`); 0 = none open.
    pri 146: this is the passage counter of the ORGAN INSTANCE, not a process-global one, so it is NOT a valid
    key for a process-global memo -- the one memo that used it (the reader's affect-path POS memo) now lives on
    the PassageFile, which the reader owns."""
    return int(getattr(get(), "_reg_gen", 0) or 0)
'''

SRC_LC_NEWDOC = '''    def new_document(self) -> None:
        """Passage boundary: open a fresh set of file cards and clear the passage register (Heim: a new file).
        pri 146: the cards, the clock, the passage register and the passage's POS memo are ONE `PassageFile`,
        OWNED BY THE READER that opened it -- `SituationReader.read` takes it back when the read ends
        (`detach_passage`), so no passage state survives a read at module level and no process-global generation
        counter is needed to keep one passage's belief out of another passage's memo."""
        global _ACTIVE_PASSAGE
        self._reg_gen += 1
        p = PassageFile(self._reg_gen)
        self._reg = p.reg
        self._doc_shape = p.doc_shape
        _ACTIVE_PASSAGE = p
'''

SRC_SR_AFFECT_POS = '''def _affect_pos(sentence_text: str):
    """The affect path's tags for this sentence, memoised ON THE PASSAGE FILE THE READER OWNS (pri 146).

    EFFICIENCY (2026-09-06): _assign_affect runs once PER EVENT -- many events share a sentence, so the identical
    string was re-tagged repeatedly (the affect path was ~half the read's POS-tag calls).  KEYED ON THE PASSAGE
    (2026-09-14, pri-112): the category organ reads the passage's Heim file cards, so the tags for one string
    depend on WHICH PASSAGE is open, and a process-global memo keyed on the string alone served one document's
    tags into another (236 vs 235 events on the same document read twice; data/hook_state/diag_w3a9.log).
    ON THE READER (2026-09-16, pri 146): the memo is the open PassageFile's, so the unit it is keyed on IS the
    object that dies with the read -- no module-level lru_cache and no generation counter.  Outside a read (no
    passage open) the tags are recomputed: correct, just not memoised.  Returns a tuple; callers copy to a fresh
    list so a downstream mutation cannot corrupt the cache."""
    from hdlab import lexical_categories as _LC
    try:
        p = _LC.current_passage()
    except Exception:
        p = None
    memo = p.pos_memo if p is not None else None
    if memo is None:
        return tuple(_load_frontend()[0].tag(sentence_text.split(" ")))
    r = memo.get(sentence_text)
    if r is None:
        r = memo[sentence_text] = tuple(_load_frontend()[0].tag(sentence_text.split(" ")))
    return r
'''

SRC_SR_READ = '''    def read(self, conll_path: str) -> SituationModel:
        """ONE READER = ONE BRAIN (pri 146).  The two things a read owns are bound here and released here:
        (1) the reader's ACTIVATION MEMO -- the spreading activation that persists within this reading (61% of a
        read is that walk, and 26-40% of its runs inside one document were exact repeats); (2) the PASSAGE FILE --
        Heim's cards, their clock, the passage register and the passage's POS memo -- taken back off the shared
        category organ when the read ends, so no passage state survives a read at module level."""
        from hdlab import grounded_semantic_graph as _GSG
        from hdlab import lexical_categories as _LC
        self._ppr_memo = _GSG.ActivationMemo()
        if _TAG_SOURCE != "counts":
            _LC.open_memo_passage()        # the organ is not this reader's tagger: no cards, just the POS memo
        try:
            with _GSG.spreading(self._ppr_memo):
                return self._read_document(conll_path)
        finally:
            self._lc_passage = _LC.detach_passage()

    def _read_document(self, conll_path: str) -> SituationModel:
        self._read_parse_cache = {}   # per-read tag/parse memo (bound memory; safe if the reader is reused)
'''


# =====================================================================================================================
# 2. THE PATCH ANCHORS (old -> new).  `--make-diff` renders these as a unified diff in each file's own bytes.
# =====================================================================================================================

OLD_GSG_PPR = '''def _ppr(seed_idx: List[int], Tt: sp.csr_matrix, n: int, d: float = DAMPING, iters: int = PPR_ITERS):
    """stationary spreading-activation vector: r = (1-d)*p + d*T^T r, p uniform over seed synsets."""
    if not seed_idx:
        return None
    p = np.zeros(n, np.float32)
    p[seed_idx] = 1.0 / len(seed_idx)
    r = p.copy()
    for _ in range(iters):
        r = (1.0 - d) * p + d * (Tt @ r)
    return r
'''

OLD_GSG_SENSE_PPR = '''def _sense_ppr(wn, lemma, pos, context_words, syn2idx, T, n, tgt, tgt_names):
    seed = []
    tgt_set = set(tgt_names)
    for w in context_words:
        for gs in wn.synsets(w):
            j = syn2idx.get(gs.name())
            if j is not None and gs.name() not in tgt_set:
                seed.append(j)
    r = _ppr(sorted(set(seed)), T, n)
    if r is None:
        return None
    return np.array([float(r[syn2idx[s.name()]]) if s.name() in syn2idx else 0.0 for s in tgt])
'''

OLD_LC_PASSAGE = '''_REG_GEN = 0


def register_generation() -> int:
    """The identity of the passage currently open (bumped by `new_document`); 0 = no passage has ever been opened.
    A memo of anything that depends on the register (the reader's affect-path POS memo) must be keyed on this: the
    tags for a string are constant WITHIN a passage and not across passages."""
    return _REG_GEN
'''

OLD_LC_NEWDOC = '''    def new_document(self) -> None:
        """Passage boundary: open a fresh set of file cards and clear the passage register (Heim: a new file).
        Bumps the PASSAGE GENERATION so a memo of register-dependent output cannot serve one passage's belief into
        another (the reader's affect-path POS memo was exactly that -- see situation_reader._affect_pos)."""
        global _REG_GEN
        _REG_GEN += 1
        self._reg = DiscourseRegister()
        self._reg_gen = _REG_GEN
        self._doc_shape = {}
'''

OLD_SR_READ = '''    def read(self, conll_path: str) -> SituationModel:
        self._read_parse_cache = {}   # per-read tag/parse memo (bound memory; safe if the reader is reused)
'''

# The module-level lru_cache this patch removes was `lru_cache`'s only user in the file (checked: 2 hits, the
# import and the decorator), so the import goes with it -- a dead import left behind is how the next reader of
# this file concludes the memo is still there.
OLD_SR_IMPORT = '''from dataclasses import dataclass, field
from functools import lru_cache
from typing import Dict, List, Optional, Tuple
'''

SRC_SR_IMPORT = '''from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
'''

PATCH = [
    ("hdlab/grounded_semantic_graph.py", GSG_PATH, [(OLD_GSG_PPR, SRC_GSG_MEMO + "\n\n" + SRC_GSG_PPR),
                                                    (OLD_GSG_SENSE_PPR, SRC_GSG_SENSE_PPR)]),
    ("hdlab/lexical_categories.py", LC_PATH, [(OLD_LC_PASSAGE, SRC_LC_PASSAGE), (OLD_LC_NEWDOC, SRC_LC_NEWDOC)]),
    ("hdlab/situation_reader.py", SR_PATH, [(OLD_SR_IMPORT, SRC_SR_IMPORT),
                                            ("@OLD_SR_AFFECT@", SRC_SR_AFFECT_POS), (OLD_SR_READ, SRC_SR_READ)]),
]


def _read_lines(path):
    """The file as a list of lines, EACH KEEPING ITS OWN ENDING.  This tree mixes CRLF files with LF islands
    (hdlab/situation_reader.py has 8 LF-only lines at 702-709), so the patch is built at LINE granularity and
    every untouched line keeps the bytes it had -- `git diff -w --stat` must equal `git diff --stat` for it."""
    with open(path, "rb") as fh:
        raw = fh.read()
    lines = raw.decode("utf-8").splitlines(keepends=True)
    assert "".join(lines).encode("utf-8") == raw, "round trip is not byte-identical: %s" % path
    return raw, lines


def _norm_text(lines):
    return "".join(l.replace("\r\n", "\n") for l in lines)


def _apply(lines, old, new, path):
    """Replace the block `old` (given with '\\n' newlines, whole lines) by `new`, giving every inserted line the
    ending of the first line it replaces."""
    each = [l.replace("\r\n", "\n") for l in lines]
    text = "".join(each)
    k = text.count(old)
    if k != 1:
        raise SystemExit("PATCH ANCHOR matched %d times in %s (expected 1)\n---\n%s\n---" % (k, path, old[:400]))
    off = text.index(old)
    starts, acc = [], 0
    for l in each:
        starts.append(acc)
        acc += len(l)
    if off not in starts:
        raise SystemExit("PATCH ANCHOR does not start at a line boundary in %s" % path)
    i = starts.index(off)
    n_old = old.count("\n")
    eol = "\r\n" if lines[i].endswith("\r\n") else "\n"
    new_lines = [x + eol for x in new.split("\n")[:-1]]
    return lines[:i] + new_lines + lines[i + n_old:]


def _old_sr_affect(lines):
    """The affect-path POS memo as it stands on disk (the lru_cache + its wrapper), read from the LIVE file so the
    anchor cannot drift out of date silently: from `@lru_cache` down to the end of `_affect_pos`."""
    src = _norm_text(lines)
    a = src.index("@lru_cache(maxsize=8192)\ndef _affect_pos_cached(")
    b = src.index("\n\n\ndef _assign_affect(", a)
    return src[a:b + 1]


def patched_lines(path, edits):
    lines = _read_lines(path)[1]
    for old, new in edits:
        if old == "@OLD_SR_AFFECT@":
            old = _old_sr_affect(lines)
        lines = _apply(lines, old, new, path)
    return lines


def patched_source(path, edits):
    return _norm_text(patched_lines(path, edits))


def make_diff() -> str:
    """The unified diff, in each file's own bytes."""
    out = []
    for rel, path, edits in PATCH:
        a = _read_lines(path)[1]
        b = patched_lines(path, edits)
        d = list(difflib.unified_diff(a, b, fromfile="a/" + rel, tofile="b/" + rel, n=6))
        if not d:
            continue
        out.append("diff --git a/%s b/%s\n" % (rel, rel))
        out.extend(d)
    return "".join(out)


# =====================================================================================================================
# 3. THE RUNTIME SHIM  (the same source, exec'd into the live modules; skipped when the patch has LANDED)
# =====================================================================================================================

def landed():
    """Detect the landed state from the LIVE MODULES, so this cell and its witness are green on either tree."""
    import hdlab.grounded_semantic_graph as GSG
    import hdlab.lexical_categories as LC
    import hdlab.situation_reader as SR
    return {"memo": hasattr(GSG, "ActivationMemo") and hasattr(GSG, "spreading"),
            "passage": hasattr(LC, "PassageFile") and hasattr(LC, "detach_passage") and not hasattr(LC, "_REG_GEN"),
            "read_wrapped": hasattr(SR.SituationReader, "_read_document")}


_SAVED = {}


def install():
    """Exec the proposed source into the live modules.  Returns a token for `restore()`.  A no-op for any part
    that is already landed."""
    import hdlab.grounded_semantic_graph as GSG
    import hdlab.lexical_categories as LC
    import hdlab.situation_reader as SR
    st = landed()
    if not st["memo"] or "gsg_ppr" not in _SAVED:
        # `landed()` alone is NOT the test: `restore()` puts the stock functions back, and a shim that had been
        # installed once would otherwise be skipped here because its added NAMES are still in the module -- which
        # would silently run the "memo on" arm with no memo at all.  The saved token is the authority.
        _SAVED["gsg_ppr"] = GSG._ppr
        _SAVED["gsg_sense_ppr"] = GSG._sense_ppr
        _pre = set(GSG.__dict__)
        exec(compile(SRC_GSG_MEMO + "\n\n" + SRC_GSG_PPR + "\n\n" + SRC_GSG_SENSE_PPR, GSG_PATH, "exec"),
             GSG.__dict__)
        _SAVED["gsg_added"] = set(GSG.__dict__) - _pre
    if not st["passage"] or "lc_register_generation" not in _SAVED:
        _SAVED["lc_reggen"] = getattr(LC, "_REG_GEN", 0)
        _SAVED["lc_register_generation"] = LC.register_generation
        _SAVED["lc_new_document"] = LC.LexicalCategories.new_document
        _pre = set(LC.__dict__)
        exec(compile(SRC_LC_PASSAGE, LC_PATH, "exec"), LC.__dict__)
        _SAVED["lc_added"] = set(LC.__dict__) - _pre - {"_REG_GEN"}
        ns = {}
        exec(compile("class _P:\n" + SRC_LC_NEWDOC, LC_PATH, "exec"), LC.__dict__, ns)
        LC.LexicalCategories.new_document = ns["_P"].new_document
        if hasattr(LC, "_REG_GEN"):
            del LC._REG_GEN
    if not st["read_wrapped"] or "sr_read" not in _SAVED:
        _SAVED["sr_read"] = SR.SituationReader.read
        _SAVED["sr_affect_pos"] = SR._affect_pos
        _SAVED["sr_affect_pos_cached"] = SR._affect_pos_cached
        exec(compile(SRC_SR_AFFECT_POS, SR_PATH, "exec"), SR.__dict__)
        del SR._affect_pos_cached          # the patch REMOVES the module-level lru_cache; so does the shim
        ns = {}
        exec(compile("class _R:\n" + SRC_SR_READ, SR_PATH, "exec"), SR.__dict__, ns)
        SR.SituationReader._read_document = SR.SituationReader.read
        SR.SituationReader.read = ns["_R"].read
    return st


def restore():
    """Put the live modules back exactly as they were (so an arm measured AFTER a restore is the stock tree)."""
    import hdlab.grounded_semantic_graph as GSG
    import hdlab.lexical_categories as LC
    import hdlab.situation_reader as SR
    if "gsg_ppr" in _SAVED:
        GSG._ppr = _SAVED.pop("gsg_ppr")
        GSG._sense_ppr = _SAVED.pop("gsg_sense_ppr")
        for nm in _SAVED.pop("gsg_added", ()):     # the added NAMES go too, or `landed()` lies afterwards
            GSG.__dict__.pop(nm, None)
    if "lc_register_generation" in _SAVED:
        LC.detach_passage()
        LC._REG_GEN = _SAVED.pop("lc_reggen")
        LC.register_generation = _SAVED.pop("lc_register_generation")
        LC.LexicalCategories.new_document = _SAVED.pop("lc_new_document")
        for nm in _SAVED.pop("lc_added", ()):
            LC.__dict__.pop(nm, None)
    if "sr_read" in _SAVED:
        SR.SituationReader.read = _SAVED.pop("sr_read")
        SR._affect_pos = _SAVED.pop("sr_affect_pos")
        SR._affect_pos_cached = _SAVED.pop("sr_affect_pos_cached")
        del SR.SituationReader._read_document


# =====================================================================================================================
# 4. THE READ AND ITS SIGNATURE
# =====================================================================================================================

SIG_FIELDS = ("passage_id", "n_sentences", "entities", "events", "suppressed_predicates",
              "coref_resolutions", "timeline_frames", "timeline_order", "causal_links",
              "entity_states", "pronoun_abstentions")


def _canon(v):
    """Every dataclass field, recursively, in a stable order.  Opaque objects (registers, callables) render as
    their type name -- the gate is on the situation model's DATA, which is what every consumer reads."""
    if dataclasses.is_dataclass(v) and not isinstance(v, type):
        return {f.name: _canon(getattr(v, f.name)) for f in dataclasses.fields(v)}
    if isinstance(v, dict):
        return {str(k): _canon(v[k]) for k in sorted(v, key=repr)}
    if isinstance(v, (list, tuple)):
        return [_canon(x) for x in v]
    if isinstance(v, (str, int, float, bool)) or v is None:
        return v
    return "<%s>" % type(v).__name__


def sig(sm):
    """The read's full answer, field by field, plus the (predicate, agent, patient) tuple set the bar names."""
    d = {f: _canon(getattr(sm, f, None)) for f in SIG_FIELDS}
    d["_pap"] = sorted([e.predicate, str(e.agent), str(e.patient)] for e in sm.events)
    return d


def sig_json(s):
    return json.dumps(s, sort_keys=True, separators=(",", ":"))


def _docs(n_docs):
    from experiments.exp_structure_map_cost_v1 import _gum_test_docs
    return _gum_test_docs(n_docs)


def _conll(doc, tmp):
    from experiments.exp_structure_map_cost_v1 import _write_two_conll
    return _write_two_conll(doc, tmp)[0]


def _reader(gaz):
    from hdlab.situation_reader import SituationReader
    return SituationReader(gaz=gaz)


def _read(path, gaz, cap=None, reader=None, memo_factory=None, seeds=None):
    """One read.  `cap` selects the arm on a tree where the mechanism is present: 0 = the memo is inert (every
    walk recomputed AND every cue set rebuilt), None = the shipped capacity.  `seeds` False runs the activation
    memo alone (the second lever off).  Returns (seconds, situation model, memo stats)."""
    import hdlab.grounded_semantic_graph as GSG
    rdr = reader if reader is not None else _reader(gaz)
    prev, prev_seed = GSG.PPR_MEMO_MAX, GSG.SEED_MEMO
    if cap is not None:
        GSG.PPR_MEMO_MAX = cap
    if seeds is not None:
        GSG.SEED_MEMO = bool(seeds)
    if memo_factory is not None:
        GSG.ActivationMemo = memo_factory
    try:
        t0 = time.perf_counter()
        sm = rdr.read(path)
        dt = time.perf_counter() - t0
    finally:
        GSG.PPR_MEMO_MAX = prev
        GSG.SEED_MEMO = prev_seed
    m = getattr(rdr, "_ppr_memo", None)
    return dt, sm, (m.stats() if m is not None else None)


def _stock_read(path, gaz):
    """A read on the STOCK tree (shim removed) -- available only before the patch has landed."""
    restore()
    try:
        rdr = _reader(gaz)
        t0 = time.perf_counter()
        sm = rdr.read(path)
        return time.perf_counter() - t0, sm
    finally:
        install()


# =====================================================================================================================
# 5. ARMS
# =====================================================================================================================

def stability(n_docs=12, mode="annotated"):
    """BAR 1 -- READ-TO-READ STABILITY.  With the memo INERT, is one document read to a byte-identical situation
    model twice in one process with ONE reader, and with TWO FRESH readers?  A document that is not is excluded
    from the identity gate with its reason."""
    st = install()
    test, gaz = _docs(n_docs)
    tmp = tempfile.mkdtemp(prefix="p146_stab_")
    rows = []
    for d in test:
        path = _conll(d, tmp)
        _, sm1, _ = _read(path, gaz, cap=0)                     # fresh reader A
        _, sm2, _ = _read(path, gaz, cap=0)                     # fresh reader B
        r = _reader(gaz)
        _, sm3, _ = _read(path, gaz, cap=0, reader=r)           # one reader, read 1
        _, sm4, _ = _read(path, gaz, cap=0, reader=r)           # the SAME reader, read 2
        a, b, c, e = sig_json(sig(sm1)), sig_json(sig(sm2)), sig_json(sig(sm3)), sig_json(sig(sm4))
        row = {"docid": d.docid, "n_sentences": sm1.n_sentences, "n_events": len(sm1.events),
               "two_fresh_readers_identical": a == b, "one_reader_twice_identical": c == e,
               "fresh_vs_reused_reader_identical": a == c}
        row["stable"] = bool(row["two_fresh_readers_identical"] and row["one_reader_twice_identical"]
                             and row["fresh_vs_reused_reader_identical"])
        rows.append(row)
        print("  %-30s sents=%-4d events=%-4d  fresh/fresh=%s  one-reader-twice=%s  fresh/reused=%s"
              % (d.docid, row["n_sentences"], row["n_events"], row["two_fresh_readers_identical"],
                 row["one_reader_twice_identical"], row["fresh_vs_reused_reader_identical"]))
    res = {"arm": "stability", "landed_before_install": st, "n_documents": len(rows),
           "n_stable": sum(1 for r in rows if r["stable"]), "per_document": rows,
           "plain": ("with the spreading-activation memo switched off, each document is read four times -- two "
                     "fresh readers and one reader twice -- and the whole situation model is compared field by "
                     "field; a document that does not read the same way twice cannot certify the memo")}
    _write("stability.json", res)
    print("\nSTABLE: %d of %d documents" % (res["n_stable"], res["n_documents"]))
    return res


def _of_digest(rdr):
    """A numeric digest of THIS reader's plastic object-file validity table (pri 136's per-reader deep copy), so
    'the reader learned something from the document it just read' is a measured fact and not an inference."""
    V = getattr(rdr, "_of_validities", None)
    if V is None:
        return None
    tot, n = 0.0, 0
    for tab in ("counts", "crit"):
        t = getattr(V, tab, None)
        if isinstance(t, dict):
            for sub in t.values():
                if isinstance(sub, dict):
                    for x in sub.values():
                        tot += sum(x) if isinstance(x, (list, tuple)) else float(x or 0)
                        n += 1
                elif isinstance(sub, (list, tuple)):
                    tot += sum(sub)
                    n += 1
    return {"entries": n, "sum": round(tot, 6)}


def residual(n_docs=3, mode="annotated"):
    """BAR 1's RESIDUAL, PINNED TO A LINE.  Two fresh readers agree on every document; ONE READER READ TWICE does
    not, on most of them.  This arm tests the one candidate: the reader's OWN plastic object-file validity table
    (`situation_reader.py` pri 136 landing -> `self._of_validities`, a deep copy of the frozen asset that
    `entity_resolver.cluster(online=True)` accrues into on every high-margin merge/split decision, gated by
    HDLAB_OBJECT_FILE_ONLINE).  Freeze that one accrual and read the same document twice with the same reader: if
    the two reads then agree, the residual IS that accrual -- deliberate plasticity, the brain's form, and the
    reason the identity unit is ONE READER PER DOCUMENT."""
    st = install()
    test, gaz = _docs(n_docs)
    tmp = tempfile.mkdtemp(prefix="p146_resid_")
    rows = []
    for d in test:
        path = _conll(d, tmp)
        row = {"docid": d.docid}
        for label, flag in (("plastic_default", None), ("accrual_frozen", "0")):
            prev = os.environ.get("HDLAB_OBJECT_FILE_ONLINE")
            if flag is None:
                os.environ.pop("HDLAB_OBJECT_FILE_ONLINE", None)
            else:
                os.environ["HDLAB_OBJECT_FILE_ONLINE"] = flag
            try:
                r = _reader(gaz)
                _, sm1, _ = _read(path, gaz, cap=0, reader=r)
                d1 = _of_digest(r)
                _, sm2, _ = _read(path, gaz, cap=0, reader=r)
                d2 = _of_digest(r)
            finally:
                if prev is None:
                    os.environ.pop("HDLAB_OBJECT_FILE_ONLINE", None)
                else:
                    os.environ["HDLAB_OBJECT_FILE_ONLINE"] = prev
            row[label] = {"one_reader_twice_identical": sig_json(sig(sm1)) == sig_json(sig(sm2)),
                          "table_after_read_1": d1, "table_after_read_2": d2,
                          "the_reader_learned_from_the_document": (d1 != d2)}
        rows.append(row)
        print("  %-30s  plastic: identical=%-5s table moved=%-5s   frozen: identical=%-5s table moved=%s"
              % (d.docid, row["plastic_default"]["one_reader_twice_identical"],
                 row["plastic_default"]["the_reader_learned_from_the_document"],
                 row["accrual_frozen"]["one_reader_twice_identical"],
                 row["accrual_frozen"]["the_reader_learned_from_the_document"]))
    res = {"arm": "residual", "landed_before_install": st, "per_document": rows,
           "n_documents": len(rows),
           "n_identical_when_frozen": sum(1 for r in rows if r["accrual_frozen"]["one_reader_twice_identical"]),
           "n_identical_when_plastic": sum(1 for r in rows if r["plastic_default"]["one_reader_twice_identical"]),
           "plain": ("a reader that reads the same page twice does not answer identically, because it LEARNS from "
                     "what it reads; freezing that one piece of learning makes the two readings identical, which "
                     "is what identifies it")}
    _write("residual.json", res)
    print("\nidentical on the second reading: %d of %d with the learning ON, %d of %d with it FROZEN"
          % (res["n_identical_when_plastic"], len(rows), res["n_identical_when_frozen"], len(rows)))
    return res


def identity(n_docs=12, mode="annotated"):
    """BAR 3 -- THE IDENTITY GATE.  memo-inert vs memo-on, and (before landing) STOCK vs memo-on: byte-identical
    situation models, or FAIL."""
    st = install()
    test, gaz = _docs(n_docs)
    tmp = tempfile.mkdtemp(prefix="p146_ident_")
    rows = []
    for d in test:
        path = _conll(d, tmp)
        off_t, off_sm, off_m = _read(path, gaz, cap=0)
        on_t, on_sm, on_m = _read(path, gaz, cap=None)
        off_j, on_j = sig_json(sig(off_sm)), sig_json(sig(on_sm))
        row = {"docid": d.docid, "n_sentences": off_sm.n_sentences, "n_events": len(off_sm.events),
               "memo_off_vs_on_identical": off_j == on_j, "memo": on_m,
               "off_s": round(off_t, 3), "on_s": round(on_t, 3)}
        if not st["memo"]:
            _, stock_sm = _stock_read(path, gaz)
            row["stock_vs_memo_on_identical"] = sig_json(sig(stock_sm)) == on_j
        else:
            row["stock_vs_memo_on_identical"] = None      # the patch has landed: there is no stock arm to run
        row["identical"] = bool(row["memo_off_vs_on_identical"] and row["stock_vs_memo_on_identical"] is not False)
        rows.append(row)
        print("  %-30s identical=%-5s  hits=%-4d misses=%-4d peak=%-4d  %.2fs -> %.2fs"
              % (d.docid, row["identical"], on_m["hits"], on_m["misses"], on_m["peak_entries"], off_t, on_t))
    res = {"arm": "identity", "landed_before_install": st, "n_documents": len(rows),
           "n_identical": sum(1 for r in rows if r["identical"]),
           "n_failed": sum(1 for r in rows if not r["identical"]), "per_document": rows,
           "plain": ("the same documents are read with the memory of the graph walk switched off and switched on, "
                     "and the two situation models are compared field by field; any difference is a failure")}
    _write("identity.json", res)
    print("\nIDENTICAL: %d of %d documents (failures: %d)"
          % (res["n_identical"], res["n_documents"], res["n_failed"]))
    return res


def twin(n_docs=2, mode="annotated"):
    """BAR 4 -- THE POISONED-MEMO TWIN.  A memo that returns a WRONG stored vector on a hit must CHANGE the read.
    If it does not, the walk's result is not consumed -- a larger finding."""
    import hdlab.grounded_semantic_graph as GSG
    st = install()
    good = GSG.ActivationMemo

    class PoisonedMemo(good):
        """The info-free twin: on a HIT, return the activation of a DIFFERENT cue set (the previous distinct
        result).  Every other property -- key, capacity, call pattern -- is identical."""

        def get(self, key, Tt):
            v = good.get(self, key, Tt)
            if v is None:
                return None
            for k, other in self.d.items():
                if k != key:
                    return other
            return v

    import numpy as _np

    class PermutedMemo(good):
        """THE STRONGER TWIN.  A hit returns the correct activation with its NODE IDENTITIES PERMUTED (a fixed
        seed): the same shape, the same value distribution, every value on the wrong synset.  `PoisonedMemo`
        returns another cue set's real activation, which can be highly correlated with the right one -- this one
        cannot be."""

        def get(self, key, Tt):
            v = good.get(self, key, Tt)
            if v is None:
                return None
            if getattr(self, "_perm", None) is None or len(self._perm) != len(v):
                self._perm = _np.random.RandomState(20260916).permutation(len(v))
            return v[self._perm]

    test, gaz = _docs(n_docs)
    tmp = tempfile.mkdtemp(prefix="p146_twin_")
    rows = []
    for d in test:
        path = _conll(d, tmp)
        _, clean_sm, clean_m = _read(path, gaz, cap=None)
        clean = sig_json(sig(clean_sm))
        n_aff = sum(1 for e in clean_sm.events if e.affect is not None)
        row = {"docid": d.docid, "hits": clean_m["hits"], "calls": clean_m["calls"],
               "affect_fields_clean": n_aff}
        for label, factory in (("hit_returns_another_cue_sets_activation", PoisonedMemo),
                               ("hit_returns_the_activation_with_node_identities_permuted", PermutedMemo)):
            _, sm, _ = _read(path, gaz, cap=None, memo_factory=factory)
            GSG.ActivationMemo = good
            row[label] = {"changes_the_read": sig_json(sig(sm)) != clean,
                          "affect_fields": sum(1 for e in sm.events if e.affect is not None)}
        # AND THE QUESTION THE WEAK TWIN RAISES: is the WALK consumed at all?  Destroy EVERY walk (hit or miss)
        # the same way and see how much of the read moves.  This is not a memo control -- it prices the whole
        # 61% of the read the walk costs.
        base_ppr = GSG._ppr
        perm = _np.random.RandomState(20260916)

        def every_walk_permuted(seed_idx, Tt, n, d_=GSG.DAMPING, iters=GSG.PPR_ITERS, _o=base_ppr, _st={}):
            r = _o(seed_idx, Tt, n, d_, iters)
            if r is None:
                return None
            p = _st.get(len(r))
            if p is None:
                p = _st[len(r)] = perm.permutation(len(r))
            return r[p]

        GSG._ppr = every_walk_permuted
        try:
            _, sm_all, _ = _read(path, gaz, cap=None)
        finally:
            GSG._ppr = base_ppr
        row["every_walk_permuted"] = {"changes_the_read": sig_json(sig(sm_all)) != clean,
                                      "affect_fields": sum(1 for e in sm_all.events if e.affect is not None),
                                      "n_events_clean": len(clean_sm.events), "n_events": len(sm_all.events)}
        rows.append(row)
        print("  %-28s hits=%-4d/%-4d  HIT->other-cue %-5s  HIT->permuted %-5s  EVERY-WALK->permuted %-5s"
              "  (affect %d -> %d / %d / %d)"
              % (d.docid, row["hits"], row["calls"],
                 row["hit_returns_another_cue_sets_activation"]["changes_the_read"],
                 row["hit_returns_the_activation_with_node_identities_permuted"]["changes_the_read"],
                 row["every_walk_permuted"]["changes_the_read"], n_aff,
                 row["hit_returns_another_cue_sets_activation"]["affect_fields"],
                 row["hit_returns_the_activation_with_node_identities_permuted"]["affect_fields"],
                 row["every_walk_permuted"]["affect_fields"]))
    GSG.ActivationMemo = good
    res = {"arm": "twin", "landed_before_install": st, "per_document": rows, "n_documents": len(rows),
           "n_changed_hit_other_cue": sum(1 for r in rows
                                          if r["hit_returns_another_cue_sets_activation"]["changes_the_read"]),
           "n_changed_hit_permuted": sum(
               1 for r in rows
               if r["hit_returns_the_activation_with_node_identities_permuted"]["changes_the_read"]),
           "n_changed_every_walk_permuted": sum(1 for r in rows if r["every_walk_permuted"]["changes_the_read"]),
           "plain": ("a deliberately wrong memory of the graph walk must change what the reader concludes; the "
                     "third arm destroys EVERY walk, not just the remembered ones, which prices how much of the "
                     "reading actually depends on the most expensive operation in it")}
    _write("twin.json", res)
    print("\nchanged the read: %d/%d (a hit returns another cue set's activation), %d/%d (a hit returns it "
          "permuted), %d/%d (EVERY walk permuted)"
          % (res["n_changed_hit_other_cue"], len(rows), res["n_changed_hit_permuted"], len(rows),
             res["n_changed_every_walk_permuted"], len(rows)))
    return res


def timing(n_docs=6, pairs=3, mode="annotated"):
    """BAR 5 -- THE SAVING, HONESTLY TIMED.  Paired and ALTERNATING (off, on, on, off) per pair so a drift in the
    machine's load hits both arms equally; a pair whose two halves disagree by more than 3x, or whose saving is
    negative, is DISCARDED and reported."""
    st = install()
    test, gaz = _docs(n_docs)
    tmp = tempfile.mkdtemp(prefix="p146_time_")
    rows = []
    for d in test:
        path = _conll(d, tmp)
        _read(path, gaz, cap=0)                      # warm every lazy asset OUT of the measurement
        offs, ons, kept, dropped = [], [], [], []
        stats = None
        for i in range(pairs):
            if i % 2 == 0:
                t_off = _read(path, gaz, cap=0)[0]
                t_on, _, stats = _read(path, gaz, cap=None)[0:3]
            else:
                t_on, _, stats = _read(path, gaz, cap=None)[0:3]
                t_off = _read(path, gaz, cap=0)[0]
            offs.append(t_off); ons.append(t_on)
            bad = (t_on >= t_off) or (max(t_on, t_off) / max(min(t_on, t_off), 1e-9) > 3.0)
            (dropped if bad else kept).append({"pair": i, "off_s": round(t_off, 3), "on_s": round(t_on, 3)})
        row = {"docid": d.docid, "pairs": pairs, "kept": kept, "discarded": dropped, "memo": stats,
               # THE UNSELECTED NUMBER TOO.  Discarding a pair because the memo arm was SLOWER selects on the
               # outcome, which biases the kept mean upward; the all-pairs mean is reported beside it so the
               # size of that bias is visible rather than hidden by the rule.
               "mean_off_s_ALL_pairs": round(sum(offs) / len(offs), 3),
               "mean_on_s_ALL_pairs": round(sum(ons) / len(ons), 3),
               "saved_share_ALL_pairs": round((sum(offs) - sum(ons)) / sum(offs), 4)}
        if kept:
            mo = sum(k["off_s"] for k in kept) / len(kept)
            mn = sum(k["on_s"] for k in kept) / len(kept)
            row.update({"mean_off_s": round(mo, 3), "mean_on_s": round(mn, 3),
                        "saved_s": round(mo - mn, 3), "saved_share": round((mo - mn) / mo, 4)})
        rows.append(row)
        print("  %-30s kept=%d/%d  %s" % (d.docid, len(kept), pairs,
              ("%.2fs -> %.2fs (-%.1f%%)  hits=%d/%d peak=%d"
               % (row["mean_off_s"], row["mean_on_s"], 100 * row["saved_share"], stats["hits"],
                  stats["calls"], stats["peak_entries"])) if kept else "ALL PAIRS DISCARDED"))
    ok = [r for r in rows if r.get("kept")]
    res = {"arm": "timing", "landed_before_install": st, "per_document": rows,
           "n_documents": len(rows), "n_documents_with_a_stable_pair": len(ok),
           "mean_saved_share": round(sum(r["saved_share"] for r in ok) / len(ok), 4) if ok else None,
           "mean_saved_s": round(sum(r["saved_s"] for r in ok) / len(ok), 3) if ok else None,
           "mean_saved_share_ALL_pairs": round(sum(r["saved_share_ALL_pairs"] for r in rows) / len(rows), 4),
           "plain": ("how much of the reading time the memory of the graph walk removes, timed in alternating "
                     "pairs on the same machine so another job's load falls on both arms equally")}
    _write("timing.json", res)
    if ok:
        print("\nmean saving %.1f%% (%.2fs per document) over %d documents"
              % (100 * res["mean_saved_share"], res["mean_saved_s"], len(ok)))
    return res


def consumers(n_docs=12, mode="annotated"):
    """PHASE 7 (A) -- WHY DESTROYING 61% OF THE READ MOVES ~ONE FIELD.  The walk reaches the record through a
    chain of three gates, and this arm counts the survivors at each one.

    THE CHAIN, read from code (`force_dynamics_valence.force_dynamics_event_type` :844-895):
      1. `context_sense_sign(verb, toks, gi)` -> `select_sense_blended` -> `_blend_pick`, which is
         argmax[ log P_freq + lam * log PPR ] (`grounded_semantic_graph.py:248`).  THE WALK IS ONE TERM BESIDE
         THE FREQUENCY RESTING LEVEL, so it only matters when it overturns that argmax.
      2. the sign of the chosen synset is used ONLY as `override`, and only when the WORD-LEVEL cascade has no
         sign (`endstate_valence_sign(gov_word) is None`); `affecting is False` instead ABSTAINS outright.
      3. `sense_posterior_in_context` (its own blend, lam = affect_lexicon.SENSE_LAM = 4.0) is passed to
         `harm_help_arithmetic` as one more term, and `situation_reader._assign_affect` then reports nothing
         unless the certified animacy-axis override fired (`stage == "event"`).

    MEASURED HERE, per document: (a) how often the walk's term changes the argmax it is blended into, with the
    frequency barrier log(pf_top1) - log(pf_top2) recorded per call so a GATE can be sized; (b) how many chosen
    SENSE IDS change when every walk is permuted (the intermediate the earlier twin could not see); (c) how many
    (sign, affecting) verdicts change; (d) how many recorded affect fields change.  The drop from (b) to (d) IS
    the answer to 'why does destroying the walk move one field'."""
    import numpy as _np
    st = install()
    import hdlab.grounded_semantic_graph as GSG
    import hdlab.force_dynamics_valence as FDV
    test, gaz = _docs(n_docs)
    tmp = tempfile.mkdtemp(prefix="p146_cons_")
    rows = []

    def _instrument(rec):
        """Record the blend's inputs and both argmaxes, the sense verdicts, and the posterior's argmax."""
        base_blend, base_sign, base_post = GSG._blend_pick, FDV.context_sense_sign, FDV.sense_posterior_in_context

        def blend(ppr, prior, lam, alpha=0.1, eps=1e-6):
            out = base_blend(ppr, prior, lam, alpha, eps)
            pf = _np.asarray(prior, float) + alpha
            pf = pf / pf.sum()
            order = _np.argsort(-pf)
            barrier = float(_np.log(pf[order[0]]) - _np.log(pf[order[1]])) if len(pf) > 1 else float("inf")
            rec["blend"].append({"prior_argmax": int(order[0]), "picked": int(out),
                                 "walk_changed_the_argmax": int(out) != int(order[0]),
                                 "frequency_barrier": round(barrier, 4), "n_senses": int(len(pf)),
                                 "had_walk": ppr is not None})
            return out

        def sign(verb, tokens, gov_idx):
            out = base_sign(verb, tokens, gov_idx)
            rec["sign"][(verb, tuple(tokens), gov_idx)] = out
            return out

        def post(verb, tokens, gov_idx, lam=None):
            out = base_post(verb, tokens, gov_idx, lam)
            am = int(_np.argmax(out)) if out else None
            rec["post"][(verb, tuple(tokens), gov_idx)] = am
            return out

        GSG._blend_pick = blend
        FDV.context_sense_sign = sign
        FDV.sense_posterior_in_context = post
        return (base_blend, base_sign, base_post)

    def _uninstrument(saved):
        GSG._blend_pick, FDV.context_sense_sign, FDV.sense_posterior_in_context = saved

    for d in test:
        path = _conll(d, tmp)
        clean = {"blend": [], "sign": {}, "post": {}}
        saved = _instrument(clean)
        try:
            _, sm_clean, _ = _read(path, gaz, cap=None)
        finally:
            _uninstrument(saved)

        pois = {"blend": [], "sign": {}, "post": {}}
        base_ppr = GSG._ppr
        _perm = {}

        def every_walk_permuted(seed_idx, Tt, n, d_=GSG.DAMPING, iters=GSG.PPR_ITERS, _o=base_ppr):
            r = _o(seed_idx, Tt, n, d_, iters)
            if r is None:
                return None
            p = _perm.get(len(r))
            if p is None:
                p = _perm[len(r)] = _np.random.RandomState(20260916).permutation(len(r))
            return r[p]

        saved = _instrument(pois)
        GSG._ppr = every_walk_permuted
        try:
            _, sm_pois, _ = _read(path, gaz, cap=None)
        finally:
            GSG._ppr = base_ppr
            _uninstrument(saved)

        # (a) the walk's term against the frequency resting level, on the CLEAN read
        b = clean["blend"]
        with_walk = [x for x in b if x["had_walk"]]
        changed = [x for x in with_walk if x["walk_changed_the_argmax"]]
        # (b)-(c) the intermediates, keyed so a diverging control flow cannot mis-align them
        keys = set(clean["sign"]) & set(pois["sign"])
        sign_moved = [k for k in keys if clean["sign"][k] != pois["sign"][k]]
        pk = set(clean["post"]) & set(pois["post"])
        post_moved = [k for k in pk if clean["post"][k] != pois["post"][k]]
        # (d) the record
        aff_c = {(e.sent_idx, e.idx if hasattr(e, "idx") else e.global_idx, e.predicate): e.affect
                 for e in sm_clean.events}
        aff_p = {(e.sent_idx, e.idx if hasattr(e, "idx") else e.global_idx, e.predicate): e.affect
                 for e in sm_pois.events}
        shared = set(aff_c) & set(aff_p)
        aff_moved = [k for k in shared if aff_c[k] != aff_p[k]]
        row = {"docid": d.docid,
               "blend_calls": len(b), "blend_calls_with_a_walk": len(with_walk),
               "walk_changed_the_argmax": len(changed),
               "walk_changed_share": round(len(changed) / max(len(with_walk), 1), 4),
               "frequency_barrier_when_changed": sorted(round(x["frequency_barrier"], 3) for x in changed)[:12],
               "sense_verdicts": len(keys), "sense_verdicts_moved_under_permutation": len(sign_moved),
               "posterior_argmax_compared": len(pk), "posterior_argmax_moved": len(post_moved),
               "events_compared": len(shared), "affect_fields_moved": len(aff_moved),
               "affect_fields_set_clean": sum(1 for k in shared if aff_c[k] is not None)}
        # THE GATE SIZING: skip the walk when the frequency barrier is already >= tau, and count what is lost.
        gate = {}
        for tau in (0.0, 0.5, 1.0, 2.0, 3.0, 4.0, 6.0):
            skipped = [x for x in with_walk if x["frequency_barrier"] >= tau]
            lost = [x for x in skipped if x["walk_changed_the_argmax"]]
            gate["tau_%.1f" % tau] = {"walks_skipped": len(skipped),
                                      "share_skipped": round(len(skipped) / max(len(with_walk), 1), 4),
                                      "argmax_changes_lost": len(lost),
                                      "share_of_changes_lost": round(len(lost) / max(len(changed), 1), 4)}
        row["gate_sizing"] = gate
        rows.append(row)
        print("  %-28s blend %-4d (walk %-4d)  walk flips argmax %-4d (%.1f%%)  sense verdicts moved %-3d/%-4d  "
              "posterior argmax moved %-3d/%-4d  affect fields moved %d/%d"
              % (d.docid, len(b), len(with_walk), len(changed), 100 * row["walk_changed_share"],
                 len(sign_moved), len(keys), len(post_moved), len(pk), len(aff_moved), len(shared)))
    tot = {k: sum(r[k] for r in rows) for k in
           ("blend_calls", "blend_calls_with_a_walk", "walk_changed_the_argmax", "sense_verdicts",
            "sense_verdicts_moved_under_permutation", "posterior_argmax_compared", "posterior_argmax_moved",
            "events_compared", "affect_fields_moved", "affect_fields_set_clean")}
    gate_tot = {}
    for tau in (0.0, 0.5, 1.0, 2.0, 3.0, 4.0, 6.0):
        k = "tau_%.1f" % tau
        s = sum(r["gate_sizing"][k]["walks_skipped"] for r in rows)
        l = sum(r["gate_sizing"][k]["argmax_changes_lost"] for r in rows)
        gate_tot[k] = {"walks_skipped": s, "share_skipped": round(s / max(tot["blend_calls_with_a_walk"], 1), 4),
                       "argmax_changes_lost": l,
                       "share_of_changes_lost": round(l / max(tot["walk_changed_the_argmax"], 1), 4)}
    res = {"arm": "consumers", "landed_before_install": st, "per_document": rows, "totals": tot,
           "gate_sizing_totals": gate_tot,
           "walk_changed_the_argmax_share": round(tot["walk_changed_the_argmax"]
                                                  / max(tot["blend_calls_with_a_walk"], 1), 4),
           "sense_verdict_moved_share": round(tot["sense_verdicts_moved_under_permutation"]
                                              / max(tot["sense_verdicts"], 1), 4),
           "affect_field_moved_share": round(tot["affect_fields_moved"] / max(tot["events_compared"], 1), 4),
           "plain": ("the graph walk is one term beside how common each sense of the verb is; this counts how "
                     "often it actually overturns that, how often destroying it changes the sense the reader "
                     "picks, and how often that reaches the reading it records")}
    _write("consumers.json", res)
    print("\nwalk overturns the frequency argmax on %d of %d walks (%.1f%%); destroying every walk moves the "
          "sense verdict on %d of %d (%.1f%%), the posterior argmax on %d of %d, and the RECORDED affect field "
          "on %d of %d events (%.2f%%)"
          % (tot["walk_changed_the_argmax"], tot["blend_calls_with_a_walk"],
             100 * res["walk_changed_the_argmax_share"], tot["sense_verdicts_moved_under_permutation"],
             tot["sense_verdicts"], 100 * res["sense_verdict_moved_share"], tot["posterior_argmax_moved"],
             tot["posterior_argmax_compared"], tot["affect_fields_moved"], tot["events_compared"],
             100 * res["affect_field_moved_share"]))
    return res


def crossdoc(n_docs=12, mode="annotated"):
    """PHASE 7 (D) -- THE CROSS-DOCUMENT REPEAT RATE, measured, no design.  ONE reader reads the 12 documents in
    sequence; every cue set and every activation key is stamped with the document that first asked for it, so
    'how much of document k's work was already done in documents 1..k-1' is a count and not an argument."""
    st = install()
    import hdlab.grounded_semantic_graph as GSG
    test, gaz = _docs(n_docs)
    tmp = tempfile.mkdtemp(prefix="p146_xdoc_")
    seen_walk, seen_cue = {}, {}
    base_ppr, base_seed = GSG._ppr, GSG._seed_set
    cur = {"doc": None}
    rows = []

    def ppr(seed_idx, Tt, n, d=GSG.DAMPING, iters=GSG.PPR_ITERS, _o=base_ppr):
        if seed_idx:
            k = (tuple(seed_idx), n, d, iters)
            if k in seen_walk:
                if seen_walk[k] != cur["doc"]:
                    cur["walk_xdoc"] += 1
            else:
                seen_walk[k] = cur["doc"]
                cur["walk_new"] += 1
        return _o(seed_idx, Tt, n, d, iters)

    def seed_set(wn, context_words, syn2idx, tgt_names, _o=base_seed):
        k = (tuple(context_words), tuple(sorted(set(tgt_names))))
        if k in seen_cue:
            if seen_cue[k] != cur["doc"]:
                cur["cue_xdoc"] += 1
        else:
            seen_cue[k] = cur["doc"]
            cur["cue_new"] += 1
        return _o(wn, context_words, syn2idx, tgt_names)

    GSG._ppr, GSG._seed_set = ppr, seed_set
    rdr = _reader(gaz)
    try:
        for i, d in enumerate(test):
            path = _conll(d, tmp)
            cur.update({"doc": i, "walk_new": 0, "walk_xdoc": 0, "cue_new": 0, "cue_xdoc": 0})
            _read(path, gaz, cap=None, reader=rdr)
            rows.append({"docid": d.docid, "order": i,
                         "walk_cue_sets_first_seen_here": cur["walk_new"],
                         "walk_cue_sets_already_seen_in_an_EARLIER_document": cur["walk_xdoc"],
                         "cue_sets_first_seen_here": cur["cue_new"],
                         "cue_sets_already_seen_in_an_EARLIER_document": cur["cue_xdoc"]})
            print("  %2d %-28s new activation keys %-4d  cross-document repeats %-4d   new cue sets %-4d  "
                  "cross-document repeats %d"
                  % (i, d.docid, cur["walk_new"], cur["walk_xdoc"], cur["cue_new"], cur["cue_xdoc"]))
    finally:
        GSG._ppr, GSG._seed_set = base_ppr, base_seed
    nw = sum(r["walk_cue_sets_first_seen_here"] for r in rows)
    xw = sum(r["walk_cue_sets_already_seen_in_an_EARLIER_document"] for r in rows)
    nc = sum(r["cue_sets_first_seen_here"] for r in rows)
    xc = sum(r["cue_sets_already_seen_in_an_EARLIER_document"] for r in rows)
    res = {"arm": "crossdoc", "landed_before_install": st, "per_document": rows, "n_documents": len(rows),
           "distinct_activation_keys": nw, "cross_document_activation_repeats": xw,
           "cross_document_activation_repeat_share": round(xw / max(nw + xw, 1), 4),
           "distinct_cue_sets": nc, "cross_document_cue_set_repeats": xc,
           "cross_document_cue_set_repeat_share": round(xc / max(nc + xc, 1), 4),
           "plain": ("how much of the work one page needs was already done on an earlier page -- the number a "
                     "store that outlived the reading would have to beat")}
    _write("crossdoc.json", res)
    print("\nACROSS 12 documents read in sequence: %d distinct activation cue sets, %d cross-document repeats "
          "(%.2f%%); %d distinct cue sets, %d cross-document repeats (%.2f%%)"
          % (nw, xw, 100 * res["cross_document_activation_repeat_share"], nc, xc,
             100 * res["cross_document_cue_set_repeat_share"]))
    return res


def lever(n_docs=4, pairs=2, mode="annotated"):
    """PHASE 4 -- THE SECOND REPEATED QUESTION ON THE SAME PATH, measured.  Three arms, alternating within one
    process: (A) nothing remembered; (B) the ACTIVATION remembered only; (C) the activation AND THE CUE SET
    remembered.  Reports the identity of all three and the marginal saving of the cue-set memo over the walk
    memo alone.  Discard rule as in `timing`."""
    st = install()
    test, gaz = _docs(n_docs)
    tmp = tempfile.mkdtemp(prefix="p146_lever_")
    rows = []
    for d in test:
        path = _conll(d, tmp)
        _read(path, gaz, cap=0)                                  # warm
        A, B, C = [], [], []
        sigs, stats = {}, {}
        for i in range(pairs):
            order = [("A", 0, False), ("B", None, False), ("C", None, True)]
            if i % 2:
                order.reverse()
            for name, cap, seeds in order:
                t, sm, s = _read(path, gaz, cap=cap, seeds=seeds)
                {"A": A, "B": B, "C": C}[name].append(t)
                sigs.setdefault(name, sig_json(sig(sm)))
                stats[name] = s
        mA, mB, mC = (sum(x) / len(x) for x in (A, B, C))
        row = {"docid": d.docid, "pairs": pairs,
               "mean_nothing_s": round(mA, 3), "mean_walk_memo_s": round(mB, 3), "mean_walk_and_cue_s": round(mC, 3),
               "walk_memo_saving": round((mA - mB) / mA, 4), "both_saving": round((mA - mC) / mA, 4),
               "cue_memo_marginal_saving_over_walk_alone": round((mB - mC) / mA, 4),
               "identical_A_B": sigs["A"] == sigs["B"], "identical_A_C": sigs["A"] == sigs["C"],
               "cue_hits": stats["C"]["seed_hits"], "cue_misses": stats["C"]["seed_misses"],
               "walk_hits": stats["C"]["hits"], "walk_calls": stats["C"]["calls"],
               "vector_bytes": stats["C"]["vector_bytes"], "peak_bytes": stats["C"]["peak_bytes"]}
        rows.append(row)
        print("  %-30s  nothing %.2fs | walk %.2fs (-%.1f%%) | walk+cue %.2fs (-%.1f%%)  cue hits=%d/%d  "
              "identical=%s/%s" % (d.docid, mA, mB, 100 * row["walk_memo_saving"], mC,
                                   100 * row["both_saving"], row["cue_hits"],
                                   row["cue_hits"] + row["cue_misses"], row["identical_A_B"], row["identical_A_C"]))
    res = {"arm": "lever", "landed_before_install": st, "per_document": rows,
           "n_identical": sum(1 for r in rows if r["identical_A_B"] and r["identical_A_C"]),
           "n_documents": len(rows),
           "mean_walk_memo_saving": round(sum(r["walk_memo_saving"] for r in rows) / len(rows), 4),
           "mean_both_saving": round(sum(r["both_saving"] for r in rows) / len(rows), 4),
           "mean_cue_marginal": round(sum(r["cue_memo_marginal_saving_over_walk_alone"] for r in rows) / len(rows), 4),
           "plain": ("the same page is read three ways -- remembering nothing, remembering the graph walk, and "
                     "remembering the graph walk and the list of words that seeds it -- and all three must give "
                     "the identical reading")}
    _write("lever.json", res)
    print("\nwalk memo %.1f%% | walk+cue %.1f%% | the cue set adds %.1f points"
          % (100 * res["mean_walk_memo_saving"], 100 * res["mean_both_saving"], 100 * res["mean_cue_marginal"]))
    return res


def board(n_docs=4, n_boot=200, mode="annotated"):
    """BAR 6 -- THE PRODUCT BOARD'S OWN ROWS.  The board's GUM block (`exp_board_rows_on_the_reader_v1.run_gum`:
    one read per document per provenance mode, all four GUM rows scored off that one situation model) is run in
    ONE process with the memo INERT and with the memo ON, and every row value is compared byte-identically.

    A THIRD ARM, on a tree where the patch has not landed: the STOCK board.  It separates the two halves of the
    change, because the board's `reader_textonly_pron_discovered` arm TAGS BETWEEN READS
    (`_write_two_conll` -> `_organ_pron_positions`) and therefore reads whatever passage the PREVIOUS document's
    read left installed on the shared organ -- exactly the leak `detach_passage` removes.  Any flip belongs to
    THAT arm and to the passage half, never to the memo."""
    st = install()
    import experiments.exp_board_rows_on_the_reader_v1 as B
    import hdlab.grounded_semantic_graph as GSG

    def _arm(cap):
        # On the STOCK arm the shim has been removed, so PPR_MEMO_MAX does not exist -- which is the point of
        # that arm.  (This crashed the first board run; the guard is the fix, not a silent skip.)
        has = hasattr(GSG, "PPR_MEMO_MAX")
        prev = GSG.PPR_MEMO_MAX if has else None
        if cap is not None and has:
            GSG.PPR_MEMO_MAX = cap
        try:
            t0 = time.perf_counter()
            rows = B.run_gum(n_docs=n_docs, n_boot=n_boot)
            return time.perf_counter() - t0, rows
        finally:
            if has:
                GSG.PPR_MEMO_MAX = prev

    off_t, off_rows = _arm(0)
    on_t, on_rows = _arm(None)
    stock_t, stock_rows = (None, None)
    if not st["memo"]:
        restore()
        try:
            stock_t, stock_rows = _arm(None)
        finally:
            install()

    def _cmp(a, b):
        """Per (mode, row) byte comparison of the board's own published row objects (`run_gum` returns
        {"rows": {mode: {row: ...}}, "per": {...}, "diag": ...}); `per` -- the raw per-document hit/total pairs
        every row is computed from -- is compared too, because it is the part with no timing in it."""
        out, diff = {}, []
        ra, rb = a.get("rows", {}), b.get("rows", {})
        for m in sorted(ra):
            for r in sorted(ra[m]):
                same = (json.dumps(ra[m][r], sort_keys=True, default=str)
                        == json.dumps(rb[m].get(r), sort_keys=True, default=str))
                out["%s/%s" % (m, r)] = same
                if not same:
                    diff.append("%s/%s" % (m, r))
        same_per = (json.dumps(a.get("per"), sort_keys=True, default=str)
                    == json.dumps(b.get("per"), sort_keys=True, default=str))
        out["per_document_scored_data"] = same_per
        if not same_per:
            diff.append("per_document_scored_data")
        return out, diff

    # RAW FIRST: a comparison bug must not throw away three board runs (it did, once).
    _write("board_raw.json", {"memo_off": off_rows, "memo_on": on_rows, "stock": stock_rows,
                             "seconds": {"memo_off": off_t, "memo_on": on_t, "stock": stock_t}})
    memo_cmp, memo_diff = _cmp(off_rows, on_rows)
    res = {"arm": "board", "landed_before_install": st, "n_documents": n_docs, "n_boot": n_boot,
           "memo_off_s": round(off_t, 1), "memo_on_s": round(on_t, 1),
           "memo_off_vs_on_per_row": memo_cmp, "memo_off_vs_on_rows_that_differ": memo_diff,
           "memo_off_vs_on_all_identical": not memo_diff,
           "reader_block_saved_share": round((off_t - on_t) / off_t, 4) if off_t else None}
    if stock_rows is not None:
        stock_cmp, stock_diff = _cmp(stock_rows, on_rows)
        res.update({"stock_s": round(stock_t, 1), "stock_vs_memo_on_per_row": stock_cmp,
                    "stock_vs_memo_on_rows_that_differ": stock_diff,
                    "stock_vs_memo_on_all_identical": not stock_diff})
    res["plain"] = ("the product board's own reading block is run with the memory of the graph walk off and on, "
                    "and every published row value is compared exactly; the third run is the board as it stands "
                    "today, which separates the memory change from the passage-file change")
    _write("board.json", res)
    print("\nMEMO OFF vs ON: %s (%d rows differ: %s)  block %.0fs -> %.0fs"
          % ("BYTE-IDENTICAL" if not memo_diff else "DIFFERS", len(memo_diff), memo_diff or "none", off_t, on_t))
    if stock_rows is not None:
        print("STOCK vs MEMO ON: %s (%d rows differ: %s)"
              % ("BYTE-IDENTICAL" if not res["stock_vs_memo_on_rows_that_differ"] else "DIFFERS",
                 len(res["stock_vs_memo_on_rows_that_differ"]), res["stock_vs_memo_on_rows_that_differ"] or "none"))
    return res


def _write(name, obj):
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(os.path.join(OUT_DIR, name), "w", encoding="utf-8") as fh:
        json.dump(obj, fh, indent=2)
    print("wrote %s" % os.path.join(OUT_DIR, name))


# =====================================================================================================================
# 6. SELF-TEST (no corpus; the real code path)
# =====================================================================================================================

def self_test() -> int:
    import numpy as np
    import scipy.sparse as sp
    ok = []

    def chk(name, cond, detail=""):
        ok.append(bool(cond))
        print("  [%s] %s%s" % ("PASS" if cond else "FAIL", name, ("  -- " + detail) if detail else ""))

    install()
    import hdlab.grounded_semantic_graph as GSG
    import hdlab.lexical_categories as LC

    # a tiny 4-node row-stochastic graph: the walk is exercised for real
    T = GSG._row_stochastic(GSG._symmetrize([0, 1, 2], [1, 2, 3], 4))
    r0 = GSG._ppr([0], T, 4)
    p = np.zeros(4, np.float32); p[[0]] = 1.0; ref = p.copy()
    for _ in range(GSG.PPR_ITERS):
        ref = (1.0 - GSG.DAMPING) * p + GSG.DAMPING * (T @ ref)
    chk("T1 the walk with NO memo bound is byte-identical to the stated formula",
        r0 is not None and np.array_equal(np.asarray(r0), np.asarray(ref)), "sum=%.4f" % float(r0.sum()))

    m = GSG.ActivationMemo()
    with GSG.spreading(m):
        a = GSG._ppr([0, 2], T, 4)
        b = GSG._ppr([0, 2], T, 4)
        c = GSG._ppr([1], T, 4)
    chk("T2 a repeat of the SAME cue set is a HIT and returns the identical vector",
        m.hits == 1 and m.misses == 2 and a is b, "hits=%d misses=%d" % (m.hits, m.misses))
    chk("T3 a DIFFERENT cue set never collides with it", c is not a and m.peak == 2, "peak=%d" % m.peak)
    chk("T4 the memo is released at the end of the binding", GSG._ACTIVE_MEMO is None)

    # the memoised walk equals the unmemoised walk exactly
    m2 = GSG.ActivationMemo()
    with GSG.spreading(m2):
        d1 = GSG._ppr([0, 2], T, 4)
    chk("T5 the memoised value is byte-identical to the recomputed one",
        np.array_equal(np.asarray(d1), np.asarray(a)))

    # capacity + LRU
    m3 = GSG.ActivationMemo(cap=2)
    with GSG.spreading(m3):
        for s in ([0], [1], [2], [3]):
            GSG._ppr(s, T, 4)
    chk("T6 the memo is capacity-bounded and evicts least-recently-used first",
        len(m3.d) == 2 and m3.evictions == 2, "held=%d evictions=%d" % (len(m3.d), m3.evictions))
    m4 = GSG.ActivationMemo(cap=0)
    with GSG.spreading(m4):
        GSG._ppr([0], T, 4); GSG._ppr([0], T, 4)
    chk("T7 cap 0 makes the memo inert (the un-memoised arm)", m4.hits == 0 and len(m4.d) == 0)

    # the graph is pinned by identity
    T2 = GSG._row_stochastic(GSG._symmetrize([0, 1], [2, 3], 4))
    m5 = GSG.ActivationMemo()
    with GSG.spreading(m5):
        GSG._ppr([0], T, 4)
        e2 = GSG._ppr([0], T2, 4)
    chk("T8 a different graph never serves a stored vector", m5.hits == 0 and e2 is not None)

    # the poisoned twin really does return the wrong vector
    good = GSG.ActivationMemo

    class Poison(good):
        def get(self, key, Tt):
            v = good.get(self, key, Tt)
            if v is None:
                return None
            for k, other in self.d.items():
                if k != key:
                    return other
            return v

    mp = Poison()
    with GSG.spreading(mp):
        p1 = GSG._ppr([0], T, 4)
        GSG._ppr([3], T, 4)
        p2 = GSG._ppr([0], T, 4)
    chk("T9 the poisoned twin returns a DIFFERENT vector on a hit", not np.array_equal(p1, p2))

    # the passage file
    lc = LC.get()
    lc.new_document()
    p = LC.current_passage()
    chk("T10 a passage boundary opens a file the reader can take", p is not None and lc._reg is p.reg)
    p.pos_memo["x y"] = ("NOUN", "NOUN")
    got = LC.detach_passage()
    chk("T11 detaching hands the file back and leaves the organ with NO passage",
        got is p and lc._reg is None and lc._doc_shape == {} and LC.current_passage() is None)
    chk("T12 the passage's POS memo travelled with the file, not with the module", got.pos_memo == {"x y": ("NOUN", "NOUN")})
    chk("T13 no process-global generation counter survives", not hasattr(LC, "_REG_GEN"))
    lc.new_document()
    g1 = LC.register_generation()
    lc.new_document()
    chk("T14 register_generation still reports the organ's open passage", LC.register_generation() == g1 + 1)
    LC.detach_passage()

    # the SECOND lever: the cue set is remembered too, and it changes no answer
    class _Syn:
        def __init__(self, nm):
            self._n = nm

        def name(self):
            return self._n

    class _WN:
        def __init__(self):
            self.calls = 0

        def synsets(self, w):
            self.calls += 1
            return [_Syn(w + ".n.01"), _Syn(w + ".n.02")]

    names = ["a.n.01", "a.n.02", "b.n.01", "b.n.02", "t.n.01", "t.n.02"]
    syn2idx = {nm: i for i, nm in enumerate(names)}
    Tw = GSG._row_stochastic(GSG._symmetrize([0, 1, 2], [4, 5, 3], len(names)))
    tgt = [_Syn("t.n.01"), _Syn("t.n.02")]
    tn = ["t.n.01", "t.n.02"]
    wn = _WN()
    m6 = GSG.ActivationMemo()
    with GSG.spreading(m6):
        v1 = GSG._sense_ppr(wn, "t", "V", ["a", "b"], syn2idx, Tw, len(names), tgt, tn)
        after_first = wn.calls
        v2 = GSG._sense_ppr(wn, "t", "V", ["a", "b"], syn2idx, Tw, len(names), tgt, tn)
    chk("T18 the CUE SET is remembered too: the second ask does no lexicon lookup at all",
        wn.calls == after_first and m6.seed_hits == 1 and m6.seed_misses == 1,
        "lexicon calls %d then %d; seed hits=%d" % (after_first, wn.calls, m6.seed_hits))
    wn2 = _WN()
    prev_seed = GSG.SEED_MEMO
    GSG.SEED_MEMO = False
    m7 = GSG.ActivationMemo()
    try:
        with GSG.spreading(m7):
            v3 = GSG._sense_ppr(wn2, "t", "V", ["a", "b"], syn2idx, Tw, len(names), tgt, tn)
    finally:
        GSG.SEED_MEMO = prev_seed
    chk("T19 remembering the cue set changes no answer (and the walk memo alone still works)",
        np.array_equal(np.asarray(v1), np.asarray(v2)) and np.array_equal(np.asarray(v1), np.asarray(v3))
        and m7.seed_hits == 0)

    # the diff renders and is anchored
    d = make_diff()
    chk("T15 the patch anchors all match exactly once and the diff renders",
        d.count("diff --git") == 3 and "def _ppr(" in d and "class PassageFile" in d, "%d bytes" % len(d))
    for rel, path, edits in PATCH:
        src = patched_source(path, edits)
        compile(src, path, "exec")
    chk("T16 every patched file still compiles", True)

    restore()
    chk("T17 restore puts the stock tree back", not hasattr(GSG, "_ACTIVE_MEMO")
        and not hasattr(GSG, "ActivationMemo") and hasattr(LC, "_REG_GEN") and not landed()["memo"])
    # T20 -- the harness's own can-fail check: install/restore/INSTALL must really re-install, or an arm that
    # believes it is memoised would silently run unmemoised (this bug was in the first version of this cell).
    install()
    m8 = GSG.ActivationMemo()
    with GSG.spreading(m8):
        GSG._ppr([0, 2], T, 4)
        GSG._ppr([0, 2], T, 4)
    chk("T20 install after a restore really re-installs (the arm cannot silently lose its memo)", m8.hits == 1,
        "hits=%d" % m8.hits)
    restore()
    print("\n%d/%d self-test checks passed" % (sum(ok), len(ok)))
    _write("selftest.json", {"passed": sum(ok), "total": len(ok), "all_green": all(ok)})
    return 0 if all(ok) else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--stability", action="store_true")
    ap.add_argument("--identity", action="store_true")
    ap.add_argument("--twin", action="store_true")
    ap.add_argument("--timing", action="store_true")
    ap.add_argument("--board", action="store_true")
    ap.add_argument("--lever", action="store_true")
    ap.add_argument("--residual", action="store_true")
    ap.add_argument("--consumers", action="store_true")
    ap.add_argument("--crossdoc", action="store_true")
    ap.add_argument("--n-boot", type=int, default=200)
    ap.add_argument("--make-diff", action="store_true")
    ap.add_argument("--out", default=None, help="write the diff HERE, in bytes (never shell-redirect it)")
    ap.add_argument("--docs", type=int, default=12)
    ap.add_argument("--pairs", type=int, default=3)
    ap.add_argument("--mode", default="annotated", choices=("annotated", "textonly"))
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    if a.make_diff:
        # BYTES, never text: the diff carries each file's own line endings, and a text-mode write on Windows
        # would turn every "\n" into "\r\n" and every CRLF line into "\r\r\n" (git apply then rejects the patch
        # while `git apply --ignore-whitespace` accepts it -- the exact signature of this mistake).
        blob = make_diff().encode("utf-8")
        if a.out:
            with open(a.out, "wb") as fh:
                fh.write(blob)
            print("wrote %s (%d bytes)" % (a.out, len(blob)))
        else:
            sys.stdout.buffer.write(blob)
        return 0
    if a.stability:
        stability(a.docs, a.mode)
    if a.residual:
        residual(a.docs, a.mode)
    if a.identity:
        identity(a.docs, a.mode)
    if a.twin:
        twin(a.docs, a.mode)
    if a.timing:
        timing(a.docs, a.pairs, a.mode)
    if a.consumers:
        consumers(a.docs, a.mode)
    if a.crossdoc:
        crossdoc(a.docs, a.mode)
    if a.lever:
        lever(a.docs, a.pairs, a.mode)
    if a.board:
        board(a.docs, a.n_boot, a.mode)
    if not any((a.stability, a.identity, a.twin, a.timing, a.board, a.lever, a.residual, a.consumers,
                a.crossdoc)):
        ap.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
