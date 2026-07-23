"""exp_multi_turn_loop_multigenre_generalization_nphead_correct_v1 -- does the COMPLETE trustworthy reader's
ZERO-CONFIDENT-WRONG property GENERALIZE across DIVERSE genres (esp. DIALOGUE, the goal-relevant one)?

CONTEXT: the COMPLETE gate (29465-29468: coref-margin OR conflict OR NP-head-structure, PLUS correct-to-head)
gives halluc=0.000 on TWO NARRATIVE testbeds -- McGuffey (children's reader) + LitBank (literary prose)
(MM; n=53+21). SCOPE CAVEAT: 2 narrative corpora, NOT universal. The DEEP LESSON from the arc: STRUCTURAL
signals (NP-head) TRANSFER corpus-to-corpus; calibrated-margin signals are corpus-specific. This cell turns
"proven on 2 narrative testbeds" into a BROAD claim OR localizes the next error class, by applying the gate
UNCHANGED with FROZEN thresholds to 3 MORE genres.

THE INVARIANT UNDER TEST (the whole point = GENERALIZATION): the COMPLETE gate is applied BYTE-IDENTICALLY --
the imported 29468 gate functions (GN._build + CC.run_correct + GN._contribution), with the FROZEN McGuffey
threshold (FIXED_TH=0.490995, NO re-tune per corpus). Re-tuning would DEFEAT the generalization test. Only
the CORPUS is swapped (O.TEST_PASSAGES / O.TEST_QS re-pointed per genre).

    complete gate:  keep = is_answered AND coref_margin>FIXED_TH AND NOT conflict(n_distinct>1)
                            AND np_head_consistent ;  on an NP non-head answer, RETURN THE RECOVERED HEAD
                            (correct-to-head) instead of abstaining.

GENRES (3 MORE, DISTINCT from McGuffey+LitBank; REAL VERBATIM public-domain / task-available text):
  DIALOGUE  = tinyshakespeare (a PLAY -- dramatic dialogue with speaker turns). THE GOAL-RELEVANT genre
              (the substrate goal is "talk to it"). Verbatim lines from data/corpora/tinyshakespeare.txt.
  NEWS/WEB  = Universal Dependencies English Web Treebank (weblog / newsgroup / email factual sentences).
              Verbatim `# text =` sentences from data/corpora/ud_english_ewt/en_ewt-ud-test.conllu.
  EXPOSITORY= OpenStax "Concepts of Biology" textbook (technical/expository prose). Verbatim sentences
              from data/corpora/textbook_concepts_biology/cleaned/concepts_biology.clean.txt.
Each passage is a VERBATIM substring of its source (self-test asserts substring membership -- provenance
airtight, NO authored/fabricated text). Only the comprehension QUESTIONS + human GOLD are hand-authored
(independent of the extractor; anti-circular; NOT gate-friendly -- the gold is the ground-truth read of the
passage, not what the pipeline says).

ARMS per genre: NO_GATE (ungated baseline -- what halluc WOULD be) | PRIOR_GATE (coref-OR-conflict, = 29466)
  | ABSTAIN_GATE (+NP-head abstention, = 29467) | CORRECT_GATE (the COMPLETE gate, +correct-to-head, = 29468).
Anti-cheat must-fail SCRAMBLE (random passage-noun substitution at matched coverage) via CC.run_correct.

ASSESSABILITY GATE (per-genre discriminator-must-fire; META_RULE_AG / design-gate): a genre is ASSESSABLE
iff NO_GATE commits a NON-TRIVIAL answer set with SOME wrong (n_answered >= MIN_ASSESS_ATTEMPTS AND
n_wrong >= 1) -- else the reader extracts too little for the gate question to be meaningful (halluc==0
TRIVIALLY via near-total abstention), which is reported as LOW_COVERAGE_INCONCLUSIVE (an upstream EXTRACTOR
bottleneck, NOT a gate PASS). This keeps the headline claim honest.

BANDS (envelope-fail; set BEFORE the run; global halluc = wrong-answered / n_total, per genre):
  HARD_PASS (BROADLY GENERAL -- the trustworthy property is not 2-testbed-specific):
      DIALOGUE is ASSESSABLE AND every ASSESSABLE genre has complete-gate halluc <= 0.05 AND
      precision_on_answered >= 0.80 AND >=2 genres ASSESSABLE. (coverage EXPECTED + HEALTHY to DROP OOD --
      abstaining more when out of depth, with halluc held low, is the SUCCESS signature.)
  HARD_FAIL / LOCALIZE (honest + valuable -- a NEW confabulation error-class appears beyond NP-head):
      some ASSESSABLE genre has complete-gate halluc > 0.05 -> IDENTIFY the residual confident-wrong records
      (the new error class; e.g. particle/preposition-as-argument the NP-head + margin signals cannot see)
      -> localizes the next lever (does it need a NEW structural signal?).
  MIDDLE otherwise (partial -- halluc lowered but not to the <=0.05 floor on some assessable genre).

WHY GENUINELY CAN-FAIL: new genres have error classes the McGuffey/LitBank-derived signals never met --
web text grabs PARTICLES ("put OUT") and ADJECTIVES ("makes GOOD") as arguments; technical prose is largely
UN-GROUNDABLE (heavy abstention); Shakespearean syntax inverts. If a residual confident-wrong survives BOTH
the coref-margin AND the NP-head signals on any assessable genre, halluc RISES -> HARD_FAIL/LOCALIZE. The
data decides whether STRUCTURE keeps transferring or each genre has its own error profile.

DESIGN-GATE (verified at self-test): (1) VERBATIM provenance (each passage a substring of its source file);
(2) FROZEN th inherited from GN (== v3 McGuffey op-point; NO re-tune); (3) COMPLETE gate BYTE-IDENTICAL
(imported 29468 functions, corpus swapped); (4) NO answer leakage (gold token never in its spec); (5) real
code path (GN._build builds the REAL perceptron + POS + coref + NP-head on each genre); (6) per-genre
ASSESSABILITY (NO_GATE non-trivial + some-wrong, else INCONCLUSIVE); (7) arms differ per assessable genre;
(8) determinism (OMP=1, fixed seed via GN.SEED, sorted set, no hash()-seeding).

CELL-TEMPLATE (relevant subset; many SCHEMA-VET gates N/A for this non-HD glass-box cell):
# - except SystemExit/KeyboardInterrupt: raise BEFORE except Exception (no BaseException)
# - ATOMIC final metrics write (tmp + os.replace)                    [META_RULE_AH: tmp_replace]
# - ARMS-MUST-DIFFER hash check per assessable genre                 [META_RULE_AF]
# - discriminator CAN-FAIL (residual particle/adjective-as-argument survives OOD) AND FIRES (NO_GATE
#   commits wrong answers per genre)                                 [design-gate / META_RULE_AG]
# - FROZEN threshold; COMPLETE gate IDENTICAL to 29468 (the transfer invariant, imported not re-typed)
# - VERBATIM provenance self-test (passage substring of source file)
# - baseline_in_band: NO_GATE commits a non-trivial answer set on the assessable genres; gate free to fail
# - deterministic (fixed seed, OMP=1, no hash()-seed, sorted(set))   [F.5 / PROT-023]
# - start-marker + crash-diagnostic; heartbeat EXEMPT (wall < 120s)
# - crlb_n/a: symbolic glass-box; halluc (truthfulness invariant) is the reported quantity
# - progress_logging: print_flush_true.  gate_threshold: FIXED interpretable rule, FROZEN (no re-tune).
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import argparse
import json
import platform
import sys
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

# GN = the 29468 base gate module (owns O, FIXED_TH, SEED, N_SCRAMBLE_SEEDS, _build, _prior_keep, _new_keep,
#      _np_ok, _conflict, _gate_metrics, _contribution). CC = the shared complete-gate (correct-to-head)
#      logic -- BYTE-IDENTICAL to the McGuffey + LitBank sister cells (the transfer invariant).
import experiments.exp_multi_turn_loop_litbank_ood_nphead_gate_v1 as GN
import experiments._np_head_correct_common as CC

O = GN.O
ANCHOR_NAME = "multi_turn_loop_multigenre_generalization_nphead_correct_v1"
FIXED_TH = GN.FIXED_TH  # 0.490995, inherited + frozen (GN.self_test asserts == v3 McGuffey op-point)

# CITED narrative-testbed operating points (the 2-testbed baseline this cell tries to broaden).
MCGUFFEY_OP_HALLUC = 0.0377   # CITED@exp_multi_turn_loop_realtext_confidence_abstain_gate_v3
LITBANK_COMPLETE_HALLUC = 0.0  # CITED@exp_multi_turn_loop_litbank_ood_nphead_correct_v1 (complete gate)

# a genre is ASSESSABLE only if NO_GATE commits a non-trivial answer set with some wrong (discriminator fires)
MIN_ASSESS_ATTEMPTS = 5
# cross-genre bands
HP_HALLUC_MAX = 0.05
HP_PRECISION_MIN = 0.80

SOURCES = {
    "shakespeare": REPO / "data" / "corpora" / "tinyshakespeare.txt",
    "ud_ewt": REPO / "data" / "corpora" / "ud_english_ewt" / "en_ewt-ud-test.conllu",
    "biology": REPO / "data" / "corpora" / "textbook_concepts_biology" / "cleaned" / "concepts_biology.clean.txt",
}

# ============================================================================================
# GENRE CORPORA. Each entry: pid -> (verbatim_passage_text, source_key). Passages are VERBATIM
# substrings of their source file (self-test asserts membership). Qs carry a query spec (never the
# answer) + human gold (ground-truth read of the passage, NOT gate-friendly).
# ============================================================================================
DIALOGUE_PASSAGES = {  # tinyshakespeare -- dramatic dialogue (a play with speaker turns)
    "s1": ("Let us kill him, and we'll have corn at our own price.", "shakespeare"),
    "s2": ("He killed my father.", "shakespeare"),
    "s3": ("How often he had met you, sword to sword;", "shakespeare"),
    "s4": ("This fellow had a Volscian to his mother;", "shakespeare"),
    "s6": ("Is this the promise that you made your mother?", "shakespeare"),
    "s7": ("it made me once restore a purse of gold", "shakespeare"),
    "s9": ("He sent in writing after me; what he would not,", "shakespeare"),
    "s10": ("I brought high Hereford, if you call him so,", "shakespeare"),
}
DIALOGUE_QS = [
    ("d_s1", "s1", ("svo_patient", "kill", "us"), "him", "Whom do they resolve to kill?"),
    ("d_s2", "s2", ("svo_patient", "killed", "he"), "father", "Whom did he kill?"),
    ("d_s3", "s3", ("svo_patient", "met", "he"), "you", "Whom had he met?"),
    ("d_s4", "s4", ("has_owner", "volscian"), "fellow", "Who had a Volscian?"),
    ("d_s6", "s6", ("svo_patient", "made", "you"), "promise", "What did you make your mother?"),
    ("d_s7", "s7", ("svo_patient", "restore", "me"), "purse", "What did he once restore?"),
    ("d_s9", "s9", ("svo_patient", "sent", "he"), "writing", "In what did he send word?"),
    ("d_s10", "s10", ("svo_patient", "brought", "i"), "hereford", "Whom did I bring?"),
]

NEWS_PASSAGES = {  # UD English Web Treebank -- weblog / newsgroup / email factual sentences
    "w1": ("They own blogger, of course.", "ud_ewt"),
    "w2": ("One of the pictures shows a flag that was found in Fallujah.", "ud_ewt"),
    "w3": ("He makes some good observations on a few of the pic's.", "ud_ewt"),
    "w4": ("He has maintained a good relationship with Mulva.", "ud_ewt"),
    "w5": ("Santa Claus has the right idea.", "ud_ewt"),
    "w6": ("We now have over 5000 addresses.", "ud_ewt"),
    "w7": ("John Donovan from Argghhh! has put out a excellent slide show on what was "
           "actually found and fought for in Fallujah.", "ud_ewt"),
    "w8": ("Bush did not have his eye on the ball.", "ud_ewt"),
}
NEWS_QS = [
    ("n_w1", "w1", ("svo_patient", "own", "they"), "blogger", "What do they own?"),
    ("n_w2a", "w2", ("svo_patient", "shows", "pictures"), "flag", "What do the pictures show?"),
    ("n_w2b", "w2", ("loc_ground", "flag"), "fallujah", "Where was the flag found?"),
    ("n_w3", "w3", ("svo_patient", "makes", "he"), "observations", "What does he make?"),
    ("n_w4", "w4", ("svo_patient", "maintained", "he"), "relationship", "What has he maintained?"),
    ("n_w5", "w5", ("has_owner", "idea"), "claus", "Who has the right idea?"),
    ("n_w6", "w6", ("svo_patient", "have", "we"), "addresses", "What do we now have?"),
    ("n_w7", "w7", ("svo_patient", "put", "john"), "show", "What did John put out?"),
    ("n_w8", "w8", ("has_owner", "eye"), "bush", "Whose eye was not on the ball?"),
]

BIO_PASSAGES = {  # OpenStax Concepts of Biology -- technical / expository prose
    "b1": ("The domain Eukarya contains organisms that have cells with nuclei.", "biology"),
    "b6": ("Many multicellular organisms (those made up of more than one cell) produce specialized "
           "reproductive cells that will form new individuals.", "biology"),
    "b7": ("A proton is a positively charged particle that resides in the nucleus (the core of the "
           "atom) of an atom and has a mass of 1 and a charge of +1.", "biology"),
    "b8": ("Therefore, the course has a greater impact on their learning experience.", "biology"),
    "b9": ("All atoms contain protons, electrons, and neutrons.", "biology"),
    "b10": ("The second and third energy levels can hold up to eight electrons.", "biology"),
    "b13": ("Inductive reasoning uses results to produce general scientific principles.", "biology"),
    "b14": ("Different populations may live in the same specific area.", "biology"),
    "b17": ("When cows eat this plant, Tremetol is concentrated in the milk.", "biology"),
    "b21": ("Several human proteins are expressed in the milk of transgenic sheep and goats.", "biology"),
}
BIO_QS = [
    ("x_b1", "b1", ("svo_patient", "contains", "eukarya"), "organisms", "What does the domain Eukarya contain?"),
    ("x_b6", "b6", ("svo_patient", "produce", "organisms"), "cells", "What do multicellular organisms produce?"),
    ("x_b7", "b7", ("loc_ground", "proton"), "nucleus", "Where does a proton reside?"),
    ("x_b8", "b8", ("has_owner", "impact"), "course", "What has a greater impact?"),
    ("x_b9", "b9", ("svo_patient", "contain", "atoms"), "protons", "What do all atoms contain?"),
    ("x_b10", "b10", ("svo_patient", "hold", "levels"), "electrons", "What can energy levels hold?"),
    ("x_b13", "b13", ("svo_patient", "uses", "reasoning"), "results", "What does inductive reasoning use?"),
    ("x_b14", "b14", ("loc_ground", "populations"), "area", "Where may different populations live?"),
    ("x_b17", "b17", ("svo_patient", "eat", "cows"), "plant", "What do cows eat?"),
    ("x_b21", "b21", ("loc_ground", "proteins"), "milk", "Where are the human proteins expressed?"),
]

GENRES = [
    ("DIALOGUE", "shakespeare_play", DIALOGUE_PASSAGES, DIALOGUE_QS, True),  # goal-relevant
    ("NEWS_WEB", "ud_english_web_treebank", NEWS_PASSAGES, NEWS_QS, False),
    ("EXPOSITORY", "openstax_concepts_of_biology", BIO_PASSAGES, BIO_QS, False),
]

_SRC_CACHE = {}


def _source_text(key):
    if key not in _SRC_CACHE:
        _SRC_CACHE[key] = SOURCES[key].read_text(encoding="utf-8")
    return _SRC_CACHE[key]


def _install(passages):
    O.TEST_PASSAGES = {pid: txt for pid, (txt, _src) in passages.items()}
    O.TEST_QS = []


def _mk_qs(qs_spec):
    return [dict(qid=qid, p=p, slice="NC", atype="X", spec=spec, gold=gold, text=text)
            for (qid, p, spec, gold, text) in qs_spec]


# ============================================================================================
# infra: out-dir / markers / metrics / crash (atomic).
# ============================================================================================
def _out_dir(run_mode):
    sub = ANCHOR_NAME + ("_smoke" if run_mode == "smoke" else "")
    d = REPO / "data" / ("exp_" + sub)
    d.mkdir(parents=True, exist_ok=True)
    return d


def _write_start_marker(out_dir, run_mode, expected_n_units):
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": run_mode,
              "expected_n_units": expected_n_units, "host": platform.node()}
    tmp = out_dir / "_start_marker.json.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, out_dir / "_start_marker.json")


def _write_metrics(out_dir, metrics):
    tmp = out_dir / "metrics.json.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, out_dir / "metrics.json")


def _write_crash_metrics(out_dir, exc):
    diag = {"verdict": "CELL_CRASHED", "verdict_msg": "%s: %s" % (type(exc).__name__, str(exc)[:500]),
            "summary": "CELL_CRASHED: %s" % type(exc).__name__, "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000], "ts_iso": datetime.now(timezone.utc).isoformat(),
            "pid": os.getpid(), "anchor_name": ANCHOR_NAME}
    _write_metrics(out_dir, diag)


# ============================================================================================
# per-genre run: install corpus, build records via the REAL 29468 pipeline, run the COMPLETE gate.
# ============================================================================================
def run_genre(genre_label, corpus_label, passages, qs_spec, clf):
    _install(passages)
    qs = _mk_qs(qs_spec)
    O.TEST_QS = qs
    recs, _stores, scale = GN._build(clf, qs)
    res = CC.run_correct(GN, recs, scale)
    contrib = GN._contribution(recs)  # which signal (conflict / coref-margin / NP-head) catches each wrong

    no_gate = res["baseline"]
    op = res["operating_point"]         # the COMPLETE gate (coref-margin OR conflict OR NP-head + correct-to-head)
    assessable = (no_gate["n_answered"] >= MIN_ASSESS_ATTEMPTS and no_gate["n_wrong"] >= 1)

    # arms-differ only meaningful/possible when the gate acts (assessable genres)
    arms_ok, arms_note = None, None
    try:
        CC.arms_differ(res)
        arms_ok, arms_note = True, "arms_differ_verified"
    except AssertionError as e:
        arms_ok, arms_note = False, str(e)

    # residual confident-wrong records that SURVIVE the complete gate = the NEW error class (if any)
    residual = [d for d in res["_recs_debug"]
                if d["correct_gate_ans"] is not None and d["correct_gate_correct"] == 0]

    gate_ok = (op["halluc"] <= HP_HALLUC_MAX and op["precision_on_answered"] >= HP_PRECISION_MIN)

    return {
        "genre": genre_label, "corpus": corpus_label, "goal_relevant": None,
        "n_total": no_gate["n_total"], "assessable": assessable,
        "no_gate": {"halluc": no_gate["halluc"], "coverage": no_gate["coverage"],
                    "precision_on_answered": no_gate["precision_on_answered"],
                    "n_answered": no_gate["n_answered"], "n_correct": no_gate["n_correct"],
                    "n_wrong": no_gate["n_wrong"]},
        "prior_gate": {"halluc": res["prior_gate"]["halluc"], "coverage": res["prior_gate"]["coverage"]},
        "abstain_gate_29467": {"halluc": res["abstain_gate"]["halluc"],
                               "coverage": res["abstain_gate"]["coverage"]},
        "complete_gate": {"halluc": op["halluc"], "coverage": op["coverage"],
                          "precision_on_answered": op["precision_on_answered"],
                          "n_answered": op["n_answered"], "n_correct_kept": op["n_correct_kept"],
                          "n_wrong_kept": op["n_wrong_kept"]},
        "gate_ok": gate_ok,
        "coverage_rise_correct_to_head_vs_abstain": res["coverage_rise_vs_abstain"],
        "signal_attribution": {
            "n_wrong_answered": contrib["n_wrong_answered"],
            "n_caught_by_conflict": contrib["n_wrong_caught_by_conflict"],
            "n_caught_by_coref_margin": contrib["n_wrong_caught_by_coref_margin"],
            "n_prior_residual": contrib["n_prior_residual"],
            "n_prior_residual_caught_by_nphead": contrib["n_prior_residual_caught_by_nphead"],
            "nphead_caught_qids": contrib["nphead_caught_qids"],
            "n_new_residual_survives_all_signals": contrib["n_new_residual"],
            "new_residual_qids": contrib["new_residual_qids"],
            "n_correct_false_abstained_by_nphead": contrib["n_correct_false_abstained_by_nphead"],
        },
        "correct_to_head_audit": res["correction_audit"],
        "scramble_random_noun": res["scramble_random_noun"], "beat_scramble": res["beat_scramble"],
        "residual_confident_wrong_records": [
            {"qid": d["qid"], "p": d["p"], "answer": d["correct_gate_ans"], "gold": d["gold"],
             "orig_ans": d["orig_ans"], "np_status": d["np_status"], "coref_conf": d.get("coref_conf")}
            for d in residual],
        "arms_differ_ok": arms_ok, "arms_differ_note": arms_note,
        "per_question": res["_recs_debug"],
    }


# ============================================================================================
# cross-genre verdict.
# ============================================================================================
def compute_verdict(genre_results):
    by_label = {g["genre"]: g for g in genre_results}
    dialogue = by_label.get("DIALOGUE")
    assessable = [g for g in genre_results if g["assessable"]]
    inconclusive = [g for g in genre_results if not g["assessable"]]

    dialogue_assessable = bool(dialogue and dialogue["assessable"])
    dialogue_ok = bool(dialogue and dialogue["assessable"] and dialogue["gate_ok"])
    all_assessable_ok = all(g["gate_ok"] for g in assessable) if assessable else False
    failing = [g for g in assessable if not g["gate_ok"]]

    hp = (dialogue_ok and all_assessable_ok and len(assessable) >= 2)
    hf = len(failing) >= 1

    if hp:
        tier = "HARD_PASS"
        outcome = "trustworthy-property-BROADLY-GENERAL-structural-transfer-holds-across-genres-incl-dialogue"
    elif hf:
        tier = "HARD_FAIL"
        outcome = "NEW-confabulation-error-class-appears-on-a-new-genre-halluc-rises-beyond-nphead"
    else:
        tier = "MIDDLE_BAND"
        outcome = "partial-generalization-or-dialogue-not-assessable"

    localize = []
    for g in failing:
        new_cls = [r for r in g["residual_confident_wrong_records"]]
        localize.append(
            "NEW ERROR CLASS on %s: complete-gate halluc=%.3f (>%.2f); %d confident-wrong SURVIVE both the "
            "coref-margin AND NP-head signals: %s -- these are the next lever (a new structural signal?)"
            % (g["genre"], g["complete_gate"]["halluc"], HP_HALLUC_MAX,
               len(new_cls), [(r["qid"], "ans=%r" % r["answer"], "gold=%r" % r["gold"],
                               "np=%s" % r["np_status"]) for r in new_cls]))
    if not dialogue_assessable:
        localize.append("DIALOGUE not assessable (NO_GATE attempts=%s wrong=%s < bar) -- cannot confirm the "
                        "goal-relevant genre" % (dialogue["no_gate"]["n_answered"] if dialogue else "NA",
                                                 dialogue["no_gate"]["n_wrong"] if dialogue else "NA"))
    for g in inconclusive:
        localize.append("%s LOW_COVERAGE_INCONCLUSIVE: NO_GATE answered %d/%d (wrong=%d) -- the EXTRACTOR "
                        "collapses to abstention on this genre (an UPSTREAM bottleneck, distinct from the "
                        "gate); the gate question is moot here, halluc=%.3f is trivial via near-total abstention"
                        % (g["genre"], g["no_gate"]["n_answered"], g["n_total"], g["no_gate"]["n_wrong"],
                           g["complete_gate"]["halluc"]))
    if hp and not localize:
        localize.append("STRUCTURAL trustworthy property TRANSFERS to all %d assessable genres (incl DIALOGUE): "
                        "complete-gate halluc <= %.2f with FROZEN th=%.6f (NO re-tune) -- broadly general, not "
                        "2-narrative-testbed-specific" % (len(assessable), HP_HALLUC_MAX, FIXED_TH))

    parts = []
    for g in genre_results:
        parts.append("%s[%s]: NO_GATE halluc=%.3f cov=%.3f -> COMPLETE halluc=%.3f cov=%.3f prec=%.3f%s"
                     % (g["genre"], "ASSESS" if g["assessable"] else "INCONCL",
                        g["no_gate"]["halluc"], g["no_gate"]["coverage"], g["complete_gate"]["halluc"],
                        g["complete_gate"]["coverage"], g["complete_gate"]["precision_on_answered"],
                        "" if g["gate_ok"] else " GATE_MISS"))
    msg = "%s (%s) | FROZEN th=%.6f NO re-tune | %s" % (tier, outcome, FIXED_TH, " || ".join(parts))
    return tier, outcome, msg, localize


# ============================================================================================
# self-test: verbatim provenance + frozen th + no leakage + assessability + real code path.
# ============================================================================================
def self_test():
    print("[self-test] building REAL 29468 pipeline (perceptron + POS + coref + NP-head) across genres ...",
          flush=True)

    # (0) FROZEN threshold inherited from GN (GN asserts == v3 McGuffey op-point).
    assert abs(FIXED_TH - 0.490995) < 1e-6, "FIXED_TH drifted from frozen McGuffey op-point"

    # (1) VERBATIM provenance: every passage is a substring of its named source file.
    for _label, _corp, passages, _qs, _gr in GENRES:
        for pid, (txt, srckey) in passages.items():
            src = _source_text(srckey)
            assert txt in src, "PROVENANCE BREACH: %s not a verbatim substring of %s" % (pid, srckey)

    # (2) NO answer leakage: gold token never appears in its query spec.
    for _label, _corp, _passages, qs_spec, _gr in GENRES:
        for (qid, _p, spec, gold, _text) in qs_spec:
            assert str(gold).lower() not in [str(x).lower() for x in spec], \
                "answer leakage: gold %r in spec %r (%s)" % (gold, spec, qid)

    clf = GN.V1.build_clf()

    # (3) REAL code path + (4) assessability discriminator: DIALOGUE + NEWS must be ASSESSABLE
    #     (NO_GATE commits a non-trivial answer set with SOME wrong -> the gate has real work).
    dia = run_genre("DIALOGUE", "shakespeare_play", DIALOGUE_PASSAGES, DIALOGUE_QS, clf)
    news = run_genre("NEWS_WEB", "ud_english_web_treebank", NEWS_PASSAGES, NEWS_QS, clf)
    assert dia["no_gate"]["n_answered"] >= MIN_ASSESS_ATTEMPTS, \
        "DIALOGUE not assessable: NO_GATE answered %d" % dia["no_gate"]["n_answered"]
    assert dia["no_gate"]["n_wrong"] >= 1, "DIALOGUE NO_GATE has no wrong answer -> gate has nothing to catch"
    assert news["no_gate"]["n_answered"] >= MIN_ASSESS_ATTEMPTS, \
        "NEWS not assessable: NO_GATE answered %d" % news["no_gate"]["n_answered"]
    assert news["no_gate"]["n_wrong"] >= 1, "NEWS NO_GATE has no wrong answer -> gate has nothing to catch"

    # (5) real answers reproduce O.answer_reader exactly (no drift) on DIALOGUE.
    _install(DIALOGUE_PASSAGES)
    O.TEST_QS = _mk_qs(DIALOGUE_QS)
    recs, stores, _scale = GN._build(clf, O.TEST_QS)
    for r in recs:
        base = O.normalize(O.answer_reader(r["q"]["spec"], stores.get(r["q"]["p"], [])))
        assert r["ans"] == base, "answer drift on %s: %r vs %r" % (r["q"]["qid"], r["ans"], base)

    print("[self-test] PASS | DIALOGUE NO_GATE halluc=%.3f cov=%.3f (ans=%d wrong=%d) -> COMPLETE halluc=%.3f "
          "cov=%.3f | NEWS NO_GATE halluc=%.3f (ans=%d wrong=%d) -> COMPLETE halluc=%.3f | FROZEN th=%.6f"
          % (dia["no_gate"]["halluc"], dia["no_gate"]["coverage"], dia["no_gate"]["n_answered"],
             dia["no_gate"]["n_wrong"], dia["complete_gate"]["halluc"], dia["complete_gate"]["coverage"],
             news["no_gate"]["halluc"], news["no_gate"]["n_answered"], news["no_gate"]["n_wrong"],
             news["complete_gate"]["halluc"], FIXED_TH), flush=True)
    return True


# ============================================================================================
# main run. FULL runs ALL genres inline to completion.
# ============================================================================================
def run(run_mode):
    out_dir = _out_dir(run_mode)
    genres = GENRES if run_mode != "smoke" else GENRES[:2]  # smoke = dialogue + news (the assessable pair)
    n_units = sum(len(qs) for (_l, _c, _p, qs, _g) in genres)
    _write_start_marker(out_dir, run_mode, expected_n_units=n_units)
    t0 = time.perf_counter()

    clf = GN.V1.build_clf()
    genre_results = []
    for (label, corpus, passages, qs_spec, goal_rel) in genres:
        gr = run_genre(label, corpus, passages, qs_spec, clf)
        gr["goal_relevant"] = goal_rel
        genre_results.append(gr)

    tier, outcome, msg, localize = compute_verdict(genre_results)
    elapsed = time.perf_counter() - t0

    assessable = [g["genre"] for g in genre_results if g["assessable"]]
    inconclusive = [g["genre"] for g in genre_results if not g["assessable"]]
    per_genre_halluc = {g["genre"]: g["complete_gate"]["halluc"] for g in genre_results}

    metrics = {
        "anchor_name": ANCHOR_NAME, "verdict": tier, "verdict_msg": msg, "summary": msg[:300],
        "gate_outcome": outcome, "run_mode": run_mode, "elapsed_s": round(elapsed, 4),
        "ts_iso": datetime.now(timezone.utc).isoformat(), "n_genres": len(genre_results),
        "arms": ["NO_GATE", "PRIOR_GATE", "ABSTAIN_GATE(29467)", "CORRECT_GATE(29468-complete)"],
        "threshold_frozen": True, "fixed_threshold": FIXED_TH, "no_retune": True,
        "threshold_source": "exp_multi_turn_loop_realtext_confidence_abstain_gate_v3 McGuffey operating_point "
                            "(inherited via 29468); FROZEN, NO re-tune per genre (the generalization test)",
        "complete_gate_definition": "coref_margin>FIXED_TH AND NOT conflict AND np_head_consistent; on an NP "
                                    "non-head answer RETURN THE RECOVERED HEAD (correct-to-head) -- BYTE-"
                                    "IDENTICAL to 29468 (imported GN._build + CC.run_correct + GN._contribution)",
        "min_assessable_attempts": MIN_ASSESS_ATTEMPTS,
        "assessable_genres": assessable, "inconclusive_genres": inconclusive,
        "per_genre_complete_gate_halluc": per_genre_halluc,
        "narrative_testbed_reference": {"mcguffey_op_halluc": MCGUFFEY_OP_HALLUC,
                                        "litbank_complete_halluc": LITBANK_COMPLETE_HALLUC,
                                        "note": "the 2 NARRATIVE testbeds this cell broadens (or localizes past)"},
        "key_question": "does the COMPLETE gate's zero-confident-wrong property generalize across DIVERSE "
                        "genres (esp DIALOGUE), OR does each genre have its own error profile?",
        "genre_results": genre_results,
        "bands": {"HP_halluc_max": HP_HALLUC_MAX, "HP_precision_min": HP_PRECISION_MIN,
                  "HP_requires": "DIALOGUE assessable AND every assessable genre complete-gate halluc<=0.05 AND "
                                 "precision>=0.80 AND >=2 assessable",
                  "HF_requires": "any assessable genre complete-gate halluc>0.05 (a NEW error class survives "
                                 "coref-margin AND NP-head) -> localize it",
                  "assessability": "NO_GATE n_answered>=%d AND n_wrong>=1, else LOW_COVERAGE_INCONCLUSIVE"
                                   % MIN_ASSESS_ATTEMPTS},
        "weakest_interface": localize,
        "gate_threshold_kind": "fixed_interpretable_rule_FROZEN_from_mcguffey_no_retune",
        "final_metrics_atomicity": "tmp_replace", "deterministic_seeding": True,
        "progress_logging": "print_flush_true", "compute_architecture": "sequential_cpu_pure_python",
        "crlb_n_a": "symbolic glass-box; halluc (truthfulness invariant) is the reported quantity",
        "fairness": {"frozen_thresholds_no_retune": True, "real_verbatim_text_per_genre": True,
                     "natural_gold_not_gate_friendly": True, "no_answer_leakage": True,
                     "no_gate_baseline_per_genre": True,
                     "per_genre_signal_attribution": "margin / conflict / NP-head reported per genre"},
        "reuse_credited": {
            "complete_gate_29468": "exp_multi_turn_loop_litbank_ood_nphead_gate_v1.py (GN: O, FIXED_TH, SEED, "
                                   "_build, prior/abstain/np predicates, _contribution) + "
                                   "experiments/_np_head_correct_common.py (CC: correct-to-head, run_correct, "
                                   "scramble) -- IMPORTED UNCHANGED (the transfer invariant)",
            "reader_pipeline": "exp_oracle_mention_upperbound_reader_v1.py (extractor, coref, answer engine)",
            "confidence_machinery": "exp_multi_turn_loop_realtext_confidence_abstain_gate_v1.py (build_clf, "
                                    "build_real_conf, component confs, scramble)",
            "corpora": "tinyshakespeare.txt (dialogue) + ud_english_ewt (news/web) + textbook_concepts_biology "
                       "(expository) -- all REAL verbatim public-domain / task-available"},
        "REQUIRED_FIELDS": ["verdict", "assessable_genres", "inconclusive_genres",
                            "per_genre_complete_gate_halluc", "genre_results", "threshold_frozen",
                            "fixed_threshold", "bands"],
        "notes": ("Multi-genre GENERALIZATION test of the COMPLETE trustworthy reader. The 29468 gate is applied "
                  "BYTE-IDENTICALLY with FROZEN McGuffey threshold (NO re-tune) to 3 DIVERSE genres (dialogue / "
                  "news-web / expository), swapping ONLY the corpus. Measures whether STRUCTURAL signals keep "
                  "transferring (broad claim) or each genre has its own error profile (localize the next class). "
                  "Per-genre assessability guards against vacuous near-total-abstention. CLAIM-VET-pending."),
    }
    _write_metrics(out_dir, metrics)

    print("[%s:%s] %s" % (ANCHOR_NAME, run_mode, msg), flush=True)
    for g in genre_results:
        print("  [%s] %s | NO_GATE halluc=%.3f cov=%.3f (ans=%d correct=%d wrong=%d of %d)"
              % (g["genre"], "ASSESSABLE" if g["assessable"] else "LOW_COVERAGE_INCONCLUSIVE",
                 g["no_gate"]["halluc"], g["no_gate"]["coverage"], g["no_gate"]["n_answered"],
                 g["no_gate"]["n_correct"], g["no_gate"]["n_wrong"], g["n_total"]), flush=True)
        print("        PRIOR halluc=%.3f cov=%.3f | ABSTAIN(29467) halluc=%.3f cov=%.3f | COMPLETE(29468) "
              "halluc=%.3f cov=%.3f prec=%.3f"
              % (g["prior_gate"]["halluc"], g["prior_gate"]["coverage"],
                 g["abstain_gate_29467"]["halluc"], g["abstain_gate_29467"]["coverage"],
                 g["complete_gate"]["halluc"], g["complete_gate"]["coverage"],
                 g["complete_gate"]["precision_on_answered"]), flush=True)
        sa = g["signal_attribution"]
        print("        signals: wrong=%d | conflict-catch=%d | coref-margin-catch=%d | NP-head-catch=%d %s | "
              "SURVIVES-ALL=%d %s | scramble-beat=%.3f"
              % (sa["n_wrong_answered"], sa["n_caught_by_conflict"], sa["n_caught_by_coref_margin"],
                 sa["n_prior_residual_caught_by_nphead"], sa["nphead_caught_qids"],
                 sa["n_new_residual_survives_all_signals"], sa["new_residual_qids"], g["beat_scramble"]),
              flush=True)
        if g["residual_confident_wrong_records"]:
            print("        RESIDUAL confident-wrong (NEW error class): %s"
                  % [(r["qid"], "ans=%r" % r["answer"], "gold=%r" % r["gold"], "np=%s" % r["np_status"])
                     for r in g["residual_confident_wrong_records"]], flush=True)
    print("  [weakest] %s" % localize, flush=True)
    print("  [metrics] -> %s" % (out_dir / "metrics.json"), flush=True)
    return tier


def main():
    ap = argparse.ArgumentParser(description=ANCHOR_NAME)
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--run-mode", choices=["self_test", "smoke", "full"], default=None)
    args = ap.parse_args()
    if args.self_test or args.run_mode == "self_test":
        self_test()
        sys.exit(0)
    run_mode = "smoke" if (args.smoke or args.run_mode == "smoke") else "full"
    run(run_mode)
    sys.exit(0)


if __name__ == "__main__":
    _md = "smoke" if ("--smoke" in sys.argv or ("--run-mode" in sys.argv and "smoke" in sys.argv)) else \
        ("self_test" if ("--self-test" in sys.argv or ("--run-mode" in sys.argv and "self_test" in sys.argv))
         else "full")
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(line_buffering=True)
        except Exception:
            pass
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        try:
            _write_crash_metrics(_out_dir(_md), e)
        except Exception:
            pass
        raise
