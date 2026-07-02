# Pre-reg — substrate_concept_encoder_spoke2_temporal_contiguity_foldiak_trace_v1

**Filed:** 2026-07-02 late evening (Director main-thread; positions for immediate dispatch post-Spoke-1-CG)
**Anchor:** `substrate_concept_encoder_spoke2_temporal_contiguity_foldiak_trace_v1`
**Design notes:**
- `notes/design_stage2_concept_encoder_spoke2_temporal_contiguity_slow_feature_analysis_2026-07-02.md` (base design + amendment for Spoke 1 v3-D reframe)

## Prereq

Spoke 1 v3-D CG'd (FULL in flight; if lands HP, extract to `hdlab/concept_encoder.py`; Spoke 2 imports from that module). Spoke 2 does NOT fire without Spoke 1 CG.

## Framing discipline (LOAD-BEARING)

Per USER 2026-07-02 brain-best-in-class + `feedback_never_narrate_synthetic_HD_bundles_as_english_language_capability`: this cell is a MECHANISM PROOF. Adjacent-in-stream inputs (adjacent sentences in a document, or same concept in different contexts) should produce SIMILAR concept HDs. NO English understanding; substrate does not know language. The temporal-contiguity structure is a training signal for concept INVARIANCE — brain-analog: complex-cell learning in V1 (Foldiak 1991), IT face-invariance (DiCarlo & Cox 2007), Slow Feature Analysis (Wiskott & Sejnowski 2002).

**Under brain-best-in-class + 6/6 drill convergence (2026-07-02):** Spoke 2 is the LOAD-BEARING home for predictive coding in Stage 2. PC arm re-enters at this layer with tight scope — temporal-contiguity-informed prediction. See `reference_5x_drill_convergence_PC_redundant_with_WTA_for_concept_encoding_Spoke1_2026-07-02.md`.

## Mechanism (from design)

**Foldiak trace rule** — modify Spoke 1 v3-D's Hebbian update rule so post-synaptic activity is a running exponential trace of recent WTA output, not instantaneous. Temporally-adjacent inputs share overlapping traces → representations pulled together.

Composition with Spoke 1 v3-D (competitive-Hebbian sparse coding):
```
Raw text → char_positional_encoder → surface_hd
    ↓
Competitive-Hebbian layer (Spoke 1 v3-D unchanged):
    - k-largest-then-sign sparsification (k ~ 2%)
    - WTA output
    ↓
Foldiak trace (NEW for Spoke 2):
    - trace_t = alpha * WTA_output_t + (1-alpha) * trace_{t-1}
    - Hebbian outer-product update uses TRACE as post-synaptic factor: W += lr * trace_t * input_hd^T
    - alpha ~ 0.1 (approx 10-sentence memory; document boundary resets trace)
    ↓
Concept HD (sparse-bipolar, temporally-invariant, N=8192)
```

**Optional stretch arm (per Spoke 2 amendment):** ARM_TRACE_PC_HIERARCHICAL — hierarchical PC modification of Foldiak trace per Salvatori 2021. Would prove PC-in-correct-role earns complexity here even though it doesn't at Spoke 1.

## Regime constants

- N_DIM = 8192 (Spoke 1 v3-D FULL production regime)
- N_CONCEPTS = 50 (25 clusters × 2 concepts per cluster)
- SENTENCES_PER_CONCEPT = 40 (same corpus as Spoke 1 v3-D)
- k_sparsity = 0.02 (matches Spoke 1 v3-D)
- alpha_trace = 0.1 (initial; may need tuning at smoke)
- Seeds = [11, 17, 23] (3 seeds; matches Spoke 1 v3-D)
- Storage strategy: SHARDED (per USER-locked CG_META)

## Arms (5 arms × 3 seeds = 15 units)

| Arm | Mechanism | Role |
|---|---|---|
| ARM_SPOKE1_ONLY_REPRO | Spoke 1 v3-D competitive-Hebbian (NO trace); reproduces v3-D baseline | Positive control |
| **ARM_FOLDIAK_TRACE** | Spoke 1 v3-D + Foldiak trace post-synaptic factor | LOAD-BEARING |
| ARM_TRACE_ALPHA_FAST | Foldiak with alpha=0.5 (very fast trace, ~2-sentence memory) | Ablation: proves alpha value matters |
| ARM_ADJACENT_PAIR_HEBB | Direct Hebbian bind of adjacent sentence pairs via SequenceMatrix | Alternative mechanism (Spoke 2 Option C) |
| ARM_TRACE_SHUFFLE_CONTROL | Foldiak trace with sentence-order-shuffled corpus | Sanity: proves temporal order is load-bearing |

Cardinality target: `EXPECTED_N_UNITS = 5 * 3 = 15`; `arms_differ_verified` required.

## Corpus (temporal-contiguity variant of Spoke 1 v3-D synthetic)

Same 50-concept controlled corpus as Spoke 1 v3-D + Spoke 1 v2, BUT with temporal structure:
- Documents of 5-20 sentences each, all sharing the same concept cluster
- Adjacent sentences within a document = temporally-contiguous (same concept but varied phrasing)
- Document boundaries reset trace
- Cross-document adjacency = temporally non-contiguous

Compare cross-context concept HD similarity:
- `intra_concept_cross_context_cos`: for concept "cat", how similar are HDs when cat appears in sentence 3 of doc A vs sentence 12 of doc B? Target ≥ Spoke 1 v3-D baseline + 0.10 for FOLDIAK_TRACE (invariance lift)

## Metrics per arm × seed

- `intra_concept_cos_across_variants`: same concept, different sentence contexts → mean cosine of concept HDs (invariance target for FOLDIAK)
- `cat_kitten_cos`: cluster-similarity (should not regress from Spoke 1 v3-D baseline 0.52)
- `cat_airplane_cos`: cross-cluster separation (should not regress from -0.10)
- `sparse_rate`: architectural constraint (0.01-0.03)
- `invariance_lift`: intra_concept_cos_across_variants(FOLDIAK) - intra_concept_cos_across_variants(SPOKE1_ONLY_REPRO) — expect ≥ +0.15
- `shuffle_gap`: intra_concept_cos_across_variants(FOLDIAK) - intra_concept_cos_across_variants(TRACE_SHUFFLE_CONTROL) — expect ≥ +0.15 (temporal order is load-bearing)

## HP bands (HP_SCOPE: LOAD-BEARING on ARM_FOLDIAK_TRACE)

**HARD_PASS (target CG):**
- ARM_FOLDIAK_TRACE intra_concept_cos_across_variants ≥ 0.6 (invariance target)
- invariance_lift ≥ 0.15 (FOLDIAK beats SPOKE1_ONLY on invariance)
- shuffle_gap ≥ 0.15 (temporal-order-shuffle collapses invariance)
- ARM_FOLDIAK_TRACE cat/kitten cos ≥ 0.4 (no regression from Spoke 1 v3-D)
- ARM_FOLDIAK_TRACE cat/airplane cos ≤ 0.1 (no regression from Spoke 1 v3-D)
- sparse_rate ∈ [0.01, 0.03]
- 3 seeds independently HP; cv across seeds < 0.20

**HARD_FAIL:**
- ARM_FOLDIAK_TRACE invariance_lift ≤ 0.05 (Foldiak trace not adding invariance)
- OR shuffle_gap ≤ 0.05 (temporal order not doing work)
- OR discrimination regression: cat/kitten cos < 0.35 OR cat/airplane cos > 0.15

**MIDDLE_BAND:**
- invariance_lift ∈ (0.05, 0.15) — partial mechanism; v2 alpha tuning or Option C alternative

## Sanity + integration gates

- ARM_SPOKE1_ONLY_REPRO reproduces Spoke 1 v3-D FULL result within tolerance (|Δ_ck| < 0.03)
- ARM_TRACE_SHUFFLE_CONTROL confirms temporal order is load-bearing (shuffle should be at approximately SPOKE1_ONLY baseline, not lifted)
- ARM_TRACE_ALPHA_FAST provides alpha-sensitivity signal (should show intermediate invariance)

## Substrate primitives called

- Spoke 1 v3-D via `hdlab/concept_encoder.py` (post-Spoke-1-hdlab-extraction)
- `hdlab/char_positional_encoder.py` (from Spoke 1)
- NEW: `hdlab/temporal_trace.py` (~50 lines; exponential trace mechanism)
- Optional: `hdlab/sequence_memory.py::SequenceMatrix` for ARM_ADJACENT_PAIR_HEBB

## CELL-TEMPLATE MANDATORY compliance

Standard: arms_differ_verified (15/15), except SystemExit before except Exception, tmp_replace metrics, cardinality_ok, HP_SCOPE=LOAD_BEARING on FOLDIAK_TRACE, sparse-rate arch, ASCII-only, scale sentinel selftest at real N_DIM=8192, no bare except.

## Compute architecture

- (a) batched-CPU-torch or NumPy vectorized (same as Spoke 1)
- Per-seed smoke wall: ~2-5 min (2000 sentences × trace update)
- FULL wall: ~10-20 min (10K sentences)
- Route: local_cpu for smoke (USER SMOKE_ONLY_LOCAL); remote_cpu_queue for FULL

## Dispatch prereqs

1. Spoke 1 v3-D FULL landed CG (in flight; af849565)
2. `hdlab/concept_encoder.py` extraction landed post-Spoke-1-CG
3. Skunkworks SCHEMA-VET on this prereg
4. Cell authored + smoke gate on local_cpu
5. USER approval to dispatch FULL

## Post-verdict routing

**HARD_PASS at CG:**
- Extract Foldiak trace mechanism to `hdlab/temporal_trace.py` (compose with concept_encoder.py)
- Fire Spoke 3 (DG + Marr CA3 + CLS replay)
- Update KB migration plan Step 1 to incorporate temporal-contiguity training
- Consider META candidate 2 (6/6 drill convergence method) promotion — Spoke 2 CG is a strong second-witness that drill-recommended-PC-in-correct-role earns complexity

**HARD_FAIL:**
- File CG_HONEST_NEGATIVE Foldiak-in-substrate-HD; propose v2 with mechanism variant (SFA proper, adjacent-pair Hebbian, or hierarchical PC per Salvatori 2021)
- Spoke 3 dispatch NOT blocked (independent mechanism)

**MIDDLE_BAND:**
- File MM_TENTATIVE; v2 with alpha-tuning
- Spoke 3 dispatch NOT blocked

## Composability + META candidates

Composed Spoke 1 v3-D + Spoke 2 Foldiak-trace:
- Covers 4/6 brain properties (emerged, sparse-distributed, compositional via HRR, + NEW: invariance)
- Add Spoke 3 CG → 6/6 coverage (grounding + continually-updateable added)

If Spoke 2 CG: strong evidence for the drill-recommended composition — filing META candidate 2 (drill-methodology) as CG_META becomes justified (2-way witness: falsification correct + positive prediction correct).

## Estimated timeline (post-Spoke-1-CG + hdlab extraction)

- Cell authoring: ~30-45 min (hdi_exp_dev)
- Smoke: ~10-30 min (may need alpha tuning)
- SCHEMA-VET: ~5 min (Skunkworks)
- FULL dispatch: ~15-25 min wall
- Landed-VET: ~5 min
- If CG → hdlab extraction: ~30 min

Total: ~2-3 hours from Spoke 1 CG to Spoke 2 primitive availability.
