"""schema_bundle_structural_transfer_v1 -- FIRST genuine schema-formation test.

SCIENTIFIC QUESTION:
  Continual-learning drills proved forgetting-prevention is DONE (segregated
  dual-W + one-way replay: forgetting 0.678 -> 0.011) but STRUCTURAL TRANSFER
  stayed at EXACTLY 0.000 across ~80 landed CL-adjacent cells. Schema formation
  (generalize to a NOVEL, never-seen entity pair sharing a learned relational
  structure) is a SEPARATE, untouched mechanism. Does BUNDLING many episodes of
  one relation-type into a segregated one-way-fed schema store produce
  above-random completion on NOVEL same-relation entity pairs?

MECHANISM (author revision of the research draft -- see below):
  The research draft proposed bundling role-filler episodes
    S_R = bundle_i [ bind(role_subj, A_i) + bind(role_obj, B_i) ]
  and "reading against the schema store". BUT unbinding role_obj from that
  bundle returns the C-INDEPENDENT mean object (ignores the novel subject) and
  cannot do subject-conditional retrieval. The correct VSA primitive for
  novel-subject -> object structural transfer is the HOLISTIC / ANALOGICAL
  MAPPING (Kanerva "What is the Dollar of Mexico?" 2010; Plate holistic
  mapping): bundle the per-pair transforms into ONE segregated schema vector
    M_R = mean_i bind(B_i, inv(A_i))                (one-way-fed schema store)
  then for a NOVEL entity C bound as subject
    D_hat = bind(C, M_R)                            (read against schema store)
    prediction = argmax_o Re<o, D_hat>              (cleanup vs object codebook)
  This IS the segregated one-way store: M_R is written ONCE from episodes and
  never writes back; queries only READ it. This is the mechanism-class the
  concept-query surfaced (Random-Features-Hopfield "generalization phase",
  arXiv 2407.05658) and the cognitive prototype-abstraction (Posner-Keele).

WHY SYNTHETIC (deliberate author decision; research autonomy):
  Structural transfer to a novel entity is only POSSIBLE if entities carry
  SHARED LATENT STRUCTURE that a relation systematically transforms. Real KG
  entity atoms encoded as random / char-trigram vectors have NO systematic
  subject->object transform (Obama*inv(USA) and Merkel*inv(Germany) are
  unrelated random vectors) -> transfer impossible BY CONSTRUCTION -> an
  UNINFORMATIVE HARD_FAIL that tests the ENCODER, not the schema MECHANISM.
  To ISOLATE the bundling-schema mechanism we use a CLEAN synthetic generator
  with a DIAL-ABLE amount of shared structure (per feedback_clean_encoder_tests
  + feedback_smoke_clean_synthetic_data_not_substrate_state). A real-corpus
  follow-up (does the substrate's actual entity encoding CARRY such structure?)
  is the explicit NEXT cell, not this one. This cell answers: GIVEN entities
  with learnable shared structure, does bundle-schema extract it and generalize
  to NOVEL entities above random, with a clean genuine-structure discriminator?

GENERATOR (FHRR phasors, N_DIM=4096):
  K object classes; K subject-cluster prototypes MU[k] (random phasors);
  object codebook O[k] (random phasors, the K answers). A subject instance of
  class k is a PHASE-JITTERED copy of MU[k] (jitter sigma rad) -- so any single
  subject only WEAKLY signals its class (per-subject correlation with prototype
  ~ exp(-sigma^2/2)); the SCHEMA (bundle over many training subjects) is what
  sharpens the class->object mapping. Relation R maps a class-k subject to
  object o_k. Training: M pairs, M/K distinct instances per class. Held-out
  test: FRESH jittered novel subjects never in training (genuine generalization,
  no leakage).

ARMS (all paired: SAME MU/O/subjects/seed; only the manipulation differs):
  ARM_REAL          -- true class->object pairing. PRIMARY. HP gates apply.
  ARM_SHUFFLED      -- object labels of training pairs randomly permuted
                       (breaks class->object correspondence). Genuine-structure
                       discriminator: must collapse to ~chance. CONTROL.
  ARM_MEAN_OBJECT   -- C-INDEPENDENT readout D_hat = M_R (no bind with C).
                       Shows the transfer is SUBJECT-CONDITIONAL, not "return
                       the popular object". CONTROL. Expected ~chance.

SWEEP:  M in {10, 30, 50, 100, 200} = episodes bundled into the schema
        (per-class redundancy M/K in {1,3,5,10,20}). This is the SNR / sample
        -size axis (research Prediction 3 null-bracket at M/K=1).

PRE-REGISTERED BANDS (LOCKED before smoke; operating point M_OP=200):
  random_baseline = 1/K = 0.100 (THEORETICAL; K distinct object classes).
  HARD_PASS  (ARM_REAL only): real_gain(M200) >= 0.30 AND cv_real(M200) <= 0.30
             AND shuffled_gain(M200) <= 0.05 AND (real-mean_object)(M200) >= 0.20
  HARD_FAIL  (ARM_REAL): real_gain(M200) <= 0.05 (bundling extracts no usable
             structure).
  MIDDLE_BAND: 0.05 < real_gain(M200) < 0.30, or partial gates -> sweep M.
  SUSPICION demote-to-MIDDLE: real_gain(M10) >= 0.30 (transfer already maxed at
             1 example/class => codebook artifact, not sample-driven schema).
  Sanity rails: FHRR bind-roundtrip recall >= 0.90; shuffled in (0.05, 0.95)
             and real < 0.95 (baseline_in_band; not saturated).

HP_SCOPE: HARD_PASS/HARD_FAIL gates apply to ARM_REAL ONLY. ARM_SHUFFLED and
  ARM_MEAN_OBJECT are controls; they must NOT clear HP (they are expected at
  ~chance) and inherit no chain-grade gate.

PROTOTYPE-MEASURED band (complex128 prototype, N=4096 K=10 sigma=2.0, 5 seeds;
  MEASURED@scratchpad proto_confirm.py; smoke re-measures at complex64):
  M= 10 real=0.189 shuf=0.099   gain=+0.089  -> NULL/low  (null-bracket fires)
  M= 30 real=0.319 shuf=0.096   gain=+0.219  -> MIDDLE
  M= 50 real=0.394 shuf=0.102   gain=+0.294  -> MIDDLE
  M=100 real=0.512 shuf=0.083   gain=+0.412  -> HARD_PASS
  M=200 real=0.690 shuf=0.104   gain=+0.590  -> HARD_PASS (cv=0.069, not sat)
  discriminating_fraction (M-points in [0.30,0.70]) = 4/5 = 0.80 >= 0.30.

COMPUTE ARCHITECTURE:
  Class: (b) sequential-CPU with justification. Substrate primitives are
  elementwise complex mul (bind), vector sum (bundle), K x N cleanup matmul
  (K=10 tiny). Full run measured ~8-15s wall (3 seeds x 5 M x 3 arms). Per-unit
  wall << 10s and total < 60s -> below the GPU-batching threshold; sequential
  CPU is the correct resource. No N x N matrices anywhere (unlike c3 Hopfield).
  Storage strategy: bundled -- INTENTIONAL and the object under test (schema =
  bundled prototype); NOT a chained-composition cell, so META_STORAGE sharded-
  default does not apply (bundle IS the mechanism being validated).

WHAT_THIS_DOES_NOT_SHOW:
  - NOT a vs-LLM comparison (constructive schema-mechanism build).
  - NOT a claim that REAL KG encodings carry the requisite structure (explicit
    follow-up cell). This isolates the MECHANISM given structure exists.
  - NOT multi-relation coexistence (that is anchor #2, conditional on this).
  - NOT a language / BPC test; pure vector algebra, ZERO LLM calls.

FORMULA SELF-TESTS (import time):
  1. FHRR bind/unbind roundtrip: unbind(bind(a,b), a) ~ b, cosine >= 0.90.
  2. Holistic-map sanity: with a CLEAN shared transform (sigma=0), novel-C
     transfer == 1.0 (mechanism recovers a noise-free schema).
  3. Cleanup argmax picks the true object on a clean codebook.
  4. Shuffled control on the sigma=0 clean case collapses to ~1/K.

ASCII-only. Per-seed checkpoint (_seed_checkpoint). Atomic tmp+replace metrics.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import os
import argparse
import json
import time
import hashlib
import platform
import traceback
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (
    get_output_dir, resumable_seeds, write_partial, aggregate_partials,
)

# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; ARMS-MUST-DIFFER hash-test)
# - final_metrics_atomicity = tmp_replace (META_RULE_AH)
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb n/a (argmax transfer); chance floor 1/K stated; reachability declared
# - baseline_in_band at smoke (META_RULE_AG; 0.05 < shuffled < 0.95, real < 0.95)
# - discriminator survives scale (SMOKE runs at FULL N=4096 -- same regime)
# - HARD_PASS strictly above floor (gain 0.30; measured 0.59 at M200, margin 0.29)
# - HP_SCOPE: HP gates apply to ARM_REAL only
# - cardinality_ok (META_RULE_H; EXPECTED_N_UNITS = seeds*M*arms)
# - per-unit failure-class instrumentation (META_RULE_J; no bare except)
# - calibration_check = default_ok_for_this_regime (band from prototype)
# - all numbers tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@ (META_RULE_AC)

ANCHOR_NAME = "schema_bundle_structural_transfer_v1"

# ----------------------------------------------------------------------------
# Argparse + run-mode
# ----------------------------------------------------------------------------
_P = argparse.ArgumentParser()
_P.add_argument("--smoke", action="store_true")
_P.add_argument("--self-test", action="store_true", dest="self_test")
_ARGS, _ = _P.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = "_smoke" in _HDLAB_EXP_NAME.lower()
RUN_MODE = "smoke" if (_ARGS.smoke or _ARGS.self_test or _NAME_SAYS_SMOKE) \
    else os.environ.get("HDLAB_RUN_MODE", "full")

# ----------------------------------------------------------------------------
# Config (SMOKE runs at FULL N -- discriminator-survives-scale; N=4096 is the
# discriminating regime; N>=8192 saturates. Only seed count / test size shrink.)
# ----------------------------------------------------------------------------
N_DIM = 4096
K = 10                              # object classes / subject clusters
SIGMA = 2.0                         # subject phase-jitter (rad) around prototype
M_SWEEP = [10, 30, 50, 100, 200]   # episodes bundled; per-class = M/K
M_OP = 200                         # operating point for primary HP gates
ARMS = ["ARM_REAL", "ARM_SHUFFLED", "ARM_MEAN_OBJECT"]
PRIMARY_ARM = "ARM_REAL"
CONTROL_ARMS = ["ARM_SHUFFLED", "ARM_MEAN_OBJECT"]
RANDOM_BASELINE = 1.0 / K          # THEORETICAL chance = 0.100

if RUN_MODE == "smoke":
    SEEDS = [7, 13]                # 2-seed discriminator-preview at FULL N
    N_TEST_PER = 20
else:
    SEEDS = [7, 13, 19]
    N_TEST_PER = 20

# Pre-reg bands (locked)
HP_REAL_GAIN_MIN = 0.30            # real - chance at M_OP
HP_CV_MAX = 0.30
HP_SHUF_GAIN_MAX = 0.05            # shuffled - chance at M_OP (control stays low)
HP_REAL_MINUS_CIND_MIN = 0.20      # subject-conditional discriminator at M_OP
HF_REAL_GAIN_MAX = 0.05            # real - chance at M_OP => HARD_FAIL
SUSPICION_M10_GAIN = 0.30          # too-easy-at-1-example -> demote
BIND_ROUNDTRIP_MIN = 0.90
BASELINE_LO, BASELINE_HI = 0.05, 0.95

# Cardinality (META_RULE_H)
EXPECTED_N_UNITS = len(SEEDS) * len(M_SWEEP) * len(ARMS)

# ----------------------------------------------------------------------------
# FHRR primitives (complex64 phasors)
# ----------------------------------------------------------------------------
def rand_phasor(shape, rng: np.random.RandomState) -> np.ndarray:
    ang = rng.uniform(-np.pi, np.pi, size=shape).astype(np.float32)
    return np.exp(1j * ang).astype(np.complex64)


def bind(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """FHRR bind = elementwise complex multiply."""
    return (a * b).astype(np.complex64)


def unbind(c: np.ndarray, a: np.ndarray) -> np.ndarray:
    """FHRR unbind = multiply by conjugate (inverse of unit phasor)."""
    return (c * np.conj(a)).astype(np.complex64)


def cos_c(x: np.ndarray, y: np.ndarray) -> float:
    """Normalized Hermitian cosine (real part) between two complex vectors."""
    num = float(np.vdot(y, x).real)          # Re<y, x>
    den = float(np.linalg.norm(x) * np.linalg.norm(y)) + 1e-12
    return num / den


def jitter_subjects(mu: np.ndarray, sigma: float, n: int,
                    rng: np.random.RandomState) -> np.ndarray:
    """n phase-jittered phasor instances around prototype phasor mu (shape N)."""
    ang0 = np.angle(mu)[None, :]
    ang = ang0 + sigma * rng.standard_normal((n, mu.shape[0])).astype(np.float32)
    return np.exp(1j * ang).astype(np.complex64)


def cleanup_argmax(dhat: np.ndarray, O: np.ndarray) -> int:
    """Argmax real cosine of dhat (N,) against object codebook O (K,N)."""
    sims = (O @ np.conj(dhat)).real          # (K,)
    return int(np.argmax(sims))


# ----------------------------------------------------------------------------
# Core: one (seed, M) generation + all 3 arm transfers
# ----------------------------------------------------------------------------
def build_and_eval(N: int, K_: int, sigma: float, M: int, n_test_per: int,
                   seed: int) -> Dict[str, float]:
    """Returns per-arm transfer accuracy for one (seed, M) cell.

    Paired: identical MU / O / training subjects / novel subjects across arms;
    only the schema-construction manipulation differs.
    """
    assert M % K_ == 0, f"M={M} must be divisible by K={K_}"
    rng = np.random.RandomState(seed)
    MU = rand_phasor((K_, N), rng)           # subject cluster prototypes
    O = rand_phasor((K_, N), rng)            # object codebook (answers)

    per = M // K_
    labels = np.repeat(np.arange(K_), per)   # class label per training subject
    Mtot = labels.shape[0]
    A = np.zeros((Mtot, N), dtype=np.complex64)
    for k in range(K_):
        A[k * per:(k + 1) * per] = jitter_subjects(MU[k], sigma, per, rng)

    # object phasor per training pair (REAL pairing)
    obj_labels_real = labels.copy()
    # SHUFFLED pairing (paired control -- same subjects, permuted objects)
    obj_labels_shuf = rng.permutation(labels.copy())

    B_real = O[obj_labels_real]
    B_shuf = O[obj_labels_shuf]

    # Holistic map schema (one-way-fed store): mean_i bind(B_i, inv(A_i))
    inv_A = np.conj(A)
    M_real = (B_real * inv_A).mean(axis=0).astype(np.complex64)
    M_shuf = (B_shuf * inv_A).mean(axis=0).astype(np.complex64)

    # Held-out NOVEL subjects (fresh jitter; never in training A)
    correct = {a: 0 for a in ARMS}
    total = 0
    for k in range(K_):
        C = jitter_subjects(MU[k], sigma, n_test_per, rng)   # (n_test_per, N)
        Dhat_real = C * M_real[None, :]
        Dhat_shuf = C * M_shuf[None, :]
        for j in range(n_test_per):
            if cleanup_argmax(Dhat_real[j], O) == k:
                correct["ARM_REAL"] += 1
            if cleanup_argmax(Dhat_shuf[j], O) == k:
                correct["ARM_SHUFFLED"] += 1
            # C-INDEPENDENT readout: D_hat = M_real (ignores subject C)
            if cleanup_argmax(M_real, O) == k:
                correct["ARM_MEAN_OBJECT"] += 1
            total += 1
    return {a: correct[a] / total for a in ARMS}


def run_seed(seed: int) -> Dict:
    """All M-sweep x 3 arms for one seed. Per-unit failure-class instrumented."""
    t0 = time.time()
    per_unit: Dict[str, Dict] = {}
    fatal = False
    for M in M_SWEEP:
        try:
            accs = build_and_eval(N_DIM, K, SIGMA, M, N_TEST_PER, seed)
        except Exception as e:                # META_RULE_J: specific record + halt seed
            fatal = True
            for a in ARMS:
                per_unit[f"M{M}_{a}"] = {
                    "seed": seed, "M": M, "arm": a, "acc": None,
                    "failure_class": type(e).__name__,
                    "failure_msg": str(e)[:300],
                }
            print(f"  [seed={seed} M={M}] FAILED {type(e).__name__}: {e}", flush=True)
            break
        for a in ARMS:
            per_unit[f"M{M}_{a}"] = {
                "seed": seed, "M": M, "arm": a, "acc": float(accs[a]),
                "failure_class": None,
            }
        print(f"  [seed={seed} M={M:3d}] "
              f"real={accs['ARM_REAL']:.3f} shuf={accs['ARM_SHUFFLED']:.3f} "
              f"cind={accs['ARM_MEAN_OBJECT']:.3f}", flush=True)
    return {
        "seed": seed,
        "N": N_DIM,
        "K": K,
        "sigma": SIGMA,
        "run_mode": RUN_MODE,
        "config_version": f"ANCHOR={ANCHOR_NAME},N={N_DIM},K={K},sigma={SIGMA}",
        "per_unit": per_unit,
        "fatal": fatal,
        "elapsed_s": time.time() - t0,
    }


# ----------------------------------------------------------------------------
# Aggregate + verdict
# ----------------------------------------------------------------------------
def aggregate(per_seed: Dict) -> Dict:
    """Return {arm: {M: {mean, std, cv, n}}} + flat unit count."""
    # collect accs[arm][M] = list over seeds
    acc: Dict[str, Dict[int, List[float]]] = {a: {M: [] for M in M_SWEEP} for a in ARMS}
    n_units = 0
    n_units_failed = 0
    for sd in per_seed.values():
        pu = sd.get("per_unit", {})
        for key, rec in pu.items():
            n_units += 1
            if rec.get("acc") is None:
                n_units_failed += 1
                continue
            acc[rec["arm"]][rec["M"]].append(float(rec["acc"]))
    out: Dict[str, Dict] = {}
    for a in ARMS:
        out[a] = {}
        for M in M_SWEEP:
            vals = acc[a][M]
            n = len(vals)
            mean = float(np.mean(vals)) if n else float("nan")
            std = float(np.std(vals, ddof=1)) if n > 1 else 0.0
            cv = (std / abs(mean)) if (n > 1 and abs(mean) > 1e-9) else 0.0
            out[a][M] = {"mean": mean, "std": std, "cv": cv, "n": n,
                         "gain": mean - RANDOM_BASELINE if n else float("nan")}
    return {"per_arm": out, "n_units": n_units, "n_units_failed": n_units_failed}


def compute_verdict(agg: Dict, arms_differ_ok: bool, bind_roundtrip: float,
                    n_units: int) -> Tuple[str, str, Dict]:
    pa = agg["per_arm"]
    real = pa["ARM_REAL"]
    shuf = pa["ARM_SHUFFLED"]
    cind = pa["ARM_MEAN_OBJECT"]

    real_op = real[M_OP]
    shuf_op = shuf[M_OP]
    cind_op = cind[M_OP]
    real_gain_op = real_op["gain"]
    shuf_gain_op = shuf_op["gain"]
    real_cv_op = real_op["cv"]
    real_minus_cind = real_op["mean"] - cind_op["mean"]
    real_gain_m10 = real[10]["gain"]

    diag = {
        "M_OP": M_OP,
        "random_baseline": RANDOM_BASELINE,
        "real_acc_M_OP": real_op["mean"],
        "real_gain_M_OP": real_gain_op,
        "real_cv_M_OP": real_cv_op,
        "shuf_acc_M_OP": shuf_op["mean"],
        "shuf_gain_M_OP": shuf_gain_op,
        "cind_acc_M_OP": cind_op["mean"],
        "real_minus_cind_M_OP": real_minus_cind,
        "real_gain_M10": real_gain_m10,
        "bind_roundtrip": bind_roundtrip,
        "arms_differ_ok": arms_differ_ok,
        "n_units": n_units,
        "expected_n_units": EXPECTED_N_UNITS,
        "real_curve": {str(M): real[M]["mean"] for M in M_SWEEP},
        "shuf_curve": {str(M): shuf[M]["mean"] for M in M_SWEEP},
        "cind_curve": {str(M): cind[M]["mean"] for M in M_SWEEP},
    }

    # Cardinality gate (META_RULE_H)
    if n_units < EXPECTED_N_UNITS:
        return ("HARD_FAIL",
                f"HARD_FAIL_CARDINALITY_BREACH_META_RULE_H: n_units={n_units} < "
                f"expected={EXPECTED_N_UNITS} (seeds*M*arms). Missing units.",
                diag)

    # ARMS-MUST-DIFFER (META_RULE_AF)
    if not arms_differ_ok:
        return ("HARD_FAIL",
                "META_RULE_AF_VIOLATION: arm outputs bit-identical; arm-impl bug.",
                diag)

    # Sanity rail: FHRR primitive works
    if not (bind_roundtrip >= BIND_ROUNDTRIP_MIN):
        return ("HARD_FAIL",
                f"SANITY_RAIL_BIND: bind-roundtrip={bind_roundtrip:.3f} < "
                f"{BIND_ROUNDTRIP_MIN}; FHRR primitive broken.", diag)

    # baseline_in_band (META_RULE_AG): shuffled must be a low-not-saturated
    # reference; real must not be saturated (else by-construction-easy).
    if not (BASELINE_LO < shuf_op["mean"] < BASELINE_HI):
        return ("HARD_FAIL",
                f"BASELINE_OUT_OF_BAND: shuffled_M_OP={shuf_op['mean']:.3f} "
                f"outside ({BASELINE_LO},{BASELINE_HI}); control not a valid floor.",
                diag)
    if real_op["mean"] >= BASELINE_HI:
        return ("MIDDLE_BAND",
                f"REAL_SATURATED: real_M_OP={real_op['mean']:.3f} >= {BASELINE_HI}; "
                f"by-construction-easy regime, not a measured schema gradient.",
                diag)

    summ = (f"real_gain(M{M_OP})={real_gain_op:+.3f} cv={real_cv_op:.3f} "
            f"shuf_gain={shuf_gain_op:+.3f} real-cind={real_minus_cind:+.3f} "
            f"real_gain(M10)={real_gain_m10:+.3f} "
            f"| curve real={diag['real_curve']} shuf={diag['shuf_curve']}")

    # HARD_FAIL: no usable structure at operating point
    if real_gain_op <= HF_REAL_GAIN_MAX:
        return ("HARD_FAIL",
                f"HARD_FAIL_NO_TRANSFER: real_gain(M{M_OP})={real_gain_op:+.3f} "
                f"<= {HF_REAL_GAIN_MAX}; bundling extracts no usable structure. {summ}",
                diag)

    # SUSPICION: transfer already maxed at 1 example/class -> codebook artifact
    if real_gain_m10 >= SUSPICION_M10_GAIN:
        return ("MIDDLE_BAND",
                f"CODEBOOK_ARTIFACT_SUSPECTED: real_gain(M10)={real_gain_m10:+.3f} "
                f">= {SUSPICION_M10_GAIN}; transfer not sample-size-driven "
                f"(schema fires at 1 example/class). Demote. {summ}", diag)

    # HARD_PASS (ARM_REAL only)
    hp_a = real_gain_op >= HP_REAL_GAIN_MIN
    hp_b = real_cv_op <= HP_CV_MAX
    hp_c = shuf_gain_op <= HP_SHUF_GAIN_MAX
    hp_d = real_minus_cind >= HP_REAL_MINUS_CIND_MIN
    if hp_a and hp_b and hp_c and hp_d:
        return ("HARD_PASS",
                f"HARD_PASS_SCHEMA_TRANSFER: bundle-schema generalizes to novel "
                f"same-relation entities above random. {summ}", diag)

    # MIDDLE band: real signal but not full gates
    reasons = []
    if not hp_a: reasons.append(f"real_gain={real_gain_op:+.3f}<{HP_REAL_GAIN_MIN}")
    if not hp_b: reasons.append(f"cv={real_cv_op:.3f}>{HP_CV_MAX}")
    if not hp_c: reasons.append(f"shuf_gain={shuf_gain_op:+.3f}>{HP_SHUF_GAIN_MAX}")
    if not hp_d: reasons.append(f"real-cind={real_minus_cind:+.3f}<{HP_REAL_MINUS_CIND_MIN}")
    return ("MIDDLE_BAND",
            f"MIDDLE_BAND_PARTIAL: real transfer present but not full HP: "
            + "; ".join(reasons) + f". Sweep M. {summ}", diag)


# ----------------------------------------------------------------------------
# arms-differ hash (META_RULE_AF)
# ----------------------------------------------------------------------------
def arms_differ_check(seed: int) -> Tuple[bool, Dict[str, str]]:
    """Build per-arm novel-prediction vectors at M_OP and hash; assert differ."""
    rng = np.random.RandomState(seed)
    MU = rand_phasor((K, N_DIM), rng)
    O = rand_phasor((K, N_DIM), rng)
    per = M_OP // K
    labels = np.repeat(np.arange(K), per)
    A = np.zeros((labels.shape[0], N_DIM), dtype=np.complex64)
    for k in range(K):
        A[k * per:(k + 1) * per] = jitter_subjects(MU[k], SIGMA, per, rng)
    inv_A = np.conj(A)
    M_real = (O[labels] * inv_A).mean(axis=0).astype(np.complex64)
    M_shuf = (O[rng.permutation(labels.copy())] * inv_A).mean(axis=0).astype(np.complex64)
    preds = {a: [] for a in ARMS}
    for k in range(K):
        C = jitter_subjects(MU[k], SIGMA, 10, rng)
        for j in range(10):
            preds["ARM_REAL"].append(cleanup_argmax(C[j] * M_real, O))
            preds["ARM_SHUFFLED"].append(cleanup_argmax(C[j] * M_shuf, O))
            preds["ARM_MEAN_OBJECT"].append(cleanup_argmax(M_real, O))
    digests = {a: hashlib.sha256(np.array(preds[a], dtype=np.int64).tobytes()).hexdigest()
               for a in ARMS}
    ok = len(set(digests.values())) == len(ARMS)
    return ok, digests


# ----------------------------------------------------------------------------
# Formula self-tests (import time)
# ----------------------------------------------------------------------------
def _formula_selftests():
    rng = np.random.RandomState(123)
    n = 512
    a = rand_phasor((n,), rng)
    b = rand_phasor((n,), rng)
    c = bind(a, b)
    b_rec = unbind(c, a)
    rt = cos_c(b_rec, b)
    assert rt >= 0.90, f"selftest1 bind-roundtrip cos={rt}"
    # clean shared transform (sigma=0): novel transfer must be perfect
    accs_clean = build_and_eval(N=1024, K_=5, sigma=0.0, M=25, n_test_per=10, seed=7)
    assert accs_clean["ARM_REAL"] >= 0.99, f"selftest2 clean real={accs_clean['ARM_REAL']}"
    assert accs_clean["ARM_SHUFFLED"] <= 0.40, f"selftest4 clean shuf={accs_clean['ARM_SHUFFLED']}"
    # cleanup argmax picks true object on clean codebook
    O = rand_phasor((6, n), rng)
    tgt = 3
    assert cleanup_argmax(O[tgt].copy(), O) == tgt, "selftest3 cleanup argmax"
    print(f"[formula_selftest] bind_rt={rt:.3f} clean_real={accs_clean['ARM_REAL']:.3f} "
          f"clean_shuf={accs_clean['ARM_SHUFFLED']:.3f} PASS", flush=True)
    return rt


_BIND_RT = _formula_selftests()

# feasibility / discriminator-reachability (THEORETICAL; no CRLB noise-floor for
# argmax transfer). chance floor=0.100; observed ceiling ~0.69 (prototype);
# HP threshold abs=0.400 lies strictly between => reachable.
assert RANDOM_BASELINE + HP_REAL_GAIN_MIN < 0.95, "HP threshold must be below saturation"


# ----------------------------------------------------------------------------
# Defensive: start-marker + crash-diagnostic (SS13)
# ----------------------------------------------------------------------------
def _write_start_marker(out_dir: Path):
    marker = {
        "pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR_NAME, "run_mode": RUN_MODE,
        "expected_n_units": EXPECTED_N_UNITS, "host": platform.node(),
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    tmp = out_dir / "_start_marker.json.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, out_dir / "_start_marker.json")


def _write_crash_metrics(out_dir: Path, exc: Exception):
    diag = {
        "anchor_name": ANCHOR_NAME, "run_mode": RUN_MODE,
        "verdict": "CELL_CRASHED",
        "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
        "summary": f"CELL_CRASHED: {type(exc).__name__}",
        "elapsed_s": 0.0,
        "traceback": traceback.format_exc()[:5000],
        "ts_iso": datetime.now(timezone.utc).isoformat(),
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    tmp = out_dir / "metrics.json.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, out_dir / "metrics.json")


# ----------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------
def main():
    t_start = time.time()
    out_dir = get_output_dir(ANCHOR_NAME)
    _write_start_marker(out_dir)
    print(f"[{ANCHOR_NAME}] run_mode={RUN_MODE} N={N_DIM} K={K} sigma={SIGMA} "
          f"seeds={SEEDS} M_sweep={M_SWEEP} arms={ARMS} "
          f"expected_units={EXPECTED_N_UNITS}", flush=True)

    run_config = {"N": N_DIM, "run_mode": RUN_MODE, "anchor": ANCHOR_NAME}
    done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
    print(f"[ckpt] {len(done)}/{len(SEEDS)} done; running {remaining}", flush=True)

    for seed in remaining:
        r = run_seed(seed)
        write_partial(out_dir, seed, r)
        print(f"[{ANCHOR_NAME}] seed={seed} done ({r['elapsed_s']:.1f}s)", flush=True)

    per_seed = aggregate_partials(out_dir, SEEDS, run_config=run_config)
    agg = aggregate(per_seed)

    # arms-differ (META_RULE_AF) on first seed
    ad_ok, ad_digests = arms_differ_check(SEEDS[0])

    verdict, verdict_msg, diag = compute_verdict(
        agg, ad_ok, _BIND_RT, agg["n_units"])

    elapsed = time.time() - t_start
    summary = f"{verdict}: {diag.get('real_curve')}"
    metrics = {
        "anchor": ANCHOR_NAME,
        "anchor_name": ANCHOR_NAME,
        "run_mode": RUN_MODE,
        "N": N_DIM, "N_DIM": N_DIM, "K": K, "sigma": SIGMA,
        "n_seeds": len(per_seed),
        "seeds": [int(s) for s in per_seed.keys()],
        "M_sweep": M_SWEEP, "M_OP": M_OP, "arms": ARMS,
        "primary_arm": PRIMARY_ARM, "control_arms": CONTROL_ARMS,
        "random_baseline": RANDOM_BASELINE,
        "expected_n_units": EXPECTED_N_UNITS,
        "n_units_counted": agg["n_units"],
        "n_units_failed": agg["n_units_failed"],
        "cardinality_ok": agg["n_units"] >= EXPECTED_N_UNITS,
        "arms_differ_verified": ad_ok,
        "arms_differ_digests": ad_digests,
        "bind_roundtrip": _BIND_RT,
        "hp_scope": {"ARM_REAL": ["HARD_PASS", "HARD_FAIL"],
                     "ARM_SHUFFLED": [], "ARM_MEAN_OBJECT": []},
        "per_arm_aggregate": agg["per_arm"],
        "gate_diagnostics": diag,
        "corpus_provenance": "synthetic_fhrr_clustered_phasors_dialable_shared_structure",
        "allow_synthetic": True,
        "zero_llm_calls_at_inference": True,
        "n_llm_calls": 0,
        "metrics_source": "measured_cpu_fhrr_holistic_map_schema_transfer",
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": summary,
        "elapsed_s": elapsed,
    }
    # ATOMIC final write (META_RULE_AH: tmp_replace)
    tmp_path = out_dir / "metrics.json.tmp"
    with open(tmp_path, "w", encoding="utf-8") as fh:
        json.dump(metrics, fh, indent=2)
    os.replace(tmp_path, out_dir / "metrics.json")

    print(f"[{ANCHOR_NAME}] verdict={verdict}", flush=True)
    print(f"[{ANCHOR_NAME}] {verdict_msg}", flush=True)
    print(f"[{ANCHOR_NAME}] elapsed={elapsed:.1f}s units={agg['n_units']}/{EXPECTED_N_UNITS}",
          flush=True)


if __name__ == "__main__":
    if _ARGS.self_test:
        print("[main] --self-test complete (formula self-tests passed at import)", flush=True)
        sys.exit(0)
    _OUT = get_output_dir(ANCHOR_NAME)
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        _write_crash_metrics(_OUT, e)
        raise
