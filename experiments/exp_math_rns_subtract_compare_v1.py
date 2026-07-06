# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate: phase-linear codebook vs random-phasor codebook hash-distinct;
#     arm subtract-recovered integers vs scrambled-CRT recovered integers hash-distinct; half-range compare
#     predictions vs decode-SKIPPING control predictions (native_vector_signtest, order_blind) hash-distinct.
#     EXEMPT PAIR (arms_differ_exempted): decode_then_compare_baseline vs compare_halfrange -- both are EXACT
#     within range and therefore produce IDENTICAL correct labels by construction (that identity is the
#     honesty finding, not a bug); we do NOT hash-compare those two. We hash CODEBOOKS + RECOVERED-integer +
#     decode-SKIPPING-control predictions, which DO differ.
# - final_metrics_atomicity: tmp_replace (write metrics.json.tmp then os.replace).
# - except SystemExit: raise BEFORE except Exception (no BaseException).
# - crlb/capacity-feasibility: per-residue decode is a phasor argmax over m_i candidates in a sub-block of
#     dim sb=2730 (N=8192, R=3). SNR ~ sqrt(sb) rank-1 vs ~1/sqrt(sb) runner-up; sb=2730 >> max modulus 43,
#     so per-residue argmax is collision-free (rank-1 == 1.0, runner-up ~ 0.019). No superposition-noise
#     floor gates the 0.99 exact-subtract / exact-decode-then-compare target. discriminator_reachability=True.
# - baseline_in_band (META_RULE_AG): this is an EXACTNESS/CORRECTNESS test, not a difficulty sweep. The
#     mechanism-of-record for compare (decode_then_compare_baseline) and sub_phase are ~1.0 by exact CRT
#     construction; subtract controls (random-phasor, scrambled-modulus) are intentionally ~0.0; the
#     decode-SKIPPING compare controls (native_vector_signtest, order_blind) are intentionally ~chance on
#     ORDERING (a single channel / raw residues carry no order). Discriminators are CONTRASTS; none saturate
#     at scale (random-subtract -> 1/M as M grows; decode-skipping ORDERING stays ~0.5 chance).
# - discriminator survives scale: smoke runs at FULL N=8192, FULL sb=2730, ALL 3 moduli regimes (small
#     M=504, mid M=5168, large M=70520). Smoke reduces trials/seeds/depths ONLY. sub-exact + random-collapse
#     + scram-collapse + decode_then_compare-exact + halfrange-exact + native_signtest-collapse +
#     order_blind-collapse + chain-exact all FIRE in smoke (DISCRIMINATOR-MUST-SURVIVE-SCALE option A).
# - HARD_PASS strictly above floor: sub_phase HP 0.99 (HF 0.60); decode_then_compare 3-way HP 0.99 (HF 0.70);
#     MEASURED expectation ~1.0. The real compare discriminator is decode-based (baseline OR half-range, both
#     ~1.0) vs decode-SKIPPING (~chance), NOT half-range vs baseline (they MATCH -- the honesty finding).
# - all numbers in comments tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@.
#
# MATH CAPABILITY -- RNS SUBTRACTION + THREE-WAY NUMERIC-THRESHOLD COMPARISON  v1
# ==============================================================================
# SECOND real math-capability cell. Extends the landed exact-ADDITION cell
# (exp_math_rns_add_chain_v1, FULL HARD_PASS exact-add=1.000
# MEASURED@data/exp_math_rns_add_chain_v1/metrics.json:arms.small.phase_linear_add.exact_mean) with the two
# next primitives self-reasoning / self-VET needs: SUBTRACTION and NUMERIC-THRESHOLD ORDER COMPARISON
# (a<b / a==b / a>b, i.e. does a >= threshold). Both reuse the add cell's phase-linear phasor encoding + CRT
# decode VERBATIM. Two independent research threads converged on this gap:
#   CITED@notes/research_math_arithmetic_basis_next_primitives_2026-07-05.md (Q2/Q3/Q4 mechanism + bands)
#   CITED@notes/research_entailment_self_check_first_cell_2026-07-05.md (native-signtest recheck + baseline gate)
#
# MECHANISM 1 -- SUBTRACTION IS FREE (conjugate phasor is the additive-group inverse):
#   codebook_m[r,j] = exp(i*2*pi*k_j*r/m). conj(enc(b)) = exp(-i*2*pi*k_j*b/m) = enc((-b) mod m). So the
#   EXISTING FHRR bind (elementwise complex product) of enc(a) with conj(enc(b)) is
#       enc(a) (*) conj(enc(b)) == enc((a-b) mod m)     [additive inverse of the SAME group homomorphism]
#   Decode via the SAME per-sub-block phasor argmax + CRT. No new operator, no new codebook, no moduli
#   constraint. (THEORETICAL: (Z_m,+) is a group -> every element has an inverse; conjugation IS it.)
#
# COMPARISON -- THE HONESTY GATE (does ANY residue-native comparator beat decode-then-compare?):
#   In THIS substrate the CRT decode is EXACT (proven by the add cell), so the STRONG BASELINE
#   `decode_then_compare` -- decode a and b to integers (two exact CRT decodes) and compare them in plain
#   scalar space -- is ALREADY exact over the FULL range [0,M) with NO dynamic-range caveat. The cell's job
#   is to test honestly whether the residue-native `half-range sign detection` (subtract, decode the SINGLE
#   difference d=(a-b) mod M, threshold vs M/2) adds anything OVER that baseline. It does NOT: half-range
#   MATCHES the baseline within |a-b| < M/2 and is STRICTLY WORSE outside it (silent mis-sign, no residue-only
#   error signal) where the baseline stays exact. Its only merit is one decode instead of two. Decode-SKIPPING
#   comparators FAIL: `native_vector_signtest` (single-channel sign read, the discrete-rep analog of the
#   prior FULL HARD_FAIL comparator, comp_acc=0.8556 < raw=0.8944, lift=-0.0389
#   MEASURED@data/exp_comparator_resonator_primitive_smoke_v1/metrics.json:summary) and `order_blind`
#   (raw-residue lexicographic) both collapse to ~chance on ORDERING because residues/single-channels carry
#   no order. HONEST DESIGN FINDING (reported, not forced): the substrate's exact decode makes numeric-
#   threshold comparison trivial via decode-then-compare; no NEW residue-native comparison mechanism is
#   needed for correctness -- half-range is validated only as a correct, range-limited efficiency variant.
#   (CITED@Hung & Parhami 1994 sign detection; Szabo & Tanaka 1967 RNS signed range -floor(M/2)..floor((M-1)/2).)
#
# ARMS (all PAIRED on identical integer pairs per regime/seed):
#   SUBTRACT:
#     sub_phase           : MECHANISM -- conjugate-bind subtract; decode=argmax+CRT; exact (a-b) mod M incl
#                           wraparound. Expected ~1.0.                                          [MECHANISM]
#     sub_random          : CONTROL -- IDENTICAL pipeline, RANDOM phasors (not linear in r) -> no
#                           homomorphism. Isolates phase-LINEARITY. ~0.0.                        [CONTROL]
#     sub_scram           : CONTROL -- arm phasor decode then DERANGE residues before CRT. CRT load-bearing. ~0.0.
#     add_inverse_id      : PRIMITIVE -- decode(subtract(enc(a),enc(a)))==0 for all a (conjugation cancels). 1.0.
#     sub_chain_dL        : subtract over an L-step running-difference chain, L in {1,3,5,10}. Group-exact.
#   COMPARE (three-way {GT,EQ,LT}; in-range a,b in [0,M//2)):
#     decode_then_compare : STRONG BASELINE / mechanism-of-record -- decode a,b separately, compare integers.
#                           Exact, FULL-range. Expected ~1.0. THE honest bar every native comparator is judged against.
#     compare_halfrange   : residue-native mechanism UNDER TEST -- decode the single difference d, threshold
#                           vs M//2. Expected ~1.0 in-range; reports lift over baseline (expected ~0.000).
#     native_vector_signtest: CONTROL / PRIOR-NEGATIVE recheck -- single-channel sign read (decode ONLY residue
#                           0, half-range on m0; NO full CRT reconstruction). Discrete-rep analog of the closed
#                           comparator_resonator HARD_FAIL. Expected ~chance ORDERING (negative is mechanism-general).
#     order_blind         : CONTROL -- order from raw residue tuple lexicographically. EQ exact; ORDERING ~chance.
#     compare_random      : CONTROL -- half-range rule on random-codebook (garbage) decode. ~chance.
#     eq_detect           : a==b correctly labeled EQ by the decode mechanism. Expected 1.0.
#   REPORTED (not pass-gated on their own):
#     compare_out_of_range: |a-b| >= M//2 -> half-range mis-sign rate (documented limitation) AND
#                           decode_then_compare accuracy (~1.0; the baseline is unaffected -> baseline strictly safer).
#     compare_near_boundary: |a-b| just below M//2 -> half-range accuracy (fragility probe). Expected 1.0.
#     threshold_entailment: does a >= threshold hold, over realistic (metric,threshold) pairs (self-VET target).
#
# is-math-easier PROBE (near-miss margin): arm subtract decode runner-up vs rank-1 (reused from add cell). Reported.
# Brain-grounding (CITED@): entorhinal grid cells ARE an RNS (Sreenivasan & Fiete 2011); abstract-magnitude
# grid codes (Constantinescu/O'Reilly/Behrens 2016). Subtract = the group inverse; compare = a magnitude read-out.
#
# ASCII-only. CPU default (numpy complex64; no GPU, no LLM; wall < 15s total -> sequential-CPU justified).
# Self-contained (synthetic phasor codebooks; no pool/re-encode dependency).
# Run: python experiments/exp_math_rns_subtract_compare_v1.py [--self-test | --smoke]
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

ANCHOR_NAME = "math_rns_subtract_compare_v1"
REPO = Path(__file__).resolve().parents[1]

N_DIM = 8192          # substrate compositional default (== landed add / rns_crt cells); never reduced
R_MODULI = 3          # residues per integer (disjoint sub-blocks)
SB = N_DIM // R_MODULI  # 2730 dims per sub-block; sb >> max modulus 43 -> collision-free phasor decode

# Three moduli regimes reused VERBATIM from the landed add cell (subtract + compare need NO prime
# constraint). Each pairwise-coprime (asserted); M = prod; half = M//2 is the half-range threshold.
REGIMES = {
    "small": (7, 8, 9),      # M=504,   half=252
    "mid":   (16, 17, 19),   # M=5168,  half=2584
    "large": (40, 41, 43),   # M=70520, half=35260
}
SEEDS = (7, 13, 19)
DEPTHS_FULL = (1, 3, 5, 10)

# Readable subtract examples (small regime, M=504): (a,b) -> (a-b) mod 504. #4 wraps (2-503=-501 -> 3).
DEMO_SUB = [(12, 5), (5, 12), (7, 7), (250, 100), (2, 503)]
# Readable in-range compare examples (both < half=252): (a,b) -> {GT,EQ,LT}.
DEMO_CMP = [(12, 5), (5, 12), (7, 7), (200, 100), (100, 200)]
# Realistic self-VET threshold-entailment demos (large regime; ints represent metric*10000): (metric,thresh).
DEMO_THRESH = [(8860, 8000), (7200, 8000), (8000, 8000), (9500, 9000), (7990, 8000)]

# ---- Pre-registered bands (HYPOTHESIZED from exact-homomorphism theory; MEASURED filled by smoke) ----
HP_SUB_EXACT = 0.99    # HARD_PASS: sub_phase exact-subtract floor (THEORETICAL ~1.0; inverse of exact hom.)
HP_CV = 0.10           # HARD_PASS: cross-seed cv of sub_phase (THEORETICAL 0.0)
HF_SUB = 0.60          # HARD_FAIL: sub_phase below -> conjugate-inverse does not transfer at substrate scale
B_CTRL_MAX = 0.15      # control: random-codebook subtract must FAIL (be below this)
B_LEAK = 0.40          # HARD_FAIL: random-codebook subtract >= this -> leak (verify-the-referent)
C_SCRAM_MAX = 0.05     # control: scrambled-modulus subtract must collapse below this
HP_ADD_INV = 0.99      # HARD_PASS: additive-inverse identity subtract(enc(a),enc(a))==0
HP_COMPARE_3WAY = 0.99 # HARD_PASS: decode_then_compare 3-way accuracy floor (mechanism-of-record; ~1.0)
HP_HALFRANGE_3WAY = 0.99  # HARD_PASS: compare_halfrange 3-way accuracy floor within valid range (~1.0)
HF_COMPARE = 0.70      # HARD_FAIL: decode_then_compare 3-way below -> exact decode does not transfer (deep breakage)
HP_ORDER_ACC = 0.99    # HARD_PASS: decode-based ORDERING sub-accuracy (GT vs LT; baseline + half-range)
DECODESKIP_ORDER_MAX = 0.72  # control: decode-SKIPPING ORDERING sub-acc must collapse below (chance 0.5)
HALFRANGE_LIFT_TOL = 0.02    # honesty gate: |halfrange_3way - baseline_3way| expected ~0 (report; not a fail-gate)
HP_CHAIN_D3 = 0.75     # HARD_PASS: depth-3 subtract-chain exact floor (THEORETICAL ~1.0)
HF_CHAIN_D3 = 0.20     # HARD_FAIL: depth-3 below -> chains drift worse than reasoning collision-bound law
HP_EQ_DETECT = 0.99    # HARD_PASS: a==b pairs correctly labeled EQ by the decode mechanism
HP_THRESH_ENTAIL = 0.99  # HARD_PASS: a>=threshold entailment accuracy (self-VET target; in-range)
NEARMISS_FRAC = 0.90   # is-math-easier: fraction of residue decodes with runner-up <= 0.5*rank-1 (reported)


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
# Phasor codebooks + encode / bind / subtract / decode (encode/bind/decode reused VERBATIM from add cell)
# ============================================================


def phasor_codebook(m: int, sb: int, seed: int) -> np.ndarray:
    """Phase-LINEAR FPE codebook (m, sb) complex64: codebook[r,j] = exp(i*2*pi*k_j*r/m), k_j in [1,m-1].
    Integer k_j -> exact period-m periodicity -> bind IS modular addition; conjugation IS the additive
    inverse -> conjugate-bind IS modular subtraction."""
    g = np.random.default_rng(seed)
    k = g.integers(1, m, size=sb).astype(np.float64)          # nonzero integer frequencies
    r = np.arange(m, dtype=np.float64)[:, None]               # (m,1)
    phase = (2.0 * np.pi / m) * (r * k[None, :])              # (m,sb)
    return np.exp(1j * phase).astype(np.complex64)


def random_phasor_codebook(m: int, sb: int, seed: int) -> np.ndarray:
    """Control codebook (m, sb) complex64: random unit phasor per (r,j), NOT linear in r. Identical modulus
    (unit-magnitude), identical bind/decode -- ONLY the phase-linearity is removed (isolates the homomorphism)."""
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
    """FHRR bind: elementwise complex product. Disjoint sub-blocks -> adds all residues simultaneously."""
    return u * v


def subtract(u: np.ndarray, v: np.ndarray) -> np.ndarray:
    """FHRR conjugate-bind: enc(a) (*) conj(enc(b)) == enc((a-b) mod M). Subtraction is the additive
    inverse of the SAME group homomorphism -- no new operator, just conj() on the second operand."""
    return u * np.conj(v)


def decode_residues(v: np.ndarray, cbs, moduli, sb: int, want_margin: bool = False):
    """Per-sub-block phasor argmax -> residues. If want_margin: also return (rank1, rank2) normalized sims."""
    residues = []
    margins = []
    for i, m in enumerate(moduli):
        sub = v[i * sb:(i + 1) * sb]
        sims = (cbs[i] @ np.conj(sub)).real / sb          # (m,) normalized; true residue -> ~1.0
        r = int(np.argmax(sims))
        residues.append(r)
        if want_margin:
            top2 = np.sort(sims)[::-1][:2]
            margins.append((float(top2[0]), float(top2[1] if len(top2) > 1 else 0.0)))
    return (residues, margins) if want_margin else residues


def decode_int(v, cbs, moduli, sb, M, Mi, yi, scramble=None):
    """Decode to integer in [0,M): phasor argmax residues -> CRT. scramble (a derangement) permutes residues
    before CRT (scrambled-modulus control)."""
    residues = decode_residues(v, cbs, moduli, sb)
    if scramble is not None:
        residues = [residues[scramble[i]] for i in range(len(residues))]
    return _crt(residues, moduli, M, Mi, yi)


# ============================================================
# Compare primitives (half-range sign detection + decode-skipping controls)
# ============================================================


def signed_diff(d: int, M: int) -> int:
    """Interpret d = (a-b) mod M as a signed value on the half-range convention. |a-b| < M/2 required."""
    half = M // 2
    return d if d <= half else d - M


def compare_from_diff(d: int, M: int) -> int:
    """Half-range sign detection -> {+1 GT, 0 EQ, -1 LT}."""
    s = signed_diff(d, M)
    if s > 0:
        return 1
    if s < 0:
        return -1
    return 0


def true_3way(a: int, b: int) -> int:
    return 0 if a == b else (1 if a > b else -1)


def compare_order_blind(a: int, b: int, moduli) -> int:
    """CONTROL: order from RAW residue tuple lexicographically, WITHOUT CRT decode + M/2 threshold.
    Residues determine value uniquely (CRT) so equal residues == equal value -> EQ exact; but residue
    ordering is NOT value ordering -> GT/LT collapses to chance."""
    ra = tuple(a % m for m in moduli)
    rb = tuple(b % m for m in moduli)
    if ra == rb:
        return 0
    return 1 if ra > rb else -1


def native_vector_signtest(dvec, cbs, moduli, sb) -> int:
    """CONTROL / PRIOR-NEGATIVE recheck: single-channel sign read -- decode ONLY residue 0 (one sub-block),
    half-range threshold on m0, NO full CRT reconstruction. Discrete-rep analog of the closed FULL HARD_FAIL
    comparator_resonator sign-test. r0 = (a-b) mod m0 does NOT preserve the sign of the full-M difference ->
    ORDERING collapses to chance (confirms the historical negative is mechanism-general, not FPE-specific)."""
    m0 = moduli[0]
    sub0 = dvec[0:sb]
    sims = (cbs[0] @ np.conj(sub0)).real / sb
    r0 = int(np.argmax(sims))
    return compare_from_diff(r0, m0)


# ============================================================
# Formula self-tests (MANDATORY per task): subtract homomorphism + compare correctness
# ============================================================


def subtract_homomorphism_selftest(moduli, seed: int = 0) -> bool:
    """Formula self-test 2: decode(subtract(enc(a),enc(b))) == (a-b) mod M for random a,b (additive inverse
    of the group homomorphism); AND per-sub-block identity conj-product == codeword-of-difference; AND the
    additive-inverse identity subtract(enc(a),enc(a)) decodes to exactly 0."""
    M, Mi, yi = _crt_setup(moduli)
    cbs = [phasor_codebook(m, SB, 6000 + seed * 10 + i) for i, m in enumerate(moduli)]
    for i, m in enumerate(moduli):
        for _ in range(8):
            a = int(np.random.default_rng(seed + i + _).integers(0, m))
            b = int(np.random.default_rng(seed + i + _ + 99).integers(0, m))
            prod = cbs[i][a] * np.conj(cbs[i][b])
            target = cbs[i][(a - b) % m]
            if not np.allclose(prod, target, atol=1e-4):
                return False
    rng = np.random.default_rng(4242 + seed)
    for _ in range(64):
        a = int(rng.integers(0, M)); b = int(rng.integers(0, M))
        got = decode_int(subtract(encode(a, cbs, moduli, SB), encode(b, cbs, moduli, SB)),
                         cbs, moduli, SB, M, Mi, yi)
        if got != (a - b) % M:
            return False
    for _ in range(16):
        a = int(rng.integers(0, M))
        got0 = decode_int(subtract(encode(a, cbs, moduli, SB), encode(a, cbs, moduli, SB)),
                          cbs, moduli, SB, M, Mi, yi)
        if got0 != 0:
            return False
    return True


def compare_selftest(moduli, seed: int = 0) -> bool:
    """Formula self-test 3: (a) half-range compare == true 3-way for in-range pairs (|a-b| < M/2); (b)
    decode_then_compare == true 3-way for FULL-range pairs (baseline is range-unrestricted); (c) at least one
    decode-SKIPPING control (native_vector_signtest OR order_blind) DISAGREES with truth on some ordering
    pair (proves the controls are genuinely different mechanisms, not accidental copies)."""
    M, Mi, yi = _crt_setup(moduli)
    cbs = [phasor_codebook(m, SB, 6000 + seed * 10 + i) for i, m in enumerate(moduli)]
    half = M // 2
    rng = np.random.default_rng(31337 + seed)
    skip_disagreed = False
    for _ in range(96):
        a = int(rng.integers(0, half)); b = int(rng.integers(0, half))
        d = decode_int(subtract(encode(a, cbs, moduli, SB), encode(b, cbs, moduli, SB)),
                       cbs, moduli, SB, M, Mi, yi)
        if compare_from_diff(d, M) != true_3way(a, b):
            return False
    for _ in range(96):                                  # baseline exact on FULL range (no M/2 restriction)
        a = int(rng.integers(0, M)); b = int(rng.integers(0, M))
        da = decode_int(encode(a, cbs, moduli, SB), cbs, moduli, SB, M, Mi, yi)
        db = decode_int(encode(b, cbs, moduli, SB), cbs, moduli, SB, M, Mi, yi)
        if true_3way(da, db) != true_3way(a, b):
            return False
        if a != b:
            dvec = subtract(encode(a, cbs, moduli, SB), encode(b, cbs, moduli, SB))
            if native_vector_signtest(dvec, cbs, moduli, SB) != true_3way(a, b):
                skip_disagreed = True
            if compare_order_blind(a, b, moduli) != true_3way(a, b):
                skip_disagreed = True
    return skip_disagreed


# ============================================================
# Arms
# ============================================================


def _digest_arr(arr) -> str:
    return hashlib.sha256(np.ascontiguousarray(np.asarray(arr)).tobytes()).hexdigest()


def _digest_int(int_list) -> str:
    return hashlib.sha256(np.asarray(int_list, dtype=np.int64).tobytes()).hexdigest()


def _cyclic_derangement(r: int):
    return [(i + 1) % r for i in range(r)]   # r=3 -> [1,2,0]


def _make_compare_pairs(M: int, n: int, rng):
    """Balanced 3-way in-range pairs (a,b in [0,M//2)): ~1/3 EQ, ~1/3 GT (a>b), ~1/3 LT (a<b)."""
    half = M // 2
    pairs, labels = [], []
    for i in range(n):
        r = i % 3
        if r == 0:
            a = int(rng.integers(0, half)); b = a
        elif r == 1:
            a = int(rng.integers(1, half)); b = int(rng.integers(0, a))
        else:
            b = int(rng.integers(1, half)); a = int(rng.integers(0, b))
        pairs.append((a, b)); labels.append(true_3way(a, b))
    return pairs, labels


def _make_oor_pairs(M: int, n: int, rng):
    """Out-of-range pairs: a,b in [0,M) with |a-b| >= M//2 (violates the half-range dynamic-range convention)."""
    half = M // 2
    pairs = []
    for _ in range(n):
        while True:
            a = int(rng.integers(0, M)); b = int(rng.integers(0, M))
            if abs(a - b) >= half:
                break
        pairs.append((a, b))
    return pairs


def _make_near_boundary_pairs(M: int, n: int, rng):
    """In-range pairs with |a-b| JUST below M//2 (near-boundary fragility probe)."""
    half = M // 2
    band = max(1, half // 20)
    pairs = []
    for i in range(n):
        delta = int(rng.integers(half - band, half))          # in [half-band, half-1]
        b = int(rng.integers(0, max(1, half - delta)))        # ensures a = b+delta < half
        a = b + delta
        pairs.append((a, b) if i % 2 == 0 else (b, a))        # alternate GT / LT
    return pairs


def run_regime(moduli, seed: int, trials: int, depths):
    """Run all arms for one (moduli-regime, seed). Returns a result dict + artifacts for arms-differ."""
    M, Mi, yi = _crt_setup(moduli)
    half = M // 2
    derange = _cyclic_derangement(R_MODULI)

    cb_phase = [phasor_codebook(m, SB, 6000 + seed * 10 + i) for i, m in enumerate(moduli)]
    cb_rand = [random_phasor_codebook(m, SB, 8000 + seed * 10 + i) for i, m in enumerate(moduli)]

    # ---- SUBTRACT arms A / B / C (paired on same full-range pairs) ----
    rng = np.random.default_rng(90000 + seed + M)
    sub_pairs = [(int(rng.integers(0, M)), int(rng.integers(0, M))) for _ in range(trials)]
    a_hits = b_hits = c_hits = 0
    rec_A, rec_C = [], []
    nm_below_half = 0
    nm_total = 0
    for (a, b) in sub_pairs:
        truth = (a - b) % M
        dvec = subtract(encode(a, cb_phase, moduli, SB), encode(b, cb_phase, moduli, SB))
        res_A, margins = decode_residues(dvec, cb_phase, moduli, SB, want_margin=True)
        tA = _crt(res_A, moduli, M, Mi, yi)
        a_hits += 1 if tA == truth else 0
        rec_A.append(tA)
        for (r1, r2) in margins:
            nm_total += 1
            if r2 <= 0.5 * r1:
                nm_below_half += 1
        dvecB = subtract(encode(a, cb_rand, moduli, SB), encode(b, cb_rand, moduli, SB))
        tB = decode_int(dvecB, cb_rand, moduli, SB, M, Mi, yi)
        b_hits += 1 if tB == truth else 0
        res_C = [res_A[derange[i]] for i in range(R_MODULI)]
        tC = _crt(res_C, moduli, M, Mi, yi)
        c_hits += 1 if tC == truth else 0
        rec_C.append(tC)
    acc_sub = a_hits / trials
    acc_rand = b_hits / trials
    acc_scram = c_hits / trials
    nm_frac = (nm_below_half / nm_total) if nm_total else 0.0

    # ---- additive-inverse identity ----
    inv_rng = np.random.default_rng(60000 + seed + M)
    inv_hits = 0
    n_inv = trials
    for _ in range(n_inv):
        a = int(inv_rng.integers(0, M))
        d0 = decode_int(subtract(encode(a, cb_phase, moduli, SB), encode(a, cb_phase, moduli, SB)),
                        cb_phase, moduli, SB, M, Mi, yi)
        inv_hits += 1 if d0 == 0 else 0
    add_inv = inv_hits / n_inv

    # ---- subtract chain arm (running difference) ----
    chain = {}
    for L in depths:
        c_rng = np.random.default_rng(50000 + seed + M + L)
        hits = 0
        step_ok = 0
        step_total = 0
        n_chain = max(20, trials // 2)
        for _ in range(n_chain):
            terms = [int(c_rng.integers(0, M)) for _ in range(L)]
            running = encode(terms[0], cb_phase, moduli, SB)
            partial = terms[0] % M
            ok_here = (decode_int(running, cb_phase, moduli, SB, M, Mi, yi) == partial)
            step_total += 1
            step_ok += 1 if ok_here else 0
            for k in range(1, L):
                running = subtract(running, encode(terms[k], cb_phase, moduli, SB))
                partial = (partial - terms[k]) % M
                dec = decode_int(running, cb_phase, moduli, SB, M, Mi, yi)
                step_total += 1
                step_ok += 1 if dec == partial else 0
            final = decode_int(running, cb_phase, moduli, SB, M, Mi, yi)
            truth_chain = (terms[0] - sum(terms[1:])) % M
            hits += 1 if final == truth_chain else 0
        chain[L] = {"exact": round(hits / n_chain, 4),
                    "per_step_ok": round(step_ok / step_total, 4),
                    "n_chain": n_chain}

    # ---- COMPARE arms on balanced in-range pairs (decode_then_compare BASELINE + halfrange + controls) ----
    cmp_rng = np.random.default_rng(70000 + seed + M)
    cmp_pairs, cmp_labels = _make_compare_pairs(M, trials, cmp_rng)
    dc_hits = hr_hits = nv_hits = ob_hits = rnd_hits = 0
    dc_order_hits = hr_order_hits = nv_order_hits = ob_order_hits = order_total = 0
    eq_detect_hits = eq_total = 0
    pred_hr, pred_nv, pred_ob = [], [], []
    for (a, b), lab in zip(cmp_pairs, cmp_labels):
        # BASELINE: decode both operands, compare (full-range exact)
        da = decode_int(encode(a, cb_phase, moduli, SB), cb_phase, moduli, SB, M, Mi, yi)
        db = decode_int(encode(b, cb_phase, moduli, SB), cb_phase, moduli, SB, M, Mi, yi)
        pd = true_3way(da, db)
        dc_hits += 1 if pd == lab else 0
        # residue-native half-range: decode the single difference
        dvec = subtract(encode(a, cb_phase, moduli, SB), encode(b, cb_phase, moduli, SB))
        d = decode_int(dvec, cb_phase, moduli, SB, M, Mi, yi)
        ph = compare_from_diff(d, M)
        pred_hr.append(ph); hr_hits += 1 if ph == lab else 0
        # decode-SKIPPING control: single-channel sign test (prior-negative recheck)
        pn = native_vector_signtest(dvec, cb_phase, moduli, SB)
        pred_nv.append(pn); nv_hits += 1 if pn == lab else 0
        # decode-SKIPPING control: raw residue lexicographic
        po = compare_order_blind(a, b, moduli)
        pred_ob.append(po); ob_hits += 1 if po == lab else 0
        # random-codebook half-range (garbage decode)
        dvecR = subtract(encode(a, cb_rand, moduli, SB), encode(b, cb_rand, moduli, SB))
        rnd_hits += 1 if compare_from_diff(decode_int(dvecR, cb_rand, moduli, SB, M, Mi, yi), M) == lab else 0
        if lab != 0:
            order_total += 1
            dc_order_hits += 1 if pd == lab else 0
            hr_order_hits += 1 if ph == lab else 0
            nv_order_hits += 1 if pn == lab else 0
            ob_order_hits += 1 if po == lab else 0
        else:
            eq_total += 1
            eq_detect_hits += 1 if pd == 0 else 0
    dc_3way = dc_hits / trials
    hr_3way = hr_hits / trials
    nv_3way = nv_hits / trials
    ob_3way = ob_hits / trials
    rnd_3way = rnd_hits / trials
    dc_order = (dc_order_hits / order_total) if order_total else float("nan")
    hr_order = (hr_order_hits / order_total) if order_total else float("nan")
    nv_order = (nv_order_hits / order_total) if order_total else float("nan")
    ob_order = (ob_order_hits / order_total) if order_total else float("nan")
    eq_detect = (eq_detect_hits / eq_total) if eq_total else float("nan")
    halfrange_lift = hr_3way - dc_3way

    # ---- out-of-range arm (REPORTED limitation): halfrange mis-signs; baseline stays exact ----
    oor_rng = np.random.default_rng(80000 + seed + M)
    oor_pairs = _make_oor_pairs(M, max(20, trials // 2), oor_rng)
    oor_hr_miss = 0
    oor_dc_hits = 0
    for (a, b) in oor_pairs:
        truth = true_3way(a, b)
        d = decode_int(subtract(encode(a, cb_phase, moduli, SB), encode(b, cb_phase, moduli, SB)),
                       cb_phase, moduli, SB, M, Mi, yi)
        if compare_from_diff(d, M) != truth:
            oor_hr_miss += 1
        da = decode_int(encode(a, cb_phase, moduli, SB), cb_phase, moduli, SB, M, Mi, yi)
        db = decode_int(encode(b, cb_phase, moduli, SB), cb_phase, moduli, SB, M, Mi, yi)
        if true_3way(da, db) == truth:
            oor_dc_hits += 1
    oor_hr_missign = oor_hr_miss / len(oor_pairs)
    oor_dc_acc = oor_dc_hits / len(oor_pairs)

    # ---- near-boundary fragility probe (half-range) ----
    nb_rng = np.random.default_rng(85000 + seed + M)
    nb_pairs = _make_near_boundary_pairs(M, max(20, trials // 2), nb_rng)
    nb_hits = 0
    for (a, b) in nb_pairs:
        d = decode_int(subtract(encode(a, cb_phase, moduli, SB), encode(b, cb_phase, moduli, SB)),
                       cb_phase, moduli, SB, M, Mi, yi)
        nb_hits += 1 if compare_from_diff(d, M) == true_3way(a, b) else 0
    nb_acc = nb_hits / len(nb_pairs)

    # ---- threshold-entailment arm (self-VET target: does value >= threshold hold) ----
    th_rng = np.random.default_rng(95000 + seed + M)
    n_th = max(20, trials // 2)
    th_hits = 0
    for _ in range(n_th):
        val = int(th_rng.integers(0, half)); thr = int(th_rng.integers(0, half))
        truth_ge = (val >= thr)
        da = decode_int(encode(val, cb_phase, moduli, SB), cb_phase, moduli, SB, M, Mi, yi)
        db = decode_int(encode(thr, cb_phase, moduli, SB), cb_phase, moduli, SB, M, Mi, yi)
        pred_ge = (true_3way(da, db) >= 0)
        th_hits += 1 if pred_ge == truth_ge else 0
    thresh_acc = th_hits / n_th

    # ---- readable demos ----
    sub_demos, cmp_demos, thr_demos = [], [], []
    if moduli == REGIMES["small"]:
        for (a, b) in DEMO_SUB:
            got = decode_int(subtract(encode(a, cb_phase, moduli, SB), encode(b, cb_phase, moduli, SB)),
                             cb_phase, moduli, SB, M, Mi, yi)
            sub_demos.append({"a": a, "b": b, "decoded_diff": got, "expected_mod_M": (a - b) % M,
                              "M": M, "correct": got == (a - b) % M, "wrapped": (a - b) < 0})
        sym = {1: "GT", 0: "EQ", -1: "LT"}
        for (a, b) in DEMO_CMP:
            d = decode_int(subtract(encode(a, cb_phase, moduli, SB), encode(b, cb_phase, moduli, SB)),
                           cb_phase, moduli, SB, M, Mi, yi)
            pred = compare_from_diff(d, M)
            cmp_demos.append({"a": a, "b": b, "pred": sym[pred], "truth": sym[true_3way(a, b)],
                              "correct": pred == true_3way(a, b)})
    if moduli == REGIMES["large"]:
        for (val, thr) in DEMO_THRESH:
            da = decode_int(encode(val, cb_phase, moduli, SB), cb_phase, moduli, SB, M, Mi, yi)
            db = decode_int(encode(thr, cb_phase, moduli, SB), cb_phase, moduli, SB, M, Mi, yi)
            pred_ge = (true_3way(da, db) >= 0)
            thr_demos.append({"metric_x10000": val, "threshold_x10000": thr, "pred_ge": bool(pred_ge),
                              "truth_ge": bool(val >= thr), "correct": bool(pred_ge) == bool(val >= thr)})

    artifacts = {
        "cb_phase0": _digest_arr(cb_phase[0]),
        "cb_rand0": _digest_arr(cb_rand[0]),
        "rec_A": _digest_int(rec_A),
        "rec_C": _digest_int(rec_C),
        "pred_hr": _digest_int(pred_hr),
        "pred_nv": _digest_int(pred_nv),
        "pred_ob": _digest_int(pred_ob),
    }
    return {
        "M": M, "half": half, "moduli": list(moduli),
        "acc_sub": round(acc_sub, 4), "acc_rand": round(acc_rand, 4), "acc_scram": round(acc_scram, 4),
        "add_inv": round(add_inv, 4),
        "nearmiss_frac_below_half": round(nm_frac, 4),
        "chain": chain,
        "dc_3way": round(dc_3way, 4), "dc_order": round(dc_order, 4),
        "hr_3way": round(hr_3way, 4), "hr_order": round(hr_order, 4), "halfrange_lift": round(halfrange_lift, 4),
        "nv_3way": round(nv_3way, 4), "nv_order": round(nv_order, 4),
        "ob_3way": round(ob_3way, 4), "ob_order": round(ob_order, 4),
        "rnd_3way": round(rnd_3way, 4),
        "eq_detect": round(eq_detect, 4),
        "oor_hr_missign": round(oor_hr_missign, 4), "oor_dc_acc": round(oor_dc_acc, 4), "n_oor": len(oor_pairs),
        "near_boundary_acc": round(nb_acc, 4), "n_near_boundary": len(nb_pairs),
        "thresh_entail_acc": round(thresh_acc, 4), "n_thresh": n_th,
        "sub_demos": sub_demos, "cmp_demos": cmp_demos, "thr_demos": thr_demos,
    }, artifacts


# ============================================================
# Config + driver
# ============================================================


def get_config(mode: str):
    if mode == "selftest":
        return {"regimes": ["small"], "trials": 12, "seeds": (7,), "depths": (1, 3)}
    if mode == "smoke":
        return {"regimes": ["small", "mid", "large"], "trials": 60, "seeds": SEEDS, "depths": (1, 3, 5)}
    return {"regimes": ["small", "mid", "large"], "trials": 300, "seeds": SEEDS, "depths": DEPTHS_FULL}


def expected_units(cfg) -> int:
    # per (regime, seed): 4 subtract (sub_phase/random/scram/add_inv) + n_depths chain
    #   + 6 compare (decode_then_compare/halfrange/native_signtest/order_blind/random/eq_detect)
    #   + 3 reported (out_of_range/near_boundary/threshold_entailment)
    per = 4 + len(cfg["depths"]) + 6 + 3
    return len(cfg["regimes"]) * len(cfg["seeds"]) * per


def run_all(mode: str, output_dir: Path, t0: float):
    cfg = get_config(mode)
    regimes, trials, seeds, depths = cfg["regimes"], cfg["trials"], cfg["seeds"], cfg["depths"]
    results = {}
    artifacts = {}
    per_unit = []
    unit = 0
    for reg in regimes:
        moduli = REGIMES[reg]
        results[reg] = {}
        for seed in seeds:
            rr, art = run_regime(moduli, seed, trials, depths)
            results[reg][seed] = rr
            artifacts[f"{reg}_{seed}"] = art
            per_unit.append({"regime": reg, "arm": "sub_phase", "seed": seed, "value": rr["acc_sub"]})
            per_unit.append({"regime": reg, "arm": "sub_random", "seed": seed, "value": rr["acc_rand"]})
            per_unit.append({"regime": reg, "arm": "sub_scram", "seed": seed, "value": rr["acc_scram"]})
            per_unit.append({"regime": reg, "arm": "add_inverse_id", "seed": seed, "value": rr["add_inv"]})
            for L, cd in rr["chain"].items():
                per_unit.append({"regime": reg, "arm": "sub_chain", "depth": L, "seed": seed, "value": cd["exact"]})
            per_unit.append({"regime": reg, "arm": "decode_then_compare", "seed": seed,
                             "value": rr["dc_3way"], "order_acc": rr["dc_order"]})
            per_unit.append({"regime": reg, "arm": "compare_halfrange", "seed": seed,
                             "value": rr["hr_3way"], "order_acc": rr["hr_order"], "lift_over_baseline": rr["halfrange_lift"]})
            per_unit.append({"regime": reg, "arm": "native_vector_signtest", "seed": seed,
                             "value": rr["nv_3way"], "order_acc": rr["nv_order"]})
            per_unit.append({"regime": reg, "arm": "compare_order_blind", "seed": seed,
                             "value": rr["ob_3way"], "order_acc": rr["ob_order"]})
            per_unit.append({"regime": reg, "arm": "compare_random", "seed": seed, "value": rr["rnd_3way"]})
            per_unit.append({"regime": reg, "arm": "eq_detect", "seed": seed, "value": rr["eq_detect"]})
            per_unit.append({"regime": reg, "arm": "compare_out_of_range", "seed": seed,
                             "value": rr["oor_hr_missign"], "baseline_acc": rr["oor_dc_acc"]})
            per_unit.append({"regime": reg, "arm": "compare_near_boundary", "seed": seed,
                             "value": rr["near_boundary_acc"]})
            per_unit.append({"regime": reg, "arm": "threshold_entailment", "seed": seed,
                             "value": rr["thresh_entail_acc"]})
            unit += 1
            _heartbeat(output_dir, unit, len(regimes) * len(seeds), t0,
                       extra={"regime": reg, "seed": seed, "M": rr["M"],
                              "acc_sub": rr["acc_sub"], "dc_3way": rr["dc_3way"], "hr_3way": rr["hr_3way"],
                              "hr_order": rr["hr_order"], "nv_order": rr["nv_order"], "ob_order": rr["ob_order"]})
            chain_str = " ".join(f"d{L}:{cd['exact']:.3f}" for L, cd in rr["chain"].items())
            _say(f"  [seed {seed}] regime={reg} moduli={moduli} M={rr['M']} half={rr['half']}: "
                 f"sub={rr['acc_sub']:.3f} rand={rr['acc_rand']:.3f} scram={rr['acc_scram']:.3f} "
                 f"inv={rr['add_inv']:.3f} | chain[{chain_str}] | "
                 f"decode_cmp={rr['dc_3way']:.3f}(ord {rr['dc_order']:.3f}) "
                 f"halfrange={rr['hr_3way']:.3f}(ord {rr['hr_order']:.3f} lift {rr['halfrange_lift']:+.3f}) "
                 f"native_sign_ord={rr['nv_order']:.3f} order_blind_ord={rr['ob_order']:.3f} "
                 f"eq={rr['eq_detect']:.3f} thr={rr['thresh_entail_acc']:.3f} | "
                 f"oor[hr_miss={rr['oor_hr_missign']:.3f} baseline={rr['oor_dc_acc']:.3f}] "
                 f"near_bound={rr['near_boundary_acc']:.3f} nm_frac={rr['nearmiss_frac_below_half']:.3f}")
    return cfg, results, artifacts, per_unit


# ============================================================
# Classify
# ============================================================


def _mean(vals):
    return float(np.mean(vals)) if vals else float("nan")


def _cv(vals):
    if not vals:
        return float("nan")
    m = float(np.mean(vals))
    if m == 0.0:
        return 0.0 if float(np.std(vals)) == 0.0 else float("inf")
    return float(np.std(vals)) / m


def classify(results, cfg, mode: str):
    regimes, seeds, depths = cfg["regimes"], cfg["seeds"], cfg["depths"]
    dmax = max(depths)

    sub_all, rand_all, scram_all, inv_all = [], [], [], []
    sub_cv_per_regime = []
    dc3_all, dc_order_all, hr3_all, hr_order_all, lift_abs_all = [], [], [], [], []
    nv_order_all, ob_order_all, eq_all, nb_all, th_all = [], [], [], [], []
    chain_d3_all, chain_dmax_all = [], []
    for reg in regimes:
        sub_reg = [results[reg][s]["acc_sub"] for s in seeds]
        sub_all.extend(sub_reg); sub_cv_per_regime.append(_cv(sub_reg))
        rand_all.extend([results[reg][s]["acc_rand"] for s in seeds])
        scram_all.extend([results[reg][s]["acc_scram"] for s in seeds])
        inv_all.extend([results[reg][s]["add_inv"] for s in seeds])
        dc3_all.extend([results[reg][s]["dc_3way"] for s in seeds])
        dc_order_all.extend([results[reg][s]["dc_order"] for s in seeds])
        hr3_all.extend([results[reg][s]["hr_3way"] for s in seeds])
        hr_order_all.extend([results[reg][s]["hr_order"] for s in seeds])
        lift_abs_all.extend([abs(results[reg][s]["halfrange_lift"]) for s in seeds])
        nv_order_all.extend([results[reg][s]["nv_order"] for s in seeds])
        ob_order_all.extend([results[reg][s]["ob_order"] for s in seeds])
        eq_all.extend([results[reg][s]["eq_detect"] for s in seeds])
        nb_all.extend([results[reg][s]["near_boundary_acc"] for s in seeds])
        th_all.extend([results[reg][s]["thresh_entail_acc"] for s in seeds])
        for s in seeds:
            ch = results[reg][s]["chain"]
            if 3 in ch:
                chain_d3_all.append(ch[3]["exact"])
            chain_dmax_all.append(ch[dmax]["exact"])

    sub_min = min(sub_all); sub_mean = _mean(sub_all); sub_cv_max = max(sub_cv_per_regime)
    rand_max = max(rand_all); scram_max = max(scram_all); inv_min = min(inv_all)
    dc3_min = min(dc3_all); dc_order_min = min(dc_order_all)
    hr3_min = min(hr3_all); hr_order_min = min(hr_order_all); lift_abs_max = max(lift_abs_all)
    skip_order_max = max(nv_order_all + ob_order_all)
    eq_min = min(eq_all); nb_min = min(nb_all); th_min = min(th_all)
    d3_min = min(chain_d3_all) if chain_d3_all else float("nan")
    dmax_min = min(chain_dmax_all)
    decode_order_min = min(dc_order_min, hr_order_min)
    order_gap = decode_order_min - skip_order_max

    diag = (f"sub[min={sub_min:.3f} mean={sub_mean:.3f} cv_max={sub_cv_max:.3f}] "
            f"rand[max={rand_max:.3f}] scram[max={scram_max:.3f}] inv[min={inv_min:.3f}] "
            f"decode_cmp[3way_min={dc3_min:.3f} ord_min={dc_order_min:.3f}] "
            f"halfrange[3way_min={hr3_min:.3f} ord_min={hr_order_min:.3f} |lift|_max={lift_abs_max:.3f}] "
            f"decode_SKIP[ord_max={skip_order_max:.3f}] order_gap={order_gap:.3f} "
            f"eq[min={eq_min:.3f}] thr[min={th_min:.3f}] near_bound[min={nb_min:.3f}] "
            f"chain[d3_min={d3_min:.3f} d{dmax}_min={dmax_min:.3f}]")

    # --- discriminator-fires / control gates (ALL modes incl smoke) ---
    if not (sub_min >= HP_SUB_EXACT):
        if sub_min < HF_SUB:
            return ("HARD_FAIL",
                    f"SUBTRACT FAILED: exact-subtract min={sub_min:.3f} < {HF_SUB}. Conjugate additive-inverse "
                    f"does not transfer at substrate scale. {diag}", False)
        return ("DISCRIMINATOR_DID_NOT_FIRE",
                f"sub_phase did not reach exact floor (min={sub_min:.3f} < {HP_SUB_EXACT}); investigate. {diag}", False)
    if not (dc3_min >= HF_COMPARE):
        return ("HARD_FAIL",
                f"BASELINE COMPARE FAILED: decode_then_compare 3-way min={dc3_min:.3f} < {HF_COMPARE}. Exact CRT "
                f"decode does not transfer -> deep breakage (this baseline should be ~1.0). {diag}", False)
    if not (rand_max <= B_CTRL_MAX):
        return ("CONTROL_DID_NOT_COLLAPSE",
                f"random-codebook subtract did NOT fail (max={rand_max:.3f} > {B_CTRL_MAX}): phase-linearity is "
                f"not load-bearing OR leak (verify-the-referent). {diag}", False)
    if not (scram_max <= C_SCRAM_MAX):
        return ("CONTROL_DID_NOT_COLLAPSE",
                f"scrambled-modulus subtract did NOT collapse (max={scram_max:.3f} > {C_SCRAM_MAX}). {diag}", False)
    if not (skip_order_max <= DECODESKIP_ORDER_MAX):
        return ("CONTROL_DID_NOT_COLLAPSE",
                f"decode-SKIPPING ORDERING did NOT collapse (native_signtest/order_blind ord_max={skip_order_max:.3f} "
                f"> {DECODESKIP_ORDER_MAX}): single-channel/raw-residue order should be ~chance 0.5; if not, residues "
                f"leak order OR the decode is not actually load-bearing for comparison. {diag}", False)

    if mode == "smoke":
        return ("HARD_PASS",
                f"SMOKE_MACHINERY_OK: sub_phase EXACT (min={sub_min:.3f}) at ALL 3 regimes and full N={N_DIM}; "
                f"random-subtract FAILS (max={rand_max:.3f}); scram collapses ({scram_max:.3f}); add-inverse holds "
                f"({inv_min:.3f}). COMPARE: decode_then_compare BASELINE exact (3way_min={dc3_min:.3f}); half-range "
                f"MATCHES baseline (3way_min={hr3_min:.3f}, |lift|_max={lift_abs_max:.3f}) -> adds NO accuracy; "
                f"decode-SKIPPING native/order-blind ORDERING collapses to chance (max={skip_order_max:.3f}, "
                f"order_gap={order_gap:.3f}) -> decode is load-bearing. eq={eq_min:.3f} thr_entail={th_min:.3f} "
                f"near_bound={nb_min:.3f} chain_d3={d3_min:.3f}. Deliverable band FULL-only (canonical=remote). {diag}",
                True)

    # --- FULL pre-registered bands ---
    if rand_max >= B_LEAK:
        return ("HARD_FAIL",
                f"RANDOM_CODEBOOK LEAK: subtract control max={rand_max:.3f} >= {B_LEAK}. {diag}", True)
    passes = (sub_min >= HP_SUB_EXACT and sub_cv_max < HP_CV and rand_max <= B_CTRL_MAX
              and scram_max <= C_SCRAM_MAX and inv_min >= HP_ADD_INV
              and dc3_min >= HP_COMPARE_3WAY and dc_order_min >= HP_ORDER_ACC
              and hr3_min >= HP_HALFRANGE_3WAY and hr_order_min >= HP_ORDER_ACC
              and skip_order_max <= DECODESKIP_ORDER_MAX and eq_min >= HP_EQ_DETECT
              and th_min >= HP_THRESH_ENTAIL and d3_min >= HP_CHAIN_D3)
    if passes:
        return ("HARD_PASS",
                f"MATH EXTENDS (honest): conjugate-phasor SUBTRACTION exact (min={sub_min:.3f}, cv<{HP_CV}) across "
                f"M in [504,70520] incl wraparound; random-subtract fails ({rand_max:.3f}); scram collapses "
                f"({scram_max:.3f}); add-inverse exact ({inv_min:.3f}); {dmax}-step subtract chains hold "
                f"(d3_min={d3_min:.3f}). COMPARE is SOLVED by decode_then_compare (exact CRT decode -> 3way_min="
                f"{dc3_min:.3f}, ordering_min={dc_order_min:.3f}, FULL-range, no M/2 caveat). Half-range sign "
                f"detection MATCHES the baseline within |a-b|<M/2 (3way_min={hr3_min:.3f}, |lift|_max={lift_abs_max:.3f}"
                f") -> adds NO accuracy, only saves one decode, and is strictly worse out-of-range. Decode-SKIPPING "
                f"comparators reproduce the prior HARD_FAIL negative (native_signtest/order_blind ordering "
                f"max={skip_order_max:.3f}, gap={order_gap:.3f}) -> the decode is load-bearing. EQ-detect "
                f"({eq_min:.3f}); a>=threshold entailment ({th_min:.3f}); near-boundary exact ({nb_min:.3f}). "
                f"DESIGN FINDING: exact decode makes numeric-threshold compare trivial via decode-then-compare; no "
                f"new residue-native comparison mechanism needed for correctness. {diag}", True)
    if d3_min < HF_CHAIN_D3:
        return ("HARD_FAIL",
                f"CHAINS DRIFT: depth-3 subtract-chain min={d3_min:.3f} < {HF_CHAIN_D3}. {diag}", True)
    return ("MIDDLE_BAND",
            f"partial: subtract + decode_then_compare exact but a secondary band missed (hr3_min={hr3_min:.3f}, "
            f"hr_order_min={hr_order_min:.3f}, eq_min={eq_min:.3f}, thr_min={th_min:.3f}, near_bound_min={nb_min:.3f}, "
            f"chain d3_min={d3_min:.3f}, sub_cv_max={sub_cv_max:.3f}). {diag}", True)


# ============================================================
# main
# ============================================================


def _run(mode: str) -> int:
    output_dir = _out_dir()
    output_dir.mkdir(parents=True, exist_ok=True)
    t0 = time.perf_counter()
    cfg = get_config(mode)
    exp = expected_units(cfg)
    _write_start_marker(output_dir, mode, exp)
    _say(f"[{ANCHOR_NAME}] mode={mode} N={N_DIM} R={R_MODULI} sb={SB} regimes={cfg['regimes']} "
         f"seeds={cfg['seeds']} trials={cfg['trials']} depths={cfg['depths']} expected_units={exp}")

    # formula self-tests (ALL modes): CRT + subtract homomorphism + compare correctness, per regime in play.
    for reg in cfg["regimes"]:
        moduli = REGIMES[reg]
        if not crt_selftest(moduli):
            raise AssertionError(f"CRT_SELFTEST_FAIL regime={reg} moduli={moduli}")
        if not subtract_homomorphism_selftest(moduli, seed=cfg["seeds"][0]):
            raise AssertionError(f"SUBTRACT_HOMOMORPHISM_SELFTEST_FAIL regime={reg} moduli={moduli} "
                                 f"(decode(subtract(enc(a),enc(b))) != (a-b) mod M, or add-inverse != 0)")
        if not compare_selftest(moduli, seed=cfg["seeds"][0]):
            raise AssertionError(f"COMPARE_SELFTEST_FAIL regime={reg} moduli={moduli} "
                                 f"(half-range or decode_then_compare != true 3-way, or decode-skip control not divergent)")
    _say(f"[{ANCHOR_NAME}] formula self-tests PASSED (CRT + subtract-homomorphism + compare) for {cfg['regimes']}")

    cfg, results, artifacts, per_unit = run_all(mode, output_dir, t0)

    # arms_differ (META_RULE_AF). EXEMPT: decode_then_compare vs compare_halfrange (both exact -> identical
    # correct labels by construction; that identity is the honesty finding). We hash codebooks + recovered
    # integers + decode-SKIPPING control predictions, which genuinely differ.
    arms_differ_ok = True
    reasons = []
    for key, art in artifacts.items():
        if art["cb_phase0"] == art["cb_rand0"]:
            arms_differ_ok = False; reasons.append(f"{key}:phase==random codebook")
        if art["rec_A"] == art["rec_C"]:
            arms_differ_ok = False; reasons.append(f"{key}:scramble did not alter recovered integers")
        if art["pred_hr"] == art["pred_nv"]:
            arms_differ_ok = False; reasons.append(f"{key}:halfrange==native_signtest predictions (control not distinct)")
        if art["pred_hr"] == art["pred_ob"]:
            arms_differ_ok = False; reasons.append(f"{key}:halfrange==order_blind predictions (control not distinct)")
    if not arms_differ_ok:
        raise AssertionError("META_RULE_AF VIOLATION: " + "; ".join(reasons))

    verdict, vmsg, controls_ok = classify(results, cfg, mode)
    elapsed = time.perf_counter() - t0

    arm_summ = {}
    for reg in cfg["regimes"]:
        seeds = cfg["seeds"]
        def col(key):
            return [results[reg][s][key] for s in seeds]
        chain_summ = {}
        for L in cfg["depths"]:
            ex = [results[reg][s]["chain"][L]["exact"] for s in seeds]
            st = [results[reg][s]["chain"][L]["per_step_ok"] for s in seeds]
            chain_summ[f"d{L}"] = {"exact_mean": round(_mean(ex), 4), "exact_per_seed": ex,
                                   "per_step_ok_mean": round(_mean(st), 4)}
        arm_summ[reg] = {
            "M": results[reg][seeds[0]]["M"], "half": results[reg][seeds[0]]["half"],
            "moduli": results[reg][seeds[0]]["moduli"],
            "sub_phase": {"exact_mean": round(_mean(col("acc_sub")), 4), "per_seed": col("acc_sub"),
                          "cv": round(_cv(col("acc_sub")), 4)},
            "sub_random": {"exact_mean": round(_mean(col("acc_rand")), 4), "per_seed": col("acc_rand")},
            "sub_scram": {"exact_mean": round(_mean(col("acc_scram")), 4), "per_seed": col("acc_scram")},
            "add_inverse_id": {"exact_mean": round(_mean(col("add_inv")), 4), "per_seed": col("add_inv")},
            "chain": chain_summ,
            "decode_then_compare": {"three_way_mean": round(_mean(col("dc_3way")), 4),
                                    "three_way_per_seed": col("dc_3way"),
                                    "order_acc_mean": round(_mean(col("dc_order")), 4),
                                    "note": "STRONG BASELINE / mechanism-of-record: exact, full-range, no M/2 caveat"},
            "compare_halfrange": {"three_way_mean": round(_mean(col("hr_3way")), 4),
                                  "three_way_per_seed": col("hr_3way"),
                                  "order_acc_mean": round(_mean(col("hr_order")), 4),
                                  "lift_over_baseline_mean": round(_mean(col("halfrange_lift")), 4),
                                  "note": "residue-native; MATCHES baseline in-range (lift~0), worse out-of-range"},
            "native_vector_signtest": {"three_way_mean": round(_mean(col("nv_3way")), 4),
                                       "order_acc_mean": round(_mean(col("nv_order")), 4),
                                       "note": "PRIOR-NEGATIVE recheck: single-channel sign, no CRT -> ~chance ordering"},
            "compare_order_blind": {"three_way_mean": round(_mean(col("ob_3way")), 4),
                                    "order_acc_mean": round(_mean(col("ob_order")), 4)},
            "compare_random": {"three_way_mean": round(_mean(col("rnd_3way")), 4)},
            "eq_detect": {"mean": round(_mean(col("eq_detect")), 4), "per_seed": col("eq_detect")},
            "compare_out_of_range": {"halfrange_missign_rate_mean": round(_mean(col("oor_hr_missign")), 4),
                                     "baseline_acc_mean": round(_mean(col("oor_dc_acc")), 4),
                                     "note": "REPORTED limitation: |a-b|>=M/2 -> half-range silently mis-signs; "
                                             "decode_then_compare BASELINE is unaffected (strictly safer)"},
            "compare_near_boundary": {"acc_mean": round(_mean(col("near_boundary_acc")), 4),
                                      "per_seed": col("near_boundary_acc")},
            "threshold_entailment": {"acc_mean": round(_mean(col("thresh_entail_acc")), 4),
                                     "per_seed": col("thresh_entail_acc"),
                                     "note": "self-VET target: does value >= threshold hold (via decode_then_compare)"},
            "nearmiss_frac_below_half_mean": round(_mean(col("nearmiss_frac_below_half")), 4),
        }

    sub_demos = results["small"][cfg["seeds"][0]]["sub_demos"] if "small" in results else []
    cmp_demos = results["small"][cfg["seeds"][0]]["cmp_demos"] if "small" in results else []
    thr_demos = results["large"][cfg["seeds"][0]]["thr_demos"] if "large" in results else []

    metrics = {
        "anchor_name": ANCHOR_NAME,
        "verdict": verdict,
        "verdict_msg": vmsg,
        "summary": f"{verdict}: RNS subtraction + numeric-threshold three-way comparison ({mode})",
        "run_mode": mode,
        "elapsed_s": round(elapsed, 2),
        "n_seeds": len(cfg["seeds"]),
        "n_units": len(per_unit),
        "expected_n_units": exp,
        "cardinality_ok": len(per_unit) >= exp,
        "config": {"N": N_DIM, "R_MODULI": R_MODULI, "SB": SB,
                   "regimes": {r: list(REGIMES[r]) for r in cfg["regimes"]},
                   "seeds": list(cfg["seeds"]), "trials": cfg["trials"], "depths": list(cfg["depths"]),
                   "mechanism": "phase_linear_phasor_FPE_residues",
                   "subtract": "FHRR_conjugate_bind_enc_a_times_conj_enc_b",
                   "compare_baseline": "decode_then_compare_two_CRT_decodes_full_range",
                   "compare_native": "half_range_sign_detection_one_decode_signed_d_vs_M_half",
                   "decode": "per_subblock_phasor_argmax_then_CRT",
                   "storage_strategy": "no_storage_algebraic_bind"},
        "arms": arm_summ,
        "sub_demos": sub_demos,
        "cmp_demos": cmp_demos,
        "thr_demos": thr_demos,
        "per_unit": per_unit,
        "arms_differ_verified": arms_differ_ok,
        "arms_differ_exempted": [["decode_then_compare", "compare_halfrange"]],
        "controls": {"controls_collapsed": controls_ok},
        "prior_negative_recheck": {
            "cited": "data/exp_comparator_resonator_primitive_smoke_v1/metrics.json",
            "cited_result": "FULL HARD_FAIL comp_acc=0.8556 < raw_acc=0.8944 (lift -0.0389)",
            "this_cell_arm": "native_vector_signtest (single-channel sign, discrete rep)",
            "finding": "negative reproduced -> mechanism-general (decode is required), not FPE-specific"},
        "bands": {"HP_sub_exact": HP_SUB_EXACT, "HP_cv": HP_CV, "HF_sub": HF_SUB,
                  "B_ctrl_max": B_CTRL_MAX, "B_leak": B_LEAK, "C_scram_max": C_SCRAM_MAX,
                  "HP_add_inv": HP_ADD_INV, "HP_compare_3way": HP_COMPARE_3WAY,
                  "HP_halfrange_3way": HP_HALFRANGE_3WAY, "HF_compare": HF_COMPARE,
                  "HP_order_acc": HP_ORDER_ACC, "decodeskip_order_max": DECODESKIP_ORDER_MAX,
                  "halfrange_lift_tol": HALFRANGE_LIFT_TOL, "HP_chain_d3": HP_CHAIN_D3, "HF_chain_d3": HF_CHAIN_D3,
                  "HP_eq_detect": HP_EQ_DETECT, "HP_thresh_entail": HP_THRESH_ENTAIL, "nearmiss_frac": NEARMISS_FRAC},
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(),
        "host": platform.node(),
    }
    _write_metrics_atomic(output_dir, metrics)
    written = json.load(open(output_dir / "metrics.json"))
    assert written["run_mode"] == mode, f"RUN_MODE_MISMATCH {written['run_mode']} != {mode}"

    _say(f"\n[{ANCHOR_NAME}] {verdict}: {vmsg}")
    if sub_demos:
        _say(f"[{ANCHOR_NAME}] sub demos: " + "; ".join(
            f"{d['a']}-{d['b']}={d['decoded_diff']}(exp {d['expected_mod_M']}"
            f"{',WRAP' if d['wrapped'] else ''}){'OK' if d['correct'] else 'X'}" for d in sub_demos))
    if cmp_demos:
        _say(f"[{ANCHOR_NAME}] cmp demos: " + "; ".join(
            f"{d['a']}vs{d['b']}={d['pred']}(exp {d['truth']}){'OK' if d['correct'] else 'X'}" for d in cmp_demos))
    if thr_demos:
        _say(f"[{ANCHOR_NAME}] thr demos (metric>=thresh, /10000): " + "; ".join(
            f"{d['metric_x10000']}>={d['threshold_x10000']}?{d['pred_ge']}"
            f"{'OK' if d['correct'] else 'X'}" for d in thr_demos))
    _say(f"[{ANCHOR_NAME}] metrics -> {output_dir / 'metrics.json'}  elapsed={elapsed:.1f}s")
    return 0


def _run_selftest() -> int:
    t0 = time.perf_counter()
    output_dir = _out_dir()
    output_dir.mkdir(parents=True, exist_ok=True)
    ok_crt = all(crt_selftest(REGIMES[r]) for r in REGIMES)
    ok_sub = all(subtract_homomorphism_selftest(REGIMES[r], seed=7) for r in REGIMES)
    ok_cmp = all(compare_selftest(REGIMES[r], seed=7) for r in REGIMES)
    cfg, results, _art, _pu = run_all("selftest", output_dir, t0)
    rr = results["small"][7]
    ok = ok_crt and ok_sub and ok_cmp and (rr["acc_sub"] >= 0.99) and (rr["acc_rand"] <= 0.15) \
        and (rr["acc_scram"] <= 0.05) and (rr["add_inv"] >= 0.99) and (rr["dc_3way"] >= 0.99) \
        and (rr["hr_3way"] >= 0.99) and (rr["dc_order"] >= 0.99) and (max(rr["nv_order"], rr["ob_order"]) <= 0.72)
    _say(f"[{ANCHOR_NAME}] SELFTEST {'PASS' if ok else 'FAIL'}: crt={ok_crt} sub_hom={ok_sub} cmp={ok_cmp} "
         f"sub={rr['acc_sub']:.3f} rand={rr['acc_rand']:.3f} scram={rr['acc_scram']:.3f} inv={rr['add_inv']:.3f} "
         f"decode_cmp={rr['dc_3way']:.3f} halfrange={rr['hr_3way']:.3f}(lift {rr['halfrange_lift']:+.3f}) "
         f"native_sign_ord={rr['nv_order']:.3f} order_blind_ord={rr['ob_order']:.3f} [{time.perf_counter()-t0:.1f}s]")
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
