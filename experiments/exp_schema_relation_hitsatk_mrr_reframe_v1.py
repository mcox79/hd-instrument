"""schema_relation_hitsatk_mrr_reframe_v1 -- RANK/SET reframe of the one-to-many entropy ceiling.

SCIENTIFIC QUESTION (the metric-correctness reframe):
  The richer-content vscan cell (schema_relation_richer_content_vscan_v1) landed HARD_FAIL:
  best_joint_rms@V300+=0.1067, best_joint-frozen=0.0022 (< IMPROVE_MIN=0.02) under an EXACT-MATCH
  (argmax single-label) metric MEASURED@data/exp_schema_relation_richer_content_vscan_v1/metrics.json.
  A research drill (CITED@notes/research_reframe_rank_set_prediction_one_to_many_ceiling_2026-07-05.md)
  recomputed the FROZEN scorer's FULL (T,V) score matrix off-disk and found the true object very
  often lands in the top-k but not at rank-1: the exact-match metric grades the substrate OUT of
  signal it is actually recovering. The mechanism is NOT raw fan-out (subject-identity oracle
  E[1/fanout]=0.81/0.94 is an order of magnitude above observed 0.06-0.09) -- it is NEAR-MISS
  content-neighbor competition: several semantically-adjacent objects sit in close score range and
  only ONE gets to be argmax. Standard KG-completion practice (Bordes et al. 2013, filtered Hits@k /
  MRR) is the field-standard remedy for exactly this one-to-many/many-to-many regime.

  THE decisive question: under the FILTERED Hits@k/MRR protocol, does the substrate's inductive
  (novel-subject) relational ranking recover strong signal -- best-of-{FROZEN,JOINT} filtered
  Hits@10 real_minus_shuf >= 0.20 AND MRR real_minus_shuf >= 0.15 on >=2 relations x >=2 encoders
  at V>=300? A curve that recovers Hits@10 but not MRR (or lands in [0.10,0.20)) is THE finding
  (genuine partial recovery; content-resolution still limiting). Constructive; brain-first.

THE ONE CHANGE vs the parent cell: the EVAL METRIC ONLY. Same FROZEN/JOINT scorer (verbatim),
  same split builder (build_split_scaled / load_relation), same features (bge/gsbc caches), same
  paired REAL/SHUFFLED arms, same inductive/transductive modes. Instead of argmax->single-label
  accuracy we keep the full (T,V) score matrix and compute FILTERED rank-based metrics: for the
  held-out true object o*, EXCLUDE the subject's OTHER in-codebook true objects before ranking o*
  against the V codebook objects (Bordes filtered protocol), then Hits@1/3/5/10/20 and MRR. Both
  filtered AND raw reported; FILTERED is the gating metric (raw-vs-filtered is not a hidden
  researcher degree of freedom). Compute overhead vs parent = one argsort per test row (negligible).

DISCRIMINATOR (load-bearing): REAL - SHUFFLED (rms) on INDUCTIVE filtered rank metrics, PAIRED arms.
  Raw ranking is a popularity trap (shuffled-trained scorer concentrates on frequent objects); rms
  isolates the subject->object correspondence that must transfer to novel entities. Two independent
  controls guard against an encoding artifact / scorer-capacity confound:
    (1) SHUFFLED control  -- subtracts the label-marginal / popularity ranking.
    (2) same-features k-NN reference (zero trained parameters, IDENTICAL frozen features) -- if a
        parameter-free neighbor vote lands in the same rms band as the trained scorers, the signal
        lives in the REPRESENTATION not the scorer capacity (rules out "the trained scorer memorized
        a spurious ranking"). k-NN is a REFERENCE, NOT HP-gating.
  DerivedFrom (surface-morphological, ~single-answer) is the discriminating watchdog: when content
  genuinely resolves the answer its rank mass concentrates at top-1 (narrow spread); the semantic
  relations should show a wide rank-1-to-rank-10 spread -- the contrast is itself evidence the
  semantic ceiling is content-resolution-specific, not architecture-generic. NOT HP-eligible.

COMPUTE: class (a) batched-GPU. FROZEN trains both PAIRED arms in one torch-bmm B=2 pass (verbatim);
  JOINT trains both PAIRED arms in one batched autograd model (B=2). k-NN is a vectorized cosine +
  scatter-add. device auto->cuda on the GPU box; numpy fallback for FROZEN/kNN if torch absent
  (JOINT records failure_class if torch absent, never dispatched to a torchless queue). Storage
  strategy: no_storage. No generative-LLM calls (deterministic caches only).

# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; FROZEN REAL!=SHUFFLED score-matrix hash, JOINT too)
# - final_metrics_atomicity = tmp_replace (META_RULE_AH)
# - except SystemExit: raise BEFORE except Exception (no BaseException); start-marker + crash-diag + heartbeat
# - crlb n/a (rank transfer; no closed-form noise floor). chance floor k/V_eff stated; reachability declared
# - baseline_in_band at smoke (SHUFFLED filtered Hits@10 not saturated <0.95; REAL FROZEN in band; synth in-band)
# - discriminator survives scale (B): synth_rank_signal proves FROZEN filtered-rank rms fires on a clean
#   linear content map by construction; synth_rank_null proves rms~0 when no signal. The V>=300 real-data
#   recovery is the MAP question itself (partial-recovery IS a finding), not smoke-provable -> justified.
# - HARD_PASS strictly above floor (Hits@10 rms 0.20 is 2x the HF ceiling 0.10; MIDDLE band [0.10,0.20)
#   sits strictly below -> not a floor-hugging single-threshold, META_RULE_L satisfied by construction)
# - HP_SCOPE: HP gates apply to best-of-{FROZEN,JOINT} REAL/inductive/FILTERED, SEMANTIC rel x enc at V>=300;
#   KNN=reference (not HP); DerivedFrom=watchdog (not HP); SHUFFLED/POP=controls (not HP)
# - cardinality_ok (META_RULE_H; EXPECTED_N_UNITS summed over grid x 3 slots x 2 arms x 2 evals)
# - per-unit failure-class instrumentation (META_RULE_J; no bare except)
# - calibration_check = adaptive_with_discriminator_gate (synth_rank_signal fires + synth_rank_null null
#   are the discriminator-fires proofs; filtered protocol is field-standard, not tuned-for-pass)
# - progress_logging = print_flush_true (all progress lines flush=True; line-buffered stdout)
# - positive controls reproduce filtered-rank arithmetic at import (formula selftest, hand-constructed exact ranks)
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

# torch import (overnight_queue GPU gate greps for `import torch`). Guarded: numpy fallback for FROZEN/kNN.
try:
    import torch
    import torch.nn.functional as F_t
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

ANCHOR_NAME = "schema_relation_hitsatk_mrr_reframe_v1"
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
RELATIONS_SEM = ["AtLocation", "CausesDesire"]      # HP-eligible (real headroom per corpus counts)
RELATIONS_NEG = ["DerivedFrom"]                     # surface-morphological watchdog (NOT HP; contrast)
RELATIONS_ALL = RELATIONS_SEM + RELATIONS_NEG
CONTENT_ENCODINGS = ["bge_semantic", "gsbc"]
ARMS = ["REAL", "SHUFFLED"]
EVAL_MODES = ["inductive", "transductive"]
SCORER_SLOTS = ["FROZEN", "JOINT", "KNN"]           # KNN = same-features zero-param reference
HP_SLOTS = ["FROZEN", "JOINT"]                      # only these are HP-gating (best-of)
PRIMARY_EVAL = "inductive"

# Rank-metric grid
HITS_KS = [1, 3, 5, 10, 20]
METRIC_KEYS = [f"hits{k}" for k in HITS_KS] + ["mrr"]
KNN_K = 15                                          # neighbor count for the k-NN reference (FULL)

# FROZEN scorer hyperparameters (VERBATIM from richer-content vscan v1 SCORER -> same code path)
FROZEN_DF = 384
FROZEN_STEPS = 2000
SCORER_LR = 1.0
SCORER_TAU = 0.05
SCORER_L2 = 1e-3
PROJ_SEED = 12345

# JOINT (richer) content encoder hyperparameters (VERBATIM from parent; NO tuning-for-pass)
JOINT_H = 256
JOINT_DF = 128
JOINT_DROPOUT = 0.1
JOINT_LR = 2e-3
JOINT_WD = 1e-3
JOINT_STEPS = 500
JOINT_TAU = 0.1

# ----------------------------------------------------------------------------
# Synthetic positive-control regimes (CALIBRATED; discriminator-fires proofs, rank-metric version)
# ----------------------------------------------------------------------------
SYNTH_N = N_DIM
SCM_D = 64
SCM_V = 40
SCM_M = 300
SCM_TEST = 200
SCORER_DF_SYNTH = 96
SCORER_STEPS_SYNTH = 300

# Pre-reg bands (LOCKED) -- rank-metric reframe
HP_HITS10_RMS_MIN = 0.20       # best-of{FROZEN,JOINT} filtered Hits@10 real_minus_shuf(ind) HARD_PASS floor
HP_MRR_RMS_MIN = 0.15          # best-of{FROZEN,JOINT} filtered MRR real_minus_shuf(ind) HARD_PASS floor
HF_HITS10_RMS_MAX = 0.10       # HARD_FAIL: max over semantic (rel x enc) of best filtered Hits@10 rms < this
# discriminator-fires gate (synthetic controls; NOT the real-data verdict):
SYNTH_SIGNAL_HITS10_RMS_MIN = 0.30   # clean linear map -> FROZEN filtered-rank rms must be large (fires)
SYNTH_NULL_RMS_MAX = 0.10            # no-signal regime -> |rms| must be small (no false signal)
SYNTH_SIGNAL_MRR_RMS_MIN = 0.20      # clean map -> MRR rms also large
BIND_ROUNDTRIP_MIN = 0.90
BASE_SAT_HI = 0.95             # SHUFFLED filtered Hits@10 must be below this (not saturated)


# ----------------------------------------------------------------------------
# CONFIG GRID
# ----------------------------------------------------------------------------
def _cfg(name, V, M, rels, encs):
    return {"name": name, "V": V, "M": M, "rels": list(rels), "encs": list(encs)}


if RUN_MODE == "smoke":
    SEEDS = [7]
    N_TEST_PER = 60
    POOL_CAP = 6000
    # SMOKE = FAST but SMOKE==FULL branch coverage: V100 + a V300 config so the load-bearing
    # V>=300 verdict branch (HARD_PASS/HARD_FAIL/MIDDLE) is exercised. tiny M, bge only.
    CONFIGS = [_cfg("V100", 100, 200, RELATIONS_SEM, ["bge_semantic"]),
               _cfg("V300", 300, 300, RELATIONS_SEM, ["bge_semantic"])]
    _SMOKE_JOINT = dict(H=128, DF=64, STEPS=80)
    _SMOKE_FROZEN_STEPS = 300
    _SMOKE_FROZEN_DF = 128
    _SMOKE_KNN_K = 10
else:
    SEEDS = [7, 13, 19]
    N_TEST_PER = 150
    POOL_CAP = 30000
    # PRIMARY V-scan (M=800 matched to the parent -> FROZEN reproduces the same code path)
    CONFIGS = [_cfg(f"V{v}", v, 800, RELATIONS_ALL, CONTENT_ENCODINGS) for v in [100, 300, 1000]]
    _SMOKE_JOINT = None
    _SMOKE_FROZEN_STEPS = None
    _SMOKE_FROZEN_DF = None
    _SMOKE_KNN_K = None


def _joint_hp():
    if RUN_MODE == "smoke":
        return _SMOKE_JOINT["H"], _SMOKE_JOINT["DF"], _SMOKE_JOINT["STEPS"]
    return JOINT_H, JOINT_DF, JOINT_STEPS


def _frozen_hp():
    if RUN_MODE == "smoke":
        return _SMOKE_FROZEN_DF, _SMOKE_FROZEN_STEPS
    return FROZEN_DF, FROZEN_STEPS


def _knn_k():
    return _SMOKE_KNN_K if RUN_MODE == "smoke" else KNN_K


def expected_units(configs, seeds) -> int:
    # per (cfg,rel,enc): slots(3) x arms(2) x evals(2) = 12
    tot = 0
    for c in configs:
        tot += len(c["rels"]) * len(c["encs"]) * (len(SCORER_SLOTS) * len(ARMS) * len(EVAL_MODES))
    return tot * len(seeds)


EXPECTED_N_UNITS = expected_units(CONFIGS, SEEDS)


# ============================================================================
# FHRR primitives (complex64 phasors) -- self-contained (only for bind-roundtrip sanity rail)
# ============================================================================
def _stable_seed(text: str, salt: int = 0) -> int:
    h = hashlib.md5(f"{salt}:{text}".encode("utf-8")).hexdigest()
    return int(h[:8], 16)


def bind(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    return (a * b).astype(np.complex64)


def unbind(c: np.ndarray, a: np.ndarray) -> np.ndarray:
    return (c * np.conj(a)).astype(np.complex64)


def cos_c(x: np.ndarray, y: np.ndarray) -> float:
    num = float(np.vdot(y, x).real)
    den = float(np.linalg.norm(x) * np.linalg.norm(y)) + 1e-12
    return num / den


# ============================================================================
# Content encoders (ZERO generative-LLM; deterministic) -- self-contained
# ============================================================================
class ContentUnavailable(Exception):
    pass


class _CachedSemanticEncoder:
    """Dense-embedding cache -> center -> unit feature. Missing cache -> ok=False (per-unit record)."""

    def __init__(self, n: int, cache_rel: Path, emb_key: str, ent_key: str, name: str):
        self.n = n
        self.name = name
        self.ok = False
        self.reason = ""
        self.dim = 0
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
        self.ok = True

    def feature(self, s: str) -> np.ndarray:
        v = self._fcache.get(s)
        if v is not None:
            return v
        i = self.idx.get(s)
        v = self.emb[i] if i is not None else np.zeros(self.dim, dtype=np.float32)
        self._fcache[s] = v
        return v


_BGE = _CachedSemanticEncoder(N_DIM, BGE_CACHE_REL, "emb", "entities", "bge")
_GSBC = _CachedSemanticEncoder(N_DIM, GSBC_CACHE_REL, "code", "entities", "gsbc")


def _enc(encoding: str) -> _CachedSemanticEncoder:
    if encoding == "bge_semantic":
        return _BGE
    if encoding == "gsbc":
        return _GSBC
    raise ValueError(f"unknown encoding {encoding}")


def encode_feature_matrix(ents: List[str], encoding: str) -> np.ndarray:
    e = _enc(encoding)
    if not e.ok:
        raise ContentUnavailable(e.reason)
    F = np.stack([e.feature(s) for s in ents]).astype(np.float32)
    nrm = np.linalg.norm(F, axis=1, keepdims=True) + 1e-9
    return (F / nrm).astype(np.float32)


# ============================================================================
# FROZEN scorer (bilinear RESCAL/DistMult on FIXED random projection) -- VERBATIM from parent
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


def score_scorer(Fc, W, Fo, Ps, Po) -> np.ndarray:
    """Full (T,V) score matrix (NO argmax) -- the ONLY substantive change vs the parent's apply_scorer."""
    U = Fc @ Ps
    Vo = Fo @ Po
    return ((U @ W) @ Vo.T).astype(np.float32)


def fit_scorer_paired(Fa, y_real, y_shuf, Fo, Ps, Po, steps, lr, tau, l2):
    """Fit REAL+SHUFFLED bilinear W in one batched pass. torch bmm B=2 on device if available."""
    if _TORCH_OK:
        dev = _DEVICE

        def _t(x):
            return torch.as_tensor(np.ascontiguousarray(x, dtype=np.float32), device=dev)
        U = _t(Fa) @ _t(Ps)
        Vo = _t(Fo) @ _t(Po)
        M, df = int(U.shape[0]), int(U.shape[1])
        Ub = U.unsqueeze(0).expand(2, -1, -1)
        VoB = Vo.unsqueeze(0).expand(2, -1, -1)
        VoT = Vo.t().unsqueeze(0).expand(2, -1, -1).contiguous()
        W = torch.zeros((2, df, df), dtype=torch.float32, device=dev)
        ys = torch.stack([torch.as_tensor(y_real, device=dev, dtype=torch.long),
                          torch.as_tensor(y_shuf, device=dev, dtype=torch.long)])
        ar = torch.arange(M, device=dev)
        for _ in range(steps):
            S = torch.bmm(torch.bmm(Ub, W), VoT) / tau
            S = S - S.max(dim=2, keepdim=True).values
            P = torch.softmax(S, dim=2)
            P[0, ar, ys[0]] -= 1.0
            P[1, ar, ys[1]] -= 1.0
            P = P / M
            gW = torch.bmm(Ub.transpose(1, 2), torch.bmm(P, VoB)) / tau + l2 * W
            W = W - lr * gW
        Wr = W[0].detach().to("cpu").numpy().astype(np.float32)
        Ws = W[1].detach().to("cpu").numpy().astype(np.float32)
        return Wr, Ws
    Wr = fit_scorer_np(Fa, y_real, Fo, Ps, Po, steps, lr, tau, l2)
    Ws = fit_scorer_np(Fa, y_shuf, Fo, Ps, Po, steps, lr, tau, l2)
    return Wr, Ws


# ============================================================================
# JOINT (richer jointly-trained content encoder) -- torch autograd; batched B=2 paired.
# Returns SCORE matrices per (arm, eval) instead of argmax (the reframe).
# ============================================================================
class JointUnavailable(Exception):
    pass


def _joint_init_params(d: int, h: int, df: int, init_seed: int, dev):
    g = torch.Generator(device="cpu").manual_seed(int(init_seed))
    sd_d = 1.0 / float(np.sqrt(d))
    sd_h = 1.0 / float(np.sqrt(h))
    W1 = (torch.randn(d, h, generator=g) * sd_d)
    b1 = torch.zeros(h)
    W2 = (torch.randn(h, df, generator=g) * sd_h)
    b2 = torch.zeros(df)
    R = torch.eye(df) + 0.01 * torch.randn(df, df, generator=g)

    def _b(t):
        return t.unsqueeze(0).repeat(2, *([1] * t.dim())).clone().to(dev).requires_grad_(True)
    return {"W1": _b(W1), "b1": _b(b1), "W2": _b(W2), "b2": _b(b2), "R": _b(R)}


def _joint_encode(Fb, params, train: bool, dropout: float):
    h = torch.einsum("nd,bdh->bnh", Fb, params["W1"]) + params["b1"].unsqueeze(1)
    h = torch.tanh(h)
    if train and dropout > 0:
        h = F_t.dropout(h, p=dropout, training=True)
    z = torch.einsum("bnh,bhe->bne", h, params["W2"]) + params["b2"].unsqueeze(1)
    return z


def joint_train_score(Fa, y_real, y_shuf, Fo, Fc_by, d, init_seed,
                      h, df, steps, lr, wd, tau, dropout) -> Dict[str, Dict[str, np.ndarray]]:
    """Train batched (B=2) joint encoder + bilinear relation on REAL and SHUFFLED. Returns
    {arm -> {eval_mode -> (T,V) float score matrix}}. Inductive-valid (g is a fn of frozen features)."""
    if not _TORCH_OK:
        raise JointUnavailable("JOINT_TORCH_UNAVAILABLE")
    dev = _DEVICE
    Fa_t = torch.as_tensor(np.ascontiguousarray(Fa, dtype=np.float32), device=dev)
    Fo_t = torch.as_tensor(np.ascontiguousarray(Fo, dtype=np.float32), device=dev)
    y = torch.stack([torch.as_tensor(y_real, device=dev, dtype=torch.long),
                     torch.as_tensor(y_shuf, device=dev, dtype=torch.long)])
    params = _joint_init_params(d, h, df, init_seed, dev)
    plist = list(params.values())
    opt = torch.optim.Adam(plist, lr=lr, weight_decay=wd)
    for _ in range(steps):
        opt.zero_grad(set_to_none=True)
        Us = _joint_encode(Fa_t, params, train=True, dropout=dropout)
        Vo = _joint_encode(Fo_t, params, train=True, dropout=dropout)
        SR = torch.einsum("bmd,bde->bme", Us, params["R"])
        logits = torch.einsum("bme,bve->bmv", SR, Vo) / tau
        loss = F_t.cross_entropy(logits[0], y[0]) + F_t.cross_entropy(logits[1], y[1])
        loss.backward()
        opt.step()
    out: Dict[str, Dict[str, np.ndarray]] = {"REAL": {}, "SHUFFLED": {}}
    with torch.no_grad():
        Vo = _joint_encode(Fo_t, params, train=False, dropout=0.0)
        for ev, Fc in Fc_by.items():
            Fc_t = torch.as_tensor(np.ascontiguousarray(Fc, dtype=np.float32), device=dev)
            Uc = _joint_encode(Fc_t, params, train=False, dropout=0.0)
            SR = torch.einsum("btd,bde->bte", Uc, params["R"])
            logits = torch.einsum("bte,bve->btv", SR, Vo)   # (2,T,V)
            sc = logits.to("cpu").numpy().astype(np.float32)
            out["REAL"][ev] = sc[0]
            out["SHUFFLED"][ev] = sc[1]
    return out


# ============================================================================
# k-NN reference (same frozen features, zero trained parameters). Similarity-weighted object vote.
# ============================================================================
def knn_scores(Fc, Fa, y_train, V_eff, k) -> np.ndarray:
    """(T,V) similarity-weighted neighbor vote. Fc:(T,d) unit, Fa:(M,d) unit -> cosine = dot.
    score[t,j] = sum over top-k neighbors of Fc[t] whose train object == j of relu(cosine)."""
    sims = (Fc @ Fa.T).astype(np.float32)            # (T,M)
    M = sims.shape[1]
    kk = int(min(k, M))
    T = Fc.shape[0]
    idx = np.argpartition(-sims, kk - 1, axis=1)[:, :kk]     # (T,kk) top-kk neighbor indices
    rows = np.repeat(np.arange(T), kk)
    nbr = idx.reshape(-1)
    w = np.maximum(sims[rows, nbr], 0.0)             # relu cosine weight (cosine can be negative)
    obj = y_train[nbr].astype(np.int64)
    scores = np.zeros((T, V_eff), dtype=np.float32)
    np.add.at(scores, (rows, obj), w)
    return scores


# ============================================================================
# FILTERED rank metrics (Bordes et al. 2013) -- THE new eval machinery.
# ============================================================================
def filtered_ranks(scores: np.ndarray, y_true: np.ndarray, filter_mask: np.ndarray) -> np.ndarray:
    """1-based rank of the held-out true object per row, EXCLUDING the subject's other true objects.
    scores:(T,V); y_true:(T,); filter_mask:(T,V) bool True at OTHER-true objects (never at y_true).
    rank = 1 + #{ j : j != y_true, not filtered, score[j] > score[y_true] }  (optimistic ties)."""
    T = scores.shape[0]
    ar = np.arange(T)
    st = scores[ar, y_true][:, None]                 # (T,1) true-object score
    greater = (scores > st) & (~filter_mask)
    greater[ar, y_true] = False
    return (1 + greater.sum(axis=1)).astype(np.int64)


def rank_metrics(ranks: np.ndarray) -> Dict[str, float]:
    r = ranks.astype(np.float64)
    out = {f"hits{k}": float((ranks <= k).mean()) for k in HITS_KS}
    out["mrr"] = float((1.0 / r).mean())
    return out


def _filter_mask(test_subs: List[str], y_true: np.ndarray, by_subj: Dict[str, List[str]],
                 obj_idx: Dict[str, int], V_eff: int) -> np.ndarray:
    """(T,V) bool: True at the subject's OTHER in-codebook true objects (excludes the held-out one)."""
    T = len(test_subs)
    fm = np.zeros((T, V_eff), dtype=bool)
    for t, s in enumerate(test_subs):
        for o in by_subj.get(s, ()):
            j = obj_idx.get(o)
            if j is not None:
                fm[t, j] = True
        fm[t, int(y_true[t])] = False                # never filter the held-out true object itself
    return fm


# ============================================================================
# Data loading + scaled split -- VERBATIM logic from parent (returns by_subj for filtering)
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
        "chance": 1.0 / V_eff, "m_eff": m_eff, "by_subj": {s: list(v) for s, v in by_subj.items()},
    }


# ============================================================================
# Core evaluation: one (config, relation, encoding, seed) -> per-slot filtered+raw rank metrics
# ============================================================================
def eval_config_relenc(cfg: Dict, relation: str, encoding: str, seed: int) -> Dict:
    V = cfg["V"]; M_op = cfg["M"]
    fdf, fsteps = _frozen_hp()
    jh, jdf, jsteps = _joint_hp()
    kk = _knn_k()
    sp = build_split_scaled(relation, seed, V, N_TEST_PER, POOL_CAP, M_op)
    codebook = sp["codebook"]; obj_idx = sp["obj_idx"]
    train_pairs = sp["train_pairs"]; ind_test = sp["ind_test"]; trans_test = sp["trans_test"]
    V_eff = sp["V_eff"]; m_eff = sp["m_eff"]; by_subj = sp["by_subj"]

    train_subs = [s for s, _ in train_pairs]
    y_train = np.array([obj_idx[o] for _, o in train_pairs], dtype=np.int64)
    rng = np.random.RandomState(seed + 991)
    perm = rng.permutation(len(train_pairs))
    y_shuf = y_train[perm]
    y_ind = np.array([obj_idx[o] for _, o in ind_test], dtype=np.int64)
    y_trans = np.array([obj_idx[o] for _, o in trans_test], dtype=np.int64)
    ind_subs = [s for s, _ in ind_test]
    trans_subs = [s for s, _ in trans_test]
    y_by = {"inductive": y_ind, "transductive": y_trans}
    subs_by = {"inductive": ind_subs, "transductive": trans_subs}

    # Features (frozen content; shared by FROZEN + JOINT + KNN so the comparison is representation-only)
    Fo = encode_feature_matrix(codebook, encoding)
    Fa = encode_feature_matrix(train_subs, encoding)
    Fc_ind = encode_feature_matrix(ind_subs, encoding)
    Fc_tr = encode_feature_matrix(trans_subs, encoding)
    Fc_by = {"inductive": Fc_ind, "transductive": Fc_tr}
    d = Fa.shape[1]

    # Filter masks (Bordes filtered) + raw masks, per eval mode (slot/arm-independent -> build once)
    filt_mask = {ev: _filter_mask(subs_by[ev], y_by[ev], by_subj, obj_idx, V_eff) for ev in EVAL_MODES}
    zero_mask = {ev: np.zeros((len(y_by[ev]), V_eff), dtype=bool) for ev in EVAL_MODES}

    # fan-out per test subject (in-codebook), for stratification diagnostic
    fanout_by = {ev: np.array([sum(1 for o in by_subj.get(s, ()) if o in obj_idx)
                               for s in subs_by[ev]], dtype=np.int64) for ev in EVAL_MODES}

    # score matrices per slot/arm/eval
    score_mats: Dict[str, Dict[str, Dict[str, np.ndarray]]] = {
        s: {a: {} for a in ARMS} for s in SCORER_SLOTS}

    # --- FROZEN (fixed random proj + trained bilinear; torch bmm B=2 paired) ---
    Ps, Po = _proj_pair(d, fdf, PROJ_SEED)
    Wr, Ws = fit_scorer_paired(Fa, y_train, y_shuf, Fo, Ps, Po, fsteps,
                               SCORER_LR, SCORER_TAU, SCORER_L2)
    for ev in EVAL_MODES:
        score_mats["FROZEN"]["REAL"][ev] = score_scorer(Fc_by[ev], Wr, Fo, Ps, Po)
        score_mats["FROZEN"]["SHUFFLED"][ev] = score_scorer(Fc_by[ev], Ws, Fo, Ps, Po)

    # --- JOINT (richer jointly-trained content encoder; torch autograd, batched B=2 paired) ---
    init_seed = _stable_seed(f"{cfg['name']}|{relation}|{encoding}", salt=seed)
    jp = joint_train_score(Fa, y_train, y_shuf, Fo, Fc_by, d, init_seed,
                           jh, jdf, jsteps, JOINT_LR, JOINT_WD, JOINT_TAU, JOINT_DROPOUT)
    for ev in EVAL_MODES:
        score_mats["JOINT"]["REAL"][ev] = jp["REAL"][ev]
        score_mats["JOINT"]["SHUFFLED"][ev] = jp["SHUFFLED"][ev]

    # --- KNN reference (same features, zero params; REAL uses y_train, SHUFFLED uses y_shuf) ---
    for ev in EVAL_MODES:
        score_mats["KNN"]["REAL"][ev] = knn_scores(Fc_by[ev], Fa, y_train, V_eff, kk)
        score_mats["KNN"]["SHUFFLED"][ev] = knn_scores(Fc_by[ev], Fa, y_shuf, V_eff, kk)

    # metrics: filtered + raw per slot/arm/eval
    metrics: Dict[str, Dict[str, Dict[str, Dict[str, Dict[str, float]]]]] = {
        s: {a: {ev: {} for ev in EVAL_MODES} for a in ARMS} for s in SCORER_SLOTS}
    for slot in SCORER_SLOTS:
        for arm in ARMS:
            for ev in EVAL_MODES:
                S = score_mats[slot][arm][ev]
                yv = y_by[ev]
                r_filt = filtered_ranks(S, yv, filt_mask[ev])
                r_raw = filtered_ranks(S, yv, zero_mask[ev])
                # invariant: filtering can only help -> filtered rank <= raw rank (per row)
                assert np.all(r_filt <= r_raw), \
                    f"FILTER_INVARIANT_VIOLATION {slot}|{arm}|{ev}: filtered rank > raw rank"
                metrics[slot][arm][ev] = {"filt": rank_metrics(r_filt), "raw": rank_metrics(r_raw)}

    # POPULARITY reference (C-independent floor): rank objects by train frequency (same all subjects)
    pop_score = np.bincount(y_train, minlength=V_eff).astype(np.float32)
    pop = {}
    for ev in EVAL_MODES:
        Sp = np.tile(pop_score[None, :], (len(y_by[ev]), 1))
        r = filtered_ranks(Sp, y_by[ev], filt_mask[ev])
        pop[ev] = rank_metrics(r)

    # fan-out stratification (FROZEN REAL inductive filtered) -- diagnostic only
    strat = {}
    S = score_mats["FROZEN"]["REAL"]["inductive"]
    r_filt = filtered_ranks(S, y_ind, filt_mask["inductive"])
    fo = fanout_by["inductive"]
    for label, sel in (("fanout1", fo == 1), ("fanout2plus", fo >= 2)):
        n = int(sel.sum())
        if n > 0:
            rr = r_filt[sel]
            strat[label] = {"n": n, "hits1": float((rr <= 1).mean()), "hits5": float((rr <= 5).mean())}
        else:
            strat[label] = {"n": 0, "hits1": None, "hits5": None}

    return {"metrics": metrics, "pop": pop, "strat": strat, "V_eff": V_eff, "m_eff": m_eff,
            "chance": 1.0 / V_eff, "n_ind": len(y_ind), "n_trans": len(y_trans),
            "score_digests": {f"{sl}|{ar}|inductive": hashlib.sha256(
                np.ascontiguousarray(score_mats[sl][ar]["inductive"]).tobytes()).hexdigest()
                for sl in SCORER_SLOTS for ar in ARMS}}


# ============================================================================
# Synthetic positive controls (discriminator-fires proofs; rank-metric version)
# ============================================================================
def _gen_linear_content(seed: int, d: int, V: int, M: int, T: int):
    rng = np.random.RandomState(seed)
    Fo = rng.standard_normal((V, d)).astype(np.float32)
    Fo /= np.linalg.norm(Fo, axis=1, keepdims=True) + 1e-9
    Tmap = rng.standard_normal((d, d)).astype(np.float32) / np.sqrt(d)

    def gen(n, rs):
        Fx = rs.standard_normal((n, d)).astype(np.float32)
        Fx /= np.linalg.norm(Fx, axis=1, keepdims=True) + 1e-9
        y = ((Fx @ Tmap.T) @ Fo.T).argmax(axis=1)
        return Fx, y
    Fs, yA = gen(M, rng)
    Fc, yC = gen(T, np.random.RandomState(seed + 7))
    return Fs, yA, Fc, yC, Fo


def synth_rank_signal(seed: int) -> Dict[str, float]:
    """object = argmax LINEAR-map(subject content) (clean, deterministic, fanout=1 per subject).
    FROZEN filtered-rank REAL must beat SHUFFLED by a wide margin -> discriminator fires + rank
    machinery correct. Empty filter (single true object per synth subject)."""
    d, V, M, T = SCM_D, SCM_V, SCM_M, SCM_TEST
    Fs, yA, Fc, yC, Fo = _gen_linear_content(seed + 555, d, V, M, T)
    Ps, Po = _proj_pair(d, SCORER_DF_SYNTH, PROJ_SEED)
    ish = np.random.RandomState(seed + 991).permutation(M)
    Wr, Ws = fit_scorer_paired(Fs, yA, yA[ish], Fo, Ps, Po, max(SCORER_STEPS_SYNTH, 300),
                               SCORER_LR, SCORER_TAU, SCORER_L2)
    fm = np.zeros((T, V), dtype=bool)
    mr = rank_metrics(filtered_ranks(score_scorer(Fc, Wr, Fo, Ps, Po), yC, fm))
    ms = rank_metrics(filtered_ranks(score_scorer(Fc, Ws, Fo, Ps, Po), yC, fm))
    return {"REAL": mr, "SHUFFLED": ms, "hits10_rms": mr["hits10"] - ms["hits10"],
            "mrr_rms": mr["mrr"] - ms["mrr"], "chance": 1.0 / V}


def synth_rank_null(seed: int) -> Dict[str, float]:
    """random content, labels INDEPENDENT of content -> FROZEN cannot learn correspondence ->
    filtered-rank REAL ~ SHUFFLED (rms ~ 0). Proves the metric does NOT invent false signal."""
    rng = np.random.RandomState(seed + 424242)
    d, V, M, T = SCM_D, SCM_V, SCM_M, SCM_TEST

    def _unit(n):
        X = rng.standard_normal((n, d)).astype(np.float32)
        X /= np.linalg.norm(X, axis=1, keepdims=True) + 1e-9
        return X
    Fo = _unit(V); Fs = _unit(M); Fc = _unit(T)
    yA = rng.randint(0, V, M); yC = rng.randint(0, V, T)
    Ps, Po = _proj_pair(d, SCORER_DF_SYNTH, PROJ_SEED)
    ish = rng.permutation(M)
    Wr, Ws = fit_scorer_paired(Fs, yA, yA[ish], Fo, Ps, Po, 300, SCORER_LR, SCORER_TAU, SCORER_L2)
    fm = np.zeros((T, V), dtype=bool)
    mr = rank_metrics(filtered_ranks(score_scorer(Fc, Wr, Fo, Ps, Po), yC, fm))
    ms = rank_metrics(filtered_ranks(score_scorer(Fc, Ws, Fo, Ps, Po), yC, fm))
    return {"REAL": mr, "SHUFFLED": ms, "hits10_rms": mr["hits10"] - ms["hits10"],
            "mrr_rms": mr["mrr"] - ms["mrr"], "chance": 1.0 / V}


# ============================================================================
# arms-differ hash (META_RULE_AF) -- FROZEN/JOINT REAL vs SHUFFLED score matrices must differ
# ============================================================================
def arms_differ_check(seed: int) -> Tuple[bool, Dict[str, str]]:
    d, V, M, T = SCM_D, SCM_V, SCM_M, SCM_TEST
    Fs, yA, Fc, yC, Fo = _gen_linear_content(seed + 555, d, V, M, T)
    ish = np.random.RandomState(seed + 991).permutation(M)
    Ps, Po = _proj_pair(d, SCORER_DF_SYNTH, PROJ_SEED)
    Wr, Ws = fit_scorer_paired(Fs, yA, yA[ish], Fo, Ps, Po, 300, SCORER_LR, SCORER_TAU, SCORER_L2)
    preds: Dict[str, np.ndarray] = {
        "FROZEN_real": score_scorer(Fc, Wr, Fo, Ps, Po),
        "FROZEN_shuf": score_scorer(Fc, Ws, Fo, Ps, Po),
    }
    if _TORCH_OK:
        jp = joint_train_score(Fs, yA, yA[ish], Fo, {"e": Fc}, d, _stable_seed("ad", salt=seed),
                               128, 64, 300, JOINT_LR, JOINT_WD, JOINT_TAU, JOINT_DROPOUT)
        preds["JOINT_real"] = jp["REAL"]["e"]
        preds["JOINT_shuf"] = jp["SHUFFLED"]["e"]
    digests = {k: hashlib.sha256(np.ascontiguousarray(v).tobytes()).hexdigest() for k, v in preds.items()}
    required = [("FROZEN_real", "FROZEN_shuf")]
    if _TORCH_OK:
        required += [("JOINT_real", "JOINT_shuf"), ("FROZEN_real", "JOINT_real")]
    ok = all(digests[a] != digests[b] for a, b in required)
    return ok, digests


# ============================================================================
# Per-seed driver (failure-instrumented; no silent continue)
# ============================================================================
def _unit_key(cfgname, rel, enc, slot, arm, ev):
    return f"{cfgname}|{rel}|{enc}|{slot}|{arm}|{ev}"


def _flatten_unit(per_unit, cfgname, rel, enc, slot, arm, ev, metric_dict, fc):
    per_unit[_unit_key(cfgname, rel, enc, slot, arm, ev)] = {
        "config": cfgname, "relation": rel, "encoding": enc, "mech": slot, "arm": arm, "eval": ev,
        "filt": (metric_dict["filt"] if metric_dict is not None else None),
        "raw": (metric_dict["raw"] if metric_dict is not None else None),
        "failure_class": fc}


def _rms_filt(per_unit, cfgname, rel, enc, slot, metric, ev="inductive"):
    r = per_unit.get(_unit_key(cfgname, rel, enc, slot, "REAL", ev))
    s = per_unit.get(_unit_key(cfgname, rel, enc, slot, "SHUFFLED", ev))
    if not r or not s or r.get("filt") is None or s.get("filt") is None:
        return float("nan")
    return r["filt"][metric] - s["filt"][metric]


def _print_cfg_progress(cfg, per_unit, seed):
    cn = cfg["name"]; rel = cfg["rels"][0]; enc = cfg["encs"][0]
    fz10 = _rms_filt(per_unit, cn, rel, enc, "FROZEN", "hits10")
    jt10 = _rms_filt(per_unit, cn, rel, enc, "JOINT", "hits10")
    kn10 = _rms_filt(per_unit, cn, rel, enc, "KNN", "hits10")
    fzm = _rms_filt(per_unit, cn, rel, enc, "FROZEN", "mrr")
    print(f"  [seed={seed} {cn:<6} {rel[:11]:<11} {enc[:4]}] filt Hits@10 rms: "
          f"FROZEN={fz10:+.3f} JOINT={jt10:+.3f} KNN={kn10:+.3f} | FROZEN MRR rms={fzm:+.3f}", flush=True)


def _emit_heartbeat(out_dir: Path, unit_idx: int, total: int, t0: float):
    row = {"ts_iso": datetime.now(timezone.utc).isoformat(), "unit_idx": unit_idx,
           "total_units": total, "elapsed_s": time.time() - t0}
    try:
        with open(out_dir / "_heartbeat.jsonl", "a", encoding="utf-8") as f:
            f.write(json.dumps(row) + "\n")
    except Exception:
        pass


def run_seed(seed: int, out_dir: Path) -> Dict:
    t0 = time.time()
    per_unit: Dict[str, Dict] = {}
    meta: Dict[str, Dict] = {}
    strat_all: Dict[str, Dict] = {}
    pop_all: Dict[str, Dict] = {}
    fatal = False
    fatal_msg = None
    unit_i = 0
    for cfg in CONFIGS:
        cfgname = cfg["name"]
        for relation in cfg["rels"]:
            for enc in cfg["encs"]:
                fc = None
                res = None
                try:
                    res = eval_config_relenc(cfg, relation, enc, seed)
                except ContentUnavailable as e:
                    fc = str(e)
                except JointUnavailable as e:
                    fc = str(e)
                except Exception as e:
                    fatal = True
                    fatal_msg = f"{cfgname}|{relation}|{enc}:{type(e).__name__}:{str(e)[:200]}"
                    print(f"  [seed={seed} {cfgname} {relation} {enc}] FAILED "
                          f"{type(e).__name__}: {e}", flush=True)
                    traceback.print_exc()
                    break
                for slot in SCORER_SLOTS:
                    for arm in ARMS:
                        for ev in EVAL_MODES:
                            md = res["metrics"][slot][arm][ev] if res is not None else None
                            _flatten_unit(per_unit, cfgname, relation, enc, slot, arm, ev, md, fc)
                if res is not None:
                    k = f"{cfgname}|{relation}|{enc}"
                    meta[k] = {"V_eff": res["V_eff"], "m_eff": res["m_eff"], "chance": res["chance"],
                               "n_ind": res["n_ind"], "n_trans": res["n_trans"],
                               "score_digests": res["score_digests"]}
                    strat_all[k] = res["strat"]
                    pop_all[k] = res["pop"]
                unit_i += 1
                _emit_heartbeat(out_dir, unit_i, len(CONFIGS), t0)
            if fatal:
                break
        if fatal:
            break
        _print_cfg_progress(cfg, per_unit, seed)

    srs = synth_rank_signal(seed)
    srn = synth_rank_null(seed)
    print(f"  [seed={seed} SYNTH] SIGNAL(clean-map) Hits@10 rms={srs['hits10_rms']:+.3f} "
          f"MRR rms={srs['mrr_rms']:+.3f} || NULL(no-signal) Hits@10 rms={srn['hits10_rms']:+.3f} "
          f"MRR rms={srn['mrr_rms']:+.3f}", flush=True)

    return {
        "seed": seed, "N": N_DIM, "run_mode": RUN_MODE, "device": _DEVICE, "torch_ok": _TORCH_OK,
        "config_version": f"ANCHOR={ANCHOR_NAME},N={N_DIM},configs={len(CONFIGS)},seeds={SEEDS}",
        "per_unit": per_unit, "meta": meta, "strat": strat_all, "pop": pop_all,
        "synth_rank_signal": srs, "synth_rank_null": srn,
        "fatal": fatal, "fatal_msg": fatal_msg, "elapsed_s": time.time() - t0,
    }


# ============================================================================
# Aggregate + verdict (rank-metric reframe; do not force a pass)
# ============================================================================
def _mean_std(vals: List[float]) -> Tuple[float, float, int]:
    v = [x for x in vals if x == x]
    n = len(v)
    if n == 0:
        return float("nan"), 0.0, 0
    return float(np.mean(v)), (float(np.std(v, ddof=1)) if n > 1 else 0.0), n


def aggregate(per_seed: Dict) -> Dict:
    # bucket per (unit_key, protocol, metric) -> list across seeds
    buckets: Dict[str, List[float]] = collections.defaultdict(list)
    n_units = 0
    n_failed = 0
    enc_unavailable = collections.Counter()
    joint_unavailable = 0
    meta_all: Dict[str, Dict] = {}
    strat_all: Dict[str, List[Dict]] = collections.defaultdict(list)
    pop_all: Dict[str, List[Dict]] = collections.defaultdict(list)
    srs_h, srs_m, srn_h, srn_m = [], [], [], []
    for sd in per_seed.values():
        for key, rec in sd.get("per_unit", {}).items():
            n_units += 1
            if rec.get("filt") is None:
                n_failed += 1
                fc = rec.get("failure_class", "NA")
                if isinstance(fc, str) and "CACHE_MISSING" in fc:
                    enc_unavailable[rec.get("encoding", "?")] += 1
                elif isinstance(fc, str) and "JOINT_TORCH_UNAVAILABLE" in fc:
                    joint_unavailable += 1
                continue
            for proto in ("filt", "raw"):
                for mk in METRIC_KEYS:
                    buckets[f"{key}|{proto}|{mk}"].append(float(rec[proto][mk]))
        for mk, mv in sd.get("meta", {}).items():
            meta_all[mk] = mv
        for mk, mv in sd.get("strat", {}).items():
            strat_all[mk].append(mv)
        for mk, mv in sd.get("pop", {}).items():
            pop_all[mk].append(mv)
        srs = sd.get("synth_rank_signal", {}); srn = sd.get("synth_rank_null", {})
        if srs:
            srs_h.append(srs["hits10_rms"]); srs_m.append(srs["mrr_rms"])
        if srn:
            srn_h.append(srn["hits10_rms"]); srn_m.append(srn["mrr_rms"])
    cells = {key: _mean_std(v)[0] for key, v in buckets.items()}
    cells_n = {key: _mean_std(v)[2] for key, v in buckets.items()}
    return {
        "cells": cells, "cells_n": cells_n, "n_units": n_units, "n_units_failed": n_failed,
        "enc_unavailable": dict(enc_unavailable), "joint_unavailable": joint_unavailable,
        "meta": meta_all, "strat": dict(strat_all), "pop": dict(pop_all),
        "synth_rank_signal": {"hits10_rms": _mean_std(srs_h)[0], "mrr_rms": _mean_std(srs_m)[0]},
        "synth_rank_null": {"hits10_rms": _mean_std(srn_h)[0], "mrr_rms": _mean_std(srn_m)[0]},
    }


def _cell(cells, key):
    return cells.get(key, float("nan"))


def _slot_rms(cells, cn, rel, enc, slot, metric, ev="inductive"):
    ri = _cell(cells, f"{cn}|{rel}|{enc}|{slot}|REAL|{ev}|filt|{metric}")
    si = _cell(cells, f"{cn}|{rel}|{enc}|{slot}|SHUFFLED|{ev}|filt|{metric}")
    if ri != ri or si != si:
        return float("nan")
    return ri - si


def compute_verdict(agg: Dict, arms_differ_ok: bool, bind_rt: float) -> Tuple[str, str, Dict]:
    cells = agg["cells"]; meta = agg["meta"]
    srs = agg["synth_rank_signal"]; srn = agg["synth_rank_null"]
    good_units = agg["n_units"] - agg["n_units_failed"]

    # discriminator-fires: clean map gives large rank rms; null gives ~0
    fires_signal = (srs["hits10_rms"] >= SYNTH_SIGNAL_HITS10_RMS_MIN
                    and srs["mrr_rms"] >= SYNTH_SIGNAL_MRR_RMS_MIN)
    null_clean = (abs(srn["hits10_rms"]) < SYNTH_NULL_RMS_MAX and abs(srn["mrr_rms"]) < SYNTH_NULL_RMS_MAX)
    discriminator_fires = fires_signal and null_clean

    V300_PLUS = {"V300", "V1000"}

    # per (config, rel, enc): best-of-{FROZEN,JOINT} filtered rms, and whether a SINGLE slot clears both
    records = []
    for cfg in CONFIGS:
        cn = cfg["name"]
        for rel in cfg["rels"]:
            is_sem = rel in RELATIONS_SEM
            for enc in cfg["encs"]:
                ch = float(meta.get(f"{cn}|{rel}|{enc}", {}).get("chance", float("nan")))
                slot_rms = {}
                for slot in SCORER_SLOTS:
                    slot_rms[slot] = {m: _slot_rms(cells, cn, rel, enc, slot, m) for m in METRIC_KEYS}
                # best-of-{FROZEN,JOINT} per metric
                def _best(m):
                    vals = [slot_rms[s][m] for s in HP_SLOTS if slot_rms[s][m] == slot_rms[s][m]]
                    return max(vals) if vals else float("nan")
                best_h10 = _best("hits10"); best_mrr = _best("mrr")
                # single-slot-clears-both (stricter; no cherry-pick across metrics)
                slot_clears_both = any(
                    slot_rms[s]["hits10"] == slot_rms[s]["hits10"]
                    and slot_rms[s]["mrr"] == slot_rms[s]["mrr"]
                    and slot_rms[s]["hits10"] >= HP_HITS10_RMS_MIN
                    and slot_rms[s]["mrr"] >= HP_MRR_RMS_MIN
                    for s in HP_SLOTS)
                # SHUFFLED filtered Hits@10 (saturation guard)
                shuf_h10 = _cell(cells, f"{cn}|{rel}|{enc}|FROZEN|SHUFFLED|inductive|filt|hits10")
                if all(slot_rms[s]["hits10"] != slot_rms[s]["hits10"] for s in SCORER_SLOTS):
                    continue
                records.append({
                    "config": cn, "V": cfg["V"], "M": cfg["M"], "rel": rel, "enc": enc,
                    "is_sem": is_sem, "is_neg_watchdog": rel in RELATIONS_NEG, "chance": ch,
                    "slot_rms": {s: {m: (round(slot_rms[s][m], 4) if slot_rms[s][m] == slot_rms[s][m] else None)
                                     for m in METRIC_KEYS} for s in SCORER_SLOTS},
                    "best_hits10_rms": (round(best_h10, 4) if best_h10 == best_h10 else None),
                    "best_mrr_rms": (round(best_mrr, 4) if best_mrr == best_mrr else None),
                    "slot_clears_both": slot_clears_both,
                    "shuf_hits10_filt": (round(float(shuf_h10), 4) if shuf_h10 == shuf_h10 else None),
                })

    # V-scan curve (semantic cells) -- filtered Hits@10 + MRR rms, best-of-{FROZEN,JOINT}
    def _vcurve():
        out = {}
        for vname in ["V100", "V300", "V1000"]:
            rows = [r for r in records if r["config"] == vname and r["is_sem"]]
            out[vname] = {f"{r['rel']}|{r['enc']}": {
                "best_hits10_rms": r["best_hits10_rms"], "best_mrr_rms": r["best_mrr_rms"],
                "FROZEN_hits10_rms": r["slot_rms"]["FROZEN"]["hits10"],
                "JOINT_hits10_rms": r["slot_rms"]["JOINT"]["hits10"],
                "KNN_hits10_rms": r["slot_rms"]["KNN"]["hits10"],
                "clears_both": r["slot_clears_both"]} for r in rows}
        return out
    vcurve = _vcurve()

    # HARD_PASS expansion: single-slot-clears-both across >=2 semantic relations AND >=2 encoders at V>=300
    wins = [r for r in records if r["is_sem"] and r["config"] in V300_PLUS and r["slot_clears_both"]]
    win_rels = set(r["rel"] for r in wins)
    win_encs = set(r["enc"] for r in wins)
    expansion_met = len(win_rels) >= 2 and len(win_encs) >= 2

    # HARD_FAIL: max over semantic (rel x enc) at V>=300 of best filtered Hits@10 rms < HF ceiling
    v300_sem = [r for r in records if r["is_sem"] and r["config"] in V300_PLUS]
    best_h10_v300 = max((r["best_hits10_rms"] for r in v300_sem
                         if r["best_hits10_rms"] is not None), default=float("nan"))
    best_mrr_v300 = max((r["best_mrr_rms"] for r in v300_sem
                         if r["best_mrr_rms"] is not None), default=float("nan"))

    # DerivedFrom watchdog rank spread (contrast diagnostic)
    watchdog = {}
    for r in records:
        if r["is_neg_watchdog"]:
            watchdog[f"{r['config']}|{r['enc']}"] = {
                "FROZEN_REAL_hits1": _cell(cells, f"{r['config']}|{r['rel']}|{r['enc']}|FROZEN|REAL|inductive|filt|hits1"),
                "FROZEN_REAL_hits20": _cell(cells, f"{r['config']}|{r['rel']}|{r['enc']}|FROZEN|REAL|inductive|filt|hits20")}

    diag = {
        "bind_roundtrip": bind_rt, "arms_differ_ok": arms_differ_ok,
        "good_units": good_units, "expected_n_units": EXPECTED_N_UNITS,
        "synth_rank_signal": srs, "synth_rank_null": srn,
        "discriminator_fires_signal": fires_signal, "discriminator_null_clean": null_clean,
        "discriminator_fires": discriminator_fires,
        "v_scan_curve_filtered_rank_rms": vcurve, "records": records,
        "wins": wins, "win_rels": sorted(win_rels), "win_encs": sorted(win_encs),
        "expansion_criterion_met": expansion_met,
        "best_filtered_hits10_rms_at_V300plus": (round(best_h10_v300, 4) if best_h10_v300 == best_h10_v300 else None),
        "best_filtered_mrr_rms_at_V300plus": (round(best_mrr_v300, 4) if best_mrr_v300 == best_mrr_v300 else None),
        "derivedfrom_watchdog_rank_spread": watchdog,
        "fanout_strata": agg["strat"], "popularity_floor": agg["pop"],
        "enc_unavailable": agg["enc_unavailable"], "joint_unavailable": agg["joint_unavailable"],
        "device": _DEVICE,
    }

    # ---- global gates ----
    expected = EXPECTED_N_UNITS
    if good_units < expected:
        gsbc_missing = agg["enc_unavailable"].get("gsbc", 0)
        if not (gsbc_missing > 0 and (good_units + gsbc_missing) >= expected):
            return ("HARD_FAIL",
                    f"HARD_FAIL_CARDINALITY_BREACH_META_RULE_H: good_units={good_units} < "
                    f"expected={expected} (not explained by gsbc-cache-missing).", diag)
    if not arms_differ_ok:
        return ("HARD_FAIL", "META_RULE_AF_VIOLATION: arm score-matrices bit-identical; arm-impl bug.", diag)
    if not (bind_rt >= BIND_ROUNDTRIP_MIN):
        return ("HARD_FAIL", f"SANITY_RAIL_BIND: bind-roundtrip={bind_rt:.3f} < {BIND_ROUNDTRIP_MIN}.", diag)

    summ = (f"dev={_DEVICE} discrim[signal={fires_signal}(H10rms={srs['hits10_rms']:+.2f},"
            f"MRRrms={srs['mrr_rms']:+.2f}),null_clean={null_clean}(H10rms={srn['hits10_rms']:+.2f})] | "
            f"V300+ best_filt_Hits@10_rms={diag['best_filtered_hits10_rms_at_V300plus']} "
            f"best_filt_MRR_rms={diag['best_filtered_mrr_rms_at_V300plus']}")

    if not discriminator_fires:
        return ("MIDDLE_BAND",
                f"MIDDLE_BAND_VACUOUS_DISCRIMINATOR: filtered-rank machinery did NOT pass the synthetic "
                f"controls (signal_fires={fires_signal}, null_clean={null_clean}); real-data rank rms "
                f"uninterpretable until the metric provably fires on a clean map AND reports ~0 on noise. "
                f"{summ}", diag)

    if expansion_met:
        return ("HARD_PASS",
                f"HARD_PASS_RANK_REFRAME_RECOVERS: under FILTERED Hits@k/MRR (Bordes 2013), best-of-"
                f"{{FROZEN,JOINT}} inductive real_minus_shuf clears Hits@10>={HP_HITS10_RMS_MIN} AND "
                f"MRR>={HP_MRR_RMS_MIN} (same slot) at V>=300 spanning relations={sorted(win_rels)} x "
                f"encoders={sorted(win_encs)} (wins={[(r['config'],r['rel'],r['enc'],r['best_hits10_rms'],r['best_mrr_rms']) for r in wins]}); "
                f"the substrate's relational transfer was being graded by the wrong (exact-match) yardstick. "
                f"{summ}", diag)

    if best_h10_v300 == best_h10_v300 and best_h10_v300 < HF_HITS10_RMS_MAX:
        return ("HARD_FAIL",
                f"HARD_FAIL_RANK_REFRAME_DOES_NOT_RESCUE: even the generous filtered Hits@10 rank reframe "
                f"fails to recover signal at V>=300 (best filtered Hits@10 rms={diag['best_filtered_hits10_rms_at_V300plus']} "
                f"< {HF_HITS10_RMS_MAX}) while discriminators fired -> thin generic-sentence content cannot "
                f"resolve novel-entity relational identity at realistic vocab under ANY scoring convention; "
                f"the only remaining lever is structurally richer per-entity content. {summ}", diag)

    return ("MIDDLE_BAND",
            f"MIDDLE_BAND_PARTIAL_RANK_RECOVERY: the filtered rank reframe recovers REAL signal (best "
            f"filtered Hits@10 rms={diag['best_filtered_hits10_rms_at_V300plus']}, best MRR rms="
            f"{diag['best_filtered_mrr_rms_at_V300plus']} at V>=300) -- converting the exact-match HARD_FAIL "
            f"into a genuine partial win -- but does not clear Hits@10>={HP_HITS10_RMS_MIN} AND MRR>="
            f"{HP_MRR_RMS_MIN} (same slot) across >=2 rels x >=2 encoders (win_rels={sorted(win_rels)}, "
            f"win_encs={sorted(win_encs)}). Content-resolution (not scoring convention) is still the limiting "
            f"factor; pair with a structured-content iteration next. This partial-recovery IS the finding. {summ}",
            diag)


# ============================================================================
# Formula self-tests (import time, fast < 180s) -- filtered-rank arithmetic is the load-bearing new code
# ============================================================================
def _test_filtered_ranks():
    scores = np.array([
        [0.9, 0.5, 0.8, 0.1, 0.7],    # row0 true=2(0.8); filter {0}(0.9)
        [0.2, 0.9, 0.3, 0.85, 0.4],   # row1 true=0(0.2); no filter
        [0.5, 0.6, 0.55, 0.4, 0.65],  # row2 true=1(0.6); filter {4}(0.65)
    ], dtype=np.float32)
    y = np.array([2, 0, 1], dtype=np.int64)
    fm = np.zeros((3, 5), dtype=bool); fm[0, 0] = True; fm[2, 4] = True
    rf = filtered_ranks(scores, y, fm)
    # row0: >0.8 & not{0,2}: none -> 1 ; row1: >0.2: {1,2,3,4} -> 5 ; row2: >0.6 & not{4,1}: none -> 1
    assert list(rf) == [1, 5, 1], f"filtered ranks {rf.tolist()} != [1,5,1]"
    rr = filtered_ranks(scores, y, np.zeros((3, 5), dtype=bool))
    # row0 raw: >0.8:{0} -> 2 ; row1: 5 ; row2 raw: >0.6:{4} -> 2
    assert list(rr) == [2, 5, 2], f"raw ranks {rr.tolist()} != [2,5,2]"
    assert np.all(rf <= rr), "filter invariant: filtered rank must be <= raw rank"
    m = rank_metrics(rf)
    assert abs(m["hits1"] - 2.0 / 3.0) < 1e-9, f"hits1 {m['hits1']}"
    assert abs(m["hits5"] - 1.0) < 1e-9, f"hits5 {m['hits5']}"
    assert abs(m["mrr"] - (1.0 + 0.2 + 1.0) / 3.0) < 1e-9, f"mrr {m['mrr']}"
    # ties: identical scores -> true object ranks above equal-scored others (optimistic, consistent)
    st = np.array([[0.5, 0.5, 0.5]], dtype=np.float32)
    rt = filtered_ranks(st, np.array([0], dtype=np.int64), np.zeros((1, 3), dtype=bool))
    assert rt[0] == 1, f"tie rank {rt[0]} (expected 1; no score strictly greater)"


def _formula_selftests() -> float:
    rng = np.random.RandomState(123)
    n = 512
    a = np.exp(1j * rng.uniform(-np.pi, np.pi, n)).astype(np.complex64)
    b = np.exp(1j * rng.uniform(-np.pi, np.pi, n)).astype(np.complex64)
    rt = cos_c(unbind(bind(a, b), a), b)
    assert rt >= 0.90, f"selftest1 bind-roundtrip cos={rt}"

    _test_filtered_ranks()

    # k-NN reference: a clean-map regime -> KNN REAL Hits@10 > SHUFFLED (representation carries signal)
    d, V, M, T = SCM_D, SCM_V, SCM_M, SCM_TEST
    Fs, yA, Fc, yC, _ = _gen_linear_content(999, d, V, M, T)
    fm = np.zeros((T, V), dtype=bool)
    ish = np.random.RandomState(3).permutation(M)
    kr = rank_metrics(filtered_ranks(knn_scores(Fc, Fs, yA, V, 15), yC, fm))
    ks = rank_metrics(filtered_ranks(knn_scores(Fc, Fs, yA[ish], V, 15), yC, fm))
    assert kr["hits10"] > ks["hits10"] + 0.10, \
        f"selftest3 kNN REAL Hits@10 {kr['hits10']:.3f} !> SHUFFLED {ks['hits10']:.3f}+0.10 (rep signal)"

    # FROZEN filtered-rank discriminator fires on clean linear map; null control ~0
    srs0 = synth_rank_signal(0)
    assert srs0["hits10_rms"] >= SYNTH_SIGNAL_HITS10_RMS_MIN, \
        f"selftest4 signal Hits@10 rms={srs0['hits10_rms']:+.3f} < {SYNTH_SIGNAL_HITS10_RMS_MIN}"
    assert srs0["mrr_rms"] >= SYNTH_SIGNAL_MRR_RMS_MIN, \
        f"selftest4b signal MRR rms={srs0['mrr_rms']:+.3f} < {SYNTH_SIGNAL_MRR_RMS_MIN}"
    srn0 = synth_rank_null(0)
    assert abs(srn0["hits10_rms"]) < SYNTH_NULL_RMS_MAX, \
        f"selftest5 null Hits@10 rms={srn0['hits10_rms']:+.3f} not < {SYNTH_NULL_RMS_MAX}"

    # arms-differ hash gate (FROZEN/JOINT REAL vs SHUFFLED score matrices differ)
    ad_ok, _ = arms_differ_check(0)
    assert ad_ok, "selftest6 arms_differ_check failed (score matrices identical)"

    print(f"[formula_selftest] bind_rt={rt:.3f} filt_rank_arith=PASS "
          f"kNN_signal(H10 R{kr['hits10']:.2f}>S{ks['hits10']:.2f}) "
          f"SIGNAL(H10rms{srs0['hits10_rms']:+.2f},MRRrms{srs0['mrr_rms']:+.2f}) "
          f"NULL(H10rms{srn0['hits10_rms']:+.2f}) torch_ok={_TORCH_OK} device={_DEVICE} "
          f"bge_ok={_BGE.ok} gsbc_ok={_GSBC.ok} PASS", flush=True)
    return rt


_BIND_RT = _formula_selftests()
# reachability (THEORETICAL; no CRLB noise-floor for rank transfer). At V=1000 with k=10 filtered,
# random-baseline Hits@10 ~ 10/1000 = 0.01; rms bands (0.10/0.20) far above chance and far below
# saturation. Reachable both directions.
assert HF_HITS10_RMS_MAX < HP_HITS10_RMS_MIN < 0.95, "HP/HF bands must be ordered and below saturation"


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
              f"failure_class; bge_semantic axis still valid.", flush=True)

    run_config = {"N": N_DIM, "run_mode": RUN_MODE, "anchor": ANCHOR_NAME}
    done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
    print(f"[ckpt] {len(done)}/{len(SEEDS)} done; running {remaining}", flush=True)

    for seed in remaining:
        r = run_seed(seed, out_dir)
        write_partial(out_dir, seed, r)
        print(f"[{ANCHOR_NAME}] seed={seed} done ({r['elapsed_s']:.1f}s) fatal={r['fatal']}", flush=True)

    per_seed = aggregate_partials(out_dir, SEEDS, run_config=run_config)
    agg = aggregate(per_seed)
    ad_ok, ad_digests = arms_differ_check(SEEDS[0])
    verdict, verdict_msg, diag = compute_verdict(agg, ad_ok, _BIND_RT)

    elapsed = time.time() - t_start
    summary = (f"{verdict}: best_filt_Hits@10_rms@V300+={diag.get('best_filtered_hits10_rms_at_V300plus')} "
               f"best_filt_MRR_rms@V300+={diag.get('best_filtered_mrr_rms_at_V300plus')} "
               f"expansion_met={diag.get('expansion_criterion_met')} "
               f"discrim_fires={diag.get('discriminator_fires')}")
    metrics = {
        "anchor": ANCHOR_NAME, "anchor_name": ANCHOR_NAME, "run_mode": RUN_MODE,
        "N": N_DIM, "N_DIM": N_DIM, "device": _DEVICE, "torch_ok": _TORCH_OK,
        "relations_semantic": RELATIONS_SEM, "relations_neg_watchdog": RELATIONS_NEG,
        "content_encodings": CONTENT_ENCODINGS, "arms": ARMS, "eval_modes": EVAL_MODES,
        "scorer_slots": SCORER_SLOTS, "hp_slots": HP_SLOTS, "hits_ks": HITS_KS, "knn_k": _knn_k(),
        "config_grid": [{"name": c["name"], "V": c["V"], "M": c["M"], "rels": c["rels"],
                         "encs": c["encs"]} for c in CONFIGS],
        "frozen_hp": {"df": FROZEN_DF, "steps": FROZEN_STEPS, "lr": SCORER_LR, "tau": SCORER_TAU,
                      "l2": SCORER_L2},
        "joint_hp": {"h": JOINT_H, "df": JOINT_DF, "dropout": JOINT_DROPOUT, "lr": JOINT_LR,
                     "wd": JOINT_WD, "steps": JOINT_STEPS, "tau": JOINT_TAU},
        "n_seeds": len(per_seed), "seeds": [int(s) for s in per_seed.keys()],
        "expected_n_units": EXPECTED_N_UNITS, "n_units_counted": agg["n_units"],
        "n_units_failed": agg["n_units_failed"],
        "cardinality_ok": (agg["n_units"] - agg["n_units_failed"]) >= EXPECTED_N_UNITS
        or agg["enc_unavailable"].get("gsbc", 0) > 0,
        "arms_differ_verified": ad_ok, "arms_differ_digests": ad_digests,
        "bind_roundtrip": _BIND_RT,
        "synth_rank_signal": agg["synth_rank_signal"], "synth_rank_null": agg["synth_rank_null"],
        "discriminator_fires_signal": diag.get("discriminator_fires_signal"),
        "discriminator_null_clean": diag.get("discriminator_null_clean"),
        "discriminator_fires": diag.get("discriminator_fires"),
        "v_scan_curve_filtered_rank_rms": diag.get("v_scan_curve_filtered_rank_rms"),
        "records": diag.get("records"),
        "wins": diag.get("wins"), "win_rels": diag.get("win_rels"), "win_encs": diag.get("win_encs"),
        "expansion_criterion_met": diag.get("expansion_criterion_met"),
        "best_filtered_hits10_rms_at_V300plus": diag.get("best_filtered_hits10_rms_at_V300plus"),
        "best_filtered_mrr_rms_at_V300plus": diag.get("best_filtered_mrr_rms_at_V300plus"),
        "derivedfrom_watchdog_rank_spread": diag.get("derivedfrom_watchdog_rank_spread"),
        "fanout_strata": diag.get("fanout_strata"), "popularity_floor": diag.get("popularity_floor"),
        "enc_unavailable": agg["enc_unavailable"], "joint_unavailable": agg["joint_unavailable"],
        "meta_per_relenc": agg["meta"],
        "hp_scope": {"best_of_FROZEN_JOINT_REAL_inductive_FILTERED_SEMANTIC_at_V>=300":
                     ["HARD_PASS", "HARD_FAIL", "MIDDLE_BAND"],
                     "KNN": ["representation_signal_reference_NOT_HP"],
                     "DerivedFrom": ["surface_morphological_watchdog_contrast_NOT_HP"],
                     "SHUFFLED": ["popularity_marginal_control"], "POP": ["C_independent_floor"],
                     "raw_metrics": ["reported_not_gating"]},
        "bands": {"HP_HITS10_RMS_MIN": HP_HITS10_RMS_MIN, "HP_MRR_RMS_MIN": HP_MRR_RMS_MIN,
                  "HF_HITS10_RMS_MAX": HF_HITS10_RMS_MAX,
                  "SYNTH_SIGNAL_HITS10_RMS_MIN": SYNTH_SIGNAL_HITS10_RMS_MIN,
                  "SYNTH_SIGNAL_MRR_RMS_MIN": SYNTH_SIGNAL_MRR_RMS_MIN,
                  "SYNTH_NULL_RMS_MAX": SYNTH_NULL_RMS_MAX, "BASE_SAT_HI": BASE_SAT_HI},
        "cells_aggregate": agg["cells"], "cells_n": agg["cells_n"],
        "gate_diagnostics": {k: v for k, v in diag.items() if k not in ("records",)},
        "filtered_protocol": "bordes_2013_filtered_hits_at_k_mrr_exclude_other_true_objects_per_subject",
        "corpus_provenance": "conceptnet5_en_100k_real_triples",
        "encoding_provenance": {
            "bge_semantic": "BAAI/bge-small-en-v1.5_bounded_cache_centered",
            "gsbc": "bge-large-en-v1.5->GSBC_EXPAND2X_student_sparse_code_cache"},
        "allow_synthetic": False, "n_generative_llm_calls": 0,
        "metrics_source": "measured_filtered_rank_reframe_frozen_joint_knn_scorers",
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
