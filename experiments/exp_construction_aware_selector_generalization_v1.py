"""exp_construction_aware_selector_generalization_v1 -- does the NULL generalize across register?

The 19c LitBank finding: a Goldberg construction-aware selector adds EXACTLY ZERO over the live proximity/Competition-
Model selector (hybrid_role_patient), because on canonical English the double-object construction is canonically
ORDERED so word-order and construction give the same role -- the construction cue is REDUNDANT with word order (a
Competition-Model prediction: high-validity cues converge on canonical structures). If that is the brain-faithful
truth, it should hold in MODERN register too (word-order dominance is register-invariant for English). This cell
re-runs the construction-vs-live comparison on the modern QA-SRL population (n=2737) and reports it beside 19c.

Glass-box, NO LLM at inference. ASCII. own dir. hdlab READ-only.
"""
from __future__ import annotations
import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
import argparse, json, sys, time
from datetime import datetime, timezone
import numpy as np

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in (_REPO, os.path.join(_REPO, "experiments")):
    if p not in sys.path:
        sys.path.insert(0, p)
import experiments.exp_verbrole_exemplar_which_arg_v1 as V1
import experiments.exp_19c_composed_cleaned_gold_v1 as CG
import experiments.exp_whodidwhat_ideal_brain_foundational_v1 as IDEAL
from experiments.exp_construction_aware_selector_diagnosis_v1 import (
    GIVE_CLASS, NAMING_CLASS, _bare, live_pick, construction_over, _boot, _null_p95)
from hdlab.pos_tagger import PosTagger
from hdlab.thematic_role_labeler import lemma_verb

OUT_DIR = os.path.join(_REPO, "data/exp_construction_aware_selector_generalization_v1")
POS_ASSET = os.path.join(_REPO, "data/frontend_assets/pos_tagger_ud_ewt_upos.json")


def eval_pop(pop_path, tg, cap=None):
    rows = [r for r in V1.load_pop(pop_path) if r.get("gold_head")]
    clean = [r for r in rows if CG.is_clean_do(r, tg.tag(r["sent"].split()))[0]]
    if cap:
        clean = clean[:cap]
    B, D, Dtwin = [], [], []
    multi_mask, constr_fires = [], []
    twin_rng = np.random.default_rng(20260903)
    for r in clean:
        toks = r["sent"].split(); vi = r["verb_idx"]; gh = r["gold_head"]
        pos = tg.tag(list(toks))
        b = (live_pick(toks, pos, vi) or "")
        d = (construction_over(toks, pos, vi, lambda t, p, v: live_pick(t, p, v) or "") or "")
        dt = (construction_over(toks, pos, vi, lambda t, p, v: live_pick(t, p, v) or "", twin_rng=twin_rng) or "")
        B.append(int(b == gh)); D.append(int(d == gh)); Dtwin.append(int(dt == gh))
        bare = _bare(toks, pos, vi)
        multi_mask.append(len(bare) >= 2)
        v = lemma_verb(toks[vi])
        constr_fires.append(len(bare) >= 2 and (v in GIVE_CLASS or v in NAMING_CLASS))
    B = np.array(B); D = np.array(D); Dtwin = np.array(Dtwin)
    mm = np.array(multi_mask, bool); cf = np.array(constr_fires, bool)
    return {
        "n": len(clean), "n_multi_do": int(mm.sum()), "n_constr_fires": int(cf.sum()),
        "acc_B_LIVE": round(float(B.mean()), 4), "acc_D_constr": round(float(D.mean()), 4),
        "acc_D_twin": round(float(Dtwin.mean()), 4),
        "acc_B_LIVE_multi": round(float(B[mm].mean()), 4) if mm.sum() else None,
        "acc_D_constr_multi": round(float(D[mm].mean()), 4) if mm.sum() else None,
        "D_vs_B_ALL": _boot(D, B),
        "D_vs_B_MULTI": _boot(D[mm], B[mm]) if mm.sum() else None,
        "D_vs_B_null_p95": _null_p95(D, B),
    }


def run(smoke=False):
    t0 = time.time(); os.makedirs(OUT_DIR, exist_ok=True)
    tg = PosTagger.load(POS_ASSET)
    cap = 150 if smoke else None
    res = {"MODERN_qasrl": eval_pop(V1.QA, tg, cap=cap),
           "C19_litbank": eval_pop(IDEAL.LB, tg, cap=cap)}
    with open(os.path.join(OUT_DIR, "metrics.json"), "w", encoding="ascii") as fh:
        json.dump({"anchor_name": "construction_aware_selector_generalization_v1", "results": res,
                   "elapsed_s": round(time.time() - t0, 1), "ts_iso": datetime.now(timezone.utc).isoformat()}, fh, indent=2)
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true", dest="self_test")
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()
    res = run(smoke=(args.self_test or args.smoke))
    for name in ("MODERN_qasrl", "C19_litbank"):
        s = res[name]
        print("\n===== %s (n=%d; multi-DO=%d; construction-fires=%d) =====" % (name, s["n"], s["n_multi_do"], s["n_constr_fires"]), flush=True)
        print("  B_LIVE %.4f | D_constr %.4f | D_twin %.4f  (multi: B_LIVE %s | D_constr %s)"
              % (s["acc_B_LIVE"], s["acc_D_constr"], s["acc_D_twin"], s["acc_B_LIVE_multi"], s["acc_D_constr_multi"]), flush=True)
        for lbl, k in [("D vs B_LIVE (ALL)", "D_vs_B_ALL"), ("D vs B_LIVE (MULTI)", "D_vs_B_MULTI")]:
            d = s[k]
            if d:
                print("     %-22s d=%+.4f CI[%+.4f,%+.4f] half=%.4f %s"
                      % (lbl, d["delta"], d["ci_lo"], d["ci_hi"], d["half"], "CI-SEP" if d["sep"] else "n.s."), flush=True)
        print("     null p95 = %.4f" % s["D_vs_B_null_p95"], flush=True)
    if args.self_test or args.smoke:
        assert res["MODERN_qasrl"]["n"] >= 50 and res["C19_litbank"]["n"] >= 50
        print("\n[self-test] PASS", flush=True)


if __name__ == "__main__":
    main()
