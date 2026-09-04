"""BRAIN-FOUNDATIONAL AGENT ROLE ASSIGNMENT via the Competition Model -- recover the board's who-did-what
AGENT arm after `referent_per_np` was turned DEFAULT-ON.

PROBLEM (measured first-hand, disk outranks the brief): the reader's who-did-what AGENT is assigned
POSITIONALLY (`situation_reader._pick_role_mentions`: agent = the sentence's `is_subject` mention, which
`referent_per_np._finalize` defines as the LEFTMOST NP head (rank==0), else nearest-preceding nominal). With
the denser, more-correct `referent_per_np` referent set DEFAULT-ON, that leftmost-NP subject proxy mis-fires
(sentence-initial PP/temporal/modifier nouns) and a single sentence-global flag is applied to every clause.
On the board (tools/baseline_board.instrument_who_did_what, LitBank 19c, load_docs(16), n=1830 agent Qs)
the AGENT accuracy REGRESSES:  positional ref-OFF 0.2257  ->  positional ref-ON 0.0410  (and the parser-
wired arm only reaches 0.0754 -- a trained parser does NOT recover it either). The picked agents are
overwhelmingly INANIMATE distractors (chapter/tuppence/trickery/river/foot...) while gold agents are
animate (passengers/chancellor/reporters...). Textbook Competition-Model territory.

HOW THE BRAIN DOES THIS (PINNED): thematic-role assignment is GRADED, PARALLEL CUE COMPETITION -- the
Competition Model (Bates & MacWhinney 1989), constraint satisfaction (MacDonald 1994), cue-based retrieval
(Lewis & Vasishth 2005). Candidates compete by additive cue activation A_i = sum_c w_c * support_c(i); the
argmax is the discrete collapse (McClelland 2013: additive+softmax IS the Bayesian posterior). English is
word-order-DOMINANT; ANIMACY is the highest-leverage secondary agent cue (animate -> agent); VOICE flips it
(passive -> by-phrase is agent). NOT a position rule, NOT a trained parser.

WHAT IS REUSED (not re-derived): the PINNED computation `hdlab.graded_competition.net_activation`/`map_pick`
(the same organ `hdlab.graded_role_assigner` uses for the PATIENT slot -- this cell adds the AGENT slot,
which the substrate lacked); `hdlab.thematic_role_labeler.is_passive_clause`/`lemma_verb`;
`hdlab.animacy_lexicon.lookup_animacy`. OUR-INVENTION-UNDER-TEST (swept, not adopted): the agent cue set +
the validity-seeded weights below.

SHADOW READER (scope: solver may NOT write hdlab/): `CMAgentReader` subclasses the live `SituationReader`
and overrides ONLY `_read_events` with a byte-faithful copy of the stock loop in which the AGENT is
recomputed by the competition; the PATIENT is left exactly as `_assign_roles` produced it (so the
`referent_per_np` +0.336 patient win is preserved BY CONSTRUCTION). This is the one-variable proof of the
hdlab change strategy would land (stated in SOLVED.md).

KEY FINDING (the brief's rule-swap was HALF the answer): the Competition-Model rule over the DENSE referent
set only reaches 0.082 (cm_dense) -- it does NOT recover. The decisive variable is the candidate SET: the
AGENT must compete over the TRACKED / GIVEN discourse entities (the coref-column set -- Centering Cb->subject,
Grosz 1995; DuBois 1987 Preferred Argument Structure), NOT every referent_per_np NP head. This DECOUPLES the
agent source (tracked/given) from the patient source (dense, the +0.336) -- the same decouple lesson as the
prior problem (coref vs role), now agent-vs-patient.

ARMS (referent_per_np ON except the floor; the varied thing is named):
  pos_OFF   positional agent, referent_per_np OFF (coref set)         -> pre-referent baseline / RECOVER-TO bar (0.2257)
  pos_ON    positional agent, referent_per_np ON  (dense set)         -> the regression / can-fail baseline (0.0410)
  cm_dense  Competition-Model agent over the DENSE set                -> set floods, does NOT recover (0.082)
  cm_ON     Competition-Model agent over the TRACKED/given set        -> THE FIX (0.2519)
  twin_ON   cm_ON with SHUFFLED cue supports (info-free)              -> MUST LOSE (0.1596)

Run:  .venv/Scripts/python.exe experiments/exp_cmrole_agent_board_v1.py [--docs 16] [--nboot 2000]
"""
from __future__ import annotations
import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone

import numpy as np

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import experiments.exp_situation_model_qa_v1 as SITQA
from hdlab.situation_reader import (
    SituationReader, EventRecord, SuppressedPredicate, DEFAULT_ROLES, EventBundleCodec, ChunkedFocus,
    FOCUS_SEED, _sentence_nominals, _assign_roles, _assign_frame_primary_roles, _assign_affect,
)
from hdlab.graded_competition import net_activation
from hdlab.thematic_role_labeler import is_passive_clause, lemma_verb
from hdlab.animacy_lexicon import lookup_animacy

SEED = 20260904
OUT_DIR = os.path.join(_REPO, "data", "exp_cmrole_agent_board_v1")

# --- validity-seeded Competition-Model agent-cue weights. English is word-order-DOMINANT (agent preverbal),
#     but the clause SUBJECT is the NEAREST preceding CORE argument (clause-locality/adjacency, Lewis-Vasishth
#     cue-based retrieval: the most active preceding NP), refined by ANIMACY (agent->animate, the decisive
#     secondary cue) and VOICE (passive flips to the by-phrase). Hand-set from cue validity, NOT trained. ---
AGENT_W = {"preverbal": 3.0, "core_arg": 2.0, "animacy": 2.0, "salience": 2.0, "adjacency": 1.0, "byagent": 6.0}
_PREPS = frozenset(("in", "on", "at", "by", "of", "for", "with", "to", "from", "into", "onto", "upon",
                    "over", "under", "through", "about", "among", "amongst", "between", "against",
                    "toward", "towards", "within", "without", "during", "after", "before", "beside",
                    "behind", "beyond", "near", "off", "out", "across", "around", "beneath"))
_NP_SKIP = frozenset(("DET", "ADJ", "NUM", "PUNCT"))          # NP-internal modifiers to skip when scanning left


def _pp_governed(low, up, p):
    """Is the noun at p the object of a preposition? Scan left over NP-internal modifiers (DET/ADJ/NUM/PUNCT
    + possessive); if a preposition governs before any clause-blocking token, it is a PP object -> NOT a subject."""
    j = p - 1
    for _ in range(5):
        if j < 0:
            return False
        t = low[j]
        u = up[j] if j < len(up) else None
        if t in _PREPS:
            return True
        if u in _NP_SKIP or t in ("'s", "'", "the", "a", "an"):
            j -= 1
            continue
        return False
    return False


# personal pronouns as discourse participants: nominative (he/she/they/we/i/you) are animate agents; 'it' is
# inanimate; accusative (him/her/them/us/me) are animate but rarely subjects (their post-verbal position, not
# their animacy, keeps them out of the agent slot). Only consulted when pronoun mentions are agent candidates.
_ANIM_PRON = frozenset(("he", "she", "they", "we", "i", "you", "him", "her", "them", "us", "me"))
# CASE cue (Competition Model: case morphology is a HIGH-VALIDITY cue where a language marks it; English marks
# it on pronouns). NOMINATIVE pronouns can be SUBJECTS; accusative (him/her/them/us/me), possessive
# (his/her/their/its/my/your/our), and reflexive (himself/themselves/...) pronouns CANNOT -> not agent candidates.
NOMINATIVE_PRON = frozenset(("he", "she", "they", "we", "i", "you", "it", "who"))


# Clause-boundary markers (brain-foundational clause segmentation: role assignment is CLAUSE-BOUNDED -- an
# argument competes within its clause, incremental parsing). Subordinators start adverbial clauses; clause-level
# coordinators + strong punctuation separate coordinate clauses. Relativizers (who/which/that) are DELIBERATELY
# NOT boundaries here -- they EMBED, and the main-clause subject precedes them, so bounding at them would delete it.
_SUBORD = frozenset(("because", "when", "while", "if", "although", "though", "since", "unless", "after",
                     "before", "until", "as", "whereas", "whenever", "wherever", "once", "lest"))
_COORD = frozenset(("and", "but", "or", "nor", "yet", "so"))
_STRONGPUNCT = frozenset((";", ":", "--", "—", "(", ")"))


def clause_bounds(toks, up, v0):
    """The [left, right) clause span of the verb at v0 (0-based). Left = just after the nearest preceding
    clause boundary (subordinator / strong punct / clause-coordinator that separates two verbs); right =
    the nearest following such boundary. This is the incremental clause segmentation the subject search is
    bounded by -- glass-box, reads only toks/pos."""
    low = [t.lower() for t in toks]
    left = 0
    for i in range(v0):
        t = low[i]
        if t in _SUBORD or t in _STRONGPUNCT:
            left = i + 1
        elif t in _COORD and any(j < len(up) and up[j] == "VERB" for j in range(left, i)):
            left = i + 1                       # a coordinator AFTER a verb in this span = a new coordinate clause
    right = len(toks)
    for i in range(v0 + 1, len(toks)):
        t = low[i]
        if t in _SUBORD or t in _STRONGPUNCT:
            right = i
            break
        if t in _COORD and any(j < len(up) and up[j] == "VERB" for j in range(v0 + 1, i)):
            right = i
            break
    return left, right


def _nominals_keep_pron(mentions, n_sents):
    """Like situation_reader._sentence_nominals but KEEPS pronoun mentions (they are the maximally-given
    Centering mentions -> valid, strong AGENT candidates). Per-sentence, sorted by token position."""
    per = [[] for _ in range(n_sents)]
    for m in mentions:
        si = m["sent_idx"]
        if 0 <= si < n_sents:
            per[si].append(m)
    for lst in per:
        lst.sort(key=lambda mm: (mm["wtok_start"], mm.get("midx", 0)))
    return per


def _is_animate(head: str, tag, gaz) -> float:
    """+1 animate, -1 inanimate, 0 unknown. lookup_animacy covers common animate/inanimate nouns; it returns
    None for most PROPN, so we recover the animacy of a NAMED discourse referent (a name denoting a person is
    animate -- a coverage fix for the same cue, NOT a new cue): a gazetteer given-name, or a PROPN head, is an
    animate participant in narrative prose. (Place-name PROPN are typically preposition-governed, so the
    core_arg cue excludes them regardless.) Personal pronouns are animate participants; 'it' is inanimate."""
    if head in _ANIM_PRON:
        return 1.0
    if head == "it":
        return -1.0
    a = lookup_animacy(head, tag)
    if a is not None:
        if a["animacy"] == "animate":
            return 1.0
        if a["animacy"] == "inanimate":
            return -1.0
    if gaz and head in gaz:
        return 1.0
    if tag == "PROPN":
        return 1.0
    return 0.0


def agent_supports(toks, up, v0, cands, gaz, cluster_freq=None):
    """Per-candidate AGENT support arrays for the Competition-Model cues. `cands` = [(wtok_start, head,
    cluster), ...] (the sentence's non-pronoun mention heads, as _pick_role_mentions sees them); v0 =
    predicate index (0-based). cluster_freq = passage-level {cluster: mention_count} for the givenness cue.
    Reads ONLY toks/pos + the animacy lexicon + gazetteer + discourse-cluster counts -- glass-box, no gold."""
    low = [t.lower() for t in toks]
    passive = is_passive_clause(toks, up)
    cf = cluster_freq or {}
    S = {"preverbal": [], "core_arg": [], "animacy": [], "salience": [], "adjacency": [], "byagent": []}
    for (p, head, cl) in cands:
        pre = p < v0
        prevtok = low[p - 1] if p - 1 >= 0 else ""
        by = 1.0 if prevtok == "by" else 0.0
        core = 0.0 if _pp_governed(low, up, p) else 1.0     # a preposition-governed noun is NOT the subject
        tag = up[p] if p < len(up) else None
        if passive:                                         # VOICE flip: surface subject demoted; by-phrase = agent
            S["preverbal"].append(0.0)
            S["byagent"].append(by)
            S["adjacency"].append(1.0 / (1.0 + abs(p - v0)) if by else 0.0)
        else:                                               # ACTIVE: agent is preverbal (word-order dominant)
            S["preverbal"].append(1.0 if pre else 0.0)
            S["byagent"].append(0.0)
            # clause-locality: the subject is the NEAREST preceding core NP (Lewis-Vasishth most-active retrieval)
            S["adjacency"].append(1.0 / (1.0 + (v0 - p)) if pre else 0.0)
        S["core_arg"].append(core)
        S["animacy"].append(_is_animate(head, tag, gaz))
        # CENTERING givenness (Grosz-Joshi-Weinstein): a TRACKED discourse entity (established coref chain,
        # freq>=2) is the salient center -> realized as SUBJECT. A one-off (fresh singleton) is not.
        S["salience"].append(1.0 if cf.get(cl, 0) >= 2 else 0.0)
    return S


def cm_agent_pick(toks, up, v0, noms, patient_head, gaz, weights, cluster_freq=None, twin_seed=None):
    """Competition-Model AGENT = argmax additive cue activation over the sentence's referent candidates.
    Returns a head string or '?'. REUSES graded_competition.net_activation. `patient_head` is accepted for
    signature parity but is NOT excluded: the cues separate the roles (preverbal dominates the agent in an
    active clause; the by-phrase wins under passive -- where the stock positional 'patient' has wrongly taken
    the by-phrase agent, so excluding it would DELETE the true agent). twin_seed set => INFO-FREE TWIN:
    shuffle each cue's per-candidate support across candidates (structure->candidate mapping destroyed)."""
    cands = [(m["wtok_start"], m["head"], m.get("cluster")) for m in noms]
    if not cands:
        return "?"
    S = agent_supports(toks, up, v0, cands, gaz, cluster_freq)
    if twin_seed is not None:
        rng = np.random.default_rng(twin_seed + v0 + len(cands))
        S = {c: list(np.asarray(v)[rng.permutation(len(v))]) for c, v in S.items()}
    A = net_activation(S, weights)
    return cands[int(np.argmax(A))][1]


class CMAgentReader(SituationReader):
    """Live reader with the AGENT recomputed by the Competition Model; PATIENT byte-identical to stock."""

    def __init__(self, *a, cm_weights=None, cm_gaz=None, cm_twin_seed=None, agent_source="coref",
                 include_pron_agents=False, resolve_pron=False, clause_local=False, agent_mode="cm",
                 case_filter=False, **k):
        super().__init__(*a, **k)
        # case_filter: drop NON-nominative pronoun mentions (accusative/possessive/reflexive) from the agent
        # candidate set -- the Competition-Model CASE cue (they are morphologically marked as non-subjects).
        self._case_filter = case_filter
        # agent_mode: 'cm' = Competition-Model cue competition (default). 'parser' = the in-repo glass-box arc
        # parser's subject (route_predicate_arguments 'agent') mapped to the tracked+pronoun candidate set.
        # 'parser_cm' = parser subject when it fires, CM competition as the fallback (a graded-precision hybrid).
        self._agent_mode = agent_mode
        self._cm_weights = dict(cm_weights) if cm_weights else dict(AGENT_W)
        self._cm_gaz = cm_gaz
        self._cm_twin_seed = cm_twin_seed
        # clause_local: bound the AGENT candidates to the verb's CLAUSE span (incremental clause segmentation --
        # the subject competes within its clause, not the whole multi-clause sentence).
        self._clause_local = clause_local
        # agent candidate source: 'coref' = the TRACKED/GIVEN discourse entities (Centering-salient set --
        # the fix); 'dense' = every referent_per_np NP head (floods the agent competition with distractors).
        self._agent_source = agent_source
        # include_pron_agents: keep SUBJECT PRONOUNS (he/she/they/...) as agent candidates. A subject pronoun is
        # the maximally-given mention of the salient entity (Centering: the Cb is pronominalized) -> the strongest
        # agent candidate; _sentence_nominals filters them, which is why 70% of gold agents were unreachable.
        # resolve_pron: additionally resolve a pronoun agent to its antecedent entity name via the coref column.
        self._include_pron_agents = include_pron_agents
        self._resolve_pron = resolve_pron
        self._cm_conll = None

    def read(self, conll_path):
        self._cm_conll = conll_path                    # stash so _read_events can build the coref-column agent set
        return super().read(conll_path)

    def _read_events(self, sents, mentions, n_sents):
        # BYTE-FAITHFUL copy of the stock SituationReader._read_events (role_route='positional' branch),
        # with EXACTLY ONE change: `agent` is recomputed by cm_agent_pick. `patient` is left as _assign_roles
        # produced it (preserves the referent_per_np +0.336 patient win). All other lines are the stock reader.
        codec = EventBundleCodec(n_dim=self.focus_n_dim, roles=DEFAULT_ROLES, seed=FOCUS_SEED)
        focus = ChunkedFocus(codec, capacity=4, fanout=2, seed=FOCUS_SEED)
        sent_noms = _sentence_nominals(mentions, n_sents)   # DENSE referent set -> PATIENT (the residual, +0.336)
        # AGENT candidate set: the TRACKED / GIVEN discourse entities (Centering-salient; DuBois 1987 Preferred
        # Argument Structure -- the transitive AGENT is the given/tracked argument). 'coref' = the coref-column
        # mentions (the tracked entities); 'dense' = every referent_per_np NP head (floods with distractors).
        if self._agent_source == "coref" and self._cm_conll is not None:
            from hdlab.coref import parse_litbank_conll
            coref_ment, _nc = parse_litbank_conll(self._cm_conll, name_gender_map=self.gaz)
            # include_pron_agents: KEEP subject pronouns as agent candidates (Centering: the salient Cb is
            # pronominalized -> a subject pronoun is the strongest agent candidate; _sentence_nominals drops them).
            agent_sent_noms = (_nominals_keep_pron(coref_ment, n_sents) if self._include_pron_agents
                               else _sentence_nominals(coref_ment, n_sents))
            if self._include_pron_agents and self._case_filter:   # CASE cue: keep only nominative pronouns
                agent_sent_noms = [[m for m in lst if (not m.get("is_pronoun"))
                                    or m["head"].lower() in NOMINATIVE_PRON] for lst in agent_sent_noms]
            agent_src = coref_ment
        else:
            agent_sent_noms = sent_noms
            agent_src = mentions
        # Centering givenness per cluster. Count pronoun mentions too when they are agent candidates
        # (frequent pronominalization == high salience -> a stronger given-entity signal).
        agent_freq = {}
        for m in agent_src:
            if self._include_pron_agents or not m.get("is_pronoun"):
                agent_freq[m.get("cluster")] = agent_freq.get(m.get("cluster"), 0) + 1
        events, role_fillers, suppressed = [], [], []
        gidx = 0
        for si, toks in enumerate(sents):
            text = " ".join(toks)
            evs, _tagged = self._extract_events(text)
            noms = sent_noms[si] if si < len(sent_noms) else []          # dense -> patient
            anoms = agent_sent_noms[si] if si < len(agent_sent_noms) else []   # tracked -> agent
            up = self._cached_tag(list(toks)) if (noms or anoms) else []
            verb_lows = self.pred_gate_fn(text) if self.pred_gate_fn is not None else None
            # PARSER arm: the in-repo arc parse -> route_predicate_arguments 'agent' position per verb, aligned
            # to the reader's tokens (the event extractor tokenizes differently -> _align_events_to_toks).
            rr = self._router_roles(list(toks)) if (anoms and self._agent_mode != "cm") else {}
            toks_pos = self._align_events_to_toks(evs, toks) if rr else [None] * len(evs)
            for ei, e in enumerate(evs):
                agent, patient = _assign_roles(e.idx, noms, lemma=e.lemma,
                                               gate_intransitive=self.gate_intransitive)
                # -- THE ONE CHANGE: Competition-Model agent over the TRACKED entities (word-order+animacy+
                #    givenness+voice competition). PATIENT stays the stock positional pick (preserves +0.336). --
                if anoms:
                    acand = anoms
                    if self._clause_local:      # bound candidates to the verb's clause span (segmentation)
                        lo, hi = clause_bounds(toks, up, e.idx)
                        acand = [m for m in anoms if lo <= m["wtok_start"] < hi] or anoms
                    parser_agent = None
                    if self._agent_mode != "cm":     # parser subject mapped to the tracked+pronoun candidate
                        vp = toks_pos[ei]
                        vr = rr.get(vp) if vp is not None else None
                        if vr and "agent" in vr:
                            parser_agent = self._nom_head_at(acand, vr["agent"])
                    if self._agent_mode == "parser":     # parser ALONE (no CM fallback) -> isolates its recall
                        agent = parser_agent if parser_agent is not None else "?"
                    elif self._agent_mode == "parser_cm":
                        agent = parser_agent if parser_agent is not None else cm_agent_pick(
                            toks, up, e.idx, acand, patient, self._cm_gaz, self._cm_weights,
                            cluster_freq=agent_freq, twin_seed=self._cm_twin_seed)
                    else:
                        agent = cm_agent_pick(toks, up, e.idx, acand, patient, self._cm_gaz, self._cm_weights,
                                              cluster_freq=agent_freq, twin_seed=self._cm_twin_seed)
                if verb_lows is not None and e.lemma not in verb_lows:
                    suppressed.append(SuppressedPredicate(
                        sent_idx=si, predicate=e.lemma, tense=str(e.tense), agent=agent, patient=patient))
                    continue
                rf = {"PRED": e.lemma, "AGENT": agent, "PATIENT": patient, "TENSE": str(e.tense)}
                vec = codec.encode_event(rf); focus.push(vec, gidx)
                subj_role, obj_role = _assign_frame_primary_roles(
                    e.lemma, toks, e.idx, noms, gate_intransitive=self.gate_intransitive)
                affect = _assign_affect(patient, text)
                events.append(EventRecord(global_idx=gidx, sent_idx=si, predicate=e.lemma, agent=agent,
                                          patient=patient, tense=str(e.tense), subj_role=subj_role,
                                          obj_role=obj_role, affect=affect, pred_idx=e.idx))
                role_fillers.append(rf); gidx += 1
        return events, focus, codec, role_fillers, suppressed


# --------------------------------------------------------------------------- scoring on the board arm
def _score_doc(sm, wdw_rec):
    """Return the per-question correctness list AND the patient-answer signature (to prove patient preserved).

    This cell reports the SOLVED HEADLINE (the LAST-matching-event readout: pos_OFF 0.2257 / pos_ON 0.0410 /
    cm_ON 0.2519), which isolates the per-event AGENT ASSIGNMENT. The context-cued answer_instanced readout
    (SITQA.ANSWER_INSTANCED, landed default-ON 2026-09-04) is a SEPARATE lever proven in
    exp_cmrole_agent_readout_v1 -- so force it OFF here (save/restore, no global leak) to keep this witness
    reproducing the assigned-bar headline regardless of the live default."""
    qa = SITQA.SituationQA(sm)
    correct, pat_sig = [], []
    _prev_ai = SITQA.ANSWER_INSTANCED
    SITQA.ANSWER_INSTANCED = False
    try:
        for q in SITQA.build_events_questions(sm, wdw_rec):
            _d, ans = qa.answer(q["question"], q)
            correct.append(int(SITQA._match(ans, q["gold"], "events")))
    finally:
        SITQA.ANSWER_INSTANCED = _prev_ai
    for ev in sm.events:                     # patient signature -- must be identical between pos_ON and cm_ON
        pat_sig.append((ev.sent_idx, ev.predicate, ev.patient))
    return correct, pat_sig


def _reader(arm, gaz):
    # PIN the positional arms to cm_agent=False now that the Competition-Model AGENT is LANDED default-ON in
    # hdlab.situation_reader (2026-09-04): a bare SituationReader(role_route='positional', referent_per_np=True)
    # would otherwise BE the fix, not the positional regression. pos_ON must stay the pre-fix positional-dense
    # regression (the can-fail baseline); the CM arms below prove the fix via the shadow CMAgentReader.
    if arm == "pos_OFF":
        return SituationReader(gaz=gaz, role_route="positional", referent_per_np=False, cm_agent=False)
    if arm == "pos_ON":
        return SituationReader(gaz=gaz, role_route="positional", referent_per_np=True, cm_agent=False)
    # CM arms: referent_per_np ON (dense PATIENT, +0.336) with a Competition-Model AGENT.
    #   cm_dense = agent competes over the DENSE set (floods with distractors -> fails)
    #   cm_ON    = agent competes over the TRACKED/given (coref) set -- the FIX
    #   twin_ON  = cm_ON with shuffled cue supports (info-free)
    src = "dense" if arm == "cm_dense" else "coref"
    twin = SEED if arm == "twin_ON" else None
    return CMAgentReader(gaz=gaz, role_route="positional", referent_per_np=True,
                         cm_weights=AGENT_W, cm_gaz=gaz, cm_twin_seed=twin, agent_source=src)


def _boot(per_doc_arm_a, per_doc_arm_b, nboot, seed, doc_level=True):
    """Paired bootstrap of (acc_a - acc_b). per_doc_* = list over docs of per-question correctness lists.
    doc_level=True resamples DOCS (honest unit; questions within a doc correlate); else resamples items."""
    rng = np.random.default_rng(seed)
    ndoc = len(per_doc_arm_a)
    if doc_level:
        deltas = []
        for _ in range(nboot):
            idx = rng.integers(0, ndoc, size=ndoc)
            a = np.concatenate([per_doc_arm_a[i] for i in idx]); b = np.concatenate([per_doc_arm_b[i] for i in idx])
            deltas.append(a.mean() - b.mean())
    else:
        flat_a = np.concatenate(per_doc_arm_a); flat_b = np.concatenate(per_doc_arm_b); n = len(flat_a)
        deltas = []
        for _ in range(nboot):
            idx = rng.integers(0, n, size=n)
            deltas.append(flat_a[idx].mean() - flat_b[idx].mean())
    deltas = np.array(deltas)
    return {"delta": float(np.concatenate(per_doc_arm_a).mean() - np.concatenate(per_doc_arm_b).mean()),
            "lo": float(np.percentile(deltas, 2.5)), "hi": float(np.percentile(deltas, 97.5)),
            "ci_hw": float((np.percentile(deltas, 97.5) - np.percentile(deltas, 2.5)) / 2),
            "p_le_0": float((deltas <= 0).mean()), "ci_sep": bool(np.percentile(deltas, 2.5) > 0)}


def run(n_docs=16, nboot=2000):
    t0 = time.time(); os.makedirs(OUT_DIR, exist_ok=True)
    gaz = SITQA.load_given_gazetteer()
    wdw = {r["doc"]: r for r in json.load(open(SITQA.WDW_GOLD, encoding="utf-8"))}
    docs = SITQA.load_docs(n_docs)
    docset = [d for d in docs if d in wdw and os.path.exists(os.path.join(SITQA.CONLL_DIR, d + ".conll"))]

    arms = ["pos_OFF", "pos_ON", "cm_dense", "cm_ON", "twin_ON"]
    per_doc = {a: [] for a in arms}
    pat_sig = {a: [] for a in arms}
    for doc in docset:
        path = os.path.join(SITQA.CONLL_DIR, doc + ".conll")
        for a in arms:
            sm = _reader(a, gaz).read(path)
            c, ps = _score_doc(sm, wdw[doc])
            per_doc[a].append(np.array(c, dtype=np.float64)); pat_sig[a].append(ps)

    acc = {a: float(np.concatenate(per_doc[a]).mean()) for a in arms}
    n = int(sum(len(x) for x in per_doc["pos_ON"]))
    # patient preservation: cm_ON patient signature must equal pos_ON's (agent-only change)
    pat_ok = all(pat_sig["cm_ON"][i] == pat_sig["pos_ON"][i] for i in range(len(docset)))

    print("=" * 92)
    print("COMPETITION-MODEL AGENT ROLE ASSIGNMENT on the board who-did-what AGENT arm")
    print("  LitBank 19c, load_docs(%d), n=%d agent questions   (%.0fs setup+read)" % (len(docset), n, time.time() - t0))
    print("-" * 92)
    for a in arms:
        print("  %-9s acc=%.4f" % (a, acc[a]))
    print("-" * 92)
    print("  RECOVER-TO bar (pos_OFF, pre-referent baseline)  = %.4f" % acc["pos_OFF"])
    print("  regression   (pos_ON)                            = %.4f" % acc["pos_ON"])
    print("  CM over DENSE set (cm_dense: set floods)         = %.4f" % acc["cm_dense"])
    print("  FIX: CM over TRACKED/given set (cm_ON)           = %.4f" % acc["cm_ON"])
    print("  info-free    (twin_ON, shuffled supports)        = %.4f" % acc["twin_ON"])
    print("  PATIENT preserved (cm_ON == pos_ON signatures)   = %s" % pat_ok)
    print("-" * 92)

    tests = {}
    for label, a, b in [("cm_ON - pos_ON  (recovery is real)", "cm_ON", "pos_ON"),
                        ("cm_ON - pos_OFF (>=0 => recovered to baseline)", "cm_ON", "pos_OFF"),
                        ("cm_ON - twin_ON (beats info-free)", "cm_ON", "twin_ON"),
                        ("twin_ON - pos_ON (twin does NOT recover)", "twin_ON", "pos_ON")]:
        d = _boot(per_doc[a], per_doc[b], nboot, SEED, doc_level=True)
        di = _boot(per_doc[a], per_doc[b], nboot, SEED, doc_level=False)
        tests[label] = {"doc": d, "item": di}
        print("  %-46s d=%+.4f  doc-CI[%+.4f,%+.4f] hw=%.4f p<=0=%.3f sep=%s | item-CI[%+.4f,%+.4f]"
              % (label, d["delta"], d["lo"], d["hi"], d["ci_hw"], d["p_le_0"], d["ci_sep"], di["lo"], di["hi"]))
    print("=" * 92)

    out = {"anchor_name": "cmrole_agent_board_v1", "n_docs": len(docset), "n_questions": n,
           "acc": acc, "patient_preserved": pat_ok, "agent_weights": AGENT_W, "twin": "shuffled-supports",
           "tests": tests, "elapsed_s": round(time.time() - t0, 1),
           "ts_iso": datetime.now(timezone.utc).isoformat()}
    tmp = os.path.join(OUT_DIR, "metrics.json.tmp")
    with open(tmp, "w", encoding="ascii") as fh:
        json.dump(out, fh, indent=2)
    os.replace(tmp, os.path.join(OUT_DIR, "metrics.json"))
    print("[done] %.0fs -> %s" % (time.time() - t0, os.path.join(OUT_DIR, "metrics.json")))
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--docs", type=int, default=16)
    ap.add_argument("--nboot", type=int, default=2000)
    args = ap.parse_args()
    run(args.docs, args.nboot)
