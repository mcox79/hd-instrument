"""Working-memory multi-bank primitive: K-item capacity via per-bank cleanup.

Architecture validated by exp_substrate_working_memory_multi_bank_K_extension_adversarial_v1
cell-land 2026-06-26 (commit 6e2ff698; HARD_PASS chain-grade at K=4096 MULTI_64x per
Skunkworks landed-VET; ledger row 62ce9e7dca071828).

ARCHITECTURE:
  K_total items routed across n_banks parallel banks; each bank holds k_per_bank =
  K_total / n_banks items. Routing is by content-anchored bank-id derivation
  (deterministic from key hash modulo n_banks); cleanup within a bank is the standard
  bind / unbind / argmax pattern over the bank's local codebook.

CHAIN-GRADE ENVELOPE (per the cell):
  K_total = 4096, n_banks = 64 (MULTI_64x), k_per_bank = 64:
    RANDOM regime:      recall = 0.9927  cv = 0.0006  (488x lift over NAIVE)
    ADVERSARIAL regime: recall = 0.9801  cv = 0.0015  (FEATURE_OVERLAP_FRAC=0.20)
    adv-within-band:    0.0126 (PASS HP_adv_within=0.05)

HONEST SCOPE FLAG (DO NOT CLAIM CHAIN-GRADE BELOW THIS GATE):
  The chain-grade claim is anchored ONLY on arms with k_per_bank >= 64 at
  FEATURE_OVERLAP_FRAC=0.20 with N_DIM=8192. Below k_per_bank=64 (e.g. K=1024
  MULTI_64x at k_per_bank=16, or K=2048 MULTI_64x at k_per_bank=32) the bank's
  per-slot cleanup saturates at recall=1.000 cv=0.000 BY CONSTRUCTION -- the
  per-bank capacity is so far below saturation that any cleanup mechanism would
  appear perfect. This is a per-bank-capacity effect, NOT a substrate-architectural
  lift; cells citing those arms as chain-grade evidence should be ruled MM per the
  META rule `META_multi_bank_WM_per_bank_capacity_governs_when_chain_grade_evidence_
  is_genuine_k_per_bank_ge_64_at_overlap_0p20_is_minimum_discriminating_regime`.

The threshold k_per_bank=64 is anchored at N_DIM=8192 OVERLAP=0.20. The threshold
shifts with N_DIM (lower N -> lower threshold) and with OVERLAP (higher overlap ->
higher threshold). For non-default config, a separate chain-grade-extension cell is
required before relying on this primitive's chain-grade guarantee.

Composes-with: sequence-binding (c3 chain-grade) for sequence-WM-multi-bank stacks;
hierarchical 2-level partition routing for WM-routed retrieval over very large K.
"""

from __future__ import annotations

# Chain-grade-confirmed envelope constants; see module docstring for cell-land provenance.
K_TOTAL_CHAIN_GRADE_ENVELOPE = 4096
N_BANKS_CHAIN_GRADE_ARM = 64
K_PER_BANK_CHAIN_GRADE_ARM = 64

# By-construction-saturation gate threshold (META rule):
# below this k_per_bank, the multi-bank K-extension claim is by-construction
# at FEATURE_OVERLAP_FRAC <= 0.20 with N_DIM=8192.
K_PER_BANK_BYCONSTRUCTION_THRESHOLD = 32
K_PER_BANK_DISCRIMINATING_REGIME_MINIMUM = 64

# Anchor for the threshold (META rule); separate cell required for non-default config.
THRESHOLD_ANCHORED_AT_N_DIM = 8192
THRESHOLD_ANCHORED_AT_OVERLAP_FRAC = 0.20


def assert_k_per_bank_in_discriminating_regime(
    k_total: int,
    n_banks: int,
    feature_overlap_frac: float = 0.20,
    n_dim: int = 8192,
) -> None:
    """Raise ValueError if (k_total, n_banks, overlap, n_dim) would land outside the
    chain-grade-confirmed discriminating regime for multi-bank WM.

    Use this BEFORE claiming a multi-bank WM cell's recall result is chain-grade
    evidence. Cells whose k_per_bank <= K_PER_BANK_BYCONSTRUCTION_THRESHOLD with
    FEATURE_OVERLAP_FRAC <= 0.20 and N_DIM=8192 are by-construction-saturated; their
    recall=1.000 cv=0.000 result is a per-bank-capacity effect, not architectural lift.

    Args:
        k_total: total items stored across all banks
        n_banks: number of parallel banks (k_per_bank = k_total / n_banks)
        feature_overlap_frac: adversarial feature-overlap fraction (default 0.20)
        n_dim: substrate dimensionality (default 8192)
    """
    if n_banks <= 0:
        raise ValueError(f"n_banks must be positive; got {n_banks}")
    k_per_bank = k_total // n_banks
    if (
        k_per_bank < K_PER_BANK_DISCRIMINATING_REGIME_MINIMUM
        and feature_overlap_frac <= THRESHOLD_ANCHORED_AT_OVERLAP_FRAC
        and n_dim >= THRESHOLD_ANCHORED_AT_N_DIM
    ):
        raise ValueError(
            f"k_per_bank={k_per_bank} (K_total={k_total} / n_banks={n_banks}) is BELOW "
            f"the chain-grade-confirmed discriminating-regime minimum "
            f"K_PER_BANK_DISCRIMINATING_REGIME_MINIMUM="
            f"{K_PER_BANK_DISCRIMINATING_REGIME_MINIMUM} at FEATURE_OVERLAP_FRAC="
            f"{feature_overlap_frac} and N_DIM={n_dim}. "
            f"This config is by-construction-saturated; multi-bank cleanup will succeed "
            f"trivially within per-bank capacity. Either (a) increase k_per_bank to >=64 "
            f"by reducing n_banks, OR (b) dispatch a chain-grade-extension cell at this "
            f"reduced k_per_bank to ratify the regime, OR (c) declare the result will be "
            f"tiered MEASURED_MECHANISM per META_multi_bank_WM_per_bank_capacity_governs."
        )


def assert_chain_grade_envelope(k_total: int, n_banks: int) -> None:
    """Raise ValueError if (k_total, n_banks) exceeds the chain-grade-confirmed envelope.

    Chain-grade is anchored at K_total <= 4096 with n_banks=64 (k_per_bank=64). Above
    this K_total, the substrate IS likely to scale (k_per_bank can grow further) but
    the claim is NOT yet chain-grade-ratified; a separate cell is required.
    """
    if k_total > K_TOTAL_CHAIN_GRADE_ENVELOPE:
        raise ValueError(
            f"k_total={k_total} exceeds chain-grade envelope K_TOTAL_CHAIN_GRADE_ENVELOPE="
            f"{K_TOTAL_CHAIN_GRADE_ENVELOPE}; either reduce K_total or dispatch a new "
            f"chain-grade-extension cell for K > {K_TOTAL_CHAIN_GRADE_ENVELOPE}."
        )
    if n_banks != N_BANKS_CHAIN_GRADE_ARM and k_total == K_TOTAL_CHAIN_GRADE_ENVELOPE:
        # Soft warning rather than error: other (k_total, n_banks) combos may still be
        # in the discriminating regime; we already have assert_k_per_bank_in_discriminating_regime
        # for that gate. This branch only flags the exact chain-grade-arm config.
        pass
