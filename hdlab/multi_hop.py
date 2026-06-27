"""Multi-hop chain-of-thought traversal: naive + iterative-cleanup (Modern-Hopfield) strategies.

Operationalizes the r1_multihop_iterative_cleanup_v1 cell mechanism (CERT chain-grade at
K=2; ratified MM at K=3,4 per r1 landed-VET commit ee4081e6 2026-06-22). The substrate-native
chain-of-thought primitive: stack single-hop W queries with Modern-Hopfield one-iteration
cleanup between hops (Ramsauer 2021 dense Hopfield = transformer attention; beta-scaled
softmax over top-K_set entities; bundle = the cleaned state for the next hop).

Composes with `hdlab.kg_traversal.KGStore` (provides the E, R, W trio + key/score ops).
Chain-grade-validated at K=2 hops; r1 MM at K=3 and K=4 (chain works but accuracy below the
chain-grade bar). Use `naive_chain` for the U1/n8 single-shot 2-hop pattern; use
`iter_cleanup_chain` when intermediate refusal-gating + deeper-hop stability matters.

Honest-scope per r1b 2026-06-22 HARD_FAIL: the iterative-cleanup chain-grade promotion path
beyond K=2 has been validated for the primitive itself but not for any specific dataset
load-bearing application beyond U1 / n8. Use with explicit per-hop tau_terminate calibration
on your data.
"""

from __future__ import annotations

import time

import torch

from . import tracing
from .kg_traversal import KGStore


def _normalize(v: torch.Tensor, eps: float = 1e-8) -> torch.Tensor:
    """L2-normalize a vector; protects against zero-norm via eps clamp."""
    nrm = torch.linalg.norm(v)
    return v / (nrm + eps)


def naive_chain(kg: KGStore, start: int, relations: list[int]) -> tuple[int, list[int]]:
    """K-hop chain without per-hop cleanup; the U1/n8 multi-value Hebbian baseline.

    state_hv = W @ (state_hv * R[p_i] * sq) per hop; final argmax against E.
    Returns (pred_entity, intermediate_chain).

    Chain-grade at K=2 (CERT 585 n8; substrate_2hop=0.426 vs frozen-enc=0.012 = 36.49x).
    Beyond K=2, accuracy decays — use iter_cleanup_chain for deeper hops.
    """
    state = kg.E[start].clone()
    chain = []
    for p in relations:
        state = kg.W @ (state * kg.R[p] * kg.sq)
        ent_scores = kg.E @ state
        chain.append(int(ent_scores.argmax()))
    final = chain[-1] if chain else start
    return final, chain


def iter_cleanup_chain(
    kg: KGStore,
    start: int,
    relations: list[int],
    k_set: int = 20,
    beta: float | None = None,
    tau_terminate: float | None = None,
    k_inner: int = 1,
    shuffle_top: bool = False,
    shuffle_generator: torch.Generator | None = None,
) -> tuple[int | None, list[float], int]:
    """ITERATIVE_CLEANUP K-hop with Modern-Hopfield per-hop attractor projection.

    Per hop: (a) transit state via W; (b) score entities; (c) select top-K_set; (d) optional
    refuse-gate if max-conf < tau_terminate; (e) Modern-Hopfield bundle = sum(softmax(beta*conf)
    * E[top_idx]); (f) renormalize; (g) repeat k_inner times within each hop.

    `shuffle_top=True` is the RANDOM_CLEANUP discriminator control: shuffles top-K_set indices
    before the bundle step; destroys cleanup signal while keeping iteration structure identical.
    Requires `shuffle_generator` (torch.Generator) for reproducibility.

    Returns (pred_entity_or_None, per_hop_top1_confs, terminated_at_hop_idx_or_minus1).
    None pred = refuse-gate terminated traversal at terminated_at.

    Args:
        kg: KGStore with ingested triples.
        start: entity index to start traversal.
        relations: list of relation indices (one per hop).
        k_set: number of top entities to bundle per hop (default 20).
        beta: Modern-Hopfield inverse-temperature; if None, uses n_dim (the Ramsauer 2021
              substrate-appropriate scale; sharpens near-argmax cleanup).

              **BETA-REGIME WARNING (research_5cell_cross_HARDFAIL_synthesis_2026-06-24):**
              `beta=N_DIM` is correct for SINGLE-HOP saturated cleanup ONLY (where you want a
              confident argmax pick on a saturated codebook). For INTER-HOP soft mechanisms
              (DFE/turbo-style, multi-hop chains where the soft posterior must carry information
              across hops), use beta in {2, 10, 50} range. At beta >= N_DIM/2 the softmax
              becomes a Dirac delta and the "soft" mechanism degenerates to hard argmax
              (= naive_chain). Empirical witness: in exp_substrate_soft_chain_dfe_multihop_v1
              + exp_substrate_resonator_multihop_integration_v1, per-seed top1 were BIT-IDENTICAL
              between RESONATOR_HARD and SOFT_CHAIN arms (0.61/0.61, 0.645/0.645, 0.64/0.64)
              because both ran at beta=8192=N_DIM. A runtime warning fires below.
        tau_terminate: refuse-gate threshold on top-1 conf per hop; if None, no terminate.
        k_inner: cleanup iterations within each hop (default 1 = standard one-step Hopfield).
        shuffle_top: discriminator control (RANDOM_CLEANUP).
        shuffle_generator: torch.Generator for shuffle reproducibility.

    Chain-grade at K=2; MIDDLE_BAND at K=3, K=4 per r1 LANDED-VET 2026-06-22.
    """
    t0 = time.perf_counter_ns()
    if beta is None:
        beta = float(kg.n_dim)
    # Beta-regime guard (research_5cell_cross_HARDFAIL_synthesis_2026-06-24):
    # multi-hop chains (len(relations) >= 2) with beta >= n_dim/2 collapse to hard argmax;
    # the "soft" mechanism is never exercised. Emit a one-shot warning so the bug surfaces.
    if len(relations) >= 2 and beta >= (kg.n_dim / 2.0):
        import warnings as _warnings
        _warnings.warn(
            "iter_cleanup_chain: beta=%.1f >= n_dim/2=%.1f on a K=%d-hop chain. "
            "At this regime softmax(beta * top_conf) is a Dirac delta and the soft "
            "Modern-Hopfield bundle degenerates to hard argmax (= naive_chain). "
            "For genuine inter-hop soft mechanism, use beta in {2, 10, 50}. See "
            "notes/research_5cell_cross_HARDFAIL_synthesis_2026-06-24.md."
            % (float(beta), kg.n_dim / 2.0, len(relations)),
            stacklevel=2,
        )
    state = kg.E[start].clone()
    per_hop_conf: list[float] = []
    terminated_at = -1
    for hop_idx, p in enumerate(relations):
        top_idx = None
        top_conf = None
        for _inner in range(k_inner):
            transit = kg.W @ (state * kg.R[p] * kg.sq)
            ent_scores = kg.E @ transit
            topk = torch.topk(ent_scores, k=k_set)
            top_idx = topk.indices
            top_conf = topk.values
            top1 = float(top_conf[0])
            if tau_terminate is not None and top1 < tau_terminate:
                terminated_at = hop_idx
                tracing.emit(
                    "multi_hop.iter_cleanup.refused",
                    {"hop_idx": hop_idx, "top1": top1, "tau": tau_terminate},
                    None,
                    elapsed_ns=time.perf_counter_ns() - t0,
                )
                return None, per_hop_conf, terminated_at
            if shuffle_top:
                if shuffle_generator is None:
                    raise ValueError("shuffle_top=True requires shuffle_generator")
                perm = torch.randperm(k_set, generator=shuffle_generator)
                top_idx = top_idx[perm]
            # Modern-Hopfield beta-scaled softmax bundle
            z = beta * top_conf
            w = torch.softmax(z - z.max(), dim=0)
            state = (w.unsqueeze(1) * kg.E[top_idx]).sum(dim=0)
            state = _normalize(state)
        per_hop_conf.append(float(top_conf[0]))
    final_scores = kg.E @ state
    final = int(final_scores.argmax())
    tracing.emit(
        "multi_hop.iter_cleanup.done",
        {"n_hops": len(relations), "k_set": k_set, "beta": beta},
        {"per_hop_top1": per_hop_conf, "final": final},
        elapsed_ns=time.perf_counter_ns() - t0,
    )
    return final, per_hop_conf, terminated_at


def random_cleanup_chain(
    kg: KGStore,
    start: int,
    relations: list[int],
    k_set: int = 20,
    beta: float | None = None,
    shuffle_generator: torch.Generator | None = None,
) -> tuple[int | None, list[float], int]:
    """RANDOM_CLEANUP discriminator: iter_cleanup_chain with shuffle_top=True.

    The r1 control arm that verifies iterative-cleanup is doing real work (not just averaging
    noise). If random_cleanup_chain accuracy matches iter_cleanup_chain, the cleanup mechanism
    is null in your regime — surface this as a discriminator-regime check (Fix #16).
    """
    if shuffle_generator is None:
        shuffle_generator = torch.Generator()
        shuffle_generator.manual_seed(0)
    return iter_cleanup_chain(
        kg, start, relations,
        k_set=k_set, beta=beta, tau_terminate=None, k_inner=1,
        shuffle_top=True, shuffle_generator=shuffle_generator,
    )


def bidirectional_chain(
    kg: KGStore,
    start: int,
    end_candidates: torch.Tensor,
    relations: list[int],
    *,
    midpoint_hop: int | None = None,
) -> tuple[int, float, dict[str, float]]:
    """Bidirectional meet-in-middle K-hop traversal; chain-grade-validated mechanism.

    Per query: (a) walk forward MID hops from `start` via W @ (state * R[p] * sq);
    (b) for each candidate Z in `end_candidates`, walk backward (DEPTH-MID) hops
    from E[Z] via W.T @ state * R[p] * sq (in reverse-predicate-order); (c) rank
    candidates by cosine(state_fwd, state_bwd_Z) at the midpoint.

    Returns (best_Z_index, best_cosine, diagnostics_dict). The diagnostics dict
    carries `mean_cosine`, `cos_top1_minus_top2` (margin), and `midpoint_hop`.

    `midpoint_hop`: defaults to len(relations) // 2. The meet-point is where the
    bidirectional split happens; mid=DEPTH//2 is the BFS-balanced choice.

    Chain-grade-validated at K=5, V_C=200, N=8192, 3 seeds [7,17,23] per
    `substrate_multihop_bidirectional_meet_middle_v2_META_M7_rail` (commit ee4081e6+;
    BIDIR_MEET_MID top1=0.620 cv=0.064 lift +0.297 over forward-only 1000-binding
    rail; META_M7 rail PASS at REPRODUCE 0.122 in [0.08, 0.25]; chain-grade
    verdict `HARD_PASS_CHAIN_GRADE_BIDIRECTIONAL_REVIVAL`).

    Honest scope: validated for KG-style triples in (E, R) basis with Hebbian
    associative W; the `W.T` reverse-walk is correct for rank-1 outer-product W
    where each (s, p, o) triple writes `E[o] outer (E[s] * R[p] * sq)`. For other
    W constructions (predicate-specific W, learned W, etc.) the reverse-walk
    semantics differ and validation must be re-done.

    Args:
        kg: KGStore with ingested triples.
        start: entity index to start traversal (forward source).
        end_candidates: LongTensor of candidate end-entity indices to rank.
        relations: list of relation indices (one per hop).
        midpoint_hop: where to meet (default: len(relations) // 2).

    Returns:
        (best_Z_index, best_cosine, diagnostics_dict)

    Hoisted into hdlab/ per results-to-application same-cycle discipline 2026-06-27
    (cell-author M5 reverse-replay drill; chain-grade verdict from META_M7 cell).
    """
    t0 = time.perf_counter_ns()
    depth = len(relations)
    if midpoint_hop is None:
        midpoint_hop = depth // 2
    if not (0 <= midpoint_hop <= depth):
        raise ValueError(f"midpoint_hop={midpoint_hop} not in [0, {depth}]")

    state_fwd = kg.E[start].clone()
    for i in range(midpoint_hop):
        p = relations[i]
        state_fwd = kg.W @ (state_fwd * kg.R[p] * kg.sq)
    fnorm = torch.linalg.norm(state_fwd) + 1e-8

    best_cos = -2.0
    best_Z = int(end_candidates[0])
    second_cos = -2.0
    cos_all = []
    for Z_t in end_candidates:
        Z = int(Z_t)
        state_bwd = kg.E[Z].clone()
        for i in range(depth - 1, midpoint_hop - 1, -1):
            p = relations[i]
            state_bwd = kg.W.T @ state_bwd
            state_bwd = state_bwd * kg.R[p] * kg.sq
        bnorm = torch.linalg.norm(state_bwd) + 1e-8
        cos = float(torch.dot(state_fwd, state_bwd) / (fnorm * bnorm))
        cos_all.append(cos)
        if cos > best_cos:
            second_cos = best_cos
            best_cos = cos
            best_Z = Z
        elif cos > second_cos:
            second_cos = cos

    mean_cos = float(sum(cos_all) / max(len(cos_all), 1))
    margin = best_cos - second_cos
    diagnostics = {
        "mean_cosine": mean_cos,
        "best_cosine": best_cos,
        "cos_top1_minus_top2": margin,
        "midpoint_hop": midpoint_hop,
        "n_candidates": int(end_candidates.numel()),
    }
    tracing.emit(
        "multi_hop.bidirectional_chain",
        {"depth": depth, "midpoint_hop": midpoint_hop, "n_candidates": int(end_candidates.numel())},
        {"best_Z": best_Z, "best_cosine": best_cos, "margin": margin},
        elapsed_ns=time.perf_counter_ns() - t0,
    )
    return best_Z, best_cos, diagnostics


def partition_routed_chain(
    kg: KGStore,
    start: int,
    relations: list[int],
    partitions: list[torch.Tensor],
    router,
    *,
    oracle_routing: bool = True,
) -> tuple[int, list[int]]:
    """K-hop chain with per-hop PARTITION routing (Cell B v2 META_M7 chain-grade mechanism).

    Per hop: (a) call router(state_hv, relation_idx) -> partition_index;
    (b) transit state via W;
    (c) score ONLY against entities in partitions[partition_index];
    (d) argmax over the partition; result becomes next hop state.

    `partitions`: list of LongTensors; partitions[i] = entity indices in partition i.
    `router`: callable taking (state_hv, relation_idx) -> int (the partition index for this
              hop).
    `oracle_routing`: HONEST-SCOPE FLAG. If True (default), the caller is responsible for
                      providing a router that returns the GROUND-TRUTH partition for each hop
                      (i.e. the partition containing the true target of the hop). This is the
                      mechanism that achieves chain-grade at K=5. If False, the router is
                      assumed to be substrate-native (relation-typed, HRR-bind-based, or
                      learned). substrate-native routing is OPEN-FOLLOW-UP (cells RC1/RC2/RC3
                      per META_BARRIER_1_QUINTUPLE_RECONCILIATION); chain-grade not yet
                      certified for substrate-native routing.

    Returns (pred_entity, intermediate_chain).

    Chain-grade-validated at K=5: ARM_COMPOSE_PARTITION_5HOP mean=0.9550 cv=0.0074 across
    3 seeds (7, 17, 23) at N=8192, V_C=200, n_partitions=20, part_size=10; META_M7 REPRODUCE
    rail PASS 0/3 breach; per-step decay [0.99, 0.98, 0.975, 0.97, 0.965] = gradual (not
    by-construction saturation). See:
      - math::T3/EXP_substrate_multihop_compose_fly_lsh_multibank_partition_v2_META_M7_rail
        _chain_grade_partition_per_hop_5hop_0p955_cv_0p007_meta_M7_pass_oracle_routing_scope_flag
      - math::T3/EXP_..._measured_mechanism_oracle_routing_required_for_5hop_chain_grade
        _substrate_native_routing_open  (production-claim scope bound)
      - meta::T3/META_BARRIER_1_QUINTUPLE_RECONCILIATION  (narrowing not breaking)
    Atomized 2026-06-26 batch 2 per skunkworks_tier_rule_batch2_4artifact_2026-06-26.md.

    HONEST-SCOPE: chain-grade-certified ONLY with oracle_routing=True. The production-claim
    "substrate can do 5-hop reasoning without oracle routing" is NOT certified; substrate-
    native router cells RC1 (relation-typed), RC2 (HRR-bind), RC3 (learned no-LLM) are
    open follow-ups. Use this primitive with explicit honest-scope flag in your application.
    """
    state = kg.E[start].clone()
    chain: list[int] = []
    for hop_idx, p in enumerate(relations):
        part_idx = router(state, p)
        if part_idx < 0 or part_idx >= len(partitions):
            raise ValueError(
                f"partition_routed_chain: router returned out-of-range partition index "
                f"{part_idx} at hop {hop_idx} (n_partitions={len(partitions)})"
            )
        ent_idxs_in_part = partitions[part_idx]
        state = kg.W @ (state * kg.R[p] * kg.sq)
        # Score only the partition's entities; argmax within partition.
        part_scores = kg.E[ent_idxs_in_part] @ state
        local_argmax = int(part_scores.argmax())
        pred = int(ent_idxs_in_part[local_argmax])
        chain.append(pred)
        state = kg.E[pred].clone()
    final = chain[-1] if chain else start
    tracing.emit(
        "multi_hop.partition_routed.done",
        {
            "n_hops": len(relations),
            "n_partitions": len(partitions),
            "oracle_routing": oracle_routing,
        },
        {"chain": chain, "final": final},
        elapsed_ns=0,
    )
    return final, chain
