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
from tools.c3_gate import (                         # noqa: E402
    BAR_FAILS, BAR_MEETS, BAR_NO_EVIDENCE, arm_ceiling_shape, claim_arm_eligibility,
    classify_arm_role,
)

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


# ---------------------------------------------------------------- offender 3: THE FALSE PASS
# 2026-08-16. `tools/verdict_bar_check.py` at commit c0802fc36 returned MEETS_BAR on a cell whose
# every genuine arm is NEGATIVE. It selected `S_INPLACE_d256_f0.020__KA` -- a PLANTED-ANSWER
# validity arm scoring hit@1 1.0000 by construction -- as the claim-carrying arm, at min ci_lo
# +0.9044 binding on the spelling floor.
#
# This is the failure class the tool exists to catch, occurring INSIDE the tool, and it is
# ANTI-CORRELATED WITH RIGOUR: a cell that ships a known-answer and a null for EVERY pipeline
# publishes more planted-answer arms for the selector to find, so the more careful design was the
# more likely to be falsely passed. That inversion is what these tests pin.
#
# Three independent defects produced it, and each is covered below:
#   D1 the walker built DOTTED path strings, so the literal dot in `f0.020__KA` split the arm's
#      own name in half;
#   D2 `_best_treatment_arm` classified only the LAST `::` segment, which was the CONTAINER
#      `MARGIN_per_floor` -- so even the nine `__NULL` arms the classifier ALREADY recognised
#      correctly were scored as treatment arms;
#   D3 `classify_arm_role` did not recognise `__KA`, `KA_QUERY_IS_GOLD_VECTOR` or `PLANTED`.
#
# The cell itself is in `scratch/` (gitignored, periodically cleared), so these tests run against
# a fixture carrying its shape and its real numbers. `test_false_pass_cell_on_disk_if_present`
# pins the real artifact opportunistically for as long as it exists.
@pytest.mark.parametrize("scaffold_name,degenerate,want,why", [
    ("S_INPLACE_d256_f0.020__KA", True, BAR_FAILS, "name AND shape both mark it"),
    ("S_INPLACE_d256_f0.020__KA", False, BAR_FAILS, "NAME alone: planted arm not at ceiling"),
    ("S_INPLACE_d256_f0.020_TREATMENT", True, BAR_FAILS, "SHAPE alone: name is clean"),
    ("S_INPLACE_d256_f0.020_TREATMENT", False, BAR_MEETS, "NEITHER fires -> the margins pass"),
])
def test_false_pass_2x2(tmp_path, scaffold_name, degenerate, want, why):
    """The false pass, as a 2x2 in which the FLOOR MARGINS ARE HELD CONSTANT.

    One variable at a time. Every cell carries the identical +0.9044 / +0.9772 / +0.9855 margins;
    the only thing that changes is whether the arm holding them is ALLOWED to carry a claim.

    The last row is the NEGATIVE CONTROL and it is the reason the other three mean anything: a
    rule that rejected every arm would satisfy rows 1-3 and be worthless. Row 4 proves the new
    rules can be SATISFIED, so rows 1-3 measure the rules rather than a blanket refusal.
    """
    p = vbc._fixture_false_pass(str(tmp_path), scaffold_name=scaffold_name,
                                degenerate_ci=degenerate)
    r = vbc.check_cell(p)
    assert r["bar_status"] == want, (
        f"{why}: expected {want}, got {r['bar_status']} on claim arm "
        f"{r['claim_carrying_arm']!r} at min_ci_lo={r['min_ci_lo']}")
    if want is BAR_FAILS:
        assert str(r["claim_carrying_arm"]).endswith("R0_BASE_DENSE"), (
            "with the scaffold arm excluded the claim must fall back to the HONEST arm, whose "
            f"every floor margin is negative; got {r['claim_carrying_arm']!r}")
        assert r["min_ci_lo"] < 0
        assert any(scaffold_name in k for k in r["claim_arm_rejected"]), (
            "the exclusion must be REPORTED, not silent -- an invisible filter is "
            "indistinguishable from one that matched nothing")
    else:
        assert str(r["claim_carrying_arm"]).endswith(scaffold_name)


def test_planted_answer_arm_can_never_be_the_claim_arm(tmp_path):
    """THE RULE, stated directly: no `__KA` arm may be selected, whatever its margin.

    Also pins D2 -- the nine per-pipeline `__NULL` arms must be excluded too. They were NOT,
    before this fix, despite `classify_arm_role` classifying them correctly all along, because
    only the container segment was ever handed to the classifier.
    """
    r = vbc.check_cell(vbc._fixture_false_pass(str(tmp_path)))
    for k in r["per_treatment_arm_min_ci_lo"]:
        assert "__KA" not in k.upper(), f"a planted-answer arm was scored as a treatment arm: {k}"
        assert "__NULL" not in k.upper(), f"a null arm was scored as a treatment arm: {k}"
        assert "KA_QUERY_IS_GOLD_VECTOR" not in k
    rejected = r["claim_arm_rejected"]
    assert any("__KA" in k for k in rejected) and any("__NULL" in k for k in rejected)
    assert all(v["reason"] in ("CONTROL_ARM", "VALIDITY_SCAFFOLD", "CEILING_BY_CONSTRUCTION",
                              "NON_FINITE_CI") for v in rejected.values())


def test_fail_closed_never_reports_meets_bar(tmp_path):
    """FAIL CLOSED. Every arm is scaffolding -> NO_EVIDENCE. Never MEETS_BAR, and never FAILS_BAR.

    FAILS_BAR would be wrong in the direction this project has paid for: it asserts a MEASURED
    refutation of a claim arm that does not exist. Before the fix the fallback pooled every
    comparison in the cell -- including the deliberately-losing null arms -- and reported their
    negative bound as the cell's verdict.
    """
    p = vbc._fixture_false_pass(str(tmp_path))
    with open(p, encoding="utf-8") as fh:
        cell = json.load(fh)
    arms = cell["REAL_TASK"]["regimes"]["EXACT_KEY_profile_bundle"]["per_arm"]
    arms["R0_BASE_DENSE__KA"] = arms.pop("R0_BASE_DENSE")     # remove the last honest arm
    with open(p, "w", encoding="utf-8", newline="") as fh:
        json.dump(cell, fh)
    r = vbc.check_cell(p)
    assert r["claim_carrying_arm"] is None
    assert r["claim_arm_status"] == "NO_ELIGIBLE_CLAIM_ARM"
    assert r["bar_status"] == BAR_NO_EVIDENCE, (
        f"a cell with no eligible claim arm must be NO_EVIDENCE; got {r['bar_status']}")
    assert r["bar_evidence_complete"] is False
    assert r["fail_closed_override"]


def test_non_finite_ci_is_not_evidence(tmp_path):
    """NaN is UNCLASSIFIABLE, and unclassifiable is not a pass.

    Measured need: the d=256 f=0.002/0.005 arms of the real cell round to k=1 active unit, their
    permutation null has zero variance and their margin CIs come back NaN. NaN comparisons are
    all False, so a NaN would have slipped through `ci_lo > 0` as a FAILS_BAR by accident rather
    than by rule -- and `max()` over a set containing NaN is order-dependent, so it could equally
    have been chosen as the BEST arm.
    """
    p = vbc._fixture_false_pass(str(tmp_path), scaffold_name="S_ARM_f0.002_TREATMENT",
                                degenerate_ci=False)
    with open(p, encoding="utf-8") as fh:
        cell = json.load(fh)
    arms = cell["REAL_TASK"]["regimes"]["EXACT_KEY_profile_bundle"]["per_arm"]
    for floor in arms["S_ARM_f0.002_TREATMENT"]["MARGIN_per_floor"].values():
        floor["margin"]["ci95"] = [float("nan"), float("nan")]
    with open(p, "w", encoding="utf-8", newline="") as fh:
        json.dump(cell, fh)
    r = vbc.check_cell(p)
    assert not any("S_ARM_f0.002_TREATMENT" in k for k in r["per_treatment_arm_min_ci_lo"]), (
        "an arm whose every margin bound is NaN was scored as if it were measured")
    assert r["claim_arm_rejected"]["EXACT_KEY_profile_bundle::S_ARM_f0.002_TREATMENT"]["reason"] \
        == "NON_FINITE_CI"
    assert r["bar_status"] != BAR_MEETS


def test_false_pass_cell_on_disk_if_present():
    """Pin the REAL artifact for as long as it exists. `scratch/` is cleared, so this may skip.

    Skipping is honest here: the durable coverage is the fixture above. This exists so that the
    ACTUAL cell that produced the false pass cannot silently start passing again while it is
    still on disk.
    """
    real = os.path.join(_REPO, "scratch", "sparse_code_real_task", "verdict_metrics.json")
    if not os.path.exists(real):
        pytest.skip(f"the false-pass artifact is not on this disk (scratch is cleared): {real}")
    r = vbc.check_cell(real)
    scored = r["per_treatment_arm_min_ci_lo"]
    assert not any("__KA" in k.upper() or "__NULL" in k.upper() or "KA_QUERY" in k.upper()
                   for k in scored), (
        "a planted-answer or null arm is again being scored as a treatment arm: "
        f"{[k for k in scored if 'KA' in k.upper() or 'NULL' in k.upper()]}")
    assert r["claim_carrying_arm"] is None or "__KA" not in str(r["claim_carrying_arm"])
    assert (r["min_ci_lo"] is None or r["min_ci_lo"] < 0.5), (
        "the claim arm's margin is back in planted-answer territory (+0.9044 was the false "
        f"pass); got {r['min_ci_lo']} on {r['claim_carrying_arm']!r}")


# ---------------------------------------------------------------- the arm classifier itself
@pytest.mark.parametrize("name,want", [
    # the per-pipeline suffix that produced the false pass, including the literal dot
    ("S_INPLACE_d256_f0.020__KA", "known_answer"),
    ("S_EXPAND_d1024_f0.500__KA", "known_answer"),
    ("KA_QUERY_IS_GOLD_VECTOR", "known_answer"),
    ("KA_PLANTED_SEMANTIC", "known_answer"),
    ("GOLD_PLANTED", "known_answer"),
    ("A_PLANTED_SEMANTIC", "known_answer"),
    ("SUBSTRATE_GT", "known_answer"),
    ("ORACLE_ADDITIVE", "known_answer"),
    ("GLOVE_POSITIVE_CONTROL", "known_answer"),
    ("S_INPLACE_d256_f0.020__NULL", "null_control"),
    # MUST NOT over-fire: `ka` is bounded on both sides, so these stay treatment arms
    ("KAPPA_WEIGHTED", None),
    ("KALMAN_SMOOTHED", None),
    ("A4_BOTH", None),
    ("R0_BASE_DENSE", None),
    ("KCAP_GRD_BOOST_f0.100", None),
    ("INC_SIMHASH", None),
    # precedence is unchanged: a scrambled planted arm is still a SCRAMBLE floor
    ("A_SHUFFLED_PLANTED", "scramble"),
    ("IDENTITY_SHUFFLE", "scramble"),
    ("F1_TRIGRAM_ONLY", "orthographic"),
    ("F3_FREQUENCY_ONLY", "frequency"),
])
def test_arm_role_lexicon(name, want):
    """Enumerated from disk, not guessed.

    Every arm-position dict key across all 7,772 banked metrics.json was collected and bucketed
    before this lexicon was written, because the verdict vocabulary went from 13 strings in June
    to 444 in July and a guessed suffix list would have been wrong in both directions. The
    `KAPPA` / `KALMAN` rows are the over-fire guard: `(^|_)ka(_|$)` must be bounded.
    """
    assert classify_arm_role(name) == want


def test_ceiling_shape_is_structural_not_name_based():
    """SHAPE, with its LIMIT stated. What it catches, and what it provably cannot."""
    # CAN: a planted arm at ceiling with a zero-width CI -- no name needed.
    assert (arm_ceiling_shape({"hit_at_1": 1.0, "hit_at_1_ci95": [1.0, 1.0]})["tell"]
            == "DEGENERATE_CI_AT_CEILING")
    assert arm_ceiling_shape({"hit_at_1": 1.0, "recall": 1.0})["tell"] == "ALL_SCORES_AT_CEILING"
    # CANNOT: the two REAL known-answer arms that FAILED. At d=256 with f=0.002 the code is one
    # active unit for 5,491 anchors, so collisions are guaranteed and the planted answer reads
    # 0.4056. Structurally that is indistinguishable from a mediocre treatment arm, and only the
    # NAME says otherwise. This assertion exists so nobody mistakes the shape rule for
    # sufficient.
    assert arm_ceiling_shape({"hit_at_1": 0.4056, "hit_at_1_ci95": [0.39, 0.42]}) is None
    assert claim_arm_eligibility(["S_INPLACE_d256_f0.002__KA"],
                                 {"hit_at_1": 0.4056})["reason"] == "CONTROL_ARM"
    # MUST NOT over-fire: a realised CONFIGURATION fraction at 1.0 is not an instrument ceiling.
    # The first cut of this rule excluded INC_SIMHASH, a legitimate incumbent arm, because a
    # SimHash is a sign function so its active fraction is 1.0 by construction.
    assert arm_ceiling_shape({"simlex_rho": 0.268, "active_frac_realised": 1.0}) is None
    assert arm_ceiling_shape({"hit_at_1": 0.0481, "hit_at_1_ci95": [0.0418, 0.0548]}) is None


def test_claim_arm_eligibility_checks_every_segment_not_just_the_tail():
    """D2, directly. The tail of the real scoped key was the CONTAINER `MARGIN_per_floor`."""
    bad = claim_arm_eligibility(["EXACT_KEY_profile_bundle", "S_INPLACE_d256_f0.020__KA",
                                 "MARGIN_per_floor"], None)
    assert bad["eligible"] is False and bad["reason"] == "CONTROL_ARM"
    assert "020__KA" in bad["detail"]
    ok = claim_arm_eligibility(["EXACT_KEY_profile_bundle", "R0_BASE_DENSE",
                                "MARGIN_per_floor"], {"hit_at_1": 0.0481})
    assert ok["eligible"] is True


def test_path_walk_does_not_split_arm_names_on_dots():
    """D1. `f0.020__KA` contains a literal dot; a dotted path string loses the segment boundary."""
    paths = [p for p, _ in vbc._iter_dicts({"per_arm": {"S_INPLACE_d256_f0.020__KA": {"x": 1}}})]
    assert all(isinstance(p, tuple) for p in paths)
    assert ("per_arm", "S_INPLACE_d256_f0.020__KA") in paths, (
        f"the arm name was split by the walker: {paths}")


def test_two_dimensionalities_are_not_pooled_into_one_arm(tmp_path):
    """SCOPE. The bar requires the IDENTICAL scorer / n / pool / gold, so two runs at different
    dimensionality must be judged apart -- merging them is the comparison the bar forbids.

    Real shape, from data/exp_meaning_lift_population_code_v1: margins live at
    `by_d.<D>.per_arm.<ARM>.THE_BAR.MARGIN_per_floor.<FLOOR>`. `THE_BAR` is the cell's own name
    for its bar block, not an arm; until it was treated as a container the walker named the arm
    `THE_BAR` and BOTH dimensionalities collapsed into one bucket called `C4_PHASOR::THE_BAR`.
    """
    p = tmp_path / "metrics.json"
    def block(lo):
        return {"THE_BAR": {"MARGIN_per_floor": {
            "A_ORTHOGRAPHIC": {"margin": {"point": lo + 0.2, "ci95": [lo + 0.1, lo + 0.3]}},
            "HARDENED_FREQUENCY_FREQ_MIN": {"margin": {"point": lo + 0.1, "ci95": [lo, lo + 0.2]}},
            "OWN_SCRAMBLE_PERM_P95": {"margin": {"point": lo + 0.15, "ci95": [lo + 0.05, lo + 0.25]}}}}}
    p.write_text(json.dumps({
        "verdict": "SCOPE_FIXTURE",
        "by_d": {"1024": {"per_arm": {"C4_PHASOR": block(0.11)}},
                 "256": {"per_arm": {"C4_PHASOR": block(0.09)}}},
    }), encoding="utf-8")
    r = vbc.check_cell(str(p))
    scored = r["per_treatment_arm_min_ci_lo"]
    assert set(scored) == {"1024::C4_PHASOR", "256::C4_PHASOR"}, (
        f"the two dimensionalities were pooled into one arm bucket: {sorted(scored)}")
    assert abs(scored["1024::C4_PHASOR"]["min_ci_lo"] - 0.11) < 1e-9
    assert abs(scored["256::C4_PHASOR"]["min_ci_lo"] - 0.09) < 1e-9
    assert r["claim_carrying_arm"] == "1024::C4_PHASOR"


def test_classifier_agrees_with_a_cell_that_declares_its_own_arm_roles():
    """INDEPENDENT CROSS-CHECK, and the strongest evidence the lexicon is calibrated.

    `exp_thematic_relation_supply_bridged_grounding_v2_smoke` publishes its OWN
    `selftest_evidence.standing_bar_arm_roles` map -- the cell author's declaration of which of
    its arms are floors, known-answer and null. Our classifier is compared against it arm by arm.
    That tests BOTH directions at once: an over-firing lexicon would demote a declared treatment
    arm, an under-firing one would miss a declared control.

    Measured 2026-08-16: 12 of 12 agree. Skips if the cell is not on this disk.
    """
    p = os.path.join(_REPO, "data",
                     "exp_thematic_relation_supply_bridged_grounding_v2_smoke", "metrics.json")
    if not os.path.exists(p):
        pytest.skip(f"cell not on this disk: {p}")
    with open(p, encoding="utf-8") as fh:
        m = json.load(fh)
    declared = m.get("selftest_evidence", {}).get("standing_bar_arm_roles")
    if not isinstance(declared, dict) or not declared:
        pytest.skip("the cell no longer declares standing_bar_arm_roles")
    disagree = {k: (v, classify_arm_role(k)) for k, v in declared.items()
                if classify_arm_role(k) != v}
    assert not disagree, (
        "our arm-role classifier disagrees with the cell's OWN declaration "
        f"(name: (cell_says, we_say)): {disagree}")


def test_tie_convention_is_named_not_silently_chosen(tmp_path):
    """A rank margin computed under a NAMED tie convention must carry that name into the report.

    This is not decorative. Rank-shaped margins really do bind: on the cell audited 2026-08-16,
    30 of 55 eligible arms bind on a TOP-50 margin rather than on hit@1. Top-50 recall and median
    rank are tie-convention dependent -- rank = #(strictly greater) + 1 gives a gold buried in a
    tie of thousands rank 1, #(>=) does not -- and on that cell the trigram/spelling channel
    carries 15.3% of the pool tied with the gold while the dense read-out carries 0.0%, so the
    spelling-vs-substrate top-50 comparison REVERSES between conventions. A cell that publishes
    both must not have the flattering one picked for it silently.

    What is asserted: both conventions are SEEN, the binding floor NAMES the one that bound, and
    the conservative bound is what governs. What is NOT asserted, deliberately: which convention
    is correct. That is the operator's call and this tool does not make it.
    """
    p = tmp_path / "metrics.json"
    p.write_text(json.dumps({
        "verdict": "TIE_FIXTURE",
        "per_arm": {"TREATMENT": {"TOP50_MARGIN_per_floor": {
            "optimistic_ties": {
                "A_ORTHOGRAPHIC": {"margin": {"point": 0.11, "ci95": [0.06, 0.16]}},
                "F_FREQUENCY": {"margin": {"point": 0.10, "ci95": [0.05, 0.15]}},
                "F_SCRAMBLE": {"margin": {"point": 0.20, "ci95": [0.15, 0.25]}}},
            "CONSERVATIVE_ties": {
                "A_ORTHOGRAPHIC": {"margin": {"point": -0.02, "ci95": [-0.07, 0.03]}},
                "F_FREQUENCY": {"margin": {"point": 0.09, "ci95": [0.04, 0.14]}},
                "F_SCRAMBLE": {"margin": {"point": 0.19, "ci95": [0.14, 0.24]}}}}}},
    }), encoding="utf-8")
    r = vbc.check_cell(str(p))
    assert r["tie_conventions_present"] == ["CONSERVATIVE_ties", "optimistic_ties"]
    assert r["binding_floor"] == "A_ORTHOGRAPHIC|CONSERVATIVE_ties", (
        "the CONSERVATIVE convention must bind and must be NAMED; got "
        f"{r['binding_floor']!r} at {r['min_ci_lo']}")
    assert r["min_ci_lo"] < 0 < 0.06, (
        "under the optimistic convention alone this arm clears at +0.06; the report must not "
        "silently take the flattering convention")


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
