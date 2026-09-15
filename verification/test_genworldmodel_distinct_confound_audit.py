"""Witness -- ADVERSARIAL confound audit of the sot_accum/distinct GLUCOSE win. Two things the SOT analysis
missed: (1) a POSITION floor was never run -- `earliest` (pick first sentence) CI-beats `distinct`; (2) the
1/k_s distinctiveness WEIGHTING is inert-to-harmful -- raw `overlap_count` CI-beats `distinct`. So the honest
semantic signal is raw content-overlap count (which itself loses to position), and "cue-distinctiveness" is the
wrong attribution. `topical` (max word-relatedness) was a weak baseline (tie-rate ~1.8, argmax breaks ties by
earliest), which is why the reported +0.159 was inflated.

problem: build_the_generative_result_state_world_model
Run: .venv/Scripts/python.exe verification/test_genworldmodel_distinct_confound_audit.py
"""
from __future__ import annotations
import os, sys
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "3")
_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)
from experiments import exp_genworldmodel_distinct_confound_audit_v1 as A


def check(name, cond, detail=""):
    print("[%s] %s: %s" % ("PASS" if cond else "FAIL", name, detail))
    return bool(cond)


def main():
    o = A.run(n=3000)
    cs = o["coalition_subset"]; ov = cs["overall"]
    oks = []

    oks.append(check(
        "W1 a POSITION floor was missed: `earliest` (pick first sentence) CI-beats `distinct` on the coalition subset",
        cs["distinct_vs_pos_best"]["ci"][1] < 0 and ov[cs["pos_best"]] > ov["distinct"],
        "earliest/%s %.3f vs distinct %.3f (distinct-pos %+.4f CI%s)" % (
            cs["pos_best"], ov[cs["pos_best"]], ov["distinct"],
            cs["distinct_vs_pos_best"]["delta"], cs["distinct_vs_pos_best"]["ci"])))

    oks.append(check(
        "W2 the 1/k_s distinctiveness WEIGHTING is inert-to-harmful: raw overlap_count >= distinct (distinct does "
        "NOT CI-beat overlap_count)",
        not cs["distinct_vs_overlap_count"]["ci_sep"],
        "distinct %.3f vs overlap_count %.3f (%+.4f CI%s)" % (
            ov["distinct"], ov["overlap_count"], cs["distinct_vs_overlap_count"]["delta"],
            cs["distinct_vs_overlap_count"]["ci"])))

    oks.append(check(
        "W3 the reported baseline was WEAK: raw overlap_count CI-beats `topical` (max word-relatedness saturates "
        "+ breaks ties by earliest), so the +0.159 over topical was inflated",
        cs["overlap_count_vs_topical"]["ci_sep"],
        "overlap_count %.3f vs topical %.3f (%+.4f CI%s) | topical_tie_rate %.2f" % (
            ov["overlap_count"], ov["topical"], cs["overlap_count_vs_topical"]["delta"],
            cs["overlap_count_vs_topical"]["ci"], o["topical_tie_rate_mean"])))

    n = sum(oks)
    print("=" * 92)
    print("%s (%d/%d)  verdict=%s  n=%d" % (
        "ALL CHECKS PASS" if n == len(oks) else "SOME CHECKS FAILED", n, len(oks), o["verdict"], cs["n"]))
    print("=" * 92)
    return 0 if n == len(oks) else 1


if __name__ == "__main__":
    sys.exit(main())


# --- pytest-collectable wrapper (pri 128, mechanical; see notes/problems/447_witness_files_define_no_test_function_so_the_certification_gate_runs_nothing_from_them_give_every_witness_a_collectable_wrapper_with_a_cost_marker_and_an_execution_manifest/PROBLEM.md) ---
import pytest as _pri128_pytest
from verification._witness_wrap import _run_main_as_test as _pri128_run


@_pri128_pytest.mark.fast
def test_witness():
    _code, _out = _pri128_run(main)
    assert _code == 0, "witness exited %r:\n%s" % (_code, _out[-4000:])
