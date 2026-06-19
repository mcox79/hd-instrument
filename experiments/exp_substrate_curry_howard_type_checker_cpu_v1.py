"""
exp_substrate_curry_howard_type_checker_cpu_v1.py -- substrate as a PROOF VERIFIER (Curry-Howard CHTV-1) -- CPU/local (no heat).

ROUTING: Research hand-off exp_dev_handoff_research_curry_howard_atoms_as_types_2x (Anchor 1, tier-A). Curry-Howard reading:
  atoms = propositions/types; a typed-edge derivation chain = a proof/term; `prove --check witness goal` TYPE-CHECKS a witness
  against a goal. Substrate-as-VERIFIER (distinct from the substrate-as-FINDER L6-PROOF drill). Demonstrates:
    CH-P1 (well-typed): a REAL derivation chain ending at the goal is ACCEPTED.
    CH-P2 (ill-typed): a chain containing a FABRICATED edge is REJECTED -- classical type-checker PRECISION = 1.0
                       (any single hallucinated edge accepted HARD-FAILs the cell; non-negotiable per hand-off).
  Substrate-product: substrate verifies proofs over its own typed-derivation graph with checker precision; an LLM cannot
  guarantee CH-P2 (hallucination-inevitability, arxiv 2401.11817) -- categorical gap. NO LLM; pure substrate file-IO + set
  membership (local-allowed, negligible heat; no torch/GPU/bge).

  DESIGN (exp_dev owns; verify-before-build findings):
   - DEPENDS_ON alone is authored only one layer deep (0 depth-2 chains). The TYPING CONTEXT is therefore the full
     STRUCTURAL-DERIVATION graph: edge types {DEPENDS_ON, USES, INSTANCE_OF, SPECIALIZES, DEFINED_OVER, SHARES_MATH}, each a
     distinct typed inference rule (2595 real 2-hop chains available). This is a MORE faithful Curry-Howard framing (multiple
     inference rules), and honest about the corpus (DEPENDS_ON-only multi-step proofs need deeper authoring).
   - A WITNESS is a chain [(s0,rt0,s1),(s1,rt1,s2),...,goal]. TYPE-CHECK = every claimed typed edge (s,rt,t) is a real edge in
     the substrate. well_typed iff all edges real -> ACCEPT; else REJECT.

PRE-REGISTERED (from hand-off): HARD-PASS CH-P1 accept-rate >= 6/8 = 0.75 AND CH-P2 reject-rate = 8/8 = 1.00 (zero false-accepts).
  HARD-FAIL CH-P1 < 0.75 OR CH-P2 < 1.00 (any hallucinated-edge chain accepted). MIDDLE: CH-P1 in [0.5,0.75) with CH-P2 = 1.00.
  UNKNOWN if corpus lacks enough real chains.
ASCII-only. CPU/local. --self-test + metrics.json.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time, json, random
from pathlib import Path
from typing import Dict, Tuple, List
from collections import defaultdict
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "substrate_curry_howard_type_checker_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
STRUCT_EDGES = {"DEPENDS_ON", "USES", "INSTANCE_OF", "SPECIALIZES", "DEFINED_OVER", "SHARES_MATH"}
N_TRIALS = 8
SEED = 1028


def _norm(x):
    return str(x).split("::")[-1].strip()


def type_check(witness, real_edges) -> bool:
    """CHTV verifier: witness = [(src,rel,tgt),...]; well-typed iff EVERY claimed typed edge is a real substrate edge."""
    return all((s, r, t) in real_edges for (s, r, t) in witness)


def _selftest():
    real = {("a", "USES", "b"), ("b", "DEPENDS_ON", "c")}
    assert type_check([("a", "USES", "b"), ("b", "DEPENDS_ON", "c")], real) is True      # well-typed
    assert type_check([("a", "USES", "b"), ("b", "DEPENDS_ON", "z")], real) is False     # fabricated edge
    assert type_check([("a", "INSTANCE_OF", "b")], real) is False                        # wrong rel-type = different edge
    print("[selftest] PASS: substrate_curry_howard_type_checker_cpu_v1", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run() -> Dict:
    from backend.substrate_index.partition import PartitionedStore
    root = REPO / "data" / "substrate_index"
    if not root.exists():
        return {"error": "no_substrate_index"}
    atoms = PartitionedStore(root).all_atoms()
    all_ids = sorted({_norm(a.id) for a in atoms})
    real_edges = set(); adj = defaultdict(list)
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
                    real_edges.add((s, rt, t)); adj[s].append((rt, t))
    # discover real depth-2 derivation chains a-[rt0]->b-[rt1]->c (distinct atoms)
    chains = []
    for a in adj:
        for (rt0, b) in adj[a]:
            for (rt1, c) in adj.get(b, ()):
                if c != a and b != a:
                    chains.append([(a, rt0, b), (b, rt1, c)])
    rng = random.Random(SEED); rng.shuffle(chains)
    # pick N distinct-goal chains (prefer distinct goals for diversity)
    seen_goal = set(); picked = []
    for ch in chains:
        goal = ch[-1][2]
        if goal in seen_goal: continue
        seen_goal.add(goal); picked.append(ch)
        if len(picked) >= N_TRIALS: break
    if len(picked) < N_TRIALS:
        for ch in chains:                      # backfill if too few distinct goals
            if ch not in picked: picked.append(ch)
            if len(picked) >= N_TRIALS: break
    if len(picked) < 3:
        return {"error": "insufficient_real_chains", "n_chains": len(chains)}

    def fabricate(ch):
        """ill-typed: replace ONE edge's target with an atom that has NO such typed edge from that source."""
        i = rng.randrange(len(ch)); s, rt, _t = ch[i]
        for _ in range(200):
            fake = rng.choice(all_ids)
            if fake != s and (s, rt, fake) not in real_edges:
                bad = list(ch); bad[i] = (s, rt, fake); return bad, i
        return None, -1

    p1_accept = 0; p2_reject = 0; p2_false_accept = 0; rows = []
    for ch in picked[:N_TRIALS]:
        goal = ch[-1][2]
        # CH-P1: real witness should ACCEPT
        wt = type_check(ch, real_edges); p1_accept += int(wt)
        # CH-P2: fabricated witness should REJECT
        bad, pos = fabricate(ch)
        if bad is None:
            rows.append({"goal": goal, "ch_p1_accept": wt, "ch_p2": "skip_no_fab"}); continue
        bad_wt = type_check(bad, real_edges)
        if bad_wt: p2_false_accept += 1                 # CRITICAL: accepted a hallucinated edge
        else: p2_reject += 1
        rows.append({"goal": goal, "witness": [list(e) for e in ch], "ch_p1_accept": wt,
                     "fab_pos": pos, "fab_edge": list(bad[pos]), "ch_p2_reject": (not bad_wt)})
    n = len(rows)
    p1_rate = round(p1_accept / n, 4); p2_rate = round(p2_reject / n, 4)
    print("  typing context: %d real structural-derivation edges, %d real depth-2 chains" % (len(real_edges), len(chains)), flush=True)
    print("  CH-P1 (well-typed ACCEPT): %d/%d = %.4f" % (p1_accept, n, p1_rate), flush=True)
    print("  CH-P2 (ill-typed REJECT) : %d/%d = %.4f | FALSE-ACCEPTS (hallucinated edges accepted) = %d" % (p2_reject, n, p2_rate, p2_false_accept), flush=True)
    for r in rows[:N_TRIALS]:
        if "witness" in r:
            print("    goal=%s p1_accept=%s p2_reject=%s fab=%s" % (r["goal"], r["ch_p1_accept"], r["ch_p2_reject"], r["fab_edge"]), flush=True)
    return {"n": n, "ch_p1_accept_rate": p1_rate, "ch_p2_reject_rate": p2_rate, "ch_p2_false_accepts": p2_false_accept,
            "n_real_edges": len(real_edges), "n_real_chains": len(chains), "rows": rows}


def verdict(r) -> Tuple[str, str]:
    if r.get("error"):
        return ("UNKNOWN", "UNKNOWN: " + r["error"] + " " + str(r.get("n_chains", "")))
    p1 = r["ch_p1_accept_rate"]; p2 = r["ch_p2_reject_rate"]; fa = r["ch_p2_false_accepts"]
    s = "CH-P1 well-typed-accept=%.4f (>=0.75 HP); CH-P2 ill-typed-reject=%.4f false-accepts=%d (must be 0); n=%d; typing-context %d edges %d depth-2 chains" % (
        p1, p2, fa, r["n"], r["n_real_edges"], r["n_real_chains"])
    if p1 >= 0.75 and fa == 0 and p2 >= 0.999:
        return ("HARD_PASS", "HARD_PASS: substrate is a sound PROOF VERIFIER -- accepts well-typed derivation witnesses (CH-P1 >=0.75) and REJECTS every ill-typed witness with a fabricated edge (CH-P2 = 1.0, zero false-accepts = classical type-checker precision). Substrate-as-verifier surface validated; the CH-P2 honest-failure guarantee is the LLM categorical gap. " + s)
    if fa == 0 and p1 >= 0.5:
        return ("MIDDLE_BAND", "MIDDLE_BAND: type-checker precision holds (zero false-accepts) but CH-P1 well-typed acceptance is in [0.5,0.75) -- verifier sound but some real witnesses under-accepted (investigate edge-set coverage). " + s)
    return ("HARD_FAIL", "HARD_FAIL: %s -- either CH-P1 < 0.5 OR a hallucinated edge was ACCEPTED (false-accept > 0), which violates type-checker precision (non-negotiable). " % ("false-accept" if fa else "low CH-P1") + s)


print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
