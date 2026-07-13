"""Periodic-table CROSS-CHANNEL GROUNDING cell (Track-B grounding build #1).

Question: can a genuinely MEASURED, non-LLM numeric channel (Channel B) be
VSA-wired into the existing bind/bundle algebra (Channel A, the substrate-native
KGStore relational store) and produce a MEASURABLE inference gain over the pure-
symbol baseline?

Channel A (relational, native): element -> (HAS_GROUP g, HAS_PERIOD p, HAS_BLOCK b)
  ingested into a REAL hdlab.kg_traversal.KGStore; element relational signatures
  built from the store's own E/R bipolar codebooks (bind = elementwise multiply,
  bundle = sum).
Channel B (measured, exterior): atomic mass, electronegativity (Pauling), atomic
  radius, first ionization energy, melting point -- REAL measured constants
  (standard IUPAC/NIST periodic-table reference data). CITED external constants.
Encoding: FHRR fractional power encoding (FPE) -- per-dimension phase * value with
  Gaussian base frequencies (Frady/Kleyko/Sommer VFA; Plate HRR). SMOKED side by
  side with a spherical-interpolation LEVEL code (the bundling-robust fallback,
  arXiv:2412.00488). A CSim-style resonator CLEANUP decoder is a first-class arm.
Oracle: periodic law. Predict a held-out element's numeric property from its
  consolidated neighbors (leave-one-out kNN in the consolidated geometry); check
  against the TRUE measured value.
Decisive ablation: A alone (relational similarity only) vs A+B (relational fused
  with FPE/level attribute similarity of the OTHER four properties).

The cell REPORTS which of three failure modes occurred and does NOT conflate them:
  - GROUNDING_NEGATIVE:  A ties/beats A+B (numeric channel not load-bearing)
  - ENCODING_BROKEN:     FPE similarity does not decay with numeric distance
  - DECODE_DEGRADATION:  raw FPE decode fails at bundle size 5 but CLEANUP fixes it
  - ORACLE_LEAK:         boundary/isolated elements fail while interior passes

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; ARMS-MUST-DIFFER hash-test)
# - final_metrics_atomicity = tmp_replace (META_RULE_AH)
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_n/a declared (regression-skill cell; no argmax capacity floor)
# - baseline_in_band at smoke (META_RULE_AG; 0.05 < A_ALONE skill < 0.95)
# - discriminator survives scale: self-test runs the REAL mechanism on the REAL
#   periodic data at n_dim=2048 (discriminator-preview arm) + FULL at n_dim=8192
# - HARD_PASS strictly above floor + margin (META_RULE_L)
# - HP_SCOPE per-arm declaration (see prereg)
# - cardinality_ok: EXPECTED_N_UNITS = n_seeds * n_targets * n_known_per_target
# - per-unit failure-class instrumentation (no bare except)
# - calibration_check: default_ok_for_this_regime (Gaussian-freq bandwidth s
#   chosen analytically so kernel decays 1.0 -> ~0.1 across the [0,1] value range)
# - all numbers tagged MEASURED@/CITED@/THEORETICAL@ in the prereg
# - F.1 real_code_path: self-test CONSTRUCTS the REAL KGStore at n_dim=16 + ingests
# - F.2/F.3 substrate_signature: KGStore bound with BASE/portable kwargs only
#   (n_ent, n_rel, n_dim, generator); NO version-specific init_entities kwarg
# - F.4 guard_baseline_valid: A_ALONE (baseline) validated above RANDOM (floor)
# - progress_logging: print_flush_true (cheap cell; timeout << 1800 anyway)

ASCII-only per feedback_ascii_only_in_scripts. No em-dashes in output.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import platform
import sys
import time
import traceback
from datetime import datetime, timezone

import torch

# Real substrate objects the FULL run uses (F.1/F.2/F.3).
from hdlab.kg_traversal import KGStore

# Mandated validity-preflight gate (Pattern-5 auto-SCP shared module).
from experiments._validity_preflight import run_validity_preflight

ANCHOR_NAME = "grounding_periodic_xchannel_fpe_v1"

# --------------------------------------------------------------------------- #
# Arm names                                                                    #
# --------------------------------------------------------------------------- #
MEAN = "MEAN"
DEGREE = "DEGREE"
RANDOM = "RANDOM"
A_ALONE = "A_ALONE"
B_ALONE = "B_ALONE"                 # FPE numeric channel only (no relational) -> does B ground at all
A_PLUS_B_FPE = "A_PLUS_B_FPE"
A_PLUS_B_LEVEL = "A_PLUS_B_LEVEL"
RAW_FEATURE_KNN = "RAW_FEATURE_KNN"  # kNN on raw normalized other-features (informative reference)
ARMS = [MEAN, DEGREE, RANDOM, A_ALONE, B_ALONE, A_PLUS_B_FPE, A_PLUS_B_LEVEL, RAW_FEATURE_KNN]

# --------------------------------------------------------------------------- #
# Config                                                                       #
# --------------------------------------------------------------------------- #
FULL_CFG = dict(n_dim=8192, seeds=[7, 13, 19, 23, 29], fpe_freq_std=2.15,
                level_bins=64, weight_exp=6.0, lam=1.0, decode_grid=257,
                decode_cleanup_iters=3)
SELFTEST_CFG = dict(n_dim=2048, seeds=[7, 13], fpe_freq_std=2.15,
                    level_bins=64, weight_exp=6.0, lam=1.0, decode_grid=129,
                    decode_cleanup_iters=3)

# HARD-PASS / HARD-FAIL bands (see prereg for full pre-registration).
HP_B_BEATS_A_MARGIN = 0.05      # A+B_FPE skill must beat A_ALONE by >= this
HP_B_BEATS_FLOOR_MARGIN = 0.10  # A+B_FPE skill must beat RANDOM by >= this
HP_FPE_DECAY_SPEARMAN = 0.90    # |dv| vs -cos monotone decay
HP_DEGREE_INVARIANCE = 0.15     # boundary skill >= interior skill - this (both > 0)
HP_DECODE_CLEANUP_MEDREL = 0.20 # cleanup decode median rel-error must be <= this
HF_ENCODING_SPEARMAN = 0.50     # below this = ENCODING_BROKEN
HF_RAW_DECODE_MEDREL = 0.50     # raw decode above this at bundle-5 = degradation

# Machinery / ship-ability thresholds (self-test). These gate SHIP-ABILITY, NOT the
# science answer: the SYNTH positive control proves the A-vs-A+B ablation DETECTS a
# load-bearing exogenous channel when one exists, so the real-data verdict (whatever
# it is) is trustworthy. The real "does B beat A" question is the FULL science, not a
# ship gate (gating ship on it would refuse to run the very test that answers it).
HP_SYNTH_GAP = 0.30             # A+B - A on a synthetic exogenous channel A cannot predict
HP_B_ALONE_GROUNDS = 0.10       # B_ALONE (numeric only) skill must beat MEAN (==0) by this


# --------------------------------------------------------------------------- #
# Measured periodic-table reference data (CITED external constants).           #
#   Z, symbol, group(1-18), period, atomic_mass(amu), electronegativity(Pauling,
#   NaN where no standard Pauling value), atomic_radius(empirical, pm),
#   first_ionization_energy(kJ/mol), melting_point(K).                          #
# Standard IUPAC/NIST/CRC reference values; periods 1-5 (H..Xe) = 5 complete    #
# rows, avoids lanthanide/superheavy uncertainty. CITED@CRC-Handbook/IUPAC.     #
# --------------------------------------------------------------------------- #
_PT = [
    # Z, sym, grp, per, mass,     EN,   rad, IE1,  mp_K
    (1,  "H",  1,  1, 1.008,    2.20,  25, 1312, 13.99),
    (2,  "He", 18, 1, 4.0026,   float("nan"), 31, 2372, 0.95),
    (3,  "Li", 1,  2, 6.94,     0.98, 145,  520, 453.65),
    (4,  "Be", 2,  2, 9.0122,   1.57, 105,  899, 1560.0),
    (5,  "B",  13, 2, 10.81,    2.04,  85,  801, 2349.0),
    (6,  "C",  14, 2, 12.011,   2.55,  70, 1086, 3823.0),
    (7,  "N",  15, 2, 14.007,   3.04,  65, 1402, 63.15),
    (8,  "O",  16, 2, 15.999,   3.44,  60, 1314, 54.36),
    (9,  "F",  17, 2, 18.998,   3.98,  50, 1681, 53.48),
    (10, "Ne", 18, 2, 20.180,   float("nan"), 38, 2081, 24.56),
    (11, "Na", 1,  3, 22.990,   0.93, 180,  496, 370.94),
    (12, "Mg", 2,  3, 24.305,   1.31, 150,  738, 923.0),
    (13, "Al", 13, 3, 26.982,   1.61, 125,  578, 933.47),
    (14, "Si", 14, 3, 28.085,   1.90, 110,  787, 1687.0),
    (15, "P",  15, 3, 30.974,   2.19, 100, 1012, 317.3),
    (16, "S",  16, 3, 32.06,    2.58, 100, 1000, 388.36),
    (17, "Cl", 17, 3, 35.45,    3.16, 100, 1251, 171.6),
    (18, "Ar", 18, 3, 39.948,   float("nan"), 71, 1521, 83.81),
    (19, "K",  1,  4, 39.098,   0.82, 220,  419, 336.7),
    (20, "Ca", 2,  4, 40.078,   1.00, 180,  590, 1115.0),
    (21, "Sc", 3,  4, 44.956,   1.36, 160,  633, 1814.0),
    (22, "Ti", 4,  4, 47.867,   1.54, 140,  659, 1941.0),
    (23, "V",  5,  4, 50.942,   1.63, 135,  651, 2183.0),
    (24, "Cr", 6,  4, 51.996,   1.66, 140,  653, 2180.0),
    (25, "Mn", 7,  4, 54.938,   1.55, 140,  717, 1519.0),
    (26, "Fe", 8,  4, 55.845,   1.83, 140,  762, 1811.0),
    (27, "Co", 9,  4, 58.933,   1.88, 135,  760, 1768.0),
    (28, "Ni", 10, 4, 58.693,   1.91, 135,  737, 1728.0),
    (29, "Cu", 11, 4, 63.546,   1.90, 135,  745, 1357.77),
    (30, "Zn", 12, 4, 65.38,    1.65, 135,  906, 692.68),
    (31, "Ga", 13, 4, 69.723,   1.81, 130,  579, 302.91),
    (32, "Ge", 14, 4, 72.630,   2.01, 125,  762, 1211.4),
    (33, "As", 15, 4, 74.922,   2.18, 115,  947, 1090.0),
    (34, "Se", 16, 4, 78.971,   2.55, 115,  941, 494.0),
    (35, "Br", 17, 4, 79.904,   2.96, 115, 1140, 265.8),
    (36, "Kr", 18, 4, 83.798,   3.00,  88, 1351, 115.79),
    (37, "Rb", 1,  5, 85.468,   0.82, 235,  403, 312.46),
    (38, "Sr", 2,  5, 87.62,    0.95, 200,  549, 1050.0),
    (39, "Y",  3,  5, 88.906,   1.22, 180,  600, 1799.0),
    (40, "Zr", 4,  5, 91.224,   1.33, 155,  640, 2128.0),
    (41, "Nb", 5,  5, 92.906,   1.60, 145,  652, 2750.0),
    (42, "Mo", 6,  5, 95.95,    2.16, 145,  684, 2896.0),
    (43, "Tc", 7,  5, 98.0,     1.90, 135,  702, 2430.0),
    (44, "Ru", 8,  5, 101.07,   2.20, 130,  710, 2607.0),
    (45, "Rh", 9,  5, 102.91,   2.28, 135,  720, 2237.0),
    (46, "Pd", 10, 5, 106.42,   2.20, 140,  804, 1828.05),
    (47, "Ag", 11, 5, 107.87,   1.93, 160,  731, 1234.93),
    (48, "Cd", 12, 5, 112.41,   1.69, 155,  868, 594.22),
    (49, "In", 13, 5, 114.82,   1.78, 155,  558, 429.75),
    (50, "Sn", 14, 5, 118.71,   1.96, 145,  709, 505.08),
    (51, "Sb", 15, 5, 121.76,   2.05, 145,  834, 903.78),
    (52, "Te", 16, 5, 127.60,   2.10, 140,  869, 722.66),
    (53, "I",  17, 5, 126.90,   2.66, 140, 1008, 386.85),
    (54, "Xe", 18, 5, 131.29,   2.60, 108, 1170, 161.4),
]
_PROP_NAMES = ["mass", "electronegativity", "radius", "ionization", "melting_point"]


def _block_of(group: int, period: int) -> int:
    """Coarse s/p/d block (0/1/2); genuinely coarser than group -> non-redundant relation."""
    if group in (1, 2):
        return 0  # s-block
    if 3 <= group <= 12:
        return 2  # d-block
    return 1      # p-block


def load_periodic() -> dict:
    """Return element arrays: props [E,5] (with NaN masks), group/period/block ids, boundary mask."""
    z = [r[0] for r in _PT]
    sym = [r[1] for r in _PT]
    group = [r[2] for r in _PT]
    period = [r[3] for r in _PT]
    props = torch.tensor([[r[4], r[5], r[6], r[7], r[8]] for r in _PT], dtype=torch.float64)
    block = [_block_of(g, p) for g, p in zip(group, period)]
    # boundary = table edges (groups 1/2/17/18) or period 1 (H/He); interior = else.
    boundary = torch.tensor([(g in (1, 2, 17, 18)) or (p == 1) for g, p in zip(group, period)],
                            dtype=torch.bool)
    return dict(z=z, sym=sym, group=group, period=period, block=block,
                props=props, boundary=boundary, n=len(_PT))


# --------------------------------------------------------------------------- #
# Encodings                                                                    #
# --------------------------------------------------------------------------- #
def _norm_prop(col: torch.Tensor) -> torch.Tensor:
    """Min-max normalize a property column to [0,1], ignoring NaN. Returns float64."""
    mask = ~torch.isnan(col)
    lo = col[mask].min()
    hi = col[mask].max()
    span = (hi - lo).clamp_min(1e-12)
    out = (col - lo) / span
    return out  # NaNs stay NaN


def fpe_encode(vals: torch.Tensor, freqs: torch.Tensor) -> torch.Tensor:
    """FHRR fractional power encoding: enc[e,d] = exp(1j * freqs[d] * vals[e]). [E,D] complex64.

    vals in [0,1] (NaN -> zero vector). freqs Gaussian per-dim base frequencies.
    cos-sim(enc(v1),enc(v2)) = mean_d cos(freqs[d]*(v1-v2)) = exp(-s^2 dv^2/2) (Gaussian kernel).
    """
    E = vals.shape[0]
    D = freqs.shape[0]
    v = torch.nan_to_num(vals, nan=0.0).to(torch.float64).view(E, 1)
    phase = v * freqs.view(1, D).to(torch.float64)
    enc = torch.exp(torch.complex(torch.zeros_like(phase), phase)).to(torch.complex64)
    nan_rows = torch.isnan(vals)
    if nan_rows.any():
        enc[nan_rows] = 0.0
    return enc


def level_encode(vals: torch.Tensor, v_lo: torch.Tensor, v_hi: torch.Tensor) -> torch.Tensor:
    """Spherical-interpolation level code: normalize(cos(t)*v_lo + sin(t)*v_hi), t=v*pi/2. [E,D] float32.

    cos-sim(level(v1),level(v2)) = cos((v1-v2)*pi/2): monotone-decreasing, bundling-robust.
    """
    E = vals.shape[0]
    v = torch.nan_to_num(vals, nan=0.0).to(torch.float64)
    t = v * (math.pi / 2.0)
    out = torch.cos(t).view(E, 1) * v_lo.view(1, -1) + torch.sin(t).view(E, 1) * v_hi.view(1, -1)
    out = out / out.norm(dim=1, keepdim=True).clamp_min(1e-12)
    nan_rows = torch.isnan(vals)
    if nan_rows.any():
        out[nan_rows] = 0.0
    return out.to(torch.float32)


def _cos_sim_real(mat: torch.Tensor) -> torch.Tensor:
    """Pairwise cosine similarity matrix [E,E] (real). Accepts real or complex; complex -> real part."""
    if torch.is_complex(mat):
        norms = mat.abs().pow(2).sum(dim=1).sqrt().clamp_min(1e-12)
        m = mat / norms.view(-1, 1)
        gram = (m @ m.conj().t()).real
        return gram
    norms = mat.norm(dim=1, keepdim=True).clamp_min(1e-12)
    m = mat / norms
    return m @ m.t()


# --------------------------------------------------------------------------- #
# Channel A: REAL KGStore relational signatures                                #
# --------------------------------------------------------------------------- #
def build_relational_store(pt: dict, n_dim: int, gen: torch.Generator):
    """Ingest element->(group,period,block) triples into a REAL KGStore; return (store, rel_sigs [E,D]).

    Exercises the REAL substrate code path (F.1): KGStore(...) with BASE/portable
    kwargs only (F.2/F.3), + ingest_triples. Element relational signature is built
    from the store's own E/R bipolar codebooks: rel[e] = sum_r R[r]*E[symbol_of(e,r)]
    (bind = elementwise multiply, bundle = sum). Shared group/period/block -> similar.
    """
    n_el = pt["n"]
    groups = sorted(set(pt["group"]))
    periods = sorted(set(pt["period"]))
    blocks = sorted(set(pt["block"]))
    # Entity index layout: [elements | group-symbols | period-symbols | block-symbols].
    g_off = n_el
    p_off = g_off + len(groups)
    b_off = p_off + len(periods)
    n_ent = b_off + len(blocks)
    n_rel = 3  # HAS_GROUP, HAS_PERIOD, HAS_BLOCK
    g_idx = {g: g_off + i for i, g in enumerate(groups)}
    p_idx = {p: p_off + i for i, p in enumerate(periods)}
    b_idx = {b: b_off + i for i, b in enumerate(blocks)}

    # BASE/portable constructor ONLY (portable across KGStore versions per F.3).
    store = KGStore(n_ent, n_rel, n_dim, gen)

    triples = []
    for e in range(n_el):
        triples.append((e, 0, g_idx[pt["group"][e]]))
        triples.append((e, 1, p_idx[pt["period"][e]]))
        triples.append((e, 2, b_idx[pt["block"][e]]))
    store.ingest_triples(torch.tensor(triples, dtype=torch.long))

    E = store.E  # [n_ent, D] bipolar float32
    R = store.R  # [n_rel, D]
    rel = torch.zeros(n_el, n_dim, dtype=torch.float32)
    for e in range(n_el):
        rel[e] = (R[0] * E[g_idx[pt["group"][e]]]
                  + R[1] * E[p_idx[pt["period"][e]]]
                  + R[2] * E[b_idx[pt["block"][e]]])
    return store, rel


# --------------------------------------------------------------------------- #
# kNN readout in a consolidated geometry                                       #
# --------------------------------------------------------------------------- #
def _predict_loo(sim: torch.Tensor, target_raw: torch.Tensor, known: torch.Tensor,
                 weight_exp: float) -> torch.Tensor:
    """Leave-one-out similarity-weighted prediction of target_raw for every known element.

    sim [E,E] similarity; target_raw [E] (raw units); known [E] bool mask (has target).
    Returns preds [E] (NaN for unknown). No leakage: an element never weights itself.
    """
    E = sim.shape[0]
    preds = torch.full((E,), float("nan"), dtype=torch.float64)
    idx_known = torch.nonzero(known, as_tuple=False).view(-1).tolist()
    for e in idx_known:
        w = sim[e].clone().to(torch.float64)
        w = torch.clamp(w, min=0.0)
        w[e] = 0.0                       # never use self
        w[~known] = 0.0                  # only neighbors with known target
        w = w.pow(weight_exp)
        wsum = w.sum()
        if wsum <= 1e-12:
            preds[e] = target_raw[known].to(torch.float64).mean()
        else:
            preds[e] = (w * torch.nan_to_num(target_raw.to(torch.float64), nan=0.0)).sum() / wsum
    return preds


def _skill(preds: torch.Tensor, target_raw: torch.Tensor, known: torch.Tensor,
           subset: torch.Tensor | None = None) -> float:
    """R^2-style skill vs the mean baseline over the known (optionally subset) elements.

    skill = 1 - SS_res/SS_tot; SS_tot from the mean of the known targets. >0 = beats mean.
    """
    m = known.clone()
    if subset is not None:
        m = m & subset
    idx = torch.nonzero(m, as_tuple=False).view(-1)
    if idx.numel() < 3:
        return float("nan")
    y = target_raw[idx].to(torch.float64)
    yhat = preds[idx].to(torch.float64)
    valid = ~torch.isnan(yhat)
    if valid.sum() < 3:
        return float("nan")
    y = y[valid]
    yhat = yhat[valid]
    ss_tot = ((y - y.mean()) ** 2).sum()
    ss_res = ((y - yhat) ** 2).sum()
    if ss_tot <= 1e-12:
        return float("nan")
    return float(1.0 - ss_res / ss_tot)


def _spearman(a: torch.Tensor, b: torch.Tensor) -> float:
    """Spearman rank correlation (numpy/scipy-free): Pearson of ranks."""
    def rank(x):
        order = torch.argsort(x)
        r = torch.zeros_like(x, dtype=torch.float64)
        r[order] = torch.arange(x.numel(), dtype=torch.float64)
        return r
    ra, rb = rank(a.to(torch.float64)), rank(b.to(torch.float64))
    ra = ra - ra.mean()
    rb = rb - rb.mean()
    denom = (ra.norm() * rb.norm()).clamp_min(1e-12)
    return float((ra * rb).sum() / denom)


# --------------------------------------------------------------------------- #
# FPE distance-decay + decode diagnostics (encoding integrity)                 #
# --------------------------------------------------------------------------- #
def fpe_distance_decay_spearman(freqs_1d: torch.Tensor) -> float:
    """Spearman(|dv|, -cos): does FPE similarity decay monotonically with numeric distance?

    freqs_1d: a single property's base frequencies [D] (all properties share the same
    Gaussian freq_std so any one is representative of the encoding's kernel).
    """
    grid = torch.linspace(0.0, 1.0, 41, dtype=torch.float64)
    enc = fpe_encode(grid, freqs_1d)              # [41, D]
    sim = _cos_sim_real(enc)                       # [41,41]
    dv = (grid.view(-1, 1) - grid.view(1, -1)).abs()
    iu = torch.triu_indices(grid.numel(), grid.numel(), offset=1)
    dvs = dv[iu[0], iu[1]]
    coss = sim[iu[0], iu[1]]
    return _spearman(dvs, -coss)


def decode_diagnostics(pt: dict, freqs: torch.Tensor, roles: torch.Tensor,
                       grid_n: int, cleanup_iters: int) -> dict:
    """Bundle all 5 FPE-encoded properties per element; decode each RAW vs CLEANUP (resonator).

    Returns median relative decode error (normalized units) for raw and cleanup. This
    distinguishes DECODE_DEGRADATION (raw high, cleanup low) from a real grounding negative.
    """
    n_el = pt["n"]
    n_dim = freqs.shape[1]
    nprops = len(_PROP_NAMES)
    norm_cols = [_norm_prop(pt["props"][:, k]) for k in range(nprops)]
    grid = torch.linspace(0.0, 1.0, grid_n, dtype=torch.float64)
    grid_codes = [fpe_encode(grid, freqs[k]) for k in range(nprops)]  # each [grid_n, D]

    raw_errs, cleanup_errs = [], []
    for e in range(n_el):
        vals = torch.tensor([norm_cols[k][e] for k in range(nprops)], dtype=torch.float64)
        present = [k for k in range(nprops) if not torch.isnan(vals[k])]
        if len(present) < 2:
            continue
        # Bundle: B = sum_k role_k (*) enc_k(v_k), unit-magnitude FPE bound to role.
        bundle = torch.zeros(n_dim, dtype=torch.complex64)
        for k in present:
            enc_k = fpe_encode(vals[k:k + 1], freqs[k]).view(-1)  # [D]
            bundle = bundle + roles[k] * enc_k

        def decode_slot(residual, k):
            unbound = residual * roles[k].conj()
            scores = (grid_codes[k].conj() * unbound.view(1, -1)).sum(dim=1).real
            gi = int(torch.argmax(scores))
            return grid[gi], gi

        # RAW: single unbind + nearest-grid, no interference removal.
        for k in present:
            dec, _ = decode_slot(bundle, k)
            raw_errs.append(abs(float(dec) - float(vals[k])))

        # CLEANUP: resonator-style iterative interference subtraction (CSim add-on).
        est = {}
        for k in present:
            _, gi = decode_slot(bundle, k)
            est[k] = gi
        for _ in range(cleanup_iters):
            for k in present:
                resid = bundle.clone()
                for m in present:
                    if m == k:
                        continue
                    resid = resid - roles[m] * grid_codes[m][est[m]]
                _, gi = decode_slot(resid, k)
                est[k] = gi
        for k in present:
            cleanup_errs.append(abs(float(grid[est[k]]) - float(vals[k])))

    med = lambda xs: float(torch.tensor(xs, dtype=torch.float64).median()) if xs else float("nan")
    return dict(raw_median_rel_err=med(raw_errs), cleanup_median_rel_err=med(cleanup_errs),
                n_decoded=len(present) if n_el else 0, bundle_size=len(_PROP_NAMES))


# --------------------------------------------------------------------------- #
# One seed                                                                     #
# --------------------------------------------------------------------------- #
def run_seed(pt: dict, cfg: dict, seed: int) -> dict:
    """Run all arms for one seed. Returns per-arm skill (overall + strata) + diagnostics + preds."""
    n_dim = cfg["n_dim"]
    gen = torch.Generator(device="cpu").manual_seed(seed)
    n_el = pt["n"]
    nprops = len(_PROP_NAMES)

    # Channel A (REAL KGStore).
    store, rel_sig = build_relational_store(pt, n_dim, gen)
    n_triples = len(store)

    # Random per-property base frequencies (Gaussian) + level endpoints + roles (complex phase).
    freqs = torch.randn(nprops, n_dim, generator=gen, dtype=torch.float32) * cfg["fpe_freq_std"]
    v_lo = (torch.randn(n_dim, generator=gen, dtype=torch.float32))
    v_hi = (torch.randn(n_dim, generator=gen, dtype=torch.float32))
    role_phase = (torch.rand(nprops, n_dim, generator=gen, dtype=torch.float32) * 2 - 1) * math.pi
    roles = torch.exp(torch.complex(torch.zeros_like(role_phase), role_phase)).to(torch.complex64)
    rand_sig = torch.randn(n_el, n_dim, generator=gen, dtype=torch.float32)

    norm_cols = [_norm_prop(pt["props"][:, k]) for k in range(nprops)]
    known = [~torch.isnan(pt["props"][:, k]) for k in range(nprops)]

    # Relational similarity (Channel A).
    sim_rel = _cos_sim_real(rel_sig)
    sim_rel_n = sim_rel / sim_rel.abs().max().clamp_min(1e-12)
    sim_rand = _cos_sim_real(rand_sig)

    # Per-target attribute encodings (exclude the target from the bundle -> no leakage).
    per_arm = {a: {} for a in ARMS}
    preds_cat = {a: [] for a in ARMS}
    strata_preds = {a: {"interior": [], "boundary": []} for a in ARMS}
    n_units = 0

    for t in range(nprops):
        others = [k for k in range(nprops) if k != t]
        # FPE attribute vector = bundle_{k!=t} role_k (*) FPE_k(v_k).
        attr_fpe = torch.zeros(n_el, n_dim, dtype=torch.complex64)
        attr_lvl = torch.zeros(n_el, n_dim, dtype=torch.float32)
        raw_feat = torch.zeros(n_el, len(others), dtype=torch.float64)
        for j, k in enumerate(others):
            attr_fpe = attr_fpe + roles[k] * fpe_encode(norm_cols[k], freqs[k])
            attr_lvl = attr_lvl + level_encode(norm_cols[k], v_lo, v_hi)
            raw_feat[:, j] = torch.nan_to_num(norm_cols[k], nan=0.0)
        sim_fpe = _cos_sim_real(attr_fpe)
        sim_lvl = _cos_sim_real(attr_lvl)
        sim_fpe_n = sim_fpe / sim_fpe.abs().max().clamp_min(1e-12)
        # RAW_FEATURE_KNN: kNN on the RAW normalized OTHER features (informative reference).
        d2 = torch.cdist(raw_feat, raw_feat) ** 2
        sim_raw = torch.exp(-d2)

        fused_fpe = sim_rel_n + cfg["lam"] * sim_fpe_n
        fused_lvl = sim_rel_n + cfg["lam"] * (sim_lvl / sim_lvl.abs().max().clamp_min(1e-12))

        target_raw = pt["props"][:, t]
        kn = known[t]
        # DEGREE baseline: weight by graph degree (constant per neighbor, ignores query identity).
        deg = torch.zeros(n_el, dtype=torch.float64)
        for e in range(n_el):
            same = sum(1 for j2 in range(n_el)
                       if j2 != e and (pt["group"][j2] == pt["group"][e]
                                       or pt["period"][j2] == pt["period"][e]))
            deg[e] = float(same)
        sim_deg = deg.view(1, -1).repeat(n_el, 1)  # every row identical -> query-agnostic

        arm_sims = {
            RANDOM: sim_rand,
            A_ALONE: sim_rel_n,
            B_ALONE: sim_fpe_n,
            A_PLUS_B_FPE: fused_fpe,
            A_PLUS_B_LEVEL: fused_lvl,
            RAW_FEATURE_KNN: sim_raw,
            DEGREE: sim_deg,
        }
        for a, sim in arm_sims.items():
            preds = _predict_loo(sim, target_raw, kn, cfg["weight_exp"])
            per_arm[a][t] = preds
            preds_cat[a].append(preds[kn])
        # MEAN baseline.
        mean_pred = torch.full((n_el,), float("nan"), dtype=torch.float64)
        mean_pred[kn] = target_raw[kn].to(torch.float64).mean()
        per_arm[MEAN][t] = mean_pred
        preds_cat[MEAN].append(mean_pred[kn])
        n_units += int(kn.sum())

    # --- SYNTHETIC EXOGENOUS POSITIVE CONTROL (machinery proof) ---
    # An exogenous scalar assigned INDEPENDENTLY of group/period/block. Channel A
    # (relational) cannot predict it; the FPE numeric channel can. If A+B beats A
    # here, the ablation DETECTS a load-bearing exogenous channel -> the real-data
    # verdict (redundant or not) is trustworthy. This is the ship-ability gate.
    perm = torch.randperm(n_el, generator=gen).to(torch.float64)
    x_synth = perm / float(n_el - 1)                 # exogenous, relational-independent, in [0,1]
    all_known = torch.ones(n_el, dtype=torch.bool)
    attr_synth = roles[0] * fpe_encode(x_synth, freqs[0])
    sim_synth = _cos_sim_real(attr_synth)
    sim_synth_n = sim_synth / sim_synth.abs().max().clamp_min(1e-12)
    p_synth_a = _predict_loo(sim_rel_n, x_synth, all_known, cfg["weight_exp"])
    p_synth_ab = _predict_loo(sim_rel_n + cfg["lam"] * sim_synth_n, x_synth, all_known, cfg["weight_exp"])
    skill_synth_a = _skill(p_synth_a, x_synth, all_known)
    skill_synth_ab = _skill(p_synth_ab, x_synth, all_known)
    synth_gap = skill_synth_ab - skill_synth_a

    # Aggregate skill per arm (overall + strata).
    interior = ~pt["boundary"]
    boundary = pt["boundary"]
    arm_skill, arm_skill_int, arm_skill_bnd = {}, {}, {}
    for a in ARMS:
        sk, ski, skb = [], [], []
        for t in range(nprops):
            kn = known[t]
            sk.append(_skill(per_arm[a][t], pt["props"][:, t], kn))
            ski.append(_skill(per_arm[a][t], pt["props"][:, t], kn, subset=interior))
            skb.append(_skill(per_arm[a][t], pt["props"][:, t], kn, subset=boundary))
        arm_skill[a] = float(torch.tensor(sk, dtype=torch.float64).nanmean())
        arm_skill_int[a] = float(torch.tensor(ski, dtype=torch.float64).nanmean())
        arm_skill_bnd[a] = float(torch.tensor(skb, dtype=torch.float64).nanmean())

    # Encoding integrity diagnostics.
    decay_spearman = fpe_distance_decay_spearman(freqs[0])
    decode = decode_diagnostics(pt, freqs, roles, cfg["decode_grid"], cfg["decode_cleanup_iters"])

    # ARMS-MUST-DIFFER (META_RULE_AF): per-arm concatenated prediction vectors.
    import hashlib
    digests = {}
    for a in ARMS:
        cat = torch.cat(preds_cat[a]).to(torch.float64)
        digests[a] = hashlib.sha256(torch.nan_to_num(cat, nan=-999.0).numpy().tobytes()).hexdigest()

    return dict(seed=seed, n_dim=n_dim, n_triples=n_triples, n_units=n_units,
                arm_skill=arm_skill, arm_skill_interior=arm_skill_int,
                arm_skill_boundary=arm_skill_bnd, fpe_decay_spearman=decay_spearman,
                decode=decode, arm_digests=digests,
                synth_skill_a=skill_synth_a, synth_skill_ab=skill_synth_ab, synth_gap=synth_gap)


# --------------------------------------------------------------------------- #
# I/O helpers (start-marker / atomic metrics / crash diagnostic)              #
# --------------------------------------------------------------------------- #
def _out_dir() -> str:
    name = os.environ.get("HDLAB_EXP_NAME", ANCHOR_NAME)
    return os.path.join("data", "exp_" + name)


def _write_start_marker(out_dir: str, run_mode: str, expected_n_units: int) -> None:
    marker = dict(pid=os.getpid(), ts_iso=datetime.now(timezone.utc).isoformat(),
                  anchor_name=ANCHOR_NAME, run_mode=run_mode,
                  expected_n_units=expected_n_units, host=platform.node())
    os.makedirs(out_dir, exist_ok=True)
    tmp = os.path.join(out_dir, "_start_marker.json.tmp")
    final = os.path.join(out_dir, "_start_marker.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, final)


def _write_metrics(out_dir: str, metrics: dict) -> None:
    os.makedirs(out_dir, exist_ok=True)
    tmp = os.path.join(out_dir, "metrics.json.tmp")
    final = os.path.join(out_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, final)


def _write_crash_metrics(out_dir: str, exc: Exception) -> None:
    diag = dict(verdict="CELL_CRASHED", verdict_msg=("%s: %s" % (type(exc).__name__, str(exc)[:500])),
                summary=("CELL_CRASHED: %s" % type(exc).__name__), elapsed_s=0.0,
                traceback=traceback.format_exc()[:5000], ts_iso=datetime.now(timezone.utc).isoformat(),
                pid=os.getpid(), anchor_name=ANCHOR_NAME)
    _write_metrics(out_dir, diag)


# --------------------------------------------------------------------------- #
# Verdict logic                                                                #
# --------------------------------------------------------------------------- #
def _agg(seed_results: list, path: str):
    """Mean over seeds of a nested path like 'arm_skill.A_PLUS_B_FPE'."""
    keys = path.split(".")
    vals = []
    for r in seed_results:
        v = r
        for k in keys:
            v = v[k]
        vals.append(v)
    return float(torch.tensor(vals, dtype=torch.float64).nanmean())


def decide_verdict(seed_results: list) -> dict:
    a_alone = _agg(seed_results, "arm_skill." + A_ALONE)
    b_alone = _agg(seed_results, "arm_skill." + B_ALONE)
    ab_fpe = _agg(seed_results, "arm_skill." + A_PLUS_B_FPE)
    ab_lvl = _agg(seed_results, "arm_skill." + A_PLUS_B_LEVEL)
    rand = _agg(seed_results, "arm_skill." + RANDOM)
    mean_arm = _agg(seed_results, "arm_skill." + MEAN)
    degree = _agg(seed_results, "arm_skill." + DEGREE)
    raw_knn = _agg(seed_results, "arm_skill." + RAW_FEATURE_KNN)
    decay = _agg(seed_results, "fpe_decay_spearman")
    raw_dec = _agg(seed_results, "decode.raw_median_rel_err")
    clean_dec = _agg(seed_results, "decode.cleanup_median_rel_err")
    int_fpe = _agg(seed_results, "arm_skill_interior." + A_PLUS_B_FPE)
    bnd_fpe = _agg(seed_results, "arm_skill_boundary." + A_PLUS_B_FPE)
    synth_gap = _agg(seed_results, "synth_gap")
    synth_a = _agg(seed_results, "synth_skill_a")
    synth_ab = _agg(seed_results, "synth_skill_ab")

    # --- Ship-ability / machinery gates (provable Phase-1 claims) ---
    machinery_ok = synth_gap >= HP_SYNTH_GAP           # ablation detects load-bearing exogenous B
    b_grounds = (b_alone - mean_arm) >= HP_B_ALONE_GROUNDS  # FPE numeric channel carries real info
    encoding_ok = decay >= HP_FPE_DECAY_SPEARMAN
    encoding_broken = decay < HF_ENCODING_SPEARMAN
    decode_degraded = raw_dec > HF_RAW_DECODE_MEDREL
    cleanup_fixes = clean_dec <= HP_DECODE_CLEANUP_MEDREL

    # --- Science headline: is B LOAD-BEARING OVER the native relational channel A ---
    b_beats_a = (ab_fpe - a_alone) >= HP_B_BEATS_A_MARGIN
    b_beats_floor = (ab_fpe - max(rand, 0.0)) >= HP_B_BEATS_FLOOR_MARGIN and ab_fpe > 0.0
    degree_invariant = (bnd_fpe >= int_fpe - HP_DEGREE_INVARIANCE) and (bnd_fpe > 0.0)
    oracle_leak = (int_fpe > 0.0) and (bnd_fpe <= 0.0)

    decode_note = "decode_ok"
    if decode_degraded and cleanup_fixes:
        decode_note = "DECODE_DEGRADATION_NEEDS_CLEANUP_cleanup_recovers"
    elif decode_degraded and not cleanup_fixes:
        decode_note = "DECODE_DEGRADATION_cleanup_insufficient"

    # Failure-mode classification (do NOT conflate the three distinct causes).
    failure_mode = "NONE"
    if encoding_broken:
        # wiring is broken -- not a statement about grounding at all.
        failure_mode = "ENCODING_BROKEN"
    elif not machinery_ok:
        # the ablation cannot detect a load-bearing channel even when one is injected.
        failure_mode = "ABLATION_MACHINERY_INSENSITIVE"
    elif not b_grounds:
        # numeric channel carries no exogenous info even alone -> genuine grounding negative.
        failure_mode = "GROUNDING_NEGATIVE_B_CARRIES_NOTHING"
    elif oracle_leak:
        failure_mode = "ORACLE_LEAK_VIA_SMOOTHNESS"
    elif not b_beats_a:
        # B carries real info (b_grounds) and the machinery works (synth) but B is
        # REDUNDANT with the native relational channel on THIS domain (A was built
        # from the properties). Distinct from B carrying nothing.
        failure_mode = "GROUNDING_REDUNDANT_WITH_RELATIONAL"

    # HARD_PASS = B is load-bearing OVER A (strong grounding). Requires the machinery/
    # encoding/decode to be valid first, else the comparison is not trustworthy.
    hard_pass = (machinery_ok and encoding_ok and cleanup_fixes and b_grounds
                 and b_beats_a and b_beats_floor and degree_invariant and (ab_fpe > mean_arm))

    if hard_pass:
        verdict = "HARD_PASS"
    elif failure_mode in ("ENCODING_BROKEN", "ABLATION_MACHINERY_INSENSITIVE",
                          "GROUNDING_NEGATIVE_B_CARRIES_NOTHING", "ORACLE_LEAK_VIA_SMOOTHNESS"):
        verdict = "HARD_FAIL"
    elif failure_mode == "GROUNDING_REDUNDANT_WITH_RELATIONAL":
        # A pre-registered, scientifically-informative outcome: the wiring works and B
        # grounds, but not OVER the native relational channel on this domain.
        verdict = "MIDDLE_BAND"
    else:
        verdict = "MIDDLE_BAND"

    msg = ("%s | [science] A+B_FPE=%.3f A_alone=%.3f (d=%+.3f) B_alone=%.3f A+B_lvl=%.3f "
           "RAW_KNN=%.3f RANDOM=%.3f DEGREE=%.3f MEAN=%.3f "
           "| [machinery] synth A=%.3f A+B=%.3f gap=%.3f | [encoding] decay=%.3f "
           "decode raw=%.3f clean=%.3f (%s) | interior_fpe=%.3f boundary_fpe=%.3f "
           "| failure_mode=%s"
           % (verdict, ab_fpe, a_alone, ab_fpe - a_alone, b_alone, ab_lvl, raw_knn, rand,
              degree, mean_arm, synth_a, synth_ab, synth_gap, decay, raw_dec, clean_dec,
              decode_note, int_fpe, bnd_fpe, failure_mode))
    return dict(verdict=verdict, verdict_msg=msg, failure_mode=failure_mode, decode_note=decode_note,
                b_beats_a=bool(b_beats_a), b_beats_floor=bool(b_beats_floor),
                machinery_ok=bool(machinery_ok), b_grounds=bool(b_grounds),
                encoding_ok=bool(encoding_ok), degree_invariant=bool(degree_invariant),
                cleanup_fixes=bool(cleanup_fixes),
                agg=dict(a_alone=a_alone, b_alone=b_alone, ab_fpe=ab_fpe, ab_lvl=ab_lvl,
                         raw_knn=raw_knn, rand=rand, degree=degree, mean=mean_arm,
                         synth_a=synth_a, synth_ab=synth_ab, synth_gap=synth_gap,
                         fpe_decay_spearman=decay, raw_decode=raw_dec, cleanup_decode=clean_dec,
                         interior_fpe=int_fpe, boundary_fpe=bnd_fpe))


# --------------------------------------------------------------------------- #
# Validity preflight (F.1-F.4 ENFORCE + original 4)                            #
# --------------------------------------------------------------------------- #
def _validity_checks(pt: dict, cfg: dict) -> None:
    """Run the mandated validity-preflight declarations at self-test scale. Raises under enforce."""
    # F.1 / F.2 / F.3: construct + ingest the REAL KGStore at tiny scale.
    exercised = set()
    gsmall = torch.Generator(device="cpu").manual_seed(1)
    store_small = KGStore(6, 2, 16, gsmall)         # BASE/portable kwargs only
    exercised.add("KGStore")
    store_small.ingest_triples(torch.tensor([[0, 0, 4], [1, 1, 5], [2, 0, 4]], dtype=torch.long))
    assert len(store_small) == 3, "ingest_triples did not register triples"
    exercised.add("ingest_triples")

    # Discriminator-preview: run the REAL mechanism on the REAL data (2 seeds).
    seed_results = [run_seed(pt, cfg, s) for s in cfg["seeds"]]
    dv = decide_verdict(seed_results)
    agg = dv["agg"]

    # metric-moves: FPE similarity must MOVE with input (dv=0 vs dv=0.5).
    freqs = torch.randn(1, cfg["n_dim"], generator=torch.Generator().manual_seed(3),
                        dtype=torch.float32) * cfg["fpe_freq_std"]
    enc0 = fpe_encode(torch.tensor([0.0], dtype=torch.float64), freqs[0])
    enc_same = fpe_encode(torch.tensor([0.0], dtype=torch.float64), freqs[0])
    enc_half = fpe_encode(torch.tensor([0.5], dtype=torch.float64), freqs[0])
    cos_same = float((enc0.view(-1) * enc_same.view(-1).conj()).sum().real / cfg["n_dim"])
    cos_half = float((enc0.view(-1) * enc_half.view(-1).conj()).sum().real / cfg["n_dim"])

    # negative-control margin: RANDOM arm skill across seeds must fail "b_beats_a" bar with margin.
    rand_scores = [r["arm_skill"][RANDOM] for r in seed_results]
    a_alone_ref = agg["a_alone"]

    # ARMS-MUST-DIFFER exercised at self-test (fail-closed gate).
    import hashlib
    d0 = seed_results[0]["arm_digests"]
    pairs = [(x, y) for i, x in enumerate(ARMS) for y in ARMS[i + 1:]]
    arms_differ = all(d0[x] != d0[y] for x, y in pairs)
    assert arms_differ, "META_RULE_AF: two arms produced bit-identical predictions"
    # cardinality exercised at self-test.
    expected_units = len(cfg["seeds"]) * sum(int((~torch.isnan(pt["props"][:, k])).sum())
                                             for k in range(len(_PROP_NAMES)))
    got_units = sum(r["n_units"] for r in seed_results)
    cardinality_ok = (got_units == expected_units)
    assert cardinality_ok, "cardinality breach: got %d expected %d" % (got_units, expected_units)

    run_validity_preflight([
        # F.1: real substrate code path exercised (ENFORCE).
        {"kind": "real_code_path",
         "full_substrate_entrypoints": ["KGStore", "ingest_triples"],
         "exercised_entrypoints": sorted(exercised)},
        # F.2/F.3: KGStore call binds the live signature with BASE kwargs (ENFORCE).
        {"kind": "substrate_signature", "callable_obj": KGStore, "callable_name": "KGStore",
         "kwargs": {"n_ent": 1, "n_rel": 1, "n_dim": 16, "generator": None}},
        # F.4: A_ALONE (the ablation baseline) must be ABOVE the RANDOM floor, so the
        # A-vs-A+B comparison is against a genuine non-floor baseline (not a structural 0).
        {"kind": "guard_baseline_valid", "baseline_score": agg["a_alone"],
         "floor_score": max(agg["rand"], 0.0), "guard_name": "ablation_needs_nonfloor_A",
         "baseline_name": "A_ALONE", "floor_name": "RANDOM", "eps": 0.02},
        # POSITIVE control = the SYNTHETIC exogenous channel machinery. A+B MUST beat A
        # when a genuinely load-bearing exogenous channel is injected -> proves the
        # ablation can detect load-bearing B, so the real-data verdict is trustworthy.
        {"kind": "positive_control",
         "positive_control_passed_headline_gate": agg["synth_gap"] >= HP_SYNTH_GAP,
         "control_name": "SYNTH_exogenous(A+B beats A)", "headline_name": "synth_ablation_gap"},
        {"kind": "metric_moves", "metric_name": "fpe_similarity",
         "before": cos_half, "after": cos_same},
        {"kind": "full_gates_exercised",
         "full_fail_closed_gates": ["arms_differ", "cardinality"],
         "exercised_gates": ["arms_differ", "cardinality"]},
        # negative control = RANDOM similarity must fail the "grounds above mean" bar.
        {"kind": "negative_control_margin", "control_scores": rand_scores,
         "headline_threshold": HP_B_ALONE_GROUNDS, "higher_is_pass": True, "margin": 0.0,
         "n_repeats_min": 2, "control_name": "RANDOM_similarity"},
    ], run_mode="selftest")

    # Discriminator-fires: the MACHINERY must fire (synth) + the FPE numeric channel must
    # carry real exogenous info (B_alone > MEAN). We do NOT gate ship on the real-data
    # "B beats A" -- that IS the FULL science question this cell exists to answer.
    assert agg["synth_gap"] >= HP_SYNTH_GAP, (
        "ABLATION MACHINERY DID NOT FIRE: synth A+B-A gap=%.3f < %.3f; the test cannot "
        "detect a load-bearing exogenous channel; do NOT ship." % (agg["synth_gap"], HP_SYNTH_GAP))
    assert (agg["b_alone"] - agg["mean"]) >= HP_B_ALONE_GROUNDS, (
        "FPE numeric channel does not ground: B_alone=%.3f <= MEAN+%.3f; wiring carries no "
        "exogenous info; do NOT ship." % (agg["b_alone"], HP_B_ALONE_GROUNDS))
    assert agg["a_alone"] > 0.05, "baseline A_ALONE below band (%.3f); regime too hard" % agg["a_alone"]
    assert agg["a_alone"] < 0.95, "baseline A_ALONE saturated (%.3f); no headroom" % agg["a_alone"]
    print("[self-test] validity + machinery + wiring PASS: %s" % dv["verdict_msg"], flush=True)


# --------------------------------------------------------------------------- #
# main                                                                         #
# --------------------------------------------------------------------------- #
def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true", help="fast validity + discriminator preview")
    ap.add_argument("--smoke", action="store_true", help="reduced-grid run")
    args, _ = ap.parse_known_args()

    pt = load_periodic()

    if args.self_test:
        _validity_checks(pt, dict(SELFTEST_CFG))
        print("SELFTEST_PASS", flush=True)
        return

    cfg = dict(SELFTEST_CFG) if args.smoke else dict(FULL_CFG)
    run_mode = "smoke" if args.smoke else "full"
    out_dir = _out_dir()
    expected_units = len(cfg["seeds"]) * sum(int((~torch.isnan(pt["props"][:, k])).sum())
                                             for k in range(len(_PROP_NAMES)))
    _write_start_marker(out_dir, run_mode, expected_units)

    t0 = time.perf_counter()
    seed_results = []
    for s in cfg["seeds"]:
        rs = run_seed(pt, cfg, s)
        seed_results.append(rs)
        print("[progress] seed=%d done A+B_FPE=%.3f A_alone=%.3f decay=%.3f elapsed=%.1fs"
              % (s, rs["arm_skill"][A_PLUS_B_FPE], rs["arm_skill"][A_ALONE],
                 rs["fpe_decay_spearman"], time.perf_counter() - t0), flush=True)

    dv = decide_verdict(seed_results)
    elapsed = time.perf_counter() - t0

    got_units = sum(r["n_units"] for r in seed_results)
    cardinality_ok = (got_units == expected_units)
    verdict = dv["verdict"]
    verdict_msg = dv["verdict_msg"]
    if not cardinality_ok:
        verdict = "HARD_FAIL_CARDINALITY_BREACH_META_RULE_H"
        verdict_msg = "cardinality breach: got %d expected %d | %s" % (got_units, expected_units, verdict_msg)

    metrics = dict(
        verdict=verdict, verdict_msg=verdict_msg,
        summary=("%s A+B_FPE=%.3f vs A_alone=%.3f decode=%s"
                 % (verdict, dv["agg"]["ab_fpe"], dv["agg"]["a_alone"], dv["decode_note"])),
        elapsed_s=round(elapsed, 3), run_mode=run_mode, anchor_name=ANCHOR_NAME,
        n_dim=cfg["n_dim"], n_seeds=len(cfg["seeds"]), expected_n_units=expected_units,
        got_n_units=got_units, cardinality_ok=cardinality_ok,
        failure_mode=dv["failure_mode"], decode_note=dv["decode_note"],
        agg=dv["agg"], gates=dict(b_beats_a=dv["b_beats_a"], b_beats_floor=dv["b_beats_floor"],
                                  encoding_ok=dv["encoding_ok"], degree_invariant=dv["degree_invariant"],
                                  cleanup_fixes=dv["cleanup_fixes"]),
        per_seed=[dict(seed=r["seed"], n_triples=r["n_triples"], n_units=r["n_units"],
                       arm_skill=r["arm_skill"], arm_skill_interior=r["arm_skill_interior"],
                       arm_skill_boundary=r["arm_skill_boundary"],
                       fpe_decay_spearman=r["fpe_decay_spearman"], decode=r["decode"])
                  for r in seed_results],
        ts_iso=datetime.now(timezone.utc).isoformat(), host=platform.node(),
    )
    _write_metrics(out_dir, metrics)
    print("[done] %s" % verdict_msg, flush=True)


if __name__ == "__main__":
    _od = _out_dir()
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # NOT BaseException; preserves SystemExit + KeyboardInterrupt
        _write_crash_metrics(_od, e)
        raise
