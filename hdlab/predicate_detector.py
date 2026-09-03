"""hdlab/predicate_detector.py -- REGISTER-ROBUST GLASS-BOX PREDICATE (verbhood) RECALL.

The landed form of the owner-DONE `register_robust_event_detection_the_reader_drops_events_when_the_
tagger_misses_the_verb` solution. The live UPOS==VERB event detector (situation_reader.tense_agnostic)
silently DROPS a whole clause -- who did what to whom, gone -- whenever the POS tagger mistags a real
verb as a noun/adj (common in archaic / register-diverse / noun-flanked prose). This organ recovers the
dropped predicates ADDITIVELY: for every non-VERB non-AUX token with a WordNet verb-reading, a small
7-weight LOGISTIC combiner over REGISTER-INVARIANT cues (the noisy-channel likelihood x structural prior;
Gibson 2013) scores P(dropped-predicate); above threshold the reader fires an extra event. It is
ADDITIVE-ONLY -> the events the reader already detects and their role picks are BYTE-IDENTICAL (no
regression by construction). Glass-box, PARSE-FREE, NO external LLM.

Validated (verification/test_register_predicate_detector.py, 12/12): recovery of tagger-DROPPED verbs
@ FP<=0.5 false-verbs/sentence -- MODERN (UD-EWT test, 5-fold CV) 0.8989, 19c-TRANSFER (LitBank, ZERO
19c labels) 0.5625, both CI-separated over the info-free random-verbhood twin; crosses the parent's
structure-only modern wall (0.16). The threshold in the asset is calibrated to FP<=0.5/sent on MODERN;
on denser 19c candidate space the SAME threshold rises to ~1.4 FP/sent (it is an FP-budget knob).

The 7 features + learned weights (standardized) are the brain's noisy-channel COMBINATION made a LEARNED
weighting (not hand AND/OR logic): verb_margin +1.63 (tagger emission VERB-minus-best-non-VERB = lexical
LIKELIHOOD), morph_finite +0.46, clause_verbless +0.43 (one-predicate-per-clause competition),
subj_before +0.39, frame_anchor +0.21 (Mintz), rel_position -0.32, obj_after -0.12.

All scoring functions are promoted VERBATIM from experiments/exp_register_predicate_detector_v1.py
(feats_parsefree / verb_margin / morph_finite) + experiments/exp_whodidwhat_verb_id_recoverable_v1.py
(has_verb_reading / frame_verb_cue) so this organ carries NO experiments/ dependency. Scoring is pure
Python (no numpy) -- it reproduces sklearn LogisticRegression.predict_proba on standardized features
EXACTLY (sigmoid(coef . standardize(feats) + intercept)).
"""
from __future__ import annotations

import json
import math
import os
from typing import Dict, List, Sequence, Tuple

from hdlab.pos_tagger import pos_features
from hdlab.thematic_role_labeler import lemma_verb

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_ASSET = os.path.join(_REPO, "data/frontend_assets/predicate_detector_ud_qasrl.json")

# Feature order MUST match the asset's `feat_names` (and feats_parsefree below).
FEAT_NAMES = ["verb_margin", "frame_anchor", "subj_before", "obj_after",
              "morph_finite", "clause_verbless", "rel_position"]
NOMINAL = ("NOUN", "PROPN", "PRON")


# ---- candidate gate + cues (promoted VERBATIM from the experiment cells; glass-box, register-invariant) ----
_WN = None


def has_verb_reading(tok: str) -> bool:
    """Glass-box lexical verbhood: WordNet has a VERB synset for the token or its de-inflected lemma.
    (verbatim from exp_whodidwhat_verb_id_recoverable_v1.has_verb_reading)"""
    global _WN
    if _WN is None:
        from nltk.corpus import wordnet as wn
        _WN = wn
    low = tok.lower()
    if _WN.synsets(low, pos="v"):
        return True
    return bool(_WN.synsets(lemma_verb(low), pos="v"))


def frame_verb_cue(toks: Sequence[str], pos: Sequence[str], ix: int, k: int = 3) -> bool:
    """Mintz frequent-frame verbhood (clause-local, low-FP): the token at ix is the clause's predicate if
    it has a VERB reading, a nominal SUBJECT sits within k tokens BEFORE it, a nominal OBJECT sits within k
    tokens AFTER it, and NO already-VERB-tagged token intervenes between that subject and ix.
    (verbatim from exp_whodidwhat_verb_id_recoverable_v1.frame_verb_cue)"""
    if pos[ix] == "VERB" or not has_verb_reading(toks[ix]):
        return False
    subs = [j for j in range(max(0, ix - k), ix) if pos[j] in NOMINAL]
    if not subs:
        return False
    objs = [j for j in range(ix + 1, min(len(toks), ix + 1 + k)) if pos[j] in NOMINAL]
    if not objs:
        return False
    if any(pos[j] == "VERB" for j in range(subs[-1] + 1, ix)):
        return False   # another verb already occupies this clause's predicate slot
    return True


def verb_margin(obs: Sequence[str], i: int, W: Dict[str, float], tags: Sequence[str]) -> float:
    """emission(VERB) - best emission over non-VERB non-AUX tags (the noisy-channel lexical LIKELIHOOD).
    (verbatim from exp_register_predicate_detector_v1.verb_margin)"""
    s = {t: sum(W.get(f, 0.0) for f in pos_features(obs, i, t)) for t in tags}
    v = s.get("VERB", -1e9)
    best_non = max(val for t, val in s.items() if t not in ("VERB", "AUX"))
    return v - best_non


def morph_finite(w: str) -> float:
    """Finite/participial verb morphology (register-inclusive incl. archaic -eth/-est/'d/-th).
    (verbatim from exp_register_predicate_detector_v1.morph_finite)"""
    wl = w.lower()
    for suf in ("ing", "eth", "est", "ed", "th", "'d", "es", "s", "d", "n"):
        if wl.endswith(suf) and len(wl) > len(suf) + 1:
            return 1.0
    return 0.0


def feats_parsefree(toks: Sequence[str], pos: Sequence[str], i: int,
                    W: Dict[str, float], tags: Sequence[str]) -> List[float]:
    """The 7 register-invariant, parse-free cues in FEAT_NAMES order.
    (verbatim from exp_register_predicate_detector_v1.feats_parsefree)"""
    subj = 1.0 if any(pos[j] in NOMINAL for j in range(max(0, i - 4), i)) else 0.0
    obj = 1.0 if any(pos[j] in NOMINAL for j in range(i + 1, min(len(toks), i + 5))) else 0.0
    frame = 1.0 if frame_verb_cue(toks, pos, i) else 0.0
    verbless = 0.0 if any(p == "VERB" for p in pos) else 1.0
    relpos = i / max(1, len(toks) - 1)
    return [verb_margin(toks, i, W, tags), frame, subj, obj, morph_finite(toks[i]), verbless, relpos]


def _sigmoid(z: float) -> float:
    if z >= 0:
        return 1.0 / (1.0 + math.exp(-z))
    e = math.exp(z)
    return e / (1.0 + e)


class PredicateDetector:
    """The static logistic predicate detector (asset = data/frontend_assets/predicate_detector_ud_qasrl.json).

    Usage (the reader wire): for each token, `is_candidate` gates it (non-VERB non-AUX + WordNet verb-reading);
    `score` returns P(dropped-predicate); `rescue_indices` returns the (idx, score) pairs above threshold to
    fire additional events for. The tagger weights/tag-set (`W`, `tags`) come from the caller's PosTagger
    (`tagger._perc.weights`, `tagger.tags`) -- the SAME tagger the detector was trained against.
    """

    def __init__(self, feat_names, coef, intercept, mu, sd, threshold,
                 gate="wordnet_verb_reading_and_non_aux", with_parse=False):
        if list(feat_names) != FEAT_NAMES:
            raise ValueError("predicate_detector asset feat order mismatch: %r" % (feat_names,))
        if with_parse:
            raise ValueError("this organ lands the PARSE-FREE detector only (with_parse asset unsupported)")
        self.feat_names = list(feat_names)
        self.coef = [float(c) for c in coef]
        self.intercept = float(intercept)
        self.mu = [float(x) for x in mu]
        self.sd = [float(x) if float(x) != 0.0 else 1.0 for x in sd]
        self.threshold = float(threshold)
        self.gate = gate

    @classmethod
    def load(cls, path: str = DEFAULT_ASSET) -> "PredicateDetector":
        with open(path, encoding="utf-8") as f:
            a = json.load(f)
        return cls(a["feat_names"], a["coef"], a["intercept"], a["mu"], a["sd"],
                   a["operating_threshold_fp_le_0p5_modern"],
                   gate=a.get("gate", "wordnet_verb_reading_and_non_aux"),
                   with_parse=bool(a.get("with_parse", False)))

    def is_candidate(self, toks: Sequence[str], pos: Sequence[str], i: int) -> bool:
        """The register-invariant rescue gate: non-VERB non-AUX token with a WordNet verb-reading."""
        return pos[i] not in ("VERB", "AUX") and has_verb_reading(toks[i])

    def score(self, toks: Sequence[str], pos: Sequence[str], i: int,
              W: Dict[str, float], tags: Sequence[str]) -> float:
        """P(token i is a tagger-dropped event predicate). Reproduces sklearn predict_proba on standardized
        features exactly: sigmoid(coef . (feats - mu)/sd + intercept)."""
        fv = feats_parsefree(toks, pos, i, W, tags)
        z = self.intercept
        for k in range(len(self.coef)):
            z += self.coef[k] * ((fv[k] - self.mu[k]) / self.sd[k])
        return _sigmoid(z)

    def rescue_indices(self, toks: Sequence[str], pos: Sequence[str],
                       W: Dict[str, float], tags: Sequence[str],
                       threshold: float = None) -> List[Tuple[int, float]]:
        """(idx, score) for every gated candidate the detector promotes to an event predicate (score >= th).
        ADDITIVE: excludes tokens already tagged VERB/AUX -> never touches an existing detection."""
        th = self.threshold if threshold is None else float(threshold)
        out = []
        for i in range(len(toks)):
            if pos[i] in ("VERB", "AUX"):
                continue
            if not has_verb_reading(toks[i]):
                continue
            p = self.score(toks, pos, i, W, tags)
            if p >= th:
                out.append((i, p))
        return out
