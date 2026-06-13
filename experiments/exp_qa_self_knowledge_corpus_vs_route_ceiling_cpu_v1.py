"""
exp_qa_self_knowledge_corpus_vs_route_ceiling_cpu_v1.py -- per-axis: is the residual CORPUS-absence (ingest) or ROUTE/SELECTION (fixable)? -- CPU/local.

ROUTING: tests + quantifies the capstone claim that the remaining path-to-0.70 gap is "corpus-bound". For every benchmark
  question with gold, classify each gold item as:
    - ABSENT: gold atom not present in the substrate at all -> needs ATOM ingest (pure corpus gap).
    - PRESENT_UNREACHABLE (B/relation axes): gold atom exists but NO edge connects it to the query target -> needs EDGE ingest.
    - PRESENT_REACHABLE: gold exists (and for relation axes is reachable via an incident edge) -> ROUTE/SELECTION-fixable
      (the gap is retrieval mechanics, not the corpus).
  This converts "corpus-bound" from an assertion into a measured per-axis split (route-fixable vs atom-ingest vs edge-ingest),
  giving Research the exact ingest target list AND honestly bounding how much route headroom remains. NO LLM; PartitionedStore +
  relations + benchmark gold (numpy-free, local-safe).

PRE-REGISTERED (descriptive). Reports per-axis: gold-present-rate, B reachability, and the route-fixable vs ingest split. The
  verdict flags whether the OVERALL residual is majority route-fixable (gold present+reachable -> my "route-exhausted" claim is
  too strong) or majority ingest-bound (gold absent/unreachable -> corpus-bound claim holds). HARD_PASS = clean decisive split.
ASCII-only. CPU/local. --self-test + metrics.json.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time, json
from pathlib import Path
from typing import Dict, Tuple
from collections import defaultdict
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "qa_self_knowledge_corpus_vs_route_ceiling_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
REL_AXES = {"B"}  # relation axes need edge-reachability, not just atom existence
SKIP_AXES = {"D", "F"}  # D = path-existence sentinel gold; F = gap/never-applied meta -> not atom-retrieval


def _norm(x):
    return str(x).split("::")[-1].strip().lower()


def _ids_in(q):
    import re
    return [m.group(0) for m in re.finditer(r"[A-Za-z0-9_]+(?:[-/][A-Za-z0-9_]+)+", q)]


def _selftest():
    assert _norm("concept::T1/X") == "t1/x"
    print("[selftest] PASS: qa_self_knowledge_corpus_vs_route_ceiling_cpu_v1", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run() -> Dict:
    from backend.substrate_index.partition import PartitionedStore
    root = REPO / "data" / "substrate_index"
    if not root.exists():
        return {"error": "no_substrate_index"}
    atoms = PartitionedStore(root).all_atoms()
    all_ids = set(_norm(a.id) for a in atoms)
    rels = []
    for rp in root.rglob("relations.jsonl"):
        for ln in open(rp, encoding="utf-8"):
            ln = ln.strip()
            if ln:
                try: rels.append(json.loads(ln))
                except Exception: pass
    inc = defaultdict(set)
    for r in rels:
        s = _norm(r.get("src_id", "")); t = _norm(r.get("tgt_id", ""))
        if s and t: inc[s].add(t); inc[t].add(s)
    bench = [json.loads(l) for l in open(REPO / "experiments" / "data" / "gap7_benchmark_v1.jsonl", encoding="utf-8") if l.strip()]
    per_axis = defaultdict(lambda: {"q": 0, "gold": 0, "absent": 0, "present_unreachable": 0, "route_fixable": 0})
    for r in bench:
        ax = r.get("type", "A").split("_")[0].upper()
        if ax in ("NEGATIVE", "N") or ax in SKIP_AXES:
            continue
        gold = [_norm(g) for g in (r.get("ground_truth_atoms") or r.get("gold") or [])]
        if not gold:
            continue
        d = per_axis[ax]; d["q"] += 1
        # query target for relation reachability
        tgt = None
        if ax in REL_AXES:
            args = r.get("args") or {}
            tgt = _norm(args.get("target") or "") or (_norm(_ids_in(r.get("question", ""))[-1]) if _ids_in(r.get("question", "")) else None)
        for g in gold:
            d["gold"] += 1
            if g not in all_ids:
                d["absent"] += 1
            elif ax in REL_AXES and tgt and tgt != "*":
                # reachable if g is incident to target OR shares any neighbor edge with target (last-seg tolerant)
                reach = (g in inc.get(tgt, set())) or (tgt in inc.get(g, set()))
                if not reach:
                    # last-segment tolerance: match target by suffix
                    tseg = tgt.split("/")[-1]
                    reach = any(tseg == nb.split("/")[-1] for nb in inc.get(g, set()))
                d["route_fixable" if reach else "present_unreachable"] += 1
            else:
                d["route_fixable"] += 1
    rows = {}
    tot = {"gold": 0, "absent": 0, "present_unreachable": 0, "route_fixable": 0}
    for ax in sorted(per_axis):
        d = per_axis[ax]; g = d["gold"]
        rows[ax] = {"q": d["q"], "gold": g, "absent": d["absent"], "present_unreachable": d["present_unreachable"],
                    "route_fixable": d["route_fixable"],
                    "route_fixable_pct": round(100 * d["route_fixable"] / g, 1),
                    "ingest_needed_pct": round(100 * (d["absent"] + d["present_unreachable"]) / g, 1)}
        for k in tot: tot[k] += d[k]
        print("  %s: %d Qs %d gold -> route-fixable %d (%.0f%%) | atom-absent %d | edge-unreachable %d -> ingest-needed %.0f%%" % (
            ax, d["q"], g, d["route_fixable"], rows[ax]["route_fixable_pct"], d["absent"], d["present_unreachable"], rows[ax]["ingest_needed_pct"]), flush=True)
    rf = round(100 * tot["route_fixable"] / tot["gold"], 1); ing = round(100 * (tot["absent"] + tot["present_unreachable"]) / tot["gold"], 1)
    print("  OVERALL: %d gold (D/F path/meta axes excluded) -> route-fixable %.0f%% | ingest-needed %.0f%% (absent %d + unreachable %d)" % (
        tot["gold"], rf, ing, tot["absent"], tot["present_unreachable"]), flush=True)
    return {"rows": rows, "total": tot, "overall_route_fixable_pct": rf, "overall_ingest_pct": ing}


def verdict(r) -> Tuple[str, str]:
    if r.get("error"): return ("UNKNOWN", "UNKNOWN: " + r["error"])
    rf = r["overall_route_fixable_pct"]; ing = r["overall_ingest_pct"]
    s = "route-fixable=%.0f%% ingest-needed=%.0f%% (atom-absent %d + edge-unreachable %d of %d gold; D/F excluded); per-axis=%s" % (
        rf, ing, r["total"]["absent"], r["total"]["present_unreachable"], r["total"]["gold"],
        {ax: (v["route_fixable_pct"], v["ingest_needed_pct"]) for ax, v in r["rows"].items()})
    if rf >= 60:
        return ("HARD_PASS", "HARD_PASS: the residual is MAJORITY route/selection-fixable (%.0f%% of gold is present + reachable) -- my capstone 'route-mechanics exhausted / corpus-bound' was TOO STRONG. Substantial route headroom remains (gold exists but is not retrieved); only %.0f%% genuinely needs ingest. Honest correction. " % (rf, ing) + s)
    if ing >= 60:
        return ("HARD_PASS", "HARD_PASS: the residual is MAJORITY ingest-bound (%.0f%% of gold is absent/unreachable) -- the corpus-bound capstone holds; route R&D is genuinely near-exhausted. " % ing + s)
    return ("MIDDLE_BAND", "MIDDLE_BAND: residual is a MIX (~%.0f%% route-fixable, ~%.0f%% ingest) -- both levers matter. " % (rf, ing) + s)


print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
