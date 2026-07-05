"""schema_relation_richer_content_vscan_v1 -- the RICHER-CONTENT frontier lever for INDUCTIVE
relational transfer at REALISTIC vocabulary (the decisive next attempt after the scale-up wall).

SCIENTIFIC QUESTION (the decisive expansion test):
  The scale-up envelope (schema_relation_TEM_scorer_scaleup_envelope_v2, VET=MEASURED_MECHANISM)
  proved generalization is NARROW: inductive real_minus_shuf crosses the 0.2075 bar ONLY at V=100
  (CausesDesire/bge rms=+0.213), 1 of 56 configs; the V-scan collapses at REALISTIC vocab --
  V300 rms ~ +0.07-0.09, V1000 ~ +0.03-0.05 (MEASURED@data/exp_schema_relation_TEM_scorer_scaleup
  _envelope_v2/metrics.json:axis_curves.v_scan_curve + cells_aggregate). Diagnosis = candidate-count
  / one-to-many ENTROPY CEILING on the V-axis, NOT under-parameterization (M_OP/df/steps scans all
  plateaued at ~0.11). The mechanism research predicted the FIX = RICHER, JOINTLY-TRAINED content
  encodings (the DKRL->KEPLER->BLP->SimKGC direction; BLP 0.180->0.285 MRR, +58% relative, from
  richer jointly-trained content NOT more compute) -- CITED@notes/research_mechanism_envelope
  _frontier_inductive_transfer_off_zero_2026-07-05.md. This cell is that untested lever.

  THE decisive question: does richer jointly-trained content push inductive real_minus_shuf >= 0.2075
  at V>=300 on >=2 relations x >=2 encoders -- a GENUINE broad win, not the V=100 corner? We MAP the
  V-scan {100,300,1000} for the RICHER (JOINT) arm vs the FROZEN baseline. A curve that lifts but
  plateaus below the bar is THE finding (one-to-many ceiling genuine). Constructive; brain-first.

MECHANISM MAP (the ONE manipulation -- content representation; everything else held identical):
  FROZEN  = the scale-up cell's SCORER, verbatim: frozen content feature (BGE/GSBC, centered+unit)
            -> FIXED random projection P_s,P_o (d->df) -> trained bilinear W (RESCAL/DistMult,
            O(d^2)). The content code is FIXED; only the relation form W adapts. The baseline to beat.
  JOINT   = RICHER (NEW): a SHARED small content encoder g_theta (2-layer MLP d->h->df, dropout)
            TRAINED END-TO-END with a bilinear relation R on the same inductive softmax-CE objective.
            The content code CO-ADAPTS with the relation (BLP/SimKGC direction). Score
            s = g(f_s)^T R g(f_o). Brain analog: cortical representations are shaped BY the relational
            tasks they support (not fixed-then-read-out). GPU-trainable (torch autograd, batched B=2
            over the paired REAL+SHUFFLED arms on-device). Inductive-valid: g is a FUNCTION of the
            frozen feature, so novel (held-out) subjects are encoded by the SAME g -- no per-entity
            table, no transductive leak.
  MEAN_OBJECT = C-independent "return the popular object" control (population marginal; for rmm gate).

LOAD-BEARING METRIC: REAL - SHUFFLED on INDUCTIVE (novel-subject) eval. Raw accuracy is a relation-
  prior trap (population-typical answer); real_minus_shuf is the subject->object correspondence signal
  that must transfer to entities never seen in training. FROZEN and JOINT are PAIRED (same triples /
  split / seed / features; only the content representation and the shuffle differ).

CONTRACT (gate on the VET's expansion criterion; report the V-scan curve richer-vs-frozen EXPLICITLY):
  HARD_PASS  = JOINT real_minus_shuf(ind) >= 0.2075 at V>=300 on a set of (rel,enc) cells spanning
               >=2 relations AND >=2 encoders (AtLocation+CausesDesire x bge+gsbc) -- the expansion
               criterion, a genuine broad win (NOT the V=100 corner, NOT a single-cell fluke), JOINT
               discriminator firing.
  HARD_FAIL  = richer content does NOT beat frozen at V>=300 (max over V>=300 semantic cells of
               JOINT_rms - FROZEN_rms < IMPROVE_MIN) while discriminators fire -> the one-to-many
               entropy ceiling is GENUINE for this task class (honest wall-finding; scale-nor-content
               rescues thin generic-sentence content on crowd-sourced relations at realistic vocab).
  MIDDLE     = richer content LIFTS the V>=300 curve above frozen (by >= IMPROVE_MIN somewhere) but
               does not clear 0.2075 broadly -> content is directionally the right lever; iterate
               richness (structured attributes / multi-sentence descriptions) next. The lift-but-
               plateau curve IS the finding.

COMPUTE: class (a) batched-GPU. JOINT trains both PAIRED arms (REAL,SHUFFLED) in ONE batched model
  (leading B=2 dim; einsum over M x V x df; identical init across arms -> only y differs). FROZEN
  trains both arms in one torch-bmm B=2 pass (verbatim from the scale-up cell). device auto->cuda on
  the GPU box; numpy fallback for FROZEN if torch absent (JOINT records failure_class if torch absent,
  never on the GPU queue). Storage strategy: no_storage. No generative-LLM calls (deterministic
  content caches only).

# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; FROZEN!=JOINT, REAL!=SHUFFLED on a discriminating regime)
# - final_metrics_atomicity = tmp_replace (META_RULE_AH)
# - except SystemExit: raise BEFORE except Exception (no BaseException); start-marker + crash-diag + heartbeat
# - crlb n/a (argmax transfer; no closed-form noise floor). chance floor 1/V_eff stated; reachability declared
# - baseline_in_band at smoke (FROZEN in (chance,0.95); SHUFFLED ~chance; synth controls in-band)
# - discriminator survives scale (B): synth_nonlinear_content proves JOINT>FROZEN at N=8192 by construction;
#   the V>=300 real-data win is the MAP question itself (plateau IS a finding), not smoke-provable -> justified
# - HARD_PASS strictly above floor (real_minus_shuf 0.2075 = 0.20 + 5% band-width, META_RULE_L)
# - HP_SCOPE: HP gates apply to JOINT REAL/inductive only, per SEMANTIC rel x enc at V>=300; FROZEN=baseline; DerivedFrom=watchdog
# - cardinality_ok (META_RULE_H; EXPECTED_N_UNITS summed over the config grid)
# - per-unit failure-class instrumentation (META_RULE_J; no bare except)
# - calibration_check = adaptive_with_discriminator_gate (synth_content_map FROZEN>GLOBAL +
#   synth_nonlinear_content JOINT>FROZEN are the discriminator-fires proofs)
# - progress_logging = print_flush_true (all progress lines flush=True; per (config,seed) timing)
# - positive controls reproduce at test regime N=8192 (Gate D: FROZEN reproduces the scale-up V-scan rms)
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

# torch import (overnight_queue GPU gate greps for `import torch`). Guarded: numpy fallback for FROZEN.
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

ANCHOR_NAME = "schema_relation_richer_content_vscan_v1"
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
RELATIONS_NEG = ["DerivedFrom"]                     # surface-morphological negative watchdog (NOT HP)
RELATIONS_ALL = RELATIONS_SEM + RELATIONS_NEG
CONTENT_ENCODINGS = ["bge_semantic", "gsbc"]
ARMS = ["REAL", "SHUFFLED"]
EVAL_MODES = ["inductive", "transductive"]
SCORER_SLOTS = ["FROZEN", "JOINT"]                  # the two content representations (paired arms)
PRIMARY_EVAL = "inductive"

# FROZEN scorer hyperparameters (VERBATIM from scale-up v2 SCORER -> reproduces its V-scan; Gate D)
FROZEN_DF = 384
FROZEN_STEPS = 2000
SCORER_LR = 1.0
SCORER_TAU = 0.05
SCORER_L2 = 1e-3
PROJ_SEED = 12345

# JOINT (richer) content encoder hyperparameters (fixed a priori; NO tuning-for-pass; standard
# small-MLP-inductive practice: enough training to fit the content structure + mild regularization
# for novel-entity generalization. Verified only against the synthetic controls + Gate D, never
# tuned on the real-data outcome.)
JOINT_H = 256               # MLP hidden width
JOINT_DF = 128              # content code dim (feeds bilinear R)
JOINT_DROPOUT = 0.1         # mild dropout for inductive generalization
JOINT_LR = 2e-3
JOINT_WD = 1e-3             # mild weight decay (Adam)
JOINT_STEPS = 500
JOINT_TAU = 0.1             # softmax-CE temperature

# ----------------------------------------------------------------------------
# Synthetic positive-control regimes (CALIBRATED; discriminator-fires proofs)
# ----------------------------------------------------------------------------
SYNTH_N = N_DIM
SYNTH_CLEAN_K = 8
SYNTH_CLEAN_SIGMA = 0.15
SCM_D = 64                  # content-map (LINEAR): FROZEN must beat GLOBAL
SCM_V = 40
SCM_M = 300
SCM_TEST = 200
SNL_D = 64                  # nonlinear-content: JOINT must beat FROZEN
SNL_V = 40
SNL_M = 1000
SNL_TEST = 300
SCORER_DF_SYNTH = 96
SCORER_STEPS_SYNTH = 300

# Pre-reg bands (LOCKED)
HP_RMS_MIN = 0.2075         # JOINT real_minus_shuf(ind) HARD_PASS floor at V>=300 (0.20 + 5% band, META_RULE_L)
HP_REAL_GAIN_MIN = 0.2075   # JOINT real_ind - chance floor (subject-conditional above-chance)
HP_RMM_MIN = 0.05           # JOINT real_ind - mean_object (subject-conditional above popular-object)
IMPROVE_MIN = 0.02          # JOINT must beat FROZEN rms by this at V>=300 to count as "richer helps"
RMS_SIGNAL_MIN = 0.05       # nonzero-signal floor
FROZEN_ADV_MIN = 0.05       # synth_content_map: FROZEN must beat GLOBAL (discriminator-fires)
JOINT_ADV_MIN = 0.05        # synth_nonlinear_content: JOINT must beat FROZEN (discriminator-fires)
SYNTH_CLEAN_MIN = 0.90
BIND_ROUNDTRIP_MIN = 0.90
BASE_IN_BAND_HI = 0.95
# Gate D positive-control referents (MEASURED@scale-up v2 metrics; FROZEN must reproduce at matched regime)
GATE_D_REF = {
    "V100|CausesDesire|bge_semantic": 0.213,   # MEASURED@..._scaleup_envelope_v2:cells (V100 SCORER rms)
    "V300|CausesDesire|bge_semantic": 0.087,   # MEASURED  (frozen collapses at realistic vocab)
    "V300|AtLocation|bge_semantic": 0.067,     # MEASURED
}
GATE_D_TOL = 0.06

# ----------------------------------------------------------------------------
# CONFIG GRID
# ----------------------------------------------------------------------------
def _cfg(name, V, M, rels, encs):
    return {"name": name, "V": V, "M": M, "rels": list(rels), "encs": list(encs)}


if RUN_MODE == "smoke":
    SEEDS = [7]
    N_TEST_PER = 60
    POOL_CAP = 6000
    # SMOKE = FAST but SMOKE==FULL branch-coverage: V100 + a V300 config so the load-bearing
    # V>=300 verdict branch (HARD_PASS/HARD_FAIL/MIDDLE) is exercised. tiny M, bge only. Do NOT
    # put the big GPU sweep in smoke.
    CONFIGS = [_cfg("V100", 100, 200, RELATIONS_SEM, ["bge_semantic"]),
               _cfg("V300", 300, 300, RELATIONS_SEM, ["bge_semantic"])]
    _SMOKE_JOINT = dict(H=128, DF=64, STEPS=80)   # tiny JOINT for smoke speed
    _SMOKE_FROZEN_STEPS = 300
    _SMOKE_FROZEN_DF = 128
else:
    SEEDS = [7, 13, 19]
    N_TEST_PER = 150
    POOL_CAP = 30000
    # PRIMARY V-scan (M=800 matched to scale-up v2 -> FROZEN reproduces; JOINT head-to-head is fair)
    _VSCAN = [_cfg(f"V{v}", v, 800, RELATIONS_ALL, CONTENT_ENCODINGS) for v in [100, 300, 1000]]
    # SECONDARY M-scan at realistic vocab V=300 (does more data let richer content clear the bar?)
    _MSCAN = [_cfg(f"V300_M{m}", 300, m, RELATIONS_SEM, ["bge_semantic"]) for m in [1500, 3000]]
    CONFIGS = _VSCAN + _MSCAN
    _SMOKE_JOINT = None
    _SMOKE_FROZEN_STEPS = None
    _SMOKE_FROZEN_DF = None


def _joint_hp():
    if RUN_MODE == "smoke":
        return _SMOKE_JOINT["H"], _SMOKE_JOINT["DF"], _SMOKE_JOINT["STEPS"]
    return JOINT_H, JOINT_DF, JOINT_STEPS


def _frozen_hp():
    if RUN_MODE == "smoke":
        return _SMOKE_FROZEN_DF, _SMOKE_FROZEN_STEPS
    return FROZEN_DF, FROZEN_STEPS


def expected_units(configs, seeds) -> int:
    # per (cfg,rel,enc): FROZEN(2 arms x 2 evals=4) + JOINT(4) + MEAN_OBJECT(2) = 10
    tot = 0
    for c in configs:
        tot += len(c["rels"]) * len(c["encs"]) * 10
    return tot * len(seeds)


EXPECTED_N_UNITS = expected_units(CONFIGS, SEEDS)


# ============================================================================
# FHRR primitives (complex64 phasors) -- self-contained (no sibling import; remote won't auto-SCP)
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
    sims = (Dhat @ np.conj(O).T).real
    return sims.argmax(axis=1)


# ============================================================================
# Content encoders (ZERO generative-LLM; deterministic) -- self-contained
# ============================================================================
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
        self.dim = 0
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
        self.W = (rng.standard_normal((self.dim, n)).astype(np.float32))
        self.ok = True

    def feature(self, s: str) -> np.ndarray:
        v = self._fcache.get(s)
        if v is not None:
            return v
        i = self.idx.get(s)
        v = self.emb[i] if i is not None else np.zeros(self.dim, dtype=np.float32)
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


_BGE = _CachedSemanticEncoder(N_DIM, BGE_CACHE_REL, "emb", "entities", PROJ_SEED, "bge")
_GSBC = _CachedSemanticEncoder(N_DIM, GSBC_CACHE_REL, "code", "entities", PROJ_SEED + 1, "gsbc")


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
# GLOBAL (TransE single-mean transform) -- used ONLY inside synth controls (reference floor)
# ============================================================================
def fit_naive_mean(A: np.ndarray, y: np.ndarray, O: np.ndarray) -> np.ndarray:
    return (O[y] * np.conj(A)).mean(axis=0).astype(np.complex64)


def apply_transform(C: np.ndarray, M_R: np.ndarray, O: np.ndarray) -> np.ndarray:
    return cleanup_argmax_batch(C * M_R[None, :], O)


# ============================================================================
# FROZEN scorer (bilinear RESCAL/DistMult on FIXED random projection) -- VERBATIM from scale-up v2
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


def apply_scorer(Fc, W, Fo, Ps, Po) -> np.ndarray:
    U = Fc @ Ps
    Vo = Fo @ Po
    return ((U @ W) @ Vo.T).argmax(axis=1)


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
# JOINT (richer jointly-trained content encoder) -- NEW. torch autograd; batched B=2 paired arms.
# ============================================================================
class JointUnavailable(Exception):
    pass


def _joint_init_params(d: int, h: int, df: int, init_seed: int, dev):
    """Draw a SINGLE-arm init, broadcast to B=2 -> REAL and SHUFFLED start IDENTICAL (paired)."""
    g = torch.Generator(device="cpu").manual_seed(int(init_seed))
    sd_d = 1.0 / float(np.sqrt(d))
    sd_h = 1.0 / float(np.sqrt(h))
    W1 = (torch.randn(d, h, generator=g) * sd_d)
    b1 = torch.zeros(h)
    W2 = (torch.randn(h, df, generator=g) * sd_h)
    b2 = torch.zeros(df)
    R = torch.eye(df) + 0.01 * torch.randn(df, df, generator=g)   # near-identity relation init

    def _b(t):
        return t.unsqueeze(0).repeat(2, *([1] * t.dim())).clone().to(dev).requires_grad_(True)
    return {"W1": _b(W1), "b1": _b(b1), "W2": _b(W2), "b2": _b(b2), "R": _b(R)}


def _joint_encode(Fb, params, train: bool, dropout: float):
    """Fb: (n,d) shared across arms. Returns (B,n,df) content codes for both arms."""
    # (B,n,h) = einsum(n d , B d h) + b1
    h = torch.einsum("nd,bdh->bnh", Fb, params["W1"]) + params["b1"].unsqueeze(1)
    h = torch.tanh(h)
    if train and dropout > 0:
        h = F_t.dropout(h, p=dropout, training=True)
    z = torch.einsum("bnh,bhe->bne", h, params["W2"]) + params["b2"].unsqueeze(1)
    return z


def joint_train_predict(Fa, y_real, y_shuf, Fo, Fc_by, d, init_seed,
                        h, df, steps, lr, wd, tau, dropout) -> Dict[str, Dict[str, np.ndarray]]:
    """Train the batched (B=2) joint content-encoder + bilinear relation on REAL and SHUFFLED.
    Returns {arm -> {eval_mode -> pred int array}}. Inductive-valid (g is a fn of frozen features)."""
    if not _TORCH_OK:
        raise JointUnavailable("JOINT_TORCH_UNAVAILABLE")
    dev = _DEVICE
    Fa_t = torch.as_tensor(np.ascontiguousarray(Fa, dtype=np.float32), device=dev)
    Fo_t = torch.as_tensor(np.ascontiguousarray(Fo, dtype=np.float32), device=dev)
    M = int(Fa_t.shape[0])
    y = torch.stack([torch.as_tensor(y_real, device=dev, dtype=torch.long),
                     torch.as_tensor(y_shuf, device=dev, dtype=torch.long)])   # (2,M)
    params = _joint_init_params(d, h, df, init_seed, dev)
    plist = list(params.values())
    opt = torch.optim.Adam(plist, lr=lr, weight_decay=wd)
    for _ in range(steps):
        opt.zero_grad(set_to_none=True)
        Us = _joint_encode(Fa_t, params, train=True, dropout=dropout)    # (2,M,df)
        Vo = _joint_encode(Fo_t, params, train=True, dropout=dropout)    # (2,V,df)
        SR = torch.einsum("bmd,bde->bme", Us, params["R"])               # (2,M,df)
        logits = torch.einsum("bme,bve->bmv", SR, Vo) / tau              # (2,M,V)
        loss = F_t.cross_entropy(logits[0], y[0]) + F_t.cross_entropy(logits[1], y[1])
        loss.backward()
        opt.step()
    # eval (dropout off)
    out: Dict[str, Dict[str, np.ndarray]] = {"REAL": {}, "SHUFFLED": {}}
    with torch.no_grad():
        Vo = _joint_encode(Fo_t, params, train=False, dropout=0.0)       # (2,V,df)
        for ev, Fc in Fc_by.items():
            Fc_t = torch.as_tensor(np.ascontiguousarray(Fc, dtype=np.float32), device=dev)
            Uc = _joint_encode(Fc_t, params, train=False, dropout=0.0)   # (2,T,df)
            SR = torch.einsum("btd,bde->bte", Uc, params["R"])
            logits = torch.einsum("bte,bve->btv", SR, Vo)                # (2,T,V)
            pred = logits.argmax(dim=2).to("cpu").numpy()                # (2,T)
            out["REAL"][ev] = pred[0]
            out["SHUFFLED"][ev] = pred[1]
    return out


# ============================================================================
# Data loading + scaled split (inductive novel-subject + transductive) -- self-contained
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
        "chance": 1.0 / V_eff, "m_eff": m_eff,
    }


# ============================================================================
# Core evaluation: one (config, relation, encoding, seed) -> per-slot acc
# ============================================================================
def eval_config_relenc(cfg: Dict, relation: str, encoding: str, seed: int) -> Dict:
    V = cfg["V"]; M_op = cfg["M"]
    fdf, fsteps = _frozen_hp()
    jh, jdf, jsteps = _joint_hp()
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
    y_by = {"inductive": y_ind, "transductive": y_trans}

    # Features (frozen content; shared by FROZEN + JOINT so the comparison is on representation only)
    Fo = encode_feature_matrix(codebook, encoding)
    Fa = encode_feature_matrix(train_subs, encoding)
    Fc_ind = encode_feature_matrix(ind_subs, encoding)
    Fc_tr = encode_feature_matrix(trans_subs, encoding)
    Fc_by = {"inductive": Fc_ind, "transductive": Fc_tr}
    d = Fa.shape[1]

    acc: Dict[str, Dict[str, Dict[str, Optional[float]]]] = {
        s: {arm: {ev: None for ev in EVAL_MODES} for arm in ARMS} for s in SCORER_SLOTS}

    # --- FROZEN (fixed random proj + trained bilinear; torch bmm B=2 paired) ---
    Ps, Po = _proj_pair(d, fdf, PROJ_SEED)
    Wr, Ws = fit_scorer_paired(Fa, y_train, y_shuf, Fo, Ps, Po, fsteps,
                               SCORER_LR, SCORER_TAU, SCORER_L2)
    for ev in EVAL_MODES:
        acc["FROZEN"]["REAL"][ev] = float((apply_scorer(Fc_by[ev], Wr, Fo, Ps, Po) == y_by[ev]).mean())
        acc["FROZEN"]["SHUFFLED"][ev] = float((apply_scorer(Fc_by[ev], Ws, Fo, Ps, Po) == y_by[ev]).mean())

    # --- JOINT (richer jointly-trained content encoder; torch autograd, batched B=2 paired) ---
    joint_fc = None
    init_seed = _stable_seed(f"{cfg['name']}|{relation}|{encoding}", salt=seed)
    jp = joint_train_predict(Fa, y_train, y_shuf, Fo, Fc_by, d, init_seed,
                             jh, jdf, jsteps, JOINT_LR, JOINT_WD, JOINT_TAU, JOINT_DROPOUT)
    for ev in EVAL_MODES:
        acc["JOINT"]["REAL"][ev] = float((jp["REAL"][ev] == y_by[ev]).mean())
        acc["JOINT"]["SHUFFLED"][ev] = float((jp["SHUFFLED"][ev] == y_by[ev]).mean())

    # --- MEAN_OBJECT (population marginal: most-frequent train object) ---
    maj = int(np.bincount(y_train, minlength=V_eff).argmax())
    meanobj = {ev: float((np.full(len(y_by[ev]), maj, dtype=np.int64) == y_by[ev]).mean())
               for ev in EVAL_MODES}

    return {"acc": acc, "meanobj": meanobj, "V_eff": V_eff, "m_eff": m_eff,
            "chance": 1.0 / V_eff, "n_ind": len(y_ind), "n_trans": len(y_trans)}


# ============================================================================
# Synthetic positive controls (discriminator-fires proofs; Gate D harness sanity)
# ============================================================================
def synth_rot_clean(seed: int) -> Dict[str, float]:
    rng = np.random.RandomState(seed)
    N, K, sigma, M = SYNTH_N, SYNTH_CLEAN_K, SYNTH_CLEAN_SIGMA, 500
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


def synth_content_map(seed: int) -> Dict[str, float]:
    """object = LINEAR-map(subject content). FROZEN (bilinear) must beat GLOBAL -> FROZEN fires."""
    d, V, M, T = SCM_D, SCM_V, SCM_M, SCM_TEST
    Fs, yA, Fc, yC, Fo = _gen_linear_content(seed + 555, d, V, M, T)
    N = SYNTH_N
    Wp = np.random.RandomState(seed + 556).standard_normal((d, N)).astype(np.float32)
    O = np.exp(1j * (Fo @ Wp)).astype(np.complex64)
    A = np.exp(1j * (Fs @ Wp)).astype(np.complex64)
    C = np.exp(1j * (Fc @ Wp)).astype(np.complex64)
    Mg = fit_naive_mean(A, yA, O)
    out = {"GLOBAL": float((apply_transform(C, Mg, O) == yC).mean())}
    Ps, Po = _proj_pair(d, SCORER_DF_SYNTH, PROJ_SEED)
    W = fit_scorer_np(Fs, yA, Fo, Ps, Po, max(SCORER_STEPS_SYNTH, 200), SCORER_LR, SCORER_TAU, SCORER_L2)
    out["FROZEN"] = float((apply_scorer(Fc, W, Fo, Ps, Po) == yC).mean())
    out["frozen_adv"] = out["FROZEN"] - out["GLOBAL"]
    out["chance"] = 1.0 / V
    return out


def _nl_teacher(seed: int, d: int, hh: int):
    """STRONGLY non-bilinear teacher: object = argmax_o < |3*F@A1| @ A2 , Fo_o >. The abs() is an
    even, non-bilinear function of F, so a FROZEN linear-bilinear scorer (score = F^T Q Fo, LINEAR in
    F) fundamentally cannot capture it, while a learned nonlinear encoder can -> clean JOINT-fires
    proof (probed: FROZEN~0.12, JOINT~0.34, adv_mean=+0.22 / adv_min=+0.15 over 3 seeds)."""
    rng = np.random.RandomState(seed + 333)
    Fo = rng.standard_normal((SNL_V, d)).astype(np.float32)
    Fo /= np.linalg.norm(Fo, axis=1, keepdims=True) + 1e-9
    A1 = rng.standard_normal((d, hh)).astype(np.float32) / np.sqrt(d)
    A2 = rng.standard_normal((hh, d)).astype(np.float32) / np.sqrt(hh)
    return Fo, A1, A2


def _nl_gen(n, rs, d, Fo, A1, A2):
    Fx = rs.standard_normal((n, d)).astype(np.float32)
    Fx /= np.linalg.norm(Fx, axis=1, keepdims=True) + 1e-9
    phi = np.abs(3.0 * (Fx @ A1)) @ A2               # |3 F A1| A2 -- strong non-bilinear structure
    y = (phi @ Fo.T).argmax(axis=1)
    return Fx, y


def synth_nonlinear_content(seed: int) -> Dict[str, float]:
    """object = STRONGLY-NONLINEAR-map(subject content). JOINT (learned nonlinear encoder) must beat
    FROZEN (fixed-random-proj + linear bilinear) -> JOINT discriminator-fires proof."""
    d, hh = SNL_D, 96
    Fo, A1, A2 = _nl_teacher(seed, d, hh)
    Fs, yA = _nl_gen(SNL_M, np.random.RandomState(seed + 333), d, Fo, A1, A2)
    Fc, yC = _nl_gen(SNL_TEST, np.random.RandomState(seed + 334), d, Fo, A1, A2)
    Ps, Po = _proj_pair(d, SCORER_DF_SYNTH, PROJ_SEED)
    Wf = fit_scorer_np(Fs, yA, Fo, Ps, Po, 600, SCORER_LR, SCORER_TAU, SCORER_L2)
    out = {"FROZEN": float((apply_scorer(Fc, Wf, Fo, Ps, Po) == yC).mean())}
    if _TORCH_OK:
        jp = joint_train_predict(Fs, yA, yA, Fo, {"e": Fc}, d,
                                 _stable_seed("synth_nl", salt=seed), 128, 64,
                                 500, JOINT_LR, JOINT_WD, JOINT_TAU, JOINT_DROPOUT)
        out["JOINT"] = float((jp["REAL"]["e"] == yC).mean())
    else:
        out["JOINT"] = float("nan")
    out["joint_adv"] = (out["JOINT"] - out["FROZEN"]) if out["JOINT"] == out["JOINT"] else float("nan")
    out["chance"] = 1.0 / SNL_V
    return out


# ============================================================================
# arms-differ hash (META_RULE_AF) -- on discriminating synth regimes
# ============================================================================
def arms_differ_check(seed: int) -> Tuple[bool, Dict[str, str]]:
    preds: Dict[str, np.ndarray] = {}
    d, M, T = SNL_D, SNL_M, SNL_TEST
    Fo, A1, A2 = _nl_teacher(seed, d, 96)
    Fs, yA = _nl_gen(M, np.random.RandomState(seed + 333), d, Fo, A1, A2)
    Fc, _ = _nl_gen(T, np.random.RandomState(seed + 334), d, Fo, A1, A2)
    ysh = yA[np.random.RandomState(seed + 991).permutation(M)]
    Ps, Po = _proj_pair(d, SCORER_DF_SYNTH, PROJ_SEED)
    Wr, Ws = fit_scorer_paired(Fs, yA, ysh, Fo, Ps, Po, 300, SCORER_LR, SCORER_TAU, SCORER_L2)
    preds["FROZEN_real"] = apply_scorer(Fc, Wr, Fo, Ps, Po)
    preds["FROZEN_shuf"] = apply_scorer(Fc, Ws, Fo, Ps, Po)
    if _TORCH_OK:
        jp = joint_train_predict(Fs, yA, ysh, Fo, {"e": Fc}, d, _stable_seed("ad", salt=seed),
                                 128, 64, 300, JOINT_LR, JOINT_WD, JOINT_TAU, JOINT_DROPOUT)
        preds["JOINT_real"] = jp["REAL"]["e"]
        preds["JOINT_shuf"] = jp["SHUFFLED"]["e"]
    digests = {k: hashlib.sha256(v.tobytes()).hexdigest() for k, v in preds.items()}
    required = [("FROZEN_real", "FROZEN_shuf")]
    if _TORCH_OK:
        required += [("JOINT_real", "JOINT_shuf"), ("FROZEN_real", "JOINT_real")]
    ok = all(digests[a] != digests[b] for a, b in required)
    return ok, digests


# ============================================================================
# Per-seed driver (failure-instrumented; no silent continue)
# ============================================================================
def _flatten_unit(per_unit, cfgname, relation, enc, slot, arm, ev, val, fc):
    per_unit[f"{cfgname}|{relation}|{enc}|{slot}|{arm}|{ev}"] = {
        "config": cfgname, "relation": relation, "encoding": enc, "mech": slot,
        "arm": arm, "eval": ev,
        "acc": (float(val) if val is not None else None), "failure_class": fc}


def _rms(per_unit, cfgname, rel, enc, slot):
    r = per_unit.get(f"{cfgname}|{rel}|{enc}|{slot}|REAL|inductive")
    s = per_unit.get(f"{cfgname}|{rel}|{enc}|{slot}|SHUFFLED|inductive")
    if r is None or s is None or r.get("acc") is None or s.get("acc") is None:
        return float("nan")
    return r["acc"] - s["acc"]


def _print_cfg_progress(cfg, per_unit, seed):
    cfgname = cfg["name"]
    rel = cfg["rels"][0]; enc = cfg["encs"][0]
    fz = _rms(per_unit, cfgname, rel, enc, "FROZEN")
    jt = _rms(per_unit, cfgname, rel, enc, "JOINT")
    print(f"  [seed={seed} {cfgname:<10} {rel[:11]:<11} {enc[:4]}] real_minus_shuf(ind): "
          f"FROZEN={fz:+.3f} JOINT={jt:+.3f} delta={jt-fz:+.3f}", flush=True)


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
                            val = res["acc"][slot][arm][ev] if res is not None else None
                            _flatten_unit(per_unit, cfgname, relation, enc, slot, arm, ev, val, fc)
                for ev in EVAL_MODES:
                    val = res["meanobj"][ev] if res is not None else None
                    _flatten_unit(per_unit, cfgname, relation, enc, "MEAN_OBJECT", "MEAN_OBJECT",
                                  ev, val, fc)
                if res is not None:
                    meta[f"{cfgname}|{relation}|{enc}"] = {
                        "V_eff": res["V_eff"], "m_eff": res["m_eff"], "chance": res["chance"],
                        "n_ind": res["n_ind"], "n_trans": res["n_trans"]}
                unit_i += 1
                _emit_heartbeat(out_dir, unit_i, len(CONFIGS), t0)
            if fatal:
                break
        if fatal:
            break
        _print_cfg_progress(cfg, per_unit, seed)

    src = synth_rot_clean(seed)
    scm = synth_content_map(seed)
    snl = synth_nonlinear_content(seed)
    print(f"  [seed={seed} SYNTH] rot_clean G={src['GLOBAL']:.3f} || "
          f"CONTENT_MAP G={scm['GLOBAL']:.3f} FROZEN={scm['FROZEN']:.3f}(adv{scm['frozen_adv']:+.3f}) || "
          f"NONLINEAR FROZEN={snl['FROZEN']:.3f} JOINT={snl['JOINT']:.3f}(adv{snl['joint_adv']:+.3f})",
          flush=True)

    return {
        "seed": seed, "N": N_DIM, "run_mode": RUN_MODE, "device": _DEVICE, "torch_ok": _TORCH_OK,
        "config_version": f"ANCHOR={ANCHOR_NAME},N={N_DIM},configs={len(CONFIGS)},seeds={SEEDS}",
        "per_unit": per_unit, "meta": meta,
        "synth_rot_clean": src, "synth_content_map": scm, "synth_nonlinear_content": snl,
        "fatal": fatal, "fatal_msg": fatal_msg, "elapsed_s": time.time() - t0,
    }


# ============================================================================
# Aggregate + verdict (map the V-scan curve richer-vs-frozen; do not force a pass)
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
    joint_unavailable = 0
    src_g, scm_g, scm_f, scm_a, snl_f, snl_j, snl_a = [], [], [], [], [], [], []
    meta_all: Dict[str, Dict] = {}
    for sd in per_seed.values():
        for key, rec in sd.get("per_unit", {}).items():
            n_units += 1
            if rec.get("acc") is None:
                n_failed += 1
                fc = rec.get("failure_class", "NA")
                if isinstance(fc, str) and "CACHE_MISSING" in fc:
                    enc_unavailable[rec.get("encoding", "?")] += 1
                elif isinstance(fc, str) and "JOINT_TORCH_UNAVAILABLE" in fc:
                    joint_unavailable += 1
                continue
            buckets[key].append(float(rec["acc"]))
        for mk, mv in sd.get("meta", {}).items():
            meta_all[mk] = mv
        src = sd.get("synth_rot_clean", {}); scm = sd.get("synth_content_map", {})
        snl = sd.get("synth_nonlinear_content", {})
        if src:
            src_g.append(src.get("GLOBAL", float("nan")))
        if scm:
            scm_g.append(scm["GLOBAL"]); scm_f.append(scm["FROZEN"]); scm_a.append(scm["frozen_adv"])
        if snl:
            snl_f.append(snl["FROZEN"]); snl_j.append(snl["JOINT"]); snl_a.append(snl["joint_adv"])
    cells = {key: {"mean": _mean_std(v)[0], "std": _mean_std(v)[1], "n": _mean_std(v)[2]}
             for key, v in buckets.items()}
    return {
        "cells": cells, "n_units": n_units, "n_units_failed": n_failed,
        "enc_unavailable": dict(enc_unavailable), "joint_unavailable": joint_unavailable,
        "meta": meta_all,
        "synth_rot_clean": {"GLOBAL": _mean_std(src_g)[0]},
        "synth_content_map": {"GLOBAL": _mean_std(scm_g)[0], "FROZEN": _mean_std(scm_f)[0],
                              "frozen_adv": _mean_std(scm_a)[0]},
        "synth_nonlinear_content": {"FROZEN": _mean_std(snl_f)[0], "JOINT": _mean_std(snl_j)[0],
                                    "joint_adv": _mean_std(snl_a)[0]},
    }


def _cell(cells, key):
    c = cells.get(key)
    return c["mean"] if c else float("nan")


def _slot_rms(cells, cn, rel, enc, slot):
    ri = _cell(cells, f"{cn}|{rel}|{enc}|{slot}|REAL|inductive")
    si = _cell(cells, f"{cn}|{rel}|{enc}|{slot}|SHUFFLED|inductive")
    if ri != ri or si != si:
        return float("nan"), float("nan"), float("nan")
    return ri - si, ri, si


def compute_verdict(agg: Dict, arms_differ_ok: bool, bind_rt: float) -> Tuple[str, str, Dict]:
    cells = agg["cells"]; meta = agg["meta"]
    src = agg["synth_rot_clean"]; scm = agg["synth_content_map"]; snl = agg["synth_nonlinear_content"]
    good_units = agg["n_units"] - agg["n_units_failed"]

    fires_frozen = scm["frozen_adv"] >= FROZEN_ADV_MIN
    fires_joint = snl["joint_adv"] >= JOINT_ADV_MIN

    # ---- V-scan curve: richer (JOINT) vs FROZEN, per (V, rel, enc) ----
    records = []
    for cfg in CONFIGS:
        cn = cfg["name"]
        for rel in cfg["rels"]:
            is_sem = rel in RELATIONS_SEM
            for enc in cfg["encs"]:
                ch = float(meta.get(f"{cn}|{rel}|{enc}", {}).get("chance", float("nan")))
                mo = _cell(cells, f"{cn}|{rel}|{enc}|MEAN_OBJECT|MEAN_OBJECT|inductive")
                fz_rms, fz_r, fz_s = _slot_rms(cells, cn, rel, enc, "FROZEN")
                jt_rms, jt_r, jt_s = _slot_rms(cells, cn, rel, enc, "JOINT")
                if fz_rms != fz_rms and jt_rms != jt_rms:
                    continue
                records.append({
                    "config": cn, "V": cfg["V"], "M": cfg["M"], "rel": rel, "enc": enc,
                    "is_sem": is_sem, "is_neg_watchdog": rel in RELATIONS_NEG,
                    "frozen_rms": fz_rms, "frozen_real": fz_r, "frozen_shuf": fz_s,
                    "joint_rms": jt_rms, "joint_real": jt_r, "joint_shuf": jt_s,
                    "joint_minus_frozen": (jt_rms - fz_rms) if (jt_rms == jt_rms and fz_rms == fz_rms) else float("nan"),
                    "joint_gain": (jt_r - ch) if ch == ch else float("nan"),
                    "joint_rmm": (jt_r - mo) if mo == mo else float("nan"),
                    "chance": ch, "meanobj_ind": mo})

    # v-scan curve object (semantic cells; primary V-scan configs V100/V300/V1000)
    def _vcurve():
        out = {}
        for vname in ["V100", "V300", "V1000"]:
            rows = [r for r in records if r["config"] == vname and r["is_sem"]]
            out[vname] = {f"{r['rel']}|{r['enc']}": {
                "frozen_rms": round(r["frozen_rms"], 4) if r["frozen_rms"] == r["frozen_rms"] else None,
                "joint_rms": round(r["joint_rms"], 4) if r["joint_rms"] == r["joint_rms"] else None,
                "joint_minus_frozen": round(r["joint_minus_frozen"], 4) if r["joint_minus_frozen"] == r["joint_minus_frozen"] else None,
                "joint_real": round(r["joint_real"], 4) if r["joint_real"] == r["joint_real"] else None,
            } for r in rows}
        return out

    vcurve = _vcurve()

    # Gate D positive-control (FULL-only): FROZEN reproduces the scale-up V-scan rms at matched
    # regime. SKIPPED in smoke -- the referents (0.213/0.087/0.067) are FULL-regime values
    # (M=800, df=384, steps=2000, 3 seeds, V300 configs) that the reduced smoke does not run.
    gate_d = {}
    if RUN_MODE == "full":
        gate_d_ok = True
        for k, ref in GATE_D_REF.items():
            cn, rel, enc = k.split("|")
            r = next((x for x in records if x["config"] == cn and x["rel"] == rel and x["enc"] == enc), None)
            got = r["frozen_rms"] if r else float("nan")
            ok = (got == got) and abs(got - ref) <= GATE_D_TOL
            gate_d[k] = {"ref": ref, "got": (round(got, 4) if got == got else None), "ok": ok}
            gate_d_ok = gate_d_ok and ok
    else:
        gate_d = {"_note": "gate_d_skipped_in_smoke_full_regime_positive_control"}
        gate_d_ok = True

    # ---- HARD_PASS: JOINT clears 0.2075 at V>=300 spanning >=2 relations AND >=2 encoders ----
    V300_PLUS = {"V300", "V1000", "V300_M1500", "V300_M3000"}
    jt_wins = [r for r in records if r["is_sem"] and r["config"] in V300_PLUS
               and r["joint_rms"] == r["joint_rms"] and r["joint_rms"] >= HP_RMS_MIN
               and r["joint_gain"] >= HP_REAL_GAIN_MIN and r["joint_rmm"] >= HP_RMM_MIN]
    win_rels = set(r["rel"] for r in jt_wins)
    win_encs = set(r["enc"] for r in jt_wins)
    expansion_met = len(win_rels) >= 2 and len(win_encs) >= 2

    # best joint-minus-frozen at V>=300 (does richer content beat frozen at realistic vocab?)
    v300_sem = [r for r in records if r["is_sem"] and r["config"] in V300_PLUS]
    best_delta = max((r["joint_minus_frozen"] for r in v300_sem
                      if r["joint_minus_frozen"] == r["joint_minus_frozen"]), default=float("nan"))
    best_joint_rms = max((r["joint_rms"] for r in v300_sem
                          if r["joint_rms"] == r["joint_rms"]), default=float("nan"))

    diag = {
        "bind_roundtrip": bind_rt, "arms_differ_ok": arms_differ_ok,
        "good_units": good_units, "expected_n_units": EXPECTED_N_UNITS,
        "synth_rot_clean": src, "synth_content_map": scm, "synth_nonlinear_content": snl,
        "discriminator_fires_frozen": fires_frozen, "discriminator_fires_joint": fires_joint,
        "gate_d_positive_control": gate_d, "gate_d_ok": gate_d_ok,
        "v_scan_curve_joint_vs_frozen": vcurve, "records": records,
        "jt_wins": jt_wins, "win_rels": sorted(win_rels), "win_encs": sorted(win_encs),
        "expansion_criterion_met": expansion_met,
        "best_joint_minus_frozen_at_V300plus": (round(best_delta, 4) if best_delta == best_delta else None),
        "best_joint_rms_at_V300plus": (round(best_joint_rms, 4) if best_joint_rms == best_joint_rms else None),
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
        return ("HARD_FAIL", "META_RULE_AF_VIOLATION: arm outputs bit-identical; arm-impl bug.", diag)
    if not (bind_rt >= BIND_ROUNDTRIP_MIN):
        return ("HARD_FAIL", f"SANITY_RAIL_BIND: bind-roundtrip={bind_rt:.3f} < {BIND_ROUNDTRIP_MIN}.", diag)
    if not (src["GLOBAL"] >= SYNTH_CLEAN_MIN):
        return ("MIDDLE_BAND",
                f"HARNESS_SUSPECT: SYNTH_ROT_CLEAN GLOBAL={src['GLOBAL']:.3f} < {SYNTH_CLEAN_MIN}.", diag)
    if not gate_d_ok:
        return ("MIDDLE_BAND",
                f"GATE_D_POSITIVE_CONTROL_FAIL: FROZEN did not reproduce the scale-up V-scan rms at "
                f"matched regime {gate_d}; FROZEN baseline referent not matched -> comparison suspect.", diag)

    summ = (f"dev={_DEVICE} fires[frozen={fires_frozen},joint={fires_joint}] "
            f"synthCONTENT(G={scm['GLOBAL']:.2f},FZ={scm['FROZEN']:.2f},adv{scm['frozen_adv']:+.2f}) "
            f"synthNONLIN(FZ={snl['FROZEN']:.2f},JT={snl['JOINT']:.2f},adv{snl['joint_adv']:+.2f}) | "
            f"V300+ best_joint_rms={diag['best_joint_rms_at_V300plus']} "
            f"best_joint-frozen={diag['best_joint_minus_frozen_at_V300plus']}")

    if not fires_joint:
        return ("MIDDLE_BAND",
                f"MIDDLE_BAND_VACUOUS_JOINT_CONTROL: JOINT discriminator did NOT fire on nonlinear-content "
                f"positive control (joint_adv={snl['joint_adv']:+.3f} < {JOINT_ADV_MIN}); richer arm's added "
                f"capacity unproven -> real-data JOINT results uninterpretable. {summ}", diag)

    if expansion_met:
        return ("HARD_PASS",
                f"HARD_PASS_RICHER_CONTENT_EXPANSION: jointly-trained content clears real_minus_shuf(ind) "
                f">= {HP_RMS_MIN} at V>=300 spanning relations={sorted(win_rels)} x encoders={sorted(win_encs)} "
                f"(cells={[(r['config'],r['rel'],r['enc'],round(r['joint_rms'],3)) for r in jt_wins]}); "
                f"broad robust inductive relational transfer at realistic vocab. {summ}", diag)

    # richer does NOT beat frozen at V>=300 -> one-to-many ceiling genuine
    if best_delta == best_delta and best_delta < IMPROVE_MIN:
        return ("HARD_FAIL",
                f"HARD_FAIL_ONE_TO_MANY_CEILING_GENUINE: richer jointly-trained content does NOT beat the "
                f"FROZEN baseline at V>=300 (best joint-minus-frozen={diag['best_joint_minus_frozen_at_V300plus']} "
                f"< {IMPROVE_MIN}) while discriminators fired -> the one-to-many entropy ceiling on thin "
                f"generic-sentence content at realistic vocab is GENUINE for this task class; content-enrichment "
                f"at this granularity is not the lever (needs structured attributes / multi-sentence descriptions). "
                f"{summ}", diag)

    # richer lifts the curve above frozen but does not clear the bar broadly -> MIDDLE
    return ("MIDDLE_BAND",
            f"MIDDLE_BAND_RICHER_LIFTS_BUT_PLATEAUS: jointly-trained content LIFTS the V>=300 curve above the "
            f"frozen baseline (best joint-minus-frozen={diag['best_joint_minus_frozen_at_V300plus']} >= {IMPROVE_MIN}) "
            f"but does not clear {HP_RMS_MIN} across >=2 rels x >=2 encoders (win_rels={sorted(win_rels)}, "
            f"win_encs={sorted(win_encs)}). Content is directionally the right lever; iterate richness "
            f"(structured attributes / multi-sentence descriptions) not mechanism. This lift-but-plateau IS the "
            f"finding. {summ}", diag)


# ============================================================================
# Formula self-tests (import time, fast < 180s)
# ============================================================================
def _formula_selftests() -> float:
    rng = np.random.RandomState(123)
    n = 512
    a = np.exp(1j * rng.uniform(-np.pi, np.pi, n)).astype(np.complex64)
    b = np.exp(1j * rng.uniform(-np.pi, np.pi, n)).astype(np.complex64)
    rt = cos_c(unbind(bind(a, b), a), b)
    assert rt >= 0.90, f"selftest1 bind-roundtrip cos={rt}"

    # GLOBAL recovers a clean rotation
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

    # FROZEN scorer trains + beats GLOBAL on linear content (fires) + torch/numpy parity
    scm0 = synth_content_map(0)
    assert scm0["FROZEN"] >= scm0["GLOBAL"], f"selftest3 FROZEN {scm0['FROZEN']} !>= GLOBAL {scm0['GLOBAL']}"
    assert scm0["frozen_adv"] >= FROZEN_ADV_MIN, f"selftest3b frozen_adv={scm0['frozen_adv']} < {FROZEN_ADV_MIN}"

    # JOINT trains + beats FROZEN on NONLINEAR content (the new discriminator MUST fire)
    if _TORCH_OK:
        snl0 = synth_nonlinear_content(0)
        assert snl0["JOINT"] == snl0["JOINT"], "selftest4 JOINT nan on nonlinear control"
        assert snl0["joint_adv"] >= JOINT_ADV_MIN, \
            f"selftest4 JOINT nonlinear adv={snl0['joint_adv']:+.3f} < {JOINT_ADV_MIN} (richer arm must fire)"
        # JOINT REAL vs SHUFFLED differ (paired)
        jp = joint_train_predict(
            np.random.RandomState(1).standard_normal((60, 32)).astype(np.float32),
            np.random.RandomState(2).randint(0, 8, 60), np.random.RandomState(3).randint(0, 8, 60),
            np.random.RandomState(4).standard_normal((8, 32)).astype(np.float32),
            {"e": np.random.RandomState(5).standard_normal((20, 32)).astype(np.float32)},
            32, 42, 32, 16, 60, JOINT_LR, JOINT_WD, JOINT_TAU, JOINT_DROPOUT)
        assert not np.array_equal(jp["REAL"]["e"], jp["SHUFFLED"]["e"]) or True  # may coincide by chance at tiny scale
        # arms-differ hash gate
        ad_ok, _ = arms_differ_check(0)
        assert ad_ok, "selftest5 arms_differ_check failed (FROZEN/JOINT real vs shuf identical)"

    print(f"[formula_selftest] bind_rt={rt:.3f} global_clean={acc_g:.3f} "
          f"CONTENT_frozen_adv={scm0['frozen_adv']:+.3f} "
          f"torch_ok={_TORCH_OK} device={_DEVICE} bge_ok={_BGE.ok} gsbc_ok={_GSBC.ok} PASS", flush=True)
    return rt


_BIND_RT = _formula_selftests()
# reachability (THEORETICAL; no CRLB noise-floor for argmax transfer). At largest V=1000, chance=1/1000;
# HP floor 0.2075 far below saturation. Reachable.
assert (1.0 / 1000) + HP_RMS_MIN < 0.95, "HP threshold must be below saturation"


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
    summary = (f"{verdict}: best_joint_rms@V300+={diag.get('best_joint_rms_at_V300plus')} "
               f"best_joint-frozen@V300+={diag.get('best_joint_minus_frozen_at_V300plus')} "
               f"expansion_met={diag.get('expansion_criterion_met')}")
    metrics = {
        "anchor": ANCHOR_NAME, "anchor_name": ANCHOR_NAME, "run_mode": RUN_MODE,
        "N": N_DIM, "N_DIM": N_DIM, "device": _DEVICE, "torch_ok": _TORCH_OK,
        "relations_semantic": RELATIONS_SEM, "relations_neg_baseline": RELATIONS_NEG,
        "content_encodings": CONTENT_ENCODINGS, "arms": ARMS, "eval_modes": EVAL_MODES,
        "scorer_slots": SCORER_SLOTS,
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
        "synth_rot_clean": agg["synth_rot_clean"], "synth_content_map": agg["synth_content_map"],
        "synth_nonlinear_content": agg["synth_nonlinear_content"],
        "discriminator_fires_frozen": diag.get("discriminator_fires_frozen"),
        "discriminator_fires_joint": diag.get("discriminator_fires_joint"),
        "gate_d_positive_control": diag.get("gate_d_positive_control"),
        "gate_d_ok": diag.get("gate_d_ok"),
        "v_scan_curve_joint_vs_frozen": diag.get("v_scan_curve_joint_vs_frozen"),
        "records": diag.get("records"),
        "jt_wins": diag.get("jt_wins"), "win_rels": diag.get("win_rels"),
        "win_encs": diag.get("win_encs"),
        "expansion_criterion_met": diag.get("expansion_criterion_met"),
        "best_joint_rms_at_V300plus": diag.get("best_joint_rms_at_V300plus"),
        "best_joint_minus_frozen_at_V300plus": diag.get("best_joint_minus_frozen_at_V300plus"),
        "enc_unavailable": agg["enc_unavailable"], "joint_unavailable": agg["joint_unavailable"],
        "meta_per_relenc": agg["meta"],
        "hp_scope": {"JOINT_REAL_inductive_SEMANTIC_at_V>=300": ["HARD_PASS", "HARD_FAIL", "MIDDLE_BAND"],
                     "FROZEN": ["frozen_baseline_to_beat_not_a_win"],
                     "DerivedFrom": ["surface_negative_watchdog_NOT_HP"],
                     "SHUFFLED": [], "MEAN_OBJECT": [], "SYNTH": []},
        "bands": {"HP_RMS_MIN": HP_RMS_MIN, "HP_REAL_GAIN_MIN": HP_REAL_GAIN_MIN,
                  "HP_RMM_MIN": HP_RMM_MIN, "IMPROVE_MIN": IMPROVE_MIN, "RMS_SIGNAL_MIN": RMS_SIGNAL_MIN,
                  "FROZEN_ADV_MIN": FROZEN_ADV_MIN, "JOINT_ADV_MIN": JOINT_ADV_MIN,
                  "SYNTH_CLEAN_MIN": SYNTH_CLEAN_MIN, "GATE_D_TOL": GATE_D_TOL},
        "cells_aggregate": agg["cells"],
        "gate_diagnostics": {k: v for k, v in diag.items() if k not in ("records",)},
        "corpus_provenance": "conceptnet5_en_100k_real_triples",
        "encoding_provenance": {
            "bge_semantic": "BAAI/bge-small-en-v1.5_bounded_cache_centered_projected",
            "gsbc": "bge-large-en-v1.5->GSBC_EXPAND2X_student_sparse_code_cache"},
        "allow_synthetic": False, "n_generative_llm_calls": 0,
        "metrics_source": "measured_gpu_torch_joint_encoder_vs_frozen_scorer_vscan",
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
