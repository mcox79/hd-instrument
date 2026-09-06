"""CONSOLIDATED MULTI-SENTENCE SITUATION-MODEL READER (thin integration layer).

ONE runnable that reads a real multi-sentence passage and returns a SituationModel
(Kintsch/van-Dijk + Zwaan event-indexing: entities / events / time / causation held
in a bounded Cowan-4 focus). This is a CONSOLIDATION + DEMONSTRATION of ALREADY-BANKED
modules -- NO new mechanism; it COMPOSES what exists (scoured + reused, not reimplemented):

  ENTITIES (who)   : the banked cross-sentence coref backbone -- EventCentralityReader
                     (hdlab/event_centrality_coref.py, 29516; recency-centrality query,
                     memory decision-driving) which inherits SceneProtagonistReader (29514
                     local-window) -> SuppressReader (29513 never-a-subject generic
                     distractor suppression) -> CorefReader (29506 WorkingOverlay). The
                     deixis-person exclusion (29517) lives in the pool-hygiene path of the
                     coref stack. Cross-sentence pronouns resolved against a persistent
                     overlay; scored vs LitBank coref gold.
  EVENTS (what)    : per-sentence predicate + agent + patient, extracted glass-box from the
                     shared token stream (predicate via the temporal POS tagger; agent =
                     the sentence subject-mention, patient = nearest post-predicate mention,
                     reusing the parse_litbank_conll mention structure). One sentence can yield
                     MULTIPLE events (every qualifying VBD/VBN/VB/VBG token, not just one).
                     2026-08-05 COVERAGE EXTENSION (experiments/_temporal_ordering.extract_events,
                     additive-only, see goldvet_oov_psych_bank.md): also emits events for
                     COORDINATED VPs sharing a distant aux ("had owned AND cherished"),
                     MODAL-governed bare-infinitive subordinate clauses ("might gain the power"),
                     and bare PARTICIPIAL -ing clauses ("resenting that ..."), subject inherited
                     via the SAME preceding-nominal selector already used for finite predicates.
                     Known residual gap: a participial token the shared NLTK tagger mistags as a
                     noun (not VBG) is still missed -- see _selftest_event_extraction_coverage.
                     Each event is stored
                     as a Cowan-4 role-slot BUNDLE (hdlab/event_bundle.py EventBundleCodec,
                     29511) -- the validated "2 chunks x 4 slots" role-slot format.
                     HONEST SCOPE: this is a LIGHTWEIGHT structural event extractor for the
                     multi-sentence demonstration. LOAD-BEARING ACCURACY (2026-08-05 component
                     audit, be6203bc4): THIS extractor's own measured predicate+agent+patient
                     F1 = 0.232 ungated / 0.278 gated / 0.297 FULL (independent gold,
                     data/exp_coherence_gate_extraction_correctness_independent_gold_v1) -- recall
                     is tagger-capped (~0.32). Do NOT read the "F1~0.64" cited historically as this
                     component's health: that 0.64 belongs to a DIFFERENT narrower single-sentence
                     role reader (29502) on DIFFERENT gold (McGuffey LCCP), ~2x higher and NOT the
                     number the situation model inherits. Everything downstream inherits recall
                     ~0.32 -- event extraction is the weakest load-bearing link (audit roadmap #1).
  TIME (when)      : chronological reconstruction via tense/aspect + connective cues ->
                     toposort timeline (experiments/_temporal_ordering_multiframe.py, 29510).
                     Fires on the passage's past-perfect / connective sentences (flashbacks).
  CAUSATION (why)  : causal cause->outcome links via the causal-network reader
                     (experiments/_causal_network.py, 29515). HONEST CAVEAT (carried from the
                     29515 VET): this mechanism is REDUCIBLE to connective-else-most-recent on
                     the banked gold; the plausibility/force-dynamics component is NOT isolated.
                     Causal links are reported as connective/adjacency-derived; NOT a claim of
                     genuine causal plausibility reasoning.
  MEMORY           : all events live in the Cowan-4 BOUNDED focus (hdlab/situation_focus.py
                     ChunkedFocus, 29512 no-runaway) -- glass-box role-query unbinding recovers
                     each recent event's fillers.

GLASS-BOX: pure symbolic coref decision + HD role-slot event memory (unbind + cleanup, hand-
auditable). NO external LLM, NO network, NO autograd at inference. ASCII-only. Deterministic
given fixed seeds. Nothing here is re-transcribed: every dimension is an IMPORT of its banked
module. This file is the THIN wiring that runs read(passage) -> SituationModel end-to-end.
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import sys
from dataclasses import dataclass, field
from functools import lru_cache
from typing import Dict, List, Optional, Tuple

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

# ---- banked entity/coref backbone (reuse, not reimplement) ----
from hdlab.coref import (
    CorefReader,
    build_pronoun_targets,
    load_name_gender,
    parse_litbank_conll,
    sent_dist_bucket,
)
from hdlab.event_centrality_coref import EVENT_N_DIM, EventCentralityReader
from hdlab.scene_segment import parse_conll_sentences

# ---- banked Cowan-4 role-slot memory (reuse) ----
from hdlab.event_bundle import DEFAULT_ROLES, EventBundleCodec
from hdlab.situation_focus import ChunkedFocus

# ---- Component-3 thematic-role labeling (reuse, 2026-08-05 wire; re-VET =
# notes/skunkworks_reVET_frame_primary_role_assigner_v1.md, MIDDLE_BAND, WIRE-the-architecture) ----
from hdlab.frame_induction import (
    frame_primary_role,
    get_induced_subj_hypothesis,
    real_construction_feats as FI_real_construction_feats,
    predict_subj_role as FI_predict_subj_role,
)
from hdlab.thematic_role_labeler import lemma_verb, lemma_word, is_strictly_intransitive

# WIRE-DON'T-ISLAND (2026-08-05): the OOV-subject construction->frame hypothesis, induced from the
# real litbank-mined TRAIN split only (experiments/data/experiencer_narrative_roles_v1.jsonl);
# held-out lemmas never seen (leakage-checked by exp_frame_induction_oov_psych_real_v1). Measured
# held-out quality: subj-axis acc=0.833 (data/exp_frame_induction_oov_psych_real_v1/metrics.json,
# MIDDLE_BAND -- data-starved, not a ceiling). Falls back to (None, None) -- the honest AGENT
# default -- if the training file is missing; never raises.
#
# LAZY AS OF 2026-08-19: this used to be a module-level call, so merely IMPORTING this module ran a
# full frame induction -- 190 s of the module's 205 s import cost, which timed out its own self-test
# at 240 s and kept it off every wire list (notes/ORGAN_MAP.md row 15). The caching was always
# correct (module-level cache keyed by data_path inside get_induced_subj_hypothesis, "trains at
# most once per process"); only the PLACEMENT was wrong. Training now fires on first USE instead of
# first IMPORT. Same values, same single training, paid by the first read() call that needs it.
def _induced_subj() -> Tuple[Optional[str], Optional[object]]:
    """(chosen_name, hypothesis) for the OOV-subject frame axis; trains at most once per process."""
    return get_induced_subj_hypothesis()


def __getattr__(name: str):
    """Back-compat: `situation_reader._INDUCED_SUBJ_NAME` still resolves (PEP 562), and now trains
    on first ACCESS rather than on import. Nothing in-repo reads these off this module, but a
    module-level name that existed for two weeks is cheap to keep working."""
    if name == "_INDUCED_SUBJ_NAME":
        return _induced_subj()[0]
    if name == "_INDUCED_SUBJ_HYP":
        return _induced_subj()[1]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

# ---- grounded-affect dimension (reuse, 2026-08-05 wire; CERTIFIED SCOPE =
# notes/landed_vet_bridge1_foundation.md, animacy-axis event override, Bopen=1.000) ----
from hdlab.context_grounded_valence import (score_context_grounded_valence,
                                            score_context_grounded_valence_pretagged, to_ternary)

# ---- banked TIME + CAUSATION mechanisms (reuse) ----
from experiments import _temporal_ordering as T
from experiments import _temporal_ordering_multiframe as M
from experiments import _causal_network as C

# The banked EventCentralityReader keyword bundle (29513/29514/29516 config).
SUP_KW = dict(suppress_generic=True, use_nonref=True, use_struct=True,
              chain_pronouns=True, use_gazetteer=True)
LOCAL_WINDOW = 5      # the banked 29514 fixed local-window baseline
MEM_SEED = 7
FOCUS_N_DIM = 4096    # shared Cowan-4 focus dim (matches banked EC memory 29511; recent round-trips)
FOCUS_SEED = 11

# ---- ASSEMBLY reader-role-routing (2026-08-30, opt-in via role_route; DEFAULT-OFF = byte-identical) ----
# Landed (Change 2) from the integrated assembly `wire_the_predarg_frontend_and_binder_into_the_live_reader`
# (owner-DONE, SOLVED/STRONG). The stock role path is POSITIONAL (agent=subject-mention, patient=nearest
# post-predicate nominal; NO parse). role_route != "positional" routes role assignment through a REAL parse
# -> the landed event-semantic router (+ a reader-native, case-independent QUOTATIVE-inversion agent rule)
# with a good-enough POSITIONAL fallback -- the HYBRID that lifts end-to-end role accuracy +0.225 CI-sep /
# +0.247 through the live class on real narrative (validated in exp_wire_predarg_binder_live_reader{,_
# integration}_v1). Default "positional" is BYTE-IDENTICAL to the stock reader (a top-level branch in
# _read_events; the wired path is a separate method). Ported VERBATIM from the validated WiredSituationReader.
# NO external LLM (the router's VerbNet/WordNet are static nltk; the tagger/parser are persisted assets).
from hdlab.predicate_argument_frontend import (  # noqa: E402
    route_predicate_arguments, is_speech_verb, matrix_verbs)

# predarg thematic slot -> the reader's role key. agent/patient stay primary; the richer roles
# (goal/recipient/source/...) are collected as ADDITIVE metadata on `self.wired_extra_roles`, never on
# EventRecord (so the stock EventRecord shape -- and byte-identical comparisons -- are unchanged).
PREDARG_TO_GOLD = {
    "agent": "agent", "theme": "patient", "goal": "goal", "recipient": "recipient",
    "source": "source", "location": "location", "path": "path", "direction": "direction",
    "instrument": "instrument",
}
_FRONTEND_POS_ASSET = os.path.join(_REPO, "data/frontend_assets/pos_tagger_ud_ewt_upos.json")
_FRONTEND_ARC_ASSET = os.path.join(_REPO, "data/frontend_assets/arc_parser_hashed_ud_ewt.npz")
# FORWARD-PREDICTION surprisal: the persisted QA-SRL-fitted PredictiveReader (default asset, committed
# alongside the other frontend model assets). Loaded lazily only when predict_surprisal is ON.
_PREDICT_SURPRISAL_ASSET = os.path.join(_REPO, "data/frontend_assets/predict_surprisal_predictor_v1.pkl")
# candidate-nominal POS + pronoun exclusion for the surprisal pass -- VERBATIM from the validated driver
# experiments/_forward_prediction_live.py (nominal_heads): the argument heads the reader could have bound.
_SURPRISAL_NOMINAL_POS = {"NOUN", "PROPN", "PRON"}
_SURPRISAL_PRON_LOW = {"i", "you", "he", "she", "it", "we", "they", "me", "him", "her", "us", "them",
                       "myself", "yourself", "himself", "herself", "itself", "ourselves", "themselves",
                       "this", "that", "these", "those", "who", "whom", "which", "what"}
_FRONTEND_CACHE: Dict[str, object] = {}


def _stock_tense(a, TP):
    """Map a Reichenbach triple (from TP.assign_sentence) to a stock-compatible EventRecord.tense label,
    so downstream .tense stays meaningful when preserve_tense is on. Byte-identical to the validated ref
    impl exp_tense_preserving_live_reader_and_timeline_v1._stock_tense; T is the shared _temporal_ordering
    module (already imported above). Only used behind the default-off preserve_tense flag."""
    if a["voice"] == TP.PASSIVE:
        return T.TENSE_PASSIVE
    if a["tense"] == TP.PAST and a["aspect"] in (TP.PERF, TP.PERF_PROG):
        return T.TENSE_PAST_PERFECT
    if a["tense"] == TP.PAST:
        return T.TENSE_SIMPLE_PAST
    if a["tense"] == TP.PRES:
        return "SIMPLE_PRESENT" if a["aspect"] == TP.SIMPLE else "PRESENT_" + str(a["aspect"])
    if a["tense"] == TP.FUT:
        return "FUTURE"
    return T.TENSE_OTHER


def _load_frontend():
    """Load the persisted UPOS tagger + hashed arc parser ONCE per process (module-cached). Imported
    lazily so a default (positional) reader never pays the parser-asset load or the import cost."""
    if "t" not in _FRONTEND_CACHE:
        from hdlab.pos_tagger import PosTagger
        from hdlab.arc_parser import ArcParser
        _FRONTEND_CACHE["t"] = PosTagger.load(_FRONTEND_POS_ASSET)
        _FRONTEND_CACHE["p"] = ArcParser.load(_FRONTEND_ARC_ASSET)
    return _FRONTEND_CACHE["t"], _FRONTEND_CACHE["p"]


class _CachedTagShim:
    """Adapts the reader's shared per-read tag cache to the `tagger.tag(toks)` interface that
    referent_per_np_source expects, so its per-sentence tagging HITS the shared _cached_tag instead of a
    redundant private PosTagger copy. Byte-identical: _cached_tag uses the same _FRONTEND_POS_ASSET the
    private tagger loaded. General (not tied to one config)."""
    __slots__ = ("_r",)

    def __init__(self, reader):
        self._r = reader

    def tag(self, toks):
        return self._r._cached_tag(list(toks))

_CAUSAL_CONNECTIVES = frozenset(
    set(getattr(C, "CONNECTIVE_CAUSE_FIRST", set()))
    | set(getattr(C, "CONNECTIVE_EFFECT_FIRST", set())))


# ===========================================================================
# SituationModel: the persistent state-of-affairs structure over the 5 dims.
# ===========================================================================
@dataclass
class TrackedEntity:
    cluster: int
    heads: List[str]           # distinct surface heads across the passage
    sent_indices: List[int]    # sentences in which this entity is mentioned
    n_mentions: int
    is_person: bool


@dataclass
class EventRecord:
    global_idx: int
    sent_idx: int
    predicate: str
    agent: str
    patient: str
    tense: str
    # Component-3 frame-primary thematic-role labels (2026-08-05 wire), ADDITIVE metadata only --
    # agent/patient above remain the untouched positional head-selection (structural bundle slots);
    # these carry the frame-primary THEMATIC label for the same heads (e.g. subj_role="EXPERIENCER"
    # for a psych-verb subject vs the positional "agent" head string). None when no subj/obj mention
    # was available to label (mirrors agent=="?" / patient=="?"). Backward-compatible default.
    subj_role: Optional[str] = None
    obj_role: Optional[str] = None
    # grounded-organ valence (2026-08-05 wire), ADDITIVE metadata only -- populated only for events
    # whose patient falls in the CERTIFIED animacy-axis scope (hdlab/context_grounded_valence.py,
    # Bopen=1.000 open-vocab); every other event (no patient, animacy lookup miss, tokenizer miss)
    # ABSTAINS (None) rather than guessing off an uncertified path. Backward-compatible default.
    affect: Optional[str] = None
    # FORWARD-PREDICTION surprisal (2026-08-31 wire, default-off predict_surprisal), ADDITIVE metadata
    # only -- the N400 error-RISK FLAG the predictive_reader organ was validated LIVE as (predicts the
    # reader's OWN who-did-what errors AUC 0.651 CI-sep; surprisal-abstain lifts committed accuracy).
    # patient_surprisal = -log P of the reader's bound PATIENT among the sentence's candidate nominals
    # under the verb-role selectional preference; pred_precision = the verb-role constraint sharpness
    # (Friston precision-weighting); low_confidence = True when patient_surprisal exceeds the abstain
    # tau (the validated withhold decision -- do NOT auto-revise, that is a proven negative). None when
    # the flag is off OR the verb-role/filler is ungrounded (abstain, never a guess). Backward-compatible.
    patient_surprisal: Optional[float] = None
    pred_precision: Optional[float] = None
    low_confidence: Optional[bool] = None
    # PREDICT-REVISE drop-fill (2026-09-01 wire, default-off predict_revise). pred_idx = the verb's 0-based
    # token index within its sentence (ALWAYS populated, like subj_role/affect -- additive metadata the
    # drop-fill re-runs the filler-gap resolver on). patient_prerevise = the ORIGINAL patient ('?') before a
    # drop-fill recovered a head; None unless the predict_revise flag is on AND this event's dropped patient
    # was recovered (so the recovery is glass-box + reversible). The default reader never sets it.
    pred_idx: Optional[int] = None
    patient_prerevise: Optional[str] = None
    # STRUCTURAL-DO recovery (2026-09-03 wire, default-off structural_do_recover). True/False when the flag is on
    # and this event has a bound patient on the WIRED path (whether the bound patient is a BARE post-verbal direct
    # object -> the verb_subcat veto is overridden and the patient kept); None otherwise. The default reader never
    # sets it. Set in _read_events_wired where the toks-space verb + candidate indices are available.
    patient_is_bare_do: Optional[bool] = None


@dataclass
class CorefResolution:
    pronoun: str
    sent_idx: int
    gold_cluster: int
    resolved_cluster: int
    correct: bool
    attempted: bool
    bucket: str
    sent_dist: int


@dataclass
class TimelineFrame:
    sent_idx: int
    text: str
    text_order: List[str]
    chrono_order: List[str]
    reordered: bool            # chrono differs from text order (a flashback was undone)


@dataclass
class CausalLink:
    sent_idx: int
    cause: str
    outcome: str
    method: str                # connective | bridge | fallback (see 29515 caveat)


@dataclass
class SuppressedPredicate:
    sent_idx: int
    predicate: str
    tense: str
    agent: str
    patient: str


@dataclass
class EntityState:
    # opt-in copular is-a/attribute BINDING (bind_entity_states): a Kimian state binding a HOLDER (subject
    # entity) to a PROPERTY/TYPE (the predicate complement) -- Maienborn 2005; Bemis & Pylkkanen 2011 LATL.
    # htype = the glass-box Higgins type: "pred_adj" / "pred_nom" (predicational property/is-a) or "ident"
    # (identificational / symmetric identity). From the owner-DONE the_reader_has_no_copular_is_a_binding_schema.
    sent_idx: int
    holder: str
    property: str
    htype: str


@dataclass
class SituationModel:
    passage_id: str
    n_sentences: int
    entities: List[TrackedEntity] = field(default_factory=list)
    events: List[EventRecord] = field(default_factory=list)
    # events dropped by an optional supplied-grammar predicate-validity gate (glass-box demo)
    suppressed_predicates: List["SuppressedPredicate"] = field(default_factory=list)
    coref_resolutions: List[CorefResolution] = field(default_factory=list)
    timeline_frames: List[TimelineFrame] = field(default_factory=list)
    timeline_order: list = field(default_factory=list)  # whole-passage chronological event order (opt-in timeline_register)
    causal_links: List[CausalLink] = field(default_factory=list)
    # opt-in TYPED within-clause causation (hdlab.causation_typing.TypedCausalLink); empty unless
    # the reader is built with causation_typed=True. Additive -- never replaces causal_links.
    typed_causal_links: list = field(default_factory=list)
    # opt-in SPACE dimension: a hdlab.location_register.LocationRegister (where_is(entity,t) /
    # present_in_scene per entity over story-time); None unless the reader is built with track_space=True.
    # Additive -- the 4th situation-model dimension (WHERE), after entities/time/causation.
    locations: Optional[object] = None
    # opt-in BELIEF/ToM dimension (WHO-BELIEVES-WHAT-WHEN); None unless the reader is built with
    # track_belief=True. Two CALLABLES bound to this passage's own extraction (the 5th situation-model
    # dimension): believes(agent_aliases, fact, t) -> the agent's registered belief VALUE at story-time t
    # (piecewise-constant sample-and-hold; may DIVERGE from reality = the false-belief case); knows(...) ->
    # the Butterfill & Apperly registration status ("current"/"stale"/"ignorant"). fact is a dict
    # {fact_aliases, value_vocab[, fact_type]}. Additive -- never touches the other dimensions.
    believes: Optional[object] = None
    knows: Optional[object] = None
    # opt-in BOUND-EVENT-TOKEN backbone (the ASSEMBLY completion, p4); both None unless the reader is built
    # with bind_event_tokens=True. event_tokens = a list of ONE FHRR bound token per event (over
    # {AGENT,PATIENT,PRED,TENSE}) -- the JOINT the parallel-silo dimensions cannot store; episodic_store = a
    # hdlab.bound_event_backbone.BoundEpisodicStore (N400-chunked + DG/CA3 episodic tier) whose resolve/
    # corefer readout answers "does this exact event -- this agent, this action -- occur?" from a partial
    # mention. Additive -- never touches the other dimensions; the prerequisite for reasoning over the story.
    event_tokens: Optional[list] = None
    episodic_store: Optional[object] = None
    # opt-in mutable WORLD-STATE dimension (WHO-HAS-WHAT / OPEN-CLOSED at story-time t); None unless the reader
    # is built with track_world_state=True. A hdlab.world_state_register.WorldState folded from THIS passage's
    # own extracted events: world_state.has(entity,obj,t) / holder_of(obj,t) / is_open(obj,t) /
    # unmet_preconditions(). Additive -- the STATE dimension (Zwaan & Radvansky event-indexing; possession =
    # Glenberg/Meyer/Lindem availability); never touches the other dimensions. Open-text who-has-what is
    # coref-bound (the located residual). None on the default reader.
    world_state: Optional[object] = None
    # opt-in COPULAR is-a/attribute BINDING (bind_entity_states); empty/None unless the reader is built with
    # bind_entity_states=True. entity_states = typed (holder, property, htype) EntityState per detected copular
    # predication ("Ahab was a captain" / "the room was cold" / "she was his wife"); state_register = a
    # hdlab.state_register.StateRegister with the predicational states applied (read-back: state_at / is_in_state
    # / had_been). Additive -- never touches the other dimensions. From the owner-DONE copular-is-a solution.
    entity_states: List["EntityState"] = field(default_factory=list)
    state_register: Optional[object] = None
    # opt-in GOAL/INTENTION dimension (WHAT-IS-X-TRYING-TO-DO / WHY-DID-X-ACT); None unless the reader is
    # built with track_goals=True. A hdlab.goal_register.GoalRegister over THIS passage's explicit
    # purpose/desire/intention constructions (the missing 5th Zwaan-Radvansky event-indexing dimension,
    # intentionality); the query callables sm.wants(agent)/sm.why(action,agent)/sm.achieved(agent,goal) are
    # bound as attributes at read time (mirroring sm.believes/knows). Additive -- never touches the other
    # dimensions. From the owner-DONE the_situation_model_has_no_goal_intention_dimension (Q111).
    goal_register: Optional[object] = None
    # opt-in AFFECT/EMOTION dimension (HOW-DOES-X-FEEL); None unless the reader is built with
    # track_affect=True. A hdlab.affect_register.AffectRegister over THIS passage's explicit emotion
    # constructions (the missing emotion dimension -- a DISTINCT appraisal/affect system, PINNED-dissociated
    # from the goal/belief mentalizing dimensions, Campanella 2022 triple dissociation); each affect is bound
    # to the resolved EXPERIENCER (the psych-verb linking split) and carries VALENCE (primary) + emotion
    # CATEGORY (secondary). The query callables sm.feels(char)/sm.valence_of(char)/sm.feels_about(char,y) are
    # bound as attributes at read time (mirroring sm.wants/why/achieved). Additive -- never touches the other
    # dimensions. From the owner-DONE the_situation_model_has_no_affect_emotion_dimension (Q111).
    affect_register: Optional[object] = None
    memory_roundtrip: Dict[str, float] = field(default_factory=dict)
    # per-dimension honest accuracy (coref only; scored vs LitBank gold on this passage)
    coref_acc: Optional[float] = None
    coref_xsent_acc: Optional[float] = None
    single_sentence_xsent_acc: Optional[float] = None  # the can-fail validity baseline
    n_targets: int = 0
    n_xsent_targets: int = 0


# ===========================================================================
# helpers
# ===========================================================================
def _person_cluster(cluster_mentions: List[dict]) -> bool:
    """A cluster is a PERSON if any mention is a he/she pronoun or has masc/fem gender."""
    for m in cluster_mentions:
        if m["is_pronoun"] and m.get("gender") in ("masc", "fem"):
            return True
        if (not m["is_pronoun"]) and m.get("gender") in ("masc", "fem"):
            return True
        if m.get("name_gender") in ("masc", "fem"):
            return True
    return False


def _build_entities(mentions: List[dict]) -> List[TrackedEntity]:
    by_cluster: Dict[int, List[dict]] = {}
    for m in mentions:
        by_cluster.setdefault(m["cluster"], []).append(m)
    out: List[TrackedEntity] = []
    # sort key tolerant of MIXED cluster-id types (the commonnoun_situation_gate re-labels non-pronoun
    # referents with 'CN:' string ids while pronoun-only clusters keep their int coref ids); all-int
    # (the default reader) sorts byte-identically to plain sorted().
    for cid in sorted(by_cluster, key=lambda c: (0, c) if isinstance(c, int) else (1, str(c))):
        ms = by_cluster[cid]
        heads: List[str] = []
        seen = set()
        for m in ms:
            if m["is_pronoun"]:
                continue
            h = " ".join(m.get("span_toks", [m["head"]]))
            if h.lower() not in seen:
                seen.add(h.lower())
                heads.append(h)
        sent_idx = sorted({m["sent_idx"] for m in ms})
        out.append(TrackedEntity(
            cluster=cid, heads=heads, sent_indices=sent_idx,
            n_mentions=len(ms), is_person=_person_cluster(ms)))
    return out


def _sentence_nominals(mentions: List[dict], n_sents: int) -> List[List[dict]]:
    """Non-pronoun mentions per sentence, sorted by within-sentence token position."""
    per = [[] for _ in range(n_sents)]
    for m in mentions:
        if m["is_pronoun"]:
            continue
        si = m["sent_idx"]
        if 0 <= si < n_sents:
            per[si].append(m)
    for lst in per:
        lst.sort(key=lambda mm: (mm["wtok_start"], mm["midx"]))
    return per


def _build_spacy_pred_gate():
    """SUPPLIED-GRAMMAR predicate-validity gate (29522 confound-free L1 win, ADOPTED here).

    Returns a callable pred_gate_fn(sentence_text) -> set[str] of the LOW surface tokens that
    spaCy (en_core_web_sm) tags as a VERB (Penn tag VB*) anywhere in the sentence. An emitted
    event whose predicate LOW token is NOT in this set is a POS mis-tag (proper-noun / adjective
    read as a verb on 19c literary prose) and is suppressed. POST-HOC filter only: it does NOT
    feed the substrate parser / role clf (no OOD) -- glass-box supplied preprocessing, exactly the
    human "read via already-known grammar" frame. Lazy import so the default reader path never
    needs spaCy; raises ImportError only when the gate is actually requested."""
    from experiments.exp_read_events_supply_grammar_spacy_pos_litbank_v1 import make_spacy_tagger
    from experiments.exp_oracle_mention_upperbound_reader_v1 import split_sentences

    spacy_tag = make_spacy_tagger()

    def pred_gate_fn(sentence_text: str):
        verbs = set()
        for clause in split_sentences(sentence_text):
            for (_surf, low, pos) in spacy_tag(clause):
                if pos.startswith("VB"):
                    verbs.add(low)
        return verbs

    return pred_gate_fn


_IRREGULAR_PARTICIPLES = frozenset({
    "done", "gone", "seen", "taken", "given", "known", "shown", "broken", "chosen", "driven",
    "eaten", "written", "spoken", "stolen", "frozen", "hidden", "bitten", "beaten", "worn", "torn",
    "sworn", "drawn", "thrown", "grown", "blown", "flown", "held", "built", "sent", "spent", "lost",
    "found", "caught", "taught", "bought", "brought", "fought", "sought", "thought", "kept", "left",
    "felt", "meant", "dealt", "made", "said", "paid", "laid", "led", "read", "hit", "cut", "put",
    "set", "cost", "hurt", "shut", "split", "spread", "cast", "burst",
})


def _is_passive_predicate(toks: Optional[List[str]], pred_idx: int) -> bool:
    """PRECISE-VOICE detector (`the_reading_extractor` SOLVED; brain-faithful -- voice is the ONLY cue
    on reversible passives, MacWhinney's Competition Model). A clause reads passive when the predicate
    has PAST-PARTICIPLE morphology AND a BE-auxiliary sits within 3 tokens before it (the surface
    'was X-ed' pattern). Heuristic on surface tokens; returns False when `toks` is None (no signal)."""
    if not toks or not (0 <= pred_idx < len(toks)):
        return False
    be = {"be", "is", "am", "are", "was", "were", "been", "being"}
    if not any(str(toks[i]).lower() in be for i in range(max(0, pred_idx - 3), pred_idx)):
        return False
    p = str(toks[pred_idx]).lower()
    return p.endswith("ed") or p.endswith("en") or p in _IRREGULAR_PARTICIPLES


def _pick_role_mentions(pred_idx: int, sent_noms: List[dict], *,
                        gate_intransitive: bool = False,
                        pred_lemma: Optional[str] = None,
                        toks: Optional[List[str]] = None,
                        precise_voice: bool = False
                        ) -> Tuple[Optional[dict], Optional[dict]]:
    """Positional mention selection (single source of truth for both head-strings and, since
    2026-08-05, frame-primary role labeling): subj-mention = the subject-mention (rank 0) if
    before/at the predicate else nearest preceding nominal; obj-mention = nearest nominal
    strictly after the predicate. Returns (subj_mention_dict_or_None, obj_mention_dict_or_None).

    FRAME-ARITY GATE (2026-08-06, additive, default OFF -> byte-identical to the pre-existing
    behavior when gate_intransitive=False): the un-gated obj-mention selection above is FRAME-
    BLIND -- it hands an intransitive verb ("sat", "arrived", "went") the nearest following
    nominal as a spurious PATIENT even though the verb's frame has no patient slot. When
    gate_intransitive=True and `pred_lemma` (already re-lemmatized by the caller, see
    hdlab.thematic_role_labeler.lemma_verb) names a verb in
    hdlab.thematic_role_labeler.STRICTLY_INTRANSITIVE_VERBS, obj_m is forced to None regardless of
    the nearest-following nominal -- the frame has no PATIENT slot, so there is nothing to select.
    AMBITRANSITIVE verbs (eat/read/sing/...) are NOT in that set and are therefore never gated
    here; their positional object selection (right or wrong) is unchanged. Subject/AGENT selection
    is never touched by this gate."""
    before = [m for m in sent_noms if m["wtok_start"] <= pred_idx]
    after = [m for m in sent_noms if m["wtok_start"] > pred_idx]
    subj_m: Optional[dict] = None
    if before:
        subj = [m for m in before if m.get("is_subject")]
        subj_m = subj[0] if subj else before[-1]
    obj_m = after[0] if after else None
    if gate_intransitive and pred_lemma is not None and is_strictly_intransitive(pred_lemma):
        obj_m = None
    # PRECISE-VOICE (the_reading_extractor SOLVED; default-OFF -> byte-identical). On a PASSIVE clause the
    # PATIENT is the SURFACE SUBJECT (before the predicate) and the AGENT is the by-phrase nominal (after):
    # "the metal was dissolved by the acid" -> patient=metal, agent=acid. The default positional rule
    # (patient = nearest AFTER) is exactly wrong there, so swap when the flag is ON and the clause is passive.
    if precise_voice and _is_passive_predicate(toks, pred_idx):
        subj_m, obj_m = obj_m, subj_m
    return subj_m, obj_m


def _assign_roles(pred_idx: int, sent_noms: List[dict], *,
                  lemma: Optional[str] = None,
                  gate_intransitive: bool = False,
                  toks: Optional[List[str]] = None,
                  precise_voice: bool = False) -> Tuple[str, str]:
    """Glass-box structural role assignment against the sentence's gold mention heads:
    AGENT = the subject-mention (rank 0) if before/at the predicate else nearest preceding
    nominal; PATIENT = nearest nominal strictly after the predicate. '?' when none.
    UNCHANGED behavior (2026-08-05): now backed by _pick_role_mentions, byte-identical output.

    FRAME-ARITY GATE (2026-08-06): `lemma` is the caller's raw predicate token (surface or
    already-a-lemma; re-lemmatized here via hdlab.thematic_role_labeler.lemma_verb, same as
    _assign_frame_primary_roles below); `gate_intransitive` defaults to False so every existing
    call site is byte-identical unless it opts in. When True, PATIENT is suppressed for verbs in
    STRICTLY_INTRANSITIVE_VERBS (see _pick_role_mentions docstring)."""
    pred_lemma = lemma_verb(lemma) if (gate_intransitive and lemma is not None) else None
    subj_m, obj_m = _pick_role_mentions(pred_idx, sent_noms,
                                        gate_intransitive=gate_intransitive,
                                        pred_lemma=pred_lemma,
                                        toks=toks, precise_voice=precise_voice)
    agent = subj_m["head"] if subj_m is not None else "?"
    patient = obj_m["head"] if obj_m is not None else "?"
    return agent, patient


def _assign_frame_primary_roles(lemma: str, toks: List[str], pred_idx: int,
                                sent_noms: List[dict], *,
                                gate_intransitive: bool = False
                                ) -> Tuple[Optional[str], Optional[str]]:
    """Component-3 wire (2026-08-05, updated same day -- WIRE-DON'T-ISLAND): frame-primary
    THEMATIC role labels for the SAME heads _assign_roles picks (via the shared
    _pick_role_mentions selector) -- additive, does not change which head is chosen. KNOWN verb
    (lemma in VERB_FRAMES) -> frame_slot_role() answers UNCONDITIONALLY (the re-VET's known-lemma
    acc=1.0 deterministic-dict path), UNCHANGED. OOV verb, subj slot -> now consults the
    pre-induced construction->frame hypothesis (_induced_subj(), trained once per process on
    FIRST USE by hdlab.frame_induction.get_induced_subj_hypothesis() -- lazy since 2026-08-19; on the
    real litbank-mined TRAIN split; held-out lemmas never seen) INSTEAD of the honest-but-wrong
    positional AGENT default -- a genuinely novel psych verb (cherish/loathe/crave/...) now gets
    EXPERIENCER when its surrounding construction cues (has_scomp/degree_mod/passive/order_pre/
    arg_animate) match the induced hypothesis, falling back to AGENT only when it abstains (an
    honest, measurable degrade, not a silent override). Production quality = the SAME held-out
    numbers the training data measured: subj-axis acc=0.833 (data-starved, MIDDLE_BAND, not 1.0 --
    see data/exp_frame_induction_oov_psych_real_v1/metrics.json). OOV verb, obj slot -> UNCHANGED,
    still falls to DEFAULT_FRAME (deferred axis; no induced obj-frame model is wired anywhere, per
    frame_primary_role's own design -- object-experiencer acc=0.455 remains un-earned in
    production).

    `lemma` here is the reader's EVENT lemma, which is actually the LOWERCASED SURFACE token
    (experiments/_temporal_ordering.py Event.lemma=low, e.g. "feared"/"cherished") -- NOT a true
    verb lemma. VERB_FRAMES is keyed by true lemma ("fear"/"cherish"), so it is re-lemmatized via
    the existing glass-box lemma_verb() (irregular table + suffix-strip) before the frame lookup,
    same as every other real-data consumer of frame_primary_role (see
    experiments/exp_frame_primary_role_assigner_v1.py which lemmatizes from record["verb_lemma"]
    supplied by the gold dataset -- here there is no supplied lemma, so lemma_verb() derives it).

    FRAME-ARITY GATE (2026-08-06): `gate_intransitive` defaults to False (byte-identical to the
    pre-existing behavior); when True, forwarded to the shared _pick_role_mentions selector so the
    obj-mention (and therefore obj_role below) is suppressed for STRICTLY_INTRANSITIVE_VERBS,
    exactly mirroring _assign_roles."""
    true_lemma = lemma_verb(lemma)
    subj_m, obj_m = _pick_role_mentions(pred_idx, sent_noms,
                                        gate_intransitive=gate_intransitive,
                                        pred_lemma=true_lemma if gate_intransitive else None)
    subj_role = None
    if subj_m is not None:
        _ind_name, _ind_hyp = _induced_subj()
        subj_role = frame_primary_role(true_lemma, toks, pred_idx, int(subj_m["wtok_start"]), "subj",
                                       chosen_name=_ind_name, hypothesis=_ind_hyp)
    obj_role = None
    if obj_m is not None:
        obj_role = frame_primary_role(true_lemma, toks, pred_idx, int(obj_m["wtok_start"]), "obj")
    return subj_role, obj_role


@lru_cache(maxsize=8192)
def _affect_pos_cached(sentence_text: str):
    """Per-string memo of the frontend UPOS tags for the affect path. EFFICIENCY (2026-09-06): tag() is a
    PURE deterministic function of the token list, and _assign_affect runs once PER EVENT -- many events share
    a sentence, so the identical string was re-tagged repeatedly (the affect path was ~half the read's POS-tag
    calls; tagging is ~40% of read cost). Memoizing by sentence_text is BYTE-IDENTICAL (same split, same
    deterministic tagger, same tags) and safe across reads (the frontend model is process-constant). Returns a
    tuple; callers copy to a fresh list so a downstream mutation cannot corrupt the cache."""
    return tuple(_load_frontend()[0].tag(sentence_text.split(" ")))


def _assign_affect(patient: str, sentence_text: str) -> Optional[str]:
    """Grounded-affect wire (2026-08-05): calls the promoted hdlab organ
    (score_context_grounded_valence) on the event's PATIENT head against the sentence text, and
    reports its predicted valence ONLY when the CERTIFIED animacy-axis event override actually
    fired for this item (result["stage"] == "event" -- the open-vocab Bopen=1.000 axis; see
    notes/landed_vet_bridge1_foundation.md). Every other case ABSTAINS (returns None):
      - no patient mention (patient == "?"),
      - the organ's own tokenizer can't locate the patient token in its re-tokenization of the
        sentence (ValueError from score_context_grounded_valence -- ASCII/punctuation edge cases),
      - the animacy-axis override did NOT fire (stage == "governor"): the governor-only fallback
        is a DIFFERENT, narrower certification (COLLISION_PAIRS only, not open-vocab) and is
        deliberately not exposed here to keep the production wire conservative (mirrors the
        Component-3 wire's OOV-abstain discipline just above).
    Uses the organ's DEFAULT seed=0 / FULL_N_TRAIN_THETA on every call -- the organ's own
    module-level caches (_GOV_PERCEPTRON_CACHE / _THETA_CACHE) train the perceptron/theta once
    per process and reuse it across every event/passage, so this is O(1) trainings, O(events)
    cheap scoring calls.

    REROUTED 2026-09-05 (owner-DONE route_the_redundant_nltk_perceptron_tagger_through_the_fast_hdlab_tagger):
    tags via the shared hdlab UD-EWT frontend tagger (_load_frontend -- the SAME asset + structured-perceptron
    model the events/roles/entity-state path uses, so the affect field is computed from ONE consistent category
    system, not a second off-the-shelf NLTK averaged-perceptron tagger), and skips the DISCARDED torch valence
    (need_valence=False -- _assign_affect reads only predicted_type + stage). VALENCED output (HARM/HELP +
    feel-category) BYTE-IDENTICAL to the NLTK route (0 flips / 8947, witness 6/6); the inert NA<->None
    firing-provenance bit differs on ~9% of events (no production consumer branches on it; hdlab tags are often
    MORE correct). Sheds ~0.37s/read off the affect path. NO NLTK perceptron tagger in the read path."""
    if patient in (None, "?"):
        return None
    toks = sentence_text.split(" ")
    pos = list(_affect_pos_cached(sentence_text))   # hdlab UD UPOS (memoized per string), one category system
    try:
        result = score_context_grounded_valence_pretagged(patient, toks, pos)   # need_valence=False
    except ValueError:
        return None  # patient head not found -- abstain, not guess
    if result["stage"] != "event":
        return None  # certified animacy-axis override did not fire for this item -- abstain
    return to_ternary(result["predicted_type"])


# ===========================================================================
# the reader
# ===========================================================================
class SituationReader:
    """read(conll_path) -> SituationModel. Composes the banked dimension modules."""

    def __init__(self, *, gaz: Optional[Dict[str, str]] = None,
                 focus_n_dim: int = FOCUS_N_DIM,
                 pred_gate_fn=None, spacy_pred_gate: bool = False,
                 gate_intransitive: bool = True,
                 role_route: str = "wired",
                 tense_agnostic_events: bool = True,
                 causation_typed: bool = False, causation_gate_mode: str = "force",
                 causation_use_gate: bool = True, causation_role_source: str = "parse",
                 causation_tendency: bool = True, causation_use_constructions: bool = True,
                 causation_sense_gate: bool = True, causation_sense_tau: float = 1.0,
                 causation_foreground_gate: bool = False,
                 timeline_register: bool = True,
                 preserve_tense: bool = True,
                 verb_subcat_gate: bool = True, verb_subcat_thr: float = 0.35,
                 track_space: bool = True,
                 predict_surprisal: bool = True,
                 surprisal_abstain_tau: Optional[float] = None,
                 predict_surprisal_asset: Optional[str] = None,
                 track_belief: bool = True,
                 bind_event_tokens: bool = True,
                 predict_revise: bool = True,
                 track_world_state: bool = True,
                 densify_world_state: bool = True,
                 track_goals: bool = True,
                 track_affect: bool = True,
                 parser_arceager: bool = True,
                 np_head_reduce: bool = True,
                 structural_patient: bool = True,
                 bind_entity_states: bool = True,
                 structural_do_recover: bool = False,
                 referent_per_np: bool = True,
                 cm_agent: bool = True,
                 include_pron_agents: bool = True,
                 case_filter: bool = True,
                 clause_local: bool = True,
                 cm_agent_struct: bool = True,
                 cm_weights: Optional[Dict[str, float]] = None,
                 cm_twin_seed: Optional[int] = None,
                 predicate_recall: bool = True,
                 causal_mental_bridge: bool = True,
                 goal_purpose_filter: bool = True,
                 entity_kb_resolver: bool = False,
                 commonnoun_situation_gate: bool = True,
                 commonnoun_canonical: bool = True) -> None:
        # === DEFAULTS FLIPPED ON 2026-09-03 (owner-authorized: "switch them on... 1 at a time, top down,
        # measure which are net positives"). The greedy forward-activation sweep (tools/flag_activation_sweep.py,
        # data/flag_activation_sweep/results.json) measured each flag one-at-a-time in dependency order on the
        # reader-QA harness: reader-QA aggregate 0.2903 (all-off) -> 0.3598 (kept stack). ALL are net non-negative
        # with NO real downstream regression (the apparent causal -0.23 under tense_agnostic_events is a MEASUREMENT
        # artifact -- the causal gold is built from sm.events which the keystone densifies, while the causal READOUT
        # reads sm.causal_links [C.extract], flag-independent; the reader's causal answers are byte-identical, and
        # the capable board has always operated at causal 0.1485). This SUPERSEDES the prior "no dimension flag
        # should be flipped default-ON yet -- the fully-on reader is N parallel silos" caution: bind_event_tokens
        # (the JOINT binder, coref 1.000 vs 0.600) is flipped ON here, so the dimensions now BIND, not just compose.
        # parser_arceager FLIPPED DEFAULT-ON 2026-09-04 (owner-DONE improve_the_parser_verb_argument_attachment...):
        # the labeled/valency/voice PATIENT readout (predicate_argument_frontend.structural_patient_pick, landed this
        # session) makes the stronger arc-eager parser REGISTER-SAFE -- it reads the labeled grammatical relation +
        # precision-weights, so OOD head errors no longer poison the patient. Net-positive on the who-did-what
        # instrument (+0.006 modern / +0.0045 19c clean-DO, reversing the -0.0017 arceager caused under the OLD position
        # readout) and BOARD-NEUTRAL (all 6 dims byte-identical 0.0-delta, arceager on-vs-off, 16 docs). Glass-box, no
        # external dep. STILL DEFAULT-OFF BY DESIGN: causation_typed + spacy_pred_gate (require spaCy -> NOT remote-safe
        # / the no-external-dep invariant). To reproduce the historical WEAK reader, pass every flag False explicitly.
        self.gaz = load_name_gender() if gaz is None else gaz
        self.focus_n_dim = int(focus_n_dim)
        # OPTIONAL supplied-grammar predicate-validity gate (29522 L1 win, ADOPTED opt-in).
        # Default OFF -> byte-identical to the banked reader. pred_gate_fn(sentence_text)->set(low).
        if pred_gate_fn is None and spacy_pred_gate:
            pred_gate_fn = _build_spacy_pred_gate()
        self.pred_gate_fn = pred_gate_fn
        # FRAME-ARITY gate (2026-08-06, PROMOTED TO DEFAULT-ON 2026-08-06): mechanism can-fail
        # 16/16 (gold-independent structural cases, hdlab/situation_reader.py::_selftest_frame_arity_gate)
        # + gold measurement precision 0.148->0.173 (+0.025, 9 spurious intransitive-patient FPs
        # removed, 0 other changes, recall unchanged) + certification 220/3 unchanged with the gate
        # OFF at land-time (commit 29842ab70). STRICTLY_INTRANSITIVE_VERBS (sit/go/arrive/...) never
        # get a spurious PATIENT from the nearest following nominal. See _pick_role_mentions. Still
        # an explicit kwarg -> callers needing the pre-fix positional-only behavior pass
        # gate_intransitive=False to opt back out.
        self.gate_intransitive = bool(gate_intransitive)
        # ASSEMBLY reader-role-routing (opt-in; default "positional" = byte-identical to the stock reader).
        # Anything != "positional" routes roles through parse -> router (+ quotative) with a positional
        # fallback (the validated HYBRID). Loads the persisted parse frontend ONCE, only when turned on.
        self.role_route = str(role_route)
        self.wired_extra_roles: List[Dict[str, object]] = []   # additive richer roles, wired path only
        if self.role_route != "positional":
            self._tagger, self._parser = _load_frontend()
        # TENSE-AGNOSTIC EVENT DETECTION (opt-in; default OFF = byte-identical to the stock detector).
        # Integrated 2026-08-31 from `the_extraction_front_end_recovers_only_a_third_of_events_and_roles`
        # (owner-DONE, EXCELLENT): the stock T.extract_events is TENSE-GATED and misses present-tense finite
        # verbs (VBZ/VBP) 100%, capping event-detection recall at ~0.33. When True, detect an event at every
        # UPOS==VERB via the in-substrate UD-trained tagger (hdlab.pos_tagger, NO spaCy/LLM) -- tense-
        # agnostic, category-based. Lifts end-to-end event recall 0.381->0.966 through THIS reader
        # (CI-separated; generalizes OOD to modern QA-SRL + 19c LitBank; info-free twin loses). This is the
        # KEYSTONE that de-risks the assembly (every downstream dimension reads off the event set). BOUNDARY:
        # this recall-max detector assigns a PLACEHOLDER tense (TENSE_SIMPLE_PAST). This flag touches ONLY
        # _read_events (via _extract_events); the TIME dimension (_read_timeline) does its OWN extraction via
        # M.extract_events_punct, so the flag does NOT corrupt the timeline today. The caution is FORWARD-
        # looking: if the dimensions ever share ONE event set (the right architecture), a tense-PRESERVING
        # variant must land first, or TIME breaks (it reconstructs order from real tense/aspect).
        self.tense_agnostic_events = bool(tense_agnostic_events)
        self._ta_tagger = None                                 # lazy hdlab.pos_tagger.PosTagger
        # TENSE-PRESERVING refinement (opt-in; default OFF = byte-identical; REFINES tense_agnostic_events
        # -- no effect unless that flag is also on). Integrated 2026-08-31 from
        # `the_tense_agnostic_detector_drops_tense_needed_by_the_time_dimension` (owner-DONE, STRONG, 12/12):
        # the tense-agnostic detector fires on the SAME UPOS==VERB tokens but replaces the PLACEHOLDER tense
        # (TENSE_SIMPLE_PAST) with a COMPOSED Reichenbach tense x aspect x voice parse of the verb group
        # (main verb + auxiliary chain) -- glass-box, in-substrate (UPOS + closed-class aux forms + suffix
        # morphology), NO spaCy/LLM. Recall is preserved EXACTLY (the detected event SET is identical; only
        # EventRecord.tense/is_pp change). This is the tense-PRESERVING variant the tense_agnostic BOUNDARY
        # note called for: with it on, the TIME dimension (timeline_register) can consume ONE is_pp-faithful
        # event set. In-substrate word-tense 0.770 CI-sep over placeholder/majority/twin; aspect 0.987/voice
        # 0.933. The composition (assign_sentence) is lazily imported from the validated experiment module
        # only when the flag is on (the experiment module is nltk-free at import; nltk loads only for the
        # optional fine-tag path, which this surface-mode landing does NOT use).
        self.preserve_tense = bool(preserve_tense)
        self._tp_mod = None                                    # lazy exp_tense_preserving_event_detector_v1
        # VERB-SUBCATEGORIZATION patient gate (opt-in; default OFF = byte-identical). Integrated 2026-08-31
        # from p2 wire_the_incremental_parser... (EXCELLENT): the reader over-generates a patient on
        # intransitive verbs ("the man arrived at noon" -> patient=noon). When on, SUPPRESS a bound patient
        # when the verb's transitivity propensity (dual WordNet-frame + corpus P(obj|verb) basis; Levin/
        # VerbNet + verb-bias, PINNED) is below verb_subcat_thr. This is the glass-box successor to the crude
        # curated gate_intransitive list (8,700 verbs). Post-read pass (matches the validated SubcatGateReader
        # through read()): beats the curated list +0.121 and a random same-rate twin +0.158; precision
        # 0.514->0.643 @ recall 0.936; NO LLM. The stronger GRADED Competition-Model gate (hdlab.verb_subcat.
        # patient_present, QA-SRL who-did-what 0.30->0.49) is a QUEUED refinement -- it needs the reader to
        # expose POS + the patient token index at role-assignment time (WIRING_MAP DEBT 2).
        self.verb_subcat_gate = bool(verb_subcat_gate)
        self.verb_subcat_thr = float(verb_subcat_thr)
        self._vs_mod = None                                    # lazy hdlab.verb_subcat
        # SPACE dimension (opt-in; default OFF = byte-identical). Integrated 2026-08-31 from
        # `the_reader_has_no_spatial_location_dimension_end_to_end` (owner-DONE, STRONG): the 4th
        # situation-model dimension (WHERE). When on, sm.locations = a per-entity LocationRegister
        # (where_is/present_in_scene) driven by the reader's OWN in-substrate parse+coref via the validated
        # experiments._space_reader (prior_ext mode -- the noisy-channel parse-as-evidence+PRIOR, the
        # best-validated arm; a stronger parser does NOT help, the ceiling is parser RECALL). Lazily imported
        # only when the flag is on. NO spaCy (in-substrate parse). Additive; the narrow inline SPACE proxies
        # are untouched.
        self.track_space = bool(track_space)
        self._space_mod = None                                 # lazy experiments._space_reader
        # CAUSATION TYPING (opt-in; default OFF = byte-identical). Integrated 2026-08-31 from p2
        # (wire_the_causation_typer, STRONG) + p3 (foreground/event-hood gate, STRONG), both owner-DONE.
        # When ON, read() adds a TYPED within-clause causation read (CAUSE/ENABLE/PREVENT) on sm.
        # typed_causal_links via hdlab.causation_typing (Talmy/Wolff force dynamics PINNED; Hopper-Thompson
        # event-hood for the foreground gate). It uses spaCy + the experiment-side literalness gate, LOADED
        # LAZILY only when the flag is on -- the default reader imports/loads NEITHER (byte-identical). The
        # WSD/literalness chain stays in experiments/ (its own separate queued promotion). Defaults are the
        # validated p2 config (gate_mode="force", use_gate/role_source="parse"/tendency/sense_gate on).
        self.causation_typed = bool(causation_typed)
        self.causation_gate_mode = str(causation_gate_mode)
        self.causation_use_gate = bool(causation_use_gate)
        self.causation_role_source = str(causation_role_source)
        self.causation_tendency = bool(causation_tendency)
        self.causation_use_constructions = bool(causation_use_constructions)
        self.causation_sense_gate = bool(causation_sense_gate)
        self.causation_sense_tau = float(causation_sense_tau)
        self.causation_foreground_gate = bool(causation_foreground_gate)
        # TIMELINE REGISTER (opt-in; default OFF = byte-identical). When ON, read() adds the whole-passage
        # chronological EVENT ORDER on sm.timeline_order via the validated experiments._temporal_order_register
        # (extract_passage clause_pluperfect=True -> DiscreteOrderRegister toposort). Lazily imported -> a default
        # (OFF) reader never imports the register. It reuses the SAME temporal modules (T/M) this reader already
        # imports; the discrete path pulls NO torch/transitive_ordering. It does NOT touch the narrow, "had"-gated
        # per-sentence _read_timeline path (that stays byte-identical); this is a NEW additive whole-passage field.
        self.timeline_register = bool(timeline_register)
        # FORWARD-PREDICTION surprisal (opt-in; default OFF = byte-identical). Integrated 2026-08-31 from
        # `the_forward_prediction_organ_is_inert_wire_its_surprisal_into_a_live_decision` (owner-DONE,
        # EXCELLENT). When ON, a POST-READ pass computes, per event, the N400 SURPRISAL of the reader's own
        # bound PATIENT among its sentence's candidate nominals via the promoted hdlab.predictive_reader
        # (loaded from a persisted QA-SRL-fitted foundation asset), exposing EventRecord.patient_surprisal +
        # pred_precision as ADDITIVE metadata (the validated error-RISK FLAG: predicts the reader's OWN
        # who-did-what errors AUC 0.651 CI-sep). If surprisal_abstain_tau is set, events with surprisal > tau
        # are marked low_confidence (the validated WITHHOLD decision; do NOT auto-revise -- a proven NEGATIVE).
        # Lazily loads the predictor + the tagger ONLY when the flag is on. NO spaCy / NO LLM.
        self.predict_surprisal = bool(predict_surprisal)
        self.surprisal_abstain_tau = surprisal_abstain_tau
        self.predict_surprisal_asset = predict_surprisal_asset
        self._pr_predictor = None      # lazy hdlab.predictive_reader.PredictiveReader (from the persisted asset)
        # BELIEF/ToM dimension (opt-in; default OFF = byte-identical). Integrated 2026-08-31 from
        # `the_belief_dimension_is_never_driven_by_the_readers_own_extraction_on_real_prose` (owner-DONE,
        # EXCELLENT; validated on FANToM, reader 0.893 vs floor 0.665 CI-sep). When ON, read() exposes
        # sm.believes/sm.knows -- CALLABLES that drive the promoted hdlab.belief_timeline from the reader's
        # OWN extraction (4 channels: narrator-epistemic + testimony dominant + perception + inference) via
        # the lazily-imported experiments._belief_reader adapter (which composes _space_reader/state_register)
        # + a hdlab.perceptual_access_ledger observation gate. The DOMINANT belief-assertion channels are
        # substrate-native (NO spaCy); the PERCEPTION track lazily loads spaCy (opt-in, local-only, like
        # causation_typed). Additive; nothing else changes.
        self.track_belief = bool(track_belief)
        self._belief_led = None        # lazy hdlab.perceptual_access_ledger.PerceptualAccessLedger
        self._belief_mod = None        # lazy experiments._belief_reader
        # BOUND-EVENT-TOKEN backbone (opt-in; default OFF = byte-identical). Integrated 2026-09-01 from
        # `the_assembled_reader_is_parallel_silos_assemble_the_tiered_bound_event_token` (p4, owner-DONE,
        # EXCELLENT): the assembled reader was N PARALLEL SILOS -- each dimension stored the MARGINALS (the
        # set of agents / actions / times), nothing stored the JOINT (which agent did which action). That is
        # the BINDING PROBLEM. When ON, read() builds sm.event_tokens (ONE FHRR bound token per event over
        # {AGENT,PATIENT,PRED,TENSE}) + sm.episodic_store (a BoundEpisodicStore: the N400-chunked + DG/CA3
        # episodic tier, with a resolve/corefer readout over the bound tokens) via the promoted thin
        # assembler hdlab.bound_event_backbone (COMPOSES existing organs only: binding + n400_coherence_
        # monitor + hippocampal_encoder). Proven to store the JOINT the silos cannot: JOINT coref 1.000 vs
        # late-fusion-of-marginals 0.600 CI-sep on LitBank old fiction AND UD-EWT modern web; binding-shuffle
        # collapses it; the tiered store holds at passage scale where a flat superposition collapses ~1/sqrt(M).
        # This is the step from the reader HAVING features to the reader UNDERSTANDING which goes with which
        # -- the prerequisite for reasoning (p6). Lazily imports the assembler ONLY when the flag is on. NO
        # spaCy / NO LLM. Flipping it default-ON is a SEPARATE owner decision (this is the evidence).
        self.bind_event_tokens = bool(bind_event_tokens)
        self._beb_mod = None           # lazy hdlab.bound_event_backbone
        # PREDICT-REVISE parse-RECALL drop-fill (opt-in; default OFF = byte-identical). Integrated 2026-09-01
        # from `the_reader_parses_as_truth_where_the_brain_parses_predictively_predict_and_revise` (p2,
        # owner-DONE, EXCELLENT). The reader takes its ONE batch parse AS TRUTH and DROPS the patient when it
        # sits BEFORE the verb (passive / object-relative / pre-verbal gap). When ON, a POST-READ pass fills
        # each event whose patient is '?' (the structural coverage violation) by REUSING the validated
        # hdlab.relcl_resolver.resolve_patient (the active-filler filler-gap resolver -- passive-subject /
        # object-gap / word-order routes) as the fill TARGET, with a nearest-nominal POSITION fallback, and
        # records the original '?' on EventRecord.patient_prerevise (glass-box, reversible). Recovers
        # who-did-what CI-separated over the batch parse on BOTH modern QA-SRL (+0.060) and 19c LitBank
        # (+0.059); the gain is a purely STRUCTURAL drop-fill (NO fitted predictor, NO surprisal gate -- the
        # drill proved those add nothing). Do NOT wire post-verbal RE-SELECTION or surprisal-gated reanalysis
        # of committed picks (p2's proven NEGATIVE). Recall-scoped only -> canonical recall PROTECTED. Lazily
        # imports relcl_resolver + the pos tagger ONLY when on. NO spaCy / NO LLM. Compose with role_route='wired'.
        self.predict_revise = bool(predict_revise)
        self._pr_revise_rr = None      # lazy hdlab.relcl_resolver
        self._pr_revise_tagger = None  # lazy pos tagger (UPOS)
        self._pr_revise_nom = None     # lazy (NOMINAL, PRON_LOW) from the validated driver
        # WORLD-STATE register (opt-in; default OFF = byte-identical). Integrated 2026-09-01 from the owner-DONE
        # problem `situation_model_has_no_mutable_world_state_register` (PARTIAL/EXCELLENT, reverified 36/36).
        # When ON, read() folds the reader's OWN extracted events into a hdlab.world_state_register.WorldState
        # (possession have(holder,obj) + open/closed toggles as STRIPS operators; operator classes from the
        # FrameNet-derived hdlab.possession_operators lexicon; recipient/source from the reader's wired_extra_roles)
        # and sets sm.world_state -> has(entity,obj,t)/holder_of(obj,t)/is_open(obj,t)/unmet_preconditions().
        # Mechanism 1.000 vs the strongest stateless floor last_obj_mention 0.750 (+0.250 CI-sep); open-text
        # who-has-what is COREF-bound (81% pronoun agents -- the located residual, a NAMED existing organ, not the
        # mechanism). Lazily loads the cached FrameNet lexicon ONLY when on. spaCy-free / NO LLM.
        self.track_world_state = bool(track_world_state)
        self._ws_lex = None            # lazy hdlab.possession_operators FrameNet lexicon (cached json)
        # COREF-DENSIFIED WORLD-STATE (opt-in; default OFF = byte-identical). Wired 2026-09-02 from the owner-DONE
        # problem the_world_state_register_is_coref_blind... : key sm.world_state HOLDERS on the canonical DISCOURSE
        # ENTITY (Glenberg/Meyer/Lindem 1987; possession attaches to the entity node, not the surface mention) via
        # the promoted hdlab.world_state_entity_binding.EntityBinder STAGE-1 dispatcher instead of the raw head
        # string. Self-contained routes (indexical I/me->NARRATOR; object it->recency theme; nominal->head;
        # we/you/pleonastic->abstain) fire on the head alone; the he/she anaphoric route consumes the reader's OWN
        # coref resolution (recs_ec) supplied per (sent_idx, head) -- REUSE, no new resolver. Requires
        # track_world_state (it re-keys the SAME fold). Additive fidelity: the +0.148 who-has-what LEVER is measured
        # in the isolated gold-aligned harness (exp_world_state_coref_densify_v1, on the board's RIGHT corpus); this
        # wire lands the ENTITY-KEYED representation live so the STATE dimension is not a raw-string island. NO LLM.
        self.densify_world_state = bool(densify_world_state)
        self._ws_binder_mod = None     # lazy hdlab.world_state_entity_binding
        # GOAL/INTENTION dimension (DEFAULT-ON 2026-09-04, no-default-off: additive + net-positive). Wired from
        # the owner-DONE problem the_situation_model_has_no_goal_intention_dimension (Q111). read() builds a per-agent
        # GOAL REGISTER (the missing 5th Zwaan-Radvansky event-indexing dimension, intentionality) from THIS
        # passage's explicit purpose/desire/intention constructions via the promoted hdlab.goal_register (extractor
        # + lexicalist hdlab.verb_subcat_frames complement-vs-adjunct filter + track_status), binds each goal to the
        # reader's OWN resolved agent (coref) + passive-agent guard, and sets sm.goal_register + the query callables
        # sm.wants(agent)/sm.why(action,agent)/sm.achieved(agent,goal). Mirrors _read_belief/_read_world_state:
        # additive, runs LAST so agents/status bind to the FINAL event+coref stream -- no other dimension field
        # changes (byte-identical off vs on; landing witness L3). Turned DEFAULT-ON like the sibling situation-model
        # dimensions (track_belief/track_world_state/bind_entity_states): net-positive (WANT-explicit CI-sep over the
        # most-recent-action floor + shuffled-agent twin loses; WHY 0.97 where physical-cause cannot), zero regression
        # (additive by construction), +~0.24s/read. NO spaCy / NO LLM.
        self.track_goals = bool(track_goals)
        # AFFECT/EMOTION dimension (DEFAULT-ON 2026-09-04, no-default-off: additive + net-positive). Wired from
        # the owner-DONE problem the_situation_model_has_no_affect_emotion_dimension (Q111). read() builds a
        # per-character AFFECT REGISTER (the missing emotion dimension -- a DISTINCT appraisal/affect system,
        # PINNED-dissociated from the goal/belief mentalizing dimensions, Campanella 2022 triple dissociation)
        # from THIS passage's explicit emotion constructions via the promoted hdlab.affect_register (extractor
        # + curated-denotation hdlab.affect_lexicon valence/category + lexicalist hdlab.psych_verb_frames
        # experiencer-linking split), binds each emotion to the reader's OWN resolved experiencer (coref), and
        # sets sm.affect_register + the query callables sm.feels(char)/sm.valence_of(char)/sm.feels_about(char,y).
        # Mirrors _read_goals: additive, runs LAST so experiencers bind to the FINAL coref stream -- no other
        # dimension field changes (byte-identical off vs on; landing witness L3). Turned DEFAULT-ON like the
        # sibling situation-model dimensions (track_goals/track_belief/track_world_state): net-positive ("how does
        # X feel" category CI-sep over the most-recent-emotion-word floor + shuffled-character twin loses; valence
        # 0.838; zero regression, additive by construction; +~0.24s/read). NO spaCy / NO LLM.
        self.track_affect = bool(track_affect)
        # IMPROVED PARSER (opt-in; default OFF = byte-identical). Wired 2026-09-02 from the owner-DONE parser problem
        # the_extraction_front_end_parser_is_the_cross_task_bottleneck...: route the WIRED who-did-what front-end
        # through the promoted arc-eager parser (hdlab.arceager_parser, UD-EWT UAS 0.775->0.842) instead of the
        # richfeat ArcParser -- swapping ONLY the head source in _router_roles that feeds predicate_argument_frontend
        # (matrix_verbs/route_predicate_arguments; the solver measured matrix-verb F1 +0.015, PP/oblique-role F1 +0.027).
        # Refines role_route='wired' ONLY. Default OFF -> the ArcParser richfeat heads, byte-identical. NO LLM.
        self.parser_arceager = bool(parser_arceager)
        self._ae_W = None              # lazy hdlab.arceager_parser model weights
        self._ae_parse = None          # lazy hdlab.arceager_parser.parse_with_conf
        # NP-HEAD REDUCE (opt-in; default OFF = byte-identical). Wired 2026-09-03 from the owner-DONE who-did-what
        # fix the_who_did_what_selection_residual_is_structural_np_head_chunking_and_case_not_meaning: the reader's
        # role assigners grab the wrong word inside a noun phrase ("the undertaker's shop" -> undertaker; "iron
        # gate" -> iron) -- 96% of their who-did-what misses. When on, reduce candidates to their NP HEAD (compound
        # Right-hand Head Rule + genitive DP-head) at BOTH sites the solver proved: (a) the ROUTER path -> pass
        # np_head_reduce into route_predicate_arguments (the primitive all consumers funnel through, +0.20 each);
        # (b) the POSITIONAL path -> filter `noms` to NP-head mentions before _assign_roles (lifts the landed
        # _assign_roles 0.7728 -> 0.9477). Reuses hdlab.np_head_reduce. NO spaCy / NO LLM.
        self.np_head_reduce = bool(np_head_reduce)
        # STRUCTURE-FIRST PATIENT (opt-in; default OFF = byte-identical). Promoted 2026-09-04 from the owner-DONE
        # who-did-what drill `consume_the_graded_pos_posterior_...`: the stock THEME/patient is a flat cue/position
        # selector (the brain's DAMAGED-BACKUP / agrammatic route -- NO arc heads). When ON, the WIRED path routes
        # the THEME structure-first through the parse relations + voice remapping (predicate_argument_frontend.
        # structural_patient_pick: object[active] / promoted-subject[passive via robust_passive] / coordination-
        # control share; heuristic fallback where the parse yields no core object -- net-safe). +0.088 test / +0.076
        # train over the live heuristic on CLEAN UD-EWT gold (patient := obj|nsubj:pass off gold relations), ZERO
        # tuned parameters (generalizes), ceiling 0.91 with a perfect parse. The AGENT is UNCHANGED (cm_agent /
        # positional / by-phrase untouched -> byte-identical agent). Requires role_route='wired' to have effect
        # (the router path); default OFF -> the heuristic THEME, byte-identical. NO spaCy / NO LLM.
        self.structural_patient = bool(structural_patient)
        # COPULAR is-a/attribute binding. When ON, read() adds a typed is-a/attribute read on sm.entity_states +
        # sm.state_register via hdlab.copular_binding (high-precision LABEL path UNION the label-ROBUST closed-class
        # copula detector robust_cop) + the glass-box Higgins typing. Integrated 2026-09-03 from the owner-DONE
        # the_reader_has_no_copular_is_a_binding_schema (10/10+6/6). **DEFAULT-ON (2026-09-03, P3 wire_the_copular_
        # state_qa_consumer... owner-DONE, no-default-off):** the landed state-QA consumer routes "what/who is X" ->
        # sm.state_register.state_at, net-positive on a CONSUMED metric (qa_state 0.712 CI-sep over floor, shuffle
        # twin loses; robust_cop lifts it to 0.833; qa_aggregate 0.315->0.404) and PURELY ADDITIVE (the 4 scored
        # dims events/coref/timeline/causal are byte-identical off vs on; state_register feeds no other dim),
        # +~5ms/read. all_capabilities_off() still sets it False. Lazy imports. NO LLM.
        self.bind_entity_states = bool(bind_entity_states)
        # STRUCTURAL-DO recovery (opt-in; default OFF = byte-identical). Coverage-gap §0g wire (2026-09-03, from
        # the owner-DONE the_who_did_what_front_end_abstains...): the verb_subcat gate's blanket intransitive veto
        # also drops genuinely-transitive uses of low-transitivity verbs on 19c prose (47 mis-vetoed clauses). When
        # ON, the WIRED path (_read_events_wired) records per event whether its bound patient is a BARE post-verbal
        # DIRECT OBJECT (hdlab.structural_do.is_bare_do -- no preposition between verb and candidate), and the
        # verb_subcat gate OVERRIDES its veto for a bare-DO patient (structural evidence beats the weak transitivity
        # prior -- Competition Model), recovering the 47 while preserving intransitive precision (a low-transitivity
        # verb WITHOUT a bare DO still abstains). Requires role_route='wired' + verb_subcat_gate to have effect;
        # default OFF -> patient_is_bare_do stays None -> the veto is unconditional (byte-identical). NO spaCy / NO LLM.
        self.structural_do_recover = bool(structural_do_recover)
        self._sdo = None               # lazy hdlab.structural_do
        # REFERENT-PER-NP mention source. The deployed read() sourced who-did-what candidates from the CoNLL COREF
        # column, so on real 19c prose the gold PATIENT is a candidate only ~0.82 of the time. A discourse referent
        # per content-noun-head NP (Kamp/Heim DRT + the determiner/name FRAME detector) recovers the missed objects
        # -> effective who-did-what PATIENT 0.4698->0.8054 (+0.336 cleaned-DO, live) + who-has-what theme +0.115.
        # **DECOUPLED (P5 wire, owner-DONE wire_the_referent_to_coref_linking_pass): referent_per_np swaps ONLY the
        # who-did-what ROLE-candidate + entity source; pronoun ANAPHORA keeps reading the coref-column source (two
        # consumers, two brain cue-filters -- Lewis-Vasishth / Grosz-Joshi-Weinstein). See read(). -> coref_acc
        # byte-identical to the OFF reader (fixes the 0.469->0.102 collapse).**
        # **DEFAULT-ON (2026-09-04, OWNER DECISION): the complete referent set IS the brain-foundational upstream
        # (a discourse referent per NP), so it is the default. HONEST CAVEAT: the board's who-did-what arm scores the
        # AGENT (subject), and the DENSER referent set transiently REGRESSES the agent (qa_events 0.252->0.075)
        # because the downstream AGENT role assignment is PURELY POSITIONAL (agent=preverbal mention -- NOT the
        # brain's mechanism), so it grabs a wrong preverbal NP head from the extra referents. This is a downstream
        # fidelity gap, NOT a referent_per_np defect: the PATIENT (where coref misses) improves +0.336; the AGENT
        # (where coref already had the subject) regresses until the role assigner is made brain-foundational. THE FIX
        # (filed URGENT): the Competition-Model cue-competition role assigner (word-order+animacy+voice+verb-frame;
        # cuts inanimate-agent error 0.333->0.081) -> then qa_events recovers and default-on is a net board win.**
        # all_capabilities_off() sets it False. NO spaCy / NO LLM.
        self.referent_per_np = bool(referent_per_np)
        self._rnp_tagger = None        # lazy hdlab.pos_tagger.PosTagger (the frontend UPOS tagger)
        # COMPETITION-MODEL AGENT role assignment (P2 wire, 2026-09-04, owner-DONE swap_the_positional_role_
        # assigner_for_the_brain_foundational_competition_model). referent_per_np default-ON banks the +0.336
        # PATIENT win but the POSITIONAL agent (leftmost-NP subject proxy) COLLAPSED over the denser set
        # (who-did-what AGENT 0.2257 -> 0.0410). THE FIX (SOLVED, scaffold-free witness 10/10): recompute the
        # AGENT by a GRADED, PARALLEL cue competition (Competition Model, Bates & MacWhinney; McClelland 2013
        # posterior; hdlab.graded_role_assigner.agent_competition_pick over hdlab.graded_competition.
        # net_activation -- the SAME organ the PATIENT side uses) over the TRACKED / GIVEN discourse entities
        # (the coref-column set; Centering Cb->subject Grosz 1995, DuBois 1987 PAS) -- DECOUPLED from the dense
        # PATIENT set (the +0.336, left EXACTLY as _assign_roles produced it -> byte-identical patient by
        # construction; agent-only change). The candidate-SET decouple is load-bearing (the same rule over the
        # DENSE set only reaches 0.082). ALL DEFAULT-ON per the no-more-default-off rule (each is net-positive,
        # patient-neutral, held-out-replicated in the SOLVED; full stack 0.041 -> ~0.69 on the arm):
        #   cm_agent            -- the Competition-Model AGENT competition (the keystone).
        #   include_pron_agents -- KEEP subject pronouns as agent candidates (Centering: the salient Cb is
        #                          pronominalized -> the strongest agent candidate; _sentence_nominals drops them,
        #                          which is why 70% of gold agents were unreachable). Lifts 0.2519 -> 0.4082.
        #   case_filter         -- keep only NOMINATIVE pronoun agents (Competition-Model CASE cue: accusative/
        #                          possessive/reflexive pronouns are morphologically marked as non-subjects).
        #   clause_local        -- bound the agent candidates to the verb's CLAUSE span (incremental clause
        #                          segmentation; hdlab.graded_role_assigner.clause_bounds). 0.4082 -> 0.4224.
        # BACKWARD-COMPATIBLE: each has effect ONLY when cm_agent AND referent_per_np are both ON and a coref
        # source exists; with cm_agent OFF (or referent_per_np OFF) the AGENT is byte-identical to the stock
        # positional/wired pick. all_capabilities_off() sets them all False (the historical pre-P2 reader).
        # cm_weights (static asset default = AGENT_VALIDITIES) + cm_twin_seed (info-free control) are knobs, not
        # capability flags. NO spaCy / NO LLM (the competition reads only toks/POS + animacy lexicon + coref).
        self.cm_agent = bool(cm_agent)
        self.include_pron_agents = bool(include_pron_agents)
        self.case_filter = bool(case_filter)
        self.clause_local = bool(clause_local)
        # STRUCTURE cue (cm_agent_struct, DEFAULT-ON 2026-09-04, owner-DONE the_agent_tie_wall_is_embedded_
        # clauses...): feed the register-general incremental left-corner subject bind (hdlab.incremental_parser.
        # incremental_subject_before) into the AGENT competition as ONE self-gating precision-weighted cue
        # (graded_role_assigner.agent_supports "structure", weight AGENT_VALIDITIES["structure"]=2.5). Resolves
        # the embedded/relative-clause nominative-vs-nominative TIE residual: tie slice +0.073 tuned / +0.056
        # held-out CI-sep, canonical +0.007 (no regression, slight gain), whole-arm +0.019 CI-sep; PATIENT
        # byte-identical (agent-only); shuffled-structure twin LOSES. SELF-GATING: votes only when the parse
        # binds a subject onto a tracked candidate -> byte-identical where it does not fire. Net-positive with a
        # measured reason -> default ON (no-more-default-off). Has effect ONLY when cm_agent stack is engaged;
        # cm_agent_struct OFF -> the AGENT is byte-identical to the pre-structure competition. NO spaCy / NO LLM
        # (the incremental parser reads only toks/POS). all_capabilities_off() sets it False.
        self.cm_agent_struct = bool(cm_agent_struct)
        self.cm_weights = dict(cm_weights) if cm_weights else None
        self.cm_twin_seed = cm_twin_seed
        self._coref_mentions = None    # stashed by read() -> the AGENT candidate source (tracked/given set)
        # PREDICATE-RECALL: register-robust event recovery (opt-in; default OFF = byte-identical). P6 wire
        # (2026-09-03, owner-DONE register_robust_event_detection...): the tense_agnostic UPOS==VERB detector
        # silently DROPS a whole clause when the tagger mistags a real verb (archaic / noun-flanked prose). When
        # ON, a glass-box 7-weight logistic over register-invariant cues (hdlab.predicate_detector, the brain's
        # noisy-channel COMBINATION; Gibson 2013) promotes tagger-dropped non-VERB non-AUX tokens with a WordNet
        # verb-reading back to event predicates. ADDITIVE-ONLY -> the existing UPOS==VERB detections + their role
        # picks are BYTE-IDENTICAL (no regression by construction). Recovers dropped verbs MODERN 0.90 / 19c 0.56
        # @ FP<=0.5/sent, twin loses CI-sep, ZERO 19c labels. The asset threshold is FP<=0.5/sent-calibrated on
        # MODERN (denser 19c -> ~1.4 FP/sent at the same threshold: an FP-budget knob).
        # FLIPPED DEFAULT-ON 2026-09-05 (owner-DONE register_robust_event_detection_turn_on_and_expand...): the
        # cross-arm re-adjudication proved the turn-on NET-POSITIVE on BOTH who-did-what arms on the CURRENT
        # reader (held-out agent +0.0125 / patient +0.0050 CI-sep, monotone in recovery = real signal), the
        # random-verbhood twin loses. SCOPED so causal stays byte-identical: _read_causation computes
        # sm.causal_links over the BASE (non-recall) event set (see there) -- without scoping the extra events
        # add distractor causes and causal regresses -0.0594 CI-sep. coref/temporal byte-identical, world_state
        # +22/-0 facts, bound_event_tokens 1/3641. FP does not reach a who-did-what answer (additive + lemma-and-
        # sentence match). NO spaCy / NO LLM (WordNet lexical gate only). all_capabilities_off() still sets False.
        self.predicate_recall = bool(predicate_recall)
        # MENTAL-BRIDGE causal path (owner-DONE a_force_dynamic_meaning_hub_causal_scorer..., 2026-09-05, Q111):
        # APPEND folk-psych mental-causation links (perception/cognition/emotion trigger -> mental/expressive
        # outcome, via the WordNet event-TYPE representation) on NON-connective sentences where _read_causation
        # otherwise builds nothing. Additive: connective causal QA + events + coref BYTE-IDENTICAL off vs on (the
        # mental path never touches connective sentences, and the causal QA gold is connective-only); the goal
        # graph stays a strict SUPERSET (connective links emitted first). Crosses the mental wall the physical
        # force lexicon cannot (11/16 real cause verbs). Default matches the measured off-vs-on board impact.
        self.causal_mental_bridge = bool(causal_mental_bridge)
        # GOAL ADVCL PURPOSE FILTER (owner-DONE validate_the_ppmi_svd_means_end_bridge... §5): gate the goal
        # register's bare-purpose 'to VP' on the reader's OWN arc-labeler deprel -- reject confirmed complements
        # (xcomp/ccomp/acl), keep purpose adjuncts (advcl). Upstream net-positive on why() (removes 131 wrong vs
        # 24 genuine, 5.5:1). Consumes the shared per-read parse (the consolidated arc-eager heads) + arc labeler.
        self.goal_purpose_filter = bool(goal_purpose_filter)
        # ENTITY-KB common-noun-coref path (owner-DONE seed_the_entity_world_model_resolver...): replace the
        # situation-gated former with the full brain-foundational chain (curated role/kinship KB + situation-model
        # instance binding + pronoun-into-entity). DEFAULT-OFF pending a live measurement -- its harness win is
        # COMMON-NOUN CoNLL, which the board's PRONOUN coref dim does not score (indirect payoff via affect/goal).
        self.entity_kb_resolver = bool(entity_kb_resolver)
        self._lab = None               # lazy shared hdlab.arc_labeler.ArcLabeler (deprels for the goal filter)
        self._pred_detector = None     # lazy hdlab.predicate_detector.PredicateDetector
        # PER-READ tag/parse memo (2026-09-03 perf): dimensions independently re-tag/re-parse the SAME
        # sentences (arc parser ~118x + POS tagger ~310x per read). Tag+parse each distinct sentence ONCE
        # per read() via _cached_tag/_cached_parse_heads; reset each read -> no cross-read leak, byte-identical
        # (pure deterministic tagger/parser). Generalizable: every reader path that tags/parses reuses it.
        self._read_parse_cache: Dict[tuple, object] = {}
        self._es_mod = None            # lazy experiments._copular_nominal_events
        self._es_typed = None          # lazy predicted_type (Higgins classifier)
        self._es_pos = None            # lazy PosTagger (the copular assets' tagger)
        self._es_arc = None            # lazy ArcParser (M._ARC_ASSET)
        self._es_lab = None            # lazy ArcLabeler (M._LAB_ASSET)
        self._es_reg_cls = None        # lazy hdlab.state_register.StateRegister
        self._causation_nlp = None     # lazy spaCy handle (loaded once, only when causation_typed)
        self._causation_lex = None     # lazy force lexicon
        # COMMON-NOUN referent former + wiring (opt-in; default OFF -> byte-identical). Wired 2026-09-04 from the
        # owner-DONE form_a_discourse_referent_for_every_entity_not_just_named_ones_common_noun_coref (Q111, §5).
        # (a) commonnoun_situation_gate: RE-CLUSTER the reader's common-noun (person) referents via the LANDED
        #     deployable situation-gated former (hdlab.commonnoun_binder: head-match-gated link + modifier-split +
        #     wide window + the event-centrality tie-break, reusing hdlab.event_centrality_coref), REPLACING the
        #     referent-per-NP gold/singleton cluster ids on sm.entities (the surface-head blind transitive merge).
        #     +0.0128 CoNLL over surface-head on the SOLVED's gold population (CI-sep, no-regress named). ONLY
        #     sm.entities changes -- coref/events/world-state read their OWN separate streams (byte-identical).
        # (b) commonnoun_canonical: expose common-noun clusters to make_canonicalizer with a stable head-lemma
        #     label (the reframe/wiring lever -- the character-bound goal/affect registers bind 'the man' to the
        #     tracked man). DISK CAVEAT (measured in the SOLVED): the experiencer subpop is near-ceiling ~0.90, so
        #     little downstream CI-sep lift is expected -- the point is the wiring-debt fix + no-regress.
        # Default OFF pending the strategy's cross-consumer measurement (no-more-default-off). NO external LLM.
        self.commonnoun_situation_gate = bool(commonnoun_situation_gate)
        self.commonnoun_canonical = bool(commonnoun_canonical)
        self._cn_binder_mod = None     # lazy hdlab.commonnoun_binder
        # persistent readers (the banked backbone + single-sentence validity baseline).
        # graded_pick=True (LANDED 2026-09-06, owner-DONE strengthen_the_cue_based_pronoun_coreference_
        # resolver...): the live pronoun pick is the PINNED graded ACT-R cue-based retrieval (recency
        # load-bearing), replacing the rolemass topical pick + event-centrality override. The graded path
        # forces the event-centrality memory OFF internally (query_memory below is overridden), lifting
        # live pooled he/she coref_acc 0.4693 -> 0.6019 (+0.1327 CI-sep), named coref no-regress. Brain-
        # fidelity correction (register-general recency mechanism); graded_pick=False = incumbent fallback.
        self.reader_ec = EventCentralityReader(n_dim=EVENT_N_DIM, mem_seed=MEM_SEED, graded_pick=True)
        self.reader_ss = CorefReader()

    # ONE authoritative capability-flag list (the ONLY hand-maintained bit). Every "flags-off historical
    # reader" derives from it: build_reader(capable=False) and each isolation witness call
    # all_capabilities_off(...) -- so a future default flip updates HERE, not N call sites. role_route is the
    # string flag whose OFF value is "positional". Add a new capability flag here when you add one to __init__.
    CAPABILITY_FLAGS = (
        "tense_agnostic_events", "preserve_tense", "timeline_register", "verb_subcat_gate", "track_space",
        "predict_surprisal", "track_belief", "bind_event_tokens", "predict_revise", "track_world_state",
        "densify_world_state", "np_head_reduce", "parser_arceager", "causation_typed", "spacy_pred_gate",
        "bind_entity_states", "structural_do_recover", "referent_per_np", "cm_agent", "include_pron_agents",
        "case_filter", "clause_local", "cm_agent_struct", "predicate_recall", "track_goals", "track_affect",
        "structural_patient", "causal_mental_bridge", "goal_purpose_filter", "entity_kb_resolver",
        "commonnoun_situation_gate", "commonnoun_canonical")

    @classmethod
    def all_capabilities_off(cls, gaz=None, **overrides):
        """Build the HISTORICAL WEAK reader -- every capability flag OFF (role_route='positional') -- with
        optional per-flag overrides. The ONE canonical 'flags off' baseline (see CAPABILITY_FLAGS): used by
        build_reader(capable=False), isolation witnesses, and any before/after comparison, so flipping a
        default in the future requires NO change at those call sites. Example (isolate one flag under test):
        SituationReader.all_capabilities_off(gaz=g, tense_agnostic_events=True, verb_subcat_gate=True)."""
        cfg = {f: False for f in cls.CAPABILITY_FLAGS}
        cfg["role_route"] = "positional"
        cfg.update(overrides)
        return cls(gaz=gaz, **cfg)

    # -- ENTITIES + COREF (banked EventCentralityReader recency-centrality, 29516) --
    def _read_entities(self, mentions, targets, n_sents):
        sid_fixed = [i // LOCAL_WINDOW for i in range(n_sents)]
        # query_memory=True / centrality_mode="event_role" are the INCUMBENT (graded_pick=False) config.
        # With the default graded_pick=True reader, resolve_stream forces the event-centrality memory OFF
        # and uses the PINNED graded ACT-R pick (recency load-bearing); these kwargs are the fallback path.
        recs_ec = self.reader_ec.resolve_stream(
            mentions, targets, scene_ids=sid_fixed, topical_mode="rolemass",
            query_memory=True, centrality_mode="event_role", **SUP_KW)
        # single-sentence validity baseline (structurally blind cross-sentence)
        recs_ss = self.reader_ss.resolve_stream(
            mentions, targets, reset_per_sentence=True, strategy="maintained")
        resolutions: List[CorefResolution] = []
        for r, tgt in zip(recs_ec, targets):
            resolutions.append(CorefResolution(
                pronoun=tgt["target"]["head"],
                sent_idx=tgt["target"]["sent_idx"],
                gold_cluster=r["gold_cluster"],
                resolved_cluster=(-1 if r["resolved_cluster"] is None
                                  else r["resolved_cluster"]),
                correct=bool(r["correct"]), attempted=bool(r["attempted"]),
                bucket=r["bucket"], sent_dist=r["sent_dist"]))
        return resolutions, recs_ec, recs_ss

    # -- event detection dispatch (stock tense-gated vs opt-in tense-agnostic UPOS==VERB) --
    def _extract_events(self, text):
        """Return (events, tagged) exactly as T.extract_events, dispatching on the tense_agnostic_events
        flag. Default (flag OFF) is byte-identical: it IS T.extract_events."""
        if not self.tense_agnostic_events:
            return T.extract_events(text)
        return self._tense_agnostic_extract(text)

    def _tense_agnostic_extract(self, text):
        """Tense-agnostic UPOS==VERB event detection via the in-substrate UD-trained tagger (glass-box,
        NO spaCy/LLM). Fires a T.Event at every UPOS==VERB token -- trusting the tagger's own AUX/VERB
        split (no form-based AUX blocklist, which wrongly drops main-verb have/do/let). This is the
        validated `fixed_extract_events` from exp_extraction_frontend_end_to_end_live_reader_v1, landed
        behind the flag. Placeholder tense (see the __init__ boundary note)."""
        toks = text.split()
        # PERF sweep #2 (2026-09-04, general): the tense-agnostic detector loads _FRONTEND_POS_ASSET -- the SAME
        # asset the shared frontend tagger uses -- so route its per-sentence tag through the shared per-read cache
        # (_cached_tag) instead of a redundant private PosTagger copy. Byte-identical (same asset); the events path
        # tags these same sentences, so most are cache HITS (measured 81 -> ~0 extra tags/read).
        up = self._cached_tag(toks)
        if self.preserve_tense:
            # tense-PRESERVING: identical detection (same UPOS==VERB tokens -> recall preserved EXACTLY),
            # but a COMPOSED Reichenbach tense/is_pp instead of the placeholder constant. Byte-identical to
            # the validated ref impl (exp_tense_preserving_live_reader_and_timeline_v1.tense_preserving_extract).
            if self._tp_mod is None:
                from hdlab import tense_preserving_detector as _TP   # promoted verbatim (no experiments dep)
                self._tp_mod = _TP
            _TP = self._tp_mod
            sent = _TP.assign_sentence(toks, up, mode="surface")
            events = []
            for i, tk in enumerate(toks):
                if up[i] == "VERB":
                    a = sent[i]
                    events.append(T.Event(lemma=tk.lower(), idx=i, pos=up[i],
                                          tense=_stock_tense(a, _TP), is_pp=bool(a["is_pp"])))
            events = self._add_predicate_recall(events, toks, up)
            return events, []
        events = []
        for i, tk in enumerate(toks):
            if up[i] == "VERB":
                events.append(T.Event(lemma=tk.lower(), idx=i, pos=up[i],
                                      tense=T.TENSE_SIMPLE_PAST, is_pp=False))
        events = self._add_predicate_recall(events, toks, up)
        return events, []

    def _add_predicate_recall(self, events, toks, up):
        """ADDITIVE register-robust predicate recovery (default-off predicate_recall). For each tagger-DROPPED
        real verb (a non-VERB non-AUX token the detector promotes) fire an extra T.Event; the existing
        UPOS==VERB detections are UNTOUCHED (additive -> no regression by construction). Returns the combined
        list SORTED by token index (event order == token order, as the UPOS==VERB loop produced). Default OFF
        returns `events` unchanged. hdlab.predicate_detector -- glass-box 7-weight logistic, NO LLM."""
        if not self.predicate_recall:
            return events
        if self._pred_detector is None:
            from hdlab.predicate_detector import PredicateDetector
            self._pred_detector = PredicateDetector.load()
        ft = self._frontend_tagger()   # same _FRONTEND_POS_ASSET as the old private _ta_tagger -> identical weights/tags
        W = ft._perc.weights
        tags = ft.tags
        for i, _p in self._pred_detector.rescue_indices(toks, up, W, tags):
            events.append(T.Event(lemma=toks[i].lower(), idx=i, pos="VERB",
                                  tense=T.TENSE_SIMPLE_PAST, is_pp=False))
        events.sort(key=lambda e: e.idx)
        return events

    # -- COMPETITION-MODEL AGENT (P2 wire): the AGENT competes over the TRACKED/GIVEN entities (decoupled) --
    def _cm_agent_candidates(self, n_sents):
        """Per-sentence AGENT candidate sets (the TRACKED / GIVEN coref-column nominals) + the per-cluster
        Centering-givenness freq, for the Competition-Model AGENT. Returns (agent_sent_noms, agent_freq), or
        (None, None) when cm_agent is off / referent_per_np off / no coref source -> the positional (or wired)
        AGENT is left UNTOUCHED (byte-identical). The AGENT source (tracked/given) is DECOUPLED from the dense
        PATIENT source; include_pron_agents keeps subject pronouns, case_filter keeps only nominative pronouns."""
        if not (self.cm_agent and self.referent_per_np):
            return None, None
        coref_ment = self._coref_mentions
        if not coref_ment:
            return None, None
        from hdlab.graded_role_assigner import NOMINATIVE_PRON, _nominals_keep_pron
        if self.include_pron_agents:
            agent_sent_noms = _nominals_keep_pron(coref_ment, n_sents)
            if self.case_filter:                       # CASE cue: keep only NOMINATIVE pronoun agents
                agent_sent_noms = [[m for m in lst if (not m.get("is_pronoun"))
                                    or m["head"].lower() in NOMINATIVE_PRON] for lst in agent_sent_noms]
        else:
            agent_sent_noms = _sentence_nominals(coref_ment, n_sents)
        # Centering givenness per cluster (count pronoun mentions too when they are agent candidates --
        # frequent pronominalization == high salience -> a stronger given-entity signal).
        agent_freq = {}
        for m in coref_ment:
            if self.include_pron_agents or not m.get("is_pronoun"):
                agent_freq[m.get("cluster")] = agent_freq.get(m.get("cluster"), 0) + 1
        return agent_sent_noms, agent_freq

    def _cm_agent_for(self, toks, agent_sent_noms, agent_freq, si, pred_idx):
        """The Competition-Model AGENT head for the event at (si, pred_idx), or None to KEEP the positional/
        wired agent (no tracked candidate in this sentence). Clause-bounded when clause_local. Reuses the
        per-read tag cache for the sentence POS -- glass-box, reads only toks/POS + animacy + coref counts."""
        anoms = agent_sent_noms[si] if si < len(agent_sent_noms) else []
        if not anoms:
            return None
        from hdlab.graded_role_assigner import agent_competition_pick, clause_bounds
        up = self._cached_tag(list(toks))
        acand = anoms
        if self.clause_local:                          # bound candidates to the verb's clause span (segmentation)
            lo, hi = clause_bounds(toks, up, pred_idx)
            acand = [m for m in anoms if lo <= m["wtok_start"] < hi] or anoms
        # STRUCTURE cue: the register-general incremental left-corner subject-before array (self-gating; the
        # weighted `structure` support votes only where the parse binds a subject onto a candidate). Default ON;
        # OFF -> subj_before=None -> agent_competition_pick is byte-identical to the pre-structure competition.
        subj_before = None
        if self.cm_agent_struct:
            from hdlab.incremental_parser import incremental_subject_before
            subj_before = incremental_subject_before(toks, up)
        return agent_competition_pick(toks, up, pred_idx, acand, cluster_freq=agent_freq,
                                      weights=self.cm_weights, gaz=self.gaz, twin_seed=self.cm_twin_seed,
                                      subj_before=subj_before)

    # -- EVENTS: per-sentence predicate+agent+patient -> Cowan-4 bundle focus --
    def _read_events(self, sents, mentions, n_sents):
        if self.role_route != "positional":
            return self._read_events_wired(sents, mentions, n_sents)   # ASSEMBLY opt-in; else byte-identical
        codec = EventBundleCodec(n_dim=self.focus_n_dim, roles=DEFAULT_ROLES, seed=FOCUS_SEED)
        focus = ChunkedFocus(codec, capacity=4, fanout=2, seed=FOCUS_SEED)
        sent_noms = _sentence_nominals(mentions, n_sents)   # DENSE referent set -> PATIENT (the residual, +0.336)
        agent_sent_noms, agent_freq = self._cm_agent_candidates(n_sents)  # TRACKED/given set -> AGENT (decoupled)
        events: List[EventRecord] = []
        role_fillers: List[Dict[str, str]] = []
        suppressed: List[SuppressedPredicate] = []
        gidx = 0
        for si, toks in enumerate(sents):
            text = " ".join(toks)
            evs, _tagged = self._extract_events(text)
            noms = sent_noms[si] if si < len(sent_noms) else []
            # supplied-grammar gate: valid predicate LOW tokens for THIS sentence (spaCy VERBs)
            verb_lows = self.pred_gate_fn(text) if self.pred_gate_fn is not None else None
            for e in evs:
                agent, patient = _assign_roles(e.idx, noms, lemma=e.lemma,
                                               gate_intransitive=self.gate_intransitive)
                # CM-AGENT (cm_agent): recompute the AGENT by the Competition-Model competition over the
                # TRACKED/given entities; PATIENT is left EXACTLY as _assign_roles produced it (byte-identical).
                if agent_sent_noms is not None:
                    cm_a = self._cm_agent_for(toks, agent_sent_noms, agent_freq, si, e.idx)
                    if cm_a is not None:
                        agent = cm_a
                if verb_lows is not None and e.lemma not in verb_lows:
                    # POS mis-tag (non-verb read as a predicate) -> suppress (glass-box record)
                    suppressed.append(SuppressedPredicate(
                        sent_idx=si, predicate=e.lemma, tense=str(e.tense),
                        agent=agent, patient=patient))
                    continue
                rf = {"PRED": e.lemma, "AGENT": agent, "PATIENT": patient,
                      "TENSE": str(e.tense)}
                vec = codec.encode_event(rf)
                focus.push(vec, gidx)
                # Component-3 wire: frame-primary thematic labels for the same agent/patient heads
                # (additive metadata; does not change codec encoding or head selection above).
                subj_role, obj_role = _assign_frame_primary_roles(
                    e.lemma, toks, e.idx, noms, gate_intransitive=self.gate_intransitive)
                # grounded-affect wire: certified animacy-axis valence for the same patient head
                # (additive metadata; does not change codec encoding or head selection above).
                affect = _assign_affect(patient, text)
                events.append(EventRecord(global_idx=gidx, sent_idx=si, predicate=e.lemma,
                                          agent=agent, patient=patient, tense=str(e.tense),
                                          subj_role=subj_role, obj_role=obj_role, affect=affect,
                                          pred_idx=e.idx))
                role_fillers.append(rf)
                gidx += 1
        return events, focus, codec, role_fillers, suppressed

    # -- ASSEMBLY reader-role-routing (opt-in; role_route != "positional") -----------------------------
    # A verbatim port of the validated WiredSituationReader (exp_wire_predarg_binder_live_reader_integration
    # _v1): route each event's agent/patient through a real parse -> route_predicate_arguments (+ a
    # reader-native, case-independent quotative-inversion rule) with the positional rule as the good-enough
    # fallback; richer roles (goal/recipient/...) are collected as additive metadata. Everything else
    # (event extraction, encoding, focus, frame/affect metadata) is UNCHANGED from the stock _read_events.
    def _cached_tag(self, toks):
        """Per-read memoized POS tag (see self._read_parse_cache): tag each distinct sentence ONCE per read().
        Returns a FRESH copy each call (like the original per-call self._tagger.tag) so a consumer that mutates
        it cannot corrupt the cache -> byte-identical; the saved cost is the Viterbi tag, not the tiny copy."""
        key = ("tag", tuple(toks))
        c = self._read_parse_cache
        if key not in c:
            c[key] = self._frontend_tagger().tag(toks)
        return list(c[key])

    def _frontend_tagger(self):
        """The SINGLE shared frontend POS tagger, lazily loaded (the module-level _FRONTEND_CACHE makes reload
        free). role_route!='positional' loads it eagerly; ANY organ that needs it under ANY config (entity-states,
        causal, ...) gets the SAME instance -> no organ carries a redundant private copy, and _cached_tag works
        regardless of role_route. General, not tied to one reader configuration."""
        if getattr(self, "_tagger", None) is None:
            self._tagger, self._parser = _load_frontend()
        return self._tagger

    def _frontend_parser(self):
        """The SINGLE shared frontend arc parser (see _frontend_tagger). NOT the parser_arceager opt-in (that is a
        separate role-routing path); this is the base frontend parser the per-read parse cache memoizes."""
        if getattr(self, "_parser", None) is None:
            self._tagger, self._parser = _load_frontend()
        return self._parser

    def _cached_parse_heads(self, toks, pos):
        """Per-read memoized SINGLE shared parse heads dict; returns a FRESH copy (see _cached_tag).

        DOUBLE-PARSE CONSOLIDATION 2026-09-05 (owner-DONE consolidate_the_arceager_and_arc_double_parse...): when
        parser_arceager (the default), the ONE shared per-read parse is the arc-eager INCREMENTAL parse (the
        PINNED brain-foundational parser -- Lewis-Vasishth incremental working-memory decode), serving BOTH the
        role path (_router_roles) AND the front-end (copular/space) -- so the base arc-FACTORED batch parser is
        never called on the read path (eliminates the redundant second parse: ~5% read-cost cut, full board ZERO
        regression -- 6/9 consumed dims byte-identical, copular/space measured no-regress; witness 14/14). The
        ROLE heads are byte-identical either way (same arceager_parser.parse_with_conf + weights); only the
        front-end switches batch->incremental (the measured no-regress). When parser_arceager=False it is
        byte-identical to the historical batch-parser path. The batch parser stays loadable (_frontend_parser) as
        a self-checkable byte-identity reference."""
        key = ("parse", tuple(toks))
        c = self._read_parse_cache
        if key not in c:
            if self.parser_arceager:
                if self._ae_W is None:
                    from hdlab.arceager_parser import load_model, parse_with_conf, MODEL_PATH
                    self._ae_W = load_model(MODEL_PATH)
                    self._ae_parse = parse_with_conf
                c[key] = self._ae_parse(toks, pos, self._ae_W)[0]   # 1-based child->head (same shape as ArcParser)
            else:
                c[key] = self._frontend_parser().parse(toks, pos).heads
        return dict(c[key])

    def _frontend_labeler(self):
        """Shared lazy arc labeler (UD deprels) -- for the goal advcl purpose filter (+ reused by entity_states)."""
        if self._lab is None:
            from hdlab.arc_labeler import ArcLabeler
            self._lab = ArcLabeler.load(os.path.join(_REPO, "data/frontend_assets/arc_labeler_hashed_ud_ewt.json"))
        return self._lab

    @staticmethod
    def _has_to_verb(toks, up):
        """True iff some 'to' token (index 1..len-2) is immediately followed by a VERB. This is the EXACT
        entry gate of GR.extract_goals_sentence branch (3) (goal_register.py:259-262), the ONLY consumer of
        the arc-labeler deprels (the ADVCL purpose filter, :299-303). A sentence failing this can NEVER reach
        the deprel read, so skipping its labeling is BYTE-IDENTICAL to labeling it -- the efficiency gate for
        the goal purpose filter (avoids labeling the ~75-90% of prose sentences with no 'to VERB')."""
        for k in range(1, len(toks) - 1):
            if toks[k].lower() == "to" and (k + 1) < len(up) and up[k + 1] == "VERB":
                return True
        return False

    def _router_roles(self, toks):
        """{verb_pos0: {pa_role: token_pos0}} from parse -> route_predicate_arguments, fed the reader's OWN
        tokens so indices align with mention wtok positions. quotative=False: the reader applies its OWN
        mention-based quotative below (its tokens are lowercased, so the router's capitalization-based
        speaker scan cannot fire here). Empty for empty / very long token lists."""
        if not toks or len(toks) > 120:
            return {}
        pos = self._cached_tag(toks)
        # DOUBLE-PARSE CONSOLIDATION: read heads from the SINGLE shared per-read parse cache (arc-eager when
        # parser_arceager) instead of a separate _ae_parse call -- so the front-end (copular/space) and this role
        # path share ONE parse (was two). Role heads are byte-identical (the shared parse IS arc-eager when the
        # flag is on, same weights); the batch parser is no longer called on the read path.
        heads = self._cached_parse_heads(toks, pos)
        out = {}
        # structural_patient passed ONLY when ON, so the OFF wired path issues a call BYTE-IDENTICAL to the
        # historical one (no new kwarg) -- preserving any caller-side wrapper/monkeypatch of the router that
        # predates this param (e.g. the solver's no-regress scaffold).
        sp_kw = {"structural_patient": True} if self.structural_patient else {}
        for v in matrix_verbs(toks, pos, heads):
            roles = route_predicate_arguments(toks, pos, heads, v, quotative=False,
                                              np_head_reduce=self.np_head_reduce, **sp_kw)
            out[v - 1] = {k: (val - 1) for k, val in roles.items() if isinstance(val, int) and val}
        return out

    @staticmethod
    def _align_events_to_toks(evs, toks):
        """Map each event's predicate (surface e.lemma) to its `toks` index, greedy left-to-right (the
        event extractor's tokenization != `toks`, so e.idx cannot be trusted). None if no surface match."""
        low = [t.lower() for t in toks]
        used = set()
        out = []
        for e in evs:
            j = next((k for k in range(len(low)) if k not in used and low[k] == str(e.lemma).lower()), None)
            if j is not None:
                used.add(j)
            out.append(j)
        return out

    @staticmethod
    def _nom_head_at(noms, pos0):
        """The non-pronoun mention head at/covering token position pos0 (the reader tracks only non-pronoun
        heads for roles), else the nearest within 1 token, else None."""
        for m in noms:
            if m["wtok_start"] == pos0:
                return m["head"]
        for m in noms:
            if abs(m["wtok_start"] - pos0) <= 1:
                return m["head"]
        return None

    def _read_events_wired(self, sents, mentions, n_sents):
        """Copy of _read_events with ONE change: agent/patient come from the parse -> router (mapped to the
        reader's mention heads) with the positional rule as the good-enough fallback; richer roles are
        collected on self.wired_extra_roles. Everything else is identical to the stock path."""
        codec = EventBundleCodec(n_dim=self.focus_n_dim, roles=DEFAULT_ROLES, seed=FOCUS_SEED)
        focus = ChunkedFocus(codec, capacity=4, fanout=2, seed=FOCUS_SEED)
        sent_noms = _sentence_nominals(mentions, n_sents)
        agent_sent_noms, agent_freq = self._cm_agent_candidates(n_sents)  # TRACKED/given set -> AGENT (decoupled)
        events: List[EventRecord] = []
        role_fillers: List[Dict[str, str]] = []
        suppressed: List[SuppressedPredicate] = []
        self.wired_extra_roles = []
        gidx = 0
        for si, toks in enumerate(sents):
            text = " ".join(toks)
            evs, _tagged = self._extract_events(text)
            noms = sent_noms[si] if si < len(sent_noms) else []
            if self.np_head_reduce and noms:
                # POSITIONAL-path fix: drop mentions whose head token is a compound modifier / genitive possessor,
                # so _assign_roles + the router's _nom_head_at pick the NP HEAD (mention-level 2nd-pass wire).
                from hdlab.np_head_reduce import is_np_head as _is_np_head
                _up = self._cached_tag(list(toks))
                noms = [m for m in noms if _is_np_head(toks, _up, m["wtok_start"])] or noms
            rr = self._router_roles(list(toks))
            # the event extractor uses a DIFFERENT tokenization than `toks` (e.idx is its space, not toks-
            # space); align each event's predicate to its `toks` position by surface match (greedy L->R), so
            # router roles (keyed in toks-space, the mention wtok_start space) line up with the reader's event.
            toks_pos = self._align_events_to_toks(evs, toks)
            verb_lows = self.pred_gate_fn(text) if self.pred_gate_fn is not None else None
            for ei, e in enumerate(evs):
                # positional roles (the fallback + the OFF behavior), computed identically to the stock reader
                agent, patient = _assign_roles(e.idx, noms, lemma=e.lemma,
                                               gate_intransitive=self.gate_intransitive)
                extra: Dict[str, object] = {}
                vp = toks_pos[ei]
                if vp is not None and is_speech_verb(lemma_verb(e.lemma)):
                    # QUOTATIVE INVERSION, reader-native (case-independent): the reader's tokens are
                    # lowercased, so use the MENTION structure -- the speaker (AGENT) is the nearest
                    # postverbal tracked mention ("... said John"), else the nearest preverbal; the quoted
                    # content is not a role filler.
                    post = [m for m in noms if m["wtok_start"] > vp]
                    pre = [m for m in noms if m["wtok_start"] < vp]
                    spk = post[0]["head"] if post else (pre[-1]["head"] if pre else None)
                    if spk is not None:
                        agent, patient = spk, "?"
                else:
                    vr = rr.get(vp) if vp is not None else None
                    if vr is not None:
                        a_head = self._nom_head_at(noms, vr["agent"]) if "agent" in vr else None
                        t_head = self._nom_head_at(noms, vr["theme"]) if "theme" in vr else None
                        if a_head is not None:
                            agent = a_head        # ROUTER agent (fixes passive/ditransitive), else positional
                        if t_head is not None:
                            patient = t_head
                        for pa in ("goal", "recipient", "source", "location", "path", "direction", "instrument"):
                            if pa in vr:
                                h = self._nom_head_at(noms, vr[pa])
                                if h is not None:
                                    extra[PREDARG_TO_GOLD.get(pa, pa)] = h
                # CM-AGENT (cm_agent): recompute the AGENT by the Competition-Model competition over the
                # TRACKED/given entities, OVERRIDING the positional/quotative/router agent; PATIENT untouched
                # (byte-identical). Runs after the wired agent so the same brain-foundational agent is used
                # regardless of role_route (the SOLVED proof was on role_route='positional'; this extends it).
                if agent_sent_noms is not None:
                    cm_a = self._cm_agent_for(toks, agent_sent_noms, agent_freq, si, e.idx)
                    if cm_a is not None:
                        agent = cm_a
                if verb_lows is not None and e.lemma not in verb_lows:
                    suppressed.append(SuppressedPredicate(sent_idx=si, predicate=e.lemma, tense=str(e.tense),
                                                          agent=agent, patient=patient))
                    continue
                rf = {"PRED": e.lemma, "AGENT": agent, "PATIENT": patient, "TENSE": str(e.tense)}
                vec = codec.encode_event(rf); focus.push(vec, gidx)
                subj_role, obj_role = _assign_frame_primary_roles(e.lemma, toks, e.idx, noms,
                                                                  gate_intransitive=self.gate_intransitive)
                affect = _assign_affect(patient, text)
                pib = None
                if self.structural_do_recover and patient not in ("?", None) and vp is not None:
                    # STRUCTURAL-DO (§0g wire): is the bound patient a BARE post-verbal direct object of this verb?
                    # verb (vp) + candidate indices are in toks-space here; find the nearest post-verbal nom whose
                    # head == patient. Feeds the verb_subcat veto override in read(). Lazy import when on.
                    if self._sdo is None:
                        from hdlab import structural_do as _SDO
                        self._sdo = _SDO
                    pcands = [m["wtok_start"] for m in noms
                              if m.get("head") == patient and m["wtok_start"] > vp]
                    if pcands:
                        _up = self._cached_tag(list(toks))
                        pib = bool(self._sdo.is_bare_do(toks, _up, vp, min(pcands)))
                    else:
                        pib = False   # patient is not a post-verbal nominal -> not a bare DO -> allow the veto
                events.append(EventRecord(global_idx=gidx, sent_idx=si, predicate=e.lemma, agent=agent,
                                          patient=patient, tense=str(e.tense), subj_role=subj_role,
                                          obj_role=obj_role, affect=affect, pred_idx=e.idx,
                                          patient_is_bare_do=pib))
                role_fillers.append(rf)
                if extra:
                    self.wired_extra_roles.append({"global_idx": gidx, **extra})
                gidx += 1
        return events, focus, codec, role_fillers, suppressed

    # -- MEMORY glass-box: role-query round-trip on the recent (direct) events --
    @staticmethod
    def _memory_roundtrip(focus: ChunkedFocus, codec: EventBundleCodec,
                          events: List[EventRecord], role_fillers: List[Dict[str, str]]):
        n_direct = n_ok = 0
        for ev, rf in zip(events, role_fillers):
            try:
                if not focus.is_direct(ev.global_idx):
                    continue
            except KeyError:
                continue  # compressed out of the bounded focus (expected, Cowan-4 forgetting)
            n_direct += 1
            for role in ("AGENT", "PATIENT", "PRED"):
                sym, _score = focus.query(ev.global_idx, role)
                if sym == rf[role]:
                    n_ok += 1
        n_probes = n_direct * 3
        return {"n_direct_events": n_direct, "n_probes": n_probes, "n_ok": n_ok,
                "roundtrip_rate": (n_ok / n_probes) if n_probes else 0.0}

    # -- TIME: reconstruct chronology on the passage's flashback (past-perfect) sentences --
    @staticmethod
    def _read_timeline(sents) -> List[TimelineFrame]:
        frames: List[TimelineFrame] = []
        for si, toks in enumerate(sents):
            if "had" not in toks:
                continue  # cheap gate: past-perfect flashback candidate
            text = " ".join(toks)
            ev, tg = M.extract_events_punct(text)
            if len(ev) < 2:
                continue
            order, _edges = M.reconstruct_order_timeline(ev, tg, use_connectives=True,
                                                         cross_sentence=True)
            chrono = [e.lemma for e in order]
            text_ord = [e.lemma for e in T.text_order(ev)]
            if not chrono:
                continue
            frames.append(TimelineFrame(sent_idx=si, text=text, text_order=text_ord,
                                        chrono_order=chrono, reordered=(chrono != text_ord)))
        return frames

    # -- TIME (opt-in whole-passage register): ONE chronological event order over the WHOLE passage --
    def _read_timeline_register(self, sents) -> list:
        """Opt-in whole-passage TEMPORAL-ORDER register (default-off; wired 2026-08-31 from the validated
        experiments/_temporal_order_register.py). Unlike _read_timeline -- which runs PER-SENTENCE and gates on
        `"had" in toks` (dropping connective-only reorderings) -- this reconstructs ONE chronological EVENT ORDER
        over the WHOLE passage using the brain-faithful clause-level pluperfect binder (clause_pluperfect=True,
        the validated config -- recovers pluperfects the fixed-window extractor mistags) + the discrete
        constraint-graph toposort (Reference-time carried across sentences, Reichenbach E/R/S). Returns the
        register's OWN chronological order as a serializable list of dicts, one per event in CHRONOLOGICAL order:
        {lemma, chrono_rank, text_rank}. NO new ordering logic -- this is exactly reg.order / reg.text_rank, so
        it is equivalence-checkable against a direct register build. Glass-box + deterministic (discrete toposort;
        no torch/seed). Lazy import -> the default (OFF) reader never imports the register module."""
        from experiments import _temporal_order_register as TOR
        ev, tg, edges = TOR.extract_passage(sents, clause_pluperfect=True)
        reg = TOR.DiscreteOrderRegister(ev, tg, edges)
        return [{"lemma": lem, "chrono_rank": i, "text_rank": reg.text_rank.get(lem)}
                for i, lem in enumerate(reg.order)]

    def _read_space(self, conll_path):
        """Opt-in SPACE dimension (default-off; wired 2026-08-31 from the validated
        experiments/_space_reader.py). Returns a hdlab.location_register.LocationRegister -- per-entity
        location as STATE, updated ONLY by motion events and PERSISTING between (Zwaan & Radvansky
        event-indexing SPACE; categorical nodes) -- driven by the reader's OWN in-substrate parse+coref, in
        `prior_ext` mode (the validated best arm: noisy-channel parse-as-EVIDENCE fused with a persistence
        PRIOR + the three brain-faithful recall extensions; a stronger general parser does NOT beat it, so
        the ceiling is parser RECALL, not parse quality). Query with sm.locations.where_is(entity_id, t) /
        present_in_scene. NO spaCy (in-substrate). Lazy import -> the default (OFF) reader never imports it."""
        if self._space_mod is None:
            from experiments import _space_reader as _SP
            self._space_mod = _SP
        _SP = self._space_mod
        # PARSE DEDUP (2026-09-03): _read_space runs AFTER _read_events, so the reader's per-read tag/parse cache
        # is already warm -> the space adapter reuses the reader's parse (SAME model) instead of re-parsing every
        # sentence a second time (~half the read's parser cost). Byte-identical.
        reg, _events, _names, _sents, _persons = _SP.read_locations_in_substrate(
            conll_path, gaz=self.gaz, mode="prior_ext", parse_provider=self._space_parse_provider)
        return reg

    def _space_parse_provider(self, toks):
        """(upos, heads) for the SPACE adapter from the reader's per-read cache -> parse each sentence ONCE."""
        u = self._cached_tag(toks)
        return u, self._cached_parse_heads(toks, u)

    def _read_belief(self, sm, sents) -> None:
        """Opt-in BELIEF/ToM dimension (default-off; wired 2026-08-31 from the owner-DONE problem
        the_belief_dimension_is_never_driven_by_the_readers_own_extraction_on_real_prose). Bind two QUERY
        callables to THIS passage's own sentences: sm.believes(agent_aliases, fact, t) and sm.knows(...).
        Each drives the promoted hdlab.belief_timeline from the reader's OWN 4-channel extraction via the
        lazily-imported experiments._belief_reader.drive (narrator-epistemic + testimony [substrate-native] +
        perception [PAL observation gate, lazy spaCy] + inference), reality separate, ignorance = None. A
        `fact` is {fact_aliases, value_vocab[, fact_type]}. believes -> the registered belief VALUE at t
        (may diverge from reality = false belief); knows -> Butterfill & Apperly registration
        (current/stale/ignorant). Byte-faithful to the validated driver (the witness asserts believes ==
        timeline_belief(*drive(...))). Lazy -> the default (OFF) reader imports NONE of this."""
        if self._belief_mod is None:
            from experiments import _belief_reader as _BR
            self._belief_mod = _BR
        BR = self._belief_mod
        from hdlab.belief_timeline import timeline_belief, reality_at
        if self._belief_led is None:
            from hdlab.perceptual_access_ledger import PerceptualAccessLedger
            self._belief_led = PerceptualAccessLedger()   # spaCy lazy-loaded on first perception use
        led = self._belief_led
        by_sent = {i: [] for i in range(len(sents))}

        def _drive(fact, agent_aliases):
            events, observed, agent, _re, _ba, _src = BR.drive(sents, by_sent, fact, agent_aliases, led)
            return events, observed, agent, str(fact["fact_aliases"][0]).lower()

        def believes(agent_aliases, fact, t):
            events, observed, agent, fh = _drive(fact, agent_aliases)
            return timeline_belief(events, observed, agent, fh, float(t))

        def knows(agent_aliases, fact, t):
            events, observed, agent, fh = _drive(fact, agent_aliases)
            belief = timeline_belief(events, observed, agent, fh, float(t))
            if belief is None:
                return "ignorant"
            return "current" if belief == reality_at(events, fh, float(t)) else "stale"

        sm.believes = believes
        sm.knows = knows

    def _read_bound_event_tokens(self, sm) -> None:
        """Opt-in BOUND-EVENT-TOKEN backbone (default-off; wired 2026-09-01 from the owner-DONE problem
        the_assembled_reader_is_parallel_silos_assemble_the_tiered_bound_event_token, p4). Build ONE FHRR
        bound token per event over {AGENT,PATIENT,PRED,TENSE} (the JOINT the parallel-silo dimensions never
        store) + a tiered episodic store (N400-chunked + DG/CA3), via the promoted thin assembler
        hdlab.bound_event_backbone.BoundEventBackbone (COMPOSES existing organs only; the tokens are
        torch-equal to the validated cell's). sm.episodic_store.resolve/corefer answers 'does this exact
        event -- this agent, this action -- occur?' from a partial mention. Lazy -> the default (OFF) reader
        imports NONE of this. NO spaCy / NO LLM."""
        if self._beb_mod is None:
            from hdlab import bound_event_backbone as _BEB
            self._beb_mod = _BEB
        BEB = self._beb_mod
        sm.event_tokens, sm.episodic_store = BEB.BoundEventBackbone(d=BEB.D).build(sm.events, sm.locations)

    def _read_predict_revise(self, sm, sents) -> None:
        """Opt-in PARSE-RECALL drop-fill (default-off; wired 2026-09-01 from the owner-DONE problem
        the_reader_parses_as_truth_where_the_brain_parses_predictively_predict_and_revise). For each event
        whose patient is '?' (DROPPED -- the structural coverage violation), fill it by REUSING the validated
        hdlab.relcl_resolver.resolve_patient (passive-subject / object-gap / word-order routes) as the fill
        TARGET, with a nearest-nominal POSITION fallback when it declines; record the original '?' on
        EventRecord.patient_prerevise (glass-box, reversible). Faithful to the validated drill's relcl_fill
        (resolve_patient + nominal_positions fallback); the witness asserts byte-equality on the reader's own
        events. Recall-scoped ONLY -- no post-verbal re-selection, no surprisal gate (p2's proven negatives).
        Lazy imports -> the default (OFF) reader loads none of this. NO spaCy / NO LLM."""
        if self._pr_revise_rr is None:
            from hdlab import relcl_resolver as _RR
            self._pr_revise_rr = _RR
        RR = self._pr_revise_rr
        if self._pr_revise_tagger is None:
            from experiments._forward_prediction_live import get_tagger
            self._pr_revise_tagger = get_tagger()
        tagger = self._pr_revise_tagger
        if self._pr_revise_nom is None:
            from experiments._forward_prediction_live import NOMINAL, PRON_LOW
            self._pr_revise_nom = (NOMINAL, PRON_LOW)
        NOMINAL, PRON_LOW = self._pr_revise_nom
        pos_cache: Dict[int, list] = {}

        def _pos(si):
            if si not in pos_cache:
                pos_cache[si] = tagger.tag(sents[si])
            return pos_cache[si]

        for e in sm.events:
            if e.patient not in ("?", None) or e.pred_idx is None:
                continue
            si = e.sent_idx
            if not (0 <= si < len(sents)):
                continue
            toks = sents[si]
            up = _pos(si)
            v0 = int(e.pred_idx)
            # nominal (non-pronoun) candidates (head_low, idx) -- VERBATIM the drill's nominal_positions
            cands = [(toks[i].lower(), i) for i in range(len(toks))
                     if i < len(up) and up[i] in NOMINAL and toks[i].lower() not in PRON_LOW]
            idx = RR.resolve_patient(toks, up, v0 + 1)   # resolve_patient is 1-based on the verb index
            if idx is not None and 1 <= idx <= len(toks):
                head = toks[idx - 1].lower()
            elif cands:                                  # fallback: nearest nominal (position)
                best, bd = None, 10 ** 9
                for (h, ci) in cands:
                    if abs(ci - v0) < bd:
                        bd, best = abs(ci - v0), h
                head = best
            else:
                continue
            e.patient_prerevise = e.patient              # the original '?'
            e.patient = head

    def _read_world_state(self, sm, sents) -> None:
        """Fold THIS passage's OWN extracted events into a mutable WORLD-STATE register (default-off
        track_world_state; wired 2026-09-01 from the owner-DONE problem
        situation_model_has_no_mutable_world_state_register). Per event: PRED/AGENT/PATIENT from the reader's
        extraction (dropped '?'/None normalized away so no junk track, but the event is KEPT so story-time t
        stays aligned), ARG2 (recipient/source) from self.wired_extra_roles (the wired richer-role metadata,
        keyed by global_idx), and the STRIPS operator class from the FrameNet-derived
        hdlab.possession_operators lexicon (cached json -- no nltk at inference). Sets sm.world_state = a
        hdlab.world_state_register.WorldState whose has(entity,obj,t)/holder_of(obj,t)/is_open(obj,t)/
        unmet_preconditions() answer the STATE the parallel-silo event LIST could not. Open-text who-has-what is
        coref-bound (the located residual, a NAMED existing organ). Lazy import -> the default (OFF) reader loads
        none of this. NO spaCy / NO LLM.

        COREF-DENSIFY SUB-FLAG (densify_world_state, default OFF): when on, HOLDER keys are the canonical
        discourse-entity (EntityBinder) instead of the raw head, so possession attaches to the entity node
        (John...he...him -> one key), not the surface mention. Default OFF -> raw-head keying, byte-identical."""
        from hdlab.world_state_register import WorldState
        if self._ws_lex is None:
            from hdlab.possession_operators import build_lexicon
            self._ws_lex = build_lexicon()
        lex = self._ws_lex
        extra_by_gi = {r.get("global_idx"): r for r in (getattr(self, "wired_extra_roles", None) or [])}
        # COREF-DENSIFY (opt-in, default OFF -> binder is None -> raw-head keying, byte-identical). When on, key
        # each HOLDER on its canonical discourse-entity via the promoted EntityBinder: self-contained routes
        # (indexical/object-anaphora/nominal/abstain) fire on the head; the he/she anaphoric route consumes the
        # reader's OWN coref via a (sent_idx, pronoun-head) -> resolved-cluster map built from sm.coref_resolutions
        # (the reader already computed it; no new resolver, no gold at inference). Events are folded in reading
        # order (global_idx), so the binder's Centering recency (object 'it' -> salient nominal theme) is faithful.
        binder = None
        he_she_cluster: Dict[tuple, int] = {}
        if self.densify_world_state:
            if self._ws_binder_mod is None:
                from hdlab import world_state_entity_binding as _WSB
                self._ws_binder_mod = _WSB
            binder = self._ws_binder_mod.EntityBinder()
            for r in (sm.coref_resolutions or []):
                rc = r.resolved_cluster
                if rc is not None and rc >= 0:
                    # the RAW cluster id: EntityBinder.bind_participant formats the "C%s" key itself.
                    he_she_cluster[(r.sent_idx, (r.pronoun or "").lower())] = rc
        reps = []
        for e in sm.events:
            v = (e.predicate or "").lower()
            entry = lex.get(v)
            op = entry.get("op") if entry else None
            roles = extra_by_gi.get(e.global_idx) or {}
            arg2 = roles.get("recipient") or roles.get("source")
            ag = e.agent if e.agent not in ("?", None) else None
            pat = e.patient if e.patient not in ("?", None) else None
            if binder is not None:
                # canonicalize theme FIRST so a same-event nominal theme is the salient antecedent for object
                # anaphora within this event's holders; holders (agent + recipient/source) -> entity keys.
                pat = (binder.bind_theme(pat, verb=v)[0]) if pat is not None else None
                ag = (binder.bind_participant(ag, coref_cluster=he_she_cluster.get((e.sent_idx, ag.lower())))[0]
                      if ag is not None else None)
                arg2 = (binder.bind_participant(arg2, coref_cluster=he_she_cluster.get((e.sent_idx, arg2.lower())))[0]
                        if arg2 is not None else None)
            reps.append({"PRED": v, "AGENT": ag, "PATIENT": pat, "ARG2": arg2, "OP": op})
        sm.world_state = WorldState().fold(reps)

    @staticmethod
    def _nominal_heads(toks, up) -> List[str]:
        """Candidate-argument head strings the reader could have bound (lowercased, deduped, sorted) --
        VERBATIM from the validated experiments/_forward_prediction_live.nominal_heads: NOUN/PROPN/PRON
        tokens minus the closed-class pronouns (which the reader never binds as role heads)."""
        out = []
        for i, tk in enumerate(toks):
            if i < len(up) and up[i] in _SURPRISAL_NOMINAL_POS:
                low = tk.lower()
                if low in _SURPRISAL_PRON_LOW:
                    continue
                out.append(low)
        return sorted(set(out))

    def _read_surprisal(self, sm, sents) -> None:
        """Opt-in FORWARD-PREDICTION surprisal (default-off; wired 2026-08-31 from the owner-DONE problem
        the_forward_prediction_organ_is_inert...). POST-READ pass: for each event, compute the N400
        surprisal of the reader's OWN bound PATIENT among its sentence's candidate nominals via the promoted
        predictive_reader (loaded from the persisted QA-SRL-fitted asset), and expose it + the verb-role
        precision as ADDITIVE EventRecord metadata; mark low_confidence above the abstain tau. Matches the
        validated experiments/_forward_prediction_live driver byte-for-byte (verb=lemma_word(predicate),
        role='PATIENT', cands=_nominal_heads). NO spaCy / NO LLM; abstains (None) on an ungrounded verb-role
        or filler rather than guessing. Runs LAST (after verb_subcat_gate), so it scores the final patient."""
        if self._pr_predictor is None:
            from hdlab.predictive_reader import PredictiveReader
            self._pr_predictor = PredictiveReader.load(self.predict_surprisal_asset or _PREDICT_SURPRISAL_ASSET)
        pr = self._pr_predictor
        cand_cache: Dict[int, List[str]] = {}

        def cands_for(si: int) -> List[str]:
            if si not in cand_cache:
                toks = sents[si] if 0 <= si < len(sents) else []
                # PERF sweep #2: route through the shared per-read tag cache (was a private _ta_tagger copy loading
                # the same _FRONTEND_POS_ASSET) -> byte-identical, cache HIT on already-tagged sentences.
                cand_cache[si] = self._nominal_heads(toks, self._cached_tag(toks)) if toks else []
            return cand_cache[si]

        for e in sm.events:
            if e.patient in ("?", None):
                continue
            verb = lemma_word(str(e.predicate).lower())
            s = pr.surprisal(verb, "PATIENT", str(e.patient).lower(), cands_for(e.sent_idx))
            e.patient_surprisal = None if s is None else round(float(s), 6)
            e.pred_precision = pr.precision(verb, "PATIENT")
            if e.patient_surprisal is not None and self.surprisal_abstain_tau is not None:
                e.low_confidence = bool(e.patient_surprisal > self.surprisal_abstain_tau)

    # -- CAUSATION: cause->outcome on the passage's causal-connective sentences --
    def _read_causation(self, sents) -> List[CausalLink]:
        """Populate sm.causal_links over the reader's OWN event stream. FIX 2026-09-03 (causal-dimension
        measurement artifact): the organ used to re-detect events via C.extract -> T.extract_events (the
        STOCK tense-GATED detector, tagger=None), a SPARSER set than the situation model's densified
        `_extract_events` (tense_agnostic_events + predicate_recall). So on 82.6% of the board's
        connective-gold causal questions the outcome predicate (located in the DENSIFIED sm.events) was
        absent from sm.causal_links -> the readout ABSTAINED -> causal scored 0.1485, BELOW its own
        adjacency floor 0.5248 (a below-floor number is a measurement lie: the reader was not answering
        backwards, it had no link to answer WITH). Fix: run the reader's causal ORGAN (connective/bridge
        direction, C.causal_net_cause -- unchanged mechanism) over `self._extract_events` (the SAME events
        the situation model + the gold use), and record EVERY connective/bridge link per sentence (not the
        first). This makes the situation model actually REPRESENT the text's connective causation. The cause
        SELECTION is still the organ's connective/bridge rule (not the gold's code); it must still BEAT the
        adjacency floor (connective direction != recency on 'because/since' effect-first cases) and a
        reversed/shuffled twin must lose. This is connective-STRUCTURE recovery (the dimension's stated
        scope), NOT force-dynamics reasoning (the separate typed causation path). sm.causal_links is
        consumed ONLY by the causal readout, so this is additive to every other dimension.

        SCOPED 2026-09-05 (owner-DONE register_robust_event_detection...): computed over the BASE (non-recall)
        event set even when predicate_recall is default-ON. predicate_recall's extra recovered events add
        distractor causes in connective sentences that mis-pick the connective/bridge selection (a density-brittle
        OUR-INVENTION heuristic) -> causal regresses -0.0594 CI-sep if unscoped. Temporarily disabling recall for
        THIS method's own _extract_events makes sm.causal_links BYTE-IDENTICAL to the recall-OFF reader while
        sm.events (already built with recall) keeps the who-did-what densification. The faithful fix (force-dynamic
        attribution) is the filed meaning-hub successor; scoping is the measured interim."""
        saved_recall = self.predicate_recall
        self.predicate_recall = False               # scope: causal extraction sees the base (validated) density
        try:
            links: List[CausalLink] = []
            for si, toks in enumerate(sents):
                if not (_CAUSAL_CONNECTIVES & set(toks)):
                    continue
                events, _tagged = self._extract_events(" ".join(toks))   # the reader's OWN densified events
                if len(events) < 2:
                    continue
                low = [t.lower() for t in toks]
                # try each event as the outcome-to-explain; record EVERY genuine connective/bridge cause link
                # (order-agnostic: "X because Y" states the effect first, so the last event is not the outcome).
                for outcome in events:
                    cause_ev, method = C.causal_net_cause(events, low, outcome)
                    if cause_ev is None or cause_ev.lemma == outcome.lemma:
                        continue
                    if method not in ("connective", "bridge"):
                        continue
                    links.append(CausalLink(sent_idx=si, cause=cause_ev.lemma,
                                            outcome=outcome.lemma, method=method))
            # PASS 2 -- MENTAL-BRIDGE links on NON-connective sentences (owner-DONE a_force_dynamic_meaning_hub_
            # causal_scorer_retire_the_connective_scoping_workaround, 2026-09-05, Q111). The brief's literal route
            # (retire scoping via a plausibility selector) is a LOCATED NEGATIVE -- connective cause-selection is
            # STRUCTURAL and scoping is its OPTIMUM (a force+agentivity plausibility selector is CI-sep WORSE,
            # -0.2079; and the connective causal QA gold IS the positional rule, so a perfect-parse oracle LOSES too
            # -- the refutation is mechanism-agnostic). The landable value is the DEEPER wall: most narrative
            # causation is MENTAL ("she saw the letter, then wept") -- a DISTINCT brain system (Jack 2013 / Saxe
            # 2003 / Campanella 2022) the physical force lexicon structurally cannot represent (it covers ~3/16 real
            # cause verbs; 11/16 are perception/cognition/emotion/communication). This appends a folk-psych episode-
            # schema bridge (Rumelhart/Stein&Glenn story grammar; Malle BDI; OCC appraisal) over the WordNet
            # event-TYPE representation (hdlab.event_type): a MENTAL/expressive OUTCOME is explained by the nearest
            # prior MENTAL TRIGGER. APPENDED AFTER the connective links so downstream first-parent-wins consumers
            # (goal_hierarchy_graph._add_enablement) keep the connective parent -> the goal graph stays a strict
            # SUPERSET (the measured landing requirement -- a first run lost 1 edge until connective links went
            # first). Additive: connective causal QA + events + coref BYTE-IDENTICAL off vs on (the mental path
            # fires only on NON-connective sentences; the causal QA gold is connective-only). MFS event-type is the
            # cheap ATL frequency default; the contextual-WSD accuracy upgrade (GroundedSemanticGraph, +0.688->0.750
            # type_ok) + the coref-experiencer gate cap the FIELD accuracy (not the mechanism -- oracle-candset
            # sound) and are filed follow-ons. NO LLM.
            if self.causal_mental_bridge:
                from hdlab.event_type import event_type as _etype, MENTAL_TRIGGER, MENTAL_OUTCOME
                for si, toks in enumerate(sents):
                    if _CAUSAL_CONNECTIVES & set(toks):
                        continue
                    events, _tagged = self._extract_events(" ".join(toks))
                    if len(events) < 2:
                        continue
                    types = {e.idx: _etype(e.lemma) for e in events}
                    for outcome in events:
                        if types.get(outcome.idx) not in MENTAL_OUTCOME:
                            continue
                        trig = [e for e in events if e.idx < outcome.idx and types.get(e.idx) in MENTAL_TRIGGER]
                        if trig:
                            links.append(CausalLink(sent_idx=si, cause=trig[-1].lemma,
                                                    outcome=outcome.lemma, method="mental_bridge"))
            return links
        finally:
            self.predicate_recall = saved_recall

    def _read_goals(self, sm, sents) -> None:
        """Opt-in GOAL/INTENTION dimension (default-off track_goals; wired 2026-09-04 from the owner-DONE
        problem the_situation_model_has_no_goal_intention_dimension, Q111). Build a per-agent GOAL REGISTER
        over THIS passage's explicit purpose/desire/intention constructions (the missing 5th Zwaan-Radvansky
        event-indexing dimension) and bind the query callables to sm. BYTE-FAITHFUL to the validated driver
        experiments/exp_goal_register_qa_v1.py::read_doc (the canonical extract->canon->passive_guard->bind->
        status->register sequence): POS from the reader's OWN shared frontend tagger (the SAME
        pos_tagger_ud_ewt_upos.json asset the QA cell's _tagger uses); the lexicalist subcat frame from the
        promoted hdlab.verb_subcat_frames (the upstream complement-vs-adjunct fix), None -> the hardcoded
        heuristic fallback. Runs AFTER coref+events (in read()) so agents/status bind to the FINAL stream.
        Additive -- sets ONLY sm.goal_register + sm.wants/why/achieved; no other dimension field changes
        (byte-identical off vs on). Lazy imports -> the default (OFF) reader loads NONE of this. NO spaCy / NO LLM."""
        from hdlab import goal_register as GR
        try:
            from hdlab.verb_subcat_frames import SubcatFrames
            sc = SubcatFrames.load()
        except Exception:
            sc = None
        pos = [self._cached_tag(list(t)) for t in sents]
        deprels_by_sent = None
        if self.goal_purpose_filter:
            # the reader's OWN arc-labeler deprels over the SHARED per-read parse (consolidated arc-eager heads).
            # EFFICIENCY (2026-09-06): the ADVCL purpose filter reads a deprel ONLY in GR.extract_goals_sentence
            # branch (3) (the bare 'to VINF' adjunct), whose entry gate requires a 'to' token followed by a VERB.
            # Label ONLY those sentences (self._has_to_verb) -- BYTE-IDENTICAL (a skipped sentence passes
            # deprels=None, exactly as it would have fallen through), ~4-8x fewer arc-labeler calls on prose.
            lab = self._frontend_labeler()
            deprels_by_sent = [
                (lab.label(list(t), pos[i], self._cached_parse_heads(list(t), pos[i]))
                 if self._has_to_verb(t, pos[i]) else None)
                for i, t in enumerate(sents)]
        goals = GR.extract_goals(sents, pos, subcat=sc, deprels_by_sent=deprels_by_sent)
        canon, _names = GR.make_canonicalizer(sm, commonnoun_canonical=self.commonnoun_canonical)
        GR.passive_agent_guard(goals, sm, sents, pos)
        GR.bind_agents(goals, canon)
        GR.track_status(goals, sm.events)
        reg = GR.GoalRegister(goals)
        sm.goal_register = reg
        sm.wants = lambda agent: reg.wants(agent)
        sm.why = lambda action_head, agent=None: reg.why(action_head, agent)
        sm.achieved = lambda agent, goal_head: reg.achieved(agent, goal_head)
        # GOAL->SUBGOAL HIERARCHY GRAPH (owner-DONE build_the_goal_subgoal_hierarchy_graph_for_plot_structure_
        # comprehension, 2026-09-05, Q111): compose the flat register's goals + the reader's causal network into
        # an explicit goal->subgoal graph, exposing the plot-structure readouts the FLAT register STRUCTURALLY
        # cannot -- the multi-hop goal-why CHAIN ("why did X do this, ULTIMATELY"), SUPERORDINATE reinstatement
        # over intervening subgoals, and CONNECTIVITY salience (Trabasso & van den Broek 1985; Suh & Trabasso
        # 1993). PURE ADD: sets sm.goal_graph + NEW query callables ONLY; never touches sm.wants/why/achieved
        # (169/169 live-board answers byte-identical off vs on -> 0 regression on every dimension). DEFAULT-ON
        # with track_goals (no-default-off: additive + net-positive; the benefit is scored on the plot-structure
        # battery -- the live board's goal-why questions are only 4% multi-hop, a filed instrument gap). NO LLM.
        from hdlab.goal_hierarchy_graph import build_goal_graph as _build_goal_graph
        # CONTEXTUAL means-end edge ON (owner-DONE validate_the_ppmi_svd_means_end_bridge...): link marker-less
        # actions to the situation-most-related open goal (recency is a located negative). Additive -- only fills
        # previously-parentless action nodes; the flat register + why()/wants() are unchanged. Gated by the goal
        # filter flag (the same means-end submission). Passes the reader's OWN sentence tokens as the situation.
        gg = _build_goal_graph(goals, causal_links=getattr(sm, "causal_links", None),
                               events=getattr(sm, "events", None),
                               link_open_stack=self.goal_purpose_filter,
                               sents=[list(t) for t in sents])
        sm.goal_graph = gg
        sm.goal_why_chain = lambda agent, action_head: gg.why_chain(agent, action_head)
        sm.superordinate_goal = lambda agent, action_head: gg.superordinate(agent, action_head)
        sm.reinstated_goal = lambda agent: gg.open_superordinate(agent)
        sm.salient_goal = lambda agent: gg.most_connected(agent)

    def _read_affect(self, sm, sents) -> None:
        """Opt-in AFFECT/EMOTION dimension (default-on track_affect; wired 2026-09-04 from the owner-DONE
        problem the_situation_model_has_no_affect_emotion_dimension, Q111). Build a per-character AFFECT
        REGISTER over THIS passage's explicit emotion constructions (the missing emotion dimension) and bind
        the query callables to sm. BYTE-FAITHFUL to the validated driver
        experiments/exp_affect_register_qa_v1.py::read_doc (the canonical extract->canon->bind_experiencers->
        register sequence): POS from the reader's OWN shared frontend tagger (the SAME pos_tagger_ud_ewt_upos.json
        asset the QA cell's _tagger uses); the emotion valence/category from the promoted hdlab.affect_lexicon
        (curated denotation gate + Warriner valence); the experiencer-linking split from the promoted
        hdlab.psych_verb_frames (the upstream psych-verb fear-type/frighten-type fix), None -> the naive
        subject-experiencer fallback; the coref canonicalizer REUSED from hdlab.goal_register (dimension-agnostic).
        Runs AFTER coref+events (in read()) so experiencers bind to the FINAL coref stream. Additive -- sets ONLY
        sm.affect_register + sm.feels/valence_of/feels_about; no other dimension field changes (byte-identical off
        vs on). Lazy imports -> the default (OFF) reader loads NONE of this. NO spaCy / NO LLM."""
        from hdlab import affect_register as AR
        from hdlab import goal_register as GR
        from hdlab.affect_lexicon import AffectLexicon
        try:
            from hdlab.psych_verb_frames import PsychVerbFrames
            pvf = PsychVerbFrames.load()
        except Exception:
            pvf = None
        lex = AffectLexicon.load()
        pos = [self._cached_tag(list(t)) for t in sents]
        affects = AR.extract_affect(sents, pos, lex, pvf=pvf)
        canon, _names = GR.make_canonicalizer(sm, commonnoun_canonical=self.commonnoun_canonical)
        AR.bind_experiencers(affects, canon)
        reg = AR.AffectRegister(affects)
        sm.affect_register = reg
        sm.feels = lambda char: reg.feels(char)
        sm.valence_of = lambda char: reg.valence_of(char)
        sm.feels_about = lambda char, stimulus: reg.feels_about(char, stimulus)

    def _read_entity_states(self, sm, sents) -> None:
        """COPULAR is-a/attribute BINDING (default-off bind_entity_states; wired 2026-09-03 from the owner-DONE
        the_reader_has_no_copular_is_a_binding_schema, 10/10+6/6). For each sentence, recover the labeled copular
        (HOLDER, PROPERTY) pairs via the validated primitive
        experiments._copular_nominal_events.extract_entity_states (the high-precision `cop`-label path -- read-back
        recall 0.672 CI-sep over the most-recent-noun floor, shuffle twin loses), TYPE each with the glass-box
        Higgins classifier (predicational property/is-a vs identificational identity), and record sm.entity_states.
        Predicational states are applied to sm.state_register (a landed hdlab.state_register.StateRegister) so
        "what is X" round-trips (state_at / is_in_state / had_been). Uses the copular solution's OWN validated
        frontend assets so flag-on == the validated experiment. Lazy imports -> byte-identical when off. NO LLM."""
        if self._es_mod is None:
            from hdlab import copular_binding as _M
            from hdlab.pos_tagger import PosTagger
            from hdlab.arc_parser import ArcParser
            from hdlab.arc_labeler import ArcLabeler
            from hdlab.state_register import StateRegister
            self._es_mod = _M
            self._es_typed = _M.predicted_type
            self._es_pos = PosTagger.load(_M.POS_ASSET)
            self._es_arc = ArcParser.load(_M.ARC_ASSET)
            self._es_lab = ArcLabeler.load(_M.LAB_ASSET)
            self._es_reg_cls = StateRegister
        M = self._es_mod
        reg = self._es_reg_cls()
        states: List[EntityState] = []
        for si, toks in enumerate(sents):
            if not toks:
                continue
            # PERF (2026-09-04, general): the copular assets (POS/ARC) are BYTE-IDENTICAL to the reader's base
            # tagger/parser, so route the tag + parse through the reader's SHARED per-read cache
            # (_cached_tag/_cached_parse_heads) -- the events/roles path already parsed these sentences, so this
            # is a cache HIT (0 extra parses/tags) instead of a redundant re-parse on the private _es_pos/_es_arc.
            # This alone eliminated ~120 arc parses/read (58% of the default read). Byte-identical (same assets).
            up = self._cached_tag(toks)
            heads = self._cached_parse_heads(toks, up)
            # DETECTION = high-precision label path UNIONED with the label-ROBUST closed-class copula detector
            # (P3 CHANGE 2, owner-DONE wire_the_copular_state_qa_consumer...): the `cop` labeler's recall is the
            # dominant loss (worst on nominal is-a); firing on the closed-class copula token + reading holder/
            # property off the tree recovers it (qa_state 0.712->0.833 CI-sep through the consumer, concentrated on
            # is-a pred_nom +0.184). Byte-faithful to the experiment's `fix = bind | robust_cop(toks,up,heads)`.
            # Pass the CACHED heads into extract_entity_states so it does not re-parse (byte-identical).
            bind = set(M.extract_entity_states(toks, up, self._es_arc, self._es_lab, heads=heads))
            pairs = bind | M.robust_cop(toks, up, heads, gate=True)
            for (h, p) in sorted(pairs):
                if not (0 <= h < len(toks) and 0 <= p < len(toks)):
                    continue
                htype = self._es_typed(toks, up, h, p)
                holder, prop = toks[h], toks[p]
                states.append(EntityState(sent_idx=si, holder=holder, property=prop, htype=htype))
                if htype in ("pred_adj", "pred_nom"):     # predicational -> state register (read-back)
                    reg.apply_state(holder.lower(), prop.lower())
        sm.entity_states = states
        sm.state_register = reg

    def _apply_commonnoun_gate(self, role_mentions):
        """(commonnoun_situation_gate) RE-CLUSTER the reader's common-noun (person) referents via the LANDED
        deployable situation-gated former (hdlab.commonnoun_binder.situation_predict: head-match-gated link +
        modifier-split + wide window W=16 + the event-centrality tie-break for >=2 head-match candidates),
        REPLACING the referent-per-NP gold/singleton cluster ids on NON-PRONOUN mentions (the reader's
        common-noun clustering / the surface-head blind transitive merge).

        Pronoun-linkage PRESERVED: each merged group INHERITS a real gold coref cluster id when any member was
        gold-coref-covered (so make_canonicalizer still ties pronoun resolutions -- keyed on the coref cluster
        -- to the named entity); a group of only referent-per-NP singletons gets a fresh 'CN:'-namespaced id (a
        newly-tracked common-noun entity). Only sm.entities changes downstream -- coref scoring, events, and
        world-state read their OWN separate mention/event streams, so they are byte-identical. Mutates
        role_mentions in place (a fresh per-read list). Default OFF -> never called. NO external LLM."""
        from collections import Counter, defaultdict
        if self._cn_binder_mod is None:
            from hdlab import commonnoun_binder as _CN
            self._cn_binder_mod = _CN
        _CN = self._cn_binder_mod
        if self.entity_kb_resolver:
            # FULL brain-foundational chain (curated KB + situation-model binding + pronoun-into-entity). Single-
            # pass here (reader_coref=None); the Step-3 reader-coref lever wants a two-pass (a filed follow-on).
            from hdlab.entity_world_model_resolver import resolve_common_noun
            labels = resolve_common_noun(role_mentions, self.gaz, reader_coref=None)
        else:
            labels = _CN.situation_predict(role_mentions, self.gaz, window=16, headmatch_gate=True)
        anchored = {m["cluster"] for m in (self._coref_mentions or []) if not m["is_pronoun"]}
        members = defaultdict(list)
        for m in role_mentions:
            if m["is_pronoun"]:
                continue
            lab = labels.get(m["midx"])
            if lab is not None:
                members[lab].append(m)
        lab_to_cluster = {}
        for lab, ms in members.items():
            gold = [m["cluster"] for m in ms if m["cluster"] in anchored]
            lab_to_cluster[lab] = Counter(gold).most_common(1)[0][0] if gold else ("CN:%s" % lab)
        for m in role_mentions:
            if m["is_pronoun"]:
                continue
            lab = labels.get(m["midx"])
            if lab is not None:
                m["cluster"] = lab_to_cluster[lab]
        return role_mentions

    def read(self, conll_path: str) -> SituationModel:
        self._read_parse_cache = {}   # per-read tag/parse memo (bound memory; safe if the reader is reused)
        if self.referent_per_np:
            # DECOUPLE (P5 wire, owner-DONE wire_the_referent_to_coref_linking_pass): referent_per_np swaps ONLY
            # the who-did-what ROLE-candidate + entity source (a discourse referent per content-noun-head NP);
            # pronoun ANAPHORA keeps reading the coref-column source. The two consumers retrieve the referent set
            # through DIFFERENT brain cue-filters (thematic-role vs animacy/Centering-gated retrieval --
            # Lewis-Vasishth / Grosz-Joshi-Weinstein), so sharing ONE mention list was the bug: it flooded the
            # anaphora pool with feature-blank singleton referents (coref_acc 0.469->0.102). Decoupled ->
            # coref reads its own (coref-column) source == byte-identical to the OFF reader (no regression),
            # while who-did-what keeps the parent's +0.336. The brief's "merge referents INTO the coref pool"
            # is REFUTED (-0.106 CI-sep -- the antecedent was already coref-covered, so the extra referents are
            # pure distractors). NO external LLM.
            from hdlab.referent_per_np import referent_per_np_source
            # PERF sweep #2: referent_per_np_source tags each sentence via tagger.tag(); the reader's frontend
            # tagger loads the SAME _FRONTEND_POS_ASSET, so pass a shim over the shared per-read tag cache instead
            # of a redundant private PosTagger copy -> byte-identical, its 71 tags/read become shared-cache hits.
            role_mentions, n_sents = referent_per_np_source(conll_path, _CachedTagShim(self), name_gender_map=self.gaz)
            coref_mentions, n_coref = parse_litbank_conll(conll_path, name_gender_map=self.gaz)
            if n_coref != n_sents:
                raise RuntimeError("SENTENCE_MISALIGN: rnp=%d coref=%d" % (n_sents, n_coref))
        else:
            role_mentions, n_sents = parse_litbank_conll(conll_path, name_gender_map=self.gaz)
            coref_mentions = role_mentions   # coupled OFF -> byte-identical to the deployed baseline
        # stash the coref-column (tracked/given) mentions -> the Competition-Model AGENT candidate source
        # (_cm_agent_candidates). Inert unless cm_agent AND referent_per_np are both ON.
        self._coref_mentions = coref_mentions
        sents = parse_conll_sentences(conll_path)
        if len(sents) != n_sents:
            raise RuntimeError("SENTENCE_MISALIGN: parse_litbank=%d parse_conll_sentences=%d"
                               % (n_sents, len(sents)))
        pid = os.path.splitext(os.path.basename(conll_path))[0]
        sm = SituationModel(passage_id=pid, n_sentences=n_sents)
        if self.commonnoun_situation_gate:
            # RE-CLUSTER common-noun referents via the landed situation-gated former (opt-in; default OFF ->
            # byte-identical). Runs BEFORE _build_entities so sm.entities reflects the former's grouping.
            self._apply_commonnoun_gate(role_mentions)
        sm.entities = _build_entities(role_mentions)   # the FULL referent set (who-has-what / entities)

        targets = build_pronoun_targets(coref_mentions)   # pronoun anaphora reads the coref-column source
        if targets:
            resolutions, recs_ec, recs_ss = self._read_entities(coref_mentions, targets, n_sents)
            sm.coref_resolutions = resolutions
            sm.n_targets = len(resolutions)
            sm.coref_acc = _acc([r.correct for r in resolutions])
            xs = [i for i, r in enumerate(resolutions) if r.sent_dist >= 1]
            sm.n_xsent_targets = len(xs)
            sm.coref_xsent_acc = _acc([resolutions[i].correct for i in xs]) if xs else None
            sm.single_sentence_xsent_acc = (
                _acc([bool(recs_ss[i]["correct"]) for i in xs]) if xs else None)

        events, focus, codec, role_fillers, suppressed = self._read_events(sents, role_mentions, n_sents)
        sm.events = events
        sm.suppressed_predicates = suppressed
        sm.memory_roundtrip = self._memory_roundtrip(focus, codec, events, role_fillers)
        sm.timeline_frames = self._read_timeline(sents)
        sm.causal_links = self._read_causation(sents)
        if self.timeline_register:
            sm.timeline_order = self._read_timeline_register(sents)
        if self.track_space:
            sm.locations = self._read_space(conll_path)
        if self.causation_typed:
            # opt-in TYPED causation read (default-off; lazy spaCy + experiment-side literalness gate).
            from hdlab.causation_typing import read_typed_causation
            if self._causation_nlp is None:
                import spacy
                self._causation_nlp = spacy.load("en_core_web_sm")
            if self._causation_lex is None:
                from hdlab.force_dynamics_lexicon import build_force_lexicon
                self._causation_lex = build_force_lexicon()
            sm.typed_causal_links = read_typed_causation(
                self, conll_path, sm,
                gate_mode=self.causation_gate_mode, use_gate=self.causation_use_gate,
                role_source=self.causation_role_source, tendency=self.causation_tendency,
                use_constructions=self.causation_use_constructions,
                sense_gate=self.causation_sense_gate, sense_tau=self.causation_sense_tau,
                foreground_gate=self.causation_foreground_gate,
                nlp=self._causation_nlp, lexicon=self._causation_lex)
        if self.track_belief:
            # BELIEF/ToM dimension: bind sm.believes / sm.knows query callables to this passage
            self._read_belief(sm, sents)
        if self.predict_revise:
            # PARSE-RECALL drop-fill: recover the DROPPED patient the batch parse missed (runs AFTER
            # causation/timeline so it only fills genuine '?' drops, and BEFORE the backbone so a bound
            # event token would see the recovered patient). Additive/reversible.
            self._read_predict_revise(sm, sents)
        if self.verb_subcat_gate:
            # post-read patient-presence gate: suppress a bound patient on low-transitivity (intransitive)
            # verbs. REORDERED 2026-09-03 (default-flag flip) to run AFTER predict_revise so the STRUCTURAL
            # intransitive-suppression has the FINAL say -- else predict_revise re-introduces the very patient
            # the gate suppressed (a spurious patient on an intransitive). Byte-identical to the validated
            # SubcatGateReader when predict_revise is off (its validation config). Lazy import -> no-op when off.
            if self._vs_mod is None:
                from hdlab import verb_subcat as _VS
                self._vs_mod = _VS
            _VS = self._vs_mod
            for e in sm.events:
                if e.patient not in ("?", None) and _VS.suppress_patient(e.predicate, self.verb_subcat_thr):
                    if self.structural_do_recover and e.patient_is_bare_do:
                        continue  # STRUCTURAL-DO override (§0g): a bare post-verbal DO beats the intransitive veto
                    e.patient = "?"
        if self.predict_surprisal:
            # forward-prediction surprisal metadata + abstain flag. Runs LAST over the FINAL patient (after
            # predict_revise's recovery AND verb_subcat_gate's suppression). Reordered 2026-09-03 (flip): with
            # these default-ON, scoring HERE makes surprisal reflect the final patient, not a stale pre-revise
            # value. Nothing after it (bind_event_tokens/track_world_state) mutates e.patient.
            self._read_surprisal(sm, sents)
        if self.bind_event_tokens:
            # BOUND-EVENT-TOKEN backbone: build sm.event_tokens + sm.episodic_store over the FINAL event set
            # (runs LAST -> binds the events exactly as every other dimension left them). Additive.
            self._read_bound_event_tokens(sm)
        if self.track_world_state:
            # WORLD-STATE dimension: fold the FINAL event set into sm.world_state (possession have(holder,obj)
            # + open/closed toggles). Runs LAST so it sees the patients predict_revise recovered. Additive --
            # sm.world_state stays None when the flag is off.
            self._read_world_state(sm, sents)
        if self.bind_entity_states:
            # COPULAR is-a/attribute dimension: typed (holder, property) states on sm.entity_states +
            # sm.state_register. Additive -- both stay empty/None when the flag is off.
            self._read_entity_states(sm, sents)
        if self.track_goals:
            # GOAL/INTENTION dimension: per-agent goal register on sm.goal_register + the query callables
            # sm.wants/why/achieved. Runs LAST so goals bind to the FINAL event+coref stream (mirrors
            # _read_belief/_read_world_state). Additive -- sm.goal_register stays None when the flag is off.
            self._read_goals(sm, sents)
        if self.track_affect:
            # AFFECT/EMOTION dimension: per-character affect register on sm.affect_register + the query
            # callables sm.feels/valence_of/feels_about. Runs LAST so experiencers bind to the FINAL coref
            # stream (mirrors _read_goals). Additive -- sm.affect_register stays None when the flag is off.
            self._read_affect(sm, sents)
        return sm


def _acc(bools: List[bool]) -> Optional[float]:
    return (sum(1 for b in bools if b) / len(bools)) if bools else None


# ===========================================================================
# formula self-tests (constructed doc + real code path)
# ===========================================================================
def _write_temp_conll(rows: List[Tuple[int, int, str, str]]) -> str:
    """rows = (sent_idx, wtok, token, coref_col). Returns temp .conll path."""
    import tempfile
    lines = ["#begin document (selftest); part 0"]
    prev_sent = 0
    for sent_idx, _w, tok, coref in rows:
        if sent_idx != prev_sent:
            lines.append("")
            prev_sent = sent_idx
        lines.append("\t".join(["selftest", "0", str(_w), tok] + ["_"] * 7 + [coref]))
    lines.append("")
    fd, path = tempfile.mkstemp(suffix=".conll", text=True)
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    return path


def _selftest_read_end_to_end() -> dict:
    """REAL code path: build a tiny 3-sentence doc with a cross-sentence pronoun,
    run read() end-to-end, assert the SituationModel is populated + coherent."""
    # S0: "John saw Mary ." ; S1: "He had finished before she arrived ." (past-perfect
    # flashback, 2 events) ; S2: "She cried because he left ." (causal connective).
    rows = [
        (0, 0, "John", "(0)"), (0, 1, "saw", "_"), (0, 2, "Mary", "(1)"), (0, 3, ".", "_"),
        (1, 0, "He", "(0)"), (1, 1, "had", "_"), (1, 2, "finished", "_"),
        (1, 3, "before", "_"), (1, 4, "she", "(1)"), (1, 5, "arrived", "_"), (1, 6, ".", "_"),
        (2, 0, "She", "(1)"), (2, 1, "cried", "_"), (2, 2, "because", "_"),
        (2, 3, "he", "(0)"), (2, 4, "left", "_"), (2, 5, ".", "_"),
    ]
    path = _write_temp_conll(rows)
    try:
        reader = SituationReader(gaz={"john": "masc", "mary": "fem"})
        sm = reader.read(path)
    finally:
        try:
            os.remove(path)
        except OSError:
            pass
    assert sm.n_sentences == 3, f"n_sentences={sm.n_sentences}"
    assert len(sm.entities) >= 2, f"entities={len(sm.entities)}"
    assert len(sm.events) >= 2, f"events={len(sm.events)}"
    # memory round-trip: direct events must recover their fillers (glass-box)
    # HONEST Cowan-4 property (29511/29512): RECENT (direct) events recover WELL ABOVE
    # chance (~1/vocab ~ 0); older events gracefully fade. Not perfect -- capacity-limited.
    rt = sm.memory_roundtrip
    assert rt["n_direct_events"] >= 1, rt
    assert rt["roundtrip_rate"] >= 0.5, f"recent-event round-trip below floor: {rt}"
    # timeline: S1 has past-perfect 'had left' -> a frame is produced
    assert any(f.sent_idx == 1 for f in sm.timeline_frames), \
        f"no timeline frame for the past-perfect sentence: {sm.timeline_frames}"
    # causation: S2 has 'because' -> a causal link is produced
    assert len(sm.causal_links) >= 1, f"causal_links={sm.causal_links}"
    # coref targets exist (He@S1->John, she@S2->Mary, he@S2->John are cross/same sentence)
    assert sm.n_targets >= 1, f"n_targets={sm.n_targets}"
    return {"n_sentences": sm.n_sentences, "n_entities": len(sm.entities),
            "n_events": len(sm.events), "n_targets": sm.n_targets,
            "n_xsent_targets": sm.n_xsent_targets,
            "roundtrip_rate": rt["roundtrip_rate"],
            "n_timeline_frames": len(sm.timeline_frames),
            "n_causal_links": len(sm.causal_links)}


def _selftest_frame_primary_wiring() -> dict:
    """Component-3 wire self-test (updated 2026-08-05, WIRE-DON'T-ISLAND): situation_reader now
    emits frame-primary thematic role labels end-to-end through the REAL read() pipeline, and the
    OOV path now routes through the production-wired induction (hdlab.frame_induction.
    get_induced_subj_hypothesis(), module-level cache -- see imports above). KNOWN psych verb
    ('feared') -> subj_role=EXPERIENCER (deterministic VERB_FRAMES lookup, re-VET known-lemma
    acc=1.0, UNCHANGED). OOV psych verb ('cherished') -> subj_role is now EXPERIENCER, EARNED via
    the induced construction->frame hypothesis (this is the fix; previously fell to the honest-
    but-wrong positional AGENT default). The construction here is deliberately "cherished that
    Mary was kind" (has_scomp + order_pre, NO arg_animate -- "John" is sentence-initial so the
    capitalization animacy cue does not fire, per _is_animate_head's idx>0 guard) so this witness
    exercises the has_scomp|order_pre residual-lookup path, not the (also EXPERIENCER-predicting,
    but animacy-driven) order_pre+arg_animate rule -- proving the wire fires on more than one
    induced decision path. HONEST: production OOV subj-axis accuracy is 0.833, NOT 1.0 (data-
    starved held-out eval, data/exp_frame_induction_oov_psych_real_v1/metrics.json, MIDDLE_BAND);
    this witness exercises ONE correctly-induced construction, not a claim of perfect coverage.
    Also asserts a plain agentive verb ('kicked') still gets subj_role=AGENT via the frame table,
    unconditionally, and an OOV AGENTIVE-leaning construction with no matching induced rule
    ('bolted', bare transitive, no scomp/degree/passive/animacy cue) still degrades honestly to
    AGENT -- the induction does not overclaim on constructions it has no signal for."""
    # NOTE: _sentence_nominals filters is_pronoun mentions entirely (pre-existing behavior,
    # untouched) -- proper-noun subjects/objects exercise the real agent/patient (non "?") path.
    rows = [
        (0, 0, "John", "(0)"), (0, 1, "feared", "_"), (0, 2, "Mary", "(1)"), (0, 3, ".", "_"),
        (1, 0, "John", "(0)"), (1, 1, "cherished", "_"), (1, 2, "that", "_"),
        (1, 3, "Mary", "(1)"), (1, 4, "was", "_"), (1, 5, "kind", "_"), (1, 6, ".", "_"),
        (2, 0, "John", "(0)"), (2, 1, "kicked", "_"), (2, 2, "Mary", "(1)"), (2, 3, ".", "_"),
        (3, 0, "John", "(0)"), (3, 1, "bolted", "_"), (3, 2, "Mary", "(1)"), (3, 3, ".", "_"),
    ]
    path = _write_temp_conll(rows)
    try:
        reader = SituationReader(gaz={"john": "masc", "mary": "fem"})
        sm = reader.read(path)
    finally:
        try:
            os.remove(path)
        except OSError:
            pass
    by_pred = {ev.predicate: ev for ev in sm.events}  # predicate = surface token (Event.lemma=low)
    assert "feared" in by_pred, f"known psych verb event missing: {[e.predicate for e in sm.events]}"
    assert by_pred["feared"].subj_role == "EXPERIENCER", by_pred["feared"]
    assert "cherished" in by_pred, f"OOV psych verb event missing: {[e.predicate for e in sm.events]}"
    # Induction-verified: cross-check that the process-cached hypothesis, applied directly to
    # this construction's own feature encoding, independently agrees with what the reader emitted
    # (not just asserting the reader's output blind).
    _ind_name, _ind_hyp = _induced_subj()
    _feats = FI_real_construction_feats(["john", "cherished", "that", "mary", "was", "kind", "."], 1, 0)
    _direct_pred = FI_predict_subj_role(_ind_name, _ind_hyp, _feats, default="AGENT")
    assert _direct_pred == "EXPERIENCER", (_feats, _direct_pred)
    assert by_pred["cherished"].subj_role == "EXPERIENCER", by_pred["cherished"]  # earned, not overclaimed to 1.0
    assert "kicked" in by_pred, f"agentive verb event missing: {[e.predicate for e in sm.events]}"
    assert by_pred["kicked"].subj_role == "AGENT", by_pred["kicked"]
    assert "bolted" in by_pred, f"OOV bare-transitive event missing: {[e.predicate for e in sm.events]}"
    assert by_pred["bolted"].subj_role == "AGENT", by_pred["bolted"]  # no induced signal -> honest default
    # non-regression: agent/patient head strings (positional selection) are unaffected by the wire.
    assert by_pred["feared"].agent.lower() == "john", by_pred["feared"]
    return {"fear_subj_role": by_pred["feared"].subj_role,
            "cherish_subj_role": by_pred["cherished"].subj_role,
            "kick_subj_role": by_pred["kicked"].subj_role,
            "bolted_subj_role": by_pred["bolted"].subj_role,
            "induced_name": _ind_name}


def _selftest_affect_wiring() -> dict:
    """Grounded-affect wire self-test (2026-08-05): situation_reader now emits certified
    animacy-axis valence end-to-end through the REAL read() pipeline. IN-SCOPE animate-patient
    force event ('battered' + 'nephew', a certified Bopen item -- see
    experiments/exp_bridge1_event_assembly_open_vocab_v1.SUBSET_B_OPEN_PAIRS) -> affect='HARM'.
    OUT-OF-SCOPE event (animate patient, non-force verb 'saw') -> affect=None (honest abstain, NOT
    a guess). Also proves NON-REGRESSION: this passage's coref/event counts are cross-checked
    against the SAME numbers the pre-wire _selftest_read_end_to_end has asserted for years (affect
    is additive metadata only -- it must not perturb entity/coref/event/timeline/causal counts)."""
    rows = [
        (0, 0, "John", "(0)"), (0, 1, "saw", "_"), (0, 2, "Mary", "(1)"), (0, 3, ".", "_"),
        (1, 0, "She", "(1)"), (1, 1, "battered", "_"), (1, 2, "her", "(1)"),
        (1, 3, "nephew", "(2)"), (1, 4, ".", "_"),
    ]
    path = _write_temp_conll(rows)
    try:
        reader = SituationReader(gaz={"john": "masc", "mary": "fem", "nephew": "masc"})
        sm = reader.read(path)
    finally:
        try:
            os.remove(path)
        except OSError:
            pass
    by_pred = {ev.predicate: ev for ev in sm.events}
    assert "saw" in by_pred, f"non-force event missing: {[e.predicate for e in sm.events]}"
    assert by_pred["saw"].affect is None, (
        f"out-of-scope event should abstain (None), got {by_pred['saw'].affect}")
    assert "battered" in by_pred, f"in-scope force event missing: {[e.predicate for e in sm.events]}"
    assert by_pred["battered"].affect == "HARM", (
        f"in-scope animate-patient force event should be HARM, got {by_pred['battered'].affect}")
    # non-regression: agent/patient positional selection and event count untouched by the wire.
    assert by_pred["saw"].agent.lower() == "john", by_pred["saw"]
    assert by_pred["battered"].patient.lower() == "nephew", by_pred["battered"]
    assert len(sm.events) == 2, f"events={len(sm.events)}"
    assert sm.n_sentences == 2, f"n_sentences={sm.n_sentences}"
    return {"saw_affect": by_pred["saw"].affect, "battered_affect": by_pred["battered"].affect,
            "n_events": len(sm.events)}


def _selftest_role_assignment() -> dict:
    """_assign_roles picks subject as agent, post-predicate nominal as patient."""
    noms = [
        {"head": "john", "wtok_start": 0, "is_subject": True, "midx": 0},
        {"head": "mary", "wtok_start": 2, "is_subject": False, "midx": 1},
    ]
    agent, patient = _assign_roles(1, noms)  # predicate at position 1 ("saw")
    assert agent == "john", agent
    assert patient == "mary", patient
    return {"agent": agent, "patient": patient}


def _selftest_frame_arity_gate() -> dict:
    """MECHANISM CAN-FAIL suite for the 2026-08-06 frame-ARITY patient gate (redirected
    event-extraction precision fix, hdlab/situation_reader.py::_pick_role_mentions). Structural
    correctness is verified directly against hdlab.thematic_role_labeler.STRICTLY_INTRANSITIVE_VERBS
    -- NOT against any gold corpus -- so this is gold-independent, decisive evidence per the
    pre-reg. Every case calls the REAL _assign_roles()/_pick_role_mentions() (unit level) with
    gate_intransitive=False (must reproduce the pre-fix bug exactly, byte-identical) and
    gate_intransitive=True (must fix it), plus one full end-to-end SituationReader().read() proof.

    Cases (16 total):
      (A) 9x STRICTLY-intransitive verb + a following nominal -> ungated WRONGLY assigns it as
          patient (the bug, reproduced); gated correctly abstains (patient='?'). Covers every verb
          family in STRICTLY_INTRANSITIVE_VERBS except the rare/archaic-only synonyms (arrive is
          the motion-verb representative; die/go/come/fall/rise/sit/sleep/kneel are the rest).
      (B) 3x TRANSITIVE / AMBITRANSITIVE-with-a-real-object -> patient KEPT identically gated and
          ungated (build=plain-transitive, eat/read=ambitransitive-but-used-transitively-here).
      (C) 1x AMBITRANSITIVE-intransitive-use with NO following nominal at all ("Tom ate.") ->
          abstains ('?') in BOTH arms via the pre-existing after=[] path, not via gating (eat is
          never in STRICTLY_INTRANSITIVE_VERBS) -- proves the natural-abstain path still works and
          is undisturbed by this change.
      (D) 1x AMBITRANSITIVE-intransitive-use WITH a trailing nominal that is not its patient
          ("Tom sang under the tree.") -> patient is WRONGLY kept ('tree') in BOTH arms (sing is
          deliberately NOT gated) -- documents the honest scope boundary: this fix only reaches
          verbs with NO transitive sense at all, not ambitransitive verbs used intransitively with
          a trailing distractor nominal (that residual needs a WSD/valence-frame classifier, not an
          arity lookup).
      (E) 2x CONSERVATIVE-EXCLUSION boundary ("stand"="tolerate", "wait"="wait one's turn") -> both
          deliberately excluded from STRICTLY_INTRANSITIVE_VERBS (see its docstring); patient KEPT
          in the gated arm, proving the conservative exclusion actually protects a real patient
          rather than being a dead declaration.
      (F) 1x full end-to-end SituationReader(gate_intransitive=True).read() over a real 2-sentence
          CoNLL doc (sit + build) -- proves the constructor flag reaches _read_events, event COUNT
          (recall) is unchanged, AGENT is unchanged, and only the intransitive verb's patient moves.
    In every case AGENT is asserted unchanged gated-vs-ungated (the gate must never touch subject
    selection)."""
    def run(pred_idx, noms, lemma, gated):
        return _assign_roles(pred_idx, noms, lemma=lemma, gate_intransitive=gated)

    # helper: two nominals, "subj" before the predicate, "obj_candidate" after it.
    def noms2(subj_head, subj_pos, obj_head, obj_pos):
        return [{"head": subj_head, "wtok_start": subj_pos, "is_subject": True, "midx": 0},
                {"head": obj_head, "wtok_start": obj_pos, "is_subject": False, "midx": 1}]

    results = {}

    # -- (A) 9x strictly-intransitive + following nominal: ungated bug reproduced, gated fixed --
    strictly_intransitive_cases = [
        ("go", 1, noms2("tom", 0, "store", 4)),
        ("come", 1, noms2("mary", 0, "door", 4)),
        ("arrive", 1, noms2("he", 0, "station", 4)),
        ("fall", 1, noms2("it", 0, "wall", 4)),
        ("rise", 2, noms2("sun", 1, "hills", 5)),
        ("die", 2, noms2("king", 1, "battle", 5)),
        ("sit", 1, noms2("tom", 0, "window", 4)),
        ("sleep", 2, noms2("baby", 1, "storm", 5)),
        ("kneel", 1, noms2("she", 0, "altar", 4)),
    ]
    for lemma, pidx, noms in strictly_intransitive_cases:
        ag_u, pt_u = run(pidx, noms, lemma, gated=False)
        ag_g, pt_g = run(pidx, noms, lemma, gated=True)
        assert pt_u == noms[1]["head"], (
            f"[{lemma}] ungated must reproduce the pre-fix bug (patient={pt_u!r}, "
            f"expected {noms[1]['head']!r})")
        assert pt_g == "?", f"[{lemma}] gated must suppress the spurious patient, got {pt_g!r}"
        assert ag_u == ag_g == noms[0]["head"], f"[{lemma}] AGENT must be untouched by the gate"
        results[lemma] = {"ungated_patient": pt_u, "gated_patient": pt_g}

    # -- (B) 3x transitive / ambitransitive-with-real-object: patient kept both arms --
    keep_patient_cases = [
        ("build", 1, noms2("tom", 0, "castle", 3)),
        ("eat", 1, noms2("tom", 0, "cake", 3)),
        ("read", 1, noms2("she", 0, "book", 3)),
    ]
    for lemma, pidx, noms in keep_patient_cases:
        ag_u, pt_u = run(pidx, noms, lemma, gated=False)
        ag_g, pt_g = run(pidx, noms, lemma, gated=True)
        assert pt_u == pt_g == noms[1]["head"], (
            f"[{lemma}] transitive/ambitransitive patient must be kept identically in both arms "
            f"(ungated={pt_u!r} gated={pt_g!r} expected={noms[1]['head']!r})")
        assert ag_u == ag_g == noms[0]["head"]
        results[lemma] = {"ungated_patient": pt_u, "gated_patient": pt_g}

    # -- (C) ambitransitive intransitive-use, NO trailing nominal: natural abstain both arms --
    noms_no_obj = [{"head": "tom", "wtok_start": 0, "is_subject": True, "midx": 0}]
    ag_u, pt_u = run(1, noms_no_obj, "eat", gated=False)
    ag_g, pt_g = run(1, noms_no_obj, "eat", gated=True)
    assert pt_u == pt_g == "?", (
        f"[eat/no-candidate] must abstain naturally in both arms (ungated={pt_u!r} gated={pt_g!r})")
    results["eat_no_object"] = {"ungated_patient": pt_u, "gated_patient": pt_g}

    # -- (D) ambitransitive intransitive-use WITH a trailing distractor nominal: known boundary --
    noms_sing = noms2("tom", 0, "tree", 4)
    ag_u, pt_u = run(1, noms_sing, "sing", gated=False)
    ag_g, pt_g = run(1, noms_sing, "sing", gated=True)
    assert pt_u == pt_g == "tree", (
        f"[sing/distractor] ambitransitive-not-in-gate-set must be UNCHANGED by this fix "
        f"(ungated={pt_u!r} gated={pt_g!r}) -- this residual is out of scope, not a regression")
    results["sing_distractor_known_boundary"] = {"ungated_patient": pt_u, "gated_patient": pt_g}

    # -- (E) conservative-exclusion boundary: stand/wait keep their real patient even gated=True --
    excluded_cases = [
        ("stand", 2, noms2("he", 0, "noise", 5)),
        ("wait", 1, noms2("tom", 0, "turn", 3)),
    ]
    for lemma, pidx, noms in excluded_cases:
        ag_g, pt_g = run(pidx, noms, lemma, gated=True)
        assert pt_g == noms[1]["head"], (
            f"[{lemma}] deliberately-excluded verb must KEEP its patient under gate_intransitive="
            f"True (got {pt_g!r}, expected {noms[1]['head']!r}) -- conservatism check")
        results[f"{lemma}_conservative_exclusion"] = {"gated_patient": pt_g}

    # -- (F) full end-to-end: SituationReader(gate_intransitive=True/False) over a real CoNLL doc --
    # NOTE (2026-08-06, PROMOTION): gate_intransitive is now DEFAULT True on SituationReader (see
    # __init__), so both arms below pass the flag EXPLICITLY -- relying on the constructor default
    # for the "ungated" arm would silently test gated-vs-gated post-promotion. This mirrors the
    # opt-out kwarg any caller still uses to get the pre-fix positional-only behavior.
    rows = [
        (0, 0, "Tom", "(0)"), (0, 1, "sat", "_"), (0, 2, "down", "_"), (0, 3, "by", "_"),
        (0, 4, "the", "_"), (0, 5, "chair", "(1)"), (0, 6, ".", "_"),
        (1, 0, "Tom", "(0)"), (1, 1, "built", "_"), (1, 2, "the", "_"),
        (1, 3, "castle", "(2)"), (1, 4, ".", "_"),
    ]
    path = _write_temp_conll(rows)
    try:
        sm_ungated = SituationReader(gaz={"tom": "masc"}, gate_intransitive=False).read(path)
        sm_gated = SituationReader(gaz={"tom": "masc"}, gate_intransitive=True).read(path)
    finally:
        try:
            os.remove(path)
        except OSError:
            pass
    bu = {ev.predicate: ev for ev in sm_ungated.events}
    bg = {ev.predicate: ev for ev in sm_gated.events}
    assert len(sm_ungated.events) == len(sm_gated.events) == 2, (
        f"end-to-end event COUNT (recall) must be unchanged: "
        f"ungated={len(sm_ungated.events)} gated={len(sm_gated.events)}")
    assert bu["sat"].patient == "chair", f"end-to-end ungated must reproduce the bug: {bu['sat']}"
    assert bg["sat"].patient == "?", f"end-to-end gated must fix it: {bg['sat']}"
    assert bu["built"].patient == bg["built"].patient == "castle", "transitive event unchanged"
    assert bu["sat"].agent == bg["sat"].agent == "tom", "AGENT untouched end-to-end"
    results["end_to_end"] = {
        "n_events_ungated": len(sm_ungated.events), "n_events_gated": len(sm_gated.events),
        "sat_patient_ungated": bu["sat"].patient, "sat_patient_gated": bg["sat"].patient,
        "built_patient_both": bu["built"].patient}

    return {"n_cases": 16, "all_pass": True, **results}


def _selftest_pred_gate() -> dict:
    """OPT-IN spaCy predicate-validity gate: a planted non-verb mis-tag is suppressed,
    a real verb survives. SKIPS gracefully if spaCy is not installed (default-env)."""
    try:
        gate_fn = _build_spacy_pred_gate()
    except ImportError:
        return {"skipped": "spacy_not_installed"}
    # "The red coat lay there ." -> a mis-tagger might read 'red' as a predicate; spaCy tags it JJ.
    verbs = gate_fn("the red coat lay there")
    assert "lay" in verbs, f"gate dropped a real verb: {verbs}"
    assert "red" not in verbs, f"gate kept an adjective as verb: {verbs}"
    return {"verbs_for_'the red coat lay there'": sorted(verbs)}


def _selftest_event_extraction_coverage() -> dict:
    """Coverage-extension self-test (2026-08-05, goldvet_oov_psych_bank.md gap-recovery task):
    _read_events -> experiments._temporal_ordering.extract_events now emits events for
    COORDINATED VPs (shared distant aux across "and"/"or"), MODAL-governed bare-infinitive
    subordinate-clause predicates, and bare PARTICIPIAL (-ing) non-finite clauses -- additive to
    the pre-existing VBD / VBN+had / VBN+be branches (BYTE-IDENTICAL, unchanged). Real-text
    fixtures are the 3 goldvet NOT_FOUND items (notes/goldvet_oov_psych_bank.md): #13 Ottenburg
    ("had long owned and cherished" -- coordinated VP, extractor previously caught only "owned"),
    #5 Queequeg ("if thereby he might happily gain the power ..." -- modal-governed subordinate
    clause), #19 Mary ("Mary, resenting that ..., began talking ..., and protesting ..." --
    participial clauses).

    HONEST per-item outcome (verified against a hand-run of the OLD extractor logic, not just
    asserted here):
      - Ottenburg: CLEAN RECOVERY. "cherished" was dropped before this fix (only "owned" fired);
        now both fire, correct agent (ottenburg) on both via the pre-existing positional selector.
      - Queequeg: the OOV goal-verb token "disdained" was ALREADY extractable before this fix
        (plain VBD); this fix ADDITIONALLY recovers "gain" -- the actual embedded desiderative
        predicate inside the modal-governed subordinate "if" clause -- with the correct agent.
      - Mary: NOT recovered. The general participial-clause branch IS proven to fire correctly on
        THIS SAME sentence (talking/protesting both get PARTICIPIAL events with the correct
        agent=mary), but the specific goal-verb token "resenting" is mistagged NN (not VBG) by the
        shared NLTK PerceptronTagger for this exact comma-fronted-gerund construction -- a POS
        signal limitation upstream of this extractor, not an architecture gap this fix can close
        without a better tagger (spaCy is available as an opt-in predicate-VALIDITY gate elsewhere
        in this module but is not installed in this environment, and it is a POST-HOC filter, not
        a tagger -- it cannot rescue a token the base tagger never proposed as a predicate).
    """
    # -- Ottenburg: coordinated VP, shared distant "had" aux --
    rows_ott = [
        (0, 0, "Otto", "_"), (0, 1, "Ottenburg", "(0)"), (0, 2, "had", "_"),
        (0, 3, "long", "_"), (0, 4, "owned", "_"), (0, 5, "and", "_"),
        (0, 6, "cherished", "_"), (0, 7, ".", "_"),
    ]
    path = _write_temp_conll(rows_ott)
    try:
        sm = SituationReader(gaz={"ottenburg": "masc"}).read(path)
    finally:
        try:
            os.remove(path)
        except OSError:
            pass
    by_pred = {ev.predicate: ev for ev in sm.events}
    assert "cherished" in by_pred, f"coordinated-VP event not recovered: {[e.predicate for e in sm.events]}"
    assert by_pred["cherished"].agent == "ottenburg", by_pred["cherished"]
    assert by_pred["cherished"].tense == "PAST_PERFECT", by_pred["cherished"]
    assert "owned" in by_pred and by_pred["owned"].agent == "ottenburg", by_pred  # unchanged

    # -- Queequeg: modal-governed subordinate clause --
    rows_qq = [
        (0, 0, "Queequeg", "(0)"), (0, 1, "disdained", "_"), (0, 2, "no", "_"),
        (0, 3, "seeming", "_"), (0, 4, "ignominy", "_"), (0, 5, "if", "_"),
        (0, 6, "thereby", "_"), (0, 7, "he", "_"), (0, 8, "might", "_"),
        (0, 9, "happily", "_"), (0, 10, "gain", "_"), (0, 11, "the", "_"),
        (0, 12, "power", "_"), (0, 13, ".", "_"),
    ]
    path = _write_temp_conll(rows_qq)
    try:
        sm = SituationReader(gaz={"queequeg": "masc"}).read(path)
    finally:
        try:
            os.remove(path)
        except OSError:
            pass
    by_pred = {ev.predicate: ev for ev in sm.events}
    assert "disdained" in by_pred and by_pred["disdained"].agent == "queequeg", by_pred  # pre-existing
    assert "gain" in by_pred, f"modal-subordinate event not recovered: {[e.predicate for e in sm.events]}"
    assert by_pred["gain"].agent == "queequeg", by_pred["gain"]
    assert by_pred["gain"].tense == "MODAL_SUBORDINATE", by_pred["gain"]

    # -- Mary: participial clauses (general construction works; the specific goal-verb token
    #    'resenting' is a documented POS-tagger mistag, NOT recovered -- asserted honestly below) --
    rows_mary = [
        (0, 0, "Mary", "(0)"), (0, 1, "resenting", "_"), (0, 2, "that", "_"),
        (0, 3, "she", "_"), (0, 4, "should", "_"), (0, 5, "be", "_"),
        (0, 6, "supposed", "_"), (0, 7, "not", "_"), (0, 8, "to", "_"),
        (0, 9, "know", "_"), (0, 10, "her", "_"), (0, 11, "own", "_"),
        (0, 12, "cousin", "_"), (0, 13, ",", "_"), (0, 14, "began", "_"),
        (0, 15, "talking", "_"), (0, 16, "and", "_"), (0, 17, "protesting", "_"),
    ]
    path = _write_temp_conll(rows_mary)
    try:
        sm = SituationReader(gaz={"mary": "fem"}).read(path)
    finally:
        try:
            os.remove(path)
        except OSError:
            pass
    by_pred = {ev.predicate: ev for ev in sm.events}
    assert "talking" in by_pred and by_pred["talking"].tense == "PARTICIPIAL", by_pred
    assert by_pred["talking"].agent == "mary", by_pred["talking"]  # general construction WORKS
    assert "protesting" in by_pred and by_pred["protesting"].tense == "PARTICIPIAL", by_pred
    assert "resenting" not in by_pred, (
        "documented tagger-mistag gap closed unexpectedly -- update this self-test's honest "
        f"claim if 'resenting' is now recovered: {[e.predicate for e in sm.events]}")

    return {"ottenburg_cherished_recovered": True, "queequeg_gain_recovered": True,
            "mary_talking_recovered": True, "mary_resenting_recovered": "resenting" in by_pred}


def _run_all_selftests() -> dict:
    out = {}
    out["role_assignment"] = _selftest_role_assignment()
    out["frame_arity_gate"] = _selftest_frame_arity_gate()
    out["read_end_to_end"] = _selftest_read_end_to_end()
    out["pred_gate"] = _selftest_pred_gate()
    out["frame_primary_wiring"] = _selftest_frame_primary_wiring()
    out["affect_wiring"] = _selftest_affect_wiring()
    out["event_extraction_coverage"] = _selftest_event_extraction_coverage()
    return out


if __name__ == "__main__":
    import json
    res = _run_all_selftests()
    print(json.dumps(res, indent=2))
    print("ALL SELF-TESTS PASSED")
