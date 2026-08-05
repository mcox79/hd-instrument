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
                     reusing the parse_litbank_conll mention structure). Each event is stored
                     as a Cowan-4 role-slot BUNDLE (hdlab/event_bundle.py EventBundleCodec,
                     29511) -- the validated "2 chunks x 4 slots" role-slot format.
                     HONEST SCOPE: this is a LIGHTWEIGHT structural event extractor for the
                     multi-sentence demonstration; the calibrated single-sentence role reader
                     (predicate+agent+patient, F1~0.64 on McGuffey LCCP gold, 29502) is the
                     component whose ACCURACY is CITED -- NOT re-scored here (no LitBank role
                     gold). Reported honestly per the "roles vs gold where available" rule.
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
from hdlab.frame_induction import frame_primary_role
from hdlab.thematic_role_labeler import lemma_verb

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


def _pick_role_mentions(pred_idx: int, sent_noms: List[dict]) -> Tuple[Optional[dict], Optional[dict]]:
    """Positional mention selection (single source of truth for both head-strings and, since
    2026-08-05, frame-primary role labeling): subj-mention = the subject-mention (rank 0) if
    before/at the predicate else nearest preceding nominal; obj-mention = nearest nominal
    strictly after the predicate. Returns (subj_mention_dict_or_None, obj_mention_dict_or_None)."""
    before = [m for m in sent_noms if m["wtok_start"] <= pred_idx]
    after = [m for m in sent_noms if m["wtok_start"] > pred_idx]
    subj_m: Optional[dict] = None
    if before:
        subj = [m for m in before if m.get("is_subject")]
        subj_m = subj[0] if subj else before[-1]
    obj_m = after[0] if after else None
    return subj_m, obj_m


def _assign_roles(pred_idx: int, sent_noms: List[dict]) -> Tuple[str, str]:
    """Glass-box structural role assignment against the sentence's gold mention heads:
    AGENT = the subject-mention (rank 0) if before/at the predicate else nearest preceding
    nominal; PATIENT = nearest nominal strictly after the predicate. '?' when none.
    UNCHANGED behavior (2026-08-05): now backed by _pick_role_mentions, byte-identical output."""
    subj_m, obj_m = _pick_role_mentions(pred_idx, sent_noms)
    agent = subj_m["head"] if subj_m is not None else "?"
    patient = obj_m["head"] if obj_m is not None else "?"
    return agent, patient


def _assign_frame_primary_roles(lemma: str, toks: List[str], pred_idx: int,
                                sent_noms: List[dict]) -> Tuple[Optional[str], Optional[str]]:
    """Component-3 wire (2026-08-05): frame-primary THEMATIC role labels for the SAME heads
    _assign_roles picks (via the shared _pick_role_mentions selector) -- additive, does not change
    which head is chosen. KNOWN verb (lemma in VERB_FRAMES) -> frame_slot_role() answers
    UNCONDITIONALLY (the re-VET's known-lemma acc=1.0 deterministic-dict path). OOV verb, subj slot,
    NO induced hypothesis wired here (chosen_name/hypothesis left None) -> honest default "AGENT",
    i.e. IDENTICAL to the pre-existing positional-default behavior for OOV subjects -- the
    re-VET-flagged coarse-animacy induced-hypothesis path (OOV earned-acc=0.767) is deliberately
    NOT wired into production labeling (see notes/skunkworks_reVET_frame_primary_role_assigner_v1.md
    revival criteria: object-experiencer unsolved + OOV cue is animacy-only); it is exercised
    separately, offline, by the end-to-end VET script, not by this reader path. This keeps the wire
    conservative: zero regression risk (OOV falls back to the exact prior default), only KNOWN-verb
    psych predicates gain a corrected label.

    `lemma` here is the reader's EVENT lemma, which is actually the LOWERCASED SURFACE token
    (experiments/_temporal_ordering.py Event.lemma=low, e.g. "feared"/"cherished") -- NOT a true
    verb lemma. VERB_FRAMES is keyed by true lemma ("fear"/"cherish"), so it is re-lemmatized via
    the existing glass-box lemma_verb() (irregular table + suffix-strip) before the frame lookup,
    same as every other real-data consumer of frame_primary_role (see
    experiments/exp_frame_primary_role_assigner_v1.py which lemmatizes from record["verb_lemma"]
    supplied by the gold dataset -- here there is no supplied lemma, so lemma_verb() derives it)."""
    true_lemma = lemma_verb(lemma)
    subj_m, obj_m = _pick_role_mentions(pred_idx, sent_noms)
    subj_role = None
    if subj_m is not None:
        subj_role = frame_primary_role(true_lemma, toks, pred_idx, int(subj_m["wtok_start"]), "subj")
    obj_role = None
    if obj_m is not None:
        obj_role = frame_primary_role(true_lemma, toks, pred_idx, int(obj_m["wtok_start"]), "obj")
    return subj_role, obj_role


# ===========================================================================
# the reader
# ===========================================================================
class SituationReader:
    """read(conll_path) -> SituationModel. Composes the banked dimension modules."""

    def __init__(self, *, gaz: Optional[Dict[str, str]] = None,
                 focus_n_dim: int = FOCUS_N_DIM,
                 pred_gate_fn=None, spacy_pred_gate: bool = False) -> None:
        self.gaz = load_name_gender() if gaz is None else gaz
        self.focus_n_dim = int(focus_n_dim)
        # OPTIONAL supplied-grammar predicate-validity gate (29522 L1 win, ADOPTED opt-in).
        # Default OFF -> byte-identical to the banked reader. pred_gate_fn(sentence_text)->set(low).
        if pred_gate_fn is None and spacy_pred_gate:
            pred_gate_fn = _build_spacy_pred_gate()
        self.pred_gate_fn = pred_gate_fn
        # persistent readers (the banked backbone + single-sentence validity baseline)
        self.reader_ec = EventCentralityReader(n_dim=EVENT_N_DIM, mem_seed=MEM_SEED)
        self.reader_ss = CorefReader()

    # -- ENTITIES + COREF (banked EventCentralityReader recency-centrality, 29516) --
    def _read_entities(self, mentions, targets, n_sents):
        sid_fixed = [i // LOCAL_WINDOW for i in range(n_sents)]
        recs_ec = self.reader_ec.resolve_stream(
            mentions, targets, scene_ids=sid_fixed, topical_mode="rolemass",
            query_memory=True, centrality_mode="recency", **SUP_KW)
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

    # -- EVENTS: per-sentence predicate+agent+patient -> Cowan-4 bundle focus --
    def _read_events(self, sents, mentions, n_sents):
        codec = EventBundleCodec(n_dim=self.focus_n_dim, roles=DEFAULT_ROLES, seed=FOCUS_SEED)
        focus = ChunkedFocus(codec, capacity=4, fanout=2, seed=FOCUS_SEED)
        sent_noms = _sentence_nominals(mentions, n_sents)
        events: List[EventRecord] = []
        role_fillers: List[Dict[str, str]] = []
        suppressed: List[SuppressedPredicate] = []
        gidx = 0
        for si, toks in enumerate(sents):
            text = " ".join(toks)
            evs, _tagged = T.extract_events(text)
            noms = sent_noms[si] if si < len(sent_noms) else []
            # supplied-grammar gate: valid predicate LOW tokens for THIS sentence (spaCy VERBs)
            verb_lows = self.pred_gate_fn(text) if self.pred_gate_fn is not None else None
            for e in evs:
                agent, patient = _assign_roles(e.idx, noms)
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
                subj_role, obj_role = _assign_frame_primary_roles(e.lemma, toks, e.idx, noms)
                events.append(EventRecord(global_idx=gidx, sent_idx=si, predicate=e.lemma,
                                          agent=agent, patient=patient, tense=str(e.tense),
                                          subj_role=subj_role, obj_role=obj_role))
                role_fillers.append(rf)
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
    """Component-3 wire self-test (2026-08-05): situation_reader now emits frame-primary
    thematic role labels end-to-end through the REAL read() pipeline. KNOWN psych verb ('feared')
    -> subj_role=EXPERIENCER (deterministic VERB_FRAMES lookup, re-VET known-lemma acc=1.0). OOV
    psych verb ('cherished', no induced hypothesis wired) -> subj_role falls back to the honest
    default 'AGENT' (matches the pre-existing positional default -- no regression, no overclaim of
    the re-VET-flagged coarse-animacy path). Also asserts a plain agentive verb ('kicked') still
    gets subj_role=AGENT via the frame table, unconditionally."""
    # NOTE: _sentence_nominals filters is_pronoun mentions entirely (pre-existing behavior,
    # untouched) -- proper-noun subjects/objects exercise the real agent/patient (non "?") path.
    rows = [
        (0, 0, "John", "(0)"), (0, 1, "feared", "_"), (0, 2, "Mary", "(1)"), (0, 3, ".", "_"),
        (1, 0, "John", "(0)"), (1, 1, "cherished", "_"), (1, 2, "Mary", "(1)"), (1, 3, ".", "_"),
        (2, 0, "John", "(0)"), (2, 1, "kicked", "_"), (2, 2, "Mary", "(1)"), (2, 3, ".", "_"),
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
    assert by_pred["cherished"].subj_role == "AGENT", by_pred["cherished"]  # honest OOV default, not overclaimed
    assert "kicked" in by_pred, f"agentive verb event missing: {[e.predicate for e in sm.events]}"
    assert by_pred["kicked"].subj_role == "AGENT", by_pred["kicked"]
    # non-regression: agent/patient head strings (positional selection) are unaffected by the wire.
    assert by_pred["feared"].agent.lower() == "john", by_pred["feared"]
    return {"fear_subj_role": by_pred["feared"].subj_role,
            "cherish_subj_role": by_pred["cherished"].subj_role,
            "kick_subj_role": by_pred["kicked"].subj_role}


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


def _run_all_selftests() -> dict:
    out = {}
    out["role_assignment"] = _selftest_role_assignment()
    out["read_end_to_end"] = _selftest_read_end_to_end()
    out["pred_gate"] = _selftest_pred_gate()
    out["frame_primary_wiring"] = _selftest_frame_primary_wiring()
    return out


if __name__ == "__main__":
    import json
    res = _run_all_selftests()
    print(json.dumps(res, indent=2))
    print("ALL SELF-TESTS PASSED")
