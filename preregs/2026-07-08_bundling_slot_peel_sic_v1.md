# Pre-reg: bundling_slot_peel_sic_v1

**Filed:** 2026-07-08 by hdi_exp_dev
**Cell:** `experiments/exp_bundling_slot_peel_sic_v1.py`
**Anchor:** `bundling_slot_peel_sic_v1`
**Source drill:** `notes/research_bundling_capacity_beyond_fixed_N_theta_gamma_chunking_sparse_2026-07-08.md` (Rank 1, P_deflated=0.48)
**Reuses:** theta-gamma v2 FHRR phasor codebook/bind (`notes/director_theta_gamma_v2_FHRR_all_complex_design_spec_2026-06-30.md`, CHAIN_GRADE); resonator slot-peel deflation decode (`experiments/exp_resonator_theta_gamma_peel_v1.py`, MEASURED_MECHANISM).

## Question
Does theta-gamma time-SLOTTING + SEQUENTIAL CANCELLATION (peel/deflate) beat the flat fixed-N
additive-bundling superposition wall for J-item bundling recall?

## Prior-work check (substrate-KB concept-query, mandatory)
`bash tools/substrate_query.sh "theta gamma phase slot sequential cancellation deflation bundling capacity additive superposition"` -> top cosine 0.3652 ("Calibration deflation", an unrelated N-scaling note) and 0.3408 ("deflation", wordnet economic term). **NONE at cosine>0.30 is a prior slot-peel-for-bundling cell.** This combination (slot-peel decode pointed at the ADDITIVE bundling task) is genuinely novel; prior slot-peel work was multiplicative K-way factorization (resonator).

## Design (5 arms, PAIRED per trial from a shared vocabulary codebook + shared true item set)
Two encodings per trial: FLAT sum `Sf = sum_j book[item_j]`; SLOT sum `Ss = sum_j slot_j (*) book[item_j]`.
Item codebook = near-orthogonal random FHRR phasors (V items). Slot carriers = random near-orthogonal phasors.
Items sampled without replacement (J distinct). Metric = SET recall `|pred_set ∩ true_set| / J`.

1. **FLAT_TOPJ** -- Sf, cleanup vs full vocab, top-J. Frontier/negative control (must degrade at high J).
2. **FLAT_PEEL** -- Sf, iterative greedy SIC / matching pursuit (global argmax -> deflate -> repeat J). NO slots.
3. **SLOT_NODEFLATE** -- Ss, per-slot unbind + argmax, no cancellation (slotting alone).
4. **SLOT_PEEL_FIXED** -- Ss, per-slot peel in fixed order 0..J-1 (resonator loop retargeted to shared vocab).
5. **SLOT_PEEL_POWER** -- Ss, per-slot peel in DESCENDING confidence order (SPARC/SIC decoding wave).

## Regime
- FULL: V=2000; N_GRID={256, 512}; J_BY_N={256:[8,16,32,48,64], 512:[16,32,64,96]}; TR=60; seeds=[7,13,19].
- SMOKE: V=1000; N=192; J=[16,32,48]; TR=20; seeds=[7,13]. (same arms + same decoders + same verdict path)
- EXPECTED_N_UNITS (full) = (5+4) * 3 = 27 units (one per seed,N,J). `cardinality_ok: true`.

## Bands (HYPOTHESIZED@this prereg, grounded in this-session pilot calibration on scratchpad)
Shoulder-J(N) = smallest J with FLAT_TOPJ_mean in [0.70, 0.90].
- **CAPABILITY HARD-PASS** (wall beaten): at a shoulder-J, `max(FLAT_PEEL, SLOT_PEEL_POWER) >= FLAT_TOPJ + 0.10` AND `>= 0.95` AND cv<=0.10.
- **MECHANISM ATTRIBUTION** (reported; refines the drill's theta-gamma claim):
  - `slotting_alone_null`: SLOT_NODEFLATE <= FLAT_TOPJ + 0.05
  - `slots_unnecessary`: |SLOT_PEEL_POWER - FLAT_PEEL| <= 0.05  (=> attribute lift to CANCELLATION, not theta-gamma slots)
  - `ordering_loadbearing`: SLOT_PEEL_POWER - SLOT_PEEL_FIXED >= 0.10
- **MIDDLE_BAND**: cancellation beats flat at some (N,J) but does not clear the full capability bar.
- **HARD-FAIL** (wall stands): best cancellation arm <= FLAT_TOPJ + 0.05 at every (N,J) -> two-head fixed-N wall confirmed fundamental.
- **VACUOUS/MIDDLE_BAND** (discriminator-fires guard, META_RULE_AG): if FLAT_TOPJ never enters/below the shoulder window, regime too easy -> demote, do not tier.

## SMOKE RESULT (MEASURED@data/exp_bundling_slot_peel_sic_v1_smoke/metrics.json)
verdict=HARD_PASS; shoulder N192_J32: FLAT_TOPJ=0.829, FLAT_PEEL=1.000, SLOT_PEEL_POWER=0.997,
SLOT_PEEL_FIXED=0.655, SLOT_NODEFLATE=0.592; cancel_lift=+0.171; cv=0.000; arms_distinct_at_hardest=5;
discriminator_fires=True; slotting_alone_null=True; slots_unnecessary=True; ordering_loadbearing=True.

## KEY REFRAMING (surfaced by smoke/pilot -- for Director + Skunkworks)
1. Clean near-orthogonal synthetic phasor codes do NOT reproduce the real encoder's ~0.20@J8 collapse
   (FLAT_TOPJ holds ~1.0 well past J=12 at these N). The real 0.20 is an encoder-EMBEDDING-GEOMETRY
   (correlation-law) artifact, NOT a clean-code capacity limit. The discriminator here is the ARM GAP at
   the capacity shoulder, not a 0.20 floor. FLAT_TOPJ still degrades gracefully with J (fires the gate).
2. The load-bearing mechanism is CANCELLATION (matching pursuit / SIC), NOT theta-gamma slotting:
   FLAT_PEEL (cancellation, no slots) matches SLOT_PEEL_POWER; phase slots add nothing (slightly hurt via
   slot-key crosstalk). This confirms the SIC half and REFUTES the theta-gamma-slotting attribution in the drill.
3. CONFIDENCE-ORDERING is essential: naive fixed-order peel (resonator's loop) mis-deflates at high J and
   loses badly; the SPARC decoding-wave (resolve most-confident slot first) repairs it.

## SCHEMA-VET fields
- `cardinality_ok: true` (EXPECTED_N_UNITS=27 counted in verdict; HARD_FAIL_CARDINALITY on mismatch)
- `arms_differ_verified: true` (>=3 of 5 arm-winner-sets distinct at hardest cell; smoke got 5/5)
- `final_metrics_atomicity: tmp_replace` (write_metrics + per-seed partials)
- `except SystemExit: raise` before `except Exception` (no BaseException; grep-clean)
- `discriminator_reachability: true` (bands bracket the shoulder lift; pilot-grounded reachable)
- `baseline_in_band: true` (FLAT_TOPJ lands in [0.70,0.90] at the shoulder; verified in smoke)
- `discriminator_survives_scale: shoulder-relative` (arm gap measured AT each N's shoulder; N-invariant by construction; confirmed at N=256/512 timing probes: FLAT_PEEL/POWER beat FLAT_TOPJ)
- `crlb_n/a`: set-recall of near-orthogonal codes has no single Cramer-Rao noise-floor threshold; capacity feasibility handled by shoulder-relative bands + pilot bracket.
- `calibration_check: default_ok_for_this_regime` (clean synthetic near-orthogonal codes; no adaptive tuning; slot near-orthogonality asserted g<0.30 in selftest)
- `correlation_law_compliant: true` (slot carriers near-orthogonal random; no store-side correlation injected by the mechanism; asserted in selftest)
- `cell_chunked: false` (single-file, seeds via _seed_checkpoint partials + resumable_seeds)
- `start_marker_written: true`; `crash_diagnostic_present: true` (Exception -> CELL_CRASHED + traceback); `heartbeat_present: true`
- `progress_logging: print_flush_true` (line-buffered stdout + flush=True per cell + heartbeat)
- `run_mode` verification: cell defaults run_mode=full; smoke via --smoke; FULL landed metrics must show run_mode=full, size>5KB.

## Composition-gate audit (§15)
- sweep_alignment_verdict: ALIGNED (J and N are the swept axes; every arm experiences the actual J,N; no nominal-vs-effective mismatch).
- discriminating_fraction: >=0.30 (pilot: shoulder cells at J in [24..64 depending on N] land FLAT_TOPJ in [0.70,0.90]; >=1 per N in band).
- composition_edges: single primitive family (FHRR phasor cleanup + deflation); no cross-primitive shape-mismatch.
- positive_control: FLAT_TOPJ reproduces the graceful additive-bundling decay (the frontier control) in-run; FLAT_PEEL is the matching-pursuit reference. Both measured in-run at test regime.
- functional_requirements: (a) recover J-item bundle set -> cleanup/matching-pursuit; (b) isolate cancellation vs slotting -> the 5-arm dissociation; (c) isolate ordering -> FIXED vs POWER.

## Compute architecture
Class (b) sequential-CPU with justification: peel/matching-pursuit is genuinely sequential (each deflation
depends on the prior resolved item). Per-round slot cleanup is BLAS-batched (one matmul per round). Sizes
small (N<=512, V<=2000). Measured worst full cell N=512/J=64/TR=40 = 32s/seed; estimated FULL total ~11min.
GPU batching not warranted (sequential dependency + small matmuls + short wall time).

## Dispatch
- Target queue: `remote_cpu_queue` (CPU cell; FULL must NOT go to local per SMOKE-ONLY-local USER lock).
- Timeout: 3600s (3x headroom over ~11min estimate; remote CPU may be slower).
- Pause state ACTIVE at authoring: FULL dispatch handed off to orchestrator; not shipped by exp_dev.
