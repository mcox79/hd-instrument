"""Scaffold-free witness for the_extraction_front_end_parser_is_the_cross_task_bottleneck.
Reproduces the headline WITHOUT re-running any landed cell in place (writes nothing to landed dirs):
  W1 arc-eager UAS on UD-EWT test > live richfeat UAS (the parser IS improved).
  W2 who-did-what: improved parser (arc-eager heads + LABEL-FREE roles) beats the live baseline
     (richfeat + arc_labeler LABELED = 0.515) CI-separated on QA-SRL science FULL.
  W3 the arc_labeler is HARMFUL: LABEL-FREE roles on the SAME frontend heads beat LABELED CI-separated.
  W4 info-free control: shuffled-head twin LOSES to the improved parser CI-separated.
  W5 19c robustness: on LitBank the improved parser beats the baseline (no 19c regression -- a gain).
  W6 N7: arc-eager attach-confidence / graded entropy predicts who-did-what errors (AUC>0.6); shuffle twin ~0.5.
  W7 argument-attach precision: arc-eager object-attach + subject-attach > live richfeat on UD-EWT.
Run: .venv/Scripts/python.exe verification/test_parser_improved_operator.py
"""
import os, sys
_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in (_REPO, os.path.join(_REPO, "experiments")):
    if p not in sys.path:
        sys.path.insert(0, p)
import numpy as np
import experiments.exp_verbrole_exemplar_which_arg_v1 as V1
import experiments.exp_parser_gap_decomp_v1 as GD
import experiments.exp_arceager_parser_operator_v1 as AEO
import experiments.exp_parser_multiobjective_v1 as MO
from hdlab.pos_tagger import PosTagger
from hdlab.arc_parser import ArcParser

FE = os.path.join(_REPO, "data", "frontend_assets")
FAILS = []


def check(name, cond, detail=""):
    print(("[PASS] " if cond else "[FAIL] ") + name + ("  " + detail if detail else ""), flush=True)
    if not cond:
        FAILS.append(name)


def main():
    tg = PosTagger.load(os.path.join(FE, "pos_tagger_ud_ewt_upos.json"))
    W = AEO.load_model(AEO.MODEL_PATH)

    # W1 UAS
    test = [s for s in AEO._load_ud_feats("test") if 1 <= len(s) <= AEO.MAXLEN]
    ae_uas = AEO.uas_on(test, W)
    rich = ArcParser.load(os.path.join(FE, "arc_parser_richfeat_ud_ewt.npz"))
    ru, _, _ = rich.eval_uas([[(i, w, p, h, d) for (i, w, p, h, d, n) in s] for s in test])
    check("W1 arc-eager UAS > richfeat UAS", ae_uas > ru + 0.01, "arc-eager=%.4f richfeat=%.4f" % (ae_uas, ru))

    # who-did-what arms on QA FULL
    rows = V1.load_pop(V1.QA); sents = sorted({r["sent"] for r in rows})
    fe = GD.frontend_parses(sents)
    ae, aeconf = MO.arceager_parses(sents, W, tg)
    ae_sh, _ = MO.arceager_parses(sents, W, tg, shuffle=True, seed=7)
    def nonrev(r): return sum(1 for h, _ in GD.cands(r) if GD.anim(h)) < 2
    FULL = [r for r in rows if len(GD.cands(r)) >= 2 and nonrev(r)]
    base = lambda r: GD.pick_labeled(r, fe)
    felf = lambda r: GD.pick_labelfree(r, fe)
    aelf = lambda r: GD.pick_labelfree(r, ae)
    twin = lambda r: GD.pick_labelfree(r, ae_sh)
    acc = lambda fn, S: sum(1 for r in S if fn(r) == r["gold_head"]) / len(S)

    d_ae_base = V1.paired_delta(FULL, aelf, base, 2000)
    check("W2 improved > baseline (QA FULL) CI-sep", d_ae_base["ci_lo"] > 0,
          "d=%+.4f CI[%+.4f,%+.4f] (AE=%.4f base=%.4f)" % (d_ae_base["delta"], d_ae_base["ci_lo"], d_ae_base["ci_hi"], acc(aelf, FULL), acc(base, FULL)))
    d_lab = V1.paired_delta(FULL, felf, base, 2000)
    check("W3 label-free > labeled (labeler harmful) CI-sep", d_lab["ci_lo"] > 0,
          "d=%+.4f CI[%+.4f,%+.4f]" % (d_lab["delta"], d_lab["ci_lo"], d_lab["ci_hi"]))
    d_twin = V1.paired_delta(FULL, aelf, twin, 2000)
    check("W4 improved > shuffled-head twin CI-sep", d_twin["ci_lo"] > 0,
          "d=%+.4f CI[%+.4f,%+.4f]" % (d_twin["delta"], d_twin["ci_lo"], d_twin["ci_hi"]))

    # W5 19c
    lrows = V1.load_pop(V1.LB); lsents = sorted({r["sent"] for r in lrows})
    lfe = GD.frontend_parses(lsents); lae, _ = MO.arceager_parses(lsents, W, tg)
    lFULL = [r for r in lrows if len(GD.cands(r)) >= 2 and nonrev(r)]
    lbase = lambda r: GD.pick_labeled(r, lfe); laelf = lambda r: GD.pick_labelfree(r, lae)
    d_19c = V1.paired_delta(lFULL, laelf, lbase, 2000)
    check("W5 19c improved > baseline CI-sep (no regression, a gain)", d_19c["ci_lo"] > 0,
          "d=%+.4f CI[%+.4f,%+.4f]" % (d_19c["delta"], d_19c["ci_lo"], d_19c["ci_hi"]))

    # W6 N7
    err = []; ent = []; shuf = []
    rng = np.random.default_rng(3)
    for r in FULL:
        pick = aelf(r); err.append(int(pick != r["gold_head"]))
        cmap = aeconf.get(r["sent"], {}).get(V1._lem(r["verb"]), {})
        C = GD.cands(r); vi = r["verb_idx"]
        from hdlab import graded_competition as GC
        gp = GC.graded_pick({"pos": [1.0 if idx > vi else 0.0 for h, idx in C],
                             "att": [cmap.get(V1._lem(h), cmap.get(h, 0.0)) for h, idx in C]}, {"pos": 1.0, "att": 2.0})
        ent.append(gp["entropy"]); shuf.append(float(rng.random()))
    auc_ent = MO._auc(ent, err); auc_shuf = MO._auc(shuf, err)
    check("W6 N7 entropy predicts errors AUC>0.6 & twin~0.5", auc_ent > 0.6 and abs(auc_shuf - 0.5) < 0.06,
          "entropy_auc=%.4f shuffle_auc=%.4f" % (auc_ent, auc_shuf))

    # W7 argument-attach precision (obj + subj) arc-eager > richfeat
    def obj_subj_acc(head_fn):
        oc = ot = sc = st = 0
        for s in test:
            heads = head_fn(s); n = len(s)
            for (i, w, p, h, dl, num) in s:
                rb = dl.split(":", 1)[0]
                if h < 1 or h > n: continue
                if rb == "obj": oc += int(heads.get(i, -1) == h); ot += 1
                elif rb == "nsubj": sc += int(heads.get(i, -1) == h); st += 1
        return oc / ot, sc / st
    ae_o, ae_s = obj_subj_acc(lambda s: AEO.parse_with_conf([w for (_i, w, _p, _h, _d, _n) in s], [p for (_i, _w, p, _h, _d, _n) in s], W)[0])
    ri_o, ri_s = obj_subj_acc(lambda s: rich.parse([w for (_i, w, _p, _h, _d, _n) in s], [p for (_i, _w, p, _h, _d, _n) in s]).heads)
    check("W7 arg-attach precision arc-eager > richfeat (obj & subj)", ae_o > ri_o and ae_s > ri_s,
          "obj %.4f>%.4f subj %.4f>%.4f" % (ae_o, ri_o, ae_s, ri_s))

    # W8 calibrated abstain/drop signal (spec behavior #5: expose drops, don't confabulate)
    import experiments.exp_arceager_calibrated_abstain_v1 as CA
    dev = [s for s in AEO._load_ud_feats("dev") if 1 <= len(s) <= AEO.MAXLEN]
    md, cd, okd = CA.collect(dev, W); mt, ct, okt = CA.collect(test, W)
    par = CA.platt_fit(md, okd.astype(float)); pcal = CA.platt_apply(mt, par)
    ece_raw = CA.ece(ct, okt); ece_cal = CA.ece(pcal, okt)
    order = np.argsort(pcal); k = int(round(0.2 * len(pcal)))
    err_drop = 1.0 - okt[order[:k]].mean(); err_keep = 1.0 - okt[order[k:]].mean()
    conc = err_drop / max(1e-9, err_keep)
    check("W8 calibrated abstain: ECE improves & drops concentrate errors >2x", ece_cal < ece_raw and conc > 2.0,
          "ECE %.3f->%.3f  drop-err %.3f vs keep %.3f (%.1fx)" % (ece_raw, ece_cal, err_drop, err_keep, conc))

    print("\n%d/%d checks passed" % (8 - len(FAILS), 8), flush=True)
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
