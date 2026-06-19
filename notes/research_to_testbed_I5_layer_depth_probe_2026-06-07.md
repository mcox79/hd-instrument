# Research -> Testbed: Cell I5 layer-depth probe -- needs LoRA adapter (Testbed's lane)

**From:** Research session
**To:** Testbed
**Inform:** Exp-Dev + Orchestrator + User
**Date:** 2026-06-07 ~11:30
**Re:** exp_dev_to_research_batchI_status_2026-06-07.md (I5 BLOCKED)
**Subject:** I5 layer-depth RP probe needs CELL-5 LoRA adapter. You have it at data/cell5_results/lora_adapter_epochs1/. Please run + report.

---

## Cell I5: Layer-depth RP probe (base vs CELL-5 LoRA at L=2/6/10/15)

Drill B (LoRA 3x deep) identified this as the cheap decisive test (~3 min) to resolve Hyp-A vs Hyp-C on WHY LoRA hurts retrieval.

Exp-Dev BLOCKED: doesn't have the LoRA adapter on their runner. **You have it at data/cell5_results/lora_adapter_epochs1/.**

### Test design

For Llama-3.2-1B BASE and BASE+CELL-5-LoRA, measure top-5-RP retrieval at layers L=2, L=6, L=10, L=15 on SQuAD-v2 (your Q4 methodology):

1. Load Llama-3.2-1B BASE
2. Extract top-5-RP at L=2, 6, 10, 15 (no LoRA)
3. Merge CELL-5 LoRA adapter
4. Extract top-5-RP at L=2, 6, 10, 15 (with LoRA)
5. Compute degradation per layer

### Pre-reg (per Drill B)

- **HP (confirms Hyp-A SFT decoder-semantics drift):** degradation top-heavy -- upper layers (L=10, L=15) substantially worse than lower (L=2, L=6)
- **HF (confirms Hyp-C LoRA r=16 rank perturbation):** degradation uniform across all layers

### Strategic value

- HP outcome: CELL-3 distillation should target L=2-6 (less SFT-disrupted); informs production extraction encoder
- HF outcome: LoRA r=16 specifically problematic; CELL-3 may revisit LoRA at lower rank

Either outcome informs CELL-3 dispatch design.

### Cost

~3 min local 4060 Ti (per your Q4 pattern); $0.

---

**END.**

**Testbed:** Cell I5 ~3 min CPU/GPU; you have the LoRA adapter. Pre-reg in body. Either outcome informs CELL-3.

**Exp-Dev:** Cell I5 routed to Testbed; results land at data/exp_<anchor>/metrics.json.

**User:** I5 routed to Testbed (had the adapter). ~3 min wall.
