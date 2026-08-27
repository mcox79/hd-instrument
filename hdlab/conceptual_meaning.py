"""Conceptual / definitional meaning channel -- the ATL amodal hub (the reader's SECOND meaning system).

Landed 2026-08-27 (consolidation phase) from the integrated `the_reader_has_no_conceptual_meaning_channel`
(SOLVED/EXCELLENT, owner-DONE; witness `test_conceptual_meaning_channel.py` PASS, re-verified first-hand). The
reader had ONLY the associative/co-occurrence meaning system (what a word goes WITH) and was at chance on human
meaning-IDENTITY (what a word IS). This organ is the missing amodal ATL CONCEPTUAL HUB (Controlled Semantic
Cognition; Lambon Ralph/Jefferies/Patterson/Rogers 2017): a glass-box STATIC asset that captures definitional/
taxonomic structure.

WHAT IS PINNED (copy the operation):
  * The ATL hub captures what a concept IS -- definitional/taxonomic structure, TAXONOMIC similarity, and it
    PRIVILEGES DISTINCTIVE features (the features lost first in semantic dementia). Meaning-IDENTITY is a HUB
    computation; thematic RELATEDNESS is the distributed distributional/associative system's job.
  * REPRESENTATION: a per-word definitional feature bag = WordNet gloss + examples + synonym lemmas + genus/
    hypernym closure (up `hyper_levels`), aggregated over the word's synsets, SENSE-FREQUENCY weighted
    (WordNet order). The distinctive-feature operation is realised as global-IDF weighting (a token's
    document-frequency over ALL ~117k synsets -- the SPARSE-space analog of the ATL's privilege-distinctive-
    features op). Scored by sparse cosine. NO learning, NO LLM -- an offline STATIC asset (admissible).
  * VALIDATED (off-WordNet human gold, vs a STEELMANNED GloVe-300, not the reader's weak 0.04 co-occurrence):
    SimLex-999 rho 0.521 vs 0.371 (+0.1505 CI-sep), SimVerb 0.499 vs 0.220; shuffled-gloss twin LOSES; IDF
    beats UNWEIGHTED overlap CI-sep (the distinctive-feature op earns its keep); a DOUBLE DISSOCIATION holds
    (conceptual->similarity, associative->relatedness; crossover +0.197 CI-sep; GloVe wins WordSim relatedness).

OUR-INVENTION / BOUNDARIES (do NOT chase):
  * The distinctive-feature op is SUPPLY-DEPENDENT: DENSE grounding -> whiten; SPARSE definitional -> IDF. A
    learned SVD covariance-DISTILLATION does NOT beat sparse IDF on this supply (tested-negative -- a fidelity
    boundary). Do NOT add a distillation step; do NOT train a GPU hub over this SINGLE spoke (premature).
  * ROUTING (composition, not this organ): DEMAND-ROUTE identity/similarity -> conceptual, relatedness ->
    associative; FUSE (not switch) for decontextualised graded RATING (fusion ties/beats routing there);
    conflict-gated SELECTION is the semantic_control organ's job. Deepest finding for the composition:
    meaning-similarity is OPERATION-SPECIFIC per word class (noun=taxonomic overlap [this organ]; adjective=
    signed-magnitude, verb=relational) -- OPERATION-ROUTE the read-out by word class downstream.

DEFAULT-SAFE / ISLAND: a NEW module -- importing it changes NO existing behaviour. The global IDF is built
once and cached to disk (offline static asset). MEASURE on the live reading task before any capability claim
(SimLex/SimVerb are naturalistic instruments, not the reader's own task); quote the CI-separated WIN over the
competitor + the twin losing + the dissociation, NOT the absolute rho (WordNet provenance).
"""
from __future__ import annotations

import json
import math
import os
from collections import Counter
from typing import Dict, List, Optional, Tuple

from nltk.corpus import wordnet as wn  # lazy LazyCorpusLoader -- import is cheap, data hit deferred to first use

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_IDF_CACHE = os.path.join(_REPO, "data", "hdlab_conceptual_idf", "global_idf.json")

# the validated headline config (C_full): gloss+examples + synonym lemmas + 2 levels of genus/hypernym closure
DEFAULT_CFG: Dict = {"gloss": True, "lemmas": True, "hyper": True, "hyper_levels": 2}
POSMAP = {"A": ("a", "s"), "N": ("n",), "V": ("v",)}
STOP = set("a an the of to in on at for and or but if then than that this these those with without within "
           "from into onto over under is are was were be been being have has had do does did would should "
           "could can will may might must not no as by up down out off about above below between through it "
           "its their they them he she his her him you your we our one two some any".split())


def _is_content(w) -> bool:
    return isinstance(w, str) and w.isalpha() and len(w) >= 3 and w.lower() not in STOP


def _toks(s: str) -> List[str]:
    return [w.lower() for w in s.replace("/", " ").replace("-", " ").split() if _is_content(w)]


def _def_bag(word: str, pos: str, hyper_levels: int, use_gloss: bool, use_lemmas: bool,
             use_hyper: bool) -> Counter:
    """Definitional/taxonomic feature bag: gloss+examples (CONTENT) + synonym lemmas + hypernym genus terms up
    `hyper_levels`. Aggregated over the word's synsets, sense-frequency weighted (WordNet order)."""
    poss = POSMAP.get(pos, ("n", "v", "a", "s"))
    syns = [s for p in poss for s in wn.synsets(word, pos=p)] or wn.synsets(word)
    bag: Counter = Counter()
    for si, syn in enumerate(syns):
        w_sense = 1.0 / (1.0 + si)
        f: Counter = Counter()
        if use_gloss:
            f.update(_toks(syn.definition()))
            for ex in syn.examples():
                f.update(_toks(ex))
        if use_lemmas:
            for ln in syn.lemma_names():
                for t in _toks(ln):
                    f[t] += 1
        if use_hyper:
            frontier = [syn]
            for _lvl in range(hyper_levels):
                nxt = []
                for s in frontier:
                    for h in s.hypernyms() + s.instance_hypernyms():
                        for ln in h.lemma_names():
                            for t in _toks(ln):
                                f[t] += 1
                        if use_gloss:
                            f.update(_toks(h.definition()))
                        nxt.append(h)
                frontier = nxt
        for k, v in f.items():
            bag[k] += w_sense * v
    return bag


def build_global_idf() -> Tuple[Dict[str, float], int]:
    """Population-INDEPENDENT distinctive-feature weighting: IDF over ALL WordNet synsets (a token's
    document-frequency = # synsets whose gloss/lemmas/examples contain it). Gold-blind, benchmark-blind.
    EXPENSIVE (one pass over ~117k synsets) -- cache it (see `load_or_build_idf`)."""
    df: Counter = Counter()
    nsyn = 0
    for syn in wn.all_synsets():
        nsyn += 1
        toks = set(_toks(syn.definition()))
        for ex in syn.examples():
            toks |= set(_toks(ex))
        for ln in syn.lemma_names():
            toks |= set(_toks(ln))
        for t in toks:
            df[t] += 1
    idf = {t: math.log(nsyn / c) for t, c in df.items()}
    return idf, nsyn


def load_or_build_idf(cache_path: str = DEFAULT_IDF_CACHE) -> Tuple[Dict[str, float], int]:
    """Load the cached global IDF, building + caching it (offline static asset) on first use."""
    if cache_path and os.path.exists(cache_path):
        with open(cache_path, encoding="utf-8") as fh:
            d = json.load(fh)
        return d["idf"], int(d["nsyn"])
    idf, nsyn = build_global_idf()
    if cache_path:
        os.makedirs(os.path.dirname(cache_path), exist_ok=True)
        tmp = cache_path + ".tmp"
        with open(tmp, "w", encoding="utf-8", newline="") as fh:
            json.dump({"nsyn": nsyn, "idf": idf}, fh)
        os.replace(tmp, cache_path)
    return idf, nsyn


def _sparse_cos(a: Dict[str, float], b: Dict[str, float]) -> Optional[float]:
    if not a or not b:
        return None
    common = set(a) & set(b)
    if not common:
        return 0.0
    num = sum(a[w] * b[w] for w in common)
    da = math.sqrt(sum(x * x for x in a.values()))
    db = math.sqrt(sum(x * x for x in b.values()))
    if da < 1e-12 or db < 1e-12:
        return None
    return num / (da * db)


class ConceptualChannel:
    """The ATL conceptual/definitional meaning hub. `similarity(w1, pos1, w2, pos2)` returns the IDF-weighted
    definitional-feature cosine in [0,1] (None if either word has no WordNet coverage). `weighted=False` gives
    the ATL WRONG-OP (unweighted feature overlap) for control comparisons."""

    def __init__(self, idf: Optional[Dict[str, float]] = None, cfg: Optional[Dict] = None,
                 weighted: bool = True, idf_cache: str = DEFAULT_IDF_CACHE):
        if idf is None:
            idf, _ = load_or_build_idf(idf_cache)
        self.idf = idf
        self.cfg = dict(cfg) if cfg is not None else dict(DEFAULT_CFG)
        self.weighted = weighted   # True = distinctive-feature (IDF); False = unweighted overlap (ATL WRONG-OP)
        self._bag_cache: Dict[Tuple[str, str], Counter] = {}
        self._vec_cache: Dict[Tuple[str, str], Dict[str, float]] = {}

    def bag(self, word: str, pos: str = "N") -> Counter:
        key = (word, pos)
        if key not in self._bag_cache:
            self._bag_cache[key] = _def_bag(word, pos, self.cfg["hyper_levels"], self.cfg["gloss"],
                                            self.cfg["lemmas"], self.cfg["hyper"])
        return self._bag_cache[key]

    def vec(self, word: str, pos: str = "N") -> Optional[Dict[str, float]]:
        key = (word, pos)
        if key in self._vec_cache:
            return self._vec_cache[key] or None
        bag = self.bag(word, pos)
        if self.weighted:
            v = {t: c * self.idf.get(t, 0.0) for t, c in bag.items()} if bag else {}
        else:
            v = {t: float(c) for t, c in bag.items()} if bag else {}
        self._vec_cache[key] = v
        return v or None

    def similarity(self, w1: str, pos1: str, w2: str, pos2: Optional[str] = None) -> Optional[float]:
        """IDF-weighted definitional-feature cosine (meaning-IDENTITY). Returns None if either word is
        out-of-vocabulary in WordNet for the given POS."""
        v1 = self.vec(w1, pos1)
        v2 = self.vec(w2, pos2 if pos2 is not None else pos1)
        if v1 is None or v2 is None:
            return None
        return _sparse_cos(v1, v2)


__all__ = ["ConceptualChannel", "build_global_idf", "load_or_build_idf",
           "DEFAULT_CFG", "DEFAULT_IDF_CACHE", "POSMAP"]
