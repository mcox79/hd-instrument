# Pre-registration: grounding_consolidation_loop_degree_invariant_v1

Date: 2026-07-10
Cell: `experiments/exp_grounding_consolidation_loop_degree_invariant_v1.py`
Anchor: `grounding_consolidation_loop_degree_invariant_v1`
Author: exp_dev (hdi_exp_dev)
Rematch of: `grounding_additive_geometric_degree_control_v1` (HARD_FAIL_GEOMETRY_IS_POPULARITY_SHORTCUT, 2026-07-10)

## Question (one decisive thing)

Does a SLOW ITERATIVE CONSOLIDATION PROCESS that rearranges concept codes to honor CROSS-CHANNEL AGREEMENT produce a
geometry that is degree-INVARIANT on held-out relational inference -- where the one-shot directly-fit additive code we
just tested was degree-DEPENDENT (a popularity shortcut: strata d(transe-discrete) LOW=-0.040 MID=+0.085 HIGH=+0.264,
pop_recover_frac 0.52)? MEASURED@data/exp_grounding_additive_geometric_degree_control_v1/metrics.json:gates.strata.

## Mechanism under test (a PROCESS, not a code)

CONSOLIDATION LOOP = normalized-Laplacian graph diffusion WITH RESTART (personalized-PageRank / successor-representation
form) over a CROSS-CHANNEL AGREEMENT graph, then a light additive relation-offset read-off. Brain analog: Complementary
Learning Systems (McClelland/O'Reilly) -- hippocampus fast/episodic (raw graph + raw surface form), neocortex slow gist
over sleep replay (the settled degree-invariant coordinate). CITED@McClelland/O'Reilly 1995; Sun et al. Nat.Neurosci.2023.

Two degree-invariance / anti-collapse properties BY CONSTRUCTION (Director-hardened via spectral-diffusion drill):
- NORMALIZED-Laplacian propagation S = D^-1/2 W D^-1/2 -- the decades-proven fix for degree/popularity bias (unnormalized
  L = D - W re-derives the bias). THEORETICAL@graph-signal-processing.
- RESTART (alpha=0.25) to the exterior-informed anchor -> personalized-PageRank/SR stationary state; PREVENTS the
  Oono-Suzuki oversmoothing collapse to the constant eigenvector. Additionally EARLY-STOPPED (6 passes). CITED@Oono-Suzuki.

## The load-bearing constraint: channel independence (guarded by a PRE-FLIGHT GATE)

The two channels MUST be genuinely independent / exterior. If both derive from the same skewed graph, consolidation
re-derives popularity and fails identically (internal loops decorrelate noise, not a SHARED bias).
- Channel S (STRUCTURAL): random-projected propagated visible-graph adjacency (relational content; also the restart anchor).
- Channel L (LEXICAL/ATTRIBUTE): char-trigram surface features of the concept string (EXTERIOR to the graph; degree-blind).

PRE-FLIGHT INDEPENDENCE GATE (runs FIRST, BEFORE the loop -- the cheapest falsifier; prior-art through-line: verify the
premise, don't assume it). Load-bearing measure = EACH channel's correlation WITH NODE DEGREE (kNN in-degree vs graph
degree). If BOTH channels are degree-loaded, agreement = shared degree bias -> BLOCK (do NOT run the loop; report the
numbers). cross_sim_r is REPORTED but only flags near-IDENTICAL channels (the co-training/CLIP subtlety: channels that
must AGREE necessarily share the semantic signal, so high marginal cross-sim is expected -- conditional independence, not
marginal, is the premise). REAL-DATA PROBE (n=733): cross_sim_r=-0.000, struct_deg_r=0.005, lex_deg_r=0.204 ->
exterior_decorrelated=True, both_degree_loaded=False, redundant=False -> PASSES. MEASURED@/tmp probe 2026-07-10 (small
subgraph; the FULL re-measures at n=5000 and gates on it).

## Arms (PAIRED; identical harness to the retest -> clean rematch)

- DISCRETE_HRR_BIND -- one-shot substrate multiplicative binding code (baseline).
- ONESHOT_TRANSE -- the JUST-FAILED one-shot additive code (degree-dependent; reproduces the retest failure mode).
- CONSOLIDATED -- MECHANISM: agreement(struct,lex) -> normalized-Laplacian diffusion-with-restart(struct anchor) -> fit
  additive relation offsets (entities FROZEN) -> score -||E_cons[h]+R_r-E_cons[t]||_1.
- CONSOLIDATED_TRAP -- shared-bias control: SAME pipeline + anchor, agreement(struct,struct2) (both structural) instead.
  REPORTED corroborator (on the random-projection structural feature the trap may be a weak control -- see limitation).
- POPULARITY_DEGREE -- degree-only popularity baseline (no geometry).
- RANDOM_CODES -- untrained-code null (chance floor + codes-necessary control).
- TRANSE_TRANSDUCTIVE -- oracle / must-fire (trained WITH held-out visible).

## Primary metric

reach@1 = filtered Hits@1 on the COMPLETABLE held-out subset (withheld directed (h,r,t), h,t visible, r visible), plus
MRR + Hits@3/10, and per-degree-stratum reach@1 (LOW/MID/HIGH tertiles of true-tail VISIBLE degree; data-driven quantiles).
DECISION = degree-INVARIANT tail survival + FLATNESS, NOT an aggregate delta (aggregate delta carries the degree confound).

## Pre-registered bands (numeric; BEFORE the run)

GEOM_MARGIN=0.05, STRAT_MARGIN=0.03, TIE_EPS=0.02, FLATNESS_EPS=0.08, HIGH_LOW_GAP_FAIL=0.15, POP_GAP=0.05,
POP_RECOVER_FRAC_MAX=0.60, POP_RECOVER_FRAC_HI=0.80, RANDOM_CEIL=0.15, ORACLE_FIRE_MARGIN=0.15, MIN_STRAT_Q=40,
INDEP_R_MAX=0.30 (degree), REDUNDANT_CROSS=0.95, COLLAPSE_RANK_FLOOR=3.0, COLLAPSE_VAR_FLOOR=0.02, HELDOUT_FRAC=0.30,
N_RANK_NEG=99, MIN_HELDOUT_COMPLETABLE=60.

### HARD_PASS_CONSOLIDATION_DEGREE_INVARIANT (ALL must hold)
- channels_independent (PRE-FLIGHT gate PASSES: exterior degree-decorrelated, not both-degree-loaded, not redundant), AND
- NOT collapsed (cons effective_rank > 3.0 AND rep_variance > 0.02), AND
- aggregate materiality: CONSOLIDATED reach@1 >= DISCRETE + 0.05, AND
- tail survival: (CONSOLIDATED - DISCRETE) reach@1 >= 0.03 in BOTH LOW and MID strata (>=40 queries each), AND
- FLATNESS (the genuinely-new degree-invariance bar): |cons_HIGH - cons_LOW| <= 0.08, AND
- popularity does NOT recover: (cons - pop) >= 0.05 AND pop/cons <= 0.60.

### HARD_FAIL_CHANNELS_NOT_INDEPENDENT
- PRE-FLIGHT gate FLAGS the channels (both-degree-loaded OR redundant) OR any seed BLOCKED -> comparison void; the only
  available exterior channel is not independent enough -> redirect to INGEST (report the correlation numbers).

### HARD_FAIL_CONSOLIDATION_COLLAPSED
- cons effective_rank <= 3.0 OR rep_variance <= 0.02 (oversmoothing collapse to ~constant mode).

### HARD_FAIL_CONSOLIDATION_ANOTHER_SHORTCUT (channels independent, not collapsed, but still shortcuts)
- tail collapse ((cons - discrete) <= 0.02 in LOW or MID) OR concentration (|cons_HIGH - cons_LOW| >= 0.15, matching
  TransE's ~0.26 head-tail gap) OR popularity recovers ((cons - pop) <= 0.02 OR pop/cons >= 0.80).

### MIDDLE_BAND_PARTIAL_DEGREE_AMBIGUOUS
- otherwise (beats popularity in aggregate but flatness/tail ambiguous).

Precondition INCONCLUSIVE gates: enough completable (>=60), negatives_valid (random <= 0.15), oracle_fires (>= random+0.15).

## Self-test (mechanism discriminators; SELFTEST_PASS 2026-07-10, 15.9s CPU) -- contract (a)/(b)/(c)/(d)

- (a) PLANTED INDEPENDENT AGREEMENT (clustered world, independent-noise channels): CONSOLIDATED recovers >=5x chance
  (0.148), degree-FLAT (|low-high|=0.022 <= 0.12), beats popularity (0.148 vs 0.008). MEASURED@self-test.
- (b) PLANTED PURE POPULARITY (zipf tails, noise channels): consolidation does NOT beat popularity (0.095 vs 0.228),
  popularity baseline FIRES (0.228). MEASURED@self-test.
- (c) PRE-FLIGHT GATE LOGIC: degree-loaded+degree-blind -> PASS (struct_r=0.53, lex_r=-0.02); identical -> redundant
  FLAGGED (cross_r=1.0); both-degree-loaded -> FLAGGED (r=0.53/0.49). MEASURED@self-test.
- (d) COLLAPSE DISCRIMINATOR: collapsed code (rep_var=0.0) CAUGHT by the floor; healthy consolidated code (rep_var=0.289)
  PASSES. MEASURED@self-test.
- Saturation-vacuous guard: the must-fail controls ((b) cons-not-beat-pop; (c) correlated/both-loaded flagged) FAIL at
  self-test scale by construction.

## SCHEMA-VET fields

- cell_chunked: false (n_seeds axis, single cell; seeds looped with write_partial per seed)
- start_marker_written: true; crash_diagnostic_present: true; heartbeat_present: false (per-seed/per-pass flush prints);
  defensive_error_checking: passed_all_4_patterns (start-marker + crash-diag + per-arm/per-seed failure-class + no bare except)
- final_metrics_atomicity: tmp_replace (write_metrics + os.replace; write_partial per seed)
- arms_differ_verified: true (>=5 distinct arm sigs asserted per seed)
- crlb: filtered Hits@1 chance = 1/(N_RANK_NEG+1) ~ 0.01 THEORETICAL; HARD_PASS thresholds on achievable side;
  discriminator_reachability: OK (self-test planted-independent arm demonstrates recovery >> chance).
- baseline_in_band: RANDOM_CODES null (<= 0.15); ORACLE must-fire (>= random+0.15); POPULARITY confound-baseline (measured).
- calibration_check: default_ok_for_this_regime (HELDOUT_FRAC/completable-subset inherited from retest; degree tertiles
  data-driven; KGE + consolidation hyperparams pre-registered here before the run).
- cardinality_ok: EXPECTED_N_UNITS = n_seeds (3 for FULL); verdict HARD_FAIL_CARDINALITY_BREACH_META_RULE_H if short.
- progress_logging: print_flush_true (line-buffered stdout + per-seed/per-arm/per-pass flush prints).
- positive_control (Gate D): TRANSE_TRANSDUCTIVE reproduces the transductive-KGE result (>> random); ONESHOT_TRANSE
  reproduces the retest degree-dependent additive result on the same 30% split.
- effective_vs_nominal / sweep_alignment: ALIGNED (ARM x seed x stratum; no nominal-vs-effective mismatch).
- discriminating_fraction: N/A (not a parameter sweep; ARM-comparison cell).
- composition_edges: agreement-graph -> diffusion-restart -> relation-offset fit -> ranking; SHAPE_MATCH each edge.

## Compute architecture

class (a) batched-GPU. Structural features = 2 dense [n,n]@[n,dim] matmuls (n<=5000 -> ~0.1GB); channel kNN = one [n,n]
cosine + topk; agreement = boolean AND of two topk masks; consolidation = 6 dense [n,n]@[n,dim] diffusion steps;
relation-offset fit = vectorized margin-rank (entities FROZEN); ranking = one shared [nq,K,dim] candidate tensor per arm.
Storage: SHARDED (each entity its own code/offset). Routes to overnight_queue (GPU) for FULL; local = self-test only
(USER-locked SMOKE-ONLY-LOCAL; KGE FULL is GPU-bound, as for the retest). Self-test is the local pre-flight gate.

## Config

- FULL: seeds=[7,13,17], n_nodes=5000, kge_dim=64, kge_epochs=600, CONS_KNN=8, CONS_PASSES=6, CONS_ALPHA=0.25, REL_EPOCHS=400.
- SMOKE: seeds=[7,13], n_nodes=1800 (available if orchestrator wants a reduced preview).
- SELFTEST: planted worlds; SHARED consolidation params (discriminator-survives-scale).

## Honest limitations (reported up front)

1. The random-projection STRUCTURAL channel is NOT itself degree-loaded on real data (struct_deg_r=0.005) -- so the
   CONSOLIDATED_TRAP (struct,struct2) is a WEAK control here (won't strongly re-derive popularity); it is a REPORTED
   corroborator, not a HARD_PASS gate. The independence premise is verified DIRECTLY by the pre-flight instead.
2. The exterior (lexical/char-trigram) channel carries only surface-form (spelling) signal, NOT relational geometry.
   Per the convergent scour + SSP note + prior-art, the MOST LIKELY outcome is HARD_FAIL / MIDDLE_BAND (the available
   exterior channel is insufficient -> the lever is INGEST, not richer same-graph processes). This cell is a decisive,
   pre-registered rematch: a positive would be a real degree-invariant inductive lever; a negative is a 3rd independent
   confirmation redirecting to grounding/ingest. Reported honestly either way.
