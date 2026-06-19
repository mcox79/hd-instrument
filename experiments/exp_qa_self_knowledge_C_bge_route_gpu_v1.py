"""
exp_qa_self_knowledge_C_bge_route_gpu_v1.py -- can a bge-semantic fallback fix the C-axis (serves_capability sparsity)? (GPU/bge) -- GPU.

ROUTING: the corpus-vs-route ceiling diagnostic showed C-axis gold is 89pct route-fixable (atoms exist), yet C-F1 is only 0.62
  -- because route_C = what_serves() depends on the serves_capability FIELD, which is SPARSE (many C-gold atoms have
  serves_capability=NONE, e.g. Q44 spectral_observability: 8/11 gold unpopulated). The atoms exist and are SEMANTICALLY about the
  capability, so a bge-semantic fallback (rank atoms by cosine to the capability vector) should recover the serves_capability=NONE
  gold -- exactly parallel to the A/E selection levers. Sweep C-route policies and compute C-F1: prod (what_serves), bge-top-k
  (cosine to capability vec), prod UNION bge-top-k, bge cosine-threshold. Decisive: either bge recovers the field-sparse C gold
  (NEW C-axis lever) or confirms route_C near its ceiling. NO generative LLM (bge embedding).

PRE-REGISTERED: HARD-PASS best policy C-F1 >= prod + 0.05. MIDDLE +0.02..0.05. HARD-FAIL <=+0.02. UNKNOWN if bge/benchmark missing.
ASCII-only. write_metrics. PROT-020 (import torch). GPU. Route via overnight_queue.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import os
os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")
import argparse, time, json, re
from pathlib import Path
from typing import Dict, Tuple
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "qa_self_knowledge_C_bge_route_gpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"


def _norm(x):
    return str(x).split("::")[-1].strip().lower()


def _f1(retrieved, gold):
    if not gold:
        return 1.0 if not retrieved else 0.0
    tp = len(retrieved & gold); fp = len(retrieved - gold); fn = len(gold - retrieved)
    p = tp / (tp + fp + 1e-9); r = tp / (tp + fn + 1e-9)
    return 2 * p * r / (p + r + 1e-9)


def _cap_text(cap):
    """capability qid -> a text cue (strip concept::/CAP_/PP-### prefixes, underscores to spaces)."""
    t = cap.split("::")[-1]
    t = re.sub(r"^(CAP_|PP-\d+_?)", "", t)
    return t.replace("_", " ").strip() or cap.split("::")[-1].replace("_", " ")


def _selftest():
    assert abs(_f1({"a", "b"}, {"a", "b"}) - 1.0) < 1e-6
    assert "spectral observability" in _cap_text("concept::CAP_spectral_observability")
    print("[selftest] PASS: qa_self_knowledge_C_bge_route_gpu_v1", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)
try:
    import torch  # PROT-020
    _ = torch.cuda.is_available()
except Exception as e:
    print("[FATAL] torch: %s" % e, flush=True); sys.exit(1)


def run() -> Dict:
    from backend.substrate_index.partition import PartitionedStore
    from backend.substrate_index import self_knowledge as sk
    bench_fp = REPO / "experiments" / "data" / "gap7_benchmark_v1.jsonl"
    if not bench_fp.exists():
        return {"error": "benchmark_missing"}
    raw = [json.loads(l) for l in open(bench_fp, encoding="utf-8") if l.strip()]
    cqs = []
    for r in raw:
        if r.get("type", "A").split("_")[0].upper() != "C":
            continue
        gold = list(r.get("ground_truth_atoms") or r.get("gold") or [])
        if not gold:
            continue
        cqs.append({"id": r.get("qid") or r.get("id"), "cap": (r.get("args") or {}).get("capability", ""),
                    "gold": set(_norm(g) for g in gold)})
    if SMOKE: cqs = cqs[:4]
    idx_dir = REPO / "data" / "substrate_index"
    if not idx_dir.exists():
        return {"error": "no_substrate_index"}
    pstore = PartitionedStore(idx_dir); atoms = pstore.all_atoms()
    all_ids = set(_norm(a.id) for a in atoms)
    try:
        from backend.substrate_index.encode import AtomEncoder
        from backend.substrate_index.retrieve import Retriever
        enc = AtomEncoder(); retr = Retriever(getattr(pstore, "store", pstore), enc); retr.rebuild_index()
    except Exception as e:
        return {"error": "bge_unavailable", "note": str(e)[:160]}
    id_order = retr._id_order; sem = retr._semantic_matrix
    norm_ids = [_norm(i) for i in id_order]
    nid_to_row = {nid: i for i, nid in enumerate(norm_ids)}
    for q in cqs:
        q["gold"] = set(g for g in q["gold"] if g in all_ids)
    policies = {"prod_what_serves": None, "bge_top5": 5, "bge_top10": 10,
                "prod_U_bge5": ("U", 5), "prod_U_bge10": ("U", 10),
                "thr_0.55": ("T", 0.55), "thr_0.60": ("T", 0.60), "prod_U_thr_0.60": ("UT", 0.60)}
    agg = {p: [] for p in policies}
    n_prod_empty = 0
    for q in cqs:
        # production structural route
        try:
            prod = set(_norm(a.id) for a in sk.what_serves(pstore, q["cap"]))
        except Exception:
            prod = set()
        if not prod: n_prod_empty += 1
        # bge cue: capability atom's own semantic vector if present, else encode cap text
        cap_nid = _norm(q["cap"])
        if cap_nid in nid_to_row:
            cv = sem[nid_to_row[cap_nid]].astype(np.float32)
        else:
            cv = enc.bge.encode([_cap_text(q["cap"])])[0].astype(np.float32)
        cv = cv / (np.linalg.norm(cv) + 1e-9)
        sims = sem @ cv
        order = np.argsort(-sims)
        # exclude the capability atom itself from candidates
        topset = lambda k: set(norm_ids[order[i]] for i in range(k + 1) if norm_ids[order[i]] != cap_nid)
        thrset = lambda t: set(nid for j, nid in enumerate(norm_ids) if sims[j] >= t and nid != cap_nid)
        for p, cfg in policies.items():
            if p == "prod_what_serves":
                ret = prod
            elif p.startswith("bge_top"):
                ret = topset(cfg)
            elif p.startswith("prod_U_bge"):
                ret = prod | topset(cfg[1])
            elif p == "prod_U_thr_0.60":
                ret = prod | thrset(cfg[1])
            elif p.startswith("thr_"):
                ret = thrset(cfg[1])
            else:
                ret = set()
            agg[p].append(_f1(ret, q["gold"]))
    macro = {p: round(float(np.mean(v)), 4) for p, v in agg.items()}
    prod = macro["prod_what_serves"]
    best_p = max((p for p in macro if p != "prod_what_serves"), key=lambda p: macro[p])
    best = macro[best_p]
    print("  C-F1 by policy (n=%d; prod-empty Qs=%d):" % (len(cqs), n_prod_empty), flush=True)
    for p in policies:
        print("    %-18s %.4f%s" % (p, macro[p], "  <-- production" if p == "prod_what_serves" else ""), flush=True)
    print("  best non-prod = %s (%.4f); production = %.4f; delta = %+.4f" % (best_p, best, prod, best - prod), flush=True)
    return {"n": len(cqs), "macro_by_policy": macro, "prod_C_f1": prod, "best_policy": best_p, "best_C_f1": best,
            "delta": round(best - prod, 4), "n_prod_empty": n_prod_empty}


def verdict(r) -> Tuple[str, str]:
    if r.get("error"):
        return ("UNKNOWN", "UNKNOWN: " + r["error"] + " " + str(r.get("note", "")))
    d = r["delta"]; s = "best=%s C-F1=%.4f vs prod(what_serves) %.4f (delta %+.4f); prod-empty Qs=%d/%d; all=%s" % (
        r["best_policy"], r["best_C_f1"], r["prod_C_f1"], d, r["n_prod_empty"], r["n"], r["macro_by_policy"])
    if d >= 0.05:
        return ("HARD_PASS", "HARD_PASS: a bge-semantic C-route BEATS what_serves by >=0.05 C-F1 -- the serves_capability field is sparse, and bge recovers the field-missing C gold (atoms exist + are semantically near the capability). A real C-axis lever toward path-to-0.70, parallel to A/E. " + s)
    if d >= 0.02:
        return ("MIDDLE_BAND", "MIDDLE_BAND: bge fallback gives a small C-F1 lift (+0.02..0.05) -- partial recovery of field-sparse gold. " + s)
    return ("HARD_FAIL", "HARD_FAIL: bge fallback does not beat what_serves by >0.02 -- C-axis is near its ceiling given the serves_capability field; the lever is field BACKFILL (populate serves_capability), not a semantic route. " + s)


print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
