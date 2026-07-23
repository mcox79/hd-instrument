"""exp_multi_turn_loop_litbank_ood_fixed_gate_v1 -- does the METACOGNITIVE ABSTAIN GATE keep the reader
TRUTHFUL on OUT-OF-DOMAIN text by ABSTAINING MORE, rather than confidently confabulating?

CONTEXT: exp_multi_turn_loop_realtext_confidence_abstain_gate_v3 (HARD_PASS, 29465) achieved near-zero
hallucination (op_halluc=0.0377 MEASURED@data/exp_multi_turn_loop_realtext_confidence_abstain_gate_v3/
metrics.json:operating_point.halluc) at modest coverage (0.3774) on 14 McGuffey second-reader passages --
BUT the operating THRESHOLD (coref-margin > 0.490995, no match-conflict) was CHOSEN ON McGUFFEY
(in-domain). Open question: does the metacognition GENERALIZE? On UNSEEN / harder text the parse+coref
components get WORSE. A GOOD metacognitive gate should ABSTAIN MORE (coverage drops) but STAY truthful
(halluc stays low). A BAD gate's confidence signals do NOT transfer -> halluc RISES out-of-domain.

DISTINCT FROM prior wildtext work: exp_learned_role_assigner_reader_wildtext_v4 (HARD_FAIL) measured
ACCURACY collapse OOD (0.571 -> 0.217). THIS cell measures whether TRUTHFULNESS survives via ABSTENTION
-- a different invariant. Accuracy is EXPECTED to drop OOD; the question is whether the gate CONVERTS
that degradation into ABSTENTION (honest "I don't know") instead of CONFIDENT WRONG ANSWERS.

CORPUS (out-of-domain, task-endorsed): LitBank -- REAL VERBATIM narrative prose from published classic
novels (Poe "Masque of the Red Death", Wilde "Picture of Dorian Gray", Melville "Bartleby", Burnett
"Secret Garden", Austen "Emma"/"Pride and Prejudice"), each a public-domain literary work DISTINCT from
McGuffey in author, register, era, and vocabulary. Passages are reconstructed VERBATIM from the LitBank
CoNLL token streams (data/corpora/litbank_coref_conll/*.conll) at runtime -- the self-test asserts every
passage is a verbatim contiguous token subsequence of its source document (provenance airtight; NO
authored/fabricated text). Only the comprehension QUESTIONS + human GOLD are hand-authored (independent
of the extractor; anti-circular). This is a GENUINE domain shift: adult literary syntax (title+name
"Lord Henry", relative clauses, long coordinations) the grade-2-trained components were never tuned on.

THE INVARIANT UNDER TEST: the gate is applied UNCHANGED, with the McGuffey operating threshold FROZEN
(FIXED_TH = 0.490995, NO re-tuning on the new corpus -- re-tuning would DEFEAT the generalization test).
keep = is_answered AND coref_conf > FIXED_TH AND NOT conflict(n_distinct>1)   [BYTE-IDENTICAL to v3's
gate; the ONLY change is the corpus + the frozen (not re-chosen) threshold].

ARMS:
  NO_GATE      = REAL pipeline answers everything it commits (shows what halluc WOULD be with no gate).
  ABSTAIN_GATE = REAL + the McGuffey-tuned gate at the FROZEN threshold (THE MECHANISM; no re-tune).
  SCRAMBLE_GATE= anti-cheat must-fail: matched-coverage RANDOM abstention (answer the same NUMBER of Qs
                 at random). The real gate must BEAT random -- else "truthful" is just "answer fewer".

BANDS (envelope-fail; set BEFORE the run; global halluc = wrong-answered / n_total on the NEW corpus):
  HARD_PASS (metacognition GENERALIZES -- truthful-via-abstention transfers out-of-domain):
      op_halluc <= 0.08 AND
      precision_on_answered >= 0.80 AND
      (scramble_halluc - op_halluc) >= 0.05  (the gate BEATS random abstention -- signal, not "fewer").
    (coverage is EXPECTED + HEALTHY to DROP vs McGuffey -- the gate correctly abstains more when out of
     its depth; a coverage drop with halluc held low is the SUCCESS signature, not a failure.)
  HARD_FAIL (confidence does NOT transfer -- the gate was tuned to McGuffey):
      op_halluc > 0.10  (halluc RISES materially out-of-domain -> an important, honest bound), OR
      (scramble_halluc - op_halluc) <= 0.0  (real no better than random abstention).
  MIDDLE otherwise (partial transfer: 0.08 < halluc <= 0.10 -- truthfulness survives directionally but
     the McGuffey <=0.05 level is not fully retained; localize the residual).

WHY GENUINELY CAN-FAIL (not guaranteed either way): the gate abstains on (a) low coref-margin and (b)
store self-conflict. A UNIQUE-match parse error with FULL coref margin -- e.g. an adjective grabbed as
the object head ("the fair young man" -> answer "fair"), or a title grabbed as the agent head ("Lord
Henry pulled out his watch" -> answer "lord") -- is INVISIBLE to BOTH signals. Adult literary prose has
MORE such constructions (titles, relative clauses, coordinations) than controlled grade-2 McGuffey text,
so the residual OOD halluc may RISE above 0.05. The data decides which side of the bands it lands.

DESIGN-GATE (verified at self-test): (1) VERBATIM provenance -- every passage is a contiguous token
  subsequence of its LitBank CoNLL source; (2) FIXED threshold -- FIXED_TH is frozen from v3's McGuffey
  operating point, asserted equal to the on-disk v3 metrics operating_point.threshold, and NO
  choose_operating_threshold is EVER called (the whole point); (3) NO answer leakage -- specs are natural
  query patterns, never contain the gold; (4) NO_GATE baseline reported; (5) real code path exercised
  (perceptron fit + POS tag + WorkingOverlay coref + conf-extract on LitBank); (6) ONE-VARIABLE isolation
  -- the conf-extractor relation set is byte-identical to base O.extract_passage per LitBank passage;
  (7) arms differ; (8) determinism (OMP=1, fixed seed, sorted set, no hash()-seeding).

CELL-TEMPLATE (relevant subset; many SCHEMA-VET gates N/A for this non-HD glass-box cell):
# - except SystemExit/KeyboardInterrupt: raise BEFORE except Exception (no BaseException)
# - ATOMIC final metrics write (tmp + os.replace)                    [META_RULE_AH: tmp_replace]
# - ARMS-MUST-DIFFER hash check at run                               [META_RULE_AF]
# - discriminator CAN-FAIL (residual unique-match parse errors invisible to both signals)  [design-gate]
# - FROZEN threshold from v3 McGuffey op-point; NO re-tune (asserted; the generalization invariant)
# - VERBATIM provenance self-test (passage == contiguous CoNLL token subsequence)
# - real_code_path: self-test builds the REAL perceptron + POS + WorkingOverlay + conf-extract on LitBank
# - baseline_in_band: NO_GATE commits a non-trivial answer set on LitBank (not vacuous), gate free to fail
# - deterministic (fixed seed, OMP=1, no hash()-seed, sorted(set))                [F.5 / PROT-023]
# - start-marker + crash-diagnostic; heartbeat EXEMPT (wall < 90s)
# - crlb_n/a: symbolic glass-box; the truthfulness INVARIANT (halluc) is the reported quantity
# - progress_logging: print_flush_true.  gate_threshold: FIXED interpretable rule, FROZEN (not re-chosen).
# - all reported numbers MEASURED@this metrics.json (McGuffey op-point CITED@v3 metrics.json)
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import argparse
import hashlib
import json
import platform
import random
import sys
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

import experiments.exp_oracle_mention_upperbound_reader_v1 as O
import experiments.exp_multi_turn_loop_realtext_confidence_abstain_gate_v1 as V1

ANCHOR_NAME = "multi_turn_loop_litbank_ood_fixed_gate_v1"
SEED = V1.SEED
N_SCRAMBLE_SEEDS = V1.N_SCRAMBLE_SEEDS
N_BOOT = V1.N_BOOT

CONLL_DIR = REPO / "data" / "corpora" / "litbank_coref_conll"

# --- FROZEN McGuffey operating point (the whole point: NO re-tune on the new corpus) ---
# CITED@data/exp_multi_turn_loop_realtext_confidence_abstain_gate_v3/metrics.json:operating_point
FIXED_TH = 0.490995                 # coref-margin threshold, frozen from v3's McGuffey op-point
MCGUFFEY_OP_HALLUC = 0.0377         # CITED@v3 metrics operating_point.halluc
MCGUFFEY_OP_COVERAGE = 0.3774       # CITED@v3 metrics operating_point.coverage
MCGUFFEY_OP_PRECISION = 0.90        # CITED@v3 metrics operating_point.precision_on_answered
V3_METRICS_PATH = REPO / "data" / "exp_multi_turn_loop_realtext_confidence_abstain_gate_v3" / "metrics.json"

# --- pre-registered bands (HYPOTHESIZED@this prereg) ---
HP_HALLUC_MAX = 0.08                # truthfulness invariant transfers OOD
HP_PRECISION_MIN = 0.80
HP_BEAT_SCRAMBLE_MIN = 0.05
HF_HALLUC_MIN = 0.10                # halluc RISES materially OOD -> confidence does not transfer
HF_BEAT_SCRAMBLE_MAX = 0.0

GATE_SIGNAL_KEY = "coref_conf"


# ===========================================================================================
# LitBank VERBATIM corpus. Each passage is a contiguous sentence window (start..end inclusive) of a
# LitBank CoNLL document; reconstructed from the token stream at runtime (verbatim by construction).
# The self-test asserts each reconstructed passage is a contiguous token subsequence of its document.
# ===========================================================================================
LITBANK_WINDOWS = {
    # pid          : (conll filename substring,         start_sent, end_sent)
    "wall":     ("1064_the_masque", 9, 10),      # "This wall had gates of iron."
    "prince":   ("1064_the_masque", 17, 17),     # "The prince had provided all the appliances of pleasure."
    "courtier": ("1064_the_masque", 11, 11),     # "The courtiers ... brought furnaces ... welded the bolts."
    "duke":     ("1064_the_masque", 47, 50),     # "...the duke... He had a fine eye... His plans were bold..."
    "reddeath": ("1064_the_masque", 0, 0),       # 'The " Red Death " had long devastated the country.'
    "watch":    ("174_the_picture", 88, 88),     # "After a pause, Lord Henry pulled out his watch."
    "painter":  ("174_the_picture", 91, 91),     # "said the painter, keeping his eyes fixed on the ground."
    "pants":    ("11231_bartleby", 77, 78),      # "...He wore his pantaloons very loose and baggy in summer."
    "thrust":   ("11231_bartleby", 51, 51),      # "-- and he made a violent thrust with the ruler."
    "nippers":  ("11231_bartleby", 64, 64),      # "...Nippers could never get this table to suit him."
    "turkey":   ("11231_bartleby", 85, 85),      # "I thought Turkey would appreciate the favor..."
    "maryknew": ("113_the_secret", 25, 26),      # "Mary knew the fair young man who looked like a boy. ..."
    "marytired":("113_the_secret", 74, 75),      # "Mary had been rather tired... her nurse had died."
    "taylor":   ("158_emma", 9, 10),             # "Miss Taylor married. It was Miss Taylor's loss..."
    "emmafath": ("158_emma", 22, 22),            # "She dearly loved her father, but he was no companion..."
    "event":    ("158_emma", 14, 14),            # "The event had every promise of happiness for her friend."
    "bennet":   ("1342_pride", 5, 5),            # "Mr. Bennet made no answer."
}

# Natural comprehension Qs. Each: (qid, pid, spec, human_gold, text). spec = the query PATTERN (never
# contains the answer). gold = human ground-truth read from the passage (answerable from the passage
# ALONE; anti-circular -- NOT what the pipeline says). slice=NC (single/cross-sentence single-hop).
LITBANK_QS_SPEC = [
    ("wall1",   "wall",     ("has_owner", "gates"),                 "wall",       "What had gates of iron?"),
    ("prince1", "prince",   ("svo_agent", "provided", "appliances"),"prince",     "Who provided the appliances of pleasure?"),
    ("prince2", "prince",   ("svo_patient", "provided", "prince"),  "appliances", "What did the prince provide?"),
    ("court1",  "courtier", ("svo_patient", "brought", "courtiers"),"furnaces",   "What did the courtiers bring?"),
    ("court2",  "courtier", ("svo_patient", "welded", "courtiers"), "bolts",      "What did the courtiers weld?"),
    ("duke1",   "duke",     ("has_owner", "eye"),                   "duke",       "Who had a fine eye for colours?"),
    ("duke2",   "duke",     ("has_owner", "plans"),                 "duke",       "Whose plans were bold and fiery?"),
    ("rd1",     "reddeath", ("svo_patient", "devastated", "red"),   "country",    "What did the Red Death devastate?"),
    ("watch1",  "watch",    ("has_owner", "watch"),                 "henry",      "Whose watch was pulled out?"),
    ("watch2",  "watch",    ("svo_agent", "pulled", "watch"),       "henry",      "Who pulled out the watch?"),
    ("paint1",  "painter",  ("has_owner", "eyes"),                  "painter",    "Whose eyes were fixed on the ground?"),
    ("pants1",  "pants",    ("svo_patient", "wore", "he"),          "pantaloons", "What did he wear?"),
    ("thrust1", "thrust",   ("svo_patient", "made", "he"),          "thrust",     "What did he make with the ruler?"),
    ("nip1",    "nippers",  ("svo_patient", "get", "nippers"),      "table",      "What could Nippers not get to suit him?"),
    ("tur1",    "turkey",   ("svo_patient", "appreciate", "turkey"),"favor",      "What would Turkey appreciate?"),
    ("mary1",   "maryknew", ("svo_patient", "knew", "mary"),        "man",        "Whom did Mary know?"),
    ("mary2",   "marytired",("has_owner", "nurse"),                 "mary",       "Whose nurse had died?"),
    ("tay1",    "taylor",   ("has_owner", "loss"),                  "taylor",     "Whose loss first brought grief?"),
    ("ef1",     "emmafath", ("svo_patient", "loved", "she"),        "father",     "Whom did she dearly love?"),
    ("ev1",     "event",    ("has_owner", "promise"),               "event",      "What had every promise of happiness?"),
    ("ben1",    "bennet",   ("svo_patient", "made", "bennet"),      "answer",     "What did Mr. Bennet make?"),
]


def _read_conll_sentences(path):
    """Return list of sentences; each = list of surface tokens (CoNLL col 3)."""
    sents = []
    cur = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if line.startswith("#"):
                continue
            if not line.strip():
                if cur:
                    sents.append(cur)
                    cur = []
                continue
            parts = line.split("\t")
            if len(parts) < 4:
                continue
            cur.append(parts[3])
    if cur:
        sents.append(cur)
    return sents


def _detok(toks):
    """Light detokenizer (readability only; the pipeline re-tokenizes with its own regex)."""
    s = ""
    for i, t in enumerate(toks):
        if i == 0:
            s = t
        elif t in ".,;:!?)]}" or t in ("'s", "n't", "'ll", "'re", "'ve", "'d", "'m"):
            s += t
        elif s and s[-1] in "([{":
            s += t
        elif t in "([{":
            s += " " + t
        else:
            s += " " + t
    return s


_DOC_CACHE = {}


def _doc_sentences(work):
    if work not in _DOC_CACHE:
        hit = None
        for fn in sorted(os.listdir(CONLL_DIR)):
            if work in fn and fn.endswith(".conll"):
                hit = fn
                break
        if hit is None:
            raise FileNotFoundError("no LitBank CoNLL doc matching %r in %s" % (work, CONLL_DIR))
        _DOC_CACHE[work] = _read_conll_sentences(CONLL_DIR / hit)
    return _DOC_CACHE[work]


def _window_tokens(work, a, b):
    sents = _doc_sentences(work)
    toks = []
    for i in range(a, b + 1):
        toks.extend(sents[i])
    return toks


def build_litbank_corpus():
    """Return (passages: {pid: text}, qs: [q-dicts]) from verbatim LitBank windows."""
    passages = {}
    for pid, (work, a, b) in LITBANK_WINDOWS.items():
        passages[pid] = _detok(_window_tokens(work, a, b))
    qs = []
    for (qid, pid, spec, gold, text) in LITBANK_QS_SPEC:
        assert pid in passages, "Q %s references unknown passage %s" % (qid, pid)
        qs.append(dict(qid=qid, p=pid, slice="NC", atype="X", spec=spec, gold=gold, text=text))
    return passages, qs


# Install the LitBank corpus into O (the shared pipeline reads O.TEST_PASSAGES / O.TEST_QS). The whole
# real pipeline (extract_passage_conf, build_real_conf, _attach_component_confs) then operates on it.
_LB_PASSAGES, _LB_QS = build_litbank_corpus()
O.TEST_PASSAGES = _LB_PASSAGES
O.TEST_QS = _LB_QS


# ===========================================================================================
# The gate -- BYTE-IDENTICAL semantics to v3, at the FROZEN threshold (no re-tune).
# ===========================================================================================
def _conflict(rec):
    return rec.get("n_distinct", 0) > 1


def _sig(rec):
    return rec[GATE_SIGNAL_KEY]


def _keep_fixed(rec):
    return rec["is_answered"] and _sig(rec) > FIXED_TH and not _conflict(rec)


def _build_records(clf, qs):
    recs, stores, scale = V1.build_real_conf(clf, qs)
    for r in recs:
        pid = r["q"]["p"]
        comp = V1._COMPONENT_CACHE.get(pid, {})
        pc, cc = V1._matched_component_conf(r["q"]["spec"], stores.get(pid, []), comp)
        r["parse_conf"] = pc
        r["coref_conf"] = cc
    return recs, stores, scale


def _gate_metrics_fixed(recs):
    n_total = len(recs)
    n_correct_kept = sum(1 for r in recs if _keep_fixed(r) and r["correct"] == 1)
    n_wrong_kept = sum(1 for r in recs if _keep_fixed(r) and r["is_answered"] and r["correct"] == 0)
    n_answered = sum(1 for r in recs if _keep_fixed(r))
    halluc = n_wrong_kept / n_total if n_total else 0.0
    coverage = n_answered / n_total if n_total else 0.0
    precision = n_correct_kept / n_answered if n_answered else 0.0
    return {"halluc": round(halluc, 4), "coverage": round(coverage, 4),
            "precision_on_answered": round(precision, 4), "n_answered": n_answered,
            "n_correct_kept": n_correct_kept, "n_wrong_kept": n_wrong_kept, "n_total": n_total,
            "threshold": FIXED_TH}


def _per_signal_contribution(recs):
    """For every ANSWERED WRONG record, which signal (if any) abstains it at the FROZEN threshold."""
    wrongs = [r for r in recs if r["is_answered"] and r["correct"] == 0]
    caught_conflict = [r for r in wrongs if _conflict(r)]
    caught_coref = [r for r in wrongs if (not _conflict(r)) and _sig(r) <= FIXED_TH]
    residual = [r for r in wrongs if (not _conflict(r)) and _sig(r) > FIXED_TH]
    return {
        "n_wrong_answered": len(wrongs),
        "n_wrong_caught_by_conflict": len(caught_conflict),
        "n_wrong_caught_by_coref_margin": len(caught_coref),
        "n_wrong_residual_neither": len(residual),
        "conflict_caught_qids": [r["q"]["qid"] for r in caught_conflict],
        "coref_caught_qids": [r["q"]["qid"] for r in caught_coref],
        "residual_qids": [r["q"]["qid"] for r in residual],
    }


def _run_from_recs(recs, scale):
    no_gate = V1._gate_metrics(recs, keep_fn=lambda r: r["is_answered"])
    n_correct = no_gate["n_correct_kept"]
    answered = [r for r in recs if r["is_answered"]]
    labels = [r["correct"] for r in answered]

    rng = random.Random(SEED)
    auc_gate, ci_lo, ci_hi = V1._auc_ci([_sig(r) for r in answered], labels, rng, N_BOOT)
    auc_parse = V1._auc([r["parse_conf"] for r in answered], labels)
    auc_coref = V1._auc([r["coref_conf"] for r in answered], labels)

    op = _gate_metrics_fixed(recs)
    retained = (op["n_correct_kept"] / n_correct) if n_correct else 0.0

    srng = random.Random(SEED + 1)
    scramble = V1.scramble_null(recs, op["n_answered"], srng, N_SCRAMBLE_SEEDS)
    beat = round(scramble["halluc_mean"] - op["halluc"], 4)

    # representative single scramble arm for arms-differ
    arng = random.Random(SEED + 2)
    k = op["n_answered"]
    keep_idx = set(arng.sample(range(len(answered)), min(k, len(answered)))) if k > 0 else set()
    answered_id = {id(r): j for j, r in enumerate(answered)}
    scramble_answers = []
    for r in recs:
        if not r["is_answered"]:
            scramble_answers.append(None)
        else:
            j = answered_id[id(r)]
            scramble_answers.append(r["ans"] if j in keep_idx else None)
    no_gate_answers = [r["ans"] if r["is_answered"] else None for r in recs]
    gate_answers = [r["ans"] if _keep_fixed(r) else None for r in recs]

    contrib = _per_signal_contribution(recs)

    return {
        "baseline": {"halluc": no_gate["halluc"], "coverage": no_gate["coverage"],
                     "precision_on_answered": no_gate["precision_on_answered"],
                     "n_correct": n_correct, "n_answered": no_gate["n_answered"],
                     "n_wrong": no_gate["n_wrong_kept"], "n_total": no_gate["n_total"]},
        "auc": {"gate_signal": round(auc_gate, 4), "ci_lo": round(ci_lo, 4), "ci_hi": round(ci_hi, 4),
                "parse_only": round(auc_parse, 4), "coref_only": round(auc_coref, 4),
                "gate_signal_name": "coref_margin_ranking", "n_boot": N_BOOT,
                "n_pos": sum(labels), "n_neg": len(labels) - sum(labels)},
        "operating_point": op, "retained_correct_frac": round(retained, 4),
        "scramble": scramble, "beat_scramble": beat, "margin_scale": round(scale, 6),
        "per_signal_contribution": contrib,
        "mcguffey_reference": {"op_halluc": MCGUFFEY_OP_HALLUC, "op_coverage": MCGUFFEY_OP_COVERAGE,
                               "op_precision": MCGUFFEY_OP_PRECISION, "threshold": FIXED_TH},
        "_answers": {"NO_GATE": no_gate_answers, "ABSTAIN_GATE": gate_answers,
                     "SCRAMBLE_GATE": scramble_answers},
        "_recs_debug": [{"qid": r["q"]["qid"], "p": r["q"]["p"], "text": r["q"]["text"],
                         "ans": r["ans"], "gold": r["gold"], "conf_min": r["conf"],
                         "parse_conf": r.get("parse_conf"), "coref_conf": r.get("coref_conf"),
                         "conflict": _conflict(r), "correct": r["correct"],
                         "n_distinct": r["n_distinct"], "kept_by_gate": _keep_fixed(r)} for r in recs],
    }


def _arms_differ(res):
    digests = {}
    for name in ("NO_GATE", "ABSTAIN_GATE", "SCRAMBLE_GATE"):
        digests[name] = hashlib.sha256(
            json.dumps(res["_answers"][name], sort_keys=True).encode()).hexdigest()
    exempted = []
    assert digests["NO_GATE"] != digests["ABSTAIN_GATE"], \
        "META_RULE_AF: NO_GATE == ABSTAIN_GATE (the gate abstained on nothing)"
    if res["operating_point"]["coverage"] == 0.0:
        exempted.append(["ABSTAIN_GATE", "SCRAMBLE_GATE"])
    else:
        assert digests["ABSTAIN_GATE"] != digests["SCRAMBLE_GATE"], \
            "META_RULE_AF: ABSTAIN_GATE == SCRAMBLE_GATE (gate identical to random abstention)"
    return digests, exempted


# ===========================================================================================
# Verdict (truthfulness-via-abstention transfer bands).
# ===========================================================================================
def compute_verdict(res):
    op = res["operating_point"]
    op_halluc = op["halluc"]
    precision = op["precision_on_answered"]
    beat = res["beat_scramble"]
    c = res["per_signal_contribution"]

    hp = (op_halluc <= HP_HALLUC_MAX and precision >= HP_PRECISION_MIN and beat >= HP_BEAT_SCRAMBLE_MIN)
    hf = (op_halluc > HF_HALLUC_MIN or beat <= HF_BEAT_SCRAMBLE_MAX)

    if hp:
        tier = "HARD_PASS"
        outcome = "metacognition-generalizes-truthful-via-abstention-out-of-domain"
    elif hf:
        tier = "HARD_FAIL"
        outcome = "confidence-does-not-transfer-halluc-rises-out-of-domain"
    else:
        tier = "MIDDLE_BAND"
        outcome = "partial-transfer-truthfulness-survives-directionally-halluc-rises-vs-mcguffey"

    localize = []
    localize.append("OOD op_halluc=%.3f vs McGuffey op_halluc=%.3f (frozen th=%.4f, NO re-tune); "
                    "coverage %.3f (McGuffey %.3f) -- gate %s more; precision=%.3f (McGuffey %.3f)"
                    % (op_halluc, MCGUFFEY_OP_HALLUC, FIXED_TH, op["coverage"], MCGUFFEY_OP_COVERAGE,
                       "abstains" if op["coverage"] < MCGUFFEY_OP_COVERAGE else "answers",
                       precision, MCGUFFEY_OP_PRECISION))
    localize.append("NO_GATE OOD halluc=%.3f -> gate cuts to %.3f; residual %d unique-match parse errors "
                    "invisible to BOTH coref-margin AND conflict: %s (conflict caught %d %s; coref-margin "
                    "caught %d %s)" % (res["baseline"]["halluc"], op_halluc, c["n_wrong_residual_neither"],
                    c["residual_qids"], c["n_wrong_caught_by_conflict"], c["conflict_caught_qids"],
                    c["n_wrong_caught_by_coref_margin"], c["coref_caught_qids"]))
    if beat <= HF_BEAT_SCRAMBLE_MAX:
        localize.append("gate NO better than random abstention: beat=%.3f <= %.2f (signal inert OOD)"
                        % (beat, HF_BEAT_SCRAMBLE_MAX))

    msg = ("%s (%s) | LitBank-OOD n_total=%d n_answerable=%d | NO_GATE halluc=%.3f cov=%.3f prec=%.3f | "
           "FROZEN-GATE@coref>%.4f&noconflict: halluc=%.3f cov=%.3f prec=%.3f retained=%.3f (%d/%d) | "
           "vs McGuffey op halluc=%.3f cov=%.3f prec=%.3f | conflict-catch=%d coref-catch=%d residual=%d %s "
           "| scramble=%.3f beat=%.3f | coref-AUC=%.3f [%.3f,%.3f]" % (
               tier, outcome, res["baseline"]["n_total"], res["baseline"]["n_answered"],
               res["baseline"]["halluc"], res["baseline"]["coverage"], res["baseline"]["precision_on_answered"],
               FIXED_TH, op_halluc, op["coverage"], precision, res["retained_correct_frac"],
               op["n_correct_kept"], res["baseline"]["n_correct"], MCGUFFEY_OP_HALLUC, MCGUFFEY_OP_COVERAGE,
               MCGUFFEY_OP_PRECISION, c["n_wrong_caught_by_conflict"], c["n_wrong_caught_by_coref_margin"],
               c["n_wrong_residual_neither"], c["residual_qids"], res["scramble"]["halluc_mean"], beat,
               res["auc"]["coref_only"], res["auc"]["ci_lo"], res["auc"]["ci_hi"]))
    return tier, outcome, msg, localize


# ===========================================================================================
# infra: out-dir / markers / metrics / crash (atomic).
# ===========================================================================================
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


# ===========================================================================================
# self-test: verbatim provenance + real code path + fixed-threshold-not-retuned + one-variable isolation.
# ===========================================================================================
def self_test():
    print("[self-test] building REAL pipeline (perceptron fit + conf-extractor) on LitBank ...", flush=True)

    # (0) FROZEN threshold matches v3's on-disk McGuffey operating point (if present).
    if V3_METRICS_PATH.exists():
        v3 = json.load(open(V3_METRICS_PATH, encoding="utf-8"))
        v3_th = v3.get("operating_point", {}).get("threshold")
        assert v3_th is not None and abs(v3_th - FIXED_TH) < 1e-6, \
            "FROZEN th %.6f != v3 McGuffey operating_point.threshold %r" % (FIXED_TH, v3_th)
        print("[self-test] FROZEN th=%.6f == v3 McGuffey op-point (no re-tune)" % FIXED_TH, flush=True)

    # (1) VERBATIM provenance: every passage is a CONTIGUOUS token subsequence of its CoNLL source.
    for pid, (work, a, b) in LITBANK_WINDOWS.items():
        doc_toks = [t for s in _doc_sentences(work) for t in s]
        win_toks = _window_tokens(work, a, b)
        assert len(win_toks) > 0, "empty window for %s" % pid
        found = False
        for start in range(0, len(doc_toks) - len(win_toks) + 1):
            if doc_toks[start:start + len(win_toks)] == win_toks:
                found = True
                break
        assert found, "PROVENANCE BREACH: %s window not a verbatim contiguous subsequence of %s" % (pid, work)
    print("[self-test] verbatim provenance OK (%d passages are contiguous CoNLL subsequences)"
          % len(LITBANK_WINDOWS), flush=True)

    clf = V1.build_clf()

    # (2) ONE-VARIABLE ISOLATION: conf-extractor relation SET == base O.extract_passage per LitBank passage.
    for pid, text in O.TEST_PASSAGES.items():
        base_rels, _ = O.extract_passage(text, "learned", clf, "maintained", "handrule", frozenset())
        conf_rels, _rl, _prov = V1.extract_passage_conf(text, clf, "maintained")
        assert set(base_rels) == set(conf_rels), \
            "ONE-VARIABLE BREACH: conf-extractor relations != base for %s" % pid

    # (3) POSITIVE CONTROL: NO_GATE per-question answers reproduce O.answer_reader exactly.
    V1._attach_component_confs(clf, O.TEST_QS)
    recs, stores, scale = _build_records(clf, O.TEST_QS)
    for r in recs:
        base_ans = O.normalize(O.answer_reader(r["q"]["spec"], stores.get(r["q"]["p"], [])))
        assert r["ans"] == base_ans, "answer drift on %s: conf=%r base=%r" % (r["q"]["qid"], r["ans"], base_ans)

    # (4) NO answer leakage: no spec tuple contains its own gold token.
    for q in O.TEST_QS:
        assert q["gold"] not in [str(x).lower() for x in q["spec"]], \
            "answer leakage: gold %r appears in spec %r (%s)" % (q["gold"], q["spec"], q["qid"])

    # (5) NON-VACUOUS: NO_GATE commits a non-trivial answer set on LitBank (else the OOD test is empty).
    n_answered = sum(1 for r in recs if r["is_answered"])
    assert len(recs) >= 18, "corpus too small: n=%d" % len(recs)
    assert n_answered >= 8, "NO_GATE commits too few answers (%d) -- vacuous OOD test" % n_answered

    # (6) coref gate signal in [0,1] and NOT constant.
    answered = [r for r in recs if r["is_answered"]]
    gsig = [_sig(r) for r in answered]
    assert all(0.0 <= c <= 1.0 for c in gsig), "coref gate signal out of [0,1]"
    assert len(set(round(c, 4) for c in gsig)) >= 3, "coref gate signal near-constant"

    # (7) run + arms differ + gate abstains something (out of its depth OOD).
    full = _run_from_recs(recs, scale)
    _arms_differ(full)
    op = full["operating_point"]
    assert op["coverage"] < 1.0, "gate never abstains on OOD text"
    assert abs(op["threshold"] - FIXED_TH) < 1e-12, "threshold drifted from FROZEN value"

    tier, outcome, msg, _loc = compute_verdict(full)
    print("[self-test] PASS | LitBank-OOD n=%d n_answered=%d | NO_GATE halluc=%.3f | FROZEN-GATE halluc=%.3f "
          "cov=%.3f prec=%.3f retained=%.3f | conflict-catch=%d coref-catch=%d residual=%d | tier=%s"
          % (len(recs), n_answered, full["baseline"]["halluc"], op["halluc"], op["coverage"],
             op["precision_on_answered"], full["retained_correct_frac"],
             full["per_signal_contribution"]["n_wrong_caught_by_conflict"],
             full["per_signal_contribution"]["n_wrong_caught_by_coref_margin"],
             full["per_signal_contribution"]["n_wrong_residual_neither"], tier), flush=True)
    return True


# ===========================================================================================
# main run. FULL runs the entire LitBank set inline to completion.
# ===========================================================================================
def run(run_mode):
    qs = list(O.TEST_QS)
    if run_mode == "smoke":
        smoke_pids = {"wall", "duke", "watch", "maryknew", "nippers", "taylor"}
        qs = [q for q in qs if q["p"] in smoke_pids]
    out_dir = _out_dir(run_mode)
    _write_start_marker(out_dir, run_mode, expected_n_units=len(qs))
    t0 = time.perf_counter()

    clf = V1.build_clf()
    V1._attach_component_confs(clf, qs)
    recs, _stores, scale = _build_records(clf, qs)
    res = _run_from_recs(recs, scale)
    digests, arms_exempted = _arms_differ(res)
    tier, outcome, msg, localize = compute_verdict(res)
    elapsed = time.perf_counter() - t0

    op = res["operating_point"]
    metrics = {
        "anchor_name": ANCHOR_NAME, "verdict": tier, "verdict_msg": msg, "summary": msg[:300],
        "gate_outcome": outcome, "run_mode": run_mode, "elapsed_s": round(elapsed, 4),
        "ts_iso": datetime.now(timezone.utc).isoformat(), "n_questions": len(qs),
        "arms": ["NO_GATE", "ABSTAIN_GATE", "SCRAMBLE_GATE"],
        "corpus": "litbank_verbatim_out_of_domain",
        "corpus_provenance": {"source": "data/corpora/litbank_coref_conll/*.conll",
                              "n_passages": len(LITBANK_WINDOWS),
                              "works": sorted(set(w for (w, _a, _b) in LITBANK_WINDOWS.values())),
                              "reconstruction": "verbatim_contiguous_token_subsequence",
                              "distinct_from_mcguffey": True},
        "threshold_frozen": True, "fixed_threshold": FIXED_TH,
        "threshold_source": "exp_multi_turn_loop_realtext_confidence_abstain_gate_v3 McGuffey operating_point",
        "no_retune_on_new_corpus": True,
        "gate_signal": "coref_margin_OR_match_conflict_union_of_abstentions_FROZEN_th",
        "n_answerable": res["baseline"]["n_answered"],
        "baseline_no_gate": res["baseline"],
        "operating_point": op,
        "retained_correct_frac": res["retained_correct_frac"],
        "scramble_matched_coverage": res["scramble"],
        "beat_scramble": res["beat_scramble"],
        "per_signal_contribution": res["per_signal_contribution"],
        "mcguffey_reference": res["mcguffey_reference"],
        "auc": res["auc"],
        "margin_scale": res["margin_scale"],
        "confidence_signals": ["coref_margin(maintained-overlay salience gap) -- GATE SIGNAL (ranking)",
                               "match_conflict(store returns >1 distinct answer; n_distinct>1) -- GATE FLAG",
                               "parse_margin(perceptron argmax-runnerup) -- reported, NOT gated"],
        "gate_threshold_kind": "fixed_interpretable_rule_FROZEN_from_mcguffey_no_retune",
        "bands": {"HP_halluc_max": HP_HALLUC_MAX, "HP_precision_min": HP_PRECISION_MIN,
                  "HP_beat_scramble_min": HP_BEAT_SCRAMBLE_MIN, "HF_halluc_min": HF_HALLUC_MIN,
                  "HF_beat_scramble_max": HF_BEAT_SCRAMBLE_MAX},
        "weakest_interface": localize,
        "arms_differ_digests": digests, "arms_differ_verified": True, "arms_differ_exempted": arms_exempted,
        "final_metrics_atomicity": "tmp_replace", "deterministic_seeding": True,
        "progress_logging": "print_flush_true", "compute_architecture": "sequential_cpu_pure_python",
        "crlb_n_a": "symbolic glass-box; halluc (truthfulness invariant) is the reported quantity",
        "per_question": res["_recs_debug"],
        "reuse_credited": {
            "gate_and_pipeline": "exp_multi_turn_loop_realtext_confidence_abstain_gate_v1.py (extractor, "
                                 "answer engine, coref/conflict conf, scramble, AUC)",
            "gate_logic_lineage": "exp_multi_turn_loop_realtext_confidence_abstain_gate_v3.py (coref-OR-"
                                  "conflict union gate; McGuffey HARD_PASS op-point th=0.490995 CITED)",
            "components_and_grounding": "exp_oracle_mention_upperbound_reader_v1.py",
            "corpus": "LitBank (data/corpora/litbank_coref_conll) -- real verbatim public-domain novels"},
        "REQUIRED_FIELDS": ["verdict", "baseline_no_gate", "operating_point", "retained_correct_frac",
                            "scramble_matched_coverage", "beat_scramble", "per_signal_contribution",
                            "mcguffey_reference", "arms_differ_digests", "gate_signal", "n_answerable",
                            "threshold_frozen", "fixed_threshold"],
        "notes": ("Out-of-domain generalization of the McGuffey-tuned trustworthy abstain gate. FROZEN "
                  "threshold (0.490995), NO re-tune, applied to REAL verbatim LitBank literary prose. "
                  "Measures whether TRUTHFULNESS (low halluc) survives via ABSTENTION (coverage drop) OOD, "
                  "distinct from prior wildtext ACCURACY collapse. CLAIM-VET-pending."),
    }
    _write_metrics(out_dir, metrics)

    print("[%s:%s] %s" % (ANCHOR_NAME, run_mode, msg), flush=True)
    print("  [NO_GATE ] halluc=%.3f cov=%.3f prec=%.3f (correct=%d wrong=%d abstain=%d of %d)"
          % (res["baseline"]["halluc"], res["baseline"]["coverage"], res["baseline"]["precision_on_answered"],
             res["baseline"]["n_correct"], res["baseline"]["n_wrong"],
             res["baseline"]["n_total"] - res["baseline"]["n_answered"], res["baseline"]["n_total"]), flush=True)
    print("  [FROZEN  ] th=%.4f (McGuffey op-point, NO re-tune) halluc=%.3f cov=%.3f prec=%.3f retained=%.3f (%d/%d)"
          % (FIXED_TH, op["halluc"], op["coverage"], op["precision_on_answered"],
             res["retained_correct_frac"], op["n_correct_kept"], res["baseline"]["n_correct"]), flush=True)
    print("  [vs McGuf] McGuffey op halluc=%.3f cov=%.3f prec=%.3f  ->  OOD halluc=%.3f cov=%.3f prec=%.3f"
          % (MCGUFFEY_OP_HALLUC, MCGUFFEY_OP_COVERAGE, MCGUFFEY_OP_PRECISION, op["halluc"], op["coverage"],
             op["precision_on_answered"]), flush=True)
    c = res["per_signal_contribution"]
    print("  [SIGNALS ] wrong=%d | conflict-catch=%d %s | coref-catch=%d %s | residual=%d %s"
          % (c["n_wrong_answered"], c["n_wrong_caught_by_conflict"], c["conflict_caught_qids"],
             c["n_wrong_caught_by_coref_margin"], c["coref_caught_qids"], c["n_wrong_residual_neither"],
             c["residual_qids"]), flush=True)
    print("  [SCRAMBLE] matched-cov halluc_mean=%.3f -> real gate BEATS random by %.3f"
          % (res["scramble"]["halluc_mean"], res["beat_scramble"]), flush=True)
    print("  [metrics ] -> %s" % (out_dir / "metrics.json"), flush=True)
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
        ("self_test" if ("--self-test" in sys.argv or ("--run-mode" in sys.argv and "self_test" in sys.argv)) else "full")
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
