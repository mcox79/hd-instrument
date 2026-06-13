"""
exp_qa_self_knowledge_unified_a_tuned_b_v3_e_bge_threshold_cpu_v1.py
UNIFIED bench + Exp-Dev's bge cosine-threshold E-route (tau=0.70 over meta/methodology corpus).

Per exp_dev_to_testbed_PATH_TO_070_combined_AE_route_fixes_macro_0p52_to_0p57_plus0p0506_validated_2026-06-12.md:
- E-route bge-threshold-0.70 lifts E-F1 from keyword-only 0.547 to 0.854 on Exp-Dev's bench (+0.307)
- Full-stack: combined A=bge-top5 + E=bge-threshold-0.70 lifts MACRO 0.5204 -> 0.5711 (+0.0506) zero regression
- Largest single path-to-0.70 lever this session

Composition projection on MY UNIFIED bench (which uses tuned-A keyword + v3 route_B + D-axis edges):
- Current UNIFIED MACRO = 0.5869
- Current E = 0.495 (keyword-only)
- If E -> 0.7667 (Exp-Dev's full-stack number): expected MACRO ~0.62 (Cycle 51 MID target HIT)
- Note: I keep tuned-A keyword (already HARD_PASS A=0.4588) rather than bge-top-5 because my keyword route already beats bge-top-5 on the bench

PRE-REG: HARD-PASS MACRO >= 0.62 (Cycle 51 mid target). MIDDLE 0.59-0.62. HARD-FAIL < 0.59.
ASCII-only. write_metrics. PROT-018 _v1. CPU (bge default CPU).
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
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "qa_self_knowledge_unified_a_tuned_b_v3_e_bge_threshold_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ap.add_argument("--top-k", type=int, default=7, help="A-axis top-K")
_ap.add_argument("--threshold", type=int, default=4, help="A-axis score threshold")
_ap.add_argument("--e-tau", type=float, default=0.70, help="E-axis bge cosine threshold")
_ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
TOP_K = _ARGS.top_k
SCORE_THRESHOLD = _ARGS.threshold
E_TAU = _ARGS.e_tau
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


def _score_atom(a, kws):
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

    return score, name_hits + alias_hits


def route_A_tuned(atoms, args, top_k=TOP_K, threshold=SCORE_THRESHOLD):
    topic = args["topic"].lower()
    kws = [w for w in topic.replace("-", " ").replace("_", " ").split()
           if w not in STOP and len(w) > 2]
    if not kws: return set()

    scored = []
    max_name_alias_hits = 0
    for a in atoms:
        score, total_hits = _score_atom(a, kws)
        if total_hits > max_name_alias_hits:
            max_name_alias_hits = total_hits
        if score >= threshold:
            scored.append((score, total_hits, _norm(a.id)))

    # Refuse heuristic: if no atom has substantive name+alias coverage of topic,
    # the question likely has no canonical answer (refuse rather than over-fetch).
    # Threshold: need at least max(1, ceil(n_kws/2)) topic-kws covered in some atom's name+aliases.
    min_required_hits = max(1, (len(kws) + 1) // 2)
    if max_name_alias_hits < min_required_hits:
        return set()  # refuse

    scored.sort(key=lambda x: (-x[0], -x[1], x[2]))
    return set(aid for _, _, aid in scored[:top_k])


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


# ---------- bge cosine-threshold route_E ----------
class BgeERouter:
    """Per Exp-Dev finding: bge cosine threshold over meta/methodology corpus.

    Single Retriever instance shared across all E-Qs (encode once, query many).
    """
    def __init__(self, atoms, tau=E_TAU):
        from backend.substrate_index.encode import AtomEncoder
        print(f"[bge_e] initializing AtomEncoder (default CPU; ~1-5 min for 1743 atoms)...", flush=True)
        self.encoder = AtomEncoder()
        self.atoms = atoms
        self.tau = tau
        # Restrict to META + METHODOLOGY atoms
        self.e_atoms = [a for a in atoms
                        if str(getattr(a.corpus, "value", a.corpus)).lower() in ("meta", "methodology")]
        print(f"[bge_e] META/METHODOLOGY atoms: {len(self.e_atoms)} of {len(atoms)}", flush=True)
        # Encode E-corpus atoms (semantic vectors)
        t0 = time.time()
        vectors = self.encoder.encode_atoms(self.e_atoms)
        self.matrix = np.stack([vectors[a.id].semantic for a in self.e_atoms])
        self.id_order = [_norm(a.id) for a in self.e_atoms]
        print(f"[bge_e] encoded {len(self.e_atoms)} atoms in {time.time()-t0:.1f}s; matrix shape {self.matrix.shape}", flush=True)

    def route(self, args):
        scenario = args.get("scenario", "")
        if not scenario.strip():
            return set()
        q = self.encoder.encode_query_text(scenario)
        scores = self.matrix @ q  # cosine
        keep = scores >= self.tau
        return {self.id_order[i] for i in range(len(self.id_order)) if keep[i]}


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


def route_G(atoms, relations, args, top_k=3):
    """G-axis: ANALOGUE edges from anchor; fallback to scored META/methodology keyword + top-K cap (P0 day-3 refinement)."""
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
    if not kws: return set()
    scored = []
    for a in atoms:
        if str(getattr(a.corpus, "value", a.corpus)).lower() not in ("meta", "methodology"): continue
        hay = (a.name + " " + (a.id or "") + " " + (getattr(a, "description", "") or "")).lower()
        name_lower = (a.name or "").lower()
        kw_hits = sum(1 for k in kws if k in hay)
        if kw_hits < 2: continue
        # Score: more hits + bonus for name match
        name_hits = sum(1 for k in kws if k in name_lower)
        score = kw_hits + 2 * name_hits
        scored.append((score, _norm(a.id)))
    scored.sort(key=lambda x: (-x[0], x[1]))
    return set(aid for _, aid in scored[:top_k])


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
    print("[selftest] PASS: unified-a-tuned-b-v3-e-bge-threshold", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run() -> Dict:
    from backend.substrate_index.partition import PartitionedStore
    from backend.substrate_index import self_knowledge as sk
    # Allow held-out / alternative benchmark via env var; default to canonical Q01-Q53.
    # Per held-out routing note (commit 50124338 + USER Goodhart directive 2026-06-13).
    _override = os.environ.get("HDLAB_QA_BENCH_PATH")
    bench_fp = Path(_override) if _override else (REPO / "experiments" / "data" / "gap7_benchmark_v1.jsonl")
    if _override:
        print(f"[bench] HDLAB_QA_BENCH_PATH override: {bench_fp}", flush=True)
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
    print("[snapshot] atoms=%d relations=%d rel_types=%d benchmark_qs=%d top_k_a=%d th_a=%d e_tau=%.2f"
          % (len(atoms), len(relations), len(rel_present), len(bench), TOP_K, SCORE_THRESHOLD, E_TAU), flush=True)

    # Initialize bge E-router (ONE-time setup; encodes all META+METHODOLOGY atoms)
    bge_e = BgeERouter(atoms, tau=E_TAU)

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
        elif t == "E": retrieved = bge_e.route(q["args"])
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
    s = ("macro-F1=%.4f (n=%d Qs, per-type %s, gold-attrition=%d, top_k_a=%d th_a=%d e_tau=%.2f) -- UNIFIED + bge-threshold-E per Cycle 51 mid->close"
         % (m, r["n_qs"], tf1, r["total_gold_attrition"], TOP_K, SCORE_THRESHOLD, E_TAU))
    if m >= 0.62:
        return ("HARD_PASS", "HARD_PASS: MACRO >= 0.62 (current %.4f) -- Cycle 51 MID target HIT. %s" % (m, s))
    if m >= 0.59:
        return ("MIDDLE_BAND", "MIDDLE_BAND: MACRO %.4f in (0.59, 0.62). %s" % (m, s))
    return ("HARD_FAIL", "HARD_FAIL: MACRO %.4f < 0.59 (regression). %s" % (m, s))


print("[config] anchor=%s mode=%s top_k_a=%d th_a=%d e_tau=%.2f" % (ANCHOR_NAME, RUN_MODE, TOP_K, SCORE_THRESHOLD, E_TAU), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
