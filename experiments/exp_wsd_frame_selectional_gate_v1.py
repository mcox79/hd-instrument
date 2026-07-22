#!/usr/bin/env python
# -*- coding: ascii -*-
"""Token-level word-sense-disambiguation gate for the meaning module.

Question (DIRECTIONAL GATE): does frame-matching + selectional-restriction
disambiguation pick the CONTEXT-CORRECT VerbNet sense (and therefore the correct
affectedness) better than the current TYPE-LEVEL max-score gate that ignores
context and mis-fires on polysemous verbs?

ONE VARIABLE: frame-matching disambiguation ON vs OFF. Same candidate-lemma pool,
same VerbNet lexicon, same parse. Baseline = max graded_score over the sense pool
(the deployed type-level gate). Mechanism = pick the sense whose VerbNet frame
matches the sentence's parsed frame, refine by per-role selectional restrictions.

Must-fail control: scramble the vn_class -> frame-signature mapping (fixed seeds);
the real gain must vanish.

Compute: symbolic frame-match + WordNet/VerbNet lookups. No matmul, no GPU, no
substrate primitive, no RNG in the clean arms (deterministic). Total wall < 10s.
Foreground-to-completion, LOCAL-ONLY. This is a lightweight diagnostic gate, run
inline (not a queued substrate cell), per compute-proportionality.

CELL-TEMPLATE MANDATORY (subset applicable to a symbolic non-substrate diagnostic):
# - arms_differ_verified at smoke gate (META_RULE_AF)
# - final_metrics_atomicity = tmp_replace (META_RULE_AH)
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - baseline_in_band at smoke (META_RULE_AG; 0.05 < baseline < 0.95)
# - HARD_PASS strictly above floor (META_RULE_L)
# - all numbers tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@ (META_RULE_AC)
# - crlb_n/a: symbolic accuracy over a fixed hand-labeled gold set; no noise floor
# - GPU-batching: class (b) sequential-CPU justified (wall<10s, no substrate matmul)
"""
import os
import sys
import json
import random
import argparse
import hashlib
import traceback
from datetime import datetime, timezone

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(line_buffering=True)

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ANCHOR_NAME = "wsd_frame_selectional_gate_v1"
LEXICON_PATH = os.path.join(REPO, "data", "verbnet_affectedness_lexicon_v1", "lexicon.json")


# ---------------------------------------------------------------------------
# GOLD SET (hand-labeled by cell-author, 2026-07-21).
# Each item: sentence, target surface token, gold affectedness_type, gold sense
# vn_class (must be REACHABLE in the candidate-lemma pool -> verified at run;
# unreachable items are dropped as UNANSWERABLE and reported, so gold is FAIR:
# we only score items whose correct sense the system CAN in principle output).
# affected = coarse "is a patient/theme changed?" binary derived from gold type.
# Difficulty-on: BOTH senses of each polysemous verb + monosemous controls +
# hard-residual cases (saw-perception) that need tense/world-knowledge.
# ---------------------------------------------------------------------------
AFFECTED_TYPES = {"change_of_state", "effected", "transfer", "possession"}  # patient/theme changed
UNAFFECTED_TYPES = {"perception", "cognition", "motion", "contact", "other"}

GOLD = [
    # leave: depart(motion) vs deposit(transfer/possession). FRAME cleanly splits.
    {"sent": "They leave for London tomorrow morning.", "verb": "leave", "type": "motion", "vn": "leave-51.2-1"},
    {"sent": "She left the room quietly.", "verb": "left", "type": "motion", "vn": "leave-51.2-1"},
    {"sent": "Leave the keys on the table.", "verb": "leave", "type": "transfer", "vn": "fulfilling-13.4.1"},
    {"sent": "He left his fortune to his son.", "verb": "left", "type": "transfer", "vn": "fulfilling-13.4.1"},
    # turn: rotate/convert(COS) vs go(motion).
    {"sent": "Turn the handle to open the door.", "verb": "turn", "type": "change_of_state", "vn": "convert-26.6.2"},
    {"sent": "The leaves turn red in autumn.", "verb": "turn", "type": "change_of_state", "vn": "convert-26.6.2"},
    {"sent": "She turned left at the corner.", "verb": "turned", "type": "motion", "vn": "roll-51.3.1"},
    {"sent": "He turned toward the window.", "verb": "turned", "type": "motion", "vn": "roll-51.3.1"},
    # get: obtain(transfer) vs become(COS).
    {"sent": "She got a new bike for her birthday.", "verb": "got", "type": "transfer", "vn": "get-13.5.1-1"},
    {"sent": "He got the book from the shelf.", "verb": "got", "type": "transfer", "vn": "get-13.5.1-1"},
    {"sent": "He got tired after the long run.", "verb": "got", "type": "change_of_state", "vn": "convert-26.6.2"},
    {"sent": "The soup got cold on the counter.", "verb": "got", "type": "change_of_state", "vn": "convert-26.6.2"},
    # fall: drop(motion) vs decrease/collapse(COS).
    {"sent": "The apple fell from the tree.", "verb": "fell", "type": "motion", "vn": "escape-51.1-2"},
    {"sent": "A book fell off the shelf.", "verb": "fell", "type": "motion", "vn": "escape-51.1-2"},
    {"sent": "Prices fell sharply last month.", "verb": "fell", "type": "change_of_state", "vn": "calibratable_cos-45.6-1"},
    {"sent": "The temperature fell overnight.", "verb": "fell", "type": "change_of_state", "vn": "calibratable_cos-45.6-1"},
    # pull: injure(COS) vs exert-force/haul(contact/motion). Needs selectional.
    {"sent": "She pulled a muscle during practice.", "verb": "pulled", "type": "change_of_state", "vn": "hurt-40.8.3-1-1"},
    {"sent": "The horse pulled the heavy cart.", "verb": "pulled", "type": "motion", "vn": "carry-11.4"},
    {"sent": "He pulled the rope hard.", "verb": "pulled", "type": "contact", "vn": "push-12-1"},
    # saw: cut(COS) vs see-past(perception). HARD residual: lemma + world-knowledge.
    {"sent": "The old man sawed the log into planks.", "verb": "sawed", "type": "change_of_state", "vn": "cut-21.1-1"},
    {"sent": "The boy saw a bird in the tree.", "verb": "saw", "type": "cognition", "vn": "see-30.1-1"},
    {"sent": "She saw her friend at the market.", "verb": "saw", "type": "cognition", "vn": "see-30.1-1"},
    # meet: contact/join vs encounter.
    {"sent": "The two roads meet at the bridge.", "verb": "meet", "type": "contact", "vn": "contiguous_location-47.8-1"},
    {"sent": "I met an old friend yesterday.", "verb": "met", "type": "other", "vn": "meet-36.3-1"},
    # ---- monosemous / low-ambiguity CONTROLS (both arms should get right;
    #      measures frame-matching does NOT BREAK easy cases) ----
    {"sent": "The chef cut the fresh bread.", "verb": "cut", "type": "change_of_state", "vn": "cut-21.1-1"},
    {"sent": "She broke the glass vase.", "verb": "broke", "type": "change_of_state", "vn": "break-45.1"},
    {"sent": "The dog ran across the field.", "verb": "ran", "type": "motion", "vn": "run-51.3.2"},
    {"sent": "They looked at the old painting.", "verb": "looked", "type": "cognition", "vn": "peer-30.3"},
    {"sent": "I know the right answer.", "verb": "know", "type": "cognition", "vn": "conjecture-29.5-1"},
    {"sent": "He pushed the wooden cart.", "verb": "pushed", "type": "contact", "vn": "push-12-1-1"},
    {"sent": "Put the book on the shelf.", "verb": "put", "type": "motion", "vn": "put-9.1-2"},
]

# Explicit irregular past -> base (morphy fails these because the surface form is
# itself a valid verb lemma: saw->saw, fell->fell). SHARED by both arms (lemma
# candidate generation is NOT the measured variable; frame-matching is).
IRREGULAR_PAST = {
    "saw": "see", "seen": "see",
    "fell": "fall", "fallen": "fall",
    "got": "get", "gotten": "get",
    "left": "leave",
    "met": "meet",
    "ran": "run",
    "knew": "know", "known": "know",
    "broke": "break", "broken": "break",
    "sawed": "saw",
}


def _lazy_nltk():
    import nltk  # noqa
    from nltk.corpus import verbnet as vn
    from nltk.corpus import wordnet as wn
    from nltk import pos_tag, word_tokenize
    # touch corpora so a missing-download fails LOUD here, not mid-loop
    _ = vn.classids()[:1]
    _ = wn.synsets("dog", pos="n")[:1]
    return vn, wn, pos_tag, word_tokenize


def candidate_lemmas(token, wn):
    """token (surface) -> set of candidate verb lemmas. Shared by both arms."""
    t = token.lower()
    cands = {t}
    m = wn.morphy(t, "v")
    if m:
        cands.add(m)
    if t in IRREGULAR_PAST:
        cands.add(IRREGULAR_PAST[t])
    return cands


def sense_pool(token, lex, wn):
    """All per_sense entries across candidate lemmas: list of dicts with vn_class,
    affectedness_type, graded_score, lemma."""
    pool = []
    seen = set()
    for lemma in candidate_lemmas(token, wn):
        e = lex.get(lemma)
        if not e:
            continue
        for ps in e.get("per_sense", []):
            key = (lemma, ps["vn_class"])
            if key in seen:
                continue
            seen.add(key)
            pool.append({
                "lemma": lemma,
                "vn_class": ps["vn_class"],
                "affectedness_type": ps["affectedness_type"],
                "graded_score": float(ps["graded_score"]),
            })
    return pool


# --- frame signature: canonical string from a syntax token list ------------
def _canon_sig(pos_seq):
    """pos_seq: list of coarse tags around the verb. Returns a canonical
    frame-signature in {INTRANS, TRANS, NP_PP, PP, DATIVE, OTHER}."""
    # pos_seq excludes the VERB itself; it is the ordered slot tags AFTER the verb
    # (subject NP before the verb is assumed present for all).
    if not pos_seq:
        return "INTRANS"
    if pos_seq == ["NP"]:
        return "TRANS"
    if pos_seq == ["NP", "NP"]:
        return "DATIVE"
    if pos_seq[0] == "PREP":
        return "PP"
    if pos_seq[0] == "NP" and "PREP" in pos_seq[1:]:
        return "NP_PP"
    if pos_seq == ["NP"]:
        return "TRANS"
    return "OTHER"


def vnclass_signatures(vn_class, vn):
    """Set of canonical frame-signatures a VerbNet class licenses, plus its
    themrole selectional restrictions. Returns (sig_set, selrestrs_dict)."""
    try:
        v = vn.vnclass(vn_class)
    except Exception:
        return set(), {}
    sigs = set()
    for fr in vn.frames(v):
        slots = []
        seen_verb = False
        for s in fr["syntax"]:
            pos = s["pos_tag"] if "pos_tag" in s else s.get("tag")
            if pos == "VERB":
                seen_verb = True
                continue
            if not seen_verb:
                continue  # subject side
            if pos == "NP":
                slots.append("NP")
            elif pos == "PREP":
                slots.append("PREP")
            elif pos in ("LEX", "ADV", "ADVP"):
                continue
        sigs.add(_canon_sig(slots))
    selr = {}
    for tr in v.findall("THEMROLES/THEMROLE"):
        role = tr.get("type")
        rests = [s.get("Value") + s.get("type") for s in tr.findall("SELRESTRS/SELRESTR")]
        selr[role] = rests
    return sigs, selr


def extract_sentence_frame(sentence, verb_token, pos_tag, word_tokenize):
    """POS-based glass-box frame extraction. Returns (sig, prep, dobj_head, pobj_head)."""
    toks = word_tokenize(sentence)
    tags = pos_tag(toks)
    # locate the verb token
    vi = None
    vt = verb_token.lower()
    for i, (w, p) in enumerate(tags):
        if w.lower() == vt and p.startswith("VB"):
            vi = i
            break
    if vi is None:
        for i, (w, p) in enumerate(tags):
            if w.lower() == vt:
                vi = i
                break
    if vi is None:
        return "OTHER", None, None, None
    slots = []
    prep = None
    dobj_head = None
    pobj_head = None
    j = vi + 1
    n = len(tags)
    # first NP directly after verb (before any prep) = direct object
    while j < n and tags[j][1] in ("DT", "JJ", "PRP$", "CD", "POS"):
        j += 1
    if j < n and tags[j][1] in ("NN", "NNS", "NNP", "NNPS", "PRP"):
        dobj_head = tags[j][0].lower()
        slots.append("NP")
        j += 1
        # possible second bare NP (dative) before a prep
        k = j
        while k < n and tags[k][1] in ("DT", "JJ", "PRP$", "CD", "POS"):
            k += 1
        if k < n and tags[k][1] in ("NN", "NNS", "NNP", "NNPS", "PRP"):
            slots.append("NP")
            j = k + 1
    # a preposition after (optional) dobj
    while j < n:
        if tags[j][1] in ("IN", "TO"):
            # infinitival "to open" is NOT a PP argument: skip TO immediately
            # followed by a (base) verb, else it corrupts the frame signature.
            if tags[j][1] == "TO" and j + 1 < n and tags[j + 1][1].startswith("VB"):
                break
            prep = tags[j][0].lower()
            slots.append("PREP")
            j += 1
            while j < n and tags[j][1] in ("DT", "JJ", "PRP$", "CD", "POS"):
                j += 1
            if j < n and tags[j][1] in ("NN", "NNS", "NNP", "NNPS", "PRP"):
                pobj_head = tags[j][0].lower()
            break
        if tags[j][1] in ("RB", "RBR", "."):
            j += 1
            continue
        break
    sig = _canon_sig(slots)
    return sig, prep, dobj_head, pobj_head


def noun_types(word, wn):
    """Coarse WordNet selectional tags for a noun head."""
    if not word:
        return set()
    tags = set()
    for s in wn.synsets(word, pos="n")[:3]:
        for path in s.hypernym_paths():
            names = [h.name().split(".")[0] for h in path]
            if "body_part" in names:
                tags.add("body_part")
            if any(x in names for x in ("living_thing", "animal", "person", "animate_thing")):
                tags.add("animate")
            if any(x in names for x in ("physical_entity", "artifact", "substance", "solid", "object")):
                tags.add("concrete")
            if any(x in names for x in ("location", "region", "structure", "way")):
                tags.add("location")
    return tags


def _selrestr_bonus(selr, dobj_tags, pobj_tags, prep):
    """Generic (non-per-item) bonus: reward a sense whose Patient/Theme/Recipient
    selrestr is satisfied by the observed fillers; penalize a clear violation.
    Weight kept small + symmetric; reported separately (L1 vs L2) so any heavy
    lifting by selrestr is visible, not hidden."""
    bonus = 0.0
    filler_tags = dobj_tags | pobj_tags
    LOC_PREPS = {"in", "on", "at", "into", "onto", "from", "to", "over", "under"}
    for role, rests in selr.items():
        for r in rests:
            want = None
            if "body_part" in r:
                want = "body_part"
            elif "animate" in r:
                want = "animate"
            elif "solid" in r or "concrete" in r:
                want = "concrete"
            elif "location" in r:
                want = "location"
            if want is None:
                continue
            if want == "location" and prep in LOC_PREPS:
                bonus += 0.3
                continue
            if want in filler_tags:
                bonus += 0.3
            elif want == "body_part" and "concrete" in filler_tags and "body_part" not in filler_tags:
                bonus -= 0.3  # sense demands a body-part patient but filler is a non-body object
    return bonus


# --- arms ------------------------------------------------------------------
def arm_baseline(item, lex, wn):
    """TYPE-LEVEL max graded_score over the full candidate pool. Ignores context."""
    pool = sense_pool(item["verb"], lex, wn)
    if not pool:
        return None
    best = max(pool, key=lambda s: s["graded_score"])
    return best


def arm_mechanism(item, lex, wn, vn, pos_tag, word_tokenize, sig_override=None, use_selrestr=True):
    """Frame-matching (+ optional selectional). sig_override lets the scramble
    control replace each vn_class's real signature set."""
    pool = sense_pool(item["verb"], lex, wn)
    if not pool:
        return None
    sig, prep, dobj_head, pobj_head = extract_sentence_frame(
        item["sent"], item["verb"], pos_tag, word_tokenize)
    dobj_tags = noun_types(dobj_head, wn)
    pobj_tags = noun_types(pobj_head, wn)
    # L1: frame filter
    compat = []
    for s in pool:
        if sig_override is not None:
            sset = sig_override.get(s["vn_class"], set())
            selr = {}
        else:
            sset, selr = vnclass_signatures(s["vn_class"], vn)
        s = dict(s)
        s["_sigs"] = sset
        s["_selr"] = selr
        if sig in sset:
            compat.append(s)
    frame_backoff = False
    if not compat:
        compat = [dict(s, _sigs=set(), _selr={}) for s in pool]
        frame_backoff = True
    # L2: selectional bonus among frame-compatible
    def score(s):
        b = 0.0
        if use_selrestr and not frame_backoff and sig_override is None:
            b = _selrestr_bonus(s["_selr"], dobj_tags, pobj_tags, prep)
        return s["graded_score"] + b
    best = max(compat, key=score)
    best["_frame_backoff"] = frame_backoff
    best["_sig"] = sig
    return best


# --- evaluation ------------------------------------------------------------
def evaluate(items, lex, wn, vn, pos_tag, word_tokenize):
    """Run all three disambiguation levels + baseline over the answerable gold."""
    answerable = []
    dropped = []
    for it in items:
        pool_classes = {s["vn_class"] for s in sense_pool(it["verb"], lex, wn)}
        if it["vn"] in pool_classes:
            answerable.append(it)
        else:
            dropped.append({"sent": it["sent"], "verb": it["verb"], "gold_vn": it["vn"],
                            "reason": "gold_sense_not_in_candidate_pool"})
    res = {"n_total": len(items), "n_answerable": len(answerable), "dropped": dropped}

    def acc_over(pred_fn):
        n_type = 0
        n_bin = 0
        per = []
        for it in answerable:
            best = pred_fn(it)
            if best is None:
                per.append({"sent": it["sent"], "pred": None, "gold": it["type"], "type_ok": False})
                continue
            pt = best["affectedness_type"]
            type_ok = (pt == it["type"])
            pred_aff = pt in AFFECTED_TYPES
            gold_aff = it["type"] in AFFECTED_TYPES
            bin_ok = (pred_aff == gold_aff)
            n_type += int(type_ok)
            n_bin += int(bin_ok)
            per.append({"sent": it["sent"], "verb": it["verb"], "gold": it["type"],
                        "pred": pt, "pred_vn": best["vn_class"], "type_ok": type_ok,
                        "bin_ok": bin_ok, "backoff": best.get("_frame_backoff", None)})
        m = len(answerable)
        return {"type_acc": n_type / m, "bin_acc": n_bin / m, "per_item": per}

    res["L0_baseline"] = acc_over(lambda it: arm_baseline(it, lex, wn))
    res["L1_frame_only"] = acc_over(
        lambda it: arm_mechanism(it, lex, wn, vn, pos_tag, word_tokenize, use_selrestr=False))
    res["L2_frame_selrestr"] = acc_over(
        lambda it: arm_mechanism(it, lex, wn, vn, pos_tag, word_tokenize, use_selrestr=True))
    return res


def scramble_control(items, lex, wn, vn, pos_tag, word_tokenize, seeds):
    """Must-fail: permute the vn_class -> signature-set mapping. Gain must vanish."""
    # collect the real signature sets over all classes referenced by the gold pool
    all_classes = set()
    for it in items:
        for s in sense_pool(it["verb"], lex, wn):
            all_classes.add(s["vn_class"])
    all_classes = sorted(all_classes)
    real_sigs = {c: vnclass_signatures(c, vn)[0] for c in all_classes}
    answerable = [it for it in items
                  if it["vn"] in {s["vn_class"] for s in sense_pool(it["verb"], lex, wn)}]
    accs = []
    for sd in seeds:
        rng = random.Random(sd)  # FIXED int seed; no hash(); PROT-023 clean
        shuffled = all_classes[:]
        rng.shuffle(shuffled)
        override = {c: real_sigs[shuffled[i]] for i, c in enumerate(all_classes)}
        n = 0
        for it in answerable:
            best = arm_mechanism(it, lex, wn, vn, pos_tag, word_tokenize,
                                 sig_override=override, use_selrestr=False)
            if best and best["affectedness_type"] == it["type"]:
                n += 1
        accs.append(n / len(answerable))
    return {"seeds": list(seeds), "type_acc_per_seed": accs,
            "type_acc_mean": sum(accs) / len(accs),
            "type_acc_std": (sum((a - sum(accs) / len(accs)) ** 2 for a in accs) / len(accs)) ** 0.5}


# --- verdict ---------------------------------------------------------------
def make_verdict(res, scr):
    b = res["L0_baseline"]["type_acc"]
    m = res["L2_frame_selrestr"]["type_acc"]
    l1 = res["L1_frame_only"]["type_acc"]
    real_gain = m - b
    scr_mean = scr["type_acc_mean"]
    scr_gain = scr_mean - b
    baseline_in_band = 0.05 < b < 0.95
    # scramble must kill most of the gain
    scramble_kills = (real_gain <= 0.0) or (scr_gain <= 0.5 * real_gain)
    if not baseline_in_band:
        verdict = "MIDDLE_BAND"
        msg = "baseline out of measurable band (AG); result inconclusive"
    elif real_gain <= 0.05:
        verdict = "HARD_FAIL"
        msg = "frame-matching gives no real lift over type-level baseline"
    elif not scramble_kills:
        verdict = "HARD_FAIL"
        msg = "scramble control did not remove the gain; mapping is not load-bearing"
    elif real_gain >= 0.20 and m >= 0.55:
        verdict = "HARD_PASS"
        msg = "frame+selectional beats type-level decisively; scramble kills gain (tier=MEASURED_MECHANISM)"
    else:
        verdict = "MIDDLE_BAND"
        msg = "frame-matching helps but not decisively"
    return {
        "verdict": verdict,
        "verdict_msg": msg,
        "tier_honest": "MEASURED_MECHANISM (WSD = better sense assignment, NOT compositional generalization)",
        "baseline_type_acc": b, "L1_frame_only_type_acc": l1, "mechanism_type_acc": m,
        "real_gain": real_gain, "scramble_type_acc_mean": scr_mean, "scramble_gain": scr_gain,
        "baseline_in_band": baseline_in_band, "scramble_kills_gain": scramble_kills,
        "improving_curve_type_acc": {"L0_baseline": b, "L1_frame": l1, "L2_frame_selrestr": m},
    }


# --- io / harness ----------------------------------------------------------
def output_dir():
    d = os.path.join(REPO, "data", "exp_" + ANCHOR_NAME)
    os.makedirs(d, exist_ok=True)
    return d


def _atomic_write(path, obj):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="ascii") as f:
        json.dump(obj, f, indent=2)
    os.replace(tmp, path)


def _write_crash(od, exc):
    diag = {"verdict": "CELL_CRASHED", "verdict_msg": (type(exc).__name__ + ": " + str(exc)[:400]),
            "summary": "CELL_CRASHED", "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:4000],
            "ts_iso": datetime.now(timezone.utc).isoformat(), "anchor_name": ANCHOR_NAME}
    _atomic_write(os.path.join(od, "metrics.json"), diag)


def arms_must_differ(res):
    """META_RULE_AF: baseline and mechanism per-item predictions must not be bit-identical."""
    def digest(level):
        preds = [str(p.get("pred_vn")) for p in res[level]["per_item"]]
        return hashlib.sha256("|".join(preds).encode("ascii")).hexdigest()
    da = digest("L0_baseline")
    dm = digest("L2_frame_selrestr")
    assert da != dm, "META_RULE_AF VIOLATION: baseline and mechanism produced identical predictions"
    return {"L0_baseline": da, "L2_frame_selrestr": dm}


def self_test():
    """Exercises the REAL code path (lexicon load, VerbNet frame lookup, POS parse,
    arms) at tiny scale + asserts a known frame-win case resolves correctly."""
    vn, wn, pos_tag, word_tokenize = _lazy_nltk()
    with open(LEXICON_PATH, "r", encoding="utf-8") as f:
        lex = json.load(f)["lexicon"]
    # real frame lookup
    sset, selr = vnclass_signatures("leave-51.2-1", vn)
    assert "INTRANS" in sset, ("leave-51.2-1 should license INTRANS, got " + str(sset))
    # POS frame extraction
    sig, prep, do, po = extract_sentence_frame(
        "Leave the keys on the table.", "leave", pos_tag, word_tokenize)
    assert sig == "NP_PP", ("expected NP_PP for deposit frame, got " + str(sig))
    sig2, _, _, _ = extract_sentence_frame(
        "They leave for London tomorrow morning.", "leave", pos_tag, word_tokenize)
    assert sig2 in ("PP", "INTRANS"), ("expected PP/INTRANS for depart frame, got " + str(sig2))
    # pool + candidate bridge saw->see
    cands = candidate_lemmas("saw", wn)
    assert "see" in cands and "saw" in cands, ("saw candidate bridge broken: " + str(cands))
    # arms return something on a control
    it = {"sent": "The chef cut the fresh bread.", "verb": "cut", "type": "change_of_state", "vn": "cut-21.1-1"}
    assert arm_baseline(it, lex, wn) is not None
    assert arm_mechanism(it, lex, wn, vn, pos_tag, word_tokenize) is not None
    print("[self-test] PASS: real lexicon+VerbNet+POS path exercised; frame signatures + arms OK", flush=True)
    return True


def run(mode):
    od = output_dir()
    t0 = datetime.now(timezone.utc)
    vn, wn, pos_tag, word_tokenize = _lazy_nltk()
    with open(LEXICON_PATH, "r", encoding="utf-8") as f:
        lex = json.load(f)["lexicon"]
    items = GOLD[:12] if mode == "smoke" else GOLD
    seeds = [1, 2, 3] if mode == "smoke" else list(range(1, 21))
    res = evaluate(items, lex, wn, vn, pos_tag, word_tokenize)
    scr = scramble_control(items, lex, wn, vn, pos_tag, word_tokenize, seeds)
    digests = arms_must_differ(res)
    verdict = make_verdict(res, scr)
    elapsed = (datetime.now(timezone.utc) - t0).total_seconds()
    out = {
        "anchor_name": ANCHOR_NAME, "run_mode": mode,
        "verdict": verdict["verdict"], "verdict_msg": verdict["verdict_msg"],
        "summary": ("baseline_type_acc=%.3f mech_type_acc=%.3f gain=%.3f scramble_mean=%.3f"
                    % (verdict["baseline_type_acc"], verdict["mechanism_type_acc"],
                       verdict["real_gain"], verdict["scramble_type_acc_mean"])),
        "elapsed_s": elapsed,
        "n_total": res["n_total"], "n_answerable": res["n_answerable"],
        "dropped_unanswerable": res["dropped"],
        "verdict_block": verdict,
        "binary_affected_acc": {"L0_baseline": res["L0_baseline"]["bin_acc"],
                                "L1_frame_only": res["L1_frame_only"]["bin_acc"],
                                "L2_frame_selrestr": res["L2_frame_selrestr"]["bin_acc"]},
        "scramble": scr,
        "arms_differ_verified": True, "arm_digests": digests,
        "per_item_L0_baseline": res["L0_baseline"]["per_item"],
        "per_item_L2_frame_selrestr": res["L2_frame_selrestr"]["per_item"],
        "ts_iso": t0.isoformat(),
    }
    _atomic_write(os.path.join(od, "metrics.json"), out)
    print("[run] mode=%s %s" % (mode, out["summary"]), flush=True)
    print("[run] verdict=%s (%s)" % (verdict["verdict"], verdict["verdict_msg"]), flush=True)
    print("[run] improving curve type_acc L0=%.3f L1=%.3f L2=%.3f"
          % (verdict["improving_curve_type_acc"]["L0_baseline"],
             verdict["improving_curve_type_acc"]["L1_frame"],
             verdict["improving_curve_type_acc"]["L2_frame_selrestr"]), flush=True)
    print("[run] baseline_in_band=%s scramble_kills_gain=%s n_answerable=%d dropped=%d"
          % (verdict["baseline_in_band"], verdict["scramble_kills_gain"],
             res["n_answerable"], len(res["dropped"])), flush=True)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--full", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        self_test()
        return
    mode = "smoke" if args.smoke else "full"
    run(mode)


if __name__ == "__main__":
    od_top = output_dir()
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        _write_crash(od_top, e)
        raise
