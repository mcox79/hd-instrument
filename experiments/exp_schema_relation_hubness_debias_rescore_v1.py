"""schema_relation_hubness_debias_rescore_v1 -- TRAINING-FREE post-hoc rescore of the reframe cell.

SCIENTIFIC QUESTION (sharpen rank-1 on the MIDDLE_BAND reframe):
  exp_schema_relation_hitsatk_mrr_reframe_v1 landed MIDDLE_BAND: filtered Hits@10 rms mostly clears
  the informal 0.20 mark but MRR never reliably clears the 0.15 HARD_PASS floor and win_rels/win_encs
  are empty -- the true object lands top-10 but not rank-1. A drill
  (CITED@notes/research_hubness_popularity_debias_rank1_sharpening_2026-07-05.md) diagnosed the rank-1
  crowding as (1) geometric HUBNESS (object-side argmax-winner Gini 0.87-0.95) + (2) LABEL-PRIOR bias
  (corr(Nk, train_freq) 0.42-0.80). The proposed fix: a training-free post-hoc rescore of the EXISTING
  (T,V) score matrix combining CSLS (mutual-neighbor hubness correction) + logit-adjustment (label-prior
  debias). NO retraining.

MECHANISM (training-free; applied on per-row CALIBRATED LOG-PROBS L = log_softmax(S / slot_tau) so the
  logit-adjust tau=1.0 default is dimensionally coherent (nats) and NONE ranks IDENTICALLY to the parent
  reframe -- log_softmax is strictly row-monotone -> positive-control reproduce, Gate D):
    NONE  = L                                   (== parent reframe baseline)
    CSLS  = L - r_k(row) - r_k(col)             (COEFFICIENT-1 form per the research note; see NOTE below)
    LOGIT = L - tau * log P_train(object)       (Menon et al. 2021 post-hoc logit adjustment)
    BOTH  = L - r_k(row) - r_k(col) - tau*log P_train(object)
  NOTE on CSLS coefficient: the canonical CSLS (Conneau et al. 2018) is 2*cos - r_k(x) - r_k(y), correct
  for a BOUNDED symmetric cosine (mutual-NN excess). For an UNBOUNDED per-row log-prob a pure additive
  object-hub bias c_j SURVIVES the 2x form at coefficient +1 (2(L+c) - r_row - (r_col+c) = 2L - r_row -
  r_col + c) but is FULLY removed by the coefficient-1 form (L+c) - (r_col+c) = L - r_col. exp_dev off-disk
  verified this: the coef-1 form is the mechanistically-correct object-hub remover here and is exactly the
  note's own written formula (s'(t,j) = s(t,j) - CSLS_term(t,j)). The canonical 2x identity is retained as
  a documented reference in the formula self-test. THEORETICAL@exp_dev diagnostic 2026-07-05.

THE LOAD-BEARING COMPARISON: POST-RESCORE vs PRE-RESCORE (NONE), PAIRED, same seed/config units.
  Discriminator = REAL - SHUFFLED (rms) on INDUCTIVE filtered rank; the rms LIFT (post-pre) is the gate.
  The SHUFFLED-absolute lift is reported as the artifact guard (rescore must not lift shuffled). The cell
  ALSO reports REAL-absolute and SHUFFLED-absolute lifts + the REAL-vs-SHUFFLED argmax-winner Gini
  asymmetry so the result is fully interpretable regardless of which band it lands in.

EXP_DEV PRE-DISPATCH CAVEAT (MEASURED off-disk 2026-07-05; surfaced honestly, not a claim of the verdict):
  On synthetic constructions the rescore lifts the PAIRED rms ONLY when the crowding is a thin-veneer
  ASYMMETRIC density hub (present in REAL, absent in SHUFFLED) over a RECOVERABLE truth (CSLS rms Hits@1
  lift +0.05..+0.125). It is NEAR-INERT (|rms lift| <= ~0.016) for (a) a SHARED label-prior hub (cancels
  in the paired difference because shuffle preserves the object multiset -> SHUFFLED already subtracts
  label-prior) and (b) a DEEP-truth weak scorer (the true object is far below the decoy -- the note's own
  z-margin 2.2-2.7 std -- so de-hubbing surfaces OTHER wrong objects, not the truth). The V>=300 real
  regime resembles (a)+(b); HARD_FAIL / low-MIDDLE is the exp_dev-predicted outcome, but the real BGE
  hubness may differ from the toy so the (cheap ~10min) full run is the pre-registered measurement -- and
  the note pre-registered HARD_FAIL as the redirect to trained hard-neg mining / richer content.

DISCRIMINATOR-FIRES CONTROLS (smoke-mandatory):
  - synth_csls_hub_veneer (POSITIVE, MUST FIRE): strong clean map (truth recoverable) + additive density
      hub injected into the REAL log-prob matrix ONLY. max(CSLS,BOTH) must lift REAL Hits@1 AND rms Hits@1
      >= floor while SHUFFLED Hits@1 is NOT lifted -> proves the instrument fires on the FIXABLE phenomenon.
  - synth_hub_null (MUST BE CLEAN): strong map, no hub. |BOTH rms lift| <= tol (no manufactured signal).
  - synth_label_hub_shared (REPORTED diagnostic): 40% of train relabeled to object 0 (shared label-prior
      hub, TRAINING-induced -> truth is genuinely deep). Documents BOTH the paired-rms cancellation
      (~0 lift by construction) and the deep-truth non-recovery -- the likely V>=300 real regime.

# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; {NONE,CSLS,LOGIT,BOTH} matrices differ; REAL!=SHUF)
# - final_metrics_atomicity = tmp_replace (META_RULE_AH)
# - except SystemExit: raise BEFORE except Exception (no BaseException); start-marker + crash-diag + heartbeat
# - crlb n/a (rank transfer; no closed-form noise floor). chance floor stated; reachability declared
# - baseline_in_band at smoke (SHUFFLED filtered Hits@10 not saturated <0.95; NONE reproduces parent)
# - discriminator survives scale (B/C): synth_csls_hub_veneer proves rescore lifts rank rms on an
#   asymmetric fixable hub; null proves ~0 when none. Real-data V>=300 lift IS the question, justified.
# - HARD_PASS strictly above floor (MRR rms 0.15 AND Hits@1 rms lift 0.05; HF is MRR rms lift <=0.02)
# - HP_SCOPE: HP gates apply to best-of-{FROZEN,JOINT} x {CSLS,LOGIT,BOTH} REAL/inductive/FILTERED
#   SEMANTIC rel x enc at V>=300; NONE=baseline; KNN=reference; DerivedFrom=watchdog; SHUFFLED=control
# - cardinality_ok (META_RULE_H; EXPECTED_N_UNITS = grid x 3 slots x 2 arms x 2 evals; variants sub-fields)
# - per-unit failure-class instrumentation (META_RULE_J; no bare except)
# - calibration_check = adaptive_with_discriminator_gate (k=10/tau=1.0 FIXED pre-run per Conneau/Menon
#   defaults; veneer-fires + null-clean are the proofs; NOT tuned-for-pass on real data)
# - progress_logging = print_flush_true (all progress lines flush=True; line-buffered stdout)
# - reuse: parent scorer/split/rank/knn/joint imported VERBATIM as `ref` (byte-identical code objects)
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
from typing import Dict, List, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

# Reuse the parent reframe cell VERBATIM (byte-identical scorer/split/rank/knn/joint code objects).
import experiments.exp_schema_relation_hitsatk_mrr_reframe_v1 as ref
from experiments._seed_checkpoint import (
    get_output_dir, resumable_seeds, write_partial, aggregate_partials,
)

_TORCH_OK = ref._TORCH_OK
_DEVICE = ref._DEVICE

ANCHOR_NAME = "schema_relation_hubness_debias_rescore_v1"

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
# Config -- reuse parent constants; add rescore machinery.
# ----------------------------------------------------------------------------
N_DIM = ref.N_DIM
RELATIONS_SEM = ref.RELATIONS_SEM
RELATIONS_NEG = ref.RELATIONS_NEG
RELATIONS_ALL = ref.RELATIONS_ALL
CONTENT_ENCODINGS = ref.CONTENT_ENCODINGS
ARMS = ref.ARMS                       # ["REAL", "SHUFFLED"]
EVAL_MODES = ref.EVAL_MODES           # ["inductive", "transductive"]
SCORER_SLOTS = ref.SCORER_SLOTS       # ["FROZEN", "JOINT", "KNN"]
HP_SLOTS = ref.HP_SLOTS               # ["FROZEN", "JOINT"]
HITS_KS = ref.HITS_KS
METRIC_KEYS = ref.METRIC_KEYS

RESCORE_VARIANTS = ["NONE", "CSLS", "LOGIT", "BOTH"]
RESCORE_ARMS_HP = ["CSLS", "LOGIT", "BOTH"]

# FIXED rescore hyperparameters (pre-registered BEFORE the real-data run; NOT tuned-for-pass):
RESCORE_K = 10          # CSLS neighborhood (note pre-reg k; Conneau et al. 2018 standard)
TAU_ADJ = 1.0           # logit-adjustment temperature (Menon et al. 2021 default)
LOGIT_EPS = 1.0         # Laplace smoothing for train-frequency prior
SLOT_TAU = {"FROZEN": ref.SCORER_TAU, "JOINT": ref.JOINT_TAU, "KNN": 1.0}

# Synthetic control regime
SCM_D = ref.SCM_D
SCM_V = ref.SCM_V
SCM_M = ref.SCM_M
SCM_TEST = ref.SCM_TEST
SCORER_DF_SYNTH = ref.SCORER_DF_SYNTH
SYNTH_STRONG_DF = 256
SYNTH_STRONG_STEPS = 3000       # veneer/null: strong map so truth is recoverable behind the hub
SYNTH_WEAK_STEPS = 300          # label-hub-shared diagnostic: weak scorer -> training-induced deep truth
VENEER_B = 10.0                 # additive density-hub bias injected into REAL log-probs (log-prob scale)
VENEER_HN = 8                   # hub-set size
LABEL_RELABEL_FRAC = 0.40       # shared label-prior hub diagnostic

# ----------------------------------------------------------------------------
# Pre-reg bands (LOCKED)
# ----------------------------------------------------------------------------
HP_MRR_RMS_MIN = 0.15          # post-rescore filtered MRR real_minus_shuf(ind) HARD_PASS floor
HP_HITS1_LIFT_MIN = 0.05       # post-rescore Hits@1 rms lift over the matched NONE Hits@1 rms
HP_HITS10_NONREG_MIN = 0.20    # non-regression guard: post Hits@10 rms must not drop below this
REAL_NONDEGRADE_TOL = 0.0      # HARD_PASS anti-phantom: REAL-abs Hits@1 lift must be >= this (rms
                               # improvement must be REAL-driven, not SHUFFLED-collapse)
HF_MRR_LIFT_MAX = 0.02         # HARD_FAIL: max over sem(rel x enc) at V>=300 of best REAL-abs MRR lift <= this
# discriminator-fires gate (synthetic controls; NOT the real-data verdict):
SYNTH_FIRE_H1_LIFT = 0.05      # veneer: max(CSLS,BOTH) REAL Hits@1 lift over NONE
SYNTH_FIRE_RMS_LIFT = 0.05     # veneer: max(CSLS,BOTH) rms Hits@1 lift over NONE
SYNTH_SHUF_MAX_LIFT = 0.04     # veneer: SHUFFLED Hits@1 lift must stay under (artifact guard)
SYNTH_NULL_TOL = 0.03          # null: |BOTH rms lift| must stay under
BIND_ROUNDTRIP_MIN = 0.90
BASE_SAT_HI = 0.95             # SHUFFLED filtered Hits@10 must be below this (not saturated)


# ----------------------------------------------------------------------------
# CONFIG GRID -- mirror the parent reframe
# ----------------------------------------------------------------------------
def _cfg(name, V, M, rels, encs):
    return {"name": name, "V": V, "M": M, "rels": list(rels), "encs": list(encs)}


if RUN_MODE == "smoke":
    SEEDS = [7]
    N_TEST_PER = 60
    POOL_CAP = 6000
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
    CONFIGS = [_cfg(f"V{v}", v, 800, RELATIONS_ALL, CONTENT_ENCODINGS) for v in [100, 300, 1000]]
    _SMOKE_JOINT = None
    _SMOKE_FROZEN_STEPS = None
    _SMOKE_FROZEN_DF = None
    _SMOKE_KNN_K = None


def _joint_hp():
    if RUN_MODE == "smoke":
        return _SMOKE_JOINT["H"], _SMOKE_JOINT["DF"], _SMOKE_JOINT["STEPS"]
    return ref.JOINT_H, ref.JOINT_DF, ref.JOINT_STEPS


def _frozen_hp():
    if RUN_MODE == "smoke":
        return _SMOKE_FROZEN_DF, _SMOKE_FROZEN_STEPS
    return ref.FROZEN_DF, ref.FROZEN_STEPS


def _knn_k():
    return _SMOKE_KNN_K if RUN_MODE == "smoke" else ref.KNN_K


def expected_units(configs, seeds) -> int:
    tot = 0
    for c in configs:
        tot += len(c["rels"]) * len(c["encs"]) * (len(SCORER_SLOTS) * len(ARMS) * len(EVAL_MODES))
    return tot * len(seeds)


EXPECTED_N_UNITS = expected_units(CONFIGS, SEEDS)


def _r(x):
    try:
        return round(float(x), 4) if x == x else None
    except Exception:
        return None


# ============================================================================
# RESCORE MACHINERY (the ONLY new mechanism) -- training-free, post-hoc.
# ============================================================================
def row_log_softmax(S: np.ndarray, tau: float) -> np.ndarray:
    """Per-row calibrated log-probabilities. Strictly row-monotone in S -> NONE ranks == parent."""
    Z = (S.astype(np.float64) / float(tau))
    Z = Z - Z.max(axis=1, keepdims=True)
    lse = np.log(np.exp(Z).sum(axis=1, keepdims=True) + 1e-12)
    return (Z - lse).astype(np.float32)


def topk_row_col_means(L: np.ndarray, k: int) -> Tuple[np.ndarray, np.ndarray]:
    """CSLS local-scaling terms. r_row[t]=mean top-k L[t,:] (cols); r_col[j]=mean top-k L[:,j] (rows)."""
    T, V = L.shape
    kc = int(min(max(k, 1), V))
    kr = int(min(max(k, 1), T))
    r_row = np.partition(L, V - kc, axis=1)[:, V - kc:].mean(axis=1)
    r_col = np.partition(L, T - kr, axis=0)[T - kr:, :].mean(axis=0)
    return r_row.astype(np.float32), r_col.astype(np.float32)


def csls_canonical_2x(L: np.ndarray, k: int) -> np.ndarray:
    """Documented reference: canonical Conneau et al. 2018 CSLS 2*s - r_k(row) - r_k(col).
    NOT applied to real data (see module docstring NOTE); retained for the formula self-test."""
    r_row, r_col = topk_row_col_means(L, k)
    return (2.0 * L - r_row[:, None] - r_col[None, :]).astype(np.float32)


def compute_log_prior(y_train: np.ndarray, V_eff: int, eps: float = LOGIT_EPS) -> np.ndarray:
    """log P_train(object) with Laplace smoothing. Invariant to subject-object shuffle (multiset same)."""
    cnt = np.bincount(y_train.astype(np.int64), minlength=V_eff).astype(np.float64)
    pi = (cnt + eps) / (cnt.sum() + eps * V_eff)
    return np.log(pi).astype(np.float32)


def apply_rescore(L: np.ndarray, variant: str, k: int, log_prior: np.ndarray, tau_adj: float) -> np.ndarray:
    """Post-hoc rescore on the log-prob scale (CSLS coefficient-1 per module docstring NOTE):
      NONE : L
      CSLS : L - r_row - r_col                 (r_row rank-inert per row; kept for formula fidelity)
      LOGIT: L - tau_adj * log_prior
      BOTH : L - r_row - r_col - tau_adj*log_prior   (both terms from the ORIGINAL L)
    """
    if variant == "NONE":
        return L.astype(np.float32)
    out = L.astype(np.float32)
    if variant in ("CSLS", "BOTH"):
        r_row, r_col = topk_row_col_means(L, k)
        out = L - r_row[:, None] - r_col[None, :]
    if variant in ("LOGIT", "BOTH"):
        out = out - float(tau_adj) * log_prior[None, :]
    return out.astype(np.float32)


def _winner_gini(scores: np.ndarray, V_eff: int) -> Dict:
    """object-side argmax-winner concentration (hubness diagnostic)."""
    winners = np.argmax(scores, axis=1)
    wc = np.bincount(winners, minlength=V_eff).astype(np.float64)
    tot = max(wc.sum(), 1.0)
    p = np.sort(wc / tot)
    n = len(p)
    gini = float(np.sum((2 * np.arange(1, n + 1) - n - 1) * p) / max(n * p.sum(), 1e-12)) if n > 0 else 0.0
    return {"gini": round(gini, 4), "top1_share": round(float(wc.max() / tot), 4),
            "distinct_winners": int((wc > 0).sum())}


# ============================================================================
# Core evaluation -- reuse parent score-matrix build; add per-variant rank metrics.
# ============================================================================
def eval_config_relenc(cfg: Dict, relation: str, encoding: str, seed: int) -> Dict:
    V = cfg["V"]; M_op = cfg["M"]
    fdf, fsteps = _frozen_hp()
    jh, jdf, jsteps = _joint_hp()
    kk = _knn_k()
    sp = ref.build_split_scaled(relation, seed, V, N_TEST_PER, POOL_CAP, M_op)
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

    Fo = ref.encode_feature_matrix(codebook, encoding)
    Fa = ref.encode_feature_matrix(train_subs, encoding)
    Fc_by = {"inductive": ref.encode_feature_matrix(ind_subs, encoding),
             "transductive": ref.encode_feature_matrix(trans_subs, encoding)}
    d = Fa.shape[1]

    filt_mask = {ev: ref._filter_mask(subs_by[ev], y_by[ev], by_subj, obj_idx, V_eff) for ev in EVAL_MODES}
    zero_mask = {ev: np.zeros((len(y_by[ev]), V_eff), dtype=bool) for ev in EVAL_MODES}

    log_prior = compute_log_prior(y_train, V_eff)
    assert np.allclose(log_prior, compute_log_prior(y_shuf, V_eff)), \
        "LOG_PRIOR_ARM_VARIANCE: shuffle must preserve object multiset -> identical prior"

    score_mats: Dict[str, Dict[str, Dict[str, np.ndarray]]] = {s: {a: {} for a in ARMS} for s in SCORER_SLOTS}

    Ps, Po = ref._proj_pair(d, fdf, ref.PROJ_SEED)
    Wr, Ws = ref.fit_scorer_paired(Fa, y_train, y_shuf, Fo, Ps, Po, fsteps,
                                   ref.SCORER_LR, ref.SCORER_TAU, ref.SCORER_L2)
    for ev in EVAL_MODES:
        score_mats["FROZEN"]["REAL"][ev] = ref.score_scorer(Fc_by[ev], Wr, Fo, Ps, Po)
        score_mats["FROZEN"]["SHUFFLED"][ev] = ref.score_scorer(Fc_by[ev], Ws, Fo, Ps, Po)

    init_seed = ref._stable_seed(f"{cfg['name']}|{relation}|{encoding}", salt=seed)
    jp = ref.joint_train_score(Fa, y_train, y_shuf, Fo, Fc_by, d, init_seed,
                               jh, jdf, jsteps, ref.JOINT_LR, ref.JOINT_WD, ref.JOINT_TAU, ref.JOINT_DROPOUT)
    for ev in EVAL_MODES:
        score_mats["JOINT"]["REAL"][ev] = jp["REAL"][ev]
        score_mats["JOINT"]["SHUFFLED"][ev] = jp["SHUFFLED"][ev]

    for ev in EVAL_MODES:
        score_mats["KNN"]["REAL"][ev] = ref.knn_scores(Fc_by[ev], Fa, y_train, V_eff, kk)
        score_mats["KNN"]["SHUFFLED"][ev] = ref.knn_scores(Fc_by[ev], Fa, y_shuf, V_eff, kk)

    metrics: Dict = {s: {a: {ev: {} for ev in EVAL_MODES} for a in ARMS} for s in SCORER_SLOTS}
    for slot in SCORER_SLOTS:
        tau_s = SLOT_TAU[slot]
        for arm in ARMS:
            for ev in EVAL_MODES:
                S = score_mats[slot][arm][ev]
                L = row_log_softmax(S, tau_s)
                yv = y_by[ev]
                var_out: Dict[str, Dict] = {}
                for var in RESCORE_VARIANTS:
                    # NONE ranks the RAW score S -> bit-exact reproduction of the parent reframe
                    # (log_softmax is row-monotone but the float32 round-trip flips near-ties, so
                    # ranking S directly is the faithful uncorrected baseline). Corrections rank L.
                    Sr = S if var == "NONE" else apply_rescore(L, var, RESCORE_K, log_prior, TAU_ADJ)
                    r_filt = ref.filtered_ranks(Sr, yv, filt_mask[ev])
                    r_raw = ref.filtered_ranks(Sr, yv, zero_mask[ev])
                    assert np.all(r_filt <= r_raw), \
                        f"FILTER_INVARIANT_VIOLATION {slot}|{arm}|{ev}|{var}: filtered > raw"
                    var_out[var] = {"filt": ref.rank_metrics(r_filt), "raw": ref.rank_metrics(r_raw)}
                metrics[slot][arm][ev] = var_out

    hub_diag = {"REAL": _winner_gini(score_mats["FROZEN"]["REAL"]["inductive"], V_eff),
                "SHUFFLED": _winner_gini(score_mats["FROZEN"]["SHUFFLED"]["inductive"], V_eff)}

    return {"metrics": metrics, "V_eff": V_eff, "m_eff": m_eff, "chance": 1.0 / V_eff,
            "n_ind": len(y_ind), "n_trans": len(y_trans), "hub_diag": hub_diag,
            "score_digests": {f"{sl}|{ar}|inductive": hashlib.sha256(
                np.ascontiguousarray(score_mats[sl][ar]["inductive"]).tobytes()).hexdigest()
                for sl in SCORER_SLOTS for ar in ARMS}}


# ============================================================================
# Synthetic discriminator-fires controls
# ============================================================================
def _rescore_metrics(Lr: np.ndarray, Ls: np.ndarray, yC: np.ndarray, V: int, log_prior_logit: np.ndarray) -> Dict:
    """Per-variant REAL/SHUF abs + rms metrics + lifts over NONE. Lr may carry an injected hub."""
    T = Lr.shape[0]
    fm = np.zeros((T, V), dtype=bool)
    kk = int(min(RESCORE_K, V))
    by = {}
    for var in RESCORE_VARIANTS:
        rr = ref.rank_metrics(ref.filtered_ranks(apply_rescore(Lr, var, kk, log_prior_logit, TAU_ADJ), yC, fm))
        rs = ref.rank_metrics(ref.filtered_ranks(apply_rescore(Ls, var, kk, log_prior_logit, TAU_ADJ), yC, fm))
        by[var] = {"real_h1": rr["hits1"], "shuf_h1": rs["hits1"], "real_mrr": rr["mrr"],
                   "rms_h1": rr["hits1"] - rs["hits1"], "rms_mrr": rr["mrr"] - rs["mrr"]}
    lifts = {var: {"real_h1_lift": by[var]["real_h1"] - by["NONE"]["real_h1"],
                   "shuf_h1_lift": by[var]["shuf_h1"] - by["NONE"]["shuf_h1"],
                   "rms_h1_lift": by[var]["rms_h1"] - by["NONE"]["rms_h1"],
                   "rms_mrr_lift": by[var]["rms_mrr"] - by["NONE"]["rms_mrr"]} for var in RESCORE_VARIANTS}
    return {"by_variant": {k: {a: round(float(b), 4) for a, b in v.items()} for k, v in by.items()},
            "lifts": {k: {a: round(float(b), 4) for a, b in v.items()} for k, v in lifts.items()}}


def _train_synth(seed_off: int, df: int, steps: int, y_relabel_frac: float = 0.0, relabel_seed: int = 0):
    """Clean linear-content map; optionally relabel a fraction of TRAIN to object 0 (label-prior hub)."""
    d, V, M, T = SCM_D, SCM_V, SCM_M, SCM_TEST
    Fs, yA, Fc, yC, Fo = ref._gen_linear_content(seed_off, d, V, M, T)
    yA2 = yA.copy()
    if y_relabel_frac > 0.0:
        rr = np.random.RandomState(relabel_seed)
        yA2[rr.choice(M, int(y_relabel_frac * M), replace=False)] = 0
    ish = np.random.RandomState(seed_off + 991).permutation(M)
    Ps, Po = ref._proj_pair(d, df, ref.PROJ_SEED)
    Wr, Ws = ref.fit_scorer_paired(Fs, yA2, yA2[ish], Fo, Ps, Po, steps,
                                   ref.SCORER_LR, ref.SCORER_TAU, ref.SCORER_L2)
    Lr = row_log_softmax(ref.score_scorer(Fc, Wr, Fo, Ps, Po), ref.SCORER_TAU)
    Ls = row_log_softmax(ref.score_scorer(Fc, Ws, Fo, Ps, Po), ref.SCORER_TAU)
    return Lr, Ls, yC, V, compute_log_prior(yA2, V)


def synth_csls_hub_veneer(seed: int) -> Dict:
    """POSITIVE control: strong clean map + additive density hub injected into REAL log-probs ONLY.
    CSLS (density) must recover REAL rank-1 while SHUFFLED is untouched -> rms lifts (instrument fires)."""
    Lr, Ls, yC, V, _ = _train_synth(seed + 111, SYNTH_STRONG_DF, SYNTH_STRONG_STEPS)
    Lr = Lr.copy()
    Lr[:, :VENEER_HN] += VENEER_B                 # inject density hub into REAL only
    lp_uniform = np.zeros(V, dtype=np.float32)    # uniform freq -> LOGIT ~inert; CSLS must carry it
    out = _rescore_metrics(Lr, Ls, yC, V, lp_uniform)
    out["hub_win_share_none"] = round(float((np.argmax(Lr, axis=1) < VENEER_HN).mean()), 4)
    return out


def synth_hub_null(seed: int) -> Dict:
    """NULL control: strong clean map, NO hub. Rescore must not manufacture/destroy signal."""
    Lr, Ls, yC, V, _ = _train_synth(seed + 222, SYNTH_STRONG_DF, SYNTH_STRONG_STEPS)
    lp_uniform = np.zeros(V, dtype=np.float32)
    out = _rescore_metrics(Lr, Ls, yC, V, lp_uniform)
    out["hub_win_share_none"] = 0.0
    return out


def synth_label_hub_shared(seed: int) -> Dict:
    """DIAGNOSTIC (reported): shared label-prior hub (40% train relabeled to obj0). Documents that the
    paired rms cancels label-prior (SHUFFLED already subtracts it) -> ~0 lift by construction."""
    Lr, Ls, yC, V, lp = _train_synth(seed + 5555, SCORER_DF_SYNTH, max(SYNTH_WEAK_STEPS, 300),
                                     y_relabel_frac=LABEL_RELABEL_FRAC, relabel_seed=seed + 13)
    out = _rescore_metrics(Lr, Ls, yC, V, lp)          # lp is the skewed prior (LOGIT gets the info)
    out["hub_win_share_none"] = round(float((np.argmax(Lr, axis=1) == 0).mean()), 4)
    return out


# ============================================================================
# arms-differ hash (META_RULE_AF)
# ============================================================================
def arms_differ_check(seed: int) -> Tuple[bool, Dict[str, str]]:
    Lr, Ls, yC, V, lp = _train_synth(seed + 555, SCORER_DF_SYNTH, 300)
    kk = int(min(RESCORE_K, V))
    preds: Dict[str, np.ndarray] = {}
    for var in RESCORE_VARIANTS:
        preds[f"REAL_{var}"] = apply_rescore(Lr, var, kk, lp, TAU_ADJ)
        preds[f"SHUF_{var}"] = apply_rescore(Ls, var, kk, lp, TAU_ADJ)
    digests = {k: hashlib.sha256(np.ascontiguousarray(v).tobytes()).hexdigest() for k, v in preds.items()}
    req = [("REAL_NONE", "REAL_CSLS"), ("REAL_NONE", "REAL_LOGIT"), ("REAL_CSLS", "REAL_BOTH"),
           ("REAL_LOGIT", "REAL_BOTH"), ("REAL_NONE", "SHUF_NONE"), ("REAL_BOTH", "SHUF_BOTH")]
    ok = all(digests[a] != digests[b] for a, b in req)
    return ok, digests


# ============================================================================
# Per-seed driver (failure-instrumented; no silent continue)
# ============================================================================
def _unit_key(cn, rel, enc, slot, arm, ev):
    return f"{cn}|{rel}|{enc}|{slot}|{arm}|{ev}"


def _flatten_unit(per_unit, cn, rel, enc, slot, arm, ev, var_metrics, fc):
    per_unit[_unit_key(cn, rel, enc, slot, arm, ev)] = {
        "config": cn, "relation": rel, "encoding": enc, "mech": slot, "arm": arm, "eval": ev,
        "variants": var_metrics, "failure_class": fc}


def _rms_re(per_unit, cn, rel, enc, slot, var, metric, ev="inductive"):
    r = per_unit.get(_unit_key(cn, rel, enc, slot, "REAL", ev))
    s = per_unit.get(_unit_key(cn, rel, enc, slot, "SHUFFLED", ev))
    if not r or not s or r.get("variants") is None or s.get("variants") is None:
        return float("nan")
    rv = r["variants"].get(var); sv = s["variants"].get(var)
    if not rv or not sv or rv.get("filt") is None or sv.get("filt") is None:
        return float("nan")
    return rv["filt"][metric] - sv["filt"][metric]


def _print_cfg_progress(cfg, per_unit, seed):
    cn = cfg["name"]; rel = cfg["rels"][0]; enc = cfg["encs"][0]
    for slot in ("FROZEN", "JOINT"):
        none_mrr = _rms_re(per_unit, cn, rel, enc, slot, "NONE", "mrr")
        vals = [(_rms_re(per_unit, cn, rel, enc, slot, v, "mrr"), v) for v in RESCORE_ARMS_HP]
        best_mrr, best_v = max(((m, v) for m, v in vals if m == m), default=(float("nan"), "-"))
        none_h1 = _rms_re(per_unit, cn, rel, enc, slot, "NONE", "hits1")
        best_h1 = max((_rms_re(per_unit, cn, rel, enc, slot, v, "hits1") for v in RESCORE_ARMS_HP
                       if _rms_re(per_unit, cn, rel, enc, slot, v, "hits1") ==
                       _rms_re(per_unit, cn, rel, enc, slot, v, "hits1")), default=float("nan"))
        print(f"  [seed={seed} {cn:<6} {rel[:11]:<11} {enc[:4]} {slot:<6}] MRR rms NONE={none_mrr:+.3f}"
              f"->best({best_v})={best_mrr:+.3f}(lift{best_mrr-none_mrr:+.3f}) | Hits@1 rms NONE={none_h1:+.3f}"
              f" best={best_h1:+.3f}(lift{best_h1-none_h1:+.3f})", flush=True)


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
    hub_diag_all: Dict[str, Dict] = {}
    fatal = False
    fatal_msg = None
    unit_i = 0
    for cfg in CONFIGS:
        cn = cfg["name"]
        for relation in cfg["rels"]:
            for enc in cfg["encs"]:
                fc = None
                res = None
                try:
                    res = eval_config_relenc(cfg, relation, enc, seed)
                except ref.ContentUnavailable as e:
                    fc = str(e)
                except ref.JointUnavailable as e:
                    fc = str(e)
                except Exception as e:
                    fatal = True
                    fatal_msg = f"{cn}|{relation}|{enc}:{type(e).__name__}:{str(e)[:200]}"
                    print(f"  [seed={seed} {cn} {relation} {enc}] FAILED {type(e).__name__}: {e}", flush=True)
                    traceback.print_exc()
                    break
                for slot in SCORER_SLOTS:
                    for arm in ARMS:
                        for ev in EVAL_MODES:
                            vm = res["metrics"][slot][arm][ev] if res is not None else None
                            _flatten_unit(per_unit, cn, relation, enc, slot, arm, ev, vm, fc)
                if res is not None:
                    k = f"{cn}|{relation}|{enc}"
                    meta[k] = {"V_eff": res["V_eff"], "m_eff": res["m_eff"], "chance": res["chance"],
                               "n_ind": res["n_ind"], "n_trans": res["n_trans"],
                               "score_digests": res["score_digests"]}
                    hub_diag_all[k] = res["hub_diag"]
                unit_i += 1
                _emit_heartbeat(out_dir, unit_i, len(CONFIGS), t0)
            if fatal:
                break
        if fatal:
            break
        _print_cfg_progress(cfg, per_unit, seed)

    ven = synth_csls_hub_veneer(seed)
    null = synth_hub_null(seed)
    lab = synth_label_hub_shared(seed)
    print(f"  [seed={seed} SYNTH veneer(POS)] hub_share={ven['hub_win_share_none']:.2f} "
          f"CSLS REAL_h1_lift={ven['lifts']['CSLS']['real_h1_lift']:+.3f} rms_h1_lift={ven['lifts']['CSLS']['rms_h1_lift']:+.3f} "
          f"SHUF_h1_lift={ven['lifts']['CSLS']['shuf_h1_lift']:+.3f} (LOGIT rms_h1={ven['lifts']['LOGIT']['rms_h1_lift']:+.3f})", flush=True)
    print(f"  [seed={seed} SYNTH null      ] BOTH rms_h1_lift={null['lifts']['BOTH']['rms_h1_lift']:+.3f} "
          f"rms_mrr_lift={null['lifts']['BOTH']['rms_mrr_lift']:+.3f}", flush=True)
    print(f"  [seed={seed} SYNTH label(diag)] share={lab['hub_win_share_none']:.2f} "
          f"BOTH rms_mrr_lift={lab['lifts']['BOTH']['rms_mrr_lift']:+.3f} (paired cancellation demo)", flush=True)

    return {
        "seed": seed, "N": N_DIM, "run_mode": RUN_MODE, "device": _DEVICE, "torch_ok": _TORCH_OK,
        "config_version": f"ANCHOR={ANCHOR_NAME},N={N_DIM},configs={len(CONFIGS)},seeds={SEEDS}",
        "per_unit": per_unit, "meta": meta, "hub_diag": hub_diag_all,
        "synth_csls_hub_veneer": ven, "synth_hub_null": null, "synth_label_hub_shared": lab,
        "fatal": fatal, "fatal_msg": fatal_msg, "elapsed_s": time.time() - t0,
    }


# ============================================================================
# Aggregate + verdict
# ============================================================================
def _mean(vals: List[float]) -> float:
    v = [x for x in vals if x == x]
    return float(np.mean(v)) if v else float("nan")


def aggregate(per_seed: Dict) -> Dict:
    buckets: Dict[str, List[float]] = collections.defaultdict(list)
    n_units = 0; n_failed = 0
    enc_unavailable = collections.Counter(); joint_unavailable = 0
    meta_all: Dict[str, Dict] = {}
    hub_all: Dict[str, List[Dict]] = collections.defaultdict(list)
    ctrl_stores = {t: collections.defaultdict(list) for t in
                   ("synth_csls_hub_veneer", "synth_hub_null", "synth_label_hub_shared")}
    for sd in per_seed.values():
        for key, rec in sd.get("per_unit", {}).items():
            n_units += 1
            if rec.get("variants") is None:
                n_failed += 1
                fcx = rec.get("failure_class", "NA")
                if isinstance(fcx, str) and "CACHE_MISSING" in fcx:
                    enc_unavailable[rec.get("encoding", "?")] += 1
                elif isinstance(fcx, str) and "JOINT_TORCH_UNAVAILABLE" in fcx:
                    joint_unavailable += 1
                continue
            for var in RESCORE_VARIANTS:
                vm = rec["variants"].get(var)
                if not vm:
                    continue
                for proto in ("filt", "raw"):
                    for mk in METRIC_KEYS:
                        buckets[f"{key}|{var}|{proto}|{mk}"].append(float(vm[proto][mk]))
        for mk, mv in sd.get("meta", {}).items():
            meta_all[mk] = mv
        for mk, mv in sd.get("hub_diag", {}).items():
            hub_all[mk].append(mv)
        for tag, store in ctrl_stores.items():
            s = sd.get(tag)
            if s:
                for var in RESCORE_VARIANTS:
                    for lk, lv in s["lifts"][var].items():
                        store[f"{var}|{lk}"].append(lv)
                store["hub_win_share_none"].append(s.get("hub_win_share_none", 0.0))
    cells = {key: _mean(v) for key, v in buckets.items()}
    cells_n = {key: len([x for x in v if x == x]) for key, v in buckets.items()}
    return {
        "cells": cells, "cells_n": cells_n, "n_units": n_units, "n_units_failed": n_failed,
        "enc_unavailable": dict(enc_unavailable), "joint_unavailable": joint_unavailable,
        "meta": meta_all, "hub_diag": {k: v for k, v in hub_all.items()},
        "synth_csls_hub_veneer": {k: round(_mean(v), 4) for k, v in ctrl_stores["synth_csls_hub_veneer"].items()},
        "synth_hub_null": {k: round(_mean(v), 4) for k, v in ctrl_stores["synth_hub_null"].items()},
        "synth_label_hub_shared": {k: round(_mean(v), 4) for k, v in ctrl_stores["synth_label_hub_shared"].items()},
    }


def compute_verdict(agg: Dict, arms_differ_ok: bool, bind_rt: float) -> Tuple[str, str, Dict]:
    cells = agg["cells"]; meta = agg["meta"]
    good_units = agg["n_units"] - agg["n_units_failed"]
    ven = agg["synth_csls_hub_veneer"]; null = agg["synth_hub_null"]
    lab = agg["synth_label_hub_shared"]

    def _pu(cn, rel, enc, slot, var, metric, ev="inductive"):
        ri = cells.get(f"{cn}|{rel}|{enc}|{slot}|REAL|{ev}|{var}|filt|{metric}", float("nan"))
        si = cells.get(f"{cn}|{rel}|{enc}|{slot}|SHUFFLED|{ev}|{var}|filt|{metric}", float("nan"))
        if ri != ri or si != si:
            return float("nan")
        return ri - si

    def _mx(*xs):
        v = [x for x in xs if x == x]
        return max(v) if v else float("nan")
    ven_real = _mx(ven.get("CSLS|real_h1_lift", float("nan")), ven.get("BOTH|real_h1_lift", float("nan")))
    ven_rms = _mx(ven.get("CSLS|rms_h1_lift", float("nan")), ven.get("BOTH|rms_h1_lift", float("nan")))
    ven_shuf = ven.get("CSLS|shuf_h1_lift", 1.0)
    veneer_fires = (ven_real >= SYNTH_FIRE_H1_LIFT and ven_rms >= SYNTH_FIRE_RMS_LIFT
                    and ven_shuf <= SYNTH_SHUF_MAX_LIFT)
    null_clean = (abs(null.get("BOTH|rms_h1_lift", 1.0)) <= SYNTH_NULL_TOL
                  and abs(null.get("BOTH|rms_mrr_lift", 1.0)) <= SYNTH_NULL_TOL)
    discriminator_fires = bool(veneer_fires and null_clean)

    V300_PLUS = {"V300", "V1000"}
    records = []
    for cfg in CONFIGS:
        cn = cfg["name"]
        for rel in cfg["rels"]:
            is_sem = rel in RELATIONS_SEM
            for enc in cfg["encs"]:
                ch = float(meta.get(f"{cn}|{rel}|{enc}", {}).get("chance", float("nan")))
                if _pu(cn, rel, enc, "FROZEN", "NONE", "hits10") != _pu(cn, rel, enc, "FROZEN", "NONE", "hits10") \
                   and _pu(cn, rel, enc, "JOINT", "NONE", "hits10") != _pu(cn, rel, enc, "JOINT", "NONE", "hits10"):
                    continue
                per_slot = {}
                cell_wins = False
                best_mrr_lift = float("-inf")
                best_real_mrr_lift = float("-inf")
                for slot in HP_SLOTS:
                    none_mrr = _pu(cn, rel, enc, slot, "NONE", "mrr")
                    none_h1 = _pu(cn, rel, enc, slot, "NONE", "hits1")
                    real_mrr_none = cells.get(f"{cn}|{rel}|{enc}|{slot}|REAL|inductive|NONE|filt|mrr", float("nan"))
                    var_stats = {}
                    for var in RESCORE_ARMS_HP:
                        mrr_rms = _pu(cn, rel, enc, slot, var, "mrr")
                        h1_rms = _pu(cn, rel, enc, slot, var, "hits1")
                        h10_rms = _pu(cn, rel, enc, slot, var, "hits10")
                        shuf_none = cells.get(f"{cn}|{rel}|{enc}|{slot}|SHUFFLED|inductive|NONE|filt|hits1", float("nan"))
                        shuf_var = cells.get(f"{cn}|{rel}|{enc}|{slot}|SHUFFLED|inductive|{var}|filt|hits1", float("nan"))
                        real_none = cells.get(f"{cn}|{rel}|{enc}|{slot}|REAL|inductive|NONE|filt|hits1", float("nan"))
                        real_var = cells.get(f"{cn}|{rel}|{enc}|{slot}|REAL|inductive|{var}|filt|hits1", float("nan"))
                        real_mrr_var = cells.get(f"{cn}|{rel}|{enc}|{slot}|REAL|inductive|{var}|filt|mrr", float("nan"))
                        mrr_lift = (mrr_rms - none_mrr) if (mrr_rms == mrr_rms and none_mrr == none_mrr) else float("nan")
                        h1_lift = (h1_rms - none_h1) if (h1_rms == h1_rms and none_h1 == none_h1) else float("nan")
                        # HONEST rank-1 sharpening: REAL-absolute lifts (not gameable by SHUFFLED-collapse)
                        real_h1_lift = (real_var - real_none) if (real_var == real_var and real_none == real_none) else float("nan")
                        real_mrr_lift = (real_mrr_var - real_mrr_none) if (real_mrr_var == real_mrr_var and real_mrr_none == real_mrr_none) else float("nan")
                        shuf_h1_lift = (shuf_var - shuf_none) if (shuf_var == shuf_var and shuf_none == shuf_none) else float("nan")
                        # HARD_PASS requires the rms improvement to be REAL-DRIVEN: REAL rank-1 must NOT
                        # degrade (real_h1_lift >= -tol). Without this a SHUFFLED-collapse (rescore crushing
                        # the popularity control) inflates the paired rms into a PHANTOM win. exp_dev 2026-07-05.
                        clears = (mrr_rms == mrr_rms and h1_lift == h1_lift and h10_rms == h10_rms
                                  and real_h1_lift == real_h1_lift
                                  and mrr_rms >= HP_MRR_RMS_MIN and h1_lift >= HP_HITS1_LIFT_MIN
                                  and h10_rms >= HP_HITS10_NONREG_MIN
                                  and real_h1_lift >= REAL_NONDEGRADE_TOL)
                        if clears:
                            cell_wins = True
                        if mrr_lift == mrr_lift:
                            best_mrr_lift = max(best_mrr_lift, mrr_lift)
                        if real_mrr_lift == real_mrr_lift:
                            best_real_mrr_lift = max(best_real_mrr_lift, real_mrr_lift)
                        shuf_collapse = bool(shuf_h1_lift == shuf_h1_lift and shuf_h1_lift <= -0.05
                                             and (real_h1_lift != real_h1_lift or real_h1_lift < HP_HITS1_LIFT_MIN))
                        var_stats[var] = {
                            "mrr_rms": _r(mrr_rms), "hits1_rms": _r(h1_rms), "hits10_rms": _r(h10_rms),
                            "mrr_rms_lift": _r(mrr_lift), "hits1_rms_lift": _r(h1_lift),
                            "real_hits1_lift": _r(real_h1_lift), "real_mrr_lift": _r(real_mrr_lift),
                            "shuf_hits1_lift": _r(shuf_h1_lift), "shuffled_collapse_phantom": shuf_collapse,
                            "clears_HP": bool(clears)}
                    per_slot[slot] = {"none_mrr_rms": _r(none_mrr), "none_hits1_rms": _r(none_h1),
                                      "corrections": var_stats}
                shuf_h10 = cells.get(f"{cn}|{rel}|{enc}|FROZEN|SHUFFLED|inductive|NONE|filt|hits10", float("nan"))
                records.append({
                    "config": cn, "V": cfg["V"], "rel": rel, "enc": enc, "is_sem": is_sem,
                    "is_neg_watchdog": rel in RELATIONS_NEG, "chance": ch,
                    "per_slot": per_slot, "cell_wins": cell_wins,
                    "best_mrr_rms_lift": _r(best_mrr_lift if best_mrr_lift != float("-inf") else float("nan")),
                    "best_real_mrr_lift": _r(best_real_mrr_lift if best_real_mrr_lift != float("-inf") else float("nan")),
                    "shuf_hits10_none_filt": _r(shuf_h10),
                    "hub_diag": (agg["hub_diag"].get(f"{cn}|{rel}|{enc}", [{}]) or [{}])[0]})

    wins = [r for r in records if r["is_sem"] and r["config"] in V300_PLUS and r["cell_wins"]]
    win_rels = sorted(set(r["rel"] for r in wins))
    win_encs = sorted(set(r["enc"] for r in wins))
    expansion_met = len(win_rels) >= 2 and len(win_encs) >= 2

    v300_sem = [r for r in records if r["is_sem"] and r["config"] in V300_PLUS]
    best_mrr_lift_v300 = max((r["best_mrr_rms_lift"] for r in v300_sem
                              if r["best_mrr_rms_lift"] is not None), default=float("nan"))
    best_real_mrr_lift_v300 = max((r["best_real_mrr_lift"] for r in v300_sem
                                   if r["best_real_mrr_lift"] is not None), default=float("nan"))

    diag = {
        "bind_roundtrip": bind_rt, "arms_differ_ok": arms_differ_ok,
        "good_units": good_units, "expected_n_units": EXPECTED_N_UNITS,
        "synth_csls_hub_veneer": ven, "synth_hub_null": null, "synth_label_hub_shared": lab,
        "veneer_control_fires": bool(veneer_fires), "null_control_clean": bool(null_clean),
        "discriminator_fires": discriminator_fires,
        "records": records, "wins": wins, "win_rels": win_rels, "win_encs": win_encs,
        "expansion_criterion_met": expansion_met,
        "best_mrr_rms_lift_at_V300plus": _r(best_mrr_lift_v300),
        "best_real_mrr_lift_at_V300plus": _r(best_real_mrr_lift_v300),
        "hub_diag": agg["hub_diag"], "enc_unavailable": agg["enc_unavailable"],
        "joint_unavailable": agg["joint_unavailable"], "device": _DEVICE,
    }

    expected = EXPECTED_N_UNITS
    if good_units < expected:
        gsbc_missing = agg["enc_unavailable"].get("gsbc", 0)
        if not (gsbc_missing > 0 and (good_units + gsbc_missing) >= expected):
            return ("HARD_FAIL",
                    f"HARD_FAIL_CARDINALITY_BREACH_META_RULE_H: good_units={good_units} < expected={expected} "
                    f"(not explained by gsbc-cache-missing).", diag)
    if not arms_differ_ok:
        return ("HARD_FAIL", "META_RULE_AF_VIOLATION: rescore-variant matrices bit-identical; impl bug.", diag)
    if not (bind_rt >= BIND_ROUNDTRIP_MIN):
        return ("HARD_FAIL", f"SANITY_RAIL_BIND: bind-roundtrip={bind_rt:.3f} < {BIND_ROUNDTRIP_MIN}.", diag)

    summ = (f"dev={_DEVICE} discrim[veneer_fires={veneer_fires}(CSLS REALh1lift={ven.get('CSLS|real_h1_lift')},"
            f"rmsh1lift={ven.get('CSLS|rms_h1_lift')},SHUFlift={ven.get('CSLS|shuf_h1_lift')}),"
            f"null_clean={null_clean}] | label_shared_rms_mrr_lift={lab.get('BOTH|rms_mrr_lift')}(cancel-demo) "
            f"| V300+ best_MRR_rms_lift={diag['best_mrr_rms_lift_at_V300plus']} (may be SHUFFLED-collapse) "
            f"best_REAL_MRR_lift={diag['best_real_mrr_lift_at_V300plus']} (honest rank-1 sharpening) "
            f"win_rels={win_rels} win_encs={win_encs}")

    if not discriminator_fires:
        return ("MIDDLE_BAND",
                f"MIDDLE_BAND_VACUOUS_DISCRIMINATOR: the rescore did NOT pass the synthetic controls "
                f"(veneer_fires={veneer_fires}, null_clean={null_clean}); real-data lift uninterpretable "
                f"until the correction provably recovers rank-1 on a by-construction fixable hub AND reports "
                f"~0 when no hub is present. {summ}", diag)

    if expansion_met:
        return ("HARD_PASS",
                f"HARD_PASS_RESCORE_SHARPENS_RANK1: training-free post-hoc rescore (CSLS+logit-adjust) "
                f"converts the MIDDLE_BAND into a broad win -- best-of-{{FROZEN,JOINT}}x{{CSLS,LOGIT,BOTH}} "
                f"filtered inductive real_minus_shuf clears MRR>={HP_MRR_RMS_MIN} AND Hits@1 rms lift>="
                f"{HP_HITS1_LIFT_MIN} AND Hits@10 rms>={HP_HITS10_NONREG_MIN} AND REAL-abs Hits@1 does NOT "
                f"degrade (anti-phantom), spanning relations={win_rels} x encoders={win_encs} at V>=300. {summ}",
                diag)

    if best_real_mrr_lift_v300 == best_real_mrr_lift_v300 and best_real_mrr_lift_v300 <= HF_MRR_LIFT_MAX:
        return ("HARD_FAIL",
                f"HARD_FAIL_RESCORE_DOES_NOT_SHARPEN_REAL_RANK1: the training-free hub/label-prior rescore "
                f"fails to lift REAL-absolute MRR over the uncorrected reframe on EVERY semantic rel x enc at "
                f"V>=300 (best REAL-abs MRR lift={diag['best_real_mrr_lift_at_V300plus']} <= {HF_MRR_LIFT_MAX}) "
                f"while the synthetic veneer control fired. Any positive paired-rms MRR lift "
                f"(={diag['best_mrr_rms_lift_at_V300plus']}) is SHUFFLED-collapse (rescore crushing the "
                f"popularity control), NOT rank-1 sharpening. Consistent with paired-rms cancellation of "
                f"shared label-prior + deep-truth; redirect to trained hard-negative mining (DPR/ANCE) or "
                f"richer content. {summ}", diag)

    return ("MIDDLE_BAND",
            f"MIDDLE_BAND_PARTIAL_RANK1_SHARPEN: the training-free rescore moves MRR rms over the uncorrected "
            f"reframe (best MRR rms lift={diag['best_mrr_rms_lift_at_V300plus']} at V>=300, in "
            f"(+{HF_MRR_LIFT_MAX},+{HP_MRR_RMS_MIN}) or Hits@1 lifts but MRR short of {HP_MRR_RMS_MIN} on one "
            f"relation) -- real but partial. Stage trained complements (train-time logit-adjust loss for "
            f"label-prior relations; DPR/ANCE hard-neg mining for geometric-hub relations). {summ}", diag)


# ============================================================================
# Formula self-tests (import time, fast)
# ============================================================================
def _test_csls_coef1_formula():
    L = np.array([[-0.1, -2.0, -1.0], [-1.5, -0.2, -3.0]], dtype=np.float32)
    out = apply_rescore(L, "CSLS", 1, np.zeros(3, dtype=np.float32), 1.0)
    # k=1: r_row=max per row=[-0.1,-0.2]; r_col=max per col=[-0.1,-0.2,-1.0]; CSLS=L-r_row-r_col
    exp = np.array([[0.1, -1.7, 0.1], [-1.2, 0.2, -1.8]], dtype=np.float32)
    assert np.allclose(out, exp, atol=1e-4), f"CSLS coef1 k=1 {out.tolist()} != {exp.tolist()}"
    assert np.allclose(apply_rescore(L, "NONE", 1, np.zeros(3, dtype=np.float32), 1.0), L), "NONE != identity"
    # coef-1 CSLS removes a pure additive column bias from the WITHIN-ROW RANKING (the mechanistic
    # property Hits@k/MRR depend on): CSLS(L+c) = CSLS(L) + per-row-constant -> identical row argsort.
    # (Value equality does NOT hold when the biased column becomes the row-max and shifts r_row, but
    # r_row is rank-inert per row, so the ordering is preserved.)
    Lw = np.array([[-0.1, -2.0, -1.0, -0.5], [-1.5, -0.2, -3.0, -0.9],
                   [-0.3, -0.7, -1.2, -2.5]], dtype=np.float32)
    c = np.array([0.0, 6.0, 0.0, 0.0], dtype=np.float32)
    a = apply_rescore(Lw, "CSLS", 2, np.zeros(4, dtype=np.float32), 1.0)
    b = apply_rescore(Lw + c[None, :], "CSLS", 2, np.zeros(4, dtype=np.float32), 1.0)
    for t in range(Lw.shape[0]):
        assert np.array_equal(np.argsort(-a[t]), np.argsort(-b[t])), \
            f"coef-1 CSLS must preserve within-row ranking under additive column bias (row {t})"
    # and the per-row difference is a constant (col-bias exactly cancelled up to a row offset)
    dd = b - a
    assert np.allclose(dd, dd[:, :1], atol=1e-4), "CSLS(L+c) - CSLS(L) must be a per-row constant"


def _test_csls_canonical_2x_reference():
    L = np.array([[-0.1, -2.0, -1.0], [-1.5, -0.2, -3.0]], dtype=np.float32)
    out = csls_canonical_2x(L, 1)
    exp = np.array([[0.0, -3.7, -0.9], [-2.7, 0.0, -4.8]], dtype=np.float32)  # 2L - r_row - r_col
    assert np.allclose(out, exp, atol=1e-4), f"canonical 2x CSLS {out.tolist()} != {exp.tolist()}"


def _test_logit_formula():
    L = np.array([[-0.1, -2.0, -1.0], [-1.5, -0.2, -3.0]], dtype=np.float32)
    lp = np.array([0.0, -1.0, -2.0], dtype=np.float32)
    out = apply_rescore(L, "LOGIT", 1, lp, 1.0)
    exp = np.array([[-0.1, -1.0, 1.0], [-1.5, 0.8, -1.0]], dtype=np.float32)
    assert np.allclose(out, exp, atol=1e-4), f"LOGIT {out.tolist()} != {exp.tolist()}"
    both = apply_rescore(L, "BOTH", 1, lp, 1.0)
    csls = apply_rescore(L, "CSLS", 1, np.zeros(3, dtype=np.float32), 1.0)
    assert np.allclose(both, csls - lp[None, :], atol=1e-4), "BOTH != CSLS - tau*log_prior"


def _test_log_softmax_row_monotone():
    rng = np.random.RandomState(7)
    S = rng.standard_normal((5, 8)).astype(np.float32)
    L = row_log_softmax(S, 0.05)
    for t in range(5):
        assert np.array_equal(np.argsort(-S[t]), np.argsort(-L[t])), "log_softmax broke row order"
    assert np.allclose(np.exp(L).sum(axis=1), 1.0, atol=1e-4), "log_softmax rows do not sum to 1"


def _test_log_prior_shuffle_invariant():
    rng = np.random.RandomState(3)
    y = rng.randint(0, 6, 40)
    assert np.allclose(compute_log_prior(y, 6), compute_log_prior(y[rng.permutation(40)], 6)), \
        "log_prior not shuffle-invariant"


def _formula_selftests() -> float:
    rng = np.random.RandomState(123)
    n = 512
    a = np.exp(1j * rng.uniform(-np.pi, np.pi, n)).astype(np.complex64)
    b = np.exp(1j * rng.uniform(-np.pi, np.pi, n)).astype(np.complex64)
    rt = ref.cos_c(ref.unbind(ref.bind(a, b), a), b)
    assert rt >= 0.90, f"selftest1 bind-roundtrip cos={rt}"

    _test_csls_coef1_formula()
    _test_csls_canonical_2x_reference()
    _test_logit_formula()
    _test_log_softmax_row_monotone()
    _test_log_prior_shuffle_invariant()

    ven = synth_csls_hub_veneer(0)
    vr = max(ven["lifts"]["CSLS"]["real_h1_lift"], ven["lifts"]["BOTH"]["real_h1_lift"])
    vrms = max(ven["lifts"]["CSLS"]["rms_h1_lift"], ven["lifts"]["BOTH"]["rms_h1_lift"])
    assert vr >= SYNTH_FIRE_H1_LIFT, f"selftest veneer REAL Hits@1 lift={vr:+.3f} < {SYNTH_FIRE_H1_LIFT}"
    assert vrms >= SYNTH_FIRE_RMS_LIFT, f"selftest veneer rms Hits@1 lift={vrms:+.3f} < {SYNTH_FIRE_RMS_LIFT}"
    assert ven["lifts"]["CSLS"]["shuf_h1_lift"] <= SYNTH_SHUF_MAX_LIFT, \
        f"selftest veneer SHUFFLED lifted {ven['lifts']['CSLS']['shuf_h1_lift']:+.3f} > {SYNTH_SHUF_MAX_LIFT} (artifact)"
    null = synth_hub_null(0)
    assert abs(null["lifts"]["BOTH"]["rms_h1_lift"]) <= SYNTH_NULL_TOL, \
        f"selftest null BOTH rms Hits@1 lift={null['lifts']['BOTH']['rms_h1_lift']:+.3f} not <= {SYNTH_NULL_TOL}"

    ad_ok, _ = arms_differ_check(0)
    assert ad_ok, "selftest arms_differ_check failed (rescore variants identical)"

    print(f"[formula_selftest] bind_rt={rt:.3f} CSLS_coef1=PASS CSLS_2x_ref=PASS LOGIT=PASS "
          f"log_softmax_monotone=PASS log_prior_shuffle_inv=PASS | veneer(REALh1lift{vr:+.2f},rmsh1lift{vrms:+.2f},"
          f"SHUFlift{ven['lifts']['CSLS']['shuf_h1_lift']:+.2f},LOGITrms{ven['lifts']['LOGIT']['rms_h1_lift']:+.2f}) "
          f"null(BOTHrmsh1{null['lifts']['BOTH']['rms_h1_lift']:+.2f}) arms_differ=OK torch_ok={_TORCH_OK} "
          f"device={_DEVICE} bge_ok={ref._BGE.ok} gsbc_ok={ref._GSBC.ok} PASS", flush=True)
    return rt


_BIND_RT = _formula_selftests()
assert HF_MRR_LIFT_MAX < HP_MRR_RMS_MIN < 0.95, "MRR bands must be ordered and below saturation"


# ============================================================================
# Defensive: start-marker + crash-diagnostic
# ============================================================================
def _write_start_marker(out_dir: Path):
    marker = {
        "pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR_NAME, "run_mode": RUN_MODE, "device": _DEVICE, "torch_ok": _TORCH_OK,
        "expected_n_units": EXPECTED_N_UNITS, "n_configs": len(CONFIGS), "host": platform.node(),
        "bge_ok": ref._BGE.ok, "gsbc_ok": ref._GSBC.ok,
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
          f"bge_ok={ref._BGE.ok} gsbc_ok={ref._GSBC.ok} k={RESCORE_K} tau_adj={TAU_ADJ}", flush=True)
    if not ref._GSBC.ok:
        print(f"[WARN] gsbc cache unavailable ({ref._GSBC.reason}); gsbc arm records per-unit "
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
    summary = (f"{verdict}: best_REAL_MRR_lift@V300+={diag.get('best_real_mrr_lift_at_V300plus')} "
               f"(honest) best_MRR_rms_lift@V300+={diag.get('best_mrr_rms_lift_at_V300plus')} (may be shuf-collapse) "
               f"win_rels={diag.get('win_rels')} win_encs={diag.get('win_encs')} "
               f"discrim_fires={diag.get('discriminator_fires')}")
    metrics = {
        "anchor": ANCHOR_NAME, "anchor_name": ANCHOR_NAME, "run_mode": RUN_MODE,
        "N": N_DIM, "N_DIM": N_DIM, "device": _DEVICE, "torch_ok": _TORCH_OK,
        "relations_semantic": RELATIONS_SEM, "relations_neg_watchdog": RELATIONS_NEG,
        "content_encodings": CONTENT_ENCODINGS, "arms": ARMS, "eval_modes": EVAL_MODES,
        "scorer_slots": SCORER_SLOTS, "hp_slots": HP_SLOTS, "rescore_variants": RESCORE_VARIANTS,
        "hits_ks": HITS_KS, "knn_k": _knn_k(), "rescore_k": RESCORE_K, "tau_adj": TAU_ADJ,
        "slot_tau": SLOT_TAU, "logit_eps": LOGIT_EPS, "csls_coefficient": 1,
        "config_grid": [{"name": c["name"], "V": c["V"], "M": c["M"], "rels": c["rels"],
                         "encs": c["encs"]} for c in CONFIGS],
        "reuses_parent": "experiments/exp_schema_relation_hitsatk_mrr_reframe_v1.py (imported verbatim as ref)",
        "n_seeds": len(per_seed), "seeds": [int(s) for s in per_seed.keys()],
        "expected_n_units": EXPECTED_N_UNITS, "n_units_counted": agg["n_units"],
        "n_units_failed": agg["n_units_failed"],
        "cardinality_ok": (agg["n_units"] - agg["n_units_failed"]) >= EXPECTED_N_UNITS
        or agg["enc_unavailable"].get("gsbc", 0) > 0,
        "arms_differ_verified": ad_ok, "arms_differ_digests": ad_digests, "bind_roundtrip": _BIND_RT,
        "synth_csls_hub_veneer": agg["synth_csls_hub_veneer"], "synth_hub_null": agg["synth_hub_null"],
        "synth_label_hub_shared": agg["synth_label_hub_shared"],
        "veneer_control_fires": diag.get("veneer_control_fires"),
        "null_control_clean": diag.get("null_control_clean"),
        "discriminator_fires": diag.get("discriminator_fires"),
        "records": diag.get("records"), "wins": diag.get("wins"),
        "win_rels": diag.get("win_rels"), "win_encs": diag.get("win_encs"),
        "expansion_criterion_met": diag.get("expansion_criterion_met"),
        "best_mrr_rms_lift_at_V300plus": diag.get("best_mrr_rms_lift_at_V300plus"),
        "best_real_mrr_lift_at_V300plus": diag.get("best_real_mrr_lift_at_V300plus"),
        "hub_diag_real_vs_shuffled_gini": agg["hub_diag"],
        "enc_unavailable": agg["enc_unavailable"], "joint_unavailable": agg["joint_unavailable"],
        "meta_per_relenc": agg["meta"],
        "hp_scope": {"best_of_FROZEN_JOINT_x_CSLS_LOGIT_BOTH_REAL_inductive_FILTERED_SEMANTIC_at_V>=300":
                     ["HARD_PASS", "HARD_FAIL", "MIDDLE_BAND"],
                     "NONE": ["pre_rescore_baseline_reproduces_parent_reframe_NOT_HP"],
                     "KNN": ["representation_signal_reference_NOT_HP"],
                     "DerivedFrom": ["surface_morphological_watchdog_contrast_NOT_HP"],
                     "SHUFFLED": ["popularity_marginal_control_artifact_guard"], "raw_metrics": ["reported_not_gating"]},
        "bands": {"HP_MRR_RMS_MIN": HP_MRR_RMS_MIN, "HP_HITS1_LIFT_MIN": HP_HITS1_LIFT_MIN,
                  "HP_HITS10_NONREG_MIN": HP_HITS10_NONREG_MIN, "HF_MRR_LIFT_MAX": HF_MRR_LIFT_MAX,
                  "SYNTH_FIRE_H1_LIFT": SYNTH_FIRE_H1_LIFT, "SYNTH_FIRE_RMS_LIFT": SYNTH_FIRE_RMS_LIFT,
                  "SYNTH_SHUF_MAX_LIFT": SYNTH_SHUF_MAX_LIFT, "SYNTH_NULL_TOL": SYNTH_NULL_TOL,
                  "BASE_SAT_HI": BASE_SAT_HI},
        "cells_aggregate": agg["cells"], "cells_n": agg["cells_n"],
        "gate_diagnostics": {k: v for k, v in diag.items() if k not in ("records",)},
        "rescore_mechanism": "CSLS_coef1(L-r_row-r_col)+logit_adjust(-tau*logP_train) on per-row calibrated log-probs",
        "exp_dev_predispatch_caveat": ("paired-rms cancels SHARED label-prior (shuffle preserves multiset) "
                                       "and shared object-geometry; lifts rms only for ASYMMETRIC fixable "
                                       "density hub over recoverable truth. V>=300 regime resembles the "
                                       "unfixable (deep-truth + shared-prior) case; HARD_FAIL/low-MIDDLE "
                                       "predicted, but real BGE hubness may differ -> cheap full run measures."),
        "filtered_protocol": "bordes_2013_filtered_hits_at_k_mrr_exclude_other_true_objects_per_subject",
        "corpus_provenance": "conceptnet5_en_100k_real_triples",
        "allow_synthetic": False, "n_generative_llm_calls": 0,
        "metrics_source": "measured_posthoc_rescore_of_frozen_joint_knn_score_matrices",
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
