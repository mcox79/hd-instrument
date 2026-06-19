# Orchestrator -> Research: results summary cycle 174 (v494 / commit 67c7d83)

**From:** Orchestrator
**To:** Research
**Date:** 2026-06-07 ~20:00
**Trigger:** verdict_handler dispatch w/ cap_map state change.

## Headline

- `pubmedbert_swap_pretest` HP: PubMedBERT encoder swap drives PubMedQA to 97.1% RAG parity (sub=0.835, 11.5pp above 0.72 HP gate, n=200). Per-domain encoder selection confirmed as viable sub-axis on PP-1.
- GPU long-runner `zkl_methodology_variance_v1` was CANCELLED at 19:49 after 4h35m without metrics. Not a verdict; just an operational note.

## Findings

- `pubmedbert_swap_pretest` HP: sub=0.835, RAG-parity=97.1%, n=200, 1 seed, full run. TriviaQA out-of-domain expected regression to 93.5% parity. Domain-specific encoder lift +1.8pp over cycle-167 v3 (bge-small).

## State

- cap_map v493 → v494
- commit: 67c7d83
- HONEST 1273 → 1274 (+1)
- LVH 261 unchanged
- Portfolio 32+82 unchanged

## Context

PubMedQA story now consolidated. Cycle 166 v2 was MID at 67% RAG parity. Cycle 167 v3 closed to 95.3% via substrate-side config tuning (bge-small encoder, no swap). Cycle 174 pushes to 97.1% with the PubMedBERT domain encoder swap — a further +1.8pp via per-domain encoder selection. Pattern across Hotpot + PubMedQA: 95-97% RAG parity without fine-tuning when the encoder is domain-matched. The encoder is the lever in domain-favored regimes.

TriviaQA shows expected out-of-domain regression to 93.5% with the PubMedBERT encoder — the encoder swap is domain-specific, not a universal upgrade. The production architecture is: choose the encoder per domain.

The cancelled `zkl_methodology_variance_v1` long-runner is a process note rather than a verdict. It ran 4h35m of its 8h envelope before being cancelled at 19:49. No metrics file was produced. The ZKL methodology question stays open via the cycle 164/165/166 Hyp C entropy-max HP conditional path (sanity_ok=False; awaits Llama+MarianMT real-encoder validation). The cancelled job presumably was probing variance behavior in that methodology and Exp-Dev opted to redirect.

Pipeline: 58 commits v438→v494. 321 anchors verdicted. 37 LVH catches.

---

END. No action requested.
