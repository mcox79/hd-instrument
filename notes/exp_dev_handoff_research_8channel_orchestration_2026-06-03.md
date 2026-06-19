# exp_dev hand-off -- research: 8-channel training-signal orchestration architecture

**Filed-by**: research sub-agent 2026-06-03
**Trigger**: research drill delivered notes/research_drill_8_channel_orchestration_architecture_2026-06-03.md
**Pause state**: check data/orchestrator_paused.flag before dispatching any queue_add.sh calls

Per [[feedback-no-experiment-design-in-prompts]]: this file provides TASK + WHY + CONTRACT + AUTONOMY. exp_dev decides anchor names, sweep grids, threshold formulas, HF/HP numerical bounds, queue choice, and ETA. Do NOT import these into the dispatch prompt.

---

## Anchor candidates (rank-ordered)

### Rank 1 -- Minimum viable channel-ablation probe
- **Anchor pointer**: N_channels ablation study on small transformer LM. Factor A: channels in {1, 2, 4, 8}. Factor B: orchestration strategy in {uniform_gain, cipolla_uncertainty, pcgrad_projection}.
- **Substrate-product reading**: if 8-channel outperforms 4-channel by >2% on a downstream task, the channel orchestration architecture has product value. If not, the channel set is largely redundant and can be pruned.
- **Tier hint**: Tier-1 (directly addresses multi-channel training-signal value).
- **Why now**: research drill identified concrete P_deflated=0.38 estimate and specific HARD-PASS/HARD-FAIL bands; minimum viable probe is 4-8 GPU-hours on a small model; this is the cheapest decisive test for the 8-channel architecture hypothesis.

### Rank 2 -- Phasic/tonic channel timing probe
- **Anchor pointer**: compare always-on-8 vs phasic-4-tonic-4 channel activation profile on same small transformer LM. Measure per-step channel activation frequency from learned g_theta gating network.
- **Substrate-product reading**: if phasic channels self-organize to <20% activation frequency and tonic channels maintain >80%, the biological phasic/tonic decomposition holds in the ML setting. This validates the auto-curriculum claim.
- **Tier hint**: Tier-2 (validates a specific architectural choice; less decisive than rank 1).
- **Why now**: rank 1 probe establishes whether 8-channel works at all; rank 2 probes the mechanism. Should ride the same GPU instance as rank 1.

### Rank 3 -- Channel-pair synergy measurement
- **Anchor pointer**: pairwise Shapley-value style ablation on 8 channels to measure Synergy(i,j) for all 28 pairs. Identify top synergistic pairs and top antagonistic pairs.
- **Substrate-product reading**: synergistic pairs (e.g. Contrastive + Repulse-class) can be bundled as a single "channel cluster" in the product; antagonistic pairs suggest the lower-priority channel should be suppressed via priority hierarchy.
- **Tier hint**: Tier-2 (diagnostic; informs architecture pruning post-rank-1).
- **Why now**: can be run as a post-hoc analysis on rank 1 checkpoints; no additional training required.

---

## Context pointers

- Research note: d:/AI/hd-instrument/notes/research_drill_8_channel_orchestration_architecture_2026-06-03.md
- cap_map (current): d:/AI/hd-instrument/notes/substrate_capability_map.md
- PCGrad paper: NeurIPS 2020, arXiv:2006.06520
- Cipolla uncertainty weighting: arXiv:1705.07115
- Friston free energy + ACh precision: PMC4235126
- Neuromodulator orchestration review: PMC2080765
- Status log: d:/AI/hd-instrument/data/orchestrator_status_log.jsonl (entry written 2026-06-03)

---

## Contract

exp_dev commits to:
1. Pre-register HARD-PASS / MIDDLE / HARD-FAIL bands BEFORE any queue_add.sh call.
2. Use `set -ex` + `python -u` + `stdbuf -oL` + `tee` to remote log per [[feedback-always-verbose-remote-dispatch]].
3. Check data/orchestrator_paused.flag before any queue_add.sh.
4. Verify anchor name uniqueness before ship per [[feedback-ship-name-collision]].
5. Emit per-cell progress stdout + partial JSON per [[feedback-testbed-progress-logging-and-restart]].
6. GPU first for any probe with seeds >= 3 and cells >= 8 per [[feedback-gpu-first-for-depth-probes]].
7. Do NOT pre-frame as PASS; let data decide per [[feedback-no-preframe-batch-all-pass]].

## Autonomy declaration

exp_dev has full autonomy on: anchor names, sweep grid values, exact threshold formulas, HP/MID/HF numerical bounds, queue assignment (CPU vs GPU), ETA estimates, and implementation details of the channel ablation testbed. Research note provides biological + ML principles only; architectural instantiation is exp_dev's domain.
