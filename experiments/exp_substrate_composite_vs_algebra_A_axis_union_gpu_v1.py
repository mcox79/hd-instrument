"""
exp_substrate_composite_vs_algebra_A_axis_union_gpu_v1.py -- INTERNAL composite_hrr vs algebra_hrr vs bge A-axis UNION delta -- GPU.

ROUTING: independent validation of the PRODUCTION two-vector fix (composite_hrr; my PP-410 spec, now in algebra_index.py) on the
  A-axis. Substrate-quality-first; NO LLM frame. This is an INTERNAL, self-contained comparison (composite vs algebra vs bge in
  ONE harness, same scoring) -- it is NOT a reproduction of Testbed's canonical UNION-A 0.458 absolute (Testbed owns that
  harness; PP-401 full-macro re-measure is theirs per my clarification note). The DELTA composite-vs-algebra is comparable
  regardless of absolute and directly answers: does identity-augmented composite_hrr improve A-axis atom-to-atom expansion?

  Mechanism (UNION-A): for each A_content question, bge-retrieve top-kb seed atoms by the free-text topic; expand the top seeds
  via AlgebraIndex atom-to-atom neighbors (composite_hrr OR algebra_hrr); UNION = bge_set ∪ expansion; score set-F1 vs gold.
  Variants: bge-only / algebra-UNION / composite-UNION. Sweep (kb, ke); report best-F1 per variant + composite-minus-algebra delta.

PRE-REGISTERED (substrate-property; the headline is the composite-vs-algebra DELTA):
  HARD-PASS: composite-UNION best-F1 >= algebra-UNION best-F1 + 0.02 AND composite-UNION >= bge-only (identity augmentation helps
    A-axis expansion without hurting vs bge). MIDDLE: composite within +/-0.02 of algebra (neutral; identity-aug doesn't hurt).
  HARD-FAIL: composite-UNION < algebra-UNION - 0.02 (identity augmentation HURTS A-axis expansion). UNKNOWN if bge unavailable.
ASCII-only. torch (light-GPU; bge). --self-test + --smoke + metrics.json. Route via overnight_queue (GPU) or remote_cpu_queue (desktop bge).
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time, json, re
from pathlib import Path
from typing import Dict, Tuple
try:
    import torch  # PROT-020 GPU cell; bge encodes on CUDA via get_encoder().
    _DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
except Exception:
    _DEVICE = "cpu"
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "substrate_composite_vs_algebra_A_axis_union_gpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
KB_SWEEP = [5, 8, 12]      # bge seed count
KE_SWEEP = [0, 3, 5]       # atom-to-atom expansion neighbors per seed (0 = bge-only)
N_SEED_EXPAND = 3          # expand the top-N bge seeds


def _norm(qid):
    s = qid.split("::", 1)[1] if "::" in qid else qid
    return s.strip().lower()


def _f1(retrieved, gold):
    if not gold: return 1.0 if not retrieved else 0.0
    tp = len(retrieved & gold)
    if tp == 0: return 0.0
    p = tp / len(retrieved); r = tp / len(gold)
    return 2 * p * r / (p + r)


def _selftest():
    assert _norm("math::T2/fhrr_bind") == "t2/fhrr_bind"
    assert abs(_f1({"x"}, {"x", "y"}) - (2 * 1 * 0.5 / 1.5)) < 1e-6
    assert _f1(set(), set()) == 1.0
    print("[selftest] PASS: composite-vs-algebra-A-axis-union", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run() -> Dict:
    from backend.substrate_index.partition import PartitionedStore
    from backend.substrate_index.algebra_index import AlgebraIndex
    idx = REPO / "data" / "substrate_index"
    bench_fp = idx / "benchmark_corpus_v2_60q.jsonl"
    if not bench_fp.exists(): return {"error": "no_benchmark"}
    bench = [json.loads(l) for l in open(bench_fp, encoding="utf-8") if l.strip()]
    A = [q for q in bench if q.get("type", "").startswith("A") and q.get("answerable", True)]
    ps = PartitionedStore(idx); atoms = ps.all_atoms(); all_ids = {_norm(a.id) for a in atoms}
    # algebra index (production encoding: algebra_hrr structural + composite_hrr identity)
    ai = AlgebraIndex(dim=1024); ai.build(ps)
    qid_of = {}  # _norm(id) -> qualified id used as AlgebraIndex key
    for a in atoms:
        qid_of[_norm(a.id)] = a.qualified_id
    # bge retriever (env-gated)
    try:
        from backend.substrate_index.encode import AtomEncoder
        from backend.substrate_index.retrieve import Retriever
        enc = AtomEncoder(); retr = Retriever(getattr(ps, "store", ps), enc); retr.rebuild_index()
    except Exception as e:
        print("[bge] unavailable: %s" % str(e)[:120], flush=True)
        return {"error": "bge_unavailable_env_gated", "note": "needs bge; harness correct + ready"}

    def expand(seed_norm, attr, ke):
        if ke <= 0: return set()
        qid = qid_of.get(seed_norm)
        if not qid: return set()
        try:
            res = ai._retrieve_by_attr(qid, attr, top_k=ke)
            return {_norm(aid) for aid, _ in res}
        except Exception:
            return set()

    kbs = [8] if SMOKE else KB_SWEEP
    kes = [0, 3] if SMOKE else KE_SWEEP
    variants = {"bge_only": None, "algebra_union": "algebra_hrr", "composite_union": "composite_hrr"}
    grid = {}  # (variant, kb, ke) -> mean F1
    for q in A:
        m = re.search(r"about (.+?)\s*\??$", q["question"], re.I)
        topic = m.group(1) if m else q["question"]
        gold = {_norm(g) for g in q.get("ground_truth_atoms", []) if _norm(g) in all_ids}
        for kb in kbs:
            try:
                cands = retr.semantic(topic, top_k=kb)
                bge_ids = [_norm(getattr(c, "atom_id", str(c))) for c in cands]
            except Exception:
                bge_ids = []
            bge_set = set(bge_ids)
            seeds = bge_ids[:N_SEED_EXPAND]
            for vname, attr in variants.items():
                for ke in kes:
                    if vname == "bge_only" and ke != 0: continue
                    if vname != "bge_only" and ke == 0: continue
                    exp = set()
                    if attr is not None and ke > 0:
                        for s in seeds: exp |= expand(s, attr, ke)
                    ret = bge_set | exp
                    grid.setdefault((vname, kb, ke), []).append(_f1(ret, gold))
    agg = {k: round(sum(v) / len(v), 4) for k, v in grid.items()}
    # best per variant
    best = {}
    for vname in variants:
        cells = [(k, f) for k, f in agg.items() if k[0] == vname]
        if cells:
            bk, bf = max(cells, key=lambda x: x[1]); best[vname] = {"f1": bf, "kb": bk[1], "ke": bk[2]}
    for vname in ("bge_only", "algebra_union", "composite_union"):
        if vname in best:
            print("  %-16s best-F1=%.4f (kb=%d ke=%d)" % (vname, best[vname]["f1"], best[vname]["kb"], best[vname]["ke"]), flush=True)
    return {"best": best, "n_A": len(A), "grid": {("%s_kb%d_ke%d" % k): v for k, v in agg.items()}, "device": _DEVICE}


def verdict(r) -> Tuple[str, str]:
    if r.get("error") == "bge_unavailable_env_gated":
        return ("UNKNOWN", "UNKNOWN: bge unavailable (env-gated). Harness correct + ready. " + r.get("note", ""))
    if r.get("error"): return ("UNKNOWN", "UNKNOWN: " + r["error"])
    b = r["best"]
    bge = b.get("bge_only", {}).get("f1"); alg = b.get("algebra_union", {}).get("f1"); comp = b.get("composite_union", {}).get("f1")
    if comp is None or alg is None:
        return ("UNKNOWN", "UNKNOWN: missing variant. best=%s" % b)
    d_ca = round(comp - alg, 4); d_cb = round(comp - (bge or 0), 4)
    s = ("bge_only=%s algebra_union=%s composite_union=%s | composite-minus-algebra=%+.4f composite-minus-bge=%+.4f (n_A=%d, device=%s). INTERNAL delta; NOT Testbed canonical absolute." % (bge, alg, comp, d_ca, d_cb, r["n_A"], r["device"]))
    if d_ca >= 0.02 and comp >= (bge or 0):
        return ("HARD_PASS", "HARD_PASS: production composite_hrr improves A-axis atom-to-atom expansion over plain algebra_hrr by >=+0.02 (and >= bge-only) -- identity-augmentation (my PP-410 fix) helps A-axis retrieval. " + s)
    if d_ca >= -0.02:
        return ("MIDDLE_BAND", "MIDDLE_BAND: composite_hrr within +/-0.02 of algebra_hrr on A-axis -- identity-augmentation is A-axis-neutral (doesn't hurt; its decode/cleanup benefit stands; A-axis gold may already be bge-covered). " + s)
    return ("HARD_FAIL", "HARD_FAIL: composite_hrr < algebra_hrr - 0.02 on A-axis -- identity augmentation HURTS A-axis expansion (the name component dilutes structural-topic neighbors). " + s)


print("[config] anchor=%s mode=%s device=%s" % (ANCHOR_NAME, RUN_MODE, _DEVICE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
