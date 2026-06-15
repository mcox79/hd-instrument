"""DECISION 85a (Exp-Dev capability pre-check) -- atom-MERGE PILOT svd -> singular_value_decomposition. Simulate the merge structurally and verify it is SAFE before Testbed executes (substrate's FIRST atom-merge = namespace consolidation + dedup, per 67th honest signal). Canonical = singular_value_decomposition (DECISION 85a). For every structural edge incident to ANY id-form whose short-name is 'svd', re-point svd -> canonical; drop resulting self-loops; delete svd. Then check: (a) axiom-termination preserved for the full goal pool; (b) no dangling references (every edge endpoint still resolves to an existing atom); (c) edge/id-form inventory (confirm Skunkworks's 35-edge / 3-id-form count). Substrate-internal; laptop; structural (no bge); no LLM. ASCII; --self-test.
HARD-PASS: axiom-termination 0 regressions + 0 dangling + edges re-pointed cleanly. HARD-FAIL: any regression/dangling -> merge protocol not yet safe."""
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
NONCANON = "svd"
CANON = "singular_value_decomposition"
SELFTEST = "--self-test" in sys.argv


def _short(x): return str(x).split("::")[-1].split("/")[-1].strip().lower()


def _selftest():
    assert _short("math::T1/svd") == "svd"
    print("[selftest] PASS", flush=True)


if __name__ == "__main__" and SELFTEST:
    _selftest(); sys.exit(0)


def run() -> Dict:
    from backend.substrate_index.partition import PartitionedStore
    atoms = list(PartitionedStore(DATA_ROOT).all_atoms())
    tier = {_norm(a.id): str(getattr(getattr(a, "tier", None), "value", getattr(a, "tier", "")) or "") for a in atoms}
    corpus = {_norm(a.id): str(getattr(getattr(a, "corpus", None), "value", getattr(a, "corpus", ""))).lower() for a in atoms}
    atom_ids = {_norm(a.id) for a in atoms}
    # id-forms present for each name
    idforms = defaultdict(set)
    for a in atoms:
        idforms[_short(a.id)].add(_norm(a.id))
    # structural edges (for proof/capability) PLUS all-rel-type incidence (for complete dangling detection:
    # a SUPERSEDED_BY / HAS_USERS / DUAL edge to the non-canonical atom would dangle if missed -- Skunkworks's note).
    real = []                 # STRUCT_EDGES only (proof graph)
    all_incident = []         # ANY rel-type edge touching noncanon (for dangling + re-point completeness)
    edge_idforms = set()
    for rp in DATA_ROOT.rglob("relations.jsonl"):
        for ln in open(rp, encoding="utf-8"):
            ln = ln.strip()
            if not ln: continue
            try: r = json.loads(ln)
            except Exception: continue
            rt = (r.get("rel_type", "") or "").upper()
            s = _norm(r.get("src_id", "")); t = _norm(r.get("tgt_id", ""))
            if not (s and t and s != t): continue
            if rt in STRUCT_EDGES:
                real.append((s, rt, t))
            if _short(s) == NONCANON or _short(t) == NONCANON:
                all_incident.append((s, rt, t))
                if _short(s) == NONCANON: edge_idforms.add(s)
                if _short(t) == NONCANON: edge_idforms.add(t)
    # canonical id-form: prefer a CANON atom id; else build the qualified form
    canon_ids = sorted(idforms.get(CANON, set()))
    canon_id = canon_ids[0] if canon_ids else CANON
    n_incident = len(all_incident)                       # ALL rel-types touching svd (re-point completeness)
    n_incident_struct = sum(1 for s, rt, t in real if _short(s) == NONCANON or _short(t) == NONCANON)
    incident_reltypes = sorted({rt for _, rt, _ in all_incident})

    def remap(x): return canon_id if _short(x) == NONCANON else x
    # build BEFORE and AFTER (merged) directed graphs
    def graph(edges):
        adj = defaultdict(list); has_out = set()
        for s, rt, t in edges:
            adj[s].append((rt, t)); has_out.add(s)
        return adj, has_out
    adjB, hoB = graph(real)
    merged = []
    selfloops = 0
    for s, rt, t in real:
        ns, nt = remap(s), remap(t)
        if ns == nt: selfloops += 1; continue   # svd->canon style self-loop after merge: drop
        merged.append((ns, rt, nt))
    adjA, hoA = graph(merged)
    # tier map after merge: svd's tier folds into canon (canon keeps its own tier)
    tierA = dict(tier)
    def axB(n): return tier.get(n, "") == "T1" or (n not in hoB)
    def axA(n): return tierA.get(n, "") == "T1" or (n not in hoA)
    # dangling check across ALL rel-types: after merge (svd id-forms removed, canon kept), re-point every
    # incident edge form-agnostically; any endpoint that fails to resolve = dangling (the HARD-FAIL mode).
    atoms_after = (atom_ids - idforms.get(NONCANON, set())) | {canon_id}
    dangling = set()
    for s, rt, t in all_incident:
        ns, nt = remap(s), remap(t)
        if ns == nt: continue                            # self-loop collapses on merge
        if ns not in atoms_after: dangling.add(ns)
        if nt not in atoms_after: dangling.add(nt)
    # also confirm no STRUCT merged edge dangles (proof-graph integrity)
    for s, rt, t in merged:
        if s not in atoms_after: dangling.add(s)
        if t not in atoms_after: dangling.add(t)
    # capability: axiom-termination for goal pool before vs after
    goal_pool = [n for n in hoB if not axB(n) and corpus.get(n, "") in MATH_CORPORA]

    def term(g, adj, isax):
        if isax(g): return True
        w = backward_chain(g, adj, isax, set(), MAX_DEPTH)
        return w is not None and isax(w[-1][2])
    before = after = 0; regressed = []
    for g in goal_pool:
        gB = g
        gA = remap(g)
        b = term(gB, adjB, axB); a = term(gA, adjA, axA)
        before += int(b); after += int(a)
        if b and not a: regressed.append(g)
    cap_ok = len(regressed) == 0 and len(dangling) == 0
    print("  atom-MERGE PILOT pre-check: %s -> %s" % (NONCANON, CANON), flush=True)
    print("  svd id-forms (atoms): %s | svd id-forms (in edges): %s | canonical id: %s" % (
        sorted(idforms.get(NONCANON, set())), sorted(edge_idforms), canon_id), flush=True)
    print("  edges incident to svd: ALL-rel-types=%d (types=%s) | STRUCT-only=%d | self-loops dropped=%d" % (
        n_incident, incident_reltypes, n_incident_struct, selfloops), flush=True)
    print("  capability: goal pool=%d | axiom-terminating before=%d after=%d | regressed=%d | dangling refs=%d" % (
        len(goal_pool), before, after, len(regressed), len(dangling)), flush=True)
    if dangling: print("    DANGLING:", sorted(dangling)[:10], flush=True)
    if regressed: print("    REGRESSED:", regressed[:10], flush=True)
    return {"noncanon": NONCANON, "canon": canon_id, "svd_atom_idforms": sorted(idforms.get(NONCANON, set())),
            "svd_edge_idforms": sorted(edge_idforms), "edges_incident": n_incident, "selfloops_dropped": selfloops,
            "goal_pool": len(goal_pool), "term_before": before, "term_after": after,
            "regressed": regressed[:30], "dangling": sorted(dangling)[:30], "cap_preserved": cap_ok}


def verdict(r) -> Tuple[str, str]:
    if r.get("error"): return ("UNKNOWN", "UNKNOWN: " + r["error"])
    s = ("atom-MERGE pilot %s->%s: %d edges incident (id-forms: atoms=%s, edges=%s); %d self-loops dropped; capability: %d->%d axiom-terminating, %d regressed, %d dangling." % (
        r["noncanon"], r["canon"], r["edges_incident"], r["svd_atom_idforms"], r["svd_edge_idforms"],
        r["selfloops_dropped"], r["term_before"], r["term_after"], len(r["regressed"]), len(r["dangling"])))
    if r["cap_preserved"]:
        return ("HARD_PASS", "atom-MERGE pilot is SAFE: re-pointing all svd edges to %s preserves axiom-termination (0 regressions) with 0 dangling references -> Testbed can execute the pilot with capability_preservation=1.0 expected. " % r["canon"] + s)
    return ("HARD_FAIL", "atom-MERGE pilot NOT yet safe: dangling refs or capability regression after re-point -> merge protocol needs fix before execution. " + s)


if __name__ == "__main__":
    _selftest()
    print("[config] anchor=substrate_85a_atom_merge_pilot_svd_precheck", flush=True)
    out_dir = get_output_dir("substrate_85a_atom_merge_pilot_svd_precheck_cpu_v1"); t0 = time.time(); r = run()
    v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
    metrics = {"anchor_name": "substrate_85a_atom_merge_pilot_svd_precheck_cpu_v1", "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": "full", "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
    write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
