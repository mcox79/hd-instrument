"""B-alpha BROAD (ARC-1 T2): build the multi-benchmark composed-reasoning held-out QA set (INDEPENDENT nltk gold).

BROAD characterizes the substrate's composed-reasoning ENVELOPE -- WHERE deterministic multi-hop QA over the
materialized typed-edge backbone works vs CLIFFS -- across (rel_type x depth) benchmarks. Each benchmark gets its OWN
independent nltk gold (so each genuinely DISCRIMINATES, per Skunkworks; a by-construction-saturated benchmark would be
MEASURED_MECHANISM not a discriminating cert). A per-benchmark HARD-FAIL is an HONEST cert-grade FINDING (the cliff),
not a failure to hide.

Benchmarks (probe-grounded; nltk-backed independent gold):
  HYPERNYM 2-hop  (probe recall 0.592 MIDDLE)   HYPERNYM 3-hop (0.368 HARD_FAIL)   HYPERNYM 4-hop (0.207 HARD_FAIL)
  PART_OF  2-hop  (0.620 MIDDLE)                 PART_OF  3-hop (0.462 MIDDLE)
-> two axes: DEPTH-CLIFF (2-hop works ~MIDDLE; 3-4 hop falls to HARD_FAIL) + RELATION-GENERALITY (hypernym + part_of
both MIDDLE at 2-hop). The envelope (HARD_PASS/MIDDLE/HARD_FAIL per benchmark) IS the deliverable.

POSITIVE: (x,z) z a TRUE depth-hop ancestor of x via the relation (nltk; x,z in-5k). NEGATIVE: (x,z') NOT a true
depth-hop ancestor + verified-unreachable. Output: experiments/data/b_alpha_broad_qa_v1.jsonl (TRACKED; frozen +
Skunkworks validity-VET). Deterministic SEED=0. Run LOCALLY (nltk); the cell does NOT need nltk. ASCII-only. No LLM.
"""
from __future__ import annotations
import argparse
import json
import random
from collections import defaultdict
from pathlib import Path
import sys

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
OUT = REPO / "experiments" / "data" / "b_alpha_broad_qa_v1.jsonl"
SEED = 0
N_PER = 150            # positives + negatives per benchmark (capped at available gold)
NEG_VERIFY_DEPTH = 10

# (benchmark key, rel_type, depth)
BENCHMARKS = [
    ("HYPERNYM_2hop", "HYPERNYM", 2),
    ("HYPERNYM_3hop", "HYPERNYM", 3),
    ("HYPERNYM_4hop", "HYPERNYM", 4),
    ("PART_OF_2hop", "PART_OF", 2),
    ("PART_OF_3hop", "PART_OF", 3),
]


def load_backbone():
    from backend.substrate_index.partition import PartitionedStore
    from backend.substrate_index.schema import Corpus
    ps = PartitionedStore(REPO / "data" / "substrate_index")
    atoms = [a for a in ps.all_atoms() if str(a.id).startswith("WN_")]
    names_in5k = {a.id[3:] for a in atoms}
    cstore = ps._store_for(Corpus.CONCEPT)
    adj = {"HYPERNYM": defaultdict(list), "PART_OF": defaultdict(list)}
    for (s, rt, t) in cstore._all_relations:
        if rt in adj and s.startswith("WN_") and t.startswith("WN_"):
            adj[rt][s[3:]].append(t[3:])
    return names_in5k, adj


def reachable_within(adjmap, x, z, depth):
    if x == z:
        return True
    frontier, seen = {x}, {x}
    for _ in range(depth):
        nxt = set()
        for n in frontier:
            for t in adjmap.get(n, []):
                if t == z:
                    return True
                if t not in seen:
                    seen.add(t); nxt.add(t)
        frontier = nxt
    return False


def true_nhop(wn, names_in5k, rel_type, name, depth):
    cur = {name}
    for _ in range(depth):
        nxt = set()
        for nm in cur:
            try:
                s = wn.synset(nm)
            except Exception:
                continue
            if rel_type == "HYPERNYM":
                for h in s.hypernyms() + s.instance_hypernyms():
                    nxt.add(h.name())
            else:  # PART_OF: part -> whole = holonyms
                for h in s.part_holonyms() + s.member_holonyms() + s.substance_holonyms():
                    nxt.add(h.name())
        cur = nxt
    return {z for z in cur if z != name and z in names_in5k}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(OUT))
    args = ap.parse_args()
    from nltk.corpus import wordnet as wn
    rng = random.Random(SEED)
    names_in5k, adj = load_backbone()
    sorted_names = sorted(names_in5k)
    items = []

    for bkey, rel, depth in BENCHMARKS:
        adjmap = adj[rel]
        # positives: true depth-hop gold pairs
        pairs = []
        for name in sorted_names:
            for z in true_nhop(wn, names_in5k, rel, name, depth):
                pairs.append((name, z))
        rng.shuffle(pairs)
        npos = min(N_PER, len(pairs))
        pos = pairs[:npos]
        true_by_x = defaultdict(set)
        for (x, z) in pairs:
            true_by_x[x].add(z)
        bpos = [{"id": f"BA-BR-{bkey}-POS-{i:03d}", "benchmark": bkey, "rel_type": rel, "depth": depth,
                 "type": "positive", "x": x, "z": z, "gold_nhop": True} for i, (x, z) in enumerate(pos)]
        # negatives: not-true + unreachable
        xs = [x for (x, _) in pos] or sorted_names
        bneg, tries = [], 0
        while len(bneg) < npos and tries < npos * 300:
            tries += 1
            x = xs[rng.randrange(len(xs))]
            zc = sorted_names[rng.randrange(len(sorted_names))]
            if zc == x or zc in true_by_x.get(x, set()):
                continue
            if reachable_within(adjmap, x, zc, NEG_VERIFY_DEPTH):
                continue
            bneg.append({"id": f"BA-BR-{bkey}-NEG-{len(bneg):03d}", "benchmark": bkey, "rel_type": rel, "depth": depth,
                         "type": "negative", "x": x, "z": zc, "gold_nhop": False,
                         "unreachable_verified_depth": NEG_VERIFY_DEPTH})
        items.extend(bpos + bneg)
        # expected recall = fraction of positives with a persisted depth-hop path
        att = sum(1 for it in bpos if reachable_within(adjmap, it["x"], it["z"], depth))
        print(f"  {bkey:16s} (rel={rel}, depth={depth}): pos={len(bpos)} neg={len(bneg)} "
              f"expected_recall={att/max(len(bpos),1):.3f}")

    outp = Path(args.out)
    outp.parent.mkdir(parents=True, exist_ok=True)
    with open(outp, "w", encoding="utf-8") as f:
        for it in items:
            f.write(json.dumps(it) + "\n")
    print(f"\nwrote {len(items)} items across {len(BENCHMARKS)} benchmarks -> {outp.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
