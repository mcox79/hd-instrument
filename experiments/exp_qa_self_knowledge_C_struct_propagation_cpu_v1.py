"""
exp_qa_self_knowledge_C_struct_propagation_cpu_v1.py -- structural-propagation C-route: recover serves_capability-sparse gold via the relation graph (no bge) -- CPU/local.

ROUTING: bge C-route FAILED (C-gold is functional, not topical). But C-gold IS graph-connected: a connectivity probe showed
  1-hop propagation from the serves_capability seed (cap atom + atoms serving cap) recovers additional gold for 8/9 C-Qs (only
  Q44 spectral_observability is an isolated cap, truly authoring-bound). This cell measures the F1 of a STRUCTURAL-propagation
  C-route: seed = what_serves(cap); expand 1-hop along the relation graph (all edges, or DEPENDS_ON/INSTANCE_OF/USES-only for
  precision). Tests whether propagation's RECALL gains survive PRECISION cost -> a non-bge, non-authoring C-axis lever. NO LLM;
  PartitionedStore + relations + serves_capability (numpy-free, local-safe).

PRE-REGISTERED: HARD-PASS best propagation policy C-F1 >= prod(what_serves) + 0.05. MIDDLE +0.02..0.05. HARD-FAIL <=+0.02
  (propagation's precision cost cancels the recall gain -> C stays serves_capability-backfill-bound). UNKNOWN if store missing.
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
ANCHOR_NAME = "qa_self_knowledge_C_struct_propagation_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
DEP_RELS = {"DEPENDS_ON", "INSTANCE_OF", "USES", "SPECIALIZES", "DEFINED_OVER"}


def _norm(x):
    return str(x).split("::")[-1].strip().lower()


def _f1(retrieved, gold):
    if not gold:
        return 1.0 if not retrieved else 0.0
    tp = len(retrieved & gold); fp = len(retrieved - gold); fn = len(gold - retrieved)
    p = tp / (tp + fp + 1e-9); r = tp / (tp + fn + 1e-9)
    return 2 * p * r / (p + r + 1e-9)


def _selftest():
    assert abs(_f1({"a", "b"}, {"a", "b", "c"}) - 0.8) < 1e-6
    print("[selftest] PASS: qa_self_knowledge_C_struct_propagation_cpu_v1", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run() -> Dict:
    from backend.substrate_index.partition import PartitionedStore
    from backend.substrate_index import self_knowledge as sk
    root = REPO / "data" / "substrate_index"
    if not root.exists():
        return {"error": "no_substrate_index"}
    pstore = PartitionedStore(root); atoms = pstore.all_atoms()
    # adjacency (bidirectional) all-edges + dep-only
    adj_all = defaultdict(set); adj_dep = defaultdict(set)
    for rp in root.rglob("relations.jsonl"):
        for ln in open(rp, encoding="utf-8"):
            ln = ln.strip()
            if not ln: continue
            try: r = json.loads(ln)
            except Exception: continue
            s = _norm(r.get("src_id", "")); t = _norm(r.get("tgt_id", "")); rt = (r.get("rel_type", "") or "").upper()
            if s and t:
                adj_all[s].add(t); adj_all[t].add(s)
                if rt in DEP_RELS: adj_dep[s].add(t); adj_dep[t].add(s)
    bench = [json.loads(l) for l in open(REPO / "experiments" / "data" / "gap7_benchmark_v1.jsonl", encoding="utf-8") if l.strip()]
    cqs = [r for r in bench if r.get("type", "A").split("_")[0].upper() == "C" and (r.get("ground_truth_atoms") or r.get("gold"))]
    policies = ["prod_what_serves", "prop_all_1hop", "prop_dep_1hop", "prop_dep_1hop_seed_only_expand"]
    agg = {p: [] for p in policies}
    for r in cqs:
        cap = (r.get("args") or {}).get("capability", "")
        gold = set(_norm(g) for g in (r.get("ground_truth_atoms") or r.get("gold") or []))
        try:
            seed = set(_norm(a.id) for a in sk.what_serves(pstore, cap))
        except Exception:
            seed = set()
        seed_plus_cap = set(seed) | {_norm(cap)}
        def expand(seedset, adj):
            out = set(seedset)
            for s in seedset:
                out |= adj.get(s, set())
            return out
        ret = {
            "prod_what_serves": seed,
            "prop_all_1hop": expand(seed_plus_cap, adj_all),
            "prop_dep_1hop": expand(seed_plus_cap, adj_dep),
            "prop_dep_1hop_seed_only_expand": expand(seed if seed else {_norm(cap)}, adj_dep),
        }
        for p in policies:
            agg[p].append(_f1(ret[p], gold))
    macro = {p: round(sum(v) / len(v), 4) for p, v in agg.items()}
    prod = macro["prod_what_serves"]
    best_p = max((p for p in macro if p != "prod_what_serves"), key=lambda p: macro[p])
    best = macro[best_p]
    print("  C-F1 by policy (n=%d):" % len(cqs), flush=True)
    for p in policies:
        print("    %-32s %.4f%s" % (p, macro[p], "  <-- production" if p == "prod_what_serves" else ""), flush=True)
    print("  best non-prod = %s (%.4f); production = %.4f; delta = %+.4f" % (best_p, best, prod, best - prod), flush=True)
    return {"n": len(cqs), "macro_by_policy": macro, "prod_C_f1": prod, "best_policy": best_p, "best_C_f1": best, "delta": round(best - prod, 4)}


def verdict(r) -> Tuple[str, str]:
    if r.get("error"): return ("UNKNOWN", "UNKNOWN: " + r["error"])
    d = r["delta"]; s = "best=%s C-F1=%.4f vs prod %.4f (delta %+.4f); all=%s; n=%d" % (
        r["best_policy"], r["best_C_f1"], r["prod_C_f1"], d, r["macro_by_policy"], r["n"])
    if d >= 0.05:
        return ("HARD_PASS", "HARD_PASS: structural 1-hop propagation along the relation graph BEATS what_serves by >=0.05 C-F1 -- a non-bge, non-authoring C-axis lever. serves_capability sparsity is recoverable from existing DEPENDS_ON/INSTANCE_OF edges. " + s)
    if d >= 0.02:
        return ("MIDDLE_BAND", "MIDDLE_BAND: propagation gives a small C-F1 lift (+0.02..0.05) -- partial recovery; precision cost eats some of the recall gain. " + s)
    return ("HARD_FAIL", "HARD_FAIL: propagation does not beat what_serves by >0.02 -- the 1-hop recall gain is cancelled by precision loss; C stays serves_capability-backfill-bound. " + s)


print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
