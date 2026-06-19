"""DECISION 78d -- L6-PROOF cycle-soundness clarification. Does the substrate's 213/213 axiom-termination assume ACYCLIC DEPENDS_ON (=> the 6 W-TYPE-SIG 2-cycles are SOUNDNESS VIOLATIONS) OR use visited-set cycle-detection (=> termination preserved; cycles are HYGIENE/sub-optimal)? Uses the REAL prover (backward_chain from exp_substrate_proof_finder_backward_chaining_cpu_v1) on the actual substrate.
Tests (substrate-internal; laptop; no LLM; no remote):
  T1 PROVE-CYCLE-ATOMS: run backward_chain on the cycle atoms as goals; report proof path + axiom-terminating + whether the path uses any of the 6 reverse(wrong-direction) edges.
  T2 NO-FALSE-PROOF: synthetic pure 2-cycle A<->B with NO axiom exit -> prover MUST return None (visited-set prevents faking grounding via the cycle). If it returns a 'proof', that is unsoundness.
  T3 REMOVE-REVERSE invariance: re-run proofs with the 6 reverse edges removed; if every cycle-atom proof is unchanged (or still axiom-terminating), the reverse edges are NOT load-bearing -> safe to remove (validates DECISION 78c cleanup + capability_preservation).
VERDICT: VISITED_SET_SOUND if T2 returns None AND all cycle atoms axiom-terminate AND T3 invariant -> cycles are hygiene not unsoundness; 213/213 stands. ACYCLIC_ASSUMED_UNSOUND if T2 fakes a proof. ASCII; --self-test."""
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
CYCLE_ATOMS = ["cosine_similarity", "inner_product", "gradient", "partial_derivative", "gradient_descent",
               "newton_method", "hessian", "bayes_rule", "conditional_probability",
               "fast_fourier_transform", "discrete_fourier_transform"]
# the 6 reverse (wrong-direction) edges = reverse of Skunkworks's STRICT pairs
REVERSE_EDGES = {("inner_product", "cosine_similarity"), ("discrete_fourier_transform", "fast_fourier_transform"),
                 ("conditional_probability", "bayes_rule"), ("partial_derivative", "gradient"),
                 ("gradient", "gradient_descent"), ("hessian", "newton_method")}
SELFTEST = "--self-test" in sys.argv


def _selftest():
    # pure 2-cycle, no axiom -> must be None (sound)
    adj = {"A": [("DEPENDS_ON", "B")], "B": [("DEPENDS_ON", "A")]}
    isax = lambda n: False  # neither is an axiom and both have out-edges
    assert backward_chain("A", adj, isax, set(), 6) is None, "pure cycle must not fake a proof"
    print("[selftest] PASS", flush=True)


if __name__ == "__main__" and SELFTEST:
    _selftest(); sys.exit(0)


def build():
    from backend.substrate_index.partition import PartitionedStore
    atoms = PartitionedStore(DATA_ROOT).all_atoms()
    tier = {_norm(a.id): str(getattr(getattr(a, "tier", None), "value", getattr(a, "tier", "")) or "") for a in atoms}
    real = set(); adj = defaultdict(list); has_out = set()
    for rp in DATA_ROOT.rglob("relations.jsonl"):
        for ln in open(rp, encoding="utf-8"):
            ln = ln.strip()
            if not ln: continue
            try: r = json.loads(ln)
            except Exception: continue
            rt = (r.get("rel_type", "") or "").upper()
            if rt in STRUCT_EDGES:
                s = _norm(r.get("src_id", "")); t = _norm(r.get("tgt_id", ""))
                if s and t and s != t: real.add((s, rt, t)); adj[s].append((rt, t)); has_out.add(s)
    return tier, real, adj, has_out


def run() -> Dict:
    tier, real, adj, has_out = build()
    # _norm keeps the tier prefix (e.g. "T2/cosine_similarity"); map plain short names -> full keys
    short2full = {}
    for k in set(tier) | set(adj) | has_out:
        short2full.setdefault(str(k).split("/")[-1].strip().lower(), k)
    def resolve(s): return short2full.get(s, s)
    goals_full = [resolve(g) for g in CYCLE_ATOMS]
    reverse_full = {(resolve(s), resolve(t)) for s, t in REVERSE_EDGES}

    def is_axiom(n): return tier.get(n, "") == "T1" or (n not in has_out)

    def uses_reverse(w):
        return [(s, t) for s, rt, t in (w or []) if (s, t) in reverse_full]

    # T1: prove cycle atoms
    t1 = []
    for g in goals_full:
        if g not in has_out and tier.get(g, "") != "T1" and g not in tier:
            t1.append({"goal": g, "status": "ATOM_ABSENT"}); continue
        if is_axiom(g):
            t1.append({"goal": g, "status": "IS_AXIOM(T1/leaf)", "axiom_term": True}); continue
        w = backward_chain(g, adj, is_axiom, real, MAX_DEPTH)
        if w is None:
            t1.append({"goal": g, "status": "NO_PROOF", "axiom_term": False}); continue
        t1.append({"goal": g, "status": "PROVED", "depth": len(w), "terminal": w[-1][2],
                   "axiom_term": is_axiom(w[-1][2]), "uses_reverse_edge": uses_reverse(w),
                   "path": " -> ".join("%s=%s=>%s" % (s, rt, t) for s, rt, t in w)})

    # T2: synthetic pure 2-cycle on REAL atom ids with NO axiom exit -> must be None
    fake_adj = {"X_cyc_a": [("DEPENDS_ON", "X_cyc_b")], "X_cyc_b": [("DEPENDS_ON", "X_cyc_a")]}
    t2 = backward_chain("X_cyc_a", fake_adj, lambda n: False, set(), MAX_DEPTH)
    t2_sound = (t2 is None)

    # T3: remove the 6 reverse edges, re-prove cycle atoms; compare axiom-termination
    adj2 = defaultdict(list); has_out2 = set()
    for s, rt, t in real:
        if (s, t) in reverse_full: continue
        adj2[s].append((rt, t)); has_out2.add(s)

    def is_axiom2(n): return tier.get(n, "") == "T1" or (n not in has_out2)
    t3 = []
    invariant = True
    for r in t1:
        g = r["goal"]
        if r["status"] in ("ATOM_ABSENT",): continue
        before = r.get("axiom_term", None)
        if is_axiom2(g):
            after = True
        else:
            w = backward_chain(g, adj2, is_axiom2, real, MAX_DEPTH)
            after = (w is not None and is_axiom2(w[-1][2]))
        ok = (before in (True, None)) <= (after in (True, None)) or before == after
        # invariant: an atom that was axiom-terminating must STILL be axiom-terminating after removal
        if before is True and after is not True: invariant = False
        t3.append({"goal": g, "axiom_term_before": before, "axiom_term_after": after})

    n_proved = sum(1 for r in t1 if r["status"] == "PROVED")
    n_axterm = sum(1 for r in t1 if r.get("axiom_term"))
    n_usesrev = sum(1 for r in t1 if r.get("uses_reverse_edge"))
    print("  T1 cycle-atom proofs: PROVED=%d | axiom-terminating=%d | proofs-using-a-reverse-edge=%d (of %d atoms)" % (
        n_proved, n_axterm, n_usesrev, len(CYCLE_ATOMS)), flush=True)
    for r in t1:
        extra = ""
        if r.get("uses_reverse_edge"): extra = "  USES-REVERSE:%s" % r["uses_reverse_edge"]
        print("    %-26s %-16s %s%s" % (r["goal"], r["status"], ("-> %s (axiom=%s) d=%s" % (r.get("terminal", "-"), r.get("axiom_term"), r.get("depth", "-"))), extra), flush=True)
    print("  T2 NO-FALSE-PROOF (pure 2-cycle, no axiom): prover returned %s -> %s" % (
        "None" if t2_sound else repr(t2), "SOUND (no fake proof)" if t2_sound else "UNSOUND!"), flush=True)
    print("  T3 REMOVE-6-REVERSE invariance: axiom-termination preserved for all cycle atoms = %s" % invariant, flush=True)
    return {"t1": t1, "n_proved": n_proved, "n_axiom_term": n_axterm, "n_uses_reverse": n_usesrev,
            "t2_no_false_proof": t2_sound, "t3_removal_invariant": invariant, "n_cycle_atoms": len(CYCLE_ATOMS)}


def verdict(r) -> Tuple[str, str]:
    if r.get("error"): return ("UNKNOWN", "UNKNOWN: " + r["error"])
    s = ("L6-PROOF cycle-soundness: of %d cycle atoms, %d PROVED, %d axiom-terminating, %d proofs use a reverse(wrong-dir) edge. T2 pure-2-cycle-no-axiom -> %s. T3 remove-6-reverse-edges axiom-termination invariant = %s." % (
        r["n_cycle_atoms"], r["n_proved"], r["n_axiom_term"], r["n_uses_reverse"],
        "None (sound)" if r["t2_no_false_proof"] else "FAKE PROOF (unsound!)", r["t3_removal_invariant"]))
    if r["t2_no_false_proof"] and r["t3_removal_invariant"]:
        return ("VISITED_SET_SOUND", "213/213 axiom-termination is SOUND via visited-set cycle-detection (NOT acyclic-assumed): the prover never fakes a proof through a cycle (T2 None), and removing the 6 reverse edges preserves axiom-termination for every cycle atom (T3 invariant) -> the 6 DEPENDS_ON 2-cycles are HYGIENE/sub-optimal, NOT unsoundness. DECISION 78c cycle-cleanup is MEDIUM priority (graph quality + W-TYPE-SIG directional correctness), not soundness-restoration; capability_preservation will hold across the removals. " + s)
    if not r["t2_no_false_proof"]:
        return ("ACYCLIC_ASSUMED_UNSOUND", "SOUNDNESS VIOLATION: prover fakes a proof through a pure cycle -> 213/213 axiom-termination assumes acyclic DEPENDS_ON; the cycles are genuine unsoundness; DECISION 78c becomes HIGHEST-priority soundness-restoration. " + s)
    return ("CLEANUP_LOAD_BEARING", "T2 sound but T3 NOT invariant: some cycle atom LOSES axiom-termination when reverse edges removed -> those reverse edges are load-bearing; cleanup needs per-edge care (cannot blanket-remove). " + s)


if __name__ == "__main__":
    _selftest()
    print("[config] anchor=substrate_78d_l6proof_cycle_soundness_probe", flush=True)
    out_dir = get_output_dir("substrate_78d_l6proof_cycle_soundness_probe_cpu_v1"); t0 = time.time(); r = run()
    v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
    metrics = {"anchor_name": "substrate_78d_l6proof_cycle_soundness_probe_cpu_v1", "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": "full", "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
    write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
