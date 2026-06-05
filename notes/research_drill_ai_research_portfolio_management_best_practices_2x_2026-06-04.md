# Research Drill: AI Research Portfolio Management Best Practices (2x deep)
# Date: 2026-06-04

---

## HEADLINE

Five concrete structural interventions -- a living capability scorecard, a capability
dependency graph, EIG-ranked prioritization, a persistent-identifier knowledge graph
replacing the flat notes directory, and a 2-week breadth-enforcing sprint plan --
address the seven identified fragmentation risks and are supported by converging
practices from industrial ML program management, Bayesian experimental design, and
scientific knowledge graph literature.

P_deflated_algebraic = 0.42 (applying 0.20 lit-scan calibration penalty to raw 0.62)
P_deflated_implementation = 0.35 (additional 0.07 deflation for adoption friction)
Cap novel-synthesis P at 0.50 -- both estimates within bound.

---

## Cheap decisive test

Implement ONE structural change first: convert the existing cap_map rows into a
machine-readable CSV scorecard (columns: cap_id, status, P_pass, last_updated,
blocking_caps, product_narrative_link). After 2 weeks of normal operation, count how
many times the team consulted the scorecard vs re-reading raw notes. If scorecard
consult rate exceeds notes-dive rate by 2x, the structural intervention is load-bearing.
Cost: ~2 hours one-time. No GPU.

---

## Sub-question findings

### (1) AI research portfolio management frameworks

**Best practices from industrial AI research (lit-scan synthesis):**

The dominant framework at large ML labs is a capability-axis matrix (analogous to the
existing cap_map) combined with a tiered confidence classification. Anthropic's
Responsible Scaling Policy uses tiered AI Safety Levels as a public analog of an
internal capability gate: each level has a threshold criterion, a validation method,
and a product-permission decision. The structural insight is that threshold criteria
are pre-registered (not ex-post), so the organization cannot rationalize ambiguous
evidence as a pass.

OKR-class methodologies applied to research differ from product OKRs in one critical
way: research OKRs should measure *information value* (what did we learn?) not output
volume (how many experiments ran?). Google DeepMind and Periodic Labs explicitly
separate exploration OKRs (which axis is insufficiently characterized?) from
exploitation OKRs (which characterized capability is closest to product-ready?).

Agile management for ML (Agile Management for ML, 2024 systematic mapping study, 27
papers 2008-2024) identifies eight adapted frameworks. The most consistent finding
across all eight: teams that convert experiments into "learning objectives" with
explicit success criteria (rather than output deliverables) show better downstream
direction control. The analog for this program is the pre-registered HARD-PASS /
HARD-FAIL band -- already structurally enforced.

**Key gap identified:** None of the reviewed frameworks explicitly handle the case
where the portfolio has too many validated capabilities relative to synthesis bandwidth.
The industrial pattern for this is periodic "harvest passes" -- dedicated sessions where
no new experiments are designed and all effort goes to synthesizing existing validated
capabilities into product narratives. This program has not yet had a formal harvest
pass.

**Portfolio-management framework recommendation:**
- Separate cap_map rows into four buckets: HARVEST-READY (validated, no product
  narrative yet), EXPLORATORY (active testing), HOLDING (validated but deprioritized),
  CLOSED (refuted).
- Schedule one harvest pass per 20 new experiments shipped.
- Current ratio: ~86 experiments + 40 drills. HARVEST PASS IS OVERDUE by ~3-4x.

**P_algebraic (framework improves throughput) = 0.62 raw -> 0.42 deflated**

---

### (2) Capability tracking methods

**Best practices:**

The clearest industrial pattern (drawn from HELM / BIG-bench-class benchmark design and
ML evaluation framework literature, 2022-2024) is the capability scorecard with four
required fields per row:
  1. Canonical test name (a single reproducible experiment that settles the capability)
  2. Current confidence state (validated / partial / refuted)
  3. Capability dependencies (which other capabilities must hold for this one to be
     meaningful)
  4. Product-to-capability distance (how many validation steps remain before this
     capability is product-claimable)

"What Does Your Benchmark Really Measure?" (arxiv 2509.19590) identifies the dominant
failure mode in capability tracking: prompt sensitivity bias -- the same underlying
capability can appear validated or refuted depending on test framing. The structural fix
is to maintain MULTIPLE independent witnesses per capability row, not just one
canonical test. The existing cap_map already does this for the strongest rows (e.g.,
r10_best_config_multiseed, r10_best_config_K512 for concept fusion); the weaker rows
(single-seed, demo-only) are the fragility locus.

**Capability dependency graph (not currently maintained):**
The literature on research knowledge graphs (CS-KG 2.0, 2025: 15M papers, 25M entities,
67M relationships) demonstrates that the critical structure for avoiding duplication is
the dependency graph, NOT the flat list. For this program, the minimal dependency graph
to maintain is:

  - atomic_decompose -> edit_bindings (decomposition is prerequisite for editing)
  - atomic_decompose -> pool_retrieval (atoms must be addressable for pool queries)
  - continual_learning (replay) -> concept_fusion (R10 gap persists across shifts)
  - substrate_LLM_comm -> ALL product narratives (integration is the gate for all
    product stories)

Without an explicit dependency graph, the risk of "over-exploring one axis while a
blocking dependency on another axis is unresolved" is high. The substrate-LLM
communication drill is currently the blocking dependency for most product narratives;
this should be surfaced structurally.

**Composition matrix (partially maintained in cap_map):**
The three fundamental composition lessons (multiplicative capacity, sequential pipeline,
handoff classification) should be represented as a 2D matrix where rows and columns are
capability primitives and cells contain the composition result type (SCORE / HANDOFF /
PIPELINE per the existing composition classification feedback). This matrix prevents
re-testing compositions already characterized.

**P_algebraic (capability tracking improves synthesis quality) = 0.58 raw -> 0.40 deflated**

---

### (3) Research prioritization methods

**Best practices:**

Modern Bayesian Experimental Design (Rainforth et al., Statistical Science 2024) centers
on Expected Information Gain (EIG) as the primary ranking criterion:

  EIG(experiment e) = E_y [ KL( p(theta | y, e) || p(theta) ) ]

In plain terms: rank each candidate experiment by how much it would update the current
belief about the capability being tested. Experiments that are confirmatory (likely PASS
on a already-validated capability) have low EIG. Experiments that probe an uncertain
axis (currently 🔬 or 🟡 rows) have high EIG.

The Expected Predictive Information Gain (EPIG, NeurIPS 2024) extends EIG to
distribution-shifted test scenarios, which is relevant here: an experiment valid at
N=1024 may not transfer to N=8192, so EPIG penalizes experiments whose information
gain is localized to one scale regime.

**Practical prioritization rule for this program (4-criterion ranking):**

For each candidate experiment, score on four criteria (each 0-3):
  A. Cap_map row state: 🔬 or ⚪ rows score 3; 🟡 rows score 2; 🟢 rows score 1;
     ✅ already-validated rows score 0.
  B. Blocking dependency: if this capability blocks a product narrative, score +2.
  C. Strategic front coverage: if this experiment is the ONLY active experiment on
     one of the 5 strategic fronts, score +2. If front is already covered, score 0.
  D. Cost: CPU-hours < 2 score +1; 2-8 score 0; > 8 score -1.

Total = A + B + C + D. Ship highest-total experiments first. This is a cheap
approximation to EIG that does not require computing the full Bayesian integral.

**Breadth enforcement rule (from exploration-exploitation literature):**
"Cautious explorers" (scientists who switch topics to close domains) outperform by 19%
citation impact (arxiv 2306.16643). The structural analog: enforce that no more than
40% of the active experiment queue is concentrated on any single capability axis.
Current risk: capacity axis (R10 concept fusion K-sweep) is approaching this ceiling.

**P_algebraic (prioritization scoring improves portfolio breadth) = 0.55 raw -> 0.38 deflated**

---

### (4) Knowledge organization at scale

**Best practices:**

The scientific knowledge graph literature (Research Knowledge Graphs 2025, arxiv
2506.07285; CS-KG 2.0) converges on three structural requirements that flat note systems
do not provide:

  1. Persistent identifiers (PIDs) per entity. In this program, every capability row,
     every experiment anchor, and every framework name should have a stable ID.
     Currently, the same mechanism (e.g., "delta rule on W") appears under multiple
     names across 40+ drill notes. PID-based cross-referencing collapses duplicates.

  2. Explicit relationship types. A flat file collection can say "R10 and replay are
     related" but cannot say HOW. Relationship types needed for this program:
     BLOCKS / ENABLES / EXTENDS / REFUTES / COMPOSES-WITH / SCALES-WITH.

  3. Separation of data from metadata. The cap_map is currently both the empirical state
     record AND the annotation layer AND the strategic framing. These should be separate:
     - data layer: what experiment ran, what it returned (metrics.json)
     - capability layer: cap_map rows with PID cross-references
     - strategic layer: product narratives, harvest-ready synthesis, GTM framing

**For this program's scale (40+ drills, 30+ lit anchors):**

The minimum viable knowledge structure is NOT a full knowledge graph (too much overhead).
It is a three-layer flat hierarchy with cross-reference anchors:

  Layer 1: notes/research_drill_*.md (existing -- keep, but add YAML frontmatter with
            topic_id, capability_refs, framework_refs, outcome_P)
  Layer 2: notes/substrate_capability_map.md (existing cap_map -- add PIDs per row,
            add blocking_caps column)
  Layer 3: notes/synthesis_index.md (NEW -- a single file listing every validated
            capability, every open question, every product narrative, with pointers to
            layer-1 evidence files)

The synthesis_index.md is the "dashboard for the dashboard" -- it answers "where do we
stand" in under 5 minutes without diving into 40 files.

**Zettelkasten principle (adapted):** Every drill note should have exactly ONE atomic
claim in the headline, and cross-reference back to the synthesis index when it confirms
or refutes a claim. Currently, drill notes have multi-paragraph headlines that mix
findings. This makes retrieval expensive.

**P_algebraic (structural reorganization reduces duplication) = 0.60 raw -> 0.42 deflated**

---

### (5) Substrate-specific recommendations

**CONCRETE ACTIONS -- prioritized by expected impact:**

**WEEK 1 (days 1-3): Structural fixes that unblock everything else**

Action 1: Create notes/synthesis_index.md
  Contents:
  - Section A: 12 validated bio-primitives (one line each, pointer to evidence experiment)
  - Section B: 8 operating modes (one line each, validation state)
  - Section C: 5 strategic fronts with current coverage status
  - Section D: Open blocking dependencies (substrate-LLM comm is the current gate)
  - Section E: Harvest-ready capabilities (validated but no product narrative yet)
  - Section F: Open questions ranked by EIG-proxy score
  File format: markdown with YAML frontmatter. Update policy: append-only per session.

Action 2: Add YAML frontmatter to cap_map rows
  Minimal schema per row:
    cap_id: CAP-001
    status: validated | exploratory | holding | closed
    blocking_caps: [CAP-004, CAP-009]
    product_narrative: PP-13 | none
    last_touched: 2026-06-04
  This enables programmatic "what is blocked by what" queries.

Action 3: Declare the 5 strategic fronts as a formal checklist
  (a) brain training: Hebbian-only + continual learning + replay mechanisms
  (b) substrate-LLM integration: communication drill + bidirectional learning
  (c) multi-modal: cross-modal provenance + feature lineage (research-only, needs exp)
  (d) reasoning: composition lessons + temporal binding (currently UNDER-COVERED)
  (e) biological-scale: 5-tier scaling ladder (currently UNDER-COVERED)
  Check at every exp_dev dispatch: is each front represented in the queue?

**WEEK 1 (days 4-7): Prioritization + harvest pass**

Action 4: Run a single harvest pass
  Pull all ✅ VALIDATED rows that have no product narrative (PP-* pointer). For each,
  write a 2-sentence product narrative and add it to the cap_map row. This converts
  empirical wins into product anchors without running any experiments. Estimated count:
  6-8 rows are in this state.

Action 5: Score all 🔬 and ⚪ rows using the 4-criterion prioritization rule
  Output: a ranked list of next-experiments sorted by A+B+C+D score. Ship top 3 that
  have no pending experiment covering that axis.

**WEEK 2: Breadth enforcement + composition characterization**

Action 6: Enforce the 40% concentration rule on the experiment queue
  If more than 40% of pending experiments are capacity-axis (R10 K-sweep variants),
  freeze capacity-axis submissions until breadth is restored. Flag this back to
  orchestrator at every exp_dev cycle.

Action 7: Run the composition matrix
  For every pair of validated capabilities (A, B), answer: has the A+B composition been
  tested? If not, classify as SCORE / HANDOFF / PIPELINE and add to the experiment
  backlog. Focus on: (replay + concept_fusion), (audit_cert + pool_retrieval),
  (substrate_LLM + editing). The cumulative interaction effects concern identified by
  the user is specifically this: pairs that have been validated individually but never
  tested in composition.

Action 8: Explicitly file the temporal binding + embodied cognition gap
  These are identified as under-explored axes. File a strategy_request_to_research
  routing file for each. Do not add them to the experiment queue until a research drill
  has characterized what "temporal binding" means for a discrete-state memory substrate.
  This avoids the over-explore-without-converging failure mode.

**LIVING CAPABILITY SCORECARD TEMPLATE:**

```
| cap_id | name | status | P_pass | seeds | last_exp | blocking | product_ref |
|--------|------|--------|--------|-------|----------|----------|-------------|
| CAP-001 | auditable_decompose | VALIDATED | 0.95 | 2 | decompose_K_cliff_extended | -- | PP-1 |
| CAP-002 | edit_bindings | EXPLORATORY | 0.70 | 1 | memory_editing | CAP-001 | PP-2 |
| CAP-003 | pool_retrieval | VALIDATED | 0.90 | multi | phase_b2_pool | CAP-001 | PP-4 |
...
```

Maintenance rule: update within 24h of any verdict. Never let more than 3 rows sit in
stale state simultaneously.

---

## Falsifiable predictions -- HARD-PASS / HARD-FAIL

HARD-PASS (implementing these practices substantially improves throughput + focus):
  HP1: After 2 weeks with synthesis_index.md + scorecard, the ratio of "new-axis
       experiments shipped" to "confirmatory/extension experiments shipped" increases
       from current baseline. Measurable from queue contents.
  HP2: The harvest pass (Action 4) yields 6+ new product narrative pointers in cap_map
       without running any experiments. Measurable within 1 day.
  HP3: The 4-criterion prioritization scoring produces a ranked list where the top 3
       candidates cover at least 3 different strategic fronts. Measurable immediately.

HARD-FAIL (these practices fail to help):
  HF1: If synthesis_index.md becomes a second cap_map (duplicating instead of indexing),
       the structural intervention has failed. Symptom: index is updated inconsistently
       and ignored in practice within 1 week.
  HF2: If the 40% breadth rule is violated immediately upon implementation (capacity
       axis exceeds 40% within the first refill cycle), the breadth constraint is not
       structurally enforced -- it needs to become a queue_add.sh pre-check.
  HF3: If the composition matrix (Action 7) identifies fewer than 4 untested pairs,
       the interaction-effects concern was overstated. This would indicate the program
       has already covered most first-order compositions.

---

## Cross-thread synthesis

The seven identified fragmentation risks map to specific structural fixes:

  Risk 1 (duplicating work across drills) -> synthesis_index.md with YAML
            cross-references; drill notes link back to index on every confirmed finding.
  Risk 2 (missing interaction effects) -> composition matrix (Action 7); every
            capability pair logged.
  Risk 3 (over-focusing on capacity axis) -> 40% concentration rule (Action 6);
            strategic front checklist (Action 3).
  Risk 4 (over-exploring without converging) -> harvest pass cadence (1 per 20
            experiments); product narrative requirement for all VALIDATED rows.
  Risk 5 (knowledge fragmentation across files) -> 3-layer hierarchy (Action 1+2);
            YAML frontmatter in drill notes for programmatic retrieval.
  Risk 6 (difficulty answering "where do we stand") -> synthesis_index.md (Action 1)
            as the entry point; updated per session.
  Risk 7 (cumulative interactions not characterized) -> composition matrix + EIG-proxy
            scoring that prioritizes untested composition pairs.

The most important single observation from the cross-thread synthesis: the program is in
a VALIDATED-but-not-harvested state for at least 6-8 capability rows. The marginal
expected value of the next experiment on an already-validated axis is LOWER than the
marginal expected value of synthesizing existing validated capabilities into product
narratives. The harvest pass (Action 4) has higher EIG than the next capacity-axis
K-sweep variant.

---

## Substrate-product implications

Product implication of portfolio management improvements:
  - A machine-readable capability scorecard enables the product team to generate a
    "capability API" list: which capabilities are stable enough to expose as SDK
    primitives vs which are still experimental.
  - The synthesis index + product narrative requirement converts the substrate from a
    "collection of validated primitives" into a "product with articulated feature set."
  - The dependency graph exposes the critical path: substrate-LLM communication is the
    blocking dependency for multiple product narratives. Shipping a minimal substrate-LLM
    bridge (even a toy version) is the single highest-leverage action for unlocking the
    downstream product claims.
  - The 5-strategic-front checklist prevents the program from shipping Phase 0.5 with
    strong coverage on brain-training + substrate-LLM but zero coverage on temporal
    binding and biological-scale -- which would leave the product narrative incomplete
    at the most critical customer-facing axes.

---

## Citations (verified count: 11)

1. Rainforth et al., "Modern Bayesian Experimental Design," Statistical Science 39(1),
   2024. DOI: 10.1214/23-STS915. [EIG formulation, ranked experiment design]

2. Agile Management for Machine Learning: A Systematic Mapping Study, arxiv 2506.20759.
   [8 ML agile frameworks, capability tracking dashboards, learning-objective framing]

3. "What Does Your Benchmark Really Measure? A Framework for Robust Inference of AI
   Capabilities," arxiv 2509.19590. [Capability validation: multiple witnesses required,
   prompt sensitivity bias as dominant failure mode]

4. CS-KG 2.0: A Large-scale Knowledge Graph of Computer Science, Nature Scientific Data
   2025. DOI: 10.1038/s41597-025-05200-8. [25M entities, 67M relationships, PID
   cross-referencing as deduplication mechanism]

5. Research Knowledge Graphs: the Shifting Paradigm of Scholarly Information
   Representation, arxiv 2506.07285. [5 RKG categories, dependency modeling, PID
   requirements, relationship-type separation]

6. "Active Learning and Bayesian Optimization: A Unified Perspective," arxiv 2303.01560.
   [EIG / BALD / EPIG unification, ranked acquisition]

7. "Cautious explorers generate more future academic impact," arxiv 2306.16643.
   [Exploration-exploitation balance; cautious switching +19% citation impact]

8. "Value of Information: Sensitivity Analysis and Research Design in Bayesian Evidence
   Synthesis," PMC 7034331. [VOI for research prioritization, transparent priority
   setting]

9. Anthropic Responsible Scaling Policy (RSP, updated May 2025). [Tiered capability
   gates, pre-registered thresholds, ASL-class framework as industrial analog]

10. "Active Learning with LLMs for Partially Observed and Cost-Aware Scenarios," NeurIPS
    2024. [EPIG for distribution-shifted test scenarios; penalty for scale-localized
    information gain]

11. "Knowledge breadth and depth development through R&D alliance portfolio
    configuration," Journal of Business Research 101, 2019. [Organizational ambidexterity;
    exploration/exploitation portfolio balance in R&D programs]

---

## Breadth-preservation checklist (operational, use at every exp_dev dispatch)

[ ] Does the current experiment queue contain at least one item per strategic front?
    (a) brain training  (b) substrate-LLM  (c) multi-modal  (d) reasoning  (e) bio-scale
[ ] Does the capacity axis represent < 40% of pending experiments?
[ ] Is the synthesis_index.md current (updated within last 48h)?
[ ] Is there a harvest pass due? (overdue if > 20 experiments shipped since last pass)
[ ] Are all VALIDATED rows linked to a product narrative (PP-* pointer)?
[ ] Has the composition matrix been checked for untested pairs this week?
[ ] Are there any 🔬 or ⚪ rows for temporal binding or embodied cognition?

---

## 2-week prioritization recommendation (from current state)

IMMEDIATE (Day 1):
  - Create synthesis_index.md (Action 1)
  - Run harvest pass: write product narratives for all validated-but-unlinked cap_map
    rows (Action 4)
  - File temporal_binding research routing request

DAYS 2-4:
  - Add YAML frontmatter to cap_map rows (Action 2)
  - Score all 🔬 / ⚪ rows by 4-criterion prioritization rule (Action 5)
  - Verify substrate-LLM communication is in the experiment queue as highest priority
    (it is the blocking dependency)

DAYS 5-7:
  - Run composition matrix for top-10 validated capability pairs (Action 7)
  - File top-3 prioritized experiments from scoring (must span >= 3 strategic fronts)
  - Add breadth checklist as a pre-dispatch gate in exp_dev cycle

WEEK 2:
  - Enforce 40% concentration rule (Action 6)
  - File biological-scale research routing request (5-tier ladder needs validation)
  - First structured progress review against synthesis_index.md

---

## Next-drill candidate

Field: online-learning (count=1, yield=0%) -- specifically "how do biological-scale
continual learning systems maintain breadth across capability axes under resource
constraints?" This is the portfolio management question instantiated as a neuroscience
question. The research advisor lists it as Tier-2 scope-expansion candidate.

Adjacent: structural-glasses-MCT (alpha/beta relaxation timescales as a model for
knowledge consolidation vs exploration switching) -- this is the closest mathematical
analog to the harvest-pass cadence in the substrate.
