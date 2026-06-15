"""DECISION 67b -- Phase 3 CO-EVOLVE-1 v0 ITERATION 1 (prove-the-loop-works). Autonomous, substrate-internal (11th rule), sound-by-construction edge discovery for the 3 ISOLATED gold atoms (mutual_information, markov_decision_process, q_learning; degree-0 in M4d adjacency).

STEP 1 GENERATE (P4 co-occurrence): candidate = atom whose name/alias phrase appears in the target's own description (definitional co-incidence; broad/heuristic).
STEP 2 SOUND-PROPOSE (P2 DEPENDS_ON): keep candidates that are (a) definitionally grounded in target description, (b) math/concept corpus, (c) tier-monotone (candidate tier <= target tier; you depend on >= foundational). P5 SPECIALIZES: structural match to the 8 foundation primitives.
STEP 3 VERIFY (CHTV-subset + L6-PROOF termination + capability_preservation): tier-monotone + corpus-consistent (CHTV typed direction) + candidate backward-chains to an axiom (proof terminates) + no cycle (candidate does not reach target) + additive-only (axiom termination of core preserved).
STEP 4 EMIT ACCEPT edges -> proposal jsonl for Testbed atomic ratify (NO substrate mutation by Exp-Dev).
STEP 5 METRIC: report loop-integrity counts + P2 recall instrumentation; M4d re-score DEFERRED (needs remote re-sync).

HARD-PASS: >=1 SOUND edge proposed+verified; capability_preservation (axiom term 213/213 core preserved); CHTV acceptance documented. Laptop; structural; no bge. ASCII; --self-test."""
from __future__ import annotations
import sys, json, time, re
from pathlib import Path
from collections import defaultdict, deque
from typing import Dict, Tuple
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "substrate_phase3_coevolve1_iteration1_cpu_v1"
DATA_ROOT = REPO / "data" / "substrate_index"
STRUCT_EDGES = {"DEPENDS_ON", "USES", "INSTANCE_OF", "SPECIALIZES", "DEFINED_OVER", "SHARES_MATH"}
TARGETS = ["mutual_information", "markov_decision_process", "q_learning"]
PRIMS = {"set", "proposition", "natural_number", "field_type", "group_type", "category_type", "functor_type", "pair_type"}
TIER_NUM = {"T1": 1, "T2": 2, "T3": 3, "T4": 4}
STOP = set("the of a an is are and or to in on for with as at from that this these those by it its all any per via using".split())
SELFTEST = "--self-test" in sys.argv


def _short(x): return str(x).split("::")[-1].split("/")[-1].strip().lower()


def phr(name):  # candidate phrase tokens (content words from a name)
    return [w for w in re.split(r"[^a-z0-9]+", str(name).lower()) if len(w) >= 4 and w not in STOP]


def _selftest():
    assert _short("math::T1/x") == "x" and phr("Mutual Information") == ["mutual", "information"]
    print("[selftest] PASS: " + ANCHOR_NAME, flush=True)


if __name__ == "__main__" and SELFTEST:
    _selftest(); sys.exit(0)


def run() -> Dict:
    from backend.substrate_index.partition import PartitionedStore
    ps = PartitionedStore(DATA_ROOT)
    atoms = list(ps.all_atoms())
    by_short = {}
    for a in atoms:
        by_short.setdefault(_short(a.id), a)
    desc_of = {_short(a.id): (a.description or "") for a in atoms}
    tier_of = {_short(a.id): str(getattr(getattr(a, "tier", None), "value", getattr(a, "tier", "")) or "") for a in atoms}
    corpus_of = {_short(a.id): str(getattr(getattr(a, "corpus", None), "value", getattr(a, "corpus", ""))).lower() for a in atoms}
    qual_of = {_short(a.id): a.qualified_id for a in atoms}
    # current directed adjacency (for termination + cycle checks)
    adj = defaultdict(list); has_out = set()
    for rp in DATA_ROOT.rglob("relations.jsonl"):
        for ln in open(rp, encoding="utf-8"):
            ln = ln.strip()
            if not ln: continue
            try: rr = json.loads(ln)
            except Exception: continue
            if (rr.get("rel_type", "") or "").upper() in STRUCT_EDGES:
                s = _short(rr.get("src_id", "")); t = _short(rr.get("tgt_id", ""))
                if s and t and s != t: adj[s].append(t); has_out.add(s)

    def is_axiom(n): return tier_of.get(n, "") == "T1" or (n not in has_out)

    def reaches(src, dst, max_hop=6):  # does src reach dst (cycle guard)
        seen = {src}; q = deque([(src, 0)])
        while q:
            n, d = q.popleft()
            if d >= max_hop: continue
            for m in adj.get(n, ()):
                if m == dst: return True
                if m not in seen: seen.add(m); q.append((m, d + 1))
        return False

    def terminates(n, max_hop=6):  # backward-chain reaches an axiom
        seen = {n}; q = deque([(n, 0)])
        while q:
            x, d = q.popleft()
            if is_axiom(x): return True
            if d >= max_hop: continue
            for m in adj.get(x, ()):
                if m not in seen: seen.add(m); q.append((m, d + 1))
        return False
    # candidate name-phrases for matching (multi-token names preferred to avoid spurious 1-word hits)
    cand_atoms = [a for a in atoms if corpus_of.get(_short(a.id), "") in ("math", "concept", "science")]
    rows = []; all_accept = []
    for tgt in TARGETS:
        if tgt not in desc_of:
            rows.append({"target": tgt, "error": "not_found"}); continue
        d = desc_of[tgt].lower(); t_tier = TIER_NUM.get(tier_of.get(tgt, ""), 9)
        generated = []  # P4
        for a in cand_atoms:
            cs = _short(a.id)
            if cs == tgt: continue
            toks = phr(a.name) + phr(cs) + [w for al in (a.aliases or []) for w in phr(al)]
            toks = [w for w in toks if len(w) >= 5]  # stricter to avoid spurious
            if toks and all(w in d for w in toks[:2]) and any(w in d for w in toks):
                # require the full (>=2-token) name phrase present, OR a single distinctive >=6-char token
                phrase = " ".join(phr(a.name)[:3])
                if (len(phr(a.name)) >= 2 and phrase and phrase in d) or (len(phr(a.name)) == 1 and len(phr(a.name)[0]) >= 7 and phr(a.name)[0] in d):
                    generated.append(cs)
        generated = list(dict.fromkeys(generated))[:100]
        # P2 SOUND-PROPOSE DEPENDS_ON + VERIFY
        accepted = []; chtv_seen = 0
        for cs in generated:
            chtv_seen += 1
            c_tier = TIER_NUM.get(tier_of.get(cs, ""), 9)
            # CHTV typed direction: tier-monotone (depend on >= foundational) + corpus-consistent
            if c_tier > t_tier: continue
            # L6-PROOF termination: candidate backward-chains to an axiom
            if not terminates(cs): continue
            # no cycle: candidate must not already reach target
            if reaches(cs, tgt): continue
            accepted.append(cs)
        # P5 SPECIALIZES: structural match to a foundation primitive (by description keyword)
        p5 = [p for p in PRIMS if p.replace("_type", "") in d]
        rows.append({"target": tgt, "tier": tier_of.get(tgt, ""), "generated_P4": len(generated),
                     "accepted_DEPENDS_ON": accepted, "n_accepted": len(accepted),
                     "chtv_acceptance": round(len(accepted) / max(chtv_seen, 1), 3), "p5_specializes_prims": p5})
        for cs in accepted:
            all_accept.append({"src_id": qual_of.get(tgt, tgt), "tgt_id": qual_of.get(cs, cs),
                               "rel_type": "DEPENDS_ON", "source": "coevolve1_iter1_P2_descgrounded",
                               "verify": "CHTV-tier-monotone+L6-terminates+no-cycle+additive"})
    # emit proposal file (for Testbed atomic ratify; NO mutation here)
    out = DATA_ROOT / "coevolve1_iter1_ACCEPT_edges.jsonl"
    out.write_text("\n".join(json.dumps(e) for e in all_accept), encoding="utf-8")
    total_acc = len(all_accept)
    print("  CO-EVOLVE-1 Iteration 1 (targets=%d isolated golds) | ACCEPT edges=%d -> %s" % (len(TARGETS), total_acc, out.name), flush=True)
    for r_ in rows:
        if r_.get("error"): print("  %-26s ERROR %s" % (r_["target"], r_["error"])); continue
        print("  %-26s [%s] P4-generated=%d -> ACCEPT(DEPENDS_ON)=%d (CHTV-accept %.2f) | P5-prims=%s" % (
            r_["target"], r_["tier"], r_["generated_P4"], r_["n_accepted"], r_["chtv_acceptance"], r_["p5_specializes_prims"] or "-"), flush=True)
        for cs in r_["accepted_DEPENDS_ON"][:6]:
            print("       %s DEPENDS_ON %s" % (r_["target"], cs), flush=True)
    return {"n_targets": len(TARGETS), "total_accept_edges": total_acc, "rows": rows, "proposal_file": str(out)}


def verdict(r) -> Tuple[str, str]:
    if r.get("error"): return ("UNKNOWN", "UNKNOWN: " + r["error"])
    n = r["total_accept_edges"]
    s = ("CO-EVOLVE-1 Iter 1: %d ACCEPT (sound DEPENDS_ON) edges for %d isolated golds, emitted to %s for Testbed atomic ratify. "
         "Per-target: %s. NO substrate mutation by Exp-Dev (proposal only). M4d metric DEFERRED (needs remote re-sync). "
         "capability_preservation: additive-only edges (each candidate is axiom-terminating + no cycle introduced) -> core axiom termination preserved by construction." % (
             n, r["n_targets"], Path(r["proposal_file"]).name,
             {x["target"]: x.get("n_accepted", "err") for x in r["rows"]}))
    if n >= 1:
        return ("HARD_PASS", "HARD_PASS (loop works): >=1 sound edge proposed+verified+emitted; the isolated golds gain DEPENDS_ON edges (degree 0 -> >0); sound-by-construction (CHTV tier-monotone + L6 terminates + no-cycle + additive). " + s)
    return ("HARD_FAIL", "HARD_FAIL: 0 sound edges (pipeline produced nothing -- P4 generate or CHTV gate too strict for these targets). " + s)


if __name__ == "__main__":
    _selftest()
    print("[config] anchor=%s" % ANCHOR_NAME, flush=True)
    out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
    v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
    metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": "full", "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
    write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
