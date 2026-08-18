"""
exp_agreement_glassbox_depth_rule_diagnostic_v1
================================================

SELF-AUDIT DIAGNOSTIC (Director task 2026-07-22): "what have we been doing wrong?"

CLAIM UNDER TEST (pre-registered): the whole number-agreement induction arc failed on
BURIED-subject cases because every learned approach (linear / trained-codes / attractor /
parser) was never given the one feature that separates subject from attractor: SYNTACTIC
EMBEDDING DEPTH (function-word-cued PP / clause nesting). The pre-registered hypothesis:
a cheap DETERMINISTIC glass-box function-word DEPTH rule -- SUBJECT = leftmost/first pre-verb
noun at MINIMUM depth (depth 0 = main clause) -- cracks the buried cases where every LEARNED
approach sat at majority.

DATA: data/corpora/agreement/agreement_word_cache_v1.json.gz (Linzen-Dupoux-Goldberg 2016;
REAL words -> function words VISIBLE; nouns partially anonymized as a<k> but noun_word_idx +
nums + subj_pos + label present). BURIED == SNF == subj_pos != 0 (prior-cell canonical
definition; MAJORITY_REF_SNF ~= 0.628; matches atom 29443 / exp_agreement_attractor_select_vsa_v1).

ARMS (buried-subset agreement accuracy for each; NO verb-number used in any selection -> fair):
  1. DEPTH-RULE (leftmost min-depth)     -- THE PRE-REGISTERED TEST.
  2. IMMEDIATE-FWC (first noun not immediately prep-preceded).
  3. NEAREST-NOUN (last noun's number)   -- positional/attractor baseline.
  4. FIRST-NOUN.
  5. MAJORITY (reported).
  DIAGNOSTIC (post-hoc, clearly labelled): NEAREST-DEPTH-0 (rightmost min-depth; head-final
     tiebreak) -- discovered during probe to matter.
  6. LEARNER-GIVEN-DEPTH: tiny glass-box logistic per-noun selector (alpha depends ONLY on
     structural features; number read from selected noun -> no label leak). WITH vs WITHOUT the
     depth feature -> "does a learner USE depth when handed it?" (missing-feature vs shortcut).

BANDS (pre-registered, on the SPECIFIED arm-1 DEPTH-RULE, buried subset):
  HARD_PASS (diagnosis CONFIRMED) = depth_rule_buried >= majority_buried + 0.15 AND far exceeds
            nearest/first/the learned ~0.63.
  HARD_FAIL (diagnosis WRONG)     = depth_rule_buried <= majority_buried (ties/underperforms).
  MIDDLE                          = partial (in between).
HONEST FRAMING: HARD_PASS is embarrassing-but-clarifying (a trivial rule beats the whole learned
  arc). HARD_FAIL means the depth cue is not the answer and the wall is deeper -- report straight.

# CELL-TEMPLATE MANDATORY:
# - deterministic (hashlib digests + fixed int seeds + sorted(set); NO builtin hash(), NO list(set()))
# - arms_differ verified (deterministic arms produce distinct predictions)
# - except SystemExit: raise BEFORE except Exception (no BaseException, no bare except)
# - crlb_n/a: classification accuracy over deterministic rules; no per-decode Gaussian noise floor
# - baseline_in_band: majority_buried ~0.61 in (0.05, 0.95)
# - no sweep axis -> cardinality trivial; single deterministic pass
# - runtime is glass-box (no gradient at inference; arm-6 build-time logistic only, runtime = argmax select + read number)
# - numbers in this header are MEASURED@data/exp_agreement_glassbox_depth_rule_diagnostic_v1/metrics.json
"""

import argparse
import gzip
import hashlib
import json
import os
import platform
import sys
import time
import traceback
from datetime import datetime, timezone

import numpy as np

ANCHOR_NAME = "exp_agreement_glassbox_depth_rule_diagnostic_v1"
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE_PATH = os.path.join(REPO, "data", "corpora", "agreement", "agreement_word_cache_v1.json.gz")
OUTPUT_DIR = os.path.join(REPO, "data", ANCHOR_NAME)  # ANCHOR already carries the exp_ prefix

# ---- pre-registered bands ----
HP_MARGIN_OVER_MAJ = 0.15   # depth-rule buried must beat majority by this for HARD_PASS
HF_TIE_MAJ = 0.0            # depth-rule buried <= majority + this -> HARD_FAIL (diagnosis wrong)

# ---- novel-lexeme split (identical hash to base cell / atom 29443) ----
TEST_HASH_MOD = 5
TEST_FRAC_CUT = 2


def _is_test(subj_word):
    h = int.from_bytes(hashlib.sha256(str(subj_word).encode("utf-8")).digest()[:8], "big")
    return (h % TEST_HASH_MOD) < TEST_FRAC_CUT


# ---- closed lists (glass-box, inspectable) ----
PREPS = set((
    "to of in on for with at by from into onto about over under between among against during "
    "without within through across after before around near above below beside besides beyond "
    "despite toward towards upon per via regarding concerning off out up down"
).split())
SUBORD = set((
    "that which who whom whose where when while because if although though unless until since "
    "whether as than"
).split())


def depths_at_nouns(item):
    """Incremental embedding-DEPTH per noun. +1 opening on a PREP or SUBORD/RELATIVIZER; close
    heuristic: a comma / close-paren / semicolon pops one level (keeps it simple + inspectable).
    Returns {noun_k: depth}. Deterministic, glass-box, NO number / NO verb used."""
    ni = item["noun_word_idx"]
    words = item["words"]
    depth = 0
    out = {}
    widx_to_k = {wi: k for k, wi in enumerate(ni)}
    for i, w in enumerate(words):
        wl = w.lower()
        if i in widx_to_k:
            out[widx_to_k[i]] = depth
        if wl in PREPS or wl in SUBORD:
            depth += 1
        elif wl in (",", ")", ";") and depth > 0:
            depth -= 1
    # any noun not seen (shouldn't happen) defaults to 0
    for k in range(len(ni)):
        out.setdefault(k, 0)
    return out


# ---- deterministic arms: each returns the noun-INDEX k it selects (number read afterward) ----
def sel_depth_leftmost(item):
    """ARM 1 -- pre-registered DEPTH-RULE: leftmost/first noun at MINIMUM depth."""
    dm = depths_at_nouns(item)
    best_k, best_d = 0, None
    for k in sorted(dm):
        if best_d is None or dm[k] < best_d:
            best_d, best_k = dm[k], k
    return best_k


def sel_depth_nearest(item):
    """DIAGNOSTIC -- NEAREST-DEPTH-0: rightmost (verb-adjacent) noun at MINIMUM depth
    (head-final tiebreak; post-hoc discovery, clearly labelled)."""
    dm = depths_at_nouns(item)
    best_k, best_d = 0, None
    for k in sorted(dm):
        if best_d is None or dm[k] <= best_d:
            best_d, best_k = dm[k], k
    return best_k


def sel_immediate_fwc(item):
    """ARM 2 -- IMMEDIATE-FWC: first noun NOT immediately preceded by a preposition."""
    ni = item["noun_word_idx"]
    words = item["words"]
    for k, wi in enumerate(ni):
        prev = words[wi - 1].lower() if wi > 0 else ""
        if prev not in PREPS:
            return k
    return 0


def sel_nearest_noun(item):
    """ARM 3 -- last noun (attractor/positional baseline)."""
    return len(item["noun_word_idx"]) - 1


def sel_first_noun(item):
    """ARM 4 -- first noun."""
    return 0


DET_ARMS = {
    "depth_rule": sel_depth_leftmost,        # arm 1 (THE test)
    "immediate_fwc": sel_immediate_fwc,      # arm 2
    "nearest_noun": sel_nearest_noun,        # arm 3
    "first_noun": sel_first_noun,            # arm 4
    "nearest_depth0": sel_depth_nearest,     # diagnostic reframe
}


# ==================================================================================================
# ARM 6 -- tiny glass-box logistic per-noun selector; alpha depends ONLY on structural features
# (depth / position / fwc flags) -> NO number leak into selection. Number read from soft-selected
# noun. Build-time gradient only; runtime = argmax select + read number (glass-box).
# ==================================================================================================
def _struct_feats(item, use_depth):
    ni = item["noun_word_idx"]
    words = item["words"]
    dm = depths_at_nouns(item)
    nn = len(ni)
    feats = []
    for k, wi in enumerate(ni):
        prev = words[wi - 1].lower() if wi > 0 else ""
        pos_norm = k / max(nn - 1, 1)
        f = [
            1.0,                                     # bias
            (float(dm[k]) if use_depth else 0.0),    # DEPTH feature (the lever)
            pos_norm,                                # position in noun sequence
            1.0 if prev in PREPS else 0.0,           # immediately prep-preceded
            1.0 if prev in SUBORD else 0.0,          # immediately subord-preceded
            1.0 if k == 0 else 0.0,                  # is-first
            1.0 if k == nn - 1 else 0.0,             # is-last
        ]
        feats.append(f)
    return np.asarray(feats, dtype=np.float64)  # (nn, F)


N_FEAT = 7


def _softmax(x):
    x = x - np.max(x)
    e = np.exp(x)
    return e / np.sum(e)


def train_learner(fit_items, use_depth, seed, steps=400, lr=0.3, l2=1e-3):
    """Per-noun logistic selector. p(plural) = sum_k alpha_k * nums_k, alpha=softmax(w.feat_k).
    Number enters ONLY as the read-out value of the selected noun (no leak into alpha)."""
    rng = np.random.default_rng(seed)
    w = rng.normal(0, 0.01, size=N_FEAT)
    # precompute per-item feats + nums
    data = []
    for it in fit_items:
        F = _struct_feats(it, use_depth)
        nums = np.asarray(it["nums"], dtype=np.float64)
        data.append((F, nums, float(it["label"])))
    for _ in range(steps):
        grad = np.zeros(N_FEAT)
        for F, nums, y in data:
            scores = F @ w
            alpha = _softmax(scores)
            p = float(np.dot(alpha, nums))
            p = min(max(p, 1e-6), 1 - 1e-6)
            dL_dp = (p - y) / (p * (1 - p))            # d BCE / d p
            # d p / d score_j = alpha_j * (nums_j - p)
            dp_dscore = alpha * (nums - p)
            gvec = F.T @ (dL_dp * dp_dscore)            # (F,)
            grad += gvec
        grad = grad / len(data) + l2 * w
        w = w - lr * grad
    return w


def learner_predict(item, w, use_depth):
    F = _struct_feats(item, use_depth)
    scores = F @ w
    k = int(np.argmax(scores))                          # runtime: hard argmax select (glass-box)
    return item["nums"][k], k


# ==================================================================================================
def load_items(max_items=None):
    with gzip.open(CACHE_PATH, "rt", encoding="utf-8") as f:
        d = json.load(f)
    items = d["linzen"]
    if max_items is not None:
        items = items[:max_items]
    return items


def _acc_on(items, selfn):
    """agreement accuracy + selection accuracy of a deterministic arm on `items`."""
    if not items:
        return None, None, 0
    c = 0
    s = 0
    for e in items:
        k = selfn(e)
        if e["nums"][k] == e["label"]:
            c += 1
        if k == e["subj_pos"]:
            s += 1
    n = len(items)
    return round(c / n, 4), round(s / n, 4), n


def _majority_acc(items):
    if not items:
        return None
    labs = [e["label"] for e in items]
    maj = int(round(float(np.mean(labs))))
    return round(float(np.mean([maj == e["label"] for e in items])), 4)


def _has_conflict(e):
    nums = e["nums"]
    sp = e["subj_pos"]
    return any(nums[k] != nums[sp] for k in range(len(nums)) if k != sp)


def eval_all(items, learner_with=None, learner_without=None):
    buried = [e for e in items if e["subj_pos"] != 0]
    easy = [e for e in items if e["subj_pos"] == 0]
    conflict = [e for e in buried if _has_conflict(e)]
    subsets = {"all": items, "buried": buried, "buried_conflict": conflict, "easy": easy}
    out = {}
    for sname, s in subsets.items():
        rec = {"n": len(s), "majority": _majority_acc(s)}
        for arm, fn in DET_ARMS.items():
            acc, sel, _ = _acc_on(s, fn)
            rec[arm] = {"acc": acc, "select_acc": sel}
        if learner_with is not None:
            wc, ws = 0, 0
            noc, nos = 0, 0
            for e in s:
                num_w, kw = learner_predict(e, learner_with, True)
                num_o, ko = learner_predict(e, learner_without, False)
                if num_w == e["label"]:
                    wc += 1
                if kw == e["subj_pos"]:
                    ws += 1
                if num_o == e["label"]:
                    noc += 1
                if ko == e["subj_pos"]:
                    nos += 1
            nn = max(len(s), 1)
            rec["learner_with_depth"] = {"acc": round(wc / nn, 4), "select_acc": round(ws / nn, 4)}
            rec["learner_no_depth"] = {"acc": round(noc / nn, 4), "select_acc": round(nos / nn, 4)}
        out[sname] = rec
    return out


def _write_start_marker(run_mode, expected_n_units):
    marker = {
        "pid": os.getpid(),
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR_NAME,
        "run_mode": run_mode,
        "expected_n_units": expected_n_units,
        "host": platform.node(),
    }
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    tmp = os.path.join(OUTPUT_DIR, "_start_marker.json.tmp")
    final = os.path.join(OUTPUT_DIR, "_start_marker.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, final)


def _write_metrics(metrics):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    tmp = os.path.join(OUTPUT_DIR, "metrics.json.tmp")
    final = os.path.join(OUTPUT_DIR, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, final)


def _write_crash_metrics(exc):
    diag = {
        "verdict": "CELL_CRASHED",
        "verdict_msg": "%s: %s" % (type(exc).__name__, str(exc)[:500]),
        "summary": "CELL_CRASHED: %s" % type(exc).__name__,
        "elapsed_s": 0.0,
        "traceback": traceback.format_exc()[:5000],
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(),
        "anchor_name": ANCHOR_NAME,
    }
    _write_metrics(diag)


def _fmt(subs):
    b = subs["buried"]
    return ("depth_rule=%s immediate_fwc=%s nearest_noun=%s first_noun=%s majority=%s "
            "[nearest_depth0(reframe)=%s]" % (
                b["depth_rule"]["acc"], b["immediate_fwc"]["acc"], b["nearest_noun"]["acc"],
                b["first_noun"]["acc"], b["majority"], b["nearest_depth0"]["acc"]))


def run(run_mode):
    t0 = time.perf_counter()
    _write_start_marker(run_mode, 1)
    items = load_items(max_items=(2000 if run_mode == "smoke" else None))

    # held-out split (novel subject lexeme) for direct comparability to the learned arms;
    # the deterministic rule is lexeme-free so this is a formality, reported for parity.
    test_items = [e for e in items if _is_test(e["subj_word"])]
    fit_items = [e for e in items if not _is_test(e["subj_word"])]

    # arm 6: train the tiny learner on the FIT split (with and without the depth feature)
    seed = 7
    w_with = train_learner(fit_items, use_depth=True, seed=seed,
                           steps=(120 if run_mode == "smoke" else 400))
    w_without = train_learner(fit_items, use_depth=False, seed=seed,
                              steps=(120 if run_mode == "smoke" else 400))

    subs_full = eval_all(items, w_with, w_without)          # full corpus (deterministic rules)
    subs_test = eval_all(test_items, w_with, w_without)     # held-out test split (comparability)

    # arms-differ (META_RULE_AF): the deterministic arms must produce distinct prediction vectors
    buried = [e for e in items if e["subj_pos"] != 0]
    arm_preds = {}
    for arm, fn in DET_ARMS.items():
        arm_preds[arm] = np.asarray([e["nums"][fn(e)] for e in buried], dtype=np.int64)
    digs = {a: hashlib.sha256(arm_preds[a].tobytes()).hexdigest() for a in arm_preds}
    arms_differ = len(set(digs.values())) >= 2

    # ---- verdict (on the pre-registered arm-1 DEPTH-RULE, buried, full corpus) ----
    b = subs_full["buried"]
    depth_acc = b["depth_rule"]["acc"]
    maj_acc = b["majority"]
    near_acc = b["nearest_noun"]["acc"]
    first_acc = b["first_noun"]["acc"]
    reframe_acc = b["nearest_depth0"]["acc"]
    margin = round(depth_acc - maj_acc, 4)

    if depth_acc >= maj_acc + HP_MARGIN_OVER_MAJ and depth_acc > near_acc and depth_acc > first_acc:
        verdict = "HARD_PASS_DIAGNOSIS_CONFIRMED"
    elif depth_acc <= maj_acc + HF_TIE_MAJ:
        verdict = "HARD_FAIL_DIAGNOSIS_REFUTED"
    else:
        verdict = "MIDDLE_BAND"

    lw = b["learner_with_depth"]["acc"]
    lo = b["learner_no_depth"]["acc"]
    learner_uses_depth = round(lw - lo, 4)

    msg = ("SELF-AUDIT depth-rule diagnostic | BURIED(subj_pos!=0, n=%d): %s | "
           "depth_rule margin_over_majority=%+.4f (%s) | REFRAME nearest_depth0=%.4f "
           "(margin_over_maj=%+.4f) select_acc: depth_leftmost=%.4f nearest_depth0=%.4f | "
           "learner_with_depth=%.4f no_depth=%.4f (uses_depth=%+.4f) | "
           "buried_conflict majority=%.4f depth_rule=%.4f | easy depth_rule=%.4f" % (
               b["n"], _fmt(subs_full), margin, verdict, reframe_acc,
               round(reframe_acc - maj_acc, 4), b["depth_rule"]["select_acc"],
               b["nearest_depth0"]["select_acc"], lw, lo, learner_uses_depth,
               subs_full["buried_conflict"]["majority"],
               subs_full["buried_conflict"]["depth_rule"]["acc"],
               subs_full["easy"]["depth_rule"]["acc"]))

    metrics = {
        "verdict": verdict,
        "verdict_tag": verdict,
        "verdict_msg": msg,
        "summary": "%s | depth_rule_buried=%.4f vs majority=%.4f (margin=%+.4f) | reframe nearest_depth0=%.4f" % (
            verdict, depth_acc, maj_acc, margin, reframe_acc),
        "elapsed_s": round(time.perf_counter() - t0, 2),
        "run_mode": run_mode,
        "anchor_name": ANCHOR_NAME,
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "full_corpus": subs_full,
        "heldout_test_split": subs_test,
        "arms_differ_verified": arms_differ,
        "arms_differ_digests": digs,
        "bands": {"HP_MARGIN_OVER_MAJ": HP_MARGIN_OVER_MAJ, "HF_TIE_MAJ": HF_TIE_MAJ,
                  "note": "bands apply to arm-1 depth_rule on buried subset"},
        "n_preps": len(PREPS), "n_subord": len(SUBORD),
        "learner_uses_depth_buried": learner_uses_depth,
        "crlb_n_a": "classification accuracy over deterministic rules; no per-decode Gaussian noise floor",
    }
    _write_metrics(metrics)
    print("[%s] %s" % (ANCHOR_NAME, msg), flush=True)
    print("[%s] elapsed=%.2fs run_mode=%s" % (ANCHOR_NAME, metrics["elapsed_s"], run_mode), flush=True)
    return metrics


def self_test():
    print("[%s] SELF-TEST" % ANCHOR_NAME, flush=True)
    # F.5: no nondeterministic seeding in this source
    try:
        from experiments._validity_preflight import assert_no_nondeterministic_seeding
        with open(os.path.abspath(__file__), "r", encoding="utf-8") as f:
            assert_no_nondeterministic_seeding(f.read())
        print("[%s] F.5 source scan clean" % ANCHOR_NAME, flush=True)
    except ImportError:
        print("[%s] F.5 preflight module absent; relying on hashlib-only discipline" % ANCHOR_NAME, flush=True)

    # ---- hand traces of the depth tracker (glass-box verification) ----
    # Trace A: fronted PP attractor, subject at depth 0 after the PP closes.
    #   "in[+1] the box[N0,d1] , [close] the keys[N1,d0] ..."   -> leftmost min-depth = N1 (keys)
    hA = {"words": ["in", "box", ",", "keys"], "noun_word_idx": [1, 3],
          "nums": [0, 1], "subj_pos": 1, "label": 1}
    dmA = depths_at_nouns(hA)
    assert dmA[0] == 1 and dmA[1] == 0, "traceA depths wrong: %s" % dmA
    assert sel_depth_leftmost(hA) == 1, "traceA leftmost-mindepth should pick keys(N1)"
    assert sel_nearest_noun(hA) == 1 and sel_first_noun(hA) == 0

    # Trace B: classic post-subject PP attractor "keys[N0,d0] to[+1] cabinet[N1,d1]"
    #   subject is FIRST here (subj_pos 0) -> depth rule picks keys (correct), nearest picks cabinet.
    hB = {"words": ["keys", "to", "cabinet"], "noun_word_idx": [0, 2],
          "nums": [1, 0], "subj_pos": 0, "label": 1}
    dmB = depths_at_nouns(hB)
    assert dmB[0] == 0 and dmB[1] == 1, "traceB depths wrong: %s" % dmB
    assert sel_depth_leftmost(hB) == 0 and sel_nearest_noun(hB) == 1

    # Trace C: head-final compound "a0[N0,d0] space[N1,d0,SUBJ]" -- BOTH depth 0; leftmost picks
    #   N0 (WRONG), nearest_depth0 picks N1 (the compound head = subject). Documents the failure mode.
    hC = {"words": ["a0", "space"], "noun_word_idx": [0, 1],
          "nums": [0, 0], "subj_pos": 1, "label": 0}
    assert sel_depth_leftmost(hC) == 0, "traceC leftmost picks N0 (documents miss)"
    assert sel_depth_nearest(hC) == 1, "traceC nearest_depth0 picks head N1"

    # immediate-fwc
    assert sel_immediate_fwc(hA) == 1, "immediate_fwc: box is prep-preceded, keys is not"

    # ---- learner trains + arms differ on a small sample ----
    items = load_items(max_items=1500)
    fit = [e for e in items if not _is_test(e["subj_word"])]
    w1 = train_learner(fit, use_depth=True, seed=7, steps=40)
    w0 = train_learner(fit, use_depth=False, seed=7, steps=40)
    assert w1.shape == (N_FEAT,) and np.all(np.isfinite(w1)), "learner_with produced non-finite w"
    assert np.all(np.isfinite(w0)), "learner_without non-finite"
    num_w, kw = learner_predict(items[0], w1, True)
    assert num_w in (0, 1)

    buried = [e for e in items if e["subj_pos"] != 0]
    preds = {a: np.asarray([e["nums"][fn(e)] for e in buried]) for a, fn in DET_ARMS.items()}
    digs = {a: hashlib.sha256(preds[a].tobytes()).hexdigest() for a in preds}
    assert len(set(digs.values())) >= 2, "arms bit-identical: %s" % digs

    # baseline in band
    maj = _majority_acc(buried)
    assert maj is not None and 0.05 < maj < 0.95, "majority out of band (AG): %s" % maj
    print("[%s] SELF-TEST PASS (hand-traces + learner + arms-differ + majority_buried=%.4f in band)" %
          (ANCHOR_NAME, maj), flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--run", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        self_test()
        return
    if args.smoke:
        run("smoke")
        return
    run("full")


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # NOT BaseException
        _write_crash_metrics(e)
        raise
