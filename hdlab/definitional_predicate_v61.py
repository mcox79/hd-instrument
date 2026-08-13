"""v6.1 predicate layer -- the five defects the director hand-scored out of the v6 sample.

WHAT THIS IS. `hdlab/definitional_extraction.py` v6 recovered the PREDICATE of a process
definition (VP1 `X is the process of V-ing Y`, VP2 `X is the process by which CLAUSE`,
VP4 `X occurs when CLAUSE`). The director blind-scored 50 of its 250 facts 35 MEANINGFUL /
7 RELATED / 8 NOISE and named five defect classes. This module is the FIX LAYER: it reuses the
v6 regexes and the v6 clause walk unchanged, and changes only how the TERM is bounded, when a
match is REFUSED, and which ARGUMENT is taken.

  D1 TERM TRUNCATION  `form`, `process`, `second-degree`, `termination` (x2, colliding).
       Fixed in ONE place: `definitional_extraction.build_term_explain` under
       TERM_POLICY_STRICT. Not re-fixed per pattern -- that is what made this recur.
  D2 NEGATION DROPPED  "does NOT volunteer" banked as `volunteer`: the stored fact asserted the
       opposite of the source. Negation in scope over the recovered predicate -> REFUSE. No
       NEGATED_* relation is invented: nothing downstream consumes one, so it would be an island.
  D3 WRONG ARGUMENT  trailing adjuncts, obliques, parentheticals and purpose clauses were being
       read as the core argument (`lactation -> nipple`, `diffusion -> region`,
       `termination -> uag`, `differentiation -> function`).
  D4 FIRES ON NON-DEFINITIONS  the predicate search escaped the trigger's own clause (a
       coordinated main verb, a deeply embedded relative clause) and a data-description
       sentence was read as a definition.
  D5 PASSIVE SLOT  on "the development ... IS DISTURBED" the surface subject is the PATIENT.

REFUSAL IS A FIRST-CLASS OUTPUT. Every refusal is returned with its reason and its sentence; a
lower fact count is an accepted outcome. Nothing here writes to any foundation path.
ASCII-only.
"""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass, field, replace
from typing import Dict, List, Optional, Tuple

from hdlab.closed_class_lexicon import is_closed_class
from hdlab.definitional_extraction import (
    TERM_POLICY_LEGACY,
    TERM_POLICY_STRICT,
    PredicateFact,
    _ANAPHORIC_SUBJ,
    _AUX_SKIP,
    _BE_FORMS,
    _CONTENTLESS_VERB,
    _RE_VP1,
    _RE_VP2,
    _RE_VP4,
    _TOKEN_RE,
    _complement_head,
    _is_nominal_or_unknown,
    _tokens,
    _vp1_verbs,
    build_term_explain,
    clause_main_verb,
    definiens_head,
    is_verbal_lemma,
    verb_lemma_of,
)
from hdlab.thematic_role_labeler import lemma_word as lemma_verb

PATTERNS_V61 = ("VP1_PROCESS_OF", "VP2_BY_WHICH", "VP4_OCCURS_WHEN")
# ENABLING_CONDITION_PATIENT is the D5 correction, not a new capability: it is the same slot the
# v6 code already emitted, carrying the role the surface actually licenses. It replaces
# ENABLING_CONDITION_AGENT on passives; no NEGATED_* / MODAL_* type is introduced anywhere.
RELATIONS_V61 = ("PROCESS_ACTION", "PROCESS_PATIENT", "ENABLING_CONDITION",
                 "ENABLING_CONDITION_AGENT", "ENABLING_CONDITION_PATIENT")


@dataclass(frozen=True)
class PredicatePolicy:
    """One flag per DEFECT, so each fix can be ablated on its own (one variable per defect)."""
    name: str = "V61_ALL"
    strict_term: bool = True             # D1
    negation_refusal: bool = True        # D2
    argument_selection: bool = True      # D3
    clause_confinement: bool = True      # D4
    passive_patient: bool = True         # D5


POLICY_V61 = PredicatePolicy()
POLICY_V6_EQUIV = PredicatePolicy("V6_EQUIVALENT", False, False, False, False, False)


@dataclass
class Refusal:
    pattern: str
    reason: str
    detail: str
    definiendum: str
    sentence: str

    def to_dict(self) -> dict:
        return {"pattern": self.pattern, "reason": self.reason, "detail": self.detail,
                "definiendum": self.definiendum, "sentence": self.sentence}


@dataclass
class V61Out:
    facts: List[PredicateFact] = field(default_factory=list)
    refusals: List[Refusal] = field(default_factory=list)
    notes: Counter = field(default_factory=Counter)


# --------------------------------------------------------------------------------------- D3
# A parenthetical is an EXAMPLE, never the core argument: "a nonsense codon (UAA, UAG, or UGA)"
# gave `uag`. Strip before any argument is selected.
_PAREN_RE = re.compile(r"\([^()]*\)|\[[^\]]*\]")
# Particles belong to the verb and are stepped over; TRUE PREPOSITIONS open an oblique and the
# argument slot REFUSES rather than taking the oblique's object ("travels FROM regions" -> the
# core argument is the subject `material`, not `region`).
_V61_PARTICLE = {"in", "out", "up", "down", "off", "away", "apart", "together", "back", "on",
                 "over", "forward", "aside", "along", "around"}
_V61_OBLIQUE_PREP = {"from", "to", "with", "at", "by", "of", "about", "between", "among",
                     "within", "toward", "towards", "into", "onto", "through", "across",
                     "against", "upon", "for", "under", "during", "after", "before", "beyond",
                     "throughout", "per", "via"}

# --------------------------------------------------------------------------------------- D4
# The predicate lives in the TRIGGER'S OWN CLAUSE. A comma+coordinator opens a new main clause
# ("...old, AND THEN INCREASED even more" -- outside the when-clause), and a relativizer opens an
# embedded one ("the function of a gene THAT PRECEDES" -- two levels down).
_CLAUSE_BREAK_RE = re.compile(
    r",\s*(?:and|or|but|then|while|whereas|although|though|yet|so|since|because|however|"
    r"which|who)\b", re.IGNORECASE)
_EMBEDDED_CLAUSE_RE = re.compile(r"\s(?:that|which|who|whom|whose)\s", re.IGNORECASE)
_PURPOSE_MARK_RE = re.compile(r"\s(?:in\s+order\s+to|so\s+as\s+to|so\s+that)\s", re.IGNORECASE)
# A sentence that is DESCRIBING A FIGURE / TABLE / DATA COLUMN is reporting an observation, not
# defining a term ("As can be seen from the mortality rate data (column D), a high death rate
# occurred when ..."). Cheap, and only consulted on the text BEFORE the match.
_NONDEF_PHRASE = ("as can be seen", "as shown", "as seen", "as illustrated", "as depicted",
                  "as we can see", "note that", "notice that", "in this example",
                  "in the example above")
_NONDEF_WORD_RE = re.compile(r"\b(?:figure|table|column|graph|chart|axis|dataset)\b",
                             re.IGNORECASE)
# A REDUCED RELATIVE is a relative clause with its relativizer and copula elided: "an enzyme
# CALLED phosphodiesterase converts cAMP" -- `called` is a postnominal modifier, `converts` is
# the clause's verb. v6 banked `termination -> call`. The inventory is the participle members of
# the module's own `_NP_BOUNDARY` (already curated as "can only follow the head noun"), NOT a new
# guess, and the skip only takes effect if a LATER verb is actually found -- so a plain past-tense
# main verb ("when the sheep died") is left alone.
_REDUCED_REL_PARTICIPLE = {"called", "known", "termed", "named", "referred", "used", "found",
                           "made", "located", "produced", "involved", "formed", "composed",
                           "derived", "attached", "surrounded", "given", "taken", "seen",
                           "shown", "based", "related", "released", "carried", "labeled",
                           "labelled", "designated", "classified"}

# --------------------------------------------------------------------------------------- D2
_NEG_TOKEN = {"not", "never", "neither", "nor", "no", "none", "nothing", "cannot", "without",
              "rather", "instead", "unable", "lack", "lacks", "lacking", "absent", "absence",
              "fail", "fails", "failed", "failing", "seldom", "rarely", "hardly", "barely",
              "except", "unless", "non"}


def strip_parentheticals(span: str) -> Tuple[str, bool]:
    out = _PAREN_RE.sub(" ", span)
    out = re.sub(r"\s{2,}", " ", out).strip(" ,;")
    return out, out != span.strip(" ,;")


def confine_to_clause(span: str) -> Tuple[str, bool]:
    """Truncate `span` at the first boundary that leaves the trigger's own clause."""
    cuts = []
    m = _CLAUSE_BREAK_RE.search(span)
    if m:
        cuts.append(m.start())
    m = _EMBEDDED_CLAUSE_RE.search(span)
    if m:
        cuts.append(m.start())
    m = _PURPOSE_MARK_RE.search(span)
    if m:
        cuts.append(m.start())
    if not cuts:
        return span, False
    cut = min(cuts)
    return span[:cut].strip(" ,;"), True


def cut_at_purpose_infinitive(span: str) -> Tuple[str, bool]:
    """"specialized TO CARRY OUT distinct functions" -- the purpose clause is not the argument."""
    for m in re.finditer(r"\bto\s+([A-Za-z][A-Za-z'\-]*)", span):
        w = m.group(1)
        lem = verb_lemma_of(w)
        if lem and is_verbal_lemma(lem) and w.lower() == lem.lower():
            return span[:m.start()].strip(" ,;"), True
    return span, False


def nondefinitional_context(sentence: str, match_start: int) -> Optional[str]:
    pre = sentence[:match_start].lower()
    for p in _NONDEF_PHRASE:
        if p in pre:
            return p
    m = _NONDEF_WORD_RE.search(pre)
    return m.group(0).lower() if m else None


def negation_in_scope(tokens: List[str], verb_idx: int) -> Optional[str]:
    """The negator that has scope over the recovered predicate, or None. Scope = anything to the
    LEFT of the verb inside its own clause. A negator to the RIGHT belongs to a later constituent
    ("one member benefits WITHOUT affecting the other" negates `affect`, not `benefit`)."""
    for i in range(0, max(0, verb_idx)):
        t = tokens[i].lower()
        if t in _NEG_TOKEN or t.endswith("n't"):
            return tokens[i]
    return None


def passive_at(tokens: List[str], verb_idx: int) -> Tuple[bool, int]:
    """(is a BE-passive, index of the BE auxiliary). Progressive `-ing` is not a passive."""
    if verb_idx <= 0 or tokens[verb_idx].lower().endswith("ing"):
        return False, -1
    j = verb_idx - 1
    while j >= 0 and tokens[j].lower() in _AUX_SKIP:
        if tokens[j].lower() in _BE_FORMS:
            return True, j
        j -= 1
    return False, -1


def clause_verb(tokens: List[str], policy: PredicatePolicy) -> Optional[Tuple[int, str]]:
    """The v6 clause walk, plus D4's reduced-relative skip. Refusing stays a legal outcome."""
    hit = clause_main_verb(tokens)
    if hit is None or not policy.clause_confinement:
        return hit
    base = 0
    for _ in range(3):
        idx, lem = hit
        tok = tokens[base + idx].lower()
        if tok not in _REDUCED_REL_PARTICIPLE:
            return base + idx, lem
        if passive_at(tokens, base + idx)[0]:
            return base + idx, lem          # a real BE-passive, not a reduced relative
        nxt = clause_main_verb(tokens[base + idx:])
        if nxt is None:
            return base + idx, lem          # no later verb: leave the original alone
        base, hit = base + idx, nxt
    return base + hit[0], hit[1]


def core_argument(span: str, policy: PredicatePolicy) -> Tuple[Optional[str], str]:
    """Head of the CORE argument in `span` (the text right of the verb), or (None, reason)."""
    if not policy.argument_selection:
        return _complement_head(span), "OK_V6_PATH"
    span, cut = cut_at_purpose_infinitive(span)
    if not span:
        return None, "D3_PATIENT_PURPOSE_ONLY"
    toks = [(m.group(0), m.start()) for m in _TOKEN_RE.finditer(span)]
    k = 0
    while k < len(toks) and toks[k][0].lower() in _V61_PARTICLE:
        k += 1
    if k >= len(toks):
        return None, "D3_PATIENT_EMPTY"
    if toks[k][0].lower() in _V61_OBLIQUE_PREP:
        return None, "D3_PATIENT_OBLIQUE"
    head = definiens_head(span[toks[k][1]:])
    if head is None:
        return None, "D3_PATIENT_NO_NOMINAL"
    return head, "OK_PURPOSE_CUT" if cut else "OK"


def _term(dfd: str, sentence: str, anaphoric_gate: bool, policy: PredicatePolicy
          ) -> Tuple[Optional[Tuple[str, str]], str]:
    toks = _tokens(dfd)
    if not toks:
        return None, "TERM_NO_TOKENS"
    if anaphoric_gate and any(t.lower() in _ANAPHORIC_SUBJ for t in toks):
        return None, "TERM_ANAPHORIC_SUBJECT"
    dfd_lemma = lemma_verb(toks[-1])
    if is_closed_class(dfd_lemma) or not _is_nominal_or_unknown(dfd_lemma):
        return None, "TERM_NOT_NOMINAL"
    pol = TERM_POLICY_STRICT if policy.strict_term else TERM_POLICY_LEGACY
    built, reason = build_term_explain(dfd, sentence, pol)
    if built is None:
        return None, "D1_" + reason if reason == "BARE_CATEGORY_HEAD" else "TERM_" + reason
    return built, reason


def _prep_span(span: str, policy: PredicatePolicy, notes: Counter) -> str:
    """Parenthetical strip (D3) + clause confinement (D4), each behind its own flag."""
    if policy.argument_selection:
        span, stripped = strip_parentheticals(span)
        if stripped:
            notes["D3_PARENTHETICAL_STRIPPED"] += 1
    if policy.clause_confinement:
        span, cut = confine_to_clause(span)
        if cut:
            notes["D4_CLAUSE_TRUNCATED"] += 1
    return span


def extract_predicates_v61(sentence: str, policy: PredicatePolicy = POLICY_V61) -> V61Out:
    """All v6.1 predicate facts in ONE sentence, plus every refusal and why."""
    out = V61Out()
    if not sentence or len(sentence) < 12:
        return out

    def _refuse(pattern: str, reason: str, detail: str, dfd: str) -> None:
        out.refusals.append(Refusal(pattern, reason, detail, dfd, sentence))
        out.notes[reason] += 1

    # ---------------------------------------------------------------- VP1  "the process of V-ing"
    for m in _RE_VP1.finditer(sentence):
        dfd = m.group("dfd").strip()
        if policy.clause_confinement:
            cue = nondefinitional_context(sentence, m.start())
            if cue:
                _refuse("VP1_PROCESS_OF", "D4_NON_DEFINITIONAL_CONTEXT", cue, dfd)
                continue
        built, treason = _term(dfd, sentence, False, policy)
        if built is None:
            _refuse("VP1_PROCESS_OF", treason, "", dfd)
            continue
        term, ttype = built
        if "COORD_RESTART" in treason:
            out.notes["D1_COORD_RESTART"] += 1
        if "OF_EXTENDED" in treason:
            out.notes["D1_OF_EXTENDED"] += 1
        rest_raw = m.group("rest")
        rest = _prep_span(rest_raw, policy, out.notes)
        verbs = _vp1_verbs(rest)
        if not verbs:
            _refuse("VP1_PROCESS_OF", "NO_VERB_IN_OWN_CLAUSE", rest[:80], dfd)
            continue
        for lem, off in verbs:
            vtoks = [t.group(0) for t in _TOKEN_RE.finditer(rest[:off])]
            if policy.negation_refusal:
                neg = negation_in_scope(vtoks + [lem], len(vtoks))
                if neg:
                    _refuse("VP1_PROCESS_OF", "D2_NEGATION_IN_SCOPE", neg, dfd)
                    continue
            if lem == term.lower():
                continue
            out.facts.append(PredicateFact(term, ttype, "PROCESS_ACTION", lem, "VP1_PROCESS_OF",
                                           dfd, rest, sentence))
            pat, why = core_argument(rest[off:], policy)
            if pat is None:
                if why.startswith("D3"):
                    _refuse("VP1_PROCESS_OF", why, rest[off:][:80], dfd)
                continue
            if pat != lem and pat != term.lower():
                out.facts.append(PredicateFact(term, ttype, "PROCESS_PATIENT", pat,
                                               "VP1_PROCESS_OF", dfd, rest, sentence))

    # ---------------------------------------------------------------- VP2  "the process by which"
    for m in _RE_VP2.finditer(sentence):
        dfd = m.group("dfd").strip()
        if policy.clause_confinement:
            cue = nondefinitional_context(sentence, m.start())
            if cue:
                _refuse("VP2_BY_WHICH", "D4_NON_DEFINITIONAL_CONTEXT", cue, dfd)
                continue
        built, treason = _term(dfd, sentence, False, policy)
        if built is None:
            _refuse("VP2_BY_WHICH", treason, "", dfd)
            continue
        term, ttype = built
        if "COORD_RESTART" in treason:
            out.notes["D1_COORD_RESTART"] += 1
        if "OF_EXTENDED" in treason:
            out.notes["D1_OF_EXTENDED"] += 1
        clause = _prep_span(m.group("clause"), policy, out.notes)
        ctoks = [(t.group(0), t.start(), t.end()) for t in _TOKEN_RE.finditer(clause)]
        hit = clause_verb([t[0] for t in ctoks], policy)
        if hit is None:
            _refuse("VP2_BY_WHICH", "NO_VERB_IN_OWN_CLAUSE", clause[:80], dfd)
            continue
        idx, lem = hit
        if policy.negation_refusal:
            neg = negation_in_scope([t[0] for t in ctoks], idx)
            if neg:
                _refuse("VP2_BY_WHICH", "D2_NEGATION_IN_SCOPE", neg, dfd)
                continue
        if lem == term.lower():
            continue
        out.facts.append(PredicateFact(term, ttype, "PROCESS_ACTION", lem, "VP2_BY_WHICH",
                                       dfd, clause, sentence))
        is_pass, aux_i = passive_at([t[0] for t in ctoks], idx)
        if policy.passive_patient and is_pass:
            subj = definiens_head(clause[:ctoks[aux_i][1]])
            out.notes["D5_PASSIVE_SUBJECT_IS_PATIENT"] += 1
            if subj and subj != lem and subj != term.lower():
                out.facts.append(PredicateFact(term, ttype, "PROCESS_PATIENT", subj,
                                               "VP2_BY_WHICH", dfd, clause, sentence))
            continue
        pat, why = core_argument(clause[ctoks[idx][2]:], policy)
        if pat is None:
            if why.startswith("D3"):
                _refuse("VP2_BY_WHICH", why, clause[ctoks[idx][2]:][:80], dfd)
            continue
        if pat != lem and pat != term.lower():
            out.facts.append(PredicateFact(term, ttype, "PROCESS_PATIENT", pat, "VP2_BY_WHICH",
                                           dfd, clause, sentence))

    # ---------------------------------------------------------------- VP4  "occurs when CLAUSE"
    for m in _RE_VP4.finditer(sentence):
        dfd = m.group("dfd").strip()
        if policy.clause_confinement:
            cue = nondefinitional_context(sentence, m.start())
            if cue:
                _refuse("VP4_OCCURS_WHEN", "D4_NON_DEFINITIONAL_CONTEXT", cue, dfd)
                continue
        built, treason = _term(dfd, sentence, True, policy)
        if built is None:
            _refuse("VP4_OCCURS_WHEN", treason, "", dfd)
            continue
        term, ttype = built
        if "COORD_RESTART" in treason:
            out.notes["D1_COORD_RESTART"] += 1
        if "OF_EXTENDED" in treason:
            out.notes["D1_OF_EXTENDED"] += 1
        clause = _prep_span(m.group("clause"), policy, out.notes)
        ctoks = [(t.group(0), t.start(), t.end()) for t in _TOKEN_RE.finditer(clause)]
        hit = clause_verb([t[0] for t in ctoks], policy)
        if hit is None:
            _refuse("VP4_OCCURS_WHEN", "NO_VERB_IN_OWN_CLAUSE", clause[:80], dfd)
            continue
        idx, lem = hit
        if policy.negation_refusal:
            neg = negation_in_scope([t[0] for t in ctoks], idx)
            if neg:
                _refuse("VP4_OCCURS_WHEN", "D2_NEGATION_IN_SCOPE", neg, dfd)
                continue
        if lem == term.lower():
            continue
        out.facts.append(PredicateFact(term, ttype, "ENABLING_CONDITION", lem, "VP4_OCCURS_WHEN",
                                       dfd, clause, sentence))
        is_pass, aux_i = passive_at([t[0] for t in ctoks], idx)
        subj_end = ctoks[aux_i][1] if (is_pass and policy.passive_patient) else (
            ctoks[idx][1] if idx > 0 else 0)
        role = ("ENABLING_CONDITION_PATIENT" if (is_pass and policy.passive_patient)
                else "ENABLING_CONDITION_AGENT")
        if is_pass and policy.passive_patient:
            out.notes["D5_PASSIVE_SUBJECT_IS_PATIENT"] += 1
        subj = definiens_head(clause[:subj_end]) if subj_end > 0 else None
        if subj and subj != lem and subj != term.lower():
            out.facts.append(PredicateFact(term, ttype, role, subj, "VP4_OCCURS_WHEN",
                                           dfd, clause, sentence))

    seen = set()
    uniq: List[PredicateFact] = []
    for p in out.facts:
        key = (p.term, p.relation, p.object)
        if key in seen:
            continue
        seen.add(key)
        uniq.append(p)
    out.facts = uniq
    return out


def ablations(base: PredicatePolicy = POLICY_V61) -> Dict[str, PredicatePolicy]:
    """LEAVE-ONE-OUT: one policy per defect with exactly that defect's fix turned OFF."""
    return {
        "D1_strict_term_OFF": replace(base, name="D1_OFF", strict_term=False),
        "D2_negation_OFF": replace(base, name="D2_OFF", negation_refusal=False),
        "D3_argument_OFF": replace(base, name="D3_OFF", argument_selection=False),
        "D4_clause_OFF": replace(base, name="D4_OFF", clause_confinement=False),
        "D5_passive_OFF": replace(base, name="D5_OFF", passive_patient=False),
    }


# -------------------------------------------------------------------------------------------
# Self-test (run: python -m hdlab.definitional_predicate_v61). Every case is a REAL corpus
# sentence from the v6 blind sample the director hand-scored, named by its sample row.
# -------------------------------------------------------------------------------------------

S07 = ("The bystander effect is a phenomenon in which a witness or bystander does not volunteer "
       "to help a victim or person in distress")
S06 = ("Often the biochemical basis of epistasis is a gene pathway in which the expression of "
       "one gene is dependent on the function of a gene that precedes or follows in the pathway")
S13 = ("Differentiation is the process by which unspecialized cells become specialized to carry "
       "out distinct functions")
S16 = ("Diffusion is a process in which material travels from regions of high concentration to "
       "low concentration until equilibrium is reached")
S21 = ("The other form of polyploidy occurs when individuals of two different species reproduce "
       "to form a viable offspring that we call an allopolyploid")
S23 = ("As can be seen from the mortality rate data (column D), a high death rate occurred when "
       "the sheep were between 6 and 12 months old, and then increased even more rapidly")
S25 = ("Lactation is the process by which milk is synthesized and secreted from the mammary "
       "glands of the postpartum female breast in response to an infant sucking at the nipple")
S30 = "Neurodevelopmental disorders occur when the development of the nervous system is disturbed"
S36 = ("The process begins when mesenchymal cells in the embryonic skeleton gather together and "
       "begin to differentiate into specialized cells (a)")
S41 = ("A second-degree or incomplete block occurs when some impulses from the SA node reach the "
       "AV node and continue, while others do not")
S44 = ("Termination of the signal occurs when an enzyme called phosphodiesterase converts cAMP "
       "into AMP")
S45 = ("Termination of translation occurs when a nonsense codon (UAA, UAG, or UGA) is "
       "encountered")


def _trip(sentence: str) -> set:
    return {(f.term, f.relation, f.object) for f in extract_predicates_v61(sentence).facts}


def _self_test() -> None:
    # ---- D2: THE PERMANENT REGRESSION. Sample row [07] must yield NO positive `volunteer` fact.
    got = _trip(S07)
    assert not any(o == "volunteer" for _s, _r, o in got), got
    assert not any(s == "bystander effect" for s, _r, _o in got), got
    res = extract_predicates_v61(S07)
    assert any(r.reason == "D2_NEGATION_IN_SCOPE" for r in res.refusals), res.refusals
    # negation to the RIGHT of the verb does not negate it -- this fact must SURVIVE
    keep = _trip("Commensalism occurs when one member benefits without affecting the other")
    assert ("commensalism", "ENABLING_CONDITION", "benefit") in keep, keep
    # "fails to" is negation, not a control verb
    assert _trip("Nondisjunction occurs when sister chromatids fail to separate") == set()

    # ---- D1: bare category nouns refuse; coordination and of-postmodifiers keep their identity
    assert _trip(S21) == set(), _trip(S21)
    assert _trip(S36) == set(), _trip(S36)
    r36 = extract_predicates_v61(S36)
    assert any(r.reason == "D1_BARE_CATEGORY_HEAD" for r in r36.refusals), r36.refusals
    assert {s for s, _r, _o in _trip(S41)} == {"incomplete block"}, _trip(S41)
    s44, s45 = {s for s, _r, _o in _trip(S44)}, {s for s, _r, _o in _trip(S45)}
    assert s44 == {"termination of signal"}, s44
    assert s45 == {"termination of translation"}, s45
    assert not (s44 & s45), (s44, s45)             # the v6 collision is gone
    # a MODIFIED container noun is still a term (PROPER here, so it keeps its surface case --
    # this is sample row [01], unchanged from v6)
    assert {s for s, _r, _o in _trip(
        "The VBNC state occurs when prokaryotes respond to environmental stressors")} == {
        "VBNC state"}
    assert {s for s, _r, _o in _trip(
        "A sensory activation occurs when a physical stimulus is processed by a receptor")} == {
        "sensory activation"}

    # ---- D3: core argument of the MAIN predicate, never an adjunct/oblique/parenthetical/purpose
    assert not any(o == "nipple" for _s, _r, o in _trip(S25)), _trip(S25)
    assert ("lactation", "PROCESS_PATIENT", "milk") in _trip(S25), _trip(S25)
    assert not any(o == "region" for _s, _r, o in _trip(S16)), _trip(S16)
    assert not any(o == "function" for _s, _r, o in _trip(S13)), _trip(S13)
    assert ("differentiation", "PROCESS_ACTION", "become") in _trip(S13), _trip(S13)
    assert not any(o == "uag" for _s, _r, o in _trip(S45)), _trip(S45)
    assert ("termination of translation", "ENABLING_CONDITION_PATIENT", "codon") in _trip(S45)

    # ---- D4: the predicate stays inside the trigger's own clause; data descriptions refuse
    assert _trip(S23) == set(), _trip(S23)
    r23 = extract_predicates_v61(S23)
    assert any(r.reason == "D4_NON_DEFINITIONAL_CONTEXT" for r in r23.refusals), r23.refusals
    assert not any(o == "precede" for _s, _r, o in _trip(S06)), _trip(S06)
    # the coordinated main verb OUTSIDE the when-clause is not the predicate, but the one INSIDE
    # it still is
    assert ("incomplete block", "ENABLING_CONDITION", "reach") in _trip(S41), _trip(S41)
    # a REDUCED RELATIVE ("an enzyme CALLED phosphodiesterase CONVERTS ...") is a relative clause:
    # its participle is not the predicate. v6 banked `termination -> call`.
    t44 = _trip(S44)
    assert not any(o == "call" for _s, _r, o in t44), t44
    assert ("termination of signal", "ENABLING_CONDITION", "convert") in t44, t44
    # ...but a plain past-tense main verb with no later verb is left alone
    assert ("dysfunction", "ENABLING_CONDITION", "die") in _trip(
        "Dysfunction occurs when the cells died"), _trip("Dysfunction occurs when the cells died")

    # ---- D5: on a passive the surface subject is the PATIENT
    assert ("neurodevelopmental disorder", "ENABLING_CONDITION_PATIENT", "development") \
        in _trip(S30), _trip(S30)
    assert not any(r == "ENABLING_CONDITION_AGENT" for _s, r, _o in _trip(S30)), _trip(S30)
    # ACTIVE clauses keep the AGENT role
    act = _trip("Vascular shock occurs when arterioles lose their normal muscular tone")
    assert ("vascular shock", "ENABLING_CONDITION_AGENT", "arteriole") in act, act

    # ---- schema
    for s in (S13, S16, S25, S30, S41, S44, S45):
        for f in extract_predicates_v61(s).facts:
            assert f.relation in RELATIONS_V61, f
            assert f.pattern in PATTERNS_V61, f
    print("[definitional_predicate_v61] self-test PASS")


if __name__ == "__main__":
    _self_test()
