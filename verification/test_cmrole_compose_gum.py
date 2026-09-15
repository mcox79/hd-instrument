"""Scaffold-free witness: the FULL landed role stack (Competition-Model + incremental-parser STRUCTURE cue)
COMPOSES with the unified referent on MODERN GUM -- three landed wins stack, and the residual is the understood
glass-box-vs-trained-parser ceiling.

  C1  the full landed stack (CM + incremental_subject_before structure cue + by-phrase cue), validated only on 19c
      LitBank, TRANSFERS to modern GUM: it beats POSITIONAL roles on the entity-KB hard-link, and its CUE STRUCTURE is
      load-bearing (the shuffled-cue info-free twin LOSES CI-separated).
  C2  the incremental-parser STRUCTURE cue (the embedded-clause tie fix) adds on top of CM on the entity-KB hard-link
      (positive), and COMMON-noun resolution fully recovers gold-role quality already with CM (CI-separated over positional).
  C3  a residual to GOLD roles remains even with the FULL glass-box stack -> the understood glass-box-vs-trained-parser
      ceiling (a trained parser is barred: it loses OOD, this project's documented failure mode), NOT a new wall.

Reads data/exp_cmrole_compose_gum_v1/metrics_full.json.
Run: .venv/Scripts/python.exe verification/test_cmrole_compose_gum.py
"""
import json
import os
import sys

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
M = os.path.join(_REPO, "data", "exp_cmrole_compose_gum_v1", "metrics_full.json")
PASS = FAIL = 0


def chk(name, cond, detail=""):
    global PASS, FAIL
    ok = bool(cond)
    print(("  PASS " if ok else "  FAIL ") + name + ("" if not detail else "  [%s]" % detail), flush=True)
    PASS += int(ok); FAIL += int(not ok)
    return ok


def main():
    T = json.load(open(M))["result"]["TEST"]
    kb, cm = T["kb_hardlink"], T["common"]
    chk("C1 full landed stack (CM+structure) transfers to modern GUM: beats positional + cue structure load-bearing",
        kb["cm_struct"] >= kb["positional"] and kb["struct_minus_positional"]["delta"] > 0
        and kb["struct_minus_twin"]["twin_loses"],
        "KB positional %.4f -> CM %.4f -> CM+STRUCT %.4f | STRUCT-pos %+.4f | STRUCT-twin %+.4f loses=%s" % (
            kb["positional"], kb["cm"], kb["cm_struct"], kb["struct_minus_positional"]["delta"],
            kb["struct_minus_twin"]["delta"], kb["struct_minus_twin"]["twin_loses"]))
    chk("C2 the incremental-parser STRUCTURE cue adds on top of CM (KB); COMMON fully recovers gold with CM (CI-sep)",
        kb["struct_minus_cm"]["delta"] > 0 and cm["cm_minus_positional"]["CIsep"]
        and cm["cm_minus_gold"]["recovers_to_gold"],
        "KB STRUCT-CM %+.4f | COMMON CM-positional CIsep=%s, CM-gold %+.4f recovers=%s" % (
            kb["struct_minus_cm"]["delta"], cm["cm_minus_positional"]["CIsep"],
            cm["cm_minus_gold"]["delta"], cm["cm_minus_gold"]["recovers_to_gold"]))
    chk("C3 a residual to GOLD remains even with the FULL glass-box stack -> glass-box-vs-trained-parser ceiling",
        not kb["struct_minus_gold"]["recovers_to_gold"] and kb["struct_minus_gold"]["delta"] < 0,
        "KB CM+STRUCT-gold %+.4f (recovers=%s); ~%d%% of the positional->gold gap recovered" % (
            kb["struct_minus_gold"]["delta"], kb["struct_minus_gold"]["recovers_to_gold"],
            round(100 * kb["struct_minus_positional"]["delta"] / max(1e-9, kb["gold"] - kb["positional"])))
        )
    print("\n%d/%d checks passed" % (PASS, PASS + FAIL), flush=True)
    return 0 if FAIL == 0 else 1


if __name__ == "__main__":
    sys.exit(main())


# --- pytest-collectable wrapper (pri 128, mechanical; see notes/problems/447_witness_files_define_no_test_function_so_the_certification_gate_runs_nothing_from_them_give_every_witness_a_collectable_wrapper_with_a_cost_marker_and_an_execution_manifest/PROBLEM.md) ---
import pytest as _pri128_pytest
from verification._witness_wrap import _run_main_as_test as _pri128_run


@_pri128_pytest.mark.corpus
def test_witness():
    _code, _out = _pri128_run(main)
    assert _code == 0, "witness exited %r:\n%s" % (_code, _out[-4000:])
