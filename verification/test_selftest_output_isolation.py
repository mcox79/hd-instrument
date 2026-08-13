"""SH-6 regression: a self-test run must never overwrite a full/lite run's metrics.json.

Incident this locks down: notes/metrics_overwrite_forensics_2026-08-13.md. Four cells had a
real lite/full result clobbered on disk by a later SELF-TEST run, turning three genuine
negatives (HARD_FAIL / LOCALIZED_WALL / MIDDLE) into SELFTEST_PASS and destroying the
per_seed / results_by_unit / bands / params blocks (-457 / -238 / -198 / -81 leaf keys).

Three layers, deliberately:

  T1  unit       -- isolate_selftest_output_dir() maps self_test to a DISTINCT dir.
  T2  behaviour  -- an end-to-end write through the guard leaves a pre-existing full-run
                    metrics.json byte-identical.
  T3  sensitivity-- the SAME behavioural scenario with the guard replaced by identity
                    (i.e. the pre-fix code) MUST clobber. Without T3, T2 could pass for
                    reasons unrelated to the fix, and a guard never observed failing is
                    not a verified guard.
  T4  source     -- each of the 4 affected cells actually routes its self-test metrics
                    write through the guard, rather than at the bare OUTPUT_DIR constant.

Run: .venv/Scripts/python.exe verification/test_selftest_output_isolation.py
     (also collected by pytest)
"""

import json
import os
import re
import shutil
import sys
import tempfile

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_REPO, "experiments"))

import _seed_checkpoint as _sc  # noqa: E402

AFFECTED_CELLS = (
    "exp_situation_model_assembly_learned_identity_head_v1.py",
    "exp_situation_model_assembly_encoder_backed_v1.py",
    "exp_situation_model_assembly_encoder_retrain_lite_v1.py",
    "exp_syntactic_role_agent_patient_voice_probe_v1.py",
)

# A full-run metrics.json of the shape the incident destroyed.
FULL_RUN_METRICS = {
    "verdict": "HARD_FAIL",
    "run_mode": "lite",
    "per_seed": [{"seed": 7, "q_agree": 0.737}, {"seed": 13, "q_agree": 0.788}],
    "bands": {"proven_min": 0.9},
    "params": {"train_n": 200},
}

SELFTEST_METRICS = {"verdict": "SELFTEST_PASS", "run_mode": "self_test", "selftest": {"ok": True}}


def _write_metrics(out_dir, payload):
    """Mirror the cells' _atomic_write_metrics: mkdir + tmp + os.replace."""
    os.makedirs(out_dir, exist_ok=True)
    tmp = os.path.join(out_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    os.replace(tmp, os.path.join(out_dir, "metrics.json"))


def _simulated_cell_main(base_output_dir, run_mode, isolator):
    """The shape every affected cell's main() has: resolve run_mode, pick the output dir,
    write metrics. `isolator` is the ONLY variable -- the guard, or pre-fix identity."""
    out_dir = isolator(base_output_dir, run_mode)
    _write_metrics(out_dir, SELFTEST_METRICS if run_mode == "self_test" else FULL_RUN_METRICS)
    return out_dir


def _identity_isolator(base_output_dir, run_mode):
    """The PRE-FIX behaviour: self-test and full share one output path."""
    return base_output_dir


def t1_unit():
    base = "/tmp/data/exp_zzz_v1"
    assert _sc.isolate_selftest_output_dir(base, "self_test") != base, \
        "T1 FAIL: self_test must not resolve to the full-run dir"
    assert _sc.isolate_selftest_output_dir(base, "self_test") == base + "_selftest", "T1 FAIL: suffix"
    for mode in ("full", "lite", "smoke"):
        assert _sc.isolate_selftest_output_dir(base, mode) == base, \
            "T1 FAIL: %s must be left alone" % mode
    assert _sc.isolate_selftest_output_dir(base + "_selftest", "self_test") == base + "_selftest", \
        "T1 FAIL: not idempotent (double-append)"
    print("T1 PASS  unit: isolate_selftest_output_dir maps self_test to a distinct dir")


def _run_clobber_scenario(isolator, tmp):
    """Full run lands, then a self-test runs. Returns the full run's metrics.json content after."""
    base = os.path.join(tmp, "data", "exp_probe_v1")
    _simulated_cell_main(base, "lite", isolator)
    before = open(os.path.join(base, "metrics.json"), "rb").read()
    _simulated_cell_main(base, "self_test", isolator)
    after = open(os.path.join(base, "metrics.json"), "rb").read()
    return base, before, after


def t2_behaviour():
    tmp = tempfile.mkdtemp(prefix="sh6_t2_")
    try:
        base, before, after = _run_clobber_scenario(_sc.isolate_selftest_output_dir, tmp)
        assert after == before, \
            "T2 FAIL: self-test overwrote the full run's metrics.json"
        d = json.loads(after.decode("utf-8"))
        assert d["verdict"] == "HARD_FAIL" and d["run_mode"] == "lite", \
            "T2 FAIL: full-run verdict/run_mode not preserved: %r" % d
        assert "per_seed" in d and "bands" in d and "params" in d, \
            "T2 FAIL: full-run detail blocks lost"
        st = os.path.join(base + "_selftest", "metrics.json")
        assert os.path.exists(st), "T2 FAIL: self-test wrote nowhere; it must still produce output"
        assert json.load(open(st, encoding="utf-8"))["verdict"] == "SELFTEST_PASS", \
            "T2 FAIL: self-test output landed in the wrong place"
        print("T2 PASS  behaviour: full-run metrics.json byte-identical after a self-test run")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def t3_sensitivity():
    """Negative control. Remove the fix -> the SAME scenario must clobber. If this does not
    clobber, T2 is not testing the fix and its PASS means nothing."""
    tmp = tempfile.mkdtemp(prefix="sh6_t3_")
    try:
        _base, before, after = _run_clobber_scenario(_identity_isolator, tmp)
        assert after != before, (
            "T3 FAIL: with the guard removed the full run was NOT clobbered -- this test is "
            "insensitive to the fix, so T2's PASS proves nothing. Fix the test, not the code."
        )
        assert json.loads(after.decode("utf-8"))["verdict"] == "SELFTEST_PASS", \
            "T3 FAIL: expected the pre-fix path to leave SELFTEST_PASS on disk"
        print("T3 PASS  sensitivity: without the guard the full run IS clobbered (test can fail)")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def t4_cells_wired():
    """Source-level: each affected cell must route its self-test metrics write through the
    guard. Catches a future edit that reinstates a bare OUTPUT_DIR write."""
    for fname in AFFECTED_CELLS:
        p = os.path.join(_REPO, "experiments", fname)
        src = open(p, encoding="utf-8").read()
        assert "isolate_selftest_output_dir" in src, \
            "T4 FAIL: %s does not call isolate_selftest_output_dir" % fname
        # The self-test metrics write must not target the bare module constant.
        bad = re.findall(r"_atomic_write_metrics\(\s*OUTPUT_DIR\b", src)
        assert not bad, \
            "T4 FAIL: %s still writes metrics at the bare OUTPUT_DIR (%d site(s))" % (fname, len(bad))
    print("T4 PASS  source: all %d affected cells route through the guard" % len(AFFECTED_CELLS))


# pytest entry points
def test_isolate_selftest_output_dir_unit():
    t1_unit()


def test_selftest_does_not_clobber_full_run():
    t2_behaviour()


def test_guard_removal_reproduces_the_clobber():
    t3_sensitivity()


def test_affected_cells_are_wired():
    t4_cells_wired()


if __name__ == "__main__":
    t1_unit()
    t2_behaviour()
    t3_sensitivity()
    t4_cells_wired()
    print("ALL PASS  SH-6 self-test output isolation")
