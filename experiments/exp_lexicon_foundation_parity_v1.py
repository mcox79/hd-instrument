"""exp_lexicon_foundation_parity_v1 -- FREEZE THE LEXICON: what the live read asks NLTK, and whether one
frozen offline organ answers it byte-identically.

problem: the_nltk_library_is_called_at_read_time_in_37_hdlab_modules_78_sites_to_read_static_lexica_freeze_
         wordnet_verbnet_framenet_into_one_offline_asset_behind_one_lexicon_organ_and_retire_the_model_stand_ins
         (priority 127)

THE BRAIN'S MECHANISM (the opening move). The brain has no library call. Lexical knowledge -- the sense
inventory of a word, its supersense, its taxonomic parents, its argument frames, its polarity -- is STORED in
the anterior-temporal hub and its spokes and retrieved by CONTENT-ADDRESSED lookup at read time (Patterson,
Nestor & Rogers 2007; Binder & Desai 2011). Acquisition happened offline, during development; retrieval at
read time is an address -> content read with no acquisition machinery in the loop. Our equivalent: ONE frozen
offline asset built once from the vetted static lexica (WordNet 3.0, VerbNet 3.x, FrameNet 1.7, the opinion
lexicon -- admissible static SUPPLY) and ONE organ that serves address -> content at read time with no
external library in the call chain. Exactly the shape hdlab/morphology.py already landed for morphy.

THE MODES (each can fail):
  --record    a recording shim on nltk.corpus.{wordnet,verbnet,framenet,opinion_lexicon,stopwords} logs every
              (hdlab module, function, line, corpus, operation, receiver, args) the DEFAULT read makes on the
              modern GUM harness -> queries.jsonl + the site table (reached / not reached, per-document
              counts, relations used).
  --rewire    build the PATCHED tree (every nltk import site routed to hdlab.lexicon_foundation) and emit the
              unified diff. Mechanical, rule-based, and it prints every line it changed.
  --parity    replay EVERY logged query against the organ and against NLTK; the answers must be equal, in
              order. Disagreements are counted and listed.
  --identity  the default read run in two subprocesses -- SHIPPED tree vs PATCHED tree with every nltk import
              POISONED (an import raises) -- must produce the same situation-model digest. This is the
              can-fail form: under the poison, any surviving library call is a crash, not a silent pass.
  --timing    per-document read time and query counts, shipped vs organ.
  --run       record -> rewire -> parity -> identity -> timing, into metrics.json.

Glass-box; the ONLY nltk here is the recording shim and the parity REFERENCE (both measurement, never
inference). Build-time nltk lives in tools/build_lexicon_foundation_index.py.
Run: .venv/Scripts/python.exe experiments/exp_lexicon_foundation_parity_v1.py --self-test
     .venv/Scripts/python.exe experiments/exp_lexicon_foundation_parity_v1.py --run --docs 4
"""
from __future__ import annotations
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "2")
os.environ.setdefault("PYTHONHASHSEED", "0")
import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
import time
import types as _types
from collections import Counter
from datetime import datetime, timezone

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from experiments._seed_checkpoint import get_output_dir

ANCHOR = "lexicon_foundation_parity_v1"
OUT_DIR = str(get_output_dir(ANCHOR))
SEED = 20260915
PATCHED = os.path.join(OUT_DIR, "patched_tree")
SLUG = ("the_nltk_library_is_called_at_read_time_in_37_hdlab_modules_78_sites_to_read_static_lexica_freeze_"
        "wordnet_verbnet_framenet_into_one_offline_asset_behind_one_lexicon_organ_and_retire_the_model_stand_ins")
DIFF_PATH = os.path.join(_REPO, "notes", "problems", SLUG, "lexicon_foundation_patch.diff")

# ------------------------------------------------------------------ the recording shim (measurement only)
# nltk returns rich objects (Synset, Lemma, VerbnetClass, Frame). To log the RELATIONS the live path walks we
# proxy those objects too: every callable attribute becomes a recording call, and any Synset / Lemma in the
# result is re-wrapped so the next hop is logged as well. Equality and hashing delegate to the wrapped object
# so `synset in hypernym_path` keeps working.
_SS_TYPES = ("Synset", "Lemma")


def _hdlab_caller():
    """(module, function, line) of the innermost hdlab/ frame -- the SITE that made the query."""
    f = sys._getframe(2)
    while f is not None:
        fn = f.f_code.co_filename.replace("\\", "/")
        if "/hdlab/" in fn and "lexicon_foundation" not in fn:
            return (os.path.basename(fn), f.f_code.co_name, f.f_lineno)
        f = f.f_back
    return ("<non-hdlab>", "<n/a>", 0)


def _key(obj):
    o = getattr(obj, "_o", obj)
    cn = type(o).__name__
    if cn == "Synset":
        return o.name()
    if cn == "Lemma":
        return "%s::%s" % (o.synset().name(), o.name())
    return repr(o)[:80]


def log_corpus_of(kind):
    return "wordnet" if kind in _SS_TYPES else kind


def _unwrap(x):
    if isinstance(x, _Rec):
        return object.__getattribute__(x, "_o")
    if isinstance(x, list):
        return [_unwrap(v) for v in x]
    if isinstance(x, tuple):
        return tuple(_unwrap(v) for v in x)
    return x


def _wrap(x, log):
    cn = type(x).__name__
    if cn in _SS_TYPES:
        return _Rec(x, log, cn)
    if isinstance(x, list):
        return [_wrap(v, log) for v in x]
    if isinstance(x, tuple):
        return tuple(_wrap(v, log) for v in x)
    if isinstance(x, _types.GeneratorType):
        return (_wrap(v, log) for v in x)
    return x


def _jsonable(x):
    if isinstance(x, (str, int, float, bool)) or x is None:
        return x
    if isinstance(x, (list, tuple)):
        return [_jsonable(v) for v in x]
    cn = type(x).__name__
    if cn == "Synset":
        return {"__synset__": x.name()}
    if cn == "Lemma":
        return {"__lemma__": "%s::%s" % (x.synset().name(), x.name())}
    return {"__repr__": repr(x)[:120]}


class _Rec:
    """Proxy that records every call made through it."""
    __slots__ = ("_o", "_log", "_kind")

    def __init__(self, o, log, kind):
        object.__setattr__(self, "_o", o)
        object.__setattr__(self, "_log", log)
        object.__setattr__(self, "_kind", kind)

    def __getattr__(self, name):
        o = object.__getattribute__(self, "_o")
        log = object.__getattribute__(self, "_log")
        kind = object.__getattribute__(self, "_kind")
        attr = getattr(o, name)
        if not callable(attr):
            return attr
        recv = _key(o) if kind in _SS_TYPES else None

        def _call(*a, **kw):
            mod, func, line = _hdlab_caller()
            aa = [_unwrap(x) for x in a]
            kk = {k: _unwrap(v) for k, v in kw.items()}
            out = attr(*aa, **kk)
            log.append({"corpus": log_corpus_of(kind), "kind": kind, "op": name, "recv": recv,
                        "args": [_jsonable(x) for x in aa],
                        "kwargs": {k: _jsonable(v) for k, v in kk.items()},
                        "site": "%s:%s:%d" % (mod, func, line), "mod": mod, "func": func, "line": line})
            return _wrap(out, log)
        return _call

    def __eq__(self, other):
        return object.__getattribute__(self, "_o") == _unwrap(other)

    def __ne__(self, other):
        return object.__getattribute__(self, "_o") != _unwrap(other)

    def __hash__(self):
        return hash(object.__getattribute__(self, "_o"))

    def __lt__(self, other):
        return object.__getattribute__(self, "_o") < _unwrap(other)

    def __repr__(self):
        return repr(object.__getattribute__(self, "_o"))

    def __iter__(self):
        log = object.__getattribute__(self, "_log")
        return iter([_wrap(x, log) for x in object.__getattribute__(self, "_o")])

    def __len__(self):
        return len(object.__getattribute__(self, "_o"))

    def __getitem__(self, i):
        log = object.__getattribute__(self, "_log")
        return _wrap(object.__getattribute__(self, "_o")[i], log)


class RecordingShim:
    """Install recording proxies on nltk.corpus.{wordnet,verbnet,framenet,opinion_lexicon,stopwords}.

    The hdlab sites use FUNCTION-LEVEL `from nltk.corpus import wordnet as wn`, so patching the module
    attribute is picked up at call time; the module-LEVEL sites are covered because the shim installs before
    hdlab is imported. Read-only: every call is forwarded to the real corpus reader."""

    CORPORA = ("wordnet", "verbnet", "framenet", "opinion_lexicon", "stopwords")

    def __init__(self):
        self.log = []
        self._saved = {}

    def install(self):
        import nltk.corpus as NC
        for c in self.CORPORA:
            try:
                real = getattr(NC, c)
            except Exception:
                continue
            self._saved[c] = real
            setattr(NC, c, _Rec(real, self.log, c))
        return self

    def restore(self):
        import nltk.corpus as NC
        for c, real in self._saved.items():
            setattr(NC, c, real)
        self._saved = {}

    def reset(self):
        self.log.clear()


# ------------------------------------------------------------------ the default read (GUM, modern gold)
def _gum_docs(n):
    import experiments.gum_coref as G
    alldocs = G.load_docs(gum_only=True, decision_source="gold")
    test = alldocs[1::2]                      # the board's own split: TEST = odd doc index
    step = max(1, len(test) // max(1, n))
    return [test[i] for i in range(0, len(test), step)][:n]


def _prepare(docs, scratch):
    from experiments.exp_crosstype_gum_conll_fullread_v1 import gum_to_conll
    os.makedirs(scratch, exist_ok=True)
    out = []
    for d in docs:
        p = os.path.join(scratch, d.docid + ".conll")
        if not os.path.exists(p):
            gum_to_conll(d, p)
        out.append((d, p))
    return out


def _read(path, gaz):
    import hdlab.situation_reader as HSR
    reader = HSR.SituationReader(gaz=gaz)
    t0 = time.time()
    sm = reader.read(path)
    return sm, time.time() - t0


def _ser(x, depth=0):
    """Canonical, order-stable serialisation of whatever the reader produced -- the byte-identity unit."""
    import dataclasses
    if depth > 12:
        return "<deep>"
    if x is None or isinstance(x, (str, bool, int)):
        return x
    if isinstance(x, float):
        return repr(round(x, 10))
    if isinstance(x, (list, tuple)):
        return [_ser(v, depth + 1) for v in x]
    if isinstance(x, (set, frozenset)):
        return sorted(repr(_ser(v, depth + 1)) for v in x)
    if isinstance(x, dict):
        return {str(k): _ser(v, depth + 1) for k, v in sorted(x.items(), key=lambda kv: str(kv[0]))}
    if dataclasses.is_dataclass(x):
        return {f.name: _ser(getattr(x, f.name, None), depth + 1) for f in dataclasses.fields(x)}
    if callable(x):
        return "<callable:%s>" % type(x).__name__
    if hasattr(x, "__dict__"):
        return {"__type__": type(x).__name__,
                **{k: _ser(v, depth + 1) for k, v in sorted(vars(x).items()) if not k.startswith("_")}}
    return repr(x)


def sm_digest(sm):
    blob = json.dumps(_ser(sm), sort_keys=True, default=str)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest(), blob


# ------------------------------------------------------------------ record mode
def record(n_docs=4, verbose=True):
    os.makedirs(OUT_DIR, exist_ok=True)
    shim = RecordingShim().install()
    from experiments.exp_name_entity_clustering_v1 import load_given_gazetteer
    docs = _gum_docs(n_docs)
    prepared = _prepare(docs, os.path.join(OUT_DIR, "conll"))
    gaz = load_given_gazetteer()
    per_doc = []
    qpath = os.path.join(OUT_DIR, "queries.jsonl")
    seen = set()
    with open(qpath, "w", encoding="utf-8") as fh:
        for (d, p) in prepared:
            shim.reset()
            _sm, dt = _read(p, gaz)
            n = len(shim.log)
            for q in shim.log:
                k = json.dumps([q["corpus"], q["op"], q["recv"], q["args"], q["kwargs"]], sort_keys=True)
                if k in seen:
                    continue
                seen.add(k)
                fh.write(json.dumps(q, sort_keys=True) + "\n")
            per_doc.append({"doc": d.docid, "secs": round(dt, 1), "queries": n})
            if verbose:
                print("  %-28s %6.1fs  %8d nltk queries" % (d.docid, dt, n), flush=True)
    shim.restore()
    return per_doc, qpath


def summarise_queries(qpath):
    sites, ops, corpora, mods = Counter(), Counter(), Counter(), Counter()
    with open(qpath, encoding="utf-8") as fh:
        for line in fh:
            q = json.loads(line)
            sites[q["site"]] += 1
            ops["%s.%s" % (q["kind"], q["op"])] += 1
            corpora[q["corpus"]] += 1
            mods[q["mod"]] += 1
    return {"unique_queries": sum(sites.values()), "by_module": dict(mods.most_common()),
            "by_site": dict(sites.most_common()), "by_op": dict(ops.most_common()),
            "by_corpus": dict(corpora.most_common())}


# ------------------------------------------------------------------ rewire mode (the proposed hdlab change)
_CRLF = chr(13) + chr(10)
_LF = chr(10)
_IMPORT_RE = re.compile(r"^(\s*)from nltk\.corpus import ([A-Za-z_]+)((?: as [A-Za-z_]+)?)(.*)$")

# The three sites that are NOT a plain corpus read. Each is replaced by an explicit block; every replacement
# is byte-for-byte deterministic and printed by --rewire.
_SPECIAL = {
    "temporal_model.py": [(
        "_tagger = _perceptron_tagger   # multiframe's historical alias for the shared in-substrate tagger\n",
        "class _PennArmTagger:\n"
        "    \"\"\"(word, Penn-tag) pairs from the category organ's Penn arm, in the shape the punctuation-preserving\n"
        "    stream expects -- read GRADED for the ONE distinction this stream depends on.\n"
        "\n"
        "    WHY THE GRADED READ (pri 127, measured). Swapping the supervised stand-in for the organ's point\n"
        "    estimate costs the timeline EVENTS: on 40 GUM test documents the two taggers make the SAME number of\n"
        "    errors on gold VBD/VBN tokens (organ 276, stand-in 277) but not the same KIND -- the organ reads a\n"
        "    VBD as VBN 97 times (stand-in: 31), and `extract_events_punct` SKIPS a bare VBN that has no `had` /\n"
        "    COPULA_BE licenser in its 3-word lookback, so each of those is an event the timeline never sees\n"
        "    (event recall 0.7168 -> 0.6674, F1 0.8017 -> 0.7748, CI-separated). A past participle REQUIRES an\n"
        "    auxiliary licenser; an -ed form without one is a simple past. So when the argmax is VBN, the\n"
        "    EXTRACTOR'S OWN licensing condition fails, and the posterior still holds VBD, read VBD. Cue\n"
        "    competition over the organ's own graded posterior -- no new table, no new word list (the licensers\n"
        "    ARE `{had} | COPULA_BE`), and REL is a swept operating point chosen on the DEV half (even doc index):\n"
        "    TEST F1 0.8126 vs the point estimate's 0.7748 (+0.0378) and the supervised stand-in's 0.8017\n"
        "    (+0.0110, CI [-0.0036, +0.0269] -- at parity, no longer a CI-separated regression).\n"
        "    \"\"\"\n"
        "\n"
        "    LICENSERS = frozenset({\"had\"} | set(COPULA_BE))\n"
        "    REL = float(os.environ.get(\"HDLAB_PUNCT_VBN_REL\", \"0.05\"))   # swept on DEV; 0 disables the read\n"
        "\n"
        "    def tag(self, words):\n"
        "        ws = list(words)\n"
        "        if not ws:\n"
        "            return []\n"
        "        if self.REL <= 0:\n"
        "            return list(zip(ws, _penn_arm().tag(ws)))\n"
        "        tags, dist = _penn_arm().tag_with_posterior(ws)\n"
        "        lows = [w.lower() for w in ws]\n"
        "        out = []\n"
        "        for i, (t, d) in enumerate(zip(tags, dist)):\n"
        "            if t == \"VBN\" and not any(lows[j] in self.LICENSERS for j in range(max(0, i - 3), i)):\n"
        "                vbd, vbn = d.get(\"VBD\", 0.0), d.get(\"VBN\", 0.0)\n"
        "                if vbn > 0 and vbd >= self.REL * vbn:\n"
        "                    t = \"VBD\"\n"
        "            out.append(t)\n"
        "        return list(zip(ws, out))\n"
        "\n"
        "\n"
        "# THE PUNCTUATION-PRESERVING STREAM'S TAGGER (pri 127). Until 2026-09-15 this alias pointed STRAIGHT at the\n"
        "# NLTK PerceptronTagger, so the 2026-09-13 flip to the category organ's Penn arm reached `default_tagger`\n"
        "# and NOT the timeline register -- `situation_reader._read_timeline_register` -> `extract_passage` ->\n"
        "# `extract_events_punct` -> `tag_punct` -> `_tagger()` ran the supervised stand-in on EVERY default read\n"
        "# (measured: the poisoned-import witness crashes here at HEAD). It now honours the same switch, with its\n"
        "# own name so the OLD behaviour is exactly reproducible for a baseline.\n"
        "PUNCT_TAGGER = os.environ.get(\"HDLAB_TEMPORAL_PUNCT_TAGGER\", TEMPORAL_TAGGER)\n"
        "if PUNCT_TAGGER not in TEMPORAL_TAGGERS:\n"
        "    raise ValueError(\"unknown HDLAB_TEMPORAL_PUNCT_TAGGER %r (allowed: %s)\"\n"
        "                     % (PUNCT_TAGGER, sorted(TEMPORAL_TAGGERS)))\n"
        "_PENN_PUNCT_TAGGER = _PennArmTagger()\n"
        "\n"
        "\n"
        "def _tagger():\n"
        "    \"\"\"The shared tagger for the punctuation-preserving stream; the organ's Penn arm by default.\"\"\"\n"
        "    return _PENN_PUNCT_TAGGER if PUNCT_TAGGER == \"counts_penn\" else _perceptron_tagger()\n"),
        (
        "        from nltk.tag import PerceptronTagger\n",
        "        from hdlab.lexicon_foundation import standin_nltk\n"
        "        PerceptronTagger = standin_nltk(\"nltk.tag\", \"PerceptronTagger\",   # OFF the live path:\n"
        "                                        reason=\"supervised stand-in; the live tagger is the category organ's Penn arm\")\n")],
    "morphology_leakage.py": [(
        "try:                                                    # optional; the prefix/substring rules below\n"
        "    from nltk.stem import PorterStemmer                 # carry the test on their own without it\n"
        "    _STEMMER = PorterStemmer()\n"
        "except Exception:                                       # noqa: BLE001\n"
        "    _STEMMER = None\n",
        "# THE STEM CLAUSE IS THE SUBSTRATE'S OWN MORPHOLOGY ORGAN (pri 127). Porter is an outside tool and it is\n"
        "# OFF by default; hdlab.morphology is the glass-box decomposition organ (exception store + detachment\n"
        "# rules + lexical check) this project already landed. MEASURED cost of the swap on WordNet vocabulary:\n"
        "# 0 of 200,000 random lemma pairs change verdict (the four surrounding rules already cover them), and\n"
        "# 2 of 80 pairs constructed to share a Porter stem lose the catch (adz/adze, nogging/nog -- not the\n"
        "# run/running class this helper exists for). Porter stays reachable via HDLAB_ALLOW_NLTK_STANDIN=1.\n"
        "_STEMMER = None\n"
        "try:\n"
        "    from hdlab.morphology import morphy as _organ_lemma\n"
        "except Exception:                                       # noqa: BLE001\n"
        "    _organ_lemma = None\n"
        "if os.environ.get(\"HDLAB_ALLOW_NLTK_STANDIN\", \"0\") == \"1\":   # deliberate baseline only\n"
        "    try:\n"
        "        from hdlab.lexicon_foundation import standin_nltk\n"
        "        _STEMMER = standin_nltk(\"nltk.stem\", \"PorterStemmer\", reason=\"leakage-strip baseline\")()\n"
        "    except Exception:                                   # noqa: BLE001\n"
        "        _STEMMER = None\n"),
        (
        "    if _STEMMER is not None and _STEMMER.stem(a) == _STEMMER.stem(b):\n"
        "        return True\n",
        "    if _STEMMER is not None and _STEMMER.stem(a) == _STEMMER.stem(b):\n"
        "        return True\n"
        "    if _organ_lemma is not None:                        # the organ's lemma, both sides non-None\n"
        "        la, lb = _organ_lemma(a), _organ_lemma(b)\n"
        "        if la and lb and la == lb:\n"
        "            return True\n")],
    "grounded_semantic_graph.py": [(
        "class GroundedSemanticGraph:\n",
        "# THE SEMANTIC GRAPH IS A STATIC STRUCTURE; BUILDING IT IS DEVELOPMENT, NOT READING (pri 127). Rebuilding\n"
        "# it at read time walked every relation of all 117,659 synsets through the library on the FIRST document\n"
        "# of every process (measured: 1,988,867 of the read's 2,006,404 unique library queries came from this\n"
        "# module). The edge list is now frozen once offline (data/frontend_assets/lexicon_foundation_graph_v1.npz,\n"
        "# 1,025,488 edges, 3.3 MB) and LOADED -- the identical matrix, checked by CSR bytes in the witness.\n"
        "# HDLAB_GSG_FROZEN=0 rebuilds from the lexicon organ instead (the baseline arm). A MISSING asset RAISES:\n"
        "# a silent rebuild is the degradation this problem exists to remove.\n"
        "FROZEN_GRAPH = os.environ.get(\"HDLAB_GSG_FROZEN\", \"1\") == \"1\"\n"
        "\n"
        "\n"
        "class GroundedSemanticGraph:\n"),
        (
        "    def build(self):\n"
        "        syns = _synsets_ordered()\n"
        "        self.syn2idx = {s.name(): i for i, s in enumerate(syns)}\n"
        "        rows, cols = [], []\n"
        "        for src in self.sources:\n"
        "            r, c = _SOURCE_EDGES[src](syns, self.syn2idx)\n"
        "            rows = rows + list(r); cols = cols + list(c)\n"
        "        self._base_rows, self._base_cols = rows, cols\n"
        "        self._rebuild()\n"
        "        return self\n",
        "    def build(self):\n"
        "        \"\"\"LOAD the frozen edge list (default) or rebuild it from the lexicon store (HDLAB_GSG_FROZEN=0).\n"
        "        Same node order (synsets sorted by name), same per-source edge concatenation order, so the\n"
        "        row-stochastic matrix is identical -- the witness compares its CSR bytes.\"\"\"\n"
        "        if FROZEN_GRAPH:\n"
        "            from hdlab.lexicon_foundation import graph_edges\n"
        "            names, rows, cols = graph_edges(self.sources)\n"
        "            self.syn2idx = {n: i for i, n in enumerate(names)}\n"
        "            self._base_rows, self._base_cols = rows, cols\n"
        "            self._rebuild()\n"
        "            return self\n"
        "        syns = _synsets_ordered()\n"
        "        self.syn2idx = {s.name(): i for i, s in enumerate(syns)}\n"
        "        rows, cols = [], []\n"
        "        for src in self.sources:\n"
        "            r, c = _SOURCE_EDGES[src](syns, self.syn2idx)\n"
        "            rows = rows + list(r); cols = cols + list(c)\n"
        "        self._base_rows, self._base_cols = rows, cols\n"
        "        self._rebuild()\n"
        "        return self\n")],
    "quality_relation.py": [(
        "    from nltk.corpus import wordnet as wn_mod\n"
        "    try:\n"
        "        wn_mod.synsets(\"test\")\n"
        "    except LookupError:\n"
        "        import nltk\n"
        "        nltk.download(\"wordnet\", quiet=True)\n"
        "        nltk.download(\"omw-1.4\", quiet=True)\n"
        "    _wn = wn_mod\n",
        "    from hdlab.lexicon_foundation import wordnet as wn_mod   # frozen offline store: no download path,\n"
        "    _wn = wn_mod                                            # and a missing asset raises, never degrades\n")],
}


def rewire(verbose=True):
    """Build the PATCHED hdlab tree: every nltk import site routed to the frozen organ. Rule-based and
    printed. Returns (changed_files, n_lines, report)."""
    src = os.path.join(_REPO, "hdlab")
    dst = os.path.join(PATCHED, "hdlab")
    if os.path.exists(PATCHED):
        shutil.rmtree(PATCHED)
    shutil.copytree(src, dst, ignore=shutil.ignore_patterns("__pycache__"))
    shutil.copy2(os.path.join(_REPO, "pyproject.toml"), os.path.join(PATCHED, "pyproject.toml"))
    report, changed = [], {}
    for fn in sorted(os.listdir(dst)):
        if not fn.endswith(".py"):
            continue
        p = os.path.join(dst, fn)
        with open(p, "rb") as fh:
            raw = fh.read()
        crlf = _CRLF.encode("ascii") in raw    # keep the file's own line endings (else the diff is whole-file)
        text = raw.decode("utf-8").replace(_CRLF, _LF)
        orig = text
        for old, new in _SPECIAL.get(fn, []):
            if old not in text:
                raise RuntimeError("special-case block not found verbatim in %s" % fn)
            text = text.replace(old, new, 1)
        out_lines = []
        for line in text.split("\n"):
            m = _IMPORT_RE.match(line)
            if m and "hdlab.lexicon_foundation" not in line:
                indent, corpus, alias, tail = m.groups()
                new = "%sfrom hdlab.lexicon_foundation import %s%s%s" % (indent, corpus, alias, tail)
                report.append({"file": fn, "old": line.strip(), "new": new.strip()})
                out_lines.append(new)
            else:
                out_lines.append(line)
        text = "\n".join(out_lines)
        if text != orig:
            out = text.replace(_LF, _CRLF) if crlf else text
            with open(p, "wb") as fh:
                fh.write(out.encode("utf-8"))
            changed[fn] = changed.get(fn, 0) + 1
    # pyproject: nltk is a BUILD-time dependency only
    pp = os.path.join(PATCHED, "pyproject.toml")
    with open(pp, encoding="utf-8") as fh:
        t = fh.read()
    add = ('[project.optional-dependencies]\n'
           '# BUILD-TIME ONLY (pri 127): nltk is needed to BUILD the frozen lexicon asset\n'
           '# (tools/build_lexicon_foundation_index.py), never to read. The runtime dependency list above must\n'
           '# NOT contain it -- verification/test_no_nltk_on_the_live_path.py fails if hdlab/ imports it.\n'
           'foundation-build = [\n'
           '    "nltk>=3.9",\n'
           ']\n')
    t = t.replace("[project.optional-dependencies]\n", add, 1)
    with open(pp, "w", encoding="utf-8", newline="") as fh:
        fh.write(t)
    if verbose:
        for r in report:
            print("  %-34s %s  ->  %s" % (r["file"], r["old"], r["new"]))
        print("rewired: %d import lines in %d files + %d special blocks + pyproject"
              % (len(report), len(changed), sum(len(v) for v in _SPECIAL.values())))
    return changed, len(report), report


def emit_diff(verbose=True):
    """Unified diff of the patched tree against HEAD's files, with b/ paths rewritten to the repo layout so
    `git apply` lands it."""
    files = ["hdlab/" + f for f in sorted(os.listdir(os.path.join(PATCHED, "hdlab"))) if f.endswith(".py")]
    files.append("pyproject.toml")
    chunks = []
    for rel in files:
        a = os.path.join(_REPO, rel)
        b = os.path.join(PATCHED, rel)
        if not os.path.exists(b):
            continue
        # BYTES, not text=True: universal-newline decoding would strip the CR from the context lines of
        # a CRLF file and the resulting patch would not apply (13 of the 36 files here are CRLF).
        r = subprocess.run(["git", "diff", "--no-index", "--no-color", "--", a, b],
                           capture_output=True, cwd=_REPO)
        raw = r.stdout.decode("utf-8")
        if not raw.strip():
            continue
        out = []
        for line in raw.split(_LF):
            if line.startswith("diff --git "):
                out.append("diff --git a/%s b/%s" % (rel, rel))
            elif line.startswith("--- "):
                out.append("--- a/%s" % rel)
            elif line.startswith("+++ "):
                out.append("+++ b/%s" % rel)
            elif line.startswith("index "):
                continue
            else:
                out.append(line)
        chunks.append(_LF.join(out).rstrip(_LF))
    diff = _LF.join(chunks) + _LF
    os.makedirs(os.path.dirname(DIFF_PATH), exist_ok=True)
    with open(DIFF_PATH, "wb") as fh:
        fh.write(diff.encode("utf-8"))
    if verbose:
        print("diff: %d files, %d lines -> %s" % (len(chunks), diff.count("\n"), DIFF_PATH))
    return DIFF_PATH, len(chunks)


# ------------------------------------------------------------------ parity mode
def _deser(x, impl):
    if isinstance(x, dict):
        if "__synset__" in x:
            return impl.synset(x["__synset__"])
        if "__lemma__" in x:
            return _lemma_of(x["__lemma__"], impl)
        if "__repr__" in x:
            raise ValueError("unreplayable arg %s" % x["__repr__"])
        return {k: _deser(v, impl) for k, v in x.items()}
    if isinstance(x, list):
        return [_deser(v, impl) for v in x]
    return x


def _lemma_of(recv, impl):
    sname, lname = recv.split("::", 1)
    for lm in impl.synset(sname).lemmas():
        if lm.name() == lname:
            return lm
    raise ValueError("no lemma %s" % recv)


def _canon(x, depth=0):
    if depth > 8:
        return "<deep>"
    cn = type(x).__name__
    if cn == "Synset":
        return "S:" + x.name()
    if cn == "Lemma":
        return "L:" + x.key()
    if isinstance(x, (list, tuple)):
        return [_canon(v, depth + 1) for v in x]
    if isinstance(x, _types.GeneratorType):
        return [_canon(v, depth + 1) for v in x]
    if isinstance(x, dict):
        return {str(k): _canon(v, depth + 1) for k, v in sorted(x.items(), key=lambda kv: str(kv[0]))}
    if isinstance(x, (str, int, bool)) or x is None:
        return x
    if isinstance(x, float):
        return repr(round(x, 10))
    return repr(x)


def _receiver(q, impl_wn):
    if q["kind"] == "Synset":
        return impl_wn.synset(q["recv"])
    if q["kind"] == "Lemma":
        return _lemma_of(q["recv"], impl_wn)
    return None


def parity(qpath=None, limit=None, verbose=True):
    """Replay every logged query against BOTH implementations and compare canonical answers."""
    qpath = qpath or os.path.join(OUT_DIR, "queries.jsonl")
    import nltk.corpus as NC
    from hdlab import lexicon_foundation as LF
    ORGAN = {"wordnet": LF.wordnet, "verbnet": LF.verbnet, "framenet": LF.framenet,
             "opinion_lexicon": LF.opinion_lexicon, "stopwords": LF.stopwords}
    NLTK = {c: getattr(NC, c) for c in ORGAN}
    n = ok = skipped = 0
    diffs = []
    by_op_fail = Counter()
    t0 = time.time()
    with open(qpath, encoding="utf-8") as fh:
        for line in fh:
            q = json.loads(line)
            if limit and n >= limit:
                break
            n += 1
            try:
                ra = _run_one(q, ORGAN["wordnet"], ORGAN)
            except Exception as e:
                ra = ("ERR", type(e).__name__, str(e)[:60])
            try:
                rb = _run_one(q, NLTK["wordnet"], NLTK)
            except Exception as e:
                rb = ("ERR", type(e).__name__, str(e)[:60])
            if ra == ("SKIP",) or rb == ("SKIP",):
                skipped += 1
                continue
            if ra == rb:
                ok += 1
            else:
                by_op_fail["%s.%s" % (q["kind"], q["op"])] += 1
                if len(diffs) < 60:
                    diffs.append({"q": {k: q[k] for k in ("kind", "op", "recv", "args", "site")},
                                  "organ": ra if not isinstance(ra, list) else ra[:8],
                                  "nltk": rb if not isinstance(rb, list) else rb[:8]})
            if verbose and n % 200000 == 0:
                print("  parity %d/%s replayed, %d equal, %d differ (%.0fs)"
                      % (n, "?", ok, n - ok - skipped, time.time() - t0), flush=True)
    res = {"replayed": n, "equal": ok, "differ": n - ok - skipped, "skipped": skipped,
           "fail_by_op": dict(by_op_fail.most_common()), "examples": diffs,
           "elapsed_s": round(time.time() - t0, 1)}
    if verbose:
        print("PARITY: %d replayed, %d equal, %d differ, %d unreplayable (%.0fs)"
              % (n, ok, res["differ"], skipped, res["elapsed_s"]))
    return res


def _run_one(q, wn_impl, impls):
    obj = _receiver(q, wn_impl) if q["kind"] in _SS_TYPES else impls.get(q["kind"])
    if obj is None:
        return ("SKIP",)
    try:
        args = [_deser(a, wn_impl) for a in q["args"]]
        kwargs = {k: _deser(v, wn_impl) for k, v in q["kwargs"].items()}
    except ValueError:
        return ("SKIP",)
    fn = getattr(obj, q["op"], None)
    if fn is None:
        return ("MISSING_OP",)
    return _canon(fn(*args, **kwargs))


# ------------------------------------------------------------------ identity mode (poisoned subprocess)
_RUNNER = r'''
import json, os, sys, time
REPO = %(repo)r
PATCHED = %(patched)r
POISON = %(poison)r
TAG = %(tag)r
sys.path.insert(0, REPO) if REPO not in sys.path else None
if PATCHED:
    # LOAD THE PATCHED SOURCE UNDER THE ORIGINAL FILENAME. A copied tree on sys.path would move every
    # module's `__file__`, and hdlab modules derive their ASSET paths from it (_REPO = dirname(dirname(
    # __file__))) -- the copy would look for data/frontend_assets inside the copy. This finder feeds the
    # patched BYTES to a loader whose path is the REAL file, so asset resolution is untouched and the only
    # difference between the two runs is the patch itself. (No junction/symlink: a scratch-tree junction
    # into data/ deleted real lexicons on 2026-09-13.)
    import importlib.util
    from importlib.machinery import SourceFileLoader

    def _patched_path(path):
        rel = os.path.relpath(path, REPO)
        pp = os.path.join(PATCHED, rel)
        return pp if os.path.exists(pp) else path

    class _PatchedLoader(SourceFileLoader):
        def get_data(self, path):
            with open(_patched_path(path), "rb") as fh:
                return fh.read()

        def get_code(self, fullname):            # always compile from source: never a stale __pycache__
            return compile(self.get_data(self.path), self.path, "exec")

    class _PatchedFinder:
        def find_spec(self, name, path=None, target=None):
            if name != "hdlab" and not name.startswith("hdlab."):
                return None
            base = os.path.join(REPO, *name.split("."))
            if os.path.isdir(base):
                init = os.path.join(base, "__init__.py")
                return importlib.util.spec_from_file_location(
                    name, init, loader=_PatchedLoader(name, init), submodule_search_locations=[base])
            fp = base + ".py"
            if not os.path.exists(fp):
                return None
            return importlib.util.spec_from_file_location(name, fp, loader=_PatchedLoader(name, fp))

    sys.dont_write_bytecode = True
    sys.meta_path.insert(0, _PatchedFinder())
if POISON:
    class _Poison:
        def find_module(self, name, path=None):
            return self.find_spec(name, path)
        def find_spec(self, name, path=None, target=None):
            if name == "nltk" or name.startswith("nltk."):
                raise ImportError("POISONED: %%s must not be imported on the live read path" %% name)
            return None
    sys.meta_path.insert(0, _Poison())
sys.path.insert(0, os.path.join(REPO, "experiments"))
sys.argv = [sys.argv[0]]
import importlib
E = importlib.import_module("experiments.exp_lexicon_foundation_parity_v1")
import hdlab.situation_reader as HSR
print("HDLAB FROM:", HSR.__file__, "loader:", type(HSR.__loader__).__name__, flush=True)
from experiments.exp_name_entity_clustering_v1 import load_given_gazetteer
gaz = load_given_gazetteer()
out = []
for p in %(paths)r:
    r = HSR.SituationReader(gaz=gaz)
    t0 = time.time()
    sm = r.read(p)
    dt = time.time() - t0
    dig, blob = E.sm_digest(sm)
    if os.environ.get("HDLAB_DUMP_BLOB"):
        bp = os.path.join(os.environ["HDLAB_DUMP_BLOB"], "blob_%%s_%%s.json" %% (TAG, os.path.basename(p)))
        open(bp, "w", encoding="utf-8").write(blob)
    out.append({"path": os.path.basename(p), "digest": dig, "secs": round(dt, 2), "chars": len(blob)})
    print("READ %%s -> %%s (%%.1fs)" %% (os.path.basename(p), dig[:16], dt), flush=True)
print("ORGAN IN USE: %%s | nltk imported: %%s | lexicon reads: %%s"
      %% ("hdlab.lexicon_foundation" in sys.modules, "nltk" in sys.modules,
          sys.modules["hdlab.lexicon_foundation"].observe() if "hdlab.lexicon_foundation" in sys.modules else 0),
      flush=True)
print("RESULT " + json.dumps(out))
'''


def _run_subprocess(paths, patched=None, poison=False, tag="", timeout=5400, env_extra=None):
    script = os.path.join(OUT_DIR, "runner_%s.py" % (tag or "x"))
    with open(script, "w", encoding="utf-8") as fh:
        fh.write(_RUNNER % {"repo": _REPO, "patched": patched or "", "poison": bool(poison),
                            "paths": list(paths), "tag": tag or "x"})
    env = dict(os.environ)
    env.update({"OMP_NUM_THREADS": "2", "OPENBLAS_NUM_THREADS": "2", "MKL_NUM_THREADS": "2",
                "PYTHONHASHSEED": "0", "HDLAB_EXP_NAME": ANCHOR})
    env.update(env_extra or {})
    t0 = time.time()
    r = subprocess.run([sys.executable, script], capture_output=True, text=True, encoding="utf-8",
                       errors="replace", cwd=_REPO, env=env, timeout=timeout)
    tail = (r.stdout or "")[-4000:] + "\n" + (r.stderr or "")[-4000:]
    res = None
    for line in (r.stdout or "").split("\n"):
        if line.startswith("RESULT "):
            res = json.loads(line[len("RESULT "):])
    return {"tag": tag, "rc": r.returncode, "result": res, "secs": round(time.time() - t0, 1), "tail": tail}


def dimension_diff(paths, tag_a, tag_b):
    """WHICH dimension of the situation model the stand-in retirement moved, and by how much. A digest that
    differs is not a result; the COUNT per dimension is."""
    out = {}
    for p in paths:
        base = os.path.basename(p)
        fa = os.path.join(OUT_DIR, "blob_%s_%s.json" % (tag_a, base))
        fb = os.path.join(OUT_DIR, "blob_%s_%s.json" % (tag_b, base))
        if not (os.path.exists(fa) and os.path.exists(fb)):
            continue
        A = json.load(open(fa, encoding="utf-8"))
        B = json.load(open(fb, encoding="utf-8"))
        per = {}
        for k in sorted(set(A) | set(B)):
            va, vb = A.get(k), B.get(k)
            if va == vb:
                continue
            per[k] = {"a_n": len(va) if isinstance(va, (list, dict)) else None,
                      "b_n": len(vb) if isinstance(vb, (list, dict)) else None}
            if isinstance(va, list) and isinstance(vb, list):
                sa = {json.dumps(x, sort_keys=True) for x in va}
                sb = {json.dumps(x, sort_keys=True) for x in vb}
                per[k]["only_a"] = len(sa - sb)
                per[k]["only_b"] = len(sb - sa)
                per[k]["shared"] = len(sa & sb)
        out[base] = per
    return out


def identity(n_docs=4, verbose=True):
    """FOUR arms, because the change has two separable halves and only one of them CAN be byte-identical:

      shipped           the tree as it ships (its punctuation-preserving tag stream runs the NLTK perceptron)
      freeze_only       the patched tree with HDLAB_TEMPORAL_PUNCT_TAGGER=perceptron -- i.e. ONLY the lexicon
                        freeze, the stand-in left exactly where it was. MUST equal `shipped` byte for byte:
                        this is the freeze's own can-fail bar.
      patched_poisoned  the patched tree with the defaults (the organ's Penn arm) and EVERY nltk import
                        POISONED. Proves no library call survives; its digest is EXPECTED to differ from
                        `shipped`, because retiring a supervised tagger from the read is a real change, and
                        the difference is quantified rather than hidden.
      control           the SHIPPED tree under the same poison -- it must CRASH, or the poison is not biting.
    """
    docs = _gum_docs(n_docs)
    prepared = _prepare(docs, os.path.join(OUT_DIR, "conll"))
    paths = [p for (_d, p) in prepared]
    dump = {"HDLAB_DUMP_BLOB": OUT_DIR}
    a = _run_subprocess(paths, patched=None, poison=False, tag="shipped", env_extra=dump)
    f = _run_subprocess(paths, patched=PATCHED, poison=False, tag="freeze_only",
                        env_extra=dict(dump, HDLAB_TEMPORAL_PUNCT_TAGGER="perceptron",
                                       HDLAB_ALLOW_NLTK_STANDIN="1"))
    b = _run_subprocess(paths, patched=PATCHED, poison=True, tag="patched_poisoned",
                        env_extra=dump)
    c = _run_subprocess(paths[:1], patched=None, poison=True, tag="shipped_poisoned")

    def digs(x):
        return [y["digest"] for y in (x["result"] or [])] or None
    freeze_same = digs(a) is not None and digs(a) == digs(f)
    full_same = digs(a) is not None and digs(a) == digs(b)
    res = {"shipped": a, "freeze_only": f, "patched_poisoned": b, "shipped_poisoned_control": c,
           "freeze_byte_identical": bool(freeze_same), "full_byte_identical": bool(full_same),
           "poisoned_completed": b["rc"] == 0 and digs(b) is not None,
           "control_crashed": c["rc"] != 0 or digs(c) is None,
           "standin_retirement_effect": dimension_diff(paths, "shipped", "patched_poisoned")}
    if verbose:
        print("IDENTITY  shipped rc=%s %ss | freeze_only rc=%s %ss (byte-identical: %s) | "
              "patched+poisoned rc=%s %ss (completed: %s, digest equal: %s)"
              % (a["rc"], a["secs"], f["rc"], f["secs"], freeze_same,
                 b["rc"], b["secs"], res["poisoned_completed"], full_same))
        print("CONTROL   shipped under poison: rc=%s %s"
              % (c["rc"], "CRASHED as required" if res["control_crashed"] else "DID NOT CRASH -- poison inert"))
        if not freeze_same:
            print(f["tail"][-2500:])
        if not res["poisoned_completed"]:
            print(b["tail"][-2500:])
    return res


# ------------------------------------------------------------------ the retired stand-in, measured
_WORDTOK = re.compile(r"[A-Za-z]+(?:'[A-Za-z]+)?$")


def tagger_arm(n_docs=None, nboot=2000, verbose=True):
    """IS THE RETIREMENT AN IMPROVEMENT? The punctuation-preserving tag stream (`temporal_model.tag_punct`)
    fed the timeline register the NLTK perceptron's tags on every default read. Score BOTH arms -- the
    perceptron stand-in and the category organ's Penn arm -- on the same word tokens against GUM's own gold
    Penn tags (xpos), doc-paired bootstrap. Population: the word tokens tag_punct actually tags (its own
    word regex), GUM TEST split. Floor for the organ arm = the stand-in it replaces."""
    import numpy as np
    import experiments.gum_coref as G
    from nltk.tag import PerceptronTagger
    from hdlab import lexical_categories as LC
    docs = G.load_docs(gum_only=True, decision_source="gold")[1::2]
    if n_docs:
        docs = docs[:n_docs]
    penn = LC.LexicalCategories.load(LC.ASSET_PENN)
    perc = PerceptronTagger()
    per_doc = []
    for d in docs:
        sents = {}
        for t in d.toks:
            sents.setdefault(t.sent, []).append(t)
        n = ok_p = ok_o = 0
        vn = vok_p = vok_o = 0
        for si in sorted(sents):
            toks = [t for t in sents[si] if _WORDTOK.match(t.form or "") and t.xpos]
            if not toks:
                continue
            words = [t.form for t in toks]
            gold = [t.xpos for t in toks]
            tp = [x[1] for x in perc.tag(words)]
            to = list(penn.tag(list(words)))
            for g, a, b in zip(gold, tp, to):
                n += 1
                ok_p += int(a == g)
                ok_o += int(b == g)
                if g.startswith("VB"):
                    vn += 1
                    vok_p += int(a == g)
                    vok_o += int(b == g)
        if n:
            per_doc.append({"doc": d.docid, "n": n, "perceptron": ok_p / n, "organ": ok_o / n,
                            "vn": vn, "v_perceptron": (vok_p / vn) if vn else None,
                            "v_organ": (vok_o / vn) if vn else None})
    rng = np.random.default_rng(SEED)
    idx = np.arange(len(per_doc))

    def pooled(rows, key, nkey="n"):
        num = sum(r[key] * r[nkey] for r in rows if r[key] is not None)
        den = sum(r[nkey] for r in rows if r[key] is not None)
        return num / den if den else float("nan")

    def boot(key_a, key_b, nkey):
        obs = pooled(per_doc, key_b, nkey) - pooled(per_doc, key_a, nkey)
        ds = np.empty(nboot)
        for i in range(nboot):
            take = [per_doc[j] for j in rng.choice(idx, size=len(idx), replace=True)]
            ds[i] = pooled(take, key_b, nkey) - pooled(take, key_a, nkey)
        lo, hi = np.percentile(ds, [2.5, 97.5])
        return {"obs": round(float(obs), 4), "ci": [round(float(lo), 4), round(float(hi), 4)],
                "ci_separated": bool(lo > 0 or hi < 0)}

    res = {"docs": len(per_doc), "tokens": sum(r["n"] for r in per_doc),
           "verb_tokens": sum(r["vn"] for r in per_doc),
           "all_perceptron": round(pooled(per_doc, "perceptron"), 4),
           "all_organ": round(pooled(per_doc, "organ"), 4),
           "verb_perceptron": round(pooled(per_doc, "v_perceptron", "vn"), 4),
           "verb_organ": round(pooled(per_doc, "v_organ", "vn"), 4),
           "delta_all": boot("perceptron", "organ", "n"),
           "delta_verbforms": boot("v_perceptron", "v_organ", "vn"),
           "per_doc": per_doc}
    if verbose:
        print("TAGGER ARM (GUM test, %d docs, %d word tokens): all-tag organ %.4f vs stand-in %.4f "
              "(delta %+.4f, CI %s, separated %s)"
              % (res["docs"], res["tokens"], res["all_organ"], res["all_perceptron"],
                 res["delta_all"]["obs"], res["delta_all"]["ci"], res["delta_all"]["ci_separated"]))
        print("           verb forms (%d tokens): organ %.4f vs stand-in %.4f (delta %+.4f, CI %s, separated %s)"
              % (res["verb_tokens"], res["verb_organ"], res["verb_perceptron"],
                 res["delta_verbforms"]["obs"], res["delta_verbforms"]["ci"],
                 res["delta_verbforms"]["ci_separated"]))
    return res


def event_arm(n_docs=40, nboot=2000, verbose=True, split="test"):
    """THE CONSEQUENCE, not the tag. The timeline register consumes `extract_events_punct`, so score THAT:
    every event the punctuation-preserving stream extracts, against GUM gold Penn tags, for both arms.
    An event is CORRECT when the token it names carries the gold tag its tense claims
    (SIMPLE_PAST -> VBD; PAST_PERFECT / PASSIVE -> VBN). RECALL is over the gold VBD/VBN content-verb
    tokens of the same sentences. Sentences whose word stream does not re-tokenise identically are dropped
    and counted (no silent misalignment)."""
    import numpy as np
    import experiments.gum_coref as G
    from hdlab import temporal_model as M
    alldocs = G.load_docs(gum_only=True, decision_source="gold")
    # THE OPERATING POINT IS SWEPT ON DEV, REPORTED ON TEST. The board's own split: TEST = odd doc
    # index, DEV = even. Choosing `rel` on the same documents it is scored on would be selection on
    # the evaluation set.
    docs = (alldocs[1::2] if split == "test" else alldocs[0::2])[:n_docs]
    rows = []
    stats = {"dropped": 0, "kept": 0}

    class _PennAdapter:
        def tag(self, words):
            ws = list(words)
            return list(zip(ws, M._penn_arm().tag(ws))) if ws else []

    class _GradedAdapter:
        """THE GRADED HAND-OFF (pri 127 quality push). The category organ hands DOWN a posterior; the timeline
        consumer was reading a POINT estimate, so every token whose argmax fell just outside the verb-forms was
        an event the timeline never saw (measured: recall 0.7168 -> 0.6674 when the supervised stand-in was
        retired). This reads the posterior for the distinction the consumer actually needs -- is this token a
        past/participial verb form? -- and accepts VBD/VBN when their summed mass clears tau, which is a SWEPT
        operating point, not an adopted number."""

        def __init__(self, tau):
            self.tau = float(tau)

        def tag(self, words):
            ws = list(words)
            if not ws:
                return []
            tags, dist = M._penn_arm().tag_with_posterior(ws)
            out = []
            for t, d in zip(tags, dist):
                if not t.startswith("VB"):
                    vbd, vbn = d.get("VBD", 0.0), d.get("VBN", 0.0)
                    if vbd + vbn >= self.tau:
                        t = "VBD" if vbd >= vbn else "VBN"
                out.append(t)
            return list(zip(ws, out))

    class _AuxLicensedAdapter:
        """THE REPAIR THE MEASUREMENT POINTED AT (pri 127 quality push, second lever). The recall the timeline
        lost when the supervised stand-in was retired is NOT missing verb evidence: on gold VBD/VBN tokens the
        two taggers make the same number of errors (organ 276, stand-in 277 over 40 GUM test docs). It is the
        DIRECTION of the confusion -- the organ reads VBD as VBN 97 times (stand-in: 31), and the extractor
        SKIPS a bare VBN with no had/be auxiliary, so each of those is an event that never reaches the
        timeline. A past participle REQUIRES an auxiliary licenser; an -ed form with none is a simple past.
        So: when the argmax is VBN, no licenser stands within the extractor's own lookback, and VBD holds at
        least `rel` of VBN's posterior mass, read VBD. Cue competition over the organ's graded posterior --
        no new knowledge, no fitted table; `rel` is a swept operating point."""

        # THE LICENSER SET IS THE EXTRACTOR'S OWN, not a new word list: `extract_events_punct` licenses a VBN
        # by "had" (perfect) or a COPULA_BE (passive) within its own 3-word lookback. The rule is therefore
        # exactly "if the extractor would DROP this token as an unlicensed bare participle, and the organ's
        # posterior still holds VBD, read the simple past it almost certainly is".
        LIC = frozenset({"had"} | set(M.COPULA_BE))

        def __init__(self, rel):
            self.rel = float(rel)

        def tag(self, words):
            ws = list(words)
            if not ws:
                return []
            tags, dist = M._penn_arm().tag_with_posterior(ws)
            lows = [w.lower() for w in ws]
            out = []
            for i, (t, d) in enumerate(zip(tags, dist)):
                if t == "VBN":
                    lic = any(lows[j] in self.LIC for j in range(max(0, i - 3), i))
                    vbd, vbn = d.get("VBD", 0.0), d.get("VBN", 0.0)
                    if not lic and vbn > 0 and vbd >= self.rel * vbn:
                        t = "VBD"
                out.append(t)
            return list(zip(ws, out))

    ARMS = {"perceptron": M._perceptron_tagger, "counts_penn": (lambda _a=_PennAdapter(): _a)}
    for rel in (0.05, 0.15, 0.30, 0.60):
        ARMS["auxlic_%0.2f" % rel] = (lambda _a=_AuxLicensedAdapter(rel): _a)
    for tau in (0.15, 0.25, 0.35, 0.50):
        ARMS["graded_%0.2f" % tau] = (lambda _a=_GradedAdapter(tau): _a)
    ARM_NAMES = tuple(ARMS)
    for d in docs:
        sents = {}
        for t in d.toks:
            sents.setdefault(t.sent, []).append(t)
        per = {"doc": d.docid}
        for arm in ARM_NAMES:
            M._tagger = ARMS[arm]
            tp = fp = fn_ = 0
            for si in sorted(sents):
                toks = sents[si]
                text = " ".join(t.form for t in toks)
                gold_words = [t for t in toks if _WORDTOK.match(t.form or "")]
                tagged = M.tag_punct(text)
                stream_words = [i for i, x in enumerate(tagged) if x[2] != M._PUNC_POS]
                if len(stream_words) != len(gold_words) or any(
                        tagged[i][0] != g.form for i, g in zip(stream_words, gold_words)):
                    stats["dropped"] += 1
                    continue
                stats["kept"] += 1
                pos_of_word = {i: g for i, g in zip(stream_words, gold_words)}
                ev, _tg = M.extract_events_punct(text)
                want = {"SIMPLE_PAST": ("VBD",), "PAST_PERFECT": ("VBN",), "PASSIVE": ("VBN",)}
                got_idx = set()
                for e in ev:
                    g = pos_of_word.get(e.idx)
                    if g is None:
                        fp += 1
                        continue
                    got_idx.add(g.gidx)
                    if g.xpos in want.get(e.tense, ()):
                        tp += 1
                    else:
                        fp += 1
                for g in gold_words:
                    if g.xpos in ("VBD", "VBN") and (g.lemma or "").lower() not in M.AUX_LEMMAS \
                            and g.gidx not in got_idx:
                        fn_ += 1
            per[arm] = {"tp": tp, "fp": fp, "fn": fn_}
        rows.append(per)
    M._tagger = M._perceptron_tagger          # restore the module's shipped alias

    def prf(rows, arm):
        tp = sum(r[arm]["tp"] for r in rows); fp = sum(r[arm]["fp"] for r in rows)
        fn_ = sum(r[arm]["fn"] for r in rows)
        p = tp / (tp + fp) if tp + fp else 0.0
        r = tp / (tp + fn_) if tp + fn_ else 0.0
        return p, r, (2 * p * r / (p + r) if p + r else 0.0)

    rng = np.random.default_rng(SEED)
    idx = np.arange(len(rows))

    def delta(arm_a, arm_b):
        obs = prf(rows, arm_b)[2] - prf(rows, arm_a)[2]
        ds = np.empty(nboot)
        for i in range(nboot):
            take = [rows[j] for j in rng.choice(idx, size=len(idx), replace=True)]
            ds[i] = prf(take, arm_b)[2] - prf(take, arm_a)[2]
        lo, hi = np.percentile(ds, [2.5, 97.5])
        return {"obs": round(float(obs), 4), "ci": [round(float(lo), 4), round(float(hi), 4)],
                "ci_separated": bool(lo > 0 or hi < 0)}

    res = {"docs": len(rows), "split": split, "dropped_sentence_arms": stats["dropped"],
           "scored_sentence_arms": stats["kept"]}
    for arm in ARM_NAMES:
        p, r, f1 = prf(rows, arm)
        res[arm] = {"precision": round(p, 4), "recall": round(r, 4), "f1": round(f1, 4),
                    "tp": sum(x[arm]["tp"] for x in rows), "fp": sum(x[arm]["fp"] for x in rows),
                    "fn": sum(x[arm]["fn"] for x in rows)}
    res["delta_f1"] = delta("perceptron", "counts_penn")
    res["deltas_vs_standin"] = {a: delta("perceptron", a) for a in ARM_NAMES if a != "perceptron"}
    res["deltas_vs_point"] = {a: delta("counts_penn", a) for a in ARM_NAMES
                              if a.startswith("graded") or a.startswith("auxlic")}
    res["per_doc"] = rows
    if verbose:
        for a in ARM_NAMES:
            print("   %-14s P %.4f R %.4f F1 %.4f   (vs stand-in %s)"
                  % (a, res[a]["precision"], res[a]["recall"], res[a]["f1"],
                     res["deltas_vs_standin"].get(a, {}).get("obs", "--")))
        print("EVENT ARM (GUM test, %d docs): organ P/R/F1 %.4f/%.4f/%.4f vs stand-in %.4f/%.4f/%.4f "
              "(delta F1 %+.4f, CI %s, separated %s)"
              % (res["docs"], res["counts_penn"]["precision"], res["counts_penn"]["recall"],
                 res["counts_penn"]["f1"], res["perceptron"]["precision"], res["perceptron"]["recall"],
                 res["perceptron"]["f1"], res["delta_f1"]["obs"], res["delta_f1"]["ci"],
                 res["delta_f1"]["ci_separated"]))
    return res


# ------------------------------------------------------------------ frozen-graph identity
_GRAPH_RUNNER = '''
import hashlib, json, os, sys, time
%(prelude)s
import numpy as np
from hdlab.grounded_semantic_graph import GroundedSemanticGraph as G

def h(T):
    m = hashlib.sha256()
    for a in (T.data, T.indices, T.indptr):
        m.update(np.ascontiguousarray(a).tobytes())
    return m.hexdigest()

out = {}
for mode in ("1", "0"):
    os.environ["HDLAB_GSG_FROZEN"] = mode
    import importlib, hdlab.grounded_semantic_graph as M
    importlib.reload(M)
    t0 = time.time()
    g = M.GroundedSemanticGraph().build()
    out["frozen" if mode == "1" else "rebuilt"] = {
        "secs": round(time.time() - t0, 1), "nodes": len(g.syn2idx), "edges": g.n_edges,
        "csr_sha256": h(g.T), "first_node": sorted(g.syn2idx.items(), key=lambda kv: kv[1])[0][0]}
print("RESULT " + json.dumps(out))
'''


def graph_check(verbose=True):
    """The frozen adjacency must be the SAME MATRIX as the rebuild -- compared on the CSR bytes, not on a
    summary count. Both arms run inside the patched tree; the rebuild arm reads the lexicon organ."""
    prelude = _RUNNER.split("sys.argv = [sys.argv[0]]")[0] % {
        "repo": _REPO, "patched": PATCHED, "poison": True, "paths": [], "tag": "graphcheck"}
    script = os.path.join(OUT_DIR, "runner_graphcheck.py")
    with open(script, "w", encoding="utf-8") as fh:
        fh.write(_GRAPH_RUNNER % {"prelude": prelude})
    env = dict(os.environ)
    env.update({"OMP_NUM_THREADS": "2", "OPENBLAS_NUM_THREADS": "2", "MKL_NUM_THREADS": "2",
                "PYTHONHASHSEED": "0", "HDLAB_EXP_NAME": ANCHOR})
    r = subprocess.run([sys.executable, script], capture_output=True, text=True, encoding="utf-8",
                       errors="replace", cwd=_REPO, env=env, timeout=3600)
    res = None
    for line in (r.stdout or "").split(_LF):
        if line.startswith("RESULT "):
            res = json.loads(line[len("RESULT "):])
    if res is None:
        return {"rc": r.returncode, "tail": (r.stdout or "")[-2000:] + (r.stderr or "")[-2000:]}
    res["identical_csr"] = res["frozen"]["csr_sha256"] == res["rebuilt"]["csr_sha256"]
    res["speedup_x"] = round(res["rebuilt"]["secs"] / max(res["frozen"]["secs"], 0.01), 1)
    if verbose:
        print("GRAPH: frozen %ss vs rebuilt-from-the-organ %ss (%sx), %s nodes / %s edges, CSR identical: %s"
              % (res["frozen"]["secs"], res["rebuilt"]["secs"], res["speedup_x"], res["frozen"]["nodes"],
                 res["frozen"]["edges"], res["identical_csr"]))
    return res


# ------------------------------------------------------------------ timing mode
def timing(n_docs=4, verbose=True):
    docs = _gum_docs(n_docs)
    prepared = _prepare(docs, os.path.join(OUT_DIR, "conll"))
    paths = [p for (_d, p) in prepared]
    a = _run_subprocess(paths, patched=None, poison=False, tag="time_shipped")
    b = _run_subprocess(paths, patched=PATCHED, poison=True, tag="time_organ")
    def tot(x):
        return round(sum(d["secs"] for d in (x["result"] or [])), 1)
    res = {"shipped_secs": tot(a), "organ_secs": tot(b),
           "shipped_per_doc": a["result"], "organ_per_doc": b["result"],
           "shipped_proc_secs": a["secs"], "organ_proc_secs": b["secs"]}
    if verbose:
        print("TIMING: read %ss shipped vs %ss organ (process %ss vs %ss)"
              % (res["shipped_secs"], res["organ_secs"], a["secs"], b["secs"]))
    return res


# ------------------------------------------------------------------ self-test
def self_test():
    shim = RecordingShim().install()
    import nltk.corpus as NC
    wn = NC.wordnet
    ss = wn.synsets("dog", "n")
    names = [s.name() for s in ss]
    paths = ss[0].hypernym_paths()
    lex = ss[0].lexname()
    shim.restore()
    from nltk.corpus import wordnet as real
    assert names == [s.name() for s in real.synsets("dog", "n")], "shim changed synsets()"
    assert lex == real.synsets("dog", "n")[0].lexname(), "shim changed lexname()"
    assert len(paths) == len(real.synsets("dog", "n")[0].hypernym_paths()), "shim changed hypernym_paths()"
    ops = Counter("%s.%s" % (q["kind"], q["op"]) for q in shim.log)
    assert ops["wordnet.synsets"] == 1 and ops["Synset.hypernym_paths"] == 1 and ops["Synset.lexname"] == 1, ops
    # the organ answers the same three queries identically
    from hdlab import lexicon_foundation as LF
    assert [s.name() for s in LF.wordnet.synsets("dog", "n")] == names
    assert LF.wordnet.synsets("dog", "n")[0].lexname() == lex
    assert ([[s.name() for s in p] for p in LF.wordnet.synsets("dog", "n")[0].hypernym_paths()]
            == [[s.name() for s in p] for p in paths])
    # the parity replayer round-trips a logged query
    q = [x for x in shim.log if x["op"] == "hypernym_paths"][0]
    assert _run_one(q, LF.wordnet, {"wordnet": LF.wordnet}) == _run_one(q, real, {"wordnet": real})
    print("self-test OK: shim faithful (%d queries), organ == nltk on synsets/lexname/hypernym_paths, "
          "replayer round-trips" % len(shim.log))
    return 0


# ------------------------------------------------------------------ main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--record", action="store_true")
    ap.add_argument("--rewire", action="store_true")
    ap.add_argument("--parity", action="store_true")
    ap.add_argument("--identity", action="store_true")
    ap.add_argument("--timing", action="store_true")
    ap.add_argument("--graphcheck", action="store_true")
    ap.add_argument("--tagger-arm", action="store_true")
    ap.add_argument("--event-arm", action="store_true")
    ap.add_argument("--docs", type=int, default=4)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    os.makedirs(OUT_DIR, exist_ok=True)
    m = {"ts_iso": datetime.now(timezone.utc).isoformat(), "anchor": ANCHOR, "docs": a.docs}
    t0 = time.time()
    if a.record or a.run:
        per_doc, qpath = record(a.docs)
        m["record"] = {"per_doc": per_doc, **summarise_queries(qpath)}
    if a.rewire or a.run:
        changed, nlines, report = rewire()
        path, nfiles = emit_diff()
        m["rewire"] = {"files": len(changed), "import_lines": nlines, "diff_files": nfiles,
                       "diff": os.path.relpath(path, _REPO), "report": report}
    if a.parity or a.run:
        m["parity"] = parity(limit=a.limit or None)
    if a.tagger_arm or a.run:
        m["tagger_arm"] = tagger_arm()
    if a.event_arm or a.run:
        m["event_arm_dev"] = event_arm(split="dev")
        m["event_arm"] = event_arm(split="test")
    if a.graphcheck or a.run:
        m["graph"] = graph_check()
    if a.identity or a.run:
        m["identity"] = identity(a.docs)
    if a.timing or a.run:
        m["timing"] = timing(a.docs)
    m["elapsed_s"] = round(time.time() - t0, 1)
    mp = os.path.join(OUT_DIR, "metrics.json")
    if os.path.exists(mp):                      # MERGE: a single-mode run must not erase the other modes'
        try:                                    # landed numbers (each section carries its own ts_iso)
            prev = json.load(open(mp, encoding="utf-8"))
            prev.update(m)
            m = prev
        except Exception:
            pass
    with open(mp, "w", encoding="utf-8") as fh:
        json.dump(m, fh, indent=2, sort_keys=True)
    print("wrote %s" % os.path.join(OUT_DIR, "metrics.json"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
