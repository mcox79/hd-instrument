# exp_dev hand-off -- research: domain-specific KG distillation into substrate

**Filed:** 2026-06-04 by research sub-agent (2x depth drill cycle).

**Trigger:** Research drill on domain-specific knowledge distillation completed.
Source note: `notes/research_drill_domain_specific_knowledge_distillation_substrate_2x_2026-06-04.md`

**Pause state:** CHECK `data/orchestrator_paused.flag` before dispatching. If flag present, queue this hand-off; do not dispatch.

**Per [[feedback-no-experiment-design-in-prompts]]:** This hand-off names ANCHORS + POINTERS only. exp_dev designs ALL of: N, M, K, seed count, threshold bands, queue choice (Tier A/B/C), anchor name, ETA, smoke profile, FULL profile. Research does NOT specify numerical parameters.

---

## Strategic context

The research drill found that:
1. Path Y (direct KG triple binding) is cost-dominant for medical and financial domains where structured KG infrastructure (UMLS/SNOMED, XBRL) already covers 60-85% of domain facts.
2. Deletion certs are a categorical product differentiator -- no fine-tuned LLM can comply with GDPR/HIPAA right-to-erasure mandates (OpenAI fined EUR 15M Dec 2024; EDPB 2026 enforcement active).
3. The smallest viable empirical test is a medical pilot: 10k PubMed abstracts + UMLS triples, PubMedQA/MedQA-USMLE-slice evaluation.
4. Distillation cost for medical domain: ~$18k one-time; financial: ~$2,300. Both are within single-sprint engineering budget.

---

## Anchor candidates (rank-ordered; exp_dev picks across queues)

### 1. Medical domain substrate pilot -- PubMed/UMLS triple binding + PubMedQA evaluation
- Anchor pointer: research note Section "SMALLEST VIABLE EMPIRICAL TESTS -- Medical"
- Substrate-product reading: confirms whether direct KG triple binding into N=8192 substrate
  achieves retrievable accuracy on a domain Q&A benchmark; validates the core product claim
  that substrate retrieval competes with RAG-augmented LLM at fraction of cost.
- Tier hint: Local CPU (binding 500k triples; PubMedQA evaluation; no GPU required)
- Why now: cheapest, clearest decisive test; UMLS data is free; PubMedQA is open benchmark;
  answer directly informs all four domain verticals' product viability.

### 2. Financial XBRL triple binding + FinQA evaluation
- Anchor pointer: research note Section "SMALLEST VIABLE EMPIRICAL TESTS -- Financial"
- Substrate-product reading: XBRL filings are already structured; no LLM extraction needed
  for 80-85% of facts; this is the cheapest distillation path across all four domains.
  FinQA numerical reasoning tests whether substrate retrieval supports multi-step queries.
- Tier hint: Local CPU (schema-driven extraction; binding trivially cheap)
- Why now: cheapest overall ($2,300 for full domain; pilot is sub-$20 compute);
  clean controlled test since no LLM extraction variability in structured fraction.

### 3. Deletion cert round-trip benchmark on domain-scale triple store
- Anchor pointer: research note Section "AUDITABLE DELETION + CONTINUAL UPDATE DIFFERENTIATORS"
- Substrate-product reading: measures per-fact deletion cert latency and correctness at
  domain scale (100k-1M triples); establishes the performance envelope for the product's
  primary regulatory differentiator vs domain-fine-tuned LLMs.
- Tier hint: Local CPU or Remote CPU (depends on triple count; timing-sensitive measurement)
- Why now: EU AI Act enforcement and EDPB 2026 priority make this the near-term product wedge;
  empirical latency numbers are required to make a credible compliance claim.

### 4. Continual update rate benchmark -- triple insertion throughput at N=8192
- Anchor pointer: research note Section "DISTILLATION PATH COMPARISON -- Continual update cost"
- Substrate-product reading: validates the algebraic claim of $0/fact update vs LLM fine-tune;
  measures actual throughput (triples/second) and capacity saturation point for the medical
  domain volume (1B facts claim vs 1.5*N=12,288 reliable patterns per domain slot).
- Tier hint: Local CPU (pure binding throughput; no GPU needed)
- Why now: capacity limit (12,288 patterns at N=8192 per domain) is the key quantitative
  question for whether hierarchical aggregation scales to production domain volumes.

---

## Context pointers

- Research note: `d:/AI/hd-instrument/notes/research_drill_domain_specific_knowledge_distillation_substrate_2x_2026-06-04.md`
- Benchmark references: PubMedQA (open), MedQA-USMLE-slice (open), FinQA (open)
- Data sources: UMLS (free research license), PubMed (open), SEC EDGAR XBRL (public)
- Prior substrate capacity measurements: `notes/substrate_capability_map.md` (Cap 2 row)
- Deletion cert algebraic validation: check `notes/capability_implication_consolidated_substrate_2026-06-04_end_of_day.md`

---

## Contract

exp_dev is authorized to:
- Design smoke + FULL anchors for any of the 4 candidates above
- Choose queue routing (local/CPU/GPU) per the Tier A/B/C policy
- Set N, seed count, threshold bands independently
- File pre-reg HP/MID/HF bands per [[feedback-envelope-expansion-fail-bands]]

exp_dev is NOT authorized to:
- Modify cap_map rows (verdict_handler owns)
- Commit research findings as cap_map decisions
- Pre-frame expected outcomes (per [[feedback-no-preframe-batch-all-pass]])

## Autonomy declaration

exp_dev has full autonomy over experiment design within the anchor pointers above.
The research note provides algebraic context and benchmark baselines; exp_dev translates
these into concrete runnable anchors per its own internal discipline. No numerical parameters
from this hand-off are binding contracts.
