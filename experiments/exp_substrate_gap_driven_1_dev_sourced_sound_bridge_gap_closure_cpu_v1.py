"""FULL-AUTO / gap-driven loop cell 1 -- CELL-GAP-DRIVEN-1. First decisive cell of the gap-driven abductive promotion loop (the path that SIDESTEPS the R2 representational wall: certify by GAP-CLOSURE utility, not carrier-extension). Substrate-internal; NO LLM; 22nd-rule firewall (DEV q01-q60 only; held-out q54-q65/56d/56d-v2 NEVER opened). bge (remote GPU). ASCII; --self-test.

LOOP (this cell = source->abduct->soundness-gate->certify-by-closure):
  GAP SOURCE: DEV v3_60q M4d top-5 MISSES (gold not retrieved) = real capability failures (22nd-rule safe).
  ABDUCTION (reverse-math weakest bridge): for miss (query, missed gold G), among the retrieved anchors pick A = argmax bge-cos(A,G) -> the most-plausible single bridge A->G that consensus would use to pull G into top-5.
  SOUNDNESS GATE (Goodhart guard): promote A->G ONLY if bge-cos(A,G) >= TAU (real relation, not gerrymander) AND tier-compatible (no foundational->derived backwards). Distinguishes genuine utility from dev-overfitting.
  CERTIFY by GAP-CLOSURE: add sound bridges, re-run M4d on DEV, measure net F1 + #gaps-closed. Utility test -> no element-model needed (sidesteps R2).
HONEST SCOPE: DEV (in-distribution) gap-closure with SOUND fillers. NOT a held-out generalization claim (22nd-rule reserves held-out). Goodhart guards: soundness gate + NET F1 (not just closed-count) + this caveat.
HARD-PASS: >=1 dev gap closed by a SOUND bridge AND net dev-F1 delta >= 0 (sound fillers close gaps without diluting). HARD-FAIL: gaps close only via sub-TAU (unsound) bridges, OR sound bridges net-dilute (-> bge-representation-bound, consistent with prior M1c/M4 finding)."""
from __future__ import annotations
import sys, json, time
from pathlib import Path
from collections import defaultdict
from typing import Dict, Tuple
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
from experiments.exp_substrate_m4d_capability_graph_walk_heldout_cpu_v1 import _short, f1_present, bfs_proximity, WALK_EDGES, POOL_K, N_ANCHORS, MAX_HOP, DECAY
DATA_ROOT = REPO / "data" / "substrate_index"
DEV = DATA_ROOT / "benchmark_corpus_v3_60q.jsonl"          # q01-q60 DEV; NOT held-out (22nd-rule safe)
BETA = 0.10
TAU_SOUND = 0.50                                            # bge-cos soundness threshold for a promotable bridge
TIER_NUM = {"T1": 1, "T2": 2, "T3": 3, "T4": 4}
SELFTEST = "--self-test" in sys.argv


def _selftest():
    assert _short("a::b/c") == "c"; print("[selftest] PASS", flush=True)


if __name__ == "__main__" and SELFTEST:
    _selftest(); sys.exit(0)


def run() -> Dict:
    import numpy as np
    from backend.substrate_index.partition import PartitionedStore
    from backend.substrate_index.encode import AtomEncoder
    from backend.substrate_index.retrieve import Retriever
    from backend.substrate_index.retrieve_cache import rebuild_index_cached
    ps = PartitionedStore(DATA_ROOT)
    try: enc = AtomEncoder()
    except Exception as e: return {"error": "bge:" + str(e)[:80]}
    r = Retriever(ps, enc); rebuild_index_cached(r, DATA_ROOT)
    qual = {a.id: a.qualified_id for a in ps.all_atoms()}
    sset = {_short(a.id) for a in ps.all_atoms()}
    tier = {_short(a.id): str(getattr(getattr(a, "tier", None), "value", getattr(a, "tier", "")) or "") for a in ps.all_atoms()}
    short2q = {}
    for a in ps.all_atoms(): short2q.setdefault(_short(a.id), a.qualified_id)
    # atom embedding matrix (for bge-cos atom<->atom; sound-bridge abduction)
    M = getattr(r, "_semantic_matrix", None); idorder = getattr(r, "_id_order", None)
    if M is None or idorder is None: return {"error": "no _semantic_matrix/_id_order on retriever"}
    M = np.asarray(M, dtype=np.float32); M = M / (np.linalg.norm(M, axis=1, keepdims=True) + 1e-9)
    row = {}
    for i, aid in enumerate(idorder): row.setdefault(_short(aid), i)

    def bge_cos(a, b):
        ia, ib = row.get(a), row.get(b)
        if ia is None or ib is None: return 0.0
        return float(M[ia] @ M[ib])

    base = defaultdict(set)
    for rp in DATA_ROOT.rglob("relations.jsonl"):
        for ln in open(rp, encoding="utf-8"):
            ln = ln.strip()
            if not ln: continue
            try: rr = json.loads(ln)
            except Exception: continue
            if (rr.get("rel_type", "") or "").upper() in WALK_EDGES:
                s = rr.get("src_id", ""); t = rr.get("tgt_id", "")
                if s and t and s != t: base[s].add(t); base[t].add(s)

    def m4d_top5(question, adj):
        cands = r.semantic(question, top_k=POOL_K)
        pool = [(qual.get(c.atom_id, c.atom_id), float(getattr(c, "score", 0.0))) for c in cands]
        if not pool: return set(), pool
        cons = defaultdict(float)
        for a_qid, a_cos in pool[:N_ANCHORS]:
            for node, hop in bfs_proximity([a_qid], adj, MAX_HOP).items():
                if hop > 0: cons[node] += a_cos * (DECAY ** hop)
        top5 = {_short(qid) for qid, _ in sorted(((qid, cos + BETA * cons.get(qid, 0.0)) for qid, cos in pool), key=lambda t: -t[1])[:5]}
        return top5, pool

    devqs = [json.loads(l) for l in open(DEV, encoding="utf-8") if l.strip()]
    # ---- baseline + gap detection ----
    base_fs = []; misses = []
    for q in devqs:
        gold = {_short(g) for g in (q.get("ground_truth_atoms") or []) if _short(g) in sset}
        if not gold: continue
        top5, pool = m4d_top5(q["question"], base)
        base_fs.append(f1_present(top5, gold))
        for G in gold - top5:
            anchors = [_short(a_qid) for a_qid, _ in pool[:N_ANCHORS]]
            misses.append((G, anchors))
    base_f1 = round(sum(base_fs) / max(len(base_fs), 1), 4)

    # ---- ABDUCTION + SOUNDNESS GATE ----
    sound_bridges = []; unsound_only = 0
    seen = set()
    for G, anchors in misses:
        if G not in sset: continue
        best = None; best_cos = -1.0
        for A in anchors:
            if A == G or A not in sset: continue
            c = bge_cos(A, G)
            if c > best_cos: best_cos, best = c, A
        if best is None: continue
        # soundness gate: real relation (cos>=TAU) + tier-compatible (no foundational->derived backwards)
        ta, tg = TIER_NUM.get(tier.get(best, ""), 9), TIER_NUM.get(tier.get(G, ""), 9)
        tier_ok = ta >= tg                                  # anchor not strictly more-foundational than gold target
        if best_cos >= TAU_SOUND and tier_ok:
            key = (best, G)
            if key not in seen: seen.add(key); sound_bridges.append((short2q.get(best, best), short2q.get(G, G), round(best_cos, 3)))
        else:
            unsound_only += 1

    # ---- CERTIFY by GAP-CLOSURE: add sound bridges, re-run M4d on dev ----
    adj2 = defaultdict(set)
    for k, v in base.items(): adj2[k] = set(v)
    for sq, tq, _ in sound_bridges:
        if sq and tq and sq != tq: adj2[sq].add(tq); adj2[tq].add(sq)
    new_fs = []; closed = 0; gold_misses_after = 0
    for q in devqs:
        gold = {_short(g) for g in (q.get("ground_truth_atoms") or []) if _short(g) in sset}
        if not gold: continue
        top5, _ = m4d_top5(q["question"], adj2)
        new_fs.append(f1_present(top5, gold))
        gold_misses_after += len(gold - top5)
    new_f1 = round(sum(new_fs) / max(len(new_fs), 1), 4)
    base_misses = sum(len(g) for g in [ {_short(x) for x in (q.get('ground_truth_atoms') or []) if _short(x) in sset} - m4d_top5(q['question'], base)[0] for q in devqs ])
    closed = base_misses - gold_misses_after
    print("  CELL-GAP-DRIVEN-1 (dev-sourced sound-bridge gap-closure; 22nd-rule: DEV only):", flush=True)
    print("  dev queries=%d | baseline M4d F1=%.4f | total gold-misses(baseline)=%d" % (len(devqs), base_f1, base_misses), flush=True)
    print("  abduction: %d sound bridges (bge-cos>=%.2f + tier-ok) | %d misses had only UNSOUND bridges (excluded=Goodhart-guard)" % (len(sound_bridges), TAU_SOUND, unsound_only), flush=True)
    print("  CERTIFY: post-bridge M4d F1=%.4f (net delta %+.4f) | gold-misses after=%d | gaps CLOSED by sound bridges=%d" % (new_f1, new_f1 - base_f1, gold_misses_after, closed), flush=True)
    for sq, tq, c in sound_bridges[:8]:
        print("    sound bridge %-26s -> %-26s bge-cos=%.3f" % (_short(sq), _short(tq), c), flush=True)
    return {"dev_q": len(devqs), "base_f1": base_f1, "new_f1": new_f1, "net_delta": round(new_f1 - base_f1, 4),
            "base_misses": base_misses, "misses_after": gold_misses_after, "gaps_closed": closed,
            "sound_bridges": len(sound_bridges), "unsound_only_misses": unsound_only,
            "bridges_sample": [(_short(s), _short(t), c) for s, t, c in sound_bridges[:20]]}


def verdict(r) -> Tuple[str, str]:
    if r.get("error"): return ("UNKNOWN", "UNKNOWN: " + r["error"])
    closed = r["gaps_closed"]; delta = r["net_delta"]
    s = ("gap-driven-1: dev baseline F1=%.4f -> post-sound-bridge F1=%.4f (net %+.4f); %d sound bridges abducted (cos>=%.2f); gaps closed=%d; %d misses had only unsound bridges (Goodhart-excluded). [DEV-only; 22nd-rule firewall; in-distribution scope.]" % (
        r["base_f1"], r["new_f1"], r["net_delta"], r["sound_bridges"], TAU_SOUND, closed, r["unsound_only_misses"]))
    if closed >= 1 and delta >= -1e-9:
        return ("HARD_PASS", "GAP-CLOSURE utility certification WORKS: >=1 dev gap closed by a SOUND failure-sourced bridge with NO net F1 dilution -> the gap-driven loop certifies promotions by closure (sidesteps R2; no element-model). SCOPE: dev/in-distribution + sound-gated (Goodhart-guarded); held-out generalization is a separate firewalled step. " + s)
    if closed >= 1:
        return ("PARTIAL", "Sound bridges close gaps but NET-DILUTE F1 (closure local, dilution global) -> consistent with prior sparse-selectivity/dilution tension; gap-closure works per-gap but the consensus walk dilutes -> needs confidence-tiered application (Claim 12). " + s)
    return ("HARD_FAIL", "0 dev gaps closed by SOUND bridges (gaps only closeable by sub-TAU unsound bridges = Goodhart, excluded) -> dev gaps are bge-representation-bound; sound failure-sourced bridges do not close them. Consistent with M1c/M4 bge-representation-bound finding; gap-driven closure does not escape it at the retrieval layer. " + s)


if __name__ == "__main__":
    _selftest()
    print("[config] anchor=substrate_gap_driven_1_dev_sourced_sound_bridge_gap_closure | TAU=%.2f BETA=%.2f" % (TAU_SOUND, BETA), flush=True)
    out_dir = get_output_dir("substrate_gap_driven_1_dev_sourced_sound_bridge_gap_closure_cpu_v1"); t0 = time.time(); r = run()
    v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
    metrics = {"anchor_name": "substrate_gap_driven_1_dev_sourced_sound_bridge_gap_closure_cpu_v1", "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": "full", "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
    write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
