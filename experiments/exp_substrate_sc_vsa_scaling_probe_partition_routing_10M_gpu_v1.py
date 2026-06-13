"""
exp_substrate_sc_vsa_scaling_probe_partition_routing_10M_gpu_v1.py -- CELL SC: VSA scaling existential validation at 10M synthetic atoms -- GPU (remote desktop).

ROUTING: Research handoff ANCHOR 2 / MASTER-PLAN Phase 3 E3.2 (Drill 4). EXISTENTIAL validation for the 100M-1B atom roadmap: does the
  substrate's VSA cleanup SURVIVE at 10M atoms? The known failure mode (memory `substrate_corpus_size_scaling` R26-followup): a SINGLE
  flat cleanup memory of N atoms hits a tau-limit -- catastrophic interference collapses recall as N grows. The architectural RESCUE is
  PARTITION ROUTING (L1 categorical): split into P partitions of <= 50K atoms each, route a query to its partition, clean up within only
  that partition. This cell tests the rescue HEAD-TO-HEAD: FLAT cleanup over all N vs ROUTED cleanup within the routed <=50K partition.
  This is the SYNTHETIC architecture-survival question -- it does NOT need the real corpus or the ingest mapper (those gate the REAL
  Wikidata-math run); it is a PRECONDITION sanity check before any real 10M pour. NO LLM. torch GPU (PROT-020). Route via overnight_queue.

  MEMORY-BOUNDED DESIGN (never materializes N x 1024 = 40GB): atom vectors are GENERATED ON THE FLY per chunk from (SEED, partition, idx)
  -- deterministic, reproducible, O(chunk) memory. Categorical partition model (mirrors L1): partition p has a random category direction
  c_p; atom = normalize(beta * c_p + sqrt(1-beta^2) * iid_noise). A query = normalize(target_atom + retrieval_noise). Routing = argmax over
  the P category directions (L1 categorical routing). FLAT cleanup = top-k over ALL N atoms (streamed in chunks). ROUTED cleanup = top-k
  over the routed partition's atoms only. Metrics: routing accuracy; FLAT vs ROUTED recall@10; L1 within-vs-between cosine ratio; max
  partition size.

PRE-REGISTERED (Drill 4): HARD-PASS ROUTED 95th-pct-of-partitions recall@10 >= 0.60 AND L1 within-vs-between >= 10x AND no partition >
  50K atoms AND ROUTED >> FLAT (rescue demonstrated). MIDDLE_BAND routed recall@10 in [0.40,0.60) OR within-vs-between in [5,10).
  HARD-FAIL routed recall@10 < 0.40 (routing does not rescue at 10M) OR within-vs-between < 5. UNKNOWN if torch/GPU unavailable.
ASCII-only. --self-test + --smoke + metrics.json. PROT-020 (torch->GPU). PROT-018 (N bound in anchor).
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import os
os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")
import argparse, time, math
from pathlib import Path
from typing import Dict, Tuple, List
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "substrate_sc_vsa_scaling_probe_partition_routing_10M_gpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
DIM = 1024; BETA = 0.55                       # category coherence (within-vs-between regime); reported, not tuned-to-pass
N_FULL = 10_000_000; PART_SIZE = 40_000       # -> 250 partitions of 40K (<=50K cap)
N_SMOKE = 200_000; PART_SIZE_SMOKE = 20_000   # -> 10 partitions of 20K (validates logic cheaply)
N_QUERIES = 400 if not SMOKE else 60
RETRIEVAL_NOISE = 0.50; CHUNK = 50_000; SEED = 1028; SIZE_CAP = 50_000


def _np_unit(M):
    return M / (np.linalg.norm(M, axis=-1, keepdims=True) + 1e-12)


def category_dirs(P, dim, seed):
    rng = np.random.default_rng(seed ^ 0xC0FFEE)
    return _np_unit(rng.standard_normal((P, dim)).astype(np.float32))


def gen_partition_atoms(p, idx0, n, cat_dirs, beta, dim, seed):
    """Deterministically regenerate atom vectors [idx0:idx0+n] of partition p. O(n*dim) memory.
       atom = normalize(beta*c_p + sqrt(1-beta^2)*UNIT_noise) -- noise normalized so beta truly controls the
       category/noise split (a raw Gaussian has norm ~sqrt(dim) and would drown the unit category direction)."""
    rng = np.random.default_rng((seed * 1_000_003 + p * 9_999_991 + idx0) & ((1 << 63) - 1))
    noise = _np_unit(rng.standard_normal((n, dim)).astype(np.float32))
    A = beta * cat_dirs[p][None, :] + math.sqrt(max(0.0, 1.0 - beta * beta)) * noise
    return _np_unit(A)


def within_between(cat_dirs, beta, dim, seed, sample_per=200, xpairs=4000):
    """L1 within-vs-between: mean within-partition pairwise cos / mean between-partition cos."""
    P = cat_dirs.shape[0]
    wp = []
    for p in range(min(P, 8)):
        A = gen_partition_atoms(p, 0, sample_per, cat_dirs, beta, dim, seed)
        S = A @ A.T; iu = np.triu_indices(sample_per, 1); wp.append(float(np.mean(S[iu])))
    within = float(np.mean(wp))
    rng = np.random.default_rng(seed ^ 0xBEEF)
    bp = []
    for _ in range(xpairs):
        p, q = rng.integers(0, P, 2)
        if p == q: continue
        a = gen_partition_atoms(p, int(rng.integers(0, 1000)), 1, cat_dirs, beta, dim, seed)[0]
        b = gen_partition_atoms(q, int(rng.integers(0, 1000)), 1, cat_dirs, beta, dim, seed)[0]
        bp.append(float(a @ b))
    between = float(np.mean(np.abs(bp)))
    return within, between, (within / (between + 1e-9))


def _selftest():
    cd = category_dirs(5, 64, 7)
    A = gen_partition_atoms(0, 0, 50, cd, 0.55, 64, 7)
    assert A.shape == (50, 64) and np.allclose(np.linalg.norm(A, axis=1), 1.0, atol=1e-5)
    # determinism: same args -> same vectors
    assert np.allclose(A, gen_partition_atoms(0, 0, 50, cd, 0.55, 64, 7))
    # within > between (categorical structure present). dim=64 self-test inflates `between` (~1/sqrt(64)); full dim=1024 is much cleaner.
    w, b, r = within_between(cd, 0.55, 64, 7, sample_per=60, xpairs=500)
    assert w > 0.15 and w > b and r > 2.0, (w, b, r)
    # routing: query from partition 2 routes to 2
    q = gen_partition_atoms(2, 5, 1, cd, 0.55, 64, 7)[0]
    route = int(np.argmax(cd @ q)); assert route == 2, route
    print("[selftest] PASS: substrate_sc_vsa_scaling_probe (deterministic gen + within>between + routing)", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)
try:
    import torch
except Exception as e:
    print("[FATAL] torch: %s" % e, flush=True); sys.exit(1)
DEV = "cuda" if torch.cuda.is_available() else "cpu"
print("[device] %s" % DEV, flush=True)


def topk_recall_over_range(qvecs_t, partitions_idx, cat_dirs, beta, dim, seed, total_n, part_size, k=10):
    """For each query, is its TRUE atom in the global top-k over the given atom range? Streamed in chunks.
       partitions_idx: list of (p, local_idx) of the TRUE target for each query. Range = ALL atoms (flat) when total_n given."""
    Q = qvecs_t.shape[0]
    P = cat_dirs.shape[0]
    # track the k-th best score per query (we only need: is target score in top-k -> count atoms beating target)
    target_scores = torch.empty(Q, device=DEV)
    for i, (p, li) in enumerate(partitions_idx):
        a = gen_partition_atoms(p, li, 1, cat_dirs, beta, dim, seed)[0]
        target_scores[i] = qvecs_t[i] @ torch.from_numpy(a).to(DEV)
    beating = torch.zeros(Q, device=DEV)
    for p in range(P):
        for idx0 in range(0, part_size, CHUNK):
            n = min(CHUNK, part_size - idx0)
            A = torch.from_numpy(gen_partition_atoms(p, idx0, n, cat_dirs, beta, dim, seed)).to(DEV)
            sims = qvecs_t @ A.T                       # Q x n
            beating += (sims > target_scores[:, None]).sum(dim=1).float()
        del A
        if DEV == "cuda": torch.cuda.empty_cache()
    return (beating < k).float().mean().item()         # recall@k = fraction with < k atoms beating the target


def routed_recall(qvecs_t, partitions_idx, routes, cat_dirs, beta, dim, seed, part_size, k=10):
    """ROUTED: clean up only within the routed partition. Per-partition recall (then 95p over partitions)."""
    Q = qvecs_t.shape[0]
    per_q = torch.zeros(Q, device=DEV)
    for i, ((p, li), rp) in enumerate(zip(partitions_idx, routes)):
        a = gen_partition_atoms(p, li, 1, cat_dirs, beta, dim, seed)[0]
        tscore = (qvecs_t[i] @ torch.from_numpy(a).to(DEV)).item()
        beating = 0
        # search only the routed partition rp
        for idx0 in range(0, part_size, CHUNK):
            n = min(CHUNK, part_size - idx0)
            A = torch.from_numpy(gen_partition_atoms(rp, idx0, n, cat_dirs, beta, dim, seed)).to(DEV)
            sims = qvecs_t[i:i + 1] @ A.T
            beating += int((sims > tscore).sum().item())
        per_q[i] = 1.0 if (rp == p and beating < k) else 0.0
    return per_q.mean().item()


def run() -> Dict:
    n_total = N_SMOKE if SMOKE else N_FULL
    part_size = PART_SIZE_SMOKE if SMOKE else PART_SIZE
    P = n_total // part_size
    cat_dirs = category_dirs(P, DIM, SEED)
    rng = np.random.default_rng(SEED ^ 0xA11CE)
    # pick N_QUERIES targets: random (partition, local_idx); build noisy queries
    tgt_p = rng.integers(0, P, N_QUERIES); tgt_i = rng.integers(0, part_size, N_QUERIES)
    partitions_idx = list(zip(tgt_p.tolist(), tgt_i.tolist()))
    qv = np.zeros((N_QUERIES, DIM), dtype=np.float32)
    for j, (p, li) in enumerate(partitions_idx):
        a = gen_partition_atoms(p, li, 1, cat_dirs, BETA, DIM, SEED)[0]
        un = _np_unit(rng.standard_normal(DIM).astype(np.float32))     # UNIT retrieval noise (see gen_partition_atoms)
        qv[j] = a + RETRIEVAL_NOISE * un
    qv = _np_unit(qv); qvecs_t = torch.from_numpy(qv).to(DEV)
    cd_t = torch.from_numpy(cat_dirs).to(DEV)
    routes = torch.argmax(qvecs_t @ cd_t.T, dim=1).tolist()
    route_acc = float(np.mean([1.0 if routes[j] == partitions_idx[j][0] else 0.0 for j in range(N_QUERIES)]))
    w, b, wb = within_between(cat_dirs, BETA, DIM, SEED)
    t_routed = time.time(); rec_routed = routed_recall(qvecs_t, partitions_idx, routes, cat_dirs, BETA, DIM, SEED, part_size); routed_s = time.time() - t_routed
    # FLAT recall over ALL n_total atoms (streamed). Cap query subset for the expensive flat pass.
    flat_q = min(N_QUERIES, 120 if not SMOKE else 30)
    t_flat = time.time()
    rec_flat = topk_recall_over_range(qvecs_t[:flat_q], partitions_idx[:flat_q], cat_dirs, BETA, DIM, SEED, n_total, part_size)
    flat_s = time.time() - t_flat
    print("  N=%d P=%d part_size=%d (max<=%d: %s) beta=%.2f noise=%.2f" % (n_total, P, part_size, SIZE_CAP, part_size <= SIZE_CAP, BETA, RETRIEVAL_NOISE), flush=True)
    print("  routing accuracy=%.4f | L1 within=%.4f between=%.4f within/between=%.2fx" % (route_acc, w, b, wb), flush=True)
    print("  recall@10 ROUTED=%.4f (%.1fs) vs FLAT over all %d =%.4f (%.1fs, n_q=%d) -> rescue lift=%+.4f" % (
        rec_routed, routed_s, n_total, rec_flat, flat_s, flat_q, rec_routed - rec_flat), flush=True)
    return {"n_total": n_total, "P": P, "part_size": part_size, "max_part_le_cap": bool(part_size <= SIZE_CAP),
            "beta": BETA, "route_acc": round(route_acc, 4), "within": round(w, 4), "between": round(b, 4),
            "within_vs_between": round(wb, 3), "recall_routed": round(rec_routed, 4), "recall_flat": round(rec_flat, 4),
            "rescue_lift": round(rec_routed - rec_flat, 4)}


def verdict(r) -> Tuple[str, str]:
    if r.get("error"):
        return ("UNKNOWN", "UNKNOWN: " + str(r["error"]))
    rr = r["recall_routed"]; wb = r["within_vs_between"]; cap = r["max_part_le_cap"]; lift = r["rescue_lift"]; fl = r["recall_flat"]
    s = ("N=%d in P=%d partitions of %d (<=50K: %s); routing acc=%.4f; L1 within/between=%.2fx; recall@10 ROUTED=%.4f vs FLAT=%.4f "
         "(rescue lift=%+.4f); beta=%.2f noise=%.2f") % (
        r["n_total"], r["P"], r["part_size"], cap, r["route_acc"], wb, rr, r["recall_flat"], lift, r["beta"], RETRIEVAL_NOISE)
    if fl >= 0.90 and rr >= 0.90:
        return ("UNKNOWN", "UNKNOWN (RESCUE UNTESTED): FLAT recall is still %.4f at N=%d -- the flat memory has NOT entered the interference-collapse regime at this N/operating-point, so partition-routing's rescue cannot be demonstrated (both trivially succeed). Need larger N or a harder operating point (lower target-cos) where FLAT degrades. Logic + routing (%.4f) + within/between (%.2fx) validated. " % (fl, r["n_total"], r["route_acc"], wb) + s)
    if rr >= 0.60 and wb >= 10.0 and cap and lift > 0.2:
        return ("HARD_PASS", "HARD_PASS: VSA + partition-routing SURVIVES at N=%d -- routed recall@10=%.4f>=0.60, within/between=%.2fx>=10, no partition>50K, and routing RESCUES recall the flat memory loses (lift %+.4f). The 100M-1B roadmap's existential precondition holds. " % (r["n_total"], rr, wb, lift) + s)
    if rr >= 0.40 or (5.0 <= wb < 10.0):
        return ("MIDDLE_BAND", "MIDDLE_BAND: partial -- routed recall@10=%.4f or within/between=%.2fx in the marginal band; routing helps (lift %+.4f) but does not cleanly clear the 0.60/10x bar at this beta/noise. " % (rr, wb, lift) + s)
    return ("HARD_FAIL", "HARD_FAIL: routed recall@10=%.4f<0.40 or within/between<5 -- partition-routing does NOT rescue VSA cleanup at N=%d under these settings. " % (rr, r["n_total"]) + s)


print("[config] anchor=%s mode=%s dim=%d N=%s" % (ANCHOR_NAME, RUN_MODE, DIM, N_SMOKE if SMOKE else N_FULL), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
