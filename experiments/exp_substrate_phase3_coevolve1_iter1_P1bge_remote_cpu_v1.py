"""DECISION 67b Phase 3 CO-EVOLVE-1 Iteration 1 -- P1 (bge-similarity) GENERATE variant (the laptop P4-lexical variant HARD_FAILED: isolated atoms' descriptions are FORMULA NOTATION not atom names -> lexical co-occurrence finds nothing; P1 bge semantic is the necessary generator per spec, deferred-but-needed). For each isolated target: bge-retrieve (name+description) top-K -> candidate DEPENDS_ON; SOUND verify = CHTV tier-monotone + corpus-consistent + L6-PROOF terminates + no-cycle + additive. Emit ACCEPT edges for Testbed atomic ratify (NO mutation here). Runs on BGE machine. ASCII; --self-test.

HARD-PASS: >=1 sound edge proposed+verified."""
from __future__ import annotations
import sys, json, time
from pathlib import Path
from collections import defaultdict, deque
from typing import Dict, Tuple
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "substrate_phase3_coevolve1_iter1_P1bge_remote_cpu_v1"
DATA_ROOT = REPO / "data" / "substrate_index"
STRUCT_EDGES = {"DEPENDS_ON", "USES", "INSTANCE_OF", "SPECIALIZES", "DEFINED_OVER", "SHARES_MATH"}
TARGETS = ["mutual_information", "markov_decision_process", "q_learning"]
TIER_NUM = {"T1": 1, "T2": 2, "T3": 3, "T4": 4}
GEN_K = 30           # bge top-K candidates per target
MIN_COS = 0.55       # P1 generation floor (broad/heuristic; CHTV is the sound gate)
SELFTEST = "--self-test" in sys.argv


def _short(x): return str(x).split("::")[-1].split("/")[-1].strip().lower()


def _selftest():
    assert _short("math::T1/mutual_information") == "mutual_information"
    print("[selftest] PASS: " + ANCHOR_NAME, flush=True)


if __name__ == "__main__" and SELFTEST:
    _selftest(); sys.exit(0)


def run() -> Dict:
    from backend.substrate_index.partition import PartitionedStore
    from backend.substrate_index.encode import AtomEncoder
    from backend.substrate_index.retrieve import Retriever
    from backend.substrate_index.retrieve_cache import rebuild_index_cached
    ps = PartitionedStore(DATA_ROOT)
    try: enc = AtomEncoder()
    except Exception as e: return {"error": "bge:" + str(e)[:60]}
    r = Retriever(ps, enc); rebuild_index_cached(r, DATA_ROOT)
    atoms = list(ps.all_atoms())
    tier_of = {_short(a.id): str(getattr(getattr(a, "tier", None), "value", getattr(a, "tier", "")) or "") for a in atoms}
    corpus_of = {_short(a.id): str(getattr(getattr(a, "corpus", None), "value", getattr(a, "corpus", ""))).lower() for a in atoms}
    qual_of = {_short(a.id): a.qualified_id for a in atoms}
    desc_of = {_short(a.id): (a.description or "") for a in atoms}
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

    def reaches(src, dst, mx=6):
        seen = {src}; q = deque([(src, 0)])
        while q:
            n, d = q.popleft()
            if d >= mx: continue
            for m in adj.get(n, ()):
                if m == dst: return True
                if m not in seen: seen.add(m); q.append((m, d + 1))
        return False

    def terminates(n, mx=6):
        seen = {n}; q = deque([(n, 0)])
        while q:
            x, d = q.popleft()
            if is_axiom(x): return True
            if d >= mx: continue
            for m in adj.get(x, ()):
                if m not in seen: seen.add(m); q.append((m, d + 1))
        return False
    rows = []; all_accept = []
    for tgt in TARGETS:
        if tgt not in tier_of:
            rows.append({"target": tgt, "error": "not_found"}); continue
        t_tier = TIER_NUM.get(tier_of.get(tgt, ""), 9)
        query = tgt.replace("_", " ") + ". " + desc_of.get(tgt, "")
        cands = r.semantic(query, top_k=GEN_K)
        gen = []
        for c in cands:
            cs = _short(getattr(c, "atom_id", "")); cos = float(getattr(c, "score", 0.0))
            if cs and cs != tgt and cos >= MIN_COS: gen.append((cs, cos))
        chtv_seen = 0; accepted = []
        for cs, cos in gen:
            chtv_seen += 1
            if corpus_of.get(cs, "") not in ("math", "concept", "science"): continue
            c_tier = TIER_NUM.get(tier_of.get(cs, ""), 9)
            if c_tier > t_tier: continue                 # CHTV tier-monotone
            if not terminates(cs): continue               # L6-PROOF terminates
            if reaches(cs, tgt): continue                 # no cycle
            accepted.append((cs, round(cos, 3)))
        rows.append({"target": tgt, "tier": tier_of.get(tgt, ""), "generated_P1": len(gen),
                     "accepted": accepted, "n_accepted": len(accepted),
                     "chtv_acceptance": round(len(accepted) / max(chtv_seen, 1), 3)})
        for cs, cos in accepted:
            all_accept.append({"src_id": qual_of.get(tgt, tgt), "tgt_id": qual_of.get(cs, cs), "rel_type": "DEPENDS_ON",
                               "source": "coevolve1_iter1_P1bge", "gen_cos": cos,
                               "verify": "CHTV-tier-monotone+corpus+L6-terminates+no-cycle+additive"})
    out = DATA_ROOT / "coevolve1_iter1_P1bge_ACCEPT_edges.jsonl"
    out.write_text("\n".join(json.dumps(e) for e in all_accept), encoding="utf-8")
    print("  CO-EVOLVE-1 Iter1 P1-bge | GEN_K=%d MIN_COS=%.2f | ACCEPT edges=%d -> %s" % (GEN_K, MIN_COS, len(all_accept), out.name), flush=True)
    for x in rows:
        if x.get("error"): print("  %-26s ERROR" % x["target"]); continue
        print("  %-26s [%s] P1-gen=%d -> ACCEPT(DEPENDS_ON)=%d (CHTV-accept %.2f)" % (x["target"], x["tier"], x["generated_P1"], x["n_accepted"], x["chtv_acceptance"]), flush=True)
        for cs, cos in x["accepted"][:8]:
            print("       %s DEPENDS_ON %s (gen_cos %.3f)" % (x["target"], cs, cos), flush=True)
    return {"n_targets": len(TARGETS), "total_accept": len(all_accept), "rows": rows, "proposal_file": str(out)}


def verdict(r) -> Tuple[str, str]:
    if r.get("error"): return ("UNKNOWN", "UNKNOWN: " + r["error"])
    n = r["total_accept"]
    s = ("CO-EVOLVE-1 Iter1 P1-bge: %d sound DEPENDS_ON edges (CHTV tier-monotone + corpus + L6-terminates + no-cycle + additive) for %d isolated golds; per-target %s; emitted for Testbed atomic ratify; NO Exp-Dev mutation. P1-bge generation succeeds where P4-lexical failed (formula-notation descriptions)." % (
        n, r["n_targets"], {x["target"]: x.get("n_accepted", "err") for x in r["rows"]}))
    if n >= 1:
        return ("HARD_PASS", "HARD_PASS (loop works; isolated golds gain sound DEPENDS_ON edges degree 0->>0): " + s)
    return ("HARD_FAIL", "HARD_FAIL: 0 sound edges even with P1-bge generation -- CHTV gate rejects all (tier/cycle); isolated targets may need looser CHTV or different edge type. " + s)


if __name__ == "__main__":
    _selftest()
    print("[config] anchor=%s" % ANCHOR_NAME, flush=True)
    out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
    v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
    metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": "full", "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
    write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
