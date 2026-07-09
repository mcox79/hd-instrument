# Pre-registration: community_of_communities_nested_retrieval_v2

**Date:** 2026-07-08
**Cell:** `experiments/exp_community_of_communities_nested_retrieval_v2.py`
**Builds on:** `experiments/exp_community_bounded_retrieval_scale_invariance_v1.py`
(commit cc804bfc1) + `preregs/2026-07-08_community_bounded_retrieval_scale_invariance_v1.md`
**Barrier addressed:** BARRIER #3 completion -- store crowding at massive scale,
FULL scale-invariance (both total-V AND per-community load bounded).

## What v1 proved and the gap it left

v1 (HARD_PASS, MEASURED@data/exp_community_bounded_retrieval_scale_invariance_v1/metrics.json):
single-tier community routing decouples crosstalk from TOTAL store size V
(TREATMENT flat fid=1.000 across V=580..58000 while CONTROL global-additive
collapsed rd=1.000). But v1's flatness holds ONLY because per-community load =
round(sqrt(V)) stayed below the FHRR bundle-capacity Plate cliff (~630 at
N=8192). The VET's isolation MEASURED the within-community cliff: a SINGLE
community whose OWN load crosses the cliff still collapses --
comm load 241->0.992, 630->0.680, 1000->0.313, 2000->0.094. So single-tier
routing is NOT scale-invariant in per-community LOAD; a coarse community
structure (few large communities) still collapses.

## Hypothesis (the science question)

A NESTED community-of-communities (2nd routing tier INSIDE each community) holds
each leaf-community's decode load below the cliff regardless of per-community
load L and regardless of total V, giving FULL scale-invariance. The v2-nested
treatment stays FLAT along the per-community-load axis where the v1-flat
single-tier control COLLAPSES.

## Mechanism / arms (identical store + identical tier-1 route; the ONLY
difference is the 2nd tier -> clean paired comparison)

Nested generator: n_comm super-communities, each of load L. Within a super, L
items partitioned into n_leaf = ceil(sqrt(L)) leaf-communities of size ~sqrt(L).
Leaves nest within supers (leaf partition is a STRICT refinement of the super
partition: leaf_of = super*n_leaf + local_leaf). Store codes near-orthogonal
random bipolar, keys/values decoupled (correlation-hurts-store law). Tier-1 and
tier-2 gists in SEPARATE near-orthogonal routing spaces. Binding = elementwise
multiply (bipolar self-inverse). Readout = operational
`hdlab.cleanup_family.peel_sic_readout` (n_items=1).

- **SINGLE_TIER (v1-flat control, must-collapse under per-community overload):**
  route tier-1 to super; unbind + peel/SIC over the WHOLE super bundle (L pairs,
  argmax over L). Reproduces the within-community cliff; collapses as L crosses
  ~630. SATURATION-VACUOUS GUARD arm: if it does not collapse at the stressed L,
  the cliff regime is not exercised -> result void.
- **NESTED (v2 treatment, should stay flat):** same tier-1 route to super, THEN
  tier-2 route to leaf, unbind + peel/SIC over the leaf bundle only (~sqrt(L)
  pairs). Effective decode load bounded ~sqrt(L).

## Fixed config

N=8192, Q_QUERIES=128, route_noise=0.5, arms={SINGLE_TIER, NESTED}.
- SMOKE: L in {256, 4000} (spans cliff); n_comm in {3}; seeds [7, 17].
- FULL:  L in {256, 630, 1600, 4000}; n_comm in {4, 12}; seeds [7, 17, 23].
n_leaf = ceil(sqrt(L)); leaf_size = ceil(L / n_leaf). V = n_comm * L (1024..48000).

## Bands (pre-registered BEFORE FULL; strict per META_RULE_L)

Relative degradation over the per-community-load axis
`rd_L = (fid(L_min) - fid(L_max)) / max(fid(L_min), eps)`.

**Discriminator-fires (MANDATORY):** SINGLE_TIER `rd_L >= 0.30` (v1-flat control
collapses under per-community overload). Enforced at smoke via
`assert_discriminator_fires`. If it does not fire -> VacuousSmokeError.

**HARD_PASS (joint):** NESTED `rd_L <= 0.10` (flat) AND SINGLE_TIER `rd_L >= 0.30`
(collapses) AND NESTED abs fidelity at L_max `>= 0.70` (holds, not flat-broken)
AND tier-1 route acc `>= 0.90` AND tier-2 route acc `>= 0.90` (neither tier
leaking) AND min Newman `Q_super >= 0.30` AND min Newman `Q_leaf >= 0.30` (real
nested structure at BOTH tiers) AND cardinality_ok.

**HARD_FAIL:** NESTED degradation not distinguishable from SINGLE_TIER
(`ne_rd_L >= 0.5 * st_rd_L`); OR either route acc collapses; OR `Q_super < 0.30`
or `Q_leaf < 0.30` (generator void); OR SINGLE_TIER fails to collapse
(`st_rd_L < 0.30`, discriminator inert -> result void); OR cardinality breach.

**MIDDLE_BAND:** `ne_rd_L < 0.5*st_rd_L` but `ne_rd_L > 0.10` (partial: leaf load
still near cliff or a 3rd tier needed).

**Total-V invariance (soft telemetry gate):** NESTED fidelity spread across
n_comm at fixed L `<= 0.15` (confirms v1's total-V decoupling persists).

## Calibration evidence (compute-formulas-in-code before quoting)

THEORETICAL@Plate 1995: cliff V* ~ N/(2 ln V) ~ 630 at N=8192.
SINGLE_TIER decode load = L: L=256 below cliff, L=4000 >> cliff -> collapse
guaranteed. NESTED leaf load = ceil(L/ceil(sqrt(L))) ~ sqrt(L): L=4000 -> 63 <<
cliff. Within-community cliff numbers MEASURED@ the v1 VET isolation.

SMOKE (this cell, MEASURED@data/exp_community_of_communities_nested_retrieval_v2_smoke/metrics.json):
SINGLE_TIER L=256 fid 0.992/1.000 -> L=4000 fid 0.023/0.016 (rd_L=0.980 COLLAPSE);
NESTED 1.000 -> 1.000 (rd_L=0.000 FLAT); tier1=1.000 tier2=1.000; Q_super=0.666
(= k=3 modularity ceiling 1-1/k), Q_leaf=0.937-0.980; v_inv=0.000 -> HARD_PASS;
all 8 structured gate claims True; cardinality_ok (8/8).

Heaviest FULL point timed: (L=4000, n_comm=12, V=48000) single-seed wall 16.8s
(laptop .venv), peak ~5-8GB (four (48000,8192) f32 arrays). Q_super=0.916 there
(= k=12 ceiling). Est FULL wall ~120-250s (3 seeds x 8 points).

## SCHEMA-VET fields

```yaml
cardinality_ok: true                 # EXPECTED_N_UNITS = n_seeds*n_L*n_ncomm*n_arms (FULL 3*4*2*2=48)
final_metrics_atomicity: tmp_replace # write_metrics tmp+os.replace
arms_differ_verified: true           # META_RULE_AF hash-test (SINGLE_TIER vs NESTED preds)
arms_differ_exempted:                # both-perfect points legitimately share output
  - pair: [SINGLE_TIER, NESTED]
    rationale: "at an easy per-community load L below the cliff BOTH arms recover ground truth perfectly, so both prediction vectors equal qidx and hash identically (correctness, not a shared-code-path bug). Exemption bounded: identical-hash allowed ONLY when st_fid>=0.999 AND ne_fid>=0.999; AND arms MUST differ at the stressed L_max point (enforced in _smoke_gates)."
baseline_in_band: true               # SINGLE_TIER spans high(~1.0 at L=256)->collapsed(~0.02 at L=4000), not saturated
discriminator_fires: true            # SINGLE_TIER rd_L>=0.30 enforced at smoke (assert_discriminator_fires); MEASURED 0.980
calibration_check: default_ok_for_this_regime   # synthetic clean codes; no adaptive tuning
cell_chunked: true                   # single-file multi-seed with per-seed write_partial checkpoint (runner death loses <=1 seed)
start_marker_written: true
crash_diagnostic_present: true       # except SystemExit: raise; except Exception -> CELL_CRASHED
heartbeat_present: false             # wall<5min; per-point flush progress lines instead
defensive_error_checking: "start_marker + crash_metrics + per-seed checkpoint + per-point flush progress (no heartbeat; wall<5min)"
progress_logging: print_flush_true   # per-point print(flush=True); stdout line_buffered
run_mode_wiring: "default full; --smoke -> smoke; --self-test -> one stressed point then exit(0)"

# CRLB / capacity-feasibility (Plate 1995 bundle capacity)
crlb_floor_computed: 630             # V* ~ N/(2 ln V), N=8192 -> ~630
crlb_formula_reference: "V* ~ N/(2 ln V) (Plate 1995 HRR bundle capacity)"
discriminator_reachability: true     # NESTED leaf load sqrt(L)<=63<630 feasible; SINGLE_TIER load L up to 4000>630 collapse guaranteed

# gate A: effective vs nominal param
swept_params: {L: [256, 630, 1600, 4000], n_comm: [4, 12]}
effective_params_per_primitive:
  single_tier_decode: effective_load = L                       # decodes whole super bundle
  nested_leaf_decode: effective_load = ceil(L/ceil(sqrt(L)))   # ~sqrt(L), decodes leaf only (BY DESIGN)
sweep_alignment_verdict: ALIGNED     # the effective-load decoupling of NESTED from nominal L IS the hypothesis under test; both arms independent of total-V by routing (confirmed v_inv gate)

# gate B: discriminating band -- N/A (slope-contrast discriminator, not per-point accuracy occupancy)
discriminating_band_applicability: "N/A: discriminator is the NESTED-vs-SINGLE_TIER degradation-SLOPE contrast over the per-community-load axis (SINGLE_TIER spans high->collapsed while NESTED stays flat), not per-sweep-point accuracy occupancy. Saturation-vacuous risk covered directly by assert_discriminator_fires (SINGLE_TIER must collapse >=0.30 at the smoke's full L=4000)."

# gate C: signal-shape compatibility
composition_edges:
  - {from: routing_cue_tier1, to: super_gist_codebook, verdict: SHAPE_MATCH}   # cosine argmax, N-dim
  - {from: routing_cue_tier2, to: leaf_gist_codebook, verdict: SHAPE_MATCH}    # cosine argmax over super's leaf slice, N-dim
  - {from: unbind_estimate, to: peel_sic_cleanup, verdict: SHAPE_MATCH}        # N-dim residual -> codebook argmax

# gate D: reproduce prior chain-grade primitive at test regime
positive_control_arms:
  - arm: SINGLE_TIER_reproduces_v1_within_community_cliff
    primitive: within_community_fine_decode (v1 treatment stage-2)
    cited_prior_regime: "v1 VET isolation N=8192: comm load 630->0.680, 2000->0.094"
    cited_prior_metric: 0.094
    test_regime: {N: 8192, L: 4000}
    note: "SINGLE_TIER at L=4000 MEASURED 0.02-0.03 in smoke, consistent with v1 within-community collapse extrapolated past L=2000 (0.094). SINGLE_TIER at L=256 (below cliff) ~1.0 reproduces the below-cliff regime."
    regime_extension_audit: SHAPE_MATCH   # identical decode primitive; only the bundle load L varies

# gate E: functional requirements
functional_requirements:
  - {fr: "route query to its super-community without scanning whole store", primitive: "tier-1 super-gist argmax (v1 primitive)"}
  - {fr: "route within super to leaf-community", primitive: "tier-2 leaf-gist argmax restricted to super slice (NEW 2nd tier)"}
  - {fr: "recover stored value from a bounded leaf bundle below the cliff", primitive: "unbind + peel_sic_readout (operational)"}
  - {fr: "keep store codes decoupled from routing semantics at both tiers", primitive: "near-orthogonal K/Vv vs separate super/leaf gists (correlation-hurts-store law)"}
  - {fr: "bound decode load by leaf size ~sqrt(L) not per-community load L", primitive: "nested two-tier route + leaf-scoped fine-decode (NEW)"}
```

## Compute architecture

Class (c) mixed batched-numpy CPU: bundle builds via np.add.at; tier-1 route one
batched matmul (Q,N)@(N,n_comm); tier-2 route a per-query small argmax
(n_leaf ~ sqrt(L) candidates); fine-decode grouped by predicted super/leaf
(batched peel per group). Heaviest point 16.8s/seed. GPU not required (well under
budget; heavy ops are BLAS + np.add.at). Route: CPU. Storage strategy: SHARDED
per-leaf bundles (each leaf its own bundle); the SINGLE_TIER control uses the
coarser per-super bundle (the arm under test for overflow).

## Dispatch

SMOKE: local (done, HARD_PASS). FULL: `remote_cpu_queue` (CPU-only; local is
smoke-only per USER lock). Multi-seed via single-file per-seed checkpoint
(restartable/pausable). Peak RAM ~5-8GB. Timeout 1200s (est wall ~120-250s;
5x margin for remote-CPU slowdown).

## Prior-work check

substrate_query "nested community of communities two-tier hierarchical routing
bounded retrieval scale invariance store crowding" -> top hit "Hierarchical
Routing" cosine=0.3018 (Tier-5c LLM-inference routing note), plus WordNet
"community" atoms. The top hit is LLM-inference domain routing, NOT the VSA
additive-store crosstalk / Plate-cliff domain this cell operates in. No prior arc
cell builds a 2nd routing tier over per-community FHRR bundles to hold each leaf
below the bundle-capacity cliff. GENUINELY NOVEL for the store-capacity arc (not
a rediscovery). KB dogfood rating: MEDIOCRE (returned superficially-related
hierarchical-routing from the wrong domain; did not surface the v1 community cell
or the correlation-hurts-store law that are the actual priors).
