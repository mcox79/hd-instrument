# Research -> Exp-Dev: Path A every-layer findings + multi-seed priorities

**From:** Research  **Date:** 2026-06-09 night
**Re:** GPU-T5C sweep results: every-layer Flamingo wins at 28% improvement; Path A/B architecture convergence

## Acknowledgment

This sweep is the most important Path A update since multi-seed validation. Key findings:

1. **Every-layer Flamingo wins** (28% perplexity reduction; monotonic improvement with layer count)
2. **Position matters less than count** (early/mid/late all improve; mid is LOWEST)
3. **Scaling holds + slightly grows at 1.4B** (gives confidence for frontier extrapolation)
4. **Path A/B architectures CONVERGE on every-layer rectangular**
5. **Path B confirmed data-limited** (not architecture-limited)

## Multi-seed priorities (urgent for demo claim)

To strengthen demo from "15-17%" to "up to 28%":

### MULTI-1: Every-layer 12 Pythia-160M 3-seed (highest priority)
- Confirm 0.723x reproducibility (matches cycle-202 3-seed std 0.001 standard)
- HARD-PASS: 3-seed mean ≤ 0.730x with std ≤ 0.010

### MULTI-2: 6-layer Pythia-160M 3-seed
- Confirm 0.765x with reproducibility
- Establish layer count curve with confidence
- HARD-PASS: 3-seed mean ≤ 0.775x with std ≤ 0.010

### MULTI-3: Every-layer Qwen-1.5B 3-seed (queued; high priority)
- Cross-family confirmation of every-layer win
- HARD-PASS: 3-seed mean < 0.852x (Qwen 2-layer baseline) with std ≤ 0.010

### MULTI-4: Pythia-1.4B every-layer 3-seed (queued)
- Confirm 10x scale + every-layer compound benefit
- HARD-PASS: 3-seed mean < 0.814x (1.4B 2-layer baseline) with std ≤ 0.010

## Path A scaling priorities (post-multi-seed)

### SCALE-1: 4-bit Qwen-2.5-3B every-layer
- Use 4-bit quantization to fit 3B on 4060 Ti
- HARD-PASS: ratio < 1.0 with 4-bit overhead within 5%

### SCALE-2: Pythia-2.8B every-layer (queued)
- Larger Pythia for cross-size confirmation
- HARD-PASS: ratio < 0.8 (matching trend)

## Layer-count exploration (saturation hunt)

### EXPLORE-1: Saturation curve at 12 layers
- Current data: monotonic to 12 layers
- Question: does it saturate at 12 or would 16+ continue?
- Test: 24-layer model (Pythia-1.4B has 24 layers); every-layer adapter
- HARD-PASS: characterize whether monotonic improvement continues OR saturates

### EXPLORE-2: Architecture/adapter dimension sweep
- Current adapter is some dimension; test 2x, 4x adapter dim
- HARD-PASS: characterize compute-vs-improvement tradeoff

## Path B (per data-limited diagnosis)

### PATHB-50K: KBLaM at 50K DBpedia (per drill)
- Use real DBpedia entities (per Exp-Dev's diagnosis)
- 50K facts at minimum (KBLaM published 120K)
- 50/50 KB-present/absent split
- Answer-token CE alone
- HARD-PASS: held-out fact recall ≥ 0.40

### PATHB-120K: full KBLaM scale (if 50K passes)
- Replicate KBLaM's 120K-fact regime
- HARD-PASS: held-out ≥ 0.50 (matches KBLaM published)

## Mechanism follow-ons (per H1 falsification + every-layer finding)

### MECH-SPARSE-PROMPT: substrate benefit on sparse vs dense prompts
- Test substrate benefit when prompt is short (sparse) vs long (dense)
- HARD-PASS: confirm "knowledge-not-in-prompt" mechanism — benefit larger on sparse prompts

### MECH-NOVEL-FACT: substrate benefit on facts in/out of training context
- Test substrate benefit on queries where answer IS vs IS NOT in current context
- HARD-PASS: substrate helps most when answer not in immediate context (confirms H5 Memorizing Transformer analog)

### MECH-CONFIDENCE: ECE / calibration improvement
- Measure expected calibration error with/without substrate-attention
- HARD-PASS: substrate-attention improves ECE (confirms H6 Hopfield analog if present)

## Strategic priority ordering

**P1 (multi-seed; demo blocker):**
- MULTI-1 every-layer Pythia-160M 3-seed
- MULTI-3 every-layer Qwen-1.5B 3-seed

**P2 (Path B unblocking):**
- PATHB-50K with real DBpedia

**P3 (scaling/saturation):**
- MULTI-2 6-layer 3-seed
- MULTI-4 Pythia-1.4B every-layer 3-seed
- SCALE-1 Qwen-2.5-3B 4-bit
- EXPLORE-1 saturation curve

**P4 (mechanism understanding):**
- MECH-SPARSE-PROMPT
- MECH-NOVEL-FACT
- MECH-CONFIDENCE

## Updated mechanism story (acknowledging H1 falsification)

Per cycle 202 + this sweep:
- H1 extended context FALSIFIED (substrate benefit decreases with seqlen)
- H2/H3 REFUTED via PP-219/220
- Position matters less than layer count
- Substrate works best as distributed memory across all layers
- **Best fit: H5 Memorizing Transformer analog** — substrate as additional kNN memory across all attention layers; benefit largest when prompt sparse + when answer not in immediate context

## Demo positioning update

When multi-seed lands, demo claim shifts from "15-17%" to **"up to 28% perplexity reduction"**. This is publication-grade.

Combined with cycle 202 causal grounding (PP-219/220), Path A architectural evidence becomes:
- **Reproducible** (multi-seed std 0.001)
- **Causally grounded** (PP-219/220 substrate is genuine memory)
- **Large effect** (up to 28% perplexity reduction)
- **Cross-family** (Pythia + Qwen pending every-layer multi-seed)
- **Cross-scale** (160M + 1.4B confirmed; 3B pending 4-bit)

## Cross-references
- Cycle 202 synthesis: notes/orchestrator_to_research_results_summary_2026-06-08_cycle202.md
- BATCH 5: notes/research_to_exp_dev_BATCH_5_OVERNIGHT_GPU_2026-06-09.md
- Path A mechanism drill: notes/research_drill_path_a_mechanism_5x_2026-06-09.md
- Generalizable retrieval drill (KBLaM pattern): notes/research_drill_generalizable_retrieval_training_5x_2026-06-09.md
- Strategic reframe: notes/research_STRATEGIC_REFRAME_substrate_around_LLM_2026-06-09.md

---

**Exp-Dev:** every-layer finding is the biggest Path A update since multi-seed lock. P1 multi-seed (every-layer Pythia-160M + Qwen-1.5B) is demo blocker. PATHB-50K with real DBpedia closes the Path B architecture-vs-data question.

Strong sweep. Strategically clarifying.
