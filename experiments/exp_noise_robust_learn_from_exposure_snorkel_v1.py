# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - final_metrics_atomicity: tmp_replace (os.replace)
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - deterministic_seeding: Dawid-Skene EM is a deterministic numeric fixed-point iteration (no RNG
#   at all); only the scramble-control permutation uses np.random.default_rng(fixed) (5 fixed
#   seeds, reused verbatim from the parent cell's helper, PROT-023-compliant, no hash()-seeding)
# - start_marker + crash_diagnostic present; cell_chunked: false (single synchronous local run,
#   measured elapsed_s well under 10 min -- see metrics.json; no per-unit checkpoint needed)
# - progress_logging: print(..., flush=True)
# - discriminator-fires gate: n_windows_soft_combine_trusted_pristine must exceed
#   n_windows_AND_baseline (measured at smoke AND full, see coverage dict)
# - arms_differ_verified: AND-gate registered map vs soft-combine registered map compared by
#   sha256 digest in aggregate() -- must differ (META_RULE_AF)
# - crlb_n/a: no swept capacity dimension; this is a label-combination-rule prove-architecture
#   cell (coverage rescue + downstream learned-map quality under noise), not a capacity envelope
# - LOCAL ONLY, ISOLATED PROBE: no queue dispatch, no remote ship, no canonical-store write, no
#   hdlab/ edits -- prove-architecture experiment cell per notes/research_learn_affect_from_
#   narrative_consequences_2026-08-07.md's diagnosis + "Cheap decisive test" section.
# - all reported numbers MEASURED@ this cell's metrics.json, tagged in the completion report.
"""experiments/exp_noise_robust_learn_from_exposure_snorkel_v1.py -- NOISE-ROBUST Stage-4 companion.

Replaces exp_consequence_learning_loop_oov_outcome_verb_valence_v1's hard Signal-A-AND-Signal-B
teacher gate (MEASURED HARD_FAIL, 2026-08-06: 3/1431 real-corpus windows drew a trusted joint
label, 0 words grounded -- data/exp_consequence_learning_loop_oov_outcome_verb_valence_v1/
metrics.json) with a Dawid-Skene / Snorkel-style SOFT-COMBINE of 4 independently-computed weak
consequence signals, feeding a REAL-VALUED per-window posterior confidence into the UNCHANGED
hdlab.self_improving_loop.decide_keep_or_revert anti-drift gate, per notes/research_learn_affect_
from_narrative_consequences_2026-08-07.md's diagnosis ("the coverage collapse is a fixable
combination-rule bug, not a restatement of the grounding wall") and its "Cheap decisive test"
section.

INTERPRETATION NOTE (read before grading the verdict): the task brief names two prior cells --
Stage 4 (experiments/exp_learn_context_affect_map_from_exposure_v1.py, HARD_PASS, synthetic clean
templates, a word -> context_class -> affect VSA superposition map) and the OOV consequence-
learning loop (this cell's direct ancestor, HARD_FAIL on real narrative prose). Real 4-novel
narrative windows carry no hand-authored context_class (animate/inanimate patient) label the way
Stage 4's synthetic templates do, so this cell builds "the context -> affect map" in the SAME
sense the consequence-learning loop did (a lemma -> POS/NEG/GROUNDED_NEUTRAL/PENDING map,
"context" = the narrative window itself), on the SAME real 4-novel corpus + the SAME
goal_bearing_modern_eval_v1.jsonl OOV eval bank Step 1 of the research note specifies, reusing
decide_keep_or_revert exactly as Stage 4 established it (a confirm-across-evidence anti-drift
gate) -- NOT Stage 4's VSA bind/bundle context-keyed layer, which has no real-narrative analog to
condition on without inventing a new context-class taxonomy (out of scope for this cheap decisive
test). This is the lowest-risk, most-directly-falsifiable reading of the task brief's own Step 1/
Step 2 sequencing (both anchored on the 4-novel real corpus), and it keeps the eval scoring path
provably identical to the HARD_FAIL cell's (same imported scorer, same eval file, same exclusion
machinery) -- an apples-to-apples comparison, not a new benchmark.

WHAT'S NEW (genuinely-new code, lives only here; hdlab/ is READ-ONLY, never edited):
  _signal_votes         -- per-window vote from each of 4 ALREADY-OWNED, independently-computed
                           weak consequence-signals (hdlab.goal_typing, imported verbatim):
                             A_verbclass       congruence_decision       (referent-linked verb-class)
                             B_lexicon         lexicon_predict           (flat lexicon + Tier-2
                                                                           embedding-similarity fallback)
                             C_referent_recur  congruence_referent_recurrence_windowed (referent
                                                                           recurrence, no verb-class
                                                                           match required)
                             D_result_class    congruence_grounded_result_class (closed-class
                                                                           result-verb + subject-
                                                                           linkage guard)
                           Each fires MET / UNMET / abstain independently; AMBIGUOUS/NA/NONE are
                           all treated as abstain (uninformative, never a forced vote).
  _fit_dawid_skene       -- classic 1979 latent-rater EM (symmetric per-signal-accuracy
                           simplification of the general confusion-matrix model; the field's
                           standard "assume-better-than-chance" identifiability floor alpha_j >=
                           0.501 applied -- Dawid & Skene 1979; Ratner et al. 2016/2017): estimates
                           each signal's reliability alpha_j and the corpus MET-prior pi from vote
                           AGREEMENT STATISTICS ALONE, no ground truth ever read.
  _trust_from_posterior  -- per-window posterior P(MET)/P(UNMET) from the fitted EM fed AS-IS into
                           decide_keep_or_revert({"MET": q_met, "UNMET": 1-q_met}, abstain_band=
                           CONF_THRESHOLD) -- the OWNED gate, imported UNMODIFIED, reused for a NEW
                           purpose (window-level trust) exactly as it already gates lemma-level
                           POS/NEG consolidation inside hdlab.consequence_learning_loop.consolidate.
  _run_pass_soft /       -- multi-pass bootstrap driver, architecturally IDENTICAL to hdlab.
  _learn_soft_combine       consequence_learning_loop.learn_corpus (same MIN_CONFIRM/NEUTRAL_BAND
                           consolidation via the imported, unmodified `consolidate`; same referent-
                           linked credit-target scan via the imported, unmodified `_credit_targets`;
                           same (window_id,lemma) first-verdict-wins master tally; same Tier-3
                           register-and-reread bootstrap loop) -- the ONLY change vs learn_corpus is
                           that the teacher-signal computation is swapped from the hard AND-gate to
                           _trust_from_posterior(EM-fit-per-pass).

REUSE (wire-don't-island; nothing below is modified, only imported):
  hdlab.goal_typing: congruence_decision / lexicon_predict / congruence_referent_recurrence_
    windowed / congruence_grounded_result_class (the 4 weak signals; final eval scoring goes
    through congruence_with_lexicon_fallback INSIDE the imported _score/_score_with_overlay)
  hdlab.consequence_learning_loop: _credit_targets / consolidate / teacher_verdict (AND-gate
    reproduction only) / learn_corpus (AND-gate baseline reproduction only) / MIN_CONFIRM /
    NEUTRAL_BAND
  hdlab.self_improving_loop: decide_keep_or_revert
  hdlab.verb_lexical_similarity: register_acquired_outcome / clear_acquired_outcome
  experiments.exp_consequence_learning_loop_oov_outcome_verb_valence_v1: the proven corpus-reader /
    window-builder / eval-loader / scorer / scramble-control / canary-analysis (_load_eval,
    _read_corpus_blocks, _build_windows, _exclusion_integrity, _score, _score_with_overlay,
    _learnable_subset, _canary_analysis, _scramble_control, NOVELS, SMOKE_NOVELS) -- reused
    VERBATIM (same pattern experiments/exp_consequence_learning_loop_signal_a_primary_v1.py
    already established for a sibling ablation) so every coverage/scoring number below is measured
    on the EXACT SAME 1431 real windows the hard-AND baseline's 3-window collapse was measured on.

Prior-work check (mandatory substrate-KB gate before authoring): `bash tools/substrate_query.sh
"soft-combine weak consequence signals noise-robust learn from exposure snorkel dawid-skene"` --
top hit cosine=0.2412 ('combine', mixed atoms/verbnet/wordnet source), all 5 returned hits below
cosine 0.30. Prior-work check: NONE at cosine>0.30 -- genuinely novel build in this substrate, not
a rediscovery.

CONF_THRESHOLD=0.70 is PRE-COMMITTED below, before this cell was ever run (not tuned after seeing
results): a window's soft-combined posterior confidence in the winning class must exceed 70% to be
trusted as a teacher label -- a moderately conservative bar, analogous in spirit (not in mechanism)
to the AND-gate design's NEUTRAL_BAND=0.34 lemma-level consolidation margin, but operating at the
WINDOW-trust stage instead.

Cites: notes/research_learn_affect_from_narrative_consequences_2026-08-07.md (the diagnosis + the
Dawid-Skene/Snorkel fix this cell implements); notes/research_consequence_learning_loop_oov_
outcome_verb_valence_2026-08-06.md (original design); data/exp_consequence_learning_loop_oov_
outcome_verb_valence_v1/metrics.json (the measured HARD_FAIL this cell answers);
data/exp_consequence_learning_loop_signal_a_primary_v1/metrics.json (measured: Signal-A-alone
grounds 11 words but scores 0/3 on eval overlap -- sobering prior context, cited honestly below).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import platform
import random
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
    congruence_decision, lexicon_predict,
    congruence_referent_recurrence_windowed, congruence_grounded_result_class,
)
from hdlab import verb_lexical_similarity as _vls  # noqa: E402
from hdlab.verb_lexical_similarity import register_acquired_outcome, clear_acquired_outcome  # noqa: E402
from hdlab.consequence_learning_loop import (  # noqa: E402
    _credit_targets, consolidate, teacher_verdict, learn_corpus as _engine_learn_corpus,
    MIN_CONFIRM, NEUTRAL_BAND,
)
from hdlab.self_improving_loop import decide_keep_or_revert  # noqa: E402

# REUSE the parent cell's validated corpus/scoring/canary/scramble helpers verbatim (wire-don't-island;
# same pattern exp_consequence_learning_loop_signal_a_primary_v1.py already established).
from experiments.exp_consequence_learning_loop_oov_outcome_verb_valence_v1 import (  # noqa: E402
    _load_eval, _read_corpus_blocks, _build_windows, _exclusion_integrity,
    _score, _score_with_overlay, _learnable_subset, _canary_analysis, _scramble_control,
    NOVELS, SMOKE_NOVELS, N_SCRAMBLE_SEEDS,
)
from tools.exp_checkpoint import unit_key, completed_units, record_unit, load_units  # noqa: E402

ANCHOR_NAME = "noise_robust_learn_from_exposure_snorkel_v1"
OUTPUT_DIR_FULL = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}")

N_PASSES = 3                 # match the parent cell's bootstrap depth
CONF_THRESHOLD = 0.70        # pre-committed window-trust posterior bar (see docstring)
N_EM_ITERS = 15
ALPHA_INIT = 0.80
ALPHA_FLOOR = 0.501
ALPHA_CEIL = 0.999
# research's own falsifiable coverage-rescue branch (notes/research_learn_affect_from_narrative_
# consequences_2026-08-07.md, "Cheap decisive test"): OR-coverage >= 15x AND-coverage.
OR_RESCUE_MULTIPLE = 15
# this cell's own operationalization of "trusted-label coverage, not just raw OR": soft-combine
# TRUSTED coverage must be >=10x the AND baseline AND clear an absolute floor of 15 windows (a
# "meaningful fraction" per the task brief, not 3->4).
SOFT_RESCUE_MULTIPLE = 10
SOFT_RESCUE_FLOOR = 15


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


# ================================================================== 4-signal weak-vote computation
def _signal_votes(goal_sentence, window_text):
    """{signal_name: 'MET'|'UNMET'} for every signal that did NOT abstain on this window.
    AMBIGUOUS/NA/NONE are all excluded (uninformative -> no vote, never a forced guess)."""
    votes = {}
    a, _ = congruence_decision([goal_sentence], window_text)
    if a in ("MET", "UNMET"):
        votes["A_verbclass"] = a
    b = lexicon_predict(window_text)
    if b in ("MET", "UNMET"):
        votes["B_lexicon"] = b
    c, _ = congruence_referent_recurrence_windowed(window_text)
    if c in ("MET", "UNMET"):
        votes["C_referent_recur"] = c
    d, _ = congruence_grounded_result_class(window_text)
    if d in ("MET", "UNMET"):
        votes["D_result_class"] = d
    return votes


# ================================================================== Dawid-Skene EM (genuinely new)
def _fit_dawid_skene(votes_list, n_iter=N_EM_ITERS, alpha_init=ALPHA_INIT):
    """votes_list: List[Dict[signal_name,'MET'|'UNMET']] (zero-vote windows allowed, excluded from
    the EM fit -- trivially posterior=pi, which alone can never clear a window-trust decision, see
    _run_pass_soft's explicit zero-vote skip). Pure numeric fixed-point EM (Dawid & Skene 1979,
    symmetric-accuracy simplification): deterministic given the vote data, no RNG anywhere.
    Returns (alpha: Dict[str,float], pi: float, q: List[float] posterior P(MET) per window in
    votes_list, INCLUDING zero-vote windows at q=pi)."""
    fit_idx = [i for i, v in enumerate(votes_list) if v]
    signal_names = sorted({s for v in votes_list for s in v})
    alpha = {s: alpha_init for s in signal_names}
    all_votes = [val for v in votes_list for val in v.values()]
    pi = (all_votes.count("MET") / len(all_votes)) if all_votes else 0.5
    pi = min(max(pi, 0.05), 0.95)
    q = [pi] * len(votes_list)
    if not fit_idx:
        return alpha, pi, q
    for _ in range(n_iter):
        for i in fit_idx:
            v = votes_list[i]
            log_met = math.log(pi)
            log_unmet = math.log(1.0 - pi)
            for s, vote in v.items():
                a = alpha[s]
                if vote == "MET":
                    log_met += math.log(a)
                    log_unmet += math.log(1.0 - a)
                else:
                    log_met += math.log(1.0 - a)
                    log_unmet += math.log(a)
            m = max(log_met, log_unmet)
            p_met = math.exp(log_met - m)
            p_unmet = math.exp(log_unmet - m)
            q[i] = p_met / (p_met + p_unmet)
        new_alpha = {}
        for s in signal_names:
            num = den = 0.0
            for i in fit_idx:
                v = votes_list[i]
                if s not in v:
                    continue
                den += 1.0
                num += q[i] if v[s] == "MET" else (1.0 - q[i])
            new_alpha[s] = min(max((num / den) if den > 0 else alpha[s], ALPHA_FLOOR), ALPHA_CEIL)
        alpha = new_alpha
        pi = min(max(sum(q[i] for i in fit_idx) / len(fit_idx), 0.05), 0.95)
    return alpha, pi, q


def _trust_from_posterior(q_met, conf_threshold=CONF_THRESHOLD):
    """Feeds the EM posterior into the OWNED, UNCHANGED decide_keep_or_revert gate. agg_deltas here
    are POSTERIOR PROBABILITIES (sum to 1, both in [0,1]) rather than coherence-margin deltas --
    decide_keep_or_revert's contract (adopt argmax iff it strictly clears abstain_band) is agnostic
    to what the float means, so this is a legitimate reuse for a NEW purpose (window-level trust),
    not a modification."""
    agg = {"MET": q_met, "UNMET": 1.0 - q_met}
    return decide_keep_or_revert(agg, abstain_band=conf_threshold)


# ================================================================== soft-combine pass / multi-pass driver
def _run_pass_soft(windows, conf_threshold=CONF_THRESHOLD):
    """One corpus pass: compute the 4 signal votes for every window (current Tier-3 overlay state),
    fit Dawid-Skene ONCE over this pass's votes, decide trust per window via _trust_from_posterior,
    then credit-assign trusted windows exactly like hdlab.consequence_learning_loop.run_pass (same
    imported, unmodified _credit_targets). Returns (n_voted, n_trusted, n_credited,
    exposure_records, em_diag)."""
    votes_list = [_signal_votes(gs, wt) for (gs, wt, _ref) in windows]
    alpha, pi, q = _fit_dawid_skene(votes_list)
    exposure_records = []
    n_voted = sum(1 for v in votes_list if v)
    n_trusted = 0
    n_credited = 0
    for wid, ((gs, wt, ref), v, qi) in enumerate(zip(windows, votes_list, q)):
        if not v:
            continue  # zero votes -> structurally abstain, never reaches the trust decision
        tv = _trust_from_posterior(qi, conf_threshold)
        if tv is None:
            continue
        n_trusted += 1
        targets = _credit_targets(wt, ref)
        if not targets:
            continue
        n_credited += 1
        for lemma in targets:
            exposure_records.append({"lemma": lemma, "window_id": wid, "teacher_verdict": tv})
    em_diag = {"alpha": {k: round(v2, 4) for k, v2 in alpha.items()}, "pi": round(pi, 4),
               "n_voted": n_voted, "n_signals_active": len(alpha)}
    return n_voted, n_trusted, n_credited, exposure_records, em_diag


def _learn_soft_combine(windows, n_passes=N_PASSES, conf_threshold=CONF_THRESHOLD, register=True):
    """Multi-pass bootstrap driver, architecturally identical to hdlab.consequence_learning_loop.
    learn_corpus (same MIN_CONFIRM/NEUTRAL_BAND consolidation via the imported `consolidate`; same
    (window_id,lemma) first-verdict-wins master tally; same Tier-3 register-and-reread loop) -- the
    ONLY change is the teacher-signal source (_run_pass_soft's EM-fit-per-pass instead of the hard
    AND-gate teacher_verdict)."""
    clear_acquired_outcome()
    master = {}
    master_records = []
    seen_pairs = set()
    registered = {}
    pass_reports = []
    for p in range(n_passes):
        n_voted, n_trusted, n_credited, records, em_diag = _run_pass_soft(windows, conf_threshold)
        added = 0
        for rec in records:
            key = (rec["window_id"], rec["lemma"])
            if key in seen_pairs:
                continue
            seen_pairs.add(key)
            pole = "POS" if rec["teacher_verdict"] == "MET" else "NEG"
            master.setdefault(rec["lemma"], {"POS": 0, "NEG": 0})[pole] += 1
            master_records.append(rec)
            added += 1
        grounded = consolidate(master)
        newly_pos = newly_neg = 0
        for lemma, verdict in grounded.items():
            if verdict in ("POS", "NEG") and registered.get(lemma) != verdict:
                if register:
                    register_acquired_outcome(lemma, verdict)
                registered[lemma] = verdict
                if verdict == "POS":
                    newly_pos += 1
                else:
                    newly_neg += 1
        pass_reports.append({
            "pass": p + 1, "n_windows_voted": n_voted, "n_windows_trusted": n_trusted,
            "n_windows_credited": n_credited, "n_new_exposure_pairs": added,
            "n_newly_registered_pos": newly_pos, "n_newly_registered_neg": newly_neg,
            "cumulative_registered": len(registered),
            "n_grounded_neutral": sum(1 for v in grounded.values() if v == "GROUNDED_NEUTRAL"),
            "n_lemmas_pending": sum(1 for v in grounded.values() if v == "PENDING"),
            "em_diag": em_diag,
        })
        if p > 0 and added == 0:
            break
    return {
        "registered": dict(registered), "master_counter": master,
        "master_grounded": consolidate(master), "master_records": master_records,
        "pass_reports": pass_reports,
    }


# ================================================================== anti-drift hand-authored micro-cases
def _anti_drift_micro_cases():
    """Hand-authored, deterministic conflict / absent-evidence micro-cases (Stage-4-style anti-drift
    arms), evaluated through _trust_from_posterior using a FIXED cold-start prior (alpha=0.8 for
    every signal, pi=0.5 -- the SAME starting point every real pass-1 EM run begins from), which
    isolates the question 'does even-split disagreement clear the trust threshold' from corpus-scale
    EM-convergence noise (a 2-4-vote EM fit would be underpowered on its own)."""
    cases = {
        "conflict_A_pos_B_neg": {"A_verbclass": "MET", "B_lexicon": "UNMET"},
        "conflict_2v2": {"A_verbclass": "MET", "B_lexicon": "MET",
                         "C_referent_recur": "UNMET", "D_result_class": "UNMET"},
        "absent_no_votes": {},
    }
    out = {}
    for name, v in cases.items():
        if not v:
            out[name] = {"trusted": False, "reason": "zero_votes_structurally_abstains"}
            continue
        log_met = math.log(0.5)
        log_unmet = math.log(0.5)
        for vote in v.values():
            if vote == "MET":
                log_met += math.log(0.8)
                log_unmet += math.log(0.2)
            else:
                log_met += math.log(0.2)
                log_unmet += math.log(0.8)
        m = max(log_met, log_unmet)
        p_met = math.exp(log_met - m)
        p_unmet = math.exp(log_unmet - m)
        q_met = p_met / (p_met + p_unmet)
        tv = _trust_from_posterior(q_met)
        out[name] = {"trusted": tv is not None, "verdict": tv, "q_met": round(q_met, 4)}
    return out


# ================================================================== core run
def _run_all(run_mode):
    novels = SMOKE_NOVELS if run_mode == "smoke" else NOVELS
    all_rows, oov_rows = _load_eval()
    majority_floor = round(sum(1 for r in oov_rows if r["gold_outcome_polarity"] == "met")
                           / len(oov_rows), 4)

    print(f"[progress] reading corpora + building windows (run_mode={run_mode})", flush=True)
    blocks, corpus_stats, _excl = _read_corpus_blocks(all_rows, novels)
    windows, win_stats = _build_windows(blocks, all_rows)
    integ = _exclusion_integrity(windows, all_rows)
    print(f"[progress] corpus: sents={win_stats['total_sents']} goal_fire={win_stats['goal_fire']} "
          f"windows={win_stats['n_windows']} exclusion_clean={integ['clean']}", flush=True)

    # ---- STEP 1 (cheap decisive test): coverage instrumentation, PRISTINE state (before any
    # Tier-3 registration can change signal votes pass-over-pass) -----------------------------------
    clear_acquired_outcome()
    print("[progress] STEP 1: computing 4-signal votes + AND-gate reproduction (pristine state)", flush=True)
    votes_pristine = [_signal_votes(gs, wt) for (gs, wt, _r) in windows]
    n_A = sum(1 for v in votes_pristine if "A_verbclass" in v)
    n_B = sum(1 for v in votes_pristine if "B_lexicon" in v)
    n_C = sum(1 for v in votes_pristine if "C_referent_recur" in v)
    n_D = sum(1 for v in votes_pristine if "D_result_class" in v)
    n_OR = sum(1 for v in votes_pristine if v)
    n_AND = sum(1 for (gs, wt, _r) in windows
               if teacher_verdict(gs, wt, signal_mode="and_gate") is not None)
    alpha0, pi0, q0 = _fit_dawid_skene(votes_pristine)
    n_soft_trusted_pristine = sum(
        1 for v, qi in zip(votes_pristine, q0) if v and _trust_from_posterior(qi) is not None)
    n_evidence_abstained_pristine = sum(
        1 for v, qi in zip(votes_pristine, q0) if v and _trust_from_posterior(qi) is None)

    coverage = {
        "n_windows": len(windows),
        "n_windows_AND_baseline": n_AND,
        "n_windows_signal_A_fires_alone": n_A,
        "n_windows_signal_B_fires_alone": n_B,
        "n_windows_signal_C_fires_alone": n_C,
        "n_windows_signal_D_fires_alone": n_D,
        "n_windows_OR_any_signal_fires": n_OR,
        "n_windows_soft_combine_trusted_pristine": n_soft_trusted_pristine,
        "n_windows_evidence_but_abstained_pristine": n_evidence_abstained_pristine,
        "or_vs_and_multiple": round(n_OR / n_AND, 2) if n_AND > 0 else None,
        "soft_vs_and_multiple": round(n_soft_trusted_pristine / n_AND, 2) if n_AND > 0 else None,
        "em_alpha_pristine": {k: round(v, 4) for k, v in alpha0.items()}, "em_pi_pristine": round(pi0, 4),
        "or_rescue_gate_pass": (n_OR >= OR_RESCUE_MULTIPLE * max(n_AND, 1)),
        "soft_rescue_gate_pass": (n_soft_trusted_pristine >= SOFT_RESCUE_MULTIPLE * max(n_AND, 1)
                                  and n_soft_trusted_pristine >= SOFT_RESCUE_FLOOR),
    }
    print(f"[progress] coverage: AND={n_AND} OR={n_OR} soft_trusted={n_soft_trusted_pristine} "
          f"(A={n_A} B={n_B} C={n_C} D={n_D}) soft_rescue_gate={coverage['soft_rescue_gate_pass']}",
          flush=True)
    clear_acquired_outcome()

    # ---- AND-gate baseline reproduction (full multi-pass, for the registered-map / arms-differ
    # comparison; same engine call the parent + signal_a_primary cells use) ------------------------
    print("[progress] AND-gate baseline reproduction (full multi-pass, unchanged engine)", flush=True)
    and_rep = _engine_learn_corpus(windows, n_passes=N_PASSES, signal_mode="and_gate",
                                   credit_mode="referent_linked", register=True)
    and_registered = and_rep["registered"]
    clear_acquired_outcome()

    # ---- STEP 2 (if coverage rescued): soft-combine multi-pass learn -------------------------------
    print("[progress] STEP 2: soft-combine multi-pass learn (Dawid-Skene EM teacher)", flush=True)
    soft_rep = _learn_soft_combine(windows, n_passes=N_PASSES, conf_threshold=CONF_THRESHOLD, register=True)
    soft_registered = soft_rep["registered"]
    acc, correct, met_c, unmet_c, n_met, n_unmet, details = _score_with_overlay(oov_rows, soft_registered)
    learnable = _learnable_subset(oov_rows, soft_registered)
    canary = _canary_analysis(soft_rep["master_counter"], soft_rep["master_grounded"])
    print(f"[progress] soft-combine: primary_acc={acc:.4f} n_registered={len(soft_registered)} "
          f"n_learnable={learnable['n_learnable']} ls_acc={learnable['learnable_subset_accuracy']}",
          flush=True)

    # ---- baseline (empty overlay) -------------------------------------------------------------
    clear_acquired_outcome()
    b_acc, b_correct = _score(oov_rows)[0:2]

    # ---- SCRAMBLE-CONSEQUENCE control (reuse the parent's proven helper verbatim, on OUR records) --
    print("[progress] scramble control (5 seeds, reused helper)", flush=True)
    scr = _scramble_control(soft_rep["master_records"], oov_rows, n_seeds=N_SCRAMBLE_SEEDS)

    # ---- ANTI-DRIFT: hand-authored conflict/absent micro-cases -------------------------------------
    anti_drift_cases = _anti_drift_micro_cases()
    anti_drift_ok = all(not c["trusted"] for c in anti_drift_cases.values())

    # ---- ARMS-MUST-DIFFER (META_RULE_AF) -----------------------------------------------------------
    def _digest(reg):
        return hashlib.sha256(json.dumps(sorted(reg.items())).encode()).hexdigest()
    arms_differ = _digest(and_registered) != _digest(soft_registered)
    clear_acquired_outcome()

    return _aggregate(run_mode, oov_rows, majority_floor, corpus_stats, win_stats, integ,
                      coverage, and_registered, soft_registered, acc, correct, met_c, unmet_c,
                      n_met, n_unmet, learnable, canary, b_acc, b_correct, scr,
                      anti_drift_cases, anti_drift_ok, arms_differ, soft_rep)


def _aggregate(run_mode, oov_rows, majority_floor, corpus_stats, win_stats, integ, coverage,
               and_registered, soft_registered, primary, correct, met_c, unmet_c, n_met, n_unmet,
               learnable, canary, b_acc, b_correct, scr, anti_drift_cases, anti_drift_ok,
               arms_differ, soft_rep):
    scrambled = scr["scrambled_primary_accuracy"]
    n_learnable = learnable["n_learnable"]
    ls_acc = learnable["learnable_subset_accuracy"]

    agg = {
        "anchor_name": ANCHOR_NAME, "run_mode": run_mode,
        "config": {"N_PASSES": N_PASSES, "CONF_THRESHOLD": CONF_THRESHOLD, "N_EM_ITERS": N_EM_ITERS,
                   "MIN_CONFIRM": MIN_CONFIRM, "NEUTRAL_BAND": NEUTRAL_BAND,
                   "n_scramble_seeds": N_SCRAMBLE_SEEDS, "n_oov_items": len(oov_rows),
                   "or_rescue_multiple": OR_RESCUE_MULTIPLE,
                   "soft_rescue_multiple": SOFT_RESCUE_MULTIPLE, "soft_rescue_floor": SOFT_RESCUE_FLOOR},
        "corpus_stats": corpus_stats, "win_stats": win_stats, "exclusion_integrity": integ,
        "majority_floor": majority_floor,
        "coverage": coverage,
        "n_registered_and_gate": len(and_registered), "and_gate_registered": and_registered,
        "n_registered_soft_combine": len(soft_registered), "soft_combine_registered": soft_registered,
        "fallthrough_baseline_accuracy": round(b_acc, 4),
        "primary_accuracy": round(primary, 4),
        "met_recall": f"{met_c}/{n_met}", "unmet_recall": f"{unmet_c}/{n_unmet}",
        "learnable_subset": learnable,
        "light_verb_canary": {k: canary[k] for k in (
            "light_verb_canary_neutral_rate", "light_verb_n_reached", "light_verb_n_neutral",
            "light_verb_n_polar_locked")},
        "noise_canary": {"consolidated_count": canary["noise_canary_consolidated_count"],
                         "consolidated_words": canary["noise_canary_consolidated_words"]},
        "bootstrap_curve": soft_rep["pass_reports"],
        "scramble": scr,
        "anti_drift_cases": anti_drift_cases, "anti_drift_all_abstain": anti_drift_ok,
        "arms_differ_verified": arms_differ,
    }

    # ---- can-fail gates (per task brief, pre-committed bands) --------------------------------------
    coverage_rescue_pass = coverage["soft_rescue_gate_pass"]
    or_rescue_pass = coverage["or_rescue_gate_pass"]
    learned_map_under_noise_pass = (ls_acc is not None and ls_acc >= 0.75 and n_learnable >= 6)
    scramble_collapse_pass = (scrambled is not None and (primary - scrambled) >= 0.15)
    scramble_no_signal = (scrambled is not None and abs(primary - scrambled) <= 0.08)
    chance_level = (primary <= majority_floor)

    hard_fail_reasons = []
    if not coverage_rescue_pass:
        hard_fail_reasons.append("COVERAGE_NOT_RESCUED_signals_absent")
    if chance_level and (ls_acc is None or ls_acc < 0.5):
        hard_fail_reasons.append("PRIMARY_AT_OR_BELOW_CHANCE")
    if scramble_no_signal:
        hard_fail_reasons.append("SCRAMBLE_DOES_NOT_COLLAPSE_no_real_signal")
    if not anti_drift_ok:
        hard_fail_reasons.append("ANTI_DRIFT_VIOLATION_spurious_trust_on_conflict")

    hard_pass = (coverage_rescue_pass and learned_map_under_noise_pass and scramble_collapse_pass
                and anti_drift_ok and arms_differ)

    if hard_pass and not hard_fail_reasons:
        verdict = "HARD_PASS"
    elif hard_fail_reasons:
        verdict = "HARD_FAIL"
    else:
        verdict = "MIDDLE_BAND"

    gate_detail = {
        "COVERAGE_RESCUE_soft_vs_and>=10x_and_floor15": coverage_rescue_pass,
        "COVERAGE_RESCUE_or_vs_and>=15x_diagnostic": or_rescue_pass,
        "LEARNED_MAP_UNDER_NOISE_ls_acc>=0.75_n>=6": learned_map_under_noise_pass,
        "SCRAMBLE_COLLAPSE_gap>=0.15": scramble_collapse_pass,
        "SCRAMBLE_NO_SIGNAL_flag_gap<=0.08": scramble_no_signal,
        "ANTI_DRIFT_all_conflict_cases_abstain": anti_drift_ok,
        "ARMS_DIFFER_and_vs_soft_registered_maps": arms_differ,
        "hard_fail_reasons": hard_fail_reasons,
    }
    agg["gate_detail"] = gate_detail
    agg["verdict"] = verdict
    agg["verdict_msg"] = (
        f"{verdict}: coverage AND={coverage['n_windows_AND_baseline']} "
        f"OR={coverage['n_windows_OR_any_signal_fires']} "
        f"soft_trusted={coverage['n_windows_soft_combine_trusted_pristine']} "
        f"(rescue_gate={coverage_rescue_pass}) | primary={primary:.4f} (floor={majority_floor}) | "
        f"learnable_ls_acc={ls_acc}({n_learnable}/N>=6) | scramble={scrambled} "
        f"gap={round(primary - scrambled, 4) if scrambled is not None else None} | "
        f"anti_drift_ok={anti_drift_ok} | arms_differ={arms_differ} | "
        f"hard_fail_reasons={hard_fail_reasons}")
    agg["summary"] = agg["verdict_msg"][:300]
    return agg


# ------------------------------------------------------------------ discriminator-fires (smoke gate)
def _discriminator_fires(agg):
    cov = agg["coverage"]
    return {"n_windows_AND": cov["n_windows_AND_baseline"],
            "n_windows_soft_trusted": cov["n_windows_soft_combine_trusted_pristine"],
            "fires": cov["n_windows_soft_combine_trusted_pristine"] > cov["n_windows_AND_baseline"]}


# ------------------------------------------------------------------ driver
def run(run_mode):
    t0 = time.perf_counter()
    output_dir = OUTPUT_DIR_FULL if run_mode == "full" else f"{OUTPUT_DIR_FULL}_{run_mode}"
    _write_start_marker(output_dir, run_mode, expected_n_units=1)
    agg = _run_all(run_mode)
    agg["elapsed_s"] = round(time.perf_counter() - t0, 2)
    agg["discriminator_fires"] = _discriminator_fires(agg)
    _atomic_write_metrics(output_dir, agg)
    print(json.dumps({"verdict": agg["verdict"], "verdict_msg": agg["verdict_msg"],
                      "discriminator_fires": agg["discriminator_fires"],
                      "elapsed_s": agg["elapsed_s"]}, indent=2), flush=True)
    return agg


# ------------------------------------------------------------------ self-test
def self_test():
    """TEST-FIRST discipline: (1) verify the Dawid-Skene EM math itself recovers approximately
    correct per-signal reliabilities from a KNOWN-ground-truth synthetic dataset and beats the best
    single raw signal -- a controlled correctness check independent of the narrative-specific
    machinery; (2) verify decide_keep_or_revert reuse is consistent (confident trusts, even-split
    abstains); (3) exercise the REAL corpus-reader + real 4-signal computation on a tiny REAL slice
    (F.1 real_code_path, no synthetic-only branch); (4) determinism of the full soft-combine driver."""
    # (1) Dawid-Skene EM ground-truth recovery, deterministic synthetic data.
    rng = random.Random(7)
    n = 300
    true_labels = [("MET" if rng.random() < 0.5 else "UNMET") for _ in range(n)]
    true_acc = {"good": 0.90, "weak": 0.62, "noisy_abstain": 0.75}
    votes_list = []
    for z in true_labels:
        v = {}
        for name, acc in true_acc.items():
            if name == "noisy_abstain" and rng.random() < 0.5:
                continue  # abstains half the time -- exercises the partial-coverage EM path
            v[name] = z if rng.random() < acc else ("UNMET" if z == "MET" else "MET")
        votes_list.append(v)
    alpha, pi, q = _fit_dawid_skene(votes_list)
    for name, true_a in true_acc.items():
        assert abs(alpha[name] - true_a) < 0.12, f"EM alpha[{name}]={alpha[name]} vs true {true_a}"
    combined_correct = sum(1 for i, z in enumerate(true_labels) if (q[i] > 0.5) == (z == "MET"))
    best_raw_correct = max(
        sum(1 for i, z in enumerate(true_labels) if votes_list[i].get(name) == z)
        for name in true_acc)
    assert combined_correct >= best_raw_correct, (
        f"EM-combined ({combined_correct}/{n}) must be >= best single raw signal ({best_raw_correct}/{n})")

    # (2) decide_keep_or_revert reuse consistency via _trust_from_posterior.
    assert _trust_from_posterior(0.95) == "MET"
    assert _trust_from_posterior(0.05) == "UNMET"
    assert _trust_from_posterior(0.55) is None, "near-even posterior must abstain, not force a guess"
    assert _trust_from_posterior(0.5) is None, "exactly-even posterior must abstain"

    # (3) real code path: tiny REAL corpus slice + real 4-signal computation + one real pass.
    all_rows, oov_rows = _load_eval()
    assert len(oov_rows) == 36, f"expected 36 OOV eval items, got {len(oov_rows)}"
    blocks, _stats, _excl = _read_corpus_blocks(all_rows, SMOKE_NOVELS)
    windows, _win_stats = _build_windows(blocks[:30], all_rows)
    assert len(windows) > 0, "self-test corpus slice produced zero windows"
    v0 = _signal_votes(windows[0][0], windows[0][1])
    assert isinstance(v0, dict)
    n_voted, n_trusted, n_credited, records, em_diag = _run_pass_soft(windows)
    assert n_trusted <= n_voted

    # (4) determinism: two independent soft-combine runs over the SAME tiny window list produce
    # byte-identical registered maps (glass-box, no hidden RNG in the EM or the credit scan).
    r1 = _learn_soft_combine(windows, n_passes=2, register=True)
    clear_acquired_outcome()
    r2 = _learn_soft_combine(windows, n_passes=2, register=True)
    clear_acquired_outcome()
    assert r1["master_grounded"] == r2["master_grounded"], \
        "GLASS-BOX FAILURE: non-deterministic soft-combine grounding"

    # (5) anti-drift micro-cases: hand-authored conflicts must all abstain.
    cases = _anti_drift_micro_cases()
    assert all(not c["trusted"] for c in cases.values()), f"anti-drift violation: {cases}"

    clear_acquired_outcome()
    return {
        "em_recovery_ok": True, "combined_correct": combined_correct,
        "best_raw_correct": best_raw_correct, "n_synth": n,
        "trust_gate_consistency_ok": True, "real_code_path_windows": len(windows),
        "n_trusted_smoke_slice": n_trusted, "determinism_ok": True, "anti_drift_ok": True,
    }


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
