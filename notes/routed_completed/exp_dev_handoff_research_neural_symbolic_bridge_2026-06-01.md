# exp_dev hand-off -- research: neural-symbolic bridge

**Filed:** 2026-06-01 by research sub-agent.

**Trigger:** Research delivery on substrate as neural-symbolic bridge. Algebraic analysis identified 5 capability differentiators vs published neural-symbolic architectures (DeepProbLog, LTN, NSCL, LNN) and established concrete HARD-PASS / HARD-FAIL thresholds for algebraic verification. Pre-registered test protocol is directly exp-dev-actionable.

**Pause state:** check `data/orchestrator_paused.flag` before dispatching.

**Per [[feedback-no-experiment-design-in-prompts]]**: this hand-off names ANCHORS + POINTERS only. exp_dev designs ALL of: N, M, seeds, threshold bands, queue choice (Tier A/B/C), anchor name, ETA, smoke/FULL profiles. Orchestrator does NOT specify numerical parameters beyond what is structurally required for the question.

**Source note:** `notes/research_neural_symbolic_bridge_2026-06-01.md`

---

## Anchor candidates (rank-ordered)

### 1. Cross-mode query round-trip: rule-fire then similarity-ranked output

- **Anchor pointer:** Research note section 3.1 + section 7 (cheap decisive test). Query class A: symbolic rule application -> conclusion -> soft-Hopfield similarity ranking. HP2: Spearman rho > 0.80 between W-eigenspace distance and soft retrieval probability. HF3: rho < 0.30 -> modes decoupled, single-substrate claim false.
- **Substrate-product reading:** If confirmed, the compositionality audit API (P4) gains a native "rule-fire + ranked-similarity" query call with no external engine. This is the direct product feature. If HF3 fires, the symbolic and connectionist modes are computationally decoupled despite sharing W -- mixed-mode products require a wrapper layer.
- **Tier hint:** CPU smoke (N=4096, F=10-50 triples, K=5 rules, finite-temperature softmax retrieval). Pure algebraic; no GPU required. Should run in <60s.
- **Why now:** Algebraic verification is the cheapest decisive test. HP2/HF3 are pre-registered with quantitative thresholds. This anchor closes the "mixed-mode query" capability gap on cap_map.

### 2. Deletion certificate cascade to dependent inference

- **Anchor pointer:** Research note section 5 (C3) + HP3/HF2. After active repulsion of stored triple T, query that would have retrieved T through a rule chain should return P(T) < 0.05; nearest alternative triple T' should be returned. HF2: deletion leaves P(T) >= 0.05 within 5 Hopfield update steps -> deletion certificate claim false.
- **Substrate-product reading:** This is the technical basis for the "deletion certificate" killer feature. If HP3 passes, legal/compliance KG maintenance is native. If HF2 fires, the product cannot guarantee retraction of facts and the deletion certificate feature requires redesign.
- **Tier hint:** CPU smoke (N=4096, small F, measure P(T) at t=1,2,5 update steps post-repulsion). Very cheap.
- **Why now:** This is the most differentiated capability vs published neural-symbolic systems. None of DeepProbLog, LTN, NSCL, LNN implements direct attractor removal. First empirical test of this claim.

### 3. Symbolic rule-application accuracy at capacity boundary

- **Anchor pointer:** Research note section 8, HP1. Rule application P(correct) > 0.95 at F <= N/4, K rules <= N/4, N=4096. HF1: P < 0.70 at F <= N/8 -> algebraic bridge claim false.
- **Substrate-product reading:** HP1 is the PREREQUISITE for all other neural-symbolic claims. If rule application is unreliable within the predicted BSC capacity envelope, the entire bridge framing collapses. This must be verified before higher-order query classes.
- **Tier hint:** CPU, N=4096, sweep F in {10, 50, 100, N/8, N/4}, K in {5, 20}, measure P(correct rule fire). Pure algebraic, should run in <30s.
- **Why now:** Foundational prerequisite. De-risks the whole anchor family.

---

## Context pointers

- Source research note: `notes/research_neural_symbolic_bridge_2026-06-01.md`
- Prior multi-hop reasoning math: `notes/wave14e_multi_hop_reasoning_research.md` (hop ceiling formulas, cleanup-between-hops protocol)
- Prior hierarchical composition math: `notes/wave14e_hierarchical_composition_research.md` (Plate 1995 chunking, per-level cleanup)
- Killer features reference: `notes/` + MEMORY.md project_substrate_killer_features_2026-05-26.md entry
- SKAH-M class confirmation: MEMORY.md project_substrate_skahm_class_confirmed_2026-05-27.md entry

---

## Contract section

exp_dev MUST:
1. Check `data/orchestrator_paused.flag` before dispatching any anchor.
2. Pre-register HP/HF/MID bands before coding.
3. Verify the algebraic self-test per [[feedback-strategy-spec-formula-selftests]] for rule-fire formula.
4. Use ASCII-only in print()/verdict_msg per [[feedback-ascii-only-in-scripts]].
5. Post-ship REMOTE VERIFY (confirm queue entry exists after queue_add.sh).

## Autonomy declaration

exp_dev has full autonomy over: anchor naming, sweep grids, N selection, seed count, queue choice (Tier A/B/C), smoke vs FULL profile, timeout formula. The hand-off names the QUESTION and PRE-REGISTERED THRESHOLDS only. Do not ask for clarification on parameters -- decide and ship.

<!-- routing-completed: Acted-on 2026-06-01: handoff to Round 10 dispatch -->
