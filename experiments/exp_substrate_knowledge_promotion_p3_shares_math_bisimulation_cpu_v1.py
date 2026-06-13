"""
exp_substrate_knowledge_promotion_p3_shares_math_bisimulation_cpu_v1.py -- CELL KP path P3: SHARES_MATH bisimulation -> T2 archetypes -- CPU/local (no heat, read-only).

ROUTING: Research handoff ANCHOR 1 (knowledge-promotion operator) path P3 + MASTER-PLAN Phase 3 E3.1. The KP operator has 5 substrate-only
  paths; P1 (frequency) and P4 (sleep-replay geometry) already HARD_PASS. This is path P3 (SHARES_MATH bisimulation): atoms that are
  BISIMILAR under the SHARES_MATH relation (they share the same underlying mathematics AND have matching typed-dependency structure) form
  an equivalence class whose common math is a candidate consolidated T2 ARCHETYPE; the class members become INSTANCE_OF it. This is
  mechanistically INDEPENDENT of P1 (graph in-degree) and P4 (codebook geometry): it uses the coarsest-bisimulation QUOTIENT over the
  independently-authored SHARES_MATH structural edges -- NOT the P4 geometry (which would be circular). READ-ONLY: identifies archetype
  classes (Testbed creates the T2 + re-parents + benchmark-validates). NO LLM; pure typed-graph partition refinement; numpy-free; no heat.

  GATE: SHARES_MATH edges are currently 0 in the corpus (Testbed T1.4 authors them from the 6 P4 clusters: distance-metric trio,
  DP-parsing sextet, numerical-LA quartet, optimization heptet + 2 broad clusters). Until then this cell returns UNKNOWN (gated) by
  design -- it is BUILT + algorithm-VERIFIED now (self-test validates the bisimulation on synthetic graphs) so it runs with zero latency
  the moment edges land. This is exactly-in-time prep, not building-ahead (need is endorsed; edges are actively being authored).

  ALGORITHM: coarsest relational bisimulation (Kanellakis-Smolka partition refinement). Two atoms are equivalent iff, for every relation
  type rt, the SET of partition-blocks reachable via rt is identical -- iterated to fixpoint. Driven by the SHARES_MATH-relevant subgraph
  (atoms touching >=1 SHARES_MATH edge) over typed edges {SHARES_MATH, DEPENDS_ON, USES}. A block of size >= MIN_CLASS whose members are
  SHARES_MATH-connected is a candidate T2 archetype.

PRE-REGISTERED (Research KPI #2): HARD-PASS >= 10 bisimulation equivalence classes of size >= MIN_CLASS (=3), each a well-formed
  SHARES_MATH-connected archetype candidate (the 90pct hand-verified-precision check is a downstream Testbed/human step). MIDDLE 3-9.
  HARD-FAIL 0-2 (bisimulation does not yield archetype classes -> P3 inactive even with edges). UNKNOWN if SHARES_MATH edges = 0 (GATED).
ASCII-only. CPU/local. --self-test + --smoke + metrics.json.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time, json
from collections import defaultdict, Counter
from pathlib import Path
from typing import Dict, Tuple, List
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "substrate_knowledge_promotion_p3_shares_math_bisimulation_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SIG_EDGES = {"SHARES_MATH", "DEPENDS_ON", "USES"}; MIN_CLASS = 3


def _norm(x):
    return str(x).split("::")[-1].strip()


def coarsest_bisimulation(nodes: List[str], out_edges: Dict[str, set]) -> Dict[str, int]:
    """Kanellakis-Smolka partition refinement to the coarsest bisimulation. out_edges[n] = set of (rel_type, succ)."""
    block = {n: 0 for n in nodes}
    while True:
        sig = {}
        for n in nodes:
            sig[n] = frozenset((rt, block[s]) for (rt, s) in out_edges.get(n, ()) if s in block)
        keys: Dict[Tuple[int, frozenset], int] = {}
        newblock = {}
        for n in nodes:
            k = (block[n], sig[n])
            newblock[n] = keys.setdefault(k, len(keys))
        if len(set(newblock.values())) == len(set(block.values())):
            return newblock                       # fixpoint: block count stable
        block = newblock


def shares_math_components(nodes: List[str], sm_adj: Dict[str, set]) -> Dict[str, int]:
    """Connected components over the (symmetric) SHARES_MATH graph -- the 'shares the same math' groups."""
    comp = {}; cid = 0
    for start in nodes:
        if start in comp:
            continue
        seen = {start}; stack = [start]
        while stack:
            u = stack.pop()
            for v in sm_adj.get(u, ()):
                if v not in seen:
                    seen.add(v); stack.append(v)
        for n in seen:
            comp[n] = cid
        cid += 1
    return comp


def classes_from(nodes, out_edges, sm_adj, min_class):
    # an archetype class = a SHARES_MATH connected component (shares math, transitively) REFINED by the coarsest
    # bisimulation block (so a large heterogeneous component splits into structurally-distinct sub-archetypes).
    comp = shares_math_components(nodes, sm_adj)
    block = coarsest_bisimulation(nodes, out_edges)
    grp = defaultdict(list)
    for n in nodes:
        grp[(comp[n], block[n])].append(n)
    out = [sorted(m) for m in grp.values() if len(m) >= min_class]
    out.sort(key=lambda c: -len(c))
    return out


def _selftest():
    # synthetic: two structurally-identical SHARES_MATH triangles {a1,a2,a3} and {b1,b2,b3} each linked to a shared axiom of its own type;
    # plus 2 singletons. Coarsest bisimulation must yield exactly 2 size>=3 SHARES_MATH-connected classes.
    def tri(p):
        nodes = [p + "1", p + "2", p + "3"]
        oe = defaultdict(set); sm = defaultdict(set)
        for i in range(3):
            for j in range(3):
                if i != j:
                    oe[nodes[i]].add(("SHARES_MATH", nodes[j])); sm[nodes[i]].add(nodes[j])
            oe[nodes[i]].add(("DEPENDS_ON", p + "_ax"))
        return nodes, oe, sm
    na, oea, sma = tri("a"); nb, oeb, smb = tri("b")
    nodes = na + nb + ["s1", "s2"]
    oe = defaultdict(set); sm = defaultdict(set)
    for d in (oea, oeb):
        for k, v in d.items(): oe[k] |= v
    for d in (sma, smb):
        for k, v in d.items(): sm[k] |= v
    oe["s1"].add(("DEPENDS_ON", "a_ax")); oe["s2"].add(("USES", "b_ax"))     # singletons: distinct sigs, no SHARES_MATH
    cls = classes_from(nodes, oe, sm, 3)
    assert len(cls) == 2, (len(cls), cls)
    assert all(len(c) == 3 for c in cls)
    # the two triangles are DISTINCT SHARES_MATH components (a's not linked to b's) -> 2 classes, NOT merged into one of 6
    # (note: pure bisimulation alone WOULD merge them -- a_ax/b_ax are indistinguishable sinks -- which is why grouping is component-refined-by-bisim)
    assert {tuple(c) for c in cls} == {("a1", "a2", "a3"), ("b1", "b2", "b3")}, cls
    # bisimulation identifies structural twins: two nodes with identical typed successors share a block
    bl = coarsest_bisimulation(["x", "y", "z"], {"x": {("USES", "z")}, "y": {("USES", "z")}, "z": set()})
    assert bl["x"] == bl["y"] and bl["x"] != bl["z"]
    print("[selftest] PASS: substrate_knowledge_promotion_p3_shares_math_bisimulation_cpu_v1 (bisimulation refinement validated on synthetic)", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run() -> Dict:
    root = REPO / "data" / "substrate_index"
    if not root.exists():
        return {"error": "no_substrate_index"}
    out_edges = defaultdict(set); sm_adj = defaultdict(set); sm_count = 0; sm_nodes = set()
    for rp in root.rglob("relations.jsonl"):
        for ln in open(rp, encoding="utf-8"):
            ln = ln.strip()
            if not ln: continue
            try: r = json.loads(ln)
            except Exception: continue
            rt = (r.get("rel_type", "") or "").upper()
            s = _norm(r.get("src_id", "")); t = _norm(r.get("tgt_id", ""))
            if not (s and t and s != t): continue
            if rt in SIG_EDGES:
                out_edges[s].add((rt, t))
            if rt == "SHARES_MATH":
                sm_count += 1; sm_adj[s].add(t); sm_adj[t].add(s); sm_nodes.add(s); sm_nodes.add(t)
                out_edges[t].add(("SHARES_MATH", s))      # SHARES_MATH is symmetric
    if sm_count == 0:
        return {"error": "shares_math_edges_absent", "gate": "Testbed T1.4 authors SHARES_MATH from P4 clusters", "sm_count": 0}
    nodes = sorted(sm_nodes)                                # bisimulation over the SHARES_MATH-relevant subgraph
    classes = classes_from(nodes, out_edges, sm_adj, MIN_CLASS)
    sizes = [len(c) for c in classes]
    print("  SHARES_MATH edges=%d over %d atoms; bisimulation -> %d archetype classes (size>=%d); sizes=%s" % (
        sm_count, len(nodes), len(classes), MIN_CLASS, sorted(sizes, reverse=True)[:12]), flush=True)
    for c in classes[:12]:
        print("    ARCHETYPE-CLASS size=%2d :: %s" % (len(c), c[:6]), flush=True)
    bf = root / "bench_reports"; bf.mkdir(parents=True, exist_ok=True)
    (bf / "kp_p3_shares_math_bisimulation_classes.json").write_text(json.dumps(
        {"classes": classes, "sm_edges": sm_count, "n_sm_nodes": len(nodes), "min_class": MIN_CLASS}, indent=2), encoding="utf-8")
    return {"sm_edges": sm_count, "n_sm_nodes": len(nodes), "n_classes": len(classes),
            "class_sizes": sorted(sizes, reverse=True), "classes": classes[:20]}


def verdict(r) -> Tuple[str, str]:
    if r.get("error") == "shares_math_edges_absent":
        return ("UNKNOWN", "UNKNOWN (GATED): SHARES_MATH edges = 0; %s. Cell is built + bisimulation-algorithm self-test-VERIFIED; runs for real the moment edges land." % r["gate"])
    if r.get("error"):
        return ("UNKNOWN", "UNKNOWN: " + r["error"])
    n = r["n_classes"]
    s = "P3 bisimulation: %d archetype classes size>=%d over %d SHARES_MATH atoms (%d edges); sizes=%s; saved bench_reports/kp_p3_shares_math_bisimulation_classes.json (READ-ONLY -- Testbed creates T2 + re-parents)" % (
        n, MIN_CLASS, r["n_sm_nodes"], r["sm_edges"], r["class_sizes"][:12])
    if n >= 10:
        return ("HARD_PASS", "HARD_PASS: SHARES_MATH bisimulation yields %d >= 10 equivalence classes -- a 3rd INDEPENDENT promotion mechanism (structural quotient, not P1 frequency nor P4 geometry). Aggregate KP operator now >=3-of-5. " % n + s)
    if n >= 3:
        return ("MIDDLE_BAND", "MIDDLE_BAND: %d bisimulation classes (3-9) -- mechanism works but the SHARES_MATH graph is still thin; more authored edges -> more classes. " % n + s)
    return ("HARD_FAIL", "HARD_FAIL: only %d bisimulation classes -- SHARES_MATH structure does not yet support archetype quotienting. " % n + s)


print("[config] anchor=%s mode=%s sig_edges=%s min_class=%d" % (ANCHOR_NAME, RUN_MODE, sorted(SIG_EDGES), MIN_CLASS), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
