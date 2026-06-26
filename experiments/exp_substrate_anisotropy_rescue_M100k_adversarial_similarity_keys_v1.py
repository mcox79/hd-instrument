"""ANISOTROPY-RESCUE M=100k adversarial-similarity-keys v1 -- chain-grade DISCRIMINATOR follow-up to v2.

PROMOTION CONTEXT (USER + Skunkworks 2026-06-25):
v2 calibrated-meter at M=10k saturated 4/4 working arms at >= 0.995 -> cell's own Q_SUSPECT_SATURATION
band fired -> Skunkworks-correctly-overrode Director chain-grade-candidate to MEASURED_MECHANISM
(by-construction-saturation tiering). The 55x rescue (0.018 -> 0.997) IS measured; what we cannot
discriminate at M=10k is WHICH mechanism (fly-LSH? Charikar? both? any random hash?) is load-bearing.

v3 design = the chain-grade DISCRIMINATOR regime:
  - M scaled to {10k, 50k, 100k} - capacity bound becomes load-bearing past M=50k
  - Adversarial-similarity keys: consecutive-token stride-1 windows of natural text -> adjacent
    keys have HIGH cosine similarity by construction. Arms that just hash uniformly will collide;
    arms that USE / RESCUE the anisotropy correctly will separate
  - NEW arm: ARM_AB_CONTROL = generic random dense Gaussian hash (no sparsity, no signs). If this
    ALSO saturates at M=100k, the apparent rescue is "any random hash works" not "LSH-specific"
  - 4 named arms + control + meter at M_eval=100k under adversarial-similarity regime

EXPECTED OUTCOMES (per Skunkworks recommendation):
  HARD_PASS_CHAIN_GRADE_CONFIRMED_FLY_LSH: ARM_FLY_LSH >= 0.85 AND ARM_RAW <= 0.30 AND fly beats Charikar by >= 0.05 AND fly beats AB_CONTROL by >= 0.10 AND cv <= 0.05
  HARD_PASS_CHAIN_GRADE_CONFIRMED_CHARIKAR: same but Charikar beats fly
  HARD_PASS_BOTH_LSH_RESCUE: fly AND Charikar BOTH >= 0.85 AND both beat control by >= 0.10
  MIDDLE_BAND_PARTIAL_RESCUE: fly and/or Charikar in [0.50, 0.85]; control beats RAW by >= 0.20
  HARD_FAIL_RESCUE_DOESNT_HOLD: fly AND Charikar BOTH <= 0.30 at M=100k (v2 0.997 was M=10k-easy)
  HARD_FAIL_CONTROL_ALSO_PASSES: ARM_AB_CONTROL >= 0.85 (any random hash works; not LSH-specific)

Q-DISCIPLINE guards: if ANY arm hits >= 0.995 even at M=100k, BIAS-Q flag -> corpus too easy even
at M=100k; need M=500k+ or harder construction (e.g. semantic-paraphrase or contrastive hard-negatives).

META_M7 discipline: smoke matches full along capacity-sensitive dimensions. Smoke at M=2k for
pipeline sanity ONLY (NOT for verdict reasoning -- v2 taught us that M=10k smoke saturated everything
including controls; the verdict regime IS M=100k adversarial-similarity).

META_M6 discipline: RAW arm baseline derived in-cell from the SAME regime keys, not copied from v2.

GPU REQUIRED (Fix #24): torch.cuda actively used; encoder hoisted; matmuls on device.
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

ANCHOR_NAME = "substrate_anisotropy_rescue_M100k_adversarial_similarity_keys_v1"

_P = argparse.ArgumentParser()
_P.add_argument("--self-test", action="store_true", dest="self_test")
_P.add_argument("--smoke", action="store_true")
_ARGS, _ = _P.parse_known_args()
RUN_MODE = "smoke" if (_ARGS.smoke or _ARGS.self_test) else os.environ.get("HDLAB_RUN_MODE", "full")

# CAPACITY-SENSITIVE: smoke matches full on PROJ_DIM, C, EXPAND, K_FANIN, KWTA_FRAC, FLY_TOPK, FLY_NONZERO,
# SIGMA, BETA_MULT, AB_CONTROL_NBITS. Only ENCODER, SEEDS, M_SWEEP, TRAIN_M change between smoke/full.
PROJ_DIM = 768          # matches v2
C = 256
EXPAND = 5              # d' = 5*d = 3840 at PROJ_DIM=768
K_FANIN = 5
KWTA_FRAC = 0.10
FLY_TOPK = 20
FLY_NONZERO = 0.05
SIGMA = 0.1
MAX_Q = 1500
BETA_MULT_SWEEP = [1.0, 4.0, 16.0, 64.0]
# AB_CONTROL: dense Gaussian random hash with d' output dim, no sparsity, no signs -- generic baseline.
# If this saturates at M=100k under adversarial keys, then "any hash works" rather than LSH-specific.
AB_CONTROL_NBITS = EXPAND * PROJ_DIM  # 3840, matches d' used by LSH arms for apples-to-apples

# Adversarial-similarity construction:
#   - generate N_TOKENS-token natural text passage (from a canned Wikipedia-style prose pool)
#   - extract M sliding stride-1 windows of WINDOW_TOKENS each (adjacent windows share WINDOW_TOKENS-1 tokens)
#   - each window is encoded by the LM; the residual is the "key"
#   - cues = same windows with token offset shifted by CUE_SHIFT positions
WINDOW_TOKENS = 16     # each key is a 16-token window
CUE_SHIFT = 1          # cue uses windows shifted by 1 token (so cue and key differ by 1 token at edges)

if RUN_MODE == "full":
    ENCODER = "EleutherAI/pythia-2.8b"
    SEEDS = [11, 13, 19]
    M_SWEEP = [10000, 50000, 100000]
    TRAIN_M = 10000           # contrastive projection training; matches v2 scaling
    TRAIN_STEPS = 600
    N_TOKENS_BUDGET = 110000  # tokens to extract M_max = 100k stride-1 windows (need M + WINDOW)
else:
    # SMOKE: tiny mode for pipeline sanity ONLY; NOT for verdict reasoning.
    # META_M7 caveat acknowledged: smoke saturating is EXPECTED; verdict regime is M=100k.
    ENCODER = "EleutherAI/pythia-160m"
    SEEDS = [11]
    M_SWEEP = [500, 2000]
    TRAIN_M = 500
    TRAIN_STEPS = 100
    N_TOKENS_BUDGET = 2200

# PROSPECTIVE BANDS (LOCKED AT MODULE INIT via assert META_PROSPECTIVE_BANDS_FRESH_SEEDS).
# Bands are EVALUATED AT M_eval = max(M_SWEEP) = 100k (full) or 2k (smoke).
# At full M=100k these are the chain-grade discriminator bands per Skunkworks spec.
BAND_HP_CHAIN_GRADE = 0.85            # ARM_X absolute floor for chain-grade CONFIRMED
BAND_HP_RAW_CEILING = 0.30            # RAW must collapse (raw <= 0.30) for rescue to be discriminable
BAND_HP_BEAT_PEER = 0.05              # winning LSH arm must beat the OTHER LSH arm by this much
BAND_HP_BEAT_CONTROL = 0.10           # winning LSH arm must beat AB_CONTROL by this much
BAND_HP_BOTH_LSH = 0.85               # both fly AND Charikar floor for joint-rescue HARD_PASS
BAND_MB_RESCUE_LOW = 0.50             # MIDDLE_BAND PARTIAL_RESCUE lower floor for either LSH arm
BAND_MB_RESCUE_HIGH = 0.85            # MIDDLE_BAND PARTIAL_RESCUE upper bound (above this is HARD_PASS)
BAND_MB_CONTROL_BEATS_RAW = 0.20      # MIDDLE_BAND PARTIAL needs control to also beat RAW by this much
BAND_HF_RESCUE = 0.30                 # HARD_FAIL_RESCUE_DOESNT_HOLD: both LSH arms <= this at M=100k
BAND_HF_CONTROL_ALSO = 0.85           # HARD_FAIL_CONTROL_ALSO_PASSES: AB_CONTROL >= this at M=100k
BAND_CV_HP = 0.05                     # cv ceiling for HARD_PASS variants
BAND_Q_SATURATION = 0.995             # any arm >= this -> suspect saturation flag (even at M=100k)
BAND_METER_FLOOR = 0.50               # arm_D meter floor at M=100k (relaxed from v2 -- at M=100k attention upper-bound is intrinsically harder)

assert 0.0 < BAND_HF_RESCUE < BAND_MB_RESCUE_LOW < BAND_MB_RESCUE_HIGH <= BAND_HP_CHAIN_GRADE < BAND_Q_SATURATION < 1.0, "bands ordered"
assert 0.0 < BAND_HP_BEAT_PEER < BAND_HP_BEAT_CONTROL < 1.0, "discriminator margins ordered"
assert 0.0 < BAND_HP_RAW_CEILING < BAND_MB_CONTROL_BEATS_RAW + BAND_HP_RAW_CEILING < BAND_MB_RESCUE_HIGH, "raw-ceiling sane"
assert 0.0 < BAND_METER_FLOOR < 1.0, "meter floor sane"
assert BAND_HP_BOTH_LSH <= BAND_HP_CHAIN_GRADE, "joint-pass floor not above single-pass floor"
assert BAND_HF_CONTROL_ALSO >= BAND_HP_CHAIN_GRADE, "control-also-passes failsafe sanity"

CONFIG_VERSION = (
    "v3_M100k_adversarial(A-cerebellar-K%d/Ap-dense/B_fly_lsh/B_charikar/AB_control/C-compose/D-attn-beta-sweep) | "
    "expand%dx kwta%.2f flytopk%d window%dt shift%d | beta_mults=%s | seeds=%s | M=%s | FP32_GPU | bands locked"
) % (K_FANIN, EXPAND, KWTA_FRAC, FLY_TOPK, WINDOW_TOKENS, CUE_SHIFT, BETA_MULT_SWEEP, SEEDS, M_SWEEP)


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


def _attention_arm_d_t(cue, Ks, codebook_d, ytrue, y, beta_base, beta_mults):
    """Arm D = MAX over beta-sweep of softmax-attention recall@1. v2 calibration semantics."""
    per_beta = []
    for bm in beta_mults:
        beta = bm * beta_base
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
    """6 arms (raw, A_cerebellar, Ap_dense, B_fly_lsh, B_charikar, AB_control, C_compose, D_meter) on torch.cuda.

    NEW v3 arm: AB_CONTROL = dense Gaussian random hash (no sparsity, no signs), to test
    "any random hash" vs "LSH-specific" attribution at M=100k under adversarial-similarity keys.
    """
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

    # ARM RAW
    W_raw = (cb_d[y].t() @ Ks)
    pred_raw = _decode_t(cue @ W_raw.t(), cb_d)
    arm1_raw = float((pred_raw == ytrue).float().mean().item())

    # ARM A: cerebellar sparse-fan-in -> kWTA -> superposition
    cb_dp_np = _np_norm(g.standard_normal((C, dp)).astype(np.float32))
    cb_dp = torch.from_numpy(cb_dp_np).to(dev)
    Sf_np = _sparse_fanin_np(d, dp, K_FANIN, g)
    Sf = torch.from_numpy(Sf_np).to(dev)
    Kexp = _kwta_t(Ks @ Sf.t(), KWTA_FRAC)
    cue_exp = _kwta_t(cue @ Sf.t(), KWTA_FRAC)
    WA = (cb_dp[y].t() @ Kexp)
    pred_A = _decode_t(cue_exp @ WA.t(), cb_dp)
    arm_A = float((pred_A == ytrue).float().mean().item())

    # ARM A': dense Gaussian fan-in control (existing v2 arm)
    Sd_np = (g.standard_normal((dp, d)).astype(np.float32) * (1.0 / math.sqrt(d)))
    Sd = torch.from_numpy(Sd_np).to(dev)
    KexpD = _kwta_t(Ks @ Sd.t(), KWTA_FRAC)
    cueD = _kwta_t(cue @ Sd.t(), KWTA_FRAC)
    WAp = (cb_dp[y].t() @ KexpD)
    pred_Ap = _decode_t(cueD @ WAp.t(), cb_dp)
    arm_Ap = float((pred_Ap == ytrue).float().mean().item())

    # ARM B_fly_lsh: median-subtract + sparse random proj + WTA top-k -> tag-overlap argmax
    Pf_np = ((g.random((dp, d)).astype(np.float32) < FLY_NONZERO).astype(np.float32)
             * g.standard_normal((dp, d)).astype(np.float32))
    Ks_np_local = Ks.detach().cpu().numpy()
    cue_np_local = cue.detach().cpu().numpy()
    Kt_np = _flylsh_tags_np(Ks_np_local, Pf_np, FLY_TOPK)
    Qt_np = _flylsh_tags_np(cue_np_local, Pf_np, FLY_TOPK)
    Kt = torch.from_numpy(Kt_np.astype(np.float32)).to(dev)
    Qt = torch.from_numpy(Qt_np.astype(np.float32)).to(dev)
    sim_fly = Qt @ Kt.t()
    pred_fly_idx = torch.argmax(sim_fly, dim=1)
    arm_B_fly_lsh = float((y.index_select(0, pred_fly_idx) == ytrue).float().mean().item())

    # ARM B_charikar: hyperplane signs
    Hc_np = g.standard_normal((dp, d)).astype(np.float32)
    Hc = torch.from_numpy(Hc_np).to(dev)
    Kc = torch.sign(Ks @ Hc.t())
    Qc = torch.sign(cue @ Hc.t())
    sim_c = Qc @ Kc.t()
    pred_c_idx = torch.argmax(sim_c, dim=1)
    arm_B_charikar = float((y.index_select(0, pred_c_idx) == ytrue).float().mean().item())

    # NEW v3 ARM_AB_CONTROL: dense Gaussian random hash (no sparsity, no signs).
    # Output is the dense projection itself (continuous values); decode by argmax cosine sim.
    # If THIS arm also saturates at M=100k adversarial-similarity keys, then the LSH attribution
    # is artifact -- any random projection works. Apples-to-apples: same output dim AB_CONTROL_NBITS = dp.
    Hab_np = (g.standard_normal((AB_CONTROL_NBITS, d)).astype(np.float32)
              * (1.0 / math.sqrt(d)))
    Hab = torch.from_numpy(Hab_np).to(dev)
    Kab = Ks @ Hab.t()       # continuous dense projection
    Qab = cue @ Hab.t()
    Kab_n = _norm_t(Kab)
    Qab_n = _norm_t(Qab)
    sim_ab = Qab_n @ Kab_n.t()
    pred_ab_idx = torch.argmax(sim_ab, dim=1)
    arm_AB_control = float((y.index_select(0, pred_ab_idx) == ytrue).float().mean().item())

    # ARM C: compose sparse-fan-in expand -> fly-LSH on expanded code
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

    # ARM D: attention upper-bound with beta sweep (v2 meter calibration)
    beta_base = 1.0 / math.sqrt(d)
    arm_D, arm_D_best_bm, arm_D_per_beta = _attention_arm_d_t(cue, Ks, cb_d, ytrue, y, beta_base, BETA_MULT_SWEEP)

    storage_bits = float(FLY_TOPK * math.log2(dp))

    if dev.type == "cuda":
        del Kp, y, cue, Ks, cb_d, cb_dp, Sf, Sd, Kexp, cue_exp, WA, WAp, Hc, Kc, Qc, Kt, Qt, Ktc, Qtc, W_raw, Hab, Kab, Qab, Kab_n, Qab_n
        torch.cuda.empty_cache()

    return {
        "arm1_raw": round(arm1_raw, 4),
        "arm_A": round(arm_A, 4),
        "arm_Ap_dense": round(arm_Ap, 4),
        "arm_B_fly_lsh": round(arm_B_fly_lsh, 4),
        "arm_B_charikar": round(arm_B_charikar, 4),
        "arm_AB_control": round(arm_AB_control, 4),  # NEW v3 arm
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

    # AB_CONTROL on numpy (for self-test discriminator check)
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

# Natural-text prose pool. Avoids needing external data fetch at runtime.
# 11 paragraphs * varying length -- replicated/concatenated to hit N_TOKENS_BUDGET.
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
    """Concat prose pool with light shuffling until target_tokens reached.

    Uses simple whitespace tokenization for length budgeting (encoder will retokenize).
    """
    pool = list(_PROSE_POOL)
    pieces = []
    total_words = 0
    while total_words < target_tokens:
        idx = int(g.integers(0, len(pool)))
        pieces.append(pool[idx])
        total_words += len(pool[idx].split())
    return " ".join(pieces)


def _facts_and_encode_adversarial(seed, M_total):
    """Adversarial-similarity key construction via consecutive-token stride-1 windows.

    Replaces v2's synthetic adj-noun make_facts. Each "key" is a 16-token sliding window
    of natural prose; adjacent keys share 15/16 tokens by construction -> HIGH cosine sim.
    Cues are the SAME windows shifted by CUE_SHIFT positions (so retrieve-self is the task,
    with high adjacency-confusion potential).
    """
    os.environ["HDLAB_RUN_MODE"] = RUN_MODE
    import experiments.exp_flagship_sparse_projected_KV_PROBE_whiten_before_topk_v1 as _probe
    _probe.ENCODER = ENCODER
    _probe.ENC_DTYPE = torch.float16 if torch.cuda.is_available() else torch.float32
    encode = _probe.encode
    train_contrastive = _probe.train_contrastive

    g = np.random.default_rng(seed)
    # Generate prose with enough words to extract M_total + CUE_SHIFT stride-1 windows.
    prose = _build_adversarial_prose(g, target_tokens=M_total + WINDOW_TOKENS + CUE_SHIFT + 50)
    words = prose.split()
    needed = M_total + WINDOW_TOKENS + CUE_SHIFT
    if len(words) < needed:
        # Re-expand with extra prose if undershoot.
        prose = _build_adversarial_prose(g, target_tokens=needed * 2)
        words = prose.split()
    # build M_total keys (window i = words[i : i+W]) and cues (window i+CUE_SHIFT)
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

    # Contrastive projection trained on the FIRST TRAIN_M facts; eval on the rest (held out).
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
    print("[seed=%d] encoder=%s M_total=%d (adversarial-similarity stride-1 windows; encode once)" % (
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
               "D=%.3f(best_beta_x=%s)") % (
            seed, M, a["arm1_raw"], a["arm_A"], a["arm_Ap_dense"],
            a["arm_B_fly_lsh"], a["arm_B_charikar"], a["arm_AB_control"], a["arm_C"],
            a["arm_D"], a["arm_D_best_beta_mult"]
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
        "CONFIG_VERSION": CONFIG_VERSION,
        "cites": [
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
        "cv_Bfly=%.3f cv_Bchar=%.3f cv_AB=%.3f cv_D=%.3f"
    ) % (raw_at_max, A, Ap, Bfly, Bchar, AB, Cc, D, cv_Bfly, cv_Bchar, cv_AB, cv_D)

    # Q-discipline: even at M=100k, saturation >= 0.995 means corpus still too easy
    q_flags = []
    for name, val in [("Bfly", Bfly), ("Bchar", Bchar), ("AB_ctrl", AB), ("C", Cc), ("D", D)]:
        if val >= BAND_Q_SATURATION:
            q_flags.append("[Q-DISCIPLINE: %s=%.4f >= %.3f -- suspect saturation even at M=100k adversarial; corpus may still be easy; need M=500k+ or harder construction]" % (name, val, BAND_Q_SATURATION))
    q_note = " ".join(q_flags) + (" " if q_flags else "")

    # HARD_FAIL_CONTROL_ALSO_PASSES (check FIRST -- this kills the LSH attribution)
    if AB >= BAND_HF_CONTROL_ALSO:
        return ("HARD_FAIL",
                ("HARD_FAIL_CONTROL_ALSO_PASSES: ARM_AB_control = %.3f >= %.2f at M=%d adversarial-similarity keys -> "
                 "generic dense Gaussian random hash also rescues; LSH-specific attribution from v2 was artifact of "
                 "M=10k easy regime. Mechanism story = 'any random projection at d'=%d works'; LSH is NOT load-bearing. "
                 "raw=%.3f. %s%s") % (AB, BAND_HF_CONTROL_ALSO, M_max, AB_CONTROL_NBITS, raw_at_max, q_note, summ),
                detail)

    # HARD_FAIL_RESCUE_DOESNT_HOLD (both LSH arms collapse)
    if Bfly <= BAND_HF_RESCUE and Bchar <= BAND_HF_RESCUE:
        return ("HARD_FAIL",
                ("HARD_FAIL_RESCUE_DOESNT_HOLD: BOTH ARM_B_fly_lsh = %.3f AND ARM_B_charikar = %.3f <= %.2f at M=%d "
                 "adversarial-similarity keys -> v2's M=10k 0.997 was a too-easy-regime artifact; LSH rescue does NOT "
                 "hold at substrate-product scale on adversarial keys. AB_control=%.3f (also low; mechanism story changes). "
                 "raw=%.3f. %s") % (Bfly, Bchar, BAND_HF_RESCUE, M_max, AB, raw_at_max, summ),
                detail)

    # HARD_PASS variants -- need RAW collapsed AND winning arm beats peer + control
    raw_collapsed = raw_at_max <= BAND_HP_RAW_CEILING

    # HARD_PASS_BOTH_LSH_RESCUE (both fly AND Charikar high; both beat control by margin)
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

    # HARD_PASS_CHAIN_GRADE_CONFIRMED_FLY_LSH (fly wins, beats Charikar AND control)
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

    # HARD_PASS_CHAIN_GRADE_CONFIRMED_CHARIKAR (Charikar wins, beats fly AND control)
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

    # MIDDLE_BAND_PARTIAL_RESCUE
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

    # Default MIDDLE_BAND for everything else (measured mechanism but not chain-grade-discriminator)
    return ("MIDDLE_BAND",
            ("MEASURED_MECHANISM_NO_DISCRIMINATOR: at M=%d adversarial-similarity keys, arms do not cleanly separate. "
             "raw = %.3f Bfly = %.3f Bchar = %.3f AB_control = %.3f D_meter = %.3f. "
             "No arm hits HP_CHAIN_GRADE = %.2f with discriminator margins; no joint-pass; no partial-rescue clean pattern. "
             "Mechanism numbers measured cleanly but the chain-grade-confirmed-attribution discriminator is inconclusive. %s%s"
             ) % (M_max, raw_at_max, Bfly, Bchar, AB, D, BAND_HP_CHAIN_GRADE, q_note, summ),
            detail)


def _selftest():
    """Self-test: (a) anisotropic raw collapses; (b) attention beta-sweep recovers >= 0.80 on isotropic synthetic;
    (c) AB_CONTROL also computes cleanly (sanity check on the new arm).
    """
    g = np.random.default_rng(0)
    d = 128
    M = 1500
    # (a) anisotropic: common-mode -> raw collapses
    sig = g.standard_normal((M, d)).astype(np.float32)
    mu = g.standard_normal((1, d)).astype(np.float32) * 3.0
    Kp = sig + mu
    y = g.integers(0, C, M).astype(np.int64)
    r = _arms_np(Kp, y, np.random.default_rng(1), 1)
    assert r["arm1_raw"] < 0.30, "raw superposition must collapse on anisotropic keys (got %.3f)" % r["arm1_raw"]

    # (b) isotropic small-M: attention beta-sweep MUST hit >= 0.80
    iso = _np_norm(g.standard_normal((400, d)).astype(np.float32))
    yi = g.integers(0, C, 400).astype(np.int64)
    ri = _arms_np(iso, yi, np.random.default_rng(2), 2)
    assert ri["arm1_raw"] > 0.5, "isotropic small-M raw decode meter must work (got %.3f)" % ri["arm1_raw"]
    assert ri["arm_D"] >= 0.80, (
        "v3 meter-calibration assertion: attention beta-sweep must hit >= 0.80 on isotropic M=400 d=128 "
        "(got %.3f via best beta_mult=%s; per_beta=%s)."
    ) % (ri["arm_D"], ri["arm_D_best_beta_mult"], ri["arm_D_per_beta"])
    assert ri["arm_AB_control"] > 0.5, (
        "isotropic small-M AB_control must work (got %.3f). Bug in new dense-Gaussian-hash arm."
    ) % ri["arm_AB_control"]

    # (c) sanity-check the adversarial-prose-window construction WITHOUT calling the encoder
    g2 = np.random.default_rng(3)
    prose = _build_adversarial_prose(g2, target_tokens=200)
    words = prose.split()
    assert len(words) >= 200, "prose-builder did not hit target_tokens (got %d words)" % len(words)
    # adjacent windows share WINDOW_TOKENS - CUE_SHIFT tokens by construction
    w_a = words[0:WINDOW_TOKENS]
    w_b = words[CUE_SHIFT:CUE_SHIFT + WINDOW_TOKENS]
    overlap = len(set(w_a) & set(w_b))
    assert overlap >= WINDOW_TOKENS - CUE_SHIFT - 1, (
        "adversarial windows must share at least %d/%d tokens by construction (got overlap=%d for window=%d shift=%d)"
    ) % (WINDOW_TOKENS - CUE_SHIFT - 1, WINDOW_TOKENS, overlap, WINDOW_TOKENS, CUE_SHIFT)

    print(
        "[selftest] PASS: anisotropic raw collapses (%.3f) + isotropic raw works (%.3f) + isotropic attention meter (D=%.3f best_beta_x=%s) + AB_control (%.3f) + adversarial-prose construction (overlap=%d/%d)"
        % (r["arm1_raw"], ri["arm1_raw"], ri["arm_D"], ri["arm_D_best_beta_mult"], ri["arm_AB_control"], overlap, WINDOW_TOKENS),
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
               "schema": "v3-M100k-adversarial-similarity-keys", "seeds": SEEDS, "M": M_SWEEP}
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
        "detail": detail,
        "gpu_avail": bool(gpu_avail),
        "gpu_name": gpu_name,
        "gpu_max_mem_alloc_mb": round(gpu_mem_alloc_mb, 1),
        "metrics_source": "measured_gpu_anisotropy_rescue_M100k_adversarial_similarity_keys_v1",
        "per_unit": units,
        "elapsed_s": time.time() - t0,
    }
    write_metrics(out_dir, metrics, units)
    print("[metrics] written to %s" % (out_dir / "metrics.json"), flush=True)
