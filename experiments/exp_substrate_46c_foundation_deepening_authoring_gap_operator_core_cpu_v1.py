"""DECISION 46c: measure foundation-deepening effect on the OPERATOR CORE authoring-gap (was 62pct; Drill 1 predicted <30pct after 8 Layer-0/1 primitives). The canonical proof finder's goal pool is now swamped by 5360 wikidata leaf atoms (trivial depth-1 leaf->class); this re-scopes to the typed math OPERATOR core (excludes wikidata_*/oeis_* knowledge leaves) and distinguishes GENUINE-T1 termination from AUTHORING-GAP leaves (terminal is a non-T1 leaf = proof stopped for lack of authored depth). Runs over the FULL operator core (no sampling). Structural; laptop; no bge. ASCII; --self-test + metrics.json."""
from __future__ import annotations
import sys, os, time, json
from pathlib import Path
from collections import defaultdict
from typing import Dict, Tuple
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
from experiments.exp_substrate_proof_finder_backward_chaining_cpu_v1 import (
    STRUCT_EDGES, MAX_DEPTH, _norm, backward_chain, type_check)
ANCHOR_NAME = "substrate_46c_foundation_deepening_authoring_gap_operator_core_cpu_v1"
RUN_MODE = "full"
SELFTEST = "--self-test" in sys.argv
MATH_CORPORA = {"math", "science", "concept", "school", "meta"}
# knowledge-graph leaf atoms to EXCLUDE from the operator core (not typed operators)
LEAF_PREFIXES = ("wikidata_", "oeis_")


def is_operator_core(short_id: str) -> bool:
    leaf = short_id.split("/")[-1].lower()
    return not any(leaf.startswith(p) for p in LEAF_PREFIXES)


def _selftest():
    assert is_operator_core("T1/inner_product") and not is_operator_core("T3/wikidata_Q123")
    assert not is_operator_core("T2/oeis_A000189")
    print("[selftest] PASS: " + ANCHOR_NAME, flush=True)


if __name__ == "__main__" and SELFTEST:
    _selftest(); sys.exit(0)


def run() -> Dict:
    from backend.substrate_index.partition import PartitionedStore
    root = REPO / "data" / "substrate_index"
    if not root.exists():
        return {"error": "no_substrate_index"}
    atoms = PartitionedStore(root).all_atoms()
    tier_of = {_norm(a.id): str(getattr(getattr(a, "tier", None), "value", getattr(a, "tier", "")) or "") for a in atoms}
    corpus_of = {_norm(a.id): str(getattr(getattr(a, "corpus", None), "value", getattr(a, "corpus", ""))).lower() for a in atoms}
    adj = defaultdict(list); real_edges = set(); has_out = set()
    for rp in root.rglob("relations.jsonl"):
        for ln in open(rp, encoding="utf-8"):
            ln = ln.strip()
            if not ln: continue
            try: r = json.loads(ln)
            except Exception: continue
            if (r.get("rel_type", "") or "").upper() in STRUCT_EDGES:
                s = _norm(r.get("src_id", "")); t = _norm(r.get("tgt_id", ""))
                if s and t and s != t:
                    real_edges.add((s, r["rel_type"].upper(), t)); adj[s].append((r["rel_type"].upper(), t)); has_out.add(s)

    def is_axiom(n):
        return tier_of.get(n, "") == "T1" or (n not in has_out)
    # OPERATOR CORE goal pool: structured-math, has outgoing, not axiom, NOT a knowledge leaf
    goal_pool = [n for n in has_out if not is_axiom(n) and corpus_of.get(n, "") in MATH_CORPORA and is_operator_core(n)]
    goal_pool.sort()  # deterministic; measure FULL pool (no sampling)
    found = sound = genuine_t1 = authoring_gap = 0
    depths = []; gap_examples = []
    for g in goal_pool:
        w = backward_chain(g, adj, is_axiom, real_edges, MAX_DEPTH)
        if w is None:
            continue
        found += 1; depths.append(len(w))
        if type_check(w, real_edges): sound += 1
        terminal = w[-1][2]
        if tier_of.get(terminal, "") == "T1":
            genuine_t1 += 1
        else:  # terminal is a non-T1 leaf -> authoring gap
            authoring_gap += 1
            if len(gap_examples) < 8:
                gap_examples.append((g, terminal))
    n = len(goal_pool)
    gap_rate = round(authoring_gap / max(found, 1), 4)
    genuine_rate = round(genuine_t1 / max(found, 1), 4)
    avg_depth = round(sum(depths) / max(len(depths), 1), 2)
    print("  OPERATOR-CORE goals: %d (wikidata/oeis leaves excluded) | proved %d" % (n, found), flush=True)
    print("  genuine-T1 termination: %d (%.4f) | authoring-gap leaves: %d (%.4f) | avg depth=%.2f | sound=%d/%d" % (
        genuine_t1, genuine_rate, authoring_gap, gap_rate, avg_depth, sound, found), flush=True)
    print("  authoring-gap rate = %.1f%% (was 62%% pre-foundation; Drill 1 predicted <30%%)" % (100 * gap_rate), flush=True)
    print("  sample authoring-gap goals (terminal non-T1 leaf):", flush=True)
    for g, t in gap_examples:
        print("    %s -> %s (tier=%s)" % (g, t, tier_of.get(t, "?")), flush=True)
    return {"n_operator_core_goals": n, "proved": found, "genuine_t1": genuine_t1, "genuine_t1_rate": genuine_rate,
            "authoring_gap": authoring_gap, "authoring_gap_rate": gap_rate, "avg_depth": avg_depth,
            "sound": sound, "sound_rate": round(sound / max(found, 1), 4), "gap_examples": gap_examples}


def verdict(r) -> Tuple[str, str]:
    if r.get("error"):
        return ("UNKNOWN", "UNKNOWN: " + r["error"])
    g = r["authoring_gap_rate"]
    s = ("Foundation-deepening (46c) OPERATOR-CORE authoring-gap = %.4f (genuine-T1 %.4f) over %d operator goals (proved %d, sound %d). "
         "Was 62%% pre-foundation; Drill 1 predicted <30%%. avg depth %.2f." % (
             g, r["genuine_t1_rate"], r["n_operator_core_goals"], r["proved"], r["sound"], r["avg_depth"]))
    if g < 0.30:
        return ("HARD_PASS", "HARD_PASS: authoring-gap %.1f%% < 30%% -- 8 Layer-0/1 foundation primitives deepened operator-core axiom termination as Drill 1 predicted. " % (100 * g) + s)
    if g > 0.50:
        return ("HARD_FAIL", "HARD_FAIL: authoring-gap %.1f%% > 50%% -- foundation primitives did NOT close the operator-core gap; Drill 1 prediction not realized; investigate (SPECIALIZES edges may not chain operators to the new primitives). " % (100 * g) + s)
    return ("MIDDLE", "MIDDLE (30-50%%): partial foundation-deepening; some operators now ground to T1 primitives, others still hit authoring-gap leaves. " + s)


if __name__ == "__main__":
    _selftest()
    print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
    out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
    v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
    metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
    write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
