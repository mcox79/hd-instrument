"""Online predictive-coding EVENT-TRANSITION world-model + the intrinsic counterfactual-necessity causal reader.

Promoted 2026-09-09 from the owner-DONE `generate_dont_retrieve_causal_edges_for_unmarked_narrative_causation`
(PARTIAL/north-star; reverified 67/67; witness verification/test_causal_antecedent_reader.py). This is the FORWARD
EVENT-SEQUENCE level of the predictive hierarchy -- the level the substrate lacked. It is NOT a duplicate:
  - hdlab.predictive_reader = the WORD/FEATURE level (verb+role -> expected argument FEATURES; static fitted centroids,
    Altmann-Kamide within-clause anticipation).
  - hdlab.n400_coherence_monitor = the BACKWARD event-coherence half.
  - THIS = the FORWARD event-transition predictor: recent event-CONCEPTS -> next event-concept, learned ONLINE.

WHAT IS PINNED (copy the operation): PREDICTIVE CODING (Rao-Ballard 1999 / Friston 2010 -- predict the next event,
learn from the error) with a RESCORLA-WAGNER delta-rule online update (Schultz dopaminergic prediction error; a SINGLE
reading pass, NO batch training, NO freeze -- the brain learns continuously); a distributed ACT-R recency context
(Anderson -- most-recent event highest activation); events = verb-CONCEPTS via the substrate's OWN glass-box
hdlab.pos_tagger + WordNet morphy lemma (the ATL codes the verb CONCEPT, not a surface stem). THE CAUSAL CRITERION
(100% brain-foundational): an antecedent A is a CAUSE of effect B iff, had A not occurred, B would have been more
SURPRISING -- COUNTERFACTUAL NECESSITY (Gerstenberg-Tenenbaum Counterfactual Simulation Model; Trabasso
necessity-in-the-circumstances; Kuperberg-Jaeger predictive coding / the N400 as prediction error):
    necessity(A, B) = surprisal(B | context minus {A}) - surprisal(B | context)  [>0 => A helped predict B]
    inferred cause of B = argmax_A necessity(A, B)
This is NON-CIRCULAR (a counterfactual ablation, not the argmax-predictability tautology) and INTRINSIC (no external
gold -> trap-proof: the solver proved every external causal gold -- MAVEN-ERE / TellMeWhy / GLUCOSE -- is a
POSITION-ARTIFACT trap that a trivial position floor beats, and that position is ORTHOGONAL to predictive coherence).

MEASURED (solver, simplewiki held-out, glass-box tagger, world-model learned online, NO gold/LLM/training):
  predictive coding 7.247 bits/event < bigram 7.495 < frequency 7.531 < random 8.229 -- PC beats static COUNTING
  +0.247 bits CI[0.221,0.274] CI-sep; the causal reader's antecedent necessity 0.345 vs random-event 0.036
  (+0.308 CI-sep) and vs nearest-event 0.111 (+0.233 CI-sep -- ESCAPES the position confound; nearest only 32%).

OUR-INVENTION-UNDER-TEST (swept, not adopted): the vocab cap `vocab_k`, the history depth `hist`, the recency `decay`,
the learning rate `lr`, the softmax over the linear read-out W (the simplest generative event model; a 2-layer
Rao-Ballard hierarchy is the named deepening).

DEFAULT-SAFE / FOUNDATION-ASSET: a fitted world-model is a STATIC OFFLINE-BUILT asset (consolidated foundation), the
brain's consolidated-memory + continuous-online-growth pattern. Build once (`python -m hdlab.predictive_world_model
--build`), persist, load at inference; `necessity`/`causal_antecedent` then read the target document's events. Importing
this changes NO existing behaviour (a NEW island). The deep wiring -- N400 prediction-error against THIS forward model
(closing the recurrent predictive-coding loop) -- is the project's pri-1 north-star and is deliberately NOT wired here.
ASCII, NumPy + hdlab.pos_tagger + nltk.wordnet (an admissible static lexical foundation) ONLY. NO external LLM.
"""
from __future__ import annotations

import math
import os
import re
import sys
from collections import Counter, deque
from typing import Dict, List, Optional, Sequence

import numpy as np

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

_POS_ASSET = os.path.join(_REPO, "data/frontend_assets/pos_tagger_ud_ewt_upos.json")
_ASSET = os.path.join(_REPO, "data/frontend_assets/predictive_world_model_simplewiki_v1.npz")
_SIMPLEWIKI = os.path.join(_REPO, "data", "corpora", "simplewiki", "simplewiki_clean_v1.txt")

# AUX / light forms filtered from the CONTENT-event set (byte-faithful to _causal_order_store.AUX).
_AUX = {"be", "been", "being", "am", "is", "are", "was", "were", "'s", "'re", "'m",
        "have", "has", "had", "'ve", "'d", "do", "does", "did", "will", "would", "shall", "should",
        "can", "could", "may", "might", "must", "let", "not", "get", "got"}
_TOK = re.compile(r"[A-Za-z']+")
_TAGGER = None
_WN_CACHE: Dict[str, str] = {}


def _tagger():
    global _TAGGER
    if _TAGGER is None:
        from hdlab.pos_tagger import PosTagger
        _TAGGER = PosTagger.load(_POS_ASSET)
    return _TAGGER


def _lemma_crude(w: str) -> str:
    w = w.lower()
    for suf in ("ing", "ed", "es", "s"):
        if w.endswith(suf) and len(w) - len(suf) >= 3:
            return w[: -len(suf)]
    return w


def _lemma(w: str) -> str:
    """Verb LEMMA via WordNet morphy (the verb CONCEPT/TYPE: went->go, decided->decide); crude-stem fallback."""
    w = w.lower()
    hit = _WN_CACHE.get(w)
    if hit is not None:
        return hit
    try:
        from nltk.corpus import wordnet as wn
        lem = wn.morphy(w, "v")
    except Exception:
        lem = None
    out = lem if lem else _lemma_crude(w)
    _WN_CACHE[w] = out
    return out


def content_events(sentence: str) -> List[str]:
    """TENSE-AGNOSTIC content-event extraction: every UPOS==VERB token that is not an AUX/light form, lemmatized to
    the verb CONCEPT (WordNet morphy). Glass-box (hdlab.pos_tagger); recovers present/bare/progressive events."""
    toks = _TOK.findall(sentence)
    if not toks:
        return []
    tags = _tagger().tag(toks)
    return [_lemma(w) for w, t in zip(toks, tags) if t == "VERB" and w.lower() not in _AUX]


class PredictiveWorldModel:
    """Online predictive-coding event-transition model: recent event-CONCEPT context -> P(next event-concept), a
    linear read-out W learned by the Rescorla-Wagner delta-rule in ONE online pass (no batch, no freeze). Exposes
    held-out `surprisal`, counterfactual `necessity`, and the concept-level `causal_antecedent` read."""

    def __init__(self, hist: int = 6, lr: float = 0.10, decay: float = 0.6):
        self.hist = int(hist)
        self.lr = float(lr)
        self.decay = float(decay)
        self.vocab: List[str] = []
        self.idx: Dict[str, int] = {}
        self.V = 0
        self.W: Optional[np.ndarray] = None
        self.b0: Optional[np.ndarray] = None

    # ---- learning (online, single pass) ----
    def _ctx(self, recent: deque) -> np.ndarray:
        c = np.zeros(self.V); w = 1.0
        for j in reversed(recent):
            c[j] += w; w *= self.decay
        return c

    def _p(self, c: np.ndarray) -> np.ndarray:
        z = self.W.T @ c + self.b0
        z = z - z.max()
        e = np.exp(z)
        return e / e.sum()

    def fit_online(self, event_stream: Sequence[str], vocab_k: int = 300) -> "PredictiveWorldModel":
        """Learn W on a reading-order stream of event-CONCEPT strings (delta-rule, single online pass). vocab = the
        top-`vocab_k` most frequent concepts; out-of-vocab events are skipped (the stream stays in reading order)."""
        freq = Counter(event_stream)
        self.vocab = [w for w, _ in freq.most_common(vocab_k)]
        self.idx = {w: i for i, w in enumerate(self.vocab)}
        self.V = len(self.vocab)
        if self.V < 2:
            raise RuntimeError("vocab too small: %d" % self.V)
        ev = [self.idx[c] for c in event_stream if c in self.idx]
        self.W = np.zeros((self.V, self.V)); self.b0 = np.zeros(self.V)
        recent: deque = deque(maxlen=self.hist)
        for nxt in ev:
            c = self._ctx(recent)
            p = self._p(c)
            onehot = np.zeros(self.V); onehot[nxt] = 1.0
            err = onehot - p                                  # prediction error (the N400 signal)
            if c.any():
                self.W += self.lr * np.outer(c, err)          # delta-rule: error x context
            self.b0 += self.lr * err
            recent.append(nxt)
        return self

    # ---- read-out (id space) ----
    def _ctx_from_ids(self, ids: Sequence[int]):
        """Recency-weighted context vector + the per-position weights, from context ids OLDEST..NEWEST."""
        n = len(ids)
        weights = [0.0] * n
        w = 1.0
        for k in range(n - 1, -1, -1):
            weights[k] = w; w *= self.decay
        c = np.zeros(self.V)
        for k, cid in enumerate(ids):
            c[cid] += weights[k]
        return c, weights

    def surprisal_id(self, nxt_id: int, context_ids: Sequence[int]) -> float:
        c, _ = self._ctx_from_ids([i for i in context_ids if 0 <= i < self.V])
        return -math.log2(max(self._p(c)[nxt_id], 1e-12))

    def necessity_ids(self, effect_id: int, context_ids: Sequence[int]) -> List[tuple]:
        """Per-context-event counterfactual necessity (surprisal INCREASE on ablating that event). Returns
        [(context_index, concept, necessity_bits)] oldest..newest; [] if <1 usable context event."""
        ids = [i for i in context_ids if 0 <= i < self.V]
        if len(ids) < 1:
            return []
        c_full, weights = self._ctx_from_ids(ids)
        base = -math.log2(max(self._p(c_full)[effect_id], 1e-12))
        out = []
        for k, cid in enumerate(ids):
            c_ab = c_full.copy(); c_ab[cid] -= weights[k]
            surp = -math.log2(max(self._p(c_ab)[effect_id], 1e-12))
            out.append((k, self.vocab[cid], surp - base))
        return out

    # ---- concept-level read (the live-reader API) ----
    def causal_antecedent(self, effect_concept: str, context_concepts: Sequence[str]) -> Optional[Dict]:
        """The inferred causal antecedent of `effect_concept` among `context_concepts` (oldest..newest) = the event
        whose removal most raises the effect's surprisal (argmax counterfactual necessity). Returns
        {'antecedent', 'necessity_bits', 'context_index'} or None (effect OOV / no in-vocab context)."""
        if self.W is None or effect_concept not in self.idx:
            return None
        ids = [self.idx[c] for c in context_concepts if c in self.idx]
        necs = self.necessity_ids(self.idx[effect_concept], ids)
        if not necs:
            return None
        am = max(necs, key=lambda t: t[2])
        return {"antecedent": am[1], "necessity_bits": round(float(am[2]), 4), "context_index": am[0]}

    # ---- persistence (a fitted world-model = a static consolidated-foundation asset) ----
    def save(self, path: str = _ASSET) -> None:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        np.savez_compressed(path, W=self.W, b0=self.b0, vocab=np.array(self.vocab, dtype=object),
                            params=np.array([self.hist, self.lr, self.decay], dtype=object))

    @classmethod
    def load(cls, path: str = _ASSET) -> "PredictiveWorldModel":
        d = np.load(path, allow_pickle=True)
        hist, lr, decay = d["params"]
        m = cls(hist=int(hist), lr=float(lr), decay=float(decay))
        m.W = d["W"]; m.b0 = d["b0"]
        m.vocab = list(d["vocab"]); m.idx = {w: i for i, w in enumerate(m.vocab)}; m.V = len(m.vocab)
        return m


def _build(n_sents: int = 40000, vocab_k: int = 300, out: str = _ASSET) -> str:
    """Learn the world-model on simplewiki (the reader's modern-prose reading source) and persist it."""
    stream = []
    with open(_SIMPLEWIKI, encoding="utf-8", errors="ignore") as f:
        for i, ln in enumerate(f):
            if i >= n_sents:
                break
            ln = ln.strip()
            if len(ln) >= 8:
                stream.extend(content_events(ln))
    m = PredictiveWorldModel().fit_online(stream, vocab_k=vocab_k)
    m.save(out)
    print("built predictive_world_model: %d events, V=%d -> %s" % (len(stream), m.V, out))
    return out


def _selftest() -> int:
    """Synthetic causal-chain stream: A->B recurs, so ablating A must raise B's surprisal MORE than a random event
    (necessity is REAL) and the argmax antecedent of B must be A (not merely the nearest)."""
    rng = np.random.default_rng(0)
    fillers = ["walk", "look", "sit", "talk", "wait", "read", "eat", "sleep"]
    stream = []
    for _ in range(4000):
        stream += [fillers[int(rng.integers(0, len(fillers)))]]
        if rng.random() < 0.5:
            stream += ["strike", "fall"]              # A=strike reliably precedes B=fall (a filler intervenes never)
    m = PredictiveWorldModel(hist=6).fit_online(stream, vocab_k=50)
    fails = []
    # surprisal of 'fall' after 'strike' should be LOW vs a random context
    s_after_strike = m.surprisal_id(m.idx["fall"], [m.idx["walk"], m.idx["strike"]])
    s_random = m.surprisal_id(m.idx["fall"], [m.idx["walk"], m.idx["eat"]])
    ok1 = s_after_strike < s_random
    print("  %s W1 surprisal(fall|..strike)=%.3f < surprisal(fall|..random)=%.3f" %
          ("PASS" if ok1 else "FAIL", s_after_strike, s_random))
    if not ok1:
        fails.append("W1")
    # causal antecedent of 'fall' among a context containing 'strike' = 'strike'
    ante = m.causal_antecedent("fall", ["walk", "strike", "look"])
    ok2 = ante is not None and ante["antecedent"] == "strike" and ante["necessity_bits"] > 0
    print("  %s W2 causal_antecedent(fall) = %s (want 'strike', nec>0)" % ("PASS" if ok2 else "FAIL", ante))
    if not ok2:
        fails.append("W2")
    # save/load round-trip is byte-faithful
    import tempfile
    p = os.path.join(tempfile.mkdtemp(), "pwm.npz"); m.save(p)
    m2 = PredictiveWorldModel.load(p)
    ok3 = m2.causal_antecedent("fall", ["walk", "strike", "look"]) == ante
    print("  %s W3 save/load round-trip byte-faithful" % ("PASS" if ok3 else "FAIL"))
    if not ok3:
        fails.append("W3")
    print("RESULT: %s" % ("PASS" if not fails else "FAIL (%s)" % ",".join(fails)))
    return 1 if fails else 0


if __name__ == "__main__":
    if "--build" in sys.argv:
        _build()
    else:
        sys.exit(_selftest())
