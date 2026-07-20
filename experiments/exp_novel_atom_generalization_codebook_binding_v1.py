"""Novel-atom generalization: codebook feature-derived code + free FHRR binding + cleanup (v1).

THE GENUINE OPEN FRONTIER (brain-drill synthesis, see notes/research_brain_novel_atom_generalization_
fewshot_composition_2026-07-20.md). The compositional-gen VET (atom 29379, exp_compgen_binding_vs_flat_
learned_frontend_v1) proved native FHRR binding COMPOSES seen-filler role-filler combinations for free
(construction-determined), but a genuinely UNSEEN filler (never in the front-end's training identity set)
scored exactly 0.000 -- the learned front-end could only ID atoms it had seen. That 0.000 marks the real
open question: NOVEL-ATOM generalization. THIS cell is an INTEGRATION test of two already-separately-
validated pieces -- the learned CODEBOOK CG (exp_learned_codebook_generalization_gate_v1: feature/corpus-
derived codes that generalize to held-out relatedness judgments, AUC 0.927) + free-algebra FHRR binding
(29379's hybrid arm) -- NOT a re-run of either alone.

THE MECHANISM (3-scan brain-drill convergence, credited in full below):
  1. ENCODE a novel atom into the SAME structured space built from prior (seen-atom) experience --
     Prototypical Networks (Snell et al. 2017) / a-la-carte embeddings (Khodak et al. 2018) / DeViSE
     (Frome et al. 2013) analog: fit a linear induction map SEEN-atom (feature -> code) pairs only, apply
     it to a novel atom's own observed features. This is the nontrivial, nonfree part (hippocampal pattern
     separation is the brain's analog).
  2. BIND the derived code to its role -- FREE once encoded (fixed native FHRR bind, never trained,
     Smolensky 1990 / Plate 1995, already validated in 29379).
  3. CLEANUP/retrieve -- similarity-based (cosine argmax against the TRUE fixed code table, the "already-
     structured ground-truth space"); per the scan-3 discriminator this is where CONTENT (not just format)
     matters: a format-valid but content-free code (random arm) should decode at chance, a content-derived
     code should decode near the oracle ceiling.

ARMS (ONE variable = how the NOVEL atom's bound code is produced; seen-atom fillers ALWAYS bind their TRUE
code in every arm -- isolates the manipulation to exactly the novel-atom encoding step):
  codebook_derived   : ridge-regression induction map (fit on SEEN atoms' noisy-feature -> true-phase pairs
                       ONLY) applied FRESH to each novel-atom query's single noisy observation [genuine arm].
  handed_ceiling     : the atom's TRUE code, handed directly (free-binding CEILING control -- the
                       construction-determined algebra ceiling the genuine arm must APPROACH without being
                       handed; NOT the claim).
  memorize_prototype : front-end can only 1-NN-classify against SEEN prototypes (candidate set excludes the
                       novel atom entirely) -- reproduces 29379's exact 0.000 failure mode independently.
  flat_end_to_end    : a separate end-to-end MLP over raw scene features, output space = SEEN classes only
                       -- structurally CANNOT name a novel atom (guaranteed 0.000; should-fail arm).
  random_code        : an independent random unit-phasor FHRR code (fixed once per atom, uncorrelated with
                       features or the true code) -- format-only, no content (scan-3 content-control).

HARD_PASS = codebook_derived >> memorize_prototype(~0.000) AND >> flat_end_to_end(~0.000), APPROACHES
handed_ceiling, AND >> random_code (demonstrates CONTENT-generalization survives composition, not just
format). HARD_FAIL = codebook_derived collapses toward 0.000 (codebook imperfection doesn't survive
binding+cleanup) OR matches random_code (no genuine content-generalization). Watches hubness (does one
code dominate the argmax regardless of query) + domain-shift (derived-vs-true cosine) per scan-3.

PRIOR ART (credit; learn-from/build-on, never steal):
  - Prototypical Networks: Snell, Swersky & Zemel, NeurIPS 2017 (few-shot class prototype = mean of
    support embeddings in a FIXED metric space learned on base classes).
  - a-la-carte embeddings: Khodak, Saunshi, Liang, Ma, Stewart & Arora, ACL 2018 (linear induction function
    from context features to embedding space, fit on seen words, applied to novel/rare words).
  - DeViSE: Frome et al., NeurIPS 2013 (visual-semantic embedding induction for zero-shot labels).
  - Smolensky 1990 TPR; Plate 1995 HRR -- fixed content-agnostic binding operator (reused from 29379).
  - Kanerva 1988 / Sahlgren 2005 Random Indexing + Levy-Goldberg 2015 PPMI/SVD (credited via the codebook
    CG cell this integrates with: exp_learned_codebook_generalization_gate_v1).
  - Fast-mapping / CLS (McClelland et al. 1995): hippocampal one-shot indexing into pre-existing cortical
    structure -- the biological analog of "register a novel item into an already-structured space."
  - Greff, van Steenkiste & Schmidhuber 2020 construction-determinism critique (same lesson as atom 29369:
    codes must be random/task-agnostic, never derived to fit the split -- GUARD #1 below).
  - Reuses hdlab.binding.bind/unbind (native FHRR) + a vectorized reimplementation of hdlab.bundling.bundle
    (verified numerically equivalent, self-test) -- same pattern as exp_compgen_binding_vs_flat_learned_
    frontend_v1.py (29379), which this cell extends onto the novel-atom axis.

Pre-reg: preregs/2026-07-20_novel_atom_generalization_codebook_binding_v1.md

CELL-TEMPLATE MANDATORY: arms_differ hash-test (with declared exemption if codebook_derived reaches
bit-identical-to-ceiling accuracy); tmp_replace atomic metrics; except SystemExit: raise BEFORE except
Exception (no BaseException); crlb_n/a declared (closed-form chance floor documented); baseline_in_band
(ceiling-check sanity); discriminator survives scale (smoke = FULL params, option A); HARD_PASS strictly
above floor; cardinality gate; per-unit failure-class; fixed arithmetic seeds (no hash()/list(set())).

ASCII-only. No emojis. No em dashes.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import sys
import time
import traceback
from datetime import datetime, timezone

import numpy as np
import torch
import torch.nn as nn

ANCHOR_NAME = "exp_novel_atom_generalization_codebook_binding_v1"
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from hdlab.binding import bind, unbind  # noqa: E402
from hdlab.bundling import bundle  # noqa: E402

# --------------------------------------------------------------------------- task constants
N = 1024            # FHRR dim (CLAUDE.md default)
D_LATENT = 16        # shared latent factor that generates BOTH the true code and the feature prototype
D_FEAT = 24           # observable feature dim (matches 29379's D_OBS convention)
R = 6                 # roles per scene (matches 29379's R; well inside the m<=24 robust-bundle envelope)
F_SEEN = 24           # seen atom identities (the codebook / regression / memorize-front-end are trained on these ONLY)
F_NOVEL = 6           # genuinely novel atom identities (never in any training set)
F_TOTAL = F_SEEN + F_NOVEL
SEEN_IDX = list(range(F_SEEN))
NOVEL_IDX = list(range(F_SEEN, F_TOTAL))

OBS_SIGMA = 1.2       # per-exemplar observation noise std (CALIBRATED at smoke: see prereg -- sigma<1.0
                       # saturates codebook_derived to the 1.000 ceiling exactly (construction-trivial,
                       # doesn't test IMPERFECT codebook generalization surviving composition, the genuine
                       # open question); sigma>=2.0 collapses to chance. 1.2 sits in the genuinely-
                       # discriminating middle of a real, gradual (not cliff-shaped) accuracy curve.
K_SHOT = 5            # few-shot exemplars used to build SEEN prototypes for the memorize-prototype 1-NN front-end
K_TRAIN = 30          # per-SEEN-atom regression training exemplars (individual noisy draws, not just the mean)
RIDGE_ALPHA = 1.0      # fixed ridge regularization, declared before running (calibration_check: default_ok)

# Task-agnostic fixed seeds (GUARD #1: generated BEFORE any seen/novel split logic is applied)
Z_SEED = 3000
ACODE_SEED = 3001
BFEAT_SEED = 3002
ROLE_SEED = 1000
RANDOM_CODE_SEED_BASE = 5000

ARMS = ["codebook_derived", "handed_ceiling", "memorize_prototype", "flat_end_to_end", "random_code"]
SEEDS_FULL = [7, 13, 19]
SEEDS_SMOKE = [7, 13, 19]  # option A: smoke uses FULL params (cell is fast; verifies discriminator at full-N)

EVAL_SCENES_PER_NOVEL_FULL = 80
EVAL_SCENES_PER_NOVEL_SMOKE = 80
CEIL_CHECK_SCENES = 200          # seen-query ceiling sanity (shared across arms; TRUE-code path only)

FLAT_TRAIN_SCENES = 2000
FLAT_EPOCHS = 30
FLAT_LR = 1e-3
FLAT_BATCH = 128

CHANCE_FLOOR = 1.0 / F_TOTAL  # THEORETICAL closed-form: a content-free code has no special relation to any of the F_TOTAL true codes

# Pre-registered bands (declared BEFORE running; HYPOTHESIZED per generative-model analysis, see prereg).
HP_CODEBOOK_ACC_MIN = 0.60          # codebook_derived must clear this outright
HP_CODEBOOK_VS_RANDOM_MARGIN = 0.30  # and beat random_code by this much
HP_CODEBOOK_VS_CEILING_FRAC = 0.70   # and reach at least this fraction of the handed ceiling
HP_MEMORIZE_MAX = 0.02
HP_FLAT_MAX = 0.02
HF_CODEBOOK_FLOOR = 0.10             # collapse-toward-chance failure
HF_CODEBOOK_VS_RANDOM_MARGIN = 0.05  # "only matches random" failure
CEIL_CHECK_MIN = 0.90                # sanity: bind/bundle/unbind/cleanup mechanics must work at this R/F scale


# --------------------------------------------------------------------------- infra guards
def _write_start_marker(output_dir, run_mode, expected_n_units):
    marker = {
        "pid": os.getpid(),
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR_NAME,
        "run_mode": run_mode,
        "expected_n_units": expected_n_units,
        "host": platform.node(),
    }
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    final = os.path.join(output_dir, "_start_marker.json")
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(marker, fh)
    os.replace(tmp, final)


def _atomic_write_metrics(output_dir, metrics):
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(metrics, fh, indent=2)
    os.replace(tmp, final)


def _write_crash_metrics(output_dir, exc):
    diag = {
        "verdict": "CELL_CRASHED",
        "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
        "summary": f"CELL_CRASHED: {type(exc).__name__}",
        "elapsed_s": 0.0,
        "traceback": traceback.format_exc()[:5000],
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(),
        "anchor_name": ANCHOR_NAME,
    }
    _atomic_write_metrics(output_dir, diag)


def _hb(output_dir, msg):
    print(f"[hb] {msg}", flush=True)
    row = {"ts_iso": datetime.now(timezone.utc).isoformat(), "msg": msg}
    with open(os.path.join(output_dir, "_heartbeat.jsonl"), "a", encoding="utf-8") as fh:
        fh.write(json.dumps(row) + "\n")


# --------------------------------------------------------------------------- generative structure (GUARD #1)
def random_fhrr(n_vecs, dim, seed):
    """Unit-phasor FHRR codes. Fixed seed, TASK-AGNOSTIC: no split/label argument (GUARD #1)."""
    g = torch.Generator().manual_seed(seed)
    theta = (torch.rand(n_vecs, dim, generator=g) * 2 - 1) * float(np.pi)
    mag = torch.ones(n_vecs, dim)
    return torch.polar(mag, theta).to(torch.complex64)


def build_world():
    """Build the fixed generative structure: F_TOTAL atoms, each with a shared latent z_i that generates
    BOTH its true FHRR phase code and its feature prototype via two FIXED random linear maps. Generated
    entirely from task-agnostic seeds BEFORE SEEN_IDX/NOVEL_IDX (defined as module constants above, never
    tuned) are used anywhere (GUARD #1).
    """
    g_z = np.random.default_rng(Z_SEED)
    Z = g_z.standard_normal((F_TOTAL, D_LATENT)).astype(np.float64)
    g_a = np.random.default_rng(ACODE_SEED)
    A_CODE = g_a.standard_normal((D_LATENT, N)).astype(np.float64)
    g_b = np.random.default_rng(BFEAT_SEED)
    B_FEAT = g_b.standard_normal((D_LATENT, D_FEAT)).astype(np.float64)

    THETA = Z @ A_CODE          # (F_TOTAL, N) real phase, exact linear function of Z
    MU = Z @ B_FEAT              # (F_TOTAL, D_FEAT) noiseless feature prototype, exact linear function of Z

    true_codes = theta_to_phasor(THETA)
    # IMPORTANT: return the UNWRAPPED THETA itself (not re-derived via np.angle(true_codes), which wraps
    # to (-pi,pi] and would destroy the genuinely-linear z->theta relationship the induction map needs to
    # learn, since THETA's std ~4 rad routinely exceeds pi -- caught during smoke calibration).
    return true_codes, MU.astype(np.float32), THETA.astype(np.float64)


def _l2_or_unit_normalize_complex(z: torch.Tensor) -> torch.Tensor:
    """Normalize a complex tensor's last-dim-independent magnitudes to unit modulus (FHRR convention)."""
    mag = z.abs()
    mag = torch.where(mag > 1e-12, mag, torch.ones_like(mag))
    return z / mag.to(z.dtype)


# --------------------------------------------------------------------------- ridge induction map
def ridge_fit(X: np.ndarray, Y: np.ndarray, alpha: float) -> np.ndarray:
    """Closed-form ridge with bias augmentation. X:(n,d) Y:(n,m) -> W:(d+1,m)."""
    Xb = np.concatenate([X, np.ones((X.shape[0], 1), dtype=X.dtype)], axis=1)
    d1 = Xb.shape[1]
    A = Xb.T @ Xb + alpha * np.eye(d1, dtype=X.dtype)
    B = Xb.T @ Y
    return np.linalg.solve(A, B)


def ridge_predict(W: np.ndarray, X: np.ndarray) -> np.ndarray:
    Xb = np.concatenate([X, np.ones((X.shape[0], 1), dtype=X.dtype)], axis=1)
    return Xb @ W


def theta_to_phasor(theta: np.ndarray) -> torch.Tensor:
    """theta: (S,N) real -> (S,N) complex64 unit phasor (cos/sin wrap naturally; no clipping needed)."""
    c = np.cos(theta).astype(np.float32)
    s = np.sin(theta).astype(np.float32)
    return torch.complex(torch.from_numpy(c), torch.from_numpy(s)).to(torch.complex64)


# --------------------------------------------------------------------------- batched HD ops (verified vs hdlab in self_test)
def batched_bundle(stack: torch.Tensor) -> torch.Tensor:
    """(batch, k, n) -> (batch, n). Same per-component-magnitude-renorm formula as hdlab.bundling.bundle."""
    s = stack.sum(dim=1)
    mag = s.abs()
    mag = torch.where(mag > 0, mag, torch.ones_like(mag))
    return s / mag.to(s.dtype)


def decode_scenes(focal_codes: torch.Tensor, other_codes: torch.Tensor, role_codes: torch.Tensor,
                   true_codes_table: torch.Tensor) -> np.ndarray:
    """focal_codes:(S,N) complex64 (role0 filler code, varies by arm); other_codes:(S,R-1,N) complex64
    (TRUE codes of the other roles' SEEN fillers); role_codes:(R,N) fixed; true_codes_table:(F_TOTAL,N)
    fixed cleanup/decode target. Returns predicted index per scene (S,) via bind -> bundle -> unbind(role0)
    -> cosine-argmax cleanup against the FIXED TRUE code table. R_local/N_local inferred from shapes (not
    module globals) so this is reusable at any toy scale (self-test) as well as the FULL/smoke regime."""
    S = focal_codes.shape[0]
    n_dim = focal_codes.shape[-1]
    n_roles = role_codes.shape[0]
    all_fillers = torch.cat([focal_codes.unsqueeze(1), other_codes], dim=1)  # (S,R,N)
    role_codes_b = role_codes.unsqueeze(0).expand(S, n_roles, n_dim)
    bound = bind(role_codes_b, all_fillers)               # (S,R,N)
    scene = batched_bundle(bound)                          # (S,N)
    role0_b = role_codes[0].unsqueeze(0).expand(S, n_dim)
    unbound = unbind(scene, role0_b)                       # (S,N)
    sims = (unbound.unsqueeze(1).conj() * true_codes_table.unsqueeze(0)).sum(dim=-1).real  # (S,F_TOTAL)
    return sims.argmax(dim=-1).numpy()


# --------------------------------------------------------------------------- flat end-to-end arm
def make_flat_mlp(seed):
    torch.manual_seed(seed)
    return nn.Sequential(
        nn.Linear(R * D_FEAT + R, 128), nn.ReLU(),
        nn.Linear(128, 64), nn.ReLU(),
        nn.Linear(64, F_SEEN),
    )


def build_flat_scene_features(obs_all_roles: np.ndarray) -> np.ndarray:
    """(S,R_local,D_local) -> (S*R_local, R_local*D_local+R_local) role-blind-flattened-obs + one-hot
    query-role, per query role. R_local/D_local inferred from shape (reusable at toy scale in self-test)."""
    S, r_local, d_local = obs_all_roles.shape
    obs_flat = obs_all_roles.reshape(S, r_local * d_local)
    eye = np.eye(r_local, dtype=np.float32)
    obs_tiled = np.repeat(obs_flat[:, None, :], r_local, axis=1)
    query_onehot = np.repeat(eye[None, :, :], S, axis=0)
    X = np.concatenate([obs_tiled, query_onehot], axis=-1).reshape(S * r_local, r_local * d_local + r_local)
    return X.astype(np.float32)


def train_flat(model, X, y, seed, epochs=FLAT_EPOCHS, lr=FLAT_LR, batch=FLAT_BATCH):
    torch.manual_seed(seed)
    opt = torch.optim.Adam(model.parameters(), lr=lr)
    loss_fn = nn.CrossEntropyLoss()
    n = X.shape[0]
    gen = torch.Generator().manual_seed(seed)
    for _ep in range(epochs):
        perm = torch.randperm(n, generator=gen)
        for i in range(0, n, batch):
            idx = perm[i:i + batch]
            opt.zero_grad()
            out = model(X[idx])
            loss = loss_fn(out, y[idx])
            loss.backward()
            opt.step()
    return model


# --------------------------------------------------------------------------- per-seed unit
def run_one_seed(seed, true_codes, MU, THETA_all, role_codes, eval_scenes_per_novel, output_dir):
    rng = np.random.default_rng(seed)

    # 1. Ridge induction map: fit on SEEN atoms' noisy-feature -> TRUE-theta pairs ONLY. THETA_all is the
    # UNWRAPPED generating phase passed in from build_world() (NOT re-derived via np.angle(true_codes),
    # which wraps to (-pi,pi] and destroys the genuinely-linear z->theta relationship -- see build_world).
    X_train, Y_train = [], []
    for i in SEEN_IDX:
        for _k in range(K_TRAIN):
            obs = MU[i] + rng.normal(0, OBS_SIGMA, D_FEAT).astype(np.float32)
            X_train.append(obs)
            Y_train.append(THETA_all[i])
    X_train = np.stack(X_train).astype(np.float64)
    Y_train = np.stack(Y_train).astype(np.float64)
    W_ridge = ridge_fit(X_train, Y_train, RIDGE_ALPHA)

    # 2. SEEN prototypes (K_SHOT-averaged) for the memorize-prototype 1-NN front-end.
    seen_protos = np.zeros((F_SEEN, D_FEAT), dtype=np.float32)
    for j in SEEN_IDX:
        exemplars = MU[j] + rng.normal(0, OBS_SIGMA, (K_SHOT, D_FEAT)).astype(np.float32)
        seen_protos[j] = exemplars.mean(axis=0)

    # 3. Fixed random codes for the random_code (format-only) arm, one per novel atom, deterministic.
    random_codes_novel = {}
    for i in NOVEL_IDX:
        random_codes_novel[i] = random_fhrr(1, N, seed=RANDOM_CODE_SEED_BASE + seed * 100 + i)[0]

    # 4. Flat end-to-end MLP: trained on SEEN-only compositional scenes.
    obs_train = np.zeros((FLAT_TRAIN_SCENES, R, D_FEAT), dtype=np.float32)
    fillers_train = rng.integers(0, F_SEEN, size=(FLAT_TRAIN_SCENES, R))
    for s in range(FLAT_TRAIN_SCENES):
        for r in range(R):
            obs_train[s, r] = MU[fillers_train[s, r]] + rng.normal(0, OBS_SIGMA, D_FEAT).astype(np.float32)
    Xflat = torch.from_numpy(build_flat_scene_features(obs_train))
    yflat = torch.from_numpy(fillers_train.reshape(-1).astype(np.int64))
    flat_model = make_flat_mlp(seed=90000 + seed)
    train_flat(flat_model, Xflat, yflat, seed=90000 + seed)

    # 5. Ceiling-check sanity: SEEN-atom queries, TRUE code path, shared across arms (mechanics validity).
    ceil_focal_idx = rng.integers(0, F_SEEN, size=CEIL_CHECK_SCENES)
    ceil_other_idx = rng.integers(0, F_SEEN, size=(CEIL_CHECK_SCENES, R - 1))
    ceil_focal_codes = true_codes[ceil_focal_idx]
    ceil_other_codes = true_codes[torch.from_numpy(ceil_other_idx)]
    ceil_preds = decode_scenes(ceil_focal_codes, ceil_other_codes, role_codes, true_codes)
    ceil_acc = float((ceil_preds == ceil_focal_idx).mean())

    # 6. Per-arm novel-query evaluation. Same per-scene (obs_focal, other_fillers, other_obs) draws are
    #    reused across all HD arms AND the flat arm for a matched, apples-to-apples comparison (removes
    #    noise-draw as a confound; ONE variable = how the novel atom's bound code / prediction is produced).
    per_arm_acc = {}
    per_arm_preds = {}
    per_atom_diag = {}  # domain-shift / hubness diagnostics for codebook_derived

    # build once per novel atom (shared scene draws reused across ALL arms -- removes noise-draw confound)
    novel_scene_cache = {}
    for i in NOVEL_IDX:
        obs_focal = MU[i] + rng.normal(0, OBS_SIGMA, (eval_scenes_per_novel, D_FEAT)).astype(np.float32)
        other_idx = rng.integers(0, F_SEEN, size=(eval_scenes_per_novel, R - 1))
        other_obs = np.zeros((eval_scenes_per_novel, R - 1, D_FEAT), dtype=np.float32)
        for r in range(R - 1):
            other_obs[:, r] = MU[other_idx[:, r]] + rng.normal(0, OBS_SIGMA, (eval_scenes_per_novel, D_FEAT))
        novel_scene_cache[i] = (obs_focal, other_idx, other_obs)

    for arm in ARMS:
        n_correct = 0
        n_total = 0
        preds_all = []
        for i in NOVEL_IDX:
            obs_focal, other_idx, other_obs = novel_scene_cache[i]
            S = obs_focal.shape[0]
            other_codes = true_codes[torch.from_numpy(other_idx)]  # (S,R-1,N)

            if arm == "handed_ceiling":
                focal_codes = true_codes[i].unsqueeze(0).expand(S, N).clone()
                preds = decode_scenes(focal_codes, other_codes, role_codes, true_codes)
            elif arm == "random_code":
                focal_codes = random_codes_novel[i].unsqueeze(0).expand(S, N).clone()
                preds = decode_scenes(focal_codes, other_codes, role_codes, true_codes)
            elif arm == "codebook_derived":
                theta_hat = ridge_predict(W_ridge, obs_focal.astype(np.float64))  # (S,N)
                focal_codes = theta_to_phasor(theta_hat)
                preds = decode_scenes(focal_codes, other_codes, role_codes, true_codes)
                cos_true = (focal_codes.conj() * true_codes[i].unsqueeze(0)).sum(dim=-1).real.mean().item() / N
                # rank of the TRUE novel code within the derived code's similarity ranking (domain-shift/hubness)
                sims_diag = (focal_codes.unsqueeze(1).conj() * true_codes.unsqueeze(0)).sum(dim=-1).real
                ranks = (sims_diag.argsort(dim=-1, descending=True) == i).float().argmax(dim=-1)
                per_atom_diag[str(i)] = {
                    "mean_cos_derived_vs_true": cos_true,
                    "mean_rank_of_true_in_similarity": float(ranks.float().mean().item()),
                }
            elif arm == "memorize_prototype":
                dists = np.linalg.norm(obs_focal[:, None, :] - seen_protos[None, :, :], axis=-1)  # (S,F_SEEN)
                j_star = dists.argmin(axis=-1)
                focal_codes = true_codes[torch.from_numpy(j_star)]
                preds = decode_scenes(focal_codes, other_codes, role_codes, true_codes)
            elif arm == "flat_end_to_end":
                obs_all = np.concatenate([obs_focal[:, None, :], other_obs], axis=1)  # (S,R,D_FEAT), focal=role0
                Xf = torch.from_numpy(build_flat_scene_features(obs_all)).reshape(S, R, -1)
                # query role0 only (the focal role)
                Xf0 = Xf[:, 0, :]
                with torch.no_grad():
                    logits = flat_model(Xf0)
                preds = logits.argmax(dim=-1).numpy()
                assert preds.max() < F_SEEN <= i, (
                    "STRUCTURAL_GUARANTEE_VIOLATED: flat_end_to_end output space must exclude novel index")
            else:
                raise ValueError(f"unknown arm {arm!r}")

            correct = (preds == i)
            n_correct += int(correct.sum())
            n_total += S
            preds_all.append(preds)
        per_arm_acc[arm] = n_correct / n_total if n_total else float("nan")
        per_arm_preds[arm] = np.concatenate(preds_all)

    return {
        "seed": seed,
        "ceiling_check_seen_query_acc": ceil_acc,
        "per_arm_acc": per_arm_acc,
        "per_arm_preds_hash": {a: hashlib.sha256(p.tobytes()).hexdigest() for a, p in per_arm_preds.items()},
        "per_arm_preds_raw": per_arm_preds,
        "novel_atom_diagnostics": per_atom_diag,
    }


# --------------------------------------------------------------------------- runner
def run(output_dir, seeds, eval_scenes_per_novel):
    t0 = time.perf_counter()
    expected_n_units = len(seeds) * len(ARMS)
    run_mode = os.path.basename(output_dir)
    _write_start_marker(output_dir, run_mode, expected_n_units)

    true_codes, MU, THETA_all = build_world()
    role_codes = random_fhrr(R, N, seed=ROLE_SEED)
    _hb(output_dir, f"world built: F_TOTAL={F_TOTAL} (seen={F_SEEN} novel={F_NOVEL}) R={R} N={N}")

    per_unit = {}
    per_seed_results = {}
    n_units_done = 0
    seed_pred_hashes = {}  # for arms_differ check

    for seed in seeds:
        try:
            res = run_one_seed(seed, true_codes, MU, THETA_all, role_codes, eval_scenes_per_novel, output_dir)
            per_seed_results[seed] = res
            seed_pred_hashes[seed] = res["per_arm_preds_hash"]
            for arm in ARMS:
                unit_key = f"{arm}__seed{seed}"
                per_unit[unit_key] = {
                    "arm": arm, "seed": seed,
                    "novel_query_acc": res["per_arm_acc"][arm],
                    "failure_class": None,
                }
                n_units_done += 1
            _hb(output_dir, f"seed={seed}: ceiling={res['ceiling_check_seen_query_acc']:.3f} "
                             f"per_arm={ {a: round(v, 3) for a, v in res['per_arm_acc'].items()} }")
        except Exception as e:  # NOT BaseException; per-unit failure-class (META_RULE_J)
            for arm in ARMS:
                unit_key = f"{arm}__seed{seed}"
                per_unit[unit_key] = {"arm": arm, "seed": seed,
                                       "failure_class": f"{type(e).__name__}: {str(e)[:200]}"}
            _hb(output_dir, f"seed={seed}: FAILED {type(e).__name__}: {e}")

    cardinality_ok = (n_units_done == expected_n_units)

    # ARMS-MUST-DIFFER (META_RULE_AF), with a declared, verified exemption when codebook_derived reaches
    # bit-identical-to-ceiling performance (a GOOD outcome, not a bug -- only exempted if BOTH near-ceiling).
    arms_differ = True
    arms_differ_detail = {}
    arms_differ_exempted = []
    for seed, hd in seed_pred_hashes.items():
        pairs = [(a, b) for a in ARMS for b in ARMS if a < b]
        for a, b in pairs:
            key = f"seed{seed}__{a}_vs_{b}"
            same = hd[a] == hd[b]
            arms_differ_detail[key] = not same
            if same:
                acc_a = per_seed_results[seed]["per_arm_acc"][a]
                acc_b = per_seed_results[seed]["per_arm_acc"][b]
                if acc_a > 0.95 and acc_b > 0.95:
                    arms_differ_exempted.append({"seed": seed, "pair": [a, b],
                                                  "rationale": "both near-ceiling accuracy; identical "
                                                                "predictions indicates ceiling-matching "
                                                                "performance, not an implementation bug",
                                                  "acc_a": acc_a, "acc_b": acc_b})
                else:
                    arms_differ = False

    # Aggregate means over seeds.
    def _m(vals):
        return float(np.mean(vals)) if vals else float("nan")

    arm_summary = {}
    for arm in ARMS:
        vals = [per_seed_results[s]["per_arm_acc"][arm] for s in seeds if s in per_seed_results]
        arm_summary[arm] = {"acc_mean": _m(vals), "acc_std": float(np.std(vals)) if len(vals) > 1 else 0.0,
                             "n_seeds": len(vals)}
    ceil_vals = [per_seed_results[s]["ceiling_check_seen_query_acc"] for s in seeds if s in per_seed_results]
    ceiling_check_mean = _m(ceil_vals)

    codebook_acc = arm_summary["codebook_derived"]["acc_mean"]
    ceiling_acc = arm_summary["handed_ceiling"]["acc_mean"]
    memorize_acc = arm_summary["memorize_prototype"]["acc_mean"]
    flat_acc = arm_summary["flat_end_to_end"]["acc_mean"]
    random_acc = arm_summary["random_code"]["acc_mean"]

    baseline_in_band = ceiling_check_mean >= CEIL_CHECK_MIN

    discriminator_fires = (
        baseline_in_band
        and memorize_acc <= 0.05 and flat_acc <= 0.05
        and abs(random_acc - CHANCE_FLOOR) <= 0.10
    )

    codebook_vs_random_margin = codebook_acc - random_acc
    codebook_vs_ceiling_frac = (codebook_acc / ceiling_acc) if ceiling_acc > 1e-9 else 0.0

    # Verdict logic.
    if not cardinality_ok:
        verdict = "HARD_FAIL_CARDINALITY_BREACH_META_RULE_H"
    elif not arms_differ:
        verdict = "HARD_FAIL_ARMS_IDENTICAL_META_RULE_AF"
    elif not baseline_in_band:
        verdict = "HARD_FAIL_MECHANICS_SANITY_CEILING_CHECK_BELOW_BAND"
    elif memorize_acc > HP_MEMORIZE_MAX + 0.05 or flat_acc > HP_FLAT_MAX + 0.05:
        verdict = "MIDDLE_BAND_BASELINE_ARMS_NOT_AT_STRUCTURAL_FLOOR"
    elif codebook_acc <= HF_CODEBOOK_FLOOR or codebook_vs_random_margin <= HF_CODEBOOK_VS_RANDOM_MARGIN:
        verdict = "HARD_FAIL_NOVEL_ATOM_CODEBOOK_DOES_NOT_SURVIVE_COMPOSITION"
    elif (codebook_acc >= HP_CODEBOOK_ACC_MIN
          and codebook_vs_random_margin >= HP_CODEBOOK_VS_RANDOM_MARGIN
          and codebook_vs_ceiling_frac >= HP_CODEBOOK_VS_CEILING_FRAC
          and memorize_acc <= HP_MEMORIZE_MAX and flat_acc <= HP_FLAT_MAX):
        verdict = "HARD_PASS"
    else:
        verdict = "MIDDLE_BAND"

    elapsed = time.perf_counter() - t0
    verdict_msg = (
        f"codebook_derived={codebook_acc:.3f} handed_ceiling={ceiling_acc:.3f} "
        f"memorize_prototype={memorize_acc:.3f} flat_end_to_end={flat_acc:.3f} random_code={random_acc:.3f} "
        f"(chance={CHANCE_FLOOR:.3f}) | codebook_vs_random_margin={codebook_vs_random_margin:.3f} "
        f"codebook_vs_ceiling_frac={codebook_vs_ceiling_frac:.3f} | ceiling_check(seen)={ceiling_check_mean:.3f} "
        f"| discriminator_fires={discriminator_fires} | cardinality_ok={cardinality_ok} "
        f"({n_units_done}/{expected_n_units}) arms_differ={arms_differ}"
    )

    # Prune raw pred arrays (not JSON-serializable-friendly at scale) before writing metrics.
    novel_atom_diag_by_seed = {}
    for s in seeds:
        if s in per_seed_results:
            novel_atom_diag_by_seed[str(s)] = per_seed_results[s]["novel_atom_diagnostics"]

    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": f"{verdict}: {verdict_msg[:220]}",
        "elapsed_s": elapsed,
        "anchor_name": ANCHOR_NAME,
        "run_mode": run_mode,
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "config": {
            "N": N, "D_LATENT": D_LATENT, "D_FEAT": D_FEAT, "R": R,
            "F_SEEN": F_SEEN, "F_NOVEL": F_NOVEL, "F_TOTAL": F_TOTAL,
            "OBS_SIGMA": OBS_SIGMA, "K_SHOT": K_SHOT, "K_TRAIN": K_TRAIN, "RIDGE_ALPHA": RIDGE_ALPHA,
            "seeds": seeds, "eval_scenes_per_novel": eval_scenes_per_novel,
            "flat_train_scenes": FLAT_TRAIN_SCENES, "flat_epochs": FLAT_EPOCHS,
        },
        "arm_summary": arm_summary,
        "ceiling_check_seen_query_acc_mean": ceiling_check_mean,
        "per_unit": per_unit,
        "novel_atom_diagnostics_by_seed": novel_atom_diag_by_seed,
        "bands": {
            "HP_CODEBOOK_ACC_MIN": HP_CODEBOOK_ACC_MIN, "HP_CODEBOOK_VS_RANDOM_MARGIN": HP_CODEBOOK_VS_RANDOM_MARGIN,
            "HP_CODEBOOK_VS_CEILING_FRAC": HP_CODEBOOK_VS_CEILING_FRAC, "HP_MEMORIZE_MAX": HP_MEMORIZE_MAX,
            "HP_FLAT_MAX": HP_FLAT_MAX, "HF_CODEBOOK_FLOOR": HF_CODEBOOK_FLOOR,
            "HF_CODEBOOK_VS_RANDOM_MARGIN": HF_CODEBOOK_VS_RANDOM_MARGIN, "CEIL_CHECK_MIN": CEIL_CHECK_MIN,
            "CHANCE_FLOOR": CHANCE_FLOOR,
        },
        "cardinality_ok": cardinality_ok,
        "expected_n_units": expected_n_units,
        "n_units_done": n_units_done,
        "arms_differ_verified": arms_differ,
        "arms_differ_detail": arms_differ_detail,
        "arms_differ_exempted": arms_differ_exempted,
        "discriminator_fires": discriminator_fires,
        "baseline_in_band": baseline_in_band,
        "guard1_role_codes_and_world_task_agnostic": True,
        "crlb_n/a": f"classification-accuracy generalization over F_TOTAL={F_TOTAL} discrete atoms; "
                    f"closed-form chance floor = 1/F_TOTAL = {CHANCE_FLOOR:.4f} (THEORETICAL)",
        "prior_art": "Snell2017 ProtoNet; Khodak2018 a-la-carte; Frome2013 DeViSE; Smolensky1990 TPR; "
                     "Plate1995 HRR; Kanerva1988/Sahlgren2005 RI; LevyGoldberg2015 PPMI-SVD; "
                     "McClelland1995 CLS; GreffVanSteensteSchmidhuber2020",
        "integration_of": ["exp_learned_codebook_generalization_gate_v1 (codebook CG)",
                            "exp_compgen_binding_vs_flat_learned_frontend_v1 / atom 29379 (free-algebra binding + 0.000 baseline)"],
    }
    _atomic_write_metrics(output_dir, metrics)
    print(f"\n[VERDICT] {verdict}\n{verdict_msg}\nelapsed={elapsed:.1f}s -> {output_dir}/metrics.json", flush=True)
    return metrics


# --------------------------------------------------------------------------- self-test
def self_test():
    """Fast real-code-path self-test at tiny scale: exercises the REAL builders (no synthetic-only branch)."""
    print("[self-test] GUARD #1: random_fhrr takes no split/label argument", flush=True)
    import inspect
    sig = inspect.signature(random_fhrr)
    assert list(sig.parameters.keys()) == ["n_vecs", "dim", "seed"], (
        f"random_fhrr carries extra params: {list(sig.parameters.keys())} -- GUARD #1 violated")

    print("[self-test] positive control: batched_bundle == hdlab.bundling.bundle", flush=True)
    torch.manual_seed(0)
    theta = torch.rand(3, 8) * 2 * float(np.pi) - float(np.pi)
    stack = torch.polar(torch.ones(3, 8), theta).to(torch.complex64)
    ref = bundle(stack)
    fast = batched_bundle(stack.unsqueeze(0)).squeeze(0)
    assert torch.allclose(ref, fast, atol=1e-5), f"batched_bundle diverges: max|diff|={(ref - fast).abs().max()}"

    print("[self-test] positive control: bind-then-unbind exact round trip", flush=True)
    rc = random_fhrr(2, 32, seed=ROLE_SEED)
    fc = random_fhrr(3, 32, seed=RANDOM_CODE_SEED_BASE)
    b = bind(rc[0], fc[1])
    rec = unbind(b, rc[0])
    cos = (rec.conj() * fc[1]).sum().real / 32
    assert cos > 0.99, f"FHRR bind/unbind round trip failed: cos={cos:.4f}"

    print("[self-test] real_code_path: exercising REAL world-builder + ridge + decode at tiny scale", flush=True)
    # Tiny toy world (small N/F/D so this runs in well under a second).
    tiny_N, tiny_Flatent, tiny_Dfeat = 64, 4, 6
    g_z = np.random.default_rng(1)
    Z = g_z.standard_normal((8, tiny_Flatent))
    g_a = np.random.default_rng(2)
    A = g_a.standard_normal((tiny_Flatent, tiny_N))
    g_b = np.random.default_rng(3)
    B = g_b.standard_normal((tiny_Flatent, tiny_Dfeat))
    THETA = Z @ A
    MU = (Z @ B).astype(np.float32)
    true_codes_tiny = theta_to_phasor(THETA)
    assert true_codes_tiny.shape == (8, tiny_N)
    mags = true_codes_tiny.abs()
    assert torch.allclose(mags, torch.ones_like(mags), atol=1e-4), "true codes not unit modulus"

    rng = np.random.default_rng(7)
    X_train, Y_train = [], []
    for i in range(6):  # 6 "seen", 2 "novel" in this toy
        for _ in range(10):
            obs = MU[i] + rng.normal(0, 0.3, tiny_Dfeat)
            X_train.append(obs)
            Y_train.append(THETA[i])
    W = ridge_fit(np.stack(X_train), np.stack(Y_train), alpha=1.0)
    assert W.shape == (tiny_Dfeat + 1, tiny_N)
    # apply to a "novel" atom's (index 6) fresh observation; derived code should correlate with truth
    # much better than a random draw (real_code_path: exercises the SAME regression fn used at FULL).
    obs_novel = (MU[6] + rng.normal(0, 0.3, (5, tiny_Dfeat))).astype(np.float64)
    theta_hat = ridge_predict(W, obs_novel)
    derived = theta_to_phasor(theta_hat)
    cos_true = (derived.conj() * true_codes_tiny[6].unsqueeze(0)).sum(dim=-1).real.mean().item() / tiny_N
    rand_code = random_fhrr(1, tiny_N, seed=999)[0]
    cos_rand = (rand_code.conj() * true_codes_tiny[6]).sum().real.item() / tiny_N
    assert cos_true > cos_rand, (
        f"toy sanity failed: derived-code cosine ({cos_true:.4f}) should exceed an unrelated random "
        f"code's cosine ({cos_rand:.4f}) against the true novel code")

    print("[self-test] real_code_path: exercising decode_scenes (bind+bundle+unbind+cleanup)", flush=True)
    tiny_role_codes = random_fhrr(3, tiny_N, seed=ROLE_SEED)
    focal = true_codes_tiny[6].unsqueeze(0).expand(4, tiny_N).clone()
    other = true_codes_tiny[torch.tensor([[0, 1], [1, 2], [0, 2], [2, 0]])]
    preds = decode_scenes(focal, other, tiny_role_codes, true_codes_tiny)
    assert preds.shape == (4,)
    assert (preds == 6).all(), f"handed-code decode should be exact on a clean toy world: preds={preds}"

    print("[self-test] real_code_path: exercising flat MLP builder + train (tiny)", flush=True)
    obs_all = np.zeros((4, 3, tiny_Dfeat), dtype=np.float32)
    for s in range(4):
        for r in range(3):
            obs_all[s, r] = MU[rng.integers(0, 6)]
    Xf = build_flat_scene_features(obs_all)
    assert Xf.shape == (4 * 3, 3 * tiny_Dfeat + 3)

    print(f"[self-test] PASS: toy cos_true={cos_true:.4f} cos_rand={cos_rand:.4f} handed-decode all-correct",
          flush=True)


# --------------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--device", default="cpu")  # CPU-only cell; accept-and-ignore for runner parity
    args, _ = ap.parse_known_args()

    if args.self_test:
        self_test()
        sys.exit(0)

    if args.smoke:
        output_dir = os.path.join(REPO, "data", ANCHOR_NAME + "_smoke")
        run(output_dir, SEEDS_SMOKE, EVAL_SCENES_PER_NOVEL_SMOKE)
    else:
        output_dir = os.path.join(REPO, "data", ANCHOR_NAME)
        run(output_dir, SEEDS_FULL, EVAL_SCENES_PER_NOVEL_FULL)
    sys.exit(0)


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        _out = os.path.join(REPO, "data", ANCHOR_NAME + "_selftest")
    elif "--smoke" in sys.argv:
        _out = os.path.join(REPO, "data", ANCHOR_NAME + "_smoke")
    else:
        _out = os.path.join(REPO, "data", ANCHOR_NAME)
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # NOT BaseException
        _write_crash_metrics(_out, e)
        raise
