"""exp_multi_turn_loop_litbank_ood_nphead_correct_v1 -- does correct-to-head COMPLETE the trustworthy reader
OUT OF DOMAIN? ONE new variable vs the 29467 LitBank ABSTAIN gate
(exp_multi_turn_loop_litbank_ood_nphead_gate_v1): on an NP-head-flagged non-head answer, instead of ABSTAINING,
RETURN THE NP HEAD as the answer (lord->henry, fair->man), UNCHANGED with the frozen McGuffey threshold on
verbatim LitBank literary prose.

CONTEXT: the 29467 LitBank ABSTAIN gate abstained on watch2 ("lord" for "Lord Henry", head "henry") and
mary1 ("fair" for "the fair young man", head "man"); the capstone showed the recovered head == gold in both.
This cell substitutes the head instead of abstaining and RECOMPUTES correctness vs gold -- the SAME
correct-to-head logic as the McGuffey sister cell (experiments/_np_head_correct_common.py), applied UNCHANGED.

    ABSTAIN (29467): keep = prior_keep AND np_head_consistent            (drop the non-head; no answer)
    CORRECT (this) : keep = prior_keep; on np non-head, answer := recovered NP head; recompute correctness

FROZEN threshold th=0.490995 (inherited; no re-tune -- the whole point is corpus-general transfer).

ARMS: NO_GATE | PRIOR_GATE | ABSTAIN_GATE (=29467 op) | CORRECT_GATE (THE mechanism).
Anti-cheat must-fail SCRAMBLE_CORRECT: substitute a RANDOM passage noun (not the head) on the same records.

BANDS (envelope-fail; set BEFORE the run; global halluc = wrong-answered / n_total on LitBank):
  HARD_PASS: n_corrected>=1 AND coverage RISES vs 29467-abstain AND every correction CORRECT
             (n_corrections_wrong==0, head==gold) AND op_halluc<=0.02 AND precision_on_answered>=0.90.
  HARD_FAIL: correct-to-head introduces a NEW OOD hallucination (head != gold, question about the MODIFIER,
             n_corrections_wrong>=1) OR op_halluc>0.05 OR precision<0.80 OR coverage did NOT rise.
  MIDDLE otherwise.

WHY GENUINELY CAN-FAIL: OOD adult-literary questions could be about the MODIFIER, OR the head recovered OOD
could differ from gold (full personal names, coordinations, adult POS drift) -> head != gold -> new
hallucination -> HARD_FAIL. The head-is-the-answer assumption is TESTED against the OOD gold, not assumed.

DESIGN-GATE (verified at self-test): (1) REAL 29467 LitBank record path reused; (2) FROZEN th inherited;
(3) mechanism FIRES (watch2->"henry", mary1->"man"); (4) ONE variable; (5) coverage RISES vs abstain;
(6) arms differ; (7) determinism; (8) head_eq_gold COMPUTED into the verdict, NOT asserted (preserves can-fail).

CELL-TEMPLATE (relevant subset; SCHEMA-VET gates N/A for this non-HD glass-box cell):
# - except SystemExit/KeyboardInterrupt: raise BEFORE except Exception (no BaseException)
# - ATOMIC final metrics write (tmp + os.replace)                    [META_RULE_AH]
# - ARMS-MUST-DIFFER hash check at run                               [META_RULE_AF]
# - discriminator CAN-FAIL (OOD head != gold -> HARD_FAIL) AND FIRES (corrects watch2/mary1)  [design-gate]
# - baseline_in_band: ABSTAIN reproduces 29467 op; CORRECT free to fail             [AG]
# - deterministic (fixed seed, OMP=1, no hash()-seed, sorted(set))       [F.5 / PROT-023]
# - start-marker + crash-diagnostic; heartbeat EXEMPT (wall < 90s)
# - crlb_n/a: symbolic glass-box; coverage-at-zero-halluc is the reported quantity
# - progress_logging: print_flush_true. gate_threshold: FIXED interpretable rule, FROZEN (no re-tune).
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

# L = the 29467 LitBank OOD ABSTAIN cell (owns O, FIXED_TH, _build, prior/abstain predicates, NP wiring).
# CC = the shared correct-to-head logic (BYTE-IDENTICAL to the McGuffey sister cell -- the transfer invariant).
import experiments.exp_multi_turn_loop_litbank_ood_nphead_gate_v1 as L
import experiments._np_head_correct_common as CC

O = L.O
ANCHOR_NAME = "multi_turn_loop_litbank_ood_nphead_correct_v1"
CORPUS_LABEL = "LitBank-OOD"
FIXED_TH = L.FIXED_TH
# expected NP-head corrections (MECHANISM check -- gold-free recovery; head_eq_gold is NOT asserted here)
EXPECTED_CORRECTIONS = {"watch2": "henry", "mary1": "man"}


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


def self_test():
    print("[self-test] building REAL 29467 LitBank pipeline (perceptron fit + POS + coref + conf) ...", flush=True)
    clf = L.V1.build_clf()
    recs, stores, scale = L._build(clf, O.TEST_QS)

    # (1) REAL code path: 29467 answers reproduce O.answer_reader exactly (no drift).
    for r in recs:
        base = O.normalize(O.answer_reader(r["q"]["spec"], stores.get(r["q"]["p"], [])))
        assert r["ans"] == base, "answer drift on %s: %r vs %r" % (r["q"]["qid"], r["ans"], base)

    cmap = CC._correct_map(L, recs)
    by_qid = {r["q"]["qid"]: r for r in recs}

    # (2) MECHANISM fires OOD: watch2 "lord"->head "henry", mary1 "fair"->head "man" (gold-free recovery).
    for qid, exp_head in EXPECTED_CORRECTIONS.items():
        r = by_qid[qid]
        assert r["np_status"] == "nonhead", "%s expected NP non-head; got status=%r" % (qid, r["np_status"])
        eff, _corr, flag = cmap[id(r)]
        assert flag and eff == exp_head, "%s expected correct-to-head %r; got %r (flag=%s)" % (qid, exp_head, eff, flag)

    # (3) mechanism actually corrected >=1 record (not inert OOD).
    audit = CC._correction_audit(L, recs, cmap)
    assert audit["n_corrected"] >= 1, "no NP-head correction fired OOD -- mechanism inert"

    # (4) ONE variable: CORRECT_GATE differs from ABSTAIN_GATE on >=1 record.
    diff = [r for r in recs if (cmap[id(r)][0] is not None) != L._new_keep(r) or
            (L._new_keep(r) and cmap[id(r)][0] != (r["ans"] if L._new_keep(r) else None))]
    assert diff, "CORRECT identical to ABSTAIN OOD -- one variable inert"

    # (5) coverage RISES vs 29467 abstain.
    abstain = CC._abstain_metrics(L, recs)
    correct = CC._correct_gate_metrics(L, recs, cmap)
    assert correct["coverage"] > abstain["coverage"], \
        "coverage did not rise OOD: abstain=%.4f correct=%.4f" % (abstain["coverage"], correct["coverage"])

    # (6) run + arms differ (head_eq_gold flows into the verdict; NOT asserted -> preserves can-fail).
    res = CC.run_correct(L, recs, scale)
    CC.arms_differ(res)
    tier, _outcome, _msg, _loc = CC.compute_verdict(L, res, CORPUS_LABEL)
    a = res["correction_audit"]
    print("[self-test] PASS | ABSTAIN halluc=%.4f cov=%.3f | CORRECT halluc=%.4f cov=%.3f (+%.4f) | "
          "corrections right=%d wrong=%d | head-beats-random=%.3f | tier=%s (head_eq_gold computed not asserted)"
          % (abstain["halluc"], abstain["coverage"], res["operating_point"]["halluc"],
             res["operating_point"]["coverage"], res["coverage_rise_vs_abstain"],
             a["n_corrections_right"], a["n_corrections_wrong"], res["beat_scramble"], tier), flush=True)
    return True


def run(run_mode):
    qs = list(O.TEST_QS)
    if run_mode == "smoke":
        smoke_pids = {"wall", "duke", "watch", "maryknew", "nippers", "taylor"}
        qs = [q for q in qs if q["p"] in smoke_pids]
    out_dir = _out_dir(run_mode)
    _write_start_marker(out_dir, run_mode, expected_n_units=len(qs))
    t0 = time.perf_counter()

    clf = L.V1.build_clf()
    recs, _stores, scale = L._build(clf, qs)
    res = CC.run_correct(L, recs, scale)
    digests = CC.arms_differ(res)
    tier, outcome, msg, localize = CC.compute_verdict(L, res, CORPUS_LABEL)
    elapsed = time.perf_counter() - t0

    op = res["operating_point"]
    a = res["correction_audit"]
    metrics = {
        "anchor_name": ANCHOR_NAME, "verdict": tier, "verdict_msg": msg, "summary": msg[:300],
        "gate_outcome": outcome, "run_mode": run_mode, "elapsed_s": round(elapsed, 4),
        "ts_iso": datetime.now(timezone.utc).isoformat(), "n_questions": len(qs),
        "corpus": "litbank_verbatim_out_of_domain",
        "corpus_provenance": {"source": "data/corpora/litbank_coref_conll/*.conll",
                              "n_passages": len(L.LB.LITBANK_WINDOWS),
                              "reconstruction": "verbatim_contiguous_token_subsequence",
                              "distinct_from_mcguffey": True},
        "arms": ["NO_GATE", "PRIOR_GATE", "ABSTAIN_GATE", "CORRECT_GATE"],
        "threshold_frozen": True, "fixed_threshold": FIXED_TH,
        "threshold_source": "exp_multi_turn_loop_realtext_confidence_abstain_gate_v3 McGuffey operating_point",
        "no_retune": True,
        "one_variable_vs_29467": "on an NP-head-flagged non-head answer, ABSTAIN (29467) -> RETURN THE NP HEAD "
                                 "(recompute correctness vs gold); frozen th; SAME correct-to-head logic as "
                                 "the McGuffey sister cell (the transfer invariant)",
        "correct_to_head_policy": "always-correct: substitute the recovered NP head when the prior-kept answer "
                                  "is an NP non-head with a recoverable head; else fall back to abstain",
        "transfer_test": {"key_question": "does correct-to-head COMPLETE the reader OOD as it does in-domain?",
                          "nphead_corrected_ood": a["corrected_qids"],
                          "corrections_all_correct_ood": a["n_corrections_wrong"] == 0 and a["n_corrected"] >= 1},
        "n_answerable": res["baseline"]["n_answered"],
        "baseline_no_gate": res["baseline"], "prior_gate": res["prior_gate"],
        "abstain_gate_29467": res["abstain_gate"], "operating_point": op,
        "coverage_rise_vs_abstain": res["coverage_rise_vs_abstain"],
        "n_recovered_to_answer": res["n_recovered_to_answer"],
        "correction_audit": a, "retained_correct_frac": res["retained_correct_frac"],
        "scramble_random_noun_matched_coverage": res["scramble_random_noun"],
        "beat_scramble_head_vs_random_noun": res["beat_scramble"], "margin_scale": res["margin_scale"],
        "head_is_answer_assumption": {
            "holds_on_all_flagged": a["head_is_answer_assumption_holds"],
            "n_corrections_right": a["n_corrections_right"], "n_corrections_wrong": a["n_corrections_wrong"],
            "caveat": "empirical OOD (small n); a question genuinely about the MODIFIER would make the head != "
                      "gold and correct-to-head WRONG -- measured, not assumed"},
        "gate_threshold_kind": "fixed_interpretable_rule_FROZEN_from_29467_no_retune",
        "bands": CC.bands_dict(), "weakest_interface": localize,
        "arms_differ_digests": digests, "arms_differ_verified": True,
        "final_metrics_atomicity": "tmp_replace", "deterministic_seeding": True,
        "progress_logging": "print_flush_true", "compute_architecture": "sequential_cpu_pure_python",
        "crlb_n_a": "symbolic glass-box; coverage-at-zero-halluc is the reported quantity",
        "per_question": res["_recs_debug"],
        "reuse_credited": {
            "abstain_gate_and_corpus": "exp_multi_turn_loop_litbank_ood_nphead_gate_v1.py (29467 LitBank ABSTAIN "
                                       "gate; verbatim LitBank corpus; NP-head signal; frozen th=0.490995)",
            "correct_to_head_logic": "experiments/_np_head_correct_common.py (IDENTICAL to McGuffey cell -- "
                                     "the transfer invariant)",
            "np_head_signal": "experiments/_np_head_signal.py (np_head_correction -- gold-free head recovery)"},
        "REQUIRED_FIELDS": ["verdict", "baseline_no_gate", "prior_gate", "abstain_gate_29467",
                            "operating_point", "coverage_rise_vs_abstain", "correction_audit", "transfer_test",
                            "scramble_random_noun_matched_coverage", "beat_scramble_head_vs_random_noun",
                            "arms_differ_digests", "n_answerable", "threshold_frozen", "fixed_threshold"],
        "notes": ("Out-of-domain (LitBank) COMPLETION of the trustworthy reader: correct NP-head abstentions to "
                  "the recovered head instead of abstaining, UNCHANGED with the frozen McGuffey threshold. "
                  "ONE new variable vs 29467. Genuine can-fail: OOD head != gold. Correct-to-head logic "
                  "IDENTICAL to the McGuffey sister cell. CLAIM-VET-pending."),
    }
    _write_metrics(out_dir, metrics)

    print("[%s:%s] %s" % (ANCHOR_NAME, run_mode, msg), flush=True)
    print("  [NO_GATE ] halluc=%.3f cov=%.3f (correct=%d wrong=%d of %d)"
          % (res["baseline"]["halluc"], res["baseline"]["coverage"], res["baseline"]["n_correct"],
             res["baseline"]["n_wrong"], res["baseline"]["n_total"]), flush=True)
    print("  [PRIOR   ] halluc=%.4f cov=%.3f | [29467-ABSTAIN] halluc=%.4f cov=%.3f"
          % (res["prior_gate"]["halluc"], res["prior_gate"]["coverage"],
             res["abstain_gate"]["halluc"], res["abstain_gate"]["coverage"]), flush=True)
    print("  [CORRECT ] halluc=%.4f cov=%.3f prec=%.3f | coverage +%.4f (%d abstentions -> answers)"
          % (op["halluc"], op["coverage"], op["precision_on_answered"], res["coverage_rise_vs_abstain"],
             res["n_recovered_to_answer"]), flush=True)
    print("  [AUDIT   ] corrections right=%d wrong=%d %s | corrections=%s"
          % (a["n_corrections_right"], a["n_corrections_wrong"], a["wrong_correction_qids"], a["corrections"]),
          flush=True)
    print("  [SCRAMBLE] head vs random-noun: correct halluc=%.4f random halluc=%.4f -> head beats random by %.3f"
          % (op["halluc"], res["scramble_random_noun"]["halluc_mean"], res["beat_scramble"]), flush=True)
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
