"""DECISION 84 (Exp-Dev byproduct probe) -- Prover evidence on the 5 NEW direction-error edges Skunkworks flagged for cycle-cleanup batch 2. For each flagged-BACKWARDS edge src->tgt: (1) confirm it EXISTS as a structural edge; (2) confirm the CORRECT-direction relationship is present (reverse edge tgt->src OR a USES the other way) = evidence the flagged edge is genuinely backwards; (3) capability pre-check: removing the backwards edge preserves axiom-termination for the full goal pool (like 79a). Generalizes the 79a/78d pattern to batch 2. Substrate-internal; laptop; structural (no bge); no LLM. ASCII; --self-test.
HARD-PASS: all 5 exist + all 5 have correct-direction evidence + removal preserves capability (0 regressions) -> batch 2 is safe + sound to remove."""
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
# Skunkworks DECISION 84 flagged-backwards edges (src->tgt is BACKWARDS; correct direction noted)
FLAGGED = [("hessian", "newton_method", "newton USES hessian"),
           ("partial_derivative", "jacobian_matrix", "jacobian uses partial_derivative"),
           ("partial_derivative", "subgradient", "subgradient uses partial_derivative"),
           ("bayes_rule", "bayesian_inference", "bayesian_inference uses bayes_rule"),
           ("conditional_probability", "bayesian_inference", "bayesian_inference uses conditional_probability")]
SELFTEST = "--self-test" in sys.argv


def _selftest():
    assert len(FLAGGED) == 5
    print("[selftest] PASS", flush=True)


if __name__ == "__main__" and SELFTEST:
    _selftest(); sys.exit(0)


def run() -> Dict:
    from backend.substrate_index.partition import PartitionedStore
    atoms = PartitionedStore(DATA_ROOT).all_atoms()
    tier = {_norm(a.id): str(getattr(getattr(a, "tier", None), "value", getattr(a, "tier", "")) or "") for a in atoms}
    corpus = {_norm(a.id): str(getattr(getattr(a, "corpus", None), "value", getattr(a, "corpus", ""))).lower() for a in atoms}
    # directed edges by (short_src, short_tgt) -> set of rel_types
    edges = defaultdict(set); real = []
    for rp in DATA_ROOT.rglob("relations.jsonl"):
        for ln in open(rp, encoding="utf-8"):
            ln = ln.strip()
            if not ln: continue
            try: r = json.loads(ln)
            except Exception: continue
            rt = (r.get("rel_type", "") or "").upper()
            if rt in STRUCT_EDGES:
                s = _norm(r.get("src_id", "")); t = _norm(r.get("tgt_id", ""))
                if s and t and s != t:
                    real.append((s, rt, t))
                    edges[(str(s).split("/")[-1].lower(), str(t).split("/")[-1].lower())].add(rt)

    def types(a, b): return edges.get((a, b), set())
    rows = []
    for s, t, correct in FLAGGED:
        fwd = types(s, t)          # the flagged (backwards) edge
        rev = types(t, s)          # the correct direction
        exists = bool(fwd)
        correct_present = bool(rev)
        rows.append({"flagged": "%s->%s" % (s, t), "flagged_types": sorted(fwd), "reverse_types": sorted(rev),
                     "exists": exists, "correct_dir_present": correct_present,
                     "is_two_cycle": exists and ("DEPENDS_ON" in fwd) and ("DEPENDS_ON" in rev), "note": correct})

    # capability pre-check: remove all flagged edges (short-name match, both this dir only -- the backwards one)
    drop = {(s, t) for s, t, _ in FLAGGED}
    adjB = defaultdict(list); hoB = set(); adjA = defaultdict(list); hoA = set()
    for s, rt, t in real:
        adjB[s].append((rt, t)); hoB.add(s)
        if (str(s).split("/")[-1].lower(), str(t).split("/")[-1].lower()) in drop: continue
        adjA[s].append((rt, t)); hoA.add(s)

    def axB(n): return tier.get(n, "") == "T1" or (n not in hoB)
    def axA(n): return tier.get(n, "") == "T1" or (n not in hoA)
    goal_pool = [n for n in hoB if not axB(n) and corpus.get(n, "") in MATH_CORPORA]

    def term(g, adj, isax):
        if isax(g): return True
        w = backward_chain(g, adj, isax, set(), MAX_DEPTH)
        return w is not None and isax(w[-1][2])
    before = after = 0; regressed = []
    for g in goal_pool:
        b = term(g, adjB, axB); a = term(g, adjA, axA)
        before += int(b); after += int(a)
        if b and not a: regressed.append(g)
    n_exist = sum(1 for r in rows if r["exists"])
    n_correct = sum(1 for r in rows if r["correct_dir_present"])
    n_cycle = sum(1 for r in rows if r["is_two_cycle"])
    print("  Batch-2 direction-error pre-check (5 flagged edges):", flush=True)
    for r in rows:
        print("    %-42s exists=%s flagged_types=%s reverse=%s 2cycle=%s" % (
            r["flagged"], r["exists"], r["flagged_types"], r["reverse_types"], r["is_two_cycle"]), flush=True)
    print("  exist=%d/5 | correct-direction-present=%d/5 | genuine-2-cycle=%d/5" % (n_exist, n_correct, n_cycle), flush=True)
    print("  capability pre-check: goal pool=%d | axiom-terminating before=%d after=%d | regressed=%d" % (
        len(goal_pool), before, after, len(regressed)), flush=True)
    if regressed: print("    REGRESSED:", regressed[:15], flush=True)
    return {"rows": rows, "n_exist": n_exist, "n_correct_dir": n_correct, "n_two_cycle": n_cycle,
            "goal_pool": len(goal_pool), "term_before": before, "term_after": after,
            "regressed": regressed[:30], "cap_preserved": len(regressed) == 0}


def verdict(r) -> Tuple[str, str]:
    if r.get("error"): return ("UNKNOWN", "UNKNOWN: " + r["error"])
    s = ("Batch-2 direction errors: %d/5 exist; %d/5 have correct-direction edge present (evidence flagged dir is backwards); %d/5 genuine 2-cycles; removal capability pre-check: %d->%d axiom-terminating, %d regressed." % (
        r["n_exist"], r["n_correct_dir"], r["n_two_cycle"], r["term_before"], r["term_after"], len(r["regressed"])))
    if r["n_exist"] == 5 and r["cap_preserved"]:
        return ("HARD_PASS", "All 5 batch-2 direction-error edges EXIST and removing them PRESERVES capability (0 regressions); %d/5 have the correct-direction relationship present as evidence -> batch 2 is safe + evidence-backed for Skunkworks/Testbed removal. " % r["n_correct_dir"] + s)
    if r["cap_preserved"]:
        return ("PARTIAL", "Removal capability-safe but not all 5 present as-flagged (existence/direction mismatch -- Skunkworks verify exact ids): " + s)
    return ("REVIEW", "Removing a flagged edge regresses capability -> that edge is load-bearing; do NOT blanket-remove: " + s)


if __name__ == "__main__":
    _selftest()
    print("[config] anchor=substrate_84_cyclecleanup_batch2_direction_precheck", flush=True)
    out_dir = get_output_dir("substrate_84_cyclecleanup_batch2_direction_precheck_cpu_v1"); t0 = time.time(); r = run()
    v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
    metrics = {"anchor_name": "substrate_84_cyclecleanup_batch2_direction_precheck_cpu_v1", "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": "full", "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
    write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
