"""ANISOTROPY-RESCUE 4-ARM sweep v2 -- CALIBRATED METER, FULL mode (3 seeds), GPU (overnight_queue).

PROMOTION CONTEXT (USER 2026-06-25): v1 smoke (1 seed, pythia-160m, M=[400,1000]) returned MIDDLE_BAND with
ARM D (attention upper-bound) = 0.445 < 0.80 -> meter under-calibrated; cell uninterpretable in absolute terms. The
mechanism numbers were interesting though: ARM B (fly-LSH) = 0.612 at M=1k, ARM B' (Charikar hyperplane LSH; intended
NEGATIVE control) = 0.982 at M=1k -- i.e. the Charikar arm BEAT fly-LSH AND beat the under-calibrated upper-bound D.
Either Charikar genuinely chain-grades on this regime, OR the meter is so broken everything is uninterpretable.

v2 CHANGES (load-bearing):
  1. Calibrated meter -- Arm D is now MAX over an attention-beta sweep (beta multipliers {1, 4, 16, 64}; v1 used
     beta=1/sqrt(d) which is flat-softmax at d=768/M=1000 -> mass spreads -> top-1 dies). True attention-upper-bound
     should pick its best temperature, not be locked at the theory-default value. ASSERT Arm D >= 0.80 in self-test
     on a fixed isotropic regime; the v1 meter bug would self-test FAIL here.
  2. ALSO report relative ratios arm_X / arm_D as a safety net. If absolute arm_D still struggles at full, the
     ratio gives the MIDDLE_BAND_RELATIVE_PROMISE band.
  3. 3 seeds [11, 13, 19] (cross-cell consistent with today's batch). cv ceiling 0.05 for chain-grade.
  4. torch.cuda used actively (Fix #24) -- big matmuls on GPU; encoder hoisted. Self-test stays numpy (CPU).
  5. Q-discipline -- if any arm hits >= 0.995, flag suspect saturation per BIAS-Q.
  6. ARM RENAMING for honesty: v1 labelled Charikar as "B' negative control of B"; v2 renames B and B' to
     B_fly_lsh and B_charikar (peers, not control), reports both as candidates. The mechanism story is "do
     hash-codes via sparse-fan-in or hyperplane signs survive anisotropy?" -- both are LSH variants worth testing.
  7. Self-test asserts both isotropic raw works (decode meter) AND attention-beta-sweep recovers >= 0.80 on
     isotropic synthetic at M=400, d=128 (catches the meter-collapse bug at smoke regime).

PRE-REGISTERED BANDS (LOCKED AT MODULE INIT via assert META_PROSPECTIVE_BANDS_FRESH_SEEDS):
  HARD_PASS_ANISOTROPY_SOLVED_VIA_LSH_FANOUT:
    Arm B_fly_lsh >= 0.80 AND Arm D >= 0.80 AND cv <= 0.05 across 3 seeds AT M=10k
  HARD_PASS_PARTIAL_LSH:
    Arm B_fly_lsh >= 0.60 AND Arm D >= 0.80 AND cv <= 0.07 AT M=10k
  HARD_PASS_CHARIKAR_RESCUE:
    Arm B_charikar >= 0.80 AND Arm D >= 0.80 AND cv <= 0.05 (v1 smoke saw 0.982; this proves whether it survives 3 seeds at d_768 pythia-2.8b)
  MIDDLE_BAND_RELATIVE_PROMISE:
    (Arm B_fly_lsh / Arm D) >= 0.80 OR (Arm B_charikar / Arm D) >= 0.80 even if absolute < 0.80
    -- meter still struggles at this regime but mechanism is real RELATIVE to attention
  HARD_FAIL_LSH_DOESNT_HOLD:
    BOTH Arm B_fly_lsh <= 0.40 AND Arm B_charikar <= 0.40 -- v1 smoke 0.982 was an artifact
  METER_UNDER_CALIBRATED:
    Arm D < 0.80 even after beta-sweep -- cell uninterpretable for absolute claims; verdict notes meter status but
    still tries the relative-promise band

Q-DISCIPLINE: any arm >= 0.995 triggers [Q-DISCIPLINE: suspect saturation] note in verdict; consider corpus too easy.

ASCII-only. Substrate-only (no LLM forward calls at inference; only encoder hoisted ONCE for hidden states). torch.cuda
active on big matmuls; CPU fallback when not available (self-test path). PROT-020 (torch). Route overnight_queue.
"""
from __future__ import annotations
import sys, os, argparse, time, math, json
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
import torch  # PROT-020 GPU-gate literal; Fix #24 active GPU use

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_partial_key, aggregate_partials, write_metrics

ANCHOR_NAME = "substrate_anisotropy_rescue_4arm_sweep_v2_calibrated_meter_full"

_P = argparse.ArgumentParser()
_P.add_argument("--self-test", action="store_true", dest="self_test")
_P.add_argument("--smoke", action="store_true")
_ARGS, _ = _P.parse_known_args()
RUN_MODE = "smoke" if (_ARGS.smoke or _ARGS.self_test) else os.environ.get("HDLAB_RUN_MODE", "full")

# CAPACITY-SENSITIVE: smoke matches full on PROJ_DIM, C, EXPAND, K_FANIN, KWTA_FRAC, FLY_TOPK, FLY_NONZERO, SIGMA, BETA_MULT
PROJ_DIM = 768
C = 256
EXPAND = 5
K_FANIN = 5
KWTA_FRAC = 0.10
FLY_TOPK = 20
FLY_NONZERO = 0.05
SIGMA = 0.1
MAX_Q = 1500
# v2 KEY ADD: attention beta multiplier sweep. Arm D = max over these multipliers.
# Real attention picks its temperature; the upper-bound test should reflect that.
BETA_MULT_SWEEP = [1.0, 4.0, 16.0, 64.0]

# v2 modes -- smoke is the calibration-check (catches meter regression); full is the verdict-grade run.
if RUN_MODE == "full":
    ENCODER = "EleutherAI/pythia-2.8b"
    SEEDS = [11, 13, 19]
    M_SWEEP = [1000, 3000, 10000]
    TRAIN_M = 7500
    TRAIN_STEPS = 600
else:
    ENCODER = "EleutherAI/pythia-160m"
    SEEDS = [11]  # smoke runs 1 seed; full runs 3
    M_SWEEP = [400, 1000]
    TRAIN_M = 600
    TRAIN_STEPS = 200

# PROSPECTIVE BANDS (LOCKED AT MODULE INIT per META_PROSPECTIVE_BANDS_FRESH_SEEDS).
BAND_HP_LSH = 0.80                # ARM B_fly_lsh or B_charikar absolute floor for HARD_PASS at M=10k
BAND_HP_PARTIAL_LSH = 0.60        # partial-rescue absolute floor
BAND_METER_FLOOR = 0.80           # ARM D must hit this for cell to be interpretable absolute
BAND_CV_HP = 0.05                 # cv ceiling for HARD_PASS_SOLVED
BAND_CV_PARTIAL = 0.07            # cv ceiling for HARD_PASS_PARTIAL
BAND_HF_LSH = 0.40                # both LSH arms below this = HARD_FAIL (v1 smoke 0.982 was an artifact)
BAND_REL_PROMISE = 0.80           # arm_X / arm_D ratio floor for MIDDLE_BAND_RELATIVE_PROMISE
BAND_Q_SATURATION = 0.995         # if any arm >= this, flag suspect saturation

# bands self-asserted
assert 0.0 < BAND_HP_LSH < 1.0, "band locked"
assert 0.0 < BAND_HP_PARTIAL_LSH < BAND_HP_LSH < 1.0, "partial < hp"
assert 0.0 < BAND_HF_LSH < BAND_HP_PARTIAL_LSH, "fail < partial"
assert 0.0 < BAND_REL_PROMISE < 1.0, "rel-promise band locked"
assert BAND_Q_SATURATION > BAND_HP_LSH, "saturation guard above hp"

CONFIG_VERSION = (
    "v2_calibrated_meter(A-cerebellar-K%d/A'-dense / B_fly_lsh / B_charikar / C-compose / D-attn-beta-sweep) | "
    "expand%dx kwta%.2f flytopk%d | beta_mults=%s | seeds=%s | M=%s | FP32_GPU | bands locked"
) % (K_FANIN, EXPAND, KWTA_FRAC, FLY_TOPK, BETA_MULT_SWEEP, SEEDS, M_SWEEP)


def _np_norm(X):
    return (X / (np.linalg.norm(X, axis=-1, keepdims=True) + 1e-8)).astype(np.float32)


def _decode_np(R, codebook):
    return np.argmax(_np_norm(R) @ codebook.T, axis=1)


def _kwta_np(X, frac):
    k = max(1, int(frac * X.shape[1]))
    out = np.zeros_like(X, np.float32)
    idx = np.argpartition(np.abs(X), -k, axis=1)[:, -k:]
    np.put_along_axis(out, idx, np.take_along_axis(X, idx, axis=1), axis=1)
    return out


def _sparse_fanin_np(d, dp, K, g):
    S = np.zeros((dp, d), np.float32)
    for i in range(dp):
        idx = g.choice(d, K, replace=False)
        S[i, idx] = g.integers(0, 2, K).astype(np.float32) * 2 - 1
    return S


def _flylsh_tags_np(X, P, topk):
    Xc = X - np.median(X, axis=0, keepdims=True)
    H = Xc @ P.T
    tags = np.zeros_like(H, np.int8)
    idx = np.argpartition(H, -topk, axis=1)[:, -topk:]
    np.put_along_axis(tags, idx, 1, axis=1)
    return tags


# ---------- torch.cuda accelerated arms (used at smoke/full when GPU available) ----------

def _torch_device():
    return torch.device("cuda" if torch.cuda.is_available() else "cpu")


def _norm_t(X):
    return X / (X.norm(dim=-1, keepdim=True) + 1e-8)


def _decode_t(R, codebook):
    Rn = _norm_t(R)
    return torch.argmax(Rn @ codebook.t(), dim=1)


def _kwta_t(X, frac):
    k = max(1, int(frac * X.shape[1]))
    abs_X = X.abs()
    topk_idx = abs_X.topk(k, dim=1).indices
    mask = torch.zeros_like(X)
    mask.scatter_(1, topk_idx, 1.0)
    return X * mask


def _attention_arm_d_t(cue, Ks, codebook_d, ytrue, y, beta_base, beta_mults):
    """Arm D = MAX over a beta-sweep of softmax-attention recall@1.

    Real attention picks its temperature. The v1 cell locked beta=1/sqrt(d) which on d=768, M=1000 was too flat;
    softmax mass spread -> argmax-decode collapsed. v2 sweeps beta over {1,4,16,64} * (1/sqrt(d)) and takes max.
    Returns (max_recall, best_beta_mult, per_beta_recalls).
    """
    per_beta = []
    for bm in beta_mults:
        beta = bm * beta_base
        # logits chunked to bound memory at large M*Q
        lg = beta * (cue @ Ks.t())
        lg = lg - lg.max(dim=1, keepdim=True).values
        w = torch.softmax(lg, dim=1)
        readout = w @ codebook_d[y]
        pred = _decode_t(readout, codebook_d)
        rec = float((pred == ytrue).float().mean().item())
        per_beta.append((float(bm), rec))
    best_bm, best_rec = max(per_beta, key=lambda t: t[1])
    return best_rec, best_bm, per_beta


def _arms_torch(Kp_np, y_np, seed_for_arms):
    """All 6 arms on torch.cuda when available. Inputs are numpy (encoder output); we move to device here."""
    dev = _torch_device()
    Kp = torch.from_numpy(Kp_np).to(dev, dtype=torch.float32)
    y = torch.from_numpy(y_np.astype(np.int64)).to(dev)
    M, d = Kp.shape
    dp = EXPAND * d

    g = np.random.default_rng(seed_for_arms)
    qidx_np = np.arange(M) if M <= MAX_Q else np.sort(g.choice(M, MAX_Q, replace=False))
    qidx = torch.from_numpy(qidx_np.astype(np.int64)).to(dev)
    noise_np = (SIGMA * g.standard_normal((len(qidx_np), d))).astype(np.float32)
    noise = torch.from_numpy(noise_np).to(dev)

    Ks = _norm_t(Kp) * math.sqrt(d)
    cue = Ks.index_select(0, qidx) + noise
    ytrue = y.index_select(0, qidx)

    # codebook d (for raw + attention)
    cb_d_np = _np_norm(g.standard_normal((C, d)).astype(np.float32))
    cb_d = torch.from_numpy(cb_d_np).to(dev)

    # ARM1_RAW: dense d-dim superposition store (the C1 kill-gate measurement).
    W_raw = (cb_d[y].t() @ Ks)
    pred_raw = _decode_t(cue @ W_raw.t(), cb_d)
    arm1_raw = float((pred_raw == ytrue).float().mean().item())

    # ARM A: cerebellar sparse-fan-in -> kWTA -> superposition (d' codebook).
    cb_dp_np = _np_norm(g.standard_normal((C, dp)).astype(np.float32))
    cb_dp = torch.from_numpy(cb_dp_np).to(dev)
    Sf_np = _sparse_fanin_np(d, dp, K_FANIN, g)
    Sf = torch.from_numpy(Sf_np).to(dev)
    Kexp = _kwta_t(Ks @ Sf.t(), KWTA_FRAC)
    cue_exp = _kwta_t(cue @ Sf.t(), KWTA_FRAC)
    WA = (cb_dp[y].t() @ Kexp)
    pred_A = _decode_t(cue_exp @ WA.t(), cb_dp)
    arm_A = float((pred_A == ytrue).float().mean().item())

    # ARM A': dense-Gaussian fan-in control.
    Sd_np = (g.standard_normal((dp, d)).astype(np.float32) * (1.0 / math.sqrt(d)))
    Sd = torch.from_numpy(Sd_np).to(dev)
    KexpD = _kwta_t(Ks @ Sd.t(), KWTA_FRAC)
    cueD = _kwta_t(cue @ Sd.t(), KWTA_FRAC)
    WAp = (cb_dp[y].t() @ KexpD)
    pred_Ap = _decode_t(cueD @ WAp.t(), cb_dp)
    arm_Ap = float((pred_Ap == ytrue).float().mean().item())

    # ARM B_fly_lsh: median-subtract + sparse random proj + WTA top-k -> tag-overlap argmax.
    Pf_np = ((g.random((dp, d)).astype(np.float32) < FLY_NONZERO).astype(np.float32)
             * g.standard_normal((dp, d)).astype(np.float32))
    # fly-LSH tags: use numpy median over the actual key matrix (deterministic), then move to torch
    Ks_np_local = Ks.detach().cpu().numpy()
    cue_np_local = cue.detach().cpu().numpy()
    Kt_np = _flylsh_tags_np(Ks_np_local, Pf_np, FLY_TOPK)
    Qt_np = _flylsh_tags_np(cue_np_local, Pf_np, FLY_TOPK)
    Kt = torch.from_numpy(Kt_np.astype(np.float32)).to(dev)
    Qt = torch.from_numpy(Qt_np.astype(np.float32)).to(dev)
    sim_fly = Qt @ Kt.t()
    pred_fly_idx = torch.argmax(sim_fly, dim=1)
    arm_B_fly_lsh = float((y.index_select(0, pred_fly_idx) == ytrue).float().mean().item())

    # ARM B_charikar: hyperplane signs (random Gaussian normals; binary signed sketches).
    Hc_np = g.standard_normal((dp, d)).astype(np.float32)
    Hc = torch.from_numpy(Hc_np).to(dev)
    Kc = torch.sign(Ks @ Hc.t())
    Qc = torch.sign(cue @ Hc.t())
    sim_c = Qc @ Kc.t()
    pred_c_idx = torch.argmax(sim_c, dim=1)
    arm_B_charikar = float((y.index_select(0, pred_c_idx) == ytrue).float().mean().item())

    # ARM C: compose sparse-fan-in expand -> fly-LSH on the expanded code.
    Pc_np = (g.random((dp, dp)).astype(np.float32) < FLY_NONZERO).astype(np.float32)
    Kexp_np_local = Kexp.detach().cpu().numpy()
    cue_exp_np_local = cue_exp.detach().cpu().numpy()
    Ktc_np = _flylsh_tags_np(Kexp_np_local, Pc_np, FLY_TOPK)
    Qtc_np = _flylsh_tags_np(cue_exp_np_local, Pc_np, FLY_TOPK)
    Ktc = torch.from_numpy(Ktc_np.astype(np.float32)).to(dev)
    Qtc = torch.from_numpy(Qtc_np.astype(np.float32)).to(dev)
    sim_c2 = Qtc @ Ktc.t()
    pred_c2_idx = torch.argmax(sim_c2, dim=1)
    arm_C = float((y.index_select(0, pred_c2_idx) == ytrue).float().mean().item())

    # ARM D: attention upper-bound with BETA SWEEP (the v2 meter calibration).
    beta_base = 1.0 / math.sqrt(d)
    arm_D, arm_D_best_bm, arm_D_per_beta = _attention_arm_d_t(cue, Ks, cb_d, ytrue, y, beta_base, BETA_MULT_SWEEP)

    # storage bits (informational; same as v1)
    storage_bits = float(FLY_TOPK * math.log2(dp))

    # cleanup; clear cuda cache as we move M points
    if dev.type == "cuda":
        del Kp, y, cue, Ks, cb_d, cb_dp, Sf, Sd, Kexp, cue_exp, WA, WAp, Hc, Kc, Qc, Kt, Qt, Ktc, Qtc, W_raw
        torch.cuda.empty_cache()

    return {
        "arm1_raw": round(arm1_raw, 4),
        "arm_A": round(arm_A, 4),
        "arm_Ap_dense": round(arm_Ap, 4),
        "arm_B_fly_lsh": round(arm_B_fly_lsh, 4),
        "arm_B_charikar": round(arm_B_charikar, 4),
        "arm_C": round(arm_C, 4),
        "arm_D": round(arm_D, 4),
        "arm_D_best_beta_mult": arm_D_best_bm,
        "arm_D_per_beta": [(round(bm, 2), round(r, 4)) for bm, r in arm_D_per_beta],
        "B_storage_bits_per_mem": round(storage_bits, 1),
    }


# ---------- pure-numpy variant for --self-test (no GPU dependency) ----------

def _arms_np(Kp, y_np, g, seed):
    d = Kp.shape[1]
    M = len(Kp)
    dp = EXPAND * d
    qidx = np.arange(M) if M <= MAX_Q else np.sort(g.choice(M, MAX_Q, replace=False))
    noise = SIGMA * g.standard_normal((len(qidx), d)).astype(np.float32)
    Ks = _np_norm(Kp) * np.sqrt(d)
    cue = Ks[qidx] + noise
    ytrue = y_np[qidx]
    cb_d = _np_norm(g.standard_normal((C, d)).astype(np.float32))
    W_raw = cb_d[y_np].T @ Ks
    arm1_raw = float((_decode_np(cue @ W_raw.T, cb_d) == ytrue).mean())
    # Arm D with beta sweep
    beta_base = 1.0 / np.sqrt(d)
    per_beta = []
    for bm in BETA_MULT_SWEEP:
        beta = bm * beta_base
        lg = beta * (cue @ Ks.T)
        lg -= lg.max(1, keepdims=True)
        w = np.exp(lg)
        w /= w.sum(1, keepdims=True)
        readout = w @ cb_d[y_np]
        rec = float((_decode_np(readout, cb_d) == ytrue).mean())
        per_beta.append((float(bm), rec))
    best_bm, arm_D = max(per_beta, key=lambda t: t[1])
    return {"arm1_raw": float(arm1_raw), "arm_D": float(arm_D),
            "arm_D_best_beta_mult": best_bm, "arm_D_per_beta": per_beta}


# ---------- encoder + facts (only used in full/smoke, not self-test) ----------

def _facts_and_encode(seed, n_total):
    """Hoisted: facts + encoder forward pass.

    Substrate-only at inference (encoder is a SETUP-TIME hidden-state extractor; no LLM forward at verdict time).
    Only encoder runs once per seed.

    IMPORTANT: the flagship module sets its OWN module-level ENCODER based on its OWN RUN_MODE detection (defaulting
    to pythia-2.8b if HDLAB_RUN_MODE is unset). We override here so v2's RUN_MODE controls which encoder runs.
    """
    # Set HDLAB_RUN_MODE BEFORE import so flagship module picks the right encoder at its module init.
    os.environ["HDLAB_RUN_MODE"] = RUN_MODE
    import experiments.exp_flagship_sparse_projected_KV_PROBE_whiten_before_topk_v1 as _probe
    # Belt-and-suspenders: explicitly override the flagship module's ENCODER to match v2's choice.
    _probe.ENCODER = ENCODER
    _probe.ENC_DTYPE = torch.float16 if torch.cuda.is_available() else torch.float32
    # Re-resolve helpers from the (possibly re-imported) module.
    make_facts = _probe.make_facts
    encode = _probe.encode
    train_contrastive = _probe.train_contrastive
    keys, cues = make_facts(n_total)
    K = encode(keys)
    Q = encode(cues)
    g = np.random.default_rng(seed)
    perm = g.permutation(n_total)
    tr = perm[:TRAIN_M]
    ho = perm[TRAIN_M:]
    W = train_contrastive(K[tr], Q[tr], PROJ_DIM, TRAIN_STEPS, seed)
    Kp_all = (K[ho] @ W).astype(np.float32)
    return Kp_all


def run_unit(seed):
    n_total = max(M_SWEEP) + TRAIN_M
    print("[seed=%d] encoder=%s n_total=%d (encoding once; substrate-only at inference)" % (seed, ENCODER, n_total), flush=True)
    Kp_all = _facts_and_encode(seed, n_total)
    g = np.random.default_rng(seed * 7 + 1)
    by_M = {}
    for M in M_SWEEP:
        y = g.integers(0, C, M).astype(np.int64)
        arms_seed = seed * 7 + M
        a = _arms_torch(Kp_all[:M].astype(np.float32), y, arms_seed)
        by_M["M%d" % M] = a
        print(("[seed=%d M=%d] raw=%.3f A=%.3f(Ap=%.3f) B_fly=%.3f B_char=%.3f C=%.3f "
               "D=%.3f(best_beta_x=%s) per_beta=%s") % (
            seed, M, a["arm1_raw"], a["arm_A"], a["arm_Ap_dense"],
            a["arm_B_fly_lsh"], a["arm_B_charikar"], a["arm_C"],
            a["arm_D"], a["arm_D_best_beta_mult"], a["arm_D_per_beta"]
        ), flush=True)
    return {"seed": seed, "by_M": by_M}


def _cv(values):
    if not values:
        return 0.0
    mean = float(np.mean(values))
    if abs(mean) < 1e-9:
        return 0.0
    return float(np.std(values) / abs(mean))


def compute_verdict(units):
    if not units:
        return ("HARD_FAIL", "no results", {})
    M_max = max(M_SWEEP) if M_SWEEP else 1000

    def vals(M, key):
        return [u["by_M"]["M%d" % M][key] for u in units if "M%d" % M in u["by_M"]]

    def med(M, key):
        v = vals(M, key)
        return float(np.median(v)) if v else 0.0

    raw_at_max = med(M_max, "arm1_raw")
    A = med(M_max, "arm_A")
    Ap = med(M_max, "arm_Ap_dense")
    Bfly = med(M_max, "arm_B_fly_lsh")
    Bchar = med(M_max, "arm_B_charikar")
    Cc = med(M_max, "arm_C")
    D = med(M_max, "arm_D")

    cv_Bfly = _cv(vals(M_max, "arm_B_fly_lsh"))
    cv_Bchar = _cv(vals(M_max, "arm_B_charikar"))
    cv_D = _cv(vals(M_max, "arm_D"))

    rel_Bfly = Bfly / D if D > 1e-6 else 0.0
    rel_Bchar = Bchar / D if D > 1e-6 else 0.0
    rel_C = Cc / D if D > 1e-6 else 0.0

    detail = {
        "M_eval": M_max,
        "arm1_raw": raw_at_max,
        "arm_A": A,
        "arm_Ap_dense": Ap,
        "arm_B_fly_lsh": Bfly,
        "arm_B_charikar": Bchar,
        "arm_C": Cc,
        "arm_D_meter": D,
        "cv_arm_B_fly_lsh": round(cv_Bfly, 4),
        "cv_arm_B_charikar": round(cv_Bchar, 4),
        "cv_arm_D": round(cv_D, 4),
        "rel_B_fly_lsh_over_D": round(rel_Bfly, 4),
        "rel_B_charikar_over_D": round(rel_Bchar, 4),
        "rel_C_over_D": round(rel_C, 4),
        "n_seeds": len(units),
        "bands": {
            "HP_LSH": BAND_HP_LSH, "HP_PARTIAL_LSH": BAND_HP_PARTIAL_LSH,
            "METER_FLOOR": BAND_METER_FLOOR, "CV_HP": BAND_CV_HP,
            "CV_PARTIAL": BAND_CV_PARTIAL, "HF_LSH": BAND_HF_LSH,
            "REL_PROMISE": BAND_REL_PROMISE, "Q_SATURATION": BAND_Q_SATURATION,
        },
        "CONFIG_VERSION": CONFIG_VERSION,
        "cites": [
            "anisotropy_rescue_4arm_sweep_v1_gpu",
            "dense_kv_whitening_revival_v1_gpu",
            "Litwin-Kumar2017_cerebellar",
            "fly_LSH_Dasgupta2017",
            "Charikar2002_hyperplane_lsh",
            "research_deep_dive_partial_open_capabilities_2026-06-25",
        ],
    }

    # Per-arm summary string (Fix #28: per-arm metrics, NOT verdict-msg framing)
    summ = (
        "raw=%.3f | A=%.3f(Ap=%.3f) Bfly=%.3f Bchar=%.3f C=%.3f | D_meter=%.3f | "
        "cv_Bfly=%.3f cv_Bchar=%.3f cv_D=%.3f | rel_Bfly/D=%.3f rel_Bchar/D=%.3f"
    ) % (raw_at_max, A, Ap, Bfly, Bchar, Cc, D, cv_Bfly, cv_Bchar, cv_D, rel_Bfly, rel_Bchar)

    # Q-discipline: suspect saturation flag if any arm hits >= 0.995
    q_flags = []
    for name, val in [("Bfly", Bfly), ("Bchar", Bchar), ("C", Cc), ("D", D)]:
        if val >= BAND_Q_SATURATION:
            q_flags.append("[Q-DISCIPLINE: %s=%.4f >= %.3f -- suspect saturation; corpus-may-be-easy; honest under-claim]" % (name, val, BAND_Q_SATURATION))
    q_note = " ".join(q_flags) + (" " if q_flags else "")

    # METER status FIRST (the v2 design rule: meter calibration governs interpretability)
    meter_ok = D >= BAND_METER_FLOOR
    detail["meter_calibrated"] = bool(meter_ok)

    # HARD_PASS variants (require meter calibrated AND absolute floor met AND cv tight)
    if meter_ok:
        # HARD_PASS variant 1: fly-LSH absolute
        if Bfly >= BAND_HP_LSH and cv_Bfly <= BAND_CV_HP:
            return ("HARD_PASS",
                    ("CHAIN-GRADE-CANDIDATE: ARM B_fly_lsh = %.3f >= %.2f at M=%d AND cv = %.3f <= %.2f across %d seeds AND meter D = %.3f >= %.2f -> cerebellar/fly-LSH-style sparse-fan-in rescues anisotropy collapse on real Pythia keys (raw collapsed to %.3f). %s%s"
                     ) % (Bfly, BAND_HP_LSH, M_max, cv_Bfly, BAND_CV_HP, len(units), D, BAND_METER_FLOOR, raw_at_max, q_note, summ),
                    detail)
        # HARD_PASS variant 2: Charikar absolute
        if Bchar >= BAND_HP_LSH and cv_Bchar <= BAND_CV_HP:
            return ("HARD_PASS",
                    ("CHAIN-GRADE-CANDIDATE: ARM B_charikar = %.3f >= %.2f at M=%d AND cv = %.3f <= %.2f across %d seeds AND meter D = %.3f >= %.2f -> Charikar hyperplane-LSH binary sketches rescue anisotropy collapse on real Pythia keys (raw collapsed to %.3f; v1 smoke 0.982 SURVIVES at full). %s%s"
                     ) % (Bchar, BAND_HP_LSH, M_max, cv_Bchar, BAND_CV_HP, len(units), D, BAND_METER_FLOOR, raw_at_max, q_note, summ),
                    detail)
        # HARD_PASS_PARTIAL_LSH variant
        if Bfly >= BAND_HP_PARTIAL_LSH and cv_Bfly <= BAND_CV_PARTIAL:
            return ("HARD_PASS",
                    ("PARTIAL_RESCUE: ARM B_fly_lsh = %.3f >= %.2f at M=%d AND cv = %.3f <= %.2f AND meter D = %.3f >= %.2f -> partial sparse-fan-in rescue at this regime (raw collapsed to %.3f). %s%s"
                     ) % (Bfly, BAND_HP_PARTIAL_LSH, M_max, cv_Bfly, BAND_CV_PARTIAL, D, BAND_METER_FLOOR, raw_at_max, q_note, summ),
                    detail)
        if Bchar >= BAND_HP_PARTIAL_LSH and cv_Bchar <= BAND_CV_PARTIAL:
            return ("HARD_PASS",
                    ("PARTIAL_RESCUE: ARM B_charikar = %.3f >= %.2f at M=%d AND cv = %.3f <= %.2f AND meter D = %.3f >= %.2f -> partial Charikar rescue (raw collapsed to %.3f). %s%s"
                     ) % (Bchar, BAND_HP_PARTIAL_LSH, M_max, cv_Bchar, BAND_CV_PARTIAL, D, BAND_METER_FLOOR, raw_at_max, q_note, summ),
                    detail)
        # HARD_FAIL: both LSH arms below the fail band
        if Bfly <= BAND_HF_LSH and Bchar <= BAND_HF_LSH:
            return ("HARD_FAIL",
                    ("HARD_FAIL_LSH_DOESNT_HOLD: BOTH ARM B_fly_lsh = %.3f AND ARM B_charikar = %.3f <= %.2f at M=%d (meter D = %.3f calibrated) -> v1 smoke 0.982 was an artifact / single-seed noise / pythia-160m vs pythia-2.8b regime shift. LSH does NOT rescue anisotropy at full scale on real Pythia-2.8b keys. raw=%.3f. %s"
                     ) % (Bfly, Bchar, BAND_HF_LSH, M_max, D, raw_at_max, summ),
                    detail)
        # Otherwise MIDDLE_BAND (meter OK but neither arm clears HP nor falls below HF)
        return ("MIDDLE_BAND",
                ("MEASURED_MECHANISM: meter D = %.3f calibrated, neither LSH arm clears HARD_PASS bar (Bfly=%.3f Bchar=%.3f vs HP=%.2f) nor falls below HARD_FAIL (HF=%.2f). Mechanism partially helps vs raw=%.3f but not at production-grade. %s%s"
                 ) % (D, Bfly, Bchar, BAND_HP_LSH, BAND_HF_LSH, raw_at_max, q_note, summ),
                detail)

    # METER NOT CALIBRATED — check MIDDLE_BAND_RELATIVE_PROMISE (the safety net)
    rel_pass = (rel_Bfly >= BAND_REL_PROMISE) or (rel_Bchar >= BAND_REL_PROMISE)
    if rel_pass:
        # Report which arm passed relatively
        winners = []
        if rel_Bfly >= BAND_REL_PROMISE:
            winners.append("B_fly_lsh/D=%.3f" % rel_Bfly)
        if rel_Bchar >= BAND_REL_PROMISE:
            winners.append("B_charikar/D=%.3f" % rel_Bchar)
        return ("MIDDLE_BAND",
                ("MIDDLE_BAND_RELATIVE_PROMISE: meter D = %.3f < %.2f (under-calibrated even with beta sweep %s), BUT relative ratio %s >= %.2f -> mechanism is real RELATIVE to attention upper-bound; meter regime needs revisiting (try larger encoder / smaller M / different beta range). raw=%.3f. %s%s"
                 ) % (D, BAND_METER_FLOOR, BETA_MULT_SWEEP, " AND ".join(winners), BAND_REL_PROMISE, raw_at_max, q_note, summ),
                detail)

    # METER NOT CALIBRATED AND no relative-promise
    return ("MIDDLE_BAND",
            ("METER_UNDER_CALIBRATED: meter D = %.3f < %.2f even with beta sweep %s; relative ratios Bfly/D=%.3f Bchar/D=%.3f also below %.2f -> cell uninterpretable for absolute or relative claims at this regime. Redesign meter (try encoder upgrade, smaller M, broader beta range, or alternative upper-bound mechanism). raw=%.3f. %s"
             ) % (D, BAND_METER_FLOOR, BETA_MULT_SWEEP, rel_Bfly, rel_Bchar, BAND_REL_PROMISE, raw_at_max, summ),
            detail)


def _selftest():
    """Self-test: (a) anisotropic raw collapses; (b) attention beta-sweep recovers >= 0.80 on isotropic synthetic.

    The v1 cell had a meter bug at smoke regime; v2 catches it here BEFORE dispatch by asserting Arm D >= 0.80
    on a controlled isotropic regime where attention SHOULD trivially work. If the beta sweep fails to recover,
    self-test fails and the cell does not dispatch.
    """
    g = np.random.default_rng(0)
    d = 128
    M = 1500
    # (a) anisotropic: common-mode -> raw superposition collapses (decode meter check)
    sig = g.standard_normal((M, d)).astype(np.float32)
    mu = g.standard_normal((1, d)).astype(np.float32) * 3.0
    Kp = sig + mu
    y = g.integers(0, C, M).astype(np.int64)
    r = _arms_np(Kp, y, np.random.default_rng(1), 1)
    assert r["arm1_raw"] < 0.30, "raw superposition must collapse on anisotropic keys (got %.3f)" % r["arm1_raw"]

    # (b) ISOTROPIC: attention with beta-sweep MUST hit >= 0.80 -- this is the v2 meter-calibration assertion.
    # At M=400, d=128 isotropic, attention should be near-perfect at some beta in the sweep. If it doesn't, the
    # meter design is broken and the cell aborts before dispatch.
    iso = _np_norm(g.standard_normal((400, d)).astype(np.float32))
    yi = g.integers(0, C, 400).astype(np.int64)
    ri = _arms_np(iso, yi, np.random.default_rng(2), 2)
    assert ri["arm1_raw"] > 0.5, "isotropic small-M raw decode meter must work (got %.3f)" % ri["arm1_raw"]
    assert ri["arm_D"] >= 0.80, (
        "v2 meter-calibration assertion: attention beta-sweep must hit >= 0.80 on isotropic M=400 d=128 synthetic "
        "(got %.3f via best beta_mult=%s; per_beta=%s). If this fails, the v1 meter bug is reproduced and the "
        "cell aborts. Fix: widen BETA_MULT_SWEEP or pick smaller smoke regime."
    ) % (ri["arm_D"], ri["arm_D_best_beta_mult"], ri["arm_D_per_beta"])

    print(
        "[selftest] PASS: anisotropic raw collapses (%.3f) + isotropic raw works (%.3f) + isotropic attention beta-sweep meter calibrated (D=%.3f best_beta_x=%s)"
        % (r["arm1_raw"], ri["arm1_raw"], ri["arm_D"], ri["arm_D_best_beta_mult"]),
        flush=True,
    )


if __name__ == "__main__":
    _selftest()
    if _ARGS.self_test:
        raise SystemExit(0)
    print("[config] %s mode=%s | %s" % (ANCHOR_NAME, RUN_MODE, CONFIG_VERSION), flush=True)
    # Fix #24: log GPU availability + active use up front (so verdict-time evidence proves GPU touched).
    gpu_avail = torch.cuda.is_available()
    gpu_name = torch.cuda.get_device_name(0) if gpu_avail else "cpu"
    print("[gpu] available=%s name=%s" % (gpu_avail, gpu_name), flush=True)

    out_dir = get_output_dir(ANCHOR_NAME)
    run_cfg = {"run_mode": RUN_MODE, "proj": PROJ_DIM, "expand": EXPAND, "kfanin": K_FANIN,
               "schema": "4arm-rescue-v2-calibrated-meter", "seeds": SEEDS, "M": M_SWEEP}
    t0 = time.time()
    for seed in SEEDS:
        key = "s%d" % seed
        if key in aggregate_partials(out_dir, [key], run_config=run_cfg):
            print("[ckpt] %s done; skip" % key, flush=True)
            continue
        write_partial_key(out_dir, key, run_unit(seed))
    units = list(aggregate_partials(out_dir, ["s%d" % sd for sd in SEEDS], run_config=run_cfg).values())
    verdict, msg, detail = compute_verdict(units)
    print("\n[VERDICT] " + msg, flush=True)

    # GPU mem allocated check (Fix #24 evidence)
    gpu_mem_alloc_mb = 0.0
    if gpu_avail:
        try:
            gpu_mem_alloc_mb = float(torch.cuda.max_memory_allocated() / (1024 * 1024))
        except Exception:
            gpu_mem_alloc_mb = 0.0

    metrics = {
        "anchor_name": ANCHOR_NAME,
        "verdict": verdict,
        "verdict_msg": msg,
        "summary": msg,
        "run_mode": RUN_MODE,
        "model": ENCODER,
        "proj_dim": PROJ_DIM,
        "M_SWEEP": M_SWEEP,
        "n_seeds": len(units),
        "seeds": SEEDS,
        "detail": detail,
        "gpu_avail": bool(gpu_avail),
        "gpu_name": gpu_name,
        "gpu_max_mem_alloc_mb": round(gpu_mem_alloc_mb, 1),
        "metrics_source": "measured_gpu_anisotropy_rescue_4arm_v2_calibrated_meter",
        "per_unit": units,
        "elapsed_s": time.time() - t0,
    }
    write_metrics(out_dir, metrics, units)
    print("[metrics] written to %s" % (out_dir / "metrics.json"), flush=True)
