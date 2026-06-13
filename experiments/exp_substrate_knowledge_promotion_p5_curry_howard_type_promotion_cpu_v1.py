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
  candidate at tier-D iff it terminates >= MIN_PROOFS distinct goals whose (shortest) proof depth >= D (foundational to deep theory).

  GRADUATED T0 (Research-endorsed 2026-06-13, notes/research_to_exp_dev_testbed_DEPTH_CEILING_3_STRUCTURAL_endorse_BOTH...): the binary
  depth>=10 gate is replaced by tiers -- P5_v1 depth>=5 "moderately foundational" (reachable 1-2 cycles; books the 4th KP path),
  P5_v2 depth>=7, P5_v3 depth>=10 "bedrock" (substrate-LLM categorical-gap maximizer). The cell evaluates all three tiers at once.

PRE-REGISTERED (graduated): HARD-PASS >= 3 T0 candidates at depth>=10 (P5_v3 bedrock). MIDDLE_BAND >= 3 candidates at depth>=5
  (P5_v1 booked -- a genuine 4th KP path) but < 3 at depth>=10. HARD-FAIL deep proofs (max depth >= 5) exist but < 3 candidates even at
  depth>=5. UNKNOWN if max observed proof depth < 5 (GATED -- graph too shallow for even P5_v1; current state, pre BATCH-18). Each axiom
  must anchor >= MIN_PROOFS=2 proofs. ASCII-only. CPU/local. --self-test + --smoke + metrics.json.
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
TIERS = {"v1": 5, "v2": 7, "v3": 10}; GATE_DEPTH = 5; MIN_PROOFS = 2; N_GOALS = 60; MAX_DEPTH = 24; SEED = 1028


def _norm(x):
    return str(x).split("::")[-1].strip()


def backward_chain(goal: str, adj, is_axiom, max_depth: int) -> Optional[List[Tuple[str, str, str]]]:
    """BFS from goal over outgoing typed edges to the NEAREST axiom; returns the (shortest) proof witness or None. (Kept for the verify/soundness sense.)"""
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


def longest_to_axiom(goal: str, adj, is_axiom, max_depth: int) -> Tuple[int, Optional[str]]:
    """LONGEST acyclic path from goal to an axiom -> (depth, terminal_axiom). Research-DECIDED P5 foundationality metric:
       Curry-Howard 'derivability' = DEEPEST grounding through the type hierarchy, NOT the nearest-axiom shortcut. Cycle-safe DFS."""
    best = [0, None]
    def dfs(node, d, seen):
        if d > 0 and is_axiom(node):
            if d > best[0]:
                best[0] = d; best[1] = node
            return                                   # axioms are terminal -- do not extend past them
        if d >= max_depth:
            return
        for (rt, nxt) in adj.get(node, ()):
            if nxt not in seen:
                dfs(nxt, d + 1, seen | {nxt})
    dfs(goal, 0, {goal}); return best[0], best[1]


def proofs_by_axiom(goals, adj, is_axiom, max_depth):
    """Return (axiom -> [(goal, depth), ...], max_depth_seen, n_proved) using the LONGEST-path foundationality depth (Research decision)."""
    by_ax = defaultdict(list); max_seen = 0; n_proved = 0
    for g in goals:
        d, terminal = longest_to_axiom(g, adj, is_axiom, max_depth)
        if not terminal or d == 0:
            continue
        n_proved += 1; max_seen = max(max_seen, d)
        by_ax[terminal].append((g, d))
    return by_ax, max_seen, n_proved


def candidates_at(by_ax, depth, min_proofs):
    """T0 candidates at tier-depth: axioms anchoring >= min_proofs proofs of depth >= `depth`."""
    cands = []
    for ax, gs in by_ax.items():
        deep = [(g, d) for (g, d) in gs if d >= depth]
        if len(deep) >= min_proofs:
            cands.append({"axiom": ax, "n_deep_proofs": len(deep), "depths": sorted(d for _, d in deep)[:8],
                          "example_goals": [g for g, _ in deep][:6]})
    cands.sort(key=lambda c: -c["n_deep_proofs"])
    return cands


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
    by_ax, mx, npv = proofs_by_axiom(["g", "g2"], adj, isax, 24)
    assert mx == 11 and npv == 2, (mx, npv)
    # AX anchors 2 deep proofs at every tier up to depth 11
    for D in (5, 7, 10):
        c = candidates_at(by_ax, D, 2)
        assert len(c) == 1 and c[0]["axiom"] == "AX" and c[0]["n_deep_proofs"] == 2, (D, c)
    assert candidates_at(by_ax, 12, 2) == []                       # no proof deeper than 11
    # shallow-only graph -> gate (max_seen < GATE_DEPTH): h -> AX2 (depth 1)
    adj2 = defaultdict(list); adj2["h"].append(("USES", "AX2"))
    _, mx2, _ = proofs_by_axiom(["h"], adj2, lambda n: n == "AX2", 24)
    assert mx2 == 1, mx2
    print("[selftest] PASS: substrate_knowledge_promotion_p5_curry_howard_type_promotion_cpu_v1 (graduated tiers + deep terminus + shallow-gate)", flush=True)


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
    by_ax, max_seen, n_proved = proofs_by_axiom(goals, adj, is_axiom, MAX_DEPTH)
    tier_cands = {name: candidates_at(by_ax, D, MIN_PROOFS) for name, D in TIERS.items()}
    n_by_tier = {name: len(c) for name, c in tier_cands.items()}
    print("  goals sampled=%d proved=%d | max proof depth seen=%d | T0 candidates by tier: v1(>=5)=%d v2(>=7)=%d v3(>=10)=%d" % (
        len(goals), n_proved, max_seen, n_by_tier["v1"], n_by_tier["v2"], n_by_tier["v3"]), flush=True)
    for c in tier_cands["v1"][:12]:
        print("    T0-CANDIDATE(v1>=5) %-28s anchors %d proofs depths=%s" % (c["axiom"], c["n_deep_proofs"], c["depths"]), flush=True)
    if max_seen >= GATE_DEPTH:
        bf = root / "bench_reports"; bf.mkdir(parents=True, exist_ok=True)
        (bf / "kp_p5_curry_howard_t0_candidates.json").write_text(json.dumps(
            {"tier_candidates": tier_cands, "tiers": TIERS, "min_proofs": MIN_PROOFS,
             "max_depth_seen": max_seen, "n_goals": len(goals), "n_proved": n_proved}, indent=2), encoding="utf-8")
    return {"n_goals": len(goals), "n_proved": n_proved, "max_depth_seen": max_seen, "n_by_tier": n_by_tier,
            "tiers": TIERS, "min_proofs": MIN_PROOFS, "candidates_v1": tier_cands["v1"][:20]}


def verdict(r) -> Tuple[str, str]:
    if r.get("error"):
        return ("UNKNOWN", "UNKNOWN: " + r["error"] + " " + str(r.get("n_goal_pool", "")))
    if r["max_depth_seen"] < GATE_DEPTH:
        return ("UNKNOWN", "UNKNOWN (GATED): max proof depth seen = %d < %d (even P5_v1) -- the typed-derivation graph is too shallow for "
                "Curry-Howard type promotion. Cell is built + self-test-VERIFIED (graduated tiers, synthetic depth-11); runs for real once "
                "deep-chain authoring (Research BATCH 19-26) lifts LONGEST-path proof depth >= 5. (n_proved=%d/%d goals; longest-path metric per Research decision; ceiling rose 3->4 post-BATCH-18.)" % (
                    r["max_depth_seen"], GATE_DEPTH, r["n_proved"], r["n_goals"]))
    nt = r["n_by_tier"]
    s = "T0 candidates by tier v1(>=5)=%d v2(>=7)=%d v3(>=10)=%d (each anchors >=%d proofs); max depth seen=%d over %d/%d proved goals; saved bench_reports/kp_p5_curry_howard_t0_candidates.json (READ-ONLY -- Testbed creates T0 + re-tiers)" % (
        nt["v1"], nt["v2"], nt["v3"], r["min_proofs"], r["max_depth_seen"], r["n_proved"], r["n_goals"])
    if nt["v3"] >= 3:
        return ("HARD_PASS", "HARD_PASS (P5_v3 BEDROCK): %d >= 3 T0 axiom-candidates at depth>=10 -- foundational types anchoring multiple BEDROCK-deep proof chains; substrate-LLM categorical-gap maximizer. A genuine 4th INDEPENDENT KP mechanism (proof-terminus depth-multiplicity). " % nt["v3"] + s)
    if nt["v1"] >= 3:
        return ("MIDDLE_BAND", "MIDDLE_BAND (P5_v1 BOOKED): %d >= 3 T0 axiom-candidates at depth>=5 (moderately foundational) -- books the 4th KP path per Research's graduated-T0 scheme; depth>=10 bedrock tier not yet reached (v3=%d). " % (nt["v1"], nt["v3"]) + s)
    return ("HARD_FAIL", "HARD_FAIL: deep proofs exist (max depth %d >= %d) but < 3 axioms anchor >=%d of them even at depth>=5 -- P5 inactive despite sufficient depth. " % (r["max_depth_seen"], GATE_DEPTH, r["min_proofs"]) + s)


print("[config] anchor=%s mode=%s tiers=%s gate_depth=%d min_proofs=%d" % (ANCHOR_NAME, RUN_MODE, TIERS, GATE_DEPTH, MIN_PROOFS), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
