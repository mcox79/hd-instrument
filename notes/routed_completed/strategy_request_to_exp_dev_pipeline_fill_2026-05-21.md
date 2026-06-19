# Strategy → Experiment Dev: pipeline-fill request (cycle 55)

**Sender**: Strategy session (session 1)
**Recipient**: Experiment Dev (session 5)
**Date**: 2026-05-21 ~18:23 EDT
**Topic**: Pipeline has been idle 8 min after Bet F S5 PARTIAL; user direction this cycle is to fill pipeline for experiment production

## User direction this cycle

> "proceed with that, but keep working after there is no reason not to
> fill the pipeline for experiment production"

User has explicitly asked for sustained pipeline depth. Per
[[feedback-two-experiments-per-cycle]] (continuous-pipeline cadence,
queue depth >=1 at all times) and the user direction, Strategy is
filing this consolidated priority-ordered queue of 8 experiments.

## Priority-ordered queue (8 experiments, all buildable at current-arch)

All multi-probe success criteria + kill criteria per cap_map v66-v71
sections referenced.

### 1. R27 L.1 — Explicit p-body coupling for super-linear capacity

**Mechanism**: substrate's softmax(β·sim) is implicit p-body coupling
per R29+R16. Make explicit via 4-body interaction terms in cleanup
operator (Musa et al. 2025, arXiv:2506.07849 Dense Associative Memory
in Nonlinear Optical Hopfield).

**Implementation**: in cleanup, replace `argmax(W @ q)` with
`argmax(W @ q + (1/N²) Σ_i,j W[k,i] W[k,j] q[i] q[j])`. The 4-body
term penalizes inconsistent triples. Sweep coupling strength
λ ∈ {0.0, 0.5, 1.0, 2.0} where λ=0 reduces to substrate baseline.

**Multi-probe success criteria**:
- Effective capacity (memorization-then-decode) ≥ 1.5× baseline Bet C M/N=8 at λ_best
- Cleanup acc preserved at all standard probes (5 Mirage probes)
- 3 seeds at N=4096

**Kill criterion**: all λ values ≤ baseline + 5%, no super-linear gain
observed.

**Suggested name**: `wave14_R27_L1_pbody_coupling_v1`

**Why high priority**: 10-50× capacity gain potential per Musa 2025;
NEW Tier-1 capability if validated.

### 2. R21 — Cross-modal substrate binding (explicit role-filler)

**Mechanism**: per R21 substrate-applicable path:
- Random-projected CLIP image embeddings → img_hv
- Random-projected CLIP text embeddings → txt_hv
- Encode fact: `img_role ⊗ img_hv ⊕ txt_role ⊗ txt_hv`
- Store via Hebbian outer-product
- Retrieve by either role

**Implementation**: small text-image dataset (50-100 pairs from
Conceptual Captions or similar pre-tokenized); use pretrained CLIP
ViT-B/32 (frozen, no fine-tune); random-project to N=4096 bipolar
via sign(R @ embed); standard substrate pipeline thereafter.

**Multi-probe success criteria**:
- img→txt retrieval acc ≥ 0.70 at M=50
- txt→img retrieval acc ≥ 0.70 at M=50
- Modality-mixed query (img+txt) acc ≥ 0.85
- 3 seeds

**Kill criterion**: any direction < 0.50 across 3 seeds.

**Suggested name**: `wave14_R21_crossmodal_rolefiller_v1`

**Why high priority**: closes Tier-2 KILLER cross-modal row untouched
since v1; substrate-applicable path identified by R21.

### 3. Bet P-Engineering — Port pretrained KGE codewords

**Mechanism**: skip substrate's random ±1 codeword generation; instead
use a pretrained knowledge-graph embedding (TransE or RotatE) trained
on FB15k-237. Random-project to N=4096 bipolar. Test multi-hop chains
on the existing KG relations.

**Implementation**: download FB15k-237 TransE embeddings (50d), pad/
project to 4096d bipolar via sign(R @ emb), build chain queries from
KG paths (h, r1, e1, r2, e2 ... type structure).

**Multi-probe success criteria**:
- acc_50hop ≥ 0.50 at NUM_FACTS=100 (must beat FHRR 0.22 floor by 2×)
- acc_50hop > random_BSC_baseline by ≥ 0.20
- 3 seeds

**Kill criterion**: acc_50hop ≤ 0.22 (no multi-hop benefit from
semantic codebook).

**Suggested name**: `wave14_betP_engineering_kge_codebook_v1`

**Why priority**: Bet P-Engineering filed cycle 45; no Experiment Dev
pickup yet; this is the cheap empirical test of the codebook-geometry
multi-hop rescue axis.

### 4. Bet F Sketch 1 — Composite Burgers + edge/screw character

**Mechanism**: per R28 Severino-Kamien 2024 — edge/screw dislocations
are topologically distinct beyond Burgers vector. Encode facts with
both Burgers integer label `b ∈ Z` AND edge/screw character bit
`c ∈ {0, 1}`. Retrieval requires both labels.

**Implementation**: substrate keys k_μ = sign(a_A + h_q^μ · a_B + c_μ · a_C)
where a_C is a third sublattice codeword and c_μ ∈ {0, 1}. Test
recovery rate at noise levels p across (q, c) combinations.

**Multi-probe success criteria**:
- Categorical Z×{0,1} recovery rate vs noise: monotone decay with
  sharp transition at predicted p_c
- Composite recovery distinct from single-Z recovery (BET_F_S1 ≠ Bet F v3)
- 3 seeds per (q, c, p) cell

**Kill criterion**: composite recovery equals single-Z recovery (no
additional protection from edge/screw character).

**Suggested name**: `wave14_bet_f_sketch1_burgers_edgescrew_v1`

**Why priority**: 2nd of 5 R28 rehab sketches to test; complements S5
PARTIAL.

### 5. R27 L.2 — Dynamic W reconfigurability

**Mechanism**: per Marsh et al. 2025 quantum-optical spin glass — 7×
over Hopfield via atomic-position reconfiguration. Substrate analog:
substrate W is updated dynamically based on workload (e.g., re-weighted
toward recent queries).

**Implementation**: substrate W_t+1 = (1-α) W_t + α · (1/m) Σ_recent
ξ_i ξ_i^T over a sliding window of recent queries. Sweep α and window
size.

**Multi-probe success criteria**:
- Effective capacity ≥ 1.3× baseline at α_best
- Recent-query bias does not break Bet A (edit-then-query) or Bet C
- 3 seeds

**Kill criterion**: no α gives ≥ 1.0× baseline.

**Suggested name**: `wave14_R27_L2_dynamic_W_v1`

**Why priority**: 7× capacity gain potential per Marsh 2025; medium-
priority new bet.

### 6. R32 M.1 — Phasor codebook (magnon-coupled standing-wave)

**Mechanism**: per R32 Entry 31 — substrate codewords as standing-wave
modes. Phasor codebook: each atom is e^{i·θ_n} with θ_n = 2πn/N,
encoded as bipolar sign(cos(θ_n)). The frequency structure should give
distinct spectral properties.

**Implementation**: replace random ±1 codeword generation with
codewords = sign(cos(2π·n·k/N)) for varying k. Test capacity and
multi-hop accuracy.

**Multi-probe success criteria**:
- Bet C M/N capacity at least 4 (matching v8 32-coset Kerdock)
- Multi-hop acc_50 > FHRR 0.22 baseline
- 3 seeds

**Kill criterion**: capacity < 2, or multi-hop ≤ 0.22.

**Suggested name**: `wave14_R32_M1_phasor_codebook_v1`

**Why priority**: substrate-novel construction validated by R32
Research; combines with Bet P P.7 axis.

### 7. Bet B Kovacs probe (R18 extension)

**Mechanism**: per R18 — Bet B's EMA-blend mechanism IS consolidation-
as-functional-regularization. Test if substrate exhibits Kovacs
memory effect under DOUBLE shift A→B→A: does substrate return to
Phase-A retention or overshoot?

**Implementation**: extend `exp_wave14d_multi_task_cl_v7` to 4-phase
A→B→A'→A'' where A'' is Phase A re-presented; measure retention_A
trajectory across phases.

**Multi-probe success criteria**:
- Kovacs effect signal: retention_A overshoots baseline upon
  re-presentation (non-monotone return)
- Or: monotone increase (no Kovacs but mechanism works)
- 3 seeds

**Kill criterion**: retention_A drops below 0.50 in A'' phase (re-
exposure destabilizes prior consolidation).

**Suggested name**: `wave14d_betB_kovacs_v1`

**Why priority**: extends Bet B ✅ mechanism understanding; tests
R18 Kovacs prediction (substrate is true glass vs mathematical-glass).

### 8. R31 S.1 — Pyrkov CGLE dissipative-attractor cleanup

**Mechanism**: per R31 Entry 32 — substrate-applicable Pyrkov 2020
direct port. Cleanup operator with CGLE parametric basin-of-attraction
structure instead of standard argmax.

**Implementation**: cleanup outputs basin-attractor instead of
nearest codeword. Implementable as iterative noisy gradient flow on
substrate energy landscape.

**Multi-probe success criteria**:
- acc_50hop ≥ 0.50 (multi-hop test)
- Bet C capacity preserved within 20%
- 3 seeds

**Kill criterion**: acc_50hop ≤ 0.22 OR Bet C drops below 50%.

**Suggested name**: `wave14r_R31_S1_pyrkov_cgle_v1`

**Why priority**: substrate-applicable Bet N rehab axis #6 from R31
Research.

## Sequencing recommendation

Cheap-first (10-min experiments) for queue depth, then 30-min for
high-upside:

1. **R27 L.1** (highest upside; super-linear capacity)
2. **R21** cross-modal (Tier-2 KILLER unblock)
3. **Bet P-Engineering** (cheap KGE port)
4. **Bet F S1** (next rehab sketch after S5)
5. **R27 L.2** dynamic W
6. **R32 M.1** phasor codebook
7. **Bet B Kovacs** (extends ✅ mechanism)
8. **R31 S.1** Pyrkov CGLE (Bet N rehab axis #6)

## What I will NOT do unilaterally

- Build the experiments myself (Experiment Dev scope)
- Promote to ✅ from smoke alone (apply v3-v5 cross-version lesson)
- Skip rehab discipline if any of these close ❌

## Cross-references

- `notes/substrate_capability_map.md` v66 (Bet P-Engineering), v70
  (R27 L.1/L.2; R21 cross-modal), v71 (Bet F S5 PARTIAL)
- `notes/research_R27_light_matter_photonic_2026-05-21.md` (L.1, L.2)
- `notes/research_R21_cross_modal_binding_2026-05-21.md`
- `notes/research_R22_sleep_consolidation_2026-05-21.md` (Bet B Kovacs)
- `notes/research_R31_soliton_attractor_2026-05-21.md` (S.1 Pyrkov)
- `notes/research_BetP_semantic_codebook_2026-05-21.md`
- `notes/strategy_request_to_research_Bet_F_rehab_2026-05-21.md` (S1-S5)

## EOF marker

---
BULK-ARCHIVED 2026-06-01: pre-2026-05-25 backlog OR processed-but-not-archived; cap_map v311+ reflects evidence of acted-on work; per dashboard inbox-clearance Path A.
