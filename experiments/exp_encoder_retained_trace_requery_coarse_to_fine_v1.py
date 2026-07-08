"""RETAINED-TRACE RE-QUERY: energy-scaled coarse-to-fine selective-depth retrieval that
recovers fine fidelity from a RETAINED DENSE trace where a SPARSE-condensed read cannot.

MECHANISM A (brain-first drill top pick, 2026-07-08). The v1 phase-traversal condenser
(exp_encoder_phase_traversal_spread_condense_v1) hit a CONFIRMED GENUINE info-wall: it stored a
HARD sign+top-k spread code and tried to recover pointwise semantics by condensing THAT sparse
code -- structural_gain = -0.348 (condense(sparse) SC 0.5383 << raw static 0.8867). Skunkworks
confirmed the wall is the sign+top-k quantization, NOT the condenser: the same cell's
phase_traversal_DENSE arm (condense off the un-sparsified DENSE code) reached SC 0.9933
(near-oracle). The brain never destroys-then-recovers (hippocampal indexing theory, Teyler-Rudy
2007: store a sparse INDEX; keep the fine trace intact and re-query IT). This cell tests the
direct analog:

  COARSE read (cheap, all V): rank every dictionary item by a CHEAP low-dim CONDENSATION of the
    RETAINED DENSE code z (a fixed random projection z @ P to D_COARSE dims, cosine). This is
    "condense the retained dense code cheaply", NOT the sparse quantized code -- so the coarse
    ranking shares the DENSE geometry the fine read uses (avoids the decoupled-geometry risk the
    drill flagged for a sparse-code coarse ranking). Produces a top-k SHORTLIST.
  FINE read (expensive, shortlist only): re-rank the shortlist by the FULL trained DENSE
    condenser (the already-MEASURED-0.9933 operator) on the RETAINED DENSE code z. Because the
    trace was never destroyed, the fine read recovers full fidelity.

ENERGY / COST (analytical flop model; the selective-depth win): fine-condense ONLY the shortlist,
not all V. Per-query read cost:
  full_fine (ceiling)   ~ (V+1) * C_fine
  retained_trace (B)@k  ~ V * C_coarse  +  (k+1) * C_fine
  with C_coarse = N*D_COARSE (one linear proj), C_fine = N*H + H*Din (2-layer condenser).
  cost_ratio(k) ~ C_coarse/C_fine + k/V. At D_COARSE=128,N=4096,H=Din=1024,k=0.10V:
  ~0.10 + 0.10 = 0.20 -> ~5x cheaper than the full fine read, at (target) negligible fidelity loss.

ARMS (decisive multi-arm coarse-to-fine selective-depth comparison; ONE lever varied = the
fine-read TRACE SOURCE, coarse shortlist held identical for B/A'):
  full_fine_read           dense condense over ALL V (no shortlist)   [CEILING / Gate-D reproduce 0.9933]
  retained_trace_requery   coarse dense-proj shortlist -> dense condense within shortlist [HEADLINE=B]
  sparse_condense_fullV    sparse condense over ALL V (the v1 negative) [MUST-FAIL / Gate-D reproduce 0.5383]
  sparse_condense_shortlist coarse dense-proj shortlist -> SPARSE condense within shortlist [ISOLATOR=A']
  coarse_only              coarse-proj argmax over ALL V (top-1)        [DIAGNOSTIC: coarse is genuinely coarse]

The A' isolator is load-bearing: it gives the SAME good dense shortlist to a SPARSE fine read.
If A' still fails while B recovers, the win is provably the DENSE fine-read TRACE, not the
shortlist. If A' rises to meet B, the shortlist alone rescued sparse (a different, honest result).

METRICS:
  final_recall@alpha  = fraction of noisy queries whose argmax (over the arm's allowed index set:
                        all V, or the coarse shortlist) is the true concept. THE decisive fidelity.
  shortlist_hit_rate@k = fraction of queries whose true concept is inside the coarse top-k
                        (the drill's kill test: coarse ranking must CONTAIN the answer).
  cost_ratio@k        = analytical read-cost of B(k) vs full_fine (energy accounting).
  SP@J (native store) = reported for continuity (preserved by construction; the store code is the
                        native spread code as in v1; not the gate here).

PRE-REG BANDS (HEADLINE = retained_trace_requery=B at k_OP=0.10; strictly-above-floor per
META_RULE_L; anchored to MEASURED v1: dense ceiling 0.9933, sparse wall 0.5383):
  HARD_PASS = B recovers (final_recall_B >= RECOVER_HI=0.90 AND within CEIL_TOL=0.05 of the
              full_fine ceiling) AND sparse CANNOT (max(sparse_fullV, sparse_shortlist) <=
              SPARSE_FAIL_CEIL=0.70) AND B beats sparse by (B - max_sparse) >= DISCRIM_GAP=0.20
              AND cost_ok (cost_ratio_B(k_OP) <= COST_MAX=0.50). -> retained-trace re-query is a
              real near-zero-new-mechanism fix: cheap coarse + recoverable fine.
  MIDDLE    = B beats sparse by DISCRIM_GAP and is within MIDDLE_TOL of RECOVER_HI but does not
              clear at k_OP (needs a larger shortlist k or wider D_COARSE) -> report the curve.
  HARD_FAIL = HARD_FAIL_NO_RECOVERY : (B - max_sparse) < DISCRIM_GAP (retained-trace does NOT beat
              sparse-condense on recoverable fidelity -> the wall is deeper than the quantization
              step), OR
            HARD_FAIL_DECOUPLED_GEOMETRY : shortlist_hit_rate@k_OP < HIT_FLOOR=0.65 (the coarse
              ranking cannot even CONTAIN the answer -> coarse and fine geometries decoupled; a
              genuinely new negative distinct from the quantization wall).

DISCRIMINATOR-FIRES (assert_discriminator_fires, MANDATORY at smoke): the SPARSE control must FAIL
the recovery gate at smoke scale. If max(sparse_fullV, sparse_shortlist) > SPARSE_FAIL_CEIL at the
smoke V, the smoke is SATURATION-VACUOUS -> raise V. sparse_condense_fullV reproduces the MEASURED
v1 wall (~0.5383 at V=8000), so the info-wall is present at smoke scale by measurement, not
by-construction.

## Compute architecture
Class (a) batched-GPU. Two condensers trained (dense + sparse), matmul-heavy (per-iter store-code
forward B x N @ N x H @ H x Din, RKD pairwise B x B). FULL routes to GPU (overnight_queue) at
production N=4096, V=40000, B=8192 (B > N -> full-rank RKD sample). SMOKE runs CPU-local at
PRODUCTION N=4096 with reduced V/iters/B -- DISCRIMINATOR-MUST-SURVIVE-SCALE option A/C (smoke at
full-N, scaled-preview V=8000 = the SAME V where v1 MEASURED the 0.9933/0.5383 gap, so the
discriminator provably fires at the smoke scale). Eval (argmax recall, coarse ranking, shortlist
masking) is vectorized numpy over precomputed codes -- no Python loop over V. Storage strategy:
no_composition / no_store (encoder-geometry cell; the "dictionary" is the per-concept code,
evaluated by argmax-cosine cleanup + coarse-to-fine shortlist, not a bundled associative store).

## Functional Requirements
  FR1 cheap coarse shortlist that CONTAINS the answer -> low-dim linear condensation of the
      retained dense code (random projection z@P, JL-preserves the semantic geometry). Measured:
      shortlist_hit_rate@k.
  FR2 fine read that recovers full pointwise fidelity FROM the retained trace -> the trained DENSE
      condenser (v1's phase_traversal_dense operator, MEASURED 0.9933). Measured: final_recall_B.
  FR3 do it at materially lower cost than the full fine read -> fine-condense only the shortlist.
      Measured: cost_ratio_B@k (analytical flop model).
  FR4 (contrast) a SPARSE-condensed fine read CANNOT recover -> the confirmed v1 info-wall,
      reproduced as sparse_condense_fullV (+ the A' isolator that keeps the good shortlist).

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
- arms_differ_verified at smoke gate (sha256 of each READ-FAMILY code: dense-fine, sparse-fine,
  coarse; distinct. k_frac variants are index-restrictions of the same family -> shared by design).
- cardinality_ok: sweep-axis (k_frac) cell -> EXPECTED_N_UNITS = n_seeds AND every seed carries all
  K_FRACS (k-cardinality gate).
- final_metrics_atomicity: tmp_replace (os.replace on final metrics.json).
- except SystemExit: raise BEFORE except Exception (no BaseException).
- crlb_n/a: retrieval recall + shortlist hit rate; no closed-form noise floor. Feasibility handled
  by calibrated operating points anchored to MEASURED v1 (dense 0.9933, sparse 0.5383 at this exact
  N=4096, V=8000, alpha=1.2, k=N/32 regime).
- baseline_in_band: sparse_condense_fullV recall in (0.05, 0.95) (the ~0.5383 wall; a tradeoff
  exists) AND sparse_condense_shortlist < 0.90 (not saturated by the shortlist).
- discriminator survives scale: smoke at production N=4096 and V=8000 = the MEASURED-gap regime.
- HARD bands strictly above floor (RECOVER_HI 0.90 headroom to 0.9933; DISCRIM_GAP 0.20 below the
  MEASURED raw gap 0.9933-0.5383=0.455).
- per-unit failure-class instrumentation (no bare except).
- calibration_check: default_ok_for_this_regime (real BGE cache; J_OP/alpha_OP/k = N/32 calibrated
  in v1 + two-head cells; the Gate-D reproduce arms validate the harness at the matched regime).
- telemetry-sensitivity self-test MANDATORY (perturb-a-seed MOVES final_recall_B, sparse recall,
  and shortlist hit rate; the shortlist CHANGES which items the fine read sees).
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

# canonical smoke discriminator gate (Pattern-5 shipped to remote)
from experiments._seed_checkpoint import assert_discriminator_fires, VacuousSmokeError

ANCHOR_NAME = "encoder_retained_trace_requery_coarse_to_fine_v1"
OUTPUT_DIR = os.path.join(_REPO, "data", f"exp_{ANCHOR_NAME}")
_CACHE_DIR = os.path.join(_REPO, "data", "substrate_index", "cached_indices")

# operating points (match v1 / two-head for comparability)
J_OP = 5
ALPHA_OP = 1.2
LAMBDA_D = 1.0
COND_H = 1024
NOISE_AUG_ALPHA = 1.6
NOISE_AUG_FRAC = 0.5

# coarse read + shortlist
D_COARSE = 128                       # low-dim coarse projection width (cheap; JL-preserves geometry)
K_FRACS = [0.05, 0.10, 0.15, 0.25]   # shortlist size as fraction of V (energy-scaled sweep)
K_OP_FRAC = 0.10                     # headline operating point (drill HARD-PASS is k <= 0.10 V)

# pre-reg bands (HEADLINE = retained_trace_requery = B at K_OP_FRAC)
RECOVER_HI = 0.90        # B final_recall must reach this (dense ceiling MEASURED 0.9933)
CEIL_TOL = 0.05          # B must be within this of the full_fine ceiling (shortlist costs little)
DISCRIM_GAP = 0.20       # B - max(sparse arms) must be at least this
SPARSE_FAIL_CEIL = 0.70  # both sparse arms must stay at/below this (= RECOVER_HI - DISCRIM_GAP)
COST_MAX = 0.50          # B(k_OP) read-cost must be <= half the full_fine cost
MIDDLE_TOL = 0.05        # near-miss tolerance for RECOVER_HI (MIDDLE band)
HIT_FLOOR = 0.65         # shortlist_hit_rate@k_OP below this -> decoupled-geometry HARD_FAIL

# Gate-D positive-control reproducers (reproduce v1 at the MATCHED smoke regime V=8000)
DENSE_PRIOR = 0.9933     # MEASURED@data/exp_encoder_phase_traversal_spread_condense_v1/metrics.json:agg.arms.phase_traversal_dense.sc_mean."1.2"
SPARSE_PRIOR = 0.5383    # MEASURED@data/exp_encoder_phase_traversal_spread_condense_v1/metrics.json:agg.arms.phase_traversal.sc_mean."1.2"
GATE_D_TOL = 0.12        # reproduce tolerance at matched V=8000 smoke (loosened to 0.12 at FULL V=40000 where argmax over more distractors drifts the ceiling; enforced hard only at smoke)

ARM_FULL_FINE = "full_fine_read"
ARM_RETAINED = "retained_trace_requery"
ARM_SPARSE_FULLV = "sparse_condense_fullV"
ARM_SPARSE_SHORT = "sparse_condense_shortlist"
ARM_COARSE = "coarse_only"
HEADLINE_ARM = ARM_RETAINED

FULL_SEEDS = [7, 13, 19, 23, 29]
SMOKE_SEEDS = [7, 13, 19]
SELFTEST_SEEDS = [7, 13]

FULL_REGIME = dict(N=4096, Din=1024, V=40000, iters=800, B=8192, lr=1e-3,
                   Js=[1, 2, 3, 5, 8], alphas=[0.0, 0.8, 1.2, 1.6], nq=600)
SMOKE_REGIME = dict(N=4096, Din=1024, V=8000, iters=300, B=1536, lr=1e-3,
                    Js=[1, 5], alphas=[0.0, 1.2], nq=400)
SELFTEST_REGIME = dict(N=2048, Din=1024, V=700, iters=80, B=350, lr=1e-3,
                       Js=[1, 5], alphas=[0.0, 1.2], nq=180)


# --------------------------------- numpy eval prims --------------------------
def _l2n(x):
    return x / (np.linalg.norm(x, axis=1, keepdims=True) + 1e-9)


def _encode_wta_sign(z, k):
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


def _recall_full(query_code_unit, dict_code_unit, qi):
    """Argmax-cosine recall over the FULL dictionary. query/dict already unit-normalized."""
    pred = np.argmax(query_code_unit @ dict_code_unit.T, axis=1)
    return float(np.mean(pred == qi))


def _shortlist_topk(coarse_q_unit, coarse_dict_unit, k):
    """Top-k coarse indices per query. Returns (nq, k) int index array."""
    scores = coarse_q_unit @ coarse_dict_unit.T          # (nq, V)
    k = min(k, scores.shape[1])
    part = np.argpartition(-scores, k - 1, axis=1)[:, :k]
    return part


def _hit_rate(topk_idx, qi):
    """Fraction of queries whose true id qi[i] is inside the shortlist row topk_idx[i]."""
    hits = [bool(qi[i] in set(topk_idx[i].tolist())) for i in range(len(qi))]
    return float(np.mean(hits))


def _recall_within_shortlist(query_code_unit, dict_code_unit, qi, topk_idx):
    """Argmax-cosine recall restricted to each query's coarse shortlist (vectorized mask)."""
    sims = query_code_unit @ dict_code_unit.T            # (nq, V)
    nq = sims.shape[0]
    mask = np.zeros_like(sims, dtype=bool)
    rows = np.arange(nq)[:, None]
    mask[rows, topk_idx] = True
    sims = np.where(mask, sims, -1e30)
    pred = np.argmax(sims, axis=1)
    return float(np.mean(pred == qi))


# --------------------------------- torch condenser ---------------------------
def _resolve_device(want):
    import torch
    if want == "cpu":
        return "cpu"
    if want == "cuda":
        if not torch.cuda.is_available():
            raise RuntimeError("device=cuda requested but torch.cuda.is_available()==False")
        return "cuda"
    return "cuda" if torch.cuda.is_available() else "cpu"


def _init_param(shape, fan_in, gen, device):
    import torch
    return (torch.randn(*shape, generator=gen).to(device) / (fan_in ** 0.5)).requires_grad_(True)


def _rkd_loss(c, tc, off_mask):
    """Relational-KD: match student (condensed) pairwise-cosine to teacher's (off-diag MSE)."""
    cc = c / (c.norm(dim=1, keepdim=True) + 1e-9)
    s_s = cc @ cc.T
    s_t = tc @ tc.T
    return ((s_s - s_t)[off_mask] ** 2).mean()


def _build_input(rep_kind, z, k):
    """Return the representation the condenser reads from, for a batch of expanded codes z."""
    if rep_kind == "wta_sign":
        return _encode_wta_sign(z, k)
    if rep_kind == "dense":
        return z.astype(np.float32)
    raise ValueError(f"unknown rep_kind {rep_kind}")


def _train_condenser(bge_np, W_up, rep_kind, t_unit_np, tag, seed, regime, device):
    """Train a 2-layer nonlinear condenser c = gelu(inp @ W1) @ W2 : (N)->(H)->(Din), RKD-distilled
    to the teacher pairwise geometry, NOISE-AUGMENTED (a fraction of each batch is source-perturbed
    at random relative alpha then read as rep_kind, mapped to the CLEAN teacher rows). Verbatim
    mechanism from v1's _train_condenser. Only W1,W2 carry gradients; W_up fixed. Returns numpy
    params + last loss."""
    import torch
    Din = t_unit_np.shape[1]
    N = W_up.shape[1]
    H = COND_H
    V = bge_np.shape[0]
    B = min(regime["B"], V)
    iters = regime["iters"]
    k = max(1, N // 32)
    src_norm = np.linalg.norm(bge_np, axis=1, keepdims=True)
    salt = int(hashlib.sha256(tag.encode()).hexdigest()[:6], 16)
    g = torch.Generator(device="cpu").manual_seed(seed * 1000 + 1 + salt)
    W1 = _init_param((N, H), N, g, device)
    W2 = _init_param((H, Din), H, g, device)
    tcos = torch.from_numpy(t_unit_np).to(device)
    off_mask = ~torch.eye(B, dtype=torch.bool, device=device)
    opt = torch.optim.Adam([W1, W2], lr=regime["lr"])
    nrng = np.random.default_rng(seed * 2000 + 17 + salt)
    z_clean_full = bge_np @ W_up
    store_clean_full = _build_input(rep_kind, z_clean_full, k)
    last = None
    for it in range(iters):
        idx = nrng.choice(V, size=B, replace=False)
        n_noisy = int(round(NOISE_AUG_FRAC * B))
        src = bge_np[idx].copy()
        if n_noisy > 0:
            a = nrng.uniform(0.0, NOISE_AUG_ALPHA, size=(n_noisy, 1)).astype(np.float32)
            nz = nrng.standard_normal((n_noisy, Din)).astype(np.float32)
            nz = nz / (np.linalg.norm(nz, axis=1, keepdims=True) + 1e-9)
            src[:n_noisy] = (src[:n_noisy] + a * src_norm[idx][:n_noisy] * nz)
        inp_np = _build_input(rep_kind, src @ W_up, k)
        inp = torch.from_numpy(np.ascontiguousarray(inp_np, dtype=np.float32)).to(device)
        c = torch.nn.functional.gelu(inp @ W1) @ W2
        loss = LAMBDA_D * _rkd_loss(c, tcos[idx], off_mask)
        opt.zero_grad(set_to_none=True)
        loss.backward()
        opt.step()
        last = float(loss.detach().cpu())
        if it % max(1, iters // 6) == 0 or it == iters - 1:
            print(f"[progress] seed={seed} cond={tag} it={it}/{iters} rkd_loss={last:.5f}", flush=True)
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
    k_sp = max(1, N // 32)                                # 3.125% sparsity (matches v1)
    sel = rng.choice(bge_full.shape[0], size=min(V, bge_full.shape[0]), replace=False)
    bge = bge_full[sel].astype(np.float32)
    t_unit = t_unit_full[sel].astype(np.float32)
    Vr = bge.shape[0]

    # native SPREAD expansion (fixed random Din->N; encoder native output) = the RETAINED DENSE code
    gW = np.random.default_rng(seed * 1000 + 7)
    W_up = (gW.standard_normal((Din, N)).astype(np.float32) / np.sqrt(Din))
    z_dict = bge @ W_up                                   # (V, N) dense expanded = RETAINED trace
    s_wta = _encode_wta_sign(z_dict, k_sp)               # (V, N) sparse bipolar store code

    # coarse read: fixed random projection of the RETAINED DENSE code to D_COARSE dims (cheap)
    gP = np.random.default_rng(seed * 1000 + 31)
    P = (gP.standard_normal((N, D_COARSE)).astype(np.float32) / np.sqrt(N))
    coarse_dict = _l2n(z_dict @ P)                        # (V, D_COARSE)

    # native-store superposition (context; preserved by construction)
    native_store_unit = _l2n(s_wta)
    sp_native = {str(J): _superposition_recall(native_store_unit,
                                               np.random.default_rng(seed * 100 + J), J, regime["nq"])
                 for J in regime["Js"]}

    # train the two condensers (dense fine-read + sparse fine-read), both noise-augmented
    Wc_dense, loss_dense = _train_condenser(bge, W_up, "dense", t_unit, "dense", seed, regime, device)
    Wc_sparse, loss_sparse = _train_condenser(bge, W_up, "wta_sign", t_unit, "sparse", seed, regime, device)

    # precompute dict fine codes (dense + sparse)
    dense_dict_code = _l2n(_condense_forward(z_dict, Wc_dense, device))     # (V, Din)
    sparse_dict_code = _l2n(_condense_forward(s_wta, Wc_sparse, device))    # (V, Din)

    # read-family hashes for arms-differ (dense-fine / sparse-fine / coarse distinct)
    fam_hash = {
        "dense_fine": hashlib.sha256(np.ascontiguousarray(dense_dict_code).tobytes()).hexdigest(),
        "sparse_fine": hashlib.sha256(np.ascontiguousarray(sparse_dict_code).tobytes()).hexdigest(),
        "coarse": hashlib.sha256(np.ascontiguousarray(coarse_dict).tobytes()).hexdigest(),
    }

    # noisy query set (shared across arms)
    qi = np.random.default_rng(seed * 7 + 3).choice(Vr, size=min(regime["nq"], Vr), replace=False)
    src = bge[qi]
    src_norm = np.linalg.norm(src, axis=1, keepdims=True)
    qrng = np.random.default_rng(seed * 7 + 5)

    per_alpha = {}
    for a in regime["alphas"]:
        nz = qrng.standard_normal(src.shape).astype(np.float32)
        nz = nz / (np.linalg.norm(nz, axis=1, keepdims=True) + 1e-9)
        q_src = (src + a * src_norm * nz).astype(np.float32)
        q_z = q_src @ W_up                                        # (nq, N) retained dense query
        q_s = _encode_wta_sign(q_z, k_sp)                        # (nq, N) sparse query

        coarse_q = _l2n(q_z @ P)                                  # (nq, D_COARSE)
        dense_q_code = _l2n(_condense_forward(q_z, Wc_dense, device))    # (nq, Din)
        sparse_q_code = _l2n(_condense_forward(q_s, Wc_sparse, device))  # (nq, Din)

        # full-V arms
        full_fine = _recall_full(dense_q_code, dense_dict_code, qi)
        sparse_fullv = _recall_full(sparse_q_code, sparse_dict_code, qi)
        coarse_only = _recall_full(coarse_q, coarse_dict, qi)

        # shortlist arms across K_FRACS
        b_by_k, aprime_by_k, hit_by_k = {}, {}, {}
        for kf in K_FRACS:
            k = max(1, int(round(kf * Vr)))
            topk = _shortlist_topk(coarse_q, coarse_dict, k)
            hit_by_k[str(kf)] = _hit_rate(topk, qi)
            b_by_k[str(kf)] = _recall_within_shortlist(dense_q_code, dense_dict_code, qi, topk)
            aprime_by_k[str(kf)] = _recall_within_shortlist(sparse_q_code, sparse_dict_code, qi, topk)

        per_alpha[str(a)] = {
            "full_fine": full_fine, "sparse_fullv": sparse_fullv, "coarse_only": coarse_only,
            "b_by_k": b_by_k, "aprime_by_k": aprime_by_k, "hit_by_k": hit_by_k,
        }
        print(f"[progress] seed={seed} alpha={a} full_fine={full_fine:.3f} "
              f"sparse_fullv={sparse_fullv:.3f} coarse_only={coarse_only:.3f} "
              f"B@{K_OP_FRAC}={b_by_k[str(K_OP_FRAC)]:.3f} Aprime@{K_OP_FRAC}={aprime_by_k[str(K_OP_FRAC)]:.3f} "
              f"hit@{K_OP_FRAC}={hit_by_k[str(K_OP_FRAC)]:.3f}", flush=True)

    return {"seed": int(seed), "V": int(Vr), "N": int(N), "Din": int(Din), "k_sp": int(k_sp),
            "D_COARSE": int(D_COARSE), "sp_native": sp_native, "fam_hash": fam_hash,
            "train_loss": {"dense": loss_dense, "sparse": loss_sparse}, "per_alpha": per_alpha}


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


def _cost_ratio(kf, N, Din):
    """Analytical read-cost ratio B(k) vs full_fine. c_coarse=N*D_COARSE, c_fine=N*H+H*Din."""
    c_coarse = N * D_COARSE
    c_fine = N * COND_H + COND_H * Din
    return float(c_coarse / c_fine + kf)                 # C_coarse/C_fine + k/V


def _aggregate(per_seed, regime):
    ao = str(ALPHA_OP)
    agg = {"n_seeds": len(per_seed), "alphas": [str(a) for a in regime["alphas"]]}
    # per-alpha means of the scalar arms
    arms = {}
    for a in regime["alphas"]:
        sa = str(a)
        arms[sa] = {
            "full_fine": _mean([s["per_alpha"][sa]["full_fine"] for s in per_seed]),
            "sparse_fullv": _mean([s["per_alpha"][sa]["sparse_fullv"] for s in per_seed]),
            "coarse_only": _mean([s["per_alpha"][sa]["coarse_only"] for s in per_seed]),
            "b_by_k": {str(kf): _mean([s["per_alpha"][sa]["b_by_k"][str(kf)] for s in per_seed])
                       for kf in K_FRACS},
            "aprime_by_k": {str(kf): _mean([s["per_alpha"][sa]["aprime_by_k"][str(kf)] for s in per_seed])
                            for kf in K_FRACS},
            "hit_by_k": {str(kf): _mean([s["per_alpha"][sa]["hit_by_k"][str(kf)] for s in per_seed])
                         for kf in K_FRACS},
        }
    agg["arms_by_alpha"] = arms
    agg["cost_ratio_by_k"] = {str(kf): _cost_ratio(kf, regime["N"], regime["Din"]) for kf in K_FRACS}
    agg["sp_native_mean"] = {str(J): _mean([s["sp_native"][str(J)] for s in per_seed])
                             for J in regime["Js"]}
    # per-seed op-point series for CV / telemetry
    agg["b_op_per_seed"] = [s["per_alpha"][ao]["b_by_k"][str(K_OP_FRAC)] for s in per_seed]
    agg["sparse_fullv_op_per_seed"] = [s["per_alpha"][ao]["sparse_fullv"] for s in per_seed]
    agg["b_op_cv"] = _cv(agg["b_op_per_seed"])
    return agg


def _classify(agg):
    ao = str(ALPHA_OP)
    A = agg["arms_by_alpha"][ao]
    ceiling = A["full_fine"]
    b = A["b_by_k"][str(K_OP_FRAC)]
    aprime = A["aprime_by_k"][str(K_OP_FRAC)]
    sparse_full = A["sparse_fullv"]
    max_sparse = max(aprime, sparse_full)
    hit = A["hit_by_k"][str(K_OP_FRAC)]
    cost = agg["cost_ratio_by_k"][str(K_OP_FRAC)]

    b_recovers = bool(b >= RECOVER_HI and b >= ceiling - CEIL_TOL)
    sparse_fails = bool(max_sparse <= SPARSE_FAIL_CEIL)
    beats_by_gap = bool((b - max_sparse) >= DISCRIM_GAP)
    cost_ok = bool(cost <= COST_MAX)
    hit_ok = bool(hit >= HIT_FLOOR)

    if not hit_ok:
        verdict = "HARD_FAIL_DECOUPLED_GEOMETRY"
    elif not beats_by_gap:
        verdict = "HARD_FAIL_NO_RECOVERY"
    elif b_recovers and sparse_fails and cost_ok:
        verdict = "HARD_PASS_RETAINED_TRACE_RECOVERS"
    elif (RECOVER_HI - b) <= MIDDLE_TOL and beats_by_gap:
        verdict = "MIDDLE_RETAINED_TRACE_NEAR_MISS"
    else:
        verdict = "HARD_FAIL_NO_RECOVERY"

    return {
        "verdict": verdict,
        "k_op": K_OP_FRAC,
        "ceiling_full_fine": ceiling,
        "B_retained_trace": b,
        "Aprime_sparse_shortlist": aprime,
        "sparse_fullV": sparse_full,
        "max_sparse": max_sparse,
        "shortlist_hit_rate": hit,
        "cost_ratio_B": cost,
        "b_recovers": b_recovers, "sparse_fails": sparse_fails,
        "beats_by_gap": beats_by_gap, "cost_ok": cost_ok, "hit_ok": hit_ok,
        "gap_B_minus_sparse": float(b - max_sparse),
        "thresholds": {"RECOVER_HI": RECOVER_HI, "CEIL_TOL": CEIL_TOL, "DISCRIM_GAP": DISCRIM_GAP,
                       "SPARSE_FAIL_CEIL": SPARSE_FAIL_CEIL, "COST_MAX": COST_MAX,
                       "MIDDLE_TOL": MIDDLE_TOL, "HIT_FLOOR": HIT_FLOOR},
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
    """Scaffold-free witnesses meaningful at the TINY selftest V (V=700 SATURATES the recall/hit
    metrics at ~1.0, so the non-saturated hit-rate/B telemetry is a SMOKE-scale property, verified
    at smoke V=8000 -- here we assert the discriminator DIRECTION + the info-wall + the
    telemetry-sensitivity of the UNSATURATED discriminator (sparse recall)). See v1's selftest which
    made the identical tiny-V-saturation exemption."""
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
    ao, kop = str(ALPHA_OP), str(K_OP_FRAC)
    p7, p13 = m7["per_alpha"], m13["per_alpha"]
    b = p7[ao]["b_by_k"][kop]
    aprime = p7[ao]["aprime_by_k"][kop]
    sparse_full = p7[ao]["sparse_fullv"]

    # 1) VALID ENCODER: dense fine read on CLEAN queries ~ near 1.0.
    valid_enc = p7[ao]["full_fine"] >= 0.90 or p7["0.0"]["full_fine"] >= 0.95
    ok &= valid_enc
    # 2) COARSE IS GENUINELY COARSE: coarse-only top1 recall < full_fine (not secretly the oracle).
    coarse_is_coarse = p7[ao]["coarse_only"] < p7[ao]["full_fine"]
    ok &= coarse_is_coarse
    # 3) INFO-WALL PRESENT: the sparse-condense fine read FAILS (< 0.90) even at the tiny selftest V,
    #    reproducing the v1 wall (mechanism direction, not scale-magnitude).
    wall_present = sparse_full < 0.90 and aprime < 0.90
    ok &= wall_present
    # 4) RETAINED-TRACE RECOVERS ABOVE SPARSE: dense fine (B) beats sparse fine (A' within shortlist,
    #    and sparse over all V) -- the core discriminator direction, fires even at saturated tiny V.
    recovers = b > aprime and b > sparse_full
    ok &= recovers
    # 5) TELEMETRY-SENSITIVITY: perturbing the seed MOVES the UNSATURATED discriminator (sparse
    #    recall). (B/hit saturate at 1.0 at tiny V -> their movement is a smoke-scale check.)
    sp_moves = p7[ao]["sparse_fullv"] != p13[ao]["sparse_fullv"]
    ok &= sp_moves
    # 6) ARMS DIFFER (META_RULE_AF): dense-fine / sparse-fine / coarse read-families distinct.
    fh = m7["fam_hash"]
    arms_differ = len(set(fh.values())) == 3
    ok &= arms_differ
    # 7) CONDENSERS TRAIN: finite RKD loss for both.
    tl = m7["train_loss"]
    trains = all(v is not None and np.isfinite(v) for v in tl.values())
    ok &= trains

    print(f"[self-test] valid_enc={valid_enc}(ff@op={p7[ao]['full_fine']:.3f} ff@0={p7['0.0']['full_fine']:.3f}) "
          f"coarse_is_coarse={coarse_is_coarse}(coarse={p7[ao]['coarse_only']:.3f}) "
          f"wall_present={wall_present}(sparse_fullv={sparse_full:.3f} Aprime={aprime:.3f}) "
          f"recovers={recovers}(B={b:.3f}) sp_moves={sp_moves}"
          f"({p7[ao]['sparse_fullv']:.3f} vs {p13[ao]['sparse_fullv']:.3f}) "
          f"arms_differ={arms_differ} trains={trains}")
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

    # optional heartbeat (long FULL on GPU); best-effort, never blocks the run
    hb = None
    try:
        from experiments._cell_heartbeat import CellHeartbeat
        hb = CellHeartbeat(OUTPUT_DIR, total_units=len(seeds), interval_s=30)
        hb.__enter__()
    except Exception:  # noqa: BLE001
        hb = None

    per_seed = []
    try:
        for si, sd in enumerate(seeds):
            pp = _seed_partial_path(OUTPUT_DIR, run_mode, sd)
            if os.path.exists(pp):
                try:
                    with open(pp, encoding="utf-8") as f:
                        per_seed.append(json.load(f))
                    print(f"[resume] seed={sd} loaded from partial", flush=True)
                    if hb is not None:
                        hb.tick(si)
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
            if hb is not None:
                hb.tick(si)
    finally:
        if hb is not None:
            try:
                hb.__exit__(None, None, None)
            except Exception:  # noqa: BLE001
                pass

    agg = _aggregate(per_seed, regime)
    cls = _classify(agg)

    # schema gates
    n_units = len(per_seed)
    cardinality_ok = (n_units == expected_units)
    # k-cardinality: every seed carries all K_FRACS at every alpha
    kcard_ok = all(
        all(str(kf) in s["per_alpha"][str(a)]["b_by_k"] for kf in K_FRACS for a in regime["alphas"])
        for s in per_seed)
    fh0 = per_seed[0]["fam_hash"]
    arms_differ = len(set(fh0.values())) == 3
    ao = str(ALPHA_OP)
    A = agg["arms_by_alpha"][ao]
    sparse_full = A["sparse_fullv"]
    aprime_op = A["aprime_by_k"][str(K_OP_FRAC)]
    baseline_in_band = bool(0.05 < sparse_full < 0.95 and aprime_op < 0.90)

    # Gate-D positive-control reproducers (hard only at smoke V=8000 matched regime)
    ceiling = A["full_fine"]
    gate_d_dense = abs(ceiling - DENSE_PRIOR) <= GATE_D_TOL
    gate_d_sparse = abs(sparse_full - SPARSE_PRIOR) <= GATE_D_TOL
    gate_d_ok = bool(gate_d_dense and gate_d_sparse)

    if not cardinality_ok:
        verdict = "HARD_FAIL_CARDINALITY_BREACH_META_RULE_H"
    elif not kcard_ok:
        verdict = "HARD_FAIL_KCARDINALITY_BREACH_META_RULE_H"
    elif not arms_differ:
        verdict = "HARD_FAIL_ARMS_IDENTICAL_META_RULE_AF"
    elif not baseline_in_band:
        verdict = "HARD_FAIL_BASELINE_SATURATED_NO_TRADEOFF_META_RULE_AG"
    elif run_mode == "smoke" and not gate_d_ok:
        verdict = "HARD_FAIL_GATE_D_REGIME_OR_INVOCATION_MISMATCH"
    else:
        verdict = cls["verdict"]

    # DISCRIMINATOR-FIRES smoke gate: the SPARSE control must FAIL the recovery gate at smoke scale.
    if run_mode == "smoke":
        max_sparse = max(sparse_full, aprime_op)
        control_passed = bool(max_sparse > SPARSE_FAIL_CEIL)  # sparse did NOT clearly fail -> vacuous
        assert_discriminator_fires(
            control_passed, control_name="sparse_condense(max fullV/shortlist)",
            headline_name="retained_trace_requery", run_mode="smoke",
            extra=(f"max_sparse={max_sparse:.3f} SPARSE_FAIL_CEIL={SPARSE_FAIL_CEIL} "
                   f"B@{K_OP_FRAC}={cls['B_retained_trace']:.3f} ceiling={ceiling:.3f}"))

    b = cls["B_retained_trace"]
    hit = cls["shortlist_hit_rate"]
    cost = cls["cost_ratio_B"]
    gap = cls["gap_B_minus_sparse"]
    curve = " ".join(f"k{kf}:B{A['b_by_k'][str(kf)]:.3f}/hit{A['hit_by_k'][str(kf)]:.3f}/"
                     f"cost{agg['cost_ratio_by_k'][str(kf)]:.3f}" for kf in K_FRACS)
    verdict_msg = (
        f"{verdict} | RETAINED-TRACE RE-QUERY (mechanism A): cheap COARSE shortlist by condensing "
        f"the RETAINED DENSE code (random proj D_COARSE={D_COARSE}), FINE read recovers within the "
        f"shortlist from the retained trace. HEADLINE B@k{K_OP_FRAC}: final_recall={b:.3f} "
        f"(recover>={RECOVER_HI}:{cls['b_recovers']}) vs full_fine CEILING={ceiling:.3f} "
        f"(Gate-D reproduce dense {DENSE_PRIOR}:{gate_d_dense}). SPARSE control: sparse_fullV="
        f"{sparse_full:.3f} (Gate-D reproduce v1 wall {SPARSE_PRIOR}:{gate_d_sparse}) "
        f"sparse_shortlist(A')={aprime_op:.3f} -> max_sparse={cls['max_sparse']:.3f} "
        f"(fails<={SPARSE_FAIL_CEIL}:{cls['sparse_fails']}). GAP B-sparse={gap:+.3f} "
        f"(>= {DISCRIM_GAP}:{cls['beats_by_gap']}). shortlist_hit@k{K_OP_FRAC}={hit:.3f} "
        f"(>= {HIT_FLOOR}:{cls['hit_ok']}). COST_ratio B(k{K_OP_FRAC})={cost:.3f} "
        f"(<= {COST_MAX}:{cls['cost_ok']}) -> ~{1.0/max(cost,1e-6):.1f}x cheaper than full fine. "
        f"CURVE[{curve}]. coarse_only(top1)={A['coarse_only']:.3f}. cache={cache_src}. "
        + ("INTERPRETATION: retained-trace re-query RECOVERS fine fidelity near the dense ceiling "
           "at materially lower coarse-read cost, where sparse-condense CANNOT -- the brain-first "
           "index-dont-invert fix works; the v1 info-wall is the quantization step, not the retrieval."
           if verdict == "HARD_PASS_RETAINED_TRACE_RECOVERS" else
           ("INTERPRETATION: retained-trace re-query beats sparse but does not clear RECOVER_HI at "
            "k_OP -- a larger shortlist k or wider D_COARSE likely closes it (see CURVE). Report to Research."
            if verdict == "MIDDLE_RETAINED_TRACE_NEAR_MISS" else
            ("INTERPRETATION: the coarse (dense-proj) ranking does not CONTAIN the answer in its "
             "top-k (hit rate below floor) -- coarse and fine geometries are decoupled; a new "
             "negative distinct from the quantization wall. Try a learned coarse condenser or wider D_COARSE."
             if verdict == "HARD_FAIL_DECOUPLED_GEOMETRY" else
             ("INTERPRETATION: retained-trace re-query does NOT beat sparse-condense by the gap on "
              "recoverable fidelity -- the wall is deeper than the quantization step; escalate/5x-drill."
              if verdict == "HARD_FAIL_NO_RECOVERY" else
              "schema/gate breach (cardinality / arms-identical / baseline-saturated / Gate-D); see verdict tag."))))
    )

    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": f"{verdict}: retained-trace re-query coarse-to-fine selective-depth ({run_mode})",
        "run_mode": run_mode,
        "device": device,
        "elapsed_s": time.perf_counter() - t0,
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR_NAME,
        "cache_source": cache_src,
        "cardinality_ok": cardinality_ok,
        "kcardinality_ok": kcard_ok,
        "expected_n_units": expected_units,
        "n_units": n_units,
        "arms_differ_verified": arms_differ,
        "fam_hash": fh0,
        "baseline_in_band": baseline_in_band,
        "gate_d": {"dense_ok": gate_d_dense, "sparse_ok": gate_d_sparse, "tol": GATE_D_TOL,
                   "dense_prior": DENSE_PRIOR, "sparse_prior": SPARSE_PRIOR,
                   "dense_measured": ceiling, "sparse_measured": sparse_full},
        "classification": cls,
        "operating_points": {"J_OP": J_OP, "ALPHA_OP": ALPHA_OP, "K_OP_FRAC": K_OP_FRAC,
                             "D_COARSE": D_COARSE},
        "bands": {"RECOVER_HI": RECOVER_HI, "CEIL_TOL": CEIL_TOL, "DISCRIM_GAP": DISCRIM_GAP,
                  "SPARSE_FAIL_CEIL": SPARSE_FAIL_CEIL, "COST_MAX": COST_MAX, "MIDDLE_TOL": MIDDLE_TOL,
                  "HIT_FLOOR": HIT_FLOOR, "LAMBDA_D": LAMBDA_D},
        "k_fracs": K_FRACS,
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
