"""
exp_qa_self_knowledge_cpu_v1.py -- substrate-self-knowledge QA evaluation (Gap 7 benchmark) -- CPU.

ROUTING: Research APPROVED + scoring spec (research_to_exp_dev_QA_CELL_SCORING_SPEC_2026-06-12). Measure whether the substrate can
  answer questions about its OWN knowledge via self_knowledge.py primitives, scored substrate-only (NO LLM-judge). Snapshot the live
  substrate_index (read-only; avoids racing Testbed evolve writes), hard-route each benchmark question by type to a query, score
  per-question F1 (TP/FN/FP) on the gold-present-in-snapshot subset (report attrition), aggregate macro-F1 + per-type breakdown.
  V1 SCOPE: first batch Q1-Q12 (types A content / B relation / C capability) to VALIDATE the pipeline end-to-end; benchmark JSONL is
  data-driven (expand to 60 + types D/E/F/G by adding rows + routes). Routes: A=keyword retrieval over name/aliases; B=typed-relation
  filter; C=what_serves(serves_capability). qid reconcile: match on id-part (strip corpus:: prefix).
PRE-REGISTERED (Drill 4; per spec, on the implemented subset): HARD-PASS macro-F1 >= 0.50. MIDDLE 0.30-0.50. HARD-FAIL <= 0.30.
  DECISIVE-PATH-TO-0.70 >= 0.60. UNKNOWN if store/benchmark load fails. (V1 = first measurement on Q1-Q12; not the full-60 HP_v1.)
ASCII-only. write_metrics. PROT-018 _v1.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time, json, shutil, tempfile
from pathlib import Path
from typing import Dict, Tuple, List
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "qa_self_knowledge_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
STOP = {"about", "the", "a", "an", "of", "do", "i", "have", "what", "atoms", "specifically", "network"}


def _norm(qid):
    """qid id-part: strip corpus:: prefix; lowercased for robust match."""
    s = qid.split("::", 1)[1] if "::" in qid else qid
    return s.strip().lower()


def _f1(retrieved, gold_present, answerable):
    if not answerable:  # gold empty -> correct refusal
        return (1.0 if not retrieved else 0.0), 0, len(retrieved), 0
    tp = len(retrieved & gold_present); fp = len(retrieved - gold_present); fn = len(gold_present - retrieved)
    if tp == 0: return 0.0, tp, fp, fn
    p = tp / (tp + fp); r = tp / (tp + fn)
    return (2 * p * r / (p + r)), tp, fp, fn


# ---------- routes ----------
def route_A(atoms, args):
    topic = args["topic"].lower(); kws = [w for w in topic.replace("-", " ").split() if w not in STOP and len(w) > 2]
    out = set()
    for a in atoms:
        hay = (a.name + " " + " ".join(getattr(a, "aliases", []) or []) + " " + (a.id or "")).lower()
        if any(k in hay for k in kws): out.add(_norm(a.id))
    return out


# benchmark rel_type -> substrate's actual edge vocabulary (substrate uses DEPENDS_ON/USES/RELATES/INSTANCE_OF,
# NOT the benchmark's DECOMPOSES_TO/USED_FOR_LIFT). v1 semantic mapping (Gap: substrate lacks these exact edge types).
REL_MAP = {"DECOMPOSES_TO": {"DEPENDS_ON", "USES"}, "USES": {"USES", "DEPENDS_ON"}, "INSTANCE_OF": {"INSTANCE_OF", "SPECIALIZES"},
           "USED_FOR_LIFT": {"USES", "RELATES"}}


def route_B(relations, args):
    rt = args["rel_type"].upper(); tgt = _norm(args["target"]); direction = args.get("direction", "in")
    accept = REL_MAP.get(rt, {rt})
    out = set()
    for r in relations:
        if r.get("rel_type", "").upper() not in accept: continue
        s = _norm(r["src_id"]); t = _norm(r["tgt_id"])
        if t == tgt: out.add(s)
        if direction == "out" and s == tgt: out.add(t)
    return out


def route_C(pstore, sk, args):
    try:
        res = sk.what_serves(pstore, args["capability"])
        return set(_norm(a.id) for a in res)
    except Exception:
        return set()


def _selftest():
    assert _norm("math::T2/fhrr_bind") == "t2/fhrr_bind"
    assert _norm("PHYS/random_matrix_theory") == "phys/random_matrix_theory"
    f, tp, fp, fn = _f1(set(), set(), answerable=False); assert f == 1.0  # correct refusal
    f2, *_ = _f1({"x"}, {"x", "y"}, answerable=True); assert abs(f2 - (2 * 1 * 0.5 / 1.5)) < 1e-6
    print("[selftest] PASS: qa-self-knowledge", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def _snapshot_index():
    src = REPO / "data" / "substrate_index"
    if not src.exists(): return None
    snap = Path(tempfile.mkdtemp(prefix="subidx_snap_"))
    dst = snap / "substrate_index"
    shutil.copytree(src, dst, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    return dst


def _load_relations(idx_dir):
    rels = []
    for rp in idx_dir.rglob("relations.jsonl"):
        for line in open(rp, encoding="utf-8"):
            line = line.strip()
            if line:
                try: rels.append(json.loads(line))
                except Exception: pass
    return rels


def run() -> Dict:
    from backend.substrate_index.partition import PartitionedStore
    from backend.substrate_index import self_knowledge as sk
    bench_fp = REPO / "experiments" / "data" / "gap7_benchmark_v1.jsonl"
    try:
        bench = [json.loads(l) for l in open(bench_fp, encoding="utf-8") if l.strip()]
        idx_dir = _snapshot_index()
        if idx_dir is None: return {"error": "no_substrate_index"}
        pstore = PartitionedStore(idx_dir)
        atoms = pstore.all_atoms(); relations = _load_relations(idx_dir)
    except Exception as e:
        print("[load] fail %s" % str(e)[:120], flush=True); return {"error": "load_failed"}
    all_ids = set(_norm(a.id) for a in atoms)
    print("[snapshot] atoms=%d relations=%d benchmark_qs=%d" % (len(atoms), len(relations), len(bench)), flush=True)
    per_q = []; by_type = {}
    for q in bench:
        t = q["type"]; ans = q.get("answerable", True)
        gold = set(_norm(g) for g in q.get("gold", []))
        gold_present = set(g for g in gold if g in all_ids)
        attrition = len(gold) - len(gold_present)
        if t == "A": retrieved = route_A(atoms, q["args"])
        elif t == "B": retrieved = route_B(relations, q["args"])
        elif t == "C": retrieved = route_C(pstore, sk, q["args"])
        else: retrieved = set()
        f1, tp, fp, fn = _f1(retrieved, gold_present, ans)
        per_q.append({"id": q["id"], "type": t, "f1": round(f1, 4), "tp": tp, "fp": fp, "fn": fn,
                      "gold_present": len(gold_present), "gold_attrition": attrition, "answerable": ans})
        by_type.setdefault(t, []).append(f1)
        print("  %s [%s] F1=%.3f (tp=%d fp=%d fn=%d gold_present=%d attrition=%d)" % (q["id"], t, f1, tp, fp, fn, len(gold_present), attrition), flush=True)
    macro = sum(p["f1"] for p in per_q) / len(per_q)
    type_f1 = {t: round(sum(v) / len(v), 4) for t, v in by_type.items()}
    worst = sorted(per_q, key=lambda p: p["f1"])[:3]
    print("  MACRO-F1 = %.4f (n=%d Qs) | per-type: %s" % (macro, len(per_q), type_f1), flush=True)
    print("  worst-3: %s" % [(p["id"], p["f1"]) for p in worst], flush=True)
    total_attr = sum(p["gold_attrition"] for p in per_q)
    return {"f1": round(macro, 4), "macro_f1": round(macro, 4), "type_f1": type_f1, "n_qs": len(per_q),
            "total_gold_attrition": total_attr, "per_q": per_q}


def verdict(r) -> Tuple[str, str]:
    if r.get("error"): return ("UNKNOWN", "UNKNOWN: " + r["error"])
    m = r["macro_f1"]; s = "macro-F1=%.4f (n=%d Qs, per-type %s, gold-attrition=%d) -- V1 pipeline on Q1-Q12 (A/B/C); expand to 60+D/E/F/G" % (
        m, r["n_qs"], r["type_f1"], r["total_gold_attrition"])
    if m >= 0.60:
        return ("HARD_PASS", "HARD_PASS: substrate-self-knowledge QA macro-F1 >=0.60 -- DECISIVE-PATH-TO-0.70; substrate knows its own knowledge (V1 subset). " + s)
    if m >= 0.50:
        return ("HARD_PASS", "HARD_PASS: substrate-self-knowledge QA macro-F1 >=0.50 (substantial over 0.30 baseline; Tier-B). " + s)
    if m >= 0.30:
        return ("MIDDLE_BAND", "MIDDLE_BAND: macro-F1 0.30-0.50 -- moderate; hard-route + keyword retrieval v1 (Gap 4 intent router would lift). " + s)
    return ("HARD_FAIL", "HARD_FAIL: macro-F1 <=0.30 -- no progress over baseline. " + s)


print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
