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

GLASS-BOX: pure symbolic inference over the SUBSTRATE'S OWN in-substrate UD parse (hdlab.pos_tagger UPOS +
  hdlab.arc_parser heads + hdlab.arc_labeler UD deprels -- the SAME frontend every other reader organ uses).
  NO spaCy, NO external LLM, NO network at inference (owner 2026-09-08: an external tool at inference is NOT
  brain-foundational). The parse is perception-of-syntax; the ledger is the glass-box situation-model
  inference. Cues re-expressed over UD topology (copula-head inversion; PP = obl noun + case child; obj/iobj;
  compound:prt). ASCII only.
"""
from __future__ import annotations

__bf_status__ = 'BF_SPIRIT'   # BF | BF_SPIRIT | NOT_BF | BF_UNPINNED | BF_UNVERIFIED ; mirrors notes/bf_status_registry.jsonl
__bf_verified__ = '2026-09-09 BF-certification pass (operation/math read of the pinned computation + key ops; strategy first-hand)'
__bf_note__ = "glass-box OBSERVATION-CUE front-end for ToM ('did agent A perceive event E?'; literature-drilled brain mechanism), replacing the lexical keyword extractor; pinned perceptual-access frame"
__bf_corrections__ = []


import os
import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

from hdlab.thematic_role_labeler import lemma_verb

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
# RULE 0 -- EXPLICIT narrator epistemic statement about the agent.
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


# ---------------------------------------------------------------------------
# In-substrate parse frontend (the SAME assets the reader uses). Loaded lazily + module-cached so importing
# this module is free and a reader that never queries belief pays nothing.
# ---------------------------------------------------------------------------
_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
_POS_ASSET = os.path.join(_REPO, "data", "frontend_assets", "pos_tagger_ud_ewt_upos.json")
_ARC_ASSET = os.path.join(_REPO, "data", "frontend_assets", "arc_parser_hashed_ud_ewt.npz")
_LAB_ASSET = os.path.join(_REPO, "data", "frontend_assets", "arc_labeler_hashed_ud_ewt.json")
_FRONTEND: Dict[str, object] = {}


def _frontend():
    """The shared in-substrate parse frontend (tagger, parser, labeler). Loaded once, reused."""
    if "t" not in _FRONTEND:
        from hdlab.pos_tagger import PosTagger
        from hdlab.arc_parser import ArcParser
        from hdlab.arc_labeler import ArcLabeler
        _FRONTEND["t"] = PosTagger.load(_POS_ASSET)
        _FRONTEND["p"] = ArcParser.load(_ARC_ASSET)
        _FRONTEND["l"] = ArcLabeler.load(_LAB_ASSET)
    return _FRONTEND["t"], _FRONTEND["p"], _FRONTEND["l"]


# lightweight deterministic tokenizer + sentence splitter (NO spaCy). The reader normally hands the ledger
# text built from its OWN pre-tokenized sentences, so this reproduces that segmentation on the joined text.
_ABBREV = {"mr", "mrs", "ms", "dr", "st", "mt", "jr", "sr", "prof", "rev", "gen", "col", "capt", "sgt"}
_TOK_RE = re.compile(r"n't|'s|'re|'ve|'ll|'d|'m|[A-Za-z]+|[0-9]+|[^\sA-Za-z0-9]")


def _tokenize(sentence: str) -> List[str]:
    return _TOK_RE.findall(sentence)


def _split_sentences(text: str) -> List[List[str]]:
    toks_all = _tokenize(text)
    sents: List[List[str]] = []
    cur: List[str] = []
    for i, tk in enumerate(toks_all):
        cur.append(tk)
        if tk in (".", "!", "?"):
            prev = toks_all[i - 1].lower() if i >= 1 else ""
            if tk == "." and prev in _ABBREV:
                continue
            nxt = toks_all[i + 1] if i + 1 < len(toks_all) else None
            if nxt is None or nxt[0:1].isupper() or nxt[0:1] in ("\"", "'"):
                sents.append(cur)
                cur = []
    if cur:
        sents.append(cur)
    return sents


@dataclass
class _ISent:
    """One sentence's in-substrate parse (1-based dep indices). Exposes `.text` so the regex-only cue
    methods (field / testimony / epistemic) run over it unchanged."""
    toks: List[str]
    upos: List[str]
    heads: Dict[int, int]        # dep_idx(1-based) -> head_idx (0 = ROOT)
    deprels: Dict[int, str]      # dep_idx(1-based) -> UD deprel
    _text: str = ""

    @property
    def text(self) -> str:
        return self._text


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
    """Glass-box perceptual-access registration ledger over the substrate's OWN in-substrate UD parse.

    Usage:
        led = PerceptualAccessLedger()
        trace = led.observed(text, agent_aliases=["Anna", "she", "her"], event_object="marble",
                             event_location=None, scene_reset_at=None)
        cue = trace.observed  # True iff RULE 1 (co-present & field-open at the move) or RULE 2 (informed) fired
    """

    def __init__(self, nlp=None):
        # `nlp` is accepted for backward-compat with callers that used to pass a spaCy model; it is IGNORED
        # (this ledger never touches spaCy). _nlp stays None so any `getattr(led, "_nlp", None)` consumer
        # (e.g. the belief driver's STATUS reality path) routes to the in-substrate fallback, not spaCy.
        self._nlp = None
        self._t = None  # lazy in-substrate frontend handles (tagger, parser, labeler)
        self._p = None
        self._l = None

    # ---- parsing -------------------------------------------------------
    def _parse_sent(self, toks: Sequence[str]) -> _ISent:
        if self._t is None:
            self._t, self._p, self._l = _frontend()
        toks = list(toks)
        upos = self._t.tag(toks)
        heads = self._p.parse(toks, upos).heads
        deprels = self._l.label(toks, upos, heads)
        return _ISent(toks=toks, upos=list(upos), heads=dict(heads), deprels=dict(deprels),
                      _text=" ".join(toks))

    def _parse_sents(self, text: str) -> List[_ISent]:
        return [self._parse_sent(t) for t in _split_sentences(text) if t]

    # ---- tree helpers over UD heads ------------------------------------
    @staticmethod
    def _descendants(sent: "_ISent", root: int) -> List[int]:
        n = len(sent.toks)
        children: Dict[int, List[int]] = {}
        for k in range(1, n + 1):
            children.setdefault(sent.heads.get(k, 0), []).append(k)
        seen: set = set()
        stack = [root]
        while stack:
            x = stack.pop()
            if x in seen:
                continue
            seen.add(x)
            for c in children.get(x, []):
                if c not in seen:
                    stack.append(c)
        return sorted(seen)

    def _subtree_text(self, sent: "_ISent", root: int) -> str:
        return " ".join(sent.toks[i - 1] for i in self._descendants(sent, root))

    # ---- subject / agent resolution -----------------------------------
    @staticmethod
    def _alias_regex(agent_aliases: Sequence[str]) -> re.Pattern:
        parts = sorted({re.escape(a.strip()) for a in agent_aliases if a.strip()}, key=len, reverse=True)
        return re.compile(r"\b(" + "|".join(parts) + r")\b", re.IGNORECASE)

    def _root_subjects(self, sent: "_ISent") -> List[int]:
        """The MAIN-clause subject token index(es): the nsubj/nsubj:pass/csubj of the ROOT verb (head==0)
        (+ its conjuncts). UD: the root is the token with head 0 (spaCy dep_=='ROOT'); the subject is its
        nsubj child (not a subordinate 'while Anna watched' subject -- the bug that mislocated the event)."""
        toks, upos, heads, deprels = sent.toks, sent.upos, sent.heads, sent.deprels
        n = len(toks)
        root = next((i for i in range(1, n + 1) if heads.get(i) == 0), None)
        if root is None:
            return []
        subs = [k for k in range(1, n + 1)
                if heads.get(k) == root and deprels.get(k) in ("nsubj", "nsubj:pass", "csubj", "csubj:pass")]
        out = list(subs)
        for s in subs:
            out += [c for c in range(1, n + 1) if heads.get(c) == s and deprels.get(c) == "conj"]
        if not out:
            # PARSE-FAILURE fallback: the leading nominal in English SVO subject position before the ROOT verb.
            for i in range(1, root):
                if upos[i - 1] in ("PUNCT", "SCONJ", "CCONJ", "ADP", "DET"):
                    continue
                if deprels.get(i) in ("mark", "cc", "det", "case", "punct"):
                    continue
                out = [i]
                break
        return out

    def _subject_is_agent(self, sent: "_ISent", agent_aliases: Sequence[str], name_head: str) -> bool:
        """True if the MAIN-clause subject of `sent` coref-resolves to the tracked agent (name or a pronoun
        alias). For the corpus path, agent_aliases are already the gold mention surfaces."""
        low_aliases = {a.lower() for a in agent_aliases}
        nh = name_head.lower()
        for s in self._root_subjects(sent):
            w = sent.toks[s - 1].lower()
            if w in low_aliases or w == nh:
                return True
        return False

    # RULE 0 epistemic-marker locality (see _epistemic_statement).
    EPI_WINDOW = 1

    # ---- motion frame: read PATH off the realized satellite/PP, not the verb ---
    PLACEMENT_VERBS = {"put", "place", "set", "lay", "drop", "hide", "conceal", "carry", "take", "bring",
                       "transfer", "shift", "throw", "push", "pull", "stow", "deposit", "replace", "remove",
                       "swap", "move", "hang", "stick", "tuck", "pop", "fetch"}
    SCENE_GROUND = {"room", "house", "kitchen", "parlour", "parlor", "hall", "home", "chamber", "cottage",
                    "bedroom", "door", "doorway", "indoors", "inside", "cabin", "hut", "office", "study",
                    "library", "shop", "nursery", "sitting", "dining", "drawing", "bed"}
    DIRECTIONAL_ADV = {"out", "outside", "away", "off", "upstairs", "downstairs", "indoors", "outdoors",
                       "inside", "forth", "abroad", "aside", "back", "hence", "hither", "thither",
                       "homeward", "afield", "yonder", "home"}
    RETURN_ADV = {"back", "again"}
    DIRECTIONAL_PREPS = {"to", "into", "toward", "towards", "unto", "from", "onto"}
    STANCE_PERCEPTION = {"gaze", "stare", "look", "peer", "glance", "glare", "squint", "sit", "stand",
                         "remain", "stay", "lie", "lean", "kneel", "rest", "watch", "behold", "dwell",
                         "pause", "wait", "linger", "crouch", "recline", "loll", "perch"}

    def _motion_signal(self, sent: "_ISent") -> Optional[Tuple[str, Optional[str]]]:
        """Return ('depart'|'return', ground) for an AGENT SELF-motion in `sent`, else None -- re-expressed
        over UD. Deixis dominates (come/return=return; go/leave/withdraw=depart) regardless of ground. A
        non-deictic manner verb is motion iff it carries a directional satellite (UD advmod/compound:prt in
        DIRECTIONAL_ADV) or a directional PP (an obl/nmod/obj noun child with a `case` child in
        DIRECTIONAL_PREPS). Transitive placement (put/move a THING) is SKIPPED -- its PP is the object's path."""
        toks, upos, heads, deprels = sent.toks, sent.upos, sent.heads, sent.deprels
        n = len(toks)
        verbs = [i for i in range(1, n + 1) if upos[i - 1] == "VERB"]
        depart = ret = False
        ground = None
        for v in verbs:
            lem = lemma_verb(toks[v - 1]).lower()
            vtext = toks[v - 1].lower()
            dobjs = [k for k in range(1, n + 1) if heads.get(k) == v and deprels.get(k) in ("obj", "iobj")]
            deixis_away = lem in DEIXIS_AWAY or vtext in DEIXIS_AWAY
            deixis_toward = lem in DEIXIS_TOWARD or vtext in DEIXIS_TOWARD
            if lem in self.STANCE_PERCEPTION and not (deixis_away or deixis_toward):
                continue
            if lem in ("leave", "quit", "exit") and dobjs:
                depart = True
                ground = self._subtree_text(sent, dobjs[0])
                continue
            if deixis_toward:
                ret = True
                continue
            if deixis_away:
                depart = True
                continue
            if dobjs and lem in self.PLACEMENT_VERBS:
                continue
            has_dir = False
            ret_cue = False
            for c in self._descendants(sent, v):
                if c == v:
                    continue
                w = toks[c - 1].lower()
                dep = deprels.get(c)
                if upos[c - 1] in ("ADV", "ADP", "PART", "NOUN") and w in self.DIRECTIONAL_ADV \
                        and dep in ("compound:prt", "prt", "advmod", "obl", "obj", "advcl", "dep", "nmod"):
                    has_dir = True
                    if w in self.RETURN_ADV:
                        ret_cue = True
            for k in range(1, n + 1):
                if heads.get(k) == v and deprels.get(k) in ("obl", "nmod", "obj"):
                    for c in range(1, n + 1):
                        if heads.get(c) == k and deprels.get(c) == "case":
                            cw = toks[c - 1].lower()
                            twotok = (cw + " " + (toks[c].lower() if c < n else "")).strip()
                            if cw in self.DIRECTIONAL_PREPS or twotok == "out of":
                                has_dir = True
                                ground = self._subtree_text(sent, k)
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

    def _absence_predicate(self, sent: "_ISent", agent_aliases) -> Optional[bool]:
        """Detect a stative absence/presence predicate about the agent: 'Anna was gone/away/out' -> away;
        'Anna was back/in/present/here' -> present. Returns True(=away), False(=present), or None. UD copula
        inversion: 'Anna was gone' = gone(root/cop-headed adj) + nsubj Anna. Regex parts are text-only."""
        low = sent.text.lower()
        arx = self._alias_regex(agent_aliases)
        if not arx.search(low):
            return None
        low_aliases = {a.lower() for a in agent_aliases}
        toks, upos, heads, deprels = sent.toks, sent.upos, sent.heads, sent.deprels
        n = len(toks)
        first = agent_aliases[0].lower() if agent_aliases else ""
        for w in range(1, n + 1):
            if toks[w - 1].lower() not in ABSENCE_PRED:
                continue
            has_cop = any(heads.get(c) == w and deprels.get(c) in ("cop", "aux") for c in range(1, n + 1))
            is_pred = (heads.get(w) == 0) or has_cop or deprels.get(w) in ("advmod", "amod", "obl", "xcomp", "advcl", "root")
            if not is_pred:
                continue
            subj = [c for c in range(1, n + 1) if heads.get(c) == w and deprels.get(c) in ("nsubj", "nsubj:pass")]
            hh = heads.get(w)
            if hh and 1 <= hh <= n and (lemma_verb(toks[hh - 1]).lower() == "be" or upos[hh - 1] == "AUX"):
                subj += [c for c in range(1, n + 1) if heads.get(c) == hh and deprels.get(c) in ("nsubj", "nsubj:pass")]
            if any(toks[s - 1].lower() in low_aliases or toks[s - 1].lower() == first for s in subj):
                return True
        # RESTORE presence only on an EXPLICIT return/present stative (text-only, unchanged).
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
        """Update the agent's running PER-MODALITY state (awake / lit / attending) from a clause."""
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
        """Compute whether the object-move event is IN the agent's field (per-modality gate over the ontology)."""
        ev_low = sents[ev].text.lower()
        win = " ".join(s.text.lower() for s in sents[max(0, ev - 1):ev + 1])  # prior + event, NOT ev+1
        barrier = self._match_any(BARRIER_CUES, win)
        transparent = self._match_any(TRANSPARENT_CUES, win)
        closed_opaque = self._match_any(CLOSED_OPAQUE_CUES, win) and not transparent
        silent = self._match_any(SILENT_CUES, win)
        loud = self._match_any(LOUD_CUES, win)
        vision = (st.present and st.awake and st.lit and st.attending and not barrier and not closed_opaque)
        audition = (st.present and st.awake and not silent and (loud or not (barrier or closed_opaque)))
        available = bool(vision or audition)
        reason = (f"vision={vision}(lit={st.lit},attend={st.attending},barrier={barrier},closed_opaque={closed_opaque}) "
                  f"audition={audition}(silent={silent},loud={loud}) -> available={available}")
        container_hint = re.search(r"\b(bag|box|drawer|chest|case|basket|jar|pot|cupboard|trunk|sack|pouch|casket)\b", win)
        if container_hint and not (transparent or closed_opaque) and st.present and st.awake and st.lit and st.attending and not barrier:
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
        """Return True/False if the narrator EXPLICITLY states the agent's knowledge of the event, else None."""
        parts = sorted({re.escape(a) for a in agent_aliases if a and a.lower() not in _PRON}, key=len, reverse=True)
        agent_re = "(?:" + "|".join(parts + ["he", "she", "they"]) + r")" if parts else r"(?:he|she|they)"
        neg, pos = _epistemic_patterns(agent_re)
        hits = []  # (distance_to_event, idx, sign)
        for i, s in enumerate(sents):
            if abs(i - event_idx) > self.EPI_WINDOW:
                continue
            txt = s.text
            if any(re.search(p, txt, re.IGNORECASE) for p in neg):
                hits.append((abs(i - event_idx), i, False))
            if any(re.search(p, txt, re.IGNORECASE) for p in pos):
                hits.append((abs(i - event_idx), i, True))
        if not hits:
            return None
        hits.sort(key=lambda h: (h[0], -h[1]))
        return hits[0][2]

    # ---- event localisation -------------------------------------------
    def _find_event_index(self, sents, event_object: Optional[str], mover_aliases: Sequence[str],
                          agent_aliases: Sequence[str], event_location: Optional[str] = None) -> int:
        """Locate the clause where the change to `event_object` happens (over the in-substrate parse)."""
        change_verbs = {"move", "moved", "put", "placed", "place", "take", "took", "hid", "hide", "shift", "shifted",
                        "transfer", "transferred", "carry", "carried", "swap", "swapped", "replace", "replaced",
                        "remove", "removed", "slip", "slipped", "drop", "dropped", "set", "knock", "knocked",
                        "nose", "nosed", "roll", "rolled", "fell", "fall", "blow", "blew", "push", "pushed",
                        "kick", "kicked", "throw", "threw", "left", "leave", "hang", "hung", "stood", "stand"}
        obj = (event_object or "").lower()
        name = agent_aliases[0] if agent_aliases else ""

        def has_change(s: "_ISent") -> bool:
            return any(lemma_verb(t).lower() in change_verbs or t.lower() in change_verbs for t in s.toks)

        if event_location:
            loc_head = event_location.lower().split()[-1]
            hits = [i for i, s in enumerate(sents) if loc_head in s.text.lower()
                    and not self._subject_is_agent(s, agent_aliases, name)]
            if hits:
                return hits[-1]
        cand = [i for i, s in enumerate(sents)
                if (not obj or obj in s.text.lower()) and has_change(s)
                and not self._subject_is_agent(s, agent_aliases, name)]
        if cand:
            return cand[-1]
        non_agent = [i for i, s in enumerate(sents)
                     if (not obj or obj in s.text.lower()) and has_change(s)
                     and not self._subject_is_agent(s, agent_aliases, name)]
        if non_agent:
            return non_agent[-1]
        any_change = [i for i, s in enumerate(sents)
                      if (not obj or obj in s.text.lower()) and has_change(s)]
        if any_change:
            return any_change[-1]
        return len(sents) // 2

    # ---- the decision --------------------------------------------------
    def observed(self, text: str, agent_aliases: Sequence[str], event_object: Optional[str] = None,
                 mover_aliases: Sequence[str] = (), event_index: Optional[int] = None,
                 event_location: Optional[str] = None, use_epistemic: bool = True) -> LedgerTrace:
        """Compute observed(agent, event) as RULE 1 (co-present & field-open at the move) OR RULE 2 (informed).
        agent_aliases[0] is the canonical agent name; include gold coref surfaces for the corpus path.
        event_location + event_index are supplied by the situation model to anchor the event clause."""
        sents = self._parse_sents(text)
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
            ap = self._absence_predicate(s, agent_aliases)
            if ap is True and st.present:
                st.present = False
                trace.per_clause.append((i, "absent_pred", low[:40]))
            elif ap is False and not st.present:
                st.present = True
                st.interval_open_at = i
                trace.per_clause.append((i, "present_pred", low[:40]))
            if arx.search(low) or is_agent_subj:
                for comp, val in self._field_state_update(st, low):
                    trace.per_clause.append((i, comp, val))

        # per-modality field at the event
        avail, field_reason = self._perceptual_field(sents, ev, st)
        trace.present_at_event = st.present
        trace.available_at_event = st.present and st.awake if avail is None else avail
        trace.per_clause.append((ev, "field", field_reason))

        # 3) RULE 2 -- testimony at/after the event
        inf_idx = self._informed_after(sents, agent_aliases, ev)
        trace.informed = inf_idx is not None

        # 4) registration. RULE 0 overrides when present.
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

    # ---- SEQUENTIAL registration over a CHAIN of changes ---------------
    def sequential_registration(self, text: str, agents: Dict[str, Sequence[str]], changes: List[dict]):
        """Fold `observed()` over a chronological CHAIN of changes to produce a per-agent REGISTRATION LEDGER."""
        world: Dict[str, str] = {}
        reg: Dict[str, Dict[str, str]] = {a: {} for a in agents}
        sents = self._parse_sents(text)
        for ch in changes:
            if ch.get("type", "move") == "tell":
                addr = ch["addressee"]
                trusted = ch.get("trusted")
                if trusted is None:
                    trusted = self._testimony_trusted(sents, agents.get(addr, [addr]), ch.get("event_index", 0))
                if trusted:
                    reg.setdefault(addr, {})[ch["obj"]] = ch["asserted"]
                continue
            world[ch["obj"]] = ch["to"]
            for a, aliases in agents.items():
                if ch.get("mover") == a:
                    perceived = True
                else:
                    tr = self.observed(text, list(aliases), event_object=ch["obj"], event_index=ch["event_index"])
                    perceived = tr.observed
                if perceived:
                    reg[a][ch["obj"]] = ch["to"]
        return reg, world

    def _testimony_trusted(self, sents, addr_aliases, event_idx: int) -> bool:
        """False if the addressee DISTRUSTS/disbelieves the source near the telling (Koenig 2004)."""
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
    led = PerceptualAccessLedger()
    cases = [
        ("Anna put her marble in the red box and went outside to play. While Anna was gone, her brother Ben "
         "moved the marble from the red box to the blue basket. Anna did not see him do it.",
         ["Anna", "she", "her"], "marble", False, "classic absence"),
        ("Anna put her marble in the red box and went outside to play. Then Anna came back inside. "
         "Ben moved the marble from the red box to the blue basket while Anna watched.",
         ["Anna", "she", "her"], "marble", True, "re-entry then present"),
        ("Anna lay asleep on the couch in the room. Ben quietly moved the marble from the red box to the blue basket.",
         ["Anna", "she", "her"], "marble", False, "asleep = occluded"),
        ("Anna went outside to play. Ben moved the marble from the red box to the blue basket. "
         "Later, Ben told Anna that he had put it in the blue basket.",
         ["Anna", "she", "her"], "marble", True, "informed"),
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
