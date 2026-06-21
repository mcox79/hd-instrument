"""DENSE-KV WHITENING-REVIVAL (GPU) -- the upgrade path: does ISOTROPIZING the learned pythia keys recover the M-indep superposition store?

The dense-KV follow-up showed ARM1 (M-indep superposition) COLLAPSES to chance on raw learned pythia keys (anisotropy: a common-mode
mu swamps the signal -- r = W.cue ~ (mu.cue) * sum(all codes)). Skunkworks's CPU PoC CONFIRMED the fix: mean-center recovers ARM1
(0.806), shrinkage-ZCA recovers slightly better (0.843) -> isotropization removes the common-mode -> ARM1 recovers toward the
isotropic level. This cell tests it on REAL pythia-2.8b keys.

Per Research sequencing (GATE-1 gap ELEVATED to a dependency: a CERT591-faithful projection -> a genuine whitened-ARM1 ceiling):
  - FIX the projection to CERT591-faithful: RANDOM-PERM train/held-out split (the diagnosed GATE-1 gap was my CONTIGUOUS split ->
    train/cal value-number range shift; CERT591 L155 random-permutes) -> GATE-1 meter should now reproduce ~0.827 (validated).
  - Then the whitened-ARM1 test on the validated meter.

Arms @ M={3k,10k} (C=256 codebook decode, M-independent; vs random-ref 0.824):
  ARM1_raw        superposition on raw learned keys           [collapses ~chance -- the baseline]
  ARM1_whitened   superposition on SHRINKAGE-ZCA(keys)        [the revival; bar >=0.80 -> item #3 viable WITH isotropization]
  ARM2_softmax    softmax-attention (O(M*d))                  [holds 1.0 -- comparison]
  ARM0_knn        exact-kNN (O(M*d))                          [exact dict -- comparison]
GATE-1 calibration (validated meter): cue->key recall over CERT591's held-out pool (2500) -> reproduce ~0.827.

WIN: GATE-1 validates (cal~0.827) AND ARM1_whitened >=0.80 (cv<=0.05) @M=10k -> item #3 M-indep store VIABLE on real keys WITH
isotropization = chain-grade-at-bound candidate (4-layer). The ZCA matrix is d x d (M-indep storage; asserted). C1 reuse: probe
funcs VERBATIM (encode fp16 / train_contrastive / recall_at / fit_zca shrinkage / _np_norm) + dense-KV _decode. ASCII; per-seed ckpt.
"""
import sys, os, argparse, time
from pathlib import Path
import numpy as np
import torch   # PROT-020 GPU-gate literal
REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_partial_key, aggregate_partials, write_metrics
import experiments.exp_flagship_sparse_projected_KV_PROBE_whiten_before_topk_v1 as _probe
_probe.ENC_DTYPE = torch.float16 if torch.cuda.is_available() else torch.float32   # CERT591 referent precision (fp16)
from experiments.exp_flagship_sparse_projected_KV_PROBE_whiten_before_topk_v1 import (
    make_facts, encode, train_contrastive, recall_at, _np_norm, fit_zca, apply_zca)
from experiments.exp_dense_projected_KV_envelope_v1 import _decode

ANCHOR_NAME = "dense_KV_whitening_revival_v1_gpu"
PROJ_DIM = 256; C = 256; SIGMA_LK = 0.1; MAX_Q = 2000
CERT591_MEAN, CAL_TOL = 0.827, 0.06; RANDOM_REF_10k = 0.824
ZCA_TAU = 0.05                                               # shrinkage-ZCA relative floor (Skunkworks PoC used the flagship's relative-floor; ~0.05)
_P = argparse.ArgumentParser(); _P.add_argument("--self-test", action="store_true", dest="self_test"); _P.add_argument("--smoke", action="store_true"); _ARGS, _ = _P.parse_known_args()
RUN_MODE = "smoke" if (_ARGS.smoke or _ARGS.self_test) else os.environ.get("HDLAB_RUN_MODE", "full")
if RUN_MODE == "full":
    ENCODER = "EleutherAI/pythia-2.8b"; SEEDS = [7, 17, 23]; M_LK = [3000, 10000]; TRAIN_M = 7500; CAL_POOL = 2500; TRAIN_STEPS = 600
else:
    ENCODER = "EleutherAI/pythia-160m"; SEEDS = [0]; M_LK = [200, 400]; TRAIN_M = 600; CAL_POOL = 100; TRAIN_STEPS = 200
CONFIG_VERSION = "whitening-revival: RANDOM-PERM-split(GATE1-fix) + shrinkage-ZCA(tau=%.2f)-isotropize-keys; proj%d C%d TRAIN_M%d CAL_POOL%d M%s; FP16" % (ZCA_TAU, PROJ_DIM, C, TRAIN_M, CAL_POOL, M_LK)


def _arms(Kp, y, codebook, sigma, seed):
    """ARM1_raw / ARM1_whitened / ARM2_softmax / ARM0_knn. ISOTROPIZE the RAW projected keys Kp (remove common-mode) BEFORE the
    Ramsauer-norm scaling (the PoC order: shrinkage_zca(Kp) then ARM1) -- isotropizing AFTER _np_norm bakes the anisotropy into
    directions + doesn't recover. Shared qidx + noise across raw/whitened for apples-to-apples."""
    g = np.random.default_rng(seed * 911 + len(Kp)); d = Kp.shape[1]; M = len(Kp)
    qidx = np.arange(M) if M <= MAX_Q else np.sort(g.choice(M, MAX_Q, replace=False))
    noise = sigma * g.standard_normal((len(qidx), d)).astype(np.float32)

    def superpos(Kmat):                                     # scale to Ramsauer norm -> superposition W (d x d, M-indep) -> decode over C
        Ks = _np_norm(Kmat) * np.sqrt(d); cue = Ks[qidx] + noise
        W = codebook[y].T @ Ks; assert W.shape == (d, d), "ARM1 W must be d x d (M-indep), got %s" % (W.shape,)
        return float((_decode(cue @ W.T, codebook) == y[qidx]).mean()), Ks, cue

    a1_raw, Ks_raw, cue_raw = superpos(Kp)                  # ARM1 on RAW projected keys (anisotropic -> collapses)
    mu, Wz = fit_zca(Kp, tau=ZCA_TAU); assert Wz.shape == (d, d), "ZCA matrix must be d x d (M-indep storage)"
    a1_white, _, _ = superpos(apply_zca(Kp, mu, Wz))        # ARM1 on ISOTROPIZED projected keys (common-mode removed -> recovers)
    beta = 1.0 / np.sqrt(d); logits = beta * (cue_raw @ Ks_raw.T); logits -= logits.max(axis=1, keepdims=True)
    wts = np.exp(logits); wts /= wts.sum(axis=1, keepdims=True)
    a2 = float((_decode(wts @ codebook[y], codebook) == y[qidx]).mean())
    a0 = float((y[np.argmax(cue_raw @ Ks_raw.T, axis=1)] == y[qidx]).mean())
    return {"arm1_raw": round(a1_raw, 4), "arm1_whitened": round(a1_white, 4), "arm2_softmax": round(a2, 4), "arm0_knn": round(a0, 4)}


def run_unit(seed):
    g = np.random.default_rng(seed)
    n_total = max(M_LK) + TRAIN_M
    keys, cues = make_facts(n_total)
    print("  [seed=%d] encoding %d facts on %s (fp16)..." % (seed, n_total, ENCODER), flush=True)
    K = encode(keys); Q = encode(cues)
    perm = g.permutation(n_total)                           # RANDOM-PERM split (the GATE-1 fix; CERT591 L155) -- no train/cal value-range shift
    tr = perm[:TRAIN_M]; ho = perm[TRAIN_M:]
    print("  [seed=%d] training proj %d (random-perm split, train=%d)..." % (seed, PROJ_DIM, TRAIN_M), flush=True)
    W = train_contrastive(K[tr], Q[tr], PROJ_DIM, TRAIN_STEPS, seed)
    Kp = K[ho] @ W; Qp = Q[ho] @ W
    cal = recall_at(_np_norm(Qp[:CAL_POOL]), _np_norm(Kp[:CAL_POOL]))   # GATE-1 validated meter (random-perm -> ~0.827)
    arms = {}
    for M in M_LK:
        y = g.integers(0, C, M); codebook = _np_norm(g.standard_normal((C, PROJ_DIM)).astype(np.float32))
        arms["M%d" % M] = _arms(Kp[:M], y, codebook, SIGMA_LK, seed)
    print("  [seed=%d] GATE1 cal=%.3f (CERT591 %.3f) | ARM1_raw %s | ARM1_WHITENED %s | ARM2 %s" % (
        seed, cal, CERT591_MEAN, {k: v["arm1_raw"] for k, v in arms.items()}, {k: v["arm1_whitened"] for k, v in arms.items()}, {k: v["arm2_softmax"] for k, v in arms.items()}), flush=True)
    return {"seed": seed, "calibration_recall": round(float(cal), 4), "arms": arms}


def compute_verdict(units):
    if not units:
        return ("HARD_FAIL", "no results", {})
    cal_mean = float(np.mean([u["calibration_recall"] for u in units])); meter_valid = abs(cal_mean - CERT591_MEAN) <= CAL_TOL
    def med(M, a): return float(np.median([u["arms"]["M%d" % M][a] for u in units]))
    def cv(M, a):
        xs = [u["arms"]["M%d" % M][a] for u in units]; return float(np.std(xs) / (abs(np.mean(xs)) + 1e-9))
    raw = {M: med(M, "arm1_raw") for M in M_LK}; white = {M: med(M, "arm1_whitened") for M in M_LK}
    a2 = {M: med(M, "arm2_softmax") for M in M_LK}; a0 = {M: med(M, "arm0_knn") for M in M_LK}
    M10 = 10000 if 10000 in M_LK else max(M_LK)
    white_cv = cv(M10, "arm1_whitened"); white_10 = white[M10]; raw_10 = raw[M10]
    detail = {"calibration_mean": round(cal_mean, 4), "meter_valid": bool(meter_valid), "ZCA_TAU": ZCA_TAU,
              "arm1_raw_by_M": raw, "arm1_whitened_by_M": white, "arm2_softmax_by_M": a2, "arm0_knn_by_M": a0,
              "whitened_recovery_at_M10": round(white_10 - raw_10, 4), "random_ref_10k": RANDOM_REF_10k, "arm1_whitened_cv@M10": round(white_cv, 4),
              "CONFIG_VERSION": CONFIG_VERSION, "cites": ["dense_KV_learned_key_MM", "skunkworks_whitening_revival_cpu_poc", "flagship_shrinkage_zca", "CERT591_kv_learned_projection_v1"]}
    summ = "GATE1 cal=%.3f(valid=%s) | ARM1_raw=%s ARM1_WHITENED=%s (recovery@M10=%+.3f vs raw; random-ref=%.3f) ARM2=%s ARM0=%s | cv@M10=%.3f" % (
        cal_mean, meter_valid, raw, white, white_10 - raw_10, RANDOM_REF_10k, a2, a0, white_cv)
    if not meter_valid:
        return ("MIDDLE_BAND", "MM (meter not validated): GATE-1 cal=%.3f != CERT591 %.3f (+/-%.2f) -- the random-perm-split fix did not fully reproduce the referent; the whitened-ARM1 magnitude is not meter-anchored (report, don't chain-grade). " % (cal_mean, CERT591_MEAN, CAL_TOL) + summ, detail)
    if white_cv > 0.05 and len(units) >= 2:
        return ("MIDDLE_BAND", "MIDDLE_BAND: ARM1_whitened seed-unstable (cv>0.05). " + summ, detail)
    if white_10 >= 0.80:
        return ("HARD_PASS", "CHAIN-GRADE-AT-BOUND CANDIDATE: meter validated (cal=%.3f~CERT591) AND ARM1_WHITENED recovers to %.3f >=0.80 @M=10k (from raw %.3f chance) -> ISOTROPIZATION rescues the M-indep superposition store on REAL learned keys -> item #3 viable WITH whitening. " % (cal_mean, white_10, raw_10) + summ, detail)
    if white_10 >= raw_10 + 0.30:
        return ("MIDDLE_BAND", "MIDDLE_BAND (partial recovery): whitening recovers ARM1 substantially (%.3f from raw %.3f) but < 0.80 @M=10k -> isotropization helps but doesn't fully rescue at this M; honest partial. " % (white_10, raw_10) + summ, detail)
    return ("HARD_FAIL", "HARD_FAIL: whitening does NOT recover ARM1 @M=10k (whitened %.3f ~ raw %.3f) -> isotropization does not rescue the M-indep store on real keys (contra the synthetic PoC -> investigate real-vs-synthetic anisotropy). " % (white_10, raw_10) + summ, detail)


def _selftest():
    g = np.random.default_rng(0); d = 256; M = 3072        # alpha = M/d ~ 12 (the M-indep capacity regime ~13 where isotropic ARM1 holds;
    # past it [alpha>>13] even isotropic crowds -> recovery not visible. The REAL store needs d s.t. M/d<=~13 -- a design question surfaced separately.)
    sig = g.standard_normal((M, d)).astype(np.float32); mu = g.standard_normal((1, d)).astype(np.float32) * 3.0
    Kp = sig + mu                                           # common-mode anisotropy (reproduces the PoC mechanism)
    y = g.integers(0, C, M); cb = _np_norm(g.standard_normal((C, d)).astype(np.float32))
    r = _arms(Kp, y, cb, 0.1, 1)
    assert r["arm1_whitened"] > r["arm1_raw"] + 0.2, "whitening must recover ARM1 vs raw on anisotropic keys at alpha~12 (white=%.2f raw=%.2f)" % (r["arm1_whitened"], r["arm1_raw"])
    iso = g.standard_normal((64, d)).astype(np.float32); yi = g.integers(0, C, 64)
    ri = _arms(iso, yi, cb, 0.0, 2); assert ri["arm1_raw"] > 0.9 and ri["arm1_whitened"] > 0.9, "isotropic tiny-M both ~1.0"
    print("[selftest] PASS: whitening recovers anisotropic ARM1 @alpha~12 (white=%.2f > raw=%.2f) + ZCA d x d (M-indep) + isotropic-tiny-M ~1.0" % (r["arm1_whitened"], r["arm1_raw"]), flush=True)


if __name__ == "__main__":
    _selftest()
    if _ARGS.self_test:
        raise SystemExit(0)
    print("[config] %s mode=%s ENCODER=%s proj=%d C=%d TRAIN_M=%d CAL_POOL=%d M_LK=%s tau=%.2f seeds=%s | %s" % (
        ANCHOR_NAME, RUN_MODE, ENCODER, PROJ_DIM, C, TRAIN_M, CAL_POOL, M_LK, ZCA_TAU, SEEDS, CONFIG_VERSION), flush=True)
    out_dir = get_output_dir(ANCHOR_NAME); run_cfg = {"run_mode": RUN_MODE, "proj": PROJ_DIM, "tau": ZCA_TAU, "TRAIN_M": TRAIN_M, "schema": "whitening-revival-randperm"}; t0 = time.time()
    for seed in SEEDS:
        key = "s%d" % seed
        if key in aggregate_partials(out_dir, [key], run_config=run_cfg):
            print("[ckpt] %s done; skip" % key, flush=True); continue
        write_partial_key(out_dir, key, run_unit(seed))
    units = list(aggregate_partials(out_dir, ["s%d" % sd for sd in SEEDS], run_config=run_cfg).values())
    verdict, msg, detail = compute_verdict(units)
    print("\n[VERDICT] " + msg, flush=True)
    metrics = {"anchor_name": ANCHOR_NAME, "verdict": verdict, "verdict_msg": msg, "run_mode": RUN_MODE, "model": ENCODER, "proj_dim": PROJ_DIM,
               "C": C, "M_LK": M_LK, "ZCA_TAU": ZCA_TAU, "n_seeds": len(SEEDS), "detail": detail,
               "metrics_source": "measured_gpu_dense_kv_whitening_revival", "per_unit": units, "elapsed_s": time.time() - t0}
    write_metrics(out_dir, metrics, units)
    print("[metrics] written to %s" % (out_dir / "metrics.json"), flush=True)
