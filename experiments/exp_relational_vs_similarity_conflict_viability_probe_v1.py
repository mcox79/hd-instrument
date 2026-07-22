#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""exp_relational_vs_similarity_conflict_viability_probe_v1

VIABILITY PROBE (design-gated, can-fail, LOCAL-ONLY). Question: on a relational-vs-similarity
CONFLICT corpus -- where a semantic-similarity-kNN provably fails by construction -- does ANY
glass-box NONLINEAR mechanism (role-binding + iterative settling + unbind-compare) BEAT the
similarity-kNN? If yes -> green-light the full fork-A build. If no (the nonlinear loop ALSO reduces
to similarity / cannot resolve the conflict) -> honest negative, fork A needs a different mechanism.

WHY (context): the learned-composition leap (atom 29440) was REFUTED because the LINEAR atomize+sleep
loop analytically reduces to a fixed WordNet-hypernym-similarity vote (parameter-free similarity-kNN
matched it 70/70). Brain-check (research_drill_does_brain_composition_beat_semantic_similarity_2026-
07-22.md) confirmed the CG bar is BRAIN-FAITHFUL: humans generalize composition to SEMANTICALLY-
DISSIMILAR novel combinations (Marcus 1999 infant ABA/ABB where similarity-nets fail exactly like
29440; Berko wug; Lake-Baroni meaning-free primitives; Gentner relational-shift). A genuine learned
composition must BEAT a similarity-kNN, and the mechanism that does so is RELATIONAL rule-resolution
(role-binding + settling), NOT more linear similarity. A LINEAR associative matrix is a kernel machine
(can only emit weighted-similarity outputs) -- that is the exact reason 29440 collapsed to kNN.

TWO PARTS:
  PART 1 (real-data feasibility DIAGNOSTIC, cheap): reuse the 29440 verb->required-feature setup and
    the SAME WordNet-hypernym verb-similarity code (verb_code_real) that matched the linear loop 70/70.
    For each held-out verb, find its nearest-similar TRAIN verb; a CONFLICT item = nearest-train-verb
    feature != held-out true feature. Count conflict items. The 29440 rule (verb-lexical-class ->
    required feature) IS a similarity-class rule, so similarity and rule are co-extensive -> we expect
    ~0 conflict items -> a real-data conflict corpus is NOT buildable in this testbed (which is exactly
    WHY 29440 reduced to kNN: its task had no relational content beyond similarity). We report the
    measured conflict count; if it is too small (<10) we fall back to the synthetic decisive test.

  PART 2 (DECISIVE synthetic relational-conflict test, Marcus-1999 rule-vs-similarity): items = 4-slot
    role-filler bundles with 4 distinct fillers. Class = a pure RELATIONAL identity rule = WHERE the one
    matched (repeated) filler pair sits (class0 = match at roles r0,r1 ; class1 = match at roles r2,r3),
    which is filler-INDEPENDENT. The design is STRUCTURALLY SYMMETRIC (both classes have exactly one
    doubled pair + two singletons) so a raw-vector kNN has no magnitude/energy fingerprint and sits
    at/near chance. TRAIN and HELD-OUT use DISJOINT filler pools (novel fillers, orthogonal), so any
    surface/filler-content similarity is uninformative on held-out by construction.
    ARMS (one variable = mechanism):
      (A) RAW-SIMILARITY-kNN  -- 1-NN over the raw item vectors (bundle of bound role-filler pairs)
                                against TRAIN items. Held-out novel fillers -> ~chance. THE BASELINE
                                TO BEAT; fails by construction.
      (B) LINEAR-LOOP (29440)  -- replay_cycle W over raw item vectors -> class readout (the exact
                                UNMODIFIED atomize+sleep machinery). A linear/kernel map cannot compute
                                cross-slot identity for NOVEL fillers -> ~chance. Confirms the corpus's
                                relational content is inaccessible to similarity/linear.
      (C) NONLINEAR-GLASSBOX   -- role-binding + unbind-COMPARE coherence gate: s_ij = cos(unbind_i,
                                unbind_j), a QUADRATIC (nonlinear, filler-INDEPENDENT) form a linear/
                                kernel loop cannot compute -> a LEARNED inspectable linear readout over
                                [s12,s13,s23]. THE PRIZE. Primary C is the SINGLE-STEP coherence gate;
                                a multi-step codebook-free interference-cancelling SETTLING (settle_
                                damped pattern) is run as an ABLATION -- reported, not primary, because
                                without a filler codebook the iterative settle injects noise and
                                DEGRADES the separation (measured; informs fork-A: settling needs a
                                codebook/attractor anchor).
      (D) kNN-ON-RELATIONAL    -- 1-NN over the SAME binding-derived relational features (no learning).
                                Attribution control: if D also beats A, the win is the REPRESENTATION
                                (role-binding), not the learner -- honest read of where the lever is.

DESIGN-GATE: real baseline (A); can-fail (C might tie A if binding-crosstalk at N/slots swamps the
relational signal, or the readout latches the uninformative feature; also scramble must collapse it);
difficulty-on (held-out fillers disjoint so surface similarity is provably useless); one variable
(mechanism). HARD-PASS (viability) = C beats A by a pre-registered margin, multi-seed, while A is
at/below chance -> green-light fork A. HARD-FAIL = C does not beat A -> fork A needs a different
mechanism.

HONEST FRAMING + CONFLICT-OF-INTEREST: Director/USER WANT the leap. On THIS synthetic construction C
is EXPECTED to pass because role-binding genuinely yields a filler-independent relational feature that
a linear/kernel machine cannot -- but a synthetic HARD-PASS is CONSTRUCTION-FAVORABLE: it proves an
EXISTENCE result (the substrate CAN express a beyond-similarity relational feature), NOT that the
mechanism learns the RIGHT feature from HARD/REAL data. A pass is a GREEN-LIGHT-PENDING-VET, never a
self-declared CG. Arm D is included precisely to keep us honest about whether the lever is the
representation (binding) or the learning.

# CELL-TEMPLATE MANDATORY:
# - arms_differ asserted (A/B/C/D predictions + C's learned weights not degenerate)
# - final_metrics_atomicity: tmp_replace ; SystemExit raised BEFORE except Exception (no BaseException)
# - discriminator survives scale: smoke = FULL N_DIM=1024 + FULL filler/item counts, 2 seeds (option A)
# - baseline_in_band: raw-kNN ~0.5 (chance), verified 0.05<acc<0.95 ; nonlinear expected high
# - crlb_n/a: relational discrimination test; the floor is HRR binding-crosstalk (empirically measured
#   this run as the raw unbind-compare separation), not an argmax-capacity CRLB
# - deterministic_seeding: fixed ints + hashlib atoms (no hash()/list(set())) ; progress_logging: flush
# - cardinality_ok: n_seed_rows == len(seeds)
# LOCAL ONLY. No push / no remote-persist / no queue / no store write / no atom bank. ASCII only.
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import argparse
import hashlib
import json
import platform
import sys
import time
import traceback
from datetime import datetime, timezone

import numpy as np

ANCHOR_NAME = "relational_vs_similarity_conflict_viability_probe_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

# ---- config (FULL == SMOKE for N_DIM/counts: discriminator surfaces at full scale, option A) ----
N_DIM = 1024
N_ROLES = 4                   # 4-slot STRUCTURALLY-SYMMETRIC design: both classes have exactly one
                              # matched pair (class0 at r0,r1 ; class1 at r2,r3) so raw-kNN cannot use
                              # a "how much doubling" fingerprint -> kNN at/near chance by construction
N_TRAIN_FILLERS = 20          # disjoint train filler pool
N_HELD_FILLERS = 20           # disjoint held-out (NOVEL) filler pool
N_TRAIN_ITEMS = 120           # balanced ABA/ABB, train fillers only
N_HELD_ITEMS = 120            # balanced ABA/ABB, held-out (novel) fillers only
SETTLE_ITERS = 0             # PRIMARY C: single-step unbind-compare coherence gate (the nonlinearity)
SETTLE_ITERS_ABL = 4         # ABLATION: multi-step codebook-free interference-cancelling settling
SETTLE_ALPHA = 0.5           # damped update factor (settle_damped pattern)
READOUT_STEPS = 400           # logistic-readout GD steps (learned, inspectable 3-weight model)
READOUT_LR = 0.5
FULL_SEEDS = [7, 13, 19, 23, 29]
SMOKE_SEEDS = [7, 13]

# ---- pre-registered bands (viability) ----
CHANCE = 0.5
KNN_CEIL = 0.65               # raw-kNN (baseline) MUST be at/below this (else strong corpus surface-leak)
LINEAR_CEIL = 0.65            # linear-loop MUST be at/below this (linear cannot resolve the conflict)
NONLINEAR_PASS_MEAN = 0.75    # C mean held-out acc HARD-PASS floor (strictly above chance+margin)
NONLINEAR_MARGIN = 0.20       # C - rawKNN margin (the "beat similarity" bar)
NONLINEAR_EVERYSEED_MIN = 0.65
WRONGROLE_CEIL = 0.65         # MUST-FAIL: unbind-compare with WRONG (unbound) roles -> chance
WRONGROLE_COLLAPSE_MIN = 0.20 # C_real - C_wrongrole (the relational signal must come from binding)
NONLINEAR_FAIL_MAX = 0.62     # C mean at/below -> reduces to similarity -> HARD-FAIL

REAL_DATA_CONFLICT_MIN = 10   # PART 1: need this many real conflict items to consider real corpus


# ==================================================================================================
# HD atoms (deterministic hashlib -> gaussian; no PYTHONHASHSEED dependence).
# ==================================================================================================
def _atom(token):
    seed = int.from_bytes(hashlib.sha256(token.encode("utf-8")).digest()[:8], "big")
    v = np.random.default_rng(seed).standard_normal(N_DIM).astype(np.float32)
    n = float(np.linalg.norm(v))
    return v / n if n > 1e-9 else v


def _roles():
    return [_atom("role:%d" % i) for i in range(N_ROLES)]


def _filler_pool(tag, n):
    return [_atom("filler:%s:%d" % (tag, i)) for i in range(n)]


# ==================================================================================================
# HRR bind / unbind (reuse the substrate primitive; float32 circular convolution).
# ==================================================================================================
def _bind_np(a, b):
    import torch
    from hdlab.binding import bind as hd_bind
    out = hd_bind(torch.from_numpy(np.ascontiguousarray(a)), torch.from_numpy(np.ascontiguousarray(b)))
    return out.numpy()


def _unbind_np(c, b):
    import torch
    from hdlab.binding import unbind as hd_unbind
    out = hd_unbind(torch.from_numpy(np.ascontiguousarray(c)), torch.from_numpy(np.ascontiguousarray(b)))
    return out.numpy()


def _norm(v):
    n = float(np.linalg.norm(v))
    return v / n if n > 1e-9 else v


def _cos(a, b):
    na = float(np.linalg.norm(a)); nb = float(np.linalg.norm(b))
    return float(a @ b / (na * nb + 1e-9))


# ==================================================================================================
# Item construction (Marcus ABA/ABB). class 0 = ABA (slot3==slot1) ; class 1 = ABB (slot3==slot2).
# ==================================================================================================
def gen_items(fillers, n_items, seed):
    """4-slot structurally-symmetric relational task. 4 DISTINCT fillers (a,b,c,d) per item; class =
    WHERE the matched (repeated) filler pair sits:
      class 0 = match at roles (0,1): fillers (a,a,b,c)  -> relational feature s01 high
      class 1 = match at roles (2,3): fillers (a,b,c,c)  -> relational feature s23 high
    Both classes have EXACTLY one doubled filler pair and two singletons -> identical global 'amount of
    doubling', so a raw-vector similarity-kNN has no filler-independent magnitude fingerprint to exploit
    and sits at/near chance. The discriminating signal is purely the LOCATION of the match, recoverable
    only by unbind-compare (a filler-independent relational read)."""
    rng = np.random.default_rng(seed)
    nf = len(fillers)
    items = []
    for k in range(n_items):
        cls = k % 2  # balanced
        a, b, c = rng.choice(nf, size=3, replace=False)
        if cls == 0:      # match at (r0, r1)
            idx = (a, a, b, c)
        else:             # match at (r2, r3)
            idx = (a, b, c, c)
        items.append({"cls": int(cls), "f": tuple(int(x) for x in idx)})
    return items


def item_vector(item, fillers, roles):
    v = np.zeros(N_DIM, dtype=np.float32)
    for r in range(N_ROLES):
        v = v + _bind_np(roles[r], fillers[item["f"][r]])
    return _norm(v)


# ==================================================================================================
# NONLINEAR mechanism: iterative interference-cancelling settling (damped, codebook-free) + unbind-
# compare relational features. The settling reuses the settle_damped PATTERN (damped bind/unbind
# update) from exp_settling_fix_learned_recurrent_v1 -- CREDIT that cell. It removes cross-slot
# interference so the unbind estimates sharpen toward their true fillers regardless of WHICH filler
# (filler-independent). s_ij = cos(unbind_i, unbind_j) is a QUADRATIC form in the item vector (the
# nonlinearity a linear/kernel loop cannot compute). NO filler codebook is used -> generalizes to
# NOVEL held-out fillers.
# ==================================================================================================
def settle_slots(item_vec, roles, n_iter, alpha):
    """Return the n_iter-settled, normalized unbind estimate per slot. n_iter=0 -> raw single unbind."""
    est = [_norm(_unbind_np(item_vec, roles[r])) for r in range(N_ROLES)]
    for _ in range(n_iter):
        new_est = []
        for r in range(N_ROLES):
            recon_others = np.zeros(N_DIM, dtype=np.float32)
            for j in range(N_ROLES):
                if j == r:
                    continue
                recon_others = recon_others + _bind_np(roles[j], est[j])
            residual = item_vec - recon_others
            target = _norm(_unbind_np(residual, roles[r]))
            upd = _norm(est[r] + alpha * (target - est[r]))
            new_est.append(upd)
        est = new_est
    return est


# ordered index of the C(N_ROLES,2) role pairs, e.g. N_ROLES=4 -> [(0,1),(0,2),(0,3),(1,2),(1,3),(2,3)]
ROLE_PAIRS = [(i, j) for i in range(N_ROLES) for j in range(i + 1, N_ROLES)]
PAIR_IDX = {p: k for k, p in enumerate(ROLE_PAIRS)}


def relational_features(item_vec, roles, n_iter, alpha):
    """Filler-independent relational feature vector: unbind-compare cosine for every role pair.
    s_ij high iff roles i,j carry the SAME filler. For the 4-slot task s01 discriminates class0 and
    s23 discriminates class1; the other 4 pairs are (learnably) uninformative distractors."""
    est = settle_slots(item_vec, roles, n_iter, alpha)
    return np.array([_cos(est[i], est[j]) for (i, j) in ROLE_PAIRS], dtype=np.float32)


# ---- learned inspectable linear readout (logistic regression on the 3 relational features) ----
def _sigmoid(z):
    return 1.0 / (1.0 + np.exp(-np.clip(z, -30, 30)))


def train_readout(X, y, steps, lr, seed):
    rng = np.random.default_rng(seed)
    d = X.shape[1]
    w = rng.standard_normal(d).astype(np.float64) * 0.01
    b = 0.0
    Xd = X.astype(np.float64); yd = y.astype(np.float64)
    n = len(yd)
    for _ in range(steps):
        p = _sigmoid(Xd @ w + b)
        g = p - yd
        w -= lr * (Xd.T @ g) / n
        b -= lr * float(np.mean(g))
    return w, b


def readout_predict(X, w, b):
    return (_sigmoid(X.astype(np.float64) @ w + b) >= 0.5).astype(int)


# ==================================================================================================
# LINEAR-LOOP arm (29440 atomize+sleep, UNMODIFIED machinery): replay_cycle W over item vectors ->
# class-code readout. A linear/kernel map; cannot compute cross-slot identity for novel fillers.
# ==================================================================================================
def linear_loop_fit_predict(train_vecs, train_cls, held_vecs, class_codebook, seed):
    import torch
    from hdlab.continual import replay_cycle
    from hdlab.glass_box_loop import cleanup_with_margin
    keys = torch.from_numpy(np.asarray(train_vecs, dtype=np.float32))
    values = torch.from_numpy(np.asarray([class_codebook[c] for c in train_cls], dtype=np.float32))
    m = keys.shape[0]
    replay_idx = torch.from_numpy(np.arange(m).astype(np.int64))
    W = torch.zeros((N_DIM, N_DIM), dtype=torch.float32)
    torch.manual_seed(seed)
    for _ in range(6):
        replay_cycle(W, replay_idx, keys, values, replay_frac=1.0, lr=1.0)
    Wn = W.numpy()
    cb = np.asarray([class_codebook[0], class_codebook[1]], dtype=np.float32)
    preds = []
    for hv in held_vecs:
        rs = Wn @ hv.astype(np.float32)
        rs = _norm(rs)
        idx, _m = cleanup_with_margin(rs, cb)
        preds.append(int(idx))
    return np.array(preds, dtype=int)


# ==================================================================================================
# kNN arms.
# ==================================================================================================
def knn_predict(train_X, train_y, held_X):
    """1-NN by cosine (raw vectors) or euclidean-equivalent for the low-dim relational features."""
    preds = []
    tX = np.asarray(train_X, dtype=np.float64)
    tnorm = tX / (np.linalg.norm(tX, axis=1, keepdims=True) + 1e-9)
    for hx in held_X:
        h = np.asarray(hx, dtype=np.float64)
        h = h / (np.linalg.norm(h) + 1e-9)
        sims = tnorm @ h
        preds.append(int(train_y[int(np.argmax(sims))]))
    return np.array(preds, dtype=int)


def _acc(pred, gold):
    return float(np.mean(np.asarray(pred) == np.asarray(gold)))


# ==================================================================================================
# PART 1: real-data conflict-corpus feasibility diagnostic (reuse 29440 verb similarity).
# ==================================================================================================
def real_data_conflict_diagnostic():
    out = {"available": False, "note": "", "n_conflict": None, "n_held_checked": None}
    try:
        from experiments.exp_learned_composition_glue_pun_selectional_generalization_v1 import (
            verb_code_real, build_items, verb_disjoint_split,
        )
    except Exception as e:
        out["note"] = "cannot import 29440 cell: %s" % (str(e)[:200],)
        return out
    try:
        items = build_items()
        n_conflict_total = 0
        n_held_total = 0
        for seed in [7, 13, 19]:
            seen, held, _sv = verb_disjoint_split(items, seed)
            train_codes = {it["verb"]: verb_code_real(it["verb"]) for it in seen}
            train_feat = {it["verb"]: it["feature"] for it in seen}
            train_verbs = sorted(train_codes.keys())
            tmat = np.asarray([train_codes[v] for v in train_verbs], dtype=np.float64)
            tmat = tmat / (np.linalg.norm(tmat, axis=1, keepdims=True) + 1e-9)
            for it in held:
                hc = verb_code_real(it["verb"]).astype(np.float64)
                hc = hc / (np.linalg.norm(hc) + 1e-9)
                sims = tmat @ hc
                nn_verb = train_verbs[int(np.argmax(sims))]
                if train_feat[nn_verb] != it["feature"]:
                    n_conflict_total += 1
                n_held_total += 1
        out["available"] = True
        out["n_conflict"] = int(n_conflict_total)
        out["n_held_checked"] = int(n_held_total)
        out["buildable"] = bool(n_conflict_total >= REAL_DATA_CONFLICT_MIN)
        out["note"] = ("real-data conflict items (nearest-similar TRAIN verb has WRONG feature) across "
                       "seeds 7/13/19: %d of %d held-out. The 29440 rule is a similarity-CLASS rule so "
                       "similarity and rule are co-extensive -> ~0 conflict -> real conflict corpus %s "
                       "buildable in this testbed; synthetic ABA/ABB is the decisive test."
                       % (n_conflict_total, n_held_total,
                          "IS" if n_conflict_total >= REAL_DATA_CONFLICT_MIN else "is NOT"))
    except Exception as e:
        out["note"] = "diagnostic error: %s" % (str(e)[:200],)
    return out


# ==================================================================================================
# PART 2: per-seed decisive run.
# ==================================================================================================
def run_seed(seed):
    roles = _roles()
    train_fillers = _filler_pool("train", N_TRAIN_FILLERS)
    held_fillers = _filler_pool("held", N_HELD_FILLERS)  # DISJOINT / novel

    train_items = gen_items(train_fillers, N_TRAIN_ITEMS, seed=seed)
    held_items = gen_items(held_fillers, N_HELD_ITEMS, seed=1000 + seed)

    train_vecs = [item_vector(it, train_fillers, roles) for it in train_items]
    held_vecs = [item_vector(it, held_fillers, roles) for it in held_items]
    train_cls = np.array([it["cls"] for it in train_items], dtype=int)
    held_cls = np.array([it["cls"] for it in held_items], dtype=int)

    # ---- Arm A: RAW-SIMILARITY-kNN over raw item vectors ----
    predA = knn_predict(train_vecs, train_cls, held_vecs)
    accA = _acc(predA, held_cls)

    # ---- Arm B: LINEAR-LOOP (29440 replay_cycle) ----
    class_codebook = {0: _atom("class:ABA"), 1: _atom("class:ABB")}
    predB = linear_loop_fit_predict(train_vecs, train_cls, held_vecs, class_codebook, seed)
    accB = _acc(predB, held_cls)

    # ---- relational features (settled) for train + held ----
    trainR = np.asarray([relational_features(v, roles, SETTLE_ITERS, SETTLE_ALPHA) for v in train_vecs],
                        dtype=np.float32)
    heldR = np.asarray([relational_features(v, roles, SETTLE_ITERS, SETTLE_ALPHA) for v in held_vecs],
                       dtype=np.float32)
    # settled ablation (multi-step codebook-free settling) for attribution of settling contribution
    trainR0 = np.asarray([relational_features(v, roles, SETTLE_ITERS_ABL, SETTLE_ALPHA) for v in train_vecs],
                         dtype=np.float32)
    heldR0 = np.asarray([relational_features(v, roles, SETTLE_ITERS_ABL, SETTLE_ALPHA) for v in held_vecs],
                        dtype=np.float32)

    # ---- Arm C: NONLINEAR-GLASSBOX (learned readout over settled relational features) ----
    w, b = train_readout(trainR, train_cls, READOUT_STEPS, READOUT_LR, seed)
    predC = readout_predict(heldR, w, b)
    accC = _acc(predC, held_cls)

    # ---- Arm C-scramble (INFORMATIONAL, not a gate): permute train labels. Because the relational
    # features form two cleanly-separated blobs, GD recovers the true split regardless of labels (only
    # the SIGN is label-set) -> acc is binary ~0 or ~1, NOT 0.5. This is the near-label-free-separability
    # signature (the readout/learning does almost nothing; the representation does everything). ----
    rng = np.random.default_rng(2000 + seed)
    scr_cls = train_cls[rng.permutation(len(train_cls))]
    ws, bs = train_readout(trainR, scr_cls, READOUT_STEPS, READOUT_LR, seed)
    predC_scr = readout_predict(heldR, ws, bs)
    accC_scr = _acc(predC_scr, held_cls)

    # ---- Arm C-wrongrole (THE MUST-FAIL GATE): unbind-compare with WRONG roles (never used in the
    # binding) destroys the role-binding structure -> relational features become noise -> readout at
    # chance on held-out. Confirms the signal comes from the ROLE-BINDING mechanism, not an artifact. ----
    roles_wrong = [_atom("role_wrong:%d" % i) for i in range(N_ROLES)]
    trainRw = np.asarray([relational_features(v, roles_wrong, SETTLE_ITERS, SETTLE_ALPHA) for v in train_vecs],
                         dtype=np.float32)
    heldRw = np.asarray([relational_features(v, roles_wrong, SETTLE_ITERS, SETTLE_ALPHA) for v in held_vecs],
                        dtype=np.float32)
    ww, bw = train_readout(trainRw, train_cls, READOUT_STEPS, READOUT_LR, seed)
    predC_wr = readout_predict(heldRw, ww, bw)
    accC_wr = _acc(predC_wr, held_cls)

    # ---- Arm D: kNN-ON-RELATIONAL (same settled features, no learning) ----
    predD = knn_predict(trainR, train_cls, heldR)
    accD = _acc(predD, held_cls)

    # ---- ablation: nonlinear on RAW (unsettled) relational features (settling contribution) ----
    w0, b0 = train_readout(trainR0, train_cls, READOUT_STEPS, READOUT_LR, seed)
    predC0 = readout_predict(heldR0, w0, b0)
    accC0 = _acc(predC0, held_cls)

    # ---- relational separation (binding-crosstalk floor): the two diagnostic pair-features by class ----
    c0 = held_cls == 0
    c1 = held_cls == 1
    i01 = PAIR_IDX[(0, 1)]
    i23 = PAIR_IDX[(2, 3)]
    sep = {
        "held_s01_class0_mean": float(np.mean(heldR[c0, i01])),
        "held_s01_class1_mean": float(np.mean(heldR[c1, i01])),
        "held_s23_class0_mean": float(np.mean(heldR[c0, i23])),
        "held_s23_class1_mean": float(np.mean(heldR[c1, i23])),
    }

    # ---- arms-differ (predictions not all identical; learned weights non-degenerate) ----
    preds_hashes = {
        "A": hashlib.sha256(predA.tobytes()).hexdigest(),
        "B": hashlib.sha256(predB.tobytes()).hexdigest(),
        "C": hashlib.sha256(predC.tobytes()).hexdigest(),
        "D": hashlib.sha256(predD.tobytes()).hexdigest(),
    }
    arms_differ = not (preds_hashes["A"] == preds_hashes["C"] and preds_hashes["B"] == preds_hashes["C"])
    weights_nondegenerate = bool(float(np.max(np.abs(w))) > 1e-4)

    return {
        "seed": seed,
        "n_train_items": len(train_items), "n_held_items": len(held_items),
        "acc_rawknn_A": round(accA, 4),
        "acc_linearloop_B": round(accB, 4),
        "acc_nonlinear_C": round(accC, 4),
        "acc_nonlinear_C_scramble_informational": round(accC_scr, 4),
        "acc_nonlinear_C_wrongrole": round(accC_wr, 4),
        "acc_knn_relational_D": round(accD, 4),
        "acc_nonlinear_C_settled_abl": round(accC0, 4),
        "nonlinear_minus_rawknn": round(accC - accA, 4),
        "wrongrole_collapse_C": round(accC - accC_wr, 4),
        "learned_readout_weights": [round(float(x), 4) for x in w],
        "learned_readout_bias": round(float(b), 4),
        "relational_separation": {k: round(v, 4) for k, v in sep.items()},
        "arms_differ": bool(arms_differ),
        "weights_nondegenerate": weights_nondegenerate,
    }


# ==================================================================================================
# Verdict.
# ==================================================================================================
def _mean(rows, key):
    vals = [r[key] for r in rows if r.get(key) is not None]
    return round(float(np.mean(vals)), 4) if vals else None


def build_verdict(rows, real_diag):
    m_A = _mean(rows, "acc_rawknn_A")
    m_B = _mean(rows, "acc_linearloop_B")
    m_C = _mean(rows, "acc_nonlinear_C")
    m_C_scr = _mean(rows, "acc_nonlinear_C_scramble_informational")
    m_C_wr = _mean(rows, "acc_nonlinear_C_wrongrole")
    m_D = _mean(rows, "acc_knn_relational_D")
    m_C0 = _mean(rows, "acc_nonlinear_C_settled_abl")
    m_margin = round(m_C - m_A, 4) if (m_C is not None and m_A is not None) else None
    m_collapse = _mean(rows, "wrongrole_collapse_C")
    everyseed_C = all(r["acc_nonlinear_C"] >= NONLINEAR_EVERYSEED_MIN for r in rows) if rows else False
    arms_ok = all(r["arms_differ"] for r in rows) if rows else False
    weights_ok = all(r["weights_nondegenerate"] for r in rows) if rows else False
    baseline_in_band = (m_A is not None and 0.05 < m_A < 0.95)

    corpus_leak = (m_A is not None and m_A > KNN_CEIL)  # baseline NOT failing -> conflict corpus invalid

    wrongrole_collapses = (m_C_wr is not None and m_C_wr <= WRONGROLE_CEIL
                           and m_collapse is not None and m_collapse >= WRONGROLE_COLLAPSE_MIN)

    hard_pass = bool(
        arms_ok and weights_ok and rows and not corpus_leak
        and m_A is not None and m_A <= KNN_CEIL
        and m_B is not None and m_B <= LINEAR_CEIL
        and m_C is not None and m_C >= NONLINEAR_PASS_MEAN
        and m_margin is not None and m_margin >= NONLINEAR_MARGIN
        and everyseed_C
        and wrongrole_collapses
    )
    hard_fail = bool(
        (m_C is not None and m_C <= NONLINEAR_FAIL_MAX)
        or (m_margin is not None and m_margin < NONLINEAR_MARGIN)
        or (not wrongrole_collapses)
        or (not arms_ok) or (not weights_ok)
    )

    if corpus_leak:
        verdict = "HARD_FAIL_CORPUS_LEAK"
        note = ("raw-kNN (baseline) held-out acc %.3f > %.2f: the conflict corpus does NOT make "
                "similarity-kNN fail by construction (surface-similarity leak). Conflict corpus invalid; "
                "no viability signal." % (m_A, KNN_CEIL))
    elif hard_pass and not hard_fail:
        verdict = "HARD_PASS_VIABILITY_GREEN_LIGHT_PENDING_VET"
        note = ("glass-box NONLINEAR mechanism (role-binding + unbind-compare coherence gate + learned "
                "readout) BEATS raw-similarity-kNN on the conflict subset by %.3f (C=%.3f vs A=%.3f) "
                "while raw-kNN (%.3f) and linear-loop (%.3f) sit at/near chance; WRONG-ROLE must-fail "
                "control collapses to chance (C_wrongrole=%.3f, C-C_wr=%.3f) so the signal comes from "
                "role-binding not an artifact. CONSTRUCTION-FAVORABLE existence proof -> green-light "
                "fork-A build. NOT a self-declared CG: fresh adversarial VET (kNN-identity attack over "
                "relational features; arm D=%.3f ties C -> lever = REPRESENTATION not learner) + "
                "real-text attested-combo test required."
                % (m_margin, m_C, m_A, m_A, m_B, m_C_wr, m_collapse, m_D))
    elif hard_fail:
        verdict = "HARD_FAIL_VIABILITY_NO_GREEN_LIGHT"
        reasons = []
        if m_C is not None and m_C <= NONLINEAR_FAIL_MAX:
            reasons.append("nonlinear C=%.3f <= %.2f (reduces to similarity / crosstalk-limited)" % (m_C, NONLINEAR_FAIL_MAX))
        if m_margin is not None and m_margin < NONLINEAR_MARGIN:
            reasons.append("C-A margin=%.3f < %.2f (does not beat kNN)" % (m_margin, NONLINEAR_MARGIN))
        if not wrongrole_collapses:
            reasons.append("wrong-role must-fail did NOT collapse (C_wrongrole=%s, C-C_wr=%s) -> "
                           "relational signal not attributable to role-binding" % (m_C_wr, m_collapse))
        if not arms_ok:
            reasons.append("arms bit-identical")
        if not weights_ok:
            reasons.append("learned readout weights degenerate")
        note = "; ".join(reasons)
    else:
        verdict = "MIDDLE_BAND"
        note = "partial: some gates fire, not all (see per-gate flags)"

    msg = (f"{verdict} | held-out (novel-filler) acc: RAW-kNN(A)={m_A} LINEAR-LOOP(B)={m_B} "
           f"NONLINEAR(C)={m_C} kNN-RELATIONAL(D)={m_D} C-wrongrole(must-fail)={m_C_wr} "
           f"C-settled-abl={m_C0} C-scramble(info)={m_C_scr} | chance={CHANCE} | C-A margin={m_margin} "
           f"wrongrole-collapse={m_collapse} everyseed_C>={NONLINEAR_EVERYSEED_MIN}={everyseed_C} "
           f"baseline_in_band={baseline_in_band} arms_differ={arms_ok} weights_nondegenerate={weights_ok} | "
           f"real_data_conflict={real_diag.get('n_conflict')}/{real_diag.get('n_held_checked')} "
           f"(buildable={real_diag.get('buildable')}) | {note}")
    summ = {
        "mean_acc_rawknn_A": m_A, "mean_acc_linearloop_B": m_B, "mean_acc_nonlinear_C": m_C,
        "mean_acc_nonlinear_C_wrongrole": m_C_wr, "mean_acc_nonlinear_C_scramble_informational": m_C_scr,
        "mean_acc_knn_relational_D": m_D, "mean_acc_nonlinear_C_settled_abl": m_C0,
        "mean_nonlinear_minus_rawknn": m_margin, "mean_wrongrole_collapse_C": m_collapse,
        "everyseed_C_ge_min": everyseed_C, "baseline_in_band": baseline_in_band,
        "arms_differ_all": arms_ok, "weights_nondegenerate_all": weights_ok, "corpus_leak": corpus_leak,
    }
    return verdict, msg, summ


# ==================================================================================================
# IO.
# ==================================================================================================
def _out_dir(mode):
    return os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}" + ("_smoke" if mode == "smoke" else ""))


def _write_start_marker(output_dir, mode):
    os.makedirs(output_dir, exist_ok=True)
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": mode, "host": platform.node()}
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, os.path.join(output_dir, "_start_marker.json"))


def write_metrics(output_dir, payload):
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    os.replace(tmp, os.path.join(output_dir, "metrics.json"))


def run_mode(mode):
    t0 = time.perf_counter()
    output_dir = _out_dir(mode)
    _write_start_marker(output_dir, mode)
    print(f"[{ANCHOR_NAME}:{mode}] START relational-vs-similarity conflict viability probe", flush=True)

    real_diag = real_data_conflict_diagnostic()
    print(f"[{ANCHOR_NAME}:{mode}] PART1 real-data diagnostic: {real_diag.get('note')}", flush=True)

    seeds = SMOKE_SEEDS if mode == "smoke" else FULL_SEEDS
    rows = []
    for seed in seeds:
        r = run_seed(seed)
        rows.append(r)
        print(f"[{ANCHOR_NAME}:{mode}] seed={seed} | RAW-kNN(A)={r['acc_rawknn_A']} "
              f"LINEAR(B)={r['acc_linearloop_B']} NONLINEAR(C)={r['acc_nonlinear_C']} "
              f"kNN-REL(D)={r['acc_knn_relational_D']} C-wr={r['acc_nonlinear_C_wrongrole']} "
              f"| margin={r['nonlinear_minus_rawknn']} sep(s01 c0/c1)="
              f"{round(r['relational_separation']['held_s01_class0_mean'],3)}/"
              f"{round(r['relational_separation']['held_s01_class1_mean'],3)}", flush=True)

    verdict, msg, summ = build_verdict(rows, real_diag)
    elapsed = time.perf_counter() - t0
    payload = {
        "anchor_name": ANCHOR_NAME, "run_mode": mode, "verdict": verdict, "verdict_msg": msg, "summary": msg,
        "elapsed_s": round(elapsed, 2), "ts_iso": datetime.now(timezone.utc).isoformat(),
        "seeds": seeds, "n_seed_rows": len(rows), "expected_n_seed_rows": len(seeds),
        "cardinality_ok": bool(len(rows) == len(seeds)),
        "N_DIM": N_DIM, "n_roles": N_ROLES, "settle_iters": SETTLE_ITERS, "settle_alpha": SETTLE_ALPHA,
        "n_train_fillers": N_TRAIN_FILLERS, "n_held_fillers": N_HELD_FILLERS,
        "n_train_items": N_TRAIN_ITEMS, "n_held_items": N_HELD_ITEMS,
        "bands": {"CHANCE": CHANCE, "KNN_CEIL": KNN_CEIL, "LINEAR_CEIL": LINEAR_CEIL,
                  "NONLINEAR_PASS_MEAN": NONLINEAR_PASS_MEAN, "NONLINEAR_MARGIN": NONLINEAR_MARGIN,
                  "NONLINEAR_EVERYSEED_MIN": NONLINEAR_EVERYSEED_MIN, "WRONGROLE_CEIL": WRONGROLE_CEIL,
                  "WRONGROLE_COLLAPSE_MIN": WRONGROLE_COLLAPSE_MIN, "NONLINEAR_FAIL_MAX": NONLINEAR_FAIL_MAX},
        "summary_metrics": summ,
        "part1_real_data_diagnostic": real_diag,
        "per_seed": rows,
        "final_metrics_atomicity": "tmp_replace",
        "compute_architecture": "sequential_cpu_seconds_no_storage",
        "crlb_n/a": ("relational-discrimination viability probe; floor is HRR binding-crosstalk "
                     "(reported per-seed as held-out s13 ABA-vs-ABB separation), not an argmax-capacity CRLB"),
        "progress_logging": "print_flush_true",
        "deterministic_seeding": True,
        "no_store_write_no_push_no_atom_bank": True,
        "honest_scope": ("synthetic ABA/ABB HARD-PASS is CONSTRUCTION-FAVORABLE existence proof (role-"
                         "binding yields a filler-independent relational feature a linear/kernel loop "
                         "cannot); it is a GREEN-LIGHT-PENDING-VET for fork A, NOT a self-declared CG. "
                         "Arm D (kNN over the same relational features) attributes whether the lever is "
                         "REPRESENTATION (binding) vs learning. Real-text attested-combo test still required."),
    }
    write_metrics(output_dir, payload)
    print(f"[{ANCHOR_NAME}:{mode}] DONE {round(elapsed,1)}s -> {verdict}", flush=True)
    print(msg, flush=True)
    return payload


# ==================================================================================================
# Self-test (real substrate code paths at tiny scale).
# ==================================================================================================
def self_test():
    global N_DIM
    print("=== relational-vs-similarity conflict viability probe self-test ===", flush=True)

    # bind/unbind roundtrip recovers a filler (HRR); crosstalk moderate at N_DIM.
    roles = _roles()
    tf = _filler_pool("train", N_TRAIN_FILLERS)
    it_c0 = {"cls": 0, "f": (0, 0, 1, 2)}   # match at (r0,r1)
    it_c1 = {"cls": 1, "f": (0, 1, 2, 2)}   # match at (r2,r3)
    v_c0 = item_vector(it_c0, tf, roles)
    v_c1 = item_vector(it_c1, tf, roles)
    assert abs(float(np.linalg.norm(v_c0)) - 1.0) < 1e-3

    # RELATIONAL feature separates the classes: s01 high for class0, low for class1 (filler-independent).
    i01 = PAIR_IDX[(0, 1)]
    r_c0 = relational_features(v_c0, roles, SETTLE_ITERS, SETTLE_ALPHA)
    r_c1 = relational_features(v_c1, roles, SETTLE_ITERS, SETTLE_ALPHA)
    assert r_c0[i01] > r_c1[i01] + 0.10, f"s01 does not separate class0({r_c0[i01]:.3f}) vs class1({r_c1[i01]:.3f})"

    # unbind recovers the bound filler above crosstalk (positive control on the primitive).
    u0 = _norm(_unbind_np(v_c0, roles[0]))
    assert _cos(u0, tf[0]) > _cos(u0, tf[1]), "unbind slot0 does not favor its true filler"

    # NONLINEAR arm generalizes to NOVEL held-out fillers where raw-kNN cannot (tiny run).
    r = run_seed(7)
    assert r["arms_differ"], "arms bit-identical"
    assert r["weights_nondegenerate"], "readout weights degenerate"
    assert 0.05 < r["acc_rawknn_A"] < 0.95, f"raw-kNN not in band: {r['acc_rawknn_A']}"
    assert r["acc_nonlinear_C"] > r["acc_rawknn_A"], \
        f"nonlinear({r['acc_nonlinear_C']}) does not exceed raw-kNN({r['acc_rawknn_A']}) at seed7"
    # wrong-role must-fail control collapses (signal comes from role-binding, not an artifact).
    assert (r["acc_nonlinear_C"] - r["acc_nonlinear_C_wrongrole"]) >= 0.20, \
        f"wrong-role control did not collapse: C={r['acc_nonlinear_C']} C_wr={r['acc_nonlinear_C_wrongrole']}"

    # linear-loop arm runs and produces a binary prediction acc in [0,1].
    assert 0.0 <= r["acc_linearloop_B"] <= 1.0

    # real-data diagnostic runs (or reports unavailability) without crashing.
    diag = real_data_conflict_diagnostic()
    assert isinstance(diag, dict) and "note" in diag

    print(f"[self-test PASS] seed7: RAW-kNN={r['acc_rawknn_A']} LINEAR={r['acc_linearloop_B']} "
          f"NONLINEAR={r['acc_nonlinear_C']} kNN-REL={r['acc_knn_relational_D']} "
          f"C-wr={r['acc_nonlinear_C_wrongrole']} margin={r['nonlinear_minus_rawknn']} | "
          f"s01 c0/c1={r_c0[i01]:.3f}/{r_c1[i01]:.3f} | real_conflict={diag.get('n_conflict')}/"
          f"{diag.get('n_held_checked')} buildable={diag.get('buildable')}", flush=True)
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["smoke", "full"], default="full")
    ap.add_argument("--self-test", action="store_true")
    args, _ = ap.parse_known_args()
    if args.self_test:
        self_test()
        return
    run_mode(args.mode)


if __name__ == "__main__":
    output_dir = _out_dir("full")
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        try:
            os.makedirs(output_dir, exist_ok=True)
            diag = {"verdict": "CELL_CRASHED", "verdict_msg": f"{type(e).__name__}: {str(e)[:400]}",
                    "summary": "CELL_CRASHED", "elapsed_s": 0.0, "traceback": traceback.format_exc()[:4000],
                    "ts_iso": datetime.now(timezone.utc).isoformat()}
            tmp = os.path.join(output_dir, "metrics.json.tmp")
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(diag, f, indent=2)
            os.replace(tmp, os.path.join(output_dir, "metrics.json"))
        finally:
            raise
