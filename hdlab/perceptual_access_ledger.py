"""perceptual_access_ledger -- the brain-faithful OBSERVATION-CUE front-end for Theory of Mind.

Replaces the landed lexical keyword extractor (extract_observed_from_text, 0.808) with a glass-box
implementation of the brain's actual computation for "did agent A perceive / come to know event E?".

BRAIN FRAME (see notes/problems/theory_of_mind_residual_is_the_observation_cue_front_end/BRAIN_MECHANISM_SPEC.md;
4-pass web-verified literature drill 2026-08-28):

  The naive `observed = co_present AND available OR informed` is right in outline, WRONG in structure. The
  literature (Butterfill & Apperly 2013, Mind&Language 28:606-637 -- the most directly formalized source)
  converges on a STICKY, procedurally-updated REGISTRATION LEDGER, not a boolean re-evaluated at query time:

    location_register[X] = OPEN presence-interval (location_node, t_start, ->) per entity   -- Zwaan&Radvansky
                           event-indexing SPACE dimension; Speer/Zacks 2009 (parahippocampal+hippocampus fire
                           on a character's location-change during ordinary reading).
    registration[A][E]   = (E's last-registered state, t) -- STICKY.
    RULE 1 (perceptual): if presence_check(A, window(E))  AND  E in field(A, window(E))  -> register
    RULE 2 (testimony):  if A in addressees(utterance asserting E)                        -> register
    knows(A,E) = registration matches truth;  false_belief = registration is STALE.

  => `observed` (the bit the landed belief_partition gate consumes) == "RULE 1 or RULE 2 fired for A on E".

PINNED design choices (copy the operation):
  * Presence is a temporal INTERVAL (departure closes, arrival opens); presence_check = interval containment
    (Allen). Handles "present before, gone during" -- the exact case the stateless keyword list cannot.
  * Motion updates location by reading the realized PATH SATELLITE / Source-Goal-Path PP ("out", "into X",
    "back"), NOT a manner-verb whitelist (Talmy 1985/2000; Papafragou 2008; FrameNet ~15-20 frames do NOT
    collapse to a small primitive set). So "she florped out" still departs via "out". Goal-over-Source
    asymmetry (Lakusta&Landau 2005): Goal realized -> present at Goal; Source only -> absent from Source.
  * The OCCLUSION / field gate is the precisely-diagnosed NLP wall (FANToM Kim 2023 Belief>>InfoAccess;
    Ullman 2023 transparent-bag) -- built explicitly: not-in-scene / asleep / blindfold / dark / back-turned.
  * Testimony is an independent, source-tagged channel (Harris&Koenig 2006).

OUR-INVENTION-UNDER-TEST (labelled): the exact Path-satellite lexicon + the Allen-interval implementation +
  the addressee->knows rule (literature gaps we fill; parameters swept, operation copied).

GLASS-BOX: pure symbolic inference over a spaCy dependency parse (the syntactic front-end, same as the litbank
  reader cells). NO external LLM, NO network at inference. The parse is perception-of-syntax; the ledger is the
  glass-box situation-model inference. ASCII only.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

# ---------------------------------------------------------------------------
# Path-satellite / deixis lexicons (Talmy PATH lives in the SATELLITE, not the verb root).
# These are PATH primitives (Source/Goal/deixis), NOT a manner-verb list -- the whole point.
# ---------------------------------------------------------------------------
# Satellites / prepositions that realize a GOAL (arrive AT ground) -> agent PRESENT at ground.
GOAL_PREPS = {"into", "in", "inside", "onto", "to", "toward", "towards", "unto", "within"}
GOAL_PARTICLES = {"in", "back", "inside", "home"}
# Satellites that realize a SOURCE / away (depart FROM ground) -> agent ABSENT from ground.
SOURCE_PREPS = {"from", "out of", "off"}
SOURCE_PARTICLES = {"out", "away", "off", "outside", "forth", "aside", "abroad"}
# Deixis on the motion verb (Talmy's Path deixis component). come/return = TOWARD (arrive at deictic centre
# = the narrated scene); go/leave/depart/withdraw/retire/set-out = AWAY from it.
DEIXIS_TOWARD = {"come", "came", "return", "returned", "arrive", "arrived", "reenter", "reentered",
                 "re-enter", "enter", "entered", "approach", "approached", "rejoin", "rejoined"}
DEIXIS_AWAY = {"go", "went", "gone", "leave", "left", "depart", "departed", "withdraw", "withdrew",
               "retire", "retired", "exit", "exited", "quit", "flee", "fled", "slip"}
# Predicate/adjunct ABSENCE states ("was gone/away/out/abroad", "had gone to bed").
ABSENCE_PRED = {"gone", "away", "out", "outside", "abroad", "absent", "off"}

# ---------------------------------------------------------------------------
# PERCEPTUAL FIELD (Butterfill&Apperly "field"; the pinned NLP wall -- FANToM/Ullman). Finer than a single
# gate: a PER-MODALITY field with a small OCCLUDER ONTOLOGY (from the occlusion research drill). vision needs
# light + line-of-sight + not-in-a-closed-opaque-container + attending + awake; audition penetrates darkness &
# thin barriers & inattention, needs earshot + a non-silent event + awake; touch needs contact + awake.
# For an object-LOCATION-MOVE (property = "occurrence"), vision OR audition can reveal it -- so a NOISY move in
# the dark IS perceived where a SILENT one is not (the discriminator a keyword list cannot make).
# ---------------------------------------------------------------------------
STATE_UNAVAIL_CUES = [  # asleep/unconscious -> ALL modalities off (awake=False)
    r"\basleep\b", r"\bslept\b", r"\bsleeping\b", r"\bdozed\b", r"\bdozing\b", r"\bdrowsed\b",
    r"\bslumber(?:ed|ing|s)?\b", r"\binsensible\b", r"\bin a (?:stupor|trance|faint|swoon)\b", r"\babed\b",
    r"\bunconscious\b", r"\bfainted\b", r"\bswoon(?:ed|ing)?\b", r"\bsenseless\b",
]
WAKE_CUES = [r"\bwoke\b", r"\bawoke\b", r"\bawakened\b", r"\bawakening\b", r"\bstirred\b", r"\bcame to\b",
             r"\bopened (his|her|their) eyes\b", r"\bsat up\b"]
DARK_CUES = [  # removes VISION only (audition intact)
    r"\bin the dark\b", r"\bin darkness\b", r"\bpitch[- ]dark\b", r"\bpitch black\b", r"\bin the gloom\b",
    r"\bdarkness\b", r"\blights? (?:were )?(?:out|off)\b", r"\bcandle (?:was )?(?:out|blown out)\b",
    r"\bunlit\b", r"\bcould not see\b", r"\bcouldn't see\b", r"\bblindfold", r"\beyes (?:were )?(?:closed|shut|bandaged)\b",
    r"\bclosed (his|her|their) eyes\b", r"\bhad (his|her) eyes shut\b",
]
LIGHT_CUES = [r"\blit\b", r"\blamp\b", r"\bcandle\b", r"\bin the light\b", r"\bdaylight\b", r"\bsunlight\b",
              r"\bmoonlight\b", r"\bopened (his|her|their) eyes\b"]
INATTENTION_CUES = [  # present + lit but not attending -> vision off (audition may still catch a salient event)
    r"\bback (?:was )?turned\b", r"\bturned (his|her|their) back\b", r"\bwith (his|her) back to\b",
    r"\bnot looking\b", r"\blooked away\b", r"\bgazing (?:out|away|elsewhere)\b", r"\bstaring (?:out|away)\b",
    r"\babsorbed in\b", r"\bengrossed in\b", r"\bintent (?:on|upon)\b", r"\bpreoccupied\b", r"\bdistracted\b",
    r"\bbusy (?:with|at|over)\b", r"\bburied in (?:his|her|a|the) (?:book|work|paper|letter)\b", r"\blost in thought\b",
]
ATTEND_CUES = [r"\bturned (round|around|back)\b", r"\bturned to\b", r"\blooked up\b", r"\bglanced\b", r"\blooked round\b"]
BARRIER_CUES = [  # opaque barrier between agent and event -> vision off (audition may pass unless soundproof)
    r"\bbehind (?:a|the|some) (?:[a-z]+ )?(screen|curtain|wall|partition|door|hedge|pillar|tree|bush|arras|drapery|blind|shutter)\b",
    r"\bhidden from (his|her|their) (view|sight|eyes)\b", r"\bout of (his|her|their) (view|sight)\b",
    r"\bconcealed from\b", r"\bunseen by\b", r"\bscreen(ed)? (him|her|them) from\b", r"\bhidden behind\b",
]
# Container opacity x state -- the transparent-bag (Ullman) case. A CLOSED OPAQUE container hides its contents
# from vision even when co-located; a TRANSPARENT or OPEN one does not.
TRANSPARENT_CUES = [r"\btransparent\b", r"\bglass\b", r"\bsee[- ]through\b", r"\bclear (?:jar|bottle|glass|case)\b",
                    r"\bopen\b", r"\buncovered\b", r"\blidless\b", r"\bajar\b", r"\bwithout a lid\b"]
CLOSED_OPAQUE_CUES = [r"\bclosed\b", r"\bshut\b", r"\bsealed\b", r"\block(?:ed)?\b", r"\bcovered\b", r"\blidded\b",
                      r"\bwrapped\b", r"\bwith the lid (?:on|down|closed)\b", r"\bopaque\b"]
# Event loudness -- gates AUDITION.
SILENT_CUES = [r"\bsilent(?:ly)?\b", r"\bquiet(?:ly)?\b", r"\bnoiseless(?:ly)?\b", r"\bwithout a sound\b",
               r"\bstealth(?:ily|y)\b", r"\bsoftly\b", r"\bon tiptoe\b", r"\bhush(?:ed)?\b", r"\bgently\b"]
LOUD_CUES = [r"\bloud(?:ly)?\b", r"\bwith a crash\b", r"\bcrash(?:ed|ing)?\b", r"\bbang(?:ed|ing)?\b",
             r"\bclatter(?:ed|ing)?\b", r"\bnoise\b", r"\bnoisy\b", r"\bthud\b", r"\bslam(?:med)?\b",
             r"\bshout(?:ed|ing)?\b", r"\bcry(?:ing)?\b", r"\bsmash(?:ed)?\b", r"\brattl(?:ed|ing)\b"]

# ---------------------------------------------------------------------------
# Testimony route (independent, source-tagged channel: Harris&Koenig 2006).
# ---------------------------------------------------------------------------
def _testimony_patterns(agent_re: str) -> List[str]:
    a = agent_re
    return [
        rf"\btold {a}\b", rf"\b{a} (was|had been) told\b", rf"\b{a} (was|had been) informed\b",
        rf"\binformed {a}\b", rf"\b{a} (heard|learned|learnt|discovered|found out|was aware)\b",
        rf"\b{a} (had )?(heard|learned|learnt) (that|of|about)\b", rf"\bsaid to {a}\b",
        rf"\b{a} (came to know|got wind|was let in)\b", rf"\bwarned {a}\b", rf"\b{a} (was )?warned\b",
    ]

_PRON = {"he", "she", "they", "him", "her", "them", "his", "hers", "their"}


# ---------------------------------------------------------------------------
# RULE 0 -- EXPLICIT narrator epistemic statement about the agent. The narrator directly asserting a mind-state
# ("unbeknownst to her", "she did not see it", "he watched") is the MOST DIRECT evidence a reader has, and a
# faithful reader uses it (it is testimony from the narrator). Highest priority; the marker NEAREST the event wins.
# Copies the developmental "seeing/being-told = knowing" gate at the surface where the text states it outright.
# ---------------------------------------------------------------------------
def _epistemic_patterns(agent_re: str):
    a = agent_re
    neg = [  # explicit NOT-knowing / NOT-perceiving about the agent -> observed = False
        rf"\bunbeknown(?:st)? to {a}\b", rf"\bunknown to {a}\b", rf"\bwithout {a}'?s? knowledge\b",
        rf"\b{a} (?:did not|did n't|didn't|never|could not|couldn't) (?:see|saw|notice|noticed|know|knew|"
        rf"perceive|observe|suspect|dream|realise|realize|hear|heard|mark|witness)\b",
        rf"\b{a} knew nothing\b", rf"\b{a} (?:had|has) no (?:idea|notion|knowledge|suspicion|inkling)\b",
        rf"\blittle did {a} (?:know|dream|suspect|think|imagine)\b",
        rf"\b{a} (?:was|were|remained|seemed) (?:unaware|ignorant|oblivious|in the dark|none the wiser)\b",
        rf"\bunseen by {a}\b", rf"\bunnoticed by {a}\b", rf"\bunobserved by {a}\b",
        rf"\b{a} failed to (?:see|notice|observe|perceive)\b", rf"\bnone the wiser\b",
    ]
    pos = [  # explicit knowing / witnessing about the agent -> observed = True
        rf"\b{a} (?:saw|watched|beheld|witnessed|observed|noticed|perceived|spied|marked|espied)\b",
        rf"\bbefore {a}'?s? (?:eyes|face|very eyes)\b", rf"\bin {a}'?s? presence\b",
        rf"\b{a} (?:knew|was aware|were aware|realised|realized|understood|noted|had seen|had watched)\b",
        rf"\bin full view of {a}\b", rf"\b{a} (?:looked on|was present|stood by and)\b",
    ]
    return neg, pos


@dataclass
class PresenceState:
    """A tracked agent's running situation-model state (the location register + the per-modality field)."""
    present: bool = True            # in the narrated scene (co-present with events there) -- default present
    location: Optional[str] = None  # named location node if known (else the deictic scene)
    awake: bool = True              # asleep/unconscious -> ALL modalities off
    lit: bool = True                # darkness -> VISION off (audition intact)
    attending: bool = True          # back-turned/absorbed -> VISION off (audition may still catch a salient event)
    interval_open_at: int = 0       # clause index the current presence interval opened at


@dataclass
class LedgerTrace:
    """Glass-box trace of one observed(A,E) decision -- every sub-decision is inspectable."""
    agent: str = ""
    event_idx: int = -1
    present_at_event: bool = True
    available_at_event: bool = True
    informed: bool = False
    observed: bool = True
    per_clause: List[Tuple[int, str, str]] = field(default_factory=list)  # (idx, signal, detail)
    reason: str = ""


class PerceptualAccessLedger:
    """Glass-box perceptual-access registration ledger over a spaCy parse.

    Usage:
        led = PerceptualAccessLedger(nlp)
        trace = led.observed(text, agent_aliases=["Anna", "she", "her"], event_object="marble",
                             event_location=None, scene_reset_at=None)
        cue = trace.observed  # True iff RULE 1 (co-present & field-open at the move) or RULE 2 (informed) fired
    """

    def __init__(self, nlp=None):
        self._nlp = nlp  # spaCy Language (lazy: caller passes it so one model is shared across a run)

    # ---- parsing -------------------------------------------------------
    def _nlp_or_load(self):
        if self._nlp is None:
            import spacy
            self._nlp = spacy.load("en_core_web_sm")
        return self._nlp

    # ---- subject / agent resolution -----------------------------------
    @staticmethod
    def _alias_regex(agent_aliases: Sequence[str]) -> re.Pattern:
        parts = sorted({re.escape(a.strip()) for a in agent_aliases if a.strip()}, key=len, reverse=True)
        return re.compile(r"\b(" + "|".join(parts) + r")\b", re.IGNORECASE)

    @staticmethod
    def _root_subjects(sent):
        """The MAIN-clause subject token(s): the nsubj/nsubjpass of the ROOT verb (+ its conjuncts). This is
        the agent's OWN action -- a subordinate 'while Anna watched' subject is NOT the main subject and must
        not count as the agent moving (the bug that mislocated the event on 'while Anna watched')."""
        root = None
        for t in sent:
            if t.dep_ == "ROOT":
                root = t
                break
        if root is None:
            return []
        subs = [t for t in sent if t.dep_ in ("nsubj", "nsubjpass") and t.head == root]
        # include conjoined subjects ("Anna and Ben went")
        out = list(subs)
        for s in subs:
            out += [c for c in s.children if c.dep_ == "conj"]
        if not out:
            # PARSE-FAILURE fallback (en_core_web_sm mis-tags sentence-initial proper nouns, e.g. "Molly"
            # as ADV): take the leading nominal in English SVO subject position -- the first alphabetic,
            # non-function token before the ROOT verb. On the corpus path GOLD coref removes this need.
            for t in sent:
                if t.i >= root.i:
                    break
                if t.is_punct or t.dep_ in ("mark", "cc", "det", "prep", "punct") or t.pos_ in ("SCONJ", "CCONJ", "ADP", "DET"):
                    continue
                out = [t]
                break
        return out

    def _subject_is_agent(self, sent, agent_aliases: Sequence[str], name_head: str) -> bool:
        """True if the MAIN-clause subject of `sent` coref-resolves to the tracked agent. Glass-box coref
        proxy: the ROOT subject is the agent NAME or a 3rd-person pronoun defaulting to the protagonist by
        recency/salience (the state_of_mind overlay heuristic). For the corpus path, gold coref replaces this
        proxy (agent_aliases already expanded to the gold mention surfaces)."""
        low_aliases = {a.lower() for a in agent_aliases}
        for s in self._root_subjects(sent):
            if s.text.lower() in low_aliases or s.lemma_.lower() in low_aliases:
                return True
            if s.text.lower() == name_head.lower():
                return True
        return False

    # RULE 0 epistemic-marker locality: a marker applies only within +/- this many sentences of the event, so a
    # marker about one change ("Anna watched" move 1) does not leak onto a later unseen change (seq-registration).
    EPI_WINDOW = 1

    # ---- motion frame: read PATH off the realized satellite/PP, not the verb ---
    # Placement/transfer verbs move a THING (their dobj), not the agent -- their PP is the object's path.
    PLACEMENT_VERBS = {"put", "place", "set", "lay", "drop", "hide", "conceal", "carry", "take", "bring",
                       "transfer", "shift", "throw", "push", "pull", "stow", "deposit", "replace", "remove",
                       "swap", "move", "hang", "stick", "tuck", "pop", "fetch"}
    # Grounds that ARE the current indoor scene -> arriving there = a RETURN to the scene (present).
    SCENE_GROUND = {"room", "house", "kitchen", "parlour", "parlor", "hall", "home", "chamber", "cottage",
                    "bedroom", "door", "doorway", "indoors", "inside", "cabin", "hut", "office", "study",
                    "library", "shop", "nursery", "sitting", "dining", "drawing", "bed"}

    # Strong PATH satellites (adverbs/particles) that mark a location change. Deliberately excludes weak /
    # posture-ambiguous ones ("up"/"down"/"in"/"on") so "sat down" is NOT read as leaving.
    DIRECTIONAL_ADV = {"out", "outside", "away", "off", "upstairs", "downstairs", "indoors", "outdoors",
                       "inside", "forth", "abroad", "aside", "back", "hence", "hither", "thither",
                       "homeward", "afield", "yonder", "home"}
    RETURN_ADV = {"back", "again"}
    # Spatial PPs whose GROUND is a destination/source: going TO a place = leaving the current scene.
    DIRECTIONAL_PREPS = {"to", "into", "toward", "towards", "unto", "from", "onto"}
    # PERCEPTION / STANCE verbs: the agent does NOT relocate, so a directional PP is a GAZE/POSTURE direction
    # ("gazed into the fire", "stared out of the window", "stayed to dinner"), NOT locomotion. Suppress motion.
    STANCE_PERCEPTION = {"gaze", "stare", "look", "peer", "glance", "glare", "squint", "sit", "stand",
                         "remain", "stay", "lie", "lean", "kneel", "rest", "watch", "behold", "dwell",
                         "pause", "wait", "linger", "crouch", "recline", "loll", "perch"}

    def _motion_signal(self, sent) -> Optional[Tuple[str, Optional[str]]]:
        """Return ('depart'|'return', ground) for an AGENT SELF-motion in `sent`, else None.

        PRINCIPLE (from the false-belief structure): the agent starts CO-PRESENT with the object it set down,
        so ANY self-motion takes it AWAY from that scene EXCEPT an explicit RETURN. DEIXIS DOMINATES: come/
        return/arrive = return; go/leave/withdraw/retire = depart -- regardless of the goal ground (fixes
        'went upstairs to bed'). A non-deictic manner verb (hurry/step/ride/climb) is motion iff it carries a
        directional satellite/PP; direction = return only for an explicit 'back'/'again', else depart (fixes
        'hurried indoors' while the object is outdoors). Reads the PATH SATELLITE, NOT a manner-verb whitelist
        (Talmy). Transitive placement (put/move a THING) is SKIPPED -- its PP is the object's path."""
        verbs = [t for t in sent if t.pos_ == "VERB"]
        depart = ret = False
        ground = None
        for v in verbs:
            lem = v.lemma_.lower()
            vtext = v.text.lower()
            dobjs = [c for c in v.children if c.dep_ in ("dobj", "obj", "dative")]
            deixis_away = lem in DEIXIS_AWAY or vtext in DEIXIS_AWAY
            deixis_toward = lem in DEIXIS_TOWARD or vtext in DEIXIS_TOWARD
            # PERCEPTION / STANCE verb: the agent does not relocate -- a directional PP is gaze/posture
            # direction, not locomotion. Suppress (unless the verb is ALSO a deixis motion verb, which it isn't).
            if lem in self.STANCE_PERCEPTION and not (deixis_away or deixis_toward):
                continue
            # leave/quit/exit + location dobj -> depart FROM that ground (Source realized as dobj)
            if lem in ("leave", "quit", "exit") and dobjs:
                depart = True
                ground = " ".join(w.text for w in dobjs[0].subtree)
                continue
            # DEIXIS DOMINATES (Talmy Path deixis component)
            if deixis_toward:
                ret = True
                continue
            if deixis_away:
                depart = True
                continue
            # transitive placement/transfer with a THING object -> object path, NOT agent self-motion. Skip.
            if dobjs and lem in self.PLACEMENT_VERBS:
                continue
            # non-deictic manner verb: motion iff a directional satellite / spatial PP is realized. Scan the
            # verb's SUBTREE (not just direct children): en_core_web_sm attaches "out" under "here" ("hurried
            # out here") and parses "downstairs" as a dobj ("hastened downstairs") -- both must be caught.
            has_dir = False
            ret_cue = False
            for c in v.subtree:
                if c is v:
                    continue
                w = c.text.lower()
                if c.pos_ in ("ADV", "ADP", "PART", "NOUN") and w in self.DIRECTIONAL_ADV \
                        and c.dep_ in ("prt", "advmod", "npadvmod", "dobj", "obj", "advcl", "dep"):
                    has_dir = True
                    if w in self.RETURN_ADV:
                        ret_cue = True
                if c.dep_ == "prep" and c.head == v:
                    twotok = (w + " " + (c.nbor().text.lower() if c.i + 1 < len(c.doc) else "")).strip()
                    if w in self.DIRECTIONAL_PREPS or twotok == "out of":
                        has_dir = True
                        pobj = [g for g in c.children if g.dep_ == "pobj"]
                        if pobj:
                            ground = " ".join(x.text for x in pobj[0].subtree)
            if has_dir:
                if ret_cue:
                    ret = True
                else:
                    depart = True
        if ret and not depart:
            return ("return", ground)
        if depart and not ret:
            return ("depart", ground)
        if ret and depart:
            return ("return", ground)  # explicit return dominates a co-occurring depart cue
        return None

    def _absence_predicate(self, sent, agent_aliases) -> Optional[bool]:
        """Detect a stative absence/presence predicate about the agent: 'Anna was gone/away/out' -> away;
        'Anna was back/in/present/here' -> present. Returns True(=away), False(=present), or None."""
        low = sent.text.lower()
        arx = self._alias_regex(agent_aliases)
        if not arx.search(low):
            return None
        low_aliases = {a.lower() for a in agent_aliases}
        # agent + be + {gone/away/out/absent} -- the AGENT must be the SUBJECT of the copula ("Anna was out"),
        # NOT merely present in the sentence ("the candle was out" must NOT read as Anna absent).
        for w in sent:
            if w.lemma_.lower() in ABSENCE_PRED and w.dep_ in ("acomp", "advmod", "attr", "oprd", "amod", "ROOT"):
                head = w.head
                if head.lemma_ == "be" or head.pos_ == "AUX":
                    subj = [c for c in head.children if c.dep_ in ("nsubj", "nsubjpass")]
                    if any(s.text.lower() in low_aliases or s.text.lower() == (agent_aliases[0].lower() if agent_aliases else "")
                           for s in subj):
                        return True
        # RESTORE presence only on an EXPLICIT return/present stative. NOT "was inside/indoors" -- that is
        # ambiguous (inside is 'present' only if the event scene is indoors; when the object is outdoors,
        # "while she was inside" means ABSENT). fixes fb_glove.
        if re.search(r"\b(was|were|is|are|had been|being)\s+(back|present|here|at home again|returned)\b", low):
            return False
        if (re.search(r"\bin (his|her|their) absence\b", low)
                or re.search(r"\bwhile .*(was|were) (gone|away|out|absent|abroad|upstairs|out of the room)\b", low)):
            return True
        return None

    # ---- occlusion / field --------------------------------------------
    @staticmethod
    def _match_any(patterns, text) -> bool:
        return any(re.search(p, text) for p in patterns)

    def _field_state_update(self, st: "PresenceState", low: str) -> List[Tuple[str, str]]:
        """Update the agent's running PER-MODALITY state (awake / lit / attending) from a clause. Returns the
        (component, new_value) changes for the trace. These persist until reversed (asleep until wake, dark
        until light, inattentive until re-attend)."""
        changes = []
        if self._match_any(STATE_UNAVAIL_CUES, low):
            if st.awake:
                st.awake = False; changes.append(("awake", "False"))
        elif self._match_any(WAKE_CUES, low):
            if not st.awake:
                st.awake = True; changes.append(("awake", "True"))
        if self._match_any(DARK_CUES, low):
            if st.lit:
                st.lit = False; changes.append(("lit", "False"))
        elif self._match_any(LIGHT_CUES, low):
            if not st.lit:
                st.lit = True; changes.append(("lit", "True"))
        if self._match_any(INATTENTION_CUES, low):
            if st.attending:
                st.attending = False; changes.append(("attending", "False"))
        elif self._match_any(ATTEND_CUES, low):
            if not st.attending:
                st.attending = True; changes.append(("attending", "True"))
        return changes

    def _perceptual_field(self, sents, ev: int, st: "PresenceState") -> Tuple[Optional[bool], str]:
        """Compute whether the object-move event is IN the agent's field (per-modality gate over the ontology).
        For a LOCATION-MOVE the property is 'occurrence' -> VISION or AUDITION can reveal it. Returns
        (available, reason); available=None means UNKNOWN (unstated opacity -- a glass-box UNKNOWN, not a guess)."""
        ev_low = sents[ev].text.lower()
        # BLOCKING occluders (barrier / closed-opaque) must hold AT-OR-BEFORE the event to block perception of
        # it -- a closure described AFTER the event ("...into the box. Then he shut the lid.") does NOT
        # retroactively block the (already-perceived) entry. So the blocking window is prior+event ONLY, never
        # the following sentence (motion-persistence: watched-it-go-in stays perceived). [seq-registration drill]
        win = " ".join(s.text.lower() for s in sents[max(0, ev - 1):ev + 1])  # prior + event, NOT ev+1
        barrier = self._match_any(BARRIER_CUES, win)
        transparent = self._match_any(TRANSPARENT_CUES, win)
        closed_opaque = self._match_any(CLOSED_OPAQUE_CUES, win) and not transparent
        silent = self._match_any(SILENT_CUES, win)
        loud = self._match_any(LOUD_CUES, win)
        # VISION: co-present + awake + lit + attending + no opaque barrier + not in a closed-opaque container
        vision = (st.present and st.awake and st.lit and st.attending and not barrier and not closed_opaque)
        # AUDITION: co-present (~earshot) + awake + a non-silent event (penetrates darkness / thin barrier / gaze)
        audition = (st.present and st.awake and not silent and (loud or not (barrier or closed_opaque)))
        available = bool(vision or audition)
        reason = (f"vision={vision}(lit={st.lit},attend={st.attending},barrier={barrier},closed_opaque={closed_opaque}) "
                  f"audition={audition}(silent={silent},loud={loud}) -> available={available}")
        # UNKNOWN: a container is present with UNSTATED opacity/state -> glass-box UNKNOWN rather than a guess.
        container_hint = re.search(r"\b(bag|box|drawer|chest|case|basket|jar|pot|cupboard|trunk|sack|pouch|casket)\b", win)
        if container_hint and not (transparent or closed_opaque) and st.present and st.awake and st.lit and st.attending and not barrier:
            # co-present and could see it, but if the move is INTO/inside a container of unknown opacity, flag UNKNOWN
            if re.search(r"\b(in|into|inside|within)\b .{0,20}" + re.escape(container_hint.group(0)), win):
                return None, reason + " | UNKNOWN(container opacity unstated)"
        return available, reason

    # ---- testimony ----------------------------------------------------
    def _informed_after(self, sents, agent_aliases, event_idx: int) -> Optional[int]:
        """Return the clause index at/after the event where the agent is TOLD/HEARS of the change, else None."""
        parts = sorted({re.escape(a) for a in agent_aliases if a and a.lower() not in _PRON}, key=len, reverse=True)
        if not parts:
            return None
        agent_re = "(?:" + "|".join(parts) + r"|he|she|they)"
        pats = _testimony_patterns(agent_re)
        for i in range(event_idx, len(sents)):
            low = sents[i].text.lower()
            if self._match_any([p.lower() for p in pats], low):
                return i
        return None

    # ---- RULE 0: explicit narrator epistemic statement ----------------
    def _epistemic_statement(self, sents, agent_aliases, event_idx: int) -> Optional[bool]:
        """Return True/False if the narrator EXPLICITLY states the agent's knowledge of the event, else None.
        The narrator directly asserting a mind-state is the most direct evidence; the marker NEAREST the event
        wins (a later 'but she had seen it after all' overrides an earlier absence)."""
        parts = sorted({re.escape(a) for a in agent_aliases if a and a.lower() not in _PRON}, key=len, reverse=True)
        agent_re = "(?:" + "|".join(parts + ["he", "she", "they"]) + r")" if parts else r"(?:he|she|they)"
        neg, pos = _epistemic_patterns(agent_re)
        hits = []  # (distance_to_event, idx, sign)
        for i, s in enumerate(sents):
            if abs(i - event_idx) > self.EPI_WINDOW:
                continue  # an epistemic marker is EVENT-SPECIFIC: "Anna watched" (move 1) must NOT leak onto
                          # a later move A did not see. Only markers LOCAL to this event apply. [seq-registration]
            txt = s.text  # search case-INSENSITIVELY on the ORIGINAL text (agent names are capitalised)
            if any(re.search(p, txt, re.IGNORECASE) for p in neg):
                hits.append((abs(i - event_idx), i, False))
            if any(re.search(p, txt, re.IGNORECASE) for p in pos):
                hits.append((abs(i - event_idx), i, True))
        if not hits:
            return None
        # nearest to the event; tie -> the later sentence (a correction supersedes)
        hits.sort(key=lambda h: (h[0], -h[1]))
        return hits[0][2]

    # ---- event localisation -------------------------------------------
    def _find_event_index(self, sents, event_object: Optional[str], mover_aliases: Sequence[str],
                          agent_aliases: Sequence[str], event_location: Optional[str] = None) -> int:
        """Locate the clause where the change to `event_object` happens. The situation model (a separate organ)
        legitimately supplies WHAT/WHERE the event is; the observation cue only decides whether A witnessed it.
        Preference order: (1) the clause where the object reaches its FINAL location (event_location head noun),
        (2) a clause with the object + a change verb by a NON-agent main subject, (3) any object+change clause."""
        change_verbs = {"move", "moved", "put", "placed", "place", "take", "took", "hid", "hide", "shift", "shifted",
                        "transfer", "transferred", "carry", "carried", "swap", "swapped", "replace", "replaced",
                        "remove", "removed", "slip", "slipped", "drop", "dropped", "set", "knock", "knocked",
                        "nose", "nosed", "roll", "rolled", "fell", "fall", "blow", "blew", "push", "pushed",
                        "kick", "kicked", "throw", "threw", "left", "leave", "hang", "hung"}
        obj = (event_object or "").lower()
        name = agent_aliases[0] if agent_aliases else ""
        # (1) final-location arrival clause -- the most reliable event anchor (given by the situation model)
        if event_location:
            loc_head = event_location.lower().split()[-1]  # head noun of the final location phrase
            hits = [i for i, s in enumerate(sents) if loc_head in s.text.lower()
                    and not self._subject_is_agent(s, agent_aliases, name)]
            if hits:
                return hits[-1]
        cand = []
        for i, s in enumerate(sents):
            low = s.text.lower()
            has_obj = (obj in low) if obj else True
            has_change = any(w.lemma_.lower() in change_verbs or w.text.lower() in change_verbs for w in s)
            # the MOVE (not the agent's initial placement): change to the object by a NON-agent main subject.
            if has_obj and has_change and not self._subject_is_agent(s, agent_aliases, name):
                cand.append(i)
        if cand:
            return cand[-1]   # last such = the actual move, after any initial placement
        # fallback: last object+change clause that is NOT the agent's own placement
        non_agent = [i for i, s in enumerate(sents)
                     if (not obj or obj in s.text.lower())
                     and any(w.lemma_.lower() in change_verbs for w in s)
                     and not self._subject_is_agent(s, agent_aliases, name)]
        if non_agent:
            return non_agent[-1]
        any_change = [i for i, s in enumerate(sents)
                      if (not obj or obj in s.text.lower())
                      and any(w.lemma_.lower() in change_verbs for w in s)]
        if any_change:
            return any_change[-1]
        return len(sents) // 2

    # ---- the decision --------------------------------------------------
    def observed(self, text: str, agent_aliases: Sequence[str], event_object: Optional[str] = None,
                 mover_aliases: Sequence[str] = (), event_index: Optional[int] = None,
                 event_location: Optional[str] = None, use_epistemic: bool = True) -> LedgerTrace:
        """Compute observed(agent, event) as RULE 1 (co-present & field-open at the move) OR RULE 2 (informed).
        agent_aliases[0] is treated as the canonical agent name; include gold coref surfaces for the corpus path.
        event_location (the move's FINAL location) + event_index are supplied by the situation model to anchor
        the event clause -- the observation cue's job is the perceptual-access inference, not event extraction."""
        nlp = self._nlp_or_load()
        doc = nlp(text)
        sents = list(doc.sents)
        if not sents:
            return LedgerTrace(observed=True, reason="empty")
        name_head = agent_aliases[0] if agent_aliases else ""

        # 1) locate the event clause
        ev = event_index if event_index is not None else self._find_event_index(
            sents, event_object, mover_aliases, agent_aliases, event_location=event_location)
        ev = max(0, min(ev, len(sents) - 1))

        # 2) walk the discourse, maintaining the agent's presence interval + per-modality field, up to ev
        st = PresenceState(present=True, interval_open_at=0)
        trace = LedgerTrace(agent=name_head, event_idx=ev)
        arx = self._alias_regex(agent_aliases)
        for i in range(0, ev + 1):
            s = sents[i]
            low = s.text.lower()
            is_agent_subj = self._subject_is_agent(s, agent_aliases, name_head)
            # motion (only when the agent is the mover of themselves)
            if is_agent_subj:
                mo = self._motion_signal(s)
                if mo is not None:
                    direction, ground = mo
                    if direction == "depart":
                        st.present = False
                        st.location = ground
                        trace.per_clause.append((i, "depart", ground or ""))
                    else:
                        st.present = True
                        st.location = ground
                        st.interval_open_at = i
                        trace.per_clause.append((i, "return", ground or "scene"))
            # stative absence predicate about the agent (need not be the grammatical subject: "in her absence")
            ap = self._absence_predicate(s, agent_aliases)
            if ap is True and st.present:
                st.present = False
                trace.per_clause.append((i, "absent_pred", low[:40]))
            elif ap is False and not st.present:
                st.present = True
                st.interval_open_at = i
                trace.per_clause.append((i, "present_pred", low[:40]))
            # PER-MODALITY field state (awake / lit / attending) -- persistent occluder states about the agent
            if arx.search(low) or is_agent_subj:
                for comp, val in self._field_state_update(st, low):
                    trace.per_clause.append((i, comp, val))

        # per-modality field at the event (event-local barrier / container-opacity / loudness + running state)
        avail, field_reason = self._perceptual_field(sents, ev, st)
        trace.present_at_event = st.present
        # UNKNOWN (unstated opacity) -> fall back to co-presence (do not fabricate an occluder we cannot read)
        trace.available_at_event = st.present and st.awake if avail is None else avail
        trace.per_clause.append((ev, "field", field_reason))

        # 3) RULE 2 -- testimony at/after the event
        inf_idx = self._informed_after(sents, agent_aliases, ev)
        trace.informed = inf_idx is not None

        # 4) registration. RULE 0 (explicit narrator epistemic statement) OVERRIDES when present -- the narrator
        # asserting the mind-state outright is the most direct evidence. Else observed iff (co-present AND
        # field-open at the move = RULE 1) OR informed (RULE 2).
        rule1 = bool(trace.present_at_event and trace.available_at_event)
        epi = self._epistemic_statement(sents, agent_aliases, ev) if use_epistemic else None
        if epi is not None:
            trace.observed = epi
            trace.per_clause.append((ev, "epistemic", str(epi)))
            trace.reason = (f"RULE0 explicit epistemic statement => observed={epi} "
                            f"(spatial: present={trace.present_at_event} available={trace.available_at_event} "
                            f"informed={trace.informed})")
        else:
            trace.observed = bool(rule1 or trace.informed)
            trace.reason = (f"present={trace.present_at_event} available={trace.available_at_event} "
                            f"informed={trace.informed} -> RULE1={rule1} => observed={trace.observed}")
        return trace

    # ---- SEQUENTIAL registration over a CHAIN of changes (from the sequential-registration drill) -------
    def sequential_registration(self, text: str, agents: Dict[str, Sequence[str]], changes: List[dict]):
        """Fold `observed()` over a chronological CHAIN of changes to produce a per-agent REGISTRATION LEDGER.

        This is the mechanism's completion: a single move needs only a boolean, but a SEQUENCE (A->B->C) needs a
        sticky per-agent cell overwritten ONLY on changes the agent PERCEIVED (Butterfill&Apperly registration;
        Baker/Saxe/Tenenbaum 2011 freeze-when-unobserved). No new theory -- the per-event `observed()` is reused.

        agents : {name: aliases_list} (aliases[0] = the agent's canonical name).
        changes: [{'obj':str, 'to':str, 'event_index':int, 'mover':name_or_None}, ...] in chronological order --
                 supplied by the situation model / event-sequence extractor (the observation cue's job is the
                 perceptual-access inference, not event extraction).
        Returns (registration, world): registration[name][obj] = the LAST location the agent PERCEIVED the object
                 reach, or ABSENT (never perceived any placement = IGNORANT, distinct from a false belief).
        MOTION-PERSISTENCE falls out for free: an agent who watched the object ENTER an occluder registers the
        destination (the entry was perceived); later hidden changes fail the field check and the cell stays frozen.
        """
        world: Dict[str, str] = {}
        reg: Dict[str, Dict[str, str]] = {a: {} for a in agents}
        nlp = self._nlp_or_load()
        sents = list(nlp(text).sents)
        for ch in changes:
            if ch.get("type", "move") == "tell":
                # TESTIMONY event: the addressee registers the ASSERTED location -- = reality for HONEST testimony,
                # but a LIE gives a FALSE belief matching what was asserted (Harris&Koenig: testimony is a channel
                # to the ledger, its CONTENT need not be true). A DISTRUSTED source is DISCOUNTED (Koenig 2004
                # reliability): the addressee keeps its prior belief. Does NOT change world_state (telling != moving).
                addr = ch["addressee"]
                trusted = ch.get("trusted")
                if trusted is None:
                    trusted = self._testimony_trusted(sents, agents.get(addr, [addr]), ch.get("event_index", 0))
                if trusted:
                    reg.setdefault(addr, {})[ch["obj"]] = ch["asserted"]
                continue
            world[ch["obj"]] = ch["to"]                       # MOVE: world track updates on every change
            for a, aliases in agents.items():
                if ch.get("mover") == a:
                    perceived = True                          # the mover trivially perceives its own action
                else:
                    tr = self.observed(text, list(aliases), event_object=ch["obj"], event_index=ch["event_index"])
                    perceived = tr.observed
                if perceived:
                    reg[a][ch["obj"]] = ch["to"]              # OVERWRITE; else the sticky cell carries forward
        return reg, world

    def _testimony_trusted(self, sents, addr_aliases, event_idx: int) -> bool:
        """False if the addressee DISTRUSTS/disbelieves the source near the telling (Koenig 2004 reliability
        discounting) -- 'but Anna did not believe him', 'she doubted it'. Deception by the SOURCE is orthogonal
        (a lie still produces belief unless the addressee distrusts) and is carried by the ASSERTED location."""
        parts = sorted({re.escape(a) for a in addr_aliases if a and a.lower() not in _PRON}, key=len, reverse=True)
        a = "(?:" + "|".join(parts + ["he", "she", "they"]) + ")" if parts else "(?:he|she|they)"
        distrust = [rf"\b{a} (?:did not|did n't|didn't|would not|wouldn't|could not) believe\b",
                    rf"\b{a} (?:distrusted|mistrusted|doubted|disbelieved)\b", rf"\b{a} knew (?:better|it was a lie)\b",
                    rf"\b{a} was not (?:fooled|deceived|taken in)\b", rf"\b{a} saw through\b"]
        lo, hi = max(0, event_idx - 1), min(len(sents), event_idx + 2)
        span = " ".join(s.text for s in sents[lo:hi])
        return not any(re.search(p, span, re.IGNORECASE) for p in distrust)

    @staticmethod
    def belief_of(reg, agent: str, obj: str):
        """The agent's believed location of obj, or None = IGNORANT (never registered)."""
        return reg.get(agent, {}).get(obj)

    @staticmethod
    def is_false_belief(reg, world, agent: str, obj: str) -> bool:
        r = reg.get(agent, {}).get(obj)
        return r is not None and r != world.get(obj)

    @staticmethod
    def is_ignorant(reg, agent: str, obj: str) -> bool:
        return reg.get(agent, {}).get(obj) is None


# ---------------------------------------------------------------------------
# Self-test: the four canonical perceptual-access cases the STATELESS keyword list gets wrong.
# ---------------------------------------------------------------------------
def _self_test():
    import spacy
    nlp = spacy.load("en_core_web_sm")
    led = PerceptualAccessLedger(nlp)
    cases = [
        # (text, aliases, object, expected_observed, note)
        ("Anna put her marble in the red box and went outside to play. While Anna was gone, her brother Ben "
         "moved the marble from the red box to the blue basket. Anna did not see him do it.",
         ["Anna", "she", "her"], "marble", False, "classic absence"),
        # RE-ENTRY before the move: keyword list sees 'went outside' and wrongly says absent; ledger re-opens presence.
        ("Anna put her marble in the red box and went outside to play. Then Anna came back inside. "
         "Ben moved the marble from the red box to the blue basket while Anna watched.",
         ["Anna", "she", "her"], "marble", True, "re-entry then present"),
        # OCCLUSION despite co-presence: asleep in the same room.
        ("Anna lay asleep on the couch in the room. Ben quietly moved the marble from the red box to the blue basket.",
         ["Anna", "she", "her"], "marble", False, "asleep = occluded"),
        # TESTIMONY after absence: told about the move.
        ("Anna went outside to play. Ben moved the marble from the red box to the blue basket. "
         "Later, Ben told Anna that he had put it in the blue basket.",
         ["Anna", "she", "her"], "marble", True, "informed"),
        # WENT TO A NEW PLACE (not 'outside'): the keyword list has no 'to the field' rule; ledger departs.
        ("Anna rode to the far field to see the horses. Meanwhile Ben moved the marble from the red box "
         "to the blue basket. Anna knew nothing of it.",
         ["Anna", "she", "her"], "marble", False, "went to a new place"),
    ]
    ok = 0
    for text, aliases, obj, exp, note in cases:
        tr = led.observed(text, aliases, event_object=obj)
        good = (tr.observed == exp)
        ok += int(good)
        print(f"  [{'PASS' if good else 'FAIL'}] {note}: observed={tr.observed} (exp {exp}) | {tr.reason}")
    print(f"SELF-TEST {ok}/{len(cases)} cases")
    assert ok == len(cases), f"perceptual-access ledger self-test failed ({ok}/{len(cases)})"


if __name__ == "__main__":
    _self_test()
