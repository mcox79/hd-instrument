# Pre-registration: community_bounded_retrieval_scale_invariance_v1

**Date:** 2026-07-08
**Cell:** `experiments/exp_community_bounded_retrieval_scale_invariance_v1.py`
**Design source:** `notes/research_reasoning_over_large_store_without_collapse_brain_first_2026-07-08.md`
(thread 4 + "Substrate-product implications" cheap decisive test).
**Barrier addressed:** BARRIER #3 -- the store gets crowded at massive scale
(additive-store crosstalk wall `M < N/(2 ln V)`).

## Hypothesis (the science question)

The brain defeats store crowding not by a bigger/sparser store (capacity-constant
levers) but by CHANGING THE DECODE REGIME: hippocampal indexing (store pointers,
near-orthogonal, decoupled from content) + community/small-world routing (route a
query to its community FIRST, then resolve only within it). This converts the
crosstalk-relevant codebook size from total-V (grows without bound) to
active-community size (bounded ~sqrt(V)). It is the one SCALE-INVARIANCE lever
(schema-consolidation + sparse-expansion only raise the capacity constant).

## Mechanism / arms

Store: V key-value pairs, keys/values near-orthogonal random bipolar, decoupled
(correlation-hurts-store law). Community structure lives in a SEPARATE routing
feature space (per-community gist pointer + per-item noise). Binding = elementwise
multiply (bipolar self-inverse). Readout = operational
`hdlab.cleanup_family.peel_sic_readout` (n_items=1 confidence-ordered cleanup;
composes to n_items>1 for multi-item answer sets).

- **CONTROL (dense-additive, must-collapse):** one GLOBAL bound bundle over all V
  pairs; retrieval unbinds a key, cleans up value against the WHOLE V codebook.
  Additive load = V; argmax over V. Reproduces `M < N/(2 ln V)`. SATURATION-VACUOUS
  GUARD arm: if it does not collapse, the crosstalk regime is not exercised.
- **TREATMENT (index + community, two-stage):** per-community bound bundles.
  Stage 1 coarse route: argmax over the community-gist codebook (~sqrt(V)
  near-orthogonal pointers). Stage 2 fine decode: unbind + peel/SIC cleanup within
  the selected community only (~sqrt(V) items). Effective codebook bounded ~sqrt(V).

## Fixed config

N=8192, Q_QUERIES=128, route_noise=0.6, arms={CONTROL,TREATMENT}.
- SMOKE: V in {580, 2900}; seeds [7, 17].
- FULL:  V in {580, 2900, 29000, 58000}; seeds [7, 17, 23].
comm_size = round(sqrt(V)); n_comm = ceil(V/comm_size).

## Bands (pre-registered BEFORE FULL; strict per META_RULE_L)

Relative degradation `rd = (fid(V_min) - fid(V_max)) / max(fid(V_min), eps)`.

**Discriminator-fires (MANDATORY):** CONTROL `rd >= 0.30` (dense-additive control
collapses). Enforced at smoke via `assert_discriminator_fires`.

**HARD_PASS (joint):** TREATMENT `rd <= 0.10` (flat) AND CONTROL `rd >= 0.30`
(collapses) AND TREATMENT abs fidelity at V_max `>= 0.70` (holds, not flat-broken)
AND coarse-route accuracy at V_max `>= 0.90` (not leaking) AND min Newman `Q >= 0.30`
(real community structure) AND cardinality_ok.

**HARD_FAIL:** TREATMENT degradation not distinguishable from CONTROL
(`treat_rd >= 0.5 * ctrl_rd`); OR route_acc collapses; OR modularity `Q < 0.30`
(generator void); OR CONTROL fails to collapse (`ctrl_rd < 0.30`, discriminator
inert -> result void); OR cardinality breach.

**MIDDLE_BAND:** `treat_rd < 0.5*ctrl_rd` but `treat_rd > 0.10` (partial mechanism;
route to community-size v2 + community-of-communities second tier).

## Calibration evidence (compute-formulas-in-code before quoting)

MEASURED off-disk (scratchpad calib, N=8192, seeds 7/17) BEFORE authoring:

- CONTROL fid: V=580 **0.742**, V=2900 **0.039**, V=29000 **0.000**, V=58000 **0.000** (rd~0.95)
- TREATMENT:   V=580 **1.000**, V=2900 **1.000**, V=29000 **1.000**, V=58000 **0.996** (rd~0.004)
- ROUTE acc:   **1.000** across all V (coarse-select does NOT leak with V)
- Newman Q:    **0.951 / 0.981 / 0.717 / 0.511** (all >> 0.30)

SMOKE (this cell, MEASURED@data/exp_community_bounded_retrieval_scale_invariance_v1_smoke/metrics.json):
CONTROL 0.797->0.023 (rd=0.971), TREATMENT 1.000->1.000 (rd=0.000), route=1.000,
Q_min=0.951 -> HARD_PASS; all 5 structured gate claims True; cardinality_ok (8/8).

FULL heaviest point timed: V=58000 single-seed wall **14.1s** (laptop .venv), peak
RAM ~6-8GB (four (58000,8192) f32 codebooks). Est FULL wall ~70-120s (3 seeds).

## SCHEMA-VET fields

```yaml
cardinality_ok: true                 # EXPECTED_N_UNITS = n_seeds*n_V*n_arms (FULL 3*4*2=24)
final_metrics_atomicity: tmp_replace # write_metrics tmp+os.replace
arms_differ_verified: true           # META_RULE_AF hash-test on CONTROL vs TREATMENT preds (smoke)
baseline_in_band: true               # CONTROL spans high(0.74)->collapsed(0), not saturated
discriminator_fires: true            # CONTROL rd>=0.30 enforced at smoke (assert_discriminator_fires)
calibration_check: default_ok_for_this_regime   # synthetic clean codes; no adaptive tuning
cell_chunked: true                   # single-file multi-seed with per-seed write_partial checkpoint (runner death loses <=1 seed)
start_marker_written: true
crash_diagnostic_present: true       # except SystemExit: raise; except Exception -> CELL_CRASHED
heartbeat_present: false             # wall<30min; per-V flush progress lines instead
defensive_error_checking: "start_marker + crash_metrics + per-seed checkpoint + per-V flush progress (no heartbeat; wall<2min)"
progress_logging: print_flush_true   # per-V print(flush=True); stdout line_buffered
run_mode_wiring: "default full; --smoke -> smoke; --self-test -> one tiny V then exit(0)"

# CRLB / capacity-feasibility (Plate 1995 / self-margin order-statistic)
crlb_floor_computed: 630             # reliable bundle capacity V* ~ N/(2 ln V), N=8192 -> ~630
crlb_formula_reference: "V* ~ N/(2 ln V) (Plate 1995 HRR bundle capacity)"
discriminator_reachability: true     # TREATMENT active load sqrt(V)<=241<630 feasible; CONTROL load V>=2900>630 collapse guaranteed

# gate A: effective vs nominal param
swept_params: {V: [580, 2900, 29000, 58000]}
effective_params_per_primitive:
  control_cleanup: effective_V = V                 # decodes against full store
  treatment_fine_decode: effective_V = sqrt(V)     # decodes against community only (BY DESIGN)
sweep_alignment_verdict: ALIGNED     # treatment effective-V decoupling from nominal-V IS the hypothesis under test

# gate B: discriminating band -- N/A (slope-contrast discriminator, not per-point accuracy)
discriminating_band_applicability: "N/A: the discriminator is the treatment-vs-control degradation-SLOPE contrast (CONTROL spans high->collapsed while TREATMENT stays flat), not per-sweep-point accuracy occupancy. The saturation-vacuous risk gate B guards is covered directly by assert_discriminator_fires (CONTROL must collapse >=0.30 at smoke V)."

# gate C: signal-shape compatibility
composition_edges:
  - {from: routing_cue, to: gist_codebook, verdict: SHAPE_MATCH}        # cosine argmax, N-dim
  - {from: unbind_estimate, to: peel_sic_cleanup, verdict: SHAPE_MATCH} # N-dim residual -> codebook argmax

# gate D: reproduce prior chain-grade primitive at test regime
positive_control_arms:
  - arm: CONTROL_at_Vmin_reproduces_plate_capacity
    primitive: hrr_bundle_capacity
    cited_prior_regime: "Plate 1995 V* ~ N/(2 ln V)"
    test_regime: {N: 8192, V: 580}
    note: "CONTROL=0.742 at V=580 consistent with operating just below cliff V*~630"

# gate E: functional requirements
functional_requirements:
  - {fr: "route query to relevant community without scanning whole store", primitive: "stage-1 community-gist argmax (NEW component)"}
  - {fr: "recover stored value from bounded local bundle", primitive: "unbind + peel_sic_readout (operational)"}
  - {fr: "keep store codes decoupled from routing semantics", primitive: "near-orthogonal K/Vv vs structured routing gist (operational: correlation-hurts-store law)"}
  - {fr: "bound decode cost by active-community size not total store", primitive: "two-stage coarse-route + fine-decode (NEW)"}
```

## Compute architecture

Class (c) mixed batched-numpy CPU: CONTROL cleanup is a single batched matmul
(Q,N)@(N,V) per V (already batched over queries; no python-loop matmul); TREATMENT
stage-2 is a per-query loop (128 iters, cheap, each a small community-scoped argmax).
Total wall ~70-120s FULL (heaviest V=58000 point = 14.1s/seed measured). GPU not
required (well under budget; the only heavy op is one BLAS call). Route: CPU.

## Dispatch

SMOKE: local (done, HARD_PASS). FULL: `remote_cpu_queue` (CPU-only; local is
smoke-only per USER lock). Multi-seed via single-file per-seed checkpoint
(restartable/pausable). Peak RAM ~6-8GB (four (58000,8192) f32 codebooks).

## Prior-work check

substrate_query "community-bounded two-stage retrieval hippocampal index pointer
store scale invariance crosstalk" -> top hit `hippocampal_index.py` cosine=0.2705
(Spoke-3 design note), BELOW 0.30. No prior arc cell builds two-stage
coarse-community-select then fine-decode retrieval. The design note itself flags
thread 4 (community routing) as the piece Spoke-3 does NOT include. GENUINELY NOVEL.
