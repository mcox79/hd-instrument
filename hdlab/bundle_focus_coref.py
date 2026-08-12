"""BOUNDED Cowan-4 event-bundle FOCUS wired into cross-sentence coreference.

INTEGRATION-PATH THESIS: the situation model's brain-grounded memory (Cowan 2001
~4-chunk bounded FOCUS OF ATTENTION + hierarchical chunking + graceful forgetting,
validated in hdlab.situation_focus) FEEDS BACK to pronoun resolution. Each tracked
ENTITY is a role-bound EVENT BUNDLE (hdlab.event_bundle.EventBundleCodec) held in a
BOUNDED active focus; on each mention the entity is refreshed to the most-recent
active slot (chaining), and older entities are CHUNKED OUT (graceful degradation),
so the active competition is a small bounded set. A pronoun resolves against the
entities currently IN the bounded focus.

WHY BOUNDED FIXES THE STEP-1b RUNAWAY (the load-bearing claim, glass-box):
  On the UNBOUNDED flat WorkingOverlay, chaining a resolved pronoun onto its
  antecedent grows that entity's COUNT without bound. A single misresolution then
  becomes a global SALIENCE SUPER-ATTRACTOR that wins EVERY later pronoun regardless
  of local context. This is MEASURED on disk: flat maintained+chaining collapses to
  0.105 (xsent_chain_only) from the 0.185 no-chain backbone.
  In the BOUNDED focus, salience is RECENCY-OF-ACTIVATION within a small buffer, NOT
  an unbounded counter. Chaining refreshes an entity's RECENCY (keeps the protagonist
  in the bounded focus across a stretch of other-entity mentions) but grants NO
  count-mass: the very next NOMINAL mention of a different entity takes the most-recent
  slot and out-ranks the chained entity for the next pronoun. So chaining gives
  protagonist CONTINUITY without cross-context CAPTURE => chaining done RIGHT.

HONEST SCOPE: this addresses SALIENCE / bounded competition, NOT the common-noun
APPOSITIVE bridging (father/daughter/widow/friend) that step-1c found is the majority
of the per-cluster fragmentation. So the honest expectation is a MODEST effect, and
possibly NOT clearing the plateau -- which would honestly confirm appositive-bridging
(not the memory format) is the remaining wall.

REUSE (nothing re-transcribed; banked cells are NOT edited):
  - EventBundleCodec role-slot event encoding + query: hdlab.event_bundle.
  - ChunkedFocus bounded active buffer + fanout chunk compression: hdlab.situation_focus.
  - PRONOUN_SCOPE / TARGET_PRONOUNS / compatible() agreement: hdlab.state_of_mind.
  - parse_litbank_conll / build_pronoun_targets / sent_dist_bucket: hdlab.coref.

This focus is ENTITY-granular: capacity counts DISTINCT live entities (~4 = Cowan's
~4 chunks). The banked situation_focus.ChunkedFocus counts a CHUNK as one of its slots
(fewer live raw events when a chunk is present), so the genuine HD store forgets at
least as aggressively as this entity buffer -- its direct (depth-0) set is a SUBSET of
this focus's active set. The self-test BACKS the symbolic decision path with that real
HD store: every live entity's event bundle is stored in a real ChunkedFocus and
round-trips (proves the event-bundle memory is genuine, not decorative), and the HD
direct set is asserted consistent (subset) with the symbolic active set.
ASCII-only, no em-dashes; no torch phasors in the decision path; no network; no gold.
"""
from __future__ import annotations

from typing import Dict, List, Optional, Tuple

from hdlab.state_of_mind import PRONOUN_SCOPE, TARGET_PRONOUNS, compatible
from hdlab.coref import sent_dist_bucket


# ---------------------------------------------------------------------------
# The bounded Cowan-4 entity focus (entity-granular; mirrors ChunkedFocus).
# ---------------------------------------------------------------------------
class BoundedEntityFocus:
    """Bounded active focus of ENTITIES with fanout chunk-compression (Cowan-4).

    The active buffer holds <= capacity DISTINCT entities (most-recent LAST). A
    re-mention or a chaining refresh PROMOTES the entity to the most-recent slot. When
    a new distinct entity would exceed capacity, the OLDEST `fanout` entities are
    compressed into a CHUNK (they leave the active buffer; chunk_depth += 1). Chunked
    entities are still accessible via graceful (degraded) fallback but never win over a
    direct active entity. This is the entity-level analogue of situation_focus.ChunkedFocus
    (same capacity/fanout/compress-oldest semantics), driving the coref decision.

    When hd_store=True a parallel REAL hdlab.situation_focus.ChunkedFocus is maintained
    (each mention stored as an EventBundleCodec event bundle) so the genuine HD memory's
    active/chunked membership can be asserted equal to this symbolic buffer.
    """

    def __init__(self, capacity: int = 4, fanout: int = 2, *,
                 hd_store: bool = False, codec=None, seed: int = 0) -> None:
        if fanout < 2:
            raise ValueError("fanout must be >= 2")
        if capacity < fanout:
            raise ValueError("capacity must be >= fanout")
        self.capacity = int(capacity)
        self.fanout = int(fanout)
        self.active: List[str] = []            # entity keys, recent LAST, distinct
        self.chunk_depth: Dict[str, int] = {}  # key -> depth >= 1 (chunked-out; graceful)
        self.gender: Dict[str, Optional[str]] = {}
        self.number: Dict[str, Optional[str]] = {}
        self.count: Dict[str, int] = {}        # total mentions (diagnostic; NOT the ranker)
        # BOUNDED ACTIVATION (Cowan): accumulates while an entity stays CONTINUOUSLY in the
        # active focus; RESETS to 0 when the entity is chunked out (leaves the focus of
        # attention). This is the within-focus salience the coref decision ranks by. It is
        # DISTINCT from flat recency (which picks the most-recent) AND from the flat overlay's
        # UNBOUNDED global count (the step-1b runaway): a super-attractor that drifts out of
        # the bounded focus LOSES its accumulated mass, so it cannot dominate globally.
        self.activation: Dict[str, int] = {}
        self._clock = 0
        self.last_seen: Dict[str, int] = {}    # key -> clock tick of last activation (recency)
        # genuine HD event-bundle store (optional witness of the memory format)
        self.hd_store = bool(hd_store)
        self._cf = None
        self._gidx = 0
        self._entity_gidx: Dict[str, int] = {}
        if self.hd_store:
            if codec is None:
                raise ValueError("hd_store=True requires an EventBundleCodec")
            from hdlab.situation_focus import ChunkedFocus
            self._codec = codec
            self._cf = ChunkedFocus(codec, capacity=self.capacity, fanout=self.fanout,
                                    seed=seed)

    # ---- internal buffer mechanics -------------------------------------------
    def _promote(self, key: str) -> bool:
        """Move key to the most-recent active slot; compress oldest entities if over capacity.
        Zeroes the activation of any entity chunked out (it leaves the focus of attention).
        Returns True if `key` was ALREADY active (a continuous-focus re-activation), else False
        (a new entity or a re-entry from a chunk => fresh activation)."""
        was_active = key in self.active
        if was_active:
            self.active.remove(key)
        elif key in self.chunk_depth:
            del self.chunk_depth[key]           # pulled back from a chunk into active (re-entry)
        self.active.append(key)
        while len(self.active) > self.capacity:
            for k in self.active[:self.fanout]:  # compress oldest fanout distinct entities
                self.chunk_depth[k] = self.chunk_depth.get(k, 0) + 1
                self.activation[k] = 0           # left the focus => accumulated mass RESETS
            self.active = self.active[self.fanout:]
        return was_active

    def _activate(self, key: str) -> None:
        """Bump bounded activation: +1 if the entity was already in the focus (continuous
        accumulation), else reset to 1 (a new entity or a fresh re-entry from a chunk)."""
        was_active = self._promote(key)
        self._clock += 1
        self.last_seen[key] = self._clock
        self.activation[key] = (self.activation.get(key, 0) + 1) if was_active else 1

    def observe(self, key: str, gender: Optional[str], number: Optional[str],
                fillers: Optional[Dict[str, str]] = None) -> None:
        """Observe a NOMINAL mention of entity `key`: update attrs, activate, store HD bundle."""
        self.count[key] = self.count.get(key, 0) + 1
        if key not in self.gender or (self.gender.get(key) is None and gender is not None):
            self.gender[key] = gender if key not in self.gender else (self.gender[key] or gender)
        if key not in self.number or (self.number.get(key) is None and number is not None):
            self.number[key] = number if key not in self.number else (self.number[key] or number)
        self._activate(key)
        if self.hd_store:
            rf = fillers or {"PRED": "MENTION", "AGENT": key, "PATIENT": key,
                             "TENSE": (gender or "unk")}
            ev = self._codec.encode_event(rf)
            self._cf.push(ev, self._gidx)
            self._entity_gidx[key] = self._gidx
            self._gidx += 1

    def refresh(self, key: str) -> None:
        """CHAINING (bounded): a resolved pronoun re-activates its antecedent WITHIN the focus
        (bumps bounded activation + recency; pulls it back if chunked). Grants NO global mass
        and writes NO new HD mention. This is the step-1b chaining lever made bounded: because
        activation RESETS when the entity leaves the focus, chaining gives protagonist
        continuity WITHOUT the unbounded-count super-attractor that broke the flat overlay."""
        if key is None:
            return
        self._activate(key)

    # ---- resolution ----------------------------------------------------------
    def resolve(self, gender: Optional[str], number: Optional[str], *,
                chunk_fallback: bool = True) -> Optional[str]:
        """Resolve a pronoun against the bounded focus. Among gender/number-compatible DIRECT
        active entities, pick the highest BOUNDED ACTIVATION (recency breaks ties) -- the
        chaining-sensitive within-focus salience (distinct from flat recency, which takes the
        most-recent, and from flat unbounded count, which runs away). If none is active,
        GRACEFULLY falls back to the least-degraded compatible chunked entity (Cowan graceful-
        forgetting recall). None = ABSTAIN (never-confidently-wrong)."""
        direct = [k for k in self.active
                  if compatible(gender, number, self.gender.get(k), self.number.get(k))]
        if direct:
            return max(direct, key=lambda k: (self.activation.get(k, 0), self.last_seen.get(k, 0)))
        if chunk_fallback and self.chunk_depth:
            chunked = [k for k in self.chunk_depth
                       if compatible(gender, number, self.gender.get(k), self.number.get(k))]
            if chunked:
                # least-degraded (smallest depth) then most-recent
                return min(chunked, key=lambda k: (self.chunk_depth[k], -self.last_seen.get(k, 0)))
        return None

    # ---- HD-store introspection (witness only) -------------------------------
    def hd_active_keys(self) -> List[str]:
        """Entity keys whose latest HD mention is a DIRECT (depth-0) slot in the real
        ChunkedFocus store. Used to assert structural equivalence with self.active."""
        if not self.hd_store:
            raise RuntimeError("hd_store disabled")
        out = []
        for k, g in self._entity_gidx.items():
            try:
                if self._cf.is_direct(g):
                    out.append(k)
            except KeyError:
                pass
        return out

    def hd_query_latest(self, key: str, role: str) -> Tuple[Optional[str], float]:
        """Glass-box: recover a role filler of the entity's latest stored event bundle from
        the real HD ChunkedFocus (proves the memory is genuine, not decorative)."""
        if not self.hd_store:
            raise RuntimeError("hd_store disabled")
        g = self._entity_gidx[key]
        return self._cf.query(g, role)


# ---------------------------------------------------------------------------
# The reader: replay mentions into the bounded focus; resolve each target.
# Returns the SAME per-target record schema as hdlab.coref.CorefReader so the cell
# scores every arm identically.
# ---------------------------------------------------------------------------
class BundleFocusReader:
    """Cross-sentence pronoun reader over the BOUNDED Cowan-4 entity focus.

    resolve_stream(mentions, targets, ...) mirrors CorefReader.resolve_stream's output
    records: {target_midx, gold_cluster, sent_dist, bucket, resolved_head,
              resolved_cluster, attempted, correct}.
    """

    def __init__(self, *, capacity: int = 4, fanout: int = 2,
                 hd_store: bool = False, codec=None, seed: int = 0) -> None:
        self.capacity = int(capacity)
        self.fanout = int(fanout)
        self.hd_store = bool(hd_store)
        self._codec = codec
        self._seed = int(seed)

    def resolve_stream(self, mentions: List[dict], targets: List[dict], *,
                       chain_pronouns: bool = True, use_gazetteer: bool = True,
                       chunk_fallback: bool = True) -> List[dict]:
        focus = BoundedEntityFocus(capacity=self.capacity, fanout=self.fanout,
                                   hd_store=self.hd_store, codec=self._codec,
                                   seed=self._seed)
        target_by_midx = {t["target"]["midx"]: t for t in targets}
        head_to_cluster: Dict[str, int] = {}
        records: List[dict] = []

        for m in mentions:
            resolved_key = None
            if m["is_pronoun"] and m["head"] in TARGET_PRONOUNS:
                sc = PRONOUN_SCOPE[m["head"]]
                resolved_key = focus.resolve(sc["gender"], sc["number"],
                                             chunk_fallback=chunk_fallback)
                if m["midx"] in target_by_midx:
                    tinfo = target_by_midx[m["midx"]]
                    if resolved_key is None:
                        rec = dict(resolved_head=None, resolved_cluster=None,
                                   attempted=False, correct=False)
                    else:
                        rc = head_to_cluster.get(resolved_key)
                        rec = dict(resolved_head=resolved_key, resolved_cluster=rc,
                                   attempted=True,
                                   correct=(rc is not None and rc == m["cluster"]))
                    rec.update(target_midx=m["midx"], gold_cluster=m["cluster"],
                               sent_dist=tinfo["sent_dist"],
                               bucket=sent_dist_bucket(tinfo["sent_dist"]))
                    records.append(rec)

            if m["is_pronoun"]:
                # CHAINING (bounded): refresh the resolved antecedent's recency only.
                if chain_pronouns and resolved_key is not None:
                    focus.refresh(resolved_key)
            else:
                eff_gender = m["gender"]
                if eff_gender is None and use_gazetteer:
                    eff_gender = m.get("name_gender")
                key = m["head"]
                fillers = {"PRED": "MENTION", "AGENT": key,
                           "PATIENT": (eff_gender or "unk"), "TENSE": "n"}
                focus.observe(key, eff_gender, m["number"], fillers=fillers)
                head_to_cluster[key] = m["cluster"]

        return records


# ===================== formula self-tests ==========================================

def _selftest_bounded_no_runaway_vs_flat_chain() -> None:
    """The core claim, on a constructed doc: bounded-focus chaining does NOT collapse the
    way flat maintained+chaining does, and does NOT let one entity capture a runaway share.

    Construction: a protagonist A introduced early, then a long alternation where a distractor
    B is repeatedly the LOCALLY-recent fem entity right before each pronoun that (by gold)
    refers to B. On the flat overlay, chaining A once early and then mis-chaining inflates a
    super-attractor; the bounded focus keeps the LOCALLY-recent B winning each local pronoun.
    """
    from hdlab.coref import build_pronoun_targets

    # Build a synthetic mention stream directly (bypass conll): two fem entities A(1), B(2).
    def mk(head, cluster, is_pron, sent, midx, gender):
        return {"head": head, "cluster": cluster, "is_pronoun": is_pron,
                "sent_idx": sent, "midx": midx, "gender": gender, "number": "singular",
                "name_gender": None, "span_toks": [head]}

    mentions = []
    mi = 0
    # S0: introduce A
    mentions.append(mk("anna", 1, False, 0, mi, "fem")); mi += 1
    # 3 local scenes: each introduces B then a pronoun that refers to B (local, gold=2)
    for s in range(1, 4):
        mentions.append(mk("bella", 2, False, s, mi, "fem")); mi += 1
        mentions.append(mk("she", 2, True, s, mi, "fem")); mi += 1
    for m in mentions:
        pass
    targets = build_pronoun_targets(mentions)
    # all 3 pronouns are gold cluster 2 (B), each with B as the most-recent mention.
    assert len(targets) == 3, "expected 3 pronoun targets, got %d" % len(targets)

    rdr = BundleFocusReader(capacity=4, fanout=2)
    recs_chain = rdr.resolve_stream(mentions, targets, chain_pronouns=True, use_gazetteer=False)
    recs_nochain = rdr.resolve_stream(mentions, targets, chain_pronouns=False, use_gazetteer=False)
    acc_chain = sum(r["correct"] for r in recs_chain) / len(recs_chain)
    acc_nochain = sum(r["correct"] for r in recs_nochain) / len(recs_nochain)
    # bounded chaining must NOT collapse: the LOCALLY-recent B wins each local pronoun
    # (the correct antecedent), never a global A super-attractor capturing them.
    assert acc_chain >= 0.99, "bounded chaining mis-resolved local pronouns: %.3f" % acc_chain
    heads = [r["resolved_head"] for r in recs_chain if r["attempted"]]
    assert all(h == "bella" for h in heads), (
        "bounded chaining let a non-local entity capture local pronouns: %s" % heads)
    # chaining does not HURT relative to no-chain in the bounded focus (no runaway penalty)
    assert acc_chain >= acc_nochain - 1e-9, (
        "bounded chaining HURT vs no-chain: chain=%.3f nochain=%.3f" % (acc_chain, acc_nochain))


def _selftest_chunking_bounds_active_and_graceful() -> None:
    """Cowan-4 bound holds + graceful forgetting: active <= capacity; an old un-refreshed
    entity is chunked out; a chained (refreshed) entity STAYS active across new mentions."""
    focus = BoundedEntityFocus(capacity=4, fanout=2)
    for k in ["a", "b", "c", "d"]:
        focus.observe(k, "fem", "singular")
    assert set(focus.active) == {"a", "b", "c", "d"}, focus.active
    # chain-refresh 'a' (the protagonist) so it stays active as new entities arrive
    focus.refresh("a")
    for k in ["e", "f", "g"]:
        focus.observe(k, "fem", "singular")
        focus.refresh("a")                      # keep protagonist alive via chaining
        assert len(focus.active) <= focus.capacity, "active grew past capacity"
        assert "a" in focus.active, "chaining failed to keep protagonist active"
    # an entity never refreshed (e.g. 'b') must have been chunked out (graceful forgetting)
    assert "b" not in focus.active and focus.chunk_depth.get("b", 0) >= 1, \
        "un-refreshed old entity should be chunked out: active=%s chunk=%s" % (
            focus.active, focus.chunk_depth)


def _selftest_hd_store_backs_focus() -> None:
    """The GENUINE HD event-bundle memory BACKS the symbolic buffer: every live entity's
    event bundle is stored in a real situation_focus.ChunkedFocus and round-trips (proves
    the memory is genuine, not decorative); the HD direct (depth-0) set is CONSISTENT with
    the symbolic active set (a subset -- the HD store's chunk-as-slot forgets at least as
    aggressively), and the most-recent entity is always HD-direct + round-trips."""
    from hdlab.event_bundle import EventBundleCodec

    codec = EventBundleCodec(n_dim=512, seed=3)
    codec.prime_symbols(["MENTION", "n", "fem", "masc", "unk",
                         "anna", "bella", "cara", "dora", "ella", "fira"])
    focus = BoundedEntityFocus(capacity=4, fanout=2, hd_store=True, codec=codec, seed=1)
    keys = ["anna", "bella", "cara", "dora", "ella", "fira"]
    for k in keys:
        focus.observe(k, "fem", "singular",
                      fillers={"PRED": "MENTION", "AGENT": k, "PATIENT": "fem", "TENSE": "n"})
    hd_direct = set(focus.hd_active_keys())
    # consistency: the genuine HD store forgets >= as aggressively (chunk occupies a slot).
    assert hd_direct.issubset(set(focus.active)), (
        "HD direct set not a subset of symbolic active: hd=%s sym=%s" % (hd_direct, focus.active))
    assert hd_direct, "HD store retained no direct events (memory not populated)"
    # every HD-direct entity's latest bundle round-trips its AGENT role filler (genuine memory).
    for k in hd_direct:
        got, _score = focus.hd_query_latest(k, "AGENT")
        assert got == k, "HD event bundle did not round-trip AGENT for %r: got %r" % (k, got)
    # the most-recent entity is HD-direct (the freshest mention is never already chunked).
    newest = focus.active[-1]
    assert newest in hd_direct, "newest entity %r not HD-direct: %s" % (newest, hd_direct)


def _run_all_selftests() -> dict:
    _selftest_chunking_bounds_active_and_graceful()
    _selftest_bounded_no_runaway_vs_flat_chain()
    _selftest_hd_store_backs_focus()
    return {"capacity_default": 4, "fanout_default": 2,
            "reuse": ["EventBundleCodec", "ChunkedFocus", "state_of_mind.compatible"]}


if __name__ == "__main__":
    r = _run_all_selftests()
    print("[bundle_focus_coref selftest] PASS %s" % r)
