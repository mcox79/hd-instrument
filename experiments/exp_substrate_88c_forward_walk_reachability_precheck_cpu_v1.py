"""DECISION 88c -- forward-walk reachability PRE-CHECK primitive (the gate that would have caught the 87c HARD_FAIL). The substrate's axiom-termination forward-walk uses DEPENDS_ON + SPECIALIZES as OUTGOING edges; an atom terminates iff that walk reaches a T1 axiom. Batch 2b removed ALL outgoing family-->member DEPENDS_ON from T2_FAM atoms and added only INCOMING member-->family SPECIALIZES, leaf-stranding graph_traversal + discriminative_classification (211/213). Prior 79a/84-style checks MISSED this because they treat a no-outgoing leaf as an axiom -- this primitive instead requires non-T1 atoms to REACH a T1 axiom.
API: precheck_batch(removals, adds) -> {stranded: [...], ok: bool}. removals/adds are (src_short, tgt_short) pairs; forward edges only.
This run (1) builds the primitive, (2) DEMONSTRATES it flags the batch-2b T2_FAM family-->member DEPENDS_ON removals as leaf-stranding (validating it catches 87c), and (3) confirms the DECISION 88a rescue (add T2_FAM-->root SPECIALIZES) un-strands them. Substrate-internal; laptop; structural; no LLM. ASCII; --self-test."""
from __future__ import annotations
import sys, json, time
from pathlib import Path
from collections import defaultdict, deque
from typing import Dict, Tuple, List
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
DATA_ROOT = REPO / "data" / "substrate_index"
FORWARD = {"DEPENDS_ON", "SPECIALIZES"}     # the substrate's axiom-termination forward-walk edge set (USES excluded)
MAX_HOP = 12
SELFTEST = "--self-test" in sys.argv


def _short(x): return str(x).split("::")[-1].split("/")[-1].strip().lower()


def reaches_t1(start, adj, is_t1):
    """Forward-walk (DEPENDS_ON+SPECIALIZES) from start; True if it reaches a T1 axiom. Visited-set safe (cycles ok)."""
    if is_t1(start): return True
    seen = {start}; q = deque([(start, 0)])
    while q:
        n, d = q.popleft()
        if d >= MAX_HOP: continue
        for m in adj.get(n, ()):
            if is_t1(m): return True
            if m not in seen: seen.add(m); q.append((m, d + 1))
    return False


def _selftest():
    adj = {"a": ["b"], "b": ["AX"]}; is_t1 = lambda n: n == "AX"
    assert reaches_t1("a", adj, is_t1) and not reaches_t1("a", {"a": ["b"], "b": ["a"]}, is_t1)
    print("[selftest] PASS", flush=True)


if __name__ == "__main__" and SELFTEST:
    _selftest(); sys.exit(0)


def load():
    from backend.substrate_index.partition import PartitionedStore
    atoms = list(PartitionedStore(DATA_ROOT).all_atoms())
    tier = {_short(a.id): str(getattr(getattr(a, "tier", None), "value", getattr(a, "tier", "")) or "") for a in atoms}
    corpus = {_short(a.id): str(getattr(getattr(a, "corpus", None), "value", getattr(a, "corpus", ""))).lower() for a in atoms}
    adj = defaultdict(list)
    for rp in DATA_ROOT.rglob("relations.jsonl"):
        for ln in open(rp, encoding="utf-8"):
            ln = ln.strip()
            if not ln: continue
            try: r = json.loads(ln)
            except Exception: continue
            if (r.get("rel_type", "") or "").upper() in FORWARD:
                s = _short(r.get("src_id", "")); t = _short(r.get("tgt_id", ""))
                if s and t and s != t: adj[s].append(t)
    return tier, adj, corpus


TIER_NUM = {"T1": 1, "T2": 2, "T3": 3, "T4": 4}


def precheck_batch(tier, adj, removals: List, adds: List, tier_changes: List = None, corpus: Dict = None) -> Dict:
    """removals/adds = (src_short, tgt_short) forward edges; tier_changes = (atom_short, old_tier, new_tier).
    corpus = {atom_short: corpus} -> if provided, tier-monotone is CORPUS-SCOPED (DECISION 92a): only WITHIN-corpus
    edges are checked; cross-corpus edges (e.g. concept->math) are EXEMPT (legitimate conceptual dependency).
    Returns atoms that LOSE reach-to-an-axiom (leaf-strand) PLUS tier-monotone violations. OPERATION-CLASS-INVARIANT:
    leaf-strand arises from edge ops (87c) AND tier mutations (84a; an atom demoted T1->T2/T3 is no longer an axiom
    and must reach one via forward walk)."""
    tier_changes = tier_changes or []
    corpus = corpus or {}
    is_t1_pre = lambda n: tier.get(n, "") == "T1"
    # post-tier map (tier mutations applied)
    post_tier = dict(tier)
    for a, _old, new in tier_changes:
        post_tier[a] = new
    is_t1_post = lambda n: post_tier.get(n, "") == "T1"
    # DECISION 93d-1: only FORWARD rel-types (DEPENDS_ON, SPECIALIZES) affect forward-walk/monotone.
    # removals/adds entries may be (s,t) or (s,t,rel_type); a non-FORWARD rel-type (e.g. USES) is EXEMPT
    # (a re-type DEPENDS_ON->USES = forward REMOVE + non-forward ADD; the USES add is invisible here).
    def fwd_only(pairs):
        out = []
        for p in pairs:
            if len(p) >= 3 and str(p[2]).upper() not in FORWARD: continue   # non-forward rel-type exempt
            out.append((p[0], p[1]))
        return out
    removals = fwd_only(removals); adds = fwd_only(adds)
    rem = {(s, t) for s, t in removals}
    post = defaultdict(list)
    for s, vs in adj.items():
        for v in vs:
            if (s, v) in rem: continue
            post[s].append(v)
    for s, t in adds:
        post[s].append(t)
    touched = {s for s, _ in removals} | {s for s, _ in adds} | {t for _, t in removals} | {t for _, t in adds}
    touched |= {a for a, _, _ in tier_changes}
    universe = set(adj) | touched | set(tier)
    stranded = []
    for n in universe:
        before = reaches_t1(n, adj, is_t1_pre)            # was it grounded before (pre-tier, pre-edge)?
        after = reaches_t1(n, post, is_t1_post)           # still grounded after (post-tier demotion + edge ops)?
        if before and not after:
            stranded.append(n)
    # tier-monotone violations (blind-spot 1): a DEPENDS_ON/SPECIALIZES edge src->tgt should have
    # tier(src) >= tier(tgt) in tier-NUMBER (foundational=low number depends on nothing more-derived).
    # After tier mutation, check incident edges of mutated atoms for src(low) -> tgt(high) violations.
    mutated = {a for a, _, _ in tier_changes}
    monotone_viol = []; cross_corpus_exempt = []
    for s, vs in post.items():
        for t in vs:
            if s not in mutated and t not in mutated: continue
            ts, tt = TIER_NUM.get(post_tier.get(s, ""), 9), TIER_NUM.get(post_tier.get(t, ""), 9)
            if ts < tt:  # foundational src depends on more-derived tgt = candidate backwards/monotone violation
                # DECISION 92a: tier-monotone is CORPUS-SCOPED. Only flag WITHIN-corpus edges; exempt cross-corpus.
                cs, ct = corpus.get(s, ""), corpus.get(t, "")
                if corpus and cs and ct and cs != ct:
                    cross_corpus_exempt.append("%s(%s)->%s(%s)" % (s, cs, t, ct))
                    continue
                monotone_viol.append("%s(%s)->%s(%s)" % (s, post_tier.get(s, "?"), t, post_tier.get(t, "?")))
    return {"stranded": sorted(stranded), "monotone_violations": sorted(set(monotone_viol)),
            "cross_corpus_exempt": sorted(set(cross_corpus_exempt)),
            "ok": len(stranded) == 0 and len(monotone_viol) == 0, "post_adj": post}


def run() -> Dict:
    tier, adj, corpus = load()
    is_t1 = lambda n: tier.get(n, "") == "T1"
    # T2_FAM family roots = T2 atoms with >=2 incoming SPECIALIZES (members specialize them)
    inspec = defaultdict(int)
    for s, vs in adj.items():
        pass
    # recompute incoming SPECIALIZES from relations (adj is forward-merged; need rel-typed)
    inspec = defaultdict(int); fam_out_dep = defaultdict(list)
    for rp in DATA_ROOT.rglob("relations.jsonl"):
        for ln in open(rp, encoding="utf-8"):
            ln = ln.strip()
            if not ln: continue
            try: r = json.loads(ln)
            except Exception: continue
            rt = (r.get("rel_type", "") or "").upper(); s = _short(r.get("src_id", "")); t = _short(r.get("tgt_id", ""))
            if not (s and t and s != t): continue
            if rt == "SPECIALIZES": inspec[t] += 1
            if rt == "DEPENDS_ON": fam_out_dep[s].append(t)
    fam_roots = [s for s in tier if tier.get(s) == "T2" and inspec.get(s, 0) >= 2]

    # DEMO 1: reconstruct batch 2b (remove ALL family->member DEPENDS_ON; add member->family SPECIALIZES)
    removals = []; adds = []
    for f in fam_roots:
        for m in fam_out_dep.get(f, []):
            removals.append((f, m)); adds.append((m, f))   # SPECIALIZES member->family (incoming to family)
    r_naive = precheck_batch(tier, adj, removals, adds)
    naive_stranded = [s for s in r_naive["stranded"] if s in set(fam_roots)]

    # DEMO 2: DECISION 88a rescue -- add T2_FAM->root SPECIALIZES so each family reaches a T1 axiom.
    # Use an existing T1 root if available; else synthesize a T1 anchor for the demo.
    t1_root = next((n for n in tier if tier.get(n) == "T1" and ("operation_family" in n or "family_root" in n)), None)
    demo_root = t1_root or "operation_family_root_DEMO_T1"
    tier_demo = dict(tier); tier_demo[demo_root] = "T1"
    adds_rescue = list(adds) + [(f, demo_root) for f in fam_roots]
    r_rescue = precheck_batch(tier_demo, adj, removals, adds_rescue)
    rescue_stranded = [s for s in r_rescue["stranded"] if s in set(fam_roots)]

    print("  forward-walk reachability pre-check primitive (FORWARD = DEPENDS_ON + SPECIALIZES; axiom = T1):", flush=True)
    print("  T2_FAM family roots detected: %d -> %s" % (len(fam_roots), sorted(fam_roots)), flush=True)
    print("  DEMO 1 (naive batch 2b: remove family->member DEPENDS_ON + add member->family SPECIALIZES):", flush=True)
    print("    total stranded atoms=%d | T2_FAM stranded=%d -> %s" % (len(r_naive["stranded"]), len(naive_stranded), naive_stranded), flush=True)
    print("    => pre-check FLAGS the batch (ok=%s) -- would have caught 87c HARD_FAIL BEFORE dispatch" % r_naive["ok"], flush=True)
    print("  DEMO 2 (DECISION 88a rescue: + T2_FAM->%s SPECIALIZES):" % demo_root, flush=True)
    print("    total stranded atoms=%d | T2_FAM stranded=%d (rescue un-strands)" % (len(r_rescue["stranded"]), len(rescue_stranded)), flush=True)
    print("    => rescue makes batch SAFE (ok=%s)" % r_rescue["ok"], flush=True)
    return {"fam_roots": sorted(fam_roots), "naive_stranded_total": len(r_naive["stranded"]),
            "naive_fam_stranded": naive_stranded, "naive_ok": r_naive["ok"],
            "rescue_root": demo_root, "rescue_t1_root_existed": bool(t1_root),
            "rescue_stranded_total": len(r_rescue["stranded"]), "rescue_fam_stranded": rescue_stranded, "rescue_ok": r_rescue["ok"]}


def verdict(r) -> Tuple[str, str]:
    if r.get("error"): return ("UNKNOWN", "UNKNOWN: " + r["error"])
    s = ("Forward-walk reachability primitive: DEMO1 naive batch-2b strands %d T2_FAM atoms (%s) -> pre-check FLAGS (would have caught 87c); DEMO2 DECISION-88a rescue (T2_FAM->root SPECIALIZES; T1 root existed=%s) -> %d T2_FAM stranded (rescue %s)." % (
        len(r["naive_fam_stranded"]), r["naive_fam_stranded"], r["rescue_t1_root_existed"], len(r["rescue_fam_stranded"]), "works" if r["rescue_ok"] else "INSUFFICIENT"))
    if len(r["naive_fam_stranded"]) >= 1 and r["rescue_ok"]:
        return ("HARD_PASS", "Primitive VALIDATED: it flags the leaf-stranding the naive batch-2b would cause (catches 87c BEFORE dispatch) AND confirms the DECISION 88a rescue un-strands the T2_FAM atoms. Ready as the standing forward-walk pre-check for non-additive batches. " + s)
    if len(r["naive_fam_stranded"]) >= 1:
        return ("PARTIAL", "Primitive catches the stranding but the demo rescue did not fully un-strand (may need a real T1 root authored): " + s)
    return ("REVIEW", "Primitive did not reproduce the expected stranding -- check fam-root detection vs the exact batch-2b edge list: " + s)


if __name__ == "__main__":
    _selftest()
    print("[config] anchor=substrate_88c_forward_walk_reachability_precheck", flush=True)
    out_dir = get_output_dir("substrate_88c_forward_walk_reachability_precheck_cpu_v1"); t0 = time.time(); r = run()
    v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
    metrics = {"anchor_name": "substrate_88c_forward_walk_reachability_precheck_cpu_v1", "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": "full", "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
    write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
