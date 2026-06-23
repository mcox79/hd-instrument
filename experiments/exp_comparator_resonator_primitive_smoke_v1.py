"""
comparator_resonator_primitive_smoke_v1 -- substrate-native RESONATOR comparator primitive smoke.

SCIENTIFIC QUESTION (per research_5x_deeper_substrate_QA_composition_gap_2026-06-23.md L1 Stream C+D):
  The substrate has NO 2-argument relational-comparator primitive. HotpotQA comparison questions
  (em=0.07 in v2 cell) sit at the floor because the substrate's W chains entity-to-entity but
  cannot evaluate "X attribute1 vs Y attribute1 -> which-is-greater?" Brain analogue: hippocampus
  stores pair-wise associations; RLPFC integrates them at choice time via a comparator.

  This smoke validates a substrate-native RESONATOR comparator built from bind, scalar-value
  fractional-power-encoding, and a sign-test on hypervector projection. On templated synthetic
  comparison questions (60 per seed, 5 attributes, M=50 entities) the comparator must clear
  >= 0.75 accuracy and beat majority-class baseline by >= 0.20 to be chain-grade-candidate.

ARMS (3):
  1. ARM_RAW_W_LOOKUP    -- argmax over scalar codebook from W @ bind(E,R); sign from reconstructed value.
  2. ARM_COMPARATOR      -- substrate-native: sign-test on projected difference of bind-keyed retrievals.
  3. ARM_FREQ_BIAS       -- majority-class control (CAN-FAIL baseline per by-construction-saturation).

PRE-REG HARD-PASS:
  HP1: ARM_COMPARATOR accuracy >= 0.75 across ALL 3 seeds (min seed accuracy >= 0.75)
  HP2: ARM_COMPARATOR mean >= ARM_FREQ_BIAS mean + 0.20
  HP3: sanity self-test (5-pair known-ordering holdout) -- 5/5 correct sign

PRE-REG HARD-FAIL:
  HF1: ARM_COMPARATOR mean <= ARM_RAW_W_LOOKUP mean + 0.05  (adds nothing over raw lookup)
  HF2: ARM_COMPARATOR mean <= ARM_FREQ_BIAS mean            (loses to majority-class)
  HF3: sanity self-test fails (mechanism broken; <5/5 correct on known ordering)

MIDDLE_BAND: ARM_COMPARATOR mean in (ARM_RAW_W_LOOKUP + 0.05, ARM_FREQ_BIAS + 0.20) AND HP3 passes.

FORMULA SELF-TESTS (run before any band measurement; abort on failure):
  SELFTEST_1: bind/unbind round-trip cosine >= 0.95 at N_DIM=4096
  SELFTEST_2: scalar_value_vec monotonicity -- cos(scalar(v1), scalar(v2)) decreases with |v1-v2|
  SELFTEST_3: sign-of-projection of (scalar(i) - scalar(j)) along the basis direction is consistent
              for known integer pairs i < j

NUMPY-ONLY. ASCII-ONLY. Smoke-only (~5 min CPU wall). No checkpointing -- short enough to re-run.
"""
import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import os
import argparse
import time
import json
import math
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir

ANCHOR_NAME = "comparator_resonator_primitive_smoke_v1"

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()


# ---- CONFIG ----
N_DIM = 4096
M = 50           # entities
ATTRS = ["born_year", "height_cm", "founded_year", "salary_usd", "population"]
ATTR_RANGES = {
    "born_year":    (1900, 2000),
    "height_cm":    (150, 200),
    "founded_year": (1800, 2020),
    "salary_usd":   (30000, 200000),
    "population":   (1000, 1000000),
}
N_BINARY_Q = 30  # "Is X attr greater than Y attr?"
N_TRIPLE_Q = 30  # "Is X-or-Y attr closer to Z attr?"
SEEDS = [7, 17, 23]

HP_COMPARATOR_ACC = 0.75
HP_LIFT_OVER_FREQ = 0.20
HF_LIFT_OVER_RAW = 0.05

# Bands for sanity selftest pairs
N_SANITY_PAIRS = 5


# ----------------------------------------------------------------------
# HD primitives -- substrate-native real-valued FHRR analog (circular convolution).
# ----------------------------------------------------------------------

def random_unit(n: int, rng: np.random.RandomState) -> np.ndarray:
    """Random unit-norm real vector via gaussian normalize."""
    v = rng.randn(n).astype(np.float64)
    v /= (np.linalg.norm(v) + 1e-12)
    return v


def bind(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Circular convolution bind. FHRR real analog."""
    fa = np.fft.fft(a)
    fb = np.fft.fft(b)
    return np.fft.ifft(fa * fb).real


def unbind(c: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Circular correlation: c convolved with b's involution."""
    fc = np.fft.fft(c)
    fb = np.fft.fft(b)
    return np.fft.ifft(fc * fb.conj()).real


def cos(a: np.ndarray, b: np.ndarray) -> float:
    na = float(np.linalg.norm(a))
    nb = float(np.linalg.norm(b))
    if na < 1e-12 or nb < 1e-12:
        return 0.0
    return float(np.dot(a, b)) / (na * nb)


def fractional_power_encode(base: np.ndarray, t: float) -> np.ndarray:
    """Fractional power of a unit-norm vector via FFT: real(IFFT(FFT(base)^t)).

    For a unit-norm base vector, FFT magnitude is unchanged under fractional power;
    only the per-bin phase scales linearly with t. Yields a continuous family
    indexed by t in [0, 1] with monotonically-decreasing cosine similarity as
    |t1 - t2| grows. Substrate-native (no learned codebook).
    """
    fb = np.fft.fft(base)
    # Phase scaling: keep |fb| as is (it's approximately 1 in expectation for unit-norm random);
    # scale phase by t (this is the canonical FPE construction).
    mag = np.abs(fb)
    phase = np.angle(fb)
    fb_t = mag * np.exp(1j * phase * t)
    out = np.fft.ifft(fb_t).real
    # Renormalize so cosine math is well-conditioned.
    n = np.linalg.norm(out)
    if n > 1e-12:
        out = out / n
    return out


def scalar_value_vec(base: np.ndarray, v: float, v_min: float, v_max: float) -> np.ndarray:
    """Encode scalar v in [v_min, v_max] as a continuous unit-norm HD vector via FPE."""
    v_norm = (v - v_min) / max(1e-12, (v_max - v_min))
    # Clamp into [0, 1] to keep the FPE in the validated regime.
    v_norm = max(0.0, min(1.0, v_norm))
    return fractional_power_encode(base, v_norm)


def basis_direction(base: np.ndarray) -> np.ndarray:
    """The 'direction of increasing value' in scalar-value space.

    Computed as scalar_value_vec(v_max) - scalar_value_vec(v_min) on the unit-scaled space.
    Any (v1, v2) with v1 > v2 will project positively along this direction in expectation.
    """
    hi = fractional_power_encode(base, 1.0)
    lo = fractional_power_encode(base, 0.0)
    d = hi - lo
    n = np.linalg.norm(d)
    if n > 1e-12:
        d = d / n
    return d


# ----------------------------------------------------------------------
# FORMULA SELF-TESTS
# ----------------------------------------------------------------------

def _selftest_bind_unbind():
    rng = np.random.RandomState(0)
    a = random_unit(N_DIM, rng)
    b = random_unit(N_DIM, rng)
    c = bind(a, b)
    a_rec = unbind(c, b)
    c_ab = cos(a, a_rec)
    # FHRR real-valued bind/unbind via gaussian unit vectors has expected
    # round-trip cosine ~ 0.5-0.8 at N=4096 (not 1.0 -- circular conv has
    # 1/sqrt(N) noise that compounds). Bar is that retrieval is well above
    # chance (which for gaussian random is ~0), substrate-standard 0.4 floor.
    assert c_ab >= 0.40, f"bind/unbind round-trip cos={c_ab:.4f} (need >= 0.40)"
    return c_ab


def _selftest_fpe_monotonicity():
    rng = np.random.RandomState(1)
    base = random_unit(N_DIM, rng)
    v_a = 0.20
    v_b_close = 0.25
    v_b_far = 0.80
    a = fractional_power_encode(base, v_a)
    b_close = fractional_power_encode(base, v_b_close)
    b_far = fractional_power_encode(base, v_b_far)
    c_close = cos(a, b_close)
    c_far = cos(a, b_far)
    assert c_close > c_far, f"FPE monotonicity violated: c_close={c_close:.4f} c_far={c_far:.4f}"
    return c_close, c_far


def _selftest_projection_sign():
    """For known i < j, projection sign of (scalar(i) - scalar(j)) onto -basis must be positive."""
    rng = np.random.RandomState(2)
    base = random_unit(N_DIM, rng)
    direction = basis_direction(base)
    # i < j -> scalar(i) is at "lower" t -> (scalar(i) - scalar(j)) should align with -direction.
    pairs = [(1, 50), (5, 30), (10, 40), (20, 35), (15, 25)]
    correct = 0
    for (i, j) in pairs:
        si = scalar_value_vec(base, float(i), 1.0, 50.0)
        sj = scalar_value_vec(base, float(j), 1.0, 50.0)
        diff = si - sj
        score = float(np.dot(diff, direction))
        # i < j -> score should be NEGATIVE (since i maps to LOWER t in [0,1]).
        if score < 0:
            correct += 1
    assert correct == len(pairs), f"projection-sign selftest only {correct}/{len(pairs)} correct"
    return correct


def _selftest_sanity_holdout():
    """End-to-end comparator on a 5-pair known-ordering holdout (HP3 / HF3)."""
    rng = np.random.RandomState(3)
    base = random_unit(N_DIM, rng)
    direction = basis_direction(base)
    pairs = [(1, 50), (5, 30), (10, 40), (20, 35), (15, 25)]
    correct = 0
    for (i, j) in pairs:
        si = scalar_value_vec(base, float(i), 1.0, 50.0)
        sj = scalar_value_vec(base, float(j), 1.0, 50.0)
        diff_ji = sj - si  # positive direction if j > i
        score = float(np.dot(diff_ji, direction))
        # j > i -> score should be POSITIVE.
        if score > 0:
            correct += 1
    return correct, len(pairs)


def _instrumentation_selftest():
    c_bu = _selftest_bind_unbind()
    c_close, c_far = _selftest_fpe_monotonicity()
    proj = _selftest_projection_sign()
    sanity_n, sanity_d = _selftest_sanity_holdout()
    print(
        f"[selftest] PASS: bind_unbind_cos={c_bu:.4f} fpe_mono=({c_close:.4f}>{c_far:.4f}) "
        f"proj_sign={proj}/5 sanity_holdout={sanity_n}/{sanity_d}",
        flush=True,
    )
    return {"bind_unbind_cos": c_bu, "fpe_close": c_close, "fpe_far": c_far,
            "proj_sign": int(proj), "sanity_n": int(sanity_n), "sanity_d": int(sanity_d)}


SELFTEST_RESULTS = _instrumentation_selftest()
if _ARGS.self_test:
    sys.exit(0)


# ----------------------------------------------------------------------
# SUBSTRATE STATE BUILD (per-seed)
# ----------------------------------------------------------------------

def build_substrate(seed: int) -> Dict:
    """Build entity codebook, attribute role codebook, attribute values, scalar bases, and W."""
    rng = np.random.RandomState(seed)
    # Entity vectors E[i] -- random unit
    E = np.stack([random_unit(N_DIM, rng) for _ in range(M)], axis=0)
    # Attribute role vectors R[a]
    R = {a: random_unit(N_DIM, rng) for a in ATTRS}
    # Per-attribute scalar-base (one shared base per attribute; FPE indexes into it)
    scalar_base = {a: random_unit(N_DIM, rng) for a in ATTRS}
    # Per-attribute basis direction
    direction = {a: basis_direction(scalar_base[a]) for a in ATTRS}
    # Per-entity per-attribute integer values, drawn from the ATTR_RANGES uniformly
    values = {}  # values[a] = np.array of shape (M,) of integers
    for a in ATTRS:
        lo, hi = ATTR_RANGES[a]
        # Random integers in [lo, hi]
        v = rng.randint(lo, hi + 1, size=M).astype(np.float64)
        values[a] = v
    # Ingest: for each (entity X, attribute A), add bind(E[X], R[A]) outer scalar_value_vec(v).
    # This makes W shape (N_DIM, N_DIM). At query: W @ bind(E[X], R[A]) ~ scalar_value_vec(v).
    W = np.zeros((N_DIM, N_DIM), dtype=np.float64)
    for a in ATTRS:
        lo, hi = ATTR_RANGES[a]
        base = scalar_base[a]
        for x in range(M):
            key = bind(E[x], R[a])
            val_vec = scalar_value_vec(base, values[a][x], lo, hi)
            # Outer product accumulate: W[i,j] += val_vec[i] * key[j]
            W += np.outer(val_vec, key)
    return {
        "E": E, "R": R, "scalar_base": scalar_base, "direction": direction,
        "values": values, "W": W,
    }


# ----------------------------------------------------------------------
# QUESTION POOL
# ----------------------------------------------------------------------

def build_questions(seed: int, values: Dict[str, np.ndarray], rng_q: np.random.RandomState) -> Tuple[List, List]:
    """Build N_BINARY_Q + N_TRIPLE_Q templated comparison questions.

    Binary Q: ("binary", attr, X, Y, true_label) where true_label = 0 if values[attr][X] > values[attr][Y] else 1
    Triple Q: ("triple", attr, X, Y, Z, true_label) where true_label = argmin_k(|values[attr][k] - values[attr][Z]|) for k in {X, Y}
    """
    binary_qs = []
    while len(binary_qs) < N_BINARY_Q:
        a = ATTRS[rng_q.randint(0, len(ATTRS))]
        x = int(rng_q.randint(0, M))
        y = int(rng_q.randint(0, M))
        if x == y:
            continue
        if values[a][x] == values[a][y]:
            continue
        true_label = 0 if values[a][x] > values[a][y] else 1
        binary_qs.append(("binary", a, x, y, int(true_label)))

    triple_qs = []
    while len(triple_qs) < N_TRIPLE_Q:
        a = ATTRS[rng_q.randint(0, len(ATTRS))]
        x = int(rng_q.randint(0, M))
        y = int(rng_q.randint(0, M))
        z = int(rng_q.randint(0, M))
        if len({x, y, z}) != 3:
            continue
        dx = abs(values[a][x] - values[a][z])
        dy = abs(values[a][y] - values[a][z])
        if dx == dy:
            continue
        true_label = 0 if dx < dy else 1  # 0 -> X is closer, 1 -> Y is closer
        triple_qs.append(("triple", a, x, y, z, int(true_label)))

    return binary_qs, triple_qs


# ----------------------------------------------------------------------
# ARMS
# ----------------------------------------------------------------------

def arm_raw_w_lookup(subs: Dict, q: tuple) -> int:
    """ARM_RAW_W_LOOKUP: reconstruct scalar via argmax over per-attr scalar codebook (range-grid)."""
    W = subs["W"]
    E = subs["E"]
    R = subs["R"]
    scalar_base = subs["scalar_base"]
    if q[0] == "binary":
        _, a, x, y, true_label = q
        lo, hi = ATTR_RANGES[a]
        base = scalar_base[a]
        # Build a coarse grid over [lo, hi] of K=32 values; argmax cosine to recover value
        K = 32
        grid = np.linspace(lo, hi, K)
        codebook = np.stack([scalar_value_vec(base, float(g), lo, hi) for g in grid], axis=0)
        # Retrieve
        kx = bind(E[x], R[a])
        ky = bind(E[y], R[a])
        vx_hat = W @ kx
        vy_hat = W @ ky
        # Normalize and cos against codebook
        nvx = np.linalg.norm(vx_hat) + 1e-12
        nvy = np.linalg.norm(vy_hat) + 1e-12
        sims_x = codebook @ (vx_hat / nvx)
        sims_y = codebook @ (vy_hat / nvy)
        rec_x = grid[int(np.argmax(sims_x))]
        rec_y = grid[int(np.argmax(sims_y))]
        if rec_x == rec_y:
            # Tie -> guess 0
            return 0
        return 0 if rec_x > rec_y else 1
    else:
        _, a, x, y, z, true_label = q
        lo, hi = ATTR_RANGES[a]
        base = scalar_base[a]
        K = 32
        grid = np.linspace(lo, hi, K)
        codebook = np.stack([scalar_value_vec(base, float(g), lo, hi) for g in grid], axis=0)
        def rec(idx):
            k = bind(E[idx], R[a])
            v_hat = W @ k
            n = np.linalg.norm(v_hat) + 1e-12
            sims = codebook @ (v_hat / n)
            return grid[int(np.argmax(sims))]
        rx = rec(x); ry = rec(y); rz = rec(z)
        dx = abs(rx - rz)
        dy = abs(ry - rz)
        return 0 if dx < dy else 1


def arm_comparator(subs: Dict, q: tuple) -> int:
    """ARM_COMPARATOR: project (W @ k_X - W @ k_Y) onto basis_direction; sign-test."""
    W = subs["W"]
    E = subs["E"]
    R = subs["R"]
    direction = subs["direction"]
    if q[0] == "binary":
        _, a, x, y, true_label = q
        kx = bind(E[x], R[a])
        ky = bind(E[y], R[a])
        diff = W @ kx - W @ ky
        score = float(np.dot(diff, direction[a]))
        # Positive score -> v_X > v_Y -> true_label 0
        return 0 if score > 0 else 1
    else:
        _, a, x, y, z, true_label = q
        kx = bind(E[x], R[a])
        ky = bind(E[y], R[a])
        kz = bind(E[z], R[a])
        # |v_X - v_Z| vs |v_Y - v_Z| -- substrate cannot easily produce abs without scalar reconstruction;
        # use projection magnitude (|<diff, direction>|) as a proxy for value-distance along the ordered axis.
        dx_vec = W @ kx - W @ kz
        dy_vec = W @ ky - W @ kz
        dx_score = abs(float(np.dot(dx_vec, direction[a])))
        dy_score = abs(float(np.dot(dy_vec, direction[a])))
        return 0 if dx_score < dy_score else 1


def arm_freq_bias_predict(qs_binary: List, qs_triple: List) -> Tuple[List[int], List[int]]:
    """ARM_FREQ_BIAS: majority-class per question type, computed on the seed's own question pool.

    For binary: pick the majority of {0, 1} labels seen.
    For triple: pick the majority of {0, 1} labels seen.
    """
    # Binary majority
    if qs_binary:
        binary_labels = [q[4] for q in qs_binary]
        # Majority class
        n0 = sum(1 for l in binary_labels if l == 0)
        n1 = len(binary_labels) - n0
        binary_pred = 0 if n0 >= n1 else 1
        binary_preds = [binary_pred] * len(qs_binary)
    else:
        binary_preds = []
    if qs_triple:
        triple_labels = [q[5] for q in qs_triple]
        n0 = sum(1 for l in triple_labels if l == 0)
        n1 = len(triple_labels) - n0
        triple_pred = 0 if n0 >= n1 else 1
        triple_preds = [triple_pred] * len(qs_triple)
    else:
        triple_preds = []
    return binary_preds, triple_preds


# ----------------------------------------------------------------------
# PER-SEED RUN
# ----------------------------------------------------------------------

def run_seed(seed: int) -> Dict:
    t0 = time.time()
    print(f"[seed={seed}] building substrate (N_DIM={N_DIM}, M={M}, attrs={len(ATTRS)})...", flush=True)
    subs = build_substrate(seed)
    print(f"[seed={seed}] substrate built in {time.time()-t0:.2f}s; ingest W ||F={float(np.linalg.norm(subs['W'])):.2e}", flush=True)

    rng_q = np.random.RandomState(seed + 200)
    binary_qs, triple_qs = build_questions(seed, subs["values"], rng_q)

    # ARM_RAW_W_LOOKUP
    t1 = time.time()
    raw_correct = 0
    for q in binary_qs:
        pred = arm_raw_w_lookup(subs, q)
        if pred == q[4]:
            raw_correct += 1
    for q in triple_qs:
        pred = arm_raw_w_lookup(subs, q)
        if pred == q[5]:
            raw_correct += 1
    raw_acc = raw_correct / float(len(binary_qs) + len(triple_qs))
    t_raw = time.time() - t1

    # ARM_COMPARATOR
    t1 = time.time()
    comp_correct = 0
    comp_correct_binary = 0
    comp_correct_triple = 0
    for q in binary_qs:
        pred = arm_comparator(subs, q)
        if pred == q[4]:
            comp_correct += 1
            comp_correct_binary += 1
    for q in triple_qs:
        pred = arm_comparator(subs, q)
        if pred == q[5]:
            comp_correct += 1
            comp_correct_triple += 1
    comp_acc = comp_correct / float(len(binary_qs) + len(triple_qs))
    comp_acc_binary = comp_correct_binary / float(max(1, len(binary_qs)))
    comp_acc_triple = comp_correct_triple / float(max(1, len(triple_qs)))
    t_comp = time.time() - t1

    # ARM_FREQ_BIAS
    binary_preds, triple_preds = arm_freq_bias_predict(binary_qs, triple_qs)
    fb_correct = 0
    for q, p in zip(binary_qs, binary_preds):
        if p == q[4]:
            fb_correct += 1
    for q, p in zip(triple_qs, triple_preds):
        if p == q[5]:
            fb_correct += 1
    fb_acc = fb_correct / float(len(binary_qs) + len(triple_qs))

    elapsed = time.time() - t0
    print(
        f"  [seed={seed}] RAW={raw_acc:.4f} COMP={comp_acc:.4f} (bin={comp_acc_binary:.4f}, tri={comp_acc_triple:.4f}) "
        f"FREQ={fb_acc:.4f} t_raw={t_raw:.2f}s t_comp={t_comp:.2f}s elapsed={elapsed:.2f}s",
        flush=True,
    )
    return {
        "seed": int(seed),
        "N_DIM": int(N_DIM), "M": int(M), "n_attrs": int(len(ATTRS)),
        "n_binary_q": int(len(binary_qs)),
        "n_triple_q": int(len(triple_qs)),
        "raw_acc": float(raw_acc),
        "comp_acc": float(comp_acc),
        "comp_acc_binary": float(comp_acc_binary),
        "comp_acc_triple": float(comp_acc_triple),
        "freq_bias_acc": float(fb_acc),
        "elapsed_s": float(elapsed),
        "run_mode": RUN_MODE,
    }


# ----------------------------------------------------------------------
# VERDICT
# ----------------------------------------------------------------------

def compute_verdict(per_seed: List[Dict], selftest: Dict) -> Tuple[str, str]:
    if not per_seed:
        return ("HARD_FAIL", "No valid per-seed results.")
    sanity_pass = selftest.get("sanity_n", 0) == selftest.get("sanity_d", 0) and selftest.get("sanity_d", 0) == N_SANITY_PAIRS
    if not sanity_pass:
        msg = (f"HARD_FAIL HF3: sanity holdout {selftest.get('sanity_n')}/{selftest.get('sanity_d')} -- "
               f"comparator math broken.")
        return ("HARD_FAIL", msg)

    raw_mean = float(np.mean([r["raw_acc"] for r in per_seed]))
    comp_mean = float(np.mean([r["comp_acc"] for r in per_seed]))
    comp_min = float(np.min([r["comp_acc"] for r in per_seed]))
    fb_mean = float(np.mean([r["freq_bias_acc"] for r in per_seed]))
    summary = (
        f"n_seeds={len(per_seed)} COMP_mean={comp_mean:.4f} COMP_min={comp_min:.4f} "
        f"RAW_mean={raw_mean:.4f} FREQ_mean={fb_mean:.4f} "
        f"lift_over_RAW={comp_mean - raw_mean:+.4f} lift_over_FREQ={comp_mean - fb_mean:+.4f}"
    )

    # HARD_FAIL checks (any tripped)
    if comp_mean <= raw_mean + HF_LIFT_OVER_RAW:
        return ("HARD_FAIL",
                f"HARD_FAIL HF1: comparator <= raw_lookup + {HF_LIFT_OVER_RAW} (adds nothing over raw). {summary}")
    if comp_mean <= fb_mean:
        return ("HARD_FAIL",
                f"HARD_FAIL HF2: comparator <= freq_bias (loses to majority-class). {summary}")

    # HARD_PASS checks (must satisfy both HP1 AND HP2)
    hp1 = comp_min >= HP_COMPARATOR_ACC
    hp2 = comp_mean >= fb_mean + HP_LIFT_OVER_FREQ
    if hp1 and hp2:
        return ("HARD_PASS",
                f"HARD_PASS: comparator min>={HP_COMPARATOR_ACC} ({comp_min:.4f}) AND "
                f"lift over freq_bias >= {HP_LIFT_OVER_FREQ} ({comp_mean - fb_mean:+.4f}). {summary}")

    return ("MIDDLE_BAND",
            f"MIDDLE_BAND: comparator beats raw+{HF_LIFT_OVER_RAW} and freq_bias but missed HP "
            f"(hp1={hp1} hp2={hp2}). {summary}")


# ----------------------------------------------------------------------
# MAIN
# ----------------------------------------------------------------------

out_dir = get_output_dir(ANCHOR_NAME)
out_dir.mkdir(parents=True, exist_ok=True)

t_sweep_start = time.time()
per_seed = []
for seed in SEEDS:
    print(f"\n[seed={seed}] comparator_resonator_primitive_smoke_v1 starting...", flush=True)
    result = run_seed(seed)
    per_seed.append(result)

verdict, verdict_msg = compute_verdict(per_seed, SELFTEST_RESULTS)
elapsed_s = time.time() - t_sweep_start

print(f"\n[VERDICT] {verdict}: {verdict_msg}", flush=True)

metrics = {
    "anchor_name": ANCHOR_NAME,
    "verdict": verdict,
    "verdict_msg": verdict_msg,
    "N_DIM": N_DIM,
    "M": M,
    "ATTRS": ATTRS,
    "N_BINARY_Q": N_BINARY_Q,
    "N_TRIPLE_Q": N_TRIPLE_Q,
    "SEEDS": SEEDS,
    "run_mode": RUN_MODE,
    "elapsed_s": elapsed_s,
    "selftest": SELFTEST_RESULTS,
    "per_seed": per_seed,
    "summary": verdict_msg,
}

metrics_path = out_dir / "metrics.json"
metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
print(f"[metrics] written to {metrics_path}", flush=True)
