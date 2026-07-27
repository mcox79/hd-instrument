"""UNIFIED SELF-LEARNING LOOP v2 -- brain-faithful consolidation replaces plain mention-averaging.

v1 (unified_self_learning_loop_v1, MIDDLE_BAND) validated the whole loop MECHANISM (sleep fires every
cycle, comprehension real, controls clean, retention holds) but knowledge_gain WASHED OUT: main_curve
0.636 -> 0.641 (cycle2) -> 0.638 final (net +0.002, need +0.02) -- the plain-averaging DILUTION
signature (early reads help, then a uniform running mean regresses every concept toward the shared
cross-concept centroid = anisotropy/representation-degeneration).

v2 SWAPS ONLY the consolidation UPDATE rule (and adds a coverage-aware override gate). EVERYTHING ELSE
is reused verbatim from v1: the trained-encoder comprehension engine, clarify_gate FLAG, hippocampal
FAST-WRITE, MDL-gated SLEEP commit, the 3 loop-integrity controls, and the leak-proof relational probe.

CONSOLIDATION ABLATION (cumulative; per notes/drill_brainfaithful_consolidation_for_read_sleep_loop_
2026-07-27.md + notes/scour_prior_consolidation_fusion_selflearning_2026-07-27.md):
  plain        : v1 exact -- running mean over all accumulated mention reps (must reproduce wash-out).
  precision    : + precision-weighted KALMAN fold (gain K_t = p_mention/(prec_concept+p_mention); the
                 step SHRINKS as concept confidence grows; outlier mentions down-weighted by LOCAL
                 leave-one-out reliability -- fixes noise-dilution) + coverage-aware OVERRIDE GATE.
  precision_cm : + COMMON-MODE SUBTRACTION (all-but-the-top: strip the shared cross-concept direction(s)
                 from each mention BEFORE the Kalman fold; U/mu estimated once from the fixed foundation
                 -- fixes CENTROID-REGRESSION, the bias precision-weighting alone cannot remove).
  ca3          : + CA3-COMPLETION-before-write (denoise the consolidated readout toward the clean
                 foundation-rep manifold via a k-NN attractor step BEFORE committing; blind to the
                 answer graph -> leak-proof preserved). The full brain-faithful stack.

THE BAR (FULL): does a brain-faithful arm produce SUSTAINED knowledge_gain across cycles (gain > +0.02
AND final within WASHOUT_EPS of the peak = does NOT wash out) AND beat plain-averaging's wash-out --
while KEEPING sleep-fires-every-cycle + controls-below-main + retention-held + comprehension-real +
leak-proof (all validated in v1)? HARD_PASS = >=1 brain-faithful arm sustains gain>+0.02 AND its gain
beats plain's AND plain reproduces the wash-out (validates the anisotropy diagnosis).

BRAIN-FAITHFUL / INVARIANTS: TEACHER-FREE; NO borrowed vectors (OUR trained encoder only); GLASS-BOX
(symbolic gates + Kalman + streaming-PCA common-mode + k-NN attractor; no external LLM / no autograd at
inference); LEAK-PROOF (predicted edge disjoint from read text; CA3 blind to adjacency). ASCII-only.
Deterministic seeds. Store writes LOCAL-ONLY + UNCOMMITTED. Agent-reported VET-PENDING.

FULL loads the scale-v2 checkpoint (data/exp_scale_meaning_learn_arc_heldout_v2/ckpt_seed_<seed>.pt)
as the comprehension engine via --ckpt; SMOKE trains a tiny fresh encoder and validates the MECHANISM
(the across-cycle capability GAIN is FULL-deferred: a tiny encoder is below the signal threshold where
mention reps concentrate -- v1 MEASURED negative gain on tiny; the CM MECHANISM-fires check IS smoke-able).
"""
# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scale/floor):
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - final_metrics_atomicity: tmp_replace (os.replace)
# - crash-diagnostic metrics + start-marker + heartbeat
# - arms_differ_verified at smoke gate (NO_READ==READ_NO_SLEEP store exempted: both freeze cycle-0 by construction)
# - discriminator (SMOKE) = CM reduces cross-concept anisotropy + comprehension MAIN>SCRAMBLED (both FIRE on tiny)
# - discriminator (FULL) = sustained gain deferred to real ckpt (analytical justification path B; v1 MEASURED negative gain on tiny)
# - deterministic seeding (fixed ints + default_rng; no hash()/list(set()) ordering)
# - progress_logging: print_flush_true
# - self-test constructs REAL objects (encoder, clarify gate, learner gate, relational probe, Kalman, common-mode, CA3, override) at N~tiny, no corpus read
# - all reported numbers MEASURED@ this cell's metrics.json
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import sys
import json
import math
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
from hdlab.clarify_gate import ClarifyGate, GateOutcome
from hdlab.learner.core import LearnResult, per_cluster_gate

ANCHOR_NAME = "unified_self_learning_loop_v2"

# ---- arms: 4 MAIN consolidation-mode arms + 3 loop-integrity controls -------
# spec = (name, do_read, do_sleep, scramble, consolidation_mode)
ARM_SPECS = [
    ("MAIN_plainavg", True, True, False, "plain"),
    ("MAIN_precision", True, True, False, "precision"),
    ("MAIN_precision_cm", True, True, False, "precision_cm"),
    ("MAIN_ca3", True, True, False, "ca3"),
    ("NO_READ", False, True, False, "precision_cm"),
    ("SCRAMBLED", True, True, True, "precision_cm"),
    ("READ_NO_SLEEP", True, False, False, "precision_cm"),
]
ARMS = [s[0] for s in ARM_SPECS]
ARM_SPEC = {s[0]: dict(read=s[1], sleep=s[2], scramble=s[3], mode=s[4]) for s in ARM_SPECS}
MAIN_MODE_ARMS = ["MAIN_plainavg", "MAIN_precision", "MAIN_precision_cm", "MAIN_ca3"]
PLAIN_ARM = "MAIN_plainavg"
BRAINFAITHFUL_ARMS = ["MAIN_precision", "MAIN_precision_cm", "MAIN_ca3"]
NOREAD_ARM = "NO_READ"
SCRAM_ARM = "SCRAMBLED"
NOSLEEP_ARM = "READ_NO_SLEEP"
CONTROL_ARMS = [NOREAD_ARM, SCRAM_ARM, NOSLEEP_ARM]
CM_MODES = ("precision_cm", "ca3")   # arms whose reps live in common-mode-removed space
KALMAN_MODES = ("precision", "precision_cm", "ca3")

TEXT_KEY = "ARM_RAW_TEXT"
RAW_KEY = "ARM_RAW_GROUNDING"
SH_KEY = "ARM_COLLAPSE_SHUFFLE"
POP_KEY = "ARM_POPULARITY"

# ---------------------------------------------------------------------------
# Config profiles. Data keys mirror V2. Loop + consolidation keys are additive.
# ---------------------------------------------------------------------------
_CONSOL_DEFAULTS = dict(
    # precision-weighted Kalman
    prec_unit=1.0,                 # base precision scale of one fully-reliable mention
    prec_prior=0.25,               # concept prior precision (small -> big early steps, cold-start)
    prec_reliab_floor=0.05,        # min local reliability weight (never zero a mention entirely)
    prec_single_reliab=0.5,        # reliability when a cycle has a single mention (no siblings)
    # common-mode / anisotropy removal (all-but-the-top; estimated from fixed foundation reps)
    cm_rank=3,                     # number of top shared directions removed
    # CA3 completion-before-write (k-NN attractor step; blind to answer graph)
    ca3_k=8, ca3_alpha=0.7, ca3_iters=1, ca3_temp=0.10,
    # coverage-aware override gate (new read-knowledge overrides only when high-confidence/high-coverage)
    override_min=0.30,             # new evidence confidence must clear this to override at all
    override_cov_target=8.0,       # mentions for full coverage credit
    override_defer_eps=0.05,       # allow tiny confidence regressions; larger -> defer to existing rep
)

SELFTEST_CFG = dict(
    run_mode="selftest",
    n_cycles=3, mentions_per_cycle=2, min_evidence_mentions=2, clarify_min_evidence=6,
    concentration_thresh=0.0, min_compression_ratio=1.0,
    gain_margin_hp=0.0, clarify_seed=7,
    d_model=16, n_layers=1, n_heads=2, ffn_mult=2, max_len=16, vocab=64, encode_batch=32,
    **_CONSOL_DEFAULTS,
)
SMOKE_CFG = dict(
    run_mode="smoke", seed=7,
    min_deg=2, cap_eval_concepts=2500, heldout_count=250, min_mentions_eval=12,
    max_lines=160000, dedup_cap=200000, bpe_sample_lines=80000, cap_mentions=16,
    vocab=2048, max_len=40, train_token_budget=1500000, max_shards=6,
    d_model=128, n_layers=2, n_heads=4, ffn_mult=2,
    mlm_steps=250, mlm_batch=64, mlm_mask_frac=0.15, mlm_lr=3e-3,
    encode_batch=128, n_freq_buckets=5,
    n_cycles=4, mentions_per_cycle=3, min_evidence_mentions=3, clarify_min_evidence=12,
    concentration_thresh=0.15, min_compression_ratio=1.0,
    gain_margin_hp=0.0, clarify_seed=7,
    **_CONSOL_DEFAULTS,
)
FULL_CFG = dict(
    run_mode="full", seed=7,
    min_deg=2, cap_eval_concepts=None, heldout_count=800, min_mentions_eval=20,
    max_lines=10000000, dedup_cap=6000000, bpe_sample_lines=400000, cap_mentions=128,
    vocab=16000, max_len=128, train_token_budget=130000000, max_shards=16,
    d_model=512, n_layers=6, n_heads=8, ffn_mult=4,
    mlm_steps=60000, mlm_batch=128, mlm_mask_frac=0.15, mlm_lr=3e-4,
    encode_batch=256, n_freq_buckets=8,
    n_cycles=6, mentions_per_cycle=16, min_evidence_mentions=16, clarify_min_evidence=96,
    concentration_thresh=0.15, min_compression_ratio=1.0,
    gain_margin_hp=0.02, clarify_seed=7,
    **_CONSOL_DEFAULTS,
)

# HARD-PASS bands (FULL).
HP_GAIN_MARGIN = 0.02          # a brain-faithful arm's AUC[final]-AUC[0] must exceed this
WASHOUT_EPS = 0.01             # "sustained" = final within this of the peak (no wash-out)
HP_CONTROL_SEP = 0.0           # best MAIN[final] must exceed each control[final] by > this
RETENTION_EPS = 0.02           # an arm's AUC may never drop below AUC[0]-eps (no catastrophic forgetting)
MIN_QUERY_TASKS = 40           # relational power floor (SMOKE relaxed to 15)
CM_ANISOTROPY_EPS = 0.002      # SMOKE: precision_cm cross-concept sim must be < plain by > this


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
# Encoder: comprehension engine (train tiny for smoke, OR load v2 checkpoint)
# ===========================================================================
def _build_encoder_from_ckpt(ckpt_path, device):
    from tokenizers import Tokenizer
    ckpt = torch.load(ckpt_path, map_location="cpu")
    mc = ckpt["model_cfg"]
    model = V2.TinyTransformer(mc["vocab"], mc["max_len"], mc["d_model"], mc["n_layers"],
                               mc["n_heads"], mc["ffn_mult"], mc["pad_id"]).to(device)
    model.load_state_dict(ckpt["state_dict"])
    model.eval()
    tok = Tokenizer.from_str(ckpt["tokenizer_json"])
    spec = ckpt["spec"]
    return model, tok, spec, mc


def _encode_sentences(model, tok, sents, cfg, device, spec):
    if not sents:
        return np.zeros((0, model.d_model), dtype=np.float32)
    max_len = cfg["max_len"]
    pad_id = spec["pad"]
    X = np.stack([V2._encode_pad(tok, s, max_len, pad_id) for s in sents], axis=0)
    bs = cfg["encode_batch"]
    use_amp = (device.type == "cuda")
    out = []
    with torch.no_grad():
        for i in range(0, X.shape[0], bs):
            ids = torch.from_numpy(X[i:i + bs]).to(device)
            with torch.autocast(device_type=device.type, dtype=torch.float16, enabled=use_amp):
                pooled = model.pooled(ids)
            out.append(pooled.float().cpu().numpy())
    return np.concatenate(out, axis=0).astype(np.float32)


def _scramble_words(sent, rng):
    w = sent.split()
    if len(w) < 2:
        return sent
    order = rng.permutation(len(w))
    return " ".join(w[i] for i in order)


# ===========================================================================
# COMMON-MODE / anisotropy removal (all-but-the-top; Mu & Viswanath 2018).
# mu + top-cm_rank shared directions estimated ONCE from the FIXED foundation
# (train concept reps). Applied identically to held mentions AND to the base rep
# matrix so both sides of the relational cosine live in the same de-anisotropized
# space. This is the fix for centroid-regression (bias), not noise (variance).
# ===========================================================================
def _fit_common_mode(base_text, cm_rank):
    mask = np.linalg.norm(base_text, axis=1) > 1e-8
    B = base_text[mask].astype(np.float64)
    mu = B.mean(axis=0)
    Bc = B - mu
    # top-r right singular vectors of the centered foundation reps
    r = int(max(0, min(cm_rank, Bc.shape[1] - 1, Bc.shape[0] - 1)))
    if r == 0:
        U = np.zeros((base_text.shape[1], 0), dtype=np.float64)
    else:
        _, _, Vt = np.linalg.svd(Bc, full_matrices=False)
        U = Vt[:r].T  # (d, r)
    return dict(mu=mu.astype(np.float32), U=U.astype(np.float32), rank=int(r))


def _apply_common_mode(X, cm):
    """(n,d) -> de-anisotropized + L2-normalized (n,d). Subtract mean then top-r shared directions."""
    if X.size == 0:
        return X.astype(np.float32)
    Xc = X.astype(np.float64) - cm["mu"].astype(np.float64)
    U = cm["U"].astype(np.float64)
    if U.shape[1] > 0:
        Xc = Xc - (Xc @ U) @ U.T
    nrm = np.linalg.norm(Xc, axis=1, keepdims=True)
    nrm = np.where(nrm < 1e-8, 1.0, nrm)
    return (Xc / nrm).astype(np.float32)


def _mean_cross_concept_sim(store):
    """Mean pairwise cosine among committed held reps -> anisotropy/centroid-regression diagnostic.
    RISES under plain averaging (wash-out); FLAT/LOWER under common-mode removal."""
    if len(store) < 2:
        return None
    M = np.stack([store[ci] for ci in sorted(store.keys())], axis=0).astype(np.float64)
    nrm = np.linalg.norm(M, axis=1, keepdims=True)
    M = M / np.where(nrm < 1e-8, 1.0, nrm)
    G = M @ M.T
    n = M.shape[0]
    off = (G.sum() - np.trace(G)) / (n * (n - 1))
    return float(off)


# ===========================================================================
# PRECISION-WEIGHTED KALMAN fold + CA3-completion
# ===========================================================================
def _mention_precision(cycle_reps, cfg):
    """LOCAL per-mention precision (drill row 3: must be local, never a global statistic). Reliability =
    leave-one-out cosine agreement with the concept's OWN sibling mentions this cycle -> outliers (noise)
    down-weighted; clean corroborating mentions weighted up. Returns array (n,) of precisions."""
    X = np.asarray(cycle_reps, dtype=np.float64)
    n = X.shape[0]
    if n == 0:
        return np.zeros((0,), dtype=np.float64)
    if n == 1:
        return np.array([cfg["prec_unit"] * cfg["prec_single_reliab"]], dtype=np.float64)
    s = X.sum(axis=0)
    prec = np.empty((n,), dtype=np.float64)
    for t in range(n):
        loo = s - X[t]
        loo = loo / (np.linalg.norm(loo) + 1e-8)
        rel = (float(X[t] @ loo) + 1.0) / 2.0
        rel = max(cfg["prec_reliab_floor"], min(1.0, rel))
        prec[t] = cfg["prec_unit"] * rel
    return prec


def _kalman_fold(kal_rep, kal_prec, cycle_reps, cfg):
    """Fold this cycle's new mentions into the running estimate via precision-weighted Kalman updates.
    Innovation gain K_t = p_mention / (prec_concept + p_mention) -- the CORRECT Bayesian precision form:
    the step SHRINKS as prec_concept grows (confident concept moves little); an unreliable mention (low
    local precision) gets a small step. (Canonical Kalman/HGF form; the drill's row-1 K expression had
    the ratio inverted -- corrected here.) Returns (kal_rep, kal_prec)."""
    mu = np.asarray(kal_rep, dtype=np.float64)
    tau = float(kal_prec)
    prec = _mention_precision(cycle_reps, cfg)
    for t in range(len(cycle_reps)):
        v = np.asarray(cycle_reps[t], dtype=np.float64)
        p = float(prec[t])
        K = p / (tau + p)
        mu = mu + K * (v - mu)
        tau = tau + p
    return mu.astype(np.float64), tau


def _ca3_complete(rep, clean, cfg):
    """CA3-completion: denoise the consolidated readout toward the CLEAN foundation-rep manifold via a
    soft k-NN attractor step BEFORE write (scour note: pattern-completion-before-write beats naive avg).
    Uses ONLY text-derived foundation reps (clean); BLIND to the answer graph -> leak-proof preserved."""
    if clean.shape[0] == 0:
        return rep
    m = np.asarray(rep, dtype=np.float64)
    m = m / (np.linalg.norm(m) + 1e-8)
    C = clean.astype(np.float64)
    k = int(min(cfg["ca3_k"], C.shape[0]))
    for _ in range(int(cfg["ca3_iters"])):
        sims = C @ m
        idx = np.argpartition(-sims, k - 1)[:k]
        s = sims[idx]
        s = s - s.max()
        w = np.exp(s / max(1e-6, cfg["ca3_temp"]))
        w = w / (w.sum() + 1e-12)
        attractor = (w[:, None] * C[idx]).sum(axis=0)
        m = cfg["ca3_alpha"] * m + (1.0 - cfg["ca3_alpha"]) * attractor
        m = m / (np.linalg.norm(m) + 1e-8)
    return m.astype(np.float64)


# ===========================================================================
# SLEEP: MDL-gated consolidation (routes commit through hdlab.learner) with the
# selected consolidation UPDATE rule + coverage-aware override gate.
# ===========================================================================
def _concept_learn_result(reps):
    """MDL two-part-code over a concept's accumulated mention reps (unchanged from v1). The consolidated
    MEAN is the candidate rule; null = code each mention independently. Returns (LearnResult, coherence)."""
    X = np.asarray(reps, dtype=np.float64)
    n, d = X.shape
    mean = X.mean(axis=0)
    mn = mean / (np.linalg.norm(mean) + 1e-8)
    coherence = float(np.mean(X @ mn))
    resid_var = float(np.mean(np.sum((X - mean) ** 2, axis=1)))
    BITS = 32.0
    null_bits = float(n * d * BITS)
    desc_bits = float(d * BITS + n * d * math.log2(1.0 + resid_var + 1e-9))
    lr = LearnResult(plugin_name="concept_consolidation",
                     hypothesis={"coherence": round(coherence, 4), "n_mentions": int(n)},
                     is_episodic=False, description_bits=desc_bits, null_bits=null_bits,
                     n_free_params=int(d), cost_rank=1,
                     metrics={"coherence": coherence, "resid_var": resid_var})
    return lr, coherence


def _consolidate_candidate(ci, acc_reps, new_reps, mode, kal_rep, kal_prec, is_init, cfg, base_clean):
    """Compute the concept's candidate consolidated rep under the selected update rule. Advances the
    Kalman state in place (dicts). Returns unit-normalized candidate (d,)."""
    if mode == "plain":
        X = np.asarray(acc_reps, dtype=np.float64)
        m = X.mean(axis=0)
        return (m / (np.linalg.norm(m) + 1e-8)).astype(np.float32)
    # kalman modes (precision / precision_cm / ca3): fold THIS cycle's new mentions into running estimate
    if is_init or ci not in kal_rep:
        kal_rep[ci] = np.zeros(np.asarray(acc_reps[0]).shape[0], dtype=np.float64)
        kal_prec[ci] = float(cfg["prec_prior"])
    if len(new_reps) > 0:
        mu, tau = _kalman_fold(kal_rep[ci], kal_prec[ci], new_reps, cfg)
        kal_rep[ci] = mu
        kal_prec[ci] = tau
    cand = kal_rep[ci] / (np.linalg.norm(kal_rep[ci]) + 1e-8)
    if mode == "ca3":
        cand = _ca3_complete(cand, base_clean, cfg)
    return cand.astype(np.float32)


def _sleep_consolidate(acc_reps, new_reps, store, kal_rep, kal_prec, committed_conf,
                       is_init, mode, cfg, base_clean):
    """MDL-gated SLEEP over one cycle's buffer with the selected update rule. Commits a concept's rep into
    the working foundation store ONLY when MDL passes AND evidence is coherent+sufficient AND (for the
    brain-faithful modes) the coverage-aware OVERRIDE GATE allows it (new read-knowledge overrides an
    established rep only when high-confidence/high-coverage; else DEFER to the existing rep = retention).
    cycle-0 (is_init) initializes the foundation unconditionally. Returns (log, committed_ids)."""
    n_consolidated = 0
    n_kept_episodic = 0
    n_evaluated = 0
    committed_now = []
    cr_samples = []
    for ci, reps in acc_reps.items():
        if len(reps) < 1:
            continue
        n_evaluated += 1
        lr, coh = _concept_learn_result(reps)
        cr = float(lr.compression_ratio)
        mdl_ok = per_cluster_gate(lr, cfg["min_compression_ratio"])
        sufficient = (len(reps) >= cfg["min_evidence_mentions"]) and (coh >= cfg["concentration_thresh"])
        cand = _consolidate_candidate(ci, reps, new_reps.get(ci, []), mode, kal_rep, kal_prec,
                                      is_init, cfg, base_clean)
        # coverage-aware override gate (brain-faithful modes only; plain reproduces v1 exactly)
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
# FLAG: ClarifyGate flags concepts not-yet-known
# ===========================================================================
def _clarify_flag_population(acc_reps, held, gate, cfg):
    n_flagged = 0
    for ci in held:
        reps = acc_reps.get(ci, [])
        if len(reps) < 1:
            n_flagged += 1
            continue
        _lr, coh = _concept_learn_result(reps)
        suff = min(1.0, len(reps) / float(max(1, cfg["clarify_min_evidence"])))
        conf = ((coh + 1.0) / 2.0) * suff
        if gate.evaluate(conf) != GateOutcome.ACCEPT:
            n_flagged += 1
    return n_flagged


# ===========================================================================
# PROBE: leak-proof relational AUC on the consolidated foundation store
# ===========================================================================
def _store_to_text_matrix(store, base_text):
    text = base_text.copy()
    for ci, rep in store.items():
        text[ci] = rep
    return text


def _probe_relational(store, base_text, ground, counts, universe, split, adj, deg, n_shards, seed):
    text = _store_to_text_matrix(store, base_text)
    return V2.relational_eval(ground, text, counts, universe, split, adj, deg, n_shards, seed, 0.5)


# ===========================================================================
# ONE ARM: run the full cycle loop for a given arm-spec
# ===========================================================================
def _run_arm(arm, held, postings, model, tok, spec, cfg, device, out_dir,
             ground, counts, universe, split, adj, deg, n_shards, seed, base_text, base_text_cm, cm, base_clean):
    a = ARM_SPEC[arm]
    do_read, do_sleep, scramble, mode = a["read"], a["sleep"], a["scramble"], a["mode"]
    use_cm = mode in CM_MODES
    base_for_probe = base_text_cm if use_cm else base_text
    gate = ClarifyGate()
    store = {}
    kal_rep, kal_prec, committed_conf = {}, {}, {}
    acc_reps = {ci: [] for ci in held}
    n_cycles = cfg["n_cycles"]
    m = cfg["mentions_per_cycle"]
    curve, sleep_log, flag_log, xsim_curve, ncommit_curve = [], [], [], [], []
    for k in range(n_cycles):
        read_this_cycle = (k == 0) or do_read
        new_reps = {ci: [] for ci in held}
        if read_this_cycle:
            for ci in held:
                chunk = postings[ci][k * m:(k + 1) * m]
                if not chunk:
                    continue
                if scramble:
                    rng = np.random.default_rng(seed + 1009 * int(ci) + 31 * k)
                    chunk = [_scramble_words(s, rng) for s in chunk]
                reps = _encode_sentences(model, tok, chunk, cfg, device, spec)
                if use_cm:
                    reps = _apply_common_mode(reps, cm)
                for r in reps:
                    acc_reps[ci].append(r)
                    new_reps[ci].append(r)
        # FLAG
        n_flagged = _clarify_flag_population(acc_reps, held, gate, cfg)
        flag_log.append(n_flagged)
        # SLEEP
        is_init = (k == 0)
        if is_init or do_sleep:
            slog, _committed = _sleep_consolidate(acc_reps, new_reps, store, kal_rep, kal_prec,
                                                  committed_conf, is_init, mode, cfg, base_clean)
            # SLEEP-MUST-FIRE (v1 cycle2 bug fix): the consolidation step EXECUTED over >=1 candidate.
            assert slog["n_evaluated"] >= 1, (
                "SLEEP_DID_NOT_FIRE arm=%s cycle=%d (n_evaluated=0) -- the cycle2 sleep=False bug" % (arm, k))
        else:
            slog = dict(n_consolidated=0, n_kept_episodic=len(held), n_evaluated=0,
                        sample_commits=[], sleep_disabled=True)
        sleep_log.append(slog)
        ncommit_curve.append(slog["n_consolidated"])
        # PROBE
        rel = _probe_relational(store, base_for_probe, ground, counts, universe, split, adj, deg, n_shards, seed)
        auc = rel.get(TEXT_KEY)
        curve.append(auc)
        xsim = _mean_cross_concept_sim(store)
        xsim_curve.append(xsim)
        _log("  arm=%s mode=%s cycle=%d auc_text=%s xsim=%s n_query=%s n_flagged=%d n_consol=%d n_eval=%d"
             % (arm, mode, k, _fmt(auc), _fmt(xsim), rel.get("_n_query"), n_flagged,
                slog["n_consolidated"], slog["n_evaluated"]))
        _heartbeat(out_dir, unit_idx=k, total_units=n_cycles, elapsed_s=0.0,
                   extra={"arm": arm, "auc_text": auc, "xsim": xsim, "n_query": rel.get("_n_query")})
    text_final = _store_to_text_matrix(store, np.zeros_like(base_for_probe))
    digest = hashlib.sha256(np.ascontiguousarray(text_final).tobytes()).hexdigest()
    return dict(arm=arm, mode=mode, auc_curve=curve, xsim_curve=xsim_curve, sleep_log=sleep_log,
                flag_log=flag_log, ncommit_curve=ncommit_curve, n_query_final=rel.get("_n_query"),
                store_digest=digest, n_committed_final=len(store),
                raw_grounding_auc=rel.get(RAW_KEY), shuffle_auc=rel.get(SH_KEY), pop_auc=rel.get(POP_KEY))


# ===========================================================================
# DATA PREP (reuse V2 verbatim) + encoder acquisition + common-mode fit
# ===========================================================================
def _prepare(cfg, out_dir, ckpt_path, device):
    _log("data prep (universe/counts/split/postings/adjacency/grounding) ...")
    universe = V2.load_concept_universe(cfg)
    _log("  universe K=%d" % universe["K"])
    counts, cstats = V2.count_pass(cfg, universe["surf_to_idx"])
    _log("  corpus read=%d kept=%d tokens=%d" % (cstats["n_read"], cstats["n_kept"], cstats["total_alpha_tokens"]))
    split = V2.build_split(universe, counts, cfg)
    _log("  split heldout=%d train_eval=%d" % (len(split["held_idx"]), len(split["train_eval_idx"])))
    postings, bpe_lines, pmeta = V2.collect_pass(cfg, universe, split)
    adj, deg, n_shards = V2.load_adjacency(universe, cfg)
    ground = V2.build_grounding_reps(universe, split)
    if ckpt_path:
        _log("  loading trained v2 encoder from %s" % ckpt_path)
        model, tok, spec, mc = _build_encoder_from_ckpt(ckpt_path, device)
        _log("  encoder loaded: d=%d L=%d vocab=%d" % (mc["d_model"], mc["n_layers"], mc["vocab"]))
        encoder_source = "v2_checkpoint:" + os.path.basename(ckpt_path)
    else:
        _log("  training tiny fresh encoder (smoke; validates loop mechanism) ...")
        tok, spec = V2.build_bpe(bpe_lines, cfg["vocab"])
        stream, ntok = V2.tokenize_train_stream(cfg, tok, split, spec)
        _log("  train stream tokens=%d" % ntok)
        model, final_loss = V2.mlm_train(stream, spec, cfg, device, cfg["seed"], out_dir, cfg["mlm_steps"])
        _log("  tiny encoder trained final_loss=%.4f" % final_loss)
        encoder_source = "tiny_fresh_smoke"
    d = model.d_model
    K = universe["K"]
    need = cfg["n_cycles"] * cfg["mentions_per_cycle"]
    held_all = [int(i) for i in split["held_idx"].tolist()]
    held = sorted(ci for ci in held_all if len(postings[ci]) >= need)
    _log("  well-covered held concepts (>= %d mentions): %d / %d" % (need, len(held), len(held_all)))
    _log("  encoding fixed base reps for train foundation concepts ...")
    base_text, _mcnt = V2.encode_concept_text_reps(model, tok, postings, cfg, device, spec)
    base_text = base_text.astype(np.float32)
    hmask = np.zeros(K, dtype=bool)
    hmask[np.array(held, dtype=np.int64)] = True
    base_text[hmask] = 0.0
    _log("  base reps ready: %d train concepts with text" % int((np.linalg.norm(base_text, axis=1) > 1e-8).sum()))
    # common-mode fit from the FIXED foundation (train concept reps); apply to base for the CM-arm probe.
    cm = _fit_common_mode(base_text, cfg["cm_rank"])
    _log("  common-mode fit: rank=%d (from foundation reps)" % cm["rank"])
    base_text_cm = np.zeros_like(base_text)
    tmask = np.linalg.norm(base_text, axis=1) > 1e-8
    base_text_cm[tmask] = _apply_common_mode(base_text[tmask], cm)
    # CA3 clean attractor set = de-anisotropized foundation (train) reps only (leak-proof: text-derived)
    base_clean = base_text_cm[tmask].astype(np.float32)
    return dict(universe=universe, counts=counts, split=split, postings=postings, adj=adj, deg=deg,
                n_shards=n_shards, ground=ground, model=model, tok=tok, spec=spec, d=d, K=K,
                held=held, encoder_source=encoder_source, corpus_stats=cstats,
                collect_meta=pmeta, need_mentions=need, base_text=base_text, base_text_cm=base_text_cm,
                cm=cm, base_clean=base_clean)


# ===========================================================================
# VERDICT
# ===========================================================================
def _gain(curve):
    if not curve or curve[0] is None or curve[-1] is None:
        return None
    return curve[-1] - curve[0]


def _sustained(curve):
    """gain > HP_GAIN_MARGIN AND final within WASHOUT_EPS of the peak (does NOT wash out)."""
    g = _gain(curve)
    if g is None:
        return False, g, None
    vals = [c for c in curve if c is not None]
    peak = max(vals)
    washout = (curve[-1] < peak - WASHOUT_EPS)
    return bool(g > HP_GAIN_MARGIN and not washout), g, washout


def _retention_ok(curve):
    if not curve or curve[0] is None:
        return False
    rmin = min((c for c in curve if c is not None), default=None)
    return rmin is not None and rmin >= curve[0] - RETENTION_EPS


def _monotone_ish(curve, max_dips=1):
    dips = 0
    for a, b in zip(curve, curve[1:]):
        if a is None or b is None:
            return False
        if b < a - 1e-9:
            dips += 1
    return dips <= max_dips


def build_verdict(arm_results, cfg):
    by = {r["arm"]: r for r in arm_results}
    per_mode = {}
    for arm in MAIN_MODE_ARMS:
        curve = by[arm]["auc_curve"]
        sus, g, wash = _sustained(curve)
        per_mode[arm] = dict(
            mode=by[arm]["mode"],
            auc_curve=[(round(c, 4) if c is not None else None) for c in curve],
            xsim_curve=[(round(x, 4) if x is not None else None) for x in by[arm]["xsim_curve"]],
            gain=(round(g, 4) if g is not None else None),
            washed_out=wash, sustained=sus,
            retention_ok=_retention_ok(curve), monotone_ish=_monotone_ish(curve),
            sleep_executed_every_cycle=all(s.get("n_evaluated", 0) >= 1 for s in by[arm]["sleep_log"]),
            ncommit_curve=by[arm]["ncommit_curve"],
        )
    plain = per_mode[PLAIN_ARM]
    plain_gain = plain["gain"] if plain["gain"] is not None else -1.0
    # plain must reproduce the wash-out (validates the anisotropy diagnosis)
    plain_reproduces_washout = (not plain["sustained"])
    # winning brain-faithful arm = highest sustained gain that also beats plain
    winner, winner_gain = None, None
    for arm in BRAINFAITHFUL_ARMS:
        pm = per_mode[arm]
        if pm["sustained"] and pm["gain"] is not None and pm["gain"] > plain_gain:
            if winner_gain is None or pm["gain"] > winner_gain:
                winner, winner_gain = arm, pm["gain"]
    # best MAIN final AUC (for controls-below-main), and its curve for retention/comprehension refs
    best_arm = max(MAIN_MODE_ARMS, key=lambda a: (by[a]["auc_curve"][-1]
                   if by[a]["auc_curve"][-1] is not None else -1.0))
    best_final = by[best_arm]["auc_curve"][-1]
    ctrl_finals = {a: by[a]["auc_curve"][-1] for a in CONTROL_ARMS}
    controls_below_main = all(
        (best_final is not None and cf is not None and best_final > cf + HP_CONTROL_SEP) for cf in ctrl_finals.values())
    # comprehension: reference MAIN (precision_cm, matched-space with SCRAMBLED control) vs SCRAMBLED
    ref = "MAIN_precision_cm"
    ref_curve = by[ref]["auc_curve"]
    scram_curve = by[SCRAM_ARM]["auc_curve"]
    comp_c0 = ((ref_curve[0] - scram_curve[0]) if (ref_curve[0] is not None and scram_curve[0] is not None) else None)
    comp_f = ((ref_curve[-1] - scram_curve[-1]) if (ref_curve[-1] is not None and scram_curve[-1] is not None) else None)
    comprehension_fires = bool(comp_c0 is not None and comp_c0 > 0.0 and comp_f is not None and comp_f > 0.0)
    noread_curve = by[NOREAD_ARM]["auc_curve"]
    noread_flat = bool(max(noread_curve) - min(noread_curve) < 1e-6)
    clarify_fired = bool(max(by[ref]["flag_log"]) > 0)
    # common-mode reduces cross-concept anisotropy (the CM mechanism-fires check; fires even on tiny encoder)
    plain_xsim_f = by[PLAIN_ARM]["xsim_curve"][-1]
    cm_xsim_f = by["MAIN_precision_cm"]["xsim_curve"][-1]
    cm_reduces_anisotropy = bool(plain_xsim_f is not None and cm_xsim_f is not None
                                 and cm_xsim_f < plain_xsim_f - CM_ANISOTROPY_EPS)
    sleep_every = all(pm["sleep_executed_every_cycle"] for pm in per_mode.values())
    n_query = by[ref]["n_query_final"]
    power_floor = 15 if cfg["run_mode"] == "smoke" else MIN_QUERY_TASKS
    power_ok = (n_query is not None and n_query >= power_floor)
    modes_differ = (len({by[a]["store_digest"] for a in MAIN_MODE_ARMS}) == len(MAIN_MODE_ARMS))

    if cfg["run_mode"] == "smoke":
        mechanism_ok = bool(sleep_every and power_ok and comprehension_fires and noread_flat
                            and clarify_fired and modes_differ and cm_reduces_anisotropy)
        verdict = "SMOKE_MECHANISM_PASS" if mechanism_ok else "SMOKE_MECHANISM_INCONCLUSIVE"
    else:
        hard = bool(winner is not None and plain_reproduces_washout and sleep_every
                    and controls_below_main and comprehension_fires and power_ok
                    and per_mode[winner]["retention_ok"])
        any_gain = any((per_mode[a]["gain"] or -1) > 0 for a in BRAINFAITHFUL_ARMS)
        verdict = "HARD_PASS" if hard else ("MIDDLE_BAND" if any_gain else "HARD_FAIL")

    return dict(
        verdict=verdict,
        per_mode=per_mode,
        plain_gain=plain["gain"], plain_washed_out=plain["washed_out"],
        plain_reproduces_washout=plain_reproduces_washout,
        winning_consolidation=winner, winning_gain=(round(winner_gain, 4) if winner_gain is not None else None),
        sustains_gain=bool(winner is not None),
        best_main_arm=best_arm, best_main_final=(round(best_final, 4) if best_final is not None else None),
        control_finals={a: (round(v, 4) if v is not None else None) for a, v in ctrl_finals.items()},
        controls_below_main=controls_below_main,
        comprehension_gap_cycle0=(round(comp_c0, 4) if comp_c0 is not None else None),
        comprehension_gap_final=(round(comp_f, 4) if comp_f is not None else None),
        comprehension_fires=comprehension_fires,
        noread_flat=noread_flat, clarify_fired=clarify_fired,
        cm_reduces_anisotropy=cm_reduces_anisotropy,
        plain_xsim_final=(round(plain_xsim_f, 4) if plain_xsim_f is not None else None),
        cm_xsim_final=(round(cm_xsim_f, 4) if cm_xsim_f is not None else None),
        sleep_fired_every_cycle=sleep_every,
        modes_differ=modes_differ,
        n_query_final=n_query, power_ok=power_ok,
        flag_population_curve=by[ref]["flag_log"],
    )


# ===========================================================================
# ARMS-MUST-DIFFER (META_RULE_AF)
# ===========================================================================
def _arms_differ(arm_results):
    dig = {r["arm"]: r["store_digest"] for r in arm_results}
    # EXEMPT (NO_READ, READ_NO_SLEEP): both freeze the consolidated store at cycle-0 (same mode) by
    # construction -- sleep-off/read-off => reading changes nothing; THAT identity is the finding.
    exempt = {frozenset((NOREAD_ARM, NOSLEEP_ARM))}
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
    if len(held) < 8:
        raise RuntimeError("too few well-covered held concepts (%d) -- raise max_lines/cap_mentions or "
                           "lower n_cycles*mentions_per_cycle" % len(held))
    seed = cfg["seed"]
    arm_results = []
    for arm in ARMS:
        _log("=== ARM %s (mode=%s) ===" % (arm, ARM_SPEC[arm]["mode"]))
        r = _run_arm(arm, held, prep["postings"], prep["model"], prep["tok"], prep["spec"], cfg, device,
                     out_dir, prep["ground"], prep["counts"], prep["universe"], prep["split"],
                     prep["adj"], prep["deg"], prep["n_shards"], seed,
                     prep["base_text"], prep["base_text_cm"], prep["cm"], prep["base_clean"])
        arm_results.append(r)
    digests = _arms_differ(arm_results)
    verdict = build_verdict(arm_results, cfg)
    payload = dict(
        anchor_name=ANCHOR_NAME, run_mode=cfg["run_mode"], ts_iso=_now(),
        encoder_source=prep["encoder_source"], device=device.type,
        n_held_concepts=len(held), n_cycles=cfg["n_cycles"], mentions_per_cycle=cfg["mentions_per_cycle"],
        cm_rank=prep["cm"]["rank"],
        corpus_stats=prep["corpus_stats"], collect_meta=prep["collect_meta"],
        arms={r["arm"]: {k: v for k, v in r.items() if k != "store_digest"} for r in arm_results},
        arm_store_digests=digests,
        consol_cfg={k: cfg[k] for k in _CONSOL_DEFAULTS},
        loop_cfg=dict(n_cycles=cfg["n_cycles"], mentions_per_cycle=cfg["mentions_per_cycle"],
                      min_evidence_mentions=cfg["min_evidence_mentions"],
                      concentration_thresh=cfg["concentration_thresh"],
                      min_compression_ratio=cfg["min_compression_ratio"]),
        **verdict,
    )
    pm = verdict["per_mode"]
    payload["verdict_msg"] = (
        "winner=%s win_gain=%s | plain_gain=%s(wash=%s) precision=%s precision_cm=%s ca3=%s | "
        "sleep_every=%s controls_below=%s comprehension=%s n_query=%s" % (
            verdict["winning_consolidation"], verdict["winning_gain"],
            pm[PLAIN_ARM]["gain"], pm[PLAIN_ARM]["washed_out"],
            pm["MAIN_precision"]["gain"], pm["MAIN_precision_cm"]["gain"], pm["MAIN_ca3"]["gain"],
            verdict["sleep_fired_every_cycle"], verdict["controls_below_main"],
            verdict["comprehension_fires"], verdict["n_query_final"]))
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
# SELF-TEST: constructs REAL objects (encoder, clarify gate, learner MDL gate,
# relational probe, Kalman fold, common-mode removal, CA3 completion, override
# gate, full loop) at tiny synthetic scale -- NO corpus read.
# ===========================================================================
def self_test():
    out = {}
    device = torch.device("cpu")
    torch.manual_seed(7)
    np.random.seed(7)
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
    reps = _encode_sentences(model, tk, toy, cfg, device, spec)
    assert reps.shape == (6, 16), reps.shape
    assert np.allclose(np.linalg.norm(reps, axis=1), 1.0, atol=1e-3), "pooled reps must be L2-normalized"
    out["encode"] = {"shape": list(reps.shape)}

    # (2) learner MDL gate: coherent compresses -> commit; incoherent -> keep episodic
    coherent = [reps[0] + 0.01 * np.random.randn(16).astype(np.float32) for _ in range(4)]
    for c in coherent:
        c /= (np.linalg.norm(c) + 1e-8)
    lr_c, coh_c = _concept_learn_result(coherent)
    lr_i, coh_i = _concept_learn_result(list(reps[:4]))
    assert coh_c > coh_i, (coh_c, coh_i)
    assert per_cluster_gate(lr_c, 1.0), "coherent evidence must pass MDL compression gate"
    out["learner_gate"] = {"coherent_coh": round(coh_c, 4), "incoherent_coh": round(coh_i, 4)}

    # (3) ClarifyGate flag population
    gate = ClarifyGate()
    n_flag = _clarify_flag_population({0: [reps[0]], 1: coherent}, [0, 1], gate, dict(clarify_min_evidence=6))
    assert n_flag >= 1, "clarify gate must flag the under-known concept"
    out["clarify"] = {"n_flagged": int(n_flag)}

    # (4) COMMON-MODE removal: inject a shared direction into distinct reps; verify it reduces mean
    # pairwise cosine (de-anisotropization) -- the fix for centroid-regression.
    rng = np.random.default_rng(11)
    shared = rng.standard_normal(16).astype(np.float32); shared /= np.linalg.norm(shared)
    base = rng.standard_normal((20, 16)).astype(np.float32)
    base /= np.linalg.norm(base, axis=1, keepdims=True)
    anis = base + 1.6 * shared[None, :]
    anis /= np.linalg.norm(anis, axis=1, keepdims=True)
    cm = _fit_common_mode(anis, cm_rank=3)
    anis_cm = _apply_common_mode(anis, cm)
    sim_before = _mean_cross_concept_sim({i: anis[i] for i in range(20)})
    sim_after = _mean_cross_concept_sim({i: anis_cm[i] for i in range(20)})
    assert sim_after < sim_before - 1e-3, ("common-mode removal must lower cross-concept sim", sim_before, sim_after)
    assert np.allclose(np.linalg.norm(anis_cm, axis=1), 1.0, atol=1e-3)
    out["common_mode"] = {"rank": cm["rank"], "sim_before": round(sim_before, 4), "sim_after": round(sim_after, 4)}

    # (5) KALMAN fold: (a) confident concept moves less than a cold one for the same mention;
    # (b) a high-reliability cycle produces a larger precision increment than a noisy one.
    ccfg = dict(_CONSOL_DEFAULTS)
    v = reps[1].astype(np.float64)
    mu_cold, tau_cold = _kalman_fold(reps[0].astype(np.float64), ccfg["prec_prior"], [v], ccfg)
    mu_conf, tau_conf = _kalman_fold(reps[0].astype(np.float64), 20.0, [v], ccfg)
    step_cold = float(np.linalg.norm(mu_cold - reps[0]))
    step_conf = float(np.linalg.norm(mu_conf - reps[0]))
    assert step_conf < step_cold, ("confident concept must take a smaller step", step_conf, step_cold)
    clean_cycle = [reps[0] + 0.01 * np.random.randn(16).astype(np.float32) for _ in range(4)]
    for c in clean_cycle:
        c /= np.linalg.norm(c)
    noisy_cycle = list(rng.standard_normal((4, 16)).astype(np.float32))
    for c in noisy_cycle:
        c /= np.linalg.norm(c)
    p_clean = _mention_precision(clean_cycle, ccfg).sum()
    p_noisy = _mention_precision(noisy_cycle, ccfg).sum()
    assert p_clean > p_noisy, ("coherent cycle must yield more total precision than an incoherent one", p_clean, p_noisy)
    out["kalman"] = {"step_cold": round(step_cold, 4), "step_confident": round(step_conf, 4),
                     "prec_clean": round(float(p_clean), 4), "prec_noisy": round(float(p_noisy), 4)}

    # (6) CA3 completion pulls a noisy rep toward its clean nearest neighbour (uses only clean reps)
    clean_set = base.copy()
    target = clean_set[3]
    noisy = target + 0.9 * rng.standard_normal(16).astype(np.float32)
    noisy /= np.linalg.norm(noisy)
    completed = _ca3_complete(noisy, clean_set, dict(ca3_k=5, ca3_alpha=0.5, ca3_iters=2, ca3_temp=0.1))
    assert float(completed @ target) > float(noisy @ target), "CA3 completion must increase similarity to the clean attractor"
    out["ca3"] = {"sim_before": round(float(noisy @ target), 4), "sim_after": round(float(completed @ target), 4)}

    # (7) SLEEP with override gate: a high-confidence rep is NOT overridden by a low-coverage (1-mention) cycle
    store, kal_rep, kal_prec, committed_conf = {}, {}, {}, {}
    ocfg = dict(_CONSOL_DEFAULTS); ocfg.update(min_compression_ratio=1.0, min_evidence_mentions=1,
                                               concentration_thresh=0.0, override_min=0.30, override_cov_target=8.0)
    slog0, _ = _sleep_consolidate({0: coherent}, {0: coherent}, store, kal_rep, kal_prec, committed_conf,
                                  is_init=True, mode="precision", cfg=ocfg, base_clean=np.zeros((0, 16), np.float32))
    assert slog0["n_consolidated"] == 1 and 0 in store
    conf_after_init = committed_conf[0]
    rep_after_init = store[0].copy()
    lowcov = [rng.standard_normal(16).astype(np.float32)]; lowcov[0] /= np.linalg.norm(lowcov[0])
    slog1, _ = _sleep_consolidate({0: coherent[:1]}, {0: lowcov}, store, kal_rep, kal_prec, committed_conf,
                                  is_init=False, mode="precision", cfg=ocfg, base_clean=np.zeros((0, 16), np.float32))
    # 1-mention low coverage => new_conf < override_min or < prev-eps => deferred, store rep unchanged
    assert slog1["n_consolidated"] == 0, ("override gate must defer a low-coverage cycle", slog1)
    assert np.allclose(store[0], rep_after_init), "deferred cycle must not change the committed rep (retention)"
    out["override_gate"] = {"conf_init": round(float(conf_after_init), 4),
                            "n_consol_lowcov_cycle": slog1["n_consolidated"]}

    # (8) relational_eval probe code path on a tiny synthetic universe/graph
    K, d = 12, 16
    rng2 = np.random.default_rng(3)
    ground = rng2.standard_normal((K, d)).astype(np.float32)
    ground /= (np.linalg.norm(ground, axis=1, keepdims=True) + 1e-8)
    text = ground.copy()
    universe = dict(ids=["c%d" % i for i in range(K)], K=K, surfaces=["c%d" % i for i in range(K)])
    split = dict(held_idx=np.arange(0, 6, dtype=np.int64), train_eval_idx=np.arange(6, 12, dtype=np.int64))
    adj = [set() for _ in range(K)]
    for h in range(6):
        nb = 6 + h
        text[nb] = ground[h] * 0.9 + 0.1 * ground[nb]
        text[nb] /= (np.linalg.norm(text[nb]) + 1e-8)
        adj[h].add(nb); adj[nb].add(h)
    deg = np.array([len(a) for a in adj], dtype=np.int64)
    counts = np.ones(K, dtype=np.int64)
    rel = V2.relational_eval(ground, text, counts, universe, split, adj, deg, 1, 7, 0.5)
    assert rel.get("_n_query") is not None, "relational probe produced no queries"
    out["relational_probe"] = {"n_query": rel.get("_n_query"), "text_auc": rel.get(TEXT_KEY)}

    # (9) FULL code path: v2-checkpoint round-trip (the FULL comprehension-engine loader)
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
        m2, tk2, spec2, mc2 = _build_encoder_from_ckpt(cpath, device)
        reps2 = _encode_sentences(m2, tk2, toy, cfg, device, spec2)
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
    ap.add_argument("--ckpt", type=str, default=None, help="path to v2 encoder checkpoint (FULL comprehension engine)")
    ap.add_argument("--seed", type=int, default=None)
    args = ap.parse_args()
    if args.self_test:
        self_test()
        return
    # Run-mode resolution: the production runner (runner_v2_prod) invokes the script BARE and signals
    # FULL scope via HDLAB_RUN_MODE=full (it passes NO CLI flags). Honor that so a queue-dispatched run
    # loads the ckpt + FULL_CFG instead of silently falling to SMOKE (SCRIPT_PRECONDITION_VIOLATION).
    env_mode = os.environ.get("HDLAB_RUN_MODE", "").lower()
    is_full = bool(args.full or (env_mode == "full" and not args.smoke))
    cfg = dict(FULL_CFG if is_full else SMOKE_CFG)
    if args.seed is not None:
        cfg["seed"] = args.seed
    # ckpt resolution: explicit --ckpt wins; else FULL auto-resolves the seed's v2 checkpoint (the
    # comprehension engine). SMOKE trains a tiny fresh encoder (ckpt=None). Fail LOUD if FULL + missing.
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
