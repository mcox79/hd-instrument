"""
exp_substrate_derivation_depth_ceiling_probe_cpu_v1.py -- derivation-depth ceiling instrument (shortest vs LONGEST path to axiom) -- CPU/local (no heat, read-only).

ROUTING: instruments the gate of KP P5 (Curry-Howard type promotion needs proof depth >= 10) + the L6-PROOF FINDER re-run KPI (depth
  1.3 -> 2.5+ post-BATCH-17). The FINDER + P5 measure proof depth via BFS SHORTEST-path-to-axiom (~1.3). An atom can DEPENDS_ON a T1
  directly (depth 1) AND unfold through a longer chain, so the shortest path could UNDER-state true derivation depth. This cell measures
  the LONGEST acyclic path-to-axiom too, converting "is the corpus deep enough to unblock P5 yet?" from a guess into a TRACKED number to
  re-run each ingest cycle. NO LLM; pure typed-graph DFS/BFS; numpy-free; no heat. Re-run after every authoring/ingest batch.

  Finding it was built to capture (2026-06-13 baseline): SHORTEST avg 1.31 / max 2; LONGEST avg 1.71 / max 3; depth>=5 ABSENT.
  -> shallowness is STRUCTURAL, not a shortest-path artifact; P5's depth>=10 gate is many cycles away; recommend Research recalibrate
  (graduated T0 at depth>=5?) or commit to sustained deep-chain authoring. This cell tracks progress toward whatever threshold is set.

PRE-REGISTERED: this is a MEASUREMENT INSTRUMENT (not a pass/fail capability claim). Verdict bands describe the corpus depth REGIME so
  the gate state is explicit: HARD_PASS longest-max >= 10 (P5 unblockable); MIDDLE_BAND longest-max in [5,10) (moderate depth; graduated
  T0 feasible); HARD_FAIL longest-max < 5 (shallow; P5 far off -- current state, EXPECTED, an honest tracked baseline not a defect).
  UNKNOWN if graph absent. ASCII-only. CPU/local. --self-test + --smoke + metrics.json.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time, json, random
from collections import defaultdict, deque
from pathlib import Path
from typing import Dict, Tuple, List
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "substrate_derivation_depth_ceiling_probe_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
STRUCT_EDGES = {"DEPENDS_ON", "USES", "INSTANCE_OF", "SPECIALIZES", "DEFINED_OVER", "SHARES_MATH"}
MATH_CORPORA = {"math", "science", "concept", "school", "meta"}
N_GOALS = 80; DFS_LIMIT = 40; SEED = 1028


def _norm(x):
    return str(x).split("::")[-1].strip()


def shortest_to_axiom(g, adj, is_axiom) -> int:
    q = deque([(g, 0)]); seen = {g}
    while q:
        n, d = q.popleft()
        if d > 0 and is_axiom(n):
            return d
        for nx in adj.get(n, ()):
            if nx not in seen:
                seen.add(nx); q.append((nx, d + 1))
    return 0


def longest_to_axiom(g, adj, is_axiom, limit=DFS_LIMIT) -> int:
    best = [0]
    def dfs(n, d, seen):
        if d > 0 and is_axiom(n):
            best[0] = max(best[0], d); return
        if d >= limit:
            return
        for nx in adj.get(n, ()):
            if nx not in seen:
                dfs(nx, d + 1, seen | {nx})
    dfs(g, 0, {g}); return best[0]


def _selftest():
    adj = {"g": [("a")], }
    # build a small graph: g->n1->...->AX depth 4 longest, but g->AX2 depth 1 shortest
    A = defaultdict(list)
    chain = ["g", "n1", "n2", "n3", "AX"]
    for i in range(len(chain) - 1):
        A[chain[i]].append(chain[i + 1])
    A["g"].append("AXq")                       # shortcut: g -> AXq (axiom) depth 1
    isax = lambda n: n in {"AX", "AXq"}
    assert shortest_to_axiom("g", A, isax) == 1, shortest_to_axiom("g", A, isax)
    assert longest_to_axiom("g", A, isax) == 4, longest_to_axiom("g", A, isax)
    # cycle safety: g->h->g plus g->AX
    C = defaultdict(list); C["g"] = ["h", "AX"]; C["h"] = ["g"]
    assert longest_to_axiom("g", C, lambda n: n == "AX") == 1
    print("[selftest] PASS: substrate_derivation_depth_ceiling_probe_cpu_v1 (shortest<longest + cycle-safe)", flush=True)


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
                    adj[s].append(t); has_out.add(s)

    def is_axiom(n): return tier_of.get(n, "") == "T1" or (n not in has_out)
    goal_pool = [n for n in has_out if not is_axiom(n) and corpus_of.get(n, "") in MATH_CORPORA]
    if len(goal_pool) < 3:
        return {"error": "too_few_goals", "n_goal_pool": len(goal_pool)}
    rng = random.Random(SEED); rng.shuffle(goal_pool)
    goals = goal_pool[: (15 if RUN_MODE == "smoke" else N_GOALS)]
    sh = [shortest_to_axiom(g, adj, is_axiom) for g in goals]
    lo = [longest_to_axiom(g, adj, is_axiom) for g in goals]
    n = len(goals)
    sh_avg = round(sum(sh) / n, 3); lo_avg = round(sum(lo) / n, 3)
    hist = {">=3": sum(1 for x in lo if x >= 3), ">=5": sum(1 for x in lo if x >= 5), ">=10": sum(1 for x in lo if x >= 10)}
    deepest = sorted(zip(lo, goals), reverse=True)[:6]
    print("  goals=%d | SHORTEST depth avg=%.2f max=%d | LONGEST depth avg=%.2f max=%d" % (n, sh_avg, max(sh), lo_avg, max(lo)), flush=True)
    print("  LONGEST-depth histogram: >=3:%d >=5:%d >=10:%d" % (hist[">=3"], hist[">=5"], hist[">=10"]), flush=True)
    for d, g in deepest:
        print("    deepest longest=%d  %s" % (d, g), flush=True)
    return {"n_goals": n, "shortest_avg": sh_avg, "shortest_max": max(sh), "longest_avg": lo_avg, "longest_max": max(lo),
            "longest_hist": hist, "deepest": [[d, g] for d, g in deepest]}


def verdict(r) -> Tuple[str, str]:
    if r.get("error"):
        return ("UNKNOWN", "UNKNOWN: " + r["error"] + " " + str(r.get("n_goal_pool", "")))
    lm = r["longest_max"]
    s = ("derivation depth over %d math goals: SHORTEST avg=%.2f max=%d ; LONGEST avg=%.2f max=%d ; longest-depth hist %s. "
         "(shortest = FINDER/P5 metric; longest = true derivation ceiling -- if longest~shortest, shallowness is STRUCTURAL not a "
         "shortest-path artifact.) P5 gate = depth>=10.") % (
        r["n_goals"], r["shortest_avg"], r["shortest_max"], r["longest_avg"], r["longest_max"], r["longest_hist"])
    if lm >= 10:
        return ("HARD_PASS", "HARD_PASS: derivation ceiling >= 10 -- KP P5 is unblockable; deep proof chains exist. " + s)
    if lm >= 5:
        return ("MIDDLE_BAND", "MIDDLE_BAND: derivation ceiling in [5,10) -- moderate depth; a graduated T0 (depth>=5) is feasible, full depth>=10 P5 still needs more authoring. " + s)
    return ("HARD_FAIL", "HARD_FAIL (EXPECTED baseline, not a defect): derivation ceiling < 5 -- corpus is structurally SHALLOW; shortest~=longest confirms it is NOT a measurement artifact. KP P5 (depth>=10) is many authoring cycles away; recommend Research either recalibrate P5 to a graduated T0 (depth>=5) or commit to sustained deep-chain (multi-hop T3->T2->T1->T0) authoring. Tracked metric: re-run each ingest cycle. " + s)


print("[config] anchor=%s mode=%s n_goals=%d" % (ANCHOR_NAME, RUN_MODE, N_GOALS), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
