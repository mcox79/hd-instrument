"""Scaffold-free witness for `score_counts_abstention_as_error`.

THE DEFECT (was): experiments/exp_consequence_learning_loop_oov_outcome_verb_valence_v1.py::_score did
`ok = (pred == gold)` and never named the readout's third/fourth outcomes NONE / AMBIGUOUS. The live
readout (hdlab.goal_typing.congruence_with_lexicon_fallback) treats BOTH as ABSTENTIONS -- its own
abstain set `_LEVIN_ABSTAIN = ('NA','NONE','AMBIGUOUS')` is what it branches on at goal_typing.py:2200
and :2214. So the cell disagreed with its own engine and scored every abstention as a wrong answer.

THE FIX: _score now classifies each item correct / wrong / abstained via tools/score_with_abstention.py
(ABSTAIN_MAJORITY), and reports BOTH conventions. `primary_accuracy` stays coverage-weighted
(abstain==error), which is arithmetically invariant to the relabel, so NO gate threshold moves.

WHAT THIS WITNESS PROVES, live, re-deriving predictions from the already-learned overlay (it re-learns
NOTHING and writes NOTHING to the landed directory):

  1. GATE-SAFE. Coverage-weighted accuracy (correct/n) is byte-identical to the landed primary -- the
     fix cannot change the verdict; it is a correctness fix to the instrument, not a rescue.
  2. THE DEFECT IS BROADER THAN THE BRIEF. The brief named 3 AMBIGUOUS items. The disk shows 17
     abstentions (14 NONE + 3 AMBIGUOUS), all of reason `abstain_fallback_to_lexicon`, every one scored
     wrong by the old `pred == gold`. NONE is an abstention in the readout's OWN set and in BOTH guard
     conventions; the brief undercounted because it named only the token that makes the conventions
     DISAGREE.
  3. POSITIVE CONTROL, tied to the 3 motivating items. The 3 AMBIGUOUS carried correct:False in the
     landed record (scored as wrong). After the fix they are abstentions, and the committed-subset
     (selective) accuracy moves BECAUSE of exactly those 3: 0.5000 (narrow: AMBIGUOUS==error) ->
     0.5789 (engine/majority: AMBIGUOUS==abstain). Remove the 3 and the two conventions AGREE.
  4. NEGATIVE CONTROL. The empty-overlay baseline re-derived live has zero AMBIGUOUS and a
     coverage-weighted accuracy byte-identical to the landed baseline -- the fix touches nothing there.
  5. ENGINE-CONVENTION COUPLING (positive, not an absence check): NONE and AMBIGUOUS are both members
     of hdlab.goal_typing._LEVIN_ABSTAIN, and the guard's ABSTAIN_MAJORITY matches it.

Run:  .venv/Scripts/python.exe verification/test_oov_cell_scores_abstention_as_abstention.py
ASCII-only. No network, no scaffold, no writes to the landed directory. ~30-60 s (scores 36 items x2).
"""
import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import json
import sys
from collections import Counter

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import experiments.exp_consequence_learning_loop_oov_outcome_verb_valence_v1 as CELL
from tools.score_with_abstention import both_conventions, ABSTAIN_MAJORITY
from hdlab.goal_typing import _LEVIN_ABSTAIN

LANDED = os.path.join(_REPO, "data", "exp_consequence_learning_loop_oov_outcome_verb_valence_v1",
                      "metrics.json")


def _approx(a, b, tol=1e-9):
    return a is not None and b is not None and abs(a - b) <= tol


def main():
    m = json.load(open(LANDED, encoding="utf-8"))
    landed_primary = m["primary_accuracy"]
    landed_base = m["fallthrough_baseline_accuracy"]
    landed_pred = {d["id"]: d["pred"] for d in m["per_item_predictions"]}
    landed_amb = {d["id"] for d in m["per_item_predictions"] if d["pred"] == "AMBIGUOUS"}

    _all_rows, oov_rows = CELL._load_eval()
    assert len(oov_rows) == 36, "expected the OOV-36 population"

    ok = True

    def chk(cond, msg):
        nonlocal ok
        print(("[witness] PASS " if cond else "[witness] FAIL ") + msg)
        ok = ok and bool(cond)

    # ---- exercise the EDITED cell LIVE on the already-learned overlay (re-derives predictions) ----
    registered = m["registered"]
    acc, correct, met_c, unmet_c, n_met, n_unmet, details, abst = \
        CELL._score_with_overlay(oov_rows, registered)
    live_pred = {d["id"]: d["pred"] for d in details}
    preds = [d["pred"] for d in details]
    golds = [d["gold"] for d in details]
    dist = dict(Counter(preds))
    print("[witness] live pred dist = %s  correct=%d  n=%d" % (dist, correct, len(details)))

    # predictions reproduce from the saved overlay (not a stale JSON replay)
    chk(live_pred == landed_pred,
        "predictions reproduce live from the landed overlay (%d/%d identical)"
        % (sum(1 for i in live_pred if live_pred[i] == landed_pred.get(i)), len(live_pred)))

    # ---- 1. GATE-SAFE: coverage-weighted accuracy unchanged --------------------------------------
    chk(_approx(round(acc, 4), landed_primary),
        "coverage-weighted accuracy is byte-identical to the landed primary (%.4f == %.4f) -- no gate moves"
        % (round(acc, 4), landed_primary))

    # ---- independent recomputation of both conventions -------------------------------------------
    pair = both_conventions(preds, golds)
    maj, nar = pair.majority, pair.narrow
    n_none = sum(1 for p in preds if p == "NONE")
    n_amb = sum(1 for p in preds if p == "AMBIGUOUS")

    # cell's own abstention dict must match the independent computation
    em = abst["engine_convention_majority"]
    chk(em["correct"] == maj.correct and em["wrong"] == maj.wrong and em["abstained"] == maj.abstained,
        "cell's abstention split matches independent guard: correct=%d wrong=%d abstained=%d"
        % (maj.correct, maj.wrong, maj.abstained))
    chk(abst["conventions_agree"] == pair.agree,
        "cell's conventions_agree matches guard: %s" % pair.agree)

    # ---- 2. THE DEFECT IS BROADER THAN THE BRIEF: 17 abstentions, not 3 --------------------------
    chk(maj.abstained == n_none + n_amb == 17 and n_none == 14 and n_amb == 3,
        "17 abstentions scored wrong by the old scorer = 14 NONE + 3 AMBIGUOUS (brief named only 3)")
    chk(maj.correct == 11 and maj.wrong == 8,
        "engine convention: 11 correct, 8 genuine commission errors, 17 abstained (11+8+17=36)")
    sel_maj = maj.precision_when_committing
    chk(maj.correct + maj.wrong == 19 and _approx(round(sel_maj, 4), 0.5789, 5e-4),
        "selective accuracy when committing (engine convention) = 11/19 = %.4f" % sel_maj)

    # ---- 3. POSITIVE CONTROL tied to the 3 AMBIGUOUS ---------------------------------------------
    landed_amb_rows = [d for d in m["per_item_predictions"] if d["pred"] == "AMBIGUOUS"]
    chk(len(landed_amb_rows) == 3 and all(d["correct"] is False for d in landed_amb_rows),
        "the 3 AMBIGUOUS items (%s) were scored correct:False (wrong by omission) before the fix"
        % ", ".join(sorted(d["outcome_lemma"] for d in landed_amb_rows)))
    sel_nar = nar.precision_when_committing            # AMBIGUOUS counted as wrong commitments
    chk(_approx(round(sel_nar, 4), 0.5000, 5e-4) and not pair.agree,
        "the 3 items move committed-subset accuracy 0.5000 (AMBIGUOUS==error) -> %.4f "
        "(AMBIGUOUS==abstain); conventions DISAGREE" % sel_maj)
    # removing exactly the 3 AMBIGUOUS makes the conventions agree -> they are the whole disagreement
    keep = [(p, g) for p, g in zip(preds, golds) if p != "AMBIGUOUS"]
    pair_no_amb = both_conventions([p for p, _ in keep], [g for _, g in keep])
    chk(pair_no_amb.agree,
        "removing the 3 AMBIGUOUS makes the two conventions AGREE -- they are the entire disagreement")

    # ---- 4. NEGATIVE CONTROL: empty-overlay baseline byte-identical, zero AMBIGUOUS ---------------
    CELL._vls.clear_acquired_outcome()
    b_out = CELL._score(oov_rows)
    b_acc, b_details, b_abst = b_out[0], b_out[6], b_out[7]
    CELL._vls.clear_acquired_outcome()
    b_amb = sum(1 for d in b_details if d["pred"] == "AMBIGUOUS")
    chk(b_amb == 0, "empty-overlay baseline has zero AMBIGUOUS predictions")
    chk(_approx(round(b_acc, 4), landed_base),
        "empty-overlay baseline accuracy byte-identical to landed (%.4f == %.4f)"
        % (round(b_acc, 4), landed_base))
    chk(b_abst["conventions_agree"] is True,
        "baseline is convention-free (no AMBIGUOUS) -- the fix touches nothing there")

    # ---- 5. ENGINE-CONVENTION COUPLING (positive control, not an absence check) -------------------
    chk("NONE" in _LEVIN_ABSTAIN and "AMBIGUOUS" in _LEVIN_ABSTAIN,
        "readout's own abstain set _LEVIN_ABSTAIN=%s contains BOTH NONE and AMBIGUOUS"
        % (tuple(_LEVIN_ABSTAIN),))
    chk(set(t for t in ABSTAIN_MAJORITY if t is not None) == set(_LEVIN_ABSTAIN),
        "guard ABSTAIN_MAJORITY matches the engine's source-of-truth abstain set")

    # ---- diagnostic honesty: selective accuracy does NOT clear its own fair floor ----------------
    committed = [(p, g) for p, g in zip(preds, golds) if p not in ABSTAIN_MAJORITY]
    gold_committed = Counter(g for _, g in committed)
    committed_majority_floor = max(gold_committed.values()) / len(committed) if committed else None
    print("[witness] DIAGNOSTIC: selective acc %.4f on %d committed items vs committed-majority floor "
          "%.4f -- selective accuracy does NOT clear its floor; this is an instrument fix, not a rescue"
          % (sel_maj, len(committed), committed_majority_floor))
    print("[witness] RISK-COVERAGE: coverage %.4f (%d/36 committed), selective accuracy %.4f, "
          "coverage-weighted accuracy %.4f" % (len(committed) / 36.0, len(committed), sel_maj, acc))

    print("[witness] RESULT:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
