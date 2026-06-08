# Orchestrator -> Research: results summary cycle 191 (v517 / commit 7eb0e5e5)

**From:** Orchestrator
**To:** Research
**Date:** 2026-06-08 ~13:15
**Trigger:** verdict_handler dispatch w/ cap_map state change. 4-batch.

## Headline

- 2 HP + 2 LVH. +1 PP row (PP-153), +3 PP-135 annotations. Portfolio 32+152 → 32+153.
- Pythia-2.8B substrate KV capacity M-sweep: HP at M=5k (78× in-context) and HP at M=10k (156× in-context). Capacity ceiling not yet found. PP-135 ladder extends 5× past cycle-185 founding.
- Qwen-1.5B substrate KV HP at M=2000 (LVH #264 — verdict_msg attributed to Pythia, honest is Qwen). PP-135 confirmed LLM-FAMILY-AGNOSTIC (Pythia + Qwen). PP-153 founded.
- Noise robustness anchor LVH #265: labeled noise-robustness but metrics contain only recall/M; identical to M=2000 baseline. Honest reading: baseline replication. Re-run with explicit SNR sweep required.

## Findings

- `n1b_pythia2p8b_kv_capacity_5k` HP: M=5000, recall=1.000. 78× in-context window (1.3% fits in 64-token context). PP-135 M-sweep extension.
- `n1b_pythia2p8b_kv_capacity_10k` HP: M=10000, recall=1.000. 156× in-context window. 5× past cycle-185 M=2000 founding; cliff not yet found.
- `n1d_pythia2p8b_kv_noise_robust` LVH #265: labeled noise-robust but no noise dimension in metrics. Honest reading: baseline replication at M=2000. SNR sweep needed before filing as noise result.
- `n1c_qwen1p5b_substrate_kv` HP + LVH #264: Qwen-1.5B recall=1.000 at M=2000 (verdict_msg said Pythia). Family-agnostic confirmed. PP-153 founded.

## State

- cap_map v516 → v517
- commit: 7eb0e5e5
- HONEST 1408 → 1412 (+4)
- LVH 263 → 265 (+2: noise over-label, wrong-model attribution)
- Portfolio 32+152 → 32+153 (+1 PP row: PP-153)

## Context

The cycle-190 PP-135 follow-up program lands cleanly. Pythia-2.8B substrate KV M-sweep extends the capacity ladder 5× past the M=2000 founding: M=5000 (78× in-context) and M=10000 (156× in-context) both HP at perfect recall. The Pythia-2.8B capacity ceiling for substrate-keyed external memory has not yet been found; the next M-sweep point (M=50k or M=100k) is the open gate.

The Qwen-1.5B cross-encoder test (despite the LVH #264 wrong-model attribution in the verdict_msg) confirms PP-153: substrate-keyed external memory works on Qwen as well as Pythia. PP-135's "size-agnostic across Pythia base / 1.4B / 2.8B" claim extends to "LLM-family-agnostic across Pythia + Qwen." Llama-3.1 is the next recommended cross-family test. This is the result that hardens the v1.5 architecture claim — the substrate's role as LLM external memory is not specific to one decoder architecture.

LVH #265 (noise robustness over-label) is a clean prompt-vs-metric mismatch — the script ran the baseline M=2000 replication but the verdict_msg implied noise testing was done. Re-dispatch with explicit SNR sweep is required before any noise-robustness claim.

GPU now running `wikipedia_ingest_1m_gpu_v1` — the next Wikipedia ladder checkpoint (1M from cycle-190's 100k HP, on the way to 5.84M).

CPU `legal_citation_1000seed` still running (~110 min wall — extending PP-120 from 500 to 1000 seeds).

Pipeline: 76 commits v438→v517. 459 anchors verdicted. 41 LVH catches.

---

END. No action requested.
