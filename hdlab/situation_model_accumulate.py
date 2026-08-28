"""Per-entity situation-model register: FHRR bind(role, event-slot) accumulated via
bundle, decoded via unbind + cleanup argmax.

Promotion of the VET-CONFIRMED accumulate-vs-overwrite organ (atom 29609,
experiments/exp_situation_model_accumulate_vs_overwrite_v1.py ARM B, capability_registry.jsonl
id situation_model_accumulate_register_organ) into a reusable hdlab/ module. Same algebra,
same decode as the validated cell -- reimplemented on torch complex64 tensors via the
canonical hdlab.binding.bind/unbind + hdlab.bundling.bundle primitives (the experiment cell
used bare numpy at its declared numpy/CPU pre-reg scope; this module follows CLAUDE.md's
torch-tensor-at-API-boundary convention instead, not a mechanism change).

ACCUMULATE (default, validated: accumulate=1.0000 vs overwrite=0.4600 vs floor=0.2100 on
real McGuffey multiclause entity-tracking gold, atom 29609, chain length 2-3): each entity's
register is the FHRR-bundle of ALL its (role, event-slot) bindings -- Kintsch C-I / Zwaan
multi-event indexing. Bounded by bundling capacity beyond the validated chain-length scope.

OVERWRITE (reserved mode, per Finding 3 of notes/wire_extraction_wm_real_text_entity_
tracking_design_2026-08-02.md): each entity's register is REPLACED by only the newest
binding -- genuine state-replacement (e.g. "the cup is now empty"), not multi-event history.
Structurally recovers only the last-written event (the Finding-3 too-simple negative control).
"""
from __future__ import annotations

import math
from typing import Dict, List, Tuple

import torch

from . import binding, bundling


def unit_phase_vec(d: int, generator: torch.Generator) -> torch.Tensor:
    """Random unit-magnitude complex64 vector of dim d (FHRR atomic symbol)."""
    theta = torch.rand(d, generator=generator) * (2.0 * math.pi)
    return torch.polar(torch.ones(d), theta).to(torch.complex64)


def cleanup_argmax(
    readback: torch.Tensor, vocab: Dict[str, torch.Tensor]
) -> Tuple[str, Dict[str, float]]:
    """FHRR cleanup readout: argmax over vocab of Re(sum(conj(vocab_v) * readback)) / d."""
    d = readback.shape[0]
    scores: Dict[str, float] = {}
    for name, v in vocab.items():
        scores[name] = float(torch.real(torch.sum(torch.conj(v) * readback))) / d
    best = max(scores.items(), key=lambda kv: kv[1])[0]
    return best, scores


def cleanup_set(
    readback: torch.Tensor, vocab: Dict[str, torch.Tensor], rel_margin: float = 0.5
) -> Tuple[List[str], Dict[str, float]]:
    """FHRR SET readout = CA3 context-cued reactivation of the whole event set bound at a context,
    instead of the single argmax. Returns EVERY vocab symbol whose cleanup score clears a margin
    relative to the peak (score >= rel_margin * peak, score > 0), sorted by score descending.

    Landed 2026-08-27 from the integrated `the_entity_store_is_a_dense_bundle_that_fans` (SOLVED/EXCELLENT,
    owner-DONE; witnesses test_entity_store_fan.py 21/21 + test_entity_store_frontier.py 26/26, re-verified
    FIRST-HAND). The measured LitBank "fan" (decode accuracy 0.945@few-events -> 0.657@many, slope 0.288) is
    NOT superposition blur: unique-(entity,slot) addresses decode at 1.0000 at EVERY load level, and the dense
    bundle keeps the information (a top-m read recovers the co-slot set at ~1.0). The fan is an ARGMAX-vs-SET
    readout artifact on a COARSE key where 22.7% of (entity,sentence) addresses hold >1 distinct verb (a busy
    character does several things per context). SET-return alone flattens the slope 0.288 -> 0.0003 (CI-sep),
    with an info-free shuffled-order twin LOSING (1.000 vs 0.502). This is the brain's read: CA3 pattern
    completion reactivates the whole set bound to the reinstated context (Nakazawa 2002; Bramao 2022).

    `rel_margin` is a DEPLOYABLE threshold (OUR-INVENTION, not brain-pinned): the pinned part is set-vs-argmax;
    the maximally faithful stop is the CMR race-to-stop (self-terminating, no oracle set size) validated in the
    frontier (F1 0.928 vs fixed-k 0.781) -- a follow-on. Paired brain-faithful fix (caller-side): a FINER
    conjunctive temporal key (within-sentence order = TCM drift) so co-context actions get distinct addresses;
    it flattens the fan equally and is where the finer index carries the specific-action info (twin loses)."""
    d = readback.shape[0]
    scores: Dict[str, float] = {}
    for name, v in vocab.items():
        scores[name] = float(torch.real(torch.sum(torch.conj(v) * readback))) / d
    peak = max(scores.values()) if scores else 0.0
    thresh = rel_margin * peak
    keep = sorted((r for r, s in scores.items() if s > 0.0 and s >= thresh), key=lambda r: -scores[r])
    return keep, scores


class AccumulateRegister:
    """FHRR situation-model register: bind(role_vec, event_idx_vec) per event, accumulate via bundle.

    overwrite=False (default): register = bundle of ALL bound events for the entity (validated
    ACCUMULATE organ, atom 29609). overwrite=True: register = only the most recently bound
    event (reserved OVERWRITE / state-replacement mode, Finding 3).
    """

    def __init__(
        self,
        role_vocab: List[str],
        d: int,
        generator: torch.Generator,
        max_event_slots: int = 8,
        overwrite: bool = False,
    ) -> None:
        self.role_vocab = list(role_vocab)
        self.d = int(d)
        self.overwrite = bool(overwrite)
        self.max_event_slots = int(max_event_slots)
        self.role_vecs: Dict[str, torch.Tensor] = {
            r: unit_phase_vec(self.d, generator) for r in self.role_vocab
        }
        self.idx_vecs: List[torch.Tensor] = [
            unit_phase_vec(self.d, generator) for _ in range(self.max_event_slots)
        ]
        self._events: Dict[str, List[torch.Tensor]] = {}

    def add_event(self, entity: str, role: str, event_idx: int) -> None:
        """Bind role_vec to idx_vec at event_idx; accumulate (bundle) or overwrite entity's register."""
        if role not in self.role_vecs:
            raise KeyError(f"unknown role {role!r}; known={self.role_vocab}")
        if not (0 <= event_idx < self.max_event_slots):
            raise ValueError(f"event_idx {event_idx} out of range [0, {self.max_event_slots})")
        bound = binding.bind(self.role_vecs[role], self.idx_vecs[event_idx])
        if self.overwrite:
            self._events[entity] = [bound]
        else:
            self._events.setdefault(entity, []).append(bound)

    def register(self, entity: str) -> torch.Tensor:
        """Entity's current register: bundle of all accumulated events, or the sole event if one."""
        events = self._events.get(entity)
        if not events:
            raise KeyError(f"no events recorded for entity {entity!r}")
        if len(events) == 1:
            return events[0]
        return bundling.bundle(torch.stack(events, dim=0))

    def decode(self, entity: str, event_idx: int) -> Tuple[str, Dict[str, float]]:
        """Unbind entity's register by event_idx's key, then cleanup-argmax over role_vocab."""
        reg = self.register(entity)
        readback = binding.unbind(reg, self.idx_vecs[event_idx])
        return cleanup_argmax(readback, self.role_vecs)

    def decode_set(self, entity: str, event_idx: int, rel_margin: float = 0.5) -> Tuple[List[str], Dict[str, float]]:
        """SET-return decode (CA3 context-cued reactivation): return ALL roles bound at (entity, event_idx)
        whose cleanup score clears the margin, not just the argmax. Flattens the addressing-collision fan where
        a coarse key holds >1 role (see cleanup_set). Additive / default-safe: decode() is unchanged."""
        reg = self.register(entity)
        readback = binding.unbind(reg, self.idx_vecs[event_idx])
        return cleanup_set(readback, self.role_vecs, rel_margin=rel_margin)

    def entities(self) -> List[str]:
        """Entity ids with at least one recorded event."""
        return list(self._events.keys())


def make_situation_register(
    role_vocab: List[str],
    d: int,
    generator: torch.Generator,
    max_event_slots: int = 8,
    backend: str = "multibank",
    n_banks: int = 8,
):
    """Backend-selectable factory for the situation-model entity-event register.

    WIRE-DON'T-ISLAND wire-point (2026-08-03, closing the WIRED_BUT_NOT_PIPELINE_REACHABLE
    gap on hdlab.situation_model_multibank.MultiBankAccumulateRegister, capability_registry
    id situation_model_multibank / working_memory_multibank_K_capacity): every active-pipeline
    caller that used to construct AccumulateRegister directly (tools/read_anne_glassbox_v2_
    honest_ledger.py, hdlab/self_improving_loop.py) should call this factory instead so the
    memory backend is chosen in ONE place.

    backend="multibank" (DEFAULT): returns MultiBankAccumulateRegister with n_banks=8 -- the
    validated config from experiments/exp_situation_model_multibank_capacity_v1.py
    (data/exp_situation_model_multibank_capacity_v1/metrics.json), which holds decode
    self-consistency >=0.999 at n_events=256/entity (multibank_8=0.9992) where the flat
    register degrades to 0.6547 at the same load. Strictly >= flat at every swept load in that
    cell (n_events in {64,96,128,192,256}: multibank_8 in [1.0000, 0.9992], flat in
    [0.9781, 0.6547]) -- there is no regime in the measured sweep where flat beats multibank_8,
    so multibank is a safe default, not a scale-vs-small-scale tradeoff.

    HONEST SCOPE: at current pilot scale (few events/entity, e.g. the Anne consolidated-only
    situation model, bundle-load ~2) multibank and flat decode IDENTICALLY (both saturate near
    1.0 -- see verification/verify_situation_model_multibank_dropin.py). Switching the default
    here is NOT claimed to lift current comprehension-pipeline accuracy; it is capacity-
    headroom future-proofing (book-scale event counts will hit the flat-bundle wall this fixes)
    PLUS making the validated-but-previously-unreachable multibank module actually pipeline-USED
    per the capability registry's WIRED_AND_PIPELINE_USED gate.

    backend="flat": returns the original AccumulateRegister(overwrite=False) -- kept available
    as an explicit opt-out so no caller is forced onto multibank; pass backend="flat" to
    reproduce prior behavior exactly (bit-identical to constructing AccumulateRegister directly
    with the same args, since this branch does exactly that).
    """
    if backend == "flat":
        return AccumulateRegister(role_vocab, d, generator, max_event_slots=max_event_slots)
    if backend == "multibank":
        # Deferred import: situation_model_multibank imports FROM this module
        # (cleanup_argmax/unit_phase_vec), so a module-level import here would be circular.
        from .situation_model_multibank import MultiBankAccumulateRegister
        return MultiBankAccumulateRegister(
            role_vocab, d, generator, max_event_slots=max_event_slots, n_banks=n_banks
        )
    raise ValueError(f"unknown backend {backend!r}; expected 'multibank' or 'flat'")


class CausalLinkRegister(AccumulateRegister):
    """Passage-level CAUSE/EFFECT link register (2026-08-02 comprehension-arc extension).

    Extends AccumulateRegister VERBATIM (same bind/unbind/bundle/cleanup_argmax chain,
    same ACCUMULATE-via-bundle organ validated at atom 29609) to bind EVENT-to-EVENT
    causal links instead of ENTITY-to-role links. The "entity" key becomes an event-slot
    index (as str); the "role_vocab" becomes the fixed 2-symbol meta-role set
    {CAUSE, EFFECT}; the thing bound as "event_idx" is the OTHER linked event's own
    idx_vec (reusing the existing idx_vecs vocabulary, no new vector class).

    add_causal_link(cause_idx, effect_idx) writes BOTH directions in one call:
      - entity=str(cause_idx) accumulates bind(CAUSE_vec, idx_vecs[effect_idx])
        ("this event's effect is <effect_idx>")
      - entity=str(effect_idx) accumulates bind(EFFECT_vec, idx_vecs[cause_idx])
        ("this event's cause is <cause_idx>")
    Multiple links sharing an entity (an event that causes >1 effect, or is caused by
    >1 event) bundle into that entity's register exactly as multi-event entity chains do
    in the base class -- this is the SAME capacity-bounded accumulate organ, not a new one.

    query_effect_of(cause_idx) / query_cause_of(effect_idx) decode by unbinding the
    entity's register with the ROLE vector (mirror of the base class's decode(), which
    unbinds by the EVENT key and cleanup-argmaxes the role; here we unbind by the ROLE
    key and cleanup-argmax the EVENT vocabulary) -- same primitives, reversed which side
    is treated as "key" vs "vocabulary to search," which is a valid symmetry of FHRR
    bind (elementwise complex multiply is commutative).
    """

    CAUSE_ROLE = "CAUSE"
    EFFECT_ROLE = "EFFECT"

    def __init__(self, d: int, generator: torch.Generator, max_event_slots: int) -> None:
        super().__init__(
            role_vocab=[self.CAUSE_ROLE, self.EFFECT_ROLE],
            d=d,
            generator=generator,
            max_event_slots=max_event_slots,
            overwrite=False,
        )
        # per-entity set of roles actually bound (an entity can be present in self._events
        # with ONLY an EFFECT fact and no CAUSE fact, or vice versa -- decode must not guess
        # against an unbound role; base class has no per-role bookkeeping, so track it here).
        self._roles_present: Dict[str, set] = {}
        # cause_idx,effect_idx -> +1/-1 (2026-08-10 WIQA causal-chain-loop extension, see
        # add_causal_link docstring). Plain Python side-dict, NOT bound into the FHRR algebra --
        # a +-1 scalar has nothing to cleanup; existence + index recovery is still done by the
        # unchanged bind/bundle/cleanup_argmax chain below.
        self._link_polarity: Dict[Tuple[int, int], int] = {}

    def add_causal_link(self, cause_idx: int, effect_idx: int, polarity: int = 1) -> None:
        """Bind event cause_idx -> has-effect -> effect_idx, and the reverse, in one write.

        polarity (2026-08-10 extension, exp_wiqa_causal_chain_loop_v1): +1 (default) or -1 --
        signed CAUSE/EFFECT bit for propagating a perturbation's direction along a multi-hop
        chain (does cause_idx increasing make effect_idx increase [+1] or decrease [-1]?).
        Stored as a plain scalar side-dict, not encoded via bind/bundle (there is nothing to
        "clean up" about a +-1 sign; the existing FHRR CAUSE/EFFECT existence+index-recovery
        chain is UNCHANGED). Additive-only: default polarity=1 reproduces prior unsigned
        call sites exactly (query_effect_of/query_cause_of behavior is bit-for-bit unchanged).
        """
        if polarity not in (1, -1):
            raise ValueError(f"polarity must be +1 or -1; got {polarity!r}")
        self.add_event(str(cause_idx), self.CAUSE_ROLE, effect_idx)
        self._roles_present.setdefault(str(cause_idx), set()).add(self.CAUSE_ROLE)
        self.add_event(str(effect_idx), self.EFFECT_ROLE, cause_idx)
        self._roles_present.setdefault(str(effect_idx), set()).add(self.EFFECT_ROLE)
        self._link_polarity[(int(cause_idx), int(effect_idx))] = int(polarity)

    def query_link_polarity(self, cause_idx: int, effect_idx: int) -> int:
        """Return the signed polarity of the cause_idx->effect_idx link (+1 or -1).

        Raises KeyError if this exact (cause_idx, effect_idx) link was never added via
        add_causal_link -- an honest "no signed fact known" rather than a spurious default.
        """
        return self._link_polarity[(int(cause_idx), int(effect_idx))]

    def _decode_linked_event(self, event_idx: int, role: str) -> Tuple[object, Dict[str, float]]:
        """Unbind event_idx's register by role_vecs[role]; cleanup-argmax over idx_vecs vocab.

        Returns (None, {}) if event_idx has no accumulated fact of this SPECIFIC role
        (honest "no link known" rather than a spurious chance-level guess against a role
        that was never bound at all).
        """
        entity = str(event_idx)
        if role not in self._roles_present.get(entity, set()):
            return None, {}
        reg = self.register(entity)
        readback = binding.unbind(reg, self.role_vecs[role])
        vocab = {str(i): v for i, v in enumerate(self.idx_vecs)}
        best, scores = cleanup_argmax(readback, vocab)
        return int(best), scores

    def query_effect_of(self, cause_idx: int) -> Tuple[object, Dict[str, float]]:
        """Decode the effect event linked to cause_idx (or (None, {}) if none recorded)."""
        return self._decode_linked_event(cause_idx, self.CAUSE_ROLE)

    def query_cause_of(self, effect_idx: int) -> Tuple[object, Dict[str, float]]:
        """Decode the cause event linked to effect_idx (or (None, {}) if none recorded)."""
        return self._decode_linked_event(effect_idx, self.EFFECT_ROLE)


class RelationRegister(AccumulateRegister):
    """Two-role (GOAL_ROLE/OUTCOME_ROLE) register binding a role vector to an ARBITRARY supplied
    content concept-vector (2026-08-09, Direction-B build #2,
    exp_situation_model_relation_ablation_v1 -- see notes/exp_dev_handoff_research_psych_bridging_
    inference_situation_models_2026-08-09.md).

    Mirrors CausalLinkRegister's CAUSE/EFFECT role-extension pattern (same base class, same bind/
    bundle/unbind/cleanup_argmax chain) but generalizes what gets bound: CausalLinkRegister binds a
    role to another event's idx_vec (closed max_event_slots vocabulary, since it links event-slot
    indices to each other); this class binds a role to any externally-supplied concept vector (e.g.
    a word's lexical_similarity.concept_vector, or a quality_relation axis-position vector) via
    `bind_filler`, since the goal_outcome_relation ablation needs to carry an OPEN-vocabulary
    concept representation, not a closed idx_vecs symbol.

    Usage note (honest, not hidden): binding+immediately-unbinding a SINGLE filler on a role is
    mathematically EXACT (bind then unbind by the same unit-magnitude role vector recovers the
    input bit-for-bit -- unbind(bind(v,r),r) = v*r*conj(r) = v, since |r|=1), so `decode_filler`
    after exactly one `bind_filler` call on that role is a lossless passthrough, not noise
    injection. This register is used where GOAL_ROLE/OUTCOME_ROLE are bound on SEPARATE per-call
    ephemeral instances (see hdlab.goal_outcome_relation_grounded), specifically to preserve the
    Stage-1-confound-immunity invariant goal_outcome_relation.py's own docstring documents (goal-
    side and outcome-side features must stay independently computable, never a joint goal-word-vs-
    outcome-word comparison) -- its role here is ARCHITECTURAL CONSISTENCY with the proven organ
    (same primitives, auditable bind/unbind trace) and forward-compatibility with genuinely-
    multi-filler use (where bundling would introduce real interference), not a computational
    change on the single-filler case.
    """

    GOAL_ROLE = "GOAL"
    OUTCOME_ROLE = "OUTCOME"

    def __init__(self, d: int, generator: torch.Generator) -> None:
        super().__init__(
            role_vocab=[self.GOAL_ROLE, self.OUTCOME_ROLE],
            d=d,
            generator=generator,
            max_event_slots=1,
            overwrite=False,
        )

    def bind_filler(self, entity: str, role: str, content_vec: torch.Tensor) -> None:
        """Bind role_vecs[role] to an arbitrary content vector (NOT idx_vecs); accumulate
        (bundle) into entity's register exactly as add_event does internally."""
        if role not in self.role_vecs:
            raise KeyError(f"unknown role {role!r}; known={self.role_vocab}")
        bound = binding.bind(self.role_vecs[role], content_vec)
        self._events.setdefault(entity, []).append(bound)

    def decode_filler(self, entity: str, role: str) -> torch.Tensor:
        """Unbind entity's register by role_vecs[role] -> reconstruction of the bound content
        vector (exact if role was the only filler bound for this entity; see class docstring)."""
        reg = self.register(entity)
        return binding.unbind(reg, self.role_vecs[role])
