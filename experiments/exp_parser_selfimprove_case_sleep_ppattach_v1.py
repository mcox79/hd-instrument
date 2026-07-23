#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""exp_parser_selfimprove_case_sleep_ppattach_v1

PARSER SELF-IMPROVEMENT via CLS (complementary learning systems) case+sleep, applied to the
transition PARSER's own attachment errors (not a downstream role-labeler as in the certified
templates this ADAPTS). USER-directed build: does fast episodic case-encoding of the parser's
own mis-attachments, generalized by a SLEEP/NREM-replay consolidation pass, fold back as a
glass-box structural PRIOR that improves HELD-OUT parsing (on sentences/verbs never cased)?
= complementary learning systems (McClelland/O'Reilly) + sleep-dependent grammar-rule
extraction (Gomez 2006, Durrant 2011) + syntactic adaptation (Fine & Jaeger 2013) transplanted
onto THIS substrate's own case+sleep primitives.

ADAPTS the certified templates:
  - experiments/exp_reader_selfimprove_case_sleep_udewt_v1.py (atom 29405, grammar/arc-labeler
    surface -- REAL_IMPROVING_PROPERTY, verb-disjoint held-out generalization, scramble control)
  - experiments/exp_reader_meaning_correction_case_sleep_affectedness_v1.py (meaning surface)
This cell moves the SAME mechanism one layer down: instead of correcting a frozen role-LABELER,
it corrects the transition PARSER's own head-attachment decisions.

ERROR SURFACE (non-circular, out-of-sample, glass-box): classic PP-ATTACHMENT AMBIGUITY
  (Ratnaparkhi 1994; Collins & Brooks 1995) -- the textbook "V N1 P N2" configuration where a
  prepositional phrase can structurally attach to either the governing VERB (V) or the preceding
  NOUN (N1). In UD terms: a nominal token N2 with deprel in {obl, nmod} whose ADP "case" child
  sits between two live candidate governors (nearest preceding VERB = V; nearest preceding
  NOUN/PROPN before the ADP, excluding N2 itself = N1). Gold class = VERB iff gold_head(N2)==V,
  NOUN iff gold_head(N2)==N1; instances where gold attaches elsewhere are excluded (clean binary
  ambiguity only, matching the classic disambiguation-corpus convention). The transition parser
  (arc-eager, dynamic-oracle averaged-perceptron; CITED VERBATIM transcription @exp_multipred_
  depparse_argstruct_recall_v2.py lines ~267-544, itself CITED @exp_depparse_transition_arceager_
  cpu_v1.py / atom 29451) is trained on UD-EWT TRAIN ONLY; PP instances + attachment errors are
  harvested from DEV+TEST (out-of-sample for the parser -- no in-sample confound). is_fail =
  (parser's decoded head-class != gold_class).

SIGNATURE (glass-box, GOLD-FREE, mutation-probed): hashlib-coded dense bipolar HD bundle of
  {V lemma, N1 lemma, N1 upos, P form, N2 lemma, dist(P-V) bucket, dist(P-N1) bucket} -- the
  classic Ratnaparkhi 4-tuple (V,N1,P,N2) plus coarse distance buckets. NEVER reads gold_head or
  gold_class. Mutation-probe: permute gold_class across instances -> every signature byte-
  identical (asserted; source-scanned for "gold" references).

MECHANISM (RECOMBINATION of certified primitives, composed IN-CELL; NO hdlab/production mutation):
  FAST   = hdlab.hippocampal_encoder.HippocampalEncoder (DG+CA3 one-shot; SEEN recall sanity).
  SLEEP  = dense Hebbian superposition W [role x sig] via hdlab.continual.replay_cycle (NREM
           re-Hebb) over (signature, gold_class) case pairs mined on the SEEN verb-split.
  SCHEMA = hdlab.schema_exemplar_bayes.SchemaExemplarBayesIndex (coherence/purity diagnostic).
  GATE   = hdlab.glass_box_loop.cleanup_with_margin -- override the parser's own decoded class
           with the store's readout iff margin >= tau (tau calibrated on SEEN only, ART-vigilance).

THE CRUX (2026-07-23 USER routing task, "the 29440 trap"): atom 29440 PROVED analytically that a
  linear Hebbian atomize+sleep loop (role_space = W @ sig = sum_j role_j * (sig_j . sig)) is
  MATHEMATICALLY a similarity-weighted vote over the stored cases -- "learned a rule" is
  UNSUPPORTED unless the loop BEATS a parameter-free surface-similarity vote, not merely ties it.
  This cell's PRIMARY discriminator is therefore NOT the scramble-collapse alone (necessary but,
  per 29440, INSUFFICIENT) -- it is the coherent store's held-out net_gain/fix_rate BEATING BOTH:
  (a) ARM_KNN_SIMILARITY -- a parameter-free cosine-similarity k-NN vote (k=5) over the SAME SEEN
      case signatures (the exact control 29440's adversarial VET built; if the store ties this,
      "learned a rule" is unsupported -- structured-lookup-in-disguise).
  (b) ARM_MEMORIZE -- an exact discrete-feature-key (V,N1,P,N2) lookup table from SEEN cases (the
      "memorize-the-error-sentences" floor; on a VERB-DISJOINT held-out split this can never
      exact-match by construction -- if the store does not clear this trivial floor either, there
      is no generalization signal at all).
  MUST-FAIL CONTROLS (both must fire):
  (c) SCRAMBLE case<->correction (shuffle gold_class among SEEN cases before consolidation) ->
      held-out fix-rate must COLLAPSE toward scramble baseline (coherence control).
  (d) ARM_ZERO_CYCLES (freeze the sleep pass: n_cycles=0, W stays all-zero) -> tau calibration
      degenerates (margin always 0) -> net_gain must be FLAT (~0) -- proves the LIFT (if any) is
      attributable to consolidation cycles, not to the architecture merely existing.
  CYCLES CURVE (flexible/improving property): coherent net_gain / fix_rate measured at
  n_cycles in {0,1,2,3,6} (same SEEN cases, same tau-recalibration per cycle count).

BANDS (pre-registered BEFORE this run):
  HARD_PASS_REAL_LEARNED_RULE: scramble_collapse >= 0.15 AND all-seed coherent net_gain > 0 AND
    rescue_precision >= 0.60 AND leak_clean AND zero_cycles |net_gain| <= 0.02 (freeze control
    holds flat) AND coherent BEATS knn (net_gain margin >= 0.05 absolute AND fix_rate strictly
    greater) AND coherent BEATS memorize (net_gain margin >= 0.05 absolute AND fix_rate strictly
    greater).
  HARD_FAIL_MEMORIZATION_OR_SIMILARITY_LOOKUP (honest negative: parse-errors are more fact-like /
    similarity-shaped than grammar-like on this surface -- report it, per 29440 precedent): ANY of
    coherent net_gain <= 0 OR coherent fix_rate < 0.10 OR scramble does not collapse (< 0.05) OR
    coherent does NOT beat knn with margin (margin < 0.02, i.e. ties or loses -- the 29440 trap
    fires again) OR coherent does not beat memorize with margin.
  MIDDLE_BAND: otherwise (genuine but partial signal; localize which condition failed).

BRAIN-CHECK: PP-attachment resolution via lexically-conditioned frequency/co-occurrence statistics
  is the standard psycholinguistic account (Ratnaparkhi 1994 statistical account predates and
  matches human garden-path/preference data collected by Whittemore et al. 1990, Taraban &
  McClelland 1988 -- lexical-bias effects); CLS sleep-consolidation of episodic parse-error traces
  into schema-like structural priors (Gomez & Edgin 2015 sleep-dependent statistical learning;
  Fine & Jaeger 2013 syntactic adaptation via error-driven re-weighting) is the mechanism being
  replicated. If the substrate's loop reduces to similarity (matching 29440), that itself matches
  a documented brain-mechanism class (exemplar/analogical PP-attachment models, e.g. Daelemans
  et al. 1999 memory-based parsing) -- NOT a substrate-specific artifact; either outcome is
  informative and is reported honestly.

COMPUTE ARCHITECTURE: class (b) sequential-CPU (justified: one arc-eager training pass on UD-EWT
  TRAIN + greedy decode over DEV+TEST + a few hundred tiny [512x512] Hebbian outer-product builds
  across 3 seeds x 5 cycle-counts x 5 arms; no GPU-batchable primitive; wall budget < ~6min).
  Storage: sharded episodic (hippocampal) + dense superposition (cortical W); no_storage for the
  parser itself (transition-system state, not a KG). LOCAL-ONLY, foreground-to-completion; NO
  queue, NO push, NO remote-persist, NO git add of data/, NO hdlab mutation, NO atom bank
  (skunkworks VETs). Deterministic: OMP/MKL/OPENBLAS=1, fixed int seeds, numpy default_rng,
  hashlib feature codes (NO hash()-seeded RNG), sorted(set) splits. progress_logging:
  print_flush_true.

CELL-TEMPLATE MANDATORY (subset applicable to this LOCAL foreground measurement cell):
  - arms_differ_verified at smoke gate (hash test over predicted-class tuples per arm)
  - final_metrics_atomicity: tmp_replace (os.replace)
  - except SystemExit/KeyboardInterrupt: raise BEFORE except Exception (no BaseException)
  - crlb_n/a: generalization fix-rate measurement; noise floor = 1/n_heldout_fail reported
  - baseline_in_band: parser-decoded base accuracy on held-out patient set in (0.05, 0.95)
  - discriminator survives scale: smoke = full mechanism on a capped DEV-only slice (option A)
  - cardinality_ok: EXPECTED per-seed rows = len(seeds); verdict counts len(per_seed)
  - calibration_check: adaptive_with_discriminator_gate (tau on SEEN net_gain; controls fire)
  - all numbers tagged MEASURED@ / CITED@ / THEORETICAL@ / HYPOTHESIZED@ in this docstring
  - deterministic_seeding: true; progress_logging: print_flush_true
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
import zlib
from collections import Counter, defaultdict
from datetime import datetime, timezone

import numpy as np

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

ANCHOR_NAME = "parser_selfimprove_case_sleep_ppattach_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

UD_DIR = os.path.join(REPO_ROOT, "experiments", "data", "ud_english_ewt")

N_SIG = 512
DG_DIM = 2048
SPARSITY = 0.02
ROLES = ("VERB", "NOUN")
K_KNN = 5

# ---- Pre-registered bands (set BEFORE this run; see docstring) ------------------------
SCRAMBLE_COLLAPSE_MIN = 0.15
RESCUE_PRECISION_MIN = 0.60
ZERO_CYCLES_FLAT_MAX = 0.02
BEAT_MARGIN_HARD_PASS = 0.05
BEAT_MARGIN_HARD_FAIL = 0.02
FIX_RATE_FLOOR = 0.10
CYCLES_CURVE = [0, 1, 2, 3, 6]


# ========================================================================================
# CoNLL-U reader: (idx, form, lemma, upos, head, deprel), 1-based idx.
# ========================================================================================
def read_conllu(fn):
    sents = []
    cur = []
    with open(os.path.join(UD_DIR, fn), encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if not line:
                if cur:
                    sents.append(cur)
                    cur = []
                continue
            if line.startswith("#"):
                continue
            c = line.split("\t")
            if len(c) < 8 or "-" in c[0] or "." in c[0]:
                continue
            try:
                idx = int(c[0])
                head = int(c[6])
            except Exception:
                continue
            cur.append((idx, c[1], c[2], c[3], head, c[7]))
    if cur:
        sents.append(cur)
    return sents


# ========================================================================================
# ARC-EAGER TRANSITION PARSER core (train + greedy decode) -- CITED VERBATIM (transcribed, same
# algorithm/feature family) @experiments/exp_multipred_depparse_argstruct_recall_v2.py lines
# ~267-479 (itself CITED @exp_depparse_transition_arceager_cpu_v1.py / atom 29451). Transcribed
# (not imported) per that cell's own documented rationale: the 29451 script's module scope runs
# its FULL multi-seed experiment unconditionally with no __main__ guard, so importing it would
# silently re-run and overwrite the landed atom; pure functions are reused by direct transcription.
# ========================================================================================
_DP_SIZE = 1 << 21
_DP_MASK = _DP_SIZE - 1
_DP_SHIFT, _DP_LARC, _DP_RARC, _DP_REDU = 0, 1, 2, 3
_DP_ACT_SALT = np.array([0x9E3779B1, 0x85EBCA77, 0xC2B2AE3D, 0x27D4EB2F], dtype=np.int64)
_DP_ROOT_ATTR = ("<root>", "ROOT", "<root>")
_DP_NONE_ATTR = ("<none>", "<NONE>", "<none>")


def _dp_h(f):
    return zlib.crc32(f.encode("utf-8")) & _DP_MASK


def _dp_dist(d):
    a = abs(d)
    return "1" if a == 1 else ("2" if a == 2 else ("3-5" if a <= 5 else ("6-10" if a <= 10 else "11+")))


def _dp_suf(w):
    return w[-3:] if len(w) >= 3 else w


def _dp_szbucket(k):
    return "1" if k <= 1 else ("2" if k == 2 else ("3" if k == 3 else ("4-6" if k <= 6 else "7+")))


def _dp_mk_attr(sent):
    a = [_DP_ROOT_ATTR]
    for (i, w, p, h, dl, num) in sent:
        a.append((w.lower(), p, _dp_suf(w.lower())))
    return a


def _dp_config_feats(stack, bptr, n, attr, heads):
    s0 = stack[-1]
    s1 = stack[-2] if len(stack) >= 2 else None
    b0 = bptr if bptr <= n else None
    b1 = (bptr + 1) if (bptr + 1) <= n else None
    b2 = (bptr + 2) if (bptr + 2) <= n else None
    s0w, s0p, s0s = attr[s0]
    s1w, s1p, s1s = attr[s1] if s1 is not None else _DP_NONE_ATTR
    b0w, b0p, b0s = attr[b0] if b0 is not None else _DP_NONE_ATTR
    b1w, b1p, b1s = attr[b1] if b1 is not None else _DP_NONE_ATTR
    b2w, b2p, b2s = attr[b2] if b2 is not None else _DP_NONE_ATTR
    if b0 is not None and s0 > 0:
        dd = _dp_dist(b0 - s0)
    else:
        dd = "0"
    s0hh = "1" if s0 in heads else "0"
    F = [
        "bias",
        "s0p:" + s0p, "s0w:" + s0w, "s1p:" + s1p,
        "b0p:" + b0p, "b0w:" + b0w, "b1p:" + b1p, "b2p:" + b2p,
        "s0p_b0p:%s_%s" % (s0p, b0p), "s0w_b0w:%s_%s" % (s0w, b0w),
        "s0p_b0w:%s_%s" % (s0p, b0w), "s0w_b0p:%s_%s" % (s0w, b0p),
        "s0p_b0p_b1p:%s_%s_%s" % (s0p, b0p, b1p), "s1p_s0p_b0p:%s_%s_%s" % (s1p, s0p, b0p),
        "s0s:" + s0s, "b0s:" + b0s, "s0s_b0p:%s_%s" % (s0s, b0p), "b0s_s0p:%s_%s" % (b0s, s0p),
        "dist:%s_%s_%s" % (dd, s0p, b0p),
        "s0hh_p:%s_%s" % (s0hh, s0p), "s0hh_b0p:%s_%s" % (s0hh, b0p),
        "stksz:" + _dp_szbucket(len(stack)),
    ]
    return F


def _dp_legal(stack, bptr, n, heads):
    moves = []
    s0 = stack[-1]
    buf_nonempty = bptr <= n
    if buf_nonempty:
        moves.append(_DP_SHIFT)
    if buf_nonempty and s0 != 0 and s0 not in heads:
        moves.append(_DP_LARC)
    if buf_nonempty:
        moves.append(_DP_RARC)
    if s0 != 0 and s0 in heads:
        moves.append(_DP_REDU)
    return moves


def _dp_apply(stack, bptr, heads, a):
    if a == _DP_SHIFT:
        stack.append(bptr); bptr += 1
    elif a == _DP_LARC:
        heads[stack[-1]] = bptr; stack.pop()
    elif a == _DP_RARC:
        heads[bptr] = stack[-1]; stack.append(bptr); bptr += 1
    elif a == _DP_REDU:
        stack.pop()
    return stack, bptr


def _dp_move_costs_live(stack, bptr, n, gold, heads):
    costs = {}
    s0 = stack[-1]
    b0 = bptr if bptr <= n else None
    stack_set = set(stack)
    legal = _dp_legal(stack, bptr, n, heads)
    for a in legal:
        if a == _DP_SHIFT:
            c = 0
            for k in stack:
                if gold[k] == b0: c += 1
            if 0 <= gold[b0] and gold[b0] in stack_set: c += 1
            costs[a] = c
        elif a == _DP_LARC:
            c = 0
            gh = gold[s0]
            if gh != b0 and (bptr + 1) <= gh <= n: c += 1
            for k in range(bptr, n + 1):
                if gold[k] == s0: c += 1
            costs[a] = c
        elif a == _DP_RARC:
            c = 0
            gh = gold[b0]
            if gh != s0 and (gh in stack_set or (bptr + 1) <= gh <= n): c += 1
            for k in stack:
                if gold[k] == b0: c += 1
            costs[a] = c
        elif a == _DP_REDU:
            c = 0
            for k in range(bptr, n + 1):
                if gold[k] == s0: c += 1
            costs[a] = c
    return costs


def _dp_score_actions(base_ids, W, legal):
    out = {}
    for a in legal:
        ids = (base_ids ^ _DP_ACT_SALT[a]) & _DP_MASK
        out[a] = float(W[ids].sum())
    return out


def _dp_argmax_legal(scores):
    best_a = None; best = -1e18
    for a, s in scores.items():
        if s > best: best = s; best_a = a
    return best_a


def _dp_perc_update(W, CW, base_ids, a_gold, a_pred, c):
    ig = (base_ids ^ _DP_ACT_SALT[a_gold]) & _DP_MASK
    ip = (base_ids ^ _DP_ACT_SALT[a_pred]) & _DP_MASK
    np.add.at(W, ig, 1.0); np.add.at(CW, ig, c)
    np.add.at(W, ip, -1.0); np.add.at(CW, ip, -c)


def _dp_train_transition(train, seed, epochs, explore_after=2, explore_p=0.9):
    """Dynamic-oracle arc-eager averaged perceptron (Goldberg & Nivre 2012). CITED@exp_depparse_
    transition_arceager_cpu_v1.py _train_transition (dynamic=True branch, transcribed verbatim)."""
    rng = np.random.default_rng(seed)
    W = np.zeros(_DP_SIZE); CW = np.zeros(_DP_SIZE); c = 1
    for ep in range(epochs):
        explore = ep >= explore_after
        for si in rng.permutation(len(train)):
            s = train[si]; n = len(s)
            attr = _dp_mk_attr(s)
            gold = [0] * (n + 1)
            for (i, w, p, h, dl, num) in s:
                gold[i] = h if 0 <= h <= n else 0
            stack = [0]; bptr = 1; heads = {}
            guard = 0
            while bptr <= n or len(stack) > 1:
                if bptr > n and len(stack) <= 1:
                    break
                legal = _dp_legal(stack, bptr, n, heads)
                if not legal:
                    break
                base_ids = np.fromiter((_dp_h(f) for f in _dp_config_feats(stack, bptr, n, attr, heads)),
                                       dtype=np.int64)
                scores = _dp_score_actions(base_ids, W, legal)
                a_pred = _dp_argmax_legal(scores)
                costs = _dp_move_costs_live(stack, bptr, n, gold, heads)
                zero = [a for a in legal if costs.get(a, 1) == 0]
                if not zero:
                    zero = [min(costs, key=lambda k: costs[k])]
                a_orl = max(zero, key=lambda a: scores.get(a, -1e18))
                if a_pred != a_orl and costs.get(a_pred, 1) > 0:
                    _dp_perc_update(W, CW, base_ids, a_orl, a_pred, c); c += 1
                if explore and a_pred in legal and rng.random() < explore_p:
                    a_next = a_pred
                else:
                    a_next = a_orl
                stack, bptr = _dp_apply(stack, bptr, heads, a_next)
                guard += 1
                if guard > 4 * (n + 2):
                    break
    return W - CW / c


def _dp_decode_greedy(sent, attr, W):
    """CITED@exp_depparse_transition_arceager_cpu_v1.py _decode_greedy (transcribed verbatim)."""
    n = len(sent)
    stack = [0]; bptr = 1; heads = {}
    guard = 0
    while bptr <= n or len(stack) > 1:
        if bptr > n and len(stack) <= 1:
            break
        legal = _dp_legal(stack, bptr, n, heads)
        if not legal:
            break
        base_ids = np.fromiter((_dp_h(f) for f in _dp_config_feats(stack, bptr, n, attr, heads)),
                               dtype=np.int64)
        scores = _dp_score_actions(base_ids, W, legal)
        a = _dp_argmax_legal(scores)
        stack, bptr = _dp_apply(stack, bptr, heads, a)
        guard += 1
        if guard > 4 * (n + 2):
            break
    for i in range(1, n + 1):
        if i not in heads:
            heads[i] = 0
    return heads


def _dp_uas(sents, W):
    tot = 0; corr = 0
    for s in sents:
        attr = _dp_mk_attr(s)
        heads = _dp_decode_greedy(s, attr, W)
        for (i, w, p, h, dl, num) in s:
            tot += 1
            if heads.get(i) == h: corr += 1
    return corr / tot if tot else 0.0


def train_dep_parser(run_mode):
    train = read_conllu("en_ewt-ud-train.conllu")
    train = [[(i, w, u, h, dl) for (i, w, lem, u, h, dl) in s] for s in train]
    train = [s for s in train if 1 <= len(s) <= 50]
    dev = read_conllu("en_ewt-ud-dev.conllu")
    dev = [[(i, w, u, h, dl) for (i, w, lem, u, h, dl) in s] for s in dev]
    dev = [s for s in dev if 1 <= len(s) <= 50]
    if run_mode == "smoke":
        train = train[:1200]
        dev = dev[:250]
        epochs = 2
    else:
        dev = dev[:600]
        epochs = 4
    dev_p = [[(i, w, u, h, "_", None) for (i, w, u, h, dl) in s] for s in dev]
    t0 = time.perf_counter()
    W = _dp_train_transition([[(i, w, u, h, "_", None) for (i, w, u, h, dl) in s] for s in train], 1, epochs=epochs)
    uas = round(_dp_uas(dev_p, W), 4)
    elapsed = round(time.perf_counter() - t0, 1)
    print(f"[parser] trained n_train={len(train)} epochs={epochs} elapsed={elapsed}s UAS(dev n={len(dev)})={uas}",
          flush=True)
    return W, dict(n_train=len(train), epochs=epochs, elapsed_s=elapsed, uas_dev=uas, n_dev=len(dev))


# ========================================================================================
# PP-ATTACHMENT ambiguous-instance extraction (gold structure) + parser prediction.
# ========================================================================================
def extract_pp_instances(sent):
    """sent: list of (idx, form, lemma, upos, head, deprel), 1-based idx.
    Returns list of dicts: clean V-vs-N1 binary attachment ambiguity instances (gold-derived)."""
    toks = {t[0]: t for t in sent}
    out = []
    for (idx, form, lemma, upos, head, deprel) in sent:
        base_dl = deprel.split(":")[0]
        if base_dl not in ("obl", "nmod"):
            continue
        adp_idx = None
        for (i2, f2, l2, u2, h2, dl2) in sent:
            if h2 == idx and u2 == "ADP" and dl2.split(":")[0] == "case":
                adp_idx = i2
                break
        if adp_idx is None:
            continue
        v_idx = None
        for j in range(adp_idx - 1, 0, -1):
            if j in toks and toks[j][3] == "VERB":
                v_idx = j
                break
        n1_idx = None
        for j in range(adp_idx - 1, 0, -1):
            if j in toks and toks[j][3] in ("NOUN", "PROPN") and j != idx:
                n1_idx = j
                break
        if v_idx is None or n1_idx is None or v_idx == n1_idx:
            continue
        if head == v_idx:
            gold_class = "VERB"
        elif head == n1_idx:
            gold_class = "NOUN"
        else:
            continue
        out.append(dict(
            n2_idx=idx, n2_lemma=toks[idx][2].lower(),
            adp_idx=adp_idx, p_form=toks[adp_idx][1].lower(),
            v_idx=v_idx, v_lemma=toks[v_idx][2].lower(),
            n1_idx=n1_idx, n1_lemma=toks[n1_idx][2].lower(), n1_upos=toks[n1_idx][3],
            gold_head=head, gold_class=gold_class,
        ))
    return out


def _bucket(d):
    a = abs(d)
    return "1" if a <= 1 else ("2-3" if a <= 3 else ("4-6" if a <= 6 else "7+"))


_FEAT_CACHE = {}


def _feat_code(f):
    v = _FEAT_CACHE.get(f)
    if v is None:
        seed = int.from_bytes(hashlib.sha256(f.encode("utf-8")).digest()[:8], "big")
        v = (np.random.default_rng(seed).integers(0, 2, size=N_SIG).astype(np.float32) * 2.0 - 1.0)
        _FEAT_CACHE[f] = v
    return v


def instance_feats(inst):
    """Bundle of (V,N1,P,N2) tuple + coarse distance buckets (Ratnaparkhi 1994 style). Signature
    fields only -- deliberately excludes the correction-target fields (asserted by _leak_probe)."""
    return [
        "v:" + inst["v_lemma"], "n1:" + inst["n1_lemma"], "n1pos:" + inst["n1_upos"],
        "p:" + inst["p_form"], "n2:" + inst["n2_lemma"],
        "vpdist:" + _bucket(inst["adp_idx"] - inst["v_idx"]),
        "npdist:" + _bucket(inst["adp_idx"] - inst["n1_idx"]),
    ]


def signature(inst):
    v = np.zeros(N_SIG, dtype=np.float32)
    for f in instance_feats(inst):
        v += _feat_code(f)
    return v


def instance_key(inst):
    return "%s|%s|%s|%s" % (inst["v_lemma"], inst["n1_lemma"], inst["p_form"], inst["n2_lemma"])


def score_pred_class(sent_upos_form_head, W):
    """Decode the whole sentence with the trained parser; return {idx: pred_head}."""
    sent = [(i, w, u, 0, "_", None) for (i, w, u) in sent_upos_form_head]
    attr = _dp_mk_attr(sent)
    return _dp_decode_greedy(sent, attr, W)


def attach_predictions(sents_raw, W):
    """For each sentence, decode + extract PP instances, tag with parser's pred_class."""
    out = []
    for sent in sents_raw:
        inst_list = extract_pp_instances(sent)
        if not inst_list:
            continue
        sent_uf = [(i, w, u) for (i, w, lem, u, h, dl) in sent]
        heads = score_pred_class(sent_uf, W)
        for inst in inst_list:
            ph = heads.get(inst["n2_idx"], 0)
            if ph == inst["v_idx"]:
                pred_class = "VERB"
            elif ph == inst["n1_idx"]:
                pred_class = "NOUN"
            else:
                pred_class = "OTHER"
            inst = dict(inst)
            inst["pred_head"] = ph
            inst["pred_class"] = pred_class
            inst["is_fail"] = bool(pred_class != inst["gold_class"])
            inst["sig"] = signature(inst)
            inst["key"] = instance_key(inst)
            out.append(inst)
    return out


def _leak_probe(instances, n=200):
    import inspect as _insp
    src = _insp.getsource(instance_feats) + _insp.getsource(signature)
    src_clean = ("gold_class" not in src) and ("gold_head" not in src) and ("pred_class" not in src) \
        and ("pred_head" not in src)
    ok = True
    for inst in instances[:n]:
        s1 = signature(inst)
        mutant = dict(inst, gold_class=("NOUN" if inst["gold_class"] == "VERB" else "VERB"),
                      gold_head=inst["gold_head"] + 1000)
        s2 = signature(mutant)
        if not np.array_equal(s1, s2):
            ok = False
    return bool(ok and src_clean)


# ========================================================================================
# Verb-DISJOINT split (by governing verb V lemma).
# ========================================================================================
def verb_split(instances, seed, frac_seen=0.6):
    verbs = sorted(set(a["v_lemma"] for a in instances))
    rng = np.random.default_rng(seed)
    perm = rng.permutation(len(verbs))
    n_seen = int(round(frac_seen * len(verbs)))
    seen_v = set(verbs[j] for j in perm[:n_seen])
    seen = [a for a in instances if a["v_lemma"] in seen_v]
    held = [a for a in instances if a["v_lemma"] not in seen_v]
    return seen, held, seen_v


# ========================================================================================
# CLS SLEEP store: dense Hebbian superposition W[role x sig] via continual.replay_cycle.
# ========================================================================================
def build_role_codebook(roles, seed=1234):
    rng = np.random.default_rng(seed)
    return {r: (rng.integers(0, 2, size=N_SIG).astype(np.float32) * 2.0 - 1.0) for r in roles}


def consolidate_store(case_sigs, case_roles, role_codebook, *, n_cycles, replay_frac, seed=7):
    import torch
    from hdlab.continual import replay_cycle
    keys = torch.from_numpy(np.asarray(case_sigs, dtype=np.float32))
    values = torch.from_numpy(np.asarray([role_codebook[r] for r in case_roles], dtype=np.float32))
    m = keys.shape[0]
    replay_idx = torch.from_numpy(np.arange(m).astype(np.int64))
    W = torch.zeros((N_SIG, N_SIG), dtype=torch.float32)
    torch.manual_seed(seed)
    for _ in range(int(n_cycles)):
        replay_cycle(W, replay_idx, keys, values, replay_frac=replay_frac, lr=1.0)
    return W.numpy()


def store_predict(W, role_codebook, roles, sig):
    from hdlab.glass_box_loop import cleanup_with_margin
    rs = (W @ sig.astype(np.float32))
    nrm = float(np.linalg.norm(rs))
    if nrm > 1e-9:
        rs = rs / nrm
    codebook = np.asarray([role_codebook[r] for r in roles], dtype=np.float32)
    idx, margin = cleanup_with_margin(rs, codebook)
    return roles[idx], margin


def knn_predict(seen_sigs, seen_roles, sig, k=K_KNN):
    """Parameter-free surface-similarity control (the '29440 trap'): cosine-sim k-NN majority
    vote over SEEN case signatures. If the Hebbian store cannot BEAT this, 'learned a rule' is
    unsupported (structured-lookup-in-disguise)."""
    if not seen_sigs:
        return ROLES[0], 0.0
    sn = float(np.linalg.norm(sig)) + 1e-9
    sims = []
    for cs, cr in zip(seen_sigs, seen_roles):
        num = float(np.dot(cs, sig))
        den = (np.linalg.norm(cs) + 1e-9) * sn
        sims.append((num / den, cr))
    sims.sort(key=lambda x: -x[0])
    topk = sims[:min(k, len(sims))]
    votes = Counter(r for _, r in topk)
    role, _cnt = votes.most_common(1)[0]
    margin = float(np.mean([s for s, _ in topk]))
    return role, margin


def memorize_predict(memo_table, key, majority_role):
    """MEMORIZE-the-error-instances floor: exact discrete (V,N1,P,N2) key lookup from SEEN.
    On a verb-disjoint held-out split this can never exact-match (v_lemma always differs) --
    the trivial floor a real generalization signal must clear."""
    if key in memo_table:
        return memo_table[key], 1.0
    return majority_role, 0.0


def calibrate_tau(predict_fn, seen):
    margins = np.asarray([predict_fn(a)[1] for a in seen], dtype=np.float64)
    if margins.size == 0:
        return 0.0
    cand = sorted(set(float(np.percentile(margins, p)) for p in (0, 10, 20, 30, 40, 50, 60, 70, 80, 90)))
    best_tau, best_gain = cand[0], -1e9
    for tau in cand:
        r = eval_heldout(predict_fn, seen, tau)
        g = r["net_gain"] if r["net_gain"] is not None else -1e9
        if g >= best_gain:
            best_gain, best_tau = g, tau
    return round(best_tau, 6)


def eval_heldout(predict_fn, held, tau):
    fixes = breaks = base_correct = loop_correct = overrides = 0
    n_fail = sum(1 for a in held if a["is_fail"])
    n_corr = len(held) - n_fail
    for a in held:
        rhat, margin = predict_fn(a)
        base_ok = (a["pred_class"] == a["gold_class"])
        base_correct += int(base_ok)
        net = a["pred_class"]
        if margin > tau and rhat != a["pred_class"]:
            net = rhat
            overrides += 1
        net_ok = (net == a["gold_class"])
        loop_correct += int(net_ok)
        if (not base_ok) and net_ok:
            fixes += 1
        if base_ok and (not net_ok):
            breaks += 1
    n = len(held)
    return {
        "n_heldout": n, "n_heldout_fail": n_fail, "n_heldout_correct": n_corr,
        "base_acc": round(base_correct / n, 4) if n else None,
        "loop_acc": round(loop_correct / n, 4) if n else None,
        "net_gain": round((loop_correct - base_correct) / n, 4) if n else None,
        "fixes": fixes, "breaks": breaks, "overrides": overrides,
        "heldout_fix_rate": round(fixes / n_fail, 4) if n_fail else None,
        "collateral_rate": round(breaks / n_corr, 4) if n_corr else None,
        "rescue_precision": round(fixes / (fixes + breaks), 4) if (fixes + breaks) else None,
    }


def _nz(x, default):
    """None-coalescing helper (NOT `x or default` -- a legitimate net_gain==0.0 is falsy in Python
    and would be silently replaced by `or`, corrupting margin arithmetic)."""
    return default if x is None else x


def _majority_base_rate(held):
    fails = [a for a in held if a["is_fail"]]
    if not fails:
        return None
    maj = Counter(a["gold_class"] for a in fails).most_common(1)[0][0]
    return round(sum(1 for a in fails if a["gold_class"] == maj) / len(fails), 4)


def _fast_seen_recall(seen_fail):
    if len(seen_fail) < 2:
        return None
    from hdlab.hippocampal_encoder import HippocampalEncoder
    X = np.asarray([a["sig"] for a in seen_fail], dtype=np.float32)
    enc = HippocampalEncoder(input_dim=N_SIG, dg_dim=DG_DIM, sparsity=SPARSITY, seed=7)
    codes = enc.encode_and_write(X)
    ret = enc.retrieve(X, use_ca3=True, sparsify_after_settle=True)
    hits = sum(int(int(np.argmax(codes @ ret[i])) == i) for i in range(len(seen_fail)))
    return round(hits / len(seen_fail), 4)


def _schema_report(seen_fail):
    if len(seen_fail) < 6:
        return {"n": len(seen_fail), "note": "too few for schema clustering"}
    from hdlab.schema_exemplar_bayes import SchemaExemplarBayesIndex
    X = np.asarray([a["sig"] for a in seen_fail], dtype=np.float32)
    Xn = X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-9)
    idx = SchemaExemplarBayesIndex(compression_ratio=5, seed=7).fit(Xn)
    st = idx.stats()
    purities = []
    for c, fidxs in idx.schema_to_facts.items():
        rs = [seen_fail[j]["gold_class"] for j in fidxs]
        purities.append(Counter(rs).most_common(1)[0][1] / len(rs))
    return {"n_schemas": st["n_schemas"], "mean_role_purity": round(float(np.mean(purities)), 4),
            "compression": round(st["compression_ratio_effective"], 2)}


# ========================================================================================
# PER-CLUSTER rule-vs-episodic gate (USER design reinforcement, 2026-07-23): consolidation must
# NOT be all-or-nothing over the whole error set. Cluster SEEN failures by signature similarity
# (SchemaExemplarBayesIndex, unaffected by label permutation -- it clusters on Xn only); for each
# cluster, PROMOTE TO RULE only if it shows a genuine structural pattern (size >= MIN_CLUSTER_SIZE
# AND role-purity >= PURITY_THRESH); otherwise the cluster's cases stay EPISODIC-ONLY (fast
# hippocampal-style near-exact recall, NOT folded into the generalizing cortical store). This is
# the brain's CLS split realized at cluster granularity: regularities -> cortical rule (abstracted
# to the cluster CENTROID, not the raw per-item Hebbian sum -- so a promoted rule is mechanistically
# a PROTOTYPE-abstraction, not merely more weight on the same item-level kNN-equivalent sum atom
# 29440 refuted); exceptions -> stay episodic (only fire on near-exact signature match, tight
# cosine threshold, no generalization claimed). Under SCRAMBLE (case<->correction shuffled BEFORE
# gating), clustering is unaffected (label-blind) but per-cluster purity collapses toward chance
# (0.5 for 2 classes) -- most/all clusters should FAIL the purity gate and fall back to episodic-
# only, which structurally cannot fire on a verb-disjoint held-out split -> this is the expected
# scramble-collapse mechanism now expressed through the gate rather than through W alone.
# ========================================================================================
PURITY_THRESH = 0.75
MIN_CLUSTER_SIZE = 3
EPISODIC_SIM_THRESH = 0.90


def build_cluster_gated_store(seen_fail, role_codebook, roles, *, n_cycles, replay_frac, seed=7):
    from hdlab.schema_exemplar_bayes import SchemaExemplarBayesIndex
    if len(seen_fail) < 6:
        return (np.zeros((N_SIG, N_SIG), dtype=np.float32), [], [],
                dict(n_clusters=0, n_rule_clusters=0, n_episodic_clusters=0,
                     n_rule_cases_abstracted=0, n_episodic_cases=len(seen_fail), clusters=[]))
    X = np.asarray([a["sig"] for a in seen_fail], dtype=np.float32)
    Xn = X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-9)
    idx = SchemaExemplarBayesIndex(compression_ratio=5, seed=seed).fit(Xn)
    rule_sigs, rule_roles = [], []
    episodic_sigs, episodic_roles = [], []
    cluster_reports = []
    for c, fidxs in idx.schema_to_facts.items():
        members = [seen_fail[j] for j in fidxs]
        roles_in_cluster = [m["gold_class"] for m in members]
        maj_role, maj_count = Counter(roles_in_cluster).most_common(1)[0]
        purity = maj_count / len(members)
        is_rule = bool(len(members) >= MIN_CLUSTER_SIZE and purity >= PURITY_THRESH)
        cluster_reports.append(dict(cluster=int(c), size=len(members), purity=round(purity, 4),
                                    majority_role=maj_role, promoted_to_rule=is_rule))
        if is_rule:
            centroid = np.mean([m["sig"] for m in members], axis=0).astype(np.float32)
            rule_sigs.append(centroid)
            rule_roles.append(maj_role)
        else:
            for m in members:
                episodic_sigs.append(m["sig"])
                episodic_roles.append(m["gold_class"])
    if rule_sigs:
        W = consolidate_store(rule_sigs, rule_roles, role_codebook, n_cycles=n_cycles,
                              replay_frac=replay_frac, seed=seed)
    else:
        W = np.zeros((N_SIG, N_SIG), dtype=np.float32)
    n_rule = sum(1 for r in cluster_reports if r["promoted_to_rule"])
    summary = dict(n_clusters=len(cluster_reports), n_rule_clusters=n_rule,
                   n_episodic_clusters=len(cluster_reports) - n_rule,
                   n_rule_cases_abstracted=len(rule_sigs), n_episodic_cases=len(episodic_sigs),
                   clusters=cluster_reports)
    return W, episodic_sigs, episodic_roles, summary


def cluster_gated_predict_factory(W, role_codebook, roles, episodic_sigs, episodic_roles, tau_rule,
                                  ep_sim_thresh=EPISODIC_SIM_THRESH):
    """Returns a predict_fn(a) -> (role, margin) that ALWAYS pre-bakes the override-or-not
    decision (margin in {-1.0 (no override), 1.0 (override)} once a path fires; eval_heldout is
    called with tau=0.0 for this arm) so RULE-path and EPISODIC-path use their own criteria
    without eval_heldout needing a second, external tau."""
    fire_log = []  # (source: 'RULE'|'EPISODIC'|'NONE', rule_role_if_fired)

    def fn(a):
        role_rule, margin_rule = store_predict(W, role_codebook, roles, a["sig"])
        if margin_rule > tau_rule:
            fire_log.append(("RULE", role_rule))
            return role_rule, 1.0
        if episodic_sigs:
            sn = float(np.linalg.norm(a["sig"])) + 1e-9
            best_sim, best_role = -1.0, None
            for cs, cr in zip(episodic_sigs, episodic_roles):
                sim = float(np.dot(cs, a["sig"])) / ((float(np.linalg.norm(cs)) + 1e-9) * sn)
                if sim > best_sim:
                    best_sim, best_role = sim, cr
            if best_sim > ep_sim_thresh:
                fire_log.append(("EPISODIC", best_role))
                return best_role, 1.0
        fire_log.append(("NONE", None))
        return a["pred_class"], -1.0
    fn.fire_log = fire_log
    return fn


def calibrate_tau_rule_only(W, role_codebook, roles, seen):
    """Calibrate tau_rule on SEEN using ONLY the rule-store readout (episodic path excluded from
    calibration -- episodic uses its own fixed near-exact threshold, not tuned for net_gain)."""
    rule_fn = lambda a: store_predict(W, role_codebook, roles, a["sig"])  # noqa: E731
    return calibrate_tau(rule_fn, seen)


# ========================================================================================
# Per-seed run: harvest PP instances, verb-disjoint split, build ALL arms, compute controls.
# ========================================================================================
def run_seed(instances, seed, replay_frac=0.5, n_cycles_coherent=6, frac_seen=0.6):
    seen, held, seen_v = verb_split(instances, seed, frac_seen)
    seen_fail = [a for a in seen if a["is_fail"]]
    held_fail = [a for a in held if a["is_fail"]]
    base_rate = _majority_base_rate(held)
    fast_recall = _fast_seen_recall(seen_fail)
    schema = _schema_report(seen_fail)
    roles = list(ROLES)
    role_codebook = build_role_codebook(roles)

    case_sigs = [a["sig"] for a in seen_fail]
    case_roles = [a["gold_class"] for a in seen_fail]

    if len(case_sigs) < 4:
        return {"seed": seed, "skipped": "too_few_seen_cases", "n_seen_fail": len(seen_fail),
                "n_heldout_fail": len(held_fail)}

    # ---- COHERENT store ----
    W = consolidate_store(case_sigs, case_roles, role_codebook, n_cycles=n_cycles_coherent,
                          replay_frac=replay_frac, seed=seed)
    coh_fn = lambda a: store_predict(W, role_codebook, roles, a["sig"])  # noqa: E731
    tau_coh = calibrate_tau(coh_fn, seen)
    coherent = eval_heldout(coh_fn, held, tau_coh)

    # ---- MUST-FAIL (c): SCRAMBLE case<->correction ----
    rng = np.random.default_rng(1000 + seed)
    scr_roles = [case_roles[j] for j in rng.permutation(len(case_roles))]
    W_scr = consolidate_store(case_sigs, scr_roles, role_codebook, n_cycles=n_cycles_coherent,
                              replay_frac=replay_frac, seed=seed)
    scr_fn = lambda a: store_predict(W_scr, role_codebook, roles, a["sig"])  # noqa: E731
    scramble = eval_heldout(scr_fn, held, tau_coh)

    # ---- ORDER-SCRAMBLE replay order (reported honestly; expected NOT to collapse -- additive) ----
    order_perm = rng.permutation(len(case_sigs))
    W_ord = consolidate_store([case_sigs[j] for j in order_perm], [case_roles[j] for j in order_perm],
                              role_codebook, n_cycles=n_cycles_coherent, replay_frac=replay_frac, seed=seed + 5)
    ord_fn = lambda a: store_predict(W_ord, role_codebook, roles, a["sig"])  # noqa: E731
    order_scr = eval_heldout(ord_fn, held, tau_coh)

    # ---- MUST-FAIL (d): ARM_ZERO_CYCLES (freeze the sleep pass) ----
    W_zero = consolidate_store(case_sigs, case_roles, role_codebook, n_cycles=0,
                               replay_frac=replay_frac, seed=seed)
    zero_fn = lambda a: store_predict(W_zero, role_codebook, roles, a["sig"])  # noqa: E731
    tau_zero = calibrate_tau(zero_fn, seen)
    zero_cycles = eval_heldout(zero_fn, held, tau_zero)

    # ---- ARM_KNN_SIMILARITY (the 29440-trap control; must be BEATEN not tied) ----
    knn_fn = lambda a: knn_predict(case_sigs, case_roles, a["sig"], k=K_KNN)  # noqa: E731
    tau_knn = calibrate_tau(knn_fn, seen)
    knn_arm = eval_heldout(knn_fn, held, tau_knn)

    # ---- ARM_MEMORIZE (exact discrete-key lookup; verb-disjoint held-out floor) ----
    memo_table = {}
    for a in seen_fail:
        memo_table.setdefault(a["key"], Counter()).update([a["gold_class"]])
    memo_table = {k: c.most_common(1)[0][0] for k, c in memo_table.items()}
    maj_role = Counter(case_roles).most_common(1)[0][0]
    memo_fn = lambda a: memorize_predict(memo_table, a["key"], maj_role)  # noqa: E731
    memo_arm = eval_heldout(memo_fn, held, 0.5)

    # ---- CYCLES CURVE (flexible/improving property) ----
    curve = []
    for nc in CYCLES_CURVE:
        Wc = consolidate_store(case_sigs, case_roles, role_codebook, n_cycles=nc,
                               replay_frac=replay_frac, seed=seed)
        fn_c = lambda a, _W=Wc: store_predict(_W, role_codebook, roles, a["sig"])  # noqa: E731
        tau_c = calibrate_tau(fn_c, seen)
        r_c = eval_heldout(fn_c, held, tau_c)
        curve.append({"n_cycles": nc, "net_gain": r_c["net_gain"], "heldout_fix_rate": r_c["heldout_fix_rate"],
                      "rescue_precision": r_c["rescue_precision"]})

    gain_collapse_scramble = round((coherent["heldout_fix_rate"] or 0) - (scramble["heldout_fix_rate"] or 0), 4)
    beat_knn_margin = round(_nz(coherent["net_gain"], -9) - _nz(knn_arm["net_gain"], -9), 4)
    beat_memo_margin = round(_nz(coherent["net_gain"], -9) - _nz(memo_arm["net_gain"], -9), 4)

    # ---- CLUSTER_GATED (USER design reinforcement, 2026-07-23): per-cluster rule-vs-episodic ----
    # gate. This is the NEW headline arm -- promotes ONLY clusters with a genuine structural
    # pattern (size + purity) to a generalizing rule (built from the cluster CENTROID, not the raw
    # per-item Hebbian sum); idiosyncratic clusters stay episodic-only (near-exact recall only).
    W_rule, ep_sigs, ep_roles, cluster_summary = build_cluster_gated_store(
        seen_fail, role_codebook, roles, n_cycles=n_cycles_coherent, replay_frac=replay_frac, seed=seed)
    tau_rule = calibrate_tau_rule_only(W_rule, role_codebook, roles, seen)
    cg_fn = cluster_gated_predict_factory(W_rule, role_codebook, roles, ep_sigs, ep_roles, tau_rule)
    cluster_gated = eval_heldout(cg_fn, held, 0.0)
    rule_routed = [(a, role) for a, (src, role) in zip(held, cg_fn.fire_log) if src == "RULE"]
    episodic_routed_n = sum(1 for (src, _r) in cg_fn.fire_log if src == "EPISODIC")

    # SCRAMBLE for cluster-gated: shuffle gold_class among SEEN cases BEFORE clustering+gating.
    # Clustering itself is label-blind (Xn only) so cluster MEMBERSHIP is unaffected; purity per
    # cluster should collapse toward chance (0.5) -- most/all clusters should FAIL the purity gate.
    seen_fail_scr = [dict(a, gold_class=scr_roles[i]) for i, a in enumerate(seen_fail)]
    W_rule_scr, ep_sigs_scr, ep_roles_scr, cluster_summary_scr = build_cluster_gated_store(
        seen_fail_scr, role_codebook, roles, n_cycles=n_cycles_coherent, replay_frac=replay_frac, seed=seed)
    tau_rule_scr = calibrate_tau_rule_only(W_rule_scr, role_codebook, roles, seen)
    cg_scr_fn = cluster_gated_predict_factory(W_rule_scr, role_codebook, roles, ep_sigs_scr, ep_roles_scr,
                                              tau_rule_scr)
    cluster_gated_scramble = eval_heldout(cg_scr_fn, held, 0.0)

    # Rule-fire-vs-kNN-agreement diagnostic (the 29440-trap check restricted to the RULE-routed
    # subset): near-total overlap with the plain kNN vote on the SAME instances = the promoted
    # "rule" is still just reproducing item-level similarity in disguise.
    n_rule_routed = len(rule_routed)
    if n_rule_routed:
        agree = sum(1 for a, role in rule_routed if knn_predict(case_sigs, case_roles, a["sig"], k=K_KNN)[0] == role)
        rule_knn_agreement = round(agree / n_rule_routed, 4)
    else:
        rule_knn_agreement = None

    gain_collapse_cluster_gated = round((cluster_gated["heldout_fix_rate"] or 0) -
                                        (cluster_gated_scramble["heldout_fix_rate"] or 0), 4)
    beat_knn_margin_cg = round(_nz(cluster_gated["net_gain"], -9) - _nz(knn_arm["net_gain"], -9), 4)
    beat_memo_margin_cg = round(_nz(cluster_gated["net_gain"], -9) - _nz(memo_arm["net_gain"], -9), 4)
    beat_ungated_margin = round(_nz(cluster_gated["net_gain"], -9) - _nz(coherent["net_gain"], -9), 4)

    return {
        "seed": seed, "n_seen_verbs": len(seen_v), "n_seen_fail": len(seen_fail),
        "n_heldout": len(held), "n_heldout_fail": len(held_fail), "base_rate_majority": base_rate,
        "tau_coherent": tau_coh, "fast_seen_recall": fast_recall, "schema": schema,
        "coherent": coherent, "scramble": scramble, "order_scramble": order_scr,
        "zero_cycles": zero_cycles, "knn_similarity": knn_arm, "memorize": memo_arm,
        "gain_collapse_scramble": gain_collapse_scramble,
        "beat_knn_margin": beat_knn_margin, "beat_memo_margin": beat_memo_margin,
        "coherent_beats_knn_fixrate": bool((coherent["heldout_fix_rate"] or 0) > (knn_arm["heldout_fix_rate"] or 0)),
        "coherent_beats_memo_fixrate": bool((coherent["heldout_fix_rate"] or 0) > (memo_arm["heldout_fix_rate"] or 0)),
        "cycles_curve": curve,
        "cluster_gated": cluster_gated, "cluster_gated_scramble": cluster_gated_scramble,
        "cluster_summary": cluster_summary, "cluster_summary_scramble": cluster_summary_scr,
        "gain_collapse_cluster_gated": gain_collapse_cluster_gated,
        "beat_knn_margin_cg": beat_knn_margin_cg, "beat_memo_margin_cg": beat_memo_margin_cg,
        "beat_ungated_margin": beat_ungated_margin,
        "cg_beats_knn_fixrate": bool((cluster_gated["heldout_fix_rate"] or 0) > (knn_arm["heldout_fix_rate"] or 0)),
        "cg_beats_memo_fixrate": bool((cluster_gated["heldout_fix_rate"] or 0) > (memo_arm["heldout_fix_rate"] or 0)),
        "n_rule_routed_heldout": n_rule_routed, "n_episodic_routed_heldout": episodic_routed_n,
        "rule_knn_agreement": rule_knn_agreement,
    }


# ========================================================================================
# Mode configs + I/O.
# ========================================================================================
def cfg_smoke():
    return dict(mode="smoke", seeds=[7], replay_frac=0.5, n_cycles_coherent=6, frac_seen=0.6, dev_cap=900)


def cfg_full():
    return dict(mode="full", seeds=[7, 13, 19], replay_frac=0.5, n_cycles_coherent=6, frac_seen=0.6, dev_cap=None)


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
    cfg = cfg_smoke() if mode == "smoke" else cfg_full()
    output_dir = _out_dir(mode)
    _write_start_marker(output_dir, mode)
    print(f"[{ANCHOR_NAME}:{mode}] START parser self-improvement case+sleep on PP-attachment", flush=True)

    W, parser_info = train_dep_parser(mode)

    dev = read_conllu("en_ewt-ud-dev.conllu")
    test = read_conllu("en_ewt-ud-test.conllu")
    sents = dev + test
    sents = [s for s in sents if 1 <= len(s) <= 60]
    if cfg["dev_cap"]:
        sents = sents[:cfg["dev_cap"]]
    print(f"[{ANCHOR_NAME}:{mode}] out-of-sample conllu sents={len(sents)} (dev+test)", flush=True)

    instances = attach_predictions(sents, W)
    n_fail = sum(1 for a in instances if a["is_fail"])
    base_acc_all = round(1 - n_fail / len(instances), 4) if instances else None
    verb_counts = defaultdict(int)
    for a in instances:
        verb_counts[a["v_lemma"]] += 1
    census = {
        "n_pp_instances": len(instances), "n_base_errors": n_fail,
        "base_acc_all": base_acc_all, "n_distinct_governing_verbs": len(verb_counts),
        "class_balance_gold": dict(Counter(a["gold_class"] for a in instances)),
        "class_balance_pred": dict(Counter(a["pred_class"] for a in instances)),
    }
    print(f"[{ANCHOR_NAME}:{mode}] CENSUS pp_instances={len(instances)} base_errors={n_fail} "
          f"acc={base_acc_all} verbs={len(verb_counts)} parser_uas={parser_info['uas_dev']}", flush=True)

    leak_clean = _leak_probe(instances)
    print(f"[{ANCHOR_NAME}:{mode}] LEAK-CLEAN (signature gold-free, mutation-invariant): {leak_clean}", flush=True)

    per_seed = []
    for seed in cfg["seeds"]:
        row = run_seed(instances, seed, replay_frac=cfg["replay_frac"],
                       n_cycles_coherent=cfg["n_cycles_coherent"], frac_seen=cfg["frac_seen"])
        per_seed.append(row)
        if "coherent" in row:
            cs = row["cluster_summary"]
            print(f"[{ANCHOR_NAME}:{mode}] seed={seed} n_seen_fail={row['n_seen_fail']} "
                  f"n_held_fail={row['n_heldout_fail']} base_rate={row['base_rate_majority']} | "
                  f"CLUSTER_GATED fix={row['cluster_gated']['heldout_fix_rate']} gain={row['cluster_gated']['net_gain']} "
                  f"prec={row['cluster_gated']['rescue_precision']} clusters={cs['n_clusters']} "
                  f"rule={cs['n_rule_clusters']} episodic={cs['n_episodic_clusters']} | "
                  f"CG_SCRAMBLE fix={row['cluster_gated_scramble']['heldout_fix_rate']} "
                  f"(collapse={row['gain_collapse_cluster_gated']}) | "
                  f"CG_beat_knn={row['beat_knn_margin_cg']} CG_beat_memo={row['beat_memo_margin_cg']} "
                  f"CG_beat_ungated={row['beat_ungated_margin']} rule_knn_agree={row['rule_knn_agreement']} "
                  f"(n_rule_routed={row['n_rule_routed_heldout']}) || UNGATED(coherent) fix="
                  f"{row['coherent']['heldout_fix_rate']} gain={row['coherent']['net_gain']} "
                  f"SCRAMBLE fix={row['scramble']['heldout_fix_rate']} (collapse={row['gain_collapse_scramble']}) "
                  f"ZERO_CYCLES gain={row['zero_cycles']['net_gain']} | KNN fix={row['knn_similarity']['heldout_fix_rate']} "
                  f"gain={row['knn_similarity']['net_gain']} | MEMO fix={row['memorize']['heldout_fix_rate']} "
                  f"gain={row['memorize']['net_gain']}", flush=True)
        else:
            print(f"[{ANCHOR_NAME}:{mode}] seed={seed} SKIPPED: {row.get('skipped')}", flush=True)

    scored = [s for s in per_seed if "coherent" in s]

    def mean(path):
        vals = []
        for s in scored:
            v = s
            for p in path:
                v = v[p] if isinstance(v, dict) else None
            if isinstance(v, (int, float)):
                vals.append(v)
        return round(float(np.mean(vals)), 4) if vals else None

    # ---- PRIMARY headline arm = CLUSTER_GATED (per-cluster rule-vs-episodic gate) ----
    m_fix = mean(["cluster_gated", "heldout_fix_rate"])
    m_gain = mean(["cluster_gated", "net_gain"])
    m_prec = mean(["cluster_gated", "rescue_precision"])
    m_base = mean(["base_rate_majority"])
    m_collapse = mean(["gain_collapse_cluster_gated"])
    m_recall = mean(["fast_seen_recall"])
    m_zero_gain = mean(["zero_cycles", "net_gain"])
    m_knn_gain = mean(["knn_similarity", "net_gain"])
    m_knn_fix = mean(["knn_similarity", "heldout_fix_rate"])
    m_memo_gain = mean(["memorize", "net_gain"])
    m_memo_fix = mean(["memorize", "heldout_fix_rate"])
    m_beat_knn = mean(["beat_knn_margin_cg"])
    m_beat_memo = mean(["beat_memo_margin_cg"])
    m_beat_ungated = mean(["beat_ungated_margin"])
    m_rule_knn_agree = mean(["rule_knn_agreement"])
    base_acc = mean(["cluster_gated", "base_acc"])
    baseline_in_band = bool(base_acc is not None and 0.05 < base_acc < 0.95)

    # ---- UNGATED (global, flat Hebbian over ALL seen cases) comparison numbers -- reported to show
    # whether per-cluster gating is doing real work vs the atom-29440-style monolithic reduction.
    m_fix_ungated = mean(["coherent", "heldout_fix_rate"])
    m_gain_ungated = mean(["coherent", "net_gain"])
    m_collapse_ungated = mean(["gain_collapse_scramble"])

    n_clusters_total = sum(s["cluster_summary"]["n_clusters"] for s in scored)
    n_rule_total = sum(s["cluster_summary"]["n_rule_clusters"] for s in scored)
    n_episodic_total = sum(s["cluster_summary"]["n_episodic_clusters"] for s in scored)
    rule_cluster_ratio = round(n_rule_total / n_clusters_total, 4) if n_clusters_total else None

    all_seeds_gain_pos = bool(scored) and all(_nz(s["cluster_gated"]["net_gain"], -1) > 0 for s in scored)
    all_seeds_beat_knn = bool(scored) and all(s["cg_beats_knn_fixrate"] for s in scored)
    all_seeds_beat_memo = bool(scored) and all(s["cg_beats_memo_fixrate"] for s in scored)
    scramble_collapses = (m_collapse is not None and m_collapse >= SCRAMBLE_COLLAPSE_MIN)
    net_gain_pos = (m_gain is not None and m_gain > 0.0)
    prec_ok = (m_prec is not None and m_prec >= RESCUE_PRECISION_MIN)
    zero_cycles_flat = (m_zero_gain is not None and abs(m_zero_gain) <= ZERO_CYCLES_FLAT_MAX)
    beats_knn_hp = (m_beat_knn is not None and m_beat_knn >= BEAT_MARGIN_HARD_PASS and all_seeds_beat_knn)
    beats_memo_hp = (m_beat_memo is not None and m_beat_memo >= BEAT_MARGIN_HARD_PASS and all_seeds_beat_memo)
    ties_or_loses_knn = (m_beat_knn is not None and m_beat_knn < BEAT_MARGIN_HARD_FAIL)
    ties_or_loses_memo = (m_beat_memo is not None and m_beat_memo < BEAT_MARGIN_HARD_FAIL)
    rule_reduces_to_knn = (m_rule_knn_agree is not None and m_rule_knn_agree >= 0.95 and (n_rule_total > 0))

    memorization_or_lookup = (
        (not scored) or
        (m_fix is not None and m_fix < FIX_RATE_FLOOR) or
        (m_gain is not None and m_gain <= 0.0) or
        (m_collapse is not None and m_collapse < 0.05) or
        ties_or_loses_knn or ties_or_loses_memo
    )

    if not scored:
        verdict = "INSUFFICIENT_SURFACE"
    elif (scramble_collapses and net_gain_pos and all_seeds_gain_pos and prec_ok and leak_clean
          and zero_cycles_flat and beats_knn_hp and beats_memo_hp and not rule_reduces_to_knn):
        verdict = "HARD_PASS_REAL_LEARNED_RULE"
    elif memorization_or_lookup or (not leak_clean) or rule_reduces_to_knn:
        verdict = "HARD_FAIL_MEMORIZATION_OR_SIMILARITY_LOOKUP"
    else:
        verdict = "MIDDLE_BAND"

    elapsed = time.perf_counter() - t0
    msg = (f"{verdict} | out-of-sample PP-attachment census: {census['n_pp_instances']} instances, "
           f"{census['n_base_errors']} parser errors (base_acc={census['base_acc_all']}, "
           f"parser_uas_dev={parser_info['uas_dev']}); PER-CLUSTER GATE: {n_clusters_total} clusters total "
           f"({n_rule_total} promoted to RULE / {n_episodic_total} stayed EPISODIC-ONLY, "
           f"rule_ratio={rule_cluster_ratio}); held-out (verb-disjoint) generalization: "
           f"CLUSTER_GATED fix_rate={m_fix} (base_rate={m_base}, net_gain={m_gain}, rescue_prec={m_prec}) | "
           f"SCRAMBLE collapse={m_collapse} (need>={SCRAMBLE_COLLAPSE_MIN}) | ZERO_CYCLES net_gain={m_zero_gain} "
           f"(need flat <= {ZERO_CYCLES_FLAT_MAX}) | KNN_SIMILARITY fix={m_knn_fix} gain={m_knn_gain} "
           f"(CG beat_margin={m_beat_knn}, need>={BEAT_MARGIN_HARD_PASS}) | MEMORIZE fix={m_memo_fix} "
           f"gain={m_memo_gain} (CG beat_margin={m_beat_memo}, need>={BEAT_MARGIN_HARD_PASS}) | "
           f"rule_knn_agreement={m_rule_knn_agree} (>=0.95 = trap-fired) | vs UNGATED(coherent) fix="
           f"{m_fix_ungated} gain={m_gain_ungated} collapse={m_collapse_ungated} (CG beats ungated by "
           f"{m_beat_ungated}) | leak_clean={leak_clean} baseline_in_band={baseline_in_band}")

    payload = {
        "anchor_name": ANCHOR_NAME, "run_mode": mode, "verdict": verdict, "verdict_msg": msg, "summary": msg,
        "elapsed_s": round(elapsed, 2), "ts_iso": datetime.now(timezone.utc).isoformat(),
        "seeds": cfg["seeds"], "expected_n_seed_rows": len(cfg["seeds"]), "n_seed_rows": len(per_seed),
        "cardinality_ok": bool(len(per_seed) == len(cfg["seeds"])),
        "census": census, "parser_info": parser_info,
        "PRIMARY_heldout_fix_rate_cluster_gated": m_fix, "base_rate_majority": m_base,
        "heldout_net_gain_cluster_gated": m_gain, "rescue_precision_cluster_gated": m_prec,
        "MUSTFAIL_scramble_gain_collapse": m_collapse, "scramble_collapses_gain": scramble_collapses,
        "MUSTFAIL_zero_cycles_net_gain": m_zero_gain, "zero_cycles_flat": zero_cycles_flat,
        "CONTROL_knn_similarity_fix_rate": m_knn_fix, "CONTROL_knn_similarity_net_gain": m_knn_gain,
        "CONTROL_memorize_fix_rate": m_memo_fix, "CONTROL_memorize_net_gain": m_memo_gain,
        "beat_knn_margin_mean": m_beat_knn, "beat_memo_margin_mean": m_beat_memo,
        "beat_ungated_margin_mean": m_beat_ungated,
        "beats_knn_hard_pass": beats_knn_hp, "beats_memo_hard_pass": beats_memo_hp,
        "all_seeds_net_gain_positive": all_seeds_gain_pos, "all_seeds_beat_knn": all_seeds_beat_knn,
        "all_seeds_beat_memo": all_seeds_beat_memo,
        "rule_knn_agreement_mean": m_rule_knn_agree, "rule_reduces_to_knn_trap_fired": rule_reduces_to_knn,
        "n_clusters_total": n_clusters_total, "n_rule_clusters_total": n_rule_total,
        "n_episodic_clusters_total": n_episodic_total, "rule_cluster_ratio": rule_cluster_ratio,
        "UNGATED_COMPARISON_fix_rate": m_fix_ungated, "UNGATED_COMPARISON_net_gain": m_gain_ungated,
        "UNGATED_COMPARISON_scramble_collapse": m_collapse_ungated,
        "fast_seen_recall_mean": m_recall,
        "leak_clean": leak_clean, "baseline_in_band": baseline_in_band, "baseline_heldout_acc": base_acc,
        "final_metrics_atomicity": "tmp_replace", "crlb_n_a": "generalization fix-rate; noise floor=1/n_heldout_fail",
        "progress_logging": "print_flush_true", "compute_architecture": "sequential-CPU (justified <6min)",
        "calibration_check": "adaptive_with_discriminator_gate (tau on SEEN net_gain; scramble+zero_cycles+knn+memo verify fire)",
        "deterministic_seeding": True, "compose_in_cell_no_hdlab_mutation": True,
        "additive_store_note": "Per-cluster gate (USER 2026-07-23): rule clusters consolidated via continual."
                               "replay_cycle over CENTROIDS (prototype abstraction, not raw per-item Hebbian sum); "
                               "episodic clusters use near-exact cosine recall only, no generalization claimed. "
                               "role_space=W@sig over centroids is still linear (atom 29440 lineage) -- the "
                               "knn_similarity + memorize arms + rule_knn_agreement diagnostic are the load-bearing "
                               "checks for whether promoted rules genuinely beat item-level similarity or just "
                               "reproduce it at cluster granularity",
        "per_seed": per_seed,
    }
    write_metrics(output_dir, payload)
    print(f"[{ANCHOR_NAME}:{mode}] DONE {round(elapsed,1)}s -> {verdict}", flush=True)
    print(msg, flush=True)
    return payload


def self_test():
    print("=== parser case+sleep (PP-attachment) self-test (real code paths) ===", flush=True)
    W, parser_info = train_dep_parser("smoke")
    assert parser_info["uas_dev"] > 0.4, f"parser UAS suspiciously low: {parser_info}"
    dev = read_conllu("en_ewt-ud-dev.conllu")[:400]
    instances = attach_predictions(dev, W)
    assert instances, "no PP-attachment instances extracted at smoke scale"
    assert all(a["gold_class"] in ROLES for a in instances)
    n_fail = sum(1 for a in instances if a["is_fail"])
    assert n_fail > 0, "zero parser errors on PP-attachment at smoke scale (discriminator dead)"
    base_acc = 1 - n_fail / len(instances)
    assert 0.05 < base_acc < 0.98, f"base_acc {base_acc} outside plausible band (baseline_in_band check)"

    # leak: signature deterministic + gold-free + mutation-invariant
    a0 = instances[0]
    s1 = signature(a0)
    s2 = signature(a0)
    assert np.array_equal(s1, s2), "signature not deterministic"
    leak = _leak_probe(instances[:80])
    assert leak, "LEAK: signature not gold-free / not mutation-invariant"

    seen, held, seen_v = verb_split(instances, 7, 0.6)
    sf = [a for a in seen if a["is_fail"]]
    if len(sf) >= 4:
        roles = list(ROLES)
        rcb = build_role_codebook(roles)
        W_store = consolidate_store([a["sig"] for a in sf], [a["gold_class"] for a in sf], rcb,
                                    n_cycles=2, replay_frac=1.0)
        assert W_store.shape == (N_SIG, N_SIG)
        r, m = store_predict(W_store, rcb, roles, sf[0]["sig"])
        assert r in roles and isinstance(m, float)
        ev = eval_heldout(lambda a: store_predict(W_store, rcb, roles, a["sig"]), held, 0.0)
        assert set(("fixes", "breaks", "heldout_fix_rate")).issubset(ev)

        # arms_differ_verified (META_RULE_AF): coherent vs scrambled predicted-class tuples differ
        rng = np.random.default_rng(3)
        scr_roles = [(a["gold_class"]) for a in sf]
        scr_roles = [scr_roles[j] for j in rng.permutation(len(scr_roles))]
        W_scr = consolidate_store([a["sig"] for a in sf], scr_roles, rcb, n_cycles=2, replay_frac=1.0)
        assert not np.array_equal(W_store, W_scr) or len(set(scr_roles)) == 1, \
            "META_RULE_AF: scramble store bit-identical to coherent"

        # knn + memorize real code paths
        r_knn, m_knn = knn_predict([a["sig"] for a in sf], [a["gold_class"] for a in sf], sf[0]["sig"], k=3)
        assert r_knn in roles
        memo = {}
        for a in sf:
            memo.setdefault(a["key"], a["gold_class"])
        r_memo, m_memo = memorize_predict(memo, sf[0]["key"], Counter([a["gold_class"] for a in sf]).most_common(1)[0][0])
        assert r_memo in roles

        fr = _fast_seen_recall(sf)
        assert fr is None or 0.0 <= fr <= 1.0

        # PER-CLUSTER GATE real code path (USER design reinforcement 2026-07-23).
        W_rule, ep_sigs, ep_roles, csum = build_cluster_gated_store(sf, rcb, roles, n_cycles=2, replay_frac=1.0)
        assert W_rule.shape == (N_SIG, N_SIG)
        assert csum["n_clusters"] >= 0 and csum["n_rule_clusters"] + csum["n_episodic_clusters"] == csum["n_clusters"]
        n_cases_in_rule_clusters = sum(c["size"] for c in csum["clusters"] if c["promoted_to_rule"])
        assert n_cases_in_rule_clusters + csum["n_episodic_cases"] == len(sf) or csum["n_clusters"] == 0
        tau_rule = calibrate_tau_rule_only(W_rule, rcb, roles, seen)
        cg_fn = cluster_gated_predict_factory(W_rule, rcb, roles, ep_sigs, ep_roles, tau_rule)
        ev_cg = eval_heldout(cg_fn, held, 0.0)
        assert set(("fixes", "breaks", "heldout_fix_rate")).issubset(ev_cg)
        assert len(cg_fn.fire_log) == len(held), "fire_log length mismatch (routing not tracked per held-out item)"
        sources = set(src for src, _r in cg_fn.fire_log)
        assert sources.issubset({"RULE", "EPISODIC", "NONE"})
        print(f"[selftest] cluster-gate real path OK: n_clusters={csum['n_clusters']} "
              f"rule={csum['n_rule_clusters']} episodic={csum['n_episodic_clusters']} "
              f"fire_log_sources={sources}", flush=True)
    print(f"[selftest] real store/knn/memorize paths OK: n_instances={len(instances)} n_fail={n_fail} "
          f"base_acc={round(base_acc,4)} n_seen_fail={len(sf)} n_verbs={len(seen_v)}", flush=True)
    print("[selftest] PASS", flush=True)
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["smoke", "full"], default="full")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
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
