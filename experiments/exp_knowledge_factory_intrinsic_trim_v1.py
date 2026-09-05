"""exp_knowledge_factory_intrinsic_trim_v1 -- the INTRINSIC (unsupervised, no-label) quality transform + anomaly
trim for the meaning store. Brain-faithful: efficient coding / redundancy reduction (Barlow 1961) prunes on the
representation's OWN statistics, no external teacher -- so score the KB, PINPOINT the associates that stick out,
trim the worst tail, and only CONFIRM with the held-out downstream metric.

PROBLEM: build_and_freeze_the_clean_curated_knowledge_foundation_the_proven_meaning_lift

WHY (owner 2026-09-04): "do a transform on the knowledge base and get a score... pinpoint things that stick out
poorly to trim." The held-out a_s is the LABELED criterion; the brain's pruning signal is INTRINSIC. This builds
the intrinsic signal and tests whether a TARGETED anomaly trim (remove only the worst-sticking-out tail) can
shrink/clean the store WITHOUT dropping a_s -- where the blanket schema-margin trim collapsed it (that removed ALL
non-discriminative associates; this removes only outliers).

INTRINSIC SCORES:
  * KB-level: effective rank (participation ratio -> redundancy); between-sense SEPARATION (mean pairwise cosine
    of a lemma's sibling sense signatures -- LOWER = better separated = the unsupervised WSD-quality proxy);
    within-sense coherence.
  * per-associate anomaly: incoherence (1 - cos(word, own sense centroid)) and sibling-confusion
    (max cos(word, sibling sense) - cos(word, own centroid)). High = sticks out.

Strict doc-disjoint SemCor subordinate; DEV=even (tune trim fraction), TEST=odd (report). Reuses the meaning-store
builder + the live hdlab readout. Glass-box, NO external LLM. ASCII.
Run: .venv/Scripts/python.exe experiments/exp_knowledge_factory_intrinsic_trim_v1.py --self-test
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

OUT_DIR = os.path.join(_REPO, "data", "exp_knowledge_factory_intrinsic_trim_v1")


# ---------------------------------------------------------------------------------------------------
# INTRINSIC KB-LEVEL SCORES (a transform -> a number; NO labels)
# ---------------------------------------------------------------------------------------------------
def effective_rank(sig_by_syn):
    """Participation ratio of the signature matrix' singular spectrum = (sum s)^2 / sum(s^2). High = the senses
    span many independent directions (low redundancy); low = collapsing onto each other (over-redundant)."""
    V = np.stack([v for v in sig_by_syn.values() if v is not None]).astype(np.float32)
    s = np.linalg.svd(V, compute_uv=False)
    return float((s.sum() ** 2) / (np.square(s).sum() + 1e-12))


def sense_separation(sig_by_syn):
    """The UNSUPERVISED WSD-quality proxy: for each lemma with >=2 in-store senses, the mean pairwise cosine
    between its sibling sense signatures. LOWER = better separated (bank(river) far from bank(money)). Returns
    mean over lemmas + the count. NO labels used."""
    from nltk.corpus import wordnet as wn
    by_lemma = defaultdict(list)
    for syn in sig_by_syn:
        if sig_by_syn[syn] is None:
            continue
        try:
            s = wn.synset(syn); key = (s.lemmas()[0].name(), s.pos())
        except Exception:
            continue
        by_lemma[key].append(sig_by_syn[syn])
    sims = []
    for key, vs in by_lemma.items():
        if len(vs) < 2:
            continue
        Vv = np.stack(vs).astype(np.float32); Cc = Vv @ Vv.T
        iu = np.triu_indices(len(vs), 1)
        sims.append(float(Cc[iu].mean()))
    return {"mean_sibling_cos": round(float(np.mean(sims)), 4) if sims else None,
            "n_polysemous_lemmas": len(sims)}


def within_coherence(prep, mat, w2i):
    """Mean over synsets of the mean cos(associate word, own sense centroid). High = tight/clean bags."""
    vals = []
    for s in prep["syns"]:
        c = prep["seed_sig"][s]
        if c is None:
            continue
        idx = [w2i[w] for w in prep["assoc"][s] if w in w2i]
        if not idx:
            continue
        V = mat[idx]; V = V / (np.linalg.norm(V, axis=1, keepdims=True) + 1e-9)
        vals.append(float((V @ c).mean()))
    return round(float(np.mean(vals)), 4) if vals else None


# ---------------------------------------------------------------------------------------------------
# PER-ASSOCIATE ANOMALY (pinpoint what sticks out) + TARGETED TAIL TRIM
# ---------------------------------------------------------------------------------------------------
def associate_anomaly(assoc, mat, w2i, sig_self, sib_sigs, mode="confusion"):
    """Per-associate anomaly score (higher = sticks out more). mode:
      'incoherence' = 1 - cos(word, own centroid)      (far from its own sense = likely noise)
      'confusion'   = max cos(word, sibling) - cos(word, own centroid)   (mis-attributed toward a competitor)
      'combo'       = mean of the two (z-normalised)."""
    idx = [w2i[w] for w in assoc if w in w2i]
    words = [w for w in assoc if w in w2i]
    if not idx or sig_self is None:
        return words, np.zeros(len(words))
    V = mat[idx]; V = V / (np.linalg.norm(V, axis=1, keepdims=True) + 1e-9)
    coh = V @ sig_self
    if sib_sigs:
        sib = (V @ np.stack(sib_sigs).T).max(axis=1)
    else:
        sib = np.full(len(words), -1.0)
    if mode == "incoherence":
        a = 1.0 - coh
    elif mode == "confusion":
        a = sib - coh
    else:
        z = lambda x: (x - x.mean()) / (x.std() + 1e-9)
        a = 0.5 * z(1.0 - coh) + 0.5 * z(sib - coh)
    return words, a


def anomaly_trim_sigs(prep, mat, w2i, frac, mode="confusion"):
    """Drop the top-`frac` most-anomalous associates PER SYNSET, rebuild signatures. frac=0 -> keep-all."""
    sig = {}
    for s in prep["syns"]:
        words, a = associate_anomaly(prep["assoc"][s], mat, w2i, prep["seed_sig"][s], prep["sib"][s], mode)
        if frac > 0 and len(words) > 0:
            ncut = int(np.floor(frac * len(words)))
            if ncut > 0:
                keep = np.argsort(a)[:len(words) - ncut]   # keep the LEAST anomalous
                words = [words[i] for i in sorted(keep)]
        sig[s] = G1._sigvec(mat, w2i, prep["seed_words"][s] + words)
    return sig


def run(level=3, smoke=False, mode="confusion",
        fracs=(0.0, 0.05, 0.1, 0.2, 0.3, 0.5), gamma=1.0, topk=None):
    t0 = time.time(); os.makedirs(OUT_DIR, exist_ok=True)
    w2i, mat, recs, dev, test, test_all = M._load_eval()
    if smoke:
        dev = dev[:400]; test = test[:400]; fracs = (0.0, 0.1, 0.3)
    cand = set()
    for i in dev + test:
        cand.update(recs[i]["tn"])
    Ctx_dev = G1.precompute_ctx(recs, dev, mat, w2i)
    Ctx_test = G1.precompute_ctx(recs, test, mat, w2i)
    prep = M.prep_bags(cand, mat, w2i, level)
    prep0 = M.prep_bags(cand, mat, w2i, 0)
    gloss = M.sigs_at(prep0, mat, w2i, None)
    ok_gloss_test = M.a_s(recs, test, gloss, Ctx_test)

    # sweep trim fraction on DEV: measure held-out a_s AND intrinsic sense-separation + size
    sweep = {}
    for f in fracs:
        sig = anomaly_trim_sigs(prep, mat, w2i, f, mode)
        dev_a = float(M.a_s(recs, dev, sig, Ctx_dev, gamma=gamma, topk=topk).mean())
        sep = sense_separation(sig)
        meansz = np.mean([max(0, len(prep["assoc"][s]) - int(np.floor(f * len(prep["assoc"][s]))))
                          for s in list(prep["syns"])[:3000]])
        sweep[f] = {"dev_a_s": round(dev_a, 4), "sibling_cos": sep["mean_sibling_cos"],
                    "mean_assoc": round(float(meansz), 1)}
        print("[trim] frac=%.2f dev_a_s=%.4f sibling_cos=%.4f mean_assoc=%.1f (%.0fs)"
              % (f, dev_a, sep["mean_sibling_cos"] or -1, meansz, time.time() - t0), flush=True)

    # knee: smallest store (largest frac) whose DEV a_s is within 0.005 of the best DEV a_s
    best_dev = max(v["dev_a_s"] for v in sweep.values())
    knee = max([f for f in fracs if sweep[f]["dev_a_s"] >= best_dev - 0.005])
    sig_knee = anomaly_trim_sigs(prep, mat, w2i, knee, mode)
    sig_keepall = anomaly_trim_sigs(prep, mat, w2i, 0.0, mode)

    ok_knee = M.a_s(recs, test, sig_knee, Ctx_test, gamma=gamma, topk=topk)
    ok_keepall = M.a_s(recs, test, sig_keepall, Ctx_test, gamma=gamma, topk=topk)
    n = min(len(ok_knee), len(ok_keepall), len(ok_gloss_test))
    res = {"mode": mode, "level": level, "n_test": int(n), "knee_frac": knee,
           "intrinsic": {"effective_rank_keepall": round(effective_rank(sig_keepall), 2),
                         "within_coherence_keepall": within_coherence(prep, mat, w2i),
                         "sibling_cos_keepall": sweep[0.0]["sibling_cos"],
                         "sibling_cos_knee": sense_separation(sig_knee)["mean_sibling_cos"]},
           "sweep": {str(k): v for k, v in sweep.items()},
           "test_a_s": {"gloss": round(float(ok_gloss_test.mean()), 4),
                        "keepall": round(float(ok_keepall.mean()), 4),
                        "anomaly_trim_knee": round(float(ok_knee.mean()), 4)},
           "knee_vs_keepall": G1._paired(ok_knee[:n], ok_keepall[:n], 953),
           "knee_vs_gloss": G1._paired(ok_knee[:n], ok_gloss_test[:n], 950),
           "elapsed_s": round(time.time() - t0, 1)}
    res["headline"] = ("INTRINSIC ANOMALY TRIM (%s) knee=%.0f%%: test a_s keepall=%.4f -> trim=%.4f (d=%+.4f "
                       "sep=%s) vs gloss +%.4f | sibling_cos %.4f->%.4f (lower=better) | mean_assoc %.1f->%.1f"
                       % (mode, 100 * knee, res["test_a_s"]["keepall"], res["test_a_s"]["anomaly_trim_knee"],
                          res["knee_vs_keepall"]["delta"], res["knee_vs_keepall"]["sep"],
                          res["knee_vs_gloss"]["delta"], sweep[0.0]["sibling_cos"] or -1,
                          res["intrinsic"]["sibling_cos_knee"] or -1, sweep[0.0]["mean_assoc"],
                          sweep[knee]["mean_assoc"]))
    with open(os.path.join(OUT_DIR, "metrics_%s_%s.json" % (mode, "smoke" if smoke else "full")), "w",
              encoding="ascii") as f:
        json.dump({"anchor_name": "knowledge_factory_intrinsic_trim_v1", "verdict": "MEASURED", "result": res},
                  f, indent=2, default=str)
    print("[run] " + res["headline"], flush=True)
    return res


def self_test():
    # anomaly ranks a sibling-aligned associate above a self-aligned one; effective_rank ~ #independent dirs;
    # sense_separation returns a number for a real polysemous lemma.
    rng = np.random.default_rng(0)
    sig_self = M.G1._unit(rng.standard_normal(M.EMB_DIM)); sib = M.G1._unit(rng.standard_normal(M.EMB_DIM))
    mat = np.stack([sig_self, sib]).astype(np.float32); w2i = {"good": 0, "bad": 1}
    words, a = associate_anomaly(["good", "bad"], mat, w2i, sig_self, [sib], mode="confusion")
    assert a[words.index("bad")] > a[words.index("good")], "sibling-aligned associate is more anomalous"
    er = effective_rank({"a": np.array([1., 0, 0]), "b": np.array([0, 1., 0]), "c": np.array([0, 0, 1.])})
    assert 2.9 < er < 3.1, "effective rank of 3 orthonormal vecs ~3: %.3f" % er
    sep = sense_separation({"bank.n.01": sig_self, "bank.n.09": sib})   # real polysemous lemma 'bank'
    assert sep["n_polysemous_lemmas"] == 1 and sep["mean_sibling_cos"] is not None
    print("SELFTEST PASS (anomaly ranks sibling-aligned high; eff_rank=%.2f; sep n=%d)"
          % (er, sep["n_polysemous_lemmas"]), flush=True)
    return True


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--level", type=int, default=3)
    ap.add_argument("--mode", default="confusion", choices=["confusion", "incoherence", "combo"])
    ap.add_argument("--gamma", type=float, default=1.0)
    ap.add_argument("--topk", type=int, default=None)
    ap.add_argument("--timeout", type=float, default=None)
    args = ap.parse_args(argv)
    if args.self_test:
        return 0 if self_test() else 1
    run(level=args.level, smoke=args.smoke, mode=args.mode, gamma=args.gamma, topk=args.topk)
    return 0


if __name__ == "__main__":
    sys.exit(main())
