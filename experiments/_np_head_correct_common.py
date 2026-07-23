"""_np_head_correct_common -- shared CORRECT-TO-HEAD gate logic for the trustworthy-reader completion.

The 29467 pair (McGuffey exp_multi_turn_loop_realtext_nphead_gate_v1 + LitBank
exp_multi_turn_loop_litbank_ood_nphead_gate_v1) ABSTAINS when the reader's answer is an NP pre-modifier
(a non-head: "log" for "log house", "lord" for "Lord Henry", "fair" for "the fair young man"). The capstone
established that in ALL flagged cases the RECOVERED HEAD == the gold answer (log->house, lord->henry,
fair->man). So instead of abstaining on an NP-head-flagged non-head, RETURN THE NP HEAD as the answer:
turn abstentions into (correct) answers, raising coverage while keeping hallucination at zero.

ONE new variable vs the 29467 ABSTAIN gate: on NP-head-flagged prior-kept records, abstain -> correct-to-head.

    ABSTAIN (29467): keep = prior_keep AND np_head_consistent      (drop the non-head; no answer)
    CORRECT (this) : keep = prior_keep; on np non-head, REPLACE answer with the recovered NP head
                     (and RECOMPUTE correctness of the substituted answer vs gold)

GENUINE CAN-FAIL (load-bearing): correct-to-head ASSUMES the question is about the HEAD entity. If a
question is genuinely about the MODIFIER ("what KIND of house? -> log"), the head is NOT the gold answer and
correcting introduces a NEW hallucination -> abstain would have been safer. The cell reports, per corpus,
how many corrections are RIGHT (head == gold) vs WRONG (head != gold). n_corrections_wrong >= 1 -> HARD_FAIL.
The head-is-the-answer assumption is thus TESTED on the real gold, not assumed.

ANTI-CHEAT must-fail (SCRAMBLE_CORRECT): on the SAME flagged records, substitute a RANDOM passage noun
instead of the structural head. If a random noun recovered gold as often as the head, the head rule would be
non-load-bearing / the result construction-determined. The head must beat random-noun substitution.

Signals are POS-only + gold-free (np_head_correction reads no gold; correctness is recomputed against gold
only for scoring, exactly as build_real_conf does for the base answer). ASCII-only; pure functions; the base
29467 module (which owns O, FIXED_TH, the record builder and the prior/abstain keep-predicates) is passed in.
"""
from __future__ import annotations

import hashlib
import json
import random
import statistics

import experiments._np_head_signal as NP

# pre-registered bands (identical on both corpora; the completion criterion is corpus-general)
HP_HALLUC_MAX = 0.02        # corrections keep hallucination at (near) zero
HP_PRECISION_MIN = 0.90     # precision-on-answered stays high
HF_HALLUC_MAX_SOFT = 0.05   # correct-to-head clearly worse than the abstain floor
HF_PRECISION_MIN = 0.80


def _corrected(base, r):
    """(eff_ans, eff_correct, corrected_flag) for record r under the CORRECT-TO-HEAD policy.
      not prior-kept          -> (None, 0, False)   the prior gate abstains anyway
      prior-kept, np-head-ok   -> (ans, correct, False)   unchanged
      prior-kept, np non-head:
         head recoverable      -> (head, 1 if head==gold else 0, True)   the CORRECTION
         head not recoverable  -> (None, 0, False)   cannot correct -> abstain (matches ABSTAIN)
    Correctness is recomputed against the SAME normalized gold build_real_conf uses (no leakage: the head
    itself is recovered by np_head_correction with no view of gold)."""
    if not base._prior_keep(r):
        return None, 0, False
    if base._np_ok(r):
        return r["ans"], r["correct"], False
    corr = r["np_correction"]
    if corr is None:
        return None, 0, False
    eff = base.O.normalize(corr)
    return eff, (1 if eff == r["gold"] else 0), True


def _correct_map(base, recs):
    return {id(r): _corrected(base, r) for r in recs}


def _abstain_metrics(base, recs):
    """29467 ABSTAIN operating point (positive control / the coverage-comparison baseline)."""
    return base._gate_metrics(recs, keep_fn=base._new_keep)


def _correct_gate_metrics(base, recs, cmap):
    n_total = len(recs)
    kept = [r for r in recs if cmap[id(r)][0] is not None]
    n_answered = len(kept)
    n_correct_kept = sum(1 for r in kept if cmap[id(r)][1] == 1)
    n_wrong_kept = n_answered - n_correct_kept
    halluc = n_wrong_kept / n_total if n_total else 0.0
    coverage = n_answered / n_total if n_total else 0.0
    precision = n_correct_kept / n_answered if n_answered else 0.0
    return {"halluc": round(halluc, 4), "coverage": round(coverage, 4),
            "precision_on_answered": round(precision, 4), "n_answered": n_answered,
            "n_correct_kept": n_correct_kept, "n_wrong_kept": n_wrong_kept, "n_total": n_total,
            "threshold": base.FIXED_TH}


def _correction_audit(base, recs, cmap):
    """RIGHT vs WRONG breakdown of every correct-to-head substitution -- the genuine can-fail evidence."""
    corrected = [r for r in recs if cmap[id(r)][2]]
    right = [r for r in corrected if cmap[id(r)][1] == 1]
    wrong = [r for r in corrected if cmap[id(r)][1] == 0]
    return {
        "n_corrected": len(corrected),
        "n_corrections_right": len(right),
        "n_corrections_wrong": len(wrong),
        "corrected_qids": [r["q"]["qid"] for r in corrected],
        "wrong_correction_qids": [r["q"]["qid"] for r in wrong],
        "corrections": {r["q"]["qid"]: {"orig_ans": r["ans"], "head": base.O.normalize(r["np_correction"]),
                                        "gold": r["gold"], "head_eq_gold": cmap[id(r)][1] == 1}
                        for r in corrected},
        "head_is_answer_assumption_holds": len(wrong) == 0 and len(corrected) >= 1,
    }


def _passage_noun_lows(base, pid):
    O = base.O
    lows = []
    for sent in O.split_sentences(O.TEST_PASSAGES[pid]):
        for _surf, low, pos in O.pos_tag_sentence(sent):
            if pos in NP.NOUN_POS:
                nl = O.normalize(low)
                if nl:
                    lows.append(nl)
    return sorted(set(lows))


def scramble_correct(base, recs, cmap, rng, n_seeds):
    """Must-fail: substitute a RANDOM passage noun (not the head) on the SAME flagged records; matched
    coverage. Head must beat this (else head-selection is non-load-bearing / construction-determined)."""
    n_total = len(recs)
    fixed_kept = [r for r in recs if cmap[id(r)][0] is not None and not cmap[id(r)][2]]
    corrected = [r for r in recs if cmap[id(r)][2]]
    n_kept = len(fixed_kept) + len(corrected)
    base_wrong = sum(1 for r in fixed_kept if cmap[id(r)][1] == 0)
    cand = {id(r): [c for c in _passage_noun_lows(base, r["q"]["p"]) if c != r["ans"]] for r in corrected}
    halls, precs = [], []
    for _s in range(n_seeds):
        w = base_wrong
        for r in corrected:
            cs = cand[id(r)]
            pick = cs[rng.randrange(len(cs))] if cs else r["ans"]
            if base.O.normalize(pick) != r["gold"]:
                w += 1
        halls.append(w / n_total if n_total else 0.0)
        precs.append((n_kept - w) / n_kept if n_kept else 0.0)
    return {"halluc_mean": round(statistics.mean(halls), 4),
            "halluc_p95": round(sorted(halls)[int(0.95 * len(halls)) - 1], 4) if halls else 0.0,
            "precision_mean": round(statistics.mean(precs), 4), "n_kept": n_kept, "n_seeds": n_seeds}


def run_correct(base, recs, scale):
    O = base.O
    cmap = _correct_map(base, recs)

    no_gate = base._gate_metrics(recs, keep_fn=lambda r: r["is_answered"])
    n_correct = no_gate["n_correct_kept"]
    prior = base._gate_metrics(recs, keep_fn=base._prior_keep)
    abstain = _abstain_metrics(base, recs)
    correct = _correct_gate_metrics(base, recs, cmap)

    audit = _correction_audit(base, recs, cmap)
    coverage_rise = round(correct["coverage"] - abstain["coverage"], 4)
    n_recovered = correct["n_answered"] - abstain["n_answered"]

    srng = random.Random(base.SEED + 3)
    scramble = scramble_correct(base, recs, cmap, srng, base.N_SCRAMBLE_SEEDS)
    beat_scramble = round(scramble["halluc_mean"] - correct["halluc"], 4)

    no_gate_answers = [r["ans"] if r["is_answered"] else None for r in recs]
    prior_answers = [r["ans"] if base._prior_keep(r) else None for r in recs]
    abstain_answers = [r["ans"] if base._new_keep(r) else None for r in recs]
    correct_answers = [cmap[id(r)][0] for r in recs]

    return {
        "baseline": {"halluc": no_gate["halluc"], "coverage": no_gate["coverage"],
                     "precision_on_answered": no_gate["precision_on_answered"], "n_correct": n_correct,
                     "n_answered": no_gate["n_answered"], "n_wrong": no_gate["n_wrong_kept"],
                     "n_total": no_gate["n_total"]},
        "prior_gate": prior,
        "abstain_gate": abstain,                                  # = 29467 operating point
        "operating_point": correct,                              # CORRECT-TO-HEAD (THE mechanism)
        "coverage_rise_vs_abstain": coverage_rise, "n_recovered_to_answer": n_recovered,
        "correction_audit": audit,
        "scramble_random_noun": scramble, "beat_scramble": beat_scramble,
        "margin_scale": round(scale, 6),
        "retained_correct_frac": round((correct["n_correct_kept"] / n_correct) if n_correct else 0.0, 4),
        "_answers": {"NO_GATE": no_gate_answers, "PRIOR_GATE": prior_answers,
                     "ABSTAIN_GATE": abstain_answers, "CORRECT_GATE": correct_answers},
        "_recs_debug": [{"qid": r["q"]["qid"], "p": r["q"]["p"], "orig_ans": r["ans"], "gold": r["gold"],
                         "coref_conf": r.get("coref_conf"), "conflict": base._conflict(r),
                         "np_status": r["np_status"], "np_correction": r["np_correction"],
                         "orig_correct": r["correct"], "prior_kept": base._prior_keep(r),
                         "abstain_kept": base._new_keep(r), "correct_gate_ans": cmap[id(r)][0],
                         "correct_gate_correct": cmap[id(r)][1], "was_corrected": cmap[id(r)][2]}
                        for r in recs],
    }


def arms_differ(res):
    digests = {n: hashlib.sha256(json.dumps(res["_answers"][n], sort_keys=True).encode()).hexdigest()
               for n in ("NO_GATE", "PRIOR_GATE", "ABSTAIN_GATE", "CORRECT_GATE")}
    assert digests["NO_GATE"] != digests["PRIOR_GATE"], "arms: NO_GATE == PRIOR_GATE"
    assert digests["PRIOR_GATE"] != digests["ABSTAIN_GATE"], \
        "arms: ABSTAIN_GATE == PRIOR_GATE (NP-head flagged nothing -- nothing to correct)"
    assert digests["ABSTAIN_GATE"] != digests["CORRECT_GATE"], \
        "arms: CORRECT_GATE == ABSTAIN_GATE (correct-to-head inert -- the one new variable did nothing)"
    return digests


def compute_verdict(base, res, corpus_label):
    op = res["operating_point"]
    op_halluc = op["halluc"]
    precision = op["precision_on_answered"]
    a = res["correction_audit"]
    coverage_rise = res["coverage_rise_vs_abstain"]

    fired = a["n_corrected"] >= 1
    all_corrections_right = a["n_corrections_wrong"] == 0
    coverage_rose = coverage_rise > 0.0

    hp = (fired and coverage_rose and all_corrections_right and op_halluc <= HP_HALLUC_MAX
          and precision >= HP_PRECISION_MIN)
    hf = ((fired and not all_corrections_right)                      # correct-to-head made a NEW error
          or op_halluc > HF_HALLUC_MAX_SOFT
          or precision < HF_PRECISION_MIN
          or (fired and not coverage_rose))

    if hp:
        tier, outcome = "HARD_PASS", "correct-to-head-raises-coverage-clean-corrections-correct-halluc-stays-zero"
    elif hf:
        tier, outcome = "HARD_FAIL", "correct-to-head-introduces-new-errors-or-net-hurts-abstain-safer"
    else:
        tier, outcome = "MIDDLE_BAND", "correct-to-head-partial"

    localize = []
    if fired and not all_corrections_right:
        localize.append("correct-to-head INTRODUCED %d new hallucination(s) (head != gold, question about the "
                        "MODIFIER not the head): %s -> abstain is safer on these"
                        % (a["n_corrections_wrong"], a["wrong_correction_qids"]))
    if not fired:
        localize.append("no NP-head-flagged case in prior-kept -> nothing to correct (mechanism inert here)")
    if fired and not coverage_rose:
        localize.append("coverage did NOT rise vs 29467 abstain (rise=%.4f)" % coverage_rise)
    if not localize:
        localize.append("correct-to-head recovered %d abstention(s) to CORRECT answers %s (head==gold on all); "
                        "coverage %.3f->%.3f (+%.4f), halluc %.4f (abstain %.4f), precision %.3f; head beats "
                        "random-noun by %.3f -- head-is-the-answer assumption HOLDS on all flagged Qs"
                        % (res["n_recovered_to_answer"], a["corrected_qids"], res["abstain_gate"]["coverage"],
                           op["coverage"], coverage_rise, op_halluc, res["abstain_gate"]["halluc"], precision,
                           res["beat_scramble"]))

    msg = ("%s (%s) | %s n_total=%d n_answerable=%d n_correct=%d | NO_GATE halluc=%.3f | "
           "PRIOR halluc=%.4f cov=%.3f | 29467-ABSTAIN halluc=%.4f cov=%.3f | CORRECT-TO-HEAD: halluc=%.4f "
           "cov=%.3f prec=%.3f (coverage +%.4f, %d abstentions->answers) | corrections right=%d wrong=%d %s | "
           "head-vs-random-noun beat=%.3f (scramble halluc=%.3f)" % (
               tier, outcome, corpus_label, res["baseline"]["n_total"], res["baseline"]["n_answered"],
               res["baseline"]["n_correct"], res["baseline"]["halluc"],
               res["prior_gate"]["halluc"], res["prior_gate"]["coverage"],
               res["abstain_gate"]["halluc"], res["abstain_gate"]["coverage"],
               op_halluc, op["coverage"], precision, coverage_rise, res["n_recovered_to_answer"],
               a["n_corrections_right"], a["n_corrections_wrong"], a["wrong_correction_qids"],
               res["beat_scramble"], res["scramble_random_noun"]["halluc_mean"]))
    return tier, outcome, msg, localize


def bands_dict():
    return {"HP_halluc_max": HP_HALLUC_MAX, "HP_precision_min": HP_PRECISION_MIN,
            "HF_halluc_max_soft": HF_HALLUC_MAX_SOFT, "HF_precision_min": HF_PRECISION_MIN,
            "HP_requires": "n_corrected>=1 AND coverage_rise>0 AND n_corrections_wrong==0 AND "
                           "halluc<=HP_halluc_max AND precision>=HP_precision_min",
            "HF_requires": "n_corrections_wrong>=1 (new hallucination) OR halluc>HF_halluc_max_soft OR "
                           "precision<HF_precision_min OR coverage did NOT rise"}
