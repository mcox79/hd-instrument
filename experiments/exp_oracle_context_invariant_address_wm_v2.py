# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at self-test (META_RULE_AF; CONTEXT/ORACLE/JITTERED/ONEHOT eval-logit hashes)
# - final_metrics_atomicity: tmp_replace (os.replace at end)
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_n/a: no Cramer-Rao noise floor; discriminator = held-out-role RECALL accuracy vs the
#   pre-registered CONTEXT_INVARIANCE_SUFFICIENT_ZEROSHOT/INSUFFICIENT_ZEROSHOT/INVALID bands
#   (Director spawn 2026-07-30, fixing 3 flaws found by VET in commit 107b11848's v1 cell).
#   chance_recall=1/V_FILL=0.05, oracle ceiling 1.0.
# - baseline_in_band: ARM_CONTEXTVARYING (floor A, real context-varying reps) and ARM_JITTERED
#   (floor B, distinct-but-UNSTABLE oracle address) are the can-fail controls; BOTH MUST fail
#   (near-chance held-out recall), else the test is INVALID (a floor failed to fail).
# - discriminator survives scale: this cell IS the discriminator-preview -- a decisive, cheap (<8min),
#   frozen-encoder ORACLE probe run BEFORE any encoder-training bet. self-test builds the REAL v2
#   encoder + REAL ReadCondWM at tiny N (real_code_path).
# - numbers in comments tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@ (META_RULE_AC)
# - deterministic seeding: numpy default_rng + torch.manual_seed/torch.Generator only; NO hash(),
#   NO list(set())
"""ORACLE context-invariant role-address vs the proven content-gated WM -- v2, fixing 3 flaws a VET
found in v1 (commit 107b11848, exp_oracle_context_invariant_address_wm_v1.py):

FLAW 1 FIXED -- TRUE ZERO-SHOT (was: held-out-role QUERIES entered end-to-end recall-CE training,
even though they got no ADDRESS supervision -- so v1 proved sentence/item-generalization with
recall-trained held-out roles, not binding a role NEVER seen in training).
  FIX + ENFORCEMENT: this cell builds the TRAINING corpus with a brand-new generator,
  gen_dataset_zeroshot(n, rng, role_pool=TRAIN_ROLES_V2), that restricts BOTH target-role WRITES and
  the QUERY selection to TRAIN_ROLES_V2 only (see gen_stream_zeroshot below) -- held-out roles are
  ABSENT from the training corpus itself (not merely masked out of a loss term), so they never occur
  as an event token or a query in ANY training minibatch, and consequently never receive an update
  target from the recall-CE loss (the loss is computed only over minibatches drawn from this corpus).
  zeroshot_construction_selftest() asserts n_heldout_query == 0 AND n_heldout_event == 0 over a
  training-corpus sample, i.e. directly measures (not merely argues) the zero-shot property before any
  training happens. The EVAL corpus (gen_dataset_zeroshot(n, rng, role_pool=ALL 15 roles)) is the ONLY
  place held-out roles appear, and it is never used for a gradient step.

FLAW 2 FIXED -- GENUINE CAN-FAIL FLOOR (was: v1's "shuffled" arm permuted the oracle table across
roles, which is STILL a stable+distinct address per role -- v1's actual measured shuffled_held was
[0.647, 0.232] MEASURED@data/exp_oracle_context_invariant_address_wm_v1/metrics.json:bands.shuffled_held,
i.e. it did NOT fail, so it could not discriminate "correct addressing" from "merely stable addressing"
-- v1 landed INVALID on exactly this flaw).
  FIX: ARM_JITTERED replaces "shuffled". Same per-role oracle base vector, but FRESH per-occurrence
  Gaussian noise is added on EVERY forward call (a torch.Generator advances state call-to-call, so
  even the identical (role, sentence) pair gets a DIFFERENT address vector each time it is read) --
  distinct-on-average (the noise is centered on the correct role's oracle row) but NOT STABLE (no two
  occurrences share a vector). The noise scale (JITTER_STD) is MEASURED from the real encoder, not an
  arbitrary knob: it is the mean per-context deviation of the REAL role-query-extracted rep around its
  own role's oracle-table mean (compute_context_var_scale), i.e. jitter is exactly as unstable as the
  real context-varying representation already shown to fail (ARM_CONTEXTVARYING). This arm MUST fail
  (near chance), proving STABILITY -- not mere role-distinctness -- is the load-bearing property.
  jitter_instability_selftest() directly measures that two successive jittered draws for the identical
  (role, sentence) differ, while two successive oracle draws are bit-identical.

FLAW 3 FIXED -- POWER (was: 3 held-out roles, 2 seeds -> underpowered, magnitude seed-noisy 0.57 vs
0.89, only qualitative direction survived).
  FIX: a NEW disjoint role split, TRAIN_ROLES_V2 (10 roles) / HELD_OUT_ROLES_V2 (5 roles) out of the
  SAME S_TARGET_TOTAL=15 role inventory (ROLE_SPLIT_SEED_V2, independent of ho's 3-held-out split so
  this cell's zero-shot corpus and ho's existing cells never collide), and SEEDS_FULL=(7,13,19), 3
  seeds. Mean +/- sd across seeds reported for every arm.

CONSTRUCTION (reuses the SAME proven ReadCondWM architecture + pca_whiten Conditioner + frozen v2
encoder as exp_selective_overwrite_recall_nl_wm_readcond_v1 (aliased `rc`) and
exp_selective_overwrite_recall_nl_wm_roleseparated_v1 (aliased `base`, whose S_TARGET module-global is
monkeypatched to 15 by exp_wm_addressing_heldout_role_warmstart_v1, aliased `ho`, imported for that
side-effect + its generic calib-derived helpers/oracle-sanity fns only -- this cell's OWN role split
and dataset generator are independent of ho's TRAIN_ROLES/HELD_OUT_ROLES/gen_dataset_expanded).

ORACLE TABLE (context-invariant address, one row per role, all 15 roles -- LEGITIMATE here: an
upper-bound oracle probe of "does the property suffice", not a deployable method): a FIXED
(never-trained) probe role-query attends over pca_whiten-conditioned frozen-v2 token reps of EVERY
cached context for that role, then averages them into ONE stable vector per role.

THE ONE VARIABLE: what feeds the WM's address key-lookup (`wm._addr_logits`) for a TARGET-role
event/query token. The filler-VALUE extraction path, the write-gate's input, the WM architecture, the
split, the seeds, and the training steps are IDENTICAL across all four arms (see read_features_arm()).
Distractor-role tokens (slot id >= 15) always keep the natural context-varying address input in every
arm, so distractor-suppression learning is not a confound between arms.

ARMS (3 seeds each: 7, 13, 19):
  ARM_CONTEXTVARYING  -- address input = the actual per-sentence role-query-extracted rep (context-
    varying). CAN-FAIL FLOOR A: MUST reproduce near-chance held-out recall, or the test is vacuous.
  ARM_ORACLE_INVARIANT -- address input = the oracle table row for that role (same vector regardless
    of which context produced the token; same vector regardless of which forward CALL reads it). THE
    DECISIVE ARM.
  ARM_JITTERED -- address input = the oracle table row PLUS fresh per-occurrence noise (same role,
    different vector every read). CAN-FAIL FLOOR B: MUST also fail, or a distinct-but-unstable address
    would "work" too and the metric can't discriminate stability from mere distinctness.
  ARM_ONEHOT_ORACLE -- address input = 15 orthonormal directions (QR of a random matrix), one per
    role: a CEILING reference establishing the WM's best case given PERFECT, maximally separated,
    stable addressing (not load-bearing for the verdict; reported alongside).

DECISIVE METRIC: recall_heldout_acc (predicted filler == true filler, evaluated on held-out-role
queries that were NEVER present in the training corpus), all 3 seeds. recall_train_acc also reported
(secondary). Mean +/- sd across seeds reported per arm.

PRE-REGISTERED DECISION RULE (written BEFORE running; NOT loosened after seeing results):
  CONTEXT_INVARIANCE_SUFFICIENT_ZEROSHOT: ARM_ORACLE_INVARIANT recall_held >= ORACLE_MIN=0.50 on ALL
    3 seeds AND (ARM_ORACLE_INVARIANT recall_held - ARM_JITTERED recall_held) >= JITTER_MARGIN=0.30 on
    ALL 3 seeds AND ARM_CONTEXTVARYING recall_held <= FAIL_MAX on ALL 3 seeds AND ARM_JITTERED
    recall_held <= FAIL_MAX on ALL 3 seeds. => a stable+distinct role address is sufficient for TRUE
    zero-shot novel-role binding; the encoder-training target (context-invariance) is proven-sufficient.
  INSUFFICIENT_ZEROSHOT: both can-fail floors hold (ARM_CONTEXTVARYING fails, ARM_JITTERED fails --
    test is VALID), but ARM_ORACLE_INVARIANT does NOT clear ORACLE_MIN and/or JITTER_MARGIN on some
    seed => a stable address alone does NOT give zero-shot novel-role binding; something more is
    required (re-scope encoder expectations) -- learned cheaply, before the encoder bet.
  INVALID: ARM_CONTEXTVARYING does NOT fail (test vacuous) OR ARM_JITTERED does NOT fail (a
    distinct-but-unstable address also "works", so the metric can't discriminate stability).

FAIL_MAX = CHANCE_RECALL(0.05) + NEAR_CHANCE_MARGIN(0.10) = 0.15.

Run:  .venv/Scripts/python.exe experiments/exp_oracle_context_invariant_address_wm_v2.py --self-test
      .venv/Scripts/python.exe experiments/exp_oracle_context_invariant_address_wm_v2.py --full

ASCII-only. No emojis. Deterministic seeding (torch.Generator + np.random.default_rng; no hash(), no
list(set())). CPU (local, push-free; this .venv has no CUDA). progress_logging: print_flush_true.
Compute architecture: sequential-CPU, justified -- 4 arms x 3 seeds = 12 tiny WM-training units
(K_SLOTS=15, D_MEM=64), each a few hundred gradient steps over a small cached-rep batch; total wall
time is a design target of <8 minutes (compute-proportionality: this is a cheap oracle GATE question,
not a magnitude-fit).
"""

import argparse
import hashlib
import json
import math
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
import exp_selective_overwrite_recall_nl_calib_v1 as calib  # noqa: E402
import exp_selective_overwrite_recall_nl_wm_roleseparated_v1 as base  # noqa: E402
import exp_selective_overwrite_recall_nl_wm_readcond_v1 as rc  # noqa: E402
import exp_wm_addressing_heldout_role_warmstart_v1 as ho  # noqa: E402  -- fires base.S_TARGET=15 patch

ANCHOR_NAME = "oracle_context_invariant_address_wm_v2"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO_ROOT, "tools"))
import exp_checkpoint as ckpt  # noqa: E402  -- per-unit checkpoint/resume (MANDATORY, CLAUDE.md)
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", "exp_" + ANCHOR_NAME)
V2_CKPT = base.V2_CKPT

# ---- reused constants (single source of truth: ho / rc / calib) ----
S_TARGET_TOTAL = ho.S_TARGET_TOTAL          # 15 (MEASURED@ho: widened target-role inventory)
K_SLOTS = S_TARGET_TOTAL
D_MEM = rc.D_MEM                            # 64
HIDDEN = rc.HIDDEN                          # 64
ADDR_TEMP = rc.ADDR_TEMP                    # 0.3
V_FILL = ho.V_FILL                          # 20 -> CHANCE_RECALL = 0.05
CHANCE_RECALL = ho.CHANCE_RECALL
QUERY_TEMPLATE = ho.QUERY_TEMPLATE
SLOT_NOUNS = ho.SLOT_NOUNS
EVENT_TEMPLATES = ho.EVENT_TEMPLATES
COLORS = ho.COLORS
WRITES_MIN, WRITES_MAX = ho.WRITES_MIN, ho.WRITES_MAX
N_DISTRACT_EVENTS = ho.N_DISTRACT_EVENTS
N_DISTRACT_SLOTS_LOCAL = ho.N_DISTRACT_SLOTS_LOCAL
TAIL_MIN = ho.TAIL_MIN
TARGET_TAIL_MIN = ho.TARGET_TAIL_MIN

# ---- v2's OWN disjoint role split (independent of ho's 3-held-out split; flaw-3 fix: 5 held-out) ----
ROLE_SPLIT_SEED_V2 = 20260731
N_HELDOUT_V2 = 5
_role_rng_v2 = np.random.default_rng(ROLE_SPLIT_SEED_V2)
_perm_v2 = _role_rng_v2.permutation(S_TARGET_TOTAL).tolist()
HELD_OUT_ROLES_V2 = sorted(int(x) for x in _perm_v2[:N_HELDOUT_V2])
TRAIN_ROLES_V2 = sorted(int(x) for x in _perm_v2[N_HELDOUT_V2:])
HELD_OUT_SET_V2 = set(HELD_OUT_ROLES_V2)
TRAIN_SET_V2 = set(TRAIN_ROLES_V2)
assert HELD_OUT_SET_V2.isdisjoint(TRAIN_SET_V2), "SPLIT_IDENTITY_BREACH: train/held-out roles overlap"
assert len(HELD_OUT_ROLES_V2) + len(TRAIN_ROLES_V2) == S_TARGET_TOTAL
assert len(HELD_OUT_ROLES_V2) == N_HELDOUT_V2

ALL_ROLES = list(range(S_TARGET_TOTAL))

# ---- run params (compute-proportionality: cheap oracle GATE, not a magnitude-fit; <8min target) ----
FULL_TRAIN, FULL_EVAL = 300, 220
STEPS_WM = 200
BATCH = 128
LR = 1e-2
EARLY_STOP_LOSS = 0.05
SEEDS_FULL = (7, 13, 19)
ORACLE_PROBE_SEED = 20260730                # fixed probe role-query seed (independent of training seed)
JITTER_SEED_OFFSET = 3141593                # fixed offset for the per-(mode=jittered, seed) generator

# ---- pre-registered bands (this file, written BEFORE running; NOT loosened) ----
NEAR_CHANCE_MARGIN = 0.10
FAIL_MAX = CHANCE_RECALL + NEAR_CHANCE_MARGIN         # THEORETICAL: 0.05 + 0.10 = 0.15
ORACLE_MIN = 0.50
JITTER_MARGIN = 0.30

ARMS = ("context", "oracle", "jittered", "onehot")


def _log(msg):
    print("[%s] %s" % (ANCHOR_NAME, msg), flush=True)


def _now_iso():
    return datetime.now(timezone.utc).isoformat()


# ---------------- canonical hardening ----------------
def _write_start_marker(output_dir, run_mode, expected_n_units):
    marker = {"pid": os.getpid(), "ts_iso": _now_iso(), "anchor_name": ANCHOR_NAME,
              "run_mode": run_mode, "expected_n_units": expected_n_units, "host": platform.node()}
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
    safe_metrics = _jsonify(metrics)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(safe_metrics, f, indent=2)
    os.replace(tmp, os.path.join(output_dir, "metrics.json"))


def _digest_tensor(t):
    return hashlib.sha256(t.detach().cpu().numpy().tobytes()).hexdigest()


# ---------------- FLAW-1 FIX: zero-shot dataset generator (role-pool-restricted) ----------------
def gen_stream_zeroshot(rng, role_pool):
    """Forks ho.gen_stream_expanded, parameterized by role_pool: ONLY roles in role_pool get target
    WRITES, and consequently the QUERY (drawn from `eligible`, itself derived only from role_pool's
    last-write bookkeeping) can ONLY be a role_pool role. Distractor events (ids >= S_TARGET_TOTAL)
    are unchanged (never supervised in any arm/mode). Calling this with role_pool=TRAIN_ROLES_V2 for
    training makes held-out roles LITERALLY ABSENT from the corpus -- not merely unsupervised -- which
    is the enforcement mechanism for TRUE ZERO-SHOT (flaw 1, Director spawn 2026-07-30)."""
    slot_vocab = S_TARGET_TOTAL + N_DISTRACT_SLOTS_LOCAL
    slot_seq = []
    for s in role_pool:
        k = int(rng.integers(WRITES_MIN, WRITES_MAX + 1))
        slot_seq.extend([s] * k)
    for _ in range(N_DISTRACT_EVENTS):
        slot_seq.append(int(rng.integers(S_TARGET_TOTAL, slot_vocab)))
    slot_seq = np.array(slot_seq, dtype=np.int64)
    slot_seq = slot_seq[rng.permutation(len(slot_seq))]
    L = len(slot_seq)

    reps = L // V_FILL
    rem = L - reps * V_FILL
    fill_pool = np.concatenate([
        np.repeat(np.arange(V_FILL), reps),
        rng.permutation(V_FILL)[:rem] if rem else np.array([], dtype=np.int64),
    ]).astype(np.int64)
    fill_pool = fill_pool[rng.permutation(len(fill_pool))]
    events = [[int(slot_seq[i]), int(fill_pool[i])] for i in range(L)]

    role_pool_set = set(int(x) for x in role_pool)
    last_write = {s: -1 for s in role_pool}
    for idx, (sl, _fl) in enumerate(events):
        if sl in role_pool_set:
            last_write[sl] = idx
    is_target = np.array([1 if e[0] in role_pool_set else 0 for e in events])
    cum_target_after = np.concatenate([np.cumsum(is_target[::-1])[::-1][1:], [0]])
    eligible = [s for s in role_pool
                if last_write[s] >= 0
                and (L - 1 - last_write[s]) >= TAIL_MIN
                and int(cum_target_after[last_write[s]]) >= TARGET_TAIL_MIN]
    if not eligible:
        return None

    query = int(eligible[rng.integers(0, len(eligible))])
    answer = int(events[last_write[query]][1])
    slots = np.array([e[0] for e in events], dtype=np.int64)
    fills = np.array([e[1] for e in events], dtype=np.int64)
    return {"slots": slots, "fills": fills, "query": query, "answer": answer,
            "last_write_idx": int(last_write[query])}


def gen_dataset_zeroshot(n, rng, role_pool):
    out = []
    while len(out) < n:
        ex = gen_stream_zeroshot(rng, role_pool)
        if ex is not None:
            ex["text"] = calib.render_text(ex, rng)
            out.append(ex)
    return out


def build_index_batch_ext_v2(examples, enc, seed):
    """v2's OWN batch builder: uses TRAIN_SET_V2/HELD_OUT_SET_V2 (this cell's split), NOT ho's."""
    b = base.build_index_batch(examples, enc, seed)
    B, Lmax = b["ev_idx"].shape
    ev_slot = np.full((B, Lmax), -1, dtype=np.int64)
    q_slot = np.zeros((B,), dtype=np.int64)
    q_is_train = np.zeros((B,), dtype=bool)
    q_is_heldout = np.zeros((B,), dtype=bool)
    for i, ex in enumerate(examples):
        for t, sl in enumerate(ex["slots"]):
            s = int(sl)
            if s < S_TARGET_TOTAL:
                ev_slot[i, t] = s
        q = int(ex["query"])
        q_slot[i] = q
        q_is_train[i] = q in TRAIN_SET_V2
        q_is_heldout[i] = q in HELD_OUT_SET_V2
    b["ev_slot"] = torch.from_numpy(ev_slot)
    b["q_slot"] = torch.from_numpy(q_slot)
    b["q_is_train"] = torch.from_numpy(q_is_train)
    b["q_is_heldout"] = torch.from_numpy(q_is_heldout)
    return b


def zeroshot_construction_selftest(seed=7, n=300):
    """Directly MEASURES the zero-shot enforcement (flaw 1): the training corpus must contain ZERO
    held-out-role queries AND ZERO held-out-role events."""
    rng = np.random.default_rng(seed)
    ds = gen_dataset_zeroshot(n, rng, TRAIN_ROLES_V2)
    n_heldout_query = sum(1 for ex in ds if int(ex["query"]) in HELD_OUT_SET_V2)
    n_heldout_event = sum(1 for ex in ds for sl in ex["slots"] if int(sl) in HELD_OUT_SET_V2)
    kl = calib.oracle_acc(ds, calib.oracle_keep_last)
    fails = []
    if n_heldout_query != 0:
        fails.append("held-out role appeared as a TRAINING query %d times" % n_heldout_query)
    if n_heldout_event != 0:
        fails.append("held-out role appeared as a TRAINING event %d times" % n_heldout_event)
    if kl < 0.999:
        fails.append("oracle_keep_last=%.4f != 1.0 on zero-shot training corpus" % kl)
    assert not fails, "ZEROSHOT_CONSTRUCTION_SELFTEST_FAIL: %s" % fails
    return {"n_examples": n, "n_heldout_query": n_heldout_query, "n_heldout_event": n_heldout_event,
            "oracle_keep_last": float(kl), "train_roles": TRAIN_ROLES_V2,
            "held_out_roles": HELD_OUT_ROLES_V2}


# ---------------- oracle table construction (fixed, never-trained probe role-query) ----------------
def build_role_query_probe(seed, d_enc):
    g = torch.Generator().manual_seed(seed + 424242)
    rq = torch.empty(d_enc)
    rq.normal_(0.0, 0.02, generator=g)
    return rq


def _extract_slot_rep_single(rq_row, U_tok, U_pad, d_enc):
    """Single-role-query attention pooling over ALL cached sentences (mirrors ReadCondWM._role_reps
    but for one fixed query row instead of the 2-row trainable role_query)."""
    scores = torch.einsum("nld,d->nl", U_tok, rq_row) / math.sqrt(d_enc)
    scores = scores.masked_fill(U_pad, float("-inf"))
    attn = torch.softmax(scores, dim=-1)
    return torch.einsum("nl,nld->nd", attn, U_tok)


def _role_context_idxs(s):
    idxs = [QUERY_TEMPLATE.format(slot=SLOT_NOUNS[s])]
    for tm in EVENT_TEMPLATES:
        for fl in COLORS:
            idxs.append(tm.format(slot=SLOT_NOUNS[s], fill=fl))
    return idxs


def build_oracle_table(enc, Uc, seed):
    """Averages the FIXED probe's role-query-extracted rep across ALL of a role's contexts, for ALL
    15 roles (train AND held-out -- legitimate here: upper-bound oracle probe of context-invariance,
    not a deployable method). Returns ([15, d_enc] table, all_reps [Nu,d], per-role context idx lists,
    per-role context counts)."""
    rq_row = build_role_query_probe(seed, enc.d)
    all_reps = _extract_slot_rep_single(rq_row, Uc, enc.U_pad_t, enc.d)     # [Nu, d]
    table = torch.zeros(S_TARGET_TOTAL, enc.d)
    n_ctx = []
    idx_lists = []
    for s in range(S_TARGET_TOTAL):
        idxs = [enc.idx_of(txt) for txt in _role_context_idxs(s)]
        idx_t = torch.tensor(idxs)
        table[s] = all_reps[idx_t].mean(dim=0)
        n_ctx.append(len(idxs))
        idx_lists.append(idx_t)
    return table, all_reps, idx_lists, n_ctx


def build_onehot_table(d_enc, k, seed):
    """Ceiling reference: k orthonormal directions in R^d_enc (QR of a random matrix) -- a clean,
    maximally-separated, STABLE address per role, establishing the WM's best case given PERFECT
    addressing."""
    g = torch.Generator().manual_seed(seed + 987654)
    M = torch.randn(d_enc, d_enc, generator=g)
    Q, _ = torch.linalg.qr(M)
    return Q[:, :k].t().contiguous()          # [k, d_enc], orthonormal rows


def compute_context_var_scale(table, all_reps, idx_lists):
    """FLAW-2 FIX: measures how much the REAL context-varying rep moves around its role's oracle mean,
    across ALL 15 roles' cached contexts -- the principled magnitude used to scale ARM_JITTERED's
    per-occurrence noise, so the floor's instability matches the REAL instability already shown to
    defeat addressing (ARM_CONTEXTVARYING), not an arbitrary knob."""
    devs = []
    for s in range(S_TARGET_TOTAL):
        reps_s = all_reps[idx_lists[s]]
        dev = (reps_s - table[s]).norm(dim=1)
        devs.append(dev)
    all_devs = torch.cat(devs)
    return float(all_devs.mean())


def build_all_tables(enc, Uc):
    table, all_reps, idx_lists, n_ctx = build_oracle_table(enc, Uc, ORACLE_PROBE_SEED)
    onehot = build_onehot_table(enc.d, S_TARGET_TOTAL, ORACLE_PROBE_SEED)
    mean_norm = float(table.norm(dim=1).mean())
    onehot = onehot * mean_norm      # scale onehot rows to oracle table's mean row norm (temp-scale sanity)
    jitter_std = compute_context_var_scale(table, all_reps, idx_lists)
    return {"context": None, "oracle": table, "onehot": onehot}, \
        {"n_ctx_per_role": n_ctx, "onehot_mean_norm_scale": mean_norm, "jitter_std_measured": jitter_std}


# ---------------- ONE-VARIABLE WM forward: address input differs by arm, everything else identical --
def read_features_arm(wm, batch, mode, oracle_table, jitter_std=None, jitter_gen=None):
    """mode in ARMS. The address key-lookup input for TARGET-role tokens/queries is the ONE variable;
    the filler-VALUE extraction path (ev_fill) and the write-gate's input (flat_gate_in, always the
    real context rep) are IDENTICAL across every mode. Distractor-role tokens (ev_slot == -1) always
    keep the natural context address input, in every mode -- distractor-suppression learning is not a
    confound between arms. mode=='jittered' draws FRESH noise from jitter_gen on every call (the
    generator's state advances call-to-call), so even the identical (role, sentence) pair gets a
    DIFFERENT address vector every time it is read -- the genuine can-fail floor for stability."""
    slot_u, fill_u = wm._role_reps()                        # [Nu, d] (WM's own trainable role_query)
    ev_idx = batch["ev_idx"]; active = batch["active"]; q_idx = batch["q_idx"]
    ev_slot = batch["ev_slot"]; q_slot = batch["q_slot"]
    B, Lmax = ev_idx.shape
    ev_slot_ctx = slot_u[ev_idx]                             # [B,Lmax,d] context rep (gate input, always)
    ev_fill = fill_u[ev_idx]                                 # UNCHANGED filler path in every arm
    if mode == "context":
        ev_addr_in = ev_slot_ctx
        q_addr_in = slot_u[q_idx]
    elif mode == "jittered":
        is_target = (ev_slot >= 0).unsqueeze(-1)
        base_ev = oracle_table[ev_slot.clamp(min=0)]
        noise_ev = torch.randn(base_ev.shape, generator=jitter_gen) * jitter_std
        ev_addr_in = torch.where(is_target, base_ev + noise_ev, ev_slot_ctx)
        base_q = oracle_table[q_slot]
        noise_q = torch.randn(base_q.shape, generator=jitter_gen) * jitter_std
        q_addr_in = base_q + noise_q
    else:
        is_target = (ev_slot >= 0).unsqueeze(-1)
        oracle_rows = oracle_table[ev_slot.clamp(min=0)]
        ev_addr_in = torch.where(is_target, oracle_rows, ev_slot_ctx)
        q_addr_in = oracle_table[q_slot]
    flat_addr = ev_addr_in.reshape(B * Lmax, wm.d_enc)
    flat_gate_in = ev_slot_ctx.reshape(B * Lmax, wm.d_enc)   # gate ALWAYS sees the real context rep
    ev_logits = wm._addr_logits(flat_addr).reshape(B, Lmax, wm.k_slots)
    addr = torch.softmax(ev_logits, dim=-1)
    wgate = torch.sigmoid(wm.write_gate(flat_gate_in)).reshape(B, Lmax)
    cand = wm.value_proj(ev_fill.reshape(B * Lmax, wm.d_enc)).reshape(B, Lmax, wm.d_mem)
    h = torch.zeros(B, wm.k_slots, wm.d_mem)
    for t in range(Lmax):
        w = (addr[:, t] * (wgate[:, t] * active[:, t]).unsqueeze(-1)).unsqueeze(-1)
        h = (1.0 - w) * h + w * cand[:, t].unsqueeze(1)
    q_logits = wm._addr_logits(q_addr_in)
    addr_q = torch.softmax(q_logits, dim=-1)
    h_read = (addr_q.unsqueeze(-1) * h).sum(dim=1)
    return h_read, ev_logits, q_logits


def _eval_acc(logits, answer):
    return float((logits.argmax(dim=-1) == answer).float().mean().item())


def build_wm(seed, enc, Uc):
    return rc.ReadCondWM(seed, enc.d, D_MEM, K_SLOTS, HIDDEN, V_FILL, ADDR_TEMP, Uc, enc.U_pad_t)


def train_oracle_arm(wm, tr_batch, ev_batch, mode, oracle_table, steps, lr, seed, log_tag, jitter_std=None):
    torch.manual_seed(seed)
    g = torch.Generator().manual_seed(seed + 555)
    jitter_gen = torch.Generator().manual_seed(seed + JITTER_SEED_OFFSET) if mode == "jittered" else None
    opt = torch.optim.Adam(wm.parameters(), lr=lr)
    N = tr_batch["answer"].shape[0]
    loss_curve = []
    ema = None
    step = 0
    for step in range(steps):
        opt.zero_grad()
        if BATCH < N:
            idx = torch.randint(0, N, (BATCH,), generator=g)
            mb = {k: v[idx] for k, v in tr_batch.items()}
        else:
            mb = tr_batch
        h_read, _, _ = read_features_arm(wm, mb, mode, oracle_table, jitter_std, jitter_gen)
        logits = wm.readout(h_read)
        loss = F.cross_entropy(logits, mb["answer"])
        loss.backward()
        opt.step()
        lv = float(loss.item())
        ema = lv if ema is None else 0.9 * ema + 0.1 * lv
        if step == 0 or (step + 1) % max(1, steps // 6) == 0:
            loss_curve.append((step, lv))
            _log("    [%s seed=%d] step=%d loss=%.4f ema=%.4f" % (log_tag, seed, step + 1, lv, ema))
        if step >= 100 and ema is not None and ema < EARLY_STOP_LOSS:
            break
    wm.eval()
    with torch.no_grad():
        ev_h, _, _ = read_features_arm(wm, ev_batch, mode, oracle_table, jitter_std, jitter_gen)
        ev_pred = wm.readout(ev_h)
        eval_acc = _eval_acc(ev_pred, ev_batch["answer"])
        recall_correct = (ev_pred.argmax(-1) == ev_batch["answer"]).float()
        tm, hm = ev_batch["q_is_train"], ev_batch["q_is_heldout"]
        recall_train_acc = float(recall_correct[tm].mean()) if tm.any() else float("nan")
        recall_held_acc = float(recall_correct[hm].mean()) if hm.any() else float("nan")
        tr_h, _, _ = read_features_arm(wm, tr_batch, mode, oracle_table, jitter_std, jitter_gen)
        tr_pred = wm.readout(tr_h)
        tr_acc = _eval_acc(tr_pred, tr_batch["answer"])
    wm.train()
    first_loss = loss_curve[0][1] if loss_curve else float("nan")
    last_loss = loss_curve[-1][1] if loss_curve else float("nan")
    _log("  [%s seed=%d] eval_acc=%.4f train_acc=%.4f recall_train=%.4f recall_held=%.4f "
         "loss %.3f->%.3f steps=%d"
         % (log_tag, seed, eval_acc, tr_acc, recall_train_acc, recall_held_acc, first_loss, last_loss,
            step + 1))
    return dict(eval_acc=eval_acc, train_acc=tr_acc, recall_train_acc=recall_train_acc,
                recall_heldout_acc=recall_held_acc, ev_logits=ev_pred.detach(),
                loss_curve=loss_curve, steps_run=step + 1, first_loss=first_loss, last_loss=last_loss)


def _strip_for_checkpoint(res):
    out = dict(res)
    t = out.pop("ev_logits")
    out["ev_logits_sha256"] = _digest_tensor(t)
    return out


# ---------------- self-test: oracle-averaging construction (context-invariant by construction) ------
def role_invariance_construction_selftest(enc, Uc, oracle_table):
    """Directly proves the load-bearing construction claim: in mode='oracle', the address key-lookup
    input for a TARGET-role token depends ONLY on its ev_slot id, NOT on which sentence (ev_idx)
    produced it -- i.e. context-invariant by construction. In mode='context' the same change in ev_idx
    (different underlying sentence, same claimed role) DOES change the address input."""
    wm = rc.ReadCondWM(7, enc.d, D_MEM, K_SLOTS, HIDDEN, V_FILL, ADDR_TEMP, Uc, enc.U_pad_t)
    s = 0
    idx_a = enc.idx_of(QUERY_TEMPLATE.format(slot=SLOT_NOUNS[s]))
    idx_b = enc.idx_of(EVENT_TEMPLATES[0].format(slot=SLOT_NOUNS[s], fill=COLORS[0]))
    assert idx_a != idx_b, "self-test picked identical sentence indices (construction bug)"
    ev_idx_a = torch.tensor([[idx_a]])
    ev_idx_b = torch.tensor([[idx_b]])
    ev_slot = torch.tensor([[s]])              # SAME claimed role in both batches
    q_idx = torch.tensor([idx_a])
    q_slot = torch.tensor([s])
    active = torch.ones(1, 1)
    batch_a = {"ev_idx": ev_idx_a, "ev_slot": ev_slot, "q_idx": q_idx, "q_slot": q_slot, "active": active}
    batch_b = {"ev_idx": ev_idx_b, "ev_slot": ev_slot, "q_idx": q_idx, "q_slot": q_slot, "active": active}
    with torch.no_grad():
        _, ev_logits_ctx_a, _ = read_features_arm(wm, batch_a, "context", oracle_table)
        _, ev_logits_ctx_b, _ = read_features_arm(wm, batch_b, "context", oracle_table)
        _, ev_logits_orc_a, _ = read_features_arm(wm, batch_a, "oracle", oracle_table)
        _, ev_logits_orc_b, _ = read_features_arm(wm, batch_b, "oracle", oracle_table)
    context_varies = not torch.allclose(ev_logits_ctx_a, ev_logits_ctx_b, atol=1e-6)
    oracle_invariant = torch.allclose(ev_logits_orc_a, ev_logits_orc_b, atol=1e-6)
    assert context_varies, ("SELF-TEST SETUP BUG: the two contexts for role %d produced identical "
                             "context-mode address logits -- the invariance check would be vacuous" % s)
    assert oracle_invariant, ("ORACLE MODE IS NOT CONTEXT-INVARIANT: same role, different sentence "
                              "(ev_idx %d vs %d) produced different address logits" % (idx_a, idx_b))
    return {"context_varies_across_sentences": bool(context_varies),
            "oracle_invariant_across_sentences": bool(oracle_invariant)}


def jitter_instability_selftest(enc, Uc, oracle_table, jitter_std):
    """FLAW-2 FIX proof: two successive ARM_JITTERED reads of the IDENTICAL (role, sentence) produce
    DIFFERENT address logits (fresh per-occurrence noise -- the genuine instability), while two
    successive ARM_ORACLE_INVARIANT reads of the same input are bit-identical (sanity: oracle mode
    never touches the jitter generator)."""
    wm = rc.ReadCondWM(7, enc.d, D_MEM, K_SLOTS, HIDDEN, V_FILL, ADDR_TEMP, Uc, enc.U_pad_t)
    s = 0
    idx_a = enc.idx_of(QUERY_TEMPLATE.format(slot=SLOT_NOUNS[s]))
    ev_idx = torch.tensor([[idx_a]])
    ev_slot = torch.tensor([[s]])
    q_idx = torch.tensor([idx_a])
    q_slot = torch.tensor([s])
    active = torch.ones(1, 1)
    batch = {"ev_idx": ev_idx, "ev_slot": ev_slot, "q_idx": q_idx, "q_slot": q_slot, "active": active}
    gen = torch.Generator().manual_seed(999001)
    with torch.no_grad():
        _, ev_logits_j1, _ = read_features_arm(wm, batch, "jittered", oracle_table, jitter_std, gen)
        _, ev_logits_j2, _ = read_features_arm(wm, batch, "jittered", oracle_table, jitter_std, gen)
        _, ev_logits_o1, _ = read_features_arm(wm, batch, "oracle", oracle_table)
        _, ev_logits_o2, _ = read_features_arm(wm, batch, "oracle", oracle_table)
    jitter_varies = not torch.allclose(ev_logits_j1, ev_logits_j2, atol=1e-6)
    oracle_stable = torch.allclose(ev_logits_o1, ev_logits_o2, atol=1e-6)
    assert jitter_varies, ("ARM_JITTERED SELF-TEST FAILURE: same role/sentence produced identical "
                            "address logits across two draws -- jitter is not actually unstable")
    assert oracle_stable, "ARM_ORACLE_INVARIANT regressed: repeated calls produced different logits"
    return {"jitter_varies_across_occurrences": bool(jitter_varies),
            "oracle_stable_across_calls": bool(oracle_stable), "jitter_std_used": float(jitter_std)}


# ---------------- self-test: serialization + checkpoint/resume (same pattern as v1) ----------------
def serialization_selftest():
    fake = {"arms": {"oracle": {"recall_heldout_acc": np.float64(0.6)},
                     "loss_curve": [(0, torch.tensor(1.0)), (10, 0.2)]}}
    safe = _jsonify(fake)
    dumped = json.dumps(safe)
    reloaded = json.loads(dumped)
    assert isinstance(reloaded["arms"]["oracle"]["recall_heldout_acc"], float)
    fake_train_res = dict(eval_acc=0.5, train_acc=0.6, recall_train_acc=0.5, recall_heldout_acc=0.4,
                           ev_logits=torch.randn(4, K_SLOTS), loss_curve=[(0, 1.0)],
                           steps_run=11, first_loss=1.0, last_loss=0.5)
    stripped = _strip_for_checkpoint(fake_train_res)
    assert "ev_logits" not in stripped
    json.dumps(stripped)
    return {"jsonify_roundtrip_ok": True, "strip_for_checkpoint_ok": True}


def checkpoint_resume_selftest():
    import shutil
    import tempfile
    tmp_dir = tempfile.mkdtemp(prefix="oracle_addr_v2_ckpt_selftest_")
    try:
        unit_specs = [("context", 7), ("oracle", 7), ("jittered", 7), ("onehot", 7)]

        def _compute(kind, seed):
            g = torch.Generator().manual_seed((abs(sum(ord(c) for c in kind)) % 100000) + seed)
            return {"kind": kind, "seed": seed, "acc": float(torch.rand(1, generator=g).item()),
                    "ev_logits_sha256": _digest_tensor(torch.rand(3, 3, generator=g))}

        d_single = os.path.join(tmp_dir, "single")
        for kind, seed in unit_specs:
            k = ckpt.unit_key(kind, seed)
            res = _compute(kind, seed)
            json.dumps(res)
            ckpt.record_unit(d_single, k, res)
        single_final = ckpt.load_units(d_single)
        assert len(single_final) == 4

        d_resume = os.path.join(tmp_dir, "resume")
        for kind, seed in unit_specs[:2]:
            ckpt.record_unit(d_resume, ckpt.unit_key(kind, seed), _compute(kind, seed))
        done = ckpt.completed_units(d_resume)
        assert done == {ckpt.unit_key(k, s) for k, s in unit_specs[:2]}
        n_skipped = 0
        for kind, seed in unit_specs:
            k = ckpt.unit_key(kind, seed)
            if k in done:
                n_skipped += 1
                continue
            ckpt.record_unit(d_resume, k, _compute(kind, seed))
        assert n_skipped == 2
        resumed_final = ckpt.load_units(d_resume)
        assert json.dumps(resumed_final, sort_keys=True) == json.dumps(single_final, sort_keys=True)
        return {"resume_skip_count": n_skipped, "bit_identical_resume": True}
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


# ---------------- self-test ----------------
def run_self_test():
    _log("SELF-TEST: serialization safety ...")
    ser_diag = serialization_selftest()
    _log("  PASS: %s" % ser_diag)

    _log("SELF-TEST: checkpoint/resume wiring ...")
    ckpt_diag = checkpoint_resume_selftest()
    _log("  PASS: %s" % ckpt_diag)

    _log("SELF-TEST: zero-shot corpus construction (flaw 1: held-out roles ABSENT from training) ...")
    zs_diag = zeroshot_construction_selftest()
    _log("  PASS: %s" % zs_diag)

    _log("SELF-TEST: load REAL v2 encoder (widened closed sentence set via ho's monkeypatch) ...")
    assert os.path.exists(V2_CKPT), "v2 checkpoint missing: %s" % V2_CKPT
    enc = base.FrozenV2Encoder(V2_CKPT)
    n_cached = enc.build_cache()
    assert n_cached >= 3000, "closed sentence set smaller than expected (widened query set missing?)"
    cond = rc.Conditioner(enc.U_tok_t, enc.U_pad_t)
    Uc = cond.apply(enc.U_tok_t, enc.U_pad_t, "pca_whiten")

    _log("SELF-TEST: build oracle/onehot tables + measure jitter_std from the REAL encoder ...")
    tables, table_diag = build_all_tables(enc, Uc)
    _log("  n_ctx_per_role=%s (min=%d max=%d) mean_row_norm(oracle)=%.4f jitter_std=%.4f"
         % (table_diag["n_ctx_per_role"][:3] + ["..."], min(table_diag["n_ctx_per_role"]),
            max(table_diag["n_ctx_per_role"]), float(tables["oracle"].norm(dim=1).mean()),
            table_diag["jitter_std_measured"]))
    assert tables["oracle"].shape == (S_TARGET_TOTAL, enc.d)
    assert tables["onehot"].shape == tables["oracle"].shape
    assert table_diag["jitter_std_measured"] > 0.0

    _log("SELF-TEST: role invariance-by-construction (context varies, oracle does not) ...")
    inv_diag = role_invariance_construction_selftest(enc, Uc, tables["oracle"])
    _log("  PASS: %s" % inv_diag)

    _log("SELF-TEST: jitter instability-by-construction (flaw 2: jittered varies, oracle stable) ...")
    jit_diag = jitter_instability_selftest(enc, Uc, tables["oracle"], table_diag["jitter_std_measured"])
    _log("  PASS: %s" % jit_diag)

    _log("SELF-TEST: tiny end-to-end all 4 arms (arms-must-differ, ranges valid) ...")
    tr = gen_dataset_zeroshot(150, np.random.default_rng(7), TRAIN_ROLES_V2)
    ev = gen_dataset_zeroshot(150, np.random.default_rng(7 + 777), ALL_ROLES)
    tr_b = build_index_batch_ext_v2(tr, enc, 7)
    ev_b = build_index_batch_ext_v2(ev, enc, 7 + 777)
    assert ev_b["q_is_heldout"].sum().item() > 0, "tiny eval set drew no held-out-role queries"
    assert tr_b["q_is_heldout"].sum().item() == 0, "tiny TRAIN set drew a held-out-role query (leak)"
    tiny_results = {}
    for mode in ARMS:
        wm = build_wm(7, enc, Uc)
        jstd = table_diag["jitter_std_measured"] if mode == "jittered" else None
        table_arg = tables["oracle"] if mode == "jittered" else tables[mode]
        res = train_oracle_arm(wm, tr_b, ev_b, mode, table_arg, steps=40, lr=LR, seed=7,
                                log_tag="TINY_%s" % mode, jitter_std=jstd)
        tiny_results[mode] = res
        assert 0.0 <= res["eval_acc"] <= 1.0
        assert 0.0 <= res["recall_heldout_acc"] <= 1.0 or math.isnan(res["recall_heldout_acc"])
    digests = {m: _digest_tensor(r["ev_logits"]) for m, r in tiny_results.items()}
    pairs = [(a, b) for a in digests for b in digests if a < b]
    for a, b in pairs:
        assert digests[a] != digests[b], (
            "META_RULE_AF VIOLATION: arms %r and %r bit-identical" % (a, b))
    _log("SELF-TEST PASS")
    return {"serialization_selftest": ser_diag, "checkpoint_resume_selftest": ckpt_diag,
            "zeroshot_construction_selftest": zs_diag, "n_cached": n_cached, "table_diag": table_diag,
            "invariance_diag": inv_diag, "jitter_instability_diag": jit_diag,
            "tiny": {m: {"eval_acc": r["eval_acc"], "recall_train": r["recall_train_acc"],
                         "recall_held": r["recall_heldout_acc"]} for m, r in tiny_results.items()},
            "arms_differ_verified": True}


# ---------------- verdict ----------------
def decide_verdict(arm_results):
    """arm_results: {mode: [per-seed dict, ...]} for mode in ARMS."""
    ctx_held = [r["recall_heldout_acc"] for r in arm_results["context"]]
    orc_held = [r["recall_heldout_acc"] for r in arm_results["oracle"]]
    jit_held = [r["recall_heldout_acc"] for r in arm_results["jittered"]]
    onh_held = [r["recall_heldout_acc"] for r in arm_results["onehot"]]

    ctx_fails = all(h <= FAIL_MAX for h in ctx_held)
    jit_fails = all(h <= FAIL_MAX for h in jit_held)
    gaps_vs_jittered = [o - j for o, j in zip(orc_held, jit_held)]

    if not ctx_fails:
        verdict = "INVALID"
        msg = ("ARM_CONTEXTVARYING (floor A) did not reproduce near-chance held-out recall "
               "(fail_max=%.3f): held=%s -- the prior HARD-FAIL did not reproduce at this zero-shot "
               "scale/schedule; the test is vacuous as run. Do not interpret ORACLE arm against this "
               "control." % (FAIL_MAX, [round(h, 3) for h in ctx_held]))
    elif not jit_fails:
        verdict = "INVALID"
        msg = ("ARM_JITTERED (floor B) did not fail (fail_max=%.3f): held=%s -- a distinct-but-UNSTABLE "
               "address also produces non-trivial recall, so the metric cannot discriminate stability "
               "from mere role-distinctness. Any ORACLE win is untrustworthy until this is fixed "
               "(e.g. larger jitter_std, more seeds)." % (FAIL_MAX, [round(h, 3) for h in jit_held]))
    else:
        oracle_clears_min = all(h >= ORACLE_MIN for h in orc_held)
        oracle_clears_jitter = all(g >= JITTER_MARGIN for g in gaps_vs_jittered)
        if oracle_clears_min and oracle_clears_jitter:
            verdict = "CONTEXT_INVARIANCE_SUFFICIENT_ZEROSHOT"
            msg = ("Context-invariance IS the sufficient missing property for TRUE zero-shot novel-role "
                   "binding: ARM_ORACLE_INVARIANT held-out recall=%s (>= %.2f all seeds) clears "
                   "ARM_JITTERED (%s) by >= %.2f (gaps=%s), while ARM_CONTEXTVARYING (%s) and "
                   "ARM_JITTERED (%s) both stayed <= %.3f. Held-out roles were LITERALLY ABSENT from "
                   "training (zeroshot_construction_selftest measured n_heldout_query=0, "
                   "n_heldout_event=0). The proven WM generalizes its addressing to a role it NEVER saw "
                   "in training given ONLY a stable, distinct per-role vector -- NO aux loss, NO "
                   "warm-start probe. The encoder-training target is now exactly defined: make role "
                   "reps context-invariant. ARM_ONEHOT_ORACLE (perfect-address ceiling) held-out "
                   "recall=%s for reference."
                   % ([round(h, 3) for h in orc_held], ORACLE_MIN, [round(h, 3) for h in jit_held],
                      JITTER_MARGIN, [round(g, 3) for g in gaps_vs_jittered],
                      [round(h, 3) for h in ctx_held], [round(h, 3) for h in jit_held], FAIL_MAX,
                      [round(h, 3) for h in onh_held]))
        else:
            verdict = "INSUFFICIENT_ZEROSHOT"
            msg = ("Context-invariance ALONE is NOT sufficient for TRUE zero-shot novel-role binding: "
                   "with both can-fail floors valid (ARM_CONTEXTVARYING held=%s <= %.3f, ARM_JITTERED "
                   "held=%s <= %.3f), ARM_ORACLE_INVARIANT held-out recall=%s did not clear "
                   "ORACLE_MIN=%.2f and/or beat ARM_JITTERED by >= %.2f (gaps=%s) on every seed -- a "
                   "perfectly stable, distinct per-role address (never seen in training) is not enough "
                   "for the proven WM to generalize its addressing via ordinary end-to-end gradient "
                   "descent alone. The residual gap implicates something beyond raw stability -- "
                   "learned cheaply, before the encoder-training bet. ARM_ONEHOT_ORACLE (perfect-address "
                   "ceiling) held-out recall=%s for reference."
                   % ([round(h, 3) for h in ctx_held], FAIL_MAX, [round(h, 3) for h in jit_held],
                      FAIL_MAX, [round(h, 3) for h in orc_held], ORACLE_MIN, JITTER_MARGIN,
                      [round(g, 3) for g in gaps_vs_jittered], [round(h, 3) for h in onh_held]))
    bands = {"chance_recall": CHANCE_RECALL, "fail_max": FAIL_MAX, "oracle_min": ORACLE_MIN,
             "jitter_margin": JITTER_MARGIN, "oracle_ceiling": 1.0,
             "ctx_fails": bool(ctx_fails), "jit_fails": bool(jit_fails),
             "context_held": ctx_held, "oracle_held": orc_held, "jittered_held": jit_held,
             "onehot_held": onh_held, "gaps_oracle_vs_jittered": gaps_vs_jittered}
    return verdict, msg, bands


# ---------------- main ----------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--full", action="store_true")
    ap.add_argument("--train-n", type=int, default=FULL_TRAIN)
    ap.add_argument("--eval-n", type=int, default=FULL_EVAL)
    ap.add_argument("--steps-wm", type=int, default=STEPS_WM)
    args = ap.parse_args()

    torch.set_num_threads(min(6, max(1, os.cpu_count() or 1)))
    run_mode = "self_test" if args.self_test or not args.full else "full"
    expected_units = 1 if run_mode == "self_test" else len(ARMS) * len(SEEDS_FULL)
    _write_start_marker(OUTPUT_DIR, run_mode, expected_units)
    t0 = time.perf_counter()

    if run_mode == "self_test":
        st = run_self_test()
        elapsed = time.perf_counter() - t0
        _atomic_write_metrics(OUTPUT_DIR, {
            "verdict": "SELFTEST_PASS",
            "verdict_msg": "SELFTEST_PASS (serialization + checkpoint/resume + real encoder + "
                           "zero-shot-corpus + oracle/onehot tables + context-invariance-by-"
                           "construction + jitter-instability-by-construction + arms-differ)",
            "summary": "SELFTEST_PASS", "run_mode": "self_test", "elapsed_s": elapsed,
            "ts_iso": _now_iso(), "anchor_name": ANCHOR_NAME, "chance_recall": CHANCE_RECALL,
            "selftest": st})
        _log("DONE self-test in %.1fs" % elapsed)
        return

    steps_wm = args.steps_wm
    _log("FULL: train_n=%d eval_n=%d steps_wm=%d seeds=%s chance_recall=%.4f arms=%s"
         % (args.train_n, args.eval_n, steps_wm, SEEDS_FULL, CHANCE_RECALL, ARMS))
    enc = base.FrozenV2Encoder(V2_CKPT)
    n_cached = enc.build_cache()
    _log("  cached %d unique sentence TOKEN reps (d=%d)" % (n_cached, enc.d))
    cond = rc.Conditioner(enc.U_tok_t, enc.U_pad_t)
    Uc = cond.apply(enc.U_tok_t, enc.U_pad_t, "pca_whiten")

    tables, table_diag = build_all_tables(enc, Uc)
    _log("  oracle table n_ctx_per_role min=%d max=%d; jitter_std_measured=%.4f"
         % (min(table_diag["n_ctx_per_role"]), max(table_diag["n_ctx_per_role"]),
            table_diag["jitter_std_measured"]))

    inv_diag = role_invariance_construction_selftest(enc, Uc, tables["oracle"])
    _log("  construction check (invariance): %s" % inv_diag)
    jit_diag = jitter_instability_selftest(enc, Uc, tables["oracle"], table_diag["jitter_std_measured"])
    _log("  construction check (jitter instability): %s" % jit_diag)

    datasets = {}
    for seed in SEEDS_FULL:
        tr = gen_dataset_zeroshot(args.train_n, np.random.default_rng(seed), TRAIN_ROLES_V2)
        ev = gen_dataset_zeroshot(args.eval_n, np.random.default_rng(seed + 777), ALL_ROLES)
        tr_b = build_index_batch_ext_v2(tr, enc, seed)
        ev_b = build_index_batch_ext_v2(ev, enc, seed + 777)
        assert tr_b["q_is_heldout"].sum().item() == 0, (
            "ZERO_SHOT_BREACH: seed=%d training set drew a held-out-role query" % seed)
        assert ev_b["q_is_heldout"].sum().item() > 0, (
            "seed=%d eval set drew no held-out-role queries" % seed)
        datasets[seed] = (tr_b, ev_b)

    prior_units = ckpt.load_units(OUTPUT_DIR)
    expected_n_units_full = len(ARMS) * len(SEEDS_FULL)
    if prior_units:
        _log("checkpoint: %d/%d units already recorded on disk; resuming"
             % (len(prior_units), expected_n_units_full))

    arm_results = {mode: [] for mode in ARMS}
    for mode in ARMS:
        _log("--- ARM_%s ---" % mode.upper())
        for seed in SEEDS_FULL:
            k = ckpt.unit_key(mode, seed)
            if k in prior_units:
                arm_results[mode].append(prior_units[k])
                _log("  [resume] %s seed=%d loaded from checkpoint" % (mode, seed))
                continue
            tr_b, ev_b = datasets[seed]
            wm = build_wm(seed, enc, Uc)
            jstd = table_diag["jitter_std_measured"] if mode == "jittered" else None
            table_arg = tables["oracle"] if mode == "jittered" else tables[mode]
            res = _strip_for_checkpoint(
                train_oracle_arm(wm, tr_b, ev_b, mode, table_arg, steps_wm, LR, seed,
                                 "ARM_%s" % mode.upper(), jitter_std=jstd))
            ckpt.record_unit(OUTPUT_DIR, k, res)
            arm_results[mode].append(res)

    verdict, msg, bands = decide_verdict(arm_results)
    elapsed = time.perf_counter() - t0

    n_units_done = sum(len(v) for v in arm_results.values())

    digests = {mode: [r["ev_logits_sha256"] for r in arm_results[mode]] for mode in ARMS}
    arms_differ = len({digests[m][0] for m in ARMS}) == len(ARMS)   # seed-0 outputs pairwise distinct

    def _mean_sd(xs):
        xs = [x for x in xs if not (isinstance(x, float) and math.isnan(x))]
        if not xs:
            return {"mean": float("nan"), "sd": float("nan")}
        m = sum(xs) / len(xs)
        var = sum((x - m) ** 2 for x in xs) / len(xs) if len(xs) > 1 else 0.0
        return {"mean": m, "sd": math.sqrt(var)}

    held_summary = {mode: _mean_sd([r["recall_heldout_acc"] for r in arm_results[mode]]) for mode in ARMS}

    _atomic_write_metrics(OUTPUT_DIR, {
        "verdict": verdict, "verdict_msg": msg,
        "summary": "%s | chance_recall=%.4f | %s" % (verdict, CHANCE_RECALL, msg[:160]),
        "run_mode": "full", "elapsed_s": elapsed, "ts_iso": _now_iso(), "anchor_name": ANCHOR_NAME,
        "chance_recall": CHANCE_RECALL, "oracle_ceiling_ref": 1.0, "bands": bands,
        "held_recall_mean_sd_by_arm": held_summary,
        "table_diag": table_diag,
        "invariance_construction_check": inv_diag, "jitter_instability_check": jit_diag,
        "arm_results": {mode: [{k: v for k, v in r.items() if k != "ev_logits"} for r in arm_results[mode]]
                        for mode in ARMS},
        "arms_differ_verified": bool(arms_differ),
        "cardinality_ok": bool(n_units_done == expected_n_units_full),
        "expected_n_units": expected_n_units_full, "n_units_done": n_units_done,
        "params": {"S_TARGET_TOTAL": S_TARGET_TOTAL, "K_SLOTS": K_SLOTS, "D_MEM": D_MEM,
                   "HIDDEN": HIDDEN, "ADDR_TEMP": ADDR_TEMP, "STEPS_WM": steps_wm, "LR": LR,
                   "train_n": args.train_n, "eval_n": args.eval_n, "seeds": list(SEEDS_FULL),
                   "train_roles_v2": TRAIN_ROLES_V2, "held_out_roles_v2": HELD_OUT_ROLES_V2,
                   "n_heldout_roles": N_HELDOUT_V2, "n_cached_sentences": n_cached,
                   "encoder": "real_v2_frozen", "conditioning": "pca_whiten",
                   "oracle_probe_seed": ORACLE_PROBE_SEED, "jitter_seed_offset": JITTER_SEED_OFFSET,
                   "v2_ckpt": os.path.relpath(V2_CKPT, REPO_ROOT)},
        "start_marker_written": True, "crash_diagnostic_present": True,
        "final_metrics_atomicity": "tmp_replace", "defensive_error_checking": "passed_all_4_patterns",
        "progress_logging": "print_flush_true", "progress_cadence_expected_s": 15})
    _log("VERDICT: %s" % verdict)
    _log("  %s" % msg)
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
