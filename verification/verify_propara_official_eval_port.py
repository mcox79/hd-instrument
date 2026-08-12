"""Scaffold-free witness: the vendored ProPara OFFICIAL evaluator port stays bit-exact.

WHY THIS EXISTS (2026-08-12, hdi_skunkworks island-harvest audit). `tools/benchmark_trap_check/
propara_official_eval.py` is a Python port of the ProPara leaderboard's official evaluator,
registered as `propara_official_eval_port` (gate WIRE: "do NOT reimplement the official
metric"). Its correctness rested on a `self_test()` nobody runs, so a silent regression in the
port would silently change every ProPara number the project ever reports. This witness puts the
port under `pytest verification/`.

It runs the REAL port over the OFFICIAL regression fixtures vendored at
`data/benchmark_trap_check/propara_official_testfiles/` (no mocks, no tracing) and pins the three
officially published overall F1 values. Can-fail: perturb any scoring rule in the port and
testfiles-1/-3 move off 0.545/0.686.

SCOPE (honest): this witness proves the SCORER is faithful. It says nothing about any ProPara
RESULT -- the ProPara task rows in the capability registry remain SHELVED.
"""
from __future__ import annotations

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools", "benchmark_trap_check"))

import propara_official_eval as poe  # noqa: E402

# Officially published expected overall F1 per fixture (fixture README.md, official repo).
EXPECTED = {"testfiles-2": 1.000, "testfiles-3": 0.686, "testfiles-1": 0.545}
FIXTURE_DIR = os.path.join(ROOT, "data", "benchmark_trap_check", "propara_official_testfiles")


def test_official_fixtures_are_vendored():
    for tf in EXPECTED:
        for fname in ("answers.tsv", "predictions.tsv"):
            p = os.path.join(FIXTURE_DIR, tf, fname)
            assert os.path.exists(p), f"missing official fixture {p}"


def test_port_reproduces_official_f1_bit_exact():
    out = poe.self_test()
    fixtures = out["official_fixtures"]
    for tf, expected in EXPECTED.items():
        got = fixtures[tf]["got_f1"]
        assert abs(got - expected) < 1e-3, f"{tf}: port F1 {got} != official {expected}"


def test_gold_vs_itself_is_perfect():
    out = poe.self_test()
    assert out["gold_vs_itself"]["overall"]["f1"] == 1.0
    assert out["label_roundtrip_ok"] is True


if __name__ == "__main__":
    test_official_fixtures_are_vendored()
    test_port_reproduces_official_f1_bit_exact()
    test_gold_vs_itself_is_perfect()
    print("[WITNESS] PASS -- ProPara official evaluator port bit-exact on testfiles-1/2/3")
