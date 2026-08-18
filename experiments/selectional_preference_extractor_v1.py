"""SELECTIONAL-PREFERENCE extraction -- what KIND of thing can fill this verb's argument slot.

WHY THIS EXISTS, and it is a brain-fidelity change, not a tuning change.
--------------------------------------------------------------------------------------------
The owner was asked what they take from "the tove ran across the road" (BOARD Q5) and answered,
verbatim:

  "Since the tove ran - it must be an animal (or at least something that has legs). Since it ran
   accross the road, I think of rabbits and deer which I've seen cross roads, and so I assume it's
   a smallish animal, most likely a mammel but it could also be a reptile."

THEY NEVER COPIED A NEIGHBOURING WORD. The first and primary inference is from the VERB'S
SELECTIONAL CONSTRAINT: `run` requires an agent that is animate and has legs. Our existing bridge
(`exp_thematic_relation_supply_bridged_grounding_v2`, landed
BRIDGED_CODES_DO_NOT_CLEAR_THE_FLOOR_ON_OUR_GRAPH, B1 rho 0.0270 against a 0.0900 scramble p95)
copies the code of a CO-OCCURRING NEIGHBOUR WORD. That is lexical association, not argument
structure.

BRAIN STRUCTURE.
  Verb-argument / thematic-role structure is carried by TEMPORO-PARIETAL cortex -- posterior middle
  temporal gyrus and ANGULAR GYRUS -- separate from the anterior-temporal taxonomic hub, and AG
  activation scales with the complexity of the verb's argument structure.
  [PINNED: Schwartz et al. 2011 PNAS lesion double dissociation; Mirman, Landrigan & Britt 2017
   Psych Bull 143:499 dual hub; pMTG-vs-AG TMS dissociation J Neurosci 36(16):4405; 'Same words,
   different structures' Neuropsychologia PMID 30735675.]
  Selectional restriction is a THEMATIC-ROLE phenomenon, so this rides the hub that
  `thematic_relation_extractor_v1` opened. It does NOT build a third hub.
  [PINNED, developmental: slot-filler organisation is prior to taxonomic organisation to ~7y --
   Nelson/Lucariello. A "slot filler" is LITERALLY what this module extracts.]

WHAT IS OURS -- INVENTION UNDER TEST, and it is marked as such everywhere it appears:
  - the SLOT definition (verb lemma x normalised UD role) as the unit of selectional constraint
  - mapping nsubj:pass -> OBJ and obl:agent -> SUBJ (the passive alternation), so a deep patient
    is not counted as an agent
  - attaching the case preposition to obliques (obl:across) rather than pooling all obliques
  - the count / distinct-filler gates and the top-k slot cap
  The literature pins that verbs constrain their arguments and that AG carries it. It pins no
  extraction rule and no estimator.

ORGAN REUSE, NOT A PARALLEL BUILD -- every one verified by RUNTIME (import + call), not by grep:
  hdlab.pos_tagger.PosTagger          persisted UD-EWT averaged perceptron tagger
  hdlab.arc_parser.ArcParser          persisted hashed arc-factored dependency parser
  hdlab.arc_labeler.ArcLabeler        persisted UD RELATION labeler (nsubj/obj/nsubj:pass/obl:agent)
  hdlab.reading_grounding_loop        normalize_lemma -- the SAME lemmatiser the definitional graph
                                      uses, so nodes are comparable across channels
  experiments.thematic_relation_extractor_v1  the corpus budget, the sentence filter and the
                                      token regex, so the SENTENCE SET is identical and the only
                                      variable changed is the RELATION RULE
These three front-end modules are imported INSIDE a function body in hdlab/reading_grounding_loop.py
and are therefore invisible to grep; they were verified here by loading the persisted assets and
parsing "the tove ran across the road", which yields nsubj(tove, run) and obl(road, run).

NO EXTERNAL LANGUAGE MODEL ANYWHERE. The tagger/parser/labeler are our own glass-box perceptrons
trained on UD EWT and persisted as json/npz. WordNet is used only as a POS/lemma oracle, exactly as
the existing extractors already use it.

ASCII-only. CPU. No network. data/foundation/** is never opened by this module.
"""
from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import argparse
import collections
import json
import multiprocessing as mp
import pickle
import re
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

REPO = Path(__file__).resolve().parent.parent
for _p in (str(REPO), str(REPO / "experiments")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

EXTRACTOR_VERSION = "selectional_v1.0"
OUT_DIR = REPO / "data" / "selectional_preferences_v1"
SLOTS_PKL = OUT_DIR / "selectional_slots_v1.pkl"
REPORT_JSON = OUT_DIR / "extraction_report_v1.json"

FRONTEND_DIR = REPO / "data" / "frontend_assets"
POS_ASSET = "pos_tagger_ud_ewt_upos.json"
PARSER_ASSET = "arc_parser_richfeat_ud_ewt.npz"
LABELER_ASSET = "arc_labeler_hashed_ud_ewt.json"

# identical to thematic_relation_extractor_v1 -- the SENTENCE SET must not be a variable
TOKEN = re.compile(r"[a-z]+")
MIN_SENT_TOKENS = 4
MAX_SENT_TOKENS = 40
MIN_LEMMA_LEN = 3

STRUCT_TOKEN_RE = re.compile(r"[A-Za-z]+(?:'[A-Za-z]+)?|[0-9]+|[^\sA-Za-z0-9]")

# ---- OURS -- INVENTION UNDER TEST: the role normalisation ---------------------------------
# nsubj:pass -> OBJ and obl:agent -> SUBJ implement the PASSIVE ALTERNATION, so "the road was
# crossed by the tove" contributes `tove` to cross/SUBJ and `road` to cross/OBJ, exactly as the
# active sentence does. Without this the same event teaches the opposite constraint.
CORE_ROLE = {
    "nsubj": "SUBJ",
    "obj": "OBJ",
    "iobj": "IOBJ",
    "nsubj:pass": "OBJ",
    "obl:agent": "SUBJ",
    "csubj": "SUBJ",
}
OBL_ROLE = "obl"


def _load_frontend():
    from hdlab.pos_tagger import PosTagger
    from hdlab.arc_parser import ArcParser
    from hdlab.arc_labeler import ArcLabeler
    tg = PosTagger.load(str(FRONTEND_DIR / POS_ASSET))
    pr = ArcParser.load(str(FRONTEND_DIR / PARSER_ASSET))
    lb = ArcLabeler.load(str(FRONTEND_DIR / LABELER_ASSET))
    return tg, lb, pr


_W: Dict[str, object] = {}


def _init_worker(norms_words: Set[str], track_words: Set[str]) -> None:
    from hdlab.reading_grounding_loop import normalize_lemma
    tg, lb, pr = _load_frontend()
    _W["tg"] = tg
    _W["lb"] = lb
    _W["pr"] = pr
    _W["norms"] = norms_words
    _W["track"] = track_words
    _W["lem_cache"] = {}
    _W["normalize_lemma"] = normalize_lemma


def _lem(tok: str) -> str:
    c = _W["lem_cache"]
    v = c.get(tok)
    if v is None:
        v = _W["normalize_lemma"](tok)
        c[tok] = v
    return v


def _process_chunk(lines: List[str]) -> Tuple[Dict, Dict, Dict, Dict]:
    """-> (slot_filler, word_cooc, stats, role_hist).

    slot_filler : {(verb_lemma, role): {filler_lemma: count}}
      role is "SUBJ" / "OBJ" / "IOBJ" / "obl:<prep>".
    word_cooc   : {tracked_word: {lemma: count}}  -- sentence-level co-occurrence, TRACKED WORDS
      ONLY (the SimLex vocabulary). This exists solely to power the decisive control arm that
      deletes every filler which ever shares a sentence with the target.
    """
    tg, lb, pr = _W["tg"], _W["lb"], _W["pr"]
    norms: Set[str] = _W["norms"]
    track: Set[str] = _W["track"]
    slot_filler: Dict[Tuple[str, str], collections.Counter] = collections.defaultdict(
        collections.Counter)
    word_cooc: Dict[str, collections.Counter] = collections.defaultdict(collections.Counter)
    role_hist: collections.Counter = collections.Counter()
    n_seen = n_parsed = n_slots = 0

    for line in lines:
        n_seen += 1
        toks = STRUCT_TOKEN_RE.findall(line)
        if not toks or len(toks) > 60:
            continue
        try:
            pos = tg.tag(toks)
            heads = pr.parse(toks, pos).heads
            labs = lb.label(toks, pos, heads)
        except Exception:
            continue
        n_parsed += 1
        n = len(toks)
        lemmas = [_lem(t) for t in toks]

        # sentence-level co-occurrence, tracked words only
        present = {lm for lm in lemmas if lm and len(lm) >= MIN_LEMMA_LEN and lm in norms}
        for w in present & track:
            for other in present:
                if other != w:
                    word_cooc[w][other] += 1

        # case preposition of each token (for obliques)
        case_of: Dict[int, str] = {}
        for i in range(1, n + 1):
            if labs.get(i) == "case":
                h = heads.get(i, 0)
                if h and h not in case_of:
                    case_of[h] = toks[i - 1].lower()

        for i in range(1, n + 1):
            rel = labs.get(i)
            if rel is None:
                continue
            h = heads.get(i, 0)
            if not h or not (1 <= h <= n):
                continue
            if pos[h - 1] != "VERB":            # AUX excluded -- a copula is not an event predicate
                continue
            filler = lemmas[i - 1]
            if not filler or len(filler) < MIN_LEMMA_LEN or filler not in norms:
                continue
            if rel in CORE_ROLE:
                role = CORE_ROLE[rel]
            elif rel == OBL_ROLE:
                prep = case_of.get(i)
                if not prep or not prep.isalpha():
                    continue
                role = "obl:" + prep
            else:
                continue
            verb = lemmas[h - 1]
            if not verb or len(verb) < 2:
                continue
            slot_filler[(verb, role)][filler] += 1
            role_hist[role if not role.startswith("obl:") else "obl:*"] += 1
            n_slots += 1

    return (
        {k: dict(v) for k, v in slot_filler.items()},
        {k: dict(v) for k, v in word_cooc.items()},
        {"n_seen": n_seen, "n_parsed": n_parsed, "n_slot_observations": n_slots},
        dict(role_hist),
    )


def _simlex_vocab() -> Set[str]:
    import csv
    out: Set[str] = set()
    with open(REPO / "data" / "encoder_eval_benchmarks" / "simlex999.txt", encoding="utf-8") as fh:
        rd = csv.reader(fh, delimiter="\t")
        next(rd)
        for r in rd:
            if len(r) >= 4:
                out.add(r[0].strip().lower())
                out.add(r[1].strip().lower())
    return out


def extract(corpus_bytes: Optional[int] = None, max_sentences: Optional[int] = None,
            n_workers: int = 8, verbose: bool = True) -> Dict:
    """Stream the SAME corpus budget as thematic_relation_extractor_v1 and return raw slot tables.

    NO gating is applied here -- the count / distinct-filler / top-k gates belong to the CONSUMING
    cell's pre-registration, not to the extractor.
    """
    import thematic_relation_extractor_v1 as THEM
    from hdlab import grounded_similarity as GS

    t0 = time.time()
    cb = THEM.CORPUS_BYTES if corpus_bytes is None else corpus_bytes
    with open(THEM.CORPUS, "rb") as f:
        raw = f.read(cb)
    cut = raw.rfind(b"\n")
    if cut > 0:
        raw = raw[:cut]
    all_lines = raw.decode("utf-8", errors="ignore").split("\n")
    del raw

    # IDENTICAL sentence filter to the thematic extractor: token count measured on the LOWERCASED
    # line with the same [a-z]+ regex. The line itself is parsed with ITS ORIGINAL CASE, because the
    # UD tagger reads capitalisation as a feature. Same sentences, better tags.
    lines = []
    for ln in all_lines:
        s = ln.strip()
        if not s:
            continue
        k = len(TOKEN.findall(s.lower()))
        if MIN_SENT_TOKENS <= k <= MAX_SENT_TOKENS:
            lines.append(s)
    del all_lines
    if max_sentences:
        lines = lines[:max_sentences]
    if verbose:
        print(f"[corpus] {len(lines)} sentences in [{MIN_SENT_TOKENS},{MAX_SENT_TOKENS}] tokens "
              f"from {cb} bytes ({time.time() - t0:.0f}s)", flush=True)

    norms = set(GS._table())
    track = _simlex_vocab()

    n_workers = max(1, int(n_workers))
    chunk = max(1, (len(lines) + n_workers * 8 - 1) // (n_workers * 8))
    chunks = [lines[i:i + chunk] for i in range(0, len(lines), chunk)]
    if verbose:
        print(f"[parallel] {len(chunks)} chunks of <= {chunk} sentences over {n_workers} workers",
              flush=True)

    slot_filler: Dict[Tuple[str, str], collections.Counter] = collections.defaultdict(
        collections.Counter)
    word_cooc: Dict[str, collections.Counter] = collections.defaultdict(collections.Counter)
    role_hist: collections.Counter = collections.Counter()
    stats = collections.Counter()

    _si = sys.intern

    def _merge(res):
        # INTERN on merge: each worker returns its own copies of the same few thousand lemma
        # strings, and without interning the parent holds one object per (worker, chunk, lemma).
        # Measured necessity, not hygiene -- word_cooc is the memory hot spot.
        sf, wc, st, rh = res
        for k, v in sf.items():
            slot_filler[(_si(k[0]), _si(k[1]))].update({_si(a): b for a, b in v.items()})
        for k, v in wc.items():
            word_cooc[_si(k)].update({_si(a): b for a, b in v.items()})
        role_hist.update(rh)
        stats.update(st)

    if n_workers == 1:
        _init_worker(norms, track)
        for i, ch in enumerate(chunks):
            _merge(_process_chunk(ch))
            if verbose:
                print(f"[chunk] {i + 1}/{len(chunks)} t={time.time() - t0:.0f}s", flush=True)
    else:
        ctx = mp.get_context("spawn")
        with ctx.Pool(processes=n_workers, initializer=_init_worker,
                      initargs=(norms, track)) as pool:
            for i, res in enumerate(pool.imap_unordered(_process_chunk, chunks)):
                _merge(res)
                if verbose:
                    print(f"[chunk] {i + 1}/{len(chunks)} t={time.time() - t0:.0f}s "
                          f"slots={len(slot_filler)}", flush=True)

    out = {
        "extractor_version": EXTRACTOR_VERSION,
        "corpus": str(THEM.CORPUS),
        "corpus_bytes": cb,
        "slot_filler": {k: dict(v) for k, v in slot_filler.items()},
        "word_cooc": {k: dict(v) for k, v in word_cooc.items()},
        "stats": dict(stats),
        "role_histogram": dict(role_hist),
        "n_slots": len(slot_filler),
        "elapsed_s": round(time.time() - t0, 1),
    }
    if verbose:
        print(f"[done] slots={out['n_slots']} obs={stats['n_slot_observations']} "
              f"parsed={stats['n_parsed']}/{stats['n_seen']} in {out['elapsed_s']}s", flush=True)
    return out


def build_or_load(force: bool = False, verbose: bool = True, n_workers: int = 8) -> Dict:
    if SLOTS_PKL.exists() and not force:
        with open(SLOTS_PKL, "rb") as f:
            d = pickle.load(f)
        if d.get("extractor_version") == EXTRACTOR_VERSION:
            if verbose:
                print(f"[cache] loaded {SLOTS_PKL} slots={d['n_slots']}", flush=True)
            return d
    d = extract(n_workers=n_workers, verbose=verbose)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    tmp = str(SLOTS_PKL) + ".tmp"
    with open(tmp, "wb") as f:
        pickle.dump(d, f, protocol=4)
    os.replace(tmp, str(SLOTS_PKL))
    rep = {k: v for k, v in d.items() if k not in ("slot_filler", "word_cooc")}
    rep["example_slots"] = _examples(d, 12)
    tmp = str(REPORT_JSON) + ".tmp"
    with open(tmp, "w", encoding="ascii", errors="replace") as f:
        json.dump(rep, f, indent=1)
    os.replace(tmp, str(REPORT_JSON))
    return d


def _examples(d: Dict, k: int) -> Dict:
    sf = d["slot_filler"]
    top = sorted(sf, key=lambda s: -sum(sf[s].values()))[:k]
    return {f"{v}/{r}": sorted(sf[(v, r)].items(), key=lambda kv: -kv[1])[:10] for v, r in top}


def self_test() -> Dict:
    """Assert MEASURED values, not just 'it ran'. Every assertion is a real trap."""
    ev: Dict[str, object] = {}

    # S1 -- the persisted front-end really produces the roles this module depends on, on the
    # owner's own sentence. A tagger that cannot find nsubj makes this whole module a no-op.
    _init_worker(set(), set())
    toks = STRUCT_TOKEN_RE.findall("The tove ran across the road .")
    pos = _W["tg"].tag(toks)
    heads = _W["pr"].parse(toks, pos).heads
    labs = _W["lb"].label(toks, pos, heads)
    got = {toks[i - 1].lower(): (labs.get(i), toks[heads.get(i, 1) - 1].lower())
           for i in range(1, len(toks) + 1)}
    assert got.get("tove") == ("nsubj", "ran"), f"S1 nsubj not recovered: {got}"
    assert got.get("road", (None, None))[0] == "obl", f"S1 obl not recovered: {got}"
    assert _lem("ran") == "run", f"S1 lemmatiser: ran -> {_lem('ran')}"
    ev["S1_owner_sentence_parse"] = {"tove": got.get("tove"), "road": got.get("road"),
                                     "ran_lemma": _lem("ran")}

    # S2 -- the passive alternation really maps to the DEEP roles (the mapping is OURS; this proves
    # the code does what the docstring claims, not that the mapping is correct biology).
    assert CORE_ROLE["nsubj:pass"] == "OBJ" and CORE_ROLE["obl:agent"] == "SUBJ"
    ev["S2_passive_alternation_mapping"] = dict(CORE_ROLE)

    # S3 -- a tiny end-to-end extraction really fills the slot with the right filler, and really
    # EXCLUDES a copular clause (AUX head), which would otherwise flood every slot.
    _init_worker({"dog", "rabbit", "road", "animal", "deer"}, {"road"})
    sf, wc, st, rh = _process_chunk([
        "The dog ran across the road .",
        "A rabbit ran across the road .",
        "The deer ran across the road .",
        "The dog is an animal .",
    ])
    subj = sf.get(("run", "SUBJ"), {})
    assert set(subj) == {"dog", "rabbit", "deer"}, f"S3 run/SUBJ fillers = {subj}"
    assert sf.get(("be", "SUBJ")) is None and sf.get(("is", "SUBJ")) is None, \
        f"S3 copula was not excluded: {sorted(sf)}"
    assert ("run", "obl:across") in sf and set(sf[("run", "obl:across")]) == {"road"}, \
        f"S3 obl:across = {sf.get(('run', 'obl:across'))}"
    assert "road" in wc and wc["road"].get("dog") == 1, f"S3 cooc = {wc}"
    ev["S3_end_to_end"] = {"run/SUBJ": subj, "run/obl:across": sf[("run", "obl:across")],
                           "slots": sorted(f"{a}/{b}" for a, b in sf), "stats": st}

    # S4 -- the sentence filter is BYTE-IDENTICAL in spirit to the thematic extractor's, so the
    # sentence SET is not a hidden second variable.
    import thematic_relation_extractor_v1 as THEM
    assert (THEM.MIN_SENT_TOKENS, THEM.MAX_SENT_TOKENS) == (MIN_SENT_TOKENS, MAX_SENT_TOKENS)
    assert THEM.TOKEN.pattern == TOKEN.pattern
    assert THEM.MIN_LEMMA_LEN == MIN_LEMMA_LEN
    ev["S4_sentence_filter_identical_to_thematic_extractor"] = {
        "min": MIN_SENT_TOKENS, "max": MAX_SENT_TOKENS, "token_re": TOKEN.pattern}

    print("[selftest] ALL PASS " + json.dumps(ev, default=str)[:900], flush=True)
    return ev


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--max-sentences", type=int, default=0)
    a = ap.parse_args()
    self_test()
    if a.self_test:
        print("SELFTEST_ONLY_OK")
        return 0
    if a.max_sentences:
        d = extract(max_sentences=a.max_sentences, n_workers=a.workers)
        print(json.dumps(_examples(d, 10), indent=1)[:3000])
        return 0
    d = build_or_load(force=a.force, n_workers=a.workers)
    print(json.dumps(_examples(d, 10), indent=1)[:3000])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
