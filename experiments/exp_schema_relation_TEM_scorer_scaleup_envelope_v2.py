"""schema_relation_TEM_scorer_scaleup_envelope_v2 -- ENVELOPE scale-up of the frontier
INDUCTIVE relational-transfer result (novel-entity, subject-conditional).

SCIENTIFIC QUESTION (the envelope test):
  The base cell (schema_relation_TEM_structural_content_binding_v1) moved inductive
  real_minus_shuf OFF ZERO (~0.05-0.13 on AtLocation/CausesDesire, both mechanisms, both encoders)
  where every prior AVERAGED/GLOBAL-transform family was exactly shuffle-invariant. That smoke was
  UNDER-PARAMETERIZED (V=100, M_OP=200, small df/steps, HARD-argmax TEM). THE QUESTION: does ANY
  (arm x scale) config push inductive real_minus_shuf from ~0.1 toward/past useful magnitude
  (>= 0.2075), and WHERE does the curve plateau? Map the curve; do NOT force a pass. A curve that
  climbs with M_OP but plateaus below 0.21 is itself the finding.
  Load-bearing metric: REAL - SHUFFLED on INDUCTIVE (novel-subject) eval. Raw accuracy is a
  relation-prior trap (population-typical answer); real_minus_shuf is the correspondence signal.

MECHANISM MAP (held from research a53f8b, verified off-disk):
  GLOBAL   = TransE / population-marginal single additive relation vector (M_R = mean bind(O,conj(A)));
             MUST degenerate to the popular object on one-to-many relations -> shuffle-invariant.
             The exhausted family; carried as reference baseline only (NOT HP-eligible).
  TEM_HARD = hard K-means type-prototype clustering + per-type transform + HARD nearest-proto argmax
             (the base cell's as-built arm; a discretized low-rank RESCAL approx / Prototypical-Net-
             like). Carried for contrast against the soft upgrade.
  TEM_SOFT = brain-aligned upgrade (NEW): posterior-weighted prototype MIXTURE. Softmax(beta*cos)
             over ALL K prototypes (temperature beta -> soft attention over structural codes;
             beta->inf recovers TEM_HARD). Weighted mixture of per-type transforms, argmax cleanup.
             The cheapest brain-aligned fix targeting the "under-realized hard discretization"
             critique WITHOUT a full recurrent-TEM rebuild (no precedent; high cost).
  SCORER   = trained bilinear content scorer s(f_subj,f_obj)=(P_s f_s)^T W (P_o f_o) = RESCAL/DistMult
             O(d^2) capacity (vs TransE O(d)); softmax-CE full-codebook negatives. PRIMARY.

SCALE AXES (primary = M_OP training pairs, per a53f8b):
  M_OP ladder (PRIMARY): {200,500,800,1500,3000} at V=300, df=384, steps=2000 (capped by in-codebook
       data per relation; M_eff recorded). Only 200 of ~9366(AtLoc)/~1423(CausesDesire) in-codebook
       triples were used before -> real headroom.
  df-scan (SECONDARY, scorer capacity): {96,192,384,768} at M_OP=800.
  steps-scan (SECONDARY, scorer training): {300,600,2000,6000} at M_OP=800.
  V-scan (SECONDARY, vocab/coverage): {100,300,1000} at M_OP=800.

RELATIONS (per a53f8b -- DROP CapableOf, structurally data-starved 18541 obj/22677 triples near
  one-to-one, top-100 covers 4.2%):
  AtLocation, CausesDesire -- semantic one-to-many, real headroom (HP-eligible).
  DerivedFrom -- surface-morphological NEGATIVE-baseline watchdog (shuffle-climbs-to-real = encoding
                 artifact). NOT HP-eligible; excluded from the envelope/HP tally.

CONTENT ENCODING AXIS (both semantic; entity encoder FIXED -> inductive):
  bge_semantic -- BAAI/bge-small-en-v1.5 bounded cache, centered + unit; phasor via fixed proj.
  gsbc         -- program TARGET encoder (GSBC_EXPAND2X sparse 8192-d code). Cache-gated.

ARMS (PAIRED -- SAME triples/split/seed/clustering; only the manipulation differs):
  REAL     -- true (subject,object) training pairs. PRIMARY (HP gates apply to mechanism arms).
  SHUFFLED -- object labels permuted within the M train sample (breaks subject->object corr). For
              TEM, clustering is on unchanged content; only the per-type transform uses shuffled
              pairs. MUST stay ~chance. If it CLIMBS to REAL -> codebook/encoding artifact.
  MEAN_OBJECT -- C-independent "return the popular object" control.
EVAL: inductive (novel-subject; PRIMARY) + transductive (seen-subject, held-out object; gap reported).

COMPUTE: class (c) MIXED. SCORER on torch (device auto -> cuda on the GPU box; batched bmm over the
  paired REAL+SHUFFLED arms) -- at real M_OP + df + steps the bilinear softmax-CE is a genuine
  GPU-trainable matmul job. TEM_HARD/TEM_SOFT/GLOBAL/cleanup on numpy-CPU (cheap; clustering is the
  brain-first CPU-cheap arm; bit-reference). Falls back to numpy scorer if torch/cuda absent (same
  analytic-gradient math; verified equal in self-test). Storage strategy: no_storage.

# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; ARMS-MUST-DIFFER hash-test)
# - final_metrics_atomicity = tmp_replace (META_RULE_AH)
# - except SystemExit: raise BEFORE except Exception (no BaseException); start-marker + crash-diag
# - crlb n/a (argmax transfer); chance floor 1/V stated; reachability declared
# - baseline_in_band at smoke (SYNTH_TYPE_HARD GLOBAL in (0.05,0.95); controls ~chance)
# - discriminator survives scale (SMOKE runs at FULL N=8192; only seeds/test/M/steps/grid shrink)
# - HARD_PASS strictly above floor (real_minus_shuf 0.2075 = 0.20 + 5% band-width, META_RULE_L)
# - HP_SCOPE: HP gates apply to TEM_SOFT/TEM_HARD/SCORER REAL/inductive only, per semantic rel x enc
# - cardinality_ok (META_RULE_H; EXPECTED_N_UNITS summed over the config grid)
# - per-unit failure-class instrumentation (META_RULE_J; no bare except)
# - calibration_check = adaptive_with_discriminator_gate (SYNTH_TYPE_HARD TEM(hard+soft)>GLOBAL +
#   SYNTH_CONTENT_MAP SCORER>GLOBAL are the discriminator-fires proofs; per-family gating)
# - progress_logging = print_flush_true (all progress lines flush=True; per (config,seed) timing)
# - positive controls reproduce/differentiate at test regime N=8192 (Gate D)
# - all numbers in design notes tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import os
for _v in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS"):
    os.environ.setdefault(_v, "8")
os.environ.setdefault("CUDA_MODULE_LOADING", "LAZY")   # CUDA env BEFORE torch import

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

# torch import (overnight_queue GPU gate greps for `import torch`). Guarded: numpy fallback if absent.
try:
    import torch
    _TORCH_OK = True
    _DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
except Exception:
    _TORCH_OK = False
    _DEVICE = "cpu"

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (
    get_output_dir, resumable_seeds, write_partial, aggregate_partials,
)

ANCHOR_NAME = "schema_relation_TEM_scorer_scaleup_envelope_v2"
DATASET_REL = Path("data/datasets/conceptnet5_en_100k.jsonl")
BGE_CACHE_REL = Path("data/datasets/bge_small_schema_TEM_entities_v1.npz")
GSBC_CACHE_REL = Path("data/datasets/gsbc_expand2x_schema_TEM_entities_v1.npz")

# ----------------------------------------------------------------------------
# Run mode. Runner invokes BARE + injects HDLAB_RUN_MODE=full. Terminal tier = full.
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
# Fixed substrate config
# ----------------------------------------------------------------------------
N_DIM = 8192
RELATIONS_SEM = ["AtLocation", "CausesDesire"]      # HP-eligible (real headroom)
RELATIONS_NEG = ["DerivedFrom"]                     # surface negative-baseline watchdog (NOT HP)
RELATIONS_ALL = RELATIONS_SEM + RELATIONS_NEG
CONTENT_ENCODINGS = ["bge_semantic", "gsbc"]
ARMS = ["REAL", "SHUFFLED"]
EVAL_MODES = ["inductive", "transductive"]
PRIMARY_ARM = "REAL"
PRIMARY_EVAL = "inductive"

# TEM sweep knobs (both hard + soft share the clustering per K)
K_LIST = [10, 20, 40]
BETA_LIST = [8.0, 20.0, 50.0]        # soft-TEM temperature; beta->inf recovers hard argmax
TEM_KMEANS_ITERS = 6

# Scorer fixed hyperparameters (bilinear projected content scorer; df/steps swept per-config)
SCORER_LR = 1.0
SCORER_TAU = 0.05
SCORER_L2 = 1e-3
PROJ_SEED = 12345

# Semantic-phasor deterministic projection
SEM_PROJ_SEED = 12345
SEM_PROJ_SCALE = 1.0

# ----------------------------------------------------------------------------
# Synthetic positive-control regimes (CALIBRATED; reused from v1, discriminator-fires proofs)
# ----------------------------------------------------------------------------
SYNTH_N = N_DIM
SYNTH_CLEAN_K = 8
SYNTH_CLEAN_SIGMA = 0.15
STH_KTRUE = 20
STH_V = 40
STH_M = 500
STH_TEST = 400
STH_ALPHA = 1.5
STH_OBJSIG = 0.9
STH_SIGMA = 0.4
SCM_D = 64
SCM_V = 40
SCM_M = 300
SCM_TEST = 200
TEM_K_SWEEP_SYNTH = [5, 10, 20]
SCORER_DF_SYNTH = 96
SCORER_STEPS_SYNTH = 300

# Pre-reg bands (LOCKED; identical thresholds to v1, now applied over the config envelope)
HP_REAL_GAIN_MIN = 0.2075
HP_RMS_MIN = 0.2075          # real_minus_shuf HARD_PASS floor (envelope max, trustworthy family)
HP_RMM_MIN = 0.05           # real_minus_meanobj (subject-conditional)
RMS_SIGNAL_MIN = 0.05       # nonzero-signal floor / HARD_FAIL ceiling on real_minus_shuf
BIND_ROUNDTRIP_MIN = 0.90
SYNTH_CLEAN_MIN = 0.90
TEM_ADV_MIN = 0.04          # SYNTH_TYPE_HARD: TEM (hard or soft) must beat GLOBAL by >= this
SCORER_ADV_MIN = 0.05       # SYNTH_CONTENT_MAP: SCORER must beat GLOBAL by >= this

# ----------------------------------------------------------------------------
# CONFIG GRID (each config: dict with V, M, df, steps, K list, betas, rels, encs, mech, name).
# mech="all" -> GLOBAL + TEM_HARD(K) + TEM_SOFT(K,beta) + SCORER; mech="scorer" -> SCORER only.
# ----------------------------------------------------------------------------
def _cfg(name, V, M, df, steps, rels, encs, mech, K=None, betas=None):
    return {"name": name, "V": V, "M": M, "df": df, "steps": steps,
            "rels": list(rels), "encs": list(encs), "mech": mech,
            "K": list(K if K is not None else K_LIST),
            "betas": list(betas if betas is not None else BETA_LIST)}

# Anchor scorer capacity for the M_OP ladder + V-scan (moderate; well past base df=96/steps=300)
_ANCHOR_DF = 384
_ANCHOR_STEPS = 2000
_ANCHOR_V = 300
_ANCHOR_M = 800

if RUN_MODE == "smoke":
    SEEDS = [7, 13]
    N_TEST_PER = 60
    POOL_CAP = 6000
    CONFIGS = [
        _cfg("S0_M200", 100, 200, 128, 300, RELATIONS_SEM, ["bge_semantic"], "all",
             K=[10, 20], betas=[8.0, 20.0]),
        _cfg("S1_M500", 100, 500, 128, 300, RELATIONS_SEM, ["bge_semantic"], "all",
             K=[10, 20], betas=[8.0, 20.0]),
        _cfg("S_dfscan", 100, 500, 192, 300, RELATIONS_SEM, ["bge_semantic"], "scorer"),
    ]
else:
    SEEDS = [7, 13, 19]
    N_TEST_PER = 150
    POOL_CAP = 30000
    _MOP_LADDER = [
        _cfg(f"MOP{m}", _ANCHOR_V, m, _ANCHOR_DF, _ANCHOR_STEPS, RELATIONS_ALL,
             CONTENT_ENCODINGS, "all")
        for m in [200, 500, 800, 1500, 3000]
    ]
    _DF_SCAN = [
        _cfg(f"DF{d}", _ANCHOR_V, _ANCHOR_M, d, _ANCHOR_STEPS, RELATIONS_SEM,
             CONTENT_ENCODINGS, "scorer")
        for d in [96, 192, 384, 768]
    ]
    _STEPS_SCAN = [
        _cfg(f"ST{s}", _ANCHOR_V, _ANCHOR_M, _ANCHOR_DF, s, RELATIONS_SEM,
             ["bge_semantic"], "scorer")
        for s in [300, 600, 2000, 6000]
    ]
    _V_SCAN = [
        _cfg(f"V{v}", v, _ANCHOR_M, _ANCHOR_DF, _ANCHOR_STEPS, RELATIONS_ALL,
             CONTENT_ENCODINGS, "all")
        for v in [100, 300, 1000]
    ]
    CONFIGS = _MOP_LADDER + _DF_SCAN + _STEPS_SCAN + _V_SCAN


def _slots_for(cfg) -> List[str]:
    if cfg["mech"] == "scorer":
        return ["SCORER"]
    slots = ["GLOBAL"]
    slots += [f"TEMH_K{k}" for k in cfg["K"]]
    slots += [f"TEMS_K{k}_B{int(b)}" for k in cfg["K"] for b in cfg["betas"]]
    slots += ["SCORER"]
    return slots


def _family_of(slot: str) -> str:
    if slot == "GLOBAL":
        return "GLOBAL"
    if slot.startswith("TEMH_"):
        return "TEM_HARD"
    if slot.startswith("TEMS_"):
        return "TEM_SOFT"
    if slot == "SCORER":
        return "SCORER"
    return "OTHER"


def expected_units(configs, seeds) -> int:
    tot = 0
    for c in configs:
        nslot = len(_slots_for(c))
        u = len(c["rels"]) * len(c["encs"]) * (nslot * len(ARMS) * len(EVAL_MODES))
        if c["mech"] == "all":
            u += len(c["rels"]) * len(c["encs"]) * len(EVAL_MODES)   # MEAN_OBJECT
        tot += u * len(seeds)
    return tot


EXPECTED_N_UNITS = expected_units(CONFIGS, SEEDS)


# ============================================================================
# FHRR primitives (complex64 phasors) -- verbatim reuse from v1
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


def unit_phasor(x: np.ndarray) -> np.ndarray:
    return np.exp(1j * np.angle(x)).astype(np.complex64)


def cos_c(x: np.ndarray, y: np.ndarray) -> float:
    num = float(np.vdot(y, x).real)
    den = float(np.linalg.norm(x) * np.linalg.norm(y)) + 1e-12
    return num / den


def cleanup_argmax_batch(Dhat: np.ndarray, O: np.ndarray) -> np.ndarray:
    """Argmax real cosine of each row of Dhat (B,N) against object codebook O (V,N)."""
    sims = (Dhat @ np.conj(O).T).real
    return sims.argmax(axis=1)


# ============================================================================
# Content encoders (ZERO generative-LLM; deterministic) -- verbatim reuse from v1
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
    return unit_phasor(acc)


def encode_random(s: str, n: int, seed: int) -> np.ndarray:
    return rand_phasor_from_seed(n, _stable_seed(s, salt=100 + seed))


class ContentUnavailable(Exception):
    pass


class _CachedSemanticEncoder:
    """Dense-embedding cache -> center -> unit feature; phasor via fixed projection.
    Missing cache -> ok=False (caller records CACHE_MISSING per-unit; no crash)."""

    def __init__(self, n: int, cache_rel: Path, emb_key: str, ent_key: str,
                 proj_seed: int, name: str):
        self.n = n
        self.name = name
        self.ok = False
        self.reason = ""
        self._missing = 0
        self._pcache: Dict[str, np.ndarray] = {}
        self._fcache: Dict[str, np.ndarray] = {}
        path = REPO / cache_rel
        if not path.exists():
            self.reason = f"{name.upper()}_CACHE_MISSING:{cache_rel}"
            return
        try:
            d = np.load(path, allow_pickle=True)
            ents = [str(e) for e in d[ent_key].tolist()]
            emb = d[emb_key].astype(np.float32)
        except Exception as e:
            self.reason = f"{name.upper()}_CACHE_LOAD_ERR:{type(e).__name__}"
            return
        emb = emb - emb.mean(axis=0, keepdims=True)
        nrm = np.linalg.norm(emb, axis=1, keepdims=True) + 1e-9
        emb = emb / nrm
        self.dim = emb.shape[1]
        self.idx = {e: i for i, e in enumerate(ents)}
        self.emb = emb
        rng = np.random.RandomState(proj_seed)
        self.W = (rng.standard_normal((self.dim, n)).astype(np.float32) * SEM_PROJ_SCALE)
        self.ok = True

    def feature(self, s: str) -> np.ndarray:
        v = self._fcache.get(s)
        if v is not None:
            return v
        i = self.idx.get(s)
        if i is None:
            v = np.zeros(self.dim, dtype=np.float32)
            self._missing += 1
        else:
            v = self.emb[i]
        self._fcache[s] = v
        return v

    def phasor(self, s: str) -> np.ndarray:
        v = self._pcache.get(s)
        if v is not None:
            return v
        i = self.idx.get(s)
        if i is None:
            v = rand_phasor_from_seed(self.n, _stable_seed(s, salt=777))
        else:
            v = np.exp(1j * (self.emb[i] @ self.W)).astype(np.complex64)
        self._pcache[s] = v
        return v


_BGE = _CachedSemanticEncoder(N_DIM, BGE_CACHE_REL, "emb", "entities", SEM_PROJ_SEED, "bge")
_GSBC = _CachedSemanticEncoder(N_DIM, GSBC_CACHE_REL, "code", "entities", SEM_PROJ_SEED + 1, "gsbc")


def _enc(encoding: str) -> _CachedSemanticEncoder:
    if encoding == "bge_semantic":
        return _BGE
    if encoding == "gsbc":
        return _GSBC
    raise ValueError(f"unknown encoding {encoding}")


def encode_phasor_matrix(ents: List[str], encoding: str) -> np.ndarray:
    e = _enc(encoding)
    if not e.ok:
        raise ContentUnavailable(e.reason)
    return np.stack([e.phasor(s) for s in ents]).astype(np.complex64)


def encode_feature_matrix(ents: List[str], encoding: str) -> np.ndarray:
    e = _enc(encoding)
    if not e.ok:
        raise ContentUnavailable(e.reason)
    F = np.stack([e.feature(s) for s in ents]).astype(np.float32)
    nrm = np.linalg.norm(F, axis=1, keepdims=True) + 1e-9
    return (F / nrm).astype(np.float32)


# ============================================================================
# MECHANISM 1: GLOBAL (naive-mean single per-relation transform) -- verbatim
# ============================================================================
def fit_naive_mean(A: np.ndarray, y: np.ndarray, O: np.ndarray) -> np.ndarray:
    return (O[y] * np.conj(A)).mean(axis=0).astype(np.complex64)


def apply_transform(C: np.ndarray, M_R: np.ndarray, O: np.ndarray) -> np.ndarray:
    return cleanup_argmax_batch(C * M_R[None, :], O)


def apply_transform_meanobj(A_train: np.ndarray, M_R: np.ndarray, O: np.ndarray, T: int) -> np.ndarray:
    a_mean = A_train.mean(axis=0)
    a_mean = a_mean / (np.abs(a_mean) + 1e-9)
    pred1 = int(cleanup_argmax_batch((a_mean * M_R)[None, :], O)[0])
    return np.full(T, pred1, dtype=np.int64)


# ============================================================================
# MECHANISM 2: TEM type-prototype structural code (hard + SOFT) -- hard verbatim; soft NEW
# ============================================================================
def kmeans_phasor(A: np.ndarray, K: int, seed: int, iters: int) -> Tuple[np.ndarray, np.ndarray]:
    """Bundle-centroid clustering of unit phasors by real-cosine (PP-254 mechanism)."""
    M, N = A.shape
    rng = np.random.RandomState(seed + 313)
    if K >= M:
        protos = A.copy()
    else:
        protos = A[rng.choice(M, K, replace=False)].copy()
    assign = np.zeros(M, dtype=np.int64)
    for _ in range(iters):
        sims = (A @ np.conj(protos).T).real
        assign = sims.argmax(axis=1)
        for k in range(protos.shape[0]):
            m = assign == k
            if m.sum() > 0:
                protos[k] = unit_phasor(A[m].sum(axis=0))
    return protos, assign


def fit_tem(A: np.ndarray, y: np.ndarray, O: np.ndarray, protos: np.ndarray,
            assign: np.ndarray) -> np.ndarray:
    """Per-type transforms given precomputed clustering (shared REAL vs SHUFFLED -> paired)."""
    Kk = protos.shape[0]
    Mglob = fit_naive_mean(A, y, O)
    Mk = np.zeros((Kk, A.shape[1]), dtype=np.complex64)
    for k in range(Kk):
        m = assign == k
        Mk[k] = fit_naive_mean(A[m], y[m], O) if m.sum() >= 1 else Mglob
    return Mk


def apply_tem_hard(C: np.ndarray, protos: np.ndarray, Mk: np.ndarray, O: np.ndarray) -> np.ndarray:
    """HARD nearest-prototype argmax (the base cell's arm)."""
    t = (C @ np.conj(protos).T).real.argmax(axis=1)
    return cleanup_argmax_batch(C * Mk[t], O)


def apply_tem_soft(C: np.ndarray, protos: np.ndarray, Mk: np.ndarray, O: np.ndarray,
                   beta: float) -> np.ndarray:
    """SOFT posterior-weighted prototype MIXTURE (brain-aligned upgrade). softmax(beta*cos) over
    ALL K prototypes -> weighted mixture of per-type transforms -> argmax cleanup. beta->inf
    recovers apply_tem_hard."""
    sims = (C @ np.conj(protos).T).real            # (T,K) real cosine
    sims = sims - sims.max(axis=1, keepdims=True)
    P = np.exp(beta * sims)
    P = (P / (P.sum(axis=1, keepdims=True) + 1e-12)).astype(np.complex64)   # (T,K)
    Mmix = P @ Mk                                  # (T,N) weighted transform mixture
    return cleanup_argmax_batch(C * Mmix, O)


# ============================================================================
# MECHANISM 3: ENTITY_FEATURE_SCORER (bilinear RESCAL/DistMult). numpy reference + torch backend.
# ============================================================================
def _softmax_rows(S: np.ndarray) -> np.ndarray:
    S = S - S.max(axis=1, keepdims=True)
    e = np.exp(S)
    return e / (e.sum(axis=1, keepdims=True) + 1e-12)


def _proj_pair(d: int, df: int, seed: int) -> Tuple[np.ndarray, np.ndarray]:
    rng = np.random.RandomState(seed)
    sd = float(np.sqrt(d))
    Ps = (rng.standard_normal((d, df)) / sd).astype(np.float32)
    Po = (rng.standard_normal((d, df)) / sd).astype(np.float32)
    return Ps, Po


def fit_scorer_np(Fa, y, Fo, Ps, Po, steps, lr, tau, l2) -> np.ndarray:
    """numpy analytic-gradient bilinear scorer (reference + fallback)."""
    U = Fa @ Ps
    Vo = Fo @ Po
    df = U.shape[1]
    M = U.shape[0]
    W = np.zeros((df, df), dtype=np.float32)
    yv = y.astype(np.int64)
    for _ in range(steps):
        S = (U @ W) @ Vo.T
        P = _softmax_rows(S / tau)
        P[np.arange(M), yv] -= 1.0
        P /= M
        gW = U.T @ (P @ Vo) / tau + l2 * W
        W -= lr * gW
    return W


def apply_scorer(Fc, W, Fo, Ps, Po) -> np.ndarray:
    U = Fc @ Ps
    Vo = Fo @ Po
    return ((U @ W) @ Vo.T).argmax(axis=1)


def fit_scorer_paired(Fa, y_real, y_shuf, Fo, Ps, Po, steps, lr, tau, l2):
    """Fit REAL and SHUFFLED bilinear W in one batched pass. torch(device) bmm B=2 if available
    (the GPU-batching win; REAL/SHUFFLED share U,Vo,Ps,Po -> only y differs), else numpy twice.
    Returns (W_real, W_shuf) as numpy (df,df)."""
    if _TORCH_OK:
        dev = _DEVICE
        def _t(x):
            return torch.as_tensor(np.ascontiguousarray(x, dtype=np.float32), device=dev)
        U = _t(Fa) @ _t(Ps)     # (M,df)
        Vo = _t(Fo) @ _t(Po)    # (V,df)
        M, df = int(U.shape[0]), int(U.shape[1])
        Ub = U.unsqueeze(0).expand(2, -1, -1)                                      # (2,M,df)
        VoB = Vo.unsqueeze(0).expand(2, -1, -1)                                    # (2,V,df)
        VoT = Vo.t().unsqueeze(0).expand(2, -1, -1).contiguous()                   # (2,df,V)
        W = torch.zeros((2, df, df), dtype=torch.float32, device=dev)
        ys = torch.stack([torch.as_tensor(y_real, device=dev, dtype=torch.long),
                          torch.as_tensor(y_shuf, device=dev, dtype=torch.long)])  # (2,M)
        ar = torch.arange(M, device=dev)
        for _ in range(steps):
            S = torch.bmm(torch.bmm(Ub, W), VoT) / tau                            # (2,M,V)
            S = S - S.max(dim=2, keepdim=True).values
            P = torch.softmax(S, dim=2)
            P[0, ar, ys[0]] -= 1.0
            P[1, ar, ys[1]] -= 1.0
            P = P / M
            gW = torch.bmm(Ub.transpose(1, 2), torch.bmm(P, VoB)) / tau + l2 * W   # (2,df,df)
            W = W - lr * gW
        Wr = W[0].detach().to("cpu").numpy().astype(np.float32)
        Ws = W[1].detach().to("cpu").numpy().astype(np.float32)
        return Wr, Ws
    Wr = fit_scorer_np(Fa, y_real, Fo, Ps, Po, steps, lr, tau, l2)
    Ws = fit_scorer_np(Fa, y_shuf, Fo, Ps, Po, steps, lr, tau, l2)
    return Wr, Ws


# ============================================================================
# Data loading + scaled split (inductive novel-subject + transductive seen-subject)
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


def build_split_scaled(relation: str, seed: int, V: int, n_test_per: int, pool_cap: int,
                       M_op: int) -> Dict:
    """Inductive (novel-subject) + transductive split with configurable V and M_op (train-pair cap).
    Test subjects are DISJOINT from train subjects (the load-bearing inductive property)."""
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

    ind_test: List[Tuple[str, str]] = []
    for s in test_subs:
        o = by_subj[s][rng.randint(len(by_subj[s]))]
        ind_test.append((s, o))
        if len(ind_test) >= n_test_per:
            break

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

    if len(train_pairs) < 40 or len(ind_test) < 20 or len(trans_test) < 20:
        raise ValueError(
            f"relation {relation} V={V} M_op={M_op}: insufficient data (train={len(train_pairs)}, "
            f"ind_test={len(ind_test)}, trans_test={len(trans_test)}; need train>=40, tests>=20)")

    rng.shuffle(train_pairs)
    m_eff = min(M_op, len(train_pairs))
    train_pairs = train_pairs[:m_eff]
    return {
        "relation": relation, "V_eff": V_eff, "codebook": codebook, "obj_idx": obj_idx,
        "train_pairs": train_pairs, "ind_test": ind_test, "trans_test": trans_test,
        "chance": 1.0 / V_eff, "m_eff": m_eff, "m_available": None,
    }


# ============================================================================
# Core evaluation: one (config, relation, encoding, seed) -> per-slot acc
# ============================================================================
def eval_config_relenc(cfg: Dict, relation: str, encoding: str, seed: int) -> Dict:
    V = cfg["V"]; M_op = cfg["M"]; df = cfg["df"]; steps = cfg["steps"]
    sp = build_split_scaled(relation, seed, V, N_TEST_PER, POOL_CAP, M_op)
    codebook = sp["codebook"]; obj_idx = sp["obj_idx"]
    train_pairs = sp["train_pairs"]; ind_test = sp["ind_test"]; trans_test = sp["trans_test"]
    V_eff = sp["V_eff"]; m_eff = sp["m_eff"]

    train_subs = [s for s, _ in train_pairs]
    y_train = np.array([obj_idx[o] for _, o in train_pairs], dtype=np.int64)
    rng = np.random.RandomState(seed + 991)
    perm = rng.permutation(len(train_pairs))
    y_shuf = y_train[perm]
    y_ind = np.array([obj_idx[o] for _, o in ind_test], dtype=np.int64)
    y_trans = np.array([obj_idx[o] for _, o in trans_test], dtype=np.int64)
    ind_subs = [s for s, _ in ind_test]
    trans_subs = [s for s, _ in trans_test]

    O = encode_phasor_matrix(codebook, encoding)
    A = encode_phasor_matrix(train_subs, encoding)
    C_ind = encode_phasor_matrix(ind_subs, encoding)
    C_tr = encode_phasor_matrix(trans_subs, encoding)
    C_by = {"inductive": C_ind, "transductive": C_tr}
    y_by = {"inductive": y_ind, "transductive": y_trans}

    slots = _slots_for(cfg)
    acc: Dict[str, Dict[str, Dict[str, float]]] = {
        s: {arm: {ev: None for ev in EVAL_MODES} for arm in ARMS} for s in slots}
    meanobj: Dict[str, float] = {}

    do_all = cfg["mech"] == "all"

    if do_all:
        # --- GLOBAL ---
        Mg_real = fit_naive_mean(A, y_train, O)
        Mg_shuf = fit_naive_mean(A, y_shuf, O)
        for ev in EVAL_MODES:
            acc["GLOBAL"]["REAL"][ev] = float((apply_transform(C_by[ev], Mg_real, O) == y_by[ev]).mean())
            acc["GLOBAL"]["SHUFFLED"][ev] = float((apply_transform(C_by[ev], Mg_shuf, O) == y_by[ev]).mean())
        for ev in EVAL_MODES:
            pm = apply_transform_meanobj(A, Mg_real, O, len(y_by[ev]))
            meanobj[ev] = float((pm == y_by[ev]).mean())

        # --- TEM (hard + soft share clustering per K; paired REAL vs SHUFFLED) ---
        for K in cfg["K"]:
            protos, assign = kmeans_phasor(A, K, seed, TEM_KMEANS_ITERS)
            Mk_real = fit_tem(A, y_train, O, protos, assign)
            Mk_shuf = fit_tem(A, y_shuf, O, protos, assign)
            hs = f"TEMH_K{K}"
            for ev in EVAL_MODES:
                acc[hs]["REAL"][ev] = float((apply_tem_hard(C_by[ev], protos, Mk_real, O) == y_by[ev]).mean())
                acc[hs]["SHUFFLED"][ev] = float((apply_tem_hard(C_by[ev], protos, Mk_shuf, O) == y_by[ev]).mean())
            for b in cfg["betas"]:
                ss = f"TEMS_K{K}_B{int(b)}"
                for ev in EVAL_MODES:
                    acc[ss]["REAL"][ev] = float((apply_tem_soft(C_by[ev], protos, Mk_real, O, b) == y_by[ev]).mean())
                    acc[ss]["SHUFFLED"][ev] = float((apply_tem_soft(C_by[ev], protos, Mk_shuf, O, b) == y_by[ev]).mean())

    # --- SCORER (always; torch/bmm-paired) ---
    Fo = encode_feature_matrix(codebook, encoding)
    Fa = encode_feature_matrix(train_subs, encoding)
    Fc_ind = encode_feature_matrix(ind_subs, encoding)
    Fc_tr = encode_feature_matrix(trans_subs, encoding)
    Fc_by = {"inductive": Fc_ind, "transductive": Fc_tr}
    Ps, Po = _proj_pair(Fa.shape[1], df, PROJ_SEED)
    W_real, W_shuf = fit_scorer_paired(Fa, y_train, y_shuf, Fo, Ps, Po, steps,
                                       SCORER_LR, SCORER_TAU, SCORER_L2)
    for ev in EVAL_MODES:
        acc["SCORER"]["REAL"][ev] = float((apply_scorer(Fc_by[ev], W_real, Fo, Ps, Po) == y_by[ev]).mean())
        acc["SCORER"]["SHUFFLED"][ev] = float((apply_scorer(Fc_by[ev], W_shuf, Fo, Ps, Po) == y_by[ev]).mean())

    return {"acc": acc, "meanobj": meanobj, "V_eff": V_eff, "m_eff": m_eff,
            "chance": 1.0 / V_eff, "n_ind": len(y_ind), "n_trans": len(y_trans),
            "do_all": do_all}


# ============================================================================
# Synthetic positive controls (Gate D) -- reused; TYPE_HARD extended to score SOFT-TEM
# ============================================================================
def synth_rot_clean(seed: int) -> Dict[str, float]:
    rng = np.random.RandomState(seed)
    N, K, sigma, M = SYNTH_N, SYNTH_CLEAN_K, SYNTH_CLEAN_SIGMA, STH_M
    theta_true = rng.uniform(-np.pi, np.pi, N).astype(np.float32)
    O = np.exp(1j * rng.uniform(-np.pi, np.pi, (K, N))).astype(np.complex64)
    ks = rng.randint(0, K, M)
    A = np.exp(1j * (np.angle(O[ks]) - theta_true[None, :]
                     + sigma * rng.standard_normal((M, N)))).astype(np.complex64)
    kt = rng.randint(0, K, 80)
    C = np.exp(1j * (np.angle(O[kt]) - theta_true[None, :]
                     + sigma * rng.standard_normal((80, N)))).astype(np.complex64)
    Mr = fit_naive_mean(A, ks.astype(np.int64), O)
    return {"GLOBAL": float((apply_transform(C, Mr, O) == kt).mean()), "chance": 1.0 / K}


def synth_type_hard(seed: int) -> Dict[str, float]:
    """K_true type-conditional structure. GLOBAL below ceiling; TEM (hard AND soft) must beat it.
    Discriminator-fires proof for the brain-first arms."""
    rng = np.random.RandomState(seed + 777)
    N, Ktrue, V, M, T = SYNTH_N, STH_KTRUE, STH_V, STH_M, STH_TEST
    O = np.exp(1j * rng.uniform(-np.pi, np.pi, (V, N))).astype(np.complex64)
    theta = rng.uniform(-np.pi, np.pi, (Ktrue, N)).astype(np.float32)
    TypeSig = np.exp(1j * rng.uniform(-np.pi, np.pi, (Ktrue, N))).astype(np.complex64)

    def gen(n, rs):
        k = rs.randint(0, Ktrue, n); yv = rs.randint(0, V, n)
        objrot = np.exp(1j * (np.angle(O[yv]) - theta[k])).astype(np.complex64)
        mix = STH_ALPHA * TypeSig[k] + STH_OBJSIG * objrot
        A = np.exp(1j * (np.angle(mix) + STH_SIGMA * rs.standard_normal((n, N)))).astype(np.complex64)
        ytrue = cleanup_argmax_batch(A * np.exp(1j * theta[k]), O)
        return A, ytrue

    A, yA = gen(M, rng)
    C, yC = gen(T, np.random.RandomState(seed + 999))
    Mg = fit_naive_mean(A, yA, O)
    out = {"GLOBAL": float((apply_transform(C, Mg, O) == yC).mean())}
    ysh = yA[rng.permutation(M)]
    Msh = fit_naive_mean(A, ysh, O)
    out["GLOBAL_shuf"] = float((apply_transform(C, Msh, O) == yC).mean())
    best_hard = -1.0
    best_soft = -1.0
    for K in TEM_K_SWEEP_SYNTH:
        protos, assign = kmeans_phasor(A, K, seed, TEM_KMEANS_ITERS)
        Mk = fit_tem(A, yA, O, protos, assign)
        ah = float((apply_tem_hard(C, protos, Mk, O) == yC).mean())
        best_hard = max(best_hard, ah)
        for b in BETA_LIST:
            asf = float((apply_tem_soft(C, protos, Mk, O, b) == yC).mean())
            best_soft = max(best_soft, asf)
    out["TEM_HARD_best"] = best_hard
    out["TEM_SOFT_best"] = best_soft
    out["tem_hard_adv"] = best_hard - out["GLOBAL"]
    out["tem_soft_adv"] = best_soft - out["GLOBAL"]
    out["chance"] = 1.0 / V
    return out


def synth_content_map(seed: int) -> Dict[str, float]:
    """object = linear-map(subject content) + codebook nearest. SCORER must beat GLOBAL.
    Discriminator-fires proof for the scorer arm."""
    rng = np.random.RandomState(seed + 555)
    N, d, V, M, T = SYNTH_N, SCM_D, SCM_V, SCM_M, SCM_TEST
    Fo = rng.standard_normal((V, d)).astype(np.float32)
    Fo /= np.linalg.norm(Fo, axis=1, keepdims=True) + 1e-9
    Tmap = rng.standard_normal((d, d)).astype(np.float32) / np.sqrt(d)
    Wp = rng.standard_normal((d, N)).astype(np.float32)

    def gen(n, rs):
        F = rs.standard_normal((n, d)).astype(np.float32)
        F /= np.linalg.norm(F, axis=1, keepdims=True) + 1e-9
        y = ((F @ Tmap.T) @ Fo.T).argmax(axis=1)
        return F, y

    Fs, yA = gen(M, rng)
    Fc, yC = gen(T, np.random.RandomState(seed + 888))
    O = np.exp(1j * (Fo @ Wp)).astype(np.complex64)
    A = np.exp(1j * (Fs @ Wp)).astype(np.complex64)
    C = np.exp(1j * (Fc @ Wp)).astype(np.complex64)
    Mg = fit_naive_mean(A, yA, O)
    out = {"GLOBAL": float((apply_transform(C, Mg, O) == yC).mean())}
    Ps, Po = _proj_pair(d, SCORER_DF_SYNTH, PROJ_SEED)
    W = fit_scorer_np(Fs, yA, Fo, Ps, Po, max(SCORER_STEPS_SYNTH, 200), SCORER_LR, SCORER_TAU, SCORER_L2)
    out["SCORER"] = float((apply_scorer(Fc, W, Fo, Ps, Po) == yC).mean())
    ysh = yA[rng.permutation(M)]
    Wsh = fit_scorer_np(Fs, ysh, Fo, Ps, Po, max(SCORER_STEPS_SYNTH, 200), SCORER_LR, SCORER_TAU, SCORER_L2)
    out["SCORER_shuf"] = float((apply_scorer(Fc, Wsh, Fo, Ps, Po) == yC).mean())
    out["scorer_adv"] = out["SCORER"] - out["GLOBAL"]
    out["chance"] = 1.0 / V
    return out


# ============================================================================
# Per-seed driver (failure-instrumented; no silent continue)
# ============================================================================
def _flatten_unit(per_unit, cfgname, relation, enc, slot, arm, ev, val, fc):
    per_unit[f"{cfgname}|{relation}|{enc}|{slot}|{arm}|{ev}"] = {
        "config": cfgname, "relation": relation, "encoding": enc, "mech": slot,
        "family": _family_of(slot), "arm": arm, "eval": ev,
        "acc": (float(val) if val is not None else None), "failure_class": fc}


def run_seed(seed: int) -> Dict:
    t0 = time.time()
    per_unit: Dict[str, Dict] = {}
    meta: Dict[str, Dict] = {}
    fatal = False
    fatal_msg = None
    for cfg in CONFIGS:
        cfgname = cfg["name"]
        slots = _slots_for(cfg)
        for relation in cfg["rels"]:
            for enc in cfg["encs"]:
                fc = None
                res = None
                try:
                    res = eval_config_relenc(cfg, relation, enc, seed)
                except ContentUnavailable as e:
                    fc = str(e)
                except Exception as e:
                    fatal = True
                    fatal_msg = f"{cfgname}|{relation}|{enc}:{type(e).__name__}:{str(e)[:200]}"
                    print(f"  [seed={seed} {cfgname} {relation} {enc}] FAILED "
                          f"{type(e).__name__}: {e}", flush=True)
                    traceback.print_exc()
                    break
                for slot in slots:
                    for arm in ARMS:
                        for ev in EVAL_MODES:
                            val = res["acc"][slot][arm][ev] if res is not None else None
                            _flatten_unit(per_unit, cfgname, relation, enc, slot, arm, ev, val, fc)
                if cfg["mech"] == "all":
                    for ev in EVAL_MODES:
                        val = res["meanobj"][ev] if res is not None else None
                        _flatten_unit(per_unit, cfgname, relation, enc, "MEAN_OBJECT", "MEAN_OBJECT",
                                      ev, val, fc)
                if res is not None:
                    meta[f"{cfgname}|{relation}|{enc}"] = {
                        "V_eff": res["V_eff"], "m_eff": res["m_eff"], "chance": res["chance"],
                        "n_ind": res["n_ind"], "n_trans": res["n_trans"]}
            if fatal:
                break
        if fatal:
            break
        # per-config progress line (bge AtLocation SCORER + best TEM_SOFT inductive real_minus_shuf)
        _print_cfg_progress(cfg, per_unit, seed)

    src = synth_rot_clean(seed)
    sth = synth_type_hard(seed)
    scm = synth_content_map(seed)
    print(f"  [seed={seed} SYNTH] rot_clean G={src['GLOBAL']:.3f} || TYPE_HARD G={sth['GLOBAL']:.3f} "
          f"HARD={sth['TEM_HARD_best']:.3f}(adv{sth['tem_hard_adv']:+.3f}) "
          f"SOFT={sth['TEM_SOFT_best']:.3f}(adv{sth['tem_soft_adv']:+.3f}) || "
          f"CONTENT_MAP G={scm['GLOBAL']:.3f} SC={scm['SCORER']:.3f}(adv{scm['scorer_adv']:+.3f})",
          flush=True)

    return {
        "seed": seed, "N": N_DIM, "run_mode": RUN_MODE, "device": _DEVICE, "torch_ok": _TORCH_OK,
        "config_version": f"ANCHOR={ANCHOR_NAME},N={N_DIM},configs={len(CONFIGS)},seeds={SEEDS}",
        "per_unit": per_unit, "meta": meta,
        "synth_rot_clean": src, "synth_type_hard": sth, "synth_content_map": scm,
        "fatal": fatal, "fatal_msg": fatal_msg, "elapsed_s": time.time() - t0,
    }


def _rms(per_unit, cfgname, rel, enc, slot):
    r = per_unit.get(f"{cfgname}|{rel}|{enc}|{slot}|REAL|inductive")
    s = per_unit.get(f"{cfgname}|{rel}|{enc}|{slot}|SHUFFLED|inductive")
    if r is None or s is None or r.get("acc") is None or s.get("acc") is None:
        return float("nan")
    return r["acc"] - s["acc"]


def _print_cfg_progress(cfg, per_unit, seed):
    cfgname = cfg["name"]
    rel = cfg["rels"][0]; enc = cfg["encs"][0]
    sc = _rms(per_unit, cfgname, rel, enc, "SCORER")
    parts = [f"SCORER rms={sc:+.3f}"]
    if cfg["mech"] == "all":
        temh = max([_rms(per_unit, cfgname, rel, enc, f"TEMH_K{k}") for k in cfg["K"]]
                   + [float("-inf")])
        tems = max([_rms(per_unit, cfgname, rel, enc, f"TEMS_K{k}_B{int(b)}")
                    for k in cfg["K"] for b in cfg["betas"]] + [float("-inf")])
        parts += [f"TEMhard={temh:+.3f}", f"TEMsoft={tems:+.3f}"]
    print(f"  [seed={seed} {cfgname:<10} {rel[:11]:<11} {enc[:4]}] real_minus_shuf(ind): "
          + " ".join(parts), flush=True)


# ============================================================================
# Aggregate + envelope verdict (map the curve; do not force a pass)
# ============================================================================
def _mean_std(vals: List[float]) -> Tuple[float, float, int]:
    v = [x for x in vals if x == x]
    n = len(v)
    if n == 0:
        return float("nan"), 0.0, 0
    m = float(np.mean(v))
    s = float(np.std(v, ddof=1)) if n > 1 else 0.0
    return m, s, n


def aggregate(per_seed: Dict) -> Dict:
    buckets: Dict[str, List[float]] = collections.defaultdict(list)
    n_units = 0
    n_failed = 0
    enc_unavailable = collections.Counter()
    sth_g, sth_hb, sth_sb, sth_ha, sth_sa = [], [], [], [], []
    scm_g, scm_s, scm_a = [], [], []
    src_g = []
    meta_all: Dict[str, Dict] = {}
    for sd in per_seed.values():
        for key, rec in sd.get("per_unit", {}).items():
            n_units += 1
            if rec.get("acc") is None:
                n_failed += 1
                fc = rec.get("failure_class", "NA")
                if isinstance(fc, str) and "CACHE_MISSING" in fc:
                    enc_unavailable[rec.get("encoding", "?")] += 1
                continue
            buckets[key].append(float(rec["acc"]))
        for mk, mv in sd.get("meta", {}).items():
            meta_all[mk] = mv
        src = sd.get("synth_rot_clean", {}); sth = sd.get("synth_type_hard", {})
        scm = sd.get("synth_content_map", {})
        if src:
            src_g.append(src.get("GLOBAL", float("nan")))
        if sth:
            sth_g.append(sth["GLOBAL"]); sth_hb.append(sth["TEM_HARD_best"]); sth_sb.append(sth["TEM_SOFT_best"])
            sth_ha.append(sth["tem_hard_adv"]); sth_sa.append(sth["tem_soft_adv"])
        if scm:
            scm_g.append(scm["GLOBAL"]); scm_s.append(scm["SCORER"]); scm_a.append(scm["scorer_adv"])
    cells = {key: {"mean": _mean_std(v)[0], "std": _mean_std(v)[1], "n": _mean_std(v)[2]}
             for key, v in buckets.items()}
    return {
        "cells": cells, "n_units": n_units, "n_units_failed": n_failed,
        "enc_unavailable": dict(enc_unavailable), "meta": meta_all,
        "synth_rot_clean": {"GLOBAL": _mean_std(src_g)[0]},
        "synth_type_hard": {"GLOBAL": _mean_std(sth_g)[0], "TEM_HARD_best": _mean_std(sth_hb)[0],
                            "TEM_SOFT_best": _mean_std(sth_sb)[0], "tem_hard_adv": _mean_std(sth_ha)[0],
                            "tem_soft_adv": _mean_std(sth_sa)[0]},
        "synth_content_map": {"GLOBAL": _mean_std(scm_g)[0], "SCORER": _mean_std(scm_s)[0],
                              "scorer_adv": _mean_std(scm_a)[0]},
    }


def _cell(cells, key):
    c = cells.get(key)
    return c["mean"] if c else float("nan")


def _best_family_rms(cells, cfg, rel, enc, family):
    """Best-of real_minus_shuf(inductive) over the family's slots at (cfg,rel,enc). Returns
    (rms, slot, real_ind, gain, rmm)."""
    if family == "SCORER":
        slots = ["SCORER"]
    elif family == "TEM_HARD":
        slots = [f"TEMH_K{k}" for k in cfg["K"]]
    elif family == "TEM_SOFT":
        slots = [f"TEMS_K{k}_B{int(b)}" for k in cfg["K"] for b in cfg["betas"]]
    else:
        slots = ["GLOBAL"]
    cn = cfg["name"]
    ch = 1.0 / 1.0
    meta = None
    best = None
    for slot in slots:
        ri = _cell(cells, f"{cn}|{rel}|{enc}|{slot}|REAL|inductive")
        si = _cell(cells, f"{cn}|{rel}|{enc}|{slot}|SHUFFLED|inductive")
        if ri != ri or si != si:
            continue
        rms = ri - si
        if best is None or rms > best[0]:
            best = (rms, slot, ri)
    if best is None:
        return None
    rms, slot, ri = best
    mo = _cell(cells, f"{cn}|{rel}|{enc}|MEAN_OBJECT|MEAN_OBJECT|inductive")
    return {"rms": rms, "slot": slot, "real_ind": ri, "meanobj_ind": mo}


def compute_envelope_verdict(agg: Dict, arms_differ_ok: bool, bind_rt: float) -> Tuple[str, str, Dict]:
    cells = agg["cells"]
    meta = agg["meta"]
    src = agg["synth_rot_clean"]; sth = agg["synth_type_hard"]; scm = agg["synth_content_map"]
    good_units = agg["n_units"] - agg["n_units_failed"]

    fires_hard = sth["tem_hard_adv"] >= TEM_ADV_MIN
    fires_soft = sth["tem_soft_adv"] >= TEM_ADV_MIN
    fires_scorer = scm["scorer_adv"] >= SCORER_ADV_MIN
    trustworthy = set()
    if fires_hard:
        trustworthy.add("TEM_HARD")
    if fires_soft:
        trustworthy.add("TEM_SOFT")
    if fires_scorer:
        trustworthy.add("SCORER")

    HP_FAMILIES = ["TEM_HARD", "TEM_SOFT", "SCORER"]
    # per (config, rel, enc, family) best-of; collect for envelope + axis curves
    records = []            # each: dict(config, rel, enc, family, rms, slot, real_ind, gain, rmm, chance)
    for cfg in CONFIGS:
        cn = cfg["name"]
        for rel in cfg["rels"]:
            is_sem = rel in RELATIONS_SEM
            for enc in cfg["encs"]:
                ch = float(meta.get(f"{cn}|{rel}|{enc}", {}).get("chance", float("nan")))
                for fam in HP_FAMILIES:
                    if fam in ("TEM_HARD", "TEM_SOFT") and cfg["mech"] != "all":
                        continue
                    bf = _best_family_rms(cells, cfg, rel, enc, fam)
                    if bf is None:
                        continue
                    gain = bf["real_ind"] - ch if ch == ch else float("nan")
                    rmm = bf["real_ind"] - bf["meanobj_ind"] if bf["meanobj_ind"] == bf["meanobj_ind"] else float("nan")
                    records.append({
                        "config": cn, "rel": rel, "enc": enc, "family": fam, "is_sem": is_sem,
                        "rms": bf["rms"], "slot": bf["slot"], "real_ind": bf["real_ind"],
                        "gain": gain, "rmm": rmm, "chance": ch,
                        "M": cfg["M"], "V": cfg["V"], "df": cfg["df"], "steps": cfg["steps"],
                        "trustworthy": fam in trustworthy})

    # ENVELOPE: max real_minus_shuf over trustworthy families, semantic relations only
    env_cands = [r for r in records if r["is_sem"] and r["trustworthy"]]
    env_best = max(env_cands, key=lambda r: r["rms"], default=None)

    # HARD_PASS candidates: trustworthy semantic family clearing all three sub-gates
    hp_wins = [r for r in env_cands
               if r["rms"] >= HP_RMS_MIN and r["gain"] >= HP_REAL_GAIN_MIN and r["rmm"] >= HP_RMM_MIN]

    # axis curves (mean over semantic rel x enc of the best trustworthy family rms, per config)
    def _axis_curve(cfg_names):
        out = {}
        for cn in cfg_names:
            vals = [r["rms"] for r in records if r["config"] == cn and r["is_sem"] and r["trustworthy"]]
            best_by_fam = {}
            for fam in HP_FAMILIES:
                fv = [r["rms"] for r in records if r["config"] == cn and r["is_sem"] and r["family"] == fam]
                if fv:
                    best_by_fam[fam] = round(float(np.max(fv)), 4)
            out[cn] = {"best_rms": (round(float(np.max(vals)), 4) if vals else None),
                       "per_family_best": best_by_fam}
        return out

    mop_names = [c["name"] for c in CONFIGS if c["name"].startswith("MOP") or c["name"].startswith("S")]
    df_names = [c["name"] for c in CONFIGS if c["name"].startswith("DF") or "dfscan" in c["name"]]
    steps_names = [c["name"] for c in CONFIGS if c["name"].startswith("ST")]
    v_names = [c["name"] for c in CONFIGS if c["name"].startswith("V")]
    curves = {
        "M_OP": {c["name"]: c["M"] for c in CONFIGS}, "V": {c["name"]: c["V"] for c in CONFIGS},
        "df": {c["name"]: c["df"] for c in CONFIGS}, "steps": {c["name"]: c["steps"] for c in CONFIGS},
        "mop_ladder_curve": _axis_curve(mop_names),
        "df_scan_curve": _axis_curve(df_names),
        "steps_scan_curve": _axis_curve(steps_names),
        "v_scan_curve": _axis_curve(v_names),
    }

    diag = {
        "bind_roundtrip": bind_rt, "arms_differ_ok": arms_differ_ok,
        "good_units": good_units, "expected_n_units": EXPECTED_N_UNITS,
        "synth_rot_clean": src, "synth_type_hard": sth, "synth_content_map": scm,
        "discriminator_fires_tem_hard": fires_hard, "discriminator_fires_tem_soft": fires_soft,
        "discriminator_fires_scorer": fires_scorer, "trustworthy_families": sorted(trustworthy),
        "envelope_best": env_best, "hp_wins": hp_wins, "n_records": len(records),
        "records": records, "axis_curves": curves,
        "enc_unavailable": agg["enc_unavailable"], "device": _DEVICE,
    }

    # ---- global gates ----
    if good_units < EXPECTED_N_UNITS:
        gsbc_missing = agg["enc_unavailable"].get("gsbc", 0)
        if not (gsbc_missing > 0 and (good_units + gsbc_missing) >= EXPECTED_N_UNITS):
            return ("HARD_FAIL",
                    f"HARD_FAIL_CARDINALITY_BREACH_META_RULE_H: good_units={good_units} < "
                    f"expected={EXPECTED_N_UNITS} (not explained by gsbc-cache-missing).", diag)
        diag["gsbc_cache_missing_note"] = "gsbc content arm skipped (bge + mechanism axis valid)"
    if not arms_differ_ok:
        return ("HARD_FAIL", "META_RULE_AF_VIOLATION: arm outputs bit-identical; arm-impl bug.", diag)
    if not (bind_rt >= BIND_ROUNDTRIP_MIN):
        return ("HARD_FAIL", f"SANITY_RAIL_BIND: bind-roundtrip={bind_rt:.3f} < {BIND_ROUNDTRIP_MIN}.", diag)
    if not (src["GLOBAL"] >= SYNTH_CLEAN_MIN):
        return ("MIDDLE_BAND",
                f"HARNESS_SUSPECT: SYNTH_ROT_CLEAN GLOBAL={src['GLOBAL']:.3f} < {SYNTH_CLEAN_MIN}; "
                f"algebra did not recover a clean rotation -> real arms uninterpretable.", diag)

    eb = env_best
    eb_str = ("none" if eb is None else
              f"{eb['family']}@{eb['config']}|{eb['rel']}|{eb['enc']}|{eb['slot']} "
              f"rms={eb['rms']:+.3f} gain={eb['gain']:+.3f} rmm={eb['rmm']:+.3f}")
    summ = (f"dev={_DEVICE} fires[hard={fires_hard},soft={fires_soft},scorer={fires_scorer}] "
            f"synthTYPE(G={sth['GLOBAL']:.2f},H={sth['TEM_HARD_best']:.2f},S={sth['TEM_SOFT_best']:.2f}) "
            f"synthCONTENT(G={scm['GLOBAL']:.2f},SC={scm['SCORER']:.2f}) | ENVELOPE_BEST={eb_str}")

    if not trustworthy:
        return ("MIDDLE_BAND",
                f"MIDDLE_BAND_VACUOUS_CONTROL: NO discriminator fired (hard={fires_hard}, "
                f"soft={fires_soft}, scorer={fires_scorer}); real arms uninterpretable. {summ}", diag)

    if hp_wins:
        fams = sorted(set(r["family"] for r in hp_wins))
        head = "TEM" if any(f.startswith("TEM") for f in fams) else "SCORER"
        return ("HARD_PASS",
                f"HARD_PASS_ENVELOPE_INDUCTIVE_TRANSFER: scaling reaches useful magnitude "
                f"(real_minus_shuf(ind) >= {HP_RMS_MIN}) on a trustworthy family "
                f"({[ (r['family'],r['config'],r['rel'],r['enc']) for r in hp_wins]}); "
                f"headline family={head}. {summ}", diag)

    if eb is not None and eb["rms"] > RMS_SIGNAL_MIN:
        return ("MIDDLE_BAND",
                f"MIDDLE_BAND_PARTIAL_ENVELOPE: scaling improves inductive real_minus_shuf to a "
                f"nonzero envelope max (>{RMS_SIGNAL_MIN}) but PLATEAUS below useful magnitude "
                f"({HP_RMS_MIN}). Curve climbs then flattens -> partial/under-parameterized OR "
                f"one-to-many/content ceiling; this plateau IS the finding. {summ}", diag)

    # envelope at floor across all configs from trustworthy families
    both_brain = fires_hard and fires_soft
    if fires_scorer and both_brain:
        return ("HARD_FAIL",
                f"HARD_FAIL_SCALE_DOES_NOT_HELP: envelope max real_minus_shuf(ind) <= "
                f"{RMS_SIGNAL_MIN} across the WHOLE grid (M_OP {[c['M'] for c in CONFIGS if c['name'].startswith('MOP')]}, "
                f"df/steps/V scans) for ALL trustworthy families WHILE all discriminators fired "
                f"-> scaling this content/mechanism does not extract subject-specific correspondence "
                f"at novel entities; honest content/one-to-many wall. {summ}", diag)
    return ("MIDDLE_BAND",
            f"MIDDLE_BAND_PARTIAL_WALL: trustworthy family(ies) {sorted(trustworthy)} at floor but "
            f"not all discriminators fired -> full wall claim not warranted. {summ}", diag)


# ============================================================================
# arms-differ hash (META_RULE_AF)
# Run on the NON-DEGENERATE synthetic DISCRIMINATING regimes (type-hard for GLOBAL/TEM; content-map
# for GLOBAL/SCORER) where the arm implementations MUST produce different predictions by
# construction. On the REAL relation, arms legitimately collapse to the same (popular-object)
# prediction under shuffle-invariance -- that degeneracy is the FINDING, not a bit-identical-arm
# bug -- so array-identity on real data is the wrong AF regime.
# ============================================================================
def arms_differ_check(seed: int) -> Tuple[bool, Dict[str, str]]:
    preds: Dict[str, np.ndarray] = {}
    # --- type-conditional regime: GLOBAL vs TEM_HARD vs TEM_SOFT vs MEAN_OBJECT must differ ---
    rng = np.random.RandomState(seed + 777)
    N, Ktrue, V, M, T = SYNTH_N, STH_KTRUE, STH_V, STH_M, STH_TEST
    O = np.exp(1j * rng.uniform(-np.pi, np.pi, (V, N))).astype(np.complex64)
    theta = rng.uniform(-np.pi, np.pi, (Ktrue, N)).astype(np.float32)
    TypeSig = np.exp(1j * rng.uniform(-np.pi, np.pi, (Ktrue, N))).astype(np.complex64)

    def _gen_th(n, rs):
        k = rs.randint(0, Ktrue, n); yv = rs.randint(0, V, n)
        objrot = np.exp(1j * (np.angle(O[yv]) - theta[k])).astype(np.complex64)
        mix = STH_ALPHA * TypeSig[k] + STH_OBJSIG * objrot
        A = np.exp(1j * (np.angle(mix) + STH_SIGMA * rs.standard_normal((n, N)))).astype(np.complex64)
        return A, cleanup_argmax_batch(A * np.exp(1j * theta[k]), O)

    A, yA = _gen_th(M, rng)
    C, _ = _gen_th(T, np.random.RandomState(seed + 999))
    Mg = fit_naive_mean(A, yA, O)
    protos, assign = kmeans_phasor(A, TEM_K_SWEEP_SYNTH[-1], seed, TEM_KMEANS_ITERS)
    Mk = fit_tem(A, yA, O, protos, assign)
    preds["GLOBAL_th"] = apply_transform(C, Mg, O)
    preds["TEMHARD_th"] = apply_tem_hard(C, protos, Mk, O)
    preds["TEMSOFT_B8_th"] = apply_tem_soft(C, protos, Mk, O, 8.0)
    preds["MEANOBJ_th"] = apply_transform_meanobj(A, Mg, O, T)

    # --- content-map regime: GLOBAL vs SCORER, and SCORER_REAL vs SCORER_SHUF (paired-batch) ---
    rng2 = np.random.RandomState(seed + 555)
    Nc, d, Vc, Mc, Tc = SYNTH_N, SCM_D, SCM_V, SCM_M, SCM_TEST
    Fo = rng2.standard_normal((Vc, d)).astype(np.float32)
    Fo /= np.linalg.norm(Fo, axis=1, keepdims=True) + 1e-9
    Tmap = rng2.standard_normal((d, d)).astype(np.float32) / np.sqrt(d)
    Wp = rng2.standard_normal((d, Nc)).astype(np.float32)

    def _gen_cm(n, rs):
        F = rs.standard_normal((n, d)).astype(np.float32)
        F /= np.linalg.norm(F, axis=1, keepdims=True) + 1e-9
        return F, ((F @ Tmap.T) @ Fo.T).argmax(axis=1)

    Fs, yA2 = _gen_cm(Mc, rng2)
    Fc, _ = _gen_cm(Tc, np.random.RandomState(seed + 888))
    Oc = np.exp(1j * (Fo @ Wp)).astype(np.complex64)
    Ac = np.exp(1j * (Fs @ Wp)).astype(np.complex64)
    Cc = np.exp(1j * (Fc @ Wp)).astype(np.complex64)
    Mgc = fit_naive_mean(Ac, yA2, Oc)
    ysh = yA2[np.random.RandomState(seed + 991).permutation(Mc)]
    Ps, Po = _proj_pair(d, SCORER_DF_SYNTH, PROJ_SEED)
    Wr, Ws = fit_scorer_paired(Fs, yA2, ysh, Fo, Ps, Po, max(SCORER_STEPS_SYNTH, 200),
                               SCORER_LR, SCORER_TAU, SCORER_L2)
    preds["GLOBAL_cm"] = apply_transform(Cc, Mgc, Oc)
    preds["SCORER_real_cm"] = apply_scorer(Fc, Wr, Fo, Ps, Po)
    preds["SCORER_shuf_cm"] = apply_scorer(Fc, Ws, Fo, Ps, Po)

    digests = {k: hashlib.sha256(v.tobytes()).hexdigest() for k, v in preds.items()}
    # Required-distinct pairs, each guaranteed to differ on ITS OWN discriminating regime:
    required = [
        ("GLOBAL_th", "TEMHARD_th"), ("GLOBAL_th", "TEMSOFT_B8_th"),
        ("GLOBAL_th", "MEANOBJ_th"), ("TEMHARD_th", "MEANOBJ_th"),
        ("SCORER_real_cm", "SCORER_shuf_cm"), ("GLOBAL_cm", "SCORER_real_cm"),
    ]
    ok = all(digests[a] != digests[b] for a, b in required)
    return ok, digests


# ============================================================================
# Formula self-tests (import time, fast < 180s) -- + torch-vs-numpy scorer equivalence
# ============================================================================
def _scorer_backend() -> str:
    return f"torch:{_DEVICE}" if _TORCH_OK else "numpy"


def _formula_selftests() -> float:
    rng = np.random.RandomState(123)
    n = 512
    a = np.exp(1j * rng.uniform(-np.pi, np.pi, n)).astype(np.complex64)
    b = np.exp(1j * rng.uniform(-np.pi, np.pi, n)).astype(np.complex64)
    rt = cos_c(unbind(bind(a, b), a), b)
    assert rt >= 0.90, f"selftest1 bind-roundtrip cos={rt}"

    K = 5; Nt = 256
    theta = rng.uniform(-np.pi, np.pi, Nt).astype(np.float32)
    O = np.exp(1j * rng.uniform(-np.pi, np.pi, (K, Nt))).astype(np.complex64)
    ks = rng.randint(0, K, 40)
    A = np.exp(1j * (np.angle(O[ks]) - theta[None, :] + 0.1 * rng.standard_normal((40, Nt)))).astype(np.complex64)
    Mr = fit_naive_mean(A, ks.astype(np.int64), O)
    kt = rng.randint(0, K, 40)
    Ct = np.exp(1j * (np.angle(O[kt]) - theta[None, :] + 0.1 * rng.standard_normal((40, Nt)))).astype(np.complex64)
    acc_g = float((apply_transform(Ct, Mr, O) == kt).mean())
    assert acc_g >= 0.90, f"selftest2 GLOBAL clean rotation acc={acc_g}"

    # kmeans purity
    Kc = 4; per = 15
    cent = np.exp(1j * rng.uniform(-np.pi, np.pi, (Kc, n))).astype(np.complex64)
    pts, lab = [], []
    for k in range(Kc):
        for _ in range(per):
            pts.append(unit_phasor(cent[k] + 0.05 * (rng.standard_normal(n) + 1j * rng.standard_normal(n))))
            lab.append(k)
    Pn = np.stack(pts).astype(np.complex64); lab = np.array(lab)
    protos, assign = kmeans_phasor(Pn, Kc, 0, 8)
    pure = np.mean([max(np.bincount(lab[assign == k], minlength=Kc)) / max((assign == k).sum(), 1)
                    for k in range(Kc) if (assign == k).sum() > 0])
    assert pure >= 0.85, f"selftest3 kmeans purity={pure}"

    # soft-TEM: at beta->large it approaches hard-argmax; at beta small it is a genuine mixture
    protos2, assign2 = kmeans_phasor(A, 3, 0, TEM_KMEANS_ITERS)
    Mk2 = fit_tem(A, ks.astype(np.int64), O, protos2, assign2)
    ph = apply_tem_hard(Ct, protos2, Mk2, O)
    ps_hi = apply_tem_soft(Ct, protos2, Mk2, O, 1e3)
    frac_match = float((ph == ps_hi).mean())
    assert frac_match >= 0.90, f"selftest4 soft(beta=1e3) != hard argmax frac={frac_match}"

    # type-conditional control: BOTH hard and soft TEM above chance (margins gated at run-time)
    sth0 = synth_type_hard(0)
    ch = sth0["chance"]
    assert sth0["GLOBAL"] >= 2.0 * ch, f"selftest5 GLOBAL {sth0['GLOBAL']} not > chance {ch}"
    assert sth0["TEM_HARD_best"] >= 2.0 * ch, f"selftest5 TEMhard {sth0['TEM_HARD_best']} not > chance"
    assert sth0["TEM_SOFT_best"] >= 2.0 * ch, f"selftest5 TEMsoft {sth0['TEM_SOFT_best']} not > chance"

    # scorer analytic gradient reduces CE + torch backend matches numpy
    d = 32; Vv = 10; Mv = 120; df = 24
    Fo2 = rng.standard_normal((Vv, d)).astype(np.float32); Fo2 /= np.linalg.norm(Fo2, axis=1, keepdims=True) + 1e-9
    Tm = rng.standard_normal((d, d)).astype(np.float32) / np.sqrt(d)
    Fs = rng.standard_normal((Mv, d)).astype(np.float32); Fs /= np.linalg.norm(Fs, axis=1, keepdims=True) + 1e-9
    yy = ((Fs @ Tm.T) @ Fo2.T).argmax(axis=1)
    yy_sh = yy[rng.permutation(Mv)]
    Ps, Po = _proj_pair(d, df, 0)
    W_np = fit_scorer_np(Fs, yy, Fo2, Ps, Po, 200, 1.0, 0.05, 1e-3)
    acc_np = float((apply_scorer(Fs, W_np, Fo2, Ps, Po) == yy).mean())
    assert acc_np >= 0.5, f"selftest6 numpy scorer train acc={acc_np}"
    Wr, Ws = fit_scorer_paired(Fs, yy, yy_sh, Fo2, Ps, Po, 200, 1.0, 0.05, 1e-3)
    acc_bk = float((apply_scorer(Fs, Wr, Fo2, Ps, Po) == yy).mean())
    assert abs(acc_bk - acc_np) <= 0.12, \
        f"selftest7 scorer backend({_scorer_backend()}) acc={acc_bk} vs numpy {acc_np} (>0.12 drift)"
    # shuffled arm must differ from real arm (paired-batch sanity)
    assert not np.array_equal(Wr, Ws), "selftest7b paired REAL==SHUFFLED W (arm-impl bug)"

    print(f"[formula_selftest] bind_rt={rt:.3f} global_clean={acc_g:.3f} kmeans_pure={pure:.3f} "
          f"soft~hard={frac_match:.3f} scorer_np={acc_np:.3f} scorer_{_scorer_backend()}={acc_bk:.3f} "
          f"torch_ok={_TORCH_OK} device={_DEVICE} bge_ok={_BGE.ok} gsbc_ok={_GSBC.ok} PASS", flush=True)
    return rt


_BIND_RT = _formula_selftests()
# reachability (THEORETICAL; no CRLB noise-floor for argmax transfer). At the largest V=1000 in the
# grid, chance=1/1000; HP real_gain floor 0.2075 -> target 0.2085 << 0.95 saturation. Reachable.
assert (1.0 / 100) + HP_REAL_GAIN_MIN < 0.95, "HP threshold must be below saturation"


# ============================================================================
# Defensive: start-marker + crash-diagnostic
# ============================================================================
def _write_start_marker(out_dir: Path):
    marker = {
        "pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR_NAME, "run_mode": RUN_MODE, "device": _DEVICE, "torch_ok": _TORCH_OK,
        "expected_n_units": EXPECTED_N_UNITS, "n_configs": len(CONFIGS), "host": platform.node(),
        "bge_ok": _BGE.ok, "gsbc_ok": _GSBC.ok, "bge_reason": _BGE.reason, "gsbc_reason": _GSBC.reason,
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
        "traceback": traceback.format_exc()[:5000], "ts_iso": datetime.now(timezone.utc).isoformat(),
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
    print(f"[{ANCHOR_NAME}] run_mode={RUN_MODE} device={_DEVICE} torch_ok={_TORCH_OK} N={N_DIM} "
          f"n_configs={len(CONFIGS)} seeds={SEEDS} expected_units={EXPECTED_N_UNITS} "
          f"bge_ok={_BGE.ok} gsbc_ok={_GSBC.ok}", flush=True)
    if not _GSBC.ok:
        print(f"[WARN] gsbc cache unavailable ({_GSBC.reason}); gsbc arm records per-unit "
              f"failure_class; bge_semantic + mechanism axis still valid.", flush=True)

    run_config = {"N": N_DIM, "run_mode": RUN_MODE, "anchor": ANCHOR_NAME}
    done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
    print(f"[ckpt] {len(done)}/{len(SEEDS)} done; running {remaining}", flush=True)

    for seed in remaining:
        r = run_seed(seed)
        write_partial(out_dir, seed, r)
        print(f"[{ANCHOR_NAME}] seed={seed} done ({r['elapsed_s']:.1f}s) fatal={r['fatal']}", flush=True)

    per_seed = aggregate_partials(out_dir, SEEDS, run_config=run_config)
    agg = aggregate(per_seed)
    ad_ok, ad_digests = arms_differ_check(SEEDS[0])
    verdict, verdict_msg, diag = compute_envelope_verdict(agg, ad_ok, _BIND_RT)

    elapsed = time.time() - t_start
    eb = diag.get("envelope_best")
    summary = (f"{verdict}: env_best_rms={round(eb['rms'],4) if eb else None} "
               f"@{eb['config'] if eb else '-'}/{eb['family'] if eb else '-'}")
    metrics = {
        "anchor": ANCHOR_NAME, "anchor_name": ANCHOR_NAME, "run_mode": RUN_MODE,
        "N": N_DIM, "N_DIM": N_DIM, "device": _DEVICE, "torch_ok": _TORCH_OK,
        "relations_semantic": RELATIONS_SEM, "relations_neg_baseline": RELATIONS_NEG,
        "content_encodings": CONTENT_ENCODINGS, "arms": ARMS, "eval_modes": EVAL_MODES,
        "k_list": K_LIST, "beta_list": BETA_LIST,
        "config_grid": [{"name": c["name"], "V": c["V"], "M": c["M"], "df": c["df"],
                         "steps": c["steps"], "mech": c["mech"], "rels": c["rels"],
                         "encs": c["encs"], "K": c["K"], "betas": c["betas"]} for c in CONFIGS],
        "n_seeds": len(per_seed), "seeds": [int(s) for s in per_seed.keys()],
        "expected_n_units": EXPECTED_N_UNITS, "n_units_counted": agg["n_units"],
        "n_units_failed": agg["n_units_failed"],
        "cardinality_ok": (agg["n_units"] - agg["n_units_failed"]) >= EXPECTED_N_UNITS
        or agg["enc_unavailable"].get("gsbc", 0) > 0,
        "arms_differ_verified": ad_ok, "arms_differ_digests": ad_digests,
        "bind_roundtrip": _BIND_RT,
        "synth_rot_clean": agg["synth_rot_clean"], "synth_type_hard": agg["synth_type_hard"],
        "synth_content_map": agg["synth_content_map"],
        "discriminator_fires_tem_hard": diag.get("discriminator_fires_tem_hard"),
        "discriminator_fires_tem_soft": diag.get("discriminator_fires_tem_soft"),
        "discriminator_fires_scorer": diag.get("discriminator_fires_scorer"),
        "trustworthy_families": diag.get("trustworthy_families"),
        "envelope_best": diag.get("envelope_best"), "hp_wins": diag.get("hp_wins"),
        "axis_curves": diag.get("axis_curves"),
        "enc_unavailable": agg["enc_unavailable"], "meta_per_relenc": agg["meta"],
        "hp_scope": {"TEM_SOFT_TEM_HARD_SCORER_REAL_inductive_SEMANTIC": ["HARD_PASS", "HARD_FAIL"],
                     "GLOBAL": ["reference_baseline_TransE_not_a_win"],
                     "DerivedFrom": ["surface_negative_baseline_watchdog_NOT_HP"],
                     "SHUFFLED": [], "MEAN_OBJECT": [], "SYNTH": []},
        "bands": {"HP_REAL_GAIN_MIN": HP_REAL_GAIN_MIN, "HP_RMS_MIN": HP_RMS_MIN,
                  "HP_RMM_MIN": HP_RMM_MIN, "RMS_SIGNAL_MIN": RMS_SIGNAL_MIN,
                  "TEM_ADV_MIN": TEM_ADV_MIN, "SCORER_ADV_MIN": SCORER_ADV_MIN,
                  "SYNTH_CLEAN_MIN": SYNTH_CLEAN_MIN, "BIND_ROUNDTRIP_MIN": BIND_ROUNDTRIP_MIN},
        "cells_aggregate": agg["cells"],
        "gate_diagnostics": {k: v for k, v in diag.items() if k not in ("records",)},
        "per_family_record_count": diag.get("n_records"),
        "corpus_provenance": "conceptnet5_en_100k_real_triples",
        "encoding_provenance": {
            "bge_semantic": "BAAI/bge-small-en-v1.5_bounded_cache_centered_projected_phasor",
            "gsbc": "bge-large-en-v1.5->GSBC_EXPAND2X_student_global_top192_sparse_code_cache"},
        "allow_synthetic": False, "n_generative_llm_calls": 0,
        "metrics_source": "measured_mixed_cpu_numpy_TEM_plus_torch_scorer_scaleup_envelope",
        "verdict": verdict, "verdict_msg": verdict_msg, "summary": summary, "elapsed_s": elapsed,
    }
    tmp_path = out_dir / "metrics.json.tmp"
    with open(tmp_path, "w", encoding="utf-8") as fh:
        json.dump(metrics, fh, indent=2)
    os.replace(tmp_path, out_dir / "metrics.json")

    print(f"[{ANCHOR_NAME}] verdict={verdict}", flush=True)
    print(f"[{ANCHOR_NAME}] {verdict_msg}", flush=True)
    print(f"[{ANCHOR_NAME}] elapsed={elapsed:.1f}s good_units={agg['n_units']-agg['n_units_failed']}/"
          f"{EXPECTED_N_UNITS} device={_DEVICE}", flush=True)


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
