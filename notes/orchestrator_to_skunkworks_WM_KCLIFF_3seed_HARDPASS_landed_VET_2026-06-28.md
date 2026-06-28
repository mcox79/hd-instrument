# orchestrator -> skunkworks: 3-seed WM K-cliff phase diagram HARD_PASS — landed-VET

**Date:** 2026-06-28T17:18Z
**Surfaced by:** orchestrator post-recovery audit (cells landed 13:10-13:12 UTC; pre-discovered during runner zombie investigation)

## Quick state
3-seed WM K-cliff phase diagram (substrate_wm_multibank_K_cliff_phase_diagram_v1, seeds 7/13/19) landed HARD_PASS on overnight_queue earlier today; not surfaced to you via Monitor at the time (heartbeat bug masked landing path). All 4 cells landed:

| cell | verdict | elapsed | gpu_util_p50 | corridor_pass | cardinality_ok |
|---|---|---|---|---|---|
| seed_7_smoke | SMOKE_PASS | 4.9s | 43% | n/a (5 pts) | True |
| seed_7_v1 | HARD_PASS | 32.9s | 77% | 3/5 | True |
| seed_13_v1 | HARD_PASS | 31.3s | 77% | 3/5 | True |
| seed_19_v1 | HARD_PASS | 35.5s | 88% | 3/5 | True |

## Identical phase structure across 3 seeds
All 3 FULL seeds: 45 phase points (5 K x 3 overlap x 3 noise) x 2 arms = 90 units. Each seed reports:
- `phase_points=45 pass=27 saturate=27 floor=0 probe_cliffs=36 arms_differ=27/9`
- `corridor_pass=3/5` (3 of 5 overlap-x-noise corridors discriminate at full K-range)
- `cliff_per_ov_rn={'ov=0.00_rn=0.00': 16384, 'ov=0.00_rn=0.05': 16384, ...}` (K=16384 is the cliff floor across clean-input corridors)

Key cert-question for you (Fix #28 / by-construction-saturation defaulting):
- `saturate=27/45` (60%) — high saturation count; need verdict on by-construction vs. real-mechanism
- `probe_cliffs=36/45` (80%) — HP_VRAM_PROBE_BREACH at K=65536 expected per pre-reg cliff prediction (treated as cliff markers NOT failures per cell-author spec)
- `arms_differ=27/9` notation suggests 27 distinct + 9 collapsed-arms — verify substrate vs random truly diverged at the 27 passing points (Fix #28: read per-arm metrics not verdict_msg)

## Where to look
Per Fix #18 absolute-path discipline:
- `C:/dev/hd-instrument/data/exp_substrate_wm_multibank_K_cliff_phase_diagram_v1_seed_7_v1/metrics.json` (+ partial_metrics_seed7_K{4096,8192,16384}_ov{000,010,030}_rn{0000,0050,0150}_regime{RANDOM,SUBSTRATE}.json — 36 partials)
- ditto seed_13_v1 + seed_19_v1
- pre-reg: `preregs/2026-06-28_substrate_wm_multibank_K_cliff_phase_diagram_v1.md`
- exp_dev's original routing note: `notes/exp_dev_to_orchestrator_dispatch_wm_multibank_K_cliff_phase_diagram_v1_3seeds_2026-06-28.md`

## Cert-grade ask
Skunkworks landed-VET to tier. Chain-grade-eligible per exp_dev's framing: 3-seed aggregation grade WM multibank K-cliff phase diagram extension to K=65536 with overlap + routing-noise axes.

orchestrator
