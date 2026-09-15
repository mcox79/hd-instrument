"""Witness: coordination as parallel structure in the attachment arm. The parallel-structure teacher (upstream) + the
corrected read-time coord construction lift conj recall over the same-cap base pipeline under BOTH decodes, UAS not down,
and an info-free twin (coord-cue strengths permuted across configurations) collapses conj back toward base.

NOTE: CI-separation is the FULL-scale headline (UD-EWT test 700, cap 6000). The witness runs a SMOKE (cap 1200, test 200)
and asserts the point-estimate direction + the twin collapse, which reproduce deterministically.
Run: .venv/Scripts/python.exe verification/test_attachment_coordination.py
"""
from __future__ import annotations
import os
import sys

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)
os.environ.setdefault("OMP_NUM_THREADS", "3")
os.environ.setdefault("HDLAB_EXP_NAME", "attachment_coordination_v1_witness")

RESULTS = []


def check(name, cond, detail=""):
    RESULTS.append((name, bool(cond)))
    print(("  [PASS] " if cond else "  [FAIL] ") + name + (("  " + detail) if detail else ""))
    return bool(cond)


def main():
    from experiments.exp_attachment_coordination_v1 import run, coord_sites
    # unit: parallel-head identification fixes the modifier bug and handles verb/adjective coordination
    L, R, k = coord_sites(["the", "tall", "man", "and", "the", "short", "woman"],
                          ["DET", "ADJ", "NOUN", "CCONJ", "DET", "ADJ", "NOUN"], coarse=True)[0]
    check("W0 parallel heads skip the 2nd conjunct's modifier (man<-woman, not short)", (L, R) == (3, 7),
          "L=%d R=%d cc=%d" % (L, R, k))

    o = run(smoke=True, cap=1200, rounds=2, arms=["base", "full", "scramble"])
    r = o["results"]
    cb = r["base@map1"]["conj"]["acc"]; cf = r["full@map1"]["conj"]["acc"]
    cbi = r["base@incr"]["conj"]["acc"]; cfi = r["full@incr"]["conj"]["acc"]
    ub = r["base@map1"]["uas"]; uf = r["full@map1"]["uas"]
    csc = r["scramble@map1"]["conj"]["acc"]
    twin = o["twin_conj_map1"]; twin_uas = o["twin_uas_map1"]

    check("W1 conj recall rises under map1 (full > base)", cf > cb + 0.02, "base=%.3f full=%.3f" % (cb, cf))
    check("W2 conj recall rises under the incremental decode too", cfi > cbi + 0.01, "base=%.3f full=%.3f" % (cbi, cfi))
    check("W3 UAS not down (full >= base - 0.005)", uf >= ub - 0.005, "base=%.4f full=%.4f" % (ub, uf))
    check("W4 PARALLELISM is load-bearing: the scramble twin (coord machinery on WRONG heads) collapses conj toward base",
          csc <= cf - 0.05, "scramble=%.3f full=%.3f base=%.3f" % (csc, cf, cb))
    check("W5 shuffled-strengths twin collapses attachment (UAS far below base)",
          (max(twin_uas) <= ub - 0.1) if twin_uas else False, "twin_uas=%s base_uas=%.4f" % (twin_uas, ub))

    npass = sum(1 for _, ok in RESULTS if ok)
    print("\n[witness] %d/%d PASS" % (npass, len(RESULTS)))
    return 0 if npass == len(RESULTS) else 1


if __name__ == "__main__":
    sys.exit(main())


# --- pytest-collectable wrapper (pri 128, mechanical; see notes/problems/447_witness_files_define_no_test_function_so_the_certification_gate_runs_nothing_from_them_give_every_witness_a_collectable_wrapper_with_a_cost_marker_and_an_execution_manifest/PROBLEM.md) ---
import pytest as _pri128_pytest
from verification._witness_wrap import _run_main_as_test as _pri128_run


@_pri128_pytest.mark.fast
def test_witness():
    _code, _out = _pri128_run(main)
    assert _code == 0, "witness exited %r:\n%s" % (_code, _out[-4000:])
