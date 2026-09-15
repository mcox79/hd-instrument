"""SCAFFOLD-FREE WITNESS for problem the_tense_agnostic_detector_drops_tense_needed_by_the_time_dimension.

Recomputes EVERY headline from source (UD English-EWT FEATS gold + the in-substrate tagger + the live
hdlab.SituationReader). Does NOT read any landed metrics.json -- it calls the mechanism on freshly
loaded gold and asserts the bars, so a green run is independent evidence.

Run:  .venv/Scripts/python.exe verification/test_tense_preserving_event_detector.py
"""
import os
import sys

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import experiments.exp_tense_preserving_event_detector_v1 as TP
import experiments.exp_tense_preserving_live_reader_and_timeline_v1 as LT

PASS = []


def check(name, cond, detail=""):
    PASS.append(bool(cond))
    print(f"[{'PASS' if cond else 'FAIL'}] {name}  {detail}")


def main():
    # W0 -- the composition is correct on canonical verb groups + mark-and-inherit (can-fail)
    try:
        TP._self_test()
        check("W0 verb-group composition correct on 10 canonical groups + mark-and-inherit", True)
    except AssertionError as e:
        check("W0 verb-group composition", False, str(e))

    # Recompute the two runtime-faithful arms fresh from UD-EWT test gold
    ins = TP.evaluate("test", "surface", use_gold_upos=False)   # full in-substrate pipeline
    fin = TP.evaluate("test", "finetag", use_gold_upos=True)    # +fine-tag optimization

    # W1 -- word-tense CI-separated over the strongest constant floor; info-free twin LOSES
    wt = ins["word_tense"]
    check("W1 word-tense (in-substrate) CI-sep over majority floor AND placeholder; twin loses",
          wt["beats_majority_ci"] and wt["ci_lo"] > wt["placeholder_floor_allPAST"] and wt["beats_twin_ci"],
          f"acc={wt['acc']} [{wt['ci_lo']},{wt['ci_hi']}] > maj {wt['majority_floor']} "
          f"placeholder {wt['placeholder_floor_allPAST']} twin {wt['twin_shuffled_p95']}")

    # W2 -- the COMPOSITIONAL win: aspect + voice (no word-tense label carries these)
    cl = ins["clausal"]
    check("W2 aspect + voice recovered (the compositional Reichenbach win)",
          cl["aspect_acc"] > 0.9 and cl["voice_acc"] > 0.85,
          f"aspect={cl['aspect_acc']} voice={cl['voice_acc']}")

    # W3 -- FINITE clausal tense (the temporal anchors) CI-separated over floors
    fo = ins["finite_only"]
    check("W3 FINITE clausal-tense >> placeholder+majority floors (the temporal anchors)",
          fo["clausal_tense_acc"] > fo["majority_floor"] + 0.2
          and fo["clausal_tense_acc"] > fo["placeholder_floor_allPAST"] + 0.3,
          f"finite clausal-tense={fo['clausal_tense_acc']} vs maj {fo['majority_floor']} "
          f"placeholder {fo['placeholder_floor_allPAST']} (n={fo['n']})")

    # W4 -- EFFECTIVE temporal location (mark-and-inherit) beats floors CI-separated; twin loses
    ef = ins["effective_temporal_location"]
    check("W4 EFFECTIVE temporal location (every event placed) CI-sep over floors; twin loses",
          ef["beats_majority_ci"] and ef["beats_twin_ci"]
          and ef["ci_lo"] > ef["placeholder_floor_allPAST"],
          f"acc={ef['acc']} [{ef['ci_lo']},{ef['ci_hi']}] > maj {ef['majority_floor']} "
          f"placeholder {ef['placeholder_floor_allPAST']} twin {ef['twin_shuffled_p95']} (n={ef['n']})")

    # W5 -- the non-finite WALL is understood: inherit >> standalone; oracle-anchor ~ finite ceiling
    check("W5 mark-and-inherit is the right instrument: NF inherited > standalone; oracle ~ finite",
          ef["nonfinite_inherited_acc"] > ef["nonfinite_standalone_acc_NEGATIVE"] + 0.2
          and ef["nonfinite_inherited_oracle_anchor_acc"] > 0.8,
          f"NF standalone(NEG)={ef['nonfinite_standalone_acc_NEGATIVE']} -> inherit "
          f"{ef['nonfinite_inherited_acc']} -> oracle {ef['nonfinite_inherited_oracle_anchor_acc']}")

    # W6 -- the brief's NEGATIVE HINT is REFUTED: the extra present-tense verbs ARE recoverable
    px = ins["per_xpos_word_tense_acc"]
    check("W6 negative hint refuted: present-tense (VBZ/VBP) recoverable, not the ambiguous ones",
          px.get("VBZ", 0) > 0.9 and px.get("VBP", 0) > 0.8,
          f"VBZ={px.get('VBZ')} VBP={px.get('VBP')} (the hard ones are non-finite VB/VBG)")

    # W7 -- GENERALIZATION: the fixed composition holds on a different (train) split
    gen = TP.evaluate("train", "surface", use_gold_upos=True, cap=2000)
    check("W7 generalizes: fixed composition holds on the train split (not fit to any corpus)",
          gen["finite_only"]["clausal_tense_acc"] > 0.8
          and gen["word_tense"]["beats_majority_ci"],
          f"train finite clausal-tense={gen['finite_only']['clausal_tense_acc']} "
          f"word-tense acc={gen['word_tense']['acc']}")

    # W8 -- the fine-tag OPTIMIZATION lifts word-tense (separable English-morphology parameter)
    check("W8 fine-tag parameter lifts word-tense over the in-substrate surface rule",
          fin["word_tense"]["acc"] > ins["word_tense"]["acc"] + 0.05,
          f"surface={ins['word_tense']['acc']} -> finetag={fin['word_tense']['acc']}")

    # W9 -- RECALL PRESERVED EXACTLY through the live SituationReader.read(); tense stops being constant
    rp = LT.recall_preservation()
    check("W9 live read(): event set IDENTICAL to placeholder (recall preserved) + tense now varied",
          rp["event_sets_identical"] and rp["placeholder_is_constant"] and rp["preserving_is_varied"],
          f"n_events={rp['n_events']} identical={rp['event_sets_identical']} "
          f"placeholder_tenses={rp['placeholder_distinct_tenses']} "
          f"preserving_tenses={rp['preserving_distinct_tenses']}")

    # W10 -- PAYOFF: is_pp AGREEMENT with the timeline's own extractor on shared flashback events
    b1 = LT.timeline_ispp_fidelity()
    check("W10 timeline payoff: is_pp agreement ~1.0 (flashback signal preserved) + superset events",
          b1["is_pp_agreement"] >= 0.95 and b1["unified_extra_events_recovered"] > 0,
          f"is_pp_agreement={b1['is_pp_agreement']} shared={b1['shared_events']} "
          f"extra_recovered={b1['unified_extra_events_recovered']}")

    # W11 -- PAYOFF: no reconstruction regression on a constructed flashback gold
    b2 = LT.timeline_reconstruction_gold()
    check("W11 timeline payoff: unified reconstruction >= stock on flashback gold (no regression)",
          b2["no_regression"] and b2["unified_acc"] >= 0.75,
          f"unified={b2['unified_acc']} stock={b2['stock_acc']} no_regression={b2['no_regression']}")

    print(f"\n{'ALL PASS' if all(PASS) else 'SOME FAILED'}: {sum(PASS)}/{len(PASS)} checks")
    sys.exit(0 if all(PASS) else 1)


if __name__ == "__main__":
    main()


# --- pytest-collectable wrapper (pri 128, mechanical; see notes/problems/447_witness_files_define_no_test_function_so_the_certification_gate_runs_nothing_from_them_give_every_witness_a_collectable_wrapper_with_a_cost_marker_and_an_execution_manifest/PROBLEM.md) ---
import pytest as _pri128_pytest
from verification._witness_wrap import _run_main_as_test as _pri128_run


@_pri128_pytest.mark.fast
def test_witness():
    _code, _out = _pri128_run(main)
    assert _code == 0, "witness exited %r:\n%s" % (_code, _out[-4000:])
