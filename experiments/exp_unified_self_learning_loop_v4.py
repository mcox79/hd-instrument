"""UNIFIED SELF-LEARNING LOOP v4 -- FAST EPISODIC STORE (CLS hippocampus) for learning NEW concepts.

v1/v2/v3 all represent a newly-read concept by folding its read-context mention reps INTO a SLOW rep
(plain running-mean, or precision-weighted Kalman) and measure relational placement on that SLOW rep.
Both WASH OUT: averaging into a well-trained encoder rep barely moves it and dilutes toward the shared
cross-concept centroid (anisotropy/centroid-regression). That is a SLOW-cortex nudge -- NOT how the brain
learns a new concept fast.

THE BRAIN-FAITHFUL FIX (Complementary Learning Systems; McClelland/McNaughton/O'Reilly 1995; the fast
hippocampal system is sparse, pattern-separated (dentate gyrus expansion recoding), high-plasticity,
context-addressed episodic): represent an under-known concept by a FAST rep built from a SEPARATE FAST
STORE of its read-context episodic traces, queryable IMMEDIATELY -- NOT a running-mean fold into the
pretrained rep. Consolidate to the slow encoder only slowly over many exposures (out of scope here).
Measure "did it learn" on the FAST rep (+ a direct specific-fact-acquired probe), not the averaged rep.
(Prior-art credit: CLS anchor = notes/research_brain_within_concept_floor_5x_drill_2026-06-22.md; that
framed a hippocampal side-channel to lower within-concept DECODE entropy. v4's use is DISTINCT: the fast
context-addressed store IS the concept rep for a newly-read concept, scored on relational placement per
pretraining-exposure slice. Design note: notes/research_fast_concept_learning_informs_selflearning_loop_
2026-07-27.md.)

THE FAST-EPISODIC-STORE MECHANISM (mode="fast_episodic"; the new arm):
  - PATTERN SEPARATION (DG-analog): each mention rep is recoded through a FIXED random expansion
    projection P (d -> D=expansion*d) + k-WTA sparsification (ReLU + top active_frac) -> a sparse,
    decorrelated KEY. Sparse expansion decorrelates keys so different concepts' traces do not interfere.
  - CONTEXT-ADDRESSED COMPETITIVE READ: the concept rep = a softmax(sparse-key . query)/temp weighted
    combination of the concept's episodic VALUES (values stay in d-dim encoder space = the probe's readout
    space). The query is the concept's accumulated read-context, recoded through the same P+k-WTA. This is
    a sharp, non-linear, pattern-separated read (a modern-Hopfield / attention read over episodic traces),
    NOT a linear running mean -- so it denoises outlier mentions AND avoids centroid regression.

ARMS (the discriminating axis = the READ-content and HOW a concept rep is computed from its mentions;
gating held IDENTICAL to isolate the variable, exactly as v3 isolated precision-vs-plain):
  MAIN_plainavg      : v2/v3 baseline running-mean (expected wash-out; validates the diagnosis).
  MAIN_precision     : slow precision-Kalman consolidate (the best v2 slow-rep arm; the slow contrast).
  MAIN_fast_episodic : the NEW fast episodic store (sparse / pattern-separated / context-addressed),
                       reading the concept's OWN coherent sentences (correct concept).
  SCRAMBLED          : WEAK control -- the concept's own sentences with words shuffled (bag-of-words
                       survives; v3 showed this is TOO WEAK -- it gained as much as coherent text).
  WRONG_CONCEPT      : STRONG control (NEW in v4) -- coherent grammatical English but about a DIFFERENT
                       concept (a deterministic derangement). Tests comprehension-specificity: if reading
                       the RIGHT content is not better than reading the WRONG content, the gain is pure
                       distributional sample-accumulation, not comprehension.
  NO_READ / READ_NO_SLEEP : loop-integrity controls (fast_episodic mode).

STRATIFICATION (v3 core): held concepts split into terciles by ARC pretraining mention count (exposure
proxy): LOW (under-known), MID, HIGH (v2-saturated), ALL. Reading is MATCHED across slices; the only
variable is pretraining exposure. THE BAR is on the LOW slice.

THE BAR (FULL; pre-registered -- v4 upgrades v3's bar per the loop-v3 VET redirect): MAIN_fast_episodic on
the LOW slice produces SUSTAINED knowledge_gain (LOW gain > +0.02 AND final within WASHOUT_EPS of the LOW
peak = no wash-out) AND -- THE LOAD-BEARING NEW GATE -- COMPREHENSION-SPECIFIC GAIN: its LOW gain EXCEEDS
BOTH the word-scrambled control's LOW gain AND the wrong-concept control's LOW gain (reading the right
content teaches more than reading scrambled OR wrong content) AND its LOW gain BEATS plain-average's LOW
gain (plain reproduces the wash-out) AND LOW gain > HIGH gain (teaches NEW > known), while keeping
sleep-fires-every-cycle + controls-below-main(LOW) + retention-held(LOW) + leak-proof + power. Gain is ALSO
reported headroom-normalized (gain/(1-baseline)) per slice, since LOW slices have more headroom. HARD_PASS =
the substrate LEARNS NEW concepts from GENUINE comprehension of reading via a fast episodic store.
DEFLATE (the honest null): if NO arm shows comprehension-specific gain (correct ~= scrambled ~= wrong on
the GAIN), the loop refines reps DISTRIBUTIONALLY but does NOT comprehend -- report that plainly; the path
to comprehension-learning is likely a READER that extracts STRUCTURED relations from sentences
(situation_reader), NOT encoder-rep pooling. If fast_episodic is flat on LOW, report per-slice power,
mentions/concept, gain magnitude, specific-fact hit@1 -- the per-item why-autopsy.

BRAIN-FAITHFUL / INVARIANTS: TEACHER-FREE; NO borrowed vectors (OUR trained encoder only); GLASS-BOX
(fixed random DG projection + k-WTA + symbolic gates + softmax read; no external LLM / no autograd at
inference); LEAK-PROOF (predicted edge disjoint from read text; probe negatives degree-matched, adjacency
excluded -- reused verbatim from V2.relational_eval + a matched per-concept specific-fact probe). ASCII-only.
Deterministic seeds (fixed ints + default_rng + fixed DG projection). Store writes LOCAL-ONLY + UNCOMMITTED.
Agent-reported VET-PENDING.

FULL loads the scale-v2 checkpoint (data/exp_scale_meaning_learn_arc_heldout_v2/ckpt_seed_<seed>.pt) as the
comprehension engine via --ckpt; SMOKE trains a tiny fresh encoder and validates the MECHANISM only (the
across-cycle capability GAIN is FULL-deferred -- a tiny encoder is below the signal threshold where mention
reps concentrate; v1/v2/v3 MEASURED negative/flat gain on tiny). The SMOKE discriminator: the fast-episodic
mechanism FIRES (pattern-separation lowers key cross-concept overlap; fast read differs from plain average;
context-addressability + read-sharpening in self-test) AND the exposure-stratified probe fires (>=2 slices,
monotone exposure) AND sleep/comprehension/controls/clarify all fire.
"""
# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scale/floor):
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - final_metrics_atomicity: tmp_replace (os.replace)
# - crash-diagnostic metrics + start-marker + heartbeat
# - arms_differ_verified at smoke gate (NO_READ==READ_NO_SLEEP store exempted: both freeze cycle-0)
# - discriminator (SMOKE) = fast-episodic mechanism fires (pattern-sep + arms differ + context-address +
#     read-sharpen self-test) + stratified probe fires + sleep/comprehension/controls/clarify fire (all tiny)
# - discriminator (FULL) = COMPREHENSION-SPECIFIC LOW-slice gain: fast_episodic correct-concept gain beats
#     BOTH word-scrambled AND wrong-concept controls' gain (+ beats plain wash-out) (real ckpt; path B
#     analytical: tiny encoder below signal threshold, per v1/v2/v3 MEASURED negative/flat on tiny)
# - baseline_in_band: MAIN_plainavg LOW-slice relational AUC ~0.5 (in [0.05,0.95]); smoke defers capability
# - crlb_n/a: directional gain gate, not a capacity/noise-floor threshold (no Cramer-Rao floor applies)
# - deterministic seeding (fixed ints + default_rng + fixed DG projection; no hash()/list(set()) ordering)
# - progress_logging: print_flush_true (timeout_s >= 1800)
# - self-test constructs REAL objects (encoder, clarify, MDL, Kalman, fast episodic read, pattern-sep,
#     context-address, per-slice probe, specific-fact probe, override gate, ckpt round-trip)
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

ANCHOR_NAME = "unified_self_learning_loop_v4"

# ---- arms: PLAIN baseline + PRECISION (slow contrast) + FAST_EPISODIC (new) + comprehension-specificity
# controls (v4: the v3 VET showed word-scramble is TOO WEAK -- bag-of-words survives it, so scrambled text
# produced AS MUCH gain as coherent text => the v3 gain was distributional sample-accumulation, NOT
# comprehension. v4 adds a STRONG WRONG_CONCEPT control: coherent grammatical English but about a DIFFERENT
# concept. The load-bearing discriminator is now COMPREHENSION-SPECIFIC GAIN: correct-concept reading must
# produce MORE across-cycle gain than BOTH word-scrambled AND wrong-concept reading.)
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

# fast episodic store (CLS hippocampus/DG) defaults -- glass-box, fixed, deterministic.
FAST_DEFAULTS = dict(
    fast_expansion=8,              # DG expansion recoding factor: D_sparse = expansion * d
    fast_active_frac=0.05,         # DG sparsity: fraction of expanded units kept active (k-WTA ~2-5%)
    fast_read_temp=0.05,           # softmax temperature of the context-addressed competitive read (sharp)
    fast_proj_seed=12345,          # fixed DG random projection seed (deterministic pattern separation)
)

# Base on v3 configs (LOW-exposure-qualifying schedule) + add the fast-store knobs.
SELFTEST_CFG = dict(LOOP3.SELFTEST_CFG); SELFTEST_CFG.update(FAST_DEFAULTS)
SMOKE_CFG = dict(LOOP3.SMOKE_CFG); SMOKE_CFG.update(FAST_DEFAULTS)
FULL_CFG = dict(LOOP3.FULL_CFG); FULL_CFG.update(FAST_DEFAULTS)

# HARD-PASS bands (FULL). Pre-registered (mirror v3; the KEY arm is fast_episodic not precision).
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
# FAST EPISODIC STORE (CLS hippocampus / DG): pattern separation + context read
# ===========================================================================
def _build_fast_projection(d, cfg):
    """Fixed random DG expansion projection P: (d, D) with D = expansion*d. Shared across ALL concepts
    (one dentate gyrus), deterministic (fixed seed). Gaussian random projection (Johnson-Lindenstrauss)."""
    D = int(cfg["fast_expansion"]) * int(d)
    rng = np.random.default_rng(int(cfg["fast_proj_seed"]))
    P = rng.standard_normal((int(d), D)).astype(np.float64) / np.sqrt(float(d))
    return dict(P=P, d=int(d), D=D, active_frac=float(cfg["fast_active_frac"]),
               read_temp=float(cfg["fast_read_temp"]))


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
    """Pattern-separate reps X (n,d) -> L2-normalized sparse keys (n,D). Empty-safe."""
    X = np.asarray(X, dtype=np.float64)
    if X.ndim != 2 or X.shape[0] == 0:
        return np.zeros((0, fast["D"]), dtype=np.float64)
    Kd = _kwta_rows(X @ fast["P"], fast["active_frac"])
    nrm = np.linalg.norm(Kd, axis=1, keepdims=True)
    return Kd / np.where(nrm < 1e-12, 1.0, nrm)


def _fast_episodic_read(reps, fast):
    """Context-addressed competitive read over a concept's episodic traces (values in encoder space).
    query = k-WTA(mean-context @ P); weights = softmax(sparse-key . query / temp); rep = weighted values.
    A sharp non-linear pattern-separated read -- denoises outliers + avoids centroid regression. Returns
    L2-normalized (d,)."""
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
# v4 SLEEP: identical to LOOP2._sleep_consolidate but dispatches the fast_episodic
# candidate. Gating held IDENTICAL to the kalman modes (coverage-override gate) so
# the ONLY variable between fast_episodic and precision is the READ. (plain keeps
# no gate, exactly as v2/v3.)
# ===========================================================================
def _consolidate_candidate_v4(ci, reps, new_reps, mode, kal_rep, kal_prec, is_init, cfg, base_clean, fast):
    if mode == "fast_episodic":
        return _fast_episodic_read(reps, fast)         # fresh competitive read of the FULL episodic buffer
    return LOOP2._consolidate_candidate(ci, reps, new_reps, mode, kal_rep, kal_prec, is_init, cfg, base_clean)


def _sleep_consolidate_v4(acc_reps, new_reps, store, kal_rep, kal_prec, committed_conf,
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
        cand = _consolidate_candidate_v4(ci, reps, new_reps.get(ci, []), mode, kal_rep, kal_prec,
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
# SPECIFIC-FACT probe: per-concept "did it acquire the SPECIFIC just-read fact"?
# hit@1 / MRR of the concept's TRUE train-neighbour vs degree-matched non-neighbour
# negatives, scored by rep cosine. Leak-proof exclusion identical to relational_eval
# (adjacency excluded from negatives; rep has zero relational input; read text disjoint
# from the predicted edge). Cheap (reuses text/adj/deg). Computed at the FINAL cycle.
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
# WRONG-CONCEPT map: deterministic derangement of held concepts. The strong
# comprehension control reads a DIFFERENT concept's coherent sentences in place of
# the concept's own -- grammatical English, but false-for-this-concept content.
# ===========================================================================
def _build_wrong_map(held):
    order = sorted(int(c) for c in held)
    n = len(order)
    shift = max(1, n // 2)                 # != 0 and != n for n>=2 -> guaranteed derangement
    return {order[i]: order[(i + shift) % n] for i in range(n)}


# ===========================================================================
# ONE ARM: stratified cycle loop (per-slice AUC curves) with the v4 sleep + fast diag
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
            slog, _committed = _sleep_consolidate_v4(acc_reps, new_reps, store, kal_rep, kal_prec,
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
    # specific-fact probe (LOW + HIGH) at the final store
    spec_fact = {}
    for s in ("LOW", "HIGH", "ALL"):
        spec_fact[s] = _specific_fact_probe(text_final, adj, deg, split, slices[s], seed)
    # fast-store mechanism diagnostic (only meaningful for the fast_episodic arm)
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
# DATA PREP (reuse v3 verbatim: v2 loop prep + exposure slices)
# ===========================================================================
def _prepare(cfg, out_dir, ckpt_path, device):
    return LOOP3._prepare(cfg, out_dir, ckpt_path, device)


# ===========================================================================
# VERDICT helpers
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
    """gain / (1 - baseline): normalizes for the fact that low-exposure (LOW) slices have more headroom.
    A large raw gain that is merely filling headroom is a WEAKER signal than the raw number suggests."""
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


def build_verdict(arm_results, cfg, slice_meta):
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
    # fast BEATS plain wash-out on LOW: fast LOW gain > plain LOW gain AND plain does NOT sustain (washes)
    beats_plain = bool(low_gain is not None and plain_low_gain is not None
                       and low_gain > plain_low_gain and (not plain_low_sustained))

    # ---- COMPREHENSION-SPECIFIC GAIN (the load-bearing v4 discriminator; per the loop-v3 VET redirect) --
    # Correct-concept reading must produce MORE across-cycle GAIN than BOTH the weak word-scramble control
    # AND the strong wrong-concept control. If correct ~= scrambled ~= wrong-concept on the GAIN, the loop
    # is refining reps distributionally (sample-accumulation + headroom), NOT comprehending.
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

    # comprehension: fast LOW-slice AUC beats SCRAMBLED LOW-slice AUC at c0 and final
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

    # arms differ (plain vs fast store digests distinct); pattern separation fires (fast_diag ratio < 1)
    modes_differ = (by[PLAIN_ARM]["store_digest"] != by[FAST_ARM]["store_digest"]
                    and by[PRECISION_ARM]["store_digest"] != by[FAST_ARM]["store_digest"])
    fast_diag = by[FAST_ARM].get("fast_diag")
    pattern_sep_fires = bool(fast_diag is not None and fast_diag.get("ratio") is not None
                             and fast_diag["ratio"] < 1.0 - PATTERN_SEP_EPS)

    spec_fact_low = by[FAST_ARM]["spec_fact"].get("LOW")
    spec_fact_high = by[FAST_ARM]["spec_fact"].get("HIGH")
    plain_spec_low = by[PLAIN_ARM]["spec_fact"].get("LOW")

    # SMOKE comprehension-discriminator check: prove the correct/scrambled/wrong-concept read arms are
    # genuinely different reads the discriminator can RESOLVE (distinct LOW gains) -- NOT that correct
    # beats them (that DIRECTION is the FULL capability question, path-B deferred to the real encoder).
    _rc_gains = [g for g in (low_gain, scram_low_gain, wrong_low_gain) if g is not None]
    comprehension_discriminator_resolves = bool(len(_rc_gains) == 3 and (max(_rc_gains) - min(_rc_gains) > 0.005))

    if cfg["run_mode"] == "smoke":
        mechanism_ok = bool(sleep_every and stratified_probe_fires and comprehension_discriminator_resolves
                            and noread_flat and clarify_fired and modes_differ and power_ok
                            and pattern_sep_fires)
        verdict = "SMOKE_MECHANISM_PASS" if mechanism_ok else "SMOKE_MECHANISM_INCONCLUSIVE"
        teaches_new = None
    else:
        # teaches_new (genuine comprehension-learning) REQUIRES comprehension-specific gain -- the v4
        # load-bearing bar. Sustained + contrast + beats-plain-washout are necessary but NOT sufficient
        # (v3 met those on a distributional artifact). comprehension_specific_gain is the new gate.
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
        autopsy=autopsy,
        flag_population_curve=by[FAST_ARM]["flag_log"],
    )


# ===========================================================================
# ARMS-MUST-DIFFER (META_RULE_AF)
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
    _log("device=%s run_mode=%s ckpt=%s" % (device.type, cfg["run_mode"], ckpt_path))
    prep = _prepare(cfg, out_dir, ckpt_path, device)
    held = prep["held"]
    if len(held) < 12:
        raise RuntimeError("too few well-covered held concepts (%d) for tercile stratification" % len(held))
    d = prep["model"].d_model
    fast = _build_fast_projection(d, cfg)
    _log("  fast episodic store: d=%d D_sparse=%d active_frac=%.3f read_temp=%.3f"
         % (fast["d"], fast["D"], fast["active_frac"], fast["read_temp"]))
    wrong_map = _build_wrong_map(held)
    n_self_map = sum(1 for ci in held if wrong_map[ci] == ci)
    assert n_self_map == 0, "wrong-concept map must be a derangement (no concept maps to itself)"
    _log("  wrong-concept control: derangement over %d held concepts (n_self_map=0)" % len(held))
    seed = cfg["seed"]
    arm_results = []
    for arm in ARMS:
        _log("=== ARM %s (mode=%s) ===" % (arm, ARM_SPEC[arm]["mode"]))
        r = _run_arm(arm, held, prep["slices"], prep["postings"], prep["model"], prep["tok"],
                     prep["spec"], cfg, device, out_dir, prep["ground"], prep["counts"],
                     prep["universe"], prep["split"], prep["adj"], prep["deg"], prep["n_shards"],
                     seed, prep["base_text"], prep["base_clean"], fast, wrong_map)
        arm_results.append(r)
    digests = _arms_differ(arm_results)
    verdict = build_verdict(arm_results, cfg, prep["slice_meta"])
    payload = dict(
        anchor_name=ANCHOR_NAME, run_mode=cfg["run_mode"], ts_iso=_now(),
        encoder_source=prep["encoder_source"], device=device.type,
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
        "teaches_new=%s comprehension_specific=%s | FAST_LOW_gain=%s(sustained=%s,wash=%s,head_norm=%s) "
        "HIGH_gain=%s contrast=%s | vs_controls: scrambled_LOW=%s(beats=%s) wrongconcept_LOW=%s(beats=%s) "
        "plain_LOW=%s(beats=%s) precision_LOW=%s | spec_fact_LOW_hit1=%s | sleep_every=%s controls_below=%s "
        "LOW_nq=%s LOW_exp_med=%.0f HIGH_exp_med=%.0f pattern_sep=%s" % (
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
# metrics IO (atomic) + crash diag
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
# SELF-TEST: constructs REAL objects (encoder, clarify, MDL, Kalman, fast episodic
# read, pattern separation, context-address, per-slice probe, specific-fact probe,
# override gate, ckpt round-trip) at tiny scale -- NO corpus.
# ===========================================================================
def self_test():
    out = {}
    device = torch.device("cpu")
    torch.manual_seed(7)
    np.random.seed(7)

    # (1) exposure stratifier (reuse v3): terciles by ARC count, monotone, ALL == union
    held = [10, 11, 12, 13, 14, 15, 16, 17, 18]
    counts = np.zeros(64, dtype=np.int64)
    for j, ci in enumerate(held):
        counts[ci] = 20 + j * 40
    slices, meta = LOOP3._build_slices(held, counts)
    assert meta["LOW"]["exposure_median"] < meta["HIGH"]["exposure_median"], meta
    assert slices["ALL"] == sorted(held)
    out["stratify"] = {k: meta[k]["n_concepts"] for k in SLICES}

    # (2) tiny REAL encoder + L2-normalized pooled reps
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

    # (3) FAST EPISODIC STORE mechanics -----------------------------------------------------------------
    fast = _build_fast_projection(16, cfg)
    assert fast["D"] == 16 * cfg["fast_expansion"], fast
    # (3a) k-WTA sparsity: exactly the top ceil(active_frac*D) entries active, non-negative
    x = np.random.default_rng(1).standard_normal((3, fast["D"]))
    kw = _kwta_rows(x, 0.1)
    k_expected = max(1, int(np.ceil(0.1 * fast["D"])))
    assert (kw >= 0).all(), "k-WTA must be non-negative (ReLU)"
    assert all((kw[i] > 0).sum() <= k_expected + 1 for i in range(3)), (kw > 0).sum(axis=1)
    # (3b) PATTERN SEPARATION: sparse keys of anisotropic reps are MORE decorrelated than the dense reps
    rng = np.random.default_rng(5)
    shared = rng.standard_normal(16).astype(np.float32); shared /= np.linalg.norm(shared)
    base = rng.standard_normal((16, 16)).astype(np.float32); base /= np.linalg.norm(base, axis=1, keepdims=True)
    anis = base + 1.5 * shared[None, :]; anis /= np.linalg.norm(anis, axis=1, keepdims=True)
    ps = _pattern_sep_ratio(anis, fast)
    assert ps is not None and ps["ratio"] < 1.0, ("pattern separation must decorrelate keys", ps)
    out["pattern_sep"] = ps
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
    cand_fast = _consolidate_candidate_v4(0, coherent, coherent, "fast_episodic", {}, {}, True, cfg,
                                          np.zeros((0, 16), np.float32), fast)
    cand_plain = _consolidate_candidate_v4(0, coherent, coherent, "plain", {}, {}, True, cfg,
                                           np.zeros((0, 16), np.float32), fast)
    assert not np.allclose(cand_fast, cand_plain, atol=1e-4), "fast_episodic must differ from plain average"
    lr_c, coh_c = LOOP2._concept_learn_result(coherent)
    assert _pcg(lr_c, 1.0), "coherent evidence must pass MDL gate"
    out["candidate_differs"] = {"fast_vs_plain_cos": round(float(cand_fast @ cand_plain), 4)}

    # (5) v4 SLEEP + override gate (fast mode): high-confidence rep NOT overridden by 1-mention low cover
    store, kal_rep, kal_prec, committed_conf = {}, {}, {}, {}
    ocfg = dict(cfg); ocfg.update(min_compression_ratio=1.0, min_evidence_mentions=1,
                                  concentration_thresh=0.0)
    _sleep_consolidate_v4({0: coherent}, {0: coherent}, store, kal_rep, kal_prec, committed_conf,
                          is_init=True, mode="fast_episodic", cfg=ocfg,
                          base_clean=np.zeros((0, 16), np.float32), fast=fast)
    assert 0 in store, "init cycle must commit the fast rep"
    rep_after_init = store[0].copy()
    rng2 = np.random.default_rng(11)
    lowcov = [rng2.standard_normal(16).astype(np.float32)]; lowcov[0] /= np.linalg.norm(lowcov[0])
    slog1, _ = _sleep_consolidate_v4({0: coherent[:1]}, {0: lowcov}, store, kal_rep, kal_prec,
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
    # held reps ALIGNED to their true neighbour so specific-fact hit@1 fires (a learned placement)
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

    # (8) FULL code path: v2-checkpoint round-trip via the shared loader
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
