"""exp_multi_turn_loop_litbank_ood_nphead_gate_v1 -- does the STRUCTURAL NP-head-consistency signal
TRANSFER out-of-domain? ONE new variable vs the LitBank frozen gate (29466): a UNION abstention on
NP-head-inconsistency, applied UNCHANGED with the FROZEN McGuffey threshold on LitBank literary prose.

CONTEXT + KEY HYPOTHESIS: exp_multi_turn_loop_litbank_ood_fixed_gate_v1 (MIDDLE_BAND, 29466) applied the
McGuffey-tuned coref-OR-conflict gate (frozen th=0.490995) to out-of-domain LitBank prose and left
op_halluc=0.0952 MEASURED@data/exp_multi_turn_loop_litbank_ood_fixed_gate_v1/metrics.json:operating_point
.halluc. Its 2 residual confident-wrong answers are BOTH NP-HEAD-selection errors that the coref margin
and match-conflict flag cannot see (coref=1.0, n_distinct=1):
    watch2: answer "lord" for "Lord Henry pulled out his watch" (gold "henry") -- proper-noun TITLE part.
    mary1 : answer "fair" for "Mary knew the fair young man"   (gold "man")   -- ADJECTIVE pre-modifier.
The coref-margin signal was INERT out-of-domain (OOD coref-AUC=0.433 CITED@29466). The KEY HYPOTHESIS:
NP structure is corpus-GENERAL, so a structural NP-head check should TRANSFER where the corpus-specific
coref margin did not -- it should catch watch2 + mary1 on LitBank exactly as it catches "log house" on
McGuffey (sister cell exp_multi_turn_loop_realtext_nphead_gate_v1).

THE ONE NEW VARIABLE (BYTE-IDENTICAL signal to the McGuffey sister cell -- the transfer claim):
    prior: keep = is_answered AND coref>FIXED_TH AND NOT conflict(rec)                        (= 29466)
    new  : keep = is_answered AND coref>FIXED_TH AND NOT conflict(rec) AND np_head_consistent(rec)  [+NP-head]
FROZEN threshold (no re-tune) -- the whole point is transfer, not fitting LitBank. NP-head signal =
experiments/_np_head_signal.py, the SAME function the McGuffey cell uses (a title-vs-name-aware,
POS-only, gold-free structural check).

ARMS:
  NO_GATE      = REAL pipeline answers everything it commits.
  PRIOR_GATE   = frozen coref-OR-conflict gate (reproduces 29466 op: halluc=0.0952, residual watch2/mary1).
  NEW_GATE     = PRIOR_GATE AND NP-head-consistent (THE MECHANISM; the ONE added, corpus-general variable).
  SCRAMBLE_GATE= anti-cheat must-fail: matched-coverage RANDOM abstention at NEW_GATE coverage.

BANDS (envelope-fail; set BEFORE the run; global halluc = wrong-answered / n_total on LitBank n=21):
  HARD_PASS (the STRUCTURAL signal TRANSFERS -- lowers OOD halluc where the corpus-specific margin was inert):
      new_op_halluc <= 0.06 AND
      precision_on_answered >= 0.80 AND
      (scramble_halluc - new_op_halluc) >= 0.05 AND
      prior residual (>=1 wrong that survived coref+conflict) is FULLY caught by NP-head AND
      NP-head falsely-abstains ZERO correct answers PRIOR_GATE kept (no coverage collapse / no new errors).
  HARD_FAIL (the signal does NOT transfer / creates errors):
      NP-head does NOT catch the full prior residual (does NOT transfer), OR
      new_op_halluc > 0.10, OR
      (scramble_halluc - new_op_halluc) <= 0.0, OR
      NP-head falsely-abstains a correct answer (new OOD errors).
  MIDDLE otherwise (0.06 < halluc <= 0.10 -- partial OOD transfer).

WHY GENUINELY CAN-FAIL: the adult-literary POS tagging may differ from grade-2 (e.g. "lord"/"fair"
mis-tagged as a head noun -> NP-head does not fire and the residual survives -> no transfer), OR NP-head
may falsely flag a correct OOD answer (full personal names, coordinations) -> new errors. If the
structural signal is inert OR harmful OOD, HARD_FAIL. The data decides whether structure transfers where
the margin did not. Correction-to-head ("lord"->"henry", "fair"->"man") is a DIAGNOSTIC only.

DESIGN-GATE (verified at self-test): (1) VERBATIM provenance (reused from 29466 corpus builder); (2) FROZEN
threshold == v3 McGuffey op-point (asserted; NO re-tune); (3) real code path; (4) POSITIVE-CONTROL
PRIOR_GATE reproduces 29466 op halluc; (5) NP-head signal BYTE-IDENTICAL to McGuffey cell (imported, not
re-typed); (6) NP-head reads NO gold; (7) ONE variable -- NEW_GATE differs from PRIOR_GATE on >=1 record;
(8) arms differ; (9) determinism (OMP=1, fixed seed, sorted set, no hash()-seeding).

CELL-TEMPLATE (relevant subset; many SCHEMA-VET gates N/A for this non-HD glass-box cell):
# - except SystemExit/KeyboardInterrupt: raise BEFORE except Exception (no BaseException)
# - ATOMIC final metrics write (tmp + os.replace)                    [META_RULE_AH: tmp_replace]
# - ARMS-MUST-DIFFER hash check at run                               [META_RULE_AF]
# - discriminator CAN-FAIL (OOD POS mis-tag OR false-abstain) AND FIRES (catches watch2/mary1)  [design-gate]
# - FROZEN threshold; NP-head signal IDENTICAL to McGuffey cell (the transfer invariant)
# - real_code_path: self-test builds the REAL perceptron + POS + WorkingOverlay + conf-extract on LitBank
# - baseline_in_band: PRIOR_GATE reproduces 29466 op; gate free to fail                    [AG]
# - deterministic (fixed seed, OMP=1, no hash()-seed, sorted(set))                [F.5 / PROT-023]
# - start-marker + crash-diagnostic; heartbeat EXEMPT (wall < 90s)
# - crlb_n/a: symbolic glass-box; halluc (truthfulness invariant) is the reported quantity
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

# LB installs the verbatim LitBank corpus into O at import + supplies the frozen-gate record builder.
# V1 supplies the underlying machinery (extractor, scramble, AUC). NP = the shared structural signal.
import experiments.exp_multi_turn_loop_litbank_ood_fixed_gate_v1 as LB
import experiments.exp_multi_turn_loop_realtext_confidence_abstain_gate_v1 as V1
import experiments._np_head_signal as NP

O = LB.O

ANCHOR_NAME = "multi_turn_loop_litbank_ood_nphead_gate_v1"

SEED = V1.SEED
N_SCRAMBLE_SEEDS = V1.N_SCRAMBLE_SEEDS
N_BOOT = V1.N_BOOT
GATE_SIGNAL_KEY = "coref_conf"

# FROZEN McGuffey operating point (the whole point: NO re-tune on the new corpus). CITED@v3 op-point.
FIXED_TH = LB.FIXED_TH               # 0.490995 (asserted == v3 op-point in LB.self_test)
PRIOR_OP_HALLUC = 0.0952            # CITED@data/exp_multi_turn_loop_litbank_ood_fixed_gate_v1/metrics.json
PRIOR_OP_HALLUC_TOL = 0.02
MCGUFFEY_OP_HALLUC = LB.MCGUFFEY_OP_HALLUC

# pre-registered bands (HYPOTHESIZED@this prereg)
HP_HALLUC_MAX = 0.06
HP_PRECISION_MIN = 0.80
HP_BEAT_SCRAMBLE_MIN = 0.05
HF_HALLUC_MIN = 0.10
HF_BEAT_SCRAMBLE_MAX = 0.0


def _conflict(rec):
    return rec.get("n_distinct", 0) > 1


def _sig(rec):
    return rec[GATE_SIGNAL_KEY]


def _np_ok(rec):
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
    wrongs = [r for r in recs if r["is_answered"] and r["correct"] == 0]
    caught_conflict = [r for r in wrongs if _conflict(r)]
    caught_coref = [r for r in wrongs if (not _conflict(r)) and _sig(r) <= FIXED_TH]
    prior_residual = [r for r in wrongs if _prior_keep(r)]
    nphead_catch = [r for r in prior_residual if not _np_ok(r)]
    new_residual = [r for r in prior_residual if _np_ok(r)]
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
        "mcguffey_reference": {"op_halluc": MCGUFFEY_OP_HALLUC, "threshold": FIXED_TH},
        "_answers": {"NO_GATE": no_gate_answers, "PRIOR_GATE": prior_answers,
                     "NEW_GATE": new_answers, "SCRAMBLE_GATE": scramble_answers},
        "_recs_debug": [{"qid": r["q"]["qid"], "p": r["q"]["p"], "text": r["q"]["text"], "ans": r["ans"],
                         "gold": r["gold"], "coref_conf": r.get("coref_conf"), "conflict": _conflict(r),
                         "n_distinct": r["n_distinct"], "np_status": r["np_status"],
                         "np_correction": r["np_correction"], "correct": r["correct"],
                         "prior_kept": _prior_keep(r), "new_kept": _new_keep(r)} for r in recs],
    }


def _arms_differ(res):
    digests = {n: hashlib.sha256(json.dumps(res["_answers"][n], sort_keys=True).encode()).hexdigest()
               for n in ("NO_GATE", "PRIOR_GATE", "NEW_GATE", "SCRAMBLE_GATE")}
    assert digests["NO_GATE"] != digests["PRIOR_GATE"], "META_RULE_AF: NO_GATE == PRIOR_GATE"
    assert digests["PRIOR_GATE"] != digests["NEW_GATE"], \
        "META_RULE_AF: NEW_GATE == PRIOR_GATE (NP-head abstained on nothing OOD -- signal inert)"
    exempted = []
    if res["operating_point"]["coverage"] == 0.0:
        exempted.append(["NEW_GATE", "SCRAMBLE_GATE"])
    else:
        assert digests["NEW_GATE"] != digests["SCRAMBLE_GATE"], "META_RULE_AF: NEW_GATE == SCRAMBLE_GATE"
    return digests, exempted


def compute_verdict(res):
    op = res["operating_point"]
    op_halluc = op["halluc"]
    precision = op["precision_on_answered"]
    beat = res["beat_scramble"]
    c = res["nphead_contribution"]
    transfers = (c["n_prior_residual"] >= 1 and
                 c["n_prior_residual_caught_by_nphead"] == c["n_prior_residual"])
    no_new_errors = c["n_correct_false_abstained_by_nphead"] == 0

    hp = (op_halluc <= HP_HALLUC_MAX and precision >= HP_PRECISION_MIN and beat >= HP_BEAT_SCRAMBLE_MIN
          and transfers and no_new_errors)
    hf = ((not transfers) or op_halluc > HF_HALLUC_MIN or beat <= HF_BEAT_SCRAMBLE_MAX
          or (not no_new_errors))

    if hp:
        tier, outcome = "HARD_PASS", "structural-nphead-signal-TRANSFERS-lowers-ood-halluc-margin-was-inert"
    elif hf:
        tier, outcome = "HARD_FAIL", "nphead-does-not-transfer-or-creates-ood-errors-or-no-beat"
    else:
        tier, outcome = "MIDDLE_BAND", "partial-ood-transfer-halluc-lowered-not-to-floor"

    localize = []
    if not transfers:
        localize.append("NP-head did NOT transfer: caught %d of %d prior residual (%s); OOD residual %s "
                        "survives (POS mis-tag OR construction NP-head cannot see)"
                        % (c["n_prior_residual_caught_by_nphead"], c["n_prior_residual"],
                           c["nphead_caught_qids"], c["new_residual_qids"]))
    if not no_new_errors:
        localize.append("NP-head falsely abstained %d CORRECT OOD answers (new errors): %s"
                        % (c["n_correct_false_abstained_by_nphead"], c["false_abstained_qids"]))
    if beat <= HF_BEAT_SCRAMBLE_MAX:
        localize.append("NEW gate no better than random abstention OOD: beat=%.3f" % beat)
    if not localize:
        localize.append("STRUCTURAL NP-head TRANSFERS OOD: caught %s (corrections->gold: %s) where the "
                        "corpus-specific coref margin was INERT (OOD coref-AUC=%.3f); op_halluc %.4f->%.4f "
                        "(McGuffey %.4f), zero false-abstain, beat=%.3f"
                        % (c["nphead_caught_qids"], c["nphead_corrections"], res["auc"]["coref_only"],
                           res["prior_gate"]["halluc"], op_halluc, MCGUFFEY_OP_HALLUC, beat))

    msg = ("%s (%s) | LitBank-OOD n_total=%d n_answerable=%d n_correct=%d | NO_GATE halluc=%.3f | "
           "PRIOR_GATE@coref>%.4f&noconflict: halluc=%.4f cov=%.3f (= 29466) | +NP-HEAD NEW_GATE: "
           "halluc=%.4f cov=%.3f prec=%.3f retained=%.3f (%d/%d) | nphead TRANSFER caught %d/%d %s | "
           "false-abstain=%d %s | new-residual=%s | scramble=%.3f beat=%.3f | OOD coref-AUC=%.3f (inert)" % (
               tier, outcome, res["baseline"]["n_total"], res["baseline"]["n_answered"],
               res["baseline"]["n_correct"], res["baseline"]["halluc"], FIXED_TH,
               res["prior_gate"]["halluc"], res["prior_gate"]["coverage"], op_halluc, op["coverage"],
               precision, res["retained_correct_frac"], op["n_correct_kept"], res["baseline"]["n_correct"],
               c["n_prior_residual_caught_by_nphead"], c["n_prior_residual"], c["nphead_caught_qids"],
               c["n_correct_false_abstained_by_nphead"], c["false_abstained_qids"], c["new_residual_qids"],
               res["scramble"]["halluc_mean"], beat, res["auc"]["coref_only"]))
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
    recs, stores, scale = LB._build_records(clf, qs)
    _attach_np(recs)
    return recs, stores, scale


def self_test():
    print("[self-test] building REAL pipeline (perceptron fit + conf-extractor) on LitBank ...", flush=True)

    # (0) FROZEN threshold matches v3 McGuffey op-point (LB asserts this too; belt-and-suspenders).
    if LB.V3_METRICS_PATH.exists():
        v3 = json.load(open(LB.V3_METRICS_PATH, encoding="utf-8"))
        v3_th = v3.get("operating_point", {}).get("threshold")
        assert v3_th is not None and abs(v3_th - FIXED_TH) < 1e-6, \
            "FROZEN th %.6f != v3 op-point %r" % (FIXED_TH, v3_th)

    # (1) VERBATIM provenance (reuse LB's own provenance self-test primitives).
    for pid, (work, a, b) in LB.LITBANK_WINDOWS.items():
        doc_toks = [t for s in LB._doc_sentences(work) for t in s]
        win_toks = LB._window_tokens(work, a, b)
        assert any(doc_toks[s:s + len(win_toks)] == win_toks
                   for s in range(0, len(doc_toks) - len(win_toks) + 1)), \
            "PROVENANCE BREACH: %s not a verbatim subsequence of %s" % (pid, work)

    clf = V1.build_clf()
    recs, stores, scale = _build(clf, O.TEST_QS)

    # (2) POSITIVE CONTROL: NO_GATE reproduces O.answer_reader exactly (real code path).
    for r in recs:
        base = O.normalize(O.answer_reader(r["q"]["spec"], stores.get(r["q"]["p"], [])))
        assert r["ans"] == base, "answer drift on %s: %r vs %r" % (r["q"]["qid"], r["ans"], base)

    # (3) POSITIVE CONTROL: PRIOR_GATE reproduces 29466 op halluc within tol.
    prior = _gate_metrics(recs, keep_fn=_prior_keep)
    assert abs(prior["halluc"] - PRIOR_OP_HALLUC) <= PRIOR_OP_HALLUC_TOL, \
        "PRIOR_GATE halluc=%.4f not within %.3f of 29466 op %.4f" % (prior["halluc"], PRIOR_OP_HALLUC_TOL, PRIOR_OP_HALLUC)

    # (4) the KEY can-fail / TRANSFER: NP-head flags watch2/mary1 (nonhead) and NOT head answers henry/man.
    by_qid = {r["q"]["qid"]: r for r in recs}
    assert by_qid["watch2"]["ans"] == "lord" and by_qid["watch2"]["np_status"] == "nonhead", \
        "watch2 'lord' expected NP nonhead; got ans=%r status=%r" % (by_qid["watch2"]["ans"], by_qid["watch2"]["np_status"])
    assert by_qid["watch2"]["np_correction"] == "henry", "watch2 correction expected 'henry'"
    assert by_qid["mary1"]["ans"] == "fair" and by_qid["mary1"]["np_status"] == "nonhead", \
        "mary1 'fair' expected NP nonhead; got ans=%r status=%r" % (by_qid["mary1"]["ans"], by_qid["mary1"]["np_status"])
    assert by_qid["mary1"]["np_correction"] == "man", "mary1 correction expected 'man'"
    assert NP.np_head_status("henry", O.TEST_PASSAGES["watch"], O.pos_tag_sentence, O.split_sentences) == "head"
    assert NP.np_head_status("man", O.TEST_PASSAGES["maryknew"], O.pos_tag_sentence, O.split_sentences) == "head"

    # (5) NP-head reads NO gold (pure fn of ans+passage).
    for r in recs[:5]:
        s2 = NP.np_head_status(r["ans"], O.TEST_PASSAGES[r["q"]["p"]], O.pos_tag_sentence, O.split_sentences)
        assert s2 == r["np_status"], "np-head not a pure fn of (ans, passage)"

    # (6) ONE variable: NEW_GATE differs from PRIOR_GATE on >=1 record.
    assert any(_prior_keep(r) != _new_keep(r) for r in recs), "NP-head changes NO keep decision OOD -- inert"

    # (7) run + arms differ.
    full = _run_from_recs(recs, scale)
    _arms_differ(full)
    tier, outcome, msg, _loc = compute_verdict(full)
    c = full["nphead_contribution"]
    print("[self-test] PASS | PRIOR halluc=%.4f (29466 op %.4f) | NEW halluc=%.4f | nphead TRANSFER caught "
          "%d/%d %s | false-abstain=%d | beat=%.3f | tier=%s"
          % (prior["halluc"], PRIOR_OP_HALLUC, full["operating_point"]["halluc"],
             c["n_prior_residual_caught_by_nphead"], c["n_prior_residual"], c["nphead_caught_qids"],
             c["n_correct_false_abstained_by_nphead"], full["beat_scramble"], tier), flush=True)
    return True


def run(run_mode):
    qs = list(O.TEST_QS)
    if run_mode == "smoke":
        smoke_pids = {"wall", "duke", "watch", "maryknew", "nippers", "taylor"}
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
        "corpus": "litbank_verbatim_out_of_domain",
        "corpus_provenance": {"source": "data/corpora/litbank_coref_conll/*.conll",
                              "n_passages": len(LB.LITBANK_WINDOWS),
                              "works": sorted(set(w for (w, _a, _b) in LB.LITBANK_WINDOWS.values())),
                              "reconstruction": "verbatim_contiguous_token_subsequence",
                              "distinct_from_mcguffey": True},
        "arms": ["NO_GATE", "PRIOR_GATE", "NEW_GATE", "SCRAMBLE_GATE"],
        "threshold_frozen": True, "fixed_threshold": FIXED_TH,
        "threshold_source": "exp_multi_turn_loop_realtext_confidence_abstain_gate_v3 McGuffey operating_point",
        "no_retune": True,
        "gate_signal": "coref_margin_OR_match_conflict_OR_np_head_inconsistency_union_of_abstentions_FROZEN_th",
        "one_variable_vs_29466": "added the STRUCTURAL NP-head-consistency abstention (identical signal to "
                                 "the McGuffey sister cell) to the frozen coref-OR-conflict gate",
        "np_head_rule": "answer noun trustworthy iff it occurs as the HEAD (rightmost noun of its "
                        "noun-run) of its NP; abstain when it occurs ONLY as an adjective / compound-noun "
                        "modifier / proper-noun TITLE (title-vs-name aware). POS-only; reads no gold.",
        "transfer_test": {"key_question": "does the STRUCTURAL signal TRANSFER OOD where the corpus-"
                          "specific coref margin was INERT (OOD coref-AUC=0.433 CITED@29466)?",
                          "ood_coref_auc_measured": res["auc"]["coref_only"],
                          "nphead_caught_ood_residual": c["nphead_caught_qids"],
                          "nphead_transfers": c["n_prior_residual"] >= 1 and
                          c["n_prior_residual_caught_by_nphead"] == c["n_prior_residual"]},
        "n_answerable": res["baseline"]["n_answered"],
        "baseline_no_gate": res["baseline"], "prior_gate": res["prior_gate"],
        "operating_point": op, "retained_correct_frac": res["retained_correct_frac"],
        "scramble_matched_coverage": res["scramble"], "beat_scramble": res["beat_scramble"],
        "nphead_contribution": res["nphead_contribution"], "mcguffey_reference": res["mcguffey_reference"],
        "auc": res["auc"], "margin_scale": res["margin_scale"],
        "confidence_signals": ["coref_margin(maintained-overlay salience gap) -- ranking (INERT OOD)",
                               "match_conflict(store returns >1 distinct answer) -- flag",
                               "np_head_consistency(answer is NP head vs pre-modifier) -- NEW structural flag"],
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
            "frozen_gate_and_corpus": "exp_multi_turn_loop_litbank_ood_fixed_gate_v1.py (frozen coref-OR-"
                                      "conflict gate; verbatim LitBank corpus; 29466 op halluc=0.0952 CITED)",
            "pipeline_machinery": "exp_multi_turn_loop_realtext_confidence_abstain_gate_v1.py",
            "components_and_grounding": "exp_oracle_mention_upperbound_reader_v1.py",
            "np_head_signal": "experiments/_np_head_signal.py (IDENTICAL to McGuffey sister cell -- the "
                              "transfer invariant)"},
        "REQUIRED_FIELDS": ["verdict", "baseline_no_gate", "prior_gate", "operating_point",
                            "retained_correct_frac", "scramble_matched_coverage", "beat_scramble",
                            "nphead_contribution", "transfer_test", "arms_differ_digests", "gate_signal",
                            "n_answerable", "threshold_frozen", "fixed_threshold"],
        "notes": ("Out-of-domain TRANSFER test of the STRUCTURAL NP-head-consistency signal. The SAME "
                  "gold-free, POS-only NP-head function that fixes the McGuffey 'log house' residual is "
                  "applied UNCHANGED with the frozen McGuffey threshold to verbatim LitBank literary prose. "
                  "Measures whether structure TRANSFERS where the corpus-specific coref margin was inert. "
                  "CLAIM-VET-pending."),
    }
    _write_metrics(out_dir, metrics)

    print("[%s:%s] %s" % (ANCHOR_NAME, run_mode, msg), flush=True)
    print("  [NO_GATE ] halluc=%.3f cov=%.3f (correct=%d wrong=%d of %d)"
          % (res["baseline"]["halluc"], res["baseline"]["coverage"], res["baseline"]["n_correct"],
             res["baseline"]["n_wrong"], res["baseline"]["n_total"]), flush=True)
    print("  [PRIOR   ] coref>%.4f&noconflict: halluc=%.4f cov=%.3f (= 29466)"
          % (FIXED_TH, res["prior_gate"]["halluc"], res["prior_gate"]["coverage"]), flush=True)
    print("  [+NPHEAD ] NEW halluc=%.4f cov=%.3f prec=%.3f retained=%.3f (%d/%d)"
          % (op["halluc"], op["coverage"], op["precision_on_answered"], res["retained_correct_frac"],
             op["n_correct_kept"], res["baseline"]["n_correct"]), flush=True)
    print("  [TRANSFER] nphead caught OOD residual %d/%d %s corrections=%s | false-abstain=%d %s | OOD coref-AUC=%.3f (inert)"
          % (c["n_prior_residual_caught_by_nphead"], c["n_prior_residual"], c["nphead_caught_qids"],
             c["nphead_corrections"], c["n_correct_false_abstained_by_nphead"], c["false_abstained_qids"],
             res["auc"]["coref_only"]), flush=True)
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
