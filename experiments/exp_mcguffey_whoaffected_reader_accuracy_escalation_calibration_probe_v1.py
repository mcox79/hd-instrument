#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""exp_mcguffey_whoaffected_reader_accuracy_escalation_calibration_probe_v1

FIRST-REAL-READING PROBE (honest small-N reconnaissance, NOT a powered capability claim; N=34).
Runs the glass-box reader on REAL McGuffey First Reader story text against the Director-oracle gold
(data/mcguffey_whoaffected_oracle_gold_v1/gold.json) and measures the two make-or-break things:
  (1) READER ACCURACY on who-is-affected vs the oracle gold, OVERALL + BY affectedness-TYPE
      (does it get PATIENT right? does it correctly say NOT-affected for PERCEPTION targets +
       NEGATION -- the USER affectedness-type distinctions).
  (2) ESCALATION-TRIGGER CALIBRATION (the crux of the oracle-escalation loop): do the reader's
      uncertainty cues fire preferentially on its ACTUAL wrong answers? BIFURCATED trigger per the
      brain-grounded drill (notes/research_drill_metacognitive_calibration_escalation_trigger_
      2026-07-21.md): (a) LOW SIGNAL-STRENGTH (arc-parser margin < tau = parietal) OR (b) CONFLICT
      (base-vs-salient CONTRADICTION flag = ACC). Report precision/recall of margin-only, flag-only,
      bifurcated-OR as a WRONG-ANSWER detector; does bifurcated beat either alone (brain prediction)?
  (3) ESCALATION RATE + would escalating+correcting the cue-firing set lift accuracy to ~100% on the
      remaining (non-escalated) covered set (the exact-atom tier of the loop)?

WHO-IS-AFFECTED TARGET DEFINITION (encodes the USER affectedness-type guidance):
  types {patient, effected, transfer} -> there IS an affected entity = gold['affected'] span.
  types {target_not_affected, none, negated} -> NOBODY is affected (correct answer = NONE):
    perception/search/contact targets are NOT changed; negated verbs did not actually affect; and
    stative/possession/intransitive/departure have no affected entity.
  So the raw grammatical-patient reader is EXPECTED to fail perception + negation (it extracts the
  grammatical object where the correct who-is-affected answer is NONE). That gap is the probe's point.

REUSE (read-only import; NO hdlab mutation, NO production reader change): the VALIDATED reader front-
end + overlay wiring from exp_read_discourse_docorder_stateofmind_whoaffected_ud_ewt_v1 (reader_pass,
base_pick, salient_pick, observe_sentence, load_ud_docs, POS/ARC/LABELER paths, UD_TEST) + the census
recon cell's tau-calibration pattern (UD-EWT 16th-pct base-pick margin, applied UNCHANGED = non-circular
comparability, NOT fit to the McGuffey gold).

DESIGN GATE (can-fail, real baseline, difficulty-on):
  real baseline = the reader's RAW who-affected (base_pick). CAN-FAIL: (i) accuracy near-chance on real
  text, OR (ii) the triggers are UNCORRELATED with errors (calibration fails = the oracle-escalation
  loop won't work as designed). Difficulty-on: real archaic McGuffey story text + the hard affectedness
  types (perception target_not_affected, negation). LEAK-CLEAN: the reader never sees the gold; tau is
  UD-calibrated (not McGuffey); the escalation cues are reader-internal (computed gold-free). HONEST
  BANDS + N=34 flagged = a PROBE (illustrative per-type n; if promising, scale the oracle labels).

Compute architecture: sequential-CPU, justified. Pure-python glass-box pass over 34 gold sentences +
a UD-EWT test subset for tau (persisted averaged-perceptron POS + hashed arc-parser + hashed labeler;
numpy only). Wall time seconds. No GPU batching candidate (34 items, no matmul-heavy inner loop).
Storage: no_storage/no_composition (measurement cell; writes metrics.json atomic tmp+replace).

LOCAL-ONLY foreground; NO queue, NO push, NO remote-persist, NO git add. Determinism: OMP/MKL/
OPENBLAS=1, fixed percentile, sorted(set). ASCII-only, no em-dashes.
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import argparse
import json
import sys
import time
import traceback
from collections import defaultdict
from datetime import datetime, timezone

import numpy as np

ANCHOR_NAME = "mcguffey_whoaffected_reader_accuracy_escalation_calibration_probe_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

# reuse the validated reader/overlay wiring (read-only import)
from experiments.exp_read_discourse_docorder_stateofmind_whoaffected_ud_ewt_v1 import (  # noqa: E402
    POS_PATH, ARC_PATH, LABELER_PATH, UD_TEST,
    reader_pass, base_pick, salient_pick, observe_sentence,
    load_ud_docs,
)
from hdlab.pos_tagger import PosTagger  # noqa: E402
from hdlab.arc_parser import ArcParser  # noqa: E402
from hdlab.arc_labeler import ArcLabeler  # noqa: E402
from hdlab.state_of_mind import WorkingOverlay, PRONOUN_SCOPE  # noqa: E402
from hdlab.candidate_generator import ud_tokenize  # noqa: E402

GOLD_PATH = os.path.join(REPO_ROOT, "data", "mcguffey_whoaffected_oracle_gold_v1", "gold.json")

# who-is-affected target: which affectedness types have a REAL affected entity vs NONE (nobody).
AFFECTED_TYPES = {"patient", "effected", "transfer"}          # gold['affected'] span IS the answer
NONE_TYPES = {"target_not_affected", "none", "negated"}       # correct answer = NONE (nobody affected)

# span-head stopwords (dropped when reducing a gold 'affected' span to its content head tokens)
SPAN_STOP = {"the", "a", "an", "and", ",", "his", "her", "its", "their", "of", "to"}

# glass-box negation markers (for the OPTIONAL negation-gate variant + escalation-conflict signal)
NEG_MARKERS = {"not", "n't", "never", "no", "none", "cannot", "nor"}

# FIXED perception/search/contact verb lexicon (verb-affectedness TYPE fact; independent of the gold
# labels -> non-circular). Used ONLY for the labeled DIAGNOSTIC headroom arm (the proposed but
# not-yet-built verb-affectedness gate); NOT part of the raw-reader baseline.
PERCEPTION_VERBS = {"see", "saw", "seen", "look", "looked", "watch", "watched", "hear", "heard",
                    "feel", "felt", "smell", "smelt", "smelled", "find", "found", "seek", "sought",
                    "search", "searched", "behold", "spy", "spied", "gaze", "gazed", "view", "viewed"}


def span_head_tokens(affected):
    """Reduce a gold 'affected' span string to its lowercased content head tokens (drop determiners)."""
    if affected is None:
        return set()
    toks = ud_tokenize(affected)
    return {t.lower() for t in toks if t.lower() not in SPAN_STOP and t.isalpha()}


def find_verb_index(tokens, pos, gold_verb):
    """1-based index of the gold verb token in the reader's tokenization. Prefer a VERB-tagged match on
    the verb's HEAD word (first word of a multiword verb like 'get up'/'look at'); fall back to any
    surface match (records a POS-miss). Returns (vidx or None, pos_missed_bool)."""
    head_word = gold_verb.split()[0].lower()
    verb_hits = [i for i in range(1, len(tokens) + 1)
                 if tokens[i - 1].lower() == head_word and pos[i - 1] == "VERB"]
    if verb_hits:
        return verb_hits[0], False
    surf_hits = [i for i in range(1, len(tokens) + 1) if tokens[i - 1].lower() == head_word]
    if surf_hits:
        return surf_hits[0], True     # token present but NOT tagged VERB -> POS miss
    return None, True


def sentence_is_negated(tokens, vidx):
    """Glass-box clause negation: a negation marker present in the (short, single-clause McGuffey)
    sentence flags the predicate as negated. Conservative + transparent for the probe."""
    lows = {t.lower().strip(".,'\"!?;:") for t in tokens}
    return bool(lows & NEG_MARKERS)


def within_sentence_overlay(tokens, pos):
    """Fresh WorkingOverlay observing THIS sentence's own predicted mentions (the gold items are
    ISOLATED sentences, not a running story, so the state-of-mind contradiction cue is built from the
    sentence's own entities). Faithful to observe_sentence; no cross-gold-sentence leakage."""
    overlay = WorkingOverlay()
    observe_sentence(overlay, tokens, pos)
    return overlay


def compute_tau(tagger, parser, labeler, mode):
    """tau_abstain = 16th percentile of predicted-patient base-pick arc-parser margins on a UD-EWT test
    subset (the memory's ~16% abstain operating point), applied UNCHANGED to McGuffey = non-circular."""
    ud_docs = load_ud_docs(UD_TEST)
    ud_docs = [d for d in ud_docs if len(d) >= 1]
    ud_docs = ud_docs[:(15 if mode == "smoke" else 80)]
    margins = []
    for doc in ud_docs:
        for sent in doc:
            rp = reader_pass(sent, tagger, parser, labeler)
            for _v, pool in rp["pools"].items():
                bp = base_pick(pool)
                if bp is not None:
                    margins.append(bp["margin"])
    tau = float(np.percentile(margins, 16)) if margins else 0.0
    return tau, len(margins), len(ud_docs)


def run_probe(mode):
    t0 = time.perf_counter()
    out_dir = os.path.join(REPO_ROOT, "data",
                           f"exp_{ANCHOR_NAME}" + ("_smoke" if mode == "smoke" else ""))
    os.makedirs(out_dir, exist_ok=True)
    print(f"[{ANCHOR_NAME}:{mode}] START", flush=True)

    with open(GOLD_PATH, encoding="utf-8") as f:
        gold_doc = json.load(f)
    gold = gold_doc["gold"]
    if mode == "smoke":
        gold = gold[:10]
    print(f"[{ANCHOR_NAME}:{mode}] gold loaded: {len(gold)} sentences", flush=True)

    tagger = PosTagger.load(POS_PATH)
    parser = ArcParser.load(ARC_PATH)
    labeler = ArcLabeler.load(LABELER_PATH)
    print(f"[{ANCHOR_NAME}:{mode}] front-end loaded", flush=True)

    tau, n_ud_margins, n_ud_docs = compute_tau(tagger, parser, labeler, mode)
    print(f"[{ANCHOR_NAME}:{mode}] tau_abstain(UD 16pct)={tau:.4f} n_ud_margins={n_ud_margins}", flush=True)

    inst = []  # per gold sentence
    for g in gold:
        text, gverb, gaff, gtype = g["text"], g["verb"], g["affected"], g["type"]
        gold_none = gtype in NONE_TYPES
        heads_gold = span_head_tokens(gaff)

        tokens = ud_tokenize(text)
        rp = reader_pass({"tokens": tokens}, tagger, parser, labeler)
        pos = rp["pos"]
        vidx, pos_missed = find_verb_index(tokens, pos, gverb)

        pool = rp["pools"].get(vidx, []) if vidx is not None else []
        bp = base_pick(pool)
        pred_surf = bp["surf"] if bp is not None else None
        pred_none = bp is None
        margin = bp["margin"] if bp is not None else None

        # contradiction flag: base-vs-salient disagreement (state-of-mind vs parse), within-sentence overlay
        overlay = within_sentence_overlay(tokens, pos)
        sp = salient_pick(pool, overlay)
        contradiction = bool(sp is not None and bp is not None and sp["aidx"] != bp["aidx"])

        negated = sentence_is_negated(tokens, vidx)
        is_perception = gverb.split()[0].lower() in PERCEPTION_VERBS

        # --- RAW correctness (who-is-affected, affectedness-type-aware) ---
        if gold_none:
            raw_correct = pred_none                      # correct iff reader says nobody affected
        else:
            raw_correct = bool(pred_surf is not None and pred_surf in heads_gold)

        # --- +negation-gate variant: a negated predicate -> force NONE ---
        pred_none_ng = pred_none or negated
        if gold_none:
            ng_correct = pred_none_ng
        else:
            ng_correct = bool((not negated) and pred_surf is not None and pred_surf in heads_gold)

        # --- +perception-gate DIAGNOSTIC (labeled illustrative; NOT the baseline) ---
        pred_none_pg = pred_none_ng or is_perception
        if gold_none:
            pg_correct = pred_none_pg
        else:
            pg_correct = bool((not negated) and (not is_perception)
                              and pred_surf is not None and pred_surf in heads_gold)

        # --- escalation cues (reader-internal, gold-free) ---
        margin_low = bool(margin is not None and margin < tau)
        cue_margin = margin_low
        cue_flag = contradiction
        cue_bifurcated = bool(cue_margin or cue_flag)

        # error class for the calibration decomposition
        if raw_correct:
            err_class = "correct"
        elif gold_none and not pred_none:
            err_class = "type_error"          # confidently extracted a target where answer is NONE
        elif (not gold_none) and pred_none:
            err_class = "extraction_miss"     # no candidate for a real patient
        else:
            err_class = "wrong_entity"        # extracted the wrong entity

        inst.append({
            "id": g["id"], "text": text, "verb": gverb, "type": gtype,
            "gold_affected": gaff, "gold_none": gold_none,
            "pred_surf": pred_surf, "pred_none": pred_none, "margin": margin,
            "n_cands": len(pool), "pos_missed": pos_missed, "vidx_found": vidx is not None,
            "negated": negated, "is_perception": is_perception,
            "raw_correct": raw_correct, "ng_correct": ng_correct, "pg_correct": pg_correct,
            "cue_margin": cue_margin, "cue_flag": cue_flag, "cue_bifurcated": cue_bifurcated,
            "err_class": err_class,
        })

    n = len(inst)

    # ---------------- accuracy: overall + per type ----------------
    def acc(items, key):
        c = sum(1 for i in items if i[key])
        return (round(c / len(items), 4) if items else None), len(items), c

    overall_raw = acc(inst, "raw_correct")
    overall_ng = acc(inst, "ng_correct")
    overall_pg = acc(inst, "pg_correct")

    per_type = {}
    types_present = sorted({i["type"] for i in inst})
    for ty in types_present:
        items = [i for i in inst if i["type"] == ty]
        a_raw, nt, c_raw = acc(items, "raw_correct")
        a_ng, _, c_ng = acc(items, "ng_correct")
        per_type[ty] = {"n": nt, "raw_acc": a_raw, "raw_correct": c_raw,
                        "ng_acc": a_ng, "ng_correct": c_ng}

    # ---------------- calibration: cue as a WRONG-answer detector (on RAW) ----------------
    def calib(cue_key):
        tp = sum(1 for i in inst if i[cue_key] and not i["raw_correct"])   # cue fires AND wrong
        fp = sum(1 for i in inst if i[cue_key] and i["raw_correct"])       # cue fires AND correct
        fn = sum(1 for i in inst if (not i[cue_key]) and not i["raw_correct"])  # miss a wrong
        fires = tp + fp
        n_wrong = tp + fn
        precision = round(tp / fires, 4) if fires else None
        recall = round(tp / n_wrong, 4) if n_wrong else None
        return {"n_fires": fires, "tp": tp, "fp": fp, "fn": fn,
                "precision": precision, "recall": recall}

    cal_margin = calib("cue_margin")
    cal_flag = calib("cue_flag")
    cal_bifurcated = calib("cue_bifurcated")

    n_wrong = sum(1 for i in inst if not i["raw_correct"])
    # decomposition of wrong answers by class + whether the bifurcated cue caught them
    err_by_class = defaultdict(lambda: {"n": 0, "caught_bifurcated": 0})
    for i in inst:
        if not i["raw_correct"]:
            eb = err_by_class[i["err_class"]]
            eb["n"] += 1
            eb["caught_bifurcated"] += int(i["cue_bifurcated"])
    err_by_class = {k: dict(v) for k, v in err_by_class.items()}

    bifur_beats_either = bool(
        cal_bifurcated["recall"] is not None
        and cal_margin["recall"] is not None and cal_flag["recall"] is not None
        and cal_bifurcated["recall"] > max(cal_margin["recall"], cal_flag["recall"]) + 1e-9)
    bifur_ge_either = bool(
        cal_bifurcated["recall"] is not None
        and cal_bifurcated["recall"] >= max(cal_margin["recall"] or 0.0, cal_flag["recall"] or 0.0) - 1e-9)

    # ---------------- escalation rate + would-lift-to-100 ----------------
    n_escalate = sum(1 for i in inst if i["cue_bifurcated"])
    escalation_rate = round(n_escalate / n, 4) if n else None
    non_esc = [i for i in inst if not i["cue_bifurcated"]]
    non_esc_correct = sum(1 for i in non_esc if i["raw_correct"])
    post_esc_acc_noncovered = round(non_esc_correct / len(non_esc), 4) if non_esc else None
    n_missed_wrong = sum(1 for i in non_esc if not i["raw_correct"])  # wrong but NOT escalated
    would_lift_to_100 = bool(n_missed_wrong == 0)

    # ---------------- verdict ----------------
    raw_acc_val = overall_raw[0] or 0.0
    bifur_recall = cal_bifurcated["recall"] or 0.0
    # chance for who-affected: gold is ~half none-types; a naive all-none or all-extract baseline ~0.5.
    usable_reader = raw_acc_val >= 0.55
    calibrated = (bifur_recall >= 0.60) and (bifur_ge_either)
    if usable_reader and calibrated:
        verdict = "PROBE_PROMISING"
    elif (not usable_reader) and (not calibrated):
        verdict = "PROBE_BOTH_FAIL"
    elif usable_reader and not calibrated:
        verdict = "PROBE_READER_OK_CALIBRATION_FAILS"
    else:
        verdict = "PROBE_READER_WEAK_CALIBRATION_OK"

    elapsed = round(time.perf_counter() - t0, 2)
    verdict_msg = (
        f"[{verdict}] N={n} (PROBE; illustrative per-type n) "
        f"| reader who-affected RAW acc={overall_raw[0]} ({overall_raw[2]}/{overall_raw[1]}) "
        f"+neg_gate={overall_ng[0]} +percep_gate_DIAG={overall_pg[0]} "
        f"| per_type_raw=" + ",".join(f"{ty}:{per_type[ty]['raw_acc']}({per_type[ty]['raw_correct']}/{per_type[ty]['n']})"
                                      for ty in types_present)
        + f" | n_wrong={n_wrong} "
        f"| CALIB wrong-detector recall/prec: margin={cal_margin['recall']}/{cal_margin['precision']} "
        f"flag={cal_flag['recall']}/{cal_flag['precision']} "
        f"bifurcated={cal_bifurcated['recall']}/{cal_bifurcated['precision']} "
        f"(bifur_beats_either={bifur_beats_either} bifur_ge_either={bifur_ge_either}) "
        f"| escalation_rate={escalation_rate} post_esc_acc_noncovered={post_esc_acc_noncovered} "
        f"n_missed_wrong={n_missed_wrong} would_lift_to_100={would_lift_to_100} "
        f"| tau_abstain={round(tau,4)}(UD16pct) "
        f"| err_by_class=" + json.dumps(err_by_class, ensure_ascii=True)
    )

    metrics = {
        "verdict": verdict, "verdict_msg": verdict_msg, "summary": verdict,
        "elapsed_s": elapsed, "run_mode": mode, "anchor_name": ANCHOR_NAME,
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "N": n, "is_probe_flag": True,
        "note": ("FIRST-REAL-READING PROBE, N=34 single-annotator oracle gold. who-is-affected target is "
                 "affectedness-type-aware: NONE for target_not_affected/none/negated. Escalation cues are "
                 "reader-internal (arc-parser margin < UD-16pct tau OR base-vs-salient contradiction), gold-"
                 "free. LEAK-CLEAN. Per-type n small = illustrative, not powered."),
        "reader_accuracy": {
            "overall_raw_acc": overall_raw[0], "overall_raw_correct": overall_raw[2], "overall_n": overall_raw[1],
            "overall_with_negation_gate_acc": overall_ng[0],
            "overall_with_perception_gate_DIAGNOSTIC_acc": overall_pg[0],
            "per_type": per_type,
        },
        "calibration": {
            "tau_abstain_ud16pct": round(tau, 4), "n_ud_margins": n_ud_margins, "n_ud_docs": n_ud_docs,
            "n_wrong": n_wrong,
            "margin_only": cal_margin, "flag_only": cal_flag, "bifurcated_or": cal_bifurcated,
            "bifurcated_beats_either_recall": bifur_beats_either,
            "bifurcated_ge_either_recall": bifur_ge_either,
            "error_by_class_and_bifurcated_catch": err_by_class,
        },
        "escalation": {
            "escalation_rate": escalation_rate, "n_escalate": n_escalate,
            "post_escalation_accuracy_on_noncovered": post_esc_acc_noncovered,
            "n_missed_wrong": n_missed_wrong, "would_lift_to_100_on_covered": would_lift_to_100,
        },
        "per_instance": inst,
        "gold_meta": gold_doc.get("_meta", {}),
        "design_gate": {
            "real_baseline": "reader RAW who-affected (base_pick over arc-labeled patient pool)",
            "can_fail": "acc near-chance (<0.55) OR triggers uncorrelated with errors (calibration fails)",
            "difficulty_on": "real archaic McGuffey text + perception (target_not_affected) + negation types",
            "leak_clean": "reader never sees gold; tau UD-calibrated not McGuffey; cues reader-internal",
        },
    }
    tmp = os.path.join(out_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, os.path.join(out_dir, "metrics.json"))
    print(f"[{ANCHOR_NAME}:{mode}] DONE {verdict} elapsed={elapsed}s", flush=True)
    print(f"[{ANCHOR_NAME}:{mode}] {verdict_msg}", flush=True)
    return metrics


def self_test():
    print("[self_test] start", flush=True)
    # span-head reduction
    assert span_head_tokens("the eggs") == {"eggs"}
    assert span_head_tokens("the pan and the eggs") == {"pan", "eggs"}
    assert span_head_tokens("the big man") == {"big", "man"}
    assert span_head_tokens(None) == set()
    # real front-end constructs + runs on real McGuffey text (real code path, not synthetic)
    tagger = PosTagger.load(POS_PATH)
    parser = ArcParser.load(ARC_PATH)
    labeler = ArcLabeler.load(LABELER_PATH)
    toks = ud_tokenize("Ned has fed the hen.")
    rp = reader_pass({"tokens": toks}, tagger, parser, labeler)
    assert "pos" in rp and "pools" in rp
    vidx, missed = find_verb_index(toks, rp["pos"], "fed")
    assert vidx is not None, "must locate the gold verb 'fed'"
    # negation detector fires on the one negated gold sentence, not on a plain one
    assert sentence_is_negated(ud_tokenize("Then the cat can not catch it."), 1)
    assert not sentence_is_negated(ud_tokenize("Ann can catch Rab."), 1)
    # cannot -> 'can not' handled by ud_tokenize; 'not' present
    assert "not" in {t.lower() for t in ud_tokenize("Then the cat can not catch it.")}
    # perception lexicon (verb-affectedness type fact, gold-independent)
    assert "see" in PERCEPTION_VERBS and "catch" not in PERCEPTION_VERBS
    # gold file present + schema
    with open(GOLD_PATH, encoding="utf-8") as f:
        gd = json.load(f)
    assert len(gd["gold"]) == 34
    for g in gd["gold"]:
        assert g["type"] in (AFFECTED_TYPES | NONE_TYPES), "unexpected gold type: %r" % g["type"]
    print("[self_test] span-heads OK; front-end real-code-path OK; negation OK; gold schema OK", flush=True)
    print("[self_test] PASS", flush=True)
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--full", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        self_test(); return
    if args.smoke:
        run_probe("smoke"); return
    if args.full:
        run_probe("full"); return
    self_test()


if __name__ == "__main__":
    out_dir_crash = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}")
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        os.makedirs(out_dir_crash, exist_ok=True)
        with open(os.path.join(out_dir_crash, "metrics.json"), "w", encoding="utf-8") as f:
            json.dump({"verdict": "CELL_CRASHED", "verdict_msg": f"{type(e).__name__}: {str(e)[:400]}",
                       "traceback": traceback.format_exc()[:4000]}, f, indent=2)
        raise
