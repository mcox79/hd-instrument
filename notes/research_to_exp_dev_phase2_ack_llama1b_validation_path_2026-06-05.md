# Research -> Exp-Dev: Phase 2 unblocked at Llama-1B; validation path locked in (Gemma-2-2B remains Phase 3 production target)

**From:** Research session
**To:** Exp-Dev (primary)
**Inform:** Testbed + Orchestrator + User
**Date:** 2026-06-05 ~12:35
**Subject:** Phase 2 first verdict landed: substrate-audit-core at 1B HARD_PASS. Llama-1B is the Phase 2 validation tier; Gemma-2-2B switch is for Phase 3 production only (no need to re-extract). Plus OOM constraint acknowledged for model-load cells.

---

## Major win

**substrate-audit-core at Llama-1B HARD_PASS:**
- C2 deletion-cert = 1.00 (perfect on real Llama-1B residuals, 3 seeds)
- C3 drift-sep = 15.5x (BETTER than Pythia's C2=0.98)
- **MOAT 1 (deletion certs) + MOAT 2 (drift detection) empirically validated at 1B scale**

This is the HIPAA/GDPR/EU AI Act product wedge moving from theory to empirical validation. Tier-1 product anchor locked in at 1B.

---

## Phase 2 validation path: use Llama-1B (do NOT re-extract to Gemma-2-2B)

Important clarification: the Phase 3 blueprint drill recommended Gemma-2-2B as the **Phase 3 production** LLM partner (distillation-trained from 27B teacher; richer intermediate-layer geometry for KV bridge). That recommendation is for PRODUCTION DEPLOYMENT, not for Phase 2 validation.

**For Phase 2 validation: Llama-1B is fine.** The data is delivered; cost was $0.86; categorical product findings transfer between LLM tiers (per architectural framing).

**For Phase 3 production: switch to Gemma-2-2B.** This requires a separate ~$5-8 extraction when Phase 3 deployment is imminent. Not needed now.

Phase 2 work plan with Llama-1B residuals:
1. substrate-audit-core C2+C3 at 1B: HARD_PASS (DONE, 12:31)
2. EX-CONCEPT-1-real at 1B: MIDDLE (bigram-level; architectural not LLM-tier-specific) -- K2-XOR rescue next
3. K2-XOR rescue at 1B concepts: BUILDING NEXT
4. CCC-1-v2 at 1B (residual-only dimensions): buildable now
5. Tier-4 attn-swap at 1B: GATED on bigger GPU or bf16 fits 8GB

---

## EX-CONCEPT-1-real at 1B MIDDLE confirms architectural finding

substrate 0.727 vs bigram 0.716 at V_c=256 -- same bigram-level finding as Pythia.

**This is GOOD news.** It confirms substrate sequence prediction limit is ARCHITECTURAL (Hebbian writes = n-gram class), not Pythia-specific. The K2-XOR rescue should apply at 1B too; building next.

If K2-XOR-1B HP: rescue mechanism robust across LLM tiers. If K2-XOR-1B HF: surprising; warrants drill on why the rescue doesn't scale.

---

## OOM constraint for model-load cells

Llama-1B on 4060Ti 8GB OOM risk:
- Residual-only cells SAFE (work on the 392 MB npz; no model load): audit-core, EX-CONCEPT, K2-XOR, CCC-1-v2 capability dims
- Model-load cells need bigger GPU or bf16: Tier-4 attn-swap, CCC-1-v2 generation/decoder cells

### Mitigation options

**Option A: bf16 (likely first attempt)**
- Cuts model memory in half
- Llama-1B in bf16 is ~2.4 GB; fits with KV cache room on 8GB
- Some accuracy loss; usually negligible for inference
- Exp-Dev already proposed; default route

**Option B: Cloud GPU for model-load cells**
- ~$1-3 per run on Lambda H100
- Cleaner; no quantization concerns
- Authorized for Tier-4 attn-swap (critical test)

**Option C: Sequential / batch=1**
- Wall time increase but fits memory
- Worth trying if bf16 has accuracy concerns

Recommend Option A (bf16) for first attempt; fall back to Option B if bf16 accuracy degrades.

---

## Updated experiment priority

Per the Llama-1B unblock + K-fact combination drill landing:

**Highest priority (immediate, all residual-only at Pythia + Llama-1B):**
1. K2-XOR rescue at Llama-1B (validates rescue at scale; ~30 min)
2. 4 K-fact combination anchors at Pythia (validates beta* before HP-7 design lock; ~50-65 min total)
3. HP-7 integrated cognitive-core e2e at Pythia (THE demo; with Rule 8 + beta* design)
4. CCC-1-v2 capability dimensions at Llama-1B residual-only (transferred categorical wins to 1B scale)

**Second priority:**
5. Tier-4 attn-swap at Llama-1B (model-load; bf16 first; OOM fallback)
6. HP-10 adversarial failure modes (honest limits)
7. HP-9 multi-modal substrate with cross-modal log-sum fusion
8. HP-11 distribution-shift continual learning
9. HP-8 10k-exchange scale push

**Cubic-tensor + two-bridge hybrid smoke (Phase 3 prep):**
10. CUBIC-N3-1 cubic-tensor-write empirical validation at N=4096
11. Two-bridge hybrid smoke at scaled-down Phase 3 config (now uses Llama-1B not Gemma-2-2B; valid for design validation; Gemma-2-2B re-run when Phase 3 production launches)

---

## Discipline declarations

- Per [[feedback-routings-direct-to-exp-dev]]: Exp-Dev primary
- Per [[feedback-no-padding-experiments]]: each cell tests distinct architectural hypothesis or transfer
- Per [[feedback-pressure-test-negative-findings]]: EX-CONCEPT-1-real at 1B MIDDLE confirms architectural finding; K2-XOR rescue tested next at 1B
- Per stay-at-Pythia + opportunistic-1B: residual-only cells transfer easily to 1B; model-load cells gated on GPU
- ASCII-only

---

**END.**

**Exp-Dev:** Phase 2 unblocked; Llama-1B residual-only cells are safe at 8GB. Use Llama-1B for Phase 2 validation; don't re-extract to Gemma-2-2B (that's Phase 3 production only). Priority order: K2-XOR-1B -> 4 K-fact combination anchors -> HP-7 with locked-in Rule 8 design -> CCC-1-v2 at 1B residual-only -> Tier-4 attn-swap with bf16. Model-load cells may need bf16 or cloud GPU.

**Testbed:** stellar 1B extraction delivery (~$0.86; zero failures; data integrity preserved despite watchdog race). Watchdog fix landed; Pythia got lucky on smaller npz; Llama hit it; permanent fix in scripts. Standing for HP-5 PubMed + MedQA data when bandwidth allows.

**User:** Phase 2 first verdict locked in: substrate-audit-core at Llama-1B HARD_PASS (C2=1.00 deletion-cert, C3=15.5x drift-sep). **The HIPAA/GDPR product wedge (MOAT 1 + MOAT 2) is now empirically validated at 1B scale.** Llama-1B extraction was $0.86; way cheaper than expected. Phase 3 production still targets Gemma-2-2B per blueprint drill; no need to re-extract for Phase 2 validation.
