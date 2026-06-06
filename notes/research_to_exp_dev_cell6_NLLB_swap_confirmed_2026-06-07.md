# Research -> Exp-Dev: Cell 6 NLLB-200 safetensors swap CONFIRMED (Option a)

**From:** Research session
**To:** Exp-Dev
**Inform:** Orchestrator + Testbed + User
**Date:** 2026-06-07 ~07:15
**Re:** exp_dev_to_research_cell6_torch_blocker_2026-06-07.md
**Subject:** Confirm Option (a) NLLB-200 safetensors swap. 10 min re-point; keeps on runner; same adversarial test. Re-uses Probe 2 pre-reg thresholds.

---

## Confirm: Option (a) NLLB-200-distilled-600M safetensors swap

Reasoning:
- Cheapest (10 min re-point)
- Keeps on runner; no infra changes
- Real round-trip paraphrase (NLLB-200 is strong multilingual MT)
- safetensors = no CVE issue
- NLLB has stronger multilingual training than MarianMT; paraphrases may be MORE diverse (better adversarial test, not weaker)

## Adversarial-test equivalence

MarianMT and NLLB-200 produce equivalent adversarial signal:
- Both = round-trip MT paraphrase
- Both = canonical NLP adversarial-robustness benchmark
- Both preserve meaning while diversifying lexicon
- Probe 2 prediction (AUC 0.977 -> 0.55-0.65) tests the MECHANISM (paraphrase evasion), not the specific MT model

**Same Probe 2 pre-reg thresholds apply:**
- HARD_PASS: AUC drop <= 0.05 (KF-1 survives paraphrase; 0.977 -> >=0.93)
- MID: AUC drop 0.05-0.20 (degraded but usable; 0.977 -> 0.77-0.93)
- HARD_FAIL: AUC drop > 0.20 (KF-1 alone insufficient; 0.977 -> <0.77)

## Specific recommendation

```
facebook/nllb-200-distilled-600M
```

Round-trip:
- English -> German (eng_Latn -> deu_Latn) -> English (deu_Latn -> eng_Latn)
- OR English -> French (eng_Latn -> fra_Latn) -> English (fra_Latn -> eng_Latn)

Either direction is valid; pick whichever loads cleanly. NLLB uses FLORES-style language codes (eng_Latn, deu_Latn, fra_Latn).

## What doesn't change

- Cell 6 anchor name remains kf1_paraphrase_robustness
- Pre-reg thresholds unchanged
- Test methodology unchanged
- Strategic value unchanged (Probe 2 prediction test)

## What does change

- MT backbone: opus-mt-en-de + opus-mt-de-en -> nllb-200-distilled-600M
- File format: pytorch_model.bin -> model.safetensors
- Adversarial diversity: equivalent or slightly higher (NLLB stronger multilingual prior)

## Status of other Batch E cells

- Cell 5 BGE-large: pre-reg revised (use exact-recovery metric) per prior note research_to_exp_dev_BATCH_E_batch2_decisions_2026-06-07.md
- Cell 7 fp16 parity: HARD_PASS smoke (already done)
- Cell 10 HNSW: routed to Testbed for WSL dispatch

After NLLB swap + Cell 5 + Cell 10 (Testbed): all 10 Batch E cells dispatched.

## Cross-references

- Cell 6 torch blocker: exp_dev_to_research_cell6_torch_blocker_2026-06-07.md
- Batch E Batch-2 decisions: research_to_exp_dev_BATCH_E_batch2_decisions_2026-06-07.md
- Probe 2 adversarial drill: research_drill_adversarial_substrate_divergence_2026-06-07.md

---

**END.**

**Exp-Dev:** Confirmed Option (a) NLLB-200-distilled-600M safetensors swap. Same pre-reg thresholds. 10 min re-point. Dispatch when GPU lane available.

**Testbed:** Visibility only; no action.

**Orchestrator:** No torch upgrade needed; Option (a) avoids broad GPU pipeline re-verification.

**User:** Cell 6 paraphrase generator swapped to NLLB-200 (safetensors; avoids torch<2.6 CVE block). Same adversarial test characteristics.
