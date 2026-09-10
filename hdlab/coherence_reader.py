"""hdlab/coherence_reader.py -- a glass-box SDRT-lite DISCOURSE COHERENCE reader.

Promoted (owner-DONE sdrt_discourse_coherence_reader_for_temporal_order_and_unmarked_causal_inference_on_
real_prose, Q111 strategy landing 2026-09-07) from the solver cell experiments/_sdrt_coherence.py -- the
CoherenceReader / directed_plausibility / the physics+psychology+GOAL causal-plausibility engines / aspect
route / the means-end gate / kintsch_select are UNCHANGED in behaviour (the CoherenceReader class body is
byte-identical to the reference; only the two experiments-side imports are re-homed, see DEPENDENCY NOTE).
This module is the REUSABLE coherence-inference core -- the corpus-measurement harnesses (TB-Dense /
TellMeWhy / the mechanism minimal-pairs / the diagnostic / the lever-survey cells) stay in experiments.

Infers the coherence relation between two ADJACENT discourse units from CAUSAL-WORLD-KNOWLEDGE (a
generative causal-plausibility simulator), NOT surface connectives, and maps it (Lascarides-Asher DICE)
to a temporal-order edit + an unmarked causal edge. NO external LLM (the invariant).

RELATIONS (SDRT-lite): NARRATION, RESULT, EXPLANATION, BACKGROUND, ELABORATION.

BRAIN GROUNDING (PINNED -- copy the COMPUTATION):
  * Coherence is INFERRED by defeasible/abductive reasoning over world knowledge, NOT read off connective
    words (Hobbs 1985; Hobbs, Stickel, Appelt & Martin 1993 "Interpretation as Abduction"; Kehler 2002
    Cause-Effect coherence; constructionist "search after meaning" Graesser-Singer-Trabasso 1994; Kintsch
    1988 construction-integration).
  * SDRT/DICE (Lascarides & Asher 1993; Asher & Lascarides 2003): the RELATION fixes the temporal/causal
    reading via defeasible axioms + the INDEFEASIBLE "Causes Precede Effects" (cause(e1,e2) -> e1<e2):
      NARRATION(e1,e2)   => e1<e2, no overlap (the Narration default).
      RESULT(e1,e2)      => cause(e1,e2): forward, e1<e2; insert causal edge e1->e2.
      EXPLANATION(e1,e2) => cause(e2,e1): e2<e1 -- REVERSE surface order; insert causal edge e2->e1.
      BACKGROUND(e1,e2)  => the units OVERLAP (States-Overlap law, keyed to STATIVITY -- NOT causal).
      ELABORATION(e1,e2) => e2 is a subevent/part-of e1 (mereological, Moens-Steedman -- NOT causal).
  * The Narration/Result/Explanation discriminator is causal PLAUSIBILITY (the causality-by-default reading,
    Sanders): does the later unit plausibly CAUSE the earlier (Explanation) or vice versa (Result)?
  * Division confirmed by a literature drill (2026-09-07): Background/Elaboration are ASPECTUAL/mereological,
    NOT causal -- so they route to the ASPECT signal (stativity), never the causal engine. Only the
    Narration/Result/Explanation family is decided by causal plausibility.
  * The dominant NARRATIVE causal engine is REASON/GOAL causation (Malle 1999 reason-vs-cause; Trabasso goal
    chains; Graesser goal hierarchies) -- measured 36% of TellMeWhy non-adjacent causes, the largest single
    type; it is load-bearing on its category (the info-free twin LOSES CI-sep) and is default-ON WITHIN this
    channel (the coherence channel itself lands DEFAULT-OFF; see the SOLVED's measured full-population
    trade-off + the un-built generative-world-model completing lever).

OUR-INVENTION-UNDER-TEST (sweep, don't adopt): the causal-plausibility ENGINE composition + weights
(base=class-level engines; deepened=FrameNet force typer + implicit-causality psych-verb direction); the
override CONFIDENCE threshold tau + directional MARGIN (default-to-prior, override iconicity/adjacency only
on a CONFIDENT directed asymmetry -- the causal reasoner's U5 cue-integration discipline); the relation
granularity.

REUSE (all landed hdlab organs): hdlab.event_type (MENTAL_TRIGGER/MENTAL_OUTCOME + STATIVE) +
hdlab.affect_lexicon (Warriner valence appraisal) + hdlab.force_dynamics_typer (FrameNet CAUSE/ENABLE force
lexicon, deepened physics) + hdlab.psych_verb_frames (implicit-causality experiencer direction) +
hdlab.goal_register (the PINNED desire/intention/try matrix-verb lexicon = the landed GOAL dimension).

DEPENDENCY NOTE (honest deviation, reported at landing -- NO experiments dep):
  * The associative CONTENT relatedness (`relatedness`) reads the SAME static offline asset
    data/frontend_assets/associative_similarity_store_v1.npz that hdlab.goal_hierarchy_graph loads (the
    landed associative-similarity store; a STATIC ADMISSIBLE FOUNDATION, no external LLM at inference). The
    loader is inlined here rather than imported from experiments.exp_causal_reasoner_densify_v1 so this
    module carries NO experiments dependency.
  * FORCE_ACTION / RESULT_STATE are the U8 class-level physics closed sets, inlined verbatim from
    experiments._causal_network (a copied closed-class CONSTANT, not a code dependency) -- same reason.
Glass-box, deterministic, numpy-only for the associative store (heavy hdlab organs imported LAZILY at
first use). NO external LLM.
"""
from __future__ import annotations

__bf_status__ = 'BF_SPIRIT'   # BF | BF_SPIRIT | NOT_BF | BF_UNPINNED | BF_UNVERIFIED ; mirrors notes/bf_status_registry.jsonl
__bf_verified__ = '2026-09-09 BF-certification pass (operation/math read of the pinned computation + key ops; strategy first-hand)'
__bf_note__ = 'SDRT-lite discourse coherence: directed plausibility + physics/psychology/GOAL causal-plausibility + means-end gate + Kintsch select (owner-DONE); pinned SDRT frame; DORMANT (track_coherence=False)'
__bf_corrections__ = []


import os
import re
import sys
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

# ---- U8 class-level physics closed sets (Talmy CAUSE; inlined verbatim from the reference; a copied
# closed-class CONSTANT, NOT an experiments dependency). An ACTION verb (an agonist exerting force) beside a
# RESULT change-of-state verb of the affected entity = the class-level force-dynamic CAUSE cue.
FORCE_ACTION = {
    "caught", "slipped", "stopped", "threw", "struck", "pushed", "hit", "shouted",
    "dropped", "seized", "grabbed", "knocked", "kicked", "flung", "tripped", "shoved",
    "hurled", "swung", "plunged", "dashed", "hurtled",
}
RESULT_STATE = {
    "fell", "started", "shattered", "broke", "burst", "flared", "spilled", "crashed",
    "tumbled", "toppled", "snapped", "rolled", "collapsed", "staggered", "reeled",
}

# ---- associative CONTENT relatedness over the landed static store (same asset hdlab.goal_hierarchy_graph
# loads). Lazy singleton; glass-box cosine; NO external LLM.
_ASSOC_NPZ = os.path.join(_REPO, "data", "frontend_assets", "associative_similarity_store_v1.npz")
_ASSOC = None


def _assoc():
    global _ASSOC
    if _ASSOC is None:
        import numpy as np
        d = np.load(_ASSOC_NPZ, allow_pickle=True)
        W = d["words"]; V = d["vecs"].astype(np.float32)
        V = V / (np.linalg.norm(V, axis=1, keepdims=True) + 1e-9)
        _ASSOC = (V, {str(w).lower(): i for i, w in enumerate(W)})
    return _ASSOC


def relatedness(a: str, b: str) -> Optional[float]:
    """Associative (ATL-hub) content relatedness in [-1,1]; None if either word is out of the store.
    Reads the landed data/frontend_assets/associative_similarity_store_v1.npz (a STATIC OFFLINE asset)."""
    try:
        V, w2i = _assoc()
    except Exception:
        return None
    ia, ib = w2i.get((a or "").lower()), w2i.get((b or "").lower())
    if ia is None or ib is None:
        return None
    return float(V[ia] @ V[ib])


# ---- relation labels ------------------------------------------------------
NARRATION = "NARRATION"
RESULT = "RESULT"
EXPLANATION = "EXPLANATION"
BACKGROUND = "BACKGROUND"
ELABORATION = "ELABORATION"
CAUSAL_FAMILY = (NARRATION, RESULT, EXPLANATION)   # the ones decided by causal plausibility
RELATIONS = (NARRATION, RESULT, EXPLANATION, BACKGROUND, ELABORATION)

_ET_CACHE: Dict[str, str] = {}
_AFF = None
_FORCE_LEX = None
_PSYCH = None
_GOAL_VERBS = None


def _goal_verbs():
    """The PINNED goal/desire/intention matrix-verb lexicon (Levin desiderative/volition/intention/try
    classes; Malle reason-vs-cause -- the 'reason' engine is decisively separate from physical cause).
    Reused from hdlab.goal_register (the landed GOAL dimension)."""
    global _GOAL_VERBS
    if _GOAL_VERBS is None:
        try:
            from hdlab.goal_register import GOAL_VERBS
            _GOAL_VERBS = set(GOAL_VERBS)
        except Exception:
            _GOAL_VERBS = {"want", "wanted", "wish", "wished", "hope", "hoped", "decide", "decided",
                           "plan", "planned", "try", "tried", "intend", "intended", "need", "needed"}
    return _GOAL_VERBS


def _etype(lemma: str) -> str:
    if lemma not in _ET_CACHE:
        from hdlab.event_type import event_type
        _ET_CACHE[lemma] = event_type(lemma)
    return _ET_CACHE[lemma]


def _aff():
    global _AFF
    if _AFF is None:
        from hdlab.affect_lexicon import AffectLexicon
        _AFF = AffectLexicon.load()
    return _AFF


def _force_lex():
    """FrameNet CAUSE/ENABLE/PREVENT force lexicon (deepened physics). Falls back to None if FrameNet
    (nltk data) is unavailable -- callers then use the U8 closed-set physics."""
    global _FORCE_LEX
    if _FORCE_LEX is None:
        try:
            from hdlab.force_dynamics_typer import build_force_lexicon
            _FORCE_LEX = build_force_lexicon(use_cache=True) or {}
        except Exception:
            _FORCE_LEX = {}
    return _FORCE_LEX


def _psych():
    global _PSYCH
    if _PSYCH is None:
        try:
            from hdlab.psych_verb_frames import PsychVerbFrames
            _PSYCH = PsychVerbFrames.load()
        except Exception:
            _PSYCH = False
    return _PSYCH


# ---------------------------------------------------------------------------
# CONFIG (swept, not adopted)
# ---------------------------------------------------------------------------
@dataclass
class PlausibilityConfig:
    """Toggle each generative engine + set weights. `deepened` swaps the U8 class-level physics/psych
    for the FrameNet force typer + implicit-causality experiencer direction. Ablations set the toggles."""
    content: bool = True
    physics: bool = True
    psych_appraisal: bool = True
    psych_cascade: bool = True
    goal: bool = False                # GOAL/INTENTIONAL causation (Malle reason-cause; Trabasso goal chains)
    goal_meansend: bool = False       # gate the goal engine on the means-end satisfaction match (precision)
    deepened: bool = False            # use force_dynamics_typer + psych_verb_frames IC direction
    w_physics: float = 1.0
    w_psych: float = 1.0
    w_goal: float = 1.0
    content_floor: float = 0.02


@dataclass
class CoherenceConfig:
    """The reader's decision policy (swept). tau = min causal plausibility to leave NARRATION; margin =
    directional asymmetry required to commit to RESULT/EXPLANATION; use_aspect routes Background/Elaboration."""
    plaus: PlausibilityConfig = field(default_factory=PlausibilityConfig)
    tau: float = 0.05
    margin: float = 0.15              # relative asymmetry (b vs a) needed to override the telling-order prior
    use_aspect: bool = True


@dataclass
class Relation:
    """One inferred coherence relation between adjacent units (a narrated first, b second)."""
    label: str
    confidence: float                 # directional-asymmetry magnitude (0 for NARRATION default)
    forward: float                    # plausibility a causes b (Result)
    backward: float                   # plausibility b causes a (Explanation)
    provenance: str                   # which engine fired (content/physics/psych/aspect/none)


def _content_words(words: Sequence[str]) -> List[str]:
    return [w for w in words if len(w) > 2 and re.match(r"^[a-z']+$", w)]


def _max_relatedness(aw: Sequence[str], bw: Sequence[str]) -> float:
    rel = 0.0
    for x in set(_content_words(aw)):
        for y in set(_content_words(bw)):
            r = relatedness(x, y)
            if r is not None and r > rel:
                rel = r
    return rel


def _sent_valence(words: Sequence[str]) -> Optional[float]:
    aff = _aff()
    vs = [aff._warriner(w) for w in words if aff._warriner(w) is not None]
    return float(sum(vs) / len(vs)) if vs else None


def _has_emotion_valence(words: Sequence[str]) -> Optional[float]:
    aff = _aff()
    for w in words:
        if aff.is_emotion_word(w):
            v = aff._warriner(w)
            return v if v is not None else 0.0
    return None


def _physics_fires(a_lemmas: Sequence[str], b_lemmas: Sequence[str],
                   b_words: Sequence[str], cfg: PlausibilityConfig) -> Tuple[float, str]:
    """Does A's action FORCE-generate B's result-state? Returns (strength, provenance)."""
    al, bl = set(a_lemmas), set(b_lemmas)
    if not cfg.deepened:
        if (al & FORCE_ACTION) and (bl & RESULT_STATE):        # U8 class-level closed sets
            return 1.0, "physics"
        return 0.0, ""
    # DEEPENED: FrameNet force typer -- A has a CAUSE/ENABLE force verb, B reaches a change-of-state endstate
    lex = _force_lex()
    if lex:
        from hdlab.force_dynamics_typer import force_dynamic_type, detect_endstate_reached
        reached = detect_endstate_reached([w.lower() for w in b_words])
        for l in a_lemmas:
            t = force_dynamic_type(l, reached, lex)
            if t in ("CAUSE", "ENABLE"):
                return (1.0 if t == "CAUSE" else 0.6), "physics_fn"
    # back-off to the closed set even when deepened (superset)
    if (al & FORCE_ACTION) and (bl & RESULT_STATE):
        return 1.0, "physics"
    return 0.0, ""


def _psych_fires(a_words, b_words, a_lemmas, b_lemmas, cfg: PlausibilityConfig) -> Tuple[float, str]:
    """Does A's event psychologically GENERATE B's mental/expressive reaction? Appraisal valence-congruence
    (Warriner) + mental TRIGGER->OUTCOME cascade (event_type); deepened adds implicit-causality direction."""
    strength, prov = 0.0, ""
    if cfg.psych_appraisal:
        b_emo = _has_emotion_valence([w.lower() for w in b_words])
        if b_emo is not None:
            av = _sent_valence([w.lower() for w in a_words])
            if av is not None and abs(av) > 0.05 and (av * b_emo) > 0:   # same-sign appraisal
                strength, prov = 1.0, "psych_appraisal"
    if cfg.psych_cascade:
        from hdlab.event_type import MENTAL_TRIGGER, MENTAL_OUTCOME
        if any(_etype(l) in MENTAL_TRIGGER for l in a_lemmas) and \
           any(_etype(l) in MENTAL_OUTCOME for l in b_lemmas):
            if 0.6 > strength:
                strength, prov = 0.6, "psych_cascade"
    if cfg.deepened:
        # IMPLICIT-CAUSALITY direction (Garvey-Caramazza; psych_verb_frames): an OBJECT-experiencer verb
        # in B ("frightened", "angered") attributes the CAUSE to the stimulus (A) -> A explains B.
        pv = _psych()
        if pv:
            for l in b_lemmas:
                if pv.is_psych_verb(l):
                    pos = pv.experiencer_position(l)
                    if pos == "object":      # stimulus-subject verb: the prior event is the cause
                        strength = max(strength, 0.8)
                        prov = prov or "psych_ic"
                        break
    return strength, prov


_GOAL_STOP = {"the", "a", "an", "his", "her", "their", "my", "your", "our", "its", "to", "of", "for",
              "and", "or", "it", "them", "him", "up", "out", "back", "down", "so", "that", "not"}


def _goal_span(a_words) -> List[str]:
    """The goal-OBJECT / satisfaction-condition span: the content words AFTER the goal/desire matrix verb
    (or after 'to'). e.g. 'she wanted MILK' -> ['milk']; 'to BUY BREAD' -> ['buy','bread']."""
    gv = _goal_verbs()
    aw = [w.lower() for w in a_words]
    start = None
    for i, w in enumerate(aw):
        if w in gv or w == "to":
            start = i + 1
            break
    if start is None:
        return []
    return [w for w in aw[start:] if w.isalpha() and w not in _GOAL_STOP and len(w) > 2]


def _goal_fires(a_words, a_lemmas, b_words, b_lemmas, means_end: bool = False) -> Tuple[float, str]:
    """GOAL / INTENTIONAL (reason) causation -- the engine physics+appraisal lack. A (cause) expresses a
    DESIRE/INTENTION/GOAL (a Levin desiderative/intention/try matrix verb, or a bare 'to'+VINF purpose) and
    B (effect) is an ACTION serving it. Malle 1999/2004: the 'reason' engine is decisively separate from
    physical cause (reason categories d=0.4-0.7 where generic cause/effect give null); Trabasso goal chains
    are the DOMINANT narrative causal category.

    means_end=False -> the coarse Tier-1 version (goal marker present -> fire): high recall, OVER-FIRES on
    non-goal pairs. means_end=True -> the MEANS-END SATISFACTION MATCH (Csibra-Gergely teleological
    efficiency / Baker-Saxe-Tenenbaum inverse planning): fire ONLY when B's action plausibly SERVES the
    goal-OBJECT (relatedness(goal_span, B) is real) -- the precision gate that stops the over-firing. This
    is the genuinely-distinct computation (a symbolic/relational check, not a force-sum). Still Tier-1
    anchored (an explicit desire marker); NOT full inverse planning over latent goals (the Tier-2 wall)."""
    gv = _goal_verbs()
    aw = [w.lower() for w in a_words]
    has_goal = bool(set(a_lemmas) & gv) or bool(set(aw) & gv)
    if not has_goal and "to" in aw:
        ti = aw.index("to")
        if ti + 1 < len(aw) and aw[ti + 1].isalpha() and aw[ti + 1] not in ("the", "a", "an", "his", "her"):
            has_goal = True
    if not (has_goal and b_lemmas):
        return 0.0, ""
    if not means_end:
        return 0.8, "goal"
    # MEANS-END: does B's action/content serve the goal-object in A?
    span = _goal_span(a_words)
    bw = [w.lower() for w in b_words if w.isalpha() and len(w) > 2]
    me = 0.0
    for x in set(span):
        for y in set(bw):
            r = relatedness(x, y)
            if r is not None and r > me:
                me = r
    # fire proportional to the means-end relatedness (gated): a served goal -> strong; unrelated -> ~0
    if me <= 0.05:
        return 0.0, ""
    return min(1.0, 0.4 + me), "goal_meansend"


def directed_plausibility(a_words, a_lemmas, b_words, b_lemmas,
                          cfg: Optional[PlausibilityConfig] = None) -> Tuple[float, str]:
    """Directed causal-plausibility that A (cause) GENERATES B (effect). Composes the intuitive-physics +
    intuitive-psychology engines over the associative CONTENT signal (which specific effect):
        score = base_content * (1 + w_phys*physics + w_psych*psych)
    Weights set by PRINCIPLE (a structural simulation match multiplies the content score), not fit to gold.
    Returns (score, provenance)."""
    cfg = cfg or PlausibilityConfig()
    aw, bw = [w.lower() for w in a_words], [w.lower() for w in b_words]
    base = max(_max_relatedness(aw, bw), cfg.content_floor) if cfg.content else 1.0
    phys, pprov = (_physics_fires(a_lemmas, b_lemmas, b_words, cfg) if cfg.physics else (0.0, ""))
    psy, sprov = (_psych_fires(a_words, b_words, a_lemmas, b_lemmas, cfg)
                  if (cfg.psych_appraisal or cfg.psych_cascade or cfg.deepened) else (0.0, ""))
    goal, gprov = (_goal_fires(a_words, a_lemmas, b_words, b_lemmas, means_end=cfg.goal_meansend)
                   if cfg.goal else (0.0, ""))
    score = base * (1.0 + cfg.w_physics * phys + cfg.w_psych * psy + cfg.w_goal * goal)
    prov = pprov or sprov or gprov or ("content" if base > cfg.content_floor else "none")
    return score, prov


def plausibility_components(a_words, a_lemmas, b_words, b_lemmas,
                            cfg: Optional[PlausibilityConfig] = None) -> Dict[str, float]:
    """The per-ENGINE cue contributions for a directed pair (A causes B), exposed for a KINTSCH
    construction-integration SETTLING stage (which needs the separable cues, not just their product).
    Returns {content, physics, psych, goal}."""
    cfg = cfg or PlausibilityConfig()
    aw, bw = [w.lower() for w in a_words], [w.lower() for w in b_words]
    base = max(_max_relatedness(aw, bw), cfg.content_floor) if cfg.content else 1.0
    phys = _physics_fires(a_lemmas, b_lemmas, b_words, cfg)[0] if cfg.physics else 0.0
    psy = (_psych_fires(a_words, b_words, a_lemmas, b_lemmas, cfg)[0]
           if (cfg.psych_appraisal or cfg.psych_cascade or cfg.deepened) else 0.0)
    goal = (_goal_fires(a_words, a_lemmas, b_words, b_lemmas, means_end=cfg.goal_meansend)[0]
            if cfg.goal else 0.0)
    return {"content": base, "physics": phys, "psych": psy, "goal": goal}


def kintsch_select(cands: List[Dict[str, float]], inhib: float = 0.5, iters: int = 30,
                   corroborate: bool = True) -> Optional[int]:
    """KINTSCH construction-integration SELECTION (the 'integration' the product-of-experts lacks).
    cands = per-candidate {content, physics, psych, goal}. CONSTRUCTION: initial evidence e = content *
    (1 + phys + psych + goal * corroboration), where the goal cue is TRUSTED only in proportion to its
    CONTENT corroboration (a goal cue on a low-content isolated candidate is incoherent -> discounted;
    'resonance proposes, necessity/coherence disposes'). INTEGRATION: iterative interactive activation
    with LATERAL INHIBITION (a[i] <- relu(e[i] - inhib * sum_{j!=i} a[j]); renormalize) settling to a
    stable pattern that suppresses weakly-corroborated candidates. Returns the settled argmax index."""
    import numpy as np
    if not cands:
        return None
    cont = np.array([c["content"] for c in cands], float)
    med = float(np.median(cont[cont > 0])) if np.any(cont > 0) else 1.0
    corr = np.clip(cont / (med + 1e-9), 0.0, 1.0) if corroborate else np.ones_like(cont)
    e = cont * (1.0 + np.array([c["physics"] for c in cands])
                + np.array([c["psych"] for c in cands])
                + np.array([c["goal"] for c in cands]) * corr)
    a = e.copy()
    for _ in range(iters):
        tot = a.sum()
        nxt = np.maximum(0.0, e - inhib * (tot - a))
        m = nxt.max()
        if m <= 0:
            break
        nxt = nxt / m
        if np.allclose(nxt, a, atol=1e-6):
            a = nxt
            break
        a = nxt
    return int(np.argmax(a)) if a.max() > 0 else None


# ---------------------------------------------------------------------------
# THE COHERENCE READER
# ---------------------------------------------------------------------------
class CoherenceReader:
    """Infer the SDRT-lite coherence relation between adjacent units (a first, b second) from causal
    plausibility (+ aspect for Background/Elaboration), confidence-gated so it OVERRIDES the telling-order
    / adjacency prior only on a confident directed asymmetry."""

    def __init__(self, cfg: Optional[CoherenceConfig] = None) -> None:
        self.cfg = cfg or CoherenceConfig()

    def relate(self, a_words, a_lemmas, b_words, b_lemmas,
               a_stative: Optional[bool] = None, b_stative: Optional[bool] = None) -> Relation:
        c = self.cfg
        f, fp = directed_plausibility(a_words, a_lemmas, b_words, b_lemmas, c.plaus)
        r, rp = directed_plausibility(b_words, b_lemmas, a_words, a_lemmas, c.plaus)
        # ASPECT route (NOT causal): a stative unit beside an eventive one => BACKGROUND (overlap).
        if c.use_aspect:
            asv = self._stative(a_lemmas) if a_stative is None else a_stative
            bsv = self._stative(b_lemmas) if b_stative is None else b_stative
            if asv != bsv and (asv or bsv):
                return Relation(BACKGROUND, 0.0, f, r, "aspect")
        # CAUSAL family: is either direction plausibly causal, and is it asymmetric?
        strong = max(f, r)
        if strong < c.tau:
            return Relation(NARRATION, 0.0, f, r, "none")
        # relative directional asymmetry (avoid div0)
        if r > f * (1.0 + c.margin):
            return Relation(EXPLANATION, r - f, f, r, rp)
        if f > r * (1.0 + c.margin):
            return Relation(RESULT, f - r, f, r, fp)
        return Relation(NARRATION, 0.0, f, r, "symmetric")   # causal but no confident direction

    def _stative(self, lemmas: Sequence[str]) -> bool:
        from hdlab.event_type import event_type
        return any(event_type(l) == "STATIVE" for l in lemmas)

    # -- DICE consequences -------------------------------------------------
    @staticmethod
    def order_edit(rel: Relation) -> str:
        """The temporal consequence: 'reverse' (Explanation), 'overlap' (Background/Elaboration),
        or 'forward' (Narration/Result -- keep telling order)."""
        if rel.label == EXPLANATION:
            return "reverse"
        if rel.label in (BACKGROUND, ELABORATION):
            return "overlap"
        return "forward"

    @staticmethod
    def causal_edge(rel: Relation, a_key: str, b_key: str) -> Optional[Tuple[str, str]]:
        """The inserted UNMARKED causal edge (cause, effect): RESULT => a->b; EXPLANATION => b->a."""
        if rel.label == RESULT:
            return (a_key, b_key)
        if rel.label == EXPLANATION:
            return (b_key, a_key)
        return None


def shuffle_labels(labels: Sequence[str], seed: int) -> List[str]:
    """The info-free TWIN: permute the inferred coherence labels across items, preserving the exact
    relation-count distribution. Proves the correction uses THIS pair's inferred relation, not a shape
    artifact (a relation-count-matched shuffle: same #Explanation etc., assigned to random pairs)."""
    import numpy as np
    rng = np.random.default_rng(seed)
    out = list(labels)
    rng.shuffle(out)
    return out


# ---------------------------------------------------------------------------
# self-test: the mechanism fires on the canonical Lascarides-Asher contrasts
# ---------------------------------------------------------------------------
def _selftest() -> None:
    rd = CoherenceReader()
    # (A) EXPLANATION (no connective, reversed order): "Max fell. John had pushed him." (Lascarides-Asher)
    #     b (pushed, a FORCE_ACTION) plausibly causes a (fell, a RESULT_STATE) -> reverse order, edge b->a.
    #     NB: the plain-language "he had spilt water" needs a DEEPER/KG engine (spill->wet->slip is a 2-hop
    #     world-knowledge chain the class-level closed set does not carry -- the documented coverage wall).
    rel = rd.relate(["fell"], ["fell"], ["pushed", "him"], ["pushed"])
    assert rel.label == EXPLANATION, f"Explanation not inferred: {rel}"
    assert CoherenceReader.order_edit(rel) == "reverse"
    assert CoherenceReader.causal_edge(rel, "fell", "pushed") == ("pushed", "fell")
    # (B) RESULT (forward causation): "Max pushed the vase. It shattered."
    rel2 = rd.relate(["pushed", "vase"], ["pushed"], ["shattered"], ["shattered"])
    assert rel2.label == RESULT, f"Result not inferred: {rel2}"
    assert CoherenceReader.order_edit(rel2) == "forward"
    # (C) NARRATION default when neither direction is causally plausible (two unrelated motions).
    rel3 = rd.relate(["walked"], ["walked"], ["sat"], ["sat"])
    assert rel3.label in (NARRATION,), f"Narration default violated: {rel3}"
    assert CoherenceReader.order_edit(rel3) == "forward"
    # (D) directed asymmetry: forward != backward on the physics pair (else it could not discriminate)
    f, _ = directed_plausibility(["pushed"], ["pushed"], ["shattered"], ["shattered"])
    r, _ = directed_plausibility(["shattered"], ["shattered"], ["pushed"], ["pushed"])
    assert f > r, f"physics not directed: f={f} r={r}"
    print("[hdlab.coherence_reader] self-test PASS: Explanation/Result/Narration inferred; physics directed "
          "(f=%.3f > r=%.3f); DICE order-edit + causal-edge mapping correct" % (f, r))


if __name__ == "__main__":
    _selftest()
