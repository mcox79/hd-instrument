#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""COREF CANDIDATE-POOL HYGIENE: phi-feature agreement filtering (number + person-deixis).

CONFIRM-BEFORE-ATTACK DIAGNOSTIC (a690e2af) found ~31% of same-gender xsent coref MISSES
are the reader picking an entity that should NEVER have been in a same-gender PERSON pool:
places (its banks), generic plurals (men/women/servants), the narrator (I/we/my), collective
nouns (family). This BOTH loses recoverable cases AND corrupts the plateau measurement (the
banked 0.25->0.45 same-gender numbers were measured against a pool polluted with non-persons
-> the fair-test gate is NOT met). This cell filters the pronoun candidate pool by PHI-FEATURE
AGREEMENT so only agreeing PERSON candidates compete (basic brain-faithful pronoun resolution:
a personal pronoun agrees with its antecedent in number/person/gender/animacy).

TWO PRIMARY LEVERS (clean, polysemy-SAFE; general grammatical features, NOT LitBank lexicons):
  1. NUMBER agreement: a singular pronoun (he/him/his/she/her) must NOT match a PLURAL
     candidate. Plural = irregular-plural set (men/women/...) OR regular morphological plural
     (lowercase common noun ending in -s, not -ss/-us/-is). Proper-name spans (capitalized)
     are treated singular (protects surnames Banks/Johns/Jones). Clean grammatical feature.
  2. PERSON-DEIXIS: a 3rd-person pronoun must NOT match a 1st/2nd-person mention (narrator
     I/me/my/we, addressee you/thou). These index a discourse ROLE (speaker/addressee), not a
     prior 3rd-person surface referent. Reuses hdlab.state_of_mind.deixis_person. Clean.

SECONDARY (INVESTIGATE, report mechanism; do NOT force): PLACE/COLLECTIVE leakage (hall,
family). The banked 29513 never-a-subject distractor-suppress FAILS to suppress these because
they ARE realized as grammatical subjects ("The hall echoed"; "his family were") OR are
is_named ("Kellynch Hall") -> guard-protected. NUMBER cannot fix them (singular/collective).
Per 29513 we do NOT re-add WordNet-animacy person-typing (polysemy: the doctor/the stranger);
so these are reported as a RESIDUAL wall, not attacked here.

FAIR TEST (pre-reg BELOW): baseline = the banked recency-centrality reader (0.4523 on the
same-gender xsent subset, current best). ONE variable = phi-agreement filtering on/off.
Difficulty on = xsent (sent_dist>=1) + backbone n_pool>=2 (>=2 same-gender competitors).
Discriminator (CAN-FAIL): does phi-filtering LIFT net accuracy on the fixed subset (fixed vs
broke)? AND the RE-CLEANED honest same-gender-PERSON plateau (remove targets whose gold cluster
has no surviving PERSON mention OR that drop below 2 person competitors after filtering) -- a
FAIRNESS result even if accuracy is flat (re-baselines the polluted measurement).

STORE: LOCAL-ONLY diagnostic. No bank / no push / no commit (skunkworks banks). Glass-box:
pure symbolic + the same genuine HD event-bundle memory as the baseline; NO external LLM, NO
network. ASCII-only, no em-dash.

# ============================ PRE-REG (bands BEFORE running) ============================
# question_class: DIAGNOSTIC + FAIRNESS (agreement-filter helps-or-hurts; re-baseline the pool)
# one_variable: phi-agreement filtering {off, number, deixis, number+deixis}
# baseline_arm: recency-centrality reader on RAW mentions (positive control, MUST reproduce
#   the banked 0.4523 / 270-of-597 -- Gate D reproduce-prior-at-test-regime).
# difficulty_on: xsent (sent_dist>=1) AND backbone n_pool>=2 (same-gender >=2 competitors).
# compute_architecture: sequential-CPU, justified -- cell IS the symbolic reader; the only HD
#   is the small Cowan-4 event-bundle unbind/cleanup (n_dim=4096) already in the baseline; wall
#   est < 2 min over 25 books x 4 conditions. No matmul-batching payoff. Foreground-to-complete.
# discriminator_can_fail: YES -- number/deixis filters CAN remove a valid person (break) and net
#   accuracy CAN drop; HARD_FAIL band below makes that a loud negative.
# HARD_PASS  (mechanism recovers recoverable cases): net accuracy lift on fixed-597 >= +0.020
#   (>= ~12 net targets) with fixes > breaks; OR (fairness) re-cleaned plateau differs from
#   0.4523 by >= 0.030 AND pollution removed >= 30 targets (>=5% of 597).
# HARD_FAIL  (filter is wrong / not brain-faithful): net accuracy DROPS by > 0.020 (breaks
#   exceed fixes) -> a valid-person is being suppressed; keep-digging autopsy required.
# MIDDLE_BAND (the 31% was over-counted): net within +/-0.020 AND pollution < 30 targets ->
#   report plainly that number+person-deixis recover little.
# reuse: hdlab.coref, hdlab.coref_distractor_suppress (29513), hdlab.event_centrality_coref
#   (baseline), hdlab.state_of_mind.deixis_person. Banked modules NOT edited.
# =======================================================================================
"""

from __future__ import annotations

import glob
import hashlib
import json
import os
import sys
import time
import traceback
from datetime import datetime, timezone

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from hdlab.coref import (
    build_pronoun_targets, load_name_gender, parse_litbank_conll,
)
from hdlab.coref_distractor_suppress import SuppressReader
from hdlab.event_centrality_coref import EVENT_N_DIM, EventCentralityReader
from hdlab.state_of_mind import deixis_person

ANCHOR_NAME = "coref_candidate_pool_phi_hygiene_v1"
CORPUS_DIR = os.path.join(REPO_ROOT, "data", "corpora", "litbank_coref_conll")
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", "exp_%s" % ANCHOR_NAME)
LOCAL_WINDOW = 5
MEM_SEED = 7
SUP_KW = dict(suppress_generic=True, use_nonref=True, use_struct=True,
              chain_pronouns=True, use_gazetteer=True)

# ---------------------------------------------------------------------------
# NUMBER agreement: general morphological plural detection (no LitBank lexicon).
# ---------------------------------------------------------------------------
# Irregular plurals (closed general English set; person-relevant forms weighted).
IRREGULAR_PLURAL = frozenset({
    "men", "women", "children", "people", "peoples", "folk", "folks", "gentlefolk",
    "gentlemen", "gentlewomen", "noblemen", "noblewomen", "clergymen", "countrymen",
    "countrywomen", "workmen", "workwomen", "tradesmen", "kinsmen", "kinswomen",
    "horsemen", "footmen", "fishermen", "yeomen", "freemen", "policemen", "watchmen",
    "brethren", "feet", "teeth", "geese", "mice", "oxen", "police", "cattle", "gentry",
})
# Regular-plural morphological exclusions: singular nouns ending in -s / -ss / -us / -is.
_PLURAL_S_EXCLUDE_SUFFIX = ("ss", "us", "is", "ous")


def is_plural_nominal(m: dict) -> bool:
    """GENERAL number-disagreement test: is this nominal mention grammatically PLURAL?

    True iff head in IRREGULAR_PLURAL, or (lowercase common noun ending in -s and not a
    known singular -ss/-us/-is ending). Proper-name spans (capitalized last token) are treated
    SINGULAR (protects surnames Banks/Johns/Jones/Charles). Deixis heads (we/us) are handled by
    the person-deixis filter, not here. No lexicon of LitBank characters; pure morphology."""
    if m.get("is_pronoun"):
        return False
    h = m["head"].lower()
    if deixis_person(h) is not None:
        return False                      # 1st/2nd-person plural -> person-deixis filter owns it
    if h in IRREGULAR_PLURAL:
        return True
    span = m.get("span_toks") or [m["head"]]
    last = span[-1] if span else h
    if last[:1].isupper():
        return False                      # capitalized proper name span -> singular
    if len(h) >= 4 and h.endswith("s") and not h.endswith(_PLURAL_S_EXCLUDE_SUFFIX):
        return True
    return False


def phi_rule_for_mention(m: dict, do_number: bool, do_deixis: bool):
    """Return the phi-agreement rule that DISQUALIFIES this nominal as a 3rd-person-singular
    antecedent candidate ('deixis' | 'number'), or None if it stays in the pool. Deixis is
    checked first (a 1st/2nd-person plural like 'we' is a deixis case, not a number case)."""
    if m.get("is_pronoun"):
        return None
    if do_deixis and deixis_person(m["head"]) is not None:
        return "deixis"
    if do_number and is_plural_nominal(m):
        return "number"
    return None


def phi_filter_mentions(mentions, do_number: bool, do_deixis: bool):
    """Transform the mention stream: mark disqualified nominal candidates as non-entity-creating
    (is_pronoun=True) so they NEVER enter the candidate pool, WITHOUT changing stream positions
    (recency distances are identical -- observe() advances the stream for a pronoun too). This is
    the ONE isolated variable; do_number=do_deixis=False returns a byte-identical mention stream.
    Returns (filtered_mentions, fired) where fired[midx] = rule string for audit/glass-box."""
    out = []
    fired = {}
    for m in mentions:
        rule = phi_rule_for_mention(m, do_number, do_deixis)
        if rule is not None:
            m2 = dict(m)
            m2["is_pronoun"] = True            # advances stream, creates no entity
            m2["_phi_filtered"] = rule
            out.append(m2)
            fired[m["midx"]] = rule
        else:
            out.append(m)
    return out, fired


# ---------------------------------------------------------------------------
# Arm runners (reuse the banked readers UNMODIFIED; the filter is upstream).
# ---------------------------------------------------------------------------
def fixed_window_scenes(n_sents, size):
    return [i // size for i in range(n_sents)]


def run_recency_arm(mentions, targets, n_sent):
    """The banked recency-centrality reader (baseline mechanism)."""
    sid = fixed_window_scenes(n_sent, LOCAL_WINDOW)
    rec = EventCentralityReader(n_dim=EVENT_N_DIM, mem_seed=MEM_SEED)
    return rec.resolve_stream(mentions, targets, scene_ids=sid, topical_mode="rolemass",
                              query_memory=True, centrality_mode="recency", **SUP_KW)


def run_backbone_arm(mentions, targets):
    """The banked SuppressReader backbone (used to define the difficulty subset + n_pool)."""
    rs = SuppressReader()
    return rs.resolve_stream(mentions, targets, **SUP_KW)


def records_by_target(records):
    return {r["target_midx"]: r for r in records}


# ===================== formula self-tests ==========================================
def _mk(head, cluster, is_pron, sent, midx, gender, role_rank, number="singular",
        name_gender=None, span=None):
    return {"head": head, "cluster": cluster, "is_pronoun": is_pron,
            "sent_idx": sent, "midx": midx, "gender": gender, "number": number,
            "name_gender": name_gender, "sent_role_rank": role_rank,
            "is_subject": (role_rank == 0), "span_toks": span or [head]}


def _selftest_plural_and_deixis_classifier():
    """Number classifier: irregular + regular plurals True; singular / capitalized proper /
    -ss endings False. Deixis classifier: I/we/my flagged, he/she/name not."""
    T = lambda h, span=None: is_plural_nominal(_mk(h, 1, False, 0, 0, None, 1, span=span))
    assert T("men") and T("women") and T("people") and T("gentlemen"), "irregular plural miss"
    assert T("servants", ["the", "servants"]), "regular plural (lowercase -s) miss"
    assert T("banks", ["its", "banks"]), "river-banks plural (the place-leak NUMBER should catch)"
    assert T("pigs", ["pigs"]), "regular plural miss"
    assert not T("mistress", ["his", "mistress"]), "-ss singular must NOT be plural"
    assert not T("duchess", ["the", "Duchess"]), "capitalized/-ss singular must NOT be plural"
    assert not T("johns", ["Sir", "Johns"]), "capitalized proper surname must NOT be plural"
    assert not T("hall", ["the", "hall"]), "singular place must NOT be plural (NUMBER cannot fix)"
    assert not T("family", ["his", "family"]), "collective -y singular must NOT be plural"
    assert not T("sir", ["sir"]) and not T("widow", ["the", "widow"]), "gendered singular person"
    # deixis
    assert deixis_person("i") == "first" and deixis_person("we") == "first"
    assert deixis_person("my") == "first" and deixis_person("you") == "second"
    assert deixis_person("he") is None and deixis_person("anna") is None
    # rule router: deixis wins over number for a 1st-person plural
    assert phi_rule_for_mention(_mk("we", 1, False, 0, 0, None, 0), True, True) == "deixis"
    assert phi_rule_for_mention(_mk("men", 1, False, 0, 0, "masc", 1), True, True) == "number"
    assert phi_rule_for_mention(_mk("anna", 1, False, 0, 0, "fem", 0), True, True) is None


def _selftest_filter_off_is_identity():
    """do_number=do_deixis=False leaves the mention stream byte-identical (one-variable proof)."""
    mentions = [
        _mk("anna", 1, False, 0, 0, "fem", 0, name_gender="fem"),
        _mk("men", 2, False, 0, 1, "masc", 1, span=["men"]),
        _mk("i", 3, False, 1, 2, None, 0, span=["I"]),
        _mk("she", 1, True, 2, 3, "fem", 0),
    ]
    off, fired = phi_filter_mentions(mentions, do_number=False, do_deixis=False)
    assert fired == {} and off == mentions, "filter-off must be identity"


def _selftest_filter_removes_pollution_and_recovers():
    """Constructed same-gender doc: the fem protagonist ANNA competes with a genderless
    genderNONE narrator 'I' (deixis) and a plural 'women' (number). The banked reader (filter
    OFF) is drawn to the recency-local pollutant; filter ON removes both from the pool so ANNA
    (the only real person) wins -> the discriminator FIRES and net accuracy improves."""
    from hdlab.coref import build_pronoun_targets
    mentions = []
    mi = 0
    mentions.append(_mk("anna", 1, False, 0, mi, "fem", 0, name_gender="fem")); mi += 1
    # narrator I (parsed as a genderless nominal by the banked pipeline) + plural women, each
    # dropped right before each pronoun so recency prefers them if not filtered.
    for s in range(1, 4):
        mentions.append(_mk("i", 9, False, s, mi, None, 0, span=["I"])); mi += 1
        mentions.append(_mk("women", 8, False, s, mi, "fem", 1, span=["women"])); mi += 1
        mentions.append(_mk("she", 1, True, s, mi, "fem", 0)); mi += 1     # gold = Anna(1)
    targets = build_pronoun_targets(mentions)
    assert len(targets) == 3
    raw_acc = _acc(run_recency_arm(mentions, targets, 4), targets)
    filt, fired = phi_filter_mentions(mentions, do_number=True, do_deixis=True)
    filt_acc = _acc(run_recency_arm(filt, targets, 4), targets)
    assert any(v == "deixis" for v in fired.values()), "deixis filter did not fire"
    assert any(v == "number" for v in fired.values()), "number filter did not fire"
    assert filt_acc >= raw_acc, "phi-filter must not hurt this constructed case (%.2f<%.2f)" % (
        filt_acc, raw_acc)
    assert filt_acc >= 0.99, "phi-filter should let the real person Anna win: %.2f" % filt_acc


def _acc(records, targets):
    tb = records_by_target(records)
    ok = tot = 0
    for t in targets:
        r = tb.get(t["target"]["midx"])
        if r is None:
            continue
        tot += 1
        ok += 1 if r["correct"] else 0
    return ok / tot if tot else 0.0


def run_selftests():
    _selftest_plural_and_deixis_classifier()
    _selftest_filter_off_is_identity()
    _selftest_filter_removes_pollution_and_recovers()
    return {"irregular_plural_n": len(IRREGULAR_PLURAL),
            "reuse": ["EventCentralityReader", "SuppressReader", "deixis_person"]}


# ===================== main diagnostic ==========================================
def _write_atomic(path_dir, name, obj):
    os.makedirs(path_dir, exist_ok=True)
    tmp = os.path.join(path_dir, name + ".tmp")
    fin = os.path.join(path_dir, name)
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2)
    os.replace(tmp, fin)


def classify_pick(head, span_toks):
    """Type a wrong-pick head for the 'wrong-type recovery' tally (glass-box)."""
    if head is None:
        return "abstain"
    if deixis_person(head) is not None:
        return "deixis"
    if is_plural_nominal({"head": head, "is_pronoun": False,
                          "span_toks": span_toks or [head]}):
        return "number_plural"
    return "other"


def main():
    t0 = time.perf_counter()
    gaz = load_name_gender()
    paths = sorted(glob.glob(os.path.join(CORPUS_DIR, "*.conll")))
    paths = [p for p in paths if os.path.getsize(p) > 1000]

    CONDITIONS = {
        "raw":            dict(do_number=False, do_deixis=False),
        "number":         dict(do_number=True,  do_deixis=False),
        "deixis":         dict(do_number=False, do_deixis=True),
        "number_deixis":  dict(do_number=True,  do_deixis=True),
    }
    # per-target: subset membership (from RAW backbone) + per-condition recency correctness
    #   + per-condition filtered n_pool + gold-reachability flags.
    per_target = {}          # key=(book,target_midx) -> dict
    fired_counts = {"deixis": 0, "number": 0}
    fired_head_examples = {"deixis": {}, "number": {}}
    leak_investigation = {"hall": 0, "family": 0, "banks": 0, "the_hall_subject": 0}

    for path in paths:
        book = os.path.basename(path)
        mentions, n_sent = parse_litbank_conll(path, name_gender_map=gaz)
        targets = build_pronoun_targets(mentions)
        if not targets:
            continue
        # RAW backbone (subset definition + n_pool) and RAW recency (baseline control)
        bb_raw = records_by_target(run_backbone_arm(mentions, targets))
        rec_raw = records_by_target(run_recency_arm(mentions, targets, n_sent))

        # phi-filtered streams (compute once per condition; reuse for recency + backbone)
        filt_streams = {}
        for cond, kw in CONDITIONS.items():
            if cond == "raw":
                filt_streams[cond] = (mentions, {})
            else:
                filt_streams[cond] = phi_filter_mentions(mentions, **kw)
        # tally filter firings on the combined condition
        _, fired_nd = filt_streams["number_deixis"]
        mby_midx = {m["midx"]: m for m in mentions}
        for midx, rule in fired_nd.items():
            fired_counts[rule] += 1
            hh = mby_midx[midx]["head"]
            fired_head_examples[rule][hh] = fired_head_examples[rule].get(hh, 0) + 1

        rec_cond = {"raw": rec_raw}
        bb_cond = {"raw": bb_raw}
        for cond in ("number", "deixis", "number_deixis"):
            fm, _ = filt_streams[cond]
            rec_cond[cond] = records_by_target(run_recency_arm(fm, targets, n_sent))
            bb_cond[cond] = records_by_target(run_backbone_arm(fm, targets))

        # gold-cluster surviving-person map (per condition): which clusters keep >=1 entity-
        # creating (non-filtered) nominal mention (a reachable PERSON antecedent).
        def surviving_clusters(fm):
            s = set()
            for m in fm:
                if not m.get("is_pronoun"):
                    s.add(m["cluster"])
            return s
        surv = {cond: surviving_clusters(filt_streams[cond][0]) for cond in CONDITIONS}

        for t in targets:
            tmid = t["target"]["midx"]
            b = bb_raw.get(tmid)
            if b is None:
                continue
            if b["bucket"] == "same":
                continue                      # xsent only
            if b.get("n_pool", -1) < 2:
                continue                      # difficulty: >=2 same-gender competitors (RAW)
            key = (book, tmid)
            rec = {"book": book, "pronoun": t["target"]["head"],
                   "gold_cluster": t["target"]["cluster"],
                   "sent_dist": b["sent_dist"]}
            for cond in CONDITIONS:
                rr = rec_cond[cond].get(tmid)
                rec["correct_%s" % cond] = bool(rr["correct"]) if rr else False
                rec["pick_%s" % cond] = rr["resolved_head"] if rr else None
                bbc = bb_cond[cond].get(tmid)
                rec["npool_%s" % cond] = bbc.get("n_pool", -1) if bbc else -1
            # gold reachability under combined filter (is the gold cluster still a person?)
            rec["gold_survives_nd"] = (t["target"]["cluster"] in surv["number_deixis"])
            # glass-box: the RAW wrong pick head + its type (for wrong-type recovery tally)
            rr0 = rec_raw.get(tmid)
            pick0 = rr0["resolved_head"] if rr0 else None
            span0 = None
            rec["pick_raw_type"] = classify_pick(pick0, span0)
            per_target[key] = rec

        # leak investigation (mechanism report; count occurrences of unfixable non-persons)
        for m in mentions:
            h = m["head"]
            if h in ("hall", "family", "banks"):
                leak_investigation[h] += 1
            if h == "hall" and m.get("sent_role_rank", 99) == 0 and \
                    not (m.get("span_toks") and m["span_toks"][-1][:1].isupper()):
                leak_investigation["the_hall_subject"] += 1

    # -------------------- metrics --------------------
    subset = list(per_target.values())
    n_sub = len(subset)

    def acc_over(cond, rows):
        if not rows:
            return None
        return sum(1 for r in rows if r["correct_%s" % cond]) / len(rows)

    # METRIC 1: net accuracy on the FIXED subset + fixed/broke per arm
    metric1 = {}
    for cond in CONDITIONS:
        acc = acc_over(cond, subset)
        fixed = sum(1 for r in subset if r["correct_%s" % cond] and not r["correct_raw"])
        broke = sum(1 for r in subset if r["correct_raw"] and not r["correct_%s" % cond])
        metric1[cond] = {"acc": acc, "n_correct": sum(r["correct_%s" % cond] for r in subset),
                         "fixed_vs_raw": fixed, "broke_vs_raw": broke,
                         "net_targets": fixed - broke}

    baseline_acc = metric1["raw"]["acc"]
    best_cond = "number_deixis"
    net_acc_delta = metric1[best_cond]["acc"] - baseline_acc

    # METRIC 2: RE-CLEANED honest same-gender-PERSON plateau (combined filter).
    # Remove targets that are pollution-artifacts: gold cluster no longer a reachable person,
    # OR fewer than 2 same-gender PERSON competitors after filtering (difficulty gone).
    recleaned = [r for r in subset
                 if r["gold_survives_nd"] and r["npool_number_deixis"] >= 2]
    removed = [r for r in subset if r not in recleaned]
    recleaned_plateau = acc_over("number_deixis", recleaned)
    removed_raw_acc = acc_over("raw", removed)   # how baseline "scored" the polluted targets

    # WRONG-TYPE RECOVERY: of the RAW misses, how many had a deixis/plural wrong pick, and how
    # many of those does the combined filter now get right?
    raw_misses = [r for r in subset if not r["correct_raw"]]
    wt = {"deixis": {"n": 0, "recovered": 0}, "number_plural": {"n": 0, "recovered": 0},
          "other": {"n": 0, "recovered": 0}, "abstain": {"n": 0, "recovered": 0}}
    for r in raw_misses:
        typ = r["pick_raw_type"]
        wt.setdefault(typ, {"n": 0, "recovered": 0})
        wt[typ]["n"] += 1
        if r["correct_number_deixis"]:
            wt[typ]["recovered"] += 1
    n_wrongtype = wt["deixis"]["n"] + wt["number_plural"]["n"]
    wrongtype_frac = n_wrongtype / len(raw_misses) if raw_misses else 0.0

    # ARMS-MUST-DIFFER (META_RULE_AF): baseline vs combined resolve vectors must differ.
    def _digest(cond):
        v = "".join("1" if r["correct_%s" % cond] else "0" for r in subset)
        return hashlib.sha256(v.encode()).hexdigest()
    d_raw, d_nd = _digest("raw"), _digest("number_deixis")
    arms_differ = (d_raw != d_nd)

    # GLASS-BOX: sample newly-fixed + newly-broken targets under the combined filter.
    fixed_examples = [{"book": r["book"], "pronoun": r["pronoun"],
                       "gold_cluster": r["gold_cluster"],
                       "raw_pick": r["pick_raw"], "raw_pick_type": r["pick_raw_type"],
                       "nd_pick": r["pick_number_deixis"]}
                      for r in subset
                      if r["correct_number_deixis"] and not r["correct_raw"]][:25]
    broke_examples = [{"book": r["book"], "pronoun": r["pronoun"],
                       "gold_cluster": r["gold_cluster"],
                       "raw_pick": r["pick_raw"], "nd_pick": r["pick_number_deixis"],
                       "npool_nd": r["npool_number_deixis"]}
                      for r in subset
                      if r["correct_raw"] and not r["correct_number_deixis"]][:25]

    # -------------------- verdict banding --------------------
    HP_ACC = (net_acc_delta >= 0.020 and metric1[best_cond]["net_targets"] > 0)
    pollution_removed = len(removed)
    HP_FAIR = (abs((recleaned_plateau or baseline_acc) - baseline_acc) >= 0.030
               and pollution_removed >= 30)
    HF = (net_acc_delta < -0.020)
    if HF:
        verdict = "HARD_FAIL"
    elif HP_ACC or HP_FAIR:
        verdict = "HARD_PASS"
    else:
        verdict = "MIDDLE_BAND"
    verdict_msg = (
        "phi-hygiene: base=%.4f nd=%.4f (dAcc=%+.4f fixed=%d broke=%d net=%+d); "
        "recleaned_plateau=%s on n=%d (removed %d polluted of %d); "
        "wrongtype misses=%d/%d (%.1f%%) recovered deixis=%d/%d number=%d/%d" % (
            baseline_acc, metric1[best_cond]["acc"], net_acc_delta,
            metric1[best_cond]["fixed_vs_raw"], metric1[best_cond]["broke_vs_raw"],
            metric1[best_cond]["net_targets"],
            ("%.4f" % recleaned_plateau) if recleaned_plateau is not None else "NA",
            len(recleaned), pollution_removed, n_sub,
            n_wrongtype, len(raw_misses), 100.0 * wrongtype_frac,
            wt["deixis"]["recovered"], wt["deixis"]["n"],
            wt["number_plural"]["recovered"], wt["number_plural"]["n"]))

    metrics = {
        "anchor_name": ANCHOR_NAME,
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": verdict_msg[:200],
        "elapsed_s": round(time.perf_counter() - t0, 2),
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "n_books": len(paths),
        "n_subset": n_sub,
        "baseline_recency_acc": baseline_acc,
        "baseline_control_target_270_of_597": {
            "n_correct": metric1["raw"]["n_correct"], "n_subset": n_sub,
            "reproduces_banked_0.4523": (abs(baseline_acc - 0.4523) < 0.005 and n_sub == 597)},
        "metric1_net_accuracy_fixed_subset": metric1,
        "metric2_recleaned_person_plateau": {
            "plateau_number_deixis": recleaned_plateau,
            "n_recleaned": len(recleaned),
            "n_removed_pollution": pollution_removed,
            "removed_raw_acc": removed_raw_acc,
            "delta_vs_polluted_baseline": (
                (recleaned_plateau - baseline_acc) if recleaned_plateau is not None else None)},
        "wrong_type_recovery": {"by_type": wt, "n_raw_misses": len(raw_misses),
                                "wrongtype_frac_of_misses": wrongtype_frac},
        "filter_firings": {"counts": fired_counts,
                           "top_deixis_heads": sorted(
                               fired_head_examples["deixis"].items(),
                               key=lambda kv: -kv[1])[:10],
                           "top_number_heads": sorted(
                               fired_head_examples["number"].items(),
                               key=lambda kv: -kv[1])[:10]},
        "place_leak_investigation": leak_investigation,
        "arms_differ_verified": arms_differ,
        "arms_digests": {"raw": d_raw, "number_deixis": d_nd},
        "glass_box_fixed_examples": fixed_examples,
        "glass_box_broke_examples": broke_examples,
        "selftest": SELFTEST_RESULT,
        "prereg_bands": {
            "HARD_PASS_acc": "net dAcc>=+0.020 and net_targets>0",
            "HARD_PASS_fairness": "|recleaned-base|>=0.030 and pollution>=30",
            "HARD_FAIL": "net dAcc<-0.020 (valid-person suppressed)",
            "MIDDLE_BAND": "dAcc within +/-0.020 and pollution<30"},
    }
    _write_atomic(OUTPUT_DIR, "metrics.json", metrics)
    print(verdict + " :: " + verdict_msg)
    print("metrics -> %s" % os.path.join(OUTPUT_DIR, "metrics.json"))
    return metrics


SELFTEST_RESULT = None

if __name__ == "__main__":
    try:
        SELFTEST_RESULT = run_selftests()
        print("[selftest] PASS %s" % SELFTEST_RESULT)
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        diag = {"anchor_name": ANCHOR_NAME, "verdict": "CELL_CRASHED",
                "verdict_msg": "%s: %s" % (type(e).__name__, str(e)[:400]),
                "summary": "CELL_CRASHED", "elapsed_s": 0.0,
                "traceback": traceback.format_exc()[:5000],
                "ts_iso": datetime.now(timezone.utc).isoformat()}
        tmp = os.path.join(OUTPUT_DIR, "metrics.json.tmp")
        fin = os.path.join(OUTPUT_DIR, "metrics.json")
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(diag, f, indent=2)
        os.replace(tmp, fin)
        raise
