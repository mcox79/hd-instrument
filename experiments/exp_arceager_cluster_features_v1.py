"""exp_arceager_cluster_features_v1 -- BUILD ACROSS THE 0.81 UAS WALL with a richer brain-plausible lexical
representation. The sanctioned search lever (global structured-perceptron/beam) HARD_FAILED on disk (0.809 vs
0.811); the earned bound was "the saturation is a REPRESENTATION/feature gap, deeper than decode." The brain
generalizes over lexical CLASSES, not surface word strings (distributional word classes; Koo/Carreras/Collins
2008 semi-supervised clusters gave +1-2 UAS). This adds DISTRIBUTIONAL WORD-CLUSTER features (K-means over
GloVe-300) to the arc-eager transition config features -- ONE variable = +cluster features -- and remeasures UAS
on UD-EWT test vs the base arc-eager (0.818 gold-POS). A positive result CROSSES the located negative; a null
HARDENS it (the ceiling survives a richer lexical representation too, not merely a richer search).

CPU numpy + sklearn MiniBatchKMeans + GloVe (static offline asset). NO torch/spaCy/LLM at inference. ASCII.
--smoke = tiny. Own dir; the cluster map is cached under data/exp_arceager_cluster_features_v1/.
"""
from __future__ import annotations
import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
import argparse, json, sys, time, zlib
from pathlib import Path
from datetime import datetime, timezone
import numpy as np

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in (_REPO, os.path.join(_REPO, "experiments")):
    if p not in sys.path:
        sys.path.insert(0, p)
import experiments.exp_register_native_store_v1 as E  # load_glove_union

from experiments._seed_checkpoint import get_output_dir
OUT_DIR = get_output_dir("exp_arceager_cluster_features_v1")
UD_DIR = Path(_REPO) / "experiments" / "data" / "ud_english_ewt"
SIZE = 1 << 21; MASK = SIZE - 1
SHIFT, LARC, RARC, REDU = 0, 1, 2, 3
ACT_SALT = np.array([0x9E3779B1, 0x85EBCA77, 0xC2B2AE3D, 0x27D4EB2F], dtype=np.int64)
MAXLEN = 50
EPOCHS = int(os.environ.get("HDLAB_EPOCHS", "10"))
EXPLORE_AFTER = 2; EXPLORE_P = 0.9
KCLUST = int(os.environ.get("HDLAB_KCLUST", "500"))


def _h(f): return zlib.crc32(f.encode("utf-8")) & MASK
def _dist(d):
    a = abs(d); return "1" if a == 1 else ("2" if a == 2 else ("3-5" if a <= 5 else ("6-10" if a <= 10 else "11+")))
def _suf(w): return w[-3:] if len(w) >= 3 else w
def _szbucket(k): return "1" if k <= 1 else ("2" if k == 2 else ("3" if k == 3 else ("4-6" if k <= 6 else "7+")))


def _num_of(feats):
    for kv in feats.split("|"):
        if kv.startswith("Number="):
            v = kv.split("=", 1)[1]; return v if v in ("Sing", "Plur") else None
    return None


def _load_ud_feats(split):
    fp = UD_DIR / ("en_ewt-ud-%s.conllu" % split); sents = []; cur = []
    with open(fp, encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if not line:
                if cur: sents.append(cur); cur = []
                continue
            if line.startswith("#"): continue
            c = line.split("\t")
            if len(c) < 8 or "-" in c[0] or "." in c[0]: continue
            try: idx = int(c[0]); head = int(c[6])
            except Exception: continue
            cur.append((idx, c[1], c[3], head, c[7], _num_of(c[5])))
    if cur: sents.append(cur)
    return sents


def build_clusters(sents_all):
    """word(lower) -> cluster-id string, via MiniBatchKMeans over GloVe-300 for the corpus vocab. Cached."""
    cache = os.path.join(OUT_DIR, "cluster_map_k%d.json" % KCLUST)
    if os.path.exists(cache):
        with open(cache, encoding="ascii") as fh:
            return json.load(fh)
    vocab = set()
    for s in sents_all:
        for (i, w, p, h, dl, num) in s:
            vocab.add(w.lower())
    gv = E.load_glove_union(vocab)
    words = [w for w in sorted(vocab) if gv.get(w) is not None]
    X = np.stack([gv[w] for w in words])
    from sklearn.cluster import MiniBatchKMeans
    km = MiniBatchKMeans(n_clusters=min(KCLUST, len(words)), random_state=0, n_init=3, batch_size=1024)
    lab = km.fit_predict(X)
    cmap = {w: "c%d" % int(lab[i]) for i, w in enumerate(words)}
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(cache + ".tmp", "w", encoding="ascii") as fh:
        json.dump(cmap, fh)
    os.replace(cache + ".tmp", cache)
    print("[cluster] %d words -> %d clusters (cached)" % (len(words), KCLUST), flush=True)
    return cmap


_ROOT = ("<root>", "ROOT", "<root>", "<rc>"); _NONE = ("<none>", "<NONE>", "<none>", "<nc>")


def _mk_attr(sent, cmap):
    a = [_ROOT]
    for (i, w, p, h, dl, num) in sent:
        wl = w.lower(); a.append((wl, p, _suf(wl), cmap.get(wl, "<oovc>")))
    return a


def _config_feats(stack, bptr, n, attr, heads, use_clusters):
    s0 = stack[-1]; s1 = stack[-2] if len(stack) >= 2 else None
    b0 = bptr if bptr <= n else None; b1 = (bptr + 1) if (bptr + 1) <= n else None; b2 = (bptr + 2) if (bptr + 2) <= n else None
    s0w, s0p, s0s, s0c = attr[s0]
    s1w, s1p, s1s, s1c = attr[s1] if s1 is not None else _NONE
    b0w, b0p, b0s, b0c = attr[b0] if b0 is not None else _NONE
    b1w, b1p, b1s, b1c = attr[b1] if b1 is not None else _NONE
    b2w, b2p, b2s, b2c = attr[b2] if b2 is not None else _NONE
    dd = _dist(b0 - s0) if (b0 is not None and s0 > 0) else "0"
    s0hh = "1" if s0 in heads else "0"
    F = ["bias", "s0p:" + s0p, "s0w:" + s0w, "s1p:" + s1p, "b0p:" + b0p, "b0w:" + b0w, "b1p:" + b1p, "b2p:" + b2p,
         "s0p_b0p:%s_%s" % (s0p, b0p), "s0w_b0w:%s_%s" % (s0w, b0w), "s0p_b0w:%s_%s" % (s0p, b0w), "s0w_b0p:%s_%s" % (s0w, b0p),
         "s0p_b0p_b1p:%s_%s_%s" % (s0p, b0p, b1p), "s1p_s0p_b0p:%s_%s_%s" % (s1p, s0p, b0p),
         "s0s:" + s0s, "b0s:" + b0s, "s0s_b0p:%s_%s" % (s0s, b0p), "b0s_s0p:%s_%s" % (b0s, s0p),
         "dist:%s_%s_%s" % (dd, s0p, b0p), "s0hh_p:%s_%s" % (s0hh, s0p), "s0hh_b0p:%s_%s" % (s0hh, b0p),
         "stksz:" + _szbucket(len(stack))]
    if use_clusters:
        F += ["s0c:" + s0c, "b0c:" + b0c, "s1c:" + s1c, "b1c:" + b1c,
              "s0c_b0c:%s_%s" % (s0c, b0c), "s0c_b0p:%s_%s" % (s0c, b0p), "s0p_b0c:%s_%s" % (s0p, b0c),
              "s0c_b0w:%s_%s" % (s0c, b0w), "s0w_b0c:%s_%s" % (s0w, b0c),
              "s0c_b0c_dir:%s_%s_%s" % (s0c, b0c, ("L" if (b0 is not None and s0 > 0 and b0 < s0) else "R")),
              "dist_c:%s_%s_%s" % (dd, s0c, b0c)]
    return F


def _legal(stack, bptr, n, heads):
    moves = []; s0 = stack[-1]; buf = bptr <= n
    if buf: moves.append(SHIFT)
    if buf and s0 != 0 and s0 not in heads: moves.append(LARC)
    if buf: moves.append(RARC)
    if s0 != 0 and s0 in heads: moves.append(REDU)
    return moves


def _apply(stack, bptr, heads, a):
    if a == SHIFT: stack.append(bptr); bptr += 1
    elif a == LARC: heads[stack[-1]] = bptr; stack.pop()
    elif a == RARC: heads[bptr] = stack[-1]; stack.append(bptr); bptr += 1
    elif a == REDU: stack.pop()
    return stack, bptr


def _move_costs_live(stack, bptr, n, gold, heads):
    costs = {}; s0 = stack[-1]; b0 = bptr if bptr <= n else None; ss = set(stack)
    for a in _legal(stack, bptr, n, heads):
        if a == SHIFT:
            c = sum(1 for k in stack if gold[k] == b0)
            if 0 <= gold[b0] and gold[b0] in ss: c += 1
            costs[a] = c
        elif a == LARC:
            c = 0; gh = gold[s0]
            if gh != b0 and (bptr + 1) <= gh <= n: c += 1
            c += sum(1 for k in range(bptr, n + 1) if gold[k] == s0); costs[a] = c
        elif a == RARC:
            c = 0; gh = gold[b0]
            if gh != s0 and (gh in ss or (bptr + 1) <= gh <= n): c += 1
            c += sum(1 for k in stack if gold[k] == b0); costs[a] = c
        elif a == REDU:
            costs[a] = sum(1 for k in range(bptr, n + 1) if gold[k] == s0)
    return costs


def _score(base_ids, W, legal):
    return {a: float(W[(base_ids ^ ACT_SALT[a]) & MASK].sum()) for a in legal}


def _amax(scores):
    ba = None; b = -1e18
    for a, s in scores.items():
        if s > b: b = s; ba = a
    return ba


def _upd(W, CW, base_ids, ag, ap, c):
    ig = (base_ids ^ ACT_SALT[ag]) & MASK; ip = (base_ids ^ ACT_SALT[ap]) & MASK
    np.add.at(W, ig, 1.0); np.add.at(CW, ig, c); np.add.at(W, ip, -1.0); np.add.at(CW, ip, -c)


def _train(train, cmap, seed, use_clusters):
    rng = np.random.default_rng(seed); W = np.zeros(SIZE); CW = np.zeros(SIZE); c = 1
    for ep in range(EPOCHS):
        explore = ep >= EXPLORE_AFTER; te = time.time()
        for si in rng.permutation(len(train)):
            s = train[si]; n = len(s); attr = _mk_attr(s, cmap)
            gold = [0] * (n + 1)
            for (i, w, p, h, dl, num) in s: gold[i] = h if 0 <= h <= n else 0
            stack = [0]; bptr = 1; heads = {}; guard = 0
            while bptr <= n or len(stack) > 1:
                if bptr > n and len(stack) <= 1: break
                legal = _legal(stack, bptr, n, heads)
                if not legal: break
                base_ids = np.fromiter((_h(f) for f in _config_feats(stack, bptr, n, attr, heads, use_clusters)), dtype=np.int64)
                scores = _score(base_ids, W, legal); ap = _amax(scores)
                costs = _move_costs_live(stack, bptr, n, gold, heads)
                zero = [a for a in legal if costs.get(a, 1) == 0] or [min(costs, key=lambda k: costs[k])]
                aorl = max(zero, key=lambda a: scores.get(a, -1e18))
                if ap != aorl and costs.get(ap, 1) > 0: _upd(W, CW, base_ids, aorl, ap, c); c += 1
                anext = ap if (explore and ap in legal and rng.random() < EXPLORE_P) else aorl
                stack, bptr = _apply(stack, bptr, heads, anext); guard += 1
                if guard > 4 * (n + 2): break
        print("  [train uc=%s] epoch %d/%d %.1fs" % (use_clusters, ep + 1, EPOCHS, time.time() - te), flush=True)
    return W - CW / c


def _decode(sent, cmap, W, use_clusters):
    n = len(sent); attr = _mk_attr(sent, cmap); stack = [0]; bptr = 1; heads = {}; guard = 0
    while bptr <= n or len(stack) > 1:
        if bptr > n and len(stack) <= 1: break
        legal = _legal(stack, bptr, n, heads)
        if not legal: break
        base_ids = np.fromiter((_h(f) for f in _config_feats(stack, bptr, n, attr, heads, use_clusters)), dtype=np.int64)
        a = _amax(_score(base_ids, W, legal)); stack, bptr = _apply(stack, bptr, heads, a); guard += 1
        if guard > 4 * (n + 2): break
    for i in range(1, n + 1): heads.setdefault(i, 0)
    return heads


def uas(sents, cmap, W, use_clusters):
    hit = tot = 0
    for s in sents:
        heads = _decode(s, cmap, W, use_clusters)
        for (i, w, p, h, d, num) in s:
            if h < 0 or h > len(s): continue
            hit += int(heads.get(i, -1) == h); tot += 1
    return hit / tot if tot else 0.0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true"); ap.add_argument("--epochs", type=int, default=None)
    args = ap.parse_args()
    global EPOCHS
    if args.epochs is not None: EPOCHS = args.epochs
    t0 = time.time(); os.makedirs(OUT_DIR, exist_ok=True)
    train = [s for s in _load_ud_feats("train") if 1 <= len(s) <= MAXLEN]
    dev = [s for s in _load_ud_feats("dev") if 1 <= len(s) <= MAXLEN]
    test = [s for s in _load_ud_feats("test") if 1 <= len(s) <= MAXLEN]
    cmap = build_clusters(train + dev + test)
    if args.smoke:
        EPOCHS = min(EPOCHS, 3); train = train[:400]; test = test[:150]
    print("[data] train=%d test=%d EPOCHS=%d K=%d" % (len(train), len(test), EPOCHS, KCLUST), flush=True)
    res = {}
    for uc in (False, True):
        tt = time.time(); W = _train(train, cmap, 1, uc)
        u = round(uas(test, cmap, W, uc), 4)
        res["clusters" if uc else "base"] = u
        print("[uas] use_clusters=%s test gold-POS UAS=%.4f (%.0fs)" % (uc, u, time.time() - tt), flush=True)
    res["cluster_gain"] = round(res["clusters"] - res["base"], 4)
    res["base_arceager_cited"] = 0.8184
    with open(os.path.join(OUT_DIR, "metrics.json"), "w", encoding="ascii") as fh:
        json.dump({"anchor_name": "arceager_cluster_features_v1", "results": res,
                   "elapsed_s": round(time.time() - t0, 1), "ts_iso": datetime.now(timezone.utc).isoformat()}, fh, indent=2)
    print("\n[SUMMARY] base=%.4f +clusters=%.4f gain=%+.4f (base arc-eager cited 0.8184) [%.0fs]" % (
        res["base"], res["clusters"], res["cluster_gain"], time.time() - t0), flush=True)


if __name__ == "__main__":
    main()
