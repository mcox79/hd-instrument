"""
exp_qa_gap4_integration_demo_cpu_v1.py -- Cycle 45 integration DEMO: Testbed Gap-4 router + Exp-Dev route primitives on canonical 60-Q.

ROUTING: Research Cycle 45 Option-3 target (research_to_exp_dev_testbed_BENCHMARK_DIVISION_LABOR). DEMONSTRATES the integrated pipeline
  WITHOUT editing Testbed's router: for each canonical question, call intent_router.route() (NL -> primitive + args; semantic anchor
  resolution + fabricated-qid honesty filter), then dispatch to the IMPLEMENTATIONS -- using Exp-Dev's validated _qa_route_primitives
  for the primitives the router names but doesn't implement (predecessors_via, analogues, bidirectional composition) + existing
  self_knowledge primitives for what_serves/coverage/what_do_you_know_about. Scores the canonical benchmark_corpus_v2_60q.jsonl.
  Quantifies the Cycle-45 absorption lift + surfaces the remaining name->id gap. Pure composition; Testbed does the official wiring.
PRE-REGISTERED (Research Cycle 45): HARD-PASS integrated macro-F1 >= 0.55 (mechanisms absorb). MIDDLE 0.49-0.55. HARD-FAIL <= 0.481
  (no effective absorption). Reports per-axis + the A/G name->id-resolution residual. UNKNOWN if load fails.
ASCII-only. write_metrics. PROT-018 _v1.
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
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
from backend.substrate_index import route_primitives as rp  # canonical (Testbed-moved)
ANCHOR_NAME = "qa_gap4_integration_demo_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"


def _f1(retrieved, gold_present, answerable):
    if not answerable:
        return 1.0 if not retrieved else 0.0
    tp = len(retrieved & gold_present); fp = len(retrieved - gold_present); fn = len(gold_present - retrieved)
    if tp == 0: return 0.0
    p = tp / (tp + fp); r = tp / (tp + fn); return 2 * p * r / (p + r)


def _selftest():
    assert abs(_f1({"x"}, {"x", "y"}, True) - (2 * 1 * 0.5 / 1.5)) < 1e-6
    assert _f1(set(), set(), False) == 1.0
    print("[selftest] PASS: qa-gap4-integration-demo", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def _load_relations(idx_dir):
    rels = []
    for rp_ in idx_dir.rglob("relations.jsonl"):
        for line in open(rp_, encoding="utf-8"):
            line = line.strip()
            if line:
                try: rels.append(json.loads(line))
                except Exception: pass
    return rels


def run() -> Dict:
    from backend.substrate_index.partition import PartitionedStore
    from backend.substrate_index import self_knowledge as sk
    try:
        from backend.substrate_index import intent_router as ir
    except Exception as e:
        print("[router] import fail %s" % str(e)[:100], flush=True); return {"error": "router_import_failed"}
    idx = REPO / "data" / "substrate_index"
    bench_fp = idx / "benchmark_corpus_v2_60q.jsonl"
    if not bench_fp.exists(): return {"error": "no_canonical_benchmark"}
    bench = [json.loads(l) for l in open(bench_fp, encoding="utf-8") if l.strip()]
    pstore = PartitionedStore(idx); atoms = pstore.all_atoms(); relations = _load_relations(idx)
    all_ids = set(rp.norm(a.id) for a in atoms)
    id2corpus = {rp.norm(a.id): str(getattr(a.corpus, "value", a.corpus)).lower() for a in atoms}
    id2qid = {rp.norm(a.id): "%s::%s" % (str(getattr(a.corpus, "value", a.corpus)).lower(), a.id) for a in atoms}
    print("[snapshot] atoms=%d relations=%d canonical_qs=%d" % (len(atoms), len(relations), len(bench)), flush=True)

    def dispatch(prim, args, qtext):
        try:
            if prim == "what_serves":
                return rp.serves(pstore, sk, args.get("capability", ""))
            if prim == "predecessors_via":
                return rp.predecessors_via(relations, args.get("target", ""), args.get("rel_types", ["USES"]), args.get("src_ns"), id2corpus)
            if prim == "supersedes_pairs":
                return rp.predecessors_via(relations, "*", ["SUPERSEDES"])
            if prim == "composition_paths":
                src = id2qid.get(rp.norm(args.get("src", ""))); tgt = id2qid.get(rp.norm(args.get("tgt", "")))
                if src and tgt and rp.composition_reachable(pstore, sk, src, tgt, bidirectional=True): return {"path_exists"}
                return set()
            if prim in ("analogues", "analogues_via_relation_traversal", "pattern_atoms"):
                anc = ir._resolve_anchor(qtext, pstore)
                return rp.analogues_via_relation_traversal(relations, anc) if anc else set()
            if prim == "coverage_report":
                return set()  # F qualitative
            # what_do_you_know_about / default: keyword content over name+aliases
            topic = args.get("topic", qtext).lower()
            kws = [w for w in topic.replace("-", " ").split() if len(w) > 2 and w not in ("about", "the", "what", "atoms", "have", "i", "do")]
            out = set()
            for a in atoms:
                hay = (a.name + " " + " ".join(getattr(a, "aliases", []) or []) + " " + (a.id or "")).lower()
                if args.get("top_k") == 0: break  # honesty filter -> empty
                if any(k in hay for k in kws): out.add(rp.norm(a.id))
            return out
        except Exception:
            return set()

    per_q = []; by_type = {}; name_id_residual = 0
    for q in bench:
        qid = q.get("qid"); qtype = q.get("type", "A"); t = qtype.split("_")[0].upper()
        if t == "NEGATIVE" or t == "N": t = "neg"
        ans = q.get("answerable", True); gold = set(rp.norm(g) for g in (q.get("ground_truth_atoms") or []))
        if t == "D" and ans and not gold: gold = {"path_exists"}
        gold_present = set(g for g in gold if (g in all_ids or g == "path_exists"))
        route = ir.route(q.get("question", ""), pstore)
        retrieved = dispatch(route["primitive"], route.get("args", {}), q.get("question", ""))
        f1 = _f1(retrieved, gold_present, ans)
        # residual: G/A answerable questions that retrieved nothing because anchor/topic didn't resolve
        if t in ("G", "A") and ans and gold_present and not retrieved: name_id_residual += 1
        per_q.append({"id": qid, "type": t, "primitive": route["primitive"], "f1": round(f1, 3)})
        by_type.setdefault(t, []).append(f1)
    macro = sum(p["f1"] for p in per_q) / len(per_q)
    type_f1 = {k: round(sum(v) / len(v), 3) for k, v in by_type.items()}
    print("  INTEGRATED macro-F1 = %.4f (n=%d) | per-type: %s" % (macro, len(per_q), type_f1), flush=True)
    print("  name->id-resolution residual (A/G answerable, retrieved empty): %d" % name_id_residual, flush=True)
    return {"f1": round(macro, 4), "macro_f1": round(macro, 4), "type_f1": type_f1, "n_qs": len(per_q),
            "name_id_residual": name_id_residual, "baseline_router_only": 0.481}


def verdict(r) -> Tuple[str, str]:
    if r.get("error"): return ("UNKNOWN", "UNKNOWN: " + r["error"])
    m = r["macro_f1"]; s = "integrated macro-F1=%.4f (n=%d, per-type %s, name->id residual=%d, vs router-only 0.481)" % (
        m, r["n_qs"], r["type_f1"], r["name_id_residual"])
    if m >= 0.55:
        return ("HARD_PASS", "HARD_PASS: Gap-4 router + Exp-Dev primitives integrated >=0.55 -- mechanism absorption lifts canonical. " + s)
    if m >= 0.49:
        return ("MIDDLE_BAND", "MIDDLE_BAND: integrated 0.49-0.55 -- partial absorption; A/G name->id resolution is the residual gap. " + s)
    return ("HARD_FAIL", "HARD_FAIL: integrated <=0.481 -- no effective absorption (likely name->id anchor resolution blocking B/G). " + s)


print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
