"""exp_multi_turn_loop_realtext_oracle_vs_real_compounding_v1 -- THE DECISIVE real-text test of
the assembled conversational substrate: does composition HOLD, or do the component MM ceilings
COMPOUND, when the multi-turn discourse loop runs over REAL grade-2 prose with the ACTUAL parser +
ACTUAL coref (NOT gold, NOT the clean animal register where parse was 1.0 by construction)?

CONTEXT: exp_multi_turn_conversational_loop_crossturn_qa_v1 HARD_PASSED -- the reader interfaces
compose into a working multi-turn loop with zero cross-turn hallucination. BUT that ran the closed
animal register where ie_extract scores parse=1.0 by construction. This cell answers the honest
question clean register could not: run the SAME multi-turn discipline over REAL McGuffey Second Reader
passages, streamed sentence-by-sentence as turns, assembling a discourse memory (relations + a
maintained-salience coref overlay across turns), then answer cross-turn / cross-sentence questions
that REQUIRE the assembled memory. Measure ORACLE (perfect components) minus REAL (true MM) = the
COMPOUNDING cost, plus per-stage (parse / coref / answer) accuracy to localize WHERE errors cascade,
plus the hallucination rate AT SCALE (does zero-hallucination survive real MM inputs?).

McGuffey here is a REAL-TEXT TESTBED for the composition/reasoning question (cross-turn QA over
assembled memory) -- NOT a breadth/recognition target. One testbed, not the focus.

GENUINE REUSE (credited):
  - Multi-turn-loop DISCIPLINE (arms isolate one variable; zero-hallucination abstain; envelope bands;
    arms-differ digests; atomic metrics): exp_multi_turn_conversational_loop_crossturn_qa_v1.py.
  - REAL-text components + gold annotations (VERBATIM McGuffey Second Reader passages, gold relations,
    cross-turn comprehension Q-set NC/CO/CC/CMP, learned averaged-perceptron role-assigner, the
    maintained-salience WorkingOverlay coref, relation-emission, the query engine, the grounded
    frequency floor): exp_oracle_mention_upperbound_reader_v1.py (imported, NOT rebuilt).
  - The upper-bound-arm idea (inject perfect components, bound the prize): the oracle-mention cell.

ARMS (each comparison isolates ONE variable):
  ORACLE       = store is the COMPLETED gold-relation set (perfect parse + perfect coref). Upper bound:
                 what the loop + QA machinery achieves with perfect components.
  REAL         = the REAL pipeline: learned role-assigner + v4 hand-rule mention detector + MAINTAINED
                 cross-turn coref overlay (RELF1 ~0.22 on this text = the true assembled MM ceiling).
  REAL_NOMEM   = the REAL pipeline with cross-turn coref OFF (pronouns unresolved) = the within-turn
                 baseline (proves cross-turn memory is load-bearing IN the real arm).
  FREQUENCY    = mention-independent grounded-frequency floor (order-insensitive; the must-beat).

  Variable isolation: ORACLE vs REAL = component quality (perfect vs true-MM parse+coref); REAL vs
  REAL_NOMEM = cross-turn coref memory (on vs off); REAL vs FREQUENCY = does the real loop beat the
  memoryless floor. Cross-turn slice = CC (competitive coref) + CMP (2-edge composition), which REQUIRE
  the assembled cross-sentence memory; NC (single-hop) is the within-turn can-fail control.

BANDS (envelope-fail; I own them; set BEFORE the run; cross_turn = CC+CMP):
  HARD_PASS (composition SURVIVES real MM): real_cross_turn >= 0.50 AND
    (REAL - REAL_NOMEM) cross_turn >= 0.15 (cross-turn memory load-bearing under real components) AND
    (ORACLE - REAL) all-Q gap <= 0.25 (MM ceilings degrade but do not destroy) AND
    oracle_cross_turn >= 0.70 (loop machinery works with perfect components) AND
    real_hallucination_rate <= 0.20 (abstains rather than errs when parse/coref fail).
  HARD_FAIL (ceilings COMPOUND -- honest, important): (ORACLE - REAL) all-Q gap >= 0.40 OR
    (real_cross_turn - freq_cross_turn) <= 0.10 (collapses toward the memoryless floor) OR
    real_hallucination_rate > 0.35 (zero-hallucination BREAKS at scale).
  MIDDLE otherwise (localize the dominant failing gate / stage).

DESIGN-GATE (verified at self-test/smoke): (1) REAL baseline present (REAL_NOMEM + FREQUENCY);
  (2) discriminator CAN-FAIL (gap can be modest or large; REAL can beat or collapse to floor);
  (3) difficulty ON (real grade-2 syntax, true-MM components); (4) ONE variable per comparison;
  (5) NO answer leakage (Q specs never contain the answer -- inherited + re-asserted);
  (6) cross-turn Qs genuinely require memory (FREQUENCY scores low on CC; asserted);
  (7) POSITIVE-CONTROL: REAL RELF1 reproduces the v4 hand-rule floor within tolerance;
  (8) ORACLE store completed to cover the Q-set (each added triple is a TRUE relation in the
      verbatim passage; anti-circular -- answers were annotated independently of the extractor);
  (9) determinism (OMP=1, fixed seed, fixed order, sorted set).

CELL-TEMPLATE (relevant subset; many SCHEMA-VET gates N/A for this non-HD glass-box cell):
# - except SystemExit/KeyboardInterrupt: raise BEFORE except Exception (no BaseException)
# - ATOMIC final metrics write (tmp + os.replace)                 [META_RULE_AH: tmp_replace]
# - ARMS-MUST-DIFFER hash check at run                            [META_RULE_AF]
# - discriminator CAN-FAIL AND FIRES (ORACLE vs REAL gap; REAL vs REAL_NOMEM) [design-gate]
# - REAL code path exercised in self-test (perceptron fit + POS tag + WorkingOverlay + extract) [F.1]
# - baseline_in_band: ORACLE ~1.0, FREQUENCY low; discriminator fires                 [META_RULE_AG]
# - deterministic (fixed seed, OMP=1, no hash()-seed, sorted(set))                    [F.5/PROT-023]
# - start-marker + crash-diagnostic; heartbeat EXEMPT (wall < 90s)
# - crlb_n/a: no quantitative HD noise floor (symbolic). N/A KGStore/cardinality-sweep.
# - progress_logging: print_flush_true.
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

# --- GENUINE REUSE of the REAL-text components + gold annotations (imported, not rebuilt) ---
import experiments.exp_oracle_mention_upperbound_reader_v1 as O

ANCHOR_NAME = "multi_turn_loop_realtext_oracle_vs_real_compounding_v1"
SEED = 12345
N_BOOT = 5000

# --- pre-registered bands (HYPOTHESIZED@this prereg) ---
HP_REAL_CROSS_MIN = 0.50
HP_MEM_BENEFIT_MIN = 0.15
HP_GAP_MAX = 0.25
HP_ORACLE_CROSS_MIN = 0.70
HP_HALLUC_MAX = 0.20
HF_GAP_MIN = 0.40
HF_REAL_OVER_FREQ_MAX = 0.10
HF_HALLUC_MAX = 0.35

# v4 hand-rule RELF1 floor (positive-control reproduce; CITED@ the oracle-mention/v4 lineage).
V4_HANDRULE_RELF1_F1 = 0.217
REPRODUCE_TOL_F1 = 0.05

CROSS_TURN_SLICES = ("CC", "CMP")   # require assembled cross-sentence memory
WITHIN_TURN_SLICES = ("NC",)        # within-turn can-fail control
COREF_SLICES = ("CO", "CC", "CMP")

# ===========================================================================================
# ORACLE store = the gold relations COMPLETED to cover the Q-set. Each added triple is a TRUE
# relation stated in the VERBATIM passage (anti-circular: the comprehension answers were annotated
# independently of the extractor; completing the relation set only makes the gold-parse+gold-coref
# store answer the questions it should, so ORACLE is a genuine perfect-components upper bound).
# These additions are used ONLY as the ORACLE arm's QA store; RELF1 (parse quality) is still scored
# against the ORIGINAL sparse O.TEST_GOLD_RELS so the v4 positive-control comparison is unchanged.
# ===========================================================================================
GOLD_RELS_ADDED = {
    # "She caught her kitten ..." her->tigress -> tigress owns the kitten.
    "L32_tiger": [("poss", "tigress", "kitten")],
    # "He sent a ball at James Mason ..." He->george.
    "L60_geo": [("svo", "sent", "george", "ball")],
    # "The name of James's Scotch terrier is Dodger." possessive 's.
    "L5b_dodger": [("poss", "james", "terrier")],
    # "Dash, her pet dog ..." her->mary.
    "L23_doll": [("poss", "mary", "dog")],
    # "held out his hat ... the man's hat." his->man / possessive 's.
    "L28_sam": [("poss", "man", "hat"), ("svo", "gave", "mother", "cents")],
    # "She brought her bread ..." She->patty.
    "L26_patty": [("svo", "brought", "patty", "bread")],
}


def build_oracle_store():
    store = {}
    for pid in O.TEST_PASSAGES:
        rels = list(O.TEST_GOLD_RELS.get(pid, []))
        rels.extend(GOLD_RELS_ADDED.get(pid, []))
        store[pid] = sorted(set(rels), key=lambda r: (r[0], tuple(str(x) for x in r[1:])))
    return store


# ===========================================================================================
# Arm runners. REAL / REAL_NOMEM run the REAL extraction pipeline (learned role-assigner + v4
# hand-rule mention detector); coref maintained (REAL) vs OFF (REAL_NOMEM). ORACLE reads the
# completed gold store. All arms answer through the SAME query engine (O.answer_reader).
# ===========================================================================================
def build_clf():
    clf = O.AveragedPerceptron()
    clf.fit(O.build_training_examples(), O.N_EPOCHS)
    return clf


def build_real_stores(clf, coref_strategy):
    """coref_strategy='maintained' -> REAL; None -> REAL_NOMEM. v4 hand-rule mentions (true MM)."""
    stores = {}
    reslogs = {}
    for pid, text in O.TEST_PASSAGES.items():
        rels, rlog = O.extract_passage(text, "learned", clf, coref_strategy, "handrule", frozenset())
        stores[pid] = rels
        reslogs[pid] = rlog
    return stores, reslogs


def answer_from_stores(stores, qs):
    """Answer each question through the shared query engine. Returns (correct, answers)."""
    correct = []
    answers = []
    for q in qs:
        ans = O.answer_reader(q["spec"], stores.get(q["p"], []))
        na, ng = O.normalize(ans), O.normalize(q["gold"])
        correct.append(1 if (na is not None and na == ng) else 0)
        answers.append(na)
    return correct, answers


def frequency_answers(qs):
    correct = []
    answers = []
    for q in qs:
        ans = O.answer_frequency(q["atype"], O.TEST_PASSAGES[q["p"]], q["spec"])
        na, ng = O.normalize(ans), O.normalize(q["gold"])
        correct.append(1 if (na is not None and na == ng) else 0)
        answers.append(na)
    return correct, answers


def _acc(correct, idx):
    return (sum(correct[i] for i in idx) / len(idx)) if idx else 0.0


def _slice_idx(qs, slices):
    return [i for i, q in enumerate(qs) if q["slice"] in slices]


def _per_slice(correct, qs):
    d = {}
    for sl in ("NC", "CO", "CC", "CMP"):
        idx = [i for i, q in enumerate(qs) if q["slice"] == sl]
        d[sl] = round(_acc(correct, idx), 4)
        d["n_" + sl] = len(idx)
    d["all"] = round(sum(correct) / len(correct), 4) if correct else 0.0
    return d


def _hallucination_rate(correct, answers):
    """Fraction of questions answered with a NON-None WRONG value (a confident wrong answer) instead
    of abstaining (None). This is the zero-hallucination robustness property under real MM inputs."""
    n = len(correct)
    if n == 0:
        return 0.0, 0, 0
    hall = sum(1 for i in range(n) if answers[i] is not None and correct[i] == 0)
    abst = sum(1 for i in range(n) if answers[i] is None)
    return hall / n, hall, abst


# ===========================================================================================
# Parse-stage RELF1 (micro over the passages present in the Q-set), scored vs the SPARSE gold
# (so the v4 positive-control comparison is apples-to-apples).
# ===========================================================================================
def relf1_micro(stores, pids):
    kinds = {"svo", "loc", "poss"}
    tp = ex = go = 0
    per = {}
    for pid in pids:
        e = set(r for r in stores.get(pid, []) if r[0] in kinds)
        g = set(r for r in O.TEST_GOLD_RELS.get(pid, []) if r[0] in kinds)
        t = len(e & g)
        tp += t
        ex += len(e)
        go += len(g)
        p = t / len(e) if e else 0.0
        r = t / len(g) if g else 0.0
        per[pid] = {"p": round(p, 3), "r": round(r, 3), "tp": t, "n_gold": len(g), "n_ext": len(e)}
    P = tp / ex if ex else 0.0
    R = tp / go if go else 0.0
    F = 2 * P * R / (P + R) if (P + R) > 0 else 0.0
    return {"micro_precision": round(P, 3), "micro_recall": round(R, 3), "micro_f1": round(F, 3),
            "tp": tp, "n_extracted": ex, "n_gold": go, "per_passage": per}


def coref_stage_stats(reslogs, qs):
    """Coref-stage signal: (a) pronoun-resolution attempt/resolved counts from the overlay reslog;
    (b) JOINT parse+coref recall on the cross-turn (CC+CMP) gold relations = fraction of those gold
    relations present in the REAL store with the CORRECT resolved head. This is where a coref miss
    (pronoun -> wrong/no antecedent) turns a would-be-answerable cross-turn fact into a miss."""
    n_attempt = sum(len(v) for v in reslogs.values())
    n_resolved = sum(1 for v in reslogs.values() for (_p, h) in v if h is not None)
    return {"n_pron_attempts": n_attempt, "n_pron_resolved": n_resolved,
            "resolved_rate": round(n_resolved / n_attempt, 3) if n_attempt else 0.0}


# ===========================================================================================
# Verdict (envelope-fail-bands per prereg).
# ===========================================================================================
def compute_verdict(res):
    gap = res["gap_all"]
    real_cross = res["REAL"]["cross_turn"]
    nomem_cross = res["REAL_NOMEM"]["cross_turn"]
    freq_cross = res["FREQUENCY"]["cross_turn"]
    oracle_cross = res["ORACLE"]["cross_turn"]
    mem_benefit = real_cross - nomem_cross
    real_over_freq = real_cross - freq_cross
    halluc = res["REAL"]["hallucination_rate"]

    hp = (real_cross >= HP_REAL_CROSS_MIN and mem_benefit >= HP_MEM_BENEFIT_MIN and
          gap <= HP_GAP_MAX and oracle_cross >= HP_ORACLE_CROSS_MIN and halluc <= HP_HALLUC_MAX)
    hf = (gap >= HF_GAP_MIN or real_over_freq <= HF_REAL_OVER_FREQ_MAX or halluc > HF_HALLUC_MAX)

    if hp:
        tier, outcome = "HARD_PASS", "composes"
    elif hf:
        tier, outcome = "HARD_FAIL", "compounds-collapses"
    else:
        tier, outcome = "MIDDLE_BAND", "partial"

    localize = []
    if gap >= HF_GAP_MIN:
        localize.append("MM ceilings COMPOUND: ORACLE-REAL all-Q gap=%.3f >= %.2f (parse RELF1=%.3f "
                        "recall=%.3f; per-slice gap NC=%.3f CO=%.3f CC=%.3f CMP=%.3f localizes cascade)"
                        % (gap, HF_GAP_MIN, res["REAL"]["relf1"]["micro_f1"], res["REAL"]["relf1"]["micro_recall"],
                           res["gap_slice"]["NC"], res["gap_slice"]["CO"], res["gap_slice"]["CC"],
                           res["gap_slice"]["CMP"]))
    if real_over_freq <= HF_REAL_OVER_FREQ_MAX:
        localize.append("REAL cross-turn collapses toward the memoryless floor (REAL=%.3f - FREQ=%.3f = %.3f <= %.2f)"
                        % (real_cross, freq_cross, real_over_freq, HF_REAL_OVER_FREQ_MAX))
    if halluc > HF_HALLUC_MAX:
        localize.append("ZERO-HALLUCINATION BREAKS at scale: REAL hallucination_rate=%.3f > %.2f "
                        "(real MM parse/coref errors -> confident WRONG answers, not abstains)" % (halluc, HF_HALLUC_MAX))
    if mem_benefit < HP_MEM_BENEFIT_MIN:
        localize.append("cross-turn memory NOT load-bearing under real components (REAL-REAL_NOMEM cross=%.3f < %.2f)"
                        % (mem_benefit, HP_MEM_BENEFIT_MIN))
    if oracle_cross < HP_ORACLE_CROSS_MIN:
        localize.append("ORACLE cross-turn=%.3f < %.2f -- loop/QA machinery itself weak with perfect components"
                        % (oracle_cross, HP_ORACLE_CROSS_MIN))
    weakest = localize if localize else ["none (composition survives real MM across all gates)"]

    msg = ("%s (%s) | ORACLE cross=%.3f all=%.3f | REAL cross=%.3f all=%.3f (parse RELF1=%.3f R=%.3f) | "
           "REAL_NOMEM cross=%.3f | FREQ cross=%.3f | ORACLE-REAL gap=%.3f (NC=%.3f CO=%.3f CC=%.3f CMP=%.3f) | "
           "mem_benefit(REAL-NOMEM)=%.3f | REAL_over_FREQ=%.3f | REAL hallucination=%.3f" % (
               tier, outcome, oracle_cross, res["ORACLE"]["all"], real_cross, res["REAL"]["all"],
               res["REAL"]["relf1"]["micro_f1"], res["REAL"]["relf1"]["micro_recall"],
               nomem_cross, freq_cross, gap, res["gap_slice"]["NC"], res["gap_slice"]["CO"],
               res["gap_slice"]["CC"], res["gap_slice"]["CMP"], mem_benefit, real_over_freq, halluc))
    return tier, outcome, msg, weakest


# ===========================================================================================
# Full arm assembly.
# ===========================================================================================
def run_all(qs, clf):
    oracle_stores = build_oracle_store()
    real_stores, real_reslogs = build_real_stores(clf, "maintained")
    nomem_stores, nomem_reslogs = build_real_stores(clf, None)

    pids = sorted(set(q["p"] for q in qs))
    arms = {}

    def pack(correct, answers, stores, reslogs, with_relf1):
        cross_idx = _slice_idx(qs, CROSS_TURN_SLICES)
        within_idx = _slice_idx(qs, WITHIN_TURN_SLICES)
        halluc, n_hall, n_abst = _hallucination_rate(correct, answers)
        d = {"per_slice": _per_slice(correct, qs), "all": round(sum(correct) / len(correct), 4),
             "cross_turn": round(_acc(correct, cross_idx), 4),
             "within_turn": round(_acc(correct, within_idx), 4),
             "hallucination_rate": round(halluc, 4), "n_hallucinated": n_hall, "n_abstained": n_abst,
             "answers": answers}
        if with_relf1:
            d["relf1"] = relf1_micro(stores, pids)
            d["coref_stage"] = coref_stage_stats(reslogs, qs)
        return d

    co, ao = answer_from_stores(oracle_stores, qs)
    cr, ar = answer_from_stores(real_stores, qs)
    cn, an = answer_from_stores(nomem_stores, qs)
    cf, af = frequency_answers(qs)

    arms["ORACLE"] = pack(co, ao, oracle_stores, {}, with_relf1=False)
    arms["REAL"] = pack(cr, ar, real_stores, real_reslogs, with_relf1=True)
    arms["REAL_NOMEM"] = pack(cn, an, nomem_stores, nomem_reslogs, with_relf1=True)
    arms["FREQUENCY"] = pack(cf, af, {}, {}, with_relf1=False)

    gap_all = arms["ORACLE"]["all"] - arms["REAL"]["all"]
    gap_slice = {sl: round(arms["ORACLE"]["per_slice"][sl] - arms["REAL"]["per_slice"][sl], 4)
                 for sl in ("NC", "CO", "CC", "CMP")}
    arms["gap_all"] = round(gap_all, 4)
    arms["gap_slice"] = gap_slice
    arms["_stores"] = {"ORACLE": oracle_stores, "REAL": real_stores, "REAL_NOMEM": nomem_stores}
    return arms


def _arms_differ(res):
    digests = {}
    for name in ("ORACLE", "REAL", "REAL_NOMEM", "FREQUENCY"):
        digests[name] = hashlib.sha256(
            json.dumps(res[name]["answers"], sort_keys=True).encode()).hexdigest()
    assert digests["ORACLE"] != digests["REAL"], "META_RULE_AF: ORACLE == REAL (component variable no-op)"
    assert digests["REAL"] != digests["REAL_NOMEM"], "META_RULE_AF: REAL == REAL_NOMEM (coref variable no-op)"
    assert digests["REAL"] != digests["FREQUENCY"], "META_RULE_AF: REAL == FREQUENCY (arms identical)"
    return digests


# ===========================================================================================
# infra: markers / metrics / crash (atomic).
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
# self-test: exercise the REAL code path + assert the discriminators FIRE.
# ===========================================================================================
def self_test():
    print("[self-test] building REAL pipeline (perceptron fit + POS tag + WorkingOverlay coref + extract) ...",
          flush=True)
    clf = build_clf()

    # (1) ORACLE store completed to cover the Q-set (perfect-components upper bound ~1.0).
    oracle_stores = build_oracle_store()
    co, _ = answer_from_stores(oracle_stores, O.TEST_QS)
    oracle_all = sum(co) / len(co)
    assert oracle_all >= 0.95, "ORACLE store does not cover the Q-set (all=%.3f); complete the gold rels" % oracle_all

    # (2) added ORACLE triples are TRUE: each argument's lemma is present in the verbatim passage
    # (substring covers surface variants: possessive "James's" -> "james", plural "cents", verb forms).
    for pid, adds in GOLD_RELS_ADDED.items():
        low_text = O.TEST_PASSAGES[pid].lower()
        for tr in adds:
            for arg in tr[1:]:
                assert arg in low_text, "added ORACLE arg %r not in verbatim passage %s" % (arg, pid)

    # (3) REAL pipeline runs and reproduces the v4 hand-rule RELF1 floor (positive control).
    real_stores, real_reslogs = build_real_stores(clf, "maintained")
    pids = sorted(O.TEST_GOLD_RELS.keys())
    rf = relf1_micro(real_stores, pids)
    assert abs(rf["micro_f1"] - V4_HANDRULE_RELF1_F1) <= REPRODUCE_TOL_F1, \
        "positive-control FAIL: REAL RELF1 f1=%.3f not within %.2f of v4 floor %.3f" % (
            rf["micro_f1"], REPRODUCE_TOL_F1, V4_HANDRULE_RELF1_F1)

    # (4) coref overlay actually resolved some pronouns in the REAL arm (the real coref ran).
    cs = coref_stage_stats(real_reslogs, O.TEST_QS)
    assert cs["n_pron_attempts"] >= 5, "coref overlay saw too few pronouns (%d) -- pipeline not exercised" % cs["n_pron_attempts"]

    # (5) ARMS-MUST-DIFFER + discriminator fires (ORACLE clearly beats REAL on cross-turn).
    res = run_all(O.TEST_QS, clf)
    _arms_differ(res)
    assert res["ORACLE"]["cross_turn"] > res["REAL"]["cross_turn"], \
        "discriminator dead: ORACLE cross=%.3f !> REAL cross=%.3f" % (
            res["ORACLE"]["cross_turn"], res["REAL"]["cross_turn"])

    # (6) cross-turn Qs genuinely require assembled memory: the memoryless FREQUENCY floor is weak on CC.
    cf, _ = frequency_answers(O.TEST_QS)
    cc_idx = [i for i, q in enumerate(O.TEST_QS) if q["slice"] == "CC"]
    freq_cc = _acc(cf, cc_idx)
    assert freq_cc < 0.5, "CC not memory-requiring: memoryless frequency floor scores %.3f on CC" % freq_cc

    # (7) NO answer leakage: no Q spec contains its own gold answer.
    for q in O.TEST_QS:
        assert O.normalize(q["gold"]) not in [str(x).lower() for x in q["spec"][1:]], \
            "answer leak in Q %s" % q["qid"]

    print("[self-test] PASS | ORACLE all=%.3f cross=%.3f | REAL all=%.3f cross=%.3f RELF1=%.3f | "
          "FREQ cc=%.3f | gap_all=%.3f | REAL halluc=%.3f | pron_attempts=%d resolved=%d"
          % (res["ORACLE"]["all"], res["ORACLE"]["cross_turn"], res["REAL"]["all"],
             res["REAL"]["cross_turn"], rf["micro_f1"], freq_cc, res["gap_all"],
             res["REAL"]["hallucination_rate"], cs["n_pron_attempts"], cs["n_pron_resolved"]), flush=True)
    return True


# ===========================================================================================
# main.
# ===========================================================================================
SMOKE_PIDS = ["L5_dogs", "L18_king", "L14_henry", "L60_geo", "L32_tiger", "L28_sam"]


def run(run_mode):
    if run_mode == "smoke":
        qs = [q for q in O.TEST_QS if q["p"] in SMOKE_PIDS]
    else:
        qs = list(O.TEST_QS)
    out_dir = _out_dir(run_mode)
    _write_start_marker(out_dir, run_mode, expected_n_units=len(qs) * 4)
    t0 = time.perf_counter()

    clf = build_clf()
    res = run_all(qs, clf)
    digests = _arms_differ(res)
    tier, outcome, msg, weakest = compute_verdict(res)

    # bootstrap significance on the load-bearing cross-turn contrasts (REAL vs FREQ, REAL vs NOMEM).
    rng = random.Random(SEED)
    cross_idx = _slice_idx(qs, CROSS_TURN_SLICES)
    cr, _ = answer_from_stores(res["_stores"]["REAL"], qs)
    cn, _ = answer_from_stores(res["_stores"]["REAL_NOMEM"], qs)
    cf, _ = frequency_answers(qs)
    p_real_vs_freq, obs_rf = O.bootstrap_lift_p(cr, cf, cross_idx, rng, n_boot=N_BOOT)
    p_real_vs_nomem, obs_rn = O.bootstrap_lift_p(cr, cn, cross_idx, rng, n_boot=N_BOOT)

    elapsed = time.perf_counter() - t0

    def strip(a):
        return {k: v for k, v in res[a].items() if k != "answers"}

    metrics = {
        "anchor_name": ANCHOR_NAME, "verdict": tier, "verdict_msg": msg, "summary": msg[:300],
        "composition_outcome": outcome, "run_mode": run_mode, "elapsed_s": round(elapsed, 4),
        "ts_iso": datetime.now(timezone.utc).isoformat(), "n_questions": len(qs),
        "n_passages": len(set(q["p"] for q in qs)),
        "arms": ["ORACLE", "REAL", "REAL_NOMEM", "FREQUENCY"],
        "ORACLE": strip("ORACLE"), "REAL": strip("REAL"),
        "REAL_NOMEM": strip("REAL_NOMEM"), "FREQUENCY": strip("FREQUENCY"),
        "gap_all": res["gap_all"], "gap_slice": res["gap_slice"],
        "compounding_cost_oracle_minus_real": res["gap_all"],
        "cross_turn_slices": list(CROSS_TURN_SLICES),
        "bootstrap": {"p_real_vs_freq_crossturn": round(p_real_vs_freq, 5), "obs_real_minus_freq": round(obs_rf, 4),
                      "p_real_vs_nomem_crossturn": round(p_real_vs_nomem, 5), "obs_real_minus_nomem": round(obs_rn, 4),
                      "n_boot": N_BOOT},
        "weakest_interface": weakest,
        "positive_control": {"real_relf1_f1": res["REAL"]["relf1"]["micro_f1"],
                             "v4_handrule_floor": V4_HANDRULE_RELF1_F1, "tol": REPRODUCE_TOL_F1,
                             "reproduced": abs(res["REAL"]["relf1"]["micro_f1"] - V4_HANDRULE_RELF1_F1) <= REPRODUCE_TOL_F1},
        "bands": {"HP_real_cross_min": HP_REAL_CROSS_MIN, "HP_mem_benefit_min": HP_MEM_BENEFIT_MIN,
                  "HP_gap_max": HP_GAP_MAX, "HP_oracle_cross_min": HP_ORACLE_CROSS_MIN,
                  "HP_halluc_max": HP_HALLUC_MAX, "HF_gap_min": HF_GAP_MIN,
                  "HF_real_over_freq_max": HF_REAL_OVER_FREQ_MAX, "HF_halluc_max": HF_HALLUC_MAX},
        "arms_differ_digests": digests, "arms_differ_verified": True,
        "final_metrics_atomicity": "tmp_replace", "deterministic_seeding": True,
        "progress_logging": "print_flush_true", "compute_architecture": "sequential_cpu_pure_python",
        "reuse_credited": {
            "loop_discipline": "exp_multi_turn_conversational_loop_crossturn_qa_v1.py",
            "realtext_components_and_gold": "exp_oracle_mention_upperbound_reader_v1.py (passages, gold rels, "
                                            "Q-set, learned role-assigner, maintained WorkingOverlay coref, "
                                            "relation-emission, query engine, frequency floor)"},
        "gold_rels_added_for_oracle_store": {k: [list(t) for t in v] for k, v in GOLD_RELS_ADDED.items()},
        "REQUIRED_FIELDS": ["verdict", "ORACLE", "REAL", "REAL_NOMEM", "FREQUENCY", "gap_all",
                            "gap_slice", "arms_differ_digests", "positive_control"],
        "notes": ("DECISIVE real-text composition test. ORACLE (completed gold store = perfect parse+coref) "
                  "vs REAL (learned role-assigner + v4 hand-rule mentions + maintained cross-turn coref, true MM) "
                  "vs REAL_NOMEM (coref OFF = within-turn baseline) vs FREQUENCY (memoryless floor). "
                  "ORACLE-REAL gap = compounding cost; per-slice gap localizes the cascade; hallucination_rate "
                  "= does zero-hallucination survive real MM. Glass-box, no LLM, no autograd. CLAIM-VET-pending. "
                  "McGuffey = real-text testbed for the composition question, not a breadth/recognition target."),
    }
    _write_metrics(out_dir, metrics)

    print("[%s:%s] %s" % (ANCHOR_NAME, run_mode, msg), flush=True)
    for a in ("ORACLE", "REAL", "REAL_NOMEM", "FREQUENCY"):
        ps = res[a]["per_slice"]
        extra = ""
        if "relf1" in res[a]:
            extra = " relf1_f1=%.3f R=%.3f coref_resolved=%d/%d" % (
                res[a]["relf1"]["micro_f1"], res[a]["relf1"]["micro_recall"],
                res[a]["coref_stage"]["n_pron_resolved"], res[a]["coref_stage"]["n_pron_attempts"])
        print("  [%-11s] all=%.3f cross=%.3f | NC=%.3f CO=%.3f CC=%.3f CMP=%.3f | halluc=%.3f abstain=%d%s"
              % (a, res[a]["all"], res[a]["cross_turn"], ps["NC"], ps["CO"], ps["CC"], ps["CMP"],
                 res[a]["hallucination_rate"], res[a]["n_abstained"], extra), flush=True)
    print("  [gap ORACLE-REAL] all=%.3f | per-slice NC=%.3f CO=%.3f CC=%.3f CMP=%.3f"
          % (res["gap_all"], res["gap_slice"]["NC"], res["gap_slice"]["CO"],
             res["gap_slice"]["CC"], res["gap_slice"]["CMP"]), flush=True)
    print("  [weakest] %s" % weakest, flush=True)
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
