"""Witness -- PHASE A/B: the mined directed causal-testimony store on POSITION-BALANCED causal SELECTION (e-CARE +
COPA), the instrument TellMeWhy's position-confound (pairwise-AUC 0.91) hid.

VERDICT (strengthened PARTIAL): on a position-FREE instrument the causal store beats the association floor + the
info-free twin where association is WEAK (COPA), but is redundant-with-association where association is STRONG
(e-CARE), and its absolute accuracy is scale-capped below the non-LLM mined-KB ceiling (0.70, CausalNet web-scale).

  W1 POSITION-FREE WIN (COPA, weak-lexical regime): causal_directed beats the LEXICAL-association floor CI-sep.
  W2 TWIN LOSES (COPA): causal_directed beats its shuffled-effect twin CI-sep -- the signal is real, not coverage.
  W3 HONEST LIMIT (e-CARE, strong-lexical regime): causal beats the twin but LOSES to lexical (association dominates);
     the association+causal COMBINATION adds nothing over the twin-combination at power (redundant / scale-capped).
  W4 causal_directed beats chance (0.50) CI-sep on BOTH datasets (the bar's generic-ATOMIC ceiling), twin ~ chance.

Runs the Phase A eval at FULL scale (~2-3 min) to reproduce the CI-separated COPA headline (the effect needs n=1000;
it is weaker/nosier at smoke). Reads the landed combination metrics for W3's redundancy claim.
Run: .venv/Scripts/python.exe verification/test_causal_selection_positionfree.py
"""
from __future__ import annotations
import json, os, sys

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "3")
_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from experiments import exp_causal_selection_ecare_copa_v1 as SEL


def check(name, cond, detail=""):
    print("[%s] %s: %s" % ("PASS" if cond else "FAIL", name, detail))
    return bool(cond)


def main():
    o = SEL.run(smoke=False)
    ec = o["datasets"]["ecare"]; co = o["datasets"]["copa"]
    oks = []

    oks.append(check(
        "W1 POSITION-FREE WIN (COPA): causal_directed beats the LEXICAL-association floor CI-sep",
        co["paired_directed_minus_lexical_full"]["ci"][0] > 0,
        "COPA causal %.3f vs lexical %.3f | paired %+.4f CI%s" % (
            co["full"]["causal_directed"]["acc"], co["full"]["lexical"]["acc"],
            co["paired_directed_minus_lexical_full"]["delta"], co["paired_directed_minus_lexical_full"]["ci"])))

    oks.append(check(
        "W2 TWIN LOSES (COPA): causal_directed beats its shuffled-effect twin CI-sep",
        co["paired_directed_minus_twin_full"]["ci"][0] > 0,
        "COPA twin %.3f | paired(directed-twin) %+.4f CI%s" % (
            co["full"]["causal_twin"]["acc"], co["paired_directed_minus_twin_full"]["delta"],
            co["paired_directed_minus_twin_full"]["ci"])))

    oks.append(check(
        "W3 HONEST LIMIT (e-CARE): causal beats the twin but association (lexical) DOMINATES (lexical > causal)",
        ec["paired_directed_minus_twin_full"]["ci"][0] > 0 and ec["full"]["lexical"]["acc"] > ec["full"]["causal_directed"]["acc"],
        "e-CARE causal %.3f lexical %.3f twin %.3f | paired(directed-twin) %+.4f%s (directed-lexical) %+.4f%s" % (
            ec["full"]["causal_directed"]["acc"], ec["full"]["lexical"]["acc"], ec["full"]["causal_twin"]["acc"],
            ec["paired_directed_minus_twin_full"]["delta"], ec["paired_directed_minus_twin_full"]["ci"],
            ec["paired_directed_minus_lexical_full"]["delta"], ec["paired_directed_minus_lexical_full"]["ci"])))

    oks.append(check(
        "W4 causal_directed beats chance (0.50) CI-sep on BOTH datasets (the generic-ATOMIC ceiling), twin ~ chance",
        co["full"]["causal_directed"]["ci"][0] > 0.5 and ec["full"]["causal_directed"]["ci"][0] > 0.5
        and abs(co["full"]["causal_twin"]["acc"] - 0.5) < 0.03 and abs(ec["full"]["causal_twin"]["acc"] - 0.5) < 0.03,
        "COPA causal %.3f CI%s | e-CARE causal %.3f CI%s" % (
            co["full"]["causal_directed"]["acc"], co["full"]["causal_directed"]["ci"],
            ec["full"]["causal_directed"]["acc"], ec["full"]["causal_directed"]["ci"])))

    # W5: combination redundancy (read landed metrics; the scale/redundancy ceiling)
    cmb_path = os.path.join(_REPO, "data", "exp_causal_selection_combined_v1", "metrics.json")
    if os.path.exists(cmb_path):
        cmb = json.load(open(cmb_path))
        ecc = cmb["datasets"]["ecare"]["paired_combined_minus_twincombined"]
        oks.append(check(
            "W5 SCALE/REDUNDANCY CEILING: on e-CARE the association+causal combination does NOT beat the "
            "twin-combination at power (causal is redundant with association where association is strong)",
            ecc["ci"][0] <= 0 <= ecc["ci"][1],
            "e-CARE combined-twincombined %+.4f CI%s" % (ecc["delta"], ecc["ci"])))

    n = sum(oks)
    print("=" * 100)
    print("%s (%d/%d)" % ("ALL CHECKS PASS" if n == len(oks) else "SOME CHECKS FAILED", n, len(oks)))
    print("=" * 100)
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
