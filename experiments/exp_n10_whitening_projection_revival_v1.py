"""N10 WHITENING-PROJECTION REVIVAL v1 -- Path C ARM A 3x-revival #1: ZCA-whiten the CERT591-style contrastive-projected key matrix BEFORE storage + retrieval.

Context (per `notes/n9_smh_landed_vet_skunkworks_2026-06-22.md`):
- n9 SMH (sparsemax-attractor decode) HONEST_NEGATIVE at M=10k sigma=0.1 (recall=0.0194, far below HARD_FAIL bar 0.35).
- Diagnosis off-data: dense softmax Hopfield IDENTICAL to SMH to 4 decimals on every (M, sigma) cell. Projection value-cue recall@1 sanity = 0.010 (chance baseline). Decode-form does not matter when attention scores don't separate. The bottleneck is at the PROJECTION step, NOT the decode step.
- Decode-algebra rescue family EXHAUSTED for eff-rank-limited storage at high M.
- Skunkworks's #1 ranked 3x revival (composite P=0.45-0.55): whitening the contrastive projection. Cheapest-first; no encoder change; composable with downstream stores.

MECHANISM UNDER TEST: ZCA-whitening of the CERT591-style contrastive projection.
- Fit Sigma = Cov(K_train_projected) on the TRAIN slice.
- Compute ZCA matrix W_zca = Sigma^(-1/2) (symmetric square root inverse).
- Apply ZCA to BOTH train and held-out projected keys/cues before storage + retrieval.
- Hypothesis: removing the collapsed-direction artifact (whitening decorrelates dimensions + flattens singular spectrum) lifts effective rank => keys become separable => proj_recall_sanity rises from chance 0.010 substantially => sparse-superposition rescue path RE-OPENS.

KEY DIFFERENCES from `exp_n9_smh_sparsemax_decode_v1` (the ARM A baseline reference):
  1. ADDED: ZCA-whitening computed on TRAIN-projected keys, applied to TRAIN + HELDOUT projected keys/cues. Shrinkage epsilon (1e-3) for numerical stability.
  2. ADDED: eff_rank measurement on the projected matrix BEFORE and AFTER whitening per seed (the load-bearing diagnostic: does whitening raise eff_rank?).
  3. ARM RESTRUCTURE -- 4 arms per (M, sigma, seed) cell:
       Arm A (anchor):    UN-whitened argmax decode    -- reproduces n9's argmax (0.0081 at M=10k sig=0.1)
       Arm B (RESCUE):    ZCA-WHITENED argmax decode   -- the proposed rescue
       Arm C (diagnostic): UN-whitened SMH (sparsemax) -- reproduces n9's SMH (0.0194 at M=10k sig=0.1) cross-cell
       Arm D (control):   ZCA-WHITENED + random-rotation argmax -- whiten-specific (should NOT help; ANY-linear-transform null)
  4. PRE-REG HARD bands (Skunkworks-rec'd P=0.45-0.55):
       HARD_PASS:   Arm B recall >= 0.35 at M=10k sig=0.1 AND proj_recall_sanity_whitened >= 0.15  -> 3x revival WORKS
       MIDDLE_BAND: 0.10 <= Arm B recall < 0.35 at M=10k sig=0.1                                    -> partial mechanism
       HARD_FAIL:   Arm B recall < 0.10 at M=10k sig=0.1 OR proj_recall_sanity_whitened < 0.05      -> whitening insufficient; route encoder upgrade
  5. DISCRIMINATING controls (per cert architecture):
       - Arm D (random-rotation): should not differ from Arm A meaningfully (not "any linear transform" effect).
       - proj_recall_sanity_whitened: must rise substantially from 0.010 chance baseline if whitening works.
       - Arm A anchor reproduction: must match n9's 0.0081 at M=10k sig=0.1 (cross-cell sanity).

Critical sanity check (LOAD-BEARING): proj_recall_sanity_whitened. If this stays at chance under whitening, the whitening diagnosis was wrong-direction and the encoder upgrade is the only remaining route.

CPU-only (pythia-160m, M up to 10k); 3 seeds; per_unit per (M, sigma, seed); B_storage_bits_per_mem reported; ASCII; per-seed checkpoint; atexit/SIGTERM synthesize from partials (Fix #11 TODO #9 patch); in-cell smoke detection (Fix #11 TODO #6 workaround).

Cites: n9_smh_sparsemax_decode_v1 (HONEST_NEGATIVE referent; ledger row 2caf2f8f6cf148ab), exp_armA_projected_key_revival_v1 (HARD_FAIL referent; row f2a658ddda005c98), CERT591_kv_learned_projection_v1 (projection lineage), Bell_Sejnowski_1997_ZCA, n9_skunkworks_landed_VET_2026-06-22 (route note).

Skunkworks structural blockers baked in:
  #3 _LLM_CALL_COUNTER = [0]  (KV-storage cell; substrate-only at inference; LLM only at encode)
  #1 per_unit per (seed, M, sigma) -- exhaustive grid + 4-arm
  #2 cv computed across seeds in compute_verdict
  #4 N/A (no VQ-floor / ceiling_bpc; KV cell not LM cell)
"""
from __future__ import annotations
import sys, os, argparse, time, signal, atexit, json
from pathlib import Path
import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_partial_key, aggregate_partials, write_metrics

ANCHOR_NAME = "n10_whitening_projection_revival_v1"
_LLM_CALL_COUNTER = [0]  # substrate-only at inference by construction (LLM only at encode)
_P = argparse.ArgumentParser()
_P.add_argument("--self-test", action="store_true", dest="self_test")
_P.add_argument("--smoke", action="store_true")
_ARGS, _ = _P.parse_known_args()

# Fix #11 TODO #6 workaround: queue_add.sh `--` env-after-separator does NOT pass HDLAB_RUN_MODE
# through to the runner reliably; the queue entry name carries `_smoke` suffix in those cases.
# Detect from HDLAB_EXP_NAME (the env var the runner ALWAYS sets) as a fallback signal.
_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = "_smoke" in _HDLAB_EXP_NAME.lower()
RUN_MODE = "smoke" if (_ARGS.smoke or _ARGS.self_test or _NAME_SAYS_SMOKE) else os.environ.get("HDLAB_RUN_MODE", "full")

# Config (CPU-only; pythia-160m; matches n9/ARM A baseline)
ENCODER = "EleutherAI/pythia-160m"
PROJ_DIM = 256          # CERT 591 full proj_dim (unchanged from n9)
C = 256                 # codebook size (value labels)
EXPAND = 5              # ARM A expand factor (d' = 5 * d) -- argmax arms only
K_FANIN = 5             # cerebellar K=5 per Litwin-Kumar -- argmax arms only
KWTA_FRAC = 0.10        # top-10% kWTA -- argmax arms only
SMH_BETA = 8.0          # sparsemax temperature (Arm C anchor parameter)
ZCA_EPSILON = 1e-3      # shrinkage for ZCA Sigma^(-1/2) stability
MAX_Q = 800             # eval-query cap per unit (matches n9)
if RUN_MODE == "full":
    SEEDS = [7, 17, 23]
    M_SWEEP = [1000, 5000, 10000]
    SIGMA_SWEEP = [0.0, 0.1, 0.3]
    TRAIN_M = 2500
    TRAIN_STEPS = 600
else:
    SEEDS = [0]
    M_SWEEP = [1000]
    SIGMA_SWEEP = [0.0]
    TRAIN_M = 600
    TRAIN_STEPS = 150

# CONFIG_VERSION must include every result-affecting param (PROT-021 lesson)
CONFIG_VERSION = ("n10_whitening_v1; encoder=%s proj=%d C=%d expand=%d K=%d kwta=%.2f beta=%.2f "
                  "zca_eps=%.4f M=%s sigma=%s seeds=%s train_M=%d steps=%d") % (
                  ENCODER, PROJ_DIM, C, EXPAND, K_FANIN, KWTA_FRAC, SMH_BETA,
                  ZCA_EPSILON, M_SWEEP, SIGMA_SWEEP, SEEDS, TRAIN_M, TRAIN_STEPS)

# Corpus (verbatim from n9 / exp_armA_projected_key_revival_v1)
_ADJ = "red blue swift quiet ancient modern silver golden hidden northern rapid silent hollow bright frozen molten crimson azure verdant amber".split()
_NOUN = "falcon river engine archive bridge reactor delta harbor summit forge canyon beacon orchard meadow glacier tower lagoon prairie quarry vault".split()
_VALW = "helium cobalt basalt cedar quartz copper marble willow granite saffron indigo cypress bronze jasper walnut".split()
_PROPS = ["founded in", "powered by", "located near", "awarded for", "merged with"]


def make_facts(M):
    keys, vq = [], []
    for i in range(M):
        ent = "the %s %s" % (_ADJ[i % len(_ADJ)], _NOUN[(i // len(_ADJ)) % len(_NOUN)])
        prop = _PROPS[i % len(_PROPS)]
        value = "%s %d" % (_VALW[i % len(_VALW)], 1000 + i)
        keys.append("%s was %s %s." % (ent, prop, value))
        vq.append("Which one was %s %s?" % (prop, value))
    return keys, vq


def _np_norm(X):
    return (X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-8)).astype(np.float32)


def _kwta(X, frac):
    """Top-frac kWTA: keep top |frac*d| magnitudes per row, zero rest (sign preserved)."""
    k = max(1, int(frac * X.shape[1]))
    out = np.zeros_like(X, np.float32)
    idx = np.argpartition(np.abs(X), -k, axis=1)[:, -k:]
    np.put_along_axis(out, idx, np.take_along_axis(X, idx, axis=1), axis=1)
    return out


def _sparse_fanin(d, dp, K, g):
    """Cerebellar sparse-fan-in: dp expanded units, each reads K random input dims (random +-1)."""
    S = np.zeros((dp, d), np.float32)
    for i in range(dp):
        idx = g.choice(d, K, replace=False)
        S[i, idx] = g.integers(0, 2, K).astype(np.float32) * 2 - 1
    return S


def _sparsemax(z):
    """Sparsemax (Martins & Astudillo 2016). z: (B, M). Returns sparse simplex projection."""
    if z.ndim == 1:
        z = z[None, :]
        squeeze = True
    else:
        squeeze = False
    B, M = z.shape
    zs = np.sort(z, axis=1)[:, ::-1]
    csum = np.cumsum(zs, axis=1)
    j_idx = np.arange(1, M + 1, dtype=np.float32)[None, :]
    cond = (1.0 + j_idx * zs) > csum
    k = cond.sum(axis=1).astype(np.int64)
    k = np.maximum(k, 1)
    csum_at_k = csum[np.arange(B), k - 1]
    tau = (csum_at_k - 1.0) / k
    p = np.maximum(0.0, z - tau[:, None])
    if squeeze:
        p = p[0]
    return p.astype(np.float32)


def _fit_zca(K_train, eps=ZCA_EPSILON):
    """Fit ZCA-whitening matrix from TRAIN keys.

    Returns (mu, W_zca) such that whitened X = (X - mu) @ W_zca makes Cov(whitened) ~ I.

    Algorithm (Bell & Sejnowski 1997):
      mu = mean(K_train)
      Sigma = Cov(K_train - mu)
      U, S, Ut = svd(Sigma)
      W_zca = U @ diag(1 / sqrt(S + eps)) @ U.T

    eps shrinkage stabilizes the inverse sqrt of small singular values.
    """
    mu = K_train.mean(axis=0, keepdims=True).astype(np.float32)
    Xc = (K_train - mu).astype(np.float32)
    # Sigma = (1/N) Xc.T @ Xc
    n = Xc.shape[0]
    Sigma = (Xc.T @ Xc) / max(n - 1, 1)
    # eigendecomposition (Sigma is symmetric PSD)
    eigvals, eigvecs = np.linalg.eigh(Sigma.astype(np.float64))
    # numerical guard: clip to >=0
    eigvals = np.maximum(eigvals, 0.0)
    inv_sqrt = 1.0 / np.sqrt(eigvals + eps)
    W_zca = (eigvecs @ np.diag(inv_sqrt) @ eigvecs.T).astype(np.float32)
    return mu, W_zca


def _apply_zca(X, mu, W_zca):
    """Apply ZCA-whitening: (X - mu) @ W_zca."""
    return ((X - mu) @ W_zca).astype(np.float32)


def _eff_rank(X):
    """Effective rank = exp(entropy of normalized singular values).

    Higher = closer to isotropic; lower = collapsed into few directions.
    """
    s = np.linalg.svd(X.astype(np.float32), compute_uv=False)
    s = np.maximum(s, 1e-12)
    p = s / s.sum()
    H = -np.sum(p * np.log(p + 1e-12))
    return float(np.exp(H))


def _random_orthogonal(d, g):
    """Sample d x d random orthogonal matrix via QR of standard normal."""
    A = g.standard_normal((d, d)).astype(np.float32)
    Q, R = np.linalg.qr(A)
    # fix sign so determinant +1 (cosmetic; doesn't matter for argmax recall)
    s = np.sign(np.diag(R))
    Q = Q * s[None, :]
    return Q.astype(np.float32)


def _decode_argmax(scores, codebook):
    """ARM A baseline decode: nearest codebook entry by cosine."""
    Sn = _np_norm(scores)
    return np.argmax(Sn @ codebook.T, axis=1)


def _armA_argmax_recall(K_keys, K_cues, y, qidx, sigma, g, codebook, S_fanin):
    """ARM A baseline (verbatim from n9/exp_armA_projected_key_revival_v1):
    kWTA write + argmax decode over kWTA-superposition."""
    d = K_keys.shape[1]
    Ks = _np_norm(K_keys) * np.sqrt(d)
    noise = sigma * g.standard_normal((len(qidx), d)).astype(np.float32) if sigma > 0 else 0.0
    cue = K_cues[qidx] + noise if isinstance(noise, np.ndarray) else K_cues[qidx].copy()
    cue = _np_norm(cue) * np.sqrt(d)
    Kexp = _kwta(Ks @ S_fanin.T, KWTA_FRAC)
    cueE = _kwta(cue @ S_fanin.T, KWTA_FRAC)
    W = codebook[y].T @ Kexp
    pred = _decode_argmax(cueE @ W.T, codebook)
    return float((pred == y[qidx]).mean())


def _armC_smh_recall(K_keys, K_cues, y, qidx, sigma, g, beta=SMH_BETA):
    """Arm C cross-cell anchor: SMH sparsemax-attractor decode (verbatim from n9)."""
    d = K_keys.shape[1]
    K_norm = _np_norm(K_keys)
    noise = sigma * g.standard_normal((len(qidx), d)).astype(np.float32) if sigma > 0 else 0.0
    cue = K_cues[qidx] + noise if isinstance(noise, np.ndarray) else K_cues[qidx].copy()
    cue_norm = _np_norm(cue)
    z = beta * (cue_norm @ K_norm.T).astype(np.float32)
    p = _sparsemax(z)
    pred_idx = np.argmax(p, axis=1)
    pred_y = y[pred_idx]
    return float((pred_y == y[qidx]).mean())


def _train_contrastive(K_tr, Q_tr, d, steps, seed, shuffle=False):
    """Linear InfoNCE projection W (D x d) -- verbatim from n9."""
    import torch
    import torch.nn.functional as F
    torch.manual_seed(seed)
    K = torch.tensor(K_tr); Q = torch.tensor(Q_tr); n, D = K.shape
    if shuffle:
        Q = Q[torch.randperm(n)]
    W = (torch.randn(D, d) * (1.0 / D ** 0.5)).requires_grad_(True)
    opt = torch.optim.Adam([W], lr=1e-2)
    bs = min(256, n)
    for step in range(steps):
        idx = torch.randperm(n)[:bs]
        tgt = torch.arange(len(idx))
        kp = F.normalize(K[idx] @ W, dim=1)
        qp = F.normalize(Q[idx] @ W, dim=1)
        lq = (qp @ kp.T) / 0.07; lk = (kp @ qp.T) / 0.07
        loss_align = 0.5 * (F.cross_entropy(lq, tgt) + F.cross_entropy(lk, tgt))
        kk = kp @ kp.T; off = kk - torch.eye(len(idx)) * 2.0
        loss_unif = off.mean()
        loss = loss_align + 0.5 * loss_unif
        opt.zero_grad(); loss.backward(); opt.step()
    return W.detach().numpy().astype(np.float32)


def _encode(texts):
    """CPU pythia-160m mean-pool encode -- verbatim from n9."""
    import torch
    from transformers import AutoModel, AutoTokenizer
    tok = AutoTokenizer.from_pretrained(ENCODER)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    mdl = AutoModel.from_pretrained(ENCODER, torch_dtype=torch.float32).eval()
    out = []
    for i in range(0, len(texts), 32):
        t = tok(texts[i:i + 32], return_tensors="pt", padding=True, truncation=True, max_length=48)
        with torch.no_grad():
            h = mdl(**t).last_hidden_state
        m = t["attention_mask"].unsqueeze(-1).float()
        out.append(((h * m).sum(1) / m.sum(1).clamp(min=1)).float().numpy())
    del mdl
    return np.concatenate(out, 0).astype(np.float32)


def _proj_recall_at1(Kp, Qp, n_test=200):
    """Diagnostic projection value-cue recall@1: argmax_i (q_j @ k_i) == j ?

    n9 baseline (un-whitened on raw projection) = 0.010 (chance for M=200 candidates is 0.005).
    Load-bearing diagnostic: must rise substantially under whitening if the hypothesis holds.
    """
    n = min(n_test, Kp.shape[0])
    Kn = _np_norm(Kp[:n])
    Qn = _np_norm(Qp[:n])
    pred = np.argmax(Qn @ Kn.T, axis=1)
    return float((pred == np.arange(n)).mean())


def run_unit(seed):
    g = np.random.default_rng(seed)
    n_total = max(M_SWEEP) + TRAIN_M
    keys, cues = make_facts(n_total)
    print("  [seed=%d] encoding %d facts on %s (CPU)..." % (seed, n_total, ENCODER), flush=True)
    t_enc = time.time()
    K = _encode(keys); Q = _encode(cues)
    print("  [seed=%d] encode done in %.1fs (D=%d)" % (seed, time.time() - t_enc, K.shape[1]), flush=True)
    perm = g.permutation(n_total)
    tr = perm[:TRAIN_M]
    ho = perm[TRAIN_M:]
    # CERT591-style learned contrastive projection on train half
    t_tr = time.time()
    W_proj = _train_contrastive(K[tr], Q[tr], PROJ_DIM, TRAIN_STEPS, seed)
    print("  [seed=%d] train_contrastive done in %.1fs" % (seed, time.time() - t_tr), flush=True)
    # raw projected (UN-whitened) keys/cues
    Kp_ho = (K[ho] @ W_proj).astype(np.float32)
    Qp_ho = (Q[ho] @ W_proj).astype(np.float32)
    # ZCA-whitening fit on the TRAIN slice's projected keys (closure-free; mu+W_zca only)
    Kp_tr = (K[tr] @ W_proj).astype(np.float32)
    mu, W_zca = _fit_zca(Kp_tr, ZCA_EPSILON)
    Kp_ho_white = _apply_zca(Kp_ho, mu, W_zca)
    Qp_ho_white = _apply_zca(Qp_ho, mu, W_zca)
    # ZCA-whitened-then-random-rotation control (Arm D): applies a random orthogonal R after whitening.
    # If whitening alone gives the lift, post-rotation should preserve it (rotation is norm/eigenvalue
    # invariant). If "any linear transform" helps, we'd expect Arm B and Arm D both lift -- we want them
    # to behave similarly under whitening alone, contrasted with Arm A. Setting differs: Arm D is meant
    # as a null vs an "unwhitening" that disrupts -- but the well-defined null IS the random rotation
    # applied to UN-whitened (i.e. another random linear pre-conditioner with no statistics-aware fit).
    # We implement Arm D = random_rotation(UN-whitened); this is the proper null for the whitening-
    # specific hypothesis: a random orthogonal does NOT raise effective rank (rank invariant), so if
    # eff_rank rise drives the lift, Arm D should NOT match Arm B.
    R = _random_orthogonal(Kp_ho.shape[1], g)
    Kp_ho_rotated = (Kp_ho @ R).astype(np.float32)
    Qp_ho_rotated = (Qp_ho @ R).astype(np.float32)
    # diagnostic: eff_rank + projection value-cue recall@1 BEFORE and AFTER whitening (load-bearing)
    eff_rank_before = _eff_rank(Kp_ho[:max(M_SWEEP)])
    eff_rank_after  = _eff_rank(Kp_ho_white[:max(M_SWEEP)])
    eff_rank_rotated = _eff_rank(Kp_ho_rotated[:max(M_SWEEP)])
    proj_recall_before = _proj_recall_at1(Kp_ho, Qp_ho)
    proj_recall_after  = _proj_recall_at1(Kp_ho_white, Qp_ho_white)
    proj_recall_rotated = _proj_recall_at1(Kp_ho_rotated, Qp_ho_rotated)
    print("  [seed=%d] eff_rank: before=%.2f after_whiten=%.2f rotated=%.2f"
          % (seed, eff_rank_before, eff_rank_after, eff_rank_rotated), flush=True)
    print("  [seed=%d] proj_recall@1: before=%.3f after_whiten=%.3f rotated=%.3f"
          % (seed, proj_recall_before, proj_recall_after, proj_recall_rotated), flush=True)
    by_cell = {}
    d_proj = Kp_ho.shape[1]
    dp_proj = EXPAND * d_proj
    for M in M_SWEEP:
        y = g.integers(0, C, M)
        qidx = np.arange(M) if M <= MAX_Q else np.sort(g.choice(M, MAX_Q, replace=False))
        gM = np.random.default_rng(seed * 7 + M)
        S_proj = _sparse_fanin(d_proj, dp_proj, K_FANIN, gM)
        cb_proj = _np_norm(gM.standard_normal((C, dp_proj)).astype(np.float32))
        for sigma in SIGMA_SWEEP:
            gS = np.random.default_rng(seed * 100 + int(sigma * 1000) + M)
            t_arm = time.time()
            # Arm A: UN-whitened argmax (n9 anchor reproduction)
            r_armA = _armA_argmax_recall(Kp_ho[:M], Qp_ho[:M], y, qidx, sigma, gS, cb_proj, S_proj)
            # Arm B: ZCA-WHITENED argmax (the proposed rescue)
            gS_b = np.random.default_rng(seed * 100 + int(sigma * 1000) + M)
            r_armB = _armA_argmax_recall(Kp_ho_white[:M], Qp_ho_white[:M], y, qidx, sigma, gS_b, cb_proj, S_proj)
            # Arm C: UN-whitened SMH (n9 cross-cell anchor reproduction)
            gS_c = np.random.default_rng(seed * 100 + int(sigma * 1000) + M)
            r_armC = _armC_smh_recall(Kp_ho[:M], Qp_ho[:M], y, qidx, sigma, gS_c)
            # Arm D: random-rotation argmax (null control; rotation is rank-invariant)
            gS_d = np.random.default_rng(seed * 100 + int(sigma * 1000) + M)
            r_armD = _armA_argmax_recall(Kp_ho_rotated[:M], Qp_ho_rotated[:M], y, qidx, sigma, gS_d, cb_proj, S_proj)
            cell = "M%d_sig%.2f" % (M, sigma)
            by_cell[cell] = {
                "M": M, "sigma": sigma,
                "recall_armA_unwhite_argmax": round(r_armA, 4),
                "recall_armB_zca_argmax": round(r_armB, 4),
                "recall_armC_unwhite_smh": round(r_armC, 4),
                "recall_armD_random_rot_argmax": round(r_armD, 4),
                "lift_B_over_A": round(r_armB - r_armA, 4),
                "lift_B_over_D": round(r_armB - r_armD, 4),
                "B_storage_bits_per_mem_armA": round(dp_proj * dp_proj * 32.0 / max(M, 1), 1),
                "B_storage_bits_per_mem_armB": round(dp_proj * dp_proj * 32.0 / max(M, 1), 1),
                "wall_s_unit": round(time.time() - t_arm, 2),
            }
            a = by_cell[cell]
            print("  [seed=%d M=%d sig=%.2f] A=%.3f B=%.3f C=%.3f D=%.3f lift_B-A=%.3f lift_B-D=%.3f (wall=%.1fs)" % (
                seed, M, sigma, a["recall_armA_unwhite_argmax"], a["recall_armB_zca_argmax"],
                a["recall_armC_unwhite_smh"], a["recall_armD_random_rot_argmax"],
                a["lift_B_over_A"], a["lift_B_over_D"], a["wall_s_unit"]), flush=True)
    return {
        "seed": seed,
        "by_cell": by_cell,
        "eff_rank_before_whitening": round(eff_rank_before, 3),
        "eff_rank_after_whitening": round(eff_rank_after, 3),
        "eff_rank_random_rotation": round(eff_rank_rotated, 3),
        "proj_recall_sanity_before": round(proj_recall_before, 4),
        "proj_recall_sanity_after_whitening": round(proj_recall_after, 4),
        "proj_recall_sanity_random_rotation": round(proj_recall_rotated, 4),
        "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
    }


def compute_verdict(units):
    if not units:
        return ("HARD_FAIL", "no results", {})
    # aggregate per (M, sigma) across seeds
    by_cell_agg = {}
    cell_keys = set()
    for u in units:
        cell_keys.update(u["by_cell"].keys())
    for ck in sorted(cell_keys):
        armA = [u["by_cell"][ck]["recall_armA_unwhite_argmax"] for u in units if ck in u["by_cell"]]
        armB = [u["by_cell"][ck]["recall_armB_zca_argmax"] for u in units if ck in u["by_cell"]]
        armC = [u["by_cell"][ck]["recall_armC_unwhite_smh"] for u in units if ck in u["by_cell"]]
        armD = [u["by_cell"][ck]["recall_armD_random_rot_argmax"] for u in units if ck in u["by_cell"]]
        M = units[0]["by_cell"][ck]["M"]; sigma = units[0]["by_cell"][ck]["sigma"]
        b_mean = float(np.mean(armB)); b_std = float(np.std(armB))
        b_cv = b_std / max(b_mean, 1e-6)
        by_cell_agg[ck] = {
            "M": M, "sigma": sigma,
            "armA_unwhite_argmax_mean": round(float(np.mean(armA)), 4),
            "armB_zca_argmax_mean": round(b_mean, 4),
            "armB_zca_argmax_std": round(b_std, 4),
            "armB_zca_argmax_cv": round(b_cv, 4),
            "armC_unwhite_smh_mean": round(float(np.mean(armC)), 4),
            "armD_random_rot_argmax_mean": round(float(np.mean(armD)), 4),
            "lift_B_over_A": round(b_mean - float(np.mean(armA)), 4),
            "lift_B_over_D": round(b_mean - float(np.mean(armD)), 4),
        }
    # discriminator: M=10000 sigma=0.1
    M_top = max(M_SWEEP)
    target_keys = [ck for ck in by_cell_agg
                   if by_cell_agg[ck]["M"] == M_top and abs(by_cell_agg[ck]["sigma"] - 0.1) < 1e-6]
    if target_keys:
        b_target = by_cell_agg[target_keys[0]]["armB_zca_argmax_mean"]
        b_target_cv = by_cell_agg[target_keys[0]]["armB_zca_argmax_cv"]
        a_anchor = by_cell_agg[target_keys[0]]["armA_unwhite_argmax_mean"]
        c_anchor = by_cell_agg[target_keys[0]]["armC_unwhite_smh_mean"]
        d_control = by_cell_agg[target_keys[0]]["armD_random_rot_argmax_mean"]
    else:
        b_target = 0.0; b_target_cv = 0.0; a_anchor = None; c_anchor = None; d_control = None
    # aggregate proj_recall_sanity across seeds (LOAD-BEARING)
    sanity_before = float(np.mean([u["proj_recall_sanity_before"] for u in units]))
    sanity_after  = float(np.mean([u["proj_recall_sanity_after_whitening"] for u in units]))
    sanity_rotated = float(np.mean([u["proj_recall_sanity_random_rotation"] for u in units]))
    eff_rank_before = float(np.mean([u["eff_rank_before_whitening"] for u in units]))
    eff_rank_after = float(np.mean([u["eff_rank_after_whitening"] for u in units]))
    eff_rank_rotated = float(np.mean([u["eff_rank_random_rotation"] for u in units]))
    # Anchor reproduction check: Arm A at M=10k sig=0.1 should reproduce n9's 0.0081
    anchor_reproduces_n9 = (a_anchor is not None and abs(a_anchor - 0.0081) <= 0.015)
    c_reproduces_n9_smh = (c_anchor is not None and abs(c_anchor - 0.0194) <= 0.015)
    detail = {
        "by_cell_agg": by_cell_agg,
        "M_top": M_top,
        "armB_at_M10k_sig0.1_mean": round(b_target, 4),
        "armB_at_M10k_sig0.1_cv": round(b_target_cv, 4),
        "armA_anchor_n9_reproduces": anchor_reproduces_n9,
        "armA_at_M10k_sig0.1_mean": a_anchor,
        "armC_anchor_n9_smh_reproduces": c_reproduces_n9_smh,
        "armC_at_M10k_sig0.1_mean": c_anchor,
        "armD_random_rot_at_M10k_sig0.1_mean": d_control,
        "proj_recall_sanity_before_mean": round(sanity_before, 4),
        "proj_recall_sanity_after_whitening_mean": round(sanity_after, 4),
        "proj_recall_sanity_random_rotation_mean": round(sanity_rotated, 4),
        "eff_rank_before_mean": round(eff_rank_before, 3),
        "eff_rank_after_whitening_mean": round(eff_rank_after, 3),
        "eff_rank_random_rotation_mean": round(eff_rank_rotated, 3),
        "n_seeds": len(units),
        "CONFIG_VERSION": CONFIG_VERSION,
        "honest_scope": "encoder=%s; CPU-only; ZCA-whitening on TRAIN-fit Sigma over CERT591-style contrastive projection; 4 arms per cell (A=unwhite-argmax, B=zca-argmax, C=unwhite-smh, D=random-rot-argmax)" % ENCODER,
        "cites": ["n9_smh_sparsemax_decode_v1_HONEST_NEGATIVE_2caf2f8f6cf148ab",
                  "exp_armA_projected_key_revival_v1_HARD_FAIL_f2a658ddda005c98",
                  "CERT591_kv_learned_projection_v1",
                  "Bell_Sejnowski_1997_ZCA",
                  "skunkworks_to_research_cc_all_LANDED_VET_path_c_armA_projected_HARD_FAIL_and_path_b_mkn_MIDDLE_BAND_MM_2026-06-22",
                  "n9_smh_landed_vet_skunkworks_2026-06-22"],
    }
    summary = ("M=%d sig=0.1: B=%.3f (cv=%.3f) | A=%.3f C=%.3f D=%.3f | sanity_before=%.3f after=%.3f rot=%.3f | eff_rank before=%.2f after=%.2f rot=%.2f"
               % (M_top, b_target, b_target_cv, (a_anchor or 0.0), (c_anchor or 0.0), (d_control or 0.0),
                  sanity_before, sanity_after, sanity_rotated,
                  eff_rank_before, eff_rank_after, eff_rank_rotated))
    # PRE-REG bands
    if b_target >= 0.35 and sanity_after >= 0.15:
        return ("HARD_PASS", "DISCRIMINATOR HARD_PASS: ZCA-whitening rescues sparse-superpos at high-M; Arm B recall=%.3f >= 0.35 at M=%d sig=0.1 across %d seeds (cv=%.3f); proj_recall_sanity_after=%.3f >= 0.15 (vs %.3f before = chance). Storage-chain item #3 RE-OPEN at projection step via eff-rank raising. " % (b_target, M_top, len(units), b_target_cv, sanity_after, sanity_before) + summary, detail)
    if b_target < 0.10 or sanity_after < 0.05:
        return ("HARD_FAIL", "DISCRIMINATOR HARD_FAIL: ZCA-whitening does NOT rescue sparse-superpos at high-M; Arm B=%.3f at M=%d sig=0.1 (bar=0.10) OR proj_recall_sanity_after=%.3f below 0.05 minimum-substantial-lift threshold. Whitening alone insufficient; route to encoder upgrade (pythia-1B -> 2.8B; CERT 591 precedent). " % (b_target, M_top, sanity_after) + summary, detail)
    return ("MIDDLE_BAND", "MIDDLE_BAND: ZCA-whitening provides partial rescue (Arm B=%.3f at M=%d sig=0.1; 0.10<=B<0.35); MEASURED_MECHANISM characterization; whitening lifts above chance but below HARD_PASS bar. sanity_after=%.3f (vs %.3f before). " % (b_target, M_top, sanity_after, sanity_before) + summary, detail)


# Fix #11 TODO #9 patch: atexit/SIGTERM synthesize metrics.json from partials if not yet written
_METRICS_WRITTEN = [False]
_OUT_DIR_REF = [None]
_T0_REF = [None]


def _synthesize_on_exit():
    """Synthesize metrics.json from per-seed partials if the cell was SIGKILLed before
    normal write_metrics fired. Fix #11 TODO #9 pattern.

    This ensures Skunkworks can verify-off-DATA even when the runner timeout SIGKILLs
    the cell mid-loop (n9 lesson: 2-of-3 seeds preserved as partials but aggregate
    NOT written by the cell's normal exit path)."""
    if _METRICS_WRITTEN[0]:
        return
    out_dir = _OUT_DIR_REF[0]
    if out_dir is None or not out_dir.exists():
        return
    try:
        partials = aggregate_partials(out_dir, ["s%d" % sd for sd in SEEDS])
        units = list(partials.values())
        if not units:
            return
        try:
            verdict, msg, detail = compute_verdict(units)
        except Exception as e:
            verdict, msg, detail = ("PARTIAL_TIMEOUT", "atexit synthesize: compute_verdict failed: %s" % e, {"n_seeds_recovered": len(units)})
        metrics = {
            "anchor_name": ANCHOR_NAME,
            "verdict": "TIMEOUT_PARTIAL_NSEEDS_%d" % len(units) if verdict != "PARTIAL_TIMEOUT" else verdict,
            "verdict_msg": "[atexit-synthesize] " + msg,
            "run_mode": RUN_MODE,
            "model": ENCODER,
            "proj_dim": PROJ_DIM,
            "zca_epsilon": ZCA_EPSILON,
            "M_SWEEP": M_SWEEP,
            "SIGMA_SWEEP": SIGMA_SWEEP,
            "n_seeds": len(units),
            "n_seeds_expected": len(SEEDS),
            "train_M": TRAIN_M,
            "train_steps": TRAIN_STEPS,
            "detail": detail,
            "metrics_source": "atexit_synthesize_partial_n10_whitening_projection_revival_v1",
            "per_unit": units,
            "elapsed_s": (time.time() - _T0_REF[0]) if _T0_REF[0] else 0.0,
            "summary": "[atexit-synthesize from %d/%d partials] %s" % (len(units), len(SEEDS), msg),
            "substrate_only_decode_gate": "N/A (KV-storage cell)",
            "zero_llm_calls_at_inference": True,
            "_llm_call_counter_final": _LLM_CALL_COUNTER[0],
            "_synthesized_by_atexit": True,
        }
        write_metrics(out_dir, metrics, units)
        _METRICS_WRITTEN[0] = True
        sys.stderr.write("[atexit] synthesized metrics.json from %d/%d partials\n" % (len(units), len(SEEDS)))
        sys.stderr.flush()
    except Exception as e:
        sys.stderr.write("[atexit] synthesize failed: %s\n" % e)
        sys.stderr.flush()


def _selftest():
    """Mechanism selftest: ZCA correctness + eff_rank monotonicity + arm wiring sanity."""
    g = np.random.default_rng(0)
    # 1. ZCA correctness: whitened cov ~ I
    X = g.standard_normal((500, 32)).astype(np.float32)
    # introduce anisotropy: scale dim 0 by 5x, dim 1 by 0.2x
    X[:, 0] *= 5.0
    X[:, 1] *= 0.2
    mu, W_zca = _fit_zca(X, eps=1e-6)
    Xw = _apply_zca(X, mu, W_zca)
    Cov_w = (Xw.T @ Xw) / (Xw.shape[0] - 1)
    # diagonal should be ~1; off-diag ~0; allow eps slop
    diag_err = float(np.max(np.abs(np.diag(Cov_w) - 1.0)))
    off_err = float(np.max(np.abs(Cov_w - np.diag(np.diag(Cov_w)))))
    assert diag_err < 0.2, "ZCA whitened cov diag should be ~1 (got max abs err %.3f)" % diag_err
    assert off_err < 0.2, "ZCA whitened cov off-diag should be ~0 (got max abs err %.3f)" % off_err
    # 2. eff_rank: isotropic > anisotropic (random Gaussian higher eff_rank than rank-1)
    iso = g.standard_normal((100, 16)).astype(np.float32)
    rank1 = (g.standard_normal((100, 1)) * g.standard_normal((1, 16))).astype(np.float32)
    er_iso = _eff_rank(iso); er_rank1 = _eff_rank(rank1)
    assert er_iso > er_rank1, "eff_rank should be higher for isotropic than rank-1 (iso=%.2f rank1=%.2f)" % (er_iso, er_rank1)
    # 3. eff_rank raises under whitening on anisotropic data
    er_X_before = _eff_rank(X)
    er_X_after = _eff_rank(Xw)
    assert er_X_after >= er_X_before - 0.1, "ZCA-whitening should not collapse eff_rank (before=%.2f after=%.2f)" % (er_X_before, er_X_after)
    # 4. random_orthogonal returns orthogonal
    R8 = _random_orthogonal(8, g)
    err = float(np.max(np.abs(R8 @ R8.T - np.eye(8, dtype=np.float32))))
    assert err < 1e-4, "random_orthogonal should be orthogonal (got max err %.4g)" % err
    # 5. random rotation preserves eff_rank (rank-invariant)
    R_X = _random_orthogonal(X.shape[1], g)
    Xrot = X @ R_X
    er_rot = _eff_rank(Xrot)
    assert abs(er_rot - er_X_before) < 0.5, "rotation should preserve eff_rank approximately (before=%.2f rot=%.2f)" % (er_X_before, er_rot)
    # 6. shape sanity (existing helpers)
    assert _kwta(g.standard_normal((5, 10)).astype(np.float32), 0.2).shape == (5, 10)
    assert _sparse_fanin(8, 20, 3, g).shape == (20, 8)
    # 7. _proj_recall_at1 on identity (perfect projection): should be 1.0 for any item being its own NN
    Kp = g.standard_normal((50, 16)).astype(np.float32)
    pr = _proj_recall_at1(Kp, Kp, n_test=50)
    assert pr > 0.99, "self-recall should be ~1 (got %.3f)" % pr
    print("[selftest] PASS: ZCA-whitened-cov (diag_err=%.3f off_err=%.3f) + eff_rank_iso(%.2f)>rank1(%.2f) + eff_rank_after(%.2f)>=before(%.2f) + ortho(err=%.4g) + rotation_preserves_eff_rank + helpers OK" % (
        diag_err, off_err, er_iso, er_rank1, er_X_after, er_X_before, err), flush=True)


if __name__ == "__main__":
    _selftest()
    if _ARGS.self_test:
        raise SystemExit(0)
    print("[config] %s mode=%s ENCODER=%s proj=%d zca_eps=%.4f M=%s sigma=%s seeds=%s train=%d/%d | name_says_smoke=%s | %s" % (
        ANCHOR_NAME, RUN_MODE, ENCODER, PROJ_DIM, ZCA_EPSILON, M_SWEEP, SIGMA_SWEEP, SEEDS, TRAIN_M, TRAIN_STEPS, _NAME_SAYS_SMOKE, CONFIG_VERSION), flush=True)
    out_dir = get_output_dir(ANCHOR_NAME)
    _OUT_DIR_REF[0] = out_dir
    # Fix #11 TODO #9: register atexit + SIGTERM synthesizer BEFORE the loop starts
    atexit.register(_synthesize_on_exit)
    try:
        signal.signal(signal.SIGTERM, lambda *a: (_synthesize_on_exit(), sys.exit(143)))
    except (ValueError, AttributeError):
        # SIGTERM unavailable on some Windows hosts; skip silently (atexit still fires on normal exit)
        pass
    run_cfg = {"run_mode": RUN_MODE, "proj": PROJ_DIM, "zca_eps": ZCA_EPSILON,
               "expand": EXPAND, "kfanin": K_FANIN, "kwta": KWTA_FRAC,
               "train_M": TRAIN_M, "train_steps": TRAIN_STEPS,
               "schema": "n10-whitening-projection-revival-v1"}
    t0 = time.time()
    _T0_REF[0] = t0
    for seed in SEEDS:
        key = "s%d" % seed
        if key in aggregate_partials(out_dir, [key], run_config=run_cfg):
            print("[ckpt] %s done; skip" % key, flush=True); continue
        write_partial_key(out_dir, key, run_unit(seed))
    units = list(aggregate_partials(out_dir, ["s%d" % sd for sd in SEEDS], run_config=run_cfg).values())
    verdict, msg, detail = compute_verdict(units)
    print("\n[VERDICT] " + msg, flush=True)
    metrics = {
        "anchor_name": ANCHOR_NAME,
        "verdict": verdict,
        "verdict_msg": msg,
        "run_mode": RUN_MODE,
        "model": ENCODER,
        "proj_dim": PROJ_DIM,
        "zca_epsilon": ZCA_EPSILON,
        "M_SWEEP": M_SWEEP,
        "SIGMA_SWEEP": SIGMA_SWEEP,
        "n_seeds": len(SEEDS),
        "train_M": TRAIN_M,
        "train_steps": TRAIN_STEPS,
        "detail": detail,
        "metrics_source": "measured_cpu_n10_whitening_projection_revival_v1",
        "per_unit": units,
        "elapsed_s": time.time() - t0,
        "summary": msg,
        "substrate_only_decode_gate": "N/A (KV-storage cell, not LM cell; per Path C revival framing)",
        "zero_llm_calls_at_inference": True,
        "_llm_call_counter_final": _LLM_CALL_COUNTER[0],
        "_name_says_smoke_workaround": _NAME_SAYS_SMOKE,
    }
    write_metrics(out_dir, metrics, units)
    _METRICS_WRITTEN[0] = True
    print("[metrics] written to %s" % (out_dir / "metrics.json"), flush=True)
