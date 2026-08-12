#!/usr/bin/env python
"""
build_verbnet_affectedness_lexicon.py

BUILD-TIME DATA RESOURCE (not a capability cell). Exports a type-level VERB
AFFECTEDNESS LEXICON from NLTK's bundled VerbNet (nltk.corpus.verbnet, 429
classes), for the English meaning-module's affectedness gate.

For every VerbNet verb we derive, from TWO signals:
  1. LEVIN CLASS TAXONOMY (Levin 1993): the class number encodes verb semantics
     (e.g. 45=change-of-state, 30=perception, 51=self-motion, 13=change-of-
     possession). A coarse class-number -> affectedness-type prior.
  2. SEMANTIC PREDICATES in the class FRAMES (Kipper-Schuler VerbNet): the frame
     predicate structure (cause / degradation_material_integrity / transfer /
     motion / perceive / desire ...) gives a precise, per-sense affectedness
     signal used both to assign the type and a GRADED proto-patient score
     (Dowty 1991 proto-patient entailments; Beavers 2011 affectedness
     hierarchy: full change-of-state > location/possession change > contact/
     motion > perception/cognition/stative).

Output types: change_of_state, effected, transfer, motion, contact,
perception, cognition, possession, other.

CREDITS: VerbNet (Kipper-Schuler 2005) ; Levin 1993 (English Verb Classes and
Alternations) ; Dowty 1991 (Thematic Proto-Roles) ; Beavers 2011 (affectedness
scale). This is a mechanical resource ingest with credited provenance; it makes
no capability claim.

LOCAL ONLY. No push / no remote-persist / no hdlab mutation. ASCII only.
"""
import json
import os
import re
import sys
import collections
from datetime import datetime, timezone

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTDIR = os.path.join(REPO, "data", "verbnet_affectedness_lexicon_v1")

# ---------------------------------------------------------------------------
# SIGNAL 1: Levin 1993 top-level class number -> coarse affectedness prior.
# Type + a base graded score. Used as a PRIOR / confirmation for the predicate
# signal, and as the fallback when no informative predicate is present.
# (Numbers are the integer Levin chapter; sub-classes inherit unless the
# predicate signal overrides.)
# ---------------------------------------------------------------------------
LEVIN_CLASS_MAP = {
    9:  ("motion", 0.50),        # put (caused change of location of Theme)
    10: ("change_of_state", 0.70),  # remove/clear/wipe (Theme removed/affected)
    11: ("motion", 0.50),        # send/carry/drive (caused motion of Theme)
    12: ("contact", 0.50),       # push/pull (exert force / carry)
    13: ("transfer", 0.70),      # change of possession (give/get/contribute)
    14: ("transfer", 0.60),      # learn/obtain (change of possession-ish)
    15: ("possession", 0.10),    # hold/keep/retain (stative-ish possession)
    17: ("motion", 0.50),        # throw/pelt (caused ballistic motion of Theme)
    18: ("contact", 0.45),       # hit/swat/spank (contact by impact)
    19: ("contact", 0.45),       # poke/prick
    20: ("contact", 0.40),       # touch/graze
    21: ("change_of_state", 0.90),  # cut (separation w/ material change)
    22: ("change_of_state", 0.70),  # combine/mix/amalgamate (config change)
    23: ("change_of_state", 0.70),  # separate/differ/disconnect
    24: ("change_of_state", 0.75),  # bend/crinkle (shape change)
    25: ("change_of_state", 0.70),  # tape/attach/fasten (attachment change)
    26: ("effected", 0.90),      # create/transform/build/performance/prepare
    27: ("change_of_state", 0.85),  # engender/produce
    29: ("cognition", 0.05),     # conjecture/consider/declare/appoint/dub
    30: ("perception", 0.05),    # see/sight/peer/stimulus (Experiencer/Stimulus)
    31: ("cognition", 0.10),     # psych (amuse/admire/marvel/appeal) - emotion
    32: ("cognition", 0.00),     # want/desire/need
    33: ("cognition", 0.05),     # judgment
    34: ("cognition", 0.05),     # assessment (study/analyze)
    35: ("perception", 0.05),    # search/hunt/seek (TARGET not affected)
    36: ("other", 0.10),         # social interaction (meet/marry/correspond)
    37: ("cognition", 0.05),     # communication (say/tell/advise) - transfer_info
    38: ("other", 0.15),         # sound emission
    39: ("change_of_state", 0.85),  # ingesting (eat/devour/chew) - food consumed
    40: ("other", 0.10),         # body-internal / nonverbal expression
    41: ("change_of_state", 0.60),  # dress/preen (change appearance)
    42: ("change_of_state", 0.90),  # murder/poison/hurt (harm)
    43: ("other", 0.15),         # emission (light/sound/substance)
    44: ("change_of_state", 1.00),  # destroy (annihilate/ruin)
    45: ("change_of_state", 0.95),  # CHANGE OF STATE (break/dry/open/freeze)
    46: ("other", 0.10),         # lodge/reside
    47: ("possession", 0.05),    # exist / spatial-config / possession-stative
    48: ("other", 0.15),         # appear/disappear/occur
    49: ("other", 0.10),         # body-internal states (posture)
    50: ("other", 0.10),         # assuming position
    51: ("motion", 0.05),        # SELF-MOTION (run/roll/vehicle/waltz/leave)
    52: ("other", 0.10),         # avoid
    53: ("other", 0.10),         # lingering/rushing
    54: ("other", 0.15),         # measure/cost/weigh
    55: ("other", 0.10),         # aspectual (begin/continue/stop)
    56: ("other", 0.10),         # weather
    57: ("other", 0.10),         # weather / begin
    58: ("cognition", 0.05),     # urge/force/order (compel)
    59: ("cognition", 0.10),     # force/prevent
    60: ("cognition", 0.05),     # try/manage
    61: ("cognition", 0.05),     # help/enable (limit)
    62: ("cognition", 0.05),     # care/hate
    63: ("cognition", 0.05),     # long/aspire
    64: ("cognition", 0.05),     # allow/permit
    65: ("cognition", 0.05),     # forbid/prohibit
    66: ("cognition", 0.05),     # want (subordinate)
    67: ("other", 0.10),         # withdraw/rebel
    68: ("cognition", 0.05),     # promise/agree
    69: ("cognition", 0.05),     # conspire
    70: ("cognition", 0.05),     # want
    71: ("other", 0.10),         # wish
    72: ("other", 0.15),         # rely/depend
    73: ("other", 0.15),         # neglect/succeed (accompany)
    74: ("other", 0.15),         # bother/matter
    75: ("cognition", 0.10),     # focus/concentrate
    76: ("cognition", 0.10),     # comprehend/estimate
    77: ("other", 0.15),         # settle/patrol (rummage)
    78: ("perception", 0.05),    # spatial config / sight
    79: ("other", 0.15),         # exceed/dominate (contiguous location)
    80: ("other", 0.15),         # contiguous location
    81: ("possession", 0.05),    # possession relations (own/belong)
    82: ("cognition", 0.10),     # disappearance / mental
    83: ("other", 0.15),         # admit/allow
    84: ("cognition", 0.10),     # confront/withdraw
    85: ("transfer", 0.55),      # give/equip/provide (fulfilling)
    86: ("other", 0.15),         # future-having
    87: ("cognition", 0.10),     # sight/discovery
    88: ("other", 0.15),         # meander / entity-specific
    89: ("other", 0.15),         # weekend/vacation
    90: ("other", 0.15),         # captain (entity-specific)
    91: ("cognition", 0.10),     # court/woo
    92: ("cognition", 0.10),     # subjugate
    93: ("change_of_state", 0.60),  # adjust/coordinate
    94: ("cognition", 0.10),     # feign/simulate
}

# ---------------------------------------------------------------------------
# SIGNAL 2: predicate -> (type, graded score). The MAX-scoring informative
# predicate present in a class's frames sets the dominant affectedness. Generic
# predicates (cause, Pred, Prep, Adv, manner, use, Predicate) carry NO
# affectedness on their own and are excluded from the argmax; they only mark
# agentivity/instrument. Scores follow Dowty/Beavers: strongest result-state
# entailment -> highest.
# ---------------------------------------------------------------------------
PRED_MAP = {
    # --- full change-of-state result entailments (high) ---
    "degradation_material_integrity": ("change_of_state", 1.00),
    "convert":                        ("change_of_state", 1.00),
    "harmed":                         ("change_of_state", 1.00),
    "destroyed":                      ("change_of_state", 1.00),
    "change_value":                   ("change_of_state", 0.90),
    "cooked":                         ("change_of_state", 0.95),
    "apply_heat":                     ("change_of_state", 0.90),
    "physical_form":                  ("change_of_state", 0.85),
    "created_image":                  ("effected", 0.95),
    # configuration / attachment change (mid-high)
    "together":                       ("change_of_state", 0.70),
    "apart":                          ("change_of_state", 0.70),
    "mingled":                        ("change_of_state", 0.70),
    "covered":                        ("change_of_state", 0.65),
    "made_of":                        ("effected", 0.60),
    # --- transfer / possession change (mid-high) ---
    "transfer":                       ("transfer", 0.75),
    "has_possession":                 ("transfer", 0.70),   # dynamic w/ transfer; stative handled below
    # --- caused / self motion & location (mid / low, disambiguated by roles) ---
    "motion":                         ("motion", 0.50),
    "location":                       ("motion", 0.40),
    "direction":                      ("motion", 0.40),
    # --- contact / force (mid) ---
    "exert_force":                    ("contact", 0.50),
    "contact":                        ("contact", 0.45),
    "take_in":                        ("change_of_state", 0.80),  # ingest (consume)
    # --- perception (low) ---
    "discover":                       ("perception", 0.10),
    "perceive":                       ("perception", 0.05),
    "visible":                        ("perception", 0.05),
    "search":                         ("perception", 0.05),
    "experience":                     ("perception", 0.05),
    # --- cognition / communication / emotion (zero-ish) ---
    "transfer_info":                  ("cognition", 0.10),
    "desire":                         ("cognition", 0.00),
    "consider":                       ("cognition", 0.00),
    "declare":                        ("cognition", 0.00),
    "describe":                       ("cognition", 0.00),
    "indicate":                       ("cognition", 0.05),
    "express":                        ("cognition", 0.05),
    "about":                          ("cognition", 0.05),
    "emotional_state":                ("cognition", 0.10),
    "in_reaction_to":                 ("cognition", 0.10),
    # --- other / stative (zero-ish) ---
    "emit":                           ("other", 0.15),
    "social_interaction":             ("other", 0.10),
    "exist":                          ("possession", 0.05),
    "state":                          ("other", 0.20),
    "equals":                         ("possession", 0.05),
    "position":                       ("other", 0.15),
    "body_process":                   ("other", 0.15),
    "cost":                           ("other", 0.10),
    "value":                          ("other", 0.10),
    "property":                       ("other", 0.20),
}
# predicates deliberately ignored for the argmax (agentivity/instrument/glue)
GENERIC_PREDS = {"cause", "Pred", "Prep", "Adv", "manner", "use", "Predicate",
                 "begin", "end", "appear", "designated"}


def load_verbnet():
    from nltk.corpus import verbnet as vn
    vn.classids("build")  # force corpus load; raises if unavailable
    return vn


def class_top_number(cid):
    m = re.search(r"-(\d+)", cid)
    return int(m.group(1)) if m else None


def ancestor_ids(cid):
    """VerbNet subclass ids inherit THEMROLES from their parent. Yield cid and
    each ancestor id formed by stripping trailing '-<int>' subclass markers
    (e.g. put-9.1-2 -> put-9.1). The Levin number segment (e.g. 9.1) is kept."""
    ids = [cid]
    cur = cid
    while True:
        m = re.match(r"^(.*)-\d+$", cur)
        if not m:
            break
        parent = m.group(1)
        # only strip the SUBCLASS integer, not the Levin class number: a valid
        # ancestor still contains the Levin number (a digit somewhere after '-').
        if not re.search(r"-\d", parent):
            break
        ids.append(parent)
        cur = parent
    return ids


def class_signals(vn, cid):
    """Return (roles, predicates_set) for a VerbNet class id. Roles are merged
    across the ancestor chain because NLTK exposes only subclass-local THEMROLES
    (inherited Agent/etc. live on the parent)."""
    roles = []
    preds = set()
    seen_roles = set()
    for aid in ancestor_ids(cid):
        try:
            vc = vn.vnclass(aid)
        except Exception:
            continue
        tr = vc.find("THEMROLES")
        if tr is not None:
            for t in tr.findall("THEMROLE"):
                rt = t.get("type")
                if rt and rt not in seen_roles:
                    seen_roles.add(rt)
                    roles.append(rt)
        frames = vc.find("FRAMES")
        if frames is not None:
            for fr in frames.findall("FRAME"):
                sem = fr.find("SEMANTICS")
                if sem is None:
                    continue
                for p in sem.findall("PRED"):
                    v = p.get("value")
                    if v:
                        preds.add(v)
    return roles, preds


def score_sense(cid, roles, preds):
    """Assign (affectedness_type, graded_score, source_signal, detail) for one
    VerbNet class sense, combining the Levin-class prior with the predicate
    argmax."""
    top = class_top_number(cid)
    levin_type, levin_score = LEVIN_CLASS_MAP.get(top, ("other", 0.15))

    # predicate argmax over INFORMATIVE predicates
    best = None  # (score, type, pred)
    for p in preds:
        if p in GENERIC_PREDS or p not in PRED_MAP:
            continue
        ptype, pscore = PRED_MAP[p]
        if best is None or pscore > best[0]:
            best = (pscore, ptype, p)

    roleset = set(roles)
    has_agent = "Agent" in roleset or "Cause" in roleset
    has_object = bool(roleset & {"Patient", "Theme", "Product", "Material",
                                 "Recipient", "Destination", "Stimulus"})

    if best is not None:
        pscore, ptype, ppred = best
        pred_type, pred_score = ptype, pscore

        # --- motion disambiguation: caused (Agent moves a distinct Theme) vs
        #     self-motion (mover is the subject) ---
        if ptype == "motion":
            theme_distinct = bool(roleset & {"Theme", "Patient"})
            if has_agent and theme_distinct:
                pred_score = max(pscore, 0.50)   # caused motion: Theme location change
            else:
                pred_type, pred_score = "motion", 0.05  # self-motion: not affected

        # --- possession disambiguation: stative have/own (has_possession as the
        #     ONLY/dominant possession pred, no transfer, no agent-driven change)
        #     -> possession/none; dynamic (transfer present) -> transfer ---
        if ppred == "has_possession" and "transfer" not in preds:
            pred_type, pred_score = "possession", 0.05

        source = "predicate"
        detail = "pred=%s levin=%d(%s)" % (ppred, top if top else -1, levin_type)
        final_type, final_score = pred_type, pred_score

        # Levin agreement bump/blend: if the Levin prior agrees on type, keep the
        # (more precise) predicate score. If they disagree, trust the predicate
        # but record the conflict.
        if levin_type != final_type:
            detail += " [levin_disagree:%s]" % levin_type
    else:
        # no informative predicate -> fall back to Levin class prior
        final_type, final_score = levin_type, levin_score
        source = "levin_class"
        detail = "no_informative_pred levin=%d" % (top if top else -1)

    return final_type, round(float(final_score), 3), source, detail


def build():
    vn = load_verbnet()
    cids = vn.classids()

    # cache per-class signal (a verb's senses reference full class ids incl
    # subclasses; vn.classids(lemma) returns the specific subclass id).
    verb_to_senses = collections.defaultdict(list)  # lemma -> [ (cid, type, score, source, detail) ]

    # iterate every class + subclass, enumerate member verbs
    all_class_ids = set(cids)
    # NLTK verbnet: lexemes via vn.lemmas(); map lemma->classids via classids(lemma)
    lemmas = sorted(set(vn.lemmas()))
    for lemma in lemmas:
        try:
            senses = vn.classids(lemma)
        except Exception:
            senses = []
        for cid in senses:
            roles, preds = class_signals(vn, cid)
            atype, ascore, source, detail = score_sense(cid, roles, preds)
            verb_to_senses[lemma].append({
                "vn_class": cid, "affectedness_type": atype,
                "graded_score": ascore, "source_signal": source,
                "detail": detail,
            })

    lexicon = {}
    for lemma, senses in verb_to_senses.items():
        # DOMINANT sense: modal affectedness_type across senses (the typical
        # reading), tie-broken by highest mean score of that type (in doubt, the
        # verb CAN affect). graded_score = mean score of the dominant type's
        # senses. Full per_sense retained; the gate defers to token context on
        # sense_ambiguous verbs (score straddles the affected line).
        scores = [s["graded_score"] for s in senses]
        by_type = collections.defaultdict(list)
        for s in senses:
            by_type[s["affectedness_type"]].append(s["graded_score"])
        max_freq = max(len(v) for v in by_type.values())
        tied = [(t, sum(v) / len(v)) for t, v in by_type.items()
                if len(v) == max_freq]
        dom_type, dom_score = max(tied, key=lambda x: x[1])
        straddle = (max(scores) > 0.5 and min(scores) < 0.2)
        lexicon[lemma] = {
            "affectedness_type": dom_type,
            "graded_score": round(float(dom_score), 3),
            "vn_classes": sorted(set(s["vn_class"] for s in senses)),
            "source_signal": "modal_type_across_%d_senses" % len(senses),
            "n_senses": len(senses),
            "sense_ambiguous": bool(straddle),
            "per_sense": senses,
        }
    return lexicon, len(all_class_ids), len(lemmas)


# ---------------------------------------------------------------------------
# coverage + quality
# ---------------------------------------------------------------------------
def mcguffey_verbs():
    p = os.path.join(REPO, "data", "mcguffey_whoaffected_oracle_gold_v1", "gold.json")
    g = json.load(open(p))
    return sorted(set(r["verb"].lower() for r in g["gold"]))


def ud_verbs():
    p = os.path.join(REPO, "data", "gold_construction_argstruct_ewt_v1",
                     "gold_construction_argstruct_ewt_v1.json")
    u = json.load(open(p))
    verbs = set()
    for r in u["gold"].values() if isinstance(u["gold"], dict) else u["gold"]:
        v = r.get("verb")
        if isinstance(v, dict):
            verbs.add(str(v.get("lemma", "")).lower())
        elif v:
            verbs.add(str(v).lower())
    verbs.discard("")
    return sorted(verbs)


# known-answer spot-check: verb -> (expected affected? True/False, VerbNet-fair
# acceptable types). Acceptable type-sets reflect VerbNet's ACTUAL classification
# (e.g. VerbNet lists 'hand' as caused-motion send-11.1, 'see' under cognition
# classes as well as perception). The load-bearing metric is the affected/not
# DECISION; the type is a secondary plausibility check.
KNOWN20 = {
    "see":   (False, {"perception", "cognition"}),
    "break": (True,  {"change_of_state"}),
    "feed":  (True,  {"change_of_state", "transfer"}),
    "fill":  (True,  {"change_of_state", "motion", "other"}),
    "put":   (True,  {"motion", "change_of_state"}),
    "have":  (False, {"possession", "other"}),   # VerbNet-OOV (stative gap)
    "own":   (False, {"possession", "other"}),    # VerbNet-OOV (stative gap)
    "run":   (False, {"motion", "other"}),
    "leave": (False, {"motion", "other", "transfer", "possession"}),
    "go":    (False, {"motion", "other"}),
    "give":  (True,  {"transfer"}),
    "hand":  (True,  {"transfer", "motion"}),
    "pat":   (True,  {"contact"}),
    "touch": (True,  {"contact"}),
    "think": (False, {"cognition"}),
    "eat":   (True,  {"change_of_state"}),
    "cut":   (True,  {"change_of_state"}),
    "carry": (True,  {"motion"}),
    "want":  (False, {"cognition"}),
    "know":  (False, {"cognition"}),
}


def coverage_and_quality(lexicon):
    mv = mcguffey_verbs()
    # McGuffey uses surface/inflected forms + phrasals; map to lemma head
    LEMMA_FIX = {"fed": "feed", "ran": "run", "left": "leave", "has": "have",
                 "get up": "get", "look at": "look"}
    mcg_lemmas = sorted(set(LEMMA_FIX.get(v, v) for v in mv))
    mcg_hit = [v for v in mcg_lemmas if v in lexicon]
    mcg_cov = 100.0 * len(mcg_hit) / len(mcg_lemmas)

    uv = ud_verbs()
    ud_hit = [v for v in uv if v in lexicon]
    ud_cov = 100.0 * len(ud_hit) / len(uv) if uv else 0.0

    # quality spot-check on KNOWN20. Primary metric = affected/not DECISION;
    # secondary = type plausibility. OOV (VerbNet coverage gap) and
    # sense_ambiguous verbs are reported separately (honest denominators).
    AFFECTED_THRESHOLD = 0.35   # >= => "affected"; below => not affected
    rows = []
    decision_correct = 0
    both_correct = 0
    n_scored = 0          # covered, non-OOV
    n_oov = 0
    n_ambiguous = 0
    for v, (exp_aff, ok_types) in KNOWN20.items():
        e = lexicon.get(v)
        if e is None:
            rows.append((v, "OOV", None, exp_aff, "OOV"))
            n_oov += 1
            continue
        n_scored += 1
        got_aff = e["graded_score"] >= AFFECTED_THRESHOLD
        dec_ok = (got_aff == exp_aff)
        type_ok = e["affectedness_type"] in ok_types
        both_ok = dec_ok and type_ok
        decision_correct += 1 if dec_ok else 0
        both_correct += 1 if both_ok else 0
        tag = "OK" if both_ok else ("dec_ok/type_off" if dec_ok else "XX")
        if e["sense_ambiguous"]:
            tag += "*"
            n_ambiguous += 1
        rows.append((v, e["affectedness_type"], round(e["graded_score"], 2),
                     exp_aff, tag))
    acc_decision = 100.0 * decision_correct / n_scored if n_scored else 0.0
    acc_both = 100.0 * both_correct / n_scored if n_scored else 0.0

    return {
        "mcguffey": {"lemmas": mcg_lemmas, "covered": mcg_hit,
                     "missed": [v for v in mcg_lemmas if v not in lexicon],
                     "coverage_pct": round(mcg_cov, 1)},
        "ud_ewt": {"n": len(uv), "covered": len(ud_hit),
                   "missed": [v for v in uv if v not in lexicon],
                   "coverage_pct": round(ud_cov, 1)},
        "spot_check": {"threshold": AFFECTED_THRESHOLD,
                       "decision_accuracy_pct": round(acc_decision, 1),
                       "type_and_decision_accuracy_pct": round(acc_both, 1),
                       "n_total": len(KNOWN20), "n_scored": n_scored,
                       "n_oov": n_oov, "n_sense_ambiguous": n_ambiguous,
                       "decision_correct": decision_correct,
                       "both_correct": both_correct, "rows": rows},
    }


def main():
    os.makedirs(OUTDIR, exist_ok=True)
    lexicon, n_classes, n_lemmas = build()
    cov = coverage_and_quality(lexicon)

    # type distribution
    dist = collections.Counter(e["affectedness_type"] for e in lexicon.values())
    ambiguous = sum(1 for e in lexicon.values() if e["sense_ambiguous"])

    meta = {
        "name": "verbnet_affectedness_lexicon_v1",
        "built_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "builder": "tools/build_verbnet_affectedness_lexicon.py",
        "resource": "nltk.corpus.verbnet (VerbNet 3.x bundled with NLTK)",
        "n_verbnet_classes": n_classes,
        "n_verbs": len(lexicon),
        "signals": ["levin_class_taxonomy (Levin 1993)",
                    "semantic_predicates (VerbNet frame PRED structure)"],
        "graded_score": "proto-patient affectedness in [0,1] (Dowty 1991 / "
                        "Beavers 2011): full change-of-state ~1.0 > location/"
                        "possession change ~0.5-0.75 > contact/caused-motion "
                        "~0.4-0.5 > perception/cognition/stative ~0.0-0.1",
        "affectedness_types": sorted(dist.keys()),
        "type_distribution": dict(dist),
        "n_sense_ambiguous": ambiguous,
        "credits": ["VerbNet: Kipper-Schuler 2005", "Levin 1993 (verb classes)",
                    "Dowty 1991 (proto-roles)", "Beavers 2011 (affectedness)"],
        "usage": "type-level grounding for the who-is-affected affectedness "
                 "gate; dominant sense = max graded_score; per_sense retained "
                 "for multi-sense disambiguation; sense_ambiguous flags verbs "
                 "straddling the affected line.",
        "caveats": "build-time resource ingest; NO capability claim. Type-level "
                   "only (ignores token-level context/negation/coercion). "
                   "Multi-sense verbs collapsed to a max-score dominant. Levin "
                   "class prior is coarse; predicate argmax is per-sense but "
                   "VerbNet frame predicate coverage is uneven.",
    }
    out = {"_meta": meta, "coverage": cov, "lexicon": lexicon}
    with open(os.path.join(OUTDIR, "lexicon.json"), "w") as f:
        json.dump(out, f, indent=1)

    # human-readable one-liner + spot-check table to stdout
    print("=== verbnet_affectedness_lexicon_v1 built ===")
    print("verbs=%d  classes=%d  types=%s" % (len(lexicon), n_classes, dict(dist)))
    print("sense_ambiguous=%d" % ambiguous)
    print("McGuffey verb coverage: %.1f%% (%d/%d) missed=%s" % (
        cov["mcguffey"]["coverage_pct"], len(cov["mcguffey"]["covered"]),
        len(cov["mcguffey"]["lemmas"]), cov["mcguffey"]["missed"]))
    print("UD-EWT verb coverage: %.1f%% (%d/%d) missed=%s" % (
        cov["ud_ewt"]["coverage_pct"], cov["ud_ewt"]["covered"],
        cov["ud_ewt"]["n"], cov["ud_ewt"]["missed"]))
    sc = cov["spot_check"]
    print("Spot-check (known-20) thr=%.2f: DECISION acc=%.1f%% (%d/%d scored); "
          "type+decision acc=%.1f%%; OOV=%d ambiguous=%d" % (
              sc["threshold"], sc["decision_accuracy_pct"],
              sc["decision_correct"], sc["n_scored"],
              sc["type_and_decision_accuracy_pct"], sc["n_oov"],
              sc["n_sense_ambiguous"]))
    for v, t, s, exp, tag in sc["rows"]:
        print("   %-7s type=%-15s score=%-5s exp_affected=%-5s %s" % (
            v, t, s, exp, tag))
    print("wrote", os.path.join(OUTDIR, "lexicon.json"))


if __name__ == "__main__":
    main()
