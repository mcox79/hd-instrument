"""schema_bundle_real_corpus_transfer_v1 -- REAL-CORPUS schema-transfer test.

SCIENTIFIC QUESTION:
  The SYNTHETIC schema cell (schema_bundle_structural_transfer_v1) HARD_PASSED at
  FULL (transfer +0.590 at M=200) proving the holistic/analogical-map MECHANISM
    M_R = mean_i bind(B_i, inv(A_i))  ;  D_hat = bind(C_novel, M_R)  ;  argmax cleanup
  works WHEN entities carry dial-able shared structure. The open question that
  actually matters: does it help on REAL knowledge? Can the substrate turn many
  stored facts of a relation into TRANSFERABLE knowledge -- answer correctly for a
  NOVEL same-relation entity pair it never saw? This cell reuses the EXACT
  validated mechanism and changes ONLY the data: real ConceptNet relation triples,
  encoded with the substrate's zero-LLM encodings. Constructive build, NOT vs-LLM.

INTERPRETATION MATRIX (pre-registered; the point of the cell):
  real-relation PASS         => substrate turns stored facts into transferable
                                knowledge in the current encoding (the GOAL).
  real-relation FAIL BUT      => the MECHANISM works (synth-positive control below
    synth-positive PASS          reproduces the synthetic HARD_PASS here), but real
                                relations lack learnable structure IN THE CURRENT
                                ENCODING -> points at ENCODER/INGEST, NOT the
                                mechanism. This is a DIAGNOSTIC, not a mechanism
                                failure, and it feeds the encoder-primary program.
  real FAIL AND synth FAIL    => HARNESS_SUSPECT: the cleanup/algebra broke at this
                                regime; downstream real arms are uninterpretable.

ENCODINGS (both ZERO-LLM, deterministic, self-contained, restartable):
  char-trigram phasor (ARM_REAL): entity string -> boundary-marked char-trigrams ->
    each trigram hashed (md5, platform-stable) to a random unit phasor -> bundle
    (sum) -> phase-only projection exp(i*angle(.)) to a UNIT-MODULUS FHRR phasor.
    Surface-similar entities get correlated phase patterns; captures SURFACE
    (morphological) structure only. This is the cheapest zero-LLM encoding the
    substrate could ingest.
  random phasor (ARM_RANDENC): entity -> hash(entity,seed) -> random unit phasor.
    This is the substrate's ACTUAL current KG-store entity encoding (KG atoms are
    random hypervectors; see exp_u1_fb15k237_ingest_eval_v1 / exp_n8_conceptnet).
    Structureless by construction -> the mechanism MUST give ~chance here.

RELATIONS (3, spanning the structure spectrum; ConceptNet English lemmas):
  AtLocation   -- flagship: 27797 pairs, top-100 objects reused ~94 subj/object;
                  PURE SEMANTIC (dog->house, sofa->house are NOT surface-similar).
                  Best-posed testbed; char-trigram expected to carry NOTHING.
  CausesDesire -- 4688 pairs, small 598-object codebook, reuse ~14; semantic.
  DerivedFrom  -- 6535 pairs, surface-morphological (runner->run); the ONE
                  relation where char-trigram COULD carry the transform. Best
                  chance for a real positive.

ARMS (all paired: SAME relation triples / split / seed; only manipulation differs):
  ARM_REAL         -- char-trigram enc, TRUE pairs. PRIMARY. HP gates apply.
  ARM_SHUFFLED     -- char-trigram enc, object labels permuted within the M-sample
                      (breaks subject->object correspondence). Structureless-
                      RELATION / codebook-artifact discriminator. Expected ~chance.
  ARM_RANDENC      -- random-phasor enc, TRUE pairs. Structureless-ENCODING
                      discriminator (the Director-mandated structureless arm).
                      Expected ~chance; proves a positive reflects ENCODING
                      structure, not codebook geometry.
  ARM_MEAN_OBJECT  -- char-trigram, C-INDEPENDENT readout D_hat = M_R (no bind with
                      novel subject C). Catches low-cardinality "return the popular
                      object". Expected below ARM_REAL.

SWEEP:  M in {25, 50, 100, 150, 200} = # training pairs bundled into the schema
        map. Transfer should CLIMB with M if real structure exists (SNR axis, as in
        the synthetic cell). M_OP=200 respects the ~200-items/bundle reliable-recall
        budget at N=8192.

POSITIVE CONTROL (Gate D; harness-reproduces-mechanism AT THIS REGIME):
  ARM_SYNTH_POSITIVE -- the validated synthetic clustered generator (K=10 clusters,
    sigma=2.0, M=200) run at N=8192. Must reproduce transfer. Cited prior:
    MEASURED@data/exp_schema_bundle_structural_transfer_v1/metrics.json real M=200
    gain=+0.590 at N=4096; expect >= 0.15 gain at N=8192 (larger N is easier). If
    synth-positive fails, the ALGEBRA/cleanup is broken -> HARNESS_SUSPECT.

PRE-REGISTERED BANDS (LOCKED before smoke; primary arm ARM_REAL, per relation):
  random_baseline = 1/V_eff (V_eff = actual codebook size, <=100). THEORETICAL.
  gain(arm) = arm_acc - random_baseline.
  HARD_PASS (per relation): gain(ARM_REAL) >= 0.2075  (0.20 floor + 5% band-width,
             META_RULE_L) AND gain(ARM_SHUFFLED) <= 0.05 AND gain(ARM_RANDENC)
             <= 0.05 AND (ARM_REAL - ARM_MEAN_OBJECT) >= 0.05 (subject-conditional).
  HARD_FAIL (per relation): gain(ARM_REAL) <= 0.05 at M_OP.
  MIDDLE_BAND (per relation): 0.05 < gain(ARM_REAL) < 0.2075, or partial gates.
  OVERALL verdict: HARD_PASS if ANY relation HP (and synth-positive OK);
             HARD_FAIL if ALL relations HF (and synth OK and controls at chance --
             a genuine null, the encoder-diagnostic outcome); MIDDLE otherwise.
  Sanity rails: FHRR bind-roundtrip >= 0.90; synth_positive_gain >= 0.15;
             ARM_REAL not saturated (< 0.95); controls not wildly above chance.

HP_SCOPE: HARD_PASS/HARD_FAIL gates apply to ARM_REAL ONLY (per relation).
  ARM_SHUFFLED / ARM_RANDENC / ARM_MEAN_OBJECT are controls; they must NOT clear HP
  (expected ~chance) and inherit no chain-grade gate. ARM_SYNTH_POSITIVE is a
  harness sanity gate, not a substrate-capability claim.

COMPUTE ARCHITECTURE:
  Class: (b) sequential-CPU with justification. Primitives are elementwise complex
  mul (bind), vector sum (bundle/mean), V x N cleanup matmul (V<=100 tiny). Per-unit
  wall << 10s; total expected ~2-6 min for 3 relations x 4 arms x 5 M x 3 seeds
  (180 units) + encoding. No N x N matrices. Below the GPU-batching threshold ->
  sequential CPU is the correct resource. Storage strategy: bundled (mean) -- the
  schema map IS a bundle and is the object under test; NOT a chained-composition
  cell, so META_STORAGE sharded-default does not apply. Route smoke local; FULL to
  remote_cpu_queue.

WHAT_THIS_DOES_NOT_SHOW:
  - NOT a vs-LLM comparison (ZERO LLM calls; pure vector algebra).
  - NOT multi-relation coexistence (that is the conditional follow-up).
  - A real HARD_FAIL here does NOT impugn the mechanism (synth-positive isolates
    that); it is a statement about the CURRENT ENCODING carrying no learnable
    relational transform -- the encoder-primary diagnostic.

FORMULA SELF-TESTS (import time, fast <180s):
  1. FHRR bind/unbind roundtrip: unbind(bind(a,b), a) ~ b, cosine >= 0.90.
  2. char-trigram determinism: encode('runner') identical across two calls.
  3. char-trigram surface-similarity: cos(enc('running'), enc('runningx')) >
     cos(enc('running'), enc('xyzqvw')) (shared trigrams -> higher cosine).
  4. Synthetic clean transform (sigma=0): novel-C transfer == 1.0 (mechanism recovers
     a noise-free schema); shuffled collapses to ~1/K. (reproduces synth harness)
  5. Cleanup argmax picks the true object on a clean codebook.

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
# - crlb n/a (argmax transfer); chance floor 1/V stated; reachability declared
# - baseline_in_band at smoke (META_RULE_AG; controls ~chance, ARM_REAL < 0.95)
# - discriminator survives scale (SMOKE runs at FULL N=8192 -- same regime)
# - HARD_PASS strictly above floor (gain 0.2075 = 0.20 + 5% band-width)
# - HP_SCOPE: HP gates apply to ARM_REAL only, per relation
# - cardinality_ok (META_RULE_H; EXPECTED_N_UNITS = relations*arms*M*seeds)
# - per-unit failure-class instrumentation (META_RULE_J; no bare except)
# - calibration_check = adaptive_with_discriminator_gate (baseline = 1/V_eff;
#   synth-positive is the discriminator-fires proof)
# - all numbers tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@ (META_RULE_AC)
# - positive_control_arm ARM_SYNTH_POSITIVE reproduces mechanism at test regime (Gate D)

ANCHOR_NAME = "schema_bundle_real_corpus_transfer_v1"
DATASET_REL = Path("data/datasets/conceptnet5_en_100k.jsonl")

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
# Config (SMOKE runs at FULL N=8192 -- discriminator-survives-scale. Only seed
# count / test size / train-pool cap shrink in smoke.)
# ----------------------------------------------------------------------------
N_DIM = 8192
V_CODEBOOK = 100                       # top-V objects per relation form the codebook
RELATIONS = ["AtLocation", "CausesDesire", "DerivedFrom"]
M_SWEEP = [25, 50, 100, 150, 200]      # training pairs bundled into the schema map
M_OP = 200                             # operating point for primary HP gates
ARMS = ["ARM_REAL", "ARM_SHUFFLED", "ARM_RANDENC", "ARM_MEAN_OBJECT"]
PRIMARY_ARM = "ARM_REAL"
CONTROL_ARMS = ["ARM_SHUFFLED", "ARM_RANDENC", "ARM_MEAN_OBJECT"]

# Synthetic positive-control (Gate D) regime
SYNTH_K = 10
SYNTH_SIGMA = 2.0
SYNTH_M = 200

if RUN_MODE == "smoke":
    SEEDS = [7, 13]
    N_TEST_PER = 60
    TRAIN_POOL_CAP = 400
else:
    SEEDS = [7, 13, 19]
    N_TEST_PER = 150
    TRAIN_POOL_CAP = 1500

# Pre-reg bands (LOCKED)
HP_REAL_GAIN_MIN = 0.2075               # 0.20 floor + 5% band-width (META_RULE_L)
HP_SHUF_GAIN_MAX = 0.05
HP_RANDENC_GAIN_MAX = 0.05
HP_REAL_MINUS_MEANOBJ_MIN = 0.05        # subject-conditional
HF_REAL_GAIN_MAX = 0.05
SYNTH_POSITIVE_GAIN_MIN = 0.15          # harness-reproduces-mechanism gate
BIND_ROUNDTRIP_MIN = 0.90
REAL_SATURATION_HI = 0.95
CONTROL_ABOVE_CHANCE_MAX = 0.10         # controls must not be wildly above chance

# Cardinality (META_RULE_H): real-relation grid only (synth tracked separately)
EXPECTED_N_UNITS = len(RELATIONS) * len(ARMS) * len(M_SWEEP) * len(SEEDS)


# ----------------------------------------------------------------------------
# FHRR primitives (complex64 phasors)
# ----------------------------------------------------------------------------
def _stable_seed(text: str, salt: int = 0) -> int:
    """Platform-stable 32-bit seed from a string (md5, not Python hash())."""
    h = hashlib.md5(f"{salt}:{text}".encode("utf-8")).hexdigest()
    return int(h[:8], 16)


def rand_phasor_from_seed(n: int, seed: int) -> np.ndarray:
    rng = np.random.RandomState(seed)
    ang = rng.uniform(-np.pi, np.pi, size=n).astype(np.float32)
    return np.exp(1j * ang).astype(np.complex64)


def bind(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """FHRR bind = elementwise complex multiply."""
    return (a * b).astype(np.complex64)


def unbind(c: np.ndarray, a: np.ndarray) -> np.ndarray:
    """FHRR unbind = multiply by conjugate (inverse of a unit phasor)."""
    return (c * np.conj(a)).astype(np.complex64)


def cos_c(x: np.ndarray, y: np.ndarray) -> float:
    """Normalized Hermitian cosine (real part) between two complex vectors."""
    num = float(np.vdot(y, x).real)
    den = float(np.linalg.norm(x) * np.linalg.norm(y)) + 1e-12
    return num / den


def cleanup_argmax_batch(Dhat: np.ndarray, O: np.ndarray) -> np.ndarray:
    """Argmax real cosine of each row of Dhat (B,N) against object codebook O (V,N)."""
    sims = (Dhat @ np.conj(O).T).real          # (B, V)
    return sims.argmax(axis=1)


# ----------------------------------------------------------------------------
# char-trigram phasor encoder (zero-LLM, deterministic, platform-stable)
# ----------------------------------------------------------------------------
_TRIGRAM_BASIS: Dict[Tuple[str, int], np.ndarray] = {}


def _trigram_basis(tg: str, n: int) -> np.ndarray:
    key = (tg, n)
    v = _TRIGRAM_BASIS.get(key)
    if v is None:
        v = rand_phasor_from_seed(n, _stable_seed(tg, salt=1))
        _TRIGRAM_BASIS[key] = v
    return v


def encode_trigram(s: str, n: int) -> np.ndarray:
    """Bag-of-char-trigrams bundle, phase-only projected to a unit FHRR phasor."""
    t = "#" + s.replace("_", " ") + "#"
    if len(t) < 3:
        t = (t + "##")[:3]
    acc = np.zeros(n, dtype=np.complex64)
    for i in range(len(t) - 2):
        acc = acc + _trigram_basis(t[i:i + 3], n)
    ang = np.angle(acc)
    return np.exp(1j * ang).astype(np.complex64)


def encode_random(s: str, n: int, seed: int) -> np.ndarray:
    """Random unit phasor (substrate's actual KG-store entity encoding)."""
    return rand_phasor_from_seed(n, _stable_seed(s, salt=100 + seed))


# ----------------------------------------------------------------------------
# Data loading
# ----------------------------------------------------------------------------
def load_relation(relation: str, V: int) -> Tuple[List[Tuple[str, str]], List[str]]:
    """Return (pairs filtered to top-V objects, codebook object-string list)."""
    import collections
    path = REPO / DATASET_REL
    pairs_all: List[Tuple[str, str]] = []
    objc = collections.Counter()
    with open(path, encoding="utf-8") as f:
        for line in f:
            d = json.loads(line)
            if d.get("predicate") != relation:
                continue
            s, o = d.get("subject"), d.get("object")
            if s is None or o is None or s == o:
                continue
            pairs_all.append((str(s), str(o)))
            objc[str(o)] += 1
    codebook = [o for o, _ in objc.most_common(V)]
    cb_set = set(codebook)
    pairs = [(s, o) for (s, o) in pairs_all if o in cb_set]
    return pairs, codebook


# ----------------------------------------------------------------------------
# Synthetic positive control (validated mechanism; reproduces synth HARD_PASS)
# ----------------------------------------------------------------------------
def synth_positive(N: int, K: int, sigma: float, M: int, n_test_per: int,
                   seed: int) -> Dict[str, float]:
    """Clustered generator identical in spirit to schema_bundle_structural_transfer_v1.

    Returns {real, shuffled} transfer accuracy. chance = 1/K.
    """
    rng = np.random.RandomState(seed)
    MU = np.exp(1j * rng.uniform(-np.pi, np.pi, (K, N))).astype(np.complex64)
    O = np.exp(1j * rng.uniform(-np.pi, np.pi, (K, N))).astype(np.complex64)
    per = M // K
    labels = np.repeat(np.arange(K), per)
    A = np.zeros((labels.shape[0], N), dtype=np.complex64)
    for k in range(K):
        ang0 = np.angle(MU[k])[None, :]
        ang = ang0 + sigma * rng.standard_normal((per, N)).astype(np.float32)
        A[k * per:(k + 1) * per] = np.exp(1j * ang).astype(np.complex64)
    inv_A = np.conj(A)
    M_real = (O[labels] * inv_A).mean(axis=0).astype(np.complex64)
    M_shuf = (O[rng.permutation(labels.copy())] * inv_A).mean(axis=0).astype(np.complex64)
    cr = cs = tot = 0
    for k in range(K):
        ang0 = np.angle(MU[k])[None, :]
        ang = ang0 + sigma * rng.standard_normal((n_test_per, N)).astype(np.float32)
        C = np.exp(1j * ang).astype(np.complex64)
        pr = cleanup_argmax_batch(C * M_real[None, :], O)
        ps = cleanup_argmax_batch(C * M_shuf[None, :], O)
        cr += int((pr == k).sum()); cs += int((ps == k).sum()); tot += n_test_per
    return {"real": cr / tot, "shuf": cs / tot, "chance": 1.0 / K}


# ----------------------------------------------------------------------------
# Core: one (relation, seed) -> all arms x M-sweep transfer accuracy
# ----------------------------------------------------------------------------
def eval_relation_seed(relation: str, seed: int, N: int, V: int,
                       n_test_per: int, pool_cap: int) -> Dict:
    """Real-corpus novel-subject transfer for one relation+seed, all arms x M-sweep."""
    pairs, codebook = load_relation(relation, V)
    V_eff = len(codebook)
    if V_eff < 2:
        raise ValueError(f"relation {relation}: codebook too small V_eff={V_eff}")
    obj_idx = {o: i for i, o in enumerate(codebook)}
    rng = np.random.RandomState(seed)

    # split by SUBJECT (novel-subject held-out): unique subjects -> test vs pool
    subs = sorted({s for s, _ in pairs})
    rng.shuffle(subs)
    n_test_subs = max(n_test_per * 2, 120)
    test_subs = set(subs[:n_test_subs])
    pool_subs = subs[n_test_subs:]
    rng.shuffle(pool_subs)
    pool_subs = set(pool_subs[:pool_cap])

    train_pool = [(s, o) for (s, o) in pairs if s in pool_subs]
    test_pool = [(s, o) for (s, o) in pairs if s in test_subs]
    # one held-out pair per novel subject (avoid multi-object subjects dominating)
    seen_ts = set()
    test_pairs = []
    for s, o in test_pool:
        if s in seen_ts:
            continue
        seen_ts.add(s); test_pairs.append((s, o))
        if len(test_pairs) >= n_test_per:
            break
    if len(train_pool) < max(M_SWEEP) or len(test_pairs) < 20:
        raise ValueError(
            f"relation {relation}: insufficient data (train_pool={len(train_pool)}, "
            f"test_pairs={len(test_pairs)}, need train>={max(M_SWEEP)}, test>=20)")

    # entities to encode: train-pool subjects + test subjects + codebook objects
    ent_set = {s for s, _ in train_pool} | {s for s, _ in test_pairs} | set(codebook)
    ents = sorted(ent_set)
    eidx = {e: i for i, e in enumerate(ents)}
    E_trig = np.stack([encode_trigram(e, N) for e in ents]).astype(np.complex64)
    E_rand = np.stack([encode_random(e, N, seed) for e in ents]).astype(np.complex64)
    O_trig = E_trig[[eidx[o] for o in codebook]]     # (V,N)
    O_rand = E_rand[[eidx[o] for o in codebook]]     # (V,N)

    # test tensors (fixed across M)
    C_trig = E_trig[[eidx[s] for s, _ in test_pairs]]    # (T,N)
    C_rand = E_rand[[eidx[s] for s, _ in test_pairs]]
    y_test = np.array([obj_idx[o] for _, o in test_pairs], dtype=np.int64)  # (T,)
    T = y_test.shape[0]
    chance = 1.0 / V_eff

    # fixed max-M training sample; nested prefixes give the M-sweep (paired, monotone)
    tp = train_pool[:]
    rng.shuffle(tp)
    tp = tp[:max(M_SWEEP)]
    A_trig_all = E_trig[[eidx[s] for s, _ in tp]]     # (Mmax,N)
    A_rand_all = E_rand[[eidx[s] for s, _ in tp]]
    y_train_all = np.array([obj_idx[o] for _, o in tp], dtype=np.int64)
    perm_all = rng.permutation(len(tp))               # shuffled-object assignment

    out: Dict[str, Dict[int, float]] = {a: {} for a in ARMS}
    for M in M_SWEEP:
        A_t = A_trig_all[:M]; A_r = A_rand_all[:M]
        yt = y_train_all[:M]
        Bt = O_trig[yt]                                # (M,N) true objects, trigram
        Br = O_rand[yt]                                # (M,N) true objects, random
        # shuffled objects: permute the object-label assignment among the M pairs
        y_shuf = y_train_all[perm_all[:M]]
        Bs = O_trig[y_shuf]

        M_real = (Bt * np.conj(A_t)).mean(axis=0).astype(np.complex64)
        M_shuf = (Bs * np.conj(A_t)).mean(axis=0).astype(np.complex64)
        M_rand = (Br * np.conj(A_r)).mean(axis=0).astype(np.complex64)

        pred_real = cleanup_argmax_batch(C_trig * M_real[None, :], O_trig)
        pred_shuf = cleanup_argmax_batch(C_trig * M_shuf[None, :], O_trig)
        pred_rand = cleanup_argmax_batch(C_rand * M_rand[None, :], O_rand)
        # C-INDEPENDENT: broadcast M_real to all test rows (ignores subject C)
        pred_mean = cleanup_argmax_batch(np.tile(M_real[None, :], (T, 1)), O_trig)

        out["ARM_REAL"][M] = float((pred_real == y_test).mean())
        out["ARM_SHUFFLED"][M] = float((pred_shuf == y_test).mean())
        out["ARM_RANDENC"][M] = float((pred_rand == y_test).mean())
        out["ARM_MEAN_OBJECT"][M] = float((pred_mean == y_test).mean())

    return {
        "relation": relation, "seed": seed, "V_eff": V_eff, "chance": chance,
        "n_train_pool": len(train_pool), "n_test": T,
        "acc": {a: {int(M): out[a][M] for M in M_SWEEP} for a in ARMS},
    }


def run_seed(seed: int) -> Dict:
    """All relations x arms x M-sweep + synth-positive for one seed. Failure-instrumented."""
    t0 = time.time()
    per_rel: Dict[str, Dict] = {}
    per_unit: Dict[str, Dict] = {}
    fatal = False
    fatal_msg = None
    for relation in RELATIONS:
        try:
            r = eval_relation_seed(relation, seed, N_DIM, V_CODEBOOK,
                                   N_TEST_PER, TRAIN_POOL_CAP)
        except Exception as e:                 # META_RULE_J: specific record + halt seed
            fatal = True
            fatal_msg = f"{relation}:{type(e).__name__}:{str(e)[:200]}"
            for a in ARMS:
                for M in M_SWEEP:
                    per_unit[f"{relation}_{a}_M{M}"] = {
                        "relation": relation, "arm": a, "M": M, "acc": None,
                        "failure_class": type(e).__name__, "failure_msg": str(e)[:200]}
            print(f"  [seed={seed} rel={relation}] FAILED {type(e).__name__}: {e}", flush=True)
            break
        per_rel[relation] = r
        for a in ARMS:
            for M in M_SWEEP:
                per_unit[f"{relation}_{a}_M{M}"] = {
                    "relation": relation, "arm": a, "M": M,
                    "acc": float(r["acc"][a][int(M)]), "failure_class": None}
        cb = r["chance"]
        print(f"  [seed={seed} {relation:<13} V={r['V_eff']} chance={cb:.4f} "
              f"nT={r['n_test']}] M{M_OP}: "
              f"real={r['acc']['ARM_REAL'][M_OP]:.3f} "
              f"shuf={r['acc']['ARM_SHUFFLED'][M_OP]:.3f} "
              f"rand={r['acc']['ARM_RANDENC'][M_OP]:.3f} "
              f"mean={r['acc']['ARM_MEAN_OBJECT'][M_OP]:.3f}", flush=True)

    # positive control (harness reproduces mechanism at N=8192)
    sp = synth_positive(N_DIM, SYNTH_K, SYNTH_SIGMA, SYNTH_M, 20, seed)
    sp_gain = sp["real"] - sp["chance"]
    print(f"  [seed={seed} SYNTH_POSITIVE K={SYNTH_K} M={SYNTH_M}] "
          f"real={sp['real']:.3f} shuf={sp['shuf']:.3f} chance={sp['chance']:.3f} "
          f"gain={sp_gain:+.3f}", flush=True)

    return {
        "seed": seed, "N": N_DIM, "V": V_CODEBOOK, "run_mode": RUN_MODE,
        "config_version": f"ANCHOR={ANCHOR_NAME},N={N_DIM},V={V_CODEBOOK}",
        "per_rel": per_rel, "per_unit": per_unit,
        "synth_positive": {"real": sp["real"], "shuf": sp["shuf"],
                           "chance": sp["chance"], "gain": sp_gain},
        "fatal": fatal, "fatal_msg": fatal_msg, "elapsed_s": time.time() - t0,
    }


# ----------------------------------------------------------------------------
# Aggregate + verdict
# ----------------------------------------------------------------------------
def aggregate(per_seed: Dict) -> Dict:
    """Return per-relation per-arm mean/std over seeds at each M + synth-positive + counts."""
    accs: Dict[str, Dict[str, Dict[int, List[float]]]] = {
        rel: {a: {M: [] for M in M_SWEEP} for a in ARMS} for rel in RELATIONS}
    chance: Dict[str, List[float]] = {rel: [] for rel in RELATIONS}
    sp_gains: List[float] = []
    n_units = 0; n_failed = 0
    for sd in per_seed.values():
        for key, rec in sd.get("per_unit", {}).items():
            n_units += 1
            if rec.get("acc") is None:
                n_failed += 1; continue
            accs[rec["relation"]][rec["arm"]][int(rec["M"])].append(float(rec["acc"]))
        for rel, r in sd.get("per_rel", {}).items():
            chance[rel].append(float(r["chance"]))
        spg = sd.get("synth_positive", {}).get("gain")
        if spg is not None:
            sp_gains.append(float(spg))

    per_arm: Dict[str, Dict] = {}
    for rel in RELATIONS:
        ch = float(np.mean(chance[rel])) if chance[rel] else float("nan")
        per_arm[rel] = {"chance": ch, "arms": {}}
        for a in ARMS:
            per_arm[rel]["arms"][a] = {}
            for M in M_SWEEP:
                vals = accs[rel][a][M]
                n = len(vals)
                mean = float(np.mean(vals)) if n else float("nan")
                std = float(np.std(vals, ddof=1)) if n > 1 else 0.0
                cv = (std / abs(mean)) if (n > 1 and abs(mean) > 1e-9) else 0.0
                per_arm[rel]["arms"][a][M] = {
                    "mean": mean, "std": std, "cv": cv, "n": n,
                    "gain": (mean - ch) if (n and ch == ch) else float("nan")}
    sp_gain_mean = float(np.mean(sp_gains)) if sp_gains else float("nan")
    return {"per_rel_arm": per_arm, "synth_positive_gain_mean": sp_gain_mean,
            "n_units": n_units, "n_units_failed": n_failed}


def _relation_verdict(rel_block: Dict) -> Tuple[str, Dict]:
    """Per-relation verdict at M_OP. Returns (verdict, diag)."""
    arms = rel_block["arms"]
    real = arms["ARM_REAL"][M_OP]
    shuf = arms["ARM_SHUFFLED"][M_OP]
    rand = arms["ARM_RANDENC"][M_OP]
    mean = arms["ARM_MEAN_OBJECT"][M_OP]
    real_gain = real["gain"]; shuf_gain = shuf["gain"]; rand_gain = rand["gain"]
    real_minus_mean = real["mean"] - mean["mean"]
    real_minus_shuf = real["mean"] - shuf["mean"]   # correspondence-dependent signal
    real_minus_rand = real["mean"] - rand["mean"]   # encoding-dependent signal
    # A genuine schema signal must EXCEED the pairing-shuffled control: if shuffling
    # the subject->object correspondence does NOT drop accuracy, the accuracy is not
    # correspondence-dependent -> it is a codebook/encoding artifact (e.g. DerivedFrom
    # "nearest-substring-object"), NOT schema transfer.
    confound = (real_gain > HF_REAL_GAIN_MAX) and (real_minus_shuf <= HP_SHUF_GAIN_MAX)
    diag = {
        "chance": rel_block["chance"],
        "real_acc": real["mean"], "real_gain": real_gain, "real_cv": real["cv"],
        "shuf_gain": shuf_gain, "rand_gain": rand_gain,
        "mean_obj_acc": mean["mean"], "real_minus_mean_obj": real_minus_mean,
        "real_minus_shuf": real_minus_shuf, "real_minus_rand": real_minus_rand,
        "confound_shuffle_invariant": confound,
        "real_curve": {str(M): arms["ARM_REAL"][M]["mean"] for M in M_SWEEP},
        "shuf_curve": {str(M): arms["ARM_SHUFFLED"][M]["mean"] for M in M_SWEEP},
        "rand_curve": {str(M): arms["ARM_RANDENC"][M]["mean"] for M in M_SWEEP},
        "meanobj_curve": {str(M): arms["ARM_MEAN_OBJECT"][M]["mean"] for M in M_SWEEP},
    }
    if any(v != v for v in (real_gain, shuf_gain, rand_gain)):  # NaN guard
        return ("MIDDLE_BAND", diag)
    if real["mean"] >= REAL_SATURATION_HI and confound:
        # high accuracy but shuffle-invariant -> artifact, not schema
        return ("HARD_FAIL", diag)
    if real_gain <= HF_REAL_GAIN_MAX:
        return ("HARD_FAIL", diag)           # real at chance: no transfer
    if real_minus_shuf <= HP_SHUF_GAIN_MAX:
        return ("HARD_FAIL", diag)           # real not separated from shuffled: artifact
    hp = (real_gain >= HP_REAL_GAIN_MIN and shuf_gain <= HP_SHUF_GAIN_MAX
          and rand_gain <= HP_RANDENC_GAIN_MAX
          and real_minus_mean >= HP_REAL_MINUS_MEANOBJ_MIN
          and real_minus_shuf >= HP_REAL_GAIN_MIN)
    if hp:
        return ("HARD_PASS", diag)
    return ("MIDDLE_BAND", diag)


def compute_verdict(agg: Dict, arms_differ_ok: bool, bind_roundtrip: float,
                    n_units: int) -> Tuple[str, str, Dict]:
    per = agg["per_rel_arm"]
    sp_gain = agg["synth_positive_gain_mean"]

    rel_verdicts: Dict[str, str] = {}
    rel_diag: Dict[str, Dict] = {}
    for rel in RELATIONS:
        v, d = _relation_verdict(per[rel])
        rel_verdicts[rel] = v; rel_diag[rel] = d

    diag = {
        "M_OP": M_OP, "synth_positive_gain_mean": sp_gain,
        "synth_positive_gate": SYNTH_POSITIVE_GAIN_MIN,
        "bind_roundtrip": bind_roundtrip, "arms_differ_ok": arms_differ_ok,
        "n_units": n_units, "expected_n_units": EXPECTED_N_UNITS,
        "relation_verdicts": rel_verdicts, "relation_diag": rel_diag,
    }

    # Cardinality gate (META_RULE_H)
    if n_units < EXPECTED_N_UNITS:
        return ("HARD_FAIL",
                f"HARD_FAIL_CARDINALITY_BREACH_META_RULE_H: n_units={n_units} < "
                f"expected={EXPECTED_N_UNITS}.", diag)
    # ARMS-MUST-DIFFER (META_RULE_AF)
    if not arms_differ_ok:
        return ("HARD_FAIL",
                "META_RULE_AF_VIOLATION: arm outputs bit-identical; arm-impl bug.", diag)
    # Sanity rail: FHRR primitive works
    if not (bind_roundtrip >= BIND_ROUNDTRIP_MIN):
        return ("HARD_FAIL",
                f"SANITY_RAIL_BIND: bind-roundtrip={bind_roundtrip:.3f} < "
                f"{BIND_ROUNDTRIP_MIN}; FHRR primitive broken.", diag)
    # Positive-control (Gate D): mechanism must reproduce at this regime
    if not (sp_gain >= SYNTH_POSITIVE_GAIN_MIN):
        return ("MIDDLE_BAND",
                f"HARNESS_SUSPECT: synth_positive_gain={sp_gain:+.3f} < "
                f"{SYNTH_POSITIVE_GAIN_MIN}; the validated mechanism did NOT reproduce "
                f"at N={N_DIM} -> real-relation arms are UNINTERPRETABLE. Fix harness.",
                diag)

    n_hp = sum(1 for v in rel_verdicts.values() if v == "HARD_PASS")
    n_hf = sum(1 for v in rel_verdicts.values() if v == "HARD_FAIL")
    summ_parts = []
    for rel in RELATIONS:
        d = rel_diag[rel]
        cf = " CONFOUND(shuffle-invariant)" if d.get("confound_shuffle_invariant") else ""
        summ_parts.append(
            f"{rel}[{rel_verdicts[rel]}{cf}]: real_acc={d['real_acc']:.3f} "
            f"real_gain={d['real_gain']:+.3f} real-shuf={d['real_minus_shuf']:+.3f} "
            f"real-rand={d['real_minus_rand']:+.3f} real-mean={d['real_minus_mean_obj']:+.3f} "
            f"chance={d['chance']:.4f}")
    summ = f"synth_pos_gain={sp_gain:+.3f} | " + " || ".join(summ_parts)

    if n_hp >= 1:
        winners = [r for r in RELATIONS if rel_verdicts[r] == "HARD_PASS"]
        return ("HARD_PASS",
                f"HARD_PASS_REAL_SCHEMA_TRANSFER: relation(s) {winners} turn stored "
                f"facts into transferable knowledge on novel same-relation pairs; "
                f"controls at chance, mechanism reproduced (synth+). {summ}", diag)
    if n_hf == len(RELATIONS):
        return ("HARD_FAIL",
                f"HARD_FAIL_NO_REAL_TRANSFER (DIAGNOSTIC): all real relations at "
                f"chance while synth-positive PASSED (gain={sp_gain:+.3f}) => the "
                f"holistic-map MECHANISM works but the CURRENT ENCODING carries no "
                f"learnable relational structure. Points at ENCODER/INGEST, not the "
                f"mechanism. {summ}", diag)
    return ("MIDDLE_BAND",
            f"MIDDLE_BAND_MIXED: real transfer present but not full HP on any "
            f"relation (n_hp={n_hp} n_hf={n_hf}); synth-positive OK. Sweep M / "
            f"encoding. {summ}", diag)


# ----------------------------------------------------------------------------
# arms-differ hash (META_RULE_AF)
# ----------------------------------------------------------------------------
def arms_differ_check(seed: int) -> Tuple[bool, Dict[str, str]]:
    """Build per-arm test-prediction vectors for one relation and hash; assert differ."""
    r = eval_relation_seed(RELATIONS[0], seed, N_DIM, V_CODEBOOK,
                           min(N_TEST_PER, 40), min(TRAIN_POOL_CAP, 300))
    # re-derive per-arm predictions at M_OP for hashing (deterministic given seed)
    digests = {}
    for a in ARMS:
        # use the accuracy curve bytes as a light-weight arm fingerprint proxy;
        # distinct arms produce distinct curves unless bit-identical impl bug.
        arr = np.array([r["acc"][a][int(M)] for M in M_SWEEP], dtype=np.float64)
        digests[a] = hashlib.sha256(arr.tobytes()).hexdigest()
    ok = len(set(digests.values())) == len(ARMS)
    return ok, digests


# ----------------------------------------------------------------------------
# Formula self-tests (import time, fast)
# ----------------------------------------------------------------------------
def _formula_selftests() -> float:
    rng = np.random.RandomState(123)
    n = 512
    a = np.exp(1j * rng.uniform(-np.pi, np.pi, n)).astype(np.complex64)
    b = np.exp(1j * rng.uniform(-np.pi, np.pi, n)).astype(np.complex64)
    c = bind(a, b)
    rt = cos_c(unbind(c, a), b)
    assert rt >= 0.90, f"selftest1 bind-roundtrip cos={rt}"
    # char-trigram determinism
    e1 = encode_trigram("runner", 1024); e2 = encode_trigram("runner", 1024)
    assert np.allclose(e1, e2), "selftest2 trigram determinism"
    # char-trigram surface-similarity: shared trigrams -> higher cosine
    sim_close = cos_c(encode_trigram("running", 1024), encode_trigram("runningx", 1024))
    sim_far = cos_c(encode_trigram("running", 1024), encode_trigram("xyzqvw", 1024))
    assert sim_close > sim_far, f"selftest3 surface-sim close={sim_close} far={sim_far}"
    # synthetic clean transform (sigma=0): perfect transfer; shuffled ~chance
    accs = synth_positive(N=1024, K=5, sigma=0.0, M=25, n_test_per=10, seed=7)
    assert accs["real"] >= 0.99, f"selftest4 clean real={accs['real']}"
    assert accs["shuf"] <= 0.60, f"selftest4 clean shuf={accs['shuf']}"
    # cleanup argmax picks true object on clean codebook
    O = np.exp(1j * rng.uniform(-np.pi, np.pi, (6, n))).astype(np.complex64)
    tgt = 3
    assert int(cleanup_argmax_batch(O[tgt:tgt + 1].copy(), O)[0]) == tgt, "selftest5 argmax"
    print(f"[formula_selftest] bind_rt={rt:.3f} trig_close={sim_close:.3f} "
          f"trig_far={sim_far:.3f} synth_clean_real={accs['real']:.3f} PASS", flush=True)
    return rt


_BIND_RT = _formula_selftests()

# feasibility / discriminator-reachability (THEORETICAL; no CRLB noise-floor for
# argmax transfer). chance floor = 1/V_eff (~0.01 at V=100); HP abs threshold
# = 1/V + 0.2075 ~ 0.22 lies strictly between chance and saturation => reachable.
assert (1.0 / V_CODEBOOK) + HP_REAL_GAIN_MIN < REAL_SATURATION_HI, \
    "HP threshold must be below saturation"


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
    print(f"[{ANCHOR_NAME}] run_mode={RUN_MODE} N={N_DIM} V={V_CODEBOOK} "
          f"relations={RELATIONS} seeds={SEEDS} M_sweep={M_SWEEP} arms={ARMS} "
          f"expected_units={EXPECTED_N_UNITS}", flush=True)

    run_config = {"N": N_DIM, "V": V_CODEBOOK, "run_mode": RUN_MODE, "anchor": ANCHOR_NAME}
    done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
    print(f"[ckpt] {len(done)}/{len(SEEDS)} done; running {remaining}", flush=True)

    for seed in remaining:
        r = run_seed(seed)
        write_partial(out_dir, seed, r)
        print(f"[{ANCHOR_NAME}] seed={seed} done ({r['elapsed_s']:.1f}s) "
              f"fatal={r['fatal']}", flush=True)

    per_seed = aggregate_partials(out_dir, SEEDS, run_config=run_config)
    agg = aggregate(per_seed)

    ad_ok, ad_digests = arms_differ_check(SEEDS[0])
    verdict, verdict_msg, diag = compute_verdict(agg, ad_ok, _BIND_RT, agg["n_units"])

    elapsed = time.time() - t_start
    summary = f"{verdict}: {diag.get('relation_verdicts')}"
    metrics = {
        "anchor": ANCHOR_NAME, "anchor_name": ANCHOR_NAME, "run_mode": RUN_MODE,
        "N": N_DIM, "N_DIM": N_DIM, "V": V_CODEBOOK,
        "relations": RELATIONS, "n_seeds": len(per_seed),
        "seeds": [int(s) for s in per_seed.keys()],
        "M_sweep": M_SWEEP, "M_OP": M_OP, "arms": ARMS,
        "primary_arm": PRIMARY_ARM, "control_arms": CONTROL_ARMS,
        "expected_n_units": EXPECTED_N_UNITS,
        "n_units_counted": agg["n_units"], "n_units_failed": agg["n_units_failed"],
        "cardinality_ok": agg["n_units"] >= EXPECTED_N_UNITS,
        "arms_differ_verified": ad_ok, "arms_differ_digests": ad_digests,
        "bind_roundtrip": _BIND_RT,
        "synth_positive_gain_mean": agg["synth_positive_gain_mean"],
        "synth_positive_gate": SYNTH_POSITIVE_GAIN_MIN,
        "hp_scope": {"ARM_REAL": ["HARD_PASS", "HARD_FAIL"],
                     "ARM_SHUFFLED": [], "ARM_RANDENC": [], "ARM_MEAN_OBJECT": []},
        "bands": {
            "HP_REAL_GAIN_MIN": HP_REAL_GAIN_MIN,
            "HP_SHUF_GAIN_MAX": HP_SHUF_GAIN_MAX,
            "HP_RANDENC_GAIN_MAX": HP_RANDENC_GAIN_MAX,
            "HP_REAL_MINUS_MEANOBJ_MIN": HP_REAL_MINUS_MEANOBJ_MIN,
            "HF_REAL_GAIN_MAX": HF_REAL_GAIN_MAX,
        },
        "per_rel_arm_aggregate": agg["per_rel_arm"],
        "gate_diagnostics": diag,
        "corpus_provenance": "conceptnet5_en_100k_real_triples_zero_llm_encodings",
        "encodings": {"ARM_REAL": "char_trigram_phasor_phase_only",
                      "ARM_RANDENC": "random_unit_phasor_substrate_native"},
        "allow_synthetic": False,
        "zero_llm_calls_at_inference": True, "n_llm_calls": 0,
        "metrics_source": "measured_cpu_fhrr_holistic_map_real_corpus_transfer",
        "verdict": verdict, "verdict_msg": verdict_msg, "summary": summary,
        "elapsed_s": elapsed,
    }
    tmp_path = out_dir / "metrics.json.tmp"
    with open(tmp_path, "w", encoding="utf-8") as fh:
        json.dump(metrics, fh, indent=2)
    os.replace(tmp_path, out_dir / "metrics.json")

    print(f"[{ANCHOR_NAME}] verdict={verdict}", flush=True)
    print(f"[{ANCHOR_NAME}] {verdict_msg}", flush=True)
    print(f"[{ANCHOR_NAME}] elapsed={elapsed:.1f}s units={agg['n_units']}/{EXPECTED_N_UNITS} "
          f"synth_pos_gain={agg['synth_positive_gain_mean']:+.3f}", flush=True)


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
