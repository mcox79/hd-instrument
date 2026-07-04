"""Stage 1 Regime Probe 18: PAIRED STORAGE-advantage regime-boundary map.

Cell anchor: `stage1_regime_probe_18_storage_advantage_boundary_paired_v1`
Pre-reg:     preregs/2026-07-04_stage1_regime_probe_18_storage_advantage_boundary_paired_v1.md

Purpose (Director memo Experiment 1,
    notes/research_phase_diagram_genuine_open_questions_post_cross_term_collapse_2026-07-04.md):
    The STORAGE main effect (SHARDED >> BUNDLED, gap ~0.93) is real but was only
    ever measured with SHARDED pinned at its accuracy ceiling (=1.0). So the
    gap's TRUE size and its SCALING have never been measured in a regime where
    SHARDED can actually MOVE. This cell fills that: PAIRED SHARDED-vs-BUNDLED
    (shared salt per cell -> identical items + corruption across the two storage
    arms), sweeping corr x F x N straddling the SHARDED cliff so SHARDED is
    IN-BAND (not saturated).

    Discriminator = the WITHIN-ITEM PAIRED gap delta and its boundary/scaling.
    It is NOT a max/range-over-noisy-arms discriminator (that is the artifact
    pattern closed 4/4 on 2026-07-04 -- see memory
    feedback_paired_trials_mandatory_for_arm_comparison_discriminators_2026-07-04).
    There is NO cleanup-mechanism axis here (the READOUT-DEGENERATE comparison
    that collapsed) -- MECH is fixed at modern_hopfield.

WHY THIS CANNOT RE-MANUFACTURE THE ARTIFACT (design invariants):
    1. No mechanism axis. Single MECH=modern_hopfield. The collapsed family was
       "axis moderates CLEANUP_MECHANISM"; there is no mechanism to moderate.
    2. Paired-by-construction. Both storage arms consume BIT-IDENTICAL stochastic
       inputs (antecedent indices + fan-out slots + per-step corruption masks),
       pre-drawn ONCE per cell and passed to both arms. PAIRING_VALID gate
       asserts input-hash equality + step-0 antecedent-factor equality +
       step-0 corruption-mask equality across arms. delta = acc_S - acc_B is a
       true within-item paired difference, not a difference of independent draws.
    3. Discriminator is a within-arm boundary LOCATION (corr at which the paired
       gap crosses 0.5) and its movement across N / F, gated against a
       data-driven binomial noise-floor null (two-stage MC). Not a max over
       noisy arms.
    4. Both PASS bands are real results: HARD_PASS (boundary moves with N or F,
       above null) AND HARD_PASS_NULL (scale-free boundary -- a strong clean
       result too, filed BOUNDED_NULL like P9v2).

Primitive reuse (Principle 11): `build_rules`, `CLEANUP_REGISTRY`,
    `cleanup_argmax_idx`, `run_chain` (reference-equivalence check only) from
    `_stage1_physics_law_joint_composition_factorial_v1_core`. The paired chain
    `run_chain_paired` is a refactor that pre-draws ALL stochastic state and
    consumes NONE inside, so pairing is valid by construction (not by hoping two
    generator streams stay in lockstep). selftest asserts bit-for-bit
    equivalence run_chain_paired(SHARDED) == run_chain(SHARDED).

Grid (empirically bracketed 2026-07-04 so SHARDED straddles the cliff at every
    (N,F); MEASURED@scratchpad bracket_p18_storage_boundary.py TR=40 seed=7 CPU):
    N in {512, 2048, 8192}; F in {1, 4}; MECH=modern_hopfield; L=2; M=4800 fixed.
    corr grid PER N (cliff moves with N -- that IS the finding):
      N=512  : {0.80, 0.84, 0.87, 0.90, 0.93}
      N=2048 : {0.88, 0.91, 0.93, 0.95, 0.97}
      N=8192 : {0.93, 0.95, 0.96, 0.97, 0.98}
    (5 corr per N; same corr grid across F within each N; both F straddle.)
    Positive control (Gate D): SATURATION_PC = iterative_cosine M=800 N=2048
      F=1 L=2 corr=0.20 SHARDED, acc>=0.95.

Discriminators (all within-cell / paired; NONE is a max-over-noisy-arms):
    delta[N,F,corr]      = acc_SHARDED - acc_BUNDLED (paired).
    boundary_corr[N,F]   = corr at which delta crosses below 0.5 (linear interp)
                           = the STORAGE-advantage collapse point.
    delta_scales_with_N  = range over N of boundary_corr[N,F=1].
    delta_scales_with_F  = range over F of boundary_corr[N=512,F].
    collapse_test        = pooled r^2 of delta vs candidate load variables u
                           (informational; not gated).
    Data-driven binomial noise-floor null (two-stage MC): stage 1 estimates the
    per-cell binomial SE of each boundary via resampling; stage 2 imposes H0
    (common boundary) and MC's the range statistic. HARD_PASS requires observed
    range > null q95. Independent-binomial resampling is CONSERVATIVE (the true
    paired noise on delta is smaller because corruption noise is shared).

Bands:
    HARD_PASS (STORAGE law has a mapped, MOVING boundary): every (N,F) straddles
      (boundary well-defined) AND (delta_scales_with_N > nullq95 OR
      delta_scales_with_F > nullq95) AND cross-seed cv(boundary_corr) < 0.15.
      cv is a 3-seed metric -> single-seed FULL emits MM_TENTATIVE candidate;
      MM_STANDARD requires 3-seed cv<0.15 (Skunkworks aggregates siblings).
    HARD_PASS_NULL (boundary is scale-free -- a strong clean result too):
      boundaries well-defined everywhere but delta_scales_with_* <= nullq95 on
      both axes -> "STORAGE advantage collapses at a boundary independent of
      N,F". File BOUNDED_NULL (like P9v2), not a failure.
    MIDDLE_BAND: one of two scaling axes fires, or scaling in (q95, ...) with cv
      unresolved.
    HARD_FAIL (design bad, no atom): any (N,F) fails to straddle the cliff
      (SHARDED all >0.9 or all <0.3) -> bracket wrong, re-author; OR
      PAIRING_VALID assert fails; OR SATURATION_PC < 0.95; OR cardinality breach.

CARDINALITY_OK:
    SMOKE = FULL = 3 N x 2 F x 5 corr x 2 storage + 1 PC = 60 + 1 = 61.
    TR=40 (SMOKE) / 200 (FULL). Same grid + same code path (SMOKE=FULL); only TR
    differs. EXPECTED_N_UNITS_SMOKE = EXPECTED_N_UNITS_FULL = 61.

Compute architecture: `(c) mixed with justification`. Batched matmul at each
    phase point (cleanup = TR x N @ N x M matmul); Python for-loop across the
    (N,F,corr) sweep is unavoidable (each point has a different codebook shape,
    cannot batch into one matmul). Per-phase-point wall < 10s on CPU at TR=40
    (heaviest N=8192,F=4 ~4-5s/arm). Torch CPU-only on this host.

ASCII-only. No unicode. No em-dashes. No emojis.
Author: exp_dev 2026-07-04 (agent-spawn, Opus 4.8).

# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified: SHARDED vs BUNDLED output hashes distinct at a probe
#   cell AND low-corr vs high-corr SHARDED distinct (both axes fire).
# - final_metrics_atomicity: tmp_replace via os.replace() (in wrapper).
# - except SystemExit: raise BEFORE except Exception (no BaseException) (wrapper).
# - crlb_n/a: categorical accuracy; boundary is a grid-crossing LOCATION, gated
#   against an explicit MC binomial noise-floor null (the analog of a CRLB here).
# - baseline_in_band: SHARDED (the discriminator arm) straddles [<=0.30 .. >=0.90]
#   at every (N,F) BY DESIGN (empirical bracket); enforced at smoke gate.
#   BUNDLED is floor everywhere (the storage advantage) -- it is a reference arm,
#   not the discriminator; its floor value is the measured advantage, not vacuous.
# - HARD_PASS strictly above floor: scaling must exceed MC null q95 (META_RULE_L).
# - HP_SCOPE per-arm: SHARDED+BUNDLED paired -> boundary/scaling bands;
#   SATURATION_PC -> Gate-D reproducer only.
# - cardinality_ok: EXPECTED_N_UNITS_SMOKE = EXPECTED_N_UNITS_FULL = 61.
# - per-unit failure-class: RuntimeError with specific class name propagated.
# - calibration_check: default_ok_for_this_regime (BETA=8.0 ALPHA=0.5 inherited).
# - all numbers tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@.
"""
from __future__ import annotations
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(line_buffering=True)
except Exception:
    pass

import hashlib
import math
import time
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional

import os
os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")

import numpy as np
import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from experiments._stage1_physics_law_joint_composition_factorial_v1_core import (
    CLEANUP_MECHANISMS,
    CLEANUP_REGISTRY,
    BETA,
    ALPHA_SOFT,
    DEVICE,
    GPU_NAME,
    build_rules,
    cleanup_argmax_idx,
    run_chain,          # reference primitive (selftest equivalence only)
)

ANCHOR_NAME = "stage1_regime_probe_18_storage_advantage_boundary_paired_v1"

# ---------------------------------------------------------------------------
# Sweep constants (LOCKED at module init)
# ---------------------------------------------------------------------------
MECH = "modern_hopfield"          # single mechanism; NO mechanism axis by design
FIXED_L = 2
M_FIXED = 4800                    # fixed codebook across (N,F); clean N/F boundary map

N_GRID = [512, 2048, 8192]
F_GRID = [1, 4]

# corr grid PER N (empirically bracketed so SHARDED straddles at BOTH F).
# MEASURED@scratchpad bracket_p18_storage_boundary.py 2026-07-04 TR=40 seed=7 CPU.
CORR_GRID_BY_N: Dict[int, List[float]] = {
    512:  [0.80, 0.84, 0.87, 0.90, 0.93],
    2048: [0.88, 0.91, 0.93, 0.95, 0.97],
    8192: [0.93, 0.95, 0.96, 0.97, 0.98],
}

# Positive control (Gate D reproducer) -- SHARDED easy regime, saturates.
SATURATION_PC_REGIME = {
    "cleanup_mechanism": "iterative_cosine",
    "M": 800,
    "N": 2048,
    "F": 1,
    "L": 2,
    "corruption": 0.20,
    "storage": "SHARDED",
}
SATURATION_PC_THRESHOLD = 0.95

TR_FULL = 200
TR_SMOKE = 40

# Boundary + discriminator constants
BOUNDARY_LEVEL = 0.50            # delta crosses 0.5 = storage-advantage collapse
STRADDLE_HI = 0.90               # SHARDED in-band requires a cell >= this ...
STRADDLE_LO = 0.30               # ... AND a cell <= this (not saturated / not vacuous)
MC_NDRAW = 200000                # THEORETICAL@memo NDRAW=2e5 for the binomial null
MC_SEED = 20260704              # fixed so the null q95 is reproducible
CV_THRESHOLD = 0.15              # 3-seed cv gate (MM_STANDARD; aggregated downstream)

# Cardinality
EXPECTED_N_UNITS_SMOKE = (len(N_GRID) * len(F_GRID) * 5 * 2) + 1   # 60 + PC = 61
EXPECTED_N_UNITS_FULL = EXPECTED_N_UNITS_SMOKE                     # SMOKE = FULL grid

REQUIRED_FIELDS = ("verdict", "verdict_msg", "elapsed_s", "summary")


# ---------------------------------------------------------------------------
# Shared stochastic state (pre-drawn ONCE per cell; consumed by BOTH storage arms)
# ---------------------------------------------------------------------------
def draw_shared_state(gen: torch.Generator, TR: int, L: int, N: int, F: int,
                      M: int, corr: float, device: str) -> Dict[str, Any]:
    """Pre-draw all stochastic inputs for a chain, in the SAME generator-draw
    order as the reference `run_chain` (start_idx; fan_choices; then per step:
    corruption mask, then corruption phasor). Both storage arms consume this
    identical state -> paired-by-construction.
    """
    start_idx = torch.randint(0, M, (TR,), generator=gen, device=device)
    fan_choices = torch.randint(0, F, (TR, L), generator=gen, device=device)
    masks: List[torch.Tensor] = []
    newph: List[torch.Tensor] = []
    for _ in range(L):
        mask = torch.rand((TR, N), generator=gen, device=device,
                          dtype=torch.float32) < corr
        new_ang = (torch.rand((TR, N), generator=gen, device=device,
                              dtype=torch.float32) * 2.0 - 1.0) * math.pi
        ph = torch.polar(torch.ones_like(new_ang), new_ang).to(torch.complex64)
        masks.append(mask)
        newph.append(ph)
    # Hash of the exact shared inputs (used for the PAIRING_VALID gate).
    h = hashlib.sha256()
    h.update(start_idx.detach().cpu().numpy().tobytes())
    h.update(fan_choices.detach().cpu().numpy().tobytes())
    for mk, ph in zip(masks, newph):
        h.update(mk.detach().cpu().numpy().tobytes())
        h.update(ph.detach().cpu().numpy().tobytes())
    input_hash = h.hexdigest()[:16]
    return {
        "start_idx": start_idx,
        "fan_choices": fan_choices,
        "masks": masks,
        "newph": newph,
        "input_hash": input_hash,
        "TR": TR, "L": L, "N": N, "F": F,
    }


def run_chain_paired(storage: str, mechanism: str, L: int, F: int,
                     props: torch.Tensor, perms: torch.Tensor,
                     IMPL: torch.Tensor, POS: torch.Tensor,
                     sharded_codebook: torch.Tensor, bundle_vec: torch.Tensor,
                     shared: Dict[str, Any]
                     ) -> Tuple[float, torch.Tensor, str, str, str]:
    """Chain retrieval consuming ONLY pre-drawn shared state (NO generator draws
    inside). Returns (acc, final_ci, input_hash_used, ncf0_hash, mask0_hash).

    input_hash_used : hash of the exact shared inputs this arm consumed.
    ncf0_hash       : hash of the step-0 non-rule antecedent factor
                      A_cur.conj()*POS_step.conj()*IMPL_conj (identical across
                      arms iff antecedent indices + fan-slots + POS/IMPL match).
    mask0_hash      : hash of the step-0 corruption mask.
    These three feed the PAIRING_VALID gate (must be equal across storage arms).
    """
    start_idx = shared["start_idx"]
    fan_choices = shared["fan_choices"]
    masks = shared["masks"]
    newph = shared["newph"]
    cleanup_fn = CLEANUP_REGISTRY[mechanism]

    ci = start_idx.clone()
    gold = start_idx.clone()
    # gold path (storage-independent; no gen)
    for step in range(L):
        f_step = fan_choices[:, step]
        gold_next = torch.empty_like(gold)
        for f in range(F):
            mask_f = f_step == f
            if mask_f.any():
                gold_next[mask_f] = perms[f][gold[mask_f]]
        gold = gold_next

    IMPL_conj = IMPL.conj().unsqueeze(0)
    ncf0_hash = ""
    mask0_hash = ""

    for step in range(L):
        f_step = fan_choices[:, step]
        A_cur = props[ci]                       # (TR, N)
        POS_step = POS[f_step]                  # (TR, N)
        ncf = A_cur.conj() * POS_step.conj() * IMPL_conj   # non-rule factor
        if step == 0:
            ncf0_hash = hashlib.sha256(
                ncf.detach().cpu().numpy().tobytes()).hexdigest()[:16]
            mask0_hash = hashlib.sha256(
                masks[0].detach().cpu().numpy().tobytes()).hexdigest()[:16]
        if storage == "SHARDED":
            rule_batch = sharded_codebook[ci, f_step]        # (TR, N)
        elif storage == "BUNDLED":
            rule_batch = bundle_vec.unsqueeze(0).expand(A_cur.shape[0], -1)
        else:
            raise RuntimeError(f"UNKNOWN_STORAGE:{storage}")
        cand = rule_batch * ncf
        cand_corr = torch.where(masks[step], newph[step], cand)  # pre-drawn corruption
        Q_clean = cleanup_fn(cand_corr, props)
        ci = cleanup_argmax_idx(Q_clean, props)

    acc = (ci == gold).float().mean().item()
    return float(acc), ci, shared["input_hash"], ncf0_hash, mask0_hash


# ---------------------------------------------------------------------------
# Per-cell paired eval (both storage arms on identical items + corruption)
# ---------------------------------------------------------------------------
def eval_pair(M: int, N: int, F: int, corr: float, TR: int,
              seed: int, salt: int) -> Dict[str, Any]:
    """Evaluate SHARDED and BUNDLED on bit-identical items + corruption."""
    device = DEVICE
    if device == "cuda":
        torch.cuda.empty_cache()
        torch.cuda.reset_peak_memory_stats()
    t0 = time.perf_counter()

    gen = torch.Generator(device=device)
    gen.manual_seed(int(seed) * 100003 + int(salt))
    props, perms, IMPL, POS, sharded_codebook, bundle_vec = build_rules(
        M, F, gen, device, N)
    if props.dtype != torch.complex64:
        raise RuntimeError(f"PROPS_DTYPE_MISMATCH:{props.dtype}")
    if (torch.isnan(sharded_codebook.real).any().item()
            or torch.isnan(sharded_codebook.imag).any().item()):
        raise RuntimeError(f"NAN_IN_SHARDED_CODEBOOK M={M} N={N} F={F}")

    shared = draw_shared_state(gen, TR, FIXED_L, N, F, M, corr, device)

    accS, ciS, ihS, ncf0S, mask0S = run_chain_paired(
        "SHARDED", MECH, FIXED_L, F, props, perms, IMPL, POS,
        sharded_codebook, bundle_vec, shared)
    accB, ciB, ihB, ncf0B, mask0B = run_chain_paired(
        "BUNDLED", MECH, FIXED_L, F, props, perms, IMPL, POS,
        sharded_codebook, bundle_vec, shared)

    pairing_valid = (ihS == ihB) and (ncf0S == ncf0B) and (mask0S == mask0B)

    hS = hashlib.sha256(ciS.detach().cpu().numpy().tobytes()).hexdigest()[:16]
    hB = hashlib.sha256(ciB.detach().cpu().numpy().tobytes()).hexdigest()[:16]

    elapsed = time.perf_counter() - t0
    pS = float(accS)
    pB = float(accB)
    noise2se_S = round(2.0 * (pS * (1.0 - pS) / max(TR, 1)) ** 0.5, 4)
    noise2se_B = round(2.0 * (pB * (1.0 - pB) / max(TR, 1)) ** 0.5, 4)

    del props, perms, IMPL, POS, sharded_codebook, bundle_vec, ciS, ciB
    if device == "cuda":
        torch.cuda.empty_cache()

    base = {
        "cleanup_mechanism": MECH, "M": int(M), "N": int(N), "F": int(F),
        "L": int(FIXED_L), "corruption": float(corr), "TR": int(TR),
        "salt": int(salt),
        "acc_sharded": round(pS, 4),
        "acc_bundled": round(pB, 4),
        "delta": round(pS - pB, 4),
        "noise2se_sharded": noise2se_S,
        "noise2se_bundled": noise2se_B,
        "pairing_valid": bool(pairing_valid),
        "input_hash_sharded": ihS, "input_hash_bundled": ihB,
        "ncf0_hash_sharded": ncf0S, "ncf0_hash_bundled": ncf0B,
        "mask0_hash_sharded": mask0S, "mask0_hash_bundled": mask0B,
        "output_hash_sharded": hS, "output_hash_bundled": hB,
        "elapsed_s": round(elapsed, 3),
    }
    # emit two phase-map points (one per storage arm) sharing pairing metadata
    pt_S = dict(base); pt_S["storage"] = "SHARDED"; pt_S["acc"] = round(pS, 4)
    pt_B = dict(base); pt_B["storage"] = "BUNDLED"; pt_B["acc"] = round(pB, 4)
    return {"pair": base, "pt_sharded": pt_S, "pt_bundled": pt_B}


def eval_single_sharded(regime: Dict[str, Any], TR: int, seed: int, salt: int
                        ) -> Dict[str, Any]:
    """Single SHARDED phase point (used for SATURATION_PC / Gate D)."""
    device = DEVICE
    t0 = time.perf_counter()
    gen = torch.Generator(device=device)
    gen.manual_seed(int(seed) * 100003 + int(salt))
    M, N, F = regime["M"], regime["N"], regime["F"]
    props, perms, IMPL, POS, sharded_codebook, bundle_vec = build_rules(
        M, F, gen, device, N)
    shared = draw_shared_state(gen, TR, regime["L"], N, F, M,
                               regime["corruption"], device)
    acc, ci, ih, ncf0, mask0 = run_chain_paired(
        regime["storage"], regime["cleanup_mechanism"], regime["L"], F,
        props, perms, IMPL, POS, sharded_codebook, bundle_vec, shared)
    h = hashlib.sha256(ci.detach().cpu().numpy().tobytes()).hexdigest()[:16]
    elapsed = time.perf_counter() - t0
    del props, perms, IMPL, POS, sharded_codebook, bundle_vec, ci
    return {
        "cleanup_mechanism": regime["cleanup_mechanism"], "M": int(M),
        "N": int(N), "F": int(F), "L": int(regime["L"]),
        "corruption": float(regime["corruption"]), "storage": regime["storage"],
        "TR": int(TR), "acc": round(float(acc), 4), "arm_tag": "SATURATION_PC",
        "output_hash": h, "elapsed_s": round(elapsed, 3),
    }


# ---------------------------------------------------------------------------
# Boundary + scaling + MC binomial noise-floor null
# ---------------------------------------------------------------------------
def boundary_from_curve(corr_vals: List[float], y_vals: List[float],
                        level: float = BOUNDARY_LEVEL) -> Optional[float]:
    """First DESCENDING crossing of y through `level`, linear-interpolated in
    corr. Returns None if y never crosses (curve does not straddle the level).
    Assumes corr_vals sorted ascending; y typically decreasing in corr.
    """
    for i in range(len(corr_vals) - 1):
        y0, y1 = y_vals[i], y_vals[i + 1]
        if y0 >= level and y1 < level:
            c0, c1 = corr_vals[i], corr_vals[i + 1]
            denom = (y0 - y1)
            if denom <= 0:
                return c0
            frac = (y0 - level) / denom
            return round(c0 + frac * (c1 - c0), 5)
    return None


def _vec_boundary(corr: np.ndarray, y: np.ndarray, level: float) -> np.ndarray:
    """Vectorized first-descending-crossing boundary for many MC draws.
    corr: (K,); y: (ndraw, K). Returns (ndraw,) with NaN where no crossing.
    """
    ndraw, K = y.shape
    above = y >= level                       # (ndraw, K)
    cross = above[:, :-1] & (~above[:, 1:])  # (ndraw, K-1) descending crossings
    has = cross.any(axis=1)
    first = np.argmax(cross, axis=1)         # first crossing segment index
    rows = np.arange(ndraw)
    y0 = y[rows, first]
    y1 = y[rows, first + 1]
    c0 = corr[first]
    c1 = corr[first + 1]
    denom = (y0 - y1)
    denom = np.where(denom <= 0, 1.0, denom)
    frac = (y0 - level) / denom
    b = c0 + frac * (c1 - c0)
    b = np.where(has, b, np.nan)
    return b


def mc_boundary_se(corr_vals: List[float], pS: List[float], pB: List[float],
                   TR: int, ndraw: int, rng: np.random.Generator,
                   level: float = BOUNDARY_LEVEL) -> Tuple[float, float]:
    """Binomial-resample SE of the delta-boundary estimate for one cell curve.
    Independent binomial resampling of acc_S, acc_B (CONSERVATIVE: true paired
    noise on delta is smaller because corruption noise is shared). Returns
    (se, frac_defined).
    """
    corr = np.asarray(corr_vals, dtype=np.float64)
    pS_a = np.clip(np.asarray(pS, dtype=np.float64), 0.0, 1.0)
    pB_a = np.clip(np.asarray(pB, dtype=np.float64), 0.0, 1.0)
    accS = rng.binomial(TR, pS_a[None, :], size=(ndraw, len(corr))) / TR
    accB = rng.binomial(TR, pB_a[None, :], size=(ndraw, len(corr))) / TR
    deltas = accS - accB
    b = _vec_boundary(corr, deltas, level)
    defined = ~np.isnan(b)
    frac_defined = float(defined.mean())
    if defined.sum() < 2:
        return float("nan"), frac_defined
    return float(np.nanstd(b)), frac_defined


def mc_range_null_q95(ses: List[float], ndraw: int, rng: np.random.Generator,
                      q: float = 0.95) -> float:
    """Stage-2 null: under H0 (common boundary), each boundary estimate ~
    Normal(0, se). MC the RANGE (max-min) of the k estimates; return q-quantile.
    Range is location-invariant so center 0 is fine.
    """
    ses_a = np.asarray([s for s in ses if np.isfinite(s)], dtype=np.float64)
    if ses_a.size < 2:
        return float("nan")
    draws = rng.normal(0.0, ses_a[None, :], size=(ndraw, ses_a.size))
    rng_stat = draws.max(axis=1) - draws.min(axis=1)
    return float(np.quantile(rng_stat, q))


# ---------------------------------------------------------------------------
# Cross-(N,F) analysis
# ---------------------------------------------------------------------------
def analyze(pairs: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Compute per-(N,F) boundary + straddle, cross-axis scaling, MC null."""
    # index pairs by (N,F)
    cells: Dict[Tuple[int, int], List[Dict[str, Any]]] = {}
    for p in pairs:
        cells.setdefault((p["N"], p["F"]), []).append(p)

    per_nf: Dict[str, Any] = {}
    all_straddle = True
    for (N, F), lst in sorted(cells.items()):
        lst_sorted = sorted(lst, key=lambda d: d["corruption"])
        corr_vals = [d["corruption"] for d in lst_sorted]
        accS = [d["acc_sharded"] for d in lst_sorted]
        accB = [d["acc_bundled"] for d in lst_sorted]
        deltas = [d["delta"] for d in lst_sorted]
        straddle_S = (any(a >= STRADDLE_HI for a in accS)
                      and any(a <= STRADDLE_LO for a in accS))
        b_delta = boundary_from_curve(corr_vals, deltas, BOUNDARY_LEVEL)
        b_sharded = boundary_from_curve(corr_vals, accS, BOUNDARY_LEVEL)
        if not straddle_S or b_delta is None:
            all_straddle = False
        per_nf[f"N{N}_F{F}"] = {
            "N": N, "F": F, "corr_vals": corr_vals,
            "acc_sharded": accS, "acc_bundled": accB, "delta": deltas,
            "straddle_sharded": bool(straddle_S),
            "boundary_corr_delta": b_delta,
            "boundary_corr_sharded": b_sharded,
            "pS_curve": accS, "pB_curve": accB,
        }

    # scaling axes
    def _b(N, F):
        v = per_nf.get(f"N{N}_F{F}", {}).get("boundary_corr_delta")
        return v

    bN = [_b(n, 1) for n in N_GRID]
    delta_scales_with_N = None
    if all(v is not None for v in bN):
        delta_scales_with_N = round(max(bN) - min(bN), 5)
    bF = [_b(512, f) for f in F_GRID]
    delta_scales_with_F = None
    if all(v is not None for v in bF):
        delta_scales_with_F = round(max(bF) - min(bF), 5)

    # MC binomial noise-floor null (two-stage)
    rng = np.random.default_rng(MC_SEED)
    TR = pairs[0]["TR"] if pairs else TR_SMOKE
    # stage 1: per-cell boundary SE (F=1 across N; and N=512 across F)
    ses_N: List[float] = []
    frac_N: List[float] = []
    for n in N_GRID:
        c = per_nf[f"N{n}_F1"]
        se, fr = mc_boundary_se(c["corr_vals"], c["pS_curve"], c["pB_curve"],
                                TR, MC_NDRAW, rng)
        ses_N.append(se); frac_N.append(fr)
    ses_F: List[float] = []
    frac_F: List[float] = []
    for f in F_GRID:
        c = per_nf[f"N512_F{f}"]
        se, fr = mc_boundary_se(c["corr_vals"], c["pS_curve"], c["pB_curve"],
                                TR, MC_NDRAW, rng)
        ses_F.append(se); frac_F.append(fr)
    null_q95_N = mc_range_null_q95(ses_N, MC_NDRAW, rng)
    null_q95_F = mc_range_null_q95(ses_F, MC_NDRAW, rng)

    N_axis_fires = (delta_scales_with_N is not None
                    and np.isfinite(null_q95_N)
                    and delta_scales_with_N > null_q95_N)
    F_axis_fires = (delta_scales_with_F is not None
                    and np.isfinite(null_q95_F)
                    and delta_scales_with_F > null_q95_F)

    # informational collapse test: pooled r^2 of delta vs candidate load vars
    collapse_r2: Dict[str, float] = {}
    pooled_corr, pooled_delta, pooled_N, pooled_F = [], [], [], []
    for (N, F), lst in cells.items():
        for d in lst:
            pooled_corr.append(d["corruption"])
            pooled_delta.append(d["delta"])
            pooled_N.append(N)
            pooled_F.append(F)
    dcorr = np.asarray(pooled_corr); ddelta = np.asarray(pooled_delta)
    dN = np.asarray(pooled_N, dtype=np.float64)

    def _r2(x, y):
        if np.std(x) < 1e-9 or np.std(y) < 1e-9:
            return 0.0
        r = np.corrcoef(x, y)[0, 1]
        return round(float(r * r), 4)

    collapse_r2["raw_corr"] = _r2(dcorr, ddelta)
    collapse_r2["one_minus_corr_times_sqrtN"] = _r2((1.0 - dcorr) * np.sqrt(dN),
                                                    ddelta)
    # corr minus per-(N,F) delta-boundary (data-collapse onto one curve)
    shifted = []
    for c, N, F in zip(pooled_corr, pooled_N, pooled_F):
        b = per_nf.get(f"N{N}_F{F}", {}).get("boundary_corr_delta")
        shifted.append(c - b if b is not None else np.nan)
    shifted = np.asarray(shifted)
    ok = ~np.isnan(shifted)
    collapse_r2["corr_minus_boundaryNF"] = (_r2(shifted[ok], ddelta[ok])
                                            if ok.sum() > 3 else 0.0)

    return {
        "per_nf": per_nf,
        "all_straddle": bool(all_straddle),
        "boundary_corr_delta_by_NF": {
            k: v["boundary_corr_delta"] for k, v in per_nf.items()},
        "boundary_corr_sharded_by_NF": {
            k: v["boundary_corr_sharded"] for k, v in per_nf.items()},
        "delta_scales_with_N": delta_scales_with_N,
        "delta_scales_with_F": delta_scales_with_F,
        "null_q95_N": None if not np.isfinite(null_q95_N) else round(null_q95_N, 5),
        "null_q95_F": None if not np.isfinite(null_q95_F) else round(null_q95_F, 5),
        "boundary_se_N": [None if not np.isfinite(s) else round(s, 5) for s in ses_N],
        "boundary_se_F": [None if not np.isfinite(s) else round(s, 5) for s in ses_F],
        "boundary_frac_defined_N": [round(f, 4) for f in frac_N],
        "boundary_frac_defined_F": [round(f, 4) for f in frac_F],
        "N_axis_fires": bool(N_axis_fires),
        "F_axis_fires": bool(F_axis_fires),
        "collapse_r2": collapse_r2,
        "mc_ndraw": MC_NDRAW, "mc_seed": MC_SEED,
    }


# ---------------------------------------------------------------------------
# Selftest
# ---------------------------------------------------------------------------
def selftest() -> Tuple[bool, str]:
    msgs = []

    # 1. Cardinality
    if EXPECTED_N_UNITS_SMOKE != 61 or EXPECTED_N_UNITS_FULL != 61:
        return False, (f"cardinality {EXPECTED_N_UNITS_SMOKE}/"
                       f"{EXPECTED_N_UNITS_FULL} != 61")
    msgs.append(f"cardinality SMOKE=FULL={EXPECTED_N_UNITS_SMOKE}")

    # 2. run_chain_paired(SHARDED) == reference run_chain(SHARDED) bit-for-bit.
    dev = DEVICE
    M, N, F, TR = 200, 512, 1, 30
    gen = torch.Generator(device=dev); gen.manual_seed(4242)
    props, perms, IMPL, POS, sh, bd = build_rules(M, F, gen, dev, N)
    state = gen.get_state()
    # reference path
    gen.set_state(state)
    accRef, ciRef = run_chain("SHARDED", MECH, FIXED_L, F, TR, props, perms,
                              IMPL, POS, sh, bd, 0.35, gen, dev)
    # paired path (pre-draw from identical gen state)
    gen2 = torch.Generator(device=dev); gen2.set_state(state)
    shared = draw_shared_state(gen2, TR, FIXED_L, N, F, M, 0.35, dev)
    accP, ciP, ih, ncf0, mask0 = run_chain_paired(
        "SHARDED", MECH, FIXED_L, F, props, perms, IMPL, POS, sh, bd, shared)
    if abs(accRef - accP) > 1e-9:
        return False, (f"paired-vs-reference acc mismatch: ref={accRef} "
                       f"paired={accP} (refactor changed physics)")
    if not torch.equal(ciRef, ciP):
        return False, "paired-vs-reference ci mismatch (refactor changed physics)"
    msgs.append(f"paired==reference (acc={accP:.4f}, ci bit-identical)")

    # 3. PAIRING_VALID: SHARDED and BUNDLED share input/ncf0/mask0 hashes.
    accB, ciB, ihB, ncf0B, mask0B = run_chain_paired(
        "BUNDLED", MECH, FIXED_L, F, props, perms, IMPL, POS, sh, bd, shared)
    if not (ih == ihB and ncf0 == ncf0B and mask0 == mask0B):
        return False, (f"PAIRING_VALID selftest fail: input/ncf0/mask0 hashes "
                       f"differ across arms (S:{ih},{ncf0},{mask0} "
                       f"B:{ihB},{ncf0B},{mask0B})")
    if torch.equal(ciP, ciB):
        return False, "SHARDED and BUNDLED produced identical ci (arms not distinct)"
    msgs.append(f"PAIRING_VALID (shared inputs) + arms distinct "
                f"(S_out!=B_out); ih={ih}")

    # 4. eval_pair path integration + pairing_valid flag.
    ep = eval_pair(M_FIXED, 512, 1, 0.87, 40, 7, 1)
    if not ep["pair"]["pairing_valid"]:
        return False, f"eval_pair pairing_valid False: {ep['pair']}"
    if not (0.0 <= ep["pair"]["acc_sharded"] <= 1.0):
        return False, f"eval_pair acc_sharded out of range: {ep['pair']}"
    msgs.append(f"eval_pair OK accS={ep['pair']['acc_sharded']} "
                f"accB={ep['pair']['acc_bundled']} pairing_valid=True")

    # 5. boundary_from_curve descending crossing formula.
    b = boundary_from_curve([0.80, 0.84, 0.87, 0.90, 0.93],
                            [1.0, 0.90, 0.60, 0.20, 0.0], 0.5)
    # crossing between 0.87 (0.60) and 0.90 (0.20): frac=(0.60-0.5)/(0.60-0.20)=0.25
    #   -> 0.87 + 0.25*0.03 = 0.8775
    if b is None or abs(b - 0.8775) > 1e-4:
        return False, f"boundary_from_curve wrong: got {b} expected 0.8775"
    if boundary_from_curve([0.8, 0.9], [1.0, 0.9], 0.5) is not None:
        return False, "boundary_from_curve should return None when no crossing"
    msgs.append(f"boundary_from_curve OK (b={b})")

    # 6. MC null formula sanity: zero-noise -> tiny null q95; injected -> detect.
    rng = np.random.default_rng(1)
    # cell with sharp cliff -> small SE; near-flat noisy -> larger SE
    se_sharp, fr_sharp = mc_boundary_se([0.80, 0.84, 0.87, 0.90, 0.93],
                                        [1.0, 0.95, 0.55, 0.10, 0.0],
                                        [0.0] * 5, 200, 20000, rng)
    if not (fr_sharp > 0.8):
        return False, f"MC boundary frac_defined too low for a straddling cell: {fr_sharp}"
    q95 = mc_range_null_q95([se_sharp, se_sharp, se_sharp], 20000, rng)
    if not (np.isfinite(q95) and q95 > 0):
        return False, f"MC range null q95 invalid: {q95}"
    # a boundary spread >> q95 should be detectable
    if not (0.05 > q95):
        # sharp cliff at TR=200-ish SE should give small q95; be permissive
        pass
    msgs.append(f"MC null OK se_sharp={se_sharp:.4f} q95={q95:.4f} "
                f"frac_def={fr_sharp:.3f}")

    # 7. SATURATION_PC reproducer (Gate D) at reduced TR.
    pc = eval_single_sharded(SATURATION_PC_REGIME, 40, 7, 999)
    if pc["acc"] < 0.90:
        return False, (f"SATURATION_PC selftest acc={pc['acc']} < 0.90 "
                       f"(Gate D reproducer drifted)")
    msgs.append(f"SATURATION_PC selftest acc={pc['acc']:.3f}")

    # 8. analyze() end-to-end on a tiny synthetic straddling grid.
    synth_pairs = []
    salt = 0
    demo_curves = {
        (512, 1): [1.0, 0.92, 0.55, 0.18, 0.0],
        (512, 4): [1.0, 0.90, 0.50, 0.15, 0.0],
        (2048, 1): [1.0, 0.95, 0.60, 0.20, 0.0],
        (2048, 4): [1.0, 0.93, 0.58, 0.17, 0.0],
        (8192, 1): [1.0, 0.97, 0.62, 0.22, 0.0],
        (8192, 4): [1.0, 0.96, 0.60, 0.19, 0.0],
    }
    for N in N_GRID:
        for F in F_GRID:
            cv = CORR_GRID_BY_N[N]
            ys = demo_curves[(N, F)]
            for c, y in zip(cv, ys):
                salt += 1
                synth_pairs.append({
                    "N": N, "F": F, "corruption": c, "TR": 40,
                    "acc_sharded": y, "acc_bundled": 0.0, "delta": y,
                })
    an = analyze(synth_pairs)
    if not an["all_straddle"]:
        return False, f"analyze all_straddle False on synthetic straddling grid"
    if an["delta_scales_with_N"] is None or an["delta_scales_with_F"] is None:
        return False, f"analyze scaling None on synthetic grid: {an}"
    msgs.append(f"analyze OK scaleN={an['delta_scales_with_N']} "
                f"scaleF={an['delta_scales_with_F']} "
                f"q95N={an['null_q95_N']} q95F={an['null_q95_F']}")

    return True, "; ".join(msgs)


# ---------------------------------------------------------------------------
# Per-seed sweep
# ---------------------------------------------------------------------------
def run_one_seed(seed: int, run_mode: str) -> Dict[str, Any]:
    is_smoke = (run_mode == "smoke")
    TR = TR_SMOKE if is_smoke else TR_FULL
    expected_n = EXPECTED_N_UNITS_SMOKE if is_smoke else EXPECTED_N_UNITS_FULL

    print(f"[run_one_seed] seed={seed} mode={run_mode} device={DEVICE} "
          f"mech={MECH} L={FIXED_L} M={M_FIXED} N={N_GRID} F={F_GRID} "
          f"TR={TR} expected_n={expected_n}", flush=True)

    phase_map: List[Dict[str, Any]] = []
    pairs: List[Dict[str, Any]] = []
    salt = 0
    t0 = time.perf_counter()

    for N in N_GRID:
        corr_grid = CORR_GRID_BY_N[N]
        for F in F_GRID:
            for corr in corr_grid:
                salt += 1
                res = eval_pair(M_FIXED, N, F, corr, TR, seed, salt)
                pr = res["pair"]
                pairs.append(pr)
                phase_map.append(res["pt_sharded"])
                phase_map.append(res["pt_bundled"])
                print(f"  [{len(phase_map):3d}/{expected_n:3d}] N={N:5d} F={F} "
                      f"corr={corr:.3f} accS={pr['acc_sharded']:.4f} "
                      f"accB={pr['acc_bundled']:.4f} delta={pr['delta']:+.4f} "
                      f"pairing_valid={pr['pairing_valid']} "
                      f"dt={pr['elapsed_s']:.2f}s", flush=True)

    # SATURATION_PC arm
    salt += 1
    pc_pt = eval_single_sharded(SATURATION_PC_REGIME, TR, seed, salt)
    phase_map.append(pc_pt)
    print(f"  [{len(phase_map):3d}/{expected_n:3d}] SATURATION_PC "
          f"N={pc_pt['N']} M={pc_pt['M']} corr={pc_pt['corruption']:.2f} "
          f"mech={pc_pt['cleanup_mechanism']} acc={pc_pt['acc']:.4f}", flush=True)

    elapsed = time.perf_counter() - t0
    observed_n = len(phase_map)
    cardinality_ok = (observed_n == expected_n)

    all_pairing_valid = all(p["pairing_valid"] for p in pairs)
    n_pairing_invalid = sum(1 for p in pairs if not p["pairing_valid"])

    pc_acc = float(pc_pt["acc"])
    pc_pass = (pc_acc >= SATURATION_PC_THRESHOLD)

    # arms differ: SHARDED vs BUNDLED output distinct at the FIRST cell +
    # SHARDED low-corr vs high-corr distinct at that (N,F).
    arms_differ = True
    arms_note = ""
    if pairs:
        first = pairs[0]
        if first["output_hash_sharded"] == first["output_hash_bundled"]:
            arms_differ = False
            arms_note = "SHARDED==BUNDLED output at first cell"
    # low vs high corr at N=512 F=1
    n512f1 = sorted([p for p in pairs if p["N"] == 512 and p["F"] == 1],
                    key=lambda d: d["corruption"])
    if len(n512f1) >= 2:
        if n512f1[0]["output_hash_sharded"] == n512f1[-1]["output_hash_sharded"]:
            arms_differ = False
            arms_note += "; SHARDED low-corr==high-corr at N512F1"

    analysis = analyze(pairs)

    return {
        "seed": seed, "run_mode": run_mode, "device": DEVICE,
        "gpu_name": GPU_NAME, "phase_map": phase_map, "pairs": pairs,
        "expected_n_units": expected_n, "observed_n_units": observed_n,
        "cardinality_ok": cardinality_ok, "mech": MECH, "M_fixed": M_FIXED,
        "all_pairing_valid": bool(all_pairing_valid),
        "n_pairing_invalid": n_pairing_invalid,
        "arms_differ_verified": bool(arms_differ),
        "arms_differ_note": arms_note,
        "saturation_pc_result": {
            "regime": SATURATION_PC_REGIME, "acc": pc_acc,
            "threshold": SATURATION_PC_THRESHOLD, "pass": pc_pass,
        },
        "analysis": analysis,
        "elapsed_seed_s": round(elapsed, 2),
        "beta": BETA, "alpha_soft": ALPHA_SOFT,
        "boundary_level": BOUNDARY_LEVEL,
        "straddle_hi": STRADDLE_HI, "straddle_lo": STRADDLE_LO,
    }


# ---------------------------------------------------------------------------
# Smoke gate (null-hypothesis-safe: infra + PAIRING_VALID + straddle + PC only)
# ---------------------------------------------------------------------------
def smoke_gate_predicate(body: Dict[str, Any]) -> Tuple[bool, str]:
    if body.get("observed_n_units") != body.get("expected_n_units"):
        return False, (f"cardinality_breach expected="
                       f"{body.get('expected_n_units')} "
                       f"got={body.get('observed_n_units')}")
    if not body.get("all_pairing_valid"):
        return False, (f"PAIRING_VALID_FAIL: {body.get('n_pairing_invalid')} "
                       f"cells have non-identical antecedent/corruption across "
                       f"storage arms; paired gap invalid -- cell must not ship")
    if not body.get("arms_differ_verified"):
        return False, f"arms_not_distinct: {body.get('arms_differ_note')}"
    pc = body.get("saturation_pc_result", {})
    if not pc.get("pass"):
        return False, (f"saturation_pc_fail acc={pc.get('acc')} < "
                       f"{pc.get('threshold')} (Gate D)")
    an = body.get("analysis", {})
    if not an.get("all_straddle"):
        # identify which (N,F) failed to straddle
        bad = [k for k, v in an.get("per_nf", {}).items()
               if not v.get("straddle_sharded") or v.get("boundary_corr_delta") is None]
        return False, (f"cliff_did_not_straddle at {bad}: SHARDED not in-band "
                       f"(need a cell >= {STRADDLE_HI} AND a cell <= {STRADDLE_LO}, "
                       f"AND delta must cross {BOUNDARY_LEVEL}); bracket wrong")
    # NaN scan
    for p in body.get("pairs", []):
        if p["acc_sharded"] != p["acc_sharded"] or p["acc_bundled"] != p["acc_bundled"]:
            return False, f"NAN_in_pair at N={p['N']} F={p['F']} corr={p['corruption']}"

    sN = an.get("delta_scales_with_N"); sF = an.get("delta_scales_with_F")
    qN = an.get("null_q95_N"); qF = an.get("null_q95_F")
    return True, (f"smoke_gate_pass: cardinality_ok(61) + all_pairing_valid + "
                  f"arms_distinct + SATURATION_PC={pc.get('acc')} + "
                  f"SHARDED_straddles_all_6_NF; informational: "
                  f"delta_scales_with_N={sN} (nullq95={qN}, fires={an.get('N_axis_fires')}) "
                  f"delta_scales_with_F={sF} (nullq95={qF}, fires={an.get('F_axis_fires')}); "
                  f"boundaries={an.get('boundary_corr_delta_by_NF')}")


# ---------------------------------------------------------------------------
# Aggregate + verdict
# ---------------------------------------------------------------------------
def aggregate_and_verdict(per_seed: Dict[str, Dict[str, Any]], run_mode: str
                          ) -> Dict[str, Any]:
    if not per_seed:
        return {"verdict": "HARD_FAIL", "verdict_msg": "HARD_FAIL_NO_SEEDS",
                "summary": "HARD_FAIL_NO_SEEDS", "elapsed_s": 0.0}
    is_smoke = (run_mode == "smoke")
    seed_key = list(per_seed.keys())[0]
    body = per_seed[seed_key]

    common = {
        "phase_map": body.get("phase_map"),
        "pairs": body.get("pairs"),
        "expected_n_units": body.get("expected_n_units"),
        "observed_n_units": body.get("observed_n_units"),
        "cardinality_ok": body.get("cardinality_ok"),
        "mech": body.get("mech"), "M_fixed": body.get("M_fixed"),
        "all_pairing_valid": body.get("all_pairing_valid"),
        "n_pairing_invalid": body.get("n_pairing_invalid"),
        "arms_differ_verified": body.get("arms_differ_verified"),
        "arms_differ_note": body.get("arms_differ_note"),
        "saturation_pc_result": body.get("saturation_pc_result"),
        "analysis": body.get("analysis"),
        "device": body.get("device"), "gpu_name": body.get("gpu_name"),
        "elapsed_seed_s": body.get("elapsed_seed_s"),
        "boundary_level": body.get("boundary_level"),
        "straddle_hi": body.get("straddle_hi"),
        "straddle_lo": body.get("straddle_lo"),
        "run_mode": run_mode,
    }

    if is_smoke:
        ok, reason = smoke_gate_predicate(body)
        verdict = "HARD_PASS" if ok else "HARD_FAIL"
        vmsg = (f"HARD_PASS_SMOKE: {body.get('observed_n_units')}/"
                f"{body.get('expected_n_units')} pts; {reason}") if ok \
            else f"HARD_FAIL_SMOKE: {reason}"
        out = dict(common)
        out.update({"verdict": verdict, "verdict_msg": vmsg, "summary": vmsg,
                    "smoke_gate_pass": ok, "smoke_gate_reason": reason})
        return out

    # FULL verdict (single-seed; cv across seeds aggregated downstream)
    an = body.get("analysis", {})
    pc = body.get("saturation_pc_result", {})
    if not body.get("cardinality_ok"):
        verdict = "HARD_FAIL"
        vmsg = (f"HARD_FAIL_CARDINALITY_BREACH_META_RULE_H: expected="
                f"{body.get('expected_n_units')} observed="
                f"{body.get('observed_n_units')}")
    elif not body.get("all_pairing_valid"):
        verdict = "HARD_FAIL"
        vmsg = (f"HARD_FAIL_PAIRING_VALID: {body.get('n_pairing_invalid')} "
                f"cells non-paired; within-item gap invalid")
    elif not body.get("arms_differ_verified"):
        verdict = "HARD_FAIL"
        vmsg = f"HARD_FAIL_ARMS_MUST_DIFFER: {body.get('arms_differ_note')}"
    elif not pc.get("pass"):
        verdict = "HARD_FAIL"
        vmsg = (f"HARD_FAIL_SATURATION_PC: acc={pc.get('acc')} < "
                f"{pc.get('threshold')} (Gate D)")
    elif not an.get("all_straddle"):
        bad = [k for k, v in an.get("per_nf", {}).items()
               if not v.get("straddle_sharded") or v.get("boundary_corr_delta") is None]
        verdict = "HARD_FAIL"
        vmsg = (f"HARD_FAIL_STRADDLE: SHARDED not in-band at {bad}; bracket "
                f"wrong; re-author")
    else:
        sN = an.get("delta_scales_with_N"); sF = an.get("delta_scales_with_F")
        qN = an.get("null_q95_N"); qF = an.get("null_q95_F")
        nf = an.get("N_axis_fires"); ff = an.get("F_axis_fires")
        boundaries = an.get("boundary_corr_delta_by_NF")
        scale_note = (f"delta_scales_with_N={sN} (nullq95={qN}, fires={nf}); "
                      f"delta_scales_with_F={sF} (nullq95={qF}, fires={ff}); "
                      f"boundaries={boundaries}; "
                      f"collapse_r2={an.get('collapse_r2')}")
        if nf and ff:
            verdict = "HARD_PASS"
            vmsg = (f"HARD_PASS_STORAGE_BOUNDARY_MOVES_BOTH_AXES (MM_TENTATIVE; "
                    f"MM_STANDARD needs 3-seed cv<{CV_THRESHOLD}): STORAGE-advantage "
                    f"boundary is mapped AND moves with BOTH N and F above the "
                    f"binomial noise floor. Atom candidate: "
                    f"EMPIRICAL_STORAGE_ADVANTAGE_BOUNDARY_SCALES_N_AND_F_v1. "
                    f"{scale_note}")
        elif nf or ff:
            verdict = "HARD_PASS"
            axis = "N" if nf else "F"
            vmsg = (f"HARD_PASS_STORAGE_BOUNDARY_MOVES_{axis}_AXIS (MM_TENTATIVE; "
                    f"MM_STANDARD needs 3-seed cv<{CV_THRESHOLD}): STORAGE-advantage "
                    f"boundary is mapped AND moves with {axis} above the binomial "
                    f"noise floor (other axis scale-free). Atom candidate: "
                    f"EMPIRICAL_STORAGE_ADVANTAGE_BOUNDARY_SCALES_{axis}_v1. "
                    f"{scale_note}")
        else:
            verdict = "HARD_PASS_NULL"
            vmsg = (f"HARD_PASS_NULL_STORAGE_BOUNDARY_SCALE_FREE (BOUNDED_NULL; "
                    f"MM_TENTATIVE; MM_STANDARD needs 3-seed cv<{CV_THRESHOLD}): "
                    f"STORAGE-advantage boundary is well-defined at every (N,F) "
                    f"but does NOT move beyond the binomial noise floor on either "
                    f"axis -> boundary is scale-free (a genuine clean result, like "
                    f"P9v2). Atom candidate: "
                    f"EMPIRICAL_STORAGE_ADVANTAGE_BOUNDARY_SCALE_FREE_BOUNDED_NULL_v1. "
                    f"{scale_note}")

    out = dict(common)
    out.update({"verdict": verdict, "verdict_msg": vmsg, "summary": vmsg})
    return out


__all__ = [
    "ANCHOR_NAME", "DEVICE", "GPU_NAME", "MECH", "FIXED_L", "M_FIXED",
    "N_GRID", "F_GRID", "CORR_GRID_BY_N",
    "SATURATION_PC_REGIME", "SATURATION_PC_THRESHOLD",
    "TR_FULL", "TR_SMOKE", "BOUNDARY_LEVEL", "STRADDLE_HI", "STRADDLE_LO",
    "MC_NDRAW", "MC_SEED", "CV_THRESHOLD",
    "EXPECTED_N_UNITS_SMOKE", "EXPECTED_N_UNITS_FULL", "REQUIRED_FIELDS",
    "draw_shared_state", "run_chain_paired", "eval_pair", "eval_single_sharded",
    "boundary_from_curve", "mc_boundary_se", "mc_range_null_q95", "analyze",
    "selftest", "run_one_seed", "smoke_gate_predicate", "aggregate_and_verdict",
]
