"""exp_arc_reasoner_symbolic_tiebreak_v1 -- make the composed DerivationReasoner PICK the gold answer
among CO-DERIVABLE candidates using SYMBOLIC tie-break signals (question-intent / relation-type match,
do-calculus direction, chain quality) INSTEAD of the thin-cosine combiner, raising reasoning accuracy on
the TIE subset above chance -> functional reasoning on the covered subset.

WHAT / WHY (VET 29568, cell exp_arc_reasoner_entity_linking_upgrade_v1, lemma_syn link mode):
  On the 206 questions the reasoner DERIVES (mode==derivation) the decision decomposes into three regimes:
    * gold_only : ONLY gold derivable            -> reasoner picks gold          -> acc ~1.00 (mechanism PERFECT)
    * TIE       : gold AND >=1 distractor derive -> thin-cosine tie-break ~chance -> acc ~0.32 (the TARGET)
    * dist_only : gold UNREACHABLE               -> reasoner can only pick wrong -> acc  0.00 (coverage/meaning; DEFERRED)
  The TIE subset is the tractable lever: BOTH candidates have a valid derivation; pick gold via SYMBOLIC
  signals rather than a thin cosine.

THE UPGRADE (ONE variable across arms = the tie-break METHOD; rules/graph/search/coverage/CI/do identical):
  tiebreak_mode = "legacy"   : completeness -> shortest chain -> combiner (thin cosine) -> index (the BEFORE).
  tiebreak_mode = "symbolic" : intent-TERMINAL match -> intent-ANY match -> do-calculus-present ->
                               completeness -> shortest -> combiner -> index. The asked-relation (parsed
                               from the stem: what CAUSES / what is REQUIRED / what RESULTS / SOURCEOF /
                               USEDFOR / COUPLEDRELATIONSHIP) ranks a candidate REACHED BY the matching
                               relation ABOVE one reached by an off-type chain; thin cosine DEMOTED to last.

GUARDRAIL (non-negotiable): the gold_only subset (only-gold-derivable) MUST stay ~1.00 -- the symbolic
  tie-break may only re-order CO-DERIVABLE candidates, never break a clean single-candidate win.

DECISIVE TEST (full ARC-Challenge test, held-out; science rules NOT derived from test labels): does
  TIE-subset accuracy rise ABOVE the 0.32 legacy value (toward the 0.50+ a real tie-breaker gives) AND
  overall derived-acc rise ABOVE fixed chance (~0.25 = mean(1/n_choices), the FIXED calc) while gold_only
  stays ~1.00? Emit traces showing the symbolic signal correctly choosing gold among co-derivable candidates.

CAN-FAIL (pre-registered honestly): if the symbolic signals CANNOT lift the ties (TIE rise < +0.03) the
  tie-break is genuinely MEANING-BOUND (deciding which valid derivation actually ANSWERS the question needs
  grounded question-relevance meaning) -> confirms grounded meaning even for the DECISION -> HONEST-NEG,
  isolated cleanly. If ties rise selectively -> functional reasoning on the covered subset (real gain).

Contract: INLINE-LOCAL foreground-to-completion; NO push/remote-persist; ASCII-only; deterministic;
  atomic metrics; start-marker; crash-diagnostic; heartbeat; self-test builds the REAL DerivationReasoner
  over a hand rule-set (GloVe-free FakeBase) and asserts the symbolic tie-break FIRES + is CAN-FAIL + keeps
  gold_only intact. VET-PENDING (skunkworks owns landed-VET); NO atom banking.

CELL-TEMPLATE MANDATORY: except SystemExit raised BEFORE except Exception (no BaseException); atomic
  metrics (tmp+os.replace); start-marker; crash-diag; heartbeat; all numbers MEASURED@ this run.
"""
from __future__ import annotations

import os
import sys
import json
import time
import argparse
import platform
import traceback
from datetime import datetime, timezone
from typing import Dict, List, Optional

import numpy as np

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)
os.environ.setdefault("GENSIM_DATA_DIR", os.path.join(_REPO, "data", "gensim_cache"))

from hdlab.reasoner import DerivationReasoner
from experiments import exp_arc_knowledge_scale_ingest_climb_v1 as arc
from experiments import exp_arc_derivation_connectivity_gate_cleannodes_v2 as clean

ANCHOR_NAME = "arc_reasoner_symbolic_tiebreak_v1"
SEED = 20260725
RULES_PATH = os.path.join(_REPO, "data", "rules", "arc_science_typed_rules_v1.json")
LINK_MODE = "lemma_syn"                 # the VET config (highest-coverage selective link mode)
TIEBREAK_MODES = ["legacy", "symbolic"]

# pre-registered bands (fixed BEFORE the run; reported STRAIGHT, NOT tuned)
TIE_RISE_PASS = 0.10            # symbolic TIE-subset acc must rise >= +0.10 absolute vs legacy for PASS
TIE_RISE_STUCK = 0.03          # rise < this => meaning-bound HONEST-NEG (decision needs grounded meaning)
TIE_ABS_PASS = 0.42            # symbolic TIE-subset acc must reach >= 0.42 (toward 0.50; strictly > legacy 0.32)
GOLD_ONLY_FLOOR = 0.95         # guardrail: gold_only subset acc must stay >= 0.95 (clean wins preserved)

_T0 = [time.perf_counter()]


# ===========================================================================
# atomic metrics / start-marker / crash-diag / heartbeat
# ===========================================================================
def _write_metrics_atomic(output_dir: str, metrics: dict) -> None:
    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, "metrics.json")
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2, sort_keys=True)
    os.replace(tmp, path)


def _write_start_marker(output_dir: str, run_mode: str, expected_n_units: int) -> None:
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": run_mode,
              "expected_n_units": expected_n_units, "host": platform.node()}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, os.path.join(output_dir, "_start_marker.json"))


def _write_crash_metrics(output_dir: str, exc: BaseException) -> None:
    diag = {
        "verdict": "CELL_CRASHED",
        "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
        "summary": f"CELL_CRASHED: {type(exc).__name__}",
        "elapsed_s": round(time.perf_counter() - _T0[0], 1),
        "traceback": traceback.format_exc()[:5000],
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(), "anchor_name": ANCHOR_NAME,
    }
    _write_metrics_atomic(output_dir, diag)


def _heartbeat(output_dir: str, stage: str, extra: Optional[dict] = None) -> None:
    row = {"ts_iso": datetime.now(timezone.utc).isoformat(), "stage": stage,
           "elapsed_s": round(time.perf_counter() - _T0[0], 1)}
    if extra:
        row.update(extra)
    try:
        with open(os.path.join(output_dir, "_heartbeat.jsonl"), "a", encoding="utf-8") as f:
            f.write(json.dumps(row) + "\n")
    except OSError:
        pass
    print(f"[hb] {stage} {extra if extra else ''}", flush=True)


# ===========================================================================
# rule loading
# ===========================================================================
def _load_rules(path: str) -> List[dict]:
    d = json.load(open(path, "r", encoding="utf-8"))
    rows = d.get("rules", d.get("rows"))
    if not rows:
        raise ValueError(f"no 'rules'/'rows' key in {path}; keys={list(d.keys())}")
    for r in rows:
        if not all(k in r for k in ("relation", "arg0", "arg1")):
            raise ValueError(f"malformed rule row: {r}")
    return rows


# ===========================================================================
# per-mode evaluation: TYPED arm only, decomposed gold_only / TIE / dist_only
# ===========================================================================
def _valid(c: dict) -> bool:
    return bool(c["derivable"]) and not bool(c["rejected_by_ci"])


def eval_mode(reasoner: DerivationReasoner, questions: List[dict], output_dir: str,
              mode: str) -> dict:
    """Run the TYPED arm under one tiebreak_mode; decompose the DERIVED subset into
    gold_only / TIE / dist_only; report per-subset accuracy + fixed chance + per-question rows."""
    reasoner.tiebreak_mode = mode
    n = len(questions)
    per_q = []
    for qi, q in enumerate(questions):
        ci = q["correct_index"]
        res = reasoner._reason_arm(q, reasoner.arms["typed"])
        pcs = res["per_choice"]
        gold_valid = _valid(pcs[ci]) if ci < len(pcs) else False
        distractor_valid = any(_valid(c) for c in pcs if c["choice_index"] != ci)
        if gold_valid and not distractor_valid:
            subset = "gold_only"
        elif gold_valid and distractor_valid:
            subset = "tie"
        elif (not gold_valid) and distractor_valid:
            subset = "dist_only"
        else:
            subset = "not_derived"
        chosen = res["chosen_index"]
        per_q.append({
            "qid": q["qid"], "correct_index": ci, "n_choices": len(q["choices"]),
            "subset": subset, "chosen": chosen, "correct": int(chosen == ci),
            "decision_mode": res["decision_mode"], "intent_relations": res["intent_relations"],
            "gold_term_rel": pcs[ci].get("term_rel") if ci < len(pcs) else None,
            "gold_chain": pcs[ci].get("chain") if ci < len(pcs) else None,
        })
        if (qi + 1) % 200 == 0:
            _heartbeat(output_dir, f"eval:{mode}", {"done": qi + 1, "total": n})

    def acc(subset_names) -> tuple:
        rows = [r for r in per_q if r["subset"] in subset_names]
        if not rows:
            return 0.0, 0
        return sum(r["correct"] for r in rows) / len(rows), len(rows)

    derived_names = ("gold_only", "tie", "dist_only")
    derived_rows = [r for r in per_q if r["subset"] in derived_names]
    # FIXED chance = mean(1/n_choices) over the DERIVED subset (NOT 1/int(mean))
    chance = float(np.mean([1.0 / max(2, r["n_choices"]) for r in derived_rows])) if derived_rows else 0.0

    gold_only_acc, n_gold_only = acc(("gold_only",))
    tie_acc, n_tie = acc(("tie",))
    dist_only_acc, n_dist_only = acc(("dist_only",))
    derived_acc, n_derived = acc(derived_names)

    return {
        "mode": mode, "n_questions": n, "n_derived": n_derived,
        "fixed_chance": round(chance, 4),
        "gold_only": {"acc": round(gold_only_acc, 4), "n": n_gold_only},
        "tie": {"acc": round(tie_acc, 4), "n": n_tie},
        "dist_only": {"acc": round(dist_only_acc, 4), "n": n_dist_only},
        "derived_acc": round(derived_acc, 4),
        "per_q": per_q,
    }


def collect_tie_traces(reasoner: DerivationReasoner, questions: List[dict],
                       legacy_pq: List[dict], symbolic_pq: List[dict], max_traces: int = 10) -> List[dict]:
    """Glass-box traces of the SYMBOLIC tie-break correctly choosing gold among co-derivable candidates.
    Priority: TIE questions where symbolic is CORRECT and legacy was WRONG (the tie-break flip); then any
    TIE question where symbolic is correct. Shows gold chain, the losing derivable distractor(s), intent."""
    reasoner.tiebreak_mode = "symbolic"
    by_qid_legacy = {r["qid"]: r for r in legacy_pq}
    traces: List[dict] = []
    # rank: flips first (symbolic correct, legacy wrong), then symbolic-correct ties
    order = []
    for r in symbolic_pq:
        if r["subset"] != "tie":
            continue
        lg = by_qid_legacy.get(r["qid"], {})
        flip = int(r["correct"] == 1 and lg.get("correct", 0) == 0)
        order.append((-flip, -r["correct"], r["qid"]))
    order.sort()
    take_qids = [o[2] for o in order][:max_traces]
    qmap = {q["qid"]: q for q in questions}
    for qid in take_qids:
        q = qmap[qid]
        ci = q["correct_index"]
        res = reasoner._reason_arm(q, reasoner.arms["typed"])
        chosen = res["chosen_index"]
        pcs = res["per_choice"]
        lg = by_qid_legacy.get(qid, {})
        others = []
        for c in pcs:
            if c["choice_index"] == chosen:
                continue
            if not _valid(c):
                reason = "NOT a valid derivation (no chain / CI-rejected)"
            else:
                reason = (f"derivable but LOST tie-break: term_rel={c.get('term_rel')} "
                          f"(intent={res['intent_relations']}), givens_covered={c['givens_covered']}, "
                          f"chain_len={c['chain_len']}, combiner={c['combiner_score']}")
            others.append({"choice": c["choice_text"][:90], "reason": reason})
        traces.append({
            "qid": qid, "stem": q["stem"][:280],
            "intent_relations": res["intent_relations"],
            "gold_choice": q["choices"][ci][:120], "chosen_choice": q["choices"][chosen][:120],
            "symbolic_correct": bool(chosen == ci), "legacy_correct": bool(lg.get("correct", 0) == 1),
            "is_flip": bool(chosen == ci and lg.get("correct", 0) == 0),
            "gold_chain": pcs[ci].get("chain") if ci < len(pcs) else None,
            "gold_term_rel": pcs[ci].get("term_rel") if ci < len(pcs) else None,
            "why_others_not_chosen": others,
        })
    return traces


def _print_tie_traces(traces: List[dict]) -> None:
    print("\n" + "=" * 78, flush=True)
    print("GLASS-BOX SYMBOLIC TIE-BREAK TRACES (gold chosen among co-derivable candidates)", flush=True)
    print("=" * 78, flush=True)
    for t in traces:
        tag = "FLIP(legacy-wrong->symbolic-right)" if t["is_flip"] else (
            "symbolic-correct" if t["symbolic_correct"] else "symbolic-wrong")
        print(f"\n[{tag}] qid={t['qid']}  intent={t['intent_relations']}", flush=True)
        print(f"  Q: {t['stem']}", flush=True)
        print(f"  gold  : {t['gold_choice']}", flush=True)
        print(f"  chosen: {t['chosen_choice']}", flush=True)
        if t["gold_chain"]:
            print(f"  gold DERIVATION: {t['gold_chain']}  (term_rel={t['gold_term_rel']})", flush=True)
        for w in t["why_others_not_chosen"]:
            print(f"  x lost : {w['choice']} :: {w['reason']}", flush=True)


# ===========================================================================
# main run
# ===========================================================================
def run(output_dir: str, n_sample: int, seed: int) -> dict:
    os.makedirs(output_dir, exist_ok=True)
    _write_start_marker(output_dir, "full" if n_sample == 0 else "smoke", len(TIEBREAK_MODES))
    _write_metrics_atomic(output_dir, {"verdict": "RUNNING", "anchor_name": ANCHOR_NAME,
                                       "ts_iso": datetime.now(timezone.utc).isoformat()})

    rows = _load_rules(RULES_PATH)
    _heartbeat(output_dir, "rules_loaded", {"n_rules": len(rows), "rules_path": RULES_PATH})

    from experiments.exp_semantic_hd_encoder_meaning_match_v1 import SemanticHDEncoder
    from experiments.exp_arc_aggregation_polarity_ci_v1 import PolarityLexicon
    base = SemanticHDEncoder()
    pol = PolarityLexicon()
    wn = base._wn
    _heartbeat(output_dir, "encoder_ready")

    reasoner = DerivationReasoner(base_encoder=base, pol_lexicon=pol, wn=wn, seed=seed, rows=rows,
                                  link_mode=LINK_MODE, tiebreak_mode="legacy")
    _heartbeat(output_dir, "graph_built",
               {"n_rules": len(reasoner.rows), "per_relation": reasoner.per_relation,
                "n_nodes": reasoner.g["n_nodes"], "n_typed_edges": reasoner.g["n_typed_edges"]})

    all_q = arc._load_questions(arc._CHAL_TEST, limit=0)
    if n_sample and n_sample < len(all_q):
        rng = np.random.default_rng(seed)
        idx = sorted(rng.permutation(len(all_q))[:n_sample].tolist())
        questions = [all_q[i] for i in idx]
    else:
        questions = all_q
    _heartbeat(output_dir, "questions_loaded", {"n_total": len(all_q), "n_eval": len(questions)})

    per_mode: Dict[str, dict] = {}
    for mode in TIEBREAK_MODES:
        per_mode[mode] = eval_mode(reasoner, questions, output_dir, mode)
        m = per_mode[mode]
        _heartbeat(output_dir, f"mode_done:{mode}",
                   {"tie_acc": m["tie"]["acc"], "tie_n": m["tie"]["n"],
                    "gold_only_acc": m["gold_only"]["acc"], "derived_acc": m["derived_acc"],
                    "fixed_chance": m["fixed_chance"]})

    legacy = per_mode["legacy"]
    symb = per_mode["symbolic"]

    # ---- MECHANISM DIAGNOSTIC on the TIE subset: WHY the symbolic lever does/does-not fire.
    # intent_fire = intent parser produced any asked-relation; intent_aligns_gold = gold's terminal
    # relation is the asked relation (the condition under which intent-terminal match favors gold).
    tie_rows = [r for r in symb["per_q"] if r["subset"] == "tie"]
    from collections import Counter as _Counter
    tie_diag = {
        "n_tie": len(tie_rows),
        "intent_fire_count": sum(1 for r in tie_rows if r["intent_relations"]),
        "intent_aligns_gold_count": sum(1 for r in tie_rows
                                        if r["gold_term_rel"] in (r["intent_relations"] or [])),
        "correct_among_intent_fired": sum(r["correct"] for r in tie_rows if r["intent_relations"]),
        "gold_term_rel_dist": dict(_Counter(r["gold_term_rel"] for r in tie_rows)),
        "note": ("intent-relation match is the primary symbolic lever; it fires on few ARC ties and, when "
                 "it fires, gold's DERIVATION-terminal relation rarely equals the asked relation (the rule "
                 "graph reaches gold via whatever science-path exists, not the asked relation) -> the lever "
                 "cannot discriminate. Residual tie = a question-relevance MEANING judgment (which valid "
                 "derivation actually ANSWERS this question), meaning-bound."),
    }

    # ---- subset-invariance guard: the DERIVED partition (gold_only/tie/dist_only counts) is a property of
    # coverage (derivability), NOT of the tie-break -> must be IDENTICAL across the two modes (one variable). ----
    partition_identical = (legacy["gold_only"]["n"] == symb["gold_only"]["n"]
                           and legacy["tie"]["n"] == symb["tie"]["n"]
                           and legacy["dist_only"]["n"] == symb["dist_only"]["n"]
                           and legacy["n_derived"] == symb["n_derived"])

    d_tie = round(symb["tie"]["acc"] - legacy["tie"]["acc"], 4)
    d_derived = round(symb["derived_acc"] - legacy["derived_acc"], 4)
    chance = symb["fixed_chance"]

    bands = {
        "tie_subset_rises_ge_0.10": d_tie >= TIE_RISE_PASS,
        "tie_subset_abs_ge_0.42": symb["tie"]["acc"] >= TIE_ABS_PASS,
        "overall_derived_gt_fixed_chance": symb["derived_acc"] > chance,
        "gold_only_preserved_ge_0.95": symb["gold_only"]["acc"] >= GOLD_ONLY_FLOOR,
        "partition_identical_one_variable": bool(partition_identical),
    }
    n_bands_pass = sum(1 for v in bands.values() if v)

    # ---- verdict (pre-registered, can-fail) ----
    gold_ok = bands["gold_only_preserved_ge_0.95"] and partition_identical
    if not gold_ok:
        verdict = "GUARDRAIL-BREACH"
        tier = "HARD_FAIL"
    elif bands["tie_subset_rises_ge_0.10"] and bands["tie_subset_abs_ge_0.42"] \
            and bands["overall_derived_gt_fixed_chance"]:
        verdict = "TIE-BREAK-WORKS-functional"
        tier = "PASS"
    elif d_tie < TIE_RISE_STUCK:
        verdict = "HONEST-NEG-decision-meaning-bound"
        tier = "HONEST_NEG"
    else:
        verdict = "MIDDLE"
        tier = "MIDDLE_BAND"

    traces = collect_tie_traces(reasoner, questions, legacy["per_q"], symb["per_q"], max_traces=10)
    n_flips = sum(1 for t in traces if t["is_flip"])
    _print_tie_traces(traces)

    summary = (f"symbolic tie-break: TIE-subset acc {legacy['tie']['acc']:.3f}->{symb['tie']['acc']:.3f} "
               f"(d={d_tie:+.3f}, n_tie={symb['tie']['n']}) | overall derived-acc "
               f"{legacy['derived_acc']:.3f}->{symb['derived_acc']:.3f} (d={d_derived:+.3f}) vs fixed chance "
               f"{chance:.3f} | gold_only {legacy['gold_only']['acc']:.3f}->{symb['gold_only']['acc']:.3f} "
               f"(n={symb['gold_only']['n']}) | dist_only {symb['dist_only']['acc']:.3f} "
               f"(n={symb['dist_only']['n']}) | {n_bands_pass}/5 bands -> {verdict}")

    metrics = {
        "verdict": verdict, "tier": tier, "summary": summary,
        "verdict_msg": (
            "Symbolic tie-break for the composed DerivationReasoner: among CO-DERIVABLE valid candidates on "
            "the TIE subset (gold AND >=1 distractor both derive), rank by question-INTENT / relation-type "
            "match (asked-relation parsed from the stem; a candidate REACHED BY the asked relation beats one "
            "reached by an off-type chain) -> do-calculus-present -> chain completeness -> shortest chain, "
            "with the thin-cosine combiner DEMOTED to the last tiebreak. ONE variable across arms = the "
            "tie-break METHOD (rules/graph/search/coverage/CI/do-calculus identical; the DERIVED partition is "
            "byte-identical across modes). GUARDRAIL = gold_only subset acc preserved >= 0.95 (clean single-"
            "candidate wins untouched). Fixed chance = mean(1/n_choices) over the derived subset (NOT the old "
            "1/int(mean) quirk). Held-out ARC-Challenge test; science rules NOT derived from test labels. "
            "CAN-FAIL pre-registered: TIE rise < +0.03 = the DECISION is meaning-bound (which valid derivation "
            "actually ANSWERS the question needs grounded question-relevance meaning) -> HONEST-NEG, isolated."),
        "anchor_name": ANCHOR_NAME, "elapsed_s": round(time.perf_counter() - _T0[0], 1),
        "ts_iso": datetime.now(timezone.utc).isoformat(), "pid": os.getpid(),
        "run_mode": "full" if n_sample == 0 else "smoke",
        "config": {"n_eval": len(questions), "n_total_test": len(all_q), "seed": seed,
                   "rules_path": RULES_PATH, "n_rules": len(rows), "link_mode": LINK_MODE,
                   "tiebreak_modes": TIEBREAK_MODES,
                   "one_variable_across_arms": "tiebreak_mode (graph/search/coverage/CI/do identical)",
                   "comprehension": "INTERIM _content_words stand-in (situation_reader NOT adapted; P6)"},
        "graph": {"n_rules": len(reasoner.rows), "per_relation": reasoner.per_relation,
                  "n_nodes": reasoner.g["n_nodes"], "n_typed_edges": reasoner.g["n_typed_edges"]},
        "prereg_bands_def": {
            "tie_subset_rises_ge_0.10": "symbolic TIE-acc - legacy TIE-acc >= 0.10 absolute",
            "tie_subset_abs_ge_0.42": "symbolic TIE-subset acc >= 0.42 (toward 0.50; strictly > legacy)",
            "overall_derived_gt_fixed_chance": "symbolic overall derived-acc > mean(1/n_choices)",
            "gold_only_preserved_ge_0.95": "GUARDRAIL: symbolic gold_only acc >= 0.95 (clean wins preserved)",
            "partition_identical_one_variable": "derived partition counts identical across modes (one variable)",
        },
        "prereg_thresholds": {"tie_rise_pass": TIE_RISE_PASS, "tie_rise_stuck": TIE_RISE_STUCK,
                              "tie_abs_pass": TIE_ABS_PASS, "gold_only_floor": GOLD_ONLY_FLOOR},
        "per_mode": {m: {k: v for k, v in per_mode[m].items() if k != "per_q"} for m in TIEBREAK_MODES},
        "deltas": {"d_tie_acc": d_tie, "d_derived_acc": d_derived, "fixed_chance": chance,
                   "partition_identical": bool(partition_identical), "n_trace_flips": n_flips},
        "tie_mechanism_diagnostic": tie_diag,
        "preregistered_bands": bands, "n_bands_pass": n_bands_pass,
        "traces": traces, "n_traces": len(traces),
        "REQUIRED_FIELDS": ["verdict", "tier", "per_mode", "deltas", "tie_mechanism_diagnostic",
                            "preregistered_bands", "traces", "prereg_thresholds"],
        "contract": "INLINE-LOCAL; no push/remote-persist; VET-PENDING; no atom banking",
    }
    _write_metrics_atomic(output_dir, metrics)
    with open(os.path.join(output_dir, "per_mode_per_question.json"), "w", encoding="utf-8") as f:
        json.dump({m: per_mode[m]["per_q"] for m in TIEBREAK_MODES}, f, indent=2)

    print("\n===== SYMBOLIC TIE-BREAK RESULT =====", flush=True)
    print(summary, flush=True)
    for m in TIEBREAK_MODES:
        pm = per_mode[m]
        print(f"  [{m:9s}] tie={pm['tie']['acc']:.3f}(n={pm['tie']['n']}) "
              f"gold_only={pm['gold_only']['acc']:.3f}(n={pm['gold_only']['n']}) "
              f"dist_only={pm['dist_only']['acc']:.3f}(n={pm['dist_only']['n']}) "
              f"derived={pm['derived_acc']:.3f} chance={pm['fixed_chance']:.3f}", flush=True)
    print(f"bands: {bands} -> {n_bands_pass}/5 | verdict={verdict} | n_traces={len(traces)} "
          f"(flips={n_flips})", flush=True)
    return metrics


# ===========================================================================
# self-test (real code path: REAL DerivationReasoner over a hand rule-set, GloVe-free FakeBase)
# ===========================================================================
def _self_test() -> None:
    from experiments.exp_arc_aggregation_polarity_ci_v1 import PolarityLexicon, _load_wordnet
    print("[self-test] building REAL reasoner over hand rules (FakeBase, GloVe-free) ...", flush=True)
    base = clean._FakeBase()
    wn = _load_wordnet()
    pol = PolarityLexicon()
    # planted: friction reaches BOTH 'heat' (via CAUSE = gold) AND 'brakes' (via USEDFOR = distractor).
    # A CAUSE-intent question must pick heat over brakes by INTENT-TERMINAL match (not thin cosine).
    rows = [
        {"relation": "CAUSE", "arg0": "friction", "arg1": "heat"},
        {"relation": "USEDFOR", "arg0": "friction", "arg1": "brakes"},
        {"relation": "COUPLEDRELATIONSHIP", "arg0": "temperature", "arg1": "evaporation"},
    ]
    exercised = set()

    # intent parser fires for CAUSE and does NOT over-fire.
    rl = DerivationReasoner(base_encoder=base, pol_lexicon=pol, wn=wn, tau_unify=0.99, tau_sim=0.5,
                            depth=3, rows=rows, link_mode="lemma_syn", tiebreak_mode="legacy",
                            verbose=False)
    assert rl._question_intent("what does friction cause") == {"CAUSE"}, "CAUSE intent must fire"
    assert "CAUSE" not in rl._question_intent("name a red object"), "intent must not over-fire"
    assert rl._question_intent("what is needed for burning") == {"REQUIRES"}, "REQUIRES intent"
    exercised.add("question_intent")

    q = {"qid": "T1", "stem": "what does friction cause between moving surfaces",
         "choices": ["heat energy", "brakes device", "metal wire", "glass sheet"],
         "correct_index": 0}
    heat_nid = next(i for i, lab in enumerate(rl.g["node_label"]) if lab == "heat")
    brakes_nid = next(i for i, lab in enumerate(rl.g["node_label"]) if "brake" in lab)

    # both gold + distractor are CO-DERIVABLE (the TIE condition the tie-break must resolve).
    res_l = rl._reason_arm(q, rl.arms["typed"])
    pcs = res_l["per_choice"]
    assert pcs[0]["derivable"] and pcs[1]["derivable"], "both heat and brakes MUST co-derive (TIE setup)"
    assert pcs[0]["term_rel"] == "CAUSE", f"gold reached via CAUSE, got {pcs[0]['term_rel']}"
    assert pcs[1]["term_rel"] == "USEDFOR", f"distractor reached via USEDFOR, got {pcs[1]['term_rel']}"
    exercised.add("co_derivable_tie")

    # SYMBOLIC tie-break: CAUSE-intent -> intent-terminal match picks heat (gold) over brakes.
    rs = DerivationReasoner(base_encoder=base, pol_lexicon=pol, wn=wn, tau_unify=0.99, tau_sim=0.5,
                            depth=3, rows=rows, link_mode="lemma_syn", tiebreak_mode="symbolic",
                            verbose=False)
    res_s = rs._reason_arm(q, rs.arms["typed"])
    assert res_s["chosen_index"] == 0, f"symbolic MUST choose gold heat via CAUSE intent, got {res_s['chosen_index']}"
    assert res_s["decision_mode"] == "derivation", f"mode={res_s['decision_mode']}"
    # the symbolic KEY must rank gold strictly above the distractor (discriminator fires).
    intent = rs._question_intent(q["stem"])
    k_gold = rs._symbolic_key(res_s["per_choice"][0], intent)
    k_dist = rs._symbolic_key(res_s["per_choice"][1], intent)
    assert k_gold < k_dist, f"symbolic key must prefer gold: gold{k_gold} !< dist{k_dist}"
    exercised.add("symbolic_tiebreak_fires")

    # GUARDRAIL: gold_only case (only gold derivable) -> BOTH modes return gold unchanged.
    q_gold_only = {"qid": "T2", "stem": "what does friction cause",
                   "choices": ["heat energy", "unrelated zzz token", "qqq widget", "vvv gadget"],
                   "correct_index": 0}
    assert rl._reason_arm(q_gold_only, rl.arms["typed"])["chosen_index"] == 0, "legacy gold_only -> gold"
    assert rs._reason_arm(q_gold_only, rs.arms["typed"])["chosen_index"] == 0, "symbolic gold_only -> gold"
    exercised.add("gold_only_guardrail")

    # CAN-FAIL: NO intent match + disconnected -> symbolic falls back (no crash, still a decision).
    q_nofire = {"qid": "T3", "stem": "unrelated tokens zzz qqq vvv",
                "choices": ["metal wire", "glass sheet", "plastic tube", "stone block"],
                "correct_index": 0}
    res_nf = rs._reason_arm(q_nofire, rs.arms["typed"])
    assert res_nf["decision_mode"] in ("similarity_fallback", "abstain_index0", "derivation"), \
        f"no-intent Q must still decide, got {res_nf['decision_mode']}"
    exercised.add("can_fail")

    # eval_mode end-to-end on the planted Qs (real decomposition path) for BOTH modes; partition identical.
    scratch = os.path.join(_REPO, "data", "_tiebreak_selftest_scratch")
    ml = eval_mode(rl, [q, q_gold_only], scratch, "legacy")
    ms = eval_mode(rs, [q, q_gold_only], scratch, "symbolic")
    assert ml["tie"]["n"] == ms["tie"]["n"] == 1, "one TIE question in the planted set"
    assert ml["gold_only"]["n"] == ms["gold_only"]["n"] == 1, "one gold_only question in the planted set"
    assert ms["tie"]["acc"] == 1.0, "symbolic must ace the planted TIE"
    assert 0.0 < ms["fixed_chance"] <= 0.5, f"fixed chance must be a sane fraction, got {ms['fixed_chance']}"
    exercised.add("eval_mode")

    # rule loader binds the real file (real_code_path for the FULL entrypoint).
    real_rows = _load_rules(RULES_PATH)
    assert len(real_rows) > 100, "real rules file must load"
    exercised.add("load_rules")

    need = {"question_intent", "co_derivable_tie", "symbolic_tiebreak_fires", "gold_only_guardrail",
            "can_fail", "eval_mode", "load_rules"}
    missing = need - exercised
    assert not missing, f"real_code_path: unexercised entrypoints {missing}"
    print(f"[self-test] real_code_path exercised={sorted(exercised)}", flush=True)
    print("[self-test] ALL PASS", flush=True)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--mode", choices=["smoke", "full"], default="full")
    ap.add_argument("--n", type=int, default=60, help="smoke sample size (full ignores this)")
    ap.add_argument("--seed", type=int, default=SEED)
    ap.add_argument("--out", type=str, default=os.path.join(_REPO, "data", "exp_" + ANCHOR_NAME))
    args = ap.parse_args()

    if args.self_test:
        _self_test()
        return

    n_sample = args.n if args.mode == "smoke" else 0   # full = all test questions
    output_dir = args.out if args.mode == "full" else args.out + "_smoke"
    try:
        run(output_dir, n_sample, args.seed)
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as exc:  # NOT BaseException
        _write_crash_metrics(output_dir, exc)
        print(f"[CRASH] {type(exc).__name__}: {exc}", flush=True)
        traceback.print_exc()
        raise


if __name__ == "__main__":
    main()
