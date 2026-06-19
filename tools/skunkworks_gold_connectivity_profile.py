"""SKUNKWORKS (Auditor) substrate-internal cell: gold-connectivity profile.

Measures the structural neighborhood of the in-coverage held-out gold atoms in the
EXACT graph M4d walks, to set the a priori edge budget / HARD-PASS bar for DECISION 55a
and to test whether M4d 0.272 is graph-bound (55a has headroom) or architecture-bound.

R2 / 15th rule: reads ONLY the ground_truth_atoms field of the held-out file (gold atom
NAMES, which are public math concepts) -- NEVER the question text. CPU-only, no bge,
no LLM. Replicates M4d's graph construction EXACTLY (same WALK_EDGES, same 11 partition
relations.jsonl, same undirected qualified-id adjacency, same _short normalization).

ASCII only.
"""
from __future__ import annotations
import sys, json
from pathlib import Path
from collections import defaultdict, deque

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
DATA_ROOT = REPO / "data" / "substrate_index"
HELDOUT = DATA_ROOT / "benchmark_corpus_HELD_OUT_q54_q65_converted.jsonl"

# EXACT M4d walk set (from exp_substrate_m4d_capability_graph_walk_heldout_cpu_v1.py).
# Note: INVERSE_PAIR is in the DRILL spec but does NOT occur in the walked files and is
# NOT in M4d's WALK_EDGES; profiling the graph M4d ACTUALLY uses.
WALK_EDGES = {"DEPENDS_ON", "SHARES_MATH", "SPECIALIZES", "USES", "INSTANCE_OF"}
MAX_HOP = 2


def _short(x):
    return str(x).split("::")[-1].split("/")[-1].strip().lower()


def bfs_levels(seeds, adj, max_hop):
    """min hop distance from any seed (0 at seed) up to max_hop. Same as M4d bfs_proximity."""
    dist = {s: 0 for s in seeds}
    q = deque((s, 0) for s in seeds)
    while q:
        n, d = q.popleft()
        if d >= max_hop:
            continue
        for m in adj.get(n, ()):
            if m not in dist:
                dist[m] = d + 1
                q.append((m, d + 1))
    return dist


def main():
    # ---- 1. atoms (qualified ids + short names), EXACTLY like M4d via PartitionedStore ----
    from backend.substrate_index.partition import PartitionedStore
    pstore = PartitionedStore(DATA_ROOT)
    atoms = list(pstore.all_atoms())
    sset = {_short(a.id) for a in atoms}
    short_to_quals = defaultdict(set)
    qual_to_short = {}
    for a in atoms:
        short_to_quals[_short(a.id)].add(a.qualified_id)
        qual_to_short[a.qualified_id] = _short(a.id)
    print("[atoms] %d atoms | %d distinct short-names" % (len(atoms), len(sset)), flush=True)

    # ---- 2. adjacency over WALK_EDGES from the 11 partition relations.jsonl (qualified-id space) ----
    adj = defaultdict(set)
    typed_adj = defaultdict(lambda: defaultdict(set))  # node -> rel_type -> set(neighbors)
    n_files = 0
    n_edges = 0
    for rp in sorted(DATA_ROOT.rglob("relations.jsonl")):
        n_files += 1
        for ln in open(rp, encoding="utf-8"):
            ln = ln.strip()
            if not ln:
                continue
            try:
                rr = json.loads(ln)
            except Exception:
                continue
            rt = (rr.get("rel_type", "") or "").upper()
            if rt in WALK_EDGES:
                s = rr.get("src_id", "")
                t = rr.get("tgt_id", "")
                if s and t and s != t:
                    adj[s].add(t)
                    adj[t].add(s)
                    typed_adj[s][rt].add(t)
                    typed_adj[t][rt].add(s)
                    n_edges += 1
    print("[graph] %d relations.jsonl files | %d walkable undirected edges | %d nodes with >=1 edge"
          % (n_files, n_edges, len(adj)), flush=True)

    # ---- 3. gold atom NAMES only (R2-safe): read ONLY ground_truth_atoms; never the question ----
    gold_raw = []  # list of (qid_label, list_of_gold_short)
    with open(HELDOUT, encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if not ln:
                continue
            obj = json.loads(ln)
            # touch ONLY these two fields; ignore obj["question"] entirely
            qlabel = obj.get("qid", "?")
            gts = obj.get("ground_truth_atoms") or []
            gshorts = [_short(g) for g in gts]
            gold_raw.append((qlabel, gshorts))
    # in-coverage gold short-names = those present in substrate (same test M4d uses)
    incov_gold = sorted({g for _, gs in gold_raw for g in gs if g in sset})
    print("[gold] %d held-out questions | %d distinct in-coverage gold atoms: %s"
          % (len(gold_raw), len(incov_gold), incov_gold), flush=True)

    # ---- 4. per-gold connectivity profile in the SAME graph ----
    rows = []
    for g in incov_gold:
        quals = sorted(short_to_quals.get(g, []))
        # gold may map to multiple qualified ids (cross-corpus); union their neighborhoods,
        # but also report per-qid degree so collisions are visible.
        present_as_node = [q for q in quals if q in adj]
        # hop-1 (union over the gold's qualified ids)
        h1 = set()
        typed = defaultdict(set)
        for q in quals:
            for nb in adj.get(q, ()):  # qualified-id neighbors
                h1.add(nb)
            for rt, nbs in typed_adj.get(q, {}).items():
                typed[rt] |= nbs
        # hop-2 reachable set (<=2 hops, excluding the gold seeds themselves)
        dist = bfs_levels(quals, adj, MAX_HOP)
        reach = {n for n, d in dist.items() if d > 0}
        h2_only = {n for n, d in dist.items() if d == 2}
        rows.append({
            "gold": g,
            "n_qual_ids": len(quals),
            "qual_ids_with_edges": len(present_as_node),
            "hop1_degree": len(h1),
            "typed": {rt: len(nbs) for rt, nbs in sorted(typed.items())},
            "hop2_reach": len(reach),
            "hop2_only": len(h2_only),
            "hop1_neighbors_short": sorted({qual_to_short.get(n, n) for n in h1}),
            "hop2_reach_short": sorted({qual_to_short.get(n, n) for n in reach}),
        })

    # ---- 5. aggregate ----
    def med(xs):
        xs = sorted(xs)
        n = len(xs)
        if n == 0:
            return 0
        return xs[n // 2] if n % 2 else (xs[n // 2 - 1] + xs[n // 2]) / 2

    h1s = [r["hop1_degree"] for r in rows]
    h2s = [r["hop2_reach"] for r in rows]

    print("\n==== GOLD CONNECTIVITY PROFILE (graph M4d walks) ====", flush=True)
    for r in rows:
        print("  %-26s qids=%d(w/edges=%d) hop1=%2d %s | hop2_reach=%3d (hop2-only=%d)"
              % (r["gold"], r["n_qual_ids"], r["qual_ids_with_edges"], r["hop1_degree"],
                 dict(r["typed"]), r["hop2_reach"], r["hop2_only"]), flush=True)
    print("\n  hop1 degree:  median=%s min=%d max=%d" % (med(h1s), min(h1s), max(h1s)), flush=True)
    print("  hop2 reach:   median=%s min=%d max=%d" % (med(h2s), min(h2s), max(h2s)), flush=True)

    out = {
        "graph": {"relations_files": n_files, "walkable_edges": n_edges,
                  "nodes_with_edges": len(adj), "walk_edges": sorted(WALK_EDGES), "max_hop": MAX_HOP},
        "n_atoms": len(atoms),
        "incoverage_gold": incov_gold,
        "per_gold": rows,
        "agg": {"hop1_median": med(h1s), "hop1_min": min(h1s), "hop1_max": max(h1s),
                "hop2_median": med(h2s), "hop2_min": min(h2s), "hop2_max": max(h2s)},
    }
    outp = DATA_ROOT / "bench_reports" / "gold_connectivity_profile.json"
    outp.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print("\n[written] %s" % outp, flush=True)


if __name__ == "__main__":
    main()
