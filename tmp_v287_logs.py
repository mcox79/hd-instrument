import sys
sys.path.insert(0, '.')
from tools.orchestrator.append_decision_log import append_entry

STRAT = 'notes/strategy_decisions_2026-05-30.md'
strat_entry = (
    "\n"
    "v286->v287 BATCHED 5-VERDICT P+Q batch MAJOR EVENT (commit ee0d4f8+392242b): multi-hop parallel-mechanism row sub-capacity caveat RESOLVED at production-scale M=8192 AND production-scale K_paths=1000. "
    "5 verdicts: P1 multi_hop_higher_m_stress_v1_n4096 MH_M_STRESS_HARD_PASS all 3 paths sustain at M=2048/4096/8192 depths 3-5 (Path D unanimous 1.000; Path B 8/9 cells 1.000 + B_8192_5=0.968; Path E 6/9 cells 1.000 weakest E_8192_3=0.864 with non-monotonic depth-recovery to 0.971 at d=5) + "
    "Q3 large_k_path_scaling_v1_n4096 LKPS_HARD_PASS all 3 paths sustain at K_paths {10..1000} all cells 1.000 unanimous (lat ratios B/D=12.49x linear E=9.27x sub-linear; Bayesian combinatorial concern REFUTED) + "
    "Q2 mechanism_composition_v1_n4096 MCOMP_MIDDLE_BAND ceiling effect at d=5 all individuals at 1.000 cA/cB/cC cannot differentiate (hp_winning=0/5 hp_inconc_ok=5/5 hf_depths_failing=0/3 honest as worded) + "
    "P2 gpu_large_n_rescue_serialized_v1_n8192 RESCUE_MIDDLE_BAND with 3 sub-verdicts (sub1 GPU N=8192 baseline mean_speedup=22.68x 3-seed HARD_PASS HONEST extends v284 N=4096 result + sub2 sparse_w_gpu_integration M=128 sub-capacity sparse_retention=1.0 hp=0/3 MIDDLE_BAND HONEST + "
    "sub3 chunked_codebook N=16384 LABEL-VS-HONEST #147 NEW SUB-FLAVOR SEED_AGGREGATION_OVER_DEGENERATE_FAILURE: only 1/3 seeds reaches max_M=4096; 2/3 seeds return -1.0 sentinel; mean_max=4096 over-claims by mean-of-1-not-3; true 3-seed mean (4096+0+0)/3=1365; net HARD_FAIL assessment correct) + "
    "Q1 adaptive_threshold_rescue_v3_n4096 ATR3_HARD_FAIL FOURTH-OCCURRENCE INSTRUMENTATION PATHOLOGY (8/9 cells saturate at lowest tau in extended sweep; 1/9 cells interior optimum at edge-regime M_frac=1.0 beta=32.0; BUT meta-finding INFORMATIVE: substrate too clean for adaptive-threshold question to be empirically meaningful in standard regime; STOP-instrumentation-rescue-cycle directive applied per user prompt). "
    "Step 0: 1 LABEL-VS-HONEST catch #147; 4 labels HONEST as worded. "
    "Cap_map decisions: 2 ROW LIFTs + 5 ANNOTATIONS + 1 RESCUE-PENDING (sub3 codebook chunking v7) + 0 ROW CLOSURES + 0 NEW ROWS. "
    "LIFT 1: Multi-hop parallel-mechanism row B/D/E 0.55-0.70 -> 0.75-0.85 (+20% lower; +15% upper; mid 0.80) RATIONALE TWO INDEPENDENT envelope-axis confirmations (P1 M-axis + Q3 K-axis) + triple-mechanism corroboration + Path D unanimous through M=8192 K=1000 + per [[feedback-lit-scan-calibration-penalty]] cap 0.50 LIFTed by multi-axis evidence + CONSERVATIVE not AGGRESSIVE per [[feedback-no-padding-experiments]] (compositional generalization untested Q2 ceiling-bound; cross-mechanism composition deferred; higher-noise untested); DOES NOT reopen QE-2 sequential-argmax closure (different mechanism class). "
    "LIFT 2: Substrate-GPU operational baseline 0.65-0.80 -> 0.75-0.85 (+10% lower; +5% upper) RATIONALE P2 sub1 N=8192 dual-N coverage with v284 N=4096 satisfies single-N-caveat; CONSERVATIVE because only 2 N values tested + N=16384 untested separately from sub3 codebook-chunking question. "
    "5 ANNOTATIONS: Path E engineering-distinct (non-monotonic depth-recovery + sub-linear K-scaling); adaptive_threshold characterization CLOSED at standard regimes (NOT framework component degradation NOT row demotion per [[feedback-dont-overextend-theorems]] substrate-property characterization positive: substrate cleaner than question requires; future adaptive-threshold work routes to edge-regime probes only at beta>=32 M_frac near M_c); mechanism_composition ceiling effect (composition test clean as feasibility; value-add untested at saturated regime); chunked_codebook sub3 HARD_FAIL rescue routing for v7; #147 LABEL-VS-HONEST SEED_AGGREGATION_OVER_DEGENERATE_FAILURE policy lock for future seed-aggregation reporting. "
    "Framework-reliability bands ALL UNCHANGED (non-eq 73-83% SKAH-M 60-75% TCFT 92-97% deletion-cert 92-98% KF-1 65-78% specific 70-83% general 73-83% product-feature 89-98% substrate-outside-static-Hopfield 64-75%); 2 capability-row LIFTs (multi-hop 0.55-0.70 -> 0.75-0.85; GPU 0.65-0.80 -> 0.75-0.85). Portfolio 14+36 UNCHANGED. HONEST 231 -> 236 +5. LABEL-VS-HONEST 146 -> 147 +1 (#147 SEED_AGGREGATION_OVER_DEGENERATE_FAILURE). "
    "4 rescue sets cheapest-first 12 rescues R1 0-compute APPLIED inline. 4 status_log entries (1 CRITICAL multi-hop production-scale durability + 1 HIGH GPU substrate dual-N confirmation + 1 HIGH adaptive-threshold instrumentation-rescue-cycle STOPPED + 1 MEDIUM composition ceiling-effect). "
    "Queue-refill: NO exp_dev refill per user prompt explicit (orchestrator dispatching 5 new experiments in parallel). PROT-007 backlog v277+v278 history rows STILL MISSING carried forward. 198th PROT-009 paired commit. "
    "Top-3 follow-on: (1) cross-mechanism composition probe at HARDER regime M=16384 + depths 5-10 + noise STRATEGICALLY HIGH-PRIORITY composition-class classification SCORE/HANDOFF/PIPELINE; (2) substrate-GPU N=16384 non-chunked probe MEDIUM-PRIORITY extends GPU row to 3-N axis would support further LIFT toward 0.80-0.88; (3) adaptive-threshold edge-regime probe at beta>=32 M_frac near M_c MEDIUM-PRIORITY only scientifically meaningful adaptive-threshold question remaining post-characterization-closure."
)
append_entry(STRAT, strat_entry)

VIS = 'notes/visibility_decisions_2026-05-30.md'
vis_entry = (
    "| v287 | 2026-05-30 | BATCHED 5-VERDICT P+Q batch MAJOR EVENT (commit ee0d4f8+392242b): multi-hop parallel-mechanism row sub-capacity caveat RESOLVED at production-scale M=8192 + K_paths=1000; "
    "P1 MH_M_STRESS_HARD_PASS all 3 paths sustain at M=2048/4096/8192 depths 3-5 (Path D unanimous; Path B near-unanimous; Path E engineering-distinct with non-monotonic depth-recovery 0.864 -> 0.971); "
    "Q3 LKPS_HARD_PASS all 3 paths at K={10..1000} 1.000 unanimous lat B/D=12.49x linear E=9.27x sub-linear Bayesian combinatorial concern REFUTED; "
    "Q2 MCOMP_MIDDLE_BAND ceiling effect at d=5 individuals at 1.0 cA/cB/cC cannot differentiate honest; "
    "P2 sub1=GPU N=8192 baseline HARD_PASS mean_speedup=22.68x sub2=sparse_w_gpu_integration MIDDLE_BAND sub-capacity M=128 sub3=chunked_codebook HARD_FAIL #147 LABEL-VS-HONEST NEW SUB-FLAVOR SEED_AGGREGATION_OVER_DEGENERATE_FAILURE 1/3 seeds operational mean_max=4096 over-claims by mean-of-1-not-3; "
    "Q1 ATR3_HARD_FAIL FOURTH-OCCURRENCE INSTRUMENTATION PATHOLOGY reframed as substrate-characterization POSITIVE (substrate too clean for question in standard regime; STOP-instrumentation-rescue-cycle directive applied) | "
    "**LIFT 1 multi-hop parallel-mechanism B/D/E**: 0.55-0.70 -> 0.75-0.85 (+20% lower; +15% upper; mid 0.80) two independent envelope-axis confirmations + triple-mechanism corroboration + Path D unanimous CONSERVATIVE not AGGRESSIVE per [[feedback-no-padding-experiments]] (compositional generalization untested); does NOT reopen QE-2 sequential-argmax closure. "
    "**LIFT 2 substrate-GPU operational baseline**: 0.65-0.80 -> 0.75-0.85 dual-N coverage N=4096+N=8192 satisfies single-N-caveat. "
    "**ANNOTATION Path E engineering-distinct**: non-monotonic depth-recovery + sub-linear K-scaling. "
    "**ANNOTATION adaptive-threshold characterization CLOSED at standard regimes**: substrate-property characterization positive NOT framework degradation NOT row demotion per [[feedback-dont-overextend-theorems]]; future work routes to edge-regime beta>=32 M_frac near M_c only. "
    "**ANNOTATION composition ceiling effect**: feasibility clean value-add untested at saturated regime; re-test at harder regime required. "
    "**ANNOTATION chunked_codebook sub3 HARD_FAIL**: rescue routing for v7. "
    "Portfolio 14+36 UNCHANGED. HONEST 231 -> 236 +5. LABEL-VS-HONEST 146 -> 147 +1 (#147 SEED_AGGREGATION_OVER_DEGENERATE_FAILURE). Framework-reliability ALL bands UNCHANGED. "
    "4 rescue sets cheapest-first 12 rescues R1 0-compute APPLIED inline. 4 status_log entries (1 CRITICAL multi-hop production-scale durability + 1 HIGH GPU substrate dual-N confirmation + 1 HIGH adaptive-threshold instrumentation-rescue-cycle STOPPED + 1 MEDIUM composition ceiling-effect). "
    "Queue-refill: NO exp_dev refill per user prompt (orchestrator dispatching 5 new experiments in parallel). 198th PROT-009 paired commit. "
    "Top-3 follow-on: cross-mechanism composition at harder regime (HIGH) + substrate-GPU N=16384 non-chunked (MEDIUM) + adaptive-threshold edge-regime probe (MEDIUM). |"
)
append_entry(VIS, vis_entry)

HIST = 'notes/substrate_capability_map_history.md'
hist_entry = (
    "| v287 | 2026-05-30 | BATCHED 5-VERDICT P+Q batch MAJOR EVENT (commit ee0d4f8+392242b): multi-hop parallel-mechanism row sub-capacity caveat RESOLVED at production-scale M=8192 + K_paths=1000. "
    "P1 MH_M_STRESS_HARD_PASS all 3 paths sustain M=2048/4096/8192 depths 3-5 (D unanimous; B near; E engineering-distinct non-monotonic depth-recovery + sub-linear K) + Q3 LKPS_HARD_PASS K={10..1000} all 1.000 + Q2 MCOMP_MIDDLE_BAND ceiling-bound + P2 RESCUE_MIDDLE_BAND (sub1 GPU N=8192 HARD_PASS + sub2 sparse-W-GPU M=128 sub-capacity MIDDLE_BAND + sub3 chunked_codebook HARD_FAIL #147 LABEL-VS-HONEST SEED_AGGREGATION_OVER_DEGENERATE_FAILURE 1/3 seeds operational mean-of-1-not-3) + Q1 ATR3_HARD_FAIL 4TH-OCCURRENCE INSTRUMENTATION PATHOLOGY reframed as substrate-characterization POSITIVE STOP-instrumentation-rescue-cycle | "
    "LIFT multi-hop B/D/E 0.55-0.70 -> 0.75-0.85 (+20%/+15%); LIFT substrate-GPU baseline 0.65-0.80 -> 0.75-0.85 (+10%/+5%); ANNOTATION Path E engineering-distinct (non-monotonic depth-recovery + sub-linear K); ANNOTATION adaptive-threshold characterization CLOSED at standard regimes (not framework degradation; substrate too clean); ANNOTATION mechanism_composition ceiling effect; ANNOTATION chunked_codebook v7 rescue routing; portfolio 14+36 UNCHANGED; HONEST 231 -> 236 +5; LABEL-VS-HONEST 146 -> 147 +1 (#147); framework-reliability bands ALL UNCHANGED; 198th PROT-009 commit |"
)
append_entry(HIST, hist_entry)

print('appended strat + vis + hist via append_decision_log')
