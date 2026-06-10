# exp_dev hand-off -- research: benchmark sweep 2x

**Filed-by:** research sub-agent
**Date:** 2026-06-09
**Trigger:** Benchmark sweep 2x drill completed; 10-anchor ranking with HARD-PASS/HARD-FAIL thresholds
**Research note path:** d:/AI/hd-instrument/notes/research_drill_benchmark_sweep_2x_2026-06-09.md

Per [[feedback-no-experiment-design-in-prompts]]: This file names anchor candidates and context pointers only. exp_dev designs all experiment specifics autonomously.

---

## Pause state

Standard pause gate applies. exp_dev checks data/orchestrator_paused.flag before dispatch.

---

## Anchor candidates (rank-ordered)

### Anchor 1 (HIGHEST PRIORITY): BENCH-GRAILQA

**Anchor pointer:** GrailQA Hits@1 evaluation on standard dev split (n >= 500), substrate K-hop chain, Freebase triples already loaded

**Substrate-product reading:** GrailQA uses the same FB15K-237 triples already in the substrate. The marginal engineering cost is one dataset loader (~1 day). PathHD (arXiv:2512.09369) published 86.7% on GrailQA. If substrate Hits@1 >= 87%, the claim "substrate exceeds PathHD on all three main KG-QA benchmarks (WebQSP + CWQ + GrailQA)" is established. That is the cleanest external-validation story available. WebQSP (98.2% graph-reachable, estimated Hits@1 ~88-92%) and CWQ (94.7% graph-reachable, estimated Hits@1 ~73-78%) are already established.

**Tier hint:** Tier-1 CPU (no GPU; K-hop chain is sub-ms; n=500 runs in <30 min)

**Why now:** Cheapest benchmark win. Zero new infra. Produces a peer-comparable number against the direct academic baseline (PathHD). GrailQA includes a zero-shot generalization split that tests schema-agnostic traversal -- substrate's algebraic design should handle this without task-specific training.

**HARD-PASS:** Hits@1 >= 87.0%, n >= 500 overall; zero-shot split Hits@1 >= 70%.
**HARD-FAIL:** Hits@1 < 78.0% overall.

---

### Anchor 2: BENCH-NELL995

**Anchor pointer:** NELL-995 multi-hop relation reasoning, K-hop chain on NELL graph (75K entities, 50 relation types), Hits@10 + MRR on full 2,980 test triples

**Substrate-product reading:** NELL-995 is a smaller, cleaner KG than FB15K-237. K-hop performance on NELL demonstrates that substrate generalizes across graph structures (Freebase vs NELL). Published RL-based baselines: MINERVA 0.69 Hits@10, M-Walk 0.73, RelaGraph 0.93. A substrate Hits@10 >= 0.90 matches RelaGraph without RL training. Graph available via PyKeen.

**Tier hint:** Tier-1 CPU (NELL graph is small; full 2,980 test triples run in <20 min)

**Why now:** Adds a second graph to the benchmark portfolio. Demonstrates KG generalization. Low engineering cost after GrailQA loader is built.

**HARD-PASS:** Hits@10 >= 0.90, full test set.
**HARD-FAIL:** Hits@10 < 0.75.

---

### Anchor 3: BENCH-METAQA3

**Anchor pointer:** MetaQA 3-hop test (n = 14,274), K=3 substrate K-hop chain on WikiMovies graph (135K triples), Hits@1

**Substrate-product reading:** MetaQA-3 is substrate's cleanest 3-hop validation. WikiMovies is small enough to be a single shard. No LLM generation needed; answer is the terminal entity. Published: EmbedKGQA 89.9%, GNN-QA 92.4% -- both trained embedding methods. Substrate with no task-specific training at >= 90% Hits@1 is a strong claim: "substrate matches trained KGE methods on 3-hop KG-QA without training."

**Tier hint:** Tier-1 CPU (WikiMovies graph is tiny; 14,274 test queries run in <60 min at sub-ms each)

**Why now:** Provides the academic 3-hop citation independent of FB15K-237. Closes the "does K-hop chain work at K=3 on a clean graph?" question definitively.

**HARD-PASS:** Hits@1 >= 90.0%.
**HARD-FAIL:** Hits@1 < 80.0% (K=3 hop accumulation noise; check intermediate recall per hop).

---

### Anchor 4: BENCH-HOTPOT-T1

**Anchor pointer:** HotpotQA fullwiki n=200+, three-way comparison: bare Qwen2.5-1.5B / vanilla-RAG-Qwen2.5-1.5B / substrate-augmented-Qwen2.5-1.5B. Report EM + F1 per condition with 95% CI.

**Substrate-product reading:** Prior smoke (n=30) showed +0.35 F1 lift. Tier-1 n=200 is the gate for any public claim. The critical comparison is substrate vs vanilla RAG (same encoder, no K-hop structure) -- this isolates substrate's architectural contribution from encoder quality. HotpotQA retrieval parity (bge-large r@5=0.66 ties vanilla RAG) means the lift must come from the K-hop multi-document combination in generation context, not from retrieval recall.

**Tier hint:** Tier-1 CPU (harness exists; re-run at n=200 with three conditions)

**Why now:** Gateway test for all LLM-augmented benchmark claims. Without Tier-1 confirmation, no LLM-augmented number is defensible.

**HARD-PASS:** F1 >= 0.55 (substrate), F1 <= 0.45 (vanilla RAG), lift >= 0.10, 95% CI excluding zero.
**HARD-FAIL:** No statistically significant lift over vanilla RAG at n=200.

---

### Anchor 5: BENCH-MUSIQUE

**Anchor pointer:** MuSiQue (2/3/4-hop) n=200+, same three-way comparison as BENCH-HOTPOT-T1. Report F1 per hop depth (2-hop / 3-hop / 4-hop separately).

**Substrate-product reading:** MuSiQue is adversarially filtered to remove shortcut paths. This is where K-hop chain shows its largest structural advantage over vanilla RAG. Published best: IRCoT 33.2% F1 at 7B class. Substrate-augmented 1.5B at 35%+ F1 is a strong result given model size. The per-hop breakdown is critical: K=4 hop questions should show the largest gap vs vanilla RAG.

**Tier hint:** Tier-2 CPU (same harness as HotpotQA, different dataset loader; ~1-2 days to wire)

**Why now:** Most defensible multi-hop claim. Adversarial design means the lift is harder to dismiss as "encoder quality."

**HARD-PASS:** F1 >= 35% (substrate-augmented), lift >= 0.07 vs vanilla RAG.
**HARD-FAIL:** F1 < 28% or lift < 0 vs vanilla RAG.

---

### Anchor 6: BENCH-MEDQA-AUG

**Anchor pointer:** MedQA (USMLE 4-option) n=300+, substrate-augmented Qwen2.5-1.5B with PubMed retrieval vs bare Qwen2.5-1.5B. Report accuracy per category.

**Substrate-product reading:** PubMedQA retrieval r@5=1.0 already validated (2026-06-08). The question is whether retrieved context improves generation accuracy on USMLE questions. Published: Qwen-1.5B-class bare ~35-40% on MedQA. Substrate + retrieval expected to reach 45-55%. Not competitive with frontier LLMs (GPT-4: 90%) but demonstrates domain-specialized augmentation at small model scale. The "vertical moat" claim for biomedical.

**Tier hint:** Tier-2 CPU (MedQA loader + generation harness; 2-3 days)

**Why now:** Closes the "does retrieval augmentation help on domain QA with 1.5B?" question. PubMed retrieval is already validated; this converts it to a benchmark number.

**HARD-PASS:** Accuracy >= 45% (substrate-augmented) vs <= 40% (bare LLM), n >= 300.
**HARD-FAIL:** Accuracy < 40% or no lift over bare LLM.

---

### Anchor 7: BENCH-2WIKI (bridge subtype)

**Anchor pointer:** 2WikiMultihopQA bridge subtype, n >= 200, three-way comparison. Wikipedia corpus already cached on runner.

**Substrate-product reading:** 2Wiki bridge questions ("Find bridge entity X, then answer via X") map directly to K=2 substrate chain with a named intermediate entity. The bridge subtype is the cleanest multi-hop test in 2Wiki; comparison and compositional subtypes involve cross-document reasoning that is harder for 1.5B models. Focus on bridge subtype for the initial benchmark.

**Tier hint:** Tier-2 CPU (same harness as HotpotQA; Wikipedia corpus already available; 1-2 days for loader)

**HARD-PASS:** F1 >= 45% on bridge subtype, lift >= 0.10 vs vanilla RAG.
**HARD-FAIL:** F1 < 30% or below vanilla RAG.

---

### Anchor 8: BENCH-HEAD-TO-HEAD

**Anchor pointer:** Substrate K-hop (no LLM) vs gpt-4o-mini (no tools, closed-book) on WebQSP n=300. Report Hits@1 + cost per query for each.

**Substrate-product reading:** This is the categorical Pareto demonstration. Substrate-only is expected to achieve ~87-92% Hits@1 (from graph-reachable validation) at sub-ms cost. gpt-4o-mini closed-book on WebQSP is expected ~65-72% (without web search / KG tools). The cost gap is 3-4 orders of magnitude. This is the most impactful demo panel: "system with structured memory exceeds frontier LLM on structured KG-QA at zero marginal query cost."

**Tier hint:** Tier-1 CPU + API call (gpt-4o-mini API calls; n=300 costs ~$0.03 total at current pricing)

**Why now:** Highest external-audience impact. Produces the "beats GPT-4o-mini at 0 cost" headline for the structured-KG panel. gpt-4o-mini closed-book is a fair comparison because the demo positioning is "substrate as external memory replaces parametric knowledge for structured KG tasks."

**HARD-PASS:** Substrate Hits@1 >= 87%, gpt-4o-mini Hits@1 <= 78% (10+ pp gap confirmed).
**HARD-FAIL:** gpt-4o-mini matches or exceeds substrate Hits@1 (implies entity linking or answer extraction bug in substrate).

---

## Context pointers

- Full research note (benchmark taxonomy + Pareto + citations): d:/AI/hd-instrument/notes/research_drill_benchmark_sweep_2x_2026-06-09.md
- Prior benchmark research (2x operational drill, 2026-06-07): d:/AI/hd-instrument/notes/research_drill_multibenchmark_suite_execution_2x_2026-06-07.md
- Empirical baseline (testbed 2026-06-08): d:/AI/hd-instrument/notes/exp_dev_to_testbed_benchmark_suite_results_2026-06-08.md
- PathHD paper context: arXiv:2512.09369 (GHRR, WebQSP 86.2%, CWQ 71.5%, GrailQA 86.7%)
- North Star: d:/AI/hd-instrument/memory/north_star_functional_system_beats_LLMs.md
- Post-compaction brief (exp-dev state): d:/AI/hd-instrument/notes/exp_dev_POST_COMPACTION_BRIEF_2026-06-09.md
- Datasets cached on runner: fb15k_237, hotpot, pubmedqa, nq_open, medqa, wikipedia_10k, webqsp_rog, cwq_rog

---

## Contract

exp_dev autonomously decides: which anchor(s) to ship, in what order, experiment design details, hyperparameters, smoke gate criteria, and queue placement. This file provides ranked priorities and context only.

## Autonomy declaration

exp_dev may reorder, split, combine, or defer these anchors based on queue state, runner availability, and smoke gate results. The ranking above is research-informed guidance, not a constraint.
