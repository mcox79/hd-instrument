"""ANISOTROPY-RESCUE M=100k adversarial-similarity-keys v2_batched -- BATCHED MATMUL OOM-FIX of v1.

PROMOTION CONTEXT (USER 2026-06-25):
v1 (same anchor minus _v2_batched) CRASHED with CUDA OOM at line 297:
    sim_c2 = Qtc @ Ktc.t()
Remote stderr trace: 6.47 GiB allocated, 230 MiB reserved, 0 free; allocator wanted 288 MiB on 8GB GPU.

Per-arm partial evidence from before crash (M=10k slice seed 11):
    raw=0.021, A=?, Ap=?, B_fly_lsh=0.189, B_charikar=0.193, AB_CTRL=0.240
Preliminary anti-LSH signal: AB_CONTROL > both LSH arms at M=10k adversarial keys.
v2_batched will COMPLETE the M sweep at M=50k and M=100k to give us the discriminator
Skunkworks recommended -- whether the v1 partial signal holds at substrate-product scale.

OOM root cause = MAX_Q x M cosine-sim matmuls accumulating GPU residency:
  sim_fly  = Qt   (MAX_Q, dp) @ Kt.t()   (dp, M)  -> (MAX_Q, M) = 1500*100k*4 = 600 MB
  sim_c    = Qc   (MAX_Q, dp) @ Kc.t()   (dp, M)  -> (MAX_Q, M) = 600 MB
  sim_ab   = Qab_n(MAX_Q, dp) @ Kab_n.t()(dp, M)  -> (MAX_Q, M) = 600 MB
  sim_c2   = Qtc  (MAX_Q, dp) @ Ktc.t()  (dp, M)  -> (MAX_Q, M) = 600 MB  <-- crash point
  attn_D   = cue  (MAX_Q, d ) @ Ks.t()   (d , M)  -> (MAX_Q, M) = 600 MB  x len(BETA_MULT_SWEEP)=4
Plus K-side residents: Kt, Kc, Kab_n, Ktc each ~ M*dp*4 = 100k*3840*4 = 1.46 GB.
At M=100k all four K-side tensors resident simultaneously = ~6 GB before any sim_* computed.

FIX (this cell): chunk Q-dim so per-batch sim_chunk = q_batch x M output stays bounded;
free K-side per-arm tensors aggressively after producing pred_*_idx. Default Q_BATCH=200
keeps per-chunk output = 200*100k*4 = 80 MB. Same NUMERIC RESULT as v1 (correctness asserted
in self-test). Same arms / same M sweep / same seeds / same bands -- ONLY memory layout changes.

EXPECTED OUTCOMES (same band logic as v1):
  HARD_PASS_CHAIN_GRADE_CONFIRMED_FLY_LSH:    fly >= 0.85 AND raw <= 0.30 AND fly beats Charikar by >= 0.05 AND fly beats AB_CONTROL by >= 0.10
  HARD_PASS_CHAIN_GRADE_CONFIRMED_CHARIKAR:   same but Charikar wins
  HARD_PASS_BOTH_LSH_RESCUE:                  fly AND Charikar BOTH >= 0.85 AND both beat control by >= 0.10
  MIDDLE_BAND_PARTIAL_RESCUE:                 fly and/or Charikar in [0.50, 0.85); control beats RAW by >= 0.20
  HARD_FAIL_RESCUE_DOESNT_HOLD:               fly AND Charikar BOTH <= 0.30 at M=100k
  HARD_FAIL_CONTROL_ALSO_PASSES:              AB_CONTROL >= 0.85 at M=100k  <-- v1 partial M=10k signal suggested this

Q-DISCIPLINE guards: same as v1 -- any arm >= 0.995 at M=100k -> BIAS-Q flag.
META_M6: RAW arm baseline derived in-cell at adversarial regime (NOT copied from v2).
META_M7: smoke matches full along capacity-sensitive dimensions.

GPU REQUIRED (Fix #24): torch.cuda actively used; encoder hoisted; matmuls on device; BATCHED.
ASCII only. Substrate-only at inference (encoder is setup-time hidden-state extractor).
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

ANCHOR_NAME = "substrate_anisotropy_rescue_M100k_adversarial_similarity_keys_v2_batched"

_P = argparse.ArgumentParser()
_P.add_argument("--self-test", action="store_true", dest="self_test")
_P.add_argument("--smoke", action="store_true")
_ARGS, _ = _P.parse_known_args()
RUN_MODE = "smoke" if (_ARGS.smoke or _ARGS.self_test) else os.environ.get("HDLAB_RUN_MODE", "full")

# CAPACITY-SENSITIVE config (matches v1; capacity-sensitive dims do NOT change between smoke/full)
PROJ_DIM = 768
C = 256
EXPAND = 5              # d' = 5*d = 3840 at PROJ_DIM=768
K_FANIN = 5
KWTA_FRAC = 0.10
FLY_TOPK = 20
FLY_NONZERO = 0.05
SIGMA = 0.1
MAX_Q = 1500
BETA_MULT_SWEEP = [1.0, 4.0, 16.0, 64.0]
AB_CONTROL_NBITS = EXPAND * PROJ_DIM  # 3840

# NEW v2_batched: Q-chunk size for cosine-sim argmax. q_batch=200 keeps per-chunk
# output = q_batch * M_max * 4 = 200 * 100000 * 4 = 80 MB << 8 GB GPU budget.
# Correctness: batched argmax is IDENTICAL to monolithic argmax when ties broken
# deterministically (PyTorch argmax returns first-occurrence index per row, which
# is row-local and identical between batched and monolithic computations).
Q_BATCH = 200

# Adversarial-similarity construction (matches v1)
WINDOW_TOKENS = 16
CUE_SHIFT = 1

if RUN_MODE == "full":
    ENCODER = "EleutherAI/pythia-2.8b"
    SEEDS = [11, 13, 19]
    M_SWEEP = [10000, 50000, 100000]
    TRAIN_M = 10000
    TRAIN_STEPS = 600
    N_TOKENS_BUDGET = 110000
else:
    ENCODER = "EleutherAI/pythia-160m"
    SEEDS = [11]
    M_SWEEP = [500, 2000]
    TRAIN_M = 500
    TRAIN_STEPS = 100
    N_TOKENS_BUDGET = 2200

# PROSPECTIVE BANDS (LOCKED AT MODULE INIT; SAME LOGIC AS v1)
BAND_HP_CHAIN_GRADE = 0.85
BAND_HP_RAW_CEILING = 0.30
BAND_HP_BEAT_PEER = 0.05
BAND_HP_BEAT_CONTROL = 0.10
BAND_HP_BOTH_LSH = 0.85
BAND_MB_RESCUE_LOW = 0.50
BAND_MB_RESCUE_HIGH = 0.85
BAND_MB_CONTROL_BEATS_RAW = 0.20
BAND_HF_RESCUE = 0.30
BAND_HF_CONTROL_ALSO = 0.85
BAND_CV_HP = 0.05
BAND_Q_SATURATION = 0.995
BAND_METER_FLOOR = 0.50

assert 0.0 < BAND_HF_RESCUE < BAND_MB_RESCUE_LOW < BAND_MB_RESCUE_HIGH <= BAND_HP_CHAIN_GRADE < BAND_Q_SATURATION < 1.0, "bands ordered"
assert 0.0 < BAND_HP_BEAT_PEER < BAND_HP_BEAT_CONTROL < 1.0, "discriminator margins ordered"
assert 0.0 < BAND_HP_RAW_CEILING < BAND_MB_CONTROL_BEATS_RAW + BAND_HP_RAW_CEILING < BAND_MB_RESCUE_HIGH, "raw-ceiling sane"
assert 0.0 < BAND_METER_FLOOR < 1.0, "meter floor sane"
assert BAND_HP_BOTH_LSH <= BAND_HP_CHAIN_GRADE, "joint-pass floor not above single-pass floor"
assert BAND_HF_CONTROL_ALSO >= BAND_HP_CHAIN_GRADE, "control-also-passes failsafe sanity"
assert 1 <= Q_BATCH <= MAX_Q, "Q_BATCH must be in [1, MAX_Q]"

CONFIG_VERSION = (
    "v2_batched_M100k_adversarial(A-cerebellar-K%d/Ap-dense/B_fly_lsh/B_charikar/AB_control/C-compose/D-attn-beta-sweep) | "
    "expand%dx kwta%.2f flytopk%d window%dt shift%d q_batch%d | beta_mults=%s | seeds=%s | M=%s | FP32_GPU | bands locked | OOM-FIX of v1"
) % (K_FANIN, EXPAND, KWTA_FRAC, FLY_TOPK, WINDOW_TOKENS, CUE_SHIFT, Q_BATCH, BETA_MULT_SWEEP, SEEDS, M_SWEEP)


def _np_norm(X):
    return (X / (np.linalg.norm(X, axis=-1, keepdims=True) + 1e-8)).astype(np.float32)


def _decode_np(R, codebook):
    return np.argmax(_np_norm(R) @ codebook.T, axis=1)


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


# ---------- torch.cuda accelerated arms ----------

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


def _batched_argmax_sim(Q, K, q_batch=Q_BATCH):
    """OOM-FIX HELPER (v2_batched). Returns argmax over K for each row of Q via Q @ K.t().

    Mathematically equivalent to torch.argmax(Q @ K.t(), dim=1) but bounds peak
    memory by chunking Q-rows so per-chunk output stays at q_batch*M*4 bytes.
    Frees per-chunk sim tensor immediately. Same numeric result for ties because
    PyTorch argmax returns row-local first-occurrence (independent of how Q is split).

    Args:
        Q: (n_q, d_h) float tensor on dev
        K: (n_k, d_h) float tensor on dev
        q_batch: number of Q rows per matmul chunk
    Returns:
        (n_q,) int64 tensor of argmax indices over K-rows
    """
    n_q = Q.shape[0]
    out = torch.empty(n_q, dtype=torch.int64, device=Q.device)
    Kt = K.t().contiguous()  # avoid re-transposing per chunk
    for i in range(0, n_q, q_batch):
        j = min(i + q_batch, n_q)
        sim_chunk = Q[i:j] @ Kt
        out[i:j] = torch.argmax(sim_chunk, dim=1)
        del sim_chunk
    return out


def _batched_attn_recall(cue, Ks, codebook_d, y, ytrue, beta, q_batch=Q_BATCH):
    """OOM-FIX HELPER (v2_batched). Softmax-attention recall, batched over cue rows.

    Equivalent to:
        lg = beta * (cue @ Ks.t())
        lg = lg - lg.max(dim=1, keepdim=True).values
        w = torch.softmax(lg, dim=1)
        readout = w @ codebook_d[y]
        pred = _decode_t(readout, codebook_d)
        return (pred == ytrue).float().mean()

    With chunking over cue rows. codebook_d[y] is materialized ONCE (M x C-shape) outside loop
    to avoid repeated gather; if memory still tight further batching is needed but at M=100k
    codebook_d[y] is M*d = 100k*768*4 = 300 MB, acceptable.
    """
    n_q = cue.shape[0]
    Kst = Ks.t().contiguous()
    Vy = codebook_d[y]                  # (M, d)  ~ 300 MB at M=100k
    correct = 0
    for i in range(0, n_q, q_batch):
        j = min(i + q_batch, n_q)
        lg = beta * (cue[i:j] @ Kst)    # (q_batch, M)  ~ 80 MB at M=100k
        lg = lg - lg.max(dim=1, keepdim=True).values
        w = torch.softmax(lg, dim=1)
        readout = w @ Vy                # (q_batch, d)
        pred = _decode_t(readout, codebook_d)
        correct += int((pred == ytrue[i:j]).sum().item())
        del lg, w, readout
    del Vy, Kst
    return correct / n_q


def _attention_arm_d_t(cue, Ks, codebook_d, ytrue, y, beta_base, beta_mults):
    """Arm D = MAX over beta-sweep of softmax-attention recall@1. v2_batched: BATCHED."""
    per_beta = []
    for bm in beta_mults:
        beta = bm * beta_base
        rec = _batched_attn_recall(cue, Ks, codebook_d, y, ytrue, beta, q_batch=Q_BATCH)
        per_beta.append((float(bm), float(rec)))
    best_bm, best_rec = max(per_beta, key=lambda t: t[1])
    return best_rec, best_bm, per_beta


def _arms_torch(Kp_np, y_np, seed_for_arms):
    """8 arms on torch.cuda; v2_batched OOM-FIX = batched cosine-sim matmuls + aggressive per-arm K free."""
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

    cb_d_np = _np_norm(g.standard_normal((C, d)).astype(np.float32))
    cb_d = torch.from_numpy(cb_d_np).to(dev)

    # ARM RAW (small: cue @ W_raw.t() -> (MAX_Q, d); no batching needed)
    W_raw = (cb_d[y].t() @ Ks)
    pred_raw = _decode_t(cue @ W_raw.t(), cb_d)
    arm1_raw = float((pred_raw == ytrue).float().mean().item())
    del W_raw
    if dev.type == "cuda":
        torch.cuda.empty_cache()

    # ARM A: cerebellar sparse-fan-in -> kWTA -> superposition
    # Kexp is (M, dp) = 100k*3840*4 = 1.46 GB; we KEEP Kexp/cue_exp for ARM C reuse.
    cb_dp_np = _np_norm(g.standard_normal((C, dp)).astype(np.float32))
    cb_dp = torch.from_numpy(cb_dp_np).to(dev)
    Sf_np = _sparse_fanin_np(d, dp, K_FANIN, g)
    Sf = torch.from_numpy(Sf_np).to(dev)
    Kexp = _kwta_t(Ks @ Sf.t(), KWTA_FRAC)
    cue_exp = _kwta_t(cue @ Sf.t(), KWTA_FRAC)
    WA = (cb_dp[y].t() @ Kexp)
    pred_A = _decode_t(cue_exp @ WA.t(), cb_dp)
    arm_A = float((pred_A == ytrue).float().mean().item())
    del Sf, WA
    if dev.type == "cuda":
        torch.cuda.empty_cache()

    # ARM A': dense Gaussian fan-in control. KexpD/cueD are TRANSIENT (not needed past this block).
    Sd_np = (g.standard_normal((dp, d)).astype(np.float32) * (1.0 / math.sqrt(d)))
    Sd = torch.from_numpy(Sd_np).to(dev)
    KexpD = _kwta_t(Ks @ Sd.t(), KWTA_FRAC)
    cueD = _kwta_t(cue @ Sd.t(), KWTA_FRAC)
    WAp = (cb_dp[y].t() @ KexpD)
    pred_Ap = _decode_t(cueD @ WAp.t(), cb_dp)
    arm_Ap = float((pred_Ap == ytrue).float().mean().item())
    del Sd, KexpD, cueD, WAp
    if dev.type == "cuda":
        torch.cuda.empty_cache()

    # ARM B_fly_lsh: median-subtract + sparse random proj + WTA top-k -> tag-overlap argmax
    # BATCHED FIX: Qt @ Kt.t() was (MAX_Q, M) = 600 MB monolithic; batched -> 80 MB/chunk.
    Pf_np = ((g.random((dp, d)).astype(np.float32) < FLY_NONZERO).astype(np.float32)
             * g.standard_normal((dp, d)).astype(np.float32))
    Ks_np_local = Ks.detach().cpu().numpy()
    cue_np_local = cue.detach().cpu().numpy()
    Kt_np = _flylsh_tags_np(Ks_np_local, Pf_np, FLY_TOPK)
    Qt_np = _flylsh_tags_np(cue_np_local, Pf_np, FLY_TOPK)
    Kt = torch.from_numpy(Kt_np.astype(np.float32)).to(dev)
    Qt = torch.from_numpy(Qt_np.astype(np.float32)).to(dev)
    pred_fly_idx = _batched_argmax_sim(Qt, Kt, q_batch=Q_BATCH)
    arm_B_fly_lsh = float((y.index_select(0, pred_fly_idx) == ytrue).float().mean().item())
    del Kt, Qt, pred_fly_idx
    if dev.type == "cuda":
        torch.cuda.empty_cache()

    # ARM B_charikar: hyperplane signs. BATCHED FIX same as B_fly_lsh.
    Hc_np = g.standard_normal((dp, d)).astype(np.float32)
    Hc = torch.from_numpy(Hc_np).to(dev)
    Kc = torch.sign(Ks @ Hc.t())
    Qc = torch.sign(cue @ Hc.t())
    del Hc
    pred_c_idx = _batched_argmax_sim(Qc, Kc, q_batch=Q_BATCH)
    arm_B_charikar = float((y.index_select(0, pred_c_idx) == ytrue).float().mean().item())
    del Kc, Qc, pred_c_idx
    if dev.type == "cuda":
        torch.cuda.empty_cache()

    # ARM_AB_CONTROL: dense Gaussian random hash. BATCHED FIX same.
    Hab_np = (g.standard_normal((AB_CONTROL_NBITS, d)).astype(np.float32)
              * (1.0 / math.sqrt(d)))
    Hab = torch.from_numpy(Hab_np).to(dev)
    Kab = Ks @ Hab.t()
    Qab = cue @ Hab.t()
    del Hab
    Kab_n = _norm_t(Kab)
    Qab_n = _norm_t(Qab)
    del Kab, Qab
    pred_ab_idx = _batched_argmax_sim(Qab_n, Kab_n, q_batch=Q_BATCH)
    arm_AB_control = float((y.index_select(0, pred_ab_idx) == ytrue).float().mean().item())
    del Kab_n, Qab_n, pred_ab_idx
    if dev.type == "cuda":
        torch.cuda.empty_cache()

    # ARM C: compose sparse-fan-in expand -> fly-LSH on expanded code. BATCHED FIX (this was the v1 crash point).
    Pc_np = (g.random((dp, dp)).astype(np.float32) < FLY_NONZERO).astype(np.float32)
    Kexp_np_local = Kexp.detach().cpu().numpy()
    cue_exp_np_local = cue_exp.detach().cpu().numpy()
    # Free Kexp/cue_exp GPU tensors now that we have CPU copies; the upcoming
    # Ktc tensor will replace them in GPU memory budget.
    del Kexp, cue_exp
    if dev.type == "cuda":
        torch.cuda.empty_cache()
    Ktc_np = _flylsh_tags_np(Kexp_np_local, Pc_np, FLY_TOPK)
    Qtc_np = _flylsh_tags_np(cue_exp_np_local, Pc_np, FLY_TOPK)
    Ktc = torch.from_numpy(Ktc_np.astype(np.float32)).to(dev)
    Qtc = torch.from_numpy(Qtc_np.astype(np.float32)).to(dev)
    pred_c2_idx = _batched_argmax_sim(Qtc, Ktc, q_batch=Q_BATCH)
    arm_C = float((y.index_select(0, pred_c2_idx) == ytrue).float().mean().item())
    del Ktc, Qtc, pred_c2_idx
    if dev.type == "cuda":
        torch.cuda.empty_cache()

    # ARM D: attention upper-bound with beta sweep. BATCHED FIX via _batched_attn_recall.
    beta_base = 1.0 / math.sqrt(d)
    arm_D, arm_D_best_bm, arm_D_per_beta = _attention_arm_d_t(cue, Ks, cb_d, ytrue, y, beta_base, BETA_MULT_SWEEP)

    storage_bits = float(FLY_TOPK * math.log2(dp))

    if dev.type == "cuda":
        del Kp, y, cue, Ks, cb_d, cb_dp
        torch.cuda.empty_cache()

    return {
        "arm1_raw": round(arm1_raw, 4),
        "arm_A": round(arm_A, 4),
        "arm_Ap_dense": round(arm_Ap, 4),
        "arm_B_fly_lsh": round(arm_B_fly_lsh, 4),
        "arm_B_charikar": round(arm_B_charikar, 4),
        "arm_AB_control": round(arm_AB_control, 4),
        "arm_C": round(arm_C, 4),
        "arm_D": round(arm_D, 4),
        "arm_D_best_beta_mult": arm_D_best_bm,
        "arm_D_per_beta": [(round(bm, 2), round(r, 4)) for bm, r in arm_D_per_beta],
        "B_storage_bits_per_mem": round(storage_bits, 1),
        "q_batch": Q_BATCH,
    }


# ---------- pure-numpy variant for --self-test (no GPU dependency) ----------

def _arms_np(Kp, y_np, g, seed):
    d = Kp.shape[1]
    M = len(Kp)
    qidx = np.arange(M) if M <= MAX_Q else np.sort(g.choice(M, MAX_Q, replace=False))
    noise = SIGMA * g.standard_normal((len(qidx), d)).astype(np.float32)
    Ks = _np_norm(Kp) * np.sqrt(d)
    cue = Ks[qidx] + noise
    ytrue = y_np[qidx]
    cb_d = _np_norm(g.standard_normal((C, d)).astype(np.float32))
    W_raw = cb_d[y_np].T @ Ks
    arm1_raw = float((_decode_np(cue @ W_raw.T, cb_d) == ytrue).mean())
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

    dp = EXPAND * d
    Hab_np = (g.standard_normal((dp, d)).astype(np.float32) * (1.0 / np.sqrt(d)))
    Kab = Ks @ Hab_np.T
    Qab = cue @ Hab_np.T
    Kab_n = _np_norm(Kab)
    Qab_n = _np_norm(Qab)
    sim_ab = Qab_n @ Kab_n.T
    pred_ab = np.argmax(sim_ab, axis=1)
    arm_AB_control = float((y_np[pred_ab] == ytrue).mean())

    return {"arm1_raw": float(arm1_raw), "arm_D": float(arm_D),
            "arm_D_best_beta_mult": best_bm, "arm_D_per_beta": per_beta,
            "arm_AB_control": float(arm_AB_control)}


# ---------- adversarial-similarity facts (consecutive-token stride-1 windows) ----------

_PROSE_POOL = [
    "The cerebellum contains more neurons than the rest of the brain combined and plays a critical role in motor learning and sensorimotor integration. Granule cells in the cerebellar cortex receive sparse fan-in connections from mossy fibers, with each granule cell typically synapsing with only four to seven mossy fiber inputs. This sparse expansion creates a high-dimensional representation that separates similar input patterns into distinguishable patterns of granule cell activity.",
    "Drosophila olfactory processing relies on a similar sparse expansion architecture. The roughly fifty projection neurons sending information to the mushroom body diverge onto two thousand Kenyon cells, with each Kenyon cell sampling input from only about six projection neurons. Hashing approaches inspired by this fly architecture have proven competitive with sophisticated deep learning methods for nearest neighbor search in high dimensional spaces.",
    "Hyperdimensional computing operates on vectors of thousands of dimensions and uses simple operations like binding multiplication and superposition addition to compose structured information. The capacity of dense superposition memory scales with the effective dimensionality of the underlying representation space and decreases when stored items become correlated rather than orthogonal.",
    "Anisotropy in pretrained language model representations limits direct application of distance based retrieval methods. Token embeddings in models like BERT and Pythia cluster in narrow cones rather than spreading uniformly across the hypersphere. This concentration reduces the effective dimensionality from theoretical bounds set by the embedding size to a much smaller fraction determined by the eigenvalue spread of the covariance matrix.",
    "Whitening transformations can rotate anisotropic distributions to appear isotropic but cannot increase the underlying rank of a representation. The Mu and Viswanath analysis showed that simple post processing fixes appear to help on word similarity benchmarks while leaving the deeper rank deficiency unchanged. Architectural approaches that expand into higher dimensional sparse spaces address the rank limitation more fundamentally.",
    "Random sparse projections create new axes of representation by combining input dimensions in unpredictable ways. Some projections happen to emphasize directions orthogonal to the dominant anisotropy cone, recovering separability that was lost in the original space. The fly olfactory circuit appears to exploit exactly this property to discriminate odors that share many of the same molecular features.",
    "Locality sensitive hashing partitions vectors into buckets such that similar inputs land in the same bucket with high probability. Charikar described a hyperplane based method using sign patterns from random Gaussian projections. The output is a binary sketch where Hamming distance approximates angular distance in the original space and the dimensionality of the sketch can be tuned independently of the input dimensionality.",
    "Memory augmented neural networks attempt to combine the flexibility of dense gradient based learning with the precise content addressable retrieval of external storage. Attention mechanisms provide a continuous approximation to retrieval that can be trained end to end but suffer from quadratic complexity in the number of stored items and require careful temperature calibration to avoid mass collapsing to uniform distributions.",
    "Substrate native hyperdimensional architectures aim to perform inference without calling out to dense neural network components at retrieval time. The encoder may be used once during setup to extract hidden state representations but the inference time operations stay within the hyperdimensional algebra. This separation allows the substrate to be analyzed and verified independently of the encoder used to bootstrap its initial representations.",
    "Capacity bounds for associative memory derive from the dimensionality of the storage substrate and the orthogonality of stored patterns. When the substrate dimensionality is large and stored patterns are uncorrelated the capacity scales linearly with dimensions. When patterns are correlated as in real language model residuals the effective capacity drops dramatically and recall accuracy collapses past a regime dependent threshold.",
    "The relationship between sparse expansion and retrieval accuracy depends on the specific structure of the input distribution. Synthetic random inputs achieve capacity matching theoretical bounds while naturalistic anisotropic inputs require either explicit decorrelation or architectural compensation. The cerebellar fly inspired sparse fan in approach addresses the latter by creating new axes through random combination rather than attempting to reshape the underlying input distribution.",
]


def _build_adversarial_prose(g, target_tokens):
    pool = list(_PROSE_POOL)
    pieces = []
    total_words = 0
    while total_words < target_tokens:
        idx = int(g.integers(0, len(pool)))
        pieces.append(pool[idx])
        total_words += len(pool[idx].split())
    return " ".join(pieces)


def _facts_and_encode_adversarial(seed, M_total):
    os.environ["HDLAB_RUN_MODE"] = RUN_MODE
    import experiments.exp_flagship_sparse_projected_KV_PROBE_whiten_before_topk_v1 as _probe
    _probe.ENCODER = ENCODER
    _probe.ENC_DTYPE = torch.float16 if torch.cuda.is_available() else torch.float32
    encode = _probe.encode
    train_contrastive = _probe.train_contrastive

    g = np.random.default_rng(seed)
    prose = _build_adversarial_prose(g, target_tokens=M_total + WINDOW_TOKENS + CUE_SHIFT + 50)
    words = prose.split()
    needed = M_total + WINDOW_TOKENS + CUE_SHIFT
    if len(words) < needed:
        prose = _build_adversarial_prose(g, target_tokens=needed * 2)
        words = prose.split()
    keys = []
    cues = []
    for i in range(M_total):
        keys.append(" ".join(words[i:i + WINDOW_TOKENS]))
        cues.append(" ".join(words[i + CUE_SHIFT:i + CUE_SHIFT + WINDOW_TOKENS]))
    print("[adversarial-facts] seed=%d M_total=%d words_pool=%d window=%d shift=%d sample_key='%s' sample_cue='%s'" % (
        seed, M_total, len(words), WINDOW_TOKENS, CUE_SHIFT,
        keys[0][:80], cues[0][:80]
    ), flush=True)

    K = encode(keys)
    Q = encode(cues)

    perm = g.permutation(M_total)
    tr = perm[:TRAIN_M]
    ho = perm[TRAIN_M:]
    W = train_contrastive(K[tr], Q[tr], PROJ_DIM, TRAIN_STEPS, seed)
    Kp_all = (K[ho] @ W).astype(np.float32)
    print("[adversarial-encode] seed=%d encoded=%d projected_dim=%d held_out=%d" % (
        seed, M_total, PROJ_DIM, len(Kp_all)
    ), flush=True)
    return Kp_all


def run_unit(seed):
    M_max = max(M_SWEEP)
    M_total = M_max + TRAIN_M
    print("[seed=%d] encoder=%s M_total=%d (adversarial-similarity stride-1 windows; encode once; v2_batched)" % (
        seed, ENCODER, M_total
    ), flush=True)
    Kp_all = _facts_and_encode_adversarial(seed, M_total)
    g = np.random.default_rng(seed * 7 + 1)
    by_M = {}
    for M in M_SWEEP:
        if M > len(Kp_all):
            print("[warn] M=%d exceeds Kp_all=%d; skipping" % (M, len(Kp_all)), flush=True)
            continue
        y = g.integers(0, C, M).astype(np.int64)
        arms_seed = seed * 7 + M
        a = _arms_torch(Kp_all[:M].astype(np.float32), y, arms_seed)
        by_M["M%d" % M] = a
        print(("[seed=%d M=%d] raw=%.3f A=%.3f(Ap=%.3f) B_fly=%.3f B_char=%.3f AB_ctrl=%.3f C=%.3f "
               "D=%.3f(best_beta_x=%s) q_batch=%d") % (
            seed, M, a["arm1_raw"], a["arm_A"], a["arm_Ap_dense"],
            a["arm_B_fly_lsh"], a["arm_B_charikar"], a["arm_AB_control"], a["arm_C"],
            a["arm_D"], a["arm_D_best_beta_mult"], a["q_batch"]
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
    M_max = max(M_SWEEP) if M_SWEEP else 100000

    def vals(M, key):
        return [u["by_M"]["M%d" % M][key] for u in units if "M%d" % M in u["by_M"] and key in u["by_M"]["M%d" % M]]

    def med(M, key):
        v = vals(M, key)
        return float(np.median(v)) if v else 0.0

    raw_at_max = med(M_max, "arm1_raw")
    A = med(M_max, "arm_A")
    Ap = med(M_max, "arm_Ap_dense")
    Bfly = med(M_max, "arm_B_fly_lsh")
    Bchar = med(M_max, "arm_B_charikar")
    AB = med(M_max, "arm_AB_control")
    Cc = med(M_max, "arm_C")
    D = med(M_max, "arm_D")

    cv_Bfly = _cv(vals(M_max, "arm_B_fly_lsh"))
    cv_Bchar = _cv(vals(M_max, "arm_B_charikar"))
    cv_AB = _cv(vals(M_max, "arm_AB_control"))
    cv_D = _cv(vals(M_max, "arm_D"))

    detail = {
        "M_eval": M_max,
        "arm1_raw": raw_at_max,
        "arm_A": A,
        "arm_Ap_dense": Ap,
        "arm_B_fly_lsh": Bfly,
        "arm_B_charikar": Bchar,
        "arm_AB_control": AB,
        "arm_C": Cc,
        "arm_D_meter": D,
        "cv_arm_B_fly_lsh": round(cv_Bfly, 4),
        "cv_arm_B_charikar": round(cv_Bchar, 4),
        "cv_arm_AB_control": round(cv_AB, 4),
        "cv_arm_D": round(cv_D, 4),
        "n_seeds": len(units),
        "bands": {
            "HP_CHAIN_GRADE": BAND_HP_CHAIN_GRADE,
            "HP_RAW_CEILING": BAND_HP_RAW_CEILING,
            "HP_BEAT_PEER": BAND_HP_BEAT_PEER,
            "HP_BEAT_CONTROL": BAND_HP_BEAT_CONTROL,
            "HP_BOTH_LSH": BAND_HP_BOTH_LSH,
            "MB_RESCUE_LOW": BAND_MB_RESCUE_LOW,
            "MB_RESCUE_HIGH": BAND_MB_RESCUE_HIGH,
            "MB_CONTROL_BEATS_RAW": BAND_MB_CONTROL_BEATS_RAW,
            "HF_RESCUE": BAND_HF_RESCUE,
            "HF_CONTROL_ALSO": BAND_HF_CONTROL_ALSO,
            "CV_HP": BAND_CV_HP,
            "Q_SATURATION": BAND_Q_SATURATION,
            "METER_FLOOR": BAND_METER_FLOOR,
        },
        "Q_BATCH": Q_BATCH,
        "CONFIG_VERSION": CONFIG_VERSION,
        "cites": [
            "substrate_anisotropy_rescue_M100k_adversarial_similarity_keys_v1",  # this cell's predecessor (OOM)
            "substrate_anisotropy_rescue_4arm_sweep_v2_calibrated_meter_full",
            "anisotropy_rescue_4arm_sweep_v1_gpu",
            "dense_kv_whitening_revival_v1_gpu",
            "Litwin-Kumar2017_cerebellar",
            "fly_LSH_Dasgupta2017",
            "Charikar2002_hyperplane_lsh",
            "skunkworks_tier_ruling_5_artifact_late_wave_2026-06-25",
            "research_anisotropy_intuitive_synthesis_with_visual_2026-06-25",
        ],
    }

    summ = (
        "raw=%.3f | A=%.3f(Ap=%.3f) Bfly=%.3f Bchar=%.3f AB_ctrl=%.3f C=%.3f | D_meter=%.3f | "
        "cv_Bfly=%.3f cv_Bchar=%.3f cv_AB=%.3f cv_D=%.3f | q_batch=%d"
    ) % (raw_at_max, A, Ap, Bfly, Bchar, AB, Cc, D, cv_Bfly, cv_Bchar, cv_AB, cv_D, Q_BATCH)

    q_flags = []
    for name, val in [("Bfly", Bfly), ("Bchar", Bchar), ("AB_ctrl", AB), ("C", Cc), ("D", D)]:
        if val >= BAND_Q_SATURATION:
            q_flags.append("[Q-DISCIPLINE: %s=%.4f >= %.3f -- suspect saturation even at M=100k adversarial; corpus may still be easy; need M=500k+ or harder construction]" % (name, val, BAND_Q_SATURATION))
    q_note = " ".join(q_flags) + (" " if q_flags else "")

    if AB >= BAND_HF_CONTROL_ALSO:
        return ("HARD_FAIL",
                ("HARD_FAIL_CONTROL_ALSO_PASSES: ARM_AB_control = %.3f >= %.2f at M=%d adversarial-similarity keys -> "
                 "generic dense Gaussian random hash also rescues; LSH-specific attribution from v2 was artifact of "
                 "M=10k easy regime. Mechanism story = 'any random projection at d'=%d works'; LSH is NOT load-bearing. "
                 "raw=%.3f. %s%s") % (AB, BAND_HF_CONTROL_ALSO, M_max, AB_CONTROL_NBITS, raw_at_max, q_note, summ),
                detail)

    if Bfly <= BAND_HF_RESCUE and Bchar <= BAND_HF_RESCUE:
        return ("HARD_FAIL",
                ("HARD_FAIL_RESCUE_DOESNT_HOLD: BOTH ARM_B_fly_lsh = %.3f AND ARM_B_charikar = %.3f <= %.2f at M=%d "
                 "adversarial-similarity keys -> v2's M=10k 0.997 was a too-easy-regime artifact; LSH rescue does NOT "
                 "hold at substrate-product scale on adversarial keys. AB_control=%.3f (also low; mechanism story changes). "
                 "raw=%.3f. %s") % (Bfly, Bchar, BAND_HF_RESCUE, M_max, AB, raw_at_max, summ),
                detail)

    raw_collapsed = raw_at_max <= BAND_HP_RAW_CEILING

    if (Bfly >= BAND_HP_BOTH_LSH and Bchar >= BAND_HP_BOTH_LSH
            and (Bfly - AB) >= BAND_HP_BEAT_CONTROL
            and (Bchar - AB) >= BAND_HP_BEAT_CONTROL
            and cv_Bfly <= BAND_CV_HP and cv_Bchar <= BAND_CV_HP and raw_collapsed):
        return ("HARD_PASS",
                ("CHAIN-GRADE-CONFIRMED_BOTH_LSH_RESCUE: ARM_B_fly_lsh = %.3f AND ARM_B_charikar = %.3f BOTH >= %.2f "
                 "at M=%d adversarial; both beat AB_control = %.3f by >= %.2f margin; raw collapsed to %.3f <= %.2f; "
                 "cv_fly = %.3f cv_char = %.3f <= %.2f -> fly-LSH AND Charikar both rescue anisotropy at substrate-product "
                 "scale on adversarial keys; cannot discriminate which is better at this regime -> atomize as JOINT LSH-rescue. %s%s"
                 ) % (Bfly, Bchar, BAND_HP_BOTH_LSH, M_max, AB, BAND_HP_BEAT_CONTROL, raw_at_max, BAND_HP_RAW_CEILING,
                      cv_Bfly, cv_Bchar, BAND_CV_HP, q_note, summ),
                detail)

    if (Bfly >= BAND_HP_CHAIN_GRADE
            and (Bfly - Bchar) >= BAND_HP_BEAT_PEER
            and (Bfly - AB) >= BAND_HP_BEAT_CONTROL
            and cv_Bfly <= BAND_CV_HP and raw_collapsed):
        return ("HARD_PASS",
                ("CHAIN-GRADE-CONFIRMED_FLY_LSH: ARM_B_fly_lsh = %.3f >= %.2f at M=%d adversarial; beats Charikar = %.3f "
                 "by %.3f (>= %.2f) AND beats AB_control = %.3f by %.3f (>= %.2f); raw collapsed to %.3f <= %.2f; "
                 "cv = %.3f <= %.2f -> sparse-fan-in (fly-LSH K=%d) is the load-bearing rescue mechanism at substrate-product "
                 "scale on adversarial keys. v2 M=10k 0.997 promoted to chain-grade with mechanism attribution. %s%s"
                 ) % (Bfly, BAND_HP_CHAIN_GRADE, M_max, Bchar, Bfly - Bchar, BAND_HP_BEAT_PEER,
                      AB, Bfly - AB, BAND_HP_BEAT_CONTROL, raw_at_max, BAND_HP_RAW_CEILING,
                      cv_Bfly, BAND_CV_HP, FLY_TOPK, q_note, summ),
                detail)

    if (Bchar >= BAND_HP_CHAIN_GRADE
            and (Bchar - Bfly) >= BAND_HP_BEAT_PEER
            and (Bchar - AB) >= BAND_HP_BEAT_CONTROL
            and cv_Bchar <= BAND_CV_HP and raw_collapsed):
        return ("HARD_PASS",
                ("CHAIN-GRADE-CONFIRMED_CHARIKAR: ARM_B_charikar = %.3f >= %.2f at M=%d adversarial; beats fly-LSH = %.3f "
                 "by %.3f (>= %.2f) AND beats AB_control = %.3f by %.3f (>= %.2f); raw collapsed to %.3f <= %.2f; "
                 "cv = %.3f <= %.2f -> Charikar hyperplane-sign-sketch is the load-bearing rescue mechanism at substrate-product "
                 "scale on adversarial keys. v2 M=10k 1.000 promoted to chain-grade with mechanism attribution. %s%s"
                 ) % (Bchar, BAND_HP_CHAIN_GRADE, M_max, Bfly, Bchar - Bfly, BAND_HP_BEAT_PEER,
                      AB, Bchar - AB, BAND_HP_BEAT_CONTROL, raw_at_max, BAND_HP_RAW_CEILING,
                      cv_Bchar, BAND_CV_HP, q_note, summ),
                detail)

    fly_partial = BAND_MB_RESCUE_LOW <= Bfly < BAND_MB_RESCUE_HIGH
    char_partial = BAND_MB_RESCUE_LOW <= Bchar < BAND_MB_RESCUE_HIGH
    control_helps = (AB - raw_at_max) >= BAND_MB_CONTROL_BEATS_RAW
    if (fly_partial or char_partial) and control_helps:
        return ("MIDDLE_BAND",
                ("MIDDLE_BAND_PARTIAL_RESCUE: at M=%d adversarial -- Bfly = %.3f Bchar = %.3f in partial band "
                 "[%.2f, %.2f); AB_control = %.3f beats raw = %.3f by %.3f (>= %.2f); meter D = %.3f. "
                 "Partial rescue with control-also-helps -> 'random expansion partially helps' regime; "
                 "not chain-grade-confirmed for any specific mechanism but anisotropy is partially bypassable. %s%s"
                 ) % (M_max, Bfly, Bchar, BAND_MB_RESCUE_LOW, BAND_MB_RESCUE_HIGH, AB, raw_at_max, AB - raw_at_max,
                      BAND_MB_CONTROL_BEATS_RAW, D, q_note, summ),
                detail)

    return ("MIDDLE_BAND",
            ("MEASURED_MECHANISM_NO_DISCRIMINATOR: at M=%d adversarial-similarity keys, arms do not cleanly separate. "
             "raw = %.3f Bfly = %.3f Bchar = %.3f AB_control = %.3f D_meter = %.3f. "
             "No arm hits HP_CHAIN_GRADE = %.2f with discriminator margins; no joint-pass; no partial-rescue clean pattern. "
             "Mechanism numbers measured cleanly but the chain-grade-confirmed-attribution discriminator is inconclusive. %s%s"
             ) % (M_max, raw_at_max, Bfly, Bchar, AB, D, BAND_HP_CHAIN_GRADE, q_note, summ),
            detail)


def _selftest():
    """v2_batched self-test extends v1 self-test with BATCHED-CORRECTNESS check:
    (a) anisotropic raw collapses; (b) isotropic attention meter works; (c) AB_CONTROL works;
    (d) adversarial prose construction; (e) NEW: batched argmax == monolithic argmax (numeric equivalence).
    """
    g = np.random.default_rng(0)
    d = 128
    M = 1500
    sig = g.standard_normal((M, d)).astype(np.float32)
    mu = g.standard_normal((1, d)).astype(np.float32) * 3.0
    Kp = sig + mu
    y = g.integers(0, C, M).astype(np.int64)
    r = _arms_np(Kp, y, np.random.default_rng(1), 1)
    assert r["arm1_raw"] < 0.30, "raw superposition must collapse on anisotropic keys (got %.3f)" % r["arm1_raw"]

    iso = _np_norm(g.standard_normal((400, d)).astype(np.float32))
    yi = g.integers(0, C, 400).astype(np.int64)
    ri = _arms_np(iso, yi, np.random.default_rng(2), 2)
    assert ri["arm1_raw"] > 0.5, "isotropic small-M raw decode meter must work (got %.3f)" % ri["arm1_raw"]
    assert ri["arm_D"] >= 0.80, (
        "v2_batched meter-calibration assertion: attention beta-sweep must hit >= 0.80 on isotropic M=400 d=128 "
        "(got %.3f via best beta_mult=%s; per_beta=%s)."
    ) % (ri["arm_D"], ri["arm_D_best_beta_mult"], ri["arm_D_per_beta"])
    assert ri["arm_AB_control"] > 0.5, (
        "isotropic small-M AB_control must work (got %.3f). Bug in dense-Gaussian-hash arm."
    ) % ri["arm_AB_control"]

    g2 = np.random.default_rng(3)
    prose = _build_adversarial_prose(g2, target_tokens=200)
    words = prose.split()
    assert len(words) >= 200, "prose-builder did not hit target_tokens (got %d words)" % len(words)
    w_a = words[0:WINDOW_TOKENS]
    w_b = words[CUE_SHIFT:CUE_SHIFT + WINDOW_TOKENS]
    overlap = len(set(w_a) & set(w_b))
    assert overlap >= WINDOW_TOKENS - CUE_SHIFT - 1, (
        "adversarial windows must share at least %d/%d tokens by construction (got overlap=%d for window=%d shift=%d)"
    ) % (WINDOW_TOKENS - CUE_SHIFT - 1, WINDOW_TOKENS, overlap, WINDOW_TOKENS, CUE_SHIFT)

    # NEW v2_batched: BATCHED-CORRECTNESS check. Build a small Q, K and confirm batched_argmax_sim
    # returns the SAME indices as monolithic argmax. This is the load-bearing correctness assertion
    # for the OOM-fix -- if it ever diverges, results are not equivalent to v1.
    gq = np.random.default_rng(42)
    n_q, n_k, dh = 300, 800, 64
    Q_np = gq.standard_normal((n_q, dh)).astype(np.float32)
    K_np = gq.standard_normal((n_k, dh)).astype(np.float32)
    dev_test = _torch_device()
    Qt = torch.from_numpy(Q_np).to(dev_test)
    Kt = torch.from_numpy(K_np).to(dev_test)
    mono_idx = torch.argmax(Qt @ Kt.t(), dim=1)
    # exercise multiple q_batch sizes including ones that split unevenly
    for qb in [1, 17, 64, 200, n_q]:
        bat_idx = _batched_argmax_sim(Qt, Kt, q_batch=qb)
        assert torch.equal(mono_idx, bat_idx), (
            "v2_batched OOM-FIX correctness violation: batched_argmax_sim(q_batch=%d) diverged from monolithic "
            "(n_q=%d n_k=%d dh=%d; %d mismatches)"
        ) % (qb, n_q, n_k, dh, int((mono_idx != bat_idx).sum().item()))

    # Also exercise batched_attn_recall vs monolithic
    cb_test_np = _np_norm(gq.standard_normal((C, dh)).astype(np.float32))
    cb_test = torch.from_numpy(cb_test_np).to(dev_test)
    Ks_test = _norm_t(torch.from_numpy(K_np).to(dev_test)) * math.sqrt(dh)
    cue_test = _norm_t(torch.from_numpy(Q_np).to(dev_test)) * math.sqrt(dh)
    y_test = torch.from_numpy(gq.integers(0, C, n_k).astype(np.int64)).to(dev_test)
    ytrue_test = torch.from_numpy(gq.integers(0, C, n_q).astype(np.int64)).to(dev_test)
    beta_test = 1.0 / math.sqrt(dh)
    # monolithic reference
    lg_m = beta_test * (cue_test @ Ks_test.t())
    lg_m = lg_m - lg_m.max(dim=1, keepdim=True).values
    w_m = torch.softmax(lg_m, dim=1)
    readout_m = w_m @ cb_test[y_test]
    pred_m = _decode_t(readout_m, cb_test)
    rec_m = float((pred_m == ytrue_test).float().mean().item())
    # batched
    rec_b = _batched_attn_recall(cue_test, Ks_test, cb_test, y_test, ytrue_test, beta_test, q_batch=37)
    # softmax + matmul ordering can introduce tiny FP differences -> allow 1e-4 tolerance on recall
    assert abs(rec_m - rec_b) <= 1e-3, (
        "v2_batched OOM-FIX attn-recall correctness: monolithic=%.6f vs batched=%.6f (diff=%.6f > 1e-3)"
    ) % (rec_m, rec_b, abs(rec_m - rec_b))

    print(
        "[selftest] PASS: anisotropic raw collapses (%.3f) + isotropic raw works (%.3f) + isotropic attention meter (D=%.3f best_beta_x=%s) + AB_control (%.3f) + adversarial-prose construction (overlap=%d/%d) + BATCHED-CORRECTNESS argmax-eq + attn-recall-eq (mono=%.4f bat=%.4f)"
        % (r["arm1_raw"], ri["arm1_raw"], ri["arm_D"], ri["arm_D_best_beta_mult"], ri["arm_AB_control"], overlap, WINDOW_TOKENS, rec_m, rec_b),
        flush=True,
    )


if __name__ == "__main__":
    _selftest()
    if _ARGS.self_test:
        raise SystemExit(0)
    print("[config] %s mode=%s | %s" % (ANCHOR_NAME, RUN_MODE, CONFIG_VERSION), flush=True)
    gpu_avail = torch.cuda.is_available()
    gpu_name = torch.cuda.get_device_name(0) if gpu_avail else "cpu"
    print("[gpu] available=%s name=%s" % (gpu_avail, gpu_name), flush=True)

    out_dir = get_output_dir(ANCHOR_NAME)
    run_cfg = {"run_mode": RUN_MODE, "proj": PROJ_DIM, "expand": EXPAND, "kfanin": K_FANIN,
               "schema": "v2_batched-M100k-adversarial-similarity-keys-OOM-FIX", "seeds": SEEDS, "M": M_SWEEP,
               "q_batch": Q_BATCH}
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
        "window_tokens": WINDOW_TOKENS,
        "cue_shift": CUE_SHIFT,
        "q_batch": Q_BATCH,
        "detail": detail,
        "gpu_avail": bool(gpu_avail),
        "gpu_name": gpu_name,
        "gpu_max_mem_alloc_mb": round(gpu_mem_alloc_mb, 1),
        "metrics_source": "measured_gpu_anisotropy_rescue_M100k_adversarial_similarity_keys_v2_batched",
        "per_unit": units,
        "elapsed_s": time.time() - t0,
    }
    write_metrics(out_dir, metrics, units)
    print("[metrics] written to %s" % (out_dir / "metrics.json"), flush=True)
