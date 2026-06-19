"""
exp_substrate_kp_p3_v2_hybrid_criterion_cpu_v1.py -- KP P3-v2: archetype-quotienting with a CRITERION SWITCH (bisimulation | connected_component | hybrid) -- CPU/local (no heat), READ-ONLY.

ROUTING: Research DECISION 12 (RECONFIRM): ship P3-v2 with HYBRID criterion. My KP P3 re-run at SHARES_MATH=18 found bisimulation=0 archetypes
  but 2 size-3 SHARES_MATH connected components -- the bisimulation refinement (behavioral equivalence) is too strict for cross-domain math-
  sharing families. Research: keep BOTH (each is a substrate self-insight); default reporting = hybrid; HARD-PASS bar at SHARES_MATH=332 stays
  BISIMULATION-defined (12 classes). connected-component reported as additional signal at every SHARES_MATH advance.

  CRITERIA:
   connected_component -- SHARES_MATH connected components of size >= MIN_CLASS = archetypes (math-sharing topology; "what families exist").
   bisimulation        -- those components REFINED by behavioral signature (outgoing typed-edge rel_type multiset), Kanellakis-Smolka style;
                          two atoms stay together iff same SHARES_MATH component AND same behavior. Strict "is this REALLY one archetype".
   hybrid (default)    -- report BOTH counts.

PRE-REGISTERED: report both counts at current SHARES_MATH. HARD-PASS (bisimulation criterion) = >= 12 bisimulation archetype classes (the 332-
  scale target). At current scale, expected bisimulation small/0 + connected_component a few; this is a TRACKING instrument (re-runs on each
  SHARES_MATH advance), not a one-shot pass. UNKNOWN if SHARES_MATH < 3 edges. ASCII-only. --self-test + --smoke + metrics.json.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time, json
from collections import defaultdict
from pathlib import Path
from typing import Dict, Tuple, List
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "substrate_kp_p3_v2_hybrid_criterion_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true")
_ap.add_argument("--criterion", default="hybrid", choices=["bisimulation", "connected_component", "hybrid"]); _ARGS, _ = _ap.parse_known_args()
MIN_CLASS = 3; BEHAV_EDGES = {"DEPENDS_ON", "USES", "SPECIALIZES", "INSTANCE_OF"}; HARD_PASS_CLASSES = 12


def _short(x):
    return str(x).split("::")[-1].split("/")[-1].strip().lower()


def connected_components(nodes, adj):
    seen = set(); comps = []
    for n in nodes:
        if n in seen: continue
        stack = [n]; comp = set()
        while stack:
            x = stack.pop()
            if x in seen: continue
            seen.add(x); comp.add(x); stack.extend(adj[x] - seen)
        comps.append(comp)
    return comps


def bisim_refine(comp, behavior):
    """Refine a SHARES_MATH component into behavioral blocks (atoms with identical behavior signature stay together)."""
    blocks = defaultdict(set)
    for a in comp:
        blocks[behavior.get(a, ())].add(a)
    return list(blocks.values())


def _selftest():
    adj = defaultdict(set)
    for a, b in [("x", "y"), ("y", "z")]:
        adj[a].add(b); adj[b].add(a)
    comps = connected_components(["x", "y", "z"], adj)
    assert len(comps) == 1 and len(comps[0]) == 3
    beh = {"x": ("DEPENDS_ON",), "y": ("DEPENDS_ON",), "z": ("USES",)}
    blocks = bisim_refine(comps[0], beh)
    assert sorted(len(b) for b in blocks) == [1, 2]      # x,y together; z split
    print("[selftest] PASS: substrate_kp_p3_v2_hybrid_criterion_cpu_v1", flush=True)


if __name__ == "__main__":
    _selftest()
    if _ARGS.self_test:
        sys.exit(0)


def run() -> Dict:
    root = REPO / "data" / "substrate_index"
    if not root.exists():
        return {"error": "no_substrate_index"}
    sm_adj = defaultdict(set); behavior = defaultdict(list); sm_edges = 0
    for rp in root.rglob("relations.jsonl"):
        try:
            for ln in open(rp, encoding="utf-8"):
                ln = ln.strip()
                if not ln: continue
                try: r = json.loads(ln)
                except Exception: continue
                rt = (r.get("rel_type", "") or "").upper()
                s = _short(r.get("src_id", "")); t = _short(r.get("tgt_id", ""))
                if not (s and t and s != t): continue
                if rt == "SHARES_MATH":
                    sm_adj[s].add(t); sm_adj[t].add(s); sm_edges += 1
                if rt in BEHAV_EDGES:
                    behavior[s].append(rt)
        except Exception:
            continue
    nodes = set(sm_adj.keys())
    if sm_edges < 3:
        return {"error": "too_few_shares_math", "sm_edges": sm_edges}
    beh_sig = {a: tuple(sorted(behavior.get(a, []))) for a in nodes}
    comps = connected_components(nodes, sm_adj)
    cc_classes = [c for c in comps if len(c) >= MIN_CLASS]
    bisim_classes = []
    for c in comps:
        for blk in bisim_refine(c, beh_sig):
            if len(blk) >= MIN_CLASS:
                bisim_classes.append(blk)
    cc_n = len(cc_classes); bis_n = len(bisim_classes)
    print("  SHARES_MATH edges=%d over %d atoms | criterion=%s | MIN_CLASS=%d" % (sm_edges, len(nodes), _ARGS.criterion, MIN_CLASS), flush=True)
    print("  connected_component archetypes (size>=%d): %d %s" % (MIN_CLASS, cc_n, [sorted(c) for c in cc_classes][:4]), flush=True)
    print("  bisimulation archetypes (component + behavioral, size>=%d): %d" % (MIN_CLASS, bis_n), flush=True)
    print("  HARD-PASS bar (bisimulation) = %d classes (at SHARES_MATH~332)" % HARD_PASS_CLASSES, flush=True)
    return {"sm_edges": sm_edges, "n_atoms": len(nodes), "criterion": _ARGS.criterion,
            "connected_component_classes": cc_n, "bisimulation_classes": bis_n,
            "cc_members": [sorted(c) for c in cc_classes][:10], "hard_pass_bar": HARD_PASS_CLASSES}


def verdict(r) -> Tuple[str, str]:
    if r.get("error"):
        return ("UNKNOWN", "UNKNOWN: " + r["error"] + " sm_edges=" + str(r.get("sm_edges", 0)))
    cc = r["connected_component_classes"]; bis = r["bisimulation_classes"]
    s = ("KP P3-v2 hybrid at SHARES_MATH=%d (%d atoms): connected_component archetypes=%d, bisimulation archetypes=%d (HARD-PASS bar=%d bisim "
         "classes at ~332). Both reported (DECISION 12). connected_component = math-sharing families ('what exists'); bisimulation = behavioral-"
         "equivalence-refined ('really one archetype'). cc members: %s.") % (
        r["sm_edges"], r["n_atoms"], cc, bis, r["hard_pass_bar"], r["cc_members"][:3])
    if bis >= HARD_PASS_CLASSES:
        return ("HARD_PASS", "HARD_PASS: %d bisimulation archetype classes >= %d -- SHARES_MATH structure supports archetype quotienting at the "
                "target scale. " % (bis, r["hard_pass_bar"]) + s)
    if cc >= 1 or bis >= 1:
        return ("MIDDLE_BAND", "MIDDLE_BAND (tracking; below 12-class HARD-PASS bar): connected_component=%d archetype(s) exist (math-sharing "
                "families forming) but bisimulation=%d < %d -- cross-domain bridges connect behaviorally-distinct atoms; archetype quotienting "
                "needs more SHARES_MATH density (toward 332) and/or within-family bridges. " % (cc, bis, r["hard_pass_bar"]) + s)
    return ("HARD_FAIL", "HARD_FAIL: 0 archetypes by either criterion at SHARES_MATH=%d. " % r["sm_edges"] + s)


if __name__ == "__main__":
    print("[config] anchor=%s mode=%s criterion=%s" % (ANCHOR_NAME, RUN_MODE, _ARGS.criterion), flush=True)
    out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
    v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
    metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
    write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
