"""Glass-box UPOS tagger -- our-own averaged structured perceptron (NO nltk).

Front-end Asset 1 for the reader-parser pipeline. Wraps hdlab.perceptron.StructuredPerceptron
(Collins 2002 averaged perceptron + Viterbi) as a persistable tag(tokens)->UPOS operator so the
reading pipeline gets POS in-substrate + inspectable, with no external nltk dependency.

Public API:
  PosTagger.train(train_seqs, epochs, ...) -> PosTagger      # train from [(word, upos), ...] sequences
  PosTagger.load(path) -> PosTagger                          # load persisted json model
  tagger.save(path)                                          # persist averaged weights + tag set (json = glass-box)
  tagger.tag(tokens) -> list[str]                            # UPOS per token (Viterbi-decoded)
  tagger.evaluate(seqs) -> float                             # token UPOS accuracy

Feature functions are module-level + deterministic so a loaded model decodes identically.
NO LLM. NO nltk. NO torch. numpy + pure-python only.
ASCII-only.
"""
from __future__ import annotations

__bf_status__ = "NOT_BF"   # BF | BF_SPIRIT | NOT_BF | BF_UNPINNED | BF_UNVERIFIED ; mirrors data/bf_status_registry.jsonl
__bf_verified__ = "2026-09-09 operation/math audit (VERIFIED_BF_LEDGER)"
__bf_note__ = "supervised avg-perceptron, frozen, hard Viterbi discards marginals, module-separated; interim asset (POS brain-unpinned)"
__bf_corrections__ = []   # append "YYYY-MM-DD <fix>: OLD -> NEW" when a fix RAISES the status

import json
from typing import List, Sequence, Tuple

import numpy as np

from hdlab.perceptron import StructuredPerceptron

# ======================================================================================================
# DP-HEAD LEXICAL-CATEGORY CORRECTION (landed 2026-09-12 from owner-DONE pri-7
# `harm_help_valence_is_a_fitted_verb_list_not_the_substrates_force_dynamic_arithmetic`, upstream POS fix;
# owner Q131: "confirm mathematically brain-foundational; land top-down" -- see notes/SIGNAL_FLOW_MAP.md §1).
# THE DEFECT: the frozen perceptron mistags rare/OOV common nouns with adjectival shape (medic, intern, civilian)
# as ADJ when they HEAD a determiner phrase; the mistag cascades (the noun cannot attach as the object -> the
# patient / from-clause structure collapses -> harm/help and who-was-affected fail downstream).
# THE COMPUTATION (probabilistic constraint satisfaction over lexical + syntactic constraints; MacDonald,
# Pearlmutter & Seidenberg 1994; Trueswell & Tanenhaus 1994 -- the DP hypothesis: a determiner projects a phrase
# whose head is nominal):   posterior odds  P(NOUN | word, DP-head) / P(ADJ | word, DP-head)
#                          = prior_odds(word) * P(DP-head | NOUN) / P(DP-head | ADJ)
# retag ADJ -> NOUN iff the posterior odds exceed `margin` (1.0 = the Bayes-optimal rule under 0-1 loss; SWEPT in
# the solver's cell, not adopted from elsewhere). Both terms are a PERSISTED offline asset
# (data/frontend_assets/pos_dp_head_bayes_ud_ewt.json, built once by tools/build_pos_dp_head_bayes_asset.py from
# UD-EWT train: 8826 lexical entries, syn_lr 8.08) -- never a treebank read at inference. The word must have a
# noun reading (WordNet lexical-category knowledge = the mental lexicon; an admissible offline foundation queried
# at read-time -- the same residual class as pri-12, recorded not expanded). Absent asset -> no-op, stated.
# MEASURED (solver, reverified 6/6): target DP-head-ADJ population recall 0.40 -> 0.70 at the Bayes margin, the
# info-free random-retag control loses on both axes; downstream "blocked the medic from saving" recovers
# HELP->HARM; "bullied the intern" recovers HARM only when this AND the harm/help arithmetic are both live.
# Global UPOS accuracy moves 0.94198 -> 0.94208 (the mistag is rare in-distribution; the value is the cascade).
# ======================================================================================================
import os as _os

DP_HEAD_CORRECTION: bool = True          # the LIVE default (owner-DONE; measured net-positive downstream)
_DP_ASSET = _os.path.join(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))),
                          "data", "frontend_assets", "pos_dp_head_bayes_ud_ewt.json")


def is_dp_head(upos: Sequence[str], i: int) -> bool:
    """Token i heads a determiner phrase: a DET precedes (skipping ADJ/ADV) and no NOUN/PROPN follows within the
    phrase (so this token is the head, not a prenominal modifier)."""
    j = i - 1
    while j >= 0 and upos[j] in ("ADJ", "ADV"):
        j -= 1
    if j < 0 or upos[j] != "DET":
        return False
    k = i + 1
    while k < len(upos) and upos[k] in ("ADJ", "ADV"):
        k += 1
    return not (k < len(upos) and upos[k] in ("NOUN", "PROPN"))


class DPHeadCategoryCorrection:
    """Bayesian DP-head ADJ->NOUN retag (see the block above). One instance per process (lazy asset load)."""
    _inst = None

    def __init__(self, asset_path: str = _DP_ASSET) -> None:
        self.asset_path = asset_path
        self.ok = False
        self.lex: dict = {}
        self.syn_lr = 1.0
        self.margin = 1.0
        self.min_evidence = 3
        self._noun_reading: dict = {}
        self.stats = {"checked": 0, "retagged": 0}
        try:
            with open(asset_path, encoding="utf-8") as f:
                d = json.load(f)
            self.lex = d["lex"]; self.syn_lr = float(d["syn_lr"]); self.margin = float(d.get("margin", 1.0))
            self.min_evidence = int(d.get("min_train_evidence", 3)); self.ok = True
        except Exception:
            self.ok = False                                   # absent asset -> the correction is a stated no-op

    @classmethod
    def get(cls) -> "DPHeadCategoryCorrection":
        if cls._inst is None:
            cls._inst = cls()
        return cls._inst

    def _has_noun_reading(self, word: str) -> bool:
        w = word.lower()
        if w in self._noun_reading:
            return self._noun_reading[w]
        try:
            from nltk.corpus import wordnet as wn
            ok = len(wn.synsets(w, pos=wn.NOUN)) >= 1
        except Exception:
            ok = True
        self._noun_reading[w] = ok
        return ok

    def prior_odds(self, word: str) -> float:
        """P(NOUN|word)/P(ADJ|word): train counts (+1) when >= min_evidence observations, else the WordNet
        noun-vs-adjective sense counts (+1) -- the mental lexicon's category knowledge as backoff."""
        w = word.lower()
        c = self.lex.get(w)
        n = (c[0] if c else 0) + 1.0
        a = (c[1] if c else 0) + 1.0
        if c and (c[0] + c[1]) >= self.min_evidence:
            return n / a
        try:
            from nltk.corpus import wordnet as wn
            return (len(wn.synsets(w, pos=wn.NOUN)) + 1.0) / (len(wn.synsets(w, pos=wn.ADJ)) + 1.0)
        except Exception:
            return n / a

    def apply(self, tokens: Sequence[str], upos: Sequence[str]) -> List[str]:
        if not self.ok:
            return list(upos)
        out = list(upos)
        for i, t in enumerate(upos):
            if t != "ADJ" or not is_dp_head(upos, i):
                continue
            self.stats["checked"] += 1
            if not self._has_noun_reading(tokens[i]):
                continue
            if self.prior_odds(tokens[i]) * self.syn_lr > self.margin:
                out[i] = "NOUN"; self.stats["retagged"] += 1
        return out


def pos_features(obs: Sequence[str], i: int, tag: str) -> List[str]:
    """Emission features for token i under candidate `tag`. Ratnaparkhi/Collins-style; word + affix + shape + context."""
    w = obs[i]
    wl = w.lower()
    feats = ["b~" + tag, "w:" + wl + "~" + tag]
    L = len(wl)
    for k in (1, 2, 3, 4):
        if L >= k:
            feats.append("suf%d:%s~%s" % (k, wl[-k:], tag))
            feats.append("pre%d:%s~%s" % (k, wl[:k], tag))
    if w[:1].isupper():
        feats.append("cap~" + tag)
    if any(c.isdigit() for c in w):
        feats.append("hasdig~" + tag)
    if "-" in w:
        feats.append("hyph~" + tag)
    if i > 0:
        feats.append("pw:" + obs[i - 1].lower() + "~" + tag)
    else:
        feats.append("BOS~" + tag)
    if i + 1 < len(obs):
        feats.append("nw:" + obs[i + 1].lower() + "~" + tag)
    else:
        feats.append("EOS~" + tag)
    return feats


def pos_transition(prev_tag: str, cur_tag: str) -> str:
    """Transition feature string prev->cur (includes <S> start pseudo-tag)."""
    return "tt:" + prev_tag + "~" + cur_tag


def token_bases(obs: Sequence[str], i: int) -> List[str]:
    """The TAG-INDEPENDENT part of pos_features(obs,i,tag), in the EXACT emit order (drop the ~tag).

    Mirrors pos_features line-for-line: b, w:, (suf/pre 1..4), cap, hasdig, hyph, pw:/BOS, nw:/EOS.
    Preserving the order => re-suffixing each base with ~tag reproduces pos_features's feature strings
    => identical dict values in identical sum order => byte-identical emission scores. Promoted verbatim
    from experiments/exp_pos_tagger_fastfeat_v1.py.
    """
    w = obs[i]
    wl = w.lower()
    bases = ["b", "w:" + wl]
    L = len(wl)
    for k in (1, 2, 3, 4):
        if L >= k:
            bases.append("suf%d:%s" % (k, wl[-k:]))
            bases.append("pre%d:%s" % (k, wl[:k]))
    if w[:1].isupper():
        bases.append("cap")
    if any(c.isdigit() for c in w):
        bases.append("hasdig")
    if "-" in w:
        bases.append("hyph")
    if i > 0:
        bases.append("pw:" + obs[i - 1].lower())
    else:
        bases.append("BOS")
    if i + 1 < len(obs):
        bases.append("nw:" + obs[i + 1].lower())
    else:
        bases.append("EOS")
    return bases


class _FastEmissionPlan:
    """Byte-identical variant-C fast emission plan for the POS tagger, promoted verbatim from
    experiments/exp_pos_tagger_fastfeat_v1.py (FastTagger). Built ONCE from the averaged weights:

      * base_contrib: base -> [(tag_idx, weight)]   (emission keys split on the LAST '~'; 'tt:' = transition)
      * TM [n_tags x n_tags] + SV [n_tags]: precomputed transition potentials (constant given the weights),
        built via pos_transition so they are bit-identical to the stock per-sentence rebuild.

    emission(obs, n) collects the PRESENT weights per tag lane IN BASE ORDER, then sum()s each lane with
    the SAME built-in sum() the stock path uses -- so CPython's Neumaier-compensated reduction is
    bit-identical (dropping the 0.0-default terms is a no-op inside the compensated sum). The witness
    asserts the whole emission matrix np.array_equal to the reference, precisely to guard this.
    """

    def __init__(self, weights, tags, transition_fn):
        self.weights = weights            # identity guard: fast path fires only when _viterbi is passed THIS dict
        self.tags = list(tags)
        self.n_tags = len(self.tags)
        ti = {t: i for i, t in enumerate(self.tags)}
        self.base_contrib = {}            # base -> list[(tag_idx, weight)]
        for key, val in weights.items():
            if key.startswith("tt:"):
                continue
            base, tag = key.rsplit("~", 1)
            k = ti[tag]
            self.base_contrib.setdefault(base, []).append((k, val))
        self.TM = np.array([[weights.get(transition_fn(self.tags[j], self.tags[k]), 0.0)
                             for k in range(self.n_tags)] for j in range(self.n_tags)])
        self.SV = np.array([weights.get(transition_fn("<S>", self.tags[k]), 0.0)
                            for k in range(self.n_tags)])

    def emission(self, obs, n):
        """Sparse per-lane emission matrix (variant C), byte-identical to the stock full-sum build.
        The per-lane lists are allocated ONCE per sentence and cleared per token (reuse avoids realloc)."""
        nt = self.n_tags
        bc = self.base_contrib
        perlane = [[] for _ in range(nt)]
        em = np.empty((n, nt))
        for i in range(n):
            for lst in perlane:
                lst.clear()
            for base in token_bases(obs, i):
                c = bc.get(base)
                if c is not None:
                    for k, w in c:
                        perlane[k].append(w)
            row = em[i]
            for k in range(nt):
                row[k] = sum(perlane[k])   # sum([]) == 0 -> +0.0, matching stock's all-0.0 lane
        return em


class PosTagger:
    """Persistable UPOS tagger over the averaged structured perceptron."""

    def __init__(self, tags: Sequence[str], perceptron: StructuredPerceptron):
        self.tags = list(tags)
        self._perc = perceptron
        self._fast: "_FastEmissionPlan | None" = None  # byte-identical variant-C plan, built lazily on first tag

    @classmethod
    def train(
        cls,
        train_seqs: Sequence[Sequence[Tuple[str, str]]],
        epochs: int = 6,
        rng_seed: int = 1024,
        tags: Sequence[str] | None = None,
    ) -> "PosTagger":
        """Train from sequences of (word, upos) pairs. Returns a fitted PosTagger."""
        if tags is None:
            tags = sorted({t for s in train_seqs for _, t in s})
        perc = StructuredPerceptron(tags, rng_seed=rng_seed)
        perc.fit(list(train_seqs), pos_features, pos_transition, epochs=epochs)
        return cls(tags, perc)

    def tag(self, tokens: Sequence[str], *, dp_head_correction: "bool | None" = None) -> List[str]:
        """UPOS tag per token via Viterbi under averaged weights (byte-identical variant-C fast path), then the
        Bayesian DP-head lexical-category correction (module default DP_HEAD_CORRECTION; pass False for the raw
        perceptron tags)."""
        self._ensure_fast()
        tags = self._perc.predict(list(tokens), pos_features, pos_transition)
        use = DP_HEAD_CORRECTION if dp_head_correction is None else dp_head_correction
        return DPHeadCategoryCorrection.get().apply(list(tokens), tags) if use else tags

    def _ensure_fast(self) -> "_FastEmissionPlan":
        """Lazily build + attach the variant-C fast emission plan (byte-identical). Idempotent.

        The plan is built from self._perc.weights (the averaged dict) and attached to the perceptron;
        _viterbi then fires the fast path whenever it is handed that same dict (inference), while
        training (fit) -- which uses the raw weights -- stays on the stock reference."""
        if self._fast is None:
            self._fast = _FastEmissionPlan(self._perc.weights, self.tags, pos_transition)
            self._perc.set_fast_emission(self._fast)
        return self._fast

    def _emission_fast(self, tokens: Sequence[str]) -> "np.ndarray":
        """Variant-C fast emission matrix (pure-hdlab byte-identity witness hook)."""
        obs = list(tokens)
        return self._ensure_fast().emission(obs, len(obs))

    def _emission_reference(self, tokens: Sequence[str]) -> "np.ndarray":
        """Stock emission matrix -- the byte-identity REFERENCE (pure-hdlab witness hook)."""
        obs = list(tokens)
        return self._perc._emission_reference(obs, self._perc.weights, pos_features)

    def _tag_reference(self, tokens: Sequence[str]) -> List[str]:
        """Stock Collins-Viterbi tags (UNCHANGED reference path). Pure-hdlab witness hook + fair-timing floor."""
        return self._perc._viterbi_reference(list(tokens), self._perc.weights, pos_features, pos_transition)

    def evaluate(self, seqs: Sequence[Sequence[Tuple[str, str]]]) -> Tuple[float, int, int]:
        """Token UPOS accuracy over gold (word, upos) sequences. Returns (acc, n_correct, n_tokens)."""
        c = 0
        t = 0
        for s in seqs:
            obs = [w for w, _ in s]
            gold = [g for _, g in s]
            pred = self.tag(obs)
            for p, g in zip(pred, gold):
                c += int(p == g)
                t += 1
        return (c / t if t else 0.0, c, t)

    def save(self, path: str) -> None:
        """Persist averaged weights + tag set to json (glass-box, inspectable)."""
        payload = {"tags": self.tags, "weights": self._perc.weights}
        with open(path, "w", encoding="utf-8") as f:
            json.dump(payload, f)

    @classmethod
    def load(cls, path: str) -> "PosTagger":
        """Load a persisted json model; decodes identically to the trained tagger."""
        with open(path, encoding="utf-8") as f:
            d = json.load(f)
        perc = StructuredPerceptron(d["tags"])
        perc._averaged = {k: float(v) for k, v in d["weights"].items()}
        return cls(d["tags"], perc)
