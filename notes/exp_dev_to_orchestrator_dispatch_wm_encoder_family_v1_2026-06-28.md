# Dispatch request: substrate_wm_encoder_family_phase_diagram_v1

**From:** exp_dev (Opus 4.7 1M agent-spawn)
**To:** orchestrator
**Date:** 2026-06-28 / 2026-06-29 UTC

## Cell

**Anchor base:** `substrate_wm_encoder_family_phase_diagram_v1_seed_{7,13,19}`
**Commit:** `329d9ef2` (on `main`; needs push by `hd_metrics_sync` before remote queue_add reads it)

## State

- **Committed:** YES (commit `329d9ef2`)
- **Local self-test (3 seeds):** SELFTEST_OK all 3 (seed=7, 13, 19; per-encoder sanity multi recall 0.50-0.94 at K=16 B=2 N=512)
- **Local smoke (seed=7):** HARD_PASS_SMOKE — 20/20 pts (4 skipped K*B>CB), sat=0 hp=4 mb=0 floor=11 fail=5; 4-encoder-distinct; positive_control@hrr_real K=64 B=4 N=4096 multi=0.500; cliff observable; smoke_gate_pass=True
- **Pre-reg:** `preregs/2026-06-28_substrate_wm_encoder_family_phase_diagram_v1.md` (committed)

## Dispatch plan (3 seeds, GPU)

Target queue: **overnight_queue** (GPU; CPU+GPU queues currently IDLE per Research context; need to fill GPU work overnight).

Per-seed dispatch commands (all 3 in parallel; each runs ~15 min on GPU):

```bash
# Seed 7
bash tools/orchestrator/queue_add.sh \
    overnight_queue \
    substrate_wm_encoder_family_phase_diagram_v1_seed_7 \
    experiments/exp_substrate_wm_encoder_family_phase_diagram_v1_seed_7.py \
    preregs/2026-06-28_substrate_wm_encoder_family_phase_diagram_v1.md \
    3600

# Seed 13
bash tools/orchestrator/queue_add.sh \
    overnight_queue \
    substrate_wm_encoder_family_phase_diagram_v1_seed_13 \
    experiments/exp_substrate_wm_encoder_family_phase_diagram_v1_seed_13.py \
    preregs/2026-06-28_substrate_wm_encoder_family_phase_diagram_v1.md \
    3600

# Seed 19
bash tools/orchestrator/queue_add.sh \
    overnight_queue \
    substrate_wm_encoder_family_phase_diagram_v1_seed_19 \
    experiments/exp_substrate_wm_encoder_family_phase_diagram_v1_seed_19.py \
    preregs/2026-06-28_substrate_wm_encoder_family_phase_diagram_v1.md \
    3600
```

**Timeout per seed:** 3600s (1h margin above 15-min per-seed budget on GPU)
- Per-point on GPU N=8192: 7-20s estimated
- 48 pts/seed * 15s avg = 720s ~ 12 min; add 30s init + margin = 1h cap
- Heuristic: ceil(1.5 * smoke_wall_s * (FULL_N/smoke_N)^1.5 * 1) = ceil(1.5 * 7 * (8192/4096)^1.5) = ceil(1.5 * 7 * 2.83) = 30 sec. Bumped to 3600s for VRAM-recovery + FFT throughput variance + 4-encoder × 48 pts.

PROT-019 check: anchor has no `_n<N>` suffix (fixed-N cell at N=8192) → no timeout floor enforced; 3600s OK.
PROT-018 check: anchor has no `_n<N>` suffix → bypass.

## Expected at FULL (per encoder, N=8192, K x B grid = 12 pts each)

Hypothesized@:
- HRR_real K=64 B=4 (positive control): MULTI >= 0.50 — gate condition for non-CONTROL_FAIL
- HRR_real / binary_bipolar K_cliff(B) = 256·B → expected MB+HP coverage at K ∈ {64-256} per B
- FHRR predicted higher per-bank cap (1.5x); should HARD_PASS at higher K
- sparse_bipolar predicted half per-bank cap; SAT at low K, FLOOR earlier

Discriminating_fraction target >= 0.30 (15+ of 48 pts per seed in MB+HP+SAT).

## After dispatch

1. Orchestrator: `predispatch_check.py substrate_wm_encoder_family_phase_diagram_v1` (verify no prior anchor); should be CLEAN.
2. After landing: notify Skunkworks via SendMessage for landed-VET.
3. Cross-cell stitch: PC encoder family v1 (CERT-pending today) + this WM encoder family v1 → potential SUBSTRATE_ENCODER_FAMILY_DISCRIMINATING_ACROSS_PRIMITIVES (chain-grade atomization candidate if both HARD_PASS).

## REMOTE VERIFY post-ship (exp_dev responsibility)

After Orchestrator confirms queue_add succeeded:
1. Verify remote queue entry exists: `ssh marsh@home "ls C:/dev/hd-instrument/data/overnight_queue/"` shows the 3 entries
2. Verify remote cell-spec matches commit `329d9ef2`: `ssh marsh@home "cd C:/dev/hd-instrument && git log --oneline -1 -- experiments/_substrate_wm_encoder_family_phase_diagram_v1_core.py"`
3. Watch for landing: poll `data/exp_substrate_wm_encoder_family_phase_diagram_v1_seed_{7,13,19}/metrics.json` mtime; expect ~15 min after queue start
