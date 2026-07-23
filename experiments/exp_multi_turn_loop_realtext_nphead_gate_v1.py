"""exp_multi_turn_loop_realtext_nphead_gate_v1 -- add a STRUCTURAL NP-HEAD-CONSISTENCY signal to the
McGuffey (in-domain) trustworthy abstain gate. ONE new variable vs v3 (29465): a UNION abstention on
NP-head-inconsistency.

CONTEXT: exp_multi_turn_loop_realtext_confidence_abstain_gate_v3 (HARD_PASS, 29465) drove McGuffey
hallucination to op_halluc=0.0377 MEASURED@data/exp_multi_turn_loop_realtext_confidence_abstain_gate_v3/
metrics.json:operating_point.halluc via a coref-margin OR match-conflict union gate at th=0.490995. The
RESIDUAL 2 confident-wrong answers it CANNOT catch are BOTH the SAME structural error: N6 + W18 both
answer "log" for "log house" (gold "house") -- coref=1.0 (ceiling, invisible to the coref margin) and
n_distinct=1 (invisible to the match-conflict flag). "log" is a COMPOUND-NOUN MODIFIER of the head
"house": an NP-HEAD-selection error.

THE ONE NEW VARIABLE: add a glass-box STRUCTURAL NP-head-consistency check (experiments/_np_head_signal.py)
to the union of abstentions. A candidate answer noun is trustworthy iff it occurs in the passage as the
HEAD of its noun phrase (rightmost noun of its noun-run) rather than ONLY as a pre-modifier (adjective /
compound-noun modifier / proper-noun title). "log" occurs only as the modifier of "house" -> NP non-head
-> abstain. NP structure is corpus-GENERAL (the sister cell tests whether it TRANSFERS out-of-domain).
    v3 : keep = is_answered AND coref>th AND NOT conflict(rec)
    v1 : keep = is_answered AND coref>th AND NOT conflict(rec) AND np_head_consistent(rec)   [+ NP-head]
FROZEN threshold th=0.490995 (v3's McGuffey operating point) for BOTH the PRIOR_GATE and the NEW_GATE, so
the ONLY difference between arms is the NP-head signal (clean one-variable isolation; no re-tune).

ARMS:
  NO_GATE      = REAL pipeline answers everything it commits (positive control).
  PRIOR_GATE   = v3 coref-OR-conflict union at frozen th (reproduces v3 op: halluc=0.0377, residual N6/W18).
  NEW_GATE     = PRIOR_GATE AND NP-head-consistent (THE MECHANISM; the ONE added variable).
  SCRAMBLE_GATE= anti-cheat must-fail: matched-coverage RANDOM abstention at NEW_GATE coverage.

BANDS (envelope-fail; set BEFORE the run; global halluc = wrong-answered / n_total on the widened n=53):
  HARD_PASS (NP-head catches the in-domain residual with no new errors -> TRUE zero confident-wrong):
      new_op_halluc <= 0.01 AND
      retained_correct_frac >= 0.60 AND
      precision_on_answered >= 0.80 AND
      prior residual (>=1 wrong that survived coref+conflict) is FULLY caught by NP-head AND
      NP-head falsely-abstains ZERO correct answers PRIOR_GATE kept (no new errors).
  HARD_FAIL (NP-head does not catch the residual / creates new errors / collapses coverage):
      NP-head does NOT catch the full prior residual, OR
      new_op_halluc > 0.05, OR
      retained_correct_frac <= 0.25, OR
      (NP-head falsely-abstains a correct answer AND retained_correct_frac < 0.60).
  MIDDLE otherwise.

WHY GENUINELY CAN-FAIL: (a) the POS tagger might tag "log" as a head noun (then NP-head does not fire and
the residual survives); (b) NP-head might falsely flag a CORRECT answer whose token happens to occur only
as a pre-modifier somewhere in the passage, collapsing coverage. Both are measured on disk; the data
decides. Correction-to-head ("log"->"house") is reported as a DIAGNOSTIC only (the gate ABSTAINS, it does
not alter answers).

DESIGN-GATE (verified at self-test): (1) REAL code path (perceptron fit + POS + WorkingOverlay coref +
conf-extract); (2) POSITIVE-CONTROL PRIOR_GATE reproduces v3 op halluc within tol; (3) NP-head CATCHES
N6/W18 (nonhead) and does NOT flag head answers house/henry; (4) NP-head reads NO gold (only ans+passage);
(5) ONE variable -- NEW_GATE differs from PRIOR_GATE on >=1 record; (6) arms differ; (7) determinism
(OMP=1, fixed seed, sorted set, no hash()-seeding).

CELL-TEMPLATE (relevant subset; many SCHEMA-VET gates N/A for this non-HD glass-box cell):
# - except SystemExit/KeyboardInterrupt: raise BEFORE except Exception (no BaseException)
# - ATOMIC final metrics write (tmp + os.replace)                 [META_RULE_AH: tmp_replace]
# - ARMS-MUST-DIFFER hash check at run                            [META_RULE_AF]
# - discriminator CAN-FAIL (POS mis-tag OR false-abstain) AND FIRES (catches N6/W18)  [design-gate]
# - REAL code path exercised in self-test                                              [F.1]
# - baseline_in_band: PRIOR_GATE reproduces v3 op; gate free to fail                   [AG]
# - deterministic (fixed seed, OMP=1, no hash()-seed, sorted(set))          [F.5 / PROT-023]
# - start-marker + crash-diagnostic; heartbeat EXEMPT (wall < 90s)
# - crlb_n/a: symbolic glass-box; coverage-at-zero-halluc ceiling IS the feasibility bound
# - progress_logging: print_flush_true.  gate_threshold: FIXED interpretable rule, FROZEN (no re-tune).
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

# v3 supplies the widened McGuffey corpus (installed into O at import), the real record builder, and the
# coref/conflict gate primitives. V1 supplies the underlying machinery (extractor, scramble, AUC).
import experiments.exp_multi_turn_loop_realtext_confidence_abstain_gate_v3 as V3
import experiments.exp_multi_turn_loop_realtext_confidence_abstain_gate_v1 as V1
import experiments._np_head_signal as NP

O = V3.O

ANCHOR_NAME = "multi_turn_loop_realtext_nphead_gate_v1"

SEED = V1.SEED
N_SCRAMBLE_SEEDS = V1.N_SCRAMBLE_SEEDS
N_BOOT = V1.N_BOOT
GATE_SIGNAL_KEY = "coref_conf"

# FROZEN McGuffey operating point (v3 HARD_PASS op-point; NO re-tune -> clean one-variable isolation).
# CITED@data/exp_multi_turn_loop_realtext_confidence_abstain_gate_v3/metrics.json:operating_point
FIXED_TH = 0.490995
V3_METRICS_PATH = REPO / "data" / "exp_multi_turn_loop_realtext_confidence_abstain_gate_v3" / "metrics.json"
PRIOR_OP_HALLUC = 0.0377            # CITED@v3 metrics operating_point.halluc (positive-control target)
PRIOR_OP_HALLUC_TOL = 0.02

# pre-registered bands (HYPOTHESIZED@this prereg)
HP_HALLUC_MAX = 0.01
HP_RETAINED_MIN = 0.60
HP_PRECISION_MIN = 0.80
HF_HALLUC_MAX_SOFT = 0.05
HF_RETAINED_MAX = 0.25


def _conflict(rec):
    return rec.get("n_distinct", 0) > 1


def _sig(rec):
    return rec[GATE_SIGNAL_KEY]


def _np_ok(rec):
    """True = NP-head-consistent (keep-eligible); False = detected NP non-head (abstain)."""
    return rec["np_status"] != "nonhead"


def _prior_keep(rec):
    return rec["is_answered"] and _sig(rec) > FIXED_TH and not _conflict(rec)


def _new_keep(rec):
    return _prior_keep(rec) and _np_ok(rec)


def _attach_np(recs):
    for r in recs:
        txt = O.TEST_PASSAGES[r["q"]["p"]]
        r["np_status"] = NP.np_head_status(r["ans"], txt, O.pos_tag_sentence, O.split_sentences)
        r["np_correction"] = NP.np_head_correction(r["ans"], txt, O.pos_tag_sentence, O.split_sentences)
    return recs


def _gate_metrics(recs, keep_fn):
    n_total = len(recs)
    n_correct_kept = sum(1 for r in recs if keep_fn(r) and r["correct"] == 1)
    n_wrong_kept = sum(1 for r in recs if keep_fn(r) and r["is_answered"] and r["correct"] == 0)
    n_answered = sum(1 for r in recs if keep_fn(r))
    halluc = n_wrong_kept / n_total if n_total else 0.0
    coverage = n_answered / n_total if n_total else 0.0
    precision = n_correct_kept / n_answered if n_answered else 0.0
    return {"halluc": round(halluc, 4), "coverage": round(coverage, 4),
            "precision_on_answered": round(precision, 4), "n_answered": n_answered,
            "n_correct_kept": n_correct_kept, "n_wrong_kept": n_wrong_kept, "n_total": n_total,
            "threshold": FIXED_TH}


def _contribution(recs):
    """Attribute each answered-wrong to the signals that abstain it; isolate the NP-head lever's effect
    on the PRIOR residual (wrongs that survived coref+conflict) and on the CORRECT answers."""
    wrongs = [r for r in recs if r["is_answered"] and r["correct"] == 0]
    caught_conflict = [r for r in wrongs if _conflict(r)]
    caught_coref = [r for r in wrongs if (not _conflict(r)) and _sig(r) <= FIXED_TH]
    prior_residual = [r for r in wrongs if _prior_keep(r)]           # survived coref+conflict (= v3 residual)
    nphead_catch = [r for r in prior_residual if not _np_ok(r)]      # NP-head rescues these
    new_residual = [r for r in prior_residual if _np_ok(r)]          # survive ALL three signals
    # NP-head action on correct answers PRIOR_GATE kept (new errors = false abstentions):
    prior_kept_correct = [r for r in recs if _prior_keep(r) and r["correct"] == 1]
    false_abstain = [r for r in prior_kept_correct if not _np_ok(r)]
    return {
        "n_wrong_answered": len(wrongs),
        "n_wrong_caught_by_conflict": len(caught_conflict),
        "n_wrong_caught_by_coref_margin": len(caught_coref),
        "n_prior_residual": len(prior_residual),
        "n_prior_residual_caught_by_nphead": len(nphead_catch),
        "nphead_caught_qids": [r["q"]["qid"] for r in nphead_catch],
        "nphead_corrections": {r["q"]["qid"]: {"ans": r["ans"], "head": r["np_correction"],
                                               "gold": r["gold"], "head_eq_gold": r["np_correction"] == r["gold"]}
                               for r in nphead_catch},
        "n_new_residual": len(new_residual),
        "new_residual_qids": [r["q"]["qid"] for r in new_residual],
        "n_correct_false_abstained_by_nphead": len(false_abstain),
        "false_abstained_qids": [r["q"]["qid"] for r in false_abstain],
    }


def _run_from_recs(recs, scale):
    no_gate = _gate_metrics(recs, keep_fn=lambda r: r["is_answered"])
    n_correct = no_gate["n_correct_kept"]
    prior = _gate_metrics(recs, keep_fn=_prior_keep)
    new = _gate_metrics(recs, keep_fn=_new_keep)
    retained = (new["n_correct_kept"] / n_correct) if n_correct else 0.0
    prior_retained = (prior["n_correct_kept"] / n_correct) if n_correct else 0.0

    answered = [r for r in recs if r["is_answered"]]
    labels = [r["correct"] for r in answered]
    auc_coref = V1._auc([r["coref_conf"] for r in answered], labels)

    srng = random.Random(SEED + 1)
    scramble = V1.scramble_null(recs, new["n_answered"], srng, N_SCRAMBLE_SEEDS)
    beat = round(scramble["halluc_mean"] - new["halluc"], 4)

    contrib = _contribution(recs)

    no_gate_answers = [r["ans"] if r["is_answered"] else None for r in recs]
    prior_answers = [r["ans"] if _prior_keep(r) else None for r in recs]
    new_answers = [r["ans"] if _new_keep(r) else None for r in recs]
    arng = random.Random(SEED + 2)
    k = new["n_answered"]
    keep_idx = set(arng.sample(range(len(answered)), min(k, len(answered)))) if k > 0 else set()
    answered_id = {id(r): j for j, r in enumerate(answered)}
    scramble_answers = [None if not r["is_answered"] else
                        (r["ans"] if answered_id[id(r)] in keep_idx else None) for r in recs]

    return {
        "baseline": {"halluc": no_gate["halluc"], "coverage": no_gate["coverage"],
                     "precision_on_answered": no_gate["precision_on_answered"], "n_correct": n_correct,
                     "n_answered": no_gate["n_answered"], "n_wrong": no_gate["n_wrong_kept"],
                     "n_total": no_gate["n_total"]},
        "prior_gate": {**prior, "retained_correct_frac": round(prior_retained, 4)},
        "operating_point": new, "retained_correct_frac": round(retained, 4),
        "auc": {"coref_only": round(auc_coref, 4), "n_pos": sum(labels), "n_neg": len(labels) - sum(labels)},
        "scramble": scramble, "beat_scramble": beat, "margin_scale": round(scale, 6),
        "nphead_contribution": contrib,
        "_answers": {"NO_GATE": no_gate_answers, "PRIOR_GATE": prior_answers,
                     "NEW_GATE": new_answers, "SCRAMBLE_GATE": scramble_answers},
        "_recs_debug": [{"qid": r["q"]["qid"], "p": r["q"]["p"], "ans": r["ans"], "gold": r["gold"],
                         "coref_conf": r.get("coref_conf"), "conflict": _conflict(r),
                         "n_distinct": r["n_distinct"], "np_status": r["np_status"],
                         "np_correction": r["np_correction"], "correct": r["correct"],
                         "prior_kept": _prior_keep(r), "new_kept": _new_keep(r)} for r in recs],
    }


def _arms_differ(res):
    digests = {n: hashlib.sha256(json.dumps(res["_answers"][n], sort_keys=True).encode()).hexdigest()
               for n in ("NO_GATE", "PRIOR_GATE", "NEW_GATE", "SCRAMBLE_GATE")}
    assert digests["NO_GATE"] != digests["PRIOR_GATE"], "META_RULE_AF: NO_GATE == PRIOR_GATE"
    assert digests["PRIOR_GATE"] != digests["NEW_GATE"], \
        "META_RULE_AF: NEW_GATE == PRIOR_GATE (NP-head abstained on nothing -- one variable inert)"
    exempted = []
    if res["operating_point"]["coverage"] == 0.0:
        exempted.append(["NEW_GATE", "SCRAMBLE_GATE"])
    else:
        assert digests["NEW_GATE"] != digests["SCRAMBLE_GATE"], "META_RULE_AF: NEW_GATE == SCRAMBLE_GATE"
    return digests, exempted


def compute_verdict(res):
    op = res["operating_point"]
    op_halluc = op["halluc"]
    retained = res["retained_correct_frac"]
    precision = op["precision_on_answered"]
    c = res["nphead_contribution"]
    residual_caught = (c["n_prior_residual"] >= 1 and
                       c["n_prior_residual_caught_by_nphead"] == c["n_prior_residual"])
    no_new_errors = c["n_correct_false_abstained_by_nphead"] == 0

    hp = (op_halluc <= HP_HALLUC_MAX and retained >= HP_RETAINED_MIN and precision >= HP_PRECISION_MIN
          and residual_caught and no_new_errors)
    hf = ((not residual_caught) or op_halluc > HF_HALLUC_MAX_SOFT or retained <= HF_RETAINED_MAX
          or (not no_new_errors and retained < HP_RETAINED_MIN))

    if hp:
        tier, outcome = "HARD_PASS", "nphead-catches-in-domain-residual-true-zero-confident-wrong"
    elif hf:
        tier, outcome = "HARD_FAIL", "nphead-misses-residual-or-creates-errors-or-collapses-coverage"
    else:
        tier, outcome = "MIDDLE_BAND", "nphead-partial-in-domain"

    localize = []
    if not residual_caught:
        localize.append("NP-head did NOT catch full prior residual: caught %d of %d (%s); new residual %s"
                        % (c["n_prior_residual_caught_by_nphead"], c["n_prior_residual"],
                           c["nphead_caught_qids"], c["new_residual_qids"]))
    if not no_new_errors:
        localize.append("NP-head falsely abstained %d CORRECT answers (new errors): %s"
                        % (c["n_correct_false_abstained_by_nphead"], c["false_abstained_qids"]))
    if not localize:
        localize.append("NP-head caught in-domain residual %s (corrections->gold: %s); zero false-abstain; "
                        "op_halluc %.4f->%.4f retained=%.3f precision=%.3f"
                        % (c["nphead_caught_qids"], c["nphead_corrections"],
                           res["prior_gate"]["halluc"], op_halluc, retained, precision))

    msg = ("%s (%s) | McGuffey-in-domain n_total=%d n_answerable=%d n_correct=%d | NO_GATE halluc=%.3f | "
           "PRIOR_GATE@coref>%.4f&noconflict: halluc=%.4f cov=%.3f retained=%.3f (%d/%d) | +NP-HEAD NEW_GATE: "
           "halluc=%.4f cov=%.3f prec=%.3f retained=%.3f (%d/%d) | nphead caught prior-residual %d/%d %s | "
           "false-abstain=%d %s | scramble=%.3f beat=%.3f | coref-AUC=%.3f" % (
               tier, outcome, res["baseline"]["n_total"], res["baseline"]["n_answered"],
               res["baseline"]["n_correct"], res["baseline"]["halluc"], FIXED_TH,
               res["prior_gate"]["halluc"], res["prior_gate"]["coverage"],
               res["prior_gate"]["retained_correct_frac"], res["prior_gate"]["n_correct_kept"],
               res["baseline"]["n_correct"], op_halluc, op["coverage"], precision, retained,
               op["n_correct_kept"], res["baseline"]["n_correct"],
               c["n_prior_residual_caught_by_nphead"], c["n_prior_residual"], c["nphead_caught_qids"],
               c["n_correct_false_abstained_by_nphead"], c["false_abstained_qids"],
               res["scramble"]["halluc_mean"], res["beat_scramble"], res["auc"]["coref_only"]))
    return tier, outcome, msg, localize


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


def _build(clf, qs):
    V1._attach_component_confs(clf, qs)
    recs, stores, scale = V3._build_records(clf, qs)
    _attach_np(recs)
    return recs, stores, scale


def self_test():
    print("[self-test] building REAL pipeline (perceptron fit + conf-extractor) ...", flush=True)

    # (0) frozen th == v3 on-disk op-point (if present).
    if V3_METRICS_PATH.exists():
        v3 = json.load(open(V3_METRICS_PATH, encoding="utf-8"))
        v3_th = v3.get("operating_point", {}).get("threshold")
        assert v3_th is not None and abs(v3_th - FIXED_TH) < 1e-6, \
            "FROZEN th %.6f != v3 op-point %r" % (FIXED_TH, v3_th)

    clf = V1.build_clf()
    recs, stores, scale = _build(clf, O.TEST_QS)

    # (1) POSITIVE CONTROL: NO_GATE reproduces O.answer_reader exactly (real code path, no answer drift).
    for r in recs:
        base = O.normalize(O.answer_reader(r["q"]["spec"], stores.get(r["q"]["p"], [])))
        assert r["ans"] == base, "answer drift on %s: %r vs %r" % (r["q"]["qid"], r["ans"], base)

    # (2) POSITIVE CONTROL: PRIOR_GATE reproduces v3 op halluc within tol.
    prior = _gate_metrics(recs, keep_fn=_prior_keep)
    assert abs(prior["halluc"] - PRIOR_OP_HALLUC) <= PRIOR_OP_HALLUC_TOL, \
        "PRIOR_GATE halluc=%.4f not within %.3f of v3 op %.4f" % (prior["halluc"], PRIOR_OP_HALLUC_TOL, PRIOR_OP_HALLUC)

    # (3) the KEY can-fail: NP-head flags the residual N6/W18 (nonhead) and NOT head answers house/henry.
    by_qid = {r["q"]["qid"]: r for r in recs}
    for q in ("N6", "W18"):
        assert by_qid[q]["ans"] == "log", "%s ans expected 'log' got %r" % (q, by_qid[q]["ans"])
        assert by_qid[q]["np_status"] == "nonhead", "%s 'log' expected NP nonhead" % q
        assert by_qid[q]["np_correction"] == "house", "%s correction expected 'house' got %r" % (q, by_qid[q]["np_correction"])
    # head answers must NOT be flagged (guards false-abstain)
    assert NP.np_head_status("house", O.TEST_PASSAGES["L26_patty"], O.pos_tag_sentence, O.split_sentences) == "head"
    assert NP.np_head_status("henry", O.TEST_PASSAGES["L14_henry"], O.pos_tag_sentence, O.split_sentences) == "head"

    # (4) NO gold leakage: np_head_status result is invariant to the gold (recompute ignoring gold).
    for r in recs[:5]:
        s2 = NP.np_head_status(r["ans"], O.TEST_PASSAGES[r["q"]["p"]], O.pos_tag_sentence, O.split_sentences)
        assert s2 == r["np_status"], "np-head not a pure fn of (ans, passage)"

    # (5) ONE variable: NEW_GATE differs from PRIOR_GATE on >=1 record.
    changed = [r for r in recs if _prior_keep(r) != _new_keep(r)]
    assert changed, "NP-head changes NO keep decision -- one variable inert (v1 == v3)"

    # (6) run + arms differ.
    full = _run_from_recs(recs, scale)
    _arms_differ(full)
    tier, outcome, msg, _loc = compute_verdict(full)
    c = full["nphead_contribution"]
    print("[self-test] PASS | PRIOR halluc=%.4f (v3 op %.4f) | NEW halluc=%.4f retained=%.3f | nphead caught "
          "prior-residual %d/%d %s | false-abstain=%d | tier=%s"
          % (prior["halluc"], PRIOR_OP_HALLUC, full["operating_point"]["halluc"], full["retained_correct_frac"],
             c["n_prior_residual_caught_by_nphead"], c["n_prior_residual"], c["nphead_caught_qids"],
             c["n_correct_false_abstained_by_nphead"], tier), flush=True)
    return True


def run(run_mode):
    qs = list(O.TEST_QS)
    if run_mode == "smoke":
        smoke_pids = {"L2_cat", "L18_king", "L35_willie", "L26_patty", "L21_bee", "L32_tiger", "L14_henry"}
        qs = [q for q in qs if q["p"] in smoke_pids]
    out_dir = _out_dir(run_mode)
    _write_start_marker(out_dir, run_mode, expected_n_units=len(qs))
    t0 = time.perf_counter()

    clf = V1.build_clf()
    recs, _stores, scale = _build(clf, qs)
    res = _run_from_recs(recs, scale)
    digests, arms_exempted = _arms_differ(res)
    tier, outcome, msg, localize = compute_verdict(res)
    elapsed = time.perf_counter() - t0

    op = res["operating_point"]
    c = res["nphead_contribution"]
    metrics = {
        "anchor_name": ANCHOR_NAME, "verdict": tier, "verdict_msg": msg, "summary": msg[:300],
        "gate_outcome": outcome, "run_mode": run_mode, "elapsed_s": round(elapsed, 4),
        "ts_iso": datetime.now(timezone.utc).isoformat(), "n_questions": len(qs),
        "corpus": "mcguffey_second_reader_in_domain",
        "arms": ["NO_GATE", "PRIOR_GATE", "NEW_GATE", "SCRAMBLE_GATE"],
        "threshold_frozen": True, "fixed_threshold": FIXED_TH,
        "threshold_source": "exp_multi_turn_loop_realtext_confidence_abstain_gate_v3 McGuffey operating_point",
        "no_retune": True,
        "gate_signal": "coref_margin_OR_match_conflict_OR_np_head_inconsistency_union_of_abstentions_FROZEN_th",
        "one_variable_vs_v3": "added the STRUCTURAL NP-head-consistency abstention (keep = coref>th AND NOT "
                              "conflict AND np_head_consistent) vs v3 keep = coref>th AND NOT conflict",
        "np_head_rule": "answer noun is trustworthy iff it occurs as the HEAD (rightmost noun of its "
                        "noun-run) of its NP; abstain when it occurs ONLY as an adjective / compound-noun "
                        "modifier / proper-noun title (a pre-modifier). POS-only; reads no gold.",
        "n_answerable": res["baseline"]["n_answered"],
        "baseline_no_gate": res["baseline"], "prior_gate": res["prior_gate"],
        "operating_point": op, "retained_correct_frac": res["retained_correct_frac"],
        "scramble_matched_coverage": res["scramble"], "beat_scramble": res["beat_scramble"],
        "nphead_contribution": res["nphead_contribution"], "auc": res["auc"],
        "margin_scale": res["margin_scale"],
        "confidence_signals": ["coref_margin(maintained-overlay salience gap) -- ranking",
                               "match_conflict(store returns >1 distinct answer) -- flag",
                               "np_head_consistency(answer is NP head vs pre-modifier) -- NEW structural flag"],
        "gate_threshold_kind": "fixed_interpretable_rule_FROZEN_from_v3_no_retune",
        "bands": {"HP_halluc_max": HP_HALLUC_MAX, "HP_retained_min": HP_RETAINED_MIN,
                  "HP_precision_min": HP_PRECISION_MIN, "HF_halluc_max_soft": HF_HALLUC_MAX_SOFT,
                  "HF_retained_max": HF_RETAINED_MAX},
        "weakest_interface": localize,
        "arms_differ_digests": digests, "arms_differ_verified": True, "arms_differ_exempted": arms_exempted,
        "final_metrics_atomicity": "tmp_replace", "deterministic_seeding": True,
        "progress_logging": "print_flush_true", "compute_architecture": "sequential_cpu_pure_python",
        "crlb_n_a": "symbolic glass-box; halluc (truthfulness invariant) is the reported quantity",
        "per_question": res["_recs_debug"],
        "reuse_credited": {
            "gate_and_widened_corpus": "exp_multi_turn_loop_realtext_confidence_abstain_gate_v3.py "
                                       "(coref-OR-conflict gate; widened 53-Q McGuffey; op th=0.490995)",
            "pipeline_machinery": "exp_multi_turn_loop_realtext_confidence_abstain_gate_v1.py",
            "components_and_grounding": "exp_oracle_mention_upperbound_reader_v1.py",
            "np_head_signal": "experiments/_np_head_signal.py (glass-box structural NP-head-consistency)"},
        "REQUIRED_FIELDS": ["verdict", "baseline_no_gate", "prior_gate", "operating_point",
                            "retained_correct_frac", "scramble_matched_coverage", "beat_scramble",
                            "nphead_contribution", "arms_differ_digests", "gate_signal", "n_answerable",
                            "threshold_frozen", "fixed_threshold"],
        "notes": ("In-domain (McGuffey) test of the STRUCTURAL NP-head-consistency signal added to the "
                  "coref-OR-conflict trustworthy gate. ONE new variable vs v3: abstain when the answer is "
                  "an NP pre-modifier (adjective/compound-modifier/title) not the NP head. Frozen th; no "
                  "re-tune. Sister cell tests OOD transfer on LitBank. CLAIM-VET-pending."),
    }
    _write_metrics(out_dir, metrics)

    print("[%s:%s] %s" % (ANCHOR_NAME, run_mode, msg), flush=True)
    print("  [NO_GATE ] halluc=%.3f cov=%.3f (correct=%d wrong=%d of %d)"
          % (res["baseline"]["halluc"], res["baseline"]["coverage"], res["baseline"]["n_correct"],
             res["baseline"]["n_wrong"], res["baseline"]["n_total"]), flush=True)
    print("  [PRIOR   ] coref>%.4f&noconflict: halluc=%.4f cov=%.3f retained=%.3f (%d/%d)"
          % (FIXED_TH, res["prior_gate"]["halluc"], res["prior_gate"]["coverage"],
             res["prior_gate"]["retained_correct_frac"], res["prior_gate"]["n_correct_kept"],
             res["baseline"]["n_correct"]), flush=True)
    print("  [+NPHEAD ] NEW halluc=%.4f cov=%.3f prec=%.3f retained=%.3f (%d/%d)"
          % (op["halluc"], op["coverage"], op["precision_on_answered"], res["retained_correct_frac"],
             op["n_correct_kept"], res["baseline"]["n_correct"]), flush=True)
    print("  [NPHEAD  ] caught prior-residual %d/%d %s corrections=%s | false-abstain=%d %s | new-residual=%s"
          % (c["n_prior_residual_caught_by_nphead"], c["n_prior_residual"], c["nphead_caught_qids"],
             c["nphead_corrections"], c["n_correct_false_abstained_by_nphead"], c["false_abstained_qids"],
             c["new_residual_qids"]), flush=True)
    print("  [SCRAMBLE] matched-cov halluc_mean=%.3f -> NEW gate beats random by %.3f"
          % (res["scramble"]["halluc_mean"], res["beat_scramble"]), flush=True)
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
