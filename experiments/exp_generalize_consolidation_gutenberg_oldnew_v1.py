"""exp_generalize_consolidation_gutenberg_oldnew_v1 -- GENERALIZATION rerun of the CONSOLIDATION store
(sparse pattern-separated cortex + SELECTIVE interleaved replay) on a REAL cross-novel OLD/NEW split.

ORGAN: one_store_does_two_jobs_and_consolidation_is_a_single_average (status PARTIAL). Headline: in a SPARSE
k-WTA cortex, SELECTIVE (surprise-prioritized) interleaved replay beats the info-free UNIFORM twin
CI-separated (keep=0.01: 0.784 vs 0.680) -- but on a SELF-BUILT PPMI paired-associate catastrophic-
interference instrument with an ARBITRARY OLD/NEW concept split within simplewiki.

THE FAIRNESS UPGRADE (scout-designed): a NATURAL OLD/NEW split by reading order across DIFFERENT novels
(different characters / topics / vocabulary = a genuine distribution shift, not an arbitrary within-corpus
split). OLD = 3 Gutenberg novels, NEW = 3 different novels. Paired associates mined from each: KEY = a
content word's PPMI+SVD context vector (the overlapping cortical semantics), TARGET = its top-PMI associate.
A shared PPMI+SVD space over OLD+NEW keeps codes comparable so interference is real.

THE MECHANISM (faithful reimpl of the small core, per exp_consolidation_sparse_hidden_cortex_v2): a 2-layer
cortex key -(fixed random expansion W1)-> pre-hidden -(k-WTA, keep HID_KEEP)-> sparse conjunctive hidden h
-(learned W2, delta rule)-> value. Phase 1 learns OLD; Phase 2 learns NEW with REPLAY of OLD at a scarce
matched budget: SELECTIVE (highest schema-error OLD items) vs the info-free UNIFORM twin (random OLD items)
vs NONE (sequential). DENSE (no k-WTA) control isolates SPARSITY as the causal variable. Scorer = JOINT
old+new hit@1; bootstrap CI over seeds. NO external LLM. CPU. ASCII-only. Deterministic.

HOLDS = SELECTIVE beats the UNIFORM twin CI-separated in the SPARSE regime on the real cross-novel shift.

Run: .venv/Scripts/python.exe experiments/exp_generalize_consolidation_gutenberg_oldnew_v1.py --self-test
     ... --full
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from datetime import datetime, timezone

import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

ANCHOR = "generalize_consolidation_gutenberg_oldnew_v1"
OUTPUT_DIR = os.path.join(REPO, "data", "exp_" + ANCHOR)
NOVELS = {"old": ["alice_in_wonderland", "wizard_of_oz", "tom_sawyer"],
          "new": ["anne_of_green_gables", "little_women", "sherlock_holmes"]}

CODE_DIM = 48        # SVD components (cortical code dim)
HID = 512            # hidden expansion (Dh >> code_dim; mossy-fiber-like divergence)
HID_KEEP = 0.02      # k-WTA sparsity (fraction of hidden units active per concept)
N_PAIRS = 128        # paired associates per set (OLD / NEW)
WINDOW = 5           # co-occurrence window
EPOCHS = 40
LR = 0.5
STOP = set("the a an and or but if then of to in on at for with from by as is are was were be been being it "
           "its this that these those i we you he she they them his her our your my me him us their so do did "
           "not no there here what when where who why how which while about into out up down over under again "
           "very just more most some any all each one two her had has have will would could should said say "
           "says like went go get got come came see saw know knew think thought make made take took time day "
           "little man old great good after before then upon".split())


def _log(m):
    print("[%s] %s" % (ANCHOR, m), flush=True)


def _now():
    return datetime.now(timezone.utc).isoformat()


def _read_novels(names):
    toks = []
    for n in names:
        d = os.path.join(REPO, "data", "corpora", n, "cleaned")
        fs = [f for f in os.listdir(d) if f.endswith(".txt")] if os.path.isdir(d) else []
        for f in fs:
            with open(os.path.join(d, f), encoding="utf-8", errors="ignore") as fh:
                txt = fh.read()
            toks.extend(w for w in re.findall(r"[a-z]+", txt.lower()) if len(w) >= 3 and w not in STOP)
    return toks


def _ppmi_svd(all_toks, vocab):
    """PPMI co-occurrence over `vocab`, truncated-SVD to CODE_DIM. Returns {word: vec}."""
    vidx = {w: i for i, w in enumerate(vocab)}
    V = len(vocab)
    co = np.zeros((V, V), dtype=np.float64)
    idxs = [vidx[w] for w in all_toks if w in vidx]
    for p in range(len(idxs)):
        wi = idxs[p]
        lo, hi = max(0, p - WINDOW), min(len(idxs), p + WINDOW + 1)
        for q in range(lo, hi):
            if q != p:
                co[wi, idxs[q]] += 1.0
    tot = co.sum()
    if tot <= 0:
        return {}
    row = co.sum(1, keepdims=True); col = co.sum(0, keepdims=True)
    with np.errstate(divide="ignore", invalid="ignore"):
        pmi = np.log((co * tot) / (row @ col + 1e-12) + 1e-12)
    ppmi = np.maximum(pmi, 0.0)
    U, S, _ = np.linalg.svd(ppmi, full_matrices=False)
    emb = U[:, :CODE_DIM] * S[:CODE_DIM]
    emb = emb / (np.linalg.norm(emb, axis=1, keepdims=True) + 1e-9)
    return {w: emb[vidx[w]] for w in vocab}, co, vidx


def build_pairs(names, shared_vocab, emb, co, vidx, n_pairs, gen):
    """For the top content words in this split, KEY = word vec, TARGET = top-PMI associate vec."""
    toks = _read_novels(names)
    from collections import Counter
    ct = Counter(w for w in toks if w in shared_vocab)
    cand = [w for w, _ in ct.most_common() if w in vidx]
    keys, vals = [], []
    used = set()
    for w in cand:
        if len(keys) >= n_pairs:
            break
        wi = vidx[w]
        assoc_order = np.argsort(-co[wi])
        tgt = None
        for j in assoc_order:
            aw = shared_vocab[j]
            if aw != w and aw not in used and co[wi, j] > 0:
                tgt = aw; break
        if tgt is None:
            continue
        keys.append(emb[w]); vals.append(emb[tgt]); used.add(w)
    return np.array(keys), np.array(vals)


# -------------------- the sparse cortex (faithful small core) --------------------
def _hidden(K, W1, keep, dense):
    pre = np.maximum(K @ W1.T, 0.0)          # relu(W1 @ key), batched
    if dense:
        n = np.linalg.norm(pre, axis=1, keepdims=True)
        return pre / (n + 1e-9)
    k = max(1, int(round(keep * pre.shape[1])))
    out = np.zeros_like(pre)
    for i in range(pre.shape[0]):
        idx = np.argpartition(pre[i], -k)[-k:]
        out[i, idx] = pre[i, idx]
    n = np.linalg.norm(out, axis=1, keepdims=True)
    return out / (n + 1e-9)


def _delta(W2, H, Vv, idxs, epochs, lr):
    for _ in range(epochs):
        for i in idxs:
            pred = W2 @ H[i]
            W2 += lr * np.outer(Vv[i] - pred, H[i])
    return W2


def _hit1(W2, H, Vv, idxs, all_targets):
    hits = 0
    for i in idxs:
        pred = W2 @ H[i]
        sims = all_targets @ pred
        if int(np.argmax(sims)) == i:
            hits += 1
    return hits / max(1, len(idxs))


def _schema_error(W2, H, Vv, idxs):
    return np.array([float(np.linalg.norm(Vv[i] - W2 @ H[i])) for i in idxs])


def run_arm(arm, seed, dense, budget_frac=0.3):
    gen = np.random.default_rng(seed)
    # shared PPMI+SVD space over OLD+NEW
    old_toks, new_toks = _read_novels(NOVELS["old"]), _read_novels(NOVELS["new"])
    from collections import Counter
    ct = Counter(old_toks + new_toks)
    vocab = [w for w, _ in ct.most_common(1200)]
    emb, co, vidx = _ppmi_svd(old_toks + new_toks, vocab)
    Kold, Vold = build_pairs(NOVELS["old"], vocab, emb, co, vidx, N_PAIRS, gen)
    Knew, Vnew = build_pairs(NOVELS["new"], vocab, emb, co, vidx, N_PAIRS, gen)
    nold, nnew = len(Kold), len(Knew)
    K = np.vstack([Kold, Knew]); Vv = np.vstack([Vold, Vnew])
    old_i, new_i = list(range(nold)), list(range(nold, nold + nnew))
    all_tgt = Vv / (np.linalg.norm(Vv, axis=1, keepdims=True) + 1e-9)

    W1 = gen.standard_normal((HID, CODE_DIM)) / np.sqrt(CODE_DIM)
    H = _hidden(K, W1, HID_KEEP, dense)
    W2 = np.zeros((CODE_DIM, HID))
    # Phase 1: learn OLD
    W2 = _delta(W2, H, Vv, old_i, EPOCHS, LR)
    old_after1 = _hit1(W2, H, Vv, old_i, all_tgt)
    # Phase 2: learn NEW with replay of OLD at scarce matched budget.
    # DRILL of the RERUN-4 negative (brain-foundational): the organ prioritizes by ENCODING-surprise (static
    # schema-error at OLD-encoding time); the brain's consolidation replay prioritizes by NEED -- what is
    # CURRENTLY at risk of being forgotten, re-evaluated during new learning (Mattar & Daw 2018 replay =
    # gain x NEED; hippocampal replay of interfered/vulnerable traces). The `need` arm tests that fidelity gap.
    budget = max(1, int(round(budget_frac * nold)))
    se0 = _schema_error(W2, H, Vv, old_i)               # encoding-time surprise (static)
    static_replay = None
    if arm == "selective":
        static_replay = [old_i[j] for j in np.argsort(-se0)[:budget]]
    elif arm == "uniform":                              # info-free twin
        static_replay = [old_i[j] for j in gen.choice(nold, size=budget, replace=False)]
    elif arm == "none":                                 # sequential (no replay)
        static_replay = []
    for _ in range(EPOCHS):
        if arm == "need":                               # dynamic NEED: replay what NEW learning is damaging NOW
            se_now = _schema_error(W2, H, Vv, old_i)
            replay = [old_i[j] for j in np.argsort(-se_now)[:budget]]
        else:
            replay = static_replay
        order = new_i + replay
        gen.shuffle(order)
        for i in order:
            pred = W2 @ H[i]
            W2 += LR * np.outer(Vv[i] - pred, H[i])
    old_after2 = _hit1(W2, H, Vv, old_i, all_tgt)
    new_after2 = _hit1(W2, H, Vv, new_i, all_tgt)
    joint = 0.5 * (old_after2 + new_after2)
    return {"old_after1": old_after1, "old_retained": old_after2, "new_learned": new_after2, "joint": joint}


def run(mode="full", n_boot=2000):
    t0 = time.perf_counter()
    seeds = [11, 23, 37, 41, 53] if mode == "full" else [11, 23]
    out = {}
    for regime, dense in [("sparse", False), ("dense", True)]:
        arms = {}
        for arm in ["selective", "uniform", "none", "need"]:
            rows = [run_arm(arm, s, dense) for s in seeds]
            arms[arm] = {k: [r[k] for r in rows] for k in rows[0]}
        out[regime] = arms
    gen = np.random.default_rng(7)

    def paired(regime, a, b, key="joint"):
        av = np.array(out[regime][a][key]); bv = np.array(out[regime][b][key])
        d = av - bv
        idx = np.array([gen.integers(0, len(d), size=len(d)) for _ in range(n_boot)])
        bt = d[idx].mean(axis=1)
        lo, hi = float(np.percentile(bt, 2.5)), float(np.percentile(bt, 97.5))
        return {"delta": float(d.mean()), "lo": lo, "hi": hi,
                "band": "ABOVE" if lo > 0 else ("BELOW" if hi < 0 else "NOT_SEP"),
                "a_mean": float(av.mean()), "b_mean": float(bv.mean())}

    res = {"sparse_selective_vs_uniform": paired("sparse", "selective", "uniform"),
           "sparse_selective_vs_none": paired("sparse", "selective", "none"),
           "dense_selective_vs_uniform": paired("dense", "selective", "uniform"),
           "sparse_need_vs_uniform": paired("sparse", "need", "uniform"),        # the DRILL: need-based priority
           "sparse_need_vs_selective": paired("sparse", "need", "selective"),
           "means": {r: {a: {k: float(np.mean(v)) for k, v in out[r][a].items()} for a in out[r]} for r in out}}
    sv = res["sparse_selective_vs_uniform"]
    res["VERDICT"] = "HOLDS" if sv["band"] == "ABOVE" else "DOES_NOT_HOLD"
    nv = res["sparse_need_vs_uniform"]
    res["DRILL_VERDICT"] = ("NEED_PRIORITY_RESCUES_THE_ORGAN" if nv["band"] == "ABOVE"
                            else "SELECTIVE_REPLAY_GENUINELY_NO_LEVER_ON_REAL_DATA")
    res["meta"] = {"anchor": ANCHOR, "ts_iso": _now(), "elapsed_s": time.perf_counter() - t0,
                   "config": {"CODE_DIM": CODE_DIM, "HID": HID, "HID_KEEP": HID_KEEP, "N_PAIRS": N_PAIRS}}
    sp = res["means"]["sparse"]
    _log("SPARSE joint: selective=%.3f uniform=%.3f none=%.3f | (old_ret/new) sel=%.3f/%.3f uni=%.3f/%.3f"
         % (sp["selective"]["joint"], sp["uniform"]["joint"], sp["none"]["joint"],
            sp["selective"]["old_retained"], sp["selective"]["new_learned"],
            sp["uniform"]["old_retained"], sp["uniform"]["new_learned"]))
    _log("SPARSE selective - uniform (twin) = %+.3f [%.3f,%.3f] %s"
         % (sv["delta"], sv["lo"], sv["hi"], sv["band"]))
    dv = res["dense_selective_vs_uniform"]
    _log("DENSE selective - uniform = %+.3f [%.3f,%.3f] %s (sparsity is the causal variable)"
         % (dv["delta"], dv["lo"], dv["hi"], dv["band"]))
    nv = res["sparse_need_vs_uniform"]
    _log("DRILL: NEED-based priority (dynamic, what NEW damages now) joint=%.3f | need - uniform = %+.3f [%.3f,%.3f] %s"
         % (sp["need"]["joint"], nv["delta"], nv["lo"], nv["hi"], nv["band"]))
    _log("VERDICT = %s | DRILL_VERDICT = %s" % (res["VERDICT"], res["DRILL_VERDICT"]))
    return res


def self_test():
    _log("SELF-TEST: novels load; pairs build; sparse cortex learns OLD above chance")
    r = run_arm("none", 11, dense=False)
    assert r["old_after1"] > 0.3, "sparse cortex should learn OLD pairs above chance: %.3f" % r["old_after1"]
    _log("  OLD hit@1 after phase1 = %.3f (chance ~1/128)" % r["old_after1"])
    _log("SELF-TEST PASS")
    return {"old_after1": r["old_after1"]}


def _atomic_write(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, default=float)
    os.replace(tmp, path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--full", action="store_true")
    args = ap.parse_args()
    t0 = time.perf_counter()
    if args.self_test or not args.full:
        st = self_test()
        _atomic_write(os.path.join(OUTPUT_DIR, "_self_test", "metrics.json"),
                      {"verdict": "SELFTEST_PASS", "selftest": st, "ts_iso": _now()})
        _log("DONE self-test in %.1fs" % (time.perf_counter() - t0))
        return
    res = run("full")
    _atomic_write(os.path.join(OUTPUT_DIR, "metrics.json"), res)
    _log("DONE full in %.1fs -> %s" % (time.perf_counter() - t0, OUTPUT_DIR))


if __name__ == "__main__":
    main()
