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
