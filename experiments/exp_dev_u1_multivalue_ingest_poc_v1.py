"""De-risk OPEN-E (my own U1 recommendation): can the substrate store a SET of objects per
1-to-many (s,p) key + read it back via top-k? Tests TWO stores before Skunkworks VETs my proposal:
  - DELTA-rule cfrpe (W += (LR/n)(o - W@key)key^T): converges to the AVERAGE of the objects ->
    predict POOR set-recall (the avg is near no single object when they are spread).
  - HEBBIAN-accumulate (W += outer(o, key)/n): sums objects -> W@key ~ sum of objects ->
    predict GOOD set-recall via top-k (if objects roughly orthogonal in the HD space).

Metric = set-recall@k: for a key with K true objects, does top-K(key) contain them? Tested on
synthetic 1-to-many keys (controlled K) + a SAMPLE of REAL FB15k-237 1-to-many keys. CPU, ASCII.
"""
import json
import math
from collections import defaultdict
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parent.parent
KG_PATH = REPO / "data" / "datasets" / "fb15k_237_train_50k.jsonl"
LR = 0.5


def bipolar(M, n, g):
    X = (g.integers(0, 2, size=(M, n)) * 2 - 1).astype(np.float32)
    return X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-8)


def build_delta(keys_objs, E, R, Ekey_fn, n):
    W = np.zeros((n, n), dtype=np.float32)
    for (s, p), objs in keys_objs:
        key = Ekey_fn(s, p)
        for o in objs:
            W += (LR / n) * np.outer(E[o] - W @ key, E[o] * 0 + E[o])  # delta toward each o (recency-avg)
    return W


def build_delta_simple(triples, E, Ekey_fn, n):
    W = np.zeros((n, n), dtype=np.float32)
    for (s, p, o) in triples:
        key = Ekey_fn(s, p)
        W += (LR / n) * np.outer(E[o] - W @ key, key)
    return W


def build_hebbian(triples, E, Ekey_fn, n):
    W = np.zeros((n, n), dtype=np.float32)
    for (s, p, o) in triples:
        W += np.outer(E[o], Ekey_fn(s, p)) / n
    return W


def set_recall_at_k(W, E, key_objs, Ekey_fn):
    """For each key with K true objects, top-K(key) set-overlap with the true objects."""
    tot = 0.0
    for (s, p), objs in key_objs:
        k = len(objs)
        scores = E @ (W @ Ekey_fn(s, p))
        topk = set(np.argsort(scores)[-k:].tolist())
        tot += len(topk & set(objs)) / k
    return tot / max(len(key_objs), 1)


def synthetic_test():
    g = np.random.default_rng(0); n = 1024; n_ent = 400; n_rel = 10
    E = bipolar(n_ent, n, g); R = bipolar(n_rel, n, g); sq = math.sqrt(n)
    ekey = lambda s, p: E[s] * R[p] * sq
    # 60 keys, each 1-to-many with K in [2..6]
    key_objs = []; triples = []
    used = set()
    for i in range(60):
        s = int(g.integers(0, n_ent)); p = int(g.integers(0, n_rel))
        if (s, p) in used:
            continue
        used.add((s, p))
        K = int(g.integers(2, 7)); objs = list(g.choice(n_ent, K, replace=False))
        key_objs.append(((s, p), objs))
        triples += [(s, p, int(o)) for o in objs]
    Wd = build_delta_simple(triples, E, ekey, n)
    Wh = build_hebbian(triples, E, ekey, n)
    rd = set_recall_at_k(Wd, E, key_objs, ekey)
    rh = set_recall_at_k(Wh, E, key_objs, ekey)
    print("[synthetic 1-to-many, %d keys K=2..6]  delta-rule set-recall@k=%.3f | hebbian set-recall@k=%.3f" % (
        len(key_objs), rd, rh))
    return rd, rh


def real_fb15k_test(n_keys=80):
    g = np.random.default_rng(1); n = 4096
    sp = defaultdict(set)
    for line in open(KG_PATH, encoding="utf-8"):
        r = json.loads(line); sp[(r["subject"], r["predicate"])].add(r["object"])
    multi = [(k, sorted(v)) for k, v in sp.items() if 2 <= len(v) <= 8]
    g.shuffle(multi); multi = multi[:n_keys]
    ents = sorted({e for (s, p), objs in multi for e in ([s] + objs)})
    rels = sorted({p for (s, p), _ in multi})
    eid = {e: i for i, e in enumerate(ents)}; rid = {p: i for i, p in enumerate(rels)}
    E = bipolar(len(ents), n, g); R = bipolar(len(rels), n, g); sq = math.sqrt(n)
    ekey = lambda s, p: E[s] * R[p] * sq
    triples = [(eid[s], rid[p], eid[o]) for (s, p), objs in multi for o in objs]
    key_objs = [((eid[s], rid[p]), [eid[o] for o in objs]) for (s, p), objs in multi]
    Wd = build_delta_simple(triples, E, ekey, n)
    Wh = build_hebbian(triples, E, ekey, n)
    rd = set_recall_at_k(Wd, E, key_objs, ekey)
    rh = set_recall_at_k(Wh, E, key_objs, ekey)
    print("[real FB15k-237 1-to-many, %d keys (2..8 obj), %d ents, n=%d]  delta=%.3f | hebbian=%.3f" % (
        len(key_objs), len(ents), n, rd, rh))
    return rd, rh


if __name__ == "__main__":
    print("=== OPEN-E de-risk: multi-value (set) ingest -- delta-rule vs Hebbian-accumulate ===")
    sd, sh = synthetic_test()
    rd, rh = real_fb15k_test()
    print()
    winner = "HEBBIAN-accumulate" if (sh > sd and rh > rd) else ("DELTA-rule" if (sd > sh and rd > rh) else "MIXED")
    print("[OPEN-E verdict] %s handles 1-to-many sets better." % winner)
    print("  -> if hebbian wins: U1 multi-value ingest = Hebbian-accumulate store + top-k set-readout")
    print("     (delta-rule averages objects -> poor set-recall, as predicted). Grounds my OPEN-E recommendation.")
    if sh >= 0.7 or rh >= 0.6:
        print("  -> multi-value set-ingest is FEASIBLE (set-recall above chance) -> OPEN-E is buildable.")
    else:
        print("  -> set-recall LOW even for hebbian -> OPEN-E harder than hoped; flag to Skunkworks before building.")
