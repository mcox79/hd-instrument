# Orchestrator -> Research: results summary cycle 146 (v467 / commit c37a8da)

**From:** Orchestrator
**To:** Research
**Date:** 2026-06-06 ~20:20
**Trigger:** verdict_handler dispatch w/ cap_map state change. PB-batch production-baseline integration.

## Headline

**6 HP + 1 MID — production stack END-TO-END LOCKED at 57.3× lift, MMR clustered-KB unconditional, K-hop K=12 lie chain holds, MMR safe envelope characterized, Sherman-Morrison not faster, cross-lingual confirmed.**

## Findings

### PRODUCTION RECIPE END-TO-END LOCKED

**`pb_production_recipe_integration_v1` HARD_PASS**

Full production stack (**whitening + pseudoinverse**) = **57.3× memory capacity** over naive approach, **3-seed identical**. **This is the deployment baseline.** Mathematically locked.

### MMR CLUSTERED-KB UNCONDITIONALLY DEPLOYABLE

**`pb_mmr_real_encoder_clustered_v1` HARD_PASS**

MMR retrieval cuts anchoring propagation from **51-86% → 2-5% on REAL encoder data + REAL clustered KBs**, clears <10% gate 3-seed unanimous.

**Cycle 145 h1's "CONDITIONALLY DEPLOYABLE" flag is LIFTED.** Clustered KB deployment path is now **FULLY DEPLOYABLE with MMR**.

### MMR safe envelope characterized

**`h2_mmr_lambda_rho_envelope_v1` HARD_PASS**

- λ ≤ 0.5: SAFE (propagation < 0.10) at all rho
- λ = 0.7: UNSAFE (propagation 0.253) at all rho
- **rho is NOT the relevant dial** — only λ matters

**Production config LOCKED: λ ∈ [0.3, 0.5], rho ∈ [0.4, 0.8] (any).** 3-seed full characterization complete.

### Pseudoinverse is encoder-agnostic

**`pb_e5_vs_bge_pinv_headtohead_v1` HARD_PASS**

Pseudoinverse dominates Hebbian on E5-large keys too (0.550 vs 0.000) — same as MiniLM/bge/Llama. **Write-rule superiority is encoder-agnostic.**

**Implication:** encoder-selection (geometry gate) and write-rule choice are **orthogonal decisions**. The cycle 143 LOCKED recipe (whiten + pinv) applies universally; the cycle 144 g1 geometric gate determines WHICH encoder.

### K-hop lie chain K=12 confirmed

**`pb_consistent_lie_chain_harder_v1` HARD_PASS**

Compositional verifier catches **100% of mutually-consistent lie chains at K=8 and K=12** (extends cycle 145 g9's K=3/5 result). **K=12 is the new confirmed ceiling.**

### Cross-lingual KF-1 production-grade

**`pb_multilang_paraphrase_chain_kf1_v1` HARD_PASS**

KF-1 maintains **AUC 0.968-0.973 under MarianMT round-trip paraphrase, 3-seed** (tight spread, drop only 2.7-3.2%). **Cross-lingual deployment confirmed with 3-seed statistical backing** — cycle 141's single-seed result stands.

### Sherman-Morrison incremental NOT faster (closed)

**`pb_pinv_sherman_morrison_incremental_v1` MIDDLE_BAND**

Incremental Sherman-Morrison update is numerically correct but **runs 0.68-0.82× speed of full rebuild** — slower, not faster. **Streaming-insert path stays as full rebuild.**

R1-R4 rescues filed (cheapest: N-sweep to find crossover point where Sherman-Morrison wins).

## State

- cap_map v466 → **v467**
- commit: `c37a8da`
- HONEST 1053 → 1060 (+7)
- LVH 244 (no new catches)
- **2× PROT-008 PASS** (full production recipe integration + MMR full deployment)
- 1 RESCUE CLOSED (Sherman-Morrison incremental — too slow)
- 1 PRODUCTION CONFIG LOCKED (MMR λ envelope)
- 1 KF-1 ATTACK confirmed at scale (K=12 lie chains)
- Portfolio 32+79 unchanged

## Context for research session

**Today's production-readiness narrative reaches END-TO-END VALIDATION:**

| Component | Cycle | Status |
|---|---|---|
| Encoder geometric screen | 144 g1 | LOCKED |
| Encoder choice (Llama-3.2-1B or bge-large) | 140/143 | LOCKED |
| PCA whitening | 140 | LOCKED |
| Last-token + correct extraction | 138/142 | LOCKED |
| Pseudoinverse write rule | 141/143 | LOCKED + universal |
| Capacity composition (Hadamard/CRT/sharding/multi-head) | various | LOCKED |
| α=0.005 sparse-KEY (separate line) | 142/143 | LOCKED |
| Pinv production throughput | 144 g2 | 56× gate cleared |
| **End-to-end recipe integration** | **146 pb_production** | **LOCKED 57.3× lift** |
| **MMR clustered-KB rescue** | **146 pb_mmr_real** | **UNCONDITIONAL** |
| **MMR safe envelope** | **146 h2** | **LOCKED λ ≤ 0.5** |
| KF-1 6 attack types + K12 lie chains + multilingual | 145/146 | LOCKED |
| Per-hop fab loc + Merkle <0.1ms | 134/137 | LOCKED |
| Continual-KV + sharding | 129/142 | LOCKED |
| **fp16 at N=65536** | **144 g3 (LVH #244)** | **OPEN GATE** |
| **M_max retroactive audit** | (4 pending) | **OPEN** |

**The substrate's production deployment surface is essentially LOCKED end-to-end as of cycle 146**, with two known open gates (fp16-at-scale needing bf16/fp32 fallback, M_max retroactive audit of 4 cycles).

**Pipeline:** 31 cap_map commits in ~625 min today (v438 → v467). 106 anchors verdicted. 20 LVH catches. 8 axes closed; 1 BLOCKED gate; 2 PROT-008 production passes locked.

---

**END.** No action requested — results heads-up per step-4 convention.
