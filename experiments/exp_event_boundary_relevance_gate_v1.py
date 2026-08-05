"""RELEVANCE GATE for event segmentation (drill: notes/research_brain_event_segmentation_2026-08-05.md).

Brain grounding: the brain's event unit is a situation-model DISCONTINUITY (Zwaan &
Radvansky 1998 event-indexing model: TIME / SPACE / CAUSATION / INTENTIONALITY(GOAL) /
PROTAGONIST). Zacks & Speer 2009 (VERIFIED in the drill) found segmentation is SELECTIVE,
not blanket: a clause becomes a boundary only when one of the 5 dimensions actually shifts,
not every content predicate. Our extractor (experiments/_temporal_ordering.py extract_events,
wired through hdlab/situation_reader.py _read_events) currently makes EVERY syntactically-
valid content verb an event unconditionally -- over-segmentation, the "every-verb-is-an-
event" baseline this cell tests against.

THIS CELL IS A POST-HOC FILTER, NOT A CHANGE TO EXTRACTION. It consumes the SAME
SituationModel.events list hdlab/situation_reader.py already produces (no edits to
_read_events / extract_events / SituationReader) and computes, for each event relative to
the immediately preceding event, an is_boundary flag: True iff >=1 available Zwaan dimension
differs from the previous event's state. Three of the five Zwaan dimensions are available
from ALREADY-OWNED readers with NO new organ:
  PROTAGONIST : agent head string, resolved through the coref entity-cluster lookup already
                built by hdlab/situation_reader.py._build_entities (SituationModel.entities).
  TIME        : EventRecord.tense, already computed by _temporal_ordering.extract_events
                (SIMPLE_PAST / PAST_PERFECT / PASSIVE / MODAL_SUBORDINATE / PARTICIPIAL).
  CAUSATION   : whether the event's sentence carries a CausalLink, already computed by
                hdlab/situation_reader.py._read_causation (experiments/_causal_network.py).
SPACE and INTENTIONALITY/GOAL have NO signal in any owned reader (no spatial-marker reader,
no goal-tracking organ beyond the narrow certified-scope affect axis, which is not a general
goal-state signal) -- named here as the two dims this prototype cannot gate on; route:
SUPPLY (a spatial-preposition/locative-NP reader) or BUILD (goal-state tracking) if wanted.

GLASS-BOX: is_boundary() returns not just a bool but the list of triggering dimension names
(protagonist/time/causation/segment_start) per event -- fully inspectable, no black box.

EVAL: hand-authored small proxy corpus (4 short synthetic passages, LitBank-CoNLL-style temp
files via the SAME _write_temp_conll helper hdlab/situation_reader.py's own self-tests use).
Gold event-boundary labels were fixed at PASSAGE-DESIGN time (before any gate code ran) from
ordinary narrative-continuity judgment: does the situation genuinely change between this event
and the previous one (new protagonist, a flashback/tense jump, a causal episode opening or
closing) or does it continue the same state of affairs. This is the "principled proxy" the
drill's memo names (Zacks & Speer 2009 code boundaries the same way against clause-level cues).
HONEST CAVEAT: n=17 events / 13 non-trivial pairs is a PROTOTYPE-SCALE corpus, hand-built by
the same author who wrote the gate -- construction-determined risk is real; this is a cheap
decisive smoke on the MECHANISM, not a claim of general-corpus event-boundary accuracy. No
LitBank event-boundary gold exists to score against (situation_reader.py's own docstring notes
NO LitBank role/event gold is used elsewhere in this reader either).

PRE-REGISTRATION (envelope-fail-bands, fixed before running):
  HARD-PASS: gated is_boundary raises precision-against-gold by >=10 points vs the
    every-verb-is-a-boundary baseline, recall loss <=15 points, AND a scramble control
    (shuffle the per-event dimension-signal tuples within each passage, fixed seeds) collapses
    the precision gain (scrambled precision-gain < 5 points, i.e. <50% of the un-scrambled gain).
  MIDDLE_BAND: precision gain in [3,10) points, or scramble only partially collapses the gain
    (>=50% but <90% retained).
  HARD-FAIL: precision gain <3 points, OR recall collapses >30 points, OR scramble control
    RETAINS >=90% of the gate's precision gain (the gate is not actually tracking the intended
    dimension signals -- any fixed per-event feature grouping would have scored the same).

NO-REGRESSION: this module imports hdlab.situation_reader / experiments._temporal_ordering
read-only; it edits neither. _run_all_selftests() in situation_reader.py is untouched.

ASCII-only. Deterministic (fixed seeds for scramble control). No LLM, no network, no autograd.
"""
from __future__ import annotations

import json
import os
import random
import sys
import time

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from hdlab.situation_reader import SituationReader, _write_temp_conll  # noqa: E402

OUTPUT_DIR = os.path.join(_REPO, "data", "exp_event_boundary_relevance_gate_v1")
SCRAMBLE_SEEDS = (1, 2, 3, 4, 5)


# ===========================================================================
# Proxy corpus: 4 short passages, gold boundary labels fixed BEFORE gate ran.
# rows format matches hdlab/situation_reader.py._write_temp_conll: (sent_idx, wtok, tok, coref).
# gold[i] = is event i (in extraction order within the passage) a genuine situation-model
# boundary relative to the immediately preceding event. gold[0] is always True by definition
# (segment start) for every passage -- not a discriminating instance, included for completeness.
# ===========================================================================
def _passage_protagonist_shift():
    # John walked / John bought bread (same protagonist, continuation) / Mary called John
    # (protagonist shift: John -> Mary) / Mary smiled (continuation).
    rows = [
        (0, 0, "John", "(0)"), (0, 1, "walked", "_"), (0, 2, ".", "_"),
        (1, 0, "John", "(0)"), (1, 1, "bought", "_"), (1, 2, "bread", "_"), (1, 3, ".", "_"),
        (2, 0, "Mary", "(1)"), (2, 1, "called", "_"), (2, 2, "John", "(0)"), (2, 3, ".", "_"),
        (3, 0, "Mary", "(1)"), (3, 1, "smiled", "_"), (3, 2, ".", "_"),
    ]
    gold = [True, False, True, False]  # walked | bought(NO) | called(YES prot) | smiled(NO)
    return rows, gold, {"john": "masc", "mary": "fem"}


def _passage_tense_shift():
    # Mary cried (narrative-now) / Mary had finished (PAST_PERFECT flashback: YES) /
    # Mary had forgotten everything (still PAST_PERFECT: NO) / Mary arrived (back to
    # narrative-now: YES). Same protagonist and no causal connective throughout -- isolates
    # the TIME dimension.
    rows = [
        (0, 0, "Mary", "(0)"), (0, 1, "cried", "_"), (0, 2, ".", "_"),
        (1, 0, "Mary", "(0)"), (1, 1, "had", "_"), (1, 2, "finished", "_"), (1, 3, ".", "_"),
        (2, 0, "Mary", "(0)"), (2, 1, "had", "_"), (2, 2, "forgotten", "_"),
        (2, 3, "everything", "_"), (2, 4, ".", "_"),
        (3, 0, "Mary", "(0)"), (3, 1, "arrived", "_"), (3, 2, ".", "_"),
    ]
    gold = [True, True, False, True]
    return rows, gold, {"mary": "fem"}


def _passage_causal_shift():
    # Peter walked / Peter smiled (continuation, NO) / Window broke because Peter pushed it
    # (2 events in one sentence: protagonist Peter->Window then Window->Peter, both YES; the
    # sentence opens a causal episode) / Peter apologized (protagonist unchanged, tense
    # unchanged, but the causal episode CLOSES -- causal_state True->False -- isolates
    # the CAUSATION dimension in isolation from protagonist/tense).
    rows = [
        (0, 0, "Peter", "(0)"), (0, 1, "walked", "_"), (0, 2, ".", "_"),
        (1, 0, "Peter", "(0)"), (1, 1, "smiled", "_"), (1, 2, ".", "_"),
        (2, 0, "Window", "(1)"), (2, 1, "broke", "_"), (2, 2, "because", "_"),
        (2, 3, "Peter", "(0)"), (2, 4, "pushed", "_"), (2, 5, "it", "_"), (2, 6, ".", "_"),
        (3, 0, "Peter", "(0)"), (3, 1, "apologized", "_"), (3, 2, ".", "_"),
    ]
    gold = [True, False, True, True, True]  # walked|smiled(NO)|broke(YES)|pushed(YES)|apologized(YES, causal-close)
    return rows, gold, {"peter": "masc"}


def _passage_multi_continuation():
    # Anna cheered / danced / laughed (3-way continuation, same protagonist) / Tom watched
    # Anna (protagonist shift: YES). Stress-tests that the gate does NOT over-fire on a run of
    # same-protagonist same-tense non-causal events (the discriminating case for precision).
    # NOTE: regular -ed verbs only (not "sang") -- hdlab/scene_segment.py parse_conll_sentences
    # LOWERCASES tokens before they reach the shared POS tagger (pre-existing, out-of-scope-to-
    # fix behavior of a banked shared component); an irregular no-suffix past tense ("sang") then
    # loses its only VBD cue (sentence-initial capitalization) and the tagger mistags it NN,
    # silently dropping the event. Regular -ed verbs keep the suffix cue and tag VBD regardless
    # of case, so this passage avoids the artifact rather than routing around a shared organ.
    rows = [
        (0, 0, "Anna", "(0)"), (0, 1, "cheered", "_"), (0, 2, ".", "_"),
        (1, 0, "Anna", "(0)"), (1, 1, "danced", "_"), (1, 2, ".", "_"),
        (2, 0, "Anna", "(0)"), (2, 1, "laughed", "_"), (2, 2, ".", "_"),
        (3, 0, "Tom", "(1)"), (3, 1, "watched", "_"), (3, 2, "Anna", "(0)"), (3, 3, ".", "_"),
    ]
    gold = [True, False, False, True]
    return rows, gold, {"anna": "fem", "tom": "masc"}


PASSAGES = [
    ("protagonist_shift", _passage_protagonist_shift),
    ("tense_shift", _passage_tense_shift),
    ("causal_shift", _passage_causal_shift),
    ("multi_continuation", _passage_multi_continuation),
]


def _read_passage(builder):
    rows, gold, gaz = builder()
    path = _write_temp_conll(rows)
    try:
        reader = SituationReader(gaz=gaz)
        sm = reader.read(path)
    finally:
        try:
            os.remove(path)
        except OSError:
            pass
    if len(sm.events) != len(gold):
        raise RuntimeError(
            f"EXTRACTION_MISMATCH: builder produced {len(gold)} gold labels but the "
            f"reader extracted {len(sm.events)} events: {[e.predicate for e in sm.events]}")
    return sm, gold


# ===========================================================================
# The relevance gate: is_boundary via Zwaan dimension discontinuity.
# ===========================================================================
def _entity_lookup(sm):
    """head-surface (lower) -> coref entity cluster id, reusing SituationModel.entities
    (the SAME cross-sentence coref backbone _read_entities/_build_entities already built)."""
    lut = {}
    for ent in sm.entities:
        for h in ent.heads:
            lut[h.lower()] = ent.cluster
    return lut


def _event_signals(sm):
    """Per-event (protagonist, tense, causal) signal tuple, in extraction order."""
    lut = _entity_lookup(sm)
    causal_sents = {lk.sent_idx for lk in sm.causal_links}
    sigs = []
    for ev in sm.events:
        prot = None if ev.agent == "?" else lut.get(ev.agent.lower(), ev.agent.lower())
        sigs.append((prot, ev.tense, ev.sent_idx in causal_sents))
    return sigs


def is_boundary_gate(sm):
    """Return (preds, triggers): preds[i] = bool (this event starts a new segment),
    triggers[i] = list of dimension names that fired ('protagonist'|'time'|'causation'|
    'segment_start'). preds[0] is always True (first event = segment start, both arms agree)."""
    sigs = _event_signals(sm)
    preds, triggers = [], []
    prev = None
    for i, sig in enumerate(sigs):
        if prev is None:
            preds.append(True)
            triggers.append(["segment_start"])
        else:
            dims = []
            if sig[0] != prev[0]:
                dims.append("protagonist")
            if sig[1] != prev[1]:
                dims.append("time")
            if sig[2] != prev[2]:
                dims.append("causation")
            preds.append(len(dims) > 0)
            triggers.append(dims)
        prev = sig
    return preds, triggers


def baseline_every_verb(sm):
    """The CURRENT (ungated) behavior: every extracted predicate is unconditionally an
    event/boundary. This is literally what _read_events already does today -- the cell
    changes nothing about extraction, only adds this gate as a NEW consumer."""
    return [True] * len(sm.events)


def scrambled_gate(sm, seed):
    """SCRAMBLE CONTROL: shuffle the per-event (protagonist,tense,causal) signal tuples
    WITHIN this passage (segment-start position kept, so preds[0] still True for both arms),
    then apply the SAME discontinuity rule to the shuffled signal sequence. If the gate's
    precision gain over baseline survives this shuffle, the gate is not actually keyed to the
    per-event dimension VALUES -- any fixed grouping of the same multiset would do as well."""
    sigs = _event_signals(sm)
    n = len(sigs)
    if n <= 1:
        return [True] * n
    rng = random.Random(seed)
    rest = list(range(1, n))
    rng.shuffle(rest)
    order = [0] + rest  # keep position 0 = the true first-event signal (segment start)
    shuffled = [sigs[j] for j in order]
    preds = []
    prev = None
    for i, sig in enumerate(shuffled):
        if prev is None:
            preds.append(True)
        else:
            fired = (sig[0] != prev[0]) or (sig[1] != prev[1]) or (sig[2] != prev[2])
            preds.append(bool(fired))
        prev = sig
    return preds


# ===========================================================================
# Scoring
# ===========================================================================
def _prf1(preds, gold):
    tp = sum(1 for p, g in zip(preds, gold) if p and g)
    fp = sum(1 for p, g in zip(preds, gold) if p and not g)
    fn = sum(1 for p, g in zip(preds, gold) if (not p) and g)
    n_pos_gold = sum(1 for g in gold if g)
    n_pos_pred = sum(1 for p in preds if p)
    precision = (tp / n_pos_pred) if n_pos_pred else 0.0
    recall = (tp / n_pos_gold) if n_pos_gold else 0.0
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) else 0.0
    return {"precision": precision, "recall": recall, "f1": f1, "tp": tp, "fp": fp, "fn": fn,
            "n": len(gold), "n_pos_gold": n_pos_gold, "n_pos_pred": n_pos_pred}


# ===========================================================================
# Self-test (formula-selftest gate per exp_dev discipline: verify the wiring
# BEFORE trusting the corpus-level metrics below).
# ===========================================================================
def _selftest():
    sm, gold = _read_passage(_passage_protagonist_shift)
    preds, triggers = is_boundary_gate(sm)
    assert preds == gold, f"protagonist_shift passage: preds={preds} gold={gold}"
    assert triggers[2] == ["protagonist"], f"expected protagonist-only trigger: {triggers[2]}"
    assert triggers[0] == ["segment_start"]
    base = baseline_every_verb(sm)
    assert base == [True] * len(gold)
    scr = scrambled_gate(sm, seed=1)
    assert len(scr) == len(gold)
    return {"selftest": "pass", "n_events": len(sm.events)}


# ===========================================================================
# Full run (smoke = protagonist_shift passage only; full = all 4 passages).
# ===========================================================================
def run(smoke: bool = False):
    passages = PASSAGES[:1] if smoke else PASSAGES
    all_gold, all_gate, all_base = [], [], []
    all_scrambled = {seed: [] for seed in SCRAMBLE_SEEDS}
    per_passage = []
    for name, builder in passages:
        sm, gold = _read_passage(builder)
        gate_preds, triggers = is_boundary_gate(sm)
        base_preds = baseline_every_verb(sm)
        all_gold.extend(gold)
        all_gate.extend(gate_preds)
        all_base.extend(base_preds)
        scr_this = {}
        for seed in SCRAMBLE_SEEDS:
            scr_preds = scrambled_gate(sm, seed)
            all_scrambled[seed].extend(scr_preds)
            scr_this[seed] = scr_preds
        per_passage.append({
            "name": name, "n_events": len(sm.events),
            "predicates": [e.predicate for e in sm.events],
            "gold": gold, "gate_preds": gate_preds, "triggers": triggers,
            "base_preds": base_preds,
        })

    gate_score = _prf1(all_gate, all_gold)
    base_score = _prf1(all_base, all_gold)
    precision_gain_pts = 100.0 * (gate_score["precision"] - base_score["precision"])
    recall_loss_pts = 100.0 * (base_score["recall"] - gate_score["recall"])

    scramble_scores = {}
    scramble_gain_pts = []
    for seed in SCRAMBLE_SEEDS:
        s = _prf1(all_scrambled[seed], all_gold)
        scramble_scores[str(seed)] = s
        scramble_gain_pts.append(100.0 * (s["precision"] - base_score["precision"]))
    mean_scramble_gain_pts = sum(scramble_gain_pts) / len(scramble_gain_pts)
    scramble_retained_frac = (
        (mean_scramble_gain_pts / precision_gain_pts) if precision_gain_pts > 0 else None)

    if precision_gain_pts >= 10.0 and recall_loss_pts <= 15.0 and (
            scramble_retained_frac is not None and scramble_retained_frac < 0.5):
        verdict = "HARD-PASS"
    elif precision_gain_pts < 3.0 or recall_loss_pts > 30.0 or (
            scramble_retained_frac is not None and scramble_retained_frac >= 0.9):
        verdict = "HARD-FAIL"
    else:
        verdict = "MIDDLE_BAND"

    metrics = {
        "cell": "exp_event_boundary_relevance_gate_v1",
        "smoke": smoke,
        "ts": time.time(),
        "n_passages": len(passages),
        "n_events_total": len(all_gold),
        "gate_score": gate_score,
        "baseline_score": base_score,
        "precision_gain_pts": precision_gain_pts,
        "recall_loss_pts": recall_loss_pts,
        "scramble_scores": scramble_scores,
        "mean_scramble_gain_pts": mean_scramble_gain_pts,
        "scramble_retained_frac": scramble_retained_frac,
        "verdict": verdict,
        "zwaan_dims_available": ["protagonist", "time", "causation"],
        "zwaan_dims_missing": ["space", "intentionality_goal"],
        "reuses_owned_readers": True,
        "per_passage": per_passage,
    }
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    tmp_path = os.path.join(OUTPUT_DIR, "metrics.json.tmp")
    final_path = os.path.join(OUTPUT_DIR, "metrics.json")
    with open(tmp_path, "w", encoding="utf-8", newline="") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp_path, final_path)
    return metrics


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        out = _selftest()
        print(json.dumps(out, indent=2))
        sys.exit(0)
    m = run(smoke=args.smoke)
    print(json.dumps({k: v for k, v in m.items() if k != "per_passage"}, indent=2))
