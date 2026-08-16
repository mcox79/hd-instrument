"""Tripwire: the verdict-bar checker must keep catching the two verdicts that lied.

WHY THIS EXISTS (2026-08-16). A cell's VERDICT STRING can say PASS while its claim does not
survive the standing bar, and every triage tool we own keys on the string. It fired twice in one
night:

  * `exp_reasoning_storage_4way_cleanup_v3_hadamard_hopid_v1_n16384` reads `4WC_HARD_PASS`
    BEFORE and AFTER a re-run -- byte-identical -- while its banked ratios were a saturated
    1.000/1.000/1.000/1.000 from ONE seed at N=512 in 0.09 s and the real 5-seed N=16384 run
    gives 0.951/0.966/0.942/0.980.
  * `exp_meaning_asset_calibrated_floor_verdict_v1` landed announcing
    `ASSET_CLEARS_THE_CALIBRATED_FLOOR_ON_THE_INSTRUMENT_POPULATION` while 2 of its 3 "clearing"
    arms are not CI-separated from the hardened frequency channel.

WHAT THIS ENFORCES, and what it does NOT. It does not demote anything, does not read the audit
report, and does not assert any count about the population -- those move for legitimate reasons
and a certification that fails on them would be noise. It asserts that the CHECKER STILL WORKS:
both offenders are still flagged, a genuine pass is still not flagged, and the guard is still
load-bearing. Precedent: verification/test_brain_canonical_defaults.py (0495d5fa8).

SPEED. Every test here reads at most three metrics.json plus temp fixtures. The FULL audit walks
7,768 metrics.json and takes minutes; it is NOT run here and NOT run in the session-start hook.
It is a deliberate act (`--scan`) whose staleness the hook reports.

Scope note: the two offender tests SKIP if the cell is absent from disk rather than fail, so a
fresh clone without the data tree still certifies. `test_offender_files_are_present` records
whether that skip is in play, so an all-skipped run cannot read as a green guard.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys

import pytest

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from tools import verdict_bar_check as vbc          # noqa: E402
from tools.c3_gate import BAR_FAILS, BAR_MEETS      # noqa: E402

OFFENDER_SATURATED = os.path.join(
    _REPO, "data", "exp_reasoning_storage_4way_cleanup_v3_hadamard_hopid_v1_n16384",
    "metrics.json")
OFFENDER_SATURATED_RERUN = os.path.join(
    _REPO, "data", "exp_reasoning_storage_4way_cleanup_v3_hadamard_hopid_v1_n16384_ckfix",
    "metrics.json")
OFFENDER_FLOOR = os.path.join(
    _REPO, "data", "exp_meaning_asset_calibrated_floor_verdict_v1", "metrics.json")


def _need(path):
    if not os.path.exists(path):
        pytest.skip(f"offender cell not on this disk: {path}")
    return path


def test_offender_files_are_present():
    """Visibility, not a gate: says out loud whether the offender tests are actually running.

    An all-skipped suite reads green, which is how a guard quietly stops guarding.
    """
    present = {p: os.path.exists(p) for p in
               (OFFENDER_SATURATED, OFFENDER_SATURATED_RERUN, OFFENDER_FLOOR)}
    print("verdict-bar offender cells on disk: " + json.dumps(present, indent=1))
    assert isinstance(present, dict)


# ---------------------------------------------------------------- offender 1: saturation
def test_offender_1_saturated_ceiling_is_flagged():
    r = vbc.check_cell(_need(OFFENDER_SATURATED))
    assert r["verdict_reads_as"] == vbc.READS_PASS, (
        "the banked verdict string must still READ as a pass, or this cell is no longer the "
        f"case under test: {r['verdict_string']!r}")
    assert r["disagreement_class"] == vbc.SATURATED_CEILING, (
        "a metric pinned at 1.000 across every arm is a broken measurement, not a pass. "
        f"got {r['disagreement_class']}, evidence={r['saturation_evidence']}")
    assert r["saturation_evidence"], "flagged as saturated with no evidence recorded"


def test_offender_1_real_rerun_is_not_flagged_saturated():
    """The DISCRIMINATOR. Same cell, same verdict string, honest numbers -- must not be flagged.

    This is what proves the check reads the NUMBERS and not the label: if this ever starts
    failing alongside the banked run, the detector has degenerated into flagging the string.
    """
    banked = vbc.check_cell(_need(OFFENDER_SATURATED))
    real = vbc.check_cell(_need(OFFENDER_SATURATED_RERUN))
    assert real["verdict_string"] == banked["verdict_string"], (
        "these two runs are only interesting because their verdict strings are IDENTICAL; "
        f"banked={banked['verdict_string']!r} rerun={real['verdict_string']!r}")
    assert real["saturated"] is False, (
        "the honest 0.951/0.966/0.942/0.980 re-run was flagged as saturated -- the ceiling "
        f"detector is over-firing: {real['saturation_evidence']}")


# ---------------------------------------------------------------- offender 2: unseparated floor
def test_offender_2_string_passes_bar_fails():
    r = vbc.check_cell(_need(OFFENDER_FLOOR))
    assert r["verdict_reads_as"] == vbc.READS_PASS
    assert r["disagreement_class"] == vbc.STRING_PASSES_BAR_FAILS, (
        f"got {r['disagreement_class']}; classes={r['classes']}")
    failing = {d["arm"] for d in r["declared_clearing_arms_that_fail_recompute"]}
    assert failing == {"d512|ASSET_RETRAIN_CTX", "d512|ASSET_V2_CTX"}, (
        "the two arms whose margin does not separate from the frequency channel must be named "
        f"individually; got {sorted(failing)}")
    assert all("FREQ" in d["binding_floor"].upper()
               for d in r["declared_clearing_arms_that_fail_recompute"])
    assert (r["real_floor_exists"], r["ci_exists"]) == (True, True), (
        "this cell HAS floors and HAS CIs -- its defect is separation. Misreporting it as "
        "NO_FLOOR/NO_CI would send the operator to the wrong fix.")


def test_offender_2_is_not_flagged_by_the_cells_own_logic():
    """Non-circularity: the cell's own `clears_floor` still says True for both flagged arms.

    So the flag comes from OUR recompute, not from reading a field the cell already set. If this
    ever fails, the checker has started agreeing with the cell instead of auditing it.
    """
    with open(_need(OFFENDER_FLOOR), encoding="utf-8") as fh:
        m = json.load(fh)
    rows = m["results"]["INSTRUMENT_322_like_for_like"]["rows"]
    for arm in ("d512|ASSET_RETRAIN_CTX", "d512|ASSET_V2_CTX"):
        assert rows[arm]["clears_floor"] is True, (
            f"{arm} no longer self-declares clears_floor=True; the offender case has changed")


# ---------------------------------------------------------------- negative controls
def test_a_genuinely_clearing_cell_is_not_flagged(tmp_path):
    """THE NEGATIVE CONTROL. A guard that flags everything proves nothing."""
    p = vbc._fixture_genuine(str(tmp_path))
    r = vbc.check_cell(p)
    assert r["disagreement_class"] == vbc.AGREES, r["classes"]
    assert r["bar_status"] == BAR_MEETS
    assert r["claim_arm_floor_roles_compared"] == ["frequency", "orthographic", "scramble"]
    assert r["bar_evidence_complete"] is True


def test_one_floor_below_zero_flips_the_same_cell(tmp_path):
    """One-variable control: the ONLY change is the frequency CI, and the class must move."""
    p = vbc._fixture_genuine(str(tmp_path))
    with open(p, encoding="utf-8") as fh:
        cell = json.load(fh)
    (cell["results"]["rows"]["TREATMENT"]["DECOMPOSED_per_floor"]
         ["HARDENED_FREQUENCY_FREQ_MIN"]["margin"]["ci95"]) = [-0.02, 0.31]
    with open(p, "w", encoding="utf-8", newline="") as fh:
        json.dump(cell, fh)
    r = vbc.check_cell(p)
    assert r["disagreement_class"] == vbc.STRING_PASSES_BAR_FAILS
    assert r["binding_floor"] == "HARDENED_FREQUENCY_FREQ_MIN"


def test_an_honest_negative_is_not_flagged(tmp_path):
    """This tool reports OVERSTATEMENT. A cell that claims nothing is not a disagreement."""
    p = tmp_path / "metrics.json"
    p.write_text(json.dumps({"verdict": "XSHARD_HARD_FAIL",
                             "verdict_msg": "mean_AUC=0.497 at chance"}), encoding="utf-8")
    r = vbc.check_cell(str(p))
    assert r["disagreement_class"] == vbc.AGREES
    assert r["bar_status"] == BAR_FAILS      # recorded, but not a DISAGREEMENT


# ---------------------------------------------------------------- the machinery itself
@pytest.mark.parametrize("s,want", [
    ("4WC_HARD_PASS", vbc.READS_PASS),
    ("ASSET_CLEARS_THE_CALIBRATED_FLOOR_ON_THE_INSTRUMENT_POPULATION", vbc.READS_PASS),
    ("KF45_SMOKE_PASS", vbc.READS_PASS),
    ("CLEANUP_HARD_PASS", vbc.READS_PASS),
    ("KF45_JOINT_MIDDLE_BAND", vbc.READS_NOT_PASS),
    ("XSHARD_HARD_FAIL", vbc.READS_NOT_PASS),
    ("NOT_SEPARATED", vbc.READS_NOT_PASS),
    ("KF4_V4_SMOKE_FAIL", vbc.READS_NOT_PASS),
    ("RULER_CAN_DETECT_MEANING_AT_THIS_N", vbc.READS_AMBIGUOUS),
    (None, vbc.READS_NONE),
])
def test_verdict_lexicon(s, want):
    """Underscore-joined verdicts are the norm; `\\bPASS\\b` misses `KF45_SMOKE_PASS`.

    That miss was real until the token normalisation landed, so these stay pinned.
    """
    assert vbc.verdict_reads_as(s) == want


def test_chance_baseline_is_not_a_floor():
    """PINNED by the standing rule: the bar is max(orthographic, frequency, scramble).

    3 of the 30 audited cells have a random-chance floor. Counting it would silently convert
    3 bare-threshold cells into floor-bearing ones.
    """
    from tools.c3_gate import REQUIRED_FLOOR_ROLES, classify_arm_role
    assert classify_arm_role("random_chance") == "random_chance"
    assert "random_chance" not in REQUIRED_FLOOR_ROLES


def test_the_checker_self_test_passes():
    """Run the tool's own --self-test as a subprocess: proves the CLI entry point works too."""
    r = subprocess.run([sys.executable, os.path.join(_REPO, "tools", "verdict_bar_check.py"),
                        "--self-test"], cwd=_REPO, capture_output=True, text=True, timeout=600)
    assert r.returncode == 0, f"stdout:\n{r.stdout}\nstderr:\n{r.stderr}"
    assert "RESULT: PASS" in r.stdout


def test_the_c3_gate_self_test_still_passes():
    """The bar predicate lives in c3_gate.py and was EXTENDED, not forked. Its own guard must
    still hold, or this checker is standing on a broken gate."""
    r = subprocess.run([sys.executable, os.path.join(_REPO, "tools", "c3_gate.py"),
                        "--self-test"], cwd=_REPO, capture_output=True, text=True, timeout=600)
    assert r.returncode == 0, f"stdout:\n{r.stdout}\nstderr:\n{r.stderr}"


def test_the_saturation_guard_is_load_bearing(monkeypatch):
    """Negative control for the guard: disabled, offender 1 must stop being caught by it."""
    _need(OFFENDER_SATURATED)
    monkeypatch.setattr(vbc, "GUARD_ENABLED", False)
    r = vbc.check_cell(OFFENDER_SATURATED)
    assert r["disagreement_class"] != vbc.SATURATED_CEILING, (
        "with the guard disabled the cell is STILL flagged saturated, so the guard is not what "
        "catches it and this whole detector is decorative")


def test_the_hook_path_is_fast_and_never_raises():
    """The hook must stay under the 10 s budget and must never block a session start."""
    import time
    t0 = time.time()
    line, rc = vbc.hook_line()
    dt = time.time() - t0
    assert dt < 5.0, f"hook_line took {dt:.1f}s; it must never rescan"
    assert isinstance(line, str) and line.startswith("[verdict-bar]")
    assert rc in (0, 1)


def test_scan_never_mutates_anything(tmp_path):
    """CLASSIFY, DO NOT DEMOTE: a scan over a fixture tree leaves every input byte-identical."""
    cell_dir = tmp_path / "exp_fixture_v1"
    cell_dir.mkdir()
    p = cell_dir / "metrics.json"
    payload = {"verdict": "FIXTURE_HARD_PASS", "verdict_msg": "acc=0.62 threshold=0.50"}
    p.write_text(json.dumps(payload), encoding="utf-8")
    before = p.read_bytes()
    rep = vbc.scan(data_dir=str(tmp_path))
    assert p.read_bytes() == before, "the checker modified a metrics.json"
    assert rep["class_counts"][vbc.NO_FLOOR] == 1
    assert list(tmp_path.iterdir()) == [cell_dir], "the checker created a file in the data tree"
