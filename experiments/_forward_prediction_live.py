"""Live forward-prediction driver: compute predictive_reader surprisal on the LIVE
SituationReader.read() event/argument stream, and score the reader's OWN who-did-what
against gold.

The brain operation being wired (forward half of predictive coding): a verb (+ its thematic
role) PRE-ACTIVATES the expected argument's grounded MEANING features (Altmann & Kamide 1999;
McRae 1998; predict features not word-forms, Nieuwland 2018); the mismatch of the ACTUAL bound
argument against that pre-activation is read out as -log P softmax SURPRISAL (Hale 2001; Levy
2008; Michaelov 2024 -- surprisal is the best single account of the N400). This module makes
that signal LIVE: it drives hdlab.predictive_reader.PredictiveReader over the argument the
reader ITSELF bound to each role in read().

WHAT IS PINNED vs OUR-INVENTION (see the 2026-08-31 research drill folded into SOLVED.md):
  PINNED: the surprisal computation; forward pre-activation of features; that misinterpretation
    (good-enough role errors, Ferreira 2003) lives exactly at low-probability / implausible
    argument sites; that the brain has a distinct conflict/monitoring response there (semantic
    P600, Van Herten & Kolk 2005/06) and can trigger reanalysis/regressions (Levy, Bicknell,
    Slattery & Rayner 2009).
  OUR-INVENTION-UNDER-TEST: that the surprisal of the reader's OWN bound argument is DIAGNOSTIC
    of that binding being a comprehension ERROR (a RISK flag, not a verdict); the decision
    threshold; the grounded space as the feature basis (its coarseness is the known ceiling).

GLASS-BOX, NO external LLM, NO spaCy: the reader's own UD-trained pos_tagger + arc_parser
(role_route='wired') drive role assignment; predictive_reader uses the grounded sensorimotor
space. ASCII only. Deterministic given fixed seeds.
"""
from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import sys
import tempfile
from typing import Dict, List, Optional, Tuple

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from hdlab.pos_tagger import PosTagger
from hdlab.situation_reader import SituationReader
from hdlab.predictive_reader import PredictiveReader
from hdlab.thematic_role_labeler import lemma_word

POS_ASSET = os.path.join(REPO, "data/frontend_assets/pos_tagger_ud_ewt_upos.json")
NOMINAL = {"NOUN", "PROPN", "PRON"}
PRON_LOW = {"i", "you", "he", "she", "it", "we", "they", "me", "him", "her", "us", "them",
            "myself", "yourself", "himself", "herself", "itself", "ourselves", "themselves",
            "this", "that", "these", "those", "who", "whom", "which", "what"}

_TAGGER = None


def get_tagger() -> PosTagger:
    global _TAGGER
    if _TAGGER is None:
        _TAGGER = PosTagger.load(POS_ASSET)
    return _TAGGER


def build_reader(role_route: str = "wired", tense_agnostic: bool = True,
                 verb_subcat_gate: bool = True) -> SituationReader:
    """The role-CAPABLE reader (measure against the correct state, not the weak default):
    tense_agnostic_events maximizes the event set roles attach to; role_route='wired' routes
    agent/patient through the in-substrate parse; verb_subcat_gate suppresses spurious
    intransitive patients. NO spaCy, NO LLM. role_route='positional' = the stock/weak reader."""
    return SituationReader(tense_agnostic_events=bool(tense_agnostic),
                           role_route=role_route,
                           verb_subcat_gate=bool(verb_subcat_gate))


def write_conll_nominals(toks: List[str], up: List[str]) -> str:
    """Mark each NOMINAL token (from the reader's OWN pos tagger) as a singleton coref mention,
    so the reader has its candidate-nominal inventory and does its own role assignment over them.
    This isolates the ROLE-ASSIGNMENT variable exactly as exp_reader_vs_twoline_qasrl_power_v1
    supplies gold-parse nominals as candidates -- the reader still binds roles itself. Returns a
    temp CoNLL path (token in col 3, coref bracket in the last col; blank line ends the sentence)."""
    fd, path = tempfile.mkstemp(suffix=".conll", text=True)
    cid = 0
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        for i, tk in enumerate(toks):
            if up[i] in NOMINAL:
                coref = "(%d)" % cid
                cid += 1
            else:
                coref = "_"
            f.write("\t".join(["s", "0", str(i), tk] + ["_"] * 7 + [coref]) + "\n")
        f.write("\n")
    return path


def nominal_heads(toks: List[str], up: List[str], include_pron: bool = False) -> List[str]:
    """The candidate-argument head strings the reader could bind (lowercased). Pronouns are
    excluded by default (the reader tracks only non-pronoun heads for roles)."""
    out = []
    for i, tk in enumerate(toks):
        if up[i] in NOMINAL:
            low = tk.lower()
            if (not include_pron) and low in PRON_LOW:
                continue
            out.append(low)
    return sorted(set(out))


class ReaderCrash(Exception):
    """A sentence the LIVE reader could not process (a pre-existing hdlab robustness bug in the
    additive frame-primary-role metadata path -- hdlab.frame_induction.is_passive_real indexes
    tokens[i] over range(lo, v_idx) and raises IndexError when the predicate index the event
    extractor emits exceeds the sentence length on a tokenization-alignment edge case). We cannot
    edit hdlab (strategy owns it, Q111); we SKIP + COUNT these and report the rate honestly. It is
    an adjacent-component finding, not a defect in this measurement."""


def read_sentence(reader: SituationReader, toks: List[str], up: List[str]):
    """Run read() on one sentence (nominals auto-marked). Returns sm.events. Raises ReaderCrash
    (skippable) if the live reader raises on this sentence."""
    path = write_conll_nominals(toks, up)
    try:
        sm = reader.read(path)
    except Exception as e:  # noqa: BLE001 -- pre-existing hdlab crash on edge-case sentences
        raise ReaderCrash(f"{type(e).__name__}: {str(e)[:120]}")
    finally:
        try:
            os.remove(path)
        except OSError:
            pass
    return sm.events


def match_event(events, verb_surface: str):
    """The reader's event whose predicate surface matches the gold verb token (first match).
    None if the reader detected no event on that verb (an extraction miss -- reported honestly)."""
    vlow = verb_surface.lower()
    for e in events:
        if str(e.predicate).lower() == vlow:
            return e
    # fall back to lemma match (the detector lowercases; lemma_word normalizes inflection)
    vl = lemma_word(vlow)
    for e in events:
        if lemma_word(str(e.predicate).lower()) == vl:
            return e
    return None


class LiveSurprisal:
    """Wraps a fitted PredictiveReader to score the reader's own bindings.

      surprisal_of(verb, role, filler, cands) -> -log P of `filler` among `cands` (None if
                                                 the verb-role centroid or filler is ungrounded)
      best_alternative(verb, role, cands, exclude) -> (head, surprisal) minimizing surprisal
                                                 over cands != exclude (the noisy-channel
                                                 reanalysis CANDIDATE -- verified, not auto-adopted)
      precision(verb, role) -> selectional-preference concentration (constraint sharpness)
    """

    def __init__(self, predictor: PredictiveReader):
        self.pr = predictor

    def surprisal_of(self, verb: str, role: str, filler: str, cands: List[str]) -> Optional[float]:
        return self.pr.surprisal(verb, role, filler, cands)

    def precision(self, verb: str, role: str) -> Optional[float]:
        return self.pr.precision(verb, role)

    def count(self, verb: str, role: str) -> int:
        return self.pr.count(verb, role)

    def best_alternative(self, verb: str, role: str, cands: List[str],
                         exclude: str) -> Tuple[Optional[str], Optional[float]]:
        best_h, best_s = None, None
        for c in cands:
            if c == exclude:
                continue
            s = self.pr.surprisal(verb, role, c, cands)
            if s is None:
                continue
            if best_s is None or s < best_s:
                best_s, best_h = s, c
        return best_h, best_s


def fit_predictor(train_split: str = "train.jsonl.gz", limit: Optional[int] = 60000,
                  temp: float = 0.5) -> PredictiveReader:
    """Fit PredictiveReader on QA-SRL TRAIN triples (held out from the dev/test eval sentences
    the reader is scored on -- no leakage)."""
    from experiments.exp_predictive_reader_anticipation_surprisal_v1 import extract_triples
    triples = extract_triples(train_split, limit=limit)
    return PredictiveReader(temp=temp).fit(triples)
