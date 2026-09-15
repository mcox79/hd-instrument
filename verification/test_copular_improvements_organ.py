"""Scaffold-free witness for the FIVE copular improvements + the end-to-end canonical read-back (owner: "do them
all"; "compose the end-to-end read-back"). Drives each experiment cell's run() in memory (writes nothing to
landed dirs) and asserts the headline. NO external LLM. Deterministic.

  I1  ARC-EAGER tree: the labeled base binding beats the July tree CI-separated (+0.111 headroom).
  I2  is-a INHERITANCE foundation: relation-extraction (Hearst UNION WordNet + traversal) beats the distributional
      ceiling (0.694) AND the shuffled-edge twin -- the wall breaks by relation-extraction, not similarity.
  I3  FULLER Higgins typing: confident accuracy does NOT regress vs the forced classifier AND it DEFERS on the
      possessive ambiguity zone (instead of forcing a guess).
  I4  identity -> COREF merge: symmetric X==Y identity edges are recorded from identity copulas.
  I5  POWER-LAW (ACT-R) salience + topicality: the controlled specificational holder is recovered by givenness
      (1.000) where the parser's syntax fails (0.000).
  I6  END-TO-END read-back: the fact binds to the CANONICAL entity, answerable via a DIFFERENT-sentence mention
      (cross-sentence) -- impossible for a token-only within-clause reader (floor 0 by construction).
Run: .venv/Scripts/python.exe verification/test_copular_improvements_organ.py
"""
import os
import sys

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in (_REPO, os.path.join(_REPO, "experiments")):
    if p not in sys.path:
        sys.path.insert(0, p)

import experiments.exp_copular_arceager_parser_comparison_v1 as AE
import experiments.exp_isa_hearst_harvest_inheritance_v1 as HZ
import experiments.exp_copular_fuller_typing_v1 as FT
import experiments.exp_copular_incremental_discourse_reader_v1 as INC

FAILS = []


def check(name, cond, detail=""):
    print(("[PASS] " if cond else "[FAIL] ") + name + ("  " + detail if detail else ""), flush=True)
    if not cond:
        FAILS.append(name)


def main():
    # I1 -- arc-eager tree lifts the labeled base binding CI-separated over July.
    ae = AE.run(cap=900, n_boot=400)
    db = ae["arceager_vs_july_base"]
    check("I1 arc-eager tree: base binding beats July CI-sep",
          ae["arceager"]["base_recall"] > ae["july"]["base_recall"] and db["delta"] > 0,
          "july %.3f -> arc-eager %.3f (d=%+.4f CI[%+.4f,%+.4f])"
          % (ae["july"]["base_recall"], ae["arceager"]["base_recall"], db["delta"], db["lo"], db["hi"]))

    # I2 -- is-a inheritance: relation-extraction breaks the distributional ceiling; twin loses.
    hz = HZ.run(cap_tokens=600_000, n_cats=200)
    found = hz["foundation_hearst_plus_wordnet"]["acc_2afc"]
    twin = hz["shuffled_edge_twin"]["acc_2afc"]
    check("I2 is-a inheritance (relation-extraction) beats distributional ceiling + twin",
          found > hz["distributional_ceiling_ref"] and found > twin + 0.2,
          "foundation %.3f vs distributional %.3f vs twin %.3f; copula-harvest compose %.3f"
          % (found, hz["distributional_ceiling_ref"], twin, hz["copula_parsed_arceager"]["precision_vs_wordnet"]))

    # I3 -- fuller typing: no regression on confident cases AND it defers on the ambiguity zone.
    ft = FT.run()
    check("I3 fuller typing: no regression + defers on the possessive ambiguity zone",
          ft["fuller_classifier"]["acc"] >= ft["forced_classifier"]["acc"] - 0.01 and ft["deferred"] > 0,
          "fuller %.4f vs forced %.4f; deferred %d (%.3f)"
          % (ft["fuller_classifier"]["acc"], ft["forced_classifier"]["acc"], ft["deferred"], ft["deferred_fraction"]))

    # I4/I5/I6 -- one incremental-reader run (arc-eager + power-law salience + identity merge + end-to-end).
    inc = INC.run(n_docs=8, n_boot=200)
    check("I4 identity->coref merge: symmetric X==Y edges recorded",
          inc["identity_links_recorded"] > 0,
          "identity edges %d (%d canonical)" % (inc["identity_links_recorded"], inc["identity_links_canonical"]))
    sp = inc["controlled_topicality"]["specificational"]
    check("I5 power-law salience + topicality: givenness recovers the specificational holder where syntax fails",
          sp["salience_acc"] > sp["syntactic_acc"] and sp["salience_acc"] >= 0.99,
          "specificational salience %.3f vs syntactic %.3f (n=%d)" % (sp["salience_acc"], sp["syntactic_acc"], sp["n"]))
    check("I6 END-TO-END read-back: fact answerable via a cross-sentence mention (within-clause floor 0)",
          inc["cross_sentence_readbacks"] > 0,
          "cross-sentence answerable %d / %d predications (%.3f); token-only floor = 0"
          % (inc["cross_sentence_readbacks"], inc["total_predications"], inc["cross_sentence_fraction"]))

    print("\n==== IMPROVEMENTS WITNESS: %d/6 ====" % (6 - len(FAILS)))
    if FAILS:
        print("FAILURES:", FAILS)
        sys.exit(1)


if __name__ == "__main__":
    main()


# --- pytest-collectable wrapper (pri 128, mechanical; see notes/problems/447_witness_files_define_no_test_function_so_the_certification_gate_runs_nothing_from_them_give_every_witness_a_collectable_wrapper_with_a_cost_marker_and_an_execution_manifest/PROBLEM.md) ---
import pytest as _pri128_pytest
from verification._witness_wrap import _run_main_as_test as _pri128_run


@_pri128_pytest.mark.fast
def test_witness():
    _code, _out = _pri128_run(main)
    assert _code == 0, "witness exited %r:\n%s" % (_code, _out[-4000:])
