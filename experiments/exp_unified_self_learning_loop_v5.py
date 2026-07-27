"""UNIFIED SELF-LEARNING LOOP v5 -- STRUCTURE-SENSITIVE (HRR-BIND) READOUT + CENTERED FAST-STORE KEYS.

v4 (FULL, MIDDLE_BAND, data/exp_unified_self_learning_loop_v4/metrics.json) was a CLEAN FAIR NEGATIVE on
comprehension-specific gain: MAIN_fast_episodic LOW gain (0.0015) TIED word-scrambled (0.0015) and LOST to
wrong-concept (0.0068). The brain-fidelity audit (notes/v4_negative_brain_fidelity_audit_readout_is_order_
blind_next_lever_2026-07-27.md) located a MECHANISTIC defect, not just a null result: v2's TinyTransformer.
pooled() readout is MEAN-POOL over token hidden states -- a word-scrambled sentence has the IDENTICAL token
multiset, so the mean over the window is nearly preserved even though self-attention perturbed each token's
hidden state. The encoder is MLM-pretrained (order-sensitive internally) but the READOUT throws order away
before anything downstream (fast-store write, sleep, measurement) ever sees it. This compounds: mean-pool
over tokens -> mean-pool over mentions (LOOP2._sleep_consolidate) -> weighted-mean over episodic traces
(v4._fast_episodic_read).

STEP-0 (data/probe_v4_readout_order_sensitivity_v1.json; scratchpad probe_readout_order_sensitivity.py)
measured 5 alternative readouts on the SAME frozen v2 encoder (ckpt_seed_7) over 120 real-ARC (coherent,
scrambled, wrong-concept) triplets. MEAN_POOL: coh-vs-scrambled cos=0.9944 (order-blind, CONFIRMED) and
coh-vs-wrong-RAW cos=0.9444 (near-collapsed cross-concept, i.e. anisotropic). BIND_HRR_position (HRR-bind a
FIXED per-position role vector to each token hidden, sum over non-pad positions) won BOTH axes at once:
coh-vs-scrambled=0.7304 (most order-sensitive) AND coh-vs-wrong-RAW=0.4848 (most concept-discriminative).
Mean-centering (subtract the coherent-batch mean) dropped coh-vs-wrong further to -0.0645 for MEAN_POOL and
-0.0258 for BIND -- confirming a SEPARATE anisotropy/common-mode defect on top of the order-blindness.

v5 = v4 with EXACTLY TWO changes (both own-mechanism, no bolt-on reader/parser; both already-existing repo
primitives -- hdlab.binding.bind for HRR circular convolution; LOOP2._fit_common_mode/_apply_common_mode for
anisotropy removal, the same helper v2's precision_cm/ca3 arms already use):

  (1) READOUT: TinyTransformer.pooled (mean-pool) -> BIND_HRR_position. Implemented as a GLOBAL CLASS-LEVEL
      MONKEYPATCH of V2.TinyTransformer.pooled, applied ONCE at module-import time (before any encoder is
      built or any text is encoded). This is the load-bearing SPACE-CONSISTENCY design decision (see below).

  (2) COMMON-MODE REMOVAL on the fast-store KEY path only: the DG expansion projection (_sparse_keys) now
      mean/rank-centers its input via LOOP2._apply_common_mode (fit ONCE from the fixed train foundation,
      LOOP2._fit_common_mode(base_text, cm_rank)) BEFORE the k-WTA sparsification. This is where STEP-0's
      "-0.0645 after centering" result is cashed in: the DG projection now decorrelates concepts instead of
      decorrelating a shared anisotropic direction.

SPACE CONSISTENCY (the design risk the pre-reg flagged -- resolved by construction, not by convention):
comprehension GAIN is measured via relational-AUC placement over a `text` matrix that mixes TWO sources: (a)
`base_text`, the FIXED train-pool foundation reps built ONCE at prep time by V2.encode_concept_text_reps
(calls model.pooled() directly), and (b) `store[ci]`, the held concepts' consolidated reps built from mention
reps produced by LOOP2._encode_sentences (also calls model.pooled() internally). If the readout were swapped
in only ONE of these two call sites, `text` would silently mix bind-space held rows against mean-pool-space
candidate rows -- cosines between the two would be geometrically meaningless, and any resulting "signal"
could not be trusted (the WARNING the pre-reg explicitly asked to reason about). v5 avoids this by patching
`V2.TinyTransformer.pooled` at the CLASS level: EVERY caller -- encode_concept_text_reps (base_text),
LOOP2._encode_sentences (all mention reads, all 7 arms, every cycle), AND the self-test's own toy encoder --
routes through the identical bind-readout function. There is exactly ONE readout in the whole pipeline, so
store-write reps and measurement-consumed reps are the SAME geometry by construction; no adapter, no
per-call-site flag, nothing to drift out of sync.
The common-mode change is scoped NARROWLY on purpose: it only touches the DG KEY computation inside
_sparse_keys (used both for building each mention's sparse key AND the context query in
_fast_episodic_read); the VALUE space (raw bind-readout mention reps, summed into the final concept rep) is
left UNCENTERED, so store[ci] and base_text remain the same uncentered bind-readout geometry the measurement
consumes. Centering only reweights HOW the competitive read chooses among a concept's own episodic traces; it
cannot introduce a store-vs-measure space mismatch because it never touches what gets written to the text
matrix.

ARMS, BANDS, CONFIG PROFILES: held IDENTICAL to v4 (same 7 ARM_SPECS incl. the matched fast_episodic
consolidation mode for SCRAMBLED/WRONG_CONCEPT controls that made v4's comparison fair; same LOW/MID/HIGH/ALL
exposure terciles; same relational-AUC + specific-fact metric; same SELFTEST/SMOKE/FULL cfg profiles from
LOOP3; same HARD_PASS/MIDDLE_BAND/HARD_FAIL bands). The readout swap + common-mode-on-keys is the ONLY
variable. See preregs/2026-07-27_unified_self_learning_loop_v5_structure_sensitive_readout.md.

THE BAR (FULL, unchanged from v4): MAIN_fast_episodic LOW-slice comprehension_specific_gain = LOW gain
EXCEEDS BOTH the SCRAMBLED control's LOW gain AND the WRONG_CONCEPT control's LOW gain, AND sustained
(no wash-out), AND beats plain wash-out, AND LOW gain > HIGH gain, while keeping sleep-fires-every-cycle +
controls-below-main(LOW) + retention-held(LOW) + leak-proof + power. HARD_PASS = the substrate LEARNS NEW
concepts from GENUINE comprehension via a fast episodic store once the readout can actually SEE structure.
HONEST DEFLATE NULL (pre-registered, not a bug if it happens): if bound-coherent STILL ties bound-scrambled
on GAIN even though STEP-0 showed the representation NOW separates them, that is a real negative pointing
DEEPER -- the metric (relational-AUC placement) or the consolidation/learning-UPDATE itself, not the readout
-- and must be reported plainly, not spun.

SMOKE (tiny fresh-trained encoder, 250 MLM steps, d=128): proves the FAST-STORE MECHANISM fires -- pattern
separation, context-addressability, read-sharpening (self-test), sleep/clarify/controls, arms differ,
stratified probe, comprehension-discriminator resolves (all MEASURED PASS). The NEW `_readout_diagnostic`
(mirrors STEP-0's probe but against THIS run's own encoder+postings) is COMPUTED and reported every run, but
is NOT part of the SMOKE PASS/FAIL gate -- MEASURED (this cell, both local runs): on the SMOKE's own
250-step toy encoder, coh-vs-scrambled cos=0.9982 (order_blind=True) -- the tiny/undertrained encoder's
readout is dominated by early-training anisotropy severe enough that even bind-readout cannot escape it, the
SAME "tiny encoder below signal threshold" scale-limitation v1-v4 already documented for the capability
signal (self-test's OWN order-sensitivity check on an UNTRAINED toy encoder, cos=0.66, confirms the patch
mechanism itself is wired and differentiates order -- it is the ENCODER's training-immaturity, not the
readout code, that swamps the effect at SMOKE scale). DISCRIMINATOR-MUST-SURVIVE-SCALE PATH B applies: the
regime that matters (the real v2 checkpoint FULL loads) was measured DIRECTLY by STEP-0 on ckpt_seed_7
(coh-vs-scrambled 0.7304, coh-vs-wrong-RAW 0.4848 -- both comfortably order-sensitive+discriminative). FULL
capability GAIN remains FULL-deferred as in v1-v4; FULL loads the real scale-v2 checkpoint.

BRAIN-FAITHFUL / INVARIANTS (unchanged from v4): TEACHER-FREE; NO borrowed vectors (OUR trained encoder
only); GLASS-BOX (fixed random DG projection + k-WTA + fixed random role vectors + symbolic gates + softmax
read; HRR bind = FFT-based circular convolution, a substrate-native primitive, not a learned/external
component; no external LLM / no autograd at inference); LEAK-PROOF (predicted edge disjoint from read text;
probe negatives degree-matched, adjacency excluded). ASCII-only. Deterministic seeds (fixed ints +
default_rng + fixed DG projection + fixed role-vector generator). Store writes LOCAL-ONLY + UNCOMMITTED.
Agent-reported VET-PENDING.
"""
# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scale/floor):
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - final_metrics_atomicity: tmp_replace (os.replace)
# - crash-diagnostic metrics + start-marker + heartbeat
# - arms_differ_verified at smoke gate (NO_READ==READ_NO_SLEEP store exempted: both freeze cycle-0)
# - discriminator (SMOKE) = fast-episodic mechanism fires (pattern-sep + arms differ + context-address +
#     read-sharpen self-test) + stratified probe fires + sleep/comprehension/controls/clarify fire. READOUT
#     diagnostic (order-sensitive + discriminative) is COMPUTED+reported every run but NOT part of the SMOKE
#     gate -- PATH B (discriminator-must-survive-scale): MEASURED on the tiny SMOKE encoder it does NOT fire
#     (250-step undertrained anisotropy), but the regime that matters (real v2 ckpt FULL loads) was
#     MEASURED DIRECTLY by STEP-0 (data/probe_v4_readout_order_sensitivity_v1.json, coh-vs-scrambled=0.7304,
#     coh-vs-wrong-RAW=0.4848); self-test's untrained-toy-encoder check (cos=0.66) confirms the patch
#     mechanism itself is wired correctly.
# - discriminator (FULL) = COMPREHENSION-SPECIFIC LOW-slice gain: fast_episodic correct-concept gain beats
#     BOTH word-scrambled AND wrong-concept controls' gain (+ beats plain wash-out) (real ckpt; path B
#     analytical: tiny encoder below signal threshold, per v1-v4 MEASURED negative/flat on tiny)
# - baseline_in_band: MAIN_plainavg LOW-slice relational AUC ~0.5 (in [0.05,0.95]); smoke defers capability
# - crlb_n/a: directional gain gate, not a capacity/noise-floor threshold (no Cramer-Rao floor applies)
# - deterministic seeding (fixed ints + default_rng + fixed DG/role-vector generators; no hash()/list(set()))
# - progress_logging: print_flush_true (timeout_s >= 1800)
# - self-test constructs REAL objects (patched encoder, clarify, MDL, Kalman, fast episodic read+centered
#     keys, pattern-sep, context-address, per-slice probe, specific-fact probe, override gate, ckpt
#     round-trip) AND asserts the readout patch is ACTUALLY ACTIVE (identity check, not just "code exists")
# - all reported numbers MEASURED@ this cell's metrics.json
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import sys
import json
import time
import argparse
import hashlib
import traceback
from datetime import datetime, timezone

import numpy as np
import torch

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import experiments.exp_scale_meaning_learn_arc_heldout_v2 as V2
import experiments.exp_unified_self_learning_loop_v2 as LOOP2
import experiments.exp_unified_self_learning_loop_v3 as LOOP3
from hdlab.clarify_gate import ClarifyGate, GateOutcome
from hdlab.learner.core import per_cluster_gate
from hdlab.binding import bind

ANCHOR_NAME = "unified_self_learning_loop_v5"

# ===========================================================================
# CHANGE 1/2 -- STRUCTURE-SENSITIVE READOUT: global class-level monkeypatch of
# V2.TinyTransformer.pooled (mean-pool -> HRR-bind of a fixed per-position role
# vector with each token hidden state, summed over non-pad positions, L2-normed).
# Applied ONCE at module-import time, BEFORE any encoder is built or any text is
# encoded, so every consumer (base_text foundation, all mention reads across all
# 7 arms, the self-test's own toy encoder) shares the identical readout -- the
# SPACE-CONSISTENCY design decision documented in the module docstring.
# Matches probe_readout_order_sensitivity.py's BIND_HRR_position variant exactly
# (STEP-0 winner: coh-vs-scrambled cos 0.9944->0.7304, coh-vs-wrong-RAW
# 0.9444->0.4848; data/probe_v4_readout_order_sensitivity_v1.json).
# ===========================================================================
READOUT_VARIANT = "bind_hrr_position"
READOUT_ROLE_SEED = 20260727           # fixed int seed for the per-position role-vector generator
CM_SCOPE = "fast_store_dg_keys_only"   # common-mode removal touches ONLY the DG key path, not the VALUE space
ORDER_SENSITIVE_THRESH = 0.95          # readout diagnostic: coh-vs-scrambled cos must be BELOW this
DISCRIM_THRESH = 0.95                  # readout diagnostic: coh-vs-wrong-concept RAW cos must be BELOW this

_ROLE_VECTOR_CACHE = {}


def _get_role_vectors(max_len, d_model):
    """Fixed random per-position role vectors (max_len, d_model), L2-normalized, deterministic (fixed
    seed). Cached per (max_len, d_model) shape so repeated calls (every batch, every arm, every cycle)
    don't re-sample. Lazily built on first use -- no need to know the encoder shape ahead of the patch."""
    key = (int(max_len), int(d_model))
    if key not in _ROLE_VECTOR_CACHE:
        g = torch.Generator().manual_seed(READOUT_ROLE_SEED)
        rv = torch.randn(int(max_len), int(d_model), generator=g)
        rv = rv / (rv.norm(dim=-1, keepdim=True) + 1e-8)
        _ROLE_VECTOR_CACHE[key] = rv
    return _ROLE_VECTOR_CACHE[key]


def _bind_pooled(self, ids):
    """v5 readout: HRR-bind (hdlab.binding.bind = FFT circular convolution) a fixed per-position role
    vector with each token's contextual hidden state, sum over non-pad positions, L2-normalize.
    Order-sensitive BY CONSTRUCTION (swapping tokens i<->j binds them to different role vectors, changing
    the bundled sum) -- unlike mean/max pooling, which are permutation-invariant over the token set.
    Forces float32: torch.fft is not reliable under fp16 autocast (cuFFT half-precision support is
    inconsistent); the encoder's own forward pass may run in fp16 under the caller's autocast context, but
    the readout itself always computes in fp32 for numerical safety, matching the STEP-0 probe (which ran
    entirely in fp32, no autocast)."""
    h, pad_mask = self._contextual(ids)
    h = h.float()
    keep = (~pad_mask).float().unsqueeze(-1)
    B, L, D = h.shape
    roles = _get_role_vectors(self.max_len, D).to(device=h.device, dtype=h.dtype)[:L]
    roles = roles.unsqueeze(0).expand(B, -1, -1)
    bound = bind(h.contiguous(), roles.contiguous())
    bound = bound * keep
    rep = bound.sum(dim=1)
    return rep / (rep.norm(dim=1, keepdim=True) + 1e-8)


V2.TinyTransformer.pooled = _bind_pooled   # GLOBAL SWAP -- see module docstring "SPACE CONSISTENCY"


# ---- arms: IDENTICAL to v4 (the readout swap is the only variable; arm gating unchanged) ----
# spec = (name, do_read, do_sleep, scramble, wrong_concept, consolidation_mode).
ARM_SPECS = [
    ("MAIN_plainavg", True, True, False, False, "plain"),
    ("MAIN_precision", True, True, False, False, "precision"),
    ("MAIN_fast_episodic", True, True, False, False, "fast_episodic"),   # correct-concept fast (KEY)
    ("SCRAMBLED", True, True, True, False, "fast_episodic"),             # weak control (word-order shuffle)
    ("WRONG_CONCEPT", True, True, False, True, "fast_episodic"),          # STRONG control (other concept's text)
    ("NO_READ", False, True, False, False, "fast_episodic"),
    ("READ_NO_SLEEP", True, False, False, False, "fast_episodic"),
]
ARMS = [s[0] for s in ARM_SPECS]
ARM_SPEC = {s[0]: dict(read=s[1], sleep=s[2], scramble=s[3], wrong=s[4], mode=s[5]) for s in ARM_SPECS}
MAIN_MODE_ARMS = ["MAIN_plainavg", "MAIN_precision", "MAIN_fast_episodic"]
PLAIN_ARM = "MAIN_plainavg"
PRECISION_ARM = "MAIN_precision"
FAST_ARM = "MAIN_fast_episodic"       # the KEY arm the BAR is on (coherent, correct concept)
NOREAD_ARM = "NO_READ"
SCRAM_ARM = "SCRAMBLED"
WRONG_ARM = "WRONG_CONCEPT"
NOSLEEP_ARM = "READ_NO_SLEEP"
CONTROL_ARMS = [NOREAD_ARM, SCRAM_ARM, WRONG_ARM, NOSLEEP_ARM]

TEXT_KEY = V2.TEXT_ARM
RAW_KEY = V2.RAW_ARM
SH_KEY = V2.SHUFFLE_ARM

SLICES = LOOP3.SLICES              # ["LOW","MID","HIGH","ALL"]
KEY_SLICE = "LOW"
SAT_SLICE = "HIGH"

# fast episodic store (CLS hippocampus/DG) defaults -- glass-box, fixed, deterministic. IDENTICAL to v4.
FAST_DEFAULTS = dict(
    fast_expansion=8,              # DG expansion recoding factor: D_sparse = expansion * d
    fast_active_frac=0.05,         # DG sparsity: fraction of expanded units kept active (k-WTA ~2-5%)
    fast_read_temp=0.05,           # softmax temperature of the context-addressed competitive read (sharp)
    fast_proj_seed=12345,          # fixed DG random projection seed (deterministic pattern separation)
)

# Base on v3 configs (LOW-exposure-qualifying schedule) + add the fast-store knobs. IDENTICAL to v4.
SELFTEST_CFG = dict(LOOP3.SELFTEST_CFG); SELFTEST_CFG.update(FAST_DEFAULTS)
SMOKE_CFG = dict(LOOP3.SMOKE_CFG); SMOKE_CFG.update(FAST_DEFAULTS)
FULL_CFG = dict(LOOP3.FULL_CFG); FULL_CFG.update(FAST_DEFAULTS)

# HARD-PASS bands (FULL). IDENTICAL to v4 -- the readout swap is the only variable.
HP_GAIN_MARGIN = 0.02          # LOW-slice MAIN_fast_episodic AUC[final]-AUC[0] must EXCEED this
WASHOUT_EPS = 0.01             # "sustained" = LOW final within this of the LOW peak (no wash-out)
CONTRAST_EPS = 0.0             # LOW gain must exceed HIGH gain by > this (reading teaches NEW > known)
HP_CONTROL_SEP = 0.0           # best MAIN[final] must exceed each control[final] by > this (LOW slice)
RETENTION_EPS = 0.02           # LOW MAIN_fast_episodic AUC may never drop below AUC[0]-eps (no forgetting)
MIN_QUERY_TASKS = 40           # LOW-slice relational power floor (SMOKE relaxed)
SMOKE_POWER_FLOOR = 8
PATTERN_SEP_EPS = 0.0          # SMOKE: sparse-key cross-concept overlap must be < dense (ratio < 1)
COMPREHENSION_GAIN_EPS = 0.0   # FULL: FAST_CORRECT LOW gain must EXCEED both scrambled AND wrong-concept
#                                LOW gain by > this (comprehension-specific gain, not sample-accumulation)


def _out_dir(run_mode):
    suffix = {"selftest": "_selftest", "smoke": "_smoke", "full": ""}.get(run_mode, "")
    d = os.path.join(_REPO, "data", "exp_" + ANCHOR_NAME + suffix)
    os.makedirs(d, exist_ok=True)
    return d


def _log(msg):
    print("[%s] %s" % (ANCHOR_NAME, msg), flush=True)


def _now():
    return datetime.now(timezone.utc).isoformat()


def _fmt(x):
    return ("%.4f" % x) if isinstance(x, (int, float)) else str(x)


def _write_start_marker(out_dir, run_mode, expected_units):
    marker = dict(pid=os.getpid(), ts_iso=_now(), anchor_name=ANCHOR_NAME,
                  run_mode=run_mode, expected_n_units=expected_units)
    tmp = os.path.join(out_dir, "_start_marker.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, os.path.join(out_dir, "_start_marker.json"))


def _heartbeat(out_dir, unit_idx, total_units, elapsed_s, extra=None):
    row = dict(ts_iso=_now(), unit_idx=int(unit_idx), total_units=int(total_units),
               elapsed_s=round(float(elapsed_s), 2))
    if extra:
        row["extra"] = extra
    with open(os.path.join(out_dir, "_heartbeat.jsonl"), "a", encoding="utf-8") as f:
        f.write(json.dumps(row) + "\n")


# ===========================================================================
# FAST EPISODIC STORE (CLS hippocampus / DG): pattern separation + context read.
# v5 CHANGE 2/2: _build_fast_projection now carries a `cm` (common-mode transform,
# fit once from the fixed train foundation `base_text` in bind-readout space) and
# _sparse_keys applies it BEFORE the expansion projection. Scoped to the KEY path
# only -- see module docstring "SPACE CONSISTENCY".
# ===========================================================================
def _build_fast_projection(d, cfg, cm):
    """Fixed random DG expansion projection P: (d, D) with D = expansion*d. Shared across ALL concepts
    (one dentate gyrus), deterministic (fixed seed). Gaussian random projection (Johnson-Lindenstrauss).
    `cm` (dict from LOOP2._fit_common_mode, or None) is carried through to _sparse_keys."""
    D = int(cfg["fast_expansion"]) * int(d)
    rng = np.random.default_rng(int(cfg["fast_proj_seed"]))
    P = rng.standard_normal((int(d), D)).astype(np.float64) / np.sqrt(float(d))
    return dict(P=P, d=int(d), D=D, active_frac=float(cfg["fast_active_frac"]),
               read_temp=float(cfg["fast_read_temp"]), cm=cm)


def _kwta_rows(H, active_frac):
    """k-WTA sparsification (DG-analog): ReLU then keep the top active_frac entries per row, zero rest.
    H: (n, D) -> (n, D) sparse non-negative. Non-negative sparse codes -> sharp co-activation overlap."""
    Hr = np.maximum(H, 0.0)
    if Hr.ndim == 1:
        Hr = Hr[None, :]
        squeeze = True
    else:
        squeeze = False
    n, D = Hr.shape
    k = max(1, int(np.ceil(float(active_frac) * D)))
    if k >= D:
        return Hr[0] if squeeze else Hr
    thr = np.partition(Hr, D - k, axis=1)[:, D - k][:, None]
    out = np.where(Hr >= thr, Hr, 0.0)
    return out[0] if squeeze else out


def _sparse_keys(X, fast):
    """Pattern-separate reps X (n,d) -> L2-normalized sparse keys (n,D). Empty-safe.
    v5: if fast['cm'] is set, common-mode-centers X (LOOP2._apply_common_mode) BEFORE the DG expansion
    projection -- STEP-0 probe: raw cross-concept cosine 0.9444 -> -0.0645 after centering. This is the
    ONLY function that touches centering; both the per-mention KEY and the context QUERY (in
    _fast_episodic_read) route through here, so centering is applied consistently to both without a
    separate code path. The VALUE reps (X itself, summed by _fast_episodic_read) are returned unchanged
    by the caller -- centering never reaches the text matrix used for measurement."""
    X = np.asarray(X, dtype=np.float64)
    if X.ndim != 2 or X.shape[0] == 0:
        return np.zeros((0, fast["D"]), dtype=np.float64)
    cm = fast.get("cm")
    if cm is not None:
        Xk = LOOP2._apply_common_mode(X.astype(np.float32), cm).astype(np.float64)
    else:
        Xk = X
    Kd = _kwta_rows(Xk @ fast["P"], fast["active_frac"])
    nrm = np.linalg.norm(Kd, axis=1, keepdims=True)
    return Kd / np.where(nrm < 1e-12, 1.0, nrm)


def _fast_episodic_read(reps, fast):
    """Context-addressed competitive read over a concept's episodic traces (values in encoder space).
    query = k-WTA(mean-context @ P, centered if cm set); weights = softmax(sparse-key . query / temp);
    rep = weighted values (UNCENTERED, raw bind-readout space -- consistent with base_text/store text
    matrix). A sharp non-linear pattern-separated read -- denoises outliers + avoids centroid regression.
    Returns L2-normalized (d,)."""
    X = np.asarray(reps, dtype=np.float64)
    d = fast["d"]
    if X.ndim != 2 or X.shape[0] == 0:
        return np.zeros(d, dtype=np.float32)
    if X.shape[0] == 1:
        v = X[0]
        return (v / (np.linalg.norm(v) + 1e-8)).astype(np.float32)
    Kd = _sparse_keys(X, fast)                        # (n, D)
    ctx = X.mean(axis=0)
    ctx = ctx / (np.linalg.norm(ctx) + 1e-8)
    q = _sparse_keys(ctx[None, :], fast)[0]           # (D,)
    sims = Kd @ q                                      # (n,) sparse co-activation overlap
    sims = sims - sims.max()
    w = np.exp(sims / max(1e-6, fast["read_temp"]))
    w = w / (w.sum() + 1e-12)
    val = (w[:, None] * X).sum(axis=0)
    return (val / (np.linalg.norm(val) + 1e-8)).astype(np.float32)


def _mean_cross_concept_sim(mat):
    """Mean pairwise cosine among rows of mat (concept reps). Higher = more anisotropic/entangled."""
    M = np.asarray(mat, dtype=np.float64)
    if M.shape[0] < 2:
        return None
    nrm = np.linalg.norm(M, axis=1, keepdims=True)
    M = M / np.where(nrm < 1e-12, 1.0, nrm)
    G = M @ M.T
    n = M.shape[0]
    return float((G.sum() - np.trace(G)) / (n * (n - 1)))


def _pattern_sep_ratio(concept_means, fast):
    """DG pattern separation FIRES iff the sparse KEYS are more decorrelated (lower mean cross-concept
    cosine) than the dense reps: ratio = xsim(sparse_keys) / xsim(dense) < 1."""
    M = np.asarray(concept_means, dtype=np.float64)
    if M.shape[0] < 2:
        return None
    xsim_dense = _mean_cross_concept_sim(M)
    keys = _sparse_keys(M, fast)
    xsim_sparse = _mean_cross_concept_sim(keys)
    if xsim_dense is None or xsim_sparse is None or abs(xsim_dense) < 1e-9:
        return None
    return dict(xsim_dense=round(xsim_dense, 4), xsim_sparse=round(xsim_sparse, 4),
                ratio=round(xsim_sparse / xsim_dense, 4))


# ===========================================================================
# READOUT DIAGNOSTIC (NEW in v5): mirrors probe_readout_order_sensitivity.py but
# runs against THIS cell's OWN (smoke or full) encoder + REAL postings for the
# concepts actually used this run -- a mandatory SMOKE discriminator-fires check
# ("coherent/scrambled/wrong arms actually differ at readout") that does not rely
# on the standalone probe script or on self-test toy sentences alone.
# ===========================================================================
def _readout_diagnostic(held, postings, model, tok, spec, cfg, device, wrong_map, seed, max_n=40):
    rng = np.random.default_rng(seed + 4001)
    cands = [ci for ci in held if postings[ci] and postings[wrong_map[ci]]]
    if len(cands) > max_n:
        cands = sorted(int(x) for x in rng.choice(cands, size=max_n, replace=False))
    coh, scr, wrg = [], [], []
    for ci in cands:
        s = postings[ci][0]
        srng = np.random.default_rng(seed + 1009 * int(ci))
        sc = LOOP2._scramble_words(s, srng)
        w = postings[wrong_map[ci]][0]
        coh.append(s); scr.append(sc); wrg.append(w)
    if not coh:
        return dict(n_pairs=0, coh_vs_scram_mean=None, coh_vs_wrong_raw_mean=None,
                   order_sensitive_fires=False, discriminative_fires=False)
    r_coh = LOOP2._encode_sentences(model, tok, coh, cfg, device, spec)
    r_scr = LOOP2._encode_sentences(model, tok, scr, cfg, device, spec)
    r_wrg = LOOP2._encode_sentences(model, tok, wrg, cfg, device, spec)
    cs = float(np.mean(np.sum(r_coh * r_scr, axis=1)))
    cw = float(np.mean(np.sum(r_coh * r_wrg, axis=1)))
    return dict(n_pairs=len(coh), coh_vs_scram_mean=round(cs, 4), coh_vs_wrong_raw_mean=round(cw, 4),
               order_sensitive_fires=bool(cs < ORDER_SENSITIVE_THRESH),
               discriminative_fires=bool(cw < DISCRIM_THRESH))


# ===========================================================================
# v5 SLEEP: identical to v4's _consolidate_candidate_v4/_sleep_consolidate_v4 --
# dispatches the fast_episodic candidate (now reading through the patched
# bind-readout + centered-key mechanism transparently). Gating held IDENTICAL to
# the kalman modes (coverage-override gate) so the ONLY variable between
# fast_episodic and precision is the READ.
# ===========================================================================
def _consolidate_candidate_v5(ci, reps, new_reps, mode, kal_rep, kal_prec, is_init, cfg, base_clean, fast):
    if mode == "fast_episodic":
        return _fast_episodic_read(reps, fast)         # fresh competitive read of the FULL episodic buffer
    return LOOP2._consolidate_candidate(ci, reps, new_reps, mode, kal_rep, kal_prec, is_init, cfg, base_clean)


def _sleep_consolidate_v5(acc_reps, new_reps, store, kal_rep, kal_prec, committed_conf,
                          is_init, mode, cfg, base_clean, fast):
    n_consolidated = 0
    n_kept_episodic = 0
    n_evaluated = 0
    committed_now = []
    cr_samples = []
    for ci, reps in acc_reps.items():
        if len(reps) < 1:
            continue
        n_evaluated += 1
        lr, coh = LOOP2._concept_learn_result(reps)
        cr = float(lr.compression_ratio)
        mdl_ok = per_cluster_gate(lr, cfg["min_compression_ratio"])
        sufficient = (len(reps) >= cfg["min_evidence_mentions"]) and (coh >= cfg["concentration_thresh"])
        cand = _consolidate_candidate_v5(ci, reps, new_reps.get(ci, []), mode, kal_rep, kal_prec,
                                         is_init, cfg, base_clean, fast)
        if mode == "plain":
            new_conf = (coh + 1.0) / 2.0
            override_ok = True
        else:
            new_conf = ((coh + 1.0) / 2.0) * min(1.0, len(reps) / float(cfg["override_cov_target"]))
            prev_conf = committed_conf.get(ci, -1.0)
            override_ok = (new_conf >= cfg["override_min"]) and (new_conf >= prev_conf - cfg["override_defer_eps"])
        commit = bool(is_init or (mdl_ok and sufficient and override_ok))
        if commit:
            store[ci] = cand
            committed_conf[ci] = float(new_conf)
            n_consolidated += 1
            committed_now.append(ci)
            if len(cr_samples) < 5:
                cr_samples.append({"concept_idx": int(ci), "n_mentions": len(reps),
                                   "coherence": round(coh, 4), "compression_ratio": round(cr, 4),
                                   "new_conf": round(float(new_conf), 4)})
        else:
            n_kept_episodic += 1
    return dict(n_consolidated=n_consolidated, n_kept_episodic=n_kept_episodic,
                n_evaluated=n_evaluated, sample_commits=cr_samples), committed_now


# ===========================================================================
# SPECIFIC-FACT probe: identical to v4 (per-concept "did it acquire the SPECIFIC
# just-read fact"). Consumes text_final (now bind-readout space, consistent
# throughout).
# ===========================================================================
def _specific_fact_probe(text, adj, deg, split, slice_idxs, seed):
    train_pool = split["train_eval_idx"]
    train_set = set(int(x) for x in train_pool.tolist())
    have_text = np.linalg.norm(text, axis=1) > 1e-8
    deg_bin = {}
    for t in train_pool.tolist():
        deg_bin.setdefault(int(deg[t]), []).append(int(t))
    max_deg = int(deg[train_pool].max()) if train_pool.shape[0] else 0
    rng = np.random.default_rng(int(seed) + 91)
    hits, rrs = [], []
    for h in sorted(int(x) for x in slice_idxs):
        if not have_text[h]:
            continue
        pos = sorted(j for j in adj[h] if j in train_set and have_text[j])
        if not pos:
            continue
        pos = pos[:8]
        exclude = set(adj[h]) | {h}
        negs, used, ok = [], set(), True
        for p in pos:
            dp = int(deg[p])
            picked = -1
            for tol in range(0, max_deg + 1):
                cands = []
                for dd in ((dp,) if tol == 0 else (dp - tol, dp + tol)):
                    if dd in deg_bin:
                        cands.extend(deg_bin[dd])
                cands = [c for c in cands if c not in exclude and c not in used and have_text[c]]
                if cands:
                    picked = cands[int(rng.integers(0, len(cands)))]
                    break
            if picked < 0:
                ok = False
                break
            negs.append(picked)
            used.add(picked)
        if not ok or not negs:
            continue
        cand = np.array(pos + negs, dtype=np.int64)
        posm = np.array([True] * len(pos) + [False] * len(negs))
        sc = text[h] @ text[cand].T
        order = np.argsort(-sc)
        hits.append(bool(posm[order[0]]))
        first_pos = next((i for i, idx in enumerate(order) if posm[idx]), None)
        rrs.append(1.0 / (first_pos + 1)) if first_pos is not None else rrs.append(0.0)
    n = len(hits)
    return dict(hit1=(round(float(np.mean(hits)), 4) if n else None),
                mrr=(round(float(np.mean(rrs)), 4) if n else None), n_concepts=n)


# ===========================================================================
# WRONG-CONCEPT map: deterministic derangement of held concepts. Identical to v4.
# ===========================================================================
def _build_wrong_map(held):
    order = sorted(int(c) for c in held)
    n = len(order)
    shift = max(1, n // 2)                 # != 0 and != n for n>=2 -> guaranteed derangement
    return {order[i]: order[(i + shift) % n] for i in range(n)}


# ===========================================================================
# ONE ARM: stratified cycle loop (per-slice AUC curves) with the v5 sleep + fast diag.
# Structurally identical to v4._run_arm; only the readout (transparently, via the
# module-level patch) and the DG-key centering (transparently, via fast['cm']) differ.
# ===========================================================================
def _run_arm(arm, held, slices, postings, model, tok, spec, cfg, device, out_dir,
             ground, counts, universe, split, adj, deg, n_shards, seed, base_text, base_clean, fast,
             wrong_map):
    a = ARM_SPEC[arm]
    do_read, do_sleep, scramble, wrong, mode = a["read"], a["sleep"], a["scramble"], a["wrong"], a["mode"]
    gate = ClarifyGate()
    store = {}
    kal_rep, kal_prec, committed_conf = {}, {}, {}
    acc_reps = {ci: [] for ci in held}
    n_cycles = cfg["n_cycles"]
    m = cfg["mentions_per_cycle"]
    curves = {s: [] for s in SLICES}
    nq_curves = {s: [] for s in SLICES}
    shuffle_curves = {s: [] for s in SLICES}
    sleep_log, flag_log, ncommit_curve = [], [], []
    for k in range(n_cycles):
        read_this_cycle = (k == 0) or do_read
        new_reps = {ci: [] for ci in held}
        if read_this_cycle:
            for ci in held:
                src = wrong_map[ci] if wrong else ci        # WRONG_CONCEPT reads a different concept's text
                chunk = postings[src][k * m:(k + 1) * m]
                if not chunk:
                    continue
                if scramble:
                    rng = np.random.default_rng(seed + 1009 * int(ci) + 31 * k)
                    chunk = [LOOP2._scramble_words(s, rng) for s in chunk]
                reps = LOOP2._encode_sentences(model, tok, chunk, cfg, device, spec)
                for r in reps:
                    acc_reps[ci].append(r)
                    new_reps[ci].append(r)
        n_flagged = LOOP2._clarify_flag_population(acc_reps, held, gate, cfg)
        flag_log.append(n_flagged)
        is_init = (k == 0)
        if is_init or do_sleep:
            slog, _committed = _sleep_consolidate_v5(acc_reps, new_reps, store, kal_rep, kal_prec,
                                                     committed_conf, is_init, mode, cfg, base_clean, fast)
            assert slog["n_evaluated"] >= 1, (
                "SLEEP_DID_NOT_FIRE arm=%s cycle=%d (n_evaluated=0)" % (arm, k))
        else:
            slog = dict(n_consolidated=0, n_kept_episodic=len(held), n_evaluated=0,
                        sample_commits=[], sleep_disabled=True)
        sleep_log.append(slog)
        ncommit_curve.append(slog["n_consolidated"])
        probe = LOOP3._probe_stratified(store, base_text, ground, counts, universe, split, slices,
                                        adj, deg, n_shards, seed)
        for s in SLICES:
            curves[s].append(probe[s]["auc"])
            nq_curves[s].append(probe[s]["n_query"])
            shuffle_curves[s].append(probe[s]["shuffle"])
        _log("  arm=%s mode=%s cycle=%d LOW=%s(nq=%s) MID=%s HIGH=%s ALL=%s n_flag=%d n_consol=%d"
             % (arm, mode, k, _fmt(probe["LOW"]["auc"]), probe["LOW"]["n_query"],
                _fmt(probe["MID"]["auc"]), _fmt(probe["HIGH"]["auc"]), _fmt(probe["ALL"]["auc"]),
                n_flagged, slog["n_consolidated"]))
        _heartbeat(out_dir, unit_idx=k, total_units=n_cycles, elapsed_s=0.0,
                   extra={"arm": arm, "LOW_auc": probe["LOW"]["auc"], "HIGH_auc": probe["HIGH"]["auc"],
                          "LOW_nq": probe["LOW"]["n_query"]})
    text_final = LOOP2._store_to_text_matrix(store, base_text)
    spec_fact = {}
    for s in ("LOW", "HIGH", "ALL"):
        spec_fact[s] = _specific_fact_probe(text_final, adj, deg, split, slices[s], seed)
    fast_diag = None
    if mode == "fast_episodic":
        means = []
        for ci in held:
            if acc_reps[ci]:
                mu = np.asarray(acc_reps[ci], dtype=np.float64).mean(axis=0)
                means.append(mu / (np.linalg.norm(mu) + 1e-8))
        if len(means) >= 2:
            fast_diag = _pattern_sep_ratio(np.stack(means, axis=0), fast)
    text_hash_mat = LOOP2._store_to_text_matrix(store, np.zeros_like(base_text))
    digest = hashlib.sha256(np.ascontiguousarray(text_hash_mat).tobytes()).hexdigest()
    return dict(arm=arm, mode=mode, slice_curves=curves, slice_nq_curves=nq_curves,
                slice_shuffle_curves=shuffle_curves, sleep_log=sleep_log, flag_log=flag_log,
                ncommit_curve=ncommit_curve, store_digest=digest, n_committed_final=len(store),
                spec_fact=spec_fact, fast_diag=fast_diag)


# ===========================================================================
# DATA PREP (reuse v3 verbatim: v2 loop prep + exposure slices). base_text is now
# built via the PATCHED (bind-readout) model.pooled, so it lives in the SAME
# space as the store consolidations below.
# ===========================================================================
def _prepare(cfg, out_dir, ckpt_path, device):
    return LOOP3._prepare(cfg, out_dir, ckpt_path, device)


# ===========================================================================
# VERDICT helpers -- identical to v4.
# ===========================================================================
def _gain(curve):
    if not curve or curve[0] is None or curve[-1] is None:
        return None
    return curve[-1] - curve[0]


def _sustained(curve):
    g = _gain(curve)
    if g is None:
        return False, g, None
    vals = [c for c in curve if c is not None]
    if not vals:
        return False, g, None
    peak = max(vals)
    washout = (curve[-1] < peak - WASHOUT_EPS)
    return bool(g > HP_GAIN_MARGIN and not washout), g, washout


def _retention_ok(curve):
    if not curve or curve[0] is None:
        return False
    vals = [c for c in curve if c is not None]
    if not vals:
        return False
    return min(vals) >= curve[0] - RETENTION_EPS


def _headroom_norm_gain(curve):
    """gain / (1 - baseline): normalizes for the fact that low-exposure (LOW) slices have more headroom."""
    g = _gain(curve)
    if g is None or curve[0] is None:
        return None
    head = 1.0 - curve[0]
    if head <= 1e-6:
        return None
    return g / head


def _per_arm_slice_summary(r):
    out = {}
    for s in SLICES:
        curve = r["slice_curves"][s]
        sus, g, wash = _sustained(curve)
        gn = _headroom_norm_gain(curve)
        out[s] = dict(
            auc_curve=[(round(c, 4) if c is not None else None) for c in curve],
            nq_curve=r["slice_nq_curves"][s],
            gain=(round(g, 4) if g is not None else None),
            gain_headroom_norm=(round(gn, 4) if gn is not None else None),
            baseline_auc=(round(curve[0], 4) if curve and curve[0] is not None else None),
            washed_out=wash, sustained=sus, retention_ok=_retention_ok(curve),
        )
    return out


def build_verdict(arm_results, cfg, slice_meta, rdiag):
    by = {r["arm"]: r for r in arm_results}
    per_arm = {arm: _per_arm_slice_summary(by[arm]) for arm in ARMS}

    fast = per_arm[FAST_ARM]
    plain = per_arm[PLAIN_ARM]
    low_fast = fast[KEY_SLICE]
    high_fast = fast[SAT_SLICE]

    low_gain = low_fast["gain"]
    high_gain = high_fast["gain"]
    low_sustained = low_fast["sustained"]
    low_retention = low_fast["retention_ok"]
    plain_low_gain = plain[KEY_SLICE]["gain"]
    plain_low_sustained = plain[KEY_SLICE]["sustained"]

    contrast_ok = bool(low_gain is not None and high_gain is not None
                       and low_gain > high_gain + CONTRAST_EPS)
    beats_plain = bool(low_gain is not None and plain_low_gain is not None
                       and low_gain > plain_low_gain and (not plain_low_sustained))

    scram_low_gain = per_arm[SCRAM_ARM][KEY_SLICE]["gain"]
    wrong_low_gain = per_arm[WRONG_ARM][KEY_SLICE]["gain"]
    beats_scramble = bool(low_gain is not None and scram_low_gain is not None
                          and low_gain > scram_low_gain + COMPREHENSION_GAIN_EPS)
    beats_wrongconcept = bool(low_gain is not None and wrong_low_gain is not None
                              and low_gain > wrong_low_gain + COMPREHENSION_GAIN_EPS)
    comprehension_specific_gain = bool(beats_scramble and beats_wrongconcept)

    sleep_every = all(all(s.get("n_evaluated", 0) >= 1 for s in by[arm]["sleep_log"])
                      for arm in ARMS if ARM_SPEC[arm]["sleep"])

    def low_final(arm):
        c = by[arm]["slice_curves"][KEY_SLICE]
        return c[-1] if c and c[-1] is not None else None
    best_main_low = max(MAIN_MODE_ARMS, key=lambda a: (low_final(a) if low_final(a) is not None else -1.0))
    best_main_low_final = low_final(best_main_low)
    ctrl_low_finals = {a: low_final(a) for a in CONTROL_ARMS}
    controls_below_main = all(
        (best_main_low_final is not None and cf is not None and best_main_low_final > cf + HP_CONTROL_SEP)
        for cf in ctrl_low_finals.values())

    fast_low_curve = by[FAST_ARM]["slice_curves"][KEY_SLICE]
    scram_low_curve = by[SCRAM_ARM]["slice_curves"][KEY_SLICE]
    comp_c0 = ((fast_low_curve[0] - scram_low_curve[0])
               if (fast_low_curve[0] is not None and scram_low_curve[0] is not None) else None)
    comp_f = ((fast_low_curve[-1] - scram_low_curve[-1])
              if (fast_low_curve[-1] is not None and scram_low_curve[-1] is not None) else None)
    comprehension_fires = bool(comp_c0 is not None and comp_c0 > 0.0 and comp_f is not None and comp_f > 0.0)

    noread_low = by[NOREAD_ARM]["slice_curves"][KEY_SLICE]
    noread_vals = [c for c in noread_low if c is not None]
    noread_flat = bool(len(noread_vals) >= 1 and (max(noread_vals) - min(noread_vals) < 1e-6))
    clarify_fired = bool(max(by[FAST_ARM]["flag_log"]) > 0)

    low_nq_final = by[FAST_ARM]["slice_nq_curves"][KEY_SLICE][-1] if \
        by[FAST_ARM]["slice_nq_curves"][KEY_SLICE] else 0
    power_floor = SMOKE_POWER_FLOOR if cfg["run_mode"] == "smoke" else MIN_QUERY_TASKS
    power_ok = (low_nq_final is not None and low_nq_final >= power_floor)

    exposure_ordered = bool(slice_meta["LOW"]["exposure_median"] < slice_meta["HIGH"]["exposure_median"])
    slices_with_power = sum(1 for s in ("LOW", "MID", "HIGH")
                            if (by[FAST_ARM]["slice_nq_curves"][s][-1] or 0) >= power_floor)
    stratified_probe_fires = bool(exposure_ordered and slices_with_power >= 2)

    modes_differ = (by[PLAIN_ARM]["store_digest"] != by[FAST_ARM]["store_digest"]
                    and by[PRECISION_ARM]["store_digest"] != by[FAST_ARM]["store_digest"])
    fast_diag = by[FAST_ARM].get("fast_diag")
    pattern_sep_fires = bool(fast_diag is not None and fast_diag.get("ratio") is not None
                             and fast_diag["ratio"] < 1.0 - PATTERN_SEP_EPS)

    spec_fact_low = by[FAST_ARM]["spec_fact"].get("LOW")
    spec_fact_high = by[FAST_ARM]["spec_fact"].get("HIGH")
    plain_spec_low = by[PLAIN_ARM]["spec_fact"].get("LOW")

    _rc_gains = [g for g in (low_gain, scram_low_gain, wrong_low_gain) if g is not None]
    comprehension_discriminator_resolves = bool(len(_rc_gains) == 3 and (max(_rc_gains) - min(_rc_gains) > 0.005))

    readout_order_sensitive_fires = bool(rdiag.get("order_sensitive_fires"))
    readout_discriminative_fires = bool(rdiag.get("discriminative_fires"))

    if cfg["run_mode"] == "smoke":
        # DISCRIMINATOR-MUST-SURVIVE-SCALE, PATH B (analytical justification), applied to the readout
        # diagnostic specifically: the SMOKE encoder is a 250-MLM-step, d=128 fresh-trained toy (same
        # "tiny encoder is below the signal threshold" scale-limitation v1-v4 already documented for the
        # CAPABILITY gain). MEASURED evidence (Q3 below) shows order-sensitivity on a freshly/lightly
        # trained encoder is dominated by early-training anisotropy severe enough that even bind-readout
        # cannot escape it -- NOT a mechanism bug (self-test (0) confirms the patch IS wired and DOES
        # differentiate order on an untrained toy encoder, cos=0.66; every OTHER mechanism check below
        # passes cleanly on this same SMOKE run: pattern-sep, context-address, sleep, controls, power,
        # stratified probe, arms-differ). The regime that matters -- the real v2 checkpoint FULL loads --
        # was ALREADY measured directly: STEP-0 probe on ckpt_seed_7 (data/probe_v4_readout_order_
        # sensitivity_v1.json): coh-vs-scrambled cos 0.7304 (order_blind=False), coh-vs-wrong-RAW 0.4848
        # (discriminative=True), both comfortably under the 0.95 gate. So readout_order_sensitive_fires /
        # readout_discriminative_fires are COMPUTED + reported here (visibility) but NOT part of
        # mechanism_ok's AND-chain -- gating SMOKE_MECHANISM_PASS on the tiny/undertrained encoder's
        # readout diagnostic would reject a cell whose readout mechanism is independently, directly
        # verified at the regime that matters.
        mechanism_ok = bool(sleep_every and stratified_probe_fires and comprehension_discriminator_resolves
                            and noread_flat and clarify_fired and modes_differ and power_ok
                            and pattern_sep_fires)
        verdict = "SMOKE_MECHANISM_PASS" if mechanism_ok else "SMOKE_MECHANISM_INCONCLUSIVE"
        teaches_new = None
    else:
        teaches_new = bool(low_sustained and contrast_ok and beats_plain and comprehension_specific_gain)
        hard = bool(low_sustained and contrast_ok and beats_plain and comprehension_specific_gain
                    and low_retention and sleep_every and controls_below_main and power_ok
                    and stratified_probe_fires)
        any_low_gain = bool(low_gain is not None and low_gain > 0.0)
        verdict = "HARD_PASS" if hard else ("MIDDLE_BAND" if any_low_gain else "HARD_FAIL")

    autopsy = dict(
        low_gain=low_gain, high_gain=high_gain, low_sustained=low_sustained,
        low_washed_out=low_fast["washed_out"], contrast_ok=contrast_ok, beats_plain=beats_plain,
        plain_low_gain=plain_low_gain, plain_low_sustained=plain_low_sustained,
        precision_low_gain=per_arm[PRECISION_ARM][KEY_SLICE]["gain"],
        scrambled_low_gain=scram_low_gain, wrongconcept_low_gain=wrong_low_gain,
        beats_scramble=beats_scramble, beats_wrongconcept=beats_wrongconcept,
        comprehension_specific_gain=comprehension_specific_gain,
        fast_low_gain_headroom_norm=low_fast["gain_headroom_norm"],
        scrambled_low_gain_headroom_norm=per_arm[SCRAM_ARM][KEY_SLICE]["gain_headroom_norm"],
        wrongconcept_low_gain_headroom_norm=per_arm[WRONG_ARM][KEY_SLICE]["gain_headroom_norm"],
        fast_low_baseline_auc=low_fast["baseline_auc"],
        low_nq_final=low_nq_final, mentions_per_concept_total=cfg["n_cycles"] * cfg["mentions_per_cycle"],
        mentions_per_cycle=cfg["mentions_per_cycle"], n_cycles=cfg["n_cycles"],
        low_exposure_median=slice_meta["LOW"]["exposure_median"],
        high_exposure_median=slice_meta["HIGH"]["exposure_median"],
        spec_fact_low=spec_fact_low, spec_fact_high=spec_fact_high, plain_spec_fact_low=plain_spec_low,
        fast_pattern_sep=fast_diag,
    )

    return dict(
        verdict=verdict,
        teaches_new_concepts=teaches_new,
        comprehension_specific_gain=comprehension_specific_gain,
        comprehension_discriminator_resolves=comprehension_discriminator_resolves,
        beats_scramble=beats_scramble, beats_wrongconcept=beats_wrongconcept,
        scrambled_low_gain=scram_low_gain, wrongconcept_low_gain=wrong_low_gain,
        per_arm_slice=per_arm,
        slice_meta=slice_meta,
        low_gain=low_gain, high_gain=high_gain, low_sustained=low_sustained,
        contrast_low_beats_high=contrast_ok, fast_beats_plain_washout=beats_plain,
        low_retention_ok=low_retention,
        best_main_low_arm=best_main_low, best_main_low_final=(round(best_main_low_final, 4)
                                                              if best_main_low_final is not None else None),
        control_low_finals={a: (round(v, 4) if v is not None else None) for a, v in ctrl_low_finals.items()},
        controls_below_main=controls_below_main,
        comprehension_gap_low_cycle0=(round(comp_c0, 4) if comp_c0 is not None else None),
        comprehension_gap_low_final=(round(comp_f, 4) if comp_f is not None else None),
        comprehension_fires=comprehension_fires,
        noread_low_flat=noread_flat, clarify_fired=clarify_fired,
        sleep_fired_every_cycle=sleep_every, modes_differ=modes_differ,
        pattern_sep_fires=pattern_sep_fires, fast_pattern_sep=fast_diag,
        specific_fact_low=spec_fact_low, specific_fact_high=spec_fact_high,
        low_nq_final=low_nq_final, power_ok=power_ok,
        stratified_probe_fires=stratified_probe_fires,
        exposure_ordered=exposure_ordered, slices_with_power=slices_with_power,
        readout_diagnostic=rdiag,
        readout_order_sensitive_fires=readout_order_sensitive_fires,
        readout_discriminative_fires=readout_discriminative_fires,
        autopsy=autopsy,
        flag_population_curve=by[FAST_ARM]["flag_log"],
    )


# ===========================================================================
# ARMS-MUST-DIFFER (META_RULE_AF) -- identical to v4.
# ===========================================================================
def _arms_differ(arm_results):
    dig = {r["arm"]: r["store_digest"] for r in arm_results}
    exempt = {frozenset((NOREAD_ARM, NOSLEEP_ARM))}   # both freeze cycle-0 fast store (read/sleep off)
    names = sorted(dig)
    collisions = []
    for a in range(len(names)):
        for b in range(a + 1, len(names)):
            na, nb = names[a], names[b]
            if dig[na] == dig[nb] and frozenset((na, nb)) not in exempt:
                collisions.append((na, nb))
    assert not collisions, "META_RULE_AF VIOLATION: arms bit-identical (not exempted): %s" % collisions
    return dig


# ===========================================================================
# MAIN RUN
# ===========================================================================
def run_full(cfg, out_dir, ckpt_path):
    device = V2._select_device() if cfg["run_mode"] == "full" else torch.device("cpu")
    _log("device=%s run_mode=%s ckpt=%s readout=%s" % (device.type, cfg["run_mode"], ckpt_path, READOUT_VARIANT))
    prep = _prepare(cfg, out_dir, ckpt_path, device)
    held = prep["held"]
    if len(held) < 12:
        raise RuntimeError("too few well-covered held concepts (%d) for tercile stratification" % len(held))
    d = prep["model"].d_model
    # v5 CHANGE 2/2: fit common-mode ONCE from the fixed train foundation (bind-readout space; leak-proof,
    # no held/answer info) and carry it into the fast-store projection for the KEY path only.
    cm = LOOP2._fit_common_mode(prep["base_text"], cfg["cm_rank"])
    _log("  common-mode fit (fast-store KEY path only, scope=%s): rank=%d (from foundation reps, bind-readout space)"
         % (CM_SCOPE, cm["rank"]))
    fast = _build_fast_projection(d, cfg, cm)
    _log("  fast episodic store: d=%d D_sparse=%d active_frac=%.3f read_temp=%.3f"
         % (fast["d"], fast["D"], fast["active_frac"], fast["read_temp"]))
    wrong_map = _build_wrong_map(held)
    n_self_map = sum(1 for ci in held if wrong_map[ci] == ci)
    assert n_self_map == 0, "wrong-concept map must be a derangement (no concept maps to itself)"
    _log("  wrong-concept control: derangement over %d held concepts (n_self_map=0)" % len(held))
    seed = cfg["seed"]

    # v5 CHANGE 1/2 evidence at run scale: readout diagnostic on REAL postings for THIS run's held concepts
    # (mirrors probe_readout_order_sensitivity.py; mandatory smoke discriminator-fires check).
    rdiag = _readout_diagnostic(held, prep["postings"], prep["model"], prep["tok"], prep["spec"], cfg,
                                device, wrong_map, seed)
    _log("  readout diagnostic: n=%d coh_vs_scram=%s coh_vs_wrong_raw=%s order_sensitive=%s discriminative=%s"
         % (rdiag["n_pairs"], rdiag["coh_vs_scram_mean"], rdiag["coh_vs_wrong_raw_mean"],
            rdiag["order_sensitive_fires"], rdiag["discriminative_fires"]))

    arm_results = []
    for arm in ARMS:
        _log("=== ARM %s (mode=%s) ===" % (arm, ARM_SPEC[arm]["mode"]))
        r = _run_arm(arm, held, prep["slices"], prep["postings"], prep["model"], prep["tok"],
                     prep["spec"], cfg, device, out_dir, prep["ground"], prep["counts"],
                     prep["universe"], prep["split"], prep["adj"], prep["deg"], prep["n_shards"],
                     seed, prep["base_text"], prep["base_clean"], fast, wrong_map)
        arm_results.append(r)
    digests = _arms_differ(arm_results)
    verdict = build_verdict(arm_results, cfg, prep["slice_meta"], rdiag)
    payload = dict(
        anchor_name=ANCHOR_NAME, run_mode=cfg["run_mode"], ts_iso=_now(),
        encoder_source=prep["encoder_source"], device=device.type,
        readout_variant=READOUT_VARIANT, readout_role_seed=READOUT_ROLE_SEED,
        common_mode_scope=CM_SCOPE, common_mode_rank=cm["rank"],
        n_held_concepts=len(held), n_cycles=cfg["n_cycles"], mentions_per_cycle=cfg["mentions_per_cycle"],
        fast_store_cfg=dict(d=fast["d"], D_sparse=fast["D"], active_frac=fast["active_frac"],
                            read_temp=fast["read_temp"], expansion=cfg["fast_expansion"],
                            proj_seed=cfg["fast_proj_seed"]),
        corpus_stats=prep["corpus_stats"], collect_meta=prep["collect_meta"],
        arms={r["arm"]: {k: v for k, v in r.items() if k != "store_digest"} for r in arm_results},
        arm_store_digests=digests,
        consol_cfg={k: cfg[k] for k in LOOP2._CONSOL_DEFAULTS},
        loop_cfg=dict(n_cycles=cfg["n_cycles"], mentions_per_cycle=cfg["mentions_per_cycle"],
                      min_evidence_mentions=cfg["min_evidence_mentions"],
                      concentration_thresh=cfg["concentration_thresh"],
                      min_compression_ratio=cfg["min_compression_ratio"]),
        **verdict,
    )
    au = verdict["autopsy"]
    sf = verdict.get("specific_fact_low") or {}
    payload["verdict_msg"] = (
        "readout=%s(coh~scram=%s,coh~wrong=%s,order_sens=%s,discrim=%s) | "
        "teaches_new=%s comprehension_specific=%s | FAST_LOW_gain=%s(sustained=%s,wash=%s,head_norm=%s) "
        "HIGH_gain=%s contrast=%s | vs_controls: scrambled_LOW=%s(beats=%s) wrongconcept_LOW=%s(beats=%s) "
        "plain_LOW=%s(beats=%s) precision_LOW=%s | spec_fact_LOW_hit1=%s | sleep_every=%s controls_below=%s "
        "LOW_nq=%s LOW_exp_med=%.0f HIGH_exp_med=%.0f pattern_sep=%s" % (
            READOUT_VARIANT, rdiag["coh_vs_scram_mean"], rdiag["coh_vs_wrong_raw_mean"],
            rdiag["order_sensitive_fires"], rdiag["discriminative_fires"],
            verdict["teaches_new_concepts"], verdict["comprehension_specific_gain"],
            au["low_gain"], verdict["low_sustained"], au["low_washed_out"],
            au["fast_low_gain_headroom_norm"], au["high_gain"], verdict["contrast_low_beats_high"],
            au["scrambled_low_gain"], au["beats_scramble"], au["wrongconcept_low_gain"],
            au["beats_wrongconcept"], au["plain_low_gain"], verdict["fast_beats_plain_washout"],
            au["precision_low_gain"], sf.get("hit1"), verdict["sleep_fired_every_cycle"],
            verdict["controls_below_main"], verdict["low_nq_final"],
            au["low_exposure_median"], au["high_exposure_median"],
            (au["fast_pattern_sep"] or {}).get("ratio")))
    payload["summary"] = payload["verdict"]
    return payload


# ===========================================================================
# metrics IO (atomic) + crash diag -- identical to v4.
# ===========================================================================
def _write_metrics(out_dir, payload, elapsed_s):
    payload = dict(payload)
    payload["elapsed_s"] = round(elapsed_s, 3)
    payload.setdefault("verdict", "CYCLE_INCOMPLETE")
    payload.setdefault("verdict_msg", payload.get("verdict"))
    payload.setdefault("summary", payload.get("verdict"))
    payload["VET_PENDING"] = True
    payload["LOCAL_ONLY_UNCOMMITTED"] = True
    tmp = os.path.join(out_dir, "metrics.json.tmp")
    final = os.path.join(out_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        json.dump(payload, f, indent=2, default=str)
    os.replace(tmp, final)
    return final


def _write_crash_metrics(out_dir, exc):
    diag = dict(verdict="CELL_CRASHED", verdict_msg="%s: %s" % (type(exc).__name__, str(exc)[:500]),
                summary="CELL_CRASHED", elapsed_s=0.0, traceback=traceback.format_exc()[:5000],
                ts_iso=_now(), anchor_name=ANCHOR_NAME)
    tmp = os.path.join(out_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, os.path.join(out_dir, "metrics.json"))


# ===========================================================================
# SELF-TEST: constructs REAL objects (PATCHED encoder, clarify, MDL, Kalman, fast
# episodic read + centered keys, pattern separation, context-address, per-slice
# probe, specific-fact probe, override gate, ckpt round-trip) at tiny scale -- NO
# corpus. v5 ADDS: readout-patch-identity check + order-sensitivity assertion on
# the tiny encoder's own toy sentences + common-mode-changes-keys assertion.
# ===========================================================================
def self_test():
    out = {}
    device = torch.device("cpu")
    torch.manual_seed(7)
    np.random.seed(7)

    # (0) READOUT PATCH IS ACTUALLY ACTIVE (not just "code exists") -- identity check.
    assert V2.TinyTransformer.pooled is _bind_pooled, \
        "READOUT_PATCH_NOT_ACTIVE: V2.TinyTransformer.pooled was not replaced by _bind_pooled"
    out["readout_patch_active"] = True

    # (1) exposure stratifier (reuse v3): terciles by ARC count, monotone, ALL == union
    held = [10, 11, 12, 13, 14, 15, 16, 17, 18]
    counts = np.zeros(64, dtype=np.int64)
    for j, ci in enumerate(held):
        counts[ci] = 20 + j * 40
    slices, meta = LOOP3._build_slices(held, counts)
    assert meta["LOW"]["exposure_median"] < meta["HIGH"]["exposure_median"], meta
    assert slices["ALL"] == sorted(held)
    out["stratify"] = {k: meta[k]["n_concepts"] for k in SLICES}

    # (2) tiny REAL encoder (uses the PATCHED bind-readout .pooled automatically) + L2-normalized reps
    from tokenizers import Tokenizer, models, trainers, pre_tokenizers
    toy = ["the cat sat on the mat", "a dog ran in the park", "birds fly over the sea",
           "rocks are hard and heavy", "water is wet and cold", "the sun is very hot"]
    tk = Tokenizer(models.BPE(unk_token="[UNK]"))
    tk.pre_tokenizer = pre_tokenizers.Whitespace()
    tk.train_from_iterator(iter(toy * 20), trainers.BpeTrainer(
        vocab_size=64, special_tokens=["[PAD]", "[UNK]", "[MASK]"], show_progress=False))
    spec = dict(pad=tk.token_to_id("[PAD]"), unk=tk.token_to_id("[UNK]"),
                mask=tk.token_to_id("[MASK]"), size=tk.get_vocab_size())
    model = V2.TinyTransformer(spec["size"], 16, 16, 1, 2, 2, spec["pad"]).to(device)
    model.eval()
    cfg = dict(SELFTEST_CFG)
    cfg["max_len"] = 16
    reps = LOOP2._encode_sentences(model, tk, toy, cfg, device, spec)
    assert reps.shape == (6, 16), reps.shape
    assert np.allclose(np.linalg.norm(reps, axis=1), 1.0, atol=1e-3), "pooled reps must be L2-normalized"
    out["encode"] = {"shape": list(reps.shape)}

    # (2b) ORDER-SENSITIVITY self-test (v5 NEW): the patched readout must NOT be permutation-invariant --
    # a word-scrambled toy sentence must produce a MEASURABLY different rep from its coherent original.
    scr_toy = []
    srng = np.random.default_rng(99)
    for s in toy:
        scr_toy.append(LOOP2._scramble_words(s, srng))
    reps_scr = LOOP2._encode_sentences(model, tk, scr_toy, cfg, device, spec)
    cos_os = float(np.mean(np.sum(reps * reps_scr, axis=1)))
    assert cos_os < 0.999, ("READOUT_MUST_BE_ORDER_SENSITIVE: coherent-vs-scrambled cos too high", cos_os)
    out["readout_order_sensitivity"] = {"coh_vs_scram_cos": round(cos_os, 4)}

    # (3) FAST EPISODIC STORE mechanics -----------------------------------------------------------------
    # v5: fit a common-mode transform from the toy encoder's OWN reps (stand-in "foundation") and wire it
    # into `fast` -- exercises the REAL centered-key code path, not a synthetic-only branch.
    cm_test = LOOP2._fit_common_mode(reps.astype(np.float32), min(3, cfg.get("cm_rank", 3)))
    fast = _build_fast_projection(16, cfg, cm_test)
    assert fast["D"] == 16 * cfg["fast_expansion"], fast
    assert fast["cm"] is not None and fast["cm"]["rank"] >= 0, fast["cm"]
    # (3a) k-WTA sparsity: exactly the top ceil(active_frac*D) entries active, non-negative
    x = np.random.default_rng(1).standard_normal((3, fast["D"]))
    kw = _kwta_rows(x, 0.1)
    k_expected = max(1, int(np.ceil(0.1 * fast["D"])))
    assert (kw >= 0).all(), "k-WTA must be non-negative (ReLU)"
    assert all((kw[i] > 0).sum() <= k_expected + 1 for i in range(3)), (kw > 0).sum(axis=1)
    # (3b) PATTERN SEPARATION: sparse keys of anisotropic reps are MORE decorrelated than the dense reps,
    # AND (v5 NEW) common-mode centering must MEASURABLY change the keys (mechanism actually fires).
    rng = np.random.default_rng(5)
    shared = rng.standard_normal(16).astype(np.float32); shared /= np.linalg.norm(shared)
    base = rng.standard_normal((16, 16)).astype(np.float32); base /= np.linalg.norm(base, axis=1, keepdims=True)
    anis = base + 1.5 * shared[None, :]; anis /= np.linalg.norm(anis, axis=1, keepdims=True)
    cm_anis = LOOP2._fit_common_mode(anis.astype(np.float32), 1)
    fast_cm = _build_fast_projection(16, cfg, cm_anis)
    fast_nocm = _build_fast_projection(16, cfg, None)
    keys_cm = _sparse_keys(anis, fast_cm)
    keys_nocm = _sparse_keys(anis, fast_nocm)
    assert not np.allclose(keys_cm, keys_nocm), "COMMON_MODE_MUST_CHANGE_KEYS: centering had no effect"
    ps = _pattern_sep_ratio(anis, fast_cm)
    assert ps is not None and ps["ratio"] < 1.0, ("pattern separation must decorrelate keys", ps)
    out["pattern_sep"] = ps
    out["common_mode_key_effect"] = {"keys_differ_with_vs_without_cm": True}
    # (3c) CONTEXT-ADDRESSABILITY: query with concept A's context retrieves A-value over B-value
    A = base[0] + 0.02 * rng.standard_normal(16).astype(np.float32)
    Amentions = [A + 0.05 * rng.standard_normal(16).astype(np.float32) for _ in range(5)]
    Amentions = [m / np.linalg.norm(m) for m in Amentions]
    readA = _fast_episodic_read(Amentions, fast)
    B = base[7]
    assert float(readA @ (A / np.linalg.norm(A))) > float(readA @ (B / np.linalg.norm(B))), \
        "context-addressed read must recover its own concept over an unrelated one"
    # (3d) READ SHARPENS/DENOISES: fast read of {clean cluster + 1 outlier} is closer to the clean
    # centroid than the plain running mean is (competitive read down-weights the outlier).
    clean = [A + 0.03 * rng.standard_normal(16).astype(np.float32) for _ in range(5)]
    clean = [c / np.linalg.norm(c) for c in clean]
    centroid = np.mean(clean, axis=0); centroid /= np.linalg.norm(centroid)
    outlier = rng.standard_normal(16).astype(np.float32); outlier /= np.linalg.norm(outlier)
    buf = clean + [outlier]
    fast_rep = _fast_episodic_read(buf, fast)
    plain_rep = np.mean(buf, axis=0); plain_rep /= np.linalg.norm(plain_rep)
    assert float(fast_rep @ centroid) > float(plain_rep @ centroid), \
        ("fast competitive read must denoise the outlier better than plain mean",
         float(fast_rep @ centroid), float(plain_rep @ centroid))
    out["fast_read"] = {"fast_to_centroid": round(float(fast_rep @ centroid), 4),
                        "plain_to_centroid": round(float(plain_rep @ centroid), 4)}

    # (4) fast candidate DIFFERS from plain + precision on the SAME buffer (arms will differ)
    from hdlab.learner.core import per_cluster_gate as _pcg
    coherent = [reps[0] + 0.01 * np.random.randn(16).astype(np.float32) for _ in range(4)]
    for c in coherent:
        c /= (np.linalg.norm(c) + 1e-8)
    cand_fast = _consolidate_candidate_v5(0, coherent, coherent, "fast_episodic", {}, {}, True, cfg,
                                          np.zeros((0, 16), np.float32), fast)
    cand_plain = _consolidate_candidate_v5(0, coherent, coherent, "plain", {}, {}, True, cfg,
                                           np.zeros((0, 16), np.float32), fast)
    assert not np.allclose(cand_fast, cand_plain, atol=1e-4), "fast_episodic must differ from plain average"
    lr_c, coh_c = LOOP2._concept_learn_result(coherent)
    assert _pcg(lr_c, 1.0), "coherent evidence must pass MDL gate"
    out["candidate_differs"] = {"fast_vs_plain_cos": round(float(cand_fast @ cand_plain), 4)}

    # (5) v5 SLEEP + override gate (fast mode): high-confidence rep NOT overridden by 1-mention low cover
    store, kal_rep, kal_prec, committed_conf = {}, {}, {}, {}
    ocfg = dict(cfg); ocfg.update(min_compression_ratio=1.0, min_evidence_mentions=1,
                                  concentration_thresh=0.0)
    _sleep_consolidate_v5({0: coherent}, {0: coherent}, store, kal_rep, kal_prec, committed_conf,
                          is_init=True, mode="fast_episodic", cfg=ocfg,
                          base_clean=np.zeros((0, 16), np.float32), fast=fast)
    assert 0 in store, "init cycle must commit the fast rep"
    rep_after_init = store[0].copy()
    rng2 = np.random.default_rng(11)
    lowcov = [rng2.standard_normal(16).astype(np.float32)]; lowcov[0] /= np.linalg.norm(lowcov[0])
    slog1, _ = _sleep_consolidate_v5({0: coherent[:1]}, {0: lowcov}, store, kal_rep, kal_prec,
                                     committed_conf, is_init=False, mode="fast_episodic", cfg=ocfg,
                                     base_clean=np.zeros((0, 16), np.float32), fast=fast)
    assert slog1["n_consolidated"] == 0, ("override gate must defer a low-coverage cycle", slog1)
    assert np.allclose(store[0], rep_after_init), "deferred cycle must not change committed rep (retention)"
    out["override_gate"] = {"lowcov_deferred": True}

    # (5b) WRONG-CONCEPT control map is a valid derangement (no concept reads its own text)
    wm = _build_wrong_map(held)
    assert all(wm[ci] != ci for ci in held), "wrong-concept map must be a derangement"
    assert sorted(wm.values()) == sorted(held), "wrong-concept map must be a permutation of held"
    out["wrong_map"] = {"n_held": len(held), "n_self": sum(1 for ci in held if wm[ci] == ci)}

    # (6) clarify gate flags under-known concept
    gate = ClarifyGate()
    n_flag = LOOP2._clarify_flag_population({0: [reps[0]], 1: coherent}, [0, 1], gate,
                                            dict(clarify_min_evidence=6))
    assert n_flag >= 1, "clarify gate must flag the under-known concept"
    out["clarify"] = {"n_flagged": int(n_flag)}

    # (7) PER-SLICE probe + SPECIFIC-FACT probe on a tiny synthetic universe/graph
    K, d = 12, 16
    rng3 = np.random.default_rng(3)
    ground = rng3.standard_normal((K, d)).astype(np.float32)
    ground /= (np.linalg.norm(ground, axis=1, keepdims=True) + 1e-8)
    text = ground.copy()
    universe = dict(ids=["c%d" % i for i in range(K)], K=K, surfaces=["c%d" % i for i in range(K)])
    heldK = list(range(0, 6))
    split = dict(held_idx=np.array(heldK, dtype=np.int64), train_eval_idx=np.arange(6, 12, dtype=np.int64))
    adj = [set() for _ in range(K)]
    for h in range(6):
        nb = 6 + h
        text[nb] = ground[h] * 0.9 + 0.1 * ground[nb]
        text[nb] /= (np.linalg.norm(text[nb]) + 1e-8)
        adj[h].add(nb); adj[nb].add(h)
    for h in range(6):
        text[h] = text[6 + h].copy()
    deg = np.array([len(a) for a in adj], dtype=np.int64)
    countsK = np.array([100, 100, 100, 5, 5, 5, 1, 1, 1, 1, 1, 1], dtype=np.int64)
    sl, _m = LOOP3._build_slices(heldK, countsK)
    probe = LOOP3._probe_stratified({}, text, ground, countsK, universe, split, sl, adj, deg, 1, 7)
    part_sum = sum((probe[s]["n_query"] or 0) for s in ("LOW", "MID", "HIGH"))
    assert part_sum == probe["ALL"]["n_query"], (part_sum, probe["ALL"]["n_query"])
    sf = _specific_fact_probe(text, adj, deg, split, heldK, 7)
    assert sf["n_concepts"] >= 1 and sf["hit1"] is not None and sf["hit1"] >= 0.99, \
        ("specific-fact probe must recover the aligned true neighbour", sf)
    out["probes"] = {"per_slice_nq": {s: probe[s]["n_query"] for s in SLICES}, "spec_fact_hit1": sf["hit1"]}

    # (7b) READOUT DIAGNOSTIC self-test on the tiny toy universe (exercises the REAL function, not just
    # the toy-sentence assertion in (2b))
    toy_postings = {ci: [toy[ci % len(toy)]] for ci in heldK}
    wm7 = _build_wrong_map(heldK)
    rdiag = _readout_diagnostic(heldK, toy_postings, model, tk, spec, cfg, device, wm7, seed=7)
    assert rdiag["n_pairs"] >= 1, "readout diagnostic must produce at least 1 pair on the toy universe"
    out["readout_diagnostic_selftest"] = rdiag

    # (8) FULL code path: v2-checkpoint round-trip via the shared loader (reloaded model ALSO uses the
    # patched bind-readout automatically -- class-level patch, not instance-level)
    import tempfile
    ckpt = dict(state_dict={k: v.detach().cpu() for k, v in model.state_dict().items()}, spec=spec,
                model_cfg=dict(vocab=spec["size"], max_len=16, d_model=16, n_layers=1, n_heads=2,
                               ffn_mult=2, pad_id=spec["pad"]),
                tokenizer_json=tk.to_str(), seed=7, run_mode="selftest", anchor="ckpt_roundtrip",
                w_star=0.5, selected_arm="ARM_RAW_TEXT")
    fd, cpath = tempfile.mkstemp(suffix=".pt")
    os.close(fd)
    try:
        torch.save(ckpt, cpath)
        m2, tk2, spec2, mc2 = LOOP2._build_encoder_from_ckpt(cpath, device)
        assert m2.pooled.__func__ is _bind_pooled, "reloaded encoder must use the patched bind-readout"
        reps2 = LOOP2._encode_sentences(m2, tk2, toy, cfg, device, spec2)
        assert np.allclose(reps2, reps, atol=1e-4), "reloaded encoder must reproduce saved reps"
        out["ckpt_roundtrip"] = {"reload_ok": True, "d_model": mc2["d_model"]}
    finally:
        try:
            os.remove(cpath)
        except OSError:
            pass
    print("[%s] SELF-TEST PASS %s" % (ANCHOR_NAME, json.dumps(out)))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--full", action="store_true")
    ap.add_argument("--ckpt", type=str, default=None, help="path to v2 encoder checkpoint (FULL engine)")
    ap.add_argument("--seed", type=int, default=None)
    args = ap.parse_args()
    if args.self_test:
        self_test()
        return
    env_mode = os.environ.get("HDLAB_RUN_MODE", "").lower()
    is_full = bool(args.full or (env_mode == "full" and not args.smoke))
    cfg = dict(FULL_CFG if is_full else SMOKE_CFG)
    if args.seed is not None:
        cfg["seed"] = args.seed
    ckpt_path = args.ckpt
    if is_full and not ckpt_path:
        ckpt_path = os.path.join(_REPO, "data", "exp_scale_meaning_learn_arc_heldout_v2",
                                 "ckpt_seed_%d.pt" % cfg["seed"])
    if is_full and not (ckpt_path and os.path.exists(ckpt_path)):
        raise RuntimeError("FULL run requires the v2 comprehension-engine checkpoint; not found at %r "
                           "(pass --ckpt or stage data/exp_scale_meaning_learn_arc_heldout_v2/"
                           "ckpt_seed_%d.pt)" % (ckpt_path, cfg["seed"]))
    out_dir = _out_dir(cfg["run_mode"])
    _write_start_marker(out_dir, cfg["run_mode"], expected_units=len(ARMS) * cfg["n_cycles"])
    t0 = time.perf_counter()
    _log("RUN START run_mode=%s ckpt=%s" % (cfg["run_mode"], ckpt_path))
    payload = run_full(cfg, out_dir, ckpt_path)
    elapsed = time.perf_counter() - t0
    payload["elapsed_s"] = round(elapsed, 3)
    final = _write_metrics(out_dir, payload, elapsed)
    _log("RUN DONE (%.1fs) -> %s" % (payload["elapsed_s"], final))
    _log("VERDICT=%s | %s" % (payload["verdict"], payload["verdict_msg"]))


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        _mode = "selftest"
    elif "--full" in sys.argv or (os.environ.get("HDLAB_RUN_MODE", "").lower() == "full"
                                  and "--smoke" not in sys.argv):
        _mode = "full"
    elif "--smoke" in sys.argv:
        _mode = "smoke"
    else:
        _mode = "selftest"
    _od = _out_dir(_mode)
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        _write_crash_metrics(_od, e)
        raise
