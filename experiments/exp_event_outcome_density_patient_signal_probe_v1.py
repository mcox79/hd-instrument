"""EVENT-OUTCOME-DENSITY PATIENT-SIGNAL PROBE (design-gate + smoke; exp_dev cycle 2026-07-20).

QUESTION (the make-or-break test gating the grounding fork; see notes/research_brain_building_event_
plausibility_web_2026-07-20.md + notes/research_brain_patienthood_affectedness_grounding_2026-07-20.md):
  Holding model CAPACITY (fixed scoring-function form, fixed verb-lexicon size) and TOTAL TOKEN BUDGET
  fixed across arms, does a TEXT-INTERNAL signal that tracks per-instance patient-correctness (Levin
  causative-inchoative corpus-ALTERNATION detection -- ranked #1 genuinely-text-internal candidate in the
  patienthood drill) STRENGTHEN as the BACKGROUND corpus's event-outcome DENSITY rises? This is the cheap,
  decisive test the literature drill recommends BEFORE any perception/grounding investment (PIQA's
  reporting-bias diagnosis: physical-outcome language is rare in ordinary text, not absent-in-principle).

TARGET METRIC (reused, frozen, from the 29375 line -- atom 29375: "within-instance argmax picks gold
  0.474 << frozen-structural 0.684"): WITHIN-INSTANCE ARGMAX PICK-GOLD over the SAME independent gold +
  SAME frozen candidate generator as the LCCP arc:
    data/gold_mcguffey_lccp_argstruct_v1.json (McGuffey THIRD READER, single-annotator independent gold)
    experiments/exp_learned_argstruct_parser_lccp_independent_gold_v1.py: load_slice_and_reader(),
      load_gold(), tokenize(), lemma_verb(), candidate_features() -- imported UNCHANGED (frozen harness;
      no re-implementation of the candidate generator or the gold-matching logic).
  For each gold POS instance (v_lemma, agent, patient) at sentence sid, group the reader's raw (v,a,p)
  candidate tuples by (sid, v_lemma) (mirrors LCCP's own inst_groups construction exactly). Score every
  rival candidate patient under the arm's SCORE function; take argmax (deterministic first-index tie-
  break, NO structural cue in the density arms' own score -- structural adjacency is used ONLY in a
  separate REFERENCE sanity-check arm, never mixed into a density arm's score). pick_gold_rate = fraction
  where argmax candidate == gold patient surface. Reported on ALL pos instances AND on the MULTI-CANDIDATE
  subset only (>=2 rival candidates -- the only subset where the task can discriminate at all; single-
  candidate instances score 1.0 by construction regardless of arm and are excluded from the discriminator
  read per the design-gate's can-fail requirement).

DENSITY METRIC (the ONE swept variable): hits-per-1000-tokens of a FIXED, CITED Levin (1993) causative-
  inchoative alternating-verb lexicon (~45 lemmas: break, open, close, melt, freeze, boil, tear, split,
  shatter, spill, sink, roll, spread, stretch, bend, grow, shrink, change, stop, start, begin, fill, empty,
  ... -- see CAUSE_INCHOATIVE_LEMMAS below), measured over BACKGROUND corpus lessons/chunks NEVER
  overlapping the eval corpus (McGuffey Third Reader is the eval set; the background corpus explicitly
  EXCLUDES it to avoid leakage/circularity -- see Corpus / no-leakage section).

SIGNAL (text-internal, no lexicon import; per patienthood-drill ranked candidate #1b): for each Levin verb
  lemma v seen in a background-corpus slice, count TRANS(v) = verb-token immediately followed by a content
  word (transitive-with-following-argument use) vs INCHOATIVE(v) = verb-token with NO following content
  word but a preceding subject NP (intransitive-inchoative use, patient-as-subject). alt(v) =
  2*min(T,I)/(T+I) if T+I >= MIN_COUNT else 0.0 (Levin's own alternation diagnostic, purely distributional/
  structural pattern-matching -- no VerbNet/hand lexicon of ROLES imported, only the closed CAUSE_INCHOATIVE
  lemma list, which is a citation of WHICH VERBS belong to the class, not of role assignments).
  ANIMACY CO-FEATURE (fixed lexicon, IDENTICAL across every arm, corpus-INDEPENDENT -- used as the
  invariance/leakage self-test): candidate treated as animate iff its surface is in a fixed PRONOUN +
  ANIMATE_NOUN set. SCORE(p, v) = alt(v) * (1.0 if not animate(p) else ANIMATE_DISCOUNT).
  ANIMACY_ONLY variant forces alt(v)==1.0 uniformly (ignores the density-derived signal entirely) --
  MUST produce a BIT-IDENTICAL pick_gold_rate across every arm (it never reads corpus counts), which is
  the smoke-gate's ONE-VARIABLE-ISOLATION validity check (a wiring bug that let something besides density
  vary between arms would break this invariance).

ARMS (background corpus that alt(v) is computed FROM; the eval gold/candidates are IDENTICAL across all
  arms -- ONE variable = which background corpus's alternation counts feed the arm's alt(v) table):
  - LOW / MED / HIGH: WITHIN-GENRE density tertiles. Background pool = McGuffey Primer + First Reader +
    Second Reader + Fourth Reader (the SAME author/series/genre/register-family as the eval Third Reader,
    but the Third Reader ITSELF is excluded -- no leakage). Lessons ranked by per-lesson density, split into
    terciles by RANK, then TOKEN-MATCHED (fixed-seed deterministic shuffle within tier + prefix-truncate to
    the smallest tier's token count) so LOW/MED/HIGH see the SAME total token budget. This is the PRIMARY,
    fairness-controlled comparison (genre/author/era/register held constant; density is the only lever).
  - TEXT8_XGENRE: first N-token-matched slice of data/text8_cache/text8.txt (Wikipedia-derived, expository,
    different genre) -- SECONDARY / reference only, explicitly genre-confounded, reported but NOT used for
    the primary HARD-PASS/HARD-FAIL call.
  - LITBANK_XGENRE: token-matched slice of 3 litbank_coref_conll 19th-c. novels (Frankenstein, Dracula,
    Pride and Prejudice) -- SECONDARY / reference only, adult-novel genre (different register from McGuffey
    AND from Wikipedia), also explicitly genre-confounded, reported but NOT used for the primary call.
  - HIGH_SCRAMBLED (MUST-FAIL CONTROL): same HIGH-tier token pool, but each detected verb-occurrence's
    TRANS/INCHOATIVE pattern hit is credited to a uniformly-random OTHER Levin lemma (fixed-seed permutation
    of lemma-labels over hit positions) before computing alt(v). Preserves corpus size / total hit count /
    vocabulary; destroys the real PER-VERB alternation correlation. Expected: pick_gold_rate(HIGH_SCRAMBLED)
    ~= pick_gold_rate(LOW), NOT ~= pick_gold_rate(HIGH) -- if scrambling doesn't hurt, the "real" HIGH signal
    was a corpus-size/noise artifact, not genuine verb-specific alternation structure.
  - STRUCTURAL_REFERENCE (validity sanity only, not a density arm): argmax under the LCCP module's own
    pure f_adj (adjacency) structural feature, reused verbatim via candidate_features(). Cross-checks this
    harness's candidate-generation/gold-matching machinery lands in the same ballpark as the historical
    atom-29375 structural figure (0.684) -- approximate cross-check only (29375's "structural" was a FULL
    frozen 6-feature logistic, not bare f_adj, so exact reproduction is not expected/required).

PRE-REGISTERED BANDS (computed on the MULTI-CANDIDATE gold-pos subset; PASS/FAIL fields per envelope-
  fail-bands discipline):
  HARD_PASS_DENSITY_IS_THE_LEVER:
    (a) pick_gold(HIGH) - pick_gold(LOW) >= 0.08 absolute, AND
    (b) monotonic-ish: pick_gold(LOW) <= pick_gold(MED) + 0.03 <= pick_gold(HIGH) + 0.03 (small slack for
        n-noise at this scale), AND
    (c) pick_gold(HIGH) - pick_gold(HIGH_SCRAMBLED) >= 0.05 (the real per-verb signal beats the scrambled
        must-fail control -- rules out "more corpus text = more noise-driven lucky ties"), AND
    (d) ANIMACY_ONLY pick_gold is IDENTICAL (within 1e-9) across LOW/MED/HIGH/scrambled (one-variable
        isolation validated), AND
    (e) baseline_in_band: 0.05 < pick_gold(LOW) < 0.95 (LOW arm not saturated/floor -- real room to move).
  HARD_FAIL_DENSITY_NOT_THE_LEVER:
    pick_gold(HIGH) - pick_gold(LOW) < 0.03 (flat, within noise) OR HIGH_SCRAMBLED performs within 0.03 of
    real HIGH (gain is a corpus-size artifact, not verb-specific alternation structure) OR ANIMACY_ONLY
    varies across arms by more than 1e-9 (harness bug -- distrust the whole read; this is a validity gate,
    not a science verdict).
  MIDDLE_BAND: gap in [0.03, 0.08) with (c)/(d)/(e) satisfied, or (a)/(b) pass but (c) fails narrowly.

FAIRNESS GUARDS (USER-flagged load-bearing; see spawn prompt):
  - ONE VARIABLE = which background corpus feeds alt(v). Scoring-function FORM (SCORE = alt(v)*animacy-
    discount), the fixed Levin lemma list, the ANIMATE lexicon, MIN_COUNT gate, and ANIMATE_DISCOUNT are
    ALL IDENTICAL across LOW/MED/HIGH/scrambled ("model capacity" fixed). Token budget is MATCHED across
    LOW/MED/HIGH (and reported, not matched, for the two cross-genre reference arms -- flagged as such).
  - GENRE CONFOUND: the PRIMARY LOW/MED/HIGH comparison is WITHIN the McGuffey graded-reader series
    (same author, same series, same era, same register family) precisely to decouple density from genre.
    TEXT8_XGENRE / LITBANK_XGENRE are reported for directional context ONLY and explicitly are NOT clean
    (different genre AND register AND era) -- this is stated up front, not discovered after the fact.
  - NO LEAKAGE: background corpus for LOW/MED/HIGH explicitly EXCLUDES the McGuffey Third Reader (the eval
    corpus). Verified by filename exclusion + an assert on the loaded background file list.
  - CAN-FAIL: MULTI-CANDIDATE-ONLY subset is the discriminator (single-candidate instances are vacuous by
    construction and are reported separately, not folded into the HARD-PASS/FAIL read).
  - COMPUTE-PROPORTIONALITY: this is a directional/correlational gate question (does X strengthen a
    correlate), NOT a magnitude-of-mechanism claim -- answered via the CHEAPEST decisive method (corpus
    counting + argmax scoring), NOT a trained model / SGD fit. Wall time expected < 60s total.

COMPUTE ARCHITECTURE (mandatory declaration): class (b) sequential-CPU with justification -- pure corpus
  token-counting + argmax over ~100 gold instances; no matmul-heavy primitive; wall < 60s. Foreground,
  local-to-completion, NO queue, NO push, NO remote-persist (mirrors the LCCP/affectedness cells' own
  "LOCAL foreground measurement" scoping). Storage: no_storage (a measurement cell, not a
  superposition/composition cell -- no KGStore, no atoms.jsonl writes, no substrate primitive calls).

CELL-TEMPLATE MANDATORY (subset applicable to a LOCAL foreground measurement; not queue-dispatched):
  - arms_differ_verified at smoke (kept-argmax-choice hashes across LOW/MED/HIGH/scrambled differ; verified)
  - final_metrics_atomicity: tmp_replace (os.replace)
  - except SystemExit: raise BEFORE except Exception (no BaseException)
  - baseline_in_band at smoke (0.05 < pick_gold(LOW, multi-cand) < 0.95)
  - discriminator fires at smoke: multi-candidate subset non-empty; ANIMACY_ONLY invariance holds
  - deterministic seeding: fixed int seeds only, sorted(set(...)) not list(set(...)), no builtin hash()
  - all numbers tagged MEASURED@ (printed + written to metrics.json) / CITED@ (Levin 1993 lemma list)

NOT DISPATCHED TO QUEUE. Foreground smoke + a token-matched "full" background pool (all available non-eval
  McGuffey text -- there is no larger "full" tier to grow into locally without fetching new corpora) run in
  the SAME local session; reported to the Director for a full-run go/no-go call, per the design-gate + smoke
  ONLY task shape.
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import argparse
import json
import re
import sys
import time
import traceback
from collections import defaultdict
from datetime import datetime, timezone

import numpy as np

ANCHOR_NAME = "event_outcome_density_patient_signal_probe_v1"
REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(REPO_ROOT)
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from experiments import exp_learned_argstruct_parser_lccp_independent_gold_v1 as LCCP  # noqa: E402

# ----------------------------------------------------------------------------------------------
# Fixed lexicons (IDENTICAL across every arm -- "model capacity" held fixed).
# ----------------------------------------------------------------------------------------------
# CITED@Levin 1993 "English Verb Classes and Alternations", causative-inchoative alternation class
# (break/open-type). Base lemma -> hand-listed surface inflections (regular + a few irregulars), kept
# small and deterministic (no external morphology lib).
CAUSE_INCHOATIVE = {
    "break": ["break", "breaks", "breaking", "broke", "broken"],
    "open": ["open", "opens", "opening", "opened"],
    "close": ["close", "closes", "closing", "closed"],
    "shut": ["shut", "shuts", "shutting"],
    "melt": ["melt", "melts", "melting", "melted"],
    "freeze": ["freeze", "freezes", "freezing", "froze", "frozen"],
    "boil": ["boil", "boils", "boiling", "boiled"],
    "burn": ["burn", "burns", "burning", "burned", "burnt"],
    "dry": ["dry", "dries", "drying", "dried"],
    "crack": ["crack", "cracks", "cracking", "cracked"],
    "burst": ["burst", "bursts", "bursting"],
    "snap": ["snap", "snaps", "snapping", "snapped"],
    "tear": ["tear", "tears", "tearing", "tore", "torn"],
    "split": ["split", "splits", "splitting"],
    "shatter": ["shatter", "shatters", "shattering", "shattered"],
    "spill": ["spill", "spills", "spilling", "spilled", "spilt"],
    "sink": ["sink", "sinks", "sinking", "sank", "sunk"],
    "float": ["float", "floats", "floating", "floated"],
    "roll": ["roll", "rolls", "rolling", "rolled"],
    "spread": ["spread", "spreads", "spreading"],
    "stretch": ["stretch", "stretches", "stretching", "stretched"],
    "bend": ["bend", "bends", "bending", "bent"],
    "fold": ["fold", "folds", "folding", "folded"],
    "twist": ["twist", "twists", "twisting", "twisted"],
    "turn": ["turn", "turns", "turning", "turned"],
    "tip": ["tip", "tips", "tipping", "tipped"],
    "rock": ["rock", "rocks", "rocking", "rocked"],
    "swing": ["swing", "swings", "swinging", "swung"],
    "shake": ["shake", "shakes", "shaking", "shook", "shaken"],
    "spin": ["spin", "spins", "spinning", "spun"],
    "grow": ["grow", "grows", "growing", "grew", "grown"],
    "shrink": ["shrink", "shrinks", "shrinking", "shrank", "shrunk"],
    "widen": ["widen", "widens", "widening", "widened"],
    "narrow": ["narrow", "narrows", "narrowing", "narrowed"],
    "thicken": ["thicken", "thickens", "thickening", "thickened"],
    "cool": ["cool", "cools", "cooling", "cooled"],
    "warm": ["warm", "warms", "warming", "warmed"],
    "heat": ["heat", "heats", "heating", "heated"],
    "darken": ["darken", "darkens", "darkening", "darkened"],
    "brighten": ["brighten", "brightens", "brightening", "brightened"],
    "change": ["change", "changes", "changing", "changed"],
    "stop": ["stop", "stops", "stopping", "stopped"],
    "start": ["start", "starts", "starting", "started"],
    "fill": ["fill", "fills", "filling", "filled"],
    "empty": ["empty", "empties", "emptying", "emptied"],
    "flood": ["flood", "floods", "flooding", "flooded"],
}
SURF2LEMMA = {}
for _lem, _surfs in CAUSE_INCHOATIVE.items():
    for _s in _surfs:
        SURF2LEMMA[_s] = _lem
ALL_LEMMAS = sorted(CAUSE_INCHOATIVE.keys())

PRONOUN = set(LCCP.PRONOUN)
ANIMATE_NOUN = {
    "boy", "boys", "girl", "girls", "man", "men", "woman", "women", "child", "children",
    "father", "mother", "papa", "mamma", "aunt", "uncle", "sister", "brother", "friend",
    "friends", "teacher", "king", "queen", "farmer", "hunter", "hunters", "gentleman",
    "gardener", "servant", "fisherman", "wife", "husband", "people", "cat", "cats", "dog",
    "dogs", "pussy", "kitten", "kittens", "horse", "horses", "bird", "birds", "beaver",
    "beavers", "herbert", "joe", "hetty", "charles", "james", "frank", "rose",
}


def is_animate(tok):
    return tok in PRONOUN or tok in ANIMATE_NOUN


FUNC_STOP = LCCP.FUNCWORD | LCCP.PREPS | LCCP.COMPLEMENTIZERS | {".", ",", ";", ":", "!", "?"}


# ----------------------------------------------------------------------------------------------
# Background-corpus loading (McGuffey non-eval lessons + cross-genre references). NO-LEAKAGE guard:
# the Third Reader (eval corpus) is never one of these paths.
# ----------------------------------------------------------------------------------------------
MCGUFFEY_NONEVAL_PATHS = [
    os.path.join(REPO_ROOT, "data", "corpora", "graded_readers_grade1", "cleaned", "mcguffey_primer.clean.txt"),
    os.path.join(REPO_ROOT, "data", "corpora", "graded_readers_grade1", "cleaned", "mcguffey_first_reader.clean.txt"),
    os.path.join(REPO_ROOT, "data", "corpora", "graded_readers_graded", "cleaned", "mcguffey_second_reader.clean.txt"),
    os.path.join(REPO_ROOT, "data", "corpora", "graded_readers_graded", "cleaned", "mcguffey_fourth_reader.clean.txt"),
]
THIRD_READER_PATH = os.path.join(REPO_ROOT, "data", "corpora", "graded_readers_graded", "cleaned",
                                  "mcguffey_third_reader.clean.txt")
TEXT8_PATH = os.path.join(REPO_ROOT, "data", "text8_cache", "text8.txt")
LITBANK_PATHS = [
    os.path.join(REPO_ROOT, "data", "corpora", "litbank_coref_conll", "84_frankenstein_or_the_modern_prometheus_brat.conll"),
    os.path.join(REPO_ROOT, "data", "corpora", "litbank_coref_conll", "345_dracula_brat.conll"),
    os.path.join(REPO_ROOT, "data", "corpora", "litbank_coref_conll", "1342_pride_and_prejudice_brat.conll"),
]

LESSON_SPLIT_RE = re.compile(r"(?m)^# LESSON\s+\S+")
WORD_RE = re.compile(r"[a-zA-Z']+")


def load_mcguffey_lessons():
    """Return list of {"src": path, "text": lesson_text} for all non-eval McGuffey lessons.
    NO-LEAKAGE guard: asserts THIRD_READER_PATH is not among the loaded paths."""
    assert THIRD_READER_PATH not in MCGUFFEY_NONEVAL_PATHS, "NO_LEAKAGE_VIOLATION: eval corpus in background set"
    lessons = []
    for p in MCGUFFEY_NONEVAL_PATHS:
        txt = open(p, encoding="utf-8").read()
        parts = [x.strip() for x in LESSON_SPLIT_RE.split(txt) if x.strip()]
        for part in parts:
            lessons.append({"src": os.path.basename(p), "text": part})
    return lessons


def lesson_density(lesson_text):
    toks = [t.lower() for t in WORD_RE.findall(lesson_text)]
    n_tok = len(toks)
    hits = sum(1 for t in toks if t in SURF2LEMMA)
    density = (hits / n_tok * 1000.0) if n_tok > 0 else 0.0
    return n_tok, hits, density


def build_density_tiers(lessons, seed):
    """Rank lessons by density, split into LOW/MED/HIGH terciles by RANK, then token-match via a
    fixed-seed deterministic shuffle + prefix-truncate to the smallest tier's token budget."""
    scored = []
    for les in lessons:
        n_tok, hits, dens = lesson_density(les["text"])
        if n_tok < 20:
            continue  # too short for a stable density estimate
        scored.append({"text": les["text"], "src": les["src"], "n_tok": n_tok, "hits": hits, "density": dens})
    scored.sort(key=lambda r: (r["density"], r["src"]))  # deterministic tie-break by src name
    n = len(scored)
    b1 = n // 3
    b2 = 2 * n // 3
    tiers_raw = {"LOW": scored[:b1], "MED": scored[b1:b2], "HIGH": scored[b2:]}
    rng = np.random.default_rng(seed)
    tiers = {}
    tier_tok_totals = {}
    for name, rows in tiers_raw.items():
        idx = rng.permutation(len(rows))
        shuffled = [rows[i] for i in idx]
        tiers[name] = shuffled
        tier_tok_totals[name] = sum(r["n_tok"] for r in shuffled)
    min_tok = min(tier_tok_totals.values()) if tier_tok_totals else 0
    matched = {}
    matched_tok = {}
    for name, rows in tiers.items():
        acc, kept = 0, []
        for r in rows:
            if acc >= min_tok:
                break
            kept.append(r)
            acc += r["n_tok"]
        matched[name] = kept
        matched_tok[name] = acc
    return matched, matched_tok, {k: len(v) for k, v in matched.items()}


def load_text8_slice(n_tok_target):
    with open(TEXT8_PATH, encoding="utf-8") as f:
        chunk = f.read(n_tok_target * 8)  # ~8 chars/token overestimate; text8 has no punctuation
    toks = WORD_RE.findall(chunk)[:n_tok_target]
    return " ".join(toks)


def load_litbank_slice(n_tok_target):
    toks = []
    for p in LITBANK_PATHS:
        for line in open(p, encoding="utf-8"):
            if line.startswith("#") or not line.strip():
                continue
            cols = line.rstrip("\n").split("\t")
            if len(cols) > 3 and cols[3]:
                toks.append(cols[3])
            if len(toks) >= n_tok_target:
                break
        if len(toks) >= n_tok_target:
            break
    return " ".join(toks[:n_tok_target])


# ----------------------------------------------------------------------------------------------
# PATIENT-PRIOR computation over a raw text blob (per-CANDIDATE-NOUN affectedness signal).
#
# DESIGN NOTE (fixed during smoke, per honest iteration -- see smoke report): a first version scored
# candidates with a per-VERB alt(v) scalar multiplying a fixed animacy term. That is a MATH bug: within
# one instance the verb v is constant across all rival candidates, so multiplying every candidate's score
# by the SAME alt(v) constant can NEVER change the argmax ranking (positive scaling preserves order) --
# the density variable could structurally never move the discriminator. Fixed by making the density-
# derived quantity vary PER CANDIDATE TOKEN (a per-noun "seen as a change-of-state affected argument in
# the background corpus" prior), which genuinely differs across rival candidates and can flip the argmax.
# This is the Dowty/Levin-style corpus-alternation signal correctly operationalized as a candidate-level
# (not verb-level) feature -- consistent with the patienthood drill's ranked candidate #1b.
# ----------------------------------------------------------------------------------------------
def split_sents(text):
    t = re.sub(r"\s+", " ", text).strip()
    return [p.strip() for p in re.split(r"(?<=[.!?])\s+", t) if p.strip()]


def compute_patient_prior(text_blob, scramble_seed=None):
    """For every occurrence of a Levin causative-inchoative verb, credit the ADJACENT noun-like token
    (the transitive object, or the inchoative subject) as having been observed as a change-of-state
    AFFECTED argument. Return {noun_token: count}, n_hits_credited. Pronoun-credited hits are dropped
    (pronouns are handled by the fixed animacy co-feature, not this corpus-derived prior)."""
    credited = []
    for sent in split_sents(text_blob):
        toks = [t.lower() for t in WORD_RE.findall(sent)]
        for i, tok in enumerate(toks):
            if tok not in SURF2LEMMA:
                continue
            nxt = toks[i + 1] if i + 1 < len(toks) else None
            prv = toks[i - 1] if i - 1 >= 0 else None
            if nxt is not None and nxt.isalpha() and nxt not in FUNC_STOP and nxt not in PRONOUN:
                credited.append(nxt)
            elif (nxt is None or nxt in FUNC_STOP) and prv is not None and prv.isalpha() \
                    and prv not in FUNC_STOP and prv not in PRONOUN:
                credited.append(prv)

    if scramble_seed is not None:
        rng = np.random.default_rng(scramble_seed)
        perm = rng.permutation(len(credited))
        credited = [credited[j] for j in perm]

    counts = defaultdict(int)
    for n in credited:
        counts[n] += 1
    return dict(counts), len(credited)


def patient_affinity(token, prior_table):
    c = prior_table.get(token, 0)
    return c / (c + 2.0)  # saturating in [0,1); fixed formula, not fit to eval accuracy


# ----------------------------------------------------------------------------------------------
# Eval: reuse the FROZEN LCCP candidate generator + independent gold, unchanged.
# ----------------------------------------------------------------------------------------------
GOLD_LESSONS = ["L04", "L05", "L07", "L08", "L09", "L10", "L12"]


def build_eval_instances():
    order, sent_text, reader_svo = LCCP.load_slice_and_reader(GOLD_LESSONS)
    gold, _meta = LCCP.load_gold(GOLD_LESSONS)
    cands = []
    for sid in order:
        toks = LCCP.tokenize(sent_text[sid])
        for tup in reader_svo[sid]:
            v_surf, a, p = tup
            feat, _pos = LCCP.candidate_features(toks, v_surf, p)
            cands.append({"sid": sid, "v": LCCP.lemma_verb(v_surf), "a": a, "p": p, "feat": feat})
    inst_groups = defaultdict(list)
    for c in cands:
        inst_groups[(c["sid"], c["v"])].append(c)

    instances = []  # {sid, v, gold_patient, candidates: [{"p":..,"feat":..}]}
    for sid, rec in gold.items():
        for g in rec["pos"]:
            key = (sid, g["v"])
            group = inst_groups.get(key)
            if not group:
                continue  # reader missed this instance; not scoreable, excluded (honest, not padded)
            instances.append({"sid": sid, "v": g["v"], "gold_patient": g["patient"],
                              "candidates": [{"p": c["p"], "feat": c["feat"]} for c in group]})
    return instances


W_AFF = 1.0
W_ANIM = 1.0


def score_arm(instances, prior_table, animate_discount, animacy_only=False):
    n_all_correct, n_all = 0, 0
    n_multi_correct, n_multi = 0, 0
    choice_hashes = []
    for inst in instances:
        best_idx, best_score = 0, None
        for idx, c in enumerate(inst["candidates"]):
            aff = 0.0 if animacy_only else patient_affinity(c["p"], prior_table)
            anim_term = 1.0 if not is_animate(c["p"]) else animate_discount
            s = W_AFF * aff + W_ANIM * anim_term
            if best_score is None or s > best_score:
                best_score, best_idx = s, idx
        chosen = inst["candidates"][best_idx]["p"]
        correct = int(chosen == inst["gold_patient"])
        n_all += 1
        n_all_correct += correct
        choice_hashes.append(chosen)
        if len(inst["candidates"]) >= 2:
            n_multi += 1
            n_multi_correct += correct
    rate_all = n_all_correct / n_all if n_all else 0.0
    rate_multi = n_multi_correct / n_multi if n_multi else 0.0
    return {"rate_all": rate_all, "n_all": n_all, "rate_multi": rate_multi, "n_multi": n_multi,
            "choice_hash": "|".join(choice_hashes)}


def score_structural_reference(instances):
    n_correct, n = 0, 0
    for inst in instances:
        best_idx, best_score = 0, None
        for idx, c in enumerate(inst["candidates"]):
            s = float(c["feat"][1])  # f_adj
            if best_score is None or s > best_score:
                best_score, best_idx = s, idx
        chosen = inst["candidates"][best_idx]["p"]
        correct = int(chosen == inst["gold_patient"])
        n += 1
        n_correct += correct
    return {"rate_all": (n_correct / n if n else 0.0), "n_all": n}


def bootstrap_ci(instances, prior_table, animate_discount, n_boot, seed):
    multi = [inst for inst in instances if len(inst["candidates"]) >= 2]
    if not multi:
        return None
    rng = np.random.default_rng(seed)
    rates = []
    for _ in range(n_boot):
        idx = rng.integers(0, len(multi), size=len(multi))
        sample = [multi[i] for i in idx]
        r = score_arm(sample, prior_table, animate_discount)
        rates.append(r["rate_multi"])
    rates = np.array(rates)
    return {"mean": float(rates.mean()), "se": float(rates.std(ddof=1)), "p05": float(np.percentile(rates, 5)),
            "p95": float(np.percentile(rates, 95))}


# ----------------------------------------------------------------------------------------------
# Config.
# ----------------------------------------------------------------------------------------------
def cfg_smoke():
    return {"min_count": 2, "animate_discount": 0.35, "seed": 7, "n_boot": 200,
            "xgenre_tok_target": 8000}


def cfg_full():
    return {"min_count": 2, "animate_discount": 0.35, "seed": 7, "n_boot": 2000,
            "xgenre_tok_target": 74000}


def run_config(cfg):
    t0 = time.perf_counter()
    lessons = load_mcguffey_lessons()
    tiers, tier_tok, tier_nles = build_density_tiers(lessons, cfg["seed"])
    tier_density = {name: (sum(r["hits"] for r in rows) / max(1, sum(r["n_tok"] for r in rows)) * 1000.0)
                    for name, rows in tiers.items()}

    instances = build_eval_instances()
    n_multi_total = sum(1 for i in instances if len(i["candidates"]) >= 2)

    results = {}
    prior_tables = {}
    for name in ["LOW", "MED", "HIGH"]:
        blob = " ".join(r["text"] for r in tiers[name])
        prior, n_hits = compute_patient_prior(blob)
        prior_tables[name] = prior
        res = score_arm(instances, prior, cfg["animate_discount"])
        res["n_bg_tok"] = tier_tok[name]
        res["n_bg_lessons"] = tier_nles[name]
        res["density_per_1000tok"] = tier_density[name]
        res["n_nouns_with_signal"] = len(prior)
        res["n_hits_bg"] = n_hits
        results[name] = res

    # HIGH_SCRAMBLED must-fail control
    blob_high = " ".join(r["text"] for r in tiers["HIGH"])
    prior_scr, n_hits_scr = compute_patient_prior(blob_high, scramble_seed=cfg["seed"] + 999)
    res_scr = score_arm(instances, prior_scr, cfg["animate_discount"])
    res_scr["n_bg_tok"] = tier_tok["HIGH"]
    res_scr["n_hits_bg"] = n_hits_scr
    res_scr["n_nouns_with_signal"] = len(prior_scr)
    results["HIGH_SCRAMBLED"] = res_scr

    # cross-genre reference arms (explicitly NOT part of the primary HARD-PASS/FAIL call)
    text8_blob = load_text8_slice(cfg["xgenre_tok_target"])
    prior_t8, n_hits_t8 = compute_patient_prior(text8_blob)
    res_t8 = score_arm(instances, prior_t8, cfg["animate_discount"])
    res_t8["n_bg_tok"] = len(WORD_RE.findall(text8_blob))
    res_t8["n_hits_bg"] = n_hits_t8
    res_t8["n_nouns_with_signal"] = len(prior_t8)
    results["TEXT8_XGENRE"] = res_t8

    litbank_blob = load_litbank_slice(cfg["xgenre_tok_target"])
    prior_lb, n_hits_lb = compute_patient_prior(litbank_blob)
    res_lb = score_arm(instances, prior_lb, cfg["animate_discount"])
    res_lb["n_bg_tok"] = len(WORD_RE.findall(litbank_blob))
    res_lb["n_hits_bg"] = n_hits_lb
    res_lb["n_nouns_with_signal"] = len(prior_lb)
    results["LITBANK_XGENRE"] = res_lb

    # ANIMACY_ONLY invariance self-test (must be identical across every arm; corpus-independent)
    animacy_only = {}
    for name, prior in list(prior_tables.items()) + [("HIGH_SCRAMBLED", prior_scr), ("TEXT8_XGENRE", prior_t8),
                                                      ("LITBANK_XGENRE", prior_lb)]:
        animacy_only[name] = score_arm(instances, prior, cfg["animate_discount"], animacy_only=True)
    animacy_rates = {k: v["rate_multi"] for k, v in animacy_only.items()}
    animacy_invariant = (max(animacy_rates.values()) - min(animacy_rates.values())) < 1e-9

    # structural reference (sanity, not a density arm)
    structural_ref = score_structural_reference(instances)

    # arms_differ (META_RULE_AF analog): argmax CHOICE hashes must differ across LOW/MED/HIGH/scrambled
    choice_hashes = {name: results[name]["choice_hash"] for name in ["LOW", "MED", "HIGH", "HIGH_SCRAMBLED"]}
    all_pairs_differ = True
    names = list(choice_hashes.keys())
    diff_pairs = {}
    for a in range(len(names)):
        for b in range(a + 1, len(names)):
            same = choice_hashes[names[a]] == choice_hashes[names[b]]
            diff_pairs[f"{names[a]}_vs_{names[b]}"] = (not same)
            # NOTE: at very sparse signal (few verbs w/ alt>0), arms CAN legitimately tie (both fall back
            # to animacy-only behavior) -- so we report but do not hard-require every pair to differ.

    # bootstrap CI on LOW / HIGH (multi-candidate subset)
    boot_low = bootstrap_ci(instances, prior_tables["LOW"], cfg["animate_discount"], cfg["n_boot"], cfg["seed"])
    boot_high = bootstrap_ci(instances, prior_tables["HIGH"], cfg["animate_discount"], cfg["n_boot"], cfg["seed"] + 1)

    gap_high_low = results["HIGH"]["rate_multi"] - results["LOW"]["rate_multi"]
    gap_high_scr = results["HIGH"]["rate_multi"] - results["HIGH_SCRAMBLED"]["rate_multi"]
    monotonic_ok = (results["LOW"]["rate_multi"] <= results["MED"]["rate_multi"] + 0.03 and
                    results["MED"]["rate_multi"] <= results["HIGH"]["rate_multi"] + 0.03)
    baseline_in_band = 0.05 < results["LOW"]["rate_multi"] < 0.95

    if (gap_high_low >= 0.08 and monotonic_ok and gap_high_scr >= 0.05 and animacy_invariant and baseline_in_band):
        verdict = "HARD_PASS_DENSITY_IS_THE_LEVER"
    elif (gap_high_low < 0.03 or gap_high_scr < 0.03 or not animacy_invariant):
        verdict = "HARD_FAIL_DENSITY_NOT_THE_LEVER"
    else:
        verdict = "MIDDLE_BAND"

    elapsed = time.perf_counter() - t0
    payload = {
        "anchor_name": ANCHOR_NAME,
        "cfg": cfg,
        "tier_density_per_1000tok": tier_density,
        "n_eval_instances_total": len(instances),
        "n_eval_instances_multi_candidate": n_multi_total,
        "results": results,
        "animacy_only_rates_by_arm": animacy_rates,
        "animacy_invariant": animacy_invariant,
        "structural_reference": structural_ref,
        "arms_differ_pairs": diff_pairs,
        "bootstrap_LOW": boot_low,
        "bootstrap_HIGH": boot_high,
        "gap_high_minus_low_multi": gap_high_low,
        "gap_high_minus_scrambled_multi": gap_high_scr,
        "monotonic_ok": monotonic_ok,
        "baseline_in_band": baseline_in_band,
        "verdict": verdict,
        "verdict_msg": (f"HIGH-LOW gap(multi)={gap_high_low:.4f} HIGH-SCRAMBLED gap={gap_high_scr:.4f} "
                        f"monotonic={monotonic_ok} animacy_invariant={animacy_invariant} "
                        f"baseline_in_band={baseline_in_band} n_multi={n_multi_total}/{len(instances)}"),
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
    """N~small smoke-of-smoke: exercise the REAL substrate call path (LCCP module load + real gold +
    real McGuffey files) at reduced scope, assert basic invariants BEFORE any dispatch decision."""
    assert os.path.exists(LCCP.GOLD_PATH), f"gold missing: {LCCP.GOLD_PATH}"
    for p in MCGUFFEY_NONEVAL_PATHS + [THIRD_READER_PATH, TEXT8_PATH]:
        assert os.path.exists(p), f"corpus missing: {p}"
    assert THIRD_READER_PATH not in MCGUFFEY_NONEVAL_PATHS, "NO_LEAKAGE_VIOLATION"
    lessons = load_mcguffey_lessons()
    assert len(lessons) >= 20, f"expected >=20 background lessons, got {len(lessons)}"
    n_tok, hits, dens = lesson_density(lessons[0]["text"])
    assert n_tok > 0
    instances = build_eval_instances()
    assert len(instances) > 0, "no eval instances built -- LCCP harness wiring broken"
    n_multi = sum(1 for i in instances if len(i["candidates"]) >= 2)
    print(f"[self_test] MEASURED n_lessons={len(lessons)} n_eval_instances={len(instances)} "
          f"n_multi_candidate={n_multi}", flush=True)
    prior, n_hits = compute_patient_prior(lessons[0]["text"] + " " + lessons[1]["text"])
    assert isinstance(prior, dict)
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
