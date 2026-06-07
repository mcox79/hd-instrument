# exp_dev hand-off -- research: natural analog hippocampal-cortical sleep consolidation

**Filed-by:** research sub-agent (2026-06-07)
**Trigger:** notes/research_drill_natural_analog_hippocampal_5x_2026-06-07.md
**Pause state:** check data/orchestrator_paused.flag before dispatching any anchor

Per [[feedback-no-experiment-design-in-prompts]]: this file hands TASK + WHY + CONTRACT + AUTONOMY. It does NOT specify anchor names, sweep grids, threshold formulas, HF/HP numerical bounds, or pre-committed cap_map decisions. exp_dev designs the experiment.

---

## CONTEXT SUMMARY

The 5x deep hippocampal-cortical drill found five engineering-tractable substrate extensions grounded in mature neuroscience (50+ year literature, causal optogenetic evidence). Three are low-cost (1-3 days engineering) and directly testable within v1 timeline. Two are medium-cost (1-2 weeks) with clear pre-test criteria. One (dual-N hierarchical architecture) requires rung-1 algebra verification before any empirical work.

The most important finding for immediate action: reverse-order unbind as counterfactual generation is directly biologically validated by hippocampal reverse replay. Nature independently evolved this same algebraic operation for counterfactual planning. This is not a new idea to test; it is confirmation that the mechanism is correct.

The substrate is structurally identical to Complementary Learning Systems (CLS) theory: substrate = hippocampus (fast, episodic), LLM = neocortex (slow, semantic), sleep defrag = NREM consolidation. This framing is accurate at the architectural level with a well-established 50-year literature behind it.

---

## ANCHOR CANDIDATES (rank-ordered by value x engineering cost)

### 1. Priority-Weighted Defrag (TMR Analog) -- TIER 1, CPU, 1-3 days

- **Anchor pointer:** notes/research_drill_natural_analog_hippocampal_5x_2026-06-07.md, Section P4.1 + Test A
- **Substrate-product reading:** Does adding a 2x Misra-Gries counter weight for flagged-priority domains achieve >=1.8x bridge accumulation rate vs unflagged domains? This gates the "important knowledge consolidates faster" product claim.
- **Tier hint:** CPU, pure substrate mechanics, no LM; test on small synthetic KB with two-domain split
- **Why now:** Cheapest of the five extensions; direct biological validation (TMR mechanism is causally confirmed); enables a concrete customer-facing feature with low engineering risk; P_deflated=0.75

### 2. Micro-Defrag Intra-Session Trigger -- TIER 1, CPU, 3-7 days

- **Anchor pointer:** notes/research_drill_natural_analog_hippocampal_5x_2026-06-07.md, Section P4.2 + Test B
- **Substrate-product reading:** Does triggering a light Misra-Gries pass when write rate drops below threshold reduce overnight full-defrag time by >=30%? This gates the "continuous availability" architecture claim.
- **Tier hint:** CPU; requires write-rate monitoring instrumentation + micro-defrag trigger; measure overnight pass time vs baseline
- **Why now:** Direct analog of awake SWRs during quiet wakefulness (causally confirmed in Science 2024); eliminates defrag batch overhead; P_deflated=0.65

### 3. Reverse-Order Unbind for Counterfactuals -- TIER 1-2, CPU, 1-2 weeks

- **Anchor pointer:** notes/research_drill_natural_analog_hippocampal_5x_2026-06-07.md, Section P4.3 + Test C
- **Substrate-product reading:** Does reverse-order unbind over a write log produce a substrate state within cosine-0.05 of the true "never-written" baseline for 8/10 test facts? This gates the counterfactual generation product feature.
- **Tier hint:** CPU smoke first (200-fact synthetic KB, 10 test facts); measure cosine distance of reverse-unbind state vs true never-written state
- **Why now:** Biologically validated by hippocampal reverse replay (direct Nature 2006 + 2024 Nature Neuroscience evidence); algebra is already present in substrate (unbind operator); sequence bookkeeping is the only new infrastructure; P_deflated=0.55

### 4. Cosine-Cluster-First Misra-Gries -- TIER 1, CPU, 1-2 weeks

- **Anchor pointer:** notes/research_drill_natural_analog_hippocampal_5x_2026-06-07.md, Section 6.3 (Clustering)
- **Substrate-product reading:** Does running Misra-Gries within cosine-similarity clusters before a global pass reduce false-positive bridge accumulation (spurious cross-cluster patterns) by >=10%?
- **Tier hint:** CPU; compare clustering-first vs standard Misra-Gries on a KB with known cross-cluster structure; measure false-positive bridge rate
- **Why now:** Place cell spatial clustering is biologically fundamental; reduces spurious cross-domain pattern consolidation; P_deflated=0.55

### 5. Per-Domain Defrag Scheduling -- TIER 1, infrastructure, 1-3 days

- **Anchor pointer:** notes/research_drill_natural_analog_hippocampal_5x_2026-06-07.md, Section P4.6
- **Substrate-product reading:** Infrastructure anchor; parameterize defrag scheduler to support per-domain timing/frequency configs. No algorithmic change; enables enterprise product requirement.
- **Tier hint:** CPU/infrastructure only; no GPU required
- **Why now:** Lowest risk; high product value for multi-tenant deployments; P_deflated=0.80

---

## CONTEXT POINTERS

- Research note (primary): d:/AI/hd-instrument/notes/research_drill_natural_analog_hippocampal_5x_2026-06-07.md
- Sleep defrag HP: cycles 167 + 170 (search data/exp_*/metrics.json for those cycles)
- Bridge cache HP: cycle 168
- Contradiction detection HP: cycle 167
- Prior REM/replay drill: d:/AI/hd-instrument/notes/research_drill_rem_replay_consolidation_substrate_2x_2026-06-04.md
- REM/replay exp_dev handoff: d:/AI/hd-instrument/notes/exp_dev_handoff_research_rem_replay_consolidation_2026-06-04.md (check if anchor 1 from that file was completed before re-testing replay energy mechanics)
- Cap map: d:/AI/hd-instrument/data/cap_map.md (look for sleep defrag / consolidation rows)

---

## CONTRACT

exp_dev is expected to:
1. Pre-register HP/MID/HF bands for each anchor before coding
2. Run smoke gate before any full dispatch
3. Run rung-1 pre-test (per feedback-drill-pretest-required memory rule) before any claim that depends on novel substrate mechanism
4. Check for existing anchor name collision in queue before ship
5. For anchor 3 (reverse unbind): verify unbind algebra produces correct state on a 5-fact toy KB before scaling to 200-fact test
6. Do NOT design the dual-N hierarchical architecture (P4.5) until rung-1 CPU theory derivation confirms dual-N binding algebra is consistent; that is a future research direction, not a current exp_dev task

## AUTONOMY DECLARATION

exp_dev has full autonomy to:
- Select which of the 5 anchors to ship in this cycle (prioritize by cheapness and P_deflated)
- Design the experimental scaffold, sweep grid, and pre-reg thresholds
- Batch multiple cheap CPU anchors into a single dispatch if they share test infrastructure
- Decide to skip any anchor whose pre-test fails cleanly
- Route anchor 3 to a rung-1 theoretical check before empirical test if the algebra is unclear
