"""parse_confidence -- calibrated per-arc reliability (precision-weighting) for the head-driven readers.

Landed 2026-09-06 from the owner-DONE
`precision_weight_the_head_driven_readers_on_calibrated_parse_confidence` (Q111 -- strategy lands the additive
wire the prototype proved; the solver wrote NO hdlab). This is the RELIABILITY SUBSTRATE the reasoning phase
stands on: the head-driven readers can now TRUST confident parse arcs and DEFER on low-confidence ones.

WHAT THIS FIXES. The arc-eager parser already emits a per-arc confidence
(`arceager_parser.parse_with_conf -> (heads, conf, marg)`) that ZERO live consumers read. The head-driven
readers (who-did-what patient, obl/spatial attachment) commit to each role assignment as fact even when the arc
it was read off was a coin flip. This organ turns that WEAK raw signal (right-vs-wrong AUC 0.615 on UD-EWT /
0.501 on QA-SRL -- near-useless as emitted) into a SENSITIVITY-optimized CALIBRATED confidence in [0,1] that
separates the readers' RIGHT-from-WRONG role assignments (AUC 0.858 UD), so a reader can PRECISION-WEIGHT its
readout -- selective accuracy on the confident half rises 0.8789->0.9745 (who-did-what patient, UD-EWT) /
0.2982->0.3414 (QA-SRL) / 0.7581->0.8919 (obl/spatial), each CI-separated with the RANDOM-confidence twin FLAT.

BRAIN-FOUNDATIONAL (Friston precision / active inference). Precision-weighting -- weight a downstream commitment
by the reliability of the estimate driving it -- is PINNED at the computation level (Ernst & Banks 2002
inverse-variance MLE cue combination; Friston 2010 active inference: a reliable cue drives belief, an unreliable
one is down-weighted, never hard-committed; Kepecs 2008 / Kiani & Shadlen 2009 decision confidence gates
commitment / opt-out). The calibration IS the substrate's own pinned `graded_competition` operation: additive
Lewis-Vasishth cue activation A = sum_c w_c * support_c -> softmax = the Bayesian posterior over
{correct, incorrect} (McClelland 2013), weights = learned Competition-Model cue VALIDITIES (Bates-MacWhinney).
The role-competition entropy cue is read straight from `graded_competition.graded_pick` (REUSE, not reinvent).
Applying confidence to gate the THEMATIC-ROLE readout specifically is an architecture-level extrapolation
(OUR-INVENTION-UNDER-TEST, a-priori P~0.30) -- tested here, upheld, twin-controlled.

SENSITIVITY, not CALIBRATION. Strict calibration (a confidence that matches probability-of-correct) is NOT a
robust brain property (the hard-easy effect; Fleming & Dolan 2012: sensitivity != calibration). What is
brain-robust is confidence SENSITIVITY -- the ordering of right-from-wrong (meta-d'). So this readout optimizes
SENSITIVITY (AUC / risk-coverage monotonicity); the logistic is a sensitivity-optimizing readout, not a claim
that the brain computes a Platt-scaled probability.

RAW is weak, CALIBRATED is the lever. Wiring the RAW emitted arc confidence would FAIL (it is the settled
"confidence-weighting is a weak lever" negative: AUC 0.615 UD / 0.501 QA). The calibration is the upstream
component that makes it consumable -- do NOT wire the raw margin for the patient; use `calibrated_*_confidence`.

FROZEN OFFLINE ASSET (admissible; NO training at inference -- the invariant). The logistic weights below were
fit ONCE offline on UD-EWT train via the validated cell's `logistic_fit` (deterministic: zero-init, fixed
l2=1.0 / iters=400 / lr=0.2 gradient descent), then frozen as literals -- a STATIC glass-box asset. The feature
bodies are copied VERBATIM from the validated experiments/exp_precwt_live_whodidwhat_v1 (patient) and
exp_precwt_live_obl_space_v1 (obl); this module IS that calibrator, reproduced store-agnostically so any caller
can score an arc's reliability without re-fitting.

ADDITIVE / no-regress. This module reads the parse READ-ONLY and changes NO parse head -- so every non-consumer
is byte-identical (the SituationReader picks + blanket accuracy are unchanged). A consumer that OPTS to gate on
the confidence trades coverage for reliability (the intended "know what you don't know"); the default (no gating)
is byte-identical. Do NOT re-attach the parse (post-hoc re-attachment is the wrong architecture and hurts UAS);
precision-WEIGHT the readout only.

Glass-box, deterministic, NO external LLM (the invariant). ASCII-only.
"""
from __future__ import annotations

from typing import Dict, Optional, Sequence

import numpy as np

from hdlab import graded_competition as GC

NOMINAL = ("NOUN", "PROPN", "PRON")
LABELED_PATIENT_RELS = ("obj", "nsubj:pass")

# ------------------------------------------------------------------------------------------------
# FROZEN calibrators -- fit offline on FULL UD-EWT train (n_patient=11018 arcs, n_obl=20556 arcs) via the
# validated cells' logistic_fit (deterministic). Each is (w, mu, sd): standardize x -> (x-mu)/sd, append a bias
# 1, then sigmoid(x_std . w). Reproduces the headline sel@50 EXACTLY (0.9745 / 0.3414 / 0.8919). DO NOT EDIT --
# regenerate only by re-running the offline fit if the feature set or the training corpus changes.
# ------------------------------------------------------------------------------------------------
_PATIENT_FULL_W = np.array([
    -0.04910294183118146, 0.3307089460535503, 0.20580265676405873, 0.3174645201450252,
    0.17824034182046883, 0.2567581807805554, 1.149179046871674, 0.28989048052780375,
    3.2113380576959716], dtype=np.float64)
_PATIENT_FULL_MU = np.array([
    0.9993296545630391, 0.9664160736221064, 0.9331115817273826, 0.3414567080820171,
    0.3040479215828681, 0.9369312865188199, 0.9165002722817208, 0.09593392630241424], dtype=np.float64)
_PATIENT_FULL_SD = np.array([
    0.013756861534491972, 0.104638870653958, 0.17006358907326305, 0.11438427038578182,
    0.13970724287864114, 0.1501683473438679, 0.27663608539471374, 0.294500608956263], dtype=np.float64)

# PARSE-CONFIDENCE-ONLY calibrator (drops the reader's is_labeled_obj branch indicator -- purely the parser's
# own graded confidence, the brief's signal). Load-bearing: still lifts sel@50 +0.0765 CI-sep on UD-EWT.
_PATIENT_PARSEONLY_W = np.array([
    -0.057039822769227026, 0.324074046516799, 0.10190081753147033, 0.4744689324275267,
    0.8615718027217438, 0.724445256398595, 0.07058667394076326, 2.869569826415019], dtype=np.float64)
_PATIENT_PARSEONLY_MU = np.array([
    0.9993296545630391, 0.9664160736221064, 0.9331115817273826, 0.3414567080820171,
    0.3040479215828681, 0.9369312865188199, 0.09593392630241424], dtype=np.float64)
_PATIENT_PARSEONLY_SD = np.array([
    0.013756861534491972, 0.104638870653958, 0.17006358907326305, 0.11438427038578182,
    0.13970724287864114, 0.1501683473438679, 0.294500608956263], dtype=np.float64)

_OBL_W = np.array([
    0.03791764005681393, 0.6879517740106396, 0.5614508063523383, 0.36978194637429673,
    -0.20078833018677816, 2.5983175514576744], dtype=np.float64)
_OBL_MU = np.array([
    0.994047749669549, 0.8963958204566238, 0.8461663918992223, 0.28013505617953166,
    0.5905493935266267], dtype=np.float64)
_OBL_SD = np.array([
    0.05437090323574055, 0.2064099930664466, 0.2570513360780771, 0.1221728246935762,
    0.2606057910886514], dtype=np.float64)


def logistic_p(X, w, mu, sd) -> np.ndarray:
    """Frozen-logistic sigmoid over standardized features + bias. Copied VERBATIM from the validated cell."""
    Xs = (np.asarray(X, float) - mu) / sd
    Xs = np.hstack([Xs, np.ones((len(Xs), 1))])
    return 1.0 / (1.0 + np.exp(-Xs @ w))


# ------------------------------------------------------------------------------------------------
# reliability features for ONE patient arc (glass-box; the parser's own margins + the role competition).
# _role_entropy + the row/feature builders are copied VERBATIM from exp_precwt_live_whodidwhat_v1.
# ------------------------------------------------------------------------------------------------
def _role_entropy(toks, pos, v, heads, labels, passive):
    """graded_competition ENTROPY over the patient candidates (REUSE the landed organ). Candidates = the verb's
    nominal dependents; cues = labeled-obj match (validity high), expected-side, locality. HIGH entropy = the
    patient is genuinely competed = unreliable. Returns (neg_entropy_as_confidence, margin)."""
    n = len(toks)
    cands = [c for c in range(1, n + 1) if heads.get(c) == v and pos[c - 1] in NOMINAL]
    if len(cands) < 2:
        return 1.0, 3.0                      # no competition -> maximally reliable
    want = "nsubj:pass" if passive else "obj"
    loc = [-abs(c - v) for c in cands]
    lab = [1.0 if labels.get(c) == want else 0.0 for c in cands]
    side = [1.0 if ((c < v) if passive else (c > v)) else 0.0 for c in cands]
    supports = {"loc": loc, "lab": lab, "side": side}
    weights = {"loc": 0.3, "lab": 2.0, "side": 1.0}       # cue validities (labeled dominant) -- Bates-MacWhinney
    gp = GC.graded_pick(supports, weights)
    return 1.0 - float(gp["entropy"]), float(gp["margin"])


def patient_row(toks: Sequence[str], pos: Sequence[str], heads: Dict[int, int], conf: Dict[int, float],
                marg: Dict[int, float], v: int, pk: int, labels: Dict[int, str],
                passive: bool, a2_marg: float = 0.0) -> Dict[str, float]:
    """Build the glass-box reliability row for the patient arc `pk` of verb `v` (both 1-based). Byte-identical
    to exp_precwt_live_whodidwhat_v1.build_rows' per-row dict. `a2_marg` = the global arc_parser margin at pk
    (an attachment-site cue; INERT for the patient by measurement -- pass 0.0 if unavailable, byte-safe)."""
    ncand = sum(1 for c in range(1, len(toks) + 1) if heads.get(c) == v and pos[c - 1] in NOMINAL)
    gc_conf, _gc_marg = _role_entropy(toks, pos, v, heads, labels, passive)
    return {"ae_conf": float(conf.get(pk, 0.0)), "ae_marg": float(marg.get(pk, 0.0)), "a2_marg": float(a2_marg),
            "dist": pk - v, "ncand": ncand, "gc_conf": gc_conf,
            "is_lab": float(labels.get(pk, "") in LABELED_PATIENT_RELS), "passive": float(passive)}


def patient_feats(row: Dict[str, float]):
    """The FULL patient calibration inputs (8). Copied VERBATIM from exp_precwt_live_whodidwhat_v1._feats."""
    return [row["ae_conf"], np.tanh(row["ae_marg"] / 20.0), np.tanh(row["a2_marg"] / 5.0),
            1.0 / (1.0 + abs(row["dist"])), min(row["ncand"], 6) / 6.0,
            row["gc_conf"], row["is_lab"], row["passive"]]


def patient_feats_parseonly(row: Dict[str, float]):
    """PARSE-CONFIDENCE-ONLY inputs (7; drops is_labeled_obj). VERBATIM from ..._feats_parseonly."""
    return [row["ae_conf"], np.tanh(row["ae_marg"] / 20.0), np.tanh(row["a2_marg"] / 5.0),
            1.0 / (1.0 + abs(row["dist"])), min(row["ncand"], 6) / 6.0, row["gc_conf"], row["passive"]]


def patient_confidence(row: Dict[str, float], parse_only: bool = False) -> float:
    """Calibrated reliability of a patient arc in [0,1] (higher = more reliable) from its `patient_row`.
    parse_only=True uses the parser-confidence-only calibrator (no reader-branch indicator)."""
    if parse_only:
        return float(logistic_p([patient_feats_parseonly(row)],
                                _PATIENT_PARSEONLY_W, _PATIENT_PARSEONLY_MU, _PATIENT_PARSEONLY_SD)[0])
    return float(logistic_p([patient_feats(row)], _PATIENT_FULL_W, _PATIENT_FULL_MU, _PATIENT_FULL_SD)[0])


def calibrated_patient_confidence(toks, pos, heads, conf, marg, v: int, pk: int, labels: Dict[int, str],
                                  passive: bool, a2_marg: float = 0.0, parse_only: bool = False) -> float:
    """Convenience: build the row + score it. `heads/conf/marg` come from arceager_parser.parse_with_conf;
    `labels` from the shared arc labeler; `passive` from relcl_resolver.precise_passive; `a2_marg` (optional)
    from the global arc_parser margin at pk."""
    return patient_confidence(patient_row(toks, pos, heads, conf, marg, v, pk, labels, passive, a2_marg),
                              parse_only=parse_only)


# ------------------------------------------------------------------------------------------------
# reliability features for ONE obl/nmod attachment arc. VERBATIM from exp_precwt_live_obl_space_v1.
# ------------------------------------------------------------------------------------------------
def obl_row(toks: Sequence[str], pos: Sequence[str], conf: Dict[int, float], marg: Dict[int, float],
            c: int, ph: int, a2_marg: float = 0.0) -> Dict[str, float]:
    """Reliability row for the obl/nmod nominal `c` (1-based) whose parser head is `ph`. VERBATIM from
    obl_rows: ncand = (#VERB attachment sites)+1; dist = ph - c."""
    ncand = sum(1 for u in range(1, len(toks) + 1) if pos[u - 1] == "VERB") + 1
    return {"ae_conf": float(conf.get(c, 0.0)), "ae_marg": float(marg.get(c, 0.0)), "a2_marg": float(a2_marg),
            "dist": ph - c, "ncand": ncand}


def obl_feats(row: Dict[str, float]):
    """obl calibration inputs (5). Copied VERBATIM from exp_precwt_live_obl_space_v1._feats. NOTE: the global
    arc_parser margin (a2_marg) is KEPT for obl (it is an attachment-site cue -- load-bearing here, unlike the
    patient where it is inert)."""
    return [row["ae_conf"], np.tanh(row["ae_marg"] / 20.0), np.tanh(row["a2_marg"] / 5.0),
            1.0 / (1.0 + abs(row["dist"])), min(row["ncand"], 6) / 6.0]


def obl_confidence(row: Dict[str, float]) -> float:
    """Calibrated reliability of an obl/nmod attachment arc in [0,1] from its `obl_row`."""
    return float(logistic_p([obl_feats(row)], _OBL_W, _OBL_MU, _OBL_SD)[0])


def calibrated_obl_confidence(toks, pos, conf, marg, c: int, ph: int, a2_marg: float = 0.0) -> float:
    """Convenience: build the obl row + score it."""
    return obl_confidence(obl_row(toks, pos, conf, marg, c, ph, a2_marg))


def defer(confidence: float, threshold: Optional[float]) -> bool:
    """The precision-weighting decision: DEFER (abstain / fall back to the robust readout) when the arc's
    calibrated reliability is below `threshold`. threshold=None (the default) -> never defer (byte-identical to
    the blanket reader). This is the Kiani-Shadlen opt-out / Friston 'do not hard-commit an unreliable cue'."""
    if threshold is None:
        return False
    return float(confidence) < float(threshold)


__all__ = ["logistic_p", "patient_row", "patient_feats", "patient_feats_parseonly", "patient_confidence",
           "calibrated_patient_confidence", "obl_row", "obl_feats", "obl_confidence",
           "calibrated_obl_confidence", "defer", "NOMINAL", "LABELED_PATIENT_RELS"]
