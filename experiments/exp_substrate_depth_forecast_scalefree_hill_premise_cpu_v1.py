"""
exp_substrate_depth_forecast_scalefree_hill_premise_cpu_v1.py -- CELL-DEPTH-FORECAST: is the substrate corpus scale-free enough for the depth-7+ forecast to extrapolate? -- CPU/local (no heat).

ROUTING: Research handoff exp_dev_handoff_research_curry_howard_depth_5_plus_LANE_B_forecast (Anchor 1, PRIORITY-0 GATE). Before committing
  200+ atom LANE B authoring (induction principles + sigma/pi + type-class hierarchy) to push proof depth to 7-12+, VALIDATE the forecasting
  model: the depth-7+ forecast borrows Mathlib/AFP/Mizar priors which assume a SCALE-FREE dependency graph (Mathlib in-degree power-law
  alpha ~ 1.81). If the substrate corpus is NOT scale-free (Hill alpha > 3.0 = thin-tailed) or its premise counts are anomalous, those
  priors DO NOT extrapolate and the depth forecast must be redone. This cell measures: (1) DEPENDS_ON in-degree Hill power-law alpha,
  (2) avg premise count (out-degree) per leaf/goal, (3) longest-path-to-axiom histogram. NO LLM; relation graph; numpy; no heat. READ-ONLY.
  Race-tolerant (relations.jsonl per-line try/except; tolerant atom read) since Testbed ingest bursts can mid-write files.

PRE-REGISTERED: FORECAST-VALID iff Hill alpha in [1.5, 3.0] (heavy-tailed / scale-free, Mathlib-like ~1.81) AND avg premise count per goal
  in [1.0, 6.0] (Mathlib-plausible) -> the depth-7+ extrapolation HOLDS; LANE B authoring is well-founded. FORECAST-SUSPECT iff Hill alpha
  in (3.0, 4.5] OR premise count outside band (thin tail or anomalous premises -> re-derive forecast before LANE B). FORECAST-INVALID iff
  Hill alpha > 4.5 (not heavy-tailed at all -> Mathlib priors do NOT apply). UNKNOWN if too few edges. ASCII-only. --self-test + --smoke + metrics.json.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time, json, math
from collections import defaultdict, Counter
from pathlib import Path
from typing import Dict, Tuple, List
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "substrate_depth_forecast_scalefree_hill_premise_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
STRUCT = {"DEPENDS_ON", "USES", "INSTANCE_OF", "SPECIALIZES", "DEFINED_OVER", "SHARES_MATH"}
MATH_CORPORA = {"math", "science", "concept", "school", "meta"}; MAX_DEPTH = 30


def _norm(x):
    return str(x).split("::")[-1].strip()


def hill_alpha(degrees: List[int], x_min: int = 2) -> Tuple[float, int]:
    """Hill power-law tail estimator: alpha = 1 + n / sum(ln(x_i / x_min)) over x_i >= x_min. Returns (alpha, n_tail)."""
    tail = [d for d in degrees if d >= x_min]
    if len(tail) < 5:
        return (float("inf"), len(tail))
    s = sum(math.log(d / x_min) for d in tail if d > 0)
    if s <= 0:
        return (float("inf"), len(tail))
    return (1.0 + len(tail) / s, len(tail))


def longest_to_axiom(goal, adj, is_axiom, max_depth):
    best = [0]
    def dfs(n, d, seen):
        if d > 0 and is_axiom(n):
            best[0] = max(best[0], d); return
        if d >= max_depth: return
        for nx in adj.get(n, ()):
            if nx not in seen: dfs(nx, d + 1, seen | {nx})
    dfs(goal, 0, {goal}); return best[0]


def _selftest():
    # spread heavy tail -> finite alpha ~ Mathlib range; flat (all at x_min) -> inf alpha
    pl = [2, 2, 3, 4, 6, 9, 15, 30, 80]
    a, n = hill_alpha(pl, 2); assert 1.2 < a < 3.0, a
    flat = [2]*100; a2, _ = hill_alpha(flat, 2); assert a2 == float("inf") or a2 > 5, a2   # no tail spread
    # longest path
    adj = {"g": ["a"], "a": ["b"], "b": ["AX"]}; isax = lambda n: n == "AX"
    assert longest_to_axiom("g", adj, isax, 30) == 3
    print("[selftest] PASS: substrate_depth_forecast_scalefree_hill_premise_cpu_v1", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run() -> Dict:
    root = REPO / "data" / "substrate_index"
    if not root.exists():
        return {"error": "no_substrate_index"}
    # tolerant atom read (race-safe): tier + corpus
    tier_of = {}; corpus_of = {}
    try:
        from backend.substrate_index.partition import PartitionedStore
        for a in PartitionedStore(root).all_atoms():
            tier_of[_norm(a.id)] = str(getattr(getattr(a, "tier", None), "value", getattr(a, "tier", "")) or "")
            corpus_of[_norm(a.id)] = str(getattr(getattr(a, "corpus", None), "value", getattr(a, "corpus", ""))).lower()
    except Exception as e:
        return {"error": "atom_read_failed_race", "note": str(e)[:80]}
    indeg = Counter(); outdeg = Counter(); adj = defaultdict(list); has_out = set()
    for rp in root.rglob("relations.jsonl"):
        for ln in open(rp, encoding="utf-8"):
            ln = ln.strip()
            if not ln: continue
            try: r = json.loads(ln)
            except Exception: continue
            rt = (r.get("rel_type", "") or "").upper(); s = _norm(r.get("src_id", "")); t = _norm(r.get("tgt_id", ""))
            if not (s and t and s != t): continue
            if rt == "DEPENDS_ON":
                indeg[t] += 1; outdeg[s] += 1
            if rt in STRUCT:
                adj[s].append(t); has_out.add(s)
    indeg_vals = [indeg[a] for a in tier_of if indeg[a] > 0] or list(indeg.values())
    alpha, n_tail = hill_alpha(indeg_vals, x_min=2)
    # avg premise count per goal (out-degree of non-axiom math atoms)
    def is_axiom(n): return tier_of.get(n, "") == "T1" or (n not in has_out)
    goals = [n for n in has_out if not is_axiom(n) and corpus_of.get(n, "") in MATH_CORPORA]
    premise_counts = [outdeg[g] for g in goals if outdeg[g] > 0]
    avg_premise = round(float(np.mean(premise_counts)), 3) if premise_counts else 0.0
    import random; rng = random.Random(1028); sample = goals[:] ; rng.shuffle(sample); sample = sample[: (40 if RUN_MODE != "smoke" else 10)]
    longest = [longest_to_axiom(g, adj, is_axiom, MAX_DEPTH) for g in sample]
    hist = {">=3": sum(1 for x in longest if x >= 3), ">=5": sum(1 for x in longest if x >= 5), ">=7": sum(1 for x in longest if x >= 7)}
    max_longest = max(longest) if longest else 0
    print("  in-degree Hill alpha=%.3f (n_tail=%d, x_min=2) | Mathlib-ref ~1.81" % (alpha, n_tail), flush=True)
    print("  avg premise count per goal=%.2f (n_goals=%d) | longest-path max=%d hist=%s" % (avg_premise, len(goals), max_longest, hist), flush=True)
    return {"hill_alpha": round(alpha, 3) if alpha != float("inf") else 999.0, "n_tail": n_tail,
            "avg_premise_count": avg_premise, "n_goals": len(goals), "max_longest_path": max_longest,
            "longest_hist": hist, "n_indeg_nonzero": len(indeg_vals)}


def verdict(r) -> Tuple[str, str]:
    if r.get("error"):
        return ("UNKNOWN", "UNKNOWN: " + r["error"] + " " + str(r.get("note", "")))
    a = r["hill_alpha"]; pc = r["avg_premise_count"]
    s = ("in-degree Hill alpha=%.3f (Mathlib ref ~1.81; scale-free if heavy-tailed); avg premise count/goal=%.2f; max longest-path=%d hist=%s. "
         "(forecast validity = does the substrate dependency graph match the scale-free priors the depth-7+ extrapolation assumes?)") % (
        a, pc, r["max_longest_path"], r["longest_hist"])
    alpha_ok = (1.5 <= a <= 3.0); pc_ok = (1.0 <= pc <= 6.0)
    if alpha_ok and pc_ok:
        return ("FORECAST_VALID", "FORECAST-VALID: substrate dependency graph IS scale-free (Hill alpha %.2f in [1.5,3.0], Mathlib-like) AND premise counts plausible (%.2f in [1,6]) -> the depth-7+ forecast extrapolation HOLDS; LANE B authoring (induction/sigma-pi/type-class) is well-founded. " % (a, pc) + s)
    if a <= 4.5:
        return ("FORECAST_SUSPECT", "FORECAST-SUSPECT: Hill alpha %.2f or premise count %.2f outside the Mathlib-like band -> re-derive the depth-7+ forecast before committing LANE B authoring (scale-free priors may not fully apply). " % (a, pc) + s)
    return ("FORECAST_INVALID", "FORECAST-INVALID: Hill alpha %.2f > 4.5 -- the in-degree distribution is NOT heavy-tailed/scale-free, so Mathlib/AFP depth priors do NOT extrapolate; the depth-7+ forecast must be redone before LANE B. (Likely the corpus is still too small/young for a clean power-law -- re-run post-BATCH-19-26.) " % a + s)


print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
