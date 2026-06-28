# Prereg: substrate_cross_modal_binding_visual_auditory_v1

**Date:** 2026-06-28
**Author:** exp_dev (Opus 4.7 1M, agent-spawn) Stage 3 TPJ-analog characterization
**Drill source:** Research directive 2026-06-28 — characteristics table BACKUP UPDATE #25 lists "Cross-modal binding" as Stage 3 UNTESTED with completeness 0%, brain analog TPJ multisensory integration. Tests it now as a Stage 3 capability (testable on substrate primitives without M5-level cortex).
**Stage:** Stage 3 (compositional understanding — cross-modal entity binding)
**P_deflated:** 0.50 (could be HARD_PASS via interchangeable random-codebook symmetry OR HARD_FAIL via non-trivial binding-symmetry break; either result fills the characteristics table)
**Phase-diagram axis:** binding success rate over (K, N, mechanism) when binding entities across two independent modality codebooks

## SUBSTRATE-AS-CANONICAL prior work

- `exp_substrate_sequence_binding_v1` atom (chain-grade at K=20): HRR pos-item bind in single codebook. Cross-modal is the natural extension to TWO codebooks.
- `exp_substrate_sequence_binding_K_cliff_phase_diagram_v1` (2026-06-28): K-cliff phase coverage for single-codebook HRR. Mechanism precedent.
- `exp_substrate_task_vector_K_cliff_phase_diagram_v1` (2026-06-28; chunked template). Sibling-per-seed architecture pattern.
- BIAS-Q (USER 2026-06-24): suspect 1.000 results. Codebook independence is by-construction here, so we must verify discrimination is mechanism-load-bearing not random-coincidence.

## HYPOTHESIS

**Cross-modal binding** = the substrate encodes an entity that exists in TWO codebooks (modality A "visual" V[i], modality B "auditory" A[i]) simultaneously; retrieve from one modality given a query in the other.

Three candidate binding mechanisms swept:
- **HRR_bind**: C = sum_i bind(V[i], A[i]); query V[i] -> unbind(C, V[i]) -> A_hat. The substrate-native binding op.
- **sum_then_query**: C = sum_i (V[i] + A[i]) (naive superposition; no bind). Query V[i] -> subtract V[i] from C. Should FAIL at K>=10 because superposition mixes all auditory items.
- **position_key_bind**: C = sum_i [bind(P_i, V[i]) + bind(P_i, A[i])]. Query (V[i], P_i): unbind(P_i, C) -> noisy (V[i]+A[i]); subtract V[i] -> A_hat. Tests whether routing-via-position works.

**Symmetry intuition** (USER vetting input): codebooks A and B are interchangeable i.i.d. bipolar random matrices. HRR_bind is symmetric (a tensor b = b tensor a in FFT). So we expect cross-modal HRR_bind to match within-modal HRR_bind (HARD_PASS path).

**Possible HARD_FAIL paths**:
- HRR bind/unbind has implicit asymmetry on real codebooks (we measure it)
- Modality A vs B identity matters (we sample fresh per phase point; should not)
- Inter-codebook noise term breaks the cleanup-via-modality-B step

## SWEEP AXES

- **K (entities per modality) ∈ {10, 50, 100, 500, 1000}** (5 points; brackets HRR K-cliff)
- **N (substrate dimensionality) ∈ {2048, 4096, 8192}** (3 points)
- **bind_mechanism ∈ {HRR_bind, sum_then_query, position_key_bind}** (3 points)
- **= 45 phase points per seed**

## DISCRIMINATOR ARMS (3) — per phase-point

1. **BIND_CROSS_MODAL** — substrate-bound; query A[i] -> retrieve B[i]; report cosine(B_hat, B[i]) + top1_recall. **The mechanism.**
2. **NO_BIND_BASELINE** — substrate is a random vector (NOT containing the bind info); cleanup vs modality-B codebook. **Floor: chance retrieval ~ 1/V_MOD_B.**
3. **WITHIN_MODAL_BIND_CONTROL** — same mechanism but binds A[i] <-> A[shifted(i)] within modality A. Query A[i] -> retrieve A[shifted(i)]. **Within-modal benchmark (HRR sense).**

**arms-must-differ** at HARD_PASS: BIND_CROSS_MODAL > NO_BIND_BASELINE by >= 0.40 lift at >= 10 of 45 grid points; BIND_CROSS_MODAL matches WITHIN_MODAL_BIND_CONTROL within 0.20 abs-diff at >= 10 of 45 grid points.

## PRE-REG BANDS (LOCKED; PROSPECTIVE; metric = top1_recall in [0,1])

- **HARD_PASS** (Stage 3 cross-modal binding CHARACTERIZED):
  - Bind-lift discriminator: BIND_CROSS_MODAL - NO_BIND_BASELINE >= 0.40 at AT LEAST 10 of 45 phase points
  - Cross-vs-within match: |BIND_CROSS_MODAL - WITHIN_MODAL_BIND_CONTROL| <= 0.20 at AT LEAST 10 of 45 phase points (cross-modal ~ within-modal as HRR symmetry predicts)
  - Positive control: K=10, N=8192, HRR_bind: BIND_CROSS_MODAL >= 0.95 (well-tested regime)
  - Not by-construction saturated (not all 45 points >= 0.99)

- **MIDDLE_BAND**:
  - Bind-lift discriminator at 3-9 phase points
  - OR cross-vs-within match at 3-9 phase points
  - OR positive control failed (regime-narrow mechanism)
  - OR HRR_bind works but the other mechanisms collapse to floor (i.e., specific mechanism not general)

- **HARD_FAIL**:
  - All 45 BIND_CROSS_MODAL recalls >= 0.99 (by-construction saturation — sweep didn't reach cliff)
  - OR avg |BIND_CROSS_MODAL - NO_BIND_BASELINE| < 0.05 (mechanism not load-bearing; broken arms)
  - OR positive control < 0.95 AND BIND_CROSS_MODAL <= NO_BIND_BASELINE at all HRR_bind points

**HEADLINE per phase point:** {K, N, mech, BIND_CROSS, NO_BIND, WITHIN, lift, cw_diff}

## FAIRNESS GATES (META_RULE_AC/AE/AF)

- Same encoder (HRR bipolar random; FFT bind) across all 3 mechanism options.
- Independent modality codebooks: book_a, book_b, book_pos all sampled fresh per phase point via different random draws — statistically i.i.d.
- Same K positions sampled without replacement across BIND_CROSS_MODAL and WITHIN_MODAL_BIND_CONTROL arms (compares same items in same positions, just different bind targets).
- NO_BIND_BASELINE uses a random vec for the bundle (same distribution); cleanup is identical against same codebook.
- Q-discipline: positive control K=10 N=8192 HRR_bind top1 = 1.000 is EXPECTED (not leakage); audit triggered only if K>=500 N=2048 HRR_bind top1 = 1.000 (would imply mechanism beats Plate capacity = bug).

## CARDINALITY (META_RULE_H_ANCHOR)

- **EXPECTED_N_UNITS_FULL per seed** = 3 arms × 45 pts × 20 queries = **2700 records per seed**
- **EXPECTED_N_UNITS_SMOKE per seed** = 3 arms × 6 corners × 4 queries = **72 records per seed**
- **EXPECTED_N_SEEDS** = 3 chunked siblings (seed 7, 13, 19)
- **EXPECTED_N_UNITS_AGGREGATE_FULL** = 2700 × 3 = **8100 records**

CARDINALITY_OK declared in metrics: `cardinality_ok = (observed_n == expected_n)` per sibling.

## DISCRIMINATOR-SURVIVES-SCALE (USER 2026-06-26)

Smoke 6 corners (verified analytically — HRR cleanup capacity ~ sqrt(N/4) bundles):

| corner                                 | K    | N    | mech            | expected BIND_CROSS |
|----------------------------------------|------|------|-----------------|---------------------|
| low-K high-N HRR (positive control)    | 10   | 8192 | HRR_bind        | HIGH (>= 0.95)      |
| high-K low-N HRR (cliff)               | 1000 | 2048 | HRR_bind        | LOW (< 0.10)        |
| low-K low-N sum_then_query             | 10   | 2048 | sum_then_query  | MID (0.2-0.7) — sum works only at K<= ~5 cleanly |
| high-K high-N sum_then_query           | 1000 | 8192 | sum_then_query  | LOW (< 0.05)        |
| mid position_key_bind                  | 100  | 4096 | position_key    | MID-LOW (0.1-0.4) — pos-key adds noise |
| higher-K position_key_bind             | 500  | 8192 | position_key    | LOW (< 0.10)        |

Smoke gate (BLOCK full dispatch if not met):
- 6 corners all RUN (no silent except)
- positive control corner (K=10, N=8192, HRR) BIND_CROSS >= 0.95
- cliff corner (K=1000, N=2048, HRR) BIND_CROSS < 0.20
- at least 2 corners show BIND_CROSS > NO_BIND by >= 0.30 lift
- at least 1 corner shows BIND_CROSS < 0.10 (cliff observable)
- cardinality_ok (observed_n == 72)

If smoke gate fails: ABORT full dispatch. Re-author cell with corrected mechanism or extended sweep.

## HARDENING

L1 STARTED early-write + L2 per-arm progress + L3 outer try/except + L4 import-crash sentinel + atomic per-seed partial via `experiments._seed_checkpoint`. META_RULE_X main-guard. PROT-021 anchor stamp on every partial.

## CPU FIRST (per task spec)

- Hardware: CPU (task spec); torch.cpu primary; torch.cuda fallback OK if available.
- HRR bind/unbind via FFT — N=8192 K=1000 FFT batch ~ 0.5-1.0s per phase point on CPU.
- No GPU profiling required per task spec ("CPU; ~5min per seed").
- Memory: N=8192 × float32 × 2048(V) ≈ 64MB per codebook; three codebooks ≈ 200MB. Fits laptop RAM easily.

## CHUNKED ARCHITECTURE (USER 2026-06-28)

3 sibling files (one seed each):
- `exp_substrate_cross_modal_binding_visual_auditory_v1_seed_7.py`
- `exp_substrate_cross_modal_binding_visual_auditory_v1_seed_13.py`
- `exp_substrate_cross_modal_binding_visual_auditory_v1_seed_19.py`

Shared core: `experiments/_substrate_cross_modal_binding_visual_auditory_v1_core.py`
Resumability: `experiments/_seed_checkpoint.py` (PROT-021 anchor + run_mode stamping).

Aggregation post-hoc: combine 3 sibling metrics.json -> phase-map matrix; verdict computed per-sibling AND combined at Skunkworks landed-VET.

## COMPUTE

- Smoke (1 seed × 6 corners × 3 arms × 4 queries = 72 records): ~30-60 sec CPU
- Full sibling (1 seed × 45 phase points × 3 arms × 20 queries = 2700 records): ~5-10 min CPU
- 3 sibling FULL aggregate: ~15-30 CPU-min
- Timeout: smoke 1800s (3 min cap inside queue_add); full 1200s per sibling (task spec)

## SUBSTRATE PREREQS (chain-grade primitives cited)

- HRR bind / unbind (FFT-based; chain-grade per `exp_substrate_sequence_binding_v1`)
- Bundle (additive sum + L2 normalize)
- Cleanup via cosine argmax over modality codebook
- Independent modality codebooks = independent bipolar random matrices

## PHASE-DIAGRAM DECISION TABLE

| Smoke + Full outcome                              | Phase-diagram verdict                                                 |
|--------------------------------------------------|-----------------------------------------------------------------------|
| HARD_PASS — disc >= 10 + cw_match >= 10 + pos_ctrl | Cross-modal binding chain-grade-eligible (TPJ-analog primitive confirmed) |
| MIDDLE_BAND — disc 3-9 or specific mechanism only | Cross-modal binding regime-narrow (HRR works; sum/pos_key don't generalize) |
| HARD_FAIL — saturated or arms identical            | Cross-modal binding broken; mechanism not load-bearing — author v2     |

## NOTES

- Fills characteristics table UNTESTED entry: Stage 3 "Cross-modal binding" (TPJ-analog).
- HARD_PASS = trivial (substrate supports cross-modal HRR-bind by codebook symmetry).
- HARD_FAIL = non-trivial (some binding-symmetry break we didn't predict).
- MIDDLE_BAND = mechanism-specific (HRR works; others don't) — informs which mechanism families generalize.
- Per USER 2026-06-26 stage progression: Stage 3 work (compositional understanding); does NOT depend on Stage 4 LM-equivalence.
- Per USER 2026-06-27 substrate-as-canonical: builds on cert atom from `exp_substrate_sequence_binding_v1`.
- Per USER 2026-06-28 chunked architecture: 3 sibling files mirroring `substrate_sequence_binding_K_cliff_phase_diagram_v1`.
