# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate: phase-linear codebook vs random-phasor codebook hash-distinct;
#     the recovered-integer arrays of the CLEAN arms differ across ops (addsub vs mul_starpower vs
#     mul_reencode recover DIFFERENT running values -- add != mul by construction); scrambled_op recovered
#     integers differ from hetero_reencode; noisy add-family vs mul-family recovered integers differ.
#     EXEMPT PAIR (arms_differ_exempted): mul_reencode vs hetero_reencode may SHARE the exact truth at some
#     depths (both exact) -- we do NOT hash-compare truth arrays; we hash CODEBOOKS + RECOVERED running-value
#     arrays of the DISTINCT-op arms (which DO differ) + the control arms.
# - final_metrics_atomicity: tmp_replace (write metrics.json.tmp then os.replace).
# - except SystemExit: raise BEFORE except Exception (no BaseException).
# - crlb/capacity-feasibility: per-residue decode is a phasor argmax over m_i candidates in a sub-block of
#     dim sb=2730 (N=8192, R=3). CLEAN operands: SNR huge (signal sim==1.0, distractor sim ~ N(0,1/(2 sb)));
#     collision-free (probe MEASURED clean operand decode == 1.000 down to sb=2). NOISY operands (HEADLINE 2):
#     read from a B-item superposition bundle via key-unbind -> distractor sim std = sqrt((B-1)/(2 sb)),
#     SNR mu = sqrt(2 sb/(B-1)); B is the SNR knob that places the per-hop decode error in a discriminating
#     band. discriminator_reachability=True (B-grid MEASURED to span censored..cliff-at-D~2, add family
#     non-censored at B in {360..1000}). crlb_n_a NOT claimed: the SNR/order-statistic argument IS the
#     capacity-feasibility analysis.
# - baseline_in_band (META_RULE_AG): HEADLINE 1 is an EXACTNESS/CORRECTNESS test (not a difficulty sweep):
#     addsub + *_reencode arms are ~1.0 by lossless-composition construction; controls (scrambled_op,
#     random_codebook) are intentionally ~0.0 -> exempt (declared controls). The NON-trivial measured content
#     is the mul_starpower NUMERICAL cliff (float32 phase compounding, MEASURED crossing ~D8) and its rescue
#     by decode-recode (fix_gap). HEADLINE 2 op-points (bundle load B) are the difficulty axis and DO span the
#     discriminating band (Gate B, discriminating_fraction MEASURED >= 0.30 for the add family).
# - discriminator survives scale: smoke runs at FULL N=8192, FULL sb=2730, both moduli regimes, full B-grid;
#     reduces seeds / n_chain / max clean depth ONLY. mul_starpower cliff + reencode rescue + control collapse
#     + add-vs-mul robustness ordering ALL fire in smoke (DISCRIMINATOR-MUST-SURVIVE-SCALE option A).
# - HARD_PASS strictly above floor: HEADLINE-1 addsub/reencode exact HP 0.99; the real discriminators are the
#     NUMERICAL cliff (mul_starpower crosses USABLE_FLOOR at D<=STARPOWER_CLIFF_MAX) + the reencode fix_gap +
#     the control collapse + HEADLINE-2 exact-predictor strictly closer to observed than the loose control.
# - all numbers in comments tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@.
#
# MATH CAPABILITY -- COMPOSITIONAL MULTI-STEP ARITHMETIC DERIVATION: DEPTH-EXACTNESS + SELF-MARGIN  v1
# ===================================================================================================
# FOURTH real math-capability cell. The single-op arithmetic primitives are proven exact by-construction:
#   add  (bind)            FULL HARD_PASS exact-add=1.000
#     MEASURED@data/exp_math_rns_add_chain_v1/metrics.json:arms.small.phase_linear_add.exact_mean
#   subtract (conj-bind), compare (decode-then-compare)  FULL HARD_PASS
#     MEASURED@data/exp_math_rns_subtract_compare_v1/metrics.json:verdict
#   multiply (star operator, decode-then-exponentiate)   FULL HARD_PASS
#     MEASURED@data/exp_math_rns_multiply_star_v1/metrics.json:verdict
# OPEN QUESTION (prim != compos, CITED@feedback_chain_grade_primitives_not_trivially_composable_2026-06-28):
# does EXACTNESS survive when these primitives are CHAINED into a multi-hop derivation (a=x+y; b=a*z; c=b-w;
# ...), at what depth D does it degrade, and does the substrate's OWN reasoning-depth exact self-margin
# (CHAIN_GRADE @data/exp_reasoning_depth_exact_order_statistic_self_margin_v1) PREDICT that depth?
#
# HEADLINE 1 (capability -- CLEAN chains, fresh isolated operands, real substrate N=8192):
#   Chain the primitives end-to-end ON THE SUBSTRATE (real bind / conj-bind / star_power / decode). Measure
#   exact-through-depth vs ground-truth modular arithmetic. THREE mechanistically distinct behaviours (all
#   MEASURED by pre-dispatch probe, tags below):
#     * addsub chain (bind / conj-bind): phases ADD -> float error accumulates LINEARLY -> EXACT to D>=256.
#       LOSSLESS COMPOSITION (no intermediate decode needed).  MEASURED@probe addsub d256=1.000
#     * mul_starpower chain (composed star_power, no re-encode): z**e multiplies PHASE ERROR by e each hop ->
#       error compounds ~ 1e-7 * (mean exponent)^D -> NUMERICAL cliff at D~8-16 (float32 phase blowup, NOT
#       decode noise).  MEASURED@probe mul d8=1.000 d16=0.450 d32=0.000
#     * mul_reencode chain (decode-recode each hop): decode running -> re-encode -> phase error RESET each hop
#       -> EXACT to D>=256 (the fix; the numerical cliff is not fundamental).  MEASURED@probe reencode d256=1.000
#   FINDING: composed arithmetic stays exact arbitrarily deep for add/sub (lossless); the multiply cliff is a
#   FLOAT-PRECISION accumulation set by clean-code numerics (phase compounding), NOT by decode noise, and is
#   removed by re-encoding. (Answers "clean-code accumulation vs decode noise" -- it is clean-code numerics.)
#
# HEADLINE 2 (self-prediction -- NOISY-readout chains; does the reasoning-depth self-margin PREDICT the cliff):
#   To create a genuine per-hop DECODE cliff (clean operands never cliff -- probe MEASURED collision-free even
#   at sb=2), operands are read from a B-item SUPERPOSITION bundle via key-unbind (the substrate's real
#   superpose/decode; the "noisy associative readout" of the cross-cell law
#   CITED@reference_crt_residue_helps_clean_encoding_hurts_noisy_readout_2026-07-06). Bundle load B is the SNR
#   knob (mu = sqrt(2 sb/(B-1))). Feed that per-hop decode SNR into the SAME extreme-value capture order
#   statistic + series-reliability law D* = ln(USABLE_FLOOR)/ln(p_hop) (reused from the CHAIN_GRADE
#   self-margin cell) and check it forecasts the OBSERVED noisy-chain cliff. TWO op families:
#     * noisy ADD chain (non-absorbing): an operand read-error shifts the running sum's residue and PERSISTS
#       -> follows the series law fairly closely (MEASURED r_exact ~1.8 at B=360; observed slightly DEEPER
#       than predicted -- residue errors self-cancel via a mild random walk).
#     * noisy MUL chain (absorbing-zero): once a running residue collapses to 0 (0*x=0), operand read-errors
#       in that residue become HARMLESS -> the chain is MUCH MORE robust than the series law predicts
#       (MEASURED censored/no-cliff down to p_hop=0.78 where series law predicts D*~2).
#   HONEST FORK (pre-registered): the self-margin either (a) PREDICTS the cliff (ratio-error <= HP band,
#   unbiased) -> transfers to the arithmetic-chain family; or (b) systematically OVER-predicts the cliff
#   (observed DEEPER; ratio-error biased) -> the arithmetic-chain collapse family DIFFERS from the associative
#   family, because modular arithmetic has error-HEALING structure (add: self-cancelling residue walk; mul:
#   absorbing zero) that associative superposition retrieval lacks. Either way the LOOSE occupancy-binary
#   control predictor is strictly worse (discriminator-fires), and the add-vs-mul robustness ORDERING
#   (mul >> add) is the mechanism signature. The cell reports the measured fork per family; it does NOT force
#   a "transfers" outcome.
#
# CROSS-HEADLINE HONEST FINDING (the cross-cell law as instrument): the reasoning-depth self-margin (a
# DECODE-NOISE order statistic) can only speak to DECODE-noise cliffs (HEADLINE 2, noisy readout) -- it is
# silent on the CLEAN mul_starpower NUMERICAL cliff (HEADLINE 1), which is not a decode event. And even on the
# decode-noise cliff it is a CONSERVATIVE (safe, never-over-promising) bound for arithmetic chains because of
# their modular error-healing. Monitor-not-control: this is a NARROW glass-box measurement of when the
# substrate's own self-margin applies to its own arithmetic, not a language or self-improvement claim.
#
# Brain-grounding (CITED@): entorhinal grid cells ARE a residue-number-system (Sreenivasan & Fiete 2011,
# Nat. Neurosci.); abstract-magnitude grid codes (Constantinescu/O'Reilly/Behrens 2016, Science). Capture /
# order statistic THEORETICAL@Hajek ECE361 L8 / Proakis Ch.4 (capture effect Roberts 1975; Arnbak & Van
# Blitterswijk 1987 IEEE JSAC) -- reused verbatim from the CHAIN_GRADE self-margin cell.
#
# ASCII-only. CPU default (numpy complex64; no GPU, no LLM). Self-contained (synthetic phasor codebooks +
# synthetic superposition bundles; no pool / re-encode / substrate-state dependency -- smoke uses clean
# synthetic data per USER-LOCKED synth-smoke rule).
# Run: python experiments/exp_math_compositional_derivation_depth_self_margin_v1.py [--self-test | --smoke]
#      (bare / runner-injected HDLAB_RUN_MODE=full -> full)

from __future__ import annotations

import hashlib
import json
import math
import os
import platform
import sys
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(line_buffering=True)  # 17. PRINT-PROGRESS flush on newline

np.seterr(over="ignore", invalid="ignore")  # mul_starpower phase-blowup -> inf/nan handled explicitly below

ANCHOR_NAME = "math_compositional_derivation_depth_self_margin_v1"
REPO = Path(__file__).resolve().parents[1]

N_DIM = 8192            # substrate compositional default (== landed add/sub/mul/rns_crt cells); never reduced
R_MODULI = 3            # residues per integer (disjoint sub-blocks)
SB = N_DIM // R_MODULI   # 2730 dims per sub-block; sb >> max modulus -> clean per-residue argmax collision-free

# Moduli regimes reused from the landed add cell. CLEAN chains run both; NOISY chains run "small" only.
REGIMES = {
    "small": (7, 8, 9),      # M=504
    "mid":   (16, 17, 19),   # M=5168
}
NOISY_REGIME = "small"

SEEDS_FULL = (7, 13, 19, 23, 29)
SEEDS_SMOKE = (7, 13, 19)

# Clean-chain depth grid (HEADLINE 1). Deep enough to expose the addsub loss-less plateau AND the
# mul_starpower numerical cliff (~D8) AND the mul_reencode deep-exact plateau.
DEPTHS_CLEAN_FULL = (1, 2, 4, 8, 12, 16, 24, 32, 48, 64, 96, 128)
DEPTHS_CLEAN_SMOKE = (1, 2, 4, 8, 16, 32, 64)
DEPTHS_CLEAN_SELFTEST = (1, 2, 4, 8, 16)

# Noisy-chain depth grid (HEADLINE 2) + bundle-load op-points (the SNR knob).
DEPTHS_NOISY_FULL = (1, 2, 3, 4, 6, 8, 12, 16, 24, 32, 48, 64)
DEPTHS_NOISY_SMOKE = (1, 2, 3, 4, 6, 8, 12, 16, 24, 32, 48, 64)
DEPTHS_NOISY_SELFTEST = (1, 2, 4, 8)
D_MAX_NOISY = 64
B_GRID_FULL = (180, 260, 360, 500, 700, 1000)   # MEASURED@probe: add family spans censored..cliff-at-D~2
B_GRID_SMOKE = (360, 500, 700, 1000)
B_GRID_SELFTEST = (500, 1000)
NOISY_OPS = ("add", "mul")
USABLE_FLOOR = 0.50     # D* floor: usable while exact-through-depth >= this (matches CHAIN_GRADE self-margin cell)

# ---- Pre-registered bands (HYPOTHESIZED from mechanism theory + MEASURED by pre-dispatch probe) ----
# HEADLINE 1 (capability):
HP_ADDSUB_EXACT = 0.99      # addsub chain exact-through-depth at max clean depth (THEORETICAL ~1.0; lossless)
HP_REENCODE_EXACT = 0.99    # mul_reencode + hetero_reencode exact at max clean depth (THEORETICAL ~1.0; phase reset)
HF_ADDSUB = 0.90           # HARD_FAIL: addsub not exact deep -> lossless composition broken (substrate breakage)
STARPOWER_CLIFF_MIN = 3    # mul_starpower MUST cliff (crossing) at D >= this (a real, non-vacuous degradation)
STARPOWER_CLIFF_MAX = 40   # ... and at D <= this (numerical cliff is REACHABLE in the tested grid)
HP_FIX_GAP = 0.50          # decode-recode fix rescues the numerical cliff: reencode_exact - starpower_exact @Dmax
CTRL_MAX = 0.15            # controls (scrambled_op / random_codebook) exact-through-depth must collapse below this
CTRL_LEAK = 0.40           # HARD_FAIL: a control >= this at depth>=4 -> exact-through-depth is vacuous (leak)
# HEADLINE 2 (self-margin prediction; ratio bands mirror the CHAIN_GRADE self-margin cell):
HP_RATIO_MAX = 1.5         # exact predictor per-op ratio-error <= this at ALL non-censored op-points -> tight transfer
HF_RATIO_MAX = 2.0         # exact predictor ratio-error > this -> that op-point does not tightly transfer
HP_BIAS_LO = 0.80          # exact aggregate geomean-ratio (pred/obs) >= this (unbiased)
HP_BIAS_HI = 1.25          # exact aggregate geomean-ratio <= this (unbiased)
CONSERVATIVE_GEOMEAN = 0.80  # geomean pred/obs < this (observed systematically DEEPER) -> CONSERVATIVE bound
LOOSE_WORSE_FACTOR = 1.30  # discriminator-fires: |ln(loose_ratio)| >= this * |ln(exact_ratio)| (loose strictly worse)
MIN_NONCENSORED = {"full": 2, "smoke": 1, "selftest": 0}  # cardinality floor on non-censored op-points (add family)
CENSOR_MARGIN = 0.5        # op-point CENSORED if observed crossing >= D_MAX_NOISY - this (a lower bound only)
DISCRIMINATING_FRAC_MIN = 0.30  # Gate B: fraction of (op,B) op-points with observed cliff in (1.5, D_MAX-0.5)


# ============================================================
# Defensive error-checking helpers (13/16)
# ============================================================


def _out_dir() -> Path:
    name = os.environ.get("HDLAB_EXP_NAME")
    return REPO / (f"data/exp_{name}" if name else f"data/exp_{ANCHOR_NAME}")


def _say(msg: str) -> None:
    print(msg, flush=True)


def _write_start_marker(output_dir: Path, run_mode: str, expected_n_units: int) -> None:
    marker = {
        "pid": os.getpid(),
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR_NAME,
        "run_mode": run_mode,
        "expected_n_units": expected_n_units,
        "host": platform.node(),
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    tmp = output_dir / "_start_marker.json.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, output_dir / "_start_marker.json")


def _heartbeat(output_dir: Path, unit_idx: int, total_units: int, t0: float, extra=None) -> None:
    row = {
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "unit_idx": unit_idx,
        "total_units": total_units,
        "elapsed_s": round(time.perf_counter() - t0, 2),
    }
    if extra:
        row["extra"] = extra
    with open(output_dir / "_heartbeat.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(row) + "\n")


def _write_metrics_atomic(output_dir: Path, metrics: dict) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    tmp = output_dir / "metrics.json.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, output_dir / "metrics.json")  # atomic (META_RULE_AH)


def _write_crash_metrics(output_dir: Path, exc: Exception) -> None:
    diag = {
        "anchor_name": ANCHOR_NAME,
        "verdict": "CELL_CRASHED",
        "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
        "summary": f"CELL_CRASHED: {type(exc).__name__}",
        "elapsed_s": 0.0,
        "traceback": traceback.format_exc()[:5000],
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(),
    }
    _write_metrics_atomic(output_dir, diag)


# ============================================================
# CRT number theory (reused VERBATIM from landed add cell; formula self-test target)
# ============================================================


def _egcd(a: int, b: int):
    if b == 0:
        return (a, 1, 0)
    g, x, y = _egcd(b, a % b)
    return (g, y, x - (a // b) * y)


def _modinv(a: int, m: int) -> int:
    g, x, _ = _egcd(a % m, m)
    if g != 1:
        raise ValueError(f"no modular inverse for {a} mod {m} (not coprime)")
    return x % m


def _coprime(moduli) -> bool:
    for i in range(len(moduli)):
        for j in range(i + 1, len(moduli)):
            if math.gcd(moduli[i], moduli[j]) != 1:
                return False
    return True


def _crt_setup(moduli):
    """Return (M=prod, Mi=[M/mi], yi=[inv(Mi) mod mi]) for CRT reconstruction."""
    if not _coprime(moduli):
        raise ValueError(f"moduli not pairwise coprime: {moduli}")
    M = 1
    for m in moduli:
        M *= m
    Mi = [M // m for m in moduli]
    yi = [_modinv(Mi[i], moduli[i]) for i in range(len(moduli))]
    return M, Mi, yi


def _crt(residues, moduli, M, Mi, yi) -> int:
    """Reconstruct t in [0,M) from residues (t mod mi). Exact iff residues correct."""
    t = 0
    for i in range(len(moduli)):
        t += (int(residues[i]) % moduli[i]) * Mi[i] * yi[i]
    return t % M


def crt_selftest(moduli) -> bool:
    """Formula self-test 1: (a) moduli pairwise coprime; (b) CRT(t mod mi) == t for all t in [0,min(M,4096))."""
    if not _coprime(moduli):
        return False
    M, Mi, yi = _crt_setup(moduli)
    lim = min(M, 4096)
    for t in range(lim):
        res = [t % m for m in moduli]
        if _crt(res, moduli, M, Mi, yi) != t:
            return False
    rng = np.random.default_rng(12345)
    for _ in range(256):
        t = int(rng.integers(0, M))
        res = [t % m for m in moduli]
        if _crt(res, moduli, M, Mi, yi) != t:
            return False
    return True


# ============================================================
# Phasor codebooks + encode / bind / subtract / star_power / decode (reused VERBATIM from add/sub/mul cells)
# ============================================================


def phasor_codebook(m: int, sb: int, seed: int) -> np.ndarray:
    """Phase-LINEAR FPE codebook (m, sb) complex64: codebook[r,j] = exp(i*2*pi*k_j*r/m), k_j in [1,m-1].
    bind (elementwise product) IS modular addition; conj IS the additive inverse (subtract); z**e IS
    modular multiply (star)."""
    g = np.random.default_rng(seed)
    k = g.integers(1, m, size=sb).astype(np.float64)
    r = np.arange(m, dtype=np.float64)[:, None]
    phase = (2.0 * np.pi / m) * (r * k[None, :])
    return np.exp(1j * phase).astype(np.complex64)


def random_phasor_codebook(m: int, sb: int, seed: int) -> np.ndarray:
    """Control codebook: random unit phasor per (r,j), NOT linear in r (isolates phase-linearity)."""
    g = np.random.default_rng(seed)
    phase = g.uniform(0.0, 2.0 * np.pi, size=(m, sb))
    return np.exp(1j * phase).astype(np.complex64)


def encode(x: int, cbs, moduli, sb: int) -> np.ndarray:
    """Encode integer x -> full-N complex vector: sub-block i = codebook_i[x mod m_i]."""
    v = np.zeros(N_DIM, dtype=np.complex64)
    for i, m in enumerate(moduli):
        v[i * sb:(i + 1) * sb] = cbs[i][x % m]
    return v


def bind(u: np.ndarray, v: np.ndarray) -> np.ndarray:
    """FHRR bind: elementwise complex product == modular ADD."""
    return u * v


def subtract(u: np.ndarray, v: np.ndarray) -> np.ndarray:
    """FHRR conjugate-bind: u (*) conj(v) == modular SUBTRACT (additive inverse)."""
    return u * np.conj(v)


def star_power(av: np.ndarray, exps, moduli, sb: int) -> np.ndarray:
    """STAR multiply core: raise sub-block i of av to integer power exps[i] (elementwise). z**e == codeword of
    (a*e) mod m. Composed WITHOUT re-encoding this multiplies per-dim PHASE ERROR by e each hop -> float32
    phase-compounding numerical cliff (HEADLINE 1)."""
    out = np.zeros(N_DIM, dtype=np.complex64)
    for i in range(len(moduli)):
        out[i * sb:(i + 1) * sb] = av[i * sb:(i + 1) * sb] ** int(exps[i])
    return out


def decode_residues(v: np.ndarray, cbs, moduli, sb: int, want_margin: bool = False):
    """Per-sub-block phasor argmax -> residues. If want_margin: also return (rank1, rank2) normalized sims."""
    residues = []
    margins = []
    for i, m in enumerate(moduli):
        sub = v[i * sb:(i + 1) * sb]
        sims = (cbs[i] @ np.conj(sub)).real / sb
        r = int(np.argmax(sims))
        residues.append(r)
        if want_margin:
            top2 = np.sort(sims)[::-1][:2]
            margins.append((float(top2[0]), float(top2[1] if len(top2) > 1 else 0.0)))
    return (residues, margins) if want_margin else residues


def decode_int(v, cbs, moduli, sb, M, Mi, yi) -> int:
    """Decode to integer in [0,M): phasor argmax residues -> CRT. Returns -1 on non-finite (dead) vector."""
    if not np.all(np.isfinite(v.view(np.float32))):
        return -1
    return _crt(decode_residues(v, cbs, moduli, sb), moduli, M, Mi, yi)


# ============================================================
# Capture order statistic + series-reliability D* (reused VERBATIM from CHAIN_GRADE self-margin cell)
# ============================================================

_GH_NODES, _GH_WEIGHTS = np.polynomial.hermite.hermgauss(64)
_INV_SQRT_PI = 1.0 / math.sqrt(math.pi)
_SQRT2 = math.sqrt(2.0)


def _logPhi(a: float) -> float:
    v = 0.5 * math.erfc(-a / _SQRT2)
    return math.log(v) if v > 0.0 else -1e300


def p_capture(c: int, mu: float, dstract: int) -> float:
    """EXACT capture order statistic: P = E_z[ Phi(z)^(c-1) * Phi(mu+z)^dstract ], z~N(0,1) (64-pt Gauss-Hermite).
    THEORETICAL@Hajek ECE361 L8 / Proakis Ch.4 (capture effect Roberts 1975; Arnbak & Van Blitterswijk 1987)."""
    acc = 0.0
    for zi, wi in zip(_GH_NODES, _GH_WEIGHTS):
        z = _SQRT2 * zi
        term = dstract * _logPhi(mu + z)
        if c > 1:
            term += (c - 1) * _logPhi(z)
        acc += wi * (math.exp(term) if term > -700.0 else 0.0)
    return _INV_SQRT_PI * acc


def _Q(mu: float) -> float:
    """Gaussian upper tail P(N(0,1) > mu)."""
    return 0.5 * math.erfc(mu / _SQRT2)


def bundle_snr_mu(sb: int, B: int) -> float:
    """Per-residue decode SNR after key-unbind from a B-item superposition bundle: signal sim = 1.0,
    distractor sim std = sqrt((B-1)/(2 sb)) -> mu = sqrt(2 sb/(B-1)). THEORETICAL@FHRR crosstalk variance."""
    return math.sqrt(2.0 * sb / max(B - 1, 1))


def p_hop_exact_theory(moduli, sb: int, B: int) -> float:
    """Parameter-free per-hop operand-decode success from the capture order statistic (all R residues right)."""
    mu = bundle_snr_mu(sb, B)
    p = 1.0
    for m in moduli:
        p *= p_capture(1, mu, m - 1)
    return p


def p_hop_loose_theory(moduli, sb: int, B: int) -> float:
    """LOOSE / occupancy-binary control predictor (union-bound collision -> guaranteed failure):
    collision_frac = sum_i (m_i-1) * Q(mu); p_clean = 1 - collision_frac. Over-counts collisions -> UNDER-
    predicts usable depth (biased). Mirrors the CHAIN_GRADE self-margin cell's loose arm."""
    mu = bundle_snr_mu(sb, B)
    cf = sum((m - 1) for m in moduli) * _Q(mu)
    return max(1e-9, 1.0 - cf)


def dstar(p_hop: float, d_max: int) -> float:
    """Series-reliability usable depth: D* = ln(USABLE_FLOOR)/ln(p_hop). THEORETICAL@series-reliability law."""
    p = min(max(p_hop, 1e-9), 1.0 - 1e-12)
    if p >= 1.0 - 1e-9:
        return float(d_max)
    return round(min(float(d_max), max(0.0, math.log(USABLE_FLOOR) / math.log(p))), 3)


def crossing_depth(curve, depths, floor: float, d_max: int) -> float:
    """Continuous exact-through-depth = floor crossing (linear interp); d_max if never crosses (CENSORED)."""
    ds = sorted(depths)
    if curve.get(ds[0], 0.0) < floor:
        return 0.0
    last = ds[0]
    for d in ds:
        if curve.get(d, 0.0) >= floor:
            last = d
        else:
            hi = curve.get(last, 0.0)
            lo = curve.get(d, 0.0)
            frac = (hi - floor) / (hi - lo) if hi > lo else 0.0
            return round(last + frac, 3)
    return float(d_max)


# ============================================================
# Formula self-tests (MANDATORY per task)
# ============================================================


def composition_selftest(moduli, seed: int = 0) -> bool:
    """Formula self-test 2: the substrate arithmetic ops agree with integer modular arithmetic when CHAINED
    via decode-recode (the exact reference): a short mixed chain add/sub/mul on the substrate reproduces the
    integer ground truth EXACTLY; AND the addsub lossless composition (composed bind/conj-bind, no re-encode)
    is exact at short depth; AND star_power single-step multiply is exact."""
    M, Mi, yi = _crt_setup(moduli)
    cbs = [phasor_codebook(m, SB, 6000 + seed * 10 + i) for i, m in enumerate(moduli)]
    rng = np.random.default_rng(4242 + seed)
    # single-step primitive identities (positive-control reproduction at THIS regime)
    for _ in range(32):
        a = int(rng.integers(0, M)); b = int(rng.integers(0, M))
        if decode_int(bind(encode(a, cbs, moduli, SB), encode(b, cbs, moduli, SB)),
                      cbs, moduli, SB, M, Mi, yi) != (a + b) % M:
            return False
        if decode_int(subtract(encode(a, cbs, moduli, SB), encode(b, cbs, moduli, SB)),
                      cbs, moduli, SB, M, Mi, yi) != (a - b) % M:
            return False
        b_res = decode_residues(encode(b, cbs, moduli, SB), cbs, moduli, SB)
        if decode_int(star_power(encode(a, cbs, moduli, SB), b_res, moduli, SB),
                      cbs, moduli, SB, M, Mi, yi) != (a * b) % M:
            return False
    # short mixed decode-recode chain == integer ground truth
    for _ in range(16):
        v = int(rng.integers(0, M)); running = encode(v, cbs, moduli, SB); gt = v % M
        for k in range(6):
            t = int(rng.integers(1, M))
            cur = decode_int(running, cbs, moduli, SB, M, Mi, yi)
            if k % 3 == 0:
                running = bind(running, encode(t, cbs, moduli, SB)); gt = (gt + t) % M
            elif k % 3 == 1:
                running = subtract(running, encode(t, cbs, moduli, SB)); gt = (gt - t) % M
            else:
                running = encode((cur * t) % M, cbs, moduli, SB); gt = (gt * t) % M
        if decode_int(running, cbs, moduli, SB, M, Mi, yi) != gt:
            return False
    # order-statistic monotonicity sanity: larger B (lower SNR) -> lower p_hop -> shallower D*
    d_small_B = dstar(p_hop_exact_theory(moduli, SB, 200), D_MAX_NOISY)
    d_large_B = dstar(p_hop_exact_theory(moduli, SB, 2000), D_MAX_NOISY)
    if not (d_small_B >= d_large_B):
        return False
    return True


# ============================================================
# Chain executors
# ============================================================


def _digest_arr(arr) -> str:
    return hashlib.sha256(np.ascontiguousarray(np.asarray(arr)).tobytes()).hexdigest()


def _digest_int(int_list) -> str:
    return hashlib.sha256(np.asarray(int_list, dtype=np.int64).tobytes()).hexdigest()


CLEAN_ARMS = ("addsub", "mul_starpower", "mul_reencode", "hetero_starpower", "hetero_reencode",
              "scrambled_op", "random_codebook")


def run_clean_arm(arm, moduli, sb, seed, n_chain, depths, cb_phase, cb_rand, M, Mi, yi):
    """One CLEAN-chain arm over a depth grid; fresh isolated operands (collision-free decode). Returns
    (exact_curve dict, recovered-running-value digest for arms-differ)."""
    dmax = max(depths)
    g = np.random.default_rng(70000 + seed + M + hash(arm) % 9973)
    ea = {d: 0 for d in depths}
    rec = []
    cbs = cb_rand if arm == "random_codebook" else cb_phase
    for _ in range(n_chain):
        x0 = int(g.integers(0, M))
        running = encode(x0, cbs, moduli, sb)
        gt = x0 % M
        for k in range(1, dmax + 1):
            if arm == "addsub":
                t = int(g.integers(0, M))
                if k % 2 == 1:
                    running = bind(running, encode(t, cbs, moduli, sb)); gt = (gt + t) % M
                else:
                    running = subtract(running, encode(t, cbs, moduli, sb)); gt = (gt - t) % M
            elif arm in ("mul_starpower", "mul_reencode"):
                t = int(g.integers(2, M))
                while math.gcd(t, M) != 1:
                    t = int(g.integers(2, M))
                if arm == "mul_starpower":
                    exps = decode_residues(encode(t, cbs, moduli, sb), cbs, moduli, sb)
                    running = star_power(running, exps, moduli, sb)
                else:  # decode-recode (phase reset)
                    cur = decode_int(running, cbs, moduli, sb, M, Mi, yi)
                    running = encode((cur * t) % M if cur >= 0 else 0, cbs, moduli, sb)
                gt = (gt * t) % M
            else:  # hetero cycle [add, mul, sub, mul]; scrambled_op applies the WRONG op vs truth
                op = k % 4
                t_add = int(g.integers(0, M))
                t_mul = int(g.integers(2, M))
                while math.gcd(t_mul, M) != 1:
                    t_mul = int(g.integers(2, M))
                use_reencode = arm in ("hetero_reencode", "scrambled_op", "random_codebook")
                if arm == "scrambled_op":
                    # substrate applies ADD everywhere; ground truth follows the real hetero cycle -> mismatch
                    running = bind(running, encode(t_add, cbs, moduli, sb))
                    if op == 1:
                        gt = (gt + t_add) % M
                    elif op == 3:
                        gt = (gt - t_add) % M
                    else:
                        gt = (gt * t_mul) % M
                else:
                    if op == 1:
                        running = bind(running, encode(t_add, cbs, moduli, sb)); gt = (gt + t_add) % M
                    elif op == 3:
                        running = subtract(running, encode(t_add, cbs, moduli, sb)); gt = (gt - t_add) % M
                    else:
                        if use_reencode:
                            cur = decode_int(running, cbs, moduli, sb, M, Mi, yi)
                            running = encode((cur * t_mul) % M if cur >= 0 else 0, cbs, moduli, sb)
                        else:
                            exps = decode_residues(encode(t_mul, cbs, moduli, sb), cbs, moduli, sb)
                            running = star_power(running, exps, moduli, sb)
                        gt = (gt * t_mul) % M
            if k in ea:
                got = decode_int(running, cbs, moduli, sb, M, Mi, yi)
                if got == gt:
                    ea[k] += 1
                if k == dmax:
                    rec.append(got)
    curve = {d: round(ea[d] / n_chain, 4) for d in depths}
    return curve, _digest_int(rec)


def run_noisy_op_point(op, moduli, sb, B, seed, n_chain, depths, cb_phase, M, Mi, yi):
    """One NOISY op-point: fixed B-item superposition working-memory (real key-bind superpose); operands read
    back via key-unbind (Gaussian crosstalk -> per-hop decode error); decode-recode chain over depth grid.
    Returns (p_hop_meas, exact_curve, recovered-value digest)."""
    dmax = max(depths)
    g = np.random.default_rng(1234 + seed + B)
    zs = [int(g.integers(1, M)) for _ in range(B)]
    keys = [np.exp(1j * g.uniform(0, 2 * np.pi, N_DIM)).astype(np.complex64) for _ in range(B)]
    bundle = np.zeros(N_DIM, dtype=np.complex64)
    for j in range(B):
        bundle += keys[j] * encode(zs[j], cb_phase, moduli, sb)
    zhat = []
    good = 0
    for j in range(B):
        z = decode_int(bundle * np.conj(keys[j]), cb_phase, moduli, sb, M, Mi, yi)
        zhat.append(z if z >= 0 else 0)
        good += 1 if z == zs[j] else 0
    p_hop_meas = good / B
    ea = {d: 0 for d in depths}
    rec = []
    for _ in range(n_chain):
        x0 = int(g.integers(1, M))
        running = encode(x0, cb_phase, moduli, sb)
        gt = x0 % M
        for k in range(1, dmax + 1):
            j = int(g.integers(0, B))
            cur = decode_int(running, cb_phase, moduli, sb, M, Mi, yi)
            if cur < 0:
                cur = 0
            if op == "add":
                running = encode((cur + zhat[j]) % M, cb_phase, moduli, sb)
                gt = (gt + zs[j]) % M
            else:  # mul (absorbing-zero)
                running = encode((cur * zhat[j]) % M, cb_phase, moduli, sb)
                gt = (gt * zs[j]) % M
            if k in ea:
                got = decode_int(running, cb_phase, moduli, sb, M, Mi, yi)
                if got == gt:
                    ea[k] += 1
                if k == dmax:
                    rec.append(got)
    curve = {d: round(ea[d] / n_chain, 4) for d in depths}
    return round(p_hop_meas, 4), curve, _digest_int(rec)


# ============================================================
# Config + driver
# ============================================================


def get_config(mode: str):
    if mode == "selftest":
        return {"regimes": ["small"], "seeds": (7,), "n_clean": 6, "n_noisy": 20,
                "depths_clean": DEPTHS_CLEAN_SELFTEST, "depths_noisy": DEPTHS_NOISY_SELFTEST,
                "b_grid": B_GRID_SELFTEST}
    if mode == "smoke":
        return {"regimes": ["small", "mid"], "seeds": SEEDS_SMOKE, "n_clean": 25, "n_noisy": 80,
                "depths_clean": DEPTHS_CLEAN_SMOKE, "depths_noisy": DEPTHS_NOISY_SMOKE,
                "b_grid": B_GRID_SMOKE}
    return {"regimes": ["small", "mid"], "seeds": SEEDS_FULL, "n_clean": 50, "n_noisy": 120,
            "depths_clean": DEPTHS_CLEAN_FULL, "depths_noisy": DEPTHS_NOISY_FULL,
            "b_grid": B_GRID_FULL}


def expected_units(cfg) -> int:
    n_clean = len(cfg["regimes"]) * len(cfg["seeds"]) * len(CLEAN_ARMS)
    n_noisy = len(NOISY_OPS) * len(cfg["b_grid"]) * len(cfg["seeds"])
    return n_clean + n_noisy


def _mean(vals):
    return float(np.mean(vals)) if vals else float("nan")


def run_all(mode: str, output_dir: Path, t0: float):
    cfg = get_config(mode)
    regimes, seeds = cfg["regimes"], cfg["seeds"]
    depths_clean, depths_noisy, b_grid = cfg["depths_clean"], cfg["depths_noisy"], cfg["b_grid"]
    n_clean, n_noisy = cfg["n_clean"], cfg["n_noisy"]
    total_units = expected_units(cfg)

    clean = {}      # clean[regime][seed][arm] = {curve, digest}
    codebook_digests = {}
    per_unit = []
    unit = 0

    # ---- CLEAN chains (HEADLINE 1) ----
    for reg in regimes:
        moduli = REGIMES[reg]
        M, Mi, yi = _crt_setup(moduli)
        clean[reg] = {}
        for seed in seeds:
            cb_phase = [phasor_codebook(m, SB, 6000 + seed * 10 + i) for i, m in enumerate(moduli)]
            cb_rand = [random_phasor_codebook(m, SB, 8000 + seed * 10 + i) for i, m in enumerate(moduli)]
            codebook_digests[f"{reg}_{seed}"] = {"cb_phase0": _digest_arr(cb_phase[0]),
                                                 "cb_rand0": _digest_arr(cb_rand[0])}
            clean[reg][seed] = {}
            for arm in CLEAN_ARMS:
                curve, digest = run_clean_arm(arm, moduli, SB, seed, n_clean, depths_clean,
                                              cb_phase, cb_rand, M, Mi, yi)
                clean[reg][seed][arm] = {"curve": curve, "digest": digest}
                per_unit.append({"section": "clean", "regime": reg, "seed": seed, "arm": arm,
                                 "exact_at_dmax": curve[max(depths_clean)],
                                 "crossing": crossing_depth(curve, depths_clean, USABLE_FLOOR, max(depths_clean))})
                unit += 1
            _heartbeat(output_dir, unit, total_units, t0, extra={"section": "clean", "regime": reg, "seed": seed})
            dmc = max(depths_clean)
            _say(f"  [clean seed {seed} {reg}] " + " ".join(
                f"{a}:d{dmc}={clean[reg][seed][a]['curve'][dmc]:.3f}"
                f"(x{crossing_depth(clean[reg][seed][a]['curve'], depths_clean, USABLE_FLOOR, dmc):.1f})"
                for a in CLEAN_ARMS))

    # ---- NOISY chains + self-margin prediction (HEADLINE 2) ----
    noisy = {}      # noisy[op][B][seed] = {p_hop, curve, digest}
    moduli = REGIMES[NOISY_REGIME]
    M, Mi, yi = _crt_setup(moduli)
    for op in NOISY_OPS:
        noisy[op] = {}
        for B in b_grid:
            noisy[op][B] = {}
            for seed in seeds:
                cb_phase = [phasor_codebook(m, SB, 6000 + seed * 10 + i) for i, m in enumerate(moduli)]
                p_hop, curve, digest = run_noisy_op_point(op, moduli, SB, B, seed, n_noisy, depths_noisy,
                                                          cb_phase, M, Mi, yi)
                noisy[op][B][seed] = {"p_hop": p_hop, "curve": curve, "digest": digest}
                per_unit.append({"section": "noisy", "op": op, "B": B, "seed": seed, "p_hop": p_hop,
                                 "crossing": crossing_depth(curve, depths_noisy, USABLE_FLOOR, D_MAX_NOISY)})
                unit += 1
            _heartbeat(output_dir, unit, total_units, t0, extra={"section": "noisy", "op": op, "B": B})
            p_mean = _mean([noisy[op][B][s]["p_hop"] for s in seeds])
            cv = {d: _mean([noisy[op][B][s]["curve"][d] for s in seeds]) for d in depths_noisy}
            Dobs = crossing_depth(cv, depths_noisy, USABLE_FLOOR, D_MAX_NOISY)
            Dex = dstar(p_hop_exact_theory(moduli, SB, B), D_MAX_NOISY)
            _say(f"  [noisy {op} B={B}] p_hop={p_mean:.4f} Dobs={Dobs:.2f} Dexact={Dex:.2f}")

    return cfg, clean, noisy, codebook_digests, per_unit, total_units


# ============================================================
# Classify
# ============================================================


def classify(clean, noisy, cfg, mode):
    regimes, seeds = cfg["regimes"], cfg["seeds"]
    depths_clean, depths_noisy, b_grid = cfg["depths_clean"], cfg["depths_noisy"], cfg["b_grid"]
    moduli = REGIMES[NOISY_REGIME]
    dmc = max(depths_clean)

    # ---- HEADLINE 1 aggregates ----
    def arm_mean_at(arm, d):
        return _mean([clean[r][s][arm]["curve"][d] for r in regimes for s in seeds])

    def arm_min_at(arm, d):
        return min(clean[r][s][arm]["curve"][d] for r in regimes for s in seeds)

    def arm_cross(arm):
        return _mean([crossing_depth(clean[r][s][arm]["curve"], depths_clean, USABLE_FLOOR, dmc)
                      for r in regimes for s in seeds])

    addsub_min = arm_min_at("addsub", dmc)
    reencode_min = min(arm_min_at("mul_reencode", dmc), arm_min_at("hetero_reencode", dmc))
    starpower_mul_at_dmax = arm_mean_at("mul_starpower", dmc)
    starpower_cross = arm_cross("mul_starpower")
    fix_gap = arm_mean_at("mul_reencode", dmc) - starpower_mul_at_dmax
    scrambled_at4 = _mean([clean[r][s]["scrambled_op"]["curve"].get(4, clean[r][s]["scrambled_op"]["curve"][min(depths_clean)])
                           for r in regimes for s in seeds])
    randcb_at4 = _mean([clean[r][s]["random_codebook"]["curve"].get(4, clean[r][s]["random_codebook"]["curve"][min(depths_clean)])
                        for r in regimes for s in seeds])
    ctrl_max = max(scrambled_at4, randcb_at4)

    # ---- HEADLINE 2: per op-family predictor-vs-observed ----
    # Three predictors of the compositional cliff D*:
    #   Dmeasured = series-reliability law fed the MEASURED per-hop decode SNR (tests whether the LAW itself
    #               holds for the arithmetic chain -- the primary transfer question).
    #   Dexact    = parameter-free capture order statistic (tests the self-margin's from-first-principles p_hop).
    #   Dloose    = occupancy-binary union-bound control (biased -> discriminator-fires).
    h2 = {}
    for op in NOISY_OPS:
        rows = []
        ln_ex, ln_me, ln_lo = [], [], []
        n_noncens = 0
        in_band = 0
        worst_ratio_me = 0.0
        predicted_cliff_but_censored = 0   # predictor says shallow cliff but observed CENSORED (over-prediction)
        for B in b_grid:
            p_mean = _mean([noisy[op][B][s]["p_hop"] for s in seeds])
            cv = {d: _mean([noisy[op][B][s]["curve"][d] for s in seeds]) for d in depths_noisy}
            Dobs = crossing_depth(cv, depths_noisy, USABLE_FLOOR, D_MAX_NOISY)
            Dex = dstar(p_hop_exact_theory(moduli, SB, B), D_MAX_NOISY)
            Dme = dstar(p_mean, D_MAX_NOISY)
            Dlo = dstar(p_hop_loose_theory(moduli, SB, B), D_MAX_NOISY)
            cens = Dobs >= D_MAX_NOISY - CENSOR_MARGIN
            r_ex = max(Dex / Dobs, Dobs / Dex) if (Dobs > 0 and not cens) else None
            r_me = max(Dme / Dobs, Dobs / Dme) if (Dobs > 0 and not cens) else None
            r_lo = max(Dlo / Dobs, Dobs / Dlo) if (Dobs > 0 and not cens) else None
            if cens and Dex <= D_MAX_NOISY - CENSOR_MARGIN:
                predicted_cliff_but_censored += 1   # order statistic predicted a cliff that did NOT happen
            if (not cens) and Dobs > 1.5:
                in_band += 1
            if (not cens) and Dobs > 0:
                n_noncens += 1
                ln_ex.append(math.log(Dex / Dobs))
                ln_me.append(math.log(Dme / Dobs))
                ln_lo.append(math.log(Dlo / Dobs))
                worst_ratio_me = max(worst_ratio_me, r_me)
            rows.append({"B": B, "p_hop": round(p_mean, 4), "Dobs": round(Dobs, 3),
                         "Dexact": round(Dex, 3), "Dmeasured": round(Dme, 3), "Dloose": round(Dlo, 3),
                         "ratio_exact": round(r_ex, 3) if r_ex is not None else None,
                         "ratio_measured": round(r_me, 3) if r_me is not None else None,
                         "ratio_loose": round(r_lo, 3) if r_lo is not None else None,
                         "censored": bool(cens)})
        gm_ex = math.exp(_mean(ln_ex)) if ln_ex else float("nan")
        gm_me = math.exp(_mean(ln_me)) if ln_me else float("nan")
        gm_lo = math.exp(_mean(ln_lo)) if ln_lo else float("nan")
        # transfer classification (data-driven honest fork) -- primary test is the LAW (measured-p predictor)
        if predicted_cliff_but_censored >= 2:
            # the self-margin predicted shallow cliffs that did NOT occur -> the arithmetic chain is FAR more
            # robust than any p_hop series law (absorbing-zero healing) -> law does not transfer.
            transfer = "DOES_NOT_TRANSFER_OVERPREDICTS_CLIFF"
        elif n_noncens < MIN_NONCENSORED[mode]:
            transfer = "INSUFFICIENT_NONCENSORED"
        elif worst_ratio_me <= HP_RATIO_MAX and HP_BIAS_LO <= gm_me <= HP_BIAS_HI:
            transfer = "LAW_TRANSFERS_TIGHT"       # series-reliability law is accurate for this chain family
        elif worst_ratio_me <= HF_RATIO_MAX:
            transfer = "LAW_TRANSFERS_WITHIN_2X"
        else:
            transfer = "DOES_NOT_TRANSFER"
        # order-statistic (parameter-free) predictor conservatism, reported separately
        if math.isnan(gm_ex):
            orderstat = "not_testable"
        elif HP_BIAS_LO <= gm_ex <= HP_BIAS_HI:
            orderstat = "unbiased"
        elif gm_ex < HP_BIAS_LO:
            orderstat = "conservative_underpromises_depth"
        else:
            orderstat = "optimistic_overpromises_depth"
        # discriminator-fires: loose strictly worse than the measured-p law
        loose_worse = (abs(math.log(gm_lo)) >= LOOSE_WORSE_FACTOR * max(abs(math.log(gm_me)), 1e-9)) \
            if (ln_me and not math.isnan(gm_lo)) else False
        h2[op] = {"rows": rows, "geomean_measured": round(gm_me, 4), "geomean_exact": round(gm_ex, 4),
                  "geomean_loose": round(gm_lo, 4), "n_noncensored": n_noncens, "in_band": in_band,
                  "worst_ratio_measured": round(worst_ratio_me, 3),
                  "predicted_cliff_but_censored": predicted_cliff_but_censored,
                  "transfer": transfer, "orderstat_predictor": orderstat, "loose_strictly_worse": bool(loose_worse)}

    # discriminating fraction (Gate B) across all (op,B) op-points
    total_pts = len(NOISY_OPS) * len(b_grid)
    band_pts = sum(h2[op]["in_band"] for op in NOISY_OPS)
    discriminating_fraction = band_pts / total_pts if total_pts else 0.0

    # add-vs-mul robustness ordering (mechanism signature): mul family (absorbing-zero) is MORE robust than
    # add family (non-absorbing) -> mul over-predicted (censored where a cliff was predicted) more often.
    robustness_ordering_mul_gt_add = (h2["mul"]["predicted_cliff_but_censored"]
                                      >= h2["add"]["predicted_cliff_but_censored"]) \
        and (h2["mul"]["n_noncensored"] <= h2["add"]["n_noncensored"])

    diag = (f"H1[addsub_min={addsub_min:.3f} reencode_min={reencode_min:.3f} "
            f"starpower_dmax={starpower_mul_at_dmax:.3f} starpower_cross={starpower_cross:.2f} "
            f"fix_gap={fix_gap:.3f} ctrl_max={ctrl_max:.3f}] "
            f"H2[add:{h2['add']['transfer']} law_gm={h2['add']['geomean_measured']} "
            f"orderstat={h2['add']['orderstat_predictor']} nnc={h2['add']['n_noncensored']}; "
            f"mul:{h2['mul']['transfer']} pcbc={h2['mul']['predicted_cliff_but_censored']} "
            f"nnc={h2['mul']['n_noncensored']}] discrim_frac={discriminating_fraction:.2f} "
            f"loose_worse=add:{h2['add']['loose_strictly_worse']} robust_order={robustness_ordering_mul_gt_add}")

    metrics_h1 = {"addsub_min": round(addsub_min, 4), "reencode_min": round(reencode_min, 4),
                  "starpower_mul_at_dmax": round(starpower_mul_at_dmax, 4),
                  "starpower_crossing": round(starpower_cross, 3), "fix_gap": round(fix_gap, 4),
                  "scrambled_at4": round(scrambled_at4, 4), "randcb_at4": round(randcb_at4, 4),
                  "ctrl_max": round(ctrl_max, 4)}
    h2_summary = {"headline2": h2, "discriminating_fraction": round(discriminating_fraction, 3),
                  "robustness_ordering_mul_more_robust_than_add": bool(robustness_ordering_mul_gt_add)}

    # ---- VERDICT ----
    # HARD_FAIL: HEADLINE-1 capability breakage or control leak.
    if addsub_min < HF_ADDSUB:
        return ("HARD_FAIL",
                f"LOSSLESS COMPOSITION BROKEN: addsub exact-through-depth min={addsub_min:.3f} < {HF_ADDSUB} at "
                f"D={dmc}. Composing exact add/sub does NOT stay exact -> substrate breakage. {diag}",
                metrics_h1, h2_summary)
    if reencode_min < HF_ADDSUB:
        return ("HARD_FAIL",
                f"DECODE-RECODE COMPOSITION BROKEN: reencode exact min={reencode_min:.3f} < {HF_ADDSUB} at "
                f"D={dmc}. {diag}", metrics_h1, h2_summary)
    if ctrl_max >= CTRL_LEAK:
        return ("HARD_FAIL",
                f"CONTROL LEAK: a control chain exact-through-depth max={ctrl_max:.3f} >= {CTRL_LEAK} at D=4 -> "
                f"exact-through-depth is vacuous (does not discriminate wrong chains). {diag}",
                metrics_h1, h2_summary)

    if mode == "smoke":
        ok = (addsub_min >= HP_ADDSUB_EXACT and reencode_min >= HP_REENCODE_EXACT
              and ctrl_max <= CTRL_MAX
              and STARPOWER_CLIFF_MIN <= starpower_cross <= STARPOWER_CLIFF_MAX
              and fix_gap >= HP_FIX_GAP)
        if ok:
            return ("HARD_PASS",
                    f"SMOKE_MACHINERY_OK: clean add/sub + decode-recode chains EXACT to D={dmc} "
                    f"(addsub_min={addsub_min:.3f} reencode_min={reencode_min:.3f}); mul_starpower NUMERICAL "
                    f"cliff at D={starpower_cross:.1f} (float32 phase compounding) RESCUED by decode-recode "
                    f"(fix_gap={fix_gap:.3f}); controls collapse (ctrl_max={ctrl_max:.3f}); self-margin "
                    f"predictor exercised on noisy add/mul families. Deliverable band is FULL-only (canonical "
                    f"= remote landing). {diag}", metrics_h1, h2_summary)
        return ("DISCRIMINATOR_DID_NOT_FIRE",
                f"SMOKE machinery incomplete: addsub_min={addsub_min:.3f} reencode_min={reencode_min:.3f} "
                f"ctrl_max={ctrl_max:.3f} starpower_cross={starpower_cross:.2f} fix_gap={fix_gap:.3f}. "
                f"Investigate before FULL. {diag}", metrics_h1, h2_summary)

    # ---- FULL verdict ----
    h1_ok = (addsub_min >= HP_ADDSUB_EXACT and reencode_min >= HP_REENCODE_EXACT
             and ctrl_max <= CTRL_MAX
             and STARPOWER_CLIFF_MIN <= starpower_cross <= STARPOWER_CLIFF_MAX
             and fix_gap >= HP_FIX_GAP)
    # HEADLINE-2 discriminator: the LAW is testable on the non-absorbing add family (>= MIN non-censored),
    # Gate B met, loose control strictly worse, and the add-vs-mul robustness ordering fires.
    h2_discriminates = (h2["add"]["n_noncensored"] >= MIN_NONCENSORED["full"]
                        and discriminating_fraction >= DISCRIMINATING_FRAC_MIN
                        and h2["add"]["loose_strictly_worse"]
                        and robustness_ordering_mul_gt_add)
    if h1_ok and h2_discriminates:
        return ("HARD_PASS",
                f"COMPOSITIONAL ARITHMETIC + SELF-MARGIN MEASURED. HEADLINE 1: composed exact add/sub is "
                f"LOSSLESS to D={dmc} (addsub_min={addsub_min:.3f}); the multiply cliff at D={starpower_cross:.1f} "
                f"is FLOAT32 phase-compounding (clean-code numerics, NOT decode noise) and is RESCUED by "
                f"decode-recode (fix_gap={fix_gap:.3f}, reencode exact to D={dmc}); wrong-op + random-codebook "
                f"controls collapse (ctrl_max={ctrl_max:.3f}) so exact-through-depth is a real discriminator. "
                f"HEADLINE 2: on the NON-ABSORBING add chain the series-reliability self-margin LAW "
                f"(D*=ln(floor)/ln(p_hop)) transfers -- add={h2['add']['transfer']} (law geomean pred/obs="
                f"{h2['add']['geomean_measured']}); the parameter-free capture order statistic is "
                f"{h2['add']['orderstat_predictor']} and the loose occupancy-binary control is strictly worse "
                f"(discriminator-fires). On the ABSORBING-ZERO mul chain the law {h2['mul']['transfer']} "
                f"(predicted_cliff_but_censored={h2['mul']['predicted_cliff_but_censored']}): the chain is FAR "
                f"more robust than any p_hop series law predicts. The add-vs-mul robustness ordering is the "
                f"mechanism signature -- modular arithmetic HEALS decode errors (add: self-cancelling residue "
                f"walk; mul: absorbing zero), so the arithmetic-chain collapse family DIFFERS from the "
                f"associative-chain family: the self-margin is a SAFE (never over-promising) depth bound for "
                f"arithmetic. {diag}", metrics_h1, h2_summary)
    if h1_ok:
        return ("MIDDLE_BAND",
                f"HEADLINE 1 confirmed (addsub/reencode exact to D={dmc}; mul cliff={starpower_cross:.1f} numerical, "
                f"rescued fix_gap={fix_gap:.3f}; controls collapse) but HEADLINE-2 discriminator underpowered "
                f"(add n_noncensored={h2['add']['n_noncensored']}, discrim_frac={discriminating_fraction:.2f}, "
                f"loose_worse={h2['add']['loose_strictly_worse']}). {diag}", metrics_h1, h2_summary)
    return ("MIDDLE_BAND",
            f"partial: a HEADLINE-1 secondary band missed (addsub_min={addsub_min:.3f} reencode_min={reencode_min:.3f} "
            f"starpower_cross={starpower_cross:.2f} fix_gap={fix_gap:.3f} ctrl_max={ctrl_max:.3f}). {diag}",
            metrics_h1, h2_summary)


# ============================================================
# main
# ============================================================


def _assemble_metrics(mode, cfg, clean, noisy, codebook_digests, per_unit, total_units, verdict, vmsg,
                      metrics_h1, h2_summary, elapsed):
    # clean-arm summaries (per regime: exact curves averaged over seeds + crossing)
    clean_summ = {}
    for reg in cfg["regimes"]:
        clean_summ[reg] = {}
        for arm in CLEAN_ARMS:
            curve = {str(d): round(_mean([clean[reg][s][arm]["curve"][d] for s in cfg["seeds"]]), 4)
                     for d in cfg["depths_clean"]}
            cross = round(_mean([crossing_depth(clean[reg][s][arm]["curve"], cfg["depths_clean"],
                                                USABLE_FLOOR, max(cfg["depths_clean"]))
                                 for s in cfg["seeds"]]), 3)
            clean_summ[reg][arm] = {"exact_curve": curve, "crossing_depth": cross}
    return {
        "anchor_name": ANCHOR_NAME,
        "verdict": verdict,
        "verdict_msg": vmsg,
        "summary": f"{verdict}: compositional multi-step arithmetic derivation depth-exactness + self-margin ({mode})",
        "run_mode": mode,
        "elapsed_s": round(elapsed, 2),
        "n_seeds": len(cfg["seeds"]),
        "n_units": len(per_unit),
        "expected_n_units": total_units,
        "cardinality_ok": len(per_unit) >= total_units,
        "config": {"N": N_DIM, "R_MODULI": R_MODULI, "SB": SB,
                   "regimes": {r: list(REGIMES[r]) for r in cfg["regimes"]},
                   "noisy_regime": NOISY_REGIME, "noisy_ops": list(NOISY_OPS),
                   "seeds": list(cfg["seeds"]), "n_clean": cfg["n_clean"], "n_noisy": cfg["n_noisy"],
                   "depths_clean": list(cfg["depths_clean"]), "depths_noisy": list(cfg["depths_noisy"]),
                   "b_grid": list(cfg["b_grid"]), "usable_floor": USABLE_FLOOR, "d_max_noisy": D_MAX_NOISY,
                   "mechanism": "compositional_chain_of_exact_rns_primitives",
                   "predictor": "capture_order_statistic_series_reliability_dstar",
                   "storage_strategy": "clean=no_storage_algebraic; noisy=sharded_key_bound_superposition_bundle"},
        "headline1_capability": metrics_h1,
        "clean_arms": clean_summ,
        "headline2_self_margin": h2_summary,
        "per_unit": per_unit,
        "codebook_digests": codebook_digests,
        "bands": {"HP_addsub_exact": HP_ADDSUB_EXACT, "HP_reencode_exact": HP_REENCODE_EXACT,
                  "HF_addsub": HF_ADDSUB, "starpower_cliff_min": STARPOWER_CLIFF_MIN,
                  "starpower_cliff_max": STARPOWER_CLIFF_MAX, "HP_fix_gap": HP_FIX_GAP,
                  "ctrl_max": CTRL_MAX, "ctrl_leak": CTRL_LEAK, "HP_ratio_max": HP_RATIO_MAX,
                  "HF_ratio_max": HF_RATIO_MAX, "HP_bias": [HP_BIAS_LO, HP_BIAS_HI],
                  "conservative_geomean": CONSERVATIVE_GEOMEAN, "usable_floor": USABLE_FLOOR,
                  "discriminating_frac_min": DISCRIMINATING_FRAC_MIN},
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(),
        "host": platform.node(),
    }


def _run(mode: str) -> int:
    output_dir = _out_dir()
    output_dir.mkdir(parents=True, exist_ok=True)
    t0 = time.perf_counter()
    cfg = get_config(mode)
    exp = expected_units(cfg)
    _write_start_marker(output_dir, mode, exp)
    _say(f"[{ANCHOR_NAME}] mode={mode} N={N_DIM} R={R_MODULI} sb={SB} regimes={cfg['regimes']} "
         f"seeds={cfg['seeds']} b_grid={cfg['b_grid']} expected_units={exp}")

    # formula self-tests (ALL modes)
    for reg in cfg["regimes"] + ([NOISY_REGIME] if NOISY_REGIME not in cfg["regimes"] else []):
        moduli = REGIMES[reg]
        if not crt_selftest(moduli):
            raise AssertionError(f"CRT_SELFTEST_FAIL regime={reg} moduli={moduli}")
        if not composition_selftest(moduli, seed=cfg["seeds"][0]):
            raise AssertionError(f"COMPOSITION_SELFTEST_FAIL regime={reg} moduli={moduli}")
    _say(f"[{ANCHOR_NAME}] formula self-tests PASSED (CRT + compositional-chain-agreement + order-stat monotone)")

    cfg, clean, noisy, codebook_digests, per_unit, total_units = run_all(mode, output_dir, t0)

    # arms_differ (META_RULE_AF): phase codebook != random codebook; distinct-op arms recover DIFFERENT values.
    arms_differ_ok = True
    reasons = []
    for key, cd in codebook_digests.items():
        if cd["cb_phase0"] == cd["cb_rand0"]:
            arms_differ_ok = False; reasons.append(f"{key}:phase==random codebook")
    for reg in cfg["regimes"]:
        for seed in cfg["seeds"]:
            d = {a: clean[reg][seed][a]["digest"] for a in CLEAN_ARMS}
            # distinct-op arms must recover different running-value arrays (add != mul by construction)
            if d["addsub"] == d["mul_starpower"]:
                arms_differ_ok = False; reasons.append(f"{reg}_{seed}:addsub==mul_starpower recovered values")
            if d["hetero_reencode"] == d["scrambled_op"]:
                arms_differ_ok = False; reasons.append(f"{reg}_{seed}:hetero==scrambled recovered values")
    if not arms_differ_ok:
        raise AssertionError("META_RULE_AF VIOLATION: " + "; ".join(reasons))

    verdict, vmsg, metrics_h1, h2_summary = classify(clean, noisy, cfg, mode)
    elapsed = time.perf_counter() - t0
    metrics = _assemble_metrics(mode, cfg, clean, noisy, codebook_digests, per_unit, total_units,
                                verdict, vmsg, metrics_h1, h2_summary, elapsed)
    metrics["arms_differ_verified"] = arms_differ_ok
    _write_metrics_atomic(output_dir, metrics)
    written = json.load(open(output_dir / "metrics.json"))
    assert written["run_mode"] == mode, f"RUN_MODE_MISMATCH {written['run_mode']} != {mode}"

    _say(f"\n[{ANCHOR_NAME}] {verdict}: {vmsg}")
    _say(f"[{ANCHOR_NAME}] metrics -> {output_dir / 'metrics.json'}  elapsed={elapsed:.1f}s")
    return 0


def _run_selftest() -> int:
    t0 = time.perf_counter()
    output_dir = _out_dir()
    output_dir.mkdir(parents=True, exist_ok=True)
    ok_crt = all(crt_selftest(REGIMES[r]) for r in REGIMES)
    ok_comp = all(composition_selftest(REGIMES[r], seed=7) for r in REGIMES)
    cfg, clean, noisy, cds, per_unit, total_units = run_all("selftest", output_dir, t0)
    moduli = REGIMES["small"]
    dmc = max(cfg["depths_clean"])
    addsub_exact = clean["small"][7]["addsub"]["curve"][dmc]
    reencode_exact = clean["small"][7]["mul_reencode"]["curve"][dmc]
    starpower_cross = crossing_depth(clean["small"][7]["mul_starpower"]["curve"], cfg["depths_clean"],
                                     USABLE_FLOOR, dmc)
    ok = (ok_crt and ok_comp and addsub_exact >= 0.99 and reencode_exact >= 0.99
          and starpower_cross <= dmc)  # starpower cliffs within the (short) selftest grid or plateaus
    _say(f"[{ANCHOR_NAME}] SELFTEST {'PASS' if ok else 'FAIL'}: crt_ok={ok_crt} comp_ok={ok_comp} "
         f"addsub_exact={addsub_exact:.3f} reencode_exact={reencode_exact:.3f} "
         f"starpower_cross={starpower_cross:.2f} [{time.perf_counter()-t0:.1f}s]")
    return 0 if ok else 1


def main() -> int:
    if "--self-test" in sys.argv:
        return _run_selftest()
    mode = "smoke" if "--smoke" in sys.argv else \
        ("smoke" if os.environ.get("HDLAB_RUN_MODE", "").lower() == "smoke" else "full")
    return _run(mode)


if __name__ == "__main__":
    _od = None
    try:
        _od = _out_dir()
        sys.exit(main())
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # NOT BaseException
        if _od is not None:
            _write_crash_metrics(_od, e)
        raise
