# Research -> Exp-Dev: Tier 5 Arch 8 (substrate-KV-cache) Pythia-160M MVE AUTHORIZED

**From:** Research session
**To:** Exp-Dev
**Date:** 2026-06-07
**Re:** Tier 5 substrate-intrinsic LLM 3x drill output. Per user "very promising" +
blanket Exp-Dev authorization.

## Authorize the cheapest Tier 5 gate: Arch 8 substrate-KV-cache replacement on Pythia-160M

This is the SINGLE cheapest pre-test that gates the entire Tier 5 program. $30-80
compute cost. ~2-3 days engineering. Frozen Pythia-160M; substrate plumbed into attention
KV cache; no LLM retraining required.

Why elegant: substrate becomes the persistent attention cache. Pre-trained LLM behavior
is preserved (frozen weights); substrate's persistence + audit + compositional structure
become accessible via the LLM's existing attention mechanism. Captures much of Tier 5's
value with Tier 4's cost profile.

## Method (per drill's MVE spec)

- Pythia-160M frozen weights
- Replace attention KV cache with substrate bipolar storage (Pattern A or Pattern B)
- Test on small QA task where attention cache content matters (multi-turn QA; document QA)
- Measure: cross-entropy / answer quality vs baseline (standard KV cache); substrate
  retrieval quality from attention queries

HARD-PASS: substrate-KV-cache achieves >= 95% of baseline quality at meaningful cache
sizes (>= 512 tokens substrate-backed).

BORDER: 80-95% quality (partial validation; needs deeper investigation).

HARD-FAIL: < 80% quality (substrate-KV-cache approach is fundamentally lossy for
attention; Tier 5 via this path closed; Arch 7 dual-mode becomes the alternative).

Wall: 2-3 days engineering + $30-80 compute.

## Decision tree

HP: authorize Arch 7 dual-mode Pythia-160M MVE ($50-200) + start Arch 8 production path
analysis. Tier 5 program legitimized empirically.

HF: Tier 5 via Arch 8 is dead. Arch 7 MVE becomes the next gate ($50-200). If Arch 7
also HF, Tier 5 stays speculative; Tier 4 captures the practical value.

## Sequencing relative to other work

DO NOT DELAY Tier 4 v1.1 for this. Arch 8 MVE runs in PARALLEL with:
- Tier 4 Pythia-160M pre-tests (vocab injection + LoRA orthogonal stability + defrag
  consistency)
- Pattern B Mechanism 1 L2 normalization
- Sleep defrag scaling 3 pre-tests
- Perf bottlenecks v1.1 actions (speculative decoding + distilled encoder)

Arch 8 MVE is OPPORTUNISTIC long-term R&D. Tier 4 v1.1 stays the v1.1 customer-ship
priority.

## Customer pitch implications

Arch 8 HP: substrate-intrinsic LLM direction is empirically viable. Tier 4 v1.1 ships
first; Tier 5 Arch 8 becomes v1.5/v2.0 architecture upgrade.

Arch 8 HF: customer pitch unchanged. Tier 4 (text interface) is the production
architecture. Tier 5 stays as v3/v4 north-star (if ever).

## Cross-references

- Tier 5 substrate-intrinsic LLM 3x drill: notes/research_drill_tier5_substrate_intrinsic_llm_3x_2026-06-07.md
- Drill Exp-Dev handoff: notes/exp_dev_handoff_research_tier5_substrate_intrinsic_llm_2026-06-07.md
- Tier 4 consolidated routing: notes/research_to_exp_dev_tier4_consolidated_routing_2026-06-07.md
- Final-impl perf bottlenecks (substrate <1% bottleneck context): notes/research_drill_final_implementation_perf_bottlenecks_2x_2026-06-07.md

---

**END.**

**Exp-Dev:** authorize Arch 8 Pythia-160M MVE. $30-80 compute. 2-3 days. Cheapest gate
for the entire Tier 5 program. Apply HARD-PASS / BORDER / HARD-FAIL autonomously. File
verdict on completion. DO NOT delay Tier 4 v1.1 work for this.
