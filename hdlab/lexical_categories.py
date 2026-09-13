"""hdlab/lexical_categories.py -- the CATEGORY organ's graded readout: a GENERATIVE count-based category model (HMM) settled
by forward-backward into a per-token POSTERIOR over categories. Landed 2026-09-12 (strategy) from the owner-DONE pri-12 solver's
prototype `experiments/glassbox_pos_bayes.py` (computation verbatim; vectorised; plastic counts; save/load), at the owner's
direction: "when we identify an important step in the right direction we should take those steps even if it causes short-term pain".

BRAIN COMPUTATION (PINNED at the computational level):
  lexical association   P(word | category)      = frequency COUNTS (Hebbian accrual; online-updatable)
  morpho-orthographic   P(suffix | category)     = last-1..4-character suffix counts -- the unknown-word cue (the form cue the
                                                   reading-induced categories rung also uses: -ing / -ly / -tion)
  sequential prediction P(category | previous)   = bigram transition counts (Christiansen & Chater sequence prediction)
  combined GENERATIVELY (Bayes) and settled by forward-backward (MacDonald 1994 constraint satisfaction; Kuperberg & Jaeger 2016
  graded predictive belief) -> a DISTRIBUTION over categories per token, handed DOWN (the heads rung can marginalise over it).
  argmax of the posterior is the point readout for consumers that insist on a tag.
MODEL (honest label): the category INVENTORY and the counts' SOURCE. Today the counts are accrued from the UD-EWT training
sentences' tag column = an OFFLINE FOUNDATION supply (admissible, like WordNet) standing in for the brain's UNSUPERVISED
distributional acquisition; the inventory is swappable: when the reading-induced categories rung (pri-15) hands down a usable
class inventory, the SAME organ accrues counts over those classes (`accrue` takes any (word, class) stream). No gradient, no
likelihood optimisation, no external tool at inference. Replaces the live `pos_tagger` (NOT_BF max-margin perceptron).
KNOWLEDGE FORM (plastic, never frozen): counts in the asset (emission / suffix / transition); log-probabilities are ONE pure
function of the counts (`finalize`); `observe(words, categories)` accrues online; `save` / `load`.
Glass-box, numpy only.
"""
from __future__ import annotations

import json
import math
import os
from collections import Counter, defaultdict
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

__bf_status__ = "BF_SPIRIT"   # BF | BF_SPIRIT | NOT_BF | BF_UNPINNED | BF_UNVERIFIED ; mirrors notes/bf_status_registry.jsonl
__bf_verified__ = ("2026-09-12 strategy landing of the owner-DONE pri-12 solver's BF POS prototype (glassbox_pos_bayes): generative "
                   "count-based category model + forward-backward graded posterior (no gradient, no tool at inference); INFERENCE pinned, "
                   "ACQUISITION = offline labelled supply until the induced-categories rung hands down its inventory")
__bf_note__ = "the inventory/counts source is the remaining MODEL element; swap to induced classes when pri-15 lands"

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSET = os.path.join(_REPO, "data", "frontend_assets", "lexical_categories_counts_v1.json")
_lag_env = os.environ.get("HDLAB_LC_LAG", "")
# DEFAULT LAG = 2 (2026-09-13 10:35 local; owner: organs take data IN ORDER): the belief about a word is revised by the next TWO words
# only. Full UD-EWT test: lag 0 0.9032 | 1 0.9251 | 2 0.9264 | 3 0.9264 | whole sentence 0.9264 -- a two-word window is exactly as
# accurate as reading the whole sentence first, so the brain-faithful form replaces the stand-in. HDLAB_LC_LAG=inf restores smoothing.
_mm = os.environ.get("HDLAB_LC_MIX_MAX", "")
MIX_MAX: Optional[int] = int(_mm) if _mm.strip() else None          # None = the asset's rare_max (current behaviour); sweep below
MIX_KAPPA = float(os.environ.get("HDLAB_LC_MIX_KAPPA", "1.0"))
# STEM-INFORMED PRIOR for KNOWN-BUT-RARE forms (2026-09-13 13:10; the 'wounded' -> ADP miss): the lemma organ's RULE route
# decomposes an inflected form into stem + inflection (wounded = wound + -ed; words-and-rules, Pinker & Ullman). The form's
# category is then predicted from the STEM's known categories and the inflection -- a table P(form category | stem category,
# inflection) accrued from the organ's own vocabulary counts (no labels beyond the supply it already has). A form seen a few times
# under one tag keeps its other readings alive through its stem. Mixing weight a = c / (c + kappa) for c <= STEM_MIX_MAX (swept).
_smm = os.environ.get("HDLAB_LC_STEM_MIX_MAX", "")
STEM_MIX_MAX: int = int(_smm) if _smm.strip() else 0          # 0 = off (current behaviour); sweep below
STEM_KAPPA = float(os.environ.get("HDLAB_LC_STEM_KAPPA", "1.0"))
# CONFLICT-TRIGGERED STEM REANALYSIS (2026-09-13 13:20; DEFAULT ON): full UD-EWT test 0.9264 -> 0.9271, known-rare slice 0.872 -> 0.878,
# "wounded" -> VERB; the blanket stem prior was -0.07 to -0.5 points (kept OFF). HDLAB_LC_STEM_REANALYSIS=0 disables.
STEM_REANALYSIS = os.environ.get("HDLAB_LC_STEM_REANALYSIS", "1") == "1"
LAG: Optional[int] = (None if _lag_env.strip().lower() in ("inf", "none", "full") else int(_lag_env)) if _lag_env.strip() else 2
BOS = "<s>"
K2 = 2.0                                                        # Dirichlet back-off mass for the second-order transitions (swept, not adopted)
SHAPES = ("lower", "Cap", "ALLCAP", "digit", "hyphen", "other")
INDUCED_ASSET = os.path.join(_REPO, "data", "frontend_assets", "induced_categories_simplewiki_1m_k68.json")   # the reading-acquired classes


def word_shape(w: str) -> str:
    if any(ch.isdigit() for ch in w):
        return "digit"
    if "-" in w and any(ch.isalpha() for ch in w):
        return "hyphen"
    if w.isalpha():
        if w.islower():
            return "lower"
        if w.isupper():
            return "ALLCAP" if len(w) > 1 else "Cap"
        if w[0].isupper() and w[1:].islower():
            return "Cap"
    return "other"
UPOS2WN = {"NOUN": "n", "VERB": "v", "ADJ": "a", "ADV": "r"}


class LexicalCategories:
    """Generative count-based category model with forward-backward posterior decoding (plastic counts)."""

    def __init__(self, lam: float = 0.1, suf_len: int = 4, order: int = 1, use_shape: bool = False, rare_max: int = 2,
                 use_cluster: bool = False):
        self.lam = float(lam); self.suf_len = int(suf_len)
        # ARM v2 (2026-09-13 07:05 local; same count-based generative model, three more count tables, all plastic):
        #   order=2      second-order transitions P(c | p2, p1) with Dirichlet back-off to the first-order row (the brain's sequence
        #                prediction is not one-step-Markov; the forward-backward runs over category PAIRS);
        #   use_shape    an ORTHOGRAPHIC-SHAPE emission factor P(shape | c) (capitalised / all-caps / digit / hyphenated / lower / other),
        #                read from the original casing -- the cue the lowercased lexical table throws away (proper nouns, numbers);
        #   rare_max     a known word seen <= rare_max times mixes its lexical emission with the unknown-word (suffix + shape) estimate
        #                in proportion to its count (a rare form's category evidence is mostly its shape and ending).
        # order=1 / use_shape=False reproduces v1 exactly (old assets load that way).
        self.order = int(order); self.use_shape = bool(use_shape); self.rare_max = int(rare_max)
        #   use_cluster  (07:40 local) a READING-ACQUIRED emission cue: the distributional class of the word in the induced inventory
        #                (`induced_categories_simplewiki_1m_k68.json`, 20k word types -> 70 clusters grown from raw text) as a factor
        #                P(cluster | c) for RARE and UNKNOWN words -- the organ's own reading arm informing its supervised arm
        #                (a word never seen in the tag supply but read 1m times in simplewiki still has a class).
        self.use_cluster = bool(use_cluster)
        self.clus: Dict[str, Counter] = defaultdict(Counter)       # category -> Counter(cluster id)
        self._w2c: Optional[Dict[str, str]] = None
        self.shape: Dict[str, Counter] = defaultdict(Counter)      # category -> Counter(shape class)
        self.trans2: Dict[Tuple[str, str], Counter] = defaultdict(Counter)   # (prev2, prev1) -> Counter(category)
        self.emit: Dict[str, Counter] = defaultdict(Counter)       # category -> Counter(word)
        self.tag_count: Counter = Counter()
        self.trans: Dict[str, Counter] = defaultdict(Counter)      # prev category (or BOS) -> Counter(category)
        self.suf: Dict[int, Dict[str, Counter]] = {k: defaultdict(Counter) for k in range(1, self.suf_len + 1)}
        self.suf_tot: Dict[int, Counter] = {k: Counter() for k in range(1, self.suf_len + 1)}
        self.vocab: set = set()
        self.tags: List[str] = []; self.tag_idx: Dict[str, int] = {}
        self.log_trans: Optional[np.ndarray] = None
        self._dirty = True

    # ------------------------------------------------------------------ plastic knowledge: counts
    def accrue(self, sentences: Sequence[Sequence[Tuple[str, str]]]) -> "LexicalCategories":
        """Accrue counts from (word, category) sequences (offline supply OR the induced-categories stream OR online outcomes)."""
        for sent in sentences:
            prev = BOS; prev2 = BOS
            for w_raw, t in sent:
                w = w_raw.lower()
                self.emit[t][w] += 1; self.tag_count[t] += 1; self.vocab.add(w); self.trans[prev][t] += 1
                self.shape[t][word_shape(w_raw)] += 1; self.trans2[(prev2, prev)][t] += 1
                if self.use_cluster:
                    c = self.word2cluster().get(w)
                    if c is not None:
                        self.clus[t][c] += 1
                for k in range(1, self.suf_len + 1):
                    if len(w) >= k:
                        self.suf[k][t][w[-k:]] += 1; self.suf_tot[k][w[-k:]] += 1
                prev2 = prev; prev = t
        self._dirty = True
        return self

    def observe(self, words: Sequence[str], categories: Sequence[str]) -> None:
        """ONLINE accrual of one confirmed categorisation (a comprehension outcome) -- the plastic path."""
        self.accrue([list(zip(words, categories))])
        self.finalize()

    def finalize(self) -> "LexicalCategories":
        """Log-probabilities as ONE pure function of the counts."""
        self.tags = sorted(self.tag_count); self.tag_idx = {t: i for i, t in enumerate(self.tags)}
        T = len(self.tags); lt = np.full((T + 1, T), -1e9)
        for pi, p in enumerate([BOS] + self.tags):
            tot = sum(self.trans[p].values()) + self.lam * T
            for ci, c in enumerate(self.tags):
                lt[pi, ci] = math.log((self.trans[p][c] + self.lam) / tot)
        self.log_trans = lt
        if self.order >= 2:
            # P(c | p2, p1) = (n(p2,p1,c) + k * P(c | p1)) / (n(p2,p1) + k): Dirichlet back-off to the first-order row, k = K2
            states = [BOS] + self.tags; S = len(states); lt2 = np.full((S, S, T), -1e9)
            for ai, a in enumerate(states):
                for bi, b in enumerate(states):
                    row = self.trans2.get((a, b)); nb = sum(row.values()) if row else 0
                    base = lt[bi]                                    # log P(c | b) (row bi of the first-order table; BOS row = 0)
                    for ci in range(T):
                        cnt = row[self.tags[ci]] if row else 0
                        lt2[ai, bi, ci] = math.log((cnt + K2 * math.exp(base[ci])) / (nb + K2))
            self.log_trans2 = lt2
        if self.use_cluster:
            ncl = max(1, len(set(self.word2cluster().values())))
            self.log_clus = {}
            for t in self.tags:
                tot = sum(self.clus[t].values()) + self.lam * ncl
                self.log_clus[t] = (self.clus[t], tot, ncl)
        if self.use_shape:
            self.log_shape = {}
            for t in self.tags:
                tot = self.tag_count[t] + self.lam * len(SHAPES)
                self.log_shape[t] = {sh: math.log((self.shape[t][sh] + self.lam) / tot) for sh in SHAPES}
        self._dirty = False
        return self

    # ------------------------------------------------------------------ inference: graded posterior
    def _log_emit(self, word: str) -> np.ndarray:
        T = len(self.tags); out = np.empty(T); w = word.lower(); V1 = len(self.vocab) + 1
        if w in self.vocab:
            for i, t in enumerate(self.tags):
                out[i] = math.log((self.emit[t][w] + self.lam) / (self.tag_count[t] + self.lam * V1))
            cw = sum(self.emit[t][w] for t in self.tags)
            # a rare known form: mix the lexical estimate with the unknown-word (suffix/shape) estimate in proportion to its count
            # -- Bayesian shrinkage a = c / (c + kappa): three sightings of "wounded" as ADJ must not make VERB impossible
            # (measured 2026-09-13: "An attacker wounded the officer" -> ADP; the lexical floor for VERB lost to the NOUN _ DET
            # sequence). MIX_MAX / MIX_KAPPA are swept operating points (module defaults below); the reading-cluster factor keeps
            # its own threshold (rare_max) -- applying it to every word costs 2 points (measured).
            mix_max = self.rare_max if MIX_MAX is None else MIX_MAX
            sp = self._log_stem_prior(w) if (STEM_MIX_MAX > 0 and cw <= STEM_MIX_MAX) else None
            if sp is not None:
                a = cw / (cw + STEM_KAPPA)
                out = np.logaddexp(math.log(a) + out, math.log(1.0 - a) + sp)
            elif mix_max > 0 and cw <= mix_max:
                unk = self._log_emit_unknown(w); a = cw / (cw + MIX_KAPPA)
                out = np.logaddexp(math.log(a) + out, math.log(1.0 - a) + unk)
            if self.rare_max > 0 and cw <= self.rare_max:
                out = out + self._log_cluster(w)
            if self.use_shape:
                sh = word_shape(word)
                out = out + np.array([self.log_shape[t][sh] for t in self.tags])
            return out
        out = self._log_emit_unknown(w) + self._log_cluster(w)
        if self.use_shape:
            sh = word_shape(word)
            out = out + np.array([self.log_shape[t][sh] for t in self.tags])
        return out

    def word2cluster(self) -> Dict[str, str]:
        if self._w2c is None:
            try:
                with open(INDUCED_ASSET, encoding="utf-8") as f:
                    self._w2c = {k.lower(): str(v) for k, v in json.load(f)["word2cat"].items()}
            except Exception:
                self._w2c = {}
        return self._w2c

    _STEM_TAB = None          # {(stem_majority_tag, route_key): np.array counts over tags}
    _MORPH = None

    @staticmethod
    def _route_key(w: str, pos_letter: str) -> str:
        for suf in ("ies", "ied", "ing", "est", "ed", "es", "er", "s", "d"):
            if w.endswith(suf) and len(w) > len(suf) + 1:
                return pos_letter + ":" + suf
        return pos_letter

    def _decompose(self, w: str):
        """(stem, route_key) via the lemma organ's rule route, or None. The stem must be a KNOWN word of this organ."""
        if LexicalCategories._MORPH is None:
            try:
                from hdlab.morphology import default_morphology
                LexicalCategories._MORPH = default_morphology()
            except Exception:
                LexicalCategories._MORPH = False
        m = LexicalCategories._MORPH
        if not m:
            return None
        for pl in ("v", "n", "a"):
            try:
                base = m.morphy(w, pl)
            except Exception:
                base = None
            if base and base != w and base in self.vocab:
                return base, self._route_key(w, pl)
        return None

    def _stem_table(self) -> dict:
        """P(form tag | stem majority tag, route) accrued from the organ's OWN vocabulary counts (built once per process)."""
        if LexicalCategories._STEM_TAB is None:
            T = len(self.tags); tab: dict = {}
            maj = {}
            for w in self.vocab:
                cnts = np.array([self.emit[t][w] for t in self.tags], dtype=float)
                if cnts.sum() > 0:
                    maj[w] = self.tags[int(cnts.argmax())]
            for w in self.vocab:
                d = self._decompose(w)
                if d is None:
                    continue
                stem, rk = d
                key = (maj.get(stem), rk)
                if key[0] is None:
                    continue
                row = tab.setdefault(key, np.zeros(T))
                for i, t in enumerate(self.tags):
                    row[i] += self.emit[t][w]
            LexicalCategories._STEM_TAB = tab
        return LexicalCategories._STEM_TAB

    def _log_stem_prior(self, w: str):
        d = self._decompose(w)
        if d is None:
            return None
        stem, rk = d
        cnts = np.array([self.emit[t][stem] for t in self.tags], dtype=float)
        if cnts.sum() == 0:
            return None
        key = (self.tags[int(cnts.argmax())], rk)
        row = self._stem_table().get(key)
        if row is None or row.sum() < 5:
            return None
        T = len(self.tags)
        return np.log((row + self.lam) / (row.sum() + self.lam * T))

    def _log_cluster(self, w: str) -> np.ndarray:
        """log P(cluster(w) | c) over categories, or zeros when the word has no reading-induced class / the arm is off."""
        T = len(self.tags)
        if not self.use_cluster:
            return np.zeros(T)
        c = self.word2cluster().get(w)
        if c is None:
            return np.zeros(T)
        out = np.empty(T)
        for i, t in enumerate(self.tags):
            cnt, tot, ncl = self.log_clus[t]
            out[i] = math.log((cnt[c] + self.lam) / tot)
        return out

    def _log_emit_unknown(self, w: str) -> np.ndarray:
        T = len(self.tags); out = np.empty(T)
        suf_used = None
        for k in range(self.suf_len, 0, -1):                      # unknown word: the longest suffix seen
            if len(w) >= k and self.suf_tot[k][w[-k:]] > 0:
                suf_used = k; break
        total = sum(self.tag_count.values())
        for i, t in enumerate(self.tags):
            if suf_used is not None:
                s = w[-suf_used:]
                out[i] = math.log((self.suf[suf_used][t][s] + self.lam) / (self.suf_tot[suf_used][s] + self.lam * T))
            else:
                out[i] = math.log((self.tag_count[t] + self.lam) / (total + self.lam * T))
        return out

    def posterior(self, words: Sequence[str], lag: Optional[int] = None) -> np.ndarray:
        """Forward-backward marginals P(category_i | words): [n, T].
        lag (2026-09-13, owner: organs take data IN ORDER): the belief about word i may use only the words up to i + lag -- lag 0 is
        the running (filtered) belief the reader holds the moment a word arrives, a small lag is revision within a short window as
        the next words come in (reanalysis), None = the whole sentence (smoothing; the offline stand-in). Module default LAG."""
        if lag is None:
            lag = LAG
        if self._dirty:
            self.finalize()
        n = len(words); T = len(self.tags)
        if n == 0:
            return np.zeros((0, T))
        le = np.stack([self._log_emit(w) for w in words])
        post = self._posterior_le(le, lag)
        if STEM_REANALYSIS:
            # CONFLICT-TRIGGERED REANALYSIS (2026-09-13): a known word whose settled category has ZERO lexical support (the sequence
            # cue forced a tag the word was never seen under) is re-read with its STEM's knowledge (the lemma organ's rule route:
            # wounded = wound + -ed -> VERB/ADJ), and the sentence is settled again. Fires only on conflicts (rare), so the blanket
            # prior's dilution (measured -0.1 to -0.5 points) is avoided.
            changed = False
            for k, w in enumerate(words):
                wl = w.lower()
                if wl in self.vocab:
                    t_star = self.tags[int(post[k].argmax())]
                    if self.emit[t_star][wl] == 0:
                        sp = self._log_stem_prior(wl)
                        if sp is not None:
                            cw = sum(self.emit[t][wl] for t in self.tags); a = cw / (cw + STEM_KAPPA)
                            le[k] = np.logaddexp(math.log(a) + le[k], math.log(1.0 - a) + sp); changed = True
            if changed:
                post = self._posterior_le(le, lag)
        return post

    def _posterior_le(self, le: np.ndarray, lag: Optional[int]) -> np.ndarray:
        n, T = le.shape
        if self.order >= 2:
            return self._posterior2(le, lag=lag)
        A = self.log_trans[1:]                                    # [T_prev, T_cur]
        fwd = np.empty((n, T)); fwd[0] = self.log_trans[0] + le[0]
        for i in range(1, n):
            m = fwd[i - 1][:, None] + A                           # [T_prev, T_cur]
            mx = m.max(axis=0); fwd[i] = mx + np.log(np.exp(m - mx).sum(axis=0)) + le[i]
        if lag is not None and lag < n - 1:
            # FIXED-LAG revision: the belief about word i reads the evidence of words i+1 .. i+lag only (a backward message started
            # at zero from position min(n-1, i+lag)); the forward pass is the running belief. Same numbers as recomputing the prefix
            # (witness), n x lag backward steps instead of n^2.
            bwd = np.zeros((n, T))
            for i in range(n - 1):
                end = min(n - 1, i + lag); b = np.zeros(T)
                for k in range(end - 1, i - 1, -1):
                    m = A + (le[k + 1] + b)[None, :]
                    mx = m.max(axis=1); b = mx + np.log(np.exp(m - mx[:, None]).sum(axis=1))
                bwd[i] = b
        else:
            bwd = np.zeros((n, T))
            for i in range(n - 2, -1, -1):
                m = A + (le[i + 1] + bwd[i + 1])[None, :]            # [T_prev, T_cur]
                mx = m.max(axis=1); bwd[i] = mx + np.log(np.exp(m - mx[:, None]).sum(axis=1))
        post = fwd + bwd; post -= post.max(axis=1, keepdims=True)
        post = np.exp(post); post /= post.sum(axis=1, keepdims=True)
        return post

    def _posterior2(self, le: np.ndarray, lag: Optional[int] = None) -> np.ndarray:
        """Second-order forward-backward. State at position i = (category_{i-1}, category_i) with index (b, c); b = BOS (index 0 of
        the state axis) at i = 0. log_trans2[a, b, c] = log P(c | a, b) over states [BOS]+tags."""
        n, T = le.shape; L2 = self.log_trans2                      # [S, S, T], S = T + 1 (BOS first)
        NEG = -1e9
        # fwd[i][b, c]: b over S (prev category incl. BOS), c over T
        fwd = np.full((n, T + 1, T), NEG)
        fwd[0][0, :] = L2[0, 0, :] + le[0]                        # (BOS, BOS) -> c
        for i in range(1, n):
            # new state (b, c) from old state (a, b): sum over a of fwd[i-1][a, b] + L2[a, b+1, c]
            prev = fwd[i - 1]                                     # [S(a), T(b)]
            m = prev[:, :, None] + L2[:, 1:, :]                   # [S(a), T(b), T(c)]
            mx = m.max(axis=0); cur = mx + np.log(np.exp(m - mx).sum(axis=0))   # [T(b), T(c)]
            fwd[i][1:, :] = cur + le[i][None, :]
        bwd = np.zeros((n, T + 1, T))
        if lag is not None and lag < n - 1:
            # fixed-lag revision (see posterior): backward message over words i+1 .. i+lag only
            for i in range(n - 1):
                end = min(n - 1, i + lag); b = np.zeros((T + 1, T))
                for k in range(end - 1, i - 1, -1):
                    nxt = le[k + 1][None, None, :] + b[1:, :][None, :, :]
                    m = L2[:, 1:, :] + nxt
                    mx = m.max(axis=2); b = mx + np.log(np.exp(m - mx[:, :, None]).sum(axis=2))
                bwd[i][:, :] = b
        else:
            for i in range(n - 2, -1, -1):
                # bwd[i][a, b] = logsum_c ( L2[a, b+1, c] + le[i+1][c] + bwd[i+1][b+1, c] )
                nxt = le[i + 1][None, None, :] + bwd[i + 1][1:, :][None, :, :]     # [1, T(b), T(c)]
                m = L2[:, 1:, :] + nxt                                              # [S(a), T(b), T(c)]
                mx = m.max(axis=2); bwd[i][:, :] = mx + np.log(np.exp(m - mx[:, :, None]).sum(axis=2))
        post = fwd + bwd                                          # [n, S, T]
        mx = post.max(axis=(1, 2), keepdims=True)
        post = np.log(np.exp(post - mx).sum(axis=1)) + mx[:, 0, :]          # marginal over the previous category -> [n, T]
        post -= post.max(axis=1, keepdims=True); post = np.exp(post); post /= post.sum(axis=1, keepdims=True)
        return post

    def tag(self, words: Sequence[str]) -> List[str]:
        """Point readout: argmax of the posterior per token (graded marginal, not Viterbi)."""
        if not words:
            return []
        post = self.posterior(words)
        return [self.tags[int(np.argmax(post[i]))] for i in range(len(words))]

    def tag_with_posterior(self, words: Sequence[str]) -> Tuple[List[str], List[Dict[str, float]]]:
        post = self.posterior(words)
        tags = [self.tags[int(np.argmax(post[i]))] for i in range(len(words))]
        dist = [{t: float(post[i, j]) for j, t in enumerate(self.tags) if post[i, j] >= 0.01} for i in range(len(words))]
        return tags, dist

    # ------------------------------------------------------------------ persistence
    def save(self, path: str = ASSET) -> str:
        d = {"lam": self.lam, "suf_len": self.suf_len, "order": self.order, "use_shape": self.use_shape, "rare_max": self.rare_max,
             "use_cluster": self.use_cluster, "clus": {t: dict(c) for t, c in self.clus.items()},
             "emit": {t: dict(c) for t, c in self.emit.items()}, "trans": {p: dict(c) for p, c in self.trans.items()},
             "suf": {str(k): {t: dict(c) for t, c in v.items()} for k, v in self.suf.items()},
             "shape": {t: dict(c) for t, c in self.shape.items()},
             "trans2": {a + "\t" + b: dict(c) for (a, b), c in self.trans2.items()},
             "note": "COUNTS only (plastic); log-probabilities are recomputed from them on load (finalize)"}
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(d, f)
        return path

    @classmethod
    def load(cls, path: str = ASSET) -> "LexicalCategories":
        with open(path, encoding="utf-8") as f:
            d = json.load(f)
        m = cls(lam=d.get("lam", 0.1), suf_len=d.get("suf_len", 4), order=d.get("order", 1), use_shape=d.get("use_shape", False),
                rare_max=d.get("rare_max", 0), use_cluster=d.get("use_cluster", False))
        for t, c in d.get("clus", {}).items():
            m.clus[t] = Counter(c)
        for t, c in d.get("shape", {}).items():
            m.shape[t] = Counter(c)
        for key, c in d.get("trans2", {}).items():
            a, b = key.split("\t"); m.trans2[(a, b)] = Counter(c)
        for t, c in d["emit"].items():
            m.emit[t] = Counter(c); m.tag_count[t] = sum(c.values()); m.vocab.update(c.keys())
        for p, c in d["trans"].items():
            m.trans[p] = Counter(c)
        for k, v in d["suf"].items():
            k = int(k)
            for t, c in v.items():
                m.suf[k][t] = Counter(c)
                for s, n in c.items():
                    m.suf_tot[k][s] += n
        return m.finalize()


_INST: Optional[LexicalCategories] = None


def get() -> LexicalCategories:
    global _INST
    if _INST is None:
        _INST = LexicalCategories.load()
    return _INST


ASSET_PENN = os.path.join(_REPO, "data", "frontend_assets", "lexical_categories_counts_penn_v1.json")   # the PENN-TAGSET ARM


def build_asset(train_path: Optional[str] = None, out: str = ASSET, column: int = 3, order: int = 1, use_shape: bool = False,
                rare_max: int = 0, use_cluster: bool = False) -> dict:
    """Offline accrual from the UD-EWT training sentences' tag column (foundation supply) -> counts asset.
    column 3 = UPOS (the live inventory); column 4 = XPOS (Penn tags: the same organ's arm for consumers that read tense/form
    classes -- the temporal ORDER organ, 2026-09-13 -- replacing nltk's PerceptronTagger at read time)."""
    train_path = train_path or os.path.join(_REPO, "data", "corpora", "ud_english_ewt", "en_ewt-ud-train.conllu")
    sents, cur = [], []
    with open(train_path, encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if not line:
                if cur:
                    sents.append(cur); cur = []
                continue
            if line.startswith("#"):
                continue
            c = line.split("\t")
            if "-" in c[0] or "." in c[0]:
                continue
            cur.append((c[1], c[column]))
    if cur:
        sents.append(cur)
    m = LexicalCategories(order=order, use_shape=use_shape, rare_max=rare_max, use_cluster=use_cluster).accrue(sents).finalize(); p = m.save(out)
    return {"n_sentences": len(sents), "n_categories": len(m.tags), "vocab": len(m.vocab), "asset": os.path.relpath(p, _REPO)}


__all__ = ["LexicalCategories", "get", "build_asset", "ASSET", "UPOS2WN"]

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "build":
        print(build_asset())
    else:
        m = get(); toks = "The dog was bitten by the man because it barked .".split()
        print(list(zip(toks, m.tag(toks))))
