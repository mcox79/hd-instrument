"""verification/test_generative_situation_sense_selector.py -- scaffold-free witness for
`the_meaning_channel_needs_a_generative_world_knowledge_situation_model_that_predicts_the_specific_sense`.

Recomputes EVERY headline FROM SOURCE on SemCor (30 files, n=17,317), no cached metric trusted. The expensive
cn_syn settling is loaded from the deterministic feature cache if present, else rebuilt from source (spaCy LOCAL).
Bakes in the LEAK-CATCHING controls that reshaped the result (strict disjoint-doc foundation + scramble label).

Run:  .venv/Scripts/python.exe verification/test_generative_situation_sense_selector.py
Exits non-zero if any check fails.
"""
from __future__ import annotations
import os
import sys
from collections import defaultdict

import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

import experiments.exp_generative_situation_sense_selector_v1 as V1
import experiments.exp_generative_situation_sense_selector_v2 as V2
import experiments.exp_incremental_generative_sense_predictor_v1 as GP

RES = []


def check(name, cond, detail=""):
    RES.append((name, bool(cond), detail))
    print("[%s] %s %s" % ("PASS" if cond else "FAIL", name, detail), flush=True)


def _z(a):
    a = np.asarray(a, float); s = a.std()
    return (a - a.mean()) / s if s > 1e-12 else np.zeros(len(a))


def main():
    # W1 -- the BRAIN-FAITHFUL rule (additive access + non-margin precision) behaves correctly, from source.
    it = {"prior": np.array([0.7, 0.2, 0.1]), "pidx": 0, "tn": ["a", "b", "c"], "gold": "b", "_rel": 1.0}
    flat = V2._additive_pick(it, np.array([0.34, 0.33, 0.33]), 1.0, 0.0)
    sharp = V2._additive_pick(it, np.array([0.05, 0.9, 0.05]), 1.0, 0.0)
    lowrel = V2._additive_pick(dict(it, _rel=0.0), np.array([0.05, 0.9, 0.05]), 1.0, 0.0)
    check("W1_additive_rule_no_hard_flip", flat == 0 and sharp == 1 and lowrel == 0,
          "(flat->dominant, sharp+reliable->override, low-reliability->keep dominant)")

    # ---- full SemCor recompute (settled features from source/cache) ----
    items = V2._build(30)
    cfg = dict(role=True, w_role=4.0, w_struct=2.0, w_bag=1.0, w_disc=0.5, expand=True, w_expand=0.5,
               cn=True, wn=True, fn=True, contrastive=True)
    V2._score_items(items, cfg)                       # it['_role'] = static world-knowledge generative signal
    for it in items:
        it["_cn"] = V2._cn_arr(it)
    sub = np.array([it["subordinate"] for it in items], bool)
    mfs = np.array([int(it["tn"][it["pidx"]] in {it["gold"]}) for it in items], int)
    doc = np.array([it["doc_id"] for it in items]); tr = (doc % 2 == 0); te = (doc % 2 == 1)
    rich = np.array([np.log1p(len(GP._feats(it))) for it in items], float)
    rn = float(np.quantile(rich[tr], 0.9))
    for i, it in enumerate(items):
        it["_rel"] = float(np.clip(rich[i] / max(rn, 1e-9), 0.0, 1.0))
    MFS = float(mfs.mean())
    check("W0_corpus_and_floor", len(items) >= 17000 and abs(MFS - 0.6831) < 0.02,
          "n=%d MFS=%.4f (parent 0.6831)" % (len(items), MFS))

    def mkL(itm, keys):
        parts = []
        for k in keys:
            v = itm.get(k); v = np.asarray(v, float) if v is not None else None
            if v is not None and v.size == len(itm["tn"]) and v.max() > 0:
                parts.append(_z(v))
        if not parts:
            return None
        s = sum(parts); e = np.exp(s - s.max()); return e / e.sum()

    def net_heldout(keys, seed, Ls=None):
        if Ls is None:
            Ls = [mkL(it, keys) for it in items]

        def okv(g, tau):
            return np.array([int(it["tn"][V2._additive_pick(it, Ls[i], g, tau)] in {it["gold"]})
                             for i, it in enumerate(items)], int)
        best = None
        for g in [0.25, 0.5, 0.75, 1.0, 1.5]:
            for tau in [0.0, 0.05, 0.1, 0.2]:
                ok = okv(g, tau); tn = ok[tr].mean() - mfs[tr].mean()
                if best is None or tn > best[0]:
                    best = (tn, g, tau, ok)
        _, g, tau, ok = best
        d = V1._paired(ok[te].astype(float), mfs[te].astype(float), seed)
        return d, ok, Ls, (g, tau)

    # W2 -- HEADLINE: precision-weighted additive rule on the leak-free (graph + static world-knowledge) signal
    # NETS over MFS, held-out even/odd, CI-separated (the parent's wall: best net -0.0013 CI-sep BELOW).
    d_cngen, ok_cngen, Ls_cngen, op = net_heldout(["_cn", "_role"], 101)
    check("W2_net_gain_over_MFS_heldout_CIsep", d_cngen["ci"][0] > 0 and d_cngen["delta"] > 0,
          "cn+GEN net_test=%+.4f CI=%s (parent best -0.0013 CI-sep BELOW)" % (d_cngen["delta"], d_cngen["ci"]))

    # W3 -- NO SEE-SAW: the dominant is preserved (additive access never erases a correct common sense).
    dom_acc = float(ok_cngen[te & ~sub].mean())
    check("W3_no_seesaw_dominant_preserved", dom_acc > 0.93,
          "dominant_test=%.4f (MFS dominant=%.4f)" % (dom_acc, float(mfs[te & ~sub].mean())))

    # W4 -- INFO-FREE TWIN loses CI-separated (shuffle the world-knowledge signal within sense-count buckets).
    buckets = defaultdict(list)
    for i, itm in enumerate(items):
        buckets[len(itm["tn"])].append(i)
    rng = np.random.default_rng(71); mp = {}
    for _, idxs in buckets.items():
        perm = list(idxs); rng.shuffle(perm)
        for a, b in zip(idxs, perm):
            mp[a] = b
    g, tau = op
    Ltw = [mkL({"tn": it["tn"], "_cn": it["_cn"], "_role": items[mp[i]]["_role"]}, ["_cn", "_role"])
           for i, it in enumerate(items)]
    ok_tw = np.array([int(it["tn"][V2._additive_pick(it, Ltw[i], g, tau)] in {it["gold"]}) for i, it in enumerate(items)], int)
    dtw = V1._paired(ok_cngen[te].astype(float), ok_tw[te].astype(float), 102)
    check("W4_shuffled_situation_twin_loses_CIsep", dtw["ci"][0] > 0,
          "real vs twin (net) +%.4f CI=%s" % (dtw["delta"], dtw["ci"]))

    # W5 -- LOCATED NEGATIVE on the a_s lever: the LEARNED generative predictor OVERFITS SemCor topics. Under a
    # STRICT train-only foundation it does NOT net-beat MFS (it goes negative), and its a_s collapses. This is
    # the honest number; the leave-one-DOC-out headline (+0.05/0.43) was cross-document leakage.
    nb = GP._train_nb([it for it in items if it["doc_id"] % 2 == 0])
    Lnb = [GP._nb_likelihood(nb, it)[0] for it in items]
    d_nb, ok_nb, _, _ = net_heldout(None, 103, Ls=Lnb)
    a_s_nb = float(np.mean([int(items[i]["tn"][int(np.argmax(Lnb[i]))] in {items[i]["gold"]})
                            for i in range(len(items)) if (te & sub)[i] and Lnb[i] is not None]))
    check("W5_learned_predictor_overfits_strict", d_nb["delta"] < 0 and a_s_nb < 0.25,
          "NB strict-train-only net_test=%+.4f a_s=%.3f (LOO-doc leaked to +0.05/0.43)" % (d_nb["delta"], a_s_nb))

    # W6 -- SCRAMBLE control: NB on shuffled sense labels collapses the (leaky LOO-doc) signal to ~0.
    tri = [it for it in items if it["doc_id"] % 2 == 0]
    golds = [it["gold"] for it in tri]
    perm = np.random.default_rng(0).permutation(len(golds))
    saved = golds[:]
    for k, itm in enumerate(tri):
        itm["gold"] = saved[perm[k]]
    nb_s = GP._train_nb(tri)
    for itm, gg in zip(tri, saved):
        itm["gold"] = gg
    Lsc = [GP._nb_likelihood(nb_s, it)[0] for it in items]
    d_sc, _, _, _ = net_heldout(None, 104, Ls=Lsc)
    check("W6_scramble_control_collapses", abs(d_sc["delta"]) < 0.01,
          "scrambled-label net_test=%+.4f (real signal is label-dependent)" % d_sc["delta"])

    # W7 -- the DECISION RULE is the lever: cn alone through the additive rule already nets CI-sep (parent's
    # gated hard-flip on the same graph signal netted -0.0013). World-knowledge adds a real but small increment.
    d_cn, _, _, _ = net_heldout(["_cn"], 105)
    check("W7_decision_rule_is_the_lever", d_cn["ci"][0] > 0 and d_cngen["delta"] >= d_cn["delta"] - 1e-9,
          "cn-only net_test=%+.4f CI=%s ; cn+GEN %+.4f (WK adds %+.4f)"
          % (d_cn["delta"], d_cn["ci"], d_cngen["delta"], d_cngen["delta"] - d_cn["delta"]))

    npass = sum(1 for _n, ok, _d in RES if ok)
    print("\n%d/%d checks PASS" % (npass, len(RES)), flush=True)
    return 0 if npass == len(RES) else 1


if __name__ == "__main__":
    sys.exit(main())


# --- pytest-collectable wrapper (pri 128, mechanical; see notes/problems/447_witness_files_define_no_test_function_so_the_certification_gate_runs_nothing_from_them_give_every_witness_a_collectable_wrapper_with_a_cost_marker_and_an_execution_manifest/PROBLEM.md) ---
import pytest as _pri128_pytest
from verification._witness_wrap import _run_main_as_test as _pri128_run


@_pri128_pytest.mark.fast
def test_witness():
    _code, _out = _pri128_run(main)
    assert _code == 0, "witness exited %r:\n%s" % (_code, _out[-4000:])
