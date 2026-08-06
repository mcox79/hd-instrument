"""exp_consequence_learning_loop_oov_outcome_verb_valence_v1 -- the continuous consequence-learning
loop for OOV outcome-verb result-valence.

Pre-reg: preregs/2026-08-06_consequence_learning_loop_oov_outcome_verb_valence_v1.md
Spec:    notes/research_consequence_learning_loop_oov_outcome_verb_valence_2026-08-06.md
Engine:  hdlab/consequence_learning_loop.py (credit_window / consolidate / run_pass / learn_corpus)

WHAT: reads the 4 real novels (eval-passage-EXCLUDED), learns OOV outcome-verb valence from each
episode's OWN computed MET/UNMET consequence (congruence_decision teacher, NOT reward theta), grounds
cross-situationally, then scores the 36-item OOV subset of goal_bearing_modern_eval_v1.jsonl via the
LIVE production congruence_with_lexicon_fallback. Full non-circularity battery (eval-passage exclusion
+ substring guard, label-scramble x5, random-credit ablation, single-signal ablations, noise canary,
light-verb-neutral canary).

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
import re
import sys
import time
import traceback
from datetime import datetime, timezone

import numpy as np

# repo root on path
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from hdlab.goal_typing import (  # noqa: E402
    find_desired_state, congruence_with_lexicon_fallback, _sentences,
)
from hdlab import verb_lexical_similarity as _vls  # noqa: E402
from hdlab.consequence_learning_loop import (  # noqa: E402
    learn_corpus, run_pass, consolidate, teacher_verdict, credit_window,
    W_DEFAULT, MIN_CONFIRM, NEUTRAL_BAND, N_PASSES_DEFAULT,
)
from hdlab.consequence_learning_loop import self_test as _engine_self_test  # noqa: E402
from tools.exp_checkpoint import unit_key, completed_units, record_unit, load_units  # noqa: E402

ANCHOR_NAME = "consequence_learning_loop_oov_outcome_verb_valence_v1"
OUTPUT_DIR_FULL = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}")
EVAL_REL = os.path.join("experiments", "data", "goal_bearing_modern_eval_v1.jsonl")

# corpus files (the 4 novels the eval draws 28/36 OOV items from -> mandatory eval-passage exclusion)
NOVELS = {
    "little_women.clean.txt": "data/corpora/little_women/cleaned/little_women.clean.txt",
    "anne_of_green_gables.clean.txt": "data/corpora/anne_of_green_gables/cleaned/anne_of_green_gables.clean.txt",
    "tom_sawyer.clean.txt": "data/corpora/tom_sawyer/cleaned/tom_sawyer.clean.txt",
    "wizard_of_oz.clean.txt": "data/corpora/wizard_of_oz/cleaned/wizard_of_oz.clean.txt",
}
SMOKE_NOVELS = {"little_women.clean.txt": NOVELS["little_women.clean.txt"]}

EXCLUDE_MARGIN = 50       # +/- lines around each cited eval passage (citations are ~-approximate)
N_SCRAMBLE_SEEDS = 5
W = W_DEFAULT
N_PASSES = N_PASSES_DEFAULT

# LIGHT_VERB_CANARY (26 lemmas; pre-reg config, fixed before running). The neutral-convergence payoff.
LIGHT_VERB_CANARY = ["be", "have", "do", "say", "try", "look", "feel", "want", "think", "make",
                     "come", "go", "find", "ask", "seem", "begin", "mean", "know", "see", "tell",
                     "get", "put", "take", "give", "carry", "buy"]
# NOISE_CANARY (8 manner-neutral verbs; none should confidently consolidate POS/NEG).
NOISE_CANARY = ["walk", "sit", "speak", "stand", "sigh", "glance", "nod", "pause"]

# reference baselines (MEASURED elsewhere, re-derived here at runtime -- never hard-coded as truth):
MAJORITY_FLOOR_REF = 0.6389    # 23/36; re-computed from the live eval file below
INCREMENT_1B_REF = 0.4444      # data/exp_grounded_word_acquisition_increment1b_v1/metrics.json


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


# ------------------------------------------------------------------ eval + corpus
def _load_eval():
    rows = []
    with open(os.path.join(REPO_ROOT, EVAL_REL), "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    oov = [r for r in rows if r.get("outcome_in_lexicon") is False]
    return rows, oov


def _norm(s):
    return " ".join(re.findall(r"[a-z']+", s.lower()))


def _parse_citation(cite):
    """'little_women.clean.txt:~1945-1981' -> ('little_women.clean.txt', 1945, 1981)."""
    fname, _, rng = cite.partition(":")
    rng = rng.strip().lstrip("~")
    fname = fname.strip()
    if "-" in rng:
        a, b = rng.split("-", 1)
        try:
            return fname, int(a), int(b)
        except ValueError:
            return fname, None, None
    if rng.isdigit():
        return fname, int(rng), int(rng)
    return fname, None, None


def _read_corpus_blocks(all_rows, novels, margin=EXCLUDE_MARGIN):
    """Read each novel's clean.txt, DROP every line inside an eval-passage exclusion range (+/- margin),
    return contiguous non-excluded text blocks (so no window sentence ever spans an excluded gap).
    Fail loud if any novel's exclusion mask is empty (a line_citation parse that came up empty must not
    silently train on contaminated passages)."""
    excl = {fname: set() for fname in novels}
    for r in all_rows:
        fname, a, b = _parse_citation(r["line_citation"])
        if fname in novels and a is not None:
            for ln in range(max(1, a - margin), b + margin + 1):
                excl[fname].add(ln)
    blocks = []
    stats = {}
    for fname, rel in novels.items():
        with open(os.path.join(REPO_ROOT, rel), "r", encoding="utf-8") as f:
            lines = f.readlines()
        excluded = excl[fname]
        buf = []
        for i, line in enumerate(lines):
            ln = i + 1
            if ln in excluded:
                if buf:
                    blocks.append(" ".join(buf))
                    buf = []
                continue
            buf.append(line.rstrip("\n"))
        if buf:
            blocks.append(" ".join(buf))
        n_cit = sum(1 for r in all_rows
                    if _parse_citation(r["line_citation"])[0] == fname
                    and _parse_citation(r["line_citation"])[1] is not None)
        stats[fname] = {"total_lines": len(lines), "excluded_lines": len(excluded),
                        "n_eval_citations": n_cit}
        # exclusion-mask-non-empty gate (only for novels that HAVE eval citations)
        if n_cit > 0 and len(excluded) == 0:
            raise RuntimeError(f"EXCLUSION_MASK_EMPTY for {fname} despite {n_cit} eval citations "
                               f"-- line_citation parse failed; refusing to train on contaminated corpus")
    return blocks, stats, excl


def _build_windows(blocks, all_rows, w=W):
    """Split blocks into sentences, build a (goal_sentence, window_text, desired_referent) per
    find_desired_state-firing sentence (window = goal sentence + next w sentences). Belt-and-suspenders
    substring guard: DROP any window whose goal sentence's normalized form appears verbatim in ANY eval
    passage (independent of the line-citation exclusion). Returns (windows, stats)."""
    eval_blob = " || ".join(_norm(r["text"]) for r in all_rows)
    windows = []
    total_sents = 0
    goal_fire = 0
    substring_dropped = 0
    for block in blocks:
        sents = _sentences(block)
        total_sents += len(sents)
        for i, s in enumerate(sents):
            desired = find_desired_state(s)
            if desired is None:
                continue
            goal_fire += 1
            ns = _norm(s)
            if len(ns) > 0 and ns in eval_blob:
                substring_dropped += 1
                continue
            win_sents = sents[i:i + 1 + w]
            windows.append((s, " ".join(win_sents), desired.get("referent")))
    return windows, {"total_sents": total_sents, "goal_fire": goal_fire,
                     "substring_dropped": substring_dropped, "n_windows": len(windows)}


def _exclusion_integrity(windows, all_rows):
    """Post-hoc re-check (pre-reg gate d): re-verify zero window goal-sentences appear verbatim in the
    eval passages. Independent of construction (belt-and-suspenders)."""
    eval_blob = " || ".join(_norm(r["text"]) for r in all_rows)
    violations = 0
    for (gs, _win, _ref) in windows:
        ns = _norm(gs)
        if len(ns) > 0 and ns in eval_blob:
            violations += 1
    return {"exclusion_integrity_violations": violations, "clean": violations == 0}


# ------------------------------------------------------------------ scoring
def _score(oov_rows):
    """Score all OOV items with the CURRENT overlay via the live production congruence_with_lexicon_
    fallback. Returns (accuracy, correct, met_correct, unmet_correct, details)."""
    correct = met_c = unmet_c = 0
    n_met = sum(1 for r in oov_rows if r["gold_outcome_polarity"] == "met")
    details = []
    for r in oov_rows:
        gold = "MET" if r["gold_outcome_polarity"] == "met" else "UNMET"
        pred, detail = congruence_with_lexicon_fallback(r["text"])
        ok = (pred == gold)
        correct += ok
        if gold == "MET":
            met_c += ok
        else:
            unmet_c += ok
        details.append({"id": r["id"], "outcome_lemma": r["outcome_verb_lemma"],
                        "gold": gold, "pred": pred, "reason": detail.get("reason"), "correct": bool(ok)})
    acc = correct / len(oov_rows)
    return acc, correct, met_c, unmet_c, n_met, len(oov_rows) - n_met, details


def _score_with_overlay(oov_rows, registered):
    _vls.clear_acquired_outcome()
    for lemma, pol in registered.items():
        _vls.register_acquired_outcome(lemma, pol)
    out = _score(oov_rows)
    _vls.clear_acquired_outcome()
    return out


# ------------------------------------------------------------------ canary analysis (from master tally)
def _canary_analysis(master_counter, master_grounded):
    """Light-verb-neutral rate + noise consolidated count, read from the single master tally."""
    lv_reached = []
    lv_neutral = 0
    lv_polar = 0
    lv_detail = {}
    for w in LIGHT_VERB_CANARY:
        c = master_counter.get(w)
        total = (c["POS"] + c["NEG"]) if c else 0
        verdict = master_grounded.get(w, "ABSENT")
        lv_detail[w] = {"pos": c["POS"] if c else 0, "neg": c["NEG"] if c else 0,
                        "total": total, "verdict": verdict}
        if total >= MIN_CONFIRM:
            lv_reached.append(w)
            if verdict == "GROUNDED_NEUTRAL":
                lv_neutral += 1
            elif verdict in ("POS", "NEG"):
                lv_polar += 1
    lv_rate = (lv_neutral / len(lv_reached)) if lv_reached else None

    noise_consolidated = []
    noise_detail = {}
    for w in NOISE_CANARY:
        c = master_counter.get(w)
        total = (c["POS"] + c["NEG"]) if c else 0
        verdict = master_grounded.get(w, "ABSENT")
        noise_detail[w] = {"pos": c["POS"] if c else 0, "neg": c["NEG"] if c else 0,
                           "total": total, "verdict": verdict}
        if verdict in ("POS", "NEG"):
            noise_consolidated.append(w)
    return {
        "light_verb_reached_minconfirm": sorted(lv_reached),
        "light_verb_n_reached": len(lv_reached),
        "light_verb_n_neutral": lv_neutral,
        "light_verb_n_polar_locked": lv_polar,
        "light_verb_canary_neutral_rate": (round(lv_rate, 4) if lv_rate is not None else None),
        "light_verb_detail": lv_detail,
        "noise_canary_consolidated_count": len(noise_consolidated),
        "noise_canary_consolidated_words": noise_consolidated,
        "noise_detail": noise_detail,
    }


# ------------------------------------------------------------------ controls
def _scramble_control(master_records, oov_rows, n_seeds=N_SCRAMBLE_SEEDS):
    """Permute teacher_verdict labels across the recorded exposures (fixed seeds), re-consolidate,
    re-register, re-score. Must collapse toward chance."""
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
        acc = _score_with_overlay(oov_rows, registered)[0]
        accs.append(acc)
    return {"scrambled_primary_accuracy": round(float(np.mean(accs)), 4) if accs else None,
            "scrambled_per_seed": [round(a, 4) for a in accs]}


def _learnable_subset(oov_rows, registered):
    """N_learnable = # unique eval-OOV lemmas that consolidated POS/NEG; learnable_subset_accuracy =
    accuracy on eval items whose outcome verb is in that set (scored with the overlay live)."""
    eval_lemmas = {r["outcome_verb_lemma"] for r in oov_rows}
    registered_eval = sorted(l for l in registered if l in eval_lemmas)
    learnable_items = [r for r in oov_rows if r["outcome_verb_lemma"] in registered]
    _vls.clear_acquired_outcome()
    for lemma, pol in registered.items():
        _vls.register_acquired_outcome(lemma, pol)
    correct = 0
    for r in learnable_items:
        gold = "MET" if r["gold_outcome_polarity"] == "met" else "UNMET"
        pred, _d = congruence_with_lexicon_fallback(r["text"])
        correct += (pred == gold)
    _vls.clear_acquired_outcome()
    acc = (correct / len(learnable_items)) if learnable_items else None
    return {"n_learnable": len(registered_eval), "registered_eval_lemmas": registered_eval,
            "learnable_subset_size": len(learnable_items),
            "learnable_subset_accuracy": (round(acc, 4) if acc is not None else None),
            "learnable_subset_correct": correct}


# ------------------------------------------------------------------ core run (resumable per-unit)
def _run_all(output_dir, run_mode):
    novels = SMOKE_NOVELS if run_mode == "smoke" else NOVELS
    all_rows, oov_rows = _load_eval()
    majority_floor = round(sum(1 for r in oov_rows if r["gold_outcome_polarity"] == "met")
                           / len(oov_rows), 4)

    # ---- UNIT 1: corpus scan (the expensive part; cached) -------------------------------------
    if unit_key("corpus", run_mode) not in completed_units(output_dir):
        print(f"[progress] reading corpora + building windows (run_mode={run_mode})", flush=True)
        blocks, corpus_stats, _excl = _read_corpus_blocks(all_rows, novels)
        windows, win_stats = _build_windows(blocks, all_rows)
        integ = _exclusion_integrity(windows, all_rows)
        record_unit(output_dir, unit_key("corpus", run_mode),
                    {"windows": windows, "corpus_stats": corpus_stats, "win_stats": win_stats,
                     "exclusion_integrity": integ})
        print(f"[progress] corpus: sents={win_stats['total_sents']} goal_fire={win_stats['goal_fire']} "
              f"windows={win_stats['n_windows']} substring_dropped={win_stats['substring_dropped']} "
              f"exclusion_clean={integ['clean']}", flush=True)
    corpus_u = load_units(output_dir)[unit_key("corpus", run_mode)]
    windows = [tuple(w) for w in corpus_u["windows"]]

    # ---- UNIT 2: main learn (and-gate, referent-linked) + score -------------------------------
    if unit_key("main", run_mode) not in completed_units(output_dir):
        print("[progress] main learn (and-gate, referent-linked, multi-pass)", flush=True)
        rep = learn_corpus(windows, n_passes=N_PASSES, signal_mode="and_gate",
                           credit_mode="referent_linked", register=True)
        registered = rep["registered"]
        acc, correct, met_c, unmet_c, n_met, n_unmet, details = _score_with_overlay(oov_rows, registered)
        learnable = _learnable_subset(oov_rows, registered)
        canary = _canary_analysis(rep["master_counter"], rep["master_grounded"])
        record_unit(output_dir, unit_key("main", run_mode), {
            "registered": registered,
            "master_grounded": rep["master_grounded"],
            "master_records": rep["master_records"],
            "pass_reports": rep["pass_reports"],
            "primary_accuracy": round(acc, 4), "primary_correct": correct,
            "met_recall_correct": met_c, "met_total": n_met,
            "unmet_recall_correct": unmet_c, "unmet_total": n_unmet,
            "score_details": details, "learnable": learnable, "canary": canary,
        })
        print(f"[progress] main: primary_acc={acc:.4f} n_registered={len(registered)} "
              f"n_learnable={learnable['n_learnable']} lv_neutral_rate={canary['light_verb_canary_neutral_rate']} "
              f"noise_consol={canary['noise_canary_consolidated_count']}", flush=True)
    main_u = load_units(output_dir)[unit_key("main", run_mode)]

    # ---- UNIT 3: baseline (empty overlay) -----------------------------------------------------
    if unit_key("baseline", run_mode) not in completed_units(output_dir):
        _vls.clear_acquired_outcome()
        b_acc, b_correct = _score(oov_rows)[0:2]
        record_unit(output_dir, unit_key("baseline", run_mode),
                    {"fallthrough_baseline_accuracy": round(b_acc, 4), "fallthrough_correct": b_correct})
    base_u = load_units(output_dir)[unit_key("baseline", run_mode)]

    # ---- UNIT 4: scramble control (5 seeds) ---------------------------------------------------
    if unit_key("scramble", run_mode) not in completed_units(output_dir):
        print("[progress] scramble control (5 seeds)", flush=True)
        scr = _scramble_control(main_u["master_records"], oov_rows)
        record_unit(output_dir, unit_key("scramble", run_mode), scr)
    scr_u = load_units(output_dir)[unit_key("scramble", run_mode)]

    # ---- UNIT 5: random-credit ablation -------------------------------------------------------
    if unit_key("random_credit", run_mode) not in completed_units(output_dir):
        print("[progress] random-credit ablation", flush=True)
        rc_rng = np.random.default_rng(3000)

        def _rc_choice(lst):
            return lst[int(rc_rng.integers(len(lst)))]

        rc_rep = learn_corpus(windows, n_passes=N_PASSES, signal_mode="and_gate",
                              credit_mode="random", rng_choice=_rc_choice, register=True)
        rc_reg = rc_rep["registered"]
        rc_learn = _learnable_subset(oov_rows, rc_reg)
        rc_acc = _score_with_overlay(oov_rows, rc_reg)[0]
        record_unit(output_dir, unit_key("random_credit", run_mode), {
            "random_credit_primary_accuracy": round(rc_acc, 4),
            "random_credit_n_registered": len(rc_reg),
            "random_credit_learnable_subset_accuracy": rc_learn["learnable_subset_accuracy"],
            "random_credit_n_learnable": rc_learn["n_learnable"],
        })
    rc_u = load_units(output_dir)[unit_key("random_credit", run_mode)]

    # ---- UNIT 6/7: single-signal ablations (noise canary comparison) --------------------------
    for mode_name in ("signal_a", "signal_b"):
        if unit_key(mode_name, run_mode) in completed_units(output_dir):
            continue
        print(f"[progress] {mode_name}-only ablation", flush=True)
        sig_mode = "signal_a_only" if mode_name == "signal_a" else "signal_b_only"
        ss_rep = learn_corpus(windows, n_passes=N_PASSES, signal_mode=sig_mode,
                              credit_mode="referent_linked", register=True)
        ss_canary = _canary_analysis(ss_rep["master_counter"], ss_rep["master_grounded"])
        _vls.clear_acquired_outcome()
        record_unit(output_dir, unit_key(mode_name, run_mode), {
            "n_registered": len(ss_rep["registered"]),
            "noise_canary_consolidated_count": ss_canary["noise_canary_consolidated_count"],
            "noise_canary_consolidated_words": ss_canary["noise_canary_consolidated_words"],
            "light_verb_canary_neutral_rate": ss_canary["light_verb_canary_neutral_rate"],
        })
    sa_u = load_units(output_dir)[unit_key("signal_a", run_mode)]
    sb_u = load_units(output_dir)[unit_key("signal_b", run_mode)]

    return _aggregate(run_mode, oov_rows, majority_floor, corpus_u, main_u, base_u, scr_u, rc_u,
                      sa_u, sb_u)


def _aggregate(run_mode, oov_rows, majority_floor, corpus_u, main_u, base_u, scr_u, rc_u, sa_u, sb_u):
    primary = main_u["primary_accuracy"]
    learnable = main_u["learnable"]
    canary = main_u["canary"]
    scrambled = scr_u["scrambled_primary_accuracy"]
    lv_rate = canary["light_verb_canary_neutral_rate"]
    n_learnable = learnable["n_learnable"]
    ls_acc = learnable["learnable_subset_accuracy"]
    noise_consol = canary["noise_canary_consolidated_count"]
    rc_ls = rc_u["random_credit_learnable_subset_accuracy"]
    integ = corpus_u["exclusion_integrity"]

    agg = {
        "anchor_name": ANCHOR_NAME, "run_mode": run_mode,
        "config": {"W": W, "MIN_CONFIRM": MIN_CONFIRM, "NEUTRAL_BAND": NEUTRAL_BAND,
                   "N_PASSES": N_PASSES, "n_scramble_seeds": N_SCRAMBLE_SEEDS,
                   "exclude_margin": EXCLUDE_MARGIN, "n_oov_items": len(oov_rows)},
        "corpus_stats": corpus_u["corpus_stats"], "win_stats": corpus_u["win_stats"],
        "exclusion_integrity": integ,
        "majority_floor": majority_floor, "increment_1b_ref": INCREMENT_1B_REF,
        "fallthrough_baseline_accuracy": base_u["fallthrough_baseline_accuracy"],
        "primary_accuracy": primary,
        "met_recall": f"{main_u['met_recall_correct']}/{main_u['met_total']}",
        "unmet_recall": f"{main_u['unmet_recall_correct']}/{main_u['unmet_total']}",
        "n_registered": len(main_u["registered"]), "registered": main_u["registered"],
        "learnable_subset": learnable,
        "light_verb_canary": {k: canary[k] for k in (
            "light_verb_canary_neutral_rate", "light_verb_n_reached", "light_verb_n_neutral",
            "light_verb_n_polar_locked", "light_verb_reached_minconfirm")},
        "noise_canary": {"consolidated_count": noise_consol,
                         "consolidated_words": canary["noise_canary_consolidated_words"]},
        "bootstrap_curve": main_u["pass_reports"],
        "scramble": scr_u,
        "random_credit": rc_u,
        "signal_a_only": sa_u, "signal_b_only": sb_u,
        "light_verb_detail": canary["light_verb_detail"],
        "noise_detail": canary["noise_detail"],
    }

    # ---- verdict (per pre-reg bands; per-gate, never aggregate) --------------------------------
    gaps = {}
    # HARD-PASS gates
    hp1 = (ls_acc is not None and ls_acc >= 0.75) and (n_learnable >= 6)
    hp2 = (primary >= 0.60)
    hp3 = (lv_rate is not None and lv_rate >= 0.70)
    scr_in_band = (scrambled is not None and 0.40 <= scrambled <= 0.60)
    scr_gap = (scrambled is not None and (primary - scrambled) >= 0.15)
    rc_gap = (ls_acc is not None and rc_ls is not None and (ls_acc - rc_ls) >= 0.15)
    ss_ok = (main_u["canary"]["noise_canary_consolidated_count"]
             <= sa_u["noise_canary_consolidated_count"]) and \
            (main_u["canary"]["noise_canary_consolidated_count"]
             <= sb_u["noise_canary_consolidated_count"])
    hp4 = scr_in_band and scr_gap and rc_gap and ss_ok and integ["clean"]
    hp5 = (noise_consol == 0)

    # HARD-FAIL gates
    hf_primary = (primary <= majority_floor)
    hf_scramble = (scrambled is not None and abs(primary - scrambled) <= 0.08)
    hf_random = (ls_acc is not None and rc_ls is not None and abs(ls_acc - rc_ls) <= 0.08)
    hf_lightverb = (lv_rate is not None and lv_rate < 0.30)
    hf_noise = (noise_consol >= 2)
    hf_yield = (n_learnable < 3)

    gate_detail = {
        "HP1_learnable_subset": {"ls_acc>=0.75": hp1, "ls_acc": ls_acc, "n_learnable": n_learnable},
        "HP2_primary>=0.60": {"pass": hp2, "primary": primary},
        "HP3_light_verb_neutral>=0.70": {"pass": hp3, "rate": lv_rate},
        "HP4_noncircularity": {"scramble_in_[0.40,0.60]": scr_in_band, "scramble": scrambled,
                               "gap>=0.15": scr_gap, "random_credit_gap>=0.15": rc_gap,
                               "single_signal_noise_ok": ss_ok, "exclusion_clean": integ["clean"]},
        "HP5_noise==0": {"pass": hp5, "noise_consolidated": noise_consol},
        "HF_primary<=floor": hf_primary, "HF_scramble_within_0.08": hf_scramble,
        "HF_random_within_0.08": hf_random, "HF_lightverb<0.30": hf_lightverb,
        "HF_noise>=2": hf_noise, "HF_insufficient_yield<3": hf_yield,
    }

    hard_pass = all([hp1, hp2, hp3, hp4, hp5])
    hard_fail = any([hf_primary, hf_scramble, hf_random, hf_lightverb, hf_noise, hf_yield])

    if hard_pass and not hard_fail:
        verdict = "HARD_PASS"
    elif hard_fail:
        verdict = "HARD_FAIL"
    else:
        verdict = "MIDDLE_BAND"

    agg["gate_detail"] = gate_detail
    agg["verdict"] = verdict
    agg["verdict_msg"] = (
        f"{verdict}: primary={primary:.4f} (floor={majority_floor}, inc1b={INCREMENT_1B_REF}) | "
        f"learnable={ls_acc}({n_learnable}/N>=6) | lv_neutral={lv_rate} | "
        f"scramble={scrambled} gap={round(primary - scrambled, 4) if scrambled is not None else None} | "
        f"rand_credit_ls={rc_ls} | noise_consol={noise_consol} | "
        f"single_sig_noise(a={sa_u['noise_canary_consolidated_count']},b={sb_u['noise_canary_consolidated_count']}) | "
        f"excl_clean={integ['clean']}")
    agg["summary"] = agg["verdict_msg"][:300]
    return agg


# ------------------------------------------------------------------ discriminator-fires (smoke gate)
def _discriminator_fires(agg):
    """Smoke gate: the mechanism must actually EXERCISE -- >=1 teacher window fired AND >=1 exposure
    was credited (some word accumulated evidence). A vacuous smoke (no teacher, no credit) is not a
    valid discriminator test."""
    passes = agg["bootstrap_curve"]
    max_teacher = max((p["n_windows_with_teacher"] for p in passes), default=0)
    max_credit = max((p["n_new_exposure_pairs"] for p in passes), default=0)
    return {"max_windows_with_teacher": max_teacher, "max_exposure_pairs": max_credit,
            "fires": (max_teacher > 0 and max_credit > 0)}


# ------------------------------------------------------------------ driver
def run(run_mode):
    t0 = time.perf_counter()
    output_dir = OUTPUT_DIR_FULL if run_mode == "full" else f"{OUTPUT_DIR_FULL}_{run_mode}"
    expected_n_units = 8  # corpus, main, baseline, scramble, random_credit, signal_a, signal_b (+curve)
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
    """Construct the REAL engine objects at tiny scale + exercise the real corpus-reader + eval-loader
    code paths (F.1 real_code_path), assert the engine self-test passes, and verify the citation parser
    + exclusion builder fire on a real eval row. No full corpus scan."""
    eng = _engine_self_test()
    assert eng["determinism_ok"], "engine determinism failed"
    # real eval load
    all_rows, oov_rows = _load_eval()
    assert len(oov_rows) == 36, f"expected 36 OOV items, got {len(oov_rows)}"
    n_met = sum(1 for r in oov_rows if r["gold_outcome_polarity"] == "met")
    assert n_met == 23, f"expected 23 met, got {n_met}"
    # citation parse on a real row
    fn, a, b = _parse_citation("little_women.clean.txt:~1945-1981")
    assert (fn, a, b) == ("little_women.clean.txt", 1945, 1981), (fn, a, b)
    # exclusion builder produces a NON-EMPTY mask on the real little_women file (F.1: real code path)
    blocks, stats, excl = _read_corpus_blocks(all_rows, SMOKE_NOVELS)
    assert stats["little_women.clean.txt"]["excluded_lines"] > 0, "exclusion mask empty on real file"
    assert len(blocks) > 0, "no corpus blocks produced"
    # a real find_desired_state-firing window can be built + scored end-to-end on a tiny slice
    windows, win_stats = _build_windows(blocks[:20], all_rows)
    # teacher_verdict + credit_window are callable on a real window (may be None; just must not crash)
    if windows:
        gs, win, ref = windows[0]
        _ = teacher_verdict(gs, win)
        _ = credit_window(gs, win, ref)
    _vls.clear_acquired_outcome()
    return {"engine": eng, "n_oov": len(oov_rows), "n_met": n_met,
            "excluded_lines_lw": stats["little_women.clean.txt"]["excluded_lines"],
            "n_blocks_smoke": len(blocks), "tiny_windows": win_stats["n_windows"]}


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
    output_dir_guess = OUTPUT_DIR_FULL
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # NOT BaseException
        # best-effort: write crash metrics to whichever dir the run targeted
        for cand in (OUTPUT_DIR_FULL, f"{OUTPUT_DIR_FULL}_smoke"):
            if os.path.exists(cand) or cand == OUTPUT_DIR_FULL:
                _write_crash_metrics(cand, e)
                break
        raise
