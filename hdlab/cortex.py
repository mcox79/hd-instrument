"""Cortex composed pipeline -- M3 cortex-layer primitive composition (Phase 2).

Composes M1.4 refuse-gate + M1.5 TwoTierContext + M1.6 chunked-attention router +
M1.7 RoleSlotSummarizer + M1.8 ClarifyGate into a single Cortex facade with a
uniform forward() API. Phase 2 of cortex integration; Phase 1 (primitive
extraction) landed as separate modules 2026-07-02.

M1.3 NoiseChannel is OUT OF SCOPE this phase (see project_M3_cortex_layer_must_
inject_stochastic_noise_at_boundary_2026-06-30.md); Phase 2b will add it as a
CortexConfig hook if the Phase 3 integration test requires stochastic coupling.

============================================================================
COMPUTE ARCHITECTURE (mandatory per USER-locked storage-strategy substrate
physics law CG_META 2026-07-02: math4_v2 + math4_rung3_v2 chain-grade)
============================================================================
Storage strategy: **MIXED (inherited-per-primitive; each sub-storage preserved)**.

The Cortex facade owns NO first-class compositional storage of its own; it
holds only references to sub-primitives and per-call provenance scratch. Each
sub-primitive preserves its own declared storage strategy verbatim:

  - M1.5 TwoTierContext:    MIXED (STM sharded across banks + LTM dense-Hopfield tape)
  - M1.7 RoleSlotSummarizer: SHARDED (S-way per-role slot buffers; NESTED for RECURSIVE)
  - M1.8 ClarifyGate:        NO_STORAGE (stateless read-only two-threshold gate)
  - M1.4 refuse_gate:        NO_STORAGE (functional; scalar tau applied to a scalar score)
  - M1.6 chunked_attention_readout: NO_STORAGE (functional read over caller-supplied K/V tape)

Rationale (why the facade adds no bundled state):
- Adding a bundled provenance cache in the facade would violate the storage-
  strategy physics law for L>=2 chain composition (BUNDLED collapse at
  K/N > 0.138 Amit-Gutfreund wall). Any facade-internal storage MUST be
  SHARDED not bundled.
- Instead, provenance is emitted PER-CALL in the CortexResponse.provenance
  dict as scalar diagnostics; NOT accumulated across calls in a facade-owned
  vector. Callers may build their own SHARDED provenance store externally.
- Composition guarantee is therefore INHERITED unchanged from each sub-
  primitive; the facade is composition-safe by construction.
============================================================================

Envelope (chain-grade-confirmed via sub-primitives; do not exceed without a
per-primitive rescue cell):
- N_DIM >= 8192 (inherited from M1.5 + M1.7 THRESHOLD_ANCHORED_AT_N_DIM)
- STM_K = 100, LTM_K in [1130, 1640] (inherited from M1.5)
- S_ROLES = 4 (inherited from M1.7)
- clarify_gate: 0.0 <= clarify_lower < clarify_upper <= 1.0 (inherited from M1.8)
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

import torch

from hdlab.chunked_attention import chunked_attention_readout
from hdlab.clarify_gate import ClarifyGate, GateOutcome
from hdlab.context_retention import TwoTierContext
from hdlab.refuse_gate import apply_refuse
from hdlab.role_slot_summarizer import RoleSlotSummarizer


# ------------------------------- config + response ---------------------------


@dataclass
class CortexConfig:
    """Cortex pipeline configuration.

    Args:
        n_dim: substrate vector dimensionality; must be >= 8192 (inherited).
        v_cb: value codebook size (default 1024).
        stm_k: M1.5 short-term buffer capacity (default 100).
        ltm_k: M1.5 long-term tape capacity (default 1200).
        n_roles: M1.7 role-slot count (default 4).
        refuse_gate_accept_tau: M1.4 apply_refuse boundary; score >= tau ->
            accept, score < tau -> refuse. Precedes clarify-gate; hard refuse
            overrides clarify-gate three-way decision.
        clarify_gate_lower_tau: M1.8 lower boundary; below -> REFUSE.
        clarify_gate_upper_tau: M1.8 upper boundary; above -> ACCEPT.
            (M1.8 field is confusingly named refuse_tau; represents ACCEPT
            threshold, not a hard refuse. We rename here for clarity.)
        attention_chunk_size: M1.6 chunk size for streaming attention.
        attention_beta: M1.6 softmax sharpness.
        enable_role_slot_summary: whether to invoke M1.7 for provenance.
        noise_channel_enabled: Phase 2b placeholder; must be False here.
        seed: torch.Generator seed for sub-primitive codebook builds.
    """
    n_dim: int = 8192
    v_cb: int = 1024
    stm_k: int = 100
    ltm_k: int = 1200
    n_roles: int = 4
    refuse_gate_accept_tau: float = 0.20
    clarify_gate_lower_tau: float = 0.35
    clarify_gate_upper_tau: float = 0.55
    attention_chunk_size: int = 1024
    attention_beta: float = 13.0
    enable_role_slot_summary: bool = True
    noise_channel_enabled: bool = False
    seed: int = 0

    def __post_init__(self):
        if self.noise_channel_enabled:
            raise NotImplementedError(
                "noise_channel_enabled=True reserved for Phase 2b M1.3 "
                "NoiseChannel extraction; not implemented in Phase 2 facade.")


@dataclass
class CortexResponse:
    """Cortex forward-pass output.

    Fields:
        retrieval: (n_dim,) retrieved value vector (from M1.6 attention router
            or from M1.5 codebook indexing when router path not used).
        predicted_val_idx: codebook index (-1 if no cleanup performed).
        tier_used: source tier -- one of {"ATTENTION_ROUTER", "M1_5_CONTEXT",
            "NONE_EMPTY_QUERY"}.
        confidence: scalar in [-1, 1]; typically in [0, 1] for cosine max_sim.
        route: final routing decision -- one of {"REFUSE", "CLARIFY", "ACCEPT"};
            derived by combining M1.4 refuse-gate with M1.8 clarify-gate.
        provenance: per-primitive diagnostic dict; scalars only (see storage
            architecture docstring for why no bundled state is kept).
        role_slots: optional (S, n_dim) or (L2, S, n_dim) tensor from M1.7 if
            summary was requested; None otherwise.
    """
    retrieval: torch.Tensor
    predicted_val_idx: int
    tier_used: str
    confidence: float
    route: str
    provenance: dict
    role_slots: Optional[torch.Tensor] = None


# --------------------------------- Cortex ------------------------------------


class Cortex:
    """Composed cortex pipeline over the M1.4-M1.8 primitives.

    Composition (per Phase 2 proposal notes/proposal_cortex_integration_hdlab_
    module_2026-07-02.md):
        1. Optional M1.5 write of (role_key, val_idx) to two-tier context.
        2. Retrieval path -- one of:
             (a) M1.6 chunked_attention_readout over caller-supplied K/V tape;
                 confidence = max cosine similarity (query, keys).
             (b) M1.5 TwoTierContext.read on the role-key query; confidence
                 held to a bounded neutral value when no attention tape given.
        3. M1.4 apply_refuse(confidence, refuse_gate_accept_tau) -- hard gate.
        4. M1.8 ClarifyGate.evaluate(confidence) -- three-way route.
        5. Combined route: hard-refuse overrides -> "REFUSE"; else clarify-gate.
        6. Optional M1.7 RoleSlotSummarizer.summarize_role over supplied
             (item_keys, role_assign, val_indices) for provenance.
        7. Return CortexResponse with all outputs + per-primitive diagnostics.
    """

    def __init__(self, config: CortexConfig):
        self.config = config
        self._context = TwoTierContext(
            n_dim=config.n_dim,
            stm_k=config.stm_k,
            ltm_k=config.ltm_k,
            v_cb=config.v_cb,
            seed=config.seed,
        )
        self._summarizer = RoleSlotSummarizer(
            n_dim=config.n_dim,
            n_roles=config.n_roles,
            v_cb=config.v_cb,
            seed=config.seed + 1,
        )
        self._clarify_gate = ClarifyGate(
            clarify_tau=config.clarify_gate_lower_tau,
            refuse_tau=config.clarify_gate_upper_tau,
        )

    # --- context accessors --------------------------------------------------

    def value_codebook(self) -> torch.Tensor:
        """Expose the M1.5 value codebook (V_CB, N_DIM) for external callers."""
        return self._context.value_codebook()

    def context_len_stm(self) -> int:
        return len(self._context._stm_role_keys)

    def context_len_ltm(self) -> int:
        return len(self._context._ltm_role_keys)

    # --- pipeline forward ---------------------------------------------------

    def forward(
        self,
        query: torch.Tensor,
        context_keys: Optional[torch.Tensor] = None,
        context_vals: Optional[torch.Tensor] = None,
        role_key_for_memory_write: Optional[torch.Tensor] = None,
        val_idx_for_memory_write: Optional[int] = None,
        role_slot_context: Optional[dict] = None,
    ) -> CortexResponse:
        """Compose the cortex pipeline for one forward pass.

        Args:
            query: (n_dim,) or (1, n_dim) query vector; the primary input.
            context_keys: optional (M, n_dim) attention tape keys for the M1.6
                router path. Required paired with context_vals.
            context_vals: optional (M, V) attention tape vals; V may equal
                n_dim (codebook-space) or a distinct readout dim.
            role_key_for_memory_write: optional (n_dim,) role key for M1.5
                write BEFORE the read (turn-taking write-through-read pattern).
            val_idx_for_memory_write: optional int codebook index paired with
                role_key_for_memory_write.
            role_slot_context: optional dict {item_keys: (K,n_dim), role_assign:
                (K,), val_indices: (K,)} for M1.7 summarize_role invocation.

        Returns:
            CortexResponse with retrieval, tier, confidence, route, provenance,
            and optional role_slots.
        """
        provenance: dict = {}

        # (1) Optional M1.5 write -------------------------------------------
        if (role_key_for_memory_write is not None
                and val_idx_for_memory_write is not None):
            self._context.write(
                role_key_for_memory_write, int(val_idx_for_memory_write))
            provenance["m15_write_committed"] = True
            provenance["m15_stm_len_after_write"] = self.context_len_stm()
            provenance["m15_ltm_len_after_write"] = self.context_len_ltm()

        # Normalize query shape --------------------------------------------
        if query.dim() == 1:
            q_2d = query.unsqueeze(0)
        elif query.dim() == 2:
            q_2d = query
        else:
            raise ValueError(
                f"query must be 1-D or 2-D; got shape {tuple(query.shape)}")

        # (2) Retrieval path -----------------------------------------------
        tier_used: str
        retrieval_vec: torch.Tensor
        predicted_val_idx: int
        max_sim: float

        have_router_tape = (context_keys is not None
                            and context_vals is not None
                            and context_keys.shape[0] > 0)

        if have_router_tape:
            # (2a) M1.6 chunked attention router -------------------------
            readout = chunked_attention_readout(
                q_2d, context_keys, context_vals,
                chunk_size=self.config.attention_chunk_size,
                beta=self.config.attention_beta,
            )  # (1, V)
            retrieval_vec = readout[0]
            # Max cosine sim (query, context_keys) -> confidence signal that
            # M1.8 ClarifyGate consumes (matches source cell's max_sim def).
            q_row = q_2d[0].to(torch.float32)
            q_normed = q_row / q_row.norm().clamp_min(1e-9)
            k_normed = (context_keys.to(torch.float32)
                        / context_keys.to(torch.float32).norm(
                            dim=-1, keepdim=True).clamp_min(1e-9))
            sims = k_normed @ q_normed
            max_sim = float(sims.max())
            predicted_val_idx = int(torch.argmax(sims).item())
            tier_used = "ATTENTION_ROUTER"
            provenance["m16_attention_readout_shape"] = tuple(readout.shape)
            provenance["m16_max_sim"] = max_sim
        elif role_key_for_memory_write is not None:
            # (2b) M1.5 context-retention path over role-key query -------
            if (self.context_len_stm() + self.context_len_ltm()) > 0:
                pred_idx = self._context.read(
                    role_key_for_memory_write, target_cos_noise=1.0)
                retrieval_vec = self._context.value_codebook()[pred_idx].clone()
                predicted_val_idx = int(pred_idx)
                # Bounded neutral confidence: without an attention tape the
                # M1.5 STM/LTM read does not expose a calibrated max_sim.
                # We report a neutral mid-band value so the clarify-gate
                # emits CLARIFY (turn-taking signal) instead of a false-
                # confident ACCEPT. Callers who need calibrated confidence
                # should supply context_keys/context_vals for the M1.6 path.
                max_sim = 0.5 * (self.config.clarify_gate_lower_tau
                                 + self.config.clarify_gate_upper_tau)
                tier_used = "M1_5_CONTEXT"
                provenance["m15_predicted_val_idx"] = predicted_val_idx
                provenance["m15_confidence_reported_as_neutral"] = True
            else:
                # Empty context; no retrieval possible.
                retrieval_vec = torch.zeros(
                    self.config.n_dim, dtype=torch.float32)
                predicted_val_idx = -1
                max_sim = 0.0
                tier_used = "NONE_EMPTY_QUERY"
                provenance["m15_empty_context"] = True
        else:
            # No tape + no role-key: nothing to retrieve on.
            retrieval_vec = torch.zeros(
                self.config.n_dim, dtype=torch.float32)
            predicted_val_idx = -1
            max_sim = 0.0
            tier_used = "NONE_EMPTY_QUERY"
            provenance["query_only_no_retrieval_source"] = True

        provenance["confidence_max_sim"] = max_sim
        provenance["tier_used"] = tier_used

        # (3) M1.4 refuse-gate (hard boundary; overrides clarify-gate) ----
        refuse_accept = apply_refuse(max_sim, self.config.refuse_gate_accept_tau)
        provenance["m14_refuse_gate_accept"] = bool(refuse_accept)

        # (4) M1.8 clarify-gate three-way route ---------------------------
        clarify_outcome = self._clarify_gate.evaluate(max_sim)
        provenance["m18_clarify_gate_outcome"] = clarify_outcome.value

        # (5) Combined route ----------------------------------------------
        if not refuse_accept:
            route = "REFUSE"
            provenance["route_source"] = "m14_hard_refuse"
        else:
            route = clarify_outcome.value
            provenance["route_source"] = "m18_clarify_gate"

        # (6) Optional M1.7 role-slot summary -----------------------------
        role_slots: Optional[torch.Tensor] = None
        if role_slot_context is not None and self.config.enable_role_slot_summary:
            item_keys = role_slot_context["item_keys"]
            role_assign = role_slot_context["role_assign"]
            val_indices = role_slot_context["val_indices"]
            role_slots = self._summarizer.summarize_role(
                item_keys, role_assign, val_indices)
            provenance["m17_role_slots_shape"] = tuple(role_slots.shape)

        return CortexResponse(
            retrieval=retrieval_vec,
            predicted_val_idx=predicted_val_idx,
            tier_used=tier_used,
            confidence=max_sim,
            route=route,
            provenance=provenance,
            role_slots=role_slots,
        )


# ----------------------------- formula selftests -----------------------------


def _bipolar_random(shape, generator: torch.Generator) -> torch.Tensor:
    r = torch.rand(shape, generator=generator)
    return torch.where(r < 0.5,
                       torch.tensor(-1.0),
                       torch.tensor(1.0)).to(torch.float32)


def _selftest_construct_default_cortex() -> None:
    """Default CortexConfig instantiates without error at CG envelope."""
    cx = Cortex(CortexConfig())
    assert cx.context_len_stm() == 0
    assert cx.context_len_ltm() == 0
    cb = cx.value_codebook()
    if cb.shape != (1024, 8192):
        raise AssertionError(f"codebook shape unexpected: got {tuple(cb.shape)}")


def _selftest_forward_empty_query_returns_valid_response() -> None:
    """forward() on query only (no tape, no role-key) returns well-typed
    NONE_EMPTY_QUERY response without crashing."""
    cx = Cortex(CortexConfig())
    q = torch.zeros(8192, dtype=torch.float32)
    resp = cx.forward(q)
    if not isinstance(resp, CortexResponse):
        raise AssertionError("forward did not return CortexResponse")
    if resp.tier_used != "NONE_EMPTY_QUERY":
        raise AssertionError(
            f"expected NONE_EMPTY_QUERY tier; got {resp.tier_used!r}")
    if resp.route not in {"REFUSE", "CLARIFY", "ACCEPT"}:
        raise AssertionError(f"route not in enum: {resp.route!r}")
    if resp.retrieval.shape != (8192,):
        raise AssertionError(
            f"retrieval shape wrong: {tuple(resp.retrieval.shape)}")
    if not isinstance(resp.provenance, dict):
        raise AssertionError("provenance must be dict")


def _selftest_forward_with_attention_tape_uses_m16_router() -> None:
    """When context_keys/vals given, forward() invokes M1.6 router; response
    reports ATTENTION_ROUTER tier and a peaked confidence when query matches
    a tape key."""
    cx = Cortex(CortexConfig())
    gen = torch.Generator()
    gen.manual_seed(29)
    M = 32
    N = 8192
    context_keys = _bipolar_random((M, N), gen)
    context_vals = _bipolar_random((M, N), gen)
    query = context_keys[7].clone()  # exact match to key 7
    resp = cx.forward(
        query,
        context_keys=context_keys,
        context_vals=context_vals,
    )
    if resp.tier_used != "ATTENTION_ROUTER":
        raise AssertionError(
            f"expected ATTENTION_ROUTER tier; got {resp.tier_used!r}")
    if resp.predicted_val_idx != 7:
        raise AssertionError(
            f"exact-match query should argmax to key 7; got "
            f"{resp.predicted_val_idx}")
    if resp.confidence < 0.95:
        raise AssertionError(
            f"exact-match confidence should be near 1.0; got {resp.confidence:.3f}")
    if resp.route != "ACCEPT":
        raise AssertionError(
            f"exact-match should ACCEPT; got {resp.route!r} "
            f"(refuse_gate_accept={resp.provenance.get('m14_refuse_gate_accept')}, "
            f"clarify_outcome={resp.provenance.get('m18_clarify_gate_outcome')})")


def _selftest_low_confidence_query_refuses() -> None:
    """When query is uncorrelated with all tape keys, confidence lands in
    the REFUSE band and the combined route is REFUSE (via clarify-gate lower
    threshold OR refuse-gate hard boundary)."""
    cx = Cortex(CortexConfig(
        refuse_gate_accept_tau=0.20,
        clarify_gate_lower_tau=0.35,
        clarify_gate_upper_tau=0.55,
    ))
    gen = torch.Generator()
    gen.manual_seed(31)
    M = 32
    N = 8192
    context_keys = _bipolar_random((M, N), gen)
    context_vals = _bipolar_random((M, N), gen)
    # Query uncorrelated with tape (fresh random draw): expected max cos ~ 0
    query = _bipolar_random((N,), gen)
    resp = cx.forward(
        query,
        context_keys=context_keys,
        context_vals=context_vals,
    )
    # Uncorrelated bipolar in 8192-D typically has |max sim over M=32| ~ 0.03
    # -- well below refuse_gate_accept_tau=0.20 -> hard REFUSE.
    if resp.route != "REFUSE":
        raise AssertionError(
            f"uncorrelated query should REFUSE; got {resp.route!r} "
            f"(confidence={resp.confidence:.4f})")


def _selftest_role_slot_summary_produced_when_requested() -> None:
    """When role_slot_context is supplied, forward() attaches the M1.7 role-
    slot bundle tensor with shape (n_roles, n_dim)."""
    cx = Cortex(CortexConfig())
    gen = torch.Generator()
    gen.manual_seed(37)
    N = 8192
    K = 16
    S = cx.config.n_roles
    item_keys = _bipolar_random((K, N), gen)
    role_assign = torch.arange(K) % S
    val_indices = torch.randint(0, cx.config.v_cb, (K,), generator=gen)
    query = _bipolar_random((N,), gen)
    resp = cx.forward(
        query,
        role_slot_context={
            "item_keys": item_keys,
            "role_assign": role_assign,
            "val_indices": val_indices,
        },
    )
    if resp.role_slots is None:
        raise AssertionError("role_slots should be non-None when context given")
    if resp.role_slots.shape != (S, N):
        raise AssertionError(
            f"role_slots shape wrong: {tuple(resp.role_slots.shape)}")


def _selftest_m15_write_then_read_updates_context_lens() -> None:
    """Writing via forward() advances the M1.5 STM buffer length by 1."""
    cx = Cortex(CortexConfig())
    gen = torch.Generator()
    gen.manual_seed(41)
    N = 8192
    role_key = _bipolar_random((N,), gen)
    val_idx = int(torch.randint(0, cx.config.v_cb, (1,), generator=gen).item())
    resp = cx.forward(
        role_key.clone(),  # query = role_key here (M1.5 path)
        role_key_for_memory_write=role_key,
        val_idx_for_memory_write=val_idx,
    )
    if cx.context_len_stm() != 1:
        raise AssertionError(
            f"expected STM len 1 after single write; got {cx.context_len_stm()}")
    if resp.tier_used != "M1_5_CONTEXT":
        raise AssertionError(
            f"expected M1_5_CONTEXT tier when no attention tape; got "
            f"{resp.tier_used!r}")


def _selftest_noise_channel_flag_is_reserved() -> None:
    """noise_channel_enabled=True must raise NotImplementedError (Phase 2b)."""
    try:
        CortexConfig(noise_channel_enabled=True)
    except NotImplementedError:
        return
    raise AssertionError("expected NotImplementedError for noise_channel_enabled=True")


def _run_all_selftests() -> dict:
    _selftest_construct_default_cortex()
    _selftest_forward_empty_query_returns_valid_response()
    _selftest_forward_with_attention_tape_uses_m16_router()
    _selftest_low_confidence_query_refuses()
    _selftest_role_slot_summary_produced_when_requested()
    _selftest_m15_write_then_read_updates_context_lens()
    _selftest_noise_channel_flag_is_reserved()
    return {
        "primitives_composed": [
            "M1.4_refuse_gate",
            "M1.5_TwoTierContext",
            "M1.6_chunked_attention_readout",
            "M1.7_RoleSlotSummarizer",
            "M1.8_ClarifyGate",
        ],
        "noise_channel_phase_2b_stub": True,
        "storage_strategy": "MIXED_inherited_per_primitive_no_facade_storage",
        "cg_source": "Phase 2 composition; Phase 1 CG sub-primitives 2026-07-01/02",
    }


if __name__ == "__main__":
    result = _run_all_selftests()
    print(f"[cortex selftest] PASS {result}")
