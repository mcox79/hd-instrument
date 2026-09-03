"""exp_register_predicate_controls_v1 -- rigor battery for the register-robust predicate detector.

Reuses exp_register_predicate_detector_v1 (D) machinery. Parse-free (fast, inline). Answers, per the bar + the
"don't submit the first thing that clears" discipline:
  1. ABLATION -- does the multi-cue COMBINATION beat the best SINGLE cue? (the brain-faithful claim; if margin-only
     ties the full combiner, the combination is not earning its keep). Leave-one-cue-out too.
  2. GATE COVERAGE -- what fraction of ALL dropped verbs are even candidates (WordNet-verb-reading + non-AUX)? This
     BOUNDS achievable event recall (the gate is a coverage ceiling; report it honestly).
  3. EVENT-RECALL FRAMING -- translate "recovery of dropped verbs" into the live detector's event-recall lift over the
     current floor, per register (the brief's deployment metric).
  4. RESIDUAL DIAGNOSIS -- the dropped verbs NOT recovered at FP<=0.5: decompose by cause (no subject / no frame /
     low margin / imperative-no-subject) and show examples -> the named ceiling.

Glass-box, CPU, NO LLM/spaCy. ASCII. own dir.
# KB_REFERENT: data/frontend_assets/pos_tagger_ud_ewt_upos.json
# KB_REFERENT: data/corpora/ud_english_ewt/en_ewt-ud-test.conllu
# KB_REFERENT: data/predict_revise_recall_v1/_population_litbank.json
# KB_REFERENT: data/benchmark_trap_check/qasrl/qasrl-v2/orig/dev.jsonl.gz
"""
from __future__ import annotations
import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
import argparse, json, sys, time
from collections import Counter
from datetime import datetime, timezone
import numpy as np

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in (_REPO, os.path.join(_REPO, "experiments")):
    if p not in sys.path:
        sys.path.insert(0, p)

import experiments.exp_register_predicate_detector_v1 as D
import experiments.exp_verbrole_exemplar_which_arg_v1 as V1
import experiments.exp_whodidwhat_verb_id_recoverable_v1 as VID

OUT_DIR = os.path.join(_REPO, "data/exp_register_predicate_controls_v1")


def _slice(rows, cols):
    return [(s, i, [fv[c] for c in cols], y) for (s, i, fv, y) in rows]


def _fit_cols(train_rows, cols):
    return D._fit(_slice(train_rows, cols))


def _recovery_at(rows, nsent, proba, budget=0.5):
    r = D.evaluate(rows, nsent, proba)
    key = "best_fp_le_0p5" if budget == 0.5 else "best_fp_le_1"
    b = r[key] if r else None
    bt = r["bootstrap_delta_vs_twin"] if r else None
    return b, bt, r


def gate_coverage(sents_or_pop, is_pop, W, tags, cap=None):
    """Fraction of ALL dropped real verbs that PASS the candidate gate (WordNet verb-reading + non-AUX)."""
    tg = D.tagger()
    total_drop = 0; gated = 0
    if is_pop:
        pop = sents_or_pop[:cap] if cap else sents_or_pop
        for r in pop:
            toks = r["sent"].split(); vi = r["verb_idx"]
            if not toks or vi >= len(toks):
                continue
            pos = tg.tag(toks)
            if pos[vi] not in ("VERB", "AUX"):     # genuine open-class drop
                total_drop += 1
                if VID.has_verb_reading(toks[vi]):
                    gated += 1
    else:
        sents = sents_or_pop[:cap] if cap else sents_or_pop
        for toks, gold_verb in sents:
            pos = tg.tag(toks)
            for i in gold_verb:
                if pos[i] not in ("VERB", "AUX"):
                    total_drop += 1
                    if VID.has_verb_reading(toks[i]):
                        gated += 1
    return {"total_dropped_open_class": total_drop, "gated_candidates": gated,
            "gate_coverage": round(gated / max(1, total_drop), 4)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true", dest="self_test")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--full", action="store_true")
    args = ap.parse_args()
    t0 = time.time(); os.makedirs(OUT_DIR, exist_ok=True)
    tg = D.tagger(); W = tg._perc.weights; tags = tg.tags

    cap = 60 if args.self_test else (150 if args.smoke else (None if args.full else 800))
    qcap = 60 if args.self_test else (150 if args.smoke else (None if args.full else 1500))
    lbcap = 400 if (args.self_test or args.smoke) else (None if args.full else 2500)

    print("building rows (parse-free) ...", flush=True)
    ud_test = D.load_ud(D.UD_TEST, cap=cap)
    qasrl = D.load_qasrl(D.QASRL, cap=qcap)
    pop = V1.load_pop(D.LB)
    mod_rows, mod_ns = D.build_rows(ud_test, W, tags, None, None, False)
    q_rows, q_ns = D.build_rows(qasrl, W, tags, None, None, False)
    c19_rows, c19_ns = D.build_rows_19c(pop, W, tags, None, None, False, cap=lbcap)
    train_all = mod_rows + q_rows

    # ---- 1. ABLATION: full vs each single cue vs leave-one-out (recovery @ FP<=0.5) ----
    N = len(D.FEAT_NAMES)
    allcols = list(range(N))
    subsets = {"FULL": allcols}
    for j, nm in enumerate(D.FEAT_NAMES):
        subsets["only_" + nm] = [j]
        subsets["drop_" + nm] = [c for c in allcols if c != j]
    ablation = {}
    for name, cols in subsets.items():
        clf, mu, sd = _fit_cols(train_all, cols)
        # modern via CV on the subset
        mod_p = _cv_cols(mod_rows, cols)
        m_b, m_bt, _ = _recovery_at(_slice(mod_rows, cols) if False else mod_rows, mod_ns, mod_p, 0.5)
        # 19c transfer
        c_p = D._proba(clf, mu, sd, _slice(c19_rows, cols))
        c_b, c_bt, _ = _recovery_at(c19_rows, c19_ns, c_p, 0.5)
        ablation[name] = {
            "modern_rec@0.5FP": m_b["recovery"] if m_b else None, "modern_fp": m_b["false_verbs_per_sent"] if m_b else None,
            "modern_sep": (m_bt["ci"][0] > 0) if m_bt else None,
            "c19_rec@0.5FP": c_b["recovery"] if c_b else None, "c19_fp": c_b["false_verbs_per_sent"] if c_b else None,
            "c19_sep": (c_bt["ci"][0] > 0) if c_bt else None,
        }

    # ---- 2. GATE COVERAGE (per register) ----
    cov = {"modern_udtest": gate_coverage(ud_test, False, W, tags),
           "c19_litbank": gate_coverage(pop, True, W, tags, cap=lbcap)}

    # ---- 3. EVENT-RECALL FRAMING: floor -> +detector, per register (at FP<=0.5, FULL combiner) ----
    clf, mu, sd = _fit_cols(train_all, allcols)
    def event_recall(rows, nsent, cov_entry, proba):
        r = D.evaluate(rows, nsent, proba)
        b = r["best_fp_le_0p5"]
        # floor event recall on the OPEN-CLASS-verb population = (gold_verbs - dropped)/gold_verbs
        drop = cov_entry["total_dropped_open_class"]; gated = cov_entry["gated_candidates"]
        # recovered = recovery * gated (gate bounds it); express as fraction of dropped recovered end-to-end
        rec_frac_of_dropped = (b["recovery"] * gated / max(1, drop)) if b else 0.0
        return {"recovery_of_gated": b["recovery"] if b else None, "fp": b["false_verbs_per_sent"] if b else None,
                "end_to_end_frac_of_ALL_dropped_recovered": round(rec_frac_of_dropped, 4)}
    er = {"modern": event_recall(mod_rows, mod_ns, cov["modern_udtest"], _cv_cols(mod_rows, allcols)),
          "c19": event_recall(c19_rows, c19_ns, cov["c19_litbank"], D._proba(clf, mu, sd, c19_rows))}

    # ---- 4. RESIDUAL DIAGNOSIS: dropped 19c verbs NOT recovered at FP<=0.5 ----
    c_p = D._proba(clf, mu, sd, c19_rows)
    r19 = D.evaluate(c19_rows, c19_ns, c_p)
    th = r19["best_fp_le_0p5"]["th"] if r19 and r19["best_fp_le_0p5"] else 0.5
    resid = Counter(); examples = []
    pop_c = pop[:lbcap] if lbcap else pop
    # rebuild proba index aligned to c19_rows (positives only)
    pos_rows = [(j, r) for j, r in enumerate(c19_rows) if r[3] == 1]
    for j, r in pos_rows:
        if c_p[j] >= th:
            continue  # recovered
        sidx, i, fv, _ = r
        rec = pop_c[sidx]; toks = rec["sent"].split()
        margin, frame, subj, obj, morph, verbless, relpos = fv[:7]
        cause = ("no_subject" if subj == 0 else ("no_frame" if frame == 0 else ("low_margin" if margin < -20 else "other")))
        resid[cause] += 1
        if len(examples) < 8:
            examples.append({"tok": toks[i] if i < len(toks) else "?", "cause": cause,
                             "margin": round(margin, 1), "subj": subj, "frame": frame, "verbless": verbless})

    res = {"ablation_rec_at_0p5FP": ablation, "gate_coverage": cov, "event_recall_framing": er,
           "residual_unrecovered_19c@0.5FP": {"by_cause": dict(resid), "examples": examples, "threshold": round(float(th), 4)},
           "feat_names": D.FEAT_NAMES}
    with open(os.path.join(OUT_DIR, "metrics.json"), "w", encoding="ascii") as fh:
        json.dump({"anchor_name": "register_predicate_controls_v1", "results": res,
                   "elapsed_s": round(time.time() - t0, 1), "ts_iso": datetime.now(timezone.utc).isoformat()}, fh, indent=2)

    print("\n===== CONTROLS: register-robust predicate detector =====", flush=True)
    print("\n1. ABLATION (recovery @ FP<=0.5; does the COMBINATION beat single cues?)", flush=True)
    print("   %-22s %8s %8s %6s | %8s %8s %6s" % ("subset", "mod_rec", "mod_fp", "sep", "c19_rec", "c19_fp", "sep"), flush=True)
    for name in ["FULL"] + ["only_" + n for n in D.FEAT_NAMES]:
        a = ablation[name]
        print("   %-22s %8s %8s %6s | %8s %8s %6s" % (
            name, a["modern_rec@0.5FP"], a["modern_fp"], a["modern_sep"], a["c19_rec@0.5FP"], a["c19_fp"], a["c19_sep"]), flush=True)
    print("\n2. GATE COVERAGE (fraction of ALL dropped open-class verbs that are candidates):", flush=True)
    for k, v in cov.items():
        print("   %-16s dropped=%d gated=%d coverage=%.4f" % (k, v["total_dropped_open_class"], v["gated_candidates"], v["gate_coverage"]), flush=True)
    print("\n3. EVENT-RECALL FRAMING (end-to-end fraction of ALL dropped verbs recovered @ FP<=0.5):", flush=True)
    for k, v in er.items():
        print("   %-8s recovery_of_gated=%.4f  end_to_end_of_all_dropped=%.4f  fp=%.4f" % (
            k, v["recovery_of_gated"] or 0, v["end_to_end_frac_of_ALL_dropped_recovered"], v["fp"] or 0), flush=True)
    print("\n4. RESIDUAL (unrecovered 19c dropped verbs @ FP<=0.5) by cause:", dict(resid), flush=True)
    for e in examples:
        print("     ", e, flush=True)

    if args.self_test or args.smoke:
        assert ablation["FULL"]["c19_rec@0.5FP"] is not None
        print("\n[self-test] PASS", flush=True)
    print("\n[done] %.0fs" % (time.time() - t0), flush=True)


def _cv_cols(rows, cols):
    return D.cv_proba(_slice(rows, cols))


if __name__ == "__main__":
    main()
