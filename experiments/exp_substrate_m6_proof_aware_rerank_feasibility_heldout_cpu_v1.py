"""DECISION 56c M6 FEASIBILITY (proof-aware reranker): compose M4d (cosine + beta*consensus) with an L6-PROOF signal -- candidates that backward-chain to a genuine T1 axiom (shallower proof = stronger) get a gamma boost. Hypothesis: gold atoms are better-proven than high-cosine distractors -> proof-signal discriminates. Substrate-internal (M4d graph + L6-PROOF FINDER; no LLM; 11th-rule clean; strengthens positioning via proof-soundness-as-discriminator). FEASIBILITY: sweep gamma on held-out (Goodhart-FLAGGED) to see if proof-signal lifts above M4d 0.272 at all; de-Goodhart later if promising. Remote bge. ASCII; --self-test."""
from __future__ import annotations
import sys, time, json
from pathlib import Path
from collections import defaultdict
from typing import Dict, Tuple
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
from experiments.exp_substrate_m4d_capability_graph_walk_heldout_cpu_v1 import (
    _short, f1_present, bfs_proximity, WALK_EDGES, POOL_K, N_ANCHORS, MAX_HOP, DECAY)
from experiments.exp_substrate_proof_finder_backward_chaining_cpu_v1 import backward_chain, STRUCT_EDGES, MAX_DEPTH, _norm as _pnorm
ANCHOR_NAME = "substrate_m6_proof_aware_rerank_feasibility_heldout_cpu_v1"
DATA_ROOT = REPO / "data" / "substrate_index"
HELDOUT = DATA_ROOT / "benchmark_corpus_HELD_OUT_q54_q65_converted.jsonl"
BETA = 0.10
GAMMAS = [0.0, 0.05, 0.1, 0.2, 0.4]
SELFTEST = "--self-test" in sys.argv


def _selftest():
    assert _short("a::b/c") == "c"
    print("[selftest] PASS: " + ANCHOR_NAME, flush=True)


if __name__ == "__main__" and SELFTEST:
    _selftest(); sys.exit(0)


def run() -> Dict:
    from backend.substrate_index.partition import PartitionedStore
    from backend.substrate_index.encode import AtomEncoder
    from backend.substrate_index.retrieve import Retriever
    from backend.substrate_index.retrieve_cache import rebuild_index_cached
    pstore = PartitionedStore(DATA_ROOT)
    try: enc = AtomEncoder()
    except Exception as e: return {"error": "bge:" + str(e)[:60]}
    r = Retriever(pstore, enc); rebuild_index_cached(r, DATA_ROOT)
    qual = {a.id: a.qualified_id for a in pstore.all_atoms()}
    sset = {_short(a.id) for a in pstore.all_atoms()}
    tier_of = {_pnorm(a.id): str(getattr(getattr(a, "tier", None), "value", getattr(a, "tier", "")) or "") for a in pstore.all_atoms()}
    # proof graph (directed adj for backward_chain) + M4d walk graph (undirected)
    padj = defaultdict(list); preal = set(); phas_out = set(); wadj = defaultdict(set)
    for rp in DATA_ROOT.rglob("relations.jsonl"):
        for ln in open(rp, encoding="utf-8"):
            ln = ln.strip()
            if not ln: continue
            try: rr = json.loads(ln)
            except Exception: continue
            rt = (rr.get("rel_type", "") or "").upper()
            s = rr.get("src_id", ""); t = rr.get("tgt_id", "")
            if not s or not t or s == t: continue
            if rt in STRUCT_EDGES:
                ss = _pnorm(s); tt = _pnorm(t)
                padj[ss].append((rt, tt)); preal.add((ss, rt, tt)); phas_out.add(ss)
            if rt in WALK_EDGES:
                wadj[s].add(t); wadj[t].add(s)

    def is_axiom(n): return tier_of.get(n, "") == "T1" or (n not in phas_out)

    def proof_signal(qid):
        n = _pnorm(qid)
        w = backward_chain(n, padj, is_axiom, preal, MAX_DEPTH)
        if not w: return 0.0
        terminal = w[-1][2]
        if tier_of.get(terminal, "") == "T1":
            return 1.0 / (1.0 + len(w))   # genuine-T1, shallower = stronger
        return 0.3 / (1.0 + len(w))       # leaf-terminating (authoring-gap), weaker
    qs = [json.loads(l) for l in open(HELDOUT, encoding="utf-8") if l.strip()]
    perq = []
    for q in qs:
        gold = q.get("ground_truth_atoms") or []
        present = {_short(g) for g in gold if _short(g) in sset}
        if not present: continue
        cands = r.semantic(q["question"], top_k=POOL_K)
        pool = [(qual.get(c.atom_id, c.atom_id), float(getattr(c, "score", 0.0))) for c in cands]
        if not pool: continue
        cons = defaultdict(float)
        for a_qid, a_cos in pool[:N_ANCHORS]:
            for node, hop in bfs_proximity([a_qid], wadj, MAX_HOP).items():
                if hop > 0: cons[node] += a_cos * (DECAY ** hop)
        # proof signal only for the top-30 (backward_chain is the cost); rest=0
        psig = {}
        for qid, _ in pool[:30]:
            psig[qid] = proof_signal(qid)
        perq.append({"qid": q["qid"], "present": present, "pool": pool, "cons": dict(cons), "psig": psig})

    def macro(gamma):
        fs = []
        for x in perq:
            sc = sorted(((qid, cos + BETA * x["cons"].get(qid, 0.0) + gamma * x["psig"].get(qid, 0.0)) for qid, cos in x["pool"]), key=lambda t: -t[1])
            fs.append(f1_present({_short(qid) for qid, _ in sc[:5]}, x["present"]))
        return round(sum(fs) / len(fs), 4) if fs else 0.0
    rows = [{"gamma": g, "macro": macro(g)} for g in GAMMAS]
    base = rows[0]["macro"]; best = max(rows, key=lambda d: d["macro"])
    print("  in-coverage held-out n=%d | beta=%.2f | proof-aware gamma sweep (Goodhart-FLAGGED feasibility):" % (len(perq), BETA), flush=True)
    for r_ in rows:
        print("    gamma=%.2f -> IN-COV F1=%.4f" % (r_["gamma"], r_["macro"]), flush=True)
    print("  M4d(gamma=0)=%.4f | best proof-aware=%.4f at gamma=%.2f (delta %+.4f)" % (base, best["macro"], best["gamma"], best["macro"] - base), flush=True)
    return {"n": len(perq), "m4d_base": base, "best_macro": best["macro"], "best_gamma": best["gamma"], "delta": round(best["macro"] - base, 4), "sweep": rows}


def verdict(r) -> Tuple[str, str]:
    if r.get("error"): return ("UNKNOWN", "UNKNOWN: " + r["error"])
    s = ("M6 proof-aware rerank FEASIBILITY: M4d base=%.4f -> best=%.4f at gamma=%.2f (delta %+.4f). Held-out gamma-swept (GOODHART-FLAGGED; "
         "de-Goodhart on dev if promising). n=%d." % (r["m4d_base"], r["best_macro"], r["best_gamma"], r["delta"], r["n"]))
    if r["delta"] >= 0.05:
        return ("PARTIAL", "PROMISING (proof-signal discriminates gold; >=+0.05 feasibility): " + s + " De-Goodhart on dev next; full M6 post-55a.")
    if r["delta"] >= 0.02:
        return ("MIDDLE", "WEAK-POSITIVE (proof-signal helps a little): " + s)
    return ("HARD_FAIL", "M6 INFEASIBLE (proof-signal does NOT discriminate gold; most atoms axiom-terminating so signal flat): " + s + " Deprioritize M6; proof-soundness not a retrieval discriminator here.")


if __name__ == "__main__":
    _selftest()
    print("[config] anchor=%s" % ANCHOR_NAME, flush=True)
    out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
    v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
    metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": "full", "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
    write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
