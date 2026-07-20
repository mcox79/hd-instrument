"""EVENT-OUTCOME-DENSITY PATIENT-SIGNAL PROBE v2 -- POWER FIX (design-gate + smoke; exp_dev cycle 2026-07-20).

WHY v2: v1 (experiments/exp_event_outcome_density_patient_signal_probe_v1.py, data/exp_event_outcome_
density_patient_signal_probe_v1/metrics.json) was FAIR (within-genre density tertiles, token-matched,
scrambled must-fail control, animacy-invariance validity gate) but POWER-STARVED: the ONLY discriminator
was the frozen LCCP hand-gold pick_gold rate over n_multi=21 gold multi-candidate instances. MEASURED
result: gap(HIGH-LOW)=0.0000 exactly, bootstrap SE~0.108-0.109 (n_boot=2000) -- a gap of even 0.08 (the
pre-registered HARD_PASS bar) sits at < 1 SE. This is UNINFORMATIVE, not a refutation (recorded honestly
in preregs/event_outcome_density_patient_signal_probe_v1.md "HONEST BOUND").

ROOT CAUSE OF THE POWER PROBLEM (MEASURED this cycle, not assumed): growing the BACKGROUND corpus does
NOT fix this. v1's own TEXT8_XGENRE reference arm already used 74,000 background tokens (8x the primary
LOW/MED/HIGH tiers) and produced the IDENTICAL 0.3810 pick_gold rate -- bit-for-bit tied with the 9K-token
arms. The bottleneck is the EVAL side: pick_gold is a Bernoulli rate over n=21 independent gold trials;
SE ~ 1/sqrt(n) regardless of how much background text feeds the density signal. Confirmed by directly
reading data/gold_mcguffey_lccp_argstruct_v1.json this cycle: only 7 of the McGuffey Third Reader's 79
lessons are hand-annotated (100 pos instances total, 57 reader-scoreable, 21 multi-candidate) -- expanding
that is a NEW hand-annotation labor task, not a corpus-fetch, and is NOT done in this design+smoke cycle
(flagged as a possible future lever, not required here).

THE FIX (label-free, needs NO new annotation, NO new corpus fetch -- per notes/research_brain_building_
event_plausibility_web_2026-07-20.md section (b)/(c) and notes/research_plausibility_web_engineering_
resources_adoptable_foundation_2026-07-20.md section 3): a Chambers & Jurafsky (2008/2010)-style PSEUDO-
DISAMBIGUATION probe. For every occurrence of a Levin causative-inchoative verb in a HELD-OUT slice of the
McGuffey Third Reader (the 72 of 79 lessons NEVER used in the hand-gold set -- MEASURED this cycle:
n=110 credited (verb, true-patient) instances, vs the n=21 multi-candidate hand-gold trials -- a ~5x
increase in the PRIMARY discriminator's trial count, achieved with ZERO new data and ZERO new
annotation), the OBSERVED adjacent noun IS the "true" patient (no semantic judgment needed -- this is
the classic label-free pseudo-disambiguation move: the corpus occurrence itself defines ground truth,
the corrupted competitor is a same-slot filler sampled from a DIFFERENT instance). Does the
density-informed patient-affinity score rank the TRUE observed patient above a randomly-substituted
CORRUPTED patient more often than chance (50%)? This is the PRIMARY discriminator in v2. The original
n=21 LCCP hand-gold pick_gold rate is RETAINED as a SECONDARY / legacy continuity check (explicitly
flagged underpowered on its own, per its own v1 pre-reg), not the primary call.

DENSITY METRIC + BACKGROUND ARMS: UNCHANGED from v1 (imported, not re-implemented) -- hits-per-1000-tokens
of the CITED Levin (1993) causative-inchoative lexicon (CAUSE_INCHOATIVE, ~45 lemmas) over McGuffey
Primer/First/Second/Fourth Reader (Third Reader excluded -- it is the eval corpus for BOTH the legacy
hand-gold AND the new held-out CJ probe). GENRE CONFOUND control: PRIMARY comparison stays WITHIN the
McGuffey graded-reader series (same author/era/register family); this is option (a) of the fairness-guard
menu (within-source density stratification) -- the ONLY option achievable with ZERO new data this cycle.
TEXT8_XGENRE / LITBANK_XGENRE remain explicitly-flagged, NOT-clean, reference-only arms (unchanged from
v1), reported for context, never for the primary call.

CAPACITY TIERS (BabyLM-style fixed-budget-vary-composition; MEASURED corpus-availability constraint, not
guessed): direct cumulative-token measurement this cycle over the full non-eval McGuffey pool (73,451
scoreable tokens across 248 lessons) shows the bottom 83 lessons by density-rank are ALL density=0.0
exactly (a real floor, not "low-but-nonzero"), totaling 9,103 raw tokens -- that sets the natural ceiling
for a "pure zero-density LOW arm" at ANY budget above ~9.1K without diluting LOW's density upward (bottom
101 lessons already carry density>=2.70). HIGH has abundant headroom (top 41 lessons alone = 10,112 tokens
at density>=16.5). Capacity tiers = FIXED TOKEN BUDGETS B in {3000, 6000, 9000}, LOW_B = bottom-ranked
(all density=0.0) lessons, fixed-seed-shuffled + prefix-truncated to B tokens; HIGH_B = top-ranked lessons,
same procedure. This tests whether the density effect (if any) holds/scales across budget, per HARD-PASS
criterion (i) "no density x capacity interaction" -- OR is an artifact of a specific small-sample budget.
(The v1 tercile LOW/MED/HIGH design, ~9.1-9.5K tokens/arm, is ALSO retained verbatim as a flagship
replication-continuity block, reusing v1's exact functions unchanged.)

DENSER-!=-EASIER CONTROL (general-syntax-analog; no BLiMP fetch needed): the SAME Chambers-Jurafsky
mechanism is ALSO run on the AGENT slot of the SAME held-out transitive Levin-verb instances (true
preceding-subject vs a corrupted swap), scored under the AFFECTEDNESS-ONLY component of the score
function (patient_affinity alone, no animacy term -- isolates exactly the density-dependent piece). Since
patient_affinity is a theory of "has this noun been seen as a change-of-state AFFECTED argument", NOT a
theory of agency, a HARD-PASS requires density to help PATIENT discrimination specifically and NOT (or
much less) AGENT discrimination -- if density helps both equally, that means "denser corpus = generically
easier to guess any salient noun", not "denser corpus = more affectedness content" (HARD-FAIL criterion
(iii)). This directly operationalizes the "concentrated on affectedness metrics, not general syntax"
requirement without staging BLiMP (flagged as a full-run nice-to-have, not required).

PERPLEXITY NUISANCE-COVARIATE DIAGNOSTIC (cheap analog of "regress out perplexity"): a closed-form add-1
bigram LM fit on each background arm (LOW_B / HIGH_B) is evaluated on the SAME held-out eval sentences
(the ones carrying the credited CJ instances) to report per-arm perplexity. This is a DIAGNOSTIC, not a
full regression (too few arms/tiers for a real slope fit at this scale) -- reported honestly as such. The
diff-in-difference between patient-slot gain and agent-slot gain (see above) is the actual mechanism doing
the "controls for generic difficulty" work in this cheap design; perplexity is reported as a secondary
sanity check that LOW_B / HIGH_B aren't wildly different in generic corpus difficulty.

MUST-FAIL CONTROL: HIGH_SCRAMBLED_B (same token pool as HIGH_B, but each credited hit's verb-lemma label
permuted with a fixed seed before building the prior table -- imported verbatim from v1's
compute_patient_prior(scramble_seed=...) mechanism) must NOT beat LOW_B by the same margin as real HIGH_B.

COMPUTE ARCHITECTURE (mandatory declaration): class (b) sequential-CPU with justification -- pure corpus
token-counting + argmax/pairwise-comparison over <=200 pseudo-disambiguation trials x 3 capacity tiers;
no matmul-heavy primitive; wall time MEASURED < 30s total (see self_test/smoke prints). Foreground,
local-to-completion, NO queue, NO push, NO remote-persist (mirrors v1 + LCCP scoping). Storage:
no_storage (a measurement cell; no KGStore, no atoms.jsonl writes, no substrate primitive calls).

CELL-TEMPLATE MANDATORY (subset applicable to a LOCAL foreground measurement; not queue-dispatched):
- arms_differ_verified at smoke (argmax/pairwise choice hashes across LOW_B/HIGH_B/HIGH_SCRAMBLED_B differ)
- final_metrics_atomicity: tmp_replace (os.replace)
- except SystemExit: raise BEFORE except Exception (no BaseException)
- baseline_in_band at smoke (0.05 < CJ-patient-accuracy(LOW_B) < 0.95 at every capacity tier -- chance-level
  pseudo-disambiguation is ~0.5 by symmetric construction, so this is a sanity floor, not a discriminating
  claim on its own)
- discriminator fires at smoke: n_trials > 0 at every tier; LCCP legacy block reproduces v1's exact numbers
  (Gate D positive-control reproduction)
- deterministic seeding: fixed int seeds only, sorted(set(...)) not list(set(...)), no builtin hash()
- all numbers tagged MEASURED@ (printed + written to metrics.json) / CITED@ (Levin 1993 lemma list, reused
  from v1) / HYPOTHESIZED@ (pre-reg band choices, stated before running)

NOT DISPATCHED TO QUEUE. Design + smoke ONLY per task shape -- reports to Director for a full-run go/no-go
call (this cycle's smoke pool IS effectively "full" for the in-genre CJ probe: the held-out Third-Reader
pool and the McGuffey background pool are both already at their LOCAL ceiling; a bigger run would require
staging ROCStories or another external corpus -- flagged explicitly in the completion report, not silently
assumed).
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import argparse
import json
import math
import re
import sys
import time
import traceback
from collections import defaultdict
from datetime import datetime, timezone

import numpy as np

ANCHOR_NAME = "event_outcome_density_patient_signal_probe_v2"
REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(REPO_ROOT)
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from experiments import exp_event_outcome_density_patient_signal_probe_v1 as V1  # noqa: E402
from experiments import exp_read_nested_clause_relative_third_reader_v1 as NEST  # noqa: E402

GOLD_LESSONS = V1.GOLD_LESSONS  # ["L04","L05","L07","L08","L09","L10","L12"] -- frozen, unchanged

# ----------------------------------------------------------------------------------------------
# Held-out Third-Reader pool (72 of 79 lessons NEVER in the hand-gold set) for the label-free CJ probe.
# ----------------------------------------------------------------------------------------------
def load_heldout_third_reader_text():
    les = NEST.load_lessons()
    heldout_ids = [k for k in sorted(les.keys()) if k not in set(GOLD_LESSONS)]
    assert len(heldout_ids) >= 50, f"expected >=50 held-out Third Reader lessons, got {len(heldout_ids)}"
    assert not (set(heldout_ids) & set(GOLD_LESSONS)), "NO_LEAKAGE_VIOLATION: held-out overlaps hand-gold"
    text = " ".join(les[k] for k in heldout_ids)
    return text, heldout_ids


# ----------------------------------------------------------------------------------------------
# Per-instance (not aggregated) credited-instance extraction -- same TRANS/INCHOATIVE pattern as v1's
# compute_patient_prior, but returns per-instance records (verb, true_patient, kind[, true_agent]) so
# individual pseudo-disambiguation TRIALS can be built (v1's function only returns aggregate counts).
# ----------------------------------------------------------------------------------------------
def extract_credited_instances(text_blob):
    """Return (patient_instances, agent_instances).
    patient_instances: [{"verb":lemma,"true_patient":tok,"kind":"trans"|"inch"}]
    agent_instances (TRANS-only, when a resolvable preceding content-word subject exists):
      [{"verb":lemma,"true_agent":tok}]
    """
    patient_insts, agent_insts = [], []
    for sent in V1.split_sents(text_blob):
        toks = [t.lower() for t in V1.WORD_RE.findall(sent)]
        for i, tok in enumerate(toks):
            if tok not in V1.SURF2LEMMA:
                continue
            lemma = V1.SURF2LEMMA[tok]
            nxt = toks[i + 1] if i + 1 < len(toks) else None
            prv = toks[i - 1] if i - 1 >= 0 else None
            if nxt is not None and nxt.isalpha() and nxt not in V1.FUNC_STOP and nxt not in V1.PRONOUN:
                patient_insts.append({"verb": lemma, "true_patient": nxt, "kind": "trans"})
                j = i - 1
                agent_tok = None
                while j >= 0:
                    cand = toks[j]
                    if cand in V1.FUNC_STOP:
                        j -= 1
                        continue
                    if cand.isalpha():
                        agent_tok = cand
                    break
                if agent_tok is not None and agent_tok not in V1.PRONOUN and agent_tok != nxt:
                    agent_insts.append({"verb": lemma, "true_agent": agent_tok})
            elif (nxt is None or nxt in V1.FUNC_STOP) and prv is not None and prv.isalpha() \
                    and prv not in V1.FUNC_STOP and prv not in V1.PRONOUN:
                patient_insts.append({"verb": lemma, "true_patient": prv, "kind": "inch"})
    return patient_insts, agent_insts


def scramble_prior_table(prior_table, seed):
    """MUST-FAIL CONTROL FIX (bug found + confirmed this cycle): v1's compute_patient_prior(...,
    scramble_seed=X) permutes the ORDER of a flat list of credited noun-tokens BEFORE tallying
    (`credited = [credited[j] for j in perm]`, then `counts[n] += 1` for n in credited). Tallying
    occurrence counts is order-invariant, so that permutation is a mathematical NO-OP: the resulting
    counts dict is IDENTICAL to the unscrambled one at every corpus scale, by construction -- confirmed
    empirically this cycle (HIGH vs HIGH_SCRAMBLED choice-hashes were BIT-IDENTICAL, 0/110 trials
    differing, at every one of the 3 capacity tiers; v1's own metrics.json shows the same
    HIGH_vs_HIGH_SCRAMBLED tie, which its pre-reg attributed to "small n" -- it is not small-n, it is
    structural). This function implements a control that ACTUALLY destroys the noun-identity -> count
    linkage: draws a fixed-seed derangement over the SET of distinct credited noun-TYPES and reassigns
    each type's count to a different type (preserves total hit count + the corpus-wide frequency
    DISTRIBUTION/multiset of counts + vocabulary size; destroys which SPECIFIC noun owns which count)."""
    types = sorted(prior_table.keys())
    if len(types) < 2:
        return dict(prior_table)
    counts = [prior_table[t] for t in types]
    rng = np.random.default_rng(seed)
    perm = build_derangement(len(types), rng)
    return {t: counts[perm[i]] for i, t in enumerate(types)}


def build_derangement(n, rng):
    """Fixed-seed near-derangement permutation of range(n) (no self-maps where n>1)."""
    perm = rng.permutation(n)
    if n > 1:
        for i in range(n):
            if perm[i] == i:
                j = (i + 1) % n
                perm[i], perm[j] = perm[j], perm[i]
    return perm


def build_cj_trials(instances, key, seed):
    """instances: list of dicts each containing `key` (the true filler). Returns trials
    [{"verb":..,"true":..,"corrupt":..}] via a fixed-seed derangement (corrupted filler = another
    instance's true filler, never self)."""
    rng = np.random.default_rng(seed)
    n = len(instances)
    if n == 0:
        return []
    perm = build_derangement(n, rng)
    trials = []
    for i in range(n):
        trials.append({"verb": instances[i]["verb"], "true": instances[i][key],
                        "corrupt": instances[perm[i]][key]})
    return trials


def score_cj_full(trials, prior_table, animate_discount, tie_seed):
    """Full SCORE (aff+anim), matches v1's score_arm formula exactly. Returns (accuracy, n, choice_hash)."""
    rng = np.random.default_rng(tie_seed)
    n_correct, choices = 0, []
    for t in trials:
        s_true = V1.patient_affinity(t["true"], prior_table) + \
            (1.0 if not V1.is_animate(t["true"]) else animate_discount)
        s_corr = V1.patient_affinity(t["corrupt"], prior_table) + \
            (1.0 if not V1.is_animate(t["corrupt"]) else animate_discount)
        if s_true > s_corr:
            n_correct += 1
            choices.append("T")
        elif s_true < s_corr:
            choices.append("C")
        else:
            win = int(rng.integers(0, 2))
            n_correct += win
            choices.append("t" if win else "c")
    n = len(trials)
    return (n_correct / n if n else 0.0), n, "".join(choices)


def score_cj_aff_only(trials, prior_table, tie_seed):
    """AFF-ONLY component (density-dependent piece alone, no animacy term) -- the denser-!=-easier
    isolation instrument, used identically for both the patient-slot AND agent-slot control trials."""
    rng = np.random.default_rng(tie_seed)
    n_correct = 0
    for t in trials:
        s_true = V1.patient_affinity(t["true"], prior_table)
        s_corr = V1.patient_affinity(t["corrupt"], prior_table)
        if s_true > s_corr:
            n_correct += 1
        elif s_true < s_corr:
            pass
        else:
            n_correct += int(rng.integers(0, 2))
    n = len(trials)
    return (n_correct / n if n else 0.0), n


# ----------------------------------------------------------------------------------------------
# Capacity-tier background pools: direct top/bottom-ranked token-budget selection (NOT the tercile
# matcher -- MEASURED this cycle that the natural zero-density tercile caps at ~9.1K raw tokens, so a
# budget sweep needs direct rank-based truncation, not tercile-then-match).
# ----------------------------------------------------------------------------------------------
def rank_lessons_by_density(lessons):
    scored = []
    for les in lessons:
        n_tok, hits, dens = V1.lesson_density(les["text"])
        if n_tok < 20:
            continue
        scored.append({"text": les["text"], "src": les["src"], "n_tok": n_tok, "hits": hits, "density": dens})
    scored.sort(key=lambda r: (r["density"], r["src"]))
    return scored


def budget_pool(scored_sorted, end, budget_tok, seed, reverse=False):
    """end='low' takes from the bottom (lowest density) of the ranked list; end='high' takes from the
    top -- selection walks the list IN RANK ORDER from that end (never shuffles the full pool, which
    would destroy the rank selection). The already-selected subset is then fixed-seed shuffled ONLY to
    randomize concatenation order within the tier (does not change tier membership/density)."""
    pool = scored_sorted if end == "low" else list(reversed(scored_sorted))
    acc, kept = 0, []
    for r in pool:
        if acc >= budget_tok:
            break
        kept.append(r)
        acc += r["n_tok"]
    rng = np.random.default_rng(seed)
    idx = rng.permutation(len(kept))
    kept = [kept[i] for i in idx]
    return kept, acc


def blob_and_density(rows):
    blob = " ".join(r["text"] for r in rows)
    n_tok = sum(r["n_tok"] for r in rows)
    n_hits = sum(r["hits"] for r in rows)
    dens = (n_hits / n_tok * 1000.0) if n_tok > 0 else 0.0
    return blob, n_tok, dens


# ----------------------------------------------------------------------------------------------
# Cheap bigram-LM perplexity diagnostic (nuisance-covariate sanity check, NOT a full regression).
# ----------------------------------------------------------------------------------------------
def bigram_perplexity(train_text, eval_sents, add_k=1.0):
    train_toks = [t.lower() for t in V1.WORD_RE.findall(train_text)]
    if len(train_toks) < 10:
        return float("nan")
    vocab = set(train_toks)
    V_size = max(len(vocab), 1)
    unigram = defaultdict(int)
    bigram = defaultdict(int)
    for i, t in enumerate(train_toks):
        unigram[t] += 1
        if i > 0:
            bigram[(train_toks[i - 1], t)] += 1
    total_lp, n = 0.0, 0
    for sent in eval_sents:
        toks = [t.lower() for t in V1.WORD_RE.findall(sent)]
        for i in range(1, len(toks)):
            prev, cur = toks[i - 1], toks[i]
            p = (bigram.get((prev, cur), 0) + add_k) / (unigram.get(prev, 0) + add_k * V_size)
            total_lp += math.log(max(p, 1e-12))
            n += 1
    if n == 0:
        return float("nan")
    return float(math.exp(-total_lp / n))


# ----------------------------------------------------------------------------------------------
# Config.
# ----------------------------------------------------------------------------------------------
CAPACITY_BUDGETS = [3000, 6000, 9000]


def cfg_smoke():
    return {"min_count": 2, "animate_discount": 0.35, "seed": 7, "n_boot": 200,
            "capacity_budgets": CAPACITY_BUDGETS}


def cfg_full():
    return {"min_count": 2, "animate_discount": 0.35, "seed": 7, "n_boot": 2000,
            "capacity_budgets": CAPACITY_BUDGETS}


def run_config(cfg):
    t0 = time.perf_counter()
    seed = cfg["seed"]

    # ---- held-out CJ eval pool (label-free; independent of hand-gold) ----
    heldout_text, heldout_ids = load_heldout_third_reader_text()
    patient_insts, agent_insts = extract_credited_instances(heldout_text)
    n_tok_heldout = len(V1.WORD_RE.findall(heldout_text))
    patient_trials = build_cj_trials(patient_insts, "true_patient", seed=seed + 100)
    agent_trials = build_cj_trials(agent_insts, "true_agent", seed=seed + 200)
    eval_sents_for_ppl = V1.split_sents(heldout_text)

    # ---- background pools: ranked lessons (McGuffey non-eval pool: Primer/First/Second/Fourth) ----
    lessons = V1.load_mcguffey_lessons()
    scored = rank_lessons_by_density(lessons)
    zero_density_n = sum(1 for r in scored if r["density"] == 0.0)

    capacity_results = {}
    for budget in cfg["capacity_budgets"]:
        low_rows, low_tok = budget_pool(scored, "low", budget, seed=seed)
        high_rows, high_tok = budget_pool(scored, "high", budget, seed=seed + 1)
        low_blob, low_bg_tok, low_dens = blob_and_density(low_rows)
        high_blob, high_bg_tok, high_dens = blob_and_density(high_rows)

        prior_low, n_hits_low = V1.compute_patient_prior(low_blob)
        prior_high, n_hits_high = V1.compute_patient_prior(high_blob)
        prior_high_scr = scramble_prior_table(prior_high, seed=seed + 999)  # FIXED control (see docstring)

        acc_low, n_p, hash_low = score_cj_full(patient_trials, prior_low, cfg["animate_discount"], tie_seed=seed + 1)
        acc_high, _, hash_high = score_cj_full(patient_trials, prior_high, cfg["animate_discount"], tie_seed=seed + 1)
        acc_high_scr, _, hash_high_scr = score_cj_full(patient_trials, prior_high_scr, cfg["animate_discount"],
                                                        tie_seed=seed + 1)

        pat_aff_low, _ = score_cj_aff_only(patient_trials, prior_low, tie_seed=seed + 2)
        pat_aff_high, _ = score_cj_aff_only(patient_trials, prior_high, tie_seed=seed + 2)
        agt_aff_low, n_a = score_cj_aff_only(agent_trials, prior_low, tie_seed=seed + 3)
        agt_aff_high, _ = score_cj_aff_only(agent_trials, prior_high, tie_seed=seed + 3)

        ppl_low = bigram_perplexity(low_blob, eval_sents_for_ppl)
        ppl_high = bigram_perplexity(high_blob, eval_sents_for_ppl)

        capacity_results[str(budget)] = {
            "budget_tok": budget,
            "low_bg_tok": low_bg_tok, "high_bg_tok": high_bg_tok,
            "low_density_per_1000tok": low_dens, "high_density_per_1000tok": high_dens,
            "n_low_lessons": len(low_rows), "n_high_lessons": len(high_rows),
            "cj_patient_full_acc": {"LOW": acc_low, "HIGH": acc_high, "HIGH_SCRAMBLED": acc_high_scr},
            "cj_patient_n_trials": n_p,
            "cj_patient_aff_only": {"LOW": pat_aff_low, "HIGH": pat_aff_high},
            "cj_agent_aff_only": {"LOW": agt_aff_low, "HIGH": agt_aff_high},
            "cj_agent_n_trials": n_a,
            "choice_hash": {"LOW": hash_low, "HIGH": hash_high, "HIGH_SCRAMBLED": hash_high_scr},
            "bigram_perplexity": {"LOW": ppl_low, "HIGH": ppl_high},
            "gap_high_minus_low": acc_high - acc_low,
            "gap_high_minus_scrambled": acc_high - acc_high_scr,
            "patient_specific_gap": (pat_aff_high - pat_aff_low) - (agt_aff_high - agt_aff_low),
            "baseline_in_band": 0.05 < acc_low < 0.95,
        }

    # ---- flagship v1 tercile replication block (verbatim reuse, positive-control reproduction, Gate D) ----
    v1_lessons = V1.load_mcguffey_lessons()
    v1_tiers, v1_tier_tok, v1_tier_n = V1.build_density_tiers(v1_lessons, seed)
    v1_instances = V1.build_eval_instances()
    n_multi_total = sum(1 for i in v1_instances if len(i["candidates"]) >= 2)
    v1_results = {}
    for name in ["LOW", "MED", "HIGH"]:
        blob = " ".join(r["text"] for r in v1_tiers[name])
        prior, n_hits = V1.compute_patient_prior(blob)
        res = V1.score_arm(v1_instances, prior, cfg["animate_discount"])
        res["n_bg_tok"] = v1_tier_tok[name]
        v1_results[name] = res

    # ---- verdict logic (per-tier gates; PRIMARY = CJ patient-slot full-score) ----
    tier_names = [str(b) for b in cfg["capacity_budgets"]]
    gap_ok = all(capacity_results[t]["gap_high_minus_low"] >= 0.08 for t in tier_names)
    gap_weak_at_all = all(capacity_results[t]["gap_high_minus_low"] < 0.03 for t in tier_names)
    scr_ok = all(capacity_results[t]["gap_high_minus_scrambled"] >= 0.05 for t in tier_names)
    scr_fail_any = any(capacity_results[t]["gap_high_minus_scrambled"] < 0.03 for t in tier_names)
    baseline_ok = all(capacity_results[t]["baseline_in_band"] for t in tier_names)
    specificity_ok = all(capacity_results[t]["patient_specific_gap"] >= 0.05 for t in tier_names)
    specificity_fail = any(capacity_results[t]["patient_specific_gap"] <= 0.0 for t in tier_names)

    if gap_ok and scr_ok and baseline_ok and specificity_ok:
        verdict = "HARD_PASS_DENSITY_IS_THE_LEVER_V2"
    elif gap_weak_at_all or scr_fail_any or specificity_fail:
        verdict = "HARD_FAIL_DENSITY_NOT_THE_LEVER_V2"
    else:
        verdict = "MIDDLE_BAND_V2"

    elapsed = time.perf_counter() - t0
    payload = {
        "anchor_name": ANCHOR_NAME,
        "cfg": cfg,
        "heldout_third_reader": {
            "n_lessons": len(heldout_ids), "n_tokens": n_tok_heldout,
            "n_patient_trials": len(patient_trials), "n_agent_trials": len(agent_trials),
            "gold_lessons_excluded": GOLD_LESSONS,
        },
        "zero_density_lesson_count_bg_pool": zero_density_n,
        "capacity_tier_results": capacity_results,
        "v1_replication_block": {
            "tier_tok": v1_tier_tok,
            "results": {k: {kk: vv for kk, vv in v.items() if kk != "choice_hash"} for k, v in v1_results.items()},
            "n_eval_instances_total": len(v1_instances),
            "n_eval_instances_multi_candidate": n_multi_total,
        },
        "gap_ok_all_tiers": gap_ok,
        "scr_ok_all_tiers": scr_ok,
        "baseline_ok_all_tiers": baseline_ok,
        "specificity_ok_all_tiers": specificity_ok,
        "verdict": verdict,
        "verdict_msg": (f"CJ patient-slot gap(HIGH-LOW) per tier={[round(capacity_results[t]['gap_high_minus_low'], 4) for t in tier_names]} "
                        f"scrambled-gap per tier={[round(capacity_results[t]['gap_high_minus_scrambled'], 4) for t in tier_names]} "
                        f"patient_specific_gap per tier={[round(capacity_results[t]['patient_specific_gap'], 4) for t in tier_names]} "
                        f"n_patient_trials={len(patient_trials)} n_agent_trials={len(agent_trials)}"),
        "summary": f"{verdict}: {ANCHOR_NAME}",
        "elapsed_s": elapsed,
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(),
    }
    return payload


# ----------------------------------------------------------------------------------------------
# I/O + harness plumbing.
# ----------------------------------------------------------------------------------------------
def get_output_dir(run_mode_str):
    suffix = {"full": "", "smoke": "_smoke", "self_test": "_selftest"}[run_mode_str]
    return os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}{suffix}")


def write_metrics(output_dir, payload):
    os.makedirs(output_dir, exist_ok=True)
    tmp_path = os.path.join(output_dir, "metrics.json.tmp")
    final_path = os.path.join(output_dir, "metrics.json")
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, default=str)
    os.replace(tmp_path, final_path)


def _write_crash_metrics(output_dir, anchor_name, exc):
    diag = {
        "verdict": "CELL_CRASHED",
        "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
        "summary": f"CELL_CRASHED: {type(exc).__name__}",
        "elapsed_s": 0.0,
        "traceback": traceback.format_exc()[:5000],
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(),
        "anchor_name": anchor_name,
    }
    os.makedirs(output_dir, exist_ok=True)
    tmp_path = os.path.join(output_dir, "metrics.json.tmp")
    final_path = os.path.join(output_dir, "metrics.json")
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp_path, final_path)


def self_test():
    """Exercise the REAL held-out extraction + background-pool path at reduced scope BEFORE any full run."""
    heldout_text, heldout_ids = load_heldout_third_reader_text()
    assert len(heldout_ids) == 72, f"expected 72 held-out lessons, got {len(heldout_ids)}"
    patient_insts, agent_insts = extract_credited_instances(heldout_text)
    assert len(patient_insts) > 50, f"expected >50 patient instances, got {len(patient_insts)}"
    print(f"[self_test] MEASURED n_heldout_lessons={len(heldout_ids)} "
          f"n_patient_instances={len(patient_insts)} n_agent_instances={len(agent_insts)}", flush=True)
    trials = build_cj_trials(patient_insts, "true_patient", seed=7)
    assert len(trials) == len(patient_insts)
    n_value_differs = sum(1 for t in trials if t["true"] != t["corrupt"])
    assert n_value_differs > 0.5 * len(trials), (
        f"derangement produced too few value-distinct trials ({n_value_differs}/{len(trials)}) "
        f"-- corruption pool may be degenerate (too few distinct patient tokens)")
    lessons = V1.load_mcguffey_lessons()
    scored = rank_lessons_by_density(lessons)
    low_rows, low_tok = budget_pool(scored, "low", 3000, seed=7)
    high_rows, high_tok = budget_pool(scored, "high", 3000, seed=8)
    assert low_tok >= 2500, f"LOW budget pool too small: {low_tok}"
    assert high_tok >= 2500, f"HIGH budget pool too small: {high_tok}"
    low_blob, _, low_dens = blob_and_density(low_rows)
    high_blob, _, high_dens = blob_and_density(high_rows)
    assert low_dens < high_dens, f"LOW density {low_dens} not < HIGH density {high_dens} at budget=3000"
    print(f"[self_test] MEASURED budget=3000 low_dens={low_dens:.3f} high_dens={high_dens:.3f}", flush=True)
    # NOTE: the scramble-control check needs a big-enough vocabulary to have real overlap with the
    # 110-trial pool -- budget=3000's tiny background vocab (too sparse) under-exercises it; use the
    # flagship budget=9000 tier (one of the 3 real capacity tiers) for this specific validity check.
    high_rows_9k, _ = budget_pool(scored, "high", 9000, seed=8)
    high_blob_9k, _, _ = blob_and_density(high_rows_9k)
    prior_high, _ = V1.compute_patient_prior(high_blob_9k)
    prior_high_scr = scramble_prior_table(prior_high, seed=999)
    assert prior_high != prior_high_scr, "MUST_FAIL_CONTROL_STILL_A_NOOP: scramble did not change prior_table"
    _, _, hash_real = score_cj_full(trials, prior_high, 0.35, tie_seed=1)
    _, _, hash_scr = score_cj_full(trials, prior_high_scr, 0.35, tie_seed=1)
    n_diff = sum(1 for a, b in zip(hash_real, hash_scr) if a != b)
    print(f"[self_test] MEASURED scramble control (budget=9000) now changes {n_diff}/{len(hash_real)} trial "
          f"outcomes (v1's original scramble_seed mechanism was a confirmed NO-OP: 0/{len(hash_real)} always, "
          f"at every capacity tier -- a math bug: permuting a flat list's ORDER before tallying counts cannot "
          f"change the tallied counts)", flush=True)
    assert n_diff > 0, "MUST_FAIL_CONTROL_STILL_VACUOUS: scrambled choices identical to real HIGH"
    print("[self_test] PASS", flush=True)
    return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-mode", choices=["full", "smoke", "self_test"], default="full")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        self_test()
        return

    mode = args.run_mode
    output_dir = get_output_dir(mode)
    try:
        cfg = cfg_smoke() if mode == "smoke" else cfg_full()
        payload = run_config(cfg)
        payload["run_mode"] = mode
        write_metrics(output_dir, payload)
        print(f"[{mode}] {payload['verdict_msg']}", flush=True)
        print(f"[{mode}] verdict={payload['verdict']} elapsed_s={payload['elapsed_s']:.2f}", flush=True)
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # noqa: BLE001 -- NOT BaseException; preserves SystemExit/KeyboardInterrupt
        _write_crash_metrics(output_dir, ANCHOR_NAME, e)
        raise


if __name__ == "__main__":
    main()
