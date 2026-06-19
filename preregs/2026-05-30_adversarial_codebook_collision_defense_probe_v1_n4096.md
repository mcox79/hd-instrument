# G8 Adversarial Codebook Collision Defense Probe v1 at N=4096

## Anchor
adversarial_codebook_collision_defense_probe_v1_n4096

## Queue
overnight_queue (GPU)

## Script
experiments/exp_adversarial_codebook_collision_defense_probe_v1_n4096.py

## Scientific question
U2 pattern_2 (codebook-collision) achieved defense=0.000 (100% breach). Do
2 simple defense mechanisms achieve >=85% defense rate AND <=10% false-positive
rate on legitimate queries?

## Pre-registered bands
- HARD_PASS: at least one defense has defense_rate >= 0.85 AND fp_rate <= 0.10.
- HARD_FAIL: both defenses fail (defense_rate < 0.50 OR fp_rate > 0.25).
- MIDDLE_BAND: otherwise.

## Defenses
- A "query-similarity-threshold": reject if max cosine_sim(q, stored_keys) < 0.5
- B "codebook-distance-check": after retrieval, verify cos(q, retrieved_value)
  >= 0.4; else return null.

## Config
- N = 4096 (PROT-018 _n4096)
- M = 2048
- N_ADV_QUERIES = 32 codebook-collision attacks per seed
- N_LEG_QUERIES = 64 legitimate (stored) queries per seed
- Seeds: [7, 17, 23, 31, 41]

## Self-test
- Per-defense build + verdict gates HP/HF/MB exercised
- Live CPU smoke at N=1024 M=128 n_adv=4 n_leg=8

## Timeout estimate
- smoke wall ~3s
- 5 seeds * (96 queries + W setup); modest
- scaling_exp = 1.0; estimate = ceil(1.5 * 3 * 4 * 5) = 90s; large margin
- timeout_s = 14400 (user spec).

## Note
This is a smoke probe; successful candidates routed to engineering for full
defense implementation.

## Importance
HIGH - first defense candidate test against U2 collision breach.
