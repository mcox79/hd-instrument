# G10 Multi-Hop Adversarial Concurrent Edits v1 at N=4096

## Anchor
multi_hop_adversarial_concurrent_edits_v1_n4096

## Queue
overnight_queue (GPU)

## Script
experiments/exp_multi_hop_adversarial_concurrent_edits_v1_n4096.py

## Scientific question
Stress test combining U2 adversarial patterns + T2 concurrent edits. Does
the substrate maintain defense rate >=80% AND audit chain integrity across
all 4 (adversarial, edit) scenarios in >=3/5 seeds?

## Pre-registered bands
- HARD_PASS: defense_rate >= 0.80 AND audit chain intact across all 4
  scenarios in >= 3/5 seeds.
- HARD_FAIL: any scenario shows defense_rate < 0.30 OR audit corrupts.
- MIDDLE_BAND: otherwise.

## Scenarios
- s1: cross-talk-adversarial + edits-on-path
- s2: codebook-collision-adversarial + edits-off-path
- s3: deleted-fact-adversarial + mixed-edits
- s4: edited-fact-adversarial + no-edits (baseline)

## Config
- N = 4096 (PROT-018 _n4096)
- M = 2048, depth = 5, K_paths = 100, N_STARTS = 16
- N_EDITS = 32
- Seeds: [7, 17, 23, 31, 41]
- beta_D = 4.0
- Path D ONLY

## Self-test
- 4 scenarios + verdict gates exercised
- Live CPU smoke at N=1024 M=128 depth=2 K=10

## Timeout estimate
- smoke wall ~3s
- 5 seeds * 4 scenarios; each scenario = Path D N_STARTS=16, K=100, depth=5
- scaling_exp = 1.5; estimate = ceil(1.5 * 3 * 4 * 5 * 4 / 1) ~ 360s
- timeout_s = 14400 (user spec).

## Importance
HIGH - first agentic deployment stress test (compose U2 + T2 attack surface).
