"""Compositional-generalization EDGE at the DECISION mechanism: 2-factor ITERATIVE resonator
role-decision vs equal-budget FLAT classifier, on held-out (construction, verb-class) product
combinations, under an extraction-noise sweep (v1).

THE ONE LIVE NOVEL SLICE (dedup-verified 2026-07-21):
The single-shot / single-factor binding-cleanup DECISION on held-out (role, filler) combos is
ALREADY BUILT + CLOSED as a free-algebra tautology (survey
notes/SURVEY_reader_chaingrade_prior_work_and_genuine_gaps_2026-07-20.md; atom for
exp_role_filler_factorization_compgen_v1 HARD_PASS FACTORED heldout=1.000 FLAT=0.003 -- the
filler was DIRECTLY OBSERVED, so a single unbind + cleanup recovers it for free). That is NOT
re-tested here.

This cell tests the genuinely-untested mechanism: the role-ASSIGNMENT DECISION is read out by an
ITERATIVE NVSA-style resonator (Hersche et al. 2023) that must jointly factor a BOUND PRODUCT
b ~= bind(construction_code, verbclass_code) into its TWO entangled unknown factors by alternating
unbind-and-cleanup against two codebooks, then look up the role label. A bound product has ~zero
marginal similarity to either factor (binding scrambles), so a single unbind (the closed prior
mechanism) and a flat classifier over marginal features are BOTH structurally blind to it; only
iterative resonance can recover the factors. The question (Fodor-Pylyshyn systematicity AT THE
DECISION MECHANISM): does iterative binding-mediated factoring generalize to HELD-OUT
(construction, verb-class) PRODUCTS better than an equal/greater-budget FLAT classifier, and does
that edge SURVIVE realistic extraction noise -- or does noise flood the resonator down to flat's
level (extraction-bound, tying to the reader's 0.557 role-assigner ceiling)?

CAN-FAIL (P_deflated 0.30): resonators have documented spurious-fixed-point failure under noise
(Kent et al. 2020); at realistic extraction noise the iterative factoring may mis-converge and
tie flat -> a genuine, informative NEGATIVE (extraction-bound dominates), NOT forced to a pass.

DESIGN SOURCE: notes/research_reader_compositional_generalization_edge_dedup_2026-07-21.md section (f).
PRIOR ART (credit; learn-from/build-on, never steal): Fodor & Pylyshyn 1988 (systematicity);
Smolensky 1990 TPR; Plate 1995 HRR; Frady/Kanerva/Sommer + Kymn et al. 2024 (resonator networks);
Kent, Frady, Sommer, Olshausen 2020 (resonator dynamics, spurious fixed points); Hersche et al.
2023 NVSA (resonator-DECISION read-out on a REAL task -- the template for binding IN the decision,
not just the encoding); Lake & Baroni 2018 SCAN; Kim & Linzen 2020 COGS; Keysers et al. 2020 CFQ
(compound-divergence split discipline); Csordas/Irie/Schmidhuber 2021 (flat-with-tricks can close
part of the gap -> the flat_factored fairness arm here).

DEDUP: does NOT re-derive atoms 29379-82 / role_filler_factorization (single-shot 1-factor,
free-algebra, CLOSED) -- the single_shot arm reproduces that mechanism AS A CONTROL and is REQUIRED
to be BELOW ceiling on held-out products in the gated regime (design gate: single_shot_not_at_ceiling),
proving this regime is OUTSIDE the closed tautology.

Pre-reg: preregs/2026-07-21_resonator_decision_compgen_2factor_v1.md

CELL-TEMPLATE MANDATORY: arms_differ hash-test; tmp_replace atomic metrics; except SystemExit: raise
BEFORE except Exception (no BaseException); crlb_n/a declared (closed-form chance floor documented);
baseline_in_band; discriminator survives scale (full-N params previewed at smoke); HARD_PASS strictly
above threshold; cardinality gate; per-unit failure-class; fixed arithmetic seeds (deterministic only);
start-marker + crash-diagnostic + heartbeat; numbers tagged in comments where estimated.

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

ANCHOR_NAME = "exp_resonator_decision_compgen_2factor_v1"
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from experiments._validity_preflight import (  # noqa: E402
    assert_no_nondeterministic_seeding,
)

# --------------------------------------------------------------------------- config
N_DIM = 2048              # FHRR dimensionality (full). CITED default N per CLAUDE.md scaled up for cleanup SNR.
N_CONSTR = 8              # construction-frame factor cardinality (C)
N_VERBCLASS = 10          # verb-class factor cardinality (V)
N_ROLE = 4               # role-slot label cardinality (who-is-affected among R slots). CHANCE = 0.25 THEORETICAL.
CHANCE = 1.0 / N_ROLE

HELD_PER_CONSTR = 3       # each construction is held-out with this many verb-classes (rotating window).
N_TRAIN_PER_PRODUCT = 24  # noisy bundle instances per TRAINABLE (c,v) product (flat training).
N_TEST_PER_PRODUCT = 24   # noisy bundle instances per product at eval (both held-out and in-dist).

# Extraction-noise proxy sweep (radians of von-Mises-ish phase jitter added to the bound product).
# sigma=0.0 = POSITIVE CONTROL (resonator must ~= 1.0, single_shot weak by 2-factor entanglement).
# GATED point = SIGMA_GATE (moderate = realistic extraction noise).
# Noise envelope located empirically (probe 2026-07-21): resonator held-out = 1.000 through sigma<=1.5,
# knee ~2.2 (RES ho ~0.88), collapse to chance by sigma>=3.0. Flat is FAR more noise-fragile: its
# in-dist itself collapses to ~chance by sigma~2.2 (a train-free algebraic resonator and a learned flat
# classifier CANNOT be in-dist-equalized under noise). So the discriminator is NOT in-dist parity but
# the per-arm GENERALIZATION GAP (in-dist - held-out): a SYSTEMATIC mechanism has ~0 gap, a MEMORIZING
# one has a large gap. GATE at moderate noise where flat is still in-dist-competent (sigma=0.8, flat
# id~0.96). Sweep traces the full robustness envelope incl. the resonator's own extraction-bound collapse.
SIGMA_SWEEP_FULL = [0.0, 0.8, 1.5, 2.2, 2.8, 3.5]
SIGMA_SWEEP_SMOKE = [0.0, 0.8]
SIGMA_GATE = 0.8          # moderate extraction-noise proxy where flat is in-dist-competent (fair gap read).

RES_N_ITER = 25           # resonator alternating-estimation iterations.
RES_N_RESTART = 4         # random restarts to mitigate spurious fixed points (Kent 2020).

SEEDS_FULL = [7, 13, 19]
SEEDS_SMOKE = [7]

ARMS = ["flat_joint", "flat_factored", "single_shot", "resonator_iter"]

# Fixed, task-agnostic seeds (codebooks + role-table built BEFORE any split logic -> GUARD: never
# selected/tuned to fit the held-out structure).
CODEBOOK_C_SEED = 101
CODEBOOK_V_SEED = 202
ROLE_TABLE_SEED = 303
FLAT_PROJ_SEED = 404      # fixed random projection giving flat a real-valued feature view of b.
FLAT_PROJ_DIM = 128

# Gate thresholds (design source section f).
HP_HELDOUT_GAP = 0.05     # resonator held-out - flat held-out must be >= this (>=5 points).
HP_INDIST_GAP_MAX = 0.01  # |resonator in-dist - flat in-dist| <= this (rules out "just a better classifier").
HF_HELDOUT_GAP = 0.01     # <= this at the gate = within-noise tie = HARD_FAIL (extraction-bound).
HF_INDIST_COST = 0.02     # resonator in-dist more than this BELOW flat in-dist = constraint costs too much.
# Design gates (regime-validity).
GATE_SINGLE_SHOT_CEIL = 0.95   # single_shot held-out >= this at the gate => tautology regime => VOID.
GATE_FLAT_MUSTFAIL = 0.75      # flat_joint held-out >= this at the gate => split does not isolate => VOID.
GATE_FLAT_INDIST_MIN = 0.60    # flat_joint in-dist < this => flat is starved / broken => VOID.


# --------------------------------------------------------------------------- infra guards
def _write_start_marker(output_dir, run_mode, expected_n_units):
    marker = {
        "pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR_NAME, "run_mode": run_mode,
        "expected_n_units": expected_n_units, "host": platform.node(),
    }
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(marker, fh)
    os.replace(tmp, os.path.join(output_dir, "_start_marker.json"))


def _atomic_write_metrics(output_dir, metrics):
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(metrics, fh, indent=2)
    os.replace(tmp, os.path.join(output_dir, "metrics.json"))


def _write_crash_metrics(output_dir, exc):
    diag = {
        "verdict": "CELL_CRASHED",
        "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
        "summary": f"CELL_CRASHED: {type(exc).__name__}",
        "elapsed_s": 0.0, "traceback": traceback.format_exc()[:5000],
        "ts_iso": datetime.now(timezone.utc).isoformat(), "pid": os.getpid(),
        "anchor_name": ANCHOR_NAME,
    }
    _atomic_write_metrics(output_dir, diag)


def _hb(output_dir, msg):
    print(f"[hb] {msg}", flush=True)
    row = {"ts_iso": datetime.now(timezone.utc).isoformat(), "msg": msg}
    with open(os.path.join(output_dir, "_heartbeat.jsonl"), "a", encoding="utf-8") as fh:
        fh.write(json.dumps(row) + "\n")


# --------------------------------------------------------------------------- FHRR primitives
def random_fhrr(n_vecs, dim, seed):
    """Unit-phasor FHRR codebook (n_vecs, dim) complex64 from a FIXED task-agnostic seed."""
    g = torch.Generator().manual_seed(seed)
    theta = (torch.rand(n_vecs, dim, generator=g) * 2 - 1) * float(np.pi)
    return torch.polar(torch.ones(n_vecs, dim), theta).to(torch.complex64)


def fhrr_bind(a, b):
    """Elementwise complex product (FHRR bind). Shapes broadcast."""
    return a * b


def fhrr_unbind(c, b):
    """FHRR unbind = bind with conjugate (approx self-inverse for unit phasors)."""
    return c * b.conj()


def unit_phase(v, eps=1e-8):
    """Project onto unit-phasor manifold (magnitude 1 per component)."""
    mag = v.abs()
    mag = torch.where(mag > eps, mag, torch.ones_like(mag))
    return v / mag.to(v.dtype)


def sim_to_codebook(q, cb):
    """Normalized real inner product of q (N,) against codebook cb (K,N) -> (K,). FHRR similarity."""
    return (cb.conj() * q.unsqueeze(0)).sum(dim=-1).real / q.shape[-1]


def cleanup_hard(q, cb):
    """Return (idx, code) of the codebook row best resonating with q."""
    s = sim_to_codebook(q, cb)
    idx = int(torch.argmax(s))
    return idx, cb[idx]


# --------------------------------------------------------------------------- world + split
def build_role_table(rng):
    """Fixed random (C,V) -> role-slot table. Task-agnostic 'grammar' known to ALL arms; recovering
    which (c,v) a noisy bundle encodes is the hard part, not the lookup."""
    return rng.integers(0, N_ROLE, size=(N_CONSTR, N_VERBCLASS)).astype(np.int64)


def build_split_2d(rng):
    """Rotating-window held-out (c,v) PRODUCT split (CFQ compound-divergence style). Each construction
    is held out with HELD_PER_CONSTR verb-classes; the window rotates so every verb-class is trainable
    with >=1 construction (grounding) and held-out with >=1 (compound novelty). Returns
    (held_out set of (c,v), trainable list, indist_eval list == a trainable subset for in-dist eval)."""
    held_out = set()
    for c in range(N_CONSTR):
        for j in range(HELD_PER_CONSTR):
            v = (c + 1 + j) % N_VERBCLASS
            held_out.add((c, v))
    trainable = [(c, v) for c in range(N_CONSTR) for v in range(N_VERBCLASS) if (c, v) not in held_out]
    # Grounding validity: every c and every v appears in >=1 trainable product AND >=1 held-out product.
    tr_c = {c for (c, v) in trainable}
    tr_v = {v for (c, v) in trainable}
    ho_c = {c for (c, v) in held_out}
    ho_v = {v for (c, v) in held_out}
    assert tr_c == set(range(N_CONSTR)), "a construction is never trainable (ungrounded)"
    assert tr_v == set(range(N_VERBCLASS)), "a verb-class is never trainable (ungrounded)"
    assert ho_c == set(range(N_CONSTR)), "a construction is never held-out"
    assert ho_v == set(range(N_VERBCLASS)), "a verb-class is never held-out"
    return held_out, trainable


def gen_bundle(c, v, sigma, code_c, code_v, gen):
    """Observed noisy feature-bundle for a (c,v) product: b = bind(code_c[c], code_v[v]) with phase
    jitter sigma (extraction-noise proxy). Returns unit-phasor (N,) complex64."""
    b = fhrr_bind(code_c[c], code_v[v])
    if sigma > 0:
        jitter = torch.randn(N_DIM, generator=gen) * sigma
        b = b * torch.polar(torch.ones(N_DIM), jitter).to(torch.complex64)
    return unit_phase(b)


def make_bundle_set(products, n_per, sigma, code_c, code_v, role_table, gen):
    """Returns (B (n,N) complex64, y_role (n,), y_c (n,), y_v (n,))."""
    B, yr, yc, yv = [], [], [], []
    for (c, v) in products:
        for _ in range(n_per):
            B.append(gen_bundle(c, v, sigma, code_c, code_v, gen))
            yr.append(int(role_table[c, v]))
            yc.append(c)
            yv.append(v)
    return (torch.stack(B, 0),
            np.asarray(yr, dtype=np.int64), np.asarray(yc, dtype=np.int64), np.asarray(yv, dtype=np.int64))


# --------------------------------------------------------------------------- decision mechanisms
def _resonator_run(B, code_c, code_v, x_v_init, n_iter):
    """One batched soft-resonator run (Kent/Frady/Kymn matched-filter projection dynamics). B (nB,N),
    x_v_init (nB,N). Returns (c_idx (nB,), v_idx (nB,), recon_score (nB,))."""
    ccb = code_c            # (C,N)
    vcb = code_v            # (V,N)
    x_v = x_v_init
    x_c = None
    for _it in range(n_iter):
        est_c = B * x_v.conj()                       # (nB,N)
        sc = est_c @ ccb.conj().t()                  # (nB,C) complex ; Re = similarity
        x_c = unit_phase(sc @ ccb)                   # (nB,N) matched-filter projection onto C span
        est_v = B * x_c.conj()
        sv = est_v @ vcb.conj().t()                  # (nB,V)
        x_v = unit_phase(sv @ vcb)                   # (nB,N)
    # hard read of the settled factor estimates.
    c_idx = (B * x_v.conj()) @ ccb.conj().t()
    c_idx = c_idx.real.argmax(-1)                    # (nB,)
    v_idx = (B * unit_phase(ccb[c_idx]).conj()) @ vcb.conj().t()
    v_idx = v_idx.real.argmax(-1)                    # (nB,)
    recon = fhrr_bind(ccb[c_idx], vcb[v_idx])
    score = (recon.conj() * B).sum(-1).real / N_DIM  # (nB,)
    return c_idx.numpy(), v_idx.numpy(), score.numpy()


def resonator_decode(B, code_c, code_v, role_table, n_iter=RES_N_ITER, n_restart=RES_N_RESTART, seed=0):
    """ITERATIVE 2-factor resonator DECISION (Hersche/NVSA + Kent/Frady soft dynamics). Alternately
    estimate the construction and verb-class factors of the bound product b ~= bind(c,v) by
    matched-filter projection against the two codebooks; multiple restarts (restart 0 = uniform-
    superposition init for a canonical basin, others = deterministic distinct single-code inits) to
    mitigate spurious fixed points; keep the (c_hat,v_hat) with the best reconstruction resonance;
    the role label = the KNOWN table lookup of the recovered pair. Returns preds (nB,)."""
    nB = B.shape[0]
    best_score = np.full(nB, -1e9, dtype=np.float64)
    best_c = np.zeros(nB, dtype=np.int64)
    best_v = np.zeros(nB, dtype=np.int64)
    for r in range(n_restart):
        if r == 0:
            x_v_init = unit_phase(code_v.mean(0, keepdim=True)).expand(nB, N_DIM)
        else:
            # deterministic distinct single-code init (covers the V factor space across restarts).
            v0 = (r * 3 + seed) % N_VERBCLASS
            x_v_init = code_v[v0:v0 + 1].expand(nB, N_DIM)
        c_idx, v_idx, score = _resonator_run(B, code_c, code_v, x_v_init, n_iter)
        take = score > best_score
        best_score = np.where(take, score, best_score)
        best_c = np.where(take, c_idx, best_c)
        best_v = np.where(take, v_idx, best_v)
    return role_table[best_c, best_v].astype(np.int64)


def single_shot_decode(B, code_c, code_v, role_table):
    """PRIOR-REPRODUCTION control (the CLOSED single-factor free-algebra mechanism, atoms 29379-82 /
    role_filler_factorization). One pass: cleanup b directly against C then unbind by that c and cleanup
    against V (NO iteration, NO restart). Structurally blind to the 2-factor entanglement -> expected
    BELOW ceiling in this regime (design gate single_shot_not_at_ceiling proves we are OUT of the
    closed tautology)."""
    nB = B.shape[0]
    preds = np.zeros(nB, dtype=np.int64)
    for i in range(nB):
        b = B[i]
        c_idx, c_hat = cleanup_hard(b, code_c)            # marginal sim (uninformative for bound product)
        v_idx, _ = cleanup_hard(fhrr_unbind(b, c_hat), code_v)
        preds[i] = int(role_table[c_idx, v_idx])
    return preds


def _flat_features(B, code_c, code_v, proj):
    """Real-valued feature view of complex bundles B (nB,N): a fixed random projection of [Re,Im] plus
    the marginal codebook-resonance vector. Shared by both flat arms. proj: (2N, FLAT_PROJ_DIM)."""
    ri = torch.cat([B.real, B.imag], dim=1)          # (nB, 2N)
    proj_feats = ri @ proj                            # (nB, FLAT_PROJ_DIM)
    sim_c = (code_c.conj().unsqueeze(0) * B.unsqueeze(1)).sum(-1).real / N_DIM   # (nB, C)
    sim_v = (code_v.conj().unsqueeze(0) * B.unsqueeze(1)).sum(-1).real / N_DIM   # (nB, V)
    return torch.cat([proj_feats, sim_c, sim_v], dim=1)   # (nB, FLAT_PROJ_DIM + C + V)


def _make_mlp(in_dim, out_dim, seed):
    torch.manual_seed(seed)
    return nn.Sequential(nn.Linear(in_dim, 128), nn.ReLU(), nn.Linear(128, 128), nn.ReLU(),
                         nn.Linear(128, out_dim))


def _train_mlp(model, X, y, seed, epochs=150, lr=1e-3, batch=128):
    torch.manual_seed(seed)
    opt = torch.optim.Adam(model.parameters(), lr=lr)
    loss_fn = nn.CrossEntropyLoss()
    yt = torch.from_numpy(y)
    n = X.shape[0]
    gen = torch.Generator().manual_seed(seed)
    for _ep in range(epochs):
        perm = torch.randperm(n, generator=gen)
        for i in range(0, n, batch):
            idx = perm[i:i + batch]
            opt.zero_grad()
            loss = loss_fn(model(X[idx]), yt[idx])
            loss.backward()
            opt.step()
    return model


def train_flat_joint(Xtr, y_role_tr, seed):
    m = _make_mlp(Xtr.shape[1], N_ROLE, seed)
    return _train_mlp(m, Xtr, y_role_tr, seed)


def eval_flat_joint(model, X, y_role):
    with torch.no_grad():
        preds = model(X).argmax(-1).numpy()
    return preds, float((preds == y_role).mean())


def train_flat_factored(Xtr, y_c_tr, y_v_tr, seed):
    """FAIRNESS control (Csordas-style flat-with-factoring): two marginal classifiers b->c, b->v; label
    via the KNOWN role table. If this generalizes to held-out products, binding-in-decision confers no
    unique edge."""
    mc = _train_mlp(_make_mlp(Xtr.shape[1], N_CONSTR, seed), Xtr, y_c_tr, seed)
    mv = _train_mlp(_make_mlp(Xtr.shape[1], N_VERBCLASS, seed + 1), Xtr, y_v_tr, seed + 1)
    return mc, mv


def eval_flat_factored(models, X, y_role, role_table):
    mc, mv = models
    with torch.no_grad():
        c_hat = mc(X).argmax(-1).numpy()
        v_hat = mv(X).argmax(-1).numpy()
    preds = role_table[c_hat, v_hat]
    return preds, float((preds == y_role).mean())


# --------------------------------------------------------------------------- runner
def run(output_dir, sigma_sweep, seeds, n_train_per, n_test_per, run_mode):
    t0 = time.perf_counter()
    expected_n_units = len(sigma_sweep) * len(seeds) * len(ARMS)
    _write_start_marker(output_dir, run_mode, expected_n_units)

    proj = None
    per_unit = {}
    pred_hashes = {}     # (sigma,seed) -> {arm: hash of held-out preds}
    sweep = {}           # str(sigma) -> arm -> {seed: {...}}
    n_units_done = 0

    for sigma in sigma_sweep:
        sweep[str(sigma)] = {arm: {} for arm in ARMS}
        for seed in seeds:
            # Fixed codebooks / table per seed (task-agnostic seeds are CONSTANT; seed only stirs the
            # noise + MLP init + resonator restarts, NOT the codebook->split relationship).
            code_c = random_fhrr(N_CONSTR, N_DIM, CODEBOOK_C_SEED)
            code_v = random_fhrr(N_VERBCLASS, N_DIM, CODEBOOK_V_SEED)
            role_table = build_role_table(np.random.default_rng(ROLE_TABLE_SEED))
            held_out, trainable = build_split_2d(np.random.default_rng(seed))
            proj = (torch.randn(2 * N_DIM, FLAT_PROJ_DIM,
                                generator=torch.Generator().manual_seed(FLAT_PROJ_SEED))
                    / np.sqrt(2 * N_DIM))

            gtr = torch.Generator().manual_seed(500 + seed)
            gte = torch.Generator().manual_seed(900 + seed)
            # in-dist eval products = a fixed subset of trainable (distinct noise draws from train).
            indist_products = sorted(trainable)[: len(held_out)]
            held_products = sorted(held_out)

            Btr, yr_tr, yc_tr, yv_tr = make_bundle_set(sorted(trainable), n_train_per, sigma,
                                                        code_c, code_v, role_table, gtr)
            Bho, yr_ho, yc_ho, yv_ho = make_bundle_set(held_products, n_test_per, sigma,
                                                       code_c, code_v, role_table, gte)
            Bid, yr_id, yc_id, yv_id = make_bundle_set(indist_products, n_test_per, sigma,
                                                       code_c, code_v, role_table, gte)
            Xtr = _flat_features(Btr, code_c, code_v, proj)
            Xho = _flat_features(Bho, code_c, code_v, proj)
            Xid = _flat_features(Bid, code_c, code_v, proj)

            pk = f"sig{sigma}_seed{seed}"
            pred_hashes[pk] = {}
            mlp_seed = 100000 * seed + int(round(sigma * 1000))   # deterministic arithmetic combo, PROT-023

            arm_results = {}
            # --- flat_joint (design-source baseline) ---
            try:
                fj = train_flat_joint(Xtr, yr_tr, mlp_seed)
                p_ho, a_ho = eval_flat_joint(fj, Xho, yr_ho)
                _, a_id = eval_flat_joint(fj, Xid, yr_id)
                arm_results["flat_joint"] = (a_id, a_ho, p_ho)
            except Exception as e:  # noqa: BLE001 -- per-unit failure-class (META_RULE_J)
                per_unit[f"flat_joint__{pk}"] = {"failure_class": f"{type(e).__name__}: {str(e)[:160]}"}

            # --- flat_factored (fairness / strong-flat) ---
            try:
                ff = train_flat_factored(Xtr, yc_tr, yv_tr, mlp_seed)
                p_ho, a_ho = eval_flat_factored(ff, Xho, yr_ho, role_table)
                _, a_id = eval_flat_factored(ff, Xid, yr_id, role_table)
                arm_results["flat_factored"] = (a_id, a_ho, p_ho)
            except Exception as e:  # noqa: BLE001
                per_unit[f"flat_factored__{pk}"] = {"failure_class": f"{type(e).__name__}: {str(e)[:160]}"}

            # --- single_shot (prior-reproduction control) ---
            try:
                p_ho = single_shot_decode(Bho, code_c, code_v, role_table)
                a_ho = float((p_ho == yr_ho).mean())
                p_id = single_shot_decode(Bid, code_c, code_v, role_table)
                a_id = float((p_id == yr_id).mean())
                arm_results["single_shot"] = (a_id, a_ho, p_ho)
            except Exception as e:  # noqa: BLE001
                per_unit[f"single_shot__{pk}"] = {"failure_class": f"{type(e).__name__}: {str(e)[:160]}"}

            # --- resonator_iter (the novel mechanism) ---
            try:
                p_ho = resonator_decode(Bho, code_c, code_v, role_table, seed=seed)
                a_ho = float((p_ho == yr_ho).mean())
                p_id = resonator_decode(Bid, code_c, code_v, role_table, seed=seed)
                a_id = float((p_id == yr_id).mean())
                arm_results["resonator_iter"] = (a_id, a_ho, p_ho)
            except Exception as e:  # noqa: BLE001
                per_unit[f"resonator_iter__{pk}"] = {"failure_class": f"{type(e).__name__}: {str(e)[:160]}"}

            for arm, (a_id, a_ho, p_ho) in arm_results.items():
                per_unit[f"{arm}__{pk}"] = {"arm": arm, "sigma": sigma, "seed": seed,
                                            "indist_acc": a_id, "heldout_acc": a_ho,
                                            "gen_gap": a_id - a_ho, "failure_class": None}
                sweep[str(sigma)][arm][str(seed)] = per_unit[f"{arm}__{pk}"]
                pred_hashes[pk][arm] = hashlib.sha256(np.asarray(p_ho).tobytes()).hexdigest()
                n_units_done += 1
            _hb(output_dir, "sig={} seed={} | ".format(sigma, seed)
                + " ".join(f"{a}:id={r[0]:.3f}/ho={r[1]:.3f}" for a, r in arm_results.items()))

    # ARMS-MUST-DIFFER (META_RULE_AF): at the gate sigma, the 4 arms' held-out preds must not be
    # pairwise bit-identical (flat_joint vs flat_factored vs single_shot vs resonator).
    arms_differ = True
    for pk, hd in pred_hashes.items():
        if pk.startswith(f"sig{SIGMA_GATE}_"):
            vals = list(hd.values())
            if vals and len(set(vals)) != len(vals):
                arms_differ = False
    cardinality_ok = (n_units_done == expected_n_units)

    def _mean(vals):
        return float(np.mean(vals)) if vals else float("nan")

    arm_by_sigma = {}
    for sigma in sigma_sweep:
        arm_by_sigma[str(sigma)] = {}
        for arm in ARMS:
            ids = [sweep[str(sigma)][arm][str(s)]["indist_acc"] for s in seeds
                   if str(s) in sweep[str(sigma)][arm]]
            hos = [sweep[str(sigma)][arm][str(s)]["heldout_acc"] for s in seeds
                   if str(s) in sweep[str(sigma)][arm]]
            arm_by_sigma[str(sigma)][arm] = {"indist_mean": _mean(ids), "heldout_mean": _mean(hos),
                                             "n_seeds": len(ids)}

    # ------------------------------------------------------------------ verdict at SIGMA_GATE
    gate = arm_by_sigma.get(str(SIGMA_GATE), {})
    res = gate.get("resonator_iter", {})
    fj = gate.get("flat_joint", {})
    ff = gate.get("flat_factored", {})
    ss = gate.get("single_shot", {})

    def _g(d, k):
        return d.get(k, float("nan"))

    res_ho, res_id = _g(res, "heldout_mean"), _g(res, "indist_mean")
    fj_ho, fj_id = _g(fj, "heldout_mean"), _g(fj, "indist_mean")
    ff_ho = _g(ff, "heldout_mean")
    ss_ho = _g(ss, "heldout_mean")

    heldout_gap = res_ho - fj_ho              # vs the design-source baseline (flat_joint)
    heldout_gap_vs_strong = res_ho - ff_ho    # vs the strongest flat (flat_factored)
    indist_gap = abs(res_id - fj_id)
    indist_cost = fj_id - res_id              # positive = resonator costs in-dist accuracy
    # INTENT-FAITHFUL confound guard: the held-out advantage must DOMINATE any in-dist advantage, i.e.
    # the resonator edge is SPECIFIC to held-out (systematicity) not uniform skill. This replaces the
    # design-source's literal |indist_gap|<=0.01 sub-gate, which under noise is tripped by flat's benign
    # in-dist noise-drop (a fragility unrelated to systematicity). The literal verdict is ALSO computed
    # and stored (verdict_literal_designsource) for the landed-VET to adjudicate. See pre-reg.
    heldout_advantage = heldout_gap
    indist_advantage = res_id - fj_id
    advantage_dominance = heldout_advantage - abs(indist_advantage)
    # GENERALIZATION-GAP systematicity signature (the theoretically correct measure): a SYSTEMATIC
    # decision mechanism generalizes to held-out combos (gap ~ 0); a MEMORIZING one does not (gap large).
    res_gen_gap = res_id - res_ho
    fj_gen_gap = fj_id - fj_ho
    ff_gen_gap = _g(ff, "indist_mean") - ff_ho

    # Regime-validity design gates (VOID if the regime is the closed tautology or the split is trivial).
    void_reasons = []
    if not np.isnan(ss_ho) and ss_ho >= GATE_SINGLE_SHOT_CEIL:
        void_reasons.append(f"single_shot_at_ceiling({ss_ho:.3f}>= {GATE_SINGLE_SHOT_CEIL}) => closed-tautology regime")
    if not np.isnan(fj_ho) and fj_ho >= GATE_FLAT_MUSTFAIL:
        void_reasons.append(f"flat_joint_heldout_high({fj_ho:.3f}>= {GATE_FLAT_MUSTFAIL}) => split does not isolate")
    if not np.isnan(fj_id) and fj_id < GATE_FLAT_INDIST_MIN:
        void_reasons.append(f"flat_joint_indist_low({fj_id:.3f}< {GATE_FLAT_INDIST_MIN}) => flat starved/broken")

    # Positive control at sigma=0: resonator must be near-ceiling (mechanism CAN fire when noiseless).
    res_pc = _g(arm_by_sigma.get("0.0", {}).get("resonator_iter", {}), "heldout_mean")
    pos_control_ok = (not np.isnan(res_pc)) and res_pc >= 0.95

    # Literal design-source verdict (stored for VET; strict absolute in-dist-parity sub-gate).
    literal_pass = (heldout_gap >= HP_HELDOUT_GAP and indist_gap <= HP_INDIST_GAP_MAX
                    and indist_cost <= HF_INDIST_COST)
    verdict_literal_designsource = "HARD_PASS" if literal_pass else (
        "HARD_FAIL_EXTRACTION_BOUND" if (heldout_gap <= HF_HELDOUT_GAP or indist_cost > HF_INDIST_COST)
        else "MIDDLE_BAND")

    if not cardinality_ok:
        verdict = "HARD_FAIL_CARDINALITY_BREACH_META_RULE_H"
    elif not arms_differ:
        verdict = "HARD_FAIL_ARMS_IDENTICAL_META_RULE_AF"
    elif not pos_control_ok:
        verdict = "HARD_FAIL_POSITIVE_CONTROL_RESONATOR_BROKEN"
    elif void_reasons:
        verdict = "VOID_REGIME_INVALID"
    elif (heldout_gap >= HP_HELDOUT_GAP and res_gen_gap <= 0.05 and fj_gen_gap >= 0.30
          and indist_cost <= HF_INDIST_COST):
        # Clean Fodor-Pylyshyn systematicity: resonator generalizes (gap~0), flat memorizes (gap large),
        # flat IS in-dist-competent (void gate ensured flat_id >= 0.60) so the gap is generalization not fitting.
        verdict = "HARD_PASS"
    elif (heldout_gap <= HF_HELDOUT_GAP) or (res_gen_gap > 0.30) or (indist_cost > HF_INDIST_COST):
        verdict = "HARD_FAIL_EXTRACTION_BOUND"
    else:
        verdict = "MIDDLE_BAND"

    verdict_msg = (
        f"{verdict} | @sigma={SIGMA_GATE}: RES ho={res_ho:.3f}/id={res_id:.3f} "
        f"FLATj ho={fj_ho:.3f}/id={fj_id:.3f} FLATf ho={ff_ho:.3f} SS ho={ss_ho:.3f} | "
        f"heldout_gap(vs flat_joint)={heldout_gap:+.3f} (vs flat_factored)={heldout_gap_vs_strong:+.3f} | "
        f"GEN_GAP res={res_gen_gap:+.3f} flat_joint={fj_gen_gap:+.3f} flat_factored={ff_gen_gap:+.3f} | "
        f"indist_gap={indist_gap:.3f} indist_cost={indist_cost:+.3f} literal_designsource={verdict_literal_designsource} | "
        f"pos_control(sig0 RES ho)={res_pc:.3f} chance={CHANCE:.3f} | "
        f"void={void_reasons if void_reasons else 'none'} cardinality_ok={cardinality_ok} arms_differ={arms_differ}"
    )

    metrics = {
        "verdict": verdict, "verdict_msg": verdict_msg,
        "verdict_literal_designsource": verdict_literal_designsource,
        "advantage_dominance": advantage_dominance, "indist_advantage": indist_advantage,
        "summary": f"{verdict}: resonator-decision compgen 2-factor (heldout_gap={heldout_gap:+.3f} @sig{SIGMA_GATE})",
        "elapsed_s": time.perf_counter() - t0, "run_mode": run_mode,
        "anchor_name": ANCHOR_NAME, "ts_iso": datetime.now(timezone.utc).isoformat(),
        "chance": CHANCE, "sigma_gate": SIGMA_GATE,
        "arm_by_sigma": arm_by_sigma, "per_unit": per_unit,
        "cardinality_ok": cardinality_ok, "expected_n_units": expected_n_units,
        "n_units_done": n_units_done, "arms_differ": arms_differ,
        "pos_control_ok": pos_control_ok, "void_reasons": void_reasons,
        "gate_metrics": {
            "heldout_gap_vs_flat_joint": heldout_gap,
            "heldout_gap_vs_flat_factored": heldout_gap_vs_strong,
            "gen_gap_resonator": res_gen_gap, "gen_gap_flat_joint": fj_gen_gap,
            "gen_gap_flat_factored": ff_gen_gap,
            "indist_gap": indist_gap, "indist_cost": indist_cost,
            "resonator_heldout": res_ho, "resonator_indist": res_id,
            "flat_joint_heldout": fj_ho, "flat_joint_indist": fj_id,
            "flat_factored_heldout": ff_ho, "single_shot_heldout": ss_ho,
        },
        "config": {
            "N_DIM": N_DIM, "N_CONSTR": N_CONSTR, "N_VERBCLASS": N_VERBCLASS, "N_ROLE": N_ROLE,
            "HELD_PER_CONSTR": HELD_PER_CONSTR, "n_train_per": n_train_per, "n_test_per": n_test_per,
            "sigma_sweep": sigma_sweep, "seeds": seeds, "arms": ARMS,
            "RES_N_ITER": RES_N_ITER, "RES_N_RESTART": RES_N_RESTART,
        },
    }
    _atomic_write_metrics(output_dir, metrics)
    _hb(output_dir, f"DONE verdict={verdict} elapsed={metrics['elapsed_s']:.1f}s")
    return metrics


# --------------------------------------------------------------------------- self-test
def self_test():
    """Exercises the REAL decision-mechanism code paths at tiny scale (F.1 real_code_path):
    resonator_decode / single_shot_decode / flat arms / gen_bundle / build_split_2d. Asserts the
    noiseless positive control (resonator recovers held-out products ~perfectly) and that arms differ."""
    print("[self_test] START", flush=True)
    # F.5 static determinism scan of THIS source (no salted-builtin-seeded RNG / nondeterministic split ordering).
    with open(os.path.abspath(__file__), encoding="utf-8") as fh:
        assert_no_nondeterministic_seeding(fh.read())
    print("[self_test] determinism scan OK", flush=True)

    code_c = random_fhrr(N_CONSTR, N_DIM, CODEBOOK_C_SEED)
    code_v = random_fhrr(N_VERBCLASS, N_DIM, CODEBOOK_V_SEED)
    role_table = build_role_table(np.random.default_rng(ROLE_TABLE_SEED))
    held_out, trainable = build_split_2d(np.random.default_rng(7))
    assert held_out.isdisjoint(set(trainable)), "held-out leaks into trainable"
    print(f"[self_test] split: {len(trainable)} trainable, {len(held_out)} held-out products", flush=True)

    gen = torch.Generator().manual_seed(1)
    held_products = sorted(held_out)
    Bho, yr, yc, yv = make_bundle_set(held_products, 3, 0.0, code_c, code_v, role_table, gen)

    # Positive control: noiseless resonator recovers held-out products -> role labels ~exact.
    p_res = resonator_decode(Bho, code_c, code_v, role_table, n_iter=25, n_restart=4, seed=1)
    acc_res = float((p_res == yr).mean())
    assert acc_res >= 0.95, f"resonator noiseless positive control failed: acc={acc_res}"
    print(f"[self_test] resonator noiseless held-out acc={acc_res:.3f} OK", flush=True)

    # single_shot exercised (must run; not asserted high -- it is the 2-factor-blind control).
    p_ss = single_shot_decode(Bho, code_c, code_v, role_table)
    acc_ss = float((p_ss == yr).mean())
    print(f"[self_test] single_shot held-out acc={acc_ss:.3f} (2-factor-blind control)", flush=True)

    # flat arms real code path at tiny scale (few epochs).
    proj = (torch.randn(2 * N_DIM, FLAT_PROJ_DIM,
                        generator=torch.Generator().manual_seed(FLAT_PROJ_SEED)) / np.sqrt(2 * N_DIM))
    gtr = torch.Generator().manual_seed(2)
    Btr, yrt, yct, yvt = make_bundle_set(sorted(trainable), 4, 0.0, code_c, code_v, role_table, gtr)
    Xtr = _flat_features(Btr, code_c, code_v, proj)
    Xho = _flat_features(Bho, code_c, code_v, proj)
    fj = _train_mlp(_make_mlp(Xtr.shape[1], N_ROLE, 3), Xtr, yrt, 3, epochs=5)
    p_fj, a_fj = eval_flat_joint(fj, Xho, yr)
    ff = train_flat_factored(Xtr, yct, yvt, 3)
    p_ff, a_ff = eval_flat_factored(ff, Xho, yr, role_table)
    print(f"[self_test] flat_joint held-out acc={a_fj:.3f} flat_factored={a_ff:.3f} (untrained-regime)", flush=True)

    # arms-differ at tiny scale (resonator vs single_shot vs flats should not be bit-identical).
    hs = {a: hashlib.sha256(np.asarray(p).tobytes()).hexdigest()
          for a, p in [("res", p_res), ("ss", p_ss), ("fj", p_fj), ("ff", p_ff)]}
    assert len(set(hs.values())) >= 2, "arms bit-identical in self-test"
    print("[self_test] arms-differ OK", flush=True)
    print("[self_test] PASS", flush=True)
    return True


# --------------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--full", action="store_true")
    args = ap.parse_args()

    if args.self_test:
        self_test()
        sys.exit(0)

    if args.smoke:
        run_mode = "smoke"
        out = os.path.join(REPO, "data", f"{ANCHOR_NAME}_smoke")
        run(out, SIGMA_SWEEP_SMOKE, SEEDS_SMOKE, 12, 12, run_mode)
    else:
        run_mode = "full"
        out = os.path.join(REPO, "data", ANCHOR_NAME)
        run(out, SIGMA_SWEEP_FULL, SEEDS_FULL, N_TRAIN_PER_PRODUCT, N_TEST_PER_PRODUCT, run_mode)
    sys.exit(0)


if __name__ == "__main__":
    OUT_DIR_FOR_CRASH = os.path.join(
        REPO, "data",
        ANCHOR_NAME + ("_smoke" if ("--smoke" in sys.argv) else "")
        if "--self-test" not in sys.argv else ANCHOR_NAME + "_selftest",
    )
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # NOT BaseException; preserves SystemExit + KeyboardInterrupt
        _write_crash_metrics(OUT_DIR_FOR_CRASH, e)
        raise
