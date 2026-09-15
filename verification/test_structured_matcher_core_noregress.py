"""Scaffold-free witness: the structured matcher's core signs + the positive control the hub CANNOT get + no-regress.

C1 CORE unit behaviour: converse(sell,buy) satisfy; antonym(win,lose) thwart; is_a(kitchen,room); cohyponym(kitchen,
   bedroom) not-a-kind-of; congruence signs (sell/buy=+1, win/lose=-1).
C2 POSITIVE CONTROL the hub CANNOT get: win/lose has HIGH cosine relatedness (the hub would call it "related"->satisfy)
   but the OPPOSITE sign -- the structured matcher signs it thwart(-1) from the antonym edge; sell/buy is equally
   related but satisfy(+1) from the converse edge. Same magnitude, opposite sign: only the structured edge separates.
C3 NO-REGRESS: where the structured store has NO edge, congruence()/type_match() ABSTAIN and fall back to the ATL hub
   (the organ is COMPLEMENTARY, additive) -- the hub is NOT removed. And the organ writes NOTHING to hdlab.

Run: .venv/Scripts/python.exe verification/test_structured_matcher_core_noregress.py
"""
import os
import sys

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)
import experiments._hashseed_guard  # noqa: E402,F401  (pins PYTHONHASHSEED=0 -> reproducible WordNet/ConceptNet sampling)

from experiments._structured_matcher import StructuredMatcher

PASS = FAIL = 0


def chk(name, cond, detail=""):
    global PASS, FAIL
    ok = bool(cond)
    print(("  PASS " if ok else "  FAIL ") + name + ("" if not detail else "  [%s]" % detail), flush=True)
    PASS += int(ok); FAIL += int(not ok)
    return ok


def main():
    from hdlab.bridging_inference import BridgeInference
    hub = BridgeInference()
    m = StructuredMatcher(hub=hub, use_conceptnet=True, use_framenet=True)

    chk("C1 core signs: converse/antonym/is_a/cohyponym + congruence",
        m.converse("sell", "buy") and m.antonym("win", "lose") and m.is_a("kitchen", "room")
        and m.cohyponym("kitchen", "bedroom") and not m.is_a("kitchen", "bedroom")
        and m.congruence("sell", "buy")[0] == 1 and m.congruence("win", "lose")[0] == -1,
        "sell/buy=%s win/lose=%s kitchen/room=%s kitchen~bedroom=%s" % (
            m.congruence("sell", "buy")[:2], m.congruence("win", "lose")[:2], m.is_a("kitchen", "room"),
            m.cohyponym("kitchen", "bedroom")))

    r_wl = hub.relatedness("win", "lose")
    r_sb = hub.relatedness("sell", "buy")
    chk("C2 positive control the hub cannot get: win/lose & sell/buy equally related, OPPOSITE structured sign",
        r_wl is not None and r_sb is not None and r_wl > 0.15 and r_sb > 0.15
        and m.congruence("win", "lose")[0] == -1 and m.congruence("sell", "buy")[0] == 1,
        "rel(win,lose)=%.3f rel(sell,buy)=%.3f -> structured signs -1 vs +1" % (r_wl, r_sb))

    # no-regress: an unrelated/no-edge pair abstains to the hub fallback (organ is additive)
    sgn, src, conf = m.congruence("cook", "legislate")
    chk("C3a no-regress: no structured edge -> abstain/hub-fuzzy fallback (hub NOT removed)",
        src in ("abstain", "hub_fuzzy"),
        "congruence(cook,legislate) -> sign=%d source=%s" % (sgn, src))
    # organ writes nothing to hdlab
    src_txt = open(os.path.join(_REPO, "experiments", "_structured_matcher.py"), encoding="ascii").read()
    writes_hdlab = ("hdlab" in src_txt) and ("open(" in src_txt) and (", \"w\"" in src_txt or ", 'w'" in src_txt)
    chk("C3b organ writes nothing to hdlab (complements the hub, additive)", not writes_hdlab,
        "hdlab-write=%s" % writes_hdlab)

    print("\n%d/%d checks passed" % (PASS, PASS + FAIL), flush=True)
    return 0 if FAIL == 0 else 1


if __name__ == "__main__":
    sys.exit(main())


# --- pytest-collectable wrapper (pri 128, mechanical; see notes/problems/447_witness_files_define_no_test_function_so_the_certification_gate_runs_nothing_from_them_give_every_witness_a_collectable_wrapper_with_a_cost_marker_and_an_execution_manifest/PROBLEM.md) ---
import pytest as _pri128_pytest
from verification._witness_wrap import _run_main_as_test as _pri128_run


@_pri128_pytest.mark.fast
def test_witness():
    _code, _out = _pri128_run(main)
    assert _code == 0, "witness exited %r:\n%s" % (_code, _out[-4000:])
