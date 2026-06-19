"""Substrate-native POS tagger for Phase-2-light Option B Component 1.

Per substrate Tier-A NL primitives (PP-364 POS tagger empirically MIDDLE-HARD-PASS):
- Tier-1: POS tags as phasor atoms
- Tier-3: per-word lexicon vectors (freq-weighted bundle of tag phasors)
- Tag inference: cleanup of word's lexicon vector over Tier-1 tag atoms
- OOV backoff via suffix-feature lexicon (PP-342 wug-mechanism)

This module wraps the technique in a reusable inference primitive:
- SubstratePOSTagger.fit(tagged_sents) trains lexicon
- SubstratePOSTagger.tag(tokens) returns per-token POS tags
- Cached lexicon serializable to numpy file for fast re-load

Used by Phase-2-light Component 1 (Option B) to filter candidates by POS:
only noun-phrase POS classes (NN, NNS, NNP, NNPS, JJ-NN compounds) are
retained as atom-name candidates.

External dep: NLTK PTB sample (~3914 WSJ sentences); free-distribution.
"""
from __future__ import annotations
from collections import defaultdict
from pathlib import Path
from typing import Optional
import math

import numpy as np


# Noun-phrase POS classes per Penn Treebank tagset:
# NN = noun, singular
# NNS = noun, plural
# NNP = proper noun, singular
# NNPS = proper noun, plural
# JJ = adjective (can be NP head modifier)
# CD = cardinal number (sometimes part of NP)
NOUN_POS = {"NN", "NNS", "NNP", "NNPS"}
NP_MODIFIER_POS = {"JJ", "VBN", "VBG", "CD"}  # tokens that can lead noun phrases


def cphasor(m: int, d: int, rng: np.random.Generator) -> np.ndarray:
    """Random complex-phasor codebook of m atoms in d dimensions."""
    ang = (rng.random((m, d)) * 2 - 1) * math.pi
    return np.exp(1j * ang).astype(np.complex64)


def cnorm(v: np.ndarray) -> np.ndarray:
    """Normalize to unit-modulus phasor (preserve phase, kill amplitude)."""
    return np.exp(1j * np.angle(v)).astype(np.complex64)


def _morphological_features(word: str) -> list[str]:
    """Substrate PP-342 wug-mechanism: suffix-based morphological features."""
    wl = word.lower()
    fs = []
    if any(c.isdigit() for c in word):
        fs.append("F:DIGIT")
    if word[:1].isupper():
        fs.append("F:CAP")
    if "-" in word:
        fs.append("F:HYPHEN")
    # Multi-length suffix features
    for k in (2, 3, 4):
        if len(wl) >= k:
            fs.append("S%d:%s" % (k, wl[-k:]))
    return fs


class SubstratePOSTagger:
    """Substrate-native POS tagger via phasor associative recall."""

    def __init__(self, dim: int = 4096, seed: int = 970):
        self.dim = dim
        self.rng = np.random.default_rng(seed)
        self.tags: list[str] = []
        self.tag_to_idx: dict[str, int] = {}
        self.tag_book: Optional[np.ndarray] = None  # (n_tags, dim) complex64
        self.lex: dict[str, np.ndarray] = {}  # word -> normalized phasor vector
        self.feat: dict[str, np.ndarray] = {}  # morphological feature -> vector

    def fit(self, tagged_sents: list[list[tuple[str, str]]]) -> None:
        """Train lexicon from tagged sentences (list of [(word, tag), ...] sentences).

        Builds:
        - Tag phasor codebook
        - Per-word frequency-weighted bundle of tag phasors
        - Per-morphological-feature frequency-weighted bundle
        """
        self.tags = sorted({t for s in tagged_sents for (_w, t) in s})
        self.tag_to_idx = {t: i for i, t in enumerate(self.tags)}
        T = len(self.tags)
        self.tag_book = cphasor(T, self.dim, self.rng)

        word_acc: dict[str, np.ndarray] = defaultdict(
            lambda: np.zeros(self.dim, dtype=np.complex64))
        feat_acc: dict[str, np.ndarray] = defaultdict(
            lambda: np.zeros(self.dim, dtype=np.complex64))

        for sent in tagged_sents:
            for (w, t) in sent:
                wl = w.lower()
                tag_vec = self.tag_book[self.tag_to_idx[t]]
                word_acc[wl] = word_acc[wl] + tag_vec
                for f in _morphological_features(w):
                    feat_acc[f] = feat_acc[f] + tag_vec

        self.lex = {w: cnorm(v) for w, v in word_acc.items()}
        self.feat = {f: cnorm(v) for f, v in feat_acc.items()}

    def predict(self, word: str) -> str:
        """Return the most-likely POS tag for word (substrate associative recall).

        For OOV words, backs off to morphological-feature lexicon.
        """
        if self.tag_book is None:
            return "NN"  # uninitialized
        wl = word.lower()
        if wl in self.lex:
            v = self.lex[wl]
        else:
            # OOV: combine morphological feature evidence
            acc = np.zeros(self.dim, dtype=np.complex64)
            got = False
            for f in _morphological_features(word):
                if f in self.feat:
                    acc = acc + self.feat[f]
                    got = True
            if not got:
                return "NN"  # default for completely unknown words
            v = cnorm(acc)
        return self.tags[int(np.argmax((self.tag_book @ np.conj(v)).real))]

    def tag(self, tokens: list[str]) -> list[tuple[str, str]]:
        """Tag a sequence of tokens; returns list of (token, pos) pairs."""
        return [(t, self.predict(t)) for t in tokens]

    def save(self, path: Path) -> None:
        """Serialize trained lexicon + tag book to npz for fast re-load."""
        if self.tag_book is None:
            raise ValueError("tagger not fitted")
        lex_words = list(self.lex.keys())
        lex_vecs = np.stack([self.lex[w] for w in lex_words])
        feat_keys = list(self.feat.keys())
        feat_vecs = np.stack([self.feat[k] for k in feat_keys]) if feat_keys else np.zeros((0, self.dim), dtype=np.complex64)
        np.savez_compressed(
            path,
            dim=self.dim,
            tags=np.array(self.tags),
            tag_book=self.tag_book,
            lex_words=np.array(lex_words),
            lex_vecs=lex_vecs,
            feat_keys=np.array(feat_keys),
            feat_vecs=feat_vecs,
        )

    @classmethod
    def load(cls, path: Path) -> "SubstratePOSTagger":
        data = np.load(path, allow_pickle=False)
        tagger = cls(dim=int(data["dim"]))
        tagger.tags = list(data["tags"])
        tagger.tag_to_idx = {t: i for i, t in enumerate(tagger.tags)}
        tagger.tag_book = data["tag_book"]
        lex_words = list(data["lex_words"])
        lex_vecs = data["lex_vecs"]
        tagger.lex = {w: lex_vecs[i] for i, w in enumerate(lex_words)}
        feat_keys = list(data["feat_keys"])
        feat_vecs = data["feat_vecs"]
        tagger.feat = {k: feat_vecs[i] for i, k in enumerate(feat_keys)}
        return tagger


_CACHED_TAGGER: Optional[SubstratePOSTagger] = None
_CACHE_PATH = Path("data/substrate_index/substrate_pos_tagger.npz")


def get_default_tagger() -> SubstratePOSTagger:
    """Singleton accessor; trains on PTB sample on first call; cached afterward."""
    global _CACHED_TAGGER
    if _CACHED_TAGGER is not None:
        return _CACHED_TAGGER
    if _CACHE_PATH.exists():
        _CACHED_TAGGER = SubstratePOSTagger.load(_CACHE_PATH)
        return _CACHED_TAGGER

    # Train from PTB sample
    import nltk
    try:
        nltk.data.find("corpora/treebank")
    except LookupError:
        nltk.download("treebank", quiet=True)
    from nltk.corpus import treebank
    sents = [s for s in treebank.tagged_sents() if s]
    tagger = SubstratePOSTagger(dim=4096)
    tagger.fit(sents)
    tagger.save(_CACHE_PATH)
    _CACHED_TAGGER = tagger
    return _CACHED_TAGGER


def is_noun_phrase(tokens: list[str], tagger: Optional[SubstratePOSTagger] = None) -> bool:
    """Permissive noun-phrase heuristic for Phase-2-light filtering.

    Returns True if:
    - At least ONE token is a noun (NN/NNS/NNP/NNPS)
    - AND no token is a definitive non-NP class (VBZ/VBP/VBD/RB/IN-only/CC/PRP/DT-leading-only)
      (NB: VB and VBN allowed since substrate POS often confuses NN/VB)
    - AND no -NONE- tokens (NLTK unknown)
    - Allow IN (preposition) in middle for compound nouns like 'bag of words'
    """
    if tagger is None:
        tagger = get_default_tagger()
    if not tokens:
        return False
    tags = [tagger.predict(t) for t in tokens]
    # Definitive non-NP tokens: present-tense verbs, adverbs, unknowns
    DEFINITIVE_NON_NP = {"VBZ", "VBP", "VBD", "RB", "RBR", "RBS", "MD",
                          "PRP", "PRP$", "WDT", "WP", "WRB", "-NONE-"}
    has_noun = any(t in NOUN_POS for t in tags)
    has_definitive_non_np = any(t in DEFINITIVE_NON_NP for t in tags)
    if not has_noun:
        return False
    if has_definitive_non_np:
        return False
    # Reject if FIRST token is a determiner or conjunction-leading construct
    if tags[0] in ("DT", "CC", "IN"):
        return False
    return True
