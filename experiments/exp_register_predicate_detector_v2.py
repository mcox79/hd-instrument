"""exp_register_predicate_detector_v2 -- two brain-fidelity pushes over v1, each addressing a NAMED residual.

v1 clears the bar (register-robust learned noisy-channel combiner; MODERN 0.899 / 19c-transfer 0.5625 recovery @
FP<=0.5, twin losing CI-sep). Its two least-brain-faithful parts, from the fidelity self-eval + residual diagnosis:
  (A) CANDIDATE GATE = WordNet verb-reading = a STATIC LEXICON (the drill: NOT brain-faithful). It misses coined/
      archaic verbs ("out-heroded") -> caps 19c candidate coverage at 0.91. The brain admits a novel verb from
      PRODUCTIVE MORPHOLOGY + frame (Jabberwocky; Fedorenko), not a dictionary. FIX: gate = WordNet OR productive
      verb morphology (out-/-ize/-ify/-ate/-en/en-/re-/de- + inflection).
  (B) MISSING CONSTRUCTION: the "no_subject" residual (obey, equal) are IMPERATIVES -- clause-initial bare verb, no
      overt subject, implied addressee. v1's subj_before cue cannot fire on them. FIX: add an imperative-slot cue
      (clause-initial / post-boundary + verb morphology + no preceding subject in the clause).

Measures v1-gate vs v2-gate coverage of dropped verbs, and v1-features vs v2-features recovery (esp. the no_subject +
novel-form residual), same CV/transfer protocol. Glass-box, CPU, NO LLM/spaCy. ASCII. own dir.
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

OUT_DIR = os.path.join(_REPO, "data/exp_register_predicate_detector_v2")
NOMINAL = D.NOMINAL
BOUNDARY = {".", ",", ";", ":", "!", "?", '"', "``", "''", "--", "-", "(", ")", "and", "but", "or", "then", "so"}
V_SUFFIX = ("ize", "ise", "ify", "ate", "en")          # derivational verb-formers
V_PREFIX = ("out", "re", "de", "un", "en", "be", "over", "under", "mis", "dis")
INFLECT = ("ing", "eth", "est", "ed", "es", "s", "'d", "th", "n", "d")
FEAT_NAMES_V2 = D.FEAT_NAMES + ["imperative_slot"]


def productive_verb_morph(w):
    """Register-invariant morphological verbhood for NOVEL/coined forms the static lexicon misses (Jabberwocky)."""
    wl = w.lower().strip("'\"-.,;:!?()")
    if not wl or not wl[0].isalpha():
        return False
    # derivational verb-formers
    if any(wl.endswith(s) and len(wl) > len(s) + 1 for s in V_SUFFIX):
        return True
    # productive prefix + inflectional ending (out-heroded, re-verbed, over-acted)
    if any(wl.startswith(p) for p in V_PREFIX) and any(wl.endswith(s) for s in ("ed", "ing", "s", "en")):
        return True
    return False


def verb_candidate(tok):
    """v2 gate: WordNet verb-reading OR productive verb morphology (extends candidacy to coined/archaic verbs)."""
    return VID.has_verb_reading(tok) or productive_verb_morph(tok)


def imperative_slot(toks, pos, i):
    """Imperative construction: a clause-initial / post-boundary token with verb morphology and NO preceding nominal
    subject in its clause (the brain reads a directive with an implied addressee-subject)."""
    if any(pos[j] in NOMINAL for j in range(0, i)):
        # a subject earlier in the sentence -> look only within the current clause (after the last boundary)
        last_b = max([j for j in range(0, i) if toks[j].lower() in BOUNDARY] + [-1])
        if any(pos[j] in NOMINAL for j in range(last_b + 1, i)):
            return 0.0
    else:
        last_b = -1
    at_clause_start = (i == last_b + 1) or (i == 0)
    return 1.0 if (at_clause_start and D.morph_finite(toks[i])) else 0.0


def feats_v2(toks, pos, i, W, tags):
    base = D.feats_parsefree(toks, pos, i, W, tags)
    return base + [imperative_slot(toks, pos, i)]


def cands_v2(toks, pos, gold_verb_set, W, tags):
    out = []
    for i in range(len(toks)):
        if pos[i] in ("VERB", "AUX"):
            continue
        if not verb_candidate(toks[i]):
            continue
        out.append((i, feats_v2(toks, pos, i, W, tags), 1 if i in gold_verb_set else 0))
    return out


def build_rows(sents, W, tags):
    tg = D.tagger(); rows = []; nsent = 0
    for toks, gold_verb in sents:
        if not toks:
            continue
        pos = tg.tag(toks)
        dropped = set(i for i in gold_verb if pos[i] not in ("VERB", "AUX"))
        for (i, fv, _l) in cands_v2(toks, pos, gold_verb, W, tags):
            rows.append((nsent, i, fv, 1 if i in dropped else 0))
        nsent += 1
    return rows, nsent


def build_rows_19c(pop, W, tags, cap=None):
    tg = D.tagger(); rows = []; nsent = 0
    if cap:
        pop = pop[:cap]
    for r in pop:
        toks = r["sent"].split(); vi = r["verb_idx"]
        if not toks or vi >= len(toks):
            continue
        pos = tg.tag(toks)
        gv = {vi} if (pos[vi] not in ("VERB", "AUX")) else set()
        for (i, fv, _l) in cands_v2(toks, pos, gv, W, tags):
            rows.append((nsent, i, fv, 1 if i in gv else 0))
        nsent += 1
    return rows, nsent


def gate_compare(pop, W, tags, cap=None):
    """v1 (WordNet) vs v2 (WordNet OR morph) candidate coverage of ALL dropped open-class 19c verbs."""
    tg = D.tagger(); total = 0; g1 = 0; g2 = 0; novel = []
    pop_c = pop[:cap] if cap else pop
    for r in pop_c:
        toks = r["sent"].split(); vi = r["verb_idx"]
        if not toks or vi >= len(toks):
            continue
        pos = tg.tag(toks)
        if pos[vi] not in ("VERB", "AUX"):
            total += 1
            w1 = VID.has_verb_reading(toks[vi]); w2 = verb_candidate(toks[vi])
            g1 += int(w1); g2 += int(w2)
            if w2 and not w1 and len(novel) < 12:
                novel.append(toks[vi])
    return {"total_dropped": total, "v1_wordnet_gated": g1, "v2_ext_gated": g2,
            "v1_cov": round(g1 / max(1, total), 4), "v2_cov": round(g2 / max(1, total), 4),
            "novel_forms_recovered_by_morph": novel}


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

    print("building v2 rows ...", flush=True)
    ud_test = D.load_ud(D.UD_TEST, cap=cap)
    qasrl = D.load_qasrl(D.QASRL, cap=qcap)
    pop = V1.load_pop(D.LB)
    mod_rows, mod_ns = build_rows(ud_test, W, tags)
    q_rows, q_ns = build_rows(qasrl, W, tags)
    c19_rows, c19_ns = build_rows_19c(pop, W, tags, cap=lbcap)
    train_all = mod_rows + q_rows

    modern = D.evaluate(mod_rows, mod_ns, D.cv_proba(mod_rows))
    clf, mu, sd = D._fit(train_all)
    coefs = dict(zip(FEAT_NAMES_V2, [round(float(c), 3) for c in clf.coef_[0]]))
    c19 = D.evaluate(c19_rows, c19_ns, D._proba(clf, mu, sd, c19_rows))
    gate = gate_compare(pop, W, tags, cap=lbcap)

    res = {"combiner_coefs_standardized": coefs, "n_train_positives": int(sum(r[3] for r in train_all)),
           "MODERN_udtest_cv": {k: modern[k] for k in ("best_fp_le_0p5", "best_fp_le_1", "twin_at_best", "bootstrap_delta_vs_twin", "n_positives", "n_sent")},
           "C19_transfer": {k: c19[k] for k in ("best_fp_le_0p5", "best_fp_le_1", "twin_at_best", "bootstrap_delta_vs_twin", "n_positives", "n_sent")},
           "gate_coverage_v1_vs_v2": gate,
           "v1_reference": {"modern_rec@0.5": 0.8989, "c19_rec@0.5": 0.5625, "c19_gate_cov": 0.9114}}
    with open(os.path.join(OUT_DIR, "metrics.json"), "w", encoding="ascii") as fh:
        json.dump({"anchor_name": "register_predicate_detector_v2", "results": res,
                   "elapsed_s": round(time.time() - t0, 1), "ts_iso": datetime.now(timezone.utc).isoformat()}, fh, indent=2)

    print("\n===== v2: morphological gate + imperative cue =====", flush=True)
    print("  coefs:", coefs, flush=True)
    print("\n  GATE COVERAGE of ALL dropped 19c verbs:  v1(WordNet)=%.4f  v2(+morph)=%.4f  (novel recovered: %s)" % (
        gate["v1_cov"], gate["v2_cov"], gate["novel_forms_recovered_by_morph"]), flush=True)
    for name, r in (("MODERN(CV)", modern), ("19c-TRANSFER", c19)):
        b = r["best_fp_le_0p5"]; bt = r["bootstrap_delta_vs_twin"]; tw = r["twin_at_best"]
        print("\n  %s n_pos=%d: recovery@0.5FP=%.4f fp=%.4f  delta_vs_twin=%.4f CI[%.4f,%.4f] p95=%.4f %s" % (
            name, r["n_positives"], b["recovery"] if b else -1, b["false_verbs_per_sent"] if b else -1,
            bt["delta_vs_twin_mean"] if bt else 0, bt["ci"][0] if bt else 0, bt["ci"][1] if bt else 0,
            tw["twin_recovery_p95"] if tw else -1, "CI-SEP" if (bt and bt["ci"][0] > 0) else "ns"), flush=True)

    if args.self_test or args.smoke:
        assert gate["v2_cov"] >= gate["v1_cov"]
        print("\n[self-test] PASS", flush=True)
    print("\n[done] %.0fs" % (time.time() - t0), flush=True)


if __name__ == "__main__":
    main()
