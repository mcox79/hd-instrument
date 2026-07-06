# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate: phase-linear codebook vs random-phasor codebook hash-distinct;
#     mechanism star-multiply recovered integers vs scrambled-CRT recovered integers hash-distinct;
#     mechanism recovered integers vs bind-not-power (additive) recovered integers hash-distinct.
#     Mechanism/control arms that legitimately share the TRUTH integers (an exact multiplier and a broken
#     multiplier both know the truth) are never hash-compared on truth arrays; we hash the CODEBOOKS and the
#     RECOVERED integer arrays (which DO differ: mechanism recovers a*b, bind recovers a+b, rand_exp recovers
#     a*wrong, scram recovers permuted-CRT).
# - final_metrics_atomicity: tmp_replace (write metrics.json.tmp then os.replace).
# - except SystemExit: raise BEFORE except Exception (no BaseException).
# - crlb/capacity-feasibility: per-residue decode is a phasor argmax over m_i candidates in a sub-block of
#     dim sb=2730 (N=8192, R=3). SNR ~ sqrt(sb) rank-1 vs ~1/sqrt(sb) runner-up; sb=2730 >> max modulus 43,
#     so per-residue argmax is collision-free (rank-1 == 1.0, runner-up ~ 0.019). Exponentiating a unit phasor
#     by an integer <= m_i-1 <= 42 stays exactly unit-modulus (z^n = exp(i*n*theta), period-m periodicity), so
#     no superposition/precision floor gates the 0.99 exact-multiply target. discriminator_reachability=True.
#     crlb_n_a is NOT claimed: the reachability argument IS the capacity-feasibility analysis.
# - baseline_in_band (META_RULE_AG): there is NO difficulty-baseline that must sit in (0.05,0.95). This is an
#     EXACTNESS/CORRECTNESS test, not a difficulty sweep. mechanism arm is expected ~1.0 by exact residue-
#     multiply construction; the 4 controls (bind_not_power / random_exponent / random_codebook /
#     scrambled_modulus) are intentionally ~0.0 -> exempt from the in-band rule (declared controls, same
#     carve-out as the landed add cell exp_math_rns_add_chain_v1). The discriminator is the CONTRAST
#     mechanism(~1.0) vs controls(~0.0), which does NOT saturate at scale (controls fall toward 1/M as M grows).
# - discriminator survives scale: smoke runs at FULL N=8192, FULL sub-block dim sb=2730, and ALL 4 moduli
#     regimes (3 all-prime + 1 all-composite). Smoke reduces trials/seeds/chain-depths ONLY, never N/sb/moduli.
#     mechanism-exact + all-4-controls-collapse + chain-exact + equality-crisp all FIRE in smoke (option A of
#     DISCRIMINATOR-MUST-SURVIVE-SCALE: smoke at full-N parameters).
# - HARD_PASS strictly above floor: mechanism exact-multiply HP floor 0.99 (HF=0.60); MEASURED expectation
#     ~1.0 (exact residue multiply, collision-free decode). Contrast/gap mechanism-vs-control ~1.0 is the real
#     discriminator.
# - all numbers in comments tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@.
#
# MATH CAPABILITY -- RNS PHASE-LINEAR MULTIPLICATION via the STAR OPERATOR (decode-then-exponentiate)  v1
# ======================================================================================================
# THIRD real math-capability cell. Completes the arithmetic primitive set alongside the landed
# exp_math_rns_add_chain_v1 (FULL HARD_PASS exact-add=1.000
# MEASURED@data/exp_math_rns_add_chain_v1/metrics.json:arms.small.phase_linear_add.exact_mean) and
# exp_math_rns_subtract_compare_v1 (FULL HARD_PASS
# MEASURED@data/exp_math_rns_subtract_compare_v1/metrics.json:verdict). Multiply completes {+, -, x, compare}
# calculator-class arithmetic; it is core-mathematics-vision, NOT on the self-reasoning critical path
# (add+compare already cover numeric-threshold logic). Reuses the add cell's phase-linear phasor encoding +
# CRT decode VERBATIM.
#   CITED@notes/research_math_arithmetic_basis_next_primitives_2026-07-05.md (Q1 mechanism sketch + bands)
#
# MECHANISM -- the STAR operator (CITED@Kymn/Kleyko/Frady/Bybee/Kanerva/Sommer/Olshausen 2024, Neural
# Computation, arXiv:2311.04872 -- the substrate's own primary VSA reference; the 'star'/multiply operator):
#   codebook_m[r,j] = exp(i*2*pi*k_j*r/m), k_j integer in [1,m-1]. The per-dim base is w_j = exp(i*2*pi*k_j/m),
#   so codebook_m[r] = w^r (elementwise). Because the integer lives in the EXPONENT (not as a log), addition
#   is free (w^a . w^b = w^(a+b)); multiplication is the MIRROR-image cost -- decode ONE operand back to a
#   concrete residue, then EXPONENTIATE the other operand's phasor by it:
#       codebook_m[a] ** b  ==  w^(a*b)  ==  codebook_m[(a*b) mod m]     [period-m periodicity: k_j integer]
#   Full integer x is split into R=3 disjoint sub-blocks (x mod m_i). Star-multiply per sub-block i:
#   decode b's residue (b mod m_i) via per-sub-block argmax, raise sub-block i of enc(a) to that integer power,
#   then per-sub-block argmax + CRT decode the result to (a*b) mod M. NO resonator, NO new decode topology
#   (glass-box per-sub-block argmax, same as the landed add/rns_crt cells; only the elementwise integer-power
#   is new vs the add cell's elementwise-product bind).
#
# PRIME-NECESSITY FINDING (HONEST, MEASURED -- inverts the drill's prediction 3):
#   The drill (research_math_arithmetic..._2026-07-05.md) HYPOTHESIZED@ that the star operator "requires moduli
#   restricted to PRIMES" and pre-registered a composite-modulus control that "collapses to <=0.15", with
#   non-collapse framed as evidence "the prime-cyclicity requirement is not actually load-bearing at substrate
#   scale." A pre-dispatch numerical probe MEASURED that decode-then-exponentiate multiply is EXACT (1.000) for
#   composite moduli (8,9,25) exactly as for prime moduli. The prime requirement is a property of the
#   drill's REJECTED discrete-log/index-calculus route (which needs a cyclic multiplicative group), NOT of
#   decode-then-exponentiate, which is exact for ANY pairwise-coprime moduli. This cell therefore reports the
#   composite regime as a PRIME-NECESSITY PROBE (an honest negative-control that did NOT fire) rather than a
#   pass-gated must-collapse arm. Primary HARD_PASS is on the 3 all-prime regimes (per the drill's convention);
#   the composite regime documents prime-independence. (THEORETICAL: w^(a*b)=codebook[(a*b) mod m] for any m
#   with integer k_j; primes only matter when representing residues by discrete logs, not here.)
#
# ARMS (all PAIRED on the same (a,b) integer pairs per regime/seed):
#   star_multiply       : MECHANISM -- decode b, exponentiate enc(a) sub-blocks by b's residues, argmax+CRT.
#                         Expected exact-multiply ~1.0.                                           [MECHANISM]
#   bind_not_power      : CONTROL -- use the free-add bind (enc(a) . enc(b) = enc((a+b) mod M)) and CLAIM it is
#                         the product. Decodes to (a+b), not (a*b). Isolates that EXPONENTIATION (not bind) is
#                         the multiply operator -- the load-bearing half of decode-then-exponentiate. ~0.0. [CONTROL]
#   random_exponent     : CONTROL -- exponentiate enc(a) by a RANDOM wrong residue instead of the decoded b.
#                         Isolates the DECODE half of decode-then-exponentiate (b must be decoded correctly). ~0.0.
#   random_codebook     : CONTROL -- IDENTICAL star pipeline on RANDOM (non-phase-linear) phasors -> no
#                         homomorphism -> exponentiation is unrelated to codebook[(a*b) mod m]. Isolates
#                         phase-LINEARITY. ~0.0.                                                   [CONTROL]
#   scrambled_modulus   : CONTROL -- mechanism decode then DERANGE residues before CRT. CRT load-bearing. ~0.0.
#   mult_chain_dL       : mechanism over an L-step running-PRODUCT chain (running ** decoded next term), for
#                         depths L in {1,3,5,10}. Residue-exact so no drift EXPECTED (chains do not accumulate
#                         encoding noise; decode noise is per-number not cumulative). MEASURED exact at L<=5.
#   equality_check      : the SELF-REASONING primitive -- decode(a*b) EXACTLY == claimed product (discrete
#                         True/False, NOT fuzzy cosine). accept-correct + reject-incorrect crispness.
#
# COMPOSITE regime runs the FULL arm set too (mechanism + all 4 controls + chain + equality): shows the
# controls collapse for composite as well, and the mechanism is exact -> prime-independence is clean.
#
# is-math-easier PROBE (near-miss margin): for mechanism decode, runner-up residue similarity vs rank-1.
# Reported, not hard-gated (same as add cell).
#
# Brain-grounding (CITED@): entorhinal grid cells ARE a residue-number-system (Sreenivasan & Fiete 2011,
# Nat. Neurosci.); abstract-magnitude grid codes (Constantinescu/O'Reilly/Behrens 2016, Science). Literal
# mechanism reuse -- multiply extends the same grid-like RNS code from addressing/addition to product.
#
# ASCII-only. CPU default (numpy complex64; no GPU, no LLM; wall < 90s total -> sequential-CPU justified).
# Self-contained (synthetic phasor codebooks; no pool/re-encode dependency).
# Run: python experiments/exp_math_rns_multiply_star_v1.py [--self-test | --smoke]
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

ANCHOR_NAME = "math_rns_multiply_star_v1"
REPO = Path(__file__).resolve().parents[1]

N_DIM = 8192          # substrate compositional default (== landed add / rns_crt cells); never reduced
R_MODULI = 3          # residues per integer (disjoint sub-blocks)
SB = N_DIM // R_MODULI  # 2730 dims per sub-block; sb >> max modulus 43 -> collision-free phasor decode

# Four moduli regimes. PRIME_REGIMES: 3 all-prime triples (drill convention for the star operator). The star
# operator (decode-then-exponentiate) does NOT actually require primes; the composite regime is a PRIME-
# NECESSITY PROBE (reported finding, not a pass gate). Each set pairwise-coprime (asserted); M = prod.
REGIMES = {
    "prime_small": (5, 7, 11),     # M=385     (all prime)
    "prime_mid":   (13, 17, 19),   # M=4199    (all prime)
    "prime_large": (37, 41, 43),   # M=65231   (all prime; max modulus 43 << sb=2730)
    "composite":   (8, 9, 25),     # M=1800    (all composite, pairwise coprime) -- prime-necessity probe
}
PRIME_REGIMES = ["prime_small", "prime_mid", "prime_large"]
COMPOSITE_REGIMES = ["composite"]
SEEDS = (7, 13, 19)
DEPTHS_FULL = (1, 3, 5, 10)

# Readable multiply examples reported verbatim (prime_small regime, M=385): (a, b). #3,#5 wrap mod 385.
DEMO_PAIRS = [(3, 4), (7, 11), (20, 20), (50, 50), (100, 100)]

# ---- Pre-registered bands (HYPOTHESIZED from exact-residue-multiply theory; MEASURED filled by smoke) ----
HP_MULT_EXACT = 0.99   # HARD_PASS: mechanism exact-multiply floor (THEORETICAL ~1.0; residue multiply exact)
HP_CV = 0.10           # HARD_PASS: cross-seed cv of mechanism exact-multiply (THEORETICAL 0.0)
HF_MULT = 0.60         # HARD_FAIL: mechanism below -> star operator does not transfer at substrate scale
CTRL_MAX = 0.15        # control: each collapsing control (bind/rand_exp/rand_cb/scram) must be below this
CTRL_LEAK = 0.40       # HARD_FAIL: any collapsing control >= this -> leak (verify-the-referent)
HP_COMPOSITE_EXACT = 0.90  # prime-necessity probe: composite regime ALSO exact -> prime NOT required (finding)
HP_CHAIN_D3 = 0.75     # HARD_PASS: depth-3 multiply-chain exact floor (THEORETICAL ~1.0)
HF_CHAIN_D3 = 0.20     # HARD_FAIL: depth-3 below -> chains drift worse than reasoning collision-bound law
HP_EQ_ACCEPT = 0.99    # HARD_PASS: equality-check accepts a correct product claim (true==true)
HP_EQ_REJECT = 0.99    # HARD_PASS: equality-check rejects an incorrect product claim (true!=false)
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


def _is_prime(n: int) -> bool:
    if n < 2:
        return False
    for d in range(2, int(n ** 0.5) + 1):
        if n % d == 0:
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
# Phasor codebooks + encode / bind / star-multiply / decode
# (codebooks + encode + bind + decode reused VERBATIM from add cell; star_multiply is the new operator)
# ============================================================


def phasor_codebook(m: int, sb: int, seed: int) -> np.ndarray:
    """Phase-LINEAR FPE codebook (m, sb) complex64: codebook[r,j] = exp(i*2*pi*k_j*r/m), k_j in [1,m-1].
    Integer k_j -> exact period-m periodicity -> per-dim base w_j = exp(i*2*pi*k_j/m), codebook[r]=w^r.
    Then codebook[a]**b == w^(a*b) == codebook[(a*b) mod m]: exponentiation IS modular multiplication."""
    g = np.random.default_rng(seed)
    k = g.integers(1, m, size=sb).astype(np.float64)          # nonzero integer frequencies
    r = np.arange(m, dtype=np.float64)[:, None]               # (m,1)
    phase = (2.0 * np.pi / m) * (r * k[None, :])              # (m,sb)
    return np.exp(1j * phase).astype(np.complex64)


def random_phasor_codebook(m: int, sb: int, seed: int) -> np.ndarray:
    """Control codebook (m, sb) complex64: random unit phasor per (r,j), NOT linear in r. Identical modulus
    (unit-magnitude), identical star pipeline -- ONLY the phase-linearity is removed (isolates the homomorphism)."""
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
    """FHRR bind: elementwise complex product. Disjoint sub-blocks -> adds all residues simultaneously
    (this is (a+b) mod M, NOT the product -- used only by the bind_not_power control)."""
    return u * v


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


def star_power(a_vec: np.ndarray, exps, moduli, sb: int) -> np.ndarray:
    """The STAR multiply core: raise sub-block i of a_vec to the integer power exps[i] (elementwise).
    codebook[a]**b == codebook[(a*b) mod m]. exps[i] is the decoded residue (b mod m_i)."""
    out = np.zeros(N_DIM, dtype=np.complex64)
    for i in range(len(moduli)):
        out[i * sb:(i + 1) * sb] = a_vec[i * sb:(i + 1) * sb] ** int(exps[i])
    return out


def star_multiply_vec(a_vec, b_vec, cbs, moduli, sb):
    """Full star multiply: decode b's residues, exponentiate a's phasor sub-blocks by them. Returns the
    product phasor (still a valid codeword of (a*b) mod M)."""
    b_res = decode_residues(b_vec, cbs, moduli, sb)
    return star_power(a_vec, b_res, moduli, sb)


# ============================================================
# Homomorphism formula self-test (MANDATORY per task): star-multiply correctness per regime
# ============================================================


def multiply_homomorphism_selftest(moduli, seed: int = 0) -> bool:
    """Formula self-test 2: decode(star_multiply(enc(a),enc(b))) == (a*b) mod M for random a,b; AND per-sub-
    block identity codebook[a]**b == codebook[(a*b) mod m] directly; AND the multiplicative-zero identity
    star_multiply(enc(a),enc(0)) decodes to exactly 0; AND star_multiply(enc(a),enc(1)) decodes to a
    (multiplicative identity). Holds for BOTH prime and composite moduli (decode-then-exponentiate is
    modulus-agnostic)."""
    M, Mi, yi = _crt_setup(moduli)
    cbs = [phasor_codebook(m, SB, 6000 + seed * 10 + i) for i, m in enumerate(moduli)]
    # direct identity: codeword raised to power b equals codeword of modular product (per residue)
    for i, m in enumerate(moduli):
        for _ in range(8):
            a = int(np.random.default_rng(seed + i + _).integers(0, m))
            b = int(np.random.default_rng(seed + i + _ + 99).integers(0, m))
            powered = cbs[i][a] ** b
            target = cbs[i][(a * b) % m]
            if not np.allclose(powered, target, atol=1e-3):
                return False
    # end-to-end: decode(star_multiply(enc(a),enc(b))) == (a*b) mod M
    rng = np.random.default_rng(4242 + seed)
    for _ in range(64):
        a = int(rng.integers(0, M))
        b = int(rng.integers(0, M))
        prod = star_multiply_vec(encode(a, cbs, moduli, SB), encode(b, cbs, moduli, SB), cbs, moduli, SB)
        if decode_int(prod, cbs, moduli, SB, M, Mi, yi) != (a * b) % M:
            return False
    # multiplicative zero + identity
    for _ in range(16):
        a = int(rng.integers(0, M))
        z = star_multiply_vec(encode(a, cbs, moduli, SB), encode(0, cbs, moduli, SB), cbs, moduli, SB)
        if decode_int(z, cbs, moduli, SB, M, Mi, yi) != 0:
            return False
        one = star_multiply_vec(encode(a, cbs, moduli, SB), encode(1, cbs, moduli, SB), cbs, moduli, SB)
        if decode_int(one, cbs, moduli, SB, M, Mi, yi) != a % M:
            return False
    return True


# ============================================================
# Arms
# ============================================================


def _digest_arr(arr) -> str:
    return hashlib.sha256(np.ascontiguousarray(np.asarray(arr)).tobytes()).hexdigest()


def _digest_int(int_list) -> str:
    return hashlib.sha256(np.asarray(int_list, dtype=np.int64).tobytes()).hexdigest()


def _cyclic_derangement(r: int):
    return [(i + 1) % r for i in range(r)]   # r=3 -> [1,2,0]


def run_regime(moduli, seed: int, trials: int, depths):
    """Run all arms for one (moduli-regime, seed). Returns a result dict + artifacts for arms-differ."""
    M, Mi, yi = _crt_setup(moduli)
    derange = _cyclic_derangement(R_MODULI)

    cb_phase = [phasor_codebook(m, SB, 6000 + seed * 10 + i) for i, m in enumerate(moduli)]
    cb_rand = [random_phasor_codebook(m, SB, 8000 + seed * 10 + i) for i, m in enumerate(moduli)]

    rng = np.random.default_rng(90000 + seed + M)
    pairs = [(int(rng.integers(0, M)), int(rng.integers(0, M))) for _ in range(trials)]
    exp_rng = np.random.default_rng(41000 + seed + M)   # wrong-exponent draws (random_exponent control)

    # --- single-step arms (all paired on same pairs) ---
    mul_hits = bind_hits = rexp_hits = rand_hits = scram_hits = 0
    rec_mul, rec_bind, rec_scram = [], [], []
    nm_below_half = 0
    nm_total = 0
    for (a, b) in pairs:
        truth = (a * b) % M
        ea = encode(a, cb_phase, moduli, SB)
        eb = encode(b, cb_phase, moduli, SB)
        b_res, margins = decode_residues(eb, cb_phase, moduli, SB, want_margin=True)
        # arm: star_multiply (MECHANISM)
        prod = star_power(ea, b_res, moduli, SB)
        res_mul = decode_residues(prod, cb_phase, moduli, SB)
        tM = _crt(res_mul, moduli, M, Mi, yi)
        mul_hits += 1 if tM == truth else 0
        rec_mul.append(tM)
        for (r1, r2) in margins:
            nm_total += 1
            if r2 <= 0.5 * r1:
                nm_below_half += 1
        # control: bind_not_power (use free-add bind, claim it is the product)
        tBind = decode_int(bind(ea, eb), cb_phase, moduli, SB, M, Mi, yi)
        bind_hits += 1 if tBind == truth else 0
        rec_bind.append(tBind)
        # control: random_exponent (exponentiate a by WRONG residues instead of decoded b)
        wrong = [int(exp_rng.integers(0, m)) for m in moduli]
        tRexp = decode_int(star_power(ea, wrong, moduli, SB), cb_phase, moduli, SB, M, Mi, yi)
        rexp_hits += 1 if tRexp == truth else 0
        # control: random_codebook (identical star pipeline on random phasors)
        earr = encode(a, cb_rand, moduli, SB)
        ebrr = encode(b, cb_rand, moduli, SB)
        brr = decode_residues(ebrr, cb_rand, moduli, SB)
        tRand = decode_int(star_power(earr, brr, moduli, SB), cb_rand, moduli, SB, M, Mi, yi)
        rand_hits += 1 if tRand == truth else 0
        # control: scrambled_modulus (mechanism decode then derange residues before CRT)
        res_C = [res_mul[derange[i]] for i in range(R_MODULI)]
        tC = _crt(res_C, moduli, M, Mi, yi)
        scram_hits += 1 if tC == truth else 0
        rec_scram.append(tC)

    acc_mul = mul_hits / trials
    acc_bind = bind_hits / trials
    acc_rexp = rexp_hits / trials
    acc_rand = rand_hits / trials
    acc_scram = scram_hits / trials
    nm_frac = (nm_below_half / nm_total) if nm_total else 0.0

    # --- multiply-chain arm (running product via repeated star exponentiation) ---
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
                tk_res = decode_residues(encode(terms[k], cb_phase, moduli, SB), cb_phase, moduli, SB)
                running = star_power(running, tk_res, moduli, SB)
                partial = (partial * terms[k]) % M
                dec = decode_int(running, cb_phase, moduli, SB, M, Mi, yi)
                step_total += 1
                step_ok += 1 if dec == partial else 0
            truth_chain = 1
            for t in terms:
                truth_chain = (truth_chain * t) % M
            final = decode_int(running, cb_phase, moduli, SB, M, Mi, yi)
            hits += 1 if final == truth_chain else 0
        chain[L] = {"exact": round(hits / n_chain, 4),
                    "per_step_ok": round(step_ok / step_total, 4),
                    "n_chain": n_chain}

    # --- equality-check arm (self-reasoning primitive: verify a claimed product exactly) ---
    eq_rng = np.random.default_rng(70000 + seed + M)
    n_eq = trials
    accept = reject = 0
    sim_eq = []
    sim_neq = []
    for _ in range(n_eq):
        a = int(eq_rng.integers(0, M)); b = int(eq_rng.integers(0, M))
        truth = (a * b) % M
        prod = star_multiply_vec(encode(a, cb_phase, moduli, SB), encode(b, cb_phase, moduli, SB),
                                 cb_phase, moduli, SB)
        got = decode_int(prod, cb_phase, moduli, SB, M, Mi, yi)
        correct_claim = truth
        wrong_claim = (truth + 1 + int(eq_rng.integers(0, max(1, M - 1)))) % M
        if wrong_claim == truth:
            wrong_claim = (truth + 1) % M
        accept += 1 if (got == correct_claim) else 0        # true == true
        reject += 1 if (got != wrong_claim) else 0          # true != false
        et = encode(truth, cb_phase, moduli, SB)
        ew = encode(wrong_claim, cb_phase, moduli, SB)
        denom = float(R_MODULI * SB)
        sim_eq.append(float((et @ np.conj(et)).real) / denom)
        sim_neq.append(float((et @ np.conj(ew)).real) / denom)
    eq_accept = accept / n_eq
    eq_reject = reject / n_eq
    eq_crisp_gap = (min(sim_eq) - max(sim_neq)) if sim_eq else 0.0

    # --- readable demo examples (prime_small regime only) ---
    demos = []
    if moduli == REGIMES["prime_small"]:
        for (a, b) in DEMO_PAIRS:
            prod = star_multiply_vec(encode(a, cb_phase, moduli, SB), encode(b, cb_phase, moduli, SB),
                                     cb_phase, moduli, SB)
            got = decode_int(prod, cb_phase, moduli, SB, M, Mi, yi)
            demos.append({"a": a, "b": b, "decoded_product": got, "expected_mod_M": (a * b) % M,
                          "M": M, "correct": got == (a * b) % M,
                          "wrapped": (a * b) >= M})

    artifacts = {
        "cb_phase0": _digest_arr(cb_phase[0]),
        "cb_rand0": _digest_arr(cb_rand[0]),
        "rec_mul": _digest_int(rec_mul),
        "rec_bind": _digest_int(rec_bind),
        "rec_scram": _digest_int(rec_scram),
    }
    return {
        "M": M, "moduli": list(moduli), "all_prime": all(_is_prime(m) for m in moduli),
        "acc_mul": round(acc_mul, 4), "acc_bind": round(acc_bind, 4), "acc_rexp": round(acc_rexp, 4),
        "acc_rand": round(acc_rand, 4), "acc_scram": round(acc_scram, 4),
        "nearmiss_frac_below_half": round(nm_frac, 4),
        "chain": chain,
        "eq_accept": round(eq_accept, 4), "eq_reject": round(eq_reject, 4),
        "eq_crisp_gap": round(eq_crisp_gap, 4),
        "eq_sim_equal_min": round(float(min(sim_eq)), 4) if sim_eq else None,
        "eq_sim_unequal_max": round(float(max(sim_neq)), 4) if sim_neq else None,
        "demos": demos,
    }, artifacts


# ============================================================
# Config + driver
# ============================================================


def get_config(mode: str):
    if mode == "selftest":
        return {"regimes": ["prime_small"], "trials": 8, "seeds": (7,), "depths": (1, 3)}
    if mode == "smoke":
        return {"regimes": ["prime_small", "prime_mid", "prime_large", "composite"],
                "trials": 40, "seeds": SEEDS, "depths": (1, 3, 5)}
    return {"regimes": ["prime_small", "prime_mid", "prime_large", "composite"],
            "trials": 300, "seeds": SEEDS, "depths": DEPTHS_FULL}


def expected_units(cfg) -> int:
    # per (regime, seed): 5 single arms (mul/bind/rexp/rand/scram) + len(depths) chain rows + 1 equality row
    per = 5 + len(cfg["depths"]) + 1
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
            per_unit.append({"regime": reg, "arm": "star_multiply", "seed": seed, "value": rr["acc_mul"]})
            per_unit.append({"regime": reg, "arm": "bind_not_power", "seed": seed, "value": rr["acc_bind"]})
            per_unit.append({"regime": reg, "arm": "random_exponent", "seed": seed, "value": rr["acc_rexp"]})
            per_unit.append({"regime": reg, "arm": "random_codebook", "seed": seed, "value": rr["acc_rand"]})
            per_unit.append({"regime": reg, "arm": "scrambled_modulus", "seed": seed, "value": rr["acc_scram"]})
            for L, cd in rr["chain"].items():
                per_unit.append({"regime": reg, "arm": "mult_chain", "depth": L, "seed": seed, "value": cd["exact"]})
            per_unit.append({"regime": reg, "arm": "equality", "seed": seed,
                             "value": rr["eq_accept"], "reject": rr["eq_reject"]})
            unit += 1
            _heartbeat(output_dir, unit, len(regimes) * len(seeds), t0,
                       extra={"regime": reg, "seed": seed, "M": rr["M"], "all_prime": rr["all_prime"],
                              "acc_mul": rr["acc_mul"], "acc_bind": rr["acc_bind"],
                              "acc_rexp": rr["acc_rexp"], "acc_rand": rr["acc_rand"], "acc_scram": rr["acc_scram"],
                              "eq_accept": rr["eq_accept"], "eq_reject": rr["eq_reject"]})
            chain_str = " ".join(f"d{L}:{cd['exact']:.3f}" for L, cd in rr["chain"].items())
            _say(f"  [seed {seed}] regime={reg} moduli={moduli} M={rr['M']} all_prime={rr['all_prime']}: "
                 f"mult={rr['acc_mul']:.3f} bind={rr['acc_bind']:.3f} rand_exp={rr['acc_rexp']:.3f} "
                 f"rand_cb={rr['acc_rand']:.3f} scram={rr['acc_scram']:.3f} | chain[{chain_str}] | "
                 f"eq_accept={rr['eq_accept']:.3f} eq_reject={rr['eq_reject']:.3f} nm_frac={rr['nearmiss_frac_below_half']:.3f}")
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
    prime_regs = [r for r in regimes if r in PRIME_REGIMES]
    comp_regs = [r for r in regimes if r in COMPOSITE_REGIMES]
    dmax = max(depths)

    # aggregate mechanism + controls over PRIME regimes (primary discriminator)
    A_all, A_cv_per_regime = [], []
    bind_all, rexp_all, rand_all, scram_all = [], [], [], []
    eq_accept_all, eq_reject_all, nm_all = [], [], []
    chain_d3_all, chain_dmax_all = [], []
    for reg in prime_regs:
        A_reg = [results[reg][s]["acc_mul"] for s in seeds]
        A_all.extend(A_reg)
        A_cv_per_regime.append(_cv(A_reg))
        bind_all.extend([results[reg][s]["acc_bind"] for s in seeds])
        rexp_all.extend([results[reg][s]["acc_rexp"] for s in seeds])
        rand_all.extend([results[reg][s]["acc_rand"] for s in seeds])
        scram_all.extend([results[reg][s]["acc_scram"] for s in seeds])
        eq_accept_all.extend([results[reg][s]["eq_accept"] for s in seeds])
        eq_reject_all.extend([results[reg][s]["eq_reject"] for s in seeds])
        nm_all.extend([results[reg][s]["nearmiss_frac_below_half"] for s in seeds])
        for s in seeds:
            ch = results[reg][s]["chain"]
            if 3 in ch:
                chain_d3_all.append(ch[3]["exact"])
            chain_dmax_all.append(ch[dmax]["exact"])

    A_min = min(A_all)
    A_mean = _mean(A_all)
    A_cv_max = max(A_cv_per_regime)
    bind_max = max(bind_all)
    rexp_max = max(rexp_all)
    rand_max = max(rand_all)
    scram_max = max(scram_all)
    ctrl_max = max(bind_max, rexp_max, rand_max, scram_max)
    eq_acc_min = min(eq_accept_all)
    eq_rej_min = min(eq_reject_all)
    nm_min = min(nm_all)
    d3_min = min(chain_d3_all) if chain_d3_all else float("nan")
    dmax_min = min(chain_dmax_all)

    # composite prime-necessity probe (mechanism exactness on composite moduli)
    comp_mul = []
    for reg in comp_regs:
        comp_mul.extend([results[reg][s]["acc_mul"] for s in seeds])
    comp_min = min(comp_mul) if comp_mul else float("nan")
    if comp_mul:
        if comp_min >= HP_COMPOSITE_EXACT:
            prime_finding = "PRIME_NOT_REQUIRED"
        elif comp_min < HF_MULT:
            prime_finding = "PRIME_REQUIRED"
        else:
            prime_finding = "AMBIGUOUS"
    else:
        prime_finding = "not_probed"

    diag = (f"star_multiply[min={A_min:.3f} mean={A_mean:.3f} cv_max={A_cv_max:.3f}] "
            f"ctrls[bind={bind_max:.3f} rand_exp={rexp_max:.3f} rand_cb={rand_max:.3f} scram={scram_max:.3f}] "
            f"chain[d3_min={d3_min:.3f} d{dmax}_min={dmax_min:.3f}] "
            f"eq[accept_min={eq_acc_min:.3f} reject_min={eq_rej_min:.3f}] "
            f"composite[min={comp_min:.3f} finding={prime_finding}] nearmiss_frac_min={nm_min:.3f}")

    # --- discriminator-fires / control gates (ALL modes incl smoke) ---
    if not (A_min >= HP_MULT_EXACT):
        if A_min < HF_MULT:
            return ("HARD_FAIL",
                    f"STAR_MULTIPLY FAILED: exact-multiply min={A_min:.3f} < {HF_MULT}. Decode-then-exponentiate "
                    f"does not transfer at substrate scale. {diag}", False)
        return ("DISCRIMINATOR_DID_NOT_FIRE",
                f"star_multiply did not reach exact floor (min={A_min:.3f} < {HP_MULT_EXACT}); mechanism "
                f"partial. Investigate before FULL. {diag}", False)
    if not (ctrl_max <= CTRL_MAX):
        return ("CONTROL_DID_NOT_COLLAPSE",
                f"a collapsing control did NOT collapse (max={ctrl_max:.3f} > {CTRL_MAX}): the isolated step "
                f"(exponentiate / decode / phase-linearity / CRT) is not load-bearing OR leak. {diag}", False)

    if mode == "smoke":
        return ("HARD_PASS",
                f"SMOKE_MACHINERY_OK: star_multiply is EXACT (min={A_min:.3f}) at all 3 prime regimes and full "
                f"N={N_DIM}; all 4 controls collapse (max={ctrl_max:.3f}); multiply chains exact "
                f"(d3_min={d3_min:.3f}); equality-check crisp (accept_min={eq_acc_min:.3f} "
                f"reject_min={eq_rej_min:.3f}); prime-necessity probe: composite mult min={comp_min:.3f} "
                f"({prime_finding}). Deliverable band is FULL-only (canonical = remote landing). {diag}", True)

    # --- FULL pre-registered bands ---
    if ctrl_max >= CTRL_LEAK:
        return ("HARD_FAIL",
                f"CONTROL LEAK: a control exact-multiply max={ctrl_max:.3f} >= {CTRL_LEAK}. Small-M brute-force "
                f"argmax may be accidentally hitting the product without the star operator. {diag}", True)
    passes = (A_min >= HP_MULT_EXACT and A_cv_max < HP_CV and ctrl_max <= CTRL_MAX
              and d3_min >= HP_CHAIN_D3 and eq_acc_min >= HP_EQ_ACCEPT and eq_rej_min >= HP_EQ_REJECT)
    if passes:
        return ("HARD_PASS",
                f"MULTIPLY TRANSLATES: the STAR operator (decode-then-exponentiate) makes MODULAR "
                f"MULTIPLICATION exact via elementwise integer-power of the existing phase-linear encoding. "
                f"Single-step exact-multiply min={A_min:.3f} (>= {HP_MULT_EXACT}, cv<{HP_CV}) across 3 all-prime "
                f"regimes M in [385,65231]; all 4 controls collapse (bind={bind_max:.3f} rand_exp={rexp_max:.3f} "
                f"rand_cb={rand_max:.3f} scram={scram_max:.3f}) -- isolating exponentiation, decode, "
                f"phase-linearity, and CRT each as load-bearing; {dmax}-step multiply-chains hold "
                f"(d3_min={d3_min:.3f}, d{dmax}_min={dmax_min:.3f}); exact equality-check crisp "
                f"(accept={eq_acc_min:.3f}, reject={eq_rej_min:.3f}). PRIME-NECESSITY FINDING: composite moduli "
                f"(8,9,25) ALSO exact (min={comp_min:.3f}) -> {prime_finding}: decode-then-exponentiate is "
                f"modulus-agnostic; prime-cyclicity is load-bearing only for the REJECTED discrete-log route, "
                f"NOT this one (inverts the drill's prediction 3). near-miss runner-up<=0.5*rank1 on "
                f"{nm_min:.3f} of decodes. {diag}", True)
    if d3_min < HF_CHAIN_D3:
        return ("HARD_FAIL",
                f"CHAINS DRIFT: depth-3 exact-multiply min={d3_min:.3f} < {HF_CHAIN_D3}: multiplicative "
                f"composition compounds noise worse than the reasoning collision-bound law. {diag}", True)
    return ("MIDDLE_BAND",
            f"partial: mechanism exact but a secondary band missed (chain d3_min={d3_min:.3f}, eq_accept="
            f"{eq_acc_min:.3f}, eq_reject={eq_rej_min:.3f}, cv_max={A_cv_max:.3f}). {diag}", True)


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

    # formula self-tests (ALL modes): CRT correctness + the MULTIPLY homomorphism, per regime in play.
    for reg in cfg["regimes"]:
        moduli = REGIMES[reg]
        if not crt_selftest(moduli):
            raise AssertionError(f"CRT_SELFTEST_FAIL regime={reg} moduli={moduli}")
        if not multiply_homomorphism_selftest(moduli, seed=cfg["seeds"][0]):
            raise AssertionError(f"MULTIPLY_HOMOMORPHISM_SELFTEST_FAIL regime={reg} moduli={moduli} "
                                 f"(decode(star_multiply(enc(a),enc(b))) != (a*b) mod M)")
    _say(f"[{ANCHOR_NAME}] formula self-tests PASSED (CRT + multiply-homomorphism) for regimes {cfg['regimes']}")

    cfg, results, artifacts, per_unit = run_all(mode, output_dir, t0)

    # arms_differ (META_RULE_AF): phase codebook != random codebook; mechanism integers != scrambled integers;
    # mechanism integers != bind (additive) integers.
    arms_differ_ok = True
    reasons = []
    for key, art in artifacts.items():
        if art["cb_phase0"] == art["cb_rand0"]:
            arms_differ_ok = False; reasons.append(f"{key}:phase==random codebook")
        if art["rec_mul"] == art["rec_scram"]:
            arms_differ_ok = False; reasons.append(f"{key}:scramble did not alter recovered integers")
        if art["rec_mul"] == art["rec_bind"]:
            arms_differ_ok = False; reasons.append(f"{key}:bind_not_power == star_multiply (arm bug)")
    if not arms_differ_ok:
        raise AssertionError("META_RULE_AF VIOLATION: " + "; ".join(reasons))

    verdict, vmsg, order_ok = classify(results, cfg, mode)
    elapsed = time.perf_counter() - t0

    # assemble arm summaries
    arm_summ = {}
    for reg in cfg["regimes"]:
        seeds = cfg["seeds"]
        MUL = [results[reg][s]["acc_mul"] for s in seeds]
        BIND = [results[reg][s]["acc_bind"] for s in seeds]
        REXP = [results[reg][s]["acc_rexp"] for s in seeds]
        RAND = [results[reg][s]["acc_rand"] for s in seeds]
        SCRAM = [results[reg][s]["acc_scram"] for s in seeds]
        eqa = [results[reg][s]["eq_accept"] for s in seeds]
        eqr = [results[reg][s]["eq_reject"] for s in seeds]
        nm = [results[reg][s]["nearmiss_frac_below_half"] for s in seeds]
        chain_summ = {}
        for L in cfg["depths"]:
            ex = [results[reg][s]["chain"][L]["exact"] for s in seeds]
            st = [results[reg][s]["chain"][L]["per_step_ok"] for s in seeds]
            chain_summ[f"d{L}"] = {"exact_mean": round(_mean(ex), 4), "exact_per_seed": ex,
                                   "per_step_ok_mean": round(_mean(st), 4)}
        arm_summ[reg] = {
            "M": results[reg][seeds[0]]["M"], "moduli": results[reg][seeds[0]]["moduli"],
            "all_prime": results[reg][seeds[0]]["all_prime"],
            "star_multiply": {"exact_mean": round(_mean(MUL), 4), "per_seed": MUL, "cv": round(_cv(MUL), 4)},
            "bind_not_power": {"exact_mean": round(_mean(BIND), 4), "per_seed": BIND},
            "random_exponent": {"exact_mean": round(_mean(REXP), 4), "per_seed": REXP},
            "random_codebook": {"exact_mean": round(_mean(RAND), 4), "per_seed": RAND},
            "scrambled_modulus": {"exact_mean": round(_mean(SCRAM), 4), "per_seed": SCRAM},
            "chain": chain_summ,
            "equality_check": {"accept_mean": round(_mean(eqa), 4), "accept_per_seed": eqa,
                               "reject_mean": round(_mean(eqr), 4), "reject_per_seed": eqr,
                               "crisp_gap": results[reg][seeds[0]]["eq_crisp_gap"],
                               "sim_equal_min": results[reg][seeds[0]]["eq_sim_equal_min"],
                               "sim_unequal_max": results[reg][seeds[0]]["eq_sim_unequal_max"]},
            "nearmiss_frac_below_half_mean": round(_mean(nm), 4),
        }

    demos = results["prime_small"][cfg["seeds"][0]]["demos"] if "prime_small" in results else []

    # prime-necessity finding summary
    comp_regs = [r for r in cfg["regimes"] if r in COMPOSITE_REGIMES]
    comp_mul = [results[r][s]["acc_mul"] for r in comp_regs for s in cfg["seeds"]]
    comp_min = min(comp_mul) if comp_mul else None
    prime_finding = ("PRIME_NOT_REQUIRED" if (comp_min is not None and comp_min >= HP_COMPOSITE_EXACT)
                     else ("PRIME_REQUIRED" if (comp_min is not None and comp_min < HF_MULT)
                           else ("AMBIGUOUS" if comp_min is not None else "not_probed")))

    metrics = {
        "anchor_name": ANCHOR_NAME,
        "verdict": verdict,
        "verdict_msg": vmsg,
        "summary": f"{verdict}: RNS star-operator modular multiplication ({mode})",
        "run_mode": mode,
        "elapsed_s": round(elapsed, 2),
        "n_seeds": len(cfg["seeds"]),
        "n_units": len(per_unit),
        "expected_n_units": exp,
        "cardinality_ok": len(per_unit) >= exp,
        "prime_necessity_finding": prime_finding,
        "composite_mult_min": comp_min,
        "config": {"N": N_DIM, "R_MODULI": R_MODULI, "SB": SB,
                   "regimes": {r: list(REGIMES[r]) for r in cfg["regimes"]},
                   "prime_regimes": [r for r in cfg["regimes"] if r in PRIME_REGIMES],
                   "composite_regimes": [r for r in cfg["regimes"] if r in COMPOSITE_REGIMES],
                   "seeds": list(cfg["seeds"]), "trials": cfg["trials"], "depths": list(cfg["depths"]),
                   "mechanism": "star_operator_decode_then_exponentiate",
                   "multiply": "per_subblock_elementwise_integer_power",
                   "decode": "per_subblock_phasor_argmax_then_CRT",
                   "storage_strategy": "no_storage_algebraic_star"},
        "arms": arm_summ,
        "demos": demos,
        "per_unit": per_unit,
        "arms_differ_verified": arms_differ_ok,
        "controls": {"scram_collapsed": order_ok},
        "bands": {"HP_mult_exact": HP_MULT_EXACT, "HP_cv": HP_CV, "HF_mult": HF_MULT,
                  "ctrl_max": CTRL_MAX, "ctrl_leak": CTRL_LEAK, "HP_composite_exact": HP_COMPOSITE_EXACT,
                  "HP_chain_d3": HP_CHAIN_D3, "HF_chain_d3": HF_CHAIN_D3,
                  "HP_eq_accept": HP_EQ_ACCEPT, "HP_eq_reject": HP_EQ_REJECT, "nearmiss_frac": NEARMISS_FRAC},
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(),
        "host": platform.node(),
    }
    _write_metrics_atomic(output_dir, metrics)
    written = json.load(open(output_dir / "metrics.json"))
    assert written["run_mode"] == mode, f"RUN_MODE_MISMATCH {written['run_mode']} != {mode}"

    _say(f"\n[{ANCHOR_NAME}] {verdict}: {vmsg}")
    if demos:
        _say(f"[{ANCHOR_NAME}] demos: " + "; ".join(
            f"{d['a']}*{d['b']}={d['decoded_product']}(exp {d['expected_mod_M']}"
            f"{',WRAP' if d['wrapped'] else ''}){'OK' if d['correct'] else 'X'}" for d in demos))
    _say(f"[{ANCHOR_NAME}] metrics -> {output_dir / 'metrics.json'}  elapsed={elapsed:.1f}s")
    return 0


def _run_selftest() -> int:
    t0 = time.perf_counter()
    output_dir = _out_dir()
    output_dir.mkdir(parents=True, exist_ok=True)
    ok_crt = all(crt_selftest(REGIMES[r]) for r in REGIMES)
    ok_hom = all(multiply_homomorphism_selftest(REGIMES[r], seed=7) for r in REGIMES)
    cfg, results, _art, _pu = run_all("selftest", output_dir, t0)
    rr = results["prime_small"][7]
    ok = ok_crt and ok_hom and (rr["acc_mul"] >= 0.99) and (rr["acc_bind"] <= 0.15) \
        and (rr["acc_rexp"] <= 0.15) and (rr["acc_rand"] <= 0.15) and (rr["acc_scram"] <= 0.05) \
        and (rr["eq_accept"] >= 0.99) and (rr["eq_reject"] >= 0.99)
    _say(f"[{ANCHOR_NAME}] SELFTEST {'PASS' if ok else 'FAIL'}: crt_ok={ok_crt} hom_ok={ok_hom} "
         f"mult={rr['acc_mul']:.3f} bind={rr['acc_bind']:.3f} rand_exp={rr['acc_rexp']:.3f} "
         f"rand_cb={rr['acc_rand']:.3f} scram={rr['acc_scram']:.3f} "
         f"eq_accept={rr['eq_accept']:.3f} eq_reject={rr['eq_reject']:.3f} [{time.perf_counter()-t0:.1f}s]")
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
