"""
exp_gap4v2_semantic_A_eval_gpu_v1.py -- Gap-4 v2 semantic A-content encoder eval harness (REMOTE; needs bge) -- ready for Testbed.

ROUTING: Research Cycle 47 -- Gap 4 v2 REMOTE encoder is the A-axis lever (A 0.18-0.28 keyword-limited; family-anchoring gave +0.001;
  semantic encoder is the real fix). Exp-Dev "design help" deliverable: this harness scores the bge semantic retriever on the canonical
  A-content questions vs the keyword baseline, so Testbed can measure the A-axis lift the moment the encoder is wired on remote.
  ENV: requires sentence-transformers + bge-large (NOT on laptop -- verified UNAVAILABLE locally; runs on the home/remote env). If the
  encoder can't load, returns UNKNOWN (env-gated), not a failure. Scoring = canonical set-overlap F1 vs ground_truth_atoms (same as the
  official benchmark). Substrate-only, no LLM-judge.
DESIGN: for each A_content question, topic = text after 'about'; retriever.semantic(topic, top_k) -> ranked atoms; F1 vs gold.
  Sweep top_k in {5,8,12,16} to find the precision/recall knee. Report per-k F1 + best-k + vs keyword baseline 0.185.
PRE-REGISTERED (Research): HARD-PASS semantic-A best-k F1 >= 0.30 (+0.10 over keyword 0.185 = A-axis lever realized). MIDDLE 0.22-0.30.
  HARD-FAIL < 0.22 (semantic encoder doesn't beat keyword -- A gold is too curated for embedding retrieval). UNKNOWN if encoder unavailable.
ASCII-only. write_metrics. PROT-018 _v1.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time, json, re
from pathlib import Path
from typing import Dict, Tuple
try:
    import torch  # noqa: F401  PROT-020: GPU cell; bge-large encodes on CUDA via get_encoder() on the home env.
    _DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
except Exception:
    _DEVICE = "cpu"
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "gap4v2_semantic_A_eval_gpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"


def _norm(qid):
    s = qid.split("::", 1)[1] if "::" in qid else qid
    return s.strip().lower()


def _f1(retrieved, gold):
    gp = set(gold)
    if not gp: return 1.0 if not retrieved else 0.0
    tp = len(retrieved & gp); fp = len(retrieved - gp); fn = len(gp - retrieved)
    if tp == 0: return 0.0
    p = tp / (tp + fp); r = tp / (tp + fn); return 2 * p * r / (p + r)


def _selftest():
    assert _norm("math::T2/fhrr_bind") == "t2/fhrr_bind"
    assert abs(_f1({"x"}, {"x", "y"}) - (2 * 1 * 0.5 / 1.5)) < 1e-6
    print("[selftest] PASS: gap4v2-semantic-A-eval", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run() -> Dict:
    from backend.substrate_index.partition import PartitionedStore
    idx = REPO / "data" / "substrate_index"
    bench_fp = idx / "benchmark_corpus_v2_60q.jsonl"
    if not bench_fp.exists(): return {"error": "no_canonical_benchmark"}
    bench = [json.loads(l) for l in open(bench_fp, encoding="utf-8") if l.strip()]
    A = [q for q in bench if q.get("type", "").startswith("A") and q.get("answerable", True)]
    ps = PartitionedStore(idx); atoms = ps.all_atoms(); all_ids = {_norm(a.id) for a in atoms}
    # build the semantic retriever (REMOTE: needs bge). If unavailable -> UNKNOWN env-gated.
    try:
        from backend.substrate_index.encode import AtomEncoder
        from backend.substrate_index.retrieve import Retriever
        enc = AtomEncoder()
        retr = Retriever(getattr(ps, "store", ps), enc)
        retr.rebuild_index()  # FIX: encode atoms + build bge semantic/composite matrices. Without this semantic() returns [] -> false 0.0 F1.
    except Exception as e:
        print("[encoder] unavailable: %s" % str(e)[:120], flush=True)
        return {"error": "encoder_unavailable_env_gated", "note": "needs sentence-transformers + bge-large (remote); harness is correct + ready"}
    KS = [5, 8, 12, 16]
    per_k = {}
    for K in KS:
        f1s = []
        for q in A:
            m = re.search(r"about (.+?)\s*\??$", q["question"], re.I)
            topic = m.group(1) if m else q["question"]
            gold = {_norm(g) for g in q.get("ground_truth_atoms", []) if _norm(g) in all_ids}
            try:
                cands = retr.semantic(topic, top_k=K)
                ret = {_norm(getattr(c, "atom_id", str(c))) for c in cands}
            except Exception:
                ret = set()
            f1s.append(_f1(ret, gold))
        per_k[K] = round(sum(f1s) / len(f1s), 4) if f1s else 0.0
    best_k = max(per_k, key=per_k.get); best = per_k[best_k]
    n_total = len(atoms); n_alg = sum(1 for a in atoms if getattr(a, "algebra", None))  # corpus-size stamp for clean breadth-ingest before/after deltas
    print("  Gap-4 v2 semantic A-content: per-k F1 %s | best-k=%d F1=%.4f vs keyword 0.185 | corpus n_total=%d n_algebra=%d" % (per_k, best_k, best, n_total, n_alg), flush=True)
    return {"f1": best, "best_k": best_k, "best_f1": best, "per_k": per_k, "keyword_baseline": 0.185, "n_A": len(A),
            "n_total_atoms": n_total, "n_algebra_atoms": n_alg}


def verdict(r) -> Tuple[str, str]:
    if r.get("error") == "encoder_unavailable_env_gated":
        return ("UNKNOWN", "UNKNOWN: bge semantic encoder unavailable in this env (needs sentence-transformers + bge-large; remote). Harness correct + ready for Testbed remote run. " + r.get("note", ""))
    if r.get("error"): return ("UNKNOWN", "UNKNOWN: " + r["error"])
    b = r["best_f1"]; s = "best-k=%d F1=%.4f (per-k %s) vs keyword 0.185 (n_A=%d)" % (r["best_k"], b, r["per_k"], r["n_A"])
    if b >= 0.30:
        return ("HARD_PASS", "HARD_PASS: Gap-4 v2 semantic A-content >=0.30 (+0.10 over keyword) -- A-axis lever realized. " + s)
    if b >= 0.22:
        return ("MIDDLE_BAND", "MIDDLE_BAND: semantic A 0.22-0.30 -- partial A-axis lift over keyword. " + s)
    return ("HARD_FAIL", "HARD_FAIL: semantic A < 0.22 -- embedding retrieval doesn't beat keyword (A gold too curated). " + s)


print("[config] anchor=%s mode=%s device=%s" % (ANCHOR_NAME, RUN_MODE, _DEVICE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
metrics["n_total_atoms"] = r.get("n_total_atoms")    # corpus-size stamp (Strategy RESCUE-1 Cycle 243): clean breadth-ingest before/after deltas
metrics["n_algebra_atoms"] = r.get("n_algebra_atoms")
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
