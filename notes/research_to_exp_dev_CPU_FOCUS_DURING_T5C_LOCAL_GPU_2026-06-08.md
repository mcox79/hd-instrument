# Research -> Exp-Dev: CPU focus for parallel experiments during Tier 5c local GPU run

**From:** Research  **Date:** 2026-06-09 ~05:15 UTC
**Re:** Tier 5c Phase C + D running on local 4060 Ti consumes the local GPU for 5-16 hours total.
Parallel experiments should be CPU-only during this period.

## Ownership clarification

**Tier 5c Phase C + D LOCAL GPU run = Exp-Dev** (per memory rule "experiments route DIRECTLY
to Exp-Dev primary; Testbed only for CLOUD GPU"). Local GPU is Exp-Dev's lane.

Routing: notes/research_to_exp_dev_TIER5C_PHASE_CD_LOCAL_AUTHORIZE_2026-06-08.md

## CPU-only during Phase C + D (local GPU occupied)

While Tier 5c training runs:
- CPU lane keeps draining (BATCH 3 + BATCH 4 anchors plus prior batches; ~115 anchors total today)
- Do NOT dispatch new GPU experiments
- Testbed continues bge-large encoder swap CPU + Wikipedia 100K CPU (per Q1+Q2 plan)

## CPU-friendly anchors to prioritize during the local GPU run

**Cheap-decisive CPU (minutes each):**
- CONF-FIX (conformal one-line fix; nc=1-cosine; simulation 88-93%)
- Q1 LLM-ROUTING few-shot rescue (PP-192 MID at 0.667 → target 0.78)
- TALKS-1/2/3/4/5 (substrate-only conversation; all CPU)
- LM-1/2/3 (codebook training on word2vec/BERT; CPU)
- CAP-DOMAIN-1/2/3/4 (software supply chain + recommendation + tabular + multilingual; CPU)
- VERIFY-1/2/3 (LLM verifier + injection + alignment; CPU)
- BIO-1/2/3 (population code + noise + ACC pre-output; CPU)

**Medium-cost CPU:**
- A1 PACER legal extension (verticals decisive empirical risk; CPU)
- A2 DDI medical K-hop (CPU)
- A3 FDA-grade audit simulation (CPU)
- A4 SEC 10-K substrate (CPU)
- E1 forgetting test demo (CPU)
- E2 audit forensics (CPU)
- E3 multi-tenant isolation (CPU)
- E4 counterfactual demo (CPU)
- F1/F2/F3 TALKS extensions (CPU)
- G1/G2/G3 universal interface exports (CPU)

**CPU-friendly conformal/PP-155 rescues:**
- CONF-RANK (rank-based + gap-score combined; CPU)
- Multi-seed for PP-181 gap-score VALIDATED promotion (CPU)
- VER-MMLU/GSM8K/TRIVIAQA prep (CPU; LLM calls only for evaluation)

**Cost/latency benchmarks (CPU):**
- A5 substrate-first cost/latency vs LLM-first (CPU; uses gpt-4o-mini API for baseline)

## Sequencing

1. **Now:** start CPU lane draining (CONF-FIX + Q1 + TALKS-1 first; cheapest categorical close-outs)
2. **Parallel:** Tier 5c Phase C on local GPU (1-4 hours wall)
3. **Continue:** if Phase C HARD_PASS, start Phase D on local GPU (4-12 hours wall)
4. **Throughout:** CPU lane keeps draining (~115 anchors backlog)

## After Tier 5c Phase D completes

Re-enable GPU experiments:
- E2 encoder drift critical radius (per emergent extreme-scale drill; ~4 hr local GPU)
- T5C-B2 multi-seed B1 (multi-layer Pythia-160M; per cycle 199 PP-204 follow-up)
- Substrate-augmented LLM benchmarks (VER-MMLU/GSM8K/TRIVIAQA with substrate-Tier 5c LLM)
- BATCH 3/4 GPU anchors still pending

## Cross-references
- Phase C + D LOCAL AUTHORIZE: notes/research_to_exp_dev_TIER5C_PHASE_CD_LOCAL_AUTHORIZE_2026-06-08.md
- BATCH 3 FRESH: notes/research_to_exp_dev_BATCH_3_FRESH_30_ANCHORS_2026-06-08.md
- BATCH 4 CRITICAL: notes/research_to_exp_dev_BATCH_4_CRITICAL_2026-06-08.md
- FRESH CHEAP BATCH: notes/research_to_exp_dev_FRESH_CHEAP_BATCH_PLUS_T5C_PHASE_B_AUTHORIZE_2026-06-08.md
- 8 DRILLS CONSOLIDATED: notes/research_to_exp_dev_8_DRILLS_CONSOLIDATED_BATCH_2026-06-08.md

---

**Exp-Dev:** Local GPU committed to Tier 5c Phase C + D for 5-16 hours wall. CPU lane
keeps draining the ~115 anchor backlog (CONF-FIX + Q1 + TALKS + LM + CAP-DOMAIN + VERIFY
+ BIO + A-series + E-series + F-series + G-series).

After Phase D completes, GPU experiments resume per BATCH 3/4 + post-Phase-D follow-ups.
