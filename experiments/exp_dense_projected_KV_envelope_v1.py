"""DENSE-projected-KV ENVELOPE -- the storage-pivot validation (revival of the flagship honest-negative; Research drill + Skunkworks SCHEMA-VET pin).

The flagship L-build showed capacity-via-SPARSIFICATION fails. This asks the storage-RULE question on DENSE keys: does an
M-INDEPENDENT superposition store (ARM1) hold value-recall at scale, or must we keep all keys (ARM0 kNN / ARM2 softmax-attention,
both O(M*d) dict-equivalents)? Win-axis: a genuine SUBSTRATE storage win = ARM1 (O(d^2), M-indep) holds recall>=0.80 at M>=10k.

Skunkworks SCHEMA-VET pins (the design that makes the win-axis coherent):
  A2 FIXED CODEBOOK size C (=256): "M distinct arbitrary values M-independently" is info-theoretically IMPOSSIBLE (needs O(M*d)).
     So each fact = (random key k_i, label y_i in {0..C-1}); values = a FIXED vocab/codebook (the substrate-vocab/LM-head model).
     Decode (ALL arms, M-indep): argmax cosine(readout, C-codebook) == y_i. chance = 1/C = 0.004, so 0.80 is well above chance.
  A1 RANDOM i.i.d. keys CORE across the full M-grid: they ARE the RMT control + the capacity UPPER-BOUND (learned keys have
     DECREASED capacity per HMM arXiv:2503.09518) + need ZERO encoding (resolves cost). If superposition fails on best-case
     random keys it definitively fails on learned. (CERT591 pythia calibration-anchor + learned-key subset = GPU follow-up, flagged.)
  A3 ARM1 superposition W=sum code[y_i] k_i^T (O(d^2)); ARM2 softmax beta=1/sqrt(d) THEORY-FIXED (not tuned); ARM0 exact-kNN.
     cv<=0.05 gate. WIN-AXIS: chain-grade IFF ARM1 recall>=0.80 @ M>=10k (cv<=0.05); [0.50,0.80)->MIDDLE_BAND; <0.50@10k->HARD_FAIL.
     ARM0/ARM2 holding at O(M*d) is NOT a substrate-storage win (dict-equivalent) -- it's the baseline the M-indep store must match.

honest_scope: claim = "recall the value-CLASS from a fixed C-codebook at M-INDEPENDENT storage" (vocab model), NOT "M distinct
arbitrary values M-independently" (impossible; that's an O(M) theorem, not an arm). Query-sampled recall (O(M*d) arms at M=100k
are hours full). ASCII; per-(M,d,sigma) checkpoint... per-seed-unit checkpoint.
"""
import sys, os, argparse, time
from pathlib import Path
import numpy as np
REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_partial_key, aggregate_partials, write_metrics

ANCHOR_NAME = "dense_projected_KV_envelope_v1"
C = 256                                                       # fixed codebook size (vocab); chance recall = 1/C
MAX_Q = 2000                                                  # query-sample for O(M*d) arms (M=100k full is hours)
_P = argparse.ArgumentParser(); _P.add_argument("--self-test", action="store_true", dest="self_test"); _P.add_argument("--smoke", action="store_true"); _ARGS, _ = _P.parse_known_args()
RUN_MODE = "smoke" if (_ARGS.smoke or _ARGS.self_test) else os.environ.get("HDLAB_RUN_MODE", "full")
if RUN_MODE == "full":
    SEEDS = [1, 2, 3, 4, 5]; M_GRID = [1000, 3000, 10000, 30000, 100000]; D_GRID = [768, 1024]; SIGMAS = [0.0, 0.1, 0.3]
else:
    SEEDS = [1]; M_GRID = [200, 1000]; D_GRID = [768]; SIGMAS = [0.0, 0.1]
WIN_M = 10000                                                 # win-axis evaluated at M >= this
CONFIG_VERSION = "fixed-C%d-codebook + random-iid-keys-core + 3arm(ARM0-kNN/ARM1-superpos-Mindep/ARM2-softmax-beta1oversqrtd) + query-sampled + win-axis-ARM1@M>=%d" % (C, WIN_M)


def _norm(X):
    return (X / (np.linalg.norm(X, axis=-1, keepdims=True) + 1e-8)).astype(np.float32)


def _decode(R, codebook):                                    # M-indep decode: argmax cosine(readout, C-codebook) -> predicted label
    return np.argmax(_norm(R) @ codebook.T, axis=1)


def run_config(M, d, sigma, seed):
    g = np.random.default_rng(seed * 100003 + M * 31 + d * 7 + int(sigma * 1000))
    # UNNORMALIZED gaussian keys (entry ~N(0,1), norm ~sqrt(d)): this is the Ramsauer scale where beta=1/sqrt(d) peaks the ARM2
    # softmax (normalized keys make the logits ~O(1/sqrt(d)) -> flat -> chance). Random i.i.d. = RMT control + capacity upper-bound.
    K = g.standard_normal((M, d)).astype(np.float32)
    y = g.integers(0, C, M)                                   # labels into the fixed codebook
    codebook = _norm(g.standard_normal((C, d)).astype(np.float32))   # codebook normalized (decode is cosine over it)
    qidx = np.arange(M) if M <= MAX_Q else np.sort(g.choice(M, MAX_Q, replace=False))   # query-sample (recall is a query-average)
    cue = K[qidx] + sigma * g.standard_normal((len(qidx), d)).astype(np.float32)   # noisy key cue (sigma rel. to unit-variance entries)
    ytrue = y[qidx]
    # ARM0 exact-kNN (O(M*d) dict-equivalent baseline): nearest key -> its label
    a0 = float((y[np.argmax(cue @ K.T, axis=1)] == ytrue).mean())
    # ARM1 SUPERPOSITION (M-INDEPENDENT store, O(d^2)): W = sum_i code[y_i] k_i^T ; readout r = cue @ W.T ; decode over C
    W = codebook[y].T @ K                                     # (d_code=d, d_key=d) -- size O(d^2), INDEPENDENT of M
    a1 = float((_decode(cue @ W.T, codebook) == ytrue).mean())
    # ARM2 softmax-attention 1-step (O(M*d)): weights = softmax(beta * K@cue); r = weights @ code[y]; decode over C
    beta = 1.0 / np.sqrt(d)
    logits = beta * (cue @ K.T)                              # (q, M)
    logits -= logits.max(axis=1, keepdims=True); wts = np.exp(logits); wts /= wts.sum(axis=1, keepdims=True)
    a2 = float((_decode(wts @ codebook[y], codebook) == ytrue).mean())
    return {"M": M, "d": d, "sigma": sigma, "arm0_knn": round(a0, 4), "arm1_superpos_Mindep": round(a1, 4), "arm2_softmax": round(a2, 4)}


def run_unit(seed):
    cfgs = {}
    for d in D_GRID:
        for sigma in SIGMAS:
            for M in M_GRID:
                r = run_config(M, d, sigma, seed)
                cfgs["d%d_s%.1f_M%d" % (d, sigma, M)] = r
    # print the win-axis config(s): largest M, sigma=0.1 (or 0.0), d=768
    sig = 0.1 if 0.1 in SIGMAS else SIGMAS[0]
    for M in [m for m in M_GRID if m >= WIN_M] or [max(M_GRID)]:
        k = "d768_s%.1f_M%d" % (sig, M)
        if k in cfgs:
            print("  [seed=%d %s] ARM0_kNN=%.3f ARM1_superpos=%.3f ARM2_softmax=%.3f" % (seed, k, cfgs[k]["arm0_knn"], cfgs[k]["arm1_superpos_Mindep"], cfgs[k]["arm2_softmax"]), flush=True)
    return {"seed": seed, "cfgs": cfgs}


def compute_verdict(units):
    if not units:
        return ("HARD_FAIL", "no results", {})
    # win-axis cell: d=768, sigma=0.1 (realistic noisy cue), M >= WIN_M. Use the SMALLEST M >= WIN_M present.
    sig = 0.1 if 0.1 in SIGMAS else SIGMAS[0]
    win_Ms = [m for m in M_GRID if m >= WIN_M] or [max(M_GRID)]; win_M = min(win_Ms)
    wk = "d768_s%.1f_M%d" % (sig, win_M)
    def med(arm, key): return float(np.median([u["cfgs"][key][arm] for u in units]))
    def cv(arm, key):
        xs = [u["cfgs"][key][arm] for u in units]; return float(np.std(xs) / (abs(np.mean(xs)) + 1e-9))
    a1 = med("arm1_superpos_Mindep", wk); a0 = med("arm0_knn", wk); a2 = med("arm2_softmax", wk)
    a1_cv = cv("arm1_superpos_Mindep", wk)
    # full curve for ARM1 (the M-indep store) across M at d=768 sigma=0.1
    curve = {("M%d" % m): med("arm1_superpos_Mindep", "d768_s%.1f_M%d" % (sig, m)) for m in M_GRID}
    detail = {"win_config": wk, "C": C, "arm1_superpos@win": round(a1, 4), "arm0_knn@win": round(a0, 4), "arm2_softmax@win": round(a2, 4),
              "arm1_cv@win": round(a1_cv, 4), "arm1_superpos_curve_d768_s%.1f" % sig: curve,
              "all_cfgs_median": {k: {a: round(float(np.median([u["cfgs"][k][a] for u in units])), 4) for a in ["arm0_knn", "arm1_superpos_Mindep", "arm2_softmax"]} for k in units[0]["cfgs"]},
              "CONFIG_VERSION": CONFIG_VERSION, "honest_scope": "value-CLASS recall from a fixed C=%d codebook at M-INDEPENDENT storage (vocab model); NOT M distinct arbitrary values (O(M) theorem)." % C,
              "cites": ["flagship_LBUILD_honest_negative_c13268e2", "CERT591_kv_learned_projection_v1", "RMT_crosstalk_AGS", "modern_hopfield_Ramsauer2020"]}
    summ = "win=%s(d768,sig%.1f,M>=%d) | ARM1_superpos(M-indep)=%.3f cv=%.3f | ARM0_kNN=%.3f ARM2_softmax=%.3f (both O(M*d) baselines) | ARM1_curve=%s" % (
        wk, sig, win_M, a1, a1_cv, a0, a2, curve)
    rescue = " [ARM2-softmax %.3f and/or ARM0-kNN %.3f hold at O(M*d) -> the STORAGE-RULE (superposition) is the bottleneck; pivot to attention-retrieval = storage-chain item #4]" % (a2, a0) if (a2 >= 0.80 or a0 >= 0.80) else ""
    if a1_cv > 0.05 and len(units) >= 2:
        return ("MIDDLE_BAND", "MIDDLE_BAND: ARM1 seed-unstable (cv>0.05) at win-M. " + summ, detail)
    if a1 >= 0.80:
        return ("HARD_PASS", "HARD_PASS (CHAIN-GRADE): the M-INDEPENDENT superposition store (ARM1, O(d^2)) holds recall>=0.80 at M>=%d -> genuine substrate KV storage at scale (not a dict). " % win_M + summ, detail)
    if a1 >= 0.50:
        return ("MIDDLE_BAND", "MIDDLE_BAND: ARM1 M-indep store in [0.50,0.80) at M>=%d -> partial; superposition degrades with crowding (RMT Phi(1/sqrt(alpha)))." % win_M + rescue + " " + summ, detail)
    return ("HARD_FAIL", "HARD_FAIL: ARM1 M-indep superposition < 0.50 at M>=%d -> superposition storage does NOT hold at scale even on best-case random keys -> capacity-via-superposition fails (consistent w/ the flagship honest-negative)." % win_M + rescue + " " + summ, detail)


def _selftest():
    # meter-check (synthetic, no encoder): at tiny M (well under capacity) + sigma=0, ALL arms recall ~1.0 -> decode meter works.
    r = run_config(64, 128, 0.0, 1)
    assert r["arm0_knn"] > 0.95 and r["arm1_superpos_Mindep"] > 0.95 and r["arm2_softmax"] > 0.95, "meter-check: tiny-M sigma0 all arms ~1.0, got %s" % r
    # M-independence of ARM1 storage: W is d x d regardless of M
    g = np.random.default_rng(0); d = 64; K = _norm(g.standard_normal((5000, d)).astype(np.float32)); y = g.integers(0, C, 5000); cb = _norm(g.standard_normal((C, d)).astype(np.float32))
    W = cb[y].T @ K; assert W.shape == (d, d), "ARM1 W is d x d (M-independent), got %s" % (W.shape,)
    # capacity direction: ARM1 recall DROPS as M grows (crowding) -- the win-axis is non-trivial
    lo = run_config(200, 128, 0.1, 2)["arm1_superpos_Mindep"]; hi = run_config(8000, 128, 0.1, 2)["arm1_superpos_Mindep"]
    assert lo >= hi - 1e-6, "ARM1 superposition recall drops with M (crowding): M200=%.2f >= M8000=%.2f" % (lo, hi)
    print("[selftest] PASS: decode-meter (tiny-M all-arms~1.0) + ARM1 W d x d (M-indep) + crowding (M200 %.2f >= M8000 %.2f)" % (lo, hi), flush=True)


if __name__ == "__main__":
    _selftest()
    if _ARGS.self_test:
        raise SystemExit(0)
    print("[config] %s mode=%s C=%d M_GRID=%s D_GRID=%s SIGMAS=%s seeds=%s win@M>=%d | %s" % (ANCHOR_NAME, RUN_MODE, C, M_GRID, D_GRID, SIGMAS, SEEDS, WIN_M, CONFIG_VERSION), flush=True)
    out_dir = get_output_dir(ANCHOR_NAME); run_config_meta = {"run_mode": RUN_MODE, "C": C, "schema": "3arm-Ccodebook-randomcore-winaxis"}; t0 = time.time()
    for seed in SEEDS:
        key = "s%d" % seed
        if key in aggregate_partials(out_dir, [key], run_config=run_config_meta):
            print("[ckpt] %s done; skip" % key, flush=True); continue
        write_partial_key(out_dir, key, run_unit(seed))
    units = list(aggregate_partials(out_dir, ["s%d" % sd for sd in SEEDS], run_config=run_config_meta).values())
    verdict, msg, detail = compute_verdict(units)
    print("\n[VERDICT] " + msg, flush=True)
    metrics = {"anchor_name": ANCHOR_NAME, "verdict": verdict, "verdict_msg": msg, "run_mode": RUN_MODE, "C": C, "M_GRID": M_GRID, "D_GRID": D_GRID, "SIGMAS": SIGMAS,
               "n_seeds": len(SEEDS), "detail": detail, "metrics_source": "measured_cpu_dense_kv_envelope_3arm_Ccodebook", "per_unit": units, "elapsed_s": time.time() - t0}
    write_metrics(out_dir, metrics, units)
    print("[metrics] written to %s" % (out_dir / "metrics.json"), flush=True)
