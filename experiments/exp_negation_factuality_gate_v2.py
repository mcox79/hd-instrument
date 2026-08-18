"""NEGATION/FACTUALITY GATE v2 -- LABELED conj-only scope propagation (fixes the v1 HARD_FAIL).

QUESTION (v1 -> v2): v1's DIRECT negation gate is a real correctness win (cue-recall 0.939, direct
scope-attachment 0.933, negated who-is-affected 0.50 -> 0.886, ZERO clean-affirmative cost). BUT v1
HARD_FAILed because its DOWNWARD conj-propagation runs over the UNLABELED persisted parse: a downward
verbal-dependent closure cannot tell a genuine coordinate `conj` verb from an xcomp/ccomp/acl/advcl
COMPLEMENT/ADJUNCT verb, so a negation on the matrix verb leaks into the complement clause
("did not remember [George telling]" -> telling wrongly NEGATED). Result: 8/66 affirmatives over-negated
(30.8% of distractors), affirmative regression 0.121 > 0.05 bar.

THE v2 FIX (glass-box, parse-based, NO training, NO LLM): wire the PERSISTED arc_labeler (Front-end Asset 3,
data/frontend_assets/arc_labeler_hashed_ud_ewt.json, label-acc 0.94 / LAS 0.76, currently UNUSED by
candidate_generator) into the scope closure. Restrict negation propagation to genuine `conj` edges ONLY,
EXCLUDING xcomp/ccomp/acl/advcl (and every other) complement+adjunct edge. A negation on the matrix verb
does NOT propagate into a complement clause. The v1 DIRECT gate (cue + head-attachment) is UNCHANGED.

MONOTONICITY (bounds the trade-off): v2 propagates a strict SUBSET of v1's downward edges (v2 keeps an edge
iff v1 kept it AND its predicted deprel == conj). Therefore, arm-to-arm, v2 over-negation <= v1 over-negation
(v2 can only FIX false-negations, never create new ones) and v2 conj-recall <= v1 conj-recall (v2 can only
LOSE genuine coordinated negations the labeler mis-labels). Both directions are measured + reported.

THREE ARMS (ONE variable = the scope-propagation rule; identical items, identical gold, identical scoring):
  gate_off        : current reader; always REALIZED; keeps the patient. (REAL baseline, re-derived.)
  v1_unlabeled    : v1 downward verbal-dependent closure, NO label restriction. (REAL baseline, re-derived;
                    positive-control -- must reproduce landed v1 metrics within tolerance.)
  v2_labeled_conj : v2 downward closure restricted to predicted-deprel == conj edges. (THE FIX.)

CAN-FAIL (pre-registered, both directions REPORTED):
  (i)  the arc_labeler may MIS-label a true complement (xcomp/ccomp) as conj on the noisy real parse -> v2
       STILL over-negates that distractor (observed at design probe: AFD_068 trigger->want mislabeled conj;
       AFD_092 refer->hesitate a conj parse-attach error). Measured: over_negation_rate_distractor(v2).
  (ii) the arc_labeler may mis-label a true `conj` as something else -> v2 UNDER-propagates and MISSES a
       genuine coordinated negation the v1 arm caught. Measured: conj-recall(v2) vs conj-recall(v1)=0.810,
       and n_conj_lost_vs_v1 (the specific NEG items v1 caught but v2 drops).

DESIGN-GATE (pre-registered; verified at run):
  (G1) REAL baselines = gate_off AND v1_unlabeled, BOTH re-derived on the identical item set (not cited).
  (G2) baseline_in_band: gate_off net who-is-affected accuracy in (0.05, 0.95) (= 0.50 on the balanced set).
  (G3) difficulty-on: the conj/complement DISTRACTOR cases that broke v1 are present (n_aff_distractor>0,
       n_conj_neg>0, n_direct_neg>0), asserted at run.
  (G4) one-variable: unlabeled-propagation (v1) vs labeled-conj-only-propagation (v2); same items/gold/score.
  (Gctrl) positive-control: v1_unlabeled arm reproduces landed v1 (direct 0.933 / cue 0.939 / conj 0.810 /
       over_neg_distractor 0.308 / lift 0.894) within tol 0.03; else the re-derivation is wrong -> flag.

LEAK-HUNT (reported in metrics, load-bearing):
  - The arc_labeler's conj/xcomp/ccomp labels are PREDICTIONS on the PERSISTED (learned, UAS~0.79) parse
    heads -- labeler.label(tokens, pos, r.heads) -- NOT gold deprels. So the labeled test is NON-CIRCULAR:
    the gate's edge-typing is a second learned model over the same noisy heads, never the gold parse.
    Asserted: the gate never reads gold['patient'] / gold['neg_info'] / gold deprel (extraction held FIXED
    at the gold verb+patient; ONLY the factuality gate varies; the gate sees ONLY tokens/pos/heads/labels).
  - MUST-FAIL control: scramble cue->verb attachment on the v2 arm; if scrambled scope-accuracy ~= real,
    the harness has a single-verb-majority degeneracy. single_verb_fraction + scrambled accuracy reported.

VERDICT BANDS (pre-registered; primary subject = the v2 arm):
  HARD_PASS: v2 cue-detection recall >= 0.95 on NEGATED; v2 DIRECT scope-attachment >= 0.85; v2 net
    who-is-affected lift on NEGATED >= 0.30 absolute; v2 affirmative regression <= 0.02 absolute.
  HARD_FAIL: v2 DIRECT scope-attachment < 0.60; OR v2 affirmative regression > 0.05 absolute.
  MIDDLE_BAND: between the bars (e.g. regression in (0.02, 0.05] = net-positive but not clean).
  ALSO REPORTED (not a gate, but the headline story): the DELTA v2-vs-v1 on over_negation_rate_distractor,
    affirmative_regression, and conj-recall -- did labeled edge-typing fix the over-negation, and at what
    cost to genuine coordinated-negation recall?

COMPUTE ARCHITECTURE (mandatory): class (b) sequential-CPU with justification -- load persisted tagger json
+ arc npz + labeler json once, tag+parse+label ~132 short sentences (arc-factored O(n^2), n<~30). Wall <
~2min. FOREGROUND local-to-completion. NO queue; NO push; NO remote-persist; NO store write. Storage:
no_storage (extraction/factuality-precision measurement, not a superposition/composition cell). Determinism:
models PERSISTED + loaded (no training); OMP/MKL/OPENBLAS=1; fixed int seed for the scramble control;
no salted hash / list(set).

CELL-TEMPLATE (subset for a LOCAL foreground measurement; NOT queue-dispatched):
- final_metrics_atomicity: tmp_replace (os.replace)
- except SystemExit: raise BEFORE except Exception (no BaseException); crash -> CELL_CRASHED metrics
- arms differ: gate_off vs v1 vs v2 predicted-affected sets differ (asserted at run; v1 != v2 required)
- discriminator fires: v2 flips >0 negated items to NONE AND v2 propagation differs from v1 on >=1 item
- baseline_in_band at run (0.05 < gate_off net acc < 0.95)
- CRLB n/a: accuracy is a fraction over a fixed gold, no argmax-noise floor
- cardinality n/a: single deterministic pass (no seed axis; one fixed scramble-control seed)
- deterministic_seeding: fixed int SCRAMBLE_SEED; no hash()/list(set) ordering
- all reported numbers MEASURED@ this run's metrics.json
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import argparse
import json
import random
import sys
import time
import traceback
from datetime import datetime, timezone

ANCHOR_NAME = "negation_factuality_gate_v2"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from hdlab.candidate_generator import CandidateGenerator  # noqa: E402
from hdlab.arc_labeler import ArcLabeler  # noqa: E402

POS_PATH = os.path.join(REPO_ROOT, "data", "frontend_assets", "pos_tagger_ud_ewt_upos.json")
ARC_PATH = os.path.join(REPO_ROOT, "data", "frontend_assets", "arc_parser_hashed_ud_ewt.npz")
LAB_PATH = os.path.join(REPO_ROOT, "data", "frontend_assets", "arc_labeler_hashed_ud_ewt.json")
GOLD_PATH = os.path.join(REPO_ROOT, "data", "gold_negation_factuality_ewt_v1",
                         "gold_negation_factuality_ewt_v1.json")
OUT_DIR = os.path.join(REPO_ROOT, "data", "exp_" + ANCHOR_NAME)

CUE_LEX = {"not", "n't", "never"}
FOCUS_FOLLOW = {"only", "just", "merely", "simply", "even"}
# v2 propagates negation ONLY across genuine coordinate edges. Everything else (xcomp/ccomp/acl/advcl/
# parataxis/...) is a complement/adjunct clause boundary that a matrix-verb negation does NOT cross.
PROPAGATE_LABELS = {"conj"}
SCRAMBLE_SEED = 1234

# v1 landed reference (positive-control target; MEASURED@data/exp_negation_factuality_gate_v1/metrics.json)
V1_REF = {
    "scope_attachment_accuracy_DIRECT": 0.9333333333333333,
    "cue_detection_recall_on_negated": 0.9393939393939394,
    "scope_attachment_accuracy_CONJ_flagged": 0.8095238095238095,
    "over_negation_rate_distractor": 0.3076923076923077,
    "lift_negated_subset": 0.8939,
    "affirmative_regression": 0.1212,
}
V1_TOL = 0.03


# ------------------------------------------------------------------------------------------------
def _write_atomic(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2)
    os.replace(tmp, path)


def _write_crash_metrics(exc):
    diag = {"verdict": "CELL_CRASHED", "verdict_msg": "%s: %s" % (type(exc).__name__, str(exc)[:400]),
            "summary": "CELL_CRASHED: %s" % type(exc).__name__, "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000], "ts_iso": datetime.now(timezone.utc).isoformat(),
            "anchor_name": ANCHOR_NAME}
    _write_atomic(os.path.join(OUT_DIR, "metrics.json"), diag)


# ------------------------------------------------------------------------------------------------
def align_verb(gold_item, tokens, pos):
    """Persisted-token index (1-based) of the gold labeled verb. UNCHANGED from v1 (shared across arms so
    the comparison isolates the propagation rule). Returns (idx or None, mistag_bool)."""
    gform = gold_item["verb"]["form"].lower()
    glem = gold_item["verb"]["lemma"].lower()
    gpos = gold_item["verb"]["id"] / max(1, gold_item["n_tokens"])
    n = len(tokens)

    def match(tok):
        t = tok.lower()
        return t == gform or t == glem or (len(gform) >= 4 and t[:4] == gform[:4]) or \
               (len(glem) >= 4 and t[:4] == glem[:4])

    verb_hits = [i for i in range(1, n + 1) if pos[i - 1] == "VERB" and match(tokens[i - 1])]
    if verb_hits:
        return min(verb_hits, key=lambda i: abs(i / max(1, n) - gpos)), False
    any_hits = [i for i in range(1, n + 1) if match(tokens[i - 1])]
    if any_hits:
        return min(any_hits, key=lambda i: abs(i / max(1, n) - gpos)), True
    return None, False


def detect_cues(tokens):
    """1-based cue indices (lexical) with FOCUS/SUGGESTION guards. UNCHANGED from v1."""
    cues = []
    n = len(tokens)
    for i in range(1, n + 1):
        low = tokens[i - 1].lower()
        if low not in CUE_LEX:
            continue
        nxt = tokens[i].lower() if i < n else ""
        if nxt in FOCUS_FOLLOW:
            continue
        prv = tokens[i - 2].lower() if i >= 2 else ""
        if prv == "why":
            continue
        cues.append(i)
    return cues


def verb_conj_closure(heads, pos, start_verb, n, labels=None):
    """Verbs in the DOWNWARD scope of a negation attached to start_verb, on the persisted parse.

    labels is None  -> v1 UNLABELED closure: every downward verbal dependent inherits NEGATED (the v1 bug:
                       reaches xcomp/ccomp/acl/advcl complement+adjunct verbs).
    labels is a dict -> v2 LABELED closure: a downward verbal dependent j inherits NEGATED ONLY IF its
                       predicted arc deprel labels[j] is in PROPAGATE_LABELS ({conj}); complement/adjunct
                       edges are the factivity/scope boundary and are NOT crossed.

    Deliberately does NOT climb to start_verb's own head (propagating UP to an affirmative matrix verb is a
    separate v1-caught bug). labels[j] = predicted deprel of the arc (dep=j -> head=heads[j]) on the
    PERSISTED heads (a learned model over noisy heads -- non-circular vs gold)."""
    scope = {start_verb}
    changed = True
    while changed:
        changed = False
        for j in range(1, n + 1):
            if pos[j - 1] != "VERB" or j in scope:
                continue
            if heads.get(j) in scope:                       # j is a downward verbal dependent of a scoped verb
                if labels is not None and labels.get(j) not in PROPAGATE_LABELS:
                    continue                                # v2: cross ONLY genuine conj edges
                scope.add(j)
                changed = True
    return scope


def gate_predict(target_verb, cues, heads, pos, n, labels=None, scramble_rng=None):
    """Predict factuality for target_verb. Returns (is_negated, mode) with mode in {direct, conj, none}.
    labels=None -> v1 unlabeled propagation; labels=dict -> v2 labeled conj-only propagation. If
    scramble_rng given, each cue is reassigned to a RANDOM verb (must-fail control) before scope."""
    if target_verb is None or not cues:
        return False, "none"
    verbs = [i for i in range(1, n + 1) if pos[i - 1] == "VERB"]
    for c in cues:
        if scramble_rng is not None and verbs:
            head = scramble_rng.choice(verbs)
        else:
            head = heads.get(c)
        if head == target_verb:
            return True, "direct"
        if head and 1 <= head <= n and pos[head - 1] == "VERB":
            if target_verb in verb_conj_closure(heads, pos, head, n, labels=labels):
                return True, "conj"
    return False, "none"


# ------------------------------------------------------------------------------------------------
ARMS = ("gate_off", "v1_unlabeled", "v2_labeled_conj")


def run(gold, gen, lab, test_only=False):
    items = {k: v for k, v in gold.items() if (not test_only or v.get("split") == "test")}
    rng_v2 = random.Random(SCRAMBLE_SEED)

    per = {}
    align_fail = 0
    labeler_touched = 0
    for k, v in items.items():
        r = gen.generate(v["text"])
        n = len(r.tokens)
        tv, mistag = align_verb(v, r.tokens, r.pos)
        cues = detect_cues(r.tokens)
        labels = lab.label(r.tokens, r.pos, r.heads)   # PREDICTED deprels on PERSISTED heads (non-circular)
        labeler_touched += 1
        if tv is None:
            align_fail += 1

        # ARM predictions (extraction held FIXED at gold verb+patient; ONLY the gate rule varies)
        neg_off, mode_off = False, "none"
        neg_v1, mode_v1 = gate_predict(tv, cues, r.heads, r.pos, n, labels=None)
        neg_v2, mode_v2 = gate_predict(tv, cues, r.heads, r.pos, n, labels=labels)
        neg_v2_scr, _ = gate_predict(tv, cues, r.heads, r.pos, n, labels=labels, scramble_rng=rng_v2)

        gold_neg = (v["factuality"] == "NEGATED")
        band = ("hard_conjprop" if (gold_neg and v.get("neg_info", {}).get("propagation") == "conj_propagated")
                else ("medium_multiverb" if (gold_neg and v["n_verbs"] >= 2)
                      else ("easy_singleverb" if gold_neg else "affirmative")))

        # diagnostic: label of the target verb's own arc (why v2 kept/dropped it)
        tv_label = labels.get(tv) if tv is not None else None
        tv_head = r.heads.get(tv) if tv is not None else None

        per[k] = {
            "gold_factuality": v["factuality"], "aff_type": v.get("aff_type"),
            "band": band, "n_verbs": v["n_verbs"], "n_tokens_persisted": n,
            "cue_detected": bool(cues),
            "verb_aligned": tv is not None, "verb_mistag": mistag,
            "tv_label": tv_label, "tv_head_is_verb": (tv_head is not None and 1 <= (tv_head or 0) <= n
                                                      and r.pos[(tv_head or 1) - 1] == "VERB"),
            "pred": {"gate_off": neg_off, "v1_unlabeled": neg_v1, "v2_labeled_conj": neg_v2},
            "mode": {"gate_off": mode_off, "v1_unlabeled": mode_v1, "v2_labeled_conj": mode_v2},
            "pred_v2_scrambled": neg_v2_scr,
            # who-is-affected correctness per arm (gate_off keeps patient always)
            "correct": {a: ((per_pred == gold_neg) if a != "gate_off" else (v["factuality"] == "REALIZED"))
                        for a, per_pred in
                        [("gate_off", neg_off), ("v1_unlabeled", neg_v1), ("v2_labeled_conj", neg_v2)]},
        }
    return per, align_fail, len(items), labeler_touched


def summarize_arm(per, arm):
    neg = [k for k, p in per.items() if p["gold_factuality"] == "NEGATED"]
    aff = [k for k, p in per.items() if p["gold_factuality"] == "REALIZED"]
    aff_clean = [k for k in aff if per[k]["aff_type"] == "clean"]
    aff_distract = [k for k in aff if per[k]["aff_type"] == "distractor"]
    direct = [k for k in neg if per[k]["band"] in ("easy_singleverb", "medium_multiverb")]
    conj = [k for k in neg if per[k]["band"] == "hard_conjprop"]

    def pred(k):
        return per[k]["pred"][arm] if arm != "gate_off" else False

    def frac(keys, fn):
        return (sum(1 for k in keys if fn(k)) / len(keys)) if keys else None

    cue_recall = frac(neg, lambda k: per[k]["cue_detected"])
    scope_direct = frac(direct, pred)
    scope_conj = frac(conj, pred)
    scope_all_neg = frac(neg, pred)
    overneg_all = frac(aff, pred)
    overneg_clean = frac(aff_clean, pred)
    overneg_distract = frac(aff_distract, pred)

    gateoff_neg = 0.0 if neg else None                 # off keeps patient -> 0 correct on negated
    gateoff_aff = 1.0 if aff else None                 # off keeps patient -> 1 correct on affirmative
    arm_neg = frac(neg, lambda k: per[k]["correct"][arm])
    arm_aff = frac(aff, lambda k: per[k]["correct"][arm])
    net_acc = frac(list(per.keys()), lambda k: per[k]["correct"][arm])

    miss = [k for k in neg if not pred(k)]
    overneg_ids = [k for k in aff if pred(k)]

    return {
        "n_negated": len(neg), "n_affirmative": len(aff), "n_aff_clean": len(aff_clean),
        "n_aff_distractor": len(aff_distract), "n_direct_neg": len(direct), "n_conj_neg": len(conj),
        "cue_detection_recall_on_negated": cue_recall,
        "scope_attachment_accuracy_DIRECT": scope_direct,
        "scope_attachment_accuracy_CONJ_flagged": scope_conj,
        "negation_recall_all": scope_all_neg,
        "over_negation_rate_all_affirmatives": overneg_all,
        "over_negation_rate_clean": overneg_clean,
        "over_negation_rate_distractor": overneg_distract,
        "net_whoaffected_acc": net_acc,
        "acc_negated_subset": arm_neg, "acc_affirmative_subset": arm_aff,
        "lift_negated_subset": (None if arm_neg is None or gateoff_neg is None else round(arm_neg - gateoff_neg, 4)),
        "affirmative_regression": (None if arm_aff is None or gateoff_aff is None else round(gateoff_aff - arm_aff, 4)),
        "n_miss_real_negation": len(miss), "n_over_negated_affirmative": len(overneg_ids),
        "miss_real_negation_ids": sorted(miss), "over_negated_affirmative_ids": sorted(overneg_ids),
    }


def scramble_summary(per):
    direct = [k for k, p in per.items() if p["band"] in ("easy_singleverb", "medium_multiverb")]
    def frac(keys, fn):
        return (sum(1 for k in keys if fn(k)) / len(keys)) if keys else None
    return {
        "scrambled_scope_accuracy_DIRECT_mustfail_control": frac(direct, lambda k: per[k]["pred_v2_scrambled"]),
        "single_verb_fraction": frac(list(per.keys()), lambda k: per[k]["n_verbs"] <= 1),
    }


def verdict_of(s_v2):
    sd = s_v2["scope_attachment_accuracy_DIRECT"]
    cr = s_v2["cue_detection_recall_on_negated"]
    lift = s_v2["lift_negated_subset"]
    reg = s_v2["affirmative_regression"]
    if sd is None:
        return "UNKNOWN", "no direct-negation items"
    if sd < 0.60 or (reg is not None and reg > 0.05):
        return "HARD_FAIL", "v2 direct scope %.3f (<0.60) or affirm regression %s (>0.05)" % (sd, reg)
    hp = (cr is not None and cr >= 0.95 and sd >= 0.85 and lift is not None and lift >= 0.30
          and reg is not None and reg <= 0.02)
    if hp:
        return "HARD_PASS", "v2 cue %.3f scope %.3f lift %.3f reg %.3f" % (cr, sd, lift, reg)
    return "MIDDLE_BAND", "v2 cue=%s scope=%.3f lift=%s reg=%s" % (cr, sd, lift, reg)


def positive_control(s_v1):
    """v1_unlabeled arm must reproduce landed v1 metrics within V1_TOL."""
    checks = {}
    ok = True
    for key, ref in V1_REF.items():
        got = s_v1.get(key)
        if got is None:
            checks[key] = {"got": None, "ref": ref, "ok": False}
            ok = False
            continue
        delta = abs(got - ref)
        passed = delta <= V1_TOL
        checks[key] = {"got": round(got, 4), "ref": ref, "delta": round(delta, 4), "ok": passed}
        ok = ok and passed
    return ok, checks


def main():
    t0 = time.perf_counter()
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()

    if not (os.path.exists(POS_PATH) and os.path.exists(ARC_PATH) and os.path.exists(LAB_PATH)):
        raise FileNotFoundError("persisted front-end assets missing: %s / %s / %s"
                                % (POS_PATH, ARC_PATH, LAB_PATH))
    gold = json.load(open(GOLD_PATH, encoding="utf-8"))["gold"]
    gen = CandidateGenerator.load(POS_PATH, ARC_PATH)
    lab = ArcLabeler.load(LAB_PATH)

    if args.self_test:
        # Exercise the REAL front-end + labeler + BOTH gate rules on hand-traced sentences.
        # v1 (unlabeled) over-negates the complement; v2 (labeled conj-only) must NOT.
        checks = []
        cases = [
            # (text, verbform, expect_v1_neg, expect_v2_neg, note)
            ("He did not break the vase.", "break", True, True, "direct: both negate"),
            ("She broke the vase but did not fix it.", "broke", False, False, "affirmative matrix: neither"),
            ("She broke the vase but did not fix it.", "fix", True, True, "direct-neg: both"),
            # complement over-negation: v1 leaks into ccomp; v2 must stop at the clause boundary
            ("Baba Groom did not remember George telling stories.", "telling", True, False,
             "ccomp complement: v1 over-negates, v2 fixes"),
            ("I do not want him to spend money.", "spend", True, False,
             "xcomp complement: v1 over-negates, v2 fixes"),
        ]
        for text, vf, exp_v1, exp_v2 in [(c[0], c[1], c[2], c[3]) for c in cases]:
            r = gen.generate(text)
            n = len(r.tokens)
            labels = lab.label(r.tokens, r.pos, r.heads)
            tv = next((i for i in range(1, n + 1) if r.tokens[i - 1].lower().startswith(vf[:3])
                       and r.pos[i - 1] == "VERB"), None)
            cues = detect_cues(r.tokens)
            neg_v1, m1 = gate_predict(tv, cues, r.heads, r.pos, n, labels=None)
            neg_v2, m2 = gate_predict(tv, cues, r.heads, r.pos, n, labels=labels)
            checks.append({"text": text, "verb": vf, "v1": neg_v1, "v2": neg_v2,
                           "exp_v1": exp_v1, "exp_v2": exp_v2, "tv_label": labels.get(tv),
                           "mode_v1": m1, "mode_v2": m2})
            assert neg_v1 == exp_v1, "SELFTEST v1 FAIL: %r verb=%s got %s want %s" % (text, vf, neg_v1, exp_v1)
            assert neg_v2 == exp_v2, "SELFTEST v2 FAIL: %r verb=%s got %s want %s" % (text, vf, neg_v2, exp_v2)
        # arms-must-differ: v1 and v2 disagree on >=1 self-test case
        assert any(c["v1"] != c["v2"] for c in checks), "SELFTEST FAIL: v1 and v2 never differ (no fix wired)"
        print("SELFTEST_PASS", json.dumps(checks), flush=True)
        _write_atomic(os.path.join(OUT_DIR, "metrics.json"),
                      {"verdict": "SELFTEST_PASS", "verdict_msg": "front-end + labeler + v1/v2 gates self-test ok",
                       "run_mode": "self_test", "elapsed_s": round(time.perf_counter() - t0, 3),
                       "summary": "SELFTEST_PASS", "ts_iso": datetime.now(timezone.utc).isoformat(),
                       "self_test_cases": checks})
        return

    per_all, align_fail_all, n_all, labeler_touched = run(gold, gen, lab, test_only=False)
    per_test, _, n_test, _ = run(gold, gen, lab, test_only=True)

    s = {arm: summarize_arm(per_all, arm) for arm in ARMS}
    s_test = {arm: summarize_arm(per_test, arm) for arm in ARMS}
    scr = scramble_summary(per_all)

    # positive control: v1 arm reproduces landed v1
    pc_ok, pc_checks = positive_control(s["v1_unlabeled"])

    # discriminator + arms-differ + design-gate assertions
    v2_flips = sum(1 for p in per_all.values() if p["pred"]["v2_labeled_conj"])
    v1_v2_differ_items = [k for k, p in per_all.items()
                          if p["pred"]["v1_unlabeled"] != p["pred"]["v2_labeled_conj"]]
    arms_differ = (len(v1_v2_differ_items) > 0)
    baseline_in_band = (s["gate_off"]["net_whoaffected_acc"] is not None
                        and 0.05 < s["gate_off"]["net_whoaffected_acc"] < 0.95)
    difficulty_on = (s["v2_labeled_conj"]["n_direct_neg"] > 0
                     and s["v2_labeled_conj"]["n_conj_neg"] > 0
                     and s["v2_labeled_conj"]["n_aff_distractor"] > 0)

    # v2-vs-v1 deltas (the headline story)
    def d(key):
        a = s["v2_labeled_conj"].get(key)
        b = s["v1_unlabeled"].get(key)
        return None if (a is None or b is None) else round(a - b, 4)
    deltas = {
        "over_negation_rate_distractor_v2_minus_v1": d("over_negation_rate_distractor"),
        "over_negation_rate_all_affirmatives_v2_minus_v1": d("over_negation_rate_all_affirmatives"),
        "affirmative_regression_v2_minus_v1": d("affirmative_regression"),
        "scope_attachment_accuracy_CONJ_v2_minus_v1": d("scope_attachment_accuracy_CONJ_flagged"),
        "negation_recall_all_v2_minus_v1": d("negation_recall_all"),
        "net_whoaffected_acc_v2_minus_v1": d("net_whoaffected_acc"),
    }
    # under-propagation: NEG items v1 caught but v2 dropped (CAN-FAIL direction ii)
    conj_lost_ids = sorted([k for k, p in per_all.items()
                            if p["gold_factuality"] == "NEGATED"
                            and p["pred"]["v1_unlabeled"] and not p["pred"]["v2_labeled_conj"]])
    # over-negations that REMAIN in v2 (CAN-FAIL direction i)
    overneg_remaining = sorted([k for k, p in per_all.items()
                                if p["gold_factuality"] == "REALIZED" and p["pred"]["v2_labeled_conj"]])
    overneg_remaining_diag = {k: {"tv_label": per_all[k]["tv_label"], "aff_type": per_all[k]["aff_type"],
                                  "mode_v2": per_all[k]["mode"]["v2_labeled_conj"]} for k in overneg_remaining}

    verdict, vmsg = verdict_of(s["v2_labeled_conj"])
    if not pc_ok:
        verdict = "FLAG_POSCTRL_" + verdict
        vmsg = "POSITIVE-CONTROL MISMATCH (v1 arm != landed v1); " + vmsg

    elapsed = round(time.perf_counter() - t0, 3)
    metrics = {
        "verdict": verdict, "verdict_msg": vmsg, "summary": "negation gate v2 (labeled conj-only): %s" % vmsg,
        "run_mode": "full", "elapsed_s": elapsed, "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR_NAME,
        "n_items_all": n_all, "n_items_test": n_test, "align_fail": align_fail_all,
        "labeler_predicted_on_persisted_parse": True, "labeler_items_labeled": labeler_touched,
        "discriminator_fires_v2_flipped_count": v2_flips,
        "arms_differ_v1_vs_v2": arms_differ, "n_items_v1_v2_differ": len(v1_v2_differ_items),
        "v1_v2_differ_item_ids": sorted(v1_v2_differ_items),
        "baseline_in_band": baseline_in_band, "difficulty_on": difficulty_on,
        "positive_control_v1_reproduced": pc_ok, "positive_control_checks": pc_checks,
        "deltas_v2_minus_v1": deltas,
        "conj_negations_lost_v2_vs_v1_ids": conj_lost_ids, "n_conj_negations_lost": len(conj_lost_ids),
        "over_negations_remaining_v2_ids": overneg_remaining,
        "over_negations_remaining_v2_diag": overneg_remaining_diag,
        "scramble_control": scr,
        "summary_by_arm_ALL": s, "summary_by_arm_TEST": s_test,
        "per_item": per_all,
    }
    _write_atomic(os.path.join(OUT_DIR, "metrics.json"), metrics)

    print("=== NEGATION/FACTUALITY GATE v2 (labeled conj-only) -- ALL items n=%d ===" % n_all, flush=True)
    keys = ["over_negation_rate_distractor", "over_negation_rate_all_affirmatives", "affirmative_regression",
            "scope_attachment_accuracy_DIRECT", "cue_detection_recall_on_negated",
            "scope_attachment_accuracy_CONJ_flagged", "negation_recall_all", "lift_negated_subset",
            "acc_negated_subset", "net_whoaffected_acc"]
    print("  %-46s %10s %10s %10s" % ("metric", "gate_off", "v1_unlab", "v2_conj"), flush=True)
    for kk in keys:
        print("  %-46s %10s %10s %10s"
              % (kk, s["gate_off"].get(kk), s["v1_unlabeled"].get(kk), s["v2_labeled_conj"].get(kk)), flush=True)
    print("  --- deltas v2-v1 ---", flush=True)
    for kk, vv in deltas.items():
        print("  %-46s %s" % (kk, vv), flush=True)
    print("  scramble:", scr, flush=True)
    print("  conj_negations_lost_v2_vs_v1:", conj_lost_ids, flush=True)
    print("  over_negations_remaining_v2:", overneg_remaining, "diag:", overneg_remaining_diag, flush=True)
    print("  positive_control_v1_reproduced=%s" % pc_ok, pc_checks, flush=True)
    print("VERDICT:", verdict, "|", vmsg, flush=True)
    print("discriminator_v2_flips=%d arms_differ_v1v2=%s n_differ=%d baseline_in_band=%s difficulty_on=%s align_fail=%d"
          % (v2_flips, arms_differ, len(v1_v2_differ_items), baseline_in_band, difficulty_on, align_fail_all),
          flush=True)


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        _write_crash_metrics(e)
        raise
