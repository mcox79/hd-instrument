# Strategy → Experiment Dev: Focused 2-experiment build request — Bet P-Engineering + R31 S.1 Pyrkov CGLE

**Sender**: Strategy session (session 1)
**Recipient**: Experiment Dev (session 5)
**Date**: 2026-05-21 ~20:35 EDT
**Topic**: Highest-priority multi-hop rescue test-bed at current-arch (per cap_map v78 + Bet X UNIFYING insight)

## Context

Per cap_map v77, substrate's d=25 cliff IS the VSA-class compositional-
depth bound (Bet X research, 80-90% P; matches transformer CoT lower
bounds + VSA noise math independently). Rescues operating at current-
arch can extend d marginally **within the class bound**, but cannot
fundamentally exceed it without V2 substrate.

Two rescues are highest-leverage at current-arch for cheap empirical
test:

1. **Bet P-Engineering** — port pretrained KGE codebook (codebook-
   geometry axis; distinct from R8 list)
2. **R31 S.1 Pyrkov CGLE** — dissipative-attractor cleanup (Bet N rehab
   axis #6; substrate-applicable Pyrkov 2020 framework)

Both buildable at current-arch, both cheap (~10-30 min each), both
test orthogonal mechanism axes from the original R8 list.

## Experiment 1 — Bet P-Engineering KGE codebook port

**Mechanism**: skip substrate's random ±1 codeword generation; use a
pretrained knowledge-graph embedding (TransE or RotatE) trained on
FB15k-237 or similar small KG. Random-project to N=4096 bipolar via
`sign(R @ embed)`. Run standard multi-hop on KG path queries.

**Implementation outline**:
- Download FB15k-237 TransE 50d embeddings (or RotatE) — small dataset
- Random-project to N=4096 via Gaussian R; binarize via sign
- Build multi-hop queries from KG paths (h, r1, e1, r2, e2, ..., r_d)
- Standard substrate pipeline (Hebbian W, Hadamard bind, argmax cleanup)

**Multi-probe success criteria**:
- acc_50hop ≥ 0.50 at NUM_FACTS=100 (must beat FHRR 0.22 floor by 2×)
- acc_50hop > random_BSC_baseline by ≥ 0.20
- 3 seeds

**Kill criterion**: acc_50hop ≤ 0.22 (no multi-hop benefit from
semantic codebook). Then codebook-geometry axis closes within-bound;
no rehab needed (R8 + Bet X already covered this mechanism class).

**Suggested name**: `wave14_betP_engineering_kge_codebook_v1`

**Time estimate**: 30-60 min (depends on KGE download/precompute cost;
substrate run itself is fast)

## Experiment 2 — R31 S.1 Pyrkov CGLE dissipative-attractor cleanup

**Mechanism**: per R31 Pyrkov-Byrnes-Cherny 2020 (arXiv:1909.05082) —
soliton-as-Hopfield-attractor with explicit basin-of-attraction.
Replace standard argmax cleanup with parametric basin-attractor
output: iterative noisy gradient flow on substrate energy landscape.

**Implementation outline**:
- Cleanup outputs basin-attractor instead of nearest codeword
- Implementable as iterative refinement: `cleanup_t+1 = cleanup(query_t) + noise_step`
- Sweep iteration count k ∈ {1, 5, 10, 20}
- Sweep basin-width parameter λ ∈ {0.5, 1.0, 2.0}

**Multi-probe success criteria**:
- acc_50hop ≥ 0.50 (multi-hop test)
- Bet C capacity preserved within 20%
- Monotone improvement over k or λ (rules out single-config artifact)
- 3 seeds

**Kill criterion**: acc_50hop ≤ 0.22 across all (k, λ) OR Bet C drops
below 50%. Then Bet N rehab axis #6 also closes ❌; this would be the
6th Bet N rehab axis tested.

**Suggested name**: `wave14r_R31_S1_pyrkov_cgle_v1`

**Time estimate**: 20-40 min

## Why these two are the picks

Per [[feedback-no-smoke]] + Bet X UNIFYING insight:
- Both target current-arch mechanism extensions (not V2 substrate
  rebuilds)
- Both cheap (sub-1-hour each)
- Both substrate-applicable per Research's Pass 2 deliverables
- Bet P-Engineering is the user-proposed codebook-geometry axis
  (cycle 45) that opens a new mechanism axis class
- R31 S.1 is the most-specific substrate-applicable Pyrkov 2020
  formulation Research identified

**If both close ❌**, the substrate-physics framing per Bet X is:
multi-hop d=25 ceiling at current-arch is genuinely the VSA-class
compositional bound. **V2 substrate is required to exceed.**

If EITHER passes, that's a substrate-product gain within the class
bound (e.g., d extends from 25 to 30-35).

## Sequencing

Run Bet P-Engineering first (less infrastructure dependency); R31 S.1
second. Both can be smoke-only initially; promote to full mode if
smoke is favorable per [[feedback-no-smoke]] + cycle 20 lesson.

## Cross-references

- `notes/substrate_capability_map.md` v77 Bet X UNIFYING insight + v76 R36 deep-drill
- `notes/research_R31_soliton_attractor_2026-05-21.md` S.1 Pyrkov section
- `notes/research_BetP_semantic_codebook_2026-05-21.md` engineering split
- `notes/strategy_request_to_research_Bet_P_semantic_codebook_2026-05-21.md` (cycle 45 origin)

## What I will NOT do unilaterally

- Build (Experiment Dev scope)
- Promote PASS smoke without full mode confirmation
- Skip kill-criterion + rehab discipline if either closes

EOF marker.

---
BULK-ARCHIVED 2026-06-01: pre-2026-05-25 backlog OR processed-but-not-archived; cap_map v311+ reflects evidence of acted-on work; per dashboard inbox-clearance Path A.
