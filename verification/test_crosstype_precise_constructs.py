"""Scaffold-free witness: the CONSTRUCTIVE glass-box path for the modern cross-type common->name bridge
(route_the_unified_referent... follow-on). Prototypes the two pieces the research named and measures how far
they close the gap on GUM -- honestly.

PC1 the ANAPHORICITY GATE + precise-constructs is NET-POSITIVE where FORCE-binding is net-negative: gated
    precision (>= 0.85) FAR exceeds ungated force-bind precision (~0.32) on the identical person-cleaned
    anaphoric-to-name population -- gating turns a flooding, wrong-most-of-the-time bind into a clean one.
PC2 a proper PRECISE-CONSTRUCTS detector recovers a real slice (>= 0.08, ~25x the narrow detector's 0.004),
    at high precision -- the in-text-stated roles ("Dvorak, the director") a narrow detector missed.
PC3 the RESIDUAL is the majority (>= 0.6) and is genuine world-knowledge (famous-person roles + local
    characters whose role the text never states) -- the honest ceiling that needs a role/occupation KB, not a
    better discourse mechanism.

Re-derives live from experiments.exp_crosstype_precise_constructs_gum_v1.run() on GUM.
Run: .venv/Scripts/python.exe verification/test_crosstype_precise_constructs.py
"""
import os
import sys

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)
os.environ.setdefault("PYTHONHASHSEED", "0")

import experiments.exp_crosstype_precise_constructs_gum_v1 as PC

PASS = FAIL = 0


def chk(name, cond, detail=""):
    global PASS, FAIL
    ok = bool(cond)
    print(("  PASS " if ok else "  FAIL ") + name + ("" if not detail else "  [%s]" % detail), flush=True)
    PASS += int(ok); FAIL += int(not ok)
    return ok


def main():
    r = PC.run(verbose=False)
    chk("PC1 the anaphoricity gate + precise-constructs is NET-POSITIVE (gated precision >> force-bind precision)",
        r["GATED_precise_PRECISION"] >= 0.85 and r["GATED_precise_PRECISION"] > r["FORCE_bind_precision"] + 0.3,
        "gated %.3f vs force %.3f" % (r["GATED_precise_PRECISION"], r["FORCE_bind_precision"]))
    chk("PC2 the OPTIMIZED detector recovers a real slice (>= 0.12, ~30x the narrow 0.004; ceiling ~0.19)",
        r["GATED_precise_hit_rate"] >= 0.12,
        "gated hit-rate %.3f (pop %d)" % (r["GATED_precise_hit_rate"], r["anaphoric_to_name_person_pop"]))
    chk("PC3 the residual is the majority (world-knowledge / context) -- not closed by the glass-box text path",
        r["residual_no_predication_frac"] >= 0.6,
        "residual %.3f" % r["residual_no_predication_frac"])
    # PC4 the acquired Wikidata OCCUPATION KB is a LOCATED NEGATIVE: it adds ~no coverage over the text path,
    #     because definite descriptors are age/gender/relation/context, NOT the person's catalogued occupation.
    kl = r["kb_LOCATED_NEGATIVE"]
    chk("PC4 the occupation KB is a LOCATED NEGATIVE (adds ~0 coverage; descriptor!=occupation almost always)",
        r["GATEDKB_hit_rate"] <= r["GATED_precise_hit_rate"] + 0.01
        and kl["of_those_the_descriptor_matches_the_occupation"] <= 2,
        "text %.3f -> +KB %.3f ; descriptor-matches-occupation %d/%d"
        % (r["GATED_precise_hit_rate"], r["GATEDKB_hit_rate"],
           kl["of_those_the_descriptor_matches_the_occupation"],
           kl["definites_whose_entity_has_occupation_roles"]))
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
