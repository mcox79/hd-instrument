"""Scaffold-free LOCAL unit test for hdlab.additive_map.AdditiveKGMap (CPU, tiny synthetic; no GPU).

Exercises the full live API on a planted TransE-consistent held-out-entity arena:
  fit -> compose_entity / compose_into_table -> insert_entity -> score_all / score_edges -> save/load round-trip
  + a SCRAMBLE must-fail discriminator (relation-scrambled compose must underperform the real compose).

Run: python verification/verify_additive_map_api.py  (exit 0 = PASS). ASCII-only, terse.
"""

import os
import sys
import tempfile
from collections import defaultdict

import numpy as np
import torch

_THIS = os.path.abspath(__file__)
_REPO = os.path.dirname(os.path.dirname(_THIS))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from hdlab.additive_map import AdditiveKGMap, additive_direct_scores  # noqa: E402


def _planted_arena(seed, n_ent=300, n_rel=6, k_lat=8, deg=3):
    """Planted TransE-consistent arena: edge (h,r,t) links h to the entity nearest z[h]+w[r]."""
    rng = np.random.default_rng(seed * 100019 + 3)
    z = rng.standard_normal((n_ent, k_lat))
    w = rng.standard_normal((n_rel, k_lat))
    edges = []
    for h in range(n_ent):
        for r in rng.choice(n_rel, size=deg, replace=False):
            d = np.linalg.norm(z - (z[h] + w[r]), axis=1)
            d[h] = np.inf
            edges.append(("e%d" % h, "r%d" % int(r), "e%d" % int(np.argmin(d))))
    return list(dict.fromkeys(edges))


def _heldout_split(edges, n_ent, frac=0.2, support_frac=0.5, seed=7):
    """Withhold ~frac entities from every train edge; partition their tail-edges into support/query."""
    rng = np.random.default_rng(seed * 100003 + 7)
    hold = {"e%d" % i for i in rng.choice(n_ent, size=max(1, int(frac * n_ent)), replace=False).tolist()}
    train, held_by_tail = [], defaultdict(list)
    for (h, r, t) in edges:
        if h not in hold and t not in hold:
            train.append((h, r, t))
        elif t in hold and h not in hold:
            held_by_tail[t].append((h, r, t))
    support, query = [], []
    rng2 = np.random.default_rng(seed * 991 + 5)
    for t in sorted(held_by_tail):
        es = held_by_tail[t]
        d = len(es)
        if d == 1:
            query.append(es[0]); continue
        order = rng2.permutation(d)
        nsup = min(max(1, int(round(support_frac * d))), d - 1)
        sup = set(order[:nsup].tolist())
        for j, e in enumerate(es):
            (support if j in sup else query).append(e)
    return train, support, query


def _to_int(triples, e2i, r2i):
    return np.array([[e2i[h], r2i[r], e2i[t]] for (h, r, t) in triples], dtype=np.int64)


def _mrr(scores, query_int):
    """Unfiltered mean reciprocal rank of the gold tail (higher score = better)."""
    rr = []
    for i in range(query_int.shape[0]):
        g = int(query_int[i, 2])
        row = scores[i]
        rr.append(1.0 / (int((row > row[g]).sum().item()) + 1))
    return float(np.mean(rr)) if rr else float("nan")


def main():
    torch.set_num_threads(1)
    device = torch.device("cpu")
    fails = []

    edges = _planted_arena(7, n_ent=300, n_rel=6, k_lat=8, deg=3)
    ent_labels = sorted({x for (h, _r, t) in edges for x in (h, t)})
    rel_labels = sorted({r for (_h, r, _t) in edges})
    n_ent, n_rel = len(ent_labels), len(rel_labels)
    e2i = {lbl: i for i, lbl in enumerate(ent_labels)}
    r2i = {lbl: i for i, lbl in enumerate(rel_labels)}
    train, support, query = _heldout_split(edges, n_ent, frac=0.2, support_frac=0.5, seed=7)
    assert len(query) >= 8, "planted arena produced too few held-out queries (%d)" % len(query)

    # ---- fit via the class (pin the full vocab so held-out rows exist) ----
    kmap = AdditiveKGMap(device=device).fit(train, entities=e2i, relations=r2i, k=12, epochs=250, seed=7)
    if kmap.num_entities != n_ent:
        fails.append("num_entities %d != %d" % (kmap.num_entities, n_ent))
    if kmap.X.shape[1] != 12:
        fails.append("k mismatch %d != 12" % kmap.X.shape[1])

    support_int = _to_int(support, e2i, r2i)
    query_int = _to_int(query, e2i, r2i)

    # ---- batch compose (ANCHOR) vs SCRAMBLE (must-fail) vs RANDOM (null) ----
    Xac, _deg = kmap.compose_into_table(support_int)
    rel_perm = np.random.default_rng(99).permutation(n_rel)
    Xscr, _ = kmap.compose_into_table(support_int, rel_perm=rel_perm)
    gR = torch.Generator(device="cpu").manual_seed(123)
    Xr = (torch.randn(n_ent, 12, generator=gR) * 0.1)
    Dr = (torch.randn(n_rel, 12, generator=gR) * 0.1)

    anchor_mrr = _mrr(additive_direct_scores(Xac, kmap.D, query_int, device), query_int)
    scramble_mrr = _mrr(additive_direct_scores(Xscr, kmap.D, query_int, device), query_int)
    random_mrr = _mrr(additive_direct_scores(Xr, Dr, query_int, device), query_int)

    if not (anchor_mrr >= random_mrr + 0.05):
        fails.append("anchor(%.4f) must beat random(%.4f) by >=0.05" % (anchor_mrr, random_mrr))
    if not (anchor_mrr >= scramble_mrr + 0.03):
        fails.append("SCRAMBLE must-fail: anchor(%.4f) - scramble(%.4f) < 0.03" % (anchor_mrr, scramble_mrr))

    # ---- single-entity live API: compose_entity -> insert_entity -> score_all ----
    held_by_tail = defaultdict(list)
    for (h, r, t) in support:
        held_by_tail[t].append((h, r))
    t_novel = max(held_by_tail, key=lambda t: len(held_by_tail[t]))
    code = kmap.compose_entity(held_by_tail[t_novel])
    if tuple(code.shape) != (12,):
        fails.append("compose_entity shape %s != (12,)" % (tuple(code.shape),))
    new_idx = kmap.insert_entity(code, name="NOVEL")
    if new_idx != n_ent or kmap.num_entities != n_ent + 1:
        fails.append("insert_entity idx=%d (want %d), N=%d" % (new_idx, n_ent, kmap.num_entities))
    # a query head reaching t_novel should rank the inserted NOVEL row near the composed position
    q_for_t = [(h, r) for (h, r, t) in query if t == t_novel]
    if q_for_t:
        h, r = q_for_t[0]
        sc = kmap.score_all(h, r)
        rank = int((sc > sc[new_idx]).sum().item()) + 1
        if rank > max(30, int(0.1 * kmap.num_entities)):
            fails.append("score_all: NOVEL inserted entity ranked %d (expected top-10%%)" % rank)

    # ---- persistence round-trip: save -> load -> identical coords + scores ----
    with tempfile.TemporaryDirectory() as td:
        path = os.path.join(td, "amap")
        kmap.save(path)
        loaded = AdditiveKGMap.load(path, device="cpu")
        if not torch.allclose(loaded.X, kmap.X):
            fails.append("persist: X mismatch after load")
        if not torch.allclose(loaded.D, kmap.D):
            fails.append("persist: D mismatch after load")
        if loaded.entity_to_idx != kmap.entity_to_idx:
            fails.append("persist: entity_to_idx mismatch")
        if loaded.relation_to_idx != kmap.relation_to_idx:
            fails.append("persist: relation_to_idx mismatch")
        s_before = kmap.score_all(query[0][0], query[0][1])
        s_after = loaded.score_all(query[0][0], query[0][1])
        if not torch.allclose(s_before, s_after):
            fails.append("persist: score_all diverged after reload")

    print("[verify_additive_map_api] anchor_mrr=%.4f scramble_mrr=%.4f random_mrr=%.4f nq=%d N=%d k=%d"
          % (anchor_mrr, scramble_mrr, random_mrr, query_int.shape[0], n_ent, 12))
    if fails:
        print("FAIL:")
        for f in fails:
            print("  - " + f)
        raise SystemExit(1)
    print("PASS: fit/compose/insert/score/persist round-trip + scramble must-fail all green")


if __name__ == "__main__":
    main()
