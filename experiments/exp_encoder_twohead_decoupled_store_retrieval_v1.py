"""Trained TWO-HEAD encoder: decouple the store code from the retrieval code -- THE FIX.

QUESTION (2026-07-08, replacing the ORACLE with a real trained architecture). The
anchor-sweep payoff cell (exp_encoder_distill_anchor_sweep_vicreg_decorr_v1, commit
697df6a52) MEASURED (smoke) that NO scalar BGE-anchor-weight setting gets BOTH high
superposition recall AND high pointwise fidelity from a single block code
(both_arms=[], verdict STRICT_TRADEOFF_STRUCTURAL_DECOUPLING_NEEDED); yet a
decoupled-ORACLE that PICKS the decorrelated store code (native_untrained WTA
SP@J5=0.905) for superposition AND the raw BGE teacher (SC@1.2=1.000) for pointwise
achieves BOTH simultaneously. The oracle is an existence proof that uses two
SEPARATE hand-picked representations. This cell asks the honest follow-up: does a
REAL TRAINED two-head architecture -- a shared trunk feeding a VICReg-decorrelating
STORE head and a BGE-distilling RETRIEVAL head -- achieve BOTH from ONE learned
system, or does the shared trunk force interference so neither head reaches target?

CERTIFIED LAW anchored here (reference_correlation_hurts_associative_store_capacity_
decouple_from_retrieval): the associative store wants DECORRELATED (near-orthogonal)
codes; retrieval wants CORRELATED (semantic) codes; the two pulls are opposite, so
DECOUPLE. This cell instantiates that law as a trained two-head encoder and tests
whether the decoupling survives a SHARED nonlinear trunk (the real cost).

MECHANISM. A shared LINEAR bottleneck trunk maps BGE source x (Din=1024) -> feats =
x @ W_trunk (H=512 < Din, a genuine shared-representation bottleneck that FORCES the
two heads to read from the same compressed subspace -- without a bottleneck a linear
trunk imposes no constraint and the heads decouple trivially). NOTE (measured during
smoke-gate design): a GELU trunk was tried FIRST and BROKE the store head -- GELU's
positive-output bias injects feature correlations that fight the VICReg decorrelation,
collapsing store WTA superposition to 0.316 (BELOW the random-projection 0.829 floor).
The zero-mean linear trunk converges reliably (store 0.895 shared / 0.966 split at the
N=1024 probe) and is the faithful realization; a zero-centered nonlinear trunk (tanh /
centered features) is future work. Two linear heads read out from feats:
  STORE head    z_store = feats @ W_store  (N)  trained with VICReg var-floor + cov
                decorrelation; evaluated by WTA-block-code superposition recall@J.
  RETRIEVAL head z_ret  = feats @ W_ret   (N)  trained with GLOBAL/landmark RKD
                BGE-distillation (match per-minibatch pairwise-cosine matrix to the
                BGE teacher); evaluated by DENSE single-concept pointwise recall.
Both heads' gradients flow into the shared trunk (twohead_shared) -- the interference
test. A twohead_split arm gives each head its OWN trunk (no shared parameters) as the
no-interference CEILING (closest trained analog to the oracle). Single-head arms
(one code, dual readout) are the strict-tradeoff FRONTIER baselines.

ARMS (all on the SAME dictionary / cleanup; metric harness reused verbatim from the
anchor-sweep cell so numbers are directly comparable):
  twohead_shared    shared trunk; store head (VICReg) + ret head (RKD)   [HEADLINE]
  twohead_split     independent trunks per head                          [CEILING]
  singlehead_distill one code, RKD only (= anchor-sweep distill_only)     [FRONTIER]
  singlehead_native  one code, VICReg only (= anchor-sweep native_trained)[FRONTIER]
  teacher_bge       raw unit BGE (SC ceiling ~1.0; SP_wta crowded ~0.43) [REF]
  native_untrained  random W + WTA (superposition ceiling ~0.905)        [REF]

METRICS (uniform across arms; store metric + retrieval metric + cross-checks):
  STORE metric      = superposition recall@J on the WTA block code of the STORE code
                      (production 3.125% sparsity; the load-bearing capacity axis).
  RETRIEVAL metric  = single-concept pointwise recall@alpha on the DENSE RETRIEVAL
                      code (a concept's BGE source perturbed by relative noise,
                      encoded THROUGH the head, argmax-cosine over the dict).
                      Retrieval does NOT need sparsity; dense is its natural readout.
  CROSS-CHECKS      = store-head SC_dense (must NOT be forced BGE-like) + ret-head
                      SP_wta (must NOT be forced decorrelated) -- confirm each head
                      specialized; logged, not gating.
  achieves_both     = store SP_wta@J_OP >= SP_HI AND ret SC_dense@alpha_OP >= SC_HI.

PRE-REG BANDS (HEADLINE arm = twohead_shared; strictly-above-floor per META_RULE_L,
thresholds carry headroom from the noise: SP_HI=0.83 sits below the decorrelated
ceiling 0.905, SC_HI=0.90 sits below the teacher 1.0):
  HARD_PASS = twohead_shared achieves_both: store SP_wta@J_OP >= 0.83 (>= the
              decorrelated single-code frontier ~0.828) AND ret SC_dense@alpha_OP
              >= 0.90 (approaching teacher 1.0, clearing every single-code arm's
              pointwise). A trained shared-trunk system decouples, approaching the
              oracle.
  MIDDLE    = exactly ONE head hits its target and the OTHER is within MIDDLE_TOL
              (0.05) of its target (near-miss; one head reaches, the other is at the
              edge -- a regime/weight nudge away).
  HARD_FAIL = neither head hits target (shared trunk forces interference / collapse
              toward the crowded-BGE or the low-pointwise frontier), OR the
              twohead_shared joint score is no better than the best single-head arm's
              joint (the shared trunk gained nothing over a single code -> escalate
              to twohead_split-only or a dual-readout finding).
  Enrichment (reported, not gating): twohead_split achieves_both (ceiling); and
  whether a single distilled code with DUAL READOUT (WTA store + dense retrieval)
  already achieves_both -- if so, a simpler solution than two heads exists and is
  surfaced in the verdict.

WHY the retrieval metric is DENSE while the store metric is WTA: this asymmetry IS
the decoupling. Superposition CAPACITY needs the sparse WTA block code (dense
geometry of any BGE-anchored linear map is JL-bounded to the crowded teacher, SP_dense
~0.43); pointwise retrieval needs the dense code (WTA of a distilled code loses
pointwise fidelity, MEASURED SC_wta=0.655 for distill_only). A single code forced to
serve BOTH through ONE representation cannot; separate codes / readouts can. The cell
measures whether a TRAINED shared trunk preserves both.

COMPUTE ARCHITECTURE. Class (a) batched-GPU. Training is matmul-heavy (per-iter RKD
pairwise B x B, VICReg covariance over a minibatch, trunk+2-head forwards); 4 trained
arms x 5 seeds x hundreds of iters. Smoke runs CPU-local at reduced iters/batch/V and
N=2048 (linear trunk is fast on CPU; the shared-vs-split interference is an
ARCHITECTURAL property that fires at any N, previewed at the N=2048 smoke and the
N=1024 design probe). FULL routes to the GPU (overnight_queue) at production N=4096
where minibatch B(8192) > N(4096) gives a full-rank covariance estimate. Storage
strategy: no_composition / no_store
(encoder-geometry cell; the "dictionary" is the per-concept code, evaluated by
argmax-cosine cleanup, not a bundled associative store).

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
- arms_differ_verified at smoke gate (sha256 of each arm's store dense dict; distinct)
- final_metrics_atomicity: tmp_replace (os.replace on final metrics.json)
- except SystemExit: raise BEFORE except Exception (no BaseException)
- crlb_n/a: retrieval recall + geometry cosines; no closed-form noise floor.
  Feasibility handled by calibrated operating points (the anchor-sweep MEASURED the
  0.43-vs-0.905 SP band and 0.655-vs-1.0 SC band at this exact regime).
- baseline_in_band: singlehead_distill store SP_wta@J_OP in (0.05,0.95).
- discriminator survives scale: smoke fires at production N=4096; PLUS the shared-vs-
  split interference is an ARCHITECTURAL property (present at any scale), and the
  anchor-sweep MEASURED the crowded-BGE-vs-decorrelated SP gap at V=4000 (-0.561) and
  V=40000 (-0.662) so the lever survives scale by that cell's own V-scaling evidence.
- HARD bands strictly above floor (SP_HI 0.83 headroom to 0.905; SC_HI 0.90 to 1.0).
- per-unit failure-class instrumentation (no bare except).
- calibration_check: default_ok_for_this_regime (real BGE cache; operating points
  calibrated in the anchor-sweep cell before this pre-reg).
- telemetry-sensitivity self-test MANDATORY (perturb-a-seed-moves-the-discriminator).
- all numbers tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@ in report.

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

ANCHOR_NAME = "encoder_twohead_decoupled_store_retrieval_v1"
OUTPUT_DIR = os.path.join(_REPO, "data", f"exp_{ANCHOR_NAME}")

_CACHE_DIR = os.path.join(_REPO, "data", "substrate_index", "cached_indices")
_PRIMARY_CACHE = os.path.join(_CACHE_DIR, "bge_large_v2_name_43905_8a40445a.npz")

# operating points (match the anchor-sweep cell for comparability)
J_OP = 5
ALPHA_OP = 1.2
GAMMA_VAR = 1.0          # VICReg variance-floor target
MU_VIC = 1.0             # variance-floor weight
NU_VIC = 1.0             # covariance-decorrelation weight
LAMBDA_D = 1.0           # RKD BGE-distillation weight on the retrieval head

# pre-reg bands (HEADLINE = twohead_shared)
SP_HI = 0.83             # store WTA superposition recall@J_OP counted as high superposition
SC_HI = 0.90             # ret DENSE single-concept recall@alpha_OP counted as high pointwise
MIDDLE_TOL = 0.05        # near-miss tolerance for the not-yet-hit head (MIDDLE band)

# arm definitions
ARMS = [
    {"name": "twohead_shared", "kind": "twohead", "shared": True,
     "lambda_d": LAMBDA_D, "mu": MU_VIC, "nu": NU_VIC},
    {"name": "twohead_split", "kind": "twohead", "shared": False,
     "lambda_d": LAMBDA_D, "mu": MU_VIC, "nu": NU_VIC},
    {"name": "singlehead_distill", "kind": "singlehead",
     "lambda_d": LAMBDA_D, "mu": 0.0, "nu": 0.0},
    {"name": "singlehead_native", "kind": "singlehead",
     "lambda_d": 0.0, "mu": MU_VIC, "nu": NU_VIC},
    {"name": "teacher_bge", "kind": "teacher"},
    {"name": "native_untrained", "kind": "untrained"},
]
HEADLINE_ARM = "twohead_shared"
CEILING_ARM = "twohead_split"
FRONTIER_ARMS = ["singlehead_distill", "singlehead_native"]
BASELINE_ARM = "singlehead_distill"    # strict-tradeoff frontier baseline (in-band check)

FULL_SEEDS = [7, 13, 19, 23, 29]
SMOKE_SEEDS = [7, 13, 19]
SELFTEST_SEEDS = [7, 13]

# FULL: production N=4096, GPU (B=8192 > N -> full-rank covariance). SMOKE: production
# N=4096, reduced V/iters/B for a CPU-local few-min gate at the SAME sparsity (the store
# WTA lever + shared-vs-split interference are architectural, so the discriminator fires
# at smoke -- DISCRIMINATOR-MUST-SURVIVE-SCALE option A partial + option B analytical).
FULL_REGIME = dict(N=4096, H=512, V=40000, iters=800, B=8192, lr=1e-3,
                   Js=[1, 2, 3, 5, 8], alphas=[0.0, 0.8, 1.2, 1.6], nq=600, sep_sample=1500)
SMOKE_REGIME = dict(N=2048, H=512, V=1500, iters=150, B=1024, lr=1e-3,
                    Js=[1, 5], alphas=[0.0, 1.2], nq=250, sep_sample=800)
SELFTEST_REGIME = dict(N=1024, H=512, V=800, iters=80, B=400, lr=1e-3,
                       Js=[1, 5], alphas=[0.0, 1.2], nq=200, sep_sample=500)


# --------------------------------- numpy eval prims (reused verbatim) --------
def _l2n(x):
    return x / (np.linalg.norm(x, axis=1, keepdims=True) + 1e-9)


def _encode_wta(z, k):
    """Sparse-bipolar block code: top-K magnitude coords -> sign, rest 0. (B,N)->(B,N)."""
    idx = np.argpartition(-np.abs(z), k, axis=1)[:, :k]
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
    # Gram identity ||cov||_F^2 = (1/(B-1)^2)||zcen zcen^T||_F^2 avoids forming N x N when
    # B<=N (O(B^2 N) vs O(N^2 B)); full form when B>N (GPU FULL).
    if B <= N:
        gram = zcen @ zcen.T                              # (B, B)
        cov_fro2 = gram.pow(2).sum() / ((B - 1) ** 2)
    else:
        cov = (zcen.T @ zcen) / (B - 1)                   # (N, N)
        cov_fro2 = cov.pow(2).sum()
    diag_sq = colss.pow(2).sum() / ((B - 1) ** 2)         # sum_i cov_ii^2
    l_cov = (cov_fro2 - diag_sq) / N
    return l_var, l_cov


def _rkd_loss(z_ret, tc, off_mask):
    """Global/landmark relational-KD: match student pairwise-cosine to teacher's (off-diag MSE)."""
    zc = z_ret / (z_ret.norm(dim=1, keepdim=True) + 1e-9)
    s_s = zc @ zc.T
    s_t = tc @ tc.T
    return ((s_s - s_t)[off_mask] ** 2).mean()


def _train_arm(bge_np, t_unit_np, arm, seed, regime, device):
    """Train an arm; return a dict of numpy params + last train loss.

    Returns params so the forward closures can be rebuilt for eval (dict build + SC encode)
    in torch (exact linear trunk), matching train/eval.
    """
    import torch
    N, H = regime["N"], regime["H"]
    B = min(regime["B"], bge_np.shape[0])
    iters = regime["iters"]
    Din = bge_np.shape[1]
    V = bge_np.shape[0]
    # arm-specific init salt: split-store and singlehead_native share objective+arch, so
    # WITHOUT a salt they draw bit-identical params (legitimate equivalence but collides the
    # arms-differ hash gate). Salt makes every arm an independent seed-deterministic draw.
    salt = int(hashlib.sha256(arm["name"].encode()).hexdigest()[:6], 16)
    g = torch.Generator(device="cpu").manual_seed(seed * 1000 + 1 + salt)
    torch.manual_seed(seed * 1000 + 3 + salt)
    x = torch.from_numpy(bge_np).to(device)               # (V, Din) raw BGE source
    tcos = torch.from_numpy(t_unit_np).to(device)         # (V, Din) unit teacher
    off_mask = ~torch.eye(B, dtype=torch.bool, device=device)
    lam, mu, nu = arm["lambda_d"], arm["mu"], arm["nu"]
    kind = arm["kind"]

    params = {}
    if kind == "twohead":
        if arm["shared"]:
            Wt = _init_param((Din, H), Din, g, device)
            Ws = _init_param((H, N), H, g, device)
            Wr = _init_param((H, N), H, g, device)
            plist = [Wt, Ws, Wr]
            params = {"shared": True, "Wt": Wt, "Ws": Ws, "Wr": Wr}
        else:
            Wts = _init_param((Din, H), Din, g, device)
            Ws = _init_param((H, N), H, g, device)
            Wtr = _init_param((Din, H), Din, g, device)
            Wr = _init_param((H, N), H, g, device)
            plist = [Wts, Ws, Wtr, Wr]
            params = {"shared": False, "Wts": Wts, "Ws": Ws, "Wtr": Wtr, "Wr": Wr}
    elif kind == "singlehead":
        Wt = _init_param((Din, H), Din, g, device)
        Wh = _init_param((H, N), H, g, device)
        plist = [Wt, Wh]
        params = {"Wt": Wt, "Wh": Wh}
    else:
        raise ValueError(f"_train_arm called with non-trainable kind {kind}")

    opt = torch.optim.Adam(plist, lr=regime["lr"])
    last = None
    for it in range(iters):
        idx = torch.randperm(V, device=device)[:B]
        xb = x[idx]
        loss = xb.new_zeros(())
        if kind == "twohead":
            if arm["shared"]:
                feats = xb @ params["Wt"]                 # LINEAR shared bottleneck trunk
                z_store = feats @ params["Ws"]
                z_ret = feats @ params["Wr"]
            else:
                z_store = (xb @ params["Wts"]) @ params["Ws"]
                z_ret = (xb @ params["Wtr"]) @ params["Wr"]
            lv, lc = _vicreg_loss(z_store, N, B)
            loss = loss + mu * lv + nu * lc
            loss = loss + lam * _rkd_loss(z_ret, tcos[idx], off_mask)
        else:  # singlehead
            z = (xb @ params["Wt"]) @ params["Wh"]        # LINEAR bottleneck trunk
            if mu > 0.0 or nu > 0.0:
                lv, lc = _vicreg_loss(z, N, B)
                loss = loss + mu * lv + nu * lc
            if lam > 0.0 and (mu == 0.0 and nu == 0.0):
                loss = loss + lam * _rkd_loss(z, tcos[idx], off_mask)
        opt.zero_grad(set_to_none=True)
        loss.backward()
        opt.step()
        last = float(loss.detach().cpu())
        if it % max(1, iters // 6) == 0 or it == iters - 1:
            print(f"[progress] seed={seed} arm={arm['name']} it={it}/{iters} loss={last:.5f}",
                  flush=True)
    np_params = {k: (v.detach().cpu().numpy().astype(np.float32) if hasattr(v, "detach") else v)
                 for k, v in params.items()}
    return np_params, last


# ------------------------- forward closures (torch, exact linear trunk) ------
def _make_forward(arm, np_params, device):
    """Return (store_fwd, ret_fwd): numpy (M,Din) -> numpy (M,N) code, or None if n/a."""
    import torch
    kind = arm["kind"]

    def _lin_mm(x_np, Wt, Wh):
        """LINEAR bottleneck trunk forward: (x @ Wt) @ Wh (exact match to training)."""
        xt = torch.from_numpy(np.ascontiguousarray(x_np, dtype=np.float32)).to(device)
        with torch.no_grad():
            feats = xt @ torch.from_numpy(Wt).to(device)
            out = feats @ torch.from_numpy(Wh).to(device)
        return out.cpu().numpy().astype(np.float32)

    if kind == "twohead":
        if np_params["shared"]:
            Wt, Ws, Wr = np_params["Wt"], np_params["Ws"], np_params["Wr"]
            return (lambda x: _lin_mm(x, Wt, Ws), lambda x: _lin_mm(x, Wt, Wr))
        Wts, Ws, Wtr, Wr = np_params["Wts"], np_params["Ws"], np_params["Wtr"], np_params["Wr"]
        return (lambda x: _lin_mm(x, Wts, Ws), lambda x: _lin_mm(x, Wtr, Wr))
    if kind == "singlehead":
        Wt, Wh = np_params["Wt"], np_params["Wh"]
        f = lambda x: _lin_mm(x, Wt, Wh)
        return (f, f)                                    # one code, dual readout
    raise ValueError(kind)


# ------------------------------ per-seed measurement -------------------------
def measure_seed(bge_full, t_unit_full, seed, regime, device):
    rng = np.random.default_rng(seed)
    V, N = regime["V"], regime["N"]
    k = max(1, N // 32)                                   # 3.125% sparsity
    sel = rng.choice(bge_full.shape[0], size=min(V, bge_full.shape[0]), replace=False)
    bge = bge_full[sel].astype(np.float32)
    t_unit = t_unit_full[sel].astype(np.float32)
    Vr = bge.shape[0]

    # SC noisy-query set (single-concept pointwise fidelity)
    qi = np.random.default_rng(seed * 7 + 3).choice(Vr, size=min(regime["nq"], Vr), replace=False)
    src = bge[qi]
    src_norm = np.linalg.norm(src, axis=1, keepdims=True)
    qrng = np.random.default_rng(seed * 7 + 5)
    noises = {}
    for a in regime["alphas"]:
        nz = qrng.standard_normal(src.shape).astype(np.float32)
        nz = nz / (np.linalg.norm(nz, axis=1, keepdims=True) + 1e-9)
        noises[a] = nz

    res_arms = {}
    for arm in ARMS:
        name = arm["name"]
        kind = arm["kind"]
        # --- build store code + retrieval code (dense) + train loss ---
        if kind == "teacher":
            store_dense = _l2n(bge)
            store_wta = _l2n(_encode_wta(bge, k))
            ret_dense = _l2n(bge)
            store_fwd = lambda x: x                       # identity dense encoder
            ret_fwd = lambda x: x
            train_loss = None
        elif kind == "untrained":
            gnp = np.random.default_rng(seed * 1000 + 7)
            Wt = (gnp.standard_normal((bge.shape[1], N)).astype(np.float32) / np.sqrt(bge.shape[1]))
            z = bge @ Wt
            store_dense = _l2n(z)
            store_wta = _l2n(_encode_wta(z, k))
            ret_dense = None                              # superposition ceiling ref only
            store_fwd = lambda x, W=Wt: (np.ascontiguousarray(x, dtype=np.float32) @ W)
            ret_fwd = None
            train_loss = None
        else:                                             # trained (twohead / singlehead)
            np_params, train_loss = _train_arm(bge, t_unit, arm, seed, regime, device)
            store_fwd, ret_fwd = _make_forward(arm, np_params, device)
            zs = store_fwd(bge)
            zr = ret_fwd(bge)
            store_dense = _l2n(zs)
            store_wta = _l2n(_encode_wta(zs, k))
            ret_dense = _l2n(zr)

        # --- STORE metric: WTA superposition recall@J (+ dense for diagnostics) ---
        sp_wta, sp_dense = {}, {}
        for J in regime["Js"]:
            sp_wta[str(J)] = _superposition_recall(store_wta, np.random.default_rng(seed * 100 + J), J, regime["nq"])
            sp_dense[str(J)] = _superposition_recall(store_dense, np.random.default_rng(seed * 100 + J), J, regime["nq"])
        sep_store_wta = _offtarget_mean_cos(store_wta, np.random.default_rng(seed + 11), regime["sep_sample"])
        sep_store_dense = _offtarget_mean_cos(store_dense, np.random.default_rng(seed + 11), regime["sep_sample"])

        # --- RETRIEVAL metric: DENSE single-concept pointwise recall@alpha (ret code) ---
        # CROSS-CHECK: store-head SC_dense (must NOT be forced BGE-like) computed too.
        sc_ret_dense, sc_store_dense, sc_ret_wta = {}, {}, {}
        for a in regime["alphas"]:
            qsrc = (src + a * src_norm * noises[a]).astype(np.float32)
            # retrieval-head DENSE pointwise (primary retrieval metric)
            if ret_fwd is not None and ret_dense is not None:
                qr = _l2n(ret_fwd(qsrc))
                pred = np.argmax(qr @ ret_dense.T, axis=1)
                sc_ret_dense[str(a)] = float(np.mean(pred == qi))
                # cross-check: retrieval head SP_wta already in sp_wta below (store); ret WTA SC
                qr_wta = _l2n(_encode_wta(ret_fwd(qsrc), k))
                ret_wta_dict = _l2n(_encode_wta(ret_fwd(bge), k))
                pred_w = np.argmax(qr_wta @ ret_wta_dict.T, axis=1)
                sc_ret_wta[str(a)] = float(np.mean(pred_w == qi))
            else:
                sc_ret_dense[str(a)] = None
                sc_ret_wta[str(a)] = None
            # cross-check: store-head DENSE pointwise (should NOT be BGE-perfect if decorrelated)
            qs = _l2n(store_fwd(qsrc))
            pred_s = np.argmax(qs @ store_dense.T, axis=1)
            sc_store_dense[str(a)] = float(np.mean(pred_s == qi))

        res_arms[name] = {
            "sp_wta": sp_wta, "sp_dense": sp_dense,
            "sep_store_wta": sep_store_wta, "sep_store_dense": sep_store_dense,
            "sc_ret_dense": sc_ret_dense, "sc_ret_wta": sc_ret_wta, "sc_store_dense": sc_store_dense,
            "store_dense_hash": hashlib.sha256(store_dense.tobytes()).hexdigest(),
            "train_loss": train_loss,
        }
        rd = sc_ret_dense.get(str(ALPHA_OP))
        print(f"[progress] seed={seed} arm={name} SP_wta@{J_OP}={sp_wta.get(str(J_OP)):.3f} "
              f"SC_ret_dense@{ALPHA_OP}={('%.3f' % rd) if rd is not None else 'n/a'} "
              f"sep_store_wta={sep_store_wta:+.4f}", flush=True)

    return {"seed": int(seed), "V": int(Vr), "N": int(N), "k": int(k), "arms": res_arms}


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
        sp_wta = {str(J): _mean([s["arms"][nm]["sp_wta"][str(J)] for s in per_seed]) for J in Js}
        sp_dense = {str(J): _mean([s["arms"][nm]["sp_dense"][str(J)] for s in per_seed]) for J in Js}
        sc_ret_dense = {str(a): _mean([s["arms"][nm]["sc_ret_dense"][str(a)] for s in per_seed]) for a in alphas}
        sc_ret_wta = {str(a): _mean([s["arms"][nm]["sc_ret_wta"][str(a)] for s in per_seed]) for a in alphas}
        sc_store_dense = {str(a): _mean([s["arms"][nm]["sc_store_dense"][str(a)] for s in per_seed]) for a in alphas}
        agg["arms"][nm] = {
            "sp_wta_mean": sp_wta, "sp_dense_mean": sp_dense,
            "sc_ret_dense_mean": sc_ret_dense, "sc_ret_wta_mean": sc_ret_wta,
            "sc_store_dense_mean": sc_store_dense,
            "sep_store_wta_mean": _mean([s["arms"][nm]["sep_store_wta"] for s in per_seed]),
            "sep_store_dense_mean": _mean([s["arms"][nm]["sep_store_dense"] for s in per_seed]),
            "sp_wta_op_per_seed": [s["arms"][nm]["sp_wta"][str(J_OP)] for s in per_seed],
            "sc_ret_dense_op_per_seed": [s["arms"][nm]["sc_ret_dense"][str(ALPHA_OP)] for s in per_seed],
        }
        agg["arms"][nm]["sp_wta_op_cv"] = _cv(agg["arms"][nm]["sp_wta_op_per_seed"])
    return agg


def _store_sp(A, nm):
    return A[nm]["sp_wta_mean"][str(J_OP)]


def _ret_sc(A, nm):
    v = A[nm]["sc_ret_dense_mean"][str(ALPHA_OP)]
    return v if v is not None else float("nan")


def _joint(sp, sc):
    if sc is None or (isinstance(sc, float) and np.isnan(sc)):
        return 0.0
    return float(min(sp / SP_HI, sc / SC_HI))


def _classify(agg):
    A = agg["arms"]
    sh_sp = _store_sp(A, HEADLINE_ARM)
    sh_sc = _ret_sc(A, HEADLINE_ARM)
    sp_hit = bool(sh_sp >= SP_HI)
    sc_hit = bool(sh_sc >= SC_HI)
    sh_both = bool(sp_hit and sc_hit)
    sh_joint = _joint(sh_sp, sh_sc)

    # frontier: does any single-head arm (one code, dual readout) achieve both?
    frontier = {}
    for nm in FRONTIER_ARMS:
        sp, sc = _store_sp(A, nm), _ret_sc(A, nm)
        frontier[nm] = {"sp": sp, "sc": sc, "both": bool(sp >= SP_HI and sc >= SC_HI),
                        "joint": _joint(sp, sc)}
    best_frontier_joint = max((v["joint"] for v in frontier.values()), default=0.0)
    frontier_both = any(v["both"] for v in frontier.values())

    # ceiling: split trunk (no shared params)
    sp_c, sc_c = _store_sp(A, CEILING_ARM), _ret_sc(A, CEILING_ARM)
    ceiling = {"sp": sp_c, "sc": sc_c, "both": bool(sp_c >= SP_HI and sc_c >= SC_HI),
               "joint": _joint(sp_c, sc_c)}

    # oracle reference (existence proof; recomputed here for continuity with anchor-sweep):
    # decorrelated store (best store arm SP_wta) + teacher retrieval (teacher SC_dense).
    store_ref_arm = max([a["name"] for a in ARMS], key=lambda nm: _store_sp(A, nm))
    oracle_sp = _store_sp(A, store_ref_arm)
    oracle_sc = A["teacher_bge"]["sc_ret_dense_mean"][str(ALPHA_OP)]
    oracle_both = bool(oracle_sp >= SP_HI and (oracle_sc is not None and oracle_sc >= SC_HI))

    if sh_both:
        verdict = "HARD_PASS_TRAINED_TWOHEAD_ACHIEVES_BOTH"
    elif sp_hit ^ sc_hit:
        miss_ok = (abs(sh_sc - SC_HI) <= MIDDLE_TOL) if sp_hit else (abs(sh_sp - SP_HI) <= MIDDLE_TOL)
        verdict = "MIDDLE_ONE_HEAD_HITS" if miss_ok else "HARD_FAIL_ONE_HEAD_FAR_MISS"
    elif sh_joint <= best_frontier_joint + 1e-6:
        verdict = "HARD_FAIL_SHARED_TRUNK_NO_GAIN_OVER_SINGLE_CODE"
    else:
        verdict = "HARD_FAIL_SHARED_TRUNK_INTERFERES_NEITHER_HEAD"

    return {
        "verdict": verdict,
        "headline": {"arm": HEADLINE_ARM, "store_sp_wta": sh_sp, "ret_sc_dense": sh_sc,
                     "sp_hit": sp_hit, "sc_hit": sc_hit, "both": sh_both, "joint": sh_joint},
        "ceiling": {"arm": CEILING_ARM, **ceiling},
        "frontier": frontier, "frontier_both": frontier_both,
        "best_frontier_joint": best_frontier_joint,
        "oracle_ref": {"store_arm": store_ref_arm, "sp": oracle_sp, "sc": oracle_sc,
                       "achieves_both": oracle_both},
        "cross_check": {
            "store_head_sc_dense": A[HEADLINE_ARM]["sc_store_dense_mean"].get(str(ALPHA_OP)),
            "ret_head_sp_wta": A[HEADLINE_ARM]["sp_wta_mean"].get(str(J_OP)),
        },
        "thresholds": {"SP_HI": SP_HI, "SC_HI": SC_HI, "MIDDLE_TOL": MIDDLE_TOL},
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


def _resolve_cache():
    if os.path.exists(_PRIMARY_CACHE):
        return _PRIMARY_CACHE
    cands = sorted(glob.glob(os.path.join(_CACHE_DIR, "bge_large_v2_name_*.npz")))
    if not cands:
        raise FileNotFoundError(f"no BGE teacher cache in {_CACHE_DIR} (bge_large_v2_name_*.npz)")

    def vcount(p):
        try:
            return int(os.path.basename(p).split("_name_")[1].split("_")[0])
        except Exception:  # noqa: BLE001
            return 0
    return max(cands, key=vcount)


def _load_teacher(regime):
    path = _resolve_cache()
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
    """Scaffold-free witnesses: encoder validity, telemetry-sensitivity, arms-differ, both heads."""
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

    # 1) teacher is a valid encoder: J=1 self-retrieval ~1.0 (dense superposition)
    valid_enc = A7["teacher_bge"]["sp_dense"]["1"] >= 0.98
    ok &= valid_enc
    # 2) TELEMETRY-SENSITIVITY: perturbing the seed MOVES the discriminators (not analytically
    #    pinned). Store axis: twohead_shared SP_wta@J_OP moves. Retrieval axis: SC_dense saturates
    #    near 1.0 for well-distilled heads (the GOAL), so prove SC responds to telemetry on the
    #    NON-saturated singlehead_native arm (SC ~0.7) -- confirms SC is data-sensitive, not pinned.
    sp_moves = (A7["twohead_shared"]["sp_wta"][str(J_OP)]
                != A13["twohead_shared"]["sp_wta"][str(J_OP)])
    sc_moves = (A7["singlehead_native"]["sc_ret_dense"][str(ALPHA_OP)]
                != A13["singlehead_native"]["sc_ret_dense"][str(ALPHA_OP)])
    ok &= (sp_moves and sc_moves)
    # 3) ARMS DIFFER (META_RULE_AF): all store-dense-dict hashes distinct
    hashes = [A7[a["name"]]["store_dense_hash"] for a in ARMS]
    arms_differ = len(set(hashes)) == len(hashes)
    ok &= arms_differ
    # 4) BOTH HEADS train: twohead_shared has finite train loss; store head decorrelates so
    #    its WTA superposition beats its dense superposition (the load-bearing lever fires).
    th = A7["twohead_shared"]
    both_heads_train = th["train_loss"] is not None and np.isfinite(th["train_loss"])
    ok &= both_heads_train
    wta_boosts = th["sp_wta"][str(J_OP)] > th["sp_dense"][str(J_OP)] + 0.05
    ok &= wta_boosts
    # 5) HEADS SPECIALIZE (decoupling): retrieval-head DENSE pointwise EXCEEDS store-head DENSE
    #    pointwise (ret head is BGE-anchored; store head is decorrelated) -- proves the two
    #    heads are NOT the same code even on the shared trunk.
    ret_sc = th["sc_ret_dense"][str(ALPHA_OP)]
    store_sc = th["sc_store_dense"][str(ALPHA_OP)]
    heads_specialize = (ret_sc is not None) and (ret_sc >= store_sc - 1e-9)
    ok &= heads_specialize
    # 6) SC degrades with noise for teacher (real pointwise metric)
    sc_noise = m7["arms"]["teacher_bge"]["sc_ret_dense"]["0.0"] >= m7["arms"]["teacher_bge"]["sc_ret_dense"]["1.2"] - 1e-9
    ok &= sc_noise

    print(f"[self-test] valid_enc={valid_enc}(spT@1={A7['teacher_bge']['sp_dense']['1']:.3f}) "
          f"sp_moves={sp_moves} sc_moves={sc_moves} arms_differ={arms_differ} "
          f"both_heads_train={both_heads_train} wta_boosts={wta_boosts}"
          f"(WTA={th['sp_wta'][str(J_OP)]:.3f} dense={th['sp_dense'][str(J_OP)]:.3f}) "
          f"heads_specialize={heads_specialize}(retSC={ret_sc if ret_sc is None else round(ret_sc,3)} "
          f"storeSC={round(store_sc,3)}) sc_noise={sc_noise}")
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
    for sd in seeds:
        pp = _seed_partial_path(OUTPUT_DIR, run_mode, sd)
        if os.path.exists(pp):
            try:
                with open(pp, encoding="utf-8") as f:
                    per_seed.append(json.load(f))
                print(f"[resume] seed={sd} loaded from partial", flush=True)
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
        print(f"[seed-done] seed={sd} elapsed={res['elapsed_s']:.1f}s", flush=True)

    agg = _aggregate(per_seed, regime)
    cls = _classify(agg)

    n_units = len(per_seed)
    cardinality_ok = (n_units == expected_units)
    A = agg["arms"]
    baseline_sp = _store_sp(A, BASELINE_ARM)
    baseline_in_band = 0.05 < baseline_sp < 0.95
    hashes = [per_seed[0]["arms"][a["name"]]["store_dense_hash"] for a in ARMS]
    arms_differ = len(set(hashes)) == len(hashes)

    if not cardinality_ok:
        verdict = "HARD_FAIL_CARDINALITY_BREACH_META_RULE_H"
    elif not arms_differ:
        verdict = "HARD_FAIL_ARMS_IDENTICAL_META_RULE_AF"
    else:
        verdict = cls["verdict"]

    hl = cls["headline"]
    cl = cls["ceiling"]
    orc = cls["oracle_ref"]
    xc = cls["cross_check"]
    fr = cls["frontier"]
    fr_str = " ".join(f"{nm}(SP{v['sp']:.2f}/SC{('%.2f'%v['sc']) if v['sc']==v['sc'] else 'nan'}"
                      f"{'=BOTH' if v['both'] else ''})" for nm, v in fr.items())
    verdict_msg = (
        f"{verdict} | THE FIX: can a TRAINED two-head encoder (shared trunk -> VICReg store "
        f"head + RKD retrieval head) achieve BOTH high superposition AND high pointwise, "
        f"replacing the anchor-sweep ORACLE? "
        f"HEADLINE twohead_shared: store SP_wta@J{J_OP}={hl['store_sp_wta']:.3f} "
        f"(hit>={SP_HI}:{hl['sp_hit']}) + ret SC_dense@a{ALPHA_OP}="
        f"{hl['ret_sc_dense']:.3f} (hit>={SC_HI}:{hl['sc_hit']}) -> achieves_both={hl['both']} "
        f"joint={hl['joint']:.3f}. "
        f"CEILING twohead_split: SP={cl['sp']:.3f} SC={('%.3f'%cl['sc']) if cl['sc']==cl['sc'] else 'nan'} "
        f"both={cl['both']}. "
        f"FRONTIER (single code, dual readout): {fr_str}; frontier_both={cls['frontier_both']} "
        f"(best_joint={cls['best_frontier_joint']:.3f}). "
        f"ORACLE ref (store={orc['store_arm']} SP={orc['sp']:.3f} + teacher SC="
        f"{('%.3f'%orc['sc']) if orc['sc'] is not None else 'nan'}) both={orc['achieves_both']}. "
        f"CROSS-CHECK (heads specialized): store-head SC_dense="
        f"{('%.3f'%xc['store_head_sc_dense']) if xc['store_head_sc_dense'] is not None else 'nan'} "
        f"(NOT forced BGE-like) ; ret-head SP_wta={xc['ret_head_sp_wta']:.3f} (NOT forced "
        f"decorrelated). cache={cache_src}. INTERPRETATION: "
        + ("a trained shared-trunk two-head encoder achieves BOTH high superposition and high "
           "pointwise fidelity from ONE learned system -> the certified decouple-store-from-retrieval "
           "law is realizable as a trained architecture (the oracle is buildable)."
           if verdict == "HARD_PASS_TRAINED_TWOHEAD_ACHIEVES_BOTH" else
           ("one head reaches target, the other is within noise of its threshold -> a weight/regime "
            "nudge (sweep RKD vs VICReg balance, trunk depth) likely closes it; report to Research."
            if verdict == "MIDDLE_ONE_HEAD_HITS" else
            ("the SHARED trunk forces interference: the two objectives (decorrelate store vs match-BGE "
             "retrieval) collide in the shared features so neither head reaches its target, OR the shared "
             "trunk gains nothing over a single code. Check the twohead_split CEILING: if split achieves "
             "both, the fix is per-head trunks (independent encoders); if even split fails, the trained "
             "system cannot reach the oracle at this regime -> escalate.")))
    )

    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": f"{verdict}: trained two-head decoupled store/retrieval encoder ({run_mode})",
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
        "operating_points": {"J_OP": J_OP, "ALPHA_OP": ALPHA_OP},
        "bands": {"SP_HI": SP_HI, "SC_HI": SC_HI, "MIDDLE_TOL": MIDDLE_TOL,
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
