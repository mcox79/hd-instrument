"""EVENT-CENTRALITY tie-break: the situation-model MEMORY drives the coref decision.

INTEGRATION-PAYOFF THESIS (the untested load-bearing claim of the integration path):
event / situation structure disambiguates reference. A situation-model dimension FEEDS
BACK to lift the same-gender cross-sentence coref residual. This module makes the coref
resolve() QUERY a genuine Cowan-4 event-bundle MEMORY (hdlab.situation_focus.ChunkedFocus
of role-slot EVENT bundles, hdlab.event_bundle.EventBundleCodec) to break same-gender ties,
so the memory is DECISION-LOAD-BEARING (fixes the 29512 write-only-witness gap: there the
HD store was a parallel witness never read by resolve(); here the HD unbind+cleanup output
IS the tie-break ranker -- ablating the query CHANGES the decision).

THE MEMORY (genuine HD, glass-box):
  As the reader walks the mention stream it extracts one EVENT per sentence that has a
  specific-character subject: AGENT = the first specific-character mention in SUBJECT
  position (sent_role_rank == 0); PATIENT = the next specific-character mention. The event
  is encoded as a role-slot bundle {PRED, AGENT, PATIENT, TENSE} and PUSHED into a bounded
  Cowan-4 ChunkedFocus (capacity 4). At a pronoun the active focus holds the ~4 most-recent
  character events. NOTE the agent/patient assignment is POSITIONAL (first-mention = subject
  proxy), NOT true SRL -- structure SUPPLIED, general, parse-derived, not tuned to LitBank.

THE QUERY (the tie-break ranker):
  On a same-gender topical target (>= 2 known-same-gender candidates after agreement-narrow)
  the reader QUERIES the memory: for each active event it UNBINDS the AGENT and PATIENT role
  keys (hdlab HD unbind == bipolar bind) and CLEANS UP to a filler symbol (matmul + argmax
  over the codebook). The cleaned-up symbols vote for the pool candidates. The candidate
  with the highest CENTRALITY wins the tie. Two centrality modes give the ONE-VARIABLE
  fair contrast (identical architecture, identical HD queries; only the weighting differs):
    * event_role : score += AGENT_W for an AGENT-role match, PATIENT_W for a PATIENT match;
                   NO recency term. Rewards being the AGENT that DRIVES the recent events
                   = the event-STRUCTURE signal.
    * recency    : score += recency_weight(event) for ANY role match (AGENT and PATIENT
                   weigh the SAME, flat); newest event dominates. Rewards being in the MOST
                   RECENT event regardless of role = the RECENCY / locality signal.
  A win of event_role over recency proves EVENT STRUCTURE adds over recency (else the lift
  collapses to the locality lever already banked in 29514).

FAITHFUL REUSE (nothing improved over validated logic; banked cells/modules NOT edited):
  - SceneProtagonistReader (local-window topical pick = the banked 29514 baseline, subset
    acc 0.407) + SuppressReader pool/suppression/adaptive-pick: hdlab.scene_segment /
    hdlab.coref_distractor_suppress. With query_memory=False this reader reproduces
    SceneProtagonistReader.resolve_stream BIT-FOR-BIT (the ONE isolated variable is the
    memory query). Asserted in the self-test.
  - EventBundleCodec role-slot event encoding + query: hdlab.event_bundle (byte-identical
    to the M1.7 RoleSlotSummarizer binding).
  - ChunkedFocus bounded Cowan-4 focus + chunk compression: hdlab.situation_focus.

GLASS-BOX: the queried centrality is inspectable (which events are in focus, each role
unbind's cleaned symbol + score, the per-candidate centrality, why the tie broke). Pure
symbolic decision arithmetic over GENUINE HD unbind+cleanup; NO external LLM, NO network,
NO gold seen by resolve(). ASCII-only, no em-dash.
"""

from __future__ import annotations

from typing import Dict, List, Optional, Set, Tuple

from collections import defaultdict

from hdlab.coref import name_content_tokens, sent_dist_bucket
from hdlab.coref_distractor_suppress import GenericDistractorFilter, build_ever_subject_heads
from hdlab.scene_segment import SceneProtagonistReader, TOPICAL_SLOT_HEADS
from hdlab.state_of_mind import PRONOUN_SCOPE, TARGET_PRONOUNS, EntityState

from hdlab.event_bundle import EventBundleCodec
from hdlab.situation_focus import ChunkedFocus

# PINNED graded ACT-R cue-based antecedent retrieval (recency load-bearing) -- the live pronoun pick
# (landed 2026-09-06, replacing the anti-brain-foundational rolemass topical pick + event-centrality
# override). See graded_pick note on EventCentralityReader below.
from hdlab.graded_coref_pick import graded_antecedent_pick, TUNED_WEIGHTS

# UNIFIED discourse referent (DRT file-change): ONE card per entity, merged across name/common/pronoun,
# pronoun pick by ACT-R base-level activation over the unified referents (landed behind unified_referent,
# default OFF -> byte-identical). Faithful port of exp_unified_referent_gum_v1.Resolver(arm='unified').
from hdlab.unified_referent import resolve_unified_stream

# Event-role centrality weights (AGENT drives the event > PATIENT); glass-box constants.
AGENT_W = 2.0
PATIENT_W = 1.0
EVENT_ROLES = ("AGENT", "PATIENT")
EVENT_N_DIM = 4096          # round-trips cleanly at Cowan-4 load (29511 capacity signature)


def _role_str(rank: int) -> str:
    """Map a mention's sent_role_rank (0=subject, 1=object, else) to the graded pick's role token
    (SUBJECT/OBJECT/OTHER). Byte-faithful to exp_coref_graded_live_transfer_v1._role_str."""
    return "SUBJECT" if rank == 0 else ("OBJECT" if rank == 1 else "OTHER")


class EventMemory:
    """Genuine Cowan-4 event-bundle memory (real HD ChunkedFocus), queried by resolve().

    Each pushed event is a role-slot bundle stored in a bounded ChunkedFocus (capacity 4).
    active_event_gidxs() returns the events currently IN the focus (direct + chunked);
    query_event(gidx, role) is the HD unbind+cleanup that recovers a role filler symbol.
    event_meta records the ground-truth agent/patient for glass-box audit (NOT used to
    rank -- the ranker reads the HD cleanup output, not this dict)."""

    def __init__(self, n_dim: int = EVENT_N_DIM, capacity: int = 4, fanout: int = 2,
                 seed: int = 0) -> None:
        self.codec = EventBundleCodec(n_dim=n_dim, seed=seed)
        self.cf = ChunkedFocus(self.codec, capacity=capacity, fanout=fanout, seed=seed)
        self.gidx = 0
        self.event_meta: Dict[int, dict] = {}
        # round-trip fidelity witness (proves the HD store is genuine, not decorative)
        self.n_rt_checks = 0
        self.n_rt_agent_ok = 0

    def push_event(self, agent: str, patient: Optional[str], sent_idx: int) -> None:
        rf = {"PRED": "EVENT", "AGENT": agent, "PATIENT": (patient or "NONE"),
              "TENSE": "n"}
        ev = self.codec.encode_event(rf)
        self.cf.push(ev, self.gidx)
        self.event_meta[self.gidx] = {"agent": agent, "patient": patient,
                                      "sent_idx": sent_idx, "order": self.gidx}
        self.gidx += 1

    def focus_events(self) -> List[Tuple[int, "object"]]:
        """The Cowan-4 FOCUS OF ATTENTION = the DIRECT (depth-0) event bundles, as
        (gidx, stored_bundle_vec). Chunked (compressed-out) events have left the focus
        (graceful forgetting) and are NOT queried by the tie-break. The Cowan-4 buffer
        governs WHICH events are in focus (recent); the individual stored bundle is read
        directly (round-trips cleanly at this load -- the focus_vec superposition is the
        lossy path and is deliberately NOT used for the faithful structural read)."""
        out: List[Tuple[int, object]] = []
        for entry in self.cf.active:
            if entry.is_chunk:
                continue
            for g in entry.index:
                out.append((g, entry.vec))
        out.sort(key=lambda gv: gv[0])
        return out

    def query_bundle(self, vec, role: str) -> Tuple[Optional[str], float]:
        """HD unbind + cleanup: recover a role filler symbol from a stored event bundle
        (bipolar unbind == bind; cleanup == codebook matmul + argmax)."""
        return self.codec.query_role_vec(vec, role)

    def check_roundtrip(self, gidx: int) -> None:
        """Diagnostic: the in-focus bundle round-trips its AGENT (genuine memory witness)."""
        for g, vec in self.focus_events():
            if g != gidx:
                continue
            self.n_rt_checks += 1
            sym, _ = self.query_bundle(vec, "AGENT")
            if sym == self.event_meta.get(gidx, {}).get("agent"):
                self.n_rt_agent_ok += 1
            return


def hd_centrality(mem: EventMemory, pool_heads: Set[str], mode: str
                  ) -> Tuple[Dict[str, float], List[dict]]:
    """Query the memory for each pool candidate's centrality via HD unbind+cleanup.

    mode='event_role': AGENT_W for AGENT matches, PATIENT_W for PATIENT matches (no recency).
    mode='recency'   : recency_weight(event) for ANY role match, AGENT==PATIENT flat.
    Returns (scores{head->centrality}, detail[glass-box per-event role queries]). Both modes
    issue the IDENTICAL HD queries -- the one variable is the weighting."""
    focus = mem.focus_events()      # [(gidx, bundle_vec)] direct/in-focus events, oldest first
    scores: Dict[str, float] = {h: 0.0 for h in pool_heads}
    detail: List[dict] = []
    # recency rank: oldest in-focus event = 1, newest = n_focus
    order = {g: (rank + 1) for rank, (g, _v) in enumerate(focus)}
    for g, vec in focus:
        rec_w = float(order[g])
        row = {"gidx": g, "sent_idx": mem.event_meta.get(g, {}).get("sent_idx"),
               "agent_gold": mem.event_meta.get(g, {}).get("agent"),
               "patient_gold": mem.event_meta.get(g, {}).get("patient"), "roles": {}}
        for role in EVENT_ROLES:
            sym, sc = mem.query_bundle(vec, role)
            row["roles"][role] = {"cleaned": sym, "score": round(float(sc), 2)}
            if sym in scores:
                if mode == "event_role":
                    scores[sym] += AGENT_W if role == "AGENT" else PATIENT_W
                else:  # recency: flat over roles, weighted by event recency
                    scores[sym] += rec_w
        detail.append(row)
    return scores, detail


def _is_specific_nominal(m: dict) -> bool:
    """Specific character = a named or gender-cued nominal (matches scene_segment)."""
    if m.get("is_pronoun"):
        return False
    return (m.get("gender") is not None) or (m.get("name_gender") is not None)


class EventCentralityReader(SceneProtagonistReader):
    """SceneProtagonistReader (local-window topical baseline) + an event-bundle MEMORY that
    DRIVES the same-gender tie-break via HD query.

    query_memory=False reproduces SceneProtagonistReader.resolve_stream(prefer_topical=True,
    per_scene=True, ...) bit-for-bit (the memory query is the ONE isolated variable).
    query_memory=True: on a topical same-gender target the pool pick becomes the highest
    HD-centrality candidate (mode in {event_role, recency}); if the centrality is degenerate
    (no in-focus event mentions any pool candidate) the base topical pick stands (strict
    addition -- no info loss). Every override is recorded (mem_changed) so the cell measures
    the decision-change rate = memory is decision-driving.

    graded_pick (DEFAULT ON, landed 2026-09-06): the brain-foundational pronoun pick. When ON, the
    pool pick is the PINNED graded ACT-R cue-based retrieval (hdlab.graded_coref_pick, Lewis & Vasishth
    2005; recency load-bearing) and the event-centrality memory is forced OFF (it measurably HURTS:
    live pooled he/she coref_acc 0.4876 EC-off vs 0.4693 EC-on). This replaces the anti-brain-foundational
    rolemass topical pick (subject-role mass, NO recency term) + HD event-centrality override that scored
    0.4693 pooled -- BELOW plain recency 0.6052 -- lifting the live pooled pick to 0.6019 (+0.1327
    CI[+0.0929,+0.1738], named coref no-regress 0.4883->0.6165). graded_pick=False restores the exact
    incumbent rolemass+event-centrality path (the self-checkable reference / fallback). This is a
    register-general recency-mechanism fidelity correction, justified independently of the LitBank (19c)
    coref_acc number it was measured on."""

    def __init__(self, *, n_dim: int = EVENT_N_DIM, capacity: int = 4, fanout: int = 2,
                 mem_seed: int = 0, graded_pick: bool = True, unified_referent: bool = False,
                 **kw) -> None:
        super().__init__(**kw)
        self._n_dim = int(n_dim)
        self._capacity = int(capacity)
        self._fanout = int(fanout)
        self._mem_seed = int(mem_seed)
        self.n_glass_kept = 0
        self.graded_pick = bool(graded_pick)     # ON = PINNED graded ACT-R pick (event-centrality forced off)
        # unified_referent (DEFAULT OFF -> byte-identical): ON routes resolve_stream to the DRT file-change
        # unified referent (hdlab.unified_referent) -- ONE card per entity across name/common/pronoun, ACT-R
        # d=2.0 pick. Landed default-off (strategy flips on after first-hand verify).
        self.unified_referent = bool(unified_referent)
        self._midx_to_sent: Dict[int, int] = {}  # per-mention sentence index (graded ACT-R distance term)

    def resolve_stream(self, mentions: List[dict], targets: List[dict], *,
                       scene_ids: Optional[List[int]] = None,
                       topical_mode: str = "rolemass",
                       topical_heads: Optional[frozenset] = None,
                       use_gazetteer: bool = True, chain_pronouns: bool = True,
                       suppress_generic: bool = True,
                       use_nonref: bool = True, use_struct: bool = True,
                       query_memory: bool = False, centrality_mode: str = "event_role",
                       glass_box_limit: int = 0) -> List[dict]:
        """Mirror of SceneProtagonistReader.resolve_stream(prefer_topical=True, per_scene=True)
        plus the event-memory query. query_memory=False == the parent bit-for-bit."""
        if self.unified_referent:
            # UNIFIED discourse referent path (DRT file-change; ACT-R d=2.0 over unified referents). Ignores
            # the scene/event-memory scaffolding (the unified referent supersedes the fragmented overlay). With
            # this flag OFF everything below runs unchanged -> byte-identical to the landed graded_pick reader.
            return resolve_unified_stream(mentions, targets)
        if self.graded_pick:
            # PINNED graded ACT-R pick: stash per-mention sentence indices for the graded distance term,
            # and force the event-centrality memory OFF -- the graded retrieval is the SOLE pick (EC
            # measurably hurts: 0.4876 EC-off vs 0.4693 EC-on). Byte-faithful to the validated GRADED arm
            # (exp_coref_graded_live_transfer_v1.GradedPickReader.resolve_stream, _use_graded clean path).
            self._midx_to_sent = {m["midx"]: m.get("sent_idx", 0) for m in mentions}
            query_memory = False
        if topical_heads is None:
            topical_heads = TOPICAL_SLOT_HEADS
        if scene_ids is None:
            raise ValueError("EventCentralityReader requires scene_ids (fixed-window baseline)")
        ever_subj = build_ever_subject_heads(mentions)
        filt = GenericDistractorFilter(ever_subj, use_nonref=use_nonref,
                                       use_struct=use_struct)
        midx_to_role = {m["midx"]: m.get("sent_role_rank", 99) for m in mentions}
        target_by_midx = {t["target"]["midx"]: t for t in targets}

        # per-scene scaffolding (fixed-window local scenes = the 29514 locality baseline)
        scene_of_midx: Dict[int, int] = {}
        scene_to_midxs: Dict[int, Set[int]] = defaultdict(set)
        for m in mentions:
            si = m.get("sent_idx", 0)
            sc = scene_ids[si] if 0 <= si < len(scene_ids) else -1
            scene_of_midx[m["midx"]] = sc
            scene_to_midxs[sc].add(m["midx"])

        overlay = self._new_overlay()
        head_to_cluster: Dict[str, int] = {}
        records: List[dict] = []
        glass: List[dict] = []

        # event memory (built incrementally; queried by resolve at same-gender ties)
        mem = EventMemory(n_dim=self._n_dim, capacity=self._capacity,
                          fanout=self._fanout, seed=self._mem_seed) if query_memory else None
        cur_sent = mentions[0]["sent_idx"] if mentions else 0
        sent_buf: List[dict] = []   # nominal mentions of the current sentence (for event extract)

        def _emit_event():
            if mem is None or not sent_buf:
                return
            agent = None
            patient = None
            for mm in sent_buf:
                if _is_specific_nominal(mm) and mm.get("sent_role_rank", 99) == 0:
                    agent = mm["head"].lower()
                    break
            if agent is None:
                return
            for mm in sent_buf:
                if _is_specific_nominal(mm) and mm.get("sent_role_rank", 99) != 0:
                    h = mm["head"].lower()
                    if h != agent:
                        patient = h
                        break
            mem.push_event(agent, patient, cur_sent)
            mem.check_roundtrip(mem.gidx - 1)

        for m in mentions:
            if m["sent_idx"] != cur_sent:
                _emit_event()             # finalize the completed sentence's event
                sent_buf = []
                cur_sent = m["sent_idx"]

            resolved_ent = None
            pool_empty = False
            suppressed_any = False
            topical_fired = False
            mem_changed = False
            if m["is_pronoun"] and m["head"] in TARGET_PRONOUNS:
                now = overlay.n_observed
                sc = PRONOUN_SCOPE[m["head"]]
                cands = overlay._compatible_entities(sc["gender"], sc["number"])
                trank = midx_to_role.get(m["midx"], 99)
                if suppress_generic:
                    pool = [c for c in cands if not filt.is_generic(c)]
                    suppressed_any = len(pool) < len(cands)
                else:
                    pool = cands
                if pool:
                    do_topical = (m["head"] in topical_heads)
                    if do_topical:
                        tpool = self._agreement_narrow(pool, sc["gender"])
                        cur_scene = scene_of_midx.get(m["midx"], -1)
                        scene_midxs = scene_to_midxs.get(cur_scene)
                        base_pick = self._topical_pick(tpool, scene_midxs, midx_to_role,
                                                       topical_mode)
                        if base_pick is None:
                            base_pick = self._topical_pick(tpool, None, midx_to_role,
                                                           topical_mode)
                        resolved_ent = base_pick
                        topical_fired = True
                        # MEMORY QUERY: same-gender tie -> event-centrality tie-break.
                        if (query_memory and mem is not None and len(tpool) >= 2):
                            pool_heads = {e.head for e in tpool}
                            scores, detail = hd_centrality(mem, pool_heads, centrality_mode)
                            mx = max(scores.values()) if scores else 0.0
                            if mx > 0.0:
                                winners = sorted(
                                    [h for h, v in scores.items() if v == mx],
                                    key=lambda h: min(
                                        (e.mention_midxs[0] for e in tpool if e.head == h),
                                        default=1 << 30))
                                win_head = winners[0]
                                mem_pick = next((e for e in tpool if e.head == win_head), None)
                                if mem_pick is not None:
                                    mem_changed = (base_pick is None
                                                   or mem_pick.head != base_pick.head)
                                    resolved_ent = mem_pick
                                    if (glass_box_limit and self.n_glass_kept < glass_box_limit
                                            and mem_changed):
                                        glass.append({
                                            "target_midx": m["midx"], "pronoun": m["head"],
                                            "gold_cluster": m["cluster"],
                                            "pool_heads": sorted(pool_heads),
                                            "centrality": {h: round(v, 2)
                                                           for h, v in scores.items()},
                                            "base_pick": base_pick.head if base_pick else None,
                                            "mem_pick": mem_pick.head,
                                            "active_events": detail})
                                        self.n_glass_kept += 1
                    else:
                        resolved_ent = self._adaptive_pick(pool, now, trank, midx_to_role)
                else:
                    pool_empty = True
                    resolved_ent = self._adaptive_pick(cands, now, trank, midx_to_role)

                if m["midx"] in target_by_midx:
                    tinfo = target_by_midx[m["midx"]]
                    if resolved_ent is None:
                        rec = dict(resolved_head=None, resolved_cluster=None,
                                   attempted=False, correct=False)
                    else:
                        rc = head_to_cluster.get(resolved_ent.head)
                        rec = dict(resolved_head=resolved_ent.head, resolved_cluster=rc,
                                   attempted=True,
                                   correct=(rc is not None and rc == m["cluster"]))
                    rec.update(target_midx=m["midx"], gold_cluster=m["cluster"],
                               sent_dist=tinfo["sent_dist"],
                               bucket=sent_dist_bucket(tinfo["sent_dist"]),
                               pool_empty=pool_empty, suppressed_any=suppressed_any,
                               topical_fired=topical_fired, mem_changed=mem_changed,
                               n_cands=len(cands), n_pool=len(pool))
                    records.append(rec)

            # advance the mention stream
            if m["is_pronoun"]:
                overlay.observe(m["head"], is_pronoun=True,
                                gender=m["gender"], number=m["number"])
                if chain_pronouns and resolved_ent is not None:
                    resolved_ent.mention_midxs.append(m["midx"])
            else:
                eff_gender = m["gender"]
                if eff_gender is None and use_gazetteer:
                    eff_gender = m.get("name_gender")
                is_named = bool(name_content_tokens(m.get("span_toks", [m["head"]])))
                overlay.observe(m["head"], gender=eff_gender, number=m["number"],
                                is_proper_name=is_named)
                head_to_cluster[m["head"].lower()] = m["cluster"]
                sent_buf.append(m)

        _emit_event()   # flush the final sentence's event (harmless; after last target)
        if glass_box_limit:
            self.last_glass = glass
            if mem is not None:
                self.last_rt = (mem.n_rt_agent_ok, mem.n_rt_checks)
        return records

    # ── PINNED graded ACT-R pronoun pick (default ON) ────────────────────────────────────────────
    # Byte-faithful to the validated clean GRADED arm of exp_coref_graded_live_transfer_v1
    # (_use_graded=True with twin/propagate/soft_gender/keep_ec all OFF). The pool construction
    # (compatible + generic-suppress + agreement-narrow) and the mention replay in resolve_stream are
    # the deployed code, byte-unchanged; ONLY the pool PICK is swapped.

    def _priors_of(self, pool, midx_to_role):
        """Per-candidate prior-mention list as (sentence_index, role) tuples for graded_antecedent_pick
        (role in {SUBJECT,OBJECT,OTHER} from the mention's sent_role_rank)."""
        return [[(self._midx_to_sent.get(mx, 0), _role_str(midx_to_role.get(mx, 99)))
                 for mx in e.mention_midxs] or [(0, "OTHER")] for e in pool]

    def _graded_pool_pick(self, pool, midx_to_role):
        """The landed graded ACT-R cue-based antecedent retrieval over the (agreement-narrowed) pool
        (hdlab.graded_coref_pick.graded_antecedent_pick, TUNED_WEIGHTS). Single-candidate pool -> that
        candidate; empty -> None. Clean validated arm (no twin / propagate / soft-gender)."""
        pool = list(pool)
        if not pool:
            return None
        if len(pool) == 1:
            return pool[0]
        priors = self._priors_of(pool, midx_to_role)
        p_sent = max((s for pr in priors for (s, _r) in pr), default=0) + 1
        res = graded_antecedent_pick(priors, p_sent, weights=TUNED_WEIGHTS)
        idx = res["pick"]
        return pool[idx] if 0 <= idx < len(pool) else None

    def _topical_pick(self, pool, scene_midxs, midx_to_role, mode):
        """Graded ACT-R pick when graded_pick is on (recency load-bearing); else the incumbent rolemass
        topical pick (SceneProtagonistReader._topical_pick) -- the self-checkable graded_pick=False fallback."""
        if not self.graded_pick:
            return super()._topical_pick(pool, scene_midxs, midx_to_role, mode)
        return self._graded_pool_pick(pool, midx_to_role)

    def _adaptive_pick(self, pool, now, trank, midx_to_role):
        """Graded ACT-R pick when graded_pick is on; else the incumbent backbone adaptive pick."""
        if not self.graded_pick:
            return super()._adaptive_pick(pool, now, trank, midx_to_role)
        return self._graded_pool_pick(pool, midx_to_role)


# ===================== formula self-tests ==========================================

def _mk(head, cluster, is_pron, sent, midx, gender, role_rank, number="singular",
        name_gender=None):
    return {"head": head, "cluster": cluster, "is_pronoun": is_pron,
            "sent_idx": sent, "midx": midx, "gender": gender, "number": number,
            "name_gender": name_gender, "sent_role_rank": role_rank,
            "is_subject": (role_rank == 0), "span_toks": [head]}


def _selftest_memory_roundtrips_and_bounds() -> None:
    """The genuine HD event memory round-trips its AGENT and stays Cowan-4 bounded."""
    mem = EventMemory(n_dim=EVENT_N_DIM, capacity=4, fanout=2, seed=1)
    agents = ["anna", "bella", "cara", "dora", "ella", "fira"]
    for i, a in enumerate(agents):
        mem.push_event(a, ("bob" if i % 2 else None), sent_idx=i)
    assert len(mem.cf.active) <= 4, "focus grew past Cowan-4 capacity"
    focus = mem.focus_events()          # DIRECT (in-focus) event bundles only
    assert focus, "no direct events in focus"
    ok = 0
    for g, vec in focus:
        sym, _ = mem.query_bundle(vec, "AGENT")
        if sym == mem.event_meta[g]["agent"]:
            ok += 1
    assert ok == len(focus), (
        "in-focus HD event memory did not round-trip AGENT cleanly (ok=%d/%d)"
        % (ok, len(focus)))


def _selftest_query_off_reproduces_parent() -> None:
    """query_memory=False reproduces SceneProtagonistReader (local-window) bit-for-bit."""
    from hdlab.coref import build_pronoun_targets
    from hdlab.scene_segment import SceneProtagonistReader

    # Two fem characters + cross-sentence pronouns; a fixed-window scene layout.
    mentions = []
    mi = 0
    mentions.append(_mk("anna", 1, False, 0, mi, "fem", 0, name_gender="fem")); mi += 1
    mentions.append(_mk("bella", 2, False, 1, mi, "fem", 0, name_gender="fem")); mi += 1
    mentions.append(_mk("anna", 1, False, 2, mi, "fem", 0, name_gender="fem")); mi += 1
    mentions.append(_mk("she", 1, True, 3, mi, "fem", 0)); mi += 1     # gold=anna
    mentions.append(_mk("bella", 2, False, 4, mi, "fem", 0, name_gender="fem")); mi += 1
    mentions.append(_mk("she", 2, True, 5, mi, "fem", 0)); mi += 1     # gold=bella
    targets = build_pronoun_targets(mentions)
    n_sents = max(m["sent_idx"] for m in mentions) + 1
    scene_ids = [i // 5 for i in range(n_sents)]

    parent = SceneProtagonistReader()
    base = parent.resolve_stream(mentions, targets, prefer_topical=True, per_scene=True,
                                 scene_ids=scene_ids, topical_mode="rolemass")
    ecr = EventCentralityReader(graded_pick=False)   # incumbent fallback == the parent bit-for-bit
    off = ecr.resolve_stream(mentions, targets, scene_ids=scene_ids,
                             topical_mode="rolemass", query_memory=False)
    assert len(base) == len(off) == len(targets), "record count mismatch"
    for b, o in zip(base, off):
        assert b["resolved_cluster"] == o["resolved_cluster"], (
            "query-OFF diverged from parent local-window: base=%s off=%s"
            % (b["resolved_cluster"], o["resolved_cluster"]))
        assert b["attempted"] == o["attempted"], "attempt divergence"


def _selftest_event_role_beats_recency_when_structure_decisive() -> None:
    """A constructed case where AGENT-structure and RECENCY disagree: the protagonist ANNA
    is the AGENT of the recent events; a distractor BELLA is only the most-recent PATIENT.
    event_role must pick ANNA (agent-central); recency must pick BELLA (in the newest event);
    the memory query must CHANGE the decision vs the local-window base."""
    from hdlab.coref import build_pronoun_targets

    # anna is the AGENT of the 3 OLDER events (the protagonist that drives the action);
    # bella is the AGENT of only the single NEWEST event. event_role -> anna (role-central);
    # recency -> bella (newest event). gold = anna.
    mentions = []
    mi = 0
    mentions.append(_mk("anna", 1, False, 0, mi, "fem", 0, name_gender="fem")); mi += 1
    mentions.append(_mk("anna", 1, False, 1, mi, "fem", 0, name_gender="fem")); mi += 1
    mentions.append(_mk("anna", 1, False, 2, mi, "fem", 0, name_gender="fem")); mi += 1
    mentions.append(_mk("bella", 2, False, 2, mi, "fem", 1, name_gender="fem")); mi += 1  # obj
    mentions.append(_mk("bella", 2, False, 3, mi, "fem", 0, name_gender="fem")); mi += 1  # newest subj
    mentions.append(_mk("she", 1, True, 4, mi, "fem", 0)); mi += 1     # gold=anna (protagonist)
    targets = build_pronoun_targets(mentions)
    assert len(targets) == 1
    n_sents = max(m["sent_idx"] for m in mentions) + 1
    scene_ids = [i // 5 for i in range(n_sents)]

    ecr = EventCentralityReader(graded_pick=False)   # exercise the incumbent EC memory tie-break (fallback)
    ev = ecr.resolve_stream(mentions, targets, scene_ids=scene_ids, topical_mode="rolemass",
                            query_memory=True, centrality_mode="event_role",
                            glass_box_limit=4)
    rc = ecr.resolve_stream(mentions, targets, scene_ids=scene_ids, topical_mode="rolemass",
                            query_memory=True, centrality_mode="recency", glass_box_limit=4)
    assert ev[0]["resolved_head"] == "anna", (
        "event_role must pick agent-central anna, got %s" % ev[0]["resolved_head"])
    assert rc[0]["resolved_head"] == "bella", (
        "recency must pick newest-event-agent bella, got %s" % rc[0]["resolved_head"])
    assert ev[0]["correct"] is True and rc[0]["correct"] is False
    # DECISION-LOAD-BEARING: the recency query CHANGED the decision vs the local-window base
    # (proves the memory query drives resolve(); base picks anna by mass, recency overrides).
    assert any(r["mem_changed"] for r in rc), "recency query never changed the decision"


def _selftest_graded_pick_default_on_prefers_recent() -> None:
    """The DEFAULT reader (graded_pick=True) uses the PINNED graded ACT-R pick (recency load-bearing):
    with two same-gender candidates where the RECENT antecedent differs from the incumbent rolemass
    subject-mass pick, the default resolves to the recency-favored candidate and DIFFERS from the
    graded_pick=False incumbent. Proves the graded pick is on by default and is decision-driving."""
    from hdlab.coref import build_pronoun_targets

    # anna is the high-MASS early subject (3 subject mentions); bella is the SINGLE most-recent subject.
    # rolemass (incumbent, NO recency) -> anna (mass); graded ACT-R (recency) -> bella (recent). gold=bella.
    mentions = []
    mi = 0
    mentions.append(_mk("anna", 1, False, 0, mi, "fem", 0, name_gender="fem")); mi += 1
    mentions.append(_mk("anna", 1, False, 1, mi, "fem", 0, name_gender="fem")); mi += 1
    mentions.append(_mk("anna", 1, False, 2, mi, "fem", 0, name_gender="fem")); mi += 1
    mentions.append(_mk("bella", 2, False, 3, mi, "fem", 0, name_gender="fem")); mi += 1  # most-recent subj
    mentions.append(_mk("she", 2, True, 4, mi, "fem", 0)); mi += 1                        # gold=bella (recent)
    targets = build_pronoun_targets(mentions)
    n_sents = max(m["sent_idx"] for m in mentions) + 1
    scene_ids = [i // 5 for i in range(n_sents)]

    default_reader = EventCentralityReader()                     # graded_pick default ON
    assert default_reader.graded_pick is True, "graded_pick must default ON"
    on = default_reader.resolve_stream(mentions, targets, scene_ids=scene_ids,
                                       topical_mode="rolemass", query_memory=True,
                                       centrality_mode="event_role")
    off = EventCentralityReader(graded_pick=False).resolve_stream(
        mentions, targets, scene_ids=scene_ids, topical_mode="rolemass",
        query_memory=True, centrality_mode="event_role")
    assert on[0]["resolved_head"] == "bella", (
        "default graded pick must prefer the RECENT antecedent bella, got %s" % on[0]["resolved_head"])
    assert off[0]["resolved_head"] == "anna", (
        "graded_pick=False incumbent must keep the mass pick anna, got %s" % off[0]["resolved_head"])


def _selftest_unified_referent_routes_and_resolves() -> None:
    """unified_referent=True routes resolve_stream to the DRT file-change unified referent: name variants
    ("Elizabeth Bennet"/"Elizabeth") share ONE card and the pronoun resolves to the gn-compatible referent;
    the flag OFF is byte-identical to the landed graded_pick reader (the default path is untouched)."""
    from hdlab.coref import build_pronoun_targets

    def M(head, cluster, is_pron, sent, midx, gender, rank, span_toks, name_gender=None, number="singular"):
        return {"head": head, "cluster": cluster, "is_pronoun": is_pron, "sent_idx": sent,
                "midx": midx, "gender": gender, "number": number, "name_gender": name_gender,
                "sent_role_rank": rank, "is_subject": rank == 0, "span_toks": span_toks}

    ms = []
    i = 0
    ms.append(M("bennet", 1, False, 0, i, None, 0, ["Elizabeth", "Bennet"], name_gender="fem")); i += 1
    ms.append(M("darcy", 2, False, 1, i, None, 0, ["Darcy"], name_gender="masc")); i += 1
    ms.append(M("elizabeth", 1, False, 2, i, None, 0, ["Elizabeth"], name_gender="fem")); i += 1  # variant -> same card
    ms.append(M("she", 1, True, 3, i, "fem", 0, ["she"])); i += 1                                  # gold cluster 1
    targets = build_pronoun_targets(ms)
    assert len(targets) == 1, "expected one target"
    scene_ids = [0, 0, 0, 0]

    uni = EventCentralityReader(graded_pick=True, unified_referent=True).resolve_stream(
        ms, targets, scene_ids=scene_ids, topical_mode="rolemass")
    assert len(uni) == 1, "one record per target"
    assert uni[0]["correct"] is True, "unified must resolve she -> Elizabeth (fem), got %r" % uni[0]

    # OFF == the default landed reader, bit-for-bit (the flag default changes nothing)
    off = EventCentralityReader(graded_pick=True, unified_referent=False).resolve_stream(
        ms, targets, scene_ids=scene_ids, topical_mode="rolemass",
        query_memory=True, centrality_mode="event_role")
    base = EventCentralityReader(graded_pick=True).resolve_stream(
        ms, targets, scene_ids=scene_ids, topical_mode="rolemass",
        query_memory=True, centrality_mode="event_role")
    for a, b in zip(off, base):
        assert a["resolved_cluster"] == b["resolved_cluster"] and a["correct"] == b["correct"], "OFF path drift"


def _run_all_selftests() -> dict:
    _selftest_memory_roundtrips_and_bounds()
    _selftest_query_off_reproduces_parent()
    _selftest_event_role_beats_recency_when_structure_decisive()
    _selftest_graded_pick_default_on_prefers_recent()
    _selftest_unified_referent_routes_and_resolves()
    return {"n_dim": EVENT_N_DIM, "agent_w": AGENT_W, "patient_w": PATIENT_W, "graded_pick_default": True,
            "unified_referent_default": False,
            "reuse": ["SceneProtagonistReader", "EventBundleCodec", "ChunkedFocus", "graded_coref_pick",
                      "unified_referent"]}


if __name__ == "__main__":
    r = _run_all_selftests()
    print("[event_centrality_coref selftest] PASS %s" % r)
