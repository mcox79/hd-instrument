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

# Event-role centrality weights (AGENT drives the event > PATIENT); glass-box constants.
AGENT_W = 2.0
PATIENT_W = 1.0
EVENT_ROLES = ("AGENT", "PATIENT")
EVENT_N_DIM = 4096          # round-trips cleanly at Cowan-4 load (29511 capacity signature)


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
    the decision-change rate = memory is decision-driving."""

    def __init__(self, *, n_dim: int = EVENT_N_DIM, capacity: int = 4, fanout: int = 2,
                 mem_seed: int = 0, **kw) -> None:
        super().__init__(**kw)
        self._n_dim = int(n_dim)
        self._capacity = int(capacity)
        self._fanout = int(fanout)
        self._mem_seed = int(mem_seed)
        self.n_glass_kept = 0

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
    ecr = EventCentralityReader()
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

    ecr = EventCentralityReader()
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


def _run_all_selftests() -> dict:
    _selftest_memory_roundtrips_and_bounds()
    _selftest_query_off_reproduces_parent()
    _selftest_event_role_beats_recency_when_structure_decisive()
    return {"n_dim": EVENT_N_DIM, "agent_w": AGENT_W, "patient_w": PATIENT_W,
            "reuse": ["SceneProtagonistReader", "EventBundleCodec", "ChunkedFocus"]}


if __name__ == "__main__":
    r = _run_all_selftests()
    print("[event_centrality_coref selftest] PASS %s" % r)
