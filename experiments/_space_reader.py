"""_space_reader -- drive the PROMOTED per-entity LOCATION tracker (hdlab.location_register) end-to-end
from the LIVE reader's OWN extraction, on real narrative prose.

THE GAP THIS FILLS (problem: the_reader_has_no_spatial_location_dimension_end_to_end):
  hdlab/location_register.py (the tracking CORE, Zwaan & Radvansky event-indexing SPACE) is promoted and
  validated -- but only on ABSTRACT motion events and CONSTRUCTION templates
  (exp_location_register_where_is_x_v1 scores 1.0 on synthetic PERSIST/REENTRY/STALE/MULTIHOP sentences,
  driven by the STANDALONE spaCy adapter + a SUPPLIED alias dict). It has NEVER been driven end-to-end
  through SituationReader.read() on real prose from the reader's OWN parse + coref. This module closes that.

TWO DRIVERS (both fold the SAME promoted hdlab tracker so where_is is apples-to-apples):
  * IN-SUBSTRATE (PRIMARY, faithful, NO spaCy/LLM): the reader's own glass-box parse -- hdlab.pos_tagger +
    hdlab.arc_parser (UAS ~0.79) + hdlab.predicate_argument_frontend.route_predicate_arguments (Talmy
    Source-Path-Goal telicity + VerbNet event-class + Goldberg caused-motion + ATL place-typing) -- yields
    goal/location/path/source/direction per matrix verb. The MOVER is the coref cluster of route's AGENT
    token (the reader's coref backbone resolves the pronoun). This is exactly "the reader's own extraction".
  * SPACY-ADAPTER (UPPER BOUND on extraction quality): the validated experiments/location_register.py motion
    reader (a better parser), fed the SAME reader coref. The GAP in-substrate->spaCy = the parser-fidelity
    cost, which enumerates what a stronger front-end (the incremental parser, p2) would buy the SPACE
    dimension -- the brief's "if extraction is too weak, name why -> points at the parser".

BRAIN FRAME (PINNED): per-entity location STATE updated ONLY by MOTION events and PERSISTING between updates
  (Zwaan & Radvansky 1998; place/grid allocentric map); motion read as Source-Path-Goal with GOAL dominant
  (Talmy 1985; Lakusta & Landau 2005), deixis (come/go, back) as the frame selector, verb-AGNOSTIC via path
  satellites. Categorical/topological scene nodes (Rinck 1997), nested regions (Wiener & Mallot). The
  motion->(kind,node) DECISION here is OUR-INVENTION-UNDER-TEST (a faithful port of the validated adapter's
  logic onto the in-substrate parse); the tracker + representation are PINNED and untouched.

Glass-box, ASCII only. Writes nothing (a pure library; the measuring cell owns data/). The solver may not
write hdlab/ -- SOLVED.md states the proposed default-off `track_space` landing (the causation/time pattern).
"""
from __future__ import annotations

from typing import Dict, List, Optional, Sequence, Tuple

# -- the PROMOTED tracking core (consumes abstract (entity, kind, node, t) motion events) --
from hdlab.location_register import LocationRegister, DEICTIC_SCENE, AWAY, MOTION_KINDS
# -- the reader's OWN in-substrate parse + event-semantic role router (glass-box, no spaCy/LLM) --
from hdlab.pos_tagger import PosTagger
from hdlab.arc_parser import ArcParser
from hdlab.predicate_argument_frontend import (
    route_predicate_arguments, matrix_verbs, is_place_ground, is_destination_verb)
from hdlab.thematic_role_labeler import lemma_verb
from hdlab.coref import parse_litbank_conll
from hdlab.scene_segment import parse_conll_sentences
import os

# ONE source of truth for the motion lexicons (do NOT drift from the validated adapter) --
from experiments.location_register import (
    canon_node, _PLACE_PARTICLE, DEICTIC_RETURN_GROUND, _NON_LOCATIVE_NOUN, _WITHIN_SCENE_GROUND,
    is_motion_verb)
from experiments.perceptual_access_ledger import DEIXIS_AWAY, DEIXIS_TOWARD

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_POS_ASSET = os.path.join(_REPO, "data/frontend_assets/pos_tagger_ud_ewt_upos.json")
_ARC_ASSET = os.path.join(_REPO, "data/frontend_assets/arc_parser_hashed_ud_ewt.npz")

_LEAVE_VERBS = {"leave", "quit", "exit", "depart", "flee", "escape", "withdraw", "retire"}
_POSTURE_VERBS = {"be", "sit", "stand", "lie", "kneel", "wait", "remain", "stay", "linger", "rest",
                  "sleep", "work", "read", "write", "dine", "recline", "crouch", "lounge", "loll", "live"}
# STATIVE-LOCATIVE class (drill: broader than posture -- any predication that commits a figure to a ground for
# the interval SETS the SPACE index; Basic Locative Construction). Posture + existence/position + concealment +
# confinement. Used when stative_expand=True.
_STATIVE_LOC_VERBS = _POSTURE_VERBS | {
    "hide", "shelter", "conceal", "lurk", "hover", "dwell", "reside", "abide", "settle", "camp", "lodge",
    "keep", "confine", "imprison", "detain", "shut", "lock", "seat", "station", "post", "gather", "assemble",
    "wander", "roam", "play", "sing", "toil", "labour", "labor", "watch", "stoop", "squat", "perch"}
# CAUSED-MOTION agent-co-moves ONLY for ACCOMPANIED-motion verbs (drill: lead/bring/take/carry/escort...);
# BALLISTIC/PLACEMENT verbs (send/throw/push/place/put) move ONLY the theme.
_ACCOMPANIED_MOTION = {"lead", "bring", "take", "carry", "escort", "conduct", "usher", "guide", "walk",
                       "drive", "accompany", "convey", "march", "follow", "haul", "drag", "hurry", "help"}
# NON-VERIDICAL governing predicates: an embedded motion under these is REPORTED/counterfactual -> a belief
# world, NOT the primary spatial model (drill: gate embedded routing on veridicality of the embedding verb;
# factive/perception governors -- see/know/hear -- are veridical and NOT listed here, so they ARE routed).
_NON_VERIDICAL_GOV = {"say", "tell", "claim", "deny", "report", "assert", "allege", "suppose", "suggest",
                      "believe", "think", "guess", "reckon", "assume", "fear", "hope", "wish", "dream",
                      "imagine", "doubt", "pretend", "fancy", "expect", "want", "intend", "plan", "mean",
                      "fail", "refuse", "decline", "promise", "threaten", "propose", "wonder"}

# ---- REALIS / noisy-channel gates (the situation-model PRIOR term) ----
# A reader does NOT move a character on an IRREALIS clause (hypothetical / modal / negated / embedded under a
# cognition-or-desire matrix). "if I shall fall through the earth", "she was not going to", "dreamt that she
# was walking" -- none relocate the entity. Suppressing these is part of reading the parse AS EVIDENCE (the
# likelihood is ~0 for an irrealis motion) -- Levy 2008 noisy-channel; the running situation-model prior wins.
_MODALS = {"shall", "should", "would", "could", "might", "may", "must", "ca", "wo", "'ll", "'d", "ll"}
# negation cues; the curly (U+2019) / replacement (U+FFFD) apostrophe variants LitBank produces are built from
# codepoints so the SOURCE stays ASCII (LitBank mangles the apostrophe; "wouldn't"->"would"+"n?t" is also caught
# by _MODALS).
_NEG = {"not", "n't", "never", "no", "nor", "n" + chr(0x2019) + "t", "n" + chr(0xFFFD) + "t"}
_SUBORD_IRREALIS = {"if", "whether", "unless", "though", "although", "lest", "wish"}
_COGNITION_MATRIX = {"wonder", "wish", "dream", "imagine", "suppose", "hope", "think", "fancy", "pretend",
                     "seem", "expect", "doubt", "believe", "consider", "mean", "want", "intend", "plan"}
_DISCOVERY_PARTICLE = {"upon", "across"}   # 'came UPON a table' = perception, not motion-to-scene


def _is_irrealis(toks: Sequence[str], upos: Sequence[str], heads: Dict[int, int], v: int) -> bool:
    """True iff the matrix verb v sits in an irrealis clause (modal/negation child, an if/whether/unless
    before it, or it is embedded under a cognition/desire matrix verb). The PRIOR says: do not update."""
    for i in range(1, len(toks) + 1):
        if heads.get(i) == v and toks[i - 1].lower() in (_MODALS | _NEG):
            return True
    # LINEAR backstop (parse-robust): a modal in the 4 tokens before v (the parser often mis-attaches aux).
    for j in range(max(0, v - 5), v - 1):
        if toks[j].lower() in _MODALS:
            return True
    for i in range(1, v):
        if toks[i - 1].lower() in _SUBORD_IRREALIS:
            return True
    h, hops = heads.get(v), 0
    while h and h != 0 and hops < 3:
        if lemma_verb(toks[h - 1]) in _COGNITION_MATRIX:
            return True
        h, hops = heads.get(h), hops + 1
    return False


def _is_discovery(toks: Sequence[str], heads: Dict[int, int], v: int) -> bool:
    """'came upon / across X' or 'found ...' = perception/discovery, not self-motion into a scene. Read the
    satellite LINEARLY (parse-robust): come/came directly followed within 2 tokens by upon/across."""
    lemma = lemma_verb(toks[v - 1])
    if lemma == "find":
        return True
    if lemma == "come":
        if any(toks[j].lower() in _DISCOVERY_PARTICLE for j in range(v, min(len(toks), v + 2))):
            return True
        return any(heads.get(i) == v and toks[i - 1].lower() in _DISCOVERY_PARTICLE
                   for i in range(1, len(toks) + 1))
    return False

_frontend_cache: Dict[str, object] = {}


def _frontend():
    if "t" not in _frontend_cache:
        _frontend_cache["t"] = PosTagger.load(_POS_ASSET)
        _frontend_cache["p"] = ArcParser.load(_ARC_ASSET)
    return _frontend_cache["t"], _frontend_cache["p"]


# ===========================================================================
# the reader's entity backbone (coref clusters from read()'s own mentions)
# ===========================================================================
_PERSON_PRON = {"he", "she", "him", "her", "his", "hers", "himself", "herself", "they", "them",
                "their", "we", "us", "our"}


def build_backbone(conll_path: str, gaz=None):
    """Return (sents, mentions_by_sent, cluster_name, person_clusters).
      sents            : CoNLL token lists (the reader's OWN tokenization; wtok positions align).
      mentions_by_sent : sent_idx -> [mention dicts] (INCLUDING pronouns -- gold coref resolves them).
      cluster_name     : cluster id -> a display name (most frequent non-pronoun head span, else head).
      person_clusters  : the set of ANIMATE/person clusters (the only valid MOVERS; the goal-over-source
                         asymmetry is animacy-modulated -- Lakusta & Landau 2012 -- and inanimate 'entities'
                         like 'the hall'/'the rabbit-hole' must not be tracked as movers).
    """
    mentions, n_sents = parse_litbank_conll(conll_path, name_gender_map=gaz)
    sents = parse_conll_sentences(conll_path)
    by_sent: Dict[int, List[dict]] = {i: [] for i in range(len(sents))}
    names: Dict[int, Dict[str, int]] = {}
    person: Dict[int, bool] = {}
    for m in mentions:
        si = m["sent_idx"]
        if 0 <= si < len(sents):
            by_sent[si].append(m)
        cid = m["cluster"]
        # animacy: a gendered pronoun mention, or a masc/fem gender/name-gender cue anywhere in the cluster
        is_p = (m["head"] in _PERSON_PRON) or (m.get("gender") in ("masc", "fem")) \
            or (m.get("name_gender") in ("masc", "fem"))
        person[cid] = person.get(cid, False) or is_p
        if not m["is_pronoun"]:
            span = " ".join(m.get("span_toks", [m["head"]]))
            names.setdefault(cid, {}).setdefault(span, 0)
            names[cid][span] += 1
    cluster_name: Dict[int, str] = {}
    for cid, cnts in names.items():
        cluster_name[cid] = max(cnts.items(), key=lambda kv: (kv[1], -len(kv[0])))[0]
    for cid in {m["cluster"] for m in mentions}:
        cluster_name.setdefault(cid, f"cluster{cid}")
    person_clusters = {cid for cid, p in person.items() if p}
    return sents, by_sent, cluster_name, person_clusters


def _cluster_covering(noms: List[dict], tok0: int) -> Optional[int]:
    """The coref cluster of the mention whose span covers 0-based token position tok0 (the reader's coref
    backbone maps the AGENT token -- name OR pronoun -- to its entity). None if no mention covers it."""
    for m in noms:
        start = m["wtok_start"]
        end = start + len(m.get("span_toks", [m["head"]])) - 1
        if start <= tok0 <= end:
            return m["cluster"]
    return None


# ===========================================================================
# motion DECISION: route roles (+ particles/deixis) -> (kind, node)  [OUR-INVENTION-UNDER-TEST]
# ===========================================================================
def _node_from_token(toks: Sequence[str], obj1: Optional[int], place_typing: bool = True) -> Optional[str]:
    """Canonical location node for a 1-based role token index (the head noun of a place PP). None if not a
    place (ATL place-typing rejects 'to a laugh') or a non-locative noun ('in a minute')."""
    if obj1 is None or not (1 <= obj1 <= len(toks)):
        return None
    w = toks[obj1 - 1].lower().strip(".,:;\"'")
    if w in _NON_LOCATIVE_NOUN:
        return None
    if w in _WITHIN_SCENE_GROUND:
        return DEICTIC_SCENE               # moved within the scene -> still present
    node = canon_node(w)
    if node in (None,):
        return None
    if node in (DEICTIC_SCENE, AWAY):
        return node
    if place_typing and not is_place_ground(node):
        return None
    return node


def _verb_particles(toks: Sequence[str], upos: Sequence[str], heads: Dict[int, int], v: int) -> List[str]:
    """Path-satellite particles (upstairs/out/away/indoors/home...) whose head is the matrix verb v. Talmy's
    satellite-framed path -- verb-AGNOSTIC ('she florped out' still departs)."""
    out = []
    for i in range(1, len(toks) + 1):
        if i == v:
            continue
        if heads.get(i) == v and toks[i - 1].lower() in _PLACE_PARTICLE:
            out.append(toks[i - 1].lower())
    return out


def _governing_verb(toks: Sequence[str], upos: Sequence[str], heads: Dict[int, int], v: int):
    """The nearest VERB ancestor of v (its embedding predicate), or None if v attaches to root directly."""
    h, hops = heads.get(v), 0
    while h and h != 0 and hops < 5:
        if upos[h - 1] == "VERB" and h != v:
            return lemma_verb(toks[h - 1])
        h, hops = heads.get(h), hops + 1
    return None


def decide_motion(toks: Sequence[str], upos: Sequence[str], heads: Dict[int, int], v: int,
                  roles: dict, place_typing: bool = True, stative_verbs=None):
    """Map one matrix verb's routed roles to (kind, node, confidence) for its AGENT, or None.

    STRONG-EVIDENCE gating (the noisy-channel LIKELIHOOD term; the PRIOR/persistence lives in the tracker &
    the prior-integration arm). A transition fires ONLY on a genuine motion reading -- a self-MOTION verb,
    an explicit LEAVE/deixis verb, a place PARTICLE (satellite-framed path, verb-agnostic), or a DESTINATION-
    class verb. A bare mis-parsed source/path PP under a NON-motion verb does NOT eject the entity
    (persistence dominates weak evidence -- Zwaan & Radvansky; a missed/spurious source lowers confidence,
    never erases -- Ji & Papafragou 2023). PINNED order: GOAL-over-SOURCE (Talmy; Lakusta & Landau).

    CONFIDENCE (the likelihood weight the prior-integration fold consumes): 3 = explicit named goal / place
    particle (strong); 2 = return-to-scene or a corroborated departure (leave-verb / away-particle) or a
    stative; 1 = a BARE source/path departure (weakest, noisiest -- the signal the prior suppresses when a
    named location is already established)."""
    lemma = lemma_verb(toks[v - 1])
    motion = is_motion_verb(lemma)
    toward = lemma in DEIXIS_TOWARD
    away_deixis = lemma in DEIXIS_AWAY
    leave = lemma in _LEAVE_VERBS
    dest = is_destination_verb(lemma)
    goal_to_agent = (roles.get("goal_belongs_to") != "theme")
    goal_node = _node_from_token(toks, roles.get("goal"), place_typing) if goal_to_agent else None
    loc_node = _node_from_token(toks, roles.get("location"), place_typing)
    src = roles.get("source")
    path = roles.get("path")
    particles = _verb_particles(toks, upos, heads, v)
    part_nodes = [_PLACE_PARTICLE[p] for p in particles]        # values: node str | None(=scene) | '<away>'
    back = any(t.lower() == "back" and heads.get(i + 1) == v for i, t in enumerate(toks))
    motion_reading = motion or leave or away_deixis or toward or dest

    # (1) explicit named GOAL that belongs to the agent, under a motion/destination reading -> arrive.
    if goal_node not in (None, DEICTIC_SCENE, AWAY) and motion_reading:
        return ("arrive", goal_node, 3)
    # (2) place PARTICLE names the destination node (satellite-framed; verb-agnostic path).
    for pn in part_nodes:
        if pn not in (None, "<away>"):
            return ("arrive", pn, 3)                        # 'upstairs' / 'downstairs'
    # (3) RETURN to the scene: an explicit return particle (indoors/inside), a named goal == scene, an
    #     explicit 'back' satellite on a motion/away verb, or toward-deixis self-motion.
    if (None in part_nodes) or (goal_node == DEICTIC_SCENE) or (back and (motion or away_deixis)) \
            or (toward and motion):
        return ("return", DEICTIC_SCENE, 2)
    # (4) DEPARTURE (destination unnamed): a leave-verb, an away-particle, away-deixis self-motion, or a
    #     realized SOURCE/PATH but ONLY under a genuine self-motion verb (not a mis-parsed PP).
    corroborated = leave or ("<away>" in part_nodes) or (away_deixis and motion)
    if corroborated or ((src is not None or path is not None) and motion):
        return ("depart", None, 2 if corroborated else 1)
    # (5) STATIVE: a posture/copula (or, with stative_expand, any position/concealment/confinement) verb with a
    # locative LOCATION role sets the current place (no move).
    posture = stative_verbs if stative_verbs is not None else _POSTURE_VERBS
    if lemma in posture and loc_node not in (None, AWAY):
        return ("stative", loc_node, 2)
    return None


# ===========================================================================
# IN-SUBSTRATE driver: reader's own parse + coref -> abstract motion events -> hdlab tracker
# ===========================================================================
def extract_events_in_substrate(sents: List[List[str]], mentions_by_sent: Dict[int, List[dict]],
                                person_clusters: Optional[set] = None, place_typing: bool = True,
                                realis_gate: bool = False, discovery_gate: bool = False,
                                embedded_route: bool = False, caused_motion_theme: bool = False,
                                stative_expand: bool = False, parse_provider=None
                                ) -> List[Tuple[int, str, Optional[str], int, int]]:
    """Walk the discourse once; per sentence tag+parse (in-substrate), route verbs, map the AGENT (and, with
    caused_motion_theme, the moved THEME) token to its coref cluster (ANIMATE movers only), emit
    (cluster, kind, node, sent_idx, conf). The reader's OWN extraction.

    realis_gate/discovery_gate  = noisy-channel PRIOR filters (drop irrealis / perception-'came-upon').
    embedded_route (WALL 1)     = route motion verbs embedded under a VERIDICAL governor (factive/perception),
                                  gating out non-veridical/reported governors (say/think/... -> belief world,
                                  NOT the primary spatial model). Drill: veridicality, not clause position.
    caused_motion_theme (WALL 2)= 'X brought/led Y into Z' relocates the THEME Y to the goal (Goldberg
                                  caused-motion entailment); the AGENT co-moves ONLY for accompanied-motion verbs.
    stative_expand              = broaden the stative-locative class (concealment/confinement/position) per the
                                  Basic Locative Construction.
    """
    # parse_provider(toks) -> (upos, heads): DEPENDENCY-INJECTED per-read parse (2026-09-03 perf). When the
    # caller (situation_reader._read_space) supplies its OWN already-computed parse (SAME model assets), every
    # sentence is parsed ONCE per read instead of re-parsed here -- byte-identical (same tagger/parser). None
    # -> the standalone frontend (unchanged behavior).
    tagger = parser = None
    if parse_provider is None:
        tagger, parser = _frontend()
    posture = _STATIVE_LOC_VERBS if stative_expand else _POSTURE_VERBS
    events: List[Tuple[int, str, Optional[str], int, int]] = []
    for i, toks in enumerate(sents):
        if not toks or len(toks) > 120:
            continue
        if parse_provider is not None:
            upos, heads = parse_provider(list(toks))
        else:
            upos = tagger.tag(list(toks))
            heads = parser.parse(list(toks), upos).heads
        noms = mentions_by_sent.get(i, [])
        matrix = set(matrix_verbs(toks, upos, heads))
        # WALL 1: consider embedded VERB tokens too, gated on the governing predicate's veridicality.
        cand_verbs = matrix if not embedded_route else \
            [k for k in range(1, len(toks) + 1) if upos[k - 1] == "VERB"]
        for v in cand_verbs:
            if realis_gate and _is_irrealis(toks, upos, heads, v):
                continue
            if discovery_gate and _is_discovery(toks, heads, v):
                continue
            if embedded_route and v not in matrix:
                gov = _governing_verb(toks, upos, heads, v)
                if gov is None or gov in _NON_VERIDICAL_GOV:
                    continue                 # reported / non-veridical embedding -> belief world, skip primary
            roles = route_predicate_arguments(list(toks), upos, heads, v, quotative=True)
            lemma = lemma_verb(toks[v - 1])
            # -- AGENT self-motion (the base path) --
            agent1 = roles.get("agent")
            acid = _cluster_covering(noms, agent1 - 1) if agent1 else None
            agent_tracked = acid is not None and (person_clusters is None or acid in person_clusters)
            mv = decide_motion(toks, upos, heads, v, roles, place_typing=place_typing, stative_verbs=posture)
            if agent_tracked and mv is not None:
                kind, node, conf = mv
                events.append((acid, kind, node, i, conf))
            # -- WALL 2: CAUSED-MOTION theme relocation ('brought/led Y into Z') --
            if caused_motion_theme and roles.get("goal_belongs_to") == "theme":
                gnode = _node_from_token(toks, roles.get("goal"), place_typing)
                theme1 = roles.get("theme")
                tcid = _cluster_covering(noms, theme1 - 1) if theme1 else None
                theme_tracked = tcid is not None and (person_clusters is None or tcid in person_clusters)
                if gnode not in (None, DEICTIC_SCENE, AWAY) and theme_tracked:
                    events.append((tcid, "arrive", gnode, i, 3))          # theme ends at the goal (entailed)
                    if agent_tracked and lemma in _ACCOMPANIED_MOTION:    # agent co-moves only if accompanied
                        events.append((acid, "arrive", gnode, i, 3))
    return events


def fold_tracker(clusters: Sequence[int], events: Sequence[Tuple[int, str, Optional[str], int, int]],
                 n_clauses: int, prior_fold: bool = False) -> LocationRegister:
    """Fold abstract (cluster, kind, node, t, conf) motion events into the PROMOTED hdlab tracker (start
    everyone present at t=0).

    prior_fold = the noisy-channel REVISE-ON-SURPRISE step (Sinclair 2021; Zwaan & Radvansky persistence): a
    LOW-confidence departure (conf 1 -- a bare source/path PP, the parser's noisiest signal) is SUPPRESSED
    when the entity already sits at a confidently-established NAMED place. Weak evidence does not eject a
    character from a known room; the prior (persistence) wins. High/med-confidence events always apply."""
    reg = LocationRegister()
    reg.start([str(c) for c in clusters], n_clauses=n_clauses)
    cur_named: Dict[str, bool] = {}     # cluster -> currently at a confidently-named place
    for ev in sorted(events, key=lambda e: (e[3], e[0])):
        cid, kind, node, t, conf = ev
        key = str(cid)
        if key not in reg.tracks or kind not in MOTION_KINDS:
            continue
        if prior_fold and kind == "depart" and conf <= 1 and cur_named.get(key):
            continue                    # persistence dominates weak, unnamed-destination evidence
        reg.apply_motion(key, kind, node, t)
        if kind == "arrive" and node not in (DEICTIC_SCENE, AWAY):
            cur_named[key] = True
        elif kind in ("depart", "return"):
            cur_named[key] = False
    return reg


def read_locations_in_substrate(conll_path: str, gaz=None, place_typing: bool = True, mode: str = "truth",
                                parse_provider=None):
    """End-to-end: the reader's OWN backbone -> in-substrate motion events -> promoted tracker.
    mode='truth'     = parse-as-truth (no prior; every extracted event applied -- the discriminator baseline).
    mode='prior'     = parse-as-EVIDENCE + situation-model PRIOR (realis + discovery gates + revise-on-surprise).
    mode='prior_ext' = 'prior' + the drill's three brain-faithful recall extensions (veridical embedded-clause
                       routing + caused-motion theme relocation + expanded stative locatives).
    Returns (register, events, cluster_name, sents, person_clusters)."""
    sents, by_sent, cluster_name, person_clusters = build_backbone(conll_path, gaz=gaz)
    prior = mode in ("prior", "prior_ext")
    ext = (mode == "prior_ext")
    events = extract_events_in_substrate(sents, by_sent, person_clusters=person_clusters,
                                         place_typing=place_typing, realis_gate=prior, discovery_gate=prior,
                                         embedded_route=ext, caused_motion_theme=ext, stative_expand=ext,
                                         parse_provider=parse_provider)
    reg = fold_tracker(sorted(person_clusters), events, n_clauses=len(sents), prior_fold=prior)
    return reg, events, cluster_name, sents, person_clusters


# ===========================================================================
# probe (viability check on real prose -- NOT a gold measurement)
# ===========================================================================
if __name__ == "__main__":
    import sys
    path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        _REPO, "data/litbank/coref/conll/11_alices_adventures_in_wonderland_brat.conll")
    for mode in ("truth", "prior"):
        reg, events, names, sents, persons = read_locations_in_substrate(path, mode=mode)
        print(f"\n=== mode={mode}  {os.path.basename(path)}  sents={len(sents)}  "
              f"events={len(events)}  persons={len(persons)} ===")
        for (cid, kind, node, t, conf) in events[:30]:
            print(f"  s{t:>3} c{conf} {names.get(cid, str(cid)):<16} {kind:<8} {str(node):<12}"
                  f"  :: {' '.join(sents[t])[:80]}")
        from collections import Counter
        movers = Counter(cid for e in events for cid in [e[0]])
        for cid, _c in movers.most_common(2):
            tl = [reg.where_is(str(cid), t) for t in range(len(sents))]
            print(f"  timeline {names.get(cid, cid)!r}: "
                  + " ".join(f"{t}:{tl[t]}" for t in range(len(sents)) if t == 0 or tl[t] != tl[t - 1]))
