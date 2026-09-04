"""exp_construction_aware_selector_residual_v1 -- the REAL problem underneath the brief, diagnosed on the FULL
cleaned-DO population.

The diagnosis cell (exp_construction_aware_selector_diagnosis_v1) established, on n=149, that a Goldberg
construction-aware selector adds EXACTLY ZERO over the LIVE reader's wired theme selector (hybrid_role_patient):
the live nearest-post-verbal NP-head rule already picks obj1=recipient on the double-object construction (its
who-did-what gold patient), so the construction cue is REDUNDANT with word-order on canonical English multi-DO
(Competition Model cue convergence). This cell (1) confirms that null on the FULL cleaned-DO population (n=669, ~4.5x
the power), where give/naming clauses are more numerous; (2) DUMPS + CATEGORIZES the live selector's actual residual
errors so the REAL remaining mechanism is named; (3) checks the faithfulness of the selector-level measurement against
the stored deployed picks (wired_pick / pos_pick).

Glass-box, NO LLM at inference. ASCII. own dir. hdlab READ-only.
"""
from __future__ import annotations
import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
import argparse, json, sys, time
from collections import Counter
from datetime import datetime, timezone
import numpy as np

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in (_REPO, os.path.join(_REPO, "experiments")):
    if p not in sys.path:
        sys.path.insert(0, p)
import experiments.exp_verbrole_exemplar_which_arg_v1 as V1
import experiments.exp_19c_composed_cleaned_gold_v1 as CG
import experiments.exp_whodidwhat_ideal_brain_foundational_v1 as IDEAL
import experiments.exp_whodidwhat_coverage_transitivity_control_v1 as TC
from experiments.exp_construction_aware_selector_diagnosis_v1 import (
    GIVE_CLASS, NAMING_CLASS, _bare, live_pick, construction_over, _boot, _null_p95)
from hdlab.pos_tagger import PosTagger
from hdlab.thematic_role_labeler import lemma_verb

OUT_DIR = os.path.join(_REPO, "data/exp_construction_aware_selector_residual_v1")
POS_ASSET = os.path.join(_REPO, "data/frontend_assets/pos_tagger_ud_ewt_upos.json")


def _categorize_error(toks, pos, vi, gh, pick):
    """Name the MECHANISM of a live-selector error. Returns a short category string."""
    refnp = IDEAL.referent_per_np(toks, pos)
    heads_present = [h for h, ix in refnp]
    bare = _bare(toks, pos, vi)
    bare_heads = [h for h, ix in bare]
    if gh not in heads_present:
        return "gold_not_a_refnp_candidate"           # POS/coverage: gold head not opened as a referent
    if gh not in bare_heads:
        # gold is a candidate but NOT a bare post-verbal DO of this verb -> preverbal / oblique / cross-clause
        gis = [ix for h, ix in refnp if h == gh]
        if any(ix < vi for ix in gis):
            return "gold_preverbal_noncanonical"       # fronted/passive subject etc.
        return "gold_not_bare_post_DO"                 # oblique / prep-governed / different clause
    # gold IS a bare post-verbal DO
    if len(bare) >= 2:
        return "multi_DO_competition"                  # >=2 bare DOs, picked the wrong one
    return "single_DO_head_or_other"                   # only one bare DO yet still wrong (NP-head / tagger)


def run(smoke=False):
    t0 = time.time(); os.makedirs(OUT_DIR, exist_ok=True)
    tg = PosTagger.load(POS_ASSET)
    rows = [r for r in V1.load_pop(IDEAL.LB) if r.get("gold_head")]
    clean = [r for r in rows if CG.is_clean_do(r, tg.tag(r["sent"].split()))[0]]
    if smoke:
        clean = clean[:120]

    A, B, D, Dtwin = [], [], [], []       # ideal / LIVE / constr-over-live / twin
    Bwired, Bpos = [], []                 # stored deployed picks (end-to-end)
    multi_mask, ctype = [], []
    errors = []
    twin_rng = np.random.default_rng(20260903)
    for r in clean:
        toks = r["sent"].split(); vi = r["verb_idx"]; gh = r["gold_head"]
        pos = tg.tag(list(toks))
        a = (IDEAL.ideal_pick(toks, pos, vi) or "")
        b = (live_pick(toks, pos, vi) or "")
        d = (construction_over(toks, pos, vi, lambda t, p, v: live_pick(t, p, v) or "") or "")
        dt = (construction_over(toks, pos, vi, lambda t, p, v: live_pick(t, p, v) or "", twin_rng=twin_rng) or "")
        A.append(int(a == gh)); B.append(int(b == gh)); D.append(int(d == gh)); Dtwin.append(int(dt == gh))
        Bwired.append(int((r.get("wired_pick") or "") == gh)); Bpos.append(int((r.get("pos_pick") or "") == gh))
        bare = _bare(toks, pos, vi)
        multi_mask.append(len(bare) >= 2)
        v = lemma_verb(toks[vi])
        ctype.append("give" if (len(bare) >= 2 and v in GIVE_CLASS) else
                     ("naming" if (len(bare) >= 2 and v in NAMING_CLASS) else
                      ("multi_other" if len(bare) >= 2 else "single")))
        if b != gh:
            cat = _categorize_error(toks, pos, vi, gh, b)
            errors.append({"cat": cat, "verb": v, "gold": gh, "live_pick": b,
                           "sent": r["sent"][:160]})

    A = np.array(A); B = np.array(B); D = np.array(D); Dtwin = np.array(Dtwin)
    Bwired = np.array(Bwired); Bpos = np.array(Bpos)
    mm = np.array(multi_mask, bool); single = ~mm; ct = np.array(ctype)
    err_cats = Counter(e["cat"] for e in errors)

    def _acc(v, mask=None):
        v = v[mask] if mask is not None else v
        return round(float(v.mean()), 4) if len(v) else None

    res = {
        "n": len(clean), "n_multi_do": int(mm.sum()), "n_single_do": int(single.sum()),
        "ctype_counts": {c: int((ct == c).sum()) for c in ("single", "give", "naming", "multi_other")},
        "acc_ALL": {"A_ideal": _acc(A), "B_LIVE_selector": _acc(B), "D_constr_over_LIVE": _acc(D),
                    "D_twin": _acc(Dtwin), "deployed_wired_pick": _acc(Bwired), "deployed_pos_pick": _acc(Bpos)},
        "acc_MULTI_DO": {"A_ideal": _acc(A, mm), "B_LIVE_selector": _acc(B, mm),
                         "D_constr_over_LIVE": _acc(D, mm), "D_twin": _acc(Dtwin, mm)},
        "acc_SINGLE_DO": {"B_LIVE_selector": _acc(B, single), "D_constr_over_LIVE": _acc(D, single)},
        "acc_by_ctype": {c: {"n": int((ct == c).sum()), "B_LIVE": _acc(B, ct == c), "D_constr": _acc(D, ct == c)}
                         for c in ("give", "naming", "multi_other")},
        # THE HONEST BAR
        "D_vs_B_LIVE_ALL": _boot(D, B),
        "D_vs_B_LIVE_MULTI": _boot(D[mm], B[mm]) if mm.sum() else None,
        "D_vs_B_null_p95_ALL": _null_p95(D, B),
        "no_regression_single_DO": _boot(D[single], B[single]) if single.sum() else None,
        # residual mechanism breakdown (of the LIVE selector's errors)
        "n_errors_LIVE": int((B == 0).sum()),
        "residual_categories": dict(err_cats.most_common()),
        "residual_multi_do_frac": round(float(err_cats.get("multi_DO_competition", 0) / max(1, (B == 0).sum())), 4),
        "example_errors": errors[:50],
    }
    with open(os.path.join(OUT_DIR, "metrics.json"), "w", encoding="ascii") as fh:
        json.dump({"anchor_name": "construction_aware_selector_residual_v1", "results": res,
                   "elapsed_s": round(time.time() - t0, 1), "ts_iso": datetime.now(timezone.utc).isoformat()}, fh, indent=2)
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true", dest="self_test")
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()
    res = run(smoke=(args.self_test or args.smoke))
    a = res["acc_ALL"]; am = res["acc_MULTI_DO"]; asg = res["acc_SINGLE_DO"]
    print("\n===== RESIDUAL DIAGNOSIS (FULL cleaned-DO n=%d; multi-DO n=%d; single-DO n=%d) ====="
          % (res["n"], res["n_multi_do"], res["n_single_do"]), flush=True)
    print("  ctype counts:", res["ctype_counts"], flush=True)
    print("  ALL      : A_ideal %.4f | B_LIVE_selector %.4f | D_constr/LIVE %.4f | D_twin %.4f || deployed wired %.4f / pos %.4f"
          % (a["A_ideal"], a["B_LIVE_selector"], a["D_constr_over_LIVE"], a["D_twin"], a["deployed_wired_pick"], a["deployed_pos_pick"]), flush=True)
    print("  MULTI-DO : A_ideal %.4f | B_LIVE %.4f | D_constr/LIVE %.4f | D_twin %.4f"
          % (am["A_ideal"], am["B_LIVE_selector"], am["D_constr_over_LIVE"], am["D_twin"]), flush=True)
    print("  SINGLE-DO: B_LIVE %.4f | D_constr/LIVE %.4f" % (asg["B_LIVE_selector"], asg["D_constr_over_LIVE"]), flush=True)
    print("  by ctype :", flush=True)
    for c, d in res["acc_by_ctype"].items():
        print("     %-12s n=%-3d B_LIVE=%s D_constr=%s" % (c, d["n"], d["B_LIVE"], d["D_constr"]), flush=True)
    print("  --- HONEST BAR: construction OVER LIVE selector ---", flush=True)
    for name, key in [("D vs B_LIVE (ALL)", "D_vs_B_LIVE_ALL"), ("D vs B_LIVE (MULTI)", "D_vs_B_LIVE_MULTI"),
                      ("no-regression single-DO", "no_regression_single_DO")]:
        d = res[key]
        if d:
            print("     %-28s d=%+.4f CI[%+.4f,%+.4f] half=%.4f %s"
                  % (name, d["delta"], d["ci_lo"], d["ci_hi"], d["half"], "CI-SEP" if d["sep"] else "n.s."), flush=True)
    print("     D vs B null p95 = %.4f" % res["D_vs_B_null_p95_ALL"], flush=True)
    print("  --- THE REAL RESIDUAL (LIVE selector errors n=%d) ---" % res["n_errors_LIVE"], flush=True)
    for cat, k in res["residual_categories"].items():
        print("     %-28s %d" % (cat, k), flush=True)
    print("  multi-DO frac of residual = %.3f (brief claimed 0.84 -- that was over ideal_pick)" % res["residual_multi_do_frac"], flush=True)
    if args.self_test or args.smoke:
        assert res["n"] >= 100
        print("\n[self-test] PASS", flush=True)


if __name__ == "__main__":
    main()
