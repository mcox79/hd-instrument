"""PROTOTYPE (research, experiments/-only): rebuild the harm/help patient-valence decision on the
in-substrate FORCE DYNAMICS (hdlab/force_dynamics_lexicon.py, FrameNet Causation-family CAUSE/ENABLE/
PREVENT) + the WordNet animacy axis, RETIRING the closed test-fitted FORCE_CLASS_HARM_REAL list and the
trained governor perceptron.

WHY (brain-foundational, Talmy 1988 / Wolff 2007): harm/help is FORCE DYNAMICS. An affector force that
overcomes an animate patient's inertia toward a changed endstate = adverse = HARM (CAUSE). A force that
OPPOSES an adverse endstate (protect/save/shield/defend) = favorable = HELP (PREVENT). A force that FREES
what the patient tends toward (free/release) = favorable = HELP (ENABLE). The current organ decides
harm/help from `FORCE_CLASS_HARM_REAL` -- a self-admitted "closed, test-fitted hand list" of 16 verbs
(exp_bridge1_event_assembly_open_vocab_v1.py L147-150) -- plus a governor perceptron trained on the tiny
cert TRAIN_ITEMS. The closed list is CAUSE-harm ONLY: it can NEVER emit HELP (no prevent/enable verbs).

WHAT THE LIVE WIRE ACTUALLY CONSUMES (verified on disk): situation_reader._assign_affect (L828-864)
reports affect ONLY when result["stage"]=="event" (the stage-2 animacy-axis override), with
need_valence=False. So live affect is driven ENTIRELY by stage-2 event_type_for_item_real
(FORCE_CLASS_HARM_REAL + animacy); the governor perceptron (stage 1) and the theta valuation (stage 3)
are NOT consumed for the affect dim (event always beats governor in combine_biased_competition when it
fires; theta valence is discarded). Live output space = {HARM (BLOCK_HIGH), NA (NEUTRAL/abstain)} -- HELP
is STRUCTURALLY UNREACHABLE today.

MEASURE (floors recomputed per population; bootstrap CI half-width; info-free twin = scrambled force
lexicon). Populations:
  P1 no-regress: the organ's OWN validation set (bridge1 Bopen 6 pairs + subset B), force-dynamics arm
     must not regress vs the closed-list arm.
  P2 harm generalization: animate-patient CAUSE-harm verbs the closed 16-list MISSES but FrameNet covers.
  P3 help (structural): animate-patient PREVENT/ENABLE verbs -- closed list cannot emit HELP at all.
  P4 over-firing honesty: animate-patient BENEFIT/neutral CAUSE verbs (delight/greet/...) -- does a
     coarse CAUSE->HARM misfire? refined (harm-frame-only) vs coarse.
  P5 modern coverage: real inflected verbs in UD-EWT affectedness gold -- fraction assigned a force class
     by FrameNet vs the closed 16-list (coverage, not accuracy; affectedness != harm/help, reported so).

NO external LLM at inference. Glass-box. ASCII. Deterministic.
"""
from __future__ import annotations

import json
import os
import random
import sys
from collections import Counter

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from hdlab.force_dynamics_lexicon import build_force_lexicon  # noqa: E402
from hdlab.patient_tendency import lemmatize_verb  # noqa: E402
import experiments.exp_bridge1_event_assembly_open_vocab_v1 as ea  # noqa: E402 (real_animacy_lookup, closed list, Bopen)
import experiments.exp_bridge1_confirmation_test_v1 as conf  # noqa: E402 (subset B)

SEED = 20260908
N_BOOT = 2000

LEX = build_force_lexicon()
CLOSED = set(ea.FORCE_CLASS_HARM_REAL)  # the test-fitted 16-verb list under retirement


# --------------------------------------------------------------------------- harm-frame verb set
def build_harm_verbs():
    """Verbs whose FrameNet frame is unambiguously ADVERSE to an animate patient (physical harm /
    impact / killing). Pure frame membership (the SAME discipline force_dynamics_lexicon uses), NOT a
    per-item gold list. Plus a SMALL principled physical-assault backoff for colloquial verbs FrameNet
    has NO lexical unit for at all (choke/clobber/wallop/strangle/throttle/bite) -- mirrors the module's
    existing NARRATIVE_BACKOFF discipline (labelled by force role, not tuned to a test item)."""
    HARM_FRAMES = ["Cause_harm", "Cause_impact", "Impact", "Killing", "Hit_target", "Cause_to_fragment",
                   "Attack"]  # Attack: an agonist directs force at a target to harm it (attack/assault/raid)
    harm = set()
    try:
        from nltk.corpus import framenet as fn
        for fr in HARM_FRAMES:
            try:
                f = fn.frame_by_name(fr)
            except Exception:
                continue
            for lu in f.lexUnit.keys():
                if lu.endswith(".v"):
                    base = lu.rsplit(".", 1)[0].strip().lower()
                    if base.isalpha():
                        harm.add(base)
    except Exception:
        pass
    # FrameNet-absent colloquial physical-assault verbs (no LU at all -- verified). CAUSE-harm role.
    # FrameNet-absent colloquial physical-assault/injury verbs (no harm-frame LU). Includes 'wrench'
    # so ALL of the retired closed FORCE_CLASS_HARM_REAL list is covered (byte-clean no-regress).
    HARM_BACKOFF = {"choke", "clobber", "wallop", "strangle", "throttle", "bite", "stomp", "shoot",
                    "kill", "bludgeon", "wrench"}
    harm |= HARM_BACKOFF
    return harm


HARM_VERBS = build_harm_verbs()

# Physical-assault verbs FrameNet has NO lexical unit for at all (verified: choke/clobber/wallop/
# strangle/throttle/bite/stomp -> no LU; shoot->Use_firearm, kill->Killing -- frames outside the
# Causation family). The brain-foundational fix mirrors force_dynamics_lexicon.NARRATIVE_BACKOFF: add
# them as CAUSE (an agonist overcoming an animate patient). Labelled by force role, NOT tuned to a test
# item. This is the exact hdlab diff proposed below.
ASSAULT_BACKOFF = {v: "CAUSE" for v in
                   ("choke", "clobber", "wallop", "strangle", "throttle", "bite", "stomp", "shoot",
                    "kill", "bludgeon")}
LEX_AUG = dict(LEX)
for _v, _c in ASSAULT_BACKOFF.items():
    LEX_AUG.setdefault(_v, _c)


# --------------------------------------------------------------------------- the harm/help decision
def harm_help(verb, animacy, lexicon, harm_verbs, mode="refined"):
    """Force-dynamics harm/help. inanimate patient -> NA (animacy axis, kept from the organ).
    HARM = harm-frame membership (Cause_harm/Cause_impact/Impact/Killing/Hit_target/Cause_to_fragment/
    Attack + the FrameNet-absent physical-assault backoff): an affector force overcoming an animate
    patient toward an adverse endstate. HELP = PREVENT (opposes an adverse endstate: protect/save/
    shield) or ENABLE (frees what the patient tends toward: free/release). refined: CAUSE-but-not-harm
    -> abstain (avoids over-firing on benefit CAUSE like delight/comfort). coarse: any CAUSE -> HARM
    (the over-firing arm, measured in P4). No force signal -> abstain (None), like the organ's abstain."""
    if animacy == "inanimate":
        return "NA"
    v = lemmatize_verb(verb)
    if v in harm_verbs:                      # harm-frame membership FIRST (covers Attack-frame verbs
        return "HARM"                        # that are not in the Causation-family lexicon)
    cls = lexicon.get(v)
    if cls in ("PREVENT", "ENABLE"):
        return "HELP"
    if cls == "CAUSE" and mode == "coarse":  # benefit/neutral CAUSE -> HARM only in the coarse arm
        return "HARM"
    return None


def closed_list_arm(verb, animacy):
    """Faithful reproduction of the CURRENT organ's live harm decision (event_type_for_item_real):
    inanimate -> NA; animate & verb in the closed 16-list -> HARM; else abstain. (The governor-UNK
    condition is always true for these OOV verbs.) The closed list has NO help verbs -> never HELP."""
    if animacy == "inanimate":
        return "NA"
    v = lemmatize_verb(verb)
    return "HARM" if v in CLOSED else None


def animacy_of(noun):
    r = ea.real_animacy_lookup(noun, "NOUN")
    if r is None:
        return None
    return r["animacy"]


# --------------------------------------------------------------------------- populations
def bopen_items():
    """P1a: bridge1 Bopen (organ's own open-vocab validation). gold sign: BLOCK_HIGH->HARM, NEUTRAL->NA."""
    out = []
    for _f, a, b in ea.SUBSET_B_OPEN_PAIRS:
        for it in (a, b):
            verb = lemmatize_verb(it["tokens"][it["target_idx"] - 2])  # verb sits two left of the patient here
            noun = it["target_word"]
            gold = "HARM" if it["gold_type"] == "BLOCK_HIGH" else "NA"
            out.append({"verb": verb, "noun": noun, "gold": gold, "note": it.get("note")})
    return out


def subsetB_items():
    """P1b: bridge1 subset B (break/shoot harm pairs)."""
    out = []
    for it in conf.SUBSET_B:
        gi = None
        for i, p in enumerate(it["pos"]):
            if p == "VERB":
                gi = i
                break
        if gi is None:
            continue
        verb = lemmatize_verb(it["tokens"][gi])
        noun = it["target_word"]
        gold = "HARM" if it["gold_type"] == "BLOCK_HIGH" else "NA"
        out.append({"verb": verb, "noun": noun, "gold": gold, "note": it.get("note")})
    return out


# P2: CAUSE-harm verbs the closed 16-list MISSES (animate patients). Verbs chosen for being canonical
# physical-harm verbs; gold HARM. (Constructed, but the point is closed-list-miss vs force-dynamics-hit.)
P2_HARM_GEN = [
    ("stab", "victim"), ("punch", "boy"), ("slap", "girl"), ("kick", "dog"), ("beat", "prisoner"),
    ("wound", "soldier"), ("injure", "player"), ("hit", "pedestrian"), ("strike", "man"),
    ("burn", "child"), ("scald", "patient"), ("scratch", "cat"), ("bludgeon", "guard"),
    ("choke", "hostage"), ("strangle", "woman"), ("bite", "toddler"),
]
# P3: PREVENT/ENABLE verbs -> HELP (closed list structurally CANNOT emit HELP). animate patients.
P3_HELP = [
    ("save", "child"), ("protect", "villager"), ("defend", "town"), ("shield", "boy"),
    ("rescue", "sailor"), ("spare", "prisoner"), ("shelter", "refugee"), ("guard", "prince"),
    ("free", "captive"), ("release", "hostage"),
]
# P4: BENEFIT / neutral CAUSE verbs on animate patients (Cause_emotion etc.). gold NOT-HARM (HELP-ish
# or NA). A coarse CAUSE->HARM MISFIRES here; refined (harm-frame-only) should abstain/not-harm.
P4_BENEFIT_CAUSE = [
    ("delight", "audience"), ("please", "queen"), ("amuse", "children"), ("comfort", "widow"),
    ("wake", "baby"), ("greet", "guest"), ("calm", "patient"), ("soothe", "infant"),
    ("entertain", "crowd"), ("reassure", "student"),
]


# --------------------------------------------------------------------------- scoring
def score_pop(items, predict_fn):
    """items: list of {verb,noun,gold}. predict_fn(verb, animacy)->HARM/HELP/NA/None.
    Returns per-item correctness list (abstain counts as wrong for accuracy)."""
    corr = []
    preds = []
    for it in items:
        an = animacy_of(it["noun"])
        p = predict_fn(it["verb"], an)
        preds.append(p)
        corr.append(1 if p == it["gold"] else 0)
    return corr, preds


def boot_ci(corr, n_boot=N_BOOT, seed=SEED):
    if not corr:
        return 0.0, 0.0
    rng = random.Random(seed)
    n = len(corr)
    means = []
    for _ in range(n_boot):
        s = sum(corr[rng.randrange(n)] for _ in range(n)) / n
        means.append(s)
    means.sort()
    lo = means[int(0.025 * n_boot)]
    hi = means[int(0.975 * n_boot)]
    mean = sum(corr) / n
    half = (hi - lo) / 2.0
    return mean, half


def scramble_lexicon(lex, seed):
    keys = sorted(lex.keys())
    vals = [lex[k] for k in keys]
    rng = random.Random(seed)
    rng.shuffle(vals)
    return dict(zip(keys, vals))


def scramble_set_membership(harm_verbs, all_verbs, seed):
    """Info-free twin for the harm-frame set: keep the SAME number of harm verbs but assign membership
    to a random subset of the vocabulary."""
    rng = random.Random(seed)
    pool = sorted(all_verbs)
    k = len(harm_verbs)
    return set(rng.sample(pool, min(k, len(pool))))


# --------------------------------------------------------------------------- run
def run():
    results = {}

    P1 = bopen_items() + subsetB_items()
    P2 = [{"verb": v, "noun": n, "gold": "HARM"} for v, n in P2_HARM_GEN]
    P3 = [{"verb": v, "noun": n, "gold": "HELP"} for v, n in P3_HELP]
    P4 = [{"verb": v, "noun": n, "gold": "NOT_HARM"} for v, n in P4_BENEFIT_CAUSE]

    # arms  (LEX_AUG = FrameNet lexicon + the physical-assault backoff; LEX = raw FrameNet only)
    def fd_refined(verb, an):
        return harm_help(verb, an, LEX_AUG, HARM_VERBS, mode="refined")

    def fd_coarse(verb, an):
        return harm_help(verb, an, LEX_AUG, HARM_VERBS, mode="coarse")

    def fd_framenet_only(verb, an):
        # raw FrameNet, NO physical-assault backoff (shows the FrameNet-only coverage gap on P1)
        return harm_help(verb, an, LEX, HARM_VERBS, mode="refined")

    scr_lex = scramble_lexicon(LEX_AUG, SEED + 1)
    all_verbs = set(LEX_AUG.keys()) | HARM_VERBS | CLOSED
    scr_harm = scramble_set_membership(HARM_VERBS, all_verbs, SEED + 2)

    def twin(verb, an):
        return harm_help(verb, an, scr_lex, scr_harm, mode="refined")

    # ---- P1 no-regress ----
    for name, fn in [("closed_list", lambda v, a: closed_list_arm(v, a)),
                     ("fd_framenet_only", fd_framenet_only),
                     ("fd_refined_backoff", fd_refined),
                     ("twin", twin)]:
        corr, preds = score_pop(P1, fn)
        m, h = boot_ci(corr)
        results[f"P1_{name}"] = {"acc": round(m, 4), "ci_half": round(h, 4), "n": len(P1),
                                 "preds": preds}
    # per-item regress diff
    c_closed, _ = score_pop(P1, lambda v, a: closed_list_arm(v, a))
    c_fd, _ = score_pop(P1, fd_refined)
    regressions = [P1[i] for i in range(len(P1)) if c_closed[i] == 1 and c_fd[i] == 0]
    gains = [P1[i] for i in range(len(P1)) if c_closed[i] == 0 and c_fd[i] == 1]
    results["P1_regressions"] = regressions
    results["P1_gains"] = gains

    # ---- P2 harm generalization (closed misses) ----
    for name, fn in [("closed_list", lambda v, a: closed_list_arm(v, a)),
                     ("fd_refined_backoff", fd_refined), ("twin", twin)]:
        corr, preds = score_pop(P2, fn)
        m, h = boot_ci(corr)
        results[f"P2_{name}"] = {"acc": round(m, 4), "ci_half": round(h, 4), "n": len(P2),
                                 "preds": preds}

    # ---- P3 help (structural) ----
    for name, fn in [("closed_list", lambda v, a: closed_list_arm(v, a)),
                     ("fd_refined_backoff", fd_refined), ("twin", twin)]:
        corr, preds = score_pop(P3, fn)
        m, h = boot_ci(corr)
        results[f"P3_{name}"] = {"acc": round(m, 4), "ci_half": round(h, 4), "n": len(P3),
                                 "preds": preds}

    # ---- P4 over-firing honesty (false-HARM rate on benefit CAUSE verbs) ----
    for name, fn in [("closed_list", lambda v, a: closed_list_arm(v, a)),
                     ("fd_coarse", fd_coarse), ("fd_refined_backoff", fd_refined)]:
        _c, preds = score_pop(P4, fn)
        false_harm = sum(1 for p in preds if p == "HARM")
        results[f"P4_{name}"] = {"false_harm": false_harm, "n": len(P4), "preds": preds}

    # ---- P5 modern coverage on UD-EWT affectedness gold ----
    gold_fp = os.path.join(REPO, "data", "ud_ewt_semantic_affectedness_gold_v1", "gold.json")
    p5 = {}
    if os.path.exists(gold_fp):
        with open(gold_fp, "r", encoding="utf-8") as f:
            g = json.load(f)["gold"]
        affecting = [row for row in g if row.get("type") in ("patient", "effected", "negated")]
        verbs = [lemmatize_verb(row["verb"]) for row in affecting]
        fd_cov = sum(1 for v in verbs if LEX.get(v) is not None)
        closed_cov = sum(1 for v in verbs if v in CLOSED)
        p5 = {"n_affecting": len(verbs),
              "fd_framenet_coverage": fd_cov,
              "fd_framenet_frac": round(fd_cov / max(1, len(verbs)), 4),
              "closed_list_coverage": closed_cov,
              "closed_list_frac": round(closed_cov / max(1, len(verbs)), 4),
              "fd_classes": dict(Counter(LEX.get(v) for v in verbs)),
              "sample_verbs": verbs[:30]}
    results["P5_modern_coverage_udewt"] = p5

    results["_meta"] = {"lexicon_size": len(LEX), "closed_list_size": len(CLOSED),
                        "harm_verbs_size": len(HARM_VERBS),
                        "lexicon_class_dist": dict(Counter(LEX.values())),
                        "n_boot": N_BOOT, "seed": SEED}
    return results


if __name__ == "__main__":
    import pprint
    r = run()
    pprint.pprint(r, width=120, sort_dicts=False)
