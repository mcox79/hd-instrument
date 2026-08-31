"""hdlab/verb_subcat.py -- verb-SUBCATEGORIZATION patient-presence organ (PROMOTED 2026-08-31 from
experiments/ref_verb_subcat_organ_v1.py; the landing-ready successor to
wire_the_incremental_parser_as_the_reader_extraction_front_end, p2, EXCELLENT). Same shape as the landed
graded_role_assigner: a static, offline-built, glass-box asset + static LEARNED cue-validities + a
pure-function cue integration. NO external LLM.

WHAT IT DOES: decides whether a verb's clause actually HAS a patient (existence), so the reader stops
assigning a spurious patient to intransitive verbs ("the man arrived at noon" -> patient=noon). This is the
PRESENCE half of who-did-what; the deployed graded_role_assigner does the IDENTITY half (which nominal),
and coref does the ENTITY half.

TWO STATIC ASSETS (offline, glass-box, no LLM):
  * verb_subcat_final_avg.json : lemma -> trans_ratio = MEAN(WordNet-frame transitive ratio, corpus
    P(obj|verb) from UD-EWT-train) -- the brain's lexical-frame + distributional-verb-bias dual basis
    (Levin 1993/VerbNet; Trueswell/Garnsey verb bias). PINNED basis; AUC 0.718/0.734 CI-sep over either
    source alone and over a shuffled twin.
  * graded_presence_model.json : the 7-feature logistic (trans_ratio + argument/adjunct + proximity +
    animacy + voice), fit offline on QA-SRL dev -- the learned cue VALIDITIES (== graded_role_assigner's
    DEFAULT_VALIDITIES pattern; the additive-cue->logistic IS the Competition-Model softmax posterior).
    On QA-SRL the graded gate AUC 0.777 beats the hard subcat gate 0.718; who-did-what id 0.30->0.49.

TWO GATES:
  * transitivity(lemma) < thr  -- the SIMPLE lexical-propensity gate. Needs only the verb lemma; this is
    the version VALIDATED END-TO-END THROUGH SituationReader.read() (the SubcatGateReader template beats the
    curated intransitive list +0.121 and a random same-rate twin +0.158; precision 0.514->0.643 @ recall
    0.936). This is what SituationReader.verb_subcat_gate wires (post-read, default-off).
  * patient_present(toks, pos, v, pick, thr)  -- the GRADED Competition-Model gate (the brain-faithful,
    QA-SRL-headline version). Needs the sentence POS + the patient token index; wiring it into the live
    reader (mid-role-path) is a QUEUED refinement that first needs the reader to expose POS + the patient
    token index at role-assignment time (WIRING_MAP DEBT 2). Provided here so the upgrade is a reader-side
    plumbing change, not a re-derivation.
"""
from __future__ import annotations

import json
import os
from typing import Dict, List, Optional, Sequence

import numpy as np

from hdlab.graded_role_assigner import robust_passive
from hdlab.thematic_role_labeler import lemma_verb
from hdlab.animacy_lexicon import lookup_animacy

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_ASSET = os.path.join(_REPO, "data", "verb_subcat_supply_optimized_v2", "verb_subcat_final_avg.json")
_MODEL = os.path.join(_REPO, "data", "verb_subcat_graded_presence_v3", "graded_presence_model.json")
NOMINAL = {"NOUN", "PROPN", "PRON"}
# CONSERVATIVE do-no-harm operating point for the GRADED gate (highest-recall gate that only suppresses
# clear intransitives; QA-SRL: presence-recall 0.954, keeps 95% of true patients). Raise toward F1-max.
CONSERVATIVE_THR = 0.30
# The transitivity-gate threshold validated END-TO-END through read() (the SubcatGateReader default).
TRANS_GATE_THR = 0.35

_ASSET_CACHE: Optional[Dict] = None
_MODEL_CACHE: Optional[Dict] = None


def _asset() -> Dict:
    global _ASSET_CACHE
    if _ASSET_CACHE is None:
        _ASSET_CACHE = json.load(open(_ASSET, encoding="utf-8")) if os.path.exists(_ASSET) else {}
    return _ASSET_CACHE


def _model() -> Optional[Dict]:
    global _MODEL_CACHE
    if _MODEL_CACHE is None:
        _MODEL_CACHE = json.load(open(_MODEL, encoding="utf-8")) if os.path.exists(_MODEL) else {}
    return _MODEL_CACHE or None


def transitivity(lemma: str) -> float:
    """The verb's transitivity propensity in [0,1] (0.5 = unknown -> neutral, defers to syntax)."""
    return _asset().get(lemma.lower(), {}).get("trans_ratio", 0.5)


def _cands(pos: Sequence[str]) -> List[int]:
    return [i for i in range(1, len(pos) + 1) if pos[i - 1] in NOMINAL]


def presence_features(toks: Sequence[str], pos: Sequence[str], v: int, pick: Optional[int]) -> Dict[str, float]:
    """The 7 Competition-Model cues for 'does verb v have a patient' (all read from toks/pos, no gold)."""
    lemma = lemma_verb(toks[v - 1])
    tr = transitivity(lemma)
    cands = _cands(pos)
    post = [i for i in cands if i > v]
    tgt = pick if (pick and pick > v) else (post[0] if post else None)
    adjunct = 1.0 if (tgt is not None and any(pos[j - 1] == "ADP" for j in range(v + 1, tgt))) else 0.0
    inv_dist = 1.0 / (1.0 + (tgt - v)) if tgt else 0.0
    an = lookup_animacy(toks[tgt - 1], pos[tgt - 1]) if tgt else None
    animate_pick = 1.0 if (an and an.get("animacy") == "animate") else 0.0
    return {"bias": 1.0, "trans_ratio": tr, "has_post": 1.0 if post else 0.0, "adjunct": adjunct,
            "inv_dist": inv_dist, "animate_pick": animate_pick,
            "passive": 1.0 if robust_passive(toks, pos, v) else 0.0, "n_post": min(len(post), 5) / 5.0}


def patient_present_prob(toks: Sequence[str], pos: Sequence[str], v: int, pick: Optional[int]) -> float:
    """P(verb v has a patient) via the learned logistic (Competition-Model cue integration)."""
    m = _model()
    f = presence_features(toks, pos, v, pick)
    if not m:      # no model asset -> back off to the raw transitivity propensity (still usable)
        return f["trans_ratio"]
    x = np.array([f[k] for k in m["feats"]], float)
    xs = (x - np.array(m["mu"])) / np.array(m["sd"])
    return float(1.0 / (1.0 + np.exp(-xs @ np.array(m["w"]))))


def patient_present(toks: Sequence[str], pos: Sequence[str], v: int, pick: Optional[int],
                    thr: float = CONSERVATIVE_THR) -> bool:
    """Decision: keep the binder's patient (True) or suppress it as spurious (False). Default threshold =
    the conservative do-no-harm point. Unknown verbs (trans_ratio 0.5) defer to the syntactic cues."""
    return patient_present_prob(toks, pos, v, pick) >= thr


def suppress_patient(lemma: str, thr: float = TRANS_GATE_THR) -> bool:
    """The SIMPLE lexical-propensity gate used by SituationReader.verb_subcat_gate (post-read): return True
    if a picked patient on this verb should be SUPPRESSED as spurious (transitivity below thr). Needs only
    the verb lemma -> usable from EventRecord.predicate. Unknown verbs (0.5) are never suppressed."""
    return transitivity(lemma_verb(lemma)) < thr


__all__ = ["transitivity", "presence_features", "patient_present_prob", "patient_present",
           "suppress_patient", "CONSERVATIVE_THR", "TRANS_GATE_THR"]


if __name__ == "__main__":
    # smoke: an intransitive verb with a PP-object should be judged patient-ABSENT; a transitive SVO present.
    t1 = "the man arrived at the station".split(); p1 = ["DET", "NOUN", "VERB", "ADP", "DET", "NOUN"]
    t2 = "the dog chased the cat".split(); p2 = ["DET", "NOUN", "VERB", "DET", "NOUN"]
    print("arrive+PP  prob=%.3f present=%s" % (patient_present_prob(t1, p1, 3, 6), patient_present(t1, p1, 3, 6)))
    print("chased SVO prob=%.3f present=%s" % (patient_present_prob(t2, p2, 3, 5), patient_present(t2, p2, 3, 5)))
    print("transitivity: arrive=%.2f chase=%.2f" % (transitivity("arrive"), transitivity("chase")))
