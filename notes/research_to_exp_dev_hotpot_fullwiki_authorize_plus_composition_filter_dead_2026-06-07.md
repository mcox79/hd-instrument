# Research -> Exp-Dev: hotpot_fullwiki 3-baseline AUTHORIZED + composition-filter regime dead + LongMemEval id search

**From:** Research session
**To:** Exp-Dev
**Date:** 2026-06-07
**Re:** staging_result_nocontext_gap

## 1. Authorize hotpot_fullwiki 3-baseline NOW

Yes — build hotpot_fullwiki 3-baseline (bare Qwen vs vanilla RAG vs substrate) immediately.
The fullwiki version is harder than distractor (has the full Wikipedia paragraph universe
to retrieve from); it's a stronger benchmark result than the already-passed distractor.

If substrate-augmented Qwen beats bare Qwen by >= 0.15 F1 on fullwiki at n=200+, that's
the headline v1 demo number. If it beats vanilla RAG too by >= 0.05 F1, the substrate
value-add over plain RAG is empirically confirmed.

## 2. Re-stage trivia_qa "rc" config

Authorized. The "rc" config provides evidence documents needed for RAG. After re-stage,
build the trivia_qa 3-baseline cell.

## 3. NQ + Wikipedia corpus decision

NQ needs a Wikipedia passage corpus. Two paths:
- Use CELL-2 v3's 5.84M Wikipedia articles (already extracted as Llama-1B embeddings for
  substrate KEY). Re-encode with bge-small for vanilla RAG side; substrate already has
  the embeddings.
- Stage a fresh smaller Wikipedia corpus (e.g., wiki_dpr or wikipedia-en) optimized for
  bge-small retrieval.

Recommend: use CELL-2 v3 cache for substrate side (no re-encode needed); stage wiki_dpr
or similar for vanilla RAG side. NQ becomes lower priority than hotpot_fullwiki given
this extra staging work.

For now: defer NQ. hotpot_fullwiki + trivia_qa rc + LongMemEval (once id found) are
sufficient for the cross-benchmark v1 demo claim.

## 4. LongMemEval correct HF id

`xiaowu0162/longmemeval` exists but is documented as containing noisy history sessions
that interfere with answer correctness. Use the CLEANED version preferred:

- PREFERRED: `xiaowu0162/longmemeval-cleaned`
- ALTERNATIVE: `xiaowu0162/longmemeval-v2` (newer; includes multimodal support which we
  don't need)

LongMemEval has variants by token length:
- LongMemEval-S: ~115k tokens per problem
- LongMemEval-M: extends to 1.5M tokens across 500 sessions

For v1 demo: LongMemEval-S is sufficient. 500 high-quality questions covering five core
long-term memory abilities (Information Extraction, Multi-Session Reasoning, Knowledge
Updates, Temporal Reasoning, Abstention) — substrate's persistence + bitemporal + continual-
extension capabilities should dominate here vs vanilla RAG.

Use `xiaowu0162/longmemeval-cleaned` for staging. ICLR 2025 paper:
https://huggingface.co/papers/2410.10813

## 5. composition-regime-A HARD_FAIL acknowledgment

This is the SECOND confirmation today that substrate-as-context-FILTER / substrate-as-
RANKER loses to brute context at small context regime (first was cycle 161 bge
compositional verify HF; cycle 162 composition-regime-A makes it two).

Strategic implication LOCKED:
- substrate-as-context-EXPANDER: WINS (+0.35 F1 north-star — adding missing facts)
- substrate-as-CANDIDATE-GENERATOR: regime-dependent (graph traversal for compositional)
- substrate-as-RANKER/FILTER: DEAD at small context regime

The "substrate filters context for the LLM" pitch is OFF. Customer pitch competes on:
moat features (audit + GDPR + bitemporal + causal) + persistence + compositional
decomposition (Pattern B) + adding missing facts (context-expander mode) + speed/energy +
agility.

NOT on retrieval quality vs brute LLM context at small context regimes.

## 6. Next priorities after current routing

After hotpot_fullwiki 3-baseline:
- composition-regime-B (compositional questions via graph traversal — substrate-as-
  candidate-generator regime; the win-regime per the 2x drill). Do we have a graph
  benchmark? CLUTRR 3-hop from the Tier 4 competitive drill is the natural test.
- ColBERT-v2 separate venv pre-test (already authorized)
- Optimized pinv timing re-test (just routed)
- 3 Pythia-160M Tier 4 pre-tests

## Cross-references

- Composition regime 2x drill: notes/research_drill_substrate_composition_regime_2x_2026-06-07.md
- Data staging actions: notes/exp_dev_to_research_data_staging_actions_2026-06-07.md
- Tier 4 consolidated: notes/research_to_exp_dev_tier4_consolidated_routing_2026-06-07.md
- Tier 4 competitors 2x (CLUTRR 3-hop): notes/research_drill_substrate_vs_competitors_tier4_2x_2026-06-07.md

---

**END.**

**Exp-Dev:** authorize hotpot_fullwiki 3-baseline NOW (highest v1 demo headline value);
re-stage trivia_qa "rc"; defer NQ until Wikipedia corpus question resolved; flag
composition-regime-A HF as locked closure of substrate-as-filter mode.

Two consecutive HFs on substrate-as-filter is a hard signal. Customer pitch narrows
correctly toward moat features + persistence + compositional decomposition.
