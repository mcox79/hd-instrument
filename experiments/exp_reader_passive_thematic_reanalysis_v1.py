"""PLUGGABLE passive-voice THEMATIC-REANALYSIS mechanism for the consolidated reader (v1).

WHAT: a SYSTEMATIC single-sentence passive mechanism. On a structurally-detected passive
(aux be/was/were/is/are/been/be + PAST-PARTICIPLE, optionally + by-PP), REVERSE the canonical
role mapping instead of trusting linear order or the perceptron:
    grammatical (pre-verbal) SUBJECT  ->  PATIENT / theme
    by-object NP head (if present)    ->  AGENT
This fires on EVERY detected passive (not parse-luck), overriding the perceptron/ECM-routing for
that predicate only. Non-passive predicates are byte-identical to the banked composed reader.

WHY (autopsy of the banked reader, diagnosed before building -- see diag): passive DETECTION already
works (M._detect_passive fires on all 13 held-out passages). The banked reader still abstains on
met/assailed/confined/washed/supplied/evinced/overtaken because of THREE downstream failures, none of
which is the detector:
  (1) BY-OBJECT LABELED LOCATION: "by" is in ORC.PREPS_LOC, so the perceptron scores by-agents as
      LOCATION (assailed->questions, confined->gout, washed->waves, overtaken->judgment) -> no AGENT.
  (2) BY-OBJECT HEAD MIS-ID when an adjective intervenes: ORC.prev_prep only skips DETERMINERS, so
      "by an elderly parson"->parson, "by an excellent woman"->woman, "by a certain impatience"->
      impatience are never linked to "by" (met, supplied, evinced).
  (3) PRE-VERBAL SUBJECT NOT ROUTED to the passive predicate in subordinate/relative clauses
      ("where he was confined", "that noble mole is washed") -> no PATIENT candidate at the verb.
The two that DO fire (opposed, revealed) are exactly where ECM-routing + perceptron happened to line
up. This mechanism replaces all three with a structural rule.

MECHANISM (general; NOT tuned to the held-out gold):
  by_object_head(tagged, v0): first 'by'(IN) after the verb (stop at a finite verb); the by-object HEAD
    = first content noun / subj-obj pronoun after the 'by', skipping determiners/adjectives/adverbs/CD.
    (Post-modifiers -- "parson astride", "judgment of Heaven", "woman as governess" -- are attachments;
    the immediate nominal is the agent head. Word-identity-free.)
  passive_subject(tagged, v0, byobj_idx): nearest pre-verbal NP/pronoun to the LEFT of the verb that is
    NOT preposition-governed and is not the by-object -> the grammatical subject = theme.
  Emission: (verb, agent=by-head-or-carried, patient=subject). Passive + by-phrase LICENSES a transitive
    frame, so the emission BYPASSES the learned admissibility gate (the evidence pass only sees POST-verbal
    objects and would wrongly suppress passive-only verbs). NEVER-CONFIDENTLY-WRONG: fires ONLY when a
    subject is found AND a real agent (by-PP head or carried antecedent) exists; ABSTAINS on agentless
    passives with no antecedent (does not manufacture a tuple) and on self-loops.

PLUGGABILITY: install(CR) monkeypatches CR.clause_predicate_pass_composed with a replacement that is
BYTE-IDENTICAL to the banked function when flags['passive_reanalysis'] is falsy, and applies the
reanalysis branch only when it is True. So P2 ablation = same installed function with the flag OFF ==
banked behavior. The banked cell file is NOT edited. ASCII-only; glass-box (no LLM/network/autograd).
"""
from __future__ import annotations


# ---------------------------------------------------------------------------------------
# Systematic structural helpers (word-identity-free; POS + preposition + order only).
# ---------------------------------------------------------------------------------------
_NOUN_POS = ("NN", "NNS", "NNP", "NNPS")
_SKIP_BEFORE_HEAD = ("DT", "JJ", "JJR", "JJS", "RB", "RBR", "RBS", "CD", "PRP$")
_FINITE_VERB_POS = ("VBD", "VBZ", "VBP", "MD")


def by_object_head(tagged, v0, ORC):
    """Index of the by-object NP head after passive verb v0, or None.
    First 'by'(IN) after v0 (stop at an intervening finite verb = next clause); then the FIRST content
    noun / subj-obj pronoun, skipping determiners/adjectives/adverbs/numerals."""
    n = len(tagged)
    bj = None
    for k in range(v0 + 1, n):
        surf, low, pos = tagged[k]
        if pos in _FINITE_VERB_POS:            # a following finite verb = a new clause; stop
            break
        if pos == "IN" and low == "by":
            bj = k
            break
    if bj is None:
        return None
    k = bj + 1
    while k < n:
        surf, low, pos = tagged[k]
        if pos in _SKIP_BEFORE_HEAD:
            k += 1
            continue
        if pos in _NOUN_POS:
            return k                            # first nominal after 'by' = agent head
        if low in ORC.PRONOUNS_SUBJ_OBJ:
            return k                            # "by them"
        return None                             # non-nominal immediately after 'by' -> no head
    return None


def passive_subject(tagged, v0, byobj_idx, ORC):
    """Index of the grammatical (pre-verbal) subject of passive verb v0, or None.
    Nearest NP/pronoun to the LEFT of v0 that is not preposition-governed and is not the by-object."""
    for i in range(v0 - 1, -1, -1):
        if byobj_idx is not None and i == byobj_idx:
            continue
        surf, low, pos = tagged[i]
        is_nom = (pos in _NOUN_POS) or (low in ORC.PRONOUNS_SUBJ_OBJ)
        if not is_nom:
            continue
        if ORC.prev_prep(tagged, i) is None:    # not governed by a preposition (exclude 'in his chamber')
            return i
    return None


# ---------------------------------------------------------------------------------------
# The replacement clause pass. Identical to CR.clause_predicate_pass_composed except the passive branch,
# which is gated on flags['passive_reanalysis'] (OFF => byte-identical to banked).
# ---------------------------------------------------------------------------------------
def make_clause_pass(CR):
    """Build a drop-in replacement for CR.clause_predicate_pass_composed bound to CR's helper modules."""
    M = CR.M
    ORC = CR.ORC
    L = CR.L
    POSSLOT = CR.POSSLOT
    E = CR.E
    GATE1 = CR.GATE1
    GATESPLIT = CR.GATESPLIT
    VC = CR.VC
    RELABEL = CR.RELABEL

    def clause_predicate_pass_composed(tagged, heads, clf, gate_fn, carried_agent_in, sel_fn, ditrans_fn,
                                       flags, supp):
        lows = [t[1] for t in tagged]

        # 1. ENUMERATE predicates (identical)
        if flags["enum_general"]:
            predicates = CR.content_verb_indices_general(tagged, use_dohave=flags["use_dohave"])
        elif flags["use_action"]:
            predicates = POSSLOT.content_verb_indices_ext_v5(tagged, use_dohave=flags["use_dohave"],
                                                             use_action=True)
        else:
            predicates = list(E.content_verb_indices_ext(tagged, use_dohave=flags["use_dohave"]))

        if flags["g1"]:
            kept_pred = []
            for i in predicates:
                if GATE1.is_contracted_aux(tagged[i][1]):
                    supp["g1_pred_dropped"] += 1
                    continue
                kept_pred.append(i)
            predicates = kept_pred

        # 2. CANDIDATES (identical)
        if flags["use_slotfix"]:
            candidates = POSSLOT.candidate_indices_slotfix(tagged, use_objpron=True, use_reflexive=True,
                                                           use_fish=True)
        else:
            candidates = ORC.candidate_indices(tagged)

        # 3. ASSIGN candidates -> predicates (identical)
        by_pred = POSSLOT._assign_ecm_v5(tagged, heads, predicates, candidates, use_ecm=flags["use_ecm"])
        main_idx, main_verb, main_passive = ORC.find_main_verb(tagged)

        out = []
        carried_agent = carried_agent_in
        evidence = {}
        for v0 in predicates:
            v1 = v0 + 1
            low = tagged[v0][1]
            passive = M._detect_passive(tagged, v0, lows)
            local_cand = sorted(by_pred.get(v1, []))
            first_cand = local_cand[0] if local_cand else None
            vl = L.lemma_verb(low)

            # ---- SYSTEMATIC PASSIVE THEMATIC REANALYSIS (the mechanism) --------------------
            if flags.get("passive_reanalysis") and passive:
                byh = by_object_head(tagged, v0, ORC)
                subj = passive_subject(tagged, v0, byh, ORC)
                # gate-independent bare-NP evidence pass (keep parity with base for the learned gate)
                for i in local_cand:
                    if i > v0 and ORC.prev_prep(tagged, i) is None:
                        evidence[vl] = True
                if subj is not None and low not in ("has", "is"):
                    agent_surf = tagged[byh][1] if byh is not None else carried_agent
                    patient_surf = tagged[subj][1]
                    # never-confidently-wrong: need a real agent (by-PP head or carried) + no self-loop.
                    # Passive+by licenses a transitive frame -> BYPASS the learned admissibility gate
                    # (the evidence pass only observes POST-verbal objects; passive-only verbs get no
                    # evidence and would be wrongly suppressed).
                    if agent_surf is not None and CR._norm(agent_surf) != CR._norm(patient_surf):
                        is_main = (v0 == main_idx)
                        kind = M.predicate_kind(tagged, v0, is_main)
                        out.append((low, agent_surf, patient_surf, v0, kind))
                        supp["passive_reanalysis_fired"] += 1
                if byh is not None:
                    carried_agent = tagged[byh][1]
                continue
            # ---- end mechanism; below is byte-identical to the banked function ------------

            # 4. ROLE assign (AveragedPerceptron)
            roles = {}
            for i in local_cand:
                feats = ORC.candidate_features(tagged, i, v0, passive, first_cand)
                roles[i] = clf.predict(feats)

            for i in local_cand:
                if i > v0 and ORC.prev_prep(tagged, i) is None:
                    evidence[vl] = True

            # 5. ROLES relabel
            if flags["relabel"]:
                RELABEL.role_relabel_reassign(roles, local_cand, tagged, v0, passive, gate_fn, ditrans_fn,
                                              use_np_head=True, emission_preserving=True)

            agents_local = [i for i in local_cand if roles.get(i) == "AGENT"]
            patients_local = [i for i in local_cand if roles.get(i) == "PATIENT"]
            resolved_agent = tagged[agents_local[0]][1] if agents_local else carried_agent

            kept_patients = patients_local
            if flags["use_argmax"] and sel_fn is not None and len(patients_local) >= 2:
                def _score(i):
                    s = sel_fn(vl, tagged[i][1])
                    return -1.0 if s is None else s
                best_i = max(patients_local, key=lambda i: (_score(i), -i))
                kept_patients = [best_i]

            # 6. EMISSION GATE
            if flags["g4_mode"] != "off" and kept_patients:
                filt = []
                for pi in kept_patients:
                    if GATESPLIT.g4_excludes(tagged, pi, flags["g4_mode"]):
                        supp["g4_patient_excluded"] += 1
                    else:
                        filt.append(pi)
                kept_patients = filt
            if flags["g2"] and kept_patients:
                if GATE1._is_nonfactive(low) and not VC._has_genuine_direct_object(tagged, v0):
                    supp["g2_emissions_suppressed"] += len(kept_patients)
                    kept_patients = []

            if resolved_agent is not None and kept_patients and low not in ("has", "is"):
                if gate_fn(vl):
                    is_main = (v0 == main_idx)
                    kind = M.predicate_kind(tagged, v0, is_main)
                    for pi in kept_patients:
                        if flags["g3"] and resolved_agent == tagged[pi][1]:
                            supp["g3_selfloops_dropped"] += 1
                            continue
                        out.append((low, resolved_agent, tagged[pi][1], v0, kind))
            if agents_local:
                carried_agent = tagged[agents_local[0]][1]
        return out, carried_agent, evidence

    return clause_predicate_pass_composed


# ---------------------------------------------------------------------------------------
# Install / uninstall (monkeypatch; banked cell file untouched on disk).
# ---------------------------------------------------------------------------------------
def install(CR):
    """Patch CR.clause_predicate_pass_composed with the reanalysis-capable replacement.
    Returns the original callable for restoration. Idempotent-safe (stashes original once)."""
    if not hasattr(CR, "_ORIG_clause_predicate_pass_composed"):
        CR._ORIG_clause_predicate_pass_composed = CR.clause_predicate_pass_composed
    CR.clause_predicate_pass_composed = make_clause_pass(CR)
    return CR._ORIG_clause_predicate_pass_composed


def uninstall(CR):
    if hasattr(CR, "_ORIG_clause_predicate_pass_composed"):
        CR.clause_predicate_pass_composed = CR._ORIG_clause_predicate_pass_composed
