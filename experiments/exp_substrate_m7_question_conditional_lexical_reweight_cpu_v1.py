"""DECISION 62b/64e M7 -- rule-driven QUESTION-CONDITIONAL reweighting of the bge top-K (no graph mutation; no LLM; clean for 56d + q54-q65). Signal: LEXICAL content-term overlap between the question and each candidate's name+aliases -- orthogonal to bge's semantic cosine; catches exact-term matches bge ranks low (e.g. Q 'permutation group' -> atom permutation_group). combined = cos + delta * lexical_overlap. Dev-tune delta on q01-q53 in-cov; apply ONCE to 56d (new concepts; M4d failed there) + q54-q65 (in-distribution). Tests whether M7 GENERALIZES to new concepts where M4d (graph-walk) could not. Substrate-internal; remote bge. ASCII; --self-test."""
from __future__ import annotations
import sys, time, json, re, hashlib
from pathlib import Path
from typing import Dict, Tuple
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
from experiments.exp_substrate_m4d_capability_graph_walk_heldout_cpu_v1 import _short, f1_present, POOL_K
ANCHOR_NAME = "substrate_m7_question_conditional_lexical_reweight_cpu_v1"
DATA_ROOT = REPO / "data" / "substrate_index"
DEV = DATA_ROOT / "benchmark_corpus_v3_60q.jsonl"
HELD_Q = DATA_ROOT / "benchmark_corpus_HELD_OUT_q54_q65_converted.jsonl"
HELD_56D = DATA_ROOT / "benchmark_corpus_56d_concept_disjoint_heldout_v1.jsonl"
SHA_56D = "22d7eb01e5f4dfda2ed8a4ce6f66b3e4edbbfa8b21d9ab8532cb8747b272d418"
STOP = set("a an the of is are was what which who whom whose to in on for and or by with as at from that this these those it its do does using used use under over into within between both same each".split())
DELTAS = [0.0, 0.02, 0.05, 0.1, 0.2, 0.4]
SELFTEST = "--self-test" in sys.argv


def toks(s):
    return {w for w in re.split(r"[^a-z0-9]+", str(s).lower()) if len(w) >= 3 and w not in STOP}


def _selftest():
    assert "permutation" in toks("Permutation Group S_n") and "the" not in toks("the group")
    assert abs(f1_present({"a"}, {"a"}) - 1.0) < 1e-9
    print("[selftest] PASS: " + ANCHOR_NAME, flush=True)


if __name__ == "__main__" and SELFTEST:
    _selftest(); sys.exit(0)


def run() -> Dict:
    if HELD_56D.exists() and hashlib.sha256(HELD_56D.read_bytes()).hexdigest() != SHA_56D:
        return {"error": "56d SHA mismatch"}
    from backend.substrate_index.partition import PartitionedStore
    from backend.substrate_index.encode import AtomEncoder
    from backend.substrate_index.retrieve import Retriever
    from backend.substrate_index.retrieve_cache import rebuild_index_cached
    pstore = PartitionedStore(DATA_ROOT)
    try: enc = AtomEncoder()
    except Exception as e: return {"error": "bge:" + str(e)[:60]}
    r = Retriever(pstore, enc); rebuild_index_cached(r, DATA_ROOT)
    sset = {_short(a.id) for a in pstore.all_atoms()}
    cand_toks = {}
    for a in pstore.all_atoms():
        cand_toks[_short(a.id)] = toks(a.name) | toks(" ".join(a.aliases or [])) | toks(_short(a.id))

    def build(path):
        per = []
        for q in (json.loads(l) for l in open(path, encoding="utf-8") if l.strip()):
            gold = q.get("ground_truth_atoms") or q.get("gold") or []
            if isinstance(gold, str): gold = [gold]
            present = {_short(g) for g in gold if _short(g) in sset}
            if not present: continue
            qtok = toks(q["question"])
            cands = r.semantic(q["question"], top_k=POOL_K)
            pool = []
            for c in cands:
                s = _short(getattr(c, "atom_id", ""))
                ov = len(qtok & cand_toks.get(s, set()))
                pool.append((s, float(getattr(c, "score", 0.0)), ov))
            if pool: per.append({"present": present, "pool": pool})
        return per

    def macro(per, delta):
        fs = []
        for x in per:
            top5 = {s for s, _ in sorted(((s, cos + delta * ov) for s, cos, ov in x["pool"]), key=lambda t: -t[1])[:5]}
            fs.append(f1_present(top5, x["present"]))
        return round(sum(fs) / len(fs), 4) if fs else 0.0
    dev = build(DEV); hq = build(HELD_Q); h56 = build(HELD_56D)
    dev_sweep = {d: macro(dev, d) for d in DELTAS}
    best_d = max(DELTAS, key=lambda d: dev_sweep[d])
    res = {"dev_best_delta": best_d, "dev_sweep": {str(k): v for k, v in dev_sweep.items()},
           "q54q65_bge": macro(hq, 0.0), "q54q65_m7": macro(hq, best_d),
           "h56d_bge": macro(h56, 0.0), "h56d_m7": macro(h56, best_d)}
    print("  M7 question-conditional lexical reweight | DEV-tuned delta=%.2f (q01-q53)" % best_d, flush=True)
    print("  DEV sweep: %s" % res["dev_sweep"], flush=True)
    print("  q54-q65 (in-distribution): bge=%.4f -> M7=%.4f (delta %+.4f) [M4d ref 0.272]" % (res["q54q65_bge"], res["q54q65_m7"], res["q54q65_m7"] - res["q54q65_bge"]), flush=True)
    print("  56d (NEW concepts):        bge=%.4f -> M7=%.4f (delta %+.4f) [M4d was +0.005 here]" % (res["h56d_bge"], res["h56d_m7"], res["h56d_m7"] - res["h56d_bge"]), flush=True)
    res["q54q65_lift"] = round(res["q54q65_m7"] - res["q54q65_bge"], 4)
    res["h56d_lift"] = round(res["h56d_m7"] - res["h56d_bge"], 4)
    return res


def verdict(r) -> Tuple[str, str]:
    if r.get("error"): return ("UNKNOWN", "UNKNOWN: " + r["error"])
    s = ("M7 lexical reweight (dev-tuned delta=%.2f, no Goodhart on held-out): q54-q65 bge %.4f->M7 %.4f (%+.4f); 56d-NEW bge %.4f->M7 %.4f (%+.4f). "
         "M4d ref: +0.124 in-dist, +0.005 new-concept." % (r["dev_best_delta"], r["q54q65_bge"], r["q54q65_m7"], r["q54q65_lift"], r["h56d_bge"], r["h56d_m7"], r["h56d_lift"]))
    if r["h56d_lift"] >= 0.04:
        return ("HARD_PASS", "M7 GENERALIZES to new concepts (where M4d could not): 56d lift %+.4f >= 0.04. M7 is the new-concept mechanism. " % r["h56d_lift"] + s)
    if r["q54q65_lift"] >= 0.04:
        return ("PARTIAL", "M7 helps in-distribution but not new concepts: " + s)
    return ("HARD_FAIL", "M7 lexical reweight does not add (correlates with bge): " + s + " Lexical overlap is already captured by bge cosine; question-conditional discrimination needs a non-lexical signal (type-match).")


if __name__ == "__main__":
    _selftest()
    print("[config] anchor=%s" % ANCHOR_NAME, flush=True)
    out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
    v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
    metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": "full", "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
    write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
