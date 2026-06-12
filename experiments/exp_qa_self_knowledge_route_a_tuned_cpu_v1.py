"""
exp_qa_self_knowledge_route_a_tuned_cpu_v1.py -- tuned RRF UNION A-axis (per Cycle 51 SPRINT GO directive).

ROUTING: Research auto-approved standing pattern "Tuned RRF UNION A-axis" (commit 5732e546).
SCOPE: Replace route_A with scored multi-field keyword match + top-K cap, addressing the
  A-axis precision crisis identified in v1 bench (Q32 fp=46, Q33 fp=30, Q34 fp=26, Q35 fp=19,
  Q37 fp=18; current A=0.378 weakest axis). Other routes (B/C/D/E/F/G) inherited from v1 unchanged.
PRE-REGISTERED: HARD-PASS A axis macro >= 0.45 (current 0.378; +0.072 needed). MIDDLE 0.40-0.45.
  HARD-FAIL <= 0.40. Macro-F1 secondary HARD-PASS >= 0.56 (lift over 0.5625 baseline). NO LLM.
TUNED ROUTE-A:
  - Score each atom by weighted keyword hits: name(4) + aliases(2) + id(1) + description(1)
  - +10 bonus if ALL topic-keywords appear in name OR aliases (canonical match)
  - Score threshold: require score >= 2 (avoid description-only matches; addressing fp tail)
  - Top-K cap = 10 per question
  - Tie-break: prefer atoms with more total keyword hits
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
import re as _re
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "qa_self_knowledge_route_a_tuned_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ap.add_argument("--top-k", type=int, default=10, help="A-axis top-K cap")
_ap.add_argument("--threshold", type=int, default=2, help="A-axis minimum score")
_ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
TOP_K = _ARGS.top_k
SCORE_THRESHOLD = _ARGS.threshold
STOP = {"about", "the", "a", "an", "of", "do", "i", "have", "what", "atoms", "specifically", "network"}


def _norm(qid):
    s = qid.split("::", 1)[1] if "::" in qid else qid
    return s.strip().lower()


def _f1(retrieved, gold_present, answerable):
    if not answerable:
        return (1.0 if not retrieved else 0.0), 0, len(retrieved), 0
    tp = len(retrieved & gold_present); fp = len(retrieved - gold_present); fn = len(gold_present - retrieved)
    if tp == 0: return 0.0, tp, fp, fn
    p = tp / (tp + fp); r = tp / (tp + fn)
    return (2 * p * r / (p + r)), tp, fp, fn


# ---------- TUNED A-route ----------
def route_A_tuned(atoms, args, top_k=TOP_K, threshold=SCORE_THRESHOLD):
    """Tuned A-route addressing precision crisis (Q32-Q37 fp=18-46 in v1 bench).

    Score = 4*name_hits + 2*alias_hits + 1*id_hits + 1*desc_hits + 10*all_in_name_or_alias.
    Filter score >= threshold; sort desc; return top-K.
    """
    topic = args["topic"].lower()
    kws = [w for w in topic.replace("-", " ").replace("_", " ").split()
           if w not in STOP and len(w) > 2]
    if not kws:
        return set()

    scored = []
    for a in atoms:
        name = (a.name or "").lower()
        aliases = " ".join(getattr(a, "aliases", []) or []).lower()
        aid = (a.id or "").lower()
        desc = (getattr(a, "description", "") or "").lower()

        name_hits = sum(1 for k in kws if k in name)
        alias_hits = sum(1 for k in kws if k in aliases)
        id_hits = sum(1 for k in kws if k in aid)
        desc_hits = sum(1 for k in kws if k in desc)

        score = 4 * name_hits + 2 * alias_hits + id_hits + desc_hits

        # Canonical-match bonus: ALL kws appear in name or aliases
        all_in_main = all((k in name or k in aliases) for k in kws)
        if all_in_main and len(kws) >= 1:
            score += 10

        if score >= threshold:
            scored.append((score, name_hits + alias_hits, _norm(a.id)))

    # Sort by (score desc, total_hits desc, name asc for stability)
    scored.sort(key=lambda x: (-x[0], -x[1], x[2]))
    return set(aid for _, _, aid in scored[:top_k])


# ---------- v1-inherited routes (unchanged) ----------
def route_B(relations, args, id2corpus):
    accept = {x.upper() for x in args["rel_types"]}; tgt = _norm(args["target"]); src_ns = args.get("src_ns")
    wild = (tgt == "*")
    out = set()
    for r in relations:
        if r.get("rel_type", "").upper() not in accept: continue
        s = _norm(r["src_id"]); t = _norm(r["tgt_id"])
        if wild or t == tgt:
            if src_ns and id2corpus.get(s) not in src_ns: continue
            out.add(s)
    return out


def route_C(pstore, sk, args):
    try:
        return set(_norm(a.id) for a in sk.what_serves(pstore, args["capability"]))
    except Exception:
        return set()


def route_D(pstore, sk, args, id2qid):
    src = id2qid.get(_norm(args["src"])); tgt = id2qid.get(_norm(args["tgt"]))
    if not src or not tgt: return set()
    try:
        fwd = sk.composition_paths(pstore, src, tgt, max_depth=5)
        rev = sk.composition_paths(pstore, tgt, src, max_depth=5) if not fwd else None
        return {"path_exists"} if (fwd or rev) else set()
    except Exception:
        return set()


def route_E(atoms, args):
    kws = [w for w in args["scenario"].lower().split() if len(w) > 2 and w not in STOP]
    out = set()
    for a in atoms:
        if str(getattr(a.corpus, "value", a.corpus)).lower() not in ("meta", "methodology"): continue
        hay = (a.name + " " + (a.id or "") + " " + " ".join(getattr(a, "aliases", []) or []) + " " + (getattr(a, "description", "") or "")).lower()
        if sum(1 for k in kws if k in hay) >= 2: out.add(_norm(a.id))
    return out


def route_F(pstore, atoms, args):
    if args.get("mode") == "never_applied":
        out = set()
        for a in atoms:
            corp = str(getattr(a.corpus, "value", a.corpus)).lower()
            tier = str(getattr(a.tier, "value", a.tier))
            if corp == "math" and tier in ("T1", "T2") and not getattr(a, "serves_capability", None):
                out.add(_norm(a.id))
        return out
    return set()


ANALOGUE_EDGES = {"RELATES", "GROUNDS", "INSTANTIATES", "ANALOGOUS_TO", "ANALOG_OF", "DUAL",
                    "BIOLOGICAL_INSPIRATION_FOR", "INFLUENCED_BY", "GENERALIZES", "SPECIALIZES"}


def route_G(atoms, relations, args):
    """v1-verbatim: anchor-based ANALOGUE edge traversal, META-restricted fallback."""
    anchor = _norm(args.get("anchor", ""))
    if anchor:
        out = set()
        for r in relations:
            if r.get("rel_type", "").upper() not in ANALOGUE_EDGES: continue
            s = _norm(r["src_id"]); t = _norm(r["tgt_id"])
            if s == anchor: out.add(t)
            if t == anchor: out.add(s)
        return out
    kws = [w for w in args.get("topic", "").lower().split() if len(w) > 2 and w not in STOP]
    out = set()
    for a in atoms:
        if str(getattr(a.corpus, "value", a.corpus)).lower() not in ("meta", "methodology"): continue
        hay = (a.name + " " + (a.id or "") + " " + (getattr(a, "description", "") or "")).lower()
        if sum(1 for k in kws if k in hay) >= 2: out.add(_norm(a.id))
    return out


# ---------- args extraction (verbatim from v1) ----------
_IDPAT = _re.compile(r"[A-Za-z][\w\-/]*::[\w\-/]+")


def _ids_in(q):
    return [m.group(0) for m in _IDPAT.finditer(q)]


def _extract_args(q, qtype):
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
    canon_fp = REPO / "data" / "substrate_index" / "benchmark_corpus_v2_60q.jsonl"
    use_canon = os.environ.get("HDLAB_QA_CANONICAL") == "1" and canon_fp.exists()
    bench_fp = canon_fp if use_canon else (REPO / "experiments" / "data" / "gap7_benchmark_v1.jsonl")
    try:
        raw = [json.loads(l) for l in open(bench_fp, encoding="utf-8") if l.strip()]
        bench = []
        for r in raw:
            qid = r.get("qid") or r.get("id"); qtype = r.get("type", "A")
            tnorm = qtype.split("_")[0].upper()
            if tnorm == "NEGATIVE" or tnorm == "N": tnorm = "A"
            q = r.get("question", ""); gold = list(r.get("ground_truth_atoms") or r.get("gold") or [])
            ans = r.get("answerable", bool(gold))
            if tnorm == "D" and ans and not gold: gold = ["PATH_EXISTS"]
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
    print("[snapshot] atoms=%d relations=%d benchmark_qs=%d top_k=%d threshold=%d"
          % (len(atoms), len(relations), len(bench), TOP_K, SCORE_THRESHOLD), flush=True)
    per_q = []; by_type = {}
    for q in bench:
        t = q["type"]; ans = q.get("answerable", True)
        gold = set(_norm(g) for g in q.get("gold", []))
        gold_present = set(g for g in gold if (g in all_ids or g == "path_exists"))
        attrition = len(gold) - len(gold_present)
        if t == "A": retrieved = route_A_tuned(atoms, q["args"])
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
        print("  %s [%s] F1=%.3f (tp=%d fp=%d fn=%d gold_present=%d attrition=%d)"
              % (q["id"], t, f1, tp, fp, fn, len(gold_present), attrition), flush=True)
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
    m = r["macro_f1"]; tf1 = r["type_f1"]
    a_axis = tf1.get("A", 0.0)
    s = ("macro-F1=%.4f A-axis=%.4f (n=%d Qs, types A-E+neg+G, per-type %s, gold-attrition=%d, top_k=%d threshold=%d) -- tuned RRF UNION A-axis per Cycle 51 SPRINT GO"
         % (m, a_axis, r["n_qs"], tf1, r["total_gold_attrition"], TOP_K, SCORE_THRESHOLD))
    # Pre-reg: HP A axis >= 0.45 (primary)
    if a_axis >= 0.45:
        return ("HARD_PASS", "HARD_PASS: A-axis macro-F1 >=0.45 (current %.4f) -- precision crisis resolved via score+threshold+top-K. %s" % (a_axis, s))
    if a_axis >= 0.40:
        return ("MIDDLE_BAND", "MIDDLE_BAND: A-axis macro-F1 %.4f in (0.40, 0.45) -- partial; further tuning needed. %s" % (a_axis, s))
    return ("HARD_FAIL", "HARD_FAIL: A-axis macro-F1 %.4f <= 0.40 -- tuning hurt or didn't help. %s" % (a_axis, s))


print("[config] anchor=%s mode=%s top_k=%d threshold=%d" % (ANCHOR_NAME, RUN_MODE, TOP_K, SCORE_THRESHOLD), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
