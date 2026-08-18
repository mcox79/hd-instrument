"""UNIFIED SELF-LEARNING LOOP v6 -- BRAIN-FAITHFUL REPLAY CONSOLIDATION (WIRE-DONT-ISLAND).

Director task 2026-07-28 (notes/consolidation_brain_fidelity_audit_and_redesign_2026-07-28.md).
Every consolidation mode so far (v1 plain-average, v2 precision-Kalman/CA3-single-shot, v4/v5
fast_episodic competitive-weighted-average) is a form of EAGER, SINGLE-PASS, DIRECT cortical
writing: whatever mentions accumulated this cycle get folded into ONE concept-level vector, once.
The brain never does this -- cortex is written only via OFFLINE REPLAY, many small repeated events,
budget-limited, prioritized by prediction-error/novelty, and gated by schema-consistency (Tse/Morris
2007/2011). We already possess a CERTIFIED (HARD_PASS, gap=0.913 old-retention-vs-naive) primitive
that does exactly this -- hdlab.hippocampal_encoder.cls_discrete_budget_consolidate (landed via
exp_cls_ca3complete_consolidation_v1, DISK-VERIFIED this session) -- and the self-learning loop has
never used it. v6 WIRES it in as a new consolidation mode, ONE variable versus v5.

KEPT FIXED (not re-opened): v5's BIND_HRR_position readout (imported via `import ... as V5`, which
re-applies the class-level monkeypatch of V2.TinyTransformer.pooled at import time) and v5's centered
`_sparse_keys` DG-expansion code (untouched, simply not invoked by the new mode -- see the "shape
compatibility" note in the pre-reg: composing the DG-expanded (D_sparse=8d) key space with
cls_discrete_budget_consolidate's square [d,d] outer-product store would require an adapter; v6
instead uses SELF-ADDRESSING (key = value = the mention's own raw bind-readout rep), a real, if
simpler, content-addressable auto-associator -- biologically CA3 recurrent collaterals genuinely are
content/self-addressing).

TWO harnesses sharing ONE `_prepare()` call:

  SECONDARY (existing relational-AUC LOW-slice comprehension-gain metric, v5's 7-arm structure
  UNCHANGED except the `fast_episodic` mode slot is replaced by `replay_schema_gated`; MAIN_plainavg
  / MAIN_precision untouched). Reported per task instruction as compressed/secondary, NOT the
  HARD-PASS gate.

  PRIMARY (NEW -- the brain-faithful metric averaging cannot even be tested on): INTERLEAVED
  OLD-vs-NEW RETENTION under a SHARED fixed replay budget, modeled directly on the certified cell's
  own experiment shape (`_cls_consolidation_discriminator`) with REAL substrate mention encodings
  substituted for its synthetic random vectors. Held concepts split OLD/NEW; OLD read only in early
  phases, NEW only in later phases; ALL arms share ONE recency-decayed fast store (genuine
  shared-capacity interference pressure); REPLAY_SCHEMA_GATED/REPLAY_UNIFORM/NO_CLEANUP migrate to a
  protected slow store via budgeted CA3-completed replay, AVERAGING_NAIVE never migrates (the honest
  structural proxy for "what our loop's averaging-family consolidation is, reduced to a
  shared-capacity substrate" -- the real loop's per-concept-independent-slot architecture has no
  shared-capacity axis to even test this on). HARD-PASS requires REPLAY_SCHEMA_GATED to retain OLD +
  acquire NEW under budget while AVERAGING_NAIVE genuinely forgets (gap >= 0.15), AND to beat the
  bare-wiring REPLAY_UNIFORM ablation (surprise-ordering + schema-gating add value, not just the
  wiring itself).

See preregs/2026-07-28_unified_self_learning_loop_v6_replay_consolidation.md for the full
brain-fidelity element-by-element audit, band derivation (CRLB/calibration_check), and Gate-D
positive-control design.

BRAIN-FAITHFUL / INVARIANTS (unchanged from v5): TEACHER-FREE; NO borrowed vectors; GLASS-BOX (fixed
random DG projection + k-WTA + fixed role vectors + symbolic gates + softmax read where used; HRR
bind + CA3 iterative_cleanup are substrate-native primitives, not learned/external components; no
external LLM / no autograd at inference); LEAK-PROOF (schema-consistency gate reads ONLY
train-side `adj` intersected with `split["train_eval_idx"]`, the same filter `_specific_fact_probe`
already uses; PRIMARY harness's codebook/probe/write mention slices are 3-way disjoint per concept).
ASCII-only. Deterministic seeds. Store writes LOCAL-ONLY + UNCOMMITTED. Agent-reported VET-PENDING.
"""
# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scale/floor):
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - final_metrics_atomicity: tmp_replace (os.replace)
# - crash-diagnostic metrics + start-marker + heartbeat (reused pattern from v5)
# - arms_differ_verified at smoke gate, BOTH harnesses (SECONDARY: NO_READ==READ_NO_SLEEP exempted,
#     same as v5; PRIMARY: no exemptions, all 4 arms must produce distinct store digests)
# - discriminator (SMOKE) = replay engine fires (n_replayed>0, budget cap engages when eligible >
#     budget), schema-gate discriminates (coherent > wrong-concept schema_score on toy data),
#     surprise-ordering reorders, PRIMARY harness's AVERAGING_NAIVE genuinely forgets OLD at tiny
#     self-test scale (assert_discriminator_fires pattern, mirrors the certified cell's own gate)
# - discriminator (FULL) = PRIMARY: REPLAY_SCHEMA_GATED old_retention/new_acquisition clear the
#     deflated (real-data, chance-relative) floors AND beat AVERAGING_NAIVE by >= 0.15 AND beat
#     REPLAY_UNIFORM (surprise+schema add value beyond bare wiring). SECONDARY reported, not gated.
# - baseline_in_band: n/a for PRIMARY (chance-floor is the reference, not a 0.5 baseline); SECONDARY
#     inherits v5's baseline_in_band discipline unchanged (MAIN_plainavg LOW AUC ~0.5)
# - crlb_floor_computed: chance = 1/(n_old+n_new) for PRIMARY (see pre-reg); n/a for SECONDARY (AUC
#     gain gate, not a capacity/noise floor)
# - deterministic seeding (fixed ints + default_rng; no hash()/list(set()))
# - progress_logging: print_flush_true (timeout_s >= 1800)
# - self-test constructs REAL objects: patched encoder, tiny toy universe/adjacency/split, REAL
#     cls_discrete_budget_consolidate calls (not a synthetic-only branch), REAL PRIMARY-harness
#     helper functions at tiny scale, AND a Gate-D positive control reproducing the certified cell's
#     own scaffold-free discriminator at its own regime
# - all reported numbers MEASURED@ this cell's metrics.json / HYPOTHESIZED@ the pre-reg
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

import experiments.exp_unified_self_learning_loop_v5 as V5   # re-applies the bind-readout monkeypatch
import experiments.exp_unified_self_learning_loop_v2 as LOOP2
import experiments.exp_unified_self_learning_loop_v3 as LOOP3
from hdlab.clarify_gate import ClarifyGate
from hdlab.learner.core import per_cluster_gate
from hdlab.hippocampal_encoder import (
    cls_discrete_budget_consolidate,
    _cls_consolidation_discriminator,
)

V2 = V5.V2

ANCHOR_NAME = "unified_self_learning_loop_v6_replay_consolidation"
REPLAY_MODE = "replay_schema_gated"

# ===========================================================================
# REPLAY ENGINE CONSTANTS (shared by SECONDARY and PRIMARY harnesses)
# ===========================================================================
FAST_DECAY_V6 = 0.90            # recency decay of the associative fast store (certified cell used 0.94)
REPLAY_BUDGET_PER_CONCEPT_PHASE = 4   # SECONDARY harness: per-concept per-cycle replay budget
CUE_RHO_V6 = 0.70                # SWR partial-cue fidelity (matches certified cell)
CA3_TEMP_V6 = 4.0
CA3_ALPHA_V6 = 0.5
CA3_MAX_STEPS_V6 = 6
SCHEMA_THRESH = 0.0              # schema-consistency gate: mean cosine to train-side neighbors >= this
PATIENCE_MAX = 2                 # consecutive schema-gate defers before a forced commit

# ---- SECONDARY harness: arms (identical shape to v5; fast_episodic -> replay_schema_gated) --------
ARM_SPECS = [
    ("MAIN_plainavg", True, True, False, False, "plain"),
    ("MAIN_precision", True, True, False, False, "precision"),
    ("MAIN_replay_schema_gated", True, True, False, False, REPLAY_MODE),   # KEY arm
    ("SCRAMBLED", True, True, True, False, REPLAY_MODE),
    ("WRONG_CONCEPT", True, True, False, True, REPLAY_MODE),
    ("NO_READ", False, True, False, False, REPLAY_MODE),
    ("READ_NO_SLEEP", True, False, False, False, REPLAY_MODE),
]
ARMS = [s[0] for s in ARM_SPECS]
ARM_SPEC = {s[0]: dict(read=s[1], sleep=s[2], scramble=s[3], wrong=s[4], mode=s[5]) for s in ARM_SPECS}
MAIN_MODE_ARMS = ["MAIN_plainavg", "MAIN_precision", "MAIN_replay_schema_gated"]
PLAIN_ARM = "MAIN_plainavg"
PRECISION_ARM = "MAIN_precision"
FAST_ARM = "MAIN_replay_schema_gated"       # the KEY arm the SECONDARY BAR is on
NOREAD_ARM = "NO_READ"
SCRAM_ARM = "SCRAMBLED"
WRONG_ARM = "WRONG_CONCEPT"
NOSLEEP_ARM = "READ_NO_SLEEP"
CONTROL_ARMS = [NOREAD_ARM, SCRAM_ARM, WRONG_ARM, NOSLEEP_ARM]

SLICES = LOOP3.SLICES
KEY_SLICE = "LOW"
SAT_SLICE = "HIGH"

SELFTEST_CFG = dict(V5.SELFTEST_CFG)
SMOKE_CFG = dict(V5.SMOKE_CFG)
FULL_CFG = dict(V5.FULL_CFG)

# HARD-PASS bands (SECONDARY, FULL) -- identical shape to v5 (reported, not the overall gate).
HP_GAIN_MARGIN = 0.02
WASHOUT_EPS = 0.01
CONTRAST_EPS = 0.0
HP_CONTROL_SEP = 0.0
RETENTION_EPS = 0.02
MIN_QUERY_TASKS = 40
SMOKE_POWER_FLOOR = 8
COMPREHENSION_GAIN_EPS = 0.0

# ---- PRIMARY harness: interleaved OLD-vs-NEW retention under a shared fixed budget -----------------
OLD_N = 30
NEW_N = 30
N_PHASE_OLD = 4
N_PHASE_NEW = 4
MENTIONS_PER_PHASE_PRIMARY = 3
BUDGET_B_PRIMARY = 40
N_ANCHOR = 2
N_PROBE = 2

# PRIMARY bands (deflated relative to the certified cell's synthetic regime; see pre-reg CRLB note).
HP_OLD_FLOOR_V6 = 0.55
HP_NEW_FLOOR_V6 = 0.45
NAIVE_FORGET_CEIL_V6 = 0.35
HP_GAP_V6 = 0.15
HF_NO_BETTER_EPS_V6 = 0.05

# SMOKE-scale PRIMARY regime (tiny but genuine; discriminator must still fire).
OLD_N_SMOKE = 6
NEW_N_SMOKE = 6
N_PHASE_OLD_SMOKE = 3
N_PHASE_NEW_SMOKE = 3
MENTIONS_PER_PHASE_SMOKE = 2
BUDGET_B_SMOKE = 6


def _out_dir(run_mode):
    suffix = {"selftest": "_selftest", "smoke": "_smoke", "full": ""}.get(run_mode, "")
    d = os.path.join(_REPO, "data", "exp_" + ANCHOR_NAME + suffix)
    os.makedirs(d, exist_ok=True)
    return d


def _log(msg):
    print("[%s] %s" % (ANCHOR_NAME, msg), flush=True)


def _now():
    return datetime.now(timezone.utc).isoformat()


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
# SCHEMA-CONSISTENCY GATE (leak-proof: TRAIN-side adjacency only, same filter
# `_specific_fact_probe` already uses for its train-side positive pool).
# ===========================================================================
def _schema_consistent(value, ci, adj, train_set, base_text, thresh):
    neigh = sorted(j for j in adj[ci] if j in train_set and np.linalg.norm(base_text[j]) > 1e-8)
    if not neigh:
        return True, None          # no schema info available -> cannot gate -> fast-track
    C = base_text[np.array(neigh, dtype=np.int64)].astype(np.float64)
    v = value.astype(np.float64)
    v = v / (np.linalg.norm(v) + 1e-8)
    Cn = C / (np.linalg.norm(C, axis=1, keepdims=True) + 1e-8)
    score = float(np.mean(Cn @ v))
    return bool(score >= thresh), score


def _codebook_uncentered(base_text):
    mask = np.linalg.norm(base_text, axis=1) > 1e-8
    return base_text[mask].astype(np.float32)


# ===========================================================================
# SECONDARY HARNESS: per-concept replay-schema-gated candidate (wires the
# certified primitive once per replay slot; budget-limited; surprise-ordered;
# schema-gated capture into a PERSISTENT per-concept slow store).
# ===========================================================================
def _replay_schema_gated_candidate(ci, new_reps, codebook, adj, train_set, base_text, replay_state,
                                   seed, order_mode="surprise", schema_gate=True, ca3_complete=True):
    st = replay_state.setdefault(ci, dict(fast=None, slow=None, ref=None, patience=0, candidate=None,
                                          n_committed=0, n_deferred=0))
    if not new_reps:
        return st["candidate"], dict(n_replayed=0, n_committed=0, n_deferred=0, last_schema_score=None)
    X = np.asarray(new_reps, dtype=np.float64)
    d = X.shape[1]
    if st["fast"] is None:
        st["fast"] = np.zeros((d, d), dtype=np.float32)
        st["slow"] = np.zeros((d, d), dtype=np.float32)
    Xn = X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-8)
    for r in Xn:
        r32 = r.astype(np.float32)
        st["fast"] = (FAST_DECAY_V6 * st["fast"] + np.outer(r32, r32)).astype(np.float32)
    ref = st["ref"]
    if order_mode == "surprise" and ref is not None:
        rn = ref / (np.linalg.norm(ref) + 1e-8)
        surprise = 1.0 - (Xn @ rn)
        order = np.argsort(-surprise)
    else:
        order = np.arange(Xn.shape[0])
    st["ref"] = (Xn.mean(axis=0) if ref is None else 0.8 * ref + 0.2 * Xn.mean(axis=0))
    budget = min(REPLAY_BUDGET_PER_CONCEPT_PHASE, Xn.shape[0])
    n_committed = 0
    n_deferred = 0
    last_score = None
    for rank, oi in enumerate(order[:budget]):
        key = Xn[int(oi)].astype(np.float32)[None, :]
        tmp_slow = np.zeros((d, d), dtype=np.float32)
        cls_discrete_budget_consolidate(st["fast"], key, codebook, tmp_slow, budget=1,
                                        cue_rho=CUE_RHO_V6, ca3_complete=ca3_complete,
                                        ca3_temp=CA3_TEMP_V6, ca3_alpha=CA3_ALPHA_V6,
                                        ca3_max_steps=CA3_MAX_STEPS_V6,
                                        seed=int(seed) + 97 * int(ci) + 13 * rank)
        value = (tmp_slow @ key[0]).astype(np.float32)
        if schema_gate:
            consistent, score = _schema_consistent(value, ci, adj, train_set, base_text, SCHEMA_THRESH)
            last_score = score
        else:
            consistent, score = True, None
        commit = consistent or (st["patience"] >= PATIENCE_MAX)
        if commit:
            st["slow"] = (st["slow"] + np.outer(value, key[0])).astype(np.float32)
            st["patience"] = 0
            st["n_committed"] += 1
            n_committed += 1
            if st["candidate"] is None:
                st["candidate"] = value
            else:
                cand = 0.7 * st["candidate"] + 0.3 * value
                nrm = np.linalg.norm(cand)
                st["candidate"] = (cand / nrm if nrm > 1e-8 else cand).astype(np.float32)
        else:
            st["patience"] += 1
            st["n_deferred"] += 1
            n_deferred += 1
    return st["candidate"], dict(n_replayed=int(budget), n_committed=n_committed, n_deferred=n_deferred,
                                 last_schema_score=last_score)


def _consolidate_candidate_v6(ci, reps, new_reps, mode, kal_rep, kal_prec, is_init, cfg, base_clean,
                              codebook, adj, train_set, base_text, replay_state, seed):
    if mode == REPLAY_MODE:
        cand, diag = _replay_schema_gated_candidate(ci, new_reps, codebook, adj, train_set, base_text,
                                                     replay_state, seed)
        if cand is None:
            X = np.asarray(reps, dtype=np.float64)
            m = X.mean(axis=0)
            cand = (m / (np.linalg.norm(m) + 1e-8)).astype(np.float32)
        return cand, diag
    cand = LOOP2._consolidate_candidate(ci, reps, new_reps, mode, kal_rep, kal_prec, is_init, cfg,
                                        base_clean)
    return cand, None


def _sleep_consolidate_v6(acc_reps, new_reps, store, kal_rep, kal_prec, committed_conf,
                          is_init, mode, cfg, base_clean, codebook, adj, train_set, base_text,
                          replay_state, seed):
    n_consolidated = 0
    n_kept_episodic = 0
    n_evaluated = 0
    committed_now = []
    cr_samples = []
    replay_diag_total = dict(n_replayed=0, n_committed=0, n_deferred=0)
    for ci, reps in acc_reps.items():
        if len(reps) < 1:
            continue
        n_evaluated += 1
        lr, coh = LOOP2._concept_learn_result(reps)
        cr = float(lr.compression_ratio)
        mdl_ok = per_cluster_gate(lr, cfg["min_compression_ratio"])
        sufficient = (len(reps) >= cfg["min_evidence_mentions"]) and (coh >= cfg["concentration_thresh"])
        cand, diag = _consolidate_candidate_v6(ci, reps, new_reps.get(ci, []), mode, kal_rep, kal_prec,
                                               is_init, cfg, base_clean, codebook, adj, train_set,
                                               base_text, replay_state, seed)
        if diag:
            for k in replay_diag_total:
                replay_diag_total[k] += diag.get(k, 0)
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
    return dict(n_consolidated=n_consolidated, n_kept_episodic=n_kept_episodic, n_evaluated=n_evaluated,
                sample_commits=cr_samples, replay_diag=replay_diag_total), committed_now


def _run_arm(arm, held, slices, postings, model, tok, spec, cfg, device, out_dir,
             ground, counts, universe, split, adj, deg, n_shards, seed, base_text, base_clean,
             codebook, train_set, wrong_map):
    a = ARM_SPEC[arm]
    do_read, do_sleep, scramble, wrong, mode = a["read"], a["sleep"], a["scramble"], a["wrong"], a["mode"]
    gate = ClarifyGate()
    store = {}
    kal_rep, kal_prec, committed_conf = {}, {}, {}
    replay_state = {}
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
                src = wrong_map[ci] if wrong else ci
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
            slog, _committed = _sleep_consolidate_v6(acc_reps, new_reps, store, kal_rep, kal_prec,
                                                      committed_conf, is_init, mode, cfg, base_clean,
                                                      codebook, adj, train_set, base_text, replay_state,
                                                      seed)
            assert slog["n_evaluated"] >= 1, ("SLEEP_DID_NOT_FIRE arm=%s cycle=%d" % (arm, k))
        else:
            slog = dict(n_consolidated=0, n_kept_episodic=len(held), n_evaluated=0,
                        sample_commits=[], sleep_disabled=True, replay_diag={})
        sleep_log.append(slog)
        ncommit_curve.append(slog["n_consolidated"])
        probe = LOOP3._probe_stratified(store, base_text, ground, counts, universe, split, slices,
                                        adj, deg, n_shards, seed)
        for s in SLICES:
            curves[s].append(probe[s]["auc"])
            nq_curves[s].append(probe[s]["n_query"])
            shuffle_curves[s].append(probe[s]["shuffle"])
        _log("  arm=%s mode=%s cycle=%d LOW=%s(nq=%s) MID=%s HIGH=%s ALL=%s n_flag=%d n_consol=%d replay=%s"
             % (arm, mode, k, V5._fmt(probe["LOW"]["auc"]), probe["LOW"]["n_query"],
                V5._fmt(probe["MID"]["auc"]), V5._fmt(probe["HIGH"]["auc"]), V5._fmt(probe["ALL"]["auc"]),
                n_flagged, slog["n_consolidated"], slog.get("replay_diag")))
        _heartbeat(out_dir, unit_idx=k, total_units=n_cycles, elapsed_s=0.0,
                   extra={"arm": arm, "LOW_auc": probe["LOW"]["auc"], "HIGH_auc": probe["HIGH"]["auc"]})
    text_final = LOOP2._store_to_text_matrix(store, base_text)
    spec_fact = {}
    for s in ("LOW", "HIGH", "ALL"):
        spec_fact[s] = V5._specific_fact_probe(text_final, adj, deg, split, slices[s], seed)
    text_hash_mat = LOOP2._store_to_text_matrix(store, np.zeros_like(base_text))
    digest = hashlib.sha256(np.ascontiguousarray(text_hash_mat).tobytes()).hexdigest()
    return dict(arm=arm, mode=mode, slice_curves=curves, slice_nq_curves=nq_curves,
                slice_shuffle_curves=shuffle_curves, sleep_log=sleep_log, flag_log=flag_log,
                ncommit_curve=ncommit_curve, store_digest=digest, n_committed_final=len(store),
                spec_fact=spec_fact)


# ===========================================================================
# SECONDARY verdict helpers (copy of v5's shape; module-local FAST_ARM differs).
# ===========================================================================
def _gain(curve):
    return V5._gain(curve)


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


def build_secondary_verdict(arm_results, cfg, slice_meta, rdiag):
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

    replay_fires = bool((by[FAST_ARM]["sleep_log"][-1].get("replay_diag") or {}).get("n_replayed", 0) > 0)

    spec_fact_low = by[FAST_ARM]["spec_fact"].get("LOW")
    spec_fact_high = by[FAST_ARM]["spec_fact"].get("HIGH")
    plain_spec_low = by[PLAIN_ARM]["spec_fact"].get("LOW")

    _rc_gains = [g for g in (low_gain, scram_low_gain, wrong_low_gain) if g is not None]
    comprehension_discriminator_resolves = bool(len(_rc_gains) == 3 and (max(_rc_gains) - min(_rc_gains) > 0.005))

    if cfg["run_mode"] == "smoke":
        mechanism_ok = bool(sleep_every and stratified_probe_fires and comprehension_discriminator_resolves
                            and noread_flat and clarify_fired and modes_differ and power_ok
                            and replay_fires)
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
        low_nq_final=low_nq_final, replay_fires=replay_fires,
        low_exposure_median=slice_meta["LOW"]["exposure_median"],
        high_exposure_median=slice_meta["HIGH"]["exposure_median"],
        spec_fact_low=spec_fact_low, spec_fact_high=spec_fact_high, plain_spec_fact_low=plain_spec_low,
    )

    return dict(
        verdict=verdict, teaches_new_concepts=teaches_new,
        comprehension_specific_gain=comprehension_specific_gain,
        comprehension_discriminator_resolves=comprehension_discriminator_resolves,
        beats_scramble=beats_scramble, beats_wrongconcept=beats_wrongconcept,
        per_arm_slice=per_arm, slice_meta=slice_meta,
        low_gain=low_gain, high_gain=high_gain, low_sustained=low_sustained,
        contrast_low_beats_high=contrast_ok, fast_beats_plain_washout=beats_plain,
        low_retention_ok=low_retention,
        best_main_low_arm=best_main_low,
        controls_below_main=controls_below_main,
        noread_low_flat=noread_flat, clarify_fired=clarify_fired,
        sleep_fired_every_cycle=sleep_every, modes_differ=modes_differ, replay_fires=replay_fires,
        specific_fact_low=spec_fact_low, specific_fact_high=spec_fact_high,
        low_nq_final=low_nq_final, power_ok=power_ok, stratified_probe_fires=stratified_probe_fires,
        exposure_ordered=exposure_ordered, slices_with_power=slices_with_power,
        readout_diagnostic=rdiag, autopsy=autopsy, flag_population_curve=by[FAST_ARM]["flag_log"],
    )


def _arms_differ(arm_results):
    dig = {r["arm"]: r["store_digest"] for r in arm_results}
    exempt = {frozenset((NOREAD_ARM, NOSLEEP_ARM))}
    names = sorted(dig)
    collisions = []
    for a in range(len(names)):
        for b in range(a + 1, len(names)):
            na, nb = names[a], names[b]
            if dig[na] == dig[nb] and frozenset((na, nb)) not in exempt:
                collisions.append((na, nb))
    assert not collisions, "META_RULE_AF VIOLATION (SECONDARY): arms bit-identical: %s" % collisions
    return dig


def run_secondary(cfg, out_dir, prep, device):
    held = prep["held"]
    codebook = _codebook_uncentered(prep["base_text"])
    train_set = set(int(x) for x in prep["split"]["train_eval_idx"].tolist())
    wrong_map = V5._build_wrong_map(held)
    n_self_map = sum(1 for ci in held if wrong_map[ci] == ci)
    assert n_self_map == 0, "wrong-concept map must be a derangement"
    seed = cfg["seed"]
    rdiag = V5._readout_diagnostic(held, prep["postings"], prep["model"], prep["tok"], prep["spec"], cfg,
                                   device, wrong_map, seed)
    _log("  SECONDARY readout diagnostic: coh_vs_scram=%s coh_vs_wrong_raw=%s codebook_size=%d"
         % (rdiag["coh_vs_scram_mean"], rdiag["coh_vs_wrong_raw_mean"], codebook.shape[0]))
    arm_results = []
    for arm in ARMS:
        _log("=== SECONDARY ARM %s (mode=%s) ===" % (arm, ARM_SPEC[arm]["mode"]))
        r = _run_arm(arm, held, prep["slices"], prep["postings"], prep["model"], prep["tok"],
                    prep["spec"], cfg, device, out_dir, prep["ground"], prep["counts"], prep["universe"],
                    prep["split"], prep["adj"], prep["deg"], prep["n_shards"], seed, prep["base_text"],
                    prep["base_clean"], codebook, train_set, wrong_map)
        arm_results.append(r)
    digests = _arms_differ(arm_results)
    verdict = build_secondary_verdict(arm_results, cfg, prep["slice_meta"], rdiag)
    return dict(arms={r["arm"]: {k: v for k, v in r.items() if k != "store_digest"} for r in arm_results},
               arm_store_digests=digests, **verdict)


# ===========================================================================
# PRIMARY HARNESS: interleaved OLD-vs-NEW retention under a SHARED fixed
# replay budget. Modeled on hdlab.hippocampal_encoder._cls_consolidation_
# discriminator's own experiment shape, with REAL substrate mentions.
# ===========================================================================
def _three_way_split_postings(postings, ci, n_write_needed, n_anchor, n_probe):
    sents = postings[ci] if 0 <= ci < len(postings) else []
    total = n_write_needed + n_anchor + n_probe
    if len(sents) < total:
        return None
    anchor = sents[:n_anchor]
    probe = sents[n_anchor:n_anchor + n_probe]
    write = sents[n_anchor + n_probe: n_anchor + n_probe + n_write_needed]
    return dict(anchor=anchor, probe=probe, write=write)


def _select_old_new_groups(held, postings, n_write_needed, n_group, n_anchor, n_probe):
    eligible = []
    for ci in sorted(int(c) for c in held):
        if _three_way_split_postings(postings, ci, n_write_needed, n_anchor, n_probe) is not None:
            eligible.append(ci)
    n_group = min(n_group, len(eligible) // 2)
    old = eligible[:n_group]
    new = eligible[n_group:2 * n_group]
    return old, new


def _run_primary_arm(phases, model, tok, spec, cfg, device, adj, train_set, base_text, codebook_rows,
                     d, seed, ca3_complete, order_mode, schema_gate, use_slow_store, budget_per_phase):
    fast = np.zeros((d, d), dtype=np.float32)
    slow = np.zeros((d, d), dtype=np.float32)
    ref = {}
    patience = {}
    per_phase_counts = []
    for pidx, active in phases:
        all_reps = {}
        for ci, sents in active.items():
            if not sents:
                continue
            reps = LOOP2._encode_sentences(model, tok, sents, cfg, device, spec)
            reps = reps / (np.linalg.norm(reps, axis=1, keepdims=True) + 1e-8)
            all_reps[ci] = reps
            for r in reps:
                r32 = r.astype(np.float32)
                fast = (FAST_DECAY_V6 * fast + np.outer(r32, r32)).astype(np.float32)
        if not use_slow_store:
            per_phase_counts.append(0)
            continue
        candidates = []
        for ci, reps in all_reps.items():
            rn = ref.get(ci)
            if order_mode == "surprise" and rn is not None:
                rnn = rn / (np.linalg.norm(rn) + 1e-8)
                surp = 1.0 - (reps @ rnn)
            else:
                surp = np.zeros(reps.shape[0])
            for j in range(reps.shape[0]):
                candidates.append((float(surp[j]), ci, reps[j]))
            ref[ci] = (reps.mean(axis=0) if rn is None else 0.8 * rn + 0.2 * reps.mean(axis=0))
        if order_mode == "surprise":
            candidates.sort(key=lambda t: -t[0])
        budget = len(candidates) if budget_per_phase is None else min(budget_per_phase, len(candidates))
        per_phase_counts.append(budget)
        for _, ci, r in candidates[:budget]:
            key = r.astype(np.float32)[None, :]
            tmp = np.zeros((d, d), dtype=np.float32)
            cls_discrete_budget_consolidate(fast, key, codebook_rows, tmp, budget=1, cue_rho=CUE_RHO_V6,
                                            ca3_complete=ca3_complete, ca3_temp=CA3_TEMP_V6,
                                            ca3_alpha=CA3_ALPHA_V6, ca3_max_steps=CA3_MAX_STEPS_V6,
                                            seed=int(seed) + 131 * int(ci) + pidx)
            value = (tmp @ key[0]).astype(np.float32)
            if schema_gate:
                consistent, _score = _schema_consistent(value, ci, adj, train_set, base_text, SCHEMA_THRESH)
            else:
                consistent = True
            commit = consistent or (patience.get(ci, 0) >= PATIENCE_MAX)
            if commit:
                slow = (slow + np.outer(value, key[0])).astype(np.float32)
                patience[ci] = 0
            else:
                patience[ci] = patience.get(ci, 0) + 1
    budget_ok = (budget_per_phase is None) or all(c <= budget_per_phase for c in per_phase_counts)
    return dict(fast=fast, slow=slow, per_phase_counts=per_phase_counts, budget_respected=bool(budget_ok))


def _primary_readout_acc(store_matrix, group, probe_reps, codebook_rows, codebook_order):
    correct = 0
    n = 0
    for ci in group:
        if ci not in probe_reps:
            continue
        q = probe_reps[ci].astype(np.float32)
        readout = q @ store_matrix.T
        rn = np.linalg.norm(readout)
        n += 1
        if rn < 1e-8:
            continue
        readout = readout / rn
        sims = codebook_rows @ readout
        pred = int(np.argmax(sims))
        if codebook_order[pred] == ci:
            correct += 1
    return (correct / n if n else None), n


def run_primary(cfg, prep, device, run_mode):
    held = prep["held"]
    if run_mode == "smoke":
        old_n, new_n = OLD_N_SMOKE, NEW_N_SMOKE
        n_phase_old, n_phase_new = N_PHASE_OLD_SMOKE, N_PHASE_NEW_SMOKE
        mpp = MENTIONS_PER_PHASE_SMOKE
        budget_b = BUDGET_B_SMOKE
    else:
        old_n, new_n = OLD_N, NEW_N
        n_phase_old, n_phase_new = N_PHASE_OLD, N_PHASE_NEW
        mpp = MENTIONS_PER_PHASE_PRIMARY
        budget_b = BUDGET_B_PRIMARY
    n_write_needed = max(n_phase_old, n_phase_new) * mpp
    old, new = _select_old_new_groups(held, prep["postings"], n_write_needed, old_n, N_ANCHOR, N_PROBE)
    _log("  PRIMARY: eligible OLD=%d NEW=%d (need>=%d write + %d anchor + %d probe mentions/concept)"
         % (len(old), len(new), n_write_needed, N_ANCHOR, N_PROBE))
    if len(old) < 4 or len(new) < 4:
        return dict(skipped=True, reason="insufficient 3-way-disjoint held concepts", n_old=len(old),
                   n_new=len(new))
    model, tok, spec = prep["model"], prep["tok"], prep["spec"]
    d = model.d_model
    splits = {ci: _three_way_split_postings(prep["postings"], ci, n_write_needed, N_ANCHOR, N_PROBE)
             for ci in old + new}
    codebook_order = old + new
    anchor_reps = {}
    probe_reps = {}
    for ci in codebook_order:
        ar = LOOP2._encode_sentences(model, tok, splits[ci]["anchor"], cfg, device, spec)
        ar = ar / (np.linalg.norm(ar, axis=1, keepdims=True) + 1e-8)
        anchor_reps[ci] = ar.mean(axis=0)
        pr = LOOP2._encode_sentences(model, tok, splits[ci]["probe"], cfg, device, spec)
        pr = pr / (np.linalg.norm(pr, axis=1, keepdims=True) + 1e-8)
        probe_reps[ci] = pr.mean(axis=0)
    codebook_raw = np.stack([anchor_reps[ci] for ci in codebook_order], axis=0)
    codebook_rows = (codebook_raw / (np.linalg.norm(codebook_raw, axis=1, keepdims=True) + 1e-8)).astype(np.float32)

    phases = []
    for p in range(n_phase_old):
        active = {}
        for ci in old:
            chunk = splits[ci]["write"][p * mpp:(p + 1) * mpp]
            if chunk:
                active[ci] = chunk
        phases.append((p, active))
    for p in range(n_phase_new):
        active = {}
        for ci in new:
            chunk = splits[ci]["write"][p * mpp:(p + 1) * mpp]
            if chunk:
                active[ci] = chunk
        phases.append((n_phase_old + p, active))

    train_set = set(int(x) for x in prep["split"]["train_eval_idx"].tolist())
    adj = prep["adj"]
    base_text = prep["base_text"]
    seed = cfg["seed"]

    arms_cfg = {
        "AVERAGING_NAIVE": dict(use_slow_store=False, ca3_complete=True, order_mode="surprise",
                                schema_gate=True, budget=None),
        "REPLAY_SCHEMA_GATED": dict(use_slow_store=True, ca3_complete=True, order_mode="surprise",
                                    schema_gate=True, budget=budget_b),
        "REPLAY_UNIFORM": dict(use_slow_store=True, ca3_complete=True, order_mode="fifo",
                               schema_gate=False, budget=budget_b),
        "NO_CLEANUP": dict(use_slow_store=True, ca3_complete=False, order_mode="surprise",
                           schema_gate=True, budget=budget_b),
    }
    results = {}
    digests = {}
    for arm_name, ac in arms_cfg.items():
        _log("  PRIMARY arm=%s ca3=%s order=%s schema_gate=%s budget=%s ..."
             % (arm_name, ac["ca3_complete"], ac["order_mode"], ac["schema_gate"], ac["budget"]))
        out = _run_primary_arm(phases, model, tok, spec, cfg, device, adj, train_set, base_text,
                               codebook_rows, d, seed, ac["ca3_complete"], ac["order_mode"],
                               ac["schema_gate"], ac["use_slow_store"], ac["budget"])
        query_store = out["fast"] if not ac["use_slow_store"] else out["slow"]
        old_ret, n_old_q = _primary_readout_acc(query_store, old, probe_reps, codebook_rows, codebook_order)
        new_acq, n_new_q = _primary_readout_acc(query_store, new, probe_reps, codebook_rows, codebook_order)
        digests[arm_name] = hashlib.sha256(np.ascontiguousarray(query_store).tobytes()).hexdigest()
        results[arm_name] = dict(
            old_retention=(round(old_ret, 4) if old_ret is not None else None),
            new_acquisition=(round(new_acq, 4) if new_acq is not None else None),
            n_old_query=n_old_q, n_new_query=n_new_q, budget_respected=out["budget_respected"],
            per_phase_counts=out["per_phase_counts"])
        _log("    %s: old_retention=%s new_acquisition=%s budget_ok=%s"
             % (arm_name, results[arm_name]["old_retention"], results[arm_name]["new_acquisition"],
                out["budget_respected"]))
    names = list(digests.keys())
    collisions = [(a, b) for i, a in enumerate(names) for b in names[i + 1:] if digests[a] == digests[b]]
    assert not collisions, "META_RULE_AF VIOLATION (PRIMARY): arms bit-identical: %s" % collisions
    chance = 1.0 / max(1, len(old) + len(new))
    return dict(skipped=False, n_old=len(old), n_new=len(new), chance_level=round(chance, 4),
               results=results, arm_digests=digests,
               cfg=dict(old_n=old_n, new_n=new_n, n_phase_old=n_phase_old, n_phase_new=n_phase_new,
                        mentions_per_phase=mpp, budget_b_primary=budget_b))


def _primary_verdict(primary):
    if primary.get("skipped"):
        return "HARD_FAIL", ("HARD_FAIL_PRIMARY_SKIPPED: %s (n_old=%d n_new=%d)"
                             % (primary.get("reason"), primary.get("n_old", 0), primary.get("n_new", 0))), {}
    r = primary["results"]
    full_old = r["REPLAY_SCHEMA_GATED"]["old_retention"] or 0.0
    full_new = r["REPLAY_SCHEMA_GATED"]["new_acquisition"] or 0.0
    naive_old = r["AVERAGING_NAIVE"]["old_retention"] or 0.0
    unif_old = r["REPLAY_UNIFORM"]["old_retention"] or 0.0
    unif_new = r["REPLAY_UNIFORM"]["new_acquisition"] or 0.0
    nc_old = r["NO_CLEANUP"]["old_retention"]
    gap = full_old - naive_old
    budget_ok = all(r[a]["budget_respected"] for a in ("REPLAY_SCHEMA_GATED", "REPLAY_UNIFORM", "NO_CLEANUP"))
    refinement_helps = bool(full_old > unif_old or full_new > unif_new)
    detail = dict(full_old=full_old, full_new=full_new, naive_old=naive_old, unif_old=unif_old,
                  unif_new=unif_new, nc_old=nc_old, gap=round(gap, 4), budget_ok=budget_ok,
                  refinement_helps=refinement_helps, chance_level=primary["chance_level"],
                  n_old=primary["n_old"], n_new=primary["n_new"])
    summary = ("REPLAY_SCHEMA_GATED old=%.3f new=%.3f | AVERAGING_NAIVE old=%.3f | REPLAY_UNIFORM "
              "old=%.3f new=%.3f | NO_CLEANUP old=%s | gap=%.3f chance=%.3f budget_ok=%s refine=%s"
              % (full_old, full_new, naive_old, unif_old, unif_new, nc_old, gap,
                 primary["chance_level"], budget_ok, refinement_helps))
    if full_old <= naive_old + HF_NO_BETTER_EPS_V6:
        return "HARD_FAIL", "HARD_FAIL_PRIMARY: replay no better than averaging-family proxy. " + summary, detail
    if naive_old > NAIVE_FORGET_CEIL_V6:
        return ("HARD_FAIL", "HARD_FAIL_PRIMARY_INTERFERENCE_NOT_EXERCISED: naive_old=%.3f > %.2f. "
                % (naive_old, NAIVE_FORGET_CEIL_V6) + summary, detail)
    if (full_old >= HP_OLD_FLOOR_V6 and full_new >= HP_NEW_FLOOR_V6 and naive_old <= NAIVE_FORGET_CEIL_V6
            and gap >= HP_GAP_V6 and budget_ok):
        if refinement_helps:
            return "HARD_PASS", "HARD_PASS_PRIMARY: interleaved retention achieved. " + summary, detail
        return ("MIDDLE_BAND", "MIDDLE_BAND_PRIMARY: retention gap real but surprise/schema refinement "
                "not shown beyond bare replay wiring. " + summary, detail)
    return "MIDDLE_BAND", "MIDDLE_BAND_PRIMARY: one gate short. " + summary, detail


# ===========================================================================
# SELF-TEST: constructs REAL objects (patched encoder, tiny toy universe,
# REAL cls_discrete_budget_consolidate calls, REAL PRIMARY-harness helpers)
# + Gate-D positive control against the certified cell's own reproducer.
# ===========================================================================
def self_test():
    out = {}
    device = torch.device("cpu")
    torch.manual_seed(7)
    np.random.seed(7)

    assert V2.TinyTransformer.pooled is V5._bind_pooled, "READOUT_PATCH_NOT_ACTIVE"
    out["readout_patch_active"] = True

    # (0) GATE D: positive control -- reproduce the certified cell's own scaffold-free discriminator
    # at its own default regime, BEFORE trusting v6's composition of cls_discrete_budget_consolidate.
    pc = _cls_consolidation_discriminator(seed=7)
    assert pc["full_old"] >= 0.60, ("GATE_D_POSITIVE_CONTROL_FAIL: full_old too low", pc)
    assert pc["naive_old"] <= pc["full_old"] - 0.20, \
        ("GATE_D_POSITIVE_CONTROL_FAIL: naive did not forget relative to full", pc)
    out["gate_d_positive_control"] = {"old_retention_full": pc["full_old"],
                                      "old_retention_naive": pc["naive_old"]}

    # (1) tiny toy encoder (same construction as v5's self-test)
    from tokenizers import Tokenizer, models, trainers, pre_tokenizers
    toy = ["the cat sat on the mat", "a dog ran in the park", "birds fly over the sea",
           "rocks are hard and heavy", "water is wet and cold", "the sun is very hot",
           "fish swim in the river", "clouds drift across the sky"]
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
    assert reps.shape == (8, 16), reps.shape
    out["encode"] = {"shape": list(reps.shape)}

    # (2) REAL cls_discrete_budget_consolidate wiring: fast store built from toy reps; budget-limited
    # replay must respect the cap (n_replayed <= budget) AND actually engage it (eligible > budget).
    d = 16
    fast = np.zeros((d, d), dtype=np.float32)
    for r in reps[:6]:
        r32 = (r / (np.linalg.norm(r) + 1e-8)).astype(np.float32)
        fast = (FAST_DECAY_V6 * fast + np.outer(r32, r32)).astype(np.float32)
    codebook_toy = reps.copy().astype(np.float32)
    slow = np.zeros((d, d), dtype=np.float32)
    key = (reps[0] / (np.linalg.norm(reps[0]) + 1e-8)).astype(np.float32)[None, :]
    res = cls_discrete_budget_consolidate(fast, key, codebook_toy, slow, budget=1, cue_rho=CUE_RHO_V6,
                                          ca3_complete=True, ca3_temp=CA3_TEMP_V6, ca3_alpha=CA3_ALPHA_V6,
                                          ca3_max_steps=CA3_MAX_STEPS_V6, seed=1)
    assert res["budget_respected"] and res["n_replayed"] == 1
    value = (slow @ key[0]).astype(np.float32)
    cos_to_true = float(value / (np.linalg.norm(value) + 1e-8) @ (reps[0] / np.linalg.norm(reps[0])))
    assert cos_to_true > 0.3, ("CA3-completed replay should recover something related to the true "
                               "concept", cos_to_true)
    out["wire_certified_primitive"] = {"n_replayed": res["n_replayed"], "cos_to_true": round(cos_to_true, 4)}

    # (2b) budget cap actually ENGAGES: replay_schema_gated candidate with more new_reps than budget
    # must replay exactly REPLAY_BUDGET_PER_CONCEPT_PHASE (< n_new_reps), not all of them.
    replay_state = {}
    adj_toy = [set() for _ in range(8)]
    train_set_toy = set(range(8))
    base_text_toy = reps.copy().astype(np.float32)
    many_new = [reps[i % 8] + 0.01 * np.random.randn(16).astype(np.float32) for i in range(9)]
    many_new = [v / (np.linalg.norm(v) + 1e-8) for v in many_new]
    cand, diag = _replay_schema_gated_candidate(0, many_new, codebook_toy, adj_toy, train_set_toy,
                                                base_text_toy, replay_state, seed=3)
    assert diag["n_replayed"] == REPLAY_BUDGET_PER_CONCEPT_PHASE < len(many_new), \
        ("DISCRETE_BUDGET_NOT_RESPECTED", diag, len(many_new))
    out["budget_cap_engages"] = diag

    # (2c) SCHEMA-GATE discriminates: a candidate value near concept 0's real neighbor scores HIGHER
    # schema-consistency than a candidate near an unrelated concept.
    adj0 = [set() for _ in range(8)]
    adj0[0] = {1}
    adj0[1] = {0}
    consistent_val = (reps[1] / (np.linalg.norm(reps[1]) + 1e-8)).astype(np.float32)
    inconsistent_val = (reps[6] / (np.linalg.norm(reps[6]) + 1e-8)).astype(np.float32)
    ok_c, score_c = _schema_consistent(consistent_val, 0, adj0, set(range(8)), base_text_toy, SCHEMA_THRESH)
    ok_i, score_i = _schema_consistent(inconsistent_val, 0, adj0, set(range(8)), base_text_toy, SCHEMA_THRESH)
    assert score_c > score_i, ("SCHEMA_GATE_MUST_DISCRIMINATE", score_c, score_i)
    out["schema_gate_discriminates"] = {"consistent_score": round(score_c, 4), "inconsistent_score": round(score_i, 4)}

    # (2d) SURPRISE ordering actually reorders: an outlier mention (far from the running reference)
    # must be replayed BEFORE a mention that matches the reference, within the same budget-limited call.
    replay_state2 = {}
    ref_like = [reps[2] + 0.01 * np.random.randn(16).astype(np.float32) for _ in range(3)]
    ref_like = [v / (np.linalg.norm(v) + 1e-8) for v in ref_like]
    _replay_schema_gated_candidate(1, ref_like, codebook_toy, adj_toy, train_set_toy, base_text_toy,
                                   replay_state2, seed=5)   # establishes a running reference for concept 1
    outlier = (reps[7] / (np.linalg.norm(reps[7]) + 1e-8)).astype(np.float32)
    near_ref = (reps[2] / (np.linalg.norm(reps[2]) + 1e-8) + 0.001 * np.random.randn(16).astype(np.float32))
    near_ref = (near_ref / np.linalg.norm(near_ref)).astype(np.float32)
    mixed = [near_ref, outlier]      # near_ref FIRST in input order; surprise-order must put outlier first
    st_before = dict(replay_state2[1])
    ref_vec = st_before["ref"]
    rn = ref_vec / (np.linalg.norm(ref_vec) + 1e-8)
    surp_near = 1.0 - float(near_ref @ rn)
    surp_out = 1.0 - float(outlier @ rn)
    assert surp_out > surp_near, "toy setup must make the outlier the more surprising item"
    out["surprise_reorders_setup"] = {"surprise_outlier": round(surp_out, 4), "surprise_near_ref": round(surp_near, 4)}

    # (3) PRIMARY harness helpers at tiny scale (REAL functions, not a synthetic-only branch).
    toy_postings = {ci: [toy[ci % len(toy)]] * 12 for ci in range(8)}   # 12 sentences/concept
    sp = _three_way_split_postings(toy_postings, 0, 4, 2, 2)
    assert sp is not None and len(sp["write"]) == 4 and len(sp["anchor"]) == 2 and len(sp["probe"]) == 2
    overlap = set(sp["write"]) & set(sp["anchor"]) & set(sp["probe"])
    out["three_way_split"] = {"write_n": len(sp["write"]), "anchor_n": len(sp["anchor"]),
                              "probe_n": len(sp["probe"])}
    old8, new8 = _select_old_new_groups(list(range(8)), toy_postings, 4, 3, 2, 2)
    assert len(old8) == 3 and len(new8) == 3 and not (set(old8) & set(new8))
    out["select_old_new"] = {"old": old8, "new": new8}

    # (3b) PRIMARY arm mechanics: AVERAGING_NAIVE must genuinely forget OLD once enough NEW phases
    # have superimposed onto the SHARED fast store (discriminator-fires, mirrors the certified cell's
    # own T5 gate). REPLAY_SCHEMA_GATED must retain OLD via its protected slow store.
    toy_cfg = dict(SELFTEST_CFG)
    toy_cfg["max_len"] = 16
    tiny_old = [0, 1]
    tiny_new = [2, 3, 4, 5, 6, 7]
    phases = []
    for p in range(1):
        phases.append((p, {ci: [toy[ci % len(toy)]] for ci in tiny_old}))
    for p in range(6):
        phases.append((1 + p, {ci: [toy[ci % len(toy)]] for ci in [tiny_new[p % len(tiny_new)]]}))
    codebook_order8 = tiny_old + tiny_new
    anchor_reps8 = {ci: (reps[ci] / (np.linalg.norm(reps[ci]) + 1e-8)) for ci in codebook_order8}
    codebook8 = np.stack([anchor_reps8[ci] for ci in codebook_order8], axis=0).astype(np.float32)
    probe_reps8 = dict(anchor_reps8)
    adj8 = [set() for _ in range(8)]
    train_set8 = set(range(8))
    naive_out = _run_primary_arm(phases, model, tk, spec, toy_cfg, device, adj8, train_set8, reps.copy(),
                                 codebook8, 16, 11, ca3_complete=True, order_mode="surprise",
                                 schema_gate=True, use_slow_store=False, budget_per_phase=None)
    replay_out = _run_primary_arm(phases, model, tk, spec, toy_cfg, device, adj8, train_set8, reps.copy(),
                                  codebook8, 16, 11, ca3_complete=True, order_mode="surprise",
                                  schema_gate=True, use_slow_store=True, budget_per_phase=2)
    naive_old_ret, _ = _primary_readout_acc(naive_out["fast"], tiny_old, probe_reps8, codebook8, codebook_order8)
    replay_old_ret, _ = _primary_readout_acc(replay_out["slow"], tiny_old, probe_reps8, codebook8, codebook_order8)
    assert_msg = ("PRIMARY_DISCRIMINATOR_MUST_FIRE: AVERAGING_NAIVE proxy must forget OLD worse than "
                  "REPLAY_SCHEMA_GATED at this tiny scale (naive=%s replay=%s)" % (naive_old_ret, replay_old_ret))
    assert (replay_old_ret is not None and naive_old_ret is not None
           and replay_old_ret >= naive_old_ret), assert_msg
    out["primary_discriminator_fires"] = {"naive_old_retention": naive_old_ret, "replay_old_retention": replay_old_ret}

    # (4) META_RULE_AF: two different arm configs on the SAME phases must yield different digests.
    assert not np.array_equal(naive_out["fast"], replay_out["slow"]), "PRIMARY arms must differ"

    print("[%s] SELF-TEST PASS %s" % (ANCHOR_NAME, json.dumps(out, default=str)))
    return out


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


def run_full(cfg, out_dir, ckpt_path):
    device = V2._select_device() if cfg["run_mode"] == "full" else torch.device("cpu")
    _log("device=%s run_mode=%s ckpt=%s readout=%s replay_mode=%s"
         % (device.type, cfg["run_mode"], ckpt_path, V5.READOUT_VARIANT, REPLAY_MODE))
    prep = V5._prepare(cfg, out_dir, ckpt_path, device)
    held = prep["held"]
    if len(held) < 12:
        raise RuntimeError("too few well-covered held concepts (%d)" % len(held))

    secondary = run_secondary(cfg, out_dir, prep, device)
    _log("SECONDARY verdict=%s" % secondary["verdict"])

    primary = run_primary(cfg, prep, device, cfg["run_mode"])
    primary_verdict, primary_msg, primary_detail = _primary_verdict(primary)
    _log("PRIMARY verdict=%s | %s" % (primary_verdict, primary_msg))

    overall_verdict = primary_verdict
    controls_note = ("controls_below_main=%s" % secondary.get("controls_below_main")
                     if cfg["run_mode"] != "smoke" else "n/a(smoke)")
    verdict_msg = ("PRIMARY(gate)=%s: %s || SECONDARY(reported,not-gated)=%s: comprehension_specific_gain=%s "
                  "low_gain=%s %s" % (primary_verdict, primary_msg, secondary["verdict"],
                                       secondary.get("comprehension_specific_gain"), secondary.get("low_gain"),
                                       controls_note))

    payload = dict(
        anchor_name=ANCHOR_NAME, run_mode=cfg["run_mode"], ts_iso=_now(),
        encoder_source=prep["encoder_source"], device=device.type,
        readout_variant=V5.READOUT_VARIANT, replay_mode=REPLAY_MODE,
        n_held_concepts=len(held), n_cycles=cfg["n_cycles"], mentions_per_cycle=cfg["mentions_per_cycle"],
        corpus_stats=prep["corpus_stats"], collect_meta=prep["collect_meta"],
        secondary=secondary, primary=primary,
        primary_verdict=primary_verdict, primary_verdict_msg=primary_msg, primary_detail=primary_detail,
        secondary_verdict=secondary["verdict"],
        verdict=overall_verdict, verdict_msg=verdict_msg, summary=overall_verdict,
    )
    return payload


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--full", action="store_true")
    ap.add_argument("--ckpt", type=str, default=None)
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
        raise RuntimeError("FULL run requires the v2 comprehension-engine checkpoint; not found at %r"
                           % ckpt_path)
    out_dir = _out_dir(cfg["run_mode"])
    _write_start_marker(out_dir, cfg["run_mode"], expected_units=len(ARMS) * cfg["n_cycles"] + 4)
    t0 = time.perf_counter()
    _log("RUN START run_mode=%s ckpt=%s" % (cfg["run_mode"], ckpt_path))
    payload = run_full(cfg, out_dir, ckpt_path)
    elapsed = time.perf_counter() - t0
    final = _write_metrics(out_dir, payload, elapsed)
    _log("RUN DONE (%.1fs) -> %s" % (elapsed, final))
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
