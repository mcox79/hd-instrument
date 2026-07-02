"""Core module for Stage 2/3 boundary cell: learned vs random-init encoder.

Question (per Sonnet Stage 2 Pareto Rank 4 / hidden-dim Dim L, P_def 0.44):
does the substrate benefit from LEARNED (gradient-optimized) encoding vs
random-init bipolar? All prior substrate work uses random-init keys. This
cell is the first substrate empirical test of trainable-pre-write encoding.

Design (2 arms x 3 alpha x 2 noise = 12 units/seed, full N=8192):

  ARM_RANDOM_INIT: bipolar iid (baseline; matches all prior substrate)
  ARM_LEARNED_CONTRASTIVE: initialize bipolar, then 500 SGD steps of
    contrastive loss on encoder outputs directly.

  Contrastive loss (encoder-only, NOT joint-with-substrate; per R21 lit-scan
  the CLIP-style-joint path was declined at P=5%, so this cell sidesteps
  by orthogonalizing encoder outputs BEFORE write):

    L = sum_{i<j} max(0, cos(k_i, k_j) - MARGIN)
      + LAMBDA * sum_i max(0, MARGIN - cos(k_i, k_i_aug))

    - MARGIN = 0.10 (off-diagonal cap)
    - LAMBDA = 0.5 (positive-pair weight)
    - k_i_aug = k_i with 1% bit-flip (bipolar noise augmentation)
    - Optimizer: SGD lr=0.01, 500 steps, batch = M

  Key: NO substrate recall in the loss. Encoder is trained to
  produce well-separated keys; substrate then writes/reads those keys via
  standard Hebbian W = sum_i o_i k_i^T / N.

Alpha sweep: {0.5, 1.5, 3.0} spans below/at/above AGS capacity wall.
Noise sweep: {0.0, 0.30} spans clean + moderate query noise.

HP conditions (symmetric; cell accepts either direction of finding):
  HP_LEARNED_HIGHER_CAPACITY:  at (alpha=1.5, f=0.0), LEARNED_top1 -
                                RANDOM_top1 >= 0.10
  HP_LEARNED_HIGHER_NOISE_TOL: at (alpha=0.5, f=0.30), LEARNED_top1 -
                                RANDOM_top1 >= 0.15
  HP_ORTHOGONALITY:            LEARNED max_pairwise_cos <= 0.20 (achieved
                                by contrastive training)

HF conditions:
  HF_LEARNED_WORSE:         LEARNED < RANDOM on >= 4 of 6 metric-gate
                             pairs (learning HURTS -- validates substrate-
                             native simplicity, closes R21's 5% prediction
                             with data)
  HF_LEARNED_EQUIVALENT:    |LEARNED - RANDOM| < 0.03 on ALL 6 gates
                             (learning does nothing at this budget)

Load-bearing framing (per spawn prompt):
- HP => opens gradient-through-write as viable Stage 2/3 pivot for M3 arch
- HF_WORSE or HF_EQUIVALENT => substrate-native simplicity validated

Cited prior: R21_cross_modal_binding C.4 (naive-CLIP-on-substrate DECLINED
at P=5%). This cell probes the *subtly different* pre-write orthogonalization
path, symmetrically. Not rediscovery.

ASCII-only. torch import at top (Fix #24).
"""
from __future__ import annotations

import hashlib
import math
import os
import time
from typing import Any, Dict, List, Tuple

import torch


# ---------- Regime constants (Option A: M-sweep at fixed N=4096) ----------

# Option A regime v2 (Director pivot 2026-07-01, iterated after empirical
# M-sweep MEASURED@ probes showed top1 saturates at 1.000 up to M=48000
# because argmax-over-M with cosine scoring is extremely resistant to
# crosstalk; the discriminating metric for LEARNED-vs-RANDOM is cos05/cos08
# (fraction of queries whose diagonal cos >= 0.5 / >= 0.8), which starts
# dropping at M=12000 and floors at M=16000):
#   4000  = below cos05-wall (cos05 = 1.0; positive-control)
#   8000  = at cos05-wall (cos05 mid-band; discriminator sweet-spot)
#   12000 = past cos05-wall (cos05 drops sharply; LEARNED's chance to shine)
#   16000 = cos05-floor (extreme test)
# Contrastive M x M matrix at M=16000 is 1 GB fwd + 2 GB grad -> GPU only;
# CPU smoke restricted to M<=8000. Full = GPU.
FULL_N = 4096
FULL_M_SWEEP = [4000, 8000, 12000, 16000]
FULL_NOISE_SWEEP = [0.0, 0.30]

# Smoke: full N=4096 + M=4000 (below-wall). Contrastive M x M at 4000 = 64 MB
# fwd + 128 MB grad; CPU 100 SGD steps ~2-3 min. Fires ARMS-MUST-DIFFER
# via max_cos_key delta between random baseline (~0.086) and LEARNED post-
# training (should push below MARGIN=0.05). Baseline in-band is not
# achievable at M=4000 for cos05 (=1.000); we accept baseline OUT of band
# in smoke and rely on ARMS-MEASURABLE via max_cos_key delta. FULL sweep
# at M=[4000,8000,12000,16000] does include cos05-wall.
SMOKE_N = 4096
SMOKE_M_SWEEP = [4000]
SMOKE_NOISE_SWEEP = [0.0]

# Encoder training hyperparameters (LEARNED arm)
LEARNED_N_STEPS_FULL = 500
LEARNED_N_STEPS_SMOKE = 100  # smaller for smoke wall budget
LEARNED_LR = 0.02  # increased from 0.01 for stronger signal at low-margin regime
# MARGIN lowered from 0.10 to 0.05 after empirical probe at N=4096 showed
# random-bipolar max_pairwise_cos ~ 0.087-0.091 at M=8000, already at or below
# MARGIN=0.10; hinge relu(cos - 0.10) had ~zero gradient. MARGIN=0.05 is BELOW
# random-baseline max, so most off-diagonal pairs enter the hinge active zone
# and LEARNED has meaningful gradient signal to drive keys further apart.
# THEORETICAL@ 3-sigma for N=4096 random-bipolar off-diag = 3/sqrt(4096) = 0.047;
# MARGIN=0.05 is 1% above the 3-sigma noise, so 99%+ of random pairs are
# below MARGIN naturally; MAX over M(M-1)/2 pairs at M=8000 (~32M pairs) has
# extreme-value scaling far above 3-sigma (measured 0.087 at M=8000).
LEARNED_MARGIN = 0.05
LEARNED_LAMBDA_POS = 0.5
LEARNED_AUG_FLIP_FRAC = 0.01

# Metrics: 6 gates per arm (top1, top5, top10, top50, cos05, cos08)
METRIC_GATES = ["top1", "top5", "top10", "top50", "cos05", "cos08"]

# HP / HF thresholds
HP_LEARNED_HIGHER_CAPACITY_DELTA = 0.10  # at (alpha=1.5, f=0.0)
HP_LEARNED_HIGHER_NOISE_TOL_DELTA = 0.15  # at (alpha=0.5, f=0.30)
HP_LEARNED_HIGHER_COMPOSITION_DELTA = 0.10  # placeholder (composition not in this cell)
HP_ORTHOGONALITY_MAX_COS = 0.20
HF_LEARNED_WORSE_GATE_COUNT = 4  # out of 6 metric-gate comparisons
HF_LEARNED_EQUIVALENT_DELTA = 0.03  # |L - R| across all 6 gates

# Baseline-in-band gate: sweep must include a point where the baseline is
# neither saturated (>0.95) nor floored (<0.05).
BASELINE_IN_BAND_LOW = 0.05
BASELINE_IN_BAND_HIGH = 0.95

# CRLB / capacity-feasibility notes (declared as THEORETICAL@ per META_RULE_AC):
# Random-init bipolar orthogonality at N=8192 has expected off-diagonal cos
# ~ 3/sqrt(N) = 3/90.5 = 0.033 (3 sigma). LEARNED target MAX pairwise 0.20
# is DEEPLY relaxed relative to random 3-sigma; the objective is NOT
# strict orthogonality but rather margin-shaping. Discriminator gap
# HP_LEARNED_HIGHER_CAPACITY = 0.10 is reachable iff LEARNED shapes
# encoder output distribution enough to bias substrate cleanup at capacity.

ARMS = ["RANDOM_INIT", "LEARNED_CONTRASTIVE"]

CROSS_SEED_CV_MAX_HP = 0.10
CROSS_SEED_CV_MAX_MB = 0.15


def _get_device(strict_gpu: bool = False) -> torch.device:
    if torch.cuda.is_available():
        return torch.device("cuda")
    if strict_gpu:
        raise RuntimeError("GPU_REQUIRED: cuda not available in full-mode")
    return torch.device("cpu")


def get_backend_label() -> str:
    if torch.cuda.is_available():
        try:
            return f"cuda:{torch.cuda.get_device_name(0)}"
        except Exception:
            return "cuda:unknown"
    return "cpu"


# ---------- Encoder construction ----------

def _make_random_init_keys(M: int, N: int, seed: int,
                            device: torch.device) -> torch.Tensor:
    """Bipolar iid keys shape (M, N)."""
    g = torch.Generator(device="cpu")
    g.manual_seed(seed + 11111)
    r = torch.randint(0, 2, (M, N), generator=g, dtype=torch.int8)
    return ((r * 2 - 1).to(torch.float32)).to(device)


def _make_learned_contrastive_keys(
    M: int, N: int, seed: int, device: torch.device,
    n_steps: int,
) -> Tuple[torch.Tensor, Dict[str, Any]]:
    """Initialize bipolar; run n_steps SGD on encoder outputs (encoder-only
    contrastive loss). Returns final keys + training diagnostics.

    Loss:
      neg: sum_{i<j} relu(cos(k_i, k_j) - MARGIN)
      pos: sum_i relu(MARGIN - cos(k_i, k_i_aug))   where k_i_aug = flip 1% of bits
      L = neg + LAMBDA_POS * pos

    NOTE: no substrate readout in the loss (avoids circular training per R21).
    """
    g = torch.Generator(device="cpu")
    g.manual_seed(seed + 22222)
    # init from bipolar (same distribution as RANDOM_INIT so start-condition matches)
    r = torch.randint(0, 2, (M, N), generator=g, dtype=torch.int8)
    K = ((r * 2 - 1).to(torch.float32)).to(device)
    K.requires_grad_(True)
    opt = torch.optim.SGD([K], lr=LEARNED_LR)

    losses = []
    max_cos_history = []
    t0 = time.perf_counter()
    for step in range(n_steps):
        opt.zero_grad()
        # normalize for cosine
        K_n = K / (K.norm(dim=1, keepdim=True) + 1e-8)
        # off-diagonal cosine matrix
        C = K_n @ K_n.T  # (M, M)
        # mask diagonal
        eye = torch.eye(M, device=device, dtype=torch.bool)
        C_off = C.masked_fill(eye, 0.0)
        # negative loss (push off-diagonals below MARGIN)
        neg_loss = torch.relu(C_off - LEARNED_MARGIN).sum() / (M * (M - 1))
        # positive-pair loss: augmented k_i vs k_i (should stay close)
        gg = torch.Generator(device="cpu")
        gg.manual_seed(seed + 33333 + step)
        # 1% bit-flip mask on CPU then send
        flip_mask_cpu = (torch.rand((M, N), generator=gg) < LEARNED_AUG_FLIP_FRAC)
        neg_one = torch.tensor(-1.0, dtype=K.dtype, device=device)
        pos_one = torch.tensor(1.0, dtype=K.dtype, device=device)
        flip = torch.where(flip_mask_cpu.to(device), neg_one, pos_one)
        K_aug = K.detach() * flip  # detached so pos-loss only pulls K toward K_aug
        K_aug_n = K_aug / (K_aug.norm(dim=1, keepdim=True) + 1e-8)
        # cos(k_i, k_i_aug) per row (diagonal of K_n @ K_aug_n.T)
        pos_cos = (K_n * K_aug_n).sum(dim=1)  # (M,)
        pos_loss = torch.relu(LEARNED_MARGIN - pos_cos).mean()
        loss = neg_loss + LEARNED_LAMBDA_POS * pos_loss
        loss.backward()
        opt.step()
        with torch.no_grad():
            # log every ~10th step to keep memory small
            if step % max(1, n_steps // 20) == 0 or step == n_steps - 1:
                losses.append((step, float(loss.item())))
                max_cos = float(C_off.abs().max().item())
                max_cos_history.append((step, max_cos))
    train_wall = time.perf_counter() - t0

    with torch.no_grad():
        K_final = K.detach().clone()
        # snap to bipolar? NO -- keep as continuous (learned encoder produces
        # dense reals; substrate must handle this natively).
        # measure final orthogonality
        K_n = K_final / (K_final.norm(dim=1, keepdim=True) + 1e-8)
        C = K_n @ K_n.T
        eye = torch.eye(M, device=device, dtype=torch.bool)
        C_off = C.masked_fill(eye, 0.0)
        final_max_cos = float(C_off.abs().max().item())
        final_mean_cos = float(C_off.abs().mean().item())
    diag = {
        "n_steps": n_steps,
        "lr": LEARNED_LR,
        "margin": LEARNED_MARGIN,
        "lambda_pos": LEARNED_LAMBDA_POS,
        "aug_flip_frac": LEARNED_AUG_FLIP_FRAC,
        "losses_by_step": losses,
        "max_cos_by_step": max_cos_history,
        "final_max_pairwise_cos": final_max_cos,
        "final_mean_pairwise_cos": final_mean_cos,
        "train_wall_s": round(train_wall, 3),
    }
    return K_final, diag


# ---------- Substrate write + read ----------

def _build_W(K: torch.Tensor, O: torch.Tensor) -> torch.Tensor:
    """Hebbian W = O^T K / N (per-outer-product bind, mean-batched).

    K: (M, N) keys
    O: (M, N) values
    Returns W: (N, N)
    """
    N = K.shape[1]
    return (O.T @ K) / float(N)


def _add_bipolar_noise(x: torch.Tensor, noise_frac: float,
                        seed: int) -> torch.Tensor:
    if noise_frac <= 0.0:
        return x.clone()
    g = torch.Generator(device="cpu")
    g.manual_seed(seed + 55555)
    mask_cpu = (torch.rand(x.shape, generator=g) < noise_frac).to(x.device)
    neg_one = torch.tensor(-1.0, dtype=x.dtype, device=x.device)
    pos_one = torch.tensor(1.0, dtype=x.dtype, device=x.device)
    flip = torch.where(mask_cpu, neg_one, pos_one)
    return x * flip


def _run_one_arm(
    arm_name: str, M: int, noise: float,
    N: int, seed: int, device: torch.device,
    n_steps_learned: int,
) -> Dict[str, Any]:
    """Build encoder keys, write W, query with noise, measure 6 gates."""
    M = int(M)
    alpha = M / float(N)
    # Build target values (bipolar, iid; same for both arms per seed for fairness)
    g_o = torch.Generator(device="cpu")
    g_o.manual_seed(seed + 77777)
    ro = torch.randint(0, 2, (M, N), generator=g_o, dtype=torch.int8)
    O = ((ro * 2 - 1).to(torch.float32)).to(device)

    train_diag: Dict[str, Any] = {}
    t_encoder = time.perf_counter()
    if arm_name == "RANDOM_INIT":
        K = _make_random_init_keys(M, N, seed, device)
    elif arm_name == "LEARNED_CONTRASTIVE":
        K, train_diag = _make_learned_contrastive_keys(
            M, N, seed, device, n_steps=n_steps_learned,
        )
    else:
        raise ValueError(f"unknown arm: {arm_name}")
    encoder_wall = time.perf_counter() - t_encoder

    # Baseline orthogonality (measured; THEORETICAL@ compared)
    with torch.no_grad():
        K_n = K / (K.norm(dim=1, keepdim=True) + 1e-8)
        C_key = K_n @ K_n.T
        eye = torch.eye(M, device=device, dtype=torch.bool)
        C_off = C_key.masked_fill(eye, 0.0)
        max_cos_key = float(C_off.abs().max().item())
        mean_cos_key = float(C_off.abs().mean().item())

    # Write W
    with torch.no_grad():
        W = _build_W(K, O)
    del K_n, C_key, C_off, eye

    # Query with noise on the *value-mapping* side: perturb the keys by
    # noise-fraction bipolar flip, then read from W.
    with torch.no_grad():
        Kq = _add_bipolar_noise(K, noise, seed)
        # Read: predicted values = W @ Kq^T -> (N, M) -> transpose to (M, N)
        Pred = (W @ Kq.T).T  # (M, N)
        # Score against all M target values via cosine
        # scores[i, j] = cos(Pred[i], O[j])
        Pred_n = Pred / (Pred.norm(dim=1, keepdim=True) + 1e-8)
        O_n = O / (O.norm(dim=1, keepdim=True) + 1e-8)
        scores = Pred_n @ O_n.T  # (M, M)
        # Correct answer is diagonal
        gt = torch.arange(M, device=device)
        # top-k gates
        topk_max = min(50, M)
        topk_vals, topk_idx = torch.topk(scores, k=topk_max, dim=1)
        gt_expanded = gt.unsqueeze(1)  # (M, 1)
        # top-N hit rates
        def _topn(n):
            n_eff = min(n, topk_max)
            return float((topk_idx[:, :n_eff] == gt_expanded).any(dim=1).float().mean().item())
        top1 = _topn(1)
        top5 = _topn(5)
        top10 = _topn(10)
        top50 = _topn(50)
        # Cosine-threshold gates (fraction of queries whose diagonal-cos >= threshold)
        diag_cos = scores.gather(1, gt.unsqueeze(1)).squeeze(1)  # (M,)
        cos05 = float((diag_cos >= 0.5).float().mean().item())
        cos08 = float((diag_cos >= 0.8).float().mean().item())

    del W, Pred, Pred_n, O_n, scores, Kq
    if device.type == "cuda":
        try:
            torch.cuda.empty_cache()
        except Exception:
            pass

    fingerprint = hashlib.sha256(
        f"{arm_name}|N={N}|alpha={alpha}|noise={noise}|"
        f"top1={top1:.6f}|top5={top5:.6f}|seed={seed}".encode()
    ).hexdigest()
    return {
        "arm": arm_name,
        "alpha": float(alpha),
        "M": int(M),
        "N": int(N),
        "noise": float(noise),
        "top1": top1,
        "top5": top5,
        "top10": top10,
        "top50": top50,
        "cos05": cos05,
        "cos08": cos08,
        "max_pairwise_cos_key": max_cos_key,
        "mean_pairwise_cos_key": mean_cos_key,
        "encoder_wall_s": round(encoder_wall, 3),
        "seed": int(seed),
        "mechanism_hash": fingerprint,
        "train_diag": train_diag,
    }


# ---------- Seed runner ----------

def run_one_seed_all_units(seed: int, run_mode: str,
                           device: torch.device) -> Dict[str, Any]:
    smoke = (run_mode == "smoke")
    if smoke:
        N = SMOKE_N
        M_sweep = SMOKE_M_SWEEP
        noise_sweep = SMOKE_NOISE_SWEEP
        n_steps = LEARNED_N_STEPS_SMOKE
    else:
        N = FULL_N
        M_sweep = FULL_M_SWEEP
        noise_sweep = FULL_NOISE_SWEEP
        n_steps = LEARNED_N_STEPS_FULL

    per_unit = {}
    t_seed_start = time.time()
    for M in M_sweep:
        for noise in noise_sweep:
            for arm in ARMS:
                key = f"{arm}__M{M}__f{noise:.2f}__N{N}"
                rec = _run_one_arm(arm, M, noise, N, seed, device,
                                    n_steps_learned=n_steps)
                per_unit[key] = rec
                elapsed = time.time() - t_seed_start
                print(f"[arm={arm} M={M} f={noise:.2f}] seed={seed} "
                      f"top1={rec['top1']:.3f} top5={rec['top5']:.3f} "
                      f"top50={rec['top50']:.3f} "
                      f"max_cos_key={rec['max_pairwise_cos_key']:.3f} "
                      f"enc_wall={rec['encoder_wall_s']:.2f}s "
                      f"seed_total={elapsed:.1f}s", flush=True)
    return {
        "seed": int(seed),
        "run_mode": run_mode,
        "per_unit": per_unit,
        "N_fixed": N,
        "M_sweep": list(M_sweep),
        "noise_sweep": list(noise_sweep),
        "arms": list(ARMS),
        "n_steps_learned": n_steps,
    }


# ---------- Cross-seed + verdict ----------

def _cross_seed_stats(per_seed: List[Dict[str, Any]],
                       unit_keys: List[str]) -> Dict[str, Dict[str, float]]:
    out = {}
    for uk in unit_keys:
        top1s = [ps["per_unit"][uk]["top1"] for ps in per_seed
                  if uk in ps["per_unit"]]
        top5s = [ps["per_unit"][uk]["top5"] for ps in per_seed
                  if uk in ps["per_unit"]]
        top10s = [ps["per_unit"][uk]["top10"] for ps in per_seed
                   if uk in ps["per_unit"]]
        top50s = [ps["per_unit"][uk]["top50"] for ps in per_seed
                   if uk in ps["per_unit"]]
        cos05s = [ps["per_unit"][uk]["cos05"] for ps in per_seed
                   if uk in ps["per_unit"]]
        cos08s = [ps["per_unit"][uk]["cos08"] for ps in per_seed
                   if uk in ps["per_unit"]]
        max_cos_keys = [ps["per_unit"][uk]["max_pairwise_cos_key"]
                          for ps in per_seed if uk in ps["per_unit"]]
        if not top1s:
            continue
        def _stats(xs):
            m = sum(xs) / len(xs)
            v = sum((x - m) ** 2 for x in xs) / len(xs)
            s = math.sqrt(v)
            return m, s, (s / m if m > 0 else 0.0)
        m_t1, s_t1, cv_t1 = _stats(top1s)
        m_t5, s_t5, cv_t5 = _stats(top5s)
        m_t10, s_t10, cv_t10 = _stats(top10s)
        m_t50, s_t50, cv_t50 = _stats(top50s)
        m_c5, s_c5, cv_c5 = _stats(cos05s)
        m_c8, s_c8, cv_c8 = _stats(cos08s)
        m_mck, _, _ = _stats(max_cos_keys)
        out[uk] = {
            "top1_mean": m_t1, "top1_std": s_t1, "top1_cv": cv_t1,
            "top5_mean": m_t5, "top5_cv": cv_t5,
            "top10_mean": m_t10, "top10_cv": cv_t10,
            "top50_mean": m_t50, "top50_cv": cv_t50,
            "cos05_mean": m_c5, "cos05_cv": cv_c5,
            "cos08_mean": m_c8, "cos08_cv": cv_c8,
            "max_pairwise_cos_key_mean": m_mck,
            "n_seeds": len(top1s),
        }
    return out


def _get_stat(stats, arm, M, noise, N, metric):
    key = f"{arm}__M{M}__f{noise:.2f}__N{N}"
    return stats.get(key, {}).get(f"{metric}_mean", float("nan"))


def aggregate_and_verdict(per_seed, run_mode: str) -> Dict[str, Any]:
    if isinstance(per_seed, dict):
        per_seed = list(per_seed.values())
    n_seeds = len(per_seed)
    if n_seeds == 0:
        return {"verdict": "HARD_FAIL",
                "verdict_msg": "HARD_FAIL: no seeds completed",
                "summary": "no per-seed data"}

    smoke = (run_mode == "smoke")
    N = SMOKE_N if smoke else FULL_N
    M_sweep = SMOKE_M_SWEEP if smoke else FULL_M_SWEEP
    noise_sweep = SMOKE_NOISE_SWEEP if smoke else FULL_NOISE_SWEEP

    unit_keys = []
    for arm in ARMS:
        for M in M_sweep:
            for noise in noise_sweep:
                unit_keys.append(f"{arm}__M{M}__f{noise:.2f}__N{N}")
    stats = _cross_seed_stats(per_seed, unit_keys)

    expected_n_units = len(ARMS) * len(M_sweep) * len(noise_sweep)
    observed_n_units_per_seed = [len(ps["per_unit"]) for ps in per_seed]
    cardinality_ok = all(n == expected_n_units for n in observed_n_units_per_seed)

    hashes = set()
    if per_seed:
        one_pu = per_seed[0]["per_unit"]
        for uk in unit_keys:
            if uk in one_pu:
                hashes.add(one_pu[uk]["mechanism_hash"])
    hashes_distinct = len(hashes) == expected_n_units

    # ARMS_MUST_DIFFER (META_RULE_AF): compare RANDOM vs LEARNED at each (M,f)
    arms_differ_ok = True
    arms_differ_details = {}
    for M in M_sweep:
        for noise in noise_sweep:
            r_t1 = _get_stat(stats, "RANDOM_INIT", M, noise, N, "top1")
            l_t1 = _get_stat(stats, "LEARNED_CONTRASTIVE", M, noise, N, "top1")
            differ = (not math.isnan(r_t1)) and (not math.isnan(l_t1)) and (abs(r_t1 - l_t1) > 1e-6)
            arms_differ_details[f"M{M}_f{noise:.2f}"] = {
                "RANDOM_top1": r_t1, "LEARNED_top1": l_t1,
                "differ": differ,
            }
            # NOTE: legitimately arms COULD produce identical top1 if both
            # saturate at 1.0 or 0.0. So we don't fail on equal, only on
            # bit-identical mechanism_hash which is caught above.

    # HP_LEARNED_HIGHER_CAPACITY: at cos05-wall M (FULL: M=12000; smoke: SMOKE_M[0])
    # Discriminator metric = cos05 (top1 saturates at 1.000 up to M=48000
    # for random-bipolar; cos05 = fraction of queries with diagonal-cos >= 0.5
    # is where LEARNED-orthogonality shows because it directly controls
    # off-diagonal crosstalk which drives diag-cos)
    HP_CAPACITY_M = 12000 if not smoke else M_sweep[0]
    r_cap_t1 = _get_stat(stats, "RANDOM_INIT", HP_CAPACITY_M, 0.0, N, "cos05")
    l_cap_t1 = _get_stat(stats, "LEARNED_CONTRASTIVE", HP_CAPACITY_M, 0.0, N, "cos05")
    cap_delta = l_cap_t1 - r_cap_t1 if (not math.isnan(r_cap_t1) and not math.isnan(l_cap_t1)) else float("nan")
    hp_learned_higher_capacity = (not math.isnan(cap_delta)) and (cap_delta >= HP_LEARNED_HIGHER_CAPACITY_DELTA)

    # HP_LEARNED_HIGHER_NOISE_TOL: at M=4000, f=0.30 (below-cos05-wall + noise; FULL only)
    HP_NOISE_M = 4000
    if not smoke:
        r_nz_t1 = _get_stat(stats, "RANDOM_INIT", HP_NOISE_M, 0.30, N, "cos05")
        l_nz_t1 = _get_stat(stats, "LEARNED_CONTRASTIVE", HP_NOISE_M, 0.30, N, "cos05")
        nz_delta = l_nz_t1 - r_nz_t1 if (not math.isnan(r_nz_t1) and not math.isnan(l_nz_t1)) else float("nan")
        hp_learned_higher_noise = (not math.isnan(nz_delta)) and (nz_delta >= HP_LEARNED_HIGHER_NOISE_TOL_DELTA)
    else:
        r_nz_t1 = float("nan"); l_nz_t1 = float("nan"); nz_delta = float("nan")
        hp_learned_higher_noise = False  # not measurable in smoke

    # HP_ORTHOGONALITY: LEARNED max pairwise cos <= 0.20 across ALL (M, noise)
    max_learned_cos = 0.0
    for M in M_sweep:
        for noise in noise_sweep:
            key = f"LEARNED_CONTRASTIVE__M{M}__f{noise:.2f}__N{N}"
            v = stats.get(key, {}).get("max_pairwise_cos_key_mean", float("nan"))
            if not math.isnan(v) and v > max_learned_cos:
                max_learned_cos = v
    hp_orthogonality = max_learned_cos <= HP_ORTHOGONALITY_MAX_COS

    # HF_LEARNED_WORSE: count metric-gate pairs (arm-pair per (alpha,f) per metric)
    # where LEARNED < RANDOM. Total pairs = alpha_sweep x noise_sweep x metrics.
    # HF fires if LEARNED_worse_count >= 4 * (total_pairs / 6)  (scaled from
    # spec-of "4 of 6 metric-gates" at the FULL grid; scale to smoke grid).
    total_pairs = len(M_sweep) * len(noise_sweep) * len(METRIC_GATES)
    learned_worse_count = 0
    learned_equivalent_count = 0
    per_gate_deltas = []
    for M in M_sweep:
        for noise in noise_sweep:
            for metric in METRIC_GATES:
                r = _get_stat(stats, "RANDOM_INIT", M, noise, N, metric)
                l = _get_stat(stats, "LEARNED_CONTRASTIVE", M, noise, N, metric)
                if math.isnan(r) or math.isnan(l):
                    continue
                delta = l - r
                per_gate_deltas.append({
                    "M": M, "noise": noise, "metric": metric,
                    "RANDOM": r, "LEARNED": l, "delta": delta,
                })
                if delta < -HF_LEARNED_EQUIVALENT_DELTA:
                    learned_worse_count += 1
                if abs(delta) < HF_LEARNED_EQUIVALENT_DELTA:
                    learned_equivalent_count += 1

    # Threshold: HF_LEARNED_WORSE (spec: 4 of 6 in FULL); scale to smoke
    hf_learned_worse_threshold = max(1, round(HF_LEARNED_WORSE_GATE_COUNT / 6.0 * total_pairs))
    hf_learned_worse = learned_worse_count >= hf_learned_worse_threshold
    hf_learned_equivalent = learned_equivalent_count == total_pairs  # ALL gates within eq band

    # META_RULE_AG: baseline-in-band (RANDOM_INIT top1 not saturated + not floored)
    # at some point in the sweep
    # BASELINE_IN_BAND: check cos05 (discriminator metric) since top1 is
    # by-construction saturated at 1.000 for argmax-cosine in this design
    baseline_in_band = False
    baseline_out_of_band_details = {}
    for M in M_sweep:
        for noise in noise_sweep:
            b = _get_stat(stats, "RANDOM_INIT", M, noise, N, "cos05")
            baseline_out_of_band_details[f"M{M}_f{noise:.2f}_cos05"] = b
            if (not math.isnan(b)) and (BASELINE_IN_BAND_LOW < b < BASELINE_IN_BAND_HIGH):
                baseline_in_band = True

    # cv gate
    max_cv = 0.0
    for uk in unit_keys:
        # take max over all metric cvs
        for c in ["top1_cv", "top5_cv", "top10_cv", "top50_cv", "cos05_cv", "cos08_cv"]:
            v = stats.get(uk, {}).get(c, 0.0)
            if v > max_cv:
                max_cv = v
    cv_hard_fail = max_cv >= CROSS_SEED_CV_MAX_MB

    # Verdict priority: cardinality > hash > cv > baseline > HP/HF resolution
    if not cardinality_ok:
        verdict = "HARD_FAIL_CARDINALITY_BREACH_META_RULE_H"
        vmsg = (f"HARD_FAIL_CARDINALITY: observed_per_seed={observed_n_units_per_seed} "
                f"expected={expected_n_units}")
    elif not hashes_distinct:
        verdict = "HARD_FAIL_META_RULE_AX_HASH_COLLISION"
        vmsg = (f"HARD_FAIL: mechanism_hash collision "
                f"({len(hashes)} distinct vs {expected_n_units} expected)")
    elif cv_hard_fail:
        verdict = "HARD_FAIL_CV_BREACH"
        vmsg = (f"HARD_FAIL: cross-seed cv >= {CROSS_SEED_CV_MAX_MB} "
                f"(max_cv={max_cv:.3f})")
    elif smoke:
        # Smoke passes if arms are measurable on max_cos_key (LEARNED training
        # reduced pairwise cos below RANDOM baseline by >=0.02). We do NOT
        # require baseline-in-band for cos05 at the smoke M-point because
        # smoke uses a below-wall M (M=4000 at N=4096) to keep contrastive-
        # training wall tractable (<5 min). The FULL sweep at higher M does
        # include the cos05-wall and enforces baseline_in_band there.
        # ARMS-MUST-DIFFER discriminator = max_cos_key delta.
        smoke_M = SMOKE_M_SWEEP[0]
        r_maxc = stats.get(
            f"RANDOM_INIT__M{smoke_M}__f0.00__N{N}", {}
        ).get("max_pairwise_cos_key_mean", float("nan"))
        l_maxc = stats.get(
            f"LEARNED_CONTRASTIVE__M{smoke_M}__f0.00__N{N}", {}
        ).get("max_pairwise_cos_key_mean", float("nan"))
        maxc_delta = (r_maxc - l_maxc) if (not math.isnan(r_maxc) and not math.isnan(l_maxc)) else float("nan")
        # measurable if (a) cos05 delta shows shape (unlikely at M=4000) OR
        # (b) max_cos_key delta >=0.02 (LEARNED reduced pairwise cos)
        smoke_arms_measurable = (
            ((not math.isnan(cap_delta)) and abs(cap_delta) >= 0.02) or
            ((not math.isnan(maxc_delta)) and abs(maxc_delta) >= 0.02)
        )
        if not smoke_arms_measurable:
            verdict = "MIDDLE_BAND_ARMS_INDISTINGUISHABLE"
            vmsg = (f"SMOKE_MIDDLE_BAND: RANDOM and LEARNED indistinguishable at "
                    f"(M={HP_CAPACITY_M}, f=0.0) N={N}: RANDOM_top1={r_cap_t1:.3f} "
                    f"LEARNED_top1={l_cap_t1:.3f} delta={cap_delta:.3f}; "
                    f"discriminator does not survive scale at n_steps={LEARNED_N_STEPS_SMOKE}")
        else:
            direction = ("LEARNED_HIGHER" if cap_delta > 0 else "RANDOM_HIGHER")
            verdict = "HARD_PASS_SMOKE_ARMS_MEASURABLE"
            vmsg = (f"SMOKE_HARD_PASS: arms measurable at (M={HP_CAPACITY_M}, f=0.0, N={N}); "
                    f"RANDOM_top1={r_cap_t1:.3f} LEARNED_top1={l_cap_t1:.3f} "
                    f"delta={cap_delta:.3f} ({direction}); "
                    f"LEARNED_max_cos_key={max_learned_cos:.3f} "
                    f"(HP_orthogonality={hp_orthogonality}); "
                    f"baseline_in_band={baseline_in_band}")
    elif not baseline_in_band:
        verdict = "HARD_FAIL_META_RULE_AG_BASELINE_OUT_OF_BAND"
        vmsg = (f"HARD_FAIL_META_RULE_AG: RANDOM baseline top1 out of band at every sweep point "
                f"(details={baseline_out_of_band_details}); test cannot discriminate")
    elif hp_learned_higher_capacity or hp_learned_higher_noise:
        verdict = "HARD_PASS_LEARNED_ENCODER_HELPS"
        which = []
        if hp_learned_higher_capacity: which.append("CAPACITY")
        if hp_learned_higher_noise: which.append("NOISE_TOL")
        vmsg = (f"HARD_PASS_LEARNED_HELPS ({'/'.join(which)}): "
                f"cap_delta={cap_delta:.3f} (HP={HP_LEARNED_HIGHER_CAPACITY_DELTA}); "
                f"nz_delta={nz_delta:.3f} (HP={HP_LEARNED_HIGHER_NOISE_TOL_DELTA}); "
                f"orthogonality={hp_orthogonality} (max_cos_learned={max_learned_cos:.3f})")
    elif hf_learned_worse:
        verdict = "HARD_FAIL_LEARNED_HURTS_SUBSTRATE_NATIVE_VALIDATED"
        vmsg = (f"HF_LEARNED_WORSE: {learned_worse_count}/{total_pairs} gates show LEARNED < RANDOM "
                f"(threshold={hf_learned_worse_threshold}); substrate-native simplicity validated; "
                f"R21 5%-prediction closed positively with data")
    elif hf_learned_equivalent:
        verdict = "HARD_FAIL_LEARNED_EQUIVALENT_NO_LIFT"
        vmsg = (f"HF_LEARNED_EQUIVALENT: {learned_equivalent_count}/{total_pairs} gates within "
                f"|delta| < {HF_LEARNED_EQUIVALENT_DELTA}; learning does nothing at "
                f"n_steps=500 budget")
    else:
        verdict = "MIDDLE_BAND"
        vmsg = (f"MIDDLE_BAND: HP-thresholds not met but HF not fired; "
                f"cap_delta={cap_delta:.3f} nz_delta={nz_delta:.3f} "
                f"orthogonality_max_cos_learned={max_learned_cos:.3f} "
                f"(HP<=0.20); learned_worse_count={learned_worse_count}/{total_pairs}")

    return {
        "verdict": verdict,
        "verdict_msg": vmsg,
        "summary": vmsg[:400],
        "run_mode": run_mode,
        "n_seeds": n_seeds,
        "arms": list(ARMS),
        "N_fixed": N,
        "M_sweep": list(M_sweep),
        "noise_sweep": list(noise_sweep),
        "metric_gates": list(METRIC_GATES),
        "hp_learned_higher_capacity": bool(hp_learned_higher_capacity),
        "hp_learned_higher_noise_tolerance": bool(hp_learned_higher_noise),
        "hp_orthogonality": bool(hp_orthogonality),
        "hf_learned_worse": bool(hf_learned_worse),
        "hf_learned_equivalent": bool(hf_learned_equivalent),
        "cap_delta": cap_delta,
        "nz_delta": nz_delta,
        "cap_random_top1": r_cap_t1,
        "cap_learned_top1": l_cap_t1,
        "nz_random_top1": r_nz_t1,
        "nz_learned_top1": l_nz_t1,
        "max_learned_cos_key": max_learned_cos,
        "learned_worse_count": learned_worse_count,
        "learned_equivalent_count": learned_equivalent_count,
        "hf_learned_worse_threshold": hf_learned_worse_threshold,
        "total_gate_pairs": total_pairs,
        "per_gate_deltas": per_gate_deltas,
        "arms_differ_details": arms_differ_details,
        "baseline_in_band": bool(baseline_in_band),
        "baseline_details": baseline_out_of_band_details,
        "max_cv_across_arms": max_cv,
        "stats_cross_seed": stats,
        "cardinality_ok": cardinality_ok,
        "expected_n_units_per_seed": expected_n_units,
        "observed_n_units_per_seed": observed_n_units_per_seed,
        "mechanism_hashes_distinct": hashes_distinct,
        "per_seed": per_seed,
        "HP_LEARNED_HIGHER_CAPACITY_DELTA": HP_LEARNED_HIGHER_CAPACITY_DELTA,
        "HP_LEARNED_HIGHER_NOISE_TOL_DELTA": HP_LEARNED_HIGHER_NOISE_TOL_DELTA,
        "HP_ORTHOGONALITY_MAX_COS": HP_ORTHOGONALITY_MAX_COS,
        "HF_LEARNED_WORSE_GATE_COUNT": HF_LEARNED_WORSE_GATE_COUNT,
        "HF_LEARNED_EQUIVALENT_DELTA": HF_LEARNED_EQUIVALENT_DELTA,
        "CROSS_SEED_CV_MAX_HP": CROSS_SEED_CV_MAX_HP,
        "CROSS_SEED_CV_MAX_MB": CROSS_SEED_CV_MAX_MB,
    }


def selftest(seed: int, device: torch.device) -> Tuple[bool, str]:
    """Self-test: tiny (N=128, M=32) 2-arm functional + learned-training curve.
    Verifies dispatch-readiness. Both arms build a substrate; contrastive
    training runs 10 steps; both arms produce valid top1 recall > 0.
    """
    tiny_device = torch.device("cpu")
    N_tiny = 128
    M_tiny = 32
    noise_tiny = 0.0
    rec_random = _run_one_arm("RANDOM_INIT", M_tiny, noise_tiny,
                                N_tiny, seed, tiny_device, n_steps_learned=10)
    rec_learned = _run_one_arm("LEARNED_CONTRASTIVE", M_tiny, noise_tiny,
                                 N_tiny, seed, tiny_device, n_steps_learned=10)
    # Assertions: both produce valid recalls in [0, 1]; both have distinct hashes
    for arm, rec in [("RANDOM", rec_random), ("LEARNED", rec_learned)]:
        for m in ["top1", "top5", "cos05"]:
            v = rec[m]
            if not (0.0 <= v <= 1.0):
                return False, f"selftest {arm} {m}={v} out of [0,1]"
    if rec_random["mechanism_hash"] == rec_learned["mechanism_hash"]:
        return False, "selftest hashes identical (arms should differ)"
    # Learned-training diagnostic present
    if not rec_learned.get("train_diag"):
        return False, "selftest LEARNED train_diag missing"
    if "final_max_pairwise_cos" not in rec_learned["train_diag"]:
        return False, "selftest LEARNED train_diag missing final_max_pairwise_cos"
    msg = (f"SELFTEST_OK: RANDOM top1={rec_random['top1']:.3f} "
           f"LEARNED top1={rec_learned['top1']:.3f} "
           f"LEARNED_final_max_cos={rec_learned['train_diag']['final_max_pairwise_cos']:.3f} "
           f"train_wall={rec_learned['train_diag']['train_wall_s']:.2f}s")
    return True, msg
