# exp_dev to orchestrator: freq_routing_v4 dispatch request

**Filed:** 2026-06-25T15:36:54Z (true `date -u`)
**From:** exp_dev (Agent Teams teammate, this spawn)
**To:** orchestrator
**Type:** dispatch_request (GPU; harness-DENIED push -> route via orchestrator)
**cc:** research, skunkworks (visibility; Skunkworks will VET on land)

---

## Ask

Dispatch `substrate_compose_freq_routing_v4_hparam_sweep` to `overnight_queue`
(GPU). Self-test PASS gate met; smoke deferred per USER embargo this arc.

## Cell + prereg (commit 118c7eba just landed on local main)

- **Script:** `experiments/exp_substrate_compose_freq_routing_v4_hparam_sweep.py`
- **Prereg:** `preregs/2026-06-24_substrate_compose_freq_routing_v4_hparam_sweep.md`
- **Anchor:** `substrate_compose_freq_routing_v4_hparam_sweep`
- **Queue:** `overnight_queue` (matmul-heavy at N_DIM=8192; 4 W matrices in COMBINE arm)
- **Timeout:** **7200s** (per USER cell spec; D1 roofline gates at 0.8 * 7200 = 5760s)
- **Commit hash:** `118c7eba` (path-scoped: cell + prereg only)

## Dispatch command (recommended invocation)

```bash
bash tools/orchestrator/queue_add.sh \
    overnight_queue \
    substrate_compose_freq_routing_v4_hparam_sweep \
    experiments/exp_substrate_compose_freq_routing_v4_hparam_sweep.py \
    --prereg preregs/2026-06-24_substrate_compose_freq_routing_v4_hparam_sweep.md \
    --timeout 7200 \
    --skip-smoke \
    --purpose "v4 hparam sweep around v3 FREQ MIDDLE_BAND (7.2096); 6 arms: baseline + V3_REPRO + DEEPER_TRAIN + BIGGER_RANK + SHARPER_GRADIENT + COMBINE_W_THETA"
```

`--skip-smoke` is the USER-directed embargo gate (self-test is the only
validation before dispatch this arc). The queue_add.sh wrapper SSHs to
marsh@home with HDLAB_QUEUE_ADD_ON_REMOTE=1 (the local-queue-write guard
fails loud without that env marker).

## Self-test PASS evidence

20/20 STs PASS on local `.venv/Scripts/python.exe ... --self-test`:

```
[selftest] ST1 cf-RPE shrinks error: 1.0000 -> 0.1000
[selftest] ST2 STDP antisymmetry OK (err=0.00e+00)
[selftest] ST3 Gram-Schmidt orthogonal split max|P1.T P2|=4.34e-08 OK
[selftest] ST4 freq-ranks: token 1 (most-freq) rank=0 OK
[selftest] ST5 hebbian baseline logits OK
[selftest] ST6 theta_phase: enc_ret_corr=0.6313 n_phase0=5 n_phase1=5 OK
[selftest] ST7 freq_routed: n_high_steps=8 n_rare_steps=22 n_high_vocab=3 OK
[selftest] ST8 orthog_subspace: residual=0.00e+00 cross_grad_corr=0.0202 OK
[selftest] ST9 arm logits diversity: bt=1.3340e-01 bf=1.0729e-01 bo=1.3013e-01 OK
[selftest] ST10 joint_sweep OK (bpc=2.698 top1=0.0667)
[selftest] ST11 sparsify_bipolar_gpu nnz=5 OK
[selftest] ST12 LAMBDA_GRID excludes 0.0 OK
[selftest] ST13 LLM call counter == 0 OK
[selftest] ST14 ARMS consistent (6 arms; configs for 5 het arms) OK
[selftest] ST15 D2 atexit handler registered OK
[selftest] ST16 config-coherence sanity OK (N_DIM=1024 N_TRAIN=2000 seeds=1)
[selftest] ST17 freq_combine_w_theta: freq_enc_ret_corr=0.5401 rare_enc_ret_corr=0.5136 n_total=30 OK
[selftest] ST18 cost-model: n_steps 50->100 wall ratio 1.80x (1x=0.0316s 2x=0.0567s) within [1.2,4.0] OK
[selftest] ST19 ARM_FREQ_CONFIGS well-formed (5 arms) OK
[selftest] ST20 budget headroom: expected_wall=2592s (3 seeds) vs timeout=7200s = 2.78x OK
[selftest] ALL PASS
```

ST18 + ST20 are the v4-specific formula self-tests asserting measured values
match expected BEFORE dispatch (per USER discipline). ST18 confirms doubling
n_steps gives ~2x wall (validates the cost model for ARM_FREQ_DEEPER_TRAIN's
2x burden). ST20 confirms the 7200s timeout has 2.78x headroom over the
expected 2592s 3-seed wall.

## Wall budget (cost model)

Per-seed expected:
- ARM_BASELINE: ~50s (v3 measured)
- ARM_FREQ_V3_REPRO: ~85s (v3 FREQ measured)
- ARM_FREQ_DEEPER_TRAIN: ~170s (2x v3 FREQ; n_steps doubled)
- ARM_FREQ_BIGGER_RANK: ~85s (rank threshold doesn't change matmul cost)
- ARM_FREQ_SHARPER_GRADIENT: ~85s (LR doesn't change matmul cost)
- ARM_FREQ_COMBINE_W_THETA: ~170s (4 W matrices; ~2x v3 FREQ)
- Overhead (encoder build + corpus load + atexit + ckpt writes): ~25s

Per-seed total: ~670s. 3 seeds: ~2010s.
With 1.5x safety against unmodeled overhead: ~3015s.
Requested timeout: 7200s = 2.4x model estimate.

D1 roofline probe runs at dispatch time and refuses if extrapolation exceeds
0.8 * 7200 = 5760s.

## REMOTE VERIFY post-ship (cell-author discipline)

I will verify after Orchestrator confirms dispatch:
1. Anchor name + script path + commit hash propagate to remote queue.json correctly
2. `--self-test` passes on remote `.venv` (Py3.11 parity vs local Py3.11)
3. metrics path `data/exp_substrate_compose_freq_routing_v4_hparam_sweep/metrics.json`
   matches REQUIRED_FIELDS (verdict, verdict_msg, elapsed_s, summary)

Will file ACK after verify completes.

## Notes / caveats

- Anchor name has NO `_n<N>` suffix -> PROT-018 + PROT-019 don't apply (no
  tier-floor constraint). 7200s is set per USER spec, not PROT-019 floor.
- LLM-call counter asserted == 0 (substrate-only invariant; detailed in
  `detail.llm_forward_calls_total`).
- Per-seed checkpoint via `experiments/_seed_checkpoint.py`; atexit handler
  flushes partial state on SIGTERM / timeout (D2 discipline).
- v3_repro arm: BPC drift from v3's 7.2096 is logged in
  `detail.v3_repro.{bpc, drift_from_v3_ref, ok}`. Drift > 0.02 = FLAG (not GATE).
- COMBINE arm uses new kernel `build_logits_freq_combine_w_theta_gpu`
  (added in this commit); ST17 confirms it produces valid alpha_stack +
  finite enc-ret bank correlations per route.

## Discriminator priorities (Fix #28 -- per-arm metrics not verdict_msg)

When result lands, cert-owner should read per-arm metrics in this order:
1. `detail.sanity_rails.baseline_rail_ok` -- gate
2. `detail.by_arm_agg.ARM_FREQ_V3_REPRO.bpc_best_mean` vs v3's 7.2096 +/- 0.02
   (reproducibility check)
3. `detail.best_het_arm` + `detail.best_het_bpc` (which knob lifted, if any)
4. `detail.tuning_null_check.tuning_null` (if true -> HARD_FAIL_NOTUNING; the
   tuning sweep produced no movement; the 0.01 gap is structural at this regime)
5. `detail.by_arm_agg.ARM_FREQ_COMBINE_W_THETA.bpc_best_mean` -- does composition
   add (~7.13 target if FREQ + THETA stack linearly)?

---

**Waiting on:** Orchestrator dispatch ACK + remote queue entry verify-the-referent.
