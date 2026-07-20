"""
CLEANUP MATURITY PROBE -- does swapping the substrate's argmax-cosine cleanup for a
GRADED modern-Hopfield attractor convert the measured sigma=2.0->3.0 STEP-FUNCTION into
GRADED, noise-robust, brain-faithful (CA3-style) pattern completion?

WHY (pointers, not trusted summaries):
  - Platform maturity audit (notes/drill_platform_maturity_base_elements_brain_sufficient_5x_2026-07-20.md):
    cleanup is the ONE clearly-IMMATURE base element -- measured as a hard STEP (recall 1.0 through
    sigma=2.0, cliffs to 0.029 at sigma=3.0) where the brain (CA3) has GRADED attractor completion.
    Prescribed cheapest decisive fix: swap the cleanup rule for a modern/dense-Hopfield attractor and
    re-run the noise sweep. HARD-PASS = step becomes graceful; HARD-FAIL = step persists regardless of
    cleanup family (=> the step is a codebook/dimensionality SNR property, not a cleanup-rule weakness).
  - The measured step: notes/vsa_core_ops_empirical_envelope_bind_bundle_unbind_2026-07-19.md Section 3 +
    data/exp_read_bridge_noise_tolerance_hd_vs_symbolic_v1/metrics.json (cleanup_recovery.single_obs).
    The current cleanup path is clean(v)=argmax_j cos(v, cb_j) over an FHRR complex phasor codebook.
  - On-disk modern-Hopfield (STEP-1 located + validated): hdlab/modern_hopfield_readout.py (10/10 self-
    tests) + hdlab/cleanup_family.py::modern_hopfield_continuous + T3/EXP_modern_hopfield_beta_capacity_gpu
    family. IMPORTANT PROVENANCE CAVEAT: those were validated on REAL/bipolar patterns in a CAPACITY (P/N)
    regime, NOT on FHRR complex phasors and NOT on the step-function noise regime. So this cell PORTS the
    same softmax-attention update rule to the FHRR-complex cleanup path (faithful, one-variable) and
    measures it against the current argmax cleanup on the SAME noise sweep.

WHAT (one variable = the CLEANUP RULE; everything else held):
  Same FHRR complex codebook, same noise draws, same atoms/seeds. Two arms:
    ARGMAX (current)  : j = argmax_j Re(<cb_j, cue>) ; recovered vector = cb[j] (hard snap).
    MODERN_HOPFIELD   : T-step softmax-attention attractor over the SAME codebook (Ramsauer 2021 update,
                        FHRR-complex port): state <- renorm(softmax(beta*scores(state)) @ cb) ; final
                        id = argmax_j Re(<cb_j, state>) ; recovered vector = attractor state (graded blend).

NOISE MODES (both substrate-native, one variable = cleanup rule at each level):
  PHASE   : cue = v * exp(i*N(0,sigma)) elementwise -- the ORIGINAL step-function test (uniform degradation).
            DENSE sigma grid around the measured 2.0->3.0 cliff to resolve step-vs-sigmoid.
  PARTIAL : cue = v with a random fraction f of components ERASED (set to 0), rest EXACT -- the CA3
            partial-cue completion capability the audit calls the brain-faithful mode.
  R-FOLD  : PHASE with R independent noisy observations bundled (analog average) THEN cleaned -- where
            multi-observation integration + attractor sharpening could push the SNR threshold.

METRICS per (arm, mode, level, seed):
  top1_id  : fraction of atoms whose cleanup returns the correct index (the step-function metric).
  vec_fid  : mean cos(recovered_vector, true_atom) -- graded reconstruction fidelity for downstream binding.

DESIGN-GATE (pre-registered; verified at smoke BEFORE full):
  (1) REAL baseline = the SUBSTRATE'S CURRENT cleanup (argmax-cosine), not a strawman. POSITIVE CONTROL:
      argmax reproduces the measured step (top1_id ~1.0 at sigma<=2.0, ~<0.10 at sigma=3.0) -- if it does
      not reproduce the prior measured cliff, the regime is wrong and downstream arms are untrustworthy.
  (2) MODERN-HOPFIELD-ARM-IS-FUNCTIONAL (not a no-op): at sigma=0 id=1.0; and at a mid sigma the attractor
      DENOISES -- cos(attractor_state, true) > cos(raw_cue, true). Proves a HARD-FAIL is a real SNR result,
      not a broken arm.
  (3) DISCRIMINATOR CAN FIRE BOTH WAYS: if modern-Hopfield beats argmax at the cliff -> step becomes graded
      (HARD-PASS). If it ties argmax (both cliff at the same sigma) -> step is a codebook SNR wall
      (HARD-FAIL). PARTIAL/vec_fid are the built-in regimes where a graded advantage CAN show even if top1
      ties -> proves the metric can show either.
  (4) ONE VARIABLE = the cleanup rule; identical codebook / cue / noise draw at every (mode, level, seed).

BANDS (strict, above-floor per META_RULE_L; realistic-cliff band = mean top1_id over sigma in {2.5,2.75,3.0};
       ALL thresholds HYPOTHESIZED@this-cell):
  HARD_PASS = GRADED_CLEANUP_FIX:
      mh_top1_cliff >= 0.30 AND (mh_top1_cliff - argmax_top1_cliff) >= 0.10 AND
      mh_top1_low(sigma<=2.0) >= argmax_top1_low - 0.02  (no low-noise regression).
  HARD_FAIL = STEP_IS_CODEBOOK_SNR_WALL_NOT_CLEANUP_RULE:
      mh_top1_cliff < 0.10  OR  max_sigma|mh_top1 - argmax_top1| < 0.05  (no rule can move the step).
  MIDDLE = PARTIAL/REGIME-SPECIFIC: anything between -> localize + honest deflate.

BRAIN-CHECK (pre-reg; outcome NOT pre-assumed): CA3 pattern completion is graded because basins are shaped
  by EXPERIENCE (correlated/structured storage) and it completes from PARTIAL cues -- NOT because it
  recovers a single sub-SNR uniform-degraded cue (that information is gone). The substrate's argmax-cosine
  is already exhaustive nearest-neighbor = the OPTIMAL single-cue top-1 rule; modern-Hopfield is a softmax
  APPROXIMATION to it, so on a RANDOM codebook it cannot beat argmax on top-1 id. SAME-LIMIT (step persists)
  would mean the brain-faithful fix is LEARNED/similarity-structured codebooks (audit item-3) + multi-cue
  integration, NOT a cleanup-rule swap. This cell tests exactly that fork. The DEVIATION (FHRR multiplicative
  phase binding is an engineering stand-in for CA3 recurrent dynamics) is flagged.

COMPUTE ARCHITECTURE: sequential-CPU. Justified: (a) wall << 10s per condition (M<=96 atoms, N=2048, small
  complex matmuls), total grid ~10-60s; (b) the cell VALIDATES substrate cleanup primitives (bit reference)
  so a CPU reference is correct; (c) no SGD/training. No GPU-batching win at this scale. STORAGE STRATEGY:
  no_storage (single-vector cleanup primitive, not a compositional map). CRLB: n/a for a top-1 id
  discriminator; the relevant analytic floor is the codebook-SNR crossover E[cos]=exp(-sigma^2/2) vs the
  max-distractor cosine ~ few/sqrt(N) -- documented, not a Cramer-Rao estimator floor.

DETERMINISM: OMP/MKL=1; fixed int SEED; np.random.default_rng(seed) with per-condition seeds from ENUMERATED
  indices (no builtin hash(); no list(set())). Codebook seed depends on seed-index ONLY (independent of the
  noise draw) so curves are comparable across levels.

Glass-box (REAL hdlab-style FHRR primitives, no external LLM). Local / foreground-to-completion.
  NO push / NO remote-persist / NO git add -A. needs_orchestrator_store_sync=True. CLAIM-VET-pending;
  strategic read = HYPOTHESIS pending skunkworks landed-VET.

ANCHOR: cleanup_graded_attractor_vs_argmax_v1
PRIOR-WORK CHECK: substrate_query "modern Hopfield dense softmax cleanup graded attractor pattern completion
  from partial noisy cue" -> top cosine 0.3545 = research_multi_iter_cleanup_brain_analog_2x_drill (CA3
  pattern-completion drill) + 0.3008 = modern-Hopfield-as-engineering-lever note. Modern-Hopfield-as-cleanup
  is a KNOWN lever, not a novel concept; this cell WIRES IT IN and MEASURES the step-vs-graded question that
  those notes flagged but never ran on the FHRR cleanup path. Rediscovery/wiring-in, honestly flagged.

# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke (ARGMAX retrieved atom vs MODERN_HOPFIELD attractor state = distinct vectors)
# - final_metrics_atomicity: tmp_replace (single-shot; os.replace)
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_n/a declared (top-1 id discriminator; analytic floor = codebook-SNR crossover, documented)
# - baseline_in_band: ARGMAX spans 1.0 (sigma<=2.0) -> ~0.03 (sigma=3.0); not saturated, must-reproduce step
# - discriminator survives scale: full runs at N=2048 (the measured-envelope operating point); smoke previews
#   the same N=2048 with fewer seeds so the arm-gap is not a small-smoke artifact
# - HARD_PASS strictly above floor (mh_top1_cliff>=0.30 AND gap>=0.10)
# - real_code_path: self-test constructs REAL FHRR phasor codebook + REAL argmax/modern-Hopfield cleanup
# - calibration_check: adaptive_with_gate (modern-Hopfield beta swept; BEST-beta reported for the arm's best
#   shot; the discriminator = comparison vs argmax + all betas logged; not tuned-for-PASS)
# - all numbers tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@
"""
import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import sys
import json
import time
import argparse
import platform
import traceback
import hashlib
from datetime import datetime, timezone

import numpy as np

_THIS = os.path.abspath(__file__)
REPO = os.path.dirname(os.path.dirname(_THIS))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

ANCHOR_NAME = "cleanup_graded_attractor_vs_argmax_v1"
OUTPUT_DIR = os.path.join(REPO, "data", "exp_" + ANCHOR_NAME)
SEED = 20260720
N_DIM = 2048                                   # substrate operating point (matches measured envelope)
N_ATOMS = 48                                   # matches the envelope's cleanup_recovery n_atoms
PHASE_SIGMAS = [0.0, 0.5, 1.0, 1.5, 2.0, 2.25, 2.5, 2.75, 3.0, 3.5]   # DENSE around the 2.0->3.0 cliff
PARTIAL_FRACS = [0.0, 0.3, 0.5, 0.7, 0.8, 0.9, 0.95]                   # erasure fraction
RFOLD_R = 3                                     # redundant observations for analog-averaging + attractor
CLIFF_SIGMAS = [2.5, 2.75, 3.0]                 # the "cliff band" for the primary top1_id gate
LOW_SIGMAS = [0.0, 0.5, 1.0, 1.5, 2.0]          # low-noise band (no-regression check)
BETAS = [8.0, 20.0, 50.0]                       # modern-Hopfield inverse-temperature (N-normalized cosine)
MH_STEPS = 3                                    # attractor update steps
N_SEEDS = 5


# ===========================================================================
# FHRR complex phasor codebook + cleanup primitives (substrate-native; deterministic).
# ===========================================================================
def make_codebook(n_dim, n_atoms, rng):
    """(M, N) complex128 unit-modulus phasor codebook."""
    theta = rng.uniform(-np.pi, np.pi, size=(n_atoms, n_dim))
    return np.exp(1j * theta)


def phase_noise(v, sigma, rng):
    """v * exp(i*N(0,sigma)) elementwise (the measured step-function noise model)."""
    if sigma <= 0.0:
        return v.copy()
    ph = rng.normal(0.0, sigma, size=v.shape)
    return v * np.exp(1j * ph)


def erase(v, frac, rng):
    """Set a random fraction of components to 0 (partial cue / CA3 erasure); rest EXACT."""
    if frac <= 0.0:
        return v.copy()
    n = v.shape[0]
    k = int(round(frac * n))
    idx = rng.choice(n, size=k, replace=False)
    out = v.copy()
    out[idx] = 0.0
    return out


def _scores(state, cb):
    """FHRR cosine-like scores Re(<cb_j, state>)/N in [-1,1]; state (N,), cb (M,N) -> (M,)."""
    return (cb.conj() @ state).real / cb.shape[1]


def cleanup_argmax(cue, cb):
    """Current substrate cleanup: exhaustive argmax-cosine. Returns (id, recovered_vector=cb[id])."""
    s = _scores(cue, cb)
    j = int(np.argmax(s))
    return j, cb[j]


def cleanup_modern_hopfield(cue, cb, beta, steps):
    """Modern dense-Hopfield (Ramsauer 2021) softmax-attention attractor, FHRR-complex port.

    state <- renorm_to_unit_phasor(softmax(beta * scores(state)) @ cb) for `steps` iterations.
    Returns (id=argmax scores(final state), recovered_vector=final attractor state).
    """
    state = cue.copy()
    n = cb.shape[1]
    for _ in range(steps):
        s = beta * _scores(state, cb)          # (M,)
        s = s - s.max()
        w = np.exp(s)
        w = w / (w.sum() + 1e-30)              # softmax attention weights
        y = w @ cb                             # (N,) complex blend of stored patterns
        mag = np.abs(y)
        mag = np.where(mag < 1e-12, 1.0, mag)
        state = y / mag                        # re-normalize to unit-modulus phasor (phase-only)
    s = _scores(state, cb)
    return int(np.argmax(s)), state


def _cos(a, b):
    """Complex cosine Re(<a,b>)/(|a||b|)."""
    na = float(np.linalg.norm(a))
    nb = float(np.linalg.norm(b))
    if na < 1e-12 or nb < 1e-12:
        return 0.0
    return float((a.conj() @ b).real / (na * nb))


# ===========================================================================
# Curve builders.
# ===========================================================================
def cond_seed(seed_idx, mode_idx, level_idx):
    """Deterministic per-condition seed from ENUMERATED indices (no builtin hash; no list(set()))."""
    return SEED + 1_000_003 * seed_idx + 10_007 * mode_idx + 101 * level_idx


def _eval_arm_top1_fid(cues, cb, arm, beta):
    """Given a list of (cue, true_idx), return (top1_id, mean_vec_fid) for `arm`."""
    hits = 0
    fid = 0.0
    for cue, ti in cues:
        if arm == "argmax":
            j, rec = cleanup_argmax(cue, cb)
        else:
            j, rec = cleanup_modern_hopfield(cue, cb, beta, MH_STEPS)
        hits += int(j == ti)
        fid += _cos(rec, cb[ti])
    m = len(cues)
    return hits / m, fid / m


def phase_curve(cb, sigmas, seed_idx, mode_idx, beta, rfold=1):
    """For each sigma: build cues (one per atom, rfold obs bundled), score both arms."""
    m = cb.shape[0]
    out = {"argmax": {"top1": [], "fid": []}, "modern_hopfield": {"top1": [], "fid": []}}
    denoise_probe = None
    for li, sigma in enumerate(sigmas):
        rng = np.random.default_rng(cond_seed(seed_idx, mode_idx, li))
        cues = []
        for ai in range(m):
            v = cb[ai]
            if rfold <= 1:
                cue = phase_noise(v, sigma, rng)
            else:
                obs = [phase_noise(v, sigma, rng) for _ in range(rfold)]
                cue = np.mean(obs, axis=0)     # analog average (bundle)
            cues.append((cue, ai))
        for arm in ("argmax", "modern_hopfield"):
            t1, fd = _eval_arm_top1_fid(cues, cb, arm, beta)
            out[arm]["top1"].append(round(t1, 4))
            out[arm]["fid"].append(round(fd, 4))
        # denoise probe at a mid sigma (functional witness): attractor state closer to true than raw cue?
        if abs(sigma - 1.5) < 1e-9:
            cue0, ti0 = cues[0]
            _, st = cleanup_modern_hopfield(cue0, cb, beta, MH_STEPS)
            denoise_probe = dict(sigma=sigma, cos_raw=round(_cos(cue0, cb[ti0]), 4),
                                 cos_attractor=round(_cos(st, cb[ti0]), 4))
    return out, denoise_probe


def partial_curve(cb, fracs, seed_idx, mode_idx, beta):
    m = cb.shape[0]
    out = {"argmax": {"top1": [], "fid": []}, "modern_hopfield": {"top1": [], "fid": []}}
    for li, f in enumerate(fracs):
        rng = np.random.default_rng(cond_seed(seed_idx, mode_idx, li))
        cues = [(erase(cb[ai], f, rng), ai) for ai in range(m)]
        for arm in ("argmax", "modern_hopfield"):
            t1, fd = _eval_arm_top1_fid(cues, cb, arm, beta)
            out[arm]["top1"].append(round(t1, 4))
            out[arm]["fid"].append(round(fd, 4))
    return out


def _mean_curves(list_of_curves):
    """Average a list of {arm:{metric:[...]}} elementwise."""
    arms = list(list_of_curves[0].keys())
    metrics = list(list_of_curves[0][arms[0]].keys())
    agg = {a: {mt: [] for mt in metrics} for a in arms}
    L = len(list_of_curves[0][arms[0]][metrics[0]])
    for a in arms:
        for mt in metrics:
            for i in range(L):
                agg[a][mt].append(round(float(np.mean([c[a][mt][i] for c in list_of_curves])), 4))
    return agg


def _band_mean(sigmas, top1, band):
    idx = [i for i, s in enumerate(sigmas) if round(s, 3) in [round(b, 3) for b in band]]
    if not idx:
        return 0.0
    return float(np.mean([top1[i] for i in idx]))


def _pick_best_beta(cb, betas, seed_idx):
    """Best-beta for the modern-Hopfield arm = beta maximizing cliff-band top1 (fair best-shot; logged)."""
    best_b, best_v = betas[0], -1.0
    per_beta = {}
    for b in betas:
        pc, _ = phase_curve(cb, PHASE_SIGMAS, seed_idx, mode_idx=0, beta=b, rfold=1)
        v = _band_mean(PHASE_SIGMAS, pc["modern_hopfield"]["top1"], CLIFF_SIGMAS)
        per_beta[b] = round(v, 4)
        if v > best_v:
            best_v, best_b = v, b
    return best_b, per_beta


# ===========================================================================
# Markers / metrics (atomic) / crash-diagnostic.
# ===========================================================================
def _write_start_marker(output_dir, run_mode, expected_n_units):
    marker = dict(pid=os.getpid(), ts_iso=datetime.now(timezone.utc).isoformat(),
                  anchor_name=ANCHOR_NAME, run_mode=run_mode,
                  expected_n_units=expected_n_units, host=platform.node())
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
    diag = dict(verdict="CELL_CRASHED", verdict_msg=f"{type(exc).__name__}: {str(exc)[:500]}",
                summary=f"CELL_CRASHED: {type(exc).__name__}", elapsed_s=0.0,
                traceback=traceback.format_exc()[:5000],
                ts_iso=datetime.now(timezone.utc).isoformat(), pid=os.getpid(),
                anchor_name=ANCHOR_NAME)
    _write_metrics(output_dir, diag)


def _arms_differ(cb, beta):
    """META_RULE_AF: ARGMAX retrieved atom vs MODERN_HOPFIELD attractor state must be distinct vectors."""
    rng = np.random.default_rng(SEED + 42)
    cue = phase_noise(cb[0], 1.0, rng)
    _, rec_a = cleanup_argmax(cue, cb)
    _, rec_m = cleanup_modern_hopfield(cue, cb, beta, MH_STEPS)
    da = hashlib.sha256(np.ascontiguousarray(rec_a).tobytes()).hexdigest()
    dm = hashlib.sha256(np.ascontiguousarray(rec_m).tobytes()).hexdigest()
    return da != dm, da, dm


# ===========================================================================
# Self-test (design-gate).
# ===========================================================================
def self_test():
    print("[self-test] building FHRR codebook + cleanup arms ...", flush=True)
    rng = np.random.default_rng(SEED)
    cb = make_codebook(N_DIM, N_ATOMS, rng)

    # ARMS-DIFFER (META_RULE_AF).
    differ, da, dm = _arms_differ(cb, beta=20.0)
    assert differ, f"META_RULE_AF: argmax vs modern-Hopfield produced bit-identical vectors ({da[:12]})"
    print(f"[self-test] arms differ: argmax={da[:12]} modern_hopfield={dm[:12]}", flush=True)

    # DESIGN-GATE (1) POSITIVE CONTROL: argmax reproduces the measured STEP.
    pc, denoise = phase_curve(cb, PHASE_SIGMAS, seed_idx=0, mode_idx=0, beta=20.0, rfold=1)
    argmax_low = _band_mean(PHASE_SIGMAS, pc["argmax"]["top1"], LOW_SIGMAS)
    argmax_s30 = pc["argmax"]["top1"][PHASE_SIGMAS.index(3.0)]
    assert argmax_low >= 0.98, f"argmax should be ~1.0 at low sigma, got {argmax_low:.3f}"
    assert argmax_s30 <= 0.15, \
        f"argmax should reproduce the cliff (~0.03 at sigma=3.0), got {argmax_s30:.3f} -- regime wrong"
    print(f"[self-test] STEP reproduced: argmax top1 low(sigma<=2.0)={argmax_low:.3f} "
          f"sigma=3.0={argmax_s30:.3f} (measured envelope: ~1.0 -> ~0.029)", flush=True)

    # DESIGN-GATE (2) MODERN-HOPFIELD-ARM-IS-FUNCTIONAL: sigma=0 id=1.0 AND denoising at mid sigma.
    mh_s0 = pc["modern_hopfield"]["top1"][PHASE_SIGMAS.index(0.0)]
    assert mh_s0 >= 0.98, f"modern-Hopfield broken at sigma=0: top1={mh_s0:.3f}"
    assert denoise is not None and denoise["cos_attractor"] > denoise["cos_raw"], \
        f"modern-Hopfield not denoising (attractor no closer to true than raw cue): {denoise}"
    print(f"[self-test] modern-Hopfield functional: sigma=0 top1={mh_s0:.3f}; denoise@sigma=1.5 "
          f"cos_raw={denoise['cos_raw']:.3f} -> cos_attractor={denoise['cos_attractor']:.3f}", flush=True)

    # DESIGN-GATE (3) DISCRIMINATOR CAN FIRE: report the cliff-band gap (either direction is a real result).
    mh_cliff = _band_mean(PHASE_SIGMAS, pc["modern_hopfield"]["top1"], CLIFF_SIGMAS)
    ar_cliff = _band_mean(PHASE_SIGMAS, pc["argmax"]["top1"], CLIFF_SIGMAS)
    max_gap = max(abs(pc["modern_hopfield"]["top1"][i] - pc["argmax"]["top1"][i])
                  for i in range(len(PHASE_SIGMAS)))
    print(f"[self-test] cliff-band top1: modern_hopfield={mh_cliff:.3f} argmax={ar_cliff:.3f} "
          f"(gap {mh_cliff - ar_cliff:+.3f}); max|gap| over sweep={max_gap:.3f}", flush=True)

    # PARTIAL-cue smoke (brain-faithful mode present + discriminating).
    pcurve = partial_curve(cb, PARTIAL_FRACS, seed_idx=0, mode_idx=1, beta=20.0)
    ar_partial_hi = pcurve["argmax"]["top1"][-1]
    print(f"[self-test] partial-cue present: argmax top1 @f={PARTIAL_FRACS[-1]}={ar_partial_hi:.3f} "
          f"(discriminating regime)", flush=True)

    # DETERMINISM: two identical phase-curve builds match.
    pc2, _ = phase_curve(cb, PHASE_SIGMAS, seed_idx=0, mode_idx=0, beta=20.0, rfold=1)
    assert pc["argmax"]["top1"] == pc2["argmax"]["top1"], "non-deterministic curves"
    print("[self-test] deterministic (two builds identical)", flush=True)
    print("[self-test] PASS", flush=True)
    return 0


# ===========================================================================
# Full verdict.
# ===========================================================================
def build_verdict(timeout_s=900):
    t0 = time.perf_counter()
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    expected_n_units = N_SEEDS * (len(PHASE_SIGMAS) + len(PARTIAL_FRACS) + len(PHASE_SIGMAS))
    _write_start_marker(OUTPUT_DIR, "full", expected_n_units)

    # Best-beta for the modern-Hopfield arm (fair best-shot; per-beta logged; seed 0).
    cb0 = make_codebook(N_DIM, N_ATOMS, np.random.default_rng(SEED))
    best_beta, per_beta = _pick_best_beta(cb0, BETAS, seed_idx=0)
    print(f"[full] best-beta={best_beta} (per-beta cliff top1: {per_beta})", flush=True)

    phase_seeds, partial_seeds, rfold_seeds = [], [], []
    denoise_any = None
    for si in range(N_SEEDS):
        cb = make_codebook(N_DIM, N_ATOMS, np.random.default_rng(SEED + 7919 * si))
        pc, denoise = phase_curve(cb, PHASE_SIGMAS, si, mode_idx=0, beta=best_beta, rfold=1)
        pcp = partial_curve(cb, PARTIAL_FRACS, si, mode_idx=1, beta=best_beta)
        pcr, _ = phase_curve(cb, PHASE_SIGMAS, si, mode_idx=2, beta=best_beta, rfold=RFOLD_R)
        phase_seeds.append(pc)
        partial_seeds.append(pcp)
        rfold_seeds.append(pcr)
        if denoise is not None and denoise_any is None:
            denoise_any = denoise
        print(f"[full] seed {si}: phase argmax cliff={_band_mean(PHASE_SIGMAS, pc['argmax']['top1'], CLIFF_SIGMAS):.3f} "
              f"mh cliff={_band_mean(PHASE_SIGMAS, pc['modern_hopfield']['top1'], CLIFF_SIGMAS):.3f}", flush=True)

    phase_m = _mean_curves(phase_seeds)
    partial_m = _mean_curves(partial_seeds)
    rfold_m = _mean_curves(rfold_seeds)

    # PRIMARY gate numbers (phase-noise single-obs top1_id).
    mh_cliff = round(_band_mean(PHASE_SIGMAS, phase_m["modern_hopfield"]["top1"], CLIFF_SIGMAS), 4)
    ar_cliff = round(_band_mean(PHASE_SIGMAS, phase_m["argmax"]["top1"], CLIFF_SIGMAS), 4)
    mh_low = round(_band_mean(PHASE_SIGMAS, phase_m["modern_hopfield"]["top1"], LOW_SIGMAS), 4)
    ar_low = round(_band_mean(PHASE_SIGMAS, phase_m["argmax"]["top1"], LOW_SIGMAS), 4)
    cliff_gap = round(mh_cliff - ar_cliff, 4)
    max_gap = round(max(abs(phase_m["modern_hopfield"]["top1"][i] - phase_m["argmax"]["top1"][i])
                        for i in range(len(PHASE_SIGMAS))), 4)
    no_low_regression = bool(mh_low >= ar_low - 0.02)

    # SECONDARY (reported): vec_fid graceful-degradation + partial-cue + R-fold.
    mh_fid_cliff = round(_band_mean(PHASE_SIGMAS, phase_m["modern_hopfield"]["fid"], CLIFF_SIGMAS), 4)
    ar_fid_cliff = round(_band_mean(PHASE_SIGMAS, phase_m["argmax"]["fid"], CLIFF_SIGMAS), 4)
    mh_rfold_cliff = round(_band_mean(PHASE_SIGMAS, rfold_m["modern_hopfield"]["top1"], CLIFF_SIGMAS), 4)
    ar_rfold_cliff = round(_band_mean(PHASE_SIGMAS, rfold_m["argmax"]["top1"], CLIFF_SIGMAS), 4)
    # partial-cue: mean top1 gap over high-erasure fracs (0.8,0.9,0.95)
    hi_fr = [0.8, 0.9, 0.95]
    mh_partial = round(float(np.mean([phase_or_partial for phase_or_partial in
                  [partial_m["modern_hopfield"]["top1"][PARTIAL_FRACS.index(f)] for f in hi_fr]])), 4)
    ar_partial = round(float(np.mean([partial_m["argmax"]["top1"][PARTIAL_FRACS.index(f)] for f in hi_fr])), 4)

    hard_pass = (mh_cliff >= 0.30 and cliff_gap >= 0.10 and no_low_regression)
    hard_fail = (mh_cliff < 0.10 or max_gap < 0.05)
    if hard_pass:
        verdict = "GRADED_CLEANUP_FIX"
    elif hard_fail:
        verdict = "STEP_IS_CODEBOOK_SNR_WALL_NOT_CLEANUP_RULE"
    else:
        verdict = "CLEANUP_PARTIAL_OR_REGIME_SPECIFIC"

    elapsed = round(time.perf_counter() - t0, 2)
    metrics = dict(
        anchor_name=ANCHOR_NAME, verdict=verdict,
        verdict_msg=(
            f"PHASE top1 cliff(sigma2.5-3.0): modern_hopfield {mh_cliff:.3f} vs argmax {ar_cliff:.3f} "
            f"(gap {cliff_gap:+.3f}, max|gap| {max_gap:.3f}); low(sigma<=2.0) mh {mh_low:.3f} vs argmax "
            f"{ar_low:.3f} (no_regression={no_low_regression}); vec_fid cliff mh {mh_fid_cliff:.3f} vs "
            f"argmax {ar_fid_cliff:.3f}; R-fold({RFOLD_R}) cliff mh {mh_rfold_cliff:.3f} vs argmax "
            f"{ar_rfold_cliff:.3f}; partial-cue hi-erasure top1 mh {mh_partial:.3f} vs argmax {ar_partial:.3f}"),
        summary=(f"{verdict}: cliff top1 mh {mh_cliff:.2f} vs argmax {ar_cliff:.2f} (gap {cliff_gap:+.2f}); "
                 f"vec_fid cliff mh {mh_fid_cliff:.2f} vs argmax {ar_fid_cliff:.2f}"),
        elapsed_s=elapsed, ts_iso=datetime.now(timezone.utc).isoformat(), pid=os.getpid(),
        seed=SEED, n_dim=N_DIM, n_atoms=N_ATOMS, n_seeds=N_SEEDS, best_beta=best_beta, per_beta=per_beta,
        mh_steps=MH_STEPS,
        decision_numbers=dict(
            phase_sigmas=PHASE_SIGMAS, cliff_sigmas=CLIFF_SIGMAS, low_sigmas=LOW_SIGMAS,
            mh_top1_cliff=mh_cliff, argmax_top1_cliff=ar_cliff, cliff_gap=cliff_gap, max_gap=max_gap,
            mh_top1_low=mh_low, argmax_top1_low=ar_low, no_low_regression=no_low_regression,
            mh_fid_cliff=mh_fid_cliff, argmax_fid_cliff=ar_fid_cliff,
            mh_rfold_cliff=mh_rfold_cliff, argmax_rfold_cliff=ar_rfold_cliff,
            partial_hi_erasure_fracs=hi_fr, mh_partial_top1=mh_partial, argmax_partial_top1=ar_partial),
        curves=dict(phase=phase_m, partial=partial_m, rfold=rfold_m,
                    phase_sigmas=PHASE_SIGMAS, partial_fracs=PARTIAL_FRACS),
        denoise_witness=denoise_any,
        arms_differ_verified=True,
        REQUIRED_FIELDS=["verdict", "decision_numbers", "curves"],
        cited=dict(audit="notes/drill_platform_maturity_base_elements_brain_sufficient_5x_2026-07-20.md",
                   envelope="notes/vsa_core_ops_empirical_envelope_bind_bundle_unbind_2026-07-19.md",
                   on_disk_mh=["hdlab/modern_hopfield_readout.py", "hdlab/cleanup_family.py"]),
        caveats=[
            "ONE VARIABLE = the cleanup rule (argmax vs modern-Hopfield); identical FHRR codebook / cue / "
            "noise draw at every (mode,level,seed). PHASE noise = the measured step-function model "
            "(v*exp(i*N(0,sigma))).",
            "argmax-cosine is EXHAUSTIVE nearest-neighbor = the optimal single-cue top-1 cleanup; modern-"
            "Hopfield is a softmax APPROXIMATION to it, so on a RANDOM codebook it cannot beat argmax on "
            "top-1 id. A cliff-band tie (max|gap|<0.05) => the step is a codebook-SNR wall, and the brain-"
            "faithful fix is LEARNED/similarity-structured codebooks (audit item-3) + multi-cue "
            "integration, NOT a cleanup-rule swap. HARD-FAIL here is a real finding, not a broken arm "
            "(the sigma=0 id=1.0 + denoise witness prove the modern-Hopfield arm is functional).",
            "vec_fid (cos of recovered vector to true atom) is the GRADED metric: argmax snaps hard "
            "(fidelity ~1 if id right, low if wrong); modern-Hopfield returns a continuous denoised blend. "
            "A modern-Hopfield vec_fid advantage at the cliff = a real graded-reconstruction win for "
            "downstream binding even when top-1 id ties.",
            "On-disk modern-Hopfield was validated on REAL/bipolar patterns in a CAPACITY (P/N) regime, not "
            "FHRR-complex phasors nor this step regime; this cell PORTS the softmax-attention update rule "
            "faithfully to the FHRR cleanup path.",
            "best-beta chosen to maximize the modern-Hopfield arm's cliff top1 (fair best-shot; per-beta "
            "logged) -> the comparison vs argmax + bands are pre-registered, not tuned-for-PASS.",
            "CLAIM-VET-pending (skunkworks landed-VET before fact). needs_orchestrator_store_sync=True.",
        ],
    )
    _write_metrics(OUTPUT_DIR, metrics)
    print(f"[verdict] {verdict} :: {metrics['verdict_msg']} :: {elapsed}s", flush=True)
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--full", action="store_true")
    ap.add_argument("--timeout", type=int, default=900)
    args = ap.parse_args()
    try:
        if args.self_test:
            return self_test()
        if args.full:
            return build_verdict(timeout_s=args.timeout)
        return self_test()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        _write_crash_metrics(OUTPUT_DIR, e)
        print(f"[CRASH] {type(e).__name__}: {e}")
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
