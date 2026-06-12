"""
exp_substrate_csls_cleanup_recovery_gpu_v1.py -- follow-on to Cell A/B: does CSLS hubness-corrected cleanup recover the
  clustered-codebook decode deficit? -- light-GPU.

ROUTING: indicated mitigation from Cell A+B verdict (clustered codebook caps cleanup at 0.84-0.93 vs uniform=1.0; Research
  revised-lock note named CSLS/MMR cleanup re-rank per the distractor-density drill). Substrate-quality-first; NO LLM frame.

  Cell A found: composition/decode has NO capacity cliff (uniform codebook = 1.0 cleanup to F=20), but the substrate's
  CLUSTERED codebook (tw_edge_z=-2.26) caps cleanup at ~0.89 at F=3 (-0.11 vs uniform). CSLS (Lample 2018, cross-domain
  similarity local scaling) penalizes HUB atoms (those in dense codebook regions): score(est,c) = 2*cos(est,c) - r_k(c),
  r_k(c) = mean cosine of c to its k nearest OTHER codebook atoms. r(est) is constant across c for argmax -> omitted. If the
  clustered-codebook deficit is HUBNESS (dense regions stealing the argmax), CSLS recovers it; if it is genuine semantic
  near-duplicates, CSLS cannot.

  Same composition setup as Cell A (bundle(bind(R_i,B_i)) over the 280-atom algebra_hrr corpus, unitary roles). Compare
  STANDARD cleanup (argmax cosine) vs CSLS cleanup, cleanup@1 across F in {1,2,3,5,10,20}, 3 seeds.

PRE-REGISTERED (substrate-property; no LLM frame):
  HARD-PASS: CSLS cleanup@1 >= 0.95 at F=3 (fully recovers to the Cell-A revised HARD-PASS bar) OR CSLS lift >= +0.05 over
    standard at F=3 (substantial hubness recovery).
  MIDDLE: CSLS lift +0.01-0.05 at F=3 (partial recovery). HARD-FAIL: CSLS lift < +0.01 (deficit is genuine near-duplicates,
    not hubness; cleanup re-rank cannot fix it). UNKNOWN if corpus load fails.
ASCII-only. torch (light-GPU). --self-test + --smoke + metrics.json. Route via overnight_queue (GPU).
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
    import torch
    _DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
except Exception:
    _DEVICE = "cpu"
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "substrate_csls_cleanup_recovery_gpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
N_SWEEP = [1, 2, 3, 5, 10, 20]
N_TRIALS = 20
SEEDS = [7, 8, 9]
CSLS_K = 10


def _unitary_roles(n_roles, dim, gen):
    v = torch.randn(n_roles, dim, generator=gen)
    fv = torch.fft.fft(v); fv = fv / (fv.abs() + 1e-12)
    return torch.fft.ifft(fv).real.contiguous()


def _load_atom_codebook():
    from backend.substrate_index.partition import PartitionedStore
    from backend.substrate_index.algebra_index import AlgebraIndex
    import numpy as np
    ps = PartitionedStore(REPO / "data" / "substrate_index")
    ai = AlgebraIndex(dim=1024); ai.build(ps)
    rows = [av.algebra_hrr for av in ai._atom_vectors.values() if av.algebra_hrr is not None]
    if not rows:
        return None
    M = torch.tensor(np.stack(rows), dtype=torch.float32)
    return M / (M.norm(dim=1, keepdim=True) + 1e-12)


def _csls_r(M, k):
    """r_k(c) = mean cosine of each codebook atom to its k nearest OTHER atoms. (Mn,)"""
    G = M @ M.t()                                   # (Mn, Mn) cosine (M unit-normed)
    G.fill_diagonal_(-2.0)                           # exclude self
    topk = torch.topk(G, k, dim=1).values            # (Mn, k)
    return topk.mean(dim=1)                           # (Mn,)


def run() -> Dict:
    from hdlab.binding import bind, unbind
    from hdlab.bundling import bundle
    M = _load_atom_codebook()
    if M is None:
        return {"error": "no_algebra_atoms"}
    M = M.to(_DEVICE); dim = M.shape[1]; Mn = M.shape[0]
    Mt = M.t().contiguous()
    rk = _csls_r(M, min(CSLS_K, Mn - 1))             # (Mn,) hubness term
    n_trials = 6 if SMOKE else N_TRIALS
    seeds = SEEDS[:1] if SMOKE else SEEDS
    sweep = [1, 2, 3] if SMOKE else N_SWEEP
    curve = []
    for N in sweep:
        if N > Mn:
            continue
        std_hit = 0; csls_hit = 0; cnt = 0
        for sd in seeds:
            gen = torch.Generator().manual_seed(sd * 1000 + N)
            for _t in range(n_trials):
                idx = torch.randperm(Mn, generator=gen)[:N]
                B = M[idx]
                R = _unitary_roles(N, dim, gen).to(_DEVICE)
                A_bound = bundle(torch.stack([bind(R[i], B[i]) for i in range(N)]))
                for j in range(N):
                    est = unbind(A_bound, R[j]); est = est / (est.norm() + 1e-12)
                    cos = est @ Mt                                  # (Mn,)
                    gold = int(idx[j])
                    std_hit += int(int(torch.argmax(cos)) == gold)
                    csls = 2.0 * cos - rk                            # CSLS score (r(est) constant -> dropped)
                    csls_hit += int(int(torch.argmax(csls)) == gold)
                    cnt += 1
        std = std_hit / cnt; cs = csls_hit / cnt
        curve.append({"F": N, "cleanup_std": round(std, 4), "cleanup_csls": round(cs, 4), "csls_lift": round(cs - std, 4)})
        print("  F=%2d standard=%.4f CSLS=%.4f lift=%+.4f" % (N, std, cs, cs - std), flush=True)
    return {"curve": curve, "n_atoms": Mn, "dim": dim, "csls_k": min(CSLS_K, Mn - 1), "device": _DEVICE, "n_seeds": len(seeds)}


def verdict(r) -> Tuple[str, str]:
    if r.get("error"): return ("UNKNOWN", "UNKNOWN: " + r["error"])
    by = {c["F"]: c for c in r["curve"]}
    c3 = by.get(3, {})
    cs3 = c3.get("cleanup_csls"); lift3 = c3.get("csls_lift")
    s = ("F3: standard=%s CSLS=%s lift=%s; curve=%s; corpus=%d csls_k=%d device=%s"
         % (c3.get("cleanup_std"), cs3, lift3, [(c["F"], c["cleanup_std"], c["cleanup_csls"], c["csls_lift"]) for c in r["curve"]],
            r["n_atoms"], r["csls_k"], r["device"]))
    if cs3 is None:
        return ("UNKNOWN", "UNKNOWN: F=3 not in sweep. " + s)
    if cs3 >= 0.95 or lift3 >= 0.05:
        return ("HARD_PASS", "HARD_PASS: CSLS hubness-corrected cleanup recovers the clustered-codebook deficit (CSLS@F3>=0.95 or lift>=+0.05) -- the substrate decode ceiling deficit is largely HUBNESS (dense-region atoms stealing argmax), fixable by cleanup re-rank. " + s)
    if lift3 >= 0.01:
        return ("MIDDLE_BAND", "MIDDLE_BAND: CSLS partially recovers (lift +0.01-0.05 at F=3) -- deficit is part hubness, part genuine near-duplicates. " + s)
    return ("HARD_FAIL", "HARD_FAIL: CSLS does not help (lift <+0.01 at F=3) -- the clustered-codebook deficit is genuine semantic near-duplicates, not hubness; cleanup re-rank cannot fix it (mitigation would need atom de-duplication / finer encoding). " + s)


def _selftest():
    g = torch.Generator().manual_seed(1)
    M = torch.randn(20, 64, generator=g); M = M / M.norm(dim=1, keepdim=True)
    rk = _csls_r(M, 5)
    assert rk.shape == (20,) and float(rk.max()) < 1.0
    print("[selftest] PASS: csls-cleanup-recovery (r_k shape %s, max %.3f)" % (tuple(rk.shape), float(rk.max())), flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s device=%s" % (ANCHOR_NAME, RUN_MODE, _DEVICE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
