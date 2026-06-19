"""Composed-reasoning A1: multi-hop-provenance cert-check over the materialized typed-edge KG (research hand-off 2026-06-18).

Tests whether the substrate can answer 2-hop reachability queries over its OWN typed-edge graph (the IS_A/HYPERNYM/PART_OF
edges materialized by TRACK-3) via a DETERMINISTIC path-walker, AND whether every returned path is PROVENANCE-SOUND
(each hop is a persisted (src, rel_type, tgt) tuple in the Store -- no hallucinated edge). The substrate-product reading:
a multi-hop-provenance check at the same layer as the 4 live self-cert gates. Deterministic structural check -- NO LLM,
NO RL training (MINERVA is RL; this is the deterministic substrate-product instantiation).

Held-out 2-hop test (built from REAL chains, per rel_type, within-corpus):
  ANSWERABLE: (X, Z) genuinely 2-hop-connected via X -rel-> Y -rel-> Z (same rel_type).
  DISTRACTOR: (X, Z) NOT reachable within max_depth (random Z) -> the walker should REFUSE (no path).
Path-walker: bounded-depth BFS over the Store edges (returns a path or None).
PROVENANCE-VERIFY: every edge in every returned path is in the Store edge-set (0-phantom on paths).

Pre-reg bands (research hand-off):
  HARD_PASS: answer-found >= 0.70 on answerable AND 100% returned-path edges verifiable.
  HARD_FAIL: answer-found < 0.40 OR ANY returned path contains an edge not in the Store.
  MIDDLE_BAND: 0.40 <= answer-found < 0.70 (all edges verifiable).
  NON_TEST: insufficient 2-hop chains to build a powered held-out set.

gate0 + discrimination (answerable AND distractor both present + non-degenerate). CPU/laptop (BFS over ~10k edges).
Deterministic seed. ASCII-only. HDLAB_RUN_MODE smoke|full ; --smoke ; --self-test.
"""
from __future__ import annotations
import argparse
import json
import os
import random
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _cell_provenance import (provenance_fields, now_utc, gate0_self_check, discrimination_self_check,
                              path_provenance_self_check, corpus_completeness_self_check)

ANCHOR = "substrate_a1_multihop_provenance_cpu_v1"
_EXP_NAME = os.environ.get("HDLAB_EXP_NAME")
OUT = REPO / "data" / (f"exp_{_EXP_NAME}" if _EXP_NAME else ANCHOR)
REL_TYPES = ("IS_A", "HYPERNYM", "PART_OF")
MAX_DEPTH = 2
DISTRACTOR_VERIFY_DEPTH = 8   # distractor "no path" verified EXHAUSTIVELY up to this depth (genuinely unreachable, not bounded-give-up)
N_ANSWERABLE_FULL, N_DISTRACTOR_FULL = 300, 300
N_ANSWERABLE_SMOKE, N_DISTRACTOR_SMOKE = 20, 20
SEED = 0
PASS_HI, FAIL_LO = 0.70, 0.40


def build_graph(ps):
    """Directed adjacency over the materialized typed edges + the Store edge-set (for provenance verify).
    Within-corpus local ids; keyed (corpus, local_id). Returns (adj, edge_set, rel_pairs_by_type)."""
    from backend.substrate_index.schema import Corpus
    adj = {}                 # (corpus, src) -> list of (rel, (corpus, tgt))
    edge_set = set()         # (corpus, src, rel, tgt) -- the persisted tuples (provenance referent)
    by_type = {r: [] for r in REL_TYPES}
    for cname, s in ps._stores.items():
        corpus = cname.name if hasattr(cname, "name") else str(cname)
        for (src, rt, tgt) in s._all_relations:
            if rt not in REL_TYPES:
                continue
            edge_set.add((corpus, src, rt, tgt))
            adj.setdefault((corpus, src), []).append((rt, (corpus, tgt)))
            by_type[rt].append((corpus, src, tgt))
    return adj, edge_set, by_type


def two_hop_chains(adj, by_type):
    """All X -rel-> Y -rel-> Z (same rel_type, 2 hops) -> answerable (X,Z) with the via Y."""
    chains = []
    for rt in REL_TYPES:
        for (corpus, x, y) in by_type[rt]:
            for (r2, (c2, z)) in adj.get((corpus, y), []):
                if r2 == rt and z != x:
                    chains.append((corpus, x, y, z, rt))
    return chains


def bfs_path(adj, start, goal, max_depth):
    """Bounded BFS over Store edges. Returns [(corpus,node), (rel,(corpus,node)), ...] path edges or None."""
    if start == goal:
        return []
    frontier = [(start, [])]
    seen = {start}
    for _ in range(max_depth):
        nxt = []
        for node, path in frontier:
            for (rel, tgt) in adj.get(node, []):
                if tgt == goal:
                    return path + [(node, rel, tgt)]
                if tgt not in seen:
                    seen.add(tgt)
                    nxt.append((tgt, path + [(node, rel, tgt)]))
        frontier = nxt
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--full", action="store_true")
    args, _ = ap.parse_known_args()
    is_smoke = args.smoke or (os.environ.get("HDLAB_RUN_MODE", "full") == "smoke" and not args.full)
    run_started_utc = now_utc()
    t0 = time.time()
    rng = random.Random(SEED)

    if args.self_test:
        # tiny synthetic graph: a->b->c (answerable a,c); d isolated (distractor a,d)
        adj = {('x', 'a'): [('IS_A', ('x', 'b'))], ('x', 'b'): [('IS_A', ('x', 'c'))]}
        p = bfs_path(adj, ('x', 'a'), ('x', 'c'), 2); none = bfs_path(adj, ('x', 'a'), ('x', 'd'), 2)
        ok = (p is not None and len(p) == 2 and none is None)
        print(f"[{ANCHOR}] --self-test {'OK' if ok else 'FAIL'} (2-hop path found={p is not None}, distractor refused={none is None}); NO metrics.")
        return 0 if ok else 1

    from backend.substrate_index.partition import PartitionedStore
    ps = PartitionedStore(REPO / "data" / "substrate_index")
    adj, edge_set, by_type = build_graph(ps)
    all_nodes = list({k for k in adj} | {tgt for nbrs in adj.values() for (_, tgt) in nbrs})
    chains = two_hop_chains(adj, by_type)

    n_ans = N_ANSWERABLE_SMOKE if is_smoke else N_ANSWERABLE_FULL
    n_dis = N_DISTRACTOR_SMOKE if is_smoke else N_DISTRACTOR_FULL

    if len(chains) < n_ans or len(all_nodes) < 10:
        metrics = {"anchor_name": ANCHOR, "verdict": "NON_TEST",
                   "verdict_msg": f"NON-TEST: only {len(chains)} 2-hop chains (need >= {n_ans}); insufficient to power the held-out.",
                   "summary": "NON-TEST insufficient 2-hop chains", "n_seeds": 1, "elapsed_s": round(time.time()-t0, 2),
                   **provenance_fields("smoke" if is_smoke else "full", "multihop_provenance", "measured_graph_bfs", run_started_utc)}
        OUT.mkdir(parents=True, exist_ok=True)
        (OUT / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
        print(f"[{ANCHOR}] -> NON_TEST ({len(chains)} chains)"); return 0

    # ANSWERABLE held-out: sample distinct (corpus,x,z) from chains
    rng.shuffle(chains)
    ans = []
    seen_pairs = set()
    for (corpus, x, y, z, rt) in chains:
        key = (corpus, x, z)
        if key in seen_pairs:
            continue
        seen_pairs.add(key); ans.append((corpus, x, z, rt))
        if len(ans) >= n_ans:
            break

    # DISTRACTOR: (corpus,x, random z) NOT reachable within MAX_DEPTH
    node_set = set(all_nodes)
    dis = []
    tries = 0
    while len(dis) < n_dis and tries < n_dis * 50:
        tries += 1
        (corpus, x, z, _rt) = ans[rng.randrange(len(ans))]
        zc, zl = rng.choice(all_nodes)
        if (corpus, x) == (zc, zl):
            continue
        # distractor target must be same corpus (cross-corpus never reachable via these within-corpus edges)
        if zc != corpus:
            continue
        # GENUINELY unreachable (exhaustive up to DISTRACTOR_VERIFY_DEPTH, not bounded-give-up at MAX_DEPTH) -- per
        # Skunkworks cert-condition 3 (corpus-completeness on the no-path claim).
        if bfs_path(adj, (corpus, x), (zc, zl), DISTRACTOR_VERIFY_DEPTH) is None:
            dis.append((corpus, x, zl))

    # RUN the walker + provenance-verify
    found = 0; path_edges_total = 0; path_edges_unverifiable = 0; depths = []
    for (corpus, x, z, _rt) in ans:
        path = bfs_path(adj, (corpus, x), (corpus, z), MAX_DEPTH)
        if path is not None:
            found += 1; depths.append(len(path))
            for (sn, rel, tn) in path:
                path_edges_total += 1
                if (sn[0], sn[1], rel, tn[1]) not in edge_set:   # provenance: hop must be a persisted tuple
                    path_edges_unverifiable += 1
    refused = sum(1 for (corpus, x, z) in dis if bfs_path(adj, (corpus, x), (corpus, z), MAX_DEPTH) is None)

    answer_found = found / len(ans)
    refuse_rate = refused / len(dis) if dis else 1.0
    edge_verifiable = (path_edges_unverifiable == 0)
    discriminates = len(ans) > 0 and len(dis) > 0

    if not discriminates:
        verdict = "NON_TEST"; msg = "NON-TEST: missing answerable or distractor class."
    elif (not edge_verifiable) or answer_found < FAIL_LO:
        verdict = "HARD_FAIL"
        msg = (f"HARD_FAIL: answer_found={answer_found:.3f} (<{FAIL_LO}) OR unverifiable path edges={path_edges_unverifiable} "
               f"(provenance breach). The multi-hop walker is unsound or low-recall.")
    elif answer_found >= PASS_HI and edge_verifiable:
        verdict = "HARD_PASS"
        msg = (f"HARD_PASS: multi-hop-provenance cert-check WORKS: answer_found={answer_found:.3f} (>={PASS_HI}) on the held-out "
               f"2-hop set AND 100% returned-path edges PROVENANCE-VERIFIED (every hop a persisted Store tuple; "
               f"{path_edges_total} path-edges, 0 unverifiable). refuse_rate={refuse_rate:.3f} on distractors. "
               f"Deterministic structural check over the materialized typed-edge KG (within-corpus; measured-bounds, NOT fundamental).")
    else:
        verdict = "MIDDLE_BAND"
        msg = (f"MIDDLE: answer_found={answer_found:.3f} in [{FAIL_LO},{PASS_HI}); all path edges verifiable "
               f"({path_edges_total} edges, 0 unverifiable). Partial multi-hop recall.")

    g0 = gate0_self_check(run_mode=("smoke" if is_smoke else "full"), metrics_source="measured_graph_bfs",
                          n_cells_declared=len(ans) + len(dis), n_cells_emitted=len(ans) + len(dis),
                          elapsed_s=round(time.time()-t0, 2), is_smoke=is_smoke)
    disc = discrimination_self_check(discriminates, answer_found, FAIL_LO, 1.0,
                                     "answerable + distractor both present (multi-hop recall vs refuse discriminates)")
    # 5th self-cert gate (composed-reasoning A1): every returned-path edge is a persisted Store tuple (provenance-sound)
    prov = path_provenance_self_check(found, path_edges_total, path_edges_unverifiable,
                                      "every returned-path hop = a persisted (src, rel_type, tgt) Store tuple (0 hallucinated)")
    # corpus-completeness on the distractor no-path claim (verified EXHAUSTIVELY to DISTRACTOR_VERIFY_DEPTH, not give-up)
    cc = corpus_completeness_self_check("distractor_no_path_reachability", len(dis), len(dis),
                                        f"exhaustive_bfs_depth_{DISTRACTOR_VERIFY_DEPTH}_per_distractor",
                                        "distractors verified genuinely unreachable (exhaustive BFS), not bounded-give-up")

    metrics = {
        "anchor_name": ANCHOR, "verdict": verdict, "verdict_msg": msg, "summary": msg, "headline": msg, "n_seeds": 1,
        **provenance_fields("smoke" if is_smoke else "full", "multihop_provenance_bfs", "measured_graph_bfs", run_started_utc),
        "gate0_self_check": g0, "discrimination_self_check": disc,
        "path_provenance_self_check": prov, "corpus_completeness_self_check": cc,
        "min_cert_along_path": "ontology-INGESTED edge tier (IS_A/HYPERNYM/PART_OF from WordNet/GO; NOT experiment-cert). "
                               "The PATH is provenance-CERT (every edge persisted/sound); the per-answer CLAIM-cert = the "
                               "weakest edge tier = ontology-ingested. The A1 RESULT (answer-rate + 100%-edge-verifiable) is "
                               "the cert-grade EXPERIMENT; per-answer claims carry the min-edge-tier (Skunkworks cert-condition 5).",
        "honest_scope": "provenance-verified multi-hop PATH-FINDING over the materialized within-5k typed-edge backbone "
                        "(IS_A/HYPERNYM/PART_OF); NOT general reasoning / NOT 'the substrate reasons'. ARC-1 T1 "
                        "proof-of-mechanism (narrow, honest-scoped) -- NOT 'ARC 1 shipped'; scale-up awaits USER ratify.",
        "answer_found": round(answer_found, 4), "refuse_rate": round(refuse_rate, 4),
        "path_edges_total": path_edges_total, "path_edges_unverifiable": path_edges_unverifiable,
        "edge_verifiable_100pct": edge_verifiable,
        "n_answerable": len(ans), "n_distractor": len(dis), "n_2hop_chains": len(chains),
        "depth_dist": {str(d): depths.count(d) for d in sorted(set(depths))} if depths else {},
        "rel_types": list(REL_TYPES), "max_depth": MAX_DEPTH,
        "bands": {"hard_pass": PASS_HI, "hard_fail": FAIL_LO},
        "bears_on": "TRACK-3 edge-materialization (IS_A/HYPERNYM/PART_OF); composed-reasoning hand-off A1; 4-gate self-cert engine",
        "measured_bounds": "within-corpus 2-hop reachability over the materialized within-5k typed-edge backbone; deterministic BFS; NOT fundamental",
        "elapsed_s": round(time.time()-t0, 2),
    }
    OUT.mkdir(parents=True, exist_ok=True)
    tmp = OUT / "metrics.json.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2); f.flush(); os.fsync(f.fileno())
    os.replace(tmp, OUT / "metrics.json")
    print(f"[{ANCHOR}] -> {verdict}  answer_found={answer_found:.3f}  refuse={refuse_rate:.3f}  "
          f"edge_verifiable={edge_verifiable} ({path_edges_unverifiable} unverifiable)  gate0={g0['pass']}")
    print(f"  {msg}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
