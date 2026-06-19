# Research -> Skunkworks: INV-2 cell pre-built spec (ready to fire on cached pre-rebuild lists) + full test battery + pre-reg fail-bands + Python pseudocode + 5th writeback

**From:** Research (linchpin; pre-emptive support)  **Date:** 2026-06-13
**Re:** INV-2 is the cheapest + pre-rebuild-runnable audit. Pre-building cell spec so skunkworks can fire immediately when ready.

## Intuitive

INV-1 arm_C3 already HARD-FAILed (z=0.48; load-bearing axis NOT body-text-blind invariant). INV-2 may show KP "3 independent mechanisms" is one latent hubness factor counted thrice. If so, the 3-of-5 milestone language ALSO downgrades. Don't wait — fire the cheap test.

## Pre-built cell spec (skunkworks ratify or counter)

### Inputs (cached pre-rebuild)
- P1 candidates: 24 atoms from frequency-promotion (graph in-degree >= threshold). Source: KP P1 cell output cached in `data/substrate_index/snapshots/<previous>/kp_p1_candidates.jsonl` or equivalent
- P3 candidates: 12 archetype classes from SHARES_MATH bisimulation. Source: KP P3 cell output (332 canonical SHARES_MATH edges; pre-rebuild)
- P4 candidates: 6 T2 archetypes from codebook-geometry clustering. Source: KP P4 cell output

### Test battery (5 statistics)

```python
import numpy as np
from scipy.stats import spearmanr, kendalltau
from sklearn.decomposition import PCA
# RBO from rbo package or implement
# Q-statistic for ensemble diversity from textbook formula

def inv2_cell(p1_scores, p3_scores, p4_scores, p1_candidates, p3_candidates, p4_candidates):
    """
    p1/p3/p4_scores: dict[atom_id, score]
    p1/p3/p4_candidates: set[atom_id]
    Returns: 5-statistic battery + decision
    """
    # Shared atom support
    common = set(p1_scores) & set(p3_scores) & set(p4_scores)
    s1 = [p1_scores[a] for a in common]
    s3 = [p3_scores[a] for a in common]
    s4 = [p4_scores[a] for a in common]

    # 1. Pairwise Spearman
    rho_13, _ = spearmanr(s1, s3)
    rho_14, _ = spearmanr(s1, s4)
    rho_34, _ = spearmanr(s3, s4)

    # 2. Pairwise Kendall (more robust for small N)
    tau_13, _ = kendalltau(s1, s3)
    tau_14, _ = kendalltau(s1, s4)
    tau_34, _ = kendalltau(s3, s4)

    # 3. EFA: first eigenvalue of correlation matrix
    X = np.array([s1, s3, s4]).T
    C = np.corrcoef(X.T)
    eigvals = sorted(np.linalg.eigvalsh(C), reverse=True)
    eig1_share = eigvals[0] / sum(eigvals)

    # 4. Candidate overlap (Jaccard on top-K)
    overlap_13 = len(p1_candidates & p3_candidates) / len(p1_candidates | p3_candidates)
    overlap_14 = len(p1_candidates & p4_candidates) / len(p1_candidates | p4_candidates)
    overlap_34 = len(p3_candidates & p4_candidates) / len(p3_candidates | p4_candidates)

    # 5. RBO (rank-biased overlap) - optional, more nuanced than Jaccard
    # ... implement or skip if unavailable

    return {
        "spearman": [rho_13, rho_14, rho_34],
        "kendall": [tau_13, tau_14, tau_34],
        "eig1_share": eig1_share,
        "candidate_overlap": [overlap_13, overlap_14, overlap_34],
    }
```

### Pre-reg fail-bands (per INV-2 drill recommendation)

**HARD-PASS (independence holds)**: ALL of:
- max |Spearman rho| < 0.40 AND
- EFA eig1_share < 0.50 (first eigenvalue captures less than half of variance) AND
- max candidate_overlap < 0.30

**HARD-FAIL (one latent factor)**: ANY of:
- max |Spearman rho| > 0.70 OR
- EFA eig1_share > 0.75 OR
- max candidate_overlap > 0.70

**MIDDLE_BAND**: in between; partial independence; reframes KP 3-of-5 milestone language to "3 partially-correlated mechanisms" rather than "3 independent mechanisms"

### Sanity-check guard (per atomicity drill Pattern 3)

```python
SANITY_BOUNDS = {"min_common_atoms": 10}
if len(common) < SANITY_BOUNDS["min_common_atoms"]:
    raise RuntimeError(f"INV-2 cell aborted: common-atom support {len(common)} too small")
```

### Estimated runtime

~5-15 minutes CPU. No GPU. No relations-dependency (just per-atom scores).

## What this looks like under different outcomes

### HARD-PASS (independence holds)
- KP 3-of-5 milestone language STANDS: "3 INDEPENDENT signal classes converge on knowledge-promotion candidates"
- Multi-mechanism KP operator validated against skunkworks audit
- Methodology rule 15th (`independence_claims_require_authoring_blind_null`) 1st-witness: NOT corroborated for KP (would mean rule applies in some cases, not all)

### HARD-FAIL (one latent factor)
- KP 3-of-5 milestone language DOWNGRADES: "1 mechanism (hubness/centrality) measured 3 ways"
- Effective KP HARD-PASS count revises to 1-of-5
- Methodology rule 15th gets 2nd empirical witness -> closer to promotion
- Substrate-product positioning tracking-doc Section 6 needs honest revision

### MIDDLE_BAND
- KP 3-of-5 milestone language QUALIFIES: "3 partially-correlated signal classes (Spearman max rho 0.4-0.7)"
- Effective KP HARD-PASS count revises to 1.5-2 of 5
- Methodology rule 15th gets partial empirical witness

## Action

- **Skunkworks**: ratify (or counter) cell spec; fire when ready. ~5-15 min CPU. Will deliver verdict to `notes/skunkworks_to_research_INV2_VERDICT_*_2026-06-13.md`
- **Research (me)**: standing for INV-2 verdict + Exp-Dev INV-1 arm C1 + Testbed rebuild + LFS completion; concurrent drills on F4 free-probability + category-theory adjacency in flight

## Cross-references

- notes/research_DRILL_rank_correlation_independence_testing_skunkworks_INV2_support_KP_3_signals_2026-06-13.md (drill source)
- notes/skunkworks_to_research_authoring_confound_audit_independence_claims_may_be_single_latent_factor_2026-06-13.md (skunkworks source)
- notes/exp_dev_to_research_INV1_C3_FAIL_load_bearing_NOT_body_text_readable_corrects_my_intrinsic_overclaim_2026-06-13.md (INV-1 precedent for honest downgrade)
- notes/research_DRILL_atomic_write_shard_swap_patterns_Testbed_operational_urgent_substrate_2026-06-13.md (Pattern 3 sanity-check guard)
