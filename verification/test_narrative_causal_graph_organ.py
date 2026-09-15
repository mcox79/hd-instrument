"""test_narrative_causal_graph_organ -- SCAFFOLD-FREE witness for narrative_causal_graph_missing_implicit_inference_organ.

Recomputes every headline claim DIRECTLY from MAVEN-ERE source through the organ module (does NOT read any landed
metrics.json). Prints PASS/FAIL per check. Brain-faithful covariation causal-graph organ:
  DETECTION (Griffiths-Tenenbaum causal SUPPORT) -- pinned mechanism; TYPING (Cheng power + KGT hierarchical
  schema) -- our-invention proxy with a linguistic-cue ceiling. Deterministic (seed 20260830). NO external LLM.

Run: .venv/Scripts/python.exe verification/test_narrative_causal_graph_organ.py
"""
from __future__ import annotations

import os
import sys

import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

import experiments._narrative_causal_graph as G  # noqa: E402
from sklearn.linear_model import LogisticRegression  # noqa: E402

SEED = 20260830
_Y = {"ENABLE": 1, "CAUSE": 0}
_n = _p = 0


def check(name, cond, detail=""):
    global _n, _p
    _n += 1
    ok = bool(cond)
    _p += ok
    print("  [%s] %-64s %s" % ("PASS" if ok else "FAIL", name, detail))
    return ok


def _bal(pred, y):
    return float(np.mean([(pred[y == c] == y[y == c]).mean() for c in (0, 1) if (y == c).sum()]))


def _fit(Xtr, ytr, Xva, balanced=True):
    mu, sd = Xtr.mean(0), Xtr.std(0) + 1e-9
    clf = LogisticRegression(max_iter=3000, class_weight="balanced" if balanced else None).fit((Xtr - mu) / sd, ytr)
    return clf.predict((Xva - mu) / sd)


def _boot_sep(pa, pb, y, gen, n_boot=600):
    """Paired balanced-accuracy bootstrap; returns (delta, lo) -- lo>0 => CI-separated above."""
    n = len(y)
    d = np.array([_bal(pa[ix], y[ix]) - _bal(pb[ix], y[ix])
                  for ix in (gen.integers(0, n, n) for _ in range(n_boot))])
    return _bal(pa, y) - _bal(pb, y), float(np.percentile(d, 2.5))


def main():
    print("=" * 90)
    print("WITNESS: narrative causal-graph implicit-inference organ (recomputed from MAVEN-ERE source)")
    print("=" * 90)
    gen = np.random.default_rng(SEED)

    # ---------- load ----------
    rels_tr = G.load_relations(G.TRAIN)
    rels_va = G.load_relations(G.VALID)
    check("MAVEN loads: train>20k, valid>5k causal relations", len(rels_tr) > 20000 and len(rels_va) > 5000,
          "tr=%d va=%d" % (len(rels_tr), len(rels_va)))
    y = np.array([_Y[r["gold"]] for r in rels_va])
    ytr = np.array([_Y[r["gold"]] for r in rels_tr])
    maj_rate = max((y == 0).mean(), (y == 1).mean())
    check("majority class is PRECONDITION/ENABLE, base rate ~0.83", 0.80 < maj_rate < 0.86, "maj=%.4f" % maj_rate)

    model = G.CovariationModel(rels_tr)

    # ---------- causal support is sample-size-aware (Griffiths-Tenenbaum) ----------
    import math
    def synth(k, n, b0=0.075):
        w = np.linspace(0, 1, 257); p = np.clip(b0 + (1 - b0) * w, 1e-9, 1 - 1e-9)
        lg = k * np.log(p) + (n - k) * np.log(1 - p); mm = lg.max()
        return (mm + math.log(np.trapezoid(np.exp(lg - mm), w))) - (k * math.log(b0) + (n - k) * math.log(1 - b0))
    check("causal SUPPORT is sample-size-aware (100/100 >> 1/1 at same rate)", synth(100, 100) > 10 * synth(1, 1),
          "1/1=%.2f 100/100=%.2f" % (synth(1, 1), synth(100, 100)))
    check("causal SUPPORT monotone in rate (5/20 > 0/20)", synth(5, 20) > synth(0, 20))

    # ---------- TYPING: hierarchical arm A ----------
    pA = G.HierarchicalTyper(model, use_cues=False, balanced=True).fit(rels_tr, ytr).predict(rels_va)
    XS_tr = np.array([G.structural_features(r) for r in rels_tr]); XS = np.array([G.structural_features(r) for r in rels_va])
    pS = _fit(XS_tr, ytr, XS)
    balA, balS = _bal(pA, y), _bal(pS, y)
    check("TYPING covariation balanced acc > 0.72 (crushes chance 0.5)", balA > 0.72, "armA_bal=%.3f" % balA)
    dAS, loAS = _boot_sep(pA, pS, y, gen)
    check("TYPING armA beats adjacency/structural floor CI-separated", loAS > 0,
          "delta=%.4f lo=%.4f (struct=%.3f)" % (dAS, loAS, balS))
    # info-free permuted-label twin loses
    ytr_p = ytr.copy(); gen.shuffle(ytr_p)
    pTw = G.HierarchicalTyper(model, use_cues=False, balanced=True).fit(rels_tr, ytr_p).predict(rels_va)
    dAT, loAT = _boot_sep(pA, pTw, y, gen)
    check("TYPING info-free permuted-label twin LOSES (CI-sep)", loAT > 0, "delta=%.4f twin_bal=%.3f" % (dAT, _bal(pTw, y)))

    # ---------- TYPING raw lift over majority >= +0.05 (the bar's stated metric) ----------
    pB_raw = G.HierarchicalTyper(model, use_cues=True, balanced=False).fit(rels_tr, ytr).predict(rels_va)
    maj = np.full_like(y, int(round(y.mean())))
    raw_lift = float((pB_raw == y).mean() - (maj == y).mean())
    check("TYPING raw accuracy lift over majority >= +0.05 (coverage=1.0)", raw_lift >= 0.05, "raw_lift=%.4f" % raw_lift)

    # ---------- brain-faithfulness: cues add only a MARGINAL amount, NOT the dominance K&B predict ----------
    # (implicit relations mostly lack the explicit connectives K&B manipulated -> covariation captures the signal)
    pB = G.HierarchicalTyper(model, use_cues=True, balanced=True).fit(rels_tr, ytr).predict(rels_va)
    dBA, _ = _boot_sep(pB, pA, y, gen)
    check("linguistic cues add only a MARGINAL amount (<0.02), NOT dominance -- an order below covariation's +0.226",
          abs(dBA) < 0.02, "armB-armA delta=%.4f (covariation armA-struct=%.4f)" % (dBA, dAS))

    # ---------- GENERALIZATION: hierarchical schema beats memorised lookup on UNSEEN pairs (KGT) ----------
    seen = set(k for k, v in model.pair_lbl.items() if sum(v.values()) >= model.min_count)
    uns = np.array([1 if (r["cty"], r["ety"]) not in seen else 0 for r in rels_va], dtype=bool)
    lookup = np.array([_Y[model.pair_lbl[(r["cty"], r["ety"])].most_common(1)[0][0]]
                       if (r["cty"], r["ety"]) in seen else int(round(y.mean())) for r in rels_va])
    balA_u, balL_u = _bal(pA[uns], y[uns]), _bal(lookup[uns], y[uns])
    check("GENERALIZATION: schema beats memorised lookup on UNSEEN pairs", balA_u > balL_u + 0.02,
          "hier=%.3f lookup=%.3f (n=%d)" % (balA_u, balL_u, uns.sum()))
    check("memorised type-pair lookup collapses to ~chance on unseen pairs", abs(balL_u - 0.5) < 0.02, "lookup=%.3f" % balL_u)

    # ---------- DETECTION: covariation causal-support beats structural floor CI-separated ----------
    pos_tr, neg_tr = G.load_detection_pairs(G.TRAIN)
    pos_va, neg_va = G.load_detection_pairs(G.VALID)
    dmodel = G.CovariationModel(rels_tr, det_pos=pos_tr, det_neg=neg_tr)
    dva = pos_va + neg_va; dy = np.array([r["is_causal"] for r in dva])
    dtr = pos_tr + neg_tr; dytr = np.array([r["is_causal"] for r in dtr])
    Xc_tr = np.array([dmodel.detection_features(r) for r in dtr]); Xc = np.array([dmodel.detection_features(r) for r in dva])
    Xs_tr = np.array([G.structural_features(r) for r in dtr]); Xs = np.array([G.structural_features(r) for r in dva])
    p_org = _fit(np.hstack([Xc_tr, Xs_tr]), dytr, np.hstack([Xc, Xs]))
    p_str = _fit(Xs_tr, dytr, Xs)
    dOS, loOS = _boot_sep(p_org, p_str, dy, gen)
    check("DETECTION covariation edge-detector beats structural floor CI-separated", loOS > 0,
          "organ=%.3f struct=%.3f delta=%.4f lo=%.4f" % (_bal(p_org, dy), _bal(p_str, dy), dOS, loOS))
    # honest BOUND: on unseen pairs covariation does NOT beat structural (support needs observed contingency)
    seen_d = set(k for k, v in dmodel.det_total.items() if v >= dmodel.min_count)
    du = np.array([1 if (r["cty"], r["ety"]) not in seen_d else 0 for r in dva], dtype=bool)
    check("DETECTION honest BOUND: covariation does NOT beat structural on unseen pairs (no observed contingency)",
          _bal(p_org[du], dy[du]) < _bal(p_str[du], dy[du]),
          "organ_unseen=%.3f struct_unseen=%.3f" % (_bal(p_org[du], dy[du]), _bal(p_str[du], dy[du])))

    # ---------- CROSS-GENRE positive control: verb-lemma covariation carries causal signal WITHIN MAVEN ----------
    # (this is the load-bearing control that makes the cross-genre NEGATIVE interpretable: the representation is
    #  valid, so the failure to transfer to fiction is genuine -- physical-event KB misses mental-intentional
    #  causation -- not a sparsity artifact. Full cross-genre transfer test: exp_narrative_causal_graph_crossgenre_v1.)
    from experiments.exp_narrative_causal_graph_crossgenre_v1 import VerbCovariation, _auc
    vc = VerbCovariation(pos_tr, neg_tr)
    spv = np.array([vc.score(r.get("clem", ""), r.get("elem", "")) for r in pos_va if r.get("clem") and r.get("elem")])
    snv = np.array([vc.score(r.get("clem", ""), r.get("elem", "")) for r in neg_va if r.get("clem") and r.get("elem")])
    pc = _auc(spv, snv)
    check("verb-lemma covariation carries causal signal WITHIN MAVEN (positive control for cross-genre test)",
          pc > 0.55, "within-MAVEN AUC=%.4f" % pc)

    # ---------- MECHANISM BOUNDARY: covariation detects PHYSICAL causation >> INTENTIONAL (drill prediction) ----------
    from experiments.exp_narrative_causal_graph_intentional_split_v1 import classify
    dm = G.CovariationModel(rels_tr, det_pos=pos_tr, det_neg=neg_tr)
    dva2 = pos_va + neg_va
    dy2 = np.array([r["is_causal"] for r in dva2])
    sc = np.array([dm.causal_support(r["cty"], r["ety"]) for r in dva2])
    cc = np.array([classify(r["cty"]) for r in dva2])
    def _aucv(pos_s, neg_s):
        a = np.concatenate([pos_s, neg_s]); rk = a.argsort().argsort().astype(float) + 1
        return float((rk[:len(pos_s)].sum() - len(pos_s) * (len(pos_s) + 1) / 2) / (len(pos_s) * len(neg_s)))
    phm = cc == "PHYSICAL"; inm = cc == "INTENTIONAL"
    auc_phys = _aucv(sc[phm][dy2[phm] == 1], sc[phm][dy2[phm] == 0])
    auc_int = _aucv(sc[inm][dy2[inm] == 1], sc[inm][dy2[inm] == 0])
    check("covariation detects PHYSICAL causation better than INTENTIONAL (drill's structural prediction)",
          auc_phys - auc_int > 0.05, "phys-AUC=%.3f int-AUC=%.3f gap=%+.3f" % (auc_phys, auc_int, auc_phys - auc_int))

    # ---------- ROBUSTNESS: covariation survives a noisy event-typer (20% type noise) ----------
    rng = np.random.default_rng(7)
    types = sorted({r["cty"] for r in rels_tr})
    def corrupt(rels, p, rr):
        out = []
        for r in rels:
            c, e = r["cty"], r["ety"]
            if rr.random() < p: c = types[rr.integers(len(types))]
            if rr.random() < p: e = types[rr.integers(len(types))]
            out.append(dict(r, cty=c, ety=e))
        return out
    trc = corrupt(rels_tr, 0.2, rng); vac = corrupt(rels_va, 0.2, np.random.default_rng(8))
    mc = G.CovariationModel(trc); yc = np.array([_Y[r["gold"]] for r in vac]); ycc = np.array([_Y[r["gold"]] for r in trc])
    pAc = G.HierarchicalTyper(mc, balanced=True).fit(trc, ycc).predict(vac)
    check("ROBUSTNESS: covariation typing survives 20% event-type noise (bal>0.68)", _bal(pAc, yc) > 0.68,
          "armA@noise0.2=%.3f" % _bal(pAc, yc))

    print("-" * 90)
    print("WITNESS: %d/%d checks passed" % (_p, _n))
    print("=" * 90)
    return 0 if _p == _n else 1


if __name__ == "__main__":
    sys.exit(main())


# --- pytest-collectable wrapper (pri 128, mechanical; see notes/problems/447_witness_files_define_no_test_function_so_the_certification_gate_runs_nothing_from_them_give_every_witness_a_collectable_wrapper_with_a_cost_marker_and_an_execution_manifest/PROBLEM.md) ---
import pytest as _pri128_pytest
from verification._witness_wrap import _run_main_as_test as _pri128_run


@_pri128_pytest.mark.fast
def test_witness():
    _code, _out = _pri128_run(main)
    assert _code == 0, "witness exited %r:\n%s" % (_code, _out[-4000:])
