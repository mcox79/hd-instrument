"""
exp_substrate_composition_capacity_gpu_v1.py -- Cell A: COMPOSITION benchmark (HRR bind/unbind capacity on the 280-atom corpus).

ROUTING: research_to_exp_dev_testbed_5_NEW_CELLS... Cell A (USER-approved "all of them"). Substrate-quality-first; NO LLM frame.
  Demonstrates substrate > atom-set: atoms COMPOSE into structured representations and decompose back. Uses the substrate's
  CANONICAL primitives (hdlab.binding.bind/unbind circular-convolution HRR + hdlab.bundling.bundle) over the substrate's REAL
  280-atom algebra-encoded vectors (AlgebraIndex.algebra_hrr) as the item codebook -- not random vectors.

  Classic Plate-1995 capacity experiment, substrate-grounded:
    A_bound = bundle( bind(R_1,B_1), ..., bind(R_N,B_N) )   (N simultaneous role-filler bindings, normalized)
    recover B_j ~= unbind(A_bound, R_j) -> cleanup over the 280-atom codebook
  Roles R_i are UNITARY HRR vectors (unit-magnitude FFT spectrum) so unbind is an exact inverse in the noiseless single-binding
  limit; crosstalk grows with N. Sweep N_bindings in {1,2,5,10,20}; report mean recovery COSINE (primary) + cleanup acc@{1,3,5}.

PRE-REGISTERED (per routing; thresholds may be refined by the in-flight VSA drill):
  HARD-PASS: mean recovery cosine >= 0.80 at N_bindings=5 AND a capacity boundary (cosine crosses 0.5) is identified in the sweep.
  MIDDLE: recovery cosine 0.50-0.80 at N=5. HARD-FAIL: < 0.50 at N=5 (capacity collapsed at small N). UNKNOWN if corpus load fails.
ASCII-only. torch (light-GPU). --self-test + --smoke + metrics.json. Route via overnight_queue (GPU) or local_cpu_queue.
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
try:
    import torch  # PROT-020 GPU cell; HRR ops + codebook cleanup run on CUDA when available.
    _DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
except Exception:
    _DEVICE = "cpu"
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "substrate_composition_capacity_gpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
N_SWEEP = [1, 2, 3, 5, 10, 20]   # VSA drill lock: include F=3 (HARD-PASS bar) + capacity F* check at 10
N_TRIALS = 20                     # per seed
SEEDS = [7, 8, 9]                 # 3 seeds per locked protocol


def _unitary_roles(n_roles, dim, gen):
    """n_roles real UNITARY HRR vectors (unit-magnitude FFT spectrum) -> exact circular-convolution inverse."""
    v = torch.randn(n_roles, dim, generator=gen)
    fv = torch.fft.fft(v)
    fv = fv / (fv.abs() + 1e-12)          # force all spectral magnitudes to 1 (unitary)
    return torch.fft.ifft(fv).real.contiguous()


def _load_atom_codebook():
    """280 real algebra_hrr atom vectors (1024-d, L2-normed) from the substrate corpus -> (M, dim) torch."""
    from backend.substrate_index.partition import PartitionedStore
    from backend.substrate_index.algebra_index import AlgebraIndex
    import numpy as np
    ps = PartitionedStore(REPO / "data" / "substrate_index")
    ai = AlgebraIndex(dim=1024); ai.build(ps)
    ids, rows = [], []
    for aid, av in ai._atom_vectors.items():
        if av.algebra_hrr is not None:
            ids.append(aid); rows.append(av.algebra_hrr)
    if not rows:
        return None, None
    M = torch.tensor(np.stack(rows), dtype=torch.float32)
    M = M / (M.norm(dim=1, keepdim=True) + 1e-12)
    return ids, M


def _sweep_codebook(M, sweep, seeds, n_trials):
    """Run the bind/bundle/unbind/cleanup capacity sweep against codebook M (Mn, dim). Returns curve + cleanup F*."""
    from hdlab.binding import bind, unbind
    from hdlab.bundling import bundle
    Mn = M.shape[0]; dim = M.shape[1]; Mt = M.t().contiguous()
    curve = []
    for N in sweep:
        if N > Mn:
            continue
        seed_cos = []; hit1 = hit3 = hit5 = 0; cnt = 0
        for sd in seeds:
            gen = torch.Generator().manual_seed(sd * 1000 + N)
            cs = 0.0; cc = 0
            for _t in range(n_trials):
                idx = torch.randperm(Mn, generator=gen)[:N]
                B = M[idx]
                R = _unitary_roles(N, dim, gen).to(M.device)
                bound = torch.stack([bind(R[i], B[i]) for i in range(N)])
                A_bound = bundle(bound)
                for j in range(N):
                    est = unbind(A_bound, R[j]); est = est / (est.norm() + 1e-12)
                    true = B[j]
                    cs += float(torch.dot(est, true / (true.norm() + 1e-12))); cc += 1
                    sims = est @ Mt; order = torch.argsort(sims, descending=True)
                    gold = int(idx[j]); top = order[:5].tolist()
                    hit1 += int(gold == top[0]); hit3 += int(gold in top[:3]); hit5 += int(gold in top[:5]); cnt += 1
            seed_cos.append(cs / cc)
        cmean = sum(seed_cos) / len(seed_cos)
        csd = (sum((x - cmean) ** 2 for x in seed_cos) / len(seed_cos)) ** 0.5
        curve.append({"N_bindings": N, "recovery_cosine": round(cmean, 4), "recovery_cosine_sd": round(csd, 4),
                      "cleanup_acc1": round(hit1 / cnt, 4), "cleanup_acc3": round(hit3 / cnt, 4), "cleanup_acc5": round(hit5 / cnt, 4)})
    f_star_clean = None
    for c in curve:
        if c["cleanup_acc1"] >= 0.80: f_star_clean = c["N_bindings"]
    return curve, f_star_clean


def run() -> Dict:
    ids, M = _load_atom_codebook()
    if M is None:
        return {"error": "no_algebra_atoms"}
    M = M.to(_DEVICE)
    dim = M.shape[1]; Mn = M.shape[0]
    n_trials = 6 if SMOKE else N_TRIALS
    seeds = SEEDS[:1] if SMOKE else SEEDS
    sweep = [1, 2, 3] if SMOKE else N_SWEEP
    # RANDOM codebook baseline (Research revised lock): uniform-on-sphere, same (Mn, dim) -> isolates clustered-codebook effect.
    rg = torch.Generator().manual_seed(12345)
    R0 = torch.randn(Mn, dim, generator=rg); R0 = (R0 / (R0.norm(dim=1, keepdim=True) + 1e-12)).to(_DEVICE)
    sub_curve, sub_fstar = _sweep_codebook(M, sweep, seeds, n_trials)
    rnd_curve, rnd_fstar = _sweep_codebook(R0, sweep, seeds, n_trials)
    rnd_by = {c["N_bindings"]: c for c in rnd_curve}
    for c in sub_curve:
        rc = rnd_by.get(c["N_bindings"], {})
        print("  F=%2d cos=%.4f | cleanup@1 substrate=%.4f random=%.4f (clustered-vs-uniform delta=%+.4f)"
              % (c["N_bindings"], c["recovery_cosine"], c["cleanup_acc1"], rc.get("cleanup_acc1", 0.0),
                 c["cleanup_acc1"] - rc.get("cleanup_acc1", 0.0)), flush=True)
    return {"curve": sub_curve, "random_baseline_curve": rnd_curve, "n_atoms": Mn, "dim": dim,
            "capacity_F_star_cleanup0.80": sub_fstar, "random_capacity_F_star_cleanup0.80": rnd_fstar,
            "device": _DEVICE, "n_trials": n_trials, "n_seeds": len(seeds)}


def verdict(r) -> Tuple[str, str]:
    if r.get("error"): return ("UNKNOWN", "UNKNOWN: " + r["error"])
    by = {c["N_bindings"]: c for c in r["curve"]}
    rby = {c["N_bindings"]: c for c in r.get("random_baseline_curve", [])}
    a3 = by.get(3, {}).get("cleanup_acc1")              # REVISED LOCK metric: cleanup accuracy at F=3
    f_star = r.get("capacity_F_star_cleanup0.80")
    a3_rand = rby.get(3, {}).get("cleanup_acc1")
    rnd_fstar = r.get("random_capacity_F_star_cleanup0.80")
    delta3 = (a3 - a3_rand) if (a3 is not None and a3_rand is not None) else None
    geom = ("clustered HURTS ceiling (intra-cluster near-collisions)" if (delta3 is not None and delta3 < -0.03)
            else "clustered HELPS (clusters discriminate)" if (delta3 is not None and delta3 > 0.03)
            else "clustered ~= uniform")
    s = ("cleanup@1_F3 substrate=%s random=%s (delta=%s -> %s); cleanup capacity F* substrate=%s random=%s; recovery_cos=1/sqrt(F) analytic; curve(F,cleanup_sub,cleanup_rnd)=%s; corpus=%d dim=%d device=%s"
         % (a3, a3_rand, (round(delta3, 4) if delta3 is not None else None), geom, f_star, rnd_fstar,
            [(c["N_bindings"], c["cleanup_acc1"], rby.get(c["N_bindings"], {}).get("cleanup_acc1")) for c in r["curve"]],
            r["n_atoms"], r["dim"], r["device"]))
    if a3 is None:
        return ("UNKNOWN", "UNKNOWN: F=3 not in sweep. " + s)
    if a3 >= 0.95 and (f_star is not None and f_star >= 10):
        return ("HARD_PASS", "HARD_PASS (revised lock, cleanup accuracy): substrate composes + decodes >=0.95 cleanup@1 at F=3 with capacity F*>=10 -- atoms compose into recoverable structured representations (substrate > atom-set). " + s)
    if a3 >= 0.50:
        return ("MIDDLE_BAND", "MIDDLE_BAND (revised lock): cleanup@1 0.50-0.95 at F=3. Capacity F*=%s (no Frady-Sommer cliff if F* high) but ceiling capped below 0.95 -- see substrate-vs-random delta for whether the clustered codebook caps the ceiling. " % f_star + s)
    return ("HARD_FAIL", "HARD_FAIL (revised lock): cleanup@1 <0.50 at F=3 -- composed states do not decode at small F. " + s)


def _selftest():
    import numpy as np
    g = torch.Generator().manual_seed(1)
    R = _unitary_roles(3, 256, g)
    assert R.shape == (3, 256)
    # unitary role: |FFT| approx 1 everywhere
    mag = torch.fft.fft(R[0]).abs()
    assert float((mag - 1.0).abs().max()) < 1e-4, float((mag - 1.0).abs().max())
    # single-binding exact recovery: unbind(bind(R,B),R) ~= B
    from hdlab.binding import bind, unbind
    B = torch.randn(256, generator=g); B = B / B.norm()
    rec = unbind(bind(R[0], B), R[0]); rec = rec / rec.norm()
    assert float(torch.dot(rec, B)) > 0.99, float(torch.dot(rec, B))
    print("[selftest] PASS: composition-capacity (unitary roles + exact single-binding recovery cos=%.4f)" % float(torch.dot(rec, B)), flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s device=%s" % (ANCHOR_NAME, RUN_MODE, _DEVICE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
