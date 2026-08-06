"""exp_consequence_learning_loop_signal_a_primary_v1 -- decisive re-score of the consequence-learning
loop with a SIGNAL-A-PRIMARY teacher.

Pre-reg: preregs/2026-08-06_consequence_learning_loop_signal_a_primary_v1.md
Parent:  experiments/exp_consequence_learning_loop_oov_outcome_verb_valence_v1.py (commit a892153ea,
         HARD_FAIL INSUFFICIENT_YIELD -- the dual-signal AND-gate grounded 0 words)
Engine:  hdlab/consequence_learning_loop.py (UNCHANGED -- already threads signal_mode="signal_a_only")

WHAT: the parent's AND-gate (Signal A congruence AND goal-blind Signal B flat lexicon) co-fired on only
3 windows -> nothing grounded. Its own ablation showed Signal-A-only grounds 11 words at 0 noise but
NEVER SCORED them on the eval. This cell DROPS the AND-gate, makes Signal A (congruence_decision's own
MET/UNMET) the PRIMARY teacher, and SCORES the grounded overlay on the 36-item OOV eval: do the grounded
verbs type MET/UNMET CORRECTLY (vs the 0.1667 empty-overlay floor + 0.6389 majority floor)? Per-verb:
which words grounded, learned polarity, whether it matches the eval gold (THE decisive number). Full
non-circularity battery (eval-passage exclusion, label-scramble, OOV-integrity, random-credit,
light-verb-neutral, noise canary) + an AND-gate positive control that reproduces the parent's starvation.

This is a RE-SCORE of an existing validated engine + the parent's validated corpus/scoring helpers
(imported verbatim) -- NOT a new build. The engine module gets ZERO edits.

# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - final_metrics_atomicity: tmp_replace (os.replace)
# - deterministic_seeding: fixed integer seeds only (np.random.default_rng(fixed)); no hash()-seeding
# - start_marker + crash_diagnostic + resumable per-unit (tools/exp_checkpoint)
# - progress_logging: print(..., flush=True)
# - discriminator-fires gate at smoke: >=1 teacher window AND >=1 credit exposure
# - all numbers MEASURED@ this cell's metrics.json (no HYPOTHESIZED numbers reported as data)
"""
from __future__ import annotations

import argparse
import json
import os
import platform
import sys
import time
import traceback
from datetime import datetime, timezone

import numpy as np

# repo root on path
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from hdlab.goal_typing import congruence_with_lexicon_fallback  # noqa: E402
from hdlab import verb_lexical_similarity as _vls  # noqa: E402
from hdlab.consequence_learning_loop import (  # noqa: E402
    learn_corpus, consolidate,
    W_DEFAULT, MIN_CONFIRM, NEUTRAL_BAND, N_PASSES_DEFAULT,
)
from hdlab.consequence_learning_loop import self_test as _engine_self_test  # noqa: E402
from hdlab.verb_lexical_similarity import in_lexicon  # noqa: E402

# REUSE the parent cell's validated corpus/scoring/canary/scramble helpers verbatim (wire-don't-island).
from experiments.exp_consequence_learning_loop_oov_outcome_verb_valence_v1 import (  # noqa: E402
    _load_eval, _read_corpus_blocks, _build_windows, _exclusion_integrity,
    _score_with_overlay, _learnable_subset, _canary_analysis, _scramble_control,
    NOVELS, SMOKE_NOVELS, N_SCRAMBLE_SEEDS, INCREMENT_1B_REF, MAJORITY_FLOOR_REF,
)
from tools.exp_checkpoint import unit_key, completed_units, record_unit, load_units  # noqa: E402

ANCHOR_NAME = "consequence_learning_loop_signal_a_primary_v1"
OUTPUT_DIR_FULL = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}")

W = W_DEFAULT
N_PASSES = N_PASSES_DEFAULT
SIGNAL_MODE = "signal_a_only"   # <-- THE single change vs the parent's "and_gate"


# ------------------------------------------------------------------ start-marker / crash diagnostics
def _write_start_marker(output_dir, run_mode, expected_n_units):
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": run_mode,
              "expected_n_units": expected_n_units, "host": platform.node()}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    final = os.path.join(output_dir, "_start_marker.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, final)


def _write_crash_metrics(output_dir, exc):
    diag = {"verdict": "CELL_CRASHED", "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
            "summary": f"CELL_CRASHED: {type(exc).__name__}", "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000], "ts_iso": datetime.now(timezone.utc).isoformat(),
            "pid": os.getpid(), "anchor_name": ANCHOR_NAME}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, final)


def _atomic_write_metrics(output_dir, metrics):
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, final)


# ------------------------------------------------------------------ new: per-verb grounded correctness
def _per_verb_grounded_correctness(oov_rows, registered, master_counter):
    """THE decisive table. For each grounded eval-OOV lemma (a lemma that consolidated POS/NEG AND is
    the outcome_verb_lemma of >=1 eval item), report the learned polarity, the vote counts (pos/neg)
    that produced it, the eval gold(s), and per-item correctness under the live overlay. Returns
    (table, polarity_match_rate, n_grounded_eval_verbs). polarity_match_rate = fraction of grounded
    eval-verbs whose learned polarity matches the majority eval gold for that verb (chance=0.5)."""
    eval_lemmas = {}
    for r in oov_rows:
        eval_lemmas.setdefault(r["outcome_verb_lemma"], []).append(r)
    # score every learnable item live under the overlay
    _vls.clear_acquired_outcome()
    for lemma, pol in registered.items():
        _vls.register_acquired_outcome(lemma, pol)
    table = []
    n_match = 0
    n_verbs = 0
    for lemma in sorted(l for l in registered if l in eval_lemmas):
        learned = registered[lemma]  # "POS" | "NEG"
        learned_polarity = "MET" if learned == "POS" else "UNMET"
        items = eval_lemmas[lemma]
        golds = ["MET" if r["gold_outcome_polarity"] == "met" else "UNMET" for r in items]
        # majority gold for this verb (ties -> report as-is; correctness is per-item below)
        maj_gold = max(set(golds), key=golds.count)
        per_item = []
        item_correct = 0
        for r in items:
            gold = "MET" if r["gold_outcome_polarity"] == "met" else "UNMET"
            pred, detail = congruence_with_lexicon_fallback(r["text"])
            ok = (pred == gold)
            item_correct += ok
            per_item.append({"id": r["id"], "gold": gold, "pred": pred,
                             "reason": detail.get("reason"), "correct": bool(ok)})
        c = master_counter.get(lemma, {"POS": 0, "NEG": 0})
        polarity_matches_gold = (learned_polarity == maj_gold)
        n_verbs += 1
        n_match += int(polarity_matches_gold)
        table.append({
            "lemma": lemma,
            "learned_polarity": learned_polarity,
            "vote_pos": c.get("POS", 0), "vote_neg": c.get("NEG", 0),
            "majority_eval_gold": maj_gold,
            "polarity_matches_gold": polarity_matches_gold,
            "n_eval_items": len(items),
            "items_typed_correct": item_correct,
            "per_item": per_item,
        })
    _vls.clear_acquired_outcome()
    match_rate = (round(n_match / n_verbs, 4) if n_verbs else None)
    return table, match_rate, n_verbs


# ------------------------------------------------------------------ new: OOV-integrity control
def _oov_integrity(registered):
    """Non-circularity control (task-mandated): every grounded lemma must be genuinely OOV of the SEED
    outcome lexicon (Tier-1/2) at learn-time -- so its polarity came from CONSEQUENCE, not from a
    re-derived seed lexicon / not from its own surface form. Check with the acquired overlay CLEARED
    (in_lexicon then consults only the seed). Any grounded lemma that is seed-known = a leak."""
    _vls.clear_acquired_outcome()
    leaks = [lemma for lemma in registered if in_lexicon(lemma, "outcome")]
    return {"n_grounded": len(registered), "oov_integrity_seed_leaks": len(leaks),
            "seed_leak_lemmas": sorted(leaks),
            "all_grounded_genuinely_oov": len(leaks) == 0}


# ------------------------------------------------------------------ new: scramble on the learnable subset
def _scramble_learnable(master_records, oov_rows, real_registered, n_seeds=N_SCRAMBLE_SEEDS):
    """Label-scramble control scored on the SAME learnable-subset items the REAL run grounded (isolates
    whether the POLARITY, not the coverage, came from the consequence label). Permute teacher_verdict
    across recorded exposures (fixed seeds 2000+s), re-consolidate, re-register, and score ONLY the eval
    items whose outcome verb the REAL run consolidated. Must collapse toward chance."""
    eval_lemmas = {r["outcome_verb_lemma"] for r in oov_rows}
    real_eval_lemmas = {l for l in real_registered if l in eval_lemmas}
    learnable_items = [r for r in oov_rows if r["outcome_verb_lemma"] in real_eval_lemmas]
    verdicts = [rec["teacher_verdict"] for rec in master_records]
    accs = []
    for s in range(n_seeds):
        rng = np.random.default_rng(2000 + s)
        perm = rng.permutation(len(verdicts)) if verdicts else np.array([], dtype=int)
        counter = {}
        for k, rec in enumerate(master_records):
            v = verdicts[int(perm[k])]
            pole = "POS" if v == "MET" else "NEG"
            counter.setdefault(rec["lemma"], {"POS": 0, "NEG": 0})[pole] += 1
        grounded = consolidate(counter)
        registered = {lem: v for lem, v in grounded.items() if v in ("POS", "NEG")}
        _vls.clear_acquired_outcome()
        for lemma, pol in registered.items():
            _vls.register_acquired_outcome(lemma, pol)
        if learnable_items:
            correct = 0
            for r in learnable_items:
                gold = "MET" if r["gold_outcome_polarity"] == "met" else "UNMET"
                pred, _d = congruence_with_lexicon_fallback(r["text"])
                correct += (pred == gold)
            accs.append(correct / len(learnable_items))
        _vls.clear_acquired_outcome()
    return {"scrambled_learnable_subset_accuracy":
            (round(float(np.mean(accs)), 4) if accs else None),
            "scrambled_learnable_per_seed": [round(a, 4) for a in accs],
            "scramble_learnable_subset_size": len(learnable_items)}


# ------------------------------------------------------------------ core run (resumable per-unit)
def _run_all(output_dir, run_mode):
    novels = SMOKE_NOVELS if run_mode == "smoke" else NOVELS
    all_rows, oov_rows = _load_eval()
    majority_floor = round(sum(1 for r in oov_rows if r["gold_outcome_polarity"] == "met")
                           / len(oov_rows), 4)

    # ---- UNIT 1: corpus scan (cached) ---------------------------------------------------------
    if unit_key("corpus", run_mode) not in completed_units(output_dir):
        print(f"[progress] reading corpora + building windows (run_mode={run_mode})", flush=True)
        blocks, corpus_stats, _excl = _read_corpus_blocks(all_rows, novels)
        windows, win_stats = _build_windows(blocks, all_rows)
        integ = _exclusion_integrity(windows, all_rows)
        record_unit(output_dir, unit_key("corpus", run_mode),
                    {"windows": windows, "corpus_stats": corpus_stats, "win_stats": win_stats,
                     "exclusion_integrity": integ})
        print(f"[progress] corpus: sents={win_stats['total_sents']} goal_fire={win_stats['goal_fire']} "
              f"windows={win_stats['n_windows']} exclusion_clean={integ['clean']}", flush=True)
    corpus_u = load_units(output_dir)[unit_key("corpus", run_mode)]
    windows = [tuple(w) for w in corpus_u["windows"]]

    # ---- UNIT 2: main learn (SIGNAL-A-PRIMARY, referent-linked) + full scoring -----------------
    if unit_key("main", run_mode) not in completed_units(output_dir):
        print(f"[progress] main learn (signal_mode={SIGNAL_MODE}, referent-linked, multi-pass)", flush=True)
        rep = learn_corpus(windows, n_passes=N_PASSES, signal_mode=SIGNAL_MODE,
                           credit_mode="referent_linked", register=True)
        registered = rep["registered"]
        acc, correct, met_c, unmet_c, n_met, n_unmet, details = _score_with_overlay(oov_rows, registered)
        learnable = _learnable_subset(oov_rows, registered)
        canary = _canary_analysis(rep["master_counter"], rep["master_grounded"])
        per_verb, pol_match_rate, n_grounded_eval = _per_verb_grounded_correctness(
            oov_rows, registered, rep["master_counter"])
        oov_integ = _oov_integrity(registered)
        record_unit(output_dir, unit_key("main", run_mode), {
            "registered": registered,
            "master_grounded": rep["master_grounded"],
            "master_records": rep["master_records"],
            "master_counter": rep["master_counter"],
            "pass_reports": rep["pass_reports"],
            "primary_accuracy": round(acc, 4), "primary_correct": correct,
            "met_recall_correct": met_c, "met_total": n_met,
            "unmet_recall_correct": unmet_c, "unmet_total": n_unmet,
            "score_details": details, "learnable": learnable, "canary": canary,
            "per_verb_grounded": per_verb, "grounded_verb_polarity_match_rate": pol_match_rate,
            "n_grounded_eval_verbs": n_grounded_eval, "oov_integrity": oov_integ,
        })
        print(f"[progress] main: primary_acc={acc:.4f} n_registered={len(registered)} "
              f"n_learnable={learnable['n_learnable']} ls_acc={learnable['learnable_subset_accuracy']} "
              f"pol_match={pol_match_rate} lv_neutral={canary['light_verb_canary_neutral_rate']} "
              f"noise_consol={canary['noise_canary_consolidated_count']} "
              f"oov_leaks={oov_integ['oov_integrity_seed_leaks']}", flush=True)
    main_u = load_units(output_dir)[unit_key("main", run_mode)]

    # ---- UNIT 3: baseline (empty overlay) -----------------------------------------------------
    if unit_key("baseline", run_mode) not in completed_units(output_dir):
        _vls.clear_acquired_outcome()
        b = _score_with_overlay(oov_rows, {})
        record_unit(output_dir, unit_key("baseline", run_mode),
                    {"fallthrough_baseline_accuracy": round(b[0], 4), "fallthrough_correct": b[1]})
    base_u = load_units(output_dir)[unit_key("baseline", run_mode)]

    # ---- UNIT 4: scramble control (5 seeds; primary + learnable-subset) ------------------------
    if unit_key("scramble", run_mode) not in completed_units(output_dir):
        print("[progress] scramble control (5 seeds)", flush=True)
        scr_primary = _scramble_control(main_u["master_records"], oov_rows)
        scr_learn = _scramble_learnable(main_u["master_records"], oov_rows, main_u["registered"])
        rec = dict(scr_primary)
        rec.update(scr_learn)
        record_unit(output_dir, unit_key("scramble", run_mode), rec)
    scr_u = load_units(output_dir)[unit_key("scramble", run_mode)]

    # ---- UNIT 5: random-credit ablation (signal-A-primary) ------------------------------------
    if unit_key("random_credit", run_mode) not in completed_units(output_dir):
        print("[progress] random-credit ablation", flush=True)
        rc_rng = np.random.default_rng(3000)

        def _rc_choice(lst):
            return lst[int(rc_rng.integers(len(lst)))]

        rc_rep = learn_corpus(windows, n_passes=N_PASSES, signal_mode=SIGNAL_MODE,
                              credit_mode="random", rng_choice=_rc_choice, register=True)
        rc_reg = rc_rep["registered"]
        rc_learn = _learnable_subset(oov_rows, rc_reg)
        rc_acc = _score_with_overlay(oov_rows, rc_reg)[0]
        _vls.clear_acquired_outcome()
        record_unit(output_dir, unit_key("random_credit", run_mode), {
            "random_credit_primary_accuracy": round(rc_acc, 4),
            "random_credit_n_registered": len(rc_reg),
            "random_credit_learnable_subset_accuracy": rc_learn["learnable_subset_accuracy"],
            "random_credit_n_learnable": rc_learn["n_learnable"],
        })
    rc_u = load_units(output_dir)[unit_key("random_credit", run_mode)]

    # ---- UNIT 6: AND-gate positive control (reproduce parent starvation at test regime) --------
    if unit_key("andgate_reference", run_mode) not in completed_units(output_dir):
        print("[progress] andgate_reference positive control (reproduce parent starvation)", flush=True)
        ag_rep = learn_corpus(windows, n_passes=N_PASSES, signal_mode="and_gate",
                              credit_mode="referent_linked", register=True)
        ag_reg = ag_rep["registered"]
        ag_acc = _score_with_overlay(oov_rows, ag_reg)[0]
        _vls.clear_acquired_outcome()
        record_unit(output_dir, unit_key("andgate_reference", run_mode), {
            "andgate_n_registered": len(ag_reg),
            "andgate_primary_accuracy": round(ag_acc, 4),
            "andgate_registered": ag_reg,
        })
    ag_u = load_units(output_dir)[unit_key("andgate_reference", run_mode)]

    return _aggregate(run_mode, oov_rows, majority_floor, corpus_u, main_u, base_u, scr_u, rc_u, ag_u)


def _aggregate(run_mode, oov_rows, majority_floor, corpus_u, main_u, base_u, scr_u, rc_u, ag_u):
    primary = main_u["primary_accuracy"]
    learnable = main_u["learnable"]
    canary = main_u["canary"]
    n_learnable = learnable["n_learnable"]
    ls_acc = learnable["learnable_subset_accuracy"]
    lv_rate = canary["light_verb_canary_neutral_rate"]
    noise_consol = canary["noise_canary_consolidated_count"]
    pol_match = main_u["grounded_verb_polarity_match_rate"]
    oov_integ = main_u["oov_integrity"]
    scr_ls = scr_u["scrambled_learnable_subset_accuracy"]
    scr_primary = scr_u["scrambled_primary_accuracy"]
    rc_ls = rc_u["random_credit_learnable_subset_accuracy"]
    rc_n_learn = rc_u["random_credit_n_learnable"]
    integ = corpus_u["exclusion_integrity"]

    agg = {
        "anchor_name": ANCHOR_NAME, "run_mode": run_mode,
        "signal_mode": SIGNAL_MODE,
        "config": {"W": W, "MIN_CONFIRM": MIN_CONFIRM, "NEUTRAL_BAND": NEUTRAL_BAND,
                   "N_PASSES": N_PASSES, "n_scramble_seeds": N_SCRAMBLE_SEEDS,
                   "n_oov_items": len(oov_rows)},
        "corpus_stats": corpus_u["corpus_stats"], "win_stats": corpus_u["win_stats"],
        "exclusion_integrity": integ,
        "majority_floor": majority_floor, "empty_overlay_floor": base_u["fallthrough_baseline_accuracy"],
        "increment_1b_ref": INCREMENT_1B_REF,
        "primary_accuracy": primary,
        "met_recall": f"{main_u['met_recall_correct']}/{main_u['met_total']}",
        "unmet_recall": f"{main_u['unmet_recall_correct']}/{main_u['unmet_total']}",
        "n_registered": len(main_u["registered"]), "registered": main_u["registered"],
        "master_grounded": main_u["master_grounded"],
        "learnable_subset": learnable,
        "grounded_verb_polarity_match_rate": pol_match,
        "n_grounded_eval_verbs": main_u["n_grounded_eval_verbs"],
        "per_verb_grounded": main_u["per_verb_grounded"],
        "oov_integrity": oov_integ,
        "light_verb_canary": {k: canary[k] for k in (
            "light_verb_canary_neutral_rate", "light_verb_n_reached", "light_verb_n_neutral",
            "light_verb_n_polar_locked", "light_verb_reached_minconfirm")},
        "noise_canary": {"consolidated_count": noise_consol,
                         "consolidated_words": canary["noise_canary_consolidated_words"]},
        "bootstrap_curve": main_u["pass_reports"],
        "scramble": scr_u,
        "random_credit": rc_u,
        "andgate_reference": {"n_registered": ag_u["andgate_n_registered"],
                              "primary_accuracy": ag_u["andgate_primary_accuracy"]},
        "light_verb_detail": canary["light_verb_detail"],
        "noise_detail": canary["noise_detail"],
    }

    # ---- verdict (per pre-reg bands; per-gate, never aggregate) --------------------------------
    # HARD-PASS gates
    hp1 = (ls_acc is not None and ls_acc >= 0.70) and (n_learnable >= 4)
    hp2 = (primary >= 0.25)
    scr_collapse = (scr_ls is not None and (ls_acc is not None) and
                    (ls_acc - scr_ls) >= 0.15 and scr_ls <= 0.60)
    # random-credit: gap load-bearing OR rc grounded too few eval-lemmas to compare (honest note)
    rc_gap = (ls_acc is not None and rc_ls is not None and (ls_acc - rc_ls) >= 0.15)
    rc_too_few = (rc_n_learn < 3)
    rc_ok = rc_gap or rc_too_few
    oov_ok = (oov_integ["oov_integrity_seed_leaks"] == 0)
    hp3 = scr_collapse and rc_ok and oov_ok and integ["clean"] and (noise_consol == 0)

    # HARD-FAIL gates
    hf_grounds_wrong = (ls_acc is not None and ls_acc <= 0.55)
    hf_yield = (n_learnable < 3)
    hf_scramble = (scr_ls is not None and ls_acc is not None and abs(ls_acc - scr_ls) <= 0.08)
    hf_random = (ls_acc is not None and rc_ls is not None and abs(ls_acc - rc_ls) <= 0.08 and rc_n_learn >= 3)
    hf_oov_leak = (oov_integ["oov_integrity_seed_leaks"] >= 1)
    hf_noise = (noise_consol >= 2)
    hf_lightverb = (lv_rate is not None and lv_rate < 0.30)

    gate_detail = {
        "HP1_learnable_subset": {"ls_acc>=0.70": hp1, "ls_acc": ls_acc, "n_learnable": n_learnable},
        "HP2_primary>=0.25": {"pass": hp2, "primary": primary, "empty_floor": base_u["fallthrough_baseline_accuracy"]},
        "HP3_noncircularity": {"scramble_collapse(gap>=0.15 & scr<=0.60)": scr_collapse,
                               "scrambled_ls_acc": scr_ls, "random_credit_ok": rc_ok,
                               "rc_ls_acc": rc_ls, "rc_n_learnable": rc_n_learn,
                               "oov_integrity_ok": oov_ok, "exclusion_clean": integ["clean"],
                               "noise==0": (noise_consol == 0)},
        "HF_grounds_wrong(ls<=0.55)": hf_grounds_wrong,
        "HF_insufficient_yield(<3)": hf_yield,
        "HF_scramble_within_0.08": hf_scramble,
        "HF_random_within_0.08(&rc>=3)": hf_random,
        "HF_oov_seed_leak": hf_oov_leak,
        "HF_noise>=2": hf_noise,
        "HF_lightverb<0.30": hf_lightverb,
    }

    hard_pass = all([hp1, hp2, hp3])
    hard_fail = any([hf_grounds_wrong, hf_yield, hf_scramble, hf_random, hf_oov_leak, hf_noise, hf_lightverb])

    if hard_fail:
        verdict = "HARD_FAIL"
    elif hard_pass:
        verdict = "HARD_PASS"
    else:
        verdict = "MIDDLE_BAND"

    agg["gate_detail"] = gate_detail
    agg["verdict"] = verdict
    agg["verdict_msg"] = (
        f"{verdict}: primary={primary:.4f} (empty_floor={base_u['fallthrough_baseline_accuracy']}, "
        f"maj={majority_floor}) | ls_acc={ls_acc}(n_learnable={n_learnable}) | "
        f"pol_match={pol_match}({main_u['n_grounded_eval_verbs']} verbs) | "
        f"scr_ls={scr_ls} scr_primary={scr_primary} | rc_ls={rc_ls}(n={rc_n_learn}) | "
        f"lv_neutral={lv_rate} | noise={noise_consol} | oov_leaks={oov_integ['oov_integrity_seed_leaks']} | "
        f"andgate_ref_n_reg={ag_u['andgate_n_registered']} | excl_clean={integ['clean']}")
    agg["summary"] = agg["verdict_msg"][:300]
    return agg


# ------------------------------------------------------------------ discriminator-fires (smoke gate)
def _discriminator_fires(agg):
    passes = agg["bootstrap_curve"]
    max_teacher = max((p["n_windows_with_teacher"] for p in passes), default=0)
    max_credit = max((p["n_new_exposure_pairs"] for p in passes), default=0)
    return {"max_windows_with_teacher": max_teacher, "max_exposure_pairs": max_credit,
            "fires": (max_teacher > 0 and max_credit > 0)}


# ------------------------------------------------------------------ driver
def run(run_mode):
    t0 = time.perf_counter()
    output_dir = OUTPUT_DIR_FULL if run_mode == "full" else f"{OUTPUT_DIR_FULL}_{run_mode}"
    expected_n_units = 6  # corpus, main, baseline, scramble, random_credit, andgate_reference
    _write_start_marker(output_dir, run_mode, expected_n_units)
    agg = _run_all(output_dir, run_mode)
    agg["elapsed_s"] = round(time.perf_counter() - t0, 2)
    agg["discriminator_fires"] = _discriminator_fires(agg)
    _atomic_write_metrics(output_dir, agg)
    print(json.dumps({"verdict": agg["verdict"], "verdict_msg": agg["verdict_msg"],
                      "discriminator_fires": agg["discriminator_fires"],
                      "elapsed_s": agg["elapsed_s"]}, indent=2), flush=True)
    return agg


def self_test():
    """Construct the REAL engine at tiny scale + exercise the parent's real corpus reader on the real
    little_women file (F.1 real_code_path). Asserts engine determinism + that the reused helpers fire on
    a real slice. No full corpus scan."""
    eng = _engine_self_test()
    assert eng["determinism_ok"], "engine determinism failed"
    all_rows, oov_rows = _load_eval()
    assert len(oov_rows) == 36, f"expected 36 OOV items, got {len(oov_rows)}"
    n_met = sum(1 for r in oov_rows if r["gold_outcome_polarity"] == "met")
    assert n_met == 23, f"expected 23 met, got {n_met}"
    # real corpus reader on real little_women file (reused parent helper -> real code path)
    blocks, stats, _excl = _read_corpus_blocks(all_rows, SMOKE_NOVELS)
    assert stats["little_women.clean.txt"]["excluded_lines"] > 0, "exclusion mask empty on real file"
    windows, win_stats = _build_windows(blocks[:20], all_rows)
    # signal-A-primary learn on a tiny real slice must run + the new scorers must be callable
    rep = learn_corpus([tuple(w) for w in windows], n_passes=1, signal_mode=SIGNAL_MODE,
                       credit_mode="referent_linked", register=False)
    _ = _oov_integrity(rep["registered"])
    _ = _per_verb_grounded_correctness(oov_rows, rep["registered"], rep["master_counter"])
    _vls.clear_acquired_outcome()
    return {"engine": eng, "n_oov": len(oov_rows), "n_met": n_met,
            "excluded_lines_lw": stats["little_women.clean.txt"]["excluded_lines"],
            "tiny_windows": win_stats["n_windows"], "signal_mode": SIGNAL_MODE}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-mode", choices=["full", "smoke"], default="full")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        res = self_test()
        print(json.dumps(res, indent=2))
        print("SELF_TEST_PASS")
        return
    run(args.run_mode)


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # NOT BaseException
        for cand in (OUTPUT_DIR_FULL, f"{OUTPUT_DIR_FULL}_smoke"):
            if os.path.exists(cand) or cand == OUTPUT_DIR_FULL:
                _write_crash_metrics(cand, e)
                break
        raise
