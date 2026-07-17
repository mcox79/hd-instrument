#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
exp_read_discourse_overlay_longdist_reference_v1

QUESTION (redirect from the precision-with-context null, cell
exp_read_discourse_overlay_context_precision_reopen_v1 7e3acab66):
Does a MAINTAINED symbolic entity-state overlay STRUCTURALLY beat a plain
RECENCY-WINDOW baseline at LONG-DISTANCE reference resolution -- resolving a
pronoun whose true antecedent lies BEYOND the recency window (where recency
structurally fails)? Glass-box, NO runtime LLM.

WHY THIS REGIME (brain-check banked, backup doc): recency is a STRONG baseline
(Tetreault/Strube; coupling wall). So we DELIBERATELY target the regime where
recency STRUCTURALLY fails -- the pronoun's nearest same-entity mention is more
than K mentions back -- and ask whether a persistent, frequency-accumulating
entity-state can reach the far antecedent that the recency window dropped.
This is NOT construction-determined: the overlay wins ONLY IF its salience
ranking correctly prefers the true (far) entity over nearer compatible
distractors. If it cannot, that is a first-class "recency dominates even at
distance" null (HARD_FAIL) that redirects to textbook-comprehension.

CORPUS: LitBank coreference (github.com/dbamman/litbank, coref/conll/*.conll),
CC-BY 4.0. Literary prose with GOLD entity-mention spans + GOLD coref clusters
spanning ~2000-token passages -> real long-distance reference. We use GOLD
mention BOUNDARIES (standard "gold mentions" eval setting) but the resolver
NEVER sees gold coref LINKING; gold cluster ids are used ONLY to (a) stratify
the long-distance subset and (b) score correctness. UD-EWT (the null cell's bed)
lacked coref gold, which is why precision could not be credited there.

GLASS-BOX RESOLUTION: fixed pronoun lexicon (reused from the precision cell),
surface-head-string entity grouping, salience arithmetic. No spaCy-default /
Stanza / torch / transformers. Pure stdlib + numpy (bootstrap only).

ARMS (primary variable = maintained entity-state vs recency; extra arms isolate
the mechanism + guard the interpretation honestly):
  recency_window      STRUCTURAL-WALL illustration (task-specified window-K
                      recency): nearest compatible prior MENTION within window K.
                      On the LD subset this is 0 BY CONSTRUCTION (no same-cluster
                      mention within K), so it demonstrates recency's structural
                      wall but is NOT the can-fail bar.
  recency_unbounded   PRIMARY BASELINE (classical Hobbs recency): most-recent
                      compatible prior mention, NO window. NOT construction-pinned
                      -- correct at distance whenever no nearer compatible
                      distractor exists. THIS is the strong can-fail bar.
  maintained_overlay  MECHANISM: a MAINTAINED entity-state = frequency ACCUMULATOR
                      over surface-head entities + recency tie-break (centering /
                      attentional-state model). Reaches far, frequently-evoked
                      antecedents the recency heuristic misses.
  freq_only           ABLATION: pure mention-frequency (no recency). Guards the
                      honest read "is the overlay just predict-the-protagonist?"

PRIMARY DISCRIMINATOR: delta_ld = ld_acc[maintained_overlay] - ld_acc[recency_unbounded]
on the LONG-DISTANCE subset (gold nearest-antecedent mention-distance > K).
(delta_ld_vs_window = overlay - recency_window is ALSO reported, as the structural-
wall context, NOT as the pass/fail discriminator.)

BANDS (K=5 primary; discriminator = overlay vs recency_unbounded):
  HARD_PASS: delta_ld >= 0.05 AND bootstrap sign-stability(delta>0) >= 0.90 AND
             overlay precision (acc-on-attempted) >= recency_unbounded precision
             - 0.05 (zero-hallucination / abstention guardrail preserved).
  HARD_FAIL: delta_ld <= 0.0 (overlay no better than the strong recency baseline
             even at distance) -> recency-dominates-even-at-distance null;
             redirect textbook-comprehension.
  MIDDLE_BAND: 0 < delta_ld < 0.05.
NOTE: freq_only is a mechanism-decomposition control; if overlay ~= freq_only the
persistence win is driven by FREQUENCY ACCUMULATION (a maintained-state property
recency structurally lacks) -- reported, not hidden.

Numbers in this header are DESIGN targets (HYPOTHESIZED@this file); all reported
numbers are MEASURED@ the metrics.json written by this run.

CELL-TEMPLATE MANDATORY:
# - arms_differ_verified at smoke gate (META_RULE_AF; hash-test on per-target picks)
# - final_metrics_atomicity: tmp_replace (single-shot; metrics.json.tmp + os.replace)
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_n/a: symbolic accuracy metric; no matmul noise floor. Reachability shown
#   empirically: recency ld_acc is low on the LD subset (by construction of the
#   subset), leaving headroom for the overlay.
# - baseline_in_band: recency ld_acc on LD subset is intentionally LOW (the point);
#   the DISCRIMINATOR is delta_ld and it is telemetry-sensitive (window K moves it).
# - discriminator survives scale: full = all cached books; smoke previews on 5 books
#   and asserts the LD subset is non-empty and delta is measurable.
# - HARD_PASS strictly above 0 by >= 0.05 band-width (META_RULE_L)
# - cardinality: EXPECTED_N_UNITS = n_books processed; verdict counts targets
# - per-unit failure-class instrumentation; no bare except
# - calibration_check: adaptive_n/a (fixed lexicon + fixed decay; no tuned-for-PASS knob)
# - all header numbers tagged HYPOTHESIZED@; reported numbers MEASURED@
# - real_code_path: self-test parses a real temp conll + runs all 4 real resolvers
"""

import argparse
import hashlib
import json
import os
import platform
import sys
import time
import traceback
import urllib.request
from datetime import datetime, timezone

import numpy as np

# ----------------------------------------------------------------------------
# CONFIG
# ----------------------------------------------------------------------------
ANCHOR_NAME = "read_discourse_overlay_longdist_reference_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CORPUS_DIR = os.path.join(REPO_ROOT, "data", "corpora", "litbank_coref_conll")
LITBANK_RAW = "https://raw.githubusercontent.com/dbamman/litbank/master/coref/conll/"

# Deterministic, alphabetical book list (subset of the 100 LitBank coref books).
# Full run uses FULL_BOOKS; smoke uses the first SMOKE_N.
FULL_BOOKS = [
    "345_dracula_brat.conll",
    "105_persuasion_brat.conll",
    "113_the_secret_garden_brat.conll",
    "110_tess_of_the_durbervilles_a_pure_woman_brat.conll",
    "1023_bleak_house_brat.conll",
    "1064_the_masque_of_the_red_death_brat.conll",
    "11231_bartleby_the_scrivener_a_story_of_wallstreet_brat.conll",
    "158_emma_brat.conll",
    "1342_pride_and_prejudice_brat.conll",
    "1400_great_expectations_brat.conll",
    "174_the_picture_of_dorian_gray_brat.conll",
    "209_the_turn_of_the_screw_brat.conll",
    "2489_moby_dick_brat.conll",
    "2814_dubliners_brat.conll",
    "2852_the_hound_of_the_baskervilles_brat.conll",
    "36_the_war_of_the_worlds_brat.conll",
    "514_little_women_brat.conll",
    "521_the_life_and_adventures_of_robinson_crusoe_brat.conll",
    "76_adventures_of_huckleberry_finn_brat.conll",
    "84_frankenstein_or_the_modern_prometheus_brat.conll",
    "1260_jane_eyre_an_autobiography_brat.conll",
    "829_gullivers_travels_into_several_remote_nations_of_the_world_brat.conll",
    "6053_evelina_or_the_history_of_a_young_ladys_entrance_into_the_world_brat.conll",
    "73_the_red_badge_of_courage_an_episode_of_the_american_civil_war_brat.conll",
    "5348_ragged_dick_or_street_life_in_new_york_with_the_bootblacks_brat.conll",
]
SMOKE_N = 5

# 3rd-person pronoun lexicon (reused verbatim from
# exp_read_discourse_overlay_context_precision_reopen_v1.py lines 107-117).
PRONOUN_SCOPE = {
    "he":   {"number": "singular", "gender": "masc"},
    "him":  {"number": "singular", "gender": "masc"},
    "his":  {"number": "singular", "gender": "masc"},
    "she":  {"number": "singular", "gender": "fem"},
    "her":  {"number": "singular", "gender": "fem"},
    "hers": {"number": "singular", "gender": "fem"},
    "it":   {"number": "singular", "gender": "neuter"},
    "its":  {"number": "singular", "gender": "neuter"},
    "they": {"number": "plural",   "gender": "any"},
    "them": {"number": "plural",   "gender": "any"},
    "their":{"number": "plural",   "gender": "any"},
}
# Targets restricted to animate gendered singular pronouns (he/she family): they
# carry a real gender+number agreement axis and are the coref-heavy case in prose.
TARGET_PRONOUNS = {"he", "him", "his", "she", "her", "hers"}

# Glass-box gender cues for NOMINAL mentions (titles + gendered common nouns).
# STEELMANS the recency baseline: a real recency pronoun-resolver filters by
# gender agreement, so nearer WRONG-gender distractors are skipped. Proper NAMES
# not on these lists stay gender-unknown (compatible-with-any) -- the honest
# limitation of a gazetteer-free glass-box resolver. Applied identically to all arms.
MASC_CUES = {"mr", "mister", "sir", "lord", "master", "gentleman", "man", "men",
             "boy", "boys", "father", "dad", "papa", "son", "brother", "uncle",
             "king", "prince", "husband", "widower", "nephew", "grandfather",
             "he", "him", "his", "himself"}
FEM_CUES = {"mrs", "miss", "ms", "madam", "madame", "lady", "mistress", "woman",
            "women", "girl", "girls", "mother", "mom", "mama", "daughter",
            "sister", "aunt", "queen", "princess", "wife", "widow", "niece",
            "grandmother", "maid", "she", "her", "hers", "herself"}

WINDOW_K_PRIMARY = 5
WINDOW_K_SWEEP = [3, 5, 8]  # robustness: the LD threshold must not be a single-K artifact
OVERLAY_BETA = 0.5          # recency tie-break weight (frequency-primary accumulator)
OVERLAY_TIEBREAK_LAMBDA = 0.1  # tie-break decay; frequency counts dominate salience
N_BOOTSTRAP = 500
BOOTSTRAP_SEED = 20260717

# Bands
HP_DELTA = 0.05
HP_SIGN_STABILITY = 0.90
GUARD_PRECISION_EPS = 0.05


# ----------------------------------------------------------------------------
# CONLL parsing (gold mention spans + gold cluster ids)
# ----------------------------------------------------------------------------
def parse_conll(path):
    """Parse a LitBank/OntoNotes-style coref conll file.

    Returns an ordered list of mention dicts:
      {cluster:int, gtok_start:int, gtok_end:int, head:str, is_pronoun:bool,
       gender:str|None, number:str|None, midx:int}
    midx = position in the returned (start-ordered) list = mention index.
    """
    tokens = []          # (gtok_idx, token_text)
    mentions = []        # raw (cluster, start, end)
    open_stacks = {}     # cluster -> list of open start gtok indices
    gidx = 0
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if not line.strip():
                continue
            if line.startswith("#"):
                continue
            cols = line.split("\t")
            if len(cols) < 4:
                continue
            token = cols[3]
            coref = cols[-1].strip()
            tokens.append((gidx, token))
            if coref and coref != "_":
                for part in coref.split("|"):
                    part = part.strip()
                    if part.startswith("(") and part.endswith(")"):
                        cid = int(part[1:-1])
                        mentions.append((cid, gidx, gidx))
                    elif part.startswith("("):
                        cid = int(part[1:])
                        open_stacks.setdefault(cid, []).append(gidx)
                    elif part.endswith(")"):
                        cid = int(part[:-1])
                        if open_stacks.get(cid):
                            start = open_stacks[cid].pop()
                            mentions.append((cid, start, gidx))
            gidx += 1

    tok_text = {gi: tx for gi, tx in tokens}
    out = []
    for cid, start, end in mentions:
        span_toks = [tok_text[i] for i in range(start, end + 1) if i in tok_text]
        if not span_toks:
            continue
        head = span_toks[-1].lower()
        is_pron = head in PRONOUN_SCOPE
        if is_pron:
            gender = PRONOUN_SCOPE[head]["gender"]
            number = PRONOUN_SCOPE[head]["number"]
        else:
            gender = infer_nominal_gender(span_toks)  # None if no cue (unknown)
            number = None
        out.append({
            "cluster": cid, "gtok_start": start, "gtok_end": end,
            "head": head, "is_pronoun": is_pron,
            "gender": gender, "number": number,
        })
    out.sort(key=lambda m: (m["gtok_start"], m["gtok_end"]))
    for i, m in enumerate(out):
        m["midx"] = i
    return out


def infer_nominal_gender(span_toks):
    """Glass-box gender from title/gendered-noun cues in a nominal mention span.
    Returns 'masc' / 'fem' / None (unknown -> compatible with any). If both cue
    types appear, returns None (ambiguous)."""
    toks = {t.lower().strip(".,'") for t in span_toks}
    m = bool(toks & MASC_CUES)
    f = bool(toks & FEM_CUES)
    if m and not f:
        return "masc"
    if f and not m:
        return "fem"
    return None


def compatible(target, cand):
    """Weak, glass-box agreement filter, applied identically to every arm.
    A candidate is compatible unless it CONFLICTS in known gender or number.
    Nominal candidates (gender/number unknown) never conflict."""
    tg, tn = target["gender"], target["number"]
    cg, cn = cand.get("gender"), cand.get("number")
    if cg is not None and tg not in ("any", None) and cg not in ("any", None):
        if cg != tg:
            return False
    if cn is not None and tn not in ("any", None) and cn not in ("any", None):
        if cn != tn:
            return False
    return True


def build_targets(mentions):
    """Targets = gendered-singular pronoun mentions that have >=1 prior mention
    in the SAME gold cluster. Attach gold nearest-antecedent mention-distance."""
    by_cluster_prior = {}
    targets = []
    for m in mentions:
        cid = m["cluster"]
        if m["is_pronoun"] and m["head"] in TARGET_PRONOUNS:
            priors = by_cluster_prior.get(cid, [])
            if priors:
                nearest = priors[-1]  # largest midx < this (list is append-ordered)
                dist = m["midx"] - nearest
                targets.append({"target": m, "gold_dist": dist})
        by_cluster_prior.setdefault(cid, []).append(m["midx"])
    return targets


# ----------------------------------------------------------------------------
# ENTITY model (glass-box; NON-gold; surface-head-string grouping)
# ----------------------------------------------------------------------------
def prior_nominal_entities(mentions, target_midx):
    """Group prior NON-pronoun mentions by lowercased head string.
    Returns dict head_str -> list of prior mention dicts (midx-ordered)."""
    ent = {}
    for m in mentions:
        if m["midx"] >= target_midx:
            break
        if m["is_pronoun"]:
            continue
        ent.setdefault(m["head"], []).append(m)
    return ent


# ----------------------------------------------------------------------------
# RESOLVERS  (each returns antecedent mention dict or None)
# ----------------------------------------------------------------------------
def resolve_recency_window(target, mentions, K):
    """BASELINE: nearest compatible prior MENTION within window K (hard cutoff)."""
    tmidx = target["midx"]
    best = None
    for m in mentions:
        if m["midx"] >= tmidx:
            break
        if tmidx - m["midx"] > K:
            continue
        if not compatible(target, m):
            continue
        best = m  # keep last (nearest) compatible within window
    return best


def resolve_recency_unbounded(target, mentions, K=None):
    """STRONG BASELINE (classical Hobbs/recency): most-recent COMPATIBLE prior
    mention, NO window. NOT construction-pinned on the LD subset -- it is correct
    at distance whenever no NEARER compatible distractor exists. This is the
    honest can-fail bar the maintained overlay must beat."""
    tmidx = target["midx"]
    best = None
    for m in mentions:
        if m["midx"] >= tmidx:
            break
        if not compatible(target, m):
            continue
        best = m  # keep last (nearest) compatible; unbounded
    return best


def resolve_maintained_overlay(target, mentions, K=None,
                               beta=None, lam=None):
    """MECHANISM: a MAINTAINED entity-state whose salience is an ACCUMULATOR over
    mentions (centering / attentional-state model: the more an entity is evoked,
    the more central it stays), with recency only as a TIE-BREAK. This is what a
    persistent working-memory state is -- NOT exponential recency (an earlier
    exp(-lam*dist) formula collapsed to recency on the LD subset; see design
    note). salience(entity) = n_mentions + beta * exp(-lam * dist_to_last).
    NO window: a frequently-evoked far entity stays selectable. Returns the
    chosen entity's most recent mention as the concrete antecedent."""
    beta = OVERLAY_BETA if beta is None else beta
    lam = OVERLAY_TIEBREAK_LAMBDA if lam is None else lam
    tmidx = target["midx"]
    ents = prior_nominal_entities(mentions, tmidx)
    best_sal = -1.0
    best_last = None
    for head, ms in ents.items():
        if not compatible(target, ms[-1]):
            continue
        last = ms[-1]
        sal = len(ms) + beta * float(np.exp(-lam * (tmidx - last["midx"])))
        if sal > best_sal:
            best_sal = sal
            best_last = last
    return best_last


def resolve_freq_only(target, mentions):
    """ABLATION: pure mention-frequency per entity (no recency at all)."""
    tmidx = target["midx"]
    ents = prior_nominal_entities(mentions, tmidx)
    best_last = None
    best_count = -1
    for head, ms in ents.items():
        if not compatible(target, ms[-1]):
            continue
        if len(ms) > best_count:
            best_count = len(ms)
            best_last = ms[-1]
    return best_last


ARMS = {
    "recency_window": lambda t, ms, K: resolve_recency_window(t, ms, K),
    "recency_unbounded": lambda t, ms, K: resolve_recency_unbounded(t, ms, K),
    "maintained_overlay": lambda t, ms, K: resolve_maintained_overlay(t, ms),
    "freq_only": lambda t, ms, K: resolve_freq_only(t, ms),
}
# PRIMARY baseline for the discriminator = unbounded recency (strong, NOT
# construction-pinned on the LD subset). recency_window (window K) is reported as
# the STRUCTURAL-WALL illustration only: it is 0 on the LD subset BY CONSTRUCTION
# (no same-cluster mention within K), so it is NOT used as the can-fail bar.
BASELINE_ARM = "recency_unbounded"
STRUCT_WALL_ARM = "recency_window"
MECHANISM_ARM = "maintained_overlay"


# ----------------------------------------------------------------------------
# EVALUATION
# ----------------------------------------------------------------------------
def evaluate_book(mentions, K):
    """Run all arms on all targets of one book. Returns per-target records +
    per-target pick signatures (for arms-differ hashing)."""
    targets = build_targets(mentions)
    records = []
    for tinfo in targets:
        t = tinfo["target"]
        rec = {"gold_dist": tinfo["gold_dist"], "gold_cluster": t["cluster"],
               "picks": {}, "correct": {}, "attempted": {}}
        for arm_name, fn in ARMS.items():
            ante = fn(t, mentions, K)
            rec["attempted"][arm_name] = ante is not None
            rec["correct"][arm_name] = bool(ante is not None and ante["cluster"] == t["cluster"])
            rec["picks"][arm_name] = (-1 if ante is None else ante["midx"])
        records.append(rec)
    return records


def aggregate(records, K):
    """Aggregate LD-subset (gold_dist > K) accuracy/precision per arm + delta."""
    ld = [r for r in records if r["gold_dist"] > K]
    sd = [r for r in records if r["gold_dist"] <= K]
    out = {"K": K, "n_targets": len(records), "n_ld": len(ld), "n_sd": len(sd)}
    per_arm = {}
    for arm in ARMS:
        def acc(subset):
            if not subset:
                return None
            return sum(r["correct"][arm] for r in subset) / len(subset)
        def prec(subset):
            att = [r for r in subset if r["attempted"][arm]]
            if not att:
                return None
            return sum(r["correct"][arm] for r in att) / len(att)
        def attrate(subset):
            if not subset:
                return None
            return sum(r["attempted"][arm] for r in subset) / len(subset)
        per_arm[arm] = {
            "ld_acc": acc(ld), "ld_prec": prec(ld), "ld_attempt_rate": attrate(ld),
            "sd_acc": acc(sd), "all_acc": acc(records),
        }
    out["per_arm"] = per_arm
    if ld:
        out["delta_ld"] = (per_arm[MECHANISM_ARM]["ld_acc"] - per_arm[BASELINE_ARM]["ld_acc"])
        out["delta_ld_vs_window"] = (per_arm[MECHANISM_ARM]["ld_acc"]
                                     - per_arm[STRUCT_WALL_ARM]["ld_acc"])
        out["delta_ld_vs_freq"] = (per_arm[MECHANISM_ARM]["ld_acc"]
                                   - per_arm["freq_only"]["ld_acc"])
    else:
        out["delta_ld"] = None
    return out, ld


def bootstrap_sign_stability(ld_records, n_boot=N_BOOTSTRAP, seed=BOOTSTRAP_SEED):
    """Fraction of book-target bootstrap resamples with delta_ld > 0.
    Deterministic (fixed integer seed; np.random.default_rng)."""
    if len(ld_records) < 2:
        return None
    rng = np.random.default_rng(seed)
    base = np.array([r["correct"][BASELINE_ARM] for r in ld_records], dtype=float)
    mech = np.array([r["correct"][MECHANISM_ARM] for r in ld_records], dtype=float)
    n = len(ld_records)
    pos = 0
    for _ in range(n_boot):
        idx = rng.integers(0, n, size=n)
        d = mech[idx].mean() - base[idx].mean()
        if d > 0:
            pos += 1
    return pos / n_boot


# ----------------------------------------------------------------------------
# CORPUS FETCH
# ----------------------------------------------------------------------------
def ensure_corpus(books):
    """Download any missing LitBank conll files to CORPUS_DIR (cached)."""
    os.makedirs(CORPUS_DIR, exist_ok=True)
    fetched, present, failed = [], [], []
    for b in books:
        dst = os.path.join(CORPUS_DIR, b)
        if os.path.exists(dst) and os.path.getsize(dst) > 1000:
            present.append(b)
            continue
        try:
            urllib.request.urlretrieve(LITBANK_RAW + b, dst)
            if os.path.getsize(dst) > 1000:
                fetched.append(b)
            else:
                failed.append((b, "empty"))
        except Exception as e:  # noqa: BLE001 -- recorded, book skipped, not silent
            failed.append((b, "%s: %s" % (type(e).__name__, str(e)[:120])))
    return present, fetched, failed


# ----------------------------------------------------------------------------
# ARMS-MUST-DIFFER (META_RULE_AF)
# ----------------------------------------------------------------------------
def arms_must_differ(all_records):
    """Hash each arm's per-target pick vector; assert not all bit-identical."""
    digests = {}
    for arm in ARMS:
        vec = bytes()
        for r in all_records:
            vec += int(r["picks"][arm]).to_bytes(4, "big", signed=True)
        digests[arm] = hashlib.sha256(vec).hexdigest()
    d_base = digests[BASELINE_ARM]
    d_mech = digests[MECHANISM_ARM]
    assert d_base != d_mech, (
        "META_RULE_AF VIOLATION: %s and %s produced bit-identical picks"
        % (BASELINE_ARM, MECHANISM_ARM))
    return digests


# ----------------------------------------------------------------------------
# RUN
# ----------------------------------------------------------------------------
def run(books, run_mode):
    t0 = time.perf_counter()
    out_dir = os.path.join(REPO_ROOT, "data",
                           "exp_%s%s" % (ANCHOR_NAME, "_smoke" if run_mode == "smoke" else ""))
    os.makedirs(out_dir, exist_ok=True)
    _write_start_marker(out_dir, run_mode, len(books))

    present, fetched, failed = ensure_corpus(books)
    usable = present + fetched
    if len(usable) < 2:
        raise RuntimeError("CORPUS_UNAVAILABLE: only %d books usable (failed=%s)"
                           % (len(usable), failed[:3]))

    per_book = {}
    all_records = []
    book_failures = []
    for b in usable:
        try:
            mentions = parse_conll(os.path.join(CORPUS_DIR, b))
            recs = evaluate_book(mentions, WINDOW_K_PRIMARY)
            per_book[b] = {"n_mentions": len(mentions), "n_targets": len(recs)}
            for r in recs:
                r["book"] = b
            all_records.extend(recs)
        except Exception as e:  # noqa: BLE001 -- per-book failure-class recorded
            book_failures.append({"book": b, "failure_class": type(e).__name__,
                                  "msg": str(e)[:160]})

    if not all_records:
        raise RuntimeError("NO_TARGETS: parsed %d books, 0 pronoun targets" % len(usable))

    digests = arms_must_differ(all_records)

    # Primary aggregate at K=5 + robustness sweep over K.
    sweep = {}
    for K in WINDOW_K_SWEEP:
        agg, _ld = aggregate(all_records, K)
        sweep[str(K)] = agg
    primary, ld_primary = aggregate(all_records, WINDOW_K_PRIMARY)
    sign_stability = bootstrap_sign_stability(ld_primary)

    # per-book delta at K=5 (sign consistency across books)
    per_book_delta = []
    for b in usable:
        brecs = [r for r in all_records if r.get("book") == b]
        if not brecs:
            continue
        bagg, bld = aggregate(brecs, WINDOW_K_PRIMARY)
        if bagg.get("delta_ld") is not None:
            per_book_delta.append({"book": b, "n_ld": bagg["n_ld"],
                                   "delta_ld": bagg["delta_ld"]})
    n_book_pos = sum(1 for x in per_book_delta if x["delta_ld"] > 0)
    n_book_eval = len(per_book_delta)

    # Interpretation-honesty telemetry: is the true entity just the top-freq one?
    ld_true_top_freq = None
    if ld_primary:
        hits = 0
        for r in ld_primary:
            # freq_only correct == "true entity is (a) top-freq compatible entity"
            hits += r["correct"]["freq_only"]
        ld_true_top_freq = hits / len(ld_primary)

    pa = primary["per_arm"]
    delta_ld = primary.get("delta_ld")
    ov_prec = pa[MECHANISM_ARM]["ld_prec"]
    rc_prec = pa[BASELINE_ARM]["ld_prec"]
    guard_ok = (ov_prec is not None and rc_prec is not None
                and ov_prec >= rc_prec - GUARD_PRECISION_EPS)

    # Verdict
    if delta_ld is None or primary["n_ld"] < 5:
        verdict = "UNKNOWN"
        verdict_msg = "LD subset too small (n_ld=%s) to decide" % primary.get("n_ld")
    elif delta_ld <= 0.0:
        verdict = "HARD_FAIL"
        verdict_msg = ("recency dominates even at distance: delta_ld=%.4f <= 0 "
                       "(overlay=%.4f vs recency=%.4f, n_ld=%d)"
                       % (delta_ld, pa[MECHANISM_ARM]["ld_acc"],
                          pa[BASELINE_ARM]["ld_acc"], primary["n_ld"]))
    elif (delta_ld >= HP_DELTA and sign_stability is not None
          and sign_stability >= HP_SIGN_STABILITY and guard_ok):
        verdict = "HARD_PASS"
        verdict_msg = ("maintained overlay beats recency at distance: delta_ld=%.4f "
                       "(overlay=%.4f vs recency=%.4f), sign_stability=%.3f, "
                       "overlay_prec=%.4f>=recency_prec-eps=%.4f, n_ld=%d"
                       % (delta_ld, pa[MECHANISM_ARM]["ld_acc"], pa[BASELINE_ARM]["ld_acc"],
                          sign_stability, ov_prec, rc_prec - GUARD_PRECISION_EPS,
                          primary["n_ld"]))
    else:
        verdict = "MIDDLE_BAND"
        verdict_msg = ("overlay > recency but sub-threshold or guard/stability short: "
                       "delta_ld=%.4f, sign_stability=%s, guard_ok=%s, n_ld=%d"
                       % (delta_ld, sign_stability, guard_ok, primary["n_ld"]))

    elapsed = time.perf_counter() - t0
    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": "%s: %s" % (ANCHOR_NAME, verdict),
        "elapsed_s": round(elapsed, 3),
        "anchor_name": ANCHOR_NAME,
        "run_mode": run_mode,
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "host": platform.node(),
        "corpus": {"source": "LitBank coref (dbamman/litbank), CC-BY 4.0",
                   "n_books_requested": len(books), "n_books_usable": len(usable),
                   "fetched_this_run": fetched, "failed": failed},
        "config": {"window_K_primary": WINDOW_K_PRIMARY, "window_K_sweep": WINDOW_K_SWEEP,
                   "overlay_beta": OVERLAY_BETA, "overlay_tiebreak_lambda": OVERLAY_TIEBREAK_LAMBDA,
                   "target_pronouns": sorted(TARGET_PRONOUNS),
                   "n_bootstrap": N_BOOTSTRAP, "bootstrap_seed": BOOTSTRAP_SEED},
        "primary_K5": primary,
        "sweep_over_K": sweep,
        "delta_ld": delta_ld,
        "bootstrap_sign_stability": sign_stability,
        "per_book_delta_K5": per_book_delta,
        "n_books_delta_positive": n_book_pos,
        "n_books_delta_evaluated": n_book_eval,
        "ld_true_is_top_freq_rate": ld_true_top_freq,
        "guard_precision_ok": guard_ok,
        "arms_differ_digests": digests,
        "arms_differ_verified": True,
        "book_failures": book_failures,
        "expected_n_units": len(usable),
        "cardinality_ok": (len(per_book) == len(usable) - len(book_failures)),
    }
    tmp = os.path.join(out_dir, "metrics.json.tmp")
    final = os.path.join(out_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, final)
    return metrics, out_dir


def _write_start_marker(out_dir, run_mode, expected_n):
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": run_mode,
              "expected_n_units": expected_n, "host": platform.node()}
    tmp = os.path.join(out_dir, "_start_marker.json.tmp")
    final = os.path.join(out_dir, "_start_marker.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, final)


def _write_crash_metrics(out_dir, exc):
    os.makedirs(out_dir, exist_ok=True)
    diag = {"verdict": "CELL_CRASHED",
            "verdict_msg": "%s: %s" % (type(exc).__name__, str(exc)[:500]),
            "summary": "CELL_CRASHED: %s" % type(exc).__name__,
            "elapsed_s": 0.0, "anchor_name": ANCHOR_NAME,
            "traceback": traceback.format_exc()[:5000],
            "ts_iso": datetime.now(timezone.utc).isoformat()}
    tmp = os.path.join(out_dir, "metrics.json.tmp")
    final = os.path.join(out_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, final)


# ----------------------------------------------------------------------------
# SELF-TEST (real code path: temp conll -> parse -> all 4 real resolvers)
# ----------------------------------------------------------------------------
def self_test():
    import tempfile
    # Construct a tiny conll where a gendered pronoun's true antecedent (cluster 7,
    # entity "alice", frequently mentioned) is FAR (>K mentions back), while a
    # nearer compatible distractor (cluster 9, "mary") sits inside the window.
    # Expected: recency_window MISSES (picks near distractor), maintained_overlay
    # HITS (alice accumulated salience). Proves the real code path + the mechanism.
    lines = ["#begin document (selftest); part 0"]
    def tok(sidx, tidx, word, coref="_"):
        return "selftest\t0\t%d\t%s\t_\t_\t_\t_\t_\t_\t_\t_\t%s" % (tidx, word, coref)
    # Alice (cluster 7) mentioned 4x EARLY (builds accumulated salience/frequency)...
    for s in range(0, 4):
        lines += [tok(s, 0, "Alice", "(7)"), tok(s, 1, "walked"), ""]
    # ...then a GAP of distinct distractor entities (each its own head string /
    # gold cluster) so Alice's LAST mention falls far outside the window K.
    fillers = [("Bob", 11), ("garden", 12), ("letter", 13),
               ("carriage", 14), ("village", 15), ("candle", 16)]
    for i, (w, cid) in enumerate(fillers):
        lines += [tok(4 + i, 0, w, "(%d)" % cid), tok(4 + i, 1, "appeared"), ""]
    # nearer distractor Mary (cluster 9) just before the pronoun (inside window)
    lines += [tok(10, 0, "Mary", "(9)"), tok(10, 1, "arrived"), ""]
    # pronoun "she" gold-refers to Alice (cluster 7); her last mention is far back
    lines += [tok(11, 0, "Later"), tok(11, 1, "she", "(7)"), tok(11, 2, "left"), ""]
    with tempfile.NamedTemporaryFile("w", suffix=".conll", delete=False,
                                     encoding="utf-8") as tf:
        tf.write("\n".join(lines) + "\n")
        tmp_path = tf.name
    try:
        mentions = parse_conll(tmp_path)
        # parse sanity
        heads = [m["head"] for m in mentions]
        assert heads.count("alice") == 4, "parse: expected 4 alice mentions, got %d" % heads.count("alice")
        assert "mary" in heads and "she" in heads, "parse: missing mary/she"
        targets = build_targets(mentions)
        assert len(targets) == 1, "expected 1 target (she->cluster7), got %d" % len(targets)
        tgt = targets[0]["target"]
        gold_dist = targets[0]["gold_dist"]
        assert gold_dist > WINDOW_K_PRIMARY, ("self-test antecedent must be long-distance: "
                                              "gold_dist=%d K=%d" % (gold_dist, WINDOW_K_PRIMARY))
        # REAL resolvers
        rw = resolve_recency_window(tgt, mentions, WINDOW_K_PRIMARY)
        ru = resolve_recency_unbounded(tgt, mentions)
        ov = resolve_maintained_overlay(tgt, mentions)
        fq = resolve_freq_only(tgt, mentions)
        # window-K recency picks the near distractor Mary (cluster 9) -> WRONG
        assert rw is not None and rw["cluster"] == 9, \
            "recency_window should pick near Mary(9), got %s" % (rw and rw["cluster"])
        # unbounded recency also picks nearest compatible = Mary (9) -> WRONG here
        assert ru is not None and ru["cluster"] == 9, \
            "recency_unbounded should pick nearest compatible Mary(9), got %s" % (ru and ru["cluster"])
        # maintained overlay reaches Alice (cluster 7) via accumulated frequency -> RIGHT
        assert ov is not None and ov["cluster"] == 7, \
            "maintained_overlay should reach Alice(7), got %s" % (ov and ov["cluster"])
        # freq_only also reaches Alice (4 mentions vs 1) -> RIGHT (ablation sanity)
        assert fq is not None and fq["cluster"] == 7, \
            "freq_only should pick Alice(7), got %s" % (fq and fq["cluster"])
        # arms-differ on this record
        recs = evaluate_book(mentions, WINDOW_K_PRIMARY)
        digs = arms_must_differ(recs)
        assert digs[BASELINE_ARM] != digs[MECHANISM_ARM], "arms-differ self-test failed"
        # aggregate + bootstrap smoke (no network)
        agg, ld = aggregate(recs, WINDOW_K_PRIMARY)
        assert agg["n_ld"] == 1 and agg["delta_ld"] is not None, "aggregate self-test failed"
        # compatibility filter: masc pronoun must reject a fem pronoun candidate
        masc = {"gender": "masc", "number": "singular"}
        femc = {"gender": "fem", "number": "singular"}
        assert not compatible(masc, femc), "compat: masc/fem must conflict"
        assert compatible(masc, {"gender": None, "number": None}), "compat: nominal must pass"
        print("SELF-TEST PASS: parse + 4 real resolvers + long-distance mechanism + "
              "arms-differ + compat filter all verified (glass-box, no network).")
        return 0
    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass


# ----------------------------------------------------------------------------
# MAIN
# ----------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()

    if args.self_test:
        sys.exit(self_test())

    books = FULL_BOOKS[:SMOKE_N] if args.smoke else FULL_BOOKS
    run_mode = "smoke" if args.smoke else "full"
    metrics, out_dir = run(books, run_mode)
    print("[%s] verdict=%s" % (run_mode, metrics["verdict"]))
    print(metrics["verdict_msg"])
    p = metrics["primary_K5"]["per_arm"]
    print("K=5 LD subset n_ld=%d:" % metrics["primary_K5"]["n_ld"])
    for arm in ARMS:
        print("  %-24s ld_acc=%s ld_prec=%s attempt=%s"
              % (arm, _f(p[arm]["ld_acc"]), _f(p[arm]["ld_prec"]), _f(p[arm]["ld_attempt_rate"])))
    print("  delta_ld(vs recency_unbounded)=%s  vs_window_wall=%s  vs_freq=%s"
          % (_f(metrics["primary_K5"].get("delta_ld")),
             _f(metrics["primary_K5"].get("delta_ld_vs_window")),
             _f(metrics["primary_K5"].get("delta_ld_vs_freq"))))
    print("  sign_stability=%s  books_pos=%d/%d  ld_true_top_freq=%s"
          % (_f(metrics["bootstrap_sign_stability"]),
             metrics["n_books_delta_positive"], metrics["n_books_delta_evaluated"],
             _f(metrics["ld_true_is_top_freq_rate"])))
    print("metrics -> %s" % os.path.join(out_dir, "metrics.json"))


def _f(x):
    return "None" if x is None else ("%.4f" % x)


if __name__ == "__main__":
    _out = os.path.join(REPO_ROOT, "data", "exp_%s" % ANCHOR_NAME)
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # noqa: BLE001 -- crash-diag then re-raise (no BaseException)
        _write_crash_metrics(_out, e)
        raise
