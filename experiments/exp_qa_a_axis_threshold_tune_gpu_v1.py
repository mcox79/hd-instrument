"""
exp_qa_a_axis_threshold_tune_gpu_v1.py -- A-axis TUNED route (keyword UNION bge-cosine-THRESHOLD; adaptive set size) -- light-GPU.

ROUTING: path-to-0.70 A-axis -- the one UNVERIFIED A lever. My 5 prior A methods (keyword 0.378, bge-top-k 0.26-0.36,
  composite-union 0.33, keyword UNION bge-top-3 0.24) all used FIXED top-k -> mismatched variable gold size -> hurt. This cell
  tests the ADAPTIVE approach: keyword set UNION {atoms with bge_cosine(topic, atom) > tau} -- a HIGH cosine threshold adds only
  genuinely-similar atoms (precision-preserving recall boost), set size ADAPTS to the topic. Sweep tau to find the sweet spot
  that BEATS keyword 0.378. Substrate-quality-first; NO LLM frame.

PRE-REGISTERED: HARD-PASS best-tau A-axis F1 >= 0.42 (+0.04 over keyword 0.378). MIDDLE 0.38-0.42 (matches/marginally beats
  keyword). HARD-FAIL < 0.378 (no adaptive threshold beats keyword -> A is bge-ceiling-bound even tuned; only Testbed RRF UNION
  helps). UNKNOWN if bge unavailable.
ASCII-only. torch (light-GPU; bge). --self-test + --smoke + metrics.json. Route via remote_cpu_queue (desktop).
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
    import torch  # PROT-020 GPU cell; bge on CUDA via get_encoder().
except Exception:
    pass
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "qa_a_axis_threshold_tune_gpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
STOP = {"about", "the", "a", "an", "of", "do", "i", "have", "what", "atoms", "specifically", "network", "which", "are", "to", "by", "math"}
TAUS = [0.30, 0.35, 0.40, 0.45, 0.50, 0.55, 0.60, 0.65]


def _norm(qid):
    s = qid.split("::", 1)[1] if "::" in qid else qid
    return s.strip().lower()


def _f1(retrieved, gold):
    if not gold: return 1.0 if not retrieved else 0.0
    tp = len(retrieved & gold)
    if tp == 0: return 0.0
    p = tp / len(retrieved); r = tp / len(gold)
    return 2 * p * r / (p + r)


def _kw_set(atoms, topic):
    kws = [w for w in topic.lower().replace("-", " ").split() if w not in STOP and len(w) > 2]
    out = set()
    for a in atoms:
        hay = (a.name + " " + " ".join(getattr(a, "aliases", []) or []) + " " + (a.id or "")).lower()
        if any(k in hay for k in kws): out.add(_norm(a.id))
    return out


def _selftest():
    assert _norm("math::T2/x") == "t2/x"
    assert abs(_f1({"x"}, {"x", "y"}) - (2 * 1 * 0.5 / 1.5)) < 1e-6
    print("[selftest] PASS: qa-a-axis-threshold-tune", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run() -> Dict:
    from backend.substrate_index.partition import PartitionedStore
    idx = REPO / "data" / "substrate_index"
    bench_fp = idx / "benchmark_corpus_v2_60q.jsonl"
    if not bench_fp.exists():
        bench_fp = REPO / "experiments" / "data" / "gap7_benchmark_v1.jsonl"
    bench = [json.loads(l) for l in open(bench_fp, encoding="utf-8") if l.strip()]
    A = [q for q in bench if q.get("type", "").upper().startswith("A") and q.get("answerable", True)]
    ps = PartitionedStore(idx); atoms = ps.all_atoms(); all_ids = {_norm(a.id) for a in atoms}
    try:
        from backend.substrate_index.encode import AtomEncoder
        from backend.substrate_index.retrieve import Retriever
        enc = AtomEncoder(); retr = Retriever(getattr(ps, "store", ps), enc); retr.rebuild_index()
    except Exception as e:
        print("[bge] unavailable: %s" % str(e)[:120], flush=True)
        return {"error": "bge_unavailable_env_gated", "note": "needs bge; harness correct + ready"}
    # collect per-A-question (keyword set, bge candidates-with-scores, gold)
    perq = []
    for q in A:
        m = re.search(r"about (.+?)\s*\??$", q["question"], re.I)
        topic = m.group(1) if m else q["question"]
        gold = {_norm(g) for g in q.get("ground_truth_atoms", q.get("gold", [])) if _norm(g) in all_ids}
        kw = _kw_set(atoms, topic)
        try:
            cands = [(_norm(getattr(c, "atom_id", str(c))), float(getattr(c, "score", 0.0))) for c in retr.semantic(topic, top_k=40)]
        except Exception:
            cands = []
        perq.append((kw, cands, gold))
    # keyword-only baseline
    kw_f1 = sum(_f1(kw, gold) for kw, _, gold in perq) / len(perq)
    # sweep tau
    curve = []
    for tau in TAUS:
        f1s = []
        for kw, cands, gold in perq:
            ret = set(kw) | {cid for cid, sc in cands if sc > tau}
            f1s.append(_f1(ret, gold))
        curve.append({"tau": tau, "a_f1": round(sum(f1s) / len(f1s), 4)})
        print("  tau=%.2f A-axis F1=%.4f" % (tau, curve[-1]["a_f1"]), flush=True)
    best = max(curve, key=lambda c: c["a_f1"])
    print("  keyword-only A-F1=%.4f | best adaptive: tau=%.2f A-F1=%.4f (delta=%+.4f)"
          % (kw_f1, best["tau"], best["a_f1"], best["a_f1"] - kw_f1), flush=True)
    return {"keyword_a_f1": round(kw_f1, 4), "best_tau": best["tau"], "best_a_f1": best["a_f1"],
            "delta_vs_keyword": round(best["a_f1"] - kw_f1, 4), "curve": curve, "n_A": len(A)}


def verdict(r) -> Tuple[str, str]:
    if r.get("error") == "bge_unavailable_env_gated":
        return ("UNKNOWN", "UNKNOWN: bge unavailable (env-gated). Harness ready. " + r.get("note", ""))
    if r.get("error"): return ("UNKNOWN", "UNKNOWN: " + r["error"])
    b = r["best_a_f1"]; kw = r["keyword_a_f1"]
    s = ("best adaptive A-F1=%.4f at tau=%.2f vs keyword %.4f (delta=%+.4f); curve=%s; n_A=%d -- macro impact ~ delta*12/53"
         % (b, r["best_tau"], kw, r["delta_vs_keyword"], [(c["tau"], c["a_f1"]) for c in r["curve"]], r["n_A"]))
    if b >= 0.42:
        return ("HARD_PASS", "HARD_PASS: adaptive bge-threshold A-route beats keyword by >=+0.04 -- the A-axis IS liftable by a simple tuned route (cosine threshold preserves precision while boosting recall); +~%.3f macro. " % (r["delta_vs_keyword"] * 12 / 53) + s)
    if b >= 0.38:
        return ("MIDDLE_BAND", "MIDDLE_BAND: adaptive threshold marginally beats/matches keyword (0.38-0.42) -- small A lift; " + s)
    return ("HARD_FAIL", "HARD_FAIL: no adaptive threshold beats keyword 0.378 -- A-axis is bge-ceiling-bound even tuned; only Testbed RRF UNION (rank-fusion + composite) lifts it. " + s)


print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
