"""DENSE-KV-envelope LEARNED-KEY + CALIBRATION follow-up (GPU) -- the gate that upgrades the random-core MM to SUBSTRATE chain-grade-at-bound.

Skunkworks landed-VET routed 2 pre-registered gates the random-core couldn't meet (random keys = best-case RMT upper bound; meter
unvalidated on real pythia):
  GATE-1 (FLAG-3 calibration / HALT-gate): reproduce CERT591's cue->key recall on REAL pythia-2.8b proj256 keys @M=10k =>
     target mean ~0.827 / worst ~0.805. Validates the recall meter against the known referent (else HALT, don't interpret).
  GATE-2 (learned-key subset): ARM1 (M-indep superposition) + ARM2 (softmax) on the SAME pythia-projected keys at M={3k,10k}.
     Learned keys have DECREASED capacity vs i.i.d. random (HMM arXiv:2503.09518) -> the SUBSTRATE's actual M-indep bound is
     <= the random-core's 0.824@10k. If ARM1 holds >=0.80 at some M (meter validated) -> upgrade THIS atom to chain-grade-at-bound.

C1 reuse: probe funcs VERBATIM (make_facts/encode[fp16-overridden]/train_contrastive/recall_at/_np_norm) + dense-KV _decode. Same C=256
codebook + ARM1 superposition + ARM2 softmax(beta=1/sqrt(d)) + apples-to-apples scaling (learned keys scaled to Ramsauer norm
~sqrt(d), matching the random-core) + query-sampled. GPU (pythia-2.8b, FP16 = CERT591-referent precision). ASCII; per-seed ckpt.
"""
import sys, os, argparse, time
from pathlib import Path
import numpy as np
import torch   # PROT-020 GPU-gate requires a LITERAL 'import torch' (used transitively via the probe encode); also for the fp16 match below
REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_partial_key, aggregate_partials, write_metrics
import experiments.exp_flagship_sparse_projected_KV_PROBE_whiten_before_topk_v1 as _probe
# Skunkworks PRECISION-FIX (verify-the-referent on the calibration target): CERT591's 0.827 referent was FLOAT16 (its line 117),
# NOT bf16. Match fp16 so GATE-1 reproduces it (else the HALT misfires on a precision artifact + GATE-2 reads bf16-depressed).
# Cheap here (proj256, M<=10k -> no OOM, unlike the L-build's 8192/100k that needed the bf16 OOM-fix). float32 on CPU smoke.
_probe.ENC_DTYPE = torch.float16 if torch.cuda.is_available() else torch.float32
from experiments.exp_flagship_sparse_projected_KV_PROBE_whiten_before_topk_v1 import (
    make_facts, encode, train_contrastive, recall_at, _np_norm)
from experiments.exp_dense_projected_KV_envelope_v1 import _decode

ANCHOR_NAME = "dense_KV_envelope_learned_key_calibration_v1_gpu"
PROJ_DIM = 256                                               # CERT591's proj_dim (the calibration referent)
C = 256; SIGMA_LK = 0.1; MAX_Q = 2000
CERT591_MEAN, CERT591_WORST, CAL_TOL = 0.827, 0.805, 0.06    # GATE-1 reproduce target (+/- tol)
RANDOM_REF_10k = 0.824                                       # random-core ARM1@10k (the best-case upper bound to compare against)
_P = argparse.ArgumentParser(); _P.add_argument("--self-test", action="store_true", dest="self_test"); _P.add_argument("--smoke", action="store_true"); _ARGS, _ = _P.parse_known_args()
RUN_MODE = "smoke" if (_ARGS.smoke or _ARGS.self_test) else os.environ.get("HDLAB_RUN_MODE", "full")
if RUN_MODE == "full":
    ENCODER = "EleutherAI/pythia-2.8b"; SEEDS = [7, 17, 23]; M_CAL = 10000; M_LK = [3000, 10000]; TRAIN_M = 4000; TRAIN_STEPS = 600
else:
    ENCODER = "EleutherAI/pythia-160m"; SEEDS = [0]; M_CAL = 400; M_LK = [200, 400]; TRAIN_M = 300; TRAIN_STEPS = 200
CONFIG_VERSION = "pythia-proj%d + GATE1-calibration(repro CERT591 %.3f) + GATE2-learned-key ARM1/ARM2 @M%s vs random-ref %.3f; C=%d; FP16(CERT591-referent-match, Skunkworks precision-fix)" % (PROJ_DIM, CERT591_MEAN, M_LK, RANDOM_REF_10k, C)


def _arm1_arm2_learned(K_proj, y, codebook, sigma, seed):
    """ARM1 superposition (M-indep O(d^2)) + ARM2 softmax on LEARNED projected keys, scaled to Ramsauer norm ~sqrt(d) (apples-to-apples w/ the random-core)."""
    g = np.random.default_rng(seed * 911 + len(K_proj))
    d = K_proj.shape[1]
    Ks = _np_norm(K_proj) * np.sqrt(d)                       # unit-direction x sqrt(d) norm = Ramsauer scale (matches random gaussian norm)
    M = len(Ks); qidx = np.arange(M) if M <= MAX_Q else np.sort(g.choice(M, MAX_Q, replace=False))
    cue = Ks[qidx] + sigma * g.standard_normal((len(qidx), d)).astype(np.float32)
    ytrue = y[qidx]
    W = codebook[y].T @ Ks                                   # (d,d) M-indep
    a1 = float((_decode(cue @ W.T, codebook) == ytrue).mean())
    beta = 1.0 / np.sqrt(d); logits = beta * (cue @ Ks.T); logits -= logits.max(axis=1, keepdims=True)
    wts = np.exp(logits); wts /= wts.sum(axis=1, keepdims=True)
    a2 = float((_decode(wts @ codebook[y], codebook) == ytrue).mean())
    return round(a1, 4), round(a2, 4)


def run_unit(seed):
    g = np.random.default_rng(seed)
    M_max = max(M_CAL, max(M_LK)); n_total = M_max + TRAIN_M
    keys, cues = make_facts(n_total)
    print("  [seed=%d] encoding %d facts on %s (fp16=CERT591-referent)..." % (seed, n_total, ENCODER), flush=True)
    K = encode(keys); Q = encode(cues)
    Ktr, Qtr = K[:TRAIN_M], Q[:TRAIN_M]; Kho, Qho = K[TRAIN_M:], Q[TRAIN_M:]
    print("  [seed=%d] training CERT591 proj D=%d -> %d..." % (seed, K.shape[1], PROJ_DIM), flush=True)
    W = train_contrastive(Ktr, Qtr, PROJ_DIM, TRAIN_STEPS, seed)
    Kp = Kho @ W; Qp = Qho @ W                              # projected held-out
    # GATE-1 calibration: CERT591 cue->key recall @M_CAL (the meter-check; must reproduce ~0.827)
    cal = recall_at(_np_norm(Qp[:M_CAL]), _np_norm(Kp[:M_CAL]))
    # GATE-2 learned-key ARM1/ARM2 @ M in M_LK (C-codebook, apples-to-apples w/ random-core)
    codebook = _np_norm(g.standard_normal((C, PROJ_DIM)).astype(np.float32))
    lk = {}
    for M in M_LK:
        y = g.integers(0, C, M)
        a1, a2 = _arm1_arm2_learned(Kp[:M], y, codebook, SIGMA_LK, seed)
        lk["M%d" % M] = {"arm1_superpos_learned": a1, "arm2_softmax_learned": a2}
    print("  [seed=%d] GATE1 cal(cue->key @M%d)=%.3f (CERT591 %.3f) | GATE2 ARM1-learned %s" % (
        seed, M_CAL, cal, CERT591_MEAN, {k: v["arm1_superpos_learned"] for k, v in lk.items()}), flush=True)
    return {"seed": seed, "calibration_recall": round(float(cal), 4), "learned_key": lk}


def compute_verdict(units):
    if not units:
        return ("HARD_FAIL", "no results", {})
    cals = [u["calibration_recall"] for u in units]
    cal_mean = float(np.mean(cals)); cal_worst = float(np.min(cals))
    meter_valid = abs(cal_mean - CERT591_MEAN) <= CAL_TOL
    def med(M, arm): return float(np.median([u["learned_key"]["M%d" % M][arm] for u in units]))
    a1 = {M: med(M, "arm1_superpos_learned") for M in M_LK}; a2 = {M: med(M, "arm2_softmax_learned") for M in M_LK}
    best_M = max((M for M in M_LK if a1[M] >= 0.80), default=None)
    detail = {"calibration_mean": round(cal_mean, 4), "calibration_worst": round(cal_worst, 4), "CERT591_target_mean": CERT591_MEAN,
              "meter_valid": bool(meter_valid), "arm1_superpos_learned_by_M": a1, "arm2_softmax_learned_by_M": a2,
              "random_ref_10k": RANDOM_REF_10k, "learned_vs_random_10k": round(a1.get(10000, a1[max(M_LK)]) - RANDOM_REF_10k, 4) if 10000 in a1 else None,
              "best_M_arm1_ge_0.80": best_M, "CONFIG_VERSION": CONFIG_VERSION,
              "cites": ["dense_projected_KV_envelope_v1_random_core_MM", "CERT591_kv_learned_projection_v1", "HMM_decreased_capacity_2503.09518"]}
    summ = "GATE1 cal_mean=%.3f cal_worst=%.3f (CERT591 %.3f/%.3f, meter_valid=%s) | GATE2 ARM1-learned=%s ARM2=%s (random-ref@10k=%.3f) | best_M(ARM1>=0.80)=%s" % (
        cal_mean, cal_worst, CERT591_MEAN, CERT591_WORST, meter_valid, a1, a2, RANDOM_REF_10k, best_M)
    if not meter_valid:
        return ("HARD_FAIL", "HALT (GATE-1 meter-check FAILED): calibration cue->key recall %.3f does NOT reproduce CERT591's %.3f (+/-%.2f) -> the recall meter is not validated on real pythia keys -> do NOT interpret the learned-key arms (meter suspect). " % (cal_mean, CERT591_MEAN, CAL_TOL) + summ, detail)
    if best_M is not None and best_M >= max(M_LK):
        return ("HARD_PASS", "CHAIN-GRADE-AT-BOUND CONFIRMED: meter validated (cal %.3f~CERT591 %.3f) AND ARM1 M-indep superposition holds recall>=0.80 on REAL learned pythia keys at M=%d -> the SUBSTRATE has a genuine M-independent KV store at the ~13xd bound (not just best-case random). " % (cal_mean, CERT591_MEAN, best_M) + summ, detail)
    if best_M is not None:
        return ("MIDDLE_BAND", "chain-grade-at-LOWER-bound: meter validated; ARM1-learned holds >=0.80 at M=%d but NOT at higher M (learned bound < random's best-case, per HMM) -> substrate M-indep store genuine at a LOWER bound than random. " % best_M + summ, detail)
    return ("MIDDLE_BAND", "MM (learned below bar): meter validated but ARM1-learned <0.80 even at M=%d -> learned keys' decreased capacity (HMM) puts the substrate M-indep bound below the 0.80 bar at these M; the random-core 0.824 was the best-case upper bound only. Honest: dense-projected M-indep store does NOT reach the bar on real keys at M>=%d. " % (min(M_LK), min(M_LK)) + summ, detail)


def _selftest():
    # decode + the learned-arm path on synthetic projected-like keys (no model): tiny M -> ARM1/ARM2 ~1.0 (meter sanity)
    g = np.random.default_rng(0); d = 128; M = 64
    Kp = g.standard_normal((M, d)).astype(np.float32); y = g.integers(0, C, M); cb = _np_norm(g.standard_normal((C, d)).astype(np.float32))
    a1, a2 = _arm1_arm2_learned(Kp, y, cb, 0.0, 1)
    assert a1 > 0.95 and a2 > 0.95, "learned-arm decode meter: tiny-M sigma0 ~1.0, got a1=%.2f a2=%.2f" % (a1, a2)
    # crowding: ARM1 drops as M grows on projected-like keys
    Kp2 = g.standard_normal((6000, d)).astype(np.float32); y2 = g.integers(0, C, 6000)
    a1hi, _ = _arm1_arm2_learned(Kp2, y2, cb, 0.1, 1)
    assert a1hi <= a1 + 1e-6, "ARM1 crowds with M (M64 %.2f >= M6000 %.2f)" % (a1, a1hi)
    print("[selftest] PASS: learned-arm decode (tiny-M a1=%.2f a2=%.2f) + crowding (M64 %.2f >= M6000 %.2f) + reuses probe/dense-KV funcs" % (a1, a2, a1, a1hi), flush=True)


if __name__ == "__main__":
    _selftest()
    if _ARGS.self_test:
        raise SystemExit(0)
    print("[config] %s mode=%s ENCODER=%s proj=%d C=%d M_CAL=%d M_LK=%s seeds=%s | %s" % (ANCHOR_NAME, RUN_MODE, ENCODER, PROJ_DIM, C, M_CAL, M_LK, SEEDS, CONFIG_VERSION), flush=True)
    out_dir = get_output_dir(ANCHOR_NAME); run_cfg = {"run_mode": RUN_MODE, "proj": PROJ_DIM, "schema": "gate1-cal+gate2-learned"}; t0 = time.time()
    for seed in SEEDS:
        key = "s%d" % seed
        if key in aggregate_partials(out_dir, [key], run_config=run_cfg):
            print("[ckpt] %s done; skip" % key, flush=True); continue
        write_partial_key(out_dir, key, run_unit(seed))
    units = list(aggregate_partials(out_dir, ["s%d" % sd for sd in SEEDS], run_config=run_cfg).values())
    verdict, msg, detail = compute_verdict(units)
    print("\n[VERDICT] " + msg, flush=True)
    metrics = {"anchor_name": ANCHOR_NAME, "verdict": verdict, "verdict_msg": msg, "run_mode": RUN_MODE, "model": ENCODER, "proj_dim": PROJ_DIM,
               "C": C, "M_CAL": M_CAL, "M_LK": M_LK, "n_seeds": len(SEEDS), "detail": detail,
               "metrics_source": "measured_gpu_dense_kv_learned_key_calibration", "per_unit": units, "elapsed_s": time.time() - t0}
    write_metrics(out_dir, metrics, units)
    print("[metrics] written to %s" % (out_dir / "metrics.json"), flush=True)
