"""exp_combined_dictionary_consequence_word_learning_tool_v1 -- the COMBINED dictionary-lookup +
consequence-learning word-learning tool, on the 36-item OOV eval.

Pre-reg: preregs/2026-08-06_combined_dictionary_consequence_word_learning_tool_v1.md
Spec:    notes/research_combined_dictionary_consequence_word_learning_tool_2026-08-06.md
Halves:  hdlab/wordnet_polarity_propagation.py (dictionary_lookup, NEW) +
         hdlab/consequence_learning_loop.py (learn_corpus, UNCHANGED engine; dictionary_priors is a
         strictly-additive optional param) fused by hdlab/word_learning_tool.py (learn_corpus_combined).

WHAT: "look the word up in the dictionary first, then confirm/refine/override through story
consequence" (USER 2026-08-06). THE DECISIVE 3-WAY ABLATION: dictionary-only vs consequence-only
(0.1944 measured @ 093ddc1aa) vs COMBINED, on the 36-item OOV eval scored by the LIVE production
congruence_with_lexicon_fallback. Per-verb table for the 16 content lemmas. Light-verb self-lock gate
(zero-tolerance). Scramble BOTH halves (dict + consequence) -> combined must collapse.

Reuses the parent consequence cell's validated corpus/scoring/canary/scramble helpers VERBATIM
(wire-don't-island). NOT a new corpus build.

# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - final_metrics_atomicity: tmp_replace (os.replace)
# - deterministic_seeding: fixed integer seeds only (np.random.default_rng(fixed)); no hash()-seeding
# - start_marker + crash_diagnostic + resumable per-unit (tools/exp_checkpoint)
# - progress_logging: print(..., flush=True)
# - discriminator-fires gate at smoke: dict priors injected AND >=1 teacher window fired
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

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from hdlab.goal_typing import congruence_with_lexicon_fallback  # noqa: E402
from hdlab import verb_lexical_similarity as _vls  # noqa: E402
from hdlab.verb_lexical_similarity import in_lexicon  # noqa: E402
from hdlab.consequence_learning_loop import (  # noqa: E402
    learn_corpus, consolidate, MIN_CONFIRM, NEUTRAL_BAND, W_DEFAULT, N_PASSES_DEFAULT,
)
from hdlab.consequence_learning_loop import self_test as _engine_self_test  # noqa: E402
from hdlab.wordnet_polarity_propagation import (  # noqa: E402
    dictionary_lookup, pseudo_counts_from_dictionary,
    ANCHOR_WORDS, ANCHOR_POLARITY, ANCHOR_WORDS_EXTENDED, ANCHOR_POLARITY_EXTENDED,
    K_MAX, NEIGHBOR_FLOOR, VOTE_MARGIN, VOTE_MARGIN_SATURATE,
)
from hdlab.word_learning_tool import learn_corpus_combined, dictionary_priors_for  # noqa: E402
from hdlab.word_learning_tool import self_test as _tool_self_test  # noqa: E402

# REUSE the parent consequence cell's validated corpus/scoring/canary/scramble helpers verbatim.
from experiments.exp_consequence_learning_loop_oov_outcome_verb_valence_v1 import (  # noqa: E402
    _load_eval, _read_corpus_blocks, _build_windows, _exclusion_integrity,
    _score, _score_with_overlay, _learnable_subset, _canary_analysis, _scramble_control,
    NOVELS, SMOKE_NOVELS, N_SCRAMBLE_SEEDS, LIGHT_VERB_CANARY, NOISE_CANARY, MAJORITY_FLOOR_REF,
)
from tools.exp_checkpoint import unit_key, completed_units, record_unit, load_units  # noqa: E402

ANCHOR_NAME = "combined_dictionary_consequence_word_learning_tool_v1"
OUTPUT_DIR_FULL = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}")

SIGNAL_MODE = "signal_a_only"      # matches the 093ddc1aa decisive-run config (consequence half)
CREDIT_MODE = "referent_linked"
N_PASSES = N_PASSES_DEFAULT

# 16-lemma content-verb subset (companion spec Section 5; re-derived from the eval this session).
CONTENT_16 = ["admit", "agree", "befriend", "croak", "encore", "flee", "improve", "jell", "like",
              "rap", "refuse", "relent", "ruin", "spoil", "whip", "whitewash"]

CONSEQUENCE_ONLY_REF = 0.1944      # 093ddc1aa primary_accuracy (re-computed here, never trusted blind)


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


# ------------------------------------------------------------------ scoring helpers (content subset)
def _score_content_subset(oov_rows, registered):
    """Primary metric restricted to eval items whose outcome_verb_lemma is in CONTENT_16 (the fair
    subset), scored live under the overlay. Returns (accuracy_or_None, n_items, correct)."""
    items = [r for r in oov_rows if r["outcome_verb_lemma"] in set(CONTENT_16)]
    _vls.clear_acquired_outcome()
    for lemma, pol in registered.items():
        _vls.register_acquired_outcome(lemma, pol)
    correct = 0
    for r in items:
        gold = "MET" if r["gold_outcome_polarity"] == "met" else "UNMET"
        pred, _d = congruence_with_lexicon_fallback(r["text"])
        correct += (pred == gold)
    _vls.clear_acquired_outcome()
    acc = (correct / len(items)) if items else None
    return (round(acc, 4) if acc is not None else None), len(items), correct


def _unmet_recall(oov_rows, registered):
    """(unmet_correct, unmet_total) under the overlay -- the class-imbalance guard for gate 1."""
    _vls.clear_acquired_outcome()
    for lemma, pol in registered.items():
        _vls.register_acquired_outcome(lemma, pol)
    uc = ut = 0
    for r in oov_rows:
        if r["gold_outcome_polarity"] != "unmet":
            continue
        ut += 1
        pred, _d = congruence_with_lexicon_fallback(r["text"])
        uc += (pred == "UNMET")
    _vls.clear_acquired_outcome()
    return uc, ut


# ------------------------------------------------------------------ dictionary priors + detail
def _dict_detail(lemmas, anchor_words=ANCHOR_WORDS, anchor_polarity=ANCHOR_POLARITY):
    """{lemma: {stage, polarity, confidence, vote_margin, n_neighbors, pseudo_pos, pseudo_neg}} for a
    lemma iterable (banker's-rounding pseudo-counts). Sorted deterministic dict."""
    out = {}
    for lm in sorted(set(lemmas)):
        lu = dictionary_lookup(lm, anchor_words, anchor_polarity)
        n = round(K_MAX * lu.confidence) if lu.polarity is not None else 0
        out[lm] = {"stage": lu.stage, "polarity": lu.polarity,
                   "confidence": round(lu.confidence, 4), "vote_margin": lu.vote_margin,
                   "n_neighbors": lu.n_neighbors,
                   "pseudo_pos": (n if lu.polarity == "POS" else 0),
                   "pseudo_neg": (n if lu.polarity == "NEG" else 0)}
    return out


# ------------------------------------------------------------------ per-verb decisive table
def _per_verb_combined(oov_rows, lookups, priors, master_counter, master_grounded):
    """THE decisive table (task's explicit ask): for each of the 33 unique OOV lemmas, dictionary
    sense+confidence, the pseudo-count, the REAL consequence adjustment (master_counter minus the dict
    prior), the combined total/margin/final verdict, and the eval gold (if the lemma is an eval item's
    outcome verb). Content lemmas flagged. Returns (table, content_table)."""
    eval_lemmas = {}
    for r in oov_rows:
        eval_lemmas.setdefault(r["outcome_verb_lemma"], []).append(r)
    table = []
    for lm in sorted(set(list(lookups) + list(eval_lemmas))):
        lu = lookups.get(lm)
        prior = priors.get(lm, {"POS": 0, "NEG": 0})
        mc = master_counter.get(lm, {"POS": 0, "NEG": 0})
        real_pos = mc.get("POS", 0) - prior.get("POS", 0)
        real_neg = mc.get("NEG", 0) - prior.get("NEG", 0)
        total = mc.get("POS", 0) + mc.get("NEG", 0)
        margin = ((mc.get("POS", 0) - mc.get("NEG", 0)) / total) if total else None
        golds = None
        if lm in eval_lemmas:
            gs = ["met" if r["gold_outcome_polarity"] == "met" else "unmet" for r in eval_lemmas[lm]]
            golds = {"met": gs.count("met"), "unmet": gs.count("unmet")}
        table.append({
            "lemma": lm, "is_content": lm in set(CONTENT_16), "in_eval": lm in eval_lemmas,
            "dict_stage": (lu.stage if lu else None),
            "dict_polarity": (lu.polarity if lu else None),
            "dict_confidence": (round(lu.confidence, 4) if lu else None),
            "dict_pseudo_pos": prior.get("POS", 0), "dict_pseudo_neg": prior.get("NEG", 0),
            "consequence_real_pos": real_pos, "consequence_real_neg": real_neg,
            "combined_total": total,
            "combined_margin": (round(margin, 4) if margin is not None else None),
            "final_verdict": master_grounded.get(lm, "ABSENT"),
            "gold": golds,
        })
    content_table = [row for row in table if row["is_content"]]
    return table, content_table


# ------------------------------------------------------------------ light-verb self-lock gate (gate 6)
def _light_verb_self_lock(master_counter, master_grounded, priors):
    """The sharpest gate (companion spec Section 4). For each LIGHT_VERB_CANARY lemma:
      dict_alone_lock  = the DICTIONARY pseudo-count alone reaches MIN_CONFIRM with a polarity
                         (pure-dictionary measure: would lock with ZERO story evidence).
      combined_self_lock = COMBINED final_verdict is POS/NEG AND real consequence exposures == 0
                         (the pre-reg's gate-6 definition: locked from dict-pseudo alone in the live run).
    Returns detail + the two violation lists. Gate-6 HARD-FAIL fires on ANY combined_self_lock."""
    dict_alone = []
    combined_lock = []
    detail = {}
    for lm in LIGHT_VERB_CANARY:
        prior = priors.get(lm, {"POS": 0, "NEG": 0})
        dict_total = prior.get("POS", 0) + prior.get("NEG", 0)
        dict_pol = ("POS" if prior.get("POS", 0) > prior.get("NEG", 0)
                    else ("NEG" if prior.get("NEG", 0) > 0 else None))
        dict_alone_lock = (dict_total >= MIN_CONFIRM and dict_pol is not None)
        mc = master_counter.get(lm, {"POS": 0, "NEG": 0})
        real_pos = mc.get("POS", 0) - prior.get("POS", 0)
        real_neg = mc.get("NEG", 0) - prior.get("NEG", 0)
        verdict = master_grounded.get(lm, "ABSENT")
        comb_lock = (verdict in ("POS", "NEG") and (real_pos + real_neg) == 0)
        if dict_alone_lock:
            dict_alone.append(lm)
        if comb_lock:
            combined_lock.append(lm)
        detail[lm] = {"dict_pseudo_pos": prior.get("POS", 0), "dict_pseudo_neg": prior.get("NEG", 0),
                      "dict_alone_lock": dict_alone_lock,
                      "real_pos": real_pos, "real_neg": real_neg,
                      "combined_verdict": verdict, "combined_self_lock": comb_lock}
    return {"dict_alone_lock_words": dict_alone, "dict_alone_lock_count": len(dict_alone),
            "combined_self_lock_words": combined_lock,
            "combined_self_lock_count": len(combined_lock), "detail": detail}


# ------------------------------------------------------------------ scramble controls
def _scramble_anchor_polarity(seed):
    """Permute the POS/NEG labels across ANCHOR_WORDS (fixed seed), WordNet graph UNCHANGED. Returns a
    scrambled anchor_polarity dict over the same words."""
    words = sorted(ANCHOR_WORDS)
    poles = [ANCHOR_POLARITY[w] for w in words]
    rng = np.random.default_rng(seed)
    perm = rng.permutation(len(poles))
    return {words[i]: poles[int(perm[i])] for i in range(len(words))}


def _dict_only_scored(oov_rows, lemmas, anchor_polarity):
    """Register EVERY non-abstain dictionary hit (bypass consolidate/MIN_CONFIRM -- Arm 1 convention),
    score primary + content subset. Returns (registered, primary_acc, content_acc)."""
    registered = {}
    for lm in lemmas:
        lu = dictionary_lookup(lm, ANCHOR_WORDS, anchor_polarity)
        if lu.polarity is not None:
            registered[lm] = lu.polarity
    primary = _score_with_overlay(oov_rows, registered)[0]
    content = _score_content_subset(oov_rows, registered)[0]
    return registered, round(primary, 4), content


def _random_graph_lookup(lemma, real_n_neighbors, rng):
    """Degree-matched random-graph Stage-B: keep the REAL kept-neighbor DEGREE but assign random anchors
    + random sims in [NEIGHBOR_FLOOR, 1.0], then run the identical weighted-vote/margin/confidence logic.
    Isolates that the REAL WordNet structure (not mere degree) drives the polarity. Abstain if degree 0."""
    if real_n_neighbors <= 0:
        return None
    words = sorted(ANCHOR_WORDS)
    idx = rng.choice(len(words), size=min(real_n_neighbors, len(words)), replace=False)
    pos_w = neg_w = 0.0
    for i in idx:
        sim = float(rng.uniform(NEIGHBOR_FLOOR, 1.0))
        if ANCHOR_POLARITY[words[int(i)]] == "POS":
            pos_w += sim
        else:
            neg_w += sim
    total = pos_w + neg_w
    if total == 0.0:
        return None
    margin = abs(pos_w - neg_w) / total
    if margin < VOTE_MARGIN:
        return None
    return "POS" if pos_w > neg_w else "NEG"


def _random_graph_arm(oov_rows, lookups):
    """Arm-1-style scoring under a degree-matched random graph (5 seeds averaged). Uses each lemma's REAL
    n_neighbors as its degree."""
    accs = []
    for s in range(N_SCRAMBLE_SEEDS):
        rng = np.random.default_rng(4000 + s)
        registered = {}
        for lm, lu in lookups.items():
            pol = _random_graph_lookup(lm, lu.n_neighbors, rng)
            if pol is not None:
                registered[lm] = pol
        accs.append(_score_with_overlay(oov_rows, registered)[0])
    return {"random_graph_accuracy": round(float(np.mean(accs)), 4),
            "random_graph_per_seed": [round(a, 4) for a in accs]}


def _combined_conseq_scramble(dict_priors, master_records, oov_rows, n_seeds=N_SCRAMBLE_SEEDS):
    """Gate 4f: REAL dictionary priors + SCRAMBLED consequence teacher labels. Reconstruct the counter =
    deep-copy(real dict priors) + accumulate(permuted teacher_verdict over the REAL exposure records),
    consolidate, register, score. Must be BELOW real combined by a small but non-zero gap (>= 0.03);
    a zero/negative gap = consequence adds no marginal value in the combined run (MIDDLE-BAND-relevant)."""
    verdicts = [rec["teacher_verdict"] for rec in master_records]
    accs = []
    for s in range(n_seeds):
        rng = np.random.default_rng(5000 + s)
        perm = rng.permutation(len(verdicts)) if verdicts else np.array([], dtype=int)
        counter = {lm: dict(c) for lm, c in dict_priors.items()}
        for k, rec in enumerate(master_records):
            v = verdicts[int(perm[k])]
            pole = "POS" if v == "MET" else "NEG"
            counter.setdefault(rec["lemma"], {"POS": 0, "NEG": 0})[pole] += 1
        grounded = consolidate(counter)
        registered = {lm: v for lm, v in grounded.items() if v in ("POS", "NEG")}
        accs.append(_score_with_overlay(oov_rows, registered)[0])
    return {"combined_conseq_scrambled_accuracy": round(float(np.mean(accs)), 4) if accs else None,
            "combined_conseq_scrambled_per_seed": [round(a, 4) for a in accs]}


# ------------------------------------------------------------------ core run (resumable per-unit)
def _run_all(output_dir, run_mode):
    novels = SMOKE_NOVELS if run_mode == "smoke" else NOVELS
    all_rows, oov_rows = _load_eval()
    eval_lemmas = sorted(set(r["outcome_verb_lemma"] for r in oov_rows))
    majority_floor = round(sum(1 for r in oov_rows if r["gold_outcome_polarity"] == "met")
                           / len(oov_rows), 4)

    # non-overlap assert (dictionary half non-circularity): ANCHOR_WORDS must contain ZERO eval lemmas.
    overlap = sorted(set(eval_lemmas) & set(ANCHOR_WORDS))
    overlap_ext = sorted(set(eval_lemmas) & set(ANCHOR_WORDS_EXTENDED))
    if overlap or overlap_ext:
        raise RuntimeError(f"NON_OVERLAP_ASSERT FAILED: eval lemmas in anchor "
                           f"(52={overlap}, ext={overlap_ext}) -- vocabulary leakage, refusing to score")

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

    # ---- UNIT 2: dictionary lookups + priors (33 eval lemmas + canaries) -----------------------
    if unit_key("dict", run_mode) not in completed_units(output_dir):
        print("[progress] dictionary lookups over 33 OOV eval lemmas + canaries", flush=True)
        lookups, priors = dictionary_priors_for(eval_lemmas)
        detail_eval = _dict_detail(eval_lemmas)
        detail_light = _dict_detail(LIGHT_VERB_CANARY)
        detail_noise = _dict_detail(NOISE_CANARY)
        # extended-anchor ablation (informational): dict-only accuracy with the larger anchor
        _reg_ext, ext_primary, ext_content = _dict_only_scored(oov_rows, eval_lemmas,
                                                               ANCHOR_POLARITY_EXTENDED)
        n_hit = sum(1 for v in detail_eval.values() if v["polarity"] is not None)
        n_content_hit = sum(1 for lm in CONTENT_16
                            if detail_eval.get(lm, {}).get("polarity") is not None)
        record_unit(output_dir, unit_key("dict", run_mode), {
            "priors": priors, "dict_detail_eval": detail_eval,
            "dict_detail_light": detail_light, "dict_detail_noise": detail_noise,
            "n_eval_lemmas": len(eval_lemmas), "n_dict_hit": n_hit,
            "n_content_lemmas": len(CONTENT_16), "n_content_dict_hit": n_content_hit,
            "extended_anchor": {"n_anchor_extended": len(ANCHOR_WORDS_EXTENDED),
                                "dict_only_primary": ext_primary, "dict_only_content": ext_content},
        })
        print(f"[progress] dict: n_hit={n_hit}/{len(eval_lemmas)} content_hit={n_content_hit}/16 "
              f"priors={ {k: dict(v) for k, v in priors.items()} }", flush=True)
    dict_u = load_units(output_dir)[unit_key("dict", run_mode)]
    priors = dict_u["priors"]
    lookups = {lm: dictionary_lookup(lm) for lm in eval_lemmas}   # cheap, deterministic; not stored raw

    # ---- UNIT 3: ARM 1 dictionary-only --------------------------------------------------------
    if unit_key("arm1", run_mode) not in completed_units(output_dir):
        print("[progress] ARM 1 dictionary-only", flush=True)
        reg1, a1_primary, a1_content = _dict_only_scored(oov_rows, eval_lemmas, ANCHOR_POLARITY)
        uc, ut = _unmet_recall(oov_rows, reg1)
        record_unit(output_dir, unit_key("arm1", run_mode), {
            "registered": reg1, "dict_only_primary_accuracy": a1_primary,
            "dict_only_content_accuracy": a1_content, "unmet_recall_correct": uc, "unmet_total": ut,
            "n_registered": len(reg1)})
        print(f"[progress] arm1: primary={a1_primary} content={a1_content} n_reg={len(reg1)}", flush=True)
    arm1_u = load_units(output_dir)[unit_key("arm1", run_mode)]

    # ---- UNIT 4: ARM 2 consequence-only (dictionary_priors=None) ------------------------------
    if unit_key("arm2", run_mode) not in completed_units(output_dir):
        print("[progress] ARM 2 consequence-only (signal_a_only, referent_linked)", flush=True)
        rep2 = learn_corpus(windows, n_passes=N_PASSES, signal_mode=SIGNAL_MODE,
                            credit_mode=CREDIT_MODE, register=True, dictionary_priors=None)
        reg2 = rep2["registered"]
        a2_primary = round(_score_with_overlay(oov_rows, reg2)[0], 4)
        a2_content = _score_content_subset(oov_rows, reg2)[0]
        a2_learn = _learnable_subset(oov_rows, reg2)
        record_unit(output_dir, unit_key("arm2", run_mode), {
            "registered": reg2, "master_records": rep2["master_records"],
            "master_counter": rep2["master_counter"], "master_grounded": rep2["master_grounded"],
            "consequence_only_primary_accuracy": a2_primary,
            "consequence_only_content_accuracy": a2_content,
            "learnable": a2_learn, "n_registered": len(reg2)})
        print(f"[progress] arm2: primary={a2_primary} content={a2_content} n_reg={len(reg2)} "
              f"n_learnable={a2_learn['n_learnable']}", flush=True)
    arm2_u = load_units(output_dir)[unit_key("arm2", run_mode)]

    # ---- UNIT 5: ARM 3 combined (dictionary_priors injected once) -----------------------------
    if unit_key("arm3", run_mode) not in completed_units(output_dir):
        print("[progress] ARM 3 combined (dict priors injected once + consequence)", flush=True)
        rep3 = learn_corpus_combined(windows, oov_lemmas=eval_lemmas, n_passes=N_PASSES,
                                     signal_mode=SIGNAL_MODE, credit_mode=CREDIT_MODE, register=True)
        reg3 = rep3["registered"]
        a3_primary, a3_correct, a3_met_c, a3_unmet_c, a3_n_met, a3_n_unmet, a3_details = \
            _score_with_overlay(oov_rows, reg3)
        a3_content = _score_content_subset(oov_rows, reg3)[0]
        a3_learn = _learnable_subset(oov_rows, reg3)
        canary = _canary_analysis(rep3["master_counter"], rep3["master_grounded"])
        per_verb, content_verb = _per_verb_combined(
            oov_rows, lookups, priors, rep3["master_counter"], rep3["master_grounded"])
        self_lock = _light_verb_self_lock(rep3["master_counter"], rep3["master_grounded"], priors)
        record_unit(output_dir, unit_key("arm3", run_mode), {
            "registered": reg3, "master_records": rep3["master_records"],
            "master_counter": rep3["master_counter"], "master_grounded": rep3["master_grounded"],
            "pass_reports": rep3["pass_reports"],
            "combined_primary_accuracy": round(a3_primary, 4), "combined_primary_correct": a3_correct,
            "combined_content_accuracy": a3_content,
            "met_recall": f"{a3_met_c}/{a3_n_met}", "unmet_recall": f"{a3_unmet_c}/{a3_n_unmet}",
            "unmet_recall_correct": a3_unmet_c, "unmet_total": a3_n_unmet,
            "score_details": a3_details, "learnable": a3_learn, "canary": canary,
            "per_verb": per_verb, "content_verb": content_verb, "self_lock": self_lock,
            "n_registered": len(reg3)})
        print(f"[progress] arm3: primary={round(a3_primary,4)} content={a3_content} n_reg={len(reg3)} "
              f"lv_dict_alone_lock={self_lock['dict_alone_lock_words']} "
              f"lv_combined_self_lock={self_lock['combined_self_lock_words']} "
              f"noise={canary['noise_canary_consolidated_count']}", flush=True)
    arm3_u = load_units(output_dir)[unit_key("arm3", run_mode)]

    # ---- UNIT 6: baseline (empty overlay) -----------------------------------------------------
    if unit_key("baseline", run_mode) not in completed_units(output_dir):
        _vls.clear_acquired_outcome()
        b = _score(oov_rows)
        record_unit(output_dir, unit_key("baseline", run_mode),
                    {"empty_overlay_accuracy": round(b[0], 4)})
    base_u = load_units(output_dir)[unit_key("baseline", run_mode)]

    # ---- UNIT 7: dictionary-half controls (a scramble, b random-graph) ------------------------
    if unit_key("dict_controls", run_mode) not in completed_units(output_dir):
        print("[progress] dict controls: anchor-polarity scramble (5) + random-graph (5)", flush=True)
        scr_accs = []
        for s in range(N_SCRAMBLE_SEEDS):
            scr_pol = _scramble_anchor_polarity(6000 + s)
            _reg, primary, _content = _dict_only_scored(oov_rows, eval_lemmas, scr_pol)
            scr_accs.append(primary)
        rg = _random_graph_arm(oov_rows, lookups)
        record_unit(output_dir, unit_key("dict_controls", run_mode), {
            "scrambled_dict_accuracy": round(float(np.mean(scr_accs)), 4),
            "scrambled_dict_per_seed": [round(a, 4) for a in scr_accs],
            **rg})
    dctl_u = load_units(output_dir)[unit_key("dict_controls", run_mode)]

    # ---- UNIT 8: consequence-half controls (c scramble, d random-credit) ----------------------
    if unit_key("conseq_controls", run_mode) not in completed_units(output_dir):
        print("[progress] conseq controls: teacher-label scramble (5) + random-credit", flush=True)
        scr_c = _scramble_control(arm2_u["master_records"], oov_rows)
        rc_rng = np.random.default_rng(3000)

        def _rc_choice(lst):
            return lst[int(rc_rng.integers(len(lst)))]

        rc_rep = learn_corpus(windows, n_passes=N_PASSES, signal_mode=SIGNAL_MODE,
                              credit_mode="random", rng_choice=_rc_choice, register=True,
                              dictionary_priors=None)
        rc_reg = rc_rep["registered"]
        rc_primary = round(_score_with_overlay(oov_rows, rc_reg)[0], 4)
        rc_learn = _learnable_subset(oov_rows, rc_reg)
        _vls.clear_acquired_outcome()
        record_unit(output_dir, unit_key("conseq_controls", run_mode), {
            "scrambled_consequence_accuracy": scr_c["scrambled_primary_accuracy"],
            "scrambled_consequence_per_seed": scr_c["scrambled_per_seed"],
            "random_credit_primary_accuracy": rc_primary,
            "random_credit_learnable_subset_accuracy": rc_learn["learnable_subset_accuracy"],
            "random_credit_n_learnable": rc_learn["n_learnable"]})
    cctl_u = load_units(output_dir)[unit_key("conseq_controls", run_mode)]

    # ---- UNIT 9: combined-arm scrambles (e dict-scrambled, f conseq-scrambled) -----------------
    if unit_key("combined_scrambles", run_mode) not in completed_units(output_dir):
        print("[progress] combined scrambles: dict-scrambled (5, re-run) + conseq-scrambled (5)", flush=True)
        cds_accs = []
        for s in range(N_SCRAMBLE_SEEDS):
            scr_pol = _scramble_anchor_polarity(7000 + s)
            rep_e = learn_corpus_combined(windows, oov_lemmas=eval_lemmas, n_passes=N_PASSES,
                                          anchor_polarity=scr_pol, signal_mode=SIGNAL_MODE,
                                          credit_mode=CREDIT_MODE, register=True)
            cds_accs.append(_score_with_overlay(oov_rows, rep_e["registered"])[0])
        cds = {"combined_dict_scrambled_accuracy": round(float(np.mean(cds_accs)), 4),
               "combined_dict_scrambled_per_seed": [round(a, 4) for a in cds_accs]}
        ccs = _combined_conseq_scramble(priors, arm3_u["master_records"], oov_rows)
        record_unit(output_dir, unit_key("combined_scrambles", run_mode), {**cds, **ccs})
    cscr_u = load_units(output_dir)[unit_key("combined_scrambles", run_mode)]

    return _aggregate(run_mode, oov_rows, majority_floor, corpus_u, dict_u, arm1_u, arm2_u, arm3_u,
                      base_u, dctl_u, cctl_u, cscr_u)


# ------------------------------------------------------------------ aggregate + verdict
def _aggregate(run_mode, oov_rows, majority_floor, corpus_u, dict_u, arm1_u, arm2_u, arm3_u, base_u,
               dctl_u, cctl_u, cscr_u):
    a1 = arm1_u["dict_only_primary_accuracy"]
    a1c = arm1_u["dict_only_content_accuracy"]
    a2 = arm2_u["consequence_only_primary_accuracy"]
    a3 = arm3_u["combined_primary_accuracy"]
    a3c = arm3_u["combined_content_accuracy"]
    canary = arm3_u["canary"]
    self_lock = arm3_u["self_lock"]
    noise_consol = canary["noise_canary_consolidated_count"]
    lv_rate = canary["light_verb_canary_neutral_rate"]
    a3_unmet_c = arm3_u["unmet_recall_correct"]
    a3_unmet_t = arm3_u["unmet_total"]

    scr_dict = dctl_u["scrambled_dict_accuracy"]
    rg = dctl_u["random_graph_accuracy"]
    scr_conseq = cctl_u["scrambled_consequence_accuracy"]
    rc = cctl_u["random_credit_primary_accuracy"]
    cds = cscr_u["combined_dict_scrambled_accuracy"]
    ccs = cscr_u["combined_conseq_scrambled_accuracy"]
    integ = corpus_u["exclusion_integrity"]

    def _gap(x, y):
        return round(x - y, 4) if (x is not None and y is not None) else None

    agg = {
        "anchor_name": ANCHOR_NAME, "run_mode": run_mode,
        "config": {"W": W_DEFAULT, "MIN_CONFIRM": MIN_CONFIRM, "NEUTRAL_BAND": NEUTRAL_BAND,
                   "N_PASSES": N_PASSES, "K_MAX": K_MAX, "NEIGHBOR_FLOOR": NEIGHBOR_FLOOR,
                   "VOTE_MARGIN": VOTE_MARGIN, "VOTE_MARGIN_SATURATE": VOTE_MARGIN_SATURATE,
                   "signal_mode": SIGNAL_MODE, "credit_mode": CREDIT_MODE,
                   "n_anchor": len(ANCHOR_WORDS), "n_anchor_extended": len(ANCHOR_WORDS_EXTENDED),
                   "n_oov_items": len(oov_rows)},
        "corpus_stats": corpus_u["corpus_stats"], "win_stats": corpus_u["win_stats"],
        "exclusion_integrity": integ,
        "majority_floor": majority_floor, "empty_overlay_floor": base_u["empty_overlay_accuracy"],
        "consequence_only_ref_093": CONSEQUENCE_ONLY_REF,
        # ---- THE 3-WAY ABLATION ----
        "three_way": {
            "dict_only_primary": a1, "consequence_only_primary": a2, "combined_primary": a3,
            "dict_only_content": a1c, "combined_content": a3c,
            "gap_combined_minus_dict": _gap(a3, a1),
            "gap_combined_minus_consequence": _gap(a3, a2)},
        "arm1_dict_only": {k: arm1_u[k] for k in (
            "dict_only_primary_accuracy", "dict_only_content_accuracy", "registered",
            "unmet_recall_correct", "unmet_total", "n_registered")},
        "arm2_consequence_only": {k: arm2_u[k] for k in (
            "consequence_only_primary_accuracy", "consequence_only_content_accuracy",
            "registered", "learnable", "n_registered")},
        "arm3_combined": {
            "combined_primary_accuracy": a3, "combined_content_accuracy": a3c,
            "met_recall": arm3_u["met_recall"], "unmet_recall": arm3_u["unmet_recall"],
            "registered": arm3_u["registered"], "n_registered": arm3_u["n_registered"],
            "learnable": arm3_u["learnable"], "bootstrap_curve": arm3_u["pass_reports"]},
        "dict_detail_eval": dict_u["dict_detail_eval"],
        "dict_detail_light": dict_u["dict_detail_light"],
        "dict_detail_noise": dict_u["dict_detail_noise"],
        "dict_coverage": {"n_eval_lemmas": dict_u["n_eval_lemmas"], "n_dict_hit": dict_u["n_dict_hit"],
                          "n_content_lemmas": dict_u["n_content_lemmas"],
                          "n_content_dict_hit": dict_u["n_content_dict_hit"]},
        "extended_anchor": dict_u["extended_anchor"],
        "per_verb_content_16": arm3_u["content_verb"],
        "per_verb_all": arm3_u["per_verb"],
        "light_verb_self_lock": self_lock,
        "light_verb_canary": {k: canary[k] for k in (
            "light_verb_canary_neutral_rate", "light_verb_n_reached", "light_verb_n_neutral",
            "light_verb_n_polar_locked", "light_verb_reached_minconfirm")},
        "noise_canary": {"consolidated_count": noise_consol,
                         "consolidated_words": canary["noise_canary_consolidated_words"]},
        "non_circularity": {
            "scrambled_dict_accuracy": scr_dict, "scrambled_dict_per_seed": dctl_u["scrambled_dict_per_seed"],
            "random_graph_accuracy": rg, "random_graph_per_seed": dctl_u["random_graph_per_seed"],
            "scrambled_consequence_accuracy": scr_conseq,
            "random_credit_primary_accuracy": rc,
            "random_credit_learnable_subset_accuracy": cctl_u["random_credit_learnable_subset_accuracy"],
            "random_credit_n_learnable": cctl_u["random_credit_n_learnable"],
            "combined_dict_scrambled_accuracy": cds,
            "combined_dict_scrambled_per_seed": cscr_u["combined_dict_scrambled_per_seed"],
            "combined_conseq_scrambled_accuracy": ccs,
            "combined_conseq_scrambled_per_seed": cscr_u["combined_conseq_scrambled_per_seed"],
            "gap_combined_vs_dict_scrambled": _gap(a3, cds),
            "gap_combined_vs_conseq_scrambled": _gap(a3, ccs)},
    }

    # ---- verdict (per pre-reg bands; per-gate, never aggregate) --------------------------------
    # HARD-PASS gates
    hp1 = (a3 >= 27 / 36) and (a3_unmet_t > 0 and a3_unmet_c >= 5)
    hp2 = (a3c is not None and a3c >= 0.70)
    g3a = (_gap(a3, a1) is not None and _gap(a3, a1) >= 0.03)
    g3b = (a3c is not None and a1c is not None and a3c >= a1c)
    g3c = (_gap(a3, a2) is not None and _gap(a3, a2) >= 0.30)
    hp3 = g3a and g3b and g3c
    nc_a = (scr_dict is not None and 0.35 <= scr_dict <= 0.65)
    nc_b = (rg is not None and 0.35 <= rg <= 0.65)
    nc_c = (scr_conseq is not None and 0.40 <= scr_conseq <= 0.60)
    nc_e = (_gap(a3, cds) is not None and _gap(a3, cds) >= 0.15)
    hp4 = nc_a and nc_b and nc_c and nc_e and integ["clean"]
    hp5 = (noise_consol == 0)
    hp6 = (self_lock["combined_self_lock_count"] == 0)

    # HARD-FAIL gates
    hf_floor = (a3 <= majority_floor)
    hf_no_better_than_dict = (a3 <= a1)
    hf_scr_dict = (scr_dict is not None and abs(a1 - scr_dict) <= 0.10)
    hf_scr_conseq = (scr_conseq is not None and abs(a2 - scr_conseq) <= 0.10)
    hf_rg = (rg is not None and abs(a1 - rg) <= 0.10)
    hf_rc = (rc is not None and abs(a2 - rc) <= 0.10)
    hf_cds = (cds is not None and abs(a3 - cds) <= 0.08)
    hf_noise = (noise_consol >= 1)
    hf_self_lock = (self_lock["combined_self_lock_count"] >= 1)
    hf_content = (a3c is not None and a3c < 0.55)

    # MIDDLE-BAND signals
    mb_conseq_no_marginal = (_gap(a3, ccs) is not None and _gap(a3, ccs) <= 0)

    gate_detail = {
        "HP1_primary>=0.75_&_unmet>=5": {"pass": hp1, "primary": a3,
                                         "unmet_recall": f"{a3_unmet_c}/{a3_unmet_t}"},
        "HP2_content>=0.70": {"pass": hp2, "content_acc": a3c},
        "HP3_three_way": {"pass": hp3, "combined>dict+0.03": g3a, "gap_vs_dict": _gap(a3, a1),
                          "combined_content>=dict_content": g3b,
                          "combined>consequence+0.30": g3c, "gap_vs_consequence": _gap(a3, a2)},
        "HP4_noncircularity": {"pass": hp4, "scr_dict_in[0.35,0.65]": nc_a, "scr_dict": scr_dict,
                               "random_graph_in[0.35,0.65]": nc_b, "random_graph": rg,
                               "scr_conseq_in[0.40,0.60]": nc_c, "scr_conseq": scr_conseq,
                               "combined_dict_scr_gap>=0.15": nc_e, "gap": _gap(a3, cds),
                               "exclusion_clean": integ["clean"]},
        "HP5_noise==0": {"pass": hp5, "noise_consolidated": noise_consol},
        "HP6_zero_light_verb_self_lock": {"pass": hp6,
                                          "combined_self_lock": self_lock["combined_self_lock_words"],
                                          "dict_alone_lock": self_lock["dict_alone_lock_words"]},
        "HF_primary<=floor": hf_floor, "HF_no_better_than_dict": hf_no_better_than_dict,
        "HF_scr_dict_within_0.10": hf_scr_dict, "HF_scr_conseq_within_0.10": hf_scr_conseq,
        "HF_random_graph_within_0.10": hf_rg, "HF_random_credit_within_0.10": hf_rc,
        "HF_combined_dict_scr_within_0.08": hf_cds, "HF_noise>=1": hf_noise,
        "HF_light_verb_self_lock>=1": hf_self_lock, "HF_content<0.55": hf_content,
        "MB_conseq_no_marginal_value(gap4f<=0)": {"signal": mb_conseq_no_marginal,
                                                  "gap_vs_conseq_scrambled": _gap(a3, ccs)},
    }

    hard_pass = all([hp1, hp2, hp3, hp4, hp5, hp6])
    hard_fail = any([hf_floor, hf_no_better_than_dict, hf_scr_dict, hf_scr_conseq, hf_rg, hf_rc,
                     hf_cds, hf_noise, hf_self_lock, hf_content])

    if hard_fail:
        verdict = "HARD_FAIL"
    elif hard_pass:
        verdict = "HARD_PASS"
    else:
        verdict = "MIDDLE_BAND"

    agg["gate_detail"] = gate_detail
    agg["verdict"] = verdict
    agg["verdict_msg"] = (
        f"{verdict}: 3-way dict={a1}/conseq={a2}/combined={a3} "
        f"(floor={majority_floor}, empty={base_u['empty_overlay_accuracy']}) | "
        f"content dict={a1c}/combined={a3c} | "
        f"gap_vs_dict={_gap(a3, a1)} gap_vs_conseq={_gap(a3, a2)} | "
        f"dict_cov={dict_u['n_dict_hit']}/{dict_u['n_eval_lemmas']}(content {dict_u['n_content_dict_hit']}/16) | "
        f"lv_dict_alone_lock={self_lock['dict_alone_lock_words']} "
        f"lv_combined_self_lock={self_lock['combined_self_lock_words']} | "
        f"noise={noise_consol} | scr_dict={scr_dict} scr_conseq={scr_conseq} "
        f"comb_dict_scr={cds} comb_conseq_scr={ccs} | excl_clean={integ['clean']}")
    agg["summary"] = agg["verdict_msg"][:300]
    return agg


# ------------------------------------------------------------------ discriminator-fires (smoke gate)
def _discriminator_fires(agg):
    """Smoke gate: dictionary priors were actually INJECTED (>=1 lemma got a pseudo-count) AND the
    consequence teacher fired (>=1 window). A vacuous smoke (no dict priors, no teacher) is invalid."""
    passes = agg["arm3_combined"]["bootstrap_curve"]
    max_teacher = max((p["n_windows_with_teacher"] for p in passes), default=0)
    n_priors = agg["dict_coverage"]["n_dict_hit"]
    return {"max_windows_with_teacher": max_teacher, "n_dict_priors_injected": n_priors,
            "fires": (max_teacher > 0 and n_priors > 0)}


# ------------------------------------------------------------------ driver
def run(run_mode):
    t0 = time.perf_counter()
    output_dir = OUTPUT_DIR_FULL if run_mode == "full" else f"{OUTPUT_DIR_FULL}_{run_mode}"
    expected_n_units = 9  # corpus, dict, arm1, arm2, arm3, baseline, dict_controls, conseq_controls, combined_scrambles
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
    """Construct the REAL objects at tiny scale + exercise the real corpus reader + eval loader (F.1
    real_code_path). Assert engine + tool + dictionary self-tests, dictionary_lookup determinism, and
    that the combined injection path runs end-to-end on a tiny real slice."""
    from hdlab.wordnet_polarity_propagation import self_test as _wn_self_test
    eng = _engine_self_test()
    assert eng["determinism_ok"] and eng["dictionary_priors_inject_once_ok"], "engine self-test failed"
    wn = _wn_self_test()
    assert wn["scramble_flips_polarity"], "dictionary non-circularity self-test failed"
    tool = _tool_self_test()
    assert tool["n_priors"] >= 0, "tool self-test failed"
    all_rows, oov_rows = _load_eval()
    assert len(oov_rows) == 36, f"expected 36 OOV items, got {len(oov_rows)}"
    n_met = sum(1 for r in oov_rows if r["gold_outcome_polarity"] == "met")
    assert n_met == 23, f"expected 23 met, got {n_met}"
    eval_lemmas = sorted(set(r["outcome_verb_lemma"] for r in oov_rows))
    # non-overlap assert on the REAL eval + anchor (F.1 real code path + non-circularity gate)
    assert not (set(eval_lemmas) & set(ANCHOR_WORDS)), "non-overlap assert violated (eval lemma in anchor)"
    # dictionary lookups run on the real 33 lemmas + are deterministic
    d1 = _dict_detail(eval_lemmas)
    d2 = _dict_detail(eval_lemmas)
    assert d1 == d2, "dictionary_lookup non-deterministic"
    n_hit = sum(1 for v in d1.values() if v["polarity"] is not None)
    # real corpus reader + a tiny combined run (injection path exercised end-to-end)
    blocks, stats, _excl = _read_corpus_blocks(all_rows, SMOKE_NOVELS)
    assert stats["little_women.clean.txt"]["excluded_lines"] > 0, "exclusion mask empty on real file"
    windows, win_stats = _build_windows(blocks[:20], all_rows)
    rep = learn_corpus_combined([tuple(w) for w in windows], oov_lemmas=eval_lemmas, n_passes=1,
                                signal_mode=SIGNAL_MODE, credit_mode=CREDIT_MODE, register=False)
    assert "dictionary_priors" in rep, "combined path did not attach dictionary_priors"
    _ = _per_verb_combined(oov_rows, rep["dictionary_lookups"], rep["dictionary_priors"],
                           rep["master_counter"], rep["master_grounded"])
    _ = _light_verb_self_lock(rep["master_counter"], rep["master_grounded"], rep["dictionary_priors"])
    _vls.clear_acquired_outcome()
    return {"engine": eng, "wordnet": wn, "tool": tool, "n_oov": len(oov_rows), "n_met": n_met,
            "n_eval_lemmas": len(eval_lemmas), "n_dict_hit": n_hit,
            "excluded_lines_lw": stats["little_women.clean.txt"]["excluded_lines"],
            "tiny_windows": win_stats["n_windows"]}


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
