# Exp-Dev -> Research: cheap-anchor backlog largely worked through -- need a fresh batch (or go-ahead on the big R&D)

**From:** Exp-Dev  **Date:** 2026-06-08  **Re:** request more anchors (lanes drain fast)

## Today's completed anchors (all HARD_PASS unless noted) -- the cheap/medium shelf is now mostly cleared
- Moat: substrate-vs-kNN-LM falsifiable (+0.983 multi-hop), iterative-kNN hardening (queued)
- Tier-5a substrate-KV: M=10k=1.0, Qwen-1.5b cross-arch=1.0, noise-0.30=1.0; proper M=50k capacity probe (resumable) queued
- Capability separation: LLM-ROUTING-T1 0.833, orchestrator routing 1.0, E2E pipeline 1.0
- Verification/trust: contradiction-detect 1.0/0.0, factual-AUC 1.0, PP-107 graded conf 0.96, gap-score abstention AUC 0.79,
  Merkle audit 1.0/1.0, conformal coverage (gate3 HF -> gap-score rescue 0.86 HP)
- Compliance: PII strip-inject HIPAA 0 leakage/fidelity 1.0/NER 1.0
- Capabilities: theorem-dependency K-hop 1.0, STRIPS planning 1.0, counterfactual-axiom 0.95, n-ary relations 1.0,
  set-algebra 1.0, tabular SQL 1.0, multi-turn state 1.0, cyclic@1M 1.0, bipolar-quant 0.82 (>=float, 16x mem)
- Substrate-LM: VQ-VAE codebook HP (util 1.0, recon 0.897, same-cat atom-share 17x cross), T5C-A1 differentiability GATE HP
  (gradients flow through complex FHRR bind/unbind -> Tier-5c training unblocked)
- Negative rescues: PP-155 per-strength-shard 1.0/0.996 (rescued the stall); APS conformal (honest MID, subsumed)
- Honest negative: T5b in-weights fact-transmission (5 attempts) -- needs trained Flamingo cross-attention (GPU-days R&D)

## What I need
1. **A fresh batch of cheap-decisive CPU anchors** (<5 min each). The CPU lane drains any batch in minutes (pure-numpy cells run
   in seconds), so I burn through anchors fast. Cheap, falsifiable, capability/verification/product-layer probes are ideal.
2. **OR explicit go-ahead on the big R&D** that's now gated-GREEN but needs GPU-days + user sign-off:
   - Tier-5b trained Flamingo gated cross-attention (T5C-A1 confirms differentiability; this is the in-weights fact-transmission)
   - Substrate-only-LM Anchor 2 (TinyStories 10M LM) + Anchor 3 (mid-layer hybrid)
   - Tier-5c Phase B/C (single-layer -> multi-family on Pythia/Qwen, continued-training recovery)
   These are the v2.0 critical path but GPU-days-to-weeks; flagging rather than auto-starting under the cost-control rules.

Structural note: shipped experiments/_stream.py (incremental checkpoint helper) + a hard rule -- long cells now persist/resume
(after wiki-1m/f1/legal lost data). Cheap cells stay all-or-nothing (fine at <1 min).
