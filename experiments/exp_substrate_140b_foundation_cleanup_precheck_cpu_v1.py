"""DECISION 140b -- Exp-Dev per-atom pre-check on Skunkworks's foundation-cleanup batch (70 backwards edges across 47 T1 atoms; prereq for gap-driven loop). VERIFICATION ONLY (Testbed executes; this cell does NOT mutate). Substrate-internal; CPU; ASCII; --self-test.

QUALIFIED-ID BASED (collision-safe): classification uses the atom's authoritative TIER ATTRIBUTE (a.tier), NOT the qualified-id PATH. This matters: Skunkworks's tier-inversion heuristic used the PATH (math::T1/...); some atoms have a PATH that disagrees with the tier FIELD (e.g. math::T1/bayes_rule whose tier attr is T2). The forward-walk / L6-PROOF axiom = T1 by FIELD, so the FIELD is authoritative for whether an edge is truly backwards.

PER ATOM (Tier A 35 leaf-safe REMOVE + Tier B 12 leaf-risk REMOVE+RESCUE):
  1. CLASSIFY (qualified, by attr-tier): edge EXISTS + tier(src)<tier(tgt) -> genuine backwards (CLEARED). If tier(src)>=tier(tgt) under the FIELD -> NOT backwards (legitimate dependency) -> DO NOT REMOVE; resolve.
  2. PATH/ATTR mismatch: flag atoms whose qualified-id path-tier != tier-field -> the spec mis-classified via the path; needs resolve (fix the tier FIELD if genuinely foundational, else DROP the removes).
  3. REMOVE-vs-RETIER (tier-placement flags): if target heavily depended-on (high DEPENDS_ON in-degree) -> RETIER target; else REMOVE.
  4. LEAF-STRAND + MONOTONE (batch): forward-walk reachability over removals + Tier-B forward rescues (reuses 88c primitive, _short-conservative) -> 0 stranded, 0 new violations.
HARD-PASS: every removal is a verified backwards edge (by attr-tier), 0 stranded, 0 new monotone, all flags resolved with a data-backed recommendation. PARTIAL: classification mismatches need resolution before ratify (precise drop-or-retier list). HARD-FAIL: a removal strands a consumer."""
from __future__ import annotations
import sys, json, time
from pathlib import Path
from collections import defaultdict
from typing import Dict, Tuple
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
from experiments.exp_substrate_88c_forward_walk_reachability_precheck_cpu_v1 import load, precheck_batch, _short, FORWARD, TIER_NUM
DATA_ROOT = REPO / "data" / "substrate_index"
SPEC = DATA_ROOT / "skunkworks_T1_foundation_backwards_edge_fix_spec_2026-06-15.jsonl"
TNUM = {"T1": 1, "T2": 2, "T2_FAM": 2, "T3": 3, "T4": 4}

TIER_B_RESCUE = {
    "brownian_motion": ("random_variable", "DEPENDS_ON"), "discrete_optimization": ("set", "DEPENDS_ON"),
    "dynamic_programming_bellman": ("set", "DEPENDS_ON"), "ergodicity": ("markov_chain", "DEPENDS_ON"),
    "graph_general": ("set", "DEPENDS_ON"), "group_axioms": ("proposition", "INSTANCE_OF"),
    "importance_sampling": ("probability_distribution", "DEPENDS_ON"), "lyapunov_stability": ("ode", "DEPENDS_ON"),
    "monte_carlo": ("random_variable", "DEPENDS_ON"), "shortest_path": ("graph_topology", "DEPENDS_ON"),
    "tensor": ("vector_space", "DEPENDS_ON"), "total_probability": ("conditional_probability", "DEPENDS_ON"),
}
TIER_PLACEMENT_FLAGS = {"brownian_motion", "dynamic_programming_bellman", "monte_carlo", "total_probability"}
SELFTEST = "--self-test" in sys.argv


def _path_tier(qid): return str(qid).split("::")[-1].split("/")[0]


def _selftest():
    assert TNUM["T1"] == 1 and _path_tier("math::T1/x") == "T1"; print("[selftest] PASS", flush=True)


if __name__ == "__main__" and SELFTEST:
    _selftest(); sys.exit(0)


def run() -> Dict:
    from backend.substrate_index.partition import PartitionedStore
    ps = PartitionedStore(DATA_ROOT)
    attr = {}                                            # qualified_id -> tier FIELD (authoritative)
    id_of_qid = {}                                       # qualified_id -> a.id (relations use a.id = 'T1/bayes_rule')
    for a in ps.all_atoms():
        attr[a.qualified_id] = str(getattr(getattr(a, "tier", None), "value", getattr(a, "tier", "")) or "")
        id_of_qid[a.qualified_id] = a.id
    # relations are keyed by a.id (NOT qualified_id); existence + DEPENDS_ON in-degree by a.id
    edgeset = set(); dep_indeg = defaultdict(int)
    for rp in DATA_ROOT.rglob("relations.jsonl"):
        for ln in open(rp, encoding="utf-8"):
            ln = ln.strip()
            if not ln: continue
            try: r = json.loads(ln)
            except Exception: continue
            s = r.get("src_id", ""); t = r.get("tgt_id", ""); rt = (r.get("rel_type", "") or "").upper()
            if s and t:
                edgeset.add((s, t, rt))
                if rt in FORWARD: dep_indeg[t] += 1

    spec = [json.loads(l) for l in open(SPEC, encoding="utf-8") if l.strip()]
    atoms_spec = [r for r in spec if r.get("atom")]
    cleared = []; not_backwards = []; path_attr_mismatch = []; retier_recos = []; phantom = []
    s_removals = []; s_adds = []                          # _short pairs for the conservative 88c batch check
    for r in atoms_spec:
        q = r["atom"]; sn = _short(q); at = attr.get(q, "MISSING"); pt = _path_tier(q)
        if at == "MISSING": phantom.append("%s atom-missing" % q); continue
        if pt != at: path_attr_mismatch.append((q, pt, at))
        src_id = id_of_qid.get(q, q)
        for rm in r.get("remove_backwards", []):
            tq = rm.get("tgt", ""); rt = (rm.get("rel", "") or "").upper()
            ta = attr.get(tq, "MISSING")
            exists = (src_id, id_of_qid.get(tq, tq), rt) in edgeset
            if not exists: phantom.append("%s -%s-> %s edge-missing" % (sn, rt, _short(tq)))
            if ta == "MISSING": phantom.append("%s target %s missing" % (sn, _short(tq))); continue
            backwards = TNUM.get(at, 9) < TNUM.get(ta, 9)        # authoritative: by tier FIELD
            rowd = {"src": sn, "src_qid": q, "src_attr": at, "src_path": pt, "rel": rt, "tgt": _short(tq),
                    "tgt_attr": ta, "exists": exists, "backwards": backwards}
            if exists and backwards: cleared.append(rowd)
            elif exists and not backwards: not_backwards.append(rowd)
            if exists and rt in FORWARD: s_removals.append((sn, _short(tq), rt))
        # tier-placement flags -> remove-vs-retier (by DEPENDS_ON in-degree of target)
        if sn in TIER_PLACEMENT_FLAGS:
            for rm in r.get("remove_backwards", []):
                tq = rm.get("tgt", ""); indeg = dep_indeg.get(id_of_qid.get(tq, tq), 0); ta = attr.get(tq, "?")
                reco = ("RETIER target (in-deg=%d -> foundational; lower its tier so the dependence is correct)" % indeg) if indeg >= 3 \
                    else ("REMOVE edge (in-deg=%d low -> genuine backwards)" % indeg)
                retier_recos.append((sn, _short(tq), ta, indeg, reco))
        # Tier B rescue add (forward only feeds the batch check)
        if r.get("leaf_risk") and sn in TIER_B_RESCUE:
            rtgt, rrel = TIER_B_RESCUE[sn]
            if rrel in FORWARD: s_adds.append((sn, rtgt, rrel))

    pc = precheck_batch(*load()[:2], s_removals, s_adds, tier_changes=[], corpus=load()[2])
    n_tierA = sum(1 for r in atoms_spec if not r.get("leaf_risk"))
    n_tierB = sum(1 for r in atoms_spec if r.get("leaf_risk"))
    n_total_removes = len(cleared) + len(not_backwards)
    hard_pass = (not not_backwards and not path_attr_mismatch and not phantom and not pc["stranded"] and not pc["monotone_violations"])

    print("  CELL-140b foundation-cleanup pre-check (qualified-id, attr-tier authoritative; VERIFICATION ONLY):", flush=True)
    print("  spec atoms=%d (TierA=%d TierB=%d) | remove-edges examined=%d" % (len(atoms_spec), n_tierA, n_tierB, n_total_removes), flush=True)
    print("  CLEARED (genuine backwards by tier-field)=%d | NOT-backwards (legit dep; DO NOT REMOVE)=%d | phantom=%d" % (
        len(cleared), len(not_backwards), len(phantom)), flush=True)
    print("  PATH/ATTR-TIER MISMATCH atoms=%d (spec trusted the id-path; tier-field disagrees):" % len(path_attr_mismatch), flush=True)
    for q, pt, at in path_attr_mismatch: print("    %-34s path=%s attr=%s" % (q, pt, at), flush=True)
    print("  NOT-backwards edges (would wrongly remove legit dependencies):", flush=True)
    for d in not_backwards: print("    %s(%s) -%s-> %s(%s)" % (d["src"], d["src_attr"], d["rel"], d["tgt"], d["tgt_attr"]), flush=True)
    print("  TIER-PLACEMENT flags (remove-vs-retier, by target in-degree):", flush=True)
    for sn, tgt, ta, indeg, reco in retier_recos: print("    %-26s -> %s (T%s) : %s" % (sn, tgt, TNUM.get(ta, "?"), reco), flush=True)
    print("  BATCH (88c, _short-conservative): stranded=%d %s | new-monotone=%d %s" % (
        len(pc["stranded"]), pc["stranded"][:6], len(pc["monotone_violations"]), pc["monotone_violations"][:6]), flush=True)
    print("  HARD-PASS=%s" % hard_pass, flush=True)
    return {"n_atoms": len(atoms_spec), "n_tierA": n_tierA, "n_tierB": n_tierB, "n_removes": n_total_removes,
            "cleared": len(cleared), "not_backwards": not_backwards, "path_attr_mismatch": path_attr_mismatch,
            "phantom": phantom, "retier_recos": retier_recos, "stranded": pc["stranded"],
            "new_monotone": pc["monotone_violations"], "hard_pass": hard_pass}


def verdict(r) -> Tuple[str, str]:
    if r.get("error"): return ("UNKNOWN", "UNKNOWN: " + r["error"])
    s = ("140b: %d atoms (TierA=%d TierB=%d); %d remove-edges -> %d CLEARED genuine-backwards, %d NOT-backwards (legit deps), %d path/attr-tier mismatches, %d phantom; batch stranded=%d new-monotone=%d." % (
        r["n_atoms"], r["n_tierA"], r["n_tierB"], r["n_removes"], r["cleared"], len(r["not_backwards"]),
        len(r["path_attr_mismatch"]), len(r["phantom"]), len(r["stranded"]), len(r["new_monotone"])))
    if r["stranded"]:
        return ("HARD_FAIL", "Removal strands consumer(s): %s -- breaks axiom-reach. " % r["stranded"][:6] + s)
    if r["hard_pass"]:
        return ("HARD_PASS", "Foundation-cleanup batch CLEARED for atomic ratify: every removal verified genuine-backwards by authoritative tier-field, 0 stranded, 0 new monotone, flags resolved. " + s)
    return ("PARTIAL", "Batch is stranding-safe + monotone-safe, BUT %d atoms have a path/attr-tier mismatch causing %d edges to be NOT genuinely backwards under the tier-field -- these would wrongly remove legitimate dependencies. RESOLVE before ratify: for each mismatch atom, EITHER fix the tier FIELD to T1 (if genuinely foundational -> then the edge IS backwards -> remove) OR DROP its removes (if genuinely derived -> the deps are legit). The OTHER %d removes are CLEARED. " % (
        len(r["path_attr_mismatch"]), len(r["not_backwards"]), r["cleared"]) + s)


if __name__ == "__main__":
    _selftest()
    print("[config] anchor=substrate_140b_foundation_cleanup_precheck", flush=True)
    out_dir = get_output_dir("substrate_140b_foundation_cleanup_precheck_cpu_v1"); t0 = time.time(); r = run()
    v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
    metrics = {"anchor_name": "substrate_140b_foundation_cleanup_precheck_cpu_v1", "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": "full", "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
    write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
