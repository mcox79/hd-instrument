# exp_dev hand-off — research: substrate-memory + small-LLM-frontend HYBRID architecture (2x DEEP)

**Filed:** 2026-06-11 by research:opus.
**Trigger:** 2x DEEP drill on hybrid architecture delivered actionable pilot recommendation at < 100 USD / 48-hour cost.
**Source research note:** `notes/research_drill_substrate_memory_llm_frontend_hybrid_2x_2026-06-11.md`
**Pause state:** Check `data/orchestrator_paused.flag` before queueing.

**Per [[feedback-no-experiment-design-in-prompts]]**: this hand-off names ANCHORS + POINTERS only. exp_dev designs ALL of: N_cal, intent-class count, KB shard count, seed count, threshold bands, queue choice, full profile. Research does NOT specify numerical parameters beyond what the research note already includes as PRE-REGISTERED HARD-PASS / HARD-FAIL bands.

---

## What the research drill closes / opens

CLOSES: methodology for substrate vs 70B head-to-head (drill 18) PLUS production deployment patterns (drill 17 hybrid_architecture_deployment) PLUS conformal calibration (drill 8) PLUS RAG-backend (drill 17). The synthesis is: substrate-memory back-end + 8B-class LLM front-end + conformal-margin routing as the production architecture.

OPENS: a concrete 48-hour pilot at < 100 USD that decides commercial viability. Pre-registered HARD-PASS bands on 6 axes (accuracy-catchup, cost, latency, memory, conformal-coverage, determinism) plus HONEST-NEGATIVE on a 7th (open-domain QA we lose).

---

## Anchor candidates (rank-ordered)

### Anchor 1 — HYBRID-1 conformal-margin routing harness on existing kb25k

- **Anchor pointer:** `notes/research_drill_substrate_memory_llm_frontend_hybrid_2x_2026-06-11.md` Section (b) Stage 1 + Section (c) Axis E.
- **Substrate-product reading:** Vovk split-conformal threshold tau on substrate cleanup-margin gives finite-sample 90pct conditional-correctness guarantee on substrate-routed share. This is the novel-synthesis math angle (Axis E HARD-PASS coverage in [0.88, 0.92] at alpha=0.10).
- **Tier hint:** Tier-A CPU (kb25k already validated; this is a calibration + routing-fraction sweep on existing infrastructure).
- **Why now:** cheapest decisive test; required for any subsequent LLM-comparison pilot to be meaningful; runs in CPU-hours not GPU-hours.

### Anchor 2 — HYBRID-2 8B-LLM frontend with substrate-RAG context (single L4 GPU)

- **Anchor pointer:** same research note Section (b) Stage 2 + Section (c) Axes A/B/C/D.
- **Substrate-product reading:** Llama-3.1-8B-Instruct via vLLM, fp16, batch=1, receives substrate-retrieved top-k facts as context. Measure accuracy on closed-KB factual recall + 20-intent classification + JSON-extraction; measure p50/p99 TTFT; measure NVML J/inference; measure peak VRAM.
- **Tier hint:** Tier-B GPU (single L4 / A10G / T4; ~4-8 GPU-hours).
- **Why now:** validates the 8B-front-end thesis. Lit-grounded prediction: 7B+RAG hits less-than-7.5pct hallucination on structured output (arXiv:2404.08189).

### Anchor 3 — HYBRID-3 hybrid end-to-end with routing threshold tau

- **Anchor pointer:** same research note Section (b) Stage 4 + cost model in Section (e).
- **Substrate-product reading:** Pipeline = query in -> substrate retrieves + computes m -> if m >= tau (from Anchor 1) return substrate; else call 8B-LLM with substrate top-k context. Measure end-to-end accuracy, p99 latency, cost-per-query, routing fraction.
- **Tier hint:** Tier-B GPU + CPU (composes Anchors 1 + 2; single end-to-end run).
- **Why now:** the decision-grade comparison. Must complete after Anchors 1 + 2 land.

### Anchor 4 — HYBRID-4 Llama-3.3-70B baseline (cloud API or rented 8xH100)

- **Anchor pointer:** same research note Section (b) Stage 3.
- **Substrate-product reading:** baseline for the comparison axes. Run via Groq or Together API at ~0.79 USD per 1M output tokens (estimated total ~5 USD for the benchmark sweep) OR rented 8xH100 at ~12 USD/hr for 1 hr. Same benchmark suite as Anchor 2.
- **Tier hint:** Tier-C cloud API (cheapest path; no infrastructure provisioning).
- **Why now:** required denominator for the 8-15x cost-ratio and accuracy-catchup claims.

### Anchor 5 — HYBRID-5 (optional, post-pilot) every-layer substrate-attention integration

- **Anchor pointer:** PP-217 (every-layer substrate-attention -28pct ppl validated across 4 model scales) + research note Section (d).
- **Substrate-product reading:** v1.1 architectural destination -- deeper integration where substrate becomes a continuous enrichment layer of LLM internal representations. NOT in scope for the 48-hour commercial pilot; track for follow-on after Anchors 1-4 ship.
- **Tier hint:** Tier-A GPU (multi-day training run).
- **Why now:** track only; do not queue until Anchors 1-4 verdict.

---

## Context pointers (no inline summaries)

- `notes/research_drill_substrate_memory_llm_frontend_hybrid_2x_2026-06-11.md` (THIS drill, source)
- `notes/research_drill_hybrid_architecture_deployment_2x_2026-06-11.md` (Patterns 1-5 decision tree)
- `notes/research_drill_substrate_vs_larger_llm_methodology_2x_2026-06-11.md` (4-axis normalization methodology)
- `notes/research_STRATEGIC_REFRAME_substrate_around_LLM_2026-06-09.md` (commercial framing context)
- Memory: `substrate_LLM_boundary_decomposition_2026-06-10.md` (boundary inventory)
- Memory: `pp225_fact_scaling_correction_2026-06-10.md` (kb25k = 0.996 genuine baseline)
- Memory: `substrate_v32_engineered_wrapper_2026-06-11.md` (substrate-backend primitives)

---

## Contract

Per [[feedback-no-experiment-design-in-prompts]]: research has named anchors + pointers only. exp_dev decides:
- N_cal sweep grid for tau calibration (Anchor 1)
- intent-class count and KB-shard partition (Anchors 1-3)
- single-seed vs multi-seed for the pilot run
- which cloud provider (Groq vs Together vs rented hardware) and the precise hardware tier per anchor
- smoke-then-FULL gating per anchor
- full latency / cost / energy / coverage / accuracy measurement harness wiring

## Autonomy declaration

exp_dev has full design autonomy over per-anchor experimental parameters within the PRE-REGISTERED HARD-PASS / HARD-FAIL bands listed in the source research note. Research does not modify those bands without a follow-on drill. Verdict events route back to verdict_handler in the normal pipeline.
