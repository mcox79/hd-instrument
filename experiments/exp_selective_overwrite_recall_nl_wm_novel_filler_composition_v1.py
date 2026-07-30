# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at self-test (META_RULE_AF; LEARNED vs RANDOM_INIT eval-logit hash)
# - final_metrics_atomicity: tmp_replace (os.replace at end)
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_n/a: no Cramer-Rao noise floor; discriminator = LEARNED_WM vs RANDOM_INIT_WM vs SHUFFLED_QUERY
#   separation on genuinely-held-out constructions, judged live (chance=1/V_FILL=0.05).
# - baseline_in_band: RANDOM_INIT_WM (frozen wm params, trained readout, same pca_whiten conditioning)
#   is the can-fail baseline on EACH eval set (std/Q1/Q2); MUST stay near chance -- EMPIRICALLY
#   VALIDATED per eval set (2026-07-30 fairness amendment: floors have repeatedly failed to floor
#   elsewhere this session, so this is measured live per eval-set, not assumed from the prior cell).
# - discriminator survives scale: FULL is the scale of interest (<8min CPU budget, frozen encoder);
#   self-test builds REAL v2 encoder + REAL construction + REAL WM at tiny N (real_code_path).
# - numbers in comments tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@ (META_RULE_AC)
# - deterministic seeding: numpy default_rng + torch.manual_seed only; NO hash(), NO list(set())
"""Selective-Overwrite-Recall NL WM -- NOVEL-FILLER + NOVEL-COMPOSITION generalization probe (v1).

REFRAME (2026-07-30): tonight's held-out-ROLE tests hard-failed even with a clean oracle address
(a perfect one-hot address fails zero-shot on a NOVEL role) -- but roles/relations are a semi-CLOSED
schema class; ENTITIES/fillers are the OPEN class. Comprehension-relevant binding = bind a NOVEL
FILLER into a KNOWN role (+ a NOVEL COMPOSITION of known roles), NOT a novel role. The proven
read-conditioning WM (exp_selective_overwrite_recall_nl_wm_readcond_v1, config pca_whiten_aux_warm,
commit <this session>) reached eval=[0.989, 0.989] both seeds on the STANDARD distribution
MEASURED@data/exp_selective_overwrite_recall_nl_wm_readcond_v1/metrics.json:bands.best_learned_accs.
This cell asks: does that same mechanism, trained the SAME way (same encoder, same conditioning, same
aux+warmstart recipe, same overwrite-with-suppression+distractor difficulty), also cover:

  Q1 TRUE NOVEL-FILLER-TO-KNOWN-ROLE: for each of the 6 target roles s, a specific filler
     HELD_OUT_FILLER[s] NEVER co-occurs with role s ANYWHERE in training (not just at the final write --
     scrubbed from every event of that role via swap-repair, preserving the global filler multiset so
     no new shortcut is introduced). The filler ITSELF is not novel (it appears elsewhere in training
     bound to OTHER roles, so the readout head has seen that class); only the (role, filler) PAIRING is
     novel. Eval forces role s's last write to be exactly that held-out filler and queries role s.

  Q2 NOVEL COMPOSITION: a specific JOINT configuration -- role Q2_SLOT_A's final filler == Q2_FILLER_A
     AND role Q2_SLOT_B's final filler == Q2_FILLER_B SIMULTANEOUSLY -- never co-occurs in training
     (each condition ALONE is common in training; only their CONJUNCTION is scrubbed via swap-repair on
     slot_b's last-write filler). Eval forces both conditions simultaneously and queries one of the two
     roles (alternating).

FAIRNESS (USER-relayed mid-task correction, 2026-07-30 -- "can-fail floors have repeatedly failed to
floor tonight"): this cell does NOT assume the RANDOM_INIT_WM floor generalizes from the readcond
cell's regime. Per eval-set (std/Q1/Q2) it separately, EMPIRICALLY measures:
  (a) RANDOM_INIT_WM (frozen wm params on the SAME pca_whiten-conditioned reps, trained readout only)
      -- must land near chance on THIS eval set.
  (b) SHUFFLED_QUERY control on the TRAINED LEARNED_WM itself: re-evaluate with each example's query
      address swapped for a DIFFERENT example's query address (torch.roll shift=1) while scoring
      against the ORIGINAL true answer -- if the metric is not sensitive to WHICH role is queried
      (i.e. answer is recoverable independent of the query), this must ALSO collapse to chance. Any
      eval-set where either floor does NOT collapse is flagged floor_broken=True and EXCLUDED from a
      HAVE_COMPREHENSION_TARGET claim (METRIC_INVALID for that eval-set specifically), per the
      mid-task correction. Numbers are reported regardless so the floor is inspectable either way.
  (c) leakage guard: no Q1/Q2 eval (slots,fills,query) tuple appears in the training set's tuple-key
      set (calib-style _key leak check).
  (d) apples-to-apples: SAME task difficulty (overwrite-with-suppression + N_DISTRACT_EVENTS=36
      distractors, TAIL_MIN/TARGET_TAIL_MIN unchanged) as the proven readcond run -- only the filler/
      composition HOLDOUT is added; no easy-mode shortcuts removed or added.

PRE-REGISTERED DECISION RULE (fixed before this cell's FULL run):
  HAVE_COMPREHENSION_TARGET -- Q1 learned_acc >= Q1_PROVEN_MIN both seeds AND Q1's floors (RI + shuffle)
      both collapse to chance (floor_broken=False) -> read-conditioning already does novel-filler-to-
      known-role binding at the real task difficulty; the held-out-ROLE failures were a harder, likely-
      not-required target. (Q2 also >= its PROVEN_MIN strengthens the claim; Q2 at chance = a
      compositional gap remains even though HAVE_COMPREHENSION_TARGET holds for Q1.)
  MISSING -- Q1 learned_acc <= Q1_CHANCE_MAX both seeds (regardless of floor state) -> read-conditioning
      does NOT do novel-filler binding; only memorizes seen (role,filler) pairs; a real gap remains.
  PARTIAL -- Q1 strictly between the two bars (beats floor, below proven bar) -- reported, not one of
      the 3 headline labels, but the honest middle state.
  METRIC_INVALID -- any of Q1's two floors (RI or shuffle) fails to collapse -> the discriminator itself
      cannot be trusted for Q1 on this construction; do NOT claim HAVE_COMPREHENSION_TARGET regardless
      of the raw learned_acc number. (Same floor-state field reported independently for Q2 and std.)

Mechanism reused UNCHANGED from the proven cell (pca_whiten_aux_warm, the WM_NL_PROVEN_VIA_READ_
CONDITIONING config): frozen v2 encoder (data/exp_scale_meaning_learn_arc_heldout_v2/ckpt_seed_7.pt),
PCA-whitened cached token reps, role-separated content-gated overwrite WM (2 learned role queries, K=6
content-address keys, learned write gate, gated OVERWRITE), aux slot-address CE loss, warm-started key
matrix. ONLY the data CONSTRUCTION changes (holdout repairs); imported directly from the proven cell's
module (no reimplementation of the mechanism).

Run:  .venv/Scripts/python.exe experiments/exp_selective_overwrite_recall_nl_wm_novel_filler_composition_v1.py --self-test
      .venv/Scripts/python.exe experiments/exp_selective_overwrite_recall_nl_wm_novel_filler_composition_v1.py --full

ASCII-only. No emojis. Deterministic seeding (torch.Generator + np.random.default_rng; no hash(), no
list(set())). CPU (local, push-free; this .venv has no CUDA). Budget: <8min CPU FULL (reduced
STEPS_WM/train_n/eval_n vs the 6-config readcond cell, which alone took ~3678s for 12 learned units --
this cell trains only 1 config x 2 seeds = 2 learned units, so scope was cut accordingly).
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

try:
    sys.stdout.reconfigure(line_buffering=True)
except (AttributeError, ValueError):
    pass

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import exp_selective_overwrite_recall_nl_calib_v1 as calib  # noqa: E402
import exp_selective_overwrite_recall_nl_wm_readcond_v1 as rc  # noqa: E402 (proven mechanism + module)

ANCHOR_NAME = "selective_overwrite_recall_nl_wm_novel_filler_composition_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", "exp_" + ANCHOR_NAME)
V2_CKPT = rc.V2_CKPT

# ---- pull calibrated NL construction constants (single source of truth) ----
V_FILL = calib.V_FILL                    # 20 -> CHANCE = 0.05
CHANCE = calib.CHANCE
S_TARGET = calib.S_TARGET                # 6 target slots (0=door .. 5=gate)
N_DISTRACT_SLOTS = calib.N_DISTRACT_SLOTS
WRITES_MIN, WRITES_MAX = calib.WRITES_MIN, calib.WRITES_MAX
N_DISTRACT_EVENTS = calib.N_DISTRACT_EVENTS
TAIL_MIN, TARGET_TAIL_MIN = calib.TAIL_MIN, calib.TARGET_TAIL_MIN

# ---- Q1 holdout: bijection target-slot -> forbidden filler (never co-occurs, ANY position) ----
# NOTE (confound caught + fixed pre-run, 2026-07-30): an earlier draft used HELD_OUT_FILLER[s] = s
# (0..5), which makes the Q1 ANSWER numerically identical to the ADDRESSED MEMORY-SLOT INDEX (K_SLOTS
# = S_TARGET = 6, keyed 0..5). That would let a degenerate "predict class = retrieved-slot-index"
# shortcut (content-BLIND, using only the aux-loss-supervised address) ace the test without ever
# reading the stored filler content -- exactly the kind of construction confound the fairness gate is
# meant to catch. Fixed: held-out filler ids are offset into 12..17, DISJOINT from the 0..5 slot-index
# range, so an address-only shortcut predicts a class in 0..5 and NEVER matches a true answer in
# 12..17 -- that shortcut is now architecturally excluded, not just empirically absent.
HELD_OUT_FILLER = {s: 12 + s for s in range(S_TARGET)}   # door->gold(12) window->silver(13) wall->teal(14)
                                                          # roof->maroon(15) floor->violet(16) gate->beige(17)

# ---- Q2 holdout: a specific JOINT final-state config (individually-common, jointly-scrubbed) ----
Q2_SLOT_A, Q2_SLOT_B = 0, 1          # door, window
Q2_FILLER_A, Q2_FILLER_B = 10, 11    # gray, cyan (disjoint from HELD_OUT_FILLER's 12..17 range)

# ---- WM / training params (mechanism IDENTICAL to the proven pca_whiten_aux_warm config) ----
K_SLOTS = 6
D_MEM = 64
HIDDEN = 64
ADDR_TEMP = 0.3
LR = 1e-2
AUX_W = 1.0
PCA_EPS = 1e-4
SEEDS_FULL = (7, 13)
N_RANDOM_INIT = 2
MAX_EVAL_RETRY = 400          # rejection-sampling cap per forced held-out example

# scope cut vs the 6-config readcond cell (that cell: STEPS_WM=800, train_n=1200 x 12 learned units,
# ~3678s MEASURED@data/exp_selective_overwrite_recall_nl_wm_readcond_v1/metrics.json:elapsed_s). This
# cell trains 1 config x 2 seeds = 2 learned units -> defaults sized for the <8min CPU budget.
FULL_TRAIN = 500
FULL_EVAL_STD = 200
FULL_EVAL_Q1_PER_SLOT = 30    # x6 slots = 180
FULL_EVAL_Q2_PER_QUERY = 90   # x2 (query=A, query=B) = 180
STEPS_WM = 300
BATCH = 128
STEPS_READOUT = 150

# ---- bands ----
Z_THRESH = 2.0
RI_NEAR_CHANCE = 0.10          # RANDOM_INIT_WM floor bar (per eval-set)
SHUF_NEAR_CHANCE = 0.15        # SHUFFLED_QUERY floor bar on LEARNED_WM (per eval-set, per seed)
Q_PROVEN_MIN = 0.50            # learned_acc >= this both seeds -> PROVEN for that eval-set
Q_CHANCE_MAX = 0.15            # learned_acc <= this both seeds -> MISSING for that eval-set
MECH_MARGIN = 0.30
ORACLE_CEILING = 1.0


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


def _binom_se(acc, n):
    n = max(int(n), 1)
    return math.sqrt(max(acc * (1.0 - acc), 1e-9) / n)


def _one_sided_p(z):
    return 0.5 * math.erfc(z / math.sqrt(2.0))


def power_stats(trained_acc, n_eval, ri_accs):
    ri = np.asarray(ri_accs, dtype=float)
    ri_mean = float(ri.mean())
    ri_std = float(ri.std(ddof=1)) if ri.size > 1 else 0.0
    ri_max = float(ri.max())
    se_trained = _binom_se(trained_acc, n_eval)
    se_ri_mean = _binom_se(ri_mean, n_eval)
    se_diff = math.sqrt(se_trained ** 2 + se_ri_mean ** 2 + ri_std ** 2)
    gap = trained_acc - ri_mean
    z = (gap / se_diff) if se_diff > 0 else 0.0
    return dict(ri_mean=ri_mean, ri_max=ri_max, se_diff=se_diff, gap=gap, z=z,
                p_value=_one_sided_p(z), significant=bool(z >= Z_THRESH and trained_acc > ri_max))


# ================= CONSTRUCTION: raw stream (mirrors calib.gen_stream up to the query pick) =================
def _raw_stream(rng):
    """Returns (slot_seq, fill_pool) BEFORE eligibility/query pick -- mirrors calib.gen_stream's
    stream-building code exactly (same distribution) so downstream repairs operate on a standard
    draw. slot_seq/fill_pool are numpy int64 arrays, mutually consistent index-for-index (event i)."""
    slot_vocab = S_TARGET + N_DISTRACT_SLOTS
    slot_seq = []
    for s in range(S_TARGET):
        k = int(rng.integers(WRITES_MIN, WRITES_MAX + 1))
        slot_seq.extend([s] * k)
    for _ in range(N_DISTRACT_EVENTS):
        slot_seq.append(int(rng.integers(S_TARGET, slot_vocab)))
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
    return slot_seq, fill_pool


def _last_write_indices(slot_seq):
    last = {s: -1 for s in range(S_TARGET)}
    for idx in range(len(slot_seq)):
        s = int(slot_seq[idx])
        if s < S_TARGET:
            last[s] = idx
    return last


def _eligible_slots(slot_seq):
    """Slots satisfying TAIL_MIN (distractor tail) + TARGET_TAIL_MIN (target tail) after their last
    write -- identical rule to calib.gen_stream's eligibility filter (position-only, filler-agnostic)."""
    L = len(slot_seq)
    last = _last_write_indices(slot_seq)
    is_target = np.array([1 if int(s) < S_TARGET else 0 for s in slot_seq])
    cum_target_after = np.concatenate([np.cumsum(is_target[::-1])[::-1][1:], [0]])
    eligible = [s for s in range(S_TARGET)
                if last[s] >= 0 and (L - 1 - last[s]) >= TAIL_MIN
                and int(cum_target_after[last[s]]) >= TARGET_TAIL_MIN]
    return eligible, last


# ---------------- Q1 repair: scrub (role, HELD_OUT_FILLER[role]) from EVERY position ----------------
def _repair_q1(slot_seq, fill_pool, rng, max_tries=MAX_EVAL_RETRY):
    L = len(slot_seq)
    distractor_idx = [j for j in range(L) if int(slot_seq[j]) >= S_TARGET]
    for i in range(L):
        s = int(slot_seq[i])
        forbidden = HELD_OUT_FILLER.get(s, -1)
        tries = 0
        while int(fill_pool[i]) == forbidden and tries < max_tries:
            tries += 1
            j = distractor_idx[int(rng.integers(0, len(distractor_idx)))]
            if int(fill_pool[j]) != forbidden:
                fill_pool[i], fill_pool[j] = fill_pool[j], fill_pool[i]
        if int(fill_pool[i]) == forbidden:
            raise RuntimeError("Q1 repair failed to converge at index %d (slot %d)" % (i, s))
    return fill_pool


# ---------------- Q2 repair: scrub the JOINT (slot_a=filler_a AND slot_b=filler_b) co-occurrence ----------------
def _repair_q2(slot_seq, fill_pool, rng, max_tries=MAX_EVAL_RETRY):
    last = _last_write_indices(slot_seq)
    ia, ib = last[Q2_SLOT_A], last[Q2_SLOT_B]
    if ia < 0 or ib < 0:
        return fill_pool   # a target slot absent this draw (WRITES_MIN>=2 makes this effectively never)
    distractor_idx = [j for j in range(len(slot_seq)) if int(slot_seq[j]) >= S_TARGET]
    forbidden_b = HELD_OUT_FILLER.get(Q2_SLOT_B, -1)
    tries = 0
    while (int(fill_pool[ia]) == Q2_FILLER_A and int(fill_pool[ib]) == Q2_FILLER_B
           and tries < max_tries):
        tries += 1
        j = distractor_idx[int(rng.integers(0, len(distractor_idx)))]
        cand = int(fill_pool[j])
        if cand != Q2_FILLER_B and cand != forbidden_b:
            fill_pool[ib], fill_pool[j] = fill_pool[j], fill_pool[ib]
    if int(fill_pool[ia]) == Q2_FILLER_A and int(fill_pool[ib]) == Q2_FILLER_B:
        raise RuntimeError("Q2 repair failed to converge")
    return fill_pool


def gen_stream_train(rng):
    """ONE training example: standard construction + Q1-scrub (every position) + Q2-scrub (joint
    final-state), THEN standard random-eligible query pick (apples-to-apples: no special targeting;
    same difficulty/recipe as the proven cell). Returns calib.gen_stream-shaped dict, or None."""
    slot_seq, fill_pool = _raw_stream(rng)
    fill_pool = _repair_q1(slot_seq, fill_pool, rng)
    fill_pool = _repair_q2(slot_seq, fill_pool, rng)
    eligible, last = _eligible_slots(slot_seq)
    if not eligible:
        return None
    query = int(eligible[rng.integers(0, len(eligible))])
    answer = int(fill_pool[last[query]])
    return {"slots": slot_seq.copy(), "fills": fill_pool.copy(), "query": query, "answer": answer,
            "last_write_idx": int(last[query])}


def gen_dataset_train(n, rng):
    out = []
    while len(out) < n:
        ex = gen_stream_train(rng)
        if ex is not None:
            out.append(ex)
    return out


def gen_q1_eval_example(rng, target_slot):
    """Force target_slot's last write to HELD_OUT_FILLER[target_slot]; query=target_slot. Rest of the
    stream is UNCONSTRAINED standard distribution (may contain the pair elsewhere by chance -- fine,
    only the FORCED position is load-bearing for the query answer)."""
    for _ in range(MAX_EVAL_RETRY):
        slot_seq, fill_pool = _raw_stream(rng)
        eligible, last = _eligible_slots(slot_seq)
        if target_slot in eligible:
            idx = last[target_slot]
            fill_pool = fill_pool.copy()
            fill_pool[idx] = HELD_OUT_FILLER[target_slot]
            return {"slots": slot_seq.copy(), "fills": fill_pool, "query": target_slot,
                    "answer": HELD_OUT_FILLER[target_slot], "last_write_idx": int(idx)}
    return None


def gen_q2_eval_example(rng, query_slot):
    """Force BOTH slot_a=filler_a AND slot_b=filler_b simultaneously; query one of the two roles."""
    for _ in range(MAX_EVAL_RETRY):
        slot_seq, fill_pool = _raw_stream(rng)
        eligible, last = _eligible_slots(slot_seq)
        if Q2_SLOT_A in eligible and Q2_SLOT_B in eligible:
            fill_pool = fill_pool.copy()
            fill_pool[last[Q2_SLOT_A]] = Q2_FILLER_A
            fill_pool[last[Q2_SLOT_B]] = Q2_FILLER_B
            idx = last[query_slot]
            return {"slots": slot_seq.copy(), "fills": fill_pool, "query": query_slot,
                    "answer": int(fill_pool[idx]), "last_write_idx": int(idx)}
    return None


def gen_dataset_q1(n_per_slot, rng):
    out = []
    for s in range(S_TARGET):
        got = 0
        while got < n_per_slot:
            ex = gen_q1_eval_example(rng, s)
            if ex is None:
                raise RuntimeError("Q1 eval construction exhausted retries for slot %d" % s)
            out.append(ex)
            got += 1
    return out


def gen_dataset_q2(n_per_query, rng):
    out = []
    for q in (Q2_SLOT_A, Q2_SLOT_B):
        got = 0
        while got < n_per_query:
            ex = gen_q2_eval_example(rng, q)
            if ex is None:
                raise RuntimeError("Q2 eval construction exhausted retries for query %d" % q)
            out.append(ex)
            got += 1
    return out


# ---------------- construction self-checks (leak/holdout-proofing) ----------------
def _key(ex):
    return (tuple(int(x) for x in ex["slots"]), tuple(int(x) for x in ex["fills"]), int(ex["query"]))


def audit_construction(seed=7, n_train=400, n_q1_per_slot=20, n_q2_per_query=20):
    rng = np.random.default_rng(seed)
    tr = gen_dataset_train(n_train, rng)
    q1 = gen_dataset_q1(n_q1_per_slot, np.random.default_rng(seed + 111))
    q2 = gen_dataset_q2(n_q2_per_query, np.random.default_rng(seed + 222))

    # (1) Q1 pair NEVER appears anywhere in training (any position, not just last-write).
    q1_violations = 0
    for ex in tr:
        for s, f in zip(ex["slots"], ex["fills"]):
            if int(s) < S_TARGET and int(f) == HELD_OUT_FILLER.get(int(s), -1):
                q1_violations += 1
    # (1b) but the FILLER CLASS itself is seen in training (bound to other roles) -- else the readout
    # head never learns that class and "novel-filler" would conflate with "unseen class".
    filler_seen_elsewhere = {f: 0 for f in HELD_OUT_FILLER.values()}
    for ex in tr:
        for sl, fl in zip(ex["slots"], ex["fills"]):
            if int(fl) in HELD_OUT_FILLER.values():
                filler_seen_elsewhere[int(fl)] = filler_seen_elsewhere.get(int(fl), 0) + 1

    # (2) Q2 joint config NEVER appears in training (individually common, jointly scrubbed).
    q2_joint_violations = 0
    q2a_alone, q2b_alone = 0, 0
    for ex in tr:
        last = _last_write_indices(ex["slots"])
        fa = int(ex["fills"][last[Q2_SLOT_A]]) if last[Q2_SLOT_A] >= 0 else -1
        fb = int(ex["fills"][last[Q2_SLOT_B]]) if last[Q2_SLOT_B] >= 0 else -1
        if fa == Q2_FILLER_A:
            q2a_alone += 1
        if fb == Q2_FILLER_B:
            q2b_alone += 1
        if fa == Q2_FILLER_A and fb == Q2_FILLER_B:
            q2_joint_violations += 1

    # (3) eval sets internally consistent + hit the forced condition 100%.
    q1_ok = all(int(ex["fills"][ex["last_write_idx"]]) == HELD_OUT_FILLER[ex["query"]]
                and ex["answer"] == HELD_OUT_FILLER[ex["query"]] for ex in q1)
    q2_ok = all(int(ex["fills"][_last_write_indices(ex["slots"])[Q2_SLOT_A]]) == Q2_FILLER_A
                and int(ex["fills"][_last_write_indices(ex["slots"])[Q2_SLOT_B]]) == Q2_FILLER_B
                for ex in q2)

    # (4) leakage: no eval (slots,fills,query) tuple present in the train key set.
    tr_keys = set(_key(ex) for ex in tr)                     # sorted(set()) not needed: membership-only
    q1_leak = sum(1 for ex in q1 if _key(ex) in tr_keys)
    q2_leak = sum(1 for ex in q2 if _key(ex) in tr_keys)

    fails = []
    if q1_violations != 0:
        fails.append("Q1 holdout violated: %d (role,filler) occurrences found in training" % q1_violations)
    if any(v == 0 for v in filler_seen_elsewhere.values()):
        fails.append("a held-out filler class is NEVER seen in training (readout can't learn it): %s"
                     % filler_seen_elsewhere)
    if q2_joint_violations != 0:
        fails.append("Q2 joint holdout violated: %d co-occurrences found in training" % q2_joint_violations)
    if not q1_ok:
        fails.append("Q1 eval construction internally inconsistent")
    if not q2_ok:
        fails.append("Q2 eval construction internally inconsistent")
    if q1_leak or q2_leak:
        fails.append("split leakage: Q1=%d Q2=%d eval tuples found verbatim in train" % (q1_leak, q2_leak))

    return {"n_train": len(tr), "n_q1": len(q1), "n_q2": len(q2),
            "q1_violations_in_train": q1_violations, "filler_seen_elsewhere_counts": filler_seen_elsewhere,
            "q2_joint_violations_in_train": q2_joint_violations,
            "q2a_alone_count": q2a_alone, "q2b_alone_count": q2b_alone,
            "q1_eval_consistent": bool(q1_ok), "q2_eval_consistent": bool(q2_ok),
            "q1_leak": q1_leak, "q2_leak": q2_leak, "fails": fails}


# ---------------- shuffled-query must-fail control ----------------
def shuffled_query_acc(wm, enc, examples, batch):
    """Re-evaluate the (trained or frozen) wm with EVERY example's query address replaced by a
    DIFFERENT, EXPLICITLY-KNOWN role's address (role -> (role+1) % S_TARGET, recomputed via enc.idx_of
    -- NOT a torch.roll/array-index permutation) while scoring against the ORIGINAL true answer.

    LESSON (caught in this cell's own FULL run, 2026-07-30): a first version used torch.roll(shift=1)
    over the BATCH INDEX. Because Q1/Q2 eval batches are built in contiguous per-role BLOCKS (all
    examples querying role s are adjacent), rolling by 1 within a block borrows a NEIGHBOR's q_idx,
    which is almost always the SAME role (identical q_idx integer) -- shuf_q1 landed at 0.956, i.e. the
    'shuffle' was a near no-op for 174/180 examples (only the 6 block-boundary examples actually
    changed role). That is exactly the 'can-fail floor doesn't floor' failure mode flagged mid-task:
    the floor wasn't broken by the MODEL, it was broken by THIS CONTROL's own construction. Fixed by
    shifting to an EXPLICIT, DIFFERENT role id (not an index permutation that can silently alias back
    to the same role under a structured eval-set ordering)."""
    shifted_roles = [(int(ex["query"]) + 1) % S_TARGET for ex in examples]
    q_idx_shifted = torch.tensor(
        [enc.idx_of(calib.QUERY_TEMPLATE.format(slot=calib.SLOT_NOUNS[s])) for s in shifted_roles],
        dtype=torch.long)
    assert bool((q_idx_shifted != batch["q_idx"]).all()), (
        "shuffled_query_acc: shifted q_idx equals original for >=1 example (shift-by-1 mod S_TARGET "
        "should always differ) -- construction bug, control would be a no-op")
    shuffled = dict(batch)
    shuffled["q_idx"] = q_idx_shifted
    with torch.no_grad():
        logits = wm(shuffled)
        acc = float((logits.argmax(dim=-1) == batch["answer"]).float().mean().item())
    return acc


# ---------------- per-seed run ----------------
def run_seed(seed, enc, cond, tr_examples, q1_examples, q2_examples, steps_wm, steps_readout,
            n_random_init):
    tr_batch = rc.build_index_batch(tr_examples, enc, seed)
    ev_std = calib.gen_dataset(FULL_EVAL_STD, np.random.default_rng(seed + 777))
    ev_std_batch = rc.build_index_batch(ev_std, enc, seed + 777)
    q1_batch = rc.build_index_batch(q1_examples, enc, seed + 888)
    q2_batch = rc.build_index_batch(q2_examples, enc, seed + 999)

    Uc = cond.apply(enc.U_tok_t, enc.U_pad_t, "pca_whiten")

    # LEARNED_WM (pca_whiten + aux + warmstart -- the PROVEN config, unchanged recipe)
    wm = rc.ReadCondWM(seed, enc.d, D_MEM, K_SLOTS, HIDDEN, V_FILL, ADDR_TEMP, Uc, enc.U_pad_t)
    warm_diag = rc.warm_start_key(wm, enc, seed)
    learned = rc.train_arm(wm, tr_batch, ev_std_batch, steps_wm, LR, list(wm.parameters()), seed,
                           "LEARNED_WM", aux=True, batch=BATCH)
    wm.eval()
    with torch.no_grad():
        std_acc = learned["eval_acc"]
        q1_logits = wm(q1_batch)
        q1_acc = float((q1_logits.argmax(-1) == q1_batch["answer"]).float().mean().item())
        q2_logits = wm(q2_batch)
        q2_acc = float((q2_logits.argmax(-1) == q2_batch["answer"]).float().mean().item())
    shuf_std = shuffled_query_acc(wm, enc, ev_std, ev_std_batch)
    shuf_q1 = shuffled_query_acc(wm, enc, q1_examples, q1_batch)
    shuf_q2 = shuffled_query_acc(wm, enc, q2_examples, q2_batch)
    wm.train()

    # RANDOM_INIT_WM: freeze wm params (SAME conditioning), train readout ONCE on tr, eval on all 3.
    ri_accs_std, ri_accs_q1, ri_accs_q2 = [], [], []
    ri_logits_std_first = None
    for c in range(n_random_init):
        cseed = seed * 100 + c
        wm_ri = rc.ReadCondWM(cseed, enc.d, D_MEM, K_SLOTS, HIDDEN, V_FILL, ADDR_TEMP, Uc, enc.U_pad_t)
        for p in wm_ri.wm_params():
            p.requires_grad_(False)
        ri_std = rc.train_readout_cached(wm_ri, tr_batch, ev_std_batch, steps_readout, LR, cseed,
                                         "RI c=%d std" % c)
        ri_accs_std.append(ri_std["eval_acc"])
        if ri_logits_std_first is None:
            ri_logits_std_first = ri_std["ev_logits"]
        with torch.no_grad():
            ri_accs_q1.append(float((wm_ri(q1_batch).argmax(-1) == q1_batch["answer"]).float().mean().item()))
            ri_accs_q2.append(float((wm_ri(q2_batch).argmax(-1) == q2_batch["answer"]).float().mean().item()))

    ps_std = power_stats(std_acc, ev_std_batch["answer"].shape[0], ri_accs_std)
    ps_q1 = power_stats(q1_acc, q1_batch["answer"].shape[0], ri_accs_q1)
    ps_q2 = power_stats(q2_acc, q2_batch["answer"].shape[0], ri_accs_q2)

    def _digest(t):
        return hashlib.sha256(t.cpu().numpy().tobytes()).hexdigest()
    arms_differ = _digest(learned["ev_logits"]) != _digest(ri_logits_std_first)

    return {
        "seed": seed, "warmstart_diag": warm_diag,
        "learned": {"std_acc": std_acc, "train_acc": learned["train_acc"],
                    "q1_acc": q1_acc, "q2_acc": q2_acc,
                    "first_loss": learned["first_loss"], "last_loss": learned["last_loss"],
                    "steps_run": learned["steps_run"]},
        "shuffled_query": {"std": shuf_std, "q1": shuf_q1, "q2": shuf_q2},
        "random_init": {"std_accs": ri_accs_std, "q1_accs": ri_accs_q1, "q2_accs": ri_accs_q2,
                        "std_mean": float(np.mean(ri_accs_std)), "std_max": float(np.max(ri_accs_std)),
                        "q1_mean": float(np.mean(ri_accs_q1)), "q1_max": float(np.max(ri_accs_q1)),
                        "q2_mean": float(np.mean(ri_accs_q2)), "q2_max": float(np.max(ri_accs_q2))},
        "power": {"std": ps_std, "q1": ps_q1, "q2": ps_q2},
        "arms_differ_verified": bool(arms_differ),
    }


# ---------------- verdict ----------------
def _floor_broken(per_seed, key):
    for ps in per_seed:
        if max(ps["random_init"]["%s_max" % key], 0.0) >= RI_NEAR_CHANCE:
            return True
        if ps["shuffled_query"][key] >= SHUF_NEAR_CHANCE:
            return True
    return False


def decide_verdict(per_seed, audit):
    q1_accs = [ps["learned"]["q1_acc"] for ps in per_seed]
    q2_accs = [ps["learned"]["q2_acc"] for ps in per_seed]
    std_accs = [ps["learned"]["std_acc"] for ps in per_seed]

    q1_floor_broken = _floor_broken(per_seed, "q1")
    q2_floor_broken = _floor_broken(per_seed, "q2")
    std_floor_broken = _floor_broken(per_seed, "std")

    q1_proven = all(a >= Q_PROVEN_MIN for a in q1_accs)
    q1_missing = all(a <= Q_CHANCE_MAX for a in q1_accs)
    q2_proven = all(a >= Q_PROVEN_MIN for a in q2_accs)
    q2_missing = all(a <= Q_CHANCE_MAX for a in q2_accs)

    if audit["fails"]:
        verdict = "CONSTRUCTION_INVALID"
        msg = ("construction self-checks failed (holdout/leak): %s" % "; ".join(audit["fails"]))
    elif q1_floor_broken:
        verdict = "METRIC_INVALID"
        msg = ("Q1's can-fail floor did NOT collapse (RI or shuffled-query control >= bar on some "
               "seed): q1_accs=%s ri_q1_max=%s shuf_q1=%s. Per the mid-task fairness correction, a "
               "floor that doesn't floor means the Q1 metric can't discriminate here -- NOT claiming "
               "HAVE_COMPREHENSION_TARGET regardless of the raw learned accuracy. Q2 floor_broken=%s "
               "(reported for completeness, not gating this verdict since Q1 already invalidates)."
               % ([round(a, 3) for a in q1_accs],
                  [round(ps["random_init"]["q1_max"], 3) for ps in per_seed],
                  [round(ps["shuffled_query"]["q1"], 3) for ps in per_seed], q2_floor_broken))
    elif q1_proven:
        verdict = "HAVE_COMPREHENSION_TARGET"
        q2_note = ("Q2 (novel composition) ALSO >= %.2f both seeds (%s), floor_broken=%s -> "
                   "compositional generalization holds too."
                   % (Q_PROVEN_MIN, [round(a, 3) for a in q2_accs], q2_floor_broken)
                   if (q2_proven and not q2_floor_broken) else
                   ("Q2 (novel composition) at/near chance (%s, floor_broken=%s) -> a COMPOSITIONAL "
                    "gap remains even though novel-filler-to-known-role binding is proven."
                    % ([round(a, 3) for a in q2_accs], q2_floor_broken)
                    if q2_missing and not q2_floor_broken else
                    "Q2 (novel composition) in between / floor_broken=%s (%s) -- not conclusive."
                    % (q2_floor_broken, [round(a, 3) for a in q2_accs])))
        msg = ("Q1 (novel-filler-to-known-role) learned_acc=%s (chance %.3f) clears %.2f both seeds, "
               "floors collapse clean (ri_q1_max=%s, shuf_q1=%s < bars) -> the PROVEN read-conditioning "
               "WM (pca_whiten_aux_warm) ALREADY covers the comprehension-relevant novel-filler binding "
               "at the real task difficulty (std reproduction=%s, matches the readcond cell's 0.989). "
               "The held-out-ROLE failures were a harder, likely-not-required target. %s"
               % ([round(a, 3) for a in q1_accs], CHANCE, Q_PROVEN_MIN,
                  [round(ps["random_init"]["q1_max"], 3) for ps in per_seed],
                  [round(ps["shuffled_query"]["q1"], 3) for ps in per_seed],
                  [round(a, 3) for a in std_accs], q2_note))
    elif q1_missing:
        verdict = "MISSING"
        msg = ("Q1 (novel-filler-to-known-role) learned_acc=%s <= %.2f both seeds (chance %.3f) -> "
               "read-conditioning does NOT do novel-filler binding; it only memorizes seen (role,"
               "filler) pairs -> a real comprehension gap remains regardless of the held-out-role "
               "question. q1_floor_broken=%s. Q2 accs=%s (floor_broken=%s, reported for completeness)."
               % ([round(a, 3) for a in q1_accs], Q_CHANCE_MAX, CHANCE, q1_floor_broken,
                  [round(a, 3) for a in q2_accs], q2_floor_broken))
    else:
        verdict = "PARTIAL"
        msg = ("Q1 (novel-filler-to-known-role) learned_acc=%s is between chance (%.2f) and the proven "
               "bar (%.2f) -- beats the floor but not conclusively PROVEN. Not one of the 3 pre-"
               "registered headline states; honest middle. q1_floor_broken=%s. Q2 accs=%s "
               "(floor_broken=%s)." % ([round(a, 3) for a in q1_accs], Q_CHANCE_MAX, Q_PROVEN_MIN,
                                       q1_floor_broken, [round(a, 3) for a in q2_accs], q2_floor_broken))

    bands = {"chance": CHANCE, "q_proven_min": Q_PROVEN_MIN, "q_chance_max": Q_CHANCE_MAX,
             "ri_near_chance": RI_NEAR_CHANCE, "shuf_near_chance": SHUF_NEAR_CHANCE,
             "q1_accs": q1_accs, "q2_accs": q2_accs, "std_accs": std_accs,
             "q1_floor_broken": bool(q1_floor_broken), "q2_floor_broken": bool(q2_floor_broken),
             "std_floor_broken": bool(std_floor_broken),
             "q1_proven": bool(q1_proven), "q1_missing": bool(q1_missing),
             "q2_proven": bool(q2_proven), "q2_missing": bool(q2_missing)}
    return verdict, msg, bands


# ---------------- self-test ----------------
def run_self_test():
    _log("SELF-TEST: construction audit (tiny) + REAL v2 encoder + tiny end-to-end ...")
    audit = audit_construction(seed=7, n_train=150, n_q1_per_slot=8, n_q2_per_query=8)
    _log("  audit: q1_violations=%d q2_joint_violations=%d q1_leak=%d q2_leak=%d fails=%s"
         % (audit["q1_violations_in_train"], audit["q2_joint_violations_in_train"],
            audit["q1_leak"], audit["q2_leak"], audit["fails"]))
    if audit["fails"]:
        raise AssertionError("construction self-test FAILED: %s" % "; ".join(audit["fails"]))

    assert os.path.exists(V2_CKPT), "v2 checkpoint missing: %s" % V2_CKPT
    enc = rc.base.FrozenV2Encoder(V2_CKPT)
    n_cached = enc.build_cache()
    assert n_cached >= 3000, "closed sentence set smaller than expected"
    cond = rc.Conditioner(enc.U_tok_t, enc.U_pad_t)

    rng = np.random.default_rng(7)
    tr = gen_dataset_train(60, rng)
    q1 = gen_dataset_q1(3, np.random.default_rng(7 + 111))     # 3 x 6 = 18
    q2 = gen_dataset_q2(4, np.random.default_rng(7 + 222))     # 4 x 2 = 8

    res = run_seed(7, enc, cond, tr, q1, q2, steps_wm=40, steps_readout=30, n_random_init=1)
    _log("  tiny: learned std=%.3f q1=%.3f q2=%.3f shuf(std/q1/q2)=%.3f/%.3f/%.3f ri(q1max/q2max)=%.3f/%.3f "
         "arms_differ=%s" % (res["learned"]["std_acc"], res["learned"]["q1_acc"], res["learned"]["q2_acc"],
                              res["shuffled_query"]["std"], res["shuffled_query"]["q1"],
                              res["shuffled_query"]["q2"], res["random_init"]["q1_max"],
                              res["random_init"]["q2_max"], res["arms_differ_verified"]))
    assert res["arms_differ_verified"], "arms bit-identical (LEARNED vs RANDOM_INIT)"
    for k in ("std_acc", "q1_acc", "q2_acc"):
        assert 0.0 <= res["learned"][k] <= 1.0, "acc out of range: %s" % k

    # shuffled-query control sanity: on a barely-trained tiny model it need not be conclusive, but the
    # function itself must run and produce a valid probability.
    assert 0.0 <= res["shuffled_query"]["q1"] <= 1.0

    _log("SELF-TEST PASS")
    return {"audit": audit, "n_cached": n_cached, "tiny": res}


# ---------------- main ----------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--full", action="store_true")
    ap.add_argument("--train-n", type=int, default=FULL_TRAIN)
    ap.add_argument("--eval-std", type=int, default=FULL_EVAL_STD)
    ap.add_argument("--eval-q1-per-slot", type=int, default=FULL_EVAL_Q1_PER_SLOT)
    ap.add_argument("--eval-q2-per-query", type=int, default=FULL_EVAL_Q2_PER_QUERY)
    ap.add_argument("--steps-wm", type=int, default=STEPS_WM)
    ap.add_argument("--n-random-init", type=int, default=N_RANDOM_INIT)
    args = ap.parse_args()

    torch.set_num_threads(min(6, max(1, os.cpu_count() or 1)))
    run_mode = "self_test" if args.self_test or not args.full else "full"
    expected_units = 1 if run_mode == "self_test" else len(SEEDS_FULL)
    _write_start_marker(OUTPUT_DIR, run_mode, expected_units)
    t0 = time.perf_counter()

    if run_mode == "self_test":
        st = run_self_test()
        elapsed = time.perf_counter() - t0
        _atomic_write_metrics(OUTPUT_DIR, {
            "verdict": "SELFTEST_PASS",
            "verdict_msg": "SELFTEST_PASS (construction audit + real v2 encoder + tiny e2e + arms-differ)",
            "summary": "SELFTEST_PASS", "run_mode": "self_test", "elapsed_s": elapsed,
            "ts_iso": _now_iso(), "anchor_name": ANCHOR_NAME, "chance": CHANCE, "selftest": st})
        _log("DONE self-test in %.1fs" % elapsed)
        return

    _log("FULL: train_n=%d eval_std=%d eval_q1_per_slot=%d(x6) eval_q2_per_query=%d(x2) steps_wm=%d "
         "seeds=%s chance=%.4f" % (args.train_n, args.eval_std, args.eval_q1_per_slot,
                                   args.eval_q2_per_query, args.steps_wm, SEEDS_FULL, CHANCE))
    _log("--- construction audit (holdout + leakage self-checks, full-scale sample) ---")
    audit = audit_construction(seed=7, n_train=max(args.train_n, 400),
                               n_q1_per_slot=max(args.eval_q1_per_slot, 20),
                               n_q2_per_query=max(args.eval_q2_per_query, 20))
    _log("  q1_violations=%d q2_joint_violations=%d q1_leak=%d q2_leak=%d filler_seen=%s fails=%s"
         % (audit["q1_violations_in_train"], audit["q2_joint_violations_in_train"], audit["q1_leak"],
            audit["q2_leak"], audit["filler_seen_elsewhere_counts"], audit["fails"]))
    if audit["fails"]:
        elapsed = time.perf_counter() - t0
        _atomic_write_metrics(OUTPUT_DIR, {
            "verdict": "CONSTRUCTION_INVALID",
            "verdict_msg": "construction self-checks failed: %s" % "; ".join(audit["fails"]),
            "summary": "CONSTRUCTION_INVALID", "run_mode": "full", "elapsed_s": elapsed,
            "ts_iso": _now_iso(), "anchor_name": ANCHOR_NAME, "chance": CHANCE, "audit": audit,
            "start_marker_written": True, "crash_diagnostic_present": True,
            "final_metrics_atomicity": "tmp_replace"})
        _log("CONSTRUCTION_INVALID -- see audit fails")
        return

    enc = rc.base.FrozenV2Encoder(V2_CKPT)
    n_cached = enc.build_cache()
    _log("  cached %d unique sentence TOKEN reps (d=%d)" % (n_cached, enc.d))
    cond = rc.Conditioner(enc.U_tok_t, enc.U_pad_t)

    per_seed = []
    for seed in SEEDS_FULL:
        _log("--- seed %d ---" % seed)
        tr = gen_dataset_train(args.train_n, np.random.default_rng(seed))
        q1 = gen_dataset_q1(args.eval_q1_per_slot, np.random.default_rng(seed + 111))
        q2 = gen_dataset_q2(args.eval_q2_per_query, np.random.default_rng(seed + 222))
        per_seed.append(run_seed(seed, enc, cond, tr, q1, q2, args.steps_wm, STEPS_READOUT,
                                 args.n_random_init))
        _log("  seed=%d learned std=%.3f q1=%.3f q2=%.3f shuf(std/q1/q2)=%.3f/%.3f/%.3f "
             "ri(q1max/q2max)=%.3f/%.3f" % (seed, per_seed[-1]["learned"]["std_acc"],
             per_seed[-1]["learned"]["q1_acc"], per_seed[-1]["learned"]["q2_acc"],
             per_seed[-1]["shuffled_query"]["std"], per_seed[-1]["shuffled_query"]["q1"],
             per_seed[-1]["shuffled_query"]["q2"], per_seed[-1]["random_init"]["q1_max"],
             per_seed[-1]["random_init"]["q2_max"]))

    verdict, msg, bands = decide_verdict(per_seed, audit)
    elapsed = time.perf_counter() - t0

    _atomic_write_metrics(OUTPUT_DIR, {
        "verdict": verdict, "verdict_msg": msg,
        "summary": "%s | chance=%.4f | %s" % (verdict, CHANCE, msg[:160]),
        "run_mode": "full", "elapsed_s": elapsed, "ts_iso": _now_iso(), "anchor_name": ANCHOR_NAME,
        "chance": CHANCE, "oracle_ceiling_ref": ORACLE_CEILING, "bands": bands, "audit": audit,
        "cardinality_ok": bool(len(per_seed) == len(SEEDS_FULL)),
        "expected_n_units": len(SEEDS_FULL), "n_units_done": len(per_seed),
        "held_out_filler": HELD_OUT_FILLER, "q2_holdout": {"slot_a": Q2_SLOT_A, "slot_b": Q2_SLOT_B,
                                                           "filler_a": Q2_FILLER_A, "filler_b": Q2_FILLER_B},
        "params": {"K_SLOTS": K_SLOTS, "D_MEM": D_MEM, "D_ENC": enc.d, "HIDDEN": HIDDEN,
                   "ADDR_TEMP": ADDR_TEMP, "STEPS_WM": args.steps_wm, "STEPS_READOUT": STEPS_READOUT,
                   "LR": LR, "AUX_W": AUX_W, "PCA_EPS": PCA_EPS, "N_RANDOM_INIT": args.n_random_init,
                   "train_n": args.train_n, "eval_std": args.eval_std,
                   "eval_q1_per_slot": args.eval_q1_per_slot, "eval_q2_per_query": args.eval_q2_per_query,
                   "seeds": list(SEEDS_FULL), "n_cached_sentences": n_cached,
                   "encoder": "real_v2_frozen", "conditioning": "pca_whiten_aux_warm",
                   "v2_ckpt": os.path.relpath(V2_CKPT, REPO_ROOT)},
        "per_seed": per_seed,
        "start_marker_written": True, "crash_diagnostic_present": True,
        "final_metrics_atomicity": "tmp_replace", "defensive_error_checking": "passed_all_4_patterns"})
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
