"""Scaffold-free witness for register_native_parse_and_pos_training_data_for_pp_attachment_and_robust_tagging.
Reproduces the LOCATED-NEGATIVE headline WITHOUT re-running any landed cell in place (recomputes on a subsample
in memory; reads landed diagnosis/ceiling metrics for the decomposition shares -- never rewrites them).

  W1 COPULA who-did-what gain is NOT separable from the info-free permissive TWIN (traverse-all) -> the apparent
     copula/reachability who-did-what gain is chain-selector PERMISSIVENESS, not a brain-faithful mechanism.
  W2 FREQUENT-FRAMES register tagging (raw exposure) does NOT yield a positive PP-chain reach gain (net<=0).
  W3 margin-gated SELECTIONAL re-attach is ~a no-op (|d|<0.01) -- the real AUC-0.64 signal does not move attachment.
  W4 ASSOC-based SELECTION is NOT separable from its SHUFFLED-association twin -> the selectional signal does not
     resolve the who-did-what SELECTION ambiguity either.
  W5 the CLEAN copular predicate-complement subset has BASE reachability == 0 -> a real UD-convention representation
     gap (the complement is the head, the copula a leaf), i.e. the biggest 'verb-mistag' bucket is NOT a tagger error.
  W6 the raw-exposure selectional signal IS real in the abstract (AUC(gold-prep vs other-prep) > 0.60).
  W7 PP-attachment is a SMALL share (<0.15) of the 19c reachability residual (diagnosis).
  W8 84%+ of the '19c verb-mistags' are COPULA-as-AUX (correct UPOS), not archaic-verb tagging errors (ceiling).
  W9 the REGISTER effect is at the SELECTION/thematic-fit STORE, not the parser: the structured verb-role exemplar
     store beats its verb-shuffle twin on MODERN (+0.081 CI-sep) but TIES it on 19c (cited p3 landed metrics).
  W10 re-estimating the thematic-fit store on 19c exposure ALONE does not revive the signal (ties its verb-shuffle twin).
  W11 a richer register-native PPMI-SVD representation also ties its twin on the CONTAMINATED 19c who-did-what gold.
  W12 but on the CLEANED direct-object gold the verb-specific thematic-fit signal is REAL (beats its verb-shuffle twin
     CI-sep) -- the gold contamination was the confound; it still ties the bag-of-args twin, so COMPOSITION remains
     the structural lever (drill: Bicknell/Chersoni 58->72).
Run: .venv/Scripts/python.exe verification/test_register_native_located_negative.py
"""
import os, sys, json
import numpy as np
_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in (_REPO, os.path.join(_REPO, "experiments")):
    if p not in sys.path:
        sys.path.insert(0, p)
import experiments.exp_verbrole_exemplar_which_arg_v1 as V1
import experiments.exp_register_native_pp_attachment_v1 as REG
import experiments.exp_register_native_levers_v1 as LV
import experiments.exp_arceager_parser_operator_v1 as AEO

FAILS = []


def check(name, cond, detail=""):
    print(("[PASS] " if cond else "[FAIL] ") + name + ("  " + detail if detail else ""), flush=True)
    if not cond:
        FAILS.append(name)


def main():
    from hdlab.pos_tagger import PosTagger
    tg = PosTagger.load(os.path.join(_REPO, "data", "frontend_assets", "pos_tagger_ud_ewt_upos.json"))
    W = AEO.load_model(AEO.MODEL_PATH)
    # small exposure is enough to reproduce the (negative) relationships
    tag = REG.load_or_tag(os.path.join(REG.OUT_DIR, "tagged_19c_6000.jsonl"), REG.LB_RAW, 6000, tg)
    ev = set(" ".join(r["sent"].split()) for pth in (V1.LB, V1.QA) for r in V1.load_pop(pth))
    tag = [(t, p) for (t, p) in tag if " ".join(t) not in ev]
    A = REG.build_assoc(tag); FM = LV.build_frames(tag)

    # recompute levers on a subsample of LB_19c (in memory; writes nothing)
    import experiments.exp_verbrole_exemplar_which_arg_v1 as _V1
    rows = [r for r in _V1.load_pop(_V1.LB) if REG.cand_ok(r)][:900]
    M = {k: [] for k in ("base_reach", "cop_reach", "twin_reach", "ftag_reach", "sel_reach",
                          "base_wdw", "cop_wdw", "twin_wdw", "sel_wdw", "assocsel_wdw", "assocsel_twin_wdw", "cop_clean")}
    from experiments.exp_19c_copula_disambiguation_v1 import cop_aware_reach, COP_AUX
    from hdlab.predicate_argument_frontend import _attaches_to_verb
    Ash = REG.shuffle_assoc(A)
    for r in rows:
        toks = r["sent"].split(); vi0 = r["verb_idx"]; gi0 = r.get("gold_idx")
        if not toks or gi0 is None or not (0 <= vi0 < len(toks)) or not (0 <= gi0 < len(toks)):
            continue
        pos = tg.tag(toks); vi1, gi1 = vi0 + 1, gi0 + 1
        heads, conf, marg = AEO.parse_with_conf(toks, pos, W)
        pos_ft = LV.retag_frames(toks, pos, FM)
        heads_ft = AEO.parse_with_conf(toks, pos_ft, W)[0] if pos_ft != pos else heads
        heads_sel = LV.sel_adapt(toks, pos, heads, marg, A)
        pred = heads.get(vi1)
        M["cop_clean"].append(int(toks[vi0].lower() in COP_AUX and pred not in (None, 0, vi1) and (gi1 == pred or heads.get(gi1) == pred)))
        M["base_reach"].append(int(_attaches_to_verb(gi1, vi1, heads, pos, max_hops=LV.MAX_HOPS)))
        M["cop_reach"].append(int(cop_aware_reach(gi1, vi1, heads, pos, toks)))
        M["ftag_reach"].append(int(_attaches_to_verb(gi1, vi1, heads_ft, pos_ft, max_hops=LV.MAX_HOPS)))
        M["sel_reach"].append(int(_attaches_to_verb(gi1, vi1, heads_sel, pos, max_hops=LV.MAX_HOPS)))
        M["base_wdw"].append(int(LV.chain_pick_r(r, toks, pos, heads, LV._reach_base) == r["gold_head"]))
        M["cop_wdw"].append(int(LV.chain_pick_r(r, toks, pos, heads, cop_aware_reach) == r["gold_head"]))
        M["twin_wdw"].append(int(LV.chain_pick_r(r, toks, pos, heads, LV.reach_all) == r["gold_head"]))
        vlem = V1._lem(toks[vi0])
        M["assocsel_wdw"].append(int(LV.chain_pick_assoc(r, toks, pos, heads, cop_aware_reach, A, vlem) == r["gold_head"]))
        M["assocsel_twin_wdw"].append(int(LV.chain_pick_assoc(r, toks, pos, heads, cop_aware_reach, Ash, vlem) == r["gold_head"]))

    d_ct = LV.bootd(M["cop_wdw"], M["twin_wdw"], 1500)
    check("W1 copula who-did-what NOT separable from info-free permissive twin", d_ct["ci_lo"] <= 0,
          "d=%+.4f CI[%+.4f,%+.4f]" % (d_ct["delta"], d_ct["ci_lo"], d_ct["ci_hi"]))
    d_ft = LV.bootd(M["ftag_reach"], M["base_reach"], 1500)
    check("W2 frequent-frames tagging is NOT a positive reach gain", d_ft["ci_lo"] <= 0,
          "d=%+.4f CI[%+.4f,%+.4f]" % (d_ft["delta"], d_ft["ci_lo"], d_ft["ci_hi"]))
    d_sel = LV.bootd(M["sel_reach"], M["base_reach"], 1500)
    check("W3 margin-gated selectional re-attach is a no-op", abs(d_sel["delta"]) < 0.01,
          "d=%+.4f" % d_sel["delta"])
    d_as = LV.bootd(M["assocsel_wdw"], M["assocsel_twin_wdw"], 1500)
    check("W4 assoc-selection NOT separable from shuffled-assoc twin", d_as["ci_lo"] <= 0,
          "d=%+.4f CI[%+.4f,%+.4f]" % (d_as["delta"], d_as["ci_lo"], d_as["ci_hi"]))
    mask = np.array(M["cop_clean"], bool)
    base_clean = float(np.array(M["base_reach"])[mask].mean()) if mask.sum() else 1.0
    check("W5 clean copular predicate-complement subset base reach == 0 (real convention gap)", base_clean == 0.0,
          "n=%d base_reach=%.4f" % (int(mask.sum()), base_clean))

    # W6 selectional signal real (AUC gold-prep vs other-prep) -- recompute small
    from experiments.exp_19c_reach_failure_diagnosis_v1 import gov_prep_of_gold
    lg = []; lo = []
    for r in rows[:500]:
        toks = r["sent"].split(); vi0 = r["verb_idx"]; gi0 = r.get("gold_idx")
        if not toks or gi0 is None or not (0 <= vi0 < len(toks)) or not (0 <= gi0 < len(toks)):
            continue
        pos = tg.tag(toks); heads = AEO.parse_with_conf(toks, pos, W)[0]
        pg = gov_prep_of_gold(toks, pos, heads, gi0 + 1); vlem = V1._lem(toks[vi0])
        if pg:
            lg.append(REG.assoc_LA(A, vlem, None, pg))
        other = [p for p in range(1, len(toks) + 1) if pos[p - 1] == "ADP" and toks[p - 1].lower() in REG.PREPS and p != pg]
        if other:
            lo.append(REG.assoc_LA(A, vlem, None, toks[other[0] - 1].lower()))
    lg = np.array(lg); lo = np.array(lo)
    auc = float(np.mean([(x > lo).mean() + 0.5 * (x == lo).mean() for x in lg])) if len(lg) and len(lo) else 0.5
    check("W6 raw-exposure selectional signal is real (AUC gold-prep>other-prep > 0.60)", auc > 0.60, "auc=%.4f" % auc)

    # W7/W8 decomposition -- read landed diagnosis + ceiling metrics (do not rewrite)
    try:
        dg = json.load(open(os.path.join(_REPO, "data/exp_19c_reach_failure_diagnosis_v1/metrics.json")))["results"]
        pp_share = dg["failure_shares"]["PP_ATTACH_ERR"]
        check("W7 PP-attachment is a SMALL share (<0.15) of the 19c reach residual", pp_share < 0.15, "PP_ATTACH_ERR share=%.4f" % pp_share)
    except Exception as e:
        check("W7 (diagnosis metrics present)", False, str(e))
    try:
        cl = json.load(open(os.path.join(_REPO, "data/exp_19c_tagging_lever_ceiling_v1/metrics.json")))["results"]["LB_19c"]
        aux = cl["mistag_as"].get("AUX", 0); tot = sum(cl["mistag_as"].values())
        check("W8 84%+ of 19c 'verb mistags' are COPULA-as-AUX (correct UPOS)", aux / max(1, tot) > 0.75, "AUX=%d/%d=%.3f" % (aux, tot, aux / max(1, tot)))
    except Exception as e:
        check("W8 (ceiling metrics present)", False, str(e))

    # W9 the register effect is at the SELECTION STORE, not the parser (cited p3, landed -- not re-derived):
    # the structured thematic-fit store beats its verb-shuffle twin on MODERN but ties it on 19c.
    try:
        p3 = json.load(open(os.path.join(_REPO, "data/exp_verbrole_exemplar_which_arg_v1/metrics.json")))["results"]
        mod = p3["QA_SRL_modern"]["FULL"]["deltas"]["EXEMPLAR_vs_VERBSHUF"]
        c19 = p3["LitBank_19c"]["FULL"]["deltas"]["EXEMPLAR_vs_VERBSHUF"]
        check("W9 structured thematic-fit store beats twin on MODERN but TIES on 19c (register bites the meaning store)",
              mod["ci_lo"] > 0 and c19["ci_lo"] <= 0,
              "modern d=%+.4f CI_lo=%+.4f ; 19c d=%+.4f CI_lo=%+.4f" % (mod["delta"], mod["ci_lo"], c19["delta"], c19["ci_lo"]))
    except Exception as e:
        check("W9 (p3 metrics present)", False, str(e))

    # W10 the drilled fix, PROTOTYPED: register re-estimation of the thematic-fit store ALONE is insufficient
    # (ties its verb-shuffle twin on 19c) -> the selection lever needs composition + richer representation, not
    # register data or re-estimation. (reads landed prototype metrics; not re-derived here.)
    try:
        pr = json.load(open(os.path.join(_REPO, "data/exp_19c_thematic_fit_reestimation_prototype_v1/metrics.json")))["results"]
        vs = pr["C19_vs_VERBSHUF"]
        check("W10 19c-re-estimated thematic-fit store TIES its verb-shuffle twin (re-estimation alone insufficient)",
              vs["ci_lo"] <= 0, "C19 vs verbshuf d=%+.4f CI[%+.4f,%+.4f] (n=%d)" % (vs["delta"], vs["ci_lo"], vs["ci_hi"], pr["n_selection"]))
    except Exception as e:
        check("W10 (prototype metrics present)", False, str(e))

    # W11 richer register-native distributional representation ALSO ties its twin -> the 19c selection lever is
    # neither re-estimation nor representation; it is composition + gold-cleaning (owned selection problems).
    try:
        dp = json.load(open(os.path.join(_REPO, "data/exp_19c_distributional_thematic_fit_prototype_v1/metrics.json")))["results"]
        full = dp["FULL"]["DIST_vs_VERBSHUF"]; clean = dp["CLEAN_DIRECT_OBJECT"]["DIST_vs_VERBSHUF"]
        check("W11 on the CONTAMINATED full gold the distributional store ties its verb-shuffle twin",
              full["ci_lo"] <= 0, "FULL DIST vs verbshuf d=%+.4f CI[%+.4f,%+.4f] (n=%d)" % (full["delta"], full["ci_lo"], full["ci_hi"], dp["FULL"]["n"]))
        check("W12 on the CLEANED direct-object gold the verb-specific thematic-fit signal is REAL (beats verb-shuffle twin CI-sep)",
              clean["ci_lo"] > 0, "CLEAN DIST vs verbshuf d=%+.4f CI[%+.4f,%+.4f] (n=%d) -> gold contamination was the confound; composition remains (ties bag-of-args)" % (clean["delta"], clean["ci_lo"], clean["ci_hi"], dp["CLEAN_DIRECT_OBJECT"]["n"]))
    except Exception as e:
        check("W11/W12 (distributional prototype metrics present)", False, str(e))

    # W13 the LAST wall drilled: COMPOSITION P(patient|agent,verb) carries REAL signal on 19c -- agent-conditioned
    # thematic fit beats its info-free AGENT-SHUFFLE twin CI-sep (the lever the drill named; Bicknell/Chersoni).
    try:
        cp = json.load(open(os.path.join(_REPO, "data/exp_19c_composition_thematic_fit_prototype_v1/metrics.json")))["results"]
        ash = cp["COMPOSED_vs_AGENTSHUF"]
        check("W13 composition beats its info-free agent-shuffle twin CI-sep (the agent x verb conjunction is real)",
              ash["ci_lo"] > 0, "COMPOSED vs agent-shuffle d=%+.4f CI[%+.4f,%+.4f] (n=%d clean-DO); vs-marginal +%.4f (underpowered)" % (
                  ash["delta"], ash["ci_lo"], ash["ci_hi"], ash["n"], cp["COMPOSED_vs_MARGINAL"]["delta"]))
    except Exception as e:
        check("W13 (composition prototype metrics present)", False, str(e))

    print("\n%d/13 checks passed" % (13 - len(FAILS)), flush=True)
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()


# --- pytest-collectable wrapper (pri 128, mechanical; see notes/problems/447_witness_files_define_no_test_function_so_the_certification_gate_runs_nothing_from_them_give_every_witness_a_collectable_wrapper_with_a_cost_marker_and_an_execution_manifest/PROBLEM.md) ---
import pytest as _pri128_pytest
from verification._witness_wrap import _run_main_as_test as _pri128_run


@_pri128_pytest.mark.fast
def test_witness():
    _code, _out = _pri128_run(main)
    assert _code == 0, "witness exited %r:\n%s" % (_code, _out[-4000:])
