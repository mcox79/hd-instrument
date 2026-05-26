# exp_dev -> queue: Cap 12 noise-cleanup OptShrink anchor (2026-05-24)

Shipment of OptShrink data-driven SVD-shrinkage denoising experiment, anchored
from `notes/research_audit_followup_drills_2026-05-24.md` Section 3 (Portfolio
Gap 1 closure attempt for Cap 12 customer-facing noise envelope).

## Queue entries (Schema B markdown table per agent spec)

| queue            | name                                         | script                                                          | prereg                                                              | timeout(s) |
|------------------|----------------------------------------------|-----------------------------------------------------------------|---------------------------------------------------------------------|------------|
| remote_cpu_queue | wave14_cap12_noise_cleanup_optshrink_v1      | experiments/exp_wave14_cap12_noise_cleanup_optshrink_v1.py      | preregs/2026-05-24_wave14_cap12_noise_cleanup_optshrink_v1.md       | 5400       |

## Pre-ship state

- Self-test 13/13 PASSED (incl. clean-Hadamard eta=0 spectral preservation;
  lambda*(beta=1) == 4/sqrt(3) to 1e-6)
- Smoke at N=64 / 1-seed / 2 codebooks / 2 eta: cells produced, metrics.json
  written, INCONCLUSIVE verdict on insufficient cells (expected).
- Name uniqueness: grep across `data/overnight_queue/queue.json`,
  `data/remote_cpu_queue/queue.json`, `data/event_outcomes/` returned ZERO
  hits for "wave14_cap12_noise_cleanup_optshrink".

## Hypothesis (one line)

Donoho-Gavish-Nadakuditi OptShrink applied to eta-bit-flip-corrupted codebook
W_noisy reconstructs W_cleaned with eta_effective <= eta_input/3 across >=4/5
families at eta_input in {0.05, 0.10}, AND Cap 12 routing >=4/5 on W_cleaned
at eta_input <= 0.10. If both, Portfolio Gap 1 closes.

## Routing note

- Queue: `remote_cpu_queue` (pure-CPU; one SVD per cell; 125 cells; long enough
  to warrant the remote machine, not laptop CPU).
- ETA: 45-60 min CPU wall.
- Note: this queue may have a dead runner per [[project-cpu-resource-underutilized]].
  If `cpu_runner_0` is down on marsh@home, the experiment will sit pending
  until revived. The orchestrator may need to launch / revive via
  `tools/orchestrator/cpu_runner_0_launcher.bat` or
  `tools/orchestrator/revive_cpu_runner_via_schtasks.ps1`.
