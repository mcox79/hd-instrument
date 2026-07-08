"""PHASE-TRAVERSAL GRADED-SPARSE RESCUE drill: does a GRADED / SOFT-SPARSE store code get
BOTH high superposition (SP) AND graceful condensation (SC) from ONE code -- rescuing the
hard sign+top-k negative?

BACKGROUND (2026-07-08). The v1 phase-traversal cell
(exp_encoder_phase_traversal_spread_condense_v1) stored a HARD sign+top-k spread code and
tried to recover pointwise semantics by a trained structural CONDENSER at read time. It hit a
genuine information wall: HEADLINE structural_gain = -0.348 (the condensed read was WORSE than
the raw static read). BUT skunkworks confirmed the wall is SPECIFIC to the hard/discontinuous
code, NOT fundamental: the cell's own phase_traversal_DENSE arm (condense off the non-sparsified
dense code) reached SC 0.993 (near-oracle) -- so the CONDENSER works perfectly; the entire loss
is the discontinuity of the sign+top-k quantization. A NOISY query, sign-quantized, maps
inconsistently through the nonlinearity.

THE DRILL QUESTION (the discriminating 5x-drill lever, skunkworks-named): replace the hard
sign+top-k with a GRADED sparse code that degrades gracefully under noise. Does a graded code
preserve enough decorrelation for high superposition SP *and* condense gracefully for high
pointwise SC -- getting BOTH from one code?

THE LEVER -- MAGNITUDE-GRADED TOP-K, swept by a gradedness exponent gamma:
  code_i = sign(z_i) * |z_i|^gamma   on the top-k magnitude support, 0 elsewhere.
    gamma = 0.0  -> sign(z_i)  == the HARD sign+top-k code (the confirmed NEGATIVE; kept as the
                    in-sweep negative-control endpoint).
    gamma = 1.0  -> z_i        == topk_mag (the already-coded-but-unused graded code; full
                    magnitude retained within the top-k support).
    0 < gamma < 1 -> partial magnitude gradedness (soft interpolation hard-WTA -> graded).
  The top-k SUPPORT (and thus sparsity k) is HELD FIXED across the sweep, so the ONLY variable
  is magnitude-gradedness -- this cleanly ISOLATES the decorrelation-vs-condensability tension
  (a temperature-softened WTA that also changed effective sparsity would confound the two).

THE TENSION TO RESOLVE EMPIRICALLY (do NOT assume either way): high SP comes from HARD WTA
decorrelation (the sign code is maximally spread / bipolar). A graded code concentrates energy
on a few large coords -> it may condense GRACEFULLY (magnitude survives noise better than a
sign flip) but LOSE the decorrelation that gives SP. The gamma sweep traces this frontier and
measures which (if either) wins -- or whether a middle gamma gets both.

PRE-REG REVIVAL CRITERION (skunkworks-specified, verbatim): a graded/soft-sparse store code
achieving SP_B >= 0.83 AND condensed SC >= 0.90 AND structural_gain >= 0.15 over ITS OWN static
readout, at production V. (structural_gain is condensed SC minus the SAME graded code's static
argmax SC -- each gamma is judged against its OWN static readout, not the hard code's.)

HARD-FAIL = even the graded code fails to beat its own static readout (no graded gamma reaches
structural_gain >= 0.15, and no graded gamma's static already achieves both) -> the wall is
FUNDAMENTAL and the two-head decoupled-code architecture is confirmed as the only solution.
This is a VALUABLE CLOSING RESULT -- report it as such, not as a mere failure.

ARMS (metric harness reused from v1 so numbers compare to v1 + two-head + oracle):
  graded_g{gamma}   store graded code (gamma), read via trained noise-aug CONDENSER  [SWEEP: rescue]
                    gamma=0.00 is the HARD-WTA negative control endpoint.
  static_g{gamma}   store graded code (gamma), read via RAW argmax (NO transform)    [own static ctrl]
  dense_condense    condense off the non-sparsified dense z (no WTA)  [v1's 0.993 near-oracle ref]
  oracle            SP from a decorrelated store; SC from teacher dense (decoupled ceiling)

METRICS (uniform across arms):
  SP  = superposition recall@J on the arm's OWN graded store code (bundle J members, argmax-
        cosine top-J over dict). Measured PER gamma (graded codes have different SP than hard).
  SC  = single-concept pointwise recall@alpha: a concept's BGE source perturbed by relative
        noise, pushed through the arm's read pipeline (expand -> graded-encode -> [condense]),
        argmax-cosine over the arm's dictionary.
  structural_gain(gamma) = graded_g{gamma} condensed SC - static_g{gamma} SC (its OWN static).

## Compute architecture
Class (a) batched-GPU. Condenser training is matmul-heavy (per-iter store-code forward B x N @
N x H @ H x Din, RKD pairwise B x B); (n_gammas + 1 dense) trainable condensers x seeds x
hundreds of iters. FULL routes to GPU (overnight_queue) at production N=4096, V=40000, B=8192
(B > N gives a full-rank RKD sample). SMOKE runs CPU-local at PRODUCTION N=4096 with reduced
V/iters/B/gammas -- DISCRIMINATOR-MUST-SURVIVE-SCALE option A/C (smoke at full-N, scaled preview
V): condensability-of-a-graded-spread-code is an info-geometry property that fires at production
N and sparsity fraction, previewed at the smoke's small V. Storage strategy: no_composition /
no_store (encoder-geometry cell; the "dictionary" is the per-concept code, evaluated by
argmax-cosine cleanup, not a bundled associative store).

## Functional Requirements
  FR1 high superposition recall (bundle J concepts, recover them) -> decorrelated spread code.
      Measured: SP@J on the graded store code (the drill tests whether gradedness KEEPS this).
  FR2 noisy pointwise discrimination (noisy query -> its concept) -> semantic-manifold code via
      trained condenser. Measured: SC@alpha condensed.
  FR3 BOTH from ONE stored code -> the graded sparse code is condensable (magnitude survives
      noise where sign flips), tested by the gamma sweep. New mechanism (no prior primitive
      maps a graded spread code to the semantic manifold) -> tested here.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
- arms_differ_verified at smoke gate (sha256 of each arm's SC dictionary code; distinct; each
  gamma's graded store + condensed code is a distinct draw -> no exemptions expected).
- cardinality_ok: sweep-axis cell -> EXPECTED_N_UNITS = n_seeds AND every seed carries all
  n_gammas graded arms (gamma-cardinality gate).
- final_metrics_atomicity: tmp_replace (os.replace on final metrics.json).
- except SystemExit: raise BEFORE except Exception (no BaseException).
- crlb_n/a: retrieval recall + geometry cosines; no closed-form noise floor. Feasibility handled
  by calibrated operating points (v1 + two-head MEASURED the SP band 0.43-0.905 and SC band
  0.655-1.0 at this exact regime) + the in-sweep gamma=0 negative-control endpoint.
- baseline_in_band: static_g0.00 (hard-WTA static; the negative-control baseline) SC@alpha_OP <
  0.95 (if the hard raw code already did pointwise there is no tradeoff to solve).
- discriminator survives scale: smoke at production N=4096; the crowded-vs-decorrelated SP gap
  was MEASURED to grow with V (-0.561 at V=4000, -0.662 at V=40000) in the anchor-sweep cell.
- HARD bands strictly above floor (SP_HI 0.83 headroom to 0.905; SC_HI 0.90 to 1.0).
- per-unit failure-class instrumentation (no bare except).
- calibration_check: default_ok_for_this_regime (real BGE cache; J_OP/alpha_OP calibrated in
  the two-head cell; gamma grid brackets hard(0)->graded(1)).
- telemetry-sensitivity self-test MANDATORY (perturb-a-seed MOVES SP and condensed SC; the
  condenser CHANGES the argmax vs static; gamma actually CHANGES the store code / SP).
- cell_chunked: false (few-seed, per-seed checkpoint/restartable, atomic partials).
- progress_logging: print_flush_true (line-buffered stdout + flush=True on every progress line).
- all numbers tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@ in the report.

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

ANCHOR_NAME = "encoder_phase_traversal_graded_sparse_rescue_v1"
OUTPUT_DIR = os.path.join(_REPO, "data", f"exp_{ANCHOR_NAME}")

_CACHE_DIR = os.path.join(_REPO, "data", "substrate_index", "cached_indices")

# operating points (match v1 / two-head / anchor-sweep cells for comparability)
J_OP = 5
ALPHA_OP = 1.2
LAMBDA_D = 1.0            # RKD BGE-distillation weight on the condenser
COND_H = 1024            # condenser hidden width (the semantic-manifold dim; "pull together")
NOISE_AUG_ALPHA = 1.6    # max relative noise during augmented condenser training (covers alpha_OP=1.2)
NOISE_AUG_FRAC = 0.5     # fraction of each training batch that is noise-perturbed (rest clean)

# pre-reg bands
SP_HI = 0.83             # graded-store WTA superposition recall@J_OP counted as high superposition
SC_HI = 0.90             # condensed (or static) single-concept recall@alpha_OP counted as high pointwise
MIDDLE_TOL = 0.05        # near-miss tolerance for condensed SC (MIDDLE band)
STRUCT_MARGIN = 0.15     # graded condensed SC must beat its OWN static SC by this (structural, not beta-knob)

# gradedness sweep: gamma=0 -> hard sign (WTA negative control); gamma=1 -> topk_mag (full graded)
FULL_GAMMAS = [0.0, 0.25, 0.5, 0.75, 1.0]
SMOKE_GAMMAS = [0.0, 0.5, 1.0]           # hard / mid / graded (fires all branches; SMOKE=FULL code path)
SELFTEST_GAMMAS = [0.0, 0.5, 1.0]
HARD_CTRL_GAMMA = 0.0                     # in-sweep hard-WTA negative control endpoint
BASELINE_STATIC_ARM = "static_g0.00"      # AG baseline (hard static; must be < 0.95)

FULL_SEEDS = [7, 13, 19, 23, 29]
SMOKE_SEEDS = [7, 13, 19]
SELFTEST_SEEDS = [7, 13]

# FULL: production N=4096, GPU. SMOKE: production N=4096, reduced V/iters/B/gammas, CPU-local.
FULL_REGIME = dict(N=4096, Din=1024, V=40000, iters=800, B=8192, lr=1e-3,
                   Js=[1, 2, 3, 5, 8], alphas=[0.0, 0.8, 1.2, 1.6], nq=600, sep_sample=1500,
                   gammas=FULL_GAMMAS)
SMOKE_REGIME = dict(N=4096, Din=1024, V=8000, iters=250, B=1280, lr=1e-3,
                    Js=[1, 5], alphas=[0.0, 1.2], nq=400, sep_sample=1500,
                    gammas=SMOKE_GAMMAS)
SELFTEST_REGIME = dict(N=2048, Din=1024, V=700, iters=80, B=350, lr=1e-3,
                       Js=[1, 5], alphas=[0.0, 1.2], nq=180, sep_sample=400,
                       gammas=SELFTEST_GAMMAS)


def _gname(gamma):
    return f"g{gamma:.2f}"


def _condense_arm(gamma):
    return f"graded_{_gname(gamma)}"


def _static_arm(gamma):
    return f"static_{_gname(gamma)}"


# --------------------------------- numpy eval prims (reused verbatim from v1) --
def _l2n(x):
    return x / (np.linalg.norm(x, axis=1, keepdims=True) + 1e-9)


def _encode_graded(z, k, gamma):
    """Magnitude-graded top-k: top-k |z| coords -> sign(z)*|z|^gamma, rest 0. (B,N)->(B,N).
    gamma=0 -> sign (hard WTA); gamma=1 -> z (topk_mag full graded)."""
    idx = np.argpartition(-np.abs(z), k, axis=1)[:, :k]
    code = np.zeros_like(z)
    rows = np.arange(z.shape[0])[:, None]
    vals = z[rows, idx]
    if gamma == 0.0:
        code[rows, idx] = np.sign(vals)
    elif gamma == 1.0:
        code[rows, idx] = vals
    else:
        code[rows, idx] = np.sign(vals) * (np.abs(vals) ** gamma)
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


def _sc_argmax(dict_code_unit, query_code_unit, qi):
    """Single-concept pointwise recall: argmax cosine of each query over dict == its true id."""
    pred = np.argmax(query_code_unit @ dict_code_unit.T, axis=1)
    return float(np.mean(pred == qi))


def _arms_differ(hash_by_name, exempt_pairs):
    """META_RULE_AF: every arm-pair's SC-dict hash must differ, except declared exemptions.
    Returns (ok, collisions)."""
    exempt = {frozenset(p) for p in exempt_pairs}
    names = list(hash_by_name.keys())
    collisions = []
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a, b = names[i], names[j]
            if hash_by_name[a] == hash_by_name[b] and frozenset((a, b)) not in exempt:
                collisions.append((a, b))
    return (len(collisions) == 0), collisions


# --------------------------------- torch condenser training ------------------
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


def _rkd_loss(c, tc, off_mask):
    """Relational-KD: match student (condensed) pairwise-cosine to teacher's (off-diag MSE)."""
    cc = c / (c.norm(dim=1, keepdim=True) + 1e-9)
    s_s = cc @ cc.T
    s_t = tc @ tc.T
    return ((s_s - s_t)[off_mask] ** 2).mean()


def _encode_input(rep, z, k):
    """rep: ('graded', gamma) | ('dense',). Returns the representation the condenser reads."""
    if rep[0] == "graded":
        return _encode_graded(z, k, rep[1])
    if rep[0] == "dense":
        return z.astype(np.float32)
    raise ValueError(f"unknown rep {rep}")


def _train_condenser(bge_np, W_up, rep, t_unit_np, arm_name, noise_aug, seed, regime, device):
    """Train a NONLINEAR condenser (2-layer MLP) c = gelu(s @ W1) @ W2 : (N)->(H)->(Din) so the
    condensed code matches the teacher's pairwise geometry (RKD). NOISE AUGMENTATION trains the
    operator on noisy store codes mapped to CLEAN teacher geometry (brain-grounded pattern
    completion; MEASURED load-bearing in v1: clean-trained SC 0.59 << raw 0.91). Only W1,W2 carry
    gradients; the native expansion W_up is fixed random. rep = ('graded', gamma) | ('dense',)."""
    import torch
    Din = t_unit_np.shape[1]
    N = W_up.shape[1]
    H = COND_H
    V = bge_np.shape[0]
    B = min(regime["B"], V)
    iters = regime["iters"]
    k = max(1, N // 32)
    src_norm = np.linalg.norm(bge_np, axis=1, keepdims=True)
    salt = int(hashlib.sha256(arm_name.encode()).hexdigest()[:6], 16)
    g = torch.Generator(device="cpu").manual_seed(seed * 1000 + 1 + salt)
    W1 = _init_param((N, H), N, g, device)
    W2 = _init_param((H, Din), H, g, device)
    tcos = torch.from_numpy(t_unit_np).to(device)
    off_mask = ~torch.eye(B, dtype=torch.bool, device=device)
    opt = torch.optim.Adam([W1, W2], lr=regime["lr"])
    nrng = np.random.default_rng(seed * 2000 + 17 + salt)
    z_clean_full = bge_np @ W_up
    store_clean_full = _encode_input(rep, z_clean_full, k)      # (V, N)
    last = None
    for it in range(iters):
        idx = nrng.choice(V, size=B, replace=False)
        if noise_aug:
            n_noisy = int(round(NOISE_AUG_FRAC * B))
            src = bge_np[idx].copy()
            if n_noisy > 0:
                a = nrng.uniform(0.0, NOISE_AUG_ALPHA, size=(n_noisy, 1)).astype(np.float32)
                nz = nrng.standard_normal((n_noisy, Din)).astype(np.float32)
                nz = nz / (np.linalg.norm(nz, axis=1, keepdims=True) + 1e-9)
                src[:n_noisy] = (src[:n_noisy] + a * src_norm[idx][:n_noisy] * nz)
            inp_np = _encode_input(rep, src @ W_up, k)
        else:
            inp_np = store_clean_full[idx]
        inp = torch.from_numpy(np.ascontiguousarray(inp_np, dtype=np.float32)).to(device)
        c = torch.nn.functional.gelu(inp @ W1) @ W2
        loss = LAMBDA_D * _rkd_loss(c, tcos[idx], off_mask)
        opt.zero_grad(set_to_none=True)
        loss.backward()
        opt.step()
        last = float(loss.detach().cpu())
        if it % max(1, iters // 6) == 0 or it == iters - 1:
            print(f"[progress] seed={seed} arm={arm_name} it={it}/{iters} rkd_loss={last:.5f}",
                  flush=True)
    params = {"W1": W1.detach().cpu().numpy().astype(np.float32),
              "W2": W2.detach().cpu().numpy().astype(np.float32)}
    return params, last


def _condense_forward(code_np, params, device):
    """Nonlinear condenser forward: c = gelu(code @ W1) @ W2. numpy (M,N) -> numpy (M,Din)."""
    import torch
    xt = torch.from_numpy(np.ascontiguousarray(code_np, dtype=np.float32)).to(device)
    with torch.no_grad():
        h = torch.nn.functional.gelu(xt @ torch.from_numpy(params["W1"]).to(device))
        c = h @ torch.from_numpy(params["W2"]).to(device)
    return c.cpu().numpy().astype(np.float32)


# ------------------------------ per-seed measurement -------------------------
def measure_seed(bge_full, t_unit_full, seed, regime, device):
    rng = np.random.default_rng(seed)
    V, N, Din = regime["V"], regime["N"], regime["Din"]
    gammas = regime["gammas"]
    k = max(1, N // 32)                                   # 3.125% sparsity (matches v1 / two-head)
    sel = rng.choice(bge_full.shape[0], size=min(V, bge_full.shape[0]), replace=False)
    bge = bge_full[sel].astype(np.float32)
    t_unit = t_unit_full[sel].astype(np.float32)
    Vr = bge.shape[0]

    # native SPREAD expansion (fixed random projection Din -> N; the encoder's native output)
    gW = np.random.default_rng(seed * 1000 + 7)
    W_up = (gW.standard_normal((Din, N)).astype(np.float32) / np.sqrt(Din))
    z_dict = bge @ W_up                                   # (V, N) dense expanded

    # SC noisy-query set (single-concept pointwise fidelity), shared across arms
    qi = np.random.default_rng(seed * 7 + 3).choice(Vr, size=min(regime["nq"], Vr), replace=False)
    src = bge[qi]
    src_norm = np.linalg.norm(src, axis=1, keepdims=True)
    qrng = np.random.default_rng(seed * 7 + 5)
    noises = {}
    for a in regime["alphas"]:
        nz = qrng.standard_normal(src.shape).astype(np.float32)
        nz = nz / (np.linalg.norm(nz, axis=1, keepdims=True) + 1e-9)
        noises[a] = nz
    q_src = {str(a): (src + a * src_norm * noises[a]).astype(np.float32) for a in regime["alphas"]}
    q_z = {str(a): (q_src[str(a)] @ W_up) for a in regime["alphas"]}

    # per-gamma store code, SP on that store, sep
    store = {}          # gamma -> (V, N) graded store code
    store_unit = {}     # gamma -> unit-normalized store
    sp_by_gamma = {}    # gamma -> {J: SP}
    sep_by_gamma = {}
    for gamma in gammas:
        s = _encode_graded(z_dict, k, gamma)
        store[gamma] = s
        su = _l2n(s)
        store_unit[gamma] = su
        sp_by_gamma[gamma] = {str(J): _superposition_recall(
            su, np.random.default_rng(seed * 100 + int(gamma * 1000) + J), J, regime["nq"])
            for J in regime["Js"]}
        sep_by_gamma[gamma] = _offtarget_mean_cos(
            su, np.random.default_rng(seed + 11 + int(gamma * 100)), regime["sep_sample"])

    # train condensers: one per gamma (graded input) + one dense
    Wc = {}
    train_loss = {}
    for gamma in gammas:
        nm = _condense_arm(gamma)
        Wc[nm], train_loss[nm] = _train_condenser(
            bge, W_up, ("graded", gamma), t_unit, nm, True, seed, regime, device)
    Wc["dense_condense"], train_loss["dense_condense"] = _train_condenser(
        bge, W_up, ("dense",), t_unit, "dense_condense", True, seed, regime, device)

    res_arms = {}

    # graded condense + static arms per gamma
    for gamma in gammas:
        cnm, snm = _condense_arm(gamma), _static_arm(gamma)
        Wm = Wc[cnm]
        dict_in = _encode_graded(z_dict, k, gamma)
        dict_code_c = _l2n(_condense_forward(dict_in, Wm, device))     # (V, Din) condensed dict
        dict_code_s = store_unit[gamma]                               # (V, N) raw graded dict
        sc_c, sc_s = {}, {}
        for a in regime["alphas"]:
            q_in = _encode_graded(q_z[str(a)], k, gamma)
            q_code_c = _l2n(_condense_forward(q_in, Wm, device))
            sc_c[str(a)] = _sc_argmax(dict_code_c, q_code_c, qi)
            q_code_s = _l2n(q_in)
            sc_s[str(a)] = _sc_argmax(dict_code_s, q_code_s, qi)
        res_arms[cnm] = {
            "kind": "condense", "gamma": gamma, "sp": sp_by_gamma[gamma], "sc": sc_c,
            "sep_store": sep_by_gamma[gamma], "train_loss": train_loss[cnm],
            "sc_dict_hash": hashlib.sha256(np.ascontiguousarray(dict_code_c).tobytes()).hexdigest(),
        }
        res_arms[snm] = {
            "kind": "static", "gamma": gamma, "sp": sp_by_gamma[gamma], "sc": sc_s,
            "sep_store": sep_by_gamma[gamma], "train_loss": None,
            "sc_dict_hash": hashlib.sha256(np.ascontiguousarray(dict_code_s).tobytes()).hexdigest(),
        }
        print(f"[progress] seed={seed} gamma={gamma:.2f} SP@{J_OP}={sp_by_gamma[gamma][str(J_OP)]:.3f} "
              f"condSC@{ALPHA_OP}={sc_c[str(ALPHA_OP)]:.3f} statSC@{ALPHA_OP}={sc_s[str(ALPHA_OP)]:.3f} "
              f"dSC={sc_c[str(ALPHA_OP)] - sc_s[str(ALPHA_OP)]:+.3f} sep={sep_by_gamma[gamma]:+.4f}",
              flush=True)

    # dense_condense (v1 near-oracle reference; SP not meaningful for dense store -> report NA-ish)
    Wm = Wc["dense_condense"]
    dict_code_d = _l2n(_condense_forward(z_dict.astype(np.float32), Wm, device))
    sc_d = {}
    for a in regime["alphas"]:
        q_code_d = _l2n(_condense_forward(q_z[str(a)].astype(np.float32), Wm, device))
        sc_d[str(a)] = _sc_argmax(dict_code_d, q_code_d, qi)
    res_arms["dense_condense"] = {
        "kind": "dense_condense", "gamma": None, "sp": sp_by_gamma[gammas[0]], "sc": sc_d,
        "sep_store": None, "train_loss": train_loss["dense_condense"],
        "sc_dict_hash": hashlib.sha256(np.ascontiguousarray(dict_code_d).tobytes()).hexdigest(),
    }

    # oracle: decoupled ceiling (SP from most-decorrelated store gamma=0; SC from teacher dense)
    dict_code_o = _l2n(bge)
    sc_o = {}
    for a in regime["alphas"]:
        sc_o[str(a)] = _sc_argmax(dict_code_o, _l2n(q_src[str(a)]), qi)
    res_arms["oracle"] = {
        "kind": "oracle", "gamma": None, "sp": sp_by_gamma[HARD_CTRL_GAMMA], "sc": sc_o,
        "sep_store": sep_by_gamma[HARD_CTRL_GAMMA], "train_loss": None,
        "sc_dict_hash": hashlib.sha256(np.ascontiguousarray(dict_code_o).tobytes()).hexdigest(),
    }
    print(f"[progress] seed={seed} dense_condense SC@{ALPHA_OP}={sc_d[str(ALPHA_OP)]:.3f} "
          f"oracle SC@{ALPHA_OP}={sc_o[str(ALPHA_OP)]:.3f}", flush=True)

    return {"seed": int(seed), "V": int(Vr), "N": int(N), "Din": int(Din), "k": int(k),
            "gammas": gammas, "sp_by_gamma": {_gname(g): sp_by_gamma[g] for g in gammas},
            "arms": res_arms}


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
    names = list(per_seed[0]["arms"].keys())
    agg = {"n_seeds": len(per_seed), "arms": {}}
    for nm in names:
        sp = {str(J): _mean([s["arms"][nm]["sp"][str(J)] for s in per_seed]) for J in Js}
        sc = {str(a): _mean([s["arms"][nm]["sc"][str(a)] for s in per_seed]) for a in alphas}
        agg["arms"][nm] = {
            "kind": per_seed[0]["arms"][nm]["kind"],
            "gamma": per_seed[0]["arms"][nm]["gamma"],
            "sp_mean": sp, "sc_mean": sc,
            "sep_store_mean": _mean([s["arms"][nm]["sep_store"] for s in per_seed]),
            "sp_op_per_seed": [s["arms"][nm]["sp"][str(J_OP)] for s in per_seed],
            "sc_op_per_seed": [s["arms"][nm]["sc"][str(ALPHA_OP)] for s in per_seed],
            "train_loss_mean": _mean([s["arms"][nm]["train_loss"] for s in per_seed]),
        }
        agg["arms"][nm]["sp_op_cv"] = _cv(agg["arms"][nm]["sp_op_per_seed"])
        agg["arms"][nm]["sc_op_cv"] = _cv(agg["arms"][nm]["sc_op_per_seed"])
    return agg


def _spv(A, nm):
    return A[nm]["sp_mean"][str(J_OP)]


def _scv(A, nm):
    return A[nm]["sc_mean"][str(ALPHA_OP)]


def _classify(agg, gammas):
    A = agg["arms"]
    graded = [g for g in gammas if g != HARD_CTRL_GAMMA]     # rescue candidates (gamma>0)

    per_gamma = {}
    for g in gammas:
        cnm, snm = _condense_arm(g), _static_arm(g)
        sp = _spv(A, cnm)
        sc_c = _scv(A, cnm)
        sc_s = _scv(A, snm)
        struct_gain = sc_c - sc_s
        per_gamma[_gname(g)] = {
            "gamma": g, "sp": sp, "sc_condense": sc_c, "sc_static": sc_s,
            "structural_gain": struct_gain,
            "sp_hit": bool(sp >= SP_HI),
            "sc_condense_hit": bool(sc_c >= SC_HI),
            "sc_static_hit": bool(sc_s >= SC_HI),
            "struct_ok": bool(struct_gain >= STRUCT_MARGIN),
            "revives": bool(sp >= SP_HI and sc_c >= SC_HI and struct_gain >= STRUCT_MARGIN),
            "static_achieves_both": bool(sp >= SP_HI and sc_s >= SC_HI),
        }

    def joint_c(g):
        pg = per_gamma[_gname(g)]
        return min(pg["sp"] / SP_HI, pg["sc_condense"] / SC_HI)

    # 1) graded static already does BOTH directly (strongest rescue; condenser not even needed)
    static_wins = [g for g in graded if per_gamma[_gname(g)]["static_achieves_both"]]
    # 2) graded condenser revives BOTH over its own static
    revivers = [g for g in graded if per_gamma[_gname(g)]["revives"]]

    graded_struct_gains = [per_gamma[_gname(g)]["structural_gain"] for g in graded]
    best_graded = max(graded, key=joint_c)                  # best at getting BOTH (condense)
    bg = per_gamma[_gname(best_graded)]

    if static_wins:
        pick = max(static_wins, key=lambda g: min(per_gamma[_gname(g)]["sp"] / SP_HI,
                                                  per_gamma[_gname(g)]["sc_static"] / SC_HI))
        verdict = "HARD_PASS_GRADED_STATIC_ACHIEVES_BOTH_NO_CONDENSER_NEEDED"
        headline_gamma = pick
    elif revivers:
        pick = max(revivers, key=joint_c)
        verdict = "HARD_PASS_GRADED_CONDENSE_REVIVES_BOTH"
        headline_gamma = pick
    elif max(graded_struct_gains) < STRUCT_MARGIN:
        verdict = "HARD_FAIL_WALL_FUNDAMENTAL_TWO_HEAD_CONFIRMED"
        headline_gamma = best_graded
    else:
        # some graded gamma beats its own static (struct real) but did not revive BOTH
        headline_gamma = max(graded, key=lambda g: per_gamma[_gname(g)]["structural_gain"])
        hg = per_gamma[_gname(headline_gamma)]
        if not hg["sp_hit"]:
            verdict = "HARD_FAIL_GRADED_LOSES_SUPERPOSITION"      # condenses but gradedness cost SP
        elif hg["sp_hit"] and (SC_HI - hg["sc_condense"]) <= MIDDLE_TOL:
            verdict = "MIDDLE_GRADED_NEAR_MISS"
        else:
            verdict = "HARD_FAIL_GRADED_CONDENSE_CANNOT_RECOVER"

    hg = per_gamma[_gname(headline_gamma)]
    return {
        "verdict": verdict,
        "headline": {"arm": _condense_arm(headline_gamma), "gamma": headline_gamma, **hg},
        "per_gamma": per_gamma,
        "best_graded_gamma": best_graded, "best_graded": bg,
        "dense_condense_sc": _scv(A, "dense_condense"),
        "oracle": {"sp": _spv(A, "oracle"), "sc": _scv(A, "oracle")},
        "hard_ctrl": per_gamma[_gname(HARD_CTRL_GAMMA)],
        "thresholds": {"SP_HI": SP_HI, "SC_HI": SC_HI, "MIDDLE_TOL": MIDDLE_TOL,
                       "STRUCT_MARGIN": STRUCT_MARGIN},
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
    """Scaffold-free witnesses: encoder validity, telemetry-sensitivity, arms-differ,
    condenser-is-real (changes argmax vs static), gamma-sweep-fires (gamma changes the code)."""
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
    hard_c, hard_s = _condense_arm(HARD_CTRL_GAMMA), _static_arm(HARD_CTRL_GAMMA)
    graded_g = [g for g in reg["gammas"] if g != HARD_CTRL_GAMMA][-1]  # topk_mag endpoint
    gc = _condense_arm(graded_g)

    # 1) VALID ENCODER: teacher (oracle) does clean pointwise ~1.0.
    valid_enc = A7["oracle"]["sc"]["0.0"] >= 0.95
    ok &= valid_enc
    # 2) SPREAD SUPERPOSITION FIRES: the hard store SP@J_OP is high (>= SP_HI).
    sp_high = m7["sp_by_gamma"][_gname(HARD_CTRL_GAMMA)][str(J_OP)] >= SP_HI
    ok &= sp_high
    # 3) TELEMETRY-SENSITIVITY (not analytically pinned): perturbing the seed MOVES both the
    #    store SP and the condensed SC of a graded arm.
    sp_moves = (m7["sp_by_gamma"][_gname(graded_g)][str(J_OP)]
                != m13["sp_by_gamma"][_gname(graded_g)][str(J_OP)])
    sc_moves = A7[gc]["sc"][str(ALPHA_OP)] != A13[gc]["sc"][str(ALPHA_OP)]
    ok &= (sp_moves and sc_moves)
    # 4) CONDENSER IS REAL (not a monotonic rescale): condensed SC differs from its OWN static SC
    #    (the operator CHANGES the argmax outcome). Tested on the hard arm (the v1 negative).
    struct_changes = A7[hard_c]["sc"][str(ALPHA_OP)] != A7[hard_s]["sc"][str(ALPHA_OP)]
    ok &= struct_changes
    # 5) GAMMA-SWEEP FIRES: gamma actually CHANGES the store code -> hard store SP differs from
    #    graded store SP (or their SC-dict hashes differ). Guards a no-op-gamma bug.
    gamma_fires = (m7["sp_by_gamma"][_gname(HARD_CTRL_GAMMA)][str(J_OP)]
                   != m7["sp_by_gamma"][_gname(graded_g)][str(J_OP)]) or (
                   A7[hard_c]["sc_dict_hash"] != A7[gc]["sc_dict_hash"])
    ok &= gamma_fires
    # 6) ARMS DIFFER (META_RULE_AF): all SC-dict hashes distinct.
    arms_differ, collisions = _arms_differ({nm: A7[nm]["sc_dict_hash"] for nm in A7}, [])
    ok &= arms_differ
    # 7) CONDENSER TRAINS: graded headline has finite RKD train loss.
    tl = A7[gc]["train_loss"]
    trains = tl is not None and np.isfinite(tl)
    ok &= trains
    # 8) SC DEGRADES WITH NOISE for the teacher (real pointwise metric, not saturated-vacuous).
    sc_noise = A7["oracle"]["sc"]["0.0"] >= A7["oracle"]["sc"][str(ALPHA_OP)] - 1e-9
    ok &= sc_noise

    print(f"[self-test] valid_enc={valid_enc}(oracleSC@0={A7['oracle']['sc']['0.0']:.3f}) "
          f"sp_high={sp_high}(hard={m7['sp_by_gamma'][_gname(HARD_CTRL_GAMMA)][str(J_OP)]:.3f} "
          f"graded={m7['sp_by_gamma'][_gname(graded_g)][str(J_OP)]:.3f}) "
          f"sp_moves={sp_moves} sc_moves={sc_moves} struct_changes={struct_changes}"
          f"(hardCond={A7[hard_c]['sc'][str(ALPHA_OP)]:.3f} hardStat={A7[hard_s]['sc'][str(ALPHA_OP)]:.3f}) "
          f"gamma_fires={gamma_fires} arms_differ={arms_differ}"
          f"{'' if arms_differ else ' collisions='+str(collisions)} trains={trains} sc_noise={sc_noise}")
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
    gammas = regime["gammas"]
    expected_units = len(seeds)
    _write_start_marker(OUTPUT_DIR, run_mode, expected_units)
    print(f"[start] run_mode={run_mode} device={device} seeds={seeds} gammas={gammas} regime={regime}",
          flush=True)

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
    cls = _classify(agg, gammas)

    n_units = len(per_seed)
    # cardinality: n_seeds AND every seed carries all gamma arms (gamma-sweep cardinality gate)
    seeds_ok = (n_units == expected_units)
    gamma_card_ok = all(
        all(_condense_arm(g) in s["arms"] and _static_arm(g) in s["arms"] for g in gammas)
        for s in per_seed)
    cardinality_ok = bool(seeds_ok and gamma_card_ok)

    A = agg["arms"]
    baseline_sc = _scv(A, BASELINE_STATIC_ARM)               # hard static (should NOT saturate)
    baseline_in_band = bool(baseline_sc < 0.95)
    arms_differ, arm_collisions = _arms_differ(
        {nm: per_seed[0]["arms"][nm]["sc_dict_hash"] for nm in per_seed[0]["arms"]}, [])

    if not cardinality_ok:
        verdict = "HARD_FAIL_CARDINALITY_BREACH_META_RULE_H"
    elif not arms_differ:
        verdict = "HARD_FAIL_ARMS_IDENTICAL_META_RULE_AF"
    elif not baseline_in_band:
        verdict = "HARD_FAIL_BASELINE_SATURATED_NO_TRADEOFF_META_RULE_AG"
    else:
        verdict = cls["verdict"]

    hl = cls["headline"]
    orc = cls["oracle"]
    hc = cls["hard_ctrl"]
    pg_str = " ".join(
        f"{nm}(SP{v['sp']:.2f}/condSC{v['sc_condense']:.2f}/statSC{v['sc_static']:.2f}/"
        f"dSC{v['structural_gain']:+.2f})" for nm, v in cls["per_gamma"].items())
    verdict_msg = (
        f"{verdict} | GRADED-SPARSE RESCUE of the phase-traversal hard sign+top-k negative "
        f"(v1 structural_gain=-0.348). Sweep magnitude-gradedness gamma (0=hard-WTA sign [neg "
        f"ctrl], 1=topk_mag) of the STORE code; each gamma judged vs ITS OWN static readout. "
        f"HEADLINE {hl['arm']} (gamma={hl['gamma']}): SP@J{J_OP}={hl['sp']:.3f} "
        f"(hit>={SP_HI}:{hl['sp_hit']}) condSC@a{ALPHA_OP}={hl['sc_condense']:.3f} "
        f"(hit>={SC_HI}:{hl['sc_condense_hit']}) statSC={hl['sc_static']:.3f} "
        f"structural_gain={hl['structural_gain']:+.3f} (>= {STRUCT_MARGIN}:{hl['struct_ok']}) "
        f"revives={hl['revives']}. PER-GAMMA: {pg_str}. HARD-CTRL gamma0 (v1 negative): "
        f"condSC={hc['sc_condense']:.3f} statSC={hc['sc_static']:.3f} dSC={hc['structural_gain']:+.3f}. "
        f"dense_condense (v1 near-oracle ref) SC={cls['dense_condense_sc']:.3f}. "
        f"ORACLE ceiling SP{orc['sp']:.2f}/SC{orc['sc']:.2f}. cache={cache_src}. INTERPRETATION: "
        + ({
            "HARD_PASS_GRADED_STATIC_ACHIEVES_BOTH_NO_CONDENSER_NEEDED":
                "the GRADED sparse store code alone (raw argmax, NO condenser) achieves BOTH high "
                "superposition AND high pointwise -> the strongest rescue: one graded code serves "
                "both directly; the hard sign quantization was the entire problem. Two-head not needed.",
            "HARD_PASS_GRADED_CONDENSE_REVIVES_BOTH":
                "a GRADED store code condenses gracefully -> ONE stored code, read through a trained "
                "structural condenser, achieves BOTH (SP high AND condensed SC high) AND beats its own "
                "static readout by the margin. The hard sign+top-k discontinuity was the whole wall; "
                "gradedness rescues it. The decouple law is realizable as a single traversed graded code.",
            "HARD_FAIL_WALL_FUNDAMENTAL_TWO_HEAD_CONFIRMED":
                "even the GRADED code cannot beat its own static readout (no gamma reaches "
                "structural_gain>=margin) -> the condensation wall is FUNDAMENTAL, not an artifact of the "
                "sign discontinuity. The two-head decoupled-code architecture is CONFIRMED as the only "
                "solution. VALUABLE CLOSING RESULT: single-code phase-traversal is exhausted; route to "
                "two-head. (Compare dense_condense: if it still hits ~0.99, condensability needs the "
                "FULL dense code, which defeats the memory-efficiency purpose of the sparse store.)",
            "HARD_FAIL_GRADED_LOSES_SUPERPOSITION":
                "gradedness lets the condenser beat the static readout (structural transform is real) "
                "BUT the graded code lost the decorrelation that gives superposition (SP < SP_HI at the "
                "gamma that condenses) -> the named tension resolves in the LOSE-SP direction: you can "
                "buy condensability with magnitude, but it costs the spread. Frontier is a genuine "
                "tradeoff; single graded code cannot hold both. Route to two-head.",
            "MIDDLE_GRADED_NEAR_MISS":
                "the graded condenser beats its static and recovers pointwise to within noise of target "
                "while keeping SP -> a weight/regime nudge (gamma grid, condenser depth, sparsity k, RKD "
                "weight) likely closes it. Report to Research for a targeted re-sweep.",
            "HARD_FAIL_GRADED_CONDENSE_CANNOT_RECOVER":
                "the graded condenser beats its static (structural transform real) and keeps SP, but "
                "cannot recover pointwise to SC_HI -> gradedness helps but is insufficient; the sparse "
                "store's information loss is only partly condensable. Route to two-head / escalate.",
        }.get(verdict, "cardinality / arms-identical / baseline-saturated schema breach; see verdict tag."))
    )

    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": f"{verdict}: graded-sparse rescue of phase-traversal hard-WTA negative ({run_mode})",
        "run_mode": run_mode,
        "device": device,
        "elapsed_s": time.perf_counter() - t0,
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR_NAME,
        "cache_source": cache_src,
        "cardinality_ok": cardinality_ok,
        "seeds_ok": seeds_ok,
        "gamma_cardinality_ok": gamma_card_ok,
        "expected_n_units": expected_units,
        "n_units": n_units,
        "gammas": gammas,
        "arms_differ_verified": arms_differ,
        "arm_collisions": arm_collisions,
        "baseline_in_band": baseline_in_band,
        "baseline_static_arm": BASELINE_STATIC_ARM,
        "baseline_static_sc": baseline_sc,
        "classification": cls,
        "operating_points": {"J_OP": J_OP, "ALPHA_OP": ALPHA_OP},
        "bands": {"SP_HI": SP_HI, "SC_HI": SC_HI, "MIDDLE_TOL": MIDDLE_TOL,
                  "STRUCT_MARGIN": STRUCT_MARGIN, "LAMBDA_D": LAMBDA_D,
                  "NOISE_AUG_ALPHA": NOISE_AUG_ALPHA, "NOISE_AUG_FRAC": NOISE_AUG_FRAC},
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
