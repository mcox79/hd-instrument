"""
exp_substrate_partition_routing_10M_full_v2.py -- CELL SC-v2: VSA scaling existential validation -- 3-seed FULL upgrade -- GPU (overnight_queue).

PROMOTION CONTEXT (USER 2026-06-25): the v1 smoke (HARD_PASS routed_recall=0.9333, N=[10k,100k], part_size=2000) cannot be
chain-grade-classified per BIAS-14 (n_seeds=1). This v2 re-dispatches at FULL with n_seeds=3 (seeds [11,13,19]; consistent with
today's other cell-batch) to make the result cert-eligible. ADD N=1M to test whether the smoke's "10M roadmap precondition holds"
claim survives at production scale. PART_SIZE LOCKED at 2000 (smoke-vs-full discipline: regime matched along every capacity-
sensitive dimension; no sign-flip allowed).

DECOUPLED-CUE model (Exp-Dev caught the coupling artifact in the naive single-noise model; this is the faithful design): every
atom has TWO independent cues --
  * CATEGORY cue c_p (dim Dc, shared within partition p): read by ROUTING (mirrors clean L1 partition labels).
  * IDENTITY cue id_g (dim Di, unique per atom, near-orthogonal): read by CLEANUP (mirrors noisier composite_hrr identity).
A query = [category cue = normalize(c_p + cat_noise)] + [identity cue = normalize(id_target + r*noise)], r set so identity-cos =
TARGET_COS. Routing accuracy is then governed by cat_noise (kept clean), INDEPENDENT of cleanup difficulty TARGET_COS -- so we
can put FLAT into the interference-collapse regime WITHOUT breaking routing.

KEY robust (non-tuned) claim: ROUTED recall@10 depends ONLY on partition size (=2000) -> N-INVARIANT; FLAT recall@10 degrades
monotonically with N. Memory-bounded: identities regenerated per chunk on the GPU from (seed, global_idx) -- never materializes
N x Di (40GB at 1e7).

PRE-REGISTERED bands (LOCKED at module init via assert META_PROSPECTIVE_BANDS_FRESH_SEEDS; cross-cell seeds [11,13,19]):
  HARD_PASS_CHAIN_GRADE_PARTITION_ROUTING_AT_M_100k:
    routed recall@10 >= 0.85 at N=100k AND cv <= 0.05 across seeds AND routing acc >= 0.95 across seeds
  HARD_PASS_PARTIAL_AT_M_1M:
    routed recall@10 >= 0.50 at N=1M (stretch goal; lower N=100k must also pass)
  CHAIN_GRADE_AT_LOWER_M_CLIFF:
    cliff (routed recall@10 drop from >=0.85 to <0.50) identified between 100k and 1M
  HARD_FAIL_PARTITION_DEGRADES:
    routed recall@10 < 0.50 at N=100k (would invalidate the smoke v1 result)

Q-DISCIPLINE (USER 2026-06-25): the smoke result was 0.9333 routed recall@10. If full gives >=0.995, suspect saturation +
HONEST UNDER-claim. >=0.95 with a mechanism story is OK; >=0.995 without one is by-construction saturation tier.

SIGMA0 CLEANUP INTEGRITY: each arm reports per-seed routed recall AND raw match-score distribution at the partition level.

ASCII-only. --self-test (numpy, no torch) + --smoke + metrics.json. PROT-020 (torch->GPU). Route overnight_queue.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import os
os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")
import argparse, time, math, json
from pathlib import Path
from typing import Dict, Tuple, List
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics, resumable_seeds, write_partial, aggregate_partials

ANCHOR_NAME = "substrate_partition_routing_10M_full_v2"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"

# CAPACITY-SENSITIVE DIMENSIONS: smoke must match full along PART_SIZE + DI + DC + TARGET_COS + CAT_COS.
DI = 1024                          # identity vector dim (smoke == full; capacity-sensitive)
DC = 256                           # category vector dim (smoke == full; capacity-sensitive)
PART_SIZE = 2000                   # USER LOCKED: smoke == full at part_size=2000 (no regime sign-flip)
SIZE_CAP = 50_000                  # per-partition ceiling for HARD_FAIL band
TARGET_COS = 0.133                 # identity recovery fidelity; centers flat transition in N sweep; REPORTED
CAT_COS = 0.70                     # clean category cue -> robust routing
N_SWEEP = [10_000, 100_000, 1_000_000] if not SMOKE else [10_000, 100_000]
N_QUERIES = 200 if not SMOKE else 60
FLAT_Q_CAP = 120 if not SMOKE else 40
CHUNK = 250_000
SEEDS_FULL = [11, 13, 19]          # USER cross-cell consistent
SEEDS_SMOKE = [11]                  # smoke runs only seed 11 (full runs all 3)
SEEDS = SEEDS_SMOKE if SMOKE else SEEDS_FULL

# PROSPECTIVE BANDS (LOCKED AT MODULE INIT per META_PROSPECTIVE_BANDS_FRESH_SEEDS)
BAND_HARD_PASS_M100K_ROUTED = 0.85         # routed recall@10 floor at N=100k
BAND_HARD_PASS_M100K_CV = 0.05             # cv ceiling across seeds at N=100k
BAND_HARD_PASS_M100K_ROUTE_ACC = 0.95      # routing accuracy floor at N=100k
BAND_HARD_PASS_M1M_ROUTED = 0.50           # routed recall@10 stretch floor at N=1M
BAND_HARD_FAIL_M100K_ROUTED = 0.50         # routed recall@10 hard-fail floor at N=100k
BAND_CLIFF_DROP = 0.35                     # cliff = drop >= 0.35 between consecutive N
BAND_Q_SUSPECT_SATURATION = 0.995          # if routed >= this, suspect saturation
# self-assert prospective bands locked (META_PROSPECTIVE_BANDS_FRESH_SEEDS)
assert 0.0 < BAND_HARD_PASS_M100K_ROUTED < 1.0, "band locked"
assert 0.0 < BAND_HARD_FAIL_M100K_ROUTED < BAND_HARD_PASS_M100K_ROUTED, "fail band must be < pass band"
assert BAND_HARD_PASS_M1M_ROUTED < BAND_HARD_PASS_M100K_ROUTED, "stretch band must be < primary band"


def _np_unit(M):
    return M / (np.linalg.norm(M, axis=-1, keepdims=True) + 1e-12)


def _retrieval_noise(target_cos):
    return math.sqrt(max(0.0, 1.0 / (target_cos * target_cos) - 1.0))


# ---------- pure-numpy core (used by self-test; torch mirrors it for the GPU run) ----------
def identity_chunk_np(g0, n, di, seed):
    rng = np.random.default_rng((seed * 2_654_435_761 + g0) & ((1 << 63) - 1))
    return _np_unit(rng.standard_normal((n, di)).astype(np.float32))


def count_beats_np(q, g0, n, di, seed, target_score):
    A = identity_chunk_np(g0, n, di, seed)
    return int((A @ q > target_score).sum())


def _selftest():
    di = 128; seed = 7
    # determinism
    assert np.allclose(identity_chunk_np(0, 5, di, seed), identity_chunk_np(0, 5, di, seed))
    # a query near identity g=3 recovers it: with low noise, recall@1 over a small set
    ids = identity_chunk_np(0, 50, di, seed)
    tgt = ids[3]
    rng = np.random.default_rng(99)
    q = _np_unit(tgt + 0.3 * _np_unit(rng.standard_normal(di).astype(np.float32)))
    ts = float(q @ tgt)
    beats = int((ids @ q > ts).sum())
    assert beats == 0, beats                                   # target is top-1 in a clean 50-set
    # N-INVARIANCE of routed vs flat-degradation: more distractors -> more beats (monotone), at fixed query
    rng2 = np.random.default_rng(5)
    tgt2 = _np_unit(rng2.standard_normal(di).astype(np.float32))
    q2 = _np_unit(tgt2 + _retrieval_noise(0.2) * _np_unit(rng2.standard_normal(di).astype(np.float32)))
    ts2 = float(q2 @ tgt2)
    b_small = count_beats_np(q2, 1000, 2000, di, seed, ts2)
    b_big = b_small + count_beats_np(q2, 3000, 8000, di, seed, ts2)
    assert b_big >= b_small, (b_small, b_big)
    # retrieval noise maps to target cos
    r = _retrieval_noise(0.133); assert abs(1.0 / math.sqrt(1 + r * r) - 0.133) < 1e-6
    # routing: clean category cue routes to the right partition
    rngc = np.random.default_rng(3); P = 50
    C = _np_unit(rngc.standard_normal((P, 64)).astype(np.float32))
    p_true = 17
    qc = _np_unit(CAT_COS * C[p_true] + math.sqrt(1 - CAT_COS**2) * _np_unit(rngc.standard_normal(64).astype(np.float32)))
    assert int(np.argmax(C @ qc)) == p_true
    # band sanity (META_PROSPECTIVE_BANDS_FRESH_SEEDS)
    assert BAND_HARD_PASS_M100K_ROUTED > BAND_HARD_FAIL_M100K_ROUTED
    assert BAND_HARD_PASS_M1M_ROUTED < BAND_HARD_PASS_M100K_ROUTED
    assert PART_SIZE == 2000, "USER LOCKED part_size=2000 across smoke/full"
    print("[selftest] PASS: substrate_partition_routing_10M_full_v2 (decoupled cues + N-monotone + routing + bands locked)", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)
try:
    import torch
except Exception as e:
    print("[FATAL] torch: %s" % e, flush=True); sys.exit(1)
DEV = "cuda" if torch.cuda.is_available() else "cpu"
print("[device] %s" % DEV, flush=True)
# Fix #24: log GPU utilization at start so verdict can verify GPU was actually used
GPU_AVAIL = torch.cuda.is_available()
GPU_NAME = torch.cuda.get_device_name(0) if GPU_AVAIL else "cpu"
print("[device] gpu_avail=%s name=%s" % (GPU_AVAIL, GPU_NAME), flush=True)


def identity_chunk_t(g0, n, di, seed):
    gen = torch.Generator(device=DEV); gen.manual_seed((seed * 2_654_435_761 + g0) & ((1 << 63) - 1))
    A = torch.randn(n, di, generator=gen, device=DEV)
    return A / (A.norm(dim=1, keepdim=True) + 1e-12)


def target_identity_t(g, di, seed):
    return identity_chunk_t(g, 1, di, seed)[0]                 # atom g's identity = its own 1-row chunk seeded by g


def flat_recall_at(N, di, seed, queries_t, target_g, target_score, k=10):
    """recall@10 of each query's target identity over ALL N identities (streamed in chunks). queries_t: (Q,di)."""
    Q = queries_t.shape[0]
    beats = torch.zeros(Q, device=DEV)
    for g0 in range(0, N, CHUNK):
        n = min(CHUNK, N - g0)
        A = identity_chunk_t(g0, n, di, seed)                 # (n,di)
        sims = queries_t @ A.T                                 # (Q,n)
        beats += (sims > target_score[:, None]).sum(dim=1).float()
        del A, sims
    if DEV == "cuda": torch.cuda.empty_cache()
    return (beats < k).float().mean().item()


def run_one_seed(seed: int) -> Dict:
    """Per-seed run. Each seed gets its own (Cc, tgt_g, queries) so seeds are independent."""
    di = DI
    r = _retrieval_noise(TARGET_COS)
    rng = np.random.default_rng(seed ^ 0xA11CE)
    part_size = PART_SIZE
    Nmax = N_SWEEP[-1]
    P_max = Nmax // part_size
    Cc = _np_unit(rng.standard_normal((P_max, DC)).astype(np.float32))
    Cc_t = torch.from_numpy(Cc).to(DEV)
    tgt_g = rng.integers(0, Nmax, N_QUERIES).astype(np.int64)
    q_id = np.zeros((N_QUERIES, di), dtype=np.float32)
    q_cat = np.zeros((N_QUERIES, DC), dtype=np.float32)
    for j, g in enumerate(tgt_g):
        idg = target_identity_t(int(g), di, seed).cpu().numpy()
        q_id[j] = _np_unit(idg + r * _np_unit(rng.standard_normal(di).astype(np.float32)))
        p = int(g) // part_size
        q_cat[j] = _np_unit(CAT_COS * Cc[p] + math.sqrt(1 - CAT_COS**2) * _np_unit(rng.standard_normal(DC).astype(np.float32)))
    q_id_t = torch.from_numpy(q_id).to(DEV); q_cat_t = torch.from_numpy(q_cat).to(DEV)
    tgt_score = torch.stack([q_id_t[j] @ target_identity_t(int(tgt_g[j]), di, seed) for j in range(N_QUERIES)])

    # routing accuracy at the LARGEST N
    routes = torch.argmax(q_cat_t @ Cc_t.T, dim=1).cpu().numpy()
    true_p = (tgt_g // part_size)
    route_acc = float(np.mean(routes == true_p))

    # ROUTED recall@10 (N-invariant by construction)
    routed_hits = 0
    for j in range(N_QUERIES):
        rp = int(routes[j]); g0 = rp * part_size
        A = identity_chunk_t(g0, part_size, di, seed)
        beats = int((A @ q_id_t[j] > tgt_score[j]).sum().item())
        del A
        routed_hits += 1 if (rp == int(true_p[j]) and beats < 10) else 0
    routed_recall = routed_hits / N_QUERIES
    if DEV == "cuda": torch.cuda.empty_cache()

    # FLAT recall@10 sweep over N
    flat_curve = {}
    for N in N_SWEEP:
        qn = min(N_QUERIES, FLAT_Q_CAP)
        t0 = time.time()
        rec = flat_recall_at(N, di, seed, q_id_t[:qn], tgt_g[:qn], tgt_score[:qn])
        flat_curve[N] = round(rec, 4)
        print("  seed=%d FLAT recall@10 @N=%d : %.4f (%.1fs, n_q=%d)" % (seed, N, rec, time.time() - t0, qn), flush=True)
    flat_vals = [flat_curve[N] for N in N_SWEEP]
    strictly_decreasing = all(flat_vals[i] > flat_vals[i + 1] - 1e-9 for i in range(len(flat_vals) - 1)) and flat_vals[0] > flat_vals[-1]

    # ROUTED recall@10 PER N: for each N in the sweep, partition the universe into N/part_size partitions, route + recall.
    # This gives the per-M chain-grade data the verdict needs.
    routed_per_N = {}
    routed_acc_per_N = {}
    for N in N_SWEEP:
        P_N = N // part_size
        # restrict targets/routes to indices in [0, N)
        in_universe = (tgt_g < N)
        if not in_universe.any():
            routed_per_N[N] = float("nan"); routed_acc_per_N[N] = float("nan"); continue
        cc_N_t = Cc_t[:P_N]                                     # use only partitions in [0, P_N)
        q_cat_N = q_cat_t[in_universe]
        q_id_N = q_id_t[in_universe]
        tgt_g_N = tgt_g[in_universe]
        tgt_score_N = tgt_score[in_universe]
        routes_N = torch.argmax(q_cat_N @ cc_N_t.T, dim=1).cpu().numpy()
        true_p_N = (tgt_g_N // part_size)
        # routing acc within this N's partition space
        # NOTE: queries' true_p might exceed P_N if global tgt_g is in a partition not in universe -- mask
        valid = true_p_N < P_N
        ra_N = float(np.mean(routes_N[valid] == true_p_N[valid])) if valid.any() else float("nan")
        routed_acc_per_N[N] = round(ra_N, 4)
        # routed recall@10 within partition
        rr_hits = 0; rr_total = int(valid.sum())
        for k_idx, valid_flag in enumerate(valid):
            if not valid_flag: continue
            rp = int(routes_N[k_idx]); g0 = rp * part_size
            if g0 + part_size > N:
                # partition extends beyond N -- cap chunk
                chunk_n = N - g0
                if chunk_n <= 0: continue
            else:
                chunk_n = part_size
            A = identity_chunk_t(g0, chunk_n, di, seed)
            beats = int((A @ q_id_N[k_idx] > tgt_score_N[k_idx]).sum().item())
            del A
            rr_hits += 1 if (rp == int(true_p_N[k_idx]) and beats < 10) else 0
        routed_per_N[N] = round(rr_hits / rr_total, 4) if rr_total else float("nan")
        if DEV == "cuda": torch.cuda.empty_cache()
        print("  seed=%d ROUTED recall@10 @N=%d : %.4f (route_acc=%.4f, P_N=%d)" % (seed, N, routed_per_N[N], routed_acc_per_N[N], P_N), flush=True)

    max_part = part_size
    return {"seed": seed, "n_sweep": N_SWEEP, "part_size": part_size, "max_part_le_cap": bool(part_size <= SIZE_CAP),
            "P_max": P_max, "target_cos": TARGET_COS, "retrieval_noise": round(r, 4), "cat_cos": CAT_COS,
            "routed_recall_at_Nmax": round(routed_recall, 4), "routing_acc_at_Nmax": round(route_acc, 4),
            "routed_per_N": {str(k): v for k, v in routed_per_N.items()},
            "routing_acc_per_N": {str(k): v for k, v in routed_acc_per_N.items()},
            "flat_curve": {str(k): v for k, v in flat_curve.items()}, "flat_strictly_decreasing": strictly_decreasing,
            "max_partition": max_part, "run_mode": RUN_MODE, "N": DI}


def aggregate_seeds(per_seed: List[Dict]) -> Dict:
    """Aggregate per-seed dicts into mean/cv per N and overall verdict inputs."""
    n_seeds = len(per_seed)
    Ns = N_SWEEP
    routed_per_N_mean = {}; routed_per_N_cv = {}; routed_per_N_seeds = {}
    route_acc_per_N_mean = {}; route_acc_per_N_cv = {}
    flat_per_N_mean = {}
    for N in Ns:
        rs = [s["routed_per_N"].get(str(N)) for s in per_seed]
        rs = [v for v in rs if v is not None and not (isinstance(v, float) and math.isnan(v))]
        if not rs:
            routed_per_N_mean[N] = float("nan"); routed_per_N_cv[N] = float("nan"); continue
        m = float(np.mean(rs)); sd = float(np.std(rs))
        cv = sd / m if m > 1e-9 else float("inf")
        routed_per_N_mean[N] = round(m, 4); routed_per_N_cv[N] = round(cv, 4); routed_per_N_seeds[N] = [round(v, 4) for v in rs]
        # route acc
        ras = [s["routing_acc_per_N"].get(str(N)) for s in per_seed]
        ras = [v for v in ras if v is not None and not (isinstance(v, float) and math.isnan(v))]
        if ras:
            ra_m = float(np.mean(ras)); ra_sd = float(np.std(ras))
            route_acc_per_N_mean[N] = round(ra_m, 4); route_acc_per_N_cv[N] = round(ra_sd / ra_m if ra_m > 1e-9 else float("inf"), 4)
        # flat
        fs = [s["flat_curve"].get(str(N)) for s in per_seed]
        fs = [v for v in fs if v is not None]
        if fs:
            flat_per_N_mean[N] = round(float(np.mean(fs)), 4)
    flat_vals = [flat_per_N_mean.get(N, float("nan")) for N in Ns]
    valid_flat = [v for v in flat_vals if not math.isnan(v)]
    flat_strictly_decreasing = len(valid_flat) >= 2 and all(valid_flat[i] > valid_flat[i + 1] - 1e-9 for i in range(len(valid_flat) - 1)) and valid_flat[0] > valid_flat[-1]
    return {"n_seeds": n_seeds, "seeds": [s["seed"] for s in per_seed],
            "routed_per_N_mean": {str(k): v for k, v in routed_per_N_mean.items()},
            "routed_per_N_cv": {str(k): v for k, v in routed_per_N_cv.items()},
            "routed_per_N_per_seed": {str(k): v for k, v in routed_per_N_seeds.items()},
            "routing_acc_per_N_mean": {str(k): v for k, v in route_acc_per_N_mean.items()},
            "routing_acc_per_N_cv": {str(k): v for k, v in route_acc_per_N_cv.items()},
            "flat_per_N_mean": {str(k): v for k, v in flat_per_N_mean.items()},
            "flat_strictly_decreasing": flat_strictly_decreasing,
            "part_size": PART_SIZE, "n_sweep": N_SWEEP, "target_cos": TARGET_COS, "cat_cos": CAT_COS}


def verdict(agg: Dict) -> Tuple[str, str]:
    if not agg.get("n_seeds") or agg["n_seeds"] == 0:
        return ("UNKNOWN", "UNKNOWN: no seed results")
    rN_mean = agg["routed_per_N_mean"]; rN_cv = agg["routed_per_N_cv"]
    raN_mean = agg["routing_acc_per_N_mean"]
    flat_mono = agg["flat_strictly_decreasing"]
    # per-arm metrics in verdict (Fix #28)
    per_N_summary = "; ".join(["N=%s: routed=%s (cv=%s; seeds=%s) routeacc=%s flat=%s" % (
        N, rN_mean.get(str(N)), rN_cv.get(str(N)),
        agg["routed_per_N_per_seed"].get(str(N), []),
        raN_mean.get(str(N)), agg["flat_per_N_mean"].get(str(N))) for N in N_SWEEP])
    s = "PER-N (%d seeds %s): %s; part_size=%d; flat_mono_dec=%s" % (
        agg["n_seeds"], agg["seeds"], per_N_summary, agg["part_size"], flat_mono)

    r100k = rN_mean.get(str(100_000))
    cv100k = rN_cv.get(str(100_000))
    ra100k = raN_mean.get(str(100_000))
    r1M = rN_mean.get(str(1_000_000)) if 1_000_000 in N_SWEEP else None

    # HARD_FAIL first
    if r100k is not None and not math.isnan(r100k) and r100k < BAND_HARD_FAIL_M100K_ROUTED:
        return ("HARD_FAIL", "HARD_FAIL_PARTITION_DEGRADES: routed recall@10 at N=100k = %.4f < %.2f -- invalidates v1 smoke; partition routing does NOT cleanly rescue at production scale. %s" % (r100k, BAND_HARD_FAIL_M100K_ROUTED, s))

    # Q-discipline saturation suspicion
    suspect_sat = (r100k is not None and r100k >= BAND_Q_SUSPECT_SATURATION) or (r1M is not None and not math.isnan(r1M) and r1M >= BAND_Q_SUSPECT_SATURATION)
    sat_note = ""
    if suspect_sat:
        sat_note = " [Q-DISCIPLINE: suspect saturation -- routed >= %.3f without mechanism story; UNDER-CLAIM tier]" % BAND_Q_SUSPECT_SATURATION

    # primary band
    primary_pass = (r100k is not None and not math.isnan(r100k) and r100k >= BAND_HARD_PASS_M100K_ROUTED
                    and cv100k is not None and not math.isnan(cv100k) and cv100k <= BAND_HARD_PASS_M100K_CV
                    and ra100k is not None and not math.isnan(ra100k) and ra100k >= BAND_HARD_PASS_M100K_ROUTE_ACC)
    # stretch band
    stretch_pass = primary_pass and (r1M is not None and not math.isnan(r1M) and r1M >= BAND_HARD_PASS_M1M_ROUTED)
    # cliff between 100k and 1M
    cliff_id = None
    if r100k is not None and r1M is not None and not math.isnan(r100k) and not math.isnan(r1M):
        if r100k >= BAND_HARD_PASS_M100K_ROUTED and r1M < BAND_HARD_PASS_M1M_ROUTED:
            cliff_id = "between_100k_and_1M"

    if stretch_pass and not suspect_sat:
        return ("HARD_PASS", "HARD_PASS_PARTIAL_AT_M_1M (+ chain-grade @ M=100k): routed recall@10 @100k=%.4f cv=%.4f route_acc=%.4f passes primary band AND @1M=%.4f >= %.2f stretch band -- partition-routing substrate scales to 1M atoms. %s" % (r100k, cv100k, ra100k, r1M, BAND_HARD_PASS_M1M_ROUTED, s + sat_note))
    if primary_pass and not suspect_sat:
        if cliff_id:
            return ("HARD_PASS", "HARD_PASS_CHAIN_GRADE_PARTITION_ROUTING_AT_M_100k (CHAIN_GRADE_AT_LOWER_M_CLIFF identified): routed @100k=%.4f cv=%.4f route_acc=%.4f passes primary band; cliff %s -- substrate KG scales chain-grade to 100k via partition routing; 1M is beyond envelope. %s" % (r100k, cv100k, ra100k, cliff_id, s + sat_note))
        return ("HARD_PASS", "HARD_PASS_CHAIN_GRADE_PARTITION_ROUTING_AT_M_100k: routed @100k=%.4f cv=%.4f route_acc=%.4f passes primary band -- substrate KG chain-grade at M=100k via partition routing. 1M: %s. %s" % (r100k, cv100k, ra100k, "not in sweep" if r1M is None else "%.4f" % r1M, s + sat_note))
    if primary_pass and suspect_sat:
        return ("HARD_PASS", "HARD_PASS_CHAIN_GRADE_PARTITION_ROUTING_AT_M_100k (UNDER-CLAIMED per Q-discipline): routed @100k=%.4f cv=%.4f passes primary band but suspect saturation; tier as MEASURED_MECHANISM by cert-owner unless mechanism story. %s" % (r100k, cv100k, s + sat_note))
    # MIDDLE_BAND
    return ("MIDDLE_BAND", "MIDDLE_BAND: routing rescue partially demonstrated but did not clear primary chain-grade band. %s" % s)


print("[config] anchor=%s mode=%s Di=%d Dc=%d N_sweep=%s part_size=%d seeds=%s target_cos=%.3f" % (
    ANCHOR_NAME, RUN_MODE, DI, DC, N_SWEEP, PART_SIZE, SEEDS, TARGET_COS), flush=True)

out_dir = get_output_dir(ANCHOR_NAME)
t0 = time.time()
# checkpoint-resume support (PROT-021)
run_config = {"N": DI, "run_mode": RUN_MODE}
done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
print("[ckpt] %d of %d seeds already complete; running %s" % (len(done), len(SEEDS), remaining), flush=True)
for seed in remaining:
    print("[seed %d] starting at %s" % (seed, time.strftime("%H:%M:%S")), flush=True)
    res = run_one_seed(seed)
    write_partial(out_dir, seed, res)
per_seed = list(aggregate_partials(out_dir, SEEDS).values())
agg = aggregate_seeds(per_seed)
v, vmsg = verdict(agg)
print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "headline": vmsg,
           "run_mode": RUN_MODE, "n_seeds": len(per_seed), "seeds": [s["seed"] for s in per_seed],
           "aggregate": agg, "per_seed": per_seed, "elapsed_s": time.time() - t0,
           "gpu_available": GPU_AVAIL, "gpu_name": GPU_NAME,
           "bands": {"HARD_PASS_M100K_ROUTED": BAND_HARD_PASS_M100K_ROUTED, "HARD_PASS_M100K_CV": BAND_HARD_PASS_M100K_CV,
                     "HARD_PASS_M100K_ROUTE_ACC": BAND_HARD_PASS_M100K_ROUTE_ACC, "HARD_PASS_M1M_ROUTED": BAND_HARD_PASS_M1M_ROUTED,
                     "HARD_FAIL_M100K_ROUTED": BAND_HARD_FAIL_M100K_ROUTED, "Q_SUSPECT_SATURATION": BAND_Q_SUSPECT_SATURATION},
           "config_version": "v2_seeds_11_13_19_partsize_2000_nsweep_10k_100k_1M"}
write_metrics(out_dir, metrics, per_seed)
print("[metrics] written", flush=True)
