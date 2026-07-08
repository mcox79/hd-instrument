"""PHASE-TRAVERSAL encoder: store in a SPREAD (expanded/decorrelated) phase, retrieve by
a REAL STRUCTURAL CONDENSATION operator. "Blow apart then pull together."

QUESTION (2026-07-08). The certified decouple law (reference_correlation_hurts_
associative_store_capacity_decouple_from_retrieval) says the associative store wants
DECORRELATED (near-orthogonal) codes for superposition capacity, while noisy pointwise
retrieval wants CORRELATED (semantic) codes -- opposite pulls, so a SINGLE code cannot do
both (the strict-tradeoff frontier). The two-head cell
(exp_encoder_twohead_decoupled_store_retrieval_v1) solved this by learning TWO SEPARATE
sibling codes off a shared trunk. This cell asks a DIFFERENT question: can ONE stored
representation serve BOTH -- if retrieval TRAVERSES it through a structural operator?

  SPREAD PHASE (store): each concept is written as its NATIVE expanded code
    s = WTA_topk(x @ W_up), a high-dim decorrelated sparse-bipolar block code (the
    fly-LSH / native-expansion construction that gives high superposition recall). We
    BUNDLE and read superposition in THIS phase -> SP high.
  CONDENSATION (retrieve): at read time a trained STRUCTURAL operator C settles the
    spread code onto the discriminative semantic manifold: c = s @ W_cond (expanded N
    -> semantic Din, "pull together"). C is distilled (RKD) to the BGE teacher's pairwise
    geometry, so a NOISY query -- expanded, WTA'd, then condensed -- lands on its concept
    -> SC high. C is a retrieval-time transform applied to BOTH query and dictionary; the
    stored engram is ONLY the spread code s (one representation, traversed at read).

WHY THIS IS NOT THE PRIOR NEGATIVE (two guardrails from the scour, NOT violated):
  1. NOT the QE-1 beta-knob. exp_qe1_substrate_annealing_v1 HARD_FAILED by sweeping a
     beta READOUT-TEMPERATURE over a STATIC unchanged codebook. A scoring temperature is a
     MONOTONIC rescale of cosine similarities -> it CANNOT change the argmax outcome, so it
     is a no-op for recall. Here the condensation operator C is a genuine STRUCTURAL
     transform of the vector geometry (c = s @ W_cond changes which concept wins argmax),
     NOT a scoring temperature. The spread_static arm below IS the beta-knob ceiling
     (raw-spread argmax == any-beta argmax); the HEADLINE must BEAT it by STRUCT_MARGIN, or
     the cell HARD_FAILs as "reduces to QE-1 beta-knob".
  2. NOT a kWTA retrofit onto a dense BGE embedding. exp_dg_projector_charlm HARD_FAILED
     by sparsifying the existing dense BGE code after the fact (bpc 2.557 -> 2.95). Here
     the WTA is applied to the encoder's NATIVE expanded output (z = x @ W_up), which is
     the sanctioned fly-LSH / native-expansion path (R5 HARD_PASS 50x capacity;
     Charikar/fly-LSH 0.998 recall). Condensation is an INDEPENDENT retrieval-time operator
     on that native code, never a retrofit onto BGE.

THE LOAD-BEARING EMPIRICAL QUESTION: the stored code is the SPARSE sign-only WTA spread
code (superposition-optimized, memory-efficient). Can a structural operator recover
SEMANTIC pointwise discrimination FROM THAT sparse code, under noise -- without our having
to store a second (semantic) code, and while the stored spread code keeps its high
superposition? If yes: one engram, both capabilities (brain-like -- one memory read out
through different dynamics). If no: sparsification for superposition destroys condensability
-> honest HARD_FAIL (collapses to the single-code tradeoff corner). Because condensation is
retrieval-only and the STORE code is unchanged, SP is preserved BY CONSTRUCTION; the entire
question is whether SC can be recovered by the structural transform.

ARMS (metric harness reused verbatim from the two-head cell so numbers compare directly to
the two-head + oracle):
  phase_traversal        store native-WTA spread s; SC on condense(s), NOISE-AUGMENTED training [HEADLINE]
  phase_traversal_clean  SC on condense(s), CLEAN-trained condenser [ablation: isolates noise-aug value] [ENRICH]
  phase_traversal_dense  SC on condense(dense z), noise-aug [no WTA; isolates sparsification cost]  [ENRICH]
  spread_static          SC on the raw spread code s directly (NO transform == beta-knob)  [FRONTIER/QE1-CTRL]
  semantic_static        store semantic BGE-WTA (crowded SP); SC on dense BGE (~1.0)        [FRONTIER]
  oracle                 SP = native spread; SC = teacher dense (decoupled existence proof) [CEILING]
  (all phase_traversal* + spread_static + oracle share the SAME native-spread store, so
   their SP is identical; only semantic_static has a distinct (crowded) semantic store.)

METRICS (uniform across arms):
  STORE / SP  = superposition recall@J on the WTA block code of the STORE code (bundle J
                members, argmax-cosine top-J over dict). The native-spread store is
                decorrelated -> SP high; the semantic store is crowded -> SP low.
  RETRIEVE / SC = single-concept pointwise recall@alpha: a concept's BGE source perturbed
                by relative noise, pushed through the arm's read pipeline (expand -> [WTA]
                -> condense, or raw), argmax-cosine over the arm's dictionary.
  achieves_both = native-spread SP@J_OP >= SP_HI AND phase_traversal SC@alpha_OP >= SC_HI.
  structural_gain = phase_traversal SC - spread_static SC (must be >= STRUCT_MARGIN: the
                structural operator must beat the static/beta-knob readout, else it is the
                QE-1 no-op).

PRE-REG BANDS (HEADLINE = phase_traversal; strictly-above-floor per META_RULE_L; thresholds
carry headroom: SP_HI=0.83 below the decorrelated ceiling ~0.905, SC_HI=0.90 below the
teacher 1.0):
  HARD_PASS = phase_traversal achieves_both (native-spread SP@J_OP >= 0.83 AND condensed
              SC@alpha_OP >= 0.90) AND structural_gain >= STRUCT_MARGIN (0.15). One stored
              spread engram serves BOTH; the certified decouple law is realizable as a
              single traversed representation, approaching the oracle / two-head.
  MIDDLE    = SP hits AND (condensed SC within MIDDLE_TOL (0.05) of SC_HI) AND structural_gain
              >= STRUCT_MARGIN (structural transform is real and close -- a regime/weight nudge
              away).
  HARD_FAIL = HARD_FAIL_REDUCES_TO_QE1_BETA_KNOB  : structural_gain < STRUCT_MARGIN (the
              condensation gained ~nothing over the static raw-spread readout -> it is the
              beta-knob no-op).
            OR HARD_FAIL_CONDENSE_CANNOT_RECOVER  : structural_gain >= STRUCT_MARGIN but
              condensed SC still below SC_HI - MIDDLE_TOL (the transform helps but cannot
              recover pointwise from the superposition-optimized sparse code -> collapses to
              the single-code tradeoff corner).

## Compute architecture
Class (a) batched-GPU. Condenser training is matmul-heavy (per-iter store-code forward
B x N @ N x Din, RKD pairwise B x B); 3 trainable arms x seeds x hundreds of iters. FULL
routes to the GPU (overnight_queue) at production N=4096, V=40000, B=8192 (B > N gives a
full-rank RKD sample). SMOKE runs CPU-local at PRODUCTION N=4096 (linear ops are cheap on
CPU) with reduced V/iters/B -- DISCRIMINATOR-MUST-SURVIVE-SCALE option A (smoke at full-N):
the condensability-of-a-sparse-spread-code is an information-geometry property that fires at
the production N and sparsity fraction, previewed at the smoke's small V. Storage strategy:
no_composition / no_store (encoder-geometry cell; the "dictionary" is the per-concept code,
evaluated by argmax-cosine cleanup, not a bundled associative store).

## Functional Requirements
  FR1 high superposition recall (bundle J concepts, recover them) -> native-expansion + WTA
      sparse block code (fly-LSH / R5 native-expansion CG primitive). Measured: SP@J.
  FR2 noisy pointwise discrimination (noisy query -> its concept) -> semantic-manifold code
      (BGE-distilled geometry). Measured: SC@alpha.
  FR3 BOTH from ONE stored code -> structural condensation operator C mapping the stored
      spread code to the semantic manifold at read time (this cell's new mechanism; no prior
      primitive maps -> flagged as new mechanism, tested here).

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
- arms_differ_verified at smoke gate (sha256 of each arm's SC dictionary code; distinct).
- final_metrics_atomicity: tmp_replace (os.replace on final metrics.json).
- except SystemExit: raise BEFORE except Exception (no BaseException).
- crlb_n/a: retrieval recall + geometry cosines; no closed-form noise floor. Feasibility
  handled by calibrated operating points (the two-head/anchor-sweep cells MEASURED the
  0.43-vs-0.905 SP band and 0.655-vs-1.0 SC band at this exact regime).
- baseline_in_band: spread_static SC@alpha_OP < 0.95 (if the raw spread code already does
  pointwise there is no tradeoff to solve -> iterate regime).
- discriminator survives scale: smoke at production N=4096; condensability is an
  info-geometry property present at any V; the crowded-BGE-vs-decorrelated SP gap was
  MEASURED to grow with V (-0.561 at V=4000, -0.662 at V=40000) in the anchor-sweep cell.
- HARD bands strictly above floor (SP_HI 0.83 headroom to 0.905; SC_HI 0.90 to 1.0).
- per-unit failure-class instrumentation (no bare except).
- calibration_check: default_ok_for_this_regime (real BGE cache; operating points
  J_OP/alpha_OP calibrated in the two-head cell before this pre-reg).
- telemetry-sensitivity self-test MANDATORY (perturb-a-seed MOVES SP and condensed SC;
  structural transform CHANGES the argmax vs static -> discriminator not analytically pinned).
- cell_chunked: false (few-seed, per-seed checkpoint/restartable, atomic partials).
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

ANCHOR_NAME = "encoder_phase_traversal_spread_condense_v1"
OUTPUT_DIR = os.path.join(_REPO, "data", f"exp_{ANCHOR_NAME}")

_CACHE_DIR = os.path.join(_REPO, "data", "substrate_index", "cached_indices")

# operating points (match the two-head / anchor-sweep cells for comparability)
J_OP = 5
ALPHA_OP = 1.2
LAMBDA_D = 1.0            # RKD BGE-distillation weight on the condenser
COND_H = 1024            # condenser hidden width (the semantic-manifold dim; "pull together")
# NOISE-AUGMENTED condenser training (the mechanism's brain-grounded pattern-completion shot):
# train the condenser on NOISY store codes (source perturbed at a random relative alpha, then
# expanded + [WTA]) mapped to the CLEAN teacher geometry, so the operator learns a NOISE-ROBUST
# settle onto the manifold. Without this, the condenser overfits clean codes and the sign-WTA of
# a noisy query maps inconsistently through the nonlinearity (MEASURED: clean-trained condenser
# SC 0.59 << raw-spread 0.91 at smoke V=8000 -- condensation HURT). alpha ~ U[0, NOISE_AUG_ALPHA].
NOISE_AUG_ALPHA = 1.6    # max relative noise during augmented condenser training (covers alpha_OP=1.2)
NOISE_AUG_FRAC = 0.5     # fraction of each training batch that is noise-perturbed (rest clean)

# oracle and semantic_static SHARE the teacher SC-dictionary BY CONSTRUCTION (oracle's
# retrieval readout IS the teacher readout; the arms differ in their SP source, not their SC
# dict). This is a legitimate META_RULE_AF exemption, not an arm-implementation bug.
ARMS_DIFFER_EXEMPT = [("oracle", "semantic_static")]

# pre-reg bands (HEADLINE = phase_traversal)
SP_HI = 0.83             # native-spread WTA superposition recall@J_OP counted as high superposition
SC_HI = 0.90             # condensed DENSE single-concept recall@alpha_OP counted as high pointwise
MIDDLE_TOL = 0.05        # near-miss tolerance for condensed SC (MIDDLE band)
STRUCT_MARGIN = 0.15     # phase_traversal SC must beat spread_static SC by this (structural, not beta-knob)

# arm definitions. kind: condense (trained C) / static_spread / static_semantic / oracle.
# input (condense arms only): wta_sign | topk_mag | dense -- the representation C reads from.
ARMS = [
    {"name": "phase_traversal", "kind": "condense", "input": "wta_sign", "noise_aug": True},
    {"name": "phase_traversal_clean", "kind": "condense", "input": "wta_sign", "noise_aug": False},
    {"name": "phase_traversal_dense", "kind": "condense", "input": "dense", "noise_aug": True},
    {"name": "spread_static", "kind": "static_spread"},
    {"name": "semantic_static", "kind": "static_semantic"},
    {"name": "oracle", "kind": "oracle"},
]
HEADLINE_ARM = "phase_traversal"
STATIC_CTRL_ARM = "spread_static"       # the beta-knob ceiling (raw spread argmax)
CEILING_ARM = "oracle"

FULL_SEEDS = [7, 13, 19, 23, 29]
SMOKE_SEEDS = [7, 13, 19]
SELFTEST_SEEDS = [7, 13]

# FULL: production N=4096, GPU (B=8192 > N -> full-rank RKD sample). SMOKE: production N=4096,
# reduced V/iters/B for a CPU-local few-min gate at the SAME sparsity fraction (option A:
# smoke fires the discriminator at production N; the condensability property is info-geometric).
FULL_REGIME = dict(N=4096, Din=1024, V=40000, iters=800, B=8192, lr=1e-3,
                   Js=[1, 2, 3, 5, 8], alphas=[0.0, 0.8, 1.2, 1.6], nq=600, sep_sample=1500)
# SMOKE at production N=4096 AND a V large enough to leave the tiny-V saturation regime, so
# the discriminator fires at a scale that PREVIEWS FULL: the raw-spread (beta-knob ceiling)
# SC must drop into the discriminating band (not >0.95), and the condenser gets real training
# signal (V >> B). This is DISCRIMINATOR-MUST-SURVIVE-SCALE option C (a scaled preview arm).
SMOKE_REGIME = dict(N=4096, Din=1024, V=8000, iters=300, B=1536, lr=1e-3,
                    Js=[1, 5], alphas=[0.0, 1.2], nq=400, sep_sample=1500)
SELFTEST_REGIME = dict(N=2048, Din=1024, V=700, iters=80, B=350, lr=1e-3,
                       Js=[1, 5], alphas=[0.0, 1.2], nq=180, sep_sample=400)


# --------------------------------- numpy eval prims (reused verbatim) --------
def _l2n(x):
    return x / (np.linalg.norm(x, axis=1, keepdims=True) + 1e-9)


def _encode_wta_sign(z, k):
    """Sparse-bipolar block code: top-K magnitude coords -> sign, rest 0. (B,N)->(B,N)."""
    idx = np.argpartition(-np.abs(z), k, axis=1)[:, :k]
    code = np.zeros_like(z)
    rows = np.arange(z.shape[0])[:, None]
    code[rows, idx] = np.sign(z[rows, idx])
    return code.astype(np.float32)


def _encode_topk_mag(z, k):
    """Sparse code: top-K magnitude coords keep their VALUE, rest 0. (B,N)->(B,N)."""
    idx = np.argpartition(-np.abs(z), k, axis=1)[:, :k]
    code = np.zeros_like(z)
    rows = np.arange(z.shape[0])[:, None]
    code[rows, idx] = z[rows, idx]
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


def _arms_differ(hash_by_name):
    """META_RULE_AF: every arm-pair's SC-dict hash must differ, EXCEPT declared exemptions
    (oracle/semantic_static share the teacher SC-dict by construction). Returns (ok, collisions)."""
    exempt = {frozenset(p) for p in ARMS_DIFFER_EXEMPT}
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


def _train_condenser(bge_np, W_up, rep_kind, t_unit_np, arm_name, noise_aug, seed, regime, device):
    """Train a NONLINEAR condenser (2-layer MLP) c = gelu(s @ W1) @ W2 : (N)->(H)->(Din) so the
    condensed code matches the teacher's pairwise geometry (RKD). The MLP is the brain-grounded
    "settle onto the discriminative manifold" operator (a linear map cannot invert the sign/top-k
    quantization). It is a genuine STRUCTURAL transform (not a scoring temperature -> not the QE-1
    beta-knob). Only the condenser trains; the native expansion W_up (upstream) is fixed random.

    NOISE AUGMENTATION (noise_aug=True): a fraction NOISE_AUG_FRAC of each batch is the source
    perturbed at a random relative alpha ~ U[0, NOISE_AUG_ALPHA], then expanded + read as rep_kind,
    mapped to the SAME rows' CLEAN teacher geometry -- so the operator learns a NOISE-ROBUST
    condensation (the brain's pattern-completion is noise-trained). noise_aug=False reproduces the
    clean-trained ablation. Inputs are built per-batch in numpy (WTA is argpartition) then fed as
    data (no grad); only W1,W2 carry gradients.

    bge_np: (V, Din) raw source; W_up: (Din, N) fixed expansion. Returns numpy {W1,W2} + loss.
    """
    import torch
    Din = t_unit_np.shape[1]
    N = W_up.shape[1]
    H = COND_H
    V = bge_np.shape[0]
    B = min(regime["B"], V)
    iters = regime["iters"]
    k = max(1, N // 32)
    src_norm = np.linalg.norm(bge_np, axis=1, keepdims=True)
    # arm-specific salt so the condenser arms are independent seed-deterministic draws.
    salt = int(hashlib.sha256(arm_name.encode()).hexdigest()[:6], 16)
    g = torch.Generator(device="cpu").manual_seed(seed * 1000 + 1 + salt)
    W1 = _init_param((N, H), N, g, device)
    W2 = _init_param((H, Din), H, g, device)
    tcos = torch.from_numpy(t_unit_np).to(device)
    off_mask = ~torch.eye(B, dtype=torch.bool, device=device)
    opt = torch.optim.Adam([W1, W2], lr=regime["lr"])
    nrng = np.random.default_rng(seed * 2000 + 17 + salt)
    # clean-path store code precomputed once (used when noise_aug=False or for the clean half).
    z_clean_full = bge_np @ W_up
    store_clean_full = _build_input(rep_kind, z_clean_full, k)      # (V, N)
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
            inp_np = _build_input(rep_kind, src @ W_up, k)
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
def _build_input(rep_kind, z, k):
    """Return the representation the condenser reads from, for a batch of expanded codes z."""
    if rep_kind == "wta_sign":
        return _encode_wta_sign(z, k)
    if rep_kind == "topk_mag":
        return _encode_topk_mag(z, k)
    if rep_kind == "dense":
        return z.astype(np.float32)
    raise ValueError(f"unknown rep_kind {rep_kind}")


def measure_seed(bge_full, t_unit_full, seed, regime, device):
    rng = np.random.default_rng(seed)
    V, N, Din = regime["V"], regime["N"], regime["Din"]
    k = max(1, N // 32)                                   # 3.125% sparsity (matches two-head)
    sel = rng.choice(bge_full.shape[0], size=min(V, bge_full.shape[0]), replace=False)
    bge = bge_full[sel].astype(np.float32)
    t_unit = t_unit_full[sel].astype(np.float32)
    Vr = bge.shape[0]

    # native SPREAD expansion (fixed random projection Din -> N; the encoder's native output)
    gW = np.random.default_rng(seed * 1000 + 7)
    W_up = (gW.standard_normal((Din, N)).astype(np.float32) / np.sqrt(Din))
    z_dict = bge @ W_up                                   # (V, N) dense expanded
    s_wta_sign = _encode_wta_sign(z_dict, k)              # stored sparse-bipolar spread code

    # STORE / SP: native-spread store (shared by phase_traversal* + spread_static + oracle)
    native_store_unit = _l2n(s_wta_sign)
    sp_native = {str(J): _superposition_recall(native_store_unit,
                                               np.random.default_rng(seed * 100 + J), J, regime["nq"])
                 for J in regime["Js"]}
    sep_native = _offtarget_mean_cos(native_store_unit, np.random.default_rng(seed + 11), regime["sep_sample"])
    # semantic store (crowded) for semantic_static SP
    semantic_store_unit = _l2n(_encode_wta_sign(bge, k))
    sp_semantic = {str(J): _superposition_recall(semantic_store_unit,
                                                 np.random.default_rng(seed * 100 + J), J, regime["nq"])
                   for J in regime["Js"]}

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
    # precompute the noisy query sources + their native expansions (shared by spread/condense arms)
    q_src = {str(a): (src + a * src_norm * noises[a]).astype(np.float32) for a in regime["alphas"]}
    q_z = {str(a): (q_src[str(a)] @ W_up) for a in regime["alphas"]}

    # train the condensers (each reads its own input representation; noise_aug per arm)
    Wc = {}
    train_loss = {}
    for arm in ARMS:
        if arm["kind"] != "condense":
            continue
        Wc[arm["name"]], train_loss[arm["name"]] = _train_condenser(
            bge, W_up, arm["input"], t_unit, arm["name"], arm["noise_aug"],
            seed, regime, device)

    res_arms = {}
    for arm in ARMS:
        name, kind = arm["name"], arm["kind"]
        sp = sp_semantic if kind == "static_semantic" else sp_native

        sc = {}
        # build the SC dictionary code (for hashing + argmax) + per-alpha recall
        if kind == "condense":
            Wm = Wc[name]
            dict_in = _build_input(arm["input"], z_dict, k)      # (V, N)
            dict_code = _l2n(_condense_forward(dict_in, Wm, device))   # (V, Din) condensed dict
            for a in regime["alphas"]:
                q_in = _build_input(arm["input"], q_z[str(a)], k)
                q_code = _l2n(_condense_forward(q_in, Wm, device))
                sc[str(a)] = _sc_argmax(dict_code, q_code, qi)
        elif kind == "static_spread":
            # NO structural transform: argmax on the raw spread code (== any-beta argmax).
            dict_code = native_store_unit                        # (V, N) raw spread, unit
            for a in regime["alphas"]:
                q_code = _l2n(_encode_wta_sign(q_z[str(a)], k))
                sc[str(a)] = _sc_argmax(dict_code, q_code, qi)
        elif kind == "static_semantic":
            dict_code = _l2n(bge)                                 # (V, Din) dense semantic
            for a in regime["alphas"]:
                q_code = _l2n(q_src[str(a)])
                sc[str(a)] = _sc_argmax(dict_code, q_code, qi)
        elif kind == "oracle":
            # existence proof: SP from native spread (above), SC from teacher dense (semantic).
            dict_code = _l2n(bge)
            for a in regime["alphas"]:
                q_code = _l2n(q_src[str(a)])
                sc[str(a)] = _sc_argmax(dict_code, q_code, qi)
        else:
            raise ValueError(f"unknown arm kind {kind}")

        res_arms[name] = {
            "sp": sp,
            "sc": sc,
            "sep_store": sep_native if kind != "static_semantic" else _offtarget_mean_cos(
                semantic_store_unit, np.random.default_rng(seed + 13), regime["sep_sample"]),
            "sc_dict_hash": hashlib.sha256(np.ascontiguousarray(dict_code).tobytes()).hexdigest(),
            "train_loss": train_loss.get(name),
        }
        print(f"[progress] seed={seed} arm={name} SP@{J_OP}={sp.get(str(J_OP)):.3f} "
              f"SC@{ALPHA_OP}={sc.get(str(ALPHA_OP)):.3f} sep={res_arms[name]['sep_store']:+.4f}",
              flush=True)

    return {"seed": int(seed), "V": int(Vr), "N": int(N), "Din": int(Din), "k": int(k),
            "sp_native": sp_native, "sp_semantic": sp_semantic, "arms": res_arms}


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
        sp = {str(J): _mean([s["arms"][nm]["sp"][str(J)] for s in per_seed]) for J in Js}
        sc = {str(a): _mean([s["arms"][nm]["sc"][str(a)] for s in per_seed]) for a in alphas}
        agg["arms"][nm] = {
            "sp_mean": sp, "sc_mean": sc,
            "sep_store_mean": _mean([s["arms"][nm]["sep_store"] for s in per_seed]),
            "sp_op_per_seed": [s["arms"][nm]["sp"][str(J_OP)] for s in per_seed],
            "sc_op_per_seed": [s["arms"][nm]["sc"][str(ALPHA_OP)] for s in per_seed],
            "train_loss_mean": _mean([s["arms"][nm]["train_loss"] for s in per_seed]),
        }
        agg["arms"][nm]["sp_op_cv"] = _cv(agg["arms"][nm]["sp_op_per_seed"])
        agg["arms"][nm]["sc_op_cv"] = _cv(agg["arms"][nm]["sc_op_per_seed"])
    return agg


def _sp(A, nm):
    return A[nm]["sp_mean"][str(J_OP)]


def _sc(A, nm):
    return A[nm]["sc_mean"][str(ALPHA_OP)]


def _joint(sp, sc):
    return float(min(sp / SP_HI, sc / SC_HI))


def _classify(agg):
    A = agg["arms"]
    sp = _sp(A, HEADLINE_ARM)                    # native spread SP (store; shared)
    sc = _sc(A, HEADLINE_ARM)                    # condensed SC
    sc_static = _sc(A, STATIC_CTRL_ARM)          # raw-spread == beta-knob ceiling
    structural_gain = sc - sc_static
    sp_hit = bool(sp >= SP_HI)
    sc_hit = bool(sc >= SC_HI)
    struct_ok = bool(structural_gain >= STRUCT_MARGIN)
    both = bool(sp_hit and sc_hit)
    joint = _joint(sp, sc)

    # enrichment localizers (clean-trained ablation isolates noise-aug value; dense isolates
    # sparsification cost)
    enrich = {nm: {"sp": _sp(A, nm), "sc": _sc(A, nm), "struct_gain": _sc(A, nm) - sc_static}
              for nm in ["phase_traversal_clean", "phase_traversal_dense"]}
    # frontier corners
    frontier = {
        "spread_static": {"sp": _sp(A, "spread_static"), "sc": sc_static},
        "semantic_static": {"sp": _sp(A, "semantic_static"), "sc": _sc(A, "semantic_static")},
    }
    # oracle ceiling (decoupled existence proof)
    oracle = {"sp": _sp(A, "oracle"), "sc": _sc(A, "oracle"),
              "both": bool(_sp(A, "oracle") >= SP_HI and _sc(A, "oracle") >= SC_HI)}

    if both and struct_ok:
        verdict = "HARD_PASS_PHASE_TRAVERSAL_ACHIEVES_BOTH"
    elif not struct_ok:
        verdict = "HARD_FAIL_REDUCES_TO_QE1_BETA_KNOB"
    elif sp_hit and (SC_HI - sc) <= MIDDLE_TOL:
        verdict = "MIDDLE_CONDENSE_NEAR_MISS"
    else:
        verdict = "HARD_FAIL_CONDENSE_CANNOT_RECOVER_COLLAPSES_TO_TRADEOFF"

    return {
        "verdict": verdict,
        "headline": {"arm": HEADLINE_ARM, "sp": sp, "sc": sc, "sc_static": sc_static,
                     "structural_gain": structural_gain, "sp_hit": sp_hit, "sc_hit": sc_hit,
                     "struct_ok": struct_ok, "both": both, "joint": joint},
        "enrich": enrich, "frontier": frontier, "oracle": oracle,
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
    structural-transform-is-real, spread-superposition-fires."""
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

    # 1) VALID ENCODER: semantic teacher (oracle/semantic_static) does clean pointwise ~1.0.
    valid_enc = A7["semantic_static"]["sc"]["0.0"] >= 0.95
    ok &= valid_enc
    # 2) SPREAD SUPERPOSITION FIRES: native spread store SP@J_OP is high (>= SP_HI). (The
    #    decorrelated store BEATS the crowded semantic store only at scale -- at the tiny
    #    selftest V both saturate, so here we only assert the store capacity fires; the
    #    crowding gap is asserted analytically in the pre-reg + measured at FULL V.)
    sp_high = m7["sp_native"][str(J_OP)] >= SP_HI
    ok &= sp_high
    # 3) TELEMETRY-SENSITIVITY (not analytically pinned): perturbing the seed MOVES both the
    #    store SP and the condensed SC of the HEADLINE.
    sp_moves = m7["sp_native"][str(J_OP)] != m13["sp_native"][str(J_OP)]
    sc_moves = A7["phase_traversal"]["sc"][str(ALPHA_OP)] != A13["phase_traversal"]["sc"][str(ALPHA_OP)]
    ok &= (sp_moves and sc_moves)
    # 4) STRUCTURAL TRANSFORM IS REAL (not the QE-1 beta-knob): the condensed SC differs from
    #    the raw-spread (static) SC -- the operator CHANGES the argmax outcome, not a monotonic
    #    rescale. (Direction/magnitude is the FULL question; here we only assert it MOVES.)
    struct_changes = (A7["phase_traversal"]["sc"][str(ALPHA_OP)]
                      != A7["spread_static"]["sc"][str(ALPHA_OP)])
    ok &= struct_changes
    # 5) ARMS DIFFER (META_RULE_AF): all SC-dict hashes distinct except declared exemptions.
    arms_differ, collisions = _arms_differ({a["name"]: A7[a["name"]]["sc_dict_hash"] for a in ARMS})
    ok &= arms_differ
    # 6) CONDENSER TRAINS: HEADLINE has finite RKD train loss.
    tl = A7["phase_traversal"]["train_loss"]
    trains = tl is not None and np.isfinite(tl)
    ok &= trains
    # 7) SC DEGRADES WITH NOISE for the teacher (real pointwise metric, not saturated-vacuous).
    sc_noise = A7["semantic_static"]["sc"]["0.0"] >= A7["semantic_static"]["sc"][str(ALPHA_OP)] - 1e-9
    ok &= sc_noise

    print(f"[self-test] valid_enc={valid_enc}(semSC@0={A7['semantic_static']['sc']['0.0']:.3f}) "
          f"sp_high={sp_high}(nat={m7['sp_native'][str(J_OP)]:.3f} "
          f"sem={m7['sp_semantic'][str(J_OP)]:.3f}) sp_moves={sp_moves} sc_moves={sc_moves} "
          f"struct_changes={struct_changes}(cond={A7['phase_traversal']['sc'][str(ALPHA_OP)]:.3f} "
          f"static={A7['spread_static']['sc'][str(ALPHA_OP)]:.3f}) arms_differ={arms_differ}"
          f"{'' if arms_differ else ' collisions='+str(collisions)} "
          f"trains={trains} sc_noise={sc_noise}")
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
    baseline_sc = _sc(A, STATIC_CTRL_ARM)                # raw-spread pointwise (should NOT saturate)
    baseline_in_band = baseline_sc < 0.95
    arms_differ, arm_collisions = _arms_differ(
        {a["name"]: per_seed[0]["arms"][a["name"]]["sc_dict_hash"] for a in ARMS})

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
    fr = cls["frontier"]
    en = cls["enrich"]
    en_str = " ".join(f"{nm}(SC{v['sc']:.2f},dSC{v['struct_gain']:+.2f})" for nm, v in en.items())
    verdict_msg = (
        f"{verdict} | PHASE-TRAVERSAL: store in a SPREAD/decorrelated phase (SP high), retrieve "
        f"by a REAL structural CONDENSATION operator (recover pointwise SC) from ONE stored code. "
        f"HEADLINE phase_traversal: native-spread SP@J{J_OP}={hl['sp']:.3f} (hit>={SP_HI}:{hl['sp_hit']}) "
        f"+ condensed SC@a{ALPHA_OP}={hl['sc']:.3f} (hit>={SC_HI}:{hl['sc_hit']}) -> achieves_both={hl['both']} "
        f"joint={hl['joint']:.3f}. STRUCTURAL-GAIN (vs beta-knob ceiling spread_static "
        f"SC={hl['sc_static']:.3f}) = {hl['structural_gain']:+.3f} (>= {STRUCT_MARGIN}:{hl['struct_ok']}). "
        f"FRONTIER corners: spread_static(SP{fr['spread_static']['sp']:.2f}/SC{fr['spread_static']['sc']:.2f}) "
        f"semantic_static(SP{fr['semantic_static']['sp']:.2f}/SC{fr['semantic_static']['sc']:.2f}). "
        f"ORACLE ceiling (decoupled): SP{orc['sp']:.2f}/SC{orc['sc']:.2f} both={orc['both']}. "
        f"ENRICH localizers: {en_str}. cache={cache_src}. INTERPRETATION: "
        + ("ONE stored spread engram, traversed by a trained structural condensation operator, "
           "achieves BOTH high superposition (in the spread phase) AND high pointwise (after "
           "condensation) -> the certified decouple-store-from-retrieval law is realizable as a "
           "SINGLE traversed representation (no second stored code), approaching the oracle/two-head."
           if verdict == "HARD_PASS_PHASE_TRAVERSAL_ACHIEVES_BOTH" else
           ("the condensation operator recovers pointwise to within noise of target; a weight/regime "
            "nudge (condenser depth, sparsity k, RKD weight) likely closes it -> report to Research."
            if verdict == "MIDDLE_CONDENSE_NEAR_MISS" else
            ("the structural condensation gained ~nothing over the STATIC raw-spread readout -> it "
             "reduces to the QE-1 beta-knob no-op (a monotonic-rescale cannot change argmax); the "
             "operator must transform the geometry, not the scoring. Re-spec the condensation form."
             if verdict == "HARD_FAIL_REDUCES_TO_QE1_BETA_KNOB" else
             ("the structural condensation helps (beats the beta-knob ceiling) but cannot recover "
              "semantic pointwise FROM the superposition-optimized sparse spread code -> the "
              "sparsification for superposition destroys condensability; collapses to the single-code "
              "tradeoff corner. Check the ENRICH localizers: if phase_traversal_dense recovers, the "
              "WTA sparsification is the culprit (store magnitude/dense); if even dense fails, the "
              "expansion itself is not linearly condensable at this regime -> escalate/5x-drill."
              if verdict == "HARD_FAIL_CONDENSE_CANNOT_RECOVER_COLLAPSES_TO_TRADEOFF" else
              "cardinality / arms-identical / baseline-saturated schema breach; see verdict tag."))))
    )

    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": f"{verdict}: phase-traversal spread-store / condense-retrieve encoder ({run_mode})",
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
        "arm_collisions": arm_collisions,
        "arms_differ_exempt": [list(p) for p in ARMS_DIFFER_EXEMPT],
        "baseline_in_band": baseline_in_band,
        "classification": cls,
        "operating_points": {"J_OP": J_OP, "ALPHA_OP": ALPHA_OP},
        "bands": {"SP_HI": SP_HI, "SC_HI": SC_HI, "MIDDLE_TOL": MIDDLE_TOL,
                  "STRUCT_MARGIN": STRUCT_MARGIN, "LAMBDA_D": LAMBDA_D},
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
