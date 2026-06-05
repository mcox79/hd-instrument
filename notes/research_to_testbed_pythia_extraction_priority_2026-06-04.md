# Research -> Testbed: Pythia-160M residual extraction priority elevation

**From:** Research session
**To:** Testbed (primary)
**Inform:** Exp-Dev + Orchestrator + User
**Date:** 2026-06-04
**Subject:** Pythia-160M residual extraction now blocks 2 priority experiments. Priority elevation request.

---

## Strategic context

User priority focus 2026-06-04: substrate-intrinsic-LLM-training (Tier 6 Phase D + Tier 4 Hopfield-attention substitution + Stage A training-speed full).

**Pythia-160M residual extraction is now the SHARED DEPENDENCY for:**
1. EX-CONCEPT-1 REAL (concept-level VQ training)
2. EX-OPTION-C-W_proj (residual injection bridge via B8)

Plus Tier 4 attention substitution test could potentially use Pythia loaded on runner (without explicit extraction; Exp-Dev confirming feasibility).

---

## Request

**Can Testbed run Pythia-160M residual extraction NOW, independent of the Llama v7 hang situation?**

Per Exp-Dev's earlier note (20:35):
- Pythia-160M LOADS on the runner (`exp_phase05_v1_algorithm1_debug_pythia160m_v1` ran with gate-log)
- Pythia is SMALLER + INDEPENDENT of the hung Llama v6/v7 (different model; unlikely to hit same I/O / pathological doc stall)
- Extraction should be FAST + RELIABLE relative to Llama

Specifically:
- Run Pythia-160M last-layer residual extraction
- Save as npz (same format as Llama Hyperprobe outputs)
- ~5-10k residuals sufficient for EX-CONCEPT-1 VQ codebook training (concept-level granularity << token-level)
- Same audit-fix protocol as Llama v7 (smoke + no-silent-synthetic; from your cornerstone audit fixes)

---

## What this unblocks

1. **EX-CONCEPT-1 REAL** — substrate-side build by Exp-Dev: VQ Pythia residuals into concept IDs → train substrate on concept-ID sequences → measure concept-level perplexity. P_deflated=0.35 per drill; substrate's entry point to concept-level language.

2. **EX-OPTION-C-W_proj** — substrate stores Pythia residuals via B8 logit-space encoding → single linear W_proj maps substrate output to residual space → inject at inference. P_deflated=0.25. Tests substrate-LLM intrinsic coupling at small-LLM scale.

3. **Tier 4 Hopfield-attention substitution backup path** — if v7 keeps blocking, can build Tier 4 against Pythia-160M without GPU contention with v7 (Pythia is much smaller).

---

## Why this is higher-priority than waiting for Llama v7 fix

- Pythia is smaller + faster + more reliable
- 2-3 priority experiments depend on Pythia residuals
- v7 fix may take hours; Pythia extraction may take ~10-30 minutes
- C2 + C3 cornerstone audit primitives are CLOSED-FORM algebraic; substrate-audit-core at Pythia-160M is a valid Tier-1 product claim (per my earlier note on cornerstone Q4)

---

## What I'm NOT asking

- NOT asking to redirect Llama v7 work (continue diagnosing if you have bandwidth)
- NOT asking for cloud compute (Pythia fits remote)
- NOT asking for full 100k docs (5-10k is sufficient for VQ + substrate-audit-core needs)

---

## What user needs to authorize

User asked: "tell me what I need to do." User decision needed:

1. **Confirm Pythia-160M extraction is HIGHER priority than v7 diagnostic** — recommend YES (faster path to substrate-LLM empirical anchors)
2. **Authorize remote 4060 Ti for Pythia extraction** — needed if v7 occupies remote (might require killing v7 first)

If user authorizes:
- Testbed runs Pythia extraction (~10-30 min wall)
- Exp-Dev runs EX-CONCEPT-1 + substrate-audit-core on REAL Pythia residuals
- Tier 4 attention substitution becomes feasible at Pythia-160M scale

---

## Discipline declarations

- Per [[feedback-routings-direct-to-exp-dev]]: Testbed primary on model extraction; Exp-Dev for substrate-side experiments
- Per [[feedback-cloud-only-when-absolutely-necessary]]: Pythia-160M fits remote 4060 Ti; no cloud needed
- Per [[feedback-small-scale-first-methodology]]: Pythia-160M is rung above substrate-class; smaller than Llama; right next step
- ASCII-only

---

**END.**

**Testbed:** Pythia-160M residual extraction priority elevated. 2-3 priority experiments depend on it. Pythia is faster + more reliable than Llama. Standing for user direction on (1) Pythia priority confirmation and (2) GPU authorization (if v7 needs killing).

**Standing for user direction on the 2 authorizations above.**
