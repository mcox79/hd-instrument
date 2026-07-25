"""exp_arc_reasoner_entity_linking_upgrade_v1 -- raise DEMONSTRATED reasoning-coverage of the composed
DerivationReasoner (hdlab/reasoner.py) by UPGRADING the front-end question->rule-entity linker, while
preserving SELECTIVITY (distractor-derive-rate).

WHAT / WHY
  The composed reasoner already emits correct selective glass-box derivation traces where it fires, but
  fires on only ~11-15% of ARC-Challenge because node-identity (question words -> rule entities) uses a
  strict GloVe cos>=0.85 bridge that cannot cross paraphrase ("shorter day" -> rule entity "daytime").
  The rules are VALID + cover the content; the gap is the LANGUAGE bridge (research finding, load-bearing).

THE UPGRADE (one variable across arms = the entity-LINKING mode; rules/graph/search/decision identical):
  link_mode = "glove"     : original strict GloVe cos>=tau_unify only (the BEFORE baseline).
  link_mode = "lemma"     : + TIGHT symbolic bridge -- morphy lemma / raw-token EXACT match to node-label
                            lemmas (rocks<->rock, days<->day). No hypernym spread.
  link_mode = "lemma_syn" : + WordNet SAME-SYNSET single-token synonyms (rock<->stone, fast<->quick).

GUARDRAIL (non-negotiable): SELECTIVITY = distractor-derive-rate (fraction of the 3 wrong choices that
  become derivable) MUST stay low (near the ~0.063 baseline). If the upgrade raises coverage by making
  EVERYTHING derive (distractors too) that is the vacuous-supply failure = NEG, not a win. Coverage AND
  selectivity reported TOGETHER, per mode.

DECISIVE TEST (full ARC-Challenge test, held-out; the science rules are NOT derived from test labels --
  selectivity is the anti-leak check): (a) does derive-COVERAGE rise vs glove while (b) SELECTIVITY holds
  AND (c) gold-derivable questions get the CORRECT answer AND (d) accuracy-on-derived >= similarity
  baseline on the same subset? Emit >=8 glass-box derivation traces.

CAN-FAIL (pre-registered honestly): if coverage stays ~stuck despite the lemma/synonym upgrade, OR rises
  only by losing selectivity -> the question-language->rule-entity bridge genuinely needs GROUNDED MEANING
  (the #1 wall); reasoning-coverage is meaning-bound, isolated cleanly -> HONEST-NEG.

Contract: INLINE-LOCAL foreground-to-completion; NO push/remote-persist; ASCII-only; deterministic;
  atomic metrics; start-marker; crash-diagnostic; heartbeat; self-test builds the REAL DerivationReasoner
  over a hand rule-set (GloVe-free FakeBase) and asserts the link-mode upgrade fires + stays selective.
  VET-PENDING (skunkworks owns landed-VET); no atom banking.

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

from hdlab.reasoner import DerivationReasoner, evaluate, _collect_traces, _print_traces
from experiments import exp_arc_knowledge_scale_ingest_climb_v1 as arc
from experiments import exp_arc_derivation_connectivity_gate_cleannodes_v2 as clean

ANCHOR_NAME = "arc_reasoner_entity_linking_upgrade_v1"
SEED = 20260725
RULES_PATH = os.path.join(_REPO, "data", "rules", "arc_science_typed_rules_v1.json")
LINK_MODES = ["glove", "lemma", "lemma_syn"]

# pre-registered thresholds (fixed BEFORE the run; reported STRAIGHT, NOT tuned)
BASELINE_DISTRACTOR_RATE = 0.063     # research-reported selectivity of the composed reasoner
SELECTIVITY_CEIL = 0.13              # upgrade must keep distractor-derive-rate <= ~2x baseline
COVERAGE_RISE_PASS = 0.05           # coverage must rise >= +0.05 absolute vs glove for PASS
COVERAGE_RISE_STUCK = 0.03         # coverage rise < this despite upgrade = meaning-bound HONEST-NEG
GOLD_RISE_PASS = 0.03              # gold-derivable rate must rise >= this vs glove

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
# rule loading + per-mode analysis
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


def _analyze(report: dict) -> dict:
    """Coverage + SELECTIVITY (distractor-derive-rate) + correctness, from evaluate()'s per_q (typed arm)."""
    per_q = report["per_q"]
    n = len(per_q)
    gold_derivable = 0
    distractor_num = 0
    distractor_den = 0
    n_derived = 0
    derived_correct = 0
    derived_baseline_correct = 0
    gold_derivable_correct = 0
    for row in per_q:
        ci = row["correct_index"]
        typed = row["typed"]
        pcs = typed["per_choice"]
        for c in pcs:
            if c["choice_index"] == ci:
                if c["derivable"]:
                    gold_derivable += 1
                    if typed["correct"]:
                        gold_derivable_correct += 1
            else:
                distractor_den += 1
                if c["derivable"]:
                    distractor_num += 1
        if typed["mode"] == "derivation":
            n_derived += 1
            derived_correct += typed["correct"]
            derived_baseline_correct += row["baseline"]["correct"]
    return {
        "n_questions": n,
        "coverage_fraction": report["coverage_fraction"],
        "n_covered": report["n_covered"],
        "gold_derive_rate": round(gold_derivable / n, 4) if n else 0.0,
        "n_gold_derivable": gold_derivable,
        "distractor_derive_rate": round(distractor_num / distractor_den, 4) if distractor_den else 0.0,
        "n_distractors": distractor_den, "n_distractors_derivable": distractor_num,
        "n_derived": n_derived,
        "derived_subset_acc": round(derived_correct / n_derived, 4) if n_derived else 0.0,
        "derived_subset_baseline_acc": round(derived_baseline_correct / n_derived, 4) if n_derived else 0.0,
        "gold_derivable_acc": round(gold_derivable_correct / gold_derivable, 4) if gold_derivable else 0.0,
        "covered_typed_acc": report["covered_subset"]["typed_acc"],
        "covered_baseline_acc": report["covered_subset"]["baseline_acc"],
        "covered_shuffle_acc": report["covered_subset"]["shuffle_direction_acc"],
        "covered_untyped_null_acc": report["covered_subset"]["untyped_null_acc"],
        "whole_typed_acc": report["typed_whole_set_acc"],
        "whole_baseline_acc": report["baseline_whole_set_acc"],
        "chance": report["chance"],
    }


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

    # ONE reasoner over the 233 science rules; graph built ONCE (link_mode toggles only the front-end).
    reasoner = DerivationReasoner(base_encoder=base, pol_lexicon=pol, wn=wn, seed=seed, rows=rows,
                                  link_mode="glove")
    _heartbeat(output_dir, "graph_built",
               {"n_rules": len(reasoner.rows), "per_relation": reasoner.per_relation,
                "n_nodes": reasoner.g["n_nodes"], "n_typed_edges": reasoner.g["n_typed_edges"],
                "max_typed_node_degree": reasoner.g["max_typed_node_degree"],
                "n_merges": reasoner.g["n_merges"], "n_node_lemma_keys": len(reasoner._node_lemma_index)})

    all_q = arc._load_questions(arc._CHAL_TEST, limit=0)
    if n_sample and n_sample < len(all_q):
        rng = np.random.default_rng(seed)
        idx = sorted(rng.permutation(len(all_q))[:n_sample].tolist())
        questions = [all_q[i] for i in idx]
    else:
        questions = all_q
    _heartbeat(output_dir, "questions_loaded", {"n_total": len(all_q), "n_eval": len(questions)})

    per_mode: Dict[str, dict] = {}
    per_mode_reports: Dict[str, dict] = {}
    for mode in LINK_MODES:
        reasoner.link_mode = mode
        rep = evaluate(reasoner, questions, output_dir)
        per_mode_reports[mode] = rep
        per_mode[mode] = _analyze(rep)
        _heartbeat(output_dir, f"mode_done:{mode}",
                   {"coverage": per_mode[mode]["coverage_fraction"],
                    "distractor_derive_rate": per_mode[mode]["distractor_derive_rate"],
                    "gold_derive_rate": per_mode[mode]["gold_derive_rate"],
                    "derived_acc": per_mode[mode]["derived_subset_acc"]})

    # ---- upgrade-arm selection: GUARDRAIL-FIRST (pre-registered decision rule, NOT tuned) ----
    # the upgrade arm = the HIGHER-coverage of {lemma, lemma_syn} that keeps selectivity <= SELECTIVITY_CEIL.
    # if neither keeps selectivity -> that IS the loss-of-selectivity failure.
    glove = per_mode["glove"]
    selective_upgrades = [m for m in ("lemma_syn", "lemma")
                          if per_mode[m]["distractor_derive_rate"] <= SELECTIVITY_CEIL]
    if selective_upgrades:
        upgrade_mode = max(selective_upgrades, key=lambda m: per_mode[m]["coverage_fraction"])
        selectivity_preserved = True
    else:
        # no selective upgrade: pick the higher-coverage one to characterize the loss
        upgrade_mode = max(("lemma_syn", "lemma"), key=lambda m: per_mode[m]["coverage_fraction"])
        selectivity_preserved = False
    up = per_mode[upgrade_mode]

    d_cov = round(up["coverage_fraction"] - glove["coverage_fraction"], 4)
    d_gold = round(up["gold_derive_rate"] - glove["gold_derive_rate"], 4)
    correctness_ok = (up["derived_subset_acc"] >= up["derived_subset_baseline_acc"]
                      and up["derived_subset_acc"] > up["chance"])

    bands = {
        "coverage_rises_ge_0.05": d_cov >= COVERAGE_RISE_PASS,
        "selectivity_preserved_le_0.13": selectivity_preserved,
        "gold_reachability_rises_ge_0.03": d_gold >= GOLD_RISE_PASS,
        "derived_acc_ge_baseline_and_gt_chance": bool(correctness_ok),
    }
    n_bands_pass = sum(1 for v in bands.values() if v)

    # ---- verdict (pre-registered, can-fail) ----
    if selectivity_preserved and bands["coverage_rises_ge_0.05"] and bands["gold_reachability_rises_ge_0.03"] \
            and bands["derived_acc_ge_baseline_and_gt_chance"]:
        verdict = "REASONING-COVERAGE-RISES-SELECTIVE"
        tier = "PASS"
    elif (d_cov < COVERAGE_RISE_STUCK) or (not selectivity_preserved):
        verdict = "HONEST-NEG-coverage-meaning-bound"
        tier = "HONEST_NEG"
    else:
        verdict = "MIDDLE"
        tier = "MIDDLE_BAND"

    # ---- glass-box traces (>=8) from the upgrade arm ----
    reasoner.link_mode = upgrade_mode
    traces = _collect_traces(reasoner, questions, per_mode_reports[upgrade_mode]["per_q"],
                             max_correct=6, max_neg=3)
    _print_traces(traces)

    summary = (f"entity-linking upgrade [{glove['coverage_fraction']:.3f} glove -> "
               f"{up['coverage_fraction']:.3f} {upgrade_mode}] d_cov={d_cov:+.3f} | "
               f"selectivity distractor-rate {glove['distractor_derive_rate']:.3f}->"
               f"{up['distractor_derive_rate']:.3f} (ceil {SELECTIVITY_CEIL}) | "
               f"gold-derive {glove['gold_derive_rate']:.3f}->{up['gold_derive_rate']:.3f} (d={d_gold:+.3f}) | "
               f"derived-acc {up['derived_subset_acc']:.3f} vs baseline {up['derived_subset_baseline_acc']:.3f} "
               f"(n_derived={up['n_derived']}, chance={up['chance']:.3f}) | "
               f"{n_bands_pass}/4 bands -> {verdict}")

    metrics = {
        "verdict": verdict, "tier": tier, "summary": summary,
        "verdict_msg": (
            "Front-end entity-linking upgrade for the composed DerivationReasoner: question-word->rule-entity "
            "bridging via TIGHT morphy-lemma exact match (lemma) + WordNet same-synset single-token synonyms "
            "(lemma_syn), on top of the strict GloVe cos>=tau_unify baseline (glove). One variable across arms "
            "= the LINK MODE (rules/graph/search/decision identical). GUARDRAIL = distractor-derive-rate "
            "(selectivity). Upgrade arm chosen GUARDRAIL-FIRST: higher-coverage of {lemma,lemma_syn} that keeps "
            f"distractor-derive-rate <= {SELECTIVITY_CEIL}. Bands reported STRAIGHT, NOT tuned. Held-out ARC-"
            "Challenge test; rules are science facts not derived from test labels; selectivity is the anti-leak "
            "check. CAN-FAIL pre-registered: coverage stuck OR bought by losing selectivity = meaning-bound "
            "HONEST-NEG (reasoning-coverage is meaning-bound -> the #1 grounded-meaning wall, isolated cleanly)."),
        "anchor_name": ANCHOR_NAME, "elapsed_s": round(time.perf_counter() - _T0[0], 1),
        "ts_iso": datetime.now(timezone.utc).isoformat(), "pid": os.getpid(),
        "run_mode": "full" if n_sample == 0 else "smoke",
        "config": {"n_eval": len(questions), "n_total_test": len(all_q), "seed": seed,
                   "rules_path": RULES_PATH, "n_rules": len(rows), "link_modes": LINK_MODES,
                   "upgrade_mode_selected": upgrade_mode, "selectivity_preserved": selectivity_preserved,
                   "one_variable_across_arms": "entity-link mode (graph/search/decision identical)",
                   "comprehension": "INTERIM _content_words stand-in (situation_reader NOT adapted; P6)"},
        "graph": {"n_rules": len(reasoner.rows), "per_relation": reasoner.per_relation,
                  "n_nodes": reasoner.g["n_nodes"], "n_typed_edges": reasoner.g["n_typed_edges"],
                  "max_typed_node_degree": reasoner.g["max_typed_node_degree"],
                  "n_merges": reasoner.g["n_merges"], "n_node_lemma_keys": len(reasoner._node_lemma_index)},
        "prereg_thresholds": {"baseline_distractor_rate": BASELINE_DISTRACTOR_RATE,
                              "selectivity_ceil": SELECTIVITY_CEIL,
                              "coverage_rise_pass": COVERAGE_RISE_PASS,
                              "coverage_rise_stuck": COVERAGE_RISE_STUCK, "gold_rise_pass": GOLD_RISE_PASS},
        "per_mode": per_mode,
        "upgrade_vs_glove": {"upgrade_mode": upgrade_mode, "d_coverage": d_cov, "d_gold_derive": d_gold,
                             "selectivity_preserved": selectivity_preserved,
                             "correctness_ok": bool(correctness_ok)},
        "preregistered_bands": bands, "n_bands_pass": n_bands_pass,
        "bands_definition": {
            "coverage_rises_ge_0.05": "coverage(upgrade) - coverage(glove) >= 0.05 absolute",
            "selectivity_preserved_le_0.13": "upgrade distractor-derive-rate <= 0.13 (~2x the 0.063 baseline)",
            "gold_reachability_rises_ge_0.03": "gold-derive-rate(upgrade) - gold-derive-rate(glove) >= 0.03",
            "derived_acc_ge_baseline_and_gt_chance": "derived-subset acc >= similarity baseline on same subset AND > chance",
        },
        "traces": traces, "n_traces": len(traces),
        "REQUIRED_FIELDS": ["verdict", "tier", "per_mode", "upgrade_vs_glove", "preregistered_bands",
                            "traces", "prereg_thresholds"],
        "contract": "INLINE-LOCAL; no push/remote-persist; VET-PENDING; no atom banking",
    }
    _write_metrics_atomic(output_dir, metrics)
    with open(os.path.join(output_dir, "per_mode_per_question.json"), "w", encoding="utf-8") as f:
        json.dump({m: per_mode_reports[m]["per_q"] for m in LINK_MODES}, f, indent=2)

    print("\n===== ENTITY-LINKING UPGRADE RESULT =====", flush=True)
    print(summary, flush=True)
    for m in LINK_MODES:
        pm = per_mode[m]
        print(f"  [{m:10s}] cov={pm['coverage_fraction']:.3f} gold={pm['gold_derive_rate']:.3f} "
              f"distractor={pm['distractor_derive_rate']:.3f} derived_acc={pm['derived_subset_acc']:.3f} "
              f"(base {pm['derived_subset_baseline_acc']:.3f}, n_der={pm['n_derived']}) "
              f"covered_typed={pm['covered_typed_acc']:.3f}", flush=True)
    print(f"bands: {bands} -> {n_bands_pass}/4 | verdict={verdict} | n_traces={len(traces)}", flush=True)
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
    # planted rules: node labels include 'rock' and 'stone' distinct; question paraphrase must bridge.
    rows = [
        {"relation": "CAUSE", "arg0": "weathering", "arg1": "erosion"},
        {"relation": "SOURCEOF", "arg0": "erosion", "arg1": "sediment"},
        {"relation": "USEDFOR", "arg0": "sediment", "arg1": "sedimentary rock"},
        {"relation": "CAUSE", "arg0": "volcano", "arg1": "lava"},
    ]
    exercised = set()

    # GLOVE mode (baseline): symbolic bridge OFF.
    rg = DerivationReasoner(base_encoder=base, pol_lexicon=pol, wn=wn, tau_unify=0.99, tau_sim=0.5,
                            depth=3, rows=rows, link_mode="glove", verbose=False)
    assert rg.link_mode == "glove"
    # 'rocks' (plural) does NOT link under strict GloVe FakeBase (encoder is char-hash; cos~0) -> selectivity floor
    exercised.add("glove")

    # LEMMA mode: 'rocks' -> lemma 'rock' -> node whose label 'sedimentary rock' contains token 'rock'.
    rl = DerivationReasoner(base_encoder=base, pol_lexicon=pol, wn=wn, tau_unify=0.99, tau_sim=0.5,
                            depth=3, rows=rows, link_mode="lemma", verbose=False)
    rock_nid = next(i for i, lab in enumerate(rl.g["node_label"]) if "rock" in lab)
    assert rock_nid in rl._symbolic_nodes("rocks"), "lemma bridge 'rocks'->sedimentary-rock MUST link"
    assert rock_nid not in rg.nodes_for("many rocks"), "glove mode must NOT symbolic-link (arms differ)"
    assert rock_nid in rl.nodes_for("many rocks"), "lemma mode nodes_for MUST include symbolic link"
    assert rl._symbolic_nodes("zzqq") == set(), "unrelated token MUST NOT link (selectivity real)"
    exercised.add("lemma")

    # LEMMA_SYN mode: WordNet synonym bridge -- 'stone' is a same-synset synonym of 'rock' -> links the rock node.
    rs = DerivationReasoner(base_encoder=base, pol_lexicon=pol, wn=wn, tau_unify=0.99, tau_sim=0.5,
                            depth=3, rows=rows, link_mode="lemma_syn", verbose=False)
    syn = rs._wn_synonyms("rock")
    assert "stone" in syn, f"WordNet synonym expansion must yield stone for rock; got {sorted(syn)[:8]}"
    assert rock_nid in rs._symbolic_nodes("stone"), "synonym bridge 'stone'->rock node MUST link"
    assert rock_nid not in rl._symbolic_nodes("stone"), "lemma mode (no syn) must NOT bridge stone->rock"
    exercised.add("lemma_syn")

    # analysis + evaluate harness end-to-end on 2 planted Qs (real per-mode analysis path).
    q1 = {"qid": "T1", "stem": "what does weathering of many rocks eventually",
          "choices": ["sediment forms sedimentary rock", "lava cools", "metal wire", "glass sheet"],
          "correct_index": 0}
    q2 = {"qid": "T2", "stem": "unrelated tokens zzz qqq",
          "choices": ["metal wire", "glass sheet", "plastic tube", "stone block"], "correct_index": 0}
    rs.link_mode = "lemma_syn"
    rep = evaluate(rs, [q1, q2], output_dir=os.path.join(_REPO, "data", "_elink_selftest_scratch"))
    ana = _analyze(rep)
    assert "distractor_derive_rate" in ana and "coverage_fraction" in ana, "analysis must return headline metrics"
    assert 0.0 <= ana["distractor_derive_rate"] <= 1.0, "distractor rate must be a fraction"
    exercised.add("analyze")

    # rule loader binds the real file (real_code_path for the FULL entrypoint).
    real_rows = _load_rules(RULES_PATH)
    assert len(real_rows) > 100 and all(("relation" in r) for r in real_rows), "real rules file must load"
    exercised.add("load_rules")

    need = {"glove", "lemma", "lemma_syn", "analyze", "load_rules"}
    missing = need - exercised
    assert not missing, f"real_code_path: unexercised entrypoints {missing}"
    print(f"[self-test] real_code_path exercised={sorted(exercised)}", flush=True)
    print("[self-test] ALL PASS", flush=True)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--mode", choices=["smoke", "full"], default="full")
    ap.add_argument("--n", type=int, default=40, help="smoke sample size (full ignores this)")
    ap.add_argument("--seed", type=int, default=SEED)
    ap.add_argument("--out", type=str, default=os.path.join(_REPO, "data", "exp_" + ANCHOR_NAME))
    args = ap.parse_args()

    if args.self_test:
        _self_test()
        return

    n_sample = args.n if args.mode == "smoke" else 0   # full = all 1172 test questions
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
