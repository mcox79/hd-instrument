"""FLAGSHIP sparse-projected-KV L-BUILD (cell 2 of 2) -- the chain-grade-vs-MM test on the probe-confirmed sparse-encode.

Gated on the PROBE (cell 1) HARD_PASS, which picks the variant (B shrinkage-ZCA whiten-before-topk, or C random-fixed) + the
healthy f. This cell measures the 4-arm capacity scan that decides whether projection+sparsification COMPOSES into genuine
super-capacity KV (Arm1 beats the ablations AND scales) or is honest-MM.

4 arms (per Research flagship prestage cell-2 + Skunkworks build-cleared checklist), all on the SAME held-out eval facts:
  Arm 1 FULL            : learned-projection -> (variant transform) -> top-k sparsify       [the composition under test]
  Arm 2 no-projection   : sparsify the RAW pythia keys (no learned projection)              [sparse alone insufficient?]
  Arm 3 no-sparsification: DENSE projected keys (CERT591 raw, no sparsify)                  [dense holds recall but limits M]
  Arm 4 no-learned-proj : ANALYTIC (random-gaussian) projection -> sparsify                 [learned >> analytic per CERT591]
Capacity M-scan {1k,10k,100k}: recall vs load -> capacity_M = max M with recall>=0.95. Sparse super-capacity => Arm1 capacity >> Arm3.

HARD_PASS (prestage): Arm1 recall>=0.60 at M=5000-equiv + cv<=0.05 (3 seeds) + Arm1 > Arm2 by >=0.20 + Arm1 capacity_M >= 2x Arm3.
HARD_FAIL: Arm1 recall<0.40 OR Arm1 capacity_M < Arm3 (sparse adds no scale). MM: Arm1 recall in [0.40,0.60].

C1 reuse: imports the PROBE cell's funcs VERBATIM (encode[bf16-on-GPU], train_contrastive, fit_zca[shrinkage], apply_zca,
top_k_magnitude, mask_fixed_random, _np_norm, recall_at, crosstalk_rho, make_facts) -> inherits the bf16 OOM-fix + the rank-def
shrinkage fix automatically. rho apples-to-apples (same held-out keys). chunked recall. checkpoint per (M,seed). 4-layer-witness.
VARIANT + F are fill-on-land from the probe verdict (env HDLAB_FLAGSHIP_VARIANT / HDLAB_FLAGSHIP_F; defaulted to the likely winner).
ASCII; no em-dashes.
"""
import sys, os, argparse, time
from pathlib import Path
import numpy as np
REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_partial_key, aggregate_partials, write_metrics
# C1: reuse the PROBE cell's funcs (import-safe via its __main__ guard) -> inherits bf16 encode + shrinkage-ZCA + sparsifiers
from experiments.exp_flagship_sparse_projected_KV_PROBE_whiten_before_topk_v1 import (
    make_facts, encode, train_contrastive, fit_zca, apply_zca, top_k_magnitude, mask_fixed_random, _np_norm, recall_at, crosstalk_rho)

ANCHOR_NAME = "flagship_sparse_projected_KV_LBUILD_v1"
VARIANT = os.environ.get("HDLAB_FLAGSHIP_VARIANT", "B_whiten_before_topk")   # fill-on-land from probe verdict (B shrinkage / C random-fixed / A naive)
F = float(os.environ.get("HDLAB_FLAGSHIP_F", "0.02"))                        # fill-on-land = probe-confirmed healthy f
HELDOUT_FRAC = 0.25
RECALL_THRESH = 0.95                                                         # capacity_M = max M with recall >= this
_P = argparse.ArgumentParser(); _P.add_argument("--self-test", action="store_true", dest="self_test"); _P.add_argument("--smoke", action="store_true"); _ARGS, _ = _P.parse_known_args()
RUN_MODE = "smoke" if (_ARGS.smoke or _ARGS.self_test) else os.environ.get("HDLAB_RUN_MODE", "full")
if RUN_MODE == "full":
    ENCODER = "EleutherAI/pythia-2.8b"; SEEDS = [7, 17, 23]; N = 8192; M_SCAN = [1000, 10000, 100000]; TRAIN_M = 4000; TRAIN_STEPS = 600
else:
    ENCODER = "EleutherAI/pythia-160m"; SEEDS = [0]; N = 2048; M_SCAN = [200, 500]; TRAIN_M = 400; TRAIN_STEPS = 200
CONFIG_VERSION = "imports-probe-funcs(bf16+shrinkage-ZCA) + 4arm-capacity-scan + rho-apples-to-apples; variant=%s f=%.3f" % (VARIANT, F)


def _arm_keys(arm, Kp, Qp, Kraw, Qraw, Wz_mu, f, g, N_dim):
    """Return (sparse/dense) key+cue matrices for an arm. Kp/Qp = projected (learned); Kraw/Qraw = raw pythia; Wz_mu = (mu,Wz) shrinkage-whiten fit on Kp."""
    if arm == "arm1_full":
        if VARIANT == "B_whiten_before_topk":
            mu, Wz = Wz_mu; return top_k_magnitude(apply_zca(Kp, mu, Wz), f), top_k_magnitude(apply_zca(Qp, mu, Wz), f)
        if VARIANT == "C_random_fixed_positions":
            idx = g.choice(N_dim, max(1, int(f * N_dim)), replace=False)
            mk = lambda X: (lambda o: (o.__setitem__((slice(None), idx), np.sign(X[:, idx]).astype(np.float32)), o)[1])(np.zeros_like(X, np.float32))
            return mk(Kp), mk(Qp)
        return top_k_magnitude(Kp, f), top_k_magnitude(Qp, f)                # A naive
    if arm == "arm2_noproj_sparse_raw":
        return top_k_magnitude(Kraw, f), top_k_magnitude(Qraw, f)
    if arm == "arm3_nosparse_dense_proj":
        return Kp.copy(), Qp.copy()                                         # dense projected (no sparsify)
    if arm == "arm4_noLearned_analytic":
        return None, None                                                  # handled in run (needs its own analytic projection)
    raise ValueError(arm)


def run_unit(seed):
    g = np.random.default_rng(seed)
    M_max = max(M_SCAN); n_total = M_max + TRAIN_M
    keys, cues = make_facts(n_total)
    print("  [seed=%d] encoding %d facts on %s..." % (seed, n_total, ENCODER), flush=True)
    K = encode(keys); Q = encode(cues)
    Ktr, Qtr = K[:TRAIN_M], Q[:TRAIN_M]; Kev, Qev = K[TRAIN_M:], Q[TRAIN_M:]    # train (projection) disjoint from eval (capacity scan)
    print("  [seed=%d] training projection D=%d -> N=%d..." % (seed, K.shape[1], N), flush=True)
    W = train_contrastive(Ktr, Qtr, N, TRAIN_STEPS, seed)
    Wa = (np.random.default_rng(seed + 1).standard_normal((K.shape[1], N)) * (1.0 / K.shape[1] ** 0.5)).astype(np.float32)   # arm4 ANALYTIC random projection
    arms = ["arm1_full", "arm2_noproj_sparse_raw", "arm3_nosparse_dense_proj", "arm4_noLearned_analytic"]
    by_arm = {a: {} for a in arms}
    for M in M_SCAN:
        Kev_M, Qev_M = Kev[:M], Qev[:M]
        Kp = Kev_M @ W; Qp = Qev_M @ W                                       # learned-projected
        Wz_mu = fit_zca(Kp)                                                  # shrinkage-whiten fit on THIS M's projected keys (rho apples-to-apples, same-run)
        for a in arms:
            if a == "arm4_noLearned_analytic":
                Ka = Kev_M @ Wa; Qa = Qev_M @ Wa; Ks, Qs = top_k_magnitude(Ka, F), top_k_magnitude(Qa, F)
            else:
                Ks, Qs = _arm_keys(a, Kp, Qp, Kev_M, Qev_M, Wz_mu, F, g, N)
            rec = recall_at(_np_norm(Qs), _np_norm(Ks)); rho = crosstalk_rho(_np_norm(Ks), g=g)
            by_arm[a]["M%d" % M] = {"recall": round(rec, 4), "rho": round(rho, 4)}
        print("    [seed=%d M=%d] %s" % (seed, M, {a: by_arm[a]["M%d" % M]["recall"] for a in arms}), flush=True)
    return {"seed": seed, "by_arm": by_arm, "variant": VARIANT, "f": F}


def _capacity(arm_curve):                                                    # max M with recall >= RECALL_THRESH (0 if none)
    ms = sorted(int(k[1:]) for k in arm_curve); cap = 0
    for m in ms:
        if arm_curve["M%d" % m]["recall"] >= RECALL_THRESH:
            cap = m
    return cap


def compute_verdict(units):
    if not units:
        return ("HARD_FAIL", "no results", {})
    def med_rec(a, M): return float(np.median([u["by_arm"][a]["M%d" % M]["recall"] for u in units]))
    def cv_rec(a, M):
        xs = [u["by_arm"][a]["M%d" % M]["recall"] for u in units]; return float(np.std(xs) / (abs(np.mean(xs)) + 1e-9))
    arms = ["arm1_full", "arm2_noproj_sparse_raw", "arm3_nosparse_dense_proj", "arm4_noLearned_analytic"]
    M_ref = M_SCAN[1] if len(M_SCAN) > 1 else M_SCAN[0]                      # the "mid" load (~5000-equiv) for the recall gate
    a1 = med_rec("arm1_full", M_ref); a2 = med_rec("arm2_noproj_sparse_raw", M_ref)
    caps = {a: _capacity({k: {"recall": med_rec(a, int(k[1:]))} for k in [("M%d" % M) for M in M_SCAN]}) for a in arms}
    worst_cv = max(cv_rec(a, M) for a in arms for M in M_SCAN)
    detail = {"variant": VARIANT, "f": F, "M_ref": M_ref, "by_arm_recall": {a: {("M%d" % M): med_rec(a, M) for M in M_SCAN} for a in arms},
              "capacity_M": caps, "arm1_minus_arm2_at_Mref": round(a1 - a2, 4), "worst_cv": round(worst_cv, 4),
              "CONFIG_VERSION": CONFIG_VERSION, "cites": ["flagship_PROBE_whiten_before_topk_v1", "CERT591_kv_learned_projection_v1", "a3f473dd_sparse_super_capacity"]}
    summ = "variant=%s f=%.3f | Arm1@Mref=%.3f Arm2@Mref=%.3f (d=%+.3f) | capacity_M=%s | worst_cv=%.3f" % (
        VARIANT, F, a1, a2, a1 - a2, caps, worst_cv)
    if worst_cv > 0.05 and len(units) >= 2:
        return ("MIDDLE_BAND", "MIDDLE_BAND: seed-unstable (cv>0.05). " + summ, detail)
    if a1 < 0.40 or caps["arm1_full"] < caps["arm3_nosparse_dense_proj"]:
        return ("HARD_FAIL", "HARD_FAIL: Arm1 recall<0.40 OR Arm1 capacity < Arm3 (sparse adds no scale -> projection+sparse does NOT compose). " + summ, detail)
    if a1 >= 0.60 and (a1 - a2) >= 0.20 and caps["arm1_full"] >= 2 * max(1, caps["arm3_nosparse_dense_proj"]):
        return ("HARD_PASS", "HARD_PASS (CHAIN-GRADE): Arm1 recall>=0.60 + beats Arm2 by >=0.20 + capacity >= 2x Arm3 -> learned-projection + sparsification COMPOSE into genuine super-capacity KV. " + summ, detail)
    return ("MIDDLE_BAND", "MIDDLE_BAND: Arm1 in [0.40,0.60] or capacity/beat thresholds not all met -> partial composition, honest-MM. " + summ, detail)


def _selftest():
    # structure-only check (no model): the arm-key builder produces correctly-shaped sparse codes for B/C/A + raw + dense.
    g = np.random.default_rng(0); n, d = 40, 256
    Kp = g.standard_normal((n, d)).astype(np.float32); Qp = Kp + 0.01 * g.standard_normal((n, d)).astype(np.float32)
    Kraw = g.standard_normal((n, 768)).astype(np.float32); Qraw = Kraw.copy()
    Wz_mu = fit_zca(Kp)
    for a in ["arm1_full", "arm2_noproj_sparse_raw", "arm3_nosparse_dense_proj"]:
        Ks, Qs = _arm_keys(a, Kp, Qp, Kraw, Qraw, Wz_mu, 0.05, np.random.default_rng(1), d)
        assert Ks is not None and Ks.shape[0] == n, "%s key shape" % a
    assert _capacity({"M100": {"recall": 0.99}, "M1000": {"recall": 0.80}}) == 100, "capacity = max M with recall>=0.95"
    print("[selftest] PASS: 4-arm key-builder shapes + capacity_M logic (variant=%s f=%.3f)" % (VARIANT, F), flush=True)


if __name__ == "__main__":
    _selftest()
    if _ARGS.self_test:
        raise SystemExit(0)
    print("[config] %s mode=%s ENCODER=%s N=%d M_SCAN=%s variant=%s f=%.3f seeds=%s | %s" % (
        ANCHOR_NAME, RUN_MODE, ENCODER, N, M_SCAN, VARIANT, F, SEEDS, CONFIG_VERSION), flush=True)
    out_dir = get_output_dir(ANCHOR_NAME); run_config = {"run_mode": RUN_MODE, "variant": VARIANT, "f": F, "schema": "4arm-capacity-scan"}; t0 = time.time()
    for seed in SEEDS:
        key = "s%d" % seed
        if key in aggregate_partials(out_dir, [key], run_config=run_config):
            print("[ckpt] %s done; skip" % key, flush=True); continue
        write_partial_key(out_dir, key, run_unit(seed))
    units = list(aggregate_partials(out_dir, ["s%d" % sd for sd in SEEDS], run_config=run_config).values())
    verdict, msg, detail = compute_verdict(units)
    print("\n[VERDICT] " + msg, flush=True)
    metrics = {"anchor_name": ANCHOR_NAME, "verdict": verdict, "verdict_msg": msg, "run_mode": RUN_MODE, "model": ENCODER, "N": N,
               "M_SCAN": M_SCAN, "variant": VARIANT, "f": F, "n_seeds": len(SEEDS), "detail": detail,
               "metrics_source": "measured_flagship_lbuild_4arm_capacity_scan", "per_unit": units, "elapsed_s": time.time() - t0}
    write_metrics(out_dir, metrics, units)
    print("[metrics] written to %s" % (out_dir / "metrics.json"), flush=True)
