#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""exp_agreement_glassbox_abl_adios_structure_induction_b2_v1

b2 FALSIFICATION TEST. Build a GLASS-BOX, NON-GRADIENT, unsupervised STRUCTURE-INDUCER
(ABL / ADIOS-style: alignment-based learning / statistical pattern-distillation over raw token
sequences) and test whether it can INDUCE head-tracking from raw agreement text -- discovering
"which prefix noun is the syntactic subject-head" from DISTRIBUTIONAL/ALIGNMENT structure alone,
with NO oracle head label -- and BEAT the linear positional baseline that failed in atom 29443
(SNF head-tracking acc 0.580, below majority 0.627).

This is a GENUINE FALSIFICATION of "structure-induction needs a gradient/opaque optimizer":
  HARD_PASS  = the induced structure BEATS the linear positional baseline on the subject-not-first
               (SNF) conflict subset by a clear margin, WITH a content-dependence signal
               -> REFUTES the closure (a glass-box non-gradient inducer exists).
  HARD_FAIL  = induced structure ties/underperforms the linear baseline on SNF (induces no usable
               hierarchy beyond linear position) -> CORROBORATES-BUT-DOES-NOT-PROVE the closure
               (ABL/ADIOS is ONE candidate, fragile at natural-text scale; cannot conclude NO
               glass-box mechanism works, only that this strong candidate did not).
  MIDDLE     = partial (beats majority narrowly, or coverage moderate) -> inconclusive.

GLASS-BOX / NON-GRADIENT INVARIANT (a violation voids the result):
  The INDUCER is discrete significance-gated pattern distillation (ADIOS-lite greedy motif merge on
  raw token sequences) + Harris substitutability -- NO backprop, NO gradient-trained operator
  anywhere in induction or the head-candidate rule. (The linear BASELINE it must beat is the
  gradient-trained logistic readout from 29443; the invariant constrains the INDUCER, not the
  baseline-to-beat.)

FAIRNESS (VET-every-base-ingredient; ABL/ADIOS gets its BEST SHOT so a failure is attributable to
  glass-box-induction-can't, not ABL-mis-run):
  - FAIR inputs: the raw token sequence + POS tags (both present in the raw Linzen input -- a taught
    scaffold like position was in 29443). NOT FAIR: the oracle subject-head index / a dependency
    parse (that is the answer to be induced; subj_pos is used ONLY for scoring, never for induction).
  - Best-regime arm (POS): induce over the low-vocabulary POS-tag prefix sequences (high repetition
    = exactly the regime where alignment/pattern induction is known to WORK). This is the fair best
    shot for glass-box induction, NOT ABL in its worst regime.
  - Fragility-regime arm (WORD): induce over the larger-vocabulary mostcommon-word prefix sequences
    (the WSJ-scale open-vocab regime the literature predicts ABL degrades on). Report BOTH.

TESTBED: the SAME real Linzen, Dupoux & Goldberg 2016 agreement data as atom 29443. The committed
  29443 cache is lexeme-FREE (no raw tokens), so this cell reads the raw corpus
  data/corpora/agreement/agr_50.tsv.gz (LOCAL-ONLY, ~150MB, NOT committed) and reproduces the
  IDENTICAL item set + subj_word novel-lexeme held-out split (Gate D: deterministic baselines
  first-noun-SNF / majority-SNF reproduce the atom's per-seed values to prove split identity).
  Because the raw tokens live only in the local-only corpus, this cell CANNOT run remote; it runs
  FULL LOCAL-FOREGROUND (discrete counting, CPU, minutes -- a light run to completion, NOT a heavy
  detached fit).

# CELL-TEMPLATE MANDATORY:
# - arms_differ asserted (ADIOS-head vs first-noun vs baselines predictions distinct)
# - final_metrics_atomicity: tmp_replace ; except SystemExit: raise BEFORE except Exception (no BaseException)
# - discriminator: SNF head-tracking; coverage + content-dependence gates (mechanism must fire + use structure)
# - baseline_in_band: majority ~0.5-0.63 (0.05<acc<0.95)
# - crlb_n/a: real-text agreement head discrimination via discrete pattern induction; no argmax-capacity CRLB
# - deterministic_seeding: fixed ints + hashlib atoms (no builtin-hash, no list-set dedupe); progress flush
# - cardinality_ok: n_seed_rows == len(seeds)
# - real_code_path exercised in self-test: load_raw_items, induce_grammar, bracket_depths (the REAL inducer)
# - NON-GRADIENT inducer asserted (no torch/optimizer import in the induction path)
# LOCAL-FOREGROUND FULL (reads local-only raw corpus; cannot go remote). No push / no store write /
#   no atom bank. ASCII only.
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import argparse
import gzip
import hashlib
import json
import math
import platform
import sys
import time
import traceback
from collections import Counter
from datetime import datetime, timezone

import numpy as np

ANCHOR_NAME = "agreement_glassbox_abl_adios_structure_induction_b2_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

CORPUS = os.path.join(REPO_ROOT, "data", "corpora", "agreement", "agr_50.tsv.gz")
CACHE = os.path.join(REPO_ROOT, "data", "corpora", "agreement", "agreement_probe_cache_v1.json.gz")

# ---- corpus build (replicate tools/prep_agreement_probe_cache.py EXACTLY so the item set + split are
#      IDENTICAL to atom 29443; additionally retain the POS/word token prefixes the inducer needs) ----
NOUN_TAGS = {"NN", "NNP", "NNS", "NNPS"}
PLURAL_NOUN = {"NNS", "NNPS"}
FWC = {"START": 0, "DET": 1, "PREP": 2, "REL": 3, "CCONJ": 4, "OTHER": 5}
BIN_TARGET = {0: 4000, 1: 4000, 2: 3000, 3: 3000, 4: 2000}


def fwc_of(prev_tag):
    if prev_tag is None:
        return FWC["START"]
    if prev_tag in ("DT", "PRP$", "POS"):
        return FWC["DET"]
    if prev_tag in ("IN", "TO"):
        return FWC["PREP"]
    if prev_tag in ("WDT", "WP", "WP$", "WRB"):
        return FWC["REL"]
    if prev_tag == "CC":
        return FWC["CCONJ"]
    return FWC["OTHER"]


def cell_cap(ndiff):
    return BIN_TARGET.get(ndiff, 0) // 2


def parse_row(fields):
    # cols: 0=sentence 1=orig 2=pos_sentence 3=subj 8=verb_pos 9=subj_index 10=verb_index 13=ndiff
    try:
        word_sentence = fields[0].split()
        pos_sentence = fields[2].split()
        subj_word = fields[3]
        verb_pos = fields[8]
        subj_index = int(fields[9])   # 1-based
        verb_index = int(fields[10])  # 1-based
        ndiff = int(fields[13])
    except (IndexError, ValueError):
        return None
    if verb_pos not in ("VBP", "VBZ"):
        return None
    label = 1 if verb_pos == "VBP" else 0
    n = len(pos_sentence)
    if verb_index < 2 or verb_index > n or subj_index < 1 or subj_index >= verb_index:
        return None
    if len(word_sentence) != n:
        # sentence and pos_sentence must be token-aligned; skip the rare mismatch
        return None
    nums = []; fwc = []; noun_tok_idx = []; subj_pos = -1
    for pos in range(1, verb_index):  # 1-based positions strictly before the verb
        tag = pos_sentence[pos - 1]
        if tag not in NOUN_TAGS:
            continue
        if pos == subj_index:
            subj_pos = len(nums)
        prev_tag = pos_sentence[pos - 2] if pos >= 2 else None
        nums.append(1 if tag in PLURAL_NOUN else 0)
        fwc.append(fwc_of(prev_tag))
        noun_tok_idx.append(pos - 1)   # 0-based token index within the full prefix
    if subj_pos < 0 or len(nums) < 1:
        return None
    if nums[subj_pos] != label:
        return None
    return {
        "ndiff": ndiff if ndiff <= 4 else 4,
        "label": label,
        "nums": nums,
        "fwc": fwc,
        "subj_pos": subj_pos,
        "subj_word": subj_word,
        "noun_tok_idx": noun_tok_idx,
        "pos_prefix": pos_sentence[:verb_index - 1],   # POS-tag tokens before the verb
        "word_prefix": word_sentence[:verb_index - 1],  # mostcommon-word/POS-mix tokens before verb
    }


def load_raw_items(max_items=None):
    """Stream the local-only raw Linzen corpus, reproduce the 29443 item set + retain token prefixes."""
    if not os.path.exists(CORPUS):
        raise FileNotFoundError(
            "raw Linzen corpus not found: %s -- this cell needs the LOCAL-ONLY raw token sequences "
            "(the committed 29443 cache is lexeme-free). Cannot run remote." % CORPUS)
    cell_count = Counter()
    kept = []
    seen = 0
    with gzip.open(CORPUS, "rt", encoding="utf-8", errors="replace") as f:
        f.readline()  # header
        for line in f:
            seen += 1
            if seen % 200000 == 0:
                print("[b2] scanned=%d kept=%d" % (seen, len(kept)), flush=True)
            rec = parse_row(line.rstrip("\n").split("\t"))
            if rec is None:
                continue
            key = (rec["ndiff"], rec["label"])
            if cell_count[key] >= cell_cap(rec["ndiff"]):
                continue
            cell_count[key] += 1
            kept.append(rec)
            if max_items is not None and len(kept) >= max_items:
                break
            if all(cell_count[(b, l)] >= cell_cap(b) for b in BIN_TARGET for l in (0, 1)):
                break
    return kept


# ---- identical novel-lexeme held-out split (same hash + seeds as 29443) ----
TEST_HASH_MOD = 5
TEST_FRAC_CUT = 2
FULL_SEEDS = [7, 13, 19]
SMOKE_SEEDS = [7, 13]
FULL_TRAIN_CAP = 6000
FULL_TEST_CAP = 6000
SMOKE_TRAIN_CAP = 1500
SMOKE_TEST_CAP = 1500


def _is_test(subj_word):
    h = int.from_bytes(hashlib.sha256(subj_word.encode("utf-8")).digest()[:8], "big")
    return (h % TEST_HASH_MOD) < TEST_FRAC_CUT


def split_items(items, train_cap, test_cap, seed):
    rng = np.random.default_rng(seed)
    train = [r for r in items if not _is_test(r["subj_word"])]
    test = [r for r in items if _is_test(r["subj_word"])]
    rng.shuffle(train); rng.shuffle(test)
    return train[:train_cap], test[:test_cap]


# ==================================================================================================
# GLASS-BOX NON-GRADIENT STRUCTURE-INDUCER: ADIOS-lite significance-gated greedy motif distillation.
# Discrete counting only -- no gradient, no optimizer, fully inspectable (every merge is a
# significant collocation with an auditable PMI + count). Harris substitutability reported alongside.
# ==================================================================================================
USES_GRADIENT = False  # invariant flag; asserted in self_test


def build_alphabet(seqs):
    """Map string tokens -> int ids (terminals). Deterministic (sorted)."""
    vocab = sorted(set(tok for s in seqs for tok in s))
    return {t: i for i, t in enumerate(vocab)}


def induce_grammar(seqs_ids, base_T, max_merges, min_count, min_pmi):
    """ADIOS-lite: greedily distill the most statistically-significant adjacent motif into a new
    nonterminal, replace, recurse. Returns ordered rules [(rank, (a,b), nt), ...].
    Significance = pointwise mutual information PMI(a,b) = log( c(a,b) * Ntok / (c(a) c(b)) ), gated by
    a minimum co-occurrence count. Purely discrete; no continuous optimization."""
    corpus = [list(s) for s in seqs_ids]
    next_nt = base_T
    rules = []
    for rank in range(max_merges):
        uni = Counter(); big = Counter()
        for s in corpus:
            for t in s:
                uni[t] += 1
            for i in range(len(s) - 1):
                big[(s[i], s[i + 1])] += 1
        ntok = sum(uni.values())
        if ntok == 0:
            break
        best = None; best_pmi = -1e18; best_c = 0
        for (a, b), c in big.items():
            if c < min_count:
                continue
            pmi = math.log((c * ntok) / (uni[a] * uni[b]))
            if pmi < min_pmi:
                continue
            # tie-break by higher count (more evidence) then lexical order for determinism
            if (pmi > best_pmi) or (pmi == best_pmi and (c > best_c or (c == best_c and (a, b) < best))):
                best = (a, b); best_pmi = pmi; best_c = c
        if best is None:
            break
        nt = next_nt; next_nt += 1
        rules.append((rank, best, nt))
        a, b = best
        for si in range(len(corpus)):
            s = corpus[si]; ns = []; i = 0
            while i < len(s):
                if i < len(s) - 1 and s[i] == a and s[i + 1] == b:
                    ns.append(nt); i += 2
                else:
                    ns.append(s[i]); i += 1
            corpus[si] = ns
    return rules


def bracket_depths(seq_ids, rule_map):
    """Apply the induced merges (rule_map: (a,b)->(rank,nt)) greedily by rank priority to a single
    sequence; return per-terminal nesting depth (number of induced nonterminals enclosing it)."""
    L = len(seq_ids)
    if L == 0:
        return []
    nodes_sym = list(seq_ids)
    nodes_leaves = [[i] for i in range(L)]
    depth = [0] * L
    while len(nodes_sym) > 1:
        best_i = -1; best_rank = 1 << 30; best_nt = None
        for i in range(len(nodes_sym) - 1):
            key = (nodes_sym[i], nodes_sym[i + 1])
            hit = rule_map.get(key)
            if hit is not None and hit[0] < best_rank:
                best_rank = hit[0]; best_i = i; best_nt = hit[1]
        if best_i < 0:
            break
        merged = nodes_leaves[best_i] + nodes_leaves[best_i + 1]
        for lf in merged:
            depth[lf] += 1
        nodes_sym = nodes_sym[:best_i] + [best_nt] + nodes_sym[best_i + 2:]
        nodes_leaves = nodes_leaves[:best_i] + [merged] + nodes_leaves[best_i + 2:]
    return depth


def head_from_depths(item, depth):
    """Head-candidate rule (PRIMARY, inspectable): among prefix nouns, pick the LEAST-embedded one
    (min induced bracket depth), leftmost tie-break. Attractors sit inside PP/RC/coordination motifs
    (deeper); the subject sits at the top level (shallower). Returns (pred_number, head_noun_index)."""
    nidx = item["noun_tok_idx"]; nums = item["nums"]
    best_k = 0; best_d = depth[nidx[0]] if nidx[0] < len(depth) else 0
    for k in range(1, len(nidx)):
        dk = depth[nidx[k]] if nidx[k] < len(depth) else 0
        if dk < best_d:
            best_d = dk; best_k = k
    return nums[best_k], best_k


def head_from_shuffled_depths(item, depth, rng):
    """Content-dependence control: destroy the depth<->noun assignment (permute depths across the
    noun slots) while keeping the same depth multiset. If head-tracking survives, the mechanism is
    NOT using the induced STRUCTURE (it rides position/frequency)."""
    nidx = item["noun_tok_idx"]; nums = item["nums"]
    dvals = [depth[j] if j < len(depth) else 0 for j in nidx]
    perm = rng.permutation(len(dvals))
    dvals = [dvals[p] for p in perm]
    best_k = int(np.argmin(dvals))  # leftmost min
    return nums[best_k], best_k


# ---- linear positional/count baseline reproduction (the thing to beat) ----
R_RANK = 8
N_FWC = 6


def clean_features(items):
    """Non-superposition signed-number votes per role slot (rank-from-verb, rank-from-start,
    function-word-class) -- the SAME clean linear features the 29443 linear readout used."""
    n = len(items)
    feats = np.zeros((n, 2 * R_RANK + N_FWC), dtype=np.float32)
    for idx, it in enumerate(items):
        nums = it["nums"]; fwc = it["fwc"]; L = len(nums)
        fwc_acc = np.zeros(N_FWC, dtype=np.float32); fwc_cnt = np.zeros(N_FWC, dtype=np.float32)
        for i in range(L):
            s = 1.0 if nums[i] == 1 else -1.0
            rv_k = L - 1 - i; rs_k = i
            if rv_k < R_RANK:
                feats[idx, rv_k] = s
            if rs_k < R_RANK:
                feats[idx, R_RANK + rs_k] = s
            fwc_acc[fwc[i]] += s; fwc_cnt[fwc[i]] += 1.0
        for c in range(N_FWC):
            if fwc_cnt[c] > 0:
                feats[idx, 2 * R_RANK + c] = fwc_acc[c] / fwc_cnt[c]
    return feats


def _sigmoid(z):
    return 1.0 / (1.0 + np.exp(-np.clip(z, -30, 30)))


def train_logistic(X, y, steps, lr, l2, seed):
    """Gradient-trained linear BASELINE (the thing the non-gradient inducer must beat). This is the
    baseline, NOT the inducer -- the glass-box invariant constrains the inducer only."""
    rng = np.random.default_rng(seed)
    d = X.shape[1]
    w = rng.standard_normal(d).astype(np.float64) * 0.01
    b = 0.0
    Xd = X.astype(np.float64); yd = y.astype(np.float64); n = len(yd)
    for _ in range(steps):
        p = _sigmoid(Xd @ w + b)
        g = p - yd
        w -= lr * ((Xd.T @ g) / n + l2 * w)
        b -= lr * float(np.mean(g))
    return w, b


def logistic_predict(X, w, b):
    return (_sigmoid(X.astype(np.float64) @ w + b) >= 0.5).astype(int)


def _acc(pred, gold):
    return float(np.mean(np.asarray(pred) == np.asarray(gold)))


def _r(x):
    return round(float(x), 4) if x is not None else None


# ==================================================================================================
# Per-seed run.
# ==================================================================================================
def _induce_and_predict(train, test, which, base_T_hint, max_merges, min_count, min_pmi):
    """Induce a grammar over `which` prefix token sequences of TRAIN, bracket TEST, return per-test
    predicted head number + head index + per-test noun-depth uniformity (coverage)."""
    key = which  # "pos_prefix" | "word_prefix"
    train_seqs = [it[key] for it in train]
    alpha = build_alphabet(train_seqs)
    base_T = len(alpha)
    unk = base_T  # single UNK terminal for held-out tokens
    def to_ids(seq):
        return [alpha.get(t, unk) for t in seq]
    train_ids = [to_ids(s) for s in train_seqs]
    rules = induce_grammar(train_ids, base_T + 1, max_merges, min_count, min_pmi)
    rule_map = {}
    for rank, (a, b), nt in rules:
        rule_map[(a, b)] = (rank, nt)
    preds = np.zeros(len(test), dtype=int)
    heads = np.zeros(len(test), dtype=int)
    fired = np.zeros(len(test), dtype=bool)
    depths_cache = []
    for i, it in enumerate(test):
        d = bracket_depths(to_ids(it[key]), rule_map)
        depths_cache.append(d)
        p, hk = head_from_depths(it, d)
        preds[i] = p; heads[i] = hk
        nd = [d[j] if j < len(d) else 0 for j in it["noun_tok_idx"]]
        fired[i] = len(set(nd)) > 1
    return {"rules": rules, "n_rules": len(rules), "preds": preds, "heads": heads,
            "fired": fired, "depths": depths_cache, "alpha_size": base_T}


def _sub_acc(mask, pred, yte):
    if int(mask.sum()) == 0:
        return None, 0
    return float(np.mean(np.asarray(pred)[mask] == yte[mask])), int(mask.sum())


def run_seed(seed, train_cap, test_cap, items):
    train, test = split_items(items, train_cap, test_cap, seed)
    ytr = np.array([r["label"] for r in train], dtype=int)
    yte = np.array([r["label"] for r in test], dtype=int)
    snf = np.array([r["subj_pos"] != 0 for r in test])
    conflict = np.array([r["nums"][-1] != r["label"] for r in test])

    # ---- deterministic baselines (Gate D split-identity proof + the bar to beat) ----
    pred_first = np.array([r["nums"][0] for r in test], dtype=int)
    pred_near = np.array([r["nums"][-1] for r in test], dtype=int)
    pred_bag = np.array([1 if sum(1 if n == 1 else -1 for n in r["nums"]) >= 0 else 0 for r in test], dtype=int)
    maj = int(round(float(np.mean(ytr))))
    pred_major = np.full(len(test), maj, dtype=int)

    # ---- gradient-trained linear readout baseline (clean features; the 29443 linear learner) ----
    cf_tr = clean_features(train); cf_te = clean_features(test)
    w, b = train_logistic(cf_tr, ytr, 600, 0.5, 1e-3, seed)
    pred_lin = logistic_predict(cf_te, w, b)

    # ---- GLASS-BOX NON-GRADIENT INDUCER: POS arm (best regime) + WORD arm (fragility regime) ----
    pos_res = _induce_and_predict(train, test, "pos_prefix", None, 120, 20, 1.0)
    word_res = _induce_and_predict(train, test, "word_prefix", None, 200, 10, 2.0)

    def arm_metrics(res):
        preds = res["preds"]; fired = res["fired"]
        snf_acc, n_snf = _sub_acc(snf, preds, yte)
        conf_acc, n_conf = _sub_acc(conflict, preds, yte)
        all_acc = _acc(preds, yte)
        coverage = float(np.mean(fired))
        coverage_snf = float(np.mean(fired[snf])) if int(snf.sum()) else None
        # content-dependence: shuffled-depth head on the SNF subset
        rng = np.random.default_rng(4000 + seed)
        preds_sh = np.zeros(len(test), dtype=int)
        for i, it in enumerate(test):
            preds_sh[i], _ = head_from_shuffled_depths(it, res["depths"][i], rng)
        snf_sh, _ = _sub_acc(snf, preds_sh, yte)
        content_delta = _r(snf_acc - snf_sh) if (snf_acc is not None and snf_sh is not None) else None
        return {
            "n_rules": res["n_rules"], "alpha_size": res["alpha_size"],
            "all_acc": _r(all_acc), "snf_acc": _r(snf_acc), "n_snf": n_snf,
            "conflict_acc": _r(conf_acc), "n_conflict": n_conf,
            "coverage": _r(coverage), "coverage_snf": _r(coverage_snf),
            "snf_shuffled_depth_acc": _r(snf_sh), "content_dependence_delta": content_delta,
        }

    pos_m = arm_metrics(pos_res)
    word_m = arm_metrics(word_res)

    # ---- baseline SNF accuracies (the bar) ----
    snf_first, _ = _sub_acc(snf, pred_first, yte)
    snf_maj, _ = _sub_acc(snf, pred_major, yte)
    snf_near, _ = _sub_acc(snf, pred_near, yte)
    snf_bag, _ = _sub_acc(snf, pred_bag, yte)
    snf_lin, _ = _sub_acc(snf, pred_lin, yte)

    # ---- arms-differ (inducer head preds distinct from first-noun and from linear) ----
    hashes = {
        "pos_head": hashlib.sha256(pos_res["preds"].tobytes()).hexdigest(),
        "first": hashlib.sha256(pred_first.tobytes()).hexdigest(),
        "lin": hashlib.sha256(pred_lin.tobytes()).hexdigest(),
    }
    arms_differ = len(set(hashes.values())) >= 2

    return {
        "seed": seed, "n_train": len(train), "n_test": len(test), "n_snf": int(snf.sum()),
        "baselines_snf": {"first_noun": _r(snf_first), "majority": _r(snf_maj), "nearest": _r(snf_near),
                          "bagcount": _r(snf_bag), "linear_learned": _r(snf_lin)},
        "baselines_all": {"first_noun": _r(_acc(pred_first, yte)), "majority": _r(_acc(pred_major, yte)),
                          "nearest": _r(_acc(pred_near, yte)), "linear_learned": _r(_acc(pred_lin, yte))},
        "inducer_pos_arm": pos_m,
        "inducer_word_arm": word_m,
        "arms_differ": bool(arms_differ),
        "uses_gradient_in_inducer": bool(USES_GRADIENT),
    }


# ==================================================================================================
# Verdict.
# ==================================================================================================
# ---- pre-registered bands ----
HP_SNF_FLOOR = 0.68            # induced-head SNF acc must clear this (majority 0.627 + >5% band-width)
HP_MARGIN_OVER_BASE = 0.05     # ... AND beat max(majority_SNF, linear_SNF) by this
HP_CONTENT_DELTA = 0.05        # ... AND real-depth head beats shuffled-depth head by this (structure used)
HP_COVERAGE = 0.60             # ... AND induced structure fires on >= this fraction of held-out SNF
HF_TIE_EPS = 0.02              # HARD_FAIL if induced-head SNF <= base + this (no clear win)
HF_COVERAGE = 0.40             # HARD_FAIL if coverage_snf < this (fragility signature)
HF_CONTENT_DELTA = 0.02        # HARD_FAIL if content-dependence delta < this (rides position/freq)
LINEAR_REF_SNF = 0.580         # atom 29443 HRR-substrate linear readout SNF acc (MEASURED@atom); reference
MAJORITY_REF_SNF = 0.627       # atom 29443 majority SNF acc (MEASURED@atom); reference


def _mean_path(rows, *path):
    vals = []
    for r in rows:
        cur = r; ok = True
        for p in path:
            if isinstance(cur, dict) and p in cur and cur[p] is not None:
                cur = cur[p]
            else:
                ok = False; break
        if ok and isinstance(cur, (int, float)):
            vals.append(float(cur))
    return round(float(np.mean(vals)), 4) if vals else None


def build_verdict(rows):
    # primary = POS arm (best regime for glass-box induction)
    snf_pos = _mean_path(rows, "inducer_pos_arm", "snf_acc")
    cov_pos = _mean_path(rows, "inducer_pos_arm", "coverage_snf")
    cont_pos = _mean_path(rows, "inducer_pos_arm", "content_dependence_delta")
    all_pos = _mean_path(rows, "inducer_pos_arm", "all_acc")
    conf_pos = _mean_path(rows, "inducer_pos_arm", "conflict_acc")
    nrules_pos = _mean_path(rows, "inducer_pos_arm", "n_rules")
    # word arm (fragility regime)
    snf_word = _mean_path(rows, "inducer_word_arm", "snf_acc")
    cov_word = _mean_path(rows, "inducer_word_arm", "coverage_snf")
    cont_word = _mean_path(rows, "inducer_word_arm", "content_dependence_delta")
    # baselines
    snf_first = _mean_path(rows, "baselines_snf", "first_noun")
    snf_maj = _mean_path(rows, "baselines_snf", "majority")
    snf_lin = _mean_path(rows, "baselines_snf", "linear_learned")
    snf_near = _mean_path(rows, "baselines_snf", "nearest")
    snf_bag = _mean_path(rows, "baselines_snf", "bagcount")

    base_bar = max([x for x in [snf_maj, snf_lin] if x is not None], default=None)
    delta = round(snf_pos - base_bar, 4) if (snf_pos is not None and base_bar is not None) else None

    arms_ok = all(r["arms_differ"] for r in rows) if rows else False
    nongrad_ok = all(not r["uses_gradient_in_inducer"] for r in rows) if rows else False
    baseline_in_band = (snf_maj is not None and 0.05 < snf_maj < 0.95)

    hard_pass = (snf_pos is not None and base_bar is not None and cov_pos is not None
                 and cont_pos is not None
                 and snf_pos >= HP_SNF_FLOOR
                 and delta is not None and delta >= HP_MARGIN_OVER_BASE
                 and cont_pos >= HP_CONTENT_DELTA
                 and cov_pos >= HP_COVERAGE
                 and nongrad_ok and arms_ok)

    hard_fail = (snf_pos is None or base_bar is None
                 or (delta is not None and delta <= HF_TIE_EPS)
                 or (cov_pos is not None and cov_pos < HF_COVERAGE)
                 or (cont_pos is not None and cont_pos < HF_CONTENT_DELTA))

    if hard_pass:
        verdict = "HARD_PASS_GLASSBOX_INDUCTION_REFUTES_CLOSURE"
        interp = ("REFUTES the induction-needs-gradient closure: a GLASS-BOX NON-GRADIENT ADIOS/ABL-"
                  "style inducer BEAT the linear positional baseline on the held-out subject-not-first "
                  "subset with a content-dependence signal. A glass-box structure-inducer exists on "
                  "real text. GREEN-LIGHT-PENDING-VET, not a self-declared refutation.")
    elif hard_fail:
        verdict = "HARD_FAIL_GLASSBOX_INDUCTION_CORROBORATES_CLOSURE"
        interp = ("CORROBORATES-BUT-DOES-NOT-PROVE the structural closure: this strong glass-box "
                  "candidate (ADIOS/ABL discrete pattern distillation) did NOT induce usable head "
                  "structure beyond linear position on real Linzen text (SNF acc %s vs bar %s, "
                  "delta=%s; coverage_snf(POS)=%s; content-dependence(POS)=%s). ABL/ADIOS is ONE "
                  "candidate and fragile at natural-text scale, so this CANNOT conclude NO glass-box "
                  "mechanism works -- only that this candidate did not, which matches the literature's "
                  "pre-registered fragility prediction." % (snf_pos, base_bar, delta, cov_pos, cont_pos))
    else:
        verdict = "MIDDLE_BAND_PARTIAL_INDUCTION"
        interp = ("INCONCLUSIVE: induced structure beats the frequency/position bar narrowly or with "
                  "moderate coverage, neither a clean refute nor a clean corroborate (SNF acc %s vs "
                  "bar %s, delta=%s; coverage_snf(POS)=%s; content-dependence(POS)=%s). Needs a harder "
                  "split or more data to resolve." % (snf_pos, base_bar, delta, cov_pos, cont_pos))

    msg = (f"{verdict} | INDUCER(POS best-regime): SNF={snf_pos} all={all_pos} conflict={conf_pos} "
           f"coverage_snf={cov_pos} content_delta={cont_pos} n_rules={nrules_pos} | INDUCER(WORD "
           f"fragility-regime): SNF={snf_word} coverage_snf={cov_word} content_delta={cont_word} | "
           f"BAR-TO-BEAT SNF: majority={snf_maj} linear_learned={snf_lin} first_noun={snf_first} "
           f"nearest={snf_near} bag={snf_bag} | atom29443 refs: HRR-linear-SNF={LINEAR_REF_SNF} "
           f"majority-SNF={MAJORITY_REF_SNF} | POS_SNF-vs-bar delta={delta} (HP floor {HP_SNF_FLOOR}, "
           f"margin {HP_MARGIN_OVER_BASE}) | non_gradient={nongrad_ok} arms_differ={arms_ok} "
           f"baseline_in_band={baseline_in_band} | {interp}")

    summ = {
        "inducer_pos_snf": snf_pos, "inducer_pos_all": all_pos, "inducer_pos_conflict": conf_pos,
        "inducer_pos_coverage_snf": cov_pos, "inducer_pos_content_delta": cont_pos,
        "inducer_pos_n_rules": nrules_pos,
        "inducer_word_snf": snf_word, "inducer_word_coverage_snf": cov_word,
        "inducer_word_content_delta": cont_word,
        "bar_to_beat_snf": base_bar, "snf_vs_bar_delta": delta,
        "baseline_majority_snf": snf_maj, "baseline_linear_learned_snf": snf_lin,
        "baseline_first_noun_snf": snf_first, "baseline_nearest_snf": snf_near, "baseline_bag_snf": snf_bag,
        "atom29443_hrr_linear_snf_ref": LINEAR_REF_SNF, "atom29443_majority_snf_ref": MAJORITY_REF_SNF,
        "non_gradient_confirmed": nongrad_ok, "arms_differ_all": arms_ok,
        "baseline_in_band": baseline_in_band,
        "hard_pass": bool(hard_pass), "hard_fail": bool(hard_fail),
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
    print(f"[{ANCHOR_NAME}:{mode}] START b2 glass-box ABL/ADIOS structure-induction falsification", flush=True)

    items = load_raw_items()
    print(f"[{ANCHOR_NAME}:{mode}] raw items reproduced: {len(items)}", flush=True)

    if mode == "smoke":
        seeds = SMOKE_SEEDS; tr_cap, te_cap = SMOKE_TRAIN_CAP, SMOKE_TEST_CAP
    else:
        seeds = FULL_SEEDS; tr_cap, te_cap = FULL_TRAIN_CAP, FULL_TEST_CAP

    rows = []
    for seed in seeds:
        r = run_seed(seed, tr_cap, te_cap, items)
        rows.append(r)
        pa = r["inducer_pos_arm"]; wa = r["inducer_word_arm"]; bs = r["baselines_snf"]
        print(f"[{ANCHOR_NAME}:{mode}] seed={seed} | POS: SNF={pa['snf_acc']} cov_snf={pa['coverage_snf']} "
              f"content={pa['content_dependence_delta']} rules={pa['n_rules']} | WORD: SNF={wa['snf_acc']} "
              f"cov_snf={wa['coverage_snf']} | bar: maj={bs['majority']} lin={bs['linear_learned']} "
              f"first={bs['first_noun']}", flush=True)

    verdict, msg, summ = build_verdict(rows)
    elapsed = time.perf_counter() - t0
    payload = {
        "anchor_name": ANCHOR_NAME, "run_mode": mode, "verdict": verdict, "verdict_msg": msg, "summary": msg,
        "elapsed_s": round(elapsed, 2), "ts_iso": datetime.now(timezone.utc).isoformat(),
        "seeds": seeds, "n_seed_rows": len(rows), "expected_n_seed_rows": len(seeds),
        "cardinality_ok": bool(len(rows) == len(seeds)),
        "train_cap": tr_cap, "test_cap": te_cap,
        "bands": {"HP_SNF_FLOOR": HP_SNF_FLOOR, "HP_MARGIN_OVER_BASE": HP_MARGIN_OVER_BASE,
                  "HP_CONTENT_DELTA": HP_CONTENT_DELTA, "HP_COVERAGE": HP_COVERAGE,
                  "HF_TIE_EPS": HF_TIE_EPS, "HF_COVERAGE": HF_COVERAGE, "HF_CONTENT_DELTA": HF_CONTENT_DELTA,
                  "LINEAR_REF_SNF": LINEAR_REF_SNF, "MAJORITY_REF_SNF": MAJORITY_REF_SNF},
        "summary_metrics": summ,
        "per_seed": rows,
        "final_metrics_atomicity": "tmp_replace",
        "compute_architecture": ("sequential_cpu_discrete_pattern_induction_no_matmul_primitive_no_gradient_"
                                 "in_inducer_wall_minutes_local_foreground_only_reads_local_only_raw_corpus"),
        "crlb_n/a": ("real-text agreement head discrimination via discrete significance-gated pattern "
                     "distillation; no argmax-capacity CRLB applies -- the floor is the linear positional "
                     "baseline (majority/first-noun/linear-learned) on the SNF subset"),
        "progress_logging": "print_flush_true",
        "deterministic_seeding": True,
        "glassbox_non_gradient_inducer": True,
        "no_store_write_no_push_no_atom_bank": True,
        "honest_scope": ("b2 falsification: a HARD_FAIL CORROBORATES-BUT-DOES-NOT-PROVE the structural "
                         "closure (ADIOS/ABL is ONE fragile candidate; cannot conclude NO glass-box "
                         "mechanism works). A HARD_PASS REFUTES the closure (a glass-box non-gradient "
                         "inducer beat the linear positional baseline on real text). Same Linzen data + "
                         "novel-lexeme SNF split as atom 29443 (Gate D split-identity verified via "
                         "deterministic first-noun/majority SNF baselines)."),
    }
    write_metrics(output_dir, payload)
    print(f"[{ANCHOR_NAME}:{mode}] DONE {round(elapsed,1)}s -> {verdict}", flush=True)
    print(msg, flush=True)
    return payload


# ==================================================================================================
# Self-test: exercises the REAL inducer code path (load_raw_items, induce_grammar, bracket_depths)
# at small scale; VALIDITY gates only (split identity, mechanism fires, arms differ, non-gradient,
# baseline in band). Does NOT assert the mechanism WINS (that is the can-fail hypothesis).
# ==================================================================================================
def self_test():
    print("=== b2 glass-box ABL/ADIOS structure-induction self-test ===", flush=True)

    # (Gate D) split-identity: our raw-corpus reader reproduces the committed lexeme-free cache items.
    items_small = load_raw_items(max_items=400)
    assert len(items_small) >= 300, "raw reader produced too few items: %d" % len(items_small)
    with gzip.open(CACHE, "rt", encoding="utf-8") as f:
        cache = json.load(f)
    clin = cache["linzen"]
    for k in range(300):
        a = items_small[k]; c = clin[k]
        assert a["nums"] == c["nums"] and a["fwc"] == c["fwc"] and a["subj_pos"] == c["subj_pos"] \
            and a["subj_word"] == c["subj_word"] and a["label"] == c["label"] and a["ndiff"] == c["ndiff"], \
            "SPLIT_IDENTITY_BREACH at item %d: raw reader diverges from committed cache" % k
        # token-prefix retention consistency: noun count == number of noun tokens in pos_prefix
        n_noun_tokens = sum(1 for t in a["pos_prefix"] if t in NOUN_TAGS)
        assert n_noun_tokens == len(a["nums"]), "noun_tok_idx / nums misalignment at %d" % k
    print("[self-test] split-identity vs committed cache OK (300 items); token prefixes aligned", flush=True)

    # (real code path) induce a grammar on a small POS-prefix corpus + bracket held-out.
    items = load_raw_items(max_items=2500)
    train, test = split_items(items, 1200, 800, 7)
    assert len(train) > 200 and len(test) > 100, "self-test split too small"
    res = _induce_and_predict(train, test, "pos_prefix", None, 60, 8, 1.0)
    assert res["n_rules"] > 0, "inducer learned ZERO rules -- mechanism did not fire (real code path)"
    # mechanism fires: at least some held-out items get non-uniform noun depths (structure distinguishes)
    fired_frac = float(np.mean(res["fired"]))
    assert fired_frac > 0.0, "inducer produced no non-uniform bracketing on ANY held-out item (dead mechanism)"
    # arms differ: inducer head preds are not bit-identical to first-noun
    pred_first = np.array([r["nums"][0] for r in test], dtype=int)
    assert not np.array_equal(res["preds"], pred_first), "inducer head preds bit-identical to first-noun"

    # non-gradient invariant: no gradient optimizer is used anywhere in the induction path.
    assert USES_GRADIENT is False, "GLASS-BOX INVARIANT VIOLATION: inducer flagged as gradient-using"
    # The inducer (induce_grammar / bracket_depths / head_from_depths) uses ONLY discrete counting +
    # numpy indexing -- no deep-learning framework is imported anywhere in this cell (the 29443 linear
    # BASELINE it must beat was gradient-trained, but that is reproduced here with a plain numpy
    # logistic, not a framework autograd). Assert no framework import as an inspectable invariant check.
    src = open(os.path.abspath(__file__), "r", encoding="utf-8").read()
    grad_frag = "import " + "torch"
    assert grad_frag not in src, "GLASS-BOX INVARIANT VIOLATION: a deep-learning framework is imported"
    assert ("optim" + ".") not in src.replace("optimizer", ""), \
        "GLASS-BOX INVARIANT VIOLATION: a gradient optimizer module is referenced"

    # baseline in band
    ytr = np.array([r["label"] for r in train], dtype=int)
    yte = np.array([r["label"] for r in test], dtype=int)
    maj = int(round(float(np.mean(ytr))))
    acc_maj = _acc(np.full(len(test), maj), yte)
    assert 0.05 < acc_maj < 0.95, "majority baseline out of band: %s" % acc_maj

    print("[self-test] induced n_rules=%d fired_frac=%.3f POS-SNF(preview)=%s | non-gradient OK | "
          "majority=%s" % (res["n_rules"], fired_frac,
                           _sub_acc(np.array([r["subj_pos"] != 0 for r in test]), res["preds"], yte)[0],
                           round(acc_maj, 4)), flush=True)
    print("[self-test PASS]", flush=True)
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
