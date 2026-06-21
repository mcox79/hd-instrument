"""FLAGSHIP sparse-projected-KV L-BUILD (cell 2 of 2) -- the chain-grade-vs-MM CAPACITY test, per the 4 RATIFIED L-build conditions
(Skunkworks landed-VET + Research ratify + Exp-Dev catch; 3-session convergence 2026-06-21).

The probe (cell 1) landed HARD_PASS on the encode-MECHANISM (B shrinkage-ZCA decrowds + survives sparse; abs-ZCA control collapses
-> rank-def fix validated) BUT its variant-pick (B) was PREMATURE: A_naive recalls HIGHER than B at every f at full scale (the
"naive collapses" RED was a smoke artifact). The variant question is a CAPACITY-CEILING one (does B's decrowding pay off as M grows,
even though A recalls better at M=5000?), which only this M-scan settles.

RATIFIED conditions baked in:
  C1: sweep M {1k,10k,100k} for BOTH arm1_A_naive AND arm1_B_shrinkage; pick the higher capacity-CEILING variant (NOT the single-M recall winner).
  C2: float32 dense-rec sanity-check (bf16-confound: probe dense_rec 0.63 << CERT591 0.83). float32 pythia-2.8b (~11GB) does NOT fit
      the 8GB GPU -> run the check on CPU for a small subset; report bf16-vs-float32 dense recall.
  C3: chain-grade bar = recall >= 0.80 and it must be GENUINE (not bf16-depressed). If recall caps ~0.63 in bf16 AND float32 also ~0.63
      -> genuine config-diff (M-crowding) -> capacity-gain WITHOUT 0.80-recall -> land MM honestly.
  C4: 4-layer-witness (process; cell-author + 2nd-witness + Skunkworks landed-VET + Director cross-check).

5 arms, all on the SAME held-out eval facts: arm1_A_naive / arm1_B_shrinkage (the 2 candidate composes) + arm2_noproj_sparse_raw
+ arm3_nosparse_dense_proj (CERT591) + arm4_noLearned_analytic. C1 reuse: imports the PROBE cell's funcs VERBATIM (bf16 encode +
shrinkage-ZCA + sparsifiers). rho apples-to-apples (same held-out keys, same run). chunked recall. checkpoint per (M,seed). ASCII.
"""
import sys, os, argparse, time
from pathlib import Path
import numpy as np
REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_partial_key, aggregate_partials, write_metrics
from experiments.exp_flagship_sparse_projected_KV_PROBE_whiten_before_topk_v1 import (
    make_facts, encode, train_contrastive, fit_zca, apply_zca, top_k_magnitude, _np_norm, recall_at, crosstalk_rho)

ANCHOR_NAME = "flagship_sparse_projected_KV_LBUILD_v1"
F = float(os.environ.get("HDLAB_FLAGSHIP_F", "0.02"))                        # probe-confirmed healthy f (capacity scan is over M at fixed f)
CAP_THRESH = 0.80                                                            # C3: capacity_M = max M with recall >= 0.80 (the chain-grade bar)
SUPERCAP_X = 3.0                                                             # chain-grade: best-arm1 capacity >= 3x arm3 (dense) capacity
F32_CHECK_N = 128                                                            # C2: float32 dense-rec sanity-check subset (CPU)
_P = argparse.ArgumentParser(); _P.add_argument("--self-test", action="store_true", dest="self_test"); _P.add_argument("--smoke", action="store_true"); _ARGS, _ = _P.parse_known_args()
RUN_MODE = "smoke" if (_ARGS.smoke or _ARGS.self_test) else os.environ.get("HDLAB_RUN_MODE", "full")
if RUN_MODE == "full":
    ENCODER = "EleutherAI/pythia-2.8b"; SEEDS = [7, 17, 23]; N = 8192; M_SCAN = [1000, 10000, 100000]; TRAIN_M = 4000; TRAIN_STEPS = 600
else:
    ENCODER = "EleutherAI/pythia-160m"; SEEDS = [0]; N = 2048; M_SCAN = [200, 500]; TRAIN_M = 400; TRAIN_STEPS = 200
ARM1_VARIANTS = ["arm1_A_naive", "arm1_B_shrinkage"]                         # C1: sweep BOTH
ARMS = ARM1_VARIANTS + ["arm2_noproj_sparse_raw", "arm3_nosparse_dense_proj", "arm4_noLearned_analytic"]
CONFIG_VERSION = "imports-probe-funcs(bf16+shrinkage) + C1:A+B-capacity-scan + C2:float32-cpu-check + C3:recall>=0.80-genuine + rho-apples; f=%.3f" % F


def recall_sampled(Qn, Kn, g, max_q=2000, chunk=256):
    """Recall (cue->key @1) over a SAMPLED subset of <=max_q queries vs ALL Kn keys. At M=100k the full MxM matmul is hours on
    CPU numpy; recall is a query-AVERAGE so sampling queries is unbiased (each sampled query i still checks argmax over all M keys).
    For M<=max_q this equals the exact recall_at."""
    M = len(Qn)
    if M <= max_q:
        idx = np.arange(M)
    else:
        idx = np.sort(g.choice(M, max_q, replace=False))
    cor = 0
    for a in range(0, len(idx), chunk):
        qi = idx[a:a + chunk]
        cor += int((np.argmax(Qn[qi] @ Kn.T, axis=1) == qi).sum())
    return cor / len(idx)


def _arm_codes(arm, Kp, Qp, Kraw, Qraw, Ka, Qa, f):
    """Sparse/dense key+cue codes per arm. Kp/Qp=learned-projected; Kraw/Qraw=raw pythia; Ka/Qa=analytic-projected; whiten fit inside for B."""
    if arm == "arm1_A_naive":             return top_k_magnitude(Kp, f), top_k_magnitude(Qp, f)
    if arm == "arm1_B_shrinkage":
        mu, Wz = fit_zca(Kp); return top_k_magnitude(apply_zca(Kp, mu, Wz), f), top_k_magnitude(apply_zca(Qp, mu, Wz), f)
    if arm == "arm2_noproj_sparse_raw":   return top_k_magnitude(Kraw, f), top_k_magnitude(Qraw, f)
    if arm == "arm3_nosparse_dense_proj": return Kp.copy(), Qp.copy()
    if arm == "arm4_noLearned_analytic":  return top_k_magnitude(Ka, f), top_k_magnitude(Qa, f)
    raise ValueError(arm)


def _f32_dense_check(keys, cues, W, n_check):
    """C2: float32 dense-rec on CPU (float32 pythia-2.8b won't fit the 8GB GPU). Loads model float32 on CPU, projects via the SAME W,
    measures dense recall on n_check held-out pairs -> compares to the bf16 dense recall. Best-effort (skip on failure/RAM)."""
    try:
        import torch
        from transformers import AutoModel, AutoTokenizer
        tok = AutoTokenizer.from_pretrained(ENCODER)
        if tok.pad_token is None: tok.pad_token = tok.eos_token
        mdl = AutoModel.from_pretrained(ENCODER, torch_dtype=torch.float32).to("cpu").eval()
        def enc(texts):
            out = []
            for i in range(0, len(texts), 16):
                t = tok(texts[i:i + 16], return_tensors="pt", padding=True, truncation=True, max_length=48)
                with torch.no_grad(): h = mdl(**t).last_hidden_state
                m = t["attention_mask"].unsqueeze(-1).float()
                out.append(((h * m).sum(1) / m.sum(1).clamp(min=1)).float().numpy())
            return np.concatenate(out, 0).astype(np.float32)
        Kf = enc(keys[:n_check]) @ W; Qf = enc(cues[:n_check]) @ W
        del mdl
        return round(recall_at(_np_norm(Qf), _np_norm(Kf)), 4)
    except Exception as e:
        print("  [C2] float32-CPU dense-check SKIPPED: %s" % str(e)[:120], flush=True); return None


def run_unit(seed, K, Q, keys, cues):                       # K/Q pre-encoded ONCE (facts are seed-independent -> no per-seed re-encode; the NEW-4 stall lesson)
    g = np.random.default_rng(seed)
    Ktr, Qtr = K[:TRAIN_M], Q[:TRAIN_M]; Kev, Qev = K[TRAIN_M:], Q[TRAIN_M:]
    print("  [seed=%d] training projection D=%d -> N=%d..." % (seed, K.shape[1], N), flush=True)
    W = train_contrastive(Ktr, Qtr, N, TRAIN_STEPS, seed)
    Wa = (np.random.default_rng(seed + 1).standard_normal((K.shape[1], N)) * (1.0 / K.shape[1] ** 0.5)).astype(np.float32)
    by_arm = {a: {} for a in ARMS}; dense_bf16 = {}
    for M in M_SCAN:
        Kev_M, Qev_M = Kev[:M], Qev[:M]; Kp = Kev_M @ W; Qp = Qev_M @ W; Ka = Kev_M @ Wa; Qa = Qev_M @ Wa
        for a in ARMS:
            Ks, Qs = _arm_codes(a, Kp, Qp, Kev_M, Qev_M, Ka, Qa, F)
            rec = recall_sampled(_np_norm(Qs), _np_norm(Ks), g)   # query-sampled (M=100k full MxM is hours on CPU numpy); exact for M<=2000
            rho = crosstalk_rho(_np_norm(Ks), g=g)
            by_arm[a]["M%d" % M] = {"recall": round(rec, 4), "rho": round(rho, 4)}
        dense_bf16["M%d" % M] = by_arm["arm3_nosparse_dense_proj"]["M%d" % M]["recall"]
        print("    [seed=%d M=%d] %s" % (seed, M, {a.replace("arm", ""): by_arm[a]["M%d" % M]["recall"] for a in ARMS}), flush=True)
    # C2: float32-CPU dense-rec sanity-check (bf16-confound) at the smallest M (use the same eval keys+cues + projection W)
    keys_ev = keys[TRAIN_M:]; cues_ev = cues[TRAIN_M:]
    f32_dense = _f32_dense_check(keys_ev, cues_ev, W, F32_CHECK_N) if seed == SEEDS[0] else None   # C2 once (loads 11GB float32 model on CPU; per-seed would be 3x slow)
    bf16_dense_at_check = recall_at(_np_norm((Kev[:F32_CHECK_N] @ W)), _np_norm((Qev[:F32_CHECK_N] @ W)))   # bf16 dense on the SAME subset for apples-to-apples
    print("  [seed=%d C2] float32-CPU dense_rec(n=%d)=%s vs bf16 dense_rec(same n)=%.3f" % (seed, F32_CHECK_N, f32_dense, bf16_dense_at_check), flush=True)
    return {"seed": seed, "by_arm": by_arm, "dense_bf16_by_M": dense_bf16, "f32_dense_check": f32_dense, "bf16_dense_check": round(bf16_dense_at_check, 4), "f": F}


def _capacity(rec_by_M):                                                      # C3: max M with recall >= CAP_THRESH (0.80)
    ms = sorted(int(k[1:]) for k in rec_by_M); cap = 0
    for m in ms:
        if rec_by_M["M%d" % m] >= CAP_THRESH: cap = m
    return cap


def compute_verdict(units):
    if not units:
        return ("HARD_FAIL", "no results", {})
    def medrec(a, M): return float(np.median([u["by_arm"][a]["M%d" % M]["recall"] for u in units]))
    def cv(a, M):
        xs = [u["by_arm"][a]["M%d" % M]["recall"] for u in units]; return float(np.std(xs) / (abs(np.mean(xs)) + 1e-9))
    rec = {a: {("M%d" % M): medrec(a, M) for M in M_SCAN} for a in ARMS}
    caps = {a: _capacity(rec[a]) for a in ARMS}
    best_arm1 = max(ARM1_VARIANTS, key=lambda a: caps[a]); best_cap = caps[best_arm1]; arm3_cap = caps["arm3_nosparse_dense_proj"]
    worst_cv = max(cv(a, M) for a in ARMS for M in M_SCAN)
    f32 = float(np.median([u["f32_dense_check"] for u in units if u.get("f32_dense_check") is not None])) if any(u.get("f32_dense_check") is not None for u in units) else None
    bf16c = float(np.median([u["bf16_dense_check"] for u in units]))
    best_arm1_maxrec = max(rec[best_arm1].values())
    detail = {"f": F, "cap_thresh": CAP_THRESH, "recall_by_arm": rec, "capacity_M": caps, "best_arm1": best_arm1, "best_arm1_capacity": best_cap,
              "arm3_dense_capacity": arm3_cap, "best_arm1_max_recall": round(best_arm1_maxrec, 4), "worst_cv": round(worst_cv, 4),
              "C2_float32_dense": f32, "C2_bf16_dense_same_subset": round(bf16c, 4),
              "C2_bf16_depresses_recall": (f32 is not None and f32 - bf16c > 0.10),
              "CONFIG_VERSION": CONFIG_VERSION, "cites": ["flagship_PROBE_whiten_before_topk_v1", "CERT591_kv_learned_projection_v1", "a3f473dd_sparse_super_capacity"]}
    summ = ("f=%.3f | capacity_M(rec>=%.2f): A=%d B=%d arm3_dense=%d arm2_raw=%d arm4_analytic=%d | best_arm1=%s(cap=%d, maxrec=%.3f) "
            "| C2: float32_dense=%s bf16_dense=%.3f (bf16_depresses=%s) | worst_cv=%.3f") % (
            F, CAP_THRESH, caps["arm1_A_naive"], caps["arm1_B_shrinkage"], arm3_cap, caps["arm2_noproj_sparse_raw"], caps["arm4_noLearned_analytic"],
            best_arm1, best_cap, best_arm1_maxrec, f32, bf16c, detail["C2_bf16_depresses_recall"], worst_cv)
    if worst_cv > 0.05 and len(units) >= 2:
        return ("MIDDLE_BAND", "MIDDLE_BAND: seed-unstable (cv>0.05). " + summ, detail)
    # C3: recall>=0.80 must be GENUINELY achievable. If best-arm1 never reaches 0.80 (capacity 0) -> capacity-gain-without-0.80 = honest MM (unless bf16-depressed + float32 recovers).
    genuine_080 = best_cap > 0 or (f32 is not None and f32 >= CAP_THRESH)
    supercap = best_cap >= SUPERCAP_X * max(1, arm3_cap)
    if not genuine_080:
        extra = " (bf16 dense %.2f; float32 dense %s -- recall>=0.80 NOT genuinely reached -> honest MM: capacity-mechanism without the 0.80 bar)" % (bf16c, f32)
        return ("MIDDLE_BAND", "MM (capacity-without-0.80): no arm1 variant reaches recall>=0.80 at any M -> the compose has a capacity DIRECTION but does not meet the genuine chain-grade recall bar." + extra + " " + summ, detail)
    if supercap and best_arm1_maxrec >= CAP_THRESH:
        return ("HARD_PASS", "HARD_PASS (CHAIN-GRADE): best arm1 variant %s reaches recall>=0.80 AND capacity_M >= %gx arm3-dense -> learned-projection + sparsification COMPOSE into genuine super-capacity KV. " % (best_arm1, SUPERCAP_X) + summ, detail)
    if best_cap > arm3_cap:
        return ("MIDDLE_BAND", "MIDDLE_BAND: best arm1 reaches 0.80 + beats dense capacity but < %gx (partial super-capacity) -> honest MM-strong. " % SUPERCAP_X + summ, detail)
    return ("HARD_FAIL", "HARD_FAIL: best arm1 capacity <= dense (arm3) -> sparsification adds no scale over dense projection. " + summ, detail)


def _selftest():
    g = np.random.default_rng(0); n, d = 40, 256
    Kp = g.standard_normal((n, d)).astype(np.float32); Qp = Kp + 0.01 * g.standard_normal((n, d)).astype(np.float32)
    Kraw = g.standard_normal((n, 768)).astype(np.float32); Ka = g.standard_normal((n, d)).astype(np.float32)
    for a in ARMS:
        Ks, Qs = _arm_codes(a, Kp, Qp, Kraw, Kraw.copy(), Ka, Ka.copy(), 0.05)
        assert Ks.shape[0] == n, "%s key shape" % a
    assert _capacity({"M100": 0.99, "M1000": 0.85, "M10000": 0.50}) == 1000, "capacity = max M with recall>=0.80"
    assert _capacity({"M100": 0.70}) == 0, "capacity 0 when never >=0.80"
    print("[selftest] PASS: 5-arm (A+B+raw+dense+analytic) key shapes + capacity_M@0.80 logic (f=%.3f)" % F, flush=True)


if __name__ == "__main__":
    _selftest()
    if _ARGS.self_test:
        raise SystemExit(0)
    print("[config] %s mode=%s ENCODER=%s N=%d M_SCAN=%s f=%.3f seeds=%s | %s" % (ANCHOR_NAME, RUN_MODE, ENCODER, N, M_SCAN, F, SEEDS, CONFIG_VERSION), flush=True)
    out_dir = get_output_dir(ANCHOR_NAME); run_config = {"run_mode": RUN_MODE, "f": F, "schema": "5arm-AB-capacity-scan-C1C2C3"}; t0 = time.time()
    done0 = aggregate_partials(out_dir, ["s%d" % s for s in SEEDS], run_config=run_config)
    K = Q = keys = cues = None
    if any(("s%d" % s) not in done0 for s in SEEDS):       # encode ONCE for all seeds (facts seed-independent); re-encode only on a fresh start, not per-seed
        M_max = max(M_SCAN); n_total = M_max + TRAIN_M; keys, cues = make_facts(n_total)
        print("[encode-once] %d facts on %s (bf16; seed-independent -> encoded ONCE for all %d seeds)..." % (n_total, ENCODER, len(SEEDS)), flush=True)
        K = encode(keys); Q = encode(cues)
    for seed in SEEDS:
        key = "s%d" % seed
        if key in aggregate_partials(out_dir, [key], run_config=run_config):
            print("[ckpt] %s done; skip" % key, flush=True); continue
        write_partial_key(out_dir, key, run_unit(seed, K, Q, keys, cues))
    units = list(aggregate_partials(out_dir, ["s%d" % sd for sd in SEEDS], run_config=run_config).values())
    verdict, msg, detail = compute_verdict(units)
    print("\n[VERDICT] " + msg, flush=True)
    metrics = {"anchor_name": ANCHOR_NAME, "verdict": verdict, "verdict_msg": msg, "run_mode": RUN_MODE, "model": ENCODER, "N": N,
               "M_SCAN": M_SCAN, "f": F, "n_seeds": len(SEEDS), "detail": detail, "conditions": "C1-AB-capacity / C2-float32-check / C3-recall>=0.80-genuine / C4-4layer",
               "metrics_source": "measured_flagship_lbuild_AB_capacity_scan", "per_unit": units, "elapsed_s": time.time() - t0}
    write_metrics(out_dir, metrics, units)
    print("[metrics] written to %s" % (out_dir / "metrics.json"), flush=True)
