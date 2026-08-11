"""hdlab/three_tier_loop.py -- the assembled three-tier knowledge loop, 2026-08-11.

Wires the individually-validated organs named in
notes/director_three_tier_knowledge_architecture_design_audit_2026-08-11.md ("(B) CONCRETE
BUILD SPEC") into ONE runnable pipeline, per the user's own 5-step architecture (recorded
verbatim in that audit): GATHER -> REASON -> PARSE -> GATE -> FOUNDATION (on PASS) or MIDDLE
tier (on FAIL, retained + periodically swept, re-queried FIRST on re-encounter until combined
evidence crosses the same strict gate). Brain-faithful framing (Complementary Learning
Systems, McClelland/O'Reilly/Norman): GATHER = external refs, MIDDLE = hippocampus (fast,
accumulate, always-first), FOUNDATION = neocortex (consolidated), GATE+SWEEP = systems
consolidation.

THIS MODULE IS ASSEMBLY GLUE, NOT A NEW MECHANISM. Every gate/store/gather/reason primitive
below is imported read-only and called verbatim; nothing here reimplements organ-level logic:

  STATE OF MIND  -> hdlab.situation_model_accumulate.RelationRegister (caller-owned; this
                     module accepts an already-decoded query_vec, see gather_and_reason)
  GATHER + REASON -> hdlab.gather_reason.ca3_relevance_gather / fanout_two_hop / build_codebook
                     (promoted 2026-08-11 from experiments/exp_state_of_mind_relevance_gather_
                     reasoning_union_v1.py -- see that module's own docstring)
  PARSE           -> hdlab.grounding_acquisition_loop.context_vector (episode context encoding)
                     + gap_item_key (this module: the (subject,relation,candidate) -> single
                     foundation-schema item-key identity a candidate resolution PARSEs into)
  GATE            -> hdlab.grounding_acquisition_loop.Library / consolidation_pass (exposure +
                     consistency + schema-consistency conjunctive gate; PROMOTE_MIN_EXPOSURE=8,
                     PROMOTE_MIN_CONSISTENCY=0.75)
  MIDDLE TIER     -> hdlab.prelim_tier.TierState / update_prelim_and_generalize (retain-forever
                     + CA3/DG near-concept sweep + combined-evidence cluster-grain promotion;
                     promoted 2026-08-11 from experiments/exp_crutch_fade_social_iqa_v1.py)
  FOUNDATION      -> hdlab.hd_fact_store.HDFactStore (role-slot-bound (s,r,o) glass-box store)

ASSEMBLY DECISION (the ONE new wiring choice this module makes; per this task's own "if the
pieces do NOT compose cleanly... report the SPECIFIC gap honestly" instruction, this is that
honest report): hdlab.prelim_tier.TierState.native_store_gen (where the middle tier's own
COMBINED-EVIDENCE cluster promotion writes -- design-audit step "[5](c) COMBINED-EVIDENCE
PROMOTE") is constructed BY TierState.__init__ as its OWN, separate HDFactStore instance --
prelim_tier.py has no constructor hook to inject an existing store. The design audit's own
build-spec diagram is explicit that combined-evidence promotion should "re-evaluate the
IDENTICAL [4] GATE at cluster grain ... -> loops back to [4]" -- i.e. land in the SAME
foundation store the single-item GATE promotes into, not a second, disconnected one. This
module makes that literal with a single documented attribute reassignment right after
constructing TierState:

    self.tier_state.native_store_gen = self.foundation_store

This is NOT a modification to prelim_tier.py (which stays byte-for-byte reused, unmodified,
its own witness untouched) -- it is this assembly module choosing WHICH object TierState's
existing, unmodified `store()` calls land in. Both organs run exactly as independently
validated; only the target object is shared, so single-item promotions (GATE) and
combined-evidence promotions (MIDDLE TIER SWEEP) both end up queryable from the one
`foundation_store` a caller constructs -- matching the diagram's "loops back to [4]" intent
without editing either reused module.

FUSE / ANSWER-TIME ROUTING: the design audit found (Gap G1) that no organ on disk performs a
holistic multi-source SCORE FUSION -- the only real precedent
(experiments/exp_crutch_fade_social_iqa_v1.py's resolve_item) tries sources in strict PRIORITY
ORDER (native -> prelim -> raw) and takes the first hit. ThreeTierLoop.answer() reproduces
that same, honestly-validated priority-order pattern (FOUNDATION -> MIDDLE -> UNRESOLVED); a
true holistic fusion is NOT claimed here (see design audit Gap G1 -- still open, out of scope
for this assembly pass).

ASCII-only. Deterministic throughout (every random draw lives in caller-supplied
torch.Generator / numpy seeds passed into the reused organs; this module draws no randomness
of its own -- no built-in hash(), no list(set()) ordering -- PROT-023/F.5 compliant).
"""
from __future__ import annotations

from typing import Callable, Dict, List, Optional, Set, Tuple

import numpy as np
import torch

from hdlab.gather_reason import ca3_relevance_gather, fanout_two_hop, top1
from hdlab.grounding_acquisition_loop import Library, consolidation_pass
from hdlab.hd_fact_store import ACTIVE_STATUSES, HDFactStore
from hdlab.kg_traversal import KGStore
from hdlab.prelim_tier import TierState, update_prelim_and_generalize
from hdlab.script_grain_acquisition_loop import build_instance_register

DEFAULT_RELATION = "GAP_FACT"
KEY_SEP = "||"


# =========================================================================== PARSE identity
def gap_item_key(subject: str, relation: str, candidate: str) -> str:
    """Deterministic item-key identity for ONE candidate resolution of a (subject, relation)
    gap -- the PARSE stage's foundation-schema item identity. Analogous to
    hdlab.prelim_tier.default_pair_key, generalized from a symmetric 2-part concept pair to an
    ordered 3-part (subject, relation, candidate) gap-fact identity: a (subject, relation) gap
    with several competing candidate answers becomes several independently-gated items (one
    per candidate), each gated on ITS OWN exposure/consistency -- a disclosed, deliberate
    composition choice (see module docstring PARSE) that lets this module reuse
    consolidation_pass's existing POS/NEG-polarity-only gate verbatim rather than modifying it
    to carry an open-vocabulary object value."""
    return f"{subject}{KEY_SEP}{relation}{KEY_SEP}{candidate}"


def parse_gap_item_key(pk: str) -> Tuple[str, str, str]:
    """Inverse of gap_item_key. Raises ValueError on a non-gap_item_key-shaped string."""
    parts = pk.split(KEY_SEP)
    if len(parts) != 3:
        raise ValueError(f"not a gap_item_key (expected 3 '{KEY_SEP}'-separated parts): {pk!r}")
    return parts[0], parts[1], parts[2]


def gap_register_fn(pk: str, cluster_key: str, label: str) -> torch.Tensor:
    """Default CA3/DG FHRR register builder for gap_item_key-shaped keys (the SWEEP stage's
    register_fn hook, per hdlab.prelim_tier.update_prelim_and_generalize's register_fn
    parameter): delegates to script_grain_acquisition_loop.build_instance_register(subject,
    candidate, cluster_key, f"GAP_{label}") -- AGENT/PATIENT slots carry (subject, candidate),
    TRIGGER/CONSEQUENT carry (cluster_key, GAP_{label}). Mirrors
    hdlab.prelim_tier.default_register_fn's own pattern for its 'a::b' pair keys, generalized
    to gap_item_key's 3-part shape. Callers whose item keys are NOT gap_item_key-shaped must
    supply their own register_fn (same contract as prelim_tier)."""
    subject, _relation, candidate = parse_gap_item_key(pk)
    return build_instance_register(subject, candidate, cluster_key, f"GAP_{label}")


# =========================================================================== GATHER + REASON
def gather_and_reason(query_vec: np.ndarray, item_names: List[str], codebook: np.ndarray,
                      ent_idx: Dict[str, int], hop1_kg: KGStore, hop2_kg: KGStore,
                      start_idx: int, hop1_rel_idx: int, hop2_rel_idx: int, k1: int, k2: int,
                      n_ent: int, *, k_peel: int = 25, sim_floor: float = 0.05) -> dict:
    """One full GATHER+REASON pass for a single gap query, composing hdlab.gather_reason's two
    promoted primitives (no new mechanism): STATE-OF-MIND `query_vec` (caller already decoded
    it, e.g. via hdlab.situation_model_accumulate.RelationRegister.decode_filler -- kept OUT of
    this function so GATHER stays decoupled from state-of-mind maintenance, per the design
    audit's own stage boundaries) -> CA3 RELEVANCE GATHER (ca3_relevance_gather) over
    (item_names, codebook) -> K<=2 REASON fan-out (fanout_two_hop) restricted at hop-1 to the
    gathered items' entity indices (via ent_idx).

    Returns {"gathered": [names...], "ranked": [(idx,score)...], "top1_idx": int|None} -- the
    PARSE stage's raw material (map top1_idx back to an entity name via the caller's own
    index-to-name table, then build a gap_item_key from it)."""
    gathered = ca3_relevance_gather(query_vec, item_names, codebook, k_peel=k_peel, sim_floor=sim_floor)
    gathered_idx: Set[int] = {ent_idx[m] for m in gathered if m in ent_idx}
    ranked = fanout_two_hop(hop1_kg, hop2_kg, start_idx, hop1_rel_idx, hop2_rel_idx, k1, k2,
                            n_ent, restrict_hop1_to=gathered_idx)
    return {"gathered": gathered, "ranked": ranked, "top1_idx": top1(ranked)}


# =========================================================================== the assembled loop
class ThreeTierLoop:
    """GATE (strict, foundation-track) + MIDDLE TIER (retain-forever + CA3/DG sweep), wired to
    a shared FOUNDATION store (see module docstring ASSEMBLY DECISION). One instance per
    logical knowledge domain (a caller may run several independent ThreeTierLoop instances,
    e.g. one per arm/condition, exactly as hdlab.prelim_tier.TierState has no opinion on how
    many instances a caller keeps alive)."""

    def __init__(self, foundation_store: HDFactStore, seed_base: int = 0, n_dim: int = 2048,
                 relation: str = DEFAULT_RELATION, prelim_trust: str = "TRUST_LOW") -> None:
        self.foundation_store = foundation_store
        self.relation = relation
        self.library = Library()  # strict/foundation-track (GATE input)
        self.tier_state = TierState(seed_base=seed_base, n_dim=n_dim, relation=relation,
                                     prelim_trust=prelim_trust)
        # ASSEMBLY DECISION (see module docstring): combined-evidence cluster promotion lands
        # in the SAME foundation store the strict single-item GATE promotes into.
        self.tier_state.native_store_gen = self.foundation_store

    def encounter(self, item_key: str, pole: str, context_vec: np.ndarray, episode_id: str,
                  pass_idx: int, *, also_strict: bool = True) -> dict:
        """One gap RE-ENCOUNTER: flag one trace of evidence. also_strict=True (default) flags
        BOTH the strict/foundation-track Library (GATE input) and the middle tier's own
        retain-forever prelim_lib (MIDDLE input) with the IDENTICAL trace -- mirrors the one
        real precedent on disk (experiments/exp_crutch_fade_social_iqa_v1.py), which flags both
        stores from the same per-episode evidence. also_strict=False flags ONLY the middle
        tier -- for evidence a caller wants to keep accumulating into the always-retained
        middle store beyond the strict track's own cadence (e.g. once the strict Library item
        has already reached a terminal status and Library.flag()'s "reject once terminal" guard
        would otherwise silently no-op the strict half of this call)."""
        flagged_middle = self.tier_state.prelim_lib.flag(item_key, episode_id, pole, context_vec, pass_idx)
        flagged_strict = False
        if also_strict:
            flagged_strict = self.library.flag(item_key, episode_id, pole, context_vec, pass_idx)
        return {"flagged_strict": flagged_strict, "flagged_middle": flagged_middle}

    def consolidate(self, pass_idx: int, cluster_key_fn: Callable[[str], str], novelty_thresh: float,
                    *, register_fn: Callable[[str, str, str], torch.Tensor] = gap_register_fn,
                    gate_kwargs: Optional[dict] = None, middle_kwargs: Optional[dict] = None) -> dict:
        """One checkpoint: GATE (hdlab.grounding_acquisition_loop.consolidation_pass, strict
        single-item promotion into foundation_store) + MIDDLE TIER retain/sweep/combined-
        evidence-promotion (hdlab.prelim_tier.update_prelim_and_generalize -- also lands in
        foundation_store, see ASSEMBLY DECISION). Both called VERBATIM; no gate math
        reimplemented here. gate_kwargs/middle_kwargs pass through to the respective reused
        functions (e.g. {"promote_min_exposure": 8}) without this module hard-coding them."""
        gate_kwargs = dict(gate_kwargs or {})
        middle_kwargs = dict(middle_kwargs or {})
        gate_kwargs.setdefault("promote_relation", self.relation)
        gate_kwargs.setdefault("promote_source", "three_tier_loop")
        gate_report = consolidation_pass(self.library, pass_idx, native_store=self.foundation_store,
                                         **gate_kwargs)
        middle_report = update_prelim_and_generalize(self.tier_state, cluster_key_fn, novelty_thresh,
                                                      register_fn=register_fn, **middle_kwargs)
        return {"gate": gate_report, "middle": middle_report}

    def answer(self, item_key: str) -> Tuple[str, Optional[str]]:
        """Priority-order routing (the ONLY real precedent on disk; see module docstring FUSE /
        ANSWER-TIME ROUTING): FOUNDATION -> MIDDLE -> UNRESOLVED. Returns
        (tier_tag, polarity_object_or_None) where tier_tag is one of "FOUNDATION_RESOLVED",
        "MIDDLE_RESOLVED", "UNRESOLVED"."""
        hit = self.foundation_store.query(item_key, self.relation)
        if hit and hit[0]["status"] in ACTIVE_STATUSES:
            return "FOUNDATION_RESOLVED", hit[0]["object"]
        hit2 = self.tier_state.prelim_store.query(item_key, self.relation)
        if hit2 and hit2[0]["status"] in ACTIVE_STATUSES:
            return "MIDDLE_RESOLVED", hit2[0]["object"]
        return "UNRESOLVED", None


if __name__ == "__main__":
    print("hdlab.three_tier_loop: assembly module, no standalone self-test payload. "
          "See verification/test_three_tier_loop_e2e.py for the scaffold-free end-to-end "
          "witness (gap -> gather -> reason -> parse -> gate -> foundation/middle cycle).")
