"""B-alpha NARROW SCALE-UP: build the held-out 2-hop hypernym QA set (INDEPENDENT gold via nltk WordNet).

The discriminating design (vs A1's by-construction control): the gold is the TRUE authoritative WordNet 2-hop
hypernym closure (computed via nltk -- a lexical DB, NOT an LLM; 11th-rule clean), INCLUDING chains whose
intermediate synset is NOT in the substrate's top-5k backbone. The deterministic walker (cell-side) traverses ONLY
the persisted in-5k HYPERNYM edges, so it CANNOT attest a 2-hop path whose intermediate was not ingested -> it
REFUSES (no hallucination). => recall measures REAL backbone coverage and genuinely falls below 1.0 (probe: 0.592),
unlike A1 (1.0/1.0 by construction). precision/provenance stays 100% (deterministic soundness; the 5th gate verifies).

POSITIVE item: (x, z) where z is a TRUE 2-hop hypernym of x per nltk, x & z both in-5k. Walker SHOULD find an
  attested path (recall); if the only intermediate is out-of-5k, walker correctly REFUSES (a genuine coverage miss).
NEGATIVE item: (x, z') where z' is NOT a true 2-hop hypernym of x AND verified-unreachable (exhaustive no-path) ->
  walker SHOULD REFUSE (safety). Since persisted edges subset true edges, refuse is guaranteed -- the negatives
  confirm the refuse path fires + power the discrimination_self_check (both classes present).

Output: experiments/data/b_alpha_2hop_qa_v1.jsonl (TRACKED location, like the A2 set + held-out gold). Frozen +
byte-identical -> Skunkworks validity-VET (the gold's correctness is the load-bearing input to the cert-run).
Deterministic seed. ASCII-only. Run LOCALLY (needs nltk); the cell does NOT need nltk (loads this frozen set).
"""
from __future__ import annotations
import argparse
import json
import random
import sys
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
OUT = REPO / "experiments" / "data" / "b_alpha_2hop_qa_v1.jsonl"
SEED = 0
N_POS = 300
N_NEG = 300
NEG_VERIFY_DEPTH = 8   # negative "not reachable" verified exhaustively (corpus-completeness on the no-path claim)


def load_backbone():
    """Return (names_in5k:set, adj:name->[hypernym names]) over the PERSISTED in-5k HYPERNYM edges (from metadata,
    mirrors the materialized Store edges: both endpoints in-5k)."""
    from backend.substrate_index.partition import PartitionedStore
    ps = PartitionedStore(REPO / "data" / "substrate_index")
    atoms = [a for a in ps.all_atoms() if str(a.id).startswith("WN_")]
    names_in5k = {a.id[3:] for a in atoms}
    adj = defaultdict(list)
    for a in atoms:
        for h in (a.metadata.get("hypernyms") or []):
            if h in names_in5k:                 # both endpoints in-5k (mirrors materialized edge 0-phantom)
                adj[a.id[3:]].append(h)
    return names_in5k, adj


def reachable_within(adj, x, z, depth):
    """Exhaustive BFS over the persisted backbone: is z reachable from x within `depth` hops?"""
    if x == z:
        return True
    frontier = {x}
    seen = {x}
    for _ in range(depth):
        nxt = set()
        for node in frontier:
            for tgt in adj.get(node, []):
                if tgt == z:
                    return True
                if tgt not in seen:
                    seen.add(tgt); nxt.add(tgt)
        frontier = nxt
    return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(OUT))
    args = ap.parse_args()
    from nltk.corpus import wordnet as wn
    rng = random.Random(SEED)

    names_in5k, adj = load_backbone()
    sorted_names = sorted(names_in5k)   # deterministic order
    n_edges = sum(len(v) for v in adj.values())
    print(f"in-5k synsets: {len(names_in5k)}  persisted HYPERNYM edges: {n_edges}")

    # TRUE 2-hop hypernym gold via nltk (X,Z both in-5k); record whether an in-5k intermediate exists
    positives = []   # (x, z, in5k_intermediate_or_None)
    for name in sorted_names:
        try:
            sx = wn.synset(name)
        except Exception:
            continue
        for h1 in sx.hypernyms() + sx.instance_hypernyms():
            for h2 in h1.hypernyms() + h1.instance_hypernyms():
                if h2.name() != name and h2.name() in names_in5k:
                    inter = h1.name() if h1.name() in names_in5k else None
                    positives.append((name, h2.name(), inter))
    # dedup by (x,z), prefer a row that has an in-5k intermediate recorded
    pos_map = {}
    for (x, z, inter) in positives:
        k = (x, z)
        if k not in pos_map or (inter and not pos_map[k]):
            pos_map[k] = inter
    pos_pairs = sorted(pos_map.keys())
    rng.shuffle(pos_pairs)
    print(f"TRUE 2-hop gold pairs (X,Z in-5k): {len(pos_pairs)}")

    pos_items = []
    for i, (x, z) in enumerate(pos_pairs[:N_POS]):
        pos_items.append({"id": f"BA-POS-{i:03d}", "type": "positive", "x": x, "z": z,
                          "gold_2hop": True, "in5k_intermediate": pos_map[(x, z)],
                          "walker_can_attest": pos_map[(x, z)] is not None})
    # sanity: walker_can_attest fraction = expected recall ceiling
    attestable = sum(1 for it in pos_items if it["walker_can_attest"])
    print(f"positives sampled: {len(pos_items)}  walker-attestable (in-5k intermediate): {attestable} "
          f"({100.0*attestable/max(len(pos_items),1):.1f}% = expected recall)")

    # NEGATIVES: (x, z') z' in-5k, NOT a true 2-hop hypernym of x, verified-unreachable within NEG_VERIFY_DEPTH
    true_2hop_by_x = defaultdict(set)
    for (x, z) in pos_map:
        true_2hop_by_x[x].add(z)
    xs_pool = [it["x"] for it in pos_items]
    neg_items = []
    tries = 0
    while len(neg_items) < N_NEG and tries < N_NEG * 200:
        tries += 1
        x = xs_pool[rng.randrange(len(xs_pool))]
        zc = sorted_names[rng.randrange(len(sorted_names))]
        if zc == x or zc in true_2hop_by_x.get(x, set()):
            continue
        # also exclude true 1-hop (direct hypernym) to keep negatives clean
        try:
            if zc in [h.name() for h in wn.synset(x).hypernyms()]:
                continue
        except Exception:
            continue
        if reachable_within(adj, x, zc, NEG_VERIFY_DEPTH):
            continue   # actually reachable -> not a clean negative
        neg_items.append({"id": f"BA-NEG-{len(neg_items):03d}", "type": "negative", "x": x, "z": zc,
                          "gold_2hop": False, "in5k_intermediate": None, "walker_can_attest": False,
                          "unreachable_verified_depth": NEG_VERIFY_DEPTH})
    print(f"negatives sampled: {len(neg_items)} (verified-unreachable within depth {NEG_VERIFY_DEPTH})")

    items = pos_items + neg_items
    outp = Path(args.out)
    outp.parent.mkdir(parents=True, exist_ok=True)
    with open(outp, "w", encoding="utf-8") as f:
        for it in items:
            f.write(json.dumps(it) + "\n")
    print(f"\nwrote {len(items)} items ({len(pos_items)} pos + {len(neg_items)} neg) -> {outp.relative_to(REPO)}")
    print(f"expected: recall ~= {100.0*attestable/max(len(pos_items),1):.1f}% (MIDDLE_BAND if 40-70); refuse ~= 100%; provenance 100%")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
