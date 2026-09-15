"""exp_board_nonverbal_predication_row_v1 -- the NON-VERBAL PREDICATION board row (who-is-what / who-is-where /
who-has-what), gold-free at decision time.

problem: the_boards_who_did_what_rows_iterate_gold_verbs_so_a_fifth_of_asserted_clauses_are_outside_their_
         population_add_the_non_verbal_predication_row_to_the_board

WHY.  The board's who-did-what AGENT/PATIENT rows iterate gold VERB predicates (`gold_agent_items`), the entity
rows read mentions, and the state row reads the copular-binding path -- none of them iterates a clause whose
GOLD predicate is non-verbal ("the sky is blue", "she is a doctor", "he was here", "there is no proof"). UD puts
that predicate on an ADJ/NOUN/ADV/PROPN/NUM by design (pri 110 SOLVED.md 10e); 167 of the 762 subject-bearing
gold clauses of UD-EWT test 700 (21.9%) and 366 of the capped 1200 GUM/GENTLE sentences are outside every
existing row's population. pri 113 (landed, `hdlab.situation_reader._add_nonverbal_predication`, default ON)
is the largest single gain on exactly this fifth of the text and has NO board row that reads it.

THE QUESTION THIS ROW ASKS (checklist item 1).  For a clause whose predicate is a property / class / location /
possession, did the reader build the right structure -- the right HOLDER (the clause's subject entity) with the
right CONTENT (the complement) -- gold-free at decision time?

POPULATION.  Every gold clause with a subject (a gold nsubj arc, UD subtypes stripped by the loader) whose gold
predicate (that arc's head) is NOT tagged VERB in the gold UPOS column: 167 of 762 on UD-EWT test 700 (modern,
deprels); 366 of the GUM/GENTLE cap-1200 population (modern, deprels). BOTH are computed and reported; the
UD-EWT row is THE board row (GUM is the out-of-supply/out-of-genre replication, reported alongside, never
fabricated into the headline).

GOLD.  The clause's subject HEAD (the gold nsubj dependent token(s) of the predicate) and the clause's
PREDICATE HEAD (the nsubj arc's gold head).

MODEL'S ANSWER.  The LIVE `hdlab.situation_reader.SituationReader`'s fired event/state for that clause, driven
EXACTLY the way the pri 113 participant instruments drive it (`_cached_tag` + `_extract_events` on the raw
sentence, no document assembly, no monkeypatch, hdlab imported read-only): a HIT on the predicate half requires
the reader's fired-event index set to contain the gold predicate token. The reader's structure DOES carry a
holder field for a non-verbal predication: `SituationReader.read()` calls `_read_entity_states` by default
(`bind_entity_states=True`), which is `hdlab.copular_binding.extract_entity_states` / `.robust_cop` -- a set of
(holder_idx, property_idx) pairs. This cell drives that SAME organ per sentence (`robust_cop(toks, up, heads,
gate=True)`, the exact call the participant instrument's `states()` function makes) to get the holder half. So
the holder field IS carried here (the escape hatch in the brief -- "if the reader's structure has no holder
field, score the predicate head alone" -- does NOT apply): a HIT requires BOTH heads right -- the predicate
fired AND a (holder, property) pair exists at that predicate AND its holder is one of the gold subject's tokens.
Read `recall_predicate_only` in the row for the predicate-alone number if the joint number undersells detection.

FLOORS (recomputed in place, gold-free, on this cell's own population).
  (a) upos_verb_detector       -- the shipped UPOS==VERB event detector ALONE: hit iff the reader's OWN tag for
                                   the gold predicate token is VERB. Expected ~0 by construction (population is
                                   gold-non-verbal; this only fires on the organ's OWN tagging mistakes).
  (b) copula_adjacent_simple_rule -- the strongest SIMPLE decision rule: scan the sentence (using the reader's
                                   OWN tags, gold-free) for a copula/linking token (`hdlab.attachment_arm.
                                   COP_FORMS`, reused read-only); predicate = the first CONTENT word after it
                                   (skip AUX/PART/DET/ADP/SCONJ/CCONJ/PUNCT); holder = the nearest NOMINAL
                                   (NOUN/PROPN/PRON) before it. A hit requires both heads to match gold.
`strongest_floor` = whichever of (a)/(b) scores higher on this row's own population (by construction, (b)).

TWIN.  Information-free: the SAME NUMBER of extra (non-VERB-tagged) fires as the model produces, placed on a
RANDOM eligible token of the SAME sentence (the exact mechanism the pri 113 participant instrument's own TWIN
uses -- "the same NUMBER of extra fires per sentence, on a random token that is not already fired"); its
implied holder is a random NOMINAL token of the same sentence, excluding the twin's own predicate guess. Must
lose CI-sep on both predicate and joint scoring.

CI.  Paired bootstrap over ITEMS (clauses), 2000 resamples (200 in --self-test), percentile 2.5/97.5; half-width
reported; ci_sep = lower bound of (model - floor/twin) > 0.

Glass-box, NO spaCy/NLTK tagger/supervised parser/external LLM anywhere. hdlab/ and tools/ are READ-ONLY (this
cell only IMPORTS the live organs to drive the reader the way the board would; it writes nothing there). ASCII.
own dir (Q115: experiments._seed_checkpoint.get_output_dir).

Run: .venv/Scripts/python.exe experiments/exp_board_nonverbal_predication_row_v1.py --self-test
     .venv/Scripts/python.exe experiments/exp_board_nonverbal_predication_row_v1.py --run
"""
from __future__ import annotations

import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "2")
os.environ.setdefault("PYTHONHASHSEED", "0")

import json
import random
import sys
from collections import defaultdict

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

import numpy as np

from experiments._seed_checkpoint import get_output_dir
from tools.build_attachment_validities import sentences, TEST
import hdlab.attachment_arm as AA
from hdlab import copular_binding as CB

ANCHOR = "board_nonverbal_predication_row_v1"
OUT_DIR = str(get_output_dir(ANCHOR))
SEED = 20260914

NOMINAL_TAGS = frozenset({"NOUN", "PROPN", "PRON"})
# tags skipped when scanning forward from a copula for "the first CONTENT word" (floor b)
_SKIP_FOR_CONTENT = frozenset({"AUX", "PART", "DET", "ADP", "SCONJ", "CCONJ", "PUNCT"})
COP_FORMS = AA.COP_FORMS  # reused read-only (the shipped copula/linking-verb lexical set)


def out_dir():
    os.makedirs(OUT_DIR, exist_ok=True)
    return OUT_DIR


def _degraded(name, err, informational=False):
    """Schema-shaped row for an unavailable asset/runtime (mirrors exp_situation_model_qa_modern_v1._degraded)."""
    return {"n": 0, "model_acc": None, "overlap_floor": None, "strongest_floor": None,
            "strongest_floor_name": None, "twin_acc": None,
            "model_minus_strongest": [None, None, None], "model_minus_twin": [None, None, None],
            "ci_sep_over_strongest": False, "ci_sep_over_twin": False, "informational": informational,
            "population": "DEGRADED (asset/runtime unavailable) -- %s" % name,
            "error": ("%s: %s" % (type(err).__name__, err)) if isinstance(err, Exception) else str(err)}


# =====================================================================================================================
# POPULATION -- every gold subject-bearing clause whose gold predicate is NOT VERB.
# =====================================================================================================================
def _corpus(pop="ud", cap=None):
    if pop == "gum":
        from experiments.exp_one_convention_two_losses_v1 import gum_sentences
        raw = gum_sentences(cap=cap or 1200)
    else:
        raw = sentences(TEST, cap=cap or 700, maxlen=10 ** 6)
    out = []
    for toks, gp, gh, rels in raw:
        if not toks or any(" " in t for t in toks):
            continue
        out.append((toks, gp, gh, rels))
    return out


def nonverbal_items(pop="ud", cap=None):
    """Every subject-bearing gold clause whose gold predicate is non-verbal. One dict per clause:
    si (sentence index into the returned corpus), toks, pred (1-based gold predicate head), subj (frozenset of
    0-based gold-subject token indices attached to that head by a gold nsubj arc)."""
    corpus = _corpus(pop=pop, cap=cap)
    items = []
    for si, (toks, gp, gh, rels) in enumerate(corpus):
        n = len(toks)
        preds = sorted(set(gh[i] for i in range(n) if rels[i] == "nsubj" and 1 <= gh[i] <= n))
        for h in preds:
            if gp[h - 1] == "VERB":
                continue
            subj = frozenset(i for i in range(n) if gh[i] == h and rels[i] == "nsubj")
            if not subj:
                continue
            items.append({"si": si, "toks": toks, "pred": h, "subj": subj})
    return items, corpus


# =====================================================================================================================
# THE SCORING PRIMITIVE -- shared by the model, both floors, the twin, AND the self-test's oracle, so the
# self-test genuinely exercises the same hit logic the row uses.
# =====================================================================================================================
def _hit(h0, subj, fired, prop_of):
    """hit = the predicate fired AND a (holder, property) pair exists at h0 AND its holder is a gold subject
    token. Returns (predicate_only_hit, joint_hit)."""
    pr = h0 in fired
    hr = pr and (h0 in prop_of) and (prop_of[h0] in subj)
    return pr, hr


# =====================================================================================================================
# FLOOR (b): the copula-adjacent simple rule (gold-free: uses the reader's OWN tags).
# =====================================================================================================================
def _simple_rule_map(up, toks):
    """{predicate_idx0: holder_idx0}: for every copula/linking token, the first CONTENT word after it paired
    with the nearest NOMINAL before it."""
    n = len(up)
    out = {}
    for i in range(n):
        if toks[i].lower() not in COP_FORMS:
            continue
        pred = None
        for j in range(i + 1, n):
            if up[j] in _SKIP_FOR_CONTENT:
                continue
            pred = j
            break
        if pred is None:
            continue
        holder = None
        for j in range(i - 1, -1, -1):
            if up[j] in NOMINAL_TAGS:
                holder = j
                break
        if holder is None:
            continue
        out.setdefault(pred, holder)
    return out


# =====================================================================================================================
# THE READER -- driven exactly as the pri 113 participant instruments drive it.
# =====================================================================================================================
def _reader(nonverbal_predication=True):
    from hdlab.situation_reader import SituationReader
    return SituationReader(predicate_recall=True, nonverbal_predication=nonverbal_predication)


def _boot_ci(model_hits, other_hits, n_boot=2000, seed=0):
    model_hits = np.asarray(model_hits, dtype=float)
    other_hits = np.asarray(other_hits, dtype=float)
    diff = model_hits - other_hits
    n = len(diff)
    if n == 0:
        return {"delta": 0.0, "lo": 0.0, "hi": 0.0, "sep": False, "half_width": 0.0}
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, n, size=(n_boot, n))
    boots = diff[idx].mean(axis=1)
    lo = float(np.percentile(boots, 2.5)); hi = float(np.percentile(boots, 97.5))
    return {"delta": round(float(diff.mean()), 4), "lo": round(lo, 4), "hi": round(hi, 4),
            "sep": bool(lo > 0), "half_width": round((hi - lo) / 2.0, 4)}


def score_population(items, corpus, nonverbal_predication=True, n_boot=2000, seed=SEED):
    """One pass over the corpus (grouped by sentence so the reader/parse/copular-binding organs run ONCE per
    sentence, however many clauses it has); returns the board per_dimension row."""
    rdr = _reader(nonverbal_predication=nonverbal_predication)
    by_si = defaultdict(list)
    for it in items:
        by_si[it["si"]].append(it)
    rng = random.Random(seed)
    model_hits, model_pred_only = [], []
    floor_a_hits = []
    floor_b_hits, floor_b_pred_only = [], []
    twin_hits, twin_pred_only = [], []
    for si in sorted(by_si):
        its = by_si[si]
        toks = its[0]["toks"]
        n = len(toks)
        up = list(rdr._cached_tag(list(toks)))
        events, _ = rdr._extract_events(" ".join(toks))
        fired = set(e.idx for e in events)
        try:
            heads = rdr._cached_parse_heads(list(toks), up)
            pairs = CB.robust_cop(list(toks), up, heads, gate=True)
        except Exception:
            pairs = set()
        prop_of = {}
        for (hh, pp) in pairs:
            prop_of.setdefault(pp, hh)
        simple_map = _simple_rule_map(up, toks)
        verb_set = set(i for i in range(n) if up[i] == "VERB")
        eligible = [i for i in range(n) if up[i] != "PUNCT" and i not in verb_set]
        extra = [i for i in fired if i not in verb_set]
        k = min(len(extra), len(eligible))
        sampled = rng.sample(eligible, k) if k else []
        twin_fired = verb_set | set(sampled)
        nominal_idx = [i for i in range(n) if up[i] in NOMINAL_TAGS]
        twin_holder_of = {}
        for q in sampled:
            cand = [i for i in nominal_idx if i != q]
            twin_holder_of[q] = rng.choice(cand) if cand else None
        for it in its:
            h0 = it["pred"] - 1
            subj = it["subj"]
            pr, hr = _hit(h0, subj, fired, prop_of)
            model_pred_only.append(int(pr)); model_hits.append(int(hr))
            floor_a_hits.append(int(up[h0] == "VERB"))
            fb_pr, fb_hr = _hit(h0, subj, set(simple_map), simple_map)
            floor_b_pred_only.append(int(fb_pr)); floor_b_hits.append(int(fb_hr))
            tw_pr, tw_hr = _hit(h0, subj, twin_fired, twin_holder_of)
            twin_pred_only.append(int(tw_pr)); twin_hits.append(int(tw_hr))
    n_items = len(model_hits)
    floor_accs = {"upos_verb_detector": round(float(np.mean(floor_a_hits)) if n_items else 0.0, 4),
                  "copula_adjacent_simple_rule": round(float(np.mean(floor_b_hits)) if n_items else 0.0, 4)}
    fname = max(floor_accs, key=floor_accs.get)
    farr = {"upos_verb_detector": floor_a_hits, "copula_adjacent_simple_rule": floor_b_hits}[fname]
    cs = _boot_ci(model_hits, farr, n_boot=n_boot, seed=seed)
    ct = _boot_ci(model_hits, twin_hits, n_boot=n_boot, seed=seed + 1)
    row = {
        "n": n_items,
        "model_acc": round(float(np.mean(model_hits)) if n_items else 0.0, 4),
        "overlap_floor": floor_accs[fname],
        "floor_accs": floor_accs,
        "strongest_floor_name": fname,
        "strongest_floor": floor_accs[fname],
        "twin_acc": round(float(np.mean(twin_hits)) if n_items else 0.0, 4),
        "model_minus_strongest": [cs["delta"], cs["lo"], cs["hi"]],
        "model_minus_twin": [ct["delta"], ct["lo"], ct["hi"]],
        "ci_sep_over_strongest": cs["sep"],
        "ci_sep_over_twin": ct["sep"],
        "ci_half_width_strongest": cs["half_width"],
        "ci_half_width_twin": ct["half_width"],
        "recall_predicate_only": {
            "model": round(float(np.mean(model_pred_only)) if n_items else 0.0, 4),
            "upos_verb_detector": floor_accs["upos_verb_detector"],
            "copula_adjacent_simple_rule": round(float(np.mean(floor_b_pred_only)) if n_items else 0.0, 4),
            "twin": round(float(np.mean(twin_pred_only)) if n_items else 0.0, 4)},
        "nonverbal_predication_flag": bool(nonverbal_predication),
        "n_sentences": len(by_si),
    }
    return row


def nonverbal_predication_row(pop="ud", cap=None, nonverbal_predication=True, n_boot=2000, seed=SEED):
    items, corpus = nonverbal_items(pop=pop, cap=cap)
    row = score_population(items, corpus, nonverbal_predication=nonverbal_predication, n_boot=n_boot, seed=seed)
    arm_note = ("current tree (pri 113 landed, HDLAB_NONVERBAL_PREDICATION default ON)" if nonverbal_predication
                else "pre-113 arm (SituationReader(nonverbal_predication=False), equivalent to "
                     "HDLAB_NONVERBAL_PREDICATION=0)")
    if pop == "gum":
        row["population"] = (
            "GUM/GENTLE cap-%d population (modern, deprels), every gold subject-bearing clause whose gold "
            "predicate is non-verbal (n=%d); %s. model=the LIVE SituationReader's fired event/state at the gold "
            "predicate token AND its copular_binding (holder,property) pair's holder in the gold subject set "
            "(a JOINT hit -- the structure carries a holder field, so the brief's no-holder fallback does not "
            "apply); floor=max(shipped UPOS==VERB detector alone [expected ~0], copula-adjacent simple rule: "
            "first content word after the copula=predicate, nearest nominal before it=holder); twin=the same "
            "NUMBER of extra (non-VERB) fires placed on a random eligible token of the same sentence, holder a "
            "random nominal token (info-free). SECONDARY population (the UD-EWT row is the board row)."
            % ((cap or 1200), row["n"], arm_note))
    else:
        row["population"] = (
            "UD-EWT test 700 (modern, deprels), every gold subject-bearing clause whose gold predicate is "
            "non-verbal (n=%d, of 762 total subject-bearing clauses); %s. model=the LIVE SituationReader's fired "
            "event/state at the gold predicate token AND its copular_binding (holder,property) pair's holder in "
            "the gold subject set (a JOINT hit -- the structure carries a holder field, so the brief's "
            "no-holder fallback does not apply); floor=max(shipped UPOS==VERB detector alone [expected ~0], "
            "copula-adjacent simple rule: first content word after the copula=predicate, nearest nominal before "
            "it=holder); twin=the same NUMBER of extra (non-VERB) fires placed on a random eligible token of the "
            "same sentence, holder a random nominal token (info-free). THIS IS THE BOARD ROW."
            % (row["n"], arm_note))
    return row


def board_nonverbal_predication_dimension(smoke=False):
    """PLAIN WORDS (scorecard line): what things are / where things are / who has what.

    Both populations computed; the UD-EWT row is the board row (checklist item 8), GUM is the out-of-supply
    replication reported alongside it. Degrades gracefully (never raises) so a board run never dies on this arm."""
    try:
        cap_ud = 60 if smoke else 700
        cap_gum = 60 if smoke else 1200
        nboot = 200 if smoke else 2000
        row_ud = nonverbal_predication_row(pop="ud", cap=cap_ud, nonverbal_predication=True,
                                           n_boot=nboot, seed=SEED)
        row_gum = nonverbal_predication_row(pop="gum", cap=cap_gum, nonverbal_predication=True,
                                            n_boot=nboot, seed=SEED + 7)
        rows = {"nonverbal_predication_udewt": row_ud, "nonverbal_predication_gum": row_gum}
        detail = {"the_row": "nonverbal_predication_udewt",
                  "note": "who-is-what/who-is-where/who-has-what (pri 113's largest board-invisible gain, now "
                          "scored). GUM is the secondary out-of-supply/out-of-genre replication, not the row."}
        return rows, detail
    except Exception as e:
        return {"nonverbal_predication_udewt": _degraded("nonverbal_predication", e)}, \
               {"error": "%s: %s" % (type(e).__name__, e)}


# =====================================================================================================================
# SELF-TEST
# =====================================================================================================================
REQUIRED_KEYS = ("n", "model_acc", "overlap_floor", "floor_accs", "strongest_floor_name", "strongest_floor",
                  "twin_acc", "model_minus_strongest", "model_minus_twin", "ci_sep_over_strongest",
                  "ci_sep_over_twin", "population")


def _oracle_check(items):
    """The SAME hit primitive (_hit), fed the gold predicate as the 'fired' set and a gold subject token as the
    'holder' -- must score 1.0 on every item. Exercises the scoring logic, not the reader."""
    hits = []
    for it in items:
        h0 = it["pred"] - 1
        subj = it["subj"]
        s0 = next(iter(subj))
        _pr, hr = _hit(h0, subj, {h0}, {h0: s0})
        hits.append(hr)
    return float(np.mean(hits)) if hits else None


def self_test():
    ok_all = True

    def ck(label, cond, extra=""):
        nonlocal ok_all
        mark = "PASS" if cond else "FAIL"
        if not cond:
            ok_all = False
        print("[%s] %s %s" % (mark, label, extra))

    items_ud, _ = nonverbal_items(pop="ud", cap=60)
    ck("UD-EWT cap60 non-verbal population non-empty", len(items_ud) > 0, "n=%d" % len(items_ud))
    oracle = _oracle_check(items_ud)
    ck("oracle (gold predicate + gold holder) scores 1.0", oracle == 1.0, "oracle=%s" % oracle)

    row_ud = nonverbal_predication_row(pop="ud", cap=60, n_boot=200, seed=1)
    for k in REQUIRED_KEYS:
        ck("UD row has key %r" % k, k in row_ud)
    ck("UD row floor_accs has both named floors",
       set(row_ud["floor_accs"]) == {"upos_verb_detector", "copula_adjacent_simple_rule"})
    ck("UD row upos_verb_detector floor is near-zero (gold-non-verbal population)",
       row_ud["floor_accs"]["upos_verb_detector"] <= 0.15,
       "got %.4f" % row_ud["floor_accs"]["upos_verb_detector"])

    items_gum, _ = nonverbal_items(pop="gum", cap=60)
    oracle_g = _oracle_check(items_gum)
    ck("GUM oracle scores 1.0", oracle_g is None or oracle_g == 1.0, "oracle=%s" % oracle_g)
    row_gum = nonverbal_predication_row(pop="gum", cap=60, n_boot=200, seed=2)
    for k in REQUIRED_KEYS:
        ck("GUM row has key %r" % k, k in row_gum)

    rows, detail = board_nonverbal_predication_dimension(smoke=True)
    ck("board wrapper returns both rows", set(rows) == {"nonverbal_predication_udewt", "nonverbal_predication_gum"})
    ck("board wrapper detail names the row", detail.get("the_row") == "nonverbal_predication_udewt")

    print("SELF-TEST %s" % ("PASS" if ok_all else "FAIL"))
    return ok_all


def run():
    os.makedirs(out_dir(), exist_ok=True)
    t0 = __import__("time").time()
    row_ud = nonverbal_predication_row(pop="ud", cap=700, nonverbal_predication=True, n_boot=2000, seed=SEED)
    row_ud_pre113 = nonverbal_predication_row(pop="ud", cap=700, nonverbal_predication=False, n_boot=2000,
                                              seed=SEED)
    row_gum = nonverbal_predication_row(pop="gum", cap=1200, nonverbal_predication=True, n_boot=2000,
                                        seed=SEED + 7)
    row_gum_pre113 = nonverbal_predication_row(pop="gum", cap=1200, nonverbal_predication=False, n_boot=2000,
                                               seed=SEED + 7)
    res = {
        "anchor": ANCHOR, "seed": SEED,
        "nonverbal_predication_udewt": row_ud,
        "nonverbal_predication_udewt_pre113_arm": row_ud_pre113,
        "nonverbal_predication_gum": row_gum,
        "nonverbal_predication_gum_pre113_arm": row_gum_pre113,
        "the_row": "nonverbal_predication_udewt",
        "runtime_sec": round(__import__("time").time() - t0, 1),
    }
    path = os.path.join(out_dir(), "metrics.json")
    with open(path, "w", encoding="ascii") as fh:
        json.dump(res, fh, indent=1)
    print("UD-EWT (THE ROW): n=%d model=%.4f floor[%s]=%.4f twin=%.4f  ci_sep_strongest=%s ci_sep_twin=%s"
          % (row_ud["n"], row_ud["model_acc"], row_ud["strongest_floor_name"], row_ud["strongest_floor"],
             row_ud["twin_acc"], row_ud["ci_sep_over_strongest"], row_ud["ci_sep_over_twin"]))
    print("UD-EWT pre-113 arm: n=%d model=%.4f (current-tree model=%.4f, delta=%+.4f)"
          % (row_ud_pre113["n"], row_ud_pre113["model_acc"], row_ud["model_acc"],
             row_ud["model_acc"] - row_ud_pre113["model_acc"]))
    print("GUM:     n=%d model=%.4f floor[%s]=%.4f twin=%.4f  ci_sep_strongest=%s ci_sep_twin=%s"
          % (row_gum["n"], row_gum["model_acc"], row_gum["strongest_floor_name"], row_gum["strongest_floor"],
             row_gum["twin_acc"], row_gum["ci_sep_over_strongest"], row_gum["ci_sep_over_twin"]))
    print("GUM pre-113 arm: n=%d model=%.4f (current-tree model=%.4f, delta=%+.4f)"
          % (row_gum_pre113["n"], row_gum_pre113["model_acc"], row_gum["model_acc"],
             row_gum["model_acc"] - row_gum_pre113["model_acc"]))
    print("wrote %s" % path)
    return res


if __name__ == "__main__":
    a = sys.argv[1:]
    if "--self-test" in a:
        sys.exit(0 if self_test() else 1)
    elif "--run" in a:
        run()
    else:
        print(__doc__)
