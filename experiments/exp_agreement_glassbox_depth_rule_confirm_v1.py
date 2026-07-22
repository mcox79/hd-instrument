"""
exp_agreement_glassbox_depth_rule_confirm_v1
============================================

CLEAN PRE-REGISTERED CONFIRMATION (Director task 2026-07-22) of the strong glass-box lead that
emerged POST-HOC from exp_agreement_glassbox_depth_rule_diagnostic_v1: the "NEAREST-to-verb
DEPTH-0 noun" rule scored 0.759 on buried subjects (n=6425), beating majority ~0.628 and the
ENTIRE learned agreement arc (~0.63) by +0.13-0.15. That was NOT the pre-registered rule in the
diagnostic (the pre-reg "first/leftmost depth-0 noun" FAILED at 0.528); the nearest-depth-0
reframe was a labelled DIAGNOSTIC. This cell PRE-REGISTERS it and confirms it with an ANTI-CHEAT
depth-scramble discriminator before it can be claimed as the first glass-box result to beat the
buried-subject agreement wall.

DATA: data/corpora/agreement/agreement_word_cache_v1.json.gz (Linzen-Dupoux-Goldberg 2016; REAL
function words visible; non-subject nouns partially anonymized a<k>; subj_word + nums + subj_pos +
label present). BURIED == SNF == subj_pos != 0 (prior-cell canonical definition; majority_ref_SNF
~= 0.628; atom 29443 / exp_agreement_attractor_select_vsa_v1). Same held-out split family.

THE REGISTERED RULE (glass-box, deterministic, incremental, NO verb-number in selection = fair):
  Incrementally track embedding DEPTH from function words (preposition / relativizer opens +1;
  comma/close pops one level). SUBJECT = the depth-0 (min-depth) noun NEAREST to the verb
  (rightmost among min-depth nouns). Read ITS number -> predict verb number.

ARMS (report BURIED agreement accuracy):
  1. nearest_depth0   -- THE REGISTERED RULE (rightmost noun at MINIMUM function-word depth).
  2. nearest_noun     -- rightmost noun raw (~0.551; the attractor baseline). The depth FILTER's
                         lift over THIS is the load-bearing delta (~+0.21).
  3. first_noun.
  4. majority (reported).
  SECOND ARM (offline, our own models, NO external download): POS-tag depth (nltk perceptron
     tagger; noun positions force-tagged NN; openers = IN/TO/WDT/WP/WP$) -> nearest-at-min-POS-depth.
     "Does better structure push buried agreement ABOVE 0.759?" Graceful-skip if tagger unavailable.

ANTI-CHEAT DISCRIMINATOR (the fairness lynchpin -- proves it is DEPTH-structure not position):
  SCRAMBLE the per-noun depth assignments (permute WHICH nouns hold which depth value while
  PRESERVING the depth multiset AND the noun POSITIONS). Re-run nearest-at-min-depth on the
  scrambled depths (multi-seed). The rule's selection MUST change and BURIED accuracy MUST DROP
  substantially. If scrambling depth does NOT drop accuracy, the rule was secretly keying on
  position (verb-adjacency) not depth -> nearest_noun with extra steps -> HARD_FAIL.

BANDS (pre-registered; on nearest_depth0, BURIED subset, held-out multi-seed mean):
  HARD_PASS (ALL of):
     (a) nearest_depth0 held-out buried >= majority + 0.10, AND
     (b) nearest_depth0 - nearest_noun_raw >= 0.05 (clear lift over the attractor baseline), AND
     (c) depth-scramble discriminator FIRES: mean(true_acc - scrambled_acc) on buried >= 0.10.
  HARD_FAIL (ANY of):
     (i) nearest_depth0 held-out buried <= majority (ties/underperforms), OR
     (ii) scramble drop < 0.05 (accuracy does NOT drop when depth is scrambled = position all along).
  MIDDLE = partial (in between).
HONEST FRAMING: if HARD_PASS this is the FIRST glass-box result to beat the buried-subject wall
  (the whole arc's target) -> flag for HARDEST skunkworks-VET (watch: is it really depth or
  disguised position; is the buried subset representative). Deterministic rule = low variance;
  the multi-seed held-out split confirms that.

# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - deterministic (hashlib digests + fixed int seeds + sorted(set)/np default_rng; NO builtin hash(), NO list(set()))
# - arms_differ verified (deterministic arms produce distinct buried prediction vectors; META_RULE_AF)
# - final_metrics_atomicity: tmp_replace (single-shot; metrics.json.tmp -> os.replace)
# - except SystemExit: raise BEFORE except Exception (no BaseException, no bare except)
# - crlb_n/a: classification accuracy over deterministic rules; no per-decode Gaussian noise floor
# - baseline_in_band: majority_buried ~0.61-0.63 in (0.05, 0.95) (META_RULE_AG); asserted at self-test
# - no sweep axis -> cardinality trivial; multi-seed loops over 5 split-seeds + 5 scramble-seeds (declared)
# - discriminator survives scale: full-N is the only regime (whole corpus); smoke = 2000-item subset preview
# - runtime is glass-box: NO gradient anywhere; runtime = incremental depth track + argmax select + read number
# - all header numbers MEASURED@ the diagnostic metrics (0.759/0.551/0.528) or MEASURED@ this cell's output
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

ANCHOR_NAME = "exp_agreement_glassbox_depth_rule_confirm_v1"
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE_PATH = os.path.join(REPO, "data", "corpora", "agreement", "agreement_word_cache_v1.json.gz")
OUTPUT_DIR = os.path.join(REPO, "data", ANCHOR_NAME)

# ---- pre-registered bands ----
HP_MARGIN_OVER_MAJ = 0.10     # (a) nearest_depth0 held-out buried must beat majority by this
HP_LIFT_OVER_NEAREST = 0.05   # (b) nearest_depth0 - nearest_noun_raw must be at least this
HP_SCRAMBLE_DROP = 0.10       # (c) mean(true - scrambled) buried must be at least this
HF_SCRAMBLE_NOEFFECT = 0.05   # scramble drop below this = position all along = HARD_FAIL

# ---- multi-seed ----
SPLIT_SEEDS = [7, 13, 19, 23, 31]      # held-out split variance (deterministic rule => should be tiny)
SCRAMBLE_SEEDS = [101, 103, 107, 109, 113]  # depth-scramble discriminator seeds
TEST_HASH_MOD = 5
TEST_FRAC_CUT = 2   # ~40% held out

# ---- closed lists (glass-box, inspectable) -- identical to the diagnostic cell ----
PREPS = set((
    "to of in on for with at by from into onto about over under between among against during "
    "without within through across after before around near above below beside besides beyond "
    "despite toward towards upon per via regarding concerning off out up down"
).split())
SUBORD = set((
    "that which who whom whose where when while because if although though unless until since "
    "whether as than"
).split())


def _is_test(subj_word, seed):
    """Held-out membership for a given split seed (salted; deterministic; lexeme-based)."""
    key = "%s:%d" % (str(subj_word), seed)
    h = int.from_bytes(hashlib.sha256(key.encode("utf-8")).digest()[:8], "big")
    return (h % TEST_HASH_MOD) < TEST_FRAC_CUT


def depths_at_nouns(item):
    """Incremental embedding-DEPTH per noun (function-word cued). +1 on PREP/SUBORD; comma/close
    pops one level. Returns list depths[k] for k in 0..n_nouns-1. Deterministic, glass-box; NO
    number and NO verb-number used. (Identical logic to the diagnostic cell.)"""
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
    return [out.get(k, 0) for k in range(len(ni))]


def nearest_at_mindepth(depth_list):
    """Rightmost (verb-adjacent) noun index at MINIMUM depth. THE registered selection, given a
    per-noun depth list. Deterministic; NO number used."""
    best_k, best_d = 0, None
    for k in range(len(depth_list)):
        d = depth_list[k]
        if best_d is None or d <= best_d:   # <= => rightmost wins ties (verb-adjacent)
            best_d, best_k = d, k
    return best_k


# ---- deterministic arms: each returns the selected noun INDEX k (number read afterward) ----
def sel_nearest_depth0(item):
    """ARM 1 -- THE REGISTERED RULE: rightmost noun at minimum function-word depth."""
    return nearest_at_mindepth(depths_at_nouns(item))


def sel_nearest_noun(item):
    """ARM 2 -- rightmost noun (attractor / positional baseline)."""
    return len(item["noun_word_idx"]) - 1


def sel_first_noun(item):
    """ARM 3 -- first noun."""
    return 0


DET_ARMS = {
    "nearest_depth0": sel_nearest_depth0,   # arm 1 (THE registered rule)
    "nearest_noun": sel_nearest_noun,       # arm 2 (attractor baseline)
    "first_noun": sel_first_noun,           # arm 3
}


# ==================================================================================================
# SECOND ARM -- POS-tag depth (our own offline nltk perceptron tagger; NO external download).
# Openers = IN/TO/WDT/WP/WP$ (prepositions + infinitival-to + relativizers), detected from POS
# tags so it generalizes beyond the hand-curated PREPS/SUBORD list; noun positions FORCE-tagged NN
# (we know which tokens are nouns) to remove the main tagger-noise source on anonymized a<k> tokens.
# Same comma/close pop. Runtime is still glass-box (tag -> incremental depth -> argmax select).
# ==================================================================================================
_POS_OPENERS = {"IN", "TO", "WDT", "WP", "WP$"}


def _pos_depth_list(item, tagger):
    """Per-noun depth from POS-tag-identified openers. tagger(words)->list[(w,tag)]."""
    ni = item["noun_word_idx"]
    words = item["words"]
    tags = tagger(words)
    noun_pos = set(ni)
    depth = 0
    out = {}
    widx_to_k = {wi: k for k, wi in enumerate(ni)}
    for i, (w, tag) in enumerate(tags):
        if i in noun_pos:
            tag = "NN"                       # force known nouns -> NN (anonymized-token noise fix)
        if i in widx_to_k:
            out[widx_to_k[i]] = depth
        wl = w.lower()
        if tag in _POS_OPENERS:
            depth += 1
        elif wl in (",", ")", ";") and depth > 0:
            depth -= 1
    return [out.get(k, 0) for k in range(len(ni))]


def _get_nltk_tagger():
    """Return a words->[(w,tag)] tagger using the offline perceptron tagger, or None if unavailable.
    NO external download attempted (offline discipline)."""
    try:
        import nltk
        # probe that the tagger data is present offline (do NOT trigger a download)
        try:
            nltk.data.find("taggers/averaged_perceptron_tagger")
        except LookupError:
            try:
                nltk.data.find("taggers/averaged_perceptron_tagger_eng")
            except LookupError:
                return None, "nltk_tagger_data_absent_offline"
        _ = nltk.pos_tag(["test", "sentence"])   # smoke the call path once
        return (lambda ws: nltk.pos_tag(ws)), None
    except Exception as ex:                       # tagger unavailable -> record + skip, never crash
        return None, "%s: %s" % (type(ex).__name__, str(ex)[:120])


# ==================================================================================================
def load_items(max_items=None, representative=False):
    """Load Linzen items. `representative=True` takes a deterministic STRIDE sample across the whole
    corpus instead of the head slice -- the corpus head is ordered/skewed (head buried majority
    ~0.81, last-is-subj ~0.74 vs full ~0.61, ~0.34), so a head slice would show the WRONG pattern
    at smoke. The stride sample reproduces the full-corpus buried distribution."""
    with gzip.open(CACHE_PATH, "rt", encoding="utf-8") as f:
        d = json.load(f)
    items = d["linzen"]
    if max_items is not None and max_items < len(items):
        if representative:
            stride = max(len(items) // max_items, 1)
            items = items[::stride][:max_items]
        else:
            items = items[:max_items]
    return items


def _acc_and_sel(items, selfn):
    """agreement accuracy + subject-selection accuracy of a deterministic arm on `items`."""
    if not items:
        return None, None
    c = 0
    s = 0
    for e in items:
        k = selfn(e)
        if e["nums"][k] == e["label"]:
            c += 1
        if k == e["subj_pos"]:
            s += 1
    n = len(items)
    return round(c / n, 4), round(s / n, 4)


def _majority_acc(items):
    if not items:
        return None
    labs = [e["label"] for e in items]
    maj = int(round(float(np.mean(labs))))
    return round(float(np.mean([maj == e["label"] for e in items])), 4)


def _scramble_drop(buried, seeds):
    """ANTI-CHEAT: for each seed, permute per-noun depth values (preserve multiset + positions),
    re-run nearest-at-min-depth, measure BURIED agreement accuracy + how often the selection
    changed. Returns (true_acc, [per-seed scrambled acc], [per-seed change_frac])."""
    # true accuracy of the registered rule on buried
    true_c = sum(1 for e in buried if e["nums"][nearest_at_mindepth(depths_at_nouns(e))] == e["label"])
    true_acc = round(true_c / len(buried), 4)
    # cache true depth lists + true selections once
    true_depths = [depths_at_nouns(e) for e in buried]
    true_sel = [nearest_at_mindepth(dl) for dl in true_depths]
    scr_accs, change_fracs = [], []
    for seed in seeds:
        rng = np.random.default_rng(seed)
        c = 0
        changed = 0
        for e, dl, tsel in zip(buried, true_depths, true_sel):
            n = len(dl)
            perm = rng.permutation(n)
            scr = [dl[perm[k]] for k in range(n)]   # preserve multiset, shuffle position<->depth
            k = nearest_at_mindepth(scr)
            if e["nums"][k] == e["label"]:
                c += 1
            if k != tsel:
                changed += 1
        scr_accs.append(round(c / len(buried), 4))
        change_fracs.append(round(changed / len(buried), 4))
    return true_acc, scr_accs, change_fracs


def eval_split(items, split_seed):
    """held-out buried metrics for the deterministic arms + majority, at a given split seed."""
    test_items = [e for e in items if _is_test(e["subj_word"], split_seed)]
    buried = [e for e in test_items if e["subj_pos"] != 0]
    rec = {"n_test": len(test_items), "n_buried": len(buried), "majority_buried": _majority_acc(buried)}
    for arm, fn in DET_ARMS.items():
        acc, sel = _acc_and_sel(buried, fn)
        rec[arm] = {"acc": acc, "select_acc": sel}
    return rec


def eval_subset(items, tagger=None, tag_diag=None):
    """full-corpus buried + easy metrics for all arms (deterministic rule => full corpus is the
    cleanest estimate; held-out is parity/variance)."""
    buried = [e for e in items if e["subj_pos"] != 0]
    easy = [e for e in items if e["subj_pos"] == 0]
    out = {"n_buried": len(buried), "n_easy": len(easy),
           "majority_buried": _majority_acc(buried), "majority_easy": _majority_acc(easy)}
    for arm, fn in DET_ARMS.items():
        ab, sb = _acc_and_sel(buried, fn)
        ae, se = _acc_and_sel(easy, fn)
        out[arm] = {"buried_acc": ab, "buried_select_acc": sb, "easy_acc": ae, "easy_select_acc": se}
    # POS-depth second arm (graceful)
    if tagger is not None:
        def _pos_sel(e):
            return nearest_at_mindepth(_pos_depth_list(e, tagger))
        ab, sb = _acc_and_sel(buried, _pos_sel)
        ae, se = _acc_and_sel(easy, _pos_sel)
        out["pos_depth"] = {"buried_acc": ab, "buried_select_acc": sb,
                            "easy_acc": ae, "easy_select_acc": se, "status": "run"}
    else:
        out["pos_depth"] = {"status": "skipped", "reason": tag_diag}
    return out


def _write_start_marker(run_mode, expected_n_units):
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": run_mode,
              "expected_n_units": expected_n_units, "host": platform.node()}
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
    diag = {"verdict": "CELL_CRASHED",
            "verdict_msg": "%s: %s" % (type(exc).__name__, str(exc)[:500]),
            "summary": "CELL_CRASHED: %s" % type(exc).__name__,
            "elapsed_s": 0.0, "traceback": traceback.format_exc()[:5000],
            "ts_iso": datetime.now(timezone.utc).isoformat(),
            "pid": os.getpid(), "anchor_name": ANCHOR_NAME}
    _write_metrics(diag)


def run(run_mode):
    t0 = time.perf_counter()
    _write_start_marker(run_mode, len(SPLIT_SEEDS) + len(SCRAMBLE_SEEDS))
    items = load_items(max_items=(2000 if run_mode == "smoke" else None),
                       representative=(run_mode == "smoke"))
    buried_full = [e for e in items if e["subj_pos"] != 0]

    # ---- second arm: our own offline POS tagger (never crashes the run) ----
    tagger, tag_diag = _get_nltk_tagger()

    # ---- full-corpus arms (deterministic rule => cleanest estimate) ----
    full = eval_subset(items, tagger=tagger, tag_diag=tag_diag)

    # ---- multi-seed held-out split (variance of the deterministic rule) ----
    splits = {}
    nd0_heldout, near_heldout, maj_heldout = [], [], []
    for s in SPLIT_SEEDS:
        rec = eval_split(items, s)
        splits["seed_%d" % s] = rec
        if rec["n_buried"] > 0:
            nd0_heldout.append(rec["nearest_depth0"]["acc"])
            near_heldout.append(rec["nearest_noun"]["acc"])
            maj_heldout.append(rec["majority_buried"])
    nd0_ho_mean = round(float(np.mean(nd0_heldout)), 4)
    nd0_ho_std = round(float(np.std(nd0_heldout)), 4)
    near_ho_mean = round(float(np.mean(near_heldout)), 4)
    maj_ho_mean = round(float(np.mean(maj_heldout)), 4)

    # ---- ANTI-CHEAT depth-scramble discriminator (multi-seed) ----
    scr_seeds = SCRAMBLE_SEEDS if run_mode != "smoke" else SCRAMBLE_SEEDS[:3]
    true_acc, scr_accs, change_fracs = _scramble_drop(buried_full, scr_seeds)
    scr_mean = round(float(np.mean(scr_accs)), 4)
    scramble_drop = round(true_acc - scr_mean, 4)
    change_frac_mean = round(float(np.mean(change_fracs)), 4)

    # ---- arms-differ (META_RULE_AF) ----
    arm_preds = {a: np.asarray([e["nums"][fn(e)] for e in buried_full], dtype=np.int64)
                 for a, fn in DET_ARMS.items()}
    digs = {a: hashlib.sha256(arm_preds[a].tobytes()).hexdigest() for a in arm_preds}
    arms_differ = len(set(digs.values())) >= 2

    # ---- verdict (pre-registered) ----
    cond_a = nd0_ho_mean >= maj_ho_mean + HP_MARGIN_OVER_MAJ
    cond_b = (nd0_ho_mean - near_ho_mean) >= HP_LIFT_OVER_NEAREST
    cond_c = scramble_drop >= HP_SCRAMBLE_DROP
    hf_i = nd0_ho_mean <= maj_ho_mean
    hf_ii = scramble_drop < HF_SCRAMBLE_NOEFFECT
    if cond_a and cond_b and cond_c:
        verdict = "HARD_PASS_DEPTH_RULE_CONFIRMED"
    elif hf_i or hf_ii:
        verdict = "HARD_FAIL_DEPTH_RULE_REFUTED"
    else:
        verdict = "MIDDLE_BAND"

    pos = full["pos_depth"]
    pos_str = ("pos_depth_buried=%s" % pos.get("buried_acc")) if pos.get("status") == "run" \
        else ("pos_depth=SKIPPED(%s)" % pos.get("reason"))

    msg = ("DEPTH-RULE CONFIRM | BURIED held-out(mean of %d splits): nearest_depth0=%.4f(+-%.4f) "
           "nearest_noun_raw=%.4f majority=%.4f | full-corpus buried: nearest_depth0=%s "
           "nearest_noun=%s first_noun=%s majority=%s | SCRAMBLE-DISCRIMINATOR true=%.4f "
           "scrambled=%.4f DROP=%+.4f (change_frac=%.3f) | %s | easy nearest_depth0=%s | %s" % (
               len(nd0_heldout), nd0_ho_mean, nd0_ho_std, near_ho_mean, maj_ho_mean,
               full["nearest_depth0"]["buried_acc"], full["nearest_noun"]["buried_acc"],
               full["first_noun"]["buried_acc"], full["majority_buried"],
               true_acc, scr_mean, scramble_drop, change_frac_mean, pos_str,
               full["nearest_depth0"]["easy_acc"], verdict))

    metrics = {
        "verdict": verdict,
        "verdict_tag": verdict,
        "verdict_msg": msg,
        "summary": ("%s | nd0_heldout_buried=%.4f vs majority=%.4f (margin=%+.4f) | scramble_drop=%+.4f | "
                    "nd0_full_buried=%s vs nearest_noun=%s" % (
                        verdict, nd0_ho_mean, maj_ho_mean, round(nd0_ho_mean - maj_ho_mean, 4),
                        scramble_drop, full["nearest_depth0"]["buried_acc"],
                        full["nearest_noun"]["buried_acc"])),
        "elapsed_s": round(time.perf_counter() - t0, 2),
        "run_mode": run_mode,
        "anchor_name": ANCHOR_NAME,
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "heldout_multiseed": {
            "n_splits": len(nd0_heldout),
            "nearest_depth0_buried_mean": nd0_ho_mean, "nearest_depth0_buried_std": nd0_ho_std,
            "nearest_noun_buried_mean": near_ho_mean, "majority_buried_mean": maj_ho_mean,
            "per_split": splits},
        "full_corpus": full,
        "scramble_discriminator": {
            "true_acc": true_acc, "scrambled_acc_mean": scr_mean, "scramble_drop": scramble_drop,
            "per_seed_scrambled_acc": scr_accs, "per_seed_change_frac": change_fracs,
            "change_frac_mean": change_frac_mean, "seeds": scr_seeds,
            "interpretation": "drop toward nearest_noun_raw => lift is DEPTH not position"},
        "verdict_conditions": {"cond_a_margin_over_maj": cond_a, "cond_b_lift_over_nearest": cond_b,
                               "cond_c_scramble_fires": cond_c, "hf_i_ties_majority": hf_i,
                               "hf_ii_scramble_no_effect": hf_ii},
        "arms_differ_verified": arms_differ, "arms_differ_digests": digs,
        "bands": {"HP_MARGIN_OVER_MAJ": HP_MARGIN_OVER_MAJ, "HP_LIFT_OVER_NEAREST": HP_LIFT_OVER_NEAREST,
                  "HP_SCRAMBLE_DROP": HP_SCRAMBLE_DROP, "HF_SCRAMBLE_NOEFFECT": HF_SCRAMBLE_NOEFFECT},
        "n_preps": len(PREPS), "n_subord": len(SUBORD),
        "final_metrics_atomicity": "tmp_replace",
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

    # ---- hand traces of the DEPTH tracker + the REGISTERED nearest-at-min-depth selection ----
    # Trace A: fronted PP attractor, subject at depth 0 AFTER the PP closes.
    #   "in[+1] box[N0,d1] , [close] keys[N1,d0,SUBJ]"  -> min-depth={N1}; nearest_depth0 picks keys.
    hA = {"words": ["in", "box", ",", "keys"], "noun_word_idx": [1, 3],
          "nums": [0, 1], "subj_pos": 1, "label": 1}
    dlA = depths_at_nouns(hA)
    assert dlA == [1, 0], "traceA depths wrong: %s" % dlA
    assert nearest_at_mindepth(dlA) == 1, "traceA nearest_depth0 should pick keys(N1)"
    assert sel_nearest_noun(hA) == 1 and sel_first_noun(hA) == 0

    # Trace B: post-subject PP attractor "keys[N0,d0,SUBJ] to[+1] cabinet[N1,d1]" (subj is first).
    #   nearest_depth0 picks keys (min-depth, correct); nearest_noun picks cabinet (attractor, WRONG).
    hB = {"words": ["keys", "to", "cabinet"], "noun_word_idx": [0, 2],
          "nums": [1, 0], "subj_pos": 0, "label": 1}
    dlB = depths_at_nouns(hB)
    assert dlB == [0, 1], "traceB depths wrong: %s" % dlB
    assert nearest_at_mindepth(dlB) == 0, "traceB nearest_depth0 picks subject keys(N0)"
    assert sel_nearest_noun(hB) == 1, "traceB nearest_noun picks attractor cabinet(N1)"

    # Trace C: buried subject AFTER an embedded clause, verb-adjacent at depth 0.
    #   "a0[N0,d0] that[+1] a1[N1,d1] , [close] cars[N2,d0,SUBJ]" -> min-depth={N0,N2}; nearest picks N2.
    hC = {"words": ["a0", "that", "a1", ",", "cars"], "noun_word_idx": [0, 2, 4],
          "nums": [0, 0, 1], "subj_pos": 2, "label": 1}
    dlC = depths_at_nouns(hC)
    assert dlC == [0, 1, 0], "traceC depths wrong: %s" % dlC
    assert nearest_at_mindepth(dlC) == 2, "traceC nearest_depth0 picks verb-adjacent cars(N2)"
    assert sel_first_noun(hC) == 0, "traceC first_noun would pick N0 (wrong on head-final subject)"

    # ---- SCRAMBLE discriminator hand-trace: depth [0,1,0] scrambled must be able to move selection.
    # multiset {0,0,1}; if the '1' lands rightmost, min-depth={N0,N1} and nearest picks N1 not N2.
    dl = [0, 1, 0]
    moved = False
    for seed in range(20):
        rng = np.random.default_rng(seed)
        perm = rng.permutation(3)
        scr = [dl[perm[k]] for k in range(3)]
        if nearest_at_mindepth(scr) != nearest_at_mindepth(dl):
            moved = True
            break
    assert moved, "scramble never moved selection on [0,1,0] -- discriminator inert"

    # ---- data-backed checks (real corpus, representative stride slice) ----
    items = load_items(max_items=1500, representative=True)
    buried = [e for e in items if e["subj_pos"] != 0]
    assert len(buried) > 100, "too few buried items in smoke slice"
    # arms differ
    preds = {a: np.asarray([e["nums"][fn(e)] for e in buried]) for a, fn in DET_ARMS.items()}
    digs = {a: hashlib.sha256(preds[a].tobytes()).hexdigest() for a in preds}
    assert len(set(digs.values())) >= 2, "arms bit-identical: %s" % digs
    # baseline in band (META_RULE_AG)
    maj = _majority_acc(buried)
    assert maj is not None and 0.05 < maj < 0.95, "majority_buried out of band (AG): %s" % maj
    # registered rule beats nearest_noun on this slice (sanity, not a gate)
    nd0, _ = _acc_and_sel(buried, sel_nearest_depth0)
    nn, _ = _acc_and_sel(buried, sel_nearest_noun)
    print("[%s] slice: nearest_depth0=%.4f nearest_noun=%.4f majority=%.4f (n_buried=%d)" %
          (ANCHOR_NAME, nd0, nn, maj, len(buried)), flush=True)
    # scramble fires on the slice
    ta, sa, cf = _scramble_drop(buried, SCRAMBLE_SEEDS[:2])
    print("[%s] slice scramble: true=%.4f scrambled_mean=%.4f change_frac_mean=%.4f" %
          (ANCHOR_NAME, ta, float(np.mean(sa)), float(np.mean(cf))), flush=True)
    assert float(np.mean(cf)) > 0.05, "scramble changed <5%% of selections on slice -- inert"
    # POS tagger probe (report availability; never assert -- second arm is optional)
    tagger, diag = _get_nltk_tagger()
    print("[%s] pos_tagger=%s%s" % (ANCHOR_NAME, "AVAILABLE" if tagger else "UNAVAILABLE",
                                    "" if tagger else (" (%s)" % diag)), flush=True)
    if tagger is not None:
        dlp = _pos_depth_list(items[0], tagger)
        assert len(dlp) == len(items[0]["noun_word_idx"]), "pos_depth length mismatch"
    print("[%s] SELF-TEST PASS (hand-traces + scramble + arms-differ + majority_buried=%.4f in band)" %
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
