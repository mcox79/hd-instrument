"""verb_role_exemplar_selector.py -- the verb-role EXEMPLAR selector (a WHICH-argument selector).

WHY THIS EXISTS (2026-09-01, landed from the owner-DONE problem
`the_plausibility_prior_is_a_coarse_centroid_needs_a_structured_verb_role_exemplar_store`, p5). The reader's
plausibility prior was a coarse holistic grounded CENTROID -- it can gate a surprising argument but cannot say
WHICH of several candidates is the right patient for a SPECIFIC verb. The brain uses verb-specific selectional
preference / thematic fit stored as an EXEMPLAR (instance) distribution, NOT a centroid (McRae et al. 1998;
Elman 2009; the eADM). This organ is that selector, promoted VERBATIM from the validated cell
`experiments/exp_verbrole_exemplar_which_arg_v1.py`: for a verb, score each candidate nominal by its NEAREST
grounded exemplar among the verb's attested OBJ fillers (k-NN=1 / Chamfer max -- keeps the instance
distribution instead of averaging clusters into a mean), and pick the argmax.

MEASURED (p5, reverified 10/10): the nearest-exemplar selector picks the patient CI-separated over the coarse
holistic prior (+0.102), the verb-role MEAN centroid (+0.067 -- the INSTANCE distribution is the lever, not
richer features), and position-only (+0.143); the verb-shuffled twin loses (+0.097); it generalizes to UNSEEN
fillers by grounded similarity (+0.062). THE DEFINITIVE FINDING: who-did-what is bounded by DOMAIN MATCH of the
store's corpus (+0.149) -- so this modern store is a MODERN-prose selector; do NOT use it on 19c/OOD (it ties
its twin there -- the register-native store is its own problem).

STORE: `data/selectional_preferences_v1/selectional_slots_v1.pkl` (a glass-box UD-parsed `slot_filler` map
(verb,role)->{filler:count}; 14.7MB offline asset). Grounded space = the wired `hdlab.grounded_similarity`.
Glass-box, NO external LLM at inference. Lazy per-verb (grounds a verb's fillers only on first query).
"""
from __future__ import annotations

import math
import os
import pickle
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STORE = os.path.join(_REPO, "data/selectional_preferences_v1/selectional_slots_v1.pkl")
_EPS = 1e-9
_TOPK = 50
_MIN_COUNT = 1

# function words / light nouns that carry no verb-specific selectional signal (grounded_vector returns a
# vector for them, so they are filtered explicitly). PROMOTED VERBATIM from the validated cell's STOP.
STOP = {
    "them", "that", "which", "him", "this", "what", "it", "he", "she", "they", "we", "you", "i",
    "who", "whom", "whose", "these", "those", "one", "ones", "some", "any", "all", "both", "each",
    "other", "another", "such", "thing", "things", "someone", "something", "anyone", "anything",
    "everyone", "everything", "nobody", "nothing", "self", "here", "there", "way", "lot", "kind",
    "sort", "number", "part", "member", "us", "me", "her", "his", "their", "its", "my", "your",
}


def _cos(a, b) -> float:
    if a is None or b is None:
        return -1.0
    a = np.asarray(a, dtype=np.float64); b = np.asarray(b, dtype=np.float64)
    na = np.linalg.norm(a); nb = np.linalg.norm(b)
    if na < _EPS or nb < _EPS:
        return -1.0
    return float(np.dot(a, b) / (na * nb))


def _grounded(word):
    from hdlab.grounded_similarity import grounded_vector
    v = grounded_vector(word)
    return None if v is None else np.asarray(v, dtype=np.float64).reshape(-1)


def fit_exemplar(gcand, exemplars, knn: int = 1) -> float:
    """candidate fit = mean of the top-`knn` cosines of the candidate to the verb's attested grounded fillers
    (knn=1 == nearest-exemplar / Chamfer max). VERBATIM the validated cell's fit_exemplar -- selects the
    NEAREST filler cluster instead of averaging clusters into a mean (keeps the instance distribution)."""
    if not exemplars or gcand is None:
        return -1.0
    cs = sorted((_cos(gcand, g) for _, g in exemplars), reverse=True)
    k = min(knn, len(cs))
    return float(np.mean(cs[:k]))


def verb_selectivity(exemplars) -> Optional[float]:
    """1 - normalized entropy of the filler COUNT distribution (HIGH = sharp preference read/eat, LOW = flat
    have/get) -- the trust/precision weight. VERBATIM from the validated cell."""
    if not exemplars or len(exemplars) < 2:
        return None
    c = np.array([w for w, _ in exemplars], dtype=np.float64)
    p = c / c.sum()
    H = -(p * np.log(p + _EPS)).sum()
    Hmax = math.log(len(p))
    return float(1.0 - H / (Hmax + _EPS))


class VerbRoleExemplarSelector:
    """The WHICH-argument selector, hung on the reader when `verb_role_exemplar_select` is on. Lazily loads the
    glass-box selectional store and, per verb, grounds its top-K OBJ fillers on first query (cached). NO LLM."""

    def __init__(self, role: str = "OBJ", store_path: str = STORE, topk: int = _TOPK):
        self.role = role
        self.store_path = store_path
        self.topk = int(topk)
        self._slot_filler = None                       # raw (verb,role)->{filler:count} (lazy pickle)
        self._exemplar_cache: Dict[str, Optional[list]] = {}

    def _load(self) -> None:
        if self._slot_filler is None:
            with open(self.store_path, "rb") as f:
                self._slot_filler = pickle.load(f)["slot_filler"]

    def _lemma(self, verb: str) -> str:
        try:
            from hdlab.reading_grounding_loop import normalize_lemma
            return normalize_lemma(verb)
        except Exception:
            return str(verb).lower()

    def _exemplars(self, verb: str) -> Optional[List[Tuple[float, np.ndarray]]]:
        """The verb's grounded (count, vec) exemplars for `role`, top-K by count; None if uncovered/empty.
        Reproduces the validated cell's per-verb build (STOP + len>=3 + grounded-covered + top-K)."""
        v = self._lemma(verb)
        if v in self._exemplar_cache:
            return self._exemplar_cache[v]
        self._load()
        counts = self._slot_filler.get((v, self.role))
        items: List[Tuple[float, np.ndarray]] = []
        if counts:
            for filler, c in counts.items():
                if c < _MIN_COUNT or filler in STOP or len(filler) < 3:
                    continue
                g = _grounded(filler)
                if g is not None:
                    items.append((float(c), g))
            items.sort(key=lambda x: -x[0])
            items = items[:self.topk]
        out = items or None
        self._exemplar_cache[v] = out
        return out

    def covers(self, verb: str) -> bool:
        return self._exemplars(verb) is not None

    def select_patient(self, verb: str, candidate_heads: Sequence[str]) -> Optional[str]:
        """Return the candidate head that best fits the verb's OBJ selectional preference by NEAREST grounded
        exemplar (k-NN=1). None if the store does not cover the verb, or no candidate has a grounded vector
        (the caller then keeps its own fallback). Ties broken by first candidate (stable)."""
        exemplars = self._exemplars(verb)
        if not exemplars:
            return None
        best_head, best_fit = None, -2.0
        for h in candidate_heads:
            g = _grounded(str(h).lower())
            if g is None:
                continue
            fit = fit_exemplar(g, exemplars, knn=1)
            if fit > best_fit:
                best_fit, best_head = fit, str(h).lower()
        return best_head
