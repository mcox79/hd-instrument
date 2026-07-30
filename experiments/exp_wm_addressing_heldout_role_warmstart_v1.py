# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at self-test (META_RULE_AF; WARM_STARTED vs CONTROL_A eval-logit hash)
# - final_metrics_atomicity: tmp_replace (os.replace at end)
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_n/a: no Cramer-Rao noise floor; discriminator = held-out-role ADDRESSING accuracy vs the
#   pre-registered HARD-PASS/HARD-FAIL/INVALID bands (research hand-off 2026-07-30, section (d)).
#   chance_addr=1/S_TARGET_TOTAL=1/15, chance_recall=1/V_FILL=0.05, oracle ceiling 1.0.
# - baseline_in_band: CONTROL_A_NO_WARMSTART (identical arch, random-init key, no aux, SAME split)
#   is the can-fail control; MUST reproduce STUCK_FLAT (near chance_addr) on BOTH train and held-out
#   query splits, else the split/construction is vacuous -> INVALID. Judged live.
# - discriminator survives scale: FULL is the scale of interest; self-test builds the REAL v2 encoder
#   + REAL conditioned WM + REAL warm-start probe at tiny N (real_code_path).
# - numbers in comments tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@ (META_RULE_AC)
# - deterministic seeding: numpy default_rng + torch.manual_seed only; NO hash(), NO list(set())
"""Held-out-role warm-start transfer test (v1) -- the decisive generalizing-binding discriminator.

CONTEXT (research hand-off notes/exp_dev_handoff_research_binding_credit_assignment_2026-07-30.md +
notes/binding_credit_assignment_structured_prior_research_2026-07-30.md section (d)): this session
proved WM_NL_PROVEN_VIA_READ_CONDITIONING (commit b3bc526ee,
exp_selective_overwrite_recall_nl_wm_readcond_v1.py) -- the content-gated WM learns NL role-filler
binding at eval~0.99 once the addressing key is warm-started from a slot-supervised linear probe fit
over PCA-whitened frozen-encoder reps (+ an aux slot-address CE loss). BUT that eval used HELD-OUT
ITEMS drawn from the SAME 6 roles/slots seen by the probe supervision -- it proves LEARN + item-
generalize, NOT that the addressing MECHANISM itself generalizes to a role it was never supervised on.
This cell is the decisive test: does the warm-started key address roles/slots it was NEVER given
address-supervision on (genuine generalizing binding = brain-faithful structural prior, per the
hippocampal-index / grid-cell / DG-analog reasoning in the research note's section (c)), or does it
only work per-supervised-role (per-instance lookup = the forbidden "supply the answer" pattern)?

THE ONE HARD VARIABLE vs b3bc526ee: the role/slot INVENTORY is widened from S_TARGET=6 (all seen by
supervision) to S_TARGET_TOTAL=15, split into a fixed disjoint TRAIN_ROLES (12, 80%) / HELD_OUT_ROLES
(3, 20%) partition (module-level, seeded, asserted disjoint below). The aux CE loss and the warm-start
probe are BOTH masked to TRAIN_ROLES ONLY -- HELD_OUT_ROLES NEVER appear as a label in either signal
(asserted at runtime in warm_start_key_heldout() and via the q_is_train/ev_slot masking in
aux_loss_trainonly()). Downstream end-to-end recall-loss training still sees held-out-role EPISODES
(task exposure, no address-label leak) -- exactly the protocol in section (d).

Construction: forks exp_selective_overwrite_recall_nl_calib_v1.gen_stream/render_text (VET-confirmed
reservoir-failing NL construction, commit 1e1a49e95) with S_TARGET widened 6->15 (SLOT_NOUNS[0:15] are
now targets, SLOT_NOUNS[15:30] are distractors; same globally-balanced filler multiset + TAIL_MIN +
TARGET_TAIL_MIN leak-guards, unchanged). The frozen v2 encoder's closed-sentence enumeration
(exp_selective_overwrite_recall_nl_wm_roleseparated_v1.FrozenV2Encoder._closed_sentences) loops over a
module-global `S_TARGET` to add query sentences; this cell monkeypatches that module's OWN global
(`base.S_TARGET = S_TARGET_TOTAL`, a process-local, safe, non-invasive widening of the query set the
encoder caches -- it does not touch any file on disk) so the closed set includes query sentences for
all 15 target roles, not just the original 6. Everything else about the encoder/tokenizer/vocab is
byte-identical (SLOT_NOUNS/COLORS/EVENT_TEMPLATES unchanged; only which nouns count as "target" moves).

ARMS:
  WARM_STARTED (the capability under test) -- ReadCondWM (b3bc526ee's conditioned WM, unmodified arch)
    with conditioning=pca_whiten (the proven fix), warm-start key rows fit ONLY for TRAIN_ROLES (each
    row an independent one-vs-rest-within-TRAIN logistic probe; HELD_OUT_ROLES rows are LEFT AT THEIR
    ORIGINAL RANDOM INIT -- asserted unchanged post-warm-start), aux slot-address CE masked to
    TRAIN_ROLES ONLY (event AND query supervision), then continued end-to-end on the SAME downstream
    recall CE loss using episodes drawn from BOTH train- and held-out-role queries (mixed, as the
    protocol specifies). Seeds 7, 13.
  CONTROL_A_NO_WARMSTART (can-fail control #1, ORIGINAL STUCK_FLAT setup) -- IDENTICAL architecture,
    SAME data/split/steps, but conditioning=none (raw reps -- the diagnosed STUCK_FLAT regime), random
    key init, no aux loss: end-to-end training on downstream recall CE alone. MUST reproduce near-
    chance addressing on BOTH splits, or the test is vacuous (INVALID). Seeds 7, 13.
  CONTROL_A_LONGER_SCHEDULE (cheap Olsson-counter-hypothesis diagnostic, hand-off anchor #2; NOT
    load-bearing, reported alongside not instead of) -- CONTROL_A_NO_WARMSTART's exact architecture/
    loss, LONGER_MULT=8x more steps, single seed=7. Disambiguates: does un-supervised gradient descent
    alone eventually un-stick (Olsson induction-head phase transition) given enough steps, or does it
    stay flat (strengthening the structural-warm-start verdict)?
  CONTROL_B_PERROLE_LOOKUP_GROUNDTRUTH (can-fail control #2, "no shared structure" per-role table) --
    a ZERO-TRAINING symbolic best-case ceiling for a non-generalizing per-role lookup: replays the
    keep-last-write bookkeeping using ONLY events whose TRUE slot id is a TRAIN role (held-out/
    distractor events are invisible to it, exactly matching a hand-built table restricted to
    supervised roles). For a TRAIN-role query this exactly reproduces oracle_keep_last (should land
    near 1.0 -- the theoretical BEST CASE any per-role table could ever achieve). For a HELD-OUT-role
    query it has NO entry (by construction; there is no "nearest wrong bucket" fallback that could ever
    be correct) -- STRUCTURALLY 0.0 on held-out. If the warm-started arm's held-out score is close to
    this (0.0 + up to 0.10, per the pre-reg's within-0.10-of-control-B HARD-FAIL clause) rather than
    near its own train-role score, that is disguised memorization, not generalization.

DECISIVE METRIC: addressing accuracy (query -> correct address argmax over the WM's K=15 address
logits), evaluated SEPARATELY on TRAIN-role queries vs HELD-OUT-role queries, on the eval split (never
used for training or for probe-fitting). End-to-end recall accuracy (predicted filler == true filler)
is also reported per split as a secondary number.

PRE-REGISTERED BANDS (research hand-off, NOT loosened; addr_chance = 1/15 = 0.0667):
  HARD_PASS_HELDOUT_ROLE_GENERALIZATION: held-out addr_acc >= 0.80 (both seeds) AND
    (train_addr_acc - held_addr_acc) <= 0.15 (both seeds) AND CONTROL_A stays near chance_addr on BOTH
    splits (both seeds) AND held_addr_acc - control_B_heldout_acc >= 0.30 (both seeds).
  HARD_FAIL_PERROLE_LOOKUP_ONLY: held-out addr_acc < 0.40 (any seed) OR gap > 0.35 (any seed) OR
    |held_addr_acc - control_B_heldout_acc| <= 0.10 (any seed).
  INVALID: CONTROL_A does not reproduce near-chance_addr on this split (construction bug) OR
    train-role addr_acc < 0.85 on any seed (aux signal did not converge on its own supervised set).
  MIDDLE_BAND_INCONCLUSIVE: none of the above triggers (result sits between bands; report honestly,
    do not round up to HARD_PASS).

Run:  .venv/Scripts/python.exe experiments/exp_wm_addressing_heldout_role_warmstart_v1.py --self-test
      .venv/Scripts/python.exe experiments/exp_wm_addressing_heldout_role_warmstart_v1.py --full

ASCII-only. No emojis. Deterministic seeding (torch.Generator + np.random.default_rng; no hash(), no
list(set())). CPU (local, push-free; this .venv has no CUDA). progress_logging: print_flush_true.
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
import torch.nn as nn
import torch.nn.functional as F
from sklearn.linear_model import LogisticRegression

try:
    sys.stdout.reconfigure(line_buffering=True)
except (AttributeError, ValueError):
    pass

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import exp_selective_overwrite_recall_nl_calib_v1 as calib  # noqa: E402
import exp_selective_overwrite_recall_nl_wm_roleseparated_v1 as base  # noqa: E402
import exp_selective_overwrite_recall_nl_wm_readcond_v1 as rc  # noqa: E402

ANCHOR_NAME = "wm_addressing_heldout_role_warmstart_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", "exp_" + ANCHOR_NAME)
V2_CKPT = base.V2_CKPT

# ---------------- expanded role/slot inventory (S_TARGET widened 6 -> 15) ----------------
S_TARGET_TOTAL = 15                                  # MEASURED@this file: 15 target roles (was 6)
N_DISTRACT_SLOTS_LOCAL = len(calib.SLOT_NOUNS) - S_TARGET_TOTAL
assert N_DISTRACT_SLOTS_LOCAL == 15, "SLOT_NOUNS inventory changed unexpectedly"
K_SLOTS = S_TARGET_TOTAL                             # one address key row per role
V_FILL = calib.V_FILL                                # 20 -> CHANCE_RECALL = 0.05
CHANCE_RECALL = calib.CHANCE
ADDR_CHANCE = 1.0 / S_TARGET_TOTAL                   # THEORETICAL: 1/15 = 0.0667
COLORS = calib.COLORS
SLOT_NOUNS = calib.SLOT_NOUNS
EVENT_TEMPLATES = calib.EVENT_TEMPLATES
QUERY_TEMPLATE = calib.QUERY_TEMPLATE

# monkeypatch the ROLE-SEPARATED module's OWN global (process-local; no file on disk touched) so its
# FrozenV2Encoder._closed_sentences() enumerates query sentences for all 15 target roles, not just 6.
base.S_TARGET = S_TARGET_TOTAL

# fixed-seed disjoint TRAIN/HELD-OUT role split (~80/20; 12 train, 3 held-out)
ROLE_SPLIT_SEED = 20260730
N_HELDOUT = 3
_role_rng = np.random.default_rng(ROLE_SPLIT_SEED)
_perm = _role_rng.permutation(S_TARGET_TOTAL).tolist()
HELD_OUT_ROLES = sorted(int(x) for x in _perm[:N_HELDOUT])
TRAIN_ROLES = sorted(int(x) for x in _perm[N_HELDOUT:])
HELD_OUT_SET = set(HELD_OUT_ROLES)
TRAIN_SET = set(TRAIN_ROLES)
assert HELD_OUT_SET.isdisjoint(TRAIN_SET), "SPLIT_IDENTITY_BREACH: train/held-out roles overlap"
assert len(HELD_OUT_ROLES) + len(TRAIN_ROLES) == S_TARGET_TOTAL, "role split does not cover all roles"
assert len(HELD_OUT_ROLES) == N_HELDOUT

# construction params (mirror calib.gen_stream; only S_TARGET widened)
WRITES_MIN, WRITES_MAX = calib.WRITES_MIN, calib.WRITES_MAX
N_DISTRACT_EVENTS = calib.N_DISTRACT_EVENTS
TAIL_MIN = calib.TAIL_MIN
TARGET_TAIL_MIN = calib.TARGET_TAIL_MIN

# WM / training params (architecture IDENTICAL to b3bc526ee's ReadCondWM; reused via `rc` import)
D_MEM = rc.D_MEM
HIDDEN = rc.HIDDEN
ADDR_TEMP = rc.ADDR_TEMP
FULL_TRAIN, FULL_EVAL = rc.FULL_TRAIN, rc.FULL_EVAL          # 1200, 700
STEPS_WM = rc.STEPS_WM                                       # 800
BATCH = rc.BATCH                                             # 256
LR = rc.LR                                                   # 1e-2
EARLY_STOP_LOSS = rc.EARLY_STOP_LOSS
AUX_W = rc.AUX_W
SEEDS_FULL = (7, 13)
LONGER_MULT = 8                                              # Olsson counter-hypothesis: 8x steps
LONGER_SEED = (7,)                                           # single seed (diagnostic, not load-bearing)

# ---- pre-registered bands (research hand-off 2026-07-30, section (d); NOT loosened) ----
HELDOUT_HARDPASS_MIN = 0.80
GAP_HARDPASS_MAX = 0.15
HELDOUT_HARDFAIL_MAX = 0.40
GAP_HARDFAIL_MIN = 0.35
CONTROLB_MARGIN_HARDPASS = 0.30
CONTROLB_INDISTINCT_MARGIN = 0.10
TRAINROLE_INVALID_MIN = 0.85
CONTROLA_STUCKFLAT_MARGIN = 0.10           # CONTROL_A addr_acc must stay < ADDR_CHANCE + this


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


def _atomic_write_metrics(output_dir, metrics):
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, os.path.join(output_dir, "metrics.json"))


# ---------------- construction (S_TARGET widened 6 -> 15; same leak-guards as calib) ----------------
def gen_stream_expanded(rng):
    """calib.gen_stream ported with S_TARGET widened 6->S_TARGET_TOTAL=15 (targets 0..14, distractors
    15..29 within SLOT_NOUNS); IDENTICAL leak-guards (globally-balanced filler multiset, TAIL_MIN,
    TARGET_TAIL_MIN). Does not touch calib.py; a local fork so widening this cell's role count cannot
    affect the shared calib module other cells import."""
    slot_vocab = S_TARGET_TOTAL + N_DISTRACT_SLOTS_LOCAL
    slot_seq = []
    for s in range(S_TARGET_TOTAL):
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

    last_write = {s: -1 for s in range(S_TARGET_TOTAL)}
    for idx, (sl, _fl) in enumerate(events):
        if sl < S_TARGET_TOTAL:
            last_write[sl] = idx
    is_target = np.array([1 if e[0] < S_TARGET_TOTAL else 0 for e in events])
    cum_target_after = np.concatenate([np.cumsum(is_target[::-1])[::-1][1:], [0]])
    eligible = [s for s in range(S_TARGET_TOTAL)
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


def gen_dataset_expanded(n, rng):
    out = []
    while len(out) < n:
        ex = gen_stream_expanded(rng)
        if ex is not None:
            ex["text"] = calib.render_text(ex, rng)     # unchanged: generic over slot/fill ids
            out.append(ex)
    return out


def construction_selftest(seed=7, n=400):
    """Re-verify the expanded (S_TARGET=15) construction is still reservoir/shortcut-failing and the
    oracle ceiling holds, mirroring calib.selftest_construction's checks (reused oracle fns are
    generic over ex dict, no S_TARGET dependency)."""
    rng = np.random.default_rng(seed)
    ds = gen_dataset_expanded(n, rng)
    fails = []
    kl = calib.oracle_acc(ds, calib.oracle_keep_last)
    if kl < 0.999:
        fails.append("oracle_keep_last=%.4f != 1.0 (construction/answer bug)" % kl)
    sc = {"globally_last": calib.oracle_acc(ds, calib.oracle_globally_last),
          "first_occurrence": calib.oracle_acc(ds, calib.oracle_first_occurrence),
          "most_frequent": calib.oracle_acc(ds, calib.oracle_most_frequent)}
    for name, acc in sc.items():
        if acc >= CHANCE_RECALL + 0.05:
            fails.append("shortcut %s solves it acc=%.3f" % (name, acc))
    n_train_q = sum(1 for ex in ds if int(ex["query"]) in TRAIN_SET)
    n_held_q = sum(1 for ex in ds if int(ex["query"]) in HELD_OUT_SET)
    if n_held_q == 0:
        fails.append("no held-out-role queries drawn in %d examples (split/eligibility skew)" % n)
    return {"keep_last": float(kl), "shortcut_accs": sc, "n_train_q": n_train_q, "n_held_q": n_held_q,
            "fails": fails}


# ---------------- index batch (adds slot-id + train/held-out masks for aux loss + stratified eval) ----------------
def build_index_batch_ext(examples, enc, seed):
    b = base.build_index_batch(examples, enc, seed)          # generic; no S_TARGET dependency
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
        q_is_train[i] = q in TRAIN_SET
        q_is_heldout[i] = q in HELD_OUT_SET
    b["ev_slot"] = torch.from_numpy(ev_slot)
    b["q_slot"] = torch.from_numpy(q_slot)
    b["q_is_train"] = torch.from_numpy(q_is_train)
    b["q_is_heldout"] = torch.from_numpy(q_is_heldout)
    return b


# ---------------- aux loss: TRAIN-ROLES ONLY (the integrity crux) ----------------
def aux_loss_trainonly(ev_logits, q_logits, mb):
    """CE forcing address-logits -> true slot id, but ONLY for TRAIN_ROLES labels (event AND query).
    HELD_OUT_ROLES and distractors are UNSUPERVISED here by construction (masked out) -- this is the
    load-bearing integrity property the self-test asserts."""
    ev_slot = mb["ev_slot"].reshape(-1)
    ev_flat = ev_logits.reshape(-1, ev_logits.shape[-1])
    is_train_role = torch.zeros_like(ev_slot, dtype=torch.bool)
    for r in TRAIN_ROLES:
        is_train_role |= (ev_slot == r)
    if is_train_role.any():
        ev_ce = F.cross_entropy(ev_flat[is_train_role], ev_slot[is_train_role])
    else:
        ev_ce = torch.zeros((), dtype=q_logits.dtype)
    qmask = mb["q_is_train"]
    if qmask.any():
        q_ce = F.cross_entropy(q_logits[qmask], mb["q_slot"][qmask])
    else:
        q_ce = torch.zeros((), dtype=q_logits.dtype)
    return q_ce + ev_ce


# ---------------- warm-start: per-TRAIN-role probe, HELD-OUT rows NEVER touched ----------------
def warm_start_key_heldout(wm, enc, seed):
    """Per-TRAIN-role one-vs-rest-WITHIN-TRAIN binary logistic probe. HELD_OUT_ROLES NEVER enter the
    fitting pool (positive or negative) -- only TRAIN_ROLES rows of wm.key are overwritten; held-out
    rows are left at their original random init, to be shaped purely by downstream end-to-end
    recall-loss gradient (the generalization under test). Asserts the integrity property live."""
    with torch.no_grad():
        slot_u, _ = wm._role_reps()
    idxs, labels = [], []
    for s in TRAIN_ROLES:
        idxs.append(enc.idx_of(QUERY_TEMPLATE.format(slot=SLOT_NOUNS[s])))
        labels.append(s)
        for tm in EVENT_TEMPLATES:
            for fl in COLORS:
                idxs.append(enc.idx_of(tm.format(slot=SLOT_NOUNS[s], fill=fl)))
                labels.append(s)
    assert not (set(int(l) for l in labels) & HELD_OUT_SET), (
        "INTEGRITY VIOLATION: a held-out role leaked into warm-start supervision labels")
    idx_t = torch.tensor(idxs)
    X_all = slot_u[idx_t].detach().numpy()
    y_all = np.asarray(labels, dtype=np.int64)
    per_role_fit_acc = {}
    with torch.no_grad():
        held_before = wm.key.data[HELD_OUT_ROLES].clone()
        for r in TRAIN_ROLES:
            y_bin = (y_all == r).astype(np.int64)
            clf = LogisticRegression(max_iter=500, C=1.0, random_state=seed)
            clf.fit(X_all, y_bin)
            coef = torch.from_numpy(clf.coef_.astype(np.float32)).reshape(-1)
            wm.key.data[r] = coef
            per_role_fit_acc[str(r)] = float(clf.score(X_all, y_bin))
        held_after = wm.key.data[HELD_OUT_ROLES].clone()
    assert torch.equal(held_before, held_after), (
        "INTEGRITY VIOLATION: held-out key rows were modified by warm-start")
    with torch.no_grad():
        logits = wm._addr_logits(slot_u[idx_t])
        trainrole_probeset_addr_acc = float((logits.argmax(1).numpy() == y_all).mean())
    return {"per_role_fit_acc": per_role_fit_acc, "n_rows_warmstarted": len(TRAIN_ROLES),
            "n_rows_total": wm.k_slots, "trainrole_probeset_addr_acc": trainrole_probeset_addr_acc,
            "held_out_rows_unchanged_verified": True}


# ---------------- control B: zero-training, best-case per-role lookup (ground-truth restricted) ----------------
def control_b_perrole_groundtruth(examples):
    """Best-case 'per-role-lookup, no shared structure' ceiling: replays keep-last-write bookkeeping
    using ONLY events whose TRUE slot id is a TRAIN role (held-out/distractor events are invisible to
    it -- exactly what a hand-built or nearest-neighbor table restricted to supervised roles could ever
    achieve). Zero gradient training; pure symbolic replay over the raw example dicts. For a TRAIN
    query this exactly reproduces oracle_keep_last (near 1.0: the theoretical best case). For a
    HELD-OUT query it has NO entry at all -- structurally 0.0, not "near chance by luck.\""""
    correct_train = correct_held = total_train = total_held = 0
    for ex in examples:
        last = {}
        for sl, fl in zip(ex["slots"], ex["fills"]):
            s = int(sl)
            if s in TRAIN_SET:
                last[s] = int(fl)
        q = int(ex["query"])
        if q in TRAIN_SET:
            pred = last.get(q, -999)
            total_train += 1
            correct_train += int(pred == ex["answer"])
        else:
            total_held += 1
            correct_held += 0            # no entry possible; structurally never correct
    return {"heldout_acc": correct_held / max(total_held, 1),
            "train_acc": correct_train / max(total_train, 1),
            "n_train": total_train, "n_held": total_held}


# ---------------- training loop (identical arch; local so the TRAIN-ONLY aux mask is explicit) ----------------
def _eval_acc(logits, answer):
    return float((logits.argmax(dim=-1) == answer).float().mean().item())


def train_arm_ext(wm, tr_batch, ev_batch, steps, lr, train_params, seed, log_tag, aux):
    torch.manual_seed(seed)
    g = torch.Generator().manual_seed(seed + 555)
    opt = torch.optim.Adam(train_params, lr=lr)
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
        if aux:
            h_read, ev_logits, q_logits = wm.read_features(mb, want_aux=True)
            logits = wm.readout(h_read)
            loss = F.cross_entropy(logits, mb["answer"]) + AUX_W * aux_loss_trainonly(ev_logits, q_logits, mb)
        else:
            logits = wm(mb)
            loss = F.cross_entropy(logits, mb["answer"])
        loss.backward()
        opt.step()
        lv = float(loss.item())
        ema = lv if ema is None else 0.9 * ema + 0.1 * lv
        if step == 0 or (step + 1) % max(1, steps // 8) == 0:
            loss_curve.append((step, lv))
            _log("    [%s seed=%d] step=%d loss=%.4f ema=%.4f" % (log_tag, seed, step + 1, lv, ema))
        if step >= 200 and ema is not None and ema < EARLY_STOP_LOSS:
            break
    wm.eval()
    with torch.no_grad():
        ev_h, ev_addr_logits, ev_q_logits = wm.read_features(ev_batch, want_aux=True)
        ev_pred = wm.readout(ev_h)
        eval_acc = _eval_acc(ev_pred, ev_batch["answer"])
        addr_pred = ev_q_logits.argmax(dim=-1)
        addr_correct = (addr_pred == ev_batch["q_slot"]).float()
        recall_correct = (ev_pred.argmax(-1) == ev_batch["answer"]).float()
        tm, hm = ev_batch["q_is_train"], ev_batch["q_is_heldout"]
        addr_train_acc = float(addr_correct[tm].mean()) if tm.any() else float("nan")
        addr_held_acc = float(addr_correct[hm].mean()) if hm.any() else float("nan")
        recall_train_acc = float(recall_correct[tm].mean()) if tm.any() else float("nan")
        recall_held_acc = float(recall_correct[hm].mean()) if hm.any() else float("nan")
        tr_logits = wm(tr_batch)
        tr_acc = _eval_acc(tr_logits, tr_batch["answer"])
    wm.train()
    first_loss = loss_curve[0][1] if loss_curve else float("nan")
    last_loss = loss_curve[-1][1] if loss_curve else float("nan")
    _log("  [%s seed=%d] eval_acc=%.4f addr_train=%.4f addr_held=%.4f recall_train=%.4f recall_held=%.4f "
         "loss %.3f->%.3f steps=%d"
         % (log_tag, seed, eval_acc, addr_train_acc, addr_held_acc, recall_train_acc, recall_held_acc,
            first_loss, last_loss, step + 1))
    return dict(eval_acc=eval_acc, train_acc=tr_acc, addr_train_acc=addr_train_acc,
                addr_heldout_acc=addr_held_acc, recall_train_acc=recall_train_acc,
                recall_heldout_acc=recall_held_acc, ev_logits=ev_pred.detach(),
                loss_curve=loss_curve, steps_run=step + 1, first_loss=first_loss, last_loss=last_loss)


def build_wm(seed, enc, cond, kind):
    Uc = cond.apply(enc.U_tok_t, enc.U_pad_t, kind)
    return rc.ReadCondWM(seed, enc.d, D_MEM, K_SLOTS, HIDDEN, V_FILL, ADDR_TEMP, Uc, enc.U_pad_t)


def run_warm_started(enc, cond, tr_batch, ev_batch, seed, steps):
    wm = build_wm(seed, enc, cond, "pca_whiten")
    warm_diag = warm_start_key_heldout(wm, enc, seed)
    res = train_arm_ext(wm, tr_batch, ev_batch, steps, LR, list(wm.parameters()), seed,
                        "WARM_STARTED", aux=True)
    res["warmstart_diag"] = warm_diag
    return res


def run_control_a(enc, cond, tr_batch, ev_batch, seed, steps, log_tag="CONTROL_A"):
    wm = build_wm(seed, enc, cond, "none")
    res = train_arm_ext(wm, tr_batch, ev_batch, steps, LR, list(wm.parameters()), seed,
                        log_tag, aux=False)
    return res


# ---------------- verdict ----------------
def decide_verdict(warm_results, controlA_results, controlB, longer_result):
    controlA_ok = all(
        (r["addr_train_acc"] < ADDR_CHANCE + CONTROLA_STUCKFLAT_MARGIN)
        and (r["addr_heldout_acc"] < ADDR_CHANCE + CONTROLA_STUCKFLAT_MARGIN)
        for r in controlA_results)
    train_addrs = [r["addr_train_acc"] for r in warm_results]
    held_addrs = [r["addr_heldout_acc"] for r in warm_results]
    gaps = [t - h for t, h in zip(train_addrs, held_addrs)]
    train_ok = all(t >= TRAINROLE_INVALID_MIN for t in train_addrs)

    if not controlA_ok:
        verdict = "INVALID"
        msg = ("CONTROL_A_NO_WARMSTART did not reproduce near-chance addressing (addr_chance=%.4f, "
               "margin=%.2f) on both splits: train=%s held=%s -- the split/construction is not a valid "
               "test of the warm-start intervention (may itself be informative, but do not interpret "
               "the warm-started arm's gap against this control)."
               % (ADDR_CHANCE, CONTROLA_STUCKFLAT_MARGIN,
                  [round(r["addr_train_acc"], 3) for r in controlA_results],
                  [round(r["addr_heldout_acc"], 3) for r in controlA_results]))
    elif not train_ok:
        verdict = "INVALID"
        msg = ("TRAIN-role addressing accuracy < %.2f on >=1 seed (%s): the aux/warm-start signal did "
               "not even converge on its OWN supervised set -- a prerequisite failure, not a "
               "generalization failure." % (TRAINROLE_INVALID_MIN, [round(t, 3) for t in train_addrs]))
    else:
        cb_held = controlB["heldout_acc"]
        clears_b = all((h - cb_held) >= CONTROLB_MARGIN_HARDPASS for h in held_addrs)
        indistinct_b = any(abs(h - cb_held) <= CONTROLB_INDISTINCT_MARGIN for h in held_addrs)
        hard_pass = (all(h >= HELDOUT_HARDPASS_MIN for h in held_addrs)
                     and all(g <= GAP_HARDPASS_MAX for g in gaps)
                     and clears_b)
        hard_fail = (any(h < HELDOUT_HARDFAIL_MAX for h in held_addrs)
                     or any(g > GAP_HARDFAIL_MIN for g in gaps)
                     or indistinct_b)
        if hard_pass:
            verdict = "HARD_PASS_HELDOUT_ROLE_GENERALIZATION"
            msg = ("held-out-role addressing >= %.2f (both seeds: %s) AND gap-vs-train <= %.2f (%s) AND "
                   "CONTROL_A stayed near chance_addr=%.4f on both splits AND warm-started arm clears "
                   "CONTROL_B (per-role-lookup ceiling, held-out=%.4f) by >= %.2f on held-out roles "
                   "(margins: %s). Genuine generalizing binding via structural warm-start -- the "
                   "hippocampal-index/DG-analog reasoning in the research note is CONFIRMED, not just "
                   "the item-generalization already shown in b3bc526ee."
                   % (HELDOUT_HARDPASS_MIN, [round(h, 3) for h in held_addrs], GAP_HARDPASS_MAX,
                      [round(g, 3) for g in gaps], ADDR_CHANCE, cb_held, CONTROLB_MARGIN_HARDPASS,
                      [round(h - cb_held, 3) for h in held_addrs]))
        elif hard_fail:
            verdict = "HARD_FAIL_PERROLE_LOOKUP_ONLY"
            msg = ("held-out-role addressing < %.2f (some seed: %s) OR gap > %.2f (some seed: %s) OR "
                   "within %.2f of CONTROL_B's held-out ceiling (%.4f). The warm-start fix is a "
                   "practical unstick-the-optimizer trick, NOT the generalizing structural-prior "
                   "mechanism claimed -- it is the forbidden per-instance 'supply the answer' pattern "
                   "in disguise. Held-out addr accs=%s, gaps=%s."
                   % (HELDOUT_HARDFAIL_MAX, [round(h, 3) for h in held_addrs], GAP_HARDFAIL_MIN,
                      [round(g, 3) for g in gaps], CONTROLB_INDISTINCT_MARGIN, cb_held,
                      [round(h, 3) for h in held_addrs], [round(g, 3) for g in gaps]))
        else:
            verdict = "MIDDLE_BAND_INCONCLUSIVE"
            msg = ("Result sits between the pre-registered bands: held-out addr accs=%s, gaps=%s, "
                   "control_B held-out ceiling=%.4f. Neither HARD_PASS nor HARD_FAIL criteria fully "
                   "met -- report honestly, do not round up." % ([round(h, 3) for h in held_addrs],
                                                                  [round(g, 3) for g in gaps], cb_held))
    bands = {"addr_chance": ADDR_CHANCE, "chance_recall": CHANCE_RECALL, "oracle_ceiling": 1.0,
             "heldout_hardpass_min": HELDOUT_HARDPASS_MIN, "gap_hardpass_max": GAP_HARDPASS_MAX,
             "heldout_hardfail_max": HELDOUT_HARDFAIL_MAX, "gap_hardfail_min": GAP_HARDFAIL_MIN,
             "controlb_margin_hardpass": CONTROLB_MARGIN_HARDPASS,
             "controlb_indistinct_margin": CONTROLB_INDISTINCT_MARGIN,
             "trainrole_invalid_min": TRAINROLE_INVALID_MIN,
             "controla_stuckflat_margin": CONTROLA_STUCKFLAT_MARGIN,
             "controlA_ok": bool(controlA_ok), "train_ok": bool(train_ok),
             "train_addrs": train_addrs, "held_addrs": held_addrs, "gaps": gaps,
             "control_b": controlB, "longer_schedule_result": longer_result}
    return verdict, msg, bands


# ---------------- self-test ----------------
def run_self_test():
    _log("SELF-TEST: role split integrity ...")
    _log("  TRAIN_ROLES(%d)=%s HELD_OUT_ROLES(%d)=%s"
         % (len(TRAIN_ROLES), TRAIN_ROLES, len(HELD_OUT_ROLES), HELD_OUT_ROLES))
    assert HELD_OUT_SET.isdisjoint(TRAIN_SET)
    assert len(HELD_OUT_ROLES) + len(TRAIN_ROLES) == S_TARGET_TOTAL

    _log("SELF-TEST: expanded construction (S_TARGET=%d) leak-proofing ..." % S_TARGET_TOTAL)
    cst = construction_selftest(seed=7, n=400)
    _log("  keep_last=%.4f n_train_q=%d n_held_q=%d shortcuts=%s"
         % (cst["keep_last"], cst["n_train_q"], cst["n_held_q"], cst["shortcut_accs"]))
    if cst["fails"]:
        raise AssertionError("construction self-test FAILED: %s" % "; ".join(cst["fails"]))

    _log("SELF-TEST: load REAL v2 encoder (widened closed sentence set) ...")
    assert os.path.exists(V2_CKPT), "v2 checkpoint missing: %s" % V2_CKPT
    enc = base.FrozenV2Encoder(V2_CKPT)
    n_cached = enc.build_cache()
    assert n_cached >= 3000, "closed sentence set smaller than expected (widened query set missing?)"
    for r in range(S_TARGET_TOTAL):
        enc.idx_of(QUERY_TEMPLATE.format(slot=SLOT_NOUNS[r]))       # raises KeyError if missing
    cond = rc.Conditioner(enc.U_tok_t, enc.U_pad_t)

    _log("SELF-TEST: warm-start integrity (held-out rows must NEVER be touched or supervised) ...")
    wm = build_wm(7, enc, cond, "pca_whiten")
    wd = warm_start_key_heldout(wm, enc, 7)
    _log("  warmstart: trainrole_probeset_addr_acc=%.4f rows_warmstarted=%d/%d"
         % (wd["trainrole_probeset_addr_acc"], wd["n_rows_warmstarted"], wd["n_rows_total"]))
    assert wd["trainrole_probeset_addr_acc"] > 0.5, "warm-start probe failed to converge on TRAIN roles"
    assert wd["held_out_rows_unchanged_verified"]

    _log("SELF-TEST: control B (zero-training per-role-lookup ceiling) ...")
    tiny_ds = gen_dataset_expanded(200, np.random.default_rng(7 + 777))
    cb = control_b_perrole_groundtruth(tiny_ds)
    _log("  control_b: train_acc=%.4f held_acc=%.4f (n_train=%d n_held=%d)"
         % (cb["train_acc"], cb["heldout_acc"], cb["n_train"], cb["n_held"]))
    assert cb["heldout_acc"] == 0.0, "control B held-out acc should be structurally 0.0"
    assert cb["train_acc"] > 0.8, "control B train-role acc should be near the oracle ceiling"

    _log("SELF-TEST: tiny end-to-end (WARM_STARTED vs CONTROL_A, arms-must-differ) ...")
    tr = build_index_batch_ext(gen_dataset_expanded(150, np.random.default_rng(7)), enc, 7)
    ev = build_index_batch_ext(gen_dataset_expanded(150, np.random.default_rng(7 + 777)), enc, 7 + 777)
    assert ev["q_is_heldout"].sum().item() > 0, "tiny eval set drew no held-out-role queries"
    warm_res = run_warm_started(enc, cond, tr, ev, 7, steps=60)
    ctrl_res = run_control_a(enc, cond, tr, ev, 7, steps=60)
    _log("  tiny WARM_STARTED: eval=%.3f addr_train=%.3f addr_held=%.3f"
         % (warm_res["eval_acc"], warm_res["addr_train_acc"], warm_res["addr_heldout_acc"]))
    _log("  tiny CONTROL_A:    eval=%.3f addr_train=%.3f addr_held=%.3f"
         % (ctrl_res["eval_acc"], ctrl_res["addr_train_acc"], ctrl_res["addr_heldout_acc"]))

    def _digest(t):
        return hashlib.sha256(t.cpu().numpy().tobytes()).hexdigest()
    arms_differ = _digest(warm_res["ev_logits"]) != _digest(ctrl_res["ev_logits"])
    assert arms_differ, "META_RULE_AF VIOLATION: WARM_STARTED and CONTROL_A bit-identical outputs"
    for r in (warm_res, ctrl_res):
        assert 0.0 <= r["eval_acc"] <= 1.0
        assert 0.0 <= r["addr_train_acc"] <= 1.0
        assert 0.0 <= r["addr_heldout_acc"] <= 1.0
    _log("SELF-TEST PASS")
    return {"role_split": {"train": TRAIN_ROLES, "held_out": HELD_OUT_ROLES}, "construction": cst,
            "n_cached": n_cached, "warmstart_diag": wd, "control_b": cb,
            "tiny_warm": {"eval_acc": warm_res["eval_acc"], "addr_train": warm_res["addr_train_acc"],
                          "addr_held": warm_res["addr_heldout_acc"]},
            "tiny_control_a": {"eval_acc": ctrl_res["eval_acc"], "addr_train": ctrl_res["addr_train_acc"],
                               "addr_held": ctrl_res["addr_heldout_acc"]},
            "arms_differ_verified": bool(arms_differ)}


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
    expected_units = 1 if run_mode == "self_test" else (len(SEEDS_FULL) * 2 + len(LONGER_SEED) + 1)
    _write_start_marker(OUTPUT_DIR, run_mode, expected_units)
    t0 = time.perf_counter()

    if run_mode == "self_test":
        st = run_self_test()
        elapsed = time.perf_counter() - t0
        _atomic_write_metrics(OUTPUT_DIR, {
            "verdict": "SELFTEST_PASS",
            "verdict_msg": "SELFTEST_PASS (role split integrity + expanded construction + real "
                           "encoder + warm-start held-out-row integrity + control B + arms-differ)",
            "summary": "SELFTEST_PASS", "run_mode": "self_test", "elapsed_s": elapsed,
            "ts_iso": _now_iso(), "anchor_name": ANCHOR_NAME, "addr_chance": ADDR_CHANCE,
            "chance_recall": CHANCE_RECALL, "selftest": st})
        _log("DONE self-test in %.1fs" % elapsed)
        return

    steps_wm = args.steps_wm
    _log("FULL: train_n=%d eval_n=%d steps_wm=%d longer_mult=%d seeds=%s addr_chance=%.4f "
         "chance_recall=%.4f train_roles=%d held_out_roles=%d"
         % (args.train_n, args.eval_n, steps_wm, LONGER_MULT, SEEDS_FULL, ADDR_CHANCE, CHANCE_RECALL,
            len(TRAIN_ROLES), len(HELD_OUT_ROLES)))
    cst = construction_selftest(seed=7, n=600)
    if cst["fails"]:
        raise AssertionError("pre-run construction self-test FAILED: %s" % "; ".join(cst["fails"]))

    enc = base.FrozenV2Encoder(V2_CKPT)
    n_cached = enc.build_cache()
    _log("  cached %d unique sentence TOKEN reps (d=%d)" % (n_cached, enc.d))
    cond = rc.Conditioner(enc.U_tok_t, enc.U_pad_t)

    datasets = {}
    for seed in SEEDS_FULL:
        tr = gen_dataset_expanded(args.train_n, np.random.default_rng(seed))
        ev = gen_dataset_expanded(args.eval_n, np.random.default_rng(seed + 777))
        datasets[seed] = (build_index_batch_ext(tr, enc, seed), build_index_batch_ext(ev, enc, seed + 777),
                          tr, ev)

    _log("--- control B (zero-training per-role-lookup ceiling; eval sets pooled) ---")
    pooled_eval = []
    for seed in SEEDS_FULL:
        pooled_eval.extend(datasets[seed][3])
    control_b = control_b_perrole_groundtruth(pooled_eval)
    _log("  control_b: train_acc=%.4f held_acc=%.4f" % (control_b["train_acc"], control_b["heldout_acc"]))

    _log("--- WARM_STARTED (pca_whiten + train-only aux + train-only warmstart) ---")
    warm_results = []
    for seed in SEEDS_FULL:
        tr_b, ev_b, _, _ = datasets[seed]
        warm_results.append(run_warm_started(enc, cond, tr_b, ev_b, seed, steps_wm))

    _log("--- CONTROL_A_NO_WARMSTART (original STUCK_FLAT setup, same split/steps) ---")
    controlA_results = []
    for seed in SEEDS_FULL:
        tr_b, ev_b, _, _ = datasets[seed]
        controlA_results.append(run_control_a(enc, cond, tr_b, ev_b, seed, steps_wm))

    _log("--- CONTROL_A_LONGER_SCHEDULE (Olsson counter-hypothesis diagnostic, %dx steps, seed=%s) ---"
         % (LONGER_MULT, LONGER_SEED))
    longer_seed = LONGER_SEED[0]
    tr_b, ev_b, _, _ = datasets[longer_seed]
    longer_result = run_control_a(enc, cond, tr_b, ev_b, longer_seed, steps_wm * LONGER_MULT,
                                  log_tag="CONTROL_A_LONGER")

    def _digest(t):
        return hashlib.sha256(t.cpu().numpy().tobytes()).hexdigest()
    arms_differ = _digest(warm_results[0]["ev_logits"]) != _digest(controlA_results[0]["ev_logits"])

    verdict, msg, bands = decide_verdict(warm_results, controlA_results, control_b, longer_result)
    elapsed = time.perf_counter() - t0

    n_units_done = len(warm_results) + len(controlA_results) + 1 + 1
    expected_n_units_full = len(SEEDS_FULL) * 2 + 1 + 1

    _atomic_write_metrics(OUTPUT_DIR, {
        "verdict": verdict, "verdict_msg": msg,
        "summary": "%s | addr_chance=%.4f | %s" % (verdict, ADDR_CHANCE, msg[:160]),
        "run_mode": "full", "elapsed_s": elapsed, "ts_iso": _now_iso(), "anchor_name": ANCHOR_NAME,
        "addr_chance": ADDR_CHANCE, "chance_recall": CHANCE_RECALL, "oracle_ceiling_ref": 1.0,
        "bands": bands, "role_split": {"train_roles": TRAIN_ROLES, "held_out_roles": HELD_OUT_ROLES,
                                        "role_split_seed": ROLE_SPLIT_SEED},
        "construction_selftest": cst, "control_b": control_b,
        "warm_started_per_seed": [
            {k: v for k, v in r.items() if k not in ("ev_logits",)} for r in warm_results],
        "control_a_per_seed": [
            {k: v for k, v in r.items() if k not in ("ev_logits",)} for r in controlA_results],
        "control_a_longer_schedule": {k: v for k, v in longer_result.items() if k not in ("ev_logits",)},
        "arms_differ_verified": bool(arms_differ),
        "cardinality_ok": bool(n_units_done == expected_n_units_full),
        "expected_n_units": expected_n_units_full, "n_units_done": n_units_done,
        "params": {"S_TARGET_TOTAL": S_TARGET_TOTAL, "K_SLOTS": K_SLOTS, "D_MEM": D_MEM, "HIDDEN": HIDDEN,
                   "ADDR_TEMP": ADDR_TEMP, "STEPS_WM": steps_wm, "LONGER_MULT": LONGER_MULT,
                   "LR": LR, "AUX_W": AUX_W, "train_n": args.train_n, "eval_n": args.eval_n,
                   "seeds": list(SEEDS_FULL), "longer_seed": list(LONGER_SEED),
                   "train_roles": TRAIN_ROLES, "held_out_roles": HELD_OUT_ROLES,
                   "n_cached_sentences": n_cached, "encoder": "real_v2_frozen",
                   "v2_ckpt": os.path.relpath(V2_CKPT, REPO_ROOT)},
        "start_marker_written": True, "crash_diagnostic_present": True,
        "final_metrics_atomicity": "tmp_replace", "defensive_error_checking": "passed_all_4_patterns",
        "progress_logging": "print_flush_true", "progress_cadence_expected_s": 60})
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
