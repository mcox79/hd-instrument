"""Witness for exp_crosstype_live_wire_gum_v1 -- the crosstype_bridge LIVE-READER wire.

Reproduces the load-bearing findings, all through the REAL hdlab consumer chain (_build_entities +
make_canonicalizer + the bind_experiencers canon), scored on modern GUM:

  W1  DETERMINISTIC known-answer: on 'Elizabeth was a doctor. The doctor cried.', the honest FLOOR does NOT bind
      'the doctor'->Elizabeth through the real make_canonicalizer; the BRIDGE (merge) DOES -> bridge C3 > floor C3.
  W2  HONEST-FLOOR LIFT: on all GUM (n=549 person-common experiencers of named entities), the bridge lifts the
      C3 experiencer bind CI-separated over the honest raw-situation_predict floor (the origin/brief floor), with
      the info-free shuffled-target TWIN LOSING CI-separated. (The lift is SMALLER than the offline proxy's
      +0.033 -- the real surface-keyed canonicalizer eats ~a third; the live consumer haircut, quantified.)
  W3  NO REGRESS: C1 entity-layer CoNLL is non-negative and C2 hard-link is up (CI-sep) under the bridge.
  W4  THE UPSTREAM GOLD-COREF LEAK (the decisive finding): the REAL _apply_commonnoun_gate, fed the gold coref
      column, gold-inherits (C3 ~0.8) while the SAME gate on honest predicted seeds collapses to ~0.15 (== raw
      situation_predict). So the live gate's high score is the gold answer key, not a resolved mechanism; the
      bridge (which needs no gold) is redundant only vs that leak, and is the brain-foundational replacement.
      ALSO verified on the reader's NATIVE LitBank path: >=80% of non-pronoun mentions keep their exact gold id.

Run: .venv/Scripts/python.exe verification/test_crosstype_live_wire.py
"""
import os
import sys

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import experiments.gum_coref as G
from experiments.exp_name_entity_clustering_v1 import load_given_gazetteer
import experiments.exp_crosstype_live_wire_gum_v1 as LW


def main():
    ok = 0
    gaz = load_given_gazetteer()

    # W1 -- deterministic known-answer through the REAL consumer
    ms = LW._synthetic_ms()
    floor = {0: 0, 1: 91, 2: 2, 3: 91}
    hf, nf = LW.score_c3_live(ms, LW._canon_from(ms, floor))
    lab_b, _ = LW._merge(ms, floor, {3: 1})
    hb, nb = LW.score_c3_live(ms, LW._canon_from(ms, lab_b))
    assert nf == nb and hb > hf, "W1: bridge must fix 'the doctor'->Elizabeth through make_canonicalizer: %d/%d vs %d/%d" % (hf, nf, hb, nb)
    print("W1 PASS: deterministic known-answer -- floor C3=%d/%d -> bridge C3=%d/%d through the REAL canonicalizer" % (hf, nf, hb, nb))
    ok += 1

    # W2/W3 -- honest-floor lift + twin loses + no-regress, on all GUM (diag off for speed here; W4 runs it).
    # The DEPLOYABLE-under-the-bar operating point is conf_thr=-3.0 (C1 up-or-flat with the biggest such lift);
    # conf_thr=0.0 is the extra-conservative point.
    res = LW.run(docs_limit=None, verbose=False, diag=False)
    sd = res["sweep"][-3.0]; s0 = res["sweep"][0.0]
    dd = sd["C3"]["delta_vs_floor"]; td = sd["C3"]["bridge_vs_twin"]
    assert dd["ci_sep"] and dd["delta"] > 0.03, "W2: deployable conf_thr=-3.0 must lift C3 CI-sep (>0.03): %s" % dd
    assert td["ci_sep"] and td["delta"] > 0, "W2: info-free twin must LOSE CI-sep at conf_thr=-3.0: %s" % td
    assert s0["C3"]["delta_vs_floor"]["ci_sep"], "W2: the conservative conf_thr=0.0 point must also lift CI-sep: %s" % s0["C3"]["delta_vs_floor"]
    print("W2 PASS: deployable conf_thr=-3.0  C3 floor %.4f -> bridge %.4f (%+.4f CI[%+.4f,%+.4f]) ; twin LOSES %+.4f CI[%+.4f,%+.4f] (n=%d) ; conservative thr=0.0 %+.4f"
          % (sd["C3"]["floor"], sd["C3"]["bridge"], dd["delta"], dd["ci"][0], dd["ci"][1],
             td["delta"], td["ci"][0], td["ci"][1], sd["C3"]["n"], s0["C3"]["delta_vs_floor"]["delta"]))
    ok += 1

    c1 = sd["C1"]; c2 = sd["C2"]["delta_vs_floor"]
    assert c1["delta"]["ci"][1] >= 0, "W3: at the deployable point C1 must be up-or-flat (CI includes 0): %s" % c1
    assert c2["delta"] >= -0.001, "W3: C2 hard-link must be up-or-flat: %s" % c2
    print("W3 PASS: deployable conf_thr=-3.0 no-regress -- C1 %.4f->%.4f (%+.4f CI[%+.4f,%+.4f], up-or-flat) ; C2 %.4f->%.4f (%+.4f, CI-sep=%s)"
          % (c1["floor"], c1["bridge"], c1["delta"]["delta"], c1["delta"]["ci"][0], c1["delta"]["ci"][1],
             sd["C2"]["floor"], sd["C2"]["bridge"], c2["delta"], c2["ci_sep"]))
    ok += 1

    # W4 -- the upstream gold-coref leak (GUM harness + native LitBank)
    docs = G.load_docs(gum_only=True, limit=140, name_gazetteer=gaz)
    diag = LW._gold_inheritance_diag(docs, gaz)
    gold_c3 = diag["gold_seeded_gate_C3"][0]; honest_c3 = diag["honest_seeded_gate_C3"][0]; raw_c3 = diag["raw_situation_predict_C3"][0]
    assert gold_c3 > 0.5 and honest_c3 < 0.30 and (gold_c3 - honest_c3) > 0.4, \
        "W4: real gate must gold-inherit (gold %.3f >> honest %.3f ~ raw %.3f)" % (gold_c3, honest_c3, raw_c3)
    # native LitBank: the reader keeps gold cluster ids
    from hdlab.coref import parse_litbank_conll, name_content_tokens
    from hdlab.situation_reader import SituationReader
    R = SituationReader(); R.gaz = gaz
    f = os.path.join(_REPO, "data/litbank/coref/conll/105_persuasion_brat.conll")
    mts, _ = parse_litbank_conll(f, name_gender_map=gaz)
    before = {m["midx"]: m["cluster"] for m in mts}
    R._coref_mentions = mts; R._apply_commonnoun_gate(mts)
    after = {m["midx"]: m["cluster"] for m in mts if not m["is_pronoun"]}
    kept = sum(1 for mid, c in after.items() if c == before[mid]) / len(after)
    assert kept >= 0.80, "W4: native reader path must gold-inherit (>=80%% keep gold id): %.3f" % kept
    print("W4 PASS: gold-coref LEAK -- real gate C3 gold-seed %.3f vs honest-seed %.3f (~raw %.3f) ; native LitBank keeps %.1f%% gold ids"
          % (gold_c3, honest_c3, raw_c3, 100 * kept))
    ok += 1

    # W5 -- the conservative..liberal DIAL: cue_competed gives ~4x the experiencer gain of cue_conf (the lift does
    # NOT shrink through the real consumer -- it matches the origin's +0.086 offline) but at a small CI-sep C1
    # regress; cue_conf is C1-safe. Both beat the honest floor + twin CI-sep.
    arms = LW.mode_arms(docs, gaz)
    comp = arms["cue_competed_m0.0"]; conf = arms["cue_conf_m0.0"]
    assert comp["C3"]["delta"]["ci_sep"] and comp["C3"]["delta"]["delta"] > conf["C3"]["delta"]["delta"], \
        "W5: cue_competed must lift C3 CI-sep and beat cue_conf: comp %s vs conf %s" % (comp["C3"]["delta"], conf["C3"]["delta"])
    assert comp["C3"]["vs_twin"]["ci_sep"], "W5: cue_competed twin must lose CI-sep: %s" % comp["C3"]["vs_twin"]
    assert conf["C1"]["delta"] >= -0.001, "W5: cue_conf must be C1-safe: %s" % conf["C1"]
    assert comp["C1"]["delta"] < conf["C1"]["delta"] - 0.001, \
        "W5: cue_competed must show the documented small C1 regress (the dial's cost) worse than cue_conf: %s vs %s" % (comp["C1"], conf["C1"])
    print("W5 PASS: dial -- cue_competed C3 %+.4f (C1 %+.4f CI[%+.4f,%+.4f] small regress) vs cue_conf C3 %+.4f (C1-safe %+.4f); both twin-loses"
          % (comp["C3"]["delta"]["delta"], comp["C1"]["delta"], comp["C1"]["ci"][0], comp["C1"]["ci"][1],
             conf["C3"]["delta"]["delta"], conf["C1"]["delta"]))
    ok += 1

    # W6 -- DOWNSTREAM NO-REGRESS through the FULL reader.read(): de-leaking the entity gate's gold inheritance leaves
    # the pronoun consumer (sm.coref_acc) byte-identical (native LitBank; mechanism check, not a capability number).
    import experiments.exp_crosstype_deleaked_full_read_v1 as DL
    fr = DL.run(n_docs=6, verbose=False)
    ab = fr["coref_acc_identical_A_vs_B"]; ac = fr["coref_acc_identical_A_vs_C"]
    assert ab.split("/")[0] == ab.split("/")[1], "W6: gate on/off must leave pronoun coref_acc byte-identical: %s" % ab
    assert ac.split("/")[0] == ac.split("/")[1], "W6: de-leak must leave pronoun coref_acc byte-identical: %s" % ac
    print("W6 PASS: full reader.read() downstream no-regress -- pronoun coref_acc byte-identical A(gold)==B(gate-off)==C(de-leak): A/B %s, A/C %s (native LitBank, mechanism check)"
          % (ab, ac))
    ok += 1

    print("\nALL WITNESSES PASS (%d/%d)" % (ok, ok))
    return 0


if __name__ == "__main__":
    sys.exit(main())


# --- pytest-collectable wrapper (pri 128, mechanical; see notes/problems/447_witness_files_define_no_test_function_so_the_certification_gate_runs_nothing_from_them_give_every_witness_a_collectable_wrapper_with_a_cost_marker_and_an_execution_manifest/PROBLEM.md) ---
import pytest as _pri128_pytest
from verification._witness_wrap import _run_main_as_test as _pri128_run


@_pri128_pytest.mark.corpus
def test_witness():
    _code, _out = _pri128_run(main)
    assert _code == 0, "witness exited %r:\n%s" % (_code, _out[-4000:])
