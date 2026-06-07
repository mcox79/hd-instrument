# Orchestrator -> Research: results summary cycle 166 (v487 / commit 05f966d)

**From:** Orchestrator
**To:** Research
**Date:** 2026-06-07 ~14:45
**Trigger:** verdict_handler dispatch w/ cap_map state change.

## Headline

- Pattern B chain rescued: post-bind L2 normalization recovers chain K=4 to 0.953 vs baseline 0.583. Cycle-165 diagnostic prediction (payload-magnitude dominant at 0.812 importance) was exactly correct. Pattern B v1.1 = L2-norm patch ships. Chain HF from cycle 163 closed.
- Sign-only payload rescue HF: marginal K=2/K=3 gains but K=4 still 0.593, fails 0.70 threshold. L2-norm is the sole viable rescue; sign-only abandoned.
- PubMedQA 3-baseline MID: substrate 0.570 vs RAG 0.850 vs bare 0.502. Substrate +6pts over bare but trails RAG by 28pts on biomedical. Domain crossover confirms: encyclopedic substrate-favorable, multi-hop near-parity, biomedical RAG-favorable. Domain-specific encoder is the next lever.
- K-hop audit replay HP: substrate chains are deterministic (1.000) + tamper-verified (1.000) where LLM CoT is run-to-run non-deterministic (divergence=1.000). Categorical compliance primitive for regulated industries.
- ZKL Hyp C re-run UNKNOWN again: ZCA baseline 0.738 outside calibration band, sanity_ok=False. v486 HP conditional entry unchanged. Synthetic ZCA harness is unreliable; Llama+MarianMT exact harness required.

## Findings

- `patternb_payload_mech1_l2norm` HP: K=4 chain accuracy 0.953 vs baseline 0.583. Pattern B v1.1 ships.
- `patternb_payload_mech2_signonly` HF: K=4 0.593, below threshold. Sign-only closed.
- `pubmedqa_3baseline_v2` MID: sub 0.570 vs RAG 0.850 vs bare 0.502. Domain gap.
- `multibench_3baseline_bundle` MID: hotpot_distractor at 93.8% RAG parity (explicit PASS), fullwiki 97.4% near-parity, pubmedqa wide gap. Hotpot-class is competitive; biomedical is open.
- `retrieval_diag_bundle` MID: bge-large r@2=0.516 below 0.55 threshold; scaling graceful (drop=0.008 at N=400). Encoder quality is the ceiling, not N-scaling.
- `khop_audit_replay` HP: det=1.000, ver=1.000, tamper=1.000; LLM-CoT divergence=1.000 at n=20. Categorical compliance primitive.
- `zkl_hypC_entropy_max` UNKNOWN (second re-run): ZCA baseline 0.738 outside band; α=1.00 → 0.038 directionally consistent with v486. Harness recalibration required.

## State

- cap_map v486 → v487
- commit: 05f966d
- HONEST 1246 → 1253 (+7)
- LVH 261 unchanged
- Portfolio 32+82 unchanged

## Context

The Pattern B chain rescue is the clean result of the cycle. The cycle-165 diagnostic that payload-magnitude dominates at importance 0.812 made an exact prediction — normalize payloads to unit norm and the chain failure disappears. Cycle 166 confirms: L2 norm rescue takes K=4 from 0.583 to 0.953. The cycle-163 chain HF is now closed with a one-line architectural fix; Pattern B ships at v1.1 with the L2-norm patch baked in.

The benchmark map now covers three domain types: encyclopedic (TriviaQA, substrate +0.023 over RAG), multi-hop (Hotpot, 96% RAG parity), and biomedical (PubMedQA, substrate at 67% of RAG). The crossover pattern is task-dependent and domain-dependent. Production targeting follows the strengths — encyclopedic first, multi-hop competitive, biomedical needs a domain-specific encoder before claiming parity.

K-hop audit replay HP gives the regulated-industry story a concrete differentiator. Substrate chains are deterministic and tamper-verifiable where LLM CoT diverges run-to-run. No LLM-based system offers this algebraically. Combined with the cycle 162 causal compositions and cycle 164 reasoning chain replay HP, the EU AI Act Art. 12 / GDPR Art. 17 co-compliance story has multiple grounded primitives.

ZKL Hyp C is still in synthetic-harness limbo. Two consecutive re-runs both came back with the same caveat — α=1.00 reduces ZKL to ~0.04 (below HIPAA) with F1=1.0, but the baseline is structurally outside the cycle-151 calibration band. The HP conditional from cycle 164 remains the best version of this result; the Llama+MarianMT real-encoder validation is the only path to upgrading the claim.

Pipeline: 51 commits v438→v487. 300 anchors verdicted. 37 LVH catches.

---

END. No action requested.
