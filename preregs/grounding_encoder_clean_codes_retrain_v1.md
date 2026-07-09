# Pre-reg: grounding_encoder_clean_codes_retrain_v1 (Stage-2 RETRAIN encoder fix)

Cell: `experiments/exp_grounding_encoder_clean_codes_retrain_v1.py`
Anchor: `grounding_encoder_clean_codes_retrain_v1`
Author: exp_dev. Filed BEFORE FULL dispatch. Bands picked before the FULL run.

## Question
Stage-1 (grounding_encoder_clean_codes_cheap_levers_v1) resolved the fork: NO post-hoc transform of the
FROZEN codes recovers role-recovery -> the codes were never TRAINED with a strong-enough structural signal.
Stage-2 RETRAINS with the levers baked in and ablates WHICH element carries the win: DG-expansion vs the
binding-consistency objective vs both.

## Arms (2x2 ablation minus the reproduced baseline; same discriminator as Stage-1)
- A BASELINE_FROZEN: baseline binding encoder (code_dim=256, baseline objective). Reproduce the MEASURED
  0.28 recall / reach-1 floor (contrast floor; NOT allowed to pass).
- B EXPAND_ONLY: DG-expansion (dg_dim) + differentiable DG k-WTA (STE; magnitude-topk == hdlab
  hippocampal_encoder._sparse_topk_mask), baseline objective.
- C BINDOBJ_ONLY: stronger BIDIRECTIONAL binding-consistency objective at code_dim=256, no expansion:
  forward bind(role_r,z_i)~z_j AND backward unbind(role_r,z_j)~z_i (exact inverse via unitary roles),
  w_bind up (2.0), w_prox down (0.3), + Hoyer L1/L2 sparsity penalty (0.05).
- D FULL_STACK: EXPAND + BINDOBJ.

## Discriminator (identical to Stage-1; machinery imported VERBATIM -> bit-identical recall/reach defs)
Role-apply (unbind) edge_recall + edge_precision on the LEARNED codes, AND effective multi-hop REACH over
the CODE-RECOVERED graph (reach>=2 == typed binding chains past 1 hop on real codes; shuffle+collapse gated).

## Pre-registered bands
- Baseline reproduce contract: BASELINE_FROZEN recall in [0.20, 0.42] AND reach <= 1. Else BASELINE_REPRO_FAIL.
- HARD_PASS: a RETRAIN arm with edge_recall >= RECALL_HP_MIN=0.45 AND precision >= PRECISION_FLOOR=0.10 AND
  eff_reach >= REACH_HP_MIN=2 AND (reach - baseline_reach) >= REACH_DELTA_HP=1.
- MIDDLE_BAND: best retrain recall >= RECALL_MIDDLE_MIN=0.38 OR a recall-preserving retrain arm reach>=2.
- HARD_FAIL_RETRAIN_CANNOT_CLEAN: best retrain recall < baseline + RECALL_HARDFAIL_DELTA=0.05 AND no recall-
  preserving retrain arm extends reach past 1 (deeper encoder-capacity limit).
- Reach-extension credited ONLY to recall-preserving arms (recall >= base_recall - 0.02): a reach win on
  codes WORSE than baseline is reach-probe noise.
- HP_SCOPE: recall+reach gates apply to {EXPAND_ONLY, BINDOBJ_ONLY, FULL_STACK}; BASELINE_FROZEN is the
  reproduce-the-floor control.

### Number provenance
- baseline role-apply edge_recall = 0.2819, reach = 1
  MEASURED@data/exp_grounding_binding_structured_encoder_multihop_v1/metrics.json:gates.recall_mean.BINDING_UNBIND
- baseline role-apply precision = 0.1334 (sets PRECISION_FLOOR)
  MEASURED@data/exp_grounding_binding_structured_encoder_multihop_v1/metrics.json:gates.precision_mean.BINDING_UNBIND
- MLC objective-change lifts role-recovery ~0% -> 99.78% (CITED@notes/research_encoder_clean_composable_relational_codes_2026-07-09.md:S1#2)
- Treves-Rolls sparse capacity ~ 1/(a ln(1/a)) (CITED@same:S1#1)
- RECALL_HP_MIN=0.45 / REACH_HP_MIN=2 HYPOTHESIZED@this prereg (decisive jump above 0.40 cosine arm + 2-hop chaining beating reach=1)

## SCHEMA-VET fields
- cardinality_ok: true. EXPECTED_N_UNITS = n_seeds (3 FULL); all 4 arms asserted present per seed.
- arms_differ_verified: true (4 distinct encoder digests + recovered-edge-set hashes). arms_differ_exempted: none.
- final_metrics_atomicity: tmp_replace (write_metrics + os.replace).
- except SystemExit: raise BEFORE except Exception (grep-clean; no bare except / BaseException).
- crlb_n/a: "reach ordering-acc chance floor = 0.5; discriminator is shuffle+collapse-gated reach + edge_recall vs a reproduced baseline floor."
- discriminator_reachability: true (baseline reproduces 0.28/reach-1; headroom to 0.45/reach-2).
- baseline_in_band: true (BASELINE_FROZEN 0.294/reach-1 at smoke; a floor to beat, not saturated).
- calibration_check: adaptive_with_discriminator_gate (shuffled null per run; collapse gate fires; crosstalk floor sqrt(2 ln n/d)).
- cell_chunked: false (<=3 seeds in-cell; per-seed write_partial). start_marker_written / crash_diagnostic_present / heartbeat_present: true.
- defensive_error_checking: passed_all_4_patterns.
- progress_logging: print_flush_true (line-buffered stdout + per-arm/epoch flush prints + heartbeat).

## §15 composition/sweep gates
- sweep_alignment_verdict: ALIGNED (ablation axis EXPAND x BINDOBJ; each arm's flags are exactly what its encoder trains with).
- discriminating_fraction: n/a-sweep; smoke confirms the discriminator fires (BINDOBJ moves recall +0.075 AND reach +1; EXPAND moves it -0.27).
- composition_edges: features -> ProjHead(->out_dim) -> [STE DG k-WTA] -> L2 code -> {HRR bind / unbind, binding-consistency loss} -> topk-floor adjacency -> reach. SHAPE_MATCH at each edge; unitary roles match each arm's code dim.
- positive_control_arms: BASELINE_FROZEN reproduces the cited baseline atom (reproduce band [0.20,0.42]/reach<=1); lever_selftest reproduces a planted-typed-graph retrain (recall 0.579/prec 0.93).
- functional_requirements: (1) lift role-recovery fidelity via TRAINING [BINDOBJ/EXPAND arms]; (2) preserve/improve precision [precision floor + F1]; (3) chain reach>=2 on real codes [reach machinery]; (4) reproduce the frozen baseline [ARM A]; (5) attribute the win to a specific element [EXPAND_ONLY vs BINDOBJ_ONLY vs FULL_STACK].

## Compute architecture
- class (b) sequential-CPU with justification: reuses the CG'd CPU-only teacher-free encoder (ProjHead / info_nce / vicreg) + hdlab HRR FFT bind/unbind (torch CPU); training has sequential epoch dependency; recovery/reach are numpy-BLAS matmul (multithreaded). 4 encoder trainings/seed. Smoke (2 seeds, dim128/384, epochs45) = 32s; FULL (3 seeds, dim256/1024, epochs120) est ~10-25 min. GPU port would fork the proven baseline machinery.
- storage strategy: SHARDED (each node its own code; recovery per-edge; no bundling).

## SMOKE result (2 seeds, n=1525, code_dim=128/dg_dim=384; MEASURED@data/exp_grounding_encoder_clean_codes_retrain_v1_smoke/metrics.json)
- baseline_reproduces=True: BASELINE_FROZEN recall 0.294, reach 1 (both seeds). Floor reproduced.
- BINDOBJ_ONLY: recall 0.294 -> **0.369** (+0.075), precision 0.175 -> **0.31** (UP => not spurious), reach **2.0 mean (seed7 reach 3)**, reach_delta_vs_base **+1**. The reach HARD_PASS gate is CLEARED at smoke; only the 0.45 recall bar unmet (0.369; expected to climb at FULL's 2x code_dim + 2.7x epochs).
- EXPAND_ONLY: recall **0.023** (DG k-WTA sparsity destroys HRR recovery -- the bound product is dense, the sparse target mismatches). FULL_STACK: 0.082 (dragged down by expansion).
- element_attribution (MEASURED): expand_gain=-0.271, bindobj_gain=+0.075, full_gain=-0.212; bindobj_reach=2.0, expand/full_reach=-1.
- **WHICH ELEMENT: the BINDING-CONSISTENCY OBJECTIVE carries the entire win. DG-expansion HURTS under HRR.**
- Verdict MIDDLE_BAND (near-HARD_PASS: reach gate met, recall gate close). Smoke previews a genuine HARD_PASS candidate at FULL.

## FULL profile
seeds=[7,13,17], n_nodes=5000, epochs=120, code_dim=256, dg_dim=1024, feat_dim=8192, D=[1,2,3,4,5].
Confirms at canonical scale whether BINDOBJ's recall clears 0.45 + reach>=2 holds over 3 seeds (HARD_PASS) or
plateaus (MIDDLE). Both outcomes gold; the element attribution (BINDOBJ carries it, EXPAND hurts) is already clean.
