"""
exp_substrate_codebook_near_duplicate_diagnostic_cpu_v1.py -- quantify the algebra-HRR near-duplicate structure that caps
  composition/decode cleanup (Cells A/B/CSLS follow-on diagnostic) -- CPU.

ROUTING: follow-on to CSLS HARD_FAIL finding (clustered-codebook decode deficit is GENUINE NEAR-DUPLICATES, not hubness).
  Turns the "fix is finer encoding / de-duplication" recommendation into an ACTIONABLE spec: how many atom pairs near-collide,
  WHICH atoms, what the F=1 cleanup floor (irreducible near-duplicate confusion) is, and whether de-duplicating the codebook
  recovers cleanup toward the uniform-codebook 1.0. Substrate-quality-first; NO LLM frame.

  Diagnostics over the 280-atom algebra_hrr codebook:
    1. Pairwise cosine Gram -> count near-duplicate pairs at cos thresholds {0.90,0.95,0.99}; nearest-neighbor cosine distribution.
    2. F=1 cleanup (single binding, NO crosstalk) -> any failure is PURE near-duplicate confusion. The F=1 deficit = irreducible
       near-duplicate floor. List the failing atoms + their nearest neighbor (the collision target) for a Testbed differentiation list.
    3. DE-DUPLICATION test: greedily merge atoms with cos > thr into one representative -> reduced codebook K'. Re-measure cleanup
       at F=1,3 on the de-duplicated codebook. If cleanup recovers toward 1.0, de-duplication is the mitigation (quantifies recoverable deficit).

PRE-REGISTERED (diagnostic; substrate-property):
  REPORT near-duplicate pair counts + F=1 floor + de-dup recovery. HARD-PASS framing: de-duplication at cos>0.95 lifts F=3
  cleanup by >= +0.05 (de-dup is a real mitigation). MIDDLE: +0.01-0.05. HARD-FAIL: < +0.01 (deficit not from mergeable
  duplicates -- atoms are distinct-but-close, needs finer ENCODING not merging). UNKNOWN if corpus load fails.
ASCII-only. CPU. --self-test + --smoke + metrics.json. Route via local_cpu_queue.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time, json
from pathlib import Path
from typing import Dict, Tuple
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "substrate_codebook_near_duplicate_diagnostic_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
THRESHOLDS = [0.90, 0.95, 0.99]
SEEDS = [7, 8, 9]
N_TRIALS = 30


def _bind(a, b): return np.fft.ifft(np.fft.fft(a) * np.fft.fft(b)).real
def _unbind(c, b): return np.fft.ifft(np.fft.fft(c) * np.fft.fft(b).conj()).real


def _unitary_roles(n, dim, rng):
    v = rng.standard_normal((n, dim)); fv = np.fft.fft(v, axis=1)
    fv = fv / (np.abs(fv) + 1e-12); return np.fft.ifft(fv, axis=1).real


def _load():
    from backend.substrate_index.partition import PartitionedStore
    from backend.substrate_index.algebra_index import AlgebraIndex
    ps = PartitionedStore(REPO / "data" / "substrate_index")
    ai = AlgebraIndex(dim=1024); ai.build(ps)
    ids, rows = [], []
    for aid, av in ai._atom_vectors.items():
        if av.algebra_hrr is not None:
            ids.append(aid); rows.append(av.algebra_hrr)
    if not rows:
        return None, None
    M = np.stack(rows).astype(np.float64)
    return ids, M / (np.linalg.norm(M, axis=1, keepdims=True) + 1e-12)


def _dedup_reps(M, thr):
    """Greedy: keep an atom unless it has cos>thr with an already-kept atom. Returns kept indices."""
    kept = []
    for i in range(M.shape[0]):
        if all(float(M[i] @ M[k]) <= thr for k in kept):
            kept.append(i)
    return kept


def _cleanup_acc(M, ids_pool, F, n_trials, seeds, dim):
    """cleanup@1 over codebook M (rows already unit), fillers from M, F bindings."""
    Mt = M.T; hit = 0; tot = 0
    for sd in seeds:
        rng = np.random.default_rng(sd * 17 + F)
        for _ in range(n_trials):
            idx = rng.permutation(M.shape[0])[:F]
            R = _unitary_roles(F, dim, rng)
            X = np.sum([_bind(R[i], M[idx[i]]) for i in range(F)], axis=0)
            X = X / (np.linalg.norm(X) + 1e-12)
            for j in range(F):
                est = _unbind(X, R[j])
                sims = (M @ est) / (np.linalg.norm(est) + 1e-12)
                hit += int(int(np.argmax(sims)) == int(idx[j])); tot += 1
    return hit / tot if tot else 0.0


def run() -> Dict:
    ids, M = _load()
    if M is None:
        return {"error": "no_algebra_atoms"}
    Mn, dim = M.shape
    G = M @ M.T; np.fill_diagonal(G, -2.0)
    # 1. near-duplicate pair counts
    iu = np.triu_indices(Mn, k=1)
    pair_cos = G[iu]
    counts = {str(t): int((pair_cos > t).sum()) for t in THRESHOLDS}
    nn = G.max(axis=1)  # nearest-neighbor cosine per atom
    nn_ge = {str(t): int((nn > t).sum()) for t in THRESHOLDS}
    # top colliding pairs (ids)
    order = np.argsort(-pair_cos)[:15]
    top_pairs = [{"a": ids[iu[0][o]], "b": ids[iu[1][o]], "cos": round(float(pair_cos[o]), 4)} for o in order]
    seeds = SEEDS[:1] if SMOKE else SEEDS
    n_trials = 8 if SMOKE else N_TRIALS
    # 2. F=1 cleanup floor (pure near-duplicate confusion)
    f1 = _cleanup_acc(M, ids, 1, n_trials, seeds, dim)
    f3 = _cleanup_acc(M, ids, 3, n_trials, seeds, dim)
    # 3. de-duplication at cos>0.95 -> reduced codebook, re-measure
    thr = 0.95
    kept = _dedup_reps(M, thr); Md = M[kept]
    f1_d = _cleanup_acc(Md, [ids[k] for k in kept], 1, n_trials, seeds, dim)
    f3_d = _cleanup_acc(Md, [ids[k] for k in kept], 3, min(n_trials, max(4, Md.shape[0] // 3)), seeds, dim) if Md.shape[0] >= 3 else None
    print("  near-dup pairs: %s | atoms w/ NN>thr: %s" % (counts, nn_ge), flush=True)
    print("  cleanup F1=%.4f F3=%.4f (full K=%d) | de-dup@0.95 -> K'=%d : F1=%.4f F3=%s (F3 lift=%s)"
          % (f1, f3, Mn, len(kept), f1_d, (round(f3_d, 4) if f3_d is not None else None),
             (round(f3_d - f3, 4) if f3_d is not None else None)), flush=True)
    print("  top colliding pairs:", flush=True)
    for p in top_pairs[:6]:
        print("    cos=%.4f  %s  <->  %s" % (p["cos"], p["a"], p["b"]), flush=True)
    return {"n_atoms": Mn, "dim": dim, "near_dup_pair_counts": counts, "atoms_with_NN_above": nn_ge,
            "top_colliding_pairs": top_pairs, "cleanup_F1_full": round(f1, 4), "cleanup_F3_full": round(f3, 4),
            "dedup_thr": thr, "K_after_dedup": len(kept), "cleanup_F1_dedup": round(f1_d, 4),
            "cleanup_F3_dedup": (round(f3_d, 4) if f3_d is not None else None),
            "f3_dedup_lift": (round(f3_d - f3, 4) if f3_d is not None else None)}


def verdict(r) -> Tuple[str, str]:
    if r.get("error"): return ("UNKNOWN", "UNKNOWN: " + r["error"])
    lift = r.get("f3_dedup_lift")
    s = ("near-dup pairs %s; atoms w/ NN>thr %s; F1_full=%.4f (near-dup floor=%.4f) F3_full=%.4f; de-dup@%.2f K=%d->%d F1=%.4f F3_lift=%s; top pair cos=%.4f (%s <-> %s)"
         % (r["near_dup_pair_counts"], r["atoms_with_NN_above"], r["cleanup_F1_full"], 1 - r["cleanup_F1_full"], r["cleanup_F3_full"],
            r["dedup_thr"], r["n_atoms"], r["K_after_dedup"], r["cleanup_F1_dedup"], lift,
            r["top_colliding_pairs"][0]["cos"], r["top_colliding_pairs"][0]["a"], r["top_colliding_pairs"][0]["b"]))
    if lift is None:
        return ("UNKNOWN", "UNKNOWN: de-dup F3 not measured. " + s)
    if lift >= 0.05:
        return ("HARD_PASS", "HARD_PASS: de-duplication (merge cos>0.95) lifts F=3 cleanup by >=+0.05 -- a chunk of the clustered-codebook deficit IS mergeable near-duplicates; de-dup is a real mitigation, and the residual is genuine distinct-but-close atoms needing finer encoding. " + s)
    if lift >= 0.01:
        return ("MIDDLE_BAND", "MIDDLE_BAND: de-dup lifts F=3 cleanup +0.01-0.05 -- some mergeable duplicates, but most of the deficit is distinct-but-close atoms (finer ENCODING needed, not just merging). " + s)
    return ("HARD_FAIL", "HARD_FAIL: de-dup lifts <+0.01 -- the deficit is NOT mergeable duplicates but distinct-but-close atoms; the fix is finer ENCODING (populate signature/complexity fields) so close atoms separate, not de-duplication. " + s)


def _selftest():
    rng = np.random.default_rng(1); dim = 128
    M = rng.standard_normal((10, dim)); M = M / np.linalg.norm(M, axis=1, keepdims=True)
    M[1] = M[0] + 1e-6 * rng.standard_normal(dim); M[1] = M[1] / np.linalg.norm(M[1])  # near-duplicate of 0
    kept = _dedup_reps(M, 0.95)
    assert 1 not in kept or 0 not in kept, "near-dup pair should drop one"
    assert abs(float(M[0] @ M[1])) > 0.99
    print("[selftest] PASS: near-duplicate-diagnostic (dedup kept %d/10, dropped the near-dup)" % len(kept), flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
