"""DECISION 79a PRE-CHECK (Exp-Dev independent verification BEFORE Testbed's FIRST non-additive ratify) -- does removing the exact 9 DEPENDS_ON edges + the fhrr INVERSE_PAIR re-type PRESERVE capability (axiom-termination of every affected/goal atom)? This is the substrate's first edge-REMOVAL; a wrong removal would delete a sound grounding. Uses the REAL prover backward_chain on the actual substrate.
Method: compute axiom-termination over the FULL math/science goal pool BEFORE vs AFTER applying all 9 removals atomically; PLUS per-removal endpoint check (does the src atom still axiom-terminate after its outgoing edge is removed?). PASS iff (a) no goal atom that was axiom-terminating BEFORE becomes non-terminating AFTER, and (b) every removed-edge src still axiom-terminates AFTER.
This generalizes the 78d T3 invariant to the EXACT DECISION 79a batch. Substrate-internal; laptop; no LLM; no remote. ASCII; --self-test."""
from __future__ import annotations
import sys, json, time
from pathlib import Path
from collections import defaultdict
from typing import Dict, Tuple
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
from experiments.exp_substrate_proof_finder_backward_chaining_cpu_v1 import backward_chain, _norm, STRUCT_EDGES
DATA_ROOT = REPO / "data" / "substrate_index"
MAX_DEPTH = 6
MATH_CORPORA = {"math", "science", "concept", "school", "meta"}
# the exact DECISION 79a removals (src -> tgt to REMOVE; the reverse/wrong direction)
REMOVALS = [("svd", "pseudoinverse"), ("graph_topology", "bipartite_graph"), ("partial_derivative", "gradient"),
            ("metric_space", "euclidean_distance"), ("derivative", "gradient"),
            ("conditional_probability", "bayes_rule"), ("measure_space", "probability_space"),
            ("gradient", "gradient_descent"), ("inner_product", "cosine_similarity")]
# fhrr_bind <-> fhrr_unbind: remove BOTH DEPENDS_ON, re-type INVERSE_PAIR
INVPAIR = [("fhrr_bind", "fhrr_unbind"), ("fhrr_unbind", "fhrr_bind")]
SELFTEST = "--self-test" in sys.argv


def _selftest():
    assert len(REMOVALS) == 9
    print("[selftest] PASS", flush=True)


if __name__ == "__main__" and SELFTEST:
    _selftest(); sys.exit(0)


def build():
    from backend.substrate_index.partition import PartitionedStore
    atoms = PartitionedStore(DATA_ROOT).all_atoms()
    tier = {_norm(a.id): str(getattr(getattr(a, "tier", None), "value", getattr(a, "tier", "")) or "") for a in atoms}
    corpus = {_norm(a.id): str(getattr(getattr(a, "corpus", None), "value", getattr(a, "corpus", ""))).lower() for a in atoms}
    real = []
    for rp in DATA_ROOT.rglob("relations.jsonl"):
        for ln in open(rp, encoding="utf-8"):
            ln = ln.strip()
            if not ln: continue
            try: r = json.loads(ln)
            except Exception: continue
            rt = (r.get("rel_type", "") or "").upper()
            if rt in STRUCT_EDGES:
                s = _norm(r.get("src_id", "")); t = _norm(r.get("tgt_id", ""))
                if s and t and s != t: real.append((s, rt, t))
    return tier, corpus, real


def make_graph(real, drop):
    adj = defaultdict(list); has_out = set(); edgeset = set()
    for s, rt, t in real:
        if (s, t) in drop: continue
        adj[s].append((rt, t)); has_out.add(s); edgeset.add((s, rt, t))
    return adj, has_out, edgeset


def run() -> Dict:
    tier, corpus, real = build()
    short2full = {}
    for k in set(tier):
        short2full.setdefault(str(k).split("/")[-1].strip().lower(), k)

    def resolve(s): return short2full.get(s, s)
    drop = {(resolve(s), resolve(t)) for s, t in REMOVALS} | {(resolve(s), resolve(t)) for s, t in INVPAIR}
    # resolve check: which removals actually map to an existing edge?
    real_pairs = {(s, t) for s, rt, t in real}
    resolved = [(resolve(s), resolve(t)) for s, t in REMOVALS]
    present = [p for p in resolved if p in real_pairs]
    absent = [(REMOVALS[i]) for i, p in enumerate(resolved) if p not in real_pairs]

    adjB, hoB, _ = make_graph(real, set())
    adjA, hoA, _ = make_graph(real, drop)

    def axiomB(n): return tier.get(n, "") == "T1" or (n not in hoB)
    def axiomA(n): return tier.get(n, "") == "T1" or (n not in hoA)

    # goal pool = non-axiom math/science atoms with outgoing edges (same definition as the L6-PROOF finder)
    goal_pool = [n for n in hoB if not axiomB(n) and corpus.get(n, "") in MATH_CORPORA]

    def term(goal, adj, isax):
        if isax(goal): return True
        w = backward_chain(goal, adj, isax, set(), MAX_DEPTH)
        return w is not None and isax(w[-1][2])

    regressed = []
    before_term = 0; after_term = 0
    for g in goal_pool:
        b = term(g, adjB, axiomB); a = term(g, adjA, axiomA)
        before_term += int(b); after_term += int(a)
        if b and not a: regressed.append(g)
    # per-removal endpoint check: each removed-edge src still axiom-terminates after
    endpoint_fail = []
    for s, t in present:
        if not term(s, adjA, axiomA): endpoint_fail.append("%s (lost termination after removing ->%s)" % (s, t))

    cap_preserved = (len(regressed) == 0 and len(endpoint_fail) == 0)
    print("  DECISION 79a cleanup PRE-CHECK on %d goal atoms (full math/science pool):" % len(goal_pool), flush=True)
    print("  removals present-in-graph=%d / 9 | absent(already-gone/mismatch)=%d" % (len(present), len(absent)), flush=True)
    if absent: print("    absent/mismatch:", absent, flush=True)
    print("  axiom-terminating BEFORE=%d | AFTER=%d | regressed=%d | endpoint-termination-fail=%d" % (
        before_term, after_term, len(regressed), len(endpoint_fail)), flush=True)
    if regressed: print("    REGRESSED goals (capability LOST):", regressed[:20], flush=True)
    if endpoint_fail: print("    ENDPOINT FAIL:", endpoint_fail, flush=True)
    print("  capability_preservation across the 9 removals + INVERSE_PAIR retype = %s" % cap_preserved, flush=True)
    return {"n_goals": len(goal_pool), "present": len(present), "absent": absent, "before_term": before_term,
            "after_term": after_term, "regressed": regressed[:50], "endpoint_fail": endpoint_fail,
            "cap_preserved": cap_preserved}


def verdict(r) -> Tuple[str, str]:
    if r.get("error"): return ("UNKNOWN", "UNKNOWN: " + r["error"])
    s = ("79a cleanup pre-check: %d goal atoms; removals present=%d/9 (absent/mismatch=%d); axiom-terminating before=%d after=%d; regressed=%d; endpoint-fail=%d." % (
        r["n_goals"], r["present"], len(r["absent"]), r["before_term"], r["after_term"], len(r["regressed"]), len(r["endpoint_fail"])))
    if r["cap_preserved"]:
        return ("PASS", "capability_preservation=1.0 HOLDS across the DECISION 79a batch (9 removals + fhrr INVERSE_PAIR): NO goal atom loses axiom-termination, every removed-edge src still grounds -> Testbed's first non-additive ratify is SAFE to commit; no rollback expected. " + s)
    return ("FAIL", "capability_preservation REGRESSES under the 79a batch -> at least one removal deletes a load-bearing grounding; Testbed should ROLLBACK those removals (see regressed/endpoint_fail lists). " + s)


if __name__ == "__main__":
    _selftest()
    print("[config] anchor=substrate_79a_cycle_cleanup_capability_preservation_precheck", flush=True)
    out_dir = get_output_dir("substrate_79a_cycle_cleanup_capability_preservation_precheck_cpu_v1"); t0 = time.time(); r = run()
    v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
    metrics = {"anchor_name": "substrate_79a_cycle_cleanup_capability_preservation_precheck_cpu_v1", "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": "full", "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
    write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
