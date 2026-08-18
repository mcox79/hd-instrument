"""NEGATION/FACTUALITY GATE for the who-is-affected reader (Phase 2+3).

QUESTION: the reader currently DISCARDS negation ("not"/"never" sit in its FUNCWORD stopword set), so
"he did not break it" is read as "he broke it" (vase marked affected). Does a glass-box cue+scope gate on
the PERSISTED front-end (pos_tagger + arc_parser, loaded not retrained) correctly FLIP negated events to
"not-affected / event-did-not-happen" (recall on negation) WITHOUT over-negating affirmatives (precision)?

THE GATE (glass-box, parse-based, NO training, NO LLM):
  cue detection : persisted token whose lower-lemma in {not, n't, never} (ud_tokenize splits didn't->did n't;
                  cannot->can not). FOCUS guard: 'not only/just/merely' = focus (both conjuncts happen), not
                  negation. SUGGESTION guard: 'why not V' = exhortation, event realized. (Matches the gold
                  builder's clausal-negation definition; determiner/interjection 'no' excluded.)
  scope resolve : on the PERSISTED (unlabeled) parse, the cue's head token IS the negated predicate
                  (dependency ATTACHMENT, not surface distance). conj-PROPAGATION: the negated verb's
                  coordinated verbs (verb-headed-by-verb closure on the persisted heads) inherit NEGATED.
  output        : factuality tag {REALIZED (default) | NEGATED}. NEGATED -> who-is-affected = NONE.

ISOLATION (ONE variable = gate on/off): extraction is held FIXED at the gold (verb, patient) so the ONLY
thing that varies is the factuality gate. The gate's decision uses ONLY the persisted parse + cue lexicon
-- it never sees the gold patient (no ground-by-X-grade-by-X). Gate-OFF = current reader (always REALIZED,
always keeps the patient). Gate-ON = flips items it tags NEGATED to NONE.

LEAK-HUNT (reported in metrics, load-bearing):
  - GOLD label (NEGATED?) is derived from the GOLD parse; the GATE prediction uses the PERSISTED parse (a
    different, learned parser, UAS ~0.79). Direct-attachment items are a clean, non-circular test of the
    persisted parser's attachment quality.
  - CONJ-PROPAGATION caveat: the propagation RULE (negation spreads across conj) is SHARED by gold-labeler
    and gate, so conj-prop items partly test parse-STRUCTURE recovery, NOT propagation CORRECTNESS; and
    hand-audit found ~2-3/21 linguistic over-reaches ('neg X and [positive] Y'). Reported SEPARATELY, flagged.
  - MUST-FAIL control: scramble cue->verb attachment; if scrambled scope-accuracy ~= real, the harness has a
    single-verb-majority degeneracy (attachment does no work). single_verb_fraction reported.

DESIGN-GATE (pre-registered; verified at run):
  (G1) REAL baseline = gate-OFF = the current ignore-negation reader on the identical item set.
  (G2) baseline_in_band: gate-OFF net who-is-affected accuracy in (0.05, 0.95) (near 0.5 on a balanced set).
  (G3) difficulty-on: NEGATED items span easy(direct single-verb)/medium(direct multi-verb)/hard(conj-prop);
       affirmatives include DISTRACTORS (a negation cue scoping a DIFFERENT verb). asserted at run.
  (G4) one-variable: gate on/off; same items, same gold, same scoring.

VERDICT BANDS (pre-registered):
  HARD_PASS: cue-detection recall >= 0.95 on NEGATED; DIRECT scope-attachment accuracy >= 0.85; net
    who-is-affected accuracy lift (gate-on - gate-off) on the NEGATED subset >= 0.30 absolute;
    affirmative accuracy regression <= 0.02 absolute (over-negation rate <= 0.02).
  HARD_FAIL: DIRECT scope-attachment accuracy < 0.60 (UD-attachment insufficient, needs a real resolver);
    OR affirmative accuracy regresses > 0.05 absolute (net-harmful over-negation).
  MIDDLE_BAND: between the bars.

COMPUTE ARCHITECTURE (mandatory): class (b) sequential-CPU with justification -- load persisted tagger json
+ arc npz once, tag+parse ~132 short sentences (arc-factored O(n^2), n<~30). Wall < ~2min. FOREGROUND
local-to-completion. NO queue; NO push; NO remote-persist; NO store write. Storage: no_storage (extraction/
factuality-precision measurement, not a superposition/composition cell). Determinism: models PERSISTED +
loaded (no training); OMP/MKL/OPENBLAS=1; fixed int seed for the scramble control; no salted hash/list(set).

CELL-TEMPLATE (subset for a LOCAL foreground measurement; NOT queue-dispatched):
- final_metrics_atomicity: tmp_replace (os.replace)
- except SystemExit: raise BEFORE except Exception (no BaseException); crash -> CELL_CRASHED metrics
- arms differ: gate-on vs gate-off predicted-affected sets differ (asserted at run)
- discriminator fires: gate flips >0 negated items to NONE
- baseline_in_band at run (0.05 < gate-off net acc < 0.95)
- CRLB n/a: accuracy is a fraction over a fixed gold, no argmax-noise floor
- cardinality n/a: single deterministic pass (no seed axis; one fixed scramble-control seed)
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
from collections import Counter, defaultdict
from datetime import datetime, timezone

ANCHOR_NAME = "negation_factuality_gate_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from hdlab.candidate_generator import CandidateGenerator, ud_tokenize  # noqa: E402

POS_PATH = os.path.join(REPO_ROOT, "data", "frontend_assets", "pos_tagger_ud_ewt_upos.json")
ARC_PATH = os.path.join(REPO_ROOT, "data", "frontend_assets", "arc_parser_hashed_ud_ewt.npz")
GOLD_PATH = os.path.join(REPO_ROOT, "data", "gold_negation_factuality_ewt_v1",
                         "gold_negation_factuality_ewt_v1.json")
OUT_DIR = os.path.join(REPO_ROOT, "data", "exp_" + ANCHOR_NAME)

CUE_LEX = {"not", "n't", "never"}
FOCUS_FOLLOW = {"only", "just", "merely", "simply", "even"}
SCRAMBLE_SEED = 1234


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
    """Find the persisted-token index (1-based) of the gold labeled verb. Surface/prefix match on VERB
    POS, pick the occurrence closest in relative position to the gold verb id. Returns (idx or None,
    mistag_bool)."""
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
    if any_hits:  # verb mis-tagged by the persisted tagger (audit)
        return min(any_hits, key=lambda i: abs(i / max(1, n) - gpos)), True
    return None, False


def detect_cues(tokens):
    """Return list of 1-based cue indices (lexical), with FOCUS/SUGGESTION guards matching the gold."""
    cues = []
    n = len(tokens)
    for i in range(1, n + 1):
        low = tokens[i - 1].lower()
        if low not in CUE_LEX:
            continue
        nxt = tokens[i].lower() if i < n else ""
        if nxt in FOCUS_FOLLOW:            # 'not only ...' focus
            continue
        prv = tokens[i - 2].lower() if i >= 2 else ""
        if prv == "why":                   # 'why not V' suggestion
            continue
        cues.append(i)
    return cues


def verb_conj_closure(heads, pos, start_verb, n):
    """Verbs in the DOWNWARD scope of a negation attached to start_verb, on the UNLABELED persisted
    parse: start_verb plus verbs reachable by following head edges DOWNWARD (a verb whose head is a
    scoped verb). Mirror of the gold conj-propagation (which only spreads to conj DEPENDENTS of the cue
    head). Deliberately does NOT climb to start_verb's own head -- propagating 'did not fix' UP to the
    affirmative matrix verb 'broke' is the bug the self-test caught. (Downward closure can still reach an
    xcomp/ccomp child verb, an over-reach shared with the modal/factivity half -- flagged, Rank-3.)"""
    scope = {start_verb}
    changed = True
    while changed:
        changed = False
        for j in range(1, n + 1):
            if pos[j - 1] != "VERB" or j in scope:
                continue
            if heads.get(j) in scope:      # j is a verbal DEPENDENT of a scoped verb (downward only)
                scope.add(j); changed = True
    return scope


def gate_predict(target_verb, cues, heads, pos, n, scramble_rng=None):
    """Predict factuality for target_verb. Returns (is_negated, mode) where mode in
    {direct, conj, none}. If scramble_rng given, each cue is reassigned to a RANDOM verb (must-fail
    control) before scope resolution."""
    if target_verb is None or not cues:
        return False, "none"
    verbs = [i for i in range(1, n + 1) if pos[i - 1] == "VERB"]
    for c in cues:
        if scramble_rng is not None and verbs:
            head = scramble_rng.choice(verbs)      # scrambled attachment
        else:
            head = heads.get(c)                    # real dependency attachment
        if head == target_verb:
            return True, "direct"
        if head and 1 <= head <= n and pos[head - 1] == "VERB":
            if target_verb in verb_conj_closure(heads, pos, head, n):
                return True, "conj"
    return False, "none"


# ------------------------------------------------------------------------------------------------
def run(gold, gen, test_only=False):
    items = {k: v for k, v in gold.items() if (not test_only or v.get("split") == "test")}
    rng = random.Random(SCRAMBLE_SEED)

    per = {}
    align_fail = 0
    for k, v in items.items():
        r = gen.generate(v["text"])
        n = len(r.tokens)
        tv, mistag = align_verb(v, r.tokens, r.pos)
        cues = detect_cues(r.tokens)
        neg, mode = gate_predict(tv, cues, r.heads, r.pos, n)
        neg_scr, _ = gate_predict(tv, cues, r.heads, r.pos, n, scramble_rng=rng)
        if tv is None:
            align_fail += 1
        band = ("hard_conjprop" if (v["factuality"] == "NEGATED" and v.get("neg_info", {}).get("propagation") == "conj_propagated")
                else ("medium_multiverb" if (v["factuality"] == "NEGATED" and v["n_verbs"] >= 2)
                      else ("easy_singleverb" if v["factuality"] == "NEGATED" else "affirmative")))
        per[k] = {
            "gold_factuality": v["factuality"], "aff_type": v.get("aff_type"),
            "band": band, "n_verbs": v["n_verbs"], "n_tokens_persisted": n,
            "cue_detected": bool(cues), "pred_negated": neg, "pred_mode": mode,
            "pred_negated_scrambled": neg_scr, "verb_aligned": tv is not None, "verb_mistag": mistag,
            # who-is-affected: gate-off ALWAYS keeps patient (REALIZED); gate-on -> NONE iff pred_negated
            "gateoff_correct": (v["factuality"] == "REALIZED"),   # off keeps patient: correct iff really realized
            "gateon_correct": (neg == (v["factuality"] == "NEGATED")),
        }
    return per, align_fail, len(items)


def summarize(per):
    neg = [k for k, p in per.items() if p["gold_factuality"] == "NEGATED"]
    aff = [k for k, p in per.items() if p["gold_factuality"] == "REALIZED"]
    aff_clean = [k for k in aff if per[k]["aff_type"] == "clean"]
    aff_distract = [k for k in aff if per[k]["aff_type"] == "distractor"]
    direct = [k for k in neg if per[k]["band"] in ("easy_singleverb", "medium_multiverb")]
    conj = [k for k in neg if per[k]["band"] == "hard_conjprop"]

    def frac(keys, pred):
        return (sum(1 for k in keys if pred(per[k])) / len(keys)) if keys else None

    cue_recall = frac(neg, lambda p: p["cue_detected"])
    scope_direct = frac(direct, lambda p: p["pred_negated"])            # clean, non-circular headline
    scope_conj = frac(conj, lambda p: p["pred_negated"])               # flagged secondary
    scope_all_neg = frac(neg, lambda p: p["pred_negated"])             # = recall on negation
    scope_scrambled_direct = frac(direct, lambda p: p["pred_negated_scrambled"])
    # over-negation (precision on affirmatives): gate flipped an affirmative to NONE
    overneg_all = frac(aff, lambda p: p["pred_negated"])
    overneg_clean = frac(aff_clean, lambda p: p["pred_negated"])
    overneg_distract = frac(aff_distract, lambda p: p["pred_negated"])
    single_verb_frac = frac(list(per.keys()), lambda p: p["n_verbs"] <= 1)

    # net who-is-affected accuracy
    gateoff_acc = frac(list(per.keys()), lambda p: p["gateoff_correct"])
    gateon_acc = frac(list(per.keys()), lambda p: p["gateon_correct"])
    gateoff_neg = frac(neg, lambda p: p["gateoff_correct"])            # = 0 by construction
    gateon_neg = frac(neg, lambda p: p["gateon_correct"])             # = negation recall
    gateoff_aff = frac(aff, lambda p: p["gateoff_correct"])           # = 1 by construction
    gateon_aff = frac(aff, lambda p: p["gateon_correct"])            # = 1 - over-negation

    # error directions
    miss_real_negation = [k for k in neg if not per[k]["pred_negated"]]      # left REALIZED
    false_negate_affirmative = [k for k in aff if per[k]["pred_negated"]]    # over-negated

    return {
        "n_negated": len(neg), "n_affirmative": len(aff), "n_aff_clean": len(aff_clean),
        "n_aff_distractor": len(aff_distract), "n_direct_neg": len(direct), "n_conj_neg": len(conj),
        "cue_detection_recall_on_negated": cue_recall,
        "scope_attachment_accuracy_DIRECT": scope_direct,
        "scope_attachment_accuracy_CONJ_flagged": scope_conj,
        "negation_recall_all": scope_all_neg,
        "scrambled_scope_accuracy_DIRECT_mustfail_control": scope_scrambled_direct,
        "single_verb_fraction": single_verb_frac,
        "over_negation_rate_all_affirmatives": overneg_all,
        "over_negation_rate_clean": overneg_clean,
        "over_negation_rate_distractor": overneg_distract,
        "net_whoaffected_acc_GATEOFF": gateoff_acc,
        "net_whoaffected_acc_GATEON": gateon_acc,
        "gateoff_acc_negated_subset": gateoff_neg, "gateon_acc_negated_subset": gateon_neg,
        "gateoff_acc_affirmative_subset": gateoff_aff, "gateon_acc_affirmative_subset": gateon_aff,
        "lift_negated_subset": (None if (gateon_neg is None or gateoff_neg is None) else round(gateon_neg - gateoff_neg, 4)),
        "affirmative_regression": (None if (gateon_aff is None or gateoff_aff is None) else round(gateoff_aff - gateon_aff, 4)),
        "n_miss_real_negation": len(miss_real_negation),
        "n_false_negate_affirmative": len(false_negate_affirmative),
        "miss_real_negation_ids": sorted(miss_real_negation),
        "false_negate_affirmative_ids": sorted(false_negate_affirmative),
    }


def verdict_of(s):
    sd = s["scope_attachment_accuracy_DIRECT"]
    cr = s["cue_detection_recall_on_negated"]
    lift = s["lift_negated_subset"]
    reg = s["affirmative_regression"]
    if sd is None:
        return "UNKNOWN", "no direct-negation items"
    if sd < 0.60 or (reg is not None and reg > 0.05):
        return "HARD_FAIL", "direct scope-attach %.3f (<0.60) or affirm regression %s (>0.05)" % (sd, reg)
    hp = (cr is not None and cr >= 0.95 and sd >= 0.85 and lift is not None and lift >= 0.30
          and reg is not None and reg <= 0.02)
    if hp:
        return "HARD_PASS", "cue %.3f scope %.3f lift %.3f reg %.3f" % (cr, sd, lift, reg)
    return "MIDDLE_BAND", "cue=%s scope=%.3f lift=%s reg=%s" % (cr, sd, lift, reg)


def main():
    t0 = time.perf_counter()
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()

    if not (os.path.exists(POS_PATH) and os.path.exists(ARC_PATH)):
        raise FileNotFoundError("persisted front-end assets missing: %s / %s" % (POS_PATH, ARC_PATH))
    gold = json.load(open(GOLD_PATH, encoding="utf-8"))["gold"]
    gen = CandidateGenerator.load(POS_PATH, ARC_PATH)

    if args.self_test:
        # exercise the REAL front-end path + the gate on 3 hand-traced sentences (real_code_path)
        checks = []
        for text, verbform, expect_neg in [
            ("He did not break the vase.", "break", True),
            ("She broke the vase but did not fix it.", "broke", False),   # broke is affirmative
            ("She broke the vase but did not fix it.", "fix", True),      # fix is negated
        ]:
            r = gen.generate(text)
            n = len(r.tokens)
            tv = next((i for i in range(1, n + 1) if r.tokens[i - 1].lower().startswith(verbform[:3])
                       and r.pos[i - 1] == "VERB"), None)
            cues = detect_cues(r.tokens)
            neg, mode = gate_predict(tv, cues, r.heads, r.pos, n)
            checks.append((text, verbform, neg, expect_neg, mode))
            assert neg == expect_neg, "SELFTEST FAIL: %r verb=%s got neg=%s want=%s" % (text, verbform, neg, expect_neg)
        print("SELFTEST_PASS", checks, flush=True)
        _write_atomic(os.path.join(OUT_DIR, "metrics.json"),
                      {"verdict": "SELFTEST_PASS", "verdict_msg": "front-end + gate self-test ok",
                       "run_mode": "self_test", "elapsed_s": round(time.perf_counter() - t0, 3),
                       "summary": "SELFTEST_PASS", "ts_iso": datetime.now(timezone.utc).isoformat()})
        return

    per_all, align_fail_all, n_all = run(gold, gen, test_only=False)
    per_test, _, n_test = run(gold, gen, test_only=True)
    s_all = summarize(per_all)
    s_test = summarize(per_test)

    # discriminator + arms-differ + design-gate assertions
    flipped = sum(1 for p in per_all.values() if p["pred_negated"])
    arms_differ = any(p["gateon_correct"] != p["gateoff_correct"] for p in per_all.values())
    baseline_in_band = (s_all["net_whoaffected_acc_GATEOFF"] is not None
                        and 0.05 < s_all["net_whoaffected_acc_GATEOFF"] < 0.95)
    difficulty_on = (s_all["n_direct_neg"] > 0 and s_all["n_conj_neg"] > 0 and s_all["n_aff_distractor"] > 0)

    verdict, vmsg = verdict_of(s_all)
    elapsed = round(time.perf_counter() - t0, 3)
    metrics = {
        "verdict": verdict, "verdict_msg": vmsg, "summary": "negation gate: %s" % vmsg,
        "run_mode": "full", "elapsed_s": elapsed, "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR_NAME,
        "n_items_all": n_all, "n_items_test": n_test, "align_fail": align_fail_all,
        "discriminator_fires_flipped_count": flipped, "arms_differ": arms_differ,
        "baseline_in_band": baseline_in_band, "difficulty_on": difficulty_on,
        "summary_ALL": s_all, "summary_TEST": s_test,
        "per_item": per_all,
    }
    _write_atomic(os.path.join(OUT_DIR, "metrics.json"), metrics)

    print("=== NEGATION/FACTUALITY GATE (ALL items, n=%d) ===" % n_all, flush=True)
    for kk in ["n_negated", "n_affirmative", "n_aff_distractor", "n_direct_neg", "n_conj_neg",
               "cue_detection_recall_on_negated", "scope_attachment_accuracy_DIRECT",
               "scope_attachment_accuracy_CONJ_flagged", "negation_recall_all",
               "scrambled_scope_accuracy_DIRECT_mustfail_control", "single_verb_fraction",
               "over_negation_rate_all_affirmatives", "over_negation_rate_clean", "over_negation_rate_distractor",
               "net_whoaffected_acc_GATEOFF", "net_whoaffected_acc_GATEON",
               "gateon_acc_negated_subset", "lift_negated_subset", "affirmative_regression",
               "n_miss_real_negation", "n_false_negate_affirmative"]:
        print("  %-48s %s" % (kk, s_all[kk]), flush=True)
    print("VERDICT:", verdict, "|", vmsg, flush=True)
    print("discriminator_fires=%d arms_differ=%s baseline_in_band=%s difficulty_on=%s align_fail=%d"
          % (flipped, arms_differ, baseline_in_band, difficulty_on, align_fail_all), flush=True)


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
