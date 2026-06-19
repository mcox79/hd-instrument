# exp_dev routing note: v225_refill -- 4 GPU anchors

**Filed:** 2026-05-27
**Trigger:** v225 state -- GPU queue 0/0 idle; user explicit priorities: Saad-Solla FULL, SKAH-M battery, orthogonal probe.

## Shipment record

```
queue=overnight_queue name=wave14_saddle_cascade_plateau_v6_n4096_gpu script=experiments/exp_wave14_saddle_cascade_plateau_v6_n4096_gpu.py prereg=prereqs/2026-05-27_wave14_saddle_cascade_plateau_v6_n4096_gpu.md timeout=14400
queue=overnight_queue name=anchor_novel_phase_battery_v3_n8192 script=experiments/exp_anchor_novel_phase_battery_v3_n8192.py prereg=prereqs/2026-05-27_anchor_novel_phase_battery_v3_n8192.md timeout=21600
queue=overnight_queue name=anchor_novel_phase_battery_v2_lit_threads script=experiments/exp_anchor_novel_phase_battery_v2_lit_threads.py prereg=prereqs/2026-05-27_anchor_novel_phase_battery_v2_lit_threads.md timeout=7200
queue=overnight_queue name=anchor_novel_class_declaration_probe_v1 script=experiments/exp_anchor_novel_class_declaration_probe_v1.py prereg=prereqs/2026-05-27_anchor_novel_class_declaration_probe_v1.md timeout=7200
```

## Justification per anchor

1. **wave14_saddle_cascade_plateau_v6_n4096_gpu** (CRITICAL, Priority 1):
   v225 cap_map explicitly flags: "genuine large-N FULL run (N>=4096, multi-seed) STILL OPEN".
   v221 was N=512 smoke mislabeled as N=4096. This is the first proper FULL test.
   N=4096, 5 seeds, GPU. Pre-reg bands: per-seed HARD-PASS R^2<0.85 AND max_dev>=0.08;
   OVERALL-PASS >= 4/5 seeds. Smoke PASS (r2=0.782, max_dev=0.085 at N=512).

2. **anchor_novel_phase_battery_v3_n8192** (CRITICAL, Priority 2):
   Battery v1 MIDDLE_BAND (doc=3, finite_N=2) with explicit instruction to "extend to N=8192 + 10 seeds".
   N_SWEEP=[512,1024,2048,4096,8192], 10 seeds, C3-C6 at N=4096. Pre-reg: HARD-PASS >=5/6 DOCUMENTED.
   Smoke PASS (q_EA=0.775, ret_G1=0.752 non-null).

3. **anchor_novel_phase_battery_v2_lit_threads** (HIGH, Priority 3 supplement):
   Pre-built 3-thread discrimination. Shipped in parallel with v3 battery so thread identification
   is ready when v3 returns. Smoke PASS (THREAD_A_PARTIAL; Arm1 r=0.0, Arm2 delta=-0.046).

4. **anchor_novel_class_declaration_probe_v1** (HIGH, Priority 4):
   5-step novel-class characterization methodology (symmetry, q_EA, Goldstone, F-wells, chi).
   Orthogonal to battery (different observables). Smoke PASS DOCUMENTED_CONFIRMED 4/5.
   Serves as "orthogonal probe" slot since Tkacik-Bialek was blocked.

## Tkacik-Bialek INSTRUMENTATION_SUSPECT (blocked)

wave14_ortho_tkacik_bialek_maxent_v1 blocked: s2_ratio constant 0.993-0.996 across all
(K, N, seed) combinations. Proxy formula algebraically constant by construction (expected_coupling
dominates denominator). Routing note at notes/exp_dev_to_strategy_instrumentation_suspect_tkacik_bialek_2026-05-27.md.
Needs log-likelihood or Fisher information reformulation.

## Bridge-verified

4/4 confirmed in remote overnight_queue (wave14_saddle_cascade_plateau_v6_n4096_gpu=running,
anchor_novel_phase_battery_v3_n8192=pending, anchor_novel_phase_battery_v2_lit_threads=pending,
anchor_novel_class_declaration_probe_v1=pending).
