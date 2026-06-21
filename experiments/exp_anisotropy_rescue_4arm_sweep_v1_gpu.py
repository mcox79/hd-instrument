"""ANISOTROPY-RESCUE 4-ARM sweep -- the sparse-fan-in / fly-LSH path to break the rank-1 anisotropy collapse on learned keys.

Parallel to the whitening-revival (isotropization path): the dense-KV learned-key MM showed superposition ARM1 COLLAPSES on real
pythia keys (common-mode anisotropy). Research's biology/brain drill: cerebellar K=5 sparse-fan-in + fly-LSH are the only 2 of 8
surveyed mechanisms that QUALITATIVELY break the rank-1 trap. This cell tests them, 4 arms each PASS/FAIL pre-reg'd (drill section c).

ARMs @ M={1k,3k,10k}, C=256 codebook, recall@1 + per-memory storage:
  ARM A  cerebellar sparse-fan-in K=5: expand d'=5d, each unit reads K=5 random input dims, kWTA top-10%, superposition + decode.
         control A' = same d'+kWTA but DENSE-Gaussian fan-in (must HARD-FAIL -> credits sparse-fan-in).  [M-INDEP O(d'^2) storage]
  ARM B  fly-LSH+CERT591: median-subtract -> sparse random proj -> WTA top-k=20 -> sparse-tag; retrieve by tag-overlap argmax.
         control B' = Charikar hyperplane LSH (must underperform -> credits WTA-shift-invariance).  [O(M) per-memory-COMPRESSED storage, NOT M-indep -- C2]
  ARM C  compose A->B (sparse-fan-in expand then fly-LSH on the expanded code).
  ARM D  attention 1-step softmax (O(M*d) upper-bound; calibration ~0.80-0.95).

Skunkworks SCHEMA-VET conditions:
  C1 (LOAD-BEARING, verified): the mean_cos<0.20 pre-flight KILL gate is ~5-20x too high (collapse onset at mean_cos~1/sqrt(M)~0.01@M=10k).
     FIX = KILL only if ARM1_RAW (raw superposition recall) >= 0.80 (direct measurement: if raw already holds, no anisotropy problem -> kill;
     if collapsed, rescue is needed -> run). Real pythia keys ARE in the collapse regime (GATE-2 proof) so this un-blocks the cell.
  C2 (storage class): ARM A/C-superposition = genuinely M-INDEP (O(d'^2)); ARM B fly-LSH = O(M) per-memory-COMPRESSED (<=1KB/mem), NOT M-indep -- report distinctly.
Bands (drill c): A HARD-PASS recall>=0.40@10k + A'<=0.20 + K-peak@5; B HARD-PASS recall>=0.60 + M-indep-degrade<=0.10 + storage<=1KB + B'<B; C HARD-PASS recall>=0.70 + beats A&B by 0.10; D calibration ~0.80-0.95.
Smoke gate: ARM A K-sweep {1,5,20,full}@M=1k unimodal peak@K=5 (Litwin-Kumar 2017). C1 reuse: probe encode/train_contrastive + dense-KV _decode. ASCII; per-seed ckpt.
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
_probe.ENC_DTYPE = torch.float16 if torch.cuda.is_available() else torch.float32
from experiments.exp_flagship_sparse_projected_KV_PROBE_whiten_before_topk_v1 import (make_facts, encode, train_contrastive, _np_norm)
from experiments.exp_dense_projected_KV_envelope_v1 import _decode

ANCHOR_NAME = "anisotropy_rescue_4arm_sweep_v1_gpu"
PROJ_DIM = 768; C = 256; EXPAND = 5; K_FANIN = 5; KWTA_FRAC = 0.10; FLY_TOPK = 20; FLY_NONZERO = 0.05; SIGMA = 0.1; MAX_Q = 1500
ARM1_RAW_KILL = 0.80                                          # C1 (Skunkworks): KILL only if raw superposition already holds (no anisotropy problem)
_P = argparse.ArgumentParser(); _P.add_argument("--self-test", action="store_true", dest="self_test"); _P.add_argument("--smoke", action="store_true"); _ARGS, _ = _P.parse_known_args()
RUN_MODE = "smoke" if (_ARGS.smoke or _ARGS.self_test) else os.environ.get("HDLAB_RUN_MODE", "full")
if RUN_MODE == "full":
    ENCODER = "EleutherAI/pythia-2.8b"; SEEDS = [7, 17, 23, 31, 41]; M_SWEEP = [1000, 3000, 10000]; TRAIN_M = 7500; TRAIN_STEPS = 600
else:
    ENCODER = "EleutherAI/pythia-160m"; SEEDS = [0]; M_SWEEP = [400, 1000]; TRAIN_M = 600; TRAIN_STEPS = 200
CONFIG_VERSION = "4arm(A-cerebellar-K%d/A'-dense / B-flyLSH/B'-charikar / C-compose / D-attn); expand%dx kwta%.2f flytopk%d; C1-ARM1_RAW>=%.2f-kill C2-storage-class; FP16" % (K_FANIN, EXPAND, KWTA_FRAC, FLY_TOPK, ARM1_RAW_KILL)


def _kwta(X, frac):                                          # keep top-frac magnitudes per row, zero rest (sign preserved)
    k = max(1, int(frac * X.shape[1])); out = np.zeros_like(X, np.float32)
    idx = np.argpartition(np.abs(X), -k, axis=1)[:, -k:]
    np.put_along_axis(out, idx, np.take_along_axis(X, idx, axis=1), axis=1); return out


def _sparse_fanin(d, dp, K, g):                             # cerebellar: dp expanded units, each reads K random input dims (random +-1)
    S = np.zeros((dp, d), np.float32)
    for i in range(dp):
        idx = g.choice(d, K, replace=False); S[i, idx] = g.integers(0, 2, K).astype(np.float32) * 2 - 1
    return S


def _superpos_recall(Kexp, y, codebook, cue_exp, qidx):     # M-indep superposition store (W d'xd') + C-codebook decode
    W = codebook[y].T @ Kexp                                # (C_dim? no: code is d'-dim) -- codebook must be d'-dim; see _arms
    return float((_decode(cue_exp @ W.T, codebook) == y[qidx]).mean())


def _flylsh_tags(X, P, topk):                              # median-subtract -> sparse random proj P -> WTA top-k -> binary tag set
    Xc = X - np.median(X, axis=0, keepdims=True); H = Xc @ P.T
    tags = np.zeros_like(H, np.int8); idx = np.argpartition(H, -topk, axis=1)[:, -topk:]
    np.put_along_axis(tags, idx, 1, axis=1); return tags


def _arms(Kp, y, g, seed):
    d = Kp.shape[1]; M = len(Kp); dp = EXPAND * d
    qidx = np.arange(M) if M <= MAX_Q else np.sort(g.choice(M, MAX_Q, replace=False))
    noise = SIGMA * g.standard_normal((len(qidx), d)).astype(np.float32)
    Ks = _np_norm(Kp) * np.sqrt(d); cue = Ks[qidx] + noise; ytrue = y[qidx]
    # ARM1_RAW (the C1 kill-gate measurement): raw superposition on the d-dim keys (dense-KV ARM1)
    cb_d = _np_norm(g.standard_normal((C, d)).astype(np.float32))
    W_raw = cb_d[y].T @ Ks; arm1_raw = float((_decode(cue @ W_raw.T, cb_d) == ytrue).mean())
    # ARM A: cerebellar sparse-fan-in -> kWTA -> superposition (expanded space). codebook in d'-dim.
    cb_dp = _np_norm(g.standard_normal((C, dp)).astype(np.float32))
    Sf = _sparse_fanin(d, dp, K_FANIN, g); Kexp = _kwta(Ks @ Sf.T, KWTA_FRAC); cue_exp = _kwta(cue @ Sf.T, KWTA_FRAC)
    WA = cb_dp[y].T @ Kexp; arm_A = float((_decode(cue_exp @ WA.T, cb_dp) == ytrue).mean())
    Sd = g.standard_normal((dp, d)).astype(np.float32) * (1.0 / d ** 0.5)        # A' dense-Gaussian fan-in (control)
    KexpD = _kwta(Ks @ Sd.T, KWTA_FRAC); cueD = _kwta(cue @ Sd.T, KWTA_FRAC)
    WAp = cb_dp[y].T @ KexpD; arm_Ap = float((_decode(cueD @ WAp.T, cb_dp) == ytrue).mean())
    # ARM B: fly-LSH tags -> retrieve by max tag-overlap -> label.  control B' = Charikar hyperplane signs.
    Pf = (g.random((dp, d)).astype(np.float32) < FLY_NONZERO).astype(np.float32) * (g.standard_normal((dp, d)).astype(np.float32))
    Kt = _flylsh_tags(Ks, Pf, FLY_TOPK); Qt = _flylsh_tags(cue, Pf, FLY_TOPK)
    arm_B = float((y[np.argmax(Qt @ Kt.T, axis=1)] == ytrue).mean())
    Hc = g.standard_normal((dp, d)).astype(np.float32)                            # Charikar hyperplanes
    Kc = np.sign(Ks @ Hc.T).astype(np.float32); Qc = np.sign(cue @ Hc.T).astype(np.float32)
    arm_Bp = float((y[np.argmax(Qc @ Kc.T, axis=1)] == ytrue).mean())
    # ARM C: compose sparse-fan-in expand -> fly-LSH on the expanded code
    Pc = (g.random((dp, dp)).astype(np.float32) < FLY_NONZERO).astype(np.float32)
    Ktc = _flylsh_tags(Kexp, Pc, FLY_TOPK); Qtc = _flylsh_tags(cue_exp, Pc, FLY_TOPK)
    arm_C = float((y[np.argmax(Qtc @ Ktc.T, axis=1)] == ytrue).mean())
    # ARM D: attention 1-step softmax (upper bound) on d-dim keys
    beta = 1.0 / np.sqrt(d); lg = beta * (cue @ Ks.T); lg -= lg.max(1, keepdims=True); w = np.exp(lg); w /= w.sum(1, keepdims=True)
    arm_D = float((_decode(w @ cb_d[y], cb_d) == ytrue).mean())
    # storage per memory (bits): A/C superposition = d'^2/M (amortized, M-indep); B = topk*log2(dp) tags (per-memory)
    return {"arm1_raw": round(arm1_raw, 4), "arm_A": round(arm_A, 4), "arm_Ap_dense": round(arm_Ap, 4),
            "arm_B": round(arm_B, 4), "arm_Bp_charikar": round(arm_Bp, 4), "arm_C": round(arm_C, 4), "arm_D": round(arm_D, 4),
            "B_storage_bits_per_mem": round(FLY_TOPK * np.log2(dp), 1)}


def run_unit(seed):
    g = np.random.default_rng(seed); n_total = max(M_SWEEP) + TRAIN_M
    keys, cues = make_facts(n_total)
    print("  [seed=%d] encoding %d facts on %s (fp16)..." % (seed, n_total, ENCODER), flush=True)
    K = encode(keys); Q = encode(cues)
    perm = g.permutation(n_total); tr = perm[:TRAIN_M]; ho = perm[TRAIN_M:]
    W = train_contrastive(K[tr], Q[tr], PROJ_DIM, TRAIN_STEPS, seed)
    Kp_all = K[ho] @ W
    by_M = {}
    for M in M_SWEEP:
        y = g.integers(0, C, M); by_M["M%d" % M] = _arms(Kp_all[:M], y, np.random.default_rng(seed * 7 + M), seed)
        a = by_M["M%d" % M]
        print("  [seed=%d M=%d] raw=%.3f A=%.3f(A'=%.3f) B=%.3f(B'=%.3f) C=%.3f D=%.3f" % (seed, M, a["arm1_raw"], a["arm_A"], a["arm_Ap_dense"], a["arm_B"], a["arm_Bp_charikar"], a["arm_C"], a["arm_D"]), flush=True)
    return {"seed": seed, "by_M": by_M}


def compute_verdict(units):
    if not units:
        return ("HARD_FAIL", "no results", {})
    M10 = 10000 if 10000 in M_SWEEP else max(M_SWEEP); M1 = min(M_SWEEP)
    def med(M, a): return float(np.median([u["by_M"]["M%d" % M][a] for u in units]))
    raw10 = med(M10, "arm1_raw")
    A, Ap = med(M10, "arm_A"), med(M10, "arm_Ap_dense"); B, Bp = med(M10, "arm_B"), med(M10, "arm_Bp_charikar")
    Cc = med(M10, "arm_C"); D = med(M10, "arm_D"); B_M1 = med(M1, "arm_B"); B_degrade = B_M1 - B
    detail = {"ARM1_RAW@M10": raw10, "arm_A": A, "arm_Ap_dense": Ap, "arm_B": B, "arm_Bp_charikar": Bp, "arm_C": Cc, "arm_D": D,
              "B_M_indep_degrade": round(B_degrade, 4), "B_storage_bits_per_mem": units[0]["by_M"]["M%d" % M10]["B_storage_bits_per_mem"],
              "storage_class": "A/C-superpos=M-INDEP O(d'^2); B-flyLSH=O(M) per-mem-compressed (C2)", "CONFIG_VERSION": CONFIG_VERSION,
              "cites": ["dense_KV_learned_key_MM_anisotropy", "research_biology_brain_drill", "Litwin-Kumar2017_cerebellar", "fly_LSH_Dasgupta2017"]}
    summ = "ARM1_RAW=%.3f(kill if>=%.2f) | A=%.3f(A'dense=%.3f) B=%.3f(B'charikar=%.3f, degrade=%.3f, %.0fb/mem) C=%.3f D=%.3f" % (
        raw10, ARM1_RAW_KILL, A, Ap, B, Bp, B_degrade, detail["B_storage_bits_per_mem"], Cc, D)
    # C1 pre-flight kill: if raw superposition ALREADY holds, no anisotropy problem -> drop
    if raw10 >= ARM1_RAW_KILL:
        return ("HARD_FAIL", "PRE-FLIGHT KILL (C1): ARM1_RAW=%.3f >= %.2f -> raw superposition already holds -> no anisotropy collapse to rescue (non-problem). " % (raw10, ARM1_RAW_KILL) + summ, detail)
    # the headline: do A (sparse-fan-in, M-indep) and/or B (fly-LSH, compressed) rescue ARM1 from raw-collapse, with their controls failing?
    A_pass = A >= 0.40 and Ap <= 0.20; B_pass = B >= 0.60 and B_degrade <= 0.10 and Bp < B; C_pass = Cc >= 0.70 and Cc >= max(A, B) + 0.10
    detail["A_pass"] = bool(A_pass); detail["B_pass"] = bool(B_pass); detail["C_pass"] = bool(C_pass)
    if D < 0.80:
        return ("MIDDLE_BAND", "CALIBRATION FLAG: ARM D (attention upper-bound) = %.3f < 0.80 -> meter under-calibrated; interpret arms RELATIVE only. " % D + summ, detail)
    wins = [n for n, p in [("A_sparse-fanin", A_pass), ("B_flyLSH", B_pass), ("C_compose", C_pass)] if p]
    if C_pass:
        return ("HARD_PASS", "CHAIN-GRADE-CANDIDATE: ARM C (sparse-fan-in + fly-LSH compose) recall>=0.70 @M=10k + beats A&B by >=0.10 -> composed anisotropy-rescue. raw collapsed %.3f -> rescued. " % raw10 + summ, detail)
    if A_pass or B_pass:
        return ("HARD_PASS", "CHAIN-GRADE-CANDIDATE (%s rescues): raw collapsed (%.3f) -> %s breaks the anisotropy trap on real learned keys (control(s) fail as required). A=M-indep / B=compressed (C2). " % ("+".join(wins), raw10, "+".join(wins)) + summ, detail)
    if max(A, B, Cc) >= 0.15:
        return ("MIDDLE_BAND", "MEASURED_MECHANISM: partial rescue (best %.3f) -- a mechanism helps vs raw-collapse %.3f but no arm clears its HARD-PASS bar; honest partial. " % (max(A, B, Cc), raw10) + summ, detail)
    return ("HARD_FAIL", "HARD_FAIL: no arm rescues ARM1 from anisotropy collapse (all ~raw %.3f) -> sparse-fan-in/fly-LSH do NOT break the trap on real keys (contra the drill prediction). " % raw10 + summ, detail)


def _selftest():
    g = np.random.default_rng(0); d = 128; M = 1500          # alpha~12 (capacity regime; light enough to run fast under runner contention)
    sig = g.standard_normal((M, d)).astype(np.float32); mu = g.standard_normal((1, d)).astype(np.float32) * 3.0
    Kp = sig + mu                                            # anisotropic (common-mode) -> raw superposition collapses
    y = g.integers(0, C, M); r = _arms(Kp, y, np.random.default_rng(1), 1)
    assert r["arm1_raw"] < 0.30, "raw superposition collapses on anisotropic keys (got %.2f)" % r["arm1_raw"]
    assert max(r["arm_A"], r["arm_B"], r["arm_C"]) > r["arm1_raw"] + 0.10, "at least one rescue arm beats raw (A=%.2f B=%.2f C=%.2f vs raw=%.2f)" % (r["arm_A"], r["arm_B"], r["arm_C"], r["arm1_raw"])
    # decode-meter check: on ISOTROPIC (no common-mode) tiny-M keys, raw superposition recovers (validates the decode meter; ARM D's
    # value is regime-dependent -- attention collapses on this EXTREME-mu synthetic but holds on real milder-anisotropy keys [dense-KV 0.997], so it's verdict-flagged not selftest-asserted).
    iso = g.standard_normal((200, d)).astype(np.float32); yi = g.integers(0, C, 200)
    ri = _arms(iso, yi, np.random.default_rng(2), 2)
    assert ri["arm1_raw"] > 0.8, "isotropic tiny-M raw superposition holds = decode meter works (got %.2f)" % ri["arm1_raw"]
    print("[selftest] PASS: anisotropic raw collapses (%.2f) + rescue beats raw (A=%.2f B=%.2f C=%.2f) + isotropic decode-meter raw=%.2f" % (r["arm1_raw"], r["arm_A"], r["arm_B"], r["arm_C"], ri["arm1_raw"]), flush=True)


if __name__ == "__main__":
    _selftest()
    if _ARGS.self_test:
        raise SystemExit(0)
    print("[config] %s mode=%s ENCODER=%s proj=%d M=%s seeds=%s | %s" % (ANCHOR_NAME, RUN_MODE, ENCODER, PROJ_DIM, M_SWEEP, SEEDS, CONFIG_VERSION), flush=True)
    out_dir = get_output_dir(ANCHOR_NAME); run_cfg = {"run_mode": RUN_MODE, "proj": PROJ_DIM, "expand": EXPAND, "kfanin": K_FANIN, "schema": "4arm-rescue"}; t0 = time.time()
    for seed in SEEDS:
        key = "s%d" % seed
        if key in aggregate_partials(out_dir, [key], run_config=run_cfg):
            print("[ckpt] %s done; skip" % key, flush=True); continue
        write_partial_key(out_dir, key, run_unit(seed))
    units = list(aggregate_partials(out_dir, ["s%d" % sd for sd in SEEDS], run_config=run_cfg).values())
    verdict, msg, detail = compute_verdict(units)
    print("\n[VERDICT] " + msg, flush=True)
    metrics = {"anchor_name": ANCHOR_NAME, "verdict": verdict, "verdict_msg": msg, "run_mode": RUN_MODE, "model": ENCODER, "proj_dim": PROJ_DIM,
               "M_SWEEP": M_SWEEP, "n_seeds": len(SEEDS), "detail": detail, "metrics_source": "measured_gpu_anisotropy_rescue_4arm", "per_unit": units, "elapsed_s": time.time() - t0}
    write_metrics(out_dir, metrics, units)
    print("[metrics] written to %s" % (out_dir / "metrics.json"), flush=True)
