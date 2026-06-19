# Research note: Continuous exploration with trustworthy tracking -- system design (2x drill)

**Date:** 2026-06-04
**Trigger:** User correction -- exploring is what surfaced the most important new capabilities; want a system that keeps all information safe, tracks the most promising, drills them to maximize characterization, and periodically branches out. Sonnet drilling is cheap; the constraint is information management + prioritization.
**P_deflated methodology:** Deflate agent P estimates by 0.15-0.25; cap novel-synthesis P at 0.50.

---

## HEADLINE

The dominant failure mode at ~40 drills/day is not exploration cost -- it is INFORMATION LOSS via fragmentation, duplication, and silent drop. The right system is a three-layer architecture: (1) atomic lossless notes with git-versioned single source of truth (SSoT); (2) a living capability scorecard as the prioritization spine; (3) epsilon-greedy branching cadence with explicit branch slots. Implementation is 2-3 days on existing Markdown + git infrastructure -- no new database required if schema discipline is enforced.

---

## Cheap decisive test

Create one synthetic "drill loss" test:
- Write a fake research note at notes/TEST_drill_loss_probe.md with 3 findings containing unique technical terms.
- 48h later, grep for those specific technical terms across ALL notes/*.md files.
- PASS: all 3 are findable in <= 2 grep commands.
- FAIL: any finding is only "remembered" in a multi-paragraph summary not indexable by key term.

If FAIL: the current notes/ architecture is already losing information at scale and the system below is URGENT.

---

## Falsifiable predictions

### HARD-PASS thresholds (system working correctly)
- HP1: Any finding from the last 30 days is retrievable in <= 3 grep operations against notes/*.md with exact technical term match.
- HP2: The capability scorecard has <= 1 row that is stale (last drill > 7 days ago for an active axis).
- HP3: Branch slots are populated >= 5 days in advance (never empty at decision time).
- HP4: Zero duplicate drill findings -- defined as: two notes claiming the same algebraic result with different P estimates and no reconciliation note.

### HARD-FAIL thresholds (system broken)
- HF1: A capability axis tracked in the scorecard has ZERO pointer to the empirical anchor that founded it (finding is "floating" with no verifiable source).
- HF2: Two drill notes contradict each other and no reconciliation or hierarchy-of-evidence note exists.
- HF3: A high-P finding (P_deflated >= 0.40) older than 14 days has no follow-up experiment queued or explicitly deferred with reason.
- HF4: More than 20% of exp_dev_handoff_*.md files reference research notes that have no entry in the capability scorecard (disconnect between research pipeline and experiment pipeline).

---

## Sub-question synthesis

### (1) TRUSTWORTHY INFORMATION STORAGE

**Core finding (P_deflated = 0.70 for general principle; 0.50 for specific stack recommendation):**

The research data management literature (biorxiv 2024 233-lab survey, PKM-at-scale analyses, MADR 4.0) consistently converges on the same failure mode at the ~40-notes/day scale: fragmentation into un-linked silos with no retrieval path. The OECD AI Capability Indicators (finalized Nov 2024) and lab notebook best-practices literature both identify the same solution: structured atomic notes with explicit entity links.

**Recommended architecture for this program:**

Three layers, not one:

Layer A -- Atomic facts: each drill landing produces ONE fact file (notes/facts/fact_<topic>_<date>.md) with schema:
  - CLAIM: (one sentence, exactly)
  - P_deflated: (number)
  - LIT_ANCHOR: (citation)
  - CAPABILITY_ROW: (pointer to cap_map row)
  - EXPERIMENT_POINTER: (pointer to anchor that tested this, if any)
  - STATUS: (VALIDATED / PARTIAL / REFUTED / OPEN)

Layer B -- Capability profile pages: one page per capability axis (notes/cap_profile_<name>.md), aggregating facts from Layer A that bear on that axis. Updated per new fact arrival; append-only.

Layer C -- Living scorecard: notes/capability_scorecard.md -- ONE row per capability, columns: (Status | P_deflated | Last drill date | Next drill candidate | Product-narrative readiness | Open compositions). This is the ONLY file that needs daily editing.

**Why not a database?** For <= 200 capabilities, Markdown + git outperforms SQLite in a key metric: grep-searchability without a running service. The 233-lab survey (biorxiv 2024) found databases are abandoned when the lab cannot maintain them; plain-text survives context switches and agent restarts. Git provides the audit trail.

**Why not a vector store?** RAG is the right retrieval layer if note count exceeds ~5000 and the query is semantic rather than exact-term. At current scale, exact-term grep on structured notes is faster and lossless. RAG can be added later as Layer D over Layer A fact files.

**Calibrated P: 0.70 for "three-layer Markdown + git is sufficient at current scale"; calibration penalty applied for novelty of agent-mediated writes (no direct published precedent for agent-maintained fact files at this cadence).**

---

### (2) PROMISING-CAPABILITY TRACKING METHODOLOGY

**Core finding (P_deflated = 0.65):**

The MLflow / Wandb experiment-tracking literature (2024 State of Data+AI: 34% of ML engineering time lost to reproducing past results without structured tracking) and the OECD AI Capability Matrix literature (2024) converge on a common insight: the right tracking unit is the CAPABILITY ROW, not the experiment. Experiments serve capabilities; capabilities serve product claims.

**Recommended scorecard schema per capability row:**

```
| Cap ID | Name | Status | P_deflated | Algebraic anchor | Empirical anchor | Composition status | Product claim | Last drill | Next drill |
```

Status values: open / partial / synthesis-grade / validated / refuted (mapped to current cap_map notation).

Key discipline: the scorecard is updated IMMEDIATELY on each research delivery or verdict landing. Never lag by more than one session.

**Saturation detection per capability:**

A capability row is "drilling-saturated" when:
- (a) Three consecutive drills return P_deflated < 0.40 (matches research_field_advisor.py logic already implemented for fields), OR
- (b) The algebraic characterization has a closed-form derivation AND >= 2 independent empirical anchors in agreement.

At saturation, drilling budget shifts to COMPOSITION (what does this capability compose with?) rather than further characterization. This is the transition from exploitation within one axis to composition-space exploration.

**Calibrated P: 0.65 for scorecard methodology (standard ML practice); 0.50 for composition-matrix tracking component (novel-synthesis class -- no published precedent for multi-primitive composition tracking at this formalism).**

---

### (3) DEEP-DRILL CADENCE FOR PROMISING CAPABILITIES

**Core finding (P_deflated = 0.50):**

The sequential Bayesian experimental design literature (arxiv 2509.21734; arxiv 2107.12809) formalizes what domain researchers discover empirically: the right stopping rule is NOT a fixed threshold but an MDP framing -- stop when the expected marginal information gain of the next experiment falls below the opportunity cost of branching to a different axis.

For a cheap-drill program (Sonnet at near-zero marginal cost), the MDP reduces to a simple rule:
  - If last 3 drills on this axis each added a NEW fact to Layer A fact files: continue drilling this axis.
  - If last 3 drills only confirmed existing facts: PIVOT -- shift to composition drills or branch to new axis.

This is operationalized without the full MDP machinery: count new facts per drill batch. Zero new facts in 3 consecutive batches = saturation.

**Applied to current substrate capabilities:**

Capacity multiplicative composition (HP at 125k patterns): Algebraic derivation exists (AGS 1985); empirical HP confirmed. Saturation for CHARACTERIZATION drills is near. Recommended next: COMPOSITION drills -- which primitives compose multiplicatively with capacity scaling? Boundary characterization (alpha_c per codebook family). Product-narrative readiness drill. Do NOT continue drilling single-primitive capacity confirmation.

SQ2 multi-hop K=12 reasoning HP: Strong empirical anchor. Recommended next: boundary characterization (K=15, K=20 degradation; cliff location). Composition with capacity scaling (does hierarchical aggregation preserve multi-hop at K=12?). Do NOT continue drilling K=12 confirmation.

12 bio-primitives: Foundation, not saturation. The COMPOSITION MATRIX is the primary gap: 12-choose-2 = 66 pairwise compositions, how many have been tested? Untested compositions = highest expected information gain per drill.

**Calibrated P: 0.50 (cap applied; applying MDP optimal-stopping to a non-convex composition space with cheap exploration is novel-synthesis class).**

---

### (4) PERIODIC BRANCHING CADENCE

**Core finding (P_deflated = 0.60):**

The exploration-exploitation literature (Bayesian hierarchical active learning 2023; Cambridge Management and Organization Review) converges on epsilon-greedy as the robust practical baseline when: (a) exploration space is large and non-stationary, (b) exploitation payoff is uncertain, (c) cost of exploration is low. All three apply here.

**Recommended implementation:**

Epsilon-greedy with epsilon = 0.20: ~20% of drill dispatches go to unexplored or under-explored axes; ~80% go to highest-P current axes. At 40 drills/day, this is ~8 branching drills per day -- more aggressive than the current once-per-24-48h cadence, which is too conservative given cheap drilling.

**Structural enforcement:**

Branch slots MUST be NAMED IN ADVANCE in branch_schedule.md, not discovered post-hoc. At the start of each session: allocate 2 named branch slots from field-advisor scope-expansion list BEFORE dispatching any exploitation drills. This prevents the common failure where "branching" is always deferred to "after we finish the current axis."

**Axes NOT YET in current program coverage (identified from field-advisor + lit scan):**

1. Population genetics / Wright-Fisher: catastrophic forgetting ~ mutation+selection+drift dynamics; fixation probability gives forgetting rate baseline (Kimura neutral theory); Tier-1b in field-advisor.
2. Queueing theory / Little's law: memory access patterns map to M/M/1 queue models; throughput-vs-latency under load is directly product-relevant.
3. Percolation / critical phenomena: capacity cliffs are percolation-class phase transitions; universality class gives cliff sharpness prediction from parameters (Tier-1b, spin-glass + semiconductor parent).
4. Ergodic theory: substrate dynamics = ergodic system?; Birkhoff theorem gives batch-average / online-average equivalence conditions; determines when batch-trained substrate generalizes to online streaming.
5. Expander / Ramanujan graphs: pool retrieval = graph retrieval problem; spectral gap bounds give retrieval quality guarantees from graph structure (Tier-1b, network-science parent).

**Calibrated P: 0.60 for epsilon-greedy as correct structural model; 0.35-0.45 for any specific new axis being high-yield (all are speculative until first drill).**

---

### (5) CONCRETE SYSTEM DESIGN

**Recommended implementation for substrate research right now:**

**Component 1: Upgrade cap_map.md to capability_scorecard.md (1-2 hours)**
Add columns: "Last drill date" | "Next drill candidate" | "Composition status (X/66 pairs tested)" | "Product-narrative readiness (NOW / BLOCKED-by)".
Backfill from existing research notes timestamps. This is the highest-ROI single change.

**Component 2: notes/facts/ subdirectory with atomic fact files (2-3 hours initial; 10 min/batch ongoing)**
Create the facts/ subdirectory. Schema per Layer A above. Retro-file the 12 validated bio-primitives + capacity multiplicative HP + SQ2 multi-hop HP as fact files (approximately 14 files to start). Every subsequent drill batch: the research sub-agent writes one fact file per new finding before returning.

**Component 3: composition_matrix.md (1-2 hours initial; 5 min/batch ongoing)**
12x12 (or NxN) table. Columns and rows = primitive names. Cell values: TESTED (link to anchor) / PREDICTED-ADDITIVE / PREDICTED-MULTIPLICATIVE / UNTESTED / REFUTED. This is the primary "what to drill next" artifact for the composition exploitation phase. Mermaid visualization block for cluster detection.

**Component 4: branch_schedule.md (30 minutes initial; 5 min/session ongoing)**
Rolling 7-day forward list of named branch slots. Format:
  Date | Axis | Why (adjacency / scope-expansion / saturation-trigger) | Research note when done.
Pre-populate with 5 axes listed in (4) above.

**Component 5: research_decisions_<date>.md discipline upgrade (0 hours; schema change only)**
Add required field to every entry: CAPABILITY_ROW pointer + STATUS (ADDED_FACT / CONFIRMED_EXISTING / REFUTED / COMPOSITION_NEW). This connects the decision log to the scorecard.

**Tooling recommendation:**
Markdown + git is the correct stack at current scale. No SQLite needed until note count > 5000. Mermaid diagrams in composition_matrix.md for visualization (renders natively in GitHub). LLM-generated capability profile summaries (Layer B) are appropriate as a batched end-of-day operation by the research sub-agent, not inline per drill.

**Migration path from current state:**

Step 1 (Day 1, 2h): Add scorecard columns to cap_map.md. Backfill "last drill date."
Step 2 (Day 1-2, 3h): Create notes/facts/ schema. Retro-file ~14 founding fact files for validated capabilities.
Step 3 (Day 2, 2h): Create composition_matrix.md. Fill known-tested cells from existing research notes.
Step 4 (Day 2, 1h): Create branch_schedule.md with 5 named slots from field-advisor scope-expansion list.
Step 5 (Day 3+, ongoing): Each research delivery: one fact file per new finding + scorecard "last drill date" update + "next drill candidate" update. Estimated ongoing overhead: 10-15 min per drill batch.

**Total implementation cost: ~8-10 engineering hours initial. Ongoing: ~15 min per drill batch. Zero external dependencies.**

**Calibrated P for system working as designed: 0.70 (standard software engineering; main risk is discipline-drop under batch pressure, not technical failure). Apply [[feedback-closures-drop-under-batch-pressure]] -- the schema disciplines need PROT entries or structural enforcement in the research sub-agent role prompt to survive multi-trigger batches.**

---

## Cross-thread synthesis

The current system has the EXPLORATION layer working well (research_field_advisor.py, exp_dev_handoff_*.md flow, epsilon-greedy triggers A-F in research.md). The 40 drills/day output confirms this. What is missing is the CONSOLIDATION layer -- the feedback path from research findings back into a queryable prioritized structure that exp_dev and strategy sessions can read without re-reading 40 individual notes.

The three-layer architecture (facts / capability profiles / scorecard) IS the consolidation layer. It does NOT replace research notes -- it indexes them. Research notes remain the authoritative source; the fact files + scorecard are the query interface.

This maps directly to the Zettelkasten principle confirmed by PKM-at-scale analysis (dsebastien.net, 8000 notes / 64000 links study): the value of the system comes from LINKS, not note count. 40 unlinked notes/day is noise; 40 linked notes/day is a compounding knowledge base.

The composition_matrix.md converts "we know X and we know Y" into "we tested whether X and Y compose" -- which is the load-bearing question for the substrate's product narrative at the current stage.

Adjacent method dispatched (not dismissed): knowledge graph (entity-relationship database approach). For <= 500 entities, this is mathematically equivalent to the fact-file + scorecard approach but operationally heavier. Mermaid in composition_matrix.md gives the graph adjacency picture without requiring a full graph database service. Knowledge Object (KO) approach (arxiv 2603.17781 -- hash-addressed fact tuples at 252x lower cost vs in-context memory with 100% retrieval accuracy) is architecturally similar to the fact-file approach proposed here; validates the direction.

---

## Substrate-product implications

1. The system design is the substrate research program's own product methodology. Implementing it demonstrates that the research pipeline self-manages at scale -- a credibility signal for the substrate product's own audit and information-management claims.

2. The composition_matrix.md is directly product-relevant: it is the audit trail of which capability compositions have been validated. When a product claim states "capabilities X + Y compose multiplicatively," the composition_matrix.md entry is the verifiable reference.

3. The branch_schedule.md naming approach surfaces 5 unexplored axes that could expand the substrate's capability surface: Wright-Fisher (forgetting dynamics prediction), queueing theory (throughput characterization under load), percolation (capacity cliff sharpness from parameters), ergodic theory (batch-vs-online equivalence), expander graphs (retrieval quality bounds from graph structure). Each is a zero-cost Sonnet drill.

4. Per [[feedback-no-papers-product-only]]: frame as "substrate research lab's information management system" (product infrastructure), never as "novel KMS methodology."

---

## P_deflated summary table

| Claim | P_deflated | Calibration note |
|---|---|---|
| Three-layer Markdown + git sufficient at current scale | 0.70 | PKM best practice; agent-write discipline is novel risk |
| Capability scorecard as prioritization spine | 0.65 | MLflow-style discipline well-validated in ML settings |
| Composition matrix as primary "next drill" artifact | 0.50 | Novel-synthesis cap applied; no direct published precedent |
| MDP saturation detection for cheap-drill | 0.50 | Formal work is 2024 preprints; composition-space application is novel |
| Epsilon-greedy branching at epsilon=0.20 | 0.60 | Robust baseline per lit; specific epsilon value is heuristic |
| Full implementation in 8-10 engineering hours | 0.70 | Standard software engineering; discipline-drop is main risk |
| Population genetics axis being high-yield | 0.40 | Tier-1b adjacency; speculative until first drill |
| Percolation axis being high-yield | 0.40 | Tier-1b adjacency; speculative until first drill |
| Ergodic theory axis being high-yield | 0.35 | No direct adjacency edge in current field-advisor |
| Queueing theory axis being high-yield | 0.40 | Throughput-characterization is directly substrate-relevant |
| Expander / Ramanujan axis being high-yield | 0.45 | Network-science Tier-1b; retrieval = graph retrieval is direct mapping |

All novel-synthesis P values capped at 0.50 per [[feedback-lit-scan-calibration-penalty]].

---

## Citations (verified count: 14)

1. biorxiv 2024.07.08.602487 -- "A platform for lab management, note-keeping and automation" (233-lab survey, electronic lab notebooks vs databases)
2. Databricks 2024 State of Data + AI -- 34% of ML engineering time spent reproducing past results without structured tracking
3. MLflow 3.0 / 3.10 (2024 / March 2026) -- structured experiment lifecycle management; multi-turn evaluation; trace cost tracking
4. OECD AI Capability Indicators (finalized Nov 2024) -- structured schema for AI capability assessment; ratings reflect state-of-art Nov 2024
5. Markdown Architectural Decision Records MADR 4.0 (September 2024) -- structured versioned decision documentation in plain text
6. arxiv 2509.21734 -- "Optimal Stopping for Sequential Bayesian Experimental Design" (MDP framing for saturation + stopping rules)
7. arxiv 2107.12809 -- "Bayesian Optimisation for Sequential Experimental Design" (diminishing returns; sequential adaptive design)
8. PMC 7515147 (Entropy 2020) -- "A Novel Active Learning Regression Framework for Balancing the Exploration-Exploitation Trade-Off" (Bayesian hierarchical adaptive control)
9. Cambridge Management and Organization Review -- "Exploration-Exploitation Duality with Both Tradeoff and Synergy: Curvilinear Interaction Effects of Learning Modes on Innovation Types"
10. dsebastien.net -- "Personal Knowledge Management at Scale: Analyzing 8,000 Notes and 64,000 Links" (link density vs note count; orphaned nodes as coverage gaps)
11. bookmarksharer.com / atlasworkspace.ai -- Advanced Zettelkasten with Obsidian: atomic notes, graph view, cluster detection, orphan detection
12. arxiv 2603.17781 -- "Facts as First Class Objects: Knowledge Objects for Persistent LLM Memory" (hash-addressed fact tuples; 252x cost reduction; 100% retrieval accuracy vs in-context)
13. Amit, Gutfreund, Sompolinsky 1985 -- AGS capacity theory (cited as algebraic anchor for capacity row; internal cross-reference)
14. research_field_advisor.py output 2026-06-04 -- 110 drills, 22 fields, saturation + scope-expansion candidates (internal reference)
