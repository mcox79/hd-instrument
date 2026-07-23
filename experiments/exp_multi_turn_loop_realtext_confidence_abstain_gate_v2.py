"""exp_multi_turn_loop_realtext_confidence_abstain_gate_v2 -- COREF-MARGIN-ONLY abstain gate.

FRESH PRE-REGISTERED TEST (NOT a retro-fit of v1). v1
(exp_multi_turn_loop_realtext_confidence_abstain_gate_v1, MIDDLE_BAND @HEAD abc39fcb9) gated on
rel_conf = min(parse_margin, coref_margin). Its threshold-free component AUCs REVEALED where the
glass-box confidence discrimination lives:
  - COREF salience margin AUC(conf,correct) = 0.885 MEASURED@data/exp_multi_turn_loop_realtext_confidence_abstain_gate_v1/metrics.json:auc.coref_only
  - PARSE role-assignment margin AUC        = 0.188 MEASURED@...:auc.parse_only  (ANTI-informative:
    confident mis-parses / high-margin role-reversals ARE a confabulation source, so a HIGH parse
    margin correlates with a WRONG answer -> AUC below 0.5).
  - min(parse,coref) combined AUC           = the v1 gate signal, dragged DOWN by the anti-informative
    parse term; the v1 operating gate cleared halluc<=0.05 only at coverage 0.161 (retained_correct
    LOW) because low-parse-margin CORRECT answers were needlessly abstained.

HYPOTHESIS (pre-registered BEFORE this run): DROPPING the anti-informative parse term and gating on the
COREF SALIENCE MARGIN ALONE operationalizes the 0.885 signal into a real single-threshold gate that
keeps hallucination near-zero at MUCH better coverage than v1's 0.161 -- into the HARD_PASS band. The
coref margin is low exactly when a pronoun was resolved on a near-tie salience (the cross-turn
confabulation signature); gating it out should remove the coref-error confabulations while KEEPING the
correct answers whose coref margin is high (including the ones v1 wrongly abstained on for low parse).

ONE VARIABLE vs v1: the abstain-gate SIGNAL only.
  v1: gate on r["conf"]        = min(parse_conf, coref_conf)   (combined)
  v2: gate on r["coref_conf"]  = coref salience margin alone
EVERYTHING ELSE IS v1 VERBATIM (imported, not re-typed): same real-text passages, same Q-set, same
confidence-annotating extractor, same relation set (byte-identical to base O.extract_passage), same
NO_GATE baseline (halluc 0.4194, n_correct 8), same normalization, same SCRAMBLE matched-coverage
anti-cheat, same bands. The per-answered-Q coref_conf column v2 gates on is the IDENTICAL column v1
already computed and reported as auc.coref_only=0.885 -- v2 simply GATES on that exact column instead
of the min column. That is the entire diff, and the self-test asserts it (coref_conf != conf on at
least one answered Q, so the gate genuinely behaves differently).

ARMS:
  NO_GATE       = REAL pipeline answers everything it matches (reproduces 0.4194; positive control;
                  IDENTICAL to v1 -- the baseline does not read any confidence signal).
  ABSTAIN_GATE  = REAL + coref-margin-only gate at the pre-registered operating threshold (lowest
                  coref-margin threshold achieving global halluc <= 0.05).  THE MECHANISM.
  SCRAMBLE_GATE = anti-cheat must-fail: matched-coverage RANDOM abstention (answer the same NUMBER of
                  Qs, chosen uniformly at random).  The real coref gate must BEAT random abstention.

BANDS (envelope-fail; SAME AS v1 for comparability; set BEFORE the run; imported from the v1 module;
global halluc = wrong-answered / n_total, same definition as the baseline):
  HARD_PASS (coref margin GENUINELY discriminates + operationalizes as a gate; zero-halluc restored at
    non-trivial coverage, materially above v1's 0.161):
      auc(coref) >= 0.70 AND
      retained_correct_frac >= 0.60 AND
      precision_on_answered >= 0.80 AND
      op_halluc <= 0.05 AND
      (scramble_halluc - op_halluc) >= 0.10 at matched coverage.
  HARD_FAIL:
      auc(coref) <= 0.55 OR
      retained_correct_frac <= 0.25 OR
      (scramble_halluc - op_halluc) <= 0.02.
  MIDDLE otherwise.

WHY THIS IS A GENUINE CAN-FAIL (not guaranteed): a 0.885 SIGNAL AUC does not guarantee a SINGLE
THRESHOLD clears halluc<=0.05 (n_wrong_kept<=1 of 31) AT retained_correct>=0.60. The coref margin is
1.0 for every relation with NO pronoun head, so relations whose wrongness is a PARSE role-reversal (not
a coref error) get coref_conf=1.0 and pass ANY threshold < 1.0 -- the coref-only gate is STRUCTURALLY
BLIND to parse-driven confabulations. If enough of the 13 wrong answers are parse-reversals rather than
coref errors, no coref threshold reaches halluc<=0.05 without also abstaining the correct answers ->
HARD_FAIL. Both bands are reachable; the data decides.

DESIGN-GATE (verified at self-test): (1) REAL baseline reproduced (NO_GATE halluc within tol of 0.4194,
  n_correct==8); (2) discriminator CAN-FAIL (coref gate blind to parse-reversals; abstain-all is the
  honest HARD_FAIL); (3) difficulty ON (real grade-2 syntax, true-MM components, unchanged); (4) ONE
  variable = the gate SIGNAL (coref-only vs min); (5) NO answer leakage (Q specs unchanged, inherited);
  (6) ONE-VARIABLE ISOLATION AIRTIGHT: relation SET byte-identical to base O.extract_passage (asserted);
  the coref_conf column is v1's own column (asserted != conf on >=1 answered Q so the gate differs);
  (7) POSITIVE-CONTROL: NO_GATE per-question answers reproduce O.answer_reader exactly; (8) determinism
  (OMP=1, fixed seed, sorted set, no hash()-seeding; scramble uses random.Random(seed)).

CELL-TEMPLATE (relevant subset; many SCHEMA-VET gates N/A for this non-HD glass-box cell):
# - except SystemExit/KeyboardInterrupt: raise BEFORE except Exception (no BaseException)
# - ATOMIC final metrics write (tmp + os.replace)                 [META_RULE_AH: tmp_replace]
# - ARMS-MUST-DIFFER hash check at run                            [META_RULE_AF]
# - discriminator CAN-FAIL AND FIRES (coref AUC; retained-correct; beat-scramble)     [design-gate]
# - REAL code path exercised in self-test (perceptron fit + POS tag + WorkingOverlay + conf-extract) [F.1]
# - baseline_in_band: NO_GATE reproduces 0.4194; coref-gate free to fail (blind to parse-reversal) [AG]
# - deterministic (fixed seed, OMP=1, no hash()-seed, sorted(set))               [F.5/PROT-023]
# - multi-seed variance probe on the discriminator: coref-AUC bootstrap CI + K-seed scramble null  [META CG]
# - start-marker + crash-diagnostic; heartbeat EXEMPT (wall < 90s)
# - crlb_n/a: symbolic glass-box; coverage-at-zero-halluc ceiling (8/31=0.258) IS the feasibility bound
# - progress_logging: print_flush_true.  gate_threshold: FIXED interpretable rule (coref margin > th);
#   the full precision/coverage CURVE over coref-margin thresholds is the deliverable.
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

# v1 is imported VERBATIM: every building block (extractor, answer engine, component-conf attach,
# metrics helpers, AUC, scramble, arms-differ, bands, baseline targets) is reused unchanged. v2 only
# overrides the handful of functions that SELECT the gate signal.
import experiments.exp_multi_turn_loop_realtext_confidence_abstain_gate_v1 as V1

O = V1.O

ANCHOR_NAME = "multi_turn_loop_realtext_confidence_abstain_gate_v2"

# --- reused VERBATIM from v1 (same seeds, same nulls, same bands, same baseline targets) ---
SEED = V1.SEED
N_SCRAMBLE_SEEDS = V1.N_SCRAMBLE_SEEDS
N_BOOT = V1.N_BOOT
HP_AUC_MIN = V1.HP_AUC_MIN
HP_RETAINED_CORRECT_MIN = V1.HP_RETAINED_CORRECT_MIN
HP_PRECISION_MIN = V1.HP_PRECISION_MIN
HP_HALLUC_MAX = V1.HP_HALLUC_MAX
HP_BEAT_SCRAMBLE_MIN = V1.HP_BEAT_SCRAMBLE_MIN
HF_AUC_MAX = V1.HF_AUC_MAX
HF_RETAINED_CORRECT_MAX = V1.HF_RETAINED_CORRECT_MAX
HF_BEAT_SCRAMBLE_MAX = V1.HF_BEAT_SCRAMBLE_MAX
BASE_HALLUC = V1.BASE_HALLUC
BASE_HALLUC_TOL = V1.BASE_HALLUC_TOL
BASE_N_CORRECT = V1.BASE_N_CORRECT
CROSS_TURN_SLICES = V1.CROSS_TURN_SLICES

# ===========================================================================================
# THE ONE VARIABLE: the gate reads the COREF SALIENCE MARGIN alone.
#   v1: GATE_SIGNAL_KEY = "conf"        (= min(parse_conf, coref_conf))
#   v2: GATE_SIGNAL_KEY = "coref_conf"  (= coref salience margin alone)
# ===========================================================================================
GATE_SIGNAL_KEY = "coref_conf"


def _sig(rec):
    """The scalar the abstain gate operates on for this record (coref margin alone in v2)."""
    return rec[GATE_SIGNAL_KEY]


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
# Gate-driving functions (the ONLY functions that differ from v1 -- they read _sig()).
# ===========================================================================================
def precision_coverage_curve(recs):
    """Sweep the COREF-MARGIN threshold over observed answered coref values; Pareto frontier."""
    answered = [r for r in recs if r["is_answered"]]
    confs = sorted(set(_sig(r) for r in answered))
    thresholds = [-1.0] + confs   # -1 = keep all answered (NO_GATE)
    curve = []
    for th in thresholds:
        m = V1._gate_metrics(recs, keep_fn=lambda r, th=th: r["is_answered"] and _sig(r) > th)
        m["threshold"] = round(th, 6)
        curve.append(m)
    return curve


def _cross_turn_report(recs, op):
    ct = [r for r in recs if r["slice"] in CROSS_TURN_SLICES]
    ng = V1._gate_metrics(ct, keep_fn=lambda r: r["is_answered"])
    gated = V1._gate_metrics(ct, keep_fn=lambda r: r["is_answered"] and _sig(r) > op["threshold"])
    return {"no_gate": ng, "gated": gated}


def _run_from_recs(recs, scale):
    """Assemble res dict. PRIMARY discriminator + gate = coref margin alone (_sig)."""
    no_gate = V1._gate_metrics(recs, keep_fn=lambda r: r["is_answered"])
    n_correct = no_gate["n_correct_kept"]
    answered = [r for r in recs if r["is_answered"]]
    labels = [r["correct"] for r in answered]

    # PRIMARY AUC = the gate signal (coref margin). Also report parse-only + v1's min-combined for context.
    gate_scores = [_sig(r) for r in answered]
    rng = random.Random(SEED)
    auc_gate, ci_lo, ci_hi = V1._auc_ci(gate_scores, labels, rng, N_BOOT)
    auc_parse = V1._auc([r["parse_conf"] for r in answered], labels)
    auc_coref = V1._auc([r["coref_conf"] for r in answered], labels)
    auc_min = V1._auc([r["conf"] for r in answered], labels)   # v1's gate signal, comparability

    curve = precision_coverage_curve(recs)
    op = V1.choose_operating_threshold(curve)
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
    gate_answers = [r["ans"] if (r["is_answered"] and _sig(r) > op["threshold"]) else None for r in recs]

    # ceiling-tie analysis: WHY a single coref threshold can/can't operationalize the AUC. If wrong
    # answers are tied with correct answers at the coref-margin ceiling (parse-reversals; coref blind),
    # no threshold below the ceiling clears them and the ceiling threshold abstains the correct too.
    ceil_val = max((_sig(r) for r in answered), default=0.0)
    at_ceiling = [r for r in answered if round(_sig(r), 6) >= round(ceil_val, 6)]
    nontrivial = [c for c in curve if c["coverage"] > 0.0]
    best_nt = min(nontrivial, key=lambda c: (c["halluc"], -c["coverage"])) if nontrivial else None
    ceiling_analysis = {
        "ceiling_value": round(ceil_val, 6),
        "n_correct_at_ceiling": sum(1 for r in at_ceiling if r["correct"] == 1),
        "n_wrong_at_ceiling": sum(1 for r in at_ceiling if r["correct"] == 0),
        "best_nontrivial_halluc": (best_nt["halluc"] if best_nt else None),
        "best_nontrivial_coverage": (best_nt["coverage"] if best_nt else None),
        "best_nontrivial_threshold": (best_nt["threshold"] if best_nt else None),
        "wrong_at_ceiling_qids": [r["q"]["qid"] for r in at_ceiling if r["correct"] == 0],
    }

    return {
        "baseline": {"halluc": no_gate["halluc"], "coverage": no_gate["coverage"],
                     "precision_on_answered": no_gate["precision_on_answered"],
                     "n_correct": n_correct, "n_answered": no_gate["n_answered"],
                     "n_wrong": no_gate["n_wrong_kept"], "n_total": no_gate["n_total"]},
        "auc": {"gate_signal": round(auc_gate, 4), "ci_lo": round(ci_lo, 4), "ci_hi": round(ci_hi, 4),
                "parse_only": round(auc_parse, 4), "coref_only": round(auc_coref, 4),
                "min_combined": round(auc_min, 4), "n_boot": N_BOOT,
                "gate_signal_name": "coref_margin_alone", "n_pos": sum(labels),
                "n_neg": len(labels) - sum(labels)},
        "operating_point": op, "retained_correct_frac": round(retained, 4),
        "scramble": scramble, "beat_scramble": beat, "curve": curve, "margin_scale": round(scale, 6),
        "ceiling_analysis": ceiling_analysis,
        "cross_turn": _cross_turn_report(recs, op),
        "_answers": {"NO_GATE": no_gate_answers, "ABSTAIN_GATE": gate_answers,
                     "SCRAMBLE_GATE": scramble_answers},
        "_recs_debug": [{"qid": r["q"]["qid"], "slice": r["slice"], "ans": r["ans"], "gold": r["gold"],
                         "conf_min": r["conf"], "parse_conf": r.get("parse_conf"),
                         "coref_conf": r.get("coref_conf"), "gate_conf": _sig(r),
                         "correct": r["correct"], "n_distinct": r["n_distinct"]} for r in recs],
    }


def run_all(qs, clf):
    V1._attach_component_confs(clf, qs)
    recs, _stores, scale = _build_records(clf, qs)
    return _run_from_recs(recs, scale)


def _arms_differ(res):
    """ARMS-MUST-DIFFER (META_RULE_AF). NO_GATE must always differ from ABSTAIN_GATE. ABSTAIN vs
    SCRAMBLE must differ EXCEPT at a legitimate abstain-all operating point (coverage 0): there the
    coref gate keeps nothing AND matched-coverage random abstention keeps nothing (k=0) -- both empty
    by construction, an EXPECTED honest-HARD_FAIL degeneracy, not an arm-implementation bug. Exempt
    that pair with a declared rationale rather than crashing on the honest outcome."""
    digests = {}
    for name in ("NO_GATE", "ABSTAIN_GATE", "SCRAMBLE_GATE"):
        digests[name] = hashlib.sha256(
            json.dumps(res["_answers"][name], sort_keys=True).encode()).hexdigest()
    exempted = []
    assert digests["NO_GATE"] != digests["ABSTAIN_GATE"], \
        "META_RULE_AF: NO_GATE == ABSTAIN_GATE (the gate abstained on nothing)"
    if res["operating_point"]["coverage"] == 0.0:
        exempted.append(["ABSTAIN_GATE", "SCRAMBLE_GATE"])   # abstain-all: both empty by construction
    else:
        assert digests["ABSTAIN_GATE"] != digests["SCRAMBLE_GATE"], \
            "META_RULE_AF: ABSTAIN_GATE == SCRAMBLE_GATE (gate identical to random abstention)"
    return digests, exempted


# ===========================================================================================
# Verdict (coref-margin-only aware messaging; same band logic as v1).
# ===========================================================================================
def compute_verdict(res):
    auc = res["auc"]["gate_signal"]          # coref margin AUC = the gate signal
    op = res["operating_point"]
    retained = res["retained_correct_frac"]
    precision = op["precision_on_answered"]
    op_halluc = op["halluc"]
    beat = res["beat_scramble"]

    hp = (auc >= HP_AUC_MIN and retained >= HP_RETAINED_CORRECT_MIN and
          precision >= HP_PRECISION_MIN and op_halluc <= HP_HALLUC_MAX and
          beat >= HP_BEAT_SCRAMBLE_MIN)
    hf = (auc <= HF_AUC_MAX or retained <= HF_RETAINED_CORRECT_MAX or beat <= HF_BEAT_SCRAMBLE_MAX)

    if hp:
        tier, outcome = "HARD_PASS", "coref-only-gate-restores-zero-halluc-at-coverage"
    elif hf:
        tier, outcome = "HARD_FAIL", "coref-only-gate-must-abstain-all-or-blind-to-parse-reversals"
    else:
        tier, outcome = "MIDDLE_BAND", "coref-only-gate-partial-precision-coverage-tradeoff"

    localize = []
    if auc <= HF_AUC_MAX:
        localize.append("coref margin NOT informative at this regime: AUC(coref,correct)=%.3f <= %.2f "
                        "(parse-only=%.3f min-combined=%.3f)" % (auc, HF_AUC_MAX,
                        res["auc"]["parse_only"], res["auc"]["min_combined"]))
    if retained <= HF_RETAINED_CORRECT_MAX:
        localize.append("to reach halluc<=%.2f the coref gate abstains on ~everything: "
                        "retained_correct_frac=%.3f <= %.2f (kept %d of %d correct) -- likely the wrong "
                        "answers are PARSE-reversals (coref_conf=1.0), blind to a coref-only gate"
                        % (HP_HALLUC_MAX, retained, HF_RETAINED_CORRECT_MAX, op["n_correct_kept"],
                           res["baseline"]["n_correct"]))
    if beat <= HF_BEAT_SCRAMBLE_MAX:
        localize.append("coref gate no better than RANDOM abstention at matched coverage: "
                        "scramble_halluc-op_halluc=%.3f <= %.2f (real=%.3f scramble=%.3f)"
                        % (beat, HF_BEAT_SCRAMBLE_MAX, op_halluc, res["scramble"]["halluc_mean"]))
    if not localize:
        if hp:
            localize.append("coref margin ALONE discriminates + gates: AUC=%.3f, kept %d/%d correct, "
                            "precision_on_answered=%.3f, beats random abstention by %.3f (dropped the "
                            "anti-informative parse term -> coverage up vs v1)"
                            % (auc, op["n_correct_kept"], res["baseline"]["n_correct"], precision, beat))
        else:
            localize.append("partial: halluc %.3f->%.3f at coverage %.3f (retained_correct=%.3f, "
                            "coref-AUC=%.3f)" % (res["baseline"]["halluc"], op_halluc, op["coverage"],
                                                 retained, auc))

    msg = ("%s (%s) | GATE=coref_margin_alone | NO_GATE halluc=%.3f cov=1.000 prec=%.3f | "
           "AUC coref=%.3f [%.3f,%.3f] (parse=%.3f min-combined=%.3f) | OP@th=%.3f: halluc=%.3f "
           "cov=%.3f prec=%.3f retained_correct=%.3f (%d/%d) | scramble halluc=%.3f -> beat=%.3f" % (
               tier, outcome, res["baseline"]["halluc"], res["baseline"]["precision_on_answered"],
               auc, res["auc"]["ci_lo"], res["auc"]["ci_hi"], res["auc"]["parse_only"],
               res["auc"]["min_combined"], op["threshold"], op_halluc, op["coverage"], precision,
               retained, op["n_correct_kept"], res["baseline"]["n_correct"],
               res["scramble"]["halluc_mean"], beat))
    return tier, outcome, msg, localize


# ===========================================================================================
# infra: out-dir / markers / metrics / crash (atomic). v2-scoped anchor name.
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
# self-test: real code path + assert isolation + the ONE-VARIABLE actually changes behavior.
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

    # (2) POSITIVE CONTROL: NO_GATE per-question answers reproduce O.answer_reader exactly.
    V1._attach_component_confs(clf, O.TEST_QS)
    recs, stores, scale = _build_records(clf, O.TEST_QS)
    for r in recs:
        base_ans = O.normalize(O.answer_reader(r["q"]["spec"], stores.get(r["q"]["p"], [])))
        assert r["ans"] == base_ans, "answer drift on %s: conf=%r base=%r" % (
            r["q"]["qid"], r["ans"], base_ans)

    # (3) baseline reproduces the 0.4194 hallucination + n_correct==8 (positive control vs prior cell).
    ng = V1._gate_metrics(recs, keep_fn=lambda r: r["is_answered"])
    assert abs(ng["halluc"] - BASE_HALLUC) <= BASE_HALLUC_TOL, \
        "baseline halluc=%.4f not within %.3f of prior %.4f" % (ng["halluc"], BASE_HALLUC_TOL, BASE_HALLUC)
    assert ng["n_correct_kept"] == BASE_N_CORRECT, \
        "baseline n_correct=%d != expected %d" % (ng["n_correct_kept"], BASE_N_CORRECT)

    # (4) coref gate signal in [0,1] and NOT constant (a constant conf cannot gate).
    answered = [r for r in recs if r["is_answered"]]
    gsig = [_sig(r) for r in answered]
    assert all(0.0 <= c <= 1.0 for c in gsig), "coref gate signal out of [0,1]"
    assert len(set(round(c, 4) for c in gsig)) >= 3, \
        "coref gate signal near-constant (%d distinct) -- cannot gate" % len(set(round(c, 4) for c in gsig))

    # (5) THE ONE VARIABLE genuinely changes behavior: coref_conf differs from v1's min-combined conf on
    # at least one answered Q (else v2 == v1 and the gate is not actually different).
    diff = [r for r in answered if round(r["coref_conf"], 6) != round(r["conf"], 6)]
    assert diff, "coref_conf == conf on ALL answered Qs -- v2 gate identical to v1 (parse never binds)"

    # (6) the gate CAN change the answer set (arms differ; op abstains something OR coverage < 1).
    full = _run_from_recs(recs, scale)
    _arms_differ(full)
    assert full["operating_point"]["threshold"] > -1.0 or full["operating_point"]["coverage"] < 1.0, \
        "gate never abstains -- operating point keeps everything"
    # (7) sanity: the reported gate-signal AUC equals the coref-only AUC (we ARE gating on coref).
    assert abs(full["auc"]["gate_signal"] - full["auc"]["coref_only"]) < 1e-9, \
        "gate_signal AUC != coref_only AUC -- gate signal wiring bug"

    print("[self-test] PASS | isolation OK | NO_GATE halluc=%.4f n_correct=%d | coref-AUC=%.3f "
          "(parse=%.3f min-combined=%.3f) | OP th=%.3f halluc=%.3f retained=%.3f | beat=%.3f | "
          "n_diff(coref!=min)=%d/%d | scale=%.4f"
          % (ng["halluc"], ng["n_correct_kept"], full["auc"]["gate_signal"], full["auc"]["parse_only"],
             full["auc"]["min_combined"], full["operating_point"]["threshold"],
             full["operating_point"]["halluc"], full["retained_correct_frac"], full["beat_scramble"],
             len(diff), len(answered), full["margin_scale"]), flush=True)
    return True


# ===========================================================================================
# main run.
# ===========================================================================================
def run(run_mode):
    qs = list(O.TEST_QS)
    if run_mode == "smoke":
        smoke_pids = {"L5_dogs", "L18_king", "L14_henry", "L60_geo", "L32_tiger", "L28_sam"}
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
        "gate_signal": "coref_margin_alone",
        "one_variable_vs_v1": "gate signal = coref_conf (v2) vs min(parse_conf,coref_conf) (v1)",
        "baseline_no_gate": res["baseline"],
        "auc": res["auc"],
        "operating_point": res["operating_point"],
        "retained_correct_frac": res["retained_correct_frac"],
        "scramble_matched_coverage": res["scramble"],
        "beat_scramble": res["beat_scramble"],
        "ceiling_analysis": res["ceiling_analysis"],
        "precision_coverage_curve": res["curve"],
        "cross_turn": res["cross_turn"],
        "margin_scale": res["margin_scale"],
        "confidence_signals": ["coref_margin(maintained-overlay salience gap) -- GATE SIGNAL",
                               "parse_margin(perceptron argmax-runnerup) -- reported, NOT gated (anti-informative)",
                               "match_support(conflict cap) -- inherited in coref_conf provenance"],
        "gate_threshold_kind": "fixed_interpretable_rule_coref_margin_gt_threshold",
        "bands": {"HP_auc_min": HP_AUC_MIN, "HP_retained_correct_min": HP_RETAINED_CORRECT_MIN,
                  "HP_precision_min": HP_PRECISION_MIN, "HP_halluc_max": HP_HALLUC_MAX,
                  "HP_beat_scramble_min": HP_BEAT_SCRAMBLE_MIN, "HF_auc_max": HF_AUC_MAX,
                  "HF_retained_correct_max": HF_RETAINED_CORRECT_MAX,
                  "HF_beat_scramble_max": HF_BEAT_SCRAMBLE_MAX},
        "coverage_at_zero_halluc_ceiling": round(res["baseline"]["n_correct"] / res["baseline"]["n_total"], 4),
        "weakest_interface": localize,
        "arms_differ_digests": digests, "arms_differ_verified": True,
        "arms_differ_exempted": arms_exempted,
        "final_metrics_atomicity": "tmp_replace", "deterministic_seeding": True,
        "progress_logging": "print_flush_true", "compute_architecture": "sequential_cpu_pure_python",
        "crlb_n_a": "symbolic glass-box; coverage-at-zero-halluc ceiling 8/31=0.258 is the feasibility bound",
        "per_question": res["_recs_debug"],
        "reuse_credited": {
            "v1_gate_cell_imported_verbatim": "exp_multi_turn_loop_realtext_confidence_abstain_gate_v1.py",
            "realtext_components_and_gold": "exp_oracle_mention_upperbound_reader_v1.py",
            "revealed_hypothesis": "v1 auc.coref_only=0.885 vs auc.parse_only=0.188 -> drop parse, gate coref alone"},
        "REQUIRED_FIELDS": ["verdict", "baseline_no_gate", "auc", "operating_point",
                            "retained_correct_frac", "scramble_matched_coverage", "beat_scramble",
                            "arms_differ_digests", "gate_signal"],
        "notes": ("Coref-margin-ONLY abstain gate (v2). Fresh pre-registered test of v1's revealed "
                  "hypothesis: the glass-box confidence discrimination lives in the coref salience "
                  "margin (AUC 0.885); parse margin is anti-informative (0.188). v2 drops parse, gates "
                  "on coref margin alone. ONE variable vs v1 = the gate signal. CLAIM-VET-pending."),
    }
    _write_metrics(out_dir, metrics)

    print("[%s:%s] %s" % (ANCHOR_NAME, run_mode, msg), flush=True)
    print("  [NO_GATE ] halluc=%.3f cov=1.000 prec=%.3f (correct=%d wrong=%d abstain=%d of %d)"
          % (res["baseline"]["halluc"], res["baseline"]["precision_on_answered"],
             res["baseline"]["n_correct"], res["baseline"]["n_wrong"],
             res["baseline"]["n_total"] - res["baseline"]["n_answered"], res["baseline"]["n_total"]), flush=True)
    print("  [AUC     ] coref(gate)=%.3f [%.3f,%.3f] parse_only=%.3f min_combined=%.3f (pos=%d neg=%d)"
          % (res["auc"]["gate_signal"], res["auc"]["ci_lo"], res["auc"]["ci_hi"], res["auc"]["parse_only"],
             res["auc"]["min_combined"], res["auc"]["n_pos"], res["auc"]["n_neg"]), flush=True)
    op = res["operating_point"]
    print("  [OP GATE ] coref_margin>%.3f halluc=%.3f cov=%.3f prec=%.3f retained_correct=%.3f (kept %d/%d)"
          % (op["threshold"], op["halluc"], op["coverage"], op["precision_on_answered"],
             res["retained_correct_frac"], op["n_correct_kept"], res["baseline"]["n_correct"]), flush=True)
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
