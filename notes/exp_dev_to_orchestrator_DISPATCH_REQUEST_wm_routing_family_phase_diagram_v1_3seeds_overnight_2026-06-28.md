# Dispatch request: substrate_wm_routing_family_phase_diagram_v1 (3 seeds, overnight_queue)

**From:** exp_dev (Opus 4.7 1M, agent-spawn)
**To:** orchestrator
**Date:** 2026-06-28
**Commit:** `18828429` (already on local main; needs hd_metrics_sync push)

## Summary

FOURTH systematic component-sweep cell ready for GPU dispatch. Routing-family
OUTER axis for multi-bank WM. 3 sibling seeds (CHUNKED per USER 2026-06-28).

## Anchors to dispatch (overnight_queue / GPU)

1. `substrate_wm_routing_family_phase_diagram_v1_seed_7`
2. `substrate_wm_routing_family_phase_diagram_v1_seed_13`
3. `substrate_wm_routing_family_phase_diagram_v1_seed_19`

## Files (all on commit 18828429)

- `experiments/_substrate_wm_routing_family_phase_diagram_v1_core.py` (shared core; 4 routing impls + selftest + sweep + verdict)
- `experiments/exp_substrate_wm_routing_family_phase_diagram_v1_seed_7.py`
- `experiments/exp_substrate_wm_routing_family_phase_diagram_v1_seed_13.py`
- `experiments/exp_substrate_wm_routing_family_phase_diagram_v1_seed_19.py`
- `preregs/2026-06-28_substrate_wm_routing_family_phase_diagram_v1.md`

## Smoke evidence (all 3 siblings; laptop CPU 2026-06-28)

| Seed | cardinality | sat | hp | PC recall | Verdict |
|------|-------------|-----|-----|-----------|---------|
| 7  | 8/8 | 3 | 5 | 0.989 | HARD_PASS_SMOKE |
| 13 | 8/8 | 6 | 2 | 0.996 | HARD_PASS_SMOKE |
| 19 | 8/8 | 4 | 4 | 0.993 | HARD_PASS_SMOKE |

POSITIVE CONTROL: partition routing at K=1024 reproduces WM v3 chain-grade.
All 4 routings COMPETITIVE at smoke (smoke K too small to discriminate);
discriminating regime is FULL K=4096+ + ADVERSARIAL.

Selftest passes on all 3 (cardinality + 4 routings registered + sanity
recall=1.000 + hierarchical 22-24% distinct from partition at ambiguous probe).

## Dispatch parameters per sibling

For each seed in {7, 13, 19}:

```bash
bash tools/orchestrator/queue_add.sh overnight_queue \
  substrate_wm_routing_family_phase_diagram_v1_seed_<SEED> \
  experiments/exp_substrate_wm_routing_family_phase_diagram_v1_seed_<SEED>.py \
  --prereg preregs/2026-06-28_substrate_wm_routing_family_phase_diagram_v1.md \
  --timeout 1800 \
  --purpose "FOURTH component-sweep: routing-family phase diagram for multi-bank WM (partition/knn_softmax/softmax_attention/learned_hierarchical); seed=<SEED>; 24 phase points; chain-grade evidence reproduction via positive control + family discrimination at K>=4096 ADVERSARIAL"
```

## Timeout justification

Per-seed FULL wall (GPU estimate):
- Codebook builds: 2 regimes * ~2s = 4s
- K=1024 routing*regime: 0.5s/arm * 4 routings * 2 regimes = 4s
- K=4096 routing*regime: 2-3s/arm * 8 = 20s
- K=8192 routing*regime: 4-6s/arm * 8 = 40s
- Total ~70-80s GPU

Timeout 1800s = 30 min = 20x margin (covers CPU fallback or slow-start).

PROT-019: anchor has no `_n<N>` suffix -> no timeout floor.
PROT-020: all files import torch at top -> GPU-queue OK.
PROT-021: cells import `_seed_checkpoint` -> checkpoint OK.
PROT-022: no `# KB_REFERENT:` declarations -> opt-in skip.

## Independence

8+ agents in flight; no collision:
- Different anchor name from WM K-ceiling v3 (`phase_diagram_wm_multibank_K_ceiling_sweep_32768_v3`)
- Different anchor name from encoder/cleanup/seqbind family cells
- Disjoint metrics directories (`data/exp_substrate_wm_routing_family_phase_diagram_v1_seed_*`)

## Standing disciplines verified

- ASCII-only (no unicode, no em-dashes, no emojis)
- META_RULE_AE: pre-reg bands LOCKED at module init
- META_RULE_AF: arms-must-differ -> 4 routing impls produce distinct
  ws_selected hashes at ambiguous regime (selftest verified hierarchical
  22% distinct from partition)
- META_RULE_H: CARDINALITY_OK_FULL=24, CARDINALITY_OK_SMOKE=8, both
  verified in selftest
- Fix #24 GPU mandate: torch at top of all files; FULL on CPU REFUSED
  unless HDLAB_QUEUE=local_cpu_queue
- Pre-dispatch self-test passes on all 3 siblings
- Pre-dispatch smoke passes on all 3 siblings
- Pre-reg committed (`preregs/2026-06-28_substrate_wm_routing_family_phase_diagram_v1.md`)
- Substrate-only decode (zero LLM calls; assert in main())
- Honest-downward verdicts (CHAIN_GRADE / ROUTING_FAMILY_INVARIANCE /
  MIDDLE_BAND / HARD_FAIL_CONTROL_FAIL all scientifically meaningful)

## Next action (orchestrator)

1. `hd_metrics_sync` push of commit `18828429` to origin/main
2. For each seed in {7, 13, 19}: `bash tools/orchestrator/queue_add.sh ...`
   (3 invocations; each runs --self-test + --smoke remote on GPU host
   before queuing)
3. Notify exp_dev (via SendMessage or routing note) on landing for each seed
4. Notify Skunkworks on chain-grade landing (data arrived; ready for landed-VET)

## REMOTE VERIFY post-ship

After dispatch, exp_dev will REMOTE VERIFY:
- `ssh marsh@home test -f C:/dev/hd-instrument/experiments/_substrate_wm_routing_family_phase_diagram_v1_core.py`
- `ssh marsh@home grep -c ROUTING_FAMILIES experiments/exp_substrate_wm_routing_family_phase_diagram_v1_seed_7.py` (expect 1)
- Per-seed metrics path: `data/exp_substrate_wm_routing_family_phase_diagram_v1_seed_<SEED>/metrics.json`
- REQUIRED_FIELDS check: verdict, verdict_msg, elapsed_s, summary, anchor_name,
  cardinality_ok, expected_n_units, observed_n_units, positive_control_result
