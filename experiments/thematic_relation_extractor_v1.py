"""THEMATIC (event co-participation) + VERB-ARGUMENT relation extraction from OUR OWN corpus.

PROMOTED OUT OF scratch/ ON 2026-08-16. Provenance: this is `scratch/relsupply_thematic.py`
(the relation-supply scan, `.claude/scan-out/relation-supply.json`) moved into `experiments/`
because its output is now LOAD-BEARING for a landed cell
(`experiments/exp_thematic_relation_supply_bridged_grounding_v2.py`) and CLAUDE.md's scratch
corollary forbids a durable citation into a directory that gets wiped. The extraction logic is
UNCHANGED from the scan that measured the supply numbers; what changed is the OUTPUT PATH
(`data/thematic_relations_v1/` instead of `scratch/`) and the addition of a `--self-test`.

WHY THIS EXISTS -- brain fidelity, stated per component:
  BRAIN STRUCTURE   THEMATIC relations -- co-participation in an EVENT (dog/leash, spoon/soup) --
                    are carried by a temporo-parietal system (posterior middle temporal gyrus +
                    angular gyrus), SEPARATE from the anterior temporal lobe that carries
                    TAXONOMIC relations. PINNED: Schwartz et al. 2011 PNAS (voxel-based
                    lesion-symptom mapping double dissociation); Mirman, Landrigan & Britt 2017
                    Psychological Bulletin 143:499 (dual-hub review). Thematic organisation is
                    developmentally PRIOR (Nelson/Lucariello slot-filler programme).
  OUR STATE BEFORE  all 5,799 relations we had extracted were TAXONOMIC-DEFINITIONAL
                    (COPULA 2006 / APPOSITIVE 1521 / CALLED 1303 / GLOSSARY_COLON 944 /
                    REFERS_TO 25). We had built one of the brain's two relational hubs.
  ORGAN REUSE       the finite-main-verb detector is hdlab.definitional_extraction.clause_main_verb
                    (REUSED, memoised, not reimplemented); the lemmatiser is
                    hdlab.reading_grounding_loop.normalize_lemma -- the SAME one the definitional
                    graph uses, so the two channels are comparable node for node. The closed-class
                    filter and the WordNet POS oracle are also the definitional extractor's own.
  OURS / INVENTION  the specific EDGE DEFINITION (event co-participation inside a finite-verb
                    clause, PMI-gated, count-gated, top-k capped) is OURS-INVENTION-UNDER-TEST.
                    The literature pins that thematic relations exist, are carried separately and
                    are action/location-flavoured. It pins NO extraction rule.

NO EXTERNAL LANGUAGE MODEL ANYWHERE. Counts and PMI are computed from OUR OWN corpus -- the
IDENTICAL simplewiki byte budget the Phase-1 instrument computes its FREQUENCY FLOOR on -- and
never from a pretrained table. WordNet is used only as a part-of-speech / lemma oracle, exactly as
the existing definitional extractor already uses it, never as a similarity or meaning source.

ASCII-only. CPU. No network.

Writes data/thematic_relations_v1/thematic_edges_v1.pkl and .../extraction_report_v1.json.
"""
from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import argparse
import collections
import csv
import functools
import json
import math
import pickle
import re
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

REPO = Path(__file__).resolve().parent.parent
for _p in (str(REPO), str(REPO / "experiments")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

TOKEN = re.compile(r"[a-z]+")
MAX_SENT_TOKENS = 40
MIN_SENT_TOKENS = 4
MIN_LEMMA_LEN = 3
CORPUS = REPO / "data" / "corpora" / "simplewiki" / "simplewiki_clean_v1.txt"
CORPUS_BYTES = 64_000_000          # the Phase-1 frequency-floor budget, deliberately identical
OUT_DIR = REPO / "data" / "thematic_relations_v1"
EDGES_PKL = OUT_DIR / "thematic_edges_v1.pkl"
REPORT_JSON = OUT_DIR / "extraction_report_v1.json"
EXTRACTOR_VERSION = "thematic_v1.0"


def _vocab_of_interest() -> set:
    """The SimLex vocabulary. Event pairs are only counted when at least one endpoint is in it --
    this BOUNDS MEMORY and is exactly the population the bridging strata are defined over."""
    out = set()
    with open(REPO / "data" / "encoder_eval_benchmarks" / "simlex999.txt", encoding="utf-8") as fh:
        rd = csv.reader(fh, delimiter="\t")
        next(rd)
        for r in rd:
            if len(r) >= 4:
                out.add(r[0].strip().lower())
                out.add(r[1].strip().lower())
    return out


def extract(corpus_bytes: int = CORPUS_BYTES, max_sentences: Optional[int] = None,
            verbose: bool = True) -> Dict:
    """Stream the corpus once and return the raw edge tables. No gating is applied here --
    the count / PMI / top-k gates are the CONSUMER's pre-registered choice, not the extractor's."""
    t0 = time.time()
    from hdlab import definitional_extraction as DE
    from hdlab.reading_grounding_loop import normalize_lemma
    from hdlab import grounded_similarity as GS

    # memoise the REUSED organ's hot WordNet lookups. Same function, same answers, cached.
    DE.verb_lemma_of = functools.lru_cache(maxsize=None)(DE.verb_lemma_of)
    DE.is_verbal_lemma = functools.lru_cache(maxsize=None)(DE.is_verbal_lemma)
    DE.is_nominal_lemma = functools.lru_cache(maxsize=None)(DE.is_nominal_lemma)
    DE.is_closed_class = functools.lru_cache(maxsize=None)(DE.is_closed_class)
    _lem_cache: Dict[str, str] = {}

    def lem(tok: str) -> str:
        v = _lem_cache.get(tok)
        if v is None:
            v = normalize_lemma(tok)
            _lem_cache[tok] = v
        return v

    norms = set(GS._table())
    simlex = _vocab_of_interest()

    with open(CORPUS, "rb") as f:
        raw = f.read(corpus_bytes)
    cut = raw.rfind(b"\n")
    if cut > 0:
        raw = raw[:cut]
    lines = raw.decode("utf-8", errors="ignore").lower().split("\n")
    if max_sentences:
        lines = lines[:max_sentences]
    if verbose:
        print(f"[corpus] {len(lines)} sentences from {len(raw)} bytes "
              f"({time.time() - t0:.0f}s)", flush=True)

    uni: collections.Counter = collections.Counter()          # sentence-level document frequency
    pair_va: collections.Counter = collections.Counter()      # (content lemma, VERB lemma)
    pair_ev: collections.Counter = collections.Counter()      # (content lemma, content lemma)
    verb_of_edge: Dict[Tuple[str, str], collections.Counter] = collections.defaultdict(
        collections.Counter)
    n_ev_sent = 0
    n_no_verb = 0
    t1 = time.time()
    for si, line in enumerate(lines):
        toks = TOKEN.findall(line)
        if not (MIN_SENT_TOKENS <= len(toks) <= MAX_SENT_TOKENS):
            continue
        hit = DE.clause_main_verb(toks)
        if hit is None:
            n_no_verb += 1
            continue
        vi, vlem = hit
        n_ev_sent += 1
        content: List[str] = []
        for i, t in enumerate(toks):
            if i == vi or len(t) < MIN_LEMMA_LEN:
                continue
            l = lem(t)
            if len(l) < MIN_LEMMA_LEN or l not in norms or l == vlem:
                continue
            if DE.is_closed_class(l):
                continue
            content.append(l)
        content = sorted(set(content))
        for l in content:
            uni[l] += 1
        if vlem in norms:
            uni[vlem] += 1
            for l in content:
                pair_va[(l, vlem)] += 1
        for i, a in enumerate(content):
            for b in content[i + 1:]:
                if a in simlex or b in simlex:
                    k = (a, b)
                    c = pair_ev[k] + 1
                    pair_ev[k] = c
                    if c >= 2:                 # bound memory: type the edge once it survives
                        verb_of_edge[k][vlem] += 1
        if verbose and si and si % 100000 == 0:
            print(f"[scan] {si} sentences {time.time() - t1:.0f}s ev={n_ev_sent} "
                  f"pairs_ev={len(pair_ev)} pairs_va={len(pair_va)}", flush=True)

    tot = max(n_ev_sent, 1)

    def pmi(c_ab: int, a: str, b: str) -> float:
        pa, pb = uni[a] / tot, uni[b] / tot
        if pa <= 0 or pb <= 0 or c_ab <= 0:
            return -99.0
        return math.log((c_ab / tot) / (pa * pb))

    ev_rows = []
    for (a, b), c in pair_ev.items():
        if c < 2:
            continue
        ev_rows.append((a, b, c, round(pmi(c, a, b), 4), verb_of_edge[(a, b)].most_common(3)))
    va_rows = []
    for (a, v), c in pair_va.items():
        if c < 2 or not (a in simlex or v in simlex):
            continue
        va_rows.append((a, v, c, round(pmi(c, a, v), 4)))

    # the RAW co-occurrence table (count >= 2), kept so a consumer can build the
    # NEVER-CO-OCCUR sub-stratum without re-reading the corpus
    cooc = {(a, b): c for (a, b), c in pair_ev.items() if c >= 2}

    report = {
        "extractor_version": EXTRACTOR_VERSION,
        "corpus": str(CORPUS.relative_to(REPO)).replace("\\", "/"),
        "corpus_bytes_read": len(raw),
        "corpus_bytes_requested": corpus_bytes,
        "n_sentences_seen": len(lines),
        "n_sentences_with_finite_main_verb": n_ev_sent,
        "n_sentences_refused_no_verb": n_no_verb,
        "verb_detection_rate": round(n_ev_sent / max(len(lines), 1), 4),
        "n_distinct_normed_lemmas_seen": len(uni),
        "n_event_pairs_raw": len(pair_ev),
        "n_event_pairs_count_ge2": len(ev_rows),
        "n_verbarg_pairs_raw": len(pair_va),
        "n_verbarg_pairs_count_ge2": len(va_rows),
        "NOTE_verb_detection_rate_is_YIELD_not_ACCURACY": (
            "clause_main_verb was built and self-tested on textbook definitional sentences; its "
            "acceptance rate on simplewiki prose is a YIELD number and has NOT been hand-scored"),
        "elapsed_s": round(time.time() - t0, 1),
    }
    return {"event": ev_rows, "verbarg": va_rows, "uni": dict(uni), "cooccurrence": cooc,
            "n_event_sentences": n_ev_sent, "report": report}


def build_or_load(force: bool = False, verbose: bool = True) -> Dict:
    """Load the banked edge tables, extracting them once if absent. Deterministic: the extraction
    is a single pass over a fixed byte budget with no randomness anywhere."""
    if EDGES_PKL.exists() and not force:
        with open(EDGES_PKL, "rb") as f:
            d = pickle.load(f)
        if d.get("report", {}).get("extractor_version") == EXTRACTOR_VERSION:
            if verbose:
                print(f"[thematic] loaded {EDGES_PKL} "
                      f"({d['report']['n_event_pairs_count_ge2']} event edges)", flush=True)
            return d
    d = extract(verbose=verbose)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    tmp = EDGES_PKL.with_suffix(".pkl.tmp")
    with open(tmp, "wb") as f:
        pickle.dump(d, f)
    os.replace(tmp, EDGES_PKL)
    tmpj = REPORT_JSON.with_suffix(".json.tmp")
    tmpj.write_text(json.dumps(d["report"], indent=1), encoding="utf-8")
    os.replace(tmpj, REPORT_JSON)
    if verbose:
        print(json.dumps(d["report"], indent=1), flush=True)
    return d


def self_test() -> int:
    """Prove the extractor produces THEMATIC edges (not morphological ones) on a tiny slice, and
    that it REFUSES sentences with no finite main verb rather than guessing."""
    d = extract(corpus_bytes=4_000_000, max_sentences=20000, verbose=False)
    r = d["report"]
    assert r["n_sentences_with_finite_main_verb"] > 100, r
    assert r["n_sentences_refused_no_verb"] > 0, "the verb detector never refused -- it is guessing"
    assert len(d["event"]) > 100, "no event edges survived count>=2 on the slice"
    # an edge must be a PAIR OF DISTINCT LEMMAS, not a word with itself or a spelling variant
    for a, b, c, p, _v in d["event"][:2000]:
        assert a != b and c >= 2
    # PMI must be finite and must actually discriminate (not all edges at one value)
    pm = sorted({round(p, 3) for _a, _b, _c, p, _v in d["event"][:5000]})
    assert len(pm) > 50, f"PMI is degenerate: only {len(pm)} distinct values"
    print(f"[selftest] OK sentences_with_verb={r['n_sentences_with_finite_main_verb']} "
          f"refused={r['n_sentences_refused_no_verb']} event_edges={len(d['event'])} "
          f"distinct_pmi={len(pm)}")
    print("SELFTEST_OK")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--force", action="store_true")
    a, _ = ap.parse_known_args()
    if a.self_test:
        return self_test()
    build_or_load(force=a.force)
    return 0


if __name__ == "__main__":
    sys.exit(main())
