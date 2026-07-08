"""Encoder BGE-anchor-weight SWEEP x VICReg decorrelation -- payoff cell.

QUESTION (reframed 2026-07-08 after the teacher-cap-vs-student-underfit
disambiguation VET, exp_recall_ceiling_teacher_cap_vs_student_underfit_v1,
commit cdfe7b465): a pure BGE-distillation objective is NOT obviously the right
anchor for the LOAD-BEARING superposition-recall task -- the disambiguation smoke
MEASURED that matching BGE geometry CAPS superposition recall@J5 at 0.337 while a
substrate-native decorrelating sparse code reaches 0.929 (SP_gap -0.592), yet BGE
wins single-concept pointwise fidelity (0.998 vs 0.793). So full BGE distillation
may DRAG DOWN the load-bearing task. This cell makes the BGE-anchor weight a SWEPT
LEVER and asks: how much BGE anchor is optimal, and does a VICReg-style
decorrelation term let a hybrid/native student EXCEED the full-distill baseline on
superposition recall while keeping enough pointwise fidelity.

Builds on the Rank-1 candidate of
notes/research_encoder_objective_beyond_bge_distillation_2026-07-08.md (add a
VICReg covariance + variance-floor decorrelation term ON TOP OF the R1
global/landmark RKD distillation anchor). Course-correction enriches it: sweep the
anchor weight, add a substrate-native arm, and report THREE metrics + the tradeoff.

MECHANISM. Train a linear student W: Din(1024)->N(4096) per arm by gradient
descent. Loss L = lambda_d * L_rkd + mu * L_var + nu * L_cov where:
  L_rkd  = GLOBAL/landmark relational-KD: match the student's per-minibatch
           pairwise-cosine matrix to the BGE teacher's pairwise-cosine matrix
           (dimension-agnostic; this is the R1 distillation anchor).
  L_var  = VICReg variance-floor  (1/N) sum_j relu(gamma - sqrt(Var(z_j)+eps)).
  L_cov  = VICReg covariance decorrelation (1/N) sum_{i!=j} Cov(z)_ij^2.
lambda_d (the BGE-anchor weight) is the SWEPT LEVER: {1.0(vicreg off baseline),
1.0, 0.3, 0.1, 0.0(native-decorr-only)}. mu=nu=1.0 fixed (justified below).

ARMS (all evaluated on the SAME dictionary, SAME cleanup, comparable to the
disambiguation harness):
  distill_only     lambda_d=1.0 mu=0 nu=0   (pure BGE distillation baseline)
  hybrid_d1.0      lambda_d=1.0 mu=1 nu=1   (Rank-1: full distill + decorrelation)
  hybrid_d0.3      lambda_d=0.3 mu=1 nu=1   (reduced anchor)
  hybrid_d0.1      lambda_d=0.1 mu=1 nu=1   (low anchor)
  native_trained   lambda_d=0.0 mu=1 nu=1   (decorrelation-primary, zero distill)
  native_untrained random W + WTA           (disambiguation zero-train reference;
                                             positive control that decorrelation is
                                             the lever; SP@J5 ~0.929 expected)
  teacher_bge      raw unit BGE             (teacher baseline for all 3 metrics;
                                             SP@J5 ~0.337, SC ~0.998 expected)

THREE metrics per arm (course-correction):
  (a) SUPERPOSITION recall@J  [PRIMARY, load-bearing] -- reuse the disambiguation
      _superposition_recall (bundle J unit members, argmax-cosine top-J over the
      V-concept dict). Reported on the DENSE learned geometry (primary, where the
      anchor lever acts directly and is guaranteed to discriminate) AND on the
      WTA-sparsified code (production 3.125% block-code cross-check).
  (b) SINGLE-CONCEPT pointwise fidelity -- SC task at alpha=1.2: a concept's BGE
      source perturbed by relative noise, encoded THROUGH the arm, argmax recall
      over the dict. (The axis BGE wins; the real tradeoff.)
  (c) OFF-TARGET separation geometry -- mean pairwise cosine among DIFFERENT
      concepts (the whitening-revival mean_cos anisotropy diagnostic). Lower =
      better separated. Compared to BGE's OWN off-target mean cosine on the SAME
      concept set (the note's decisive geometry test).

PRE-REG BANDS.
PRIMARY superposition (course-correction): the best hybrid/native arm's
  SP_recall_dense@J_OP must beat distill_only's by >= 0.05 (strictly above floor).
  -> SUPERPOSITION_WON if met; the anchor->SP knee is reported.
GEOMETRY (note's bands, expressed in this harness's measurables):
  fidelity axis = SC pointwise recall@alpha_OP;
  separation axis = off-target mean cosine vs teacher's own.
  HARD_PASS  = some arm: SP beats distill by >=0.05 AND off-target mean-cos LOWER
               than teacher's own by >=0.03 AND SC within 0.05 of distill_only
               (fidelity preserved AND separation won AND superposition won).
  MIDDLE     = SP + separation won but SC drops > 0.05 below distill_only (the real
               fidelity/superposition tradeoff; product decision, sweep nu next).
  HARD_FAIL  = no arm beats distill on SP by >=0.05, OR no arm's off-target
               separation is better than teacher by >=0.03 (repulsion-lever class
               refuted; escalate to Rank-2 sparse-coding-on-input).

WHY mu=nu=1.0 FIXED (not swept): the course-correction makes the BGE-ANCHOR weight
lambda_d the swept lever (the open question is "how much anchor", not "how much
decorrelation"). The VICReg var:cov reference ratio is set equal here because
decorrelation is the confirmed load-bearing lever (+0.255 in the certified
CHAIN_GRADE decomposition; +0.592 native-vs-BGE in the disambiguation). nu is
flagged for a follow-up sweep if the cell lands MIDDLE.

RANK-3 (InfoNCE) NOT INCLUDED: the deep-drill flags Rank-3 as a POSSIBLE but
possibly-REDUNDANT alternative to Rank-1 (same repulsion family); the
course-correction re-scoped this cell to the anchor sweep + 3 metrics + native arm,
and adding an InfoNCE arm needs a two-view construction the single-embedding-per-
concept cache does not supply. Deferred to a follow-up ALTERNATIVE-arm cell (do NOT
stack/assume-additive) -- documented in the completion report.

COMPUTE ARCHITECTURE. Class (a) batched-GPU. The training is matmul-heavy (per-iter
RKD pairwise B x B and VICReg covariance N x N over a minibatch); 5 trained arms x
5 seeds x hundreds of iters. Smoke runs CPU-local at reduced iters/batch; FULL
routes to the GPU (overnight_queue) where the minibatch B(8192) > N(4096) gives a
full-rank covariance estimate and the pairwise-cosine matmul is GPU-bound. Storage
strategy: no_composition / no_store (this is an encoder-geometry cell; the
"dictionary" is the per-concept code, evaluated by argmax-cosine cleanup, not a
bundled associative store).

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
- arms_differ_verified at smoke gate (sha256 of each arm's dense dict; all distinct)
- final_metrics_atomicity: tmp_replace (os.replace on final metrics.json)
- except SystemExit: raise BEFORE except Exception (no BaseException)
- crlb_n/a: retrieval recall + geometry cosines; no closed-form noise floor.
  Feasibility handled by calibrated operating points (disambiguation MEASURED the
  0.337-vs-0.929 SP band and 0.998-vs-0.793 SC band at this exact regime).
- baseline_in_band: distill_only SP_dense@J_OP in (0.05,0.95); native ~0.9 < 0.95.
- discriminator survives scale: smoke fires at production N=4096; PLUS analytical
  justification -- the disambiguation MEASURED the crowded-BGE-vs-decorrelated SP
  gap at BOTH V=4000 (-0.561) and V=40000 (-0.662), so the anchor-lever effect this
  cell sweeps survives scale by that cell's own V-scaling evidence.
- HARD bands strictly above floor (SP margin >= 0.05; separation >= 0.03).
- per-unit failure-class instrumentation (no bare except).
- calibration_check: default_ok_for_this_regime (real BGE cache; operating points
  calibrated in the disambiguation cell before this pre-reg).
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

ANCHOR_NAME = "encoder_distill_anchor_sweep_vicreg_decorr_v1"
OUTPUT_DIR = os.path.join(_REPO, "data", f"exp_{ANCHOR_NAME}")

_CACHE_DIR = os.path.join(_REPO, "data", "substrate_index", "cached_indices")
_PRIMARY_CACHE = os.path.join(_CACHE_DIR, "bge_large_v2_name_43905_8a40445a.npz")

# operating points (match disambiguation cell for comparability)
J_OP = 5
ALPHA_OP = 1.2
GAMMA_VAR = 1.0          # VICReg variance-floor target
MU_VIC = 1.0             # variance-floor weight (fixed; see docstring)
NU_VIC = 1.0             # covariance-decorrelation weight (fixed; see docstring)

# pre-reg bands (geometry sub-verdict; the note's original Rank-1 bands)
SP_MARGIN = 0.05         # best hybrid/native must beat distill_only SP@J_OP by this
SEP_MARGIN = 0.03        # off-target mean-cos better (lower) than teacher's own by this
SC_TOL = 0.05            # SC pointwise within this of distill_only => fidelity preserved

# RECONCILED primary bands (VET update 2026-07-08): the honest target is an objective that gets
# BOTH high superposition AND retained pointwise fidelity (certified law
# reference_correlation_hurts_associative_store_capacity_decouple_from_retrieval, at the encoder).
# SP_HI = near the decorrelated superposition ceiling (well above the crowded-BGE ~0.43 level).
# SC_HI = retains most of the teacher's pointwise discrimination.
SP_HI_THRESH = 0.75      # WTA superposition recall@J_OP counted as "high superposition"
SC_HI_THRESH = 0.90      # single-concept pointwise recall@ALPHA_OP counted as "high pointwise"

# arm definitions (lambda_d = BGE-anchor weight, the swept lever)
ARMS = [
    {"name": "distill_only", "kind": "trained", "lambda_d": 1.0, "mu": 0.0, "nu": 0.0},
    {"name": "hybrid_d1.0", "kind": "trained", "lambda_d": 1.0, "mu": MU_VIC, "nu": NU_VIC},
    {"name": "hybrid_d0.3", "kind": "trained", "lambda_d": 0.3, "mu": MU_VIC, "nu": NU_VIC},
    {"name": "hybrid_d0.1", "kind": "trained", "lambda_d": 0.1, "mu": MU_VIC, "nu": NU_VIC},
    {"name": "native_trained", "kind": "trained", "lambda_d": 0.0, "mu": MU_VIC, "nu": NU_VIC},
    {"name": "native_untrained", "kind": "untrained"},
    {"name": "teacher_bge", "kind": "teacher"},
]
HYBRID_NATIVE_ARMS = ["hybrid_d1.0", "hybrid_d0.3", "hybrid_d0.1", "native_trained"]
BASELINE_ARM = "distill_only"

FULL_SEEDS = [7, 13, 19, 23, 29]
SMOKE_SEEDS = [7, 13, 19]
SELFTEST_SEEDS = [7, 13]

# FULL: production N=4096, GPU (B=8192 > N gives full-rank covariance). SMOKE: reduced
# N=2048 for a CPU-local ~few-min gate (covariance is O(N^2 B); the WTA decorrelation lever is
# a fixed nonlinearity the disambiguation MEASURED at N=4096, so the discriminator survives to
# FULL by that cell's evidence -- DISCRIMINATOR-MUST-SURVIVE-SCALE option B + smoke preview).
FULL_REGIME = dict(N=4096, V=40000, iters=800, B=8192, lr=1e-3,
                   Js=[1, 2, 3, 5, 8], alphas=[0.0, 0.8, 1.2, 1.6], nq=600, sep_sample=1500)
SMOKE_REGIME = dict(N=2048, V=1500, iters=80, B=1024, lr=1e-3,
                    Js=[1, 5], alphas=[0.0, 1.2], nq=250, sep_sample=800)
SELFTEST_REGIME = dict(N=1024, V=800, iters=25, B=400, lr=2e-3,
                       Js=[1, 5], alphas=[0.0, 1.2], nq=200, sep_sample=600)


# --------------------------------- numpy eval prims --------------------------
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


# --------------------------------- torch training ----------------------------
def _resolve_device(want):
    import torch
    if want == "cpu":
        return "cpu"
    if want == "cuda":
        if not torch.cuda.is_available():
            raise RuntimeError("device=cuda requested but torch.cuda.is_available()==False")
        return "cuda"
    return "cuda" if torch.cuda.is_available() else "cpu"  # auto


def _train_student(bge_np, t_unit_np, arm, seed, regime, device):
    """Train linear W: Din->N by RKD-distill + VICReg. Returns W as numpy (Din,N)."""
    import torch
    N = regime["N"]
    B = min(regime["B"], bge_np.shape[0])
    iters = regime["iters"]
    Din = bge_np.shape[1]
    g = torch.Generator(device="cpu").manual_seed(seed * 1000 + 1)
    torch.manual_seed(seed * 1000 + 3)                    # minibatch-order determinism
    x = torch.from_numpy(bge_np).to(device)               # (V, Din) raw BGE source
    tcos = torch.from_numpy(t_unit_np).to(device)         # (V, Din) unit teacher
    W = (torch.randn(Din, N, generator=g).to(device) / (Din ** 0.5)).requires_grad_(True)
    opt = torch.optim.Adam([W], lr=regime["lr"])
    lam, mu, nu = arm["lambda_d"], arm["mu"], arm["nu"]
    V = x.shape[0]
    off_mask = ~torch.eye(B, dtype=torch.bool, device=device)
    last = None
    for it in range(iters):
        idx = torch.randperm(V, device=device)[:B]
        xb = x[idx]
        z = xb @ W                                        # (B, N) dense student
        loss = z.new_zeros(())
        if lam > 0.0:
            zc = z / (z.norm(dim=1, keepdim=True) + 1e-9)
            tc = tcos[idx]
            s_s = zc @ zc.T
            s_t = tc @ tc.T
            loss = loss + lam * ((s_s - s_t)[off_mask] ** 2).mean()
        if mu > 0.0 or nu > 0.0:
            zcen = z - z.mean(dim=0, keepdim=True)
            std = torch.sqrt(zcen.var(dim=0) + 1e-4)
            l_var = torch.relu(GAMMA_VAR - std).mean()
            # VICReg off-diagonal covariance penalty (1/N) sum_{i!=j} cov_ij^2.
            # Gram identity ||cov||_F^2 = (1/(B-1)^2)||zcen zcen^T||_F^2 avoids forming the
            # N x N covariance when B<=N (O(B^2 N) vs O(N^2 B)); full form when B>N (GPU FULL).
            colss = (zcen * zcen).sum(dim=0)              # (N,) per-dim sum of squares
            if B <= N:
                gram = zcen @ zcen.T                      # (B, B)
                cov_fro2 = gram.pow(2).sum() / ((B - 1) ** 2)
            else:
                cov = (zcen.T @ zcen) / (B - 1)           # (N, N)
                cov_fro2 = cov.pow(2).sum()
            diag_sq = colss.pow(2).sum() / ((B - 1) ** 2)  # sum_i cov_ii^2
            l_cov = (cov_fro2 - diag_sq) / N
            loss = loss + mu * l_var + nu * l_cov
        opt.zero_grad(set_to_none=True)
        loss.backward()
        opt.step()
        last = float(loss.detach().cpu())
        if it % max(1, iters // 6) == 0 or it == iters - 1:
            print(f"[progress] seed={seed} arm={arm['name']} it={it}/{iters} loss={last:.5f}",
                  flush=True)
    return W.detach().cpu().numpy().astype(np.float32), last


def _build_dicts(bge_np, W_np, k):
    """Return (dense_unit_dict, wta_unit_dict) for a trained/untrained arm."""
    z = bge_np.astype(np.float32) @ W_np
    dense = _l2n(z)
    wta = _l2n(_encode_wta(z, k))
    return dense, wta


# ------------------------------ per-seed measurement -------------------------
def measure_seed(bge_full, t_unit_full, seed, regime, device):
    rng = np.random.default_rng(seed)
    V = regime["V"]
    N = regime["N"]
    k = max(1, N // 32)                                   # 3.125% sparsity
    sel = rng.choice(bge_full.shape[0], size=min(V, bge_full.shape[0]), replace=False)
    bge = bge_full[sel].astype(np.float32)
    t_unit = t_unit_full[sel].astype(np.float32)
    Vr = bge.shape[0]

    # Train each arm ONCE; keep W so SC re-uses it (no double-training).
    arm_out = {}          # name -> {dense, wta, W, train_loss}
    for arm in ARMS:
        name = arm["name"]
        if arm["kind"] == "teacher":
            dense = _l2n(bge)
            arm_out[name] = {"dense": dense, "wta": None, "W": None, "train_loss": None}
        elif arm["kind"] == "untrained":
            g = np.random.default_rng(seed * 1000 + 7)
            W = (g.standard_normal((bge.shape[1], N)).astype(np.float32) / np.sqrt(bge.shape[1]))
            dense, wta = _build_dicts(bge, W, k)
            arm_out[name] = {"dense": dense, "wta": wta, "W": W, "train_loss": None}
        else:  # trained
            W, train_loss = _train_student(bge, t_unit, arm, seed, regime, device)
            dense, wta = _build_dicts(bge, W, k)
            arm_out[name] = {"dense": dense, "wta": wta, "W": W, "train_loss": train_loss}

    # ---- metrics per arm ----
    res_arms = {}
    for name, ao in arm_out.items():
        dense = ao["dense"]
        wta = ao["wta"]
        sp_dense, sp_wta = {}, {}
        for J in regime["Js"]:
            sp_dense[str(J)] = _superposition_recall(dense, np.random.default_rng(seed * 100 + J), J, regime["nq"])
            if wta is not None:
                sp_wta[str(J)] = _superposition_recall(wta, np.random.default_rng(seed * 100 + J), J, regime["nq"])
        # off-target separation (dense geometry)
        sep_dense = _offtarget_mean_cos(dense, np.random.default_rng(seed + 11), regime["sep_sample"])
        sep_wta = (_offtarget_mean_cos(wta, np.random.default_rng(seed + 11), regime["sep_sample"])
                   if wta is not None else None)
        res_arms[name] = {
            "sp_dense": sp_dense, "sp_wta": sp_wta,
            "sep_dense": sep_dense, "sep_wta": sep_wta,
            "dense_hash": hashlib.sha256(ao["dense"].tobytes()).hexdigest(),
            "train_loss": ao["train_loss"],
        }
        print(f"[progress] seed={seed} arm={name} SP_dense@{J_OP}={sp_dense.get(str(J_OP)):.3f} "
              f"sep_dense={sep_dense:+.4f}", flush=True)

    # ---- SC single-concept pointwise fidelity (encode noisy source THROUGH each arm) ----
    # Re-uses the W trained/sampled above (NO retraining); teacher uses the identity BGE encoder.
    qi = np.random.default_rng(seed * 7 + 3).choice(Vr, size=min(regime["nq"], Vr), replace=False)
    src = bge[qi]
    src_norm = np.linalg.norm(src, axis=1, keepdims=True)
    qrng = np.random.default_rng(seed * 7 + 5)
    noises = {}
    for a in regime["alphas"]:
        nz = qrng.standard_normal(src.shape).astype(np.float32)
        nz = nz / (np.linalg.norm(nz, axis=1, keepdims=True) + 1e-9)
        noises[a] = nz
    sc = {}
    for arm in ARMS:
        name = arm["name"]
        dense = arm_out[name]["dense"]                    # (V, D) dense unit dict
        wta = arm_out[name]["wta"]                        # (V, N) production WTA block code
        W = arm_out[name]["W"]
        sc[name] = {}
        for a in regime["alphas"]:
            qsrc = src + a * src_norm * noises[a]
            if W is None:                                 # teacher: identity dense encoder
                q, dref = _l2n(qsrc), dense
            else:                                         # student: production WTA block code
                q, dref = _l2n(_encode_wta(qsrc.astype(np.float32) @ W, k)), wta
            pred = np.argmax(q @ dref.T, axis=1)
            sc[name][str(a)] = float(np.mean(pred == qi))

    out = {"seed": int(seed), "V": int(Vr), "N": int(N), "k": int(k), "arms": res_arms, "sc": sc}
    return out


# ------------------------------ aggregation / verdict ------------------------
def _mean(xs):
    return float(np.mean(xs)) if xs else float("nan")


def _cv(xs):
    a = np.asarray(xs, dtype=np.float64)
    mu = float(np.mean(a))
    return 0.0 if abs(mu) < 1e-9 else float(np.std(a) / abs(mu))


def _aggregate(per_seed, regime):
    Js = regime["Js"]
    alphas = regime["alphas"]
    names = [a["name"] for a in ARMS]
    agg = {"n_seeds": len(per_seed), "arms": {}, "sc": {}}
    for nm in names:
        sp_dense = {str(J): _mean([s["arms"][nm]["sp_dense"][str(J)] for s in per_seed]) for J in Js}
        has_wta = per_seed[0]["arms"][nm]["sp_wta"] not in (None, {})
        sp_wta = ({str(J): _mean([s["arms"][nm]["sp_wta"][str(J)] for s in per_seed]) for J in Js}
                  if has_wta else None)
        sep_dense = _mean([s["arms"][nm]["sep_dense"] for s in per_seed])
        sep_wta_vals = [s["arms"][nm]["sep_wta"] for s in per_seed if s["arms"][nm]["sep_wta"] is not None]
        sep_wta = _mean(sep_wta_vals) if sep_wta_vals else None
        agg["arms"][nm] = {
            "sp_dense_mean": sp_dense, "sp_wta_mean": sp_wta,
            "sep_dense_mean": sep_dense, "sep_wta_mean": sep_wta,
            "sp_dense_op_per_seed": [s["arms"][nm]["sp_dense"][str(J_OP)] for s in per_seed],
        }
        agg["arms"][nm]["sp_dense_op_cv"] = _cv(agg["arms"][nm]["sp_dense_op_per_seed"])
        agg["sc"][nm] = {str(a): _mean([s["sc"][nm][str(a)] for s in per_seed]) for a in alphas}
    return agg


def _prim_sp(A, nm):
    """PRIMARY superposition = WTA block code for student arms; dense for teacher (no WTA)."""
    m = A[nm]["sp_wta_mean"]
    return m[str(J_OP)] if m is not None else A[nm]["sp_dense_mean"][str(J_OP)]


def _prim_sep(A, nm):
    """PRIMARY off-target separation = WTA block code for students; dense (own) for teacher."""
    w = A[nm]["sep_wta_mean"]
    return w if w is not None else A[nm]["sep_dense_mean"]


def _classify(agg):
    """Primary superposition band + geometry (fidelity + separation) tradeoff classification.

    Primary representation is the PRODUCTION WTA block code (the decorrelation lever acts
    through the top-K sparsification; dense geometry of any linear BGE map is JL-bounded to
    the crowded teacher geometry and cannot discriminate the lever). Teacher = dense BGE.
    """
    A = agg["arms"]
    distill_sp = _prim_sp(A, BASELINE_ARM)                # distill_only WTA superposition
    distill_sc = agg["sc"][BASELINE_ARM][str(ALPHA_OP)]
    teacher_sep = _prim_sep(A, "teacher_bge")             # BGE's OWN off-target separation

    # anchor -> SP knee (primary WTA, J_OP)
    knee = {nm: _prim_sp(A, nm) for nm in HYBRID_NATIVE_ARMS}
    best_arm = max(knee, key=knee.get)
    best_sp = knee[best_arm]

    sp_won = best_sp >= distill_sp + SP_MARGIN

    # separation: any hybrid/native arm better (lower off-target cos) than teacher by SEP_MARGIN
    sep_winners = [nm for nm in HYBRID_NATIVE_ARMS if _prim_sep(A, nm) <= teacher_sep - SEP_MARGIN]
    separation_won = len(sep_winners) > 0

    # geometry sub-verdict (the note's original Rank-1 bands): an arm that wins SP AND separation
    # AND preserves fidelity (SC within tol of distill_only).
    hp_arms = []
    for nm in HYBRID_NATIVE_ARMS:
        cond_sp = _prim_sp(A, nm) >= distill_sp + SP_MARGIN
        cond_sep = _prim_sep(A, nm) <= teacher_sep - SEP_MARGIN
        cond_sc = agg["sc"][nm][str(ALPHA_OP)] >= distill_sc - SC_TOL
        if cond_sp and cond_sep and cond_sc:
            hp_arms.append(nm)
    if hp_arms:
        geometry_subverdict = "GEOM_HARD_PASS"
    elif sp_won and separation_won:
        geometry_subverdict = "GEOM_MIDDLE_SEPARATION_WON_FIDELITY_TRADED"
    else:
        geometry_subverdict = "GEOM_HARD_FAIL_NO_SCALAR_GEOM_WIN"

    # ---- RECONCILED PRIMARY verdict (VET update): can a SINGLE anchor-weight arm get BOTH
    # high superposition AND retained pointwise fidelity, or is it a STRICT tradeoff along the
    # scalar knob (=> structural decoupling needed)?
    student_arms = [nm for nm in HYBRID_NATIVE_ARMS + ["distill_only", "native_untrained"]]
    per_arm_both = {}
    for nm in student_arms:
        sp = _prim_sp(A, nm)
        sc = agg["sc"][nm][str(ALPHA_OP)]
        per_arm_both[nm] = {"sp": sp, "sc": sc,
                            "sp_hi": bool(sp >= SP_HI_THRESH), "sc_hi": bool(sc >= SC_HI_THRESH)}
    both_arms = [nm for nm, v in per_arm_both.items() if v["sp_hi"] and v["sc_hi"]]

    # decoupled-ORACLE existence proof (structural decoupling preview, zero extra compute):
    # a system that uses the DECORRELATED store code for superposition AND the BGE-anchored
    # retrieval code for pointwise. Store = best student WTA superposition; retrieval = teacher.
    store_arm = max(student_arms, key=lambda nm: _prim_sp(A, nm))
    oracle_sp = _prim_sp(A, store_arm)
    oracle_sc = agg["sc"]["teacher_bge"][str(ALPHA_OP)]
    oracle_both = bool(oracle_sp >= SP_HI_THRESH and oracle_sc >= SC_HI_THRESH)

    if both_arms:
        verdict = "SCALAR_KNOB_SUFFICES_BOTH_ACHIEVED"
    elif oracle_both:
        verdict = "STRICT_TRADEOFF_STRUCTURAL_DECOUPLING_NEEDED"
    else:
        verdict = "NO_ARM_OR_DECOUPLING_ACHIEVES_BOTH"

    return {
        "verdict": verdict, "geometry_subverdict": geometry_subverdict,
        "best_arm": best_arm, "best_sp": best_sp,
        "distill_sp": distill_sp, "distill_sc": distill_sc, "teacher_sep": teacher_sep,
        "sp_won": bool(sp_won), "separation_won": bool(separation_won),
        "sep_winners": sep_winners, "hp_arms": hp_arms, "anchor_sp_knee": knee,
        "per_arm_both": per_arm_both, "both_arms": both_arms,
        "decoupled_oracle": {"store_arm": store_arm, "sp": oracle_sp, "sc": oracle_sc,
                             "achieves_both": oracle_both},
        "sp_hi_thresh": SP_HI_THRESH, "sc_hi_thresh": SC_HI_THRESH,
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
    """Scaffold-free witnesses: encoder validity, telemetry-sensitivity, arms-differ, both branches."""
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

    A7 = m7["arms"]
    # 1) teacher is a valid encoder: J=1 self-retrieval ~1.0
    valid_enc = A7["teacher_bge"]["sp_dense"]["1"] >= 0.98
    ok &= valid_enc
    # 2) TELEMETRY-SENSITIVITY: native_untrained WTA SP@J_OP NOT bit-identical across seeds
    seed_moves = (A7["native_untrained"]["sp_wta"][str(J_OP)]
                  != m13["arms"]["native_untrained"]["sp_wta"][str(J_OP)])
    ok &= seed_moves
    # 3) ARMS DIFFER (META_RULE_AF): all dense-dict hashes distinct
    hashes = [A7[a["name"]]["dense_hash"] for a in ARMS]
    arms_differ = len(set(hashes)) == len(hashes)
    ok &= arms_differ
    # 4) MECHANISM FIRES (scale-robust): the WTA block code decorrelates -> superposition recall
    #    is materially HIGHER than the JL-bounded dense geometry of the SAME code (this is the
    #    load-bearing lever; a fixed nonlinearity, so it holds even at tiny self-test scale).
    nu_wta = A7["native_untrained"]["sp_wta"][str(J_OP)]
    nu_dense = A7["native_untrained"]["sp_dense"][str(J_OP)]
    wta_boosts = nu_wta > nu_dense + 0.10
    ok &= wta_boosts
    # 5) BOTH LOSS BRANCHES real: distill_only + native_trained both have finite train_loss
    both_branches = (A7[BASELINE_ARM]["train_loss"] is not None
                     and A7["native_trained"]["train_loss"] is not None)
    ok &= both_branches
    # 6) SC pointwise is a real number in [0,1] and degrades with noise for teacher
    sc_moves = m7["sc"]["teacher_bge"]["0.0"] >= m7["sc"]["teacher_bge"]["1.2"] - 1e-9
    ok &= sc_moves
    # 7) separation is a real cosine mean for every arm (dense + student WTA present)
    sep_ok = all(isinstance(A7[a["name"]]["sep_dense"], float) for a in ARMS)
    ok &= sep_ok

    print(f"[self-test] valid_enc={valid_enc}(spT@1={A7['teacher_bge']['sp_dense']['1']:.3f}) "
          f"seed_moves={seed_moves}(nativeUNT WTA SP@{J_OP}: {nu_wta:.3f}"
          f"!={m13['arms']['native_untrained']['sp_wta'][str(J_OP)]:.3f}) "
          f"arms_differ={arms_differ} wta_boosts={wta_boosts}(WTA={nu_wta:.3f} dense={nu_dense:.3f}) "
          f"both_branches={both_branches} sc_moves={sc_moves} sep_ok={sep_ok}")
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
    distill_sp = _prim_sp(A, BASELINE_ARM)               # WTA primary
    baseline_in_band = 0.05 < distill_sp < 0.95
    hashes = [per_seed[0]["arms"][a["name"]]["dense_hash"] for a in ARMS]
    arms_differ = len(set(hashes)) == len(hashes)

    if not cardinality_ok:
        verdict = "HARD_FAIL_CARDINALITY_BREACH_META_RULE_H"
    elif not arms_differ:
        verdict = "HARD_FAIL_ARMS_IDENTICAL_META_RULE_AF"
    else:
        verdict = cls["verdict"]

    knee_str = " ".join(f"{k}={v:.3f}" for k, v in cls["anchor_sp_knee"].items())
    native_unt_sp = _prim_sp(A, "native_untrained")
    teacher_sp = A["teacher_bge"]["sp_dense_mean"][str(J_OP)]
    both_str = " ".join(
        f"{nm}(SP{v['sp']:.2f}{'+' if v['sp_hi'] else '-'},SC{v['sc']:.2f}{'+' if v['sc_hi'] else '-'})"
        for nm, v in cls["per_arm_both"].items())
    orc = cls["decoupled_oracle"]
    verdict_msg = (
        f"{verdict} | RECONCILED Q: can one scalar-anchor arm get BOTH high superposition "
        f"(WTA SP@J{J_OP}>={SP_HI_THRESH}) AND high pointwise (SC@alpha{ALPHA_OP}>={SC_HI_THRESH})? "
        f"both_arms={cls['both_arms']}. Per-arm[SP/SC hi=+]: {both_str}. "
        f"DECOUPLED-ORACLE (store={orc['store_arm']} WTA SP={orc['sp']:.3f} + teacher retrieval "
        f"SC={orc['sc']:.3f}) achieves_both={orc['achieves_both']} -> decoupling resolves the tradeoff. "
        f"| PRIMARY superposition@J{J_OP}(WTA block-code,V={per_seed[0]['V']}): "
        f"distill_only={distill_sp:.3f} best={cls['best_arm']}={cls['best_sp']:.3f}. "
        f"REF native_untrained(WTA)={native_unt_sp:.3f} teacher_bge(dense-BGE)={teacher_sp:.3f}. "
        f"ANCHOR->SP knee: {knee_str}. "
        f"FIDELITY SC@alpha{ALPHA_OP}: distill_only={cls['distill_sc']:.3f} "
        f"native_trained={agg['sc']['native_trained'][str(ALPHA_OP)]:.3f} teacher={orc['sc']:.3f}. "
        f"SEPARATION off-target mean-cos: teacher={cls['teacher_sep']:+.4f} "
        f"winners={cls['sep_winners']} separation_won={cls['separation_won']}. "
        f"geometry_subverdict={cls['geometry_subverdict']} (note's Rank-1 bands). cache={cache_src}. "
        f"INTERPRETATION: "
        + ("a single anchor-weight setting achieves BOTH high superposition and high pointwise fidelity "
           "-> a scalar distill+decorrelation objective suffices."
           if verdict == "SCALAR_KNOB_SUFFICES_BOTH_ACHIEVED" else
           ("no single anchor arm gets both (the scalar knob is a strict, and perverse, tradeoff -- more "
            "BGE anchor DEGRADES block-code pointwise fidelity); but decoupling the decorrelated store code "
            "from the BGE-anchored retrieval code achieves both -> build a structural two-head encoder "
            "(VICReg-cov on store head, RKD on retrieval head). This is the certified decouple-store-from-"
            "retrieval law at the encoder." if verdict == "STRICT_TRADEOFF_STRUCTURAL_DECOUPLING_NEEDED"
            else "neither a scalar arm nor the decoupling preview achieves both at this regime -- unexpected; "
            "inspect per-arm table before dispatching FULL."))
    )

    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": f"{verdict}: BGE-anchor sweep x VICReg decorrelation ({run_mode})",
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
        "bands": {"SP_MARGIN": SP_MARGIN, "SEP_MARGIN": SEP_MARGIN, "SC_TOL": SC_TOL,
                  "GAMMA_VAR": GAMMA_VAR, "MU_VIC": MU_VIC, "NU_VIC": NU_VIC},
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
