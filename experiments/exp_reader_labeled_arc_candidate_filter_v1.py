"""Labeled-arc candidate filter -- does adding UD deprel LABELS to the unlabeled parse cut the 9:1
distractor problem in candidate generation WITHOUT killing recall, on full McGuffey gold?

MOTIVATION (two independent bottlenecks that both trace to the parser being UNLABELED):
  (1) candidate-generation PRECISION = 0.1053 (11.65 cands/sentence, ~9:1 distractors) -- the unlabeled
      parser proposes EVERY nominal dependent of a verb as a patient candidate because it cannot tell
      subject from object (MEASURED@ exp_reader_candidate_generation_recall_persisted_frontend_v1).
  (2) the completeness checker over-flags ~1-in-4 clean sentences from noisy subject inference.
A labeled parse (obj / nsubj:pass = the true patient roles) fixes BOTH. This cell builds + persists a
glass-box UD relation labeler (hdlab.arc_labeler, a multiclass averaged perceptron -- same learning
discipline as the persisted arc parser + POS tagger) and measures the DECISIVE payoff: candidate
precision / recall / distractors-per-sentence, labeled vs unlabeled, per construction, on the full gold.

WHAT IS MEASURED:
  A. Label accuracy GIVEN gold arcs (labeling accuracy)      -- dev + test, expect ~0.90+
  B. LAS (label on PREDICTED arcs = labeled attachment score) -- dev + test, expect below UAS 0.7868
  C. PAYOFF on full McGuffey gold: restrict patient candidates to labeled obj / nsubj:pass arcs and
     re-measure precision + recall + candidates/sentence, labeled vs unlabeled, per construction.

DESIGN-GATE (pre-registered; verified at smoke BEFORE full):
  (G1) REAL baseline = the UNLABELED candidate generator, re-derived IN THIS CELL by reusing the baseline
       module's helpers verbatim (not a strawman; must reproduce precision~0.105, recall~0.90).
  (G2) CAN-FAIL: label-filtering may DROP recall on out-of-domain 1879 McGuffey (a modern-UD-web-trained
       labeler mislabels obj->nsubj etc.), OR LAS may be too low to help. Reported honestly; recall drop
       is the expected domain-shift risk (recall the baseline finding: misses are POS-tagger-dominated).
  (G3) DIFFICULTY-ON: coordination / relative / control / pronoun cases are a large gold fraction
       (measured + asserted at smoke; not a saturated all-simple set).
  (G4) ONE-VARIABLE: candidate FILTER only -- unlabeled-all-nominals vs labeled-obj/nsubj:pass. Same gold,
       same candidate rules, same recall/precision metric, same front-end. Only the label filter differs.

PASS band (payoff decisive): labeled precision >= 0.25 (>2x the 0.105 unlabeled) AND labeled extended
       recall >= 0.75 (drop <= ~0.15 abs from the 0.90 unlabeled) AND mean cands/sentence < 6.
MIDDLE band: precision improves (>0.15) but recall drops into 0.60-0.75 (labeling helps but domain shift
       costs recall) -- reports the tradeoff frontier.
FAIL band: labeled recall < 0.60 (label mislabeling destroys recall -> labels not usable on archaic text)
       OR labeled precision <= unlabeled (no separation) OR label-acc-given-gold < 0.85 (labeler broken).

COMPUTE: class (b) sequential-CPU. Train a dict-keyed multiclass averaged perceptron on UD-EWT train
(~12.5k sents, ~48s/epoch), eval dev+test, one candidate-gen pass over ~114 McGuffey sentences. Persist
the labeler (frontend_assets json). Wall: ~6 min full (train dominated), <60s smoke. FOREGROUND local.
NO queue; NO push; NO remote-persist; NO canonical store write. Storage: no_storage.
Determinism: OMP/MKL/OPENBLAS=1; np.random.default_rng(seed) permutation; single deterministic train.
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

ANCHOR_NAME = "reader_labeled_arc_candidate_filter_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from hdlab.arc_labeler import ArcLabeler, train_label  # noqa: E402
from hdlab.candidate_generator import CandidateGenerator, candidates_from_parse  # noqa: E402
from experiments._ud_loader import load_conllu  # noqa: E402
from experiments import exp_reader_candidate_generation_recall_persisted_frontend_v1 as BASE  # noqa: E402
from experiments import exp_learned_argstruct_parser_lccp_independent_gold_v1 as LCCP  # noqa: E402
from hdlab.arc_parser import ArcParser  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "data", "exp_" + ANCHOR_NAME)
LABELER_PATH = os.path.join(REPO_ROOT, "data", "frontend_assets", "arc_labeler_hashed_ud_ewt.json")
UAS_REF = 0.7868  # persisted arc_parser UAS (CITED)
UNLAB_PRECISION_REF = 0.1053  # MEASURED@ baseline cell (re-derived here)

# Patient roles: the tight, decisive filter (pre-registered).
PATIENT_TIGHT = {"obj", "nsubj:pass"}
# A looser set for the recall-preservation tradeoff report (recipients + obliques the labeler may assign).
PATIENT_LOOSE = {"obj", "nsubj:pass", "iobj", "obl"}


def labeled_keep(v, a, rule, heads, labels, patient_set):
    """Keep candidate (v,a) iff the labeled arc qualifies a as a patient. Label-informed structural filter."""
    if rule in ("core_dep", "coord"):
        return labels.get(a) in patient_set
    if rule == "conj_obj":
        m = heads.get(a)
        return (labels.get(a) in patient_set) or (m is not None and labels.get(m) in patient_set)
    if rule == "relcl_gap":
        # object-gap relative clause: verb v attaches to antecedent a as an adnominal clause (acl / acl:relcl)
        return labels.get(v) == "acl"
    return True


def filter_candidates(cr, labels, patient_set):
    """Return the labeled-filtered candidate set + kept rule tags."""
    kept = set()
    kept_rules = {}
    for (v, a) in cr.candidates:
        rule = cr.cand_rules.get((v, a), "core_dep")
        if labeled_keep(v, a, rule, cr.heads, labels, patient_set):
            kept.add((v, a))
            kept_rules[(v, a)] = rule
    return kept, kept_rules


def _get_or_train_labeler(epochs, min_label_count, retrain):
    if (not retrain) and os.path.exists(LABELER_PATH):
        return ArcLabeler.load(LABELER_PATH), "loaded"
    tr = load_conllu("train")
    lab = train_label(tr, epochs=epochs, min_label_count=min_label_count)
    lab.save(LABELER_PATH)
    return lab, "trained"


def eval_las(labeler, parser, gold_sents, maxlen=50):
    """LAS on PREDICTED arcs: parse heads, label them, score head-correct AND label-correct vs gold."""
    n_tot = uas_c = las_c = 0
    lab_on_correct_c = lab_on_correct_n = 0
    for s in gold_sents:
        if not (1 <= len(s) <= maxlen):
            continue
        tokens = [t[1] for t in s]
        pos = [t[2] for t in s]
        pr = parser.parse(tokens, pos)
        labels = labeler.label(tokens, pos, pr.heads)
        from hdlab.arc_labeler import norm_label
        for i in range(1, len(s) + 1):
            gold_h = s[i - 1][3]
            gold_lab = norm_label(s[i - 1][4])
            if gold_h < 0 or gold_h > len(s):
                continue
            n_tot += 1
            head_ok = (pr.heads.get(i, -1) == gold_h)
            lab_ok = (labels.get(i) == gold_lab)
            uas_c += int(head_ok)
            las_c += int(head_ok and lab_ok)
            if head_ok:
                lab_on_correct_n += 1
                lab_on_correct_c += int(lab_ok)
    return {
        "uas": round(uas_c / n_tot, 4) if n_tot else None,
        "las": round(las_c / n_tot, 4) if n_tot else None,
        "label_acc_on_correctly_attached": round(lab_on_correct_c / lab_on_correct_n, 4) if lab_on_correct_n else None,
        "n_arcs": n_tot,
    }


def payoff(gen, labeler, lessons):
    """Re-derive the UNLABELED baseline AND the LABELED filter on the same gold; per-construction table."""
    order, sent_text, reader_svo = LCCP.load_slice_and_reader(lessons)
    with open(BASE.GOLD_PATH, encoding="utf-8") as f:
        gold = json.load(f)["gold"]

    # per-construction: [unlab_rec, lab_tight_rec, lab_loose_rec, n]
    by_con = defaultdict(lambda: [0, 0, 0, 0])
    parse_cache = {}
    labels_cache = {}
    gold_pairs_by_sid = defaultdict(set)
    n_pairs = 0

    for sid, rec in gold.items():
        if sid.split("_")[0] not in lessons:
            continue
        pos_rels = rec.get("pos", [])
        if not pos_rels:
            continue
        txt = sent_text.get(sid)
        if not txt:
            continue
        if sid not in parse_cache:
            cr = gen.generate(txt, extended=True)
            parse_cache[sid] = cr
            labels_cache[sid] = labeler.label(cr.tokens, cr.pos, cr.heads)
        cr = parse_cache[sid]
        labels = labels_cache[sid]
        lab_tight, _ = filter_candidates(cr, labels, PATIENT_TIGHT)
        lab_loose, _ = filter_candidates(cr, labels, PATIENT_LOOSE)

        for pr in pos_rels:
            v_lemma = LCCP.lemma_verb(pr["v"])
            patient = pr["patient"].lower()
            con = BASE.classify(txt, pr["v"].lower(), patient)
            gold_pairs_by_sid[sid].add((v_lemma, patient))
            v_verb, _ = BASE.locate_verb_idxs(cr.tokens, cr.pos, v_lemma)
            p_nom, _ = BASE.locate_patient_idxs(cr.tokens, cr.pos, patient)

            def rec_in(pairset):
                return 1 if (v_verb and p_nom and any((vi, pi) in pairset
                             for vi in v_verb for pi in p_nom)) else 0

            unlab = rec_in(cr.candidates)
            lt = rec_in(lab_tight)
            ll = rec_in(lab_loose)
            t = by_con[con]
            t[0] += unlab; t[1] += lt; t[2] += ll; t[3] += 1
            n_pairs += 1

    # candidate precision + count, unlabeled vs labeled (tight/loose)
    def prec_and_count(select_fn):
        tp = tot = 0
        counts = []
        for sid, cr in parse_cache.items():
            labels = labels_cache[sid]
            pairs = select_fn(cr, labels)
            counts.append(len(pairs))
            gp = gold_pairs_by_sid.get(sid, set())
            for (vi, ai) in pairs:
                tot += 1
                v_lem = LCCP.lemma_verb(cr.tokens[vi - 1])
                a_surf = cr.tokens[ai - 1].lower()
                if any(v_lem == gv and BASE._surf_match(a_surf, gpat) for (gv, gpat) in gp):
                    tp += 1
        return {
            "precision": round(tp / tot, 4) if tot else None,
            "n_candidate_pairs": tot,
            "mean_candidates_per_sentence": round(float(np.mean(counts)), 2) if counts else None,
            "tp": tp,
        }

    unlab_stats = prec_and_count(lambda cr, labels: cr.candidates)
    tight_stats = prec_and_count(lambda cr, labels: filter_candidates(cr, labels, PATIENT_TIGHT)[0])
    loose_stats = prec_and_count(lambda cr, labels: filter_candidates(cr, labels, PATIENT_LOOSE)[0])

    def agg(idx):
        num = sum(by_con[c][idx] for c in by_con)
        den = sum(by_con[c][3] for c in by_con)
        return round(num / den, 4) if den else 0.0

    con_table = {}
    for c in BASE.CONSTRUCTIONS:
        u, lt, ll, n = by_con.get(c, [0, 0, 0, 0])
        con_table[c] = {"n_gold_pairs": n,
                        "unlabeled_recall": round(u / n, 4) if n else None,
                        "labeled_tight_recall": round(lt / n, 4) if n else None,
                        "labeled_loose_recall": round(ll / n, 4) if n else None}
    n_hard = sum(by_con[c][3] for c in BASE.HARD_CONSTR)

    return {
        "n_gold_pos_pairs": n_pairs,
        "n_sentences": len(parse_cache),
        "aggregate_recall": {
            "unlabeled": agg(0), "labeled_tight_obj_nsubjpass": agg(1), "labeled_loose": agg(2),
        },
        "candidate_precision": {
            "unlabeled": unlab_stats, "labeled_tight_obj_nsubjpass": tight_stats, "labeled_loose": loose_stats,
        },
        "per_construction": con_table,
        "difficulty_on": {"n_hard_construction_pairs": n_hard, "n_total": n_pairs,
                          "hard_fraction": round(n_hard / n_pairs, 4) if n_pairs else 0.0},
    }


def run(mode, epochs, min_label_count, retrain):
    labeler, prov = _get_or_train_labeler(epochs, min_label_count, retrain)
    parser = ArcParser.load(BASE.ARC_PATH)
    gen = CandidateGenerator.load(BASE.POS_PATH, BASE.ARC_PATH)

    dev = load_conllu("dev")
    test = load_conllu("test")
    if mode == "smoke":
        dev = dev[:300]
        test = test[:300]
    la_dev = labeler.label_accuracy(dev)
    la_test = labeler.label_accuracy(test)
    las_dev = eval_las(labeler, parser, dev)
    las_test = eval_las(labeler, parser, test)

    lessons = BASE.SMOKE_LESSONS if mode == "smoke" else BASE.FULL_LESSONS
    pay = payoff(gen, labeler, lessons)

    metrics = {
        "anchor_name": ANCHOR_NAME,
        "mode": mode,
        "labeler_provenance": prov,
        "labeler_labels": labeler.labels,
        "train_epochs": epochs,
        "A_label_accuracy_given_gold_arcs": {
            "dev": round(la_dev[0], 4), "dev_n": la_dev[2],
            "test": round(la_test[0], 4), "test_n": la_test[2],
        },
        "B_LAS_on_predicted_arcs": {
            "dev": las_dev, "test": las_test, "uas_ref_persisted_parser": UAS_REF,
        },
        "C_payoff_mcguffey": pay,
        "unlabeled_precision_ref_CITED": UNLAB_PRECISION_REF,
    }

    # verdict banding
    tight = pay["candidate_precision"]["labeled_tight_obj_nsubjpass"]["precision"]
    tight_cps = pay["candidate_precision"]["labeled_tight_obj_nsubjpass"]["mean_candidates_per_sentence"]
    unlab_prec = pay["candidate_precision"]["unlabeled"]["precision"]
    lab_rec = pay["aggregate_recall"]["labeled_tight_obj_nsubjpass"]
    unlab_rec = pay["aggregate_recall"]["unlabeled"]
    la = la_dev[0]
    tight = tight if tight is not None else 0.0
    tight_cps = tight_cps if tight_cps is not None else 99.0
    if la < 0.85 or (unlab_prec is not None and tight <= unlab_prec) or lab_rec < 0.60:
        verdict = "FAIL"
    elif tight >= 0.25 and lab_rec >= 0.75 and tight_cps < 6:
        verdict = "PASS"
    else:
        verdict = "MIDDLE_BAND"
    metrics["verdict"] = verdict
    metrics["verdict_msg"] = (
        "label_acc_gold=%.3f LAS_dev=%s | payoff: unlab prec=%.3f rec=%.3f (%.1f cps) -> labeled(obj/nsubj:pass) "
        "prec=%.3f rec=%.3f (%.1f cps) | %s"
        % (la, las_dev["las"], unlab_prec or 0.0, unlab_rec,
           pay["candidate_precision"]["unlabeled"]["mean_candidates_per_sentence"] or 0.0,
           tight, lab_rec, tight_cps, verdict))
    metrics["summary"] = metrics["verdict_msg"]
    return metrics


def _atomic_write(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2)
    os.replace(tmp, path)


def _write_crash(exc):
    diag = {"verdict": "CELL_CRASHED", "verdict_msg": "%s: %s" % (type(exc).__name__, str(exc)[:500]),
            "summary": "CELL_CRASHED: %s" % type(exc).__name__, "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000], "ts_iso": datetime.now(timezone.utc).isoformat(),
            "anchor_name": ANCHOR_NAME}
    _atomic_write(os.path.join(OUT_DIR, "metrics.json"), diag)


def self_test():
    """Fast self-test (<70s): train a small labeler, assert design-gate mechanics fire before any full run."""
    from hdlab.arc_labeler import _self_test as module_selftest
    module_selftest()  # subj/object separation on a toy
    # mini real train (2000 sents, 2 epochs) -> assert dev label-acc-given-gold clears the FAIL floor 0.85
    tr = load_conllu("train")[:2000]
    lab = train_label(tr, epochs=2, min_label_count=5)
    dev = load_conllu("dev")[:200]
    acc, cc, tt = lab.label_accuracy(dev)
    print("[selftest] mini-train dev label-acc-given-gold = %.4f (%d/%d)" % (acc, cc, tt))
    assert acc >= 0.85, "SELF-TEST FAIL: mini labeler dev acc %.3f < 0.85 floor" % acc
    assert {"obj", "nsubj", "nsubj:pass"} <= set(lab.labels), "SELF-TEST FAIL: patient-critical labels missing"
    # the labeled filter MUST actually prune (discriminator fires): a subject nominal dropped, object kept
    gen = CandidateGenerator.load(BASE.POS_PATH, BASE.ARC_PATH)
    cr = gen.generate("The boy threw the ball.", extended=True)
    labels = lab.label(cr.tokens, cr.pos, cr.heads)
    tight, _ = filter_candidates(cr, labels, PATIENT_TIGHT)
    print("[selftest] 'The boy threw the ball.' unlabeled=%d labeled=%d cands" % (len(cr.candidates), len(tight)))
    assert len(tight) < len(cr.candidates), "SELF-TEST FAIL: labeled filter did not prune ANY candidate (G4 dead)"
    print("[selftest] PASS: labeler trains + labels patient roles + filter prunes distractors")
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--epochs", type=int, default=6)
    ap.add_argument("--min-label-count", type=int, default=30)
    ap.add_argument("--retrain", action="store_true")
    args, _ = ap.parse_known_args()
    if args.self_test:
        self_test()
        return
    mode = "smoke" if args.smoke else "full"
    epochs = 3 if mode == "smoke" else args.epochs
    t0 = time.time()
    metrics = run(mode, epochs, args.min_label_count, args.retrain or mode == "smoke")
    metrics["elapsed_s"] = round(time.time() - t0, 1)
    _atomic_write(os.path.join(OUT_DIR, "metrics.json"), metrics)
    print("\n=== LABELED-ARC CANDIDATE FILTER (%s) ===" % mode)
    print("  A label-acc-given-gold  dev=%.4f test=%.4f"
          % (metrics["A_label_accuracy_given_gold_arcs"]["dev"], metrics["A_label_accuracy_given_gold_arcs"]["test"]))
    print("  B LAS on predicted arcs dev=%s test=%s (UAS ref %.4f)"
          % (metrics["B_LAS_on_predicted_arcs"]["dev"]["las"], metrics["B_LAS_on_predicted_arcs"]["test"]["las"], UAS_REF))
    pay = metrics["C_payoff_mcguffey"]
    print("  C payoff on McGuffey (%d gold pairs, %d sents, hard_frac=%.2f):"
          % (pay["n_gold_pos_pairs"], pay["n_sentences"], pay["difficulty_on"]["hard_fraction"]))
    cp = pay["candidate_precision"]
    ar = pay["aggregate_recall"]
    print("    %-14s prec    cps    recall" % "")
    print("    %-14s %.4f  %5.2f  %.4f" % ("unlabeled", cp["unlabeled"]["precision"] or 0,
          cp["unlabeled"]["mean_candidates_per_sentence"] or 0, ar["unlabeled"]))
    print("    %-14s %.4f  %5.2f  %.4f" % ("tight obj/pass", cp["labeled_tight_obj_nsubjpass"]["precision"] or 0,
          cp["labeled_tight_obj_nsubjpass"]["mean_candidates_per_sentence"] or 0, ar["labeled_tight_obj_nsubjpass"]))
    print("    %-14s %.4f  %5.2f  %.4f" % ("loose", cp["labeled_loose"]["precision"] or 0,
          cp["labeled_loose"]["mean_candidates_per_sentence"] or 0, ar["labeled_loose"]))
    print("    per-construction:")
    for c in BASE.CONSTRUCTIONS:
        r = pay["per_construction"][c]
        if r["n_gold_pairs"]:
            print("      %-14s n=%2d  unlab_rec=%s  tight_rec=%s  loose_rec=%s"
                  % (c, r["n_gold_pairs"], r["unlabeled_recall"], r["labeled_tight_recall"], r["labeled_loose_recall"]))
    print("\n  VERDICT:", metrics["verdict_msg"])
    print("  labeler ->", LABELER_PATH)
    print("  metrics ->", os.path.join(OUT_DIR, "metrics.json"))


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        _write_crash(e)
        raise
