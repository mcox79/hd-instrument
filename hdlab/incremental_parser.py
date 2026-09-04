"""Incremental left-corner argument-structure builder -- the parser's STRUCTURAL front-end, done the brain's way.

Landed 2026-08-27 (consolidation phase) from the integrated `the_argument_parser_is_batch_where_the_brain_is_incremental`
(SOLVED/EXCELLENT, owner-DONE; witness `verify_incremental_argstruct_builder.py` PASS, re-verified first-hand). The
substrate's front-end used a BATCH UD dependency parse (`candidate_generator`/`arc_parser`) to propose a verb's
candidate arguments; the brain reads LEFT-TO-RIGHT, committing incrementally under a bounded buffer. This organ is
the brain's version, and it BEATS the batch parser at candidate-argument identification (F1 0.6201 vs 0.5849,
+0.0352 CI-sep on modern QA-SRL) via a PRECISION gain (the batch parser OVER-GENERATES +1.03 args/predicate).

WHAT IS PINNED (copy the operation):
  * INCREMENTAL, left-to-right processing under the NOW-OR-NEVER bottleneck (Christiansen & Chater 2016): commit
    to a structure as each word arrives; do not wait for the sentence to end. Genuinely incremental (prefix-
    consistency 0.985 vs the batch 0.941): a prefix parse is consistent with the full parse -- eager bindings do
    not retract (with revision off).
  * LEFT-CORNER projection: on a VERB, eagerly bind the nearest preceding buffered nominal as the pre-verbal
    (subject) slot -- a bottom-up bind from a BOUNDED, lossy recent-nominal buffer (Now-or-Never: memory is
    bounded, so distant material is lost). On a following NOMINAL, eagerly fill the post-verbal (patient) slot
    (Ferreira/Frazier "good-enough" bounded attachment -- at most one extra argument). The F1 win is THIS eager
    bounded attachment, NOT prediction or revision (both ~0 on clean edited prose; honest attribution).
  * PREDICTION (optional, default ON but ~neutral on aggregate): a competing later post-verbal nominal is
    resolved by verb->PATIENT selectional-preference fit (reuse `hdlab.predictive_reader`). REVISION (optional,
    default OFF): NP/S garden-path reanalysis when a two-route conflict forces it -- brain-faithful (garden-path
    positive control re-attaches +0.0852 CI-sep, ZERO false-fire) but it HURTS clean edited prose, so it is
    default-off "don't reanalyse unless forced."

ARCHITECTURE-FIDELITY (from the integration): structure-BUILDING (this organ) and role-BINDING (the role
assigner) are SEPARATE organs (Beber 2025 double dissociation; frontal/pMTG vs posterior-temporal/angular) --
keep them separate; this proposes CANDIDATES, the role assigner labels them. And the discrete eager decision is
the noise->0 limit of graded cue-based competition (hdlab.graded_competition) -- the same substrate-wide
discrete->graded story; expose the competition where a graded readout is wanted.

DEFAULT-SAFE / ISLAND: a NEW module -- importing it changes NO existing behaviour. `incremental_build` is a pure
function of (tokens, UPOS[, predictor]); with `predictor=None` the structural core runs (prediction inert). Wire
as the CANDIDATE SOURCE behind a flag (role assigner unchanged; prediction ON, revision OFF; route reversibles to
the relcl resolver). MEASURE on the live reader before any capability claim.
"""
from __future__ import annotations

from typing import Dict, List, Optional, Sequence, Set, Tuple

import numpy as np

from hdlab.candidate_generator import NOMINAL          # single source of truth for nominal UPOS tags
from hdlab.grounded_similarity import grounded_vector  # for the optional prediction/revision fit
from hdlab.predictive_reader import PredictiveReader

_EPS = 1e-9
_LEMMA_CACHE: Dict[str, str] = {}


def _g(word: str) -> Optional[np.ndarray]:
    v = grounded_vector(word)
    return None if v is None else np.asarray(v, dtype=np.float64).reshape(-1)


def _cos(a: Optional[np.ndarray], b: Optional[np.ndarray]) -> float:
    if a is None or b is None:
        return -1.0
    na, nb = float(np.linalg.norm(a)), float(np.linalg.norm(b))
    if na < _EPS or nb < _EPS:
        return 0.0
    return float(np.dot(a, b) / (na * nb))


def _lemma(w: str) -> str:
    wl = w.lower()
    if wl in _LEMMA_CACHE:
        return _LEMMA_CACHE[wl]
    try:
        from hdlab.thematic_role_labeler import lemma_verb
        out = lemma_verb(wl)
    except Exception:  # noqa: BLE001
        out = wl
    _LEMMA_CACHE[wl] = out
    return out


def incremental_build(
    toks: Sequence[str],
    pos: Sequence[str],
    predictor: Optional[PredictiveReader] = None,
    *,
    use_predict: bool = True,
    use_revise: bool = False,
    buffer_n: int = 3,
    conflict_margin: float = 0.15,
    stop_at: Optional[int] = None,
) -> Dict[int, Set[int]]:
    """Left-to-right verb-slot-projection builder. Returns {verb_index: {arg_index, ...}} (1-based indices).

    On a VERB: open a frame; eagerly bind the nearest preceding buffered nominal as the pre-verbal (subject)
      slot -- the left-corner bottom-up bind; set it active.
    On a NOMINAL after the active verb: fill the verb's post-verbal (patient) slot eagerly (Now-or-Never). A
      competing later post-verbal nominal is resolved by PREDICTION (verb->PATIENT selectional-preference fit):
      the better-fitting nominal takes the patient slot, the other becomes a second argument (bounded good-enough:
      at most one extra).
    REVISION (default OFF): on a two-route conflict (a following verb needs a subject and the last eager patient
      fits its verb poorly), re-attach that nominal to the new verb's subject slot (bounded, local NP/S reanalysis).
    `stop_at` truncates the token stream (for the glass-box prefix-consistency / incrementality test)."""
    n = len(toks) if stop_at is None else min(stop_at, len(toks))
    frames: Dict[int, Dict[str, Optional[int]]] = {}
    buffer: List[int] = []                          # recent nominal indices (bounded lossy buffer)
    active_verb: Optional[int] = None
    last_bound: Optional[Tuple[int, int]] = None    # (verb, arg) most-recent eager patient bind

    def fit_to_patient(verb_tok: str, arg_idx: int) -> float:
        if predictor is None:
            return 0.0
        c = predictor.predict(_lemma(verb_tok), "PATIENT")
        return _cos(_g(toks[arg_idx - 1].lower()), c) if c is not None else 0.0

    for i in range(1, n + 1):
        tag = pos[i - 1]
        if tag == "VERB":
            if use_revise and last_bound is not None and buffer:
                v1, a1 = last_bound
                if a1 == buffer[-1] and a1 < i and frames.get(v1, {}).get("obj") == a1:
                    if fit_to_patient(toks[v1 - 1], a1) < conflict_margin:
                        frames[v1]["obj"] = None
                        frames.setdefault(i, {"subj": None, "obj": None, "obj2": None})
                        frames[i]["subj"] = a1
            frames.setdefault(i, {"subj": None, "obj": None, "obj2": None})
            if frames[i]["subj"] is None and buffer:
                frames[i]["subj"] = buffer[-1]      # left-corner bottom-up bind
            active_verb = i
            last_bound = None
        elif tag in NOMINAL:
            if active_verb is not None and i > active_verb:
                f = frames[active_verb]
                if f["obj"] is None:
                    f["obj"] = i
                    last_bound = (active_verb, i)
                else:
                    if use_predict:
                        vtok = toks[active_verb - 1]
                        if fit_to_patient(vtok, i) > fit_to_patient(vtok, f["obj"]) + _EPS:
                            f["obj2"], f["obj"] = f["obj"], i
                            last_bound = (active_verb, i)
                        elif f["obj2"] is None:
                            f["obj2"] = i
                    elif f["obj2"] is None:
                        f["obj2"] = i
            buffer.append(i)
            buffer = buffer[-buffer_n:]             # bounded lossy buffer (Now-or-Never)
        # non-verb, non-nominal tokens do not change bindings (good-enough)

    out: Dict[int, Set[int]] = {}
    for v, f in frames.items():
        out[v] = {x for x in (f.get("subj"), f.get("obj"), f.get("obj2")) if x is not None}
    return out


def incremental_subject_before(
    toks: Sequence[str],
    pos: Sequence[str],
    buffer_n: int = 3,
) -> List[Optional[int]]:
    """subj_before[i] = the incremental left-corner SUBJECT token index for a verb at position i: the nearest
    preceding nominal held in a bounded (buffer_n) lossy buffer (Now-or-Never). This REPRODUCES the subject
    rule of incremental_build (frames[verb].subj = buffer[-1]), generalized to EVERY token position so it is
    robust to event-extractor/tagger verb-index mismatches. Register-general, glass-box: reads only toks/UPOS.
    Returns a list of length len(toks) (None where no nominal precedes).

    Promoted VERBATIM (2026-09-04) from the owner-DONE
    `the_agent_tie_wall_is_embedded_clauses_needs_a_register_general_incremental_parse_cue`
    (reference impl experiments/exp_cmrole_agent_struct_v1.py:incremental_subject_before). It is the
    register-general STRUCTURE cue source for the Competition-Model AGENT competition
    (hdlab.graded_role_assigner.agent_supports): the parser's SUBJECT ATTACHMENT enters the role competition
    as ONE self-gating precision-weighted vote (Matchin-Hickok separate pools; eADM). 0-based indices."""
    n = len(toks)
    out: List[Optional[int]] = [None] * n
    buf: List[int] = []
    for i in range(n):
        out[i] = buf[-1] if buf else None            # buffer state BEFORE token i => subject for a verb AT i
        tag = pos[i] if i < len(pos) else None
        if tag in NOMINAL:
            buf.append(i)
            buf = buf[-buffer_n:]
    return out


__all__ = ["incremental_build", "incremental_subject_before"]
