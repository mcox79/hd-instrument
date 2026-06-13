"""
exp_substrate_conv_theorem_proof_tracker_cpu_v1.py -- CONV-THEOREM PROOF TRACKER: can L6-PROOF FINDER prove the convolution theorem from first principles yet? (red->green tracker) -- CPU/local (no heat), READ-ONLY.

ROUTING: Research 16th writeback Decision 3 AUTHORIZE. Closes the honest caveat from V2/V2.1: conv<->DFT showing derivation_present=True is
  only ONE typed edge, NOT a proof. This tracker runs the real L6-PROOF FINDER (backward-chaining prover, already HARD_PASS 20/20) on the
  convolution-theorem GOAL atom and asks: does it backward-chain to a FOUNDATIONAL (T1) axiom with a CHTV-sound witness? RED until Testbed
  finishes authoring the chain (DFT-linearity + pointwise-product + inverse-DFT lemmas wired as dependencies); GREEN when the apex goal
  convolution_theorem_synthesis proves to T1. When green, this is the substrate's first CROSS-DOMAIN L6-PROOF (VSA binding <-> signal
  processing) -- it proves one of its own theoretical identities from first principles. Ungated, read-only. Reuses the FINDER's
  backward_chain + type_check (single source of truth; FINDER now __main__-guarded so import has no side effects).

  STRICT criterion (stronger than the generic FINDER): "proven from first principles" = the witness must terminate at a TIER-1 axiom, NOT
  merely at a leaf (no-outgoing-edge) node -- a dead-end leaf is an authoring gap, not a foundation. So is_axiom = (tier == T1) only.

PRE-REGISTERED (tracker): GREEN/HARD_PASS iff convolution_theorem_synthesis backward-chains to a T1 axiom AND the witness is CHTV-sound
  (every edge real). PARTIAL/MIDDLE_BAND iff a chain exists but does NOT reach a T1 axiom within MAX_DEPTH (some lemma unwired -> report the
  deepest reachable frontier as the precise gap). PENDING/MIDDLE_BAND iff the goal atom is absent or has no outgoing chain yet (Testbed not
  done). HARD_FAIL iff a found witness FAILS CHTV re-verification (unsound -- non-negotiable). ASCII-only. --self-test + --smoke + metrics.json.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time, json
from collections import defaultdict, deque
from pathlib import Path
from typing import Dict, Tuple, List
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "experiments"))
from experiments._seed_checkpoint import get_output_dir, write_metrics
from exp_substrate_proof_finder_backward_chaining_cpu_v1 import backward_chain, type_check, STRUCT_EDGES, _norm
ANCHOR_NAME = "substrate_conv_theorem_proof_tracker_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
# apex goal + sub-lemmas to report (the convolution-theorem authoring target)
GOALS = ["convolution_theorem_synthesis", "dft_convolution_to_pointwise_lemma"]
# the essential lemmas the convolution theorem conv = IDFT(DFT.x .* DFT.y) must assemble (for completeness, beyond mere grounding-to-T1)
CONV_COMPONENTS = ["dft_linearity_lemma", "dft_convolution_to_pointwise_lemma", "idft_inverse_property_lemma", "pointwise_product"]
MAX_DEPTH = 8


def reachable_frontier(goal: str, adj, max_depth: int) -> List[str]:
    """Nodes reachable from goal over structural edges (for gap diagnosis when no T1 axiom is hit)."""
    q = deque([(goal, 0)]); seen = {goal}; front = []
    while q:
        n, d = q.popleft()
        if d >= max_depth: continue
        for (rt, nxt) in adj.get(n, ()):
            if nxt not in seen:
                seen.add(nxt); front.append(nxt); q.append((nxt, d + 1))
    return front


def _selftest():
    # strict T1 termination: a chain dead-ending at a non-T1 leaf is NOT proven
    real = {("G", "DEPENDS_ON", "L"), ("L", "USES", "M")}
    adj = {"G": [("DEPENDS_ON", "L")], "L": [("USES", "M")]}     # M is a non-T1 leaf
    is_t1 = lambda n: n == "AX"                                  # only AX is a T1 axiom
    assert backward_chain("G", adj, is_t1, real, 8) is None      # no T1 reachable -> PARTIAL
    real2 = dict.fromkeys(list(real) + [("M", "DEPENDS_ON", "AX")])
    adj2 = {"G": [("DEPENDS_ON", "L")], "L": [("USES", "M")], "M": [("DEPENDS_ON", "AX")]}
    w = backward_chain("G", adj2, is_t1, set(real2), 8)
    assert w is not None and w[-1][2] == "AX" and type_check(w, set(real2))
    assert "L" in reachable_frontier("G", adj, 8)
    print("[selftest] PASS: substrate_conv_theorem_proof_tracker_cpu_v1", flush=True)


if __name__ == "__main__":
    _selftest()
    if _ARGS.self_test:
        sys.exit(0)


def _build_graph(root: Path):
    from backend.substrate_index.partition import PartitionedStore
    atoms = list(PartitionedStore(root).all_atoms())
    tier_of = {_norm(a.id): str(getattr(getattr(a, "tier", None), "value", getattr(a, "tier", "")) or "") for a in atoms}
    real_edges = set(); adj = defaultdict(list); present = set(_norm(a.id) for a in atoms)
    for rp in root.rglob("relations.jsonl"):
        try:
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
        except Exception:
            continue
    return tier_of, real_edges, adj, present


def run() -> Dict:
    root = REPO / "data" / "substrate_index"
    if not root.exists():
        return {"error": "no_substrate_index"}
    tier_of, real_edges, adj, present = _build_graph(root)
    is_t1 = lambda n: tier_of.get(n, "") == "T1"            # strict: proven only when terminating at a T1 foundational axiom
    short2full = {}                                          # graph nodes are tier-prefixed (e.g. T3/foo); resolve bare goal names
    for fid in present:
        short2full.setdefault(fid.split("/")[-1].strip().lower(), fid)
    rows = []
    for g in GOALS:
        gn = short2full.get(g.split("/")[-1].strip().lower())
        if gn is None:
            rows.append({"goal": g, "state": "PENDING", "reason": "goal_atom_absent"}); continue
        w = backward_chain(gn, adj, is_t1, real_edges, MAX_DEPTH)
        if w is None:
            front = reachable_frontier(gn, adj, MAX_DEPTH)
            # frontier nodes that are NOT T1 and have no further outgoing edge = the precise unwired gap
            dead_ends = sorted(set(n for n in front if not is_t1(n) and n not in adj))
            rows.append({"goal": gn, "state": "PARTIAL", "frontier_size": len(front),
                         "dead_end_gaps": dead_ends[:8], "reason": "no_T1_axiom_within_depth"})
            continue
        sound = type_check(w, real_edges); term = w[-1][2]
        # COMPONENT COVERAGE (honest: grounding-to-T1 != assembling the theorem's essential lemmas). Check transitive reachability.
        reach = set(n.split("/")[-1].strip().lower() for n in reachable_frontier(gn, adj, MAX_DEPTH))
        comp_hit = [c for c in CONV_COMPONENTS if c in reach]
        comp_missing = [c for c in CONV_COMPONENTS if c not in reach]
        rows.append({"goal": gn, "state": ("GREEN" if sound else "UNSOUND"), "depth": len(w), "sound": sound,
                     "terminal_T1": term, "witness": [list(e) for e in w],
                     "components_reached": comp_hit, "components_missing": comp_missing,
                     "complete_assembly": (len(comp_missing) == 0)})
    apex = next((r for r in rows if r["goal"] == _norm(GOALS[0])), rows[0] if rows else {})
    for r in rows:
        if r["state"] == "GREEN":
            print("  [GREEN] %s PROVEN to T1 axiom %s depth=%d sound=%s | assembly=%s (components reached=%s, missing=%s)" % (
                r["goal"], r["terminal_T1"], r["depth"], r["sound"],
                "COMPLETE" if r["complete_assembly"] else "GROUNDED-ONLY", r["components_reached"], r["components_missing"]), flush=True)
            print("          shortest-grounding witness: %s" % (" ; ".join("%s-%s->%s" % (s, rt, t) for s, rt, t in r["witness"])), flush=True)
        elif r["state"] == "PARTIAL":
            print("  [RED/PARTIAL] %s reaches %d nodes but NO T1 axiom; unwired dead-ends: %s" % (r["goal"], r["frontier_size"], r["dead_end_gaps"]), flush=True)
        elif r["state"] == "PENDING":
            print("  [RED/PENDING] %s: %s" % (r["goal"], r["reason"]), flush=True)
        else:
            print("  [UNSOUND] %s witness failed CHTV" % r["goal"], flush=True)
    return {"rows": rows, "apex_state": apex.get("state", "PENDING"), "n_t1": sum(1 for t in tier_of.values() if t == "T1"),
            "n_edges": len(real_edges)}


def verdict(r) -> Tuple[str, str]:
    if r.get("error"):
        return ("UNKNOWN", "UNKNOWN: " + r["error"])
    apex = r["apex_state"]
    rows = r["rows"]
    if any(x["state"] == "UNSOUND" for x in rows):
        return ("HARD_FAIL", "HARD_FAIL: a found convolution-theorem witness FAILED CHTV re-verification (unsound prover) -- non-negotiable. %s" % rows)
    s = ("Convolution-theorem L6-PROOF tracker (strict: must terminate at a T1 axiom). apex(convolution_theorem_synthesis)=%s. Per-goal: %s. "
         "Graph has %d T1 axioms, %d structural edges. This tracks Testbed's live convolution-theorem chain authoring; GREEN = substrate proves "
         "conv = IDFT(DFT.x .* DFT.y) from first principles (its first cross-domain L6-PROOF).") % (
        apex, [(x["goal"], x["state"], x.get("dead_end_gaps", x.get("terminal_T1", ""))) for x in rows], r["n_t1"], r["n_edges"])
    if apex == "GREEN":
        ax = next((x for x in rows if x["goal"].split("/")[-1].lower() == GOALS[0]), rows[0])
        complete = ax.get("complete_assembly", False); miss = ax.get("components_missing", [])
        tag = ("COMPLETE ASSEMBLY -- all essential lemmas (DFT-linearity + pointwise-product + inverse-DFT) are reachable in the proof DAG"
               if complete else "GROUNDED-ONLY -- the apex soundly backward-chains to a T1 axiom, but NOT all essential convolution-theorem "
               "lemmas are reachable yet (missing: %s); the grounding is real but the full theorem assembly is still being authored" % miss)
        return ("HARD_PASS", "HARD_PASS (GREEN -- convolution theorem grounds to first principles; %s): the apex goal backward-chains to a T1 "
                "axiom with a CHTV-sound witness. Substrate's first cross-domain L6-PROOF (VSA binding <-> signal processing); upgrades conv<->DFT "
                "from THEOREM_LINKED-edge-present to THEOREM-GROUNDED-AND-VERIFIED. Honest scope: backward_chain returns the SHORTEST grounding "
                "path, which proves derivability-to-foundations (Curry-Howard inhabitation), distinct from verifying the chain traverses every "
                "essential lemma -- see assembly tag. " % tag + s)
    return ("MIDDLE_BAND", "MIDDLE_BAND (RED -- not yet proven; tracker working as intended): the convolution-theorem chain is being authored by "
            "Testbed but does not yet reach a T1 axiom (no unsound proof -- the prover correctly refuses). The dead-end gaps above are the precise "
            "remaining authoring targets; re-run when Testbed wires them to flip GREEN. " + s)


if __name__ == "__main__":
    print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
    out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
    v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
    metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
    write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
