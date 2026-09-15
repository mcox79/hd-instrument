"""Scaffold-free witness for reason_over_the_spatial_relational_model_containment_position_path_modern_gold.

Recomputes every headline from SOURCE (the loaders + the glass-box reasoner library + the experiment cells'
scoring functions) -- it does NOT re-run a landed cell in place and writes nothing. Deterministic.

  W0  gold corpora present (SpaceEval train/trial docs load with relations)
  W1  reasoner SANITY: transitive containment, converse+transitive position, nested-frame inheritance, vacate-source
  W2  CONTAINMENT (gold relations): reasoner beats last-mention CI-separated; reasoner==1.0; twin collapses
  W3  CONTAINMENT multi-fact subset: last-mention at/below chance while reasoner is perfect
  W4  region-ablation (two-level is_in_region) cannot do arbitrary containment (< reasoner)
  W5  PATH/TRANSFER (gold moves): reasoner beats last-mention CI-separated; vacate-source works
  W6  EXTRACTION WALL (located negative): containment recall low and multi-hop chain survival near zero
  W7  POSITION end-to-end (SpartQA): reasoner beats last-mention (CI-separated) and the twin loses

Run: .venv/Scripts/python.exe verification/test_spatial_relational_reasoning.py
"""
from __future__ import annotations
import os, sys
import numpy as np
_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from experiments.spatial_relational_model import SpatialModel
from experiments.spatial_gold_loaders import load_spaceeval_docs, load_spartqa_human
from experiments.exp_spatial_reasoner_gold_relations_v1 import (
    build_containment_items, score_containment, build_path_items, score_path, summarize, boot_margin)
from experiments.exp_spatial_position_qa_v1 import score_corpus as score_position
from experiments.exp_spatial_extraction_recall_v1 import compute as recall_compute
from experiments.exp_spatial_position_gold_v1 import (
    load_spartqa_gold_relations, build_position_items, score as score_posgold, summarize as summ_pos)

PASS = []


def check(name, cond, detail=""):
    PASS.append(bool(cond))
    print(("  PASS " if cond else "  FAIL ") + name + ("  :: " + detail if detail else ""))


def main():
    print("witness: spatial relational reasoning\n")

    # -- W0 gold present --
    train = load_spaceeval_docs("train")
    trial = load_spaceeval_docs("trial")
    ncontain = sum(1 for d in train for (f, g, r) in d["qslinks"] if r in ("IN", "NTPP", "TPP"))
    check("W0 gold corpora present", len(train) >= 50 and ncontain > 300,
          "train docs=%d, gold containment edges=%d" % (len(train), ncontain))

    # -- W1 reasoner sanity --
    m = SpatialModel(); m.add_containment("key", "box"); m.add_containment("box", "drawer")
    s1 = m.contains_path("key", "drawer") and not m.contains_path("drawer", "key")
    m2 = SpatialModel(); m2.add_position("lamp", "left", "sofa"); m2.add_position("sofa", "left", "door")
    s2 = (m2.relative("lamp", "left", "door") is True) and (m2.relative("door", "right", "lamp") is True)
    m3 = SpatialModel()
    m3.add_containment("cup", "left box"); m3.add_containment("pen", "right box")
    m3.add_position("left box", "left", "right box")
    s3 = (m3.relative("cup", "left", "pen") is True)          # nested-frame inheritance
    m4 = SpatialModel(); m4.add_move("she", "kitchen", "garden", 0)
    s4 = (m4.where_after("she") == "garden") and (m4.still_at("she", "kitchen") is False) \
        and (m4.still_at("she", "garden") is True)
    check("W1 reasoner sanity (contain/position/inherit/vacate)", s1 and s2 and s3 and s4,
          "contain=%s pos=%s inherit=%s vacate=%s" % (s1, s2, s3, s4))

    # -- W2/W3/W4 containment on gold relations (train) --
    c_items = build_containment_items(train, seed=0)
    c_arms, c_meta = score_containment(train, c_items, seed=0)
    c_res = summarize("containment", c_arms, c_meta)
    mrg = c_res["margin_reasoner_minus_lastmention"]
    check("W2 containment reasoner beats last-mention CI-separated",
          mrg["sep"] and c_res["reasoner"][0] >= 0.99 and c_res["lastmention"][0] < 0.99 and c_res["twin"][0] < 0.7,
          "reasoner=%.3f last=%.3f twin=%.3f margin=%.3f CI[%.3f,%.3f]" %
          (c_res["reasoner"][0], c_res["lastmention"][0], c_res["twin"][0], mrg["margin"], mrg["lo"], mrg["hi"]))
    multi = c_res["by_subset"].get("multi", {})
    check("W3 multi-fact: last-mention at/below chance, reasoner perfect",
          multi.get("reasoner", [0])[0] >= 0.99 and multi.get("lastmention", [1])[0] <= 0.6,
          "reasoner=%.3f last-mention=%.3f (n=%d)" %
          (multi.get("reasoner", [0])[0], multi.get("lastmention", [0])[0], multi.get("n", 0)))
    check("W4 two-level region ablation cannot do arbitrary containment",
          c_res["region"][0] < c_res["reasoner"][0], "region=%.3f < reasoner=%.3f" %
          (c_res["region"][0], c_res["reasoner"][0]))

    # -- W5 path/transfer on gold moves (train) --
    p_items = build_path_items(train)
    p_arms, p_meta = score_path(train, p_items, seed=0)
    p_res = summarize("path", p_arms, p_meta)
    pm = p_res["margin_reasoner_minus_lastmention"]
    check("W5 path/transfer reasoner beats last-mention CI-separated (vacate-source)",
          pm["sep"] and p_res["reasoner"][0] >= 0.99 and p_res["lastmention"][0] <= 0.6,
          "reasoner=%.3f last=%.3f margin=%.3f CI[%.3f,%.3f] n=%d" %
          (p_res["reasoner"][0], p_res["lastmention"][0], pm["margin"], pm["lo"], pm["hi"], p_res["n"]))

    # -- W6 extraction wall (located negative) --
    rec = recall_compute("train")
    cr = rec["containment"]["recall"]; chain = rec["multihop_chains"]["survival_rate"]
    check("W6 extraction wall: low containment recall + near-zero chain survival",
          cr is not None and cr < 0.35 and (chain is None or chain < 0.15),
          "containment recall=%.3f, multi-hop chain survival=%s" % (cr, chain))

    # -- W7 relative POSITION on gold relations (SpartQA gold): reasoner beats last-mention CI-separated --
    gdocs = load_spartqa_gold_relations("test")
    gitems = build_position_items(gdocs, seed=0)
    garms, gmeta = score_posgold(gdocs, gitems, seed=0)
    gres = summ_pos(garms, gmeta)
    gm = gres["margin_reasoner_minus_lastmention"]
    gmulti = gres["by_subset"].get("multi", {})
    check("W7 position (gold): reasoner beats last-mention CI-separated; multi-fact near chance; twin collapses",
          gm["sep"] and gres["reasoner"][0] >= 0.99 and gres["twin"][0] < 0.5
          and gmulti.get("lastmention", [1])[0] <= 0.65,
          "reasoner=%.3f last=%.3f twin=%.3f margin=%.3f CI[%.3f,%.3f] | multi last-mention=%.3f (n=%d)" %
          (gres["reasoner"][0], gres["lastmention"][0], gres["twin"][0], gm["margin"], gm["lo"], gm["hi"],
           gmulti.get("lastmention", [0])[0], gmulti.get("n", 0)))

    # -- W8 end-to-end EXTRACTION (SpartQA): the info-free twin LOSES (extracted relations load-bearing),
    #    coverage-limited -- the honest end-to-end (reasoner uses the relations; extraction caps coverage) --
    sp = load_spartqa_human("test", q_types=("YN",))

    def spg(it):
        a = it["answer"]
        return (str(a[0]).strip().lower() == "yes") if (isinstance(a, list) and a and
                str(a[0]).strip().lower() in ("yes", "no")) else None
    sp_res, _ = score_position(sp, spg, lambda it: "all", seed=0)
    sptw = sp_res["margin_reasoner_minus_twin"]
    splm = sp_res["margin_reasoner_minus_lastmention"]
    check("W8 end-to-end (SpartQA): reasoner beats last-mention AND the twin CI-separated (composition holds over "
          "the reader's OWN extraction; coverage-limited)",
          splm["sep"] and sptw["sep"] and sp_res["twin"][0] < sp_res["lastmention"][0] < sp_res["reasoner"][0]
          and sp_res["coverage_reasoner"] < 0.5,
          "reasoner=%.3f last=%.3f twin=%.3f cov=%.3f | vs-last CI[%.3f,%.3f] vs-twin CI[%.3f,%.3f]" %
          (sp_res["reasoner"][0], sp_res["lastmention"][0], sp_res["twin"][0], sp_res["coverage_reasoner"],
           splm["lo"], splm["hi"], sptw["lo"], sptw["hi"]))

    # -- W9 reasoner-completeness upgrades: consistency, principled indeterminacy, quantifier --
    con = SpatialModel(); con.add_containment("box", "drawer"); con.add_containment("drawer", "box")  # cycle
    ok = SpatialModel(); ok.add_containment("cup", "box"); ok.add_containment("pen", "box")
    ind = SpatialModel(); ind.add_position("lamp", "left", "sofa"); ind.add_position("desk", "left", "chair")
    quant = SpatialModel()
    for c in ("red square", "blue square"):
        quant.add_containment(c, "box")
    quant.add_containment("green square", "drawer")
    c_cycle = (con.is_consistent() is False) and (ok.is_consistent() is True)
    c_ind = (ind.relative_status("lamp", "left", "chair") == "indeterminate") and \
            (ind.relative_status("lamp", "left", "zzz") == "unknown") and \
            (ind.relative_status("lamp", "left", "sofa") == "yes")
    c_quant = (quant.all_rel("square", "in", "box") is False) and \
              (quant.exists_rel("in", "box", "square") is True)
    check("W9 completeness: consistency (cycle), principled indeterminate-vs-unknown, quantifier all/exists",
          c_cycle and c_ind and c_quant,
          "cycle=%s indeterminacy=%s quantifier=%s" % (c_cycle, c_ind, c_quant))

    # -- W10 commonsense gap-filler (prototype): glass-box ConceptNet fill beats the shuffled-CN control --
    from experiments.exp_spatial_commonsense_gapfill_v1 import evaluate as gf_eval, load_atlocation
    import numpy as _np
    loc, pool = load_atlocation()
    p_real, plus_real, added_real, gn, _, _ = gf_eval(loc)
    _rng = _np.random.default_rng(0)
    shuf = {t: set(pool[i] for i in _rng.integers(0, len(pool), size=len(loc[t]))) for t in loc}
    _, plus_shuf, added_shuf, _, _, _ = gf_eval(shuf)
    gm = boot_margin(plus_real, plus_shuf)
    check("W10 commonsense gap-filler (glass-box, NO LLM): real-KB fill beats shuffled-KB control CI-separated",
          gm["sep"] and added_real > added_shuf,
          "+CN=%.3f shuffled=%.3f added(real/shuf)=%d/%d margin CI[%.3f,%.3f]" %
          (plus_real.mean(), plus_shuf.mean(), added_real, added_shuf, gm["lo"], gm["hi"]))

    n_pass = sum(PASS)
    print("\n%d/%d witnesses PASS" % (n_pass, len(PASS)))
    sys.exit(0 if n_pass == len(PASS) else 1)


if __name__ == "__main__":
    main()


# --- pytest-collectable wrapper (pri 128, mechanical; see notes/problems/447_witness_files_define_no_test_function_so_the_certification_gate_runs_nothing_from_them_give_every_witness_a_collectable_wrapper_with_a_cost_marker_and_an_execution_manifest/PROBLEM.md) ---
import pytest as _pri128_pytest
from verification._witness_wrap import _run_main_as_test as _pri128_run


@_pri128_pytest.mark.fast
def test_witness():
    _code, _out = _pri128_run(main)
    assert _code == 0, "witness exited %r:\n%s" % (_code, _out[-4000:])
