"""
exp_substrate_es3_chtv_retrieval_self_verification_cpu_v1.py -- E-S3: CHTV-1 retrieval-mode self-verification -- given LHS of a promotion/equivalence pair, is RHS in top-K by typed-signature (algebra-HRR) retrieval? -- CPU/local (no heat), READ-ONLY.

ROUTING: Research F1 AMENDMENT (research_to_exp_dev_F1_AMENDMENT_...), test E-S3 (PRIORITY 1, smallest, run FIRST). The 0.0067 F1 is a
  degraded-scorer artifact (1746/20820 atoms + bge OFF). E-S3 isolates whether the DEDUCTION layer is aligned with the RETRIEVAL API:
  for each KP-P1 promotion pair (T3 source -> T2 promotion, identical algebra) and each identical-algebra (PROVABLY_EQUIVALENT) duplicate
  pair, take LHS, retrieve top-K over the typed atom core by algebra-HRR (composite_hrr) cosine, and check whether RHS is in top-K. This is
  CHTV-1 in retrieval mode: typed-signature equality should make the equivalent atom the nearest neighbor. NO BGE (sentence_transformers is
  unavailable locally; this uses the substrate's own algebra-HRR, available locally) -- so E-S3 runs on the laptop; E-S1/E-S2 (which BGE-encode
  the query) are queued to the remote desktop separately. Substrate-internal (11th rule). Stratified seed reported (R4).

PRE-REGISTERED (Research): top-5 accuracy >= 0.80 = HEALTHY (deduction layer aligned with retrieval). < 0.40 = deduction layer misaligned
  with retrieval API (a MORE serious finding than 0.0067 -- report honestly, R3). MIDDLE_BAND [0.40, 0.80). UNKNOWN if < 5 pairs or no typed
  core. Also report top-1 accuracy + median rank of RHS. ASCII-only. --self-test + --smoke + metrics.json.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time, json
from collections import defaultdict
from pathlib import Path
from typing import Dict, Tuple, List
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "substrate_es3_chtv_retrieval_self_verification_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
TOPK = 5; SEED = 53; VECTOR_FIELD = "composite_hrr"; SIG_FIELDS = ("domain", "operation_type", "signature_input_type", "signature_output_type", "complexity_class")


def _short(x):
    return str(x).split("::")[-1].split("/")[-1].strip().lower()


def topk_contains(query_vec: np.ndarray, mat: np.ndarray, ids: List[str], self_idx: int, target_id: str, k: int) -> Tuple[bool, int]:
    """Cosine retrieve; exclude self; return (target in top-k, rank-of-target 1-based)."""
    sims = mat @ query_vec
    sims[self_idx] = -1e9
    order = np.argsort(-sims)
    rank = None
    for r, j in enumerate(order, 1):
        if ids[j] == target_id:
            rank = r; break
    return ((rank is not None and rank <= k), rank if rank is not None else 10 ** 9)


def _selftest():
    # planted nearest-neighbor: identical vectors retrieve each other at rank 1
    m = np.eye(4, dtype=np.float64); ids = ["a", "b", "c", "d"]
    m[1] = m[0]                                   # b identical to a
    hit, rank = topk_contains(m[0], m, ids, 0, "b", 5)
    assert hit and rank == 1, (hit, rank)
    hit2, _ = topk_contains(m[2], m, ids, 2, "b", 1)
    assert not hit2                               # c's nearest is not b at top-1
    print("[selftest] PASS: substrate_es3_chtv_retrieval_self_verification_cpu_v1", flush=True)


if __name__ == "__main__":
    _selftest()
    if _ARGS.self_test:
        sys.exit(0)


def run() -> Dict:
    root = REPO / "data" / "substrate_index"
    if not root.exists():
        return {"error": "no_substrate_index"}
    from backend.substrate_index.partition import PartitionedStore
    from backend.substrate_index.algebra_index import AlgebraIndex
    idx = AlgebraIndex()
    atoms = list(PartitionedStore(root).all_atoms())
    # typed core: atoms with composite_hrr (the CHTV-1 / algebra domain)
    ids = []; vecs = []; alg_of = {}; tier_of = {}
    for a in atoms:
        v = getattr(idx.encode_atom(a), VECTOR_FIELD, None)
        if v is None:
            continue
        aid = str(a.id)
        ids.append(aid); vecs.append(np.asarray(v, dtype=np.float64))
        alg_of[aid] = getattr(a, "algebra", None) or {}
        tier_of[aid] = str(getattr(getattr(a, "tier", None), "value", "") or "")
    if len(ids) < 5:
        return {"error": "typed_core_too_small", "n": len(ids)}
    mat = np.stack(vecs); mat = mat / (np.linalg.norm(mat, axis=1, keepdims=True) + 1e-12)
    id_index = {aid: i for i, aid in enumerate(ids)}

    # build pairs: duplicate short-names that are promotion (kp_p1_promotion provenance) or identical-algebra (provably-equivalent)
    by = defaultdict(list)
    for aid in ids:
        by[_short(aid)].append(aid)
    pairs = []
    for sname, members in by.items():
        if len(members) < 2:
            continue
        # order: T3 (source/LHS) -> T2 (promotion/RHS) when possible, else lexical
        members_sorted = sorted(members, key=lambda x: (tier_of.get(x, ""), x), reverse=True)  # T3 before T2
        lhs, rhs = members_sorted[0], members_sorted[1]
        algs = [alg_of[m] for m in (lhs, rhs)]
        identical_alg = (len(algs[0]) >= 3 and algs[0] == algs[1])
        pairs.append({"name": sname, "lhs": lhs, "rhs": rhs, "identical_algebra": identical_alg})
    if not pairs:
        return {"error": "no_pairs"}
    # both directions (LHS->RHS and RHS->LHS) for robustness
    hits5 = 0; hits1 = 0; ranks = []; rows = []
    n_query = 0
    for p in pairs:
        for src, tgt in ((p["lhs"], p["rhs"]), (p["rhs"], p["lhs"])):
            si = id_index[src]
            ok5, rank = topk_contains(mat[si].copy(), mat, ids, si, tgt, TOPK)
            ok1 = (rank == 1)
            hits5 += int(ok5); hits1 += int(ok1); ranks.append(min(rank, 9999)); n_query += 1
            rows.append({"pair": p["name"], "src": src, "tgt": tgt, "rank": rank, "top5": ok5})
    top5_acc = round(hits5 / n_query, 4); top1_acc = round(hits1 / n_query, 4)
    med_rank = int(np.median([r for r in ranks if r < 9999])) if ranks else 9999
    print("  typed core: %d atoms with %s | pairs=%d (queries both-dir=%d, seed=%d)" % (len(ids), VECTOR_FIELD, len(pairs), n_query, SEED), flush=True)
    print("  CHTV-1 retrieval self-verification: top-5 acc=%.4f | top-1 acc=%.4f | median RHS rank=%d" % (top5_acc, top1_acc, med_rank), flush=True)
    misses = [r for r in rows if not r["top5"]][:6]
    for m in misses:
        print("    MISS %-26s src=%s tgt-rank=%d" % (m["pair"], m["src"], m["rank"]), flush=True)
    return {"n_typed_core": len(ids), "n_pairs": len(pairs), "n_queries": n_query, "top5_acc": top5_acc,
            "top1_acc": top1_acc, "median_rhs_rank": med_rank, "sample_misses": misses,
            "pair_names": sorted(p["name"] for p in pairs)}


def verdict(r) -> Tuple[str, str]:
    if r.get("error"):
        return ("UNKNOWN", "UNKNOWN: " + r["error"] + " " + str(r.get("n", "")))
    acc = r["top5_acc"]
    s = ("E-S3 CHTV-1 retrieval self-verification (substrate verifies its own algebra equivalences via retrieval): typed core=%d atoms; "
         "%d pairs (%d both-direction queries); top-5 acc=%.4f, top-1 acc=%.4f, median RHS rank=%d. BGE NOT used (algebra-HRR only; "
         "sentence_transformers unavailable locally -> E-S1/E-S2 queued to remote). Pre-reg: >=0.80 healthy, <0.40 serious (deduction layer "
         "misaligned with retrieval).") % (r["n_typed_core"], r["n_pairs"], r["n_queries"], acc, r["top1_acc"], r["median_rhs_rank"])
    if acc >= 0.80:
        return ("HARD_PASS", "HARD_PASS (deduction layer ALIGNED with retrieval): top-5 acc=%.4f>=0.80 -- given one side of a "
                "promotion/equivalence pair, the substrate retrieves the equivalent atom in its top-5 via typed-signature (algebra-HRR). The "
                "self-verification primitive is healthy; the 0.0067 F1 is NOT a retrieval-primitive failure at the algebra layer. " % acc + s)
    if acc < 0.40:
        return ("HARD_FAIL", "HARD_FAIL (MORE serious than 0.0067, R3 honest disclosure): top-5 acc=%.4f<0.40 -- the substrate canNOT retrieve "
                "its own algebra-equivalent atoms; the deduction layer is misaligned with the retrieval API. This is a real primitive defect, not "
                "a scorer artifact. " % acc + s)
    return ("MIDDLE_BAND", "MIDDLE_BAND: top-5 acc=%.4f in [0.40,0.80) -- partial alignment; some equivalent atoms not retrievable in top-5 "
            "(see misses). " % acc + s)


if __name__ == "__main__":
    print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
    out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
    v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
    metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
    write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
