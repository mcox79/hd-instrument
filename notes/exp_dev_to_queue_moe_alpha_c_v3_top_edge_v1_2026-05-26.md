# exp_dev to queue: MoE alpha_c dense-grid v3 + top-edge ratio v1 -- overnight_queue

**Filed:** 2026-05-26 by exp_dev sub-agent  
**Status:** READY FOR SSH SHIP -- main thread must run queue_add.sh (sub-agent SSH blocked)  
**Handoffs:** notes/exp_dev_handoff_research_moe_alpha_c_dense_grid_2026-05-26.md  
            notes/exp_dev_handoff_free_additive_top_edge_moe_2026-05-26.md

---

## PRE-FLIGHT VERIFICATION (alpha_c v3): PASS

- Fetched remote `data/exp_wave14_moe_alpha_c_prestep_v2/metrics.json`
- `summary.mean_cosines["1600"]` = 0.8482 -- in [0.83, 0.87] -- PASS
- Closed-form prediction: 0.8481. Residual: 0.0001. Grid-quantization root cause CONFIRMED.
- v3 proceed authorized.

---

## SMOKE RESULTS

**wave14_moe_alpha_c_prestep_v3:** Multi-scale smoke PASS.
- N=512: alpha_c=0.5625, max_residual=0.0029 -- HARD-PASS band [0.50, 0.60]
- N=2048: alpha_c=0.5000, max_residual=0.0006 -- HARD-PASS band [0.50, 0.60]
- 7/7 self-tests pass (includes new self-test 7: dense-grid band coverage, 5 pts at spacing 0.0625)

**wave14_moe_top_edge_v1:** Smoke PASS (valid metrics, distinct ratios, non-zero).
- Smoke verdict: FREE_ADDITIVE_MIDDLE (expected -- N=512 is finite-N regime, not asymptotic)
- Decisive test is N=4096 (N/K=2048 for K=2); finite-N corrections expected at smoke scale.
- 4/4 self-tests pass.

---

## ACTION REQUIRED (main thread)

SSH and SCP are blocked in sub-agent context per [[feedback-subagent-permission-inheritance]].
The orchestrator main thread must run these commands:

```bash
bash tools/orchestrator/queue_add.sh overnight_queue wave14_moe_alpha_c_prestep_v3 experiments/exp_wave14_moe_alpha_c_prestep_v3.py prereqs/2026-05-26_wave14_moe_alpha_c_prestep_v3.md 3600

bash tools/orchestrator/queue_add.sh overnight_queue wave14_moe_top_edge_v1 experiments/exp_wave14_moe_top_edge_v1.py prereqs/2026-05-26_wave14_moe_top_edge_v1.md 7200
```

Then verify both:
```bash
ssh marsh@home "C:/Users/marsh/AppData/Local/Python/bin/python3.exe -c \"import json; q=json.load(open('C:/dev/hd-instrument/data/overnight_queue/queue.json')); names=[e['name'] for e in q.get('experiments',[])]; [print(n, 'VERIFIED' if n in names else 'MISSING') for n in ['wave14_moe_alpha_c_prestep_v3','wave14_moe_top_edge_v1']]\""
```

---

## Schema A queue entries

```
queue=overnight_queue name=wave14_moe_alpha_c_prestep_v3 script=experiments/exp_wave14_moe_alpha_c_prestep_v3.py prereg=prereqs/2026-05-26_wave14_moe_alpha_c_prestep_v3.md timeout=3600
queue=overnight_queue name=wave14_moe_top_edge_v1 script=experiments/exp_wave14_moe_top_edge_v1.py prereg=prereqs/2026-05-26_wave14_moe_top_edge_v1.md timeout=7200
```

---

## What was built

### exp_wave14_moe_alpha_c_prestep_v3.py
Dense M-grid version of the alpha_c prestep calibration:
- M_GRID_FULL = [1024, 1536, 1792, 2048, 2304, 2560, 2816, 3072, 3584]
- alpha values = [0.25, 0.375, 0.4375, 0.50, 0.5625, 0.625, 0.6875, 0.75, 0.875]
- Alpha-spacing within band [0.40, 0.70] = 0.0625 (requirement <= 0.10 -- MET)
- Expected verdict: ALPHA_C_HARD_PASS with alpha_c=0.5625 (theory prediction)
- ETA: ~20-40 GPU-min for 5 seeds x 9 M-values x N=4096

### exp_wave14_moe_top_edge_v1.py
Standalone free-additive-convolution top-edge ratio analysis:
- Builds SHIFT + PARTITION W_k tensors (same construction as v2 arms)
- Computes sigma_top_shift / (K * sigma_top_partition_mean)
- Compares to free-additive-conv prediction K*(1+sqrt(c))^2 / (K*(1+sqrt(Kc))^2)
- K_sweep = {1, 2, 4, 8}; M_mults = {1.0, 2.0}; 5 seeds; N=4096
- Zero dependency on MoE v2 -- standalone and runs in parallel
- ETA: ~1-2 GPU-hr

---

## Priority note

alpha_c v3: LOW priority (precision measurement; MoE rebuild is not gated on this).  
top_edge_v1: MEDIUM priority (additive spectral discriminator for MoE SHIFT/PARTITION).  
Both can run after current overnight_queue pending experiments clear.
