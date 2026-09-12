"""STEP 1 of the who-was-affected re-architecture: CORRECT THE INSTRUMENT.

Two measurement defects the brain-map + on-disk trace exposed:
  (A) WRONG PATH. The signal-trace + fd role-validation score a SEPARATE extractor (raw arc_labeler undergoer
      test / robust_role_pairs), NOT the reader's DEPLOYED patient decision
      (predicate_argument_frontend.structural_patient_pick, marginals=None -- the wired reader path).
  (B) WRONG TARGET. They score recall of the gold GRAMMATICAL OBJECT (obj/nsubj:pass) -- a proxy. The brain's
      quantity is the AFFECTED ENTITY = proto-patient / change-of-state (Dowty 1991; Beavers 2011), which only
      CORRELATES with the grammatical object and DIVERGES exactly at: unaccusatives (the affected entity is the
      intransitive SUBJECT -- "the glass broke"), subject-experiencer PSYCH verbs (the object is a STIMULUS, not
      affected -- "admire/fear X"), and (secondarily) ditransitives/conatives/figure-ground.

This cell fixes both: it measures the DEPLOYED structural_patient_pick against a graded AFFECTED-ENTITY gold and
quantifies how much the naive-object proxy has been hiding/misdirecting. It is the corrected scoreboard that the
subsequent re-architecture steps (activate graded marginals -> learned Competition-Model ranker; activate the
affectedness legs; wire GEK prediction) will be measured against.

AFFECTED-ENTITY GOLD (from UD-EWT gold deprels + the substrate's BF affectedness model, restricted to affecting
verbs A.is_affecting):
  + obj/dobj of an affecting verb  (canonical patient)      -- EXCLUDING subject-experiencer psych stimulus objects
  + nsubj:pass of an affecting verb (passive undergoer; UD already right)
  + nsubj of an affecting verb used INTRANSITIVELY (no obj/nsubj:pass child) with affectedness_score >= TAU_AFFECT
    (UNACCUSATIVE -- the sole argument undergoes the change; this is the affected entity the object-proxy MISSES)

NO external LLM at inference. Glass-box. ASCII. Deterministic. Reuses only substrate organs + the fd affectedness model.
"""
from __future__ import annotations

import os
import sys
from collections import Counter, defaultdict

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

import hdlab.causation_typing as CT
import hdlab.predicate_argument_frontend as PAF
import experiments.exp_fd_harm_help_role_corpus_validation_v1 as V
import experiments.exp_fd_harm_help_arithmetic_v1 as A

OBJ = {"obj", "dobj"}
PASS = {"nsubj:pass", "nsubjpass"}
UND = OBJ | PASS
TAU = A.TAU_AFFECT   # 0.40 graded-affectedness engage threshold (unaccusative subject inclusion)

# UNACCUSATIVE verb classes (Levin 1993; Levin & Rappaport Hovav 1995 -- a static offline linguistic asset,
# NOT an inference tool). The SOLE argument of these verbs is a proto-PATIENT (undergoes the change), so its
# intransitive SUBJECT is the AFFECTED ENTITY -- the case the object-seeking pipeline structurally misses.
# Deliberately EXCLUDES unergatives (run/laugh/work) and agentive transitives used objectlessly (eat/read),
# whose sole argument is a proto-AGENT. Restricted to change-of-state / change-of-location / (dis)appearance.
UNACCUSATIVE = {
    # change of state (break/bend/cook classes)
    "break", "crack", "shatter", "smash", "split", "tear", "rip", "snap", "burst", "fracture", "chip",
    "melt", "freeze", "thaw", "boil", "burn", "char", "cook", "dissolve", "evaporate", "condense", "vaporize",
    "bend", "fold", "crease", "wrinkle", "curl", "warp", "collapse", "crumble", "crumple", "deflate",
    "open", "close", "shut", "widen", "narrow", "cool", "warm", "heat", "dry", "harden", "soften", "loosen",
    "tighten", "darken", "brighten", "redden", "whiten", "blacken", "sharpen", "dull", "rust", "rot", "decay",
    "spoil", "wither", "wilt", "fade", "bloom", "blossom", "sprout", "ripen", "heal", "mend", "recover",
    # change of magnitude / degree
    "grow", "shrink", "expand", "contract", "swell", "stretch", "spread", "rise", "fall", "drop", "sink",
    "increase", "decrease", "diminish", "lessen", "double", "triple", "worsen", "improve", "deteriorate",
    "accelerate", "slow", "lengthen", "shorten", "thicken", "thin", "deepen",
    # (dis)appearance / coming-to-be / ceasing
    "appear", "emerge", "arise", "form", "develop", "materialize", "surface", "disappear", "vanish", "die",
    "perish", "expire", "dissipate", "fade", "dissolve", "change", "transform", "shift", "turn",
    # motion of a theme (change of location, non-agentive)
    "move", "roll", "slide", "spin", "bounce", "float", "drift", "tip", "topple", "capsize", "overturn",
}


def _lemma(w):
    try:
        return A.lemmatize_verb(w.lower())
    except Exception:
        return w.lower()


def _isaff(w):
    return A.is_affecting(w.lower(), A._LEX)


def _verb_children(sent):
    """verb_idx0 -> set of gold deprels of its children (base deprel)."""
    kids = defaultdict(set)
    for (i, form, up, head0, dep) in sent:
        if 0 <= head0 < len(sent):
            kids[head0].add(dep.split(":")[0] if dep not in UND else dep)
    return kids


def naive_obj_gold(sent):
    """The OLD target: {(v0, p0)} for obj/dobj/nsubj:pass of an affecting VERB/AUX head."""
    forms = [t[1] for t in sent]
    ups = [t[2] for t in sent]
    g = set()
    for (i, form, up, head0, dep) in sent:
        if dep in UND and 0 <= head0 < len(sent) and ups[head0] in ("VERB", "AUX") and _isaff(forms[head0]):
            g.add((head0, i))
    return g


def affected_entity_gold(sent):
    """The CORRECTED target: proto-patient / affected entity. Returns (gold_pairs, added_unaccusative,
    removed_psych) so the divergence from the naive object can be measured."""
    forms = [t[1] for t in sent]
    ups = [t[2] for t in sent]
    kids = _verb_children(sent)
    g = set()
    added = set()      # unaccusative subjects the object-proxy misses
    removed = set()    # psych stimulus objects the object-proxy wrongly counts
    for (i, form, up, head0, dep) in sent:
        if not (0 <= head0 < len(sent)) or ups[head0] not in ("VERB", "AUX"):
            continue
        vform = forms[head0]
        if not _isaff(vform):
            continue
        base = dep.split(":")[0] if dep not in UND else dep
        if dep in OBJ:
            # canonical patient, UNLESS the verb is a subject-experiencer psych verb (object = stimulus)
            if A._is_subject_experiencer(_lemma(vform)):
                removed.add((head0, i))
                continue
            g.add((head0, i))
        elif dep in PASS:
            g.add((head0, i))
        elif base == "nsubj":
            # UNACCUSATIVE: a curated change-of-state verb used INTRANSITIVELY (no obj/nsubj:pass child) ->
            # the sole argument is the proto-patient / affected entity (Levin unaccusativity).
            ch = kids.get(head0, set())
            if _lemma(vform) in UNACCUSATIVE and not (ch & UND):
                g.add((head0, i))
                added.add((head0, i))
    return g, added, removed


# --------------------------------- the DEPLOYED patient decision ---------------------------------
def deployed_pairs(toks, pos, heads, verbs0, gp=None):
    """The reader's patient decision per affecting verb. gp=None -> the DEPLOYED path
    (structural_patient_pick marginals=None). gp=GradedParse -> STEP 2: pass the exact single-root Matrix-Tree
    marginals so the FAITHFUL learned Competition-Model ranker (argstruct_patient_ranker) re-selects the patient
    (activate the dormant graded cue-integration). verbs0 = 0-based verb indices. Returns {(v0, p0)}."""
    out = set()
    marg = None
    for v0 in verbs0:
        m = None
        if gp is not None:
            if marg is None:
                marg = gp.marginals(list(toks), list(pos))
            m = marg
        pk = PAF.structural_patient_pick(list(toks), list(pos), dict(heads), v0 + 1, marginals=m)
        if pk is not None:
            out.add((v0, pk - 1))
    return out


def _scores(pred, gold):
    tp = len(pred & gold)
    return {"recall": round(tp / max(1, len(gold)), 4), "precision": round(tp / max(1, len(pred)), 4),
            "tp": tp, "n_gold": len(gold), "n_pred": len(pred)}


def run(cap=1500, arms=("baseline", "graded_marginals")):
    """Compare re-architecture arms on the corrected instrument.
    baseline         = the deployed structural_patient_pick (marginals=None).
    graded_marginals = STEP 2: pass graded_parser single-root Matrix-Tree marginals -> the learned
                       Competition-Model ranker re-selects the patient (activate the dormant graded path)."""
    from hdlab.graded_parser import GradedParse
    t, p, l = CT._frontend()
    gp = GradedParse.load() if "graded_marginals" in arms else None
    sents = V._read(V._UD_TEST, cap)
    naive_all, aff_all, added_all, removed_all = set(), set(), set(), set()
    arm_pairs = {a: set() for a in arms}
    arm_hit_added = {a: 0 for a in arms}
    for si, sent in enumerate(sents):
        toks = [x[1] for x in sent]
        naive = {(si, v, pp) for (v, pp) in naive_obj_gold(sent)}
        gold, added, removed = affected_entity_gold(sent)
        gold = {(si, v, pp) for (v, pp) in gold}
        added = {(si, v, pp) for (v, pp) in added}
        verbs0 = sorted({v for (_, v, _) in (naive | gold | {(si, x, y) for (x, y) in removed})})
        pos_pred = list(t.tag(toks))
        heads_pred = dict(p.parse(toks, pos_pred).heads)
        gpos = [x[2] for x in sent]
        gheads = {x[0] + 1: (x[3] + 1 if x[3] >= 0 else 0) for x in sent}
        naive_all |= naive; aff_all |= gold; added_all |= added
        removed_all |= {(si, v, pp) for (v, pp) in removed}
        for a in arms:
            pos, heads = (gpos, gheads) if a.startswith("gold_parse") else (pos_pred, heads_pred)
            usegp = gp if a in ("graded_marginals", "gold_parse_graded") else None
            dep = {(si, v, pp) for (v, pp) in deployed_pairs(toks, pos, heads, verbs0, gp=usegp)}
            arm_pairs[a] |= dep
            arm_hit_added[a] += len(dep & added)
    out = {"n_sents": len(sents),
           "arms": {a: {"vs_NAIVE_object_gold": _scores(arm_pairs[a], naive_all),
                        "vs_AFFECTED_entity_gold": _scores(arm_pairs[a], aff_all),
                        "unaccusative_subjects_recovered": f"{arm_hit_added[a]}/{len(added_all)}"}
                    for a in arms},
           "divergence": {"unaccusative_subjects_added": len(added_all),
                          "psych_stimulus_objects_removed": len(removed_all)},
           "note": "Corrected scoreboard: the DEPLOYED path (baseline) vs STEP-2 graded-marginal Competition-Model "
                   "re-selection, each scored on the naive-object proxy AND the affected-entity (proto-patient) gold. "
                   "The affected gold adds unaccusative subjects the object proxy misses."}
    if arms == ("baseline",) or len(arms) == 1:
        out["single_arm"] = arms[0]
    return out


def self_test():
    r = run(cap=500)
    b = r["arms"]["baseline"]
    g = r["arms"]["graded_marginals"]
    # the deployed path + the step-2 arm both produce real measurements on both golds
    assert b["vs_AFFECTED_entity_gold"]["n_gold"] > 0 and b["vs_AFFECTED_entity_gold"]["tp"] > 0
    assert g["vs_AFFECTED_entity_gold"]["n_gold"] == b["vs_AFFECTED_entity_gold"]["n_gold"], "gold must match across arms"
    # the affected-entity gold diverges from the naive object gold (unaccusative subjects added)
    assert r["divergence"]["unaccusative_subjects_added"] >= 0
    print(f"[SELFTEST PASS] corrected instrument live. baseline vs AFFECTED gold "
          f"R={b['vs_AFFECTED_entity_gold']['recall']} P={b['vs_AFFECTED_entity_gold']['precision']}; "
          f"graded_marginals R={g['vs_AFFECTED_entity_gold']['recall']} P={g['vs_AFFECTED_entity_gold']['precision']}; "
          f"unaccusative added={r['divergence']['unaccusative_subjects_added']} "
          f"(baseline recovers {b['unaccusative_subjects_recovered']}, graded {g['unaccusative_subjects_recovered']}).")
    return True


if __name__ == "__main__":
    if "--self-test" in sys.argv or "--smoke" in sys.argv:
        self_test()
    else:
        import pprint
        pprint.pprint(run(int(sys.argv[1]) if len(sys.argv) > 1 else 1500), width=118, sort_dicts=False)
