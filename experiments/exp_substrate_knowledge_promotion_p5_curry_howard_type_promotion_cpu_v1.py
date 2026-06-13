"""
exp_substrate_knowledge_promotion_p5_curry_howard_type_promotion_cpu_v1.py -- CELL KP path P5: Curry-Howard type promotion -> T0 axiom-candidates -- CPU/local (no heat, read-only).

ROUTING: Research handoff ANCHOR 1 (knowledge-promotion operator) path P5 + MASTER-PLAN Phase 3. The KP operator has 5 substrate-only
  paths; P1 (frequency) + P4 (geometry) HARD_PASS, P3 (SHARES_MATH bisimulation) built+queue-ready. This is path P5 (Curry-Howard type
  promotion): under Curry-Howard, atom = proposition/type, a typed-derivation chain = a proof (the substrate's CHTV-1 verifier + L6-PROOF
  FINDER already validate this). An AXIOM that is the TERMINUS of many INDEPENDENT, DEEP proof chains is a genuinely FOUNDATIONAL type --
  a candidate for promotion to T0 (the type-theoretic base-axiom tier, below T1). Reuses the FINDER's backward-chaining. Mechanistically
  INDEPENDENT of P1 (in-degree), P4 (geometry), P3 (bisimulation): the signal here is proof-terminus depth-weighted multiplicity.
  READ-ONLY (Testbed creates the T0 + re-tiers). NO LLM; pure typed-graph search; numpy-free; no heat.

  GATE: the substrate's typed-derivation graph is currently shallow (avg proof depth ~1.3; FINDER baseline). P5 needs DEEP proofs
  (Research pre-reg: depth >= DEPTH_THRESHOLD=10) to distinguish foundational axioms from shallow leaves. Until the corpus is deep enough
  (Research BATCH 17+ deeper DEPENDS_ON authoring; projected 2.5+, still < 10), this returns UNKNOWN(gated) by design -- BUILT + algorithm
  self-test-VERIFIED on a synthetic deep proof graph so it runs with zero latency once depth lands. Completes the full 5-path KP harness.

  ALGORITHM: for a sample of math GOALS, backward-chain (BFS) to the nearest axiom -> (terminal axiom, proof depth). An axiom is a T0
  candidate iff it terminates >= MIN_PROOFS distinct goals whose (shortest) proof depth >= DEPTH_THRESHOLD (foundational to deep theory).

PRE-REGISTERED: HARD-PASS >= 3 T0 axiom-candidates (each terminating >= MIN_PROOFS=2 proofs of depth >= 10). MIDDLE 1-2. HARD-FAIL 0
  candidates DESPITE deep proofs existing (no axiom anchors multiple deep chains). UNKNOWN if max observed proof depth < DEPTH_THRESHOLD
  (GATED -- graph too shallow; current state). ASCII-only. CPU/local. --self-test + --smoke + metrics.json.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time, json, random
from collections import deque, defaultdict, Counter
from pathlib import Path
from typing import Dict, Tuple, List, Optional
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "substrate_knowledge_promotion_p5_curry_howard_type_promotion_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
STRUCT_EDGES = {"DEPENDS_ON", "USES", "INSTANCE_OF", "SPECIALIZES", "DEFINED_OVER", "SHARES_MATH"}
MATH_CORPORA = {"math", "science", "concept", "school", "meta"}
DEPTH_THRESHOLD = 10; MIN_PROOFS = 2; N_GOALS = 60; MAX_DEPTH = 24; SEED = 1028


def _norm(x):
    return str(x).split("::")[-1].strip()


def backward_chain(goal: str, adj, is_axiom, max_depth: int) -> Optional[List[Tuple[str, str, str]]]:
    """BFS from goal over outgoing typed edges to the NEAREST axiom; returns the (shortest) proof witness or None."""
    q = deque([(goal, [])]); seen = {goal}
    while q:
        node, path = q.popleft()
        if path and is_axiom(node):
            return path
        if len(path) >= max_depth:
            continue
        for (rt, nxt) in adj.get(node, ()):
            if nxt in seen:
                continue
            seen.add(nxt)
            q.append((nxt, path + [(node, rt, nxt)]))
    return None


def t0_candidates(goals, adj, is_axiom, max_depth, depth_threshold, min_proofs):
    """Return (candidates, max_depth_seen, n_proved). candidate = axiom terminating >=min_proofs deep(>=threshold) proofs."""
    deep_by_axiom = defaultdict(list); max_seen = 0; n_proved = 0
    for g in goals:
        w = backward_chain(g, adj, is_axiom, max_depth)
        if not w:
            continue
        n_proved += 1; d = len(w); max_seen = max(max_seen, d)
        if d >= depth_threshold:
            deep_by_axiom[w[-1][2]].append((g, d))
    cands = [{"axiom": ax, "n_deep_proofs": len(gs), "depths": sorted(d for _, d in gs)[:8],
              "example_goals": [g for g, _ in gs][:6]}
             for ax, gs in deep_by_axiom.items() if len(gs) >= min_proofs]
    cands.sort(key=lambda c: -c["n_deep_proofs"])
    return cands, max_seen, n_proved


def _selftest():
    # synthetic: a depth-11 chain g -> n1 -> ... -> AX (AX an axiom) reachable from TWO goals g and g2 -> AX anchors 2 deep proofs.
    chain = ["g"] + ["n%d" % i for i in range(1, 11)] + ["AX"]    # 12 nodes, 11 edges from g to AX
    adj = defaultdict(list)
    for i in range(len(chain) - 1):
        adj[chain[i]].append(("DEPENDS_ON", chain[i + 1]))
    adj["g2"].append(("DEPENDS_ON", "n1"))                       # g2 -> n1 -> ... -> AX : depth 11
    axioms = {"AX"}
    isax = lambda n: n in axioms
    w = backward_chain("g", adj, isax, 24); assert w and len(w) == 11 and w[-1][2] == "AX", w
    cands, mx, npv = t0_candidates(["g", "g2"], adj, isax, 24, 10, 2)
    assert mx == 11 and npv == 2, (mx, npv)
    assert len(cands) == 1 and cands[0]["axiom"] == "AX" and cands[0]["n_deep_proofs"] == 2, cands
    # shallow-only graph -> gate (max_seen < threshold): h -> AX2 (depth 1)
    adj2 = defaultdict(list); adj2["h"].append(("USES", "AX2"))
    _, mx2, _ = t0_candidates(["h"], adj2, lambda n: n == "AX2", 24, 10, 2)
    assert mx2 == 1, mx2
    print("[selftest] PASS: substrate_knowledge_promotion_p5_curry_howard_type_promotion_cpu_v1 (deep-proof terminus + shallow-gate validated)", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run() -> Dict:
    root = REPO / "data" / "substrate_index"
    if not root.exists():
        return {"error": "no_substrate_index"}
    from backend.substrate_index.partition import PartitionedStore
    atoms = PartitionedStore(root).all_atoms()
    tier_of = {_norm(a.id): str(getattr(getattr(a, "tier", None), "value", getattr(a, "tier", "")) or "") for a in atoms}
    corpus_of = {_norm(a.id): str(getattr(getattr(a, "corpus", None), "value", getattr(a, "corpus", ""))).lower() for a in atoms}
    adj = defaultdict(list); has_out = set()
    for rp in root.rglob("relations.jsonl"):
        for ln in open(rp, encoding="utf-8"):
            ln = ln.strip()
            if not ln: continue
            try: r = json.loads(ln)
            except Exception: continue
            rt = (r.get("rel_type", "") or "").upper()
            if rt in STRUCT_EDGES:
                s = _norm(r.get("src_id", "")); t = _norm(r.get("tgt_id", ""))
                if s and t and s != t:
                    adj[s].append((rt, t)); has_out.add(s)

    def is_axiom(n): return tier_of.get(n, "") == "T1" or (n not in has_out)
    goal_pool = [n for n in has_out if not is_axiom(n) and corpus_of.get(n, "") in MATH_CORPORA]
    if len(goal_pool) < 3:
        return {"error": "too_few_goals", "n_goal_pool": len(goal_pool)}
    rng = random.Random(SEED); rng.shuffle(goal_pool)
    goals = goal_pool[: (10 if RUN_MODE == "smoke" else N_GOALS)]
    cands, max_seen, n_proved = t0_candidates(goals, adj, is_axiom, MAX_DEPTH, DEPTH_THRESHOLD, MIN_PROOFS)
    print("  goals sampled=%d proved=%d | max proof depth seen=%d (need >=%d for P5) | T0 candidates=%d" % (
        len(goals), n_proved, max_seen, DEPTH_THRESHOLD, len(cands)), flush=True)
    for c in cands[:12]:
        print("    T0-CANDIDATE %-30s anchors %d deep proofs depths=%s" % (c["axiom"], c["n_deep_proofs"], c["depths"]), flush=True)
    if max_seen >= DEPTH_THRESHOLD:
        bf = root / "bench_reports"; bf.mkdir(parents=True, exist_ok=True)
        (bf / "kp_p5_curry_howard_t0_candidates.json").write_text(json.dumps(
            {"candidates": cands, "depth_threshold": DEPTH_THRESHOLD, "min_proofs": MIN_PROOFS,
             "max_depth_seen": max_seen, "n_goals": len(goals), "n_proved": n_proved}, indent=2), encoding="utf-8")
    return {"n_goals": len(goals), "n_proved": n_proved, "max_depth_seen": max_seen, "n_candidates": len(cands),
            "depth_threshold": DEPTH_THRESHOLD, "min_proofs": MIN_PROOFS, "candidates": cands[:20]}


def verdict(r) -> Tuple[str, str]:
    if r.get("error"):
        return ("UNKNOWN", "UNKNOWN: " + r["error"] + " " + str(r.get("n_goal_pool", "")))
    if r["max_depth_seen"] < r["depth_threshold"]:
        return ("UNKNOWN", "UNKNOWN (GATED): max proof depth seen = %d < threshold %d -- the typed-derivation graph is too shallow for "
                "Curry-Howard type promotion (no deep proofs to anchor foundational axioms). Cell is built + self-test-VERIFIED on a "
                "synthetic depth-11 graph; runs for real once deeper DEPENDS_ON authoring lifts proof depth >= %d (Research BATCH 17+). "
                "(n_proved=%d/%d goals; avg substrate depth ~1.3 today.)" % (
                    r["max_depth_seen"], r["depth_threshold"], r["depth_threshold"], r["n_proved"], r["n_goals"]))
    n = r["n_candidates"]
    s = "P5: %d T0 axiom-candidates (each anchors >=%d proofs of depth>=%d); max depth seen=%d over %d/%d proved goals; saved bench_reports/kp_p5_curry_howard_t0_candidates.json (READ-ONLY -- Testbed creates T0 + re-tiers)" % (
        n, r["min_proofs"], r["depth_threshold"], r["max_depth_seen"], r["n_proved"], r["n_goals"])
    if n >= 3:
        return ("HARD_PASS", "HARD_PASS: Curry-Howard type promotion identifies %d >= 3 T0 axiom-candidates -- foundational types anchoring multiple deep proof chains. A 4th/5th INDEPENDENT KP mechanism (proof-terminus depth-multiplicity). " % n + s)
    if n >= 1:
        return ("MIDDLE_BAND", "MIDDLE_BAND: %d T0 candidate(s) (deep proofs exist but few axioms anchor >=%d of them). " % (n, r["min_proofs"]) + s)
    return ("HARD_FAIL", "HARD_FAIL: deep proofs exist (max depth %d >= %d) but NO axiom anchors >=%d of them -- P5 inactive. " % (r["max_depth_seen"], r["depth_threshold"], r["min_proofs"]) + s)


print("[config] anchor=%s mode=%s depth_threshold=%d min_proofs=%d" % (ANCHOR_NAME, RUN_MODE, DEPTH_THRESHOLD, MIN_PROOFS), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
