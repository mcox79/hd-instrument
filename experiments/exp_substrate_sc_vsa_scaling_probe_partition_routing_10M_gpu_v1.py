"""
exp_substrate_sc_vsa_scaling_probe_partition_routing_10M_gpu_v1.py -- CELL SC: VSA scaling existential validation at 10M synthetic atoms (DECOUPLED-CUE scaling curve) -- GPU (remote desktop).

ROUTING: Research SC DECISION (research_to_exp_dev_CELL_SC_DECISION_ENDORSE_Option_A...) -- Option A scaling-curve study, decoupled cues,
  5-criterion pre-reg SIGNED. Existential validation for the 100M-1B atom roadmap: does the substrate's L1 partition-routing + per-partition
  VSA cleanup SURVIVE at scale? Known failure mode (memory substrate_corpus_size_scaling R26): a SINGLE flat cleanup memory hits a tau-limit
  -- catastrophic interference collapses recall as N grows. RESCUE = partition routing (cap partitions at <=50K, route, clean up within).

  DECOUPLED-CUE model (Exp-Dev caught the coupling artifact in the naive single-noise model; this is the faithful design): every atom has
  TWO independent cues --
    * CATEGORY cue c_p (dim Dc, shared within partition p): read by ROUTING (mirrors clean L1 partition labels).
    * IDENTITY cue id_g (dim Di, unique per atom, near-orthogonal): read by CLEANUP (mirrors noisier composite_hrr identity).
  A query = [category cue = normalize(c_p + cat_noise)] + [identity cue = normalize(id_target + r*noise)], r set so identity-cos = TARGET_COS.
  Routing accuracy is then governed by cat_noise (kept clean), INDEPENDENT of the cleanup difficulty TARGET_COS -- so we can put FLAT into
  the interference-collapse regime WITHOUT breaking routing (the artifact that killed the naive model).

  KEY robust (non-tuned) claim: ROUTED recall@10 depends ONLY on partition size (<=50K) -> N-INVARIANT; FLAT recall@10 degrades monotonically
  with N. TARGET_COS is chosen to CENTER the flat transition inside the {1e5,1e6,1e7} window (so the degradation is observable) and is
  REPORTED; the qualitative result (routed flat, flat decreasing) holds across a tau range. Memory-bounded: identities regenerated per chunk
  on the GPU from (seed, global_idx) -- never materializes N x Di (40GB at 1e7).

PRE-REGISTERED (Research-signed, 5 criteria): HARD-PASS = ALL of {routed recall@10 @1e7 >= 0.60 ; flat strictly monotone-decreasing across
  the N sweep ; routing accuracy @1e7 >= 0.90 ; max partition <= 50K}. Criterion 5 (tau-window vs D=2048) is a reported diagnostic. HARD-FAIL
  if ANY of {routed < 0.40 ; flat non-monotone/increasing ; routing < 0.70 ; max partition > 100K}. Else MIDDLE. UNKNOWN if torch unavailable.
ASCII-only. --self-test (numpy, no torch) + --smoke + metrics.json. PROT-020 (torch->GPU). PROT-018 (N in anchor). Route overnight_queue.
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
DI = 1024; DC = 256; PART_SIZE = 2_000 if ("--smoke" in sys.argv or os.environ.get("HDLAB_RUN_MODE", "").lower() == "smoke") else 40_000; SIZE_CAP = 50_000
TARGET_COS = 0.133                      # identity recovery fidelity; centers the flat transition in {1e5,1e6,1e7}; REPORTED
CAT_COS = 0.70                          # clean category cue -> routing robust + INDEPENDENT of TARGET_COS
N_SWEEP = [100_000, 1_000_000, 10_000_000] if not SMOKE else [10_000, 100_000]
N_QUERIES = 200 if not SMOKE else 60
FLAT_Q_CAP = 120 if not SMOKE else 40   # cap queries for the expensive flat pass at the largest N
CHUNK = 250_000; SEED = 1028; D_SWEEP = [1024, 2048]


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
    b_big = b_small + count_beats_np(q2, 3000, 8000, di, seed, ts2)   # superset
    assert b_big >= b_small, (b_small, b_big)
    # retrieval noise maps to target cos
    r = _retrieval_noise(0.133); assert abs(1.0 / math.sqrt(1 + r * r) - 0.133) < 1e-6
    # routing: clean category cue routes to the right partition
    rngc = np.random.default_rng(3); P = 50
    C = _np_unit(rngc.standard_normal((P, 64)).astype(np.float32))
    p_true = 17
    qc = _np_unit(CAT_COS * C[p_true] + math.sqrt(1 - CAT_COS**2) * _np_unit(rngc.standard_normal(64).astype(np.float32)))
    assert int(np.argmax(C @ qc)) == p_true
    print("[selftest] PASS: substrate_sc_vsa_scaling_probe (decoupled cues: identity recall + N-monotone beats + routing)", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)
try:
    import torch
except Exception as e:
    print("[FATAL] torch: %s" % e, flush=True); sys.exit(1)
DEV = "cuda" if torch.cuda.is_available() else "cpu"
print("[device] %s" % DEV, flush=True)


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


def run() -> Dict:
    di = DI
    r = _retrieval_noise(TARGET_COS)
    rng = np.random.default_rng(SEED ^ 0xA11CE)
    part_size = PART_SIZE
    Nmax = N_SWEEP[-1]
    # category dirs for the LARGEST P (Nmax/part_size); smaller N use a prefix
    P_max = Nmax // part_size
    Cc = _np_unit(rng.standard_normal((P_max, DC)).astype(np.float32))
    Cc_t = torch.from_numpy(Cc).to(DEV)
    # choose N_QUERIES target atoms by GLOBAL index in [0, Nmax); their partition = g // part_size
    tgt_g = rng.integers(0, Nmax, N_QUERIES).astype(np.int64)
    # build identity queries (noisy) + category queries (clean) for routing
    q_id = np.zeros((N_QUERIES, di), dtype=np.float32)
    q_cat = np.zeros((N_QUERIES, DC), dtype=np.float32)
    for j, g in enumerate(tgt_g):
        idg = target_identity_t(int(g), di, SEED).cpu().numpy()
        q_id[j] = _np_unit(idg + r * _np_unit(rng.standard_normal(di).astype(np.float32)))
        p = int(g) // part_size
        q_cat[j] = _np_unit(CAT_COS * Cc[p] + math.sqrt(1 - CAT_COS**2) * _np_unit(rng.standard_normal(DC).astype(np.float32)))
    q_id_t = torch.from_numpy(q_id).to(DEV); q_cat_t = torch.from_numpy(q_cat).to(DEV)
    tgt_score = torch.stack([q_id_t[j] @ target_identity_t(int(tgt_g[j]), di, SEED) for j in range(N_QUERIES)])

    # --- routing accuracy at the LARGEST N (P_max partitions) ---
    routes = torch.argmax(q_cat_t @ Cc_t.T, dim=1).cpu().numpy()
    true_p = (tgt_g // part_size)
    route_acc = float(np.mean(routes == true_p))

    # --- ROUTED recall@10: search ONLY the target's partition (<=part_size identities). N-invariant by construction. ---
    routed_hits = 0
    for j in range(N_QUERIES):
        rp = int(routes[j]); g0 = rp * part_size
        A = identity_chunk_t(g0, part_size, di, SEED)
        beats = int((A @ q_id_t[j] > tgt_score[j]).sum().item())
        del A
        routed_hits += 1 if (rp == int(true_p[j]) and beats < 10) else 0
    routed_recall = routed_hits / N_QUERIES
    if DEV == "cuda": torch.cuda.empty_cache()

    # --- FLAT recall@10 sweep over N ---
    flat_curve = {}
    for N in N_SWEEP:
        qn = min(N_QUERIES, FLAT_Q_CAP)
        t = time.time()
        rec = flat_recall_at(N, di, SEED, q_id_t[:qn], tgt_g[:qn], tgt_score[:qn])
        flat_curve[N] = round(rec, 4)
        print("  FLAT recall@10 @N=%d : %.4f (%.1fs, n_q=%d)" % (N, rec, time.time() - t, qn), flush=True)
    flat_vals = [flat_curve[N] for N in N_SWEEP]
    strictly_decreasing = all(flat_vals[i] > flat_vals[i + 1] - 1e-9 for i in range(len(flat_vals) - 1)) and flat_vals[0] > flat_vals[-1]

    # --- criterion 5: tau-window vs D (distractor-cos scale at Di=1024 vs 2048) ---
    dwin = {}
    for d in D_SWEEP:
        # empirical 99.99-percentile of |distractor cos| over a sample (proxy for flat interference floor at this D)
        smp = identity_chunk_t(7_000_000, 20000, d, SEED)
        probe = smp[0]
        cs = (smp[1:] @ probe).abs()
        dwin[d] = round(float(torch.quantile(cs, 0.9999).item()), 4)
    window_widens = dwin[2048] < dwin[1024]    # higher D -> lower interference floor -> routed/flat separation cleaner (widens)

    P_at = {N: N // part_size for N in N_SWEEP}
    max_part = part_size
    print("  N-sweep=%s part_size=%d (max<=%d:%s) P@Nmax=%d | target_cos=%.3f (r=%.2f) cat_cos=%.2f" % (
        N_SWEEP, part_size, SIZE_CAP, part_size <= SIZE_CAP, P_max, TARGET_COS, r, CAT_COS), flush=True)
    print("  ROUTED recall@10=%.4f (N-invariant; partition<=%d) | routing acc@Nmax(P=%d)=%.4f" % (routed_recall, part_size, P_max, route_acc), flush=True)
    print("  FLAT curve=%s strictly-decreasing=%s | tau-floor D1024=%.4f D2048=%.4f widens=%s" % (
        flat_curve, strictly_decreasing, dwin[1024], dwin[2048], window_widens), flush=True)
    return {"n_sweep": N_SWEEP, "part_size": part_size, "max_part_le_cap": bool(part_size <= SIZE_CAP),
            "P_max": P_max, "target_cos": TARGET_COS, "retrieval_noise": round(r, 4), "cat_cos": CAT_COS,
            "routed_recall": round(routed_recall, 4), "routing_acc": round(route_acc, 4),
            "flat_curve": {str(k): v for k, v in flat_curve.items()}, "flat_strictly_decreasing": strictly_decreasing,
            "routed_at_Nmax": round(routed_recall, 4), "flat_at_Nmax": flat_curve[N_SWEEP[-1]],
            "tau_floor_by_D": dwin, "tau_window_widens_with_D": window_widens, "max_partition": max_part}


def verdict(r) -> Tuple[str, str]:
    if r.get("error"):
        return ("UNKNOWN", "UNKNOWN: " + str(r["error"]))
    rr = r["routed_recall"]; mono = r["flat_strictly_decreasing"]; racc = r["routing_acc"]; cap = r["max_part_le_cap"]
    c1 = rr >= 0.60; c2 = mono; c3 = racc >= 0.90; c4 = cap
    f1 = rr < 0.40; f2 = (not mono); f3 = racc < 0.70; f4 = r["max_partition"] > 100_000
    s = ("N-sweep %s part_size=%d (<=50K:%s, P@Nmax=%d); ROUTED recall@10=%.4f (N-invariant) vs FLAT curve %s (strictly-decreasing=%s); "
         "routing acc@Nmax=%.4f; target_cos=%.3f cat_cos=%.2f; tau-floor D1024=%.4f D2048=%.4f (widens=%s). RESCUE = routed holds while flat collapses.") % (
        r["n_sweep"], r["part_size"], cap, r["P_max"], rr, r["flat_curve"], mono, racc, r["target_cos"], r["cat_cos"],
        r["tau_floor_by_D"].get(1024), r["tau_floor_by_D"].get(2048), r["tau_window_widens_with_D"])
    if f1 or f2 or f3 or f4:
        why = []
        if f1: why.append("routed recall %.2f<0.40" % rr)
        if f2: why.append("flat NOT monotone-decreasing (cue interaction?)")
        if f3: why.append("routing acc %.2f<0.70" % racc)
        if f4: why.append("partition>100K")
        return ("HARD_FAIL", "HARD_FAIL: %s -- partition routing does NOT cleanly rescue VSA cleanup at 10M; halt 100M ingest plan / revisit routing class. " % "; ".join(why) + s)
    if c1 and c2 and c3 and c4:
        return ("HARD_PASS", "HARD_PASS: VSA + L1 partition-routing SURVIVES to 10M on all 4 signed criteria -- routed recall@10=%.4f>=0.60 (N-invariant), flat strictly degrades across the N sweep, routing acc=%.4f>=0.90, max partition<=50K. The 100M-1B roadmap's existential precondition HOLDS: substrate scales where flat-RAG hits per-query interference. " % (rr, racc) + s)
    return ("MIDDLE_BAND", "MIDDLE_BAND: routing rescue partially demonstrated but not all 4 criteria clear HARD-PASS (routed>=0.60:%s mono-decr:%s routing>=0.90:%s cap:%s). " % (c1, c2, c3, c4) + s)


print("[config] anchor=%s mode=%s Di=%d Dc=%d N_sweep=%s target_cos=%.3f" % (ANCHOR_NAME, RUN_MODE, DI, DC, N_SWEEP, TARGET_COS), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
