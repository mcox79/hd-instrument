"""hdlab/crosstype_bridge.py -- glass-box CROSS-TYPE definite->name BRIDGE organ.

Promoted from the owner-DONE `route_the_unified_referent_to_its_non_coref_consumers` solution (the "solve it a
different way" win): a definite person role-noun ("the doctor", "the director") binds to a prior NAMED person by an
in-text DESCRIPTIVE CONDITION, resolved with the brain's actual machinery -- NO trained classifier, NO external LLM.
Lifts the affect/goal EXPERIENCER consumer CI-separated on modern gold (GUM): +0.0528 (conservative confidence
threshold) up to +0.086 (liberal), info-free twin loses, survives the live parser at ~0.86 precision.

WHY the unified referent was REFUTED and this is the right mechanism (Ariel 1990 Accessibility Hierarchy): a DEFINITE
DESCRIPTION is a LOW-accessibility marker retrieved by DESCRIPTIVE CONTENT + recency, NOT by the salience cue a pronoun
uses. So the fix is not "route the character card"; it is a content-addressable retrieval keyed on the text's
predication.

THE DEPLOYABLE CONFIG (gated_binds bind_mode="cue_conf"), stacked brain-foundational stages:
  1. PRECISE-CONSTRUCTS predication detector (Stanford precise-constructs sieve; glass-box UD): appos / copula /
     copular-verb / conjunction-shared-subject / detached-appositive / relcl / title / FrameNet-verbal-role +
     unique-gender age/gender narrative recovery -> which named entity the text PREDICATES a role to. 0.96 precision.
  2. ANAPHORICITY / FAMILIARITY gate (Heim familiarity; Poesio-Vieira: ~80% of definites are non-anaphoric) -> fire
     only on anaphoric-safe descriptors (predication-licensed OR an age/gender re-mention).
  3. CUE-BASED ACT-R RETRIEVAL (Lewis-Vasishth) over the named-entity cards: Cf-ranked grammatical-role salience
     (Centering ROLE_PROMINENCE from the parse deprels) + descriptive-content boost (Almor) + gender agreement +
     recency (ACT-R decay).
  4. FULL-REFERENT COMPETITION (Heim novelty-familiarity; DRT: ALL discourse referents compete) -> a cross-type NAME
     bind fires only when a name OUT-COMPETES the same-head COMMON referent (predication boost) OR there is no prior
     same-head common competitor; else abstain (the definite binds the common referent, the floor's job). Closes the
     88.7%-non-anaphoric / 39%-same-head-common over-merge.
  5. RETRIEVAL-CONFIDENCE gate (Heim familiarity = a matching referent is retrievable; McElree SAT low-activation =
     novel) -> abstain when the best NON-predicated candidate's ACT-R activation < `conf_thr`. A SWEPT threshold,
     ONLINE, NO training -- the tunable speed-accuracy operating point (conservative..liberal).

LOCATED NEGATIVE captured in the same solution (do NOT re-pursue): a Wikidata occupation KB adds +0.000 -- people are
re-mentioned by AGE/GENDER/RELATION/context, not catalogued occupation; the right levers are all glass-box or discourse.

INPUT SCHEMA: doc.toks (.gidx/.sent/.idx/.head/.deprel/.upos/.xpos/.form/.lemma) + doc.mentions
(.eid/.mtype/.order-by-enumerate/.start_g/.end_g/.head_g/.gender/.text/.lemma_head) -- the gum_coref.Doc shape (gold),
or a live-parse adapter of the reader's own tokens (the LIVE wiring). Self-contained: ZERO experiments/ imports;
reuses hdlab.salience_binder (ACT-R) + hdlab.commonnoun_binder (head_lemma/person_synset). nltk-WordNet only.

Ported byte-faithfully from experiments/exp_crosstype_precise_constructs_gum_v1.precise_constructs and
experiments/exp_crosstype_upgrades_gum_v1.gated_binds (the deployable cue_conf config).
"""
from __future__ import annotations

__bf_status__ = "BF_SPIRIT"   # BF | BF_SPIRIT | NOT_BF | BF_UNPINNED | BF_UNVERIFIED ; mirrors notes/bf_status_registry.jsonl
__bf_verified__ = "2026-09-09 de-leak landing (strategy first-hand)"
__bf_note__ = "precise-constructs predication + Lewis-Vasishth ACT-R cue retrieval + Almor desc-boost + Heim/DRT full-referent competition + McElree conf gate; NO classifier/LLM; hand-lexicons (_VERB_ROLE/_AGE_GENDER/_COP_VERBS) + swept conf_thr"
__bf_corrections__ = []
from collections import defaultdict

from hdlab.salience_binder import actr_activation, ROLE_PROMINENCE, DEFAULT_DECAY
from hdlab.commonnoun_binder import head_lemma, person_synset


# --- curated glass-box lexicons (verbatim from exp_crosstype_precise_constructs_gum_v1) ---
_ART = {"the", "this", "that", "these", "those"}
_AGE_GENDER = {"boy": "masc", "man": "masc", "gentleman": "masc", "lad": "masc", "guy": "masc", "fellow": "masc",
               "girl": "fem", "woman": "fem", "lady": "fem", "widow": "fem", "child": "any", "kid": "any",
               "person": "any", "individual": "any", "youth": "any", "one": "any", "elder": "any", "baby": "any"}
_COP_VERBS = {"become", "remain", "serve", "work", "act", "turn", "stay", "grow", "prove", "appoint",
              "elect", "name", "call", "make", "be", "get"}
# VERBAL role predication (FrameNet-style: a subject NAME performing a role-defining action licenses the role).
_VERB_ROLE = {
    "write": {"author", "writer", "novelist"}, "direct": {"director"}, "star": {"star", "actor", "actress"},
    "compose": {"composer"}, "paint": {"painter"}, "found": {"founder"}, "teach": {"teacher", "professor"},
    "sing": {"singer", "vocalist"}, "edit": {"editor"}, "produce": {"producer"}, "design": {"designer"},
    "invent": {"inventor"}, "sculpt": {"sculptor"}, "lead": {"leader"}, "coach": {"coach"}, "captain": {"captain"},
    "govern": {"governor"}, "command": {"commander"}, "publish": {"publisher"}, "photograph": {"photographer"},
    "conduct": {"conductor"}, "choreograph": {"choreographer"}, "pilot": {"pilot"}, "preach": {"preacher"},
    "pastor": {"pastor"}, "translate": {"translator"}, "narrate": {"narrator"}, "host": {"host"},
    "manage": {"manager"}, "chair": {"chairman", "chair"}, "captained": {"captain"},
}
# ORG/THING role-nouns WordNet marks as person-capable but which denote non-persons (person-detector cleanup)
_NONPERSON_STOP = {"publisher", "respondent", "petitioner", "appellant", "operator", "court", "study", "major",
                   "minor", "subject", "object", "party", "board", "company", "agency", "committee", "council",
                   "state", "government", "administration", "department", "office", "commission", "corporation",
                   "team", "club", "band", "group", "family", "public", "press", "media", "outlet", "journal",
                   "conservatory", "institute", "university", "college", "school", "church", "temple"}

# --- bind-stage constants (verbatim from exp_crosstype_upgrades_gum_v1) ---
_DESC_BOOST = 100.0     # descriptive-content is a strong retrieval cue that overrides salience (Almor 1999)
_ORD_SUP = {"first", "second", "third", "fourth", "fifth", "last", "next", "only", "best", "worst", "most",
            "largest", "biggest", "greatest", "smallest", "sole", "main", "chief", "primary", "former", "latter"}
# WSD-hard legal role-nouns whose FIRST WordNet sense is a person but which denote ORGS in legal register.
_LEGAL_ORG_ROLE = {"respondent", "petitioner", "appellant", "proponent", "plaintiff", "defendant", "major",
                   "umpire", "complainant", "applicant"}
_ANIMACY_CACHE = {}


def is_person_role(L):
    """ANIMACY via the FREQUENCY PRIOR (the brain's default sense): a role-noun denotes a PERSON iff its MOST-COMMON
    WordNet noun sense is in the person lexical file (noun.person). Anderson base-rate; ATL lexical-semantic type."""
    if L in _ANIMACY_CACHE:
        return _ANIMACY_CACHE[L]
    out = False
    if L not in _LEGAL_ORG_ROLE:
        try:
            from nltk.corpus import wordnet as wn
            ss = wn.synsets(L, pos="n")
            out = bool(ss) and ss[0].lexname() == "noun.person"
        except Exception:
            out = False
    _ANIMACY_CACHE[L] = out
    return out


def _mention_role(by_gidx, m):
    """The mention's CENTERING Cf role from its head token's PARSE deprel: subject > possessive > object > other."""
    t = by_gidx.get(m.head_g)
    if t is None:
        return "OTHER"
    full = (t.deprel or "")
    dep = full.split(":")[0]
    if dep in ("nsubj", "csubj"):
        return "SUBJECT"
    if "poss" in full or dep == "nmod" and "poss" in full:
        return "POSSESSIVE"
    if dep in ("obj", "iobj"):
        return "OBJECT"
    return "OTHER"


def _tok_maps(doc):
    by_gidx = {t.gidx: t for t in doc.toks}
    by_sent_idx = {(t.sent, t.idx): t.gidx for t in doc.toks}
    return by_gidx, by_sent_idx


def _span_maps(doc):
    """gidx -> (eid, mtype, head_gidx); and for each mention, its head gidx."""
    tok2ment = {}
    for m in doc.mentions:
        for g in range(m.start_g, m.end_g + 1):
            tok2ment.setdefault(g, (m.eid, m.mtype, m.head_g))
        tok2ment[m.head_g] = (m.eid, m.mtype, m.head_g)
    return tok2ment


def _person_entities(doc, gaz):
    out = set()
    gmap = {"m", "f"}
    by_eid = defaultdict(list)
    for m in doc.mentions:
        by_eid[m.eid].append(m)
    for eid, mm in by_eid.items():
        person = False
        for m in mm:
            if m.gender in gmap:
                person = True; break
            if m.mtype == "name" and any(t in gaz for t in m.text.lower().split()):
                person = True; break
            if m.mtype == "common" and head_lemma(m.lemma_head) not in _NONPERSON_STOP \
                    and person_synset(head_lemma(m.lemma_head)) is not None:
                person = True; break
        if person:
            out.add(eid)
    return out


def precise_constructs(doc, gaz):
    """Glass-box: return (role_lemma -> set(named gold-entity ids linked by an in-text precise construct), ent_person).
    Uses UD syntax to link a ROLE-noun to a NAME (the descriptive condition); person-cleaned."""
    by_gidx, by_sent_idx = _tok_maps(doc)
    tok2ment = _span_maps(doc)

    def head_gidx(t):
        return by_sent_idx.get((t.sent, t.head))

    def is_name_tok(g):
        info = tok2ment.get(g)
        return info is not None and info[1] == "name"

    def name_eid(g):
        info = tok2ment.get(g)
        return info[0] if info else None

    def role_ok(lemma):
        return lemma not in _NONPERSON_STOP and person_synset(lemma) is not None

    licensed = defaultdict(set)

    def link(role_gidx, name_gidx):
        rt = by_gidx.get(role_gidx)
        if rt is None or not is_name_tok(name_gidx):
            return
        rl = head_lemma(rt.lemma or rt.form)
        if role_ok(rl):
            licensed[rl].add(name_eid(name_gidx))

    # index children by head for fast lookup; relative-clause antecedents
    children = defaultdict(list)
    for t in doc.toks:
        hg = head_gidx(t)
        if hg is not None:
            children[hg].append(t)
    relcl_antec = {}
    for t in doc.toks:
        if (t.deprel or "").split(":")[0] == "acl":
            hg = head_gidx(t)
            if hg is not None and is_name_tok(hg):
                relcl_antec[t.gidx] = hg                        # "Dvorak, who was the director" -> was.head=Dvorak

    def subj_to_name(s, verb_gidx):
        if s is None:
            return None
        if is_name_tok(s):
            return s
        st = by_gidx.get(s)
        if st is not None and st.form.lower() in ("who", "which", "that") and verb_gidx in relcl_antec:
            return relcl_antec[verb_gidx]
        return None

    def find_subject_name(verb_gidx, depth=0):
        """The NAME subject of a verb -- direct nsubj/nsubj:pass, a relative-pronoun antecedent, or the SHARED
        subject of a conjunction ('Dvorak moved ... and became the director' -> the nsubj of 'moved')."""
        if verb_gidx is None or depth > 3:
            return None
        for c in children.get(verb_gidx, ()):
            if (c.deprel or "").split(":")[0] == "nsubj":
                nm = subj_to_name(c.gidx, verb_gidx)
                if nm is not None:
                    return nm
        vt = by_gidx.get(verb_gidx)
        if vt is not None and (vt.deprel or "").split(":")[0] == "conj":
            return find_subject_name(head_gidx(vt), depth + 1)   # conjunction-shared subject
        return None

    role_linked = {}                                            # role gidx -> name gidx (for conj propagation)

    def try_link(role_gidx, name_gidx):
        if name_gidx is not None:
            link(role_gidx, name_gidx); role_linked[role_gidx] = name_gidx

    for t in doc.toks:
        dep = (t.deprel or "").split(":")[0]
        hg = head_gidx(t)
        if not (t.upos == "NOUN" and role_ok(head_lemma(t.lemma or t.form))):
            # non-role tokens: still handle a NAME that is appos to a role noun ("the director, Dvorak")
            if dep == "appos" and hg is not None and is_name_tok(t.gidx):
                bt = by_gidx.get(hg)
                if bt is not None and bt.upos == "NOUN" and role_ok(head_lemma(bt.lemma or bt.form)):
                    try_link(hg, t.gidx)
            continue
        gt = by_gidx.get(hg) if hg is not None else None
        # APPOS: role <-appos-> name
        if dep == "appos" and hg is not None and is_name_tok(hg):
            try_link(t.gidx, hg); continue                        # "Dvorak, the director"
        # TITLE: role -flat/compound-> name
        if dep in ("flat", "compound") and hg is not None and is_name_tok(hg):
            try_link(t.gidx, hg); continue                        # "President Obama"
        # COPULA: role has a `cop` child -> its (possibly conj-shared) subject name
        if any((c.deprel or "").split(":")[0] == "cop" for c in children.get(t.gidx, ())):
            try_link(t.gidx, find_subject_name(t.gidx)); continue
        # COPULAR VERB: role is obj/xcomp/obl of become/serve/appoint/elect... -> that verb's subject name
        if dep in ("obj", "xcomp", "obl") and gt is not None and head_lemma(gt.lemma or gt.form) in _COP_VERBS:
            try_link(t.gidx, find_subject_name(hg)); continue
        # DETACHED NOMINAL APPOSITIVE: a determiner-headed role noun as advcl/acl of a verb whose subject is a
        # name ("L'Enfant was born ..., the third child and second son of ...") -- secondary predication.
        if dep in ("advcl", "acl") and gt is not None and gt.upos in ("VERB", "AUX") and \
                any((c.deprel or "").split(":")[0] == "det" for c in children.get(t.gidx, ())):
            try_link(t.gidx, find_subject_name(hg)); continue
    # CONJ PROPAGATION: a role noun conjoined to a linked role noun shares the predication ("child and son")
    for t in doc.toks:
        if (t.deprel or "").split(":")[0] == "conj" and t.upos == "NOUN" and \
                role_ok(head_lemma(t.lemma or t.form)):
            hg = head_gidx(t)
            if hg in role_linked:
                link(t.gidx, role_linked[hg])
    # VERBAL ROLE PREDICATION: a VERB in _VERB_ROLE with a subject NAME licenses that role for the name.
    for t in doc.toks:
        if t.upos in ("VERB", "AUX"):
            roles = _VERB_ROLE.get(head_lemma(t.lemma or t.form))
            if not roles:
                continue
            nm = find_subject_name(t.gidx)
            if nm is None:
                continue
            eid = name_eid(nm)
            for r in roles:
                if role_ok(r):
                    licensed[r].add(eid)
    # named-entity personhood filter: keep only entities that look like persons
    ent_person = _person_entities(doc, gaz)
    return {rl: {e for e in es if e in ent_person} for rl, es in licensed.items()}, ent_person


def gated_binds(doc, gaz, bind_mode="unique", margin=2, restrict_gold=True, animacy_wn=False, conf_thr=0.0):
    """Bridge binds -> (pop, fired, correct, {role_midx: eid}). The DEPLOYABLE config is bind_mode='cue_conf',
    margin=0.5, restrict_gold=False (deployment population), conf_thr=<swept operating point>. See module docstring for
    the five stacked stages. Ported byte-faithfully from exp_crosstype_upgrades_gum_v1.gated_binds."""
    def _person_def(L):
        return is_person_role(L) if animacy_wn else (L not in _NONPERSON_STOP and person_synset(L) is not None)
    licensed, ent_person = precise_constructs(doc, gaz)
    ms = doc.mentions
    by_gidx = {t.gidx: t for t in doc.toks}
    _bysi = {(t.sent, t.idx): t.gidx for t in doc.toks}
    _children = defaultdict(list)
    for _t in doc.toks:
        _hg = _bysi.get((_t.sent, _t.head))
        if _hg is not None:
            _children[_hg].append(_t)

    def _establishing_modifier(head_g):
        """Hawkins 1978 / Bean-Riloff 1999: a RESTRICTIVE establishing modifier (relcl, post-head PP/of,
        superlative/ordinal) marks a definite as FIRST-MENTION / discourse-new -> ABSTAIN."""
        h = by_gidx.get(head_g)
        if h is None:
            return False
        for c in _children.get(head_g, ()):
            full = (c.deprel or ""); dep = full.split(":")[0]
            if full == "acl:relcl" or dep == "acl":
                return True                                    # "the doctor WHO treated her"
            if dep == "nmod" and c.idx > h.idx:
                return True                                    # "the director OF the Conservatory" (post-head)
            if dep == "amod" and (c.xpos == "JJS" or (c.form or "").lower() in _ORD_SUP):
                return True                                    # superlative "the best/largest"
            if dep == "nummod" or (c.form or "").lower() in _ORD_SUP:
                return True                                    # ordinal "the first/second/only"
        return False

    firstname = {}
    name_gender_order = []                                    # (order, eid, gender) -- MATCHES the landable cell
    name_gender = {}
    name_hist = defaultdict(list)                            # eid -> [(order, role)] name mentions (Cf-ranked ACT-R)
    common_head_orders = defaultdict(list)                   # head lemma -> [orders of COMMON mentions] (the
    for i, m in enumerate(ms):                               #   same-head COMMON referents that compete (DRT full pool)
        if m.mtype == "common":
            common_head_orders[head_lemma(m.lemma_head)].append(i)
        if m.mtype == "name" and m.eid in ent_person:
            firstname.setdefault(m.eid, i)
            name_gender_order.append((i, m.eid, m.gender))
            name_hist[m.eid].append((i, _mention_role(by_gidx, m)))
            if m.gender in ("m", "f") and m.eid not in name_gender:
                name_gender[m.eid] = "masc" if m.gender == "m" else "fem"
    pop = fired = correct = 0
    binds = {}
    for i, m in enumerate(ms):
        if m.mtype != "common":
            continue
        L = head_lemma(m.lemma_head); toks = m.text.lower().split()
        if not toks or toks[0] not in _ART or not _person_def(L):
            continue
        if restrict_gold:
            if m.eid not in ent_person or m.eid not in firstname or firstname[m.eid] >= i:
                continue                                       # CEILING population: gold entity is a named person, prior
        else:
            if not any(o < i for (o, _e, _g) in name_gender_order):
                continue                                       # DEPLOYMENT: any person-definite with SOME prior name
        pop += 1
        named = licensed.get(L, set())
        bound = None
        if bind_mode in ("cue_retrieval", "cue_gated", "cue_competed", "cue_novelty", "cue_conf"):
            # THE UNIFIED BRAIN-FOUNDATIONAL BIND: ONE cue-based content-addressable retrieval (Lewis-Vasishth ACT-R)
            # over the entity cards -- descriptive-content boost (Almor) + Cf-ranked grammatical-role salience
            # (Centering, ROLE_PROMINENCE from the PARSE deprels) + gender agreement (filter) + recency (ACT-R decay).
            # Commit to the argmax only if it dominates the runner-up by `margin` activation nats (else abstain).
            ag = _AGE_GENDER.get(L)                            # gender constraint of an age/gender descriptor, else None
            # cue_gated: the ANAPHORICITY/FAMILIARITY gate -- fire only on anaphoric-SAFE descriptors
            # (predication-licensed OR an age/gender re-mention), NOT bare occupation role-nouns.
            gate_ok = not (bind_mode == "cue_gated" and not named and ag is None)
            # cue_competed -- FULL-REFERENT COMPETITION (Heim; DRT: ALL referents compete). A cross-type NAME bind
            # fires only when a name OUT-COMPETES the same-head COMMON referent (desc boost) OR there is NO prior
            # same-head common competitor; else ABSTAIN from the name merge (the definite binds the common referent).
            if bind_mode in ("cue_competed", "cue_novelty", "cue_conf"):
                prior_common = any(o < i for o in common_head_orders.get(L, ()))
                if not named and prior_common:
                    gate_ok = False                            # a same-head common referent wins the competition
            # cue_novelty -- ADD the Heim/Hawkins NOVELTY-FAMILIARITY gate (restrictive establishing modifier).
            if bind_mode == "cue_novelty" and not named and _establishing_modifier(m.head_g):
                gate_ok = False
            cands = []
            for e, hist in (name_hist.items() if gate_ok else ()):
                priors = [(o, r) for (o, r) in hist if o < i]
                if not priors:
                    continue
                if ag is not None and ag != "any":
                    g = name_gender.get(e)
                    if g is not None and g != ag:
                        continue                               # gender-agreement filter
                A = actr_activation(priors, float(i), DEFAULT_DECAY, ROLE_PROMINENCE)
                if e in named:
                    A += _DESC_BOOST                           # descriptive content overrides salience (Almor 1999)
                cands.append((A, e))
            if cands:
                cands.sort(reverse=True)
                dominates = len(cands) == 1 or (cands[0][0] - cands[1][0]) >= margin
                # cue_conf -- the BRAIN'S novelty-familiarity signal is the RETRIEVAL'S OWN CONFIDENCE (Heim
                # familiarity = a matching referent is retrievable; McElree low-activation = NO referent found ->
                # NOVEL). ABSTAIN when the best NON-predicated candidate's ACT-R activation is below conf_thr.
                if bind_mode == "cue_conf" and cands[0][0] < _DESC_BOOST and cands[0][0] < conf_thr:
                    dominates = False
                if dominates:
                    bound = cands[0][1]
        elif named:
            bound = m.eid if m.eid in named else next(iter(named))
        else:
            ag = _AGE_GENDER.get(L)
            if ag is not None:
                cand_recency = {}
                for (o, e, g) in name_gender_order:
                    if o < i and (ag == "any" or g == "" or g == ag):
                        cand_recency[e] = max(cand_recency.get(e, -1), o)
                if bind_mode == "unique":
                    if len(cand_recency) == 1:
                        bound = next(iter(cand_recency))
                else:                                           # recency_margin
                    ranked = sorted(((o, e) for e, o in cand_recency.items()), reverse=True)
                    if len(ranked) == 1:
                        bound = ranked[0][1]
                    elif len(ranked) >= 2 and (ranked[0][0] - ranked[1][0]) >= margin:
                        bound = ranked[0][1]
        if bound is not None:
            fired += 1; binds[i] = bound
            if bound == m.eid:
                correct += 1
    return pop, fired, correct, binds


# --- public convenience API ---
predication_licenses = precise_constructs


def crosstype_bridge_links(doc, gaz, *, conf_thr, margin=0.5, mode="cue_conf", restrict_gold=False):
    """THE deployable entry: return {role_midx: name_eid} cross-type definite->name links at the given confidence
    operating point. conf_thr is the tunable speed-accuracy threshold (higher = more conservative)."""
    _pop, _fired, _correct, binds = gated_binds(
        doc, gaz, bind_mode=mode, margin=margin, restrict_gold=restrict_gold, conf_thr=conf_thr)
    return binds


def _self_test():
    """Corpus-free structural self-test (nltk-WordNet only): proves the precise-constructs COPULA detector licenses a
    role->name, and the deployable cue_conf bind resolves an anaphoric definite ('The doctor' -> the named Elizabeth).
    The full CI-separated experiencer lift is proven by verification/test_crosstype_landable.py on GUM."""
    from types import SimpleNamespace as NS

    def tok(gidx, sent, idx, head, deprel, upos, form, lemma, xpos="NN"):
        return NS(gidx=gidx, sent=sent, idx=idx, head=head, deprel=deprel, upos=upos, form=form, lemma=lemma, xpos=xpos)

    def men(eid, mtype, start_g, end_g, head_g, gender, text, lemma_head):
        return NS(eid=eid, mtype=mtype, start_g=start_g, end_g=end_g, head_g=head_g, gender=gender,
                  text=text, lemma_head=lemma_head)

    # "Elizabeth is a doctor . The doctor arrived ."
    toks = [tok(0, 0, 1, 4, "nsubj", "PROPN", "Elizabeth", "Elizabeth", "NNP"),
            tok(1, 0, 2, 4, "cop", "AUX", "is", "be", "VBZ"),
            tok(2, 0, 3, 4, "det", "DET", "a", "a", "DT"),
            tok(3, 0, 4, 0, "root", "NOUN", "doctor", "doctor"),
            tok(4, 1, 1, 2, "det", "DET", "The", "the", "DT"),
            tok(5, 1, 2, 3, "nsubj", "NOUN", "doctor", "doctor"),
            tok(6, 1, 3, 0, "root", "VERB", "arrived", "arrive", "VBD")]
    mentions = [men(1, "name", 0, 0, 0, "f", "Elizabeth", "elizabeth"),
                men(1, "common", 2, 3, 3, "", "a doctor", "doctor"),
                men(1, "common", 4, 5, 5, "", "The doctor", "doctor")]
    doc = NS(toks=toks, mentions=mentions)
    gaz = set()

    lic, ent_person = precise_constructs(doc, gaz)
    assert lic.get("doctor") == {1}, "COPULA detector should license doctor->Elizabeth(eid 1): %s" % dict(lic)
    assert 1 in ent_person, "Elizabeth should be a person entity"

    pop, fired, correct, binds = gated_binds(doc, gaz, bind_mode="cue_conf", margin=0.5, restrict_gold=False, conf_thr=0.0)
    assert binds == {2: 1}, "the definite 'The doctor' (midx 2) should bind to Elizabeth (eid 1): %s" % binds
    assert correct == 1, "the bind should be gold-correct"
    assert crosstype_bridge_links(doc, gaz, conf_thr=0.0) == {2: 1}, "convenience API should match"
    print("SELFTEST PASS: precise-constructs copula licensing + cue_conf anaphoric definite->name bind function.")


if __name__ == "__main__":
    _self_test()
