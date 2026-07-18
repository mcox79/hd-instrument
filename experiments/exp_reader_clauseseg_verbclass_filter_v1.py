"""
CLAUSE-SEG VERB-CLASS FILTER (the precision lever the topical-animate cell localized). Completes the
clause-seg parser component on PRECISION: on top of the VET-recomputed topical-animate held subject
(reader_clauseseg_topical_animate_subject_v2; VET-pending), gate the held-subject injection by the
COORDINATED clause's VERB CLASS. Restrict injection to verbs that assert a REAL event with a GENUINE
DIRECT OBJECT (transitive factive); SUPPRESS injection into NON-FACTIVE / mental-state / irrealis verbs
(wished, thought, hoped, believed, wanted, seemed ...) and verbs with no genuine direct object.

WHY (localized by VET of the topical-animate cell v2, metrics PARTIAL_PRECISION_STUCK):
  v2 topical-animate RECOVERS composition (CMP 0.333->0.667) + orphaned-relation recall (RELF1-recall
  0.800->0.933) to the gold ceiling AND fixes the STALE-INANIMATE held-subject source (inanimate_overfire
  1->0, "time"->"george"). BUT strict precision 0.4762 < orphan-floor 0.5143 < gold 0.5263 -- STILL below
  the do-nothing floor. The VET decomposed the residual: the excess FPs are SUBJECT-INDEPENDENT. Even with
  the CORRECT animate "george"/"susie" held, two coordinated conjuncts emit junk svo:
    L34_geo2 "wished for a cool place ..." -> svo(wished,george,{cool,place,dinner})   [3 FP]
    L67_susie2 "thought she would eat her lunch" -> svo(thought,susie,lunch)           [1 FP]
  These verbs are NON-FACTIVE / mental-state: "wished for a cool place" asserts no real event on "place";
  "thought [she would eat]" takes a sentential complement, not a direct object. The precision gap is a
  VERB-CLASS problem, NOT the held subject. MEASURED delta topical fp=22 vs gold fp=18 = EXACTLY these 4.

MECHANISM (ONE variable vs v2 = the verb-class filter on the injection; everything else byte-identical):
  learned_topical           : v2 -- inject held topical-animate subject at every COORD-boundary bare-VP
                              [BASELINE -- the arm to improve on precision]
  learned_topical_verbfilter: SAME held topical-animate subject, but INJECT ONLY IF the coordinated
                              clause's main verb is TRANSITIVE + FACTIVE:
                                (a) verb-class feature: main-verb lemma NOT in a transparent NON-FACTIVE /
                                    mental-state / irrealis set (wish/think/hope/believe/want/seem/...), AND
                                (b) transitivity feature: the clause has a GENUINE DIRECT OBJECT -- a noun
                                    the verb directly governs, NOT prep-governed ("wished FOR a place") and
                                    NOT a sentential-complement subject ("thought SHE would ...").
                              Injection is SUPPRESSED when EITHER (a) or (b) fails (i.e. inject iff factive
                              AND has-direct-object). No propagation -> those conjuncts fall back to the
                              do-nothing (orphan) behavior, emitting no svo.
  Boundaries + coref + role + cheap wins + the held-subject SOURCE are all IDENTICAL to v2; the ONLY new
  behavior is the verb-class gate on whether to inject at a COORD bare-VP site.

TWO INDEPENDENT GLASS-BOX FEATURES (anti-overfit): the verb-class LIST catches wished/thought as non-
  factive; the STRUCTURAL direct-object parse ALSO suppresses both (wished: first post-verb token is the
  preposition "for"; thought: first post-verb token is the nominative subject pronoun "she" + modal, a
  sentential complement) and KEEPS both event verbs (put->strawberry, killed->sheep: genuine direct
  objects). Two orthogonal signals agree, so the localization is not merely a 2-verb lookup. HONEST caveat:
  on this 5-passage corpus only 2 non-factive verbs occur, so the corpus alone cannot distinguish a
  correct GENERAL class from a list tuned to these two; the structural feature is the generalization guard.

ARMS:
  envelope_floor            : cheap wins OFF, seg=orphan            [POSITIVE CONTROL -> envelope 3rd store]
  handrule_orphan           : cheap wins ON,  seg=orphan            [FLOOR (no recovery); precision 0.5143]
  learned_lastactive        : cheap wins ON,  seg=learned_lastactive [v1 reference: recovery, prec below floor]
  learned_topical           : cheap wins ON,  seg=learned_topical    [v2 BASELINE: recovery, prec 0.4762 < floor]
  learned_topical_verbfilter: cheap wins ON,  seg=verbfilter         [MECHANISM: + verb-class filter]
  gold_clauseseg            : cheap wins ON,  seg=gold               [CEILING = oracle INJECT_SUBJ; prec 0.5263]

MEASURE per arm: RELF1 micro P/R/F1, comprehension all/NC/CO/CMP, ref_acc, strict PRECISION + fp/tp/
  extracted, N5-relation (svo killed wolf sheep) + N5 answer. Verb-filter telemetry: per COORD bare-VP
  site the decision (verb, non_factive?, has_direct_object?, admit?); count of non-factive FP relations
  SUPPRESSED (present in v2 topical, absent in verbfilter); the verbfilter-vs-topical injection delta;
  whether verbfilter's store coincides with the gold-oracle store (glass-box rediscovers the oracle).

REGRESSION GUARD (the verb-class gate must not break the VET-confirmed controls):
  - ORC.score_passive(role_fixed) == 1.00 and ORC.score_reversal(role_fixed) == 1.00.
  - ref_acc IDENTICAL across all arms (the filter must not move coref).
  - the packaged state-of-mind overlay witness (verification/verify_state_of_mind_overlay.py) exits 0.
  - baseline arms (orphan/lastactive/topical/gold) run through V2.run_arm VERBATIM -> reproduce v2 exactly.

BRANCHES (decisive, genuinely can-fail):
  CLAUSE_SEG_PRECISION_CLEAN = verbfilter RESTORES strict precision to >= orphan floor (ideally to the gold
                               ceiling) by suppressing the non-factive FPs, WHILE KEEPING the recovery (N5
                               relation + CMP & RELF1-recall at the gold ceiling) AND no control regression
                               AND the suppressed sites are exactly the non-factive / no-direct-object
                               verbs -> the CLEAN clause-seg component (composition + recall recovery AND
                               precision non-regressing) = fold-ready first parser component; the non-
                               factive-verb localization CONFIRMED. NP-head + argument-structure remain next.
  PARTIAL_LOST_RECOVERY      = the filter OVER-suppressed (killed/put mis-classified as non-factive or as
                               no-direct-object) -> lost N5 / CMP / recall -> localize + DEFLATE.
  PARTIAL_PRECISION_STUCK    = the filter kept recovery but precision still < floor (some residual FPs are
                               NOT non-factive-verb injections -> localization refined again) -> DEFLATE.
  REGRESSION                 = a control regressed -> revert + localize.
  INVALID_POSITIVE_CONTROL_FAIL = envelope_floor / gold ceiling / v2 baseline do not reproduce.

FAIRNESS / anti-circular (design-gate; USER: fair tests every time):
  - Same REAL grade-3 McGuffey passages + INDEPENDENT gold, imported VERBATIM from the envelope cell.
  - COMPLETE_TRUTH (precision eval) + INJECT_SUBJ (gold ceiling) reused verbatim from the oracle cell.
  - baseline arms run through V2.run_arm VERBATIM; verbfilter extract byte-reproduces V2.extract_passage_cs
    on the orphan/gold/lastactive/topical modes (anti-copy-divergence) -> the ONLY new behavior is the gate.
  - REAL baseline = learned_topical (v2: recovery-but-precision-below-floor), a REAL arm, not a strawman.
  - ONE variable across topical vs verbfilter = the verb-class filter (on/off). Discriminator CAN-FAIL
    (over-suppress -> lose recovery; under-suppress -> precision stuck). Difficulty ON (real FPs at floor).
  - Determinism OMP=1, fixed seed, sorted(set). No hash()-seeded randomness (no randomness at all).

Glass-box (POS + averaged perceptron + a transparent non-factive verb-class set + a POS-based direct-object
parse; NO external LLM; NO torch/GPU at runtime). Local / foreground-to-completion. NO push / NO remote-
persist. CLAIM-VET-pending (NOT self-declared chain-grade); strategic read = hypothesis pending landed-VET.

ANCHOR: reader_clauseseg_verbclass_filter_v1
BASELINE: v2 topical-animate clause-seg (reader_clauseseg_topical_animate_subject_v2, PARTIAL_PRECISION_STUCK)
+ v1 clause-seg unlock (775c6085c; VET acc75e96) + cheap wins (VET a5ef7435) + gold clause-seg ceiling
(oracle b85422616; VET a220d138) + envelope 3rd store (00c6688b6; VET a7ecb244). COMPUTE: sequential-CPU;
wall < 120s.

CELL-TEMPLATE MANDATES (relevant subset; many SCHEMA-VET gates N/A for this non-HD, no-KG cell-type):
# - except SystemExit/KeyboardInterrupt: raise BEFORE except Exception (no BaseException)
# - ATOMIC final metrics write (tmp + os.replace)                        [META_RULE_AH: tmp_replace]
# - ARMS-MUST-DIFFER hash check at gate (mechanism must differ from v2 topical AND from floor; the
#   verbfilter==gold coincidence is a real STRONG-PASS outcome -> exempted pair reported as telemetry) [AF]
# - discriminator CAN-FAIL (over-suppress -> lose recovery / under-suppress -> precision stuck / regress)
# - POSITIVE-CONTROL: envelope_floor reproduces envelope 3rd store + v2 baseline reproduces [reproduce/Gate D]
# - anti-copy-divergence: extract_vf(orphan|gold|lastactive|topical) == V2.extract_passage_cs byte-id  [F.1]
# - deterministic seeding (fixed int seed, fixed order, sorted set; NO randomness)             [F.5/PROT-023]
# - real_code_path: self-test CONSTRUCTS + EXERCISES the REAL perceptron + POS tagger + overlay animacy +
#   the REAL verb-class parse on REAL 3rd-reader passages; runs the REAL passive/reversal + overlay witness [F.1]
# - start-marker + crash-diagnostic; heartbeat EXEMPT (wall < 120s)
# - all reported numbers MEASURED@this metrics.json; floor/v1/v2 CITED@their metrics.json
# - N/A: KGStore (no KG); N/A cardinality sweep-axis; N/A CRLB (no HD noise floor); N/A multi-seed
"""
import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import re
import sys
import json
import time
import argparse
import hashlib
import platform
import traceback
from datetime import datetime, timezone

_THIS = os.path.abspath(__file__)
REPO = os.path.dirname(os.path.dirname(_THIS))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

# Reuse the WHOLE v2 topical-animate machinery VERBATIM: the REAL passages/gold, the independent
# COMPLETE_TRUTH, the cheap wins, the gold clause-seg ceiling, the segmenter/bare-VP/topical-head helpers,
# telemetry, controls, markers. The baseline arms run through V2.run_arm -> byte-identical to v2.
from experiments import exp_oracle_mention_upperbound_reader_v1 as ORC          # noqa: E402
from experiments import exp_reader_clauseseg_topical_animate_subject_v2 as V2   # noqa: E402

# Bind v2 helpers used by the new extract (identical semantics; the ONLY new code is the verb-class gate).
segment_clauses_with_boundaries = V2.segment_clauses_with_boundaries
_is_bare_vp = V2._is_bare_vp
_topical_animate_head = V2._topical_animate_head
INJECT_SUBJ = V2.INJECT_SUBJ
_prefers_topical = V2._prefers_topical
_agreement_attrs = V2._agreement_attrs
_RESOLVABLE = V2._RESOLVABLE
_RESOLVABLE_SO = V2._RESOLVABLE_SO
_RESOLVABLE_POSS = V2._RESOLVABLE_POSS
apply_role_fix = V2.apply_role_fix
is_self_loop = V2.is_self_loop
G3_PASSAGES = V2.G3_PASSAGES
G3_GOLD_ANTECEDENTS = V2.G3_GOLD_ANTECEDENTS
G3_QS = V2.G3_QS
N5_PID = V2.N5_PID
N5_REL = V2.N5_REL
FLOOR = V2.FLOOR
SEED = V2.SEED
SetKnownBase = V2.SetKnownBase
WorkingOverlay = V2.WorkingOverlay
PRONOUN_SCOPE = V2.PRONOUN_SCOPE

ANCHOR_NAME = "reader_clauseseg_verbclass_filter_v1"
OUTPUT_DIR = os.path.join(REPO, "data", "exp_" + ANCHOR_NAME)

# CITED reference precisions (all MEASURED@ their own metrics.json; restated here for the bands).
V2_TOPICAL_PREC = 0.4762     # CITED@data/exp_reader_clauseseg_topical_animate_subject_v2/metrics.json
ORPHAN_FLOOR_PREC = 0.5143   # CITED@ same (handrule_orphan strict precision)
GOLD_CEILING_PREC = 0.5263   # CITED@ same (gold ceiling strict precision)

# Pre-registered bands (HYPOTHESIZED@this cell; set BEFORE the run; can-fail).
PREC_RESTORE_TOL = 0.005     # verbfilter strict precision >= orphan floor - 0.005 (restored/non-regressing)
CMP_CEILING_TOL = 1e-6
RECALL_CEILING_TOL = 1e-6
PASSIVE_FLOOR = 1.0
REVERSAL_FLOOR = 1.0

_COORD_WORDS = {"and", "but", "or"}
_LEARNED_MODES = ("learned_lastactive", "learned_topical")
_VF_MODE = "learned_topical_verbfilter"
_ALL_LEARNED_MODES = _LEARNED_MODES + (_VF_MODE,)


# =======================================================================================
# GLASS-BOX VERB-CLASS FILTER: transitive-factive test on the coordinated clause's main verb.
# =======================================================================================
# (a) NON-FACTIVE / mental-state / irrealis verb class: verbs that do NOT assert a real event on a direct
#     object (attitude / cognition / desire / appearance). Built from transparent base lemmas + regular
#     inflection + a small irregular-past map, so the membership test is on the surface form the tagger
#     returns and generalizes to unseen inflections of the listed verbs.
_NON_FACTIVE_BASE = frozenset({
    "wish", "think", "hope", "believe", "want", "seem", "wonder", "fear", "expect", "suppose",
    "imagine", "feel", "guess", "doubt", "dream", "pretend", "decide", "plan", "intend", "desire",
    "consider", "assume", "suspect", "presume", "prefer", "mean", "know", "hear",  # cognition/attitude
    "appear", "look", "wait", "long", "care", "worry", "remember", "forget", "realize", "notice",
})
_IRREGULAR_INFLECT = {
    "think": ("thought",), "know": ("knew", "known"), "feel": ("felt",), "mean": ("meant",),
    "dream": ("dreamt",), "hear": ("heard",), "forget": ("forgot", "forgotten"),
}


def _inflect(base):
    """Regular + irregular surface forms for one base lemma (glass-box, deterministic)."""
    forms = {base, base + "s"}
    if base.endswith("e"):
        forms.add(base + "d")           # believe->believed, desire->desired
        forms.add(base[:-1] + "ing")    # believe->believing
        forms.add(base[:-1] + "es")     # (rare) -- harmless superset
    else:
        forms.add(base + "ed")          # wish->wished, want->wanted
        forms.add(base + "ing")         # wish->wishing
    forms.update(_IRREGULAR_INFLECT.get(base, ()))
    return forms


_NON_FACTIVE_SURFACE = frozenset().union(*(_inflect(b) for b in _NON_FACTIVE_BASE))

# (b) direct-object parse helpers.
_PREPS = frozenset({"for", "at", "to", "with", "about", "of", "on", "in", "into", "over", "from",
                    "toward", "towards", "upon", "after", "around", "through"})
_COMPLEMENTIZERS = frozenset({"that", "whether", "if", "how", "why", "what", "where", "when", "who"})
_SUBJ_PRON = frozenset({"he", "she", "they", "i", "we", "who"})   # nominative -> embedded-clause subject
_OBJ_PRON = frozenset({"him", "her", "them", "it", "me", "us"})   # accusative -> possible direct object
_OBJ_NOUN_POS = ("NN", "NNS", "NNP", "NNPS")


def _has_genuine_direct_object(tagged, vi):
    """True iff the main verb at index vi directly governs a noun object -- i.e. the first CONTENT token
    after the verb is a direct-object noun/accusative-pronoun, NOT a preposition (prep-governed NP), NOT a
    complementizer, and NOT a nominative subject pronoun / modal (sentential complement)."""
    for j in range(vi + 1, len(tagged)):
        _surf, low, pos = tagged[j]
        if pos == "IN" or low in _PREPS or low in _COMPLEMENTIZERS:
            return False               # "wished FOR a place ..." / "... THAT ..." -> prep/comp-governed
        if low in _SUBJ_PRON:
            return False               # "thought SHE would ..." -> embedded-clause subject
        if pos == "MD":
            return False               # modal before any object noun -> sentential complement
        if low in _OBJ_PRON or pos in _OBJ_NOUN_POS or ORC.ground_category(low) is not None:
            return True                # first content after verb is a governed object noun
        # DT / JJ / RB / CC / PRP$ / WRB / CD etc. -> determiners/adjs/adverbs; keep scanning
    return False


def verb_admits_injection(tagged):
    """Inject the held subject iff the coordinated clause's main verb is TRANSITIVE + FACTIVE.
    Returns (admit: bool, decision: dict) -- decision carries glass-box telemetry."""
    vi, surf, _p = ORC.find_main_verb(tagged)
    if vi is None:
        return False, dict(verb=None, non_factive=None, has_direct_object=None, admit=False,
                           reason="no_main_verb")
    verb_surf = surf.lower() if isinstance(surf, str) else str(surf)
    non_factive = verb_surf in _NON_FACTIVE_SURFACE
    has_do = _has_genuine_direct_object(tagged, vi)
    admit = (not non_factive) and has_do
    reason = "admit" if admit else ("non_factive_verb" if non_factive else "no_direct_object")
    return admit, dict(verb=verb_surf, non_factive=non_factive, has_direct_object=has_do,
                       admit=admit, reason=reason)


# =======================================================================================
# Extract: byte-COPY of V2.extract_passage_cs with ONE added mode (learned_topical_verbfilter).
# For orphan/gold/lastactive/topical it is byte-identical to V2.extract_passage_cs (asserted in self-test).
# The optional decisions_out list, when provided, records the per-site verb-class decisions (verbfilter
# runs only) WITHOUT changing the 4-tuple return -> anti-copy-divergence comparison stays exact.
# =======================================================================================
def extract_passage_vf(passage_text, clf, pid, passages_dict, mention_mode, clause_seg,
                       role_fix, self_loop_guard, decisions_out=None):
    """Returns (sorted_rels, res_by_pos, removed_self_loops, injections)."""
    coref_strategy = ORC.FIXED_COREF_STRATEGY
    fix_possessive = True
    agreement = True
    topical = True
    pref = bool(agreement)
    injects = INJECT_SUBJ.get(pid, {}) if clause_seg == "gold" else {}
    bounds = segment_clauses_with_boundaries(passage_text) if clause_seg in _ALL_LEARNED_MODES else None

    known = set()
    for txt in list(passages_dict.values()):
        for s in ORC.split_sentences(txt):
            for _su, lo, _po in ORC.pos_tag_sentence(s):
                if ORC.ground_category(lo) is not None:
                    known.add(lo)
    ov = WorkingOverlay(base=SetKnownBase(known))

    rels = []
    res_by_pos = {}
    injections = []
    active_subject = None
    offset = 0
    for ci, sent in enumerate(ORC.split_sentences(passage_text)):
        tagged = ORC.pos_tag_sentence(sent)
        subj = None
        if clause_seg == "gold":
            subj = injects.get(sent.strip())
        elif clause_seg == "learned_lastactive":
            kind = bounds[ci][1]
            if kind == "COORD" and active_subject is not None and _is_bare_vp(tagged):
                subj = active_subject
        elif clause_seg == "learned_topical":
            kind = bounds[ci][1]
            if kind == "COORD" and _is_bare_vp(tagged):
                held = _topical_animate_head(ov)
                if held is not None:
                    subj = held
        elif clause_seg == _VF_MODE:
            kind = bounds[ci][1]
            if kind == "COORD" and _is_bare_vp(tagged):
                held = _topical_animate_head(ov)
                if held is not None:
                    admit, dec = verb_admits_injection(tagged)
                    if decisions_out is not None:
                        decisions_out.append(dict(pid=pid, clause=sent.strip(), held=held, **dec))
                    if admit:
                        subj = held
        if subj is not None:
            tagged = [(subj.capitalize(), subj, "NNP")] + tagged
            injections.append((pid, sent.strip(), subj))
        pron_res = {}
        for i, (surf, low, pos) in enumerate(tagged):
            if low in PRONOUN_SCOPE:
                if low not in ("i", "you", "we"):
                    ptop = _prefers_topical(low, pos) if topical else False
                    ent = ov.resolve_pronoun(low, strategy=coref_strategy,
                                             prefer_agreement=pref, prefer_topical=ptop)
                    pron_res[i] = ent.head if ent is not None else None
                sc = PRONOUN_SCOPE[low]
                ov.observe(low, is_pronoun=True, gender=sc["gender"], number=sc["number"])
            elif low in ORC.PRONOUNS_POSS:
                pass
            else:
                if not ORC.observe_as_mention(low, pos, mention_mode, frozenset()):
                    continue
                is_name = (low in ORC.NAME_GENDER) or (pos in ("NNP", "NNPS"))
                if agreement:
                    g, num, anim = _agreement_attrs(low, pos, is_name)
                    ov.observe(low, gender=g, number=num, is_proper_name=is_name, animacy=anim)
                else:
                    g, num = ORC.grounded_gender_number(low, is_name)
                    ov.observe(low, gender=g, number=num, is_proper_name=is_name)

        roles, verb_idx, verb, passive, cand = ORC.assign_roles_learned(
            tagged, clf, mention_mode, frozenset())
        if role_fix:
            roles = apply_role_fix(tagged, roles, verb_idx, cand)

        def head_of(i):
            surf, low, pos = tagged[i]
            if i in pron_res and pron_res[i] is not None:
                return pron_res[i]
            return low

        agents = [i for i in cand if roles.get(i) == "AGENT"]
        patients = [i for i in cand if roles.get(i) == "PATIENT"]
        recips = [i for i in cand if roles.get(i) == "RECIPIENT"]
        locs = [i for i in cand if roles.get(i) == "LOCATION"]
        subj_head = head_of(agents[0]) if agents else (head_of(cand[0]) if cand else None)
        if verb is not None and agents and patients and verb not in ("has", "is"):
            for pi in patients:
                rels.append(("svo", verb, head_of(agents[0]), head_of(pi)))
        lows = [t[1] for t in tagged]
        if "kind" in lows and subj_head is not None:
            for i in cand:
                if roles.get(i) in ("PATIENT", "RECIPIENT", "LOCATION") or ORC.prev_prep(tagged, i) == "to":
                    if head_of(i) != subj_head:
                        rels.append(("svo", "kind", subj_head, head_of(i)))
        if verb == "has" and patients:
            pre_verb = [i for i in cand if verb_idx is not None and i < verb_idx]
            owner_idx = agents[0] if agents else (pre_verb[0] if pre_verb else None)
            if owner_idx is not None:
                for pi in patients:
                    if pi != owner_idx:
                        rels.append(("poss", head_of(owner_idx), head_of(pi)))
        for ri in recips:
            if verb is not None and agents:
                rels.append(("recipient", verb, head_of(agents[0]), head_of(ri)))
        for li in locs:
            figure = subj_head
            for j in cand:
                if j < li and roles.get(j) in ("AGENT", "PATIENT"):
                    figure = head_of(j)
            if figure is not None and figure != head_of(li):
                rels.append(("loc", figure, head_of(li)))

        for i, (surf, low, pos) in enumerate(tagged):
            if "'" in surf and (surf.lower().endswith("'s")):
                owner = surf.split("'")[0].lower()
                for j in range(i + 1, len(tagged)):
                    if j in cand:
                        rels.append(("poss", owner, head_of(j)))
                        break
            if low in ORC.PRONOUNS_POSS:
                if fix_possessive and low in PRONOUN_SCOPE and low not in ("i", "you", "we"):
                    owner = pron_res.get(i)
                    owner = owner if owner is not None else low
                elif low in PRONOUN_SCOPE and low not in ("i", "you", "we"):
                    ptop = _prefers_topical(low, pos) if topical else False
                    ent = ov.resolve_pronoun(low, strategy=coref_strategy,
                                             prefer_agreement=pref, prefer_topical=ptop)
                    owner = ent.head if ent is not None else low
                else:
                    owner = low
                for j in range(i + 1, len(tagged)):
                    if j in cand:
                        rels.append(("poss", owner, head_of(j)))
                        break
                if low in _RESOLVABLE:
                    res_by_pos[offset + i] = (low, owner if owner != low else None)
        for i in range(len(tagged) - 1):
            if ORC.ground_category(tagged[i][1]) == "COLOR":
                for j in range(i + 1, len(tagged)):
                    if j in cand:
                        rels.append(("attr", head_of(j), tagged[i][1], "COLOR"))
                        break

        for i, (surf, low, pos) in enumerate(tagged):
            if low in _RESOLVABLE_SO and low not in _RESOLVABLE_POSS:
                res_by_pos[offset + i] = (low, pron_res.get(i))

        if agents:
            active_subject = head_of(agents[0])

        offset += len(tagged)

    removed = []
    if self_loop_guard:
        kept = []
        for r in rels:
            if is_self_loop(r):
                removed.append(tuple(r))
            else:
                kept.append(r)
        rels = kept

    sorted_rels = sorted(set(rels), key=lambda r: (r[0], tuple(str(x) for x in r[1:])))
    removed = sorted(set(removed), key=lambda r: (r[0], tuple(str(x) for x in r[1:])))
    return sorted_rels, res_by_pos, removed, injections


# =======================================================================================
# Run the verbfilter arm through MY extract (baseline arms run through V2.run_arm verbatim).
# =======================================================================================
def run_arm_vf(clf, clause_seg, role_fix, self_loop_guard):
    store, res_by_pos, injections = {}, {}, []
    decisions = []
    for pid, text in G3_PASSAGES.items():
        rels, rbp, _rem, inj = extract_passage_vf(text, clf, pid, G3_PASSAGES, "handrule",
                                                  clause_seg, role_fix, self_loop_guard,
                                                  decisions_out=decisions)
        store[pid] = rels
        res_by_pos[pid] = rbp
        injections.extend(inj)
    correct, answers = [], []
    for q in G3_QS:
        ans = ORC.answer_reader(q["spec"], store[q["p"]])
        na, ng = ORC.normalize(ans), ORC.normalize(q["gold"])
        correct.append(1 if (na is not None and na == ng) else 0)
        answers.append(na)
    relf1 = V2.ENV._relf1_g3(store)
    slices = V2.ENV._slices_g3(correct)
    n_tot = n_ok = 0
    for pid in G3_PASSAGES:
        gold = G3_GOLD_ANTECEDENTS.get(pid, [])
        pred_sorted = [res_by_pos[pid][k] for k in sorted(res_by_pos[pid].keys())]
        for gi, (g_surf, g_head) in enumerate(gold):
            p_surf, p_head = (pred_sorted[gi] if gi < len(pred_sorted) else (None, None))
            ok = (p_head is not None and ORC.normalize(p_head) == ORC.normalize(g_head))
            n_tot += 1
            n_ok += 1 if ok else 0
    ref_acc = (n_ok / n_tot) if n_tot else 0.0
    fnd = V2.ENV.build_foundation(store)
    strict = V2.ORA._strict_precision(store)
    n5_relation = tuple(N5_REL) in set(tuple(r) for r in store[N5_PID])
    n5_answer = None
    for i, q in enumerate(G3_QS):
        if q["qid"] == "N5":
            n5_answer = bool(correct[i])
            break
    return dict(store=store, correct=correct, answers=answers, relf1=relf1, slices=slices,
                ref_acc=round(ref_acc, 4), ref_ok=n_ok, ref_n=n_tot, foundation=fnd, strict=strict,
                n5_relation=n5_relation, n5_answer=n5_answer,
                injections=[list(x) for x in injections], vf_decisions=decisions,
                per_q=[dict(qid=q["qid"], slice=q["slice"], gold=q["gold"], pred=answers[i],
                            ok=bool(correct[i])) for i, q in enumerate(G3_QS)])


# =======================================================================================
# Verb-filter telemetry: what the filter suppressed vs the v2 topical arm.
# =======================================================================================
def _suppression_telemetry(vf_arm, topical_arm):
    """Which injections the verb-filter SUPPRESSED (present in v2 topical, gone in verbfilter) + the
    non-factive FP relations removed as a result."""
    tp_inj = {(pid, cl): subj for pid, cl, subj in topical_arm["injections"]}
    vf_inj = {(pid, cl): subj for pid, cl, subj in vf_arm["injections"]}
    suppressed = [[pid, cl, subj] for (pid, cl), subj in tp_inj.items() if (pid, cl) not in vf_inj]
    kept = [[pid, cl, subj] for (pid, cl), subj in vf_inj.items()]
    # FP relations present in v2 topical but absent in verbfilter (the FPs the filter removed).
    tp_fp = set(tuple(r) for r in topical_arm["strict"]["fp_relations"])
    vf_fp = set(tuple(r) for r in vf_arm["strict"]["fp_relations"])
    removed_fp = sorted(tp_fp - vf_fp)
    added_fp = sorted(vf_fp - tp_fp)   # should be empty; a non-empty set is a red flag
    # of the removed FPs, how many are svo whose verb is in the non-factive class?
    nonfactive_fp = [list(r) for r in removed_fp
                     if r and r[0] == "svo" and str(r[1]).lower() in _NON_FACTIVE_SURFACE]
    # decisions telemetry (each COORD bare-VP site the filter evaluated).
    decisions = vf_arm.get("vf_decisions", [])
    suppressed_decisions = [d for d in decisions if not d["admit"]]
    return dict(suppressed_injections=suppressed, kept_injections=kept,
                removed_fp_relations=removed_fp, added_fp_relations=added_fp,
                nonfactive_fp_relations=nonfactive_fp,
                n_suppressed=len(suppressed), n_removed_fp=len(removed_fp),
                n_nonfactive_fp_suppressed=len(nonfactive_fp),
                site_decisions=decisions, suppressed_decisions=suppressed_decisions,
                all_suppressed_are_nonfactive_or_no_do=all(
                    (not d["admit"]) and (d["non_factive"] or (d["has_direct_object"] is False))
                    for d in suppressed_decisions) if suppressed_decisions else True)


def _store_json(arm):
    return {p: [list(r) for r in arm["store"][p]] for p in G3_PASSAGES}


# =======================================================================================
# Markers / metrics / crash-diagnostic (atomic).
# =======================================================================================
def _write_start_marker(output_dir, run_mode, expected_n_units):
    marker = dict(pid=os.getpid(), ts_iso=datetime.now(timezone.utc).isoformat(),
                  anchor_name=ANCHOR_NAME, run_mode=run_mode,
                  expected_n_units=expected_n_units, host=platform.node())
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, os.path.join(output_dir, "_start_marker.json"))


def _write_metrics(output_dir, metrics):
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, os.path.join(output_dir, "metrics.json"))


def _write_crash_metrics(output_dir, exc):
    diag = dict(verdict="CELL_CRASHED", verdict_msg=f"{type(exc).__name__}: {str(exc)[:500]}",
                summary=f"CELL_CRASHED: {type(exc).__name__}", elapsed_s=0.0,
                traceback=traceback.format_exc()[:5000],
                ts_iso=datetime.now(timezone.utc).isoformat(), pid=os.getpid(),
                anchor_name=ANCHOR_NAME)
    _write_metrics(output_dir, diag)


def _arms_must_differ(named_outputs, exempt_pairs=frozenset()):
    digests = {}
    for name, out in named_outputs.items():
        b = json.dumps(out, sort_keys=True).encode("utf-8")
        digests[name] = hashlib.sha256(b).hexdigest()
    names = sorted(digests)
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            pair = tuple(sorted((names[i], names[j])))
            if pair in exempt_pairs:
                continue
            assert digests[names[i]] != digests[names[j]], \
                f"META_RULE_AF VIOLATION: arms {names[i]!r} and {names[j]!r} bit-identical"
    return digests


# =======================================================================================
# Self-test (design-gate).
# =======================================================================================
def self_test():
    print("[self-test] verb-class surface set size =", len(_NON_FACTIVE_SURFACE),
          "| 'wished' in set:", "wished" in _NON_FACTIVE_SURFACE,
          "| 'thought' in set:", "thought" in _NON_FACTIVE_SURFACE,
          "| 'killed' in set:", "killed" in _NON_FACTIVE_SURFACE,
          "| 'put' in set:", "put" in _NON_FACTIVE_SURFACE)
    assert "wished" in _NON_FACTIVE_SURFACE and "thought" in _NON_FACTIVE_SURFACE
    assert "killed" not in _NON_FACTIVE_SURFACE and "put" not in _NON_FACTIVE_SURFACE

    # Direct-object parse on the 4 real injection clauses.
    probes = {
        "wished for a cool place where he might rest and eat his dinner": (False, "non_factive_verb"),
        "put the strawberry back again": (True, "admit"),
        "killed a great many sheep": (True, "admit"),
        "thought she would eat her lunch": (False, "non_factive_verb"),
    }
    for clause, (exp_admit, _exp_reason) in probes.items():
        tagged = ORC.pos_tag_sentence(clause)
        admit, dec = verb_admits_injection(tagged)
        assert admit == exp_admit, f"verb-filter probe wrong for {clause!r}: {dec} (expected admit={exp_admit})"
        print(f"[self-test]   {clause[:38]:38s} -> admit={admit} {dec}")
    # structural DO-check must ALSO independently suppress both bad clauses (verb-independent corroboration).
    assert _has_genuine_direct_object(ORC.pos_tag_sentence("killed a great many sheep"),
                                      ORC.find_main_verb(ORC.pos_tag_sentence("killed a great many sheep"))[0])
    assert _has_genuine_direct_object(ORC.pos_tag_sentence("put the strawberry back again"),
                                      ORC.find_main_verb(ORC.pos_tag_sentence("put the strawberry back again"))[0])
    assert not _has_genuine_direct_object(ORC.pos_tag_sentence("wished for a cool place"),
                                          ORC.find_main_verb(ORC.pos_tag_sentence("wished for a cool place"))[0])
    assert not _has_genuine_direct_object(ORC.pos_tag_sentence("thought she would eat her lunch"),
                                          ORC.find_main_verb(ORC.pos_tag_sentence("thought she would eat her lunch"))[0])
    print("[self-test] direct-object parse: killed/put have DO; wished(prep)/thought(complement) do NOT")

    clf = V2._fit_clf()

    # (F.1) ANTI-COPY-DIVERGENCE: extract_vf(orphan|gold|lastactive|topical) == V2.extract_passage_cs byte-id.
    for pid, text in G3_PASSAGES.items():
        for seg in ("orphan", "gold", "learned_lastactive", "learned_topical"):
            mine = extract_passage_vf(text, clf, pid, G3_PASSAGES, "handrule", seg,
                                      role_fix=True, self_loop_guard=True)
            ref = V2.extract_passage_cs(text, clf, pid, G3_PASSAGES, "handrule", seg,
                                        role_fix=True, self_loop_guard=True)
            assert mine == ref, f"COPY-DIVERGENCE {pid}/{seg}:\n {mine}\n {ref}"
    print("[self-test] anti-copy-divergence: extract_vf == V2.extract_passage_cs on orphan/gold/lastactive/topical")

    # Baseline arms through V2.run_arm (byte-identical to v2) + the verbfilter arm through MY extract.
    ef = V2.run_arm(clf, "orphan", role_fix=False, self_loop_guard=False)
    floor = V2.run_arm(clf, "orphan", role_fix=True, self_loop_guard=True)
    lastactive = V2.run_arm(clf, "learned_lastactive", role_fix=True, self_loop_guard=True)
    topical = V2.run_arm(clf, "learned_topical", role_fix=True, self_loop_guard=True)
    verbfilter = run_arm_vf(clf, _VF_MODE, role_fix=True, self_loop_guard=True)
    gold = V2.run_arm(clf, "gold", role_fix=True, self_loop_guard=True)

    # POSITIVE CONTROL: envelope floor reproduces + gold/v1/v2 recover N5.
    assert ef["foundation"]["n_relations"] == FLOOR["n_relations"], "POS-CTRL n_rel"
    assert not ef["n5_relation"] and not floor["n5_relation"], "floor unexpectedly has N5"
    assert gold["n5_relation"] and lastactive["n5_relation"] and topical["n5_relation"], "reference N5 broken"

    # DISCRIMINATOR FIRES: verbfilter must EVALUATE >=2 COORD bare-VP sites and SUPPRESS >=1.
    assert len(verbfilter["vf_decisions"]) >= 2, \
        f"verbfilter evaluated {len(verbfilter['vf_decisions'])} sites (<2): discriminator vacuous"
    n_suppressed = sum(1 for d in verbfilter["vf_decisions"] if not d["admit"])
    assert n_suppressed >= 1, "verb-filter suppressed 0 sites -- gate never fired"
    # verbfilter store must DIFFER from v2 topical (mechanism fired) -- else the filter did nothing.
    assert _store_json(verbfilter) != _store_json(topical), "verbfilter store == topical (filter did not fire)"

    sup = _suppression_telemetry(verbfilter, topical)
    print(f"[self-test] verbfilter: sites={len(verbfilter['vf_decisions'])} suppressed={sup['n_suppressed']} "
          f"removed_fp={sup['n_removed_fp']} nonfactive_fp_suppressed={sup['n_nonfactive_fp_suppressed']} "
          f"added_fp={len(sup['added_fp_relations'])}")
    print(f"[self-test]   suppressed injections: {sup['suppressed_injections']}")
    print(f"[self-test]   kept injections:       {sup['kept_injections']}")
    print(f"[self-test]   removed FP relations:  {sup['removed_fp_relations']}")
    assert not sup["added_fp_relations"], f"filter ADDED FPs (should only remove): {sup['added_fp_relations']}"
    assert sup["all_suppressed_are_nonfactive_or_no_do"], "a suppressed site was factive+transitive (over-filter)"

    def _sp(a): return a["strict"]["strict_precision"]
    print(f"[self-test] strict_prec: floor={_sp(floor):.4f} topical={_sp(topical):.4f} "
          f"verbfilter={_sp(verbfilter):.4f} gold={_sp(gold):.4f} | "
          f"N5 vf={verbfilter['n5_relation']} | CMP vf={verbfilter['slices']['CMP']:.3f} "
          f"RELF1r vf={verbfilter['relf1']['micro_recall']:.3f}")

    # REGRESSION: role controls hold; coref ref_acc identical across arms; overlay witness green.
    ctrl = V2._role_controls(clf)
    assert ctrl["passive_rolefix"] >= PASSIVE_FLOOR and ctrl["reversal_rolefix"] >= REVERSAL_FLOOR, "role regress"
    for nm, a in (("floor", floor), ("topical", topical), ("verbfilter", verbfilter), ("gold", gold)):
        assert a["ref_acc"] == ef["ref_acc"], f"{nm} moved ref_acc (coref regression)"
    ok, tail = V2._run_overlay_witness()
    assert ok, f"overlay witness FAILED: {tail}"
    print(f"[self-test] controls: passive {ctrl['passive_rolefix']:.2f} reversal {ctrl['reversal_rolefix']:.2f}; "
          f"ref_acc {ef['ref_acc']:.3f} identical; overlay green")

    # ARMS-MUST-DIFFER (verbfilter==gold coincidence is a STRONG-PASS, exempted + reported as telemetry).
    _arms_must_differ(
        dict(handrule_orphan=_store_json(floor), learned_topical=_store_json(topical),
             learned_topical_verbfilter=_store_json(verbfilter), gold_clauseseg=_store_json(gold)),
        exempt_pairs=frozenset({tuple(sorted(("gold_clauseseg", "learned_topical_verbfilter")))}))

    # DETERMINISM.
    vf2 = run_arm_vf(clf, _VF_MODE, role_fix=True, self_loop_guard=True)
    assert vf2["strict"] == verbfilter["strict"] and vf2["injections"] == verbfilter["injections"], "nondeterministic"

    print("[self-test] PASS")
    return 0


# =======================================================================================
# Verdict.
# =======================================================================================
def build_verdict(output_dir, run_mode):
    t0 = time.perf_counter()
    _write_start_marker(output_dir, run_mode, expected_n_units=6)
    clf = V2._fit_clf()

    ef = V2.run_arm(clf, "orphan", role_fix=False, self_loop_guard=False)
    floor = V2.run_arm(clf, "orphan", role_fix=True, self_loop_guard=True)
    lastactive = V2.run_arm(clf, "learned_lastactive", role_fix=True, self_loop_guard=True)
    topical = V2.run_arm(clf, "learned_topical", role_fix=True, self_loop_guard=True)
    verbfilter = run_arm_vf(clf, _VF_MODE, role_fix=True, self_loop_guard=True)
    gold = V2.run_arm(clf, "gold", role_fix=True, self_loop_guard=True)
    arms = dict(envelope_floor=ef, handrule_orphan=floor, learned_lastactive=lastactive,
                learned_topical=topical, learned_topical_verbfilter=verbfilter, gold_clauseseg=gold)

    digests = _arms_must_differ(
        {k: _store_json(v) for k, v in arms.items() if k != "envelope_floor"},
        exempt_pairs=frozenset({tuple(sorted(("gold_clauseseg", "learned_topical_verbfilter")))}))
    mech_fired = _store_json(verbfilter) != _store_json(topical)
    ctrl = V2._role_controls(clf)
    witness_ok, witness_tail = V2._run_overlay_witness()
    sup = _suppression_telemetry(verbfilter, topical)
    verbfilter_matches_gold_oracle = (_store_json(verbfilter) == _store_json(gold))

    def _sp(a): return a["strict"]["strict_precision"]

    # positive control (basis reproduces).
    pc_ok = (ef["foundation"]["n_relations"] == FLOOR["n_relations"] and
             abs(ef["slices"]["CMP"] - FLOOR["CMP"]) <= 0.002 and
             abs(ef["ref_acc"] - FLOOR["ref_acc"]) <= 0.002 and
             abs(ef["relf1"]["micro_recall"] - FLOOR["RELF1_recall"]) <= 0.01 and
             not ef["n5_relation"] and gold["n5_relation"] and
             lastactive["n5_relation"] and topical["n5_relation"])

    passive_ok = ctrl["passive_rolefix"] >= PASSIVE_FLOOR
    reversal_ok = ctrl["reversal_rolefix"] >= REVERSAL_FLOOR
    coref_ok = all(a["ref_acc"] == ef["ref_acc"] for a in (floor, lastactive, topical, verbfilter, gold))
    no_regression = passive_ok and reversal_ok and coref_ok and witness_ok and mech_fired

    # PRIMARY: does verbfilter KEEP recovery AND RESTORE precision to >= floor (ideally to ceiling)?
    n5_recovered = verbfilter["n5_relation"]
    cmp_reaches_ceiling = verbfilter["slices"]["CMP"] >= gold["slices"]["CMP"] - CMP_CEILING_TOL
    recall_reaches_ceiling = verbfilter["relf1"]["micro_recall"] >= gold["relf1"]["micro_recall"] - RECALL_CEILING_TOL
    keeps_recovery = n5_recovered and cmp_reaches_ceiling and recall_reaches_ceiling

    precision_restored = _sp(verbfilter) >= _sp(floor) - PREC_RESTORE_TOL
    precision_reaches_ceiling = _sp(verbfilter) >= _sp(gold) - 1e-9
    precision_below_floor = _sp(verbfilter) < _sp(floor) - PREC_RESTORE_TOL
    prec_delta_vs_v2 = _sp(verbfilter) - _sp(topical)

    # the suppressed sites must all be non-factive / no-direct-object (no over-filter of an event verb).
    suppressed_all_nonfactive = sup["all_suppressed_are_nonfactive_or_no_do"] and not sup["added_fp_relations"]

    if not pc_ok:
        verdict = "INVALID_POSITIVE_CONTROL_FAIL"
        vmsg = (f"positive control failed: envelope_floor n_rel={ef['foundation']['n_relations']} N5={ef['n5_relation']}; "
                f"gold N5={gold['n5_relation']}; v2 topical N5={topical['n5_relation']}. Basis broken.")
    elif not no_regression:
        verdict = "REGRESSION"
        vmsg = (f"the verb-class filter regressed a control: passive {ctrl['passive_rolefix']:.2f} "
                f"reversal {ctrl['reversal_rolefix']:.2f} coref_ok={coref_ok} overlay={witness_ok} "
                f"mech_fired={mech_fired}. Revert + localize.")
    elif keeps_recovery and precision_restored and suppressed_all_nonfactive:
        verdict = "CLAUSE_SEG_PRECISION_CLEAN"
        vmsg = (f"THE VERB-CLASS FILTER COMPLETES THE CLAUSE-SEG COMPONENT ON PRECISION. Gating the topical-"
                f"animate held-subject injection to TRANSITIVE-FACTIVE coordinated verbs (suppress non-factive "
                f"/ mental-state / no-direct-object) KEEPS the ceiling recovery AND restores strict precision "
                f"to {'the GOLD CEILING' if precision_reaches_ceiling else 'the do-nothing floor'}. Recovery "
                f"kept: N5 (svo killed wolf sheep)={verbfilter['n5_relation']}; CMP {floor['slices']['CMP']:.3f}->"
                f"{verbfilter['slices']['CMP']:.3f} (ceiling {gold['slices']['CMP']:.3f}); RELF1-recall "
                f"{floor['relf1']['micro_recall']:.3f}->{verbfilter['relf1']['micro_recall']:.3f} (ceiling "
                f"{gold['relf1']['micro_recall']:.3f}). Precision RESTORED: verbfilter {_sp(verbfilter):.4f} vs "
                f"orphan floor {_sp(floor):.4f} (v2 topical was {_sp(topical):.4f} BELOW floor; gold ceiling "
                f"{_sp(gold):.4f}); delta_vs_v2={prec_delta_vs_v2:+.4f}; reaches_ceiling={precision_reaches_ceiling}. "
                f"Suppressed {sup['n_suppressed']} injection(s) {sup['suppressed_injections']} removing "
                f"{sup['n_nonfactive_fp_suppressed']} non-factive FP relation(s) {sup['nonfactive_fp_relations']}; "
                f"kept {sup['kept_injections']} (factive+transitive). verbfilter store matches gold oracle: "
                f"{verbfilter_matches_gold_oracle} (glass-box rediscovers the oracle's injection decisions). NO "
                f"control regression (passive {ctrl['passive_rolefix']:.2f} reversal {ctrl['reversal_rolefix']:.2f} "
                f"coref identical overlay green). The non-factive-verb LOCALIZATION is CONFIRMED. This is the "
                f"clean, fold-ready clause-seg parser component (composition + recall recovery AND precision "
                f"non-regressing). NP-head + argument-structure remain the next components. HONEST CAVEAT: on "
                f"this 5-passage corpus only 2 non-factive verbs occur, so the corpus alone cannot separate a "
                f"correct general verb-class from a list tuned to these two; the STRUCTURAL direct-object parse "
                f"(prep-governed / sentential-complement) suppresses both on verb-independent grounds and keeps "
                f"both event verbs, corroborating the localization. HYPOTHESIS pending landed-VET.")
    elif not keeps_recovery:
        verdict = "PARTIAL_LOST_RECOVERY"
        vmsg = (f"the filter OVER-suppressed and lost recovery. Precision {_sp(verbfilter):.4f} vs floor "
                f"{_sp(floor):.4f} (restored={precision_restored}) BUT N5={verbfilter['n5_relation']} CMP "
                f"{verbfilter['slices']['CMP']:.3f} (ceiling {gold['slices']['CMP']:.3f}) RELF1-recall "
                f"{verbfilter['relf1']['micro_recall']:.3f} (ceiling {gold['relf1']['micro_recall']:.3f}). A "
                f"factive event verb (killed/put) was mis-classified as non-factive or as no-direct-object. "
                f"Suppressed sites: {sup['suppressed_injections']}. DEFLATE + localize. HYPOTHESIS pending VET.")
    elif keeps_recovery and not precision_restored:
        verdict = "PARTIAL_PRECISION_STUCK"
        vmsg = (f"the filter kept recovery but precision still below floor. N5={verbfilter['n5_relation']} "
                f"CMP {verbfilter['slices']['CMP']:.3f} RELF1-recall {verbfilter['relf1']['micro_recall']:.3f} "
                f"(at ceiling) BUT strict precision {_sp(verbfilter):.4f} < floor {_sp(floor):.4f}. Some residual "
                f"FPs are NOT non-factive-verb injections (removed {sup['n_removed_fp']} FP; nonfactive "
                f"{sup['n_nonfactive_fp_suppressed']}). The localization is refined again -- residual FPs: see "
                f"verbfilter fp_relations. DEFLATE + localize. HYPOTHESIS pending landed-VET.")
    else:
        verdict = "PARTIAL"
        vmsg = (f"SPLIT. keeps_recovery={keeps_recovery} precision_restored={precision_restored} "
                f"suppressed_all_nonfactive={suppressed_all_nonfactive}; strict prec verbfilter "
                f"{_sp(verbfilter):.4f} floor {_sp(floor):.4f} topical {_sp(topical):.4f} gold {_sp(gold):.4f}. "
                f"See telemetry.")

    def _arm_summary(a):
        return dict(slices=a["slices"], ref_acc=a["ref_acc"], ref_ok=a["ref_ok"], ref_n=a["ref_n"],
                    relf1_micro_f1=a["relf1"]["micro_f1"], relf1_micro_precision=a["relf1"]["micro_precision"],
                    relf1_micro_recall=a["relf1"]["micro_recall"],
                    foundation_n_relations=a["foundation"]["n_relations"],
                    foundation_quality_lb=a["foundation"]["quality_precision_lower_bound"],
                    strict=a["strict"], n5_relation=a["n5_relation"], n5_answer=a["n5_answer"],
                    injections=a["injections"], per_q=a["per_q"])

    elapsed = time.perf_counter() - t0
    metrics = dict(
        verdict=verdict, verdict_msg=vmsg,
        summary=(f"{verdict}: strict_prec floor {_sp(floor):.4f} v2_topical {_sp(topical):.4f} "
                 f"verbfilter {_sp(verbfilter):.4f} gold {_sp(gold):.4f} (delta_vs_v2 {prec_delta_vs_v2:+.4f}; "
                 f"reaches_ceiling={precision_reaches_ceiling}) | N5 vf={verbfilter['n5_relation']} | "
                 f"CMP floor {floor['slices']['CMP']:.3f} -> vf {verbfilter['slices']['CMP']:.3f} -> gold "
                 f"{gold['slices']['CMP']:.3f} | RELF1-recall floor {floor['relf1']['micro_recall']:.3f} -> vf "
                 f"{verbfilter['relf1']['micro_recall']:.3f} -> gold {gold['relf1']['micro_recall']:.3f} | "
                 f"suppressed {sup['n_suppressed']} inj / {sup['n_nonfactive_fp_suppressed']} nonfactive FP | "
                 f"vf==gold_oracle={verbfilter_matches_gold_oracle} | passive {ctrl['passive_rolefix']:.2f} "
                 f"reversal {ctrl['reversal_rolefix']:.2f} coref_ok={coref_ok} overlay={witness_ok}"),
        elapsed_s=round(elapsed, 2), ts_iso=datetime.now(timezone.utc).isoformat(),
        anchor_name=ANCHOR_NAME, run_mode=run_mode, seed=SEED,
        one_variable=("verb-class filter on the held-subject injection (topical vs topical+verbfilter): inject "
                      "iff the coordinated clause's main verb is transitive-factive (NOT in the non-factive / "
                      "mental-state set AND has a genuine direct object); the held-subject SOURCE + boundaries "
                      "+ coref + role + cheap wins are byte-identical to v2"),
        positive_control_ok=pc_ok,
        mechanism_fired=mech_fired,
        verbfilter_matches_gold_oracle=verbfilter_matches_gold_oracle,
        primary=dict(n5_recovered=n5_recovered, cmp_reaches_ceiling=cmp_reaches_ceiling,
                     recall_reaches_ceiling=recall_reaches_ceiling, keeps_recovery=keeps_recovery,
                     precision_restored=precision_restored, precision_reaches_ceiling=precision_reaches_ceiling,
                     precision_below_floor=precision_below_floor,
                     suppressed_all_nonfactive=suppressed_all_nonfactive,
                     strict_prec_verbfilter=round(_sp(verbfilter), 4),
                     strict_prec_v2_topical=round(_sp(topical), 4),
                     strict_prec_orphan_floor=round(_sp(floor), 4),
                     strict_prec_gold_ceiling=round(_sp(gold), 4),
                     prec_delta_vs_v2=round(prec_delta_vs_v2, 4),
                     n_injections_suppressed=sup["n_suppressed"],
                     n_nonfactive_fp_suppressed=sup["n_nonfactive_fp_suppressed"]),
        suppression_telemetry=sup,
        regression=dict(passive_rolefix=ctrl["passive_rolefix"], reversal_rolefix=ctrl["reversal_rolefix"],
                        passive_ok=passive_ok, reversal_ok=reversal_ok, coref_ok=coref_ok,
                        overlay_witness_ok=witness_ok, overlay_witness_tail=witness_tail,
                        mechanism_fired=mech_fired, no_regression=no_regression,
                        passive_per=ctrl["passive_per"], reversal_per=ctrl["reversal_per"]),
        arms_differ_digests=digests,
        bands=dict(PREC_RESTORE_TOL=PREC_RESTORE_TOL, CMP_CEILING_TOL=CMP_CEILING_TOL,
                   RECALL_CEILING_TOL=RECALL_CEILING_TOL, PASSIVE_FLOOR=PASSIVE_FLOOR,
                   REVERSAL_FLOOR=REVERSAL_FLOOR),
        verb_class=dict(non_factive_base=sorted(_NON_FACTIVE_BASE),
                        non_factive_surface_size=len(_NON_FACTIVE_SURFACE),
                        preps=sorted(_PREPS), complementizers=sorted(_COMPLEMENTIZERS),
                        subj_pron=sorted(_SUBJ_PRON), obj_pron=sorted(_OBJ_PRON)),
        arms=dict(envelope_floor=_arm_summary(ef), handrule_orphan=_arm_summary(floor),
                  learned_lastactive=_arm_summary(lastactive), learned_topical=_arm_summary(topical),
                  learned_topical_verbfilter=_arm_summary(verbfilter), gold_clauseseg=_arm_summary(gold)),
        cited_refs=dict(
            v2_topical=dict(source="data/exp_reader_clauseseg_topical_animate_subject_v2/metrics.json",
                            strict_prec=V2_TOPICAL_PREC),
            orphan_floor=dict(strict_prec=ORPHAN_FLOOR_PREC), gold_ceiling=dict(strict_prec=GOLD_CEILING_PREC)),
        note=("Glass-box verb-class filter: at a COORD-boundary bare-VP conjunct, inject the overlay's "
              "topical-animate protagonist as subject ONLY IF the coordinated clause's main verb is transitive-"
              "factive -- NOT in a transparent non-factive/mental-state/irrealis set (wish/think/hope/believe/"
              "want/seem/...) AND governing a genuine direct object (not a prep-phrase 'wished FOR a place', not "
              "a sentential complement 'thought SHE would ...'). Two orthogonal glass-box signals (verb-class + "
              "direct-object parse) both suppress the non-factive conjuncts and both keep the event verbs."),
        scope_caveat=("Same mostly-in-vocab 3rd-reader narrative slice (n_questions=15, n_relations~36 -> modestly "
                      "powered). COMPLETE_TRUTH is a single-annotator hand annotation reused from the oracle cell. "
                      "'Precision restored' = to the do-nothing floor / gold ceiling, NOT a precision GAIN beyond "
                      "gold. Only 2 non-factive verbs occur here, so the corpus cannot separate a correct general "
                      "verb-class from a tuned list; the structural direct-object parse is the verb-independent "
                      "generalization guard. CLAIM-VET-pending; strategic read = hypothesis pending landed-VET."),
        n_passages=len(G3_PASSAGES), n_questions=len(G3_QS),
    )
    _write_metrics(output_dir, metrics)
    print(metrics["summary"])
    print("verdict:", verdict)
    print("verdict_msg:", vmsg)
    print("suppression telemetry:", json.dumps(sup))
    for k in ("envelope_floor", "handrule_orphan", "learned_lastactive", "learned_topical",
              "learned_topical_verbfilter", "gold_clauseseg"):
        a = arms[k]
        print(f"  {k:26s} strict_prec={a['strict']['strict_precision']:.4f} fp={a['strict']['fp']:2d}/"
              f"{a['strict']['n_extracted']:2d} tp={a['strict']['tp']:2d} | all={a['slices']['all']:.3f} "
              f"CMP={a['slices']['CMP']:.3f} | ref={a['ref_acc']:.3f} | RELF1r={a['relf1']['micro_recall']:.3f} "
              f"| N5={a['n5_relation']} | inj={len(a['injections'])}")
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--run-mode", default="full")
    args = ap.parse_args()
    if args.self_test:
        return self_test()
    run_mode = "smoke" if args.smoke else args.run_mode
    return build_verdict(OUTPUT_DIR, run_mode)


if __name__ == "__main__":
    try:
        rc = main()
        sys.exit(rc if rc is not None else 0)
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # NOT BaseException; preserves SystemExit + KeyboardInterrupt
        _write_crash_metrics(OUTPUT_DIR, e)
        raise
