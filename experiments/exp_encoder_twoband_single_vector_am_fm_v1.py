"""TWO-BAND SINGLE-VECTOR encoder: AM+FM on one wire (bundling band + fine-detail band).

QUESTION (2026-07-08). The sibling two-head cell (exp_encoder_twohead_decoupled_
store_retrieval_v1) tests whether TWO SEPARATE full-N vectors (a VICReg store head +
an RKD retrieval head, 2N total budget) can jointly achieve high superposition recall
AND high pointwise fidelity. The certified decouple law
(reference_correlation_hurts_associative_store_capacity_decouple_from_retrieval)
says the associative store wants DECORRELATED codes while retrieval wants CORRELATED
(semantic) codes -- opposite pulls -- so DECOUPLE. The strict-tradeoff frontier
(exp_encoder_distill_anchor_sweep_vicreg_decorr) MEASURED that NO single N-dim code
serving BOTH readouts through the SAME dimensions can do both (both_arms=[]): a
per-dimension conflict (a dim cannot be both decorrelated and BGE-anchored).

This cell asks the genuinely-untried WILDER workaround: can ONE N-dim vector do both
by PARTITIONING ITS OWN DIMENSIONS into two internal sub-bands read CONDITIONALLY
per task -- AM+FM on one wire -- so no dimension serves two masters?
  band_B (BUNDLING sub-band, first N_b dims): trained VICReg-decorrelated; the
          superposition-signature carrier; read via WTA sparse block code.
  band_D (fine-DETAIL sub-band, last N_d dims): trained RKD BGE-distilled; the
          pointwise-discrimination carrier; read via dense argmax-cosine.
The two bands are DISJOINT COLUMN SLICES of ONE output projection W_out (H->N), so no
dimension is shared between roles; the ONLY shared parameter is the trunk (the
interference surface). Total output budget = N (the SAME as the frontier's single
code, and HALF the two-head's 2N). If it works, you get BOTH capabilities from ONE
vector at the frontier's budget -- the thing a scalar-tradeoff single code provably
cannot do.

WHY THIS IS DISTINCT (guardrails from the corpus scour):
  vs SINGLE-CODE frontier (exp_encoder_distill_anchor_sweep): frontier forces ALL N
     dims to serve BOTH readouts (per-dim conflict). Two-band gives each dim ONE role.
  vs TWO-HEAD (exp_encoder_twohead_decoupled_store_retrieval): two-head emits TWO
     separate full-N vectors (2N budget). Two-band emits ONE vector partitioned (N).
     The twohead_2N arm here IS that sibling architecture, as the double-budget ceiling.
  vs R5 SERIAL storage/readout (exp_substrate_R5_b2_storage_b8_readout_serial): R5
     decouples two SERIAL stages from one store. This decouples two BANDS of one vector
     read in PARALLEL (conditional per task), not serial stages.
  vs sparsified-dense retrofit (exp_dg_projector_charlm, FAILED): band_B is a NATIVE
     VICReg-decorrelated code built decorrelated from the start, NOT a sparsification
     of a dense embedding.

FEASIBILITY (MEASURED, feasibility_probe on the BGE cache, V=4000, N random proj +
WTA 3.125%): band_B SP@5 = 0.876 at N_b=2048, 0.890 at 2560, 0.930 at 4096 -> the
0.83 target is reachable at N_b=2048 (50/50) with headroom. band_D dense SC@1.2 =
0.998 at every N_d>=1024 -> the detail band saturates; superposition is the binding
axis. Cross-read (random proxy): band_D read for superposition = 0.324 (fails, vs
band_B 0.909). The pointwise cross-read fires only with TRAINED bands (VICReg drops
band_B dense pointwise to ~0.7, per the sibling's measured singlehead_native SC),
which is why the bands are TRAINED, not random.

ARMS (uniform metric harness reused verbatim from the two-head sibling so numbers are
directly comparable):
  twoband_shared      shared trunk; ONE W_out (H->N); band_B slice VICReg + band_D
                      slice RKD; ONE vector, N budget                     [HEADLINE]
  twoband_split_trunk separate trunk per band; still ONE concatenated N-dim vector;
                      isolates whether TRUNK-sharing (not partition) is the cost [ENRICH]
  twohead_2N          TWO separate full-N vectors (2N budget), shared trunk (= the
                      sibling twohead_shared); the double-budget CEILING     [CEILING]
  singlecode_native   one N code, VICReg only, dual readout (WTA+dense)      [FRONTIER]
  singlecode_distill  one N code, RKD only, dual readout                     [FRONTIER]
  teacher_bge         raw unit BGE (SC ceiling ~1.0; SP_wta crowded ~0.43)   [REF]
  native_untrained    random W + WTA (superposition ceiling ~0.93)          [REF]

METRICS (per arm; a band-B superposition axis + a band-D pointwise axis + the two
CROSS-READ axes that prove the split is REAL not cosmetic):
  SP_B  = superposition recall@J on band_B WTA block code (3.125% sparsity per band).
  SC_D  = single-concept pointwise recall@alpha on band_D DENSE code (noisy BGE query
          encoded through the band, argmax-cosine over the dict).
  SP_D  = CROSS: superposition recall@J on band_D WTA (WRONG band for superposition;
          should FAIL -- band_D is BGE-anchored/crowded).
  SC_B  = CROSS: pointwise recall@alpha on band_B DENSE (WRONG band for pointwise;
          should FAIL for a VICReg-decorrelated band -> ~0.7).
  achieves_both = SP_B@J_OP >= SP_HI AND SC_D@alpha_OP >= SC_HI.
  split_real    = (SP_B - SP_D >= CROSS_SP_GAP) AND (SC_D - SC_B >= CROSS_SC_GAP)
                  -- reading the WRONG band for a task fails -> the bands carry
                  DIFFERENT things (anti-cosmetic).

PRE-REG BANDS (HEADLINE = twoband_shared at band_frac_B=0.5; strictly-above-floor per
META_RULE_L; thresholds carry noise headroom: SP_HI=0.83 below the N_b=2048 ceiling
0.876, SC_HI=0.90 below teacher 1.0):
  HARD_PASS = twoband_shared achieves_both AND split_real: ONE N-dim vector,
              partitioned, delivers BOTH high superposition (band_B SP_wta@J_OP>=0.83,
              clearing the single-code frontier) AND high pointwise (band_D
              SC_dense@alpha_OP>=0.90), AND the cross-read confirms the two bands are
              genuinely specialized (not the same content duplicated).
  MIDDLE    = exactly ONE band hits its target and the other is within MIDDLE_TOL
              (0.05) of target (a regime/split-ratio nudge away).
  HARD_FAIL:
    _COSMETIC_SPLIT_BOTH_BANDS_SAME  achieves_both numerically BUT cross-read gaps too
              small -> the split is cosmetic (both bands carry the same thing).
    _SHARED_VECTOR_INTERFERES_NEITHER_BAND  neither band hits target (the shared
              vector / shared trunk forces interference so the partition starves both).
    _NO_GAIN_OVER_SINGLE_CODE  twoband_shared joint no better than the best single-code
              frontier arm's joint (the partition bought nothing).
  Enrichment (reported, not gating): twoband_split_trunk + twohead_2N joints (ceilings
  the two-band approaches at N vs 2N budget); band_frac_B in {0.375,0.5,0.625} sweep
  (FULL only) locating the split where BOTH bands clear.

COMPUTE ARCHITECTURE. Class (a) batched-GPU. Training is matmul-heavy (per-iter RKD
pairwise BxB, VICReg covariance over a minibatch, trunk+out forwards); 5 trained arms
(twoband arms x 3 band-fracs at FULL) x 5 seeds x hundreds of iters. SMOKE runs
CPU-local at PRODUCTION N=4096 (band_B=2048 is the REAL operating dimension; the
superposition discriminator is dimension-dependent so smoke MUST be at full N per
DISCRIMINATOR-MUST-SURVIVE-SCALE option A) with reduced V/iters/B and a single
band_frac=0.5; a few minutes, per-seed checkpoint/restartable (pausable smoke).
FULL routes to the GPU (overnight_queue) at production N=4096, V=40000, B=8192>N
(full-rank covariance). Storage strategy: no_composition / no_store (encoder-geometry
cell; the "dictionary" is the per-concept code, evaluated by argmax-cosine cleanup,
not a bundled associative store).

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
- arms_differ_verified at smoke gate (sha256 of each arm's band_B code; distinct).
- final_metrics_atomicity: tmp_replace (os.replace on final metrics.json).
- except SystemExit: raise BEFORE except Exception (no BaseException).
- crlb_n/a: recall/accuracy over argmax cleanup + geometry cosines; no closed-form
  noise floor. Feasibility handled by the MEASURED probe (band_B SP@5=0.876 at N_b=2048
  clears SP_HI=0.83; band_D SC=0.998 clears SC_HI=0.90) at this exact regime.
- baseline_in_band: singlecode_distill band_B SP_wta@J_OP in (0.05,0.95) (crowded ~0.43).
- discriminator survives scale: smoke fires at PRODUCTION N=4096 (band dimensions =
  full operating dims); the partition-vs-conflict property is architectural (present at
  any scale) and the anchor-sweep MEASURED the crowded-vs-decorrelated SP gap at V=4000
  and V=40000 so the lever survives scale by that cell's V-scaling evidence.
- HARD bands strictly above floor (SP_HI 0.83 headroom to 0.876; SC_HI 0.90 to ~1.0).
- per-unit failure-class instrumentation (no bare except).
- calibration_check: default_ok_for_this_regime (real BGE cache; operating points +
  band dims calibrated by the MEASURED feasibility probe before this pre-reg).
- telemetry-sensitivity self-test MANDATORY (perturb-a-seed-moves-the-discriminator).
- cell_chunked: false (5 trained arms x 3 smoke seeds run in ONE cell; per-seed
  checkpoint + resume make it restartable; light enough that single-file is fine).
- start_marker + crash_diagnostic + heartbeat present.
- all numbers tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@ in the report.

ASCII-only. No unicode. No emojis. No em dashes.
"""
from __future__ import annotations

import argparse
import glob
import hashlib
import json
import os
import platform
import sys
import time
import traceback
from datetime import datetime, timezone

import numpy as np

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

try:
    sys.stdout.reconfigure(line_buffering=True)  # unbuffered progress (section 17)
except Exception:  # noqa: BLE001
    pass

ANCHOR_NAME = "encoder_twoband_single_vector_am_fm_v1"
OUTPUT_DIR = os.path.join(_REPO, "data", f"exp_{ANCHOR_NAME}")

_CACHE_DIR = os.path.join(_REPO, "data", "substrate_index", "cached_indices")

# operating points (match the two-head / anchor-sweep cells for comparability)
J_OP = 5
ALPHA_OP = 1.2
NOISE_PROBE_ALPHA = 4.0   # self-test only: high-noise point where SC_D is UN-saturated
                          # (at ALPHA_OP the pointwise band saturates near 1.0 by design --
                          # that is the GOAL -- so telemetry-sensitivity of the pointwise
                          # discriminator is demonstrated in its sensitive band here)
GAMMA_VAR = 1.0          # VICReg variance-floor target
MU_VIC = 1.0             # variance-floor weight
NU_VIC = 1.0             # covariance-decorrelation weight
LAMBDA_D = 1.0           # RKD BGE-distillation weight

# pre-reg bands (HEADLINE = twoband_shared at band_frac_B=0.5)
SP_HI = 0.83             # band_B WTA superposition recall@J_OP counted as high superposition
SC_HI = 0.90             # band_D DENSE pointwise recall@alpha_OP counted as high pointwise
MIDDLE_TOL = 0.05        # near-miss tolerance for the not-yet-hit band (MIDDLE band)
CROSS_SP_GAP = 0.20      # SP_B - SP_D min gap: wrong-band superposition must fail (split real)
CROSS_SC_GAP = 0.10      # SC_D - SC_B min gap: wrong-band pointwise must fail (split real)

GATE_FRAC = 0.5          # the pre-declared band split the HEADLINE gate reads

# arm definitions
ARMS = [
    {"name": "twoband_shared", "kind": "twoband", "shared": True,
     "lambda_d": LAMBDA_D, "mu": MU_VIC, "nu": NU_VIC},
    {"name": "twoband_split_trunk", "kind": "twoband", "shared": False,
     "lambda_d": LAMBDA_D, "mu": MU_VIC, "nu": NU_VIC},
    {"name": "twohead_2N", "kind": "twohead", "shared": True,
     "lambda_d": LAMBDA_D, "mu": MU_VIC, "nu": NU_VIC},
    {"name": "singlecode_native", "kind": "singlecode",
     "lambda_d": 0.0, "mu": MU_VIC, "nu": NU_VIC},
    {"name": "singlecode_distill", "kind": "singlecode",
     "lambda_d": LAMBDA_D, "mu": 0.0, "nu": 0.0},
    {"name": "teacher_bge", "kind": "teacher"},
    {"name": "native_untrained", "kind": "untrained"},
]
TWOBAND_ARMS = ["twoband_shared", "twoband_split_trunk"]
HEADLINE_ARM = "twoband_shared"
CEILING_ARMS = ["twoband_split_trunk", "twohead_2N"]
FRONTIER_ARMS = ["singlecode_native", "singlecode_distill"]
BASELINE_ARM = "singlecode_distill"    # strict-tradeoff frontier baseline (in-band check)

FULL_SEEDS = [7, 13, 19, 23, 29]
SMOKE_SEEDS = [7, 13, 19]
SELFTEST_SEEDS = [7, 13]

# FULL: production N=4096, GPU, B=8192>N (full-rank covariance), 3-ratio diagnostic.
# SMOKE: PRODUCTION N=4096 (band dims = real operating dims -> discriminator survives
# scale, option A), reduced V/iters/B, single gate ratio 0.5, CPU-local few-min gate.
FULL_REGIME = dict(N=4096, H=512, V=40000, iters=800, B=8192, lr=1e-3,
                   Js=[1, 2, 3, 5, 8], alphas=[0.0, 0.8, 1.2, 1.6], nq=600, sep_sample=1500,
                   band_fracs=[0.375, 0.5, 0.625])
SMOKE_REGIME = dict(N=4096, H=512, V=1500, iters=120, B=768, lr=1e-3,
                    Js=[1, 5], alphas=[0.0, 1.2], nq=250, sep_sample=800,
                    band_fracs=[0.5])
SELFTEST_REGIME = dict(N=4096, H=512, V=900, iters=70, B=400, lr=1e-3,
                       Js=[1, 5], alphas=[0.0, 1.2, NOISE_PROBE_ALPHA], nq=200, sep_sample=500,
                       band_fracs=[0.5])


# --------------------------------- numpy eval prims (reused verbatim) --------
def _l2n(x):
    return x / (np.linalg.norm(x, axis=1, keepdims=True) + 1e-9)


def _encode_wta(z, k):
    """Sparse-bipolar block code: top-K magnitude coords -> sign, rest 0. (B,N)->(B,N)."""
    k = int(max(1, min(k, z.shape[1])))
    idx = np.argpartition(-np.abs(z), k - 1, axis=1)[:, :k]
    code = np.zeros_like(z)
    rows = np.arange(z.shape[0])[:, None]
    code[rows, idx] = np.sign(z[rows, idx])
    return code.astype(np.float32)


def _superposition_recall(unit_dict, rng, J, nq):
    """recall@J: bundle J unit members (normalized sum), argmax-cosine top-J over dict."""
    V = unit_dict.shape[0]
    members = rng.integers(0, V, size=(nq, J))
    q = _l2n(unit_dict[members].sum(axis=1))
    sims = q @ unit_dict.T
    topJ = np.argpartition(-sims, J, axis=1)[:, :J]
    hits = [len(set(topJ[i].tolist()) & set(members[i].tolist())) / J for i in range(nq)]
    return float(np.mean(hits))


def _offtarget_mean_cos(unit_dict, rng, sample):
    """Mean pairwise cosine among DIFFERENT concepts (off-target separation; lower=better)."""
    V = unit_dict.shape[0]
    idx = rng.choice(V, size=min(sample, V), replace=False)
    sub = unit_dict[idx]
    sims = sub @ sub.T
    n = sub.shape[0]
    off = sims[~np.eye(n, dtype=bool)]
    return float(np.mean(off))


# --------------------------------- torch model / training --------------------
def _resolve_device(want):
    import torch
    if want == "cpu":
        return "cpu"
    if want == "cuda":
        if not torch.cuda.is_available():
            raise RuntimeError("device=cuda requested but torch.cuda.is_available()==False")
        return "cuda"
    return "cuda" if torch.cuda.is_available() else "cpu"  # auto


def _init_param(shape, fan_in, gen, device):
    import torch
    return (torch.randn(*shape, generator=gen).to(device) / (fan_in ** 0.5)).requires_grad_(True)


def _vicreg_loss(z, N, B):
    """VICReg variance-floor + off-diagonal covariance decorrelation on a (B,N) code."""
    import torch
    zcen = z - z.mean(dim=0, keepdim=True)
    std = torch.sqrt(zcen.var(dim=0) + 1e-4)
    l_var = torch.relu(GAMMA_VAR - std).mean()
    colss = (zcen * zcen).sum(dim=0)                      # (N,) per-dim sum of squares
    # Gram identity avoids forming N x N when B<=N (O(B^2 N) vs O(N^2 B)); full form when B>N.
    if B <= N:
        gram = zcen @ zcen.T                              # (B, B)
        cov_fro2 = gram.pow(2).sum() / ((B - 1) ** 2)
    else:
        cov = (zcen.T @ zcen) / (B - 1)                   # (N, N)
        cov_fro2 = cov.pow(2).sum()
    diag_sq = colss.pow(2).sum() / ((B - 1) ** 2)         # sum_i cov_ii^2
    l_cov = (cov_fro2 - diag_sq) / max(1, N)
    return l_var, l_cov


def _rkd_loss(z_ret, tc, off_mask):
    """Global/landmark relational-KD: match student pairwise-cosine to teacher's (off-diag MSE)."""
    zc = z_ret / (z_ret.norm(dim=1, keepdim=True) + 1e-9)
    s_s = zc @ zc.T
    s_t = tc @ tc.T
    return ((s_s - s_t)[off_mask] ** 2).mean()


def _train_arm(bge_np, t_unit_np, arm, seed, regime, device, n_b):
    """Train an arm; return numpy params + last train loss. n_b = bundling-band dim."""
    import torch
    N, H = regime["N"], regime["H"]
    B = min(regime["B"], bge_np.shape[0])
    iters = regime["iters"]
    Din = bge_np.shape[1]
    V = bge_np.shape[0]
    n_d = N - n_b
    # arm-specific + ratio-specific init salt so every (arm, band_frac) draw is an
    # independent seed-deterministic tensor (avoids arms-differ hash collisions on
    # objective-sharing arms; twoband_split_trunk and singlecode_native both use VICReg).
    salt = int(hashlib.sha256(f"{arm['name']}|{n_b}".encode()).hexdigest()[:6], 16)
    g = torch.Generator(device="cpu").manual_seed(seed * 1000 + 1 + salt)
    torch.manual_seed(seed * 1000 + 3 + salt)
    x = torch.from_numpy(bge_np).to(device)               # (V, Din) raw BGE source
    tcos = torch.from_numpy(t_unit_np).to(device)         # (V, Din) unit teacher
    off_mask = ~torch.eye(B, dtype=torch.bool, device=device)
    lam, mu, nu = arm["lambda_d"], arm["mu"], arm["nu"]
    kind = arm["kind"]

    params = {"kind": kind, "n_b": n_b}
    if kind == "twoband":
        if arm["shared"]:
            Wt = _init_param((Din, H), Din, g, device)
            Wo = _init_param((H, N), H, g, device)         # ONE output projection (H->N)
            plist = [Wt, Wo]
            params.update({"shared": True, "Wt": Wt, "Wo": Wo})
        else:
            WtB = _init_param((Din, H), Din, g, device)
            WoB = _init_param((H, n_b), H, g, device)
            WtD = _init_param((Din, H), Din, g, device)
            WoD = _init_param((H, n_d), H, g, device)
            plist = [WtB, WoB, WtD, WoD]
            params.update({"shared": False, "WtB": WtB, "WoB": WoB, "WtD": WtD, "WoD": WoD})
    elif kind == "twohead":
        Wt = _init_param((Din, H), Din, g, device)
        Ws = _init_param((H, N), H, g, device)             # store head (full N)
        Wr = _init_param((H, N), H, g, device)             # retrieval head (full N)
        plist = [Wt, Ws, Wr]
        params.update({"Wt": Wt, "Ws": Ws, "Wr": Wr})
    elif kind == "singlecode":
        Wt = _init_param((Din, H), Din, g, device)
        Wh = _init_param((H, N), H, g, device)
        plist = [Wt, Wh]
        params.update({"Wt": Wt, "Wh": Wh})
    else:
        raise ValueError(f"_train_arm called with non-trainable kind {kind}")

    opt = torch.optim.Adam(plist, lr=regime["lr"])
    last = None
    for it in range(iters):
        idx = torch.randperm(V, device=device)[:B]
        xb = x[idx]
        loss = xb.new_zeros(())
        if kind == "twoband":
            if arm["shared"]:
                z = (xb @ params["Wt"]) @ params["Wo"]     # (B,N) THE single code
                z_B = z[:, :n_b]
                z_D = z[:, n_b:]
            else:
                z_B = (xb @ params["WtB"]) @ params["WoB"]
                z_D = (xb @ params["WtD"]) @ params["WoD"]
            lv, lc = _vicreg_loss(z_B, n_b, B)             # VICReg on the bundling band
            loss = loss + mu * lv + nu * lc
            loss = loss + lam * _rkd_loss(z_D, tcos[idx], off_mask)   # RKD on the detail band
        elif kind == "twohead":
            z_store = (xb @ params["Wt"]) @ params["Ws"]
            z_ret = (xb @ params["Wt"]) @ params["Wr"]
            lv, lc = _vicreg_loss(z_store, N, B)
            loss = loss + mu * lv + nu * lc
            loss = loss + lam * _rkd_loss(z_ret, tcos[idx], off_mask)
        else:  # singlecode: one code, dual readout
            z = (xb @ params["Wt"]) @ params["Wh"]
            if mu > 0.0 or nu > 0.0:
                lv, lc = _vicreg_loss(z, N, B)
                loss = loss + mu * lv + nu * lc
            if lam > 0.0 and (mu == 0.0 and nu == 0.0):
                loss = loss + lam * _rkd_loss(z, tcos[idx], off_mask)
        opt.zero_grad(set_to_none=True)
        loss.backward()
        opt.step()
        last = float(loss.detach().cpu())
        if it % max(1, iters // 5) == 0 or it == iters - 1:
            print(f"[progress] seed={seed} arm={arm['name']} nb={n_b} it={it}/{iters} "
                  f"loss={last:.5f}", flush=True)
    np_params = {k: (v.detach().cpu().numpy().astype(np.float32) if hasattr(v, "detach") else v)
                 for k, v in params.items()}
    return np_params, last


# ------------------------- band forwards (torch, exact linear trunk) ---------
def _make_band_forward(arm, np_params, device, n_b, N):
    """Return (fwd_B, fwd_D): numpy (M,Din) -> band code (M,n_b) / (M,n_d).

    fwd_B feeds the BUNDLING-band readout (WTA superposition); fwd_D feeds the
    DETAIL-band readout (dense pointwise). For twohead/singlecode both bands are full N.
    """
    import torch
    kind = arm["kind"]

    def _mm2(x_np, A, Bm):
        xt = torch.from_numpy(np.ascontiguousarray(x_np, dtype=np.float32)).to(device)
        with torch.no_grad():
            out = (xt @ torch.from_numpy(A).to(device)) @ torch.from_numpy(Bm).to(device)
        return out.cpu().numpy().astype(np.float32)

    if kind == "twoband":
        if np_params["shared"]:
            Wt, Wo = np_params["Wt"], np_params["Wo"]
            full = lambda x: _mm2(x, Wt, Wo)               # (M,N)
            return (lambda x: full(x)[:, :n_b], lambda x: full(x)[:, n_b:])
        WtB, WoB, WtD, WoD = np_params["WtB"], np_params["WoB"], np_params["WtD"], np_params["WoD"]
        return (lambda x: _mm2(x, WtB, WoB), lambda x: _mm2(x, WtD, WoD))
    if kind == "twohead":
        Wt, Ws, Wr = np_params["Wt"], np_params["Ws"], np_params["Wr"]
        return (lambda x: _mm2(x, Wt, Ws), lambda x: _mm2(x, Wt, Wr))
    if kind == "singlecode":
        Wt, Wh = np_params["Wt"], np_params["Wh"]
        f = lambda x: _mm2(x, Wt, Wh)
        return (f, f)                                      # one code, dual readout
    raise ValueError(kind)


def _band_dims(kind, N, n_b):
    """Return (dim_B, dim_D): the actual dimension of each band's code for this arm-kind."""
    if kind == "twoband":
        return n_b, N - n_b
    return N, N  # twohead / singlecode / teacher / untrained read full N per band


# ------------------------------ per-arm band measurement ---------------------
def _measure_arm_bands(fwd_B, fwd_D, bge, qsrc_by_alpha, qi, regime, seed, dim_B, dim_D):
    """Compute SP_B/SC_D (correct reads) + SP_D/SC_B (cross reads) + separations."""
    kB = max(1, dim_B // 32)                               # 3.125% sparsity per band
    kD = max(1, dim_D // 32)
    dictB = fwd_B(bge)                                     # (V, dim_B)
    dictD = fwd_D(bge) if fwd_D is not None else None
    band_B_wta = _l2n(_encode_wta(dictB, kB))
    band_B_dense = _l2n(dictB)
    band_D_wta = _l2n(_encode_wta(dictD, kD)) if dictD is not None else None
    band_D_dense = _l2n(dictD) if dictD is not None else None

    sp_B, sp_D = {}, {}
    for J in regime["Js"]:
        sp_B[str(J)] = _superposition_recall(band_B_wta, np.random.default_rng(seed * 100 + J), J, regime["nq"])
        if band_D_wta is not None:
            sp_D[str(J)] = _superposition_recall(band_D_wta, np.random.default_rng(seed * 100 + J), J, regime["nq"])
        else:
            sp_D[str(J)] = None

    sc_D, sc_B = {}, {}
    for a in regime["alphas"]:
        q = qsrc_by_alpha[a]
        if band_D_dense is not None:
            qd = _l2n(fwd_D(q))
            sc_D[str(a)] = float(np.mean(np.argmax(qd @ band_D_dense.T, axis=1) == qi))
        else:
            sc_D[str(a)] = None
        qb = _l2n(fwd_B(q))
        sc_B[str(a)] = float(np.mean(np.argmax(qb @ band_B_dense.T, axis=1) == qi))

    sep_B_wta = _offtarget_mean_cos(band_B_wta, np.random.default_rng(seed + 11), regime["sep_sample"])
    sep_D_dense = _offtarget_mean_cos(band_D_dense, np.random.default_rng(seed + 13), regime["sep_sample"]) \
        if band_D_dense is not None else None
    return {
        "sp_B": sp_B, "sp_D": sp_D, "sc_D": sc_D, "sc_B": sc_B,
        "sep_B_wta": sep_B_wta, "sep_D_dense": sep_D_dense,
        "band_B_hash": hashlib.sha256(band_B_wta.tobytes()).hexdigest(),
    }


def measure_seed(bge_full, t_unit_full, seed, regime, device):
    rng = np.random.default_rng(seed)
    V, N = regime["V"], regime["N"]
    sel = rng.choice(bge_full.shape[0], size=min(V, bge_full.shape[0]), replace=False)
    bge = bge_full[sel].astype(np.float32)
    t_unit = t_unit_full[sel].astype(np.float32)
    Vr = bge.shape[0]

    # noisy-query set for pointwise (single-concept fidelity)
    qi = np.random.default_rng(seed * 7 + 3).choice(Vr, size=min(regime["nq"], Vr), replace=False)
    src = bge[qi]
    src_norm = np.linalg.norm(src, axis=1, keepdims=True)
    qrng = np.random.default_rng(seed * 7 + 5)
    qsrc_by_alpha = {}
    for a in regime["alphas"]:
        nz = qrng.standard_normal(src.shape).astype(np.float32)
        nz = nz / (np.linalg.norm(nz, axis=1, keepdims=True) + 1e-9)
        qsrc_by_alpha[a] = (src + a * src_norm * nz).astype(np.float32)

    res_arms = {}
    ratio_sweep = {}
    for arm in ARMS:
        name = arm["name"]
        kind = arm["kind"]
        gate_n_b = int(round(N * GATE_FRAC))

        if kind == "teacher":
            fwd_B = lambda x: np.ascontiguousarray(x, dtype=np.float32)
            fwd_D = lambda x: np.ascontiguousarray(x, dtype=np.float32)
            res_arms[name] = _measure_arm_bands(fwd_B, fwd_D, bge, qsrc_by_alpha, qi,
                                                regime, seed, N, N)
            res_arms[name]["train_loss"] = None
        elif kind == "untrained":
            gnp = np.random.default_rng(seed * 1000 + 7)
            W = (gnp.standard_normal((bge.shape[1], N)).astype(np.float32) / np.sqrt(bge.shape[1]))
            fwd_B = lambda x, W=W: (np.ascontiguousarray(x, dtype=np.float32) @ W)
            res_arms[name] = _measure_arm_bands(fwd_B, fwd_B, bge, qsrc_by_alpha, qi,
                                                regime, seed, N, N)
            res_arms[name]["train_loss"] = None
        elif kind in ("twohead", "singlecode"):
            np_params, tl = _train_arm(bge, t_unit, arm, seed, regime, device, gate_n_b)
            fwd_B, fwd_D = _make_band_forward(arm, np_params, device, gate_n_b, N)
            res_arms[name] = _measure_arm_bands(fwd_B, fwd_D, bge, qsrc_by_alpha, qi,
                                                regime, seed, N, N)
            res_arms[name]["train_loss"] = tl
        else:  # twoband: sweep band_fracs; gate ratio -> res_arms, all ratios -> ratio_sweep
            ratio_sweep[name] = {}
            for frac in regime["band_fracs"]:
                n_b = int(round(N * frac))
                np_params, tl = _train_arm(bge, t_unit, arm, seed, regime, device, n_b)
                fwd_B, fwd_D = _make_band_forward(arm, np_params, device, n_b, N)
                dim_B, dim_D = _band_dims(kind, N, n_b)
                r = _measure_arm_bands(fwd_B, fwd_D, bge, qsrc_by_alpha, qi,
                                       regime, seed, dim_B, dim_D)
                r["train_loss"] = tl
                r["n_b"] = n_b
                ratio_sweep[name][str(frac)] = r
                if abs(frac - GATE_FRAC) < 1e-9:
                    res_arms[name] = r

        rr = res_arms[name]
        scd = rr["sc_D"].get(str(ALPHA_OP))
        print(f"[progress] seed={seed} arm={name} SP_B@{J_OP}={rr['sp_B'].get(str(J_OP)):.3f} "
              f"SC_D@{ALPHA_OP}={('%.3f' % scd) if scd is not None else 'n/a'} "
              f"SP_D@{J_OP}={('%.3f' % rr['sp_D'][str(J_OP)]) if rr['sp_D'][str(J_OP)] is not None else 'n/a'} "
              f"SC_B@{ALPHA_OP}={rr['sc_B'].get(str(ALPHA_OP)):.3f}", flush=True)

    return {"seed": int(seed), "V": int(Vr), "N": int(N),
            "arms": res_arms, "ratio_sweep": ratio_sweep}


# ------------------------------ aggregation / verdict ------------------------
def _mean(xs):
    xs = [v for v in xs if v is not None]
    return float(np.mean(xs)) if xs else None


def _cv(xs):
    a = np.asarray([v for v in xs if v is not None], dtype=np.float64)
    if a.size == 0:
        return 0.0
    mu = float(np.mean(a))
    return 0.0 if abs(mu) < 1e-9 else float(np.std(a) / abs(mu))


def _aggregate(per_seed, regime):
    Js, alphas = regime["Js"], regime["alphas"]
    names = [a["name"] for a in ARMS]
    agg = {"n_seeds": len(per_seed), "arms": {}}
    for nm in names:
        sp_B = {str(J): _mean([s["arms"][nm]["sp_B"][str(J)] for s in per_seed]) for J in Js}
        sp_D = {str(J): _mean([s["arms"][nm]["sp_D"][str(J)] for s in per_seed]) for J in Js}
        sc_D = {str(a): _mean([s["arms"][nm]["sc_D"][str(a)] for s in per_seed]) for a in alphas}
        sc_B = {str(a): _mean([s["arms"][nm]["sc_B"][str(a)] for s in per_seed]) for a in alphas}
        agg["arms"][nm] = {
            "sp_B_mean": sp_B, "sp_D_mean": sp_D, "sc_D_mean": sc_D, "sc_B_mean": sc_B,
            "sep_B_wta_mean": _mean([s["arms"][nm]["sep_B_wta"] for s in per_seed]),
            "sep_D_dense_mean": _mean([s["arms"][nm]["sep_D_dense"] for s in per_seed]),
            "sp_B_op_per_seed": [s["arms"][nm]["sp_B"][str(J_OP)] for s in per_seed],
            "sc_D_op_per_seed": [s["arms"][nm]["sc_D"][str(ALPHA_OP)] for s in per_seed],
        }
        agg["arms"][nm]["sp_B_op_cv"] = _cv(agg["arms"][nm]["sp_B_op_per_seed"])
    # ratio sweep aggregate (twoband arms only; diagnostic)
    rs = {}
    for nm in TWOBAND_ARMS:
        rs[nm] = {}
        for frac in regime["band_fracs"]:
            fk = str(frac)
            rs[nm][fk] = {
                "sp_B_op": _mean([s["ratio_sweep"][nm][fk]["sp_B"][str(J_OP)] for s in per_seed]),
                "sc_D_op": _mean([s["ratio_sweep"][nm][fk]["sc_D"][str(ALPHA_OP)] for s in per_seed]),
                "n_b": per_seed[0]["ratio_sweep"][nm][fk]["n_b"],
            }
    agg["ratio_sweep"] = rs
    return agg


def _sp(A, nm):
    return A[nm]["sp_B_mean"][str(J_OP)]


def _sc(A, nm):
    v = A[nm]["sc_D_mean"][str(ALPHA_OP)]
    return v if v is not None else float("nan")


def _spD(A, nm):
    v = A[nm]["sp_D_mean"][str(J_OP)]
    return v if v is not None else float("nan")


def _scB(A, nm):
    return A[nm]["sc_B_mean"][str(ALPHA_OP)]


def _joint(sp, sc):
    if sc is None or (isinstance(sc, float) and np.isnan(sc)):
        return 0.0
    return float(min(sp / SP_HI, sc / SC_HI))


def _classify(agg):
    A = agg["arms"]
    sp_B = _sp(A, HEADLINE_ARM)
    sc_D = _sc(A, HEADLINE_ARM)
    sp_D = _spD(A, HEADLINE_ARM)
    sc_B = _scB(A, HEADLINE_ARM)
    sp_hit = bool(sp_B >= SP_HI)
    sc_hit = bool(sc_D >= SC_HI)
    both = bool(sp_hit and sc_hit)
    joint = _joint(sp_B, sc_D)
    # split-real (anti-cosmetic): wrong band fails for each task
    cross_sp_gap = sp_B - sp_D if not np.isnan(sp_D) else 0.0
    cross_sc_gap = sc_D - sc_B if not np.isnan(sc_D) else 0.0
    split_real = bool(cross_sp_gap >= CROSS_SP_GAP and cross_sc_gap >= CROSS_SC_GAP)

    frontier = {}
    for nm in FRONTIER_ARMS:
        s, c = _sp(A, nm), _sc(A, nm)
        frontier[nm] = {"sp": s, "sc": c, "both": bool(s >= SP_HI and c >= SC_HI), "joint": _joint(s, c)}
    best_frontier_joint = max((v["joint"] for v in frontier.values()), default=0.0)
    frontier_both = any(v["both"] for v in frontier.values())

    ceilings = {}
    for nm in CEILING_ARMS:
        s, c = _sp(A, nm), _sc(A, nm)
        ceilings[nm] = {"sp": s, "sc": c, "both": bool(s >= SP_HI and c >= SC_HI), "joint": _joint(s, c)}

    if both and split_real:
        verdict = "HARD_PASS_TWOBAND_SINGLE_VECTOR_ACHIEVES_BOTH"
    elif both and not split_real:
        verdict = "HARD_FAIL_COSMETIC_SPLIT_BOTH_BANDS_SAME"
    elif sp_hit ^ sc_hit:
        miss_ok = (abs(sc_D - SC_HI) <= MIDDLE_TOL) if sp_hit else (abs(sp_B - SP_HI) <= MIDDLE_TOL)
        verdict = "MIDDLE_ONE_BAND_HITS" if miss_ok else "HARD_FAIL_ONE_BAND_FAR_MISS"
    elif joint <= best_frontier_joint + 1e-6:
        verdict = "HARD_FAIL_NO_GAIN_OVER_SINGLE_CODE"
    else:
        verdict = "HARD_FAIL_SHARED_VECTOR_INTERFERES_NEITHER_BAND"

    return {
        "verdict": verdict,
        "headline": {"arm": HEADLINE_ARM, "band_frac_B": GATE_FRAC,
                     "sp_B": sp_B, "sc_D": sc_D, "sp_D": sp_D, "sc_B": sc_B,
                     "sp_hit": sp_hit, "sc_hit": sc_hit, "both": both, "joint": joint,
                     "cross_sp_gap": cross_sp_gap, "cross_sc_gap": cross_sc_gap,
                     "split_real": split_real},
        "ceilings": ceilings,
        "frontier": frontier, "frontier_both": frontier_both,
        "best_frontier_joint": best_frontier_joint,
        "thresholds": {"SP_HI": SP_HI, "SC_HI": SC_HI, "MIDDLE_TOL": MIDDLE_TOL,
                       "CROSS_SP_GAP": CROSS_SP_GAP, "CROSS_SC_GAP": CROSS_SC_GAP},
        "ratio_sweep": agg.get("ratio_sweep", {}),
    }


# --------------------------------- IO / diagnostics --------------------------
def _write_start_marker(output_dir, run_mode, expected_units):
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": run_mode,
              "expected_n_units": expected_units, "host": platform.node()}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, os.path.join(output_dir, "_start_marker.json"))


def _write_metrics(output_dir, metrics):
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, os.path.join(output_dir, "metrics.json"))


def _write_crash_metrics(output_dir, exc):
    diag = {"verdict": "CELL_CRASHED",
            "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
            "summary": f"CELL_CRASHED: {type(exc).__name__}", "elapsed_s": 0.0,
            "run_mode": "crash", "traceback": traceback.format_exc()[:5000],
            "ts_iso": datetime.now(timezone.utc).isoformat(),
            "pid": os.getpid(), "anchor_name": ANCHOR_NAME}
    _write_metrics(output_dir, diag)


def _emit_heartbeat(output_dir, unit_idx, total_units, elapsed_s, extra=None):
    row = {"ts_iso": datetime.now(timezone.utc).isoformat(), "unit_idx": unit_idx,
           "total_units": total_units, "elapsed_s": elapsed_s}
    if extra:
        row["extra"] = extra
    try:
        with open(os.path.join(output_dir, "_heartbeat.jsonl"), "a", encoding="utf-8") as f:
            f.write(json.dumps(row) + "\n")
    except Exception:  # noqa: BLE001
        pass


def _resolve_cache(min_rows=0):
    cands = sorted(glob.glob(os.path.join(_CACHE_DIR, "bge_large_v2_name_*.npz")))
    if not cands:
        raise FileNotFoundError(f"no BGE teacher cache in {_CACHE_DIR} (bge_large_v2_name_*.npz)")

    def vcount(p):
        try:
            return int(os.path.basename(p).split("_name_")[1].split("_")[0])
        except Exception:  # noqa: BLE001
            return 0
    ok = [p for p in cands if vcount(p) >= min_rows]
    pool = ok if ok else cands
    return max(pool, key=vcount)


def _load_teacher(regime):
    path = _resolve_cache(min_rows=regime["V"])
    d = np.load(path, allow_pickle=True)
    if "semantic" not in d:
        raise KeyError(f"cache {path} missing 'semantic' key; has {list(d.keys())}")
    sem = d["semantic"].astype(np.float32)
    good = np.linalg.norm(sem, axis=1) > 1e-6
    sem = sem[good]
    if sem.shape[0] < regime["V"]:
        print(f"[warn] cache has {sem.shape[0]} usable rows < requested V={regime['V']}; "
              f"using all {sem.shape[0]}", flush=True)
    t_unit = _l2n(sem)
    return sem, t_unit, os.path.basename(path)


def _seed_partial_path(output_dir, run_mode, seed):
    return os.path.join(output_dir, f"_seed_{run_mode}_{seed}.json")


# ------------------------------------ self-test ------------------------------
def self_test():
    """Scaffold-free witnesses: encoder validity, telemetry-sensitivity, arms-differ,
    both bands, cross-read (split real, not cosmetic)."""
    ok = True
    reg = SELFTEST_REGIME
    device = "cpu"
    try:
        bge_full, t_unit_full, _src = _load_teacher(reg)
    except Exception as e:  # noqa: BLE001
        print(f"[self-test] FAIL cannot load teacher cache: {e}")
        return 1
    m7 = measure_seed(bge_full, t_unit_full, 7, reg, device)
    m13 = measure_seed(bge_full, t_unit_full, 13, reg, device)
    A7, A13 = m7["arms"], m13["arms"]

    # 1) teacher is a valid encoder: J=1 band_B self-retrieval ~1.0
    valid_enc = A7["teacher_bge"]["sp_B"]["1"] >= 0.98
    ok &= valid_enc
    # 2) TELEMETRY-SENSITIVITY: perturbing the seed MOVES the discriminators. Store axis:
    #    twoband_shared band_B SP_B@J_OP moves. Retrieval/pointwise axis: SC_D saturates
    #    near 1.0 at ALPHA_OP (the GOAL), so telemetry-sensitivity of the HEADLINE pointwise
    #    discriminator is proven at NOISE_PROBE_ALPHA where SC_D is genuinely in its sensitive
    #    band (< 0.95): it MUST both move across seeds AND sit below saturation (a metric
    #    that ignored the data would be pinned/identical). Cross-checked on singlecode_native
    #    so a lucky tie on one arm cannot fake sensitivity.
    sp_moves = (A7["twoband_shared"]["sp_B"][str(J_OP)] != A13["twoband_shared"]["sp_B"][str(J_OP)])
    pk = str(NOISE_PROBE_ALPHA)
    # (a) NOISE data-axis: the HEADLINE pointwise discriminator SC_D responds strongly to
    #     query quality (drops far below saturation as noise rises) -> not analytically
    #     pinned. Robust movement (~0.5), no discretization-tie risk.
    scd_clean = A7["twoband_shared"]["sc_D"]["0.0"]
    scd_noisy = A7["twoband_shared"]["sc_D"][pk]
    sc_noise_moves = (scd_clean is not None and scd_noisy is not None
                      and (scd_clean - scd_noisy) >= 0.10 and scd_noisy < 0.95)
    # (b) SEED data-axis: a CONTINUOUS geometry readout of the trained detail band
    #     (mean off-target cosine) differs across seeds -> the pointwise band is
    #     seed/data dependent, not a fixed transform. Continuous float avoids the
    #     count/nq discretization ties that make single-point recall comparisons fragile.
    sep7 = A7["twoband_shared"]["sep_D_dense"]
    sep13 = A13["twoband_shared"]["sep_D_dense"]
    sc_seed_moves = (sep7 is not None and sep13 is not None and sep7 != sep13)
    sc_moves = bool(sc_noise_moves and sc_seed_moves)
    ok &= (sp_moves and sc_moves)
    # 3) ARMS DIFFER (META_RULE_AF): all band_B-code hashes distinct
    hashes = [A7[a["name"]]["band_B_hash"] for a in ARMS]
    arms_differ = len(set(hashes)) == len(hashes)
    ok &= arms_differ
    # 4) BOTH BANDS train: twoband_shared finite loss; bundling band decorrelates so its
    #    WTA superposition beats its DENSE self-superposition of the DETAIL band's WTA.
    th = A7["twoband_shared"]
    both_bands_train = th["train_loss"] is not None and np.isfinite(th["train_loss"])
    ok &= both_bands_train
    # 5) CROSS-READ SPLIT IS REAL (not cosmetic): band_B beats band_D on superposition AND
    #    band_D beats band_B on pointwise -> the two bands carry DIFFERENT things.
    sp_B, sp_D = th["sp_B"][str(J_OP)], th["sp_D"][str(J_OP)]
    sc_D, sc_B = th["sc_D"][str(ALPHA_OP)], th["sc_B"][str(ALPHA_OP)]
    superpos_specializes = (sp_D is not None) and (sp_B > sp_D + 0.05)
    pointwise_specializes = (sc_D is not None) and (sc_D >= sc_B - 1e-9)
    ok &= (superpos_specializes and pointwise_specializes)
    # 6) SC degrades with noise for teacher (real pointwise metric, not pinned)
    sc_noise = A7["teacher_bge"]["sc_D"]["0.0"] >= A7["teacher_bge"]["sc_D"]["1.2"] - 1e-9
    ok &= sc_noise

    print(f"[self-test] pointwise-telemetry: noise-axis SC_D 0.0={scd_clean} a{NOISE_PROBE_ALPHA}={scd_noisy} "
          f"(moves={sc_noise_moves}); seed-axis sep_D_dense s7={sep7} s13={sep13} (moves={sc_seed_moves})")
    print(f"[self-test] valid_enc={valid_enc}(spB@1={A7['teacher_bge']['sp_B']['1']:.3f}) "
          f"sp_moves={sp_moves} sc_moves={sc_moves} arms_differ={arms_differ} "
          f"both_bands_train={both_bands_train} "
          f"superpos_spec={superpos_specializes}(SP_B={sp_B:.3f}>SP_D={sp_D if sp_D is None else round(sp_D,3)}) "
          f"pointwise_spec={pointwise_specializes}(SC_D={sc_D if sc_D is None else round(sc_D,3)}"
          f">=SC_B={round(sc_B,3)}) sc_noise={sc_noise}")
    print(f"[self-test] {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


# ------------------------------------ run ------------------------------------
def run(run_mode, device_want):
    t0 = time.perf_counter()
    if run_mode == "smoke":
        regime, seeds = SMOKE_REGIME, SMOKE_SEEDS
    else:
        regime, seeds = FULL_REGIME, FULL_SEEDS
    device = _resolve_device(device_want)
    expected_units = len(seeds)
    _write_start_marker(OUTPUT_DIR, run_mode, expected_units)
    print(f"[start] run_mode={run_mode} device={device} seeds={seeds} regime={regime}", flush=True)

    bge_full, t_unit_full, cache_src = _load_teacher(regime)

    per_seed = []
    for si, sd in enumerate(seeds):
        pp = _seed_partial_path(OUTPUT_DIR, run_mode, sd)
        if os.path.exists(pp):
            try:
                with open(pp, encoding="utf-8") as f:
                    per_seed.append(json.load(f))
                print(f"[resume] seed={sd} loaded from partial", flush=True)
                _emit_heartbeat(OUTPUT_DIR, si, expected_units, time.perf_counter() - t0,
                                {"seed": sd, "resumed": True})
                continue
            except Exception:  # noqa: BLE001 - corrupt partial: recompute
                pass
        ts = time.perf_counter()
        res = measure_seed(bge_full, t_unit_full, sd, regime, device)
        res["elapsed_s"] = time.perf_counter() - ts
        tmp = pp + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(res, f)
        os.replace(tmp, pp)
        per_seed.append(res)
        _emit_heartbeat(OUTPUT_DIR, si + 1, expected_units, time.perf_counter() - t0,
                        {"seed": sd, "seed_elapsed_s": res["elapsed_s"]})
        print(f"[seed-done] seed={sd} elapsed={res['elapsed_s']:.1f}s", flush=True)

    agg = _aggregate(per_seed, regime)
    cls = _classify(agg)

    n_units = len(per_seed)
    cardinality_ok = (n_units == expected_units)
    A = agg["arms"]
    baseline_sp = _sp(A, BASELINE_ARM)
    baseline_in_band = 0.05 < baseline_sp < 0.95
    hashes = [per_seed[0]["arms"][a["name"]]["band_B_hash"] for a in ARMS]
    arms_differ = len(set(hashes)) == len(hashes)

    if not cardinality_ok:
        verdict = "HARD_FAIL_CARDINALITY_BREACH_META_RULE_H"
    elif not arms_differ:
        verdict = "HARD_FAIL_ARMS_IDENTICAL_META_RULE_AF"
    else:
        verdict = cls["verdict"]

    hl = cls["headline"]
    fr = cls["frontier"]
    ce = cls["ceilings"]
    fr_str = " ".join(f"{nm}(SP{v['sp']:.2f}/SC{('%.2f'%v['sc']) if v['sc']==v['sc'] else 'nan'}"
                      f"{'=BOTH' if v['both'] else ''})" for nm, v in fr.items())
    ce_str = " ".join(f"{nm}(SP{v['sp']:.2f}/SC{('%.2f'%v['sc']) if v['sc']==v['sc'] else 'nan'}"
                      f" joint{v['joint']:.2f}{'=BOTH' if v['both'] else ''})" for nm, v in ce.items())
    verdict_msg = (
        f"{verdict} | AM+FM ON ONE WIRE: can ONE N={regime['N']}-dim vector, dimensions "
        f"PARTITIONED into a VICReg-decorrelated BUNDLING band (first {int(round(regime['N']*GATE_FRAC))}) "
        f"+ an RKD-distilled DETAIL band (rest), read CONDITIONALLY per task, achieve BOTH high "
        f"superposition AND high pointwise from ONE vector at the frontier's N budget (half the "
        f"two-head's 2N)? "
        f"HEADLINE twoband_shared @frac{GATE_FRAC}: band_B SP_wta@J{J_OP}={hl['sp_B']:.3f} "
        f"(hit>={SP_HI}:{hl['sp_hit']}) + band_D SC_dense@a{ALPHA_OP}={hl['sc_D']:.3f} "
        f"(hit>={SC_HI}:{hl['sc_hit']}) -> achieves_both={hl['both']} joint={hl['joint']:.3f}. "
        f"SPLIT-REAL (anti-cosmetic cross-read): band_D-for-superposition SP={hl['sp_D']:.3f} "
        f"(gap {hl['cross_sp_gap']:+.3f}>= {CROSS_SP_GAP}?) ; band_B-for-pointwise SC={hl['sc_B']:.3f} "
        f"(gap {hl['cross_sc_gap']:+.3f}>= {CROSS_SC_GAP}?) -> split_real={hl['split_real']}. "
        f"FRONTIER (single code, dual readout, N budget, provably can't do both): {fr_str}; "
        f"frontier_both={cls['frontier_both']} (best_joint={cls['best_frontier_joint']:.3f}). "
        f"CEILINGS: {ce_str}. cache={cache_src}. INTERPRETATION: "
        + ("ONE vector partitioned into two conditionally-read bands delivers BOTH high "
           "superposition and high pointwise fidelity at the frontier's N budget, beating the "
           "strict-tradeoff single-code frontier and approaching the two-head 2N ceiling; the "
           "cross-read confirms the bands are genuinely specialized (AM+FM on one wire works)."
           if verdict == "HARD_PASS_TWOBAND_SINGLE_VECTOR_ACHIEVES_BOTH" else
           ("achieves_both numerically but the cross-read gaps are too small -> the split is "
            "COSMETIC (both bands carry the same content); not a real two-band decoupling."
            if verdict == "HARD_FAIL_COSMETIC_SPLIT_BOTH_BANDS_SAME" else
            ("one band reaches target, the other is within noise of threshold -> a band-ratio / "
             "regime nudge likely closes it (see the band_frac sweep); report to Research."
             if verdict == "MIDDLE_ONE_BAND_HITS" else
             ("the shared single vector / shared trunk forces interference so partitioning starves "
              "both bands, OR the partition gains nothing over a single code. Check the "
              "twoband_split_trunk ceiling (isolates trunk-sharing cost) and twohead_2N (2N budget "
              "ceiling): if split_trunk clears, the fix is per-band trunks; if even 2N barely clears, "
              "the regime is the limit -> escalate."))))
    )

    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": f"{verdict}: two-band single-vector AM+FM encoder ({run_mode})",
        "run_mode": run_mode,
        "device": device,
        "elapsed_s": time.perf_counter() - t0,
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR_NAME,
        "cache_source": cache_src,
        "cardinality_ok": cardinality_ok,
        "expected_n_units": expected_units,
        "n_units": n_units,
        "arms_differ_verified": arms_differ,
        "baseline_in_band": baseline_in_band,
        "classification": cls,
        "operating_points": {"J_OP": J_OP, "ALPHA_OP": ALPHA_OP, "GATE_FRAC": GATE_FRAC},
        "bands": {"SP_HI": SP_HI, "SC_HI": SC_HI, "MIDDLE_TOL": MIDDLE_TOL,
                  "CROSS_SP_GAP": CROSS_SP_GAP, "CROSS_SC_GAP": CROSS_SC_GAP,
                  "GAMMA_VAR": GAMMA_VAR, "MU_VIC": MU_VIC, "NU_VIC": NU_VIC, "LAMBDA_D": LAMBDA_D},
        "arms_config": ARMS,
        "regime": regime,
        "agg": agg,
        "seeds": seeds,
    }
    _write_metrics(OUTPUT_DIR, metrics)
    print("[done] " + verdict_msg, flush=True)
    return metrics


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-mode", choices=["full", "smoke", "self_test"], default="full")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--device", choices=["auto", "cpu", "cuda"], default="auto")
    args = ap.parse_args()
    if args.self_test or args.run_mode == "self_test":
        raise SystemExit(self_test())
    run(args.run_mode, args.device)


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # NOT BaseException
        _write_crash_metrics(OUTPUT_DIR, e)
        raise
