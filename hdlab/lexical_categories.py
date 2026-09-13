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
BOS = "<s>"
UPOS2WN = {"NOUN": "n", "VERB": "v", "ADJ": "a", "ADV": "r"}


class LexicalCategories:
    """Generative count-based category model with forward-backward posterior decoding (plastic counts)."""

    def __init__(self, lam: float = 0.1, suf_len: int = 4):
        self.lam = float(lam); self.suf_len = int(suf_len)
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
            prev = BOS
            for w, t in sent:
                w = w.lower()
                self.emit[t][w] += 1; self.tag_count[t] += 1; self.vocab.add(w); self.trans[prev][t] += 1
                for k in range(1, self.suf_len + 1):
                    if len(w) >= k:
                        self.suf[k][t][w[-k:]] += 1; self.suf_tot[k][w[-k:]] += 1
                prev = t
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
        self.log_trans = lt; self._dirty = False
        return self

    # ------------------------------------------------------------------ inference: graded posterior
    def _log_emit(self, word: str) -> np.ndarray:
        T = len(self.tags); out = np.empty(T); w = word.lower(); V1 = len(self.vocab) + 1
        if w in self.vocab:
            for i, t in enumerate(self.tags):
                out[i] = math.log((self.emit[t][w] + self.lam) / (self.tag_count[t] + self.lam * V1))
            return out
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

    def posterior(self, words: Sequence[str]) -> np.ndarray:
        """Forward-backward marginals P(category_i | words): [n, T]."""
        if self._dirty:
            self.finalize()
        n = len(words); T = len(self.tags)
        if n == 0:
            return np.zeros((0, T))
        le = np.stack([self._log_emit(w) for w in words])
        A = self.log_trans[1:]                                    # [T_prev, T_cur]
        fwd = np.empty((n, T)); fwd[0] = self.log_trans[0] + le[0]
        for i in range(1, n):
            m = fwd[i - 1][:, None] + A                           # [T_prev, T_cur]
            mx = m.max(axis=0); fwd[i] = mx + np.log(np.exp(m - mx).sum(axis=0)) + le[i]
        bwd = np.zeros((n, T))
        for i in range(n - 2, -1, -1):
            m = A + (le[i + 1] + bwd[i + 1])[None, :]            # [T_prev, T_cur]
            mx = m.max(axis=1); bwd[i] = mx + np.log(np.exp(m - mx[:, None]).sum(axis=1))
        post = fwd + bwd; post -= post.max(axis=1, keepdims=True)
        post = np.exp(post); post /= post.sum(axis=1, keepdims=True)
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
        d = {"lam": self.lam, "suf_len": self.suf_len,
             "emit": {t: dict(c) for t, c in self.emit.items()}, "trans": {p: dict(c) for p, c in self.trans.items()},
             "suf": {str(k): {t: dict(c) for t, c in v.items()} for k, v in self.suf.items()},
             "note": "COUNTS only (plastic); log-probabilities are recomputed from them on load (finalize)"}
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(d, f)
        return path

    @classmethod
    def load(cls, path: str = ASSET) -> "LexicalCategories":
        with open(path, encoding="utf-8") as f:
            d = json.load(f)
        m = cls(lam=d.get("lam", 0.1), suf_len=d.get("suf_len", 4))
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


def build_asset(train_path: Optional[str] = None, out: str = ASSET) -> dict:
    """Offline accrual from the UD-EWT training sentences' tag column (foundation supply) -> counts asset."""
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
            cur.append((c[1], c[3]))
    if cur:
        sents.append(cur)
    m = LexicalCategories().accrue(sents).finalize(); p = m.save(out)
    return {"n_sentences": len(sents), "n_categories": len(m.tags), "vocab": len(m.vocab), "asset": os.path.relpath(p, _REPO)}


__all__ = ["LexicalCategories", "get", "build_asset", "ASSET", "UPOS2WN"]

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "build":
        print(build_asset())
    else:
        m = get(); toks = "The dog was bitten by the man because it barked .".split()
        print(list(zip(toks, m.tag(toks))))
