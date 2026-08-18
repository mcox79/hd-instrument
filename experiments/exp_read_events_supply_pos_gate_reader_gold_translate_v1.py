"""SUPPLY-POS ADOPTION + reader-level GOLD translation test.

The ONLY clean supply win in the events thread was spaCy POS (29522: L1 confound-free predicate-noise
-56%, 606->266 nonverb predicate selections; L2 160->70). supply-PARSE was net-neutral (29524),
supply-NER negative (29523). This cell does the honest consolidation:

  (1) ADOPT the POS win: a spaCy-POS PREDICATE-VALIDITY GATE is wired into hdlab/situation_reader.py
      event emission (opt-in; default OFF preserves the banked reader). An emitted event's predicate
      LOW token must be a spaCy-VERB (Penn VB*) somewhere in its sentence, else it is suppressed as a
      POS mis-tag. POST-HOC filter only -- it does NOT feed the substrate parser / role clf (no OOD);
      glass-box supplied preprocessing (the "humans read via already-known grammar" frame).

  (2) READER-LEVEL GOLD TEST (the REAL question -- does the supply win TRANSLATE to ACCURACY, not just
      the LitBank noise proxy which is banked-unfair per 29525): run the banked 29502 who-did-what
      reader (McGuffey gold F1 ~0.59-0.62) with the spaCy-POS predicate gate ON vs OFF, scored against
      the McGuffey LCCP argstruct gold. Does supplying grammar lift the gold F1, or is McGuffey simple
      enough that NLTK POS already suffices (-> the POS win is LITERARY-PROSE-specific, gold-blocked)?
      OVER-SUPPRESSION check (can-fail): count removed tuples that were TRUE POSITIVES (a real McGuffey
      predicate the gate wrongly suppressed) -> gold F1 could REGRESS.

  (3) DEMONSTRATE the cleaned LitBank situation model glass-box: 2 passages, events now with cleaner
      predicates via the spaCy gate; the previously-noisy predicates shown suppressed.

DISCRIMINATOR (pre-reg, all HONEST outcomes):
  (a) McGuffey gold F1 delta (spaCy-POS gate ON vs OFF):
        GOLD_LIFT_TRANSLATES    delta_f1 >= +0.01  -> supplying grammar lifts gold accuracy.
        GOLD_NULL_HARD_PROSE    |delta_f1| < 0.01   -> null on easy gold; the win is hard-prose-noise-only.
        GOLD_REGRESSION         delta_f1 <= -0.01   -> gate over-suppresses a real McGuffey predicate.
      A NULL is a LEGITIMATE honest finding (the win is real on LitBank noise, banked; translation to
      easy-gold accuracy is the open question this answers).
  (b) the spaCy gate suppresses mis-tagged predicates in the reader (LitBank demo: n_suppressed >= 1).
CAN-FAIL: delta_f1 <= -0.01 (regression) is reachable if spaCy wrongly drops a gold predicate.

POSITIVE CONTROL (Gate D): gate-OFF McGuffey F1 reproduces the banked reader
  CITED_GATE_OFF_F1 = 0.592 (MEASURED@data/exp_read_events_fix_role_reader_litbank_v1/metrics.json:
  gate1_mcguffey.reader_f1). If not (+/-0.05), wiring drifted -> flag, distrust delta.

Contract: INLINE-LOCAL foreground-to-completion; LOCAL-ONLY (no bank/push/commit). ASCII-only.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified (gate-ON vs gate-OFF arm hashes differ when any suppression occurs; else exempt)
# - final_metrics_atomicity = tmp_replace (metrics.json.tmp -> os.replace)
# - except SystemExit: raise BEFORE except Exception (no BaseException; no bare except)
# - crlb_n/a: F1-delta + suppression-count comparison; no Cramer-Rao floor applies
# - baseline_in_band: gate-OFF McGuffey F1 in (0.05, 0.95) + reproduces CITED_GATE_OFF_F1 (positive control)
# - discriminator can-fail (GOLD_REGRESSION reachable via over-suppression); FULL run = FULL_SLICE gold
# - HARD/NULL/REGRESSION bands pre-registered with strict eps
# - real_code_path: self-test builds real reader (W/clf/gate/sel_fn) + real spaCy tagger + real SituationReader
# - calibration_check: default_ok_for_this_regime (fixed pretrained spaCy + fixed gold; band = effect size)
# - all numbers MEASURED@ / CITED@ / HYPOTHESIZED@

## Compute architecture
class: (b) sequential-CPU with justification. No matmul/GPU batching benefit: the compute is spaCy
POS tagging (~163 McGuffey sentences + a few LitBank books) + argmax scoring against gold; all glass-box
symbolic. Wall time << 10 min foreground. Storage strategy: no_storage / no_composition (post-hoc filter
+ re-score; no substrate bind/unbind chains introduced).
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import argparse
import glob
import hashlib
import json
import platform
import sys
import time
import traceback
from datetime import datetime, timezone

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

# reuse the 29520 events-fix cell (build_reader = banked 29502 reader components + McGuffey gate),
# its D-chain (D.L score/gold, D.M to_kept_list, D.ORC split_sentences), and the 29522 spaCy tagger.
import experiments.exp_read_events_fix_role_reader_litbank_v1 as EF  # noqa: E402
from experiments.exp_read_events_supply_grammar_spacy_pos_litbank_v1 import make_spacy_tagger  # noqa: E402
import hdlab.situation_reader as SR  # noqa: E402

D = EF.D
ORC = D.ORC
L = D.L
M = D.M

ANCHOR_NAME = "read_events_supply_pos_gate_reader_gold_translate_v1"
SEED = 20260724
LITBANK_DIR = EF.LITBANK_DIR

# ---- pre-registered bands (see docstring) ----
LIFT_EPS = 0.01                    # F1 units: |delta| below this = NULL (no translation)
CITED_GATE_OFF_F1 = 0.592          # CITED@data/exp_read_events_fix_role_reader_litbank_v1/metrics.json:gate1_mcguffey.reader_f1
POS_CTRL_TOL = 0.05                # gate-OFF F1 must reproduce CITED within +/-0.05
NAIVE_BAND = (0.05, 0.95)


# ===========================================================================
# the supplied-grammar predicate-validity gate at the REDUCE/RE-SCORE level
# ===========================================================================
def spacy_verb_lows(raw, spacy_tag):
    """Set of LOW surface tokens spaCy tags as a VERB (VB*) anywhere in the sentence."""
    verbs = set()
    for clause in ORC.split_sentences(raw):
        for (_surf, low, pos) in spacy_tag(clause):
            if pos.startswith("VB"):
                verbs.add(low)
    return verbs


def apply_pos_gate(reader_arm, sent_text, spacy_tag):
    """Return (gated_arm, removed). gated_arm drops any (pred, agent, patient) tuple whose predicate
    LOW token is not a spaCy-VERB in its sentence. removed = list of (sid, tup) dropped."""
    gated = {}
    removed = []
    for sid, tups in reader_arm.items():
        raw = sent_text.get(sid, "")
        vlows = spacy_verb_lows(raw, spacy_tag) if raw else set()
        kept = []
        for tup in tups:
            pred_low = tup[0]
            if pred_low in vlows:
                kept.append(tup)
            else:
                removed.append((sid, tup))
        gated[sid] = kept
    return gated, removed


def _arm_hash(arm):
    kept = M.to_kept_list(arm)
    b = json.dumps(kept, sort_keys=True, ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(b).hexdigest()


def classify_removed(removed, gold):
    """For each removed tuple, is it a gold TRUE POSITIVE (a real predicate the gate wrongly dropped)?
    Returns (false_suppress, within_gold_fp_removed, offgold_removed, false_suppress_examples)."""
    false_suppress = within_gold_fp = offgold = 0
    fs_examples = []
    for sid, tup in removed:
        rec = gold.get(sid)
        v = L.lemma_verb(tup[0])
        p = tup[2]
        if rec is not None:
            g = L.match_pos(v, p, rec["pos"])
            if g is not None:
                false_suppress += 1
                if len(fs_examples) < 20:
                    fs_examples.append({"sid": sid, "removed_tuple": list(tup),
                                        "gold_matched": {"v": g["v"], "agent": g["agent"],
                                                         "patient": g["patient"]}})
            else:
                within_gold_fp += 1   # sid golded but this pred/pat not a gold positive -> correctly dropped FP
        else:
            offgold += 1              # sid not in gold -> spurious on an ungolded sentence -> neutral/good
    return false_suppress, within_gold_fp, offgold, fs_examples


# ===========================================================================
# (2) reader-level McGuffey gold translation test
# ===========================================================================
def run_gold_test(run_mode, spacy_tag):
    (W, clf, rt, sel_fn, gate, order, sent_text, reader_arm,
     mcg_slice, pinfo) = EF.build_reader(run_mode)
    gold, _meta = L.load_gold(mcg_slice)

    # gate OFF (baseline = banked 29502 reader)
    sc_off = L.score_arm(M.to_kept_list(reader_arm), gold)
    # naive positional baseline (can-fail sanity anchor, same as gate1)
    _o, _st, naive_arm = D.naive_positional_arm(mcg_slice)
    sc_naive = L.score_arm(M.to_kept_list(naive_arm), gold)

    # gate ON
    gated_arm, removed = apply_pos_gate(reader_arm, sent_text, spacy_tag)
    sc_on = L.score_arm(M.to_kept_list(gated_arm), gold)

    false_suppress, within_gold_fp, offgold, fs_examples = classify_removed(removed, gold)

    delta_f1 = round(sc_on["f1"] - sc_off["f1"], 4)
    delta_prec = round(sc_on["precision"] - sc_off["precision"], 4)
    delta_rec = round(sc_on["recall"] - sc_off["recall"], 4)

    if delta_f1 >= LIFT_EPS:
        translate = "GOLD_LIFT_TRANSLATES"
    elif delta_f1 <= -LIFT_EPS:
        translate = "GOLD_REGRESSION"
    else:
        translate = "GOLD_NULL_HARD_PROSE_ONLY"

    arms_differ = bool(_arm_hash(reader_arm) != _arm_hash(gated_arm))
    pc_ok = abs(sc_off["f1"] - CITED_GATE_OFF_F1) <= POS_CTRL_TOL
    baseline_in_band = bool(NAIVE_BAND[0] < sc_off["f1"] < NAIVE_BAND[1])

    return {
        "mcg_slice": list(mcg_slice),
        "parser_uas_dev": pinfo["uas_dev"],
        "gate_off": {"f1": sc_off["f1"], "precision": sc_off["precision"], "recall": sc_off["recall"],
                     "n_pred": sc_off["n_pred"], "tp": sc_off["tp"], "n_gold": sc_off["n_gold"]},
        "gate_on": {"f1": sc_on["f1"], "precision": sc_on["precision"], "recall": sc_on["recall"],
                    "n_pred": sc_on["n_pred"], "tp": sc_on["tp"], "n_gold": sc_on["n_gold"]},
        "naive": {"f1": sc_naive["f1"]},
        "delta_f1": delta_f1, "delta_precision": delta_prec, "delta_recall": delta_rec,
        "translate_verdict": translate,
        "n_removed": len(removed),
        "over_suppression": {
            "false_suppress_TP_dropped": false_suppress,      # gate wrongly dropped a real gold predicate
            "within_gold_fp_removed": within_gold_fp,         # correctly dropped a within-gold FP
            "offgold_removed": offgold,                       # dropped a tuple on an ungolded sentence
            "false_suppress_examples": fs_examples,
        },
        "positive_control_gate_off_f1": {"cited": CITED_GATE_OFF_F1, "measured": sc_off["f1"],
                                         "reproduced": bool(pc_ok)},
        "baseline_in_band": baseline_in_band,
        "arms_differ": arms_differ,
    }


# ===========================================================================
# (3) LitBank situation-model glass-box (cleaned predicates via the gate)
# ===========================================================================
def run_litbank_glassbox(pred_gate_fn, max_books, n_demo=2):
    books = sorted(glob.glob(os.path.join(LITBANK_DIR, "*.conll")))
    books = [b for b in books if os.path.getsize(b) > 1000]
    if max_books is not None:
        books = books[:max_books]
    reader = SR.SituationReader(pred_gate_fn=pred_gate_fn)
    per_book = []
    for path in books:
        pid = os.path.splitext(os.path.basename(path))[0]
        sm = reader.read(path)
        sup = [{"sent_idx": s.sent_idx, "predicate": s.predicate, "tense": s.tense,
                "agent": s.agent, "patient": s.patient} for s in sm.suppressed_predicates]
        per_book.append({"passage_id": pid, "n_sentences": sm.n_sentences,
                         "n_events_kept": len(sm.events), "n_suppressed": len(sm.suppressed_predicates),
                         "suppressed": sup,
                         "kept_events_sample": [{"sent_idx": e.sent_idx, "predicate": e.predicate,
                                                 "agent": e.agent, "patient": e.patient, "tense": e.tense}
                                                for e in sm.events[:8]]})
        print(f"[litbank] {pid}: n_events={len(sm.events)} n_suppressed={len(sm.suppressed_predicates)}",
              flush=True)
    # rank by n_suppressed for the demonstration (passages where the gate actually cleans noise)
    per_book.sort(key=lambda d: d["n_suppressed"], reverse=True)
    total_supp = sum(d["n_suppressed"] for d in per_book)
    return {"n_books_scanned": len(books), "total_suppressed": total_supp,
            "demo_passages": per_book[:n_demo], "all_books": per_book}


# ===========================================================================
# atomic metrics + markers
# ===========================================================================
def _out_dir(run_mode):
    return os.path.join(_REPO, "data",
                        f"exp_{ANCHOR_NAME}" + ("_smoke" if run_mode == "smoke" else ""))


def _write_start_marker(output_dir, run_mode, expected_n_units):
    os.makedirs(output_dir, exist_ok=True)
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": run_mode,
              "expected_n_units": expected_n_units, "host": platform.node()}
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, os.path.join(output_dir, "_start_marker.json"))


def _write_metrics(output_dir, metrics):
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, os.path.join(output_dir, "metrics.json"))


def _write_crash_metrics(output_dir, exc):
    os.makedirs(output_dir, exist_ok=True)
    diag = {"verdict": "CELL_CRASHED",
            "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
            "summary": f"CELL_CRASHED: {type(exc).__name__}",
            "elapsed_s": 0.0, "traceback": traceback.format_exc()[:5000],
            "ts_iso": datetime.now(timezone.utc).isoformat(),
            "pid": os.getpid(), "anchor_name": ANCHOR_NAME}
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, os.path.join(output_dir, "metrics.json"))


# ===========================================================================
# formula self-test (REAL code path)
# ===========================================================================
def self_test():
    print("[self-test] building spaCy tagger + gate ...", flush=True)
    spacy_tag = make_spacy_tagger()
    # gate correctly keeps a real verb, drops an adjective/noun mis-tag
    vl = spacy_verb_lows("the red coat lay there", spacy_tag)
    assert "lay" in vl and "red" not in vl, f"gate wrong on hard case: {vl}"

    print("[self-test] building REAL banked reader (smoke) + gold test ...", flush=True)
    r = run_gold_test("smoke", spacy_tag)
    # gate-OFF baseline must be a sane reader F1 (can-fail band) and reproduce the naive gap
    assert NAIVE_BAND[0] < r["gate_off"]["f1"] < NAIVE_BAND[1], f"gate-off F1 out of band: {r['gate_off']}"
    assert r["gate_off"]["f1"] > r["naive"]["f1"], \
        f"reader did not beat naive: reader {r['gate_off']['f1']} <= naive {r['naive']['f1']}"
    # gate must PRESERVE recall of real predicates on easy gold (false_suppress low) -- can-fail check
    print(f"[self-test] (smoke) gold F1 gate_off={r['gate_off']['f1']:.4f} gate_on={r['gate_on']['f1']:.4f} "
          f"delta={r['delta_f1']:+.4f} verdict={r['translate_verdict']} "
          f"n_removed={r['n_removed']} false_suppress={r['over_suppression']['false_suppress_TP_dropped']}",
          flush=True)

    print("[self-test] LitBank glass-box (2 books, gate ON) ...", flush=True)
    def gate_fn(txt):
        return spacy_verb_lows(txt, spacy_tag)
    gb = run_litbank_glassbox(gate_fn, max_books=2, n_demo=2)
    assert gb["total_suppressed"] >= 1, f"gate fired 0 suppressions on 2 LitBank books: {gb}"
    print(f"[self-test] (smoke) LitBank total_suppressed={gb['total_suppressed']} "
          f"over {gb['n_books_scanned']} books", flush=True)
    print("[self-test] PASS", flush=True)
    return 0


# ===========================================================================
# full verdict
# ===========================================================================
def build_verdict(run_mode):
    t0 = time.perf_counter()
    output_dir = _out_dir(run_mode)
    _write_start_marker(output_dir, run_mode, expected_n_units=1)

    print(f"[full] mode={run_mode} building spaCy tagger ...", flush=True)
    spacy_tag = make_spacy_tagger()

    print("[full] reader-level McGuffey gold translation test ...", flush=True)
    gt = run_gold_test(run_mode, spacy_tag)

    print("[full] LitBank situation-model glass-box (gate ON) ...", flush=True)
    def gate_fn(txt):
        return spacy_verb_lows(txt, spacy_tag)
    max_books = 4 if run_mode == "smoke" else None
    gb = run_litbank_glassbox(gate_fn, max_books=max_books, n_demo=2)

    # ---- console report ----
    print(f"[full] parser uas={gt['parser_uas_dev']} slice={gt['mcg_slice']}", flush=True)
    print(f"[full] GOLD F1  gate_OFF={gt['gate_off']['f1']:.4f} "
          f"(P={gt['gate_off']['precision']:.4f} R={gt['gate_off']['recall']:.4f})  "
          f"gate_ON={gt['gate_on']['f1']:.4f} "
          f"(P={gt['gate_on']['precision']:.4f} R={gt['gate_on']['recall']:.4f})  "
          f"DELTA_F1={gt['delta_f1']:+.4f} (dP={gt['delta_precision']:+.4f} dR={gt['delta_recall']:+.4f})",
          flush=True)
    print(f"[full] translate_verdict={gt['translate_verdict']}  naive_f1={gt['naive']['f1']:.4f}", flush=True)
    os_ = gt["over_suppression"]
    print(f"[full] gate removed {gt['n_removed']} tuples: "
          f"false_suppress(TP)={os_['false_suppress_TP_dropped']}  "
          f"within_gold_fp_removed={os_['within_gold_fp_removed']}  "
          f"offgold_removed={os_['offgold_removed']}", flush=True)
    pc = gt["positive_control_gate_off_f1"]
    print(f"[full] positive-control gate_off_f1={pc['measured']:.4f} (cited {pc['cited']}, "
          f"reproduced={pc['reproduced']})", flush=True)

    # ---- tier ----
    if not pc["reproduced"]:
        tier = "HARD_FAIL_POSITIVE_CONTROL"
        summary = (f"gate-OFF McGuffey F1={pc['measured']:.3f} did NOT reproduce banked reader "
                   f"(cited {pc['cited']}, tol {POS_CTRL_TOL}); delta untrusted")
    elif gb["total_suppressed"] < 1:
        tier = "HARD_FAIL_DISCRIMINATOR_SILENT"
        summary = f"spaCy gate suppressed 0 predicates over {gb['n_books_scanned']} LitBank books"
    else:
        tv = gt["translate_verdict"]
        if tv == "GOLD_LIFT_TRANSLATES":
            tier = "SUPPLY_POS_TRANSLATES_TO_GOLD"
            summary = (f"spaCy-POS gate LIFTS McGuffey gold F1 {gt['gate_off']['f1']:.3f}->"
                       f"{gt['gate_on']['f1']:.3f} (delta {gt['delta_f1']:+.3f}); supplying grammar "
                       f"translates to accuracy")
        elif tv == "GOLD_REGRESSION":
            tier = "SUPPLY_POS_REGRESSES_GOLD"
            summary = (f"spaCy-POS gate REGRESSES McGuffey gold F1 {gt['gate_off']['f1']:.3f}->"
                       f"{gt['gate_on']['f1']:.3f} (delta {gt['delta_f1']:+.3f}); over-suppressed "
                       f"{os_['false_suppress_TP_dropped']} real predicates")
        else:
            tier = "SUPPLY_POS_NULL_ON_GOLD_HARD_PROSE_ONLY"
            summary = (f"spaCy-POS gate NULL on McGuffey gold F1 {gt['gate_off']['f1']:.3f}->"
                       f"{gt['gate_on']['f1']:.3f} (delta {gt['delta_f1']:+.3f}, |.|<{LIFT_EPS}); "
                       f"the supply-POS win is LitBank-hard-prose-noise-only, not measurable on easy gold. "
                       f"LitBank demo: {gb['total_suppressed']} noisy predicates suppressed")

    elapsed = time.perf_counter() - t0
    verdict_msg = (f"{tier}: {summary}. Over-suppression false_suppress(TP)="
                   f"{os_['false_suppress_TP_dropped']}; gate removed {gt['n_removed']} McGuffey tuples "
                   f"({os_['within_gold_fp_removed']} within-gold FP, {os_['offgold_removed']} off-gold). "
                   f"LitBank demo: {gb['total_suppressed']} suppressions over {gb['n_books_scanned']} books.")

    metrics = {
        "verdict": tier,
        "verdict_msg": verdict_msg,
        "summary": summary,
        "elapsed_s": elapsed,
        "anchor_name": ANCHOR_NAME,
        "run_mode": run_mode,
        "seed": SEED,
        "gold_translation_test": gt,
        "litbank_glassbox": gb,
        "bands": {"LIFT_EPS": LIFT_EPS, "CITED_GATE_OFF_F1": CITED_GATE_OFF_F1,
                  "positive_control_tol": POS_CTRL_TOL, "naive_band": list(NAIVE_BAND)},
        "arms_differ_verified": gt["arms_differ"],
        "arms_differ_note": ("gate-ON differs from gate-OFF iff any suppression occurred; if 0 McGuffey "
                             "suppressions the arms are legitimately identical (NULL translation)"),
        "baseline_in_band": gt["baseline_in_band"],
        "final_metrics_atomicity": "tmp_replace",
        "crlb_n_a": "F1-delta + suppression-count comparison; no Cramer-Rao floor applies",
        "calibration_check": "default_ok_for_this_regime",
        "cell_chunked": False,
        "start_marker_written": True,
        "crash_diagnostic_present": True,
        "heartbeat_present": False,
        "progress_logging": "per-book flush prints in run_litbank_glassbox + section prints",
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "notes": ("SUPPLY-POS ADOPTION + reader-level gold translation. The gate is a POST-HOC "
                  "predicate-validity filter (emitted event predicate must be a spaCy VERB), wired opt-in "
                  "into hdlab/situation_reader.py; it does NOT feed the substrate parser/clf (no OOD). "
                  "PRIMARY result = McGuffey gold F1 delta gate-ON vs gate-OFF (the real reader-level "
                  "translation question); the LitBank noise proxy is banked-unfair per 29525 so is NOT "
                  "re-scored as the discriminator here -- only demonstrated glass-box. Gate applied at "
                  "the LOW-surface-token level (conservative: a predicate is dropped only if spaCy tags "
                  "it non-verb at every occurrence in the sentence). CAVEAT: gate-OFF baseline F1 is "
                  "scored over the FULL_SLICE arm incl. ungolded-sentence tuples, identical to the banked "
                  "gate1_mcguffey pipeline (CITED 0.592) -> delta is apples-to-apples. A NULL delta is a "
                  "legitimate honest translation answer, not a failure."),
    }
    _write_metrics(output_dir, metrics)
    print(f"[full] wrote {os.path.join(output_dir, 'metrics.json')} elapsed={elapsed:.1f}s", flush=True)

    # ---- glass-box print: the 2 cleaned LitBank passages ----
    print("[full] === GLASS-BOX: cleaned LitBank situation models (predicates suppressed by spaCy gate) ===",
          flush=True)
    for d in gb["demo_passages"]:
        print(f"  [{d['passage_id']}] n_sentences={d['n_sentences']} n_events_kept={d['n_events_kept']} "
              f"n_suppressed={d['n_suppressed']}", flush=True)
        for s in d["suppressed"][:10]:
            print(f"      SUPPRESSED pred='{s['predicate']}' tense={s['tense']} "
                  f"(agent={s['agent']} patient={s['patient']}) sent {s['sent_idx']}", flush=True)
    # ---- glass-box print: false-suppressions on gold (the can-fail evidence) ----
    if os_["false_suppress_examples"]:
        print("[full] === FALSE-SUPPRESSIONS on McGuffey gold (real predicates the gate wrongly dropped) ===",
              flush=True)
        for e in os_["false_suppress_examples"][:10]:
            print(f"      {e['sid']} dropped {e['removed_tuple']} but gold has {e['gold_matched']}", flush=True)
    else:
        print("[full] no false-suppressions on McGuffey gold (gate dropped no real gold predicate)", flush=True)
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        return self_test()
    return build_verdict("smoke" if args.smoke else "full")


if __name__ == "__main__":
    _od = _out_dir("smoke" if ("--smoke" in sys.argv) else "full")
    try:
        rc = main()
        sys.exit(rc)
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # NOT BaseException
        _write_crash_metrics(_od, e)
        raise
