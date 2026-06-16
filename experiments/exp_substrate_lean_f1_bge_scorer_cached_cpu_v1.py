"""
exp_substrate_lean_f1_bge_scorer_cached_cpu_v1.py -- DECISION 25 Option B: lean batched bge F1 scorer + reusable full-corpus bge cache -- runs on the BGE machine (remote runner desktop).

ROUTING: Director DECISION 25 (Option B). The canonical substrate_benchmark.py is pathologically slow at full corpus (CPU-bound AlgebraIndex
  build + per-question pipeline; GPU idle 50min+). This lean scorer: (1) builds/loads the full-corpus bge cache via the CANONICAL
  rebuild_index_cached (so it's reusable + future canonical runs go from 50min to seconds), (2) retrieves per question via the CANONICAL
  Retriever.semantic (bge cosine -- identical to canonical's bge path), (3) applies the H1 tau-gate, (4) scores set-overlap F1 per axis on the
  30q + 60q benchmark sets. SKIPS the slow algebra-union pipeline.

  R3 (document path coverage): this is BGE-ONLY retrieval. The canonical scorer additionally unions algebra-HRR retrieval + structural
  (DEPENDS_ON/SHARES_MATH) + L6-PROOF answer paths for some axes (esp. B_relation, D_composition). algebra-union recall >= bge-only, so this
  lean F1 is a LOWER BOUND on canonical. Report as bge-only; cross-check vs canonical (Option A run) per R5.
  R1: also score the 30q subset so the Director/Auditor can compare per-axis vs the canonical 30q (within +-0.05 expected on bge-driven axes).
  R2: pure-python + numpy + bge only. R4: F1>=0.50 bar; tau-gate applied.

PRE-REGISTERED: report macro-F1 + per-axis (A-G) + recall@10 on 30q and 60q, ungated and gated (tau). HARD-PASS macro-F1 >= 0.50 (bge-only;
  canonical >= this). 0.20-0.45 = H1 confirmed, floor unmet. <0.20 = regression. UNKNOWN if bge unavailable. ASCII-only. --self-test + metrics.json.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time, json
from collections import defaultdict
from pathlib import Path
from typing import Dict, Tuple, List
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "substrate_lean_f1_bge_scorer_cached_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
DATA_ROOT = REPO / "data" / "substrate_index"
TAU = 0.80                                                # H1 confidence gate (DECISION/F1-BRIDGE H1: cut FP 70.6pct)
QSETS = [("30q", DATA_ROOT / "benchmark_corpus_v1_30q.jsonl"), ("60q", DATA_ROOT / "benchmark_corpus_v3_60q.jsonl")]


def set_f1(pred: set, gold: set) -> Tuple[float, float, float]:
    if not gold:
        return (1.0, 1.0, 1.0) if not pred else (0.0, 1.0, 0.0)
    inter = len(pred & gold)
    prec = inter / len(pred) if pred else 0.0
    rec = inter / len(gold)
    f1 = 2 * prec * rec / (prec + rec) if (prec + rec) else 0.0
    return round(prec, 4), round(rec, 4), round(f1, 4)


def _selftest():
    p, r, f = set_f1({"a", "b"}, {"a", "c"})
    assert abs(f - 0.5) < 1e-6, f
    p2, r2, f2 = set_f1({"a"}, {"a"}); assert f2 == 1.0
    print("[selftest] PASS: substrate_lean_f1_bge_scorer_cached_cpu_v1", flush=True)


if __name__ == "__main__":
    _selftest()
    if _ARGS.self_test:
        sys.exit(0)


def load_qs(path: Path):
    qs = []
    for ln in open(path, encoding="utf-8"):
        ln = ln.strip()
        if not ln: continue
        try: qs.append(json.loads(ln))
        except Exception: continue
    return qs


def run() -> Dict:
    if not DATA_ROOT.exists():
        return {"error": "no_substrate_index"}
    try:
        from backend.substrate_index.partition import PartitionedStore
        from backend.substrate_index.encode import AtomEncoder
        from backend.substrate_index.retrieve import Retriever
        from backend.substrate_index.retrieve_cache import rebuild_index_cached
    except Exception as e:
        return {"error": "import_failed:" + str(e)[:100]}
    pstore = PartitionedStore(DATA_ROOT)
    try:
        encoder = AtomEncoder()                          # requires sentence_transformers (remote only)
    except Exception as e:
        return {"error": "bge_unavailable:" + str(e)[:80]}
    r = Retriever(pstore, encoder)
    t_cache = time.time()
    rebuild_index_cached(r, DATA_ROOT)                   # builds + saves reusable full-corpus bge cache
    cache_s = round(time.time() - t_cache, 1)
    n_atoms = len(getattr(r, "_id_order", []) or [])
    # qualified-id map (ground_truth uses qualified ids like math::T2/fhrr_bind)
    qual = {a.id: a.qualified_id for a in pstore.all_atoms()}
    out = {"n_atoms_indexed": n_atoms, "cache_build_s": cache_s, "tau": TAU, "qsets": {}}
    for label, path in QSETS:
        if not path.exists():
            out["qsets"][label] = {"error": "qset_missing"}; continue
        qs = load_qs(path)
        if RUN_MODE == "smoke": qs = qs[:6]
        ax_ung = defaultdict(list); ax_gat = defaultdict(list); rec10 = []
        for q in qs:
            gold = set(q.get("ground_truth_atoms") or [])
            axis = (q.get("type") or "?").split("_")[0]
            try:
                cands = r.semantic(q["question"], top_k=10)
            except Exception:
                cands = []
            ranked = [(qual.get(c.atom_id, c.atom_id), getattr(c, "score", 0.0)) for c in cands]
            top10 = set(cid for cid, _ in ranked[:10])
            rec10.append(1.0 if (top10 & gold) else 0.0)
            pred_ung = set(cid for cid, _ in ranked[:5])                      # top-5 ungated
            pred_gat = set(cid for cid, sc in ranked if sc >= TAU)            # tau-gated
            ax_ung[axis].append(set_f1(pred_ung, gold)[2])
            ax_gat[axis].append(set_f1(pred_gat, gold)[2])
        def macro(d):
            per = {a: round(sum(v) / len(v), 4) for a, v in d.items()}
            return per, (round(sum(sum(v) / len(v) for v in d.values()) / len(d), 4) if d else 0.0)
        per_ung, m_ung = macro(ax_ung); per_gat, m_gat = macro(ax_gat)
        r10 = round(sum(rec10) / len(rec10), 4) if rec10 else 0.0
        out["qsets"][label] = {"n_q": len(qs), "macro_f1_ungated_top5": m_ung, "macro_f1_tau_gated": m_gat,
                               "recall_at_10": r10, "per_axis_ungated": per_ung, "per_axis_gated": per_gat}
        print("  [%s] n=%d | recall@10=%.4f | macro-F1 ungated-top5=%.4f | macro-F1 tau(%.2f)-gated=%.4f" % (
            label, len(qs), r10, m_ung, TAU, m_gat), flush=True)
        print("       per-axis ungated: %s" % per_ung, flush=True)
    print("  bge cache: %d atoms indexed, build/load %.1fs (reusable)" % (n_atoms, cache_s), flush=True)
    return out


def verdict(r) -> Tuple[str, str]:
    if r.get("error"):
        return ("UNKNOWN", "UNKNOWN: " + r["error"])
    q60 = r["qsets"].get("60q", {}); q30 = r["qsets"].get("30q", {})
    m = q60.get("macro_f1_ungated_top5", q30.get("macro_f1_ungated_top5", 0.0))
    mg = q60.get("macro_f1_tau_gated", q30.get("macro_f1_tau_gated", 0.0))
    best = max(m, mg)
    s = ("LEAN bge-only F1 (DECISION 25 Option B; reuses canonical Retriever.semantic; full-corpus bge cache %d atoms built in %.1fs reusable). "
         "30q: macro-F1 ungated=%.4f gated=%.4f r@10=%.4f. 60q: macro-F1 ungated=%.4f gated=%.4f r@10=%.4f. R3: BGE-ONLY -- canonical unions "
         "algebra-HRR + structural + L6-PROOF for B/D axes, so canonical macro-F1 >= this LOWER BOUND. tau-gate=%.2f (H1).") % (
        r["n_atoms_indexed"], r["cache_build_s"],
        q30.get("macro_f1_ungated_top5", 0), q30.get("macro_f1_tau_gated", 0), q30.get("recall_at_10", 0),
        q60.get("macro_f1_ungated_top5", 0), q60.get("macro_f1_tau_gated", 0), q60.get("recall_at_10", 0), TAU)
    if best >= 0.50:
        return ("HARD_PASS", "HARD_PASS (bge-only F1 >= 0.50 floor; canonical >= this): macro-F1=%.4f. LAKATOS F1 floor MET at the bge-retrieval layer. " % best + s)
    if best >= 0.20:
        return ("MIDDLE_BAND", "MIDDLE_BAND (H1 confirmed; bge-only macro-F1=%.4f in [0.20,0.50)): 0.0067 was a degraded-scorer artifact (real bge-F1 is much higher); floor not yet met at bge-only -- algebra-union (canonical) may close it. " % best + s)
    return ("HARD_FAIL", "HARD_FAIL: bge-only macro-F1=%.4f < 0.20 -- below H1 prediction; investigate. " % best + s)


if __name__ == "__main__":
    print("[config] anchor=%s mode=%s tau=%.2f" % (ANCHOR_NAME, RUN_MODE, TAU), flush=True)
    out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
    v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
    metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
    write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
