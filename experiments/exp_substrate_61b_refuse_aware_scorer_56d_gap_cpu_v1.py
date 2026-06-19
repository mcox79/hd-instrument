"""DECISION 61b -- refuse-aware scorer for the 7 56d GAP/refuse-control questions (Galois theory, Riemann hypothesis, Navier-Stokes, Yoneda lemma, Banach-Tarski, Fermat's Last Theorem, four-color theorem -- gold NOT in substrate). Correct behavior = REFUSE (no candidate above tau). Per question: correct-refusal if max bge cosine < tau (tau=0.70 per 35a F4 cluster). Report refusal rate + what the hallucinating ones retrieve (diagnostic). Probes whether refuse-discipline generalizes to NOVEL topics. Substrate-internal; remote bge. ASCII; --self-test."""
from __future__ import annotations
import sys, time, json, hashlib
from pathlib import Path
from typing import Dict, Tuple
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
from experiments.exp_substrate_m4d_capability_graph_walk_heldout_cpu_v1 import _short
ANCHOR_NAME = "substrate_61b_refuse_aware_scorer_56d_gap_cpu_v1"
DATA_ROOT = REPO / "data" / "substrate_index"
HELDOUT_56D = DATA_ROOT / "benchmark_corpus_56d_concept_disjoint_heldout_v1.jsonl"
EXPECTED_SHA = "22d7eb01e5f4dfda2ed8a4ce6f66b3e4edbbfa8b21d9ab8532cb8747b272d418"
TAU = 0.70  # 35a F4 refuse-discipline threshold
SELFTEST = "--self-test" in sys.argv


def _selftest():
    assert _short("a::b/c") == "c"
    print("[selftest] PASS: " + ANCHOR_NAME, flush=True)


if __name__ == "__main__" and SELFTEST:
    _selftest(); sys.exit(0)


def run() -> Dict:
    if not HELDOUT_56D.exists():
        return {"error": "no_56d_file"}
    if hashlib.sha256(HELDOUT_56D.read_bytes()).hexdigest() != EXPECTED_SHA:
        return {"error": "SHA256_MISMATCH"}
    from backend.substrate_index.partition import PartitionedStore
    from backend.substrate_index.encode import AtomEncoder
    from backend.substrate_index.retrieve import Retriever
    from backend.substrate_index.retrieve_cache import rebuild_index_cached
    pstore = PartitionedStore(DATA_ROOT)
    try: enc = AtomEncoder()
    except Exception as e: return {"error": "bge:" + str(e)[:60]}
    r = Retriever(pstore, enc); rebuild_index_cached(r, DATA_ROOT)
    sset = {_short(a.id) for a in pstore.all_atoms()}
    name_of = {a.id: (a.name or a.id) for a in pstore.all_atoms()}
    qs = [json.loads(l) for l in open(HELDOUT_56D, encoding="utf-8") if l.strip()]
    gap = [q for q in qs if not {_short(g) for g in (q.get("ground_truth_atoms") or []) if _short(g) in sset}]
    rows = []; correct_refuse = 0
    for q in gap:
        cands = r.semantic(q["question"], top_k=5)
        top = [(getattr(c, "atom_id", ""), float(getattr(c, "score", 0.0))) for c in cands]
        max_cos = top[0][1] if top else 0.0
        refused = max_cos < TAU
        if refused: correct_refuse += 1
        rows.append({"qid": q["qid"], "chapter": q.get("chapter", ""), "max_cos": round(max_cos, 4),
                     "refused": refused, "top_atom": name_of.get(top[0][0], top[0][0])[:30] if top else "-"})
    rate = round(correct_refuse / len(gap), 4) if gap else 0.0
    print("  56d GAP questions=%d | tau=%.2f | correct-refusal rate=%.4f (%d/%d)" % (len(gap), TAU, rate, correct_refuse, len(gap)), flush=True)
    print("  qid          max_cos  refused?  would-retrieve (if hallucinating)", flush=True)
    for x in rows:
        print("  %-11s  %.4f   %s     %s" % (x["qid"], x["max_cos"], "REFUSE" if x["refused"] else "HALLUC", "-" if x["refused"] else x["top_atom"]), flush=True)
    return {"n_gap": len(gap), "tau": TAU, "correct_refuse": correct_refuse, "refusal_rate": rate, "rows": rows}


def verdict(r) -> Tuple[str, str]:
    if r.get("error"): return ("UNKNOWN", "UNKNOWN: " + r["error"])
    rate = r["refusal_rate"]
    s = "56d GAP refuse-discipline (n=%d novel-concept questions, tau=%.2f): correct-refusal rate=%.4f (%d/%d). The gold concepts are NOT in substrate; correct behavior is refuse." % (
        r["n_gap"], r["tau"], rate, r["correct_refuse"], r["n_gap"])
    if rate >= 0.95:
        return ("HARD_PASS", "refuse-discipline GENERALIZES to novel topics (>=0.95 refusal): " + s)
    if rate < 0.50:
        return ("HARD_FAIL", "refuse-discipline does NOT generalize (hallucinates on novel topics; <0.50 refusal): " + s + " Confirms the categorical refuse-discipline gap on new concepts.")
    return ("MIDDLE", "refuse-discipline PARTIAL on novel topics: " + s)


if __name__ == "__main__":
    _selftest()
    print("[config] anchor=%s" % ANCHOR_NAME, flush=True)
    out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
    v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
    metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": "full", "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
    write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
