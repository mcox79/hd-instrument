"""Scaffold-free witness for the_gate_cannot_measure_its_own_floor.

A calibration of per_row_gain_c3_vet_v1's orthographic floor is only trustworthy if the machinery
around it is sound. These tests each CAN FAIL and each carries a positive control, so a broken guard
or a degenerate metric cannot pass silently. They witness the load-bearing mechanisms of the fix:

  1. THE GUARD FIRES. void_plumbing_check refuses (void=True) when the constant disagrees with the
     measured floor, when the bar is None (the current live state), when A1_BASE does not reproduce
     the stripped headline, or when self-retrieval is below floor -- and it PASSES (void=False) only
     when all four agree. A guard nobody has seen fire is untested; this makes it fire.
  2. THE NUMBER DID NOT CROSS HARNESSES. tools/per_row_gain_c3_vet_v1.py still carries ORTHO_BAR is
     None -- nobody pasted the sibling's 0.019500 across -- and the calibration measures its own
     floor rather than hard-coding any sibling constant.
  3. THE FORM-ROUTE METRIC FAILS SAFE. The trigram floor responds to the QUERY's own spelling (real
     signal in the orthographic route), and its info-free twin -- the same machinery with a
     DIFFERENT word's spelling as query -- picks by the donor's form, not the target's. "No
     target information" and "target information" do not score alike.
  4. STRIPPING THE GOLD REMOVES THE FORM-ROUTE WIN. The morphology strip that both the arm and the
     floor now use catches nation/national and NOT car/automobile, and it removes exactly the
     form-sharing gold member a spelling control would have won -- which is why the floor collapses.

Run: .venv/Scripts/python.exe verification/test_the_gate_can_measure_its_own_floor.py
"""
import os
import re
import sys

import numpy as np

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
for _p in (_REPO, os.path.join(_REPO, "experiments"), os.path.join(_REPO, "tools")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import experiments.exp_per_row_gain_trigram_floor_calibration_v1 as CAL
import experiments.exp_meaning_supply_separation_v1 as MS
from hdlab.morphology_leakage import shares_stem, strip_gold

_OK_A1 = CAL.A1_BASE_EXPECTED_STRIPPED     # 0.04575
_SR = 0.75                                  # a passing self-retrieval


def _cos(a, b):
    na, nb = float(np.linalg.norm(a)), float(np.linalg.norm(b))
    return 0.0 if na < 1e-12 or nb < 1e-12 else float(np.dot(a, b) / (na * nb))


def test_guard_fires_on_a_wrong_constant_and_passes_on_the_right_one() -> dict:
    """The positive control on the guard (brief item 3): make it fire, then restore."""
    measured = 0.019500                     # stand-in for whatever this harness measures
    # PASS only when the constant equals the measured floor and the other preconditions hold.
    ok = CAL.void_plumbing_check(measured, measured, _OK_A1, _SR)
    assert ok["void"] is False, "guard refused a correctly-calibrated bar: %r" % ok

    # FIRE on the legacy leaky constant (the exact accident the brief exists to prevent).
    leaky = CAL.void_plumbing_check(measured, 0.0870, _OK_A1, _SR)
    assert leaky["void"] is True, "guard did NOT fire on the leaky 0.0870 constant: %r" % leaky

    # FIRE when the bar was never calibrated -- the current live state of the tool.
    none_bar = CAL.void_plumbing_check(measured, None, _OK_A1, _SR)
    assert none_bar["void"] is True, "guard did NOT fire on an uncalibrated (None) bar: %r" % none_bar

    # FIRE when the arm scores no longer reproduce the stripped-gold headline (gold drifted).
    drifted = CAL.void_plumbing_check(measured, measured, 0.048, _SR)
    assert drifted["void"] is True, "guard did NOT fire on a drifted A1_BASE headline: %r" % drifted

    # FIRE when the known-answer control has collapsed (harness broken).
    sr_bad = CAL.void_plumbing_check(measured, measured, _OK_A1, 0.50)
    assert sr_bad["void"] is True, "guard did NOT fire on a failed self-retrieval control: %r" % sr_bad
    return {"pass_on_correct": True, "fires_on_leaky": True, "fires_on_none": True,
            "fires_on_drift": True, "fires_on_sr": True}


def test_the_sibling_number_did_not_cross_harnesses() -> dict:
    """No number crosses scorers or populations.

    UPDATED 2026-08-24 WHEN THE FIX LANDED, AND THE REASON MATTERS. This asserted
    `ORTHO_BAR is None` -- i.e. *the tool still refuses to grade*. That was a PROXY for the real
    property, correct only while the fix was unlanded, and it FAILED the moment the tool was
    calibrated -- which is the fix WORKING. A guard that fires when the thing it guards is repaired
    teaches the next reader to delete it.

    The real property is not "the tool refuses". It is: **the constant the tool gates on must equal
    what the calibration MEASURED IN THIS HARNESS** -- so it is checked against the landed
    metrics.json rather than against a hard-coded literal. If someone hand-edits ORTHO_BAR, this
    fails; if the calibration is re-run and legitimately moves, this still passes.
    """
    tool = os.path.join(_REPO, "tools", "per_row_gain_c3_vet_v1.py")
    with open(tool, encoding="utf-8") as fh:
        src = fh.read()
    m = re.search(r"^ORTHO_BAR\s*=\s*([0-9.]+|None)", src, re.M)
    assert m, "ORTHO_BAR not found in per_row_gain_c3_vet_v1.py"
    declared = m.group(1)
    if declared == "None":
        # Still-unlanded state is legitimate: an uncalibrated gate must refuse.
        return {"tool_refuses_uncalibrated": True, "calibration_measures_its_own": True}

    import json
    m_path = os.path.join(_REPO, "data", "exp_per_row_gain_trigram_floor_calibration_v1",
                          "metrics.json")
    if os.path.exists(m_path):
        with open(m_path, encoding="utf-8") as fh:
            measured = json.load(fh)["THE_CALIBRATED_FLOOR"]["acc"]
        assert abs(float(declared) - float(measured)) < 1e-9, (
            "ORTHO_BAR (%s) does not equal what the calibration measured in this harness (%s) -- "
            "the constant was set by hand, not by measurement" % (declared, measured))
    else:
        # Same SKIP convention as the landed-headline check below: the certification gate must not
        # depend on a persisted artifact, but the standalone reverify has it present.
        measured = "landed metrics absent (data dir pruned)"

    with open(CAL.__file__, encoding="utf-8") as fh:
        cal_src = fh.read()
    # An ASSIGNMENT of the sibling literal is a leak; a prose mention of it (the docstring explaining
    # WHY not to paste it) is not. Distinguish them, or the witness flags the warning as the crime.
    assert not re.search(r"=\s*0\.0195", cal_src), \
        "the calibration ASSIGNS a sibling constant instead of measuring its own floor"
    # positive control: the pattern we are asserting-absent is exactly the one that WOULD be a leak.
    assert re.search(r"=\s*0\.0195", "ORTHO_BAR = 0.019500"), "the leak-detector pattern is broken"
    return {"tool_gates_on_measured_value": float(declared),
            "equals_calibration": True, "calibration_measures_its_own": True}


def test_the_form_route_metric_fails_safe() -> dict:
    """A6_TRIGRAM_ONLY responds to the TARGET word's own spelling; its info-free twin (a different
    word's spelling as query) does not. If both scored alike, the floor would be uninterpretable."""
    anchors = ["cat", "cats", "kitten", "dog", "dogs", "puppy", "car", "cars", "truck",
               "run", "running", "walk"]
    t_mat, t_cov = MS.trigram_matrix(anchors)
    assert t_cov.all(), "trigram coverage gap in the fixture -- test would be vacuous"
    pos = {a: i for i, a in enumerate(anchors)}

    # POSITIVE CONTROL: a form-sharing pair is closer than a form-unrelated pair.
    assert _cos(t_mat[pos["cat"]], t_mat[pos["cats"]]) > _cos(t_mat[pos["cat"]], t_mat[pos["car"]]), \
        "trigram geometry is not form-based -- the fixture proves nothing"

    # exclude BOTH the target and the donor from the pool, or each query would trivially pick itself
    exclude = {"cat", "car"}
    sel = np.array([i for a, i in pos.items() if a not in exclude])
    real = t_mat[sel] @ t_mat[pos["cat"]]                        # query = 'cat' (the target's form)
    twin = t_mat[sel] @ t_mat[pos["car"]]                        # info-free twin: a DIFFERENT word
    real_pick = anchors[sel[int(np.argmax(real))]]
    twin_pick = anchors[sel[int(np.argmax(twin))]]
    assert real_pick == "cats", "real-query floor did not pick the target's form neighbour: %r" % real_pick
    assert twin_pick == "cars", "info-free twin did not pick by the DONOR's form: %r" % twin_pick
    assert real_pick != twin_pick, "the twin reproduced the real pick -- it is not information-free"
    return {"real_query_pick": real_pick, "twin_pick": twin_pick}


def test_stripping_the_gold_removes_the_form_route_win() -> dict:
    """Why the floor collapses: the strip catches morphological relatives (the 78%) and not genuine
    synonyms, and it removes exactly the gold member a spelling control would win."""
    # the strip catches form relatives, not meaning relatives
    assert shares_stem("nation", "national") and not shares_stem("car", "automobile"), \
        "morphology strip does not separate form from meaning"

    # a form-route (trigram) winner on leaky gold is a morphological relative...
    anchors = ["national", "country", "state", "citizen", "border"]
    t_mat, _ = MS.trigram_matrix(anchors + ["nation"])
    pos = {a: i for i, a in enumerate(anchors + ["nation"])}
    sel = np.array([pos[a] for a in anchors])
    trig = t_mat[sel] @ t_mat[pos["nation"]]
    form_pick = anchors[int(np.argmax(trig))]
    assert form_pick == "national", "fixture: the form route did not pick the morphological relative"

    leaky_gold = frozenset({"national", "country", "state"})
    stripped_gold = strip_gold("nation", leaky_gold)
    assert form_pick in leaky_gold, "control: the form win should score on LEAKY gold"
    assert form_pick not in stripped_gold, "the strip failed to remove the form-route win"
    assert "country" in stripped_gold and "state" in stripped_gold, \
        "the strip over-removed genuine meaning members"
    return {"form_pick": form_pick, "in_leaky": True, "in_stripped": False,
            "stripped_gold": sorted(stripped_gold)}


def test_landed_calibration_reproduces_the_headline() -> dict:
    """Reproduce the landed headline FROM DISK (no re-run): the floor was measured in per_row_gain's
    own population, it separates from both info-free twins, the read-out clears it while it would NOT
    clear the leaky floor, and the guard fires. SKIPS (does not fail) if the data dir was pruned, so
    the certification gate does not depend on a persisted artifact -- but the standalone reverify
    run has it present."""
    import json
    m_path = os.path.join(_REPO, "data", "exp_per_row_gain_trigram_floor_calibration_v1", "metrics.json")
    if not os.path.exists(m_path):
        return {"skipped": "landed metrics absent (data dir pruned); run the calibration to populate"}
    with open(m_path, encoding="utf-8") as fh:
        m = json.load(fh)

    assert m["harness_identity_check"]["matches_sibling_harness_to_1e-9"] is True, \
        "A1_BASE did not reproduce the stripped headline -- this is NOT per_row_gain's population"
    assert m["n_items"] == 4000, "not the full run: n_items=%r" % m["n_items"]

    fl = m["THE_CALIBRATED_FLOOR"]
    tw = m["floor_vs_info_free_twins"]
    assert tw["floor_separates_from_donorq_twin"] and tw["floor_separates_from_rowperm_twin"], \
        "the honest floor did NOT separate from its info-free twins"
    assert tw["delta_floor_minus_donorq"]["ci_excludes_zero"] and \
        tw["delta_floor_minus_rowperm"]["ci_excludes_zero"], "twin deltas do not exclude zero"

    a1 = m["RE_GRADE_leaky_vs_honest"]["per_arm"]["A1_BASE"]
    bar_hi = fl["PROPOSED_ORTHO_BAR_CI"][1]
    assert a1["clears_HONEST_floor_%.4f" % bar_hi] is True, "read-out does not clear the honest floor"
    assert a1["would_clear_LEAKY_floor_0.0960"] is False, \
        "control broke: the read-out should NOT clear the leaky floor (that is the whole point)"

    g = m["void_plumbing_guard"]
    assert g["guard_fires_on_wrong_constant"] and g["guard_passes_on_correct_constant"], \
        "the recompute-and-refuse guard did not behave (fire-on-wrong, pass-on-right)"
    return {"floor": fl["acc"], "floor_ci": fl["ci"], "a1_base": a1["acc_stripped_gold"],
            "donorq": tw["A6_TRIGRAM_DONORQ"]["acc"], "rowperm": tw["A6_TRIGRAM_ROWPERM"]["acc"]}


def main() -> int:
    tests = [
        ("guard_fires_on_wrong_constant_and_passes_on_right", test_guard_fires_on_a_wrong_constant_and_passes_on_the_right_one),
        ("sibling_number_did_not_cross_harnesses", test_the_sibling_number_did_not_cross_harnesses),
        ("form_route_metric_fails_safe", test_the_form_route_metric_fails_safe),
        ("stripping_the_gold_removes_the_form_route_win", test_stripping_the_gold_removes_the_form_route_win),
        ("landed_calibration_reproduces_the_headline", test_landed_calibration_reproduces_the_headline),
    ]
    failed = []
    for name, fn in tests:
        try:
            print("PASS  %-52s %s" % (name, fn()))
        except AssertionError as e:
            failed.append(name)
            print("FAIL  %-52s %s" % (name, e))
    print("ALL WITNESSES PASSED" if not failed else "WITNESSES FAILED: %s" % failed)
    return 0 if not failed else 1


# ---- PYTEST ENTRY POINT (WIRED: without a test_ function run_certification.py collects nothing) --
def test_the_gate_can_measure_its_own_floor():
    assert main() == 0, "witness FAILED -- run the file directly for the detail"


if __name__ == "__main__":
    raise SystemExit(main())
