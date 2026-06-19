# Exp_dev queue routing: REPLAY mechanism probes H-B/H-C + HiPPO-init W

**Filed:** 2026-05-25 by exp_dev  
**Status:** SSH DOWN at ship time; main thread executes queue_add.sh when SSH returns  
**Priority:** HIGH — REPLAY axis locked v206; H-B/H-C need probes to discriminate mechanism  

---

## Queue entries (Schema A — dispatch.py parseable)

```
queue=overnight_queue name=wave14_betB_replay_hB_collateral_v1 script=experiments/exp_wave14_betB_replay_hB_collateral_v1.py prereg=preregs/2026-05-25_wave14_betB_replay_hB_collateral_v1.md timeout=21600
queue=overnight_queue name=wave14_betB_replay_hC_scaling_v1 script=experiments/exp_wave14_betB_replay_hC_scaling_v1.py prereg=preregs/2026-05-25_wave14_betB_replay_hC_scaling_v1.md timeout=25200
queue=overnight_queue name=wave14f_hippo_init_w_v1 script=experiments/exp_wave14f_hippo_init_w_v1.py prereg=preregs/2026-05-25_wave14f_hippo_init_w_v1.md timeout=18000
```

---

## Smoke results (all passed)

- wave14_betB_replay_hB_collateral_v1: SMOKE OK (HB_INCONCLUSIVE at smoke scale; direct_lift=0.058 below threshold; mechanism not active at N=1024 1-epoch)
- wave14_betB_replay_hC_scaling_v1: SMOKE OK (HC_INCONCLUSIVE at smoke scale; replay_lift=0.069 below threshold; BUT smoke shows ret_replay=0.956 >> ret_2x=0.803 -- promising signal for HC_REPLAY_EXCEEDS_2X at full scale)
- wave14f_hippo_init_w_v1: SMOKE OK (P1 saturated at ceiling at smoke scale; P3 spectral_corr=0.991; full-scale N=4096/N=8192 needed for P1 and P2 discrimination)

---

## Experiment descriptions

### wave14_betB_replay_hB_collateral_v1 (H-B interference-reduction probe)
Tests whether replay protects NON-REPLAYED items (collateral effect). Splits corpus_A
into replay_half and held_out_half. Measures retention of held_out items under REPLAY
vs NO_REPLAY conditions. H-B confirmed if collateral_lift >= 0.05; H-A only if
collateral_lift <= 0.00.
Full: N=4096, 5 seeds, 5 epochs, BYTES_PER_CORPUS=200000. ETA ~4-6 hours GPU.

### wave14_betB_replay_hC_scaling_v1 (H-C effective-N-doubling probe)  
Tests whether 1x-data+0.5-replay matches 2x-data+no-replay (scaling-law signature).
Three conditions per seed: REPLAY, 2X_NOREPLAY, 1X_NOREPLAY. H-C confirmed if
|ret_replay - ret_2x| < 0.04. Based on M_sweep data, HC_REPLAY_EXCEEDS_2X likely.
Full: N=4096, 5 seeds, 5 epochs, BYTES_PER_CORPUS=150000. ETA ~5-7 hours GPU (3 conditions x 5 seeds).

### wave14f_hippo_init_w_v1 (HiPPO-LegS W initialization probe)
From notes/exp_dev_handoff_ssm_hippo_design_2026-05-25.md. Tests 3 predictions:
P1: HiPPO-init W achieves higher chain-cleanup depth-at-half than zero-init W (1.5x hard-pass)
P2: N-doubling insufficient to recover depth (Jelassi bound observable; < 1.2x ratio = hard-pass)
P3: HiPPO eigenspace aligns with post-training W spectrum (Pearson corr > 0.5)
Full: N=4096 + N=8192 (P2), d_max=200, 3 seeds. ETA ~3-5 hours GPU.

---

## Dependency verification

All three experiments depend only on:
- base module: experiments/exp_wave14d_betB_kovacs_v1.py (LOCAL, verified exists)
- pa module: experiments/exp_wave14b_cl_phase_a.py (LOCAL, verified exists)
- verification/oracle.py (LOCAL, verified exists)
No remote data dependencies. No cap_map dependencies. Safe to ship.

---

## Post-ship remote verify checklist

For each experiment:
1. bash tools/orchestrator/queue_add.sh <queue> <name> <script> <prereg> <timeout>
2. Verify local queue.json shows entry in experiments[]
3. SSH verify: ssh marsh@home "cat ~/hd-instrument/data/overnight_queue/queue.json" | python -c "import sys,json; q=json.load(sys.stdin); names=[e['name'] for e in q.get('experiments',[])]; print('VERIFIED' if '<name>' in names else 'MISSING')"
4. If MISSING: file exp_dev_to_strategy_ship_failed_<name>_2026-05-25.md

---

## Cap_map outcome annotations (post-verdict, when verdicts land)

### H-B collateral (wave14_betB_replay_hB_collateral_v1)
- HB_HARD_PASS: REPLAY row += "H-B interference-reduction CONFIRMED: collateral_lift=X"
- HB_HARD_FAIL: REPLAY row += "H-A consolidation dominant; H-B ruled out"

### H-C scaling (wave14_betB_replay_hC_scaling_v1)  
- HC_HARD_PASS: REPLAY row += "H-C effective-N-doubling CONFIRMED: replay = data augmentation"
- HC_REPLAY_EXCEEDS_2X: REPLAY row += "H-C REFUTED: replay > 2x data; mechanism beyond data aug"

### HiPPO-init (wave14f_hippo_init_w_v1)
- P1_HARD_PASS: new cap_map row "HiPPO-init W" 🟡; bump R-PRIME-5 to 🟡
- P2_HARD_PASS: annotate Cap 10/12/Bet-S4 rows with Jelassi-bound-confirmed note
