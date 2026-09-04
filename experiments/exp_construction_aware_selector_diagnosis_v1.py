"""exp_construction_aware_selector_diagnosis_v1 -- LOCATE the honest gain of a Goldberg construction-aware selector.

THE DISK-OUTRANKS-THE-BRIEF CHECK. The parent prototype (exp_referent_per_np_selection_improvement_v1) measured the
construction fix's +0.146 multi-DO gain OVER `ideal_pick`. But `ideal_pick` has an ANIMACY OVERRIDE that mis-fires on
double-object ditransitives: "pay passengers a penny" -> passengers animate, penny inanimate -> ideal_pick returns
"penny" (the theme), but the who-did-what GOLD is "passengers" (the recipient/obj1). The LIVE reader does NOT use
ideal_pick -- its wired theme selector is hdlab.graded_role_assigner.hybrid_role_patient -> resolve_patient, which on
a canonical clause returns the NEAREST post-verbal NP-head (obj1). So the live selector may ALREADY get double-object
right, and the construction fix's real gain over the LIVE baseline may be located elsewhere (naming/object-complement).

This cell measures, on the SAME cleaned-DO population and the SAME referent-per-NP candidate set, four selectors:
  A) ideal_pick                 -- the prototype's baseline (has the animacy override)
  B) hybrid_role_patient        -- THE LIVE READER's actual wired theme selector (np_head_reduce=True, live default)
  C) construction-over-ideal    -- the prototype's fix (reproduces +0.040 all / +0.146 multi-DO over A)
  D) construction-over-LIVE     -- the fix delegating to B on the non-construction path (the HONEST bar baseline is B)
and breaks the multi-DO gain down by Goldberg construction TYPE (give-class / naming-class / other), so we see exactly
where the live selector is already right and where the construction earns its keep.

Glass-box, NO LLM at inference (GloVe is a static distributional asset, used only for the diagnostic SP arm; the
construction routing itself uses no embeddings). ASCII. own dir. hdlab READ-only.
"""
from __future__ import annotations
import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
import argparse, glob, json, sys, time
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
import experiments.exp_referent_per_np_end_to_end_v1 as E2E
from hdlab.pos_tagger import PosTagger
from hdlab.scene_segment import parse_conll_sentences
from hdlab.thematic_role_labeler import lemma_verb
from hdlab.np_head_reduce import np_head_reduce_pairs
from hdlab.graded_role_assigner import hybrid_role_patient

OUT_DIR = os.path.join(_REPO, "data/exp_construction_aware_selector_diagnosis_v1")
POS_ASSET = os.path.join(_REPO, "data/frontend_assets/pos_tagger_ud_ewt_upos.json")

# Goldberg (1995) argument-structure CONSTRUCTIONS -- byte-identical to the parent prototype's classes.
GIVE_CLASS = frozenset("give pay offer send hand tell ask show bring teach pass lend owe promise serve feed sell "
                       "grant award mail read write sing throw buy get make find leave hand deny refuse wish".split())
NAMING_CLASS = frozenset("call name label dub christen term style appoint elect consider deem declare crown brand "
                         "nickname title pronounce vote".split())


def _bare(toks, pos, vi):
    """The referent-per-NP candidate set reduced to NP heads, restricted to BARE post-verbal direct objects. Byte-
    identical to the prototype's _bare -- the shared multi-DO competition set both selectors choose among."""
    cands = IDEAL.referent_per_np(toks, pos)
    cands = np_head_reduce_pairs(toks, pos, cands) or cands
    return sorted([(h, ix) for h, ix in cands if ix > vi and TC.is_bare_do(toks, pos, vi, ix)], key=lambda x: x[1])


def live_pick(toks, pos, vi):
    """THE LIVE READER's wired theme selector, over the referent-per-NP candidate set. Faithful to
    hdlab.predicate_argument_frontend.route_predicate_arguments, which calls
    hybrid_role_patient(toks, upos, v, cands, np_head_reduce=self.np_head_reduce) with np_head_reduce ON by default.
    Returns the picked patient HEAD string (lowercased) for comparison to gold_head, or None."""
    pairs = IDEAL.referent_per_np(toks, pos)                 # the referent-per-NP candidate set (all content-noun heads)
    if not pairs:
        return None
    cand1 = sorted(ix + 1 for h, ix in pairs)                # 1-based indices for the hdlab selector
    idx1 = hybrid_role_patient(toks, pos, vi + 1, cands=cand1, np_head_reduce=True)
    if idx1 is None or not (1 <= idx1 <= len(toks)):
        return None
    return toks[idx1 - 1].lower()


def construction_over(toks, pos, vi, base_fn, *, use_constr=True, twin_rng=None):
    """Construction-aware routing on multi-DO competition (Goldberg), else delegate to base_fn.
    twin_rng!=None => INFO-FREE TWIN: the construction ROUTE still fires at the same rate on the same multi-DO
    clauses, but which end of the bare-DO list it picks is RANDOMISED (shuffled construction), so the CONSTRUCTION
    SIGNAL is destroyed while the trigger rate is matched."""
    bare = _bare(toks, pos, vi)
    if len(bare) >= 2:
        v = lemma_verb(toks[vi])
        gc, nc = (v in GIVE_CLASS), (v in NAMING_CLASS)
        if use_constr and (gc or nc):
            if twin_rng is not None:
                return bare[twin_rng.integers(0, len(bare))][0]   # shuffled: random bare-DO (matched trigger rate)
            if gc:
                return bare[0][0]                                 # ditransitive double-object: obj1 = recipient
            return bare[-1][0]                                    # naming/object-complement: the complement
    return base_fn(toks, pos, vi)


def _boot(a, b, nboot=3000, seed=13):
    a = np.asarray(a, float); b = np.asarray(b, float); d = a - b
    rg = np.random.default_rng(seed)
    bs = d[rg.integers(0, len(d), size=(nboot, len(d)))].mean(1)
    lo, hi = float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))
    return dict(delta=round(float(d.mean()), 4), ci_lo=round(lo, 4), ci_hi=round(hi, 4),
                half=round((hi - lo) / 2.0, 4), sep=bool(lo > 0))


def _null_p95(a, b, nperm=3000, seed=17):
    """Sign-flip permutation null on the paired difference: p95 of |mean| under random sign flips."""
    d = np.asarray(a, float) - np.asarray(b, float)
    rg = np.random.default_rng(seed)
    flips = rg.choice([-1.0, 1.0], size=(nperm, len(d)))
    null = np.abs((flips * d).mean(1))
    return round(float(np.percentile(null, 95)), 4)


def run(n_docs=None):
    t0 = time.time(); os.makedirs(OUT_DIR, exist_ok=True)
    tg = PosTagger.load(POS_ASSET)
    docs = sorted(glob.glob(os.path.join(_REPO, "data/corpora/litbank_coref_conll/*.conll")))
    if n_docs:
        docs = docs[:n_docs]
    ds = set()
    for d in docs:
        for t in parse_conll_sentences(d):
            ds.add(E2E._norm(t))
    rows = [r for r in V1.load_pop(E2E.LB) if r.get("gold_head") and E2E._norm(r["sent"]) in ds]
    rows = [r for r in rows if CG.is_clean_do(r, tg.tag(r["sent"].split()))[0]]

    A, B, C, D, Dtwin = [], [], [], [], []           # ideal / live / constr-over-ideal / constr-over-live / twin
    multi_mask, ctype = [], []                        # per-clause: multi-DO? and construction type on the bare set
    twin_rng = np.random.default_rng(20260903)
    for r in rows:
        toks = r["sent"].split(); vi = r["verb_idx"]; gh = r["gold_head"]
        pos = tg.tag(list(toks))
        a = (IDEAL.ideal_pick(toks, pos, vi) or "")
        b = (live_pick(toks, pos, vi) or "")
        A.append(int(a == gh)); B.append(int(b == gh))
        C.append(int((construction_over(toks, pos, vi, lambda t, p, v: IDEAL.ideal_pick(t, p, v) or "") or "") == gh))
        D.append(int((construction_over(toks, pos, vi, lambda t, p, v: live_pick(t, p, v) or "") or "") == gh))
        Dtwin.append(int((construction_over(toks, pos, vi, lambda t, p, v: live_pick(t, p, v) or "", twin_rng=twin_rng) or "") == gh))
        bare = _bare(toks, pos, vi)
        multi_mask.append(len(bare) >= 2)
        v = lemma_verb(toks[vi])
        ctype.append("give" if (len(bare) >= 2 and v in GIVE_CLASS) else
                     ("naming" if (len(bare) >= 2 and v in NAMING_CLASS) else
                      ("multi_other" if len(bare) >= 2 else "single")))

    A = np.array(A); B = np.array(B); C = np.array(C); D = np.array(D); Dtwin = np.array(Dtwin)
    mm = np.array(multi_mask, bool); ct = np.array(ctype)
    single = ~mm
    constr_fires = np.array([c in ("give", "naming") for c in ctype], bool)  # where the construction routes

    def _acc(v, mask=None):
        v = v[mask] if mask is not None else v
        return round(float(v.mean()), 4) if len(v) else None

    res = {
        "n": len(rows), "n_multi_do": int(mm.sum()), "n_single_do": int(single.sum()),
        "n_docs": len(docs),
        "ctype_counts": {c: int((ct == c).sum()) for c in ("single", "give", "naming", "multi_other")},
        "acc_ALL": {"A_ideal": _acc(A), "B_LIVE_hybrid": _acc(B),
                    "C_constr_over_ideal": _acc(C), "D_constr_over_LIVE": _acc(D),
                    "D_twin_shuffled_constr": _acc(Dtwin)},
        "acc_MULTI_DO": {"A_ideal": _acc(A, mm), "B_LIVE_hybrid": _acc(B, mm),
                         "C_constr_over_ideal": _acc(C, mm), "D_constr_over_LIVE": _acc(D, mm),
                         "D_twin_shuffled_constr": _acc(Dtwin, mm)},
        "acc_SINGLE_DO_no_regression": {"B_LIVE_hybrid": _acc(B, single), "D_constr_over_LIVE": _acc(D, single)},
        "acc_by_ctype_LIVE_vs_constr": {
            c: {"n": int((ct == c).sum()), "B_LIVE": _acc(B, ct == c), "D_constr": _acc(D, ct == c)}
            for c in ("give", "naming", "multi_other")},
        # THE HONEST BAR: construction over the LIVE selector, CI-separated?
        "D_vs_B_LIVE_ALL": _boot(D, B),
        "D_vs_B_LIVE_MULTI": _boot(D[mm], B[mm]) if mm.sum() else None,
        "D_vs_twin_ALL": _boot(D, Dtwin),
        "D_vs_twin_MULTI": _boot(D[mm], Dtwin[mm]) if mm.sum() else None,
        "D_vs_B_null_p95_ALL": _null_p95(D, B),
        "no_regression_single_DO_D_minus_B": _boot(D[single], B[single]) if single.sum() else None,
        # reproduce the prototype for the record
        "C_vs_A_ideal_ALL": _boot(C, A),
        "C_vs_A_ideal_MULTI": _boot(C[mm], A[mm]) if mm.sum() else None,
    }
    with open(os.path.join(OUT_DIR, "metrics.json"), "w", encoding="ascii") as fh:
        json.dump({"anchor_name": "construction_aware_selector_diagnosis_v1", "results": res,
                   "scored_population_verbs": sorted({lemma_verb(r["sent"].split()[r["verb_idx"]]) for r in rows}),
                   "elapsed_s": round(time.time() - t0, 1), "ts_iso": datetime.now(timezone.utc).isoformat()}, fh, indent=2)
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true", dest="self_test")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--docs", type=int, default=None)
    args = ap.parse_args()
    res = run(n_docs=(10 if (args.self_test or args.smoke) else args.docs))
    aa, am, asg = res["acc_ALL"], res["acc_MULTI_DO"], res["acc_SINGLE_DO_no_regression"]
    print("\n===== CONSTRUCTION-AWARE SELECTOR DIAGNOSIS (cleaned-DO n=%d; multi-DO n=%d; single-DO n=%d) ====="
          % (res["n"], res["n_multi_do"], res["n_single_do"]), flush=True)
    print("  ctype counts:", res["ctype_counts"], flush=True)
    print("  ALL      : A_ideal %.4f | B_LIVE %.4f | C_constr/ideal %.4f | D_constr/LIVE %.4f | D_twin %.4f"
          % (aa["A_ideal"], aa["B_LIVE_hybrid"], aa["C_constr_over_ideal"], aa["D_constr_over_LIVE"], aa["D_twin_shuffled_constr"]), flush=True)
    print("  MULTI-DO : A_ideal %.4f | B_LIVE %.4f | C_constr/ideal %.4f | D_constr/LIVE %.4f | D_twin %.4f"
          % (am["A_ideal"], am["B_LIVE_hybrid"], am["C_constr_over_ideal"], am["D_constr_over_LIVE"], am["D_twin_shuffled_constr"]), flush=True)
    print("  SINGLE-DO (no-regression): B_LIVE %.4f | D_constr/LIVE %.4f" % (asg["B_LIVE_hybrid"], asg["D_constr_over_LIVE"]), flush=True)
    print("  by construction type (LIVE vs +constr):", flush=True)
    for c, d in res["acc_by_ctype_LIVE_vs_constr"].items():
        print("     %-12s n=%-3d  B_LIVE=%s  D_constr=%s" % (c, d["n"], d["B_LIVE"], d["D_constr"]), flush=True)
    print("  --- THE HONEST BAR: construction OVER THE LIVE selector ---", flush=True)
    for name, key in [("D vs B_LIVE (ALL)", "D_vs_B_LIVE_ALL"), ("D vs B_LIVE (MULTI-DO)", "D_vs_B_LIVE_MULTI"),
                      ("D vs shuffled-constr twin (ALL)", "D_vs_twin_ALL"),
                      ("D vs shuffled-constr twin (MULTI)", "D_vs_twin_MULTI"),
                      ("no-regression single-DO (D-B)", "no_regression_single_DO_D_minus_B"),
                      ("[record] C vs A_ideal (ALL)", "C_vs_A_ideal_ALL"),
                      ("[record] C vs A_ideal (MULTI)", "C_vs_A_ideal_MULTI")]:
        d = res[key]
        if d is None:
            continue
        print("     %-38s d=%+.4f CI[%+.4f,%+.4f] half=%.4f %s"
              % (name, d["delta"], d["ci_lo"], d["ci_hi"], d["half"], "CI-SEP" if d["sep"] else "n.s."), flush=True)
    print("     D vs B null p95 (ALL) = %.4f" % res["D_vs_B_null_p95_ALL"], flush=True)
    if args.self_test or args.smoke:
        assert res["n"] >= 20
        print("\n[self-test] PASS", flush=True)


if __name__ == "__main__":
    main()
