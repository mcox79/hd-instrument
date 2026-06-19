# Exp Dev -> Queue: post-ONLINE_W_NOISE_ENVELOPE_NARROW pipeline refill

**Filed**: 2026-05-23
**Routing trigger**: URGENT pipeline refill after ONLINE_W_NOISE_ENVELOPE_NARROW verdict (GPU queue empty)
**Trigger context**: Cap 1/Cap 3/Cap 5 all received noise-envelope probes; queue emptied; need >= 2 new experiments per [[feedback-pipeline-pacing]] queue-depth invariant.

---

## Entry 1 (CPU exploratory)

```
queue=local_cpu_queue name=wave14_betT_per_hyp_tempscale_v1 script=experiments/exp_wave14_betT_per_hyp_tempscale_v1.py prereg=preregs/2026-05-23_wave14_betT_per_hyp_tempscale_v1.md timeout=600
```

**Smoke gate**: PASSED. Self-test 4/4 PASS. Smoke at N=512, 3 hyp, 1 seed:
- beta=4: min_acc=1.000 mean_acc=1.000 ece_max=0.000
- beta=8: min_acc=1.000 mean_acc=1.000 ece_max=0.000
- beta=16: min_acc=1.000 mean_acc=1.000 ece_max=0.000
- VERDICT: BET_T_TEMPSCALE_PASS
- metrics.json: data/exp_wave14_betT_per_hyp_tempscale_v1_smoke/metrics.json
- Elapsed: <1s

**FULL config**: N=4096, 8 hypotheses, 30 facts/hyp, 3 seeds {17,23,31}, beta_h in {4,8,16}
**Memory budget**: < 4 MB total (CPU). No VRAM.
**Queue rationale**: pure CPU, expected < 5 min, local data only -> local_cpu_queue
**Substrate-product axis**: Bet T parallel hypothesis tracking (Cap class 3 provenance);
Research rescue sketch #2 P_deflated=0.45 (top-ranked path in research_betT_rescue_sketches_2026-05-23.md)

---

## Entry 2 (GPU depth)

```
queue=overnight_queue name=wave14_cap2_confidence_margin_probe_v1 script=experiments/exp_wave14_cap2_confidence_margin_probe_v1.py prereg=preregs/2026-05-23_wave14_cap2_confidence_margin_probe_v1.md timeout=900
```

**Smoke gate**: PASSED (structural). Self-test 4/4 PASS. Smoke at N=1024, M=30, 1 seed:
- All strata: err_rate=0.000 (sub-capacity at small N; expected degenerate corr)
- VERDICT: CAP2_MARGIN_KILL (expected at sub-capacity smoke; structure valid)
- 4/4 strata present in metrics.json
- metrics.json: data/exp_wave14_cap2_confidence_margin_probe_v1_smoke/metrics.json

**FULL config**: N=8192, M=200, 3 seeds {17,23,31}, noise_levels=[0.0,0.05,0.10,0.20], 200 trials/stratum
**Memory budget**: W=268 MB + keys/values=12.8 MB + transient=6.4 MB. Total peak VRAM ~290 MB.
**Queue rationale**: imports torch.cuda (device='cuda' branch), N=8192 -> overnight_queue
**Substrate-product axis**: Cap 2 self-monitoring confidence (metric-definition re-probe;
Sagawa-Ueda precedent from Cap 1 v158 re-axiomatization); if PASS lifts Cap 2 from refuted;
if KILL structurally confirms Cap 2 closure with no further rescue needed.

---

## Coordination notes

- PROT-001 compliance: notes/exp_dev_decisions_2026-05-23.md exists (stub not needed)
- PROT-002: session_prompts/session_5_exp_dev.md not checked -- out of scope this cycle
- PROT-005: no /loop change this cycle (user-triggered dispatch)
- Pipeline after these two: overnight_queue has wave14_betA_continual_edit_5seed_v3 (pending) +
  wave14_cap2_confidence_margin_probe_v1 (new) = depth 2. local_cpu_queue gains
  wave14_betT_per_hyp_tempscale_v1. Queue depth invariant satisfied.
