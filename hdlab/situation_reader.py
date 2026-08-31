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
from hdlab.thematic_role_labeler import lemma_verb, is_strictly_intransitive

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
from hdlab.context_grounded_valence import score_context_grounded_valence, to_ternary

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
_FRONTEND_CACHE: Dict[str, object] = {}


def _load_frontend():
    """Load the persisted UPOS tagger + hashed arc parser ONCE per process (module-cached). Imported
    lazily so a default (positional) reader never pays the parser-asset load or the import cost."""
    if "t" not in _FRONTEND_CACHE:
        from hdlab.pos_tagger import PosTagger
        from hdlab.arc_parser import ArcParser
        _FRONTEND_CACHE["t"] = PosTagger.load(_FRONTEND_POS_ASSET)
        _FRONTEND_CACHE["p"] = ArcParser.load(_FRONTEND_ARC_ASSET)
    return _FRONTEND_CACHE["t"], _FRONTEND_CACHE["p"]

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
class SituationModel:
    passage_id: str
    n_sentences: int
    entities: List[TrackedEntity] = field(default_factory=list)
    events: List[EventRecord] = field(default_factory=list)
    # events dropped by an optional supplied-grammar predicate-validity gate (glass-box demo)
    suppressed_predicates: List["SuppressedPredicate"] = field(default_factory=list)
    coref_resolutions: List[CorefResolution] = field(default_factory=list)
    timeline_frames: List[TimelineFrame] = field(default_factory=list)
    causal_links: List[CausalLink] = field(default_factory=list)
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
    for cid in sorted(by_cluster):
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
    cheap scoring calls."""
    if patient in (None, "?"):
        return None
    try:
        result = score_context_grounded_valence(patient, sentence_text)
    except ValueError:
        return None  # patient head not found by the organ's own tokenizer -- abstain, not guess
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
                 role_route: str = "positional",
                 tense_agnostic_events: bool = False) -> None:
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
        # this recall-max detector assigns a PLACEHOLDER tense (TENSE_SIMPLE_PAST) -- do NOT consume this flag
        # for the TIME/timeline dimension until a tense-preserving variant is validated (queued follow-on).
        self.tense_agnostic_events = bool(tense_agnostic_events)
        self._ta_tagger = None                                 # lazy hdlab.pos_tagger.PosTagger
        # persistent readers (the banked backbone + single-sentence validity baseline)
        self.reader_ec = EventCentralityReader(n_dim=EVENT_N_DIM, mem_seed=MEM_SEED)
        self.reader_ss = CorefReader()

    # -- ENTITIES + COREF (banked EventCentralityReader recency-centrality, 29516) --
    def _read_entities(self, mentions, targets, n_sents):
        sid_fixed = [i // LOCAL_WINDOW for i in range(n_sents)]
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
        if self._ta_tagger is None:
            from hdlab.pos_tagger import PosTagger
            self._ta_tagger = PosTagger.load(_FRONTEND_POS_ASSET)
        toks = text.split()
        up = self._ta_tagger.tag(toks)
        events = []
        for i, tk in enumerate(toks):
            if up[i] == "VERB":
                events.append(T.Event(lemma=tk.lower(), idx=i, pos=up[i],
                                      tense=T.TENSE_SIMPLE_PAST, is_pp=False))
        return events, []

    # -- EVENTS: per-sentence predicate+agent+patient -> Cowan-4 bundle focus --
    def _read_events(self, sents, mentions, n_sents):
        if self.role_route != "positional":
            return self._read_events_wired(sents, mentions, n_sents)   # ASSEMBLY opt-in; else byte-identical
        codec = EventBundleCodec(n_dim=self.focus_n_dim, roles=DEFAULT_ROLES, seed=FOCUS_SEED)
        focus = ChunkedFocus(codec, capacity=4, fanout=2, seed=FOCUS_SEED)
        sent_noms = _sentence_nominals(mentions, n_sents)
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
                                          subj_role=subj_role, obj_role=obj_role, affect=affect))
                role_fillers.append(rf)
                gidx += 1
        return events, focus, codec, role_fillers, suppressed

    # -- ASSEMBLY reader-role-routing (opt-in; role_route != "positional") -----------------------------
    # A verbatim port of the validated WiredSituationReader (exp_wire_predarg_binder_live_reader_integration
    # _v1): route each event's agent/patient through a real parse -> route_predicate_arguments (+ a
    # reader-native, case-independent quotative-inversion rule) with the positional rule as the good-enough
    # fallback; richer roles (goal/recipient/...) are collected as additive metadata. Everything else
    # (event extraction, encoding, focus, frame/affect metadata) is UNCHANGED from the stock _read_events.
    def _router_roles(self, toks):
        """{verb_pos0: {pa_role: token_pos0}} from parse -> route_predicate_arguments, fed the reader's OWN
        tokens so indices align with mention wtok positions. quotative=False: the reader applies its OWN
        mention-based quotative below (its tokens are lowercased, so the router's capitalization-based
        speaker scan cannot fire here). Empty for empty / very long token lists."""
        if not toks or len(toks) > 120:
            return {}
        pos = self._tagger.tag(toks)
        heads = self._parser.parse(toks, pos).heads
        out = {}
        for v in matrix_verbs(toks, pos, heads):
            roles = route_predicate_arguments(toks, pos, heads, v, quotative=False)
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
        events: List[EventRecord] = []
        role_fillers: List[Dict[str, str]] = []
        suppressed: List[SuppressedPredicate] = []
        self.wired_extra_roles = []
        gidx = 0
        for si, toks in enumerate(sents):
            text = " ".join(toks)
            evs, _tagged = self._extract_events(text)
            noms = sent_noms[si] if si < len(sent_noms) else []
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
                if verb_lows is not None and e.lemma not in verb_lows:
                    suppressed.append(SuppressedPredicate(sent_idx=si, predicate=e.lemma, tense=str(e.tense),
                                                          agent=agent, patient=patient))
                    continue
                rf = {"PRED": e.lemma, "AGENT": agent, "PATIENT": patient, "TENSE": str(e.tense)}
                vec = codec.encode_event(rf); focus.push(vec, gidx)
                subj_role, obj_role = _assign_frame_primary_roles(e.lemma, toks, e.idx, noms,
                                                                  gate_intransitive=self.gate_intransitive)
                affect = _assign_affect(patient, text)
                events.append(EventRecord(global_idx=gidx, sent_idx=si, predicate=e.lemma, agent=agent,
                                          patient=patient, tense=str(e.tense), subj_role=subj_role,
                                          obj_role=obj_role, affect=affect))
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

    # -- CAUSATION: cause->outcome on the passage's causal-connective sentences --
    @staticmethod
    def _read_causation(sents) -> List[CausalLink]:
        links: List[CausalLink] = []
        for si, toks in enumerate(sents):
            if not (_CAUSAL_CONNECTIVES & set(toks)):
                continue
            text = " ".join(toks)
            events, low = C.extract(text)
            if len(events) < 2:
                continue
            # try each event as the outcome-to-explain; record the FIRST genuine
            # connective/bridge cause link (order-agnostic: "X because Y" states the
            # effect first, so the last event is not always the outcome).
            for outcome in events:
                cause_ev, method = C.causal_net_cause(events, low, outcome)
                if cause_ev is None or cause_ev.lemma == outcome.lemma:
                    continue
                if method not in ("connective", "bridge"):
                    continue
                links.append(CausalLink(sent_idx=si, cause=cause_ev.lemma,
                                        outcome=outcome.lemma, method=method))
                break
        return links

    def read(self, conll_path: str) -> SituationModel:
        mentions, n_sents = parse_litbank_conll(conll_path, name_gender_map=self.gaz)
        sents = parse_conll_sentences(conll_path)
        if len(sents) != n_sents:
            raise RuntimeError("SENTENCE_MISALIGN: parse_litbank=%d parse_conll_sentences=%d"
                               % (n_sents, len(sents)))
        pid = os.path.splitext(os.path.basename(conll_path))[0]
        sm = SituationModel(passage_id=pid, n_sentences=n_sents)
        sm.entities = _build_entities(mentions)

        targets = build_pronoun_targets(mentions)
        if targets:
            resolutions, recs_ec, recs_ss = self._read_entities(mentions, targets, n_sents)
            sm.coref_resolutions = resolutions
            sm.n_targets = len(resolutions)
            sm.coref_acc = _acc([r.correct for r in resolutions])
            xs = [i for i, r in enumerate(resolutions) if r.sent_dist >= 1]
            sm.n_xsent_targets = len(xs)
            sm.coref_xsent_acc = _acc([resolutions[i].correct for i in xs]) if xs else None
            sm.single_sentence_xsent_acc = (
                _acc([bool(recs_ss[i]["correct"]) for i in xs]) if xs else None)

        events, focus, codec, role_fillers, suppressed = self._read_events(sents, mentions, n_sents)
        sm.events = events
        sm.suppressed_predicates = suppressed
        sm.memory_roundtrip = self._memory_roundtrip(focus, codec, events, role_fillers)
        sm.timeline_frames = self._read_timeline(sents)
        sm.causal_links = self._read_causation(sents)
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
