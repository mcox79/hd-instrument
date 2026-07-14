# Pre-registration: RULE-GATED ANCHOR_COMPOSE (rule_gated_compose_inductive_entity_cskg_v1)

**Cell:** `experiments/exp_rule_gated_compose_inductive_entity_cskg_v1.py`
**Filed:** 2026-07-14 (exp_dev). **Arena:** CSKG-12core held-out-ENTITY inductive probe (same arena + metric + split
as the additive map-builder that scored MEASURED 0.12821 MRR).
**Drill source:** `notes/research_drill_composition_operator_rule_theories_2026-07-13.md` HEADLINE #2 (rules as a GATE
on a stronger base method, not a standalone predictor). **Predecessors:**
`exp_rule_induction_heldout_entity_cskg_v1` (rule-induction VET: mined Horn rules are HIGH-PRECISION / LOW-COVERAGE,
tie POP standalone) + `exp_anchor_compose_inductive_entity_cskg_v1` (the additive ANCHOR_COMPOSE, 0.128 line).

## Question
Does using high-precision mined length<=2 Horn rules as a symbolic GATE on which 2-hop terms enter the additive
held-out-entity bundle BEAT the pure additive ANCHOR_COMPOSE (0.128), especially on the degree-STARVED d1/d2_3
support-degree buckets (where the 1-hop bundle is noisiest and has the most oracle headroom), WITHOUT regressing the
well-served d8plus bucket via crosstalk? Must-fail: a SHUFFLED rule gate (body-pattern -> confidence mapping
deranged) must NOT capture the lift.

## Mechanism (single-knob over ANCHOR_COMPOSE; all geometry arms share the SAME frozen additive fit Xa/Da)
1-hop base = ANCHOR_COMPOSE: E_base[t] = mean_i(X[h_i]+D[r_i]) over t's support edges. Rule-gated 2-hop: for each
support edge (h_i,r_i,t) and each TRAIN edge (h2 -r1-> h_i) into the anchor, admit the additive estimate
X[h2]+D[r1]+D[r_i] IFF body pattern (r1,r_i) has a mined L2 rule with PCA-confidence >= GATE_CONF; weight it by that
confidence (soft glass-box gated boost). Rules mined ONCE (AnyBURL/RuleN path-counting, ZERO training, pure graph
statistics) on the SAME train graph. Fully inspectable (admitted rules + confidences + per-bucket admit counts logged).

## Arms (7; all scored PAIRED on the SAME held-out QUERY edges + candidate set + filtered eval)
- `RULE_GATED`  : mechanism (1-hop + confidence-gated confidence-weighted 2-hop). HP_SCOPE: lift gates apply here only.
- `ANCHOR`      : pure additive 1-hop (= ANCHOR_COMPOSE 0.128 line); the beat-target + Gate-D reproduce-at-regime.
- `SHUFFLED`    : must-fail. Same construction, body-pattern->confidence mapping DERANGED over the full candidate
  universe (structured + noise patterns). Must NOT capture the lift.
- `ALL_2HOP`    : ablation (1-hop + ALL capped 2-hop, no gate). Tests gate selectivity vs blind inclusion.
- `RANDOM`      : null. `ORACLE` : positive control (additive fit, held-out folded in). `BASELINE_POP` : freq incumbent.

## Primary metric
Filtered MRR rank-vs-ALL-N (degree-unbiased, KGE standard; same as the additive cell). Degree-stratified by SUPPORT
degree (cold/d1/d2_3/d4_7/d8plus + low_support<=3) for weak-point localization on the drill's d1/d2_3 target.

## Pre-registered bands (BOTH; primary = filtered MRR; H = MEASURED oracle headroom, resolved in-run)
- ORACLE-FIRES (arena answerable): ORACLE_mrr >= 3x RANDOM_mrr AND ORACLE_mrr - RANDOM_mrr >= 0.003.
- **HARD-PASS** (rule-gating lifts additive, SELECTIVELY, on the degree-starved population, no crosstalk):
  gate fired (n_2hop_admitted_gated>0) AND ORACLE fires AND enough held-out AND not broken AND
  overall lift (RULE_GATED-ANCHOR)_mrr >= LIFT_ABS=0.002 AND
  selectivity (RULE_GATED-SHUFFLED)_mrr >= SHUF_MARGIN=0.0015 (shuffled does NOT capture) AND
  degree-starved lift on low_support(<=3) OR d1 OR d2_3 >= DEG_LIFT_ABS=0.004 AND
  RULE_GATED[d8plus]_mrr >= CROSSTALK_FLOOR=0.98 * ANCHOR[d8plus]_mrr.
- **HARD-FAIL** (clean negative): (RULE_GATED-ANCHOR)_mrr <= FAIL_ABS=0.0005 with ORACLE firing (includes the
  gate-admitted-nothing degenerate: CSKG's taxonomy-flat relation vocab too flat for rule-composition to add
  trustworthy 2-hop signal over the pure additive map).
- **MIDDLE**: oracle fires, enough held-out, lift present but not SELECTIVE (shuffled captures it), or not localized
  to the degree-starved population, or crosstalk-degraded.
- Gated INCONCLUSIVE: ORACLE not firing, too few held-out, or a control beats the mechanism degenerately (BROKEN).

## Reference lines (tagged)
- ANCHOR_COMPOSE mrr = 0.12821  CITED@data/exp_anchor_compose_inductive_entity_cskg_v1/metrics.json:gates.heldout_mrr.ANCHOR_COMPOSE
- ORACLE_ADDITIVE mrr = 0.13729  CITED@same (H = 0.13681, 284x). RANDOM_CODES mrr = 0.000483  CITED@same.
- d1 anchor_mrr = 0.0593, d2_3 = 0.0789, d8plus = 0.1277  CITED@notes/research_drill_composition_operator_rule_theories_2026-07-13.md
  (scaling_ladder_v3). The degree-starved buckets sit FAR below oracle -> lift headroom is real there.

## Compute architecture
class (c) MIXED. Additive + oracle fits = minibatch SGD (matmul-heavy, GPU-batching candidate per
feedback_gpu_batching_mandatory -> device=auto; cuda on the GPU host, remote_cpu forces cpu); k=24 epochs=500 =
the SAME fidelity as the MEASURED 0.128 ANCHOR line (direct comparability). Rule-mining + 2-hop enumeration + gating
= sequential-CPU graph stats (zero training, rides along cheaply). Storage SHARDED. Multi-seed [7,13,17] IN-PROCESS
with per-seed partials + empty_cache + fit checkpoints (outage-resumable) + cardinality gate. Routed to
**overnight_queue (GPU)**.

## SCHEMA-VET fields
- sweep_alignment_verdict: N/A (no parameter sweep axis; fixed GATE_CONF/caps).
- discriminating_fraction: N/A (contrast cell, not a bracket sweep); discriminator = the lift + selectivity margins,
  demonstrated to fire on the planted selective-2-hop arena (self-test MEASURED lift +0.0136, gate_vs_shuffle +0.0162).
- composition_edges: rule-gate -> additive bundle SHAPE_MATCH (both operate on the same per-entity code table; the
  gate only decides which additive terms enter the mean).
- positive_control_arms: ORACLE (reproduce-at-regime, must fire >=3x); ANCHOR (Gate-D: reproduces ANCHOR_COMPOSE
  ~0.128 by construction, identical builder + same fit).
- functional_requirements: (1) select trustworthy 2-hop relational compositions -> mined L2 PCA-confidence gate;
  (2) denoise a degree-starved held-out bundle -> additive index_add bundle mean.
- real_code_path_exercised: [fit_kge_anchor1, mine_rules, build_anchor_compose_codes, build_gated_compose_codes,
  additive_direct_scores, build_heldout_entity_split_ac] (self-test constructs/calls all at N~420, no synthetic branch).
- substrate_signature_checked: [fit_kge_anchor1, additive_direct_scores] (bound against live signature; base kwargs).
- guard_baseline_validated: [BROKEN_CONTROL_BEATS_MECHANISM] (protected baseline = ANCHOR, validated above RANDOM
  floor, NOT POP; F.4).
- cardinality: EXPECTED_N_UNITS = 3 seeds; FULL arms_differ requires >=4 distinct sigs (RULE_GATED legitimately
  collapsing onto ANCHOR when the gate admits nothing is a NULL verdict GATE_ADMITTED_NOTHING, not a breach).
- final_metrics_atomicity: tmp_replace. progress_logging: print_flush_true. crash_diagnostic + start_marker + heartbeat present.
- calibration_check: adaptive_with_discriminator_gate (GATE_CONF/MIN_SUPPORT/MIN_CONF/caps/split fracs pre-registered,
  NOT tuned on real data; lift bands = absolute MRR margins calibrated to MEASURED oracle/degree-bucket headroom).

## Discriminator-survives-scale (analytical, B)
A shuffled/wrong 2-hop term pulls E_gated off the true tail position -- a STRUCTURAL property independent of N -> the
real-vs-shuffled selectivity margin does not wash at scale. ORACLE (reused parent additive fit) fired at 284x on the
FULL arena (MEASURED) -> the metric can move at scale. The lift itself may HARD_FAIL on real CSKG (flat vocab) -- the
honest pre-registered negative branch.

## Self-test verdict (local, VALIDITY_PREFLIGHT_MODE=enforce)
SELFTEST_PASS. Planted selective-2-hop arena (N=810): RULE_GATED=0.2359 > ANCHOR=0.2223 (lift +0.0136) >
SHUFFLED=0.2197 (selective +0.0162) > ALL_2HOP=0.1904 (blind inclusion HURTS = crosstalk, the drill's warning) >
RANDOM=0.0076 > POP=0.0036; ORACLE=0.6675 fires 87.7x; 7 distinct sigs; 8 validity-preflight checks declared+passing.
