"""exp_knowledge_factory_signal_loss_drill_v1 -- ISOLATE where targeted meaning-growth loses signal on the
collapsed sense-pairs, and pin it to a PRECISE brain-fidelity divergence.

PROBLEM: build_and_freeze_the_clean_curated_knowledge_foundation_the_proven_meaning_lift (drilling the
targeted-acquisition located negative: the brain DOES learn senses from reading, so our failure is a fidelity gap
to isolate -- is it THIS process, or downstream?).

THE BRAIN'S PIPELINE (PINNED) vs OURS, stage by stage:
  D3 RESOLUTION: brain recomputes a CONTEXTUAL token representation -> confident sense pick even for rare senses.
     OURS: resolve via the FROZEN, COLLAPSED prototype signatures -> tiny margins -> Zipf-starved confident binds.
  D2 BINDING:    brain stores the CONTEXTUALIZED EXEMPLAR (episodic/MINERVA-2). OURS: mean-pool the context WORDS
     into the prototype -> makes it MORE topical.
  D1 REPRESENTATION: brain's sense reps are contextual + distinct. OURS: one static, sense-conflated w2v vector.

THE ISOLATING ABLATION: give acquisition PERFECT (oracle) resolution from SemCor EVEN docs (doc-disjoint from the
ODD test). Then:
  * if oracle-resolved acquisition RAISES the collapsed-pair a_s -> the bottleneck was RESOLUTION (D3, THIS process;
    our propose-and-verify can't resolve collapsed pairs because the signatures are collapsed -- fixable by a better
    representation/reader).
  * if oracle-resolved acquisition is FLAT (even perfect labels + coverage don't separate) -> the loss is DOWNSTREAM
    (D1/D2: mean-pooling static context words onto a static prototype cannot encode the distinction) -> the wall is
    the STATIC REPRESENTATION, and the only brain-foundational fix is the contextual/online predictive reader.
Also reports the frozen RESOLUTION ACCURACY on the collapsed-pair DEV occurrences (the D3 diagnostic) and an
EXEMPLAR (episodic) readout arm (the D2 test).

Strict doc-disjoint SemCor: acquire from EVEN docs (gold), test on ODD subordinate. Reuses the meaning store +
gap-analysis. Glass-box, NO LLM, ASCII.
Run: .venv/Scripts/python.exe experiments/exp_knowledge_factory_signal_loss_drill_v1.py --self-test
"""
from __future__ import annotations

import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "4")

import sys
import json
import time
import argparse
from collections import defaultdict

import numpy as np

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import experiments.exp_consolidation_gate_v1 as G1
import experiments.exp_knowledge_factory_meaning_store_v1 as M
import experiments.exp_knowledge_factory_gap_analysis_v1 as GAP
from hdlab.diagnostic_context_wsd import diagnostic_context_scores, diagnostic_query

OUT_DIR = os.path.join(_REPO, "data", "exp_knowledge_factory_signal_loss_drill_v1")
_ZERO = np.zeros(M.EMB_DIM, np.float32)


def _all_even_odd(recs):
    doc = np.array([r["doc_id"] for r in recs]); sub = np.array([r["subordinate"] for r in recs], bool)
    dev = list(np.where(doc % 2 == 0)[0])                 # EVEN = acquisition (gold), ALL senses
    test = list(np.where((doc % 2 == 1) & sub)[0])        # ODD subordinate = test
    return dev, test


def resolution_accuracy(recs, idxs, sig, mat, w2i):
    """Frozen-signature resolution accuracy on the targeted occurrences (the D3 diagnostic) + mean margin."""
    ok = []; margins = []
    for i in idxs:
        r = recs[i]; tn = r["tn"]
        rows = [G1._unit(mat[w2i[x]]) for x in r["ctx"] if x in w2i]
        if len(rows) < 1:
            continue
        C = np.stack(rows)
        G = np.stack([sig.get(s) if sig.get(s) is not None else _ZERO for s in tn]).astype(np.float64)
        if not np.any(G):
            continue
        sc = diagnostic_context_scores(C, G)
        order = np.argsort(-sc)
        ok.append(int(tn[int(order[0])] == r["gold"]))
        if len(order) > 1:
            margins.append(float(sc[order[0]] - sc[order[1]]))
    return (float(np.mean(ok)) if ok else None, float(np.mean(margins)) if margins else None, len(ok))


def oracle_acquire(recs, dev_idx, targeted_senses):
    """Oracle-resolved acquisition: bind each EVEN-doc occurrence's context words to its GOLD sense."""
    acq = defaultdict(list); inst = defaultdict(list)
    for i in dev_idx:
        r = recs[i]; g = r["gold"]
        if g not in targeted_senses:
            continue
        ctx = [x for x in r["ctx"]]
        acq[g].extend(ctx); inst[g].append(ctx)
    return acq, inst


def grow(prep, frozen, acq, mat, w2i):
    out = dict(frozen)
    for syn, words in acq.items():
        base = (prep["seed_words"].get(syn, list(M.G1._seed_words(syn, w2i))) + prep["assoc"].get(syn, []))
        out[syn] = G1._sigvec(mat, w2i, base + words)
    return out


def a_s(recs, idxs, sig, Ctx):
    return M.a_s(recs, idxs, sig, Ctx)


def bootstrap_acquire(recs, dev_idx, targeted_senses, frozen, prep, mat, w2i, rounds=5, conf_q=0.6,
                      resolver="plain"):
    """The BRAIN-FOUNDATIONAL glass-box fix (cross-situational propose-but-verify; Trueswell 2013): resolve the
    CONFIDENT occurrences first (top-(1-conf_q) margin), bind them to the resolved sense, RE-GROW the signatures,
    and RE-RESOLVE next round with the sharpened signatures. resolver:
      'plain'    = argmax of the diagnostic context scores (drifts to dominant on collapsed signatures).
      'additive' = hdlab.semantic_control.additive_reordered_read: score = log(freq prior) + gamma*reliability*
                   relu(z(context)) -- the dominant is anchored by frequency, context only ADDS to a subordinate
                   (Duffy/Morris/Rayner reordered access; the landed net-gain rule). Should resolve the
                   subordinate occurrences that have STRONG context, without the dominant see-saw."""
    from hdlab.semantic_control import additive_reordered_read
    sig = dict(frozen); hist = []
    for rnd in range(rounds):
        resolved = []; margins = []
        for i in dev_idx:
            r = recs[i]; tn = r["tn"]
            if r["gold"] not in targeted_senses:
                continue
            rows = [G1._unit(mat[w2i[x]]) for x in r["ctx"] if x in w2i]
            if len(rows) < 1:
                continue
            C = np.stack(rows)
            G = np.stack([sig.get(s) if sig.get(s) is not None else _ZERO for s in tn]).astype(np.float64)
            if not np.any(G):
                continue
            sc = diagnostic_context_scores(C, G); order = np.argsort(-sc)
            margin = float(sc[order[0]] - sc[order[1]]) if len(order) > 1 else 1.0
            if resolver == "additive":
                pr = np.asarray(r.get("prior", np.ones(len(tn))), float)
                rel = min(1.0, len(rows) / 8.0)             # non-margin context richness (Feldman-Friston precision)
                pred = tn[additive_reordered_read(pr, sc, reliability=rel)]
            else:
                pred = tn[int(order[0])]
            margins.append(margin); resolved.append((pred, r["ctx"], margin, r["gold"]))
        if not margins:
            break
        thr = float(np.quantile(margins, conf_q))          # admit only the top-(1-conf_q) most-confident
        acq = defaultdict(list); nadm = 0; ncorr = 0
        for pred, ctx, margin, gold in resolved:
            if margin >= thr:
                acq[pred].extend(ctx); nadm += 1; ncorr += int(pred == gold)
        sig = grow(prep, frozen, acq, mat, w2i)             # re-grow from frozen + this round's confident admits
        hist.append({"round": rnd, "n_admitted": nadm, "resolution_acc_admitted": round(ncorr / max(1, nadm), 4)})
    return sig, hist


def a_s_exemplar(recs, idxs, frozen, inst, mat, w2i, Ctx, k=5):
    """EXEMPLAR/episodic readout (D2 test): score a candidate sense by the max mean-cosine of the diagnostic query
    to its top-k stored oracle-acquired instance vectors (fallback to the frozen prototype if no instances)."""
    inst_vecs = {s: [G1._sigvec(mat, w2i, c) for c in cs] for s, cs in inst.items()}
    inst_vecs = {s: np.stack([v for v in vs if v is not None]) for s, vs in inst_vecs.items()
                 if any(v is not None for v in vs)}
    ok = []
    for i in idxs:
        C = Ctx[i]
        if C is None:
            continue
        r = recs[i]; tn = r["tn"]
        Gp = np.stack([frozen.get(s) if frozen.get(s) is not None else _ZERO for s in tn]).astype(np.float64)
        if not np.any(Gp):
            continue
        q = diagnostic_query(C, Gp)
        sc = []
        for s in tn:
            if s in inst_vecs:
                sims = inst_vecs[s] @ q
                kk = min(k, len(sims)); sc.append(float(np.sort(sims)[-kk:].mean()))
            else:
                fs = frozen.get(s); sc.append(float(fs @ q) if fs is not None else -9.0)
        ok.append(int(tn[int(np.argmax(sc))] == r["gold"]))
    return np.array(ok, float)


def run(smoke=False, cos_thr=0.92, max_lemmas=500):
    t0 = time.time(); os.makedirs(OUT_DIR, exist_ok=True)
    w2i, mat, recs, _dev0, _test0, _ta = M._load_eval()
    dev, test = _all_even_odd(recs)
    if smoke:
        test = test[:1000]; max_lemmas = 60
    cand = set()
    for i in dev + test:
        cand.update(recs[i]["tn"])
    prep = M.prep_bags(cand, mat, w2i, 3)
    frozen = M.sigs_at(prep, mat, w2i, None)

    from experiments.exp_knowledge_factory_targeted_acq_v1 import collapsed_targets
    targets = collapsed_targets(prep, frozen, cos_thr, max_lemmas)
    targeted_senses = set().union(*targets.values()) if targets else set()
    tgt_test = [i for i in test if recs[i]["gold"] in targeted_senses]
    tgt_dev = [i for i in dev if recs[i]["gold"] in targeted_senses]
    print("[drill] targeted senses=%d | dev occ=%d | test items=%d (%.0fs)"
          % (len(targeted_senses), len(tgt_dev), len(tgt_test), time.time() - t0), flush=True)

    # D3 diagnostic: how well does the FROZEN store resolve the collapsed-pair occurrences?
    res_acc, res_margin, res_n = resolution_accuracy(recs, tgt_dev, frozen, mat, w2i)

    # oracle-resolved acquisition from EVEN docs
    acq, inst = oracle_acquire(recs, dev, targeted_senses)
    sig_oracle = grow(prep, frozen, acq, mat, w2i)
    Ctx = G1.precompute_ctx(recs, test, mat, w2i)

    ok_frozen = a_s(recs, tgt_test, frozen, Ctx)
    ok_oracle = a_s(recs, tgt_test, sig_oracle, Ctx)
    ok_exemplar = a_s_exemplar(recs, tgt_test, frozen, inst, mat, w2i, Ctx)
    # BRAIN-FOUNDATIONAL glass-box fixes: cross-situational bootstrap, plain vs additive-reordered resolver
    sig_boot, boot_hist = bootstrap_acquire(recs, dev, targeted_senses, frozen, prep, mat, w2i, resolver="plain")
    ok_boot = a_s(recs, tgt_test, sig_boot, Ctx)
    sig_boot_add, boot_hist_add = bootstrap_acquire(recs, dev, targeted_senses, frozen, prep, mat, w2i,
                                                     resolver="additive")
    ok_boot_add = a_s(recs, tgt_test, sig_boot_add, Ctx)
    n = min(len(ok_frozen), len(ok_oracle), len(ok_exemplar), len(ok_boot), len(ok_boot_add))

    res = {"n_test": int(n), "targeted_senses": len(targeted_senses),
           "D3_resolution": {"frozen_resolution_acc": None if res_acc is None else round(res_acc, 4),
                             "mean_margin": None if res_margin is None else round(res_margin, 4), "n_dev_occ": res_n,
                             "n_chance": round(1.0 / max(2, np.mean([len(recs[i]["tn"]) for i in tgt_dev])), 4)
                             if tgt_dev else None},
           "a_s": {"frozen": round(float(ok_frozen.mean()), 4),
                   "ORACLE_meanpool": round(float(ok_oracle.mean()), 4),
                   "ORACLE_exemplar": round(float(ok_exemplar.mean()), 4),
                   "BOOTSTRAP_plain": round(float(ok_boot.mean()), 4),
                   "BOOTSTRAP_additive": round(float(ok_boot_add.mean()), 4)},
           "ORACLE_vs_frozen": G1._paired(ok_oracle[:n], ok_frozen[:n], 980),
           "EXEMPLAR_vs_frozen": G1._paired(ok_exemplar[:n], ok_frozen[:n], 981),
           "BOOTSTRAP_vs_frozen": G1._paired(ok_boot[:n], ok_frozen[:n], 982),
           "BOOTSTRAP_ADDITIVE_vs_frozen": G1._paired(ok_boot_add[:n], ok_frozen[:n], 983),
           "bootstrap_history_plain": boot_hist,
           "bootstrap_history_additive": boot_hist_add,
           "acquired_words_total": int(sum(len(v) for v in acq.values())),
           "elapsed_s": round(time.time() - t0, 1)}
    oracle_helps = res["ORACLE_vs_frozen"]["delta"] > 0 and res["ORACLE_vs_frozen"]["sep"]
    exemplar_helps = res["EXEMPLAR_vs_frozen"]["delta"] > 0 and res["EXEMPLAR_vs_frozen"]["sep"]
    if oracle_helps or exemplar_helps:
        res["ISOLATION"] = ("LOSS IS RESOLUTION (D3, THIS process): with ORACLE labels the collapsed-pair a_s RISES "
                            "CI-sep -> our propose-and-verify fails only because the FROZEN signatures are too "
                            "collapsed to resolve; a better (contextual) reader recovers it.")
    else:
        res["ISOLATION"] = ("LOSS IS DOWNSTREAM (D1/D2, the STATIC REPRESENTATION): even PERFECT (oracle) resolution "
                            "+ full DEV coverage + exemplar readout do NOT raise the collapsed-pair a_s -> mean-"
                            "pooling static context words onto a static prototype cannot encode the sense "
                            "distinction. The wall is the sense-conflated w2v vector; the only brain-foundational "
                            "fix is a CONTEXTUAL/online predictive reader (the invariant-boundary north star).")
    ba_p = [h["resolution_acc_admitted"] for h in boot_hist]
    ba_a = [h["resolution_acc_admitted"] for h in boot_hist_add]
    res["headline"] = ("SIGNAL-LOSS DRILL: frozen res_acc=%.3f (chance %.3f) | a_s frozen %.4f -> ORACLE %.4f "
                       "(+%.4f sep=%s) | BOOT-plain %.4f (res %s) | BOOT-ADDITIVE %.4f (d=%+.4f sep=%s, res %s) | %s"
                       % (res["D3_resolution"]["frozen_resolution_acc"] or -1, res["D3_resolution"]["n_chance"] or -1,
                          res["a_s"]["frozen"], res["a_s"]["ORACLE_meanpool"], res["ORACLE_vs_frozen"]["delta"],
                          res["ORACLE_vs_frozen"]["sep"], res["a_s"]["BOOTSTRAP_plain"],
                          "->".join("%.2f" % a for a in ba_p), res["a_s"]["BOOTSTRAP_additive"],
                          res["BOOTSTRAP_ADDITIVE_vs_frozen"]["delta"], res["BOOTSTRAP_ADDITIVE_vs_frozen"]["sep"],
                          "->".join("%.2f" % a for a in ba_a), res["ISOLATION"].split(":")[0]))
    with open(os.path.join(OUT_DIR, "metrics_%s.json" % ("smoke" if smoke else "full")), "w",
              encoding="ascii") as f:
        json.dump({"anchor_name": "knowledge_factory_signal_loss_drill_v1", "verdict": "MEASURED", "result": res},
                  f, indent=2, default=str)
    print("[run] " + res["headline"], flush=True)
    print("       ISOLATION: " + res["ISOLATION"], flush=True)
    return res


def self_test():
    # oracle_acquire buckets a targeted gold occurrence's context to its gold sense.
    recs = [{"doc_id": 0, "gold": "bank.n.01", "tn": ["bank.n.01", "bank.n.09"], "ctx": ["river", "water"],
             "subordinate": False}]
    acq, inst = oracle_acquire(recs, [0], {"bank.n.01"})
    assert acq["bank.n.01"] == ["river", "water"] and len(inst["bank.n.01"]) == 1, "oracle buckets to gold: %s" % dict(acq)
    print("SELFTEST PASS (oracle_acquire binds gold occurrence context to its gold sense)", flush=True)
    return True


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--cos-thr", type=float, default=0.92)
    ap.add_argument("--max-lemmas", type=int, default=500)
    ap.add_argument("--timeout", type=float, default=None)
    args = ap.parse_args(argv)
    if args.self_test:
        return 0 if self_test() else 1
    run(smoke=args.smoke, cos_thr=args.cos_thr, max_lemmas=args.max_lemmas)
    return 0


if __name__ == "__main__":
    sys.exit(main())
