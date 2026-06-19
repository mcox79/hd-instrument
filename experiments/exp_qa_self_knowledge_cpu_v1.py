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


def route_B(relations, args, id2corpus):
    """Per-Research: align to substrate's actual rel vocab (per-question rel_types) + precision filter (src namespace)."""
    accept = {x.upper() for x in args["rel_types"]}; tgt = _norm(args["target"]); src_ns = args.get("src_ns")
    wild = (tgt == "*")
    out = set()
    for r in relations:
        if r.get("rel_type", "").upper() not in accept: continue
        s = _norm(r["src_id"]); t = _norm(r["tgt_id"])
        if wild or t == tgt:
            if src_ns and id2corpus.get(s) not in src_ns: continue  # precision: source namespace filter
            out.add(s)
    return out


def route_C(pstore, sk, args):
    try:
        return set(_norm(a.id) for a in sk.what_serves(pstore, args["capability"]))
    except Exception:
        return set()


def route_D(pstore, sk, args, id2qid):
    """composition relationship existence (direction-agnostic: substrate dependency edges point capability->primitive,
    so a primitive->capability question must also try the reverse) -> {path_exists} if reachable either way."""
    src = id2qid.get(_norm(args["src"])); tgt = id2qid.get(_norm(args["tgt"]))
    if not src or not tgt: return set()
    try:
        fwd = sk.composition_paths(pstore, src, tgt, max_depth=5)
        rev = sk.composition_paths(pstore, tgt, src, max_depth=5) if not fwd else None
        return {"path_exists"} if (fwd or rev) else set()
    except Exception:
        return set()


def route_E(atoms, args):
    """methodology rules: META-partition atoms whose text matches the scenario keywords."""
    kws = [w for w in args["scenario"].lower().split() if len(w) > 2 and w not in STOP]
    out = set()
    for a in atoms:
        if str(getattr(a.corpus, "value", a.corpus)).lower() not in ("meta", "methodology"): continue
        hay = (a.name + " " + (a.id or "") + " " + " ".join(getattr(a, "aliases", []) or []) + " " + (getattr(a, "description", "") or "")).lower()
        if sum(1 for k in kws if k in hay) >= 2: out.add(_norm(a.id))
    return out


def route_F(pstore, atoms, args):
    """gap: 'primitives never applied' = math T1/T2 atoms with empty serves_capability. (Other gap Qs are qualitative
    future-work -> route returns empty = honest 'no such present atoms'.)"""
    if args.get("mode") == "never_applied":
        out = set()
        for a in atoms:
            corp = str(getattr(a.corpus, "value", a.corpus)).lower()
            tier = str(getattr(a.tier, "value", a.tier))
            if corp == "math" and tier in ("T1", "T2") and not getattr(a, "serves_capability", None):
                out.add(_norm(a.id))
        return out
    return set()


ANALOGUE_EDGES = {"RELATES", "GROUNDS", "INSTANTIATES", "ANALOGOUS_TO", "ANALOG_OF", "DUAL", "BIOLOGICAL_INSPIRATION_FOR", "INFLUENCED_BY", "GENERALIZES", "SPECIALIZES"}


def route_G(atoms, relations, args):
    """pattern/analogue: RELATION traversal from an anchor over analogue-type edges (the substrate encodes cross-disc analogues as
    edges, NOT keywords -- ready for the cross-disc GROUNDS/INSTANTIATES batch). Fallback: META-restricted keyword for rule-pattern Qs."""
    anchor = _norm(args.get("anchor", ""))
    if anchor:
        out = set()
        for r in relations:
            if r.get("rel_type", "").upper() not in ANALOGUE_EDGES: continue
            s = _norm(r["src_id"]); t = _norm(r["tgt_id"])
            if s == anchor: out.add(t)
            if t == anchor: out.add(s)
        return out
    # rule-pattern: precise META-restricted keyword (avoids the keyword over-retrieval that tanked precision)
    kws = [w for w in args.get("topic", "").lower().split() if len(w) > 2 and w not in STOP]
    out = set()
    for a in atoms:
        if str(getattr(a.corpus, "value", a.corpus)).lower() not in ("meta", "methodology"): continue
        hay = (a.name + " " + (a.id or "") + " " + (getattr(a, "description", "") or "")).lower()
        if sum(1 for k in kws if k in hay) >= 2: out.add(_norm(a.id))
    return out


def _selftest():
    assert _norm("math::T2/fhrr_bind") == "t2/fhrr_bind"
    assert _norm("PHYS/random_matrix_theory") == "phys/random_matrix_theory"
    f, tp, fp, fn = _f1(set(), set(), answerable=False); assert f == 1.0  # correct refusal
    f2, *_ = _f1({"x"}, {"x", "y"}, answerable=True); assert abs(f2 - (2 * 1 * 0.5 / 1.5)) < 1e-6
    print("[selftest] PASS: qa-self-knowledge", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


import re as _re
_IDPAT = _re.compile(r"(?:[a-z]+::)?(?:T\d/[\w]+|PP-\d+[\w]*|CAP_[\w]+|RULE_[\w]+|SCHOOL/[\w]+|[A-Z]{2,}/[\w]+|[\w]+_family)")


def _ids_in(q):
    return [m.group(0) for m in _IDPAT.finditer(q)]


def _extract_args(q, qtype):
    """Route the canonical benchmark (no args) -> per-type routing args parsed from the question text (Gap-4-lite hard-route)."""
    t = qtype.split("_")[0].upper(); ql = q.lower(); ids = _ids_in(q)
    if t == "A":
        m = _re.search(r"about (.+?)\s*\??$", q, _re.I)
        return {"topic": m.group(1) if m else q}
    if t == "C":
        m = _re.search(r"serve[s]?\s+(\S+)", q, _re.I)
        cap = (m.group(1).rstrip("?.") if m else (ids[0] if ids else ""))
        return {"capability": cap if "::" in cap else ("concept::" + cap if cap else "")}
    if t == "D":
        m = _re.search(r"from\s+(\S+)\s+to\s+(\S+)", q, _re.I)
        if m: return {"src": m.group(1).rstrip("?.,"), "tgt": m.group(2).rstrip("?.,")}
        return {"src": ids[0] if ids else "", "tgt": ids[1] if len(ids) > 1 else ""}
    if t == "B":
        if "decompose" in ql: rels = ["DEPENDS_ON", "USES"]
        elif "instance_of" in ql or "instance of" in ql: rels = ["INSTANCE_OF"]
        elif "supersede" in ql: rels = ["SUPERSEDES"]
        elif "depends_on" in ql or "depend on" in ql: rels = ["DEPENDS_ON"]
        elif "use" in ql: rels = ["USES", "INSTANCE_OF", "DEFINED_OVER", "RELATES"]
        else: rels = ["USES"]
        return {"rel_types": rels, "target": (ids[-1] if ids else "*")}
    if t == "E":
        m = _re.search(r"when (.+?)\s*\??$", q, _re.I)
        return {"scenario": (m.group(1) if m else q)}
    if t == "G":
        return {"anchor": ids[0], "topic": q} if ids else {"topic": q}
    if t == "F":
        return {"mode": "never_applied" if "never" in ql else "gap"}
    return {}


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
    # Per Research benchmark division-of-labor (Option 1): Exp-Dev cell = 53-Q hand-routed MECHANISM R&D (isolates route-quality).
    # Testbed owns the canonical 60-Q OFFICIAL number (with its Gap-4 router). Canonical scoring here is opt-in (HDLAB_QA_CANONICAL=1)
    # only for divergence diagnostics -- NOT the headline (hard-route arg-extraction diverges from Gap-4 router; confirmed 0.23 vs 0.48).
    canon_fp = REPO / "data" / "substrate_index" / "benchmark_corpus_v2_60q.jsonl"
    use_canon = os.environ.get("HDLAB_QA_CANONICAL") == "1" and canon_fp.exists()
    bench_fp = canon_fp if use_canon else (REPO / "experiments" / "data" / "gap7_benchmark_v1.jsonl")
    try:
        raw = [json.loads(l) for l in open(bench_fp, encoding="utf-8") if l.strip()]
        bench = []
        for r in raw:
            qid = r.get("qid") or r.get("id"); qtype = r.get("type", "A")
            tnorm = qtype.split("_")[0].upper()
            if tnorm == "NEGATIVE" or tnorm == "N": tnorm = "A"  # route negatives as content (should refuse)
            q = r.get("question", ""); gold = list(r.get("ground_truth_atoms") or r.get("gold") or [])
            ans = r.get("answerable", bool(gold))
            if tnorm == "D" and ans and not gold: gold = ["PATH_EXISTS"]  # D existence: answerable+empty-gold = path exists
            args = r.get("args") or _extract_args(q, tnorm)
            bench.append({"id": qid, "type": tnorm, "question": q, "args": args, "answerable": ans, "gold": gold})
        idx_dir = _snapshot_index()
        if idx_dir is None: return {"error": "no_substrate_index"}
        pstore = PartitionedStore(idx_dir)
        atoms = pstore.all_atoms(); relations = _load_relations(idx_dir)
    except Exception as e:
        print("[load] fail %s" % str(e)[:120], flush=True); return {"error": "load_failed"}
    all_ids = set(_norm(a.id) for a in atoms)
    id2corpus = {_norm(a.id): str(getattr(a.corpus, "value", a.corpus)).lower() for a in atoms}
    id2qid = {_norm(a.id): "%s::%s" % (str(getattr(a.corpus, "value", a.corpus)).lower(), a.id) for a in atoms}
    print("[snapshot] atoms=%d relations=%d benchmark_qs=%d" % (len(atoms), len(relations), len(bench)), flush=True)
    per_q = []; by_type = {}
    for q in bench:
        t = q["type"]; ans = q.get("answerable", True)
        gold = set(_norm(g) for g in q.get("gold", []))
        # D uses an existence sentinel ('path_exists') that is not an atom id -> not atom-presence-filtered
        gold_present = set(g for g in gold if (g in all_ids or g == "path_exists"))
        attrition = len(gold) - len(gold_present)
        if t == "A": retrieved = route_A(atoms, q["args"])
        elif t == "B": retrieved = route_B(relations, q["args"], id2corpus)
        elif t == "C": retrieved = route_C(pstore, sk, q["args"])
        elif t == "D": retrieved = route_D(pstore, sk, q["args"], id2qid)
        elif t == "E": retrieved = route_E(atoms, q["args"])
        elif t == "F": retrieved = route_F(pstore, atoms, q["args"])
        elif t == "G": retrieved = route_G(atoms, relations, q["args"])
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
    m = r["macro_f1"]; s = "macro-F1=%.4f (n=%d Qs, types A-E+neg, per-type %s, gold-attrition=%d) -- v2 (vocab-reconciled B + D/E routes); F/G + Q31-60 next" % (
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
