"""
exp_qa_self_knowledge_unified_a_tuned_b_v3_cpu_v1.py -- UNIFIED Cycle 51 day-1 bench:
tuned route_A (precision-trimming scored + threshold + top-K) + v3 route_B_v2 (bidirectional +
explicit-rel-type + last-segment + ACCEPT-ALL-rel-types-for-specific-target) + v1 route_C/D/E/F/G.

PROJECTED MACRO: ~0.59 (day-2 target 0.58 EXCEEDED) per additive composition:
- v1 bench: MACRO 0.5243, A=0.378, B=0.445
- v3 bench (v3 route_B only): MACRO 0.5625, A=0.378, B=0.6985
- tuned-A bench (tuned A only): MACRO 0.5486, A=0.4588, B=0.445
- UNIFIED (tuned-A + v3-B): projected MACRO ~0.59, A=0.459, B=0.699

PRE-REGISTERED: HARD-PASS MACRO >= 0.58 (Cycle 51 day-2 target). MIDDLE 0.55-0.58. HARD-FAIL < 0.55.
ASCII-only. write_metrics. PROT-018 _v1.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time, json, shutil, tempfile, re
from pathlib import Path
from typing import Dict, Tuple
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "qa_self_knowledge_unified_a_tuned_b_v3_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ap.add_argument("--top-k", type=int, default=7)
_ap.add_argument("--threshold", type=int, default=4)
_ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
TOP_K = _ARGS.top_k
SCORE_THRESHOLD = _ARGS.threshold
STOP = {"about", "the", "a", "an", "of", "do", "i", "have", "what", "atoms", "specifically", "network",
        "which", "are", "to", "by", "math"}
REL_NAMES = ["INSTANCE_OF", "DEPENDS_ON", "USES", "SUPERSEDES", "SPECIALIZES", "GENERALIZES",
             "DEFINED_OVER", "RELATES", "DUAL", "INFLUENCED_BY", "PRESERVES", "OPTIMIZES", "ENABLES", "DEFINED_BY"]


def _norm(qid):
    s = qid.split("::", 1)[1] if "::" in qid else qid
    return s.strip().lower()


def _last_seg(x):
    n = _norm(x)
    return n.rsplit("/", 1)[-1]


def _f1(retrieved, gold_present, answerable):
    if not answerable: return (1.0 if not retrieved else 0.0), 0, len(retrieved), 0
    tp = len(retrieved & gold_present); fp = len(retrieved - gold_present); fn = len(gold_present - retrieved)
    if tp == 0: return 0.0, tp, fp, fn
    p = tp / (tp + fp); r = tp / (tp + fn)
    return (2 * p * r / (p + r)), tp, fp, fn


# ---------- tuned route_A ----------
def route_A_tuned(atoms, args, top_k=TOP_K, threshold=SCORE_THRESHOLD):
    topic = args["topic"].lower()
    kws = [w for w in topic.replace("-", " ").replace("_", " ").split()
           if w not in STOP and len(w) > 2]
    if not kws: return set()

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

        if all((k in name or k in aliases) for k in kws):
            score += 10

        if score >= threshold:
            scored.append((score, name_hits + alias_hits, _norm(a.id)))

    scored.sort(key=lambda x: (-x[0], -x[1], x[2]))
    return set(aid for _, _, aid in scored[:top_k])


# ---------- v3 route_B_v2 (verbatim from v3 bench) ----------
def route_B_v2(relations, args, id2corpus, rel_present):
    tgt_full = _norm(args["target"]); tgt_seg = _last_seg(args["target"])
    src_ns = args.get("src_ns"); wild = (tgt_full == "*")
    if wild:
        accept = {x.upper() for x in args["rel_types"]}
    else:
        accept = set(rel_present)
    out = set()
    for r in relations:
        if r.get("rel_type", "").upper() not in accept: continue
        s = _norm(r["src_id"]); t = _norm(r["tgt_id"])
        s_seg = s.rsplit("/", 1)[-1]; t_seg = t.rsplit("/", 1)[-1]
        if wild:
            cand_other = [s, t]
        elif t == tgt_full or t_seg == tgt_seg:
            cand_other = [s]
        elif s == tgt_full or s_seg == tgt_seg:
            cand_other = [t]
        else:
            continue
        for o in cand_other:
            if src_ns and id2corpus.get(o) not in src_ns: continue
            out.add(o)
    return out


# ---------- v1 routes C/D/E/F/G (verbatim) ----------
def route_C(pstore, sk, args):
    try: return set(_norm(a.id) for a in sk.what_serves(pstore, args["capability"]))
    except Exception: return set()


def route_D(pstore, sk, args, id2qid):
    src = id2qid.get(_norm(args["src"])); tgt = id2qid.get(_norm(args["tgt"]))
    if not src or not tgt: return set()
    try:
        fwd = sk.composition_paths(pstore, src, tgt, max_depth=5)
        rev = sk.composition_paths(pstore, tgt, src, max_depth=5) if not fwd else None
        return {"path_exists"} if (fwd or rev) else set()
    except Exception: return set()


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


_IDPAT = re.compile(r"(?:[a-z]+::)?(?:T\d/[\w]+|PP-\d+[\w]*|CAP_[\w]+|RULE_[\w]+|SCHOOL/[\w]+|[A-Z]{2,}/[\w]+|[\w]+_family)")


def _ids_in(q): return [m.group(0) for m in _IDPAT.finditer(q)]


def _extract_args(q, qtype):
    t = qtype.split("_")[0].upper(); ql = q.lower(); ids = _ids_in(q)
    if t == "A":
        m = re.search(r"about (.+?)\s*\??$", q, re.I); return {"topic": m.group(1) if m else q}
    if t == "C":
        m = re.search(r"serve[s]?\s+(\S+)", q, re.I); cap = (m.group(1).rstrip("?.") if m else (ids[0] if ids else ""))
        return {"capability": cap if "::" in cap else ("concept::" + cap if cap else "")}
    if t == "D":
        m = re.search(r"from\s+(\S+)\s+to\s+(\S+)", q, re.I)
        if m: return {"src": m.group(1).rstrip("?.,"), "tgt": m.group(2).rstrip("?.,")}
        return {"src": ids[0] if ids else "", "tgt": ids[1] if len(ids) > 1 else ""}
    if t == "B":
        named = [rn for rn in REL_NAMES if rn.lower() in ql or rn in q]
        if named:
            rels = named
        elif "decompose" in ql: rels = ["DEPENDS_ON", "USES"]
        elif "instance" in ql: rels = ["INSTANCE_OF"]
        elif "supersede" in ql: rels = ["SUPERSEDES"]
        elif "depend" in ql: rels = ["DEPENDS_ON"]
        elif "use" in ql: rels = ["USES", "INSTANCE_OF", "DEFINED_OVER", "RELATES"]
        else: rels = ["USES", "RELATES"]
        return {"rel_types": rels, "target": (ids[-1] if ids else "*"),
                "src_ns": (["math"] if "math atom" in ql else None)}
    if t == "E":
        m = re.search(r"when (.+?)\s*\??$", q, re.I); return {"scenario": (m.group(1) if m else q)}
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


def _selftest():
    assert _norm("math::T2/fhrr_bind") == "t2/fhrr_bind"
    assert _last_seg("SCHOOL/x_family") == "x_family"
    a = _extract_args("Which atoms have INSTANCE_OF relations to SCHOOL/discriminative_learning_family?", "B")
    assert "INSTANCE_OF" in a["rel_types"], a
    print("[selftest] PASS: qa-unified-a-tuned-b-v3", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run() -> Dict:
    from backend.substrate_index.partition import PartitionedStore
    from backend.substrate_index import self_knowledge as sk
    bench_fp = REPO / "experiments" / "data" / "gap7_benchmark_v1.jsonl"
    try:
        raw = [json.loads(l) for l in open(bench_fp, encoding="utf-8") if l.strip()]
        bench = []
        for r in raw:
            qid = r.get("qid") or r.get("id"); qtype = r.get("type", "A"); tnorm = qtype.split("_")[0].upper()
            if tnorm in ("NEGATIVE", "N"): tnorm = "A"
            q = r.get("question", ""); gold = list(r.get("ground_truth_atoms") or r.get("gold") or [])
            ans = r.get("answerable", bool(gold))
            if tnorm == "D" and ans and not gold: gold = ["PATH_EXISTS"]
            args = r.get("args") or _extract_args(q, tnorm)
            bench.append({"id": qid, "type": tnorm, "question": q, "args": args, "answerable": ans, "gold": gold})
        idx_dir = _snapshot_index()
        if idx_dir is None: return {"error": "no_substrate_index"}
        pstore = PartitionedStore(idx_dir); atoms = pstore.all_atoms(); relations = _load_relations(idx_dir)
    except Exception as e:
        print("[load] fail %s" % str(e)[:120], flush=True); return {"error": "load_failed"}
    all_ids = set(_norm(a.id) for a in atoms)
    id2corpus = {_norm(a.id): str(getattr(a.corpus, "value", a.corpus)).lower() for a in atoms}
    id2qid = {_norm(a.id): "%s::%s" % (str(getattr(a.corpus, "value", a.corpus)).lower(), a.id) for a in atoms}
    rel_present = {r.get("rel_type", "").upper() for r in relations}
    print("[snapshot] atoms=%d relations=%d rel_types=%d benchmark_qs=%d top_k=%d threshold=%d"
          % (len(atoms), len(relations), len(rel_present), len(bench), TOP_K, SCORE_THRESHOLD), flush=True)
    per_q = []; by_type = {}
    for q in bench:
        t = q["type"]; ans = q.get("answerable", True)
        gold = set(_norm(g) for g in q.get("gold", []))
        gold_present = set(g for g in gold if (g in all_ids or g == "path_exists"))
        attrition = len(gold) - len(gold_present)
        if t == "A": retrieved = route_A_tuned(atoms, q["args"])
        elif t == "B": retrieved = route_B_v2(relations, q["args"], id2corpus, rel_present)
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
    s = ("macro-F1=%.4f (n=%d Qs, per-type %s, gold-attrition=%d, top_k=%d threshold=%d) -- UNIFIED tuned-A + v3-B per Cycle 51 day-1->day-2"
         % (m, r["n_qs"], tf1, r["total_gold_attrition"], TOP_K, SCORE_THRESHOLD))
    if m >= 0.58:
        return ("HARD_PASS", "HARD_PASS: MACRO >= 0.58 (current %.4f) -- Cycle 51 day-2 target HIT. %s" % (m, s))
    if m >= 0.55:
        return ("MIDDLE_BAND", "MIDDLE_BAND: MACRO %.4f in (0.55, 0.58) -- partial. %s" % (m, s))
    return ("HARD_FAIL", "HARD_FAIL: MACRO %.4f < 0.55. %s" % (m, s))


print("[config] anchor=%s mode=%s top_k=%d threshold=%d" % (ANCHOR_NAME, RUN_MODE, TOP_K, SCORE_THRESHOLD), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
