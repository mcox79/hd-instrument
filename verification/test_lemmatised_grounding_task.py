"""Scaffold-free witness for notes/problems/lookup_does_not_lemmatise.

Reproduces the HEADLINE without touching any landed directory: on inflected running-text forms of
the SimVerb-test benchmark, lemmatising the grounded-norms lookup (LEMMA) beats the information-free
random-covered-word twin (TWIN) CI-separated, while the raw exact-string lookup (RAW) is mute.

It imports the experiment module as a library and calls score_population() -- it computes, it does
not re-run the cell, so no metrics.json is rewritten. Exit 0 = headline holds.

Run:  .venv/Scripts/python.exe verification/test_lemmatised_grounding_task.py
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

REPO = Path(__file__).resolve().parent.parent
for _p in (str(REPO), str(REPO / "experiments")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import exp_lemmatised_grounding_task_v1 as EX     # noqa: E402

# Reverify needs to REPRODUCE the CI-separated margin, not the exact landed CI half-width. The
# bootstrap CI width is governed by n (2490 here), not n_boot once n_boot is large, so 3000
# resamples reproduces the headline in a fraction of the landed run's time.
EX.N_BOOT = 3000


def main() -> int:
    EX.selftest()
    r, _ = EX.score_population("SIMVERB_TEST")
    lemma = r["rho"]["LEMMA"]["point"]
    twin = r["rho"]["TWIN"]["point"]
    base = r["rho"]["BASE"]["point"]
    floor = r["strongest_floor"]
    mf = r["margin_LEMMA_vs_floor"]
    n = r["n_pairs_inflected"]
    fr = r["false_recovery"]["false_rate"]
    print(f"SIMVERB_TEST  n_infl={n}  BASE={base:+.4f} LEMMA={lemma:+.4f} TWIN={twin:+.4f}  "
          f"strongest_floor={floor}({r['rho'][floor]['point']:+.4f})  "
          f"margin(LEMMA-floor)={mf['point']:+.4f} CI[{mf['ci95'][0]:+.4f},{mf['ci95'][1]:+.4f}] "
          f"{r['band_LEMMA_vs_floor']}  vsTWIN={r['band_LEMMA_vs_TWIN']}  clears_bar={r['clears_bar']}  "
          f"false_rate={fr:.3f}", flush=True)

    ok = True
    if not (base > 0.05):
        print("FAIL: BASE positive control does not carry meaning (asset mute on this population)")
        ok = False
    if r["band_LEMMA_vs_TWIN"] != "ABOVE":
        print("FAIL: LEMMA does not beat the info-free TWIN CI-separated")
        ok = False
    if not r["clears_bar"]:
        print("FAIL: LEMMA does not clear the strongest floor (TWIN/ORTHO/FREQ) CI-separated")
        ok = False
    print("WITNESS PASS" if ok else "WITNESS FAIL", flush=True)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())


# --- pytest-collectable wrapper (pri 128, mechanical; see notes/problems/447_witness_files_define_no_test_function_so_the_certification_gate_runs_nothing_from_them_give_every_witness_a_collectable_wrapper_with_a_cost_marker_and_an_execution_manifest/PROBLEM.md) ---
import pytest as _pri128_pytest
from verification._witness_wrap import _run_main_as_test as _pri128_run


@_pri128_pytest.mark.fast
def test_witness():
    _code, _out = _pri128_run(main)
    assert _code == 0, "witness exited %r:\n%s" % (_code, _out[-4000:])
