"""
exp_qa_self_knowledge_unified_a_v2_bge_filtered_cpu_v1.py
Cycle 51 day-3 P0.1: A-axis selection-mechanism v2 (tuned keyword + bge cosine threshold filter).

Per research_to_testbed_exp_dev_CYCLE_51_DAY_3_ACTIVE_COORDINATION_PRIORITY_ORDERED_WORK_LISTS_HP_v1_0_70_PUSH_2026-06-12.md P0.1:
"Selection-mechanism A-axis production tuning -- per-Q top-k + bge threshold optimization"
Pre-reg: A axis 0.459 -> 0.50+ (+0.04+ axis = +0.007 macro)

DESIGN:
- A-route v2 = UNION(keyword_tuned_top_K, bge_top_M) filtered by bge cos >= tau
- Keyword tuned route catches name/alias matches (high precision for canonical-named atoms)
- bge top-M catches semantic matches (high recall for paraphrased queries)
- bge threshold filter keeps only candidates with cue cos >= tau (removes low-confidence)

PARAMETERS:
- Keyword tuned: top_K_kw=7, threshold=4 (unchanged from prior HP_PASS)
- bge top-M: top_M_bge=10 (cast wider net to capture paraphrase)
- bge filter tau: --a-tau (sweepable; default 0.55)

PRE-REG: HARD-PASS A axis macro >= 0.50 (+0.04 over current 0.4588). MIDDLE 0.47-0.50. HARD-FAIL < 0.46.
Reuses bge AtomEncoder (cached on remote Py3.14 from prior bench).
ASCII-only. write_metrics. PROT-018 _v1. CPU.
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
ANCHOR_NAME = "qa_self_knowledge_unified_a_v2_bge_filtered_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ap.add_argument("--top-k", type=int, default=7, help="A-axis keyword top-K")
_ap.add_argument("--threshold", type=int, default=4, help="A-axis keyword score threshold")
_ap.add_argument("--a-bge-top-m", type=int, default=10, help="A-axis bge top-M (semantic recall)")
_ap.add_argument("--a-tau", type=float, default=0.55, help="A-axis bge cosine threshold filter")
_ap.add_argument("--e-tau", type=float, default=0.70, help="E-axis bge cosine threshold")
_ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
TOP_K = _ARGS.top_k
SCORE_THRESHOLD = _ARGS.threshold
A_BGE_TOP_M = _ARGS.a_bge_top_m
A_TAU = _ARGS.a_tau
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


def _keyword_tuned_topK(atoms, args, top_k, threshold):
    topic = args["topic"].lower()
    kws = [w for w in topic.replace("-", " ").replace("_", " ").split()
           if w not in STOP and len(w) > 2]
    if not kws: return set()
    scored = []
    for a in atoms:
        score, total_hits = _score_atom(a, kws)
        if score >= threshold:
            scored.append((score, total_hits, _norm(a.id), a))
    scored.sort(key=lambda x: (-x[0], -x[1], x[2]))
    return [(t[2], t[3]) for t in scored[:top_k]]  # (norm_id, atom)


class BgeAERouter:
    """Combined A + E bge routing: encodes all atoms (semantic vectors) once, shared between A and E."""
    def __init__(self, atoms, a_tau=A_TAU, a_top_m=A_BGE_TOP_M, e_tau=E_TAU):
        from backend.substrate_index.encode import AtomEncoder
        print(f"[bge] initializing AtomEncoder (CPU); ~1-3 min for {len(atoms)} atoms...", flush=True)
        self.encoder = AtomEncoder()
        self.atoms = atoms
        self.a_tau = a_tau
        self.a_top_m = a_top_m
        self.e_tau = e_tau
        t0 = time.time()
        vectors = self.encoder.encode_atoms(atoms)
        self.matrix = np.stack([vectors[a.id].semantic for a in atoms])
        self.id_order = [_norm(a.id) for a in atoms]
        self.corpus_order = [str(getattr(a.corpus, "value", a.corpus)).lower() for a in atoms]
        print(f"[bge] encoded {len(atoms)} atoms in {time.time()-t0:.1f}s; matrix {self.matrix.shape}", flush=True)

    def route_A_v2(self, atoms, args):
        """A-route v2: UNION(keyword_tuned, bge-threshold). NO post-filter (keyword always retained)."""
        # Step 1: keyword tuned top-K candidates (high precision for canonical-named atoms)
        kw_results = _keyword_tuned_topK(atoms, args, TOP_K, SCORE_THRESHOLD)
        kw_set = {nid for nid, _ in kw_results}

        # Step 2: bge cosine threshold (high precision for semantic matches)
        topic = args.get("topic", "")
        if not topic.strip():
            return kw_set
        q = self.encoder.encode_query_text(topic)
        scores = self.matrix @ q
        bge_set = {self.id_order[i] for i in range(len(self.id_order)) if scores[i] >= self.a_tau}

        # Step 3: pure UNION (both signals additive; keyword for known-named; bge for paraphrased)
        return kw_set | bge_set

    def route_E(self, args):
        scenario = args.get("scenario", "")
        if not scenario.strip(): return set()
        q = self.encoder.encode_query_text(scenario)
        scores = self.matrix @ q
        out = set()
        for i in range(len(self.id_order)):
            if self.corpus_order[i] in ("meta", "methodology") and scores[i] >= self.e_tau:
                out.add(self.id_order[i])
        return out


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
    print("[selftest] PASS: unified-a-v2-bge-filtered", flush=True)


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
    print("[snapshot] atoms=%d relations=%d rel_types=%d benchmark_qs=%d kw_topk=%d kw_th=%d a_bge_topm=%d a_tau=%.2f e_tau=%.2f"
          % (len(atoms), len(relations), len(rel_present), len(bench), TOP_K, SCORE_THRESHOLD, A_BGE_TOP_M, A_TAU, E_TAU), flush=True)

    bge = BgeAERouter(atoms, a_tau=A_TAU, a_top_m=A_BGE_TOP_M, e_tau=E_TAU)

    per_q = []; by_type = {}
    for q in bench:
        t = q["type"]; ans = q.get("answerable", True)
        gold = set(_norm(g) for g in q.get("gold", []))
        gold_present = set(g for g in gold if (g in all_ids or g == "path_exists"))
        attrition = len(gold) - len(gold_present)
        if t == "A": retrieved = bge.route_A_v2(atoms, q["args"])
        elif t == "B": retrieved = route_B_v2(relations, q["args"], id2corpus, rel_present)
        elif t == "C": retrieved = route_C(pstore, sk, q["args"])
        elif t == "D": retrieved = route_D(pstore, sk, q["args"], id2qid)
        elif t == "E": retrieved = bge.route_E(q["args"])
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
    s = ("macro-F1=%.4f A-axis=%.4f (n=%d Qs, per-type %s, gold-attrition=%d, a_kw_topk=%d a_bge_topm=%d a_tau=%.2f e_tau=%.2f) -- UNIFIED+A-v2 bge-filter per Cycle 51 day-3 P0.1"
         % (m, a_axis, r["n_qs"], tf1, r["total_gold_attrition"], TOP_K, A_BGE_TOP_M, A_TAU, E_TAU))
    if a_axis >= 0.50:
        return ("HARD_PASS", "HARD_PASS: A-axis macro-F1 >=0.50 (current %.4f). %s" % (a_axis, s))
    if a_axis >= 0.47:
        return ("MIDDLE_BAND", "MIDDLE_BAND: A-axis macro-F1 %.4f in (0.47, 0.50). %s" % (a_axis, s))
    return ("HARD_FAIL", "HARD_FAIL: A-axis macro-F1 %.4f < 0.46 (regression). %s" % (a_axis, s))


print("[config] anchor=%s mode=%s a_kw_topk=%d a_kw_th=%d a_bge_topm=%d a_tau=%.2f e_tau=%.2f" % (ANCHOR_NAME, RUN_MODE, TOP_K, SCORE_THRESHOLD, A_BGE_TOP_M, A_TAU, E_TAU), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
