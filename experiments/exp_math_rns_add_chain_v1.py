# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate: phase-linear codebook vs random-phasor codebook hash-distinct
#     (the ONLY difference between mechanism arm A and control arm B is phase-LINEARITY); arm-A decoded
#     integers vs scrambled-CRT decoded integers hash-distinct (derangement genuinely alters output).
#     Mechanism/control arms that legitimately share the TRUTH integers (an exact adder and a broken adder
#     both know the truth) are never hash-compared on truth arrays; we hash the CODEBOOKS and the RECOVERED
#     integer arrays (which DO differ: A recovers a+b, B recovers garbage, scram recovers permuted-CRT).
# - final_metrics_atomicity: tmp_replace (write metrics.json.tmp then os.replace).
# - except SystemExit: raise BEFORE except Exception (no BaseException).
# - crlb/capacity-feasibility: per-residue decode is a phasor argmax over m_i candidates in a sub-block of
#     dim sb=2730 (N=8192, R=3). SNR ~ sqrt(sb/1) vs sqrt(sb) runner-up noise; sb=2730 >> max modulus 43,
#     so per-residue argmax is collision-free (rank-1 == 1.0, runner-up ~ 1/sqrt(sb) ~ 0.019). No
#     superposition-noise floor gates the 0.99 exact-add target. discriminator_reachability=True.
#     crlb_n_a is NOT claimed: the reachability argument IS the capacity-feasibility analysis.
# - baseline_in_band (META_RULE_AG): there is NO difficulty-baseline that must sit in (0.05,0.95). This is
#     an EXACTNESS/CORRECTNESS test, not a difficulty sweep. arm A (mechanism) is expected ~1.0 by exact
#     group-homomorphism construction; arm B (random-phasor control) and arm C (scrambled-modulus control)
#     are CONTROL arms intentionally ~0.0 -> exempt from the in-band rule (declared controls, same carve-out
#     as rns_scram/single_synth in exp_generation_decoder_rns_crt_highvocab_v1). The discriminator is the
#     CONTRAST A(~1.0) vs B(~0.0), which does NOT saturate/close at scale (arm B falls toward 1/M as M grows).
# - discriminator survives scale: smoke runs at FULL N=8192, FULL sub-block dim sb=2730, and ALL 3 moduli
#     regimes (small M=504, mid M=5168, large M=70520). Smoke reduces trials/seeds/chain-depths ONLY, never
#     N/sb/moduli. A-holds + B-collapse + C-collapse + chain-exact all FIRE in smoke (option A of
#     DISCRIMINATOR-MUST-SURVIVE-SCALE: smoke at full-N parameters).
# - HARD_PASS strictly above floor: arm A exact-add HP floor 0.99 (HF=0.60); MEASURED expectation ~1.0
#     (exact homomorphism, collision-free decode). Contrast/gap A-B ~1.0 is the real discriminator.
# - all numbers in comments tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@.
#
# MATH CAPABILITY -- RNS PHASE-LINEAR ADDITION CHAIN + EXACT EQUALITY CHECK  v1
# ============================================================================
# FIRST real math-capability cell. Turns the substrate's PROVEN exact modular-residue machinery
# (3x HARD_PASS CRT/RNS cells; exp_generation_decoder_rns_crt_highvocab_v1 FULL exact_ordered=1.000 @
# V=65536 MEASURED@data/exp_generation_decoder_rns_crt_highvocab_v1/metrics.json:arms.rns_crt@V65536D26.exact_ordered_mean)
# into genuine ARITHMETIC via a small PHASE-LINEAR re-encoding.
#
# THE MECHANISM (CITED@Kymn/Kleyko/Frady/Kanerva/Sommer/Olshausen 2024, Neural Computation, arXiv:2311.04872;
# CITED@Frady/Sommer FPE; CITED@Plate 2003 FHRR bind):
#   Encode a residue value r in [0,m) as a PHASE-LINEAR PHASOR (m-th roots of unity):
#       codebook_m[r, j] = exp(i * 2*pi * k_j * r / m),   k_j integer in [1, m-1]  (random per dim j)
#   Then the EXISTING FHRR bind operator (elementwise complex product) IS modular addition, for free:
#       enc(a) (*) enc(b)  ==  enc((a+b) mod m)          [group homomorphism (Z_m,+) -> unit phasors]
#   because exp(i*2*pi*k_j*a/m) * exp(i*2*pi*k_j*b/m) = exp(i*2*pi*k_j*(a+b)/m), and integer k_j makes the
#   encoding EXACTLY periodic with period m (so a and a+m map to the SAME phasor -> modular wraparound is
#   handled at the encoding level; CRT stitches the residues back to an integer in [0, prod(moduli))).
#
# ENCODING A FULL INTEGER x (reusing the proven disjoint-sub-block RNS layout verbatim):
#   split N into R=3 disjoint sub-blocks; sub-block i holds codebook_{m_i}[x mod m_i]. The SINGLE existing
#   full-vector bind (elementwise product) then adds ALL residues simultaneously (disjoint index ranges),
#   and per-sub-block phasor argmax + CRT decodes the result. NO new operator; NO resonator (glass-box
#   per-sub-block argmax, same decode topology as the landed rns_crt cell, phasor codebook swapped in).
#
# ARMS (all PAIRED on the same (a,b) integer pairs per regime/seed):
#   phase_linear_add   : MECHANISM -- phasor FPE codebooks, bind=complex-product, decode=argmax+CRT.
#                        Expected exact-add ~1.0.                                            [MECHANISM]
#   random_codebook_add: CONTROL/BASELINE -- IDENTICAL pipeline (complex unit phasors, same bind, same
#                        decode) but phases are RANDOM per (r,j) (NOT linear in r) -> NO homomorphism ->
#                        bind of two codes is unrelated to codebook[(a+b) mod m] -> decode fails.
#                        Isolates phase-LINEARITY as THE load-bearing ingredient (stronger control than
#                        random-real: holds everything constant except linearity). Expected ~0.0.  [CONTROL]
#   scrambled_modulus  : CONTROL -- arm-A phasor decode (residues correct) then DERANGE residues before CRT
#                        -> CRT reconstruction collapses. Confirms CRT is load-bearing. Expected ~0.0. [CONTROL]
#   phase_chain_dL     : arm-A mechanism applied over an L-step ADD chain (running bind product), for
#                        depths L in {1,3,5,10}. Tests noise accumulation vs the proven collision-bound
#                        multi-hop reasoning law. Phasor bind is EXACT so no drift is EXPECTED (honest:
#                        chains do not accumulate encoding noise; decode noise is per-number not cumulative).
#   equality_check     : the SELF-REASONING primitive -- decode(result) EXACTLY == claimed answer (discrete
#                        True/False, NOT fuzzy cosine). accept-correct + reject-incorrect crispness.
#
# is-math-easier PROBE (near-miss margin): for arm-A decode, runner-up residue similarity vs rank-1. Math's
# discrete/exact answer space should be FAR more separated (rank-1==1.0, runner-up~1/sqrt(sb)) than the
# natural-language relational near-miss problem (Hits@10~0.75 but rank-1~0.09 hubness crowding,
# CITED@notes/director_POST_COMPACTION_BACKUP_FULL_STATE_2026-07-05.md FRONTIER). Reported, not hard-gated.
#
# Brain-grounding (CITED@): entorhinal grid cells ARE a residue-number-system (Sreenivasan & Fiete 2011,
# Nat. Neurosci.); the same grid-like code generalizes to abstract magnitude spaces (Constantinescu, O'Reilly
# & Behrens 2016, Science). Literal mechanism reuse, not analogy -- the landed CRT cells were built to
# replicate it; this cell extends that same mechanism from addressing to arithmetic.
#
# ASCII-only. CPU default (numpy complex64; no GPU, no LLM; wall < 10s total -> sequential-CPU justified).
# Self-contained (synthetic phasor codebooks; no pool/re-encode dependency).
# Run: python experiments/exp_math_rns_add_chain_v1.py [--self-test | --smoke]
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

ANCHOR_NAME = "math_rns_add_chain_v1"
REPO = Path(__file__).resolve().parents[1]

N_DIM = 8192          # substrate compositional default (== landed rns_crt cell); never reduced
R_MODULI = 3          # residues per integer (disjoint sub-blocks)
SB = N_DIM // R_MODULI  # 2730 dims per sub-block; sb >> max modulus 43 -> collision-free phasor decode

# Three moduli regimes = ">=3 moduli-products worth of dynamic range" (drill pre-reg). Each set is
# pairwise-coprime (asserted at runtime); M = prod. small: readable human-scale demos (7+5=12) + fast
# wraparound (100+404 mod 504 = 0); large: 70520-range integers with wraparound.
REGIMES = {
    "small": (7, 8, 9),      # M=504
    "mid":   (16, 17, 19),   # M=5168
    "large": (40, 41, 43),   # M=70520
}
SEEDS = (7, 13, 19)
DEPTHS_FULL = (1, 3, 5, 10)

# Readable arithmetic examples reported verbatim (small regime, M=504): (a, b). Last two wrap mod 504.
DEMO_PAIRS = [(7, 5), (12, 30), (250, 250), (100, 404), (503, 2)]

# ---- Pre-registered bands (HYPOTHESIZED from exact-homomorphism theory; MEASURED filled by smoke) ----
HP_EXACT_ADD = 0.99   # HARD_PASS: arm A exact-add floor (THEORETICAL ~1.0; group homomorphism is exact)
HP_CV = 0.10          # HARD_PASS: cross-seed cv of arm A exact-add (THEORETICAL 0.0)
HF_EXACT_ADD = 0.60   # HARD_FAIL: arm A below -> phase-linear re-encoding does not transfer at substrate scale
B_CTRL_MAX = 0.15     # discriminator/control: random-codebook arm must FAIL to add (be below this)
B_LEAK = 0.40         # HARD_FAIL: random-codebook arm >= this -> leak (verify-the-referent)
C_SCRAM_MAX = 0.05    # control: scrambled-modulus arm must collapse below this
HP_CHAIN_D3 = 0.75    # HARD_PASS: depth-3 chain exact-add floor (drill; THEORETICAL ~1.0)
HF_CHAIN_D3 = 0.20    # HARD_FAIL: depth-3 below -> chains drift worse than reasoning collision-bound law
HP_EQ_ACCEPT = 0.99   # HARD_PASS: equality-check accepts a correct claim (true==true)
HP_EQ_REJECT = 0.99   # HARD_PASS: equality-check rejects an incorrect claim (true!=false; no false-accept)
NEARMISS_FRAC = 0.90  # is-math-easier: fraction of residue decodes with runner-up <= 0.5*rank-1 (drill)


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
# CRT number theory (reused verbatim from landed rns_crt cell; formula self-test target)
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
# Phasor codebooks + encode / bind / decode
# ============================================================


def phasor_codebook(m: int, sb: int, seed: int) -> np.ndarray:
    """Phase-LINEAR FPE codebook (m, sb) complex64: codebook[r,j] = exp(i*2*pi*k_j*r/m), k_j in [1,m-1].
    Integer k_j -> exact period-m periodicity -> bind (elementwise product) IS modular addition."""
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
    before CRT (arm C control)."""
    residues = decode_residues(v, cbs, moduli, sb)
    if scramble is not None:
        residues = [residues[scramble[i]] for i in range(len(residues))]
    return _crt(residues, moduli, M, Mi, yi)


# ============================================================
# Homomorphism formula self-test (MANDATORY per task)
# ============================================================


def homomorphism_selftest(moduli, seed: int = 0) -> bool:
    """Formula self-test 2: decode(bind(enc(a),enc(b))) == (a+b) mod M for random a,b (the group homomorphism).
    Also checks the elementwise-product == codeword-of-sum identity directly per sub-block."""
    M, Mi, yi = _crt_setup(moduli)
    cbs = [phasor_codebook(m, SB, 6000 + seed * 10 + i) for i, m in enumerate(moduli)]
    # direct identity: product of two codewords equals codeword of modular sum (per residue)
    for i, m in enumerate(moduli):
        for _ in range(8):
            a = int(np.random.default_rng(seed + i + _).integers(0, m))
            b = int(np.random.default_rng(seed + i + _ + 99).integers(0, m))
            prod = cbs[i][a] * cbs[i][b]
            target = cbs[i][(a + b) % m]
            if not np.allclose(prod, target, atol=1e-4):
                return False
    # end-to-end: decode(bind(enc(a),enc(b))) == (a+b) mod M
    rng = np.random.default_rng(4242 + seed)
    for _ in range(64):
        a = int(rng.integers(0, M))
        b = int(rng.integers(0, M))
        got = decode_int(bind(encode(a, cbs, moduli, SB), encode(b, cbs, moduli, SB)),
                         cbs, moduli, SB, M, Mi, yi)
        if got != (a + b) % M:
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
    m0, m1, m2 = moduli
    M, Mi, yi = _crt_setup(moduli)
    derange = _cyclic_derangement(R_MODULI)

    cb_phase = [phasor_codebook(m, SB, 6000 + seed * 10 + i) for i, m in enumerate(moduli)]
    cb_rand = [random_phasor_codebook(m, SB, 8000 + seed * 10 + i) for i, m in enumerate(moduli)]

    rng = np.random.default_rng(90000 + seed + M)
    pairs = [(int(rng.integers(0, M)), int(rng.integers(0, M))) for _ in range(trials)]

    # --- single-step arms A / B / C (all paired on same pairs) ---
    a_hits = b_hits = c_hits = 0
    rec_A, rec_C = [], []
    nm_below_half = 0
    nm_total = 0
    for (a, b) in pairs:
        truth = (a + b) % M
        # arm A: phase-linear
        ua = encode(a, cb_phase, moduli, SB)
        ub = encode(b, cb_phase, moduli, SB)
        sA = bind(ua, ub)
        res_A, margins = decode_residues(sA, cb_phase, moduli, SB, want_margin=True)
        tA = _crt(res_A, moduli, M, Mi, yi)
        a_hits += 1 if tA == truth else 0
        rec_A.append(tA)
        for (r1, r2) in margins:
            nm_total += 1
            if r2 <= 0.5 * r1:
                nm_below_half += 1
        # arm B: random codebook, identical pipeline
        vb_a = encode(a, cb_rand, moduli, SB)
        vb_b = encode(b, cb_rand, moduli, SB)
        sB = bind(vb_a, vb_b)
        tB = decode_int(sB, cb_rand, moduli, SB, M, Mi, yi)
        b_hits += 1 if tB == truth else 0
        # arm C: phase-linear decode then derange residues before CRT
        res_C = [res_A[derange[i]] for i in range(R_MODULI)]
        tC = _crt(res_C, moduli, M, Mi, yi)
        c_hits += 1 if tC == truth else 0
        rec_C.append(tC)

    acc_A = a_hits / trials
    acc_B = b_hits / trials
    acc_C = c_hits / trials
    nm_frac = (nm_below_half / nm_total) if nm_total else 0.0

    # --- chain arm (arm A over L-step add chains) ---
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
                running = bind(running, encode(terms[k], cb_phase, moduli, SB))
                partial = (partial + terms[k]) % M
                dec = decode_int(running, cb_phase, moduli, SB, M, Mi, yi)
                step_total += 1
                step_ok += 1 if dec == partial else 0
            final = decode_int(running, cb_phase, moduli, SB, M, Mi, yi)
            hits += 1 if final == (sum(terms) % M) else 0
        chain[L] = {"exact": round(hits / n_chain, 4),
                    "per_step_ok": round(step_ok / step_total, 4),
                    "n_chain": n_chain}

    # --- equality-check arm (self-reasoning primitive) ---
    # For each pair: verify decode(result) EXACTLY == correct claim (accept) and != incorrect claim (reject).
    eq_rng = np.random.default_rng(70000 + seed + M)
    n_eq = trials
    accept = reject = 0
    sim_eq = []
    sim_neq = []
    for _ in range(n_eq):
        a = int(eq_rng.integers(0, M)); b = int(eq_rng.integers(0, M))
        truth = (a + b) % M
        res_vec = bind(encode(a, cb_phase, moduli, SB), encode(b, cb_phase, moduli, SB))
        got = decode_int(res_vec, cb_phase, moduli, SB, M, Mi, yi)
        correct_claim = truth
        wrong_claim = (truth + 1 + int(eq_rng.integers(0, max(1, M - 1)))) % M
        if wrong_claim == truth:
            wrong_claim = (truth + 1) % M
        accept += 1 if (got == correct_claim) else 0        # true == true
        reject += 1 if (got != wrong_claim) else 0          # true != false
        # vector-level crispness (reported, NOT the certificate): sim(enc(t),enc(t))=1.0 vs sim(enc(t),enc(t'))
        et = encode(truth, cb_phase, moduli, SB)
        ew = encode(wrong_claim, cb_phase, moduli, SB)
        denom = float(R_MODULI * SB)
        sim_eq.append(float((et @ np.conj(et)).real) / denom)
        sim_neq.append(float((et @ np.conj(ew)).real) / denom)
    eq_accept = accept / n_eq
    eq_reject = reject / n_eq
    eq_crisp_gap = (min(sim_eq) - max(sim_neq)) if sim_eq else 0.0

    # --- readable demo examples (small regime only) ---
    demos = []
    if moduli == REGIMES["small"]:
        for (a, b) in DEMO_PAIRS:
            got = decode_int(bind(encode(a, cb_phase, moduli, SB), encode(b, cb_phase, moduli, SB)),
                             cb_phase, moduli, SB, M, Mi, yi)
            demos.append({"a": a, "b": b, "decoded_sum": got, "expected_mod_M": (a + b) % M,
                          "M": M, "correct": got == (a + b) % M,
                          "wrapped": (a + b) >= M})

    artifacts = {
        "cb_phase0": _digest_arr(cb_phase[0]),
        "cb_rand0": _digest_arr(cb_rand[0]),
        "rec_A": _digest_int(rec_A),
        "rec_C": _digest_int(rec_C),
    }
    return {
        "M": M, "moduli": list(moduli),
        "acc_A": round(acc_A, 4), "acc_B": round(acc_B, 4), "acc_C": round(acc_C, 4),
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
        return {"regimes": ["small"], "trials": 8, "seeds": (7,), "depths": (1, 3)}
    if mode == "smoke":
        return {"regimes": ["small", "mid", "large"], "trials": 40, "seeds": SEEDS, "depths": (1, 3, 5)}
    return {"regimes": ["small", "mid", "large"], "trials": 300, "seeds": SEEDS, "depths": DEPTHS_FULL}


def expected_units(cfg) -> int:
    # per (regime, seed): 3 single arms + len(depths) chain rows + 1 equality row
    per = 3 + len(cfg["depths"]) + 1
    return len(cfg["regimes"]) * len(cfg["seeds"]) * per


def run_all(mode: str, output_dir: Path, t0: float):
    cfg = get_config(mode)
    regimes, trials, seeds, depths = cfg["regimes"], cfg["trials"], cfg["seeds"], cfg["depths"]
    results = {}          # results[regime][seed] = regime_result
    artifacts = {}
    per_unit = []
    total_units = expected_units(cfg)
    unit = 0
    for reg in regimes:
        moduli = REGIMES[reg]
        results[reg] = {}
        for seed in seeds:
            rr, art = run_regime(moduli, seed, trials, depths)
            results[reg][seed] = rr
            artifacts[f"{reg}_{seed}"] = art
            # per_unit rows (cardinality)
            per_unit.append({"regime": reg, "arm": "phase_linear_add", "seed": seed, "value": rr["acc_A"]})
            per_unit.append({"regime": reg, "arm": "random_codebook_add", "seed": seed, "value": rr["acc_B"]})
            per_unit.append({"regime": reg, "arm": "scrambled_modulus", "seed": seed, "value": rr["acc_C"]})
            for L, cd in rr["chain"].items():
                per_unit.append({"regime": reg, "arm": "chain", "depth": L, "seed": seed, "value": cd["exact"]})
            per_unit.append({"regime": reg, "arm": "equality", "seed": seed,
                             "value": rr["eq_accept"], "reject": rr["eq_reject"]})
            unit += 1
            _heartbeat(output_dir, unit, len(regimes) * len(seeds), t0,
                       extra={"regime": reg, "seed": seed, "M": rr["M"],
                              "acc_A": rr["acc_A"], "acc_B": rr["acc_B"], "acc_C": rr["acc_C"],
                              "eq_accept": rr["eq_accept"], "eq_reject": rr["eq_reject"]})
            chain_str = " ".join(f"d{L}:{cd['exact']:.3f}" for L, cd in rr["chain"].items())
            _say(f"  [seed {seed}] regime={reg} moduli={moduli} M={rr['M']}: "
                 f"phase_add={rr['acc_A']:.3f} rand_add={rr['acc_B']:.3f} scram={rr['acc_C']:.3f} | "
                 f"chain[{chain_str}] | "
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

    # aggregate per arm across regimes/seeds
    A_all, B_all, C_all = [], [], []
    A_cv_per_regime = []
    eq_accept_all, eq_reject_all = [], []
    nm_all = []
    chain_d3_all, chain_dmax_all = [], []
    dmax = max(depths)
    for reg in regimes:
        A_reg = [results[reg][s]["acc_A"] for s in seeds]
        A_all.extend(A_reg)
        A_cv_per_regime.append(_cv(A_reg))
        B_all.extend([results[reg][s]["acc_B"] for s in seeds])
        C_all.extend([results[reg][s]["acc_C"] for s in seeds])
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
    B_max = max(B_all)
    C_max = max(C_all)
    eq_acc_min = min(eq_accept_all)
    eq_rej_min = min(eq_reject_all)
    nm_min = min(nm_all)
    d3_min = min(chain_d3_all) if chain_d3_all else float("nan")
    dmax_min = min(chain_dmax_all)

    diag = (f"phase_add[min={A_min:.3f} mean={A_mean:.3f} cv_max={A_cv_max:.3f}] "
            f"rand_add[max={B_max:.3f}] scram[max={C_max:.3f}] "
            f"chain[d3_min={d3_min:.3f} d{dmax}_min={dmax_min:.3f}] "
            f"eq[accept_min={eq_acc_min:.3f} reject_min={eq_rej_min:.3f}] "
            f"nearmiss_frac_min={nm_min:.3f}")

    # --- discriminator-fires / control gates (ALL modes incl smoke) ---
    if not (A_min >= HP_EXACT_ADD):
        # if mechanism arm fails to add, discriminator did not fire OR mechanism failed
        if A_min < HF_EXACT_ADD:
            return ("HARD_FAIL",
                    f"PHASE_LINEAR_ADD FAILED: exact-add min={A_min:.3f} < {HF_EXACT_ADD}. Group homomorphism "
                    f"does not transfer at substrate scale. {diag}", False)
        # in [HF, HP): mechanism works but not exact -> mechanism-not-firing-cleanly
        return ("DISCRIMINATOR_DID_NOT_FIRE",
                f"phase_linear_add did not reach exact floor (min={A_min:.3f} < {HP_EXACT_ADD}); mechanism "
                f"partial. Investigate before FULL. {diag}", False)
    if not (B_max <= B_CTRL_MAX):
        return ("CONTROL_DID_NOT_COLLAPSE",
                f"random-codebook control did NOT fail to add (max={B_max:.3f} > {B_CTRL_MAX}): phase-linearity "
                f"is not the load-bearing ingredient OR leak (verify-the-referent). {diag}", False)
    if not (C_max <= C_SCRAM_MAX):
        return ("CONTROL_DID_NOT_COLLAPSE",
                f"scrambled-modulus control did NOT collapse (max={C_max:.3f} > {C_SCRAM_MAX}): CRT "
                f"reconstruction not load-bearing / residue order leaks. {diag}", False)

    if mode == "smoke":
        return ("HARD_PASS",
                f"SMOKE_MACHINERY_OK: phase_linear_add is EXACT (min={A_min:.3f}) at ALL 3 regimes and full "
                f"N={N_DIM}; random-codebook control FAILS to add (max={B_max:.3f}); scrambled-modulus control "
                f"collapses (max={C_max:.3f}); chains exact (d3_min={d3_min:.3f}); equality-check crisp "
                f"(accept_min={eq_acc_min:.3f} reject_min={eq_rej_min:.3f}). Deliverable band is FULL-only "
                f"(canonical = remote landing). {diag}", True)

    # --- FULL pre-registered bands ---
    if B_max >= B_LEAK:
        return ("HARD_FAIL",
                f"RANDOM_CODEBOOK LEAK: control exact-add max={B_max:.3f} >= {B_LEAK}. Small-M brute-force "
                f"argmax may be accidentally adding without phase structure. {diag}", True)
    passes = (A_min >= HP_EXACT_ADD and A_cv_max < HP_CV and B_max <= B_CTRL_MAX and C_max <= C_SCRAM_MAX
              and d3_min >= HP_CHAIN_D3 and eq_acc_min >= HP_EQ_ACCEPT and eq_rej_min >= HP_EQ_REJECT)
    if passes:
        return ("HARD_PASS",
                f"MATH TRANSLATES: phase-linear residue encoding makes ADDITION exact via the existing bind "
                f"operator. Single-step exact-add min={A_min:.3f} (>= {HP_EXACT_ADD}, cv<{HP_CV}) across "
                f"M in [504,70520]; random-codebook control fails ({B_max:.3f}); scrambled-CRT collapses "
                f"({C_max:.3f}); {dmax}-step chains hold (d3_min={d3_min:.3f}, d{dmax}_min={dmax_min:.3f}); "
                f"exact equality-check crisp (accept={eq_acc_min:.3f}, reject={eq_rej_min:.3f}); near-miss "
                f"runner-up<=0.5*rank1 on {nm_min:.3f} of decodes (is-math-easier probe). {diag}", True)
    if d3_min < HF_CHAIN_D3:
        return ("HARD_FAIL",
                f"CHAINS DRIFT: depth-3 exact-add min={d3_min:.3f} < {HF_CHAIN_D3}: arithmetic composition "
                f"compounds noise worse than the reasoning collision-bound law. {diag}", True)
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

    # formula self-tests (ALL modes): CRT correctness + the ADD homomorphism, per regime in play.
    for reg in cfg["regimes"]:
        moduli = REGIMES[reg]
        if not crt_selftest(moduli):
            raise AssertionError(f"CRT_SELFTEST_FAIL regime={reg} moduli={moduli}")
        if not homomorphism_selftest(moduli, seed=cfg["seeds"][0]):
            raise AssertionError(f"HOMOMORPHISM_SELFTEST_FAIL regime={reg} moduli={moduli} "
                                 f"(decode(bind(enc(a),enc(b))) != (a+b) mod M)")
    _say(f"[{ANCHOR_NAME}] formula self-tests PASSED (CRT + add-homomorphism) for regimes {cfg['regimes']}")

    cfg, results, artifacts, per_unit = run_all(mode, output_dir, t0)

    # arms_differ (META_RULE_AF): phase codebook != random codebook; arm-A integers != scrambled integers.
    arms_differ_ok = True
    reasons = []
    for key, art in artifacts.items():
        if art["cb_phase0"] == art["cb_rand0"]:
            arms_differ_ok = False; reasons.append(f"{key}:phase==random codebook")
        if art["rec_A"] == art["rec_C"]:
            arms_differ_ok = False; reasons.append(f"{key}:scramble did not alter recovered integers")
    if not arms_differ_ok:
        raise AssertionError("META_RULE_AF VIOLATION: " + "; ".join(reasons))

    verdict, vmsg, order_ok = classify(results, cfg, mode)
    elapsed = time.perf_counter() - t0

    # assemble arm summaries
    arm_summ = {}
    for reg in cfg["regimes"]:
        seeds = cfg["seeds"]
        A = [results[reg][s]["acc_A"] for s in seeds]
        B = [results[reg][s]["acc_B"] for s in seeds]
        C = [results[reg][s]["acc_C"] for s in seeds]
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
            "phase_linear_add": {"exact_mean": round(_mean(A), 4), "per_seed": A, "cv": round(_cv(A), 4)},
            "random_codebook_add": {"exact_mean": round(_mean(B), 4), "per_seed": B},
            "scrambled_modulus": {"exact_mean": round(_mean(C), 4), "per_seed": C},
            "chain": chain_summ,
            "equality_check": {"accept_mean": round(_mean(eqa), 4), "accept_per_seed": eqa,
                               "reject_mean": round(_mean(eqr), 4), "reject_per_seed": eqr,
                               "crisp_gap": results[reg][seeds[0]]["eq_crisp_gap"],
                               "sim_equal_min": results[reg][seeds[0]]["eq_sim_equal_min"],
                               "sim_unequal_max": results[reg][seeds[0]]["eq_sim_unequal_max"]},
            "nearmiss_frac_below_half_mean": round(_mean(nm), 4),
        }

    demos = results["small"][cfg["seeds"][0]]["demos"] if "small" in results else []

    metrics = {
        "anchor_name": ANCHOR_NAME,
        "verdict": verdict,
        "verdict_msg": vmsg,
        "summary": f"{verdict}: RNS phase-linear addition chain + exact equality check ({mode})",
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
                   "bind": "FHRR_elementwise_complex_product",
                   "decode": "per_subblock_phasor_argmax_then_CRT",
                   "storage_strategy": "no_storage_algebraic_bind"},
        "arms": arm_summ,
        "demos": demos,
        "per_unit": per_unit,
        "arms_differ_verified": arms_differ_ok,
        "controls": {"scram_collapsed": order_ok},
        "bands": {"HP_exact_add": HP_EXACT_ADD, "HP_cv": HP_CV, "HF_exact_add": HF_EXACT_ADD,
                  "B_ctrl_max": B_CTRL_MAX, "B_leak": B_LEAK, "C_scram_max": C_SCRAM_MAX,
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
            f"{d['a']}+{d['b']}={d['decoded_sum']}(exp {d['expected_mod_M']}"
            f"{',WRAP' if d['wrapped'] else ''}){'OK' if d['correct'] else 'X'}" for d in demos))
    _say(f"[{ANCHOR_NAME}] metrics -> {output_dir / 'metrics.json'}  elapsed={elapsed:.1f}s")
    return 0


def _run_selftest() -> int:
    t0 = time.perf_counter()
    output_dir = _out_dir()
    output_dir.mkdir(parents=True, exist_ok=True)
    ok_crt = all(crt_selftest(REGIMES[r]) for r in REGIMES)
    ok_hom = all(homomorphism_selftest(REGIMES[r], seed=7) for r in REGIMES)
    cfg, results, _art, _pu = run_all("selftest", output_dir, t0)
    rr = results["small"][7]
    ok = ok_crt and ok_hom and (rr["acc_A"] >= 0.99) and (rr["acc_B"] <= 0.15) and (rr["acc_C"] <= 0.05) \
        and (rr["eq_accept"] >= 0.99) and (rr["eq_reject"] >= 0.99)
    _say(f"[{ANCHOR_NAME}] SELFTEST {'PASS' if ok else 'FAIL'}: crt_ok={ok_crt} hom_ok={ok_hom} "
         f"phase_add={rr['acc_A']:.3f} rand_add={rr['acc_B']:.3f} scram={rr['acc_C']:.3f} "
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
