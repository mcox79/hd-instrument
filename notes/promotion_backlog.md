# Promotion backlog — proven capabilities to WIRE into hdlab (owner: hdi_testbed)

A capability is DONE when WIRED into hdlab + discoverable, NOT when its atom is banked.
Source: integration audit 2026-07-25 (notes/integration_audit_hdlab_wired_vs_islands_2026-07-25.md)
+ detector `python tools/integration_health.py`. Rank = reuse x on-critical-path.
Do NOT promote all 237 candidates -- only VET-confirmed keepers on the critical path or high-reuse.
Exploratory one-offs stay disposable cells (the foundry is fine for exploration).

## CRITICAL PATH (reasoner pivot -- these ARE the reasoner build; P-order from the audit)
- [ ] P1  parse_tablestore_typed (in exp_arc_selection_relational_meaning_v1.py) -> hdlab/typed_rule_parser.py -- typed rule-graph builder the reasoner consumes.
- [ ] P3  M3 meet-in-middle multihop 0.62 (exp_multihop_bidirectional_meet_in_middle_depth_scaling_v3.py) -> hdlab, supersede weaker K=2 hdlab/multi_hop.py -- the derivation-search primitive.
- [ ] P4  CI/polarity consistency (exp_arc_aggregation_polarity_ci_v1.py) -> hdlab consistency stage.
- [ ] P5  CREATE hdlab/reasoner.py composed entry: reader -> typed_rule_parser -> hd_fact_store retrieval -> multihop derivation -> CI consistency -> selection. (== the reasoner build; the composed entry does not exist today.)
- [ ] P2  stable hdlab.arc_pipeline API (SemanticHDEncoder, mr retrieval, agg combiner, selection) -- stop `from experiments import ... as mr`.
- [ ] P6  decide situation_reader role (ARC comprehension front-end vs Frontier-2).
- [ ] P1b NegAwareEncoder + head-lemma merge-gate + polarity merge-gate (in exp_arc_derivation_connectivity_gate_cleannodes_v2.py, atom seq 29552) -> hdlab node-identity for the typed-rule graph. VET-confirmed keeper: sign-flip Hadamard bind gives cos(notX,notY)==cos(X,Y) exact + cos(X,notX)~0 (negation-separating, no spurious neg-hub); head-gate killed the deg-498 mega-hub (498->83); polarity-gate preserved negation (1979->0 contradiction-merges). Prerequisite for ANY derivation reasoning (a negation-collapsed graph has discarded entailment). GATE BEFORE WIRING: fix the `_has_neg_token` negation-DETECTION false-positive -- `tok.endswith("nt")` flags element/point/current/important/nutrient/continent/present/content/event/environment/plant/instrument/experiment as negated (399 neg-flagged likely contaminated). The sign-flip MECHANISM is sound; replace the detection heuristic with a real polarity-cue parser. Trapped in the ablation cell today.

## SHARED HARNESS (infra trapped in exp cells; promote to a shared lib)
- [ ] _seed_checkpoint (imported by 3653 cells!) -> shared harness module.
- [ ] _multi_hop_mechanisms (67), _validity_preflight (97), _cell_heartbeat (50), _metric_battery (50) -> shared harness.

## HOUSEKEEPING
- [ ] Quarantine/doc 7 dead hdlab modules: action_selection, compose_freq_routing, excitability, k_cliff_scaling, lock_in_amp, profiling, self_manager.

## PROCESS (make it self-enforcing)
- [ ] Wire the PROMOTE-VERDICT into the skunkworks VET step: at atomize, emit island-ok vs PROMOTE(target) for VET-confirmed reusable/critical-path capabilities -> append here.

Baseline (integration_health 2026-07-25): 237 promotion candidates, 4133/5327 (78%) bypass cells, 7 dead, composed entry = ABSENT.
