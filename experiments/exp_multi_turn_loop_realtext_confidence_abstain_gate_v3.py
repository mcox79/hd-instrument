"""exp_multi_turn_loop_realtext_confidence_abstain_gate_v3 -- COREF-OR-CONFLICT trustworthy abstain gate.

FRESH PRE-REGISTERED TEST (not a retro-fit). v2
(exp_multi_turn_loop_realtext_confidence_abstain_gate_v2, HARD_FAIL) gated on the COREF salience margin
ALONE. It HARD_FAILed because THREE confident mis-parses -- N2 (door for mat), N6 (log for house), M11
(cunning for dog) -- are PARSE/MATCH reversals, NOT coref errors: they sit at the coref-margin CEILING
(coref_conf=1.0, no pronoun head), tied with every correct answer, so no coref threshold below 1.0 can
abstain them and the ceiling threshold abstains EVERYTHING (retained_correct -> 0).
  ceiling wrongs MEASURED@data/exp_multi_turn_loop_realtext_confidence_abstain_gate_v2/metrics.json:
    ceiling_analysis.wrong_at_ceiling_qids = ["N2","N6","M11"].

KEY LEVER (pre-registered): 2 of those 3 (N2 n_distinct=2, M11 n_distinct=3) ALREADY trip the
MATCH-CONFLICT CAP -- the store returns MORE THAN ONE distinct answer for the query pattern, i.e. it
disagrees with itself. v1 computes that exact signal (n_distinct>1 -> conf capped 0.15) but v2's
coref-ONLY gate reads coref_conf and is BLIND to it. The real trustworthiness lever is a COHERENCE gate
(Kintsch construction-integration = coherence checking): abstain if the coref salience margin is LOW
*OR* the answer CONFLICTS with the maintained discourse (the store self-disagrees; the match-conflict
cap fires). Combined as a UNION OF ABSTENTIONS -- abstain if EITHER flags -- NOT min(), which drags
coverage. Non-destructive on coverage: the conflict flag removes the ceiling-tied wrongs WITHOUT moving
the coref threshold up, so a LOWER coref threshold becomes feasible and retained_correct RISES.

ONE CONCEPTUAL VARIABLE vs v2: adding the conflict/coherence flag to the coref-margin gate.
  v2: keep = is_answered AND coref_conf > th
  v3: keep = is_answered AND coref_conf > th AND NOT conflict(rec)   [conflict = match-conflict cap]
EVERYTHING ELSE is v1/v2-VERBATIM (imported, not re-typed): same confidence-annotating extractor, same
relation set (byte-identical to base O.extract_passage), same coref salience margin, same conflict cap,
same normalization, same SCRAMBLE matched-coverage anti-cheat, same AUC machinery.

WIDENED CORPUS (the VET's requirement before any MM->CG promotion -- make a HARD_PASS robust, not
small-n): v1/v2 used 31 Qs (21 answered, 8 correct). v3 appends 22 NEW natural reading-comprehension
questions over the SAME 14 REAL VERBATIM McGuffey passages already vetted into the base module
(O.TEST_PASSAGES) -- fidelity guaranteed (reused vetted verbatim text; no fabricated passages). Golds
are human ground-truth read from the passage; correctness is MEASURED by the real pipeline (a Q is
"answerable"/answered iff the pipeline commits an answer; correct iff it matches gold). This lifts the
answered set 21 -> 43 and correct 8 -> 24, materially larger n. NOTE: passage-COUNT widening (new
distinct verbatim passages beyond the vetted 14) is deliberately NOT done here -- it would require a
verified verbatim source pull; flagged as a follow-up. The widening here is purely additional questions
over already-vetted verbatim text, so the FAIR "real verbatim text" property holds cleanly.

ARMS:
  NO_GATE       = REAL pipeline answers everything it matches (positive control; the ORIGINAL-31 subset
                  reproduces the prior 0.4194 halluc / 8 correct exactly -- widening adds Qs, not
                  passages, so original extractions are bit-stable).
  ABSTAIN_GATE  = REAL + coref-OR-conflict gate at the pre-registered operating threshold (lowest coref
                  threshold achieving global halluc <= 0.05 under the union gate). THE MECHANISM.
  SCRAMBLE_GATE = anti-cheat must-fail: matched-coverage RANDOM abstention (answer the same NUMBER of Qs
                  chosen uniformly at random). The real coref-OR-conflict gate must BEAT random.

BANDS (envelope-fail; set BEFORE the run; ON THE WIDENED n; global halluc = wrong-answered / n_total):
  HARD_PASS (trustworthy: zero-ish halluc restored at non-trivial coverage on the widened set, AND the
    conflict flag catches the parse/match-reversal core):
      op_halluc <= 0.05 AND
      retained_correct_frac >= 0.60 AND
      precision_on_answered >= 0.80 AND
      (scramble_halluc - op_halluc) >= 0.10 at matched coverage AND
      auc(coref) >= 0.70 (v1/v2-comparability retained) AND
      n_wrong_caught_by_conflict >= 2 (the conflict flag DOES catch parse/match-reversals).
  HARD_FAIL:
      cannot reach op_halluc <= 0.05 without retained_correct_frac <= 0.25, OR
      n_wrong_caught_by_conflict == 0 (the conflict flag does NOT catch the parse-reversal core), OR
      (scramble_halluc - op_halluc) <= 0.02 (no better than random abstention).
  MIDDLE otherwise.

WHY THIS IS A GENUINE CAN-FAIL (not guaranteed): the conflict flag catches ONLY store-self-disagreement
(n_distinct>1). A parse role-reversal with a UNIQUE store match (n_distinct=1) AND full coref margin --
e.g. N6 (log for house, n_distinct=1, coref=1.0) -- is invisible to BOTH the coref margin AND the
conflict flag. If enough of the widened wrong answers are such unique-match role-reversals, the residual
halluc stays > 0.05 and the gate cannot pass. The conflict flag may NOT catch N6; the data decides.

DESIGN-GATE (verified at self-test): (1) REAL baseline reproduced on the ORIGINAL-31 subset (0.4194,
  n_correct 8); (2) discriminator CAN-FAIL (residual unique-match role-reversals invisible to both
  signals -> honest MIDDLE/HARD_FAIL possible); (3) difficulty ON (real grade-2 syntax, true-MM
  components, unchanged); (4) ONE conceptual variable = adding the conflict flag to the coref gate;
  (5) NO answer leakage (widened Q specs are natural read Qs; gold is human truth, correctness MEASURED);
  (6) ONE-VARIABLE ISOLATION: relation SET byte-identical to base O.extract_passage per passage
  (asserted, all passages); the conflict flag genuinely changes >=1 keep decision at the operating point;
  (7) POSITIVE-CONTROL: NO_GATE answers reproduce O.answer_reader exactly; (8) LOCALIZATION assertion:
  the conflict flag catches N2 and M11 but NOT N6 (the 2-of-3 lever + the acknowledged residual);
  (9) determinism (OMP=1, fixed seed, sorted set, no hash()-seeding; scramble uses random.Random(seed)).

CELL-TEMPLATE (relevant subset; many SCHEMA-VET gates N/A for this non-HD glass-box cell):
# - except SystemExit/KeyboardInterrupt: raise BEFORE except Exception (no BaseException)
# - ATOMIC final metrics write (tmp + os.replace)                 [META_RULE_AH: tmp_replace]
# - ARMS-MUST-DIFFER hash check at run                            [META_RULE_AF]
# - discriminator CAN-FAIL AND FIRES (conflict-catch>=2; residual invisible; beat-scramble)  [design-gate]
# - REAL code path exercised in self-test (perceptron fit + POS tag + WorkingOverlay + conf-extract) [F.1]
# - baseline_in_band: ORIG-31 reproduces 0.4194; gate free to fail (residual role-reversals)     [AG]
# - deterministic (fixed seed, OMP=1, no hash()-seed, sorted(set))               [F.5/PROT-023]
# - multi-seed variance probe on the discriminator: coref-AUC bootstrap CI + K-seed scramble null [META CG]
# - start-marker + crash-diagnostic; heartbeat EXEMPT (wall < 90s)
# - crlb_n/a: symbolic glass-box; coverage-at-zero-halluc ceiling (24/53) IS the feasibility bound
# - progress_logging: print_flush_true.  gate_threshold: FIXED interpretable rule (coref margin > th
#   AND no match-conflict); the full precision/coverage CURVE over coref-margin thresholds is delivered.
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

# v1 supplies ALL building blocks (extractor, answer engine, component-conf attach, metrics helpers,
# AUC, scramble, bands, baseline targets). v2 is cited for lineage. v3 overrides only the gate logic
# (adds the conflict flag) and appends the widened Q-set.
import experiments.exp_multi_turn_loop_realtext_confidence_abstain_gate_v1 as V1

O = V1.O

ANCHOR_NAME = "multi_turn_loop_realtext_confidence_abstain_gate_v3"

# --- reused VERBATIM from v1 ---
SEED = V1.SEED
N_SCRAMBLE_SEEDS = V1.N_SCRAMBLE_SEEDS
N_BOOT = V1.N_BOOT
HP_AUC_MIN = V1.HP_AUC_MIN                      # 0.70 (coref-AUC comparability term)
HP_RETAINED_CORRECT_MIN = V1.HP_RETAINED_CORRECT_MIN   # 0.60
HP_PRECISION_MIN = V1.HP_PRECISION_MIN          # 0.80
HP_HALLUC_MAX = V1.HP_HALLUC_MAX                # 0.05
HP_BEAT_SCRAMBLE_MIN = V1.HP_BEAT_SCRAMBLE_MIN  # 0.10
HF_RETAINED_CORRECT_MAX = V1.HF_RETAINED_CORRECT_MAX   # 0.25
HF_BEAT_SCRAMBLE_MAX = V1.HF_BEAT_SCRAMBLE_MAX  # 0.02
HP_CONFLICT_CATCH_MIN = 2       # the conflict flag must catch >=2 parse/match-reversal wrongs
BASE_HALLUC = V1.BASE_HALLUC
BASE_HALLUC_TOL = V1.BASE_HALLUC_TOL
BASE_N_CORRECT = V1.BASE_N_CORRECT
CROSS_TURN_SLICES = V1.CROSS_TURN_SLICES

GATE_SIGNAL_KEY = "coref_conf"


# ===========================================================================================
# WIDENED CORPUS: 22 NEW natural reading questions over the SAME 14 REAL VERBATIM passages already in
# O.TEST_PASSAGES. Golds are human ground-truth (read from the passage); correctness is MEASURED by the
# real pipeline. Appended to O.TEST_QS at module import (passages unchanged -> original extractions
# bit-stable -> the ORIGINAL-31 baseline is preserved, asserted in self-test). NO answer leakage: specs
# are the natural query patterns; the gold is what the passage actually says, not what the pipeline says.
# ===========================================================================================
WIDENED_QS = [
    {"qid": "W1", "p": "L5_dogs", "slice": "NC", "atype": "PATIENT",
     "spec": ("svo_patient", "uses", "james"), "gold": "sport", "text": "Whom does James use for his horse?"},
    {"qid": "W2", "p": "L5_dogs", "slice": "NC", "atype": "AGENT",
     "spec": ("has_owner", "wagon"), "gold": "james", "text": "Who has a little wagon?"},
    {"qid": "W3", "p": "L18_king", "slice": "NC", "atype": "LOCATION",
     "spec": ("loc_ground", "nest"), "gold": "tree", "text": "Where is the nest?"},
    {"qid": "W4", "p": "L18_king", "slice": "NC", "atype": "AGENT",
     "spec": ("svo_agent", "eats", "flies"), "gold": "kingbird", "text": "Who eats flies?"},
    {"qid": "W5", "p": "L21_bee", "slice": "NC", "atype": "PATIENT",
     "spec": ("svo_patient", "live", "bees"), "gold": "hive", "text": "What is the bees' house called?"},
    {"qid": "W6", "p": "L60_geo", "slice": "NC", "atype": "PATIENT",
     "spec": ("svo_patient", "sent", "ellet"), "gold": "ball", "text": "What did George send?"},
    {"qid": "W7", "p": "L60_geo", "slice": "NC", "atype": "AGENT",
     "spec": ("has_owner", "gift"), "gold": "george", "text": "Who had a gift?"},
    {"qid": "W8", "p": "L32_tiger", "slice": "NC", "atype": "PATIENT",
     "spec": ("svo_patient", "caught", "tigress"), "gold": "kitten", "text": "What did the tigress catch?"},
    {"qid": "W9", "p": "L32_tiger", "slice": "NC", "atype": "PATIENT",
     "spec": ("svo_patient", "bounded", "tigress"), "gold": "tent", "text": "Into what did the tigress bound?"},
    {"qid": "W10", "p": "L14_henry", "slice": "NC", "atype": "AGENT",
     "spec": ("svo_agent", "kind", "boy"), "gold": "henry", "text": "Who was a kind, good boy?"},
    {"qid": "W12", "p": "L8_puss", "slice": "NC", "atype": "PATIENT",
     "spec": ("svo_patient", "lived", "puss"), "gold": "cellar", "text": "Where had Puss lived?"},
    {"qid": "W13", "p": "L8_puss", "slice": "NC", "atype": "AGENT",
     "spec": ("has_owner", "kittens"), "gold": "puss", "text": "Who owns the kittens?"},
    {"qid": "W14", "p": "L23_doll", "slice": "NC", "atype": "AGENT",
     "spec": ("has_owner", "pet"), "gold": "dog", "text": "What kind of animal is Mary's pet?"},
    {"qid": "W15", "p": "L28_sam", "slice": "NC", "atype": "PATIENT",
     "spec": ("svo_patient", "gave", "mother"), "gold": "cents", "text": "What did the mother give?"},
    {"qid": "W16", "p": "L28_sam", "slice": "NC", "atype": "AGENT",
     "spec": ("has_owner", "hat"), "gold": "man", "text": "Who owns the hat?"},
    {"qid": "W17", "p": "L2_cat", "slice": "NC", "atype": "LOCATION",
     "spec": ("loc_ground", "cat"), "gold": "mat", "text": "On what is the cat asleep?"},
    {"qid": "W18", "p": "L26_patty", "slice": "NC", "atype": "LOCATION",
     "spec": ("loc_ground", "patty"), "gold": "house", "text": "In what does Patty live?"},
    {"qid": "W20", "p": "L5b_dodger", "slice": "NC", "atype": "AGENT",
     "spec": ("has_owner", "eyes"), "gold": "dodger", "text": "Who has bright eyes?"},
    {"qid": "W22", "p": "L35_willie", "slice": "NC", "atype": "AGENT",
     "spec": ("has_owner", "dog"), "gold": "willie", "text": "Who owns the dog Bounce?"},
    {"qid": "W23", "p": "L60_geo", "slice": "NC", "atype": "AGENT",
     "spec": ("has_owner", "dollar"), "gold": "george", "text": "Who had a silver dollar?"},
    {"qid": "W24", "p": "L18_king", "slice": "NC", "atype": "PATIENT",
     "spec": ("svo_patient", "builds", "bugs"), "gold": "nest", "text": "What is built in a tree?"},
    {"qid": "W28", "p": "L23_doll", "slice": "NC", "atype": "PATIENT",
     "spec": ("svo_patient", "scolded", "dash"), "gold": "dash", "text": "Whom did Mary scold?"},
]

# Original 31 Q ids (for the positive-control subset assertion), captured BEFORE we append.
_ORIG_QIDS = frozenset(q["qid"] for q in O.TEST_QS)


def _install_widened_corpus():
    """Append the widened Qs to O.TEST_QS ONCE (idempotent). Passages are unchanged (all widened Qs
    reference existing O.TEST_PASSAGES ids), so extract_passage / extract_passage_conf `known` sets are
    identical and the original passages' extracted relations are bit-stable."""
    have = {q["qid"] for q in O.TEST_QS}
    for wq in WIDENED_QS:
        assert wq["p"] in O.TEST_PASSAGES, "widened Q %s references unknown passage %s" % (wq["qid"], wq["p"])
        if wq["qid"] not in have:
            O.TEST_QS.append(wq)
            have.add(wq["qid"])


_install_widened_corpus()


# ===========================================================================================
# THE ONE NEW VARIABLE: the conflict / coherence flag.
#   conflict(rec) == True  when the store returns MORE THAN ONE distinct answer for the query pattern
#   (n_distinct > 1) -- the maintained discourse disagrees with itself (the match-conflict cap that v1
#   already computes; v2's coref-only gate is blind to it). This is Kintsch coherence-checking:
#   abstain when the answer is incoherent with the maintained bindings.
# The gate is the UNION OF ABSTENTIONS: abstain if (coref margin LOW) OR (conflict). Equivalently:
#   keep = is_answered AND coref_conf > th AND NOT conflict(rec)
# ===========================================================================================
def _conflict(rec):
    return rec.get("n_distinct", 0) > 1


def _sig(rec):
    return rec[GATE_SIGNAL_KEY]


def _keep(rec, th):
    return rec["is_answered"] and _sig(rec) > th and not _conflict(rec)


# ===========================================================================================
# Record construction: v1-VERBATIM real records + v1-VERBATIM parse_conf/coref_conf component attach.
# ===========================================================================================
def _build_records(clf, qs):
    recs, stores, scale = V1.build_real_conf(clf, qs)
    for r in recs:
        pid = r["q"]["p"]
        comp = V1._COMPONENT_CACHE.get(pid, {})
        pc, cc = V1._matched_component_conf(r["q"]["spec"], stores.get(pid, []), comp)
        r["parse_conf"] = pc
        r["coref_conf"] = cc
    return recs, stores, scale


# ===========================================================================================
# Gate-driving functions (the ONLY functions that differ from v2 -- they AND-in _conflict via _keep()).
# ===========================================================================================
def _gate_metrics_union(recs, th):
    n_total = len(recs)
    n_correct_kept = sum(1 for r in recs if _keep(r, th) and r["correct"] == 1)
    n_wrong_kept = sum(1 for r in recs if _keep(r, th) and r["is_answered"] and r["correct"] == 0)
    n_answered = sum(1 for r in recs if _keep(r, th))
    halluc = n_wrong_kept / n_total if n_total else 0.0
    coverage = n_answered / n_total if n_total else 0.0
    precision = n_correct_kept / n_answered if n_answered else 0.0
    return {"halluc": round(halluc, 4), "coverage": round(coverage, 4),
            "precision_on_answered": round(precision, 4), "n_answered": n_answered,
            "n_correct_kept": n_correct_kept, "n_wrong_kept": n_wrong_kept, "n_total": n_total,
            "threshold": round(th, 6)}


def precision_coverage_curve(recs):
    """Sweep the COREF-MARGIN threshold; the conflict flag is ANDed in at every threshold (union gate)."""
    answered = [r for r in recs if r["is_answered"]]
    confs = sorted(set(_sig(r) for r in answered))
    thresholds = [-1.0] + confs   # -1 = keep all answered that are conflict-free
    return [_gate_metrics_union(recs, th) for th in thresholds]


def choose_operating_threshold(curve):
    feasible = [c for c in curve if c["halluc"] <= HP_HALLUC_MAX]
    if not feasible:
        return curve[-1]
    return max(feasible, key=lambda c: (c["coverage"], -c["threshold"]))


def _cross_turn_report(recs, op):
    ct = [r for r in recs if r["slice"] in CROSS_TURN_SLICES]
    ng = V1._gate_metrics(ct, keep_fn=lambda r: r["is_answered"])
    gated_th = op["threshold"]
    n_total = len(ct)
    n_correct_kept = sum(1 for r in ct if _keep(r, gated_th) and r["correct"] == 1)
    n_wrong_kept = sum(1 for r in ct if _keep(r, gated_th) and r["is_answered"] and r["correct"] == 0)
    n_answered = sum(1 for r in ct if _keep(r, gated_th))
    gated = {"halluc": round(n_wrong_kept / n_total, 4) if n_total else 0.0,
             "coverage": round(n_answered / n_total, 4) if n_total else 0.0,
             "n_answered": n_answered, "n_correct_kept": n_correct_kept,
             "n_wrong_kept": n_wrong_kept, "n_total": n_total}
    return {"no_gate": ng, "gated": gated}


def _per_signal_contribution(recs, th):
    """For every ANSWERED WRONG record, attribute which signal (if any) abstains it at the operating th.
    conflict flag fires regardless of th; coref-margin fires when coref_conf <= th (and no conflict)."""
    wrongs = [r for r in recs if r["is_answered"] and r["correct"] == 0]
    caught_conflict = [r for r in wrongs if _conflict(r)]
    caught_coref = [r for r in wrongs if (not _conflict(r)) and _sig(r) <= th]
    residual = [r for r in wrongs if (not _conflict(r)) and _sig(r) > th]
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
    """Assemble res dict. Gate = coref margin OR conflict (union of abstentions)."""
    no_gate = V1._gate_metrics(recs, keep_fn=lambda r: r["is_answered"])
    n_correct = no_gate["n_correct_kept"]
    answered = [r for r in recs if r["is_answered"]]
    labels = [r["correct"] for r in answered]

    gate_scores = [_sig(r) for r in answered]   # coref margin = the continuous ranking signal
    rng = random.Random(SEED)
    auc_gate, ci_lo, ci_hi = V1._auc_ci(gate_scores, labels, rng, N_BOOT)
    auc_parse = V1._auc([r["parse_conf"] for r in answered], labels)
    auc_coref = V1._auc([r["coref_conf"] for r in answered], labels)
    auc_min = V1._auc([r["conf"] for r in answered], labels)

    curve = precision_coverage_curve(recs)
    op = choose_operating_threshold(curve)
    retained = (op["n_correct_kept"] / n_correct) if n_correct else 0.0

    srng = random.Random(SEED + 1)
    scramble = V1.scramble_null(recs, op["n_answered"], srng, N_SCRAMBLE_SEEDS)
    beat = round(scramble["halluc_mean"] - op["halluc"], 4)

    contrib = _per_signal_contribution(recs, op["threshold"])

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
    gate_answers = [r["ans"] if _keep(r, op["threshold"]) else None for r in recs]

    # ceiling-tie analysis (coref-only view) + the conflict-flag rescue localization.
    ceil_val = max((_sig(r) for r in answered), default=0.0)
    at_ceiling = [r for r in answered if round(_sig(r), 6) >= round(ceil_val, 6)]
    wrong_at_ceiling = [r for r in at_ceiling if r["correct"] == 0]
    ceiling_analysis = {
        "ceiling_value": round(ceil_val, 6),
        "n_correct_at_ceiling": sum(1 for r in at_ceiling if r["correct"] == 1),
        "n_wrong_at_ceiling": len(wrong_at_ceiling),
        "wrong_at_ceiling_qids": [r["q"]["qid"] for r in wrong_at_ceiling],
        "wrong_at_ceiling_rescued_by_conflict": [r["q"]["qid"] for r in wrong_at_ceiling if _conflict(r)],
        "wrong_at_ceiling_residual": [r["q"]["qid"] for r in wrong_at_ceiling if not _conflict(r)],
    }

    orig_recs = [r for r in recs if r["q"]["qid"] in _ORIG_QIDS]
    orig_ng = V1._gate_metrics(orig_recs, keep_fn=lambda r: r["is_answered"])

    return {
        "baseline": {"halluc": no_gate["halluc"], "coverage": no_gate["coverage"],
                     "precision_on_answered": no_gate["precision_on_answered"],
                     "n_correct": n_correct, "n_answered": no_gate["n_answered"],
                     "n_wrong": no_gate["n_wrong_kept"], "n_total": no_gate["n_total"]},
        "orig31_baseline": {"halluc": orig_ng["halluc"], "n_correct": orig_ng["n_correct_kept"],
                            "n_answered": orig_ng["n_answered"], "n_total": orig_ng["n_total"]},
        "auc": {"gate_signal": round(auc_gate, 4), "ci_lo": round(ci_lo, 4), "ci_hi": round(ci_hi, 4),
                "parse_only": round(auc_parse, 4), "coref_only": round(auc_coref, 4),
                "min_combined": round(auc_min, 4), "n_boot": N_BOOT,
                "gate_signal_name": "coref_margin_ranking", "n_pos": sum(labels),
                "n_neg": len(labels) - sum(labels)},
        "operating_point": op, "retained_correct_frac": round(retained, 4),
        "scramble": scramble, "beat_scramble": beat, "curve": curve, "margin_scale": round(scale, 6),
        "per_signal_contribution": contrib,
        "ceiling_analysis": ceiling_analysis,
        "cross_turn": _cross_turn_report(recs, op),
        "_answers": {"NO_GATE": no_gate_answers, "ABSTAIN_GATE": gate_answers,
                     "SCRAMBLE_GATE": scramble_answers},
        "_recs_debug": [{"qid": r["q"]["qid"], "slice": r["slice"], "ans": r["ans"], "gold": r["gold"],
                         "conf_min": r["conf"], "parse_conf": r.get("parse_conf"),
                         "coref_conf": r.get("coref_conf"), "conflict": _conflict(r),
                         "correct": r["correct"], "n_distinct": r["n_distinct"],
                         "is_widened": r["q"]["qid"] not in _ORIG_QIDS} for r in recs],
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
# Verdict (task bands: 4 operating metrics + coref-AUC comparability + conflict-catch localization).
# ===========================================================================================
def compute_verdict(res):
    auc = res["auc"]["coref_only"]
    op = res["operating_point"]
    retained = res["retained_correct_frac"]
    precision = op["precision_on_answered"]
    op_halluc = op["halluc"]
    beat = res["beat_scramble"]
    n_conflict_catch = res["per_signal_contribution"]["n_wrong_caught_by_conflict"]

    hp = (op_halluc <= HP_HALLUC_MAX and retained >= HP_RETAINED_CORRECT_MIN and
          precision >= HP_PRECISION_MIN and beat >= HP_BEAT_SCRAMBLE_MIN and
          auc >= HP_AUC_MIN and n_conflict_catch >= HP_CONFLICT_CATCH_MIN)
    # HARD_FAIL: cannot reach halluc<=0.05 except by killing coverage, OR conflict flag catches nothing,
    # OR no better than random abstention.
    reached_halluc = op_halluc <= HP_HALLUC_MAX
    hf = ((reached_halluc and retained <= HF_RETAINED_CORRECT_MAX) or
          (not reached_halluc) or
          n_conflict_catch == 0 or
          beat <= HF_BEAT_SCRAMBLE_MAX)

    if hp:
        tier, outcome = "HARD_PASS", "coref-OR-conflict-gate-restores-trustworthy-coverage-widened"
    elif hf:
        tier, outcome = "HARD_FAIL", "gate-cannot-reach-halluc-floor-or-conflict-blind-or-no-beat"
    else:
        tier, outcome = "MIDDLE_BAND", "coref-OR-conflict-gate-partial-precision-coverage-tradeoff"

    localize = []
    if not reached_halluc:
        localize.append("gate CANNOT reach halluc<=%.2f: best op_halluc=%.3f (residual unique-match "
                        "role-reversals invisible to BOTH coref margin AND conflict flag: %s)"
                        % (HP_HALLUC_MAX, op_halluc, res["per_signal_contribution"]["residual_qids"]))
    elif retained <= HF_RETAINED_CORRECT_MAX:
        localize.append("to reach halluc<=%.2f the gate abstains on ~everything: retained_correct=%.3f "
                        "<= %.2f (kept %d of %d correct)" % (HP_HALLUC_MAX, retained,
                        HF_RETAINED_CORRECT_MAX, op["n_correct_kept"], res["baseline"]["n_correct"]))
    if n_conflict_catch == 0:
        localize.append("conflict flag catches NO parse/match-reversal wrongs -- lever inert")
    if beat <= HF_BEAT_SCRAMBLE_MAX:
        localize.append("gate no better than RANDOM abstention: beat=%.3f <= %.2f" % (beat, HF_BEAT_SCRAMBLE_MAX))
    if not localize:
        c = res["per_signal_contribution"]
        localize.append("coref-OR-conflict gate trustworthy on widened n: op_halluc=%.3f retained=%.3f "
                        "precision=%.3f beat=%.3f coref-AUC=%.3f | conflict flag caught %d wrongs %s, "
                        "coref margin caught %d, residual %d %s (unique-match role-reversals invisible "
                        "to both)" % (op_halluc, retained, precision, beat, auc,
                        c["n_wrong_caught_by_conflict"], c["conflict_caught_qids"],
                        c["n_wrong_caught_by_coref_margin"], c["n_wrong_residual_neither"], c["residual_qids"]))

    msg = ("%s (%s) | GATE=coref_OR_conflict(union) | widened n_total=%d n_answered=%d n_correct=%d | "
           "NO_GATE halluc=%.3f | ORIG31 halluc=%.3f n_correct=%d (reproduces prior) | AUC coref=%.3f "
           "[%.3f,%.3f] (parse=%.3f) | OP@coref>%.3f&noconflict: halluc=%.3f cov=%.3f prec=%.3f "
           "retained=%.3f (%d/%d) | conflict-catch=%d coref-catch=%d residual=%d | scramble=%.3f beat=%.3f" % (
               tier, outcome, res["baseline"]["n_total"], res["baseline"]["n_answered"],
               res["baseline"]["n_correct"], res["baseline"]["halluc"], res["orig31_baseline"]["halluc"],
               res["orig31_baseline"]["n_correct"], auc, res["auc"]["ci_lo"], res["auc"]["ci_hi"],
               res["auc"]["parse_only"], op["threshold"], op_halluc, op["coverage"], precision, retained,
               op["n_correct_kept"], res["baseline"]["n_correct"],
               res["per_signal_contribution"]["n_wrong_caught_by_conflict"],
               res["per_signal_contribution"]["n_wrong_caught_by_coref_margin"],
               res["per_signal_contribution"]["n_wrong_residual_neither"],
               res["scramble"]["halluc_mean"], beat))
    return tier, outcome, msg, localize


# ===========================================================================================
# infra: out-dir / markers / metrics / crash (atomic). v3-scoped anchor name.
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
# self-test: real code path + isolation + the ONE new variable actually changes behavior + LOCALIZATION.
# ===========================================================================================
def self_test():
    print("[self-test] building REAL pipeline (perceptron fit + conf-extractor) ...", flush=True)
    clf = V1.build_clf()

    # (1) ONE-VARIABLE ISOLATION: conf-extractor relation SET == base O.extract_passage per passage.
    for pid, text in O.TEST_PASSAGES.items():
        base_rels, _ = O.extract_passage(text, "learned", clf, "maintained", "handrule", frozenset())
        conf_rels, _rl, _prov = V1.extract_passage_conf(text, clf, "maintained")
        assert set(base_rels) == set(conf_rels), \
            "ONE-VARIABLE BREACH: conf-extractor relations != base for %s" % pid

    # (2) POSITIVE CONTROL: NO_GATE per-question answers reproduce O.answer_reader exactly (all Qs).
    V1._attach_component_confs(clf, O.TEST_QS)
    recs, stores, scale = _build_records(clf, O.TEST_QS)
    for r in recs:
        base_ans = O.normalize(O.answer_reader(r["q"]["spec"], stores.get(r["q"]["p"], [])))
        assert r["ans"] == base_ans, "answer drift on %s: conf=%r base=%r" % (
            r["q"]["qid"], r["ans"], base_ans)

    # (3) ORIGINAL-31 baseline reproduces the prior 0.4194 halluc + n_correct==8 (widening added Qs, not
    # passages -> original extractions bit-stable).
    orig_recs = [r for r in recs if r["q"]["qid"] in _ORIG_QIDS]
    assert len(orig_recs) == 31, "orig subset size %d != 31" % len(orig_recs)
    ng = V1._gate_metrics(orig_recs, keep_fn=lambda r: r["is_answered"])
    assert abs(ng["halluc"] - BASE_HALLUC) <= BASE_HALLUC_TOL, \
        "ORIG-31 baseline halluc=%.4f not within %.3f of prior %.4f" % (ng["halluc"], BASE_HALLUC_TOL, BASE_HALLUC)
    assert ng["n_correct_kept"] == BASE_N_CORRECT, \
        "ORIG-31 baseline n_correct=%d != expected %d" % (ng["n_correct_kept"], BASE_N_CORRECT)

    # (4) widened set materially larger.
    n_answered = sum(1 for r in recs if r["is_answered"])
    n_correct = sum(1 for r in recs if r["is_answered"] and r["correct"] == 1)
    assert len(recs) >= 45, "widened n_total=%d too small" % len(recs)
    assert n_answered >= 25, "widened n_answered=%d below target 25" % n_answered
    assert n_correct > BASE_N_CORRECT, "widened n_correct=%d not larger than %d" % (n_correct, BASE_N_CORRECT)

    # (5) coref gate signal in [0,1] and NOT constant.
    answered = [r for r in recs if r["is_answered"]]
    gsig = [_sig(r) for r in answered]
    assert all(0.0 <= c <= 1.0 for c in gsig), "coref gate signal out of [0,1]"
    assert len(set(round(c, 4) for c in gsig)) >= 3, "coref gate signal near-constant"

    # (6) LOCALIZATION -- the KEY can-fail: the conflict flag catches N2 and M11 but NOT N6 (the 2-of-3
    # lever + the acknowledged residual). This is the whole hypothesis; assert it holds on disk.
    by_qid = {r["q"]["qid"]: r for r in recs}
    assert _conflict(by_qid["N2"]), "N2 expected to trip conflict flag (n_distinct>1)"
    assert _conflict(by_qid["M11"]), "M11 expected to trip conflict flag (n_distinct>1)"
    assert not _conflict(by_qid["N6"]), "N6 expected to be UNIQUE-match (conflict blind) -- the residual"

    # (7) the conflict flag genuinely CHANGES the gate decision vs coref-only on >=1 answered Q (the one
    # new variable actually binds): some answered rec has coref_conf high (>0.49) yet conflict fires.
    changed = [r for r in answered if _sig(r) > 0.49 and _conflict(r)]
    assert changed, "conflict flag never changes a keep decision vs coref-only -- v3 == v2"

    # (8) run + arms differ + gate abstains something.
    full = _run_from_recs(recs, scale)
    _arms_differ(full)
    op = full["operating_point"]
    assert op["threshold"] > -1.0 or op["coverage"] < 1.0, "gate never abstains"
    assert abs(full["auc"]["gate_signal"] - full["auc"]["coref_only"]) < 1e-9, "gate signal AUC wiring bug"

    print("[self-test] PASS | isolation OK | ORIG31 halluc=%.4f n_correct=%d | widened n_total=%d "
          "n_answered=%d n_correct=%d | coref-AUC=%.3f | conflict catches N2/M11 not N6 | "
          "OP th=%.3f halluc=%.3f retained=%.3f | conflict-catch=%d coref-catch=%d residual=%d"
          % (ng["halluc"], ng["n_correct_kept"], len(recs), n_answered, n_correct,
             full["auc"]["coref_only"], op["threshold"], op["halluc"], full["retained_correct_frac"],
             full["per_signal_contribution"]["n_wrong_caught_by_conflict"],
             full["per_signal_contribution"]["n_wrong_caught_by_coref_margin"],
             full["per_signal_contribution"]["n_wrong_residual_neither"]), flush=True)
    return True


# ===========================================================================================
# main run. FULL runs the entire widened set inline to completion.
# ===========================================================================================
def run(run_mode):
    qs = list(O.TEST_QS)
    if run_mode == "smoke":
        # smoke keeps passages that carry the discriminator (N2/M11 conflict-catch + residual N6 trap).
        smoke_pids = {"L2_cat", "L18_king", "L35_willie", "L26_patty", "L21_bee", "L32_tiger"}
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

    metrics = {
        "anchor_name": ANCHOR_NAME, "verdict": tier, "verdict_msg": msg, "summary": msg[:300],
        "gate_outcome": outcome, "run_mode": run_mode, "elapsed_s": round(elapsed, 4),
        "ts_iso": datetime.now(timezone.utc).isoformat(), "n_questions": len(qs),
        "arms": ["NO_GATE", "ABSTAIN_GATE", "SCRAMBLE_GATE"],
        "gate_signal": "coref_margin_OR_match_conflict_union_of_abstentions",
        "one_variable_vs_v2": "added the match-conflict/coherence flag to the coref-margin gate "
                              "(keep = coref>th AND NOT n_distinct>1) vs v2 keep = coref>th",
        "widened_corpus": {
            "n_orig_qs": len(_ORIG_QIDS), "n_widened_qs": len(WIDENED_QS),
            "n_total_qs": len(O.TEST_QS), "n_passages": len(O.TEST_PASSAGES),
            "widening_kind": "additional_natural_questions_over_existing_vetted_verbatim_passages",
            "verbatim_fidelity": "guaranteed_reused_vetted_passages_no_fabricated_text",
            "passage_count_widening_status": "deferred_needs_verified_verbatim_source_pull"},
        "n_answerable": res["baseline"]["n_answered"],
        "baseline_no_gate": res["baseline"],
        "orig31_baseline_positive_control": res["orig31_baseline"],
        "auc": res["auc"],
        "operating_point": res["operating_point"],
        "retained_correct_frac": res["retained_correct_frac"],
        "scramble_matched_coverage": res["scramble"],
        "beat_scramble": res["beat_scramble"],
        "per_signal_contribution": res["per_signal_contribution"],
        "ceiling_analysis": res["ceiling_analysis"],
        "precision_coverage_curve": res["curve"],
        "cross_turn": res["cross_turn"],
        "margin_scale": res["margin_scale"],
        "confidence_signals": ["coref_margin(maintained-overlay salience gap) -- GATE SIGNAL (ranking)",
                               "match_conflict(store returns >1 distinct answer; n_distinct>1) -- GATE FLAG (union)",
                               "parse_margin(perceptron argmax-runnerup) -- reported, NOT gated (anti-informative)"],
        "gate_threshold_kind": "fixed_interpretable_rule_coref_margin_gt_th_AND_no_match_conflict",
        "bands": {"HP_halluc_max": HP_HALLUC_MAX, "HP_retained_correct_min": HP_RETAINED_CORRECT_MIN,
                  "HP_precision_min": HP_PRECISION_MIN, "HP_beat_scramble_min": HP_BEAT_SCRAMBLE_MIN,
                  "HP_auc_min": HP_AUC_MIN, "HP_conflict_catch_min": HP_CONFLICT_CATCH_MIN,
                  "HF_retained_correct_max": HF_RETAINED_CORRECT_MAX,
                  "HF_beat_scramble_max": HF_BEAT_SCRAMBLE_MAX},
        "coverage_at_zero_halluc_ceiling": round(res["baseline"]["n_correct"] / res["baseline"]["n_total"], 4),
        "weakest_interface": localize,
        "arms_differ_digests": digests, "arms_differ_verified": True,
        "arms_differ_exempted": arms_exempted,
        "final_metrics_atomicity": "tmp_replace", "deterministic_seeding": True,
        "progress_logging": "print_flush_true", "compute_architecture": "sequential_cpu_pure_python",
        "crlb_n_a": "symbolic glass-box; coverage-at-zero-halluc ceiling (n_correct/n_total) is the feasibility bound",
        "per_question": res["_recs_debug"],
        "reuse_credited": {
            "v1_gate_machinery_imported_verbatim": "exp_multi_turn_loop_realtext_confidence_abstain_gate_v1.py",
            "v2_coref_only_lineage": "exp_multi_turn_loop_realtext_confidence_abstain_gate_v2.py (HARD_FAIL; "
                                     "ceiling_analysis localizes N2/N6/M11)",
            "realtext_components_and_gold": "exp_oracle_mention_upperbound_reader_v1.py",
            "conflict_cap_signal": "v1 build_real_conf n_distinct>1 -> CONFLICT_CAP=0.15 (Kintsch coherence)"},
        "REQUIRED_FIELDS": ["verdict", "baseline_no_gate", "orig31_baseline_positive_control", "auc",
                            "operating_point", "retained_correct_frac", "scramble_matched_coverage",
                            "beat_scramble", "per_signal_contribution", "arms_differ_digests",
                            "gate_signal", "n_answerable"],
        "notes": ("Coref-OR-conflict trustworthy abstain gate (v3). ONE new variable vs v2: add the "
                  "match-conflict/coherence flag (abstain if coref margin LOW OR the answer conflicts "
                  "with the maintained discourse -- store self-disagrees). Union of abstentions, not "
                  "min. Widened to 53 Qs over the 14 vetted verbatim passages. CLAIM-VET-pending."),
    }
    _write_metrics(out_dir, metrics)

    print("[%s:%s] %s" % (ANCHOR_NAME, run_mode, msg), flush=True)
    print("  [NO_GATE ] widened halluc=%.3f cov=1.000 (correct=%d wrong=%d abstain=%d of %d) | ORIG31 halluc=%.3f n_correct=%d"
          % (res["baseline"]["halluc"], res["baseline"]["n_correct"], res["baseline"]["n_wrong"],
             res["baseline"]["n_total"] - res["baseline"]["n_answered"], res["baseline"]["n_total"],
             res["orig31_baseline"]["halluc"], res["orig31_baseline"]["n_correct"]), flush=True)
    print("  [AUC     ] coref=%.3f [%.3f,%.3f] parse_only=%.3f min_combined=%.3f (pos=%d neg=%d)"
          % (res["auc"]["coref_only"], res["auc"]["ci_lo"], res["auc"]["ci_hi"], res["auc"]["parse_only"],
             res["auc"]["min_combined"], res["auc"]["n_pos"], res["auc"]["n_neg"]), flush=True)
    op = res["operating_point"]
    print("  [OP GATE ] coref>%.3f AND no-conflict: halluc=%.3f cov=%.3f prec=%.3f retained=%.3f (kept %d/%d)"
          % (op["threshold"], op["halluc"], op["coverage"], op["precision_on_answered"],
             res["retained_correct_frac"], op["n_correct_kept"], res["baseline"]["n_correct"]), flush=True)
    c = res["per_signal_contribution"]
    print("  [SIGNALS ] wrong=%d | conflict-catch=%d %s | coref-catch=%d | residual=%d %s"
          % (c["n_wrong_answered"], c["n_wrong_caught_by_conflict"], c["conflict_caught_qids"],
             c["n_wrong_caught_by_coref_margin"], c["n_wrong_residual_neither"], c["residual_qids"]), flush=True)
    print("  [SCRAMBLE] matched-cov halluc_mean=%.3f p95=%.3f -> real BEATS random by %.3f"
          % (res["scramble"]["halluc_mean"], res["scramble"]["halluc_p95"], res["beat_scramble"]), flush=True)
    print("  [weakest ] %s" % localize, flush=True)
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
