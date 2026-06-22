# Research (Director) Work Queue — durable anti-freeze queue

**Purpose:** mechanical anti-freeze infrastructure. Each cycle dequeues top item. Never end a cycle passive while queue is non-empty + USER hasn't directed standby. Per Fix #12 (freeze-pattern-harden discipline, 2026-06-22).

**How to use:**
- Each cycle: review queue; execute top 1-3 items in main thread or spawn background
- When item completes: mark DONE; remove or move to "Recently shipped"
- When new follow-up emerges: append to appropriate tier
- If queue depletes: refill from backlog / open loops / surfaced findings

**Anti-freeze checks (every cycle wake):**
- [ ] Did I ship at least ONE substantive thing this cycle? (spawn / edit / atom / commit / decision)
- [ ] If "standing by" — is the queue genuinely empty + USER directed standby? (If not, FREEZE pattern → execute top item)
- [ ] Did I update this queue with new follow-ups surfaced this cycle?

---

## TIER 1: In-flight (do not re-spawn; reactive on landing)

- [BG] n4 k-WTA-VQ cell (biological sparsity; brain-drill recommendation) — remote_cpu smoke + full
- [BG] Path A V_C=4096 frontier cell — remote_cpu full (~7.5h projected)
- [BG] WikiText-103 ingest cell (n6) — remote_cpu smoke
- [BG] arxiv abstracts ingest cell (n7) — remote_cpu smoke
- [BG] ConceptNet ingest cell (n8) — remote_cpu queued (OPEN-C unlock if 75x holds at full)
- [BG] text8 retry1 — accidental full on remote (~4.5h ETA)
- [BG] SMH (Sparse Modern Hopfield) cell — Path C revival #1; using pipeline-template first field-test
- [BG] HumanEval Anchor-1 cell — Qwen-1.5B stdlib-class split (substrate-as-LLM-tool pattern)
- [BG] SVAMP mechanism redesign research drill (selector-bias / multi-hop / synthetic WK training)
- [BG] Phase B chronological window 2 cert-trail enrichment (skunkworks Store-write; serialize-after)

## TIER 2: Queued (next bandwidth; ready to fire)

- [QUEUE] **Phase D cert_ledger extension** — project portfolio_state PP-rows + HP-cells into cert_ledger with own atom-id namespace; window-2 finding revealed pre-CERT-NNN-convention cert events not in cell-atom Store (COMP-DEPTH cliff / WAVES 1-4 / k-gram-XOR / theta-burst / abduction-kernel); Director-to-USER scope decision before authoring
- [QUEUE] SVAMP Candidate D — joint pair+op training (~3-4hr cell-author + new training-data generation; rescue after Candidate A HARD_FAILed; SCHEMA-VET needed)
- [QUEUE] Back-port proper uniform-fallback to N1/N2 family cells (Fix #6 audit; non-urgent; old cells OK in full)
- [QUEUE] MEMORY.md curation (overweight 31.6KB+; CURRENT STATE block stale; compress + update)
- [QUEUE] Brain-drill #2: CLS continual learning (CLS theory + sleep replay + synaptic consolidation; ~30-60min research)
- [QUEUE] Brain-drill #3: multi-hop / working memory (prefrontal + entorhinal + planning circuits; informs U1 v2 extension to 3+ hops)
- [QUEUE] Phase A reconcile-cert-N mismatch audit (595 vs 583 chain_grade classification-logic; 12-atom delta)
- [QUEUE] Director cross-check on Path A V_C=4096 land (4-layer when it returns from remote)
- [QUEUE] Director cross-check on n4 / n6 / n7 / n8 lands (4-layer per cell)
- [QUEUE] U1 v2 with entity-name staging (FB15k-237 + entity2text.txt → unlock OPEN-C frozen-encoder baseline as planned pre-STANDSTILL; ConceptNet n8 partially handles)

## TIER 3: Composition cells (gated on Tier 1 outcomes)

- [GATED] n4 + MKN composition cell (if n4 lands HARD_PASS OR MIDDLE_BAND)
- [GATED] n4 + Path A V_C=4096 + MKN triple-composition (if both individual cells closure-direction-correct)
- [GATED] SMH + projection layer scaling (if SMH HARD_PASS; scale to higher M)
- [GATED] U1 v2 multi-hop 3+ chains (extend 2-hop chain-grade to longer chains; multi-hop ceiling test)

## TIER 4: Backlog (long-horizon; no immediate gating)

- [BACKLOG] Generation / sampling from substrate (substrate-only beyond next-token; ~brain-drill scope first)
- [BACKLOG] Continual-learning at scale validation (27x no-forget MM exists; full-scale test)
- [BACKLOG] Cross-corpus transfer cells (ingest WikiText → eval text8 perplexity; or ConceptNet → FB15k-237 transfer)
- [BACKLOG] Full Wikipedia ingest at scale (multi-million facts; tests substrate at scale)
- [BACKLOG] PubMed / arxiv full-papers / math-stack ingest (Tier 2+ ingest breadth)
- [BACKLOG] Math text-LM (after NL bigram-gap closure per math/code scope drill)
- [BACKLOG] Code text-LM (after NL + math; requires StarCoder/CodeBERT encoder swap)

## Recently shipped this autonomous arc (rolling; ≤10)

- 2026-06-22 SVAMP-A weight sweep HARD_FAIL (max acc=0.3611 across 5 weights; control valid; selector-bias is deeper than scalar-prior can fix; Candidate D next per drill)
- 2026-06-22 Fix #12 freeze-pattern-harden infrastructure (durable work queue + discipline atom + memory pointer; commits be8850d0 + 17bea59)
- 2026-06-22 Fix #6 zero-D-overlap audit (10 cells; new cells fixed; old N1/N2 family epsilon-floor smoke-vulnerable; commit 10790983)
- 2026-06-22 SMH cell dispatched via Fix #11 pipeline-template first field-test (Path C revival #1)
- 2026-06-22 HumanEval Anchor-1 cell-author bounded ~3hr (Qwen-1.5B integration)
- 2026-06-22 SVAMP mechanism redesign research drill (post WK-exhaustion)
- 2026-06-22 Phase B chronological window 2 dispatched
- 2026-06-22 ConceptNet n8 cell shipped (OPEN-C unlock candidate; smoke 75x substrate vs frozen-encoder)
- 2026-06-22 WikiText n6 + arxiv n7 ingest cells shipped (smoke dispatched)
- 2026-06-22 Path A V_C=4096 cell shipped (frontier; 7.5h projected wall)

— Research (Director). Queue maintained per Fix #12 freeze-pattern-harden discipline.
