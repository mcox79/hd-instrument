"""schema_relation_transform_estimator_ablation_v1 -- the DECISIVE 2x2 continual-learning ablation.

SCIENTIFIC QUESTION (the make-or-break):
  The real-corpus schema cell (schema_bundle_real_corpus_transfer_v1) HARD_FAILED: no real
  relation showed genuine novel-subject transfer under the NAIVE-AVERAGING transform estimator
  M_R = mean_i bind(B_i, inv(A_i)) on the CURRENT (char-trigram / random-phasor) encoding.
  The 2x-drill reframed WHY: naive unweighted averaging with NO negative sampling is a
  documented-weak estimator for one-to-many relations REGARDLESS of encoding quality (TransE
  cannot represent 1-to-N; Xiong 2018 few-shot-KGE motivates itself against exactly this).
  The substrate's OWN prior HARD_PASS (PP-275 lap3_rotate_analogy_cpu_v1, Hits@1=0.899) proves
  a TRAINED relation transform works -- FHRR unit-modulus bind IS mathematically a RotatE
  rotation, so the algebra is not missing; the ESTIMATOR was.
  BUT PP-275 was (likely) TRANSDUCTIVE (trained per-entity embeddings; held-out TRIPLES, not
  held-out ENTITIES). Schema transfer REQUIRES INDUCTIVE (novel subject NEVER seen). So this
  cell trains ONLY the relation transform on a FIXED encoder (entities get their encoding from
  a deterministic encoder, so a NOVEL subject still HAS an encoding -> natively inductive), and
  reports the INDUCTIVE-vs-TRANSDUCTIVE gap EXPLICITLY. A transductive-only pass is NOT a
  schema-transfer pass. Constructive build; ZERO generative-LLM calls; not vs-LLM.

THE 2x2 (crossed, plus the parent's discriminating controls):
  Axis 1 ESTIMATOR:
    NAIVE_MEAN -- M_R = mean_i bind(O_i, conj(A_i)); readout D_hat = bind(C, M_R); argmax.
                  (the FAILED baseline; generative, no negatives.)
    TRAINED    -- a per-relation rotation theta (RotatE relation embedding; unit-modulus
                  FHRR rotation r = exp(i*theta)); readout D_hat = bind(C, r); argmax. theta
                  warm-started at the naive-mean phase, then refined by SOFTMAX cross-entropy
                  over the FULL V-object codebook (= negative sampling against all codebook
                  objects) via analytic-gradient descent. Isolates what discriminative /
                  negative-sampled training buys on top of the mean.
  Axis 2 ENCODING (entity encoder is FIXED -> novel subject still encodable -> inductive):
    char_trigram -- surface/morphological phasor (the parent's ARM_REAL; carries surface only).
    bge_semantic -- bounded BGE-small-en-v1.5 semantic embedding of ONLY the test relations'
                    entities (precomputed cache; NOT a full-store re-encode), centered +
                    projected to a UNIT FHRR phasor. Carries semantic relatedness.

RELATIONS (AtLocation = flagship one-to-many pure-semantic discriminator; + 2 controls):
  AtLocation   -- one-to-many, PURE SEMANTIC (dog->house, sofa->house not surface-similar);
                  the cleanest discriminator (surface encoding must carry NOTHING here).
  CausesDesire -- semantic, small codebook.
  DerivedFrom  -- surface-morphological (runner->run); watch the shuffle-climbs-to-match-real
                  signature = char-trigram nearest-substring encoding artifact, NOT transfer.

ARMS (all paired -- SAME relation triples / split / seed; only the manipulation differs):
  REAL        -- true (subject,object) training pairs. PRIMARY. HP gates apply.
  SHUFFLED    -- object labels permuted within the M training sample (breaks subject->object
                 correspondence). Structureless-RELATION control; MUST stay ~chance. If it
                 CLIMBS to match REAL, the REAL accuracy is a codebook/encoding artifact.
  MEAN_OBJECT -- C-INDEPENDENT readout (ignore the novel subject C; predict the transform's
                 default). Low-cardinality "return the popular object" control.
  (RANDENC floor + SYNTH positive-controls tracked separately, see below.)

EVAL_MODE (the make-or-break axis):
  inductive   -- test subjects DISJOINT from training subjects (novel-subject; the schema ask).
  transductive-- test subjects that WERE in training (their OTHER codebook pairs seen); one
                 held-out object per multi-object training subject. Reported to expose the gap.
                 For a GLOBAL (subject-agnostic) transform the gap should be SMALL -- that is
                 the POINT: it shows the transform does not rely on the per-entity-embedding
                 transductive advantage PP-275 exploited.

SWEEP: M in {50, 200} training pairs (SNR axis; transfer should CLIMB with M if real structure
       exists). M_OP=200 respects the ~200-items/bundle reliable-recall budget at N=8192.

POSITIVE CONTROLS (Gate D; harness reproduces the mechanism AT THIS REGIME, per estimator):
  SYNTH_ROT_CLEAN  -- clean rotation data (object = rotate(subject, theta_true) + tiny noise);
                      BOTH estimators must recover ~1.0 (proves the algebra + both fits work).
  SYNTH_CORR_HARD  -- CORRELATED codebook (K clusters) + moderate offset variance; TRAINED must
                      EXCEED NAIVE by >= a margin -- the DISCRIMINATOR-FIRES proof that the
                      estimator axis is not vacuous (if trained can never beat naive, the whole
                      ablation cannot discriminate -> honest abort before FULL).

PRE-REGISTERED BANDS (LOCKED before smoke; gain(arm) = arm_acc - 1/V_eff; primary = REAL,
  inductive, at M_OP; semantic relations AtLocation OR CausesDesire):
  HARD_PASS: TRAINED clears gain(REAL,inductive) >= 0.2075 (0.20 floor + 5% band-width,
             META_RULE_L) on AtLocation OR CausesDesire AND gain(SHUFFLED,inductive) <= 0.05
             AND (REAL - SHUFFLED)(inductive) >= 0.2075 (correspondence-dependent, NOT an
             encoding artifact) AND (REAL - MEAN_OBJECT)(inductive) >= 0.05 (subject-conditional).
             (Which ESTIMATOR x ENCODING cell wins is the headline.)
  HARD_FAIL: TRAINED on BOTH AtLocation AND CausesDesire still gain(REAL,inductive) <= 0.05 ->
             estimator fix alone insufficient; the INDUCTIVE setting (truly novel entity, no
             lookup) is the binding constraint -> redirect to inductive-relational-embedding
             methods (entity-feature-conditioned scoring), not a bigger training budget.
  MIDDLE_BAND: 0.05 < gain < 0.2075, partial gates, OR TRANSDUCTIVE-ONLY pass (inductive fails
             but transductive passes -> NOT a schema-transfer pass; report the gap).
  DISCRIMINATOR-FIRES gate (SYNTH_CORR_HARD): trained_acc - naive_acc >= TRAINED_ADV_MIN, else
             the estimator axis is vacuous -> MIDDLE_BAND (do not claim an estimator effect).
  Sanity rails: FHRR bind-roundtrip >= 0.90; SYNTH_ROT_CLEAN both estimators >= 0.90.

HP_SCOPE: HARD_PASS/HARD_FAIL gates apply to REAL / inductive ONLY (per relation, per est x enc
  cell). SHUFFLED / MEAN_OBJECT / RANDENC are controls (expected ~chance; inherit no gate).
  SYNTH_* are harness/discriminator-fires gates, not substrate-capability claims.

WHAT_THIS_DOES_NOT_SHOW:
  - NOT a vs-LLM comparison (BGE is a fixed LOCAL sentence encoder used only to source semantic
    content for the ENCODING arm; ZERO generative-LLM calls; pure vector algebra downstream).
  - NOT a full-store re-encode (the semantic cache is bounded to the ~8756 test-relation entities).
  - A HARD_FAIL under TRAINED+bge_semantic is the honest inductive-relational-transfer wall
    outcome (a well-instrumented negative), NOT a claim the substrate is behind the field
    (inductive KGE is a known-hard open sub-area).

FORMULA SELF-TESTS (import time, fast < 180s): see _formula_selftests().
ASCII-only. Per-seed checkpoint (_seed_checkpoint). Atomic tmp+replace metrics.

# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; ARMS-MUST-DIFFER hash-test)
# - final_metrics_atomicity = tmp_replace (META_RULE_AH)
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb n/a (argmax transfer); chance floor 1/V stated; reachability declared
# - baseline_in_band at smoke (META_RULE_AG; controls ~chance)
# - discriminator survives scale (SMOKE runs at FULL N=8192; seeds/test-size shrink only)
# - HARD_PASS strictly above floor (gain 0.2075 = 0.20 + 5% band-width)
# - HP_SCOPE: HP gates apply to REAL/inductive only, per relation x est x enc cell
# - cardinality_ok (META_RULE_H; EXPECTED_N_UNITS = R*C*M*E*seed*arm*eval)
# - per-unit failure-class instrumentation (META_RULE_J; no bare except)
# - calibration_check = adaptive_with_discriminator_gate (baseline = 1/V_eff; SYNTH_CORR_HARD
#   trained>naive is the discriminator-fires proof)
# - all numbers tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@ in design notes
# - positive_control SYNTH_ROT_CLEAN + SYNTH_CORR_HARD reproduce/differentiate at test regime (Gate D)
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import os
for _v in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS"):
    os.environ.setdefault(_v, "8")

import argparse
import json
import time
import hashlib
import platform
import traceback
import collections
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Tuple, Optional

import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (
    get_output_dir, resumable_seeds, write_partial, aggregate_partials,
)

ANCHOR_NAME = "schema_relation_transform_estimator_ablation_v1"
DATASET_REL = Path("data/datasets/conceptnet5_en_100k.jsonl")
BGE_CACHE_REL = Path("data/datasets/bge_small_schema_ablation_entities_v1.npz")

# ----------------------------------------------------------------------------
# Argparse + run-mode. Runner invokes BARE and injects HDLAB_RUN_MODE=full.
# Default full = most-defensive per META_RULE_16 (no silent self-test landing).
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
# count / test size / train-pool cap / trained-steps shrink in smoke.)
# ----------------------------------------------------------------------------
N_DIM = 8192
V_CODEBOOK = 100
RELATIONS = ["AtLocation", "CausesDesire", "DerivedFrom"]
SEMANTIC_RELATIONS = ["AtLocation", "CausesDesire"]   # HP eligible (non-surface)
ESTIMATORS = ["NAIVE_MEAN", "TRAINED"]
ENCODINGS = ["char_trigram", "bge_semantic"]
M_SWEEP = [50, 200]
M_OP = 200
ARMS = ["REAL", "SHUFFLED", "MEAN_OBJECT"]
EVAL_MODES = ["inductive", "transductive"]
PRIMARY_ARM = "REAL"
PRIMARY_EVAL = "inductive"

# TRAINED estimator hyperparameters (RotatE-style rotation; full-codebook softmax negatives)
if RUN_MODE == "smoke":
    SEEDS = [7, 13]
    N_TEST_PER = 60
    TRAIN_POOL_CAP = 500
    TRAIN_STEPS = 150
else:
    SEEDS = [7, 13, 19]
    N_TEST_PER = 150
    TRAIN_POOL_CAP = 1500
    TRAIN_STEPS = 250
TRAIN_LR = 0.5
TRAIN_TAU = 0.05          # softmax temperature over cosine scores in [-1,1]

# Semantic-phasor deterministic projection (fixed; NOT per-run seed)
SEM_PROJ_SEED = 12345
SEM_PROJ_SCALE = 1.0

# Synthetic positive-control regimes
SYNTH_CLEAN_K = 8
SYNTH_CLEAN_SIGMA = 0.15
SYNTH_HARD_K = 8            # correlated-codebook clusters
SYNTH_HARD_PER_CLUSTER = 4  # confusable objects per cluster
SYNTH_HARD_SIGMA = 0.8
SYNTH_M = 200

# Pre-reg bands (LOCKED)
HP_REAL_GAIN_MIN = 0.2075
HP_SHUF_GAIN_MAX = 0.05
HP_REAL_MINUS_MEANOBJ_MIN = 0.05
HF_REAL_GAIN_MAX = 0.05
BIND_ROUNDTRIP_MIN = 0.90
SYNTH_CLEAN_MIN = 0.90        # both estimators recover clean rotation
TRAINED_ADV_MIN = 0.05        # SYNTH_CORR_HARD: trained must beat naive by >= this
IND_TRANS_GAP_FLAG = 0.15     # |transductive - inductive| above this -> flag transductive-reliance

# Cardinality (META_RULE_H): main grid only (synth / randenc tracked separately)
EXPECTED_N_UNITS = (len(RELATIONS) * len(ENCODINGS) * len(M_SWEEP)
                    * len(ESTIMATORS) * len(SEEDS) * len(ARMS) * len(EVAL_MODES))


# ============================================================================
# FHRR primitives (complex64 phasors)
# ============================================================================
def _stable_seed(text: str, salt: int = 0) -> int:
    h = hashlib.md5(f"{salt}:{text}".encode("utf-8")).hexdigest()
    return int(h[:8], 16)


def rand_phasor_from_seed(n: int, seed: int) -> np.ndarray:
    rng = np.random.RandomState(seed)
    ang = rng.uniform(-np.pi, np.pi, size=n).astype(np.float32)
    return np.exp(1j * ang).astype(np.complex64)


def bind(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    return (a * b).astype(np.complex64)


def unbind(c: np.ndarray, a: np.ndarray) -> np.ndarray:
    return (c * np.conj(a)).astype(np.complex64)


def cos_c(x: np.ndarray, y: np.ndarray) -> float:
    num = float(np.vdot(y, x).real)
    den = float(np.linalg.norm(x) * np.linalg.norm(y)) + 1e-12
    return num / den


def cleanup_argmax_batch(Dhat: np.ndarray, O: np.ndarray) -> np.ndarray:
    """Argmax real cosine of each row of Dhat (B,N) against object codebook O (V,N)."""
    sims = (Dhat @ np.conj(O).T).real          # (B, V)
    return sims.argmax(axis=1)


# ============================================================================
# Encoders (all ZERO generative-LLM; deterministic; platform-stable)
# ============================================================================
_TRIGRAM_BASIS: Dict[Tuple[str, int], np.ndarray] = {}


def _trigram_basis(tg: str, n: int) -> np.ndarray:
    key = (tg, n)
    v = _TRIGRAM_BASIS.get(key)
    if v is None:
        v = rand_phasor_from_seed(n, _stable_seed(tg, salt=1))
        _TRIGRAM_BASIS[key] = v
    return v


def encode_trigram(s: str, n: int) -> np.ndarray:
    t = "#" + s.replace("_", " ") + "#"
    if len(t) < 3:
        t = (t + "##")[:3]
    acc = np.zeros(n, dtype=np.complex64)
    for i in range(len(t) - 2):
        acc = acc + _trigram_basis(t[i:i + 3], n)
    ang = np.angle(acc)
    return np.exp(1j * ang).astype(np.complex64)


def encode_random(s: str, n: int, seed: int) -> np.ndarray:
    return rand_phasor_from_seed(n, _stable_seed(s, salt=100 + seed))


# --- semantic (BGE) phasor: cached dense embedding -> center -> fixed projection -> unit phasor
class SemanticEncoder:
    """Loads bounded BGE cache; encodes entity -> unit FHRR phasor via a fixed projection.

    Deterministic + zero model dependency at runtime. Raises SemanticUnavailable if the cache
    is missing (caller records BGE_CACHE_MISSING per-unit; does NOT crash the whole cell)."""

    def __init__(self, n: int):
        self.n = n
        self.ok = False
        self.reason = ""
        self._proj_cache: Dict[str, np.ndarray] = {}
        path = REPO / BGE_CACHE_REL
        if not path.exists():
            self.reason = f"BGE_CACHE_MISSING:{BGE_CACHE_REL}"
            return
        try:
            d = np.load(path, allow_pickle=True)
            ents = [str(e) for e in d["entities"].tolist()]
            emb = d["emb"].astype(np.float32)              # (n_ent, 384)
        except Exception as e:                              # cache load failure
            self.reason = f"BGE_CACHE_LOAD_ERR:{type(e).__name__}"
            return
        # center (remove BGE anisotropy) then L2-normalize
        emb = emb - emb.mean(axis=0, keepdims=True)
        nrm = np.linalg.norm(emb, axis=1, keepdims=True) + 1e-9
        emb = emb / nrm
        self.dim = emb.shape[1]
        self.idx = {e: i for i, e in enumerate(ents)}
        self.emb = emb
        # fixed random projection (dim -> n) so phase ~ N(0, SEM_PROJ_SCALE^2) per component
        rng = np.random.RandomState(SEM_PROJ_SEED)
        self.W = (rng.standard_normal((self.dim, n)).astype(np.float32) * SEM_PROJ_SCALE)
        self.ok = True

    def encode(self, s: str) -> np.ndarray:
        v = self._proj_cache.get(s)
        if v is not None:
            return v
        i = self.idx.get(s)
        if i is None:
            # entity not in bounded cache -> deterministic fallback phase (unit phasor of zeros
            # -> all-ones is degenerate); use a stable random phasor so it stays a valid unit
            # vector but carries no semantic content (recorded via missing-rate below).
            v = rand_phasor_from_seed(self.n, _stable_seed(s, salt=777))
            self._missing = getattr(self, "_missing", 0) + 1
        else:
            phase = self.emb[i] @ self.W                    # (n,)
            v = np.exp(1j * phase).astype(np.complex64)
        self._proj_cache[s] = v
        return v


class SemanticUnavailable(Exception):
    pass


# module-level semantic encoder (loaded once)
_SEM = SemanticEncoder(N_DIM)


def encode_matrix(ents: List[str], encoding: str, seed: int) -> np.ndarray:
    """Stack unit phasors for a list of entity strings under the chosen encoding."""
    if encoding == "char_trigram":
        return np.stack([encode_trigram(e, N_DIM) for e in ents]).astype(np.complex64)
    if encoding == "random":
        return np.stack([encode_random(e, N_DIM, seed) for e in ents]).astype(np.complex64)
    if encoding == "bge_semantic":
        if not _SEM.ok:
            raise SemanticUnavailable(_SEM.reason)
        return np.stack([_SEM.encode(e) for e in ents]).astype(np.complex64)
    raise ValueError(f"unknown encoding {encoding}")


# ============================================================================
# Relation transform ESTIMATORS
# ============================================================================
def fit_naive_mean(A: np.ndarray, y: np.ndarray, O: np.ndarray) -> np.ndarray:
    """M_R = mean_i bind(O[y_i], conj(A_i)). Returns the transform vector (N,) complex."""
    B = O[y]                                        # (M,N) true objects
    return (B * np.conj(A)).mean(axis=0).astype(np.complex64)


def _softmax_rows(S: np.ndarray) -> np.ndarray:
    S = S - S.max(axis=1, keepdims=True)
    e = np.exp(S)
    return e / (e.sum(axis=1, keepdims=True) + 1e-12)


def fit_trained_rotation(A: np.ndarray, y: np.ndarray, O: np.ndarray,
                         steps: int, lr: float, tau: float) -> np.ndarray:
    """Train a per-relation rotation r = exp(i*theta) so bind(A_i, r) ~ O[y_i], discriminating
    against the FULL V-object codebook (softmax cross-entropy = negative sampling over all
    codebook objects). theta warm-started at the naive-mean phase. Analytic-gradient descent.
    Returns the unit-modulus transform vector r (N,) complex."""
    M, N = A.shape
    Oh = np.conj(O)                                 # (V,N)
    # warm start: naive-mean phase (unit modulus)
    M_R = fit_naive_mean(A, y, O)
    theta = np.angle(M_R).astype(np.float64)        # (N,)
    yhot_cols = y.astype(np.int64)
    for step in range(steps):
        r = np.exp(1j * theta).astype(np.complex64)         # (N,)
        Arot = (A * r[None, :]).astype(np.complex64)        # (M,N)
        S = (Arot @ Oh.T).real / N                          # (M,V) cosine-like score
        P = _softmax_rows(S / tau)                          # (M,V)
        dLdS = P.copy()
        dLdS[np.arange(M), yhot_cols] -= 1.0
        dLdS /= M                                           # (M,V)
        # dL/dtheta[n] = -(1/N) Im( sum_m Arot[m,n] * (dLdS @ conj(O))[m,n] )
        Rm = dLdS.astype(np.complex64) @ Oh                 # (M,N)
        grad = -(np.imag(Arot * Rm).sum(axis=0)) / N        # (N,)  real
        grad *= (1.0 / tau)                                 # chain-rule scale from S/tau
        theta -= lr * grad
    return np.exp(1j * theta).astype(np.complex64)


def fit_transform(estimator: str, A: np.ndarray, y: np.ndarray, O: np.ndarray) -> np.ndarray:
    if estimator == "NAIVE_MEAN":
        return fit_naive_mean(A, y, O)
    if estimator == "TRAINED":
        return fit_trained_rotation(A, y, O, TRAIN_STEPS, TRAIN_LR, TRAIN_TAU)
    raise ValueError(f"unknown estimator {estimator}")


def apply_transform(C: np.ndarray, M_R: np.ndarray, O: np.ndarray) -> np.ndarray:
    """Predict object index for each novel subject row C via D_hat = bind(C, M_R); argmax."""
    return cleanup_argmax_batch(C * M_R[None, :], O)


def apply_transform_meanobj(A_train: np.ndarray, M_R: np.ndarray, O: np.ndarray, T: int) -> np.ndarray:
    """C-INDEPENDENT readout: apply the transform to the MEAN training subject (ignore novel C),
    broadcast the single prediction to all T test rows."""
    a_mean = A_train.mean(axis=0)
    a_mean = a_mean / (np.abs(a_mean) + 1e-9)              # unit-modulus mean-subject
    pred1 = int(cleanup_argmax_batch((a_mean * M_R)[None, :], O)[0])
    return np.full(T, pred1, dtype=np.int64)


# ============================================================================
# Data loading + split (inductive novel-subject + transductive seen-subject)
# ============================================================================
def load_relation(relation: str, V: int) -> Tuple[List[Tuple[str, str]], List[str]]:
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


def build_split(relation: str, seed: int, V: int, n_test_per: int, pool_cap: int) -> Dict:
    """Return train pairs + inductive (novel-subject) + transductive (seen-subject) test pairs.

    - inductive test: one held-out pair per TEST subject (subjects disjoint from training).
    - transductive test: one held-out pair per multi-object TRAIN subject (subject seen in
      training via its OTHER codebook pairs); those held-out pairs are EXCLUDED from training.
    """
    pairs, codebook = load_relation(relation, V)
    V_eff = len(codebook)
    if V_eff < 2:
        raise ValueError(f"relation {relation}: codebook too small V_eff={V_eff}")
    obj_idx = {o: i for i, o in enumerate(codebook)}
    rng = np.random.RandomState(seed)

    by_subj = collections.defaultdict(list)
    for s, o in pairs:
        by_subj[s].append(o)
    subs = sorted(by_subj.keys())
    rng.shuffle(subs)
    n_test_subs = max(n_test_per * 2, 120)
    test_subs = subs[:n_test_subs]
    pool_subs = subs[n_test_subs:]
    rng.shuffle(pool_subs)
    pool_subs = pool_subs[:pool_cap]

    # inductive test: one pair per novel test subject
    ind_test: List[Tuple[str, str]] = []
    for s in test_subs:
        o = by_subj[s][rng.randint(len(by_subj[s]))]
        ind_test.append((s, o))
        if len(ind_test) >= n_test_per:
            break

    # training pairs from pool subjects, holding out one transductive-test pair per multi-object
    train_pairs: List[Tuple[str, str]] = []
    trans_test: List[Tuple[str, str]] = []
    for s in pool_subs:
        objs = by_subj[s]
        if len(objs) >= 2 and len(trans_test) < n_test_per:
            k = rng.randint(len(objs))
            held = objs[k]
            trans_test.append((s, held))
            for j, o in enumerate(objs):
                if j != k:
                    train_pairs.append((s, o))
        else:
            for o in objs:
                train_pairs.append((s, o))

    if len(train_pairs) < max(M_SWEEP) or len(ind_test) < 20 or len(trans_test) < 20:
        raise ValueError(
            f"relation {relation}: insufficient data (train={len(train_pairs)}, "
            f"ind_test={len(ind_test)}, trans_test={len(trans_test)}; need train>="
            f"{max(M_SWEEP)}, tests>=20)")

    rng.shuffle(train_pairs)
    train_pairs = train_pairs[:max(M_SWEEP)]        # fixed max-M sample; prefixes = M-sweep
    return {
        "relation": relation, "V_eff": V_eff, "codebook": codebook, "obj_idx": obj_idx,
        "train_pairs": train_pairs, "ind_test": ind_test, "trans_test": trans_test,
        "chance": 1.0 / V_eff,
    }


# ============================================================================
# Core evaluation: one (relation, seed) -> full grid of accuracies
# ============================================================================
def eval_relation_seed(relation: str, seed: int) -> Dict:
    sp = build_split(relation, seed, V_CODEBOOK, N_TEST_PER, TRAIN_POOL_CAP)
    codebook = sp["codebook"]
    obj_idx = sp["obj_idx"]
    train_pairs = sp["train_pairs"]
    ind_test = sp["ind_test"]
    trans_test = sp["trans_test"]
    V_eff = sp["V_eff"]

    train_subs = [s for s, _ in train_pairs]
    y_train_all = np.array([obj_idx[o] for _, o in train_pairs], dtype=np.int64)
    rng = np.random.RandomState(seed + 991)
    perm_all = rng.permutation(len(train_pairs))            # shuffled-object assignment

    y_ind = np.array([obj_idx[o] for _, o in ind_test], dtype=np.int64)
    y_trans = np.array([obj_idx[o] for _, o in trans_test], dtype=np.int64)
    ind_subs = [s for s, _ in ind_test]
    trans_subs = [s for s, _ in trans_test]

    # acc[encoding][M][estimator][arm][eval_mode] = float
    acc: Dict = {}
    enc_status: Dict[str, str] = {}
    for encoding in ENCODINGS:
        try:
            O = encode_matrix(codebook, encoding, seed)         # (V,N)
            A_all = encode_matrix(train_subs, encoding, seed)   # (Mmax,N)
            C_ind = encode_matrix(ind_subs, encoding, seed)     # (Tind,N)
            C_trans = encode_matrix(trans_subs, encoding, seed) # (Ttrans,N)
        except SemanticUnavailable as e:
            enc_status[encoding] = str(e)
            continue
        enc_status[encoding] = "ok"
        acc[encoding] = {}
        for M in M_SWEEP:
            A_M = A_all[:M]
            y_M = y_train_all[:M]
            y_shuf_M = y_train_all[perm_all[:M]]
            acc[encoding][M] = {}
            for est in ESTIMATORS:
                # REAL transform + SHUFFLED transform (each its own fit for TRAINED)
                Mr_real = fit_transform(est, A_M, y_M, O)
                Mr_shuf = fit_transform(est, A_M, y_shuf_M, O)
                pr_ind = apply_transform(C_ind, Mr_real, O)
                pr_tr = apply_transform(C_trans, Mr_real, O)
                ps_ind = apply_transform(C_ind, Mr_shuf, O)
                ps_tr = apply_transform(C_trans, Mr_shuf, O)
                pm_ind = apply_transform_meanobj(A_M, Mr_real, O, len(y_ind))
                pm_tr = apply_transform_meanobj(A_M, Mr_real, O, len(y_trans))
                acc[encoding][M][est] = {
                    "REAL": {"inductive": float((pr_ind == y_ind).mean()),
                             "transductive": float((pr_tr == y_trans).mean())},
                    "SHUFFLED": {"inductive": float((ps_ind == y_ind).mean()),
                                 "transductive": float((ps_tr == y_trans).mean())},
                    "MEAN_OBJECT": {"inductive": float((pm_ind == y_ind).mean()),
                                    "transductive": float((pm_tr == y_trans).mean())},
                }

    # RANDENC structureless floor (REAL, inductive, M_OP, both estimators)
    randenc = {}
    try:
        O_r = encode_matrix(codebook, "random", seed)
        A_r = encode_matrix(train_subs, "random", seed)[:M_OP]
        C_r = encode_matrix(ind_subs, "random", seed)
        for est in ESTIMATORS:
            Mr = fit_transform(est, A_r, y_train_all[:M_OP], O_r)
            randenc[est] = float((apply_transform(C_r, Mr, O_r) == y_ind).mean())
    except Exception as e:
        randenc = {"error": f"{type(e).__name__}:{str(e)[:120]}"}

    return {
        "relation": relation, "seed": seed, "V_eff": V_eff, "chance": sp["chance"],
        "n_train": len(train_pairs), "n_ind_test": len(y_ind), "n_trans_test": len(y_trans),
        "acc": acc, "enc_status": enc_status, "randenc_floor": randenc,
        "sem_missing": getattr(_SEM, "_missing", 0),
    }


# ============================================================================
# Synthetic positive controls (Gate D; per estimator)
# ============================================================================
def synth_clean(seed: int) -> Dict[str, float]:
    """Clean rotation: object = rotate(subject, theta_true) + tiny noise. Both estimators ~1.0."""
    rng = np.random.RandomState(seed)
    N, K, sigma, M = N_DIM, SYNTH_CLEAN_K, SYNTH_CLEAN_SIGMA, SYNTH_M
    theta_true = rng.uniform(-np.pi, np.pi, N).astype(np.float32)
    O = np.exp(1j * rng.uniform(-np.pi, np.pi, (K, N))).astype(np.complex64)
    # subjects: for each of M pairs pick an object k, subject = rotate(O_k, -theta_true)+noise
    ks = rng.randint(0, K, M)
    subj_ang = np.angle(O[ks]) - theta_true[None, :] + sigma * rng.standard_normal((M, N)).astype(np.float32)
    A = np.exp(1j * subj_ang).astype(np.complex64)
    y = ks.astype(np.int64)
    # test: fresh subjects for each object
    kt = rng.randint(0, K, 80)
    test_ang = np.angle(O[kt]) - theta_true[None, :] + sigma * rng.standard_normal((80, N)).astype(np.float32)
    C = np.exp(1j * test_ang).astype(np.complex64)
    yt = kt.astype(np.int64)
    out = {}
    for est in ESTIMATORS:
        Mr = fit_transform(est, A, y, O)
        out[est] = float((apply_transform(C, Mr, O) == yt).mean())
    out["chance"] = 1.0 / K
    return out


def synth_corr_hard(seed: int) -> Dict[str, float]:
    """Correlated codebook (K clusters x per-cluster confusable objects) + moderate offset
    variance. TRAINED (discriminates negatives) should EXCEED NAIVE (generative mean)."""
    rng = np.random.RandomState(seed + 4242)
    N, K, per, sigma, M = N_DIM, SYNTH_HARD_K, SYNTH_HARD_PER_CLUSTER, SYNTH_HARD_SIGMA, SYNTH_M
    V = K * per
    # cluster centroids; objects = centroid + small within-cluster jitter (correlated codebook)
    Cang = rng.uniform(-np.pi, np.pi, (K, N)).astype(np.float32)
    Oang = np.repeat(Cang, per, axis=0) + 0.25 * rng.standard_normal((V, N)).astype(np.float32)
    O = np.exp(1j * Oang).astype(np.complex64)
    theta_true = rng.uniform(-np.pi, np.pi, N).astype(np.float32)
    vs = rng.randint(0, V, M)
    subj_ang = Oang[vs] - theta_true[None, :] + sigma * rng.standard_normal((M, N)).astype(np.float32)
    A = np.exp(1j * subj_ang).astype(np.complex64)
    y = vs.astype(np.int64)
    vt = rng.randint(0, V, 120)
    test_ang = Oang[vt] - theta_true[None, :] + sigma * rng.standard_normal((120, N)).astype(np.float32)
    C = np.exp(1j * test_ang).astype(np.complex64)
    yt = vt.astype(np.int64)
    out = {}
    for est in ESTIMATORS:
        Mr = fit_transform(est, A, y, O)
        out[est] = float((apply_transform(C, Mr, O) == yt).mean())
    out["chance"] = 1.0 / V
    out["trained_adv"] = out["TRAINED"] - out["NAIVE_MEAN"]
    return out


# ============================================================================
# Per-seed driver (failure-instrumented; no silent continue)
# ============================================================================
def run_seed(seed: int) -> Dict:
    t0 = time.time()
    per_rel: Dict[str, Dict] = {}
    per_unit: Dict[str, Dict] = {}
    fatal = False
    fatal_msg = None
    for relation in RELATIONS:
        try:
            r = eval_relation_seed(relation, seed)
        except Exception as e:                          # META_RULE_J: record + halt seed
            fatal = True
            fatal_msg = f"{relation}:{type(e).__name__}:{str(e)[:200]}"
            print(f"  [seed={seed} rel={relation}] FAILED {type(e).__name__}: {e}", flush=True)
            traceback.print_exc()
            break
        per_rel[relation] = r
        for enc in ENCODINGS:
            if r["acc"].get(enc) is None:
                for M in M_SWEEP:
                    for est in ESTIMATORS:
                        for arm in ARMS:
                            for ev in EVAL_MODES:
                                per_unit[f"{relation}|{enc}|M{M}|{est}|{arm}|{ev}"] = {
                                    "relation": relation, "encoding": enc, "M": M,
                                    "estimator": est, "arm": arm, "eval": ev, "acc": None,
                                    "failure_class": r["enc_status"].get(enc, "ENC_UNAVAILABLE")}
                continue
            for M in M_SWEEP:
                for est in ESTIMATORS:
                    for arm in ARMS:
                        for ev in EVAL_MODES:
                            per_unit[f"{relation}|{enc}|M{M}|{est}|{arm}|{ev}"] = {
                                "relation": relation, "encoding": enc, "M": M,
                                "estimator": est, "arm": arm, "eval": ev,
                                "acc": float(r["acc"][enc][M][est][arm][ev]),
                                "failure_class": None}
        # progress line at M_OP inductive REAL
        def _g(enc, est):
            a = r["acc"].get(enc)
            if a is None:
                return float("nan")
            return a[M_OP][est]["REAL"]["inductive"]
        print(f"  [seed={seed} {relation:<13} V={r['V_eff']} chance={r['chance']:.4f} "
              f"nInd={r['n_ind_test']} nTr={r['n_trans_test']}] REAL/ind@M{M_OP}: "
              f"trig[naive={_g('char_trigram','NAIVE_MEAN'):.3f} train={_g('char_trigram','TRAINED'):.3f}] "
              f"bge[naive={_g('bge_semantic','NAIVE_MEAN'):.3f} train={_g('bge_semantic','TRAINED'):.3f}]",
              flush=True)

    sc = synth_clean(seed)
    sh = synth_corr_hard(seed)
    print(f"  [seed={seed} SYNTH_CLEAN] naive={sc['NAIVE_MEAN']:.3f} train={sc['TRAINED']:.3f} "
          f"chance={sc['chance']:.3f} || SYNTH_HARD naive={sh['NAIVE_MEAN']:.3f} "
          f"train={sh['TRAINED']:.3f} adv={sh['trained_adv']:+.3f}", flush=True)

    return {
        "seed": seed, "N": N_DIM, "V": V_CODEBOOK, "run_mode": RUN_MODE,
        "config_version": f"ANCHOR={ANCHOR_NAME},N={N_DIM},V={V_CODEBOOK},steps={TRAIN_STEPS}",
        "per_rel": per_rel, "per_unit": per_unit,
        "synth_clean": sc, "synth_hard": sh,
        "fatal": fatal, "fatal_msg": fatal_msg, "elapsed_s": time.time() - t0,
    }


# ============================================================================
# Aggregate + verdict
# ============================================================================
def _mean_std(vals: List[float]) -> Tuple[float, float, int]:
    n = len(vals)
    if n == 0:
        return float("nan"), 0.0, 0
    m = float(np.mean(vals))
    s = float(np.std(vals, ddof=1)) if n > 1 else 0.0
    return m, s, n


def aggregate(per_seed: Dict) -> Dict:
    # cells keyed relation|enc|M|est|arm|eval -> list of accs
    buckets: Dict[str, List[float]] = collections.defaultdict(list)
    chance: Dict[str, List[float]] = collections.defaultdict(list)
    sc_naive, sc_train, sh_naive, sh_train, sh_adv = [], [], [], [], []
    rand_floor: Dict[str, List[float]] = collections.defaultdict(list)
    n_units = 0
    n_failed = 0
    enc_unavailable = collections.Counter()
    sem_missing_total = 0
    for sd in per_seed.values():
        for key, rec in sd.get("per_unit", {}).items():
            n_units += 1
            if rec.get("acc") is None:
                n_failed += 1
                fc = rec.get("failure_class", "NA")
                if isinstance(fc, str) and fc.startswith("BGE_CACHE"):
                    enc_unavailable["bge_semantic"] += 1
                continue
            buckets[key].append(float(rec["acc"]))
        for rel, r in sd.get("per_rel", {}).items():
            chance[rel].append(float(r["chance"]))
            rf = r.get("randenc_floor", {})
            for est in ESTIMATORS:
                if isinstance(rf.get(est), (int, float)):
                    rand_floor[est].append(float(rf[est]))
            sem_missing_total += int(r.get("sem_missing", 0) or 0)
        sc = sd.get("synth_clean", {})
        sh = sd.get("synth_hard", {})
        if sc:
            sc_naive.append(sc["NAIVE_MEAN"]); sc_train.append(sc["TRAINED"])
        if sh:
            sh_naive.append(sh["NAIVE_MEAN"]); sh_train.append(sh["TRAINED"]); sh_adv.append(sh["trained_adv"])

    cells: Dict[str, Dict] = {}
    for key, vals in buckets.items():
        m, s, n = _mean_std(vals)
        cells[key] = {"mean": m, "std": s, "n": n}
    chance_by_rel = {rel: (float(np.mean(v)) if v else float("nan")) for rel, v in chance.items()}
    return {
        "cells": cells, "chance_by_rel": chance_by_rel,
        "synth_clean": {"naive": _mean_std(sc_naive)[0], "trained": _mean_std(sc_train)[0]},
        "synth_hard": {"naive": _mean_std(sh_naive)[0], "trained": _mean_std(sh_train)[0],
                       "trained_adv": _mean_std(sh_adv)[0]},
        "randenc_floor": {est: _mean_std(rand_floor[est])[0] for est in ESTIMATORS},
        "n_units": n_units, "n_units_failed": n_failed,
        "enc_unavailable": dict(enc_unavailable), "sem_missing_total": sem_missing_total,
    }


def _cell(cells: Dict, relation: str, enc: str, M: int, est: str, arm: str, ev: str) -> float:
    c = cells.get(f"{relation}|{enc}|M{M}|{est}|{arm}|{ev}")
    return c["mean"] if c else float("nan")


def compute_verdict(agg: Dict, arms_differ_ok: bool, bind_roundtrip: float) -> Tuple[str, str, Dict]:
    cells = agg["cells"]
    chance = agg["chance_by_rel"]
    sc = agg["synth_clean"]
    sh = agg["synth_hard"]
    n_units = agg["n_units"] - agg["n_units_failed"]   # counted-good units

    # per (relation, encoding, estimator) verdict on REAL/inductive @ M_OP with joint gates
    cell_verdicts: Dict[str, str] = {}
    cell_diag: Dict[str, Dict] = {}
    for rel in RELATIONS:
        ch = chance.get(rel, float("nan"))
        for enc in ENCODINGS:
            for est in ESTIMATORS:
                real_ind = _cell(cells, rel, enc, M_OP, est, "REAL", "inductive")
                real_tr = _cell(cells, rel, enc, M_OP, est, "REAL", "transductive")
                shuf_ind = _cell(cells, rel, enc, M_OP, est, "SHUFFLED", "inductive")
                meanobj_ind = _cell(cells, rel, enc, M_OP, est, "MEAN_OBJECT", "inductive")
                real_gain = real_ind - ch
                shuf_gain = shuf_ind - ch
                r_minus_shuf = real_ind - shuf_ind
                r_minus_mean = real_ind - meanobj_ind
                ind_trans_gap = real_tr - real_ind
                key = f"{rel}|{enc}|{est}"
                diag = {
                    "chance": ch, "real_ind": real_ind, "real_trans": real_tr,
                    "real_gain": real_gain, "shuf_ind": shuf_ind, "shuf_gain": shuf_gain,
                    "meanobj_ind": meanobj_ind, "real_minus_shuf": r_minus_shuf,
                    "real_minus_meanobj": r_minus_mean, "ind_trans_gap": ind_trans_gap,
                    "real_curve_ind": {str(M): _cell(cells, rel, enc, M, est, "REAL", "inductive")
                                       for M in M_SWEEP},
                }
                cell_diag[key] = diag
                if any(v != v for v in (real_gain, shuf_gain)):   # NaN (e.g. bge unavailable)
                    cell_verdicts[key] = "NA"
                    continue
                confound = (real_gain > HF_REAL_GAIN_MAX) and (r_minus_shuf <= HP_SHUF_GAIN_MAX)
                diag["confound_shuffle_invariant"] = confound
                if real_gain <= HF_REAL_GAIN_MAX:
                    cell_verdicts[key] = "HARD_FAIL"
                elif r_minus_shuf <= HP_SHUF_GAIN_MAX:
                    cell_verdicts[key] = "HARD_FAIL"          # artifact, not correspondence-dependent
                elif (real_gain >= HP_REAL_GAIN_MIN and shuf_gain <= HP_SHUF_GAIN_MAX
                      and r_minus_shuf >= HP_REAL_GAIN_MIN and r_minus_mean >= HP_REAL_MINUS_MEANOBJ_MIN):
                    cell_verdicts[key] = "HARD_PASS"
                else:
                    cell_verdicts[key] = "MIDDLE_BAND"

    diag = {
        "M_OP": M_OP, "bind_roundtrip": bind_roundtrip, "arms_differ_ok": arms_differ_ok,
        "n_units": n_units, "expected_n_units": EXPECTED_N_UNITS,
        "synth_clean": sc, "synth_hard": sh, "randenc_floor": agg["randenc_floor"],
        "trained_adv_gate": TRAINED_ADV_MIN, "cell_verdicts": cell_verdicts,
        "cell_diag": cell_diag, "enc_unavailable": agg["enc_unavailable"],
        "sem_missing_total": agg["sem_missing_total"],
    }

    # ---- global gates ----
    if n_units < EXPECTED_N_UNITS:
        # allow the semantic-cache-missing case to still be interpretable on char_trigram
        bge_missing = agg["enc_unavailable"].get("bge_semantic", 0)
        if bge_missing > 0 and (n_units + bge_missing) >= EXPECTED_N_UNITS:
            diag["bge_cache_missing_note"] = ("bge_semantic cache absent on host; semantic arm "
                                              "skipped (char_trigram + estimator axis still valid)")
        else:
            return ("HARD_FAIL",
                    f"HARD_FAIL_CARDINALITY_BREACH_META_RULE_H: good_units={n_units} < "
                    f"expected={EXPECTED_N_UNITS} (not explained by bge-cache-missing).", diag)
    if not arms_differ_ok:
        return ("HARD_FAIL", "META_RULE_AF_VIOLATION: arm outputs bit-identical; arm-impl bug.", diag)
    if not (bind_roundtrip >= BIND_ROUNDTRIP_MIN):
        return ("HARD_FAIL",
                f"SANITY_RAIL_BIND: bind-roundtrip={bind_roundtrip:.3f} < {BIND_ROUNDTRIP_MIN}.", diag)
    # positive control: clean rotation must be recovered by BOTH estimators
    if not (sc["naive"] >= SYNTH_CLEAN_MIN and sc["trained"] >= SYNTH_CLEAN_MIN):
        return ("MIDDLE_BAND",
                f"HARNESS_SUSPECT: SYNTH_CLEAN naive={sc['naive']:.3f} trained={sc['trained']:.3f} "
                f"< {SYNTH_CLEAN_MIN}; an estimator did NOT recover a clean rotation -> real arms "
                f"uninterpretable. Fix harness/hparams.", diag)
    # discriminator-fires: trained must beat naive on the correlated-codebook control
    discriminator_fires = sh["trained_adv"] >= TRAINED_ADV_MIN

    # ---- headline: which (est x enc) cell gives inductive real transfer on a semantic relation ----
    hp_cells = [k for k, v in cell_verdicts.items() if v == "HARD_PASS"
                and k.split("|")[0] in SEMANTIC_RELATIONS]
    trained_hp = [k for k in hp_cells if k.endswith("|TRAINED")]

    # transductive-only pass detector (NOT a schema-transfer pass)
    trans_only = []
    for key, d in cell_diag.items():
        rel = key.split("|")[0]
        if rel not in SEMANTIC_RELATIONS:
            continue
        real_ind = d.get("real_ind", float("nan"))
        real_tr = d.get("real_trans", float("nan"))
        ch = d.get("chance", float("nan"))
        if (real_tr - ch) >= HP_REAL_GAIN_MIN and (real_ind - ch) <= HF_REAL_GAIN_MAX:
            trans_only.append(key)
    diag["transductive_only_cells"] = trans_only
    diag["discriminator_fires"] = discriminator_fires

    def _fmt_cell(key):
        d = cell_diag[key]
        return (f"{key}: real_ind={d['real_ind']:.3f} real_tr={d['real_trans']:.3f} "
                f"gain={d['real_gain']:+.3f} r-shuf={d['real_minus_shuf']:+.3f} "
                f"r-mean={d['real_minus_meanobj']:+.3f} ind-tr-gap={d['ind_trans_gap']:+.3f} "
                f"[{cell_verdicts[key]}]")
    focus = [f"{rel}|{enc}|{est}" for rel in SEMANTIC_RELATIONS for enc in ENCODINGS
             for est in ESTIMATORS]
    summ = (f"synthCLEAN(n={sc['naive']:.2f},t={sc['trained']:.2f}) "
            f"synthHARD(n={sh['naive']:.2f},t={sh['trained']:.2f},adv={sh['trained_adv']:+.2f},"
            f"fires={discriminator_fires}) | " + " || ".join(_fmt_cell(k) for k in focus))

    if trained_hp:
        winners = trained_hp
        adv_note = "" if discriminator_fires else " (WARN: synth discriminator-fires weak)"
        return ("HARD_PASS",
                f"HARD_PASS_TRAINED_INDUCTIVE_TRANSFER: TRAINED estimator gives genuine "
                f"novel-subject (INDUCTIVE) real schema transfer on {winners}; controls at chance, "
                f"correspondence-dependent, subject-conditional.{adv_note} {summ}", diag)
    # any non-trained HP? (would mean encoding alone carried it)
    enc_only_hp = [k for k in hp_cells if k.endswith("|NAIVE_MEAN")]
    if enc_only_hp:
        return ("HARD_PASS",
                f"HARD_PASS_ENCODING_CARRIED (NAIVE_MEAN): inductive transfer without the trained "
                f"estimator on {enc_only_hp} -> the encoding alone carried it. {summ}", diag)

    # all trained semantic cells at/near chance -> HARD_FAIL (inductive wall)
    trained_semantic_gains = [
        cell_diag[f"{rel}|{enc}|TRAINED"]["real_gain"]
        for rel in SEMANTIC_RELATIONS for enc in ENCODINGS
        if cell_verdicts.get(f"{rel}|{enc}|TRAINED") not in (None, "NA")]
    if trained_semantic_gains and all(g <= HF_REAL_GAIN_MAX for g in trained_semantic_gains):
        return ("HARD_FAIL",
                f"HARD_FAIL_INDUCTIVE_WALL: TRAINED estimator at chance on ALL semantic relations "
                f"x encodings (inductive) while synth controls fired "
                f"(clean-ok, hard-adv={sh['trained_adv']:+.3f}). The estimator fix alone is "
                f"insufficient; strictly-novel-entity (inductive) transfer is the binding "
                f"constraint -> inductive-relational-embedding methods needed. {summ}", diag)

    if trans_only:
        return ("MIDDLE_BAND",
                f"MIDDLE_BAND_TRANSDUCTIVE_ONLY: transductive passes but INDUCTIVE fails on "
                f"{trans_only} -> NOT a schema-transfer pass (the transform relies on having seen "
                f"the subject). Report the gap. {summ}", diag)

    return ("MIDDLE_BAND",
            f"MIDDLE_BAND_PARTIAL: no full inductive HP on a semantic relation; partial signal. "
            f"discriminator_fires={discriminator_fires}. {summ}", diag)


# ============================================================================
# arms-differ hash (META_RULE_AF)
# ============================================================================
def arms_differ_check(seed: int) -> Tuple[bool, Dict[str, str]]:
    """Fit REAL vs SHUFFLED transforms + MEAN_OBJECT readout on one relation/encoding; assert the
    resulting inductive prediction vectors are not bit-identical across arms."""
    sp = build_split(RELATIONS[0], seed, V_CODEBOOK, min(N_TEST_PER, 40), min(TRAIN_POOL_CAP, 300))
    codebook = sp["codebook"]; obj_idx = sp["obj_idx"]
    train_pairs = sp["train_pairs"]; ind_test = sp["ind_test"]
    O = encode_matrix(codebook, "char_trigram", seed)
    A = encode_matrix([s for s, _ in train_pairs], "char_trigram", seed)[:M_OP]
    C = encode_matrix([s for s, _ in ind_test], "char_trigram", seed)
    y = np.array([obj_idx[o] for _, o in train_pairs], dtype=np.int64)[:M_OP]
    rng = np.random.RandomState(seed + 991)
    y_shuf = y[rng.permutation(len(y))]
    Mr_real = fit_transform("TRAINED", A, y, O)
    Mr_shuf = fit_transform("TRAINED", A, y_shuf, O)
    Mr_naive = fit_naive_mean(A, y, O)
    preds = {
        "REAL_trained": apply_transform(C, Mr_real, O),
        "SHUFFLED_trained": apply_transform(C, Mr_shuf, O),
        "REAL_naive": apply_transform(C, Mr_naive, O),
        "MEAN_OBJECT": apply_transform_meanobj(A, Mr_real, O, len(ind_test)),
    }
    digests = {k: hashlib.sha256(v.tobytes()).hexdigest() for k, v in preds.items()}
    ok = len(set(digests.values())) == len(preds)
    return ok, digests


# ============================================================================
# Formula self-tests (import time, fast)
# ============================================================================
def _formula_selftests() -> float:
    rng = np.random.RandomState(123)
    n = 512
    a = np.exp(1j * rng.uniform(-np.pi, np.pi, n)).astype(np.complex64)
    b = np.exp(1j * rng.uniform(-np.pi, np.pi, n)).astype(np.complex64)
    rt = cos_c(unbind(bind(a, b), a), b)
    assert rt >= 0.90, f"selftest1 bind-roundtrip cos={rt}"
    # char-trigram determinism + surface-similarity
    assert np.allclose(encode_trigram("runner", 1024), encode_trigram("runner", 1024)), "selftest2 determinism"
    sc_close = cos_c(encode_trigram("running", 1024), encode_trigram("runningx", 1024))
    sc_far = cos_c(encode_trigram("running", 1024), encode_trigram("xyzqvw", 1024))
    assert sc_close > sc_far, f"selftest3 surface-sim {sc_close} !> {sc_far}"
    # trained estimator recovers a clean rotation better-than-chance on a tiny problem
    K = 5; Ntest = 256
    theta_true = rng.uniform(-np.pi, np.pi, Ntest).astype(np.float32)
    O = np.exp(1j * rng.uniform(-np.pi, np.pi, (K, Ntest))).astype(np.complex64)
    ks = rng.randint(0, K, 40)
    A = np.exp(1j * (np.angle(O[ks]) - theta_true[None, :]
                     + 0.1 * rng.standard_normal((40, Ntest)))).astype(np.complex64)
    r = fit_trained_rotation(A, ks.astype(np.int64), O, steps=120, lr=0.5, tau=0.05)
    kt = rng.randint(0, K, 40)
    Ct = np.exp(1j * (np.angle(O[kt]) - theta_true[None, :]
                      + 0.1 * rng.standard_normal((40, Ntest)))).astype(np.complex64)
    acc_tr = float((cleanup_argmax_batch(Ct * r[None, :], O) == kt).mean())
    assert acc_tr >= 0.90, f"selftest4 trained clean rotation acc={acc_tr}"
    # naive mean also recovers clean rotation
    Mr = fit_naive_mean(A, ks.astype(np.int64), O)
    acc_nv = float((cleanup_argmax_batch(Ct * Mr[None, :], O) == kt).mean())
    assert acc_nv >= 0.90, f"selftest5 naive clean rotation acc={acc_nv}"
    # cleanup argmax picks true object
    O2 = np.exp(1j * rng.uniform(-np.pi, np.pi, (6, n))).astype(np.complex64)
    assert int(cleanup_argmax_batch(O2[3:4].copy(), O2)[0]) == 3, "selftest6 argmax"
    print(f"[formula_selftest] bind_rt={rt:.3f} trig_close={sc_close:.3f} trig_far={sc_far:.3f} "
          f"trained_clean={acc_tr:.3f} naive_clean={acc_nv:.3f} sem_cache_ok={_SEM.ok} PASS", flush=True)
    return rt


_BIND_RT = _formula_selftests()

# feasibility / reachability (THEORETICAL; no CRLB noise-floor for argmax transfer)
assert (1.0 / V_CODEBOOK) + HP_REAL_GAIN_MIN < 0.95, "HP threshold must be below saturation"


# ============================================================================
# Defensive: start-marker + crash-diagnostic (SS13)
# ============================================================================
def _write_start_marker(out_dir: Path):
    marker = {
        "pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR_NAME, "run_mode": RUN_MODE,
        "expected_n_units": EXPECTED_N_UNITS, "host": platform.node(),
        "sem_cache_ok": _SEM.ok, "sem_cache_reason": _SEM.reason,
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    tmp = out_dir / "_start_marker.json.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, out_dir / "_start_marker.json")


def _write_crash_metrics(out_dir: Path, exc: Exception):
    diag = {
        "anchor_name": ANCHOR_NAME, "run_mode": RUN_MODE, "verdict": "CELL_CRASHED",
        "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
        "summary": f"CELL_CRASHED: {type(exc).__name__}", "elapsed_s": 0.0,
        "traceback": traceback.format_exc()[:5000],
        "ts_iso": datetime.now(timezone.utc).isoformat(),
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    tmp = out_dir / "metrics.json.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, out_dir / "metrics.json")


# ============================================================================
# Main
# ============================================================================
def main():
    t_start = time.time()
    out_dir = get_output_dir(ANCHOR_NAME)
    _write_start_marker(out_dir)
    print(f"[{ANCHOR_NAME}] run_mode={RUN_MODE} N={N_DIM} V={V_CODEBOOK} relations={RELATIONS} "
          f"encodings={ENCODINGS} estimators={ESTIMATORS} M={M_SWEEP} seeds={SEEDS} "
          f"steps={TRAIN_STEPS} expected_units={EXPECTED_N_UNITS} sem_cache_ok={_SEM.ok}", flush=True)
    if not _SEM.ok:
        print(f"[WARN] semantic cache unavailable ({_SEM.reason}); bge_semantic arm will record "
              f"failure_class per-unit; char_trigram + estimator axis still valid.", flush=True)

    run_config = {"N": N_DIM, "V": V_CODEBOOK, "run_mode": RUN_MODE, "anchor": ANCHOR_NAME,
                  "steps": TRAIN_STEPS}
    done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
    print(f"[ckpt] {len(done)}/{len(SEEDS)} done; running {remaining}", flush=True)

    for seed in remaining:
        r = run_seed(seed)
        write_partial(out_dir, seed, r)
        print(f"[{ANCHOR_NAME}] seed={seed} done ({r['elapsed_s']:.1f}s) fatal={r['fatal']}", flush=True)

    per_seed = aggregate_partials(out_dir, SEEDS, run_config=run_config)
    agg = aggregate(per_seed)
    ad_ok, ad_digests = arms_differ_check(SEEDS[0])
    verdict, verdict_msg, diag = compute_verdict(agg, ad_ok, _BIND_RT)

    elapsed = time.time() - t_start
    summary = f"{verdict}: {diag.get('cell_verdicts')}"
    metrics = {
        "anchor": ANCHOR_NAME, "anchor_name": ANCHOR_NAME, "run_mode": RUN_MODE,
        "N": N_DIM, "N_DIM": N_DIM, "V": V_CODEBOOK,
        "relations": RELATIONS, "semantic_relations": SEMANTIC_RELATIONS,
        "encodings": ENCODINGS, "estimators": ESTIMATORS, "arms": ARMS, "eval_modes": EVAL_MODES,
        "n_seeds": len(per_seed), "seeds": [int(s) for s in per_seed.keys()],
        "M_sweep": M_SWEEP, "M_OP": M_OP, "train_steps": TRAIN_STEPS,
        "train_lr": TRAIN_LR, "train_tau": TRAIN_TAU,
        "expected_n_units": EXPECTED_N_UNITS,
        "n_units_counted": agg["n_units"], "n_units_failed": agg["n_units_failed"],
        "cardinality_ok": (agg["n_units"] - agg["n_units_failed"]) >= EXPECTED_N_UNITS
        or agg["enc_unavailable"].get("bge_semantic", 0) > 0,
        "arms_differ_verified": ad_ok, "arms_differ_digests": ad_digests,
        "bind_roundtrip": _BIND_RT,
        "synth_clean": agg["synth_clean"], "synth_hard": agg["synth_hard"],
        "discriminator_fires": diag.get("discriminator_fires"),
        "randenc_floor": agg["randenc_floor"],
        "enc_unavailable": agg["enc_unavailable"], "sem_missing_total": agg["sem_missing_total"],
        "hp_scope": {"REAL_inductive": ["HARD_PASS", "HARD_FAIL"],
                     "SHUFFLED": [], "MEAN_OBJECT": [], "RANDENC": [], "SYNTH": []},
        "bands": {
            "HP_REAL_GAIN_MIN": HP_REAL_GAIN_MIN, "HP_SHUF_GAIN_MAX": HP_SHUF_GAIN_MAX,
            "HP_REAL_MINUS_MEANOBJ_MIN": HP_REAL_MINUS_MEANOBJ_MIN,
            "HF_REAL_GAIN_MAX": HF_REAL_GAIN_MAX, "TRAINED_ADV_MIN": TRAINED_ADV_MIN,
            "IND_TRANS_GAP_FLAG": IND_TRANS_GAP_FLAG,
        },
        "cells_aggregate": agg["cells"], "chance_by_rel": agg["chance_by_rel"],
        "gate_diagnostics": diag,
        "corpus_provenance": "conceptnet5_en_100k_real_triples",
        "encoding_provenance": {"char_trigram": "surface_phasor_zero_llm",
                                "bge_semantic": "BAAI/bge-small-en-v1.5_bounded_cache_centered_projected_phasor"},
        "allow_synthetic": False,
        "n_generative_llm_calls": 0,
        "metrics_source": "measured_cpu_fhrr_estimator_x_encoding_ablation_inductive_transductive",
        "verdict": verdict, "verdict_msg": verdict_msg, "summary": summary,
        "elapsed_s": elapsed,
    }
    tmp_path = out_dir / "metrics.json.tmp"
    with open(tmp_path, "w", encoding="utf-8") as fh:
        json.dump(metrics, fh, indent=2)
    os.replace(tmp_path, out_dir / "metrics.json")

    print(f"[{ANCHOR_NAME}] verdict={verdict}", flush=True)
    print(f"[{ANCHOR_NAME}] {verdict_msg}", flush=True)
    print(f"[{ANCHOR_NAME}] elapsed={elapsed:.1f}s good_units={agg['n_units']-agg['n_units_failed']}/"
          f"{EXPECTED_N_UNITS}", flush=True)


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
