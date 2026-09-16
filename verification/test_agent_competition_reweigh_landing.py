"""LANDING WITNESS -- pri 140: the AGENT competition re-weighed from cue validities ACCRUED FROM READING.

WHAT THIS WITNESS PINS (claims, not numbers -- per the standing rule).
  1. THE SPLIT is a real three-way classifier over entity identity and it CAN FAIL: a second token of the gold
     NAME RUN is "right entity, wrong token"; a token of a DIFFERENT entity is "wrong entity"; an NP-internal
     MODIFIER of the gold agent is neither (it is a real misread, not a scoring convention).
  2. THE VALIDITIES ARE COUNTS.  strengths = a pure function of the counts; a reliable cue value earns a
     positive contrast and an anti-reliable one a negative contrast; a value observed once is shrunk toward
     silence (availability); and there is an ONLINE OBSERVE PATH that moves the table (plastic, never frozen).
  3. THE DEFECT IS GONE ON THE LANDED TREE.  Before landing, the only agent cue weights in the organ are the
     HAND-SET `AGENT_VALIDITIES` dict and nothing in the organ reads a learned agent-cue asset.  This witness
     DETECTS the landed state from the live module: on the landed tree it asserts the organ exposes the
     counts-based table and that the live competition consults it; before landing it asserts the same
     capability exists in the experiment cell that proposes it, and says so out loud.
  4. THE INFO-FREE TWIN IS A REAL DESTRUCTION -- permuting the learned strengths within each cue changes the
     activation, so a twin that loses is evidence and not a no-op.
  5. THE RECORDED RESULT, when the cell's metrics are on disk, agrees with itself: the re-weighed arm's
     direction and CI-separation flags are read back from the record rather than re-asserted as constants.

Run: .venv/Scripts/python.exe verification/test_agent_competition_reweigh_landing.py
"""
from __future__ import annotations

import json
import os
import sys

import numpy as np

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import experiments.exp_agent_pick_reweigh_v1 as E          # noqa: E402
import hdlab.graded_role_assigner as GRA                    # noqa: E402

_OK = [True]


def ck(name, cond, extra=""):
    _OK[0] = _OK[0] and bool(cond)
    print("  [%s] %s%s" % ("PASS" if cond else "FAIL", name, ("   %s" % (extra,)) if extra != "" else ""))


def landed():
    """Is the pri 140 arm IN THE ORGAN (landed) or still only in the experiment cell (proposed)?"""
    return hasattr(GRA, "agent_competition_reweighed") and hasattr(GRA, "load_agent_validities")


def test_split_is_a_real_classifier():
    sent = [{"id": 1, "form": "Kori", "upos": "PROPN", "head": 2, "deprel": "nsubj", "dep": "nsubj"},
            {"id": 2, "form": "Schulman", "upos": "PROPN", "head": 1, "deprel": "flat", "dep": "flat"},
            {"id": 3, "form": "wrote", "upos": "VERB", "head": 0, "deprel": "root", "dep": "root"},
            {"id": 4, "form": "Obama", "upos": "PROPN", "head": 3, "deprel": "obj", "dep": "obj"}]
    toks = [t["form"] for t in sent]
    ck("a second token of the gold NAME RUN is right-entity-wrong-token",
       E.split_pick_error(sent, toks, 1, "Schulman")[0] == "right_entity_name_token")
    ck("a token of a DIFFERENT entity is wrong-entity",
       E.split_pick_error(sent, toks, 1, "Obama")[0] == "wrong_entity")
    sent2 = [{"id": 1, "form": "the", "upos": "DET", "head": 3, "deprel": "det", "dep": "det"},
             {"id": 2, "form": "Korean", "upos": "ADJ", "head": 3, "deprel": "amod", "dep": "amod"},
             {"id": 3, "form": "company", "upos": "NOUN", "head": 4, "deprel": "nsubj", "dep": "nsubj"},
             {"id": 4, "form": "said", "upos": "VERB", "head": 0, "deprel": "root", "dep": "root"}]
    ck("an NP-internal MODIFIER is NOT credited as the same entity (the convention fix cannot launder a "
       "real misread)",
       E.split_pick_error(sent2, [t["form"] for t in sent2], 3, "Korean")[0] == "right_np_modifier")


def test_validities_are_counts_with_an_observe_path():
    mod = GRA if landed() else E
    c = mod.empty_agent_counts()
    for _ in range(200):
        mod.accrue_agent(c, "act", {"order": "pre"}, True)
    for _ in range(200):
        mod.accrue_agent(c, "act", {"order": "post"}, False)
    mod.accrue_agent(c, "act", {"order": "weird"}, True)
    S = mod.agent_strengths_from_counts(c)["act"]["cue"]["order"]
    ck("a reliable cue value earns a POSITIVE contrast (reliability)", S["pre"] > 0.0, "%+.3f" % S["pre"])
    ck("an anti-reliable cue value earns a NEGATIVE contrast", S["post"] < 0.0, "%+.3f" % S["post"])
    ck("a value observed ONCE is shrunk toward silence (availability)",
       abs(S["weird"]) < abs(S["pre"]), "weird %+.3f vs pre %+.3f" % (S["weird"], S["pre"]))
    ck("the strengths are a PURE FUNCTION of the counts (a round-trip through JSON rebuilds them exactly)",
       mod.agent_strengths_from_counts(json.loads(json.dumps(c))) == mod.agent_strengths_from_counts(c))
    tab = mod.agent_table_from_counts(c)
    before = json.dumps(tab["strengths"], sort_keys=True)
    n_before = sum(g["n"][1] for g in tab["counts"]["config"].values())
    cands = [{"wtok_start": 0, "head": "dog", "cluster": 1, "wtok_end": 0},
             {"wtok_start": 3, "head": "cat", "cluster": 2, "wtok_end": 3}]
    mod.observe_agent_outcome(["dog", "and", "the", "cat", "ran"],
                              ["NOUN", "CCONJ", "DET", "NOUN", "VERB"], 4, cands, "dog", tab)
    ck("ONE comprehended clause updates the counts (the table is plastic, not a frozen fit)",
       sum(g["n"][1] for g in tab["counts"]["config"].values()) > n_before)
    ck("and the strengths move with the counts",
       json.dumps(tab["strengths"], sort_keys=True) != before)


def test_the_defect_is_absent_on_the_landed_tree():
    """BEFORE landing: the organ's only agent cue weights are the HAND-SET `AGENT_VALIDITIES` dict, which no
    count ever touches.  AFTER landing: the organ owns a counts-accrued table and the live agent competition
    consults it.  The same check, read in both directions, so it cannot pass vacuously either way."""
    hand_set = getattr(GRA, "AGENT_VALIDITIES", None)
    ck("the organ still carries the landed hand-set table (nothing was deleted out from under a consumer)",
       isinstance(hand_set, dict) and "preverbal" in hand_set)
    if landed():
        ck("LANDED: the organ exposes the counts-accrued agent validity table", hasattr(GRA, "load_agent_validities"))
        ck("LANDED: the organ exposes the online observe path for it", hasattr(GRA, "observe_agent_outcome"))
        ck("LANDED: the organ exposes the re-weighed competition arm", hasattr(GRA, "agent_competition_reweighed"))
        asset = GRA.load_agent_validities()
        ck("LANDED: the learned asset loads and its strengths rebuild FROM ITS COUNTS",
           asset is not None and asset["strengths"] == GRA.agent_strengths_from_counts(asset["counts"]))
        # THE DEFECT ITSELF, ON THE SHIPPED PATH.  `The company OF FALLUJAH condemned it` is the
        # commonest remaining pattern: the reader picked the postmodifier INSIDE the gold agent's own NP.
        # On the landed tree the shipped entry point must pick the NP HEAD, and the hand-set arm -- still
        # reachable for A/B -- must still pick the postmodifier, so this check can fail in both directions.
        toks = ["The", "company", "of", "Fallujah", "condemned", "it", "."]
        pos = ["DET", "NOUN", "ADP", "PROPN", "VERB", "PRON", "PUNCT"]
        cands = [{"wtok_start": 1, "head": "company", "cluster": 1, "wtok_end": 1},
                 {"wtok_start": 3, "head": "Fallujah", "cluster": 2, "wtok_end": 3}]
        got = GRA.agent_competition_pick_conf(toks, pos, 4, cands)[0]
        old = GRA.agent_competition_pick_conf(toks, pos, 4, cands, weights=GRA.AGENT_VALIDITIES)[0]
        ck("LANDED: the shipped competition picks the NP HEAD (the defect is gone)", got == "company",
           "picked %r" % got)
        ck("LANDED: the hand-set arm still picks the postmodifier, so that check CAN FAIL",
           old == "Fallujah", "picked %r" % old)
        ck("LANDED: the learned table is not the hand-set one (the validities really were re-weighed)",
           asset is not None and bool(asset["counts"]["config"]) and
           set(next(iter(asset["strengths"].values()))["cue"]) != set(hand_set))
    else:
        print("       (NOT YET LANDED -- the arm lives in experiments/exp_agent_pick_reweigh_v1.py; "
              "the checks below are against the proposed implementation)")
        ck("PROPOSED: the counts-accrued table exists in the cell", hasattr(E, "load_agent_validities"))
        ck("PROPOSED: the online observe path exists in the cell", hasattr(E, "observe_agent_outcome"))
        ck("PROPOSED: the re-weighed competition arm exists in the cell",
           hasattr(E, "agent_competition_reweighed"))
        a = E.load_agent_validities()
        ck("PROPOSED: the learned asset is on disk and its strengths rebuild FROM ITS COUNTS",
           a is not None and a["strengths"] == E.agent_strengths_from_counts(a["counts"]))


def test_the_twin_is_a_real_destruction():
    mod = GRA if landed() else E
    c = mod.empty_agent_counts()
    import random
    rng = random.Random(11)
    for _ in range(4000):
        pre = rng.random() < 0.5
        mod.accrue_agent(c, "act", {"order": "pre" if pre else "post",
                                    "anim": rng.choice(["anim", "inanim", "unk"])}, pre)
    tab = mod.agent_table_from_counts(c)
    vals = [{"order": "pre", "anim": "inanim"}, {"order": "post", "anim": "anim"}]
    a0 = mod.agent_activation(tab, "act", vals)
    a1 = mod.agent_activation(tab, "act", vals, permute_seed=5)
    ck("the info-free twin reaches the activation (permuting the learned strengths is not a no-op)",
       not np.allclose(a0, a1))
    ck("the real table separates the two candidates (so a twin CAN lose)", abs(a0[0] - a0[1]) > 1e-6)


def test_the_recorded_result_agrees_with_itself():
    """The cell's own landed record, when present.  Reads the RECORD -- it never re-asserts a constant."""
    d = os.path.join(_REPO, "data", "exp_agent_pick_reweigh_v1")
    f = os.path.join(d, "metrics_measure.json")
    if not os.path.exists(f):
        print("       (no measurement record on disk at %s -- SKIPPED; run the cell with --measure)"
              % os.path.relpath(f, _REPO))
        return
    with open(f, encoding="utf-8") as fh:
        M = json.load(fh)
    m = M.get("measure") or {}
    rows = m.get("rows") or {}
    ck("the record names both arms in ONE process", "landed" in rows and "reweigh" in rows)
    ck("the record carries the word-order floor it is gated against", "floor" in rows)
    ck("the record carries the info-free twin", "twin" in rows)
    for k in ("agent_vs_floor", "agent_reweigh_vs_landed", "wrong_entity_reweigh_vs_landed"):
        if k in (m.get("contrasts") or {}):
            cc = m["contrasts"][k]
            ck("contrast %s carries a CI and a separation verdict" % k,
               "ci95" in cc and "ci_sep" in cc, "%s %s" % (cc.get("delta"), cc.get("ci95")))
    ng = (m.get("no_regress") or {})
    for k in ("patient", "state"):
        if k in ng:
            ck("no-regress row %s is recorded with its own contrast" % k, "ci95" in ng[k],
               "%s %s" % (ng[k].get("delta"), ng[k].get("ci95")))


def main():
    print("WITNESS test_agent_competition_reweigh_landing  (tree state: %s)"
          % ("LANDED" if landed() else "PROPOSED -- arm still in experiments/"))
    test_split_is_a_real_classifier()
    test_validities_are_counts_with_an_observe_path()
    test_the_defect_is_absent_on_the_landed_tree()
    test_the_twin_is_a_real_destruction()
    test_the_recorded_result_agrees_with_itself()
    print("WITNESS " + ("PASS" if _OK[0] else "FAIL"))
    return 0 if _OK[0] else 1


if __name__ == "__main__":
    raise SystemExit(main())
