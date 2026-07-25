"""exp_arc_reasoner_link_precision_tie_prune_v1 -- the LAST untested structural lever before the
grounded-meaning commitment: does tightening entity-link PRECISION prune SPURIOUS distractor co-derivations,
converting reasoner TIES into clean gold_only wins WITHOUT collapsing gold-coverage?

VET 29569 (capstone, arc_reasoner_symbolic_tiebreak_v1) MEASURED at link_mode=lemma_syn on the 206 derived
ARC-Challenge questions: gold_only 26 @ 1.00, TIE 66 @ 0.3636 (symbolic tie-break EXHAUSTED, d=0),
dist_only 114 @ 0.00. The symbolic tie-break is done. Remaining structural lever: some TIEs may be SPURIOUS
-- a distractor co-derives only because the lemma_syn WordNet-synonym bridge mapped a distractor word onto a
rule-entity LOOSELY, not because it is a genuine competing answer.

HYPOTHESIS: tighten entity-link precision (loose lemma_syn -> lemma [drop WN synonyms] -> glove [drop the
whole lemma bridge]) -> the distractor's spurious derivation is pruned PRE-tie -> TIE -> gold_only -> gold
wins clean (gold_only is 1.00 by construction). Distinguishes SPURIOUS ties (prunable = structural gain)
from GENUINE ties (both truly derive = meaning-bound).

ONE VARIABLE across the sweep = entity-link precision (link_mode). Reuse hdlab/reasoner.py DerivationReasoner
UNCHANGED (opt-in link_mode; graph/search/CI/decision identical; tiebreak_mode=legacy fixed). link_mode is a
per-instance query-time attribute with mode-keyed caches; ONE instance, flip the mode, no graph rebuild.

PER-TIE INSTRUMENT: baseline lemma_syn defines the 66 tie qids. For each tighter config, cross-tabulate each
baseline-tie qid's NEW subset -> CONVERTED (->gold_only, spurious pruned, gold kept) | GENUINE (->tie) |
BROKE_GOLD (->dist_only) | BROKE_BOTH (->not_derived).

GUARDRAIL (non-negotiable): gold_only@1.00 preserved (baseline 26 gold_only acc >= 0.95) AND gold-coverage
NOT collapsed (gold_cov_ratio >= 0.90). Over-tightening that prunes GOLD chains = trading coverage for false
precision = NOT a win.

CAN-FAIL (pre-registered): few ties convert / most genuine / any real gain requires breaking gold-coverage
-> ties genuinely MEANING-BOUND, both structural doors measured shut -> grounded meaning is the lever
(HONEST-NEG). Many ties convert to clean wins WITHOUT losing gold -> real structural gain (functional lift).

Contract: INLINE-LOCAL foreground-to-completion; NO push/remote-persist; ASCII-only; deterministic; atomic
metrics; start-marker; crash-diagnostic; heartbeat; self-test builds the REAL DerivationReasoner over a hand
rule-set (GloVe-free FakeBase) with a PLANTED spurious tie + genuine tie + broke-gold case and asserts the
cross-tab classifies all three. VET-PENDING (skunkworks owns landed-VET); NO atom banking.

CELL-TEMPLATE MANDATORY: except SystemExit raised BEFORE except Exception (no BaseException); atomic metrics
(tmp+os.replace); start-marker; crash-diag; heartbeat; all numbers MEASURED@ this run.
"""
from __future__ import annotations

import os
import sys
import json
import time
import argparse
import platform
import traceback
from collections import Counter
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

import numpy as np

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)
os.environ.setdefault("GENSIM_DATA_DIR", os.path.join(_REPO, "data", "gensim_cache"))

from hdlab.reasoner import DerivationReasoner
from experiments import exp_arc_knowledge_scale_ingest_climb_v1 as arc
from experiments import exp_arc_derivation_connectivity_gate_cleannodes_v2 as clean

ANCHOR_NAME = "arc_reasoner_link_precision_tie_prune_v1"
SEED = 20260725
RULES_PATH = os.path.join(_REPO, "data", "rules", "arc_science_typed_rules_v1.json")

# precision sweep: loose -> tight. lemma_syn is the VET baseline (defines the ties).
LINK_MODES = ["lemma_syn", "lemma", "glove"]
BASE_MODE = "lemma_syn"
TIEBREAK_MODE = "legacy"                 # FIXED across the sweep (one variable = link precision)

# pre-registered bands (fixed BEFORE the run; reported STRAIGHT, NOT tuned)
CONV_PASS = 10                 # >= this many of the ties CONVERTED at a gold-cov-preserving config = spurious/prunable
CONV_STUCK = 5                 # < this many CONVERTED at every gold-cov-preserving config = genuine
BROKE_MAX_RATIO = 0.5          # BROKE <= 0.5 * CONVERTED for a config to count as clean
GOLD_COV_FLOOR = 0.90          # gold-coverage ratio (tighter / baseline) must stay >= this
GOLD_ONLY_FLOOR = 0.95         # baseline gold_only subset acc must stay >= this under tightening
DERIVED_ACC_RISE = 0.05        # config derived-acc >= baseline derived-acc + this
CHANCE = 0.25                  # fixed chance reference

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
# per-config evaluation: TYPED arm, decompose the derived partition per question
# ===========================================================================
def _valid(c: dict) -> bool:
    return bool(c["derivable"]) and not bool(c["rejected_by_ci"])


def eval_config(reasoner: DerivationReasoner, questions: List[dict], output_dir: str,
                link_mode: str) -> dict:
    """Run the TYPED arm at one link_mode (tiebreak_mode=legacy fixed); decompose every question into
    gold_only / tie / dist_only / not_derived; return per-qid subset + correctness + accuracies."""
    reasoner.link_mode = link_mode
    reasoner.tiebreak_mode = TIEBREAK_MODE
    n = len(questions)
    per_q: Dict[str, dict] = {}
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
        per_q[q["qid"]] = {
            "qid": q["qid"], "correct_index": ci, "n_choices": len(q["choices"]),
            "subset": subset, "chosen": chosen, "correct": int(chosen == ci),
            "gold_valid": bool(gold_valid), "distractor_valid": bool(distractor_valid),
            "decision_mode": res["decision_mode"],
        }
        if (qi + 1) % 300 == 0:
            _heartbeat(output_dir, f"eval:{link_mode}", {"done": qi + 1, "total": n})

    def acc(subset_names) -> Tuple[float, int]:
        rows = [r for r in per_q.values() if r["subset"] in subset_names]
        if not rows:
            return 0.0, 0
        return sum(r["correct"] for r in rows) / len(rows), len(rows)

    derived_names = ("gold_only", "tie", "dist_only")
    derived_rows = [r for r in per_q.values() if r["subset"] in derived_names]
    chance = float(np.mean([1.0 / max(2, r["n_choices"]) for r in derived_rows])) if derived_rows else 0.0
    gold_only_acc, n_gold_only = acc(("gold_only",))
    tie_acc, n_tie = acc(("tie",))
    dist_only_acc, n_dist_only = acc(("dist_only",))
    derived_acc, n_derived = acc(derived_names)
    # gold-coverage = questions where gold is a VALID derivation (gold_only + tie)
    n_gold_cov = sum(1 for r in per_q.values() if r["gold_valid"])

    return {
        "link_mode": link_mode, "n_questions": n, "n_derived": n_derived,
        "fixed_chance": round(chance, 4),
        "gold_only": {"acc": round(gold_only_acc, 4), "n": n_gold_only},
        "tie": {"acc": round(tie_acc, 4), "n": n_tie},
        "dist_only": {"acc": round(dist_only_acc, 4), "n": n_dist_only},
        "derived_acc": round(derived_acc, 4),
        "n_gold_cov": n_gold_cov,
        "per_q": per_q,
    }


def classify_tie_transitions(base_pq: Dict[str, dict], tight_pq: Dict[str, dict],
                             tie_qids: List[str]) -> dict:
    """Cross-tabulate each baseline-tie qid's new subset under a tighter config.
    CONVERTED (->gold_only) | GENUINE (->tie) | BROKE_GOLD (->dist_only) | BROKE_BOTH (->not_derived)."""
    counts = {"CONVERTED": 0, "GENUINE": 0, "BROKE_GOLD": 0, "BROKE_BOTH": 0}
    detail: List[dict] = []
    for qid in tie_qids:
        new = tight_pq[qid]["subset"]
        if new == "gold_only":
            klass = "CONVERTED"
        elif new == "tie":
            klass = "GENUINE"
        elif new == "dist_only":
            klass = "BROKE_GOLD"
        else:
            klass = "BROKE_BOTH"
        counts[klass] += 1
        detail.append({"qid": qid, "new_subset": new, "class": klass,
                       "correct_after": tight_pq[qid]["correct"]})
    counts["BROKE"] = counts["BROKE_GOLD"] + counts["BROKE_BOTH"]
    return {"counts": counts, "detail": detail}


def collect_conversion_traces(reasoner: DerivationReasoner, questions: List[dict],
                              base_pq: Dict[str, dict], tight_pq: Dict[str, dict],
                              tie_qids: List[str], tight_mode: str, max_traces: int = 10) -> List[dict]:
    """Glass-box traces of SPURIOUS ties pruned to clean gold_only wins: for CONVERTED qids, show the gold
    chain that survived tightening and the distractor derivation that vanished (the spurious link)."""
    qmap = {q["qid"]: q for q in questions}
    converted = [qid for qid in tie_qids if tight_pq[qid]["subset"] == "gold_only"]
    traces: List[dict] = []
    for qid in converted[:max_traces]:
        q = qmap[qid]
        ci = q["correct_index"]
        # gold chain under the TIGHT config (gold still derives)
        reasoner.link_mode = tight_mode
        res_t = reasoner._reason_arm(q, reasoner.arms["typed"])
        gold_pc_t = res_t["per_choice"][ci] if ci < len(res_t["per_choice"]) else {}
        # the distractor(s) that derived at BASELINE but not under TIGHT (the spurious link)
        reasoner.link_mode = BASE_MODE
        res_b = reasoner._reason_arm(q, reasoner.arms["typed"])
        spurious = []
        for c in res_b["per_choice"]:
            if c["choice_index"] == ci:
                continue
            was_valid = _valid(c)
            reasoner.link_mode = tight_mode
            c_t = reasoner._reason_arm(q, reasoner.arms["typed"])["per_choice"][c["choice_index"]]
            reasoner.link_mode = BASE_MODE
            now_valid = _valid(c_t)
            if was_valid and not now_valid:
                spurious.append({"choice": c["choice_text"][:90],
                                 "baseline_chain": c.get("chain"),
                                 "baseline_term_rel": c.get("term_rel"),
                                 "note": "derived at lemma_syn, PRUNED under tightening (spurious link)"})
        traces.append({
            "qid": qid, "stem": q["stem"][:280], "tight_mode": tight_mode,
            "gold_choice": q["choices"][ci][:120],
            "chosen_after": q["choices"][res_t["chosen_index"]][:120],
            "correct_after": bool(res_t["chosen_index"] == ci),
            "gold_chain_after": gold_pc_t.get("chain"),
            "gold_term_rel_after": gold_pc_t.get("term_rel"),
            "pruned_spurious_distractors": spurious,
        })
    reasoner.link_mode = BASE_MODE
    return traces


def _print_conversion_traces(traces: List[dict]) -> None:
    print("\n" + "=" * 78, flush=True)
    print("GLASS-BOX PRECISION-CONVERSION TRACES (spurious tie pruned -> clean gold_only win)", flush=True)
    print("=" * 78, flush=True)
    for t in traces:
        print(f"\n[CONVERTED via {t['tight_mode']}] qid={t['qid']} correct_after={t['correct_after']}", flush=True)
        print(f"  Q: {t['stem']}", flush=True)
        print(f"  gold  : {t['gold_choice']}", flush=True)
        if t["gold_chain_after"]:
            print(f"  gold DERIVATION (survived tightening): {t['gold_chain_after']} "
                  f"(term_rel={t['gold_term_rel_after']})", flush=True)
        for s in t["pruned_spurious_distractors"]:
            print(f"  x pruned distractor: {s['choice']} :: {s['note']}", flush=True)
            if s["baseline_chain"]:
                print(f"      (was: {s['baseline_chain']}  term_rel={s['baseline_term_rel']})", flush=True)


# ===========================================================================
# main run
# ===========================================================================
def run(output_dir: str, n_sample: int, seed: int) -> dict:
    os.makedirs(output_dir, exist_ok=True)
    _write_start_marker(output_dir, "full" if n_sample == 0 else "smoke", len(LINK_MODES))
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
                                  link_mode=BASE_MODE, tiebreak_mode=TIEBREAK_MODE)
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

    per_config: Dict[str, dict] = {}
    for lm in LINK_MODES:
        per_config[lm] = eval_config(reasoner, questions, output_dir, lm)
        m = per_config[lm]
        _heartbeat(output_dir, f"config_done:{lm}",
                   {"gold_only_n": m["gold_only"]["n"], "tie_n": m["tie"]["n"],
                    "dist_only_n": m["dist_only"]["n"], "n_gold_cov": m["n_gold_cov"],
                    "derived_acc": m["derived_acc"]})

    base_cfg = per_config[BASE_MODE]
    base_pq = base_cfg["per_q"]
    base_derived_acc = base_cfg["derived_acc"]
    base_gold_cov = base_cfg["n_gold_cov"]
    tie_qids = sorted(qid for qid, r in base_pq.items() if r["subset"] == "tie")
    gold_only_qids = sorted(qid for qid, r in base_pq.items() if r["subset"] == "gold_only")

    # ---- per-config transition analysis vs baseline ----
    tighten_modes = [lm for lm in LINK_MODES if lm != BASE_MODE]
    transitions: Dict[str, dict] = {}
    for tm in tighten_modes:
        tight_pq = per_config[tm]["per_q"]
        trans = classify_tie_transitions(base_pq, tight_pq, tie_qids)
        gold_cov_ratio = (per_config[tm]["n_gold_cov"] / base_gold_cov) if base_gold_cov else 0.0
        # gold_only guardrail: baseline gold_only qids still correct under tightening
        go_correct = sum(tight_pq[qid]["correct"] for qid in gold_only_qids)
        gold_only_preserved = (go_correct / len(gold_only_qids)) if gold_only_qids else 1.0
        c = trans["counts"]
        converted, broke = c["CONVERTED"], c["BROKE"]
        cov_ok = gold_cov_ratio >= GOLD_COV_FLOOR
        go_ok = gold_only_preserved >= GOLD_ONLY_FLOOR
        clean = (broke <= BROKE_MAX_RATIO * converted) if converted > 0 else True
        acc_rise = round(per_config[tm]["derived_acc"] - base_derived_acc, 4)
        transitions[tm] = {
            "counts": c, "gold_cov_ratio": round(gold_cov_ratio, 4),
            "n_gold_cov": per_config[tm]["n_gold_cov"],
            "gold_only_preserved": round(gold_only_preserved, 4),
            "derived_acc": per_config[tm]["derived_acc"], "derived_acc_rise": acc_rise,
            "guardrail_cov_ok": bool(cov_ok), "guardrail_gold_only_ok": bool(go_ok),
            "broke_clean": bool(clean),
            "detail": trans["detail"],
        }

    # ---- verdict (pre-registered, can-fail); evaluate on gold-cov-preserving configs ----
    preserving = {tm: t for tm, t in transitions.items()
                  if t["guardrail_cov_ok"] and t["guardrail_gold_only_ok"]}
    # a config is a functional WIN if it preserves guardrails AND converts >= CONV_PASS clean AND acc rises
    win_configs = {tm: t for tm, t in preserving.items()
                   if t["counts"]["CONVERTED"] >= CONV_PASS and t["broke_clean"]
                   and t["derived_acc_rise"] >= DERIVED_ACC_RISE and t["derived_acc"] > CHANCE}
    # conversion happens but only by breaking gold-coverage (any config w/ >=CONV_STUCK converts but fails cov guard)
    conversion_needs_breaking = any(
        t["counts"]["CONVERTED"] >= CONV_STUCK and not t["guardrail_cov_ok"]
        for t in transitions.values())
    max_conv_preserving = max((t["counts"]["CONVERTED"] for t in preserving.values()), default=0)

    if win_configs:
        best_tm = max(win_configs, key=lambda k: win_configs[k]["counts"]["CONVERTED"])
        verdict = "PRECISION-CONVERTS-TIES-functional"
        tier = "PASS"
    elif max_conv_preserving < CONV_STUCK and not (
            any(t["counts"]["CONVERTED"] >= CONV_STUCK for t in transitions.values())):
        best_tm = None
        verdict = "HONEST-NEG-ties-genuine-meaning-bound"
        tier = "HONEST_NEG"
    elif conversion_needs_breaking and not win_configs and max_conv_preserving < CONV_PASS:
        best_tm = None
        verdict = "HONEST-NEG-ties-genuine-meaning-bound"
        tier = "HONEST_NEG"
    else:
        best_tm = max(transitions, key=lambda k: transitions[k]["counts"]["CONVERTED"])
        verdict = "MIDDLE"
        tier = "MIDDLE_BAND"

    # traces from the best available tightening (win config, else max-conversion config)
    trace_tm = best_tm if best_tm is not None else max(
        transitions, key=lambda k: transitions[k]["counts"]["CONVERTED"])
    traces = collect_conversion_traces(reasoner, questions, base_pq, per_config[trace_tm]["per_q"],
                                       tie_qids, trace_tm, max_traces=10)
    _print_conversion_traces(traces)

    # headline numbers from the reported config (best win, else max-conversion preserving-or-not)
    head_tm = best_tm if best_tm is not None else trace_tm
    head = transitions[head_tm]
    hc = head["counts"]

    summary = (f"link precision [{BASE_MODE}->{head_tm}]: of {len(tie_qids)} ties -> "
               f"{hc['CONVERTED']} spurious(converted) / {hc['GENUINE']} genuine / "
               f"{hc['BROKE']} broke-gold (BG={hc['BROKE_GOLD']},BB={hc['BROKE_BOTH']}) | "
               f"gold-coverage {base_gold_cov}->{head['n_gold_cov']} (ratio={head['gold_cov_ratio']:.3f}) | "
               f"gold_only preserved={head['gold_only_preserved']:.3f} | derived-acc "
               f"{base_derived_acc:.3f}->{head['derived_acc']:.3f} (d={head['derived_acc_rise']:+.3f}) "
               f"vs chance {CHANCE:.2f} | verdict={verdict}")

    metrics = {
        "verdict": verdict, "tier": tier, "summary": summary,
        "verdict_msg": (
            "Entity-link PRECISION sweep on the composed DerivationReasoner: does tightening link_mode "
            "(loose lemma_syn -> lemma [drop WordNet synonyms] -> glove [drop the whole lemma bridge]) prune "
            "SPURIOUS distractor co-derivations PRE-tie, converting TIE -> gold_only (clean gold win) WITHOUT "
            "collapsing gold-coverage? ONE variable across the sweep = link precision (graph/search/CI/decision "
            "identical; tiebreak_mode=legacy fixed). Per-tie cross-tab classifies each baseline-tie qid's new "
            "subset: CONVERTED(->gold_only, spurious pruned + gold kept) | GENUINE(->tie) | BROKE_GOLD(->dist_"
            "only) | BROKE_BOTH(->not_derived). GUARDRAIL = gold_only@1.00 preserved (>=0.95) AND gold-coverage "
            "ratio >=0.90 (over-tightening that prunes GOLD = trading coverage for false precision = NOT a win). "
            "Held-out ARC-Challenge test; science rules NOT derived from test labels. CAN-FAIL pre-registered: "
            "few convert / most genuine / gain requires breaking gold-coverage -> ties MEANING-BOUND (grounded "
            "meaning is the lever), both structural doors measured shut. Emits traces of spurious ties pruned "
            "to clean wins."),
        "anchor_name": ANCHOR_NAME, "elapsed_s": round(time.perf_counter() - _T0[0], 1),
        "ts_iso": datetime.now(timezone.utc).isoformat(), "pid": os.getpid(),
        "run_mode": "full" if n_sample == 0 else "smoke",
        "config": {"n_eval": len(questions), "n_total_test": len(all_q), "seed": seed,
                   "rules_path": RULES_PATH, "n_rules": len(rows), "link_modes": LINK_MODES,
                   "base_mode": BASE_MODE, "tiebreak_mode": TIEBREAK_MODE,
                   "one_variable_across_arms": "link_mode (entity-link precision; graph/search/CI/decision identical)",
                   "comprehension": "INTERIM _content_words stand-in (situation_reader NOT adapted; P6)"},
        "graph": {"n_rules": len(reasoner.rows), "per_relation": reasoner.per_relation,
                  "n_nodes": reasoner.g["n_nodes"], "n_typed_edges": reasoner.g["n_typed_edges"]},
        "baseline_partition": {"link_mode": BASE_MODE, "gold_only_n": base_cfg["gold_only"]["n"],
                               "tie_n": base_cfg["tie"]["n"], "dist_only_n": base_cfg["dist_only"]["n"],
                               "n_derived": base_cfg["n_derived"], "n_gold_cov": base_gold_cov,
                               "derived_acc": base_derived_acc,
                               "gold_only_acc": base_cfg["gold_only"]["acc"],
                               "tie_acc": base_cfg["tie"]["acc"]},
        "per_config": {lm: {k: v for k, v in per_config[lm].items() if k != "per_q"} for lm in LINK_MODES},
        "tie_transitions": {tm: {k: v for k, v in transitions[tm].items() if k != "detail"}
                            for tm in tighten_modes},
        "prereg_thresholds": {"conv_pass": CONV_PASS, "conv_stuck": CONV_STUCK,
                              "broke_max_ratio": BROKE_MAX_RATIO, "gold_cov_floor": GOLD_COV_FLOOR,
                              "gold_only_floor": GOLD_ONLY_FLOOR, "derived_acc_rise": DERIVED_ACC_RISE,
                              "chance": CHANCE},
        "reported_config": head_tm,
        "n_ties_baseline": len(tie_qids),
        "traces": traces, "n_traces": len(traces),
        "REQUIRED_FIELDS": ["verdict", "tier", "baseline_partition", "per_config", "tie_transitions",
                            "prereg_thresholds", "reported_config", "traces"],
        "contract": "INLINE-LOCAL; no push/remote-persist; VET-PENDING; no atom banking",
    }
    _write_metrics_atomic(output_dir, metrics)
    with open(os.path.join(output_dir, "tie_transition_detail.json"), "w", encoding="utf-8") as f:
        json.dump({tm: transitions[tm]["detail"] for tm in tighten_modes}, f, indent=2)

    print("\n===== LINK-PRECISION TIE-PRUNE RESULT =====", flush=True)
    print(summary, flush=True)
    for lm in LINK_MODES:
        pm = per_config[lm]
        print(f"  [{lm:9s}] gold_only={pm['gold_only']['n']} tie={pm['tie']['n']} "
              f"dist_only={pm['dist_only']['n']} gold_cov={pm['n_gold_cov']} "
              f"derived_acc={pm['derived_acc']:.3f}", flush=True)
    for tm in tighten_modes:
        t = transitions[tm]
        c = t["counts"]
        print(f"  transitions {BASE_MODE}->{tm}: CONVERTED={c['CONVERTED']} GENUINE={c['GENUINE']} "
              f"BROKE_GOLD={c['BROKE_GOLD']} BROKE_BOTH={c['BROKE_BOTH']} | cov_ratio={t['gold_cov_ratio']:.3f} "
              f"gold_only_preserved={t['gold_only_preserved']:.3f} guards(cov={t['guardrail_cov_ok']},"
              f"go={t['guardrail_gold_only_ok']},clean={t['broke_clean']})", flush=True)
    print(f"verdict={verdict} | tier={tier} | reported_config={head_tm} | n_traces={len(traces)}", flush=True)
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
    # planted rule graph: 'rain' reaches gold 'river' (lemma-exact link, survives), a distractor node
    # 'stone' (reachable ONLY via the WN synonym 'rock'->stone; lemma_syn-only = SPURIOUS), and 'metal'
    # (lemma-exact, GENUINE competitor).
    rows = [
        {"relation": "CAUSE", "arg0": "rain", "arg1": "river"},
        {"relation": "CAUSE", "arg0": "rain", "arg1": "stone"},
        {"relation": "CAUSE", "arg0": "rain", "arg1": "metal"},
    ]
    exercised = set()

    reasoner = DerivationReasoner(base_encoder=base, pol_lexicon=pol, wn=wn, tau_unify=0.99, tau_sim=0.5,
                                  depth=3, rows=rows, link_mode=BASE_MODE, tiebreak_mode=TIEBREAK_MODE,
                                  verbose=False)
    # sanity: 'rock' links to node 'stone' ONLY in lemma_syn (synonym), NOT in lemma.
    stone_nid = next(i for i, lab in enumerate(reasoner.g["node_label"]) if lab == "stone")
    reasoner.link_mode = "lemma_syn"
    assert stone_nid in reasoner.nodes_for("rock hard"), "lemma_syn: 'rock'->stone synonym MUST link"
    reasoner.link_mode = "lemma"
    reasoner._word2nodes.clear()  # clear glove cache only; sym cache is mode-keyed
    assert stone_nid not in reasoner.nodes_for("rock hard"), "lemma: 'rock'->stone MUST NOT link (tighter)"
    exercised.add("link_precision_prunes")

    # three planted questions exercising all three transition classes.
    q_spurious = {"qid": "S1", "stem": "what does rain cause to form",
                  "choices": ["river water", "rock formation", "glass sheet", "plastic tube"],
                  "correct_index": 0}   # lemma_syn: river+stone(via rock) derive=TIE; lemma: only river=gold_only
    q_genuine = {"qid": "G1", "stem": "what does rain cause to form",
                 "choices": ["river water", "metal ore", "glass sheet", "plastic tube"],
                 "correct_index": 0}    # both river+metal lemma-exact -> TIE in both modes
    q_broke = {"qid": "B1", "stem": "what does rain cause to form",
               "choices": ["rock formation", "metal ore", "glass sheet", "plastic tube"],
               "correct_index": 0}      # gold=rock(->stone syn); lemma_syn TIE; lemma: gold lost -> dist_only
    qs = [q_spurious, q_genuine, q_broke]
    scratch = os.path.join(_REPO, "data", "_link_precision_selftest_scratch")

    base_cfg = eval_config(reasoner, qs, scratch, "lemma_syn")
    lemma_cfg = eval_config(reasoner, qs, scratch, "lemma")
    exercised.add("eval_config")
    bpq, lpq = base_cfg["per_q"], lemma_cfg["per_q"]
    # baseline: all three are ties
    assert bpq["S1"]["subset"] == "tie", f"S1 baseline must be tie, got {bpq['S1']['subset']}"
    assert bpq["G1"]["subset"] == "tie", f"G1 baseline must be tie, got {bpq['G1']['subset']}"
    assert bpq["B1"]["subset"] == "tie", f"B1 baseline must be tie, got {bpq['B1']['subset']}"

    tie_qids = sorted(qid for qid, r in bpq.items() if r["subset"] == "tie")
    assert len(tie_qids) == 3, f"expected 3 baseline ties, got {len(tie_qids)}"
    trans = classify_tie_transitions(bpq, lpq, tie_qids)
    exercised.add("classify_tie_transitions")
    by_qid = {d["qid"]: d["class"] for d in trans["detail"]}
    assert by_qid["S1"] == "CONVERTED", f"S1 must CONVERT (spurious pruned), got {by_qid['S1']}"
    assert by_qid["G1"] == "GENUINE", f"G1 must stay GENUINE tie, got {by_qid['G1']}"
    assert by_qid["B1"] in ("BROKE_GOLD", "BROKE_BOTH"), f"B1 must BREAK gold, got {by_qid['B1']}"
    assert trans["counts"]["CONVERTED"] == 1 and trans["counts"]["GENUINE"] == 1, \
        f"transition counts wrong: {trans['counts']}"
    # CONVERTED question is now correctly answered (gold_only -> gold picked)
    assert lpq["S1"]["subset"] == "gold_only" and lpq["S1"]["correct"] == 1, \
        "converted S1 must be gold_only + correct"
    print(f"[self-test] cross-tab: {trans['counts']} (S1=CONVERTED, G1=GENUINE, B1=BROKE)", flush=True)

    # can-fail: if the synonym bridge were the ONLY thing linking a real competitor, tightening would
    # BREAK it (B1 above) -> the classifier records BROKE, not a phantom win. (already asserted.)
    exercised.add("can_fail_broke")

    # conversion trace builder fires on the CONVERTED qid and names the pruned spurious distractor.
    traces = collect_conversion_traces(reasoner, qs, bpq, lpq, tie_qids, "lemma", max_traces=5)
    assert any(t["qid"] == "S1" for t in traces), "conversion trace must include the converted S1"
    s1_tr = next(t for t in traces if t["qid"] == "S1")
    assert s1_tr["gold_chain_after"] and "-->" in s1_tr["gold_chain_after"], "gold chain must survive"
    assert s1_tr["pruned_spurious_distractors"], "trace must name the pruned spurious distractor"
    exercised.add("collect_conversion_traces")
    print(f"[self-test] conversion trace: gold survived={s1_tr['gold_chain_after']}, "
          f"pruned={[s['choice'] for s in s1_tr['pruned_spurious_distractors']]}", flush=True)

    # real rules file binds (real_code_path for the FULL entrypoint).
    real_rows = _load_rules(RULES_PATH)
    assert len(real_rows) > 100, "real rules file must load"
    exercised.add("load_rules")

    need = {"link_precision_prunes", "eval_config", "classify_tie_transitions", "can_fail_broke",
            "collect_conversion_traces", "load_rules"}
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
