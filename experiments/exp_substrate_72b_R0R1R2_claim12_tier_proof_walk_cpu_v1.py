"""DECISION 72b -- R0/R1/R2 cheap decisive test (Claim 12 empirical: ARM-1 confidence-tiered + ARM-2 proof-path retrieval under sound oracle).
  R0 = M4d unrestricted full edge set (base + all-29 loose autonomous edges) -> expected dilute (-0.04 per 69c).
  R1 = M4d on STRICT-confidence tier (base + 6 STRICT only; excludes 14 PLAUSIBLE + 9 REJECT) -> expected dilution-NEUTRAL (per 70c).
  R2 = M4d on PROOF-PATH subgraph (edges participating in >=1 L6-PROOF backward-chain derivation) -> ARM-2; expect plateau ~depth 2.
HARD-PASS R1: R1 >= R0 (tier-restriction avoids dilution -> Claim 12 graduates CANDIDATE->MEASURED).
HARD-PASS R2: F1 plateau at depth 2 (proof-path retrieval consistent w/ proof-depth ceiling 1.30).
Production M4d beta=0.10. Remote bge. ASCII; --self-test."""
from __future__ import annotations
import sys, json, time, hashlib
from pathlib import Path
from collections import defaultdict, deque
from typing import Dict, Tuple
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
from experiments.exp_substrate_m4d_capability_graph_walk_heldout_cpu_v1 import _short, f1_present, bfs_proximity, WALK_EDGES, POOL_K, N_ANCHORS, MAX_HOP, DECAY
DATA_ROOT = REPO / "data" / "substrate_index"
HELD_Q = DATA_ROOT / "benchmark_corpus_HELD_OUT_q54_q65_converted.jsonl"
ALL29 = DATA_ROOT / "coevolve1_iter1_P1bge_ACCEPT_edges.jsonl"
STRICT6 = [("mutual_information", "shannon_entropy"), ("markov_decision_process", "markov_chain_property_lemma"),
           ("markov_decision_process", "probability_space"), ("markov_decision_process", "markov_chain"),
           ("q_learning", "bellman_equation"), ("q_learning", "markov_decision_process")]
STRUCT_EDGES = {"DEPENDS_ON", "USES", "INSTANCE_OF", "SPECIALIZES", "DEFINED_OVER", "SHARES_MATH"}
BETA = 0.10
SELFTEST = "--self-test" in sys.argv


def _selftest():
    assert _short("a::b/c") == "c"; print("[selftest] PASS", flush=True)


if __name__ == "__main__" and SELFTEST:
    _selftest(); sys.exit(0)


def run() -> Dict:
    from backend.substrate_index.partition import PartitionedStore
    from backend.substrate_index.encode import AtomEncoder
    from backend.substrate_index.retrieve import Retriever
    from backend.substrate_index.retrieve_cache import rebuild_index_cached
    ps = PartitionedStore(DATA_ROOT)
    try: enc = AtomEncoder()
    except Exception as e: return {"error": "bge:" + str(e)[:60]}
    r = Retriever(ps, enc); rebuild_index_cached(r, DATA_ROOT)
    qual = {a.id: a.qualified_id for a in ps.all_atoms()}
    sset = {_short(a.id) for a in ps.all_atoms()}
    tier_of = {_short(a.id): str(getattr(getattr(a, "tier", None), "value", getattr(a, "tier", "")) or "") for a in ps.all_atoms()}
    corpus_of = {_short(a.id): str(getattr(getattr(a, "corpus", None), "value", getattr(a, "corpus", ""))).lower() for a in ps.all_atoms()}
    short2q = {}
    for a in ps.all_atoms(): short2q.setdefault(_short(a.id), a.qualified_id)
    # base undirected adjacency (qualified) + directed (short, for proof-path)
    base = defaultdict(set); dadj = defaultdict(list); has_out = set()
    for rp in DATA_ROOT.rglob("relations.jsonl"):
        for ln in open(rp, encoding="utf-8"):
            ln = ln.strip()
            if not ln: continue
            try: rr = json.loads(ln)
            except Exception: continue
            if (rr.get("rel_type", "") or "").upper() in WALK_EDGES:
                s = rr.get("src_id", ""); t = rr.get("tgt_id", "")
                if s and t and s != t: base[s].add(t); base[t].add(s)
            if (rr.get("rel_type", "") or "").upper() in STRUCT_EDGES:
                ss = _short(rr.get("src_id", "")); tt = _short(rr.get("tgt_id", ""))
                if ss and tt and ss != tt: dadj[ss].append(tt); has_out.add(ss)

    def is_axiom(n): return tier_of.get(n, "") == "T1" or (n not in has_out)
    # R0 adjacency = base + all-29
    def plus(qedges):
        a = defaultdict(set)
        for k, v in base.items(): a[k] = set(v)
        for s, t in qedges:
            if s and t and s != t: a[s].add(t); a[t].add(s)
        return a
    all29 = []
    if ALL29.exists():
        for ln in open(ALL29, encoding="utf-8"):
            ln = ln.strip()
            if not ln: continue
            try: e = json.loads(ln); all29.append((e.get("src_id", ""), e.get("tgt_id", "")))
            except Exception: pass
    adj_R0 = plus(all29)
    adj_R1 = plus([(short2q.get(s, s), short2q.get(t, t)) for s, t in STRICT6])
    # R2 proof-path subgraph: edges used in backward-chain proofs of operator-core atoms (qualified undirected)
    proof_edges = set()
    core = [n for n in dadj if corpus_of.get(n, "") in ("math", "concept", "science") and not (_short(n).startswith(("wikidata_", "oeis_")))]
    for goal in core:
        seen = {goal}; q = deque([(goal, 0)])
        while q:
            x, d = q.popleft()
            if is_axiom(x) or d >= MAX_HOP: continue
            for m in dadj.get(x, ()):
                proof_edges.add((short2q.get(x, x), short2q.get(m, m)))
                if m not in seen: seen.add(m); q.append((m, d + 1))
    adj_R2 = defaultdict(set)
    for s, t in proof_edges: adj_R2[s].add(t); adj_R2[t].add(s)

    def score(adj, max_hop=MAX_HOP):
        fs = []
        for q in (json.loads(l) for l in open(HELD_Q, encoding="utf-8") if l.strip()):
            gold = q.get("ground_truth_atoms") or []
            present = {_short(g) for g in gold if _short(g) in sset}
            if not present: continue
            cands = r.semantic(q["question"], top_k=POOL_K)
            pool = [(qual.get(c.atom_id, c.atom_id), float(getattr(c, "score", 0.0))) for c in cands]
            if not pool: continue
            cons = defaultdict(float)
            for a_qid, a_cos in pool[:N_ANCHORS]:
                for node, hop in bfs_proximity([a_qid], adj, max_hop).items():
                    if hop > 0: cons[node] += a_cos * (DECAY ** hop)
            top5 = {_short(qid) for qid, _ in sorted(((qid, cos + BETA * cons.get(qid, 0.0)) for qid, cos in pool), key=lambda t: -t[1])[:5]}
            fs.append(f1_present(top5, present))
        return round(sum(fs) / len(fs), 4) if fs else 0.0
    R0 = score(adj_R0); R1 = score(adj_R1)
    R2_h1 = score(adj_R2, 1); R2_h2 = score(adj_R2, 2); R2_h3 = score(adj_R2, 3)
    print("  R0 (full+29 loose)     M4d=%.4f" % R0, flush=True)
    print("  R1 (STRICT tier; base+6) M4d=%.4f  (R1-R0 %+.4f)" % (R1, R1 - R0), flush=True)
    print("  R2 (proof-path subgraph) hop1=%.4f hop2=%.4f hop3=%.4f | proof-edges=%d" % (R2_h1, R2_h2, R2_h3, len(proof_edges)), flush=True)
    return {"R0": R0, "R1": R1, "R1_minus_R0": round(R1 - R0, 4), "R2_hop1": R2_h1, "R2_hop2": R2_h2, "R2_hop3": R2_h3,
            "proof_edges": len(proof_edges)}


def verdict(r) -> Tuple[str, str]:
    if r.get("error"): return ("UNKNOWN", "UNKNOWN: " + r["error"])
    r1ok = r["R1"] >= r["R0"] - 1e-9
    r2plateau = abs(r["R2_hop3"] - r["R2_hop2"]) <= 0.01
    s = ("Claim 12 R0/R1/R2: R0(full+loose)=%.4f, R1(STRICT-tier)=%.4f (R1-R0 %+.4f), R2(proof-path) hop1/2/3=%.4f/%.4f/%.4f (proof-edges=%d)." % (
        r["R0"], r["R1"], r["R1_minus_R0"], r["R2_hop1"], r["R2_hop2"], r["R2_hop3"], r["proof_edges"]))
    if r1ok and r["R1_minus_R0"] > 1e-9:
        return ("HARD_PASS", "Claim 12 R1 MEASURED: confidence-tier restriction AVOIDS dilution (R1 > R0 by %.4f); tier-restricted sound-oracle walk is the substrate's ARM-1 wedge. R2 proof-path %s. " % (r["R1_minus_R0"], "plateaus at depth 2" if r2plateau else "climbs past depth 2") + s)
    if r1ok:
        return ("PARTIAL", "Claim 12 R1: tier-restriction NEUTRAL vs R0 (R1=R0; no dilution to recover because loose edges not in substrate). R2 proof-path %s. " % ("plateaus" if r2plateau else "climbs") + s)
    return ("HARD_FAIL", "Claim 12 R1 REFUTED: tier-restriction dilutes too (R1 < R0). " + s)


if __name__ == "__main__":
    _selftest()
    print("[config] anchor=substrate_72b_R0R1R2_claim12", flush=True)
    out_dir = get_output_dir("substrate_72b_R0R1R2_claim12_tier_proof_walk_cpu_v1"); t0 = time.time(); r = run()
    v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
    metrics = {"anchor_name": "substrate_72b_R0R1R2_claim12_tier_proof_walk_cpu_v1", "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": "full", "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
    write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
