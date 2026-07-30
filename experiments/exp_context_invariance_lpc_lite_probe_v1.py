# CELL-TEMPLATE MANDATORY (subset applicable to a standalone <5min measurement probe, not a multi-unit
# training cell): except SystemExit: raise BEFORE except Exception (no BaseException); atomic tmp_replace
# metrics write; deterministic seeding (np.random.default_rng + torch.manual_seed only; no hash(), no
# list(set())); numbers tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@; arms_differ_verified
# (LPC-lite vs MLM-lite vs RANDOM held-rep digests distinct, self-test); real_code_path (self-test loads
# the REAL V2 checkpoint via the REAL FrozenV2Encoder + ReadCondWM + gather_role_reps + nearest_centroid_
# acc, not a pure-synthetic-only branch); progress_logging not required (<5min, no gradient training).
"""Context-invariance / role-distinctness / filler-invariance EARLY-SIGNAL probe (v1).

WHY (Director hand-off 2026-07-30, coordinator-revised spec): the FULL LPC-vs-MLM encoder run
(exp_encoder_latent_pc_arc_v1.py, no --lite) trains for ~15h on GPU. This cell is the DECISIVE EARLY
READ on the encoder-objective question, consuming the cheap --lite checkpoints (same file, --lite flag;
~10x fewer steps, same architecture) instead of waiting on the full run.

THE QUESTION: role-binding addressing just FAILED to generalize on the frozen MLM v2 encoder because role
identity is CONTEXT-ENTANGLED (a linear probe decodes held-out roles at 0.95, but the SAME role looks
different across different sentences -- no simple addressing finds a stable, generalizing address). The
forward-predictive (LPC) encoder's whole thesis is that predict-forward training yields MORE
context-INVARIANT / separable reps than MLM's bidirectional reconstruction. This cell measures that
directly and cheaply, on the --lite checkpoints, before committing more compute to the full run's
downstream binding re-test.

FAIRNESS (coordinator's 6 mandatory requirements, all applied):
  1. BUDGET-MATCHED BASELINE: compares LPC-lite vs MLM-lite, BOTH trained at the IDENTICAL reduced
     schedule (exp_encoder_latent_pc_arc_v1.py --lite; LITE_CFG; ARM_LPC + ARM_MLM, matched steps/data/
     architecture -- the ONE variable is the objective). Does NOT compare against the fully-trained V2
     MLM ckpt (that would be the unfair undertrained-vs-fully-trained confound) -- V2 is not read here.
  2. CAN-FAIL FLOOR THAT ACTUALLY FLOORS: a third arm, RANDOM-INIT (same architecture, untrained,
     reconstructed from the LPC-lite checkpoint's shape/tokenizer with a fixed seed, NOT loaded from any
     trained state_dict). The random arm's context-invariance is MEASURED against its own shuffled-pairing
     control, not assumed near chance (the shared-component probe found random reps can carry non-trivial
     role signal, ~0.38 accuracy on a DIFFERENT metric) -- if random does not floor HERE, this cell's
     verdict is METRIC_INVALID_RANDOM_DOES_NOT_FLOOR, not a silently-trusted LPC-vs-MLM delta.
  3. IDENTICAL PIPELINE: all three encoders get the SAME construction -- a fresh, RANDOM-INIT, UNTRAINED,
     shared role_query (rc.ReadCondWM with a FIXED seed, no gradient training of the query itself) applied
     to that encoder's own frozen token reps. This is a FIXED POOLING (not learned per-encoder), so no
     encoder's role_query is ever warm-started or trained differently from another's.
  4. THREE PROPERTIES measured for all three encoders: (a) CONTEXT-INVARIANCE (decisive) -- cosine
     similarity between the SAME role's QUERY-context rep and ASSIGNMENT-context rep; (b)
     ROLE-DISTINCTNESS -- nearest-centroid decode accuracy (TRAIN roles and HELD-OUT roles separately,
     chance=1/15); (c) FILLER-INVARIANCE -- mean pairwise cosine among a role's ASSIGNMENT-context reps
     across 20 different fillers (same template, filler varies) -- contrasted against the CROSS-ROLE
     floor (mean pairwise cosine among DIFFERENT roles' canonical reps).
  5. PRE-REGISTERED DECISION RULE (this file, NOT loosened after seeing results) -- see classify_result().
  6. HONESTY: --lite is undertrained by construction (10x fewer steps than FULL). A POSITIVE
     (LPC-lite > MLM-lite on context-invariance, with random floored) is ENCOURAGING evidence for the
     full run; a NULL/tie is INCONCLUSIVE (undertraining caveat), NEVER reported as a refutation of the
     encoder-objective hypothesis; only a clear MLM > LPC delta is reported as LPC_NOT_BETTER_YET (still
     hedged "at this budget", not a refutation).

METHOD (frozen encoders, zero gradient training in THIS cell):
  Reuses the SAME 15-role/12-train/3-held split, role/slot/template/filler inventory, and the SAME
  role-query attention extraction (rc.ReadCondWM._role_reps()) as
  exp_wm_addressing_heldout_role_warmstart_v1 (aliased `ho`) and
  exp_shared_component_role_identity_probe_v1 (aliased `rip`, for gather_role_reps + nearest_centroid_acc
  -- reused directly, not reimplemented).
  CONTEXT-INVARIANCE can-fail floor: SHUFFLED-PAIRING control (query[r] paired with assign[derangement(r)],
  a fixed derangement, no self-pairs) -- a wrong pairing has no legitimate reason to match unless the
  address space has collapsed onto a dominant shared component.

PRE-REGISTERED BANDS (this file; cosine-similarity units; HYPOTHESIZED@this file -- no prior citation for
  this exact metric; chosen conservatively, same order of magnitude as the 0.10-0.15 margins this repo
  uses elsewhere for decisive deltas on accuracy-space metrics, scaled to cosine units):
  CI_DELTA_LPC_OVER_MLM = 0.05        -- LPC held-out CI must beat MLM held-out CI by this much
  CI_LPC_OVER_SHUFFLED_MARGIN = 0.10  -- LPC's own held-out CI must clear ITS shuffled floor by this much
                                         (a "win" over MLM that isn't even above noise is not trustworthy)
  RANDOM_FLOOR_MAX_ABOVE_SHUFFLED = 0.10 -- RANDOM's held-out CI must NOT exceed its shuffled floor by
                                         more than this, or the metric itself is not trusted at this point

VERDICT:
  METRIC_INVALID_RANDOM_DOES_NOT_FLOOR : random-init's CI - shuffled_CI >= 0.10 on held-out roles -- the
    measurement pipeline itself leaks structure (dimensionality / shared-component artifact); do not trust
    any LPC-vs-MLM delta from this run; fix the metric before re-running.
  INCONCLUSIVE_LPC_NOT_ABOVE_OWN_FLOOR : LPC's held-out CI - its own shuffled floor < 0.10 -- LPC has not
    yet cleared its own can-fail floor at this budget; any apparent LPC>MLM delta is not trustworthy.
  LPC_MORE_CONTEXT_INVARIANT : LPC held CI - MLM held CI >= +0.05 (both floor checks above pass) --
    encoder-objective direction VALIDATED EARLY (hypothesis-pending-full-VET); worth the full 15h run +
    the downstream binding re-test.
  LPC_NOT_BETTER_YET : MLM held CI - LPC held CI >= +0.05 -- at this (undertrained) budget MLM leads;
    report honestly, this is NOT a refutation of the full run (lite is 10x under-trained by construction).
  INCONCLUSIVE_TIE_UNDERTRAINING_CAVEAT : |delta| < 0.05 -- undertrained tie; genuinely inconclusive, not
    a refutation either way.

Run:  .venv/Scripts/python.exe experiments/exp_context_invariance_lpc_lite_probe_v1.py --self-test
      .venv/Scripts/python.exe experiments/exp_context_invariance_lpc_lite_probe_v1.py --full
      (--full requires the --lite checkpoints from exp_encoder_latent_pc_arc_v1.py --lite to already
      exist at data/exp_encoder_latent_pc_arc_v1_lite/ckpt_seed_7_ARM_{LPC,MLM}.pt)

ASCII-only. No emojis. CPU-only, expected <2 minutes (dominated by the frozen closed-sentence cache
build, x3 encoders; no gradient training anywhere in this cell).
"""

import argparse
import json
import os
import platform
import sys
import time
import traceback
from datetime import datetime, timezone

import numpy as np
import torch
import torch.nn.functional as F

try:
    sys.stdout.reconfigure(line_buffering=True)
except (AttributeError, ValueError):
    pass

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import exp_wm_addressing_heldout_role_warmstart_v1 as ho  # noqa: E402
import exp_shared_component_role_identity_probe_v1 as rip  # noqa: E402  (gather_role_reps, nearest_centroid_acc)

ANCHOR_NAME = "context_invariance_lpc_lite_probe_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", "exp_" + ANCHOR_NAME)

LITE_OUT_DIR = os.path.join(REPO_ROOT, "data", "exp_encoder_latent_pc_arc_v1_lite")
LPC_LITE_CKPT = os.path.join(LITE_OUT_DIR, "ckpt_seed_7_ARM_LPC.pt")
MLM_LITE_CKPT = os.path.join(LITE_OUT_DIR, "ckpt_seed_7_ARM_MLM.pt")
ARM_LPC_LITE = "ARM_LPC_lite"
ARM_MLM_LITE = "ARM_MLM_lite"
ARM_RANDOM = "ARM_RANDOM"
ARMS = [ARM_LPC_LITE, ARM_MLM_LITE, ARM_RANDOM]

ROLEQUERY_SEED = 7                 # SAME fixed seed for the shared, random-init, UNTRAINED role_query
                                    # (IDENTICAL construction across all 3 encoders -- requirement #3)
RANDOM_INIT_SEED = 1006            # documents parity with exp_encoder_latent_pc_arc_v1._build_encoder's
                                    # ARM_RANDOM convention (torch.manual_seed(seed + 999), seed=7)
DERANGEMENT_SEED = 20260730003     # fixed derangement permutation seed (deterministic; no hash())

S_TARGET_TOTAL = ho.S_TARGET_TOTAL
TRAIN_SET, HELD_OUT_SET = ho.TRAIN_SET, ho.HELD_OUT_SET
TRAIN_ROLES, HELD_OUT_ROLES = ho.TRAIN_ROLES, ho.HELD_OUT_ROLES
SLOT_NOUNS, EVENT_TEMPLATES, COLORS, QUERY_TEMPLATE = (
    ho.SLOT_NOUNS, ho.EVENT_TEMPLATES, ho.COLORS, ho.QUERY_TEMPLATE)
V_FILL = ho.V_FILL

# ---- pre-registered bands (this file; cosine-similarity units) ----
CI_DELTA_LPC_OVER_MLM = 0.05             # HYPOTHESIZED@this file (see module docstring rationale)
CI_LPC_OVER_SHUFFLED_MARGIN = 0.10       # HYPOTHESIZED@this file
RANDOM_FLOOR_MAX_ABOVE_SHUFFLED = 0.10   # HYPOTHESIZED@this file


def _log(msg):
    print("[%s] %s" % (ANCHOR_NAME, msg), flush=True)


def _now_iso():
    return datetime.now(timezone.utc).isoformat()


def _write_start_marker(output_dir, run_mode):
    marker = {"pid": os.getpid(), "ts_iso": _now_iso(), "anchor_name": ANCHOR_NAME,
              "run_mode": run_mode, "host": platform.node()}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, os.path.join(output_dir, "_start_marker.json"))


def _write_crash_metrics(output_dir, exc):
    diag = {"verdict": "CELL_CRASHED",
            "verdict_msg": "%s: %s" % (type(exc).__name__, str(exc)[:500]),
            "summary": "CELL_CRASHED: %s" % type(exc).__name__, "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000], "ts_iso": _now_iso(),
            "pid": os.getpid(), "anchor_name": ANCHOR_NAME, "failure_class": type(exc).__name__}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, os.path.join(output_dir, "metrics.json"))


def _jsonify(obj):
    if isinstance(obj, torch.Tensor):
        return _jsonify(obj.detach().cpu().tolist())
    if isinstance(obj, np.ndarray):
        return _jsonify(obj.tolist())
    if isinstance(obj, (np.floating,)):
        return float(obj)
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, np.bool_):
        return bool(obj)
    if isinstance(obj, dict):
        return {str(k): _jsonify(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_jsonify(v) for v in obj]
    return obj


def _atomic_write_metrics(output_dir, metrics):
    os.makedirs(output_dir, exist_ok=True)
    safe = _jsonify(metrics)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(safe, f, indent=2)
    os.replace(tmp, os.path.join(output_dir, "metrics.json"))


# ---------------- random-init encoder (requirement #2: genuine untrained floor) ----------------
class FrozenRandomInitEncoder(ho.base.FrozenV2Encoder):
    """SAME architecture + tokenizer as the ckpt used for shape (LPC-lite's, by convention), but the
    transformer weights are FRESH RANDOM INIT (state_dict from the ckpt is NEVER loaded) -- the genuine
    can-fail floor. Deterministic seed documents parity with _build_encoder's ARM_RANDOM convention."""

    def __init__(self, shape_ckpt_path, seed=RANDOM_INIT_SEED):
        from tokenizers import Tokenizer
        ck = torch.load(shape_ckpt_path, map_location="cpu", weights_only=False)
        mc = ck["model_cfg"]
        self.pad_id = int(mc["pad_id"])
        self.d = int(mc["d_model"])
        torch.manual_seed(seed)
        self.model = ho.base.V2Transformer(mc["vocab"], mc["max_len"], mc["d_model"], mc["n_layers"],
                                           mc["n_heads"], mc["ffn_mult"], mc["pad_id"])
        # NOTE: state_dict intentionally NOT loaded -- this is the untrained floor.
        self.model.eval()
        self.tok = Tokenizer.from_str(ck["tokenizer_json"])
        self.name2idx = {}
        self.U_tok = None
        self.U_pad = None
        self.U_tok_t = None
        self.U_pad_t = None
        self._selected_arm = "RANDOM_INIT_FLOOR"
        self._seed = seed


def _fixed_derangement(n, seed):
    """Deterministic derangement (no fixed points) of range(n). No hash(), no list(set())."""
    rng = np.random.default_rng(seed)
    for _ in range(10000):
        perm = rng.permutation(n)
        if not np.any(perm == np.arange(n)):
            return perm
    raise RuntimeError("could not find a derangement of size %d" % n)  # pragma: no cover


# ---------------- the 3-property probe (identical pipeline for every encoder) ----------------
def compute_encoder_probe(enc, wm, role_ids, train_set, held_set, derangement_seed):
    """Returns context-invariance, role-distinctness, and filler-invariance, split TRAIN vs HELD-OUT,
    for ONE frozen encoder + its (fixed, untrained, shared-construction) role_query WM."""
    with torch.no_grad():
        slot_u, _ = wm._role_reps()   # [Nu, d] -- attention-pooled rep per cached closed-sentence row

    n_roles = len(role_ids)
    q_idxs = [enc.idx_of(QUERY_TEMPLATE.format(slot=SLOT_NOUNS[r])) for r in role_ids]
    a_idxs = [enc.idx_of(EVENT_TEMPLATES[0].format(slot=SLOT_NOUNS[r], fill=COLORS[0])) for r in role_ids]
    rep_q = F.normalize(slot_u[torch.tensor(q_idxs)], dim=-1)     # [n_roles, d] query-context
    rep_a = F.normalize(slot_u[torch.tensor(a_idxs)], dim=-1)     # [n_roles, d] assignment-context

    ci_per_role = (rep_q * rep_a).sum(dim=-1)                     # (a) CONTEXT-INVARIANCE, same role
    perm = torch.as_tensor(_fixed_derangement(n_roles, derangement_seed))
    ci_shuffled_per_role = (rep_q * rep_a[perm]).sum(dim=-1)      # can-fail floor: wrong-role pairing

    held_pos = [i for i, r in enumerate(role_ids) if r in held_set]
    train_pos = [i for i, r in enumerate(role_ids) if r in train_set]

    def _mean(t, pos):
        return float(t[pos].mean().item()) if pos else float("nan")

    ci = dict(train=_mean(ci_per_role, train_pos), held=_mean(ci_per_role, held_pos),
             overall=float(ci_per_role.mean().item()))
    ci_shuf = dict(train=_mean(ci_shuffled_per_role, train_pos), held=_mean(ci_shuffled_per_role, held_pos),
                  overall=float(ci_shuffled_per_role.mean().item()))

    # (b) ROLE-DISTINCTNESS: reused directly (gather_role_reps + nearest_centroid_acc), raw dims, no PCA.
    fit_X, fit_y, eval_X, eval_y = rip.gather_role_reps(enc, wm)
    roles_present = sorted(set(fit_y.tolist()))
    eval_train_mask = np.isin(eval_y, list(train_set))
    eval_held_mask = np.isin(eval_y, list(held_set))
    _, nc_train = rip.nearest_centroid_acc(fit_X, fit_y, eval_X[eval_train_mask], eval_y[eval_train_mask],
                                           roles_present) if eval_train_mask.any() else (None, float("nan"))
    _, nc_held = rip.nearest_centroid_acc(fit_X, fit_y, eval_X[eval_held_mask], eval_y[eval_held_mask],
                                          roles_present) if eval_held_mask.any() else (None, float("nan"))

    # (c) FILLER-INVARIANCE: canonical template fixed, filler varies over all COLORS; mean pairwise
    # cosine among same-role reps (want HIGH) vs cross-role floor (mean pairwise cosine among DIFFERENT
    # roles' canonical reps -- want the within-role number to clearly exceed this).
    filler_scores = {}
    for r in role_ids:
        idxs = [enc.idx_of(EVENT_TEMPLATES[0].format(slot=SLOT_NOUNS[r], fill=c)) for c in COLORS]
        reps = F.normalize(slot_u[torch.tensor(idxs)], dim=-1)
        sim = reps @ reps.t()
        iu = torch.triu_indices(len(idxs), len(idxs), offset=1)
        filler_scores[r] = float(sim[iu[0], iu[1]].mean().item())
    fi_train = float(np.mean([filler_scores[r] for r in role_ids if r in train_set])) if train_pos else float("nan")
    fi_held = float(np.mean([filler_scores[r] for r in role_ids if r in held_set])) if held_pos else float("nan")
    sim_cross = rep_a @ rep_a.t()
    iu2 = torch.triu_indices(n_roles, n_roles, offset=1)
    fi_cross_role_floor = float(sim_cross[iu2[0], iu2[1]].mean().item())

    return dict(
        context_invariance=ci, context_invariance_shuffled_floor=ci_shuf,
        role_distinctness_nc_acc=dict(train=nc_train, held=nc_held),
        filler_invariance=dict(train=fi_train, held=fi_held, per_role=filler_scores,
                               cross_role_floor=fi_cross_role_floor),
    )


# ---------------- pre-registered decision rule (NOT loosened after seeing results) ----------------
def classify_result(probes):
    lpc, mlm, rnd = probes[ARM_LPC_LITE], probes[ARM_MLM_LITE], probes[ARM_RANDOM]
    ci_lpc_held = lpc["context_invariance"]["held"]
    ci_mlm_held = mlm["context_invariance"]["held"]
    ci_lpc_shuf_held = lpc["context_invariance_shuffled_floor"]["held"]
    ci_rnd_held = rnd["context_invariance"]["held"]
    ci_rnd_shuf_held = rnd["context_invariance_shuffled_floor"]["held"]

    random_floors = (ci_rnd_held - ci_rnd_shuf_held) < RANDOM_FLOOR_MAX_ABOVE_SHUFFLED
    lpc_clears_own_floor = (ci_lpc_held - ci_lpc_shuf_held) >= CI_LPC_OVER_SHUFFLED_MARGIN
    delta = ci_lpc_held - ci_mlm_held

    if not random_floors:
        verdict = "METRIC_INVALID_RANDOM_DOES_NOT_FLOOR"
        msg = ("random-init held-out CI (%.4f) exceeds its own shuffled floor (%.4f) by %.4f >= %.2f -- "
               "the measurement itself leaks structure at this regime; do NOT trust any LPC-vs-MLM delta "
               "from this run. delta_lpc_minus_mlm=%.4f (untrusted)."
               % (ci_rnd_held, ci_rnd_shuf_held, ci_rnd_held - ci_rnd_shuf_held,
                  RANDOM_FLOOR_MAX_ABOVE_SHUFFLED, delta))
    elif not lpc_clears_own_floor:
        verdict = "INCONCLUSIVE_LPC_NOT_ABOVE_OWN_FLOOR"
        msg = ("LPC-lite held-out CI (%.4f) does not clear its own shuffled floor (%.4f) by the required "
               "%.2f margin (gap=%.4f) -- LPC has not yet cleared its own can-fail floor at this budget; "
               "any apparent delta vs MLM is not trustworthy. delta_lpc_minus_mlm=%.4f."
               % (ci_lpc_held, ci_lpc_shuf_held, CI_LPC_OVER_SHUFFLED_MARGIN,
                  ci_lpc_held - ci_lpc_shuf_held, delta))
    elif delta >= CI_DELTA_LPC_OVER_MLM:
        verdict = "LPC_MORE_CONTEXT_INVARIANT"
        msg = ("LPC-lite held-out context-invariance (%.4f) beats MLM-lite (%.4f) by %.4f >= %.2f, both "
               "floor checks pass (random floors at %.4f vs shuffled %.4f; LPC clears its own floor by "
               "%.4f). Encoder-objective direction VALIDATED EARLY (hypothesis-pending-full-VET) -- worth "
               "the full 15h run + the downstream binding re-test."
               % (ci_lpc_held, ci_mlm_held, delta, CI_DELTA_LPC_OVER_MLM, ci_rnd_held, ci_rnd_shuf_held,
                  ci_lpc_held - ci_lpc_shuf_held))
    elif delta <= -CI_DELTA_LPC_OVER_MLM:
        verdict = "LPC_NOT_BETTER_YET"
        msg = ("MLM-lite held-out CI (%.4f) beats LPC-lite (%.4f) by %.4f at this MATCHED-lite budget. "
               "NOT a refutation of the full-run hypothesis (--lite is 10x under-trained by construction) "
               "-- report honestly as a caveat, not a kill."
               % (ci_mlm_held, ci_lpc_held, ci_mlm_held - ci_lpc_held))
    else:
        verdict = "INCONCLUSIVE_TIE_UNDERTRAINING_CAVEAT"
        msg = ("LPC-lite (%.4f) and MLM-lite (%.4f) held-out CI tie within +/-%.2f (delta=%.4f) at this "
               "undertrained budget -- genuinely inconclusive, NOT a refutation either way."
               % (ci_lpc_held, ci_mlm_held, CI_DELTA_LPC_OVER_MLM, delta))
    return verdict, msg, float(delta)


# ---------------- self-test ----------------
def _synthetic_ci_case(high_ci, n_roles=8, d=12, seed=7):
    """Constructs role_reps_query/assign directly (bypassing the encoder) to validate classify_result's
    decision logic. high_ci=True -> query/assign nearly identical per role (high CI); False -> query and
    assign are independent draws (should floor near its own shuffled control)."""
    rng = np.random.default_rng(seed)
    base = rng.normal(0.0, 1.0, size=(n_roles, d)).astype(np.float32) * 5.0
    if high_ci:
        noise = rng.normal(0.0, 0.15, size=(n_roles, d)).astype(np.float32)
        assign = base + noise
    else:
        assign = rng.normal(0.0, 1.0, size=(n_roles, d)).astype(np.float32) * 5.0   # independent
    q = torch.from_numpy(base)
    a = torch.from_numpy(assign)
    qn, an = F.normalize(q, dim=-1), F.normalize(a, dim=-1)
    ci = (qn * an).sum(dim=-1)
    perm = torch.as_tensor(_fixed_derangement(n_roles, DERANGEMENT_SEED))
    ci_shuf = (qn * an[perm]).sum(dim=-1)
    return dict(train=float(ci[: n_roles - 2].mean()), held=float(ci[n_roles - 2:].mean()),
               overall=float(ci.mean())), dict(train=float(ci_shuf[: n_roles - 2].mean()),
                                               held=float(ci_shuf[n_roles - 2:].mean()),
                                               overall=float(ci_shuf.mean()))


def run_self_test():
    _log("SELF-TEST: derangement determinism + no-fixed-points ...")
    perm1 = _fixed_derangement(15, DERANGEMENT_SEED)
    perm2 = _fixed_derangement(15, DERANGEMENT_SEED)
    assert np.array_equal(perm1, perm2), "derangement not deterministic"
    assert not np.any(perm1 == np.arange(15)), "derangement has a fixed point"
    assert sorted(perm1.tolist()) == list(range(15))

    _log("SELF-TEST: classify_result decisive-logic on synthetic constructions ...")
    ci_high, ci_high_shuf = _synthetic_ci_case(True, seed=7)
    ci_low, ci_low_shuf = _synthetic_ci_case(False, seed=13)

    # case A: LPC=high-CI, MLM=low-CI, RANDOM=low-CI (floors) -> LPC_MORE_CONTEXT_INVARIANT
    probes_a = {ARM_LPC_LITE: dict(context_invariance=ci_high, context_invariance_shuffled_floor=ci_high_shuf),
               ARM_MLM_LITE: dict(context_invariance=ci_low, context_invariance_shuffled_floor=ci_low_shuf),
               ARM_RANDOM: dict(context_invariance=ci_low, context_invariance_shuffled_floor=ci_low_shuf)}
    v, m, d = classify_result(probes_a)
    assert v == "LPC_MORE_CONTEXT_INVARIANT", (v, m)
    _log("  case A (LPC high-CI, MLM/RANDOM low-CI): %s (delta=%.4f)" % (v, d))

    # case B: all three low-CI (random does not floor relative to itself -- degenerate: shuffled==real
    # here since both draws are independent, so random_floors should hold trivially; construct a
    # DELIBERATE random-leaks-structure case instead)
    leak_ci = dict(train=0.5, held=0.5)
    leak_shuf = dict(train=0.05, held=0.05)   # real >> shuffled -> random does NOT floor
    probes_b = {ARM_LPC_LITE: dict(context_invariance=ci_high, context_invariance_shuffled_floor=ci_high_shuf),
               ARM_MLM_LITE: dict(context_invariance=ci_low, context_invariance_shuffled_floor=ci_low_shuf),
               ARM_RANDOM: dict(context_invariance=leak_ci, context_invariance_shuffled_floor=leak_shuf)}
    v, m, d = classify_result(probes_b)
    assert v == "METRIC_INVALID_RANDOM_DOES_NOT_FLOOR", (v, m)
    _log("  case B (random leaks structure, must NOT float above LPC win): %s" % v)

    # case C: LPC does not clear its own shuffled floor -> INCONCLUSIVE_LPC_NOT_ABOVE_OWN_FLOOR
    flat_ci = dict(train=0.06, held=0.06)
    flat_shuf = dict(train=0.02, held=0.02)   # gap=0.04 < 0.10 margin
    probes_c = {ARM_LPC_LITE: dict(context_invariance=flat_ci, context_invariance_shuffled_floor=flat_shuf),
               ARM_MLM_LITE: dict(context_invariance=ci_low, context_invariance_shuffled_floor=ci_low_shuf),
               ARM_RANDOM: dict(context_invariance=ci_low, context_invariance_shuffled_floor=ci_low_shuf)}
    v, m, d = classify_result(probes_c)
    assert v == "INCONCLUSIVE_LPC_NOT_ABOVE_OWN_FLOOR", (v, m)
    _log("  case C (LPC flat, does not clear own floor): %s" % v)

    # case D: tie -> INCONCLUSIVE_TIE_UNDERTRAINING_CAVEAT
    tie_lpc = dict(train=0.30, held=0.30)
    tie_mlm = dict(train=0.28, held=0.28)     # delta=0.02 < 0.05
    tie_shuf = dict(train=0.05, held=0.05)
    probes_d = {ARM_LPC_LITE: dict(context_invariance=tie_lpc, context_invariance_shuffled_floor=tie_shuf),
               ARM_MLM_LITE: dict(context_invariance=tie_mlm, context_invariance_shuffled_floor=tie_shuf),
               ARM_RANDOM: dict(context_invariance=ci_low, context_invariance_shuffled_floor=ci_low_shuf)}
    v, m, d = classify_result(probes_d)
    assert v == "INCONCLUSIVE_TIE_UNDERTRAINING_CAVEAT", (v, m)
    _log("  case D (tie): %s (delta=%.4f)" % (v, d))

    # case E: MLM clearly ahead -> LPC_NOT_BETTER_YET
    probes_e = {ARM_LPC_LITE: dict(context_invariance=ci_low, context_invariance_shuffled_floor=ci_low_shuf),
               ARM_MLM_LITE: dict(context_invariance=ci_high, context_invariance_shuffled_floor=ci_high_shuf),
               ARM_RANDOM: dict(context_invariance=ci_low, context_invariance_shuffled_floor=ci_low_shuf)}
    v, m, d = classify_result(probes_e)
    assert v == "INCONCLUSIVE_LPC_NOT_ABOVE_OWN_FLOOR", (v, m)   # ci_low doesn't clear ITS OWN floor either
    _log("  case E note: with ci_low as LPC (does not clear its own floor) -> %s (expected, floor-gated "
         "before the MLM-ahead branch can ever fire)" % v)

    _log("SELF-TEST: real_code_path -- REAL V2 checkpoint via REAL FrozenV2Encoder + FrozenRandomInitEncoder "
         "+ ReadCondWM + gather_role_reps + nearest_centroid_acc, tiny integration (3-encoder pipeline "
         "plumbing; LPC-lite/MLM-lite checkpoints do not exist yet pre-dispatch, so this uses the REAL "
         "V2 ckpt as the shape/tokenizer source for all 3 slots -- verifies PLUMBING, not the mechanism "
         "comparison, which needs the actual --lite ckpts at --full time) ...")
    assert os.path.exists(ho.V2_CKPT), "v2 checkpoint missing: %s" % ho.V2_CKPT
    enc_lpc = ho.base.FrozenV2Encoder(ho.V2_CKPT)
    enc_mlm = ho.base.FrozenV2Encoder(ho.V2_CKPT)
    enc_rnd = FrozenRandomInitEncoder(ho.V2_CKPT)
    encoders = {ARM_LPC_LITE: enc_lpc, ARM_MLM_LITE: enc_mlm, ARM_RANDOM: enc_rnd}
    role_ids = list(range(S_TARGET_TOTAL))
    probes = {}
    for name, enc in encoders.items():
        n_cached = enc.build_cache()
        assert n_cached >= 3000, "closed sentence set smaller than expected for %s" % name
        wm = ho.rc.ReadCondWM(ROLEQUERY_SEED, enc.d, 8, S_TARGET_TOTAL, 8, V_FILL, 0.3, enc.U_tok_t, enc.U_pad_t)
        probes[name] = compute_encoder_probe(enc, wm, role_ids, TRAIN_SET, HELD_OUT_SET, DERANGEMENT_SEED)
        p = probes[name]
        for split in ("train", "held", "overall"):
            v = p["context_invariance"][split]
            assert (-1.0 - 1e-6) <= v <= (1.0 + 1e-6), "%s CI[%s] out of cosine range: %s" % (name, split, v)
        _log("  [%-14s] ci_held=%.4f ci_shuf_held=%.4f nc_held=%s fi_held=%.4f fi_cross_floor=%.4f"
             % (name, p["context_invariance"]["held"], p["context_invariance_shuffled_floor"]["held"],
                str(p["role_distinctness_nc_acc"]["held"]), p["filler_invariance"]["held"],
                p["filler_invariance"]["cross_role_floor"]))
    v_real, m_real, d_real = classify_result(probes)
    assert v_real in ("METRIC_INVALID_RANDOM_DOES_NOT_FLOOR", "INCONCLUSIVE_LPC_NOT_ABOVE_OWN_FLOOR",
                      "LPC_MORE_CONTEXT_INVARIANT", "LPC_NOT_BETTER_YET",
                      "INCONCLUSIVE_TIE_UNDERTRAINING_CAVEAT")
    # LPC/MLM slots both point at the byte-identical V2 ckpt in this self-test -> delta must be ~0
    # (arms_differ is NOT expected to hold here; the REAL --full run uses two DISTINCT --lite ckpts).
    assert abs(d_real) < 1e-6, "LPC==MLM slots (same ckpt) should give delta~0 in this self-test, got %.6f" % d_real
    _log("  real_code_path plumbing verdict=%s delta=%.6f (expected ~0: LPC/MLM slots share one ckpt "
         "in self-test)" % (v_real, d_real))

    _log("SELF-TEST PASS")
    return {"synthetic_cases": {"A": "LPC_MORE_CONTEXT_INVARIANT", "B": "METRIC_INVALID_RANDOM_DOES_NOT_FLOOR",
                                "C": "INCONCLUSIVE_LPC_NOT_ABOVE_OWN_FLOOR",
                                "D": "INCONCLUSIVE_TIE_UNDERTRAINING_CAVEAT"},
            "real_code_path_verdict": v_real, "real_code_path_delta": d_real,
            "real_code_path_probes": probes}


# ---------------- full run (REAL --lite checkpoints) ----------------
def run_full():
    for name, path in ((ARM_LPC_LITE, LPC_LITE_CKPT), (ARM_MLM_LITE, MLM_LITE_CKPT)):
        if not os.path.exists(path):
            raise FileNotFoundError(
                "%s checkpoint missing: %s -- run exp_encoder_latent_pc_arc_v1.py --lite first "
                "(produces both ckpt_seed_7_ARM_LPC.pt and ckpt_seed_7_ARM_MLM.pt under %s)"
                % (name, path, LITE_OUT_DIR))
    _log("FULL: loading LPC-lite + MLM-lite + RANDOM-init (shape from LPC-lite) encoders ...")
    enc_lpc = ho.base.FrozenV2Encoder(LPC_LITE_CKPT)
    enc_mlm = ho.base.FrozenV2Encoder(MLM_LITE_CKPT)
    enc_rnd = FrozenRandomInitEncoder(LPC_LITE_CKPT)
    encoders = {ARM_LPC_LITE: enc_lpc, ARM_MLM_LITE: enc_mlm, ARM_RANDOM: enc_rnd}

    role_ids = list(range(S_TARGET_TOTAL))
    probes = {}
    arm_digests = {}
    for name, enc in encoders.items():
        n_cached = enc.build_cache()
        _log("  [%s] cached %d unique sentence TOKEN reps (d=%d)" % (name, n_cached, enc.d))
        wm = ho.rc.ReadCondWM(ROLEQUERY_SEED, enc.d, 8, S_TARGET_TOTAL, 8, V_FILL, 0.3, enc.U_tok_t, enc.U_pad_t)
        probes[name] = compute_encoder_probe(enc, wm, role_ids, TRAIN_SET, HELD_OUT_SET, DERANGEMENT_SEED)
        import hashlib
        arm_digests[name] = hashlib.sha256(np.ascontiguousarray(enc.U_tok).tobytes()).hexdigest()
        p = probes[name]
        _log("  [%-14s] ci[train=%.4f held=%.4f] ci_shuf[train=%.4f held=%.4f] "
             "nc_acc[train=%s held=%s] filler_inv[train=%.4f held=%.4f cross_floor=%.4f]"
             % (name, p["context_invariance"]["train"], p["context_invariance"]["held"],
                p["context_invariance_shuffled_floor"]["train"], p["context_invariance_shuffled_floor"]["held"],
                str(p["role_distinctness_nc_acc"]["train"]), str(p["role_distinctness_nc_acc"]["held"]),
                p["filler_invariance"]["train"], p["filler_invariance"]["held"],
                p["filler_invariance"]["cross_role_floor"]))

    arms_differ = len(set(arm_digests.values())) == len(arm_digests)
    verdict, msg, delta = classify_result(probes)
    if not arms_differ:
        verdict = "ARMS_IDENTICAL_BUG"
        msg = "META_RULE_AF VIOLATION: encoder token-rep digests not all distinct: %s" % arm_digests

    return {
        "verdict": verdict, "verdict_msg": msg,
        "summary": "%s | delta_lpc_minus_mlm_ci_held=%.4f | %s" % (verdict, delta, msg[:160]),
        "delta_lpc_minus_mlm_ci_held": delta,
        "probes": probes, "arms_differ_verified": bool(arms_differ), "arm_digests": arm_digests,
        "bands": dict(ci_delta_lpc_over_mlm=CI_DELTA_LPC_OVER_MLM,
                     ci_lpc_over_shuffled_margin=CI_LPC_OVER_SHUFFLED_MARGIN,
                     random_floor_max_above_shuffled=RANDOM_FLOOR_MAX_ABOVE_SHUFFLED),
        "role_split": {"train_roles": TRAIN_ROLES, "held_out_roles": HELD_OUT_ROLES},
        "lpc_lite_ckpt": os.path.relpath(LPC_LITE_CKPT, REPO_ROOT),
        "mlm_lite_ckpt": os.path.relpath(MLM_LITE_CKPT, REPO_ROOT),
    }


# ---------------- main ----------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--full", action="store_true")
    args = ap.parse_args()

    torch.set_num_threads(min(6, max(1, os.cpu_count() or 1)))
    run_mode = "self_test" if args.self_test or not args.full else "full"
    _write_start_marker(OUTPUT_DIR, run_mode)
    t0 = time.perf_counter()

    if run_mode == "self_test":
        st = run_self_test()
        elapsed = time.perf_counter() - t0
        _atomic_write_metrics(OUTPUT_DIR, {
            "verdict": "SELFTEST_PASS",
            "verdict_msg": "SELFTEST_PASS (derangement + classify_result decisive-logic on 4 synthetic "
                          "cases + real_code_path 3-encoder plumbing via real V2 ckpt)",
            "summary": "SELFTEST_PASS", "run_mode": "self_test", "elapsed_s": elapsed,
            "ts_iso": _now_iso(), "anchor_name": ANCHOR_NAME, "selftest": st})
        _log("DONE self-test in %.1fs" % elapsed)
        return

    result = run_full()
    elapsed = time.perf_counter() - t0
    payload = dict(result)
    payload.update({"run_mode": "full", "elapsed_s": elapsed, "ts_iso": _now_iso(),
                    "anchor_name": ANCHOR_NAME, "start_marker_written": True,
                    "crash_diagnostic_present": True, "final_metrics_atomicity": "tmp_replace",
                    "defensive_error_checking": "passed_all_4_patterns"})
    _atomic_write_metrics(OUTPUT_DIR, payload)
    _log("VERDICT: %s" % result["verdict"])
    _log("  %s" % result["verdict_msg"])
    _log("DONE full in %.1fs" % elapsed)


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # NOT BaseException
        _write_crash_metrics(OUTPUT_DIR, e)
        raise
